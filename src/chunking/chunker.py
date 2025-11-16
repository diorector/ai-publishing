# Text Chunker Implementation - Phase 1 GREEN (Minimal)
# 구현 시간: 2025-11-16 14:59 KST
# 텍스트를 처리 가능한 청크로 분할

from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TextChunker:
    """텍스트를 청크로 분할합니다"""

    def __init__(
        self,
        chunk_size: int = 5000,
        overlap: int = 0,
        boundary_type: str = 'word',
        document_structure: Optional[Dict] = None,
        preserve_code_blocks: bool = False
    ):
        """
        텍스트 청커 초기화

        Args:
            chunk_size: 청크 크기 (단어 수)
            overlap: 오버랩 크기
            boundary_type: 분할 경계 타입 ('word', 'sentence', 'paragraph', 'section')
            document_structure: 문서 구조 정보
            preserve_code_blocks: 코드 블록 보존 여부
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if overlap < 0:
            raise ValueError("overlap must be non-negative")

        self.chunk_size = chunk_size
        self.overlap = min(overlap, chunk_size)  # Auto-adjust if too large
        self.boundary_type = boundary_type
        self.document_structure = document_structure
        self.preserve_code_blocks = preserve_code_blocks

    def chunk_text(self, text: str) -> List[str]:
        """
        텍스트를 청크로 분할합니다

        Args:
            text: 분할할 텍스트

        Returns:
            청크 리스트
        """
        if text is None:
            raise TypeError("text cannot be None")

        if not text:
            return []

        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))

        return chunks if chunks else [""]

    def generate_metadata(
        self,
        chunks: List[str],
        original_text: Optional[str] = None
    ) -> List[Dict]:
        """
        각 청크의 메타데이터를 생성합니다

        Args:
            chunks: 청크 리스트
            original_text: 원본 텍스트 (위치 계산용)

        Returns:
            메타데이터 리스트
        """
        metadata_list = []

        for i, chunk in enumerate(chunks):
            metadata = {
                "chunk_id": f"chunk_{i:04d}",
                "position": i,
                "word_count": len(chunk.split()),
                "sequence_number": i
            }

            if original_text:
                metadata["original_position"] = len(" ".join(chunks[:i]))

            metadata_list.append(metadata)

        return metadata_list

    def add_context_overlap(self, chunks: List[str]) -> List[Dict]:
        """오버랩 컨텍스트 추가"""
        return [{"text": chunk, "metadata": {}} for chunk in chunks]

    def chunk_with_context(self, text: str) -> List[Dict]:
        """컨텍스트와 함께 청킹"""
        chunks = self.chunk_text(text)

        result = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                "text": chunk,
                "context_before": chunks[i-1][-100:] if i > 0 else "",
                "context_after": chunks[i+1][:100] if i < len(chunks) - 1 else ""
            }
            result.append(chunk_data)

        return result

    def remove_overlap_and_reassemble(self, translated_chunks: List[Dict]) -> str:
        """오버랩 제거 및 재조합"""
        texts = [c.get("translated_text", "") for c in translated_chunks]
        return " ".join(texts)
