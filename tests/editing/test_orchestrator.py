# 오케스트레이터 모듈 테스트
# 작성일: 2025-11-18
# 목적: 전체 편집 파이프라인 오케스트레이션 검증

import pytest
import tempfile
import os
from pathlib import Path


class TestEditOrchestrator:
    """편집 오케스트레이터 테스트"""

    def test_orchestrator_initialization(self):
        """오케스트레이터 초기화"""
        from src.editing.edit_orchestrator import EditOrchestrator

        orchestrator = EditOrchestrator()

        assert orchestrator is not None
        assert hasattr(orchestrator, 'proofread_module')
        assert hasattr(orchestrator, 'fact_check_module')
        assert hasattr(orchestrator, 'copywrite_module')

    def test_document_loading(self):
        """문서 로딩"""
        from src.editing.edit_orchestrator import EditOrchestrator

        orchestrator = EditOrchestrator()

        # 임시 마크다운 파일 생성
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# 테스트 문서\n\n이것은 테스트입니다.")
            temp_file = f.name

        try:
            doc = orchestrator.load_document(temp_file, "startup", "general")

            assert doc is not None
            assert doc.title == "테스트 문서"
            assert len(doc.content) > 0
        finally:
            os.unlink(temp_file)

    def test_document_analysis(self):
        """문서 분석"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="이것은 테스트 문서입니다.",
            domain="general",
            target_audience="general"
        )

        analysis = orchestrator.analyze_document(doc)

        assert isinstance(analysis, dict)
        assert "statistics" in analysis
        assert "issues" in analysis

    def test_single_stage_execution(self):
        """단일 단계 실행 (교정만)"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="한국어띄어쓰기가 틀렸습니다.",
            domain="general",
            target_audience="general"
        )

        result = orchestrator.proofread_document(doc)

        assert isinstance(result, dict)
        assert "corrected_text" in result

    def test_two_stage_execution(self):
        """2단계 실행 (교정 + 교열)"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="한국어띄어쓰기가 틀렸습니다. 2020년 통계를 확인하세요.",
            domain="general",
            target_audience="general"
        )

        result = orchestrator.proofread_and_factcheck_document(doc)

        assert isinstance(result, dict)
        assert "text" in result

    def test_full_pipeline_execution(self):
        """전체 파이프라인 실행 (교정 + 교열 + 윤문)"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="""
            한국어띄어쓰기가 틀렸습니다.
            우리가 분석한 결과에 따르면, 이것은 매우 중요합니다.
            2020년 통계를 확인하세요.
            """,
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert isinstance(result, dict)
        assert "final_text" in result
        assert "quality_score" in result

    def test_pipeline_with_checkpoint(self):
        """체크포인트를 통한 진행 추적"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="테스트 콘텐츠입니다.",
            domain="general",
            target_audience="general"
        )

        # 진행 상황 추적 활성화
        result = orchestrator.edit_comprehensive(doc, track_progress=True)

        assert isinstance(result, dict)

    def test_error_recovery(self):
        """오류 복구"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="테스트 콘텐츠입니다.",
            domain="general",
            target_audience="general"
        )

        # 정상 동작 확인
        result = orchestrator.edit_comprehensive(doc)
        assert result is not None

    def test_batch_document_processing(self):
        """배치 문서 처리"""
        from src.editing.edit_orchestrator import EditOrchestrator

        orchestrator = EditOrchestrator()

        # 임시 파일 생성
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(f"# 문서 {i}\n\n이것은 테스트입니다. " * 10)
                temp_files.append(f.name)

        try:
            results = orchestrator.batch_process_documents(
                temp_files,
                domain="startup",
                target_audience="general"
            )

            assert isinstance(results, list)
            assert len(results) == 3
        finally:
            for f in temp_files:
                os.unlink(f)

    def test_progress_tracking(self):
        """진행률 추적"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="테스트 콘텐츠입니다.",
            domain="general",
            target_audience="general"
        )

        progress_log = []

        def progress_callback(stage, progress):
            progress_log.append({'stage': stage, 'progress': progress})

        result = orchestrator.edit_comprehensive(doc, progress_callback=progress_callback)

        assert result is not None
        assert len(progress_log) > 0

    def test_quality_scoring(self):
        """품질 점수 계산"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="이것은 완벽한 한국어 문서입니다.",
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert "quality_score" in result
        assert isinstance(result["quality_score"], (int, float))
        assert 0 <= result["quality_score"] <= 100

    def test_change_tracking(self):
        """변경사항 추적"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="한국어 맞춤법이 틀렸습니다.",
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert "changes_summary" in result
        assert isinstance(result["changes_summary"], dict)

    def test_parallel_processing_stages(self):
        """단계별 병렬 처리"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        # 큰 문서
        large_content = "테스트 문장입니다. " * 500

        doc = Document(
            id="test-001",
            title="테스트",
            content=large_content,
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc, enable_parallel=True)

        assert isinstance(result, dict)

    def test_custom_stage_selection(self):
        """커스텀 단계 선택"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="테스트 콘텐츠입니다.",
            domain="general",
            target_audience="general"
        )

        # 교정과 윤문만 실행
        result = orchestrator.edit_custom_stages(doc, stages=["proofreading", "copywriting"])

        assert isinstance(result, dict)

    def test_document_statistics(self):
        """문서 통계"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="테스트",
            content="테스트 콘텐츠입니다. " * 50,
            domain="general",
            target_audience="general"
        )

        stats = orchestrator.get_document_statistics(doc)

        assert isinstance(stats, dict)
        assert "word_count" in stats
        assert "character_count" in stats


class TestEditOrchestratorIntegration:
    """통합 테스트"""

    def test_end_to_end_pipeline(self):
        """E2E 파이프라인"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        # 복합적인 문서
        doc = Document(
            id="test-001",
            title="포괄적 편집 도구",
            content="""
            # 소개
            우리가 개발한 편집 도구는 한국어 문서를 자동으로 교정하고 개선합니다.
            이 도구는 교정, 교열, 윤문의 3단계로 구성됩니다.

            ## 교정 단계
            교정 단계에서는 맞춤법과 표기법을 검사합니다.
            이 단계는 매우 중요합니다.

            ## 교열 단계
            교열 단계에서는 팩트를 검증합니다.
            2020년 통계를 확인하고 최신화합니다.

            ## 윤문 단계
            윤문 단계에서는 문체를 개선합니다.
            우리가 분석한 결과에 따르면, 이것은 매우 효과적입니다.
            """,
            domain="startup",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert result is not None
        assert "final_text" in result
        assert "quality_score" in result
        assert result["quality_score"] > 0

    def test_real_world_document(self):
        """실제 문서 처리"""
        from src.editing.edit_orchestrator import EditOrchestrator

        orchestrator = EditOrchestrator()

        # 임시 파일로 실제 상황 시뮬레이션
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# AI 출판 시스템

## 개요
이 시스템은 AI를 활용하여 출판 프로세스를 자동화합니다.

## 기능
- 자동 번역
- 자동 교정
- 품질 관리

## 성과
우리팀은 2024년에 이 시스템을 개발했습니다.
이시스템은 여러 문제가 있었지만 지금은 잘 작동합니다.
            """)
            temp_file = f.name

        try:
            doc = orchestrator.load_document(temp_file, "startup", "developer")
            result = orchestrator.edit_comprehensive(doc)

            assert result is not None
            assert isinstance(result, dict)
        finally:
            os.unlink(temp_file)


class TestEdgeCases:
    """엣지 케이스"""

    def test_very_long_document(self):
        """매우 긴 문서"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        # 10,000자 이상의 문서
        large_content = "테스트 문장입니다. " * 1000

        doc = Document(
            id="test-001",
            title="큰 문서",
            content=large_content,
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert isinstance(result, dict)

    def test_document_with_special_formatting(self):
        """특수 형식의 문서"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="특수 형식",
            content="""
# 제목

> 인용문

`코드 블록`

- 리스트
- 아이템

**굵은 글씨**
            """,
            domain="general",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert isinstance(result, dict)

    def test_mixed_language_document(self):
        """혼합 언어 문서"""
        from src.editing.edit_orchestrator import EditOrchestrator
        from src.editing.models.document import Document

        orchestrator = EditOrchestrator()

        doc = Document(
            id="test-001",
            title="혼합 언어",
            content="""
            Python과 JavaScript는 인기있는 프로그래밍 언어입니다.
            Machine Learning 기술이 중요합니다.
            한국어와 영어가 섞여있습니다.
            """,
            domain="technology",
            target_audience="general"
        )

        result = orchestrator.edit_comprehensive(doc)

        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
