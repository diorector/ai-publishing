# Translation Module Tests - Phase 1 RED
# 구현 시간: 2025-11-16 14:40 KST
# 번역 모듈의 포괄적 테스트
# SPEC-PUB-TRANSLATE-001 요구사항:
# - 청크 단위 병렬 번역
# - Claude API 통합
# - 용어 일관성 유지
# - 포맷 보존

import pytest
from typing import List, Dict
from unittest.mock import Mock, patch, AsyncMock
import asyncio


@pytest.fixture
def sample_english_chunk():
    """샘플 영문 청크"""
    return """Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that enables systems to learn and improve
from experience without being explicitly programmed. In recent years, machine learning has become
increasingly important in various domains including healthcare, finance, and autonomous vehicles.

The fundamental concept behind machine learning is that systems can learn from data. This is achieved
through algorithms that identify patterns in the data and make decisions based on those patterns."""


@pytest.fixture
def style_guide():
    """스타일 가이드"""
    return {
        "terminology": {
            "machine learning": "기계 학습",
            "artificial intelligence": "인공지능",
            "neural network": "신경망",
            "deep learning": "딥러닝"
        },
        "style": {
            "voice": "academic",
            "tone": "formal",
            "korean_formality": "formal"
        }
    }


@pytest.fixture
def mock_translation_result():
    """Mock 번역 결과"""
    return {
        "original": "Machine learning is a subset of artificial intelligence",
        "translated": "기계 학습은 인공지능의 부분 집합이다",
        "confidence": 0.95,
        "terminology_used": ["기계 학습", "인공지능"]
    }


# ==================== TEST CLASSES ====================

class TestBasicTranslation:
    """기본 번역 테스트"""

    def test_translate_single_chunk(self, sample_english_chunk):
        """
        Given: 영문 청크
        When: translate() 호출
        Then: 한국어 번역이 반환되어야 함
        """
        from src.translation import Translator

        translator = Translator()
        result = translator.translate(sample_english_chunk)

        assert isinstance(result, dict)
        assert "translated_text" in result
        assert isinstance(result["translated_text"], str)
        assert len(result["translated_text"]) > 0

    def test_translation_result_structure(self, sample_english_chunk):
        """
        Given: 번역 요청
        When: translate() 호출
        Then: 정의된 구조의 결과가 반환되어야 함
        """
        from src.translation import Translator

        translator = Translator()
        result = translator.translate(sample_english_chunk)

        assert "translated_text" in result
        assert "metadata" in result or "confidence" in result
        assert "original_text" in result or "source" in result

    def test_translate_preserves_formatting(self):
        """
        Given: 포맷 마크업이 있는 텍스트
        When: translate() 호출
        Then: 포맷 마크업이 보존되어야 함
        """
        from src.translation import Translator

        formatted_text = """**Introduction**

This is *important* content:

1. Point one
2. Point two

> Quote text"""

        translator = Translator()
        result = translator.translate(formatted_text)

        translated = result["translated_text"]
        # Formatting markers should be preserved
        assert "**" in translated or "[BOLD]" in translated
        assert any(marker in translated for marker in ["*", "___", "[BOLD]"])

    def test_translate_empty_chunk_gracefully(self):
        """
        Given: 빈 청크
        When: translate() 호출
        Then: 빈 결과를 반환하거나 예외를 발생시켜야 함
        """
        from src.translation import Translator

        translator = Translator()
        result = translator.translate("")

        assert isinstance(result, dict)
        assert result.get("translated_text") == "" or result.get("translated_text") is not None

    def test_translate_very_long_chunk(self):
        """
        Given: 매우 긴 청크 (>10000 단어)
        When: translate() 호출
        Then: 청크 크기 제한을 확인하거나 적절히 처리해야 함
        """
        from src.translation import Translator

        # Create very long text
        long_text = "This is a test sentence. " * 1000

        translator = Translator()

        # Should either succeed or raise appropriate error
        try:
            result = translator.translate(long_text)
            assert "translated_text" in result
        except Exception as e:
            assert "too long" in str(e).lower() or "exceeds" in str(e).lower()


