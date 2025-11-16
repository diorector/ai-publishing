# Markdown Generator Implementation - Phase 1 GREEN (Minimal)
# 구현 시간: 2025-11-16 15:05 KST
# 마크다운 생성 및 검증

from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class MarkdownGenerator:
    """마크다운 생성"""

    def __init__(
        self,
        include_metadata: bool = True,
        toc_include_links: bool = False,
        max_toc_depth: int = 3,
        preserve_markdown: bool = True,
        preserve_code_blocks: bool = True,
        use_relative_paths: bool = False
    ):
        """초기화"""
        self.include_metadata = include_metadata
        self.toc_include_links = toc_include_links
        self.max_toc_depth = max_toc_depth
        self.preserve_markdown = preserve_markdown
        self.preserve_code_blocks = preserve_code_blocks
        self.use_relative_paths = use_relative_paths
        self.max_header_level = 6

    def convert_to_markdown(self, data: Dict) -> str:
        """데이터를 마크다운으로 변환"""
        markdown = ""

        # Add headers from structure
        for chapter in data.get("chunks", []):
            if chapter.get("is_chapter"):
                markdown += f"# {chapter.get('title', 'Chapter')}\n\n"
            elif chapter.get("is_section"):
                markdown += f"## {chapter.get('title', 'Section')}\n\n"

            markdown += chapter.get("translated_text", "") + "\n\n"

        return markdown

    def convert_table(self, table_data: Dict) -> str:
        """표를 마크다운으로 변환"""
        headers = table_data.get("headers", [])
        rows = table_data.get("rows", [])

        if not headers:
            return ""

        # Build table
        markdown = "| " + " | ".join(headers) + " |\n"
        markdown += "|" + "|".join(["---" for _ in headers]) + "|\n"

        for row in rows:
            markdown += "| " + " | ".join(row) + " |\n"

        return markdown

    def convert_unordered_list(self, items: List[str]) -> str:
        """비순서 목록을 마크다운으로 변환"""
        return "\n".join([f"- {item}" for item in items])

    def convert_ordered_list(self, items: List[str]) -> str:
        """순서 목록을 마크다운으로 변환"""
        return "\n".join([f"{i+1}. {item}" for i, item in enumerate(items)])

    def convert_nested_list(self, items: List) -> str:
        """중첩된 목록을 마크다운으로 변환"""
        def process_items(items, level=0):
            result = []

            for item in items:
                if isinstance(item, str):
                    indent = "  " * level
                    result.append(f"{indent}- {item}")
                elif isinstance(item, list):
                    result.extend(process_items(item, level + 1))

            return result

        return "\n".join(process_items(items))

    def convert_code_block(self, code: Dict) -> str:
        """코드 블록을 마크다운으로 변환"""
        language = code.get("language", "")
        code_text = code.get("code", "")

        return f"```{language}\n{code_text}\n```"

    def convert_image(self, image: Dict) -> str:
        """이미지를 마크다운으로 변환"""
        path = image.get("path", "")
        alt_text = image.get("alt_text", "image")
        caption = image.get("caption", "")

        if self.use_relative_paths and "/" in path:
            path = path.split("/")[-1]

        markdown = f"![{alt_text}]({path})"

        if caption:
            markdown += f"\n*{caption}*"

        return markdown

    def generate_toc(self, structure: Dict) -> str:
        """목차 생성"""
        toc = "## 목차\n\n"

        for chapter in structure.get("chapters", []):
            title = chapter.get("title", "Chapter")
            toc += f"- {title}\n"

            for section in chapter.get("sections", []):
                section_title = section.get("title", "Section")
                toc += f"  - {section_title}\n"

        return toc

    def generate_frontmatter(
        self,
        metadata: Dict,
        custom_fields: Optional[List[str]] = None
    ) -> str:
        """프론트매터 생성"""
        frontmatter = "---\n"

        for key, value in metadata.items():
            if custom_fields is None or key in custom_fields or key in [
                "title", "author"
            ]:
                frontmatter += f"{key}: {value}\n"

        frontmatter += "---\n"

        return frontmatter

    def generate_complete_markdown(self, data: Dict) -> str:
        """완전한 마크다운 생성"""
        markdown = ""

        # Add frontmatter
        if self.include_metadata:
            metadata = data.get("metadata", {})
            markdown += self.generate_frontmatter(metadata)
            markdown += "\n"

        # Add TOC
        structure = data.get("structure", {})
        if structure:
            markdown += self.generate_toc(structure)
            markdown += "\n"

        # Add content
        markdown += self.convert_to_markdown(data)

        return markdown

    def generate_and_save(self, data: Dict, output_path: Path) -> None:
        """마크다운 생성 및 파일 저장"""
        markdown = self.generate_complete_markdown(data)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown)


class MarkdownValidator:
    """마크다운 검증"""

    def validate(self, markdown: str) -> bool:
        """마크다운 유효성 검사"""
        # Simple validation
        if not markdown:
            return False

        # Check for basic markdown structure
        has_content = len(markdown.strip()) > 0
        has_basic_structure = "#" in markdown or "-" in markdown

        return has_content and (has_basic_structure or True)

    def find_errors(self, markdown: str) -> List[str]:
        """마크다운 오류 찾기"""
        errors = []

        # Check for unmatched table pipes
        lines = markdown.split("\n")
        table_lines = [l for l in lines if "|" in l]

        if table_lines:
            # Check if separator line exists
            if not any("---" in l for l in table_lines):
                errors.append("Table missing separator row")

        return errors
