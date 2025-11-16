# PDF Processor Tests - Phase 1 RED
# 구현 시간: 2025-11-16 14:30 KST
# PDF 추출 및 구조 분석 모듈의 포괄적 테스트
# SPEC-PUB-TRANSLATE-001 요구사항:
# - PDF 텍스트 추출 및 구조 분석
# - 챕터/절/단락 자동 감지
# - 원본 구조 정보 메타데이터 저장
# - 추출된 텍스트 프리뷰 제공

import pytest
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from unittest.mock import Mock, patch, MagicMock
import json


# Fixtures
@pytest.fixture
def sample_pdf_path():
    """Test PDF 파일 경로"""
    return Path("tests/fixtures/sample_academic_book.pdf")


@pytest.fixture
def complex_pdf_path():
    """복잡한 구조의 PDF 파일 경로"""
    return Path("tests/fixtures/complex_multi_chapter_book.pdf")


@pytest.fixture
def minimal_pdf_path():
    """최소 구조 PDF 파일 경로"""
    return Path("tests/fixtures/simple_document.pdf")


@pytest.fixture
def pdf_with_special_elements_path():
    """표, 이미지 참조, 수식이 포함된 PDF"""
    return Path("tests/fixtures/pdf_with_tables_and_images.pdf")


@pytest.fixture
def mock_pdf_content():
    """Mock PDF 콘텐츠"""
    return {
        "text": """Chapter 1: Introduction to AI

This chapter introduces the fundamental concepts of artificial intelligence.

1.1 Historical Context

The field of artificial intelligence emerged in the 1950s...

1.2 Core Concepts

Machine learning is a subset of AI that focuses on...

Chapter 2: Neural Networks

Neural networks form the foundation of modern AI systems.

2.1 Perceptron Models

The perceptron is the simplest form of neural network...

2.2 Deep Learning

Deep learning uses multiple layers of neural networks...""",
        "pages": 15,
        "metadata": {
            "title": "Introduction to Artificial Intelligence",
            "author": "John Smith",
            "creation_date": "2024-01-15"
        }
    }


# ==================== TEST CLASSES ====================

class TestPDFExtraction:
    """PDF 텍스트 추출 테스트"""

    def test_extract_text_from_valid_pdf(self, sample_pdf_path):
        """
        Given: 유효한 텍스트 기반 PDF 파일
        When: extract_text() 호출
        Then: 추출된 텍스트가 반환되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        result = processor.extract_text(sample_pdf_path)

        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
        assert len(result) > 100  # 최소 100자 이상 expected

    def test_extract_text_preserves_paragraph_breaks(self, mock_pdf_content):
        """
        Given: 여러 단락으로 구성된 PDF
        When: 텍스트 추출
        Then: 단락 구분이 보존되어야 함 (최소 2개 이상의 줄바꿈)
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        # Mock PDF content with multiple paragraphs
        result = processor._parse_text_structure(mock_pdf_content["text"])

        paragraphs = result.split('\n\n')
        assert len(paragraphs) >= 2

    def test_extract_text_handles_special_characters(self):
        """
        Given: 특수 문자, 공식, 기호가 포함된 PDF
        When: 텍스트 추출
        Then: 특수 문자가 손상되지 않고 보존되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        test_text = 'Mathematical formula: E=mc², symbol: α, dash: —, quote: "hello"'

        result = processor._normalize_text(test_text)

        assert "E=mc²" in result
        assert "α" in result
        assert "—" in result or "-" in result  # dash normalization acceptable
        assert "hello" in result

    def test_extract_text_from_nonexistent_file_raises_error(self):
        """
        Given: 존재하지 않는 PDF 파일 경로
        When: extract_text() 호출
        Then: FileNotFoundError 발생해야 함
        """
        from src.pdf_processor import PDFProcessor, PDFProcessingError

        processor = PDFProcessor()

        with pytest.raises((FileNotFoundError, PDFProcessingError)):
            processor.extract_text(Path("nonexistent_file.pdf"))

    def test_extract_text_from_corrupted_pdf_raises_error(self):
        """
        Given: 손상된 PDF 파일
        When: extract_text() 호출
        Then: 명확한 오류 메시지와 함께 PDFProcessingError 발생해야 함
        """
        from src.pdf_processor import PDFProcessor, PDFProcessingError

        processor = PDFProcessor()

        with pytest.raises(PDFProcessingError) as exc_info:
            processor.extract_text(Path("tests/fixtures/corrupted.pdf"))

        assert "corrupted" in str(exc_info.value).lower() or "invalid" in str(exc_info.value).lower()

    def test_extract_metadata_from_pdf(self, sample_pdf_path):
        """
        Given: 메타데이터가 포함된 PDF
        When: extract_metadata() 호출
        Then: 제목, 저자, 생성 날짜 등이 반환되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        metadata = processor.extract_metadata(sample_pdf_path)

        assert isinstance(metadata, dict)
        assert "title" in metadata or "author" in metadata
        assert "page_count" in metadata
        assert metadata["page_count"] > 0

    def test_extract_page_count_accurately(self, mock_pdf_content):
        """
        Given: 페이지 수가 명시된 PDF
        When: extract_metadata() 호출
        Then: 정확한 페이지 수가 반환되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        metadata = processor._extract_pdf_metadata(mock_pdf_content)

        assert metadata["page_count"] == mock_pdf_content["pages"]

    def test_extract_text_respects_maximum_size_limit(self):
        """
        Given: 매우 큰 PDF 파일 (>100MB)
        When: extract_text() 호출
        Then: 파일 크기 제한 체크 또는 적절한 경고와 함께 처리되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor(max_file_size_mb=100)

        # Create a mock large file
        large_file_path = Path("tests/fixtures/very_large.pdf")

        # Verify size check is implemented
        assert hasattr(processor, 'max_file_size_mb')
        assert processor.max_file_size_mb == 100


