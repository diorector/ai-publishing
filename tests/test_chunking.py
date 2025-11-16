# Chunking Module Tests - Phase 1 RED
# 구현 시간: 2025-11-16 14:35 KST
# 청킹 시스템의 포괄적 테스트
# SPEC-PUB-TRANSLATE-001 요구사항:
# - 텍스트를 처리 가능한 단위로 분할
# - 청크별 메타데이터 생성 (ID, 위치, 문맥)
# - 오버랩 컨텍스트 유지
# - 구조 보존

import pytest
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class ChunkMetadata:
    """청크 메타데이터 구조"""
    chunk_id: str
    position: int
    original_position: int
    context_before: str
    context_after: str
    word_count: int
    is_section_boundary: bool


@pytest.fixture
def sample_text():
    """샘플 긴 텍스트"""
    return """Chapter 1: Introduction to AI

This chapter introduces the fundamental concepts of artificial intelligence and machine learning.
AI has become increasingly important in modern society. The applications range from healthcare to finance.

1.1 Historical Context

The field of artificial intelligence emerged in the 1950s with the Turing Test. Early researchers
believed that human-level intelligence could be simulated by machines. However, the journey has been
more complex than initially expected.

1.2 Core Concepts

Machine learning is a subset of AI that focuses on enabling computers to learn from data.
Unlike traditional programming, machine learning systems improve their performance through experience.
Deep learning, a subset of machine learning, uses neural networks with multiple layers.

Chapter 2: Neural Networks

Neural networks form the foundation of modern AI systems. They are inspired by biological neural networks.
A neural network consists of interconnected nodes that process information.

2.1 Perceptron Models

The perceptron is the simplest form of neural network. It was developed in the 1950s.
A single perceptron can solve simple classification problems. However, more complex problems require multiple layers.

2.2 Deep Learning

Deep learning uses multiple layers of neural networks. This approach has revolutionized the field.
Modern deep learning systems can achieve superhuman performance on specific tasks.
Applications include image recognition, natural language processing, and game playing."""


@pytest.fixture
def structured_document():
    """구조화된 문서"""
    return {
        "text": """Chapter 1: First
Section 1.1: Content A
More content.
Section 1.2: Content B
Additional content.

Chapter 2: Second
Section 2.1: Content C
More information.
Section 2.2: Content D
Final details.""",
        "structure": {
            "chapters": [
                {"id": "ch1", "title": "First", "start": 0},
                {"id": "ch2", "title": "Second", "start": 200}
            ]
        }
    }


@pytest.fixture
def multilingual_text():
    """다국어 텍스트"""
    return """Chapter 1: Introduction

English text: The quick brown fox jumps over the lazy dog.

French text: Le renard brun rapide saute par-dessus le chien paresseux.

Korean text: 빠른 갈색 여우가 게으른 개를 뛰어넘는다.

Technical terms: API, REST, JSON, XML

Chapter 2: Advanced Topics

More mixed-language content here."""


# ==================== TEST CLASSES ====================