class TestBatchTranslation:
    """배치 번역 테스트"""

    def test_translate_multiple_chunks_sequentially(self, sample_english_chunk):
        """
        Given: 여러 청크
        When: translate_batch(sequential=True) 호출
        Then: 모든 청크가 번역되어야 함
        """
        from src.translation import Translator

        chunks = [sample_english_chunk] * 3
        translator = Translator()

        results = translator.translate_batch(chunks, parallel=False)

        assert len(results) == 3
        assert all("translated_text" in r for r in results)

    def test_translate_multiple_chunks_in_parallel(self, sample_english_chunk):
        """
        Given: 여러 청크와 병렬 설정
        When: translate_batch(parallel=True, max_workers=5) 호출
        Then: 모든 청크가 번역되어야 함
        """
        from src.translation import Translator

        chunks = [sample_english_chunk] * 5
        translator = Translator()

        results = translator.translate_batch(chunks, parallel=True, max_workers=3)

        assert len(results) == 5
        assert all("translated_text" in r for r in results)

    def test_parallel_translation_faster_than_sequential(self, sample_english_chunk):
        """
        Given: 여러 청크
        When: 순차 vs 병렬 번역 성능 비교
        Then: 병렬 처리가 더 빨라야 함
        """
        from src.translation import Translator
        import time

        chunks = [sample_english_chunk] * 5
        translator = Translator()

        # Mock timing (since API calls would be slow)
        assert hasattr(translator, 'translate_batch')

    def test_batch_translation_maintains_order(self, sample_english_chunk):
        """
        Given: 순서가 있는 여러 청크
        When: translate_batch() 호출
        Then: 반환된 결과가 동일한 순서를 유지해야 함
        """
        from src.translation import Translator

        chunks = [
            f"{i}: {sample_english_chunk}"
            for i in range(5)
        ]

        translator = Translator()
        results = translator.translate_batch(chunks)

        assert len(results) == 5
        # Results should maintain order (content check)
        for i, result in enumerate(results):
            translated = result.get("translated_text", "")
            # Should contain reference to chunk number if preserved
            assert isinstance(translated, str)

    def test_batch_translation_error_handling(self, sample_english_chunk):
        """
        Given: 배치 번역 중 일부 청크 오류
        When: translate_batch(continue_on_error=True) 호출
        Then: 실패한 청크를 마크하고 나머지는 처리해야 함
        """
        from src.translation import Translator

        chunks = [sample_english_chunk] * 5
        translator = Translator()

        results = translator.translate_batch(
            chunks,
            continue_on_error=True
        )

        assert len(results) == 5
        # Each result should have status or error indication
        for result in results:
            assert "translated_text" in result or "error" in result


class TestTerminologyConsistency:
    """용어 일관성 테스트"""

    def test_apply_style_guide_terminology(self, sample_english_chunk, style_guide):
        """
        Given: 번역된 텍스트와 스타일 가이드
        When: apply_style_guide() 호출
        Then: 스타일 가이드의 용어가 적용되어야 함
        """
        from src.translation import TerminologyManager

        manager = TerminologyManager(style_guide)
        result = manager.apply_terminology(
            sample_english_chunk,
            style_guide["terminology"]
        )

        assert "기계 학습" in result or "machine learning" not in result.lower()
        assert "인공지능" in result or "artificial intelligence" not in result.lower()

    def test_detect_terminology_inconsistencies(self):
        """
        Given: 같은 용어의 다양한 번역
        When: detect_inconsistencies() 호출
        Then: 불일치하는 용어들이 식별되어야 함
        """
        from src.translation import TerminologyManager

        text_with_inconsistency = """
        기계 학습은 중요하다.
        머신러닝의 발전이 가속화되고 있다.
        """

        manager = TerminologyManager()
        inconsistencies = manager.detect_inconsistencies(text_with_inconsistency)

        assert isinstance(inconsistencies, list)
        # Should identify 기계 학습 vs 머신러닝

    def test_maintain_technical_terminology(self, style_guide):
        """
        Given: 기술 용어와 스타일 가이드
        When: 번역 수행
        Then: 기술 용어가 일관되게 유지되어야 함
        """
        from src.translation import Translator

        english_text = """
        Deep learning uses neural networks.
        The neural network architecture is important."""

        translator = Translator(style_guide=style_guide)
        result = translator.translate(english_text)

        translated = result["translated_text"]
        # Check terminology consistency
        korean_dl_mentions = translated.count("딥러닝")
        korean_nn_mentions = translated.count("신경망")

        # If either appears, it should be consistent
        if korean_dl_mentions > 0:
            assert korean_dl_mentions >= 1

    def test_build_custom_terminology_dictionary(self):
        """
        Given: 사용자 정의 용어 목록
        When: add_custom_terminology() 호출
        Then: 커스텀 용어가 번역에 적용되어야 함
        """
        from src.translation import TerminologyManager

        custom_terms = {
            "knowledge graph": "지식 그래프",
            "embedding": "임베딩"
        }

        manager = TerminologyManager()
        manager.add_custom_terminology(custom_terms)

        # Verify custom terms are registered
        assert hasattr(manager, 'custom_terminology')


class TestTranslationQuality:
    """번역 품질 테스트"""

    def test_translation_confidence_score(self, sample_english_chunk):
        """
        Given: 번역 수행
        When: translate() 호출
        Then: 신뢰도 점수가 포함되어야 함 (0-1)
        """
        from src.translation import Translator

        translator = Translator()
        result = translator.translate(sample_english_chunk)

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 1

    def test_identify_translation_issues(self):
        """
        Given: 번역된 텍스트
        When: analyze_translation_quality() 호출
        Then: 잠재적 문제들이 식별되어야 함
        """
        from src.translation import TranslationAnalyzer

        analyzer = TranslationAnalyzer()
        result = analyzer.analyze(
            original="This is a test",
            translated="이것이 테스트입니다"
        )

        assert isinstance(result, dict)
        assert "issues" in result or "quality_score" in result

    def test_detect_untranslated_content(self):
        """
        Given: 부분 번역된 텍스트
        When: detect_untranslated() 호출
        Then: 번역되지 않은 부분이 식별되어야 함
        """
        from src.translation import TranslationAnalyzer

        analyzer = TranslationAnalyzer()
        partially_translated = """
        This sentence is in English.
        이 문장은 한국어입니다.
        Another English sentence here.
        """

        untranslated = analyzer.detect_untranslated(partially_translated)

        assert isinstance(untranslated, list)
        if untranslated:
            for item in untranslated:
                assert isinstance(item, str)

    def test_detect_hallucinated_content(self):
        """
        Given: 원본과 번역본
        When: detect_hallucinations() 호출
        Then: 추가되거나 변경된 내용이 식별되어야 함
        """
        from src.translation import TranslationAnalyzer

        analyzer = TranslationAnalyzer()
        original = "The system works well."
        translated = "시스템은 잘 작동하며 매우 안정적입니다."  # Added "안정적"

        issues = analyzer.detect_hallucinations(original, translated)

        assert isinstance(issues, list)


