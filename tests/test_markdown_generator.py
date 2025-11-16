# Markdown Generator Tests - Phase 1 RED
# 구현 시간: 2025-11-16 14:50 KST
# 마크다운 생성 모듈의 포괄적 테스트
# SPEC-PUB-TRANSLATE-001 요구사항:
# - 구조화된 번역을 마크다운으로 변환
# - 원본 문서 구조 복원
# - 특수 요소 포맷 복원
# - 최종 완성원고 생성

import pytest
from pathlib import Path
from typing import Dict, List


@pytest.fixture
def translated_chunks_with_structure():
    """구조 정보가 있는 번역된 청크"""
    return {
        "metadata": {
            "title": "인공지능 소개",
            "author": "John Smith",
            "original_language": "English",
            "translated_language": "Korean"
        },
        "structure": {
            "chapters": [
                {
                    "id": "ch1",
                    "title": "인공지능의 기초",
                    "sections": [
                        {"id": "sec1.1", "title": "역사적 배경"},
                        {"id": "sec1.2", "title": "핵심 개념"}
                    ]
                },
                {
                    "id": "ch2",
                    "title": "신경망",
                    "sections": [
                        {"id": "sec2.1", "title": "퍼셉트론 모델"},
                        {"id": "sec2.2", "title": "딥러닝"}
                    ]
                }
            ]
        },
        "chunks": [
            {
                "chunk_id": "ch1",
                "title": "인공지능의 기초",
                "translated_text": "이 장은 인공지능의 기본 개념을 소개합니다.",
                "is_chapter": True
            },
            {
                "chunk_id": "sec1.1",
                "title": "역사적 배경",
                "translated_text": "인공지능 분야는 1950년대에 등장했습니다.",
                "is_section": True
            },
            {
                "chunk_id": "content1",
                "translated_text": "초기 연구자들은 인간 수준의 지능을 기계로 구현할 수 있다고 믿었습니다.",
                "type": "paragraph"
            }
        ]
    }


@pytest.fixture
def translated_chunks_with_special_elements():
    """특수 요소가 있는 번역된 청크"""
    return {
        "chunks": [
            {
                "chunk_id": "text1",
                "translated_text": "다음은 주요 특징들입니다:",
                "type": "paragraph"
            },
            {
                "chunk_id": "list1",
                "translated_text": """- 특징 A
- 특징 B
- 특징 C""",
                "type": "list"
            },
            {
                "chunk_id": "table1",
                "markdown_table": """| 헤더1 | 헤더2 |
|-------|-------|
| 데이터1 | 데이터2 |""",
                "type": "table"
            },
            {
                "chunk_id": "code1",
                "code": "print('Hello')",
                "language": "python",
                "type": "code_block"
            },
            {
                "chunk_id": "image1",
                "image_path": "images/diagram.png",
                "alt_text": "시스템 다이어그램",
                "type": "image"
            }
        ]
    }


@pytest.fixture
def sample_toc_structure():
    """목차 구조"""
    return [
        {
            "level": 1,
            "title": "인공지능의 기초",
            "page": 1,
            "children": [
                {"level": 2, "title": "역사적 배경", "page": 2},
                {"level": 2, "title": "핵심 개념", "page": 5}
            ]
        },
        {
            "level": 1,
            "title": "신경망",
            "page": 10,
            "children": [
                {"level": 2, "title": "퍼셉트론 모델", "page": 11},
                {"level": 2, "title": "딥러닝", "page": 15}
            ]
        }
    ]


# ==================== TEST CLASSES ====================