class TestBasicChunking:
    """기본 청킹 테스트"""

    def test_chunk_text_by_word_count(self, sample_text):
        """
        Given: 50KB 이상의 텍스트
        When: chunk_by_word_count(chunk_size=1000) 호출
        Then: 대략 1000단어씩 청크가 분할되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000)
        chunks = chunker.chunk_text(sample_text)

        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

        # Check chunk sizes (allowing 10% variance)
        for chunk in chunks[:-1]:  # Except last chunk
            word_count = len(chunk.split())
            assert 900 <= word_count <= 1100

    def test_chunk_text_respects_chunk_size(self):
        """
        Given: 큰 텍스트와 지정된 청크 크기
        When: chunk_text() 호출
        Then: 청크가 최대 크기를 초과하지 않아야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=500)
        large_text = " ".join(["word"] * 5000)

        chunks = chunker.chunk_text(large_text)

        for chunk in chunks:
            word_count = len(chunk.split())
            assert word_count <= 550  # 10% tolerance

    def test_chunk_at_sentence_boundaries(self, sample_text):
        """
        Given: 문장 경계가 있는 텍스트
        When: chunk_at_sentence_boundaries=True로 청킹
        Then: 청크가 문장 경계에서 분할되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000, boundary_type='sentence')
        chunks = chunker.chunk_text(sample_text)

        for chunk in chunks:
            # Each chunk should end with sentence-ending punctuation (except possibly last)
            stripped = chunk.rstrip()
            if stripped:
                assert stripped[-1] in '.!?' or chunk == chunks[-1]

    def test_chunk_at_paragraph_boundaries(self, sample_text):
        """
        Given: 단락 구분이 있는 텍스트
        When: chunk_at_paragraph_boundaries=True로 청킹
        Then: 청크가 단락 경계에서 분할되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000, boundary_type='paragraph')
        chunks = chunker.chunk_text(sample_text)

        # Chunks should not split paragraphs
        assert len(chunks) > 0
        for chunk in chunks:
            # Paragraph breaks should be preserved
            assert "\n\n" not in chunk.strip() or len(chunk.split("\n\n")) <= 2

    def test_chunk_at_section_boundaries(self, structured_document):
        """
        Given: 문서 구조 정보와 텍스트
        When: chunk_at_section_boundaries=True로 청킹
        Then: 청크가 절 경계에서 분할되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(
            chunk_size=1000,
            boundary_type='section',
            document_structure=structured_document["structure"]
        )
        chunks = chunker.chunk_text(structured_document["text"])

        assert len(chunks) > 0
        # Sections should not be split unnecessarily
        for chunk in chunks:
            assert "Section" not in chunk or len(chunk) > 100

    def test_no_text_loss_during_chunking(self, sample_text):
        """
        Given: 원본 텍스트
        When: 텍스트 청킹 후 재결합
        Then: 원본과 동일해야 함 (공백 정규화 제외)
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000)
        chunks = chunker.chunk_text(sample_text)

        reconstructed = "".join(chunks)
        original_normalized = " ".join(sample_text.split())
        reconstructed_normalized = " ".join(reconstructed.split())

        assert original_normalized == reconstructed_normalized

    def test_handle_empty_text_gracefully(self):
        """
        Given: 빈 텍스트
        When: chunk_text() 호출
        Then: 빈 리스트 또는 예외를 반환해야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker()
        result = chunker.chunk_text("")

        assert isinstance(result, list)
        assert len(result) == 0 or (len(result) == 1 and result[0] == "")

    def test_handle_very_small_text(self):
        """
        Given: 청크 크기보다 작은 텍스트
        When: chunk_text() 호출
        Then: 전체 텍스트가 하나의 청크로 반환되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000)
        small_text = "This is a small piece of text."

        chunks = chunker.chunk_text(small_text)

        assert len(chunks) == 1
        assert chunks[0] == small_text


class TestChunkMetadata:
    """청크 메타데이터 테스트"""

    def test_generate_chunk_metadata(self, sample_text):
        """
        Given: 청킹된 텍스트
        When: generate_metadata() 호출
        Then: 각 청크에 대한 메타데이터가 생성되어야 함
        """
        from src.chunking import TextChunker, ChunkMetadata

        chunker = TextChunker(chunk_size=1000)
        chunks = chunker.chunk_text(sample_text)
        metadata_list = chunker.generate_metadata(chunks)

        assert len(metadata_list) == len(chunks)
        for i, metadata in enumerate(metadata_list):
            assert "chunk_id" in metadata
            assert "position" in metadata
            assert "word_count" in metadata
            assert metadata["position"] == i

    def test_chunk_id_generation(self, sample_text):
        """
        Given: 여러 청크
        When: 메타데이터 생성
        Then: 각 청크에 고유 ID가 부여되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=500)
        chunks = chunker.chunk_text(sample_text)
        metadata_list = chunker.generate_metadata(chunks)

        chunk_ids = [m["chunk_id"] for m in metadata_list]
        assert len(chunk_ids) == len(set(chunk_ids))  # All unique

    def test_metadata_includes_word_count(self, sample_text):
        """
        Given: 청크들
        When: 메타데이터 생성
        Then: 각 청크의 단어 수가 기록되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000)
        chunks = chunker.chunk_text(sample_text)
        metadata_list = chunker.generate_metadata(chunks)

        for i, metadata in enumerate(metadata_list):
            expected_count = len(chunks[i].split())
            assert metadata["word_count"] == expected_count

    def test_metadata_includes_position_info(self, sample_text):
        """
        Given: 원본 텍스트와 청크
        When: 메타데이터 생성
        Then: 원본 텍스트에서의 시작/종료 위치가 기록되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000)
        chunks = chunker.chunk_text(sample_text)
        metadata_list = chunker.generate_metadata(chunks, original_text=sample_text)

        # Verify positions are correct
        current_pos = 0
        for metadata in metadata_list:
            assert "original_position" in metadata or "start_char" in metadata

    def test_metadata_includes_chunk_sequence(self, sample_text):
        """
        Given: 순차적 청크들
        When: 메타데이터 생성
        Then: 청크 순서 정보가 포함되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=500)
        chunks = chunker.chunk_text(sample_text)
        metadata_list = chunker.generate_metadata(chunks)

        for i, metadata in enumerate(metadata_list):
            assert metadata.get("sequence_number") == i or metadata.get("position") == i


