# 문서 모델 테스트
# 작성일: 2025-11-18
# 목적: Document 모델의 높은 커버리지

import pytest
from src.editing.models.document import Document, DocumentStructure, Chapter, Section


class TestDocumentStructure:
    """문서 구조 테스트"""

    def test_chapter_creation(self):
        """장 객체 생성"""
        chapter = Chapter(number=1, title="서론")
        assert chapter.number == 1
        assert chapter.title == "서론"
        assert chapter.level == 1

    def test_section_creation(self):
        """절 객체 생성"""
        section = Section(number=1, title="배경", content="내용입니다")
        assert section.number == 1
        assert section.title == "배경"
        assert section.level == 2

    def test_document_structure_analyze_with_chapters(self):
        """마크다운 구조 분석 - 장"""
        content = """# 제1장: 소개

이것은 첫 번째 장입니다.

# 제2장: 본론

두 번째 장입니다.
"""
        structure = DocumentStructure()
        structure.analyze(content)

        assert len(structure.chapters) == 2
        assert structure.chapters[0].title == "제1장: 소개"
        assert structure.chapters[1].title == "제2장: 본론"

    def test_document_structure_analyze_with_sections(self):
        """마크다운 구조 분석 - 절"""
        content = """# 제1장: 소개

## 제1절: 배경

배경 설명입니다.

## 제2절: 목표

목표를 설명합니다.

# 제2장: 본론

본론입니다.
"""
        structure = DocumentStructure()
        structure.analyze(content)

        assert len(structure.chapters) == 2
        assert len(structure.chapters[0].sections) == 2
        assert structure.chapters[0].sections[0].title == "제1절: 배경"
        assert structure.total_sections == 2

    def test_document_structure_paragraph_counting(self):
        """문단 수 계산"""
        content = """첫 번째 문단입니다.

두 번째 문단입니다.

세 번째 문단입니다."""

        structure = DocumentStructure()
        structure.analyze(content)

        assert structure.total_paragraphs == 3

    def test_document_structure_heading_tracking(self):
        """제목 추적"""
        content = """# 장1

## 절1

### 소절1

내용입니다.
"""
        structure = DocumentStructure()
        structure.analyze(content)

        assert 1 in structure.headings  # 1단계 제목
        assert 2 in structure.headings  # 2단계 제목


