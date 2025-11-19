# 변경사항 비교 도구
# 원문과 편집본의 차이를 명확하게 표시

import difflib
from typing import List, Tuple
import re


class DiffGenerator:
    """편집 전후 비교 생성기"""
    
    def __init__(self):
        self.changes = []
    
    def generate_side_by_side(self, original: str, edited: str, context_lines: int = 2) -> str:
        """
        좌우 비교 형식으로 변경사항 표시
        
        Args:
            original: 원본 텍스트
            edited: 편집된 텍스트
            context_lines: 변경 전후 표시할 컨텍스트 라인 수
        
        Returns:
            좌우 비교 텍스트
        """
        original_lines = original.splitlines()
        edited_lines = edited.splitlines()
        
        diff = difflib.unified_diff(
            original_lines,
            edited_lines,
            lineterm='',
            n=context_lines
        )
        
        result = []
        result.append("=" * 80)
        result.append("편집 전후 비교")
        result.append("=" * 80)
        result.append("")
        
        for line in diff:
            if line.startswith('---') or line.startswith('+++'):
                continue
            elif line.startswith('@@'):
                result.append("")
                result.append("-" * 80)
                continue
            elif line.startswith('-'):
                result.append(f"❌ 원문: {line[1:]}")
            elif line.startswith('+'):
                result.append(f"✅ 편집: {line[1:]}")
            else:
                result.append(f"   {line}")
        
        return '\n'.join(result)
    
    def generate_inline_diff(self, original: str, edited: str) -> str:
        """
        인라인 형식으로 변경사항 표시
        
        Args:
            original: 원본 텍스트
            edited: 편집된 텍스트
        
        Returns:
            인라인 비교 텍스트
        """
        original_lines = original.splitlines()
        edited_lines = edited.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, edited_lines)
        
        result = []
        result.append("=" * 80)
        result.append("편집 변경사항")
        result.append("=" * 80)
        result.append("")
        
        change_count = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                change_count += 1
                result.append(f"\n[변경 {change_count}]")
                result.append("-" * 40)
                result.append("❌ 원문:")
                for line in original_lines[i1:i2]:
                    result.append(f"  {line}")
                result.append("")
                result.append("✅ 편집:")
                for line in edited_lines[j1:j2]:
                    result.append(f"  {line}")
                result.append("-" * 40)
            
            elif tag == 'delete':
                change_count += 1
                result.append(f"\n[삭제 {change_count}]")
                result.append("-" * 40)
                for line in original_lines[i1:i2]:
                    result.append(f"❌ {line}")
                result.append("-" * 40)
            
            elif tag == 'insert':
                change_count += 1
                result.append(f"\n[추가 {change_count}]")
                result.append("-" * 40)
                for line in edited_lines[j1:j2]:
                    result.append(f"✅ {line}")
                result.append("-" * 40)
        
        result.append(f"\n총 {change_count}개 변경사항")
        
        return '\n'.join(result)
    
    def generate_summary(self, original: str, edited: str) -> dict:
        """
        변경사항 요약 통계
        
        Args:
            original: 원본 텍스트
            edited: 편집된 텍스트
        
        Returns:
            통계 딕셔너리
        """
        original_lines = original.splitlines()
        edited_lines = edited.splitlines()
        
        matcher = difflib.SequenceMatcher(None, original_lines, edited_lines)
        
        stats = {
            'total_lines_original': len(original_lines),
            'total_lines_edited': len(edited_lines),
            'lines_changed': 0,
            'lines_added': 0,
            'lines_deleted': 0,
            'similarity_ratio': matcher.ratio(),
            'changes': []
        }
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                stats['lines_changed'] += max(i2 - i1, j2 - j1)
                stats['changes'].append({
                    'type': 'replace',
                    'original': '\n'.join(original_lines[i1:i2]),
                    'edited': '\n'.join(edited_lines[j1:j2])
                })
            elif tag == 'delete':
                stats['lines_deleted'] += i2 - i1
                stats['changes'].append({
                    'type': 'delete',
                    'original': '\n'.join(original_lines[i1:i2])
                })
            elif tag == 'insert':
                stats['lines_added'] += j2 - j1
                stats['changes'].append({
                    'type': 'insert',
                    'edited': '\n'.join(edited_lines[j1:j2])
                })
        
        return stats
    
    def highlight_word_changes(self, original: str, edited: str) -> List[Tuple[str, str]]:
        """
        단어 수준의 변경사항 하이라이트
        
        Args:
            original: 원본 문장
            edited: 편집된 문장
        
        Returns:
            (원문, 편집본) 튜플 리스트
        """
        original_words = original.split()
        edited_words = edited.split()
        
        matcher = difflib.SequenceMatcher(None, original_words, edited_words)
        
        changes = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                orig = ' '.join(original_words[i1:i2])
                edit = ' '.join(edited_words[j1:j2])
                changes.append((f"[{orig}]", f"[{edit}]"))
            elif tag == 'delete':
                orig = ' '.join(original_words[i1:i2])
                changes.append((f"[{orig}]", "[삭제]"))
            elif tag == 'insert':
                edit = ' '.join(edited_words[j1:j2])
                changes.append(("[추가]", f"[{edit}]"))
        
        return changes


def generate_markdown_diff(original: str, edited: str, title: str = "편집 비교") -> str:
    """
    마크다운 형식의 비교 문서 생성
    
    Args:
        original: 원본 텍스트
        edited: 편집된 텍스트
        title: 문서 제목
    
    Returns:
        마크다운 형식의 비교 문서
    """
    generator = DiffGenerator()
    stats = generator.generate_summary(original, edited)
    
    md = []
    md.append(f"# {title}\n")
    md.append("## 📊 변경 통계\n")
    md.append(f"- 원본 라인 수: {stats['total_lines_original']}")
    md.append(f"- 편집 라인 수: {stats['total_lines_edited']}")
    md.append(f"- 변경된 라인: {stats['lines_changed']}")
    md.append(f"- 추가된 라인: {stats['lines_added']}")
    md.append(f"- 삭제된 라인: {stats['lines_deleted']}")
    md.append(f"- 유사도: {stats['similarity_ratio']*100:.1f}%\n")
    
    md.append("## 📝 주요 변경사항\n")
    
    for i, change in enumerate(stats['changes'][:10], 1):  # 상위 10개만
        md.append(f"### 변경 {i}\n")
        
        if change['type'] == 'replace':
            md.append("**원문:**")
            md.append(f"```\n{change['original']}\n```\n")
            md.append("**편집:**")
            md.append(f"```\n{change['edited']}\n```\n")
        elif change['type'] == 'delete':
            md.append("**삭제:**")
            md.append(f"```\n{change['original']}\n```\n")
        elif change['type'] == 'insert':
            md.append("**추가:**")
            md.append(f"```\n{change['edited']}\n```\n")
    
    if len(stats['changes']) > 10:
        md.append(f"\n... 외 {len(stats['changes']) - 10}개 변경사항\n")
    
    return '\n'.join(md)