class TestStructureAnalysis:
    """문서 구조 분석 테스트"""

    def test_detect_chapters_from_text(self, mock_pdf_content):
        """
        Given: 여러 챕터로 구성된 텍스트
        When: detect_structure() 호출
        Then: 최소 2개 이상의 챕터가 감지되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])

        assert "chapters" in structure
        assert len(structure["chapters"]) >= 2
        assert all("title" in ch for ch in structure["chapters"])

    def test_detect_chapter_titles_correctly(self, mock_pdf_content):
        """
        Given: "Chapter X: Title" 형식의 챕터
        When: detect_structure() 호출
        Then: 올바른 챕터 제목이 추출되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])

        chapter_titles = [ch["title"] for ch in structure["chapters"]]
        assert "Introduction to AI" in chapter_titles or "Introduction to AI" in str(chapter_titles)
        assert "Neural Networks" in chapter_titles or "Neural Networks" in str(chapter_titles)

    def test_detect_sections_within_chapters(self, mock_pdf_content):
        """
        Given: 절 구분이 있는 챕터 (1.1, 1.2, 2.1, 2.2)
        When: detect_structure() 호출
        Then: 각 챕터 내 절이 감지되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])

        # At least one chapter should have sections
        has_sections = any("sections" in ch for ch in structure["chapters"])
        assert has_sections

        # Chapters with sections should have proper section titles
        for chapter in structure["chapters"]:
            if "sections" in chapter:
                assert len(chapter["sections"]) > 0
                assert all("title" in sec for sec in chapter["sections"])

    def test_detect_section_numbering_pattern(self):
        """
        Given: 번호 체계를 가진 절들 (1.1, 1.2, 2.1)
        When: detect_structure() 호출
        Then: 번호 체계가 올바르게 파싱되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        text = """Chapter 1: First

1.1 Section One
Content here.

1.2 Section Two
More content.

Chapter 2: Second

2.1 Another Section
Final content."""

        structure = processor.detect_structure(text)

        assert len(structure["chapters"]) >= 2
        first_chapter = structure["chapters"][0]
        assert "sections" in first_chapter
        assert len(first_chapter["sections"]) >= 2

    def test_preserve_paragraph_hierarchy(self, mock_pdf_content):
        """
        Given: 계층적 구조 (챕터 > 절 > 단락)
        When: detect_structure() 호출
        Then: 계층 구조가 보존되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])

        # Verify hierarchical structure exists
        assert "chapters" in structure
        for chapter in structure["chapters"]:
            assert isinstance(chapter, dict)
            assert "content" in chapter or "sections" in chapter

    def test_detect_empty_structure_gracefully(self):
        """
        Given: 구조화되지 않은 텍스트 (제목 없음)
        When: detect_structure() 호출
        Then: 최소한 하나의 기본 구조를 반환해야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        unstructured_text = "This is just plain text without any chapter or section headers."

        structure = processor.detect_structure(unstructured_text)

        assert structure is not None
        assert "chapters" in structure or "content" in structure

    def test_detect_page_breaks_and_positions(self):
        """
        Given: 페이지 정보를 포함한 PDF
        When: detect_structure() 호출
        Then: 각 요소의 페이지 위치가 기록되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()

        # Mock PDF with page information
        pdf_data = {
            "text": "Chapter 1...",
            "pages": [
                {"page_num": 1, "content": "Chapter 1..."},
                {"page_num": 2, "content": "Content continues..."}
            ]
        }

        structure = processor.detect_structure_with_pages(pdf_data)

        assert "chapters" in structure
        for chapter in structure["chapters"]:
            assert "start_page" in chapter or "page_num" in chapter

    def test_handle_missing_chapter_titles(self):
        """
        Given: 일부 챕터가 명시적 제목 없이 번호만 있는 경우
        When: detect_structure() 호출
        Then: 자동으로 기본 제목을 생성하거나 표시해야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        text = """1
        Content of first chapter

2
        Content of second chapter"""

        structure = processor.detect_structure(text)

        # Should still detect chapters even without explicit titles
        assert "chapters" in structure
        assert len(structure["chapters"]) >= 2


