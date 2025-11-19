#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
품질 검증에서 발견된 이슈 자동 수정
- 포맷팅 이슈 (제목 공백, 연속 공백, 줄 끝 공백)
- 번역체 표현 자동 교정
- 기타 기계적 수정 가능한 항목

사용법:
  python auto_fix.py output_edited/growth_levers_kr/growth_levers_kr_edited.md
  python auto_fix.py output_edited/growth_levers_kr/growth_levers_kr_edited.md --backup
"""

import sys
import os
from pathlib import Path
import argparse
import re
from datetime import datetime

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class AutoFixer:
    """자동 수정기"""
    
    def __init__(self):
        self.fixes_applied = []
    
    def fix_document(self, content: str) -> str:
        """문서 자동 수정"""
        original_content = content
        
        # 1. 제목 포맷 수정
        content = self._fix_heading_format(content)
        
        # 2. 번역체 표현 수정
        content = self._fix_translation_style(content)
        
        # 3. 공백 정리
        content = self._fix_whitespace(content)
        
        # 4. 연속 빈 줄 정리
        content = self._fix_empty_lines(content)
        
        return content
    
    def _fix_heading_format(self, content: str) -> str:
        """제목 포맷 수정 (# 뒤 공백 추가)"""
        lines = content.split('\n')
        fixed_lines = []
        count = 0
        
        for line in lines:
            if line.startswith('#') and not line.startswith('# '):
                # #제목 → # 제목
                match = re.match(r'^(#+)(.+)$', line)
                if match:
                    hashes, title = match.groups()
                    fixed_line = f"{hashes} {title.lstrip()}"
                    fixed_lines.append(fixed_line)
                    count += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        if count > 0:
            self.fixes_applied.append(f"제목 포맷 수정: {count}개")
        
        return '\n'.join(fixed_lines)
    
    def _fix_translation_style(self, content: str) -> str:
        """번역체 표현 수정"""
        fixes = [
            (r'되어지다', '되다'),
            (r'되어진', '된'),
            (r'(\w+)할 것이다\.', r'\1할 것입니다.'),  # 존댓말로 통일
            (r'(\w+)할 것이다([,\s])', r'\1할 것입니다\2'),
            (r'에 대해서', '에 대해'),
            (r'에 있어서', '에서'),
        ]
        
        count = 0
        for pattern, replacement in fixes:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                count += content.count(pattern)
                content = new_content
        
        if count > 0:
            self.fixes_applied.append(f"번역체 표현 수정: {count}개")
        
        return content
    
    def _fix_whitespace(self, content: str) -> str:
        """공백 정리"""
        lines = content.split('\n')
        fixed_lines = []
        count = 0
        
        for line in lines:
            original = line
            
            # 1. 연속 공백 제거 (코드 블록 제외)
            if not line.startswith('    '):
                line = re.sub(r'  +', ' ', line)
            
            # 2. 줄 끝 공백 제거
            line = line.rstrip()
            
            if line != original:
                count += 1
            
            fixed_lines.append(line)
        
        if count > 0:
            self.fixes_applied.append(f"공백 정리: {count}개 라인")
        
        return '\n'.join(fixed_lines)
    
    def _fix_empty_lines(self, content: str) -> str:
        """연속 빈 줄 정리 (최대 2개까지만)"""
        # 3개 이상 연속 빈 줄 → 2개로
        count = 0
        while '\n\n\n\n' in content:
            content = content.replace('\n\n\n\n', '\n\n\n')
            count += 1
        
        if count > 0:
            self.fixes_applied.append(f"연속 빈 줄 정리: {count}개 위치")
        
        return content


def main():
    parser = argparse.ArgumentParser(
        description='품질 이슈 자동 수정',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python auto_fix.py output_edited/growth_levers_kr/growth_levers_kr_edited.md
  python auto_fix.py output_edited/growth_levers_kr/growth_levers_kr_edited.md --backup
        """
    )
    
    parser.add_argument('file', help='수정할 파일 경로')
    parser.add_argument('--backup', action='store_true',
                       help='원본 백업 생성')
    
    args = parser.parse_args()
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {file_path}")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("🔧 자동 수정 시스템")
    print("=" * 80)
    print(f"\n파일: {file_path.name}")
    
    # 원본 읽기
    original_content = file_path.read_text(encoding='utf-8')
    original_size = len(original_content)
    
    print(f"원본 크기: {original_size:,} 자")
    
    # 백업
    if args.backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = file_path.with_suffix(f'.backup_{timestamp}.md')
        backup_path.write_text(original_content, encoding='utf-8')
        print(f"백업 생성: {backup_path.name}")
    
    # 자동 수정 실행
    print("\n🔧 자동 수정 중...")
    fixer = AutoFixer()
    fixed_content = fixer.fix_document(original_content)
    
    # 저장
    file_path.write_text(fixed_content, encoding='utf-8')
    fixed_size = len(fixed_content)
    
    print("\n✅ 수정 완료!")
    print(f"수정 후 크기: {fixed_size:,} 자")
    print(f"크기 변화: {fixed_size - original_size:+,} 자")
    
    # 적용된 수정 내역
    print("\n📋 적용된 수정:")
    if fixer.fixes_applied:
        for fix in fixer.fixes_applied:
            print(f"  ✓ {fix}")
    else:
        print("  (수정 사항 없음)")
    
    print("\n" + "=" * 80)
    print("다음 단계: 품질 검증")
    print("=" * 80)
    print(f"\npython quality_check.py {file_path}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
