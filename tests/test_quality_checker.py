# Quality Checker Tests - Phase 1 RED
# 구현 시간: 2025-11-16 14:45 KST
# 품질 검사 모듈의 포괄적 테스트
# SPEC-PUB-TRANSLATE-001 요구사항:
# - 가독성 점수 계산 (≥85 목표)
# - 용어 일관성 검증 (≥95 목표)
# - 오류율 측정 (<0.5% 목표)
# - 자동 품질 검수

import pytest
from typing import Dict, List


@pytest.fixture
def high_quality_korean_text():
    """고품질 한국어 텍스트"""
    return """인공지능 개론

인공지능은 컴퓨터 과학의 한 분야로, 기계가 인간과 같이 학습하고 추론할 수 있도록 하는 기술입니다.
최근 몇 년 동안 인공지능은 의료, 금융, 자율주행 등 다양한 분야에서 중요한 역할을 하고 있습니다.

1.1 역사적 배경

인공지능 분야는 1950년대에 등장했습니다. 초기 연구자들은 인간 수준의 지능을 기계로 구현할 수 있다고
믿었습니다. 하지만 이 여정은 처음 예상보다 훨씬 복잡했습니다."""


@pytest.fixture
def poor_quality_korean_text():
    """저품질 한국어 텍스트"""
    return """AI(인공지능) 소개

AI 는 machine learning의 부분이다. AI는 중요하다. 최근에 AI가 많이 사용된다.
AI는 healthcare에서 사용된다. AI는 finance에서도 사용된다.

1.1 History

AI field는 1950s에서 나타났다. Early researchers들은 human-level intelligence를
machines로 구현할 수 있다고 생각했다."""


@pytest.fixture
def mixed_language_text():
    """혼합 언어 텍스트"""
    return """인공지능 Introduction

Machine Learning은 AI의 부분집합입니다.
Neural networks are important."""


@pytest.fixture
def inconsistent_terminology_text():
    """용어 불일치 텍스트"""
    return """인공지능에 대해 논의합니다.
AI 기술은 중요합니다.
인공지능(AI)의 발전이 빠릅니다.
머신러닝은 기계학습의 영어 표현입니다.
Machine Learning이 핵심입니다."""


# ==================== TEST CLASSES ====================

class TestReadabilityMetrics:
    """가독성 지표 테스트"""

    def test_calculate_readability_score(self, high_quality_korean_text):
        """
        Given: 한국어 텍스트
        When: calculate_readability_score() 호출
        Then: 0-100 범위의 점수가 반환되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        score = checker.calculate_readability_score(high_quality_korean_text)

        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_high_quality_text_high_score(self, high_quality_korean_text):
        """
        Given: 고품질 텍스트
        When: calculate_readability_score() 호출
        Then: 높은 점수(≥80)가 반환되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        score = checker.calculate_readability_score(high_quality_korean_text)

        assert score >= 80

    def test_poor_quality_text_low_score(self, poor_quality_korean_text):
        """
        Given: 저품질 텍스트
        When: calculate_readability_score() 호출
        Then: 낮은 점수(<70)가 반환되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        score = checker.calculate_readability_score(poor_quality_korean_text)

        assert score < 70

    def test_readability_considers_sentence_length(self):
        """
        Given: 긴 문장과 짧은 문장이 섞인 텍스트
        When: calculate_readability_score() 호출
        Then: 문장 길이가 가독성에 영향을 미쳐야 함
        """
        from src.quality import QualityChecker

        short_sentences = "문장은 짧다. 이것이 낫다. 읽기 쉽다."
        long_sentence = "문장이 매우 길면 읽기가 어려워질 수 있는데 이는 가독성을 떨어뜨린다는 점을 고려해야 한다."

        checker = QualityChecker()
        score_short = checker.calculate_readability_score(short_sentences)
        score_long = checker.calculate_readability_score(long_sentence)

        assert score_short > score_long

    def test_readability_considers_vocabulary_difficulty(self):
        """
        Given: 난이도가 다른 어휘
        When: calculate_readability_score() 호출
        Then: 어휘 난이도가 가독성에 영향을 미쳐야 함
        """
        from src.quality import QualityChecker

        simple_text = "좋은 책을 읽으면 배울 수 있다."
        complex_text = "고급 텍스트 분석 알고리즘의 성능 최적화는 다중 처리 인프라 구축을 필요로 한다."

        checker = QualityChecker()
        score_simple = checker.calculate_readability_score(simple_text)
        score_complex = checker.calculate_readability_score(complex_text)

        assert score_simple > score_complex

    def test_readability_considers_paragraph_structure(self):
        """
        Given: 구조화된 텍스트와 혼란스러운 텍스트
        When: calculate_readability_score() 호출
        Then: 단락 구조가 가독성에 영향을 미쳐야 함
        """
        from src.quality import QualityChecker

        structured = """첫 번째 주제.