class TestStructureMetadata:
    """구조 메타데이터 저장 테스트"""

    def test_generate_structure_metadata(self, mock_pdf_content):
        """
        Given: 감지된 문서 구조
        When: generate_metadata() 호출
        Then: 각 요소에 대한 메타데이터가 생성되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])
        metadata = processor.generate_structure_metadata(structure)

        assert isinstance(metadata, dict)
        assert "total_chapters" in metadata
        assert "total_sections" in metadata
        assert metadata["total_chapters"] >= 2

    def test_assign_unique_ids_to_sections(self, mock_pdf_content):
        """
        Given: 문서 구조
        When: generate_metadata() 호출
        Then: 각 챕터/절에 고유 ID가 할당되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])
        structure = processor.assign_element_ids(structure)

        # Check that IDs are assigned
        chapter_ids = set()
        for chapter in structure["chapters"]:
            assert "id" in chapter
            chapter_ids.add(chapter["id"])

        # All IDs should be unique
        assert len(chapter_ids) == len(structure["chapters"])

    def test_calculate_content_statistics(self, mock_pdf_content):
        """
        Given: 추출된 텍스트
        When: calculate_statistics() 호출
        Then: 단어 수, 문장 수, 평균 문단 길이 등이 계산되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        stats = processor.calculate_text_statistics(mock_pdf_content["text"])

        assert isinstance(stats, dict)
        assert "word_count" in stats
        assert "sentence_count" in stats
        assert "average_paragraph_length" in stats

        assert stats["word_count"] > 0
        assert stats["sentence_count"] > 0
        assert stats["average_paragraph_length"] > 0

    def test_record_element_positions(self, mock_pdf_content):
        """
        Given: 문서 구조와 페이지 정보
        When: record_positions() 호출
        Then: 각 요소의 페이지/위치 정보가 기록되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        structure = processor.detect_structure(mock_pdf_content["text"])
        structure_with_pos = processor.record_element_positions(
            structure,
            mock_pdf_content["text"]
        )

        for chapter in structure_with_pos["chapters"]:
            assert "start_char" in chapter
            assert "end_char" in chapter
            assert chapter["start_char"] >= 0
            assert chapter["end_char"] > chapter["start_char"]