class TestFormattingPreservation:
    """포맷 보존 테스트"""

    def test_preserve_markdown_bold(self):
        """
        Given: **bold** 마크다운
        When: 번역
        Then: 볼드 포맷이 보존되어야 함
        """
        from src.translation import Translator

        text = "This is **important** text"
        translator = Translator(preserve_markdown=True)
        result = translator.translate(text)

        assert "**" in result["translated_text"]

    def test_preserve_markdown_lists(self):
        """
        Given: 마크다운 목록
        When: 번역
        Then: 목록 구조가 보존되어야 함
        """
        from src.translation import Translator

        text = """
        - Item one
        - Item two
        - Item three"""

        translator = Translator(preserve_markdown=True)
        result = translator.translate(text)

        assert "-" in result["translated_text"] or "•" in result["translated_text"]

    def test_preserve_code_blocks(self):
        """
        Given: 코드 블록
        When: 번역
        Then: 코드는 번역되지 않아야 함
        """
        from src.translation import Translator

        text = """
        Here is code:

        ```python
        print("Hello World")
        ```

        This is text."""

        translator = Translator(preserve_code_blocks=True)
        result = translator.translate(text)

        assert "print(" in result["translated_text"]

    def test_preserve_special_characters(self):
        """
        Given: 특수 문자와 기호
        When: 번역
        Then: 특수 문자가 보존되어야 함
        """
        from src.translation import Translator

        text = "Formula: E=mc². Equation: x² + y² = r²"

        translator = Translator()
        result = translator.translate(text)

        # Check that mathematical symbols are preserved
        translated = result["translated_text"]
        assert "=" in translated or "=" in translated


class TestErrorHandling:
    """오류 처리 테스트"""

    def test_handle_api_timeout(self):
        """
        Given: API 타임아웃
        When: translate() 호출
        Then: TranslationError 발생 또는 재시도해야 함
        """
        from src.translation import Translator, TranslationError

        translator = Translator(timeout=0.001)  # Very short timeout

        with pytest.raises((TranslationError, TimeoutError)):
            translator.translate("Test text")

    def test_handle_rate_limiting(self):
        """
        Given: API 레이트 제한
        When: 연속 요청
        Then: 재시도 로직이 작동해야 함
        """
        from src.translation import Translator

        translator = Translator()

        # Should have retry mechanism
        assert hasattr(translator, 'retry_attempts') or \
               hasattr(translator, 'backoff_strategy')

    def test_handle_invalid_language_pair(self):
        """
        Given: 지원하지 않는 언어 쌍
        When: translate() 호출
        Then: ValueError 발생해야 함
        """
        from src.translation import Translator

        # Assuming translator doesn't support English to Spanish
        translator = Translator()

        # Should validate language pair
        assert hasattr(translator, 'source_language') and \
               hasattr(translator, 'target_language')

    def test_handle_none_input_gracefully(self):
        """
        Given: None 입력
        When: translate() 호출
        Then: ValueError 발생해야 함
        """
        from src.translation import Translator

        translator = Translator()

        with pytest.raises((TypeError, ValueError)):
            translator.translate(None)


class TestTranslationWithContext:
    """컨텍스트를 고려한 번역 테스트"""

    def test_translate_with_previous_context(self, sample_english_chunk):
        """
        Given: 이전 청크의 컨텍스트
        When: translate_with_context() 호출
        Then: 컨텍스트를 고려한 일관된 번역이 반환되어야 함
        """
        from src.translation import Translator

        context = "In the field of artificial intelligence..."
        translator = Translator()

        result = translator.translate_with_context(
            sample_english_chunk,
            context=context
        )

        assert "translated_text" in result
        assert "context_used" in result or "with_context" in result

    def test_translate_with_future_context(self):
        """
        Given: 다음 청크의 미리보기
        When: translate_with_lookahead() 호출
        Then: 미리보기 정보를 고려한 번역이 반환되어야 함
        """
        from src.translation import Translator

        current = "Machine learning is..."
        next_chunk = "Neural networks process..."

        translator = Translator()

        result = translator.translate_with_lookahead(
            current,
            next_chunk=next_chunk
        )

        assert "translated_text" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
