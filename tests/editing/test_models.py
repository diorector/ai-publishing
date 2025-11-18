# 편집 모듈 데이터 모델 테스트
# 작성일: 2025-11-18
# 목적: 문서, 편집 결과, 메타데이터 모델 검증

import pytest
from datetime import datetime
from typing import List
from dataclasses import dataclass


class TestDocumentModel:
    """문서 모델 테스트"""

    def test_document_creation_with_required_fields(self):
        """필수 필드로 문서 객체 생성"""
        from src.editing.models.document import Document

        doc = Document(
            id="doc-001",
            title="테스트 문서",
            content="이것은 테스트 내용입니다.",
            domain="startup",
            target_audience="개발자"
        )

        assert doc.id == "doc-001"
        assert doc.title == "테스트 문서"
        assert doc.content == "이것은 테스트 내용입니다."
        assert doc.domain == "startup"
        assert doc.target_audience == "개발자"

    def test_document_word_count_calculation(self):
        """단어 수 자동 계산"""
        from src.editing.models.document import Document

        doc = Document(
            id="doc-002",
            title="단어 테스트",
            content="한국어 문서입니다. 단어 수를 세어야 합니다. 여러 문장이 있습니다.",
            domain="finance",
            target_audience="투자자"
        )

        assert doc.word_count > 0
        assert doc.word_count == len(doc.content.split())

    def test_document_structure_analysis(self):
        """문서 구조 분석"""
        from src.editing.models.document import Document

        content = """# 제1장: 소개

이것은 첫 번째 섹션입니다.

## 제1절: 배경

배경 설명 내용입니다.

# 제2장: 본론

본론 내용입니다.
"""

        doc = Document(
            id="doc-003",
            title="구조 테스트",
            content=content,
            domain="education",
            target_audience="학생"
        )

        assert doc.structure is not None
        assert len(doc.structure.chapters) >= 1
        assert doc.structure.total_sections >= 1

    def test_document_metadata_extraction(self):
        """메타데이터 자동 추출"""
        from src.editing.models.document import Document

        doc = Document(
            id="doc-004",
            title="메타데이터 테스트",
            content="테스트 내용입니다.",
            domain="law",
            target_audience="변호사",
            metadata={"author": "테스트 작성자", "version": "1.0"}
        )

        assert doc.metadata["author"] == "테스트 작성자"
        assert doc.metadata["version"] == "1.0"
        assert "created_at" in doc.metadata or hasattr(doc, "created_at")


class TestEditResultModel:
    """편집 결과 모델 테스트"""

    def test_edit_result_creation(self):
        """편집 결과 객체 생성"""
        from src.editing.models.edit_result import EditResult, EditStage, Change

        result = EditResult(
            document_id="doc-001",
            stage=EditStage.PROOFREADING,
            original_text="원본 텍스트입니다.",
            edited_text="수정된 텍스트입니다."
        )

        assert result.document_id == "doc-001"
        assert result.stage == EditStage.PROOFREADING
        assert result.original_text == "원본 텍스트입니다."
        assert result.edited_text == "수정된 텍스트입니다."

    def test_edit_result_change_tracking(self):
        """변경 사항 추적"""
        from src.editing.models.edit_result import EditResult, EditStage, Change

        changes = [
            Change(
                type="spacing",
                original="한글 영어",
                modified="한글 영어",
                reason="띄어쓰기 규칙"
            ),
            Change(
                type="spelling",
                original="틀렸습니다",
                modified="틀렸습니다",
                reason="맞춤법"
            )
        ]

        result = EditResult(
            document_id="doc-002",
            stage=EditStage.PROOFREADING,
            original_text="원본",
            edited_text="수정본",
            changes=changes
        )

        assert len(result.changes) == 2
        assert result.changes[0].type == "spacing"
        assert result.changes[1].type == "spelling"

    def test_edit_result_quality_score(self):
        """품질 점수 계산"""
        from src.editing.models.edit_result import EditResult, EditStage

        result = EditResult(
            document_id="doc-003",
            stage=EditStage.FACT_CHECKING,
            original_text="원본",
            edited_text="수정본",
            quality_score=92.5
        )

        assert result.quality_score == 92.5
        assert result.quality_score >= 0 and result.quality_score <= 100


class TestMetadataModel:
    """메타데이터 모델 테스트"""

    def test_document_metadata_creation(self):
        """문서 메타데이터 생성"""
        from src.editing.models.metadata import DocumentMetadata

        metadata = DocumentMetadata(
            author="테스트 저자",
            title="테스트 제목",
            domain="startup",
            created_date=datetime.now(),
            page_count=100,
            word_count=50000
        )

        assert metadata.author == "테스트 저자"
        assert metadata.domain == "startup"
        assert metadata.page_count == 100

    def test_edit_statistics(self):
        """편집 통계"""
        from src.editing.models.metadata import EditStatistics

        stats = EditStatistics(
            total_changes=125,
            spacing_errors=45,
            spelling_errors=30,
            foreign_language_issues=20,
            formatting_issues=30
        )

        assert stats.total_changes == 125
        assert stats.spacing_errors == 45
        assert stats.spelling_errors + stats.foreign_language_issues + stats.formatting_issues == 80


class TestEditConfigModel:
    """편집 설정 모델 테스트"""

    def test_proofreading_config_creation(self):
        """교정 설정 생성"""
        from src.editing.models.config import ProofreadingConfig

        config = ProofreadingConfig(
            check_spacing=True,
            check_spelling=True,
            check_foreign_language=True,
            check_numbers=True,
            check_symbols=True
        )

        assert config.check_spacing is True
        assert config.check_spelling is True

    def test_fact_checking_config_creation(self):
        """교열 설정 생성"""
        from src.editing.models.config import FactCheckingConfig

        config = FactCheckingConfig(
            verify_statistics=True,
            verify_dates=True,
            verify_organizations=True,
            verify_people_names=True,
            check_outdated_info=True,
            reference_year=2025
        )

        assert config.verify_statistics is True
        assert config.reference_year == 2025

    def test_copywriting_config_creation(self):
        """윤문 설정 생성"""
        from src.editing.models.config import CopywritingConfig

        config = CopywritingConfig(
            improve_clarity=True,
            improve_readability=True,
            maintain_tone=True,
            improve_flow=True,
            preserve_intent=True
        )

        assert config.improve_clarity is True
        assert config.preserve_intent is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
