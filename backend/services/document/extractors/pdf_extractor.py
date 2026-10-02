import pymupdf as fitz  # PyMuPDF — replaces deprecated 'import fitz'

import pdfplumber
import re
from typing import List, Dict, Any
from backend.services.document.extractors.base_extractor import BaseExtractor, ExtractionResult, PageContent

class PDFExtractor(BaseExtractor):
    def extract(self, file_path: str) -> ExtractionResult:
        try:
            pages = []
            full_text_parts = []
            page_boundaries = []
            headings = []
            current_cumulative_length = 0
            
            # Open with pdfplumber for table extraction
            pdf_plumber_doc = pdfplumber.open(file_path)
            
            # Open with fitz for block extraction
            doc = fitz.open(file_path)
            metadata = doc.metadata or {}
            
            for page_idx, fitz_page in enumerate(doc):
                page_num = page_idx + 1
                plumber_page = pdf_plumber_doc.pages[page_idx]
                
                # 1. Extract tables and their bounding boxes
                tables = plumber_page.extract_tables()
                table_objects = plumber_page.find_tables()
                
                # Store table boxes: (x0, y0, x1, y1) but note pdfplumber uses different coordinate orientation.
                # pdfplumber y0 is top, y1 is bottom (same as fitz).
                table_boxes = []
                for tobj in table_objects:
                    table_boxes.append((tobj.bbox, tobj))
                
                # 2. Extract layout-aware blocks using fitz
                # get_text("blocks") returns list of blocks: (x0, y0, x1, y1, text, block_no, block_type)
                raw_blocks = fitz_page.get_text("blocks")
                
                # Sort blocks primarily by y0 (top-to-bottom), then x0 (left-to-right) to handle multi-column
                # We can group blocks into vertical columns if their x coordinates align.
                # For standard reading, fitz's default sorting in get_text("blocks") is already layout-aware.
                sorted_blocks = sorted(raw_blocks, key=lambda b: (b[1], b[0]))
                
                page_text_parts = []
                processed_tables = set()
                
                for block in sorted_blocks:
                    x0, y0, x1, y1, block_text, block_no, block_type = block
                    
                    if block_type != 0:  # Skip image blocks
                        continue
                        
                    block_text_stripped = block_text.strip()
                    if not block_text_stripped:
                        continue
                    
                    # Check if this block falls inside a table boundary
                    in_table = False
                    for idx, (tbox, tobj) in enumerate(table_boxes):
                        tx0, ty0, tx1, ty1 = tbox
                        # Check overlap
                        if not (x1 < tx0 or x0 > tx1 or y1 < ty0 or y0 > ty1):
                            in_table = True
                            if idx not in processed_tables:
                                # Convert table to markdown
                                table_data = tables[idx]
                                markdown_table = self._format_table_as_markdown(table_data)
                                page_text_parts.append(markdown_table)
                                processed_tables.add(idx)
                            break
                            
                    if not in_table:
                        # Regular text block - check if it is a heading
                        is_head, clean_head = self._check_and_clean_heading(block_text_stripped)
                        if is_head:
                            # Save heading with its cumulative start character position
                            headings.append({
                                "text": clean_head,
                                "start_offset": current_cumulative_length + len("\n\n".join(page_text_parts)) if page_text_parts else current_cumulative_length
                            })
                        page_text_parts.append(block_text_stripped)
                
                # Format page text
                page_text = "\n\n".join(page_text_parts)
                pages.append(PageContent(page_number=page_num, text=page_text))
                full_text_parts.append(page_text)
                
                # Update boundary indices
                current_cumulative_length += len(page_text) + 2  # +2 accounts for the "\n\n" separator
                page_boundaries.append(current_cumulative_length)
                
            pdf_plumber_doc.close()
            doc.close()
            
            full_text = "\n\n".join(full_text_parts)
            
            return ExtractionResult(
                full_text=full_text,
                pages=pages,
                metadata=metadata,
                total_pages=len(pages),
                extraction_success=True,
                page_boundaries=page_boundaries,
                headings=headings
            )
            
        except Exception as e:
            import traceback
            print(f"PDF Extraction error: {e}\n{traceback.format_exc()}")
            return ExtractionResult(
                full_text="",
                pages=[],
                metadata={},
                total_pages=0,
                extraction_success=False
            )

    def _format_table_as_markdown(self, table_data: List[List[str]]) -> str:
        if not table_data or not table_data[0]:
            return ""
            
        markdown_lines = []
        # Filter out completely empty rows
        filtered_rows = []
        for row in table_data:
            if any(cell is not None and str(cell).strip() for cell in row):
                filtered_rows.append([str(cell or "").strip().replace("\n", " ") for cell in row])
                
        if not filtered_rows:
            return ""
            
        # Headers
        headers = filtered_rows[0]
        markdown_lines.append("| " + " | ".join(headers) + " |")
        # Separators
        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        
        # Data rows
        for row in filtered_rows[1:]:
            # Pad row if it has fewer cells than headers
            if len(row) < len(headers):
                row.extend([""] * (len(headers) - len(row)))
            markdown_lines.append("| " + " | ".join(row[:len(headers)]) + " |")
            
        return "\n".join(markdown_lines)

    def _check_and_clean_heading(self, text: str) -> tuple[bool, str]:
        """
        Heuristic to detect if a text block is a section heading.
        Headings are short (under 80 characters), usually single line,
        and start with numbers (e.g., 1.1, Chapter 1, Section A).
        """
        lines = text.split("\n")
        if len(lines) > 2:
            return False, ""
            
        text_clean = text.replace("\n", " ").strip()
        if len(text_clean) > 80:
            return False, ""
            
        # Decimal numbers, Chapter, Section, Appendix, etc.
        heading_patterns = [
            r'^\d+(\.\d+)*\s+[A-Z]', # 1. Introduction or 1.1.2 Scope
            r'^(Chapter|Section|Appendix|Part|Clause)\s+\d+', # Chapter 1
            r'^[I|V|X|L|C|D|M]+\.\s+[A-Z]', # Roman numerals: I. Introduction
            r'^[A-Z][A-Za-z\s]{3,30}$' # ALL CAPS or Title Case short lines
        ]
        
        for pat in heading_patterns:
            if re.match(pat, text_clean):
                return True, text_clean
                
        return False, ""
