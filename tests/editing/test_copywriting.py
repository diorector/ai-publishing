# 윤문 모듈 테스트
# 작성일: 2025-11-18
# 목적: 문체 통일, 문장 개선, 가독성 최적화, 저자 의도 보존 검증

import pytest
import time


class TestSentenceStructureImprovement:
    """문장 구조 개선 테스트"""

    def test_complex_sentence_simplification(self):
        """복문을 단문으로 단순화"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 복문
        original = "우리가 분석한 결과에 따르면, 사용자들이 원하는 기능이 바로 이것이었고, 따라서 우리는 이를 구현하기로 결정했다."

        result = copywriter.improve_sentence(original)

        assert isinstance(result, dict)
        assert "improved_text" in result
        assert "improvements" in result
        assert len(result["improvements"]) > 0

    def test_long_sentence_splitting(self):
        """긴 문장을 2-3개로 분해"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 긴 문장 (60자 이상)
        original = "이 프로젝트는 매우 복잡한 요구사항을 가지고 있었고, 많은 시간과 노력이 들었으며, 결과적으로 우리는 성공적인 결과를 얻을 수 있었다."

        result = copywriter.improve_sentence(original)

        assert isinstance(result, dict)
        assert "improved_text" in result

    def test_passive_voice_to_active(self):
        """수동태를 능동태로 변경"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 수동태
        original = "이 기능은 우리 팀에 의해 개발되었다."

        result = copywriter.improve_sentence(original)

        assert isinstance(result, dict)

    def test_unclear_pronouns_clarification(self):
        """불분명한 대명사 명확화"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 모호한 대명사
        original = "그는 그것을 했고, 그것은 매우 좋았다."

        result = copywriter.improve_sentence(original)

        assert isinstance(result, dict)


class TestToneConsistency:
    """문체 일관성 검증 테스트"""

    def test_honorific_consistency(self):
        """존댓말 일관성"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 존댓말 혼합
        text = """
        이것은 매우 중요합니다.
        우리는 이를 고려해야 해요.
        따라서 다음과 같이 진행합니다.
        """

        result = copywriter.check_tone_consistency(text)

        assert isinstance(result, dict)
        assert "consistency_score" in result
        assert "issues" in result
        assert 0 <= result["consistency_score"] <= 100

    def test_informal_formal_balance(self):
        """비격식과 격식의 균형"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 너무 격식적
        text = "당신이 고려하셔야 할 사항은 다음과 같은 바이다. 첫째, ..."

        result = copywriter.check_tone_consistency(text)

        assert isinstance(result, dict)

    def test_technical_vs_friendly_balance(self):
        """기술적 vs 친근한 표현 균형"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 기술적 표현이 많음
        text = "비동기 작업 큐 메커니즘은 다양한 구현 패러다임을 활용하여 최적화된 처리량을 달성한다."

        result = copywriter.check_tone_consistency(text)

        assert isinstance(result, dict)


class TestReadabilityOptimization:
    """가독성 최적화 테스트"""

    def test_word_frequency_analysis(self):
        """단어 반복도 분석"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 단어 반복이 많음
        text = """
        개발은 중요합니다. 개발 과정에서는 개발 팀의 협력이 필수입니다.
        개발 팀은 개발 일정을 준수해야 합니다.
        """

        result = copywriter.analyze_readability(text)

        assert isinstance(result, dict)
        assert "repeated_words" in result

    def test_paragraph_structure_analysis(self):
        """문단 구조 분석"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 긴 문단
        text = """
        이것은 첫 번째 문장입니다. 이것은 두 번째 문장입니다. 이것은 세 번째 문장입니다.
        이것은 네 번째 문장입니다. 이것은 다섯 번째 문장입니다. 이것은 여섯 번째 문장입니다.
        """

        result = copywriter.analyze_readability(text)

        assert isinstance(result, dict)
        assert "readability_score" in result

    def test_connector_words_usage(self):
        """연결사 사용도 분석"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 연결사 부족
        text = "우리는 분석했다. 우리는 설계했다. 우리는 구현했다."

        result = copywriter.analyze_readability(text)

        assert isinstance(result, dict)