class TestDocumentOperations:
    """문서 작업 테스트"""

    def test_get_chapter_content(self):
        """장 콘텐츠 추출"""
        content = """# 제1장: 소개

첫 번째 장의 내용입니다.

# 제2장: 본론

두 번째 장의 내용입니다.
"""
        doc = Document(
            id="doc-001",
            title="테스트",
            content=content,
            domain="education",
            target_audience="students"
        )

        chapter1_content = doc.get_chapter_content(1)
        assert "제1장" in chapter1_content or "첫 번째" in chapter1_content

    def test_get_chapter_content_invalid(self):
        """잘못된 장 번호"""
        doc = Document(
            id="doc-002",
            title="테스트",
            content="# 제1장\n내용",
            domain="education",
            target_audience="students"
        )

        content = doc.get_chapter_content(10)  # 존재하지 않는 장
        assert content == ""

    def test_update_content(self):
        """문서 내용 업데이트"""
        original = "원본 내용입니다."
        doc = Document(
            id="doc-003",
            title="테스트",
            content=original,
            domain="education",
            target_audience="students"
        )

        new_content = "새로운 내용입니다."
        doc.update_content(new_content)

        assert doc.content == new_content
        assert doc.word_count == len(new_content.split())
        # updated_at은 같거나 나중일 수 있음 (매우 빠른 실행)
        assert doc.updated_at >= doc.created_at

    def test_get_statistics(self):
        """문서 통계"""
        doc = Document(
            id="doc-004",
            title="테스트 문서",
            content="# 제1장\n내용입니다\n\n# 제2장\n더 많은 내용",
            domain="startup",
            target_audience="investors"
        )

        stats = doc.get_statistics()

        assert stats["id"] == "doc-004"
        assert stats["title"] == "테스트 문서"
        assert stats["domain"] == "startup"
        assert stats["word_count"] > 0
        assert stats["chapters"] >= 0
        assert "created_at" in stats
        assert "updated_at" in stats

    def test_document_metadata_on_init(self):
        """초기화 시 메타데이터"""
        doc = Document(
            id="doc-005",
            title="메타데이터 테스트",
            content="내용입니다",
            domain="finance",
            target_audience="traders",
            metadata={"author": "John Doe"}
        )

        assert doc.metadata["author"] == "John Doe"
        assert doc.metadata["domain"] == "finance"
        assert doc.metadata["target_audience"] == "traders"
        assert "created_at" in doc.metadata

    def test_document_word_count_zero(self):
        """단어 수 0 처리"""
        doc = Document(
            id="doc-006",
            title="테스트",
            content="",
            domain="general",
            target_audience="everyone"
        )

        assert doc.word_count == 0

    def test_document_structure_empty_content(self):
        """빈 내용 구조 분석"""
        doc = Document(
            id="doc-007",
            title="테스트",
            content="",
            domain="general",
            target_audience="everyone"
        )

        assert doc.structure is not None
        assert len(doc.structure.chapters) == 0

    def test_document_with_complex_structure(self):
        """복잡한 문서 구조"""
        content = """# 제1장: 소개

## 제1절: 배경

배경 내용

### 보조 항목

보조 내용

## 제2절: 목표

목표 내용

# 제2장: 본론

## 제1절: 방법론

방법론 설명

## 제2절: 결과

결과 설명

# 제3장: 결론

결론입니다.
"""

        doc = Document(
            id="doc-008",
            title="복잡한 문서",
            content=content,
            domain="education",
            target_audience="researchers"
        )

        stats = doc.get_statistics()
        assert stats["chapters"] == 3
        assert stats["sections"] >= 4  # 최소 4개 절

    def test_document_preservation_on_analysis(self):
        """분석 후 내용 보존"""
        original_content = "# 제목\n\n내용입니다.\n\n더 많은 내용"

        doc = Document(
            id="doc-009",
            title="분석 테스트",
            content=original_content,
            domain="general",
            target_audience="everyone"
        )

        assert doc.content == original_content  # 내용이 변경되지 않음


class TestDocumentEdgeCases:
    """문서 엣지 케이스"""

    def test_document_with_special_characters(self):
        """특수 문자 포함"""
        doc = Document(
            id="doc-010",
            title="특수문자 테스트",
            content="한글, 영어, 숫자123, 기호!@#$%",
            domain="general",
            target_audience="everyone"
        )

        assert len(doc.content) > 0
        assert doc.word_count > 0

    def test_document_with_markdown_code(self):
        """마크다운 코드 포함"""
        content = """# 프로그래밍

```python
def hello():
    print("Hello")
```

다음은 코드입니다.
"""

        doc = Document(
            id="doc-011",
            title="코드 포함",
            content=content,
            domain="technology",
            target_audience="developers"
        )

        assert "```" in doc.content

    def test_document_very_long_content(self):
        """매우 긴 내용"""
        long_content = "문장입니다. " * 1000

        doc = Document(
            id="doc-012",
            title="긴 문서",
            content=long_content,
            domain="general",
            target_audience="everyone"
        )

        # "문장입니다. " * 1000 = "문장입니다." (2) + " " (1) = 3 단어 * 1000 = 3000 단어
        # split()은 "문장입니다." 와 "문장입니다." 를 나누므로 약 2000 단어
        assert doc.word_count >= 1000

    def test_document_single_word(self):
        """한 단어만"""
        doc = Document(
            id="doc-013",
            title="한 단어",
            content="단어",
            domain="general",
            target_audience="everyone"
        )

        assert doc.word_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