두 번째 주제.

세 번째 주제."""

        unstructured = "첫 번째 주제. 두 번째 주제. 세 번째 주제."

        checker = QualityChecker()
        score_structured = checker.calculate_readability_score(structured)
        score_unstructured = checker.calculate_readability_score(unstructured)

        assert score_structured > score_unstructured


class TestTerminologyConsistency:
    """용어 일관성 테스트"""

    def test_calculate_terminology_consistency(self, high_quality_korean_text):
        """
        Given: 일관된 용어를 사용한 텍스트
        When: calculate_terminology_consistency() 호출
        Then: 높은 일관성 점수(≥90)가 반환되어야 함
        """
        from src.quality import TerminologyChecker

        checker = TerminologyChecker()
        score = checker.calculate_consistency(high_quality_korean_text)

        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_detect_terminology_inconsistencies(self, inconsistent_terminology_text):
        """
        Given: 용어가 불일치하는 텍스트
        When: detect_inconsistencies() 호출
        Then: 불일치하는 용어들이 식별되어야 함
        """
        from src.quality import TerminologyChecker

        checker = TerminologyChecker()
        inconsistencies = checker.detect_inconsistencies(inconsistent_terminology_text)

        assert isinstance(inconsistencies, list)
        assert len(inconsistencies) > 0

    def test_inconsistency_includes_alternatives(self, inconsistent_terminology_text):
        """
        Given: 용어 불일치 감지 결과
        When: 결과 분석
        Then: 각 불일치는 대안들을 포함해야 함
        """
        from src.quality import TerminologyChecker

        checker = TerminologyChecker()
        inconsistencies = checker.detect_inconsistencies(inconsistent_terminology_text)

        for inconsistency in inconsistencies:
            assert "term" in inconsistency or "original" in inconsistency
            assert "alternatives" in inconsistency or "variations" in inconsistency

    def test_consistency_against_style_guide(self):
        """
        Given: 스타일 가이드와 텍스트
        When: check_against_style_guide() 호출
        Then: 스타일 가이드 준수 여부가 확인되어야 함
        """
        from src.quality import TerminologyChecker

        style_guide = {
            "preferred_terms": {
                "AI": "인공지능",
                "ML": "기계 학습",
                "NN": "신경망"
            }
        }

        text = "AI와 ML은 중요하다. ML은 강력하다."

        checker = TerminologyChecker(style_guide=style_guide)
        violations = checker.check_against_guide(text)

        assert isinstance(violations, list)
        # Should flag use of abbreviations instead of full terms


class TestOrthoepyAndGrammar:
    """띄어쓰기, 맞춤법, 문법 테스트"""

    def test_detect_spacing_errors(self):
        """
        Given: 띄어쓰기 오류가 있는 텍스트
        When: detect_spacing_errors() 호출
        Then: 오류 위치가 식별되어야 함
        """
        from src.quality import GrammarChecker

        text_with_errors = "인공지능은중요하다.기계학습도중요하다."  # Missing spaces

        checker = GrammarChecker()
        errors = checker.detect_spacing_errors(text_with_errors)

        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_detect_spelling_errors(self):
        """
        Given: 맞춤법 오류가 있는 텍스트
        When: detect_spelling_errors() 호출
        Then: 오류가 식별되어야 함
        """
        from src.quality import GrammarChecker

        text_with_errors = "인공지능은 매우 중요한 기술이다. 그것은 미래를 바꿀 수있다."

        checker = GrammarChecker()
        errors = checker.detect_spelling_errors(text_with_errors)

        assert isinstance(errors, list)

    def test_detect_grammatical_errors(self):
        """
        Given: 문법 오류가 있는 텍스트
        When: detect_grammatical_errors() 호출
        Then: 오류가 식별되어야 함
        """
        from src.quality import GrammarChecker

        text_with_errors = "나는 책을 읽다. 그는 떠나였다."  # 문법 오류

        checker = GrammarChecker()
        errors = checker.detect_grammatical_errors(text_with_errors)

        assert isinstance(errors, list)


class TestMixedLanguageDetection:
    """혼합 언어 감지 테스트"""

    def test_detect_mixed_language_content(self, mixed_language_text):
        """
        Given: 한국어와 영어가 섞인 텍스트
        When: detect_mixed_languages() 호출
        Then: 섞인 언어가 식별되어야 함
        """
        from src.quality import LanguageAnalyzer

        analyzer = LanguageAnalyzer()
        languages = analyzer.detect_mixed_languages(mixed_language_text)

        assert isinstance(languages, dict)
        assert "Korean" in languages or "ko" in languages
        assert "English" in languages or "en" in languages

    def test_calculate_language_mixing_ratio(self, mixed_language_text):
        """
        Given: 혼합된 언어 텍스트
        When: calculate_mixing_ratio() 호출
        Then: 각 언어의 비율이 계산되어야 함
        """
        from src.quality import LanguageAnalyzer

        analyzer = LanguageAnalyzer()
        ratio = analyzer.calculate_mixing_ratio(mixed_language_text)

        assert isinstance(ratio, dict)
        assert "Korean" in ratio or "ko" in ratio
        total = sum(ratio.values())
        assert 95 <= total <= 105  # Should sum to ~100%

    def test_flag_excessive_english_usage(self):
        """
        Given: 과도한 영문이 포함된 텍스트
        When: analyze() 호출
        Then: 경고가 발생해야 함
        """
        from src.quality import LanguageAnalyzer

        english_heavy = "This is mostly English text. 가끔 한국어. More English. 더 한국어."

        analyzer = LanguageAnalyzer(max_english_ratio=0.3)
        warnings = analyzer.analyze(english_heavy)

        assert isinstance(warnings, list)
        if sum(1 for c in english_heavy if ord(c) > 127) < len(english_heavy) * 0.3:
            assert any("English" in w or "mixing" in w.lower() for w in warnings)


class TestFormatPreservation:
    """포맷 보존 검증 테스트"""

    def test_verify_markdown_preserved(self):
        """
        Given: 마크다운이 있는 원본과 번역본
        When: verify_markdown_preserved() 호출
        Then: 마크다운 마커가 보존되었는지 확인해야 함
        """
        from src.quality import FormatChecker

        original = "This is **bold** and *italic* text."
        translated = "이것은 **굵은** 그리고 *기울임* 텍스트입니다."

        checker = FormatChecker()
        is_preserved = checker.verify_markdown_preserved(original, translated)

        assert isinstance(is_preserved, bool)
        assert is_preserved is True

    def test_detect_lost_formatting(self):
        """
        Given: 포맷이 손실된 번역
        When: detect_lost_formatting() 호출
        Then: 손실된 포맷이 식별되어야 함
        """
        from src.quality import FormatChecker

        original = "This is **bold** and *italic* text."
        translated = "이것은 굵은 그리고 기울임 텍스트입니다."  # Formatting lost

        checker = FormatChecker()
        lost = checker.detect_lost_formatting(original, translated)

        assert isinstance(lost, list)
        assert len(lost) > 0

    def test_verify_code_blocks_untranslated(self):
        """
        Given: 코드 블록이 있는 텍스트
        When: verify_code_blocks_untranslated() 호출
        Then: 코드가 번역되지 않았는지 확인해야 함
        """
        from src.quality import FormatChecker

        text_with_code = """
        Text:
        ```python
        print("Hello")
        ```
        More text."""

        checker = FormatChecker()
        is_untranslated = checker.verify_code_blocks_untranslated(text_with_code)

        assert isinstance(is_untranslated, bool)
        assert is_untranslated is True


class TestComprehensiveQualityReport:
    """종합 품질 보고서 테스트"""

    def test_generate_quality_report(self, high_quality_korean_text):
        """
        Given: 한국어 텍스트
        When: generate_quality_report() 호출
        Then: 종합 품질 보고서가 생성되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        report = checker.generate_quality_report(high_quality_korean_text)

        assert isinstance(report, dict)
        assert "readability_score" in report
        assert "terminology_consistency" in report
        assert "issues" in report or "errors" in report
        assert "overall_quality" in report

    def test_quality_report_includes_recommendations(self, poor_quality_korean_text):
        """
        Given: 품질 문제가 있는 텍스트
        When: generate_quality_report() 호출
        Then: 개선 권고사항이 포함되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        report = checker.generate_quality_report(poor_quality_korean_text)

        assert "recommendations" in report or "suggestions" in report
        recommendations = report.get("recommendations") or report.get("suggestions")

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_quality_report_actionable(self, high_quality_korean_text):
        """
        Given: 생성된 품질 보고서
        When: 보고서 분석
        Then: 각 문제는 해결 방법을 포함해야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker()
        report = checker.generate_quality_report(high_quality_korean_text)

        for issue in report.get("issues", []):
            assert "description" in issue or "issue" in issue
            assert "suggestion" in issue or "fix" in issue or "recommendation" in issue

    def test_quality_report_includes_metadata(self):
        """
        Given: 텍스트와 메타데이터
        When: generate_quality_report() 호출
        Then: 텍스트 메타데이터가 포함되어야 함
        """
        from src.quality import QualityChecker

        text = "고품질 텍스트입니다." * 10

        checker = QualityChecker()
        report = checker.generate_quality_report(text)

        assert "text_statistics" in report or "statistics" in report
        stats = report.get("text_statistics") or report.get("statistics")

        assert "word_count" in stats
        assert "sentence_count" in stats
        assert "paragraph_count" in stats