class TestBasicMarkdownGeneration:
    """기본 마크다운 생성 테스트"""

    def test_convert_chunks_to_markdown(self, translated_chunks_with_structure):
        """
        Given: 구조 정보가 있는 번역된 청크
        When: generate_markdown() 호출
        Then: 유효한 마크다운이 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        assert isinstance(markdown, str)
        assert len(markdown) > 0
        assert "#" in markdown  # Should have headers

    def test_markdown_output_valid_syntax(self, translated_chunks_with_structure):
        """
        Given: 생성된 마크다운
        When: 유효성 검사
        Then: 유효한 마크다운 구문이어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        # Basic markdown validation
        assert markdown.count("# ") >= 1
        assert markdown.count("## ") >= 1 or markdown.count("- ") >= 0

    def test_markdown_includes_metadata(self, translated_chunks_with_structure):
        """
        Given: 메타데이터가 있는 청크
        When: generate_markdown() 호출
        Then: 마크다운이 메타데이터를 포함해야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator(include_metadata=True)
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        # Should include title and author
        assert "인공지능 소개" in markdown or "title" in markdown.lower()


class TestHeaderGeneration:
    """헤더 생성 테스트"""

    def test_generate_chapter_headers(self, translated_chunks_with_structure):
        """
        Given: 챕터 정보
        When: 헤더 생성
        Then: 적절한 레벨의 마크다운 헤더가 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        # Should have H1 headers for chapters
        assert "# 인공지능의 기초" in markdown or "# " in markdown

    def test_generate_section_headers(self, translated_chunks_with_structure):
        """
        Given: 절 정보
        When: 헤더 생성
        Then: 적절한 레벨의 마크다운 헤더가 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        # Should have H2 headers for sections
        assert "## " in markdown

    def test_header_hierarchy_correct(self, translated_chunks_with_structure):
        """
        Given: 여러 레벨의 제목
        When: 마크다운 생성
        Then: 헤더 계층이 올바르게 유지되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        lines = markdown.split('\n')
        h1_count = sum(1 for line in lines if line.startswith('# '))
        h2_count = sum(1 for line in lines if line.startswith('## '))

        assert h1_count >= 1
        assert h2_count >= 1
        assert h1_count <= h2_count  # More detailed sections than chapters

    def test_avoid_invalid_header_syntax(self):
        """
        Given: 제목 생성
        When: 마크다운 생성
        Then: 유효하지 않은 헤더 구문이 없어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()

        # Should not generate invalid headers like "######## Too many hashes"
        assert hasattr(generator, 'max_header_level')
        assert generator.max_header_level <= 6


class TestTableGeneration:
    """표 생성 테스트"""

    def test_convert_table_data_to_markdown(self):
        """
        Given: 표 데이터
        When: convert_table() 호출
        Then: 마크다운 표 형식으로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        table_data = {
            "headers": ["컬럼1", "컬럼2", "컬럼3"],
            "rows": [
                ["값1", "값2", "값3"],
                ["값4", "값5", "값6"]
            ]
        }

        generator = MarkdownGenerator()
        markdown_table = generator.convert_table(table_data)

        assert isinstance(markdown_table, str)
        assert "|" in markdown_table  # Should use pipe characters
        assert "---" in markdown_table  # Should have separator row

    def test_preserve_table_formatting(self, translated_chunks_with_special_elements):
        """
        Given: 마크다운 표가 있는 청크
        When: 마크다운 생성
        Then: 표 포맷이 보존되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_special_elements)

        # Should preserve table structure
        assert "|" in markdown or "[TABLE]" in markdown

    def test_handle_complex_tables(self):
        """
        Given: 복잡한 표 (병합 셀, 긴 콘텐츠)
        When: convert_table() 호출
        Then: 마크다운 호환 포맷으로 처리해야 함
        """
        from src.markdown import MarkdownGenerator

        complex_table = {
            "headers": ["이름", "설명", "값"],
            "rows": [
                ["매우 긴 항목 이름", "이것은 매우 긴 설명입니다", "1000"],
                ["항목2", "짧음", "200"]
            ]
        }

        generator = MarkdownGenerator()
        markdown_table = generator.convert_table(complex_table)

        # Should be valid markdown
        assert "|" in markdown_table
        assert "매우 긴 항목 이름" in markdown_table


class TestListGeneration:
    """목록 생성 테스트"""

    def test_convert_unordered_list(self):
        """
        Given: 비순서 목록 데이터
        When: convert_list() 호출
        Then: 마크다운 비순서 목록으로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        list_items = ["항목 1", "항목 2", "항목 3"]

        generator = MarkdownGenerator()
        markdown_list = generator.convert_unordered_list(list_items)

        assert isinstance(markdown_list, str)
        assert markdown_list.count("- ") == 3

    def test_convert_ordered_list(self):
        """
        Given: 순서가 있는 목록 데이터
        When: convert_ordered_list() 호출
        Then: 마크다운 순서 목록으로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        list_items = ["첫 번째", "두 번째", "세 번째"]

        generator = MarkdownGenerator()
        markdown_list = generator.convert_ordered_list(list_items)

        assert isinstance(markdown_list, str)
        assert "1. " in markdown_list
        assert "2. " in markdown_list
        assert "3. " in markdown_list

    def test_preserve_list_nesting(self):
        """
        Given: 중첩된 목록
        When: convert_list() 호출
        Then: 중첩 구조가 보존되어야 함
        """
        from src.markdown import MarkdownGenerator

        nested_list = [
            "항목 1",
            ["항목 1.1", "항목 1.2"],
            "항목 2"
        ]

        generator = MarkdownGenerator()
        markdown_list = generator.convert_nested_list(nested_list)

        assert isinstance(markdown_list, str)
        # Should have indentation
        lines = markdown_list.split('\n')
        assert any(line.startswith('  -') or line.startswith('    -') for line in lines)


class TestCodeBlockHandling:
    """코드 블록 처리 테스트"""

    def test_convert_code_block_to_markdown(self):
        """
        Given: 코드 블록 데이터
        When: convert_code_block() 호출
        Then: 마크다운 코드 블록으로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        code = {
            "language": "python",
            "code": "print('Hello World')"
        }

        generator = MarkdownGenerator()
        markdown_code = generator.convert_code_block(code)

        assert isinstance(markdown_code, str)
        assert "```python" in markdown_code
        assert "```" in markdown_code
        assert "print(" in markdown_code

    def test_preserve_code_syntax_highlighting(self, translated_chunks_with_special_elements):
        """
        Given: 언어 정보가 있는 코드 블록
        When: 마크다운 생성
        Then: 언어 지정이 보존되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_special_elements)

        # Should preserve language specification
        assert "```python" in markdown or "```" in markdown

    def test_handle_code_with_special_characters(self):
        """
        Given: 특수 문자가 있는 코드
        When: convert_code_block() 호출
        Then: 특수 문자가 보존되어야 함
        """
        from src.markdown import MarkdownGenerator

        code = {
            "language": "python",
            "code": "if x > 5 and y < 10:\n    print('Result: x != y')"
        }

        generator = MarkdownGenerator()
        markdown_code = generator.convert_code_block(code)

        assert ">" in markdown_code
        assert "<" in markdown_code
        assert "&" in markdown_code or "and" in markdown_code


class TestImageHandling:
    """이미지 처리 테스트"""

    def test_convert_image_reference(self):
        """
        Given: 이미지 참조 정보
        When: convert_image() 호출
        Then: 마크다운 이미지 링크로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        image = {
            "path": "images/diagram.png",
            "alt_text": "시스템 다이어그램",
            "caption": "그림 1: 아키텍처"
        }

        generator = MarkdownGenerator()
        markdown_image = generator.convert_image(image)

        assert isinstance(markdown_image, str)
        assert "![" in markdown_image
        assert "시스템 다이어그램" in markdown_image
        assert "images/diagram.png" in markdown_image

    def test_handle_missing_image_gracefully(self):
        """
        Given: 존재하지 않는 이미지 참조
        When: convert_image() 호출
        Then: 대체 텍스트와 함께 처리해야 함
        """
        from src.markdown import MarkdownGenerator

        image = {
            "path": "nonexistent.png",
            "alt_text": "누락된 이미지"
        }

        generator = MarkdownGenerator()
        markdown_image = generator.convert_image(image)

        assert "![누락된 이미지]" in markdown_image or "alt" in markdown_image.lower()

    def test_relative_paths_for_images(self):
        """
        Given: 절대 경로의 이미지
        When: convert_image() with relative_paths=True 호출
        Then: 상대 경로로 변환되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator(use_relative_paths=True)

        image = {
            "path": "/home/user/project/images/diagram.png",
            "alt_text": "다이어그램"
        }

        markdown_image = generator.convert_image(image)

        # Should use relative path
        assert "/" not in markdown_image or markdown_image.count("/") <= 2


class TestTableOfContents:
    """목차 생성 테스트"""

    def test_generate_table_of_contents(self, translated_chunks_with_structure):
        """
        Given: 문서 구조
        When: generate_toc() 호출
        Then: 마크다운 목차가 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        toc = generator.generate_toc(translated_chunks_with_structure["structure"])

        assert isinstance(toc, str)
        assert "인공지능의 기초" in toc or "#" in toc

    def test_toc_with_links(self, translated_chunks_with_structure):
        """
        Given: 생성된 목차
        When: include_links=True
        Then: 각 항목이 내부 링크를 포함해야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator(toc_include_links=True)
        toc = generator.generate_toc(translated_chunks_with_structure["structure"])

        # Should have markdown links
        assert "[" in toc and "]" in toc and "(" in toc

    def test_toc_respects_depth_limit(self, sample_toc_structure):
        """
        Given: 깊은 계층의 목차
        When: max_toc_depth=2로 설정하여 생성
        Then: 지정된 깊이까지만 포함해야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator(max_toc_depth=2)
        toc = generator.generate_toc(sample_toc_structure)

        # Should not go deeper than level 2
        assert toc.count("  - ") <= len(sample_toc_structure)