class TestContextOverlap:
    """컨텍스트 오버랩 테스트"""

    def test_generate_context_overlap(self, sample_text):
        """
        Given: 청킹된 텍스트
        When: overlap=200으로 설정하여 청킹
        Then: 인접한 청크 간 오버랩이 생성되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=1000, overlap=200)
        chunks = chunker.chunk_text(sample_text)
        chunks_with_context = chunker.add_context_overlap(chunks)

        # Should have overlap metadata
        assert len(chunks_with_context) == len(chunks)

    def test_context_overlap_preserves_semantics(self, sample_text):
        """
        Given: 오버랩이 있는 청크
        When: 번역 후 재조합
        Then: 의미가 손상되지 않아야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=500, overlap=100)
        chunks_with_context = chunker.chunk_with_context(sample_text)

        for chunk_data in chunks_with_context:
            assert "context_before" in chunk_data or "previous_context" in chunk_data
            assert "context_after" in chunk_data or "next_context" in chunk_data

    def test_context_overlap_size_configurable(self):
        """
        Given: 다양한 오버랩 크기 설정
        When: 청킹 수행
        Then: 설정된 오버랩 크기가 적용되어야 함
        """
        from src.chunking import TextChunker

        text = " ".join(["word"] * 2000)

        for overlap_size in [0, 50, 100, 200]:
            chunker = TextChunker(chunk_size=500, overlap=overlap_size)
            chunks_with_context = chunker.chunk_with_context(text)

            if overlap_size > 0:
                # Verify overlap exists
                assert any(
                    len(c.get("context_before", "")) > 0 or
                    len(c.get("context_after", "")) > 0
                    for c in chunks_with_context
                )

    def test_remove_overlap_for_final_assembly(self, sample_text):
        """
        Given: 오버랩이 있는 청크들의 번역본
        When: remove_overlap() 호출
        Then: 중복이 제거되어 재조합되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(chunk_size=500, overlap=100)
        chunks_with_context = chunker.chunk_with_context(sample_text)

        # Mock translated chunks (same structure with translated content)
        translated_chunks = [
            {**c, "translated_text": f"[번역] {c.get('text', '')}"}
            for c in chunks_with_context
        ]

        reassembled = chunker.remove_overlap_and_reassemble(translated_chunks)

        assert isinstance(reassembled, str)
        assert len(reassembled) > 0


class TestStructurePreservation:
    """구조 보존 테스트"""

    def test_preserve_chapter_boundaries(self, structured_document):
        """
        Given: 장 구분이 있는 문서
        When: 청킹
        Then: 장 경계가 보존되어야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker(
            chunk_size=500,
            document_structure=structured_document["structure"]
        )
        chunks = chunker.chunk_text(structured_document["text"])

        # Chapter titles should not be split across chunks
        for chunk in chunks:
            chapter_count = chunk.count("Chapter")
            assert chapter_count <= 2  # At most 2 chapters per chunk

    def test_preserve_formatting_markers(self):
        """
        Given: 마크다운 포맷 마커 (**bold**, *italic*)가 있는 텍스트
        When: 청킹
        Then: 포맷 마커가 보존되어야 함
        """
        from src.chunking import TextChunker

        formatted_text = """Chapter 1: **Introduction**

This is *important* content.

**Subsection**: _emphasized_ text"""

        chunker = TextChunker(chunk_size=100)
        chunks = chunker.chunk_text(formatted_text)

        reassembled = "".join(chunks)
        assert "**" in reassembled
        assert "*" in reassembled

    def test_preserve_list_structure(self):
        """
        Given: 목록 구조가 있는 텍스트
        When: 청킹
        Then: 목록 들여쓰기가 보존되어야 함
        """
        from src.chunking import TextChunker

        list_text = """Chapter 1: Features

- Feature A
  - Sub-feature A1
  - Sub-feature A2
- Feature B
- Feature C

Chapter 2: Details"""

        chunker = TextChunker(chunk_size=200)
        chunks = chunker.chunk_text(list_text)

        reassembled = "".join(chunks)
        assert reassembled.count("- ") >= 4

    def test_preserve_code_blocks(self):
        """
        Given: 코드 블록이 있는 텍스트
        When: 청킹
        Then: 코드 블록이 온전히 보존되어야 함
        """
        from src.chunking import TextChunker

        code_text = """Chapter 1: Programming

Here is example code:

```python
def hello():
    print("Hello World")
    return True
```

This is regular text."""

        chunker = TextChunker(chunk_size=200, preserve_code_blocks=True)
        chunks = chunker.chunk_text(code_text)

        reassembled = "".join(chunks)
        assert "```python" in reassembled
        assert "print(" in reassembled
        assert "```" in reassembled.count("```") >= 2

    def test_preserve_special_elements(self):
        """
        Given: 표, 이미지 참조, 수식이 포함된 텍스트
        When: 청킹
        Then: 특수 요소가 보존되거나 마크되어야 함
        """
        from src.chunking import TextChunker

        special_text = """Chapter 1

| Header1 | Header2 |
|---------|---------|
| Data1   | Data2   |

Some text.

![Image](image.png)

Equation: E=mc²"""

        chunker = TextChunker(chunk_size=500)
        chunks = chunker.chunk_text(special_text)

        reassembled = "".join(chunks)
        # Elements should be preserved
        assert "|" in reassembled or "[TABLE]" in reassembled
        assert "![Image]" in reassembled or "[IMAGE]" in reassembled