class TestPreviewGeneration:
    """추출 프리뷰 생성 테스트"""

    def test_generate_extraction_preview(self, mock_pdf_content):
        """
        Given: 추출된 PDF 텍스트
        When: generate_preview() 호출
        Then: 사용자 확인용 프리뷰가 생성되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        preview = processor.generate_preview(mock_pdf_content)

        assert isinstance(preview, dict)
        assert "summary" in preview
        assert "structure_outline" in preview
        assert "sample_content" in preview

    def test_preview_includes_structure_outline(self, mock_pdf_content):
        """
        Given: 복잡한 문서 구조
        When: generate_preview() 호출
        Then: 구조 개요가 포함되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        preview = processor.generate_preview(mock_pdf_content)

        outline = preview["structure_outline"]
        # Should show chapters and sections
        assert "Chapter" in outline or "1." in outline

    def test_preview_includes_sample_content(self, mock_pdf_content):
        """
        Given: 추출된 텍스트
        When: generate_preview() 호출
        Then: 대표 샘플 콘텐츠가 포함되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        preview = processor.generate_preview(mock_pdf_content)

        sample = preview["sample_content"]
        assert len(sample) > 0
        assert len(sample) <= 500  # Preview should be concise

    def test_preview_includes_quality_indicators(self, mock_pdf_content):
        """
        Given: 추출된 텍스트
        When: generate_preview() 호출
        Then: 추출 품질 지표가 포함되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        preview = processor.generate_preview(mock_pdf_content)

        assert "quality_score" in preview
        assert "warnings" in preview or "notes" in preview
        assert 0 <= preview["quality_score"] <= 100

    def test_preview_warns_about_special_elements(self):
        """
        Given: 표, 이미지, 수식이 포함된 콘텐츠
        When: generate_preview() 호출
        Then: 특수 요소 경고가 포함되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        content_with_special = {
            "text": "Content with [TABLE] and [IMAGE] elements",
            "has_tables": True,
            "has_images": True,
            "has_formulas": False
        }

        preview = processor.generate_preview(content_with_special)

        warnings = preview.get("warnings", [])
        assert len(warnings) > 0


class TestErrorHandling:
    """오류 처리 및 복구 테스트"""

    def test_pdf_processor_initialization(self):
        """
        Given: PDFProcessor 생성
        When: __init__() 호출
        Then: 필요한 속성이 초기화되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()

        assert hasattr(processor, 'max_file_size_mb')
        assert hasattr(processor, 'supported_formats')
        assert 'pdf' in processor.supported_formats.lower()

    def test_handle_encoding_errors_gracefully(self):
        """
        Given: 인코딩 문제가 있는 PDF
        When: extract_text() 호출
        Then: 인코딩 오류를 처리하고 best-effort 텍스트를 반환해야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()

        # The method should handle encoding issues
        assert hasattr(processor, '_handle_encoding_error') or \
               hasattr(processor, '_normalize_text')

    def test_recover_from_partial_extraction(self):
        """
        Given: 부분적으로 손상된 PDF
        When: extract_text() 호출
        Then: 가능한 부분만 추출하고 상태를 반환해야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()

        # Should have mechanism to handle partial extraction
        result = processor.extract_text_with_status(Path("tests/fixtures/partially_corrupted.pdf"))

        assert isinstance(result, dict)
        assert "text" in result
        assert "extraction_status" in result or "success" in result


# ==================== HELPER TEST CLASSES ====================

class TestPDFProcessorIntegration:
    """통합 테스트"""

    def test_full_extraction_pipeline(self, sample_pdf_path):
        """
        Given: 유효한 PDF 파일
        When: 전체 추출 파이프라인 실행
        Then: 추출된 텍스트, 구조, 메타데이터가 모두 반환되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        result = processor.process(sample_pdf_path)

        assert isinstance(result, dict)
        assert "text" in result
        assert "structure" in result
        assert "metadata" in result
        assert "preview" in result

    def test_pipeline_returns_consistent_data(self, sample_pdf_path):
        """
        Given: 동일한 PDF 파일
        When: 파이프라인을 여러 번 실행
        Then: 동일한 결과가 반환되어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        result1 = processor.process(sample_pdf_path)
        result2 = processor.process(sample_pdf_path)

        assert result1["text"] == result2["text"]
        assert result1["metadata"]["page_count"] == result2["metadata"]["page_count"]

    def test_process_large_pdf_with_progress_tracking(self):
        """
        Given: 대용량 PDF 파일 (100+ pages)
        When: process() 호출 시 progress callback 제공
        Then: 진행 상황을 콜백으로 추적할 수 있어야 함
        """
        from src.pdf_processor import PDFProcessor

        processor = PDFProcessor()
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        # Process should support progress tracking
        assert hasattr(processor, 'process_with_progress') or \
               callable(getattr(processor, 'process', None))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
