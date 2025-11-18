# Diff 생성 유틸리티
# 작성일: 2025-11-18
# 목적: 원문과 편집본 비교 및 변경사항 시각화

from typing import Dict, List, Any, Tuple
import difflib


class DiffGenerator:
    """원문과 편집본 비교 및 Diff 생성"""

    @staticmethod
    def generate_diff(original: str, edited: str) -> List[Dict[str, Any]]:
        """텍스트 Diff 생성"""
        diffs = []

        # 라인 단위 diff
        original_lines = original.split('\n')
        edited_lines = edited.split('\n')

        diff_lines = list(difflib.unified_diff(
            original_lines,
            edited_lines,
            lineterm='',
            n=1
        ))

        # Diff 파싱
        for line in diff_lines:
            if line.startswith('@@'):
                # 헤더 스킵
                continue
            elif line.startswith('-'):
                diffs.append({
                    'type': 'deletion',
                    'content': line[1:],
                })
            elif line.startswith('+'):
                diffs.append({
                    'type': 'addition',
                    'content': line[1:],
                })
            elif line.startswith(' '):
                diffs.append({
                    'type': 'context',
                    'content': line[1:],
                })

        return diffs

    @staticmethod
    def generate_side_by_side(original: str, edited: str) -> Dict[str, List[str]]:
        """좌우 비교 형식 생성"""
        original_lines = original.split('\n')
        edited_lines = edited.split('\n')

        # 라인 수 맞추기
        max_lines = max(len(original_lines), len(edited_lines))
        original_lines.extend([''] * (max_lines - len(original_lines)))
        edited_lines.extend([''] * (max_lines - len(edited_lines)))

        return {
            'original': original_lines,
            'edited': edited_lines,
        }

    @staticmethod
    def calculate_similarity(original: str, edited: str) -> float:
        """편집 전후 유사도 계산"""
        matcher = difflib.SequenceMatcher(None, original, edited)
        ratio = matcher.ratio()
        return ratio * 100

    @staticmethod
    def generate_html_diff(original: str, edited: str) -> str:
        """HTML 형식 Diff 생성"""
        from difflib import HtmlDiff

        hdiff = HtmlDiff()
        html = hdiff.make_file(
            original.split('\n'),
            edited.split('\n'),
            context=True,
            numlines=1
        )
        return html

    @staticmethod
    def highlight_changes(original: str, edited: str, context_size: int = 50) -> List[Dict[str, Any]]:
        """변경 부분 강조"""
        changes = []

        # 단어 단위 비교
        original_words = original.split()
        edited_words = edited.split()

        matcher = difflib.SequenceMatcher(None, original_words, edited_words)

        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                changes.append({
                    'type': 'changed',
                    'original': ' '.join(original_words[i1:i2]),
                    'edited': ' '.join(edited_words[j1:j2]),
                    'position': i1,
                })
            elif tag == 'delete':
                changes.append({
                    'type': 'deleted',
                    'content': ' '.join(original_words[i1:i2]),
                    'position': i1,
                })
            elif tag == 'insert':
                changes.append({
                    'type': 'added',
                    'content': ' '.join(edited_words[j1:j2]),
                    'position': j1,
                })

        return changes

    @staticmethod
    def generate_markdown_diff(original: str, edited: str) -> str:
        """마크다운 형식 Diff 생성"""
        markdown = "# 변경 사항\n\n"

        diffs = DiffGenerator.generate_diff(original, edited)

        for diff in diffs:
            if diff['type'] == 'deletion':
                markdown += f"~~{diff['content']}~~\n"
            elif diff['type'] == 'addition':
                markdown += f"**{diff['content']}**\n"
            elif diff['type'] == 'context':
                markdown += f"{diff['content']}\n"

        return markdown

    @staticmethod
    def generate_change_summary(original: str, edited: str) -> Dict[str, Any]:
        """변경 요약"""
        changes = DiffGenerator.highlight_changes(original, edited)

        summary = {
            'total_changes': len(changes),
            'changes_by_type': {
                'changed': sum(1 for c in changes if c['type'] == 'changed'),
                'deleted': sum(1 for c in changes if c['type'] == 'deleted'),
                'added': sum(1 for c in changes if c['type'] == 'added'),
            },
            'similarity': DiffGenerator.calculate_similarity(original, edited),
            'original_length': len(original),
            'edited_length': len(edited),
            'length_change': len(edited) - len(original),
        }

        return summary
