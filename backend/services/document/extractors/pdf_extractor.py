import pymupdf as fitz  # PyMuPDF native high-speed C++ engine
import re
import logging
from typing import List, Dict, Any, Tuple
from backend.services.document.extractors.base_extractor import (
    BaseExtractor, ExtractionResult, PageContent, FigureContent
)

logger = logging.getLogger(__name__)

# Minimum area (in PDF points^2) for a figure to be considered significant
_MIN_FIGURE_AREA = 3000  # ~55x55 points — filters noise/decorative icons
# DPI scale factor for rendering figure crops (200 DPI = matrix 200/72)
_FIGURE_DPI_MATRIX = fitz.Matrix(200 / 72, 200 / 72)
# Context window: characters before/after a figure bbox to capture as surrounding text
_CONTEXT_RADIUS_PT = 80   # PDF points above/below figure to search for text


class PDFExtractor(BaseExtractor):

    def extract(self, file_path: str) -> ExtractionResult:
        try:
            pages = []
            full_text_parts = []
            page_boundaries = []
            headings = []
            figures: List[FigureContent] = []
            current_cumulative_length = 0

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
                    table_boxes = []
                    tables_markdown = []

                # 2. Extract all image references on this page for figure detection
                page_images = fitz_page.get_images(full=True)

                # 3. Extract layout-aware text blocks
                raw_blocks = fitz_page.get_text("blocks")
                sorted_blocks = sorted(raw_blocks, key=lambda b: (b[1], b[0]))

                page_text_parts = []
                inserted_tables = set()
                page_text_block_strs: List[Tuple[fitz.Rect, str]] = []

                for block in sorted_blocks:
                    x0, y0, x1, y1, block_text, block_no, block_type = block

                    if block_type != 0:  # Non-text blocks (images) — handled separately below
                        continue

                    block_text_stripped = block_text.strip()
                    if not block_text_stripped:
                        continue

                    rect = fitz.Rect(x0, y0, x1, y1)
                    page_text_block_strs.append((rect, block_text_stripped))

                    in_table = False
                    for idx, tbox in enumerate(table_boxes):
                        tx0, ty0, tx1, ty1 = tbox
                        if not (x1 < tx0 or x0 > tx1 or y1 < ty0 or y0 > ty1):
                            in_table = True
                            if idx not in inserted_tables and idx < len(tables_markdown):
                                md_table = tables_markdown[idx]
                                if md_table:
                                    page_text_parts.append(md_table)
                                inserted_tables.add(idx)
                            break

                    if not in_table:
                        is_head, clean_head = self._check_and_clean_heading(block_text_stripped)
                        if is_head:
                            headings.append({
                                "text": clean_head,
                                "start_offset": current_cumulative_length + len("\n\n".join(page_text_parts)) if page_text_parts else current_cumulative_length
                            })
                        page_text_parts.append(block_text_stripped)

                # 4. Visual RAG: Extract significant figures on this page
                page_figures = self._extract_page_figures(
                    fitz_page, page_num, page_text_block_strs, table_boxes
                )
                figures.extend(page_figures)

                # 5. Scanned-page detection: if page has no text but has images → mark for OCR
                if not page_text_parts and page_images:
                    logger.info(
                        f"[PDFExtractor] Page {page_num} appears scanned "
                        f"({len(page_images)} image(s), 0 text blocks). Flagging for OCR."
                    )
                    # Render full page for OCR (handled in FigureExtractionStage)
                    page_pixmap = fitz_page.get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72))
                    scanned_figure = FigureContent(
                        page_number=page_num,
                        figure_index=0,
                        bbox=(0.0, 0.0, float(fitz_page.rect.width), float(fitz_page.rect.height)),
                        image_bytes=page_pixmap.tobytes("png"),
                        context_text="[Full page render for scanned/image-only page]",
                        figure_type="scanned_page",
                    )
                    figures.append(scanned_figure)

                page_text = "\n\n".join(page_text_parts)
                pages.append(PageContent(page_number=page_num, text=page_text))
                full_text_parts.append(page_text)

                current_cumulative_length += len(page_text) + 2
                page_boundaries.append(current_cumulative_length)

            doc.close()
            full_text = "\n\n".join(full_text_parts)

            logger.info(
                f"[PDFExtractor] Extracted {len(pages)} pages, "
                f"{len(figures)} figures from {file_path}"
            )

            return ExtractionResult(
                full_text=full_text,
                pages=pages,
                metadata=metadata,
                total_pages=len(pages),
                extraction_success=True,
                page_boundaries=page_boundaries,
                headings=headings,
                figures=figures,
            )

        except Exception as e:
            import traceback
            logger.error(f"[PDFExtractor] Extraction error: {e}\n{traceback.format_exc()}")
            return ExtractionResult(
                full_text="",
                pages=[],
                metadata={},
                total_pages=0,
                extraction_success=False,
            )

    # ------------------------------------------------------------------
    # Visual RAG: Figure Extraction
    # ------------------------------------------------------------------

    def _extract_page_figures(
        self,
        page: "fitz.Page",
        page_num: int,
        text_blocks: List[Tuple["fitz.Rect", str]],
        table_boxes: List[tuple],
    ) -> List[FigureContent]:
        """
        Detects and extracts significant embedded images from a single page.
        Strategy:
        1. Get image list with xrefs
        2. For each image, reconstruct its bounding rect via get_image_rects()
        3. Filter by minimum area to exclude decorative elements
        4. Skip images that overlap with detected table regions
        5. Crop and render at 200 DPI
        6. Find surrounding text (spatial proximity) as context
        """
        page_figures: List[FigureContent] = []
        image_list = page.get_images(full=True)

        if not image_list:
            return page_figures

        figure_index = 0
        for img_info in image_list:
            xref = img_info[0]
            try:
                # Get all bounding boxes where this image appears on the page
                img_rects = page.get_image_rects(xref)
                if not img_rects:
                    continue

                for raw_rect in img_rects:
                    img_rect = raw_rect & page.rect
                    if img_rect.is_empty or img_rect.width < 15 or img_rect.height < 15:
                        continue

                    area = img_rect.width * img_rect.height
                    if area < _MIN_FIGURE_AREA:
                        continue  # Skip tiny decorative icons

                    # Skip figures that are table cells (overlap with table bbox)
                    if self._overlaps_any_table(img_rect, table_boxes):
                        continue

                    # Crop figure at 200 DPI safely within page bounds
                    try:
                        pix = page.get_pixmap(clip=img_rect, matrix=_FIGURE_DPI_MATRIX)
                        # Handle alpha channel: remove transparency (avoid black backgrounds)
                        if pix.alpha:
                            pix = fitz.Pixmap(fitz.csRGB, pix)
                        image_bytes = pix.tobytes("png")
                    except Exception as crop_err:
                        logger.warning(
                            f"[PDFExtractor] Failed to crop figure on p{page_num}: {crop_err}"
                        )
                        continue

                    # Spatial context extraction
                    context_text = self._extract_context_text(img_rect, text_blocks)

                    page_figures.append(FigureContent(
                        page_number=page_num,
                        figure_index=figure_index,
                        bbox=(img_rect.x0, img_rect.y0, img_rect.x1, img_rect.y1),
                        image_bytes=image_bytes,
                        context_text=context_text,
                        figure_type="unknown",  # Will be set by FigureCaptioner
                    ))
                    figure_index += 1

            except Exception as e:
                logger.warning(f"[PDFExtractor] Figure extraction error (xref={xref}): {e}")
                continue

        return page_figures

    def _overlaps_any_table(self, rect: "fitz.Rect", table_boxes: List[tuple]) -> bool:
        """Returns True if the given rect significantly overlaps any detected table."""
        for tbox in table_boxes:
            tx0, ty0, tx1, ty1 = tbox
            # Check for meaningful overlap (>50% of figure inside table)
            overlap_x = max(0, min(rect.x1, tx1) - max(rect.x0, tx0))
            overlap_y = max(0, min(rect.y1, ty1) - max(rect.y0, ty0))
            overlap_area = overlap_x * overlap_y
            figure_area = max(rect.width * rect.height, 1)
            if overlap_area / figure_area > 0.5:
                return True
        return False

    def _extract_context_text(
        self,
        fig_rect: "fitz.Rect",
        text_blocks: List[Tuple["fitz.Rect", str]],
    ) -> str:
        """
        Finds text blocks spatially adjacent to the figure (above/below within _CONTEXT_RADIUS_PT).
        Combines them to form a natural caption context string.
        """
        context_parts = []
        search_above = fitz.Rect(
            fig_rect.x0 - 20, fig_rect.y0 - _CONTEXT_RADIUS_PT,
            fig_rect.x1 + 20, fig_rect.y0
        )
        search_below = fitz.Rect(
            fig_rect.x0 - 20, fig_rect.y1,
            fig_rect.x1 + 20, fig_rect.y1 + _CONTEXT_RADIUS_PT
        )

        for block_rect, block_text in text_blocks:
            if block_rect.intersects(search_above) or block_rect.intersects(search_below):
                stripped = block_text.strip()
                if stripped and len(stripped) > 5:
                    context_parts.append(stripped)

        # Combine and truncate context (keep it concise for prompts)
        combined = " | ".join(context_parts[:4])
        return combined[:400] if combined else ""

    # ------------------------------------------------------------------
    # Table Formatting
    # ------------------------------------------------------------------

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

        headers = filtered_rows[0]
        markdown_lines.append("| " + " | ".join(headers) + " |")
        markdown_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

        for row in filtered_rows[1:]:
            if len(row) < len(headers):
                row.extend([""] * (len(headers) - len(row)))
            markdown_lines.append("| " + " | ".join(row[:len(headers)]) + " |")

        return "\n".join(markdown_lines)

    # ------------------------------------------------------------------
    # Heading Detection
    # ------------------------------------------------------------------

    def _check_and_clean_heading(self, text: str) -> tuple:
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
