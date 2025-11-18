# 교열 모듈 테스트
# 작성일: 2025-11-18
# 목적: 팩트 검증, 구식 정보 식별, Context7 MCP 통합 검증

import pytest


class TestFactIdentification:
    """검증 필요한 팩트 식별 테스트"""

    def test_identify_statistics(self):
        """통계/수치 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        2024년 한국 인구는 5천만 명입니다.
        GDP는 2조 달러를 초과했습니다.
        기술 산업은 30% 성장했습니다.
        """

        facts = checker.identify_facts(text)

        assert isinstance(facts, dict)
        assert "statistics" in facts
        assert len(facts["statistics"]) >= 2

    def test_identify_dates_and_years(self):
        """날짜와 년도 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        2023년 1월 15일에 출범했습니다.
        2025년 현재 성공적으로 운영 중입니다.
        COVID-19는 2020년부터 시작되었습니다.
        """

        facts = checker.identify_facts(text)

        assert isinstance(facts, dict)
        assert "dates" in facts or "years" in facts

    def test_identify_organizations(self):
        """기관명/회사명 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        Google은 2004년에 설립되었습니다.
        삼성전자는 한국 대표 기업입니다.
        WHO는 국제 보건 기구입니다.
        """

        facts = checker.identify_facts(text)

        assert isinstance(facts, dict)
        assert "organizations" in facts

    def test_identify_people_names(self):
        """인물명 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        스티브 잡스가 Apple을 창립했습니다.
        빌 게이츠는 Microsoft의 창업자입니다.
        김대중 전 대통령은 1998년 당선되었습니다.
        """

        facts = checker.identify_facts(text)

        assert isinstance(facts, dict)
        assert "people" in facts or "names" in facts


class TestFactVerification:
    """팩트 검증 테스트"""

    def test_verify_statistical_accuracy(self):
        """통계 정확성 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        # 검증할 통계
        fact = {
            "type": "statistic",
            "content": "2025년 한국 인구는 5천만 명입니다",
            "year": 2025
        }

        result = checker.verify_fact(fact, reference_year=2025)

        assert isinstance(result, dict)
        assert "verified" in result
        assert "confidence" in result

    def test_verify_organization_info(self):
        """기관 정보 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        fact = {
            "type": "organization",
            "name": "Google",
            "founding_year": 1998
        }

        result = checker.verify_fact(fact, reference_year=2025)

        assert isinstance(result, dict)

    def test_verify_historical_facts(self):
        """역사적 사실 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        fact = {
            "type": "historical",
            "content": "서울올림픽은 1988년에 개최되었습니다"
        }

        result = checker.verify_fact(fact, reference_year=2025)

        assert isinstance(result, dict)

    def test_fact_confidence_scoring(self):
        """팩트 신뢰도 평점"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        fact = {
            "type": "statistic",
            "content": "한국 인구는 약 5,000만 명입니다"
        }

        result = checker.verify_fact(fact)

        assert "confidence" in result
        assert 0 <= result["confidence"] <= 5


class TestOutdatedInformationDetection:
    """구식 정보 식별 테스트"""

    def test_detect_outdated_statistics(self):
        """구식 통계 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        # 오래된 년도의 통계
        text = """
        2010년 세계 인구는 69억 명이었습니다.
        2015년 스마트폰 보유율은 30%였습니다.
        """

        result = checker.detect_outdated_info(text, reference_year=2025)

        assert isinstance(result, dict)
        assert "outdated_items" in result

    def test_detect_obsolete_technology(self):
        """구식 기술 정보 식별"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        5G 기술은 아직 개발 중입니다.
        인공지능은 먼 미래 기술입니다.
        클라우드 컴퓨팅은 새로운 개념입니다.
        """

        result = checker.detect_outdated_info(text, reference_year=2025)

        assert isinstance(result, dict)

    def test_generate_editor_notes(self):
        """편집자 주석 생성"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        original_text = "5G 기술은 아직 개발 중입니다. (2015년 기준)"
        updated_fact = "5G 기술은 2023년부터 널리 사용되고 있습니다."

        note = checker.generate_editor_note(
            original_text=original_text,
            updated_fact=updated_fact,
            reference_year=2025
        )

        assert isinstance(note, str)
        assert "편집자" in note or "2025년" in note
        assert "✏️" in note or "[" in note


