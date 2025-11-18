# 편집 모듈 데이터 모델 확장 테스트
# 작성일: 2025-11-18
# 목적: config, metadata, edit_result 모델의 높은 커버리지

import pytest
from datetime import datetime
from src.editing.models.config import (
    ProofreadingConfig,
    FactCheckingConfig,
    CopywritingConfig,
    EditingConfig
)
from src.editing.models.metadata import (
    DocumentMetadata,
    EditStatistics,
    ProofreadingStatistics,
    FactCheckingStatistics,
    CopywritingStatistics
)
from src.editing.models.edit_result import EditResult, EditStage, Change, BatchEditResult


class TestProofreadingConfigExtended:
    """교정 설정 확장 테스트"""

    def test_get_active_checks_all_enabled(self):
        """모든 검사 활성화"""
        config = ProofreadingConfig(
            check_spacing=True,
            check_spelling=True,
            check_foreign_language=True,
            check_numbers=True,
            check_symbols=True,
            check_consistency=True
        )
        checks = config.get_active_checks()
        assert len(checks) == 6
        assert "spacing" in checks
        assert "spelling" in checks

    def test_get_active_checks_selective(self):
        """선택적 검사 활성화"""
        config = ProofreadingConfig(
            check_spacing=True,
            check_spelling=False,
            check_foreign_language=True,
            check_numbers=False,
            check_symbols=False,
            check_consistency=False
        )
        checks = config.get_active_checks()
        assert len(checks) == 2
        assert "spacing" in checks
        assert "foreign_language" in checks

    def test_custom_rules(self):
        """커스텀 규칙"""
        custom_rules = {"rule1": "value1", "rule2": "value2"}
        config = ProofreadingConfig(custom_rules=custom_rules)
        assert config.custom_rules == custom_rules

    def test_intensity_levels(self):
        """강도 레벨"""
        for intensity in ["minimal", "standard", "strict"]:
            config = ProofreadingConfig(intensity=intensity)
            assert config.intensity == intensity


class TestFactCheckingConfigExtended:
    """교열 설정 확장 테스트"""

    def test_get_active_verifications_all(self):
        """모든 검증 활성화"""
        config = FactCheckingConfig(
            verify_statistics=True,
            verify_dates=True,
            verify_organizations=True,
            verify_people_names=True,
            check_outdated_info=True
        )
        verifications = config.get_active_verifications()
        assert len(verifications) == 5
        assert "statistics" in verifications

    def test_reference_year_configuration(self):
        """기준 년도 설정"""
        config = FactCheckingConfig(reference_year=2020)
        assert config.reference_year == 2020

    def test_context7_toggle(self):
        """Context7 사용 여부"""
        config1 = FactCheckingConfig(use_context7=True)
        assert config1.use_context7 is True

        config2 = FactCheckingConfig(use_context7=False)
        assert config2.use_context7 is False

    def test_intensity_for_fact_checking(self):
        """팩트 검증 강도"""
        for intensity in ["light", "standard", "deep"]:
            config = FactCheckingConfig(intensity=intensity)
            assert config.intensity == intensity


class TestCopywritingConfigExtended:
    """윤문 설정 확장 테스트"""

    def test_get_active_improvements(self):
        """활성화된 개선 항목"""
        config = CopywritingConfig(
            improve_clarity=True,
            improve_readability=True,
            maintain_tone=True,
            improve_flow=True,
            preserve_intent=True
        )
        improvements = config.get_active_improvements()
        assert len(improvements) == 5
        assert "clarity" in improvements
        assert "intent_preservation" in improvements

    def test_target_grade_level(self):
        """목표 학년 수준"""
        config = CopywritingConfig(target_grade_level=10)
        assert config.target_grade_level == 10

    def test_selective_improvements(self):
        """선택적 개선"""
        config = CopywritingConfig(
            improve_clarity=True,
            improve_readability=False,
            maintain_tone=True,
            improve_flow=False,
            preserve_intent=True
        )
        improvements = config.get_active_improvements()
        assert len(improvements) == 3


class TestEditingConfigExtended:
    """전체 편집 설정"""

    def test_editing_config_creation(self):
        """편집 설정 생성"""
        config = EditingConfig(
            document_domain="startup",
            target_audience="investors"
        )
        assert config.document_domain == "startup"
        assert config.target_audience == "investors"

    def test_chunk_and_section_sizes(self):
        """청크 및 섹션 크기"""
        config = EditingConfig(
            max_chunk_size=2000,
            fact_check_section_size=4000
        )
        assert config.max_chunk_size == 2000
        assert config.fact_check_section_size == 4000

    def test_worker_configuration(self):
        """워커 설정"""
        config = EditingConfig(
            max_workers=8,
            enable_parallel_processing=True
        )
        assert config.max_workers == 8
        assert config.enable_parallel_processing is True

    def test_custom_terminology(self):
        """커스텀 용어"""
        terminology = {"AI": "인공지능", "ML": "기계학습"}
        config = EditingConfig(custom_terminology=terminology)
        assert config.custom_terminology == terminology

    def test_settings_summary(self):
        """설정 요약"""
        config = EditingConfig()
        summary = config.get_settings_summary()
        assert "document_domain" in summary
        assert "target_audience" in summary
        assert "max_chunk_size" in summary