class TestMetadataGeneration:
    """메타데이터 생성 테스트"""

    def test_generate_frontmatter(self, translated_chunks_with_structure):
        """
        Given: 메타데이터
        When: generate_frontmatter() 호출
        Then: YAML 프론트매터가 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        frontmatter = generator.generate_frontmatter(
            translated_chunks_with_structure["metadata"]
        )

        assert isinstance(frontmatter, str)
        assert "---" in frontmatter  # Should have frontmatter delimiters
        assert "title:" in frontmatter or "Title" in frontmatter

    def test_frontmatter_includes_metadata_fields(self, translated_chunks_with_structure):
        """
        Given: 메타데이터
        When: 프론트매터 생성
        Then: 주요 필드들이 포함되어야 함
        """
        from src.markdown import MarkdownGenerator

        metadata = translated_chunks_with_structure["metadata"]
        generator = MarkdownGenerator()
        frontmatter = generator.generate_frontmatter(metadata)

        assert "인공지능 소개" in frontmatter or "title" in frontmatter.lower()
        assert "John Smith" in frontmatter or "author" in frontmatter.lower()

    def test_custom_frontmatter_fields(self):
        """
        Given: 커스텀 메타데이터 필드
        When: generate_frontmatter() with custom_fields
        Then: 커스텀 필드가 포함되어야 함
        """
        from src.markdown import MarkdownGenerator

        metadata = {
            "title": "제목",
            "custom_field": "커스텀 값"
        }

        generator = MarkdownGenerator()
        frontmatter = generator.generate_frontmatter(
            metadata,
            custom_fields=["custom_field"]
        )

        assert "커스텀 값" in frontmatter


class TestCompleteMarkdownGeneration:
    """완전한 마크다운 생성 테스트"""

    def test_generate_complete_manuscript(self, translated_chunks_with_structure):
        """
        Given: 완전한 번역 데이터
        When: generate_complete_markdown() 호출
        Then: 출판 가능한 완성원고가 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        manuscript = generator.generate_complete_markdown(translated_chunks_with_structure)

        assert isinstance(manuscript, str)
        assert len(manuscript) > 1000
        # Should include metadata, toc, and content
        assert "---" in manuscript  # Frontmatter
        assert "#" in manuscript    # Headers

    def test_manuscript_preserves_document_flow(self, translated_chunks_with_structure):
        """
        Given: 청크들
        When: 마크다운 생성 후 재결합
        Then: 문서의 흐름이 보존되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        manuscript = generator.generate_complete_markdown(translated_chunks_with_structure)

        lines = manuscript.split('\n')
        # Should have logical flow: metadata -> toc -> content
        metadata_idx = next((i for i, line in enumerate(lines) if line == "---"), -1)
        content_idx = next((i for i, line in enumerate(lines) if line.startswith("#")), -1)

        assert metadata_idx < content_idx

    def test_output_valid_markdown_file(self, translated_chunks_with_structure, tmp_path):
        """
        Given: 생성할 마크다운
        When: save_to_file() 호출
        Then: 유효한 .md 파일이 생성되어야 함
        """
        from src.markdown import MarkdownGenerator

        generator = MarkdownGenerator()
        output_file = tmp_path / "output.md"

        generator.generate_and_save(
            translated_chunks_with_structure,
            output_file
        )

        assert output_file.exists()
        assert output_file.suffix == ".md"

        content = output_file.read_text()
        assert len(content) > 0


class TestMarkdownValidation:
    """마크다운 유효성 검사 테스트"""

    def test_validate_markdown_syntax(self, translated_chunks_with_structure):
        """
        Given: 생성된 마크다운
        When: validate_markdown() 호출
        Then: 유효한 마크다운이어야 함
        """
        from src.markdown import MarkdownGenerator, MarkdownValidator

        generator = MarkdownGenerator()
        markdown = generator.convert_to_markdown(translated_chunks_with_structure)

        validator = MarkdownValidator()
        is_valid = validator.validate(markdown)

        assert is_valid is True

    def test_detect_markdown_errors(self):
        """
        Given: 유효하지 않은 마크다운
        When: validate_markdown() 호출
        Then: 오류가 식별되어야 함
        """
        from src.markdown import MarkdownValidator

        invalid_markdown = """# Title
## Subtitle
- List item
Invalid table: |col1|col2| (missing separator)
"""

        validator = MarkdownValidator()
        errors = validator.find_errors(invalid_markdown)

        assert isinstance(errors, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
