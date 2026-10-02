import pymupdf as fitz  # PyMuPDF native high-speed C++ engine
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
            
            # Open with fitz (PyMuPDF C++ core)
            doc = fitz.open(file_path)
            metadata = doc.metadata or {}
            
            for page_idx, fitz_page in enumerate(doc):
                page_num = page_idx + 1
                
                # 1. High-performance native table extraction
                table_boxes = []
                tables_markdown = []
                try:
                    native_tables = fitz_page.find_tables()
                    for tab in native_tables:
                        table_boxes.append(tab.bbox)
                        extracted_table = tab.extract()
                        if extracted_table:
                            tables_markdown.append(self._format_table_as_markdown(extracted_table))
                except Exception:
                    # Fallback gracefully if table extraction fails on a specific page
                    table_boxes = []
                    tables_markdown = []
                
                # 2. Extract layout-aware text blocks
                # get_text("blocks") returns list: (x0, y0, x1, y1, text, block_no, block_type)
                raw_blocks = fitz_page.get_text("blocks")
                sorted_blocks = sorted(raw_blocks, key=lambda b: (b[1], b[0]))
                
                page_text_parts = []
                inserted_tables = set()
                
                for block in sorted_blocks:
                    x0, y0, x1, y1, block_text, block_no, block_type = block
                    
                    if block_type != 0:  # Skip image blocks
                        continue
                        
                    block_text_stripped = block_text.strip()
                    if not block_text_stripped:
                        continue
                    
                    # Check if this block falls inside a table bounding box
                    in_table = False
                    for idx, tbox in enumerate(table_boxes):
                        tx0, ty0, tx1, ty1 = tbox
                        # Check bounding overlap
                        if not (x1 < tx0 or x0 > tx1 or y1 < ty0 or y0 > ty1):
                            in_table = True
                            if idx not in inserted_tables and idx < len(tables_markdown):
                                md_table = tables_markdown[idx]
                                if md_table:
                                    page_text_parts.append(md_table)
                                inserted_tables.add(idx)
                            break
                            
                    if not in_table:
                        # Regular text block - check if it's a section heading
                        is_head, clean_head = self._check_and_clean_heading(block_text_stripped)
                        if is_head:
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
                current_cumulative_length += len(page_text) + 2  # +2 accounts for "\n\n"
                page_boundaries.append(current_cumulative_length)
                
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
            if len(row) < len(headers):
                row.extend([""] * (len(headers) - len(row)))
            markdown_lines.append("| " + " | ".join(row[:len(headers)]) + " |")
            
        return "\n".join(markdown_lines)

    def _check_and_clean_heading(self, text: str) -> tuple[bool, str]:
        lines = text.split("\n")
        if len(lines) > 2:
            return False, ""
            
        text_clean = text.replace("\n", " ").strip()
        if len(text_clean) > 80:
            return False, ""
            
        heading_patterns = [
            r'^\d+(\.\d+)*\s+[A-Z]',
            r'^(Chapter|Section|Appendix|Part|Clause)\s+\d+',
            r'^[I|V|X|L|C|D|M]+\.\s+[A-Z]',
            r'^[A-Z][A-Za-z\s]{3,30}$'
        ]
        
        for pat in heading_patterns:
            if re.match(pat, text_clean):
                return True, text_clean
                
        return False, ""