class TestMetadataExtended:
    """메타데이터 확장 테스트"""

    def test_document_metadata_to_dict(self):
        """메타데이터 딕셔너리 변환"""
        metadata = DocumentMetadata(
            author="테스트 저자",
            title="테스트 제목",
            domain="startup",
            created_date=datetime(2025, 11, 18),
            page_count=50,
            word_count=10000,
            tags=["urgent", "important"],
            custom_fields={"priority": "high"}
        )
        d = metadata.to_dict()
        assert d["author"] == "테스트 저자"
        assert d["page_count"] == 50
        assert "urgent" in d["tags"]

    def test_edit_statistics_summary(self):
        """편집 통계 요약"""
        stats = EditStatistics(
            total_changes=100,
            spacing_errors=30,
            spelling_errors=40,
            foreign_language_issues=20,
            formatting_issues=10
        )
        summary = stats.get_summary()
        assert summary["total_changes"] == 100
        assert summary["spacing_errors"] == 30

    def test_edit_statistics_error_distribution(self):
        """오류 분포"""
        stats = EditStatistics(
            total_changes=100,
            spacing_errors=40,
            spelling_errors=30,
            foreign_language_issues=20,
            formatting_issues=10
        )
        distribution = stats.get_error_distribution()
        assert distribution["spacing"] == 40.0
        assert distribution["spelling"] == 30.0

    def test_proofreading_statistics(self):
        """교정 통계"""
        stats = ProofreadingStatistics(
            total_changes=50,
            spacing_errors=20,
            consistency_issues=5,
            number_formatting_issues=3,
            unit_formatting_issues=2
        )
        summary = stats.get_summary()
        assert summary["consistency_issues"] == 5
        assert summary["number_formatting_issues"] == 3

    def test_fact_checking_statistics(self):
        """교열 통계"""
        stats = FactCheckingStatistics(
            fact_checking_items=100,
            verified_items=95,
            suspicious_items=3,
            error_items=2,
            editor_notes=5
        )
        summary = stats.get_summary()
        assert summary["verified_items"] == 95
        assert stats.get_verification_rate() == 95.0

    def test_copywriting_statistics(self):
        """윤문 통계"""
        stats = CopywritingStatistics(
            total_changes=50,
            clarity_improvements=15,
            readability_improvements=20,
            tone_consistency_improvements=10,
            flow_improvements=5
        )
        summary = stats.get_summary()
        assert summary["clarity_improvements"] == 15


class TestEditResultExtended:
    """편집 결과 확장 테스트"""

    def test_calculate_quality_score_with_changes(self):
        """변경 있을 때 품질 점수"""
        result = EditResult(
            document_id="doc-001",
            stage=EditStage.PROOFREADING,
            original_text="원본",
            edited_text="수정본"
        )
        result.add_change(Change(
            type="spacing",
            original="원 본",
            modified="원본",
            reason="띄어쓰기",
            confidence=0.95
        ))
        score = result.calculate_quality_score()
        assert score > 95.0
        assert score <= 100.0

    def test_calculate_quality_score_no_changes(self):
        """변경 없을 때 품질 점수"""
        result = EditResult(
            document_id="doc-002",
            stage=EditStage.PROOFREADING,
            original_text="완벽한 원본",
            edited_text="완벽한 원본"
        )
        score = result.calculate_quality_score()
        assert score == 95.0

    def test_edit_result_to_dict(self):
        """편집 결과 딕셔너리 변환"""
        result = EditResult(
            document_id="doc-003",
            stage=EditStage.FACT_CHECKING,
            original_text="원본",
            edited_text="수정본",
            quality_score=92.5,
            processing_time=1.5
        )
        d = result.to_dict()
        assert d["document_id"] == "doc-003"
        assert d["stage"] == "fact_checking"
        assert d["quality_score"] == 92.5

    def test_batch_edit_result(self):
        """배치 편집 결과"""
        batch = BatchEditResult()

        for i in range(3):
            result = EditResult(
                document_id=f"doc-{i}",
                stage=EditStage.PROOFREADING,
                original_text="원본",
                edited_text="수정본",
                quality_score=90.0 + i,
                processing_time=1.0 + i
            )
            batch.add_result(result)

        assert len(batch.document_results) == 3
        assert batch.average_quality_score > 90.0
        assert batch.total_processing_time > 5.0

    def test_batch_edit_result_summary(self):
        """배치 결과 요약"""
        batch = BatchEditResult()
        result = EditResult(
            document_id="doc-001",
            stage=EditStage.PROOFREADING,
            original_text="원본",
            edited_text="수정본",
            quality_score=92.0
        )
        batch.add_result(result)
        batch.mark_completed()

        summary = batch.get_summary()
        assert summary["total_documents"] == 1
        assert summary["average_quality_score"] == 92.0
        assert summary["completed_at"] is not None

    def test_get_change_type_counts(self):
        """변경 유형별 개수"""
        result = EditResult(
            document_id="doc-004",
            stage=EditStage.PROOFREADING,
            original_text="원본",
            edited_text="수정본"
        )
        result.add_change(Change("spacing", "원 본", "원본", "띄어쓰기"))
        result.add_change(Change("spacing", "수 정", "수정", "띄어쓰기"))
        result.add_change(Change("spelling", "틀렸다", "틀렸다", "맞춤법"))

        counts = result._get_change_type_counts()
        assert counts["spacing"] == 2
        assert counts["spelling"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
