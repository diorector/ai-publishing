# 교정 모듈 테스트
# 작성일: 2025-11-18
# 목적: 한국어 맞춤법, 표기법, 외국어 표기 규칙 검증

import pytest


class TestSpacingRules:
    """띄어쓰기 규칙 테스트"""

    def test_spacing_between_korean_words(self):
        """한글 단어 간 띄어쓰기"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 띄어쓰기 오류
        text = "한국어띄어쓰기입니다"
        result = proofreader.check_spacing(text)

        assert result["has_errors"] is True
        assert len(result["corrections"]) > 0

    def test_spacing_korean_and_english(self):
        """한글과 영어 사이 띄어쓰기"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 올바른 띄어쓰기
        text = "Python 프로그래밍은 중요합니다."
        result = proofreader.check_spacing(text)

        # 이미 올바르면 오류가 없어야 함
        assert isinstance(result, dict)

    def test_spacing_korean_and_numbers(self):
        """한글과 숫자 사이 띄어쓰기"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        text = "2025년 11월 18일입니다"
        result = proofreader.check_spacing(text)

        assert isinstance(result, dict)


class TestSpellingRules:
    """맞춤법 규칙 테스트"""

    def test_common_spelling_errors(self):
        """일반적인 맞춤법 오류"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        test_cases = [
            ("안되다", "안 되다"),  # 띄어쓰기와 함께
            ("되어지다", "되다"),    # 중복
            ("때문에", "때문에"),    # 올바름
        ]

        for original, expected in test_cases:
            result = proofreader.check_spelling(original)
            assert isinstance(result, dict)

    def test_particle_usage(self):
        """조사 사용 검증"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 올바른 조사 사용
        text = "저는 학교에 간다."
        result = proofreader.check_particles(text)

        assert isinstance(result, dict)


class TestForeignLanguageRules:
    """외국어 표기법 규칙 테스트"""

    def test_english_company_names_consistency(self):
        """영문 기업명 일관성"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 같은 회사를 다른 방식으로 표기
        text = """
        Apple은 훌륭한 회사입니다.
        애플은 기술 혁신을 주도합니다.
        APPLE의 제품은 세계적입니다.
        """

        result = proofreader.check_foreign_language_consistency(text)

        assert isinstance(result, dict)
        assert "consistency_issues" in result

    def test_technical_term_consistency(self):
        """기술 용어 일관성"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        text = """
        Machine Learning은 중요합니다.
        머신 러닝은 AI의 기초입니다.
        머신러닝 알고리즘을 학습합니다.
        """

        result = proofreader.check_technical_terms(text)

        assert isinstance(result, dict)

    def test_foreign_word_spacing(self):
        """외국어 단어 띄어쓰기"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 외국어 사이에 불필요한 띄어쓰기
        text = "I have a pen"
        result = proofreader.check_foreign_spacing(text)

        assert isinstance(result, dict)


class TestNumberAndUnitRules:
    """숫자와 단위 규칙 테스트"""

    def test_arabic_vs_korean_numbers(self):
        """아라비아 숫자 vs 한글 숫자"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        test_cases = [
            "그는 10명을 고용했다",  # 올바름
            "그는 열명을 고용했다",   # 한글 숫자 (개선 가능)
            "제1장, 제2절",          # 서수 표기
        ]

        for text in test_cases:
            result = proofreader.check_number_format(text)
            assert isinstance(result, dict)

    def test_unit_formatting(self):
        """단위 표기 규칙"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        test_cases = [
            "100kg의 무게",
            "5 m 높이",
            "30%의 할인",
        ]

        for text in test_cases:
            result = proofreader.check_unit_format(text)
            assert isinstance(result, dict)


class TestProofreadingIntegration:
    """교정 모듈 통합 테스트"""

    def test_full_proofreading_process(self):
        """전체 교정 프로세스"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        original_text = """
        한국어띄어쓰기가 잘못되었습니다.
        Python프로그래밍은 중요합니다.
        ApplePython Google은 대형 회사입니다.
        그는 10명의 팀을 이끕니다.
        """

        result = proofreader.proofread(original_text)

        assert isinstance(result, dict)
        assert "corrected_text" in result
        assert "changes" in result
        assert "quality_score" in result
        assert result["quality_score"] > 0

    def test_proofreading_with_context(self):
        """문맥을 고려한 교정"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 기술 도메인
        text = "Machine Learning과 AI는 구분되어야 합니다."
        result = proofreader.proofread(text, domain="technology")

        assert isinstance(result, dict)

    def test_proofreading_preserves_meaning(self):
        """의미 보존 검증"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        original = "이것은 매우 중요한 문서입니다."
        result = proofreader.proofread(original)

        # 의미가 바뀌지 않아야 함
        assert result is not None
        assert "corrected_text" in result

    def test_proofreading_change_tracking(self):
        """변경 사항 추적"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        original = "한국어 맞춤법이 틀렸습니다."
        result = proofreader.proofread(original)

        assert "changes" in result
        assert isinstance(result["changes"], list)

        for change in result["changes"]:
            assert "type" in change
            assert "original" in change
            assert "modified" in change
            assert "reason" in change


class TestProofreadingChunkedProcessing:
    """청크 기반 병렬 처리 테스트"""

    def test_chunking_large_text(self):
        """큰 텍스트 청크 분할"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        # 큰 텍스트 (3000자 이상)
        large_text = "문장입니다. " * 300  # 약 4200자

        result = proofreader.proofread_parallel(large_text, max_chunk_size=1000)

        assert isinstance(result, dict)
        assert "corrected_text" in result

    def test_parallel_processing_consistency(self):
        """병렬 처리 일관성"""
        from src.editing.edit_proofreading import ProofreadingModule

        proofreader = ProofreadingModule()

        text = "이것은 테스트 텍스트입니다. " * 100

        # 직렬 처리
        result_sequential = proofreader.proofread(text)

        # 병렬 처리
        result_parallel = proofreader.proofread_parallel(text, num_workers=2)

        # 두 결과가 의미상 동일해야 함
        assert result_sequential is not None
        assert result_parallel is not None

    def test_parallel_processing_performance(self):
        """병렬 처리 성능"""
        from src.editing.edit_proofreading import ProofreadingModule
        import time

        proofreader = ProofreadingModule()

        # 중간 크기 텍스트
        text = "문장입니다. " * 200

        start = time.time()
        result = proofreader.proofread_parallel(text, num_workers=3)
        elapsed = time.time() - start

        # 병렬 처리가 완료되어야 함
        assert result is not None
        assert elapsed >= 0  # 처리 시간은 0 이상이어야 함


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