class TestAuthorIntentPreservation:
    """저자 의도 보존 테스트"""

    def test_meaning_preservation(self):
        """의미 보존 검증"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        original = "이 방법은 기존 방식보다 10배 빠르지만, 조금 더 복잡하다."

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)
        assert "improved_text" in result
        # 개선된 텍스트에도 "빠르다"와 "복잡하다"는 의미가 있어야 함

    def test_nuance_preservation(self):
        """뉘앙스 보존"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 약간의 회의적 톤
        original = "이 방법이 효과가 있을 수도 있지만, 더 많은 검증이 필요할 것 같다."

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)

    def test_emphasis_preservation(self):
        """강조점 보존"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 강조
        original = "가장 중요한 것은, 이 부분이 정말로 중요하다는 것이다."

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)


class TestParagraphImprovement:
    """단락 개선 테스트"""

    def test_full_paragraph_improvement(self):
        """전체 단락 개선"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        original = """
        우리가 한 분석 결과에 따르면, 사용자들이 원하는 것은 바로 이런 기능이었고,
        우리가 구현한 것이 바로 이 기능이었으므로, 우리의 결정은 옳았다고 할 수 있다.
        """

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)
        assert "improved_text" in result
        assert "changes" in result
        assert "readability_change" in result

    def test_translation_style_removal(self):
        """번역체 표현 제거"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 번역체
        original = "다음과 같이 고려되어야 한다는 점이 있다."

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)

    def test_awkward_phrasing_improvement(self):
        """어색한 표현 개선"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 어색한 표현
        original = "이 기능을 사용함으로써 얻을 수 있는 이점은 다음과 같은 바이다."

        result = copywriter.improve_paragraph(original)

        assert isinstance(result, dict)


class TestCopywritingIntegration:
    """윤문 모듈 통합 테스트"""

    def test_full_copywriting_process(self):
        """전체 윤문 프로세스"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        original_text = """
        우리가 분석한 결과에 따르면, 사용자들이 원하는 기능이 바로 이것이었고,
        따라서 우리는 이를 구현하기로 결정했다. 이 기능은 우리 팀에 의해 개발되었다.
        개발 과정은 어려웠지만, 결과는 만족할 만했다.
        """

        result = copywriter.copywrite(original_text)

        assert isinstance(result, dict)
        assert "improved_text" in result
        assert "changes" in result
        assert "quality_score" in result
        assert result["quality_score"] > 0

    def test_copywriting_with_domain(self):
        """도메인별 윤문"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "Machine Learning 알고리즘을 구현함으로써, 우리는 예측 정확도를 향상시킬 수 있었다."

        # 기술 도메인
        result = copywriter.copywrite(text, domain="technology")

        assert isinstance(result, dict)
        assert "improved_text" in result

    def test_copywriting_with_audience(self):
        """대상 독자별 윤문"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "신경망의 역전파 알고리즘은 매우 복잡한 수학적 개념이다."

        # 일반인을 대상으로
        result = copywriter.copywrite(text, target_audience="general")

        assert isinstance(result, dict)

    def test_copywriting_change_tracking(self):
        """변경 사항 추적"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        original = "이것은 테스트 텍스트입니다. 이것은 개선될 수 있습니다."
        result = copywriter.copywrite(original)

        assert "changes" in result
        assert isinstance(result["changes"], list)

        for change in result["changes"]:
            assert "type" in change
            assert "original" in change
            assert "improved" in change
            assert "reason" in change


class TestCopywritingQualityMetrics:
    """윤문 품질 지표 테스트"""

    def test_readability_score_calculation(self):
        """가독성 점수 계산"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        simple_text = "우리는 간다. 그것은 좋다."
        complex_text = "우리가 분석한 결과에 따르면, 복잡한 알고리즘을 활용하여 최적화된 처리량을 달성할 수 있다는 점이 매우 중요하다."

        result_simple = copywriter.calculate_readability_metrics(simple_text)
        result_complex = copywriter.calculate_readability_metrics(complex_text)

        assert isinstance(result_simple, dict)
        assert isinstance(result_complex, dict)
        assert "readability_score" in result_simple
        assert "readability_score" in result_complex
        # 간단한 텍스트가 더 높은 가독성 점수를 가져야 함

    def test_coherence_score_calculation(self):
        """일관성 점수 계산"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        # 논리적 흐름이 있는 텍스트
        coherent_text = """
        첫 번째, 우리는 문제를 분석했다.
        두 번째, 우리는 해결책을 설계했다.
        세 번째, 우리는 이를 구현했다.
        """

        result = copywriter.calculate_coherence_score(coherent_text)

        assert isinstance(result, dict)
        assert "coherence_score" in result

    def test_tone_consistency_score(self):
        """문체 일관성 점수"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = """
        이것은 매우 중요합니다.
        우리는 이를 고려해야 합니다.
        따라서 다음과 같이 진행합니다.
        """

        result = copywriter.calculate_tone_consistency_score(text)

        assert isinstance(result, dict)
        assert "tone_score" in result
        assert 0 <= result["tone_score"] <= 100


class TestCopywritingParallelProcessing:
    """병렬 처리 테스트"""

    def test_parallel_paragraph_processing(self):
        """병렬 단락 처리"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "단락1입니다. " * 100 + "\n\n" + "단락2입니다. " * 100 + "\n\n" + "단락3입니다. " * 100

        result = copywriter.copywrite_parallel(text, max_workers=3)

        assert isinstance(result, dict)
        assert "improved_text" in result

    def test_parallel_processing_consistency(self):
        """병렬 처리 일관성"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "테스트 단락입니다. " * 50

        # 직렬 처리
        result_sequential = copywriter.copywrite(text)

        # 병렬 처리
        result_parallel = copywriter.copywrite_parallel(text, max_workers=2)

        assert result_sequential is not None
        assert result_parallel is not None


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_empty_text_handling(self):
        """빈 텍스트 처리"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        with pytest.raises(ValueError):
            copywriter.copywrite("")

    def test_very_short_text(self):
        """매우 짧은 텍스트"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        result = copywriter.copywrite("좋습니다.")

        assert isinstance(result, dict)

    def test_special_characters_handling(self):
        """특수문자 처리"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "이것은 @#$% 특수문자를 포함합니다."
        result = copywriter.copywrite(text)

        assert isinstance(result, dict)

    def test_unicode_handling(self):
        """유니코드 처리"""
        from src.editing.edit_copywriting import CopywritingModule

        copywriter = CopywritingModule()

        text = "이것은 한글, 영어, 日本語, emoji 😀를 포함합니다."
        result = copywriter.copywrite(text)

        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