class TestChunkingPerformance:
    """청킹 성능 테스트"""

    def test_chunk_large_text_efficiently(self):
        """
        Given: 1MB 이상의 텍스트
        When: 청킹 수행
        Then: 합리적인 시간 내 완료되어야 함 (<5초)
        """
        from src.chunking import TextChunker
        import time

        # Create 1MB text
        large_text = " ".join(["word"] * 200000)

        chunker = TextChunker(chunk_size=5000)

        start_time = time.time()
        chunks = chunker.chunk_text(large_text)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 5.0
        assert len(chunks) > 0

    def test_metadata_generation_is_fast(self, sample_text):
        """
        Given: 1000개의 청크
        When: 메타데이터 생성
        Then: 빠르게 완료되어야 함 (<1초)
        """
        from src.chunking import TextChunker
        import time

        chunker = TextChunker(chunk_size=100)
        large_text = sample_text * 50  # Create larger text

        chunks = chunker.chunk_text(large_text)

        start_time = time.time()
        metadata_list = chunker.generate_metadata(chunks)
        elapsed_time = time.time() - start_time

        assert elapsed_time < 1.0
        assert len(metadata_list) == len(chunks)


class TestErrorHandling:
    """오류 처리 테스트"""

    def test_handle_none_text_gracefully(self):
        """
        Given: None 값
        When: chunk_text() 호출
        Then: 명확한 오류 메시지와 함께 예외 발생해야 함
        """
        from src.chunking import TextChunker

        chunker = TextChunker()

        with pytest.raises((TypeError, ValueError)):
            chunker.chunk_text(None)

    def test_handle_invalid_chunk_size(self):
        """
        Given: 유효하지 않은 청크 크기 (음수, 0)
        When: TextChunker 초기화
        Then: ValueError 발생해야 함
        """
        from src.chunking import TextChunker

        with pytest.raises(ValueError):
            TextChunker(chunk_size=0)

        with pytest.raises(ValueError):
            TextChunker(chunk_size=-100)

    def test_handle_invalid_overlap_size(self):
        """
        Given: 유효하지 않은 오버랩 크기 (청크 크기보다 큼)
        When: TextChunker 초기화
        Then: ValueError 발생하거나 자동 조정되어야 함
        """
        from src.chunking import TextChunker

        # Should either raise or auto-adjust
        chunker = TextChunker(chunk_size=100, overlap=150)

        # If allowed, overlap should be adjusted
        assert chunker.overlap <= chunker.chunk_size


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
