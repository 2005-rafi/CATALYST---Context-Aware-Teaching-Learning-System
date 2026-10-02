import bisect
import re
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from backend.services.document.chunking.token_counter import TokenCounter

@dataclass
class ChunkData:
    text: str
    chunk_index: int
    token_count: int
    page_number: Optional[int] = None
    section_heading: Optional[str] = None

class RecursiveChunker:
    def __init__(self, settings):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.min_chunk_size = settings.CHUNK_MIN_SIZE
        self.token_counter = TokenCounter()
        self.separators = ["\n\n", "\n", ". ", "! ", "? ", " ", ""]

    def chunk(self, text: str, page_boundaries: List[int] = None, headings: List[Dict[str, Any]] = None) -> List[ChunkData]:
        # 1. Shield LaTeX/Unicode math formulas
        shielded_text, formula_map = self._shield_formulas(text)
        
        # 2. Perform chunking on the shielded text
        splits = self._split_text(shielded_text, self.separators)
        chunks = self._merge_splits_with_metadata(shielded_text, splits, page_boundaries or [], headings or [])
        
        # 3. Unshield formulas in the final chunks
        for chunk in chunks:
            chunk.text = self._unshield_formulas(chunk.text, formula_map)
            
        return chunks

    def _shield_formulas(self, text: str) -> tuple[str, dict[str, str]]:
        block_pattern = r'\$\$(.*?)\$\$'
        inline_pattern = r'\$(.*?)\$'
        
        formula_map = {}
        counter = 0
        
        def block_replace(match):
            nonlocal counter
            placeholder = f"__MATH_FORMULA_BLOCK_{counter}__"
            formula_map[placeholder] = match.group(0)
            counter += 1
            return placeholder
            
        shielded = re.sub(block_pattern, block_replace, text, flags=re.DOTALL)
        
        def inline_replace(match):
            nonlocal counter
            placeholder = f"__MATH_FORMULA_INLINE_{counter}__"
            content = match.group(1).strip()
            if not content or len(content) > 300:
                return match.group(0)
            formula_map[placeholder] = match.group(0)
            counter += 1
            return placeholder
            
        shielded = re.sub(inline_pattern, inline_replace, shielded)
        return shielded, formula_map

    def _unshield_formulas(self, text: str, formula_map: dict[str, str]) -> str:
        for placeholder, original in formula_map.items():
            text = text.replace(placeholder, original)
        return text

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        if not separators:
            return [text] if text else []
            
        separator = separators[0]
        
        if separator == "":
            return list(text)
            
        if separator not in text:
            return self._split_text(text, separators[1:])
            
        pieces = text.split(separator)
        
        if separator != " ":
            pieces = [p + separator if i < len(pieces) - 1 else p for i, p in enumerate(pieces)]
        else:
            pieces = [p + " " if i < len(pieces) - 1 else p for i, p in enumerate(pieces)]
            
        final_pieces = []
        for piece in pieces:
            if not piece:
                continue
            if self.token_counter.count(piece) > self.chunk_size:
                final_pieces.extend(self._split_text(piece, separators[1:]))
            else:
                final_pieces.append(piece)
                
        return final_pieces

    def _merge_splits_with_metadata(self, full_text: str, splits: List[str], page_boundaries: List[int], headings: List[Dict[str, Any]]) -> List[ChunkData]:
        chunks = []
        current_chunk_text = ""
        current_token_count = 0
        chunk_index = 0
        
        # Track our search pointer in full_text to accurately locate character indices of chunks
        search_pointer = 0
        
        for split in splits:
            split_tokens = self.token_counter.count(split)
            
            if current_token_count + split_tokens > self.chunk_size and current_chunk_text:
                if current_token_count >= self.min_chunk_size:
                    # Find start char index of this chunk in full text
                    start_char_idx = full_text.find(current_chunk_text[:30], search_pointer)
                    if start_char_idx == -1:
                        start_char_idx = search_pointer
                    else:
                        search_pointer = start_char_idx
                        
                    # Calculate page number and section heading
                    page_num = self._find_page_number(start_char_idx, page_boundaries)
                    section_heading = self._find_section_heading(start_char_idx, headings)
                    
                    chunks.append(ChunkData(
                        text=current_chunk_text.strip(),
                        chunk_index=chunk_index,
                        token_count=current_token_count,
                        page_number=page_num,
                        section_heading=section_heading
                    ))
                    chunk_index += 1
                
                # Overlap
                overlap_text = self.token_counter.get_last_tokens(
                    current_chunk_text, 
                    self.chunk_overlap
                )
                
                current_chunk_text = overlap_text + split
                current_token_count = self.token_counter.count(current_chunk_text)
            else:
                current_chunk_text += split
                current_token_count = self.token_counter.count(current_chunk_text)
                
        if current_chunk_text.strip() and current_token_count >= self.min_chunk_size:
            start_char_idx = full_text.find(current_chunk_text[:30], search_pointer)
            if start_char_idx == -1:
                start_char_idx = search_pointer
            
            page_num = self._find_page_number(start_char_idx, page_boundaries)
            section_heading = self._find_section_heading(start_char_idx, headings)
            
            chunks.append(ChunkData(
                text=current_chunk_text.strip(),
                chunk_index=chunk_index,
                token_count=current_token_count,
                page_number=page_num,
                section_heading=section_heading
            ))
            
        return chunks

    def _find_page_number(self, char_idx: int, page_boundaries: List[int]) -> int:
        if not page_boundaries:
            return 1
        # O(log P) Binary Search to locate page index
        idx = bisect.bisect_right(page_boundaries, char_idx)
        return idx + 1

    def _find_section_heading(self, char_idx: int, headings: List[Dict[str, Any]]) -> Optional[str]:
        if not headings:
            return None
        active_heading = None
        for h in headings:
            if h["start_offset"] <= char_idx:
                active_heading = h["text"]
            else:
                break
        return active_heading
