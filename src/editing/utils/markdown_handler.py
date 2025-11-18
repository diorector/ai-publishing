# 마크다운 처리 유틸리티
# 작성일: 2025-11-18
# 목적: 마크다운 파일 읽기, 쓰기, 구조 분석

from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import re


class MarkdownHandler:
    """마크다운 파일 처리"""

    @staticmethod
    def read_markdown(file_path: str) -> str:
        """마크다운 파일 읽기"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp949') as f:
                return f.read()

    @staticmethod
    def write_markdown(file_path: str, content: str) -> None:
        """마크다운 파일 쓰기"""
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    @staticmethod
    def extract_headings(content: str) -> List[Dict[str, Any]]:
        """제목 추출"""
        headings = []

        lines = content.split('\n')
        for i, line in enumerate(lines):
            match = re.match(r'^(#+)\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({
                    'level': level,
                    'title': title,
                    'line': i,
                })

        return headings

    @staticmethod
    def extract_sections(content: str) -> List[Dict[str, Any]]:
        """섹션 추출"""
        sections = []

        lines = content.split('\n')
        current_section = None

        for i, line in enumerate(lines):
            match = re.match(r'^(#+)\s+(.+)$', line)
            if match:
                if current_section:
                    sections.append(current_section)

                level = len(match.group(1))
                title = match.group(2).strip()
                current_section = {
                    'level': level,
                    'title': title,
                    'start_line': i,
                    'content': [],
                }
            elif current_section is not None:
                current_section['content'].append(line)

        if current_section:
            sections.append(current_section)

        return sections

    @staticmethod
    def extract_code_blocks(content: str) -> List[Dict[str, str]]:
        """코드 블록 추출"""
        code_blocks = []

        pattern = r'```(\w+)?\n(.*?)\n```'
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            language = match.group(1) or 'text'
            code = match.group(2)
            code_blocks.append({
                'language': language,
                'code': code,
            })

        return code_blocks

    @staticmethod
    def extract_links(content: str) -> List[Dict[str, str]]:
        """링크 추출"""
        links = []

        pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        matches = re.finditer(pattern, content)

        for match in matches:
            text = match.group(1)
            url = match.group(2)
            links.append({
                'text': text,
                'url': url,
            })

        return links

    @staticmethod
    def extract_images(content: str) -> List[Dict[str, str]]:
        """이미지 추출"""
        images = []

        pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        matches = re.finditer(pattern, content)

        for match in matches:
            alt = match.group(1)
            url = match.group(2)
            images.append({
                'alt': alt,
                'url': url,
            })

        return images

    @staticmethod
    def extract_metadata(content: str) -> Dict[str, str]:
        """메타데이터 추출 (YAML front matter)"""
        metadata = {}

        if content.startswith('---'):
            # YAML front matter 파싱
            lines = content.split('\n')
            end_idx = -1

            for i in range(1, len(lines)):
                if lines[i].startswith('---'):
                    end_idx = i
                    break

            if end_idx > 0:
                for line in lines[1:end_idx]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"\'')

        return metadata

    @staticmethod
    def extract_tables(content: str) -> List[List[str]]:
        """테이블 추출"""
        tables = []

        # 마크다운 테이블 패턴
        pattern = r'\|(.+)\|'
        matches = re.finditer(pattern, content)

        for match in matches:
            row = match.group(1).split('|')
            row = [cell.strip() for cell in row]
            tables.append(row)

        return tables

    @staticmethod
    def get_word_count(content: str) -> int:
        """단어 수 계산"""
        # 마크다운 문법 제거
        cleaned = re.sub(r'[#*`\[\]()_~-]', '', content)
        words = cleaned.split()
        return len(words)

    @staticmethod
    def get_statistics(content: str) -> Dict[str, Any]:
        """마크다운 문서 통계"""
        headings = MarkdownHandler.extract_headings(content)
        code_blocks = MarkdownHandler.extract_code_blocks(content)
        links = MarkdownHandler.extract_links(content)
        images = MarkdownHandler.extract_images(content)
        tables = MarkdownHandler.extract_tables(content)

        return {
            'word_count': MarkdownHandler.get_word_count(content),
            'character_count': len(content),
            'line_count': len(content.split('\n')),
            'heading_count': len(headings),
            'code_block_count': len(code_blocks),
            'link_count': len(links),
            'image_count': len(images),
            'table_count': len(tables),
            'headings': headings,
        }

    @staticmethod
    def remove_formatting(content: str) -> str:
        """마크다운 형식 제거"""
        # 제목 마크 제거
        content = re.sub(r'^#+\s+', '', content, flags=re.MULTILINE)

        # 굵은 글씨 제거
        content = re.sub(r'\*\*(.+?)\*\*', r'\1', content)
        content = re.sub(r'__(.+?)__', r'\1', content)

        # 이탤릭 제거
        content = re.sub(r'\*(.+?)\*', r'\1', content)
        content = re.sub(r'_(.+?)_', r'\1', content)

        # 코드 형식 제거
        content = re.sub(r'`(.+?)`', r'\1', content)
        content = re.sub(r'```\w*\n(.+?)\n```', r'\1', content, flags=re.DOTALL)

        # 링크 형식 변경 (텍스트만 남김)
        content = re.sub(r'\[(.+?)\]\(.*?\)', r'\1', content)

        # 이미지 제거
        content = re.sub(r'!\[.*?\]\(.*?\)', '', content)

        # 리스트 마크 제거
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)

        # 인용문 마크 제거
        content = re.sub(r'^>\s+', '', content, flags=re.MULTILINE)

        return content