class TestQualityThresholds:
    """품질 기준 테스트"""

    def test_pass_high_quality_threshold(self, high_quality_korean_text):
        """
        Given: 고품질 텍스트
        When: check_meets_quality_threshold() 호출
        Then: True를 반환해야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker(
            readability_threshold=85,
            consistency_threshold=95
        )

        result = checker.check_meets_quality_threshold(high_quality_korean_text)

        assert result is True

    def test_fail_poor_quality_threshold(self, poor_quality_korean_text):
        """
        Given: 저품질 텍스트
        When: check_meets_quality_threshold() 호출
        Then: False를 반환해야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker(
            readability_threshold=85,
            consistency_threshold=95
        )

        result = checker.check_meets_quality_threshold(poor_quality_korean_text)

        assert result is False

    def test_configurable_quality_thresholds(self):
        """
        Given: 다양한 품질 기준 설정
        When: QualityChecker 초기화
        Then: 기준이 적용되어야 함
        """
        from src.quality import QualityChecker

        checker = QualityChecker(
            readability_threshold=75,
            consistency_threshold=85,
            error_rate_threshold=1.0
        )

        assert checker.readability_threshold == 75
        assert checker.consistency_threshold == 85
        assert checker.error_rate_threshold == 1.0


class TestBatchQualityChecking:
    """배치 품질 검사 테스트"""

    def test_check_multiple_chunks_quality(self):
        """
        Given: 여러 청크
        When: check_batch_quality() 호출
        Then: 각 청크의 품질이 평가되어야 함
        """
        from src.quality import QualityChecker

        chunks = [
            "고품질 텍스트입니다." * 10,
            "저품질텍스트입니다." * 10,
            "또다른고품질텍스트입니다." * 10
        ]

        checker = QualityChecker()
        results = checker.check_batch_quality(chunks)

        assert len(results) == len(chunks)
        assert all("readability_score" in r for r in results)

    def test_aggregate_batch_quality_report(self):
        """
        Given: 여러 청크의 품질 검사 결과
        When: generate_aggregate_report() 호출
        Then: 종합 보고서가 생성되어야 함
        """
        from src.quality import QualityChecker

        chunks = ["고품질" * 50, "저품질" * 50]

        checker = QualityChecker()
        results = checker.check_batch_quality(chunks)
        aggregate = checker.generate_aggregate_report(results)

        assert "average_readability" in aggregate
        assert "average_consistency" in aggregate
        assert "overall_quality" in aggregate


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