class TestContext7Integration:
    """Context7 MCP 통합 테스트"""

    @pytest.mark.skip(reason="Context7 MCP 연동 필수")
    def test_context7_search(self):
        """Context7 정보 검색"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        query = "2025년 한국 GDP"
        result = checker.search_context7(query)

        assert isinstance(result, dict)
        assert "results" in result

    @pytest.mark.skip(reason="Context7 MCP 연동 필수")
    def test_context7_fact_validation(self):
        """Context7 기반 팩트 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        fact = "Google은 1998년에 설립되었습니다"
        result = checker.validate_with_context7(fact)

        assert isinstance(result, dict)
        assert "verified" in result


class TestFactCheckingIntegration:
    """교열 모듈 통합 테스트"""

    def test_full_fact_checking_process(self):
        """전체 교열 프로세스"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        original_text = """
        2020년 세계 인구는 78억 명이었습니다.
        Google은 1998년에 창립되었습니다.
        5G는 아직 개발 중인 기술입니다.
        한국 GDP는 2조 달러를 초과했습니다.
        """

        result = checker.fact_check(original_text, reference_year=2025)

        assert isinstance(result, dict)
        assert "verified_text" in result or "edited_text" in result
        assert "facts_identified" in result
        assert "outdated_items" in result
        assert "editor_notes" in result
        assert "quality_score" in result

    def test_fact_checking_with_sources(self):
        """출처 포함 교열"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = "한국의 수도는 서울입니다."
        result = checker.fact_check(
            text,
            include_sources=True,
            reference_year=2025
        )

        assert isinstance(result, dict)

    def test_fact_checking_preserves_structure(self):
        """구조 보존 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        original_text = """# 제1장: 서론

2020년 통계에 따르면...

## 제1절: 배경

Google은 1998년...
"""

        result = checker.fact_check(original_text, reference_year=2025)

        assert isinstance(result, dict)
        # 마크다운 구조가 보존되어야 함


class TestFactCheckingPerformance:
    """교열 성능 테스트"""

    def test_fact_checking_on_large_text(self):
        """큰 텍스트의 교열"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        # 큰 문서 (5000자 이상)
        large_text = """
        2020년 데이터: 인구 78억, GDP 85조 달러.
        """ * 50  # 약 5000자

        result = checker.fact_check(large_text, reference_year=2025)

        assert result is not None

    def test_parallel_fact_verification(self):
        """병렬 팩트 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = "Google은 1998년. 삼성은 1938년. Apple은 1976년 창립되었습니다." * 20

        result = checker.fact_check_parallel(text, num_workers=3, reference_year=2025)

        assert isinstance(result, dict)

    def test_batch_fact_checking(self):
        """배치 팩트 검증"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        texts = [
            "2020년 인구는 78억 명입니다.",
            "Google은 1998년에 창립되었습니다.",
            "5G는 아직 개발 중입니다."
        ]

        results = checker.fact_check_batch(texts, reference_year=2025)

        assert isinstance(results, list)
        assert len(results) == len(texts)

        for result in results:
            assert isinstance(result, dict)


class TestFactCheckingErrorHandling:
    """교열 에러 처리 테스트"""

    def test_handle_invalid_text(self):
        """유효하지 않은 텍스트 처리"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        with pytest.raises((ValueError, TypeError)):
            checker.fact_check("")

    def test_handle_context7_failure(self):
        """Context7 실패 처리"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        # Context7 없이도 기본 검증 수행
        text = "Google은 1998년에 창립되었습니다."
        result = checker.fact_check(text, reference_year=2025)

        assert result is not None  # 폴백 검증 수행

    def test_handle_conflicting_information(self):
        """모순된 정보 처리"""
        from src.editing.edit_fact_checking import FactCheckingModule

        checker = FactCheckingModule()

        text = """
        Google은 1998년에 창립되었습니다.
        Google은 2000년에 창립되었습니다.
        """

        result = checker.fact_check(text, reference_year=2025)

        assert isinstance(result, dict)
        # 모순된 정보가 플래그되어야 함


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
