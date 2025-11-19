#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DOCX 파일을 마크다운으로 변환하는 스크립트

사용법:
  python convert_docx_to_md.py input/growth_levers_kr.docx
  python convert_docx_to_md.py input/growth_levers_kr.docx --output custom_output.md
"""

import sys
import os
from pathlib import Path
import argparse

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

try:
    from docx import Document
except ImportError:
    print("❌ python-docx 패키지가 필요합니다.")
    print("   설치: pip install python-docx")
    sys.exit(1)


def convert_docx_to_markdown(docx_path: Path) -> str:
    """DOCX 파일을 마크다운으로 변환"""
    doc = Document(docx_path)
    markdown_lines = []
    
    for para in doc.paragraphs:
        text = para.text.strip()
        
        if not text:
            markdown_lines.append("")
            continue
        
        # 스타일 기반 변환
        style_name = para.style.name.lower()
        
        if 'heading 1' in style_name or 'title' in style_name:
            markdown_lines.append(f"# {text}")
        elif 'heading 2' in style_name:
            markdown_lines.append(f"## {text}")
        elif 'heading 3' in style_name:
            markdown_lines.append(f"### {text}")
        elif 'heading 4' in style_name:
            markdown_lines.append(f"#### {text}")
        elif 'heading 5' in style_name:
            markdown_lines.append(f"##### {text}")
        elif 'heading 6' in style_name:
            markdown_lines.append(f"###### {text}")
        else:
            # 일반 텍스트
            markdown_lines.append(text)
        
        markdown_lines.append("")
    
    return "\n".join(markdown_lines)


def main():
    parser = argparse.ArgumentParser(
        description='DOCX 파일을 마크다운으로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python convert_docx_to_md.py input/growth_levers_kr.docx
  python convert_docx_to_md.py input/growth_levers_kr.docx --output custom.md
        """
    )
    
    parser.add_argument('file', help='변환할 DOCX 파일 경로')
    parser.add_argument('--output', '-o', help='출력 마크다운 파일 경로 (선택)')
    
    args = parser.parse_args()
    
    # 입력 파일 확인
    input_path = Path(args.file)
    if not input_path.exists():
        print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
        sys.exit(1)
    
    # 출력 파일 경로 결정
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = Path('output') / f"{input_path.stem}.md"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 80)
    print("📄 DOCX → 마크다운 변환")
    print("=" * 80)
    print(f"\n입력: {input_path}")
    print(f"출력: {output_path}")
    
    try:
        # 변환 실행
        print("\n🔄 변환 중...")
        markdown_content = convert_docx_to_markdown(input_path)
        
        # 저장
        output_path.write_text(markdown_content, encoding='utf-8')
        
        file_size = output_path.stat().st_size
        line_count = len(markdown_content.split('\n'))
        
        print(f"\n✅ 변환 완료!")
        print(f"   크기: {file_size:,} bytes")
        print(f"   라인: {line_count:,}개")
        print(f"\n📁 저장 위치: {output_path.absolute()}")
        
        print("\n" + "=" * 80)
        print("다음 단계: 편집하기")
        print("=" * 80)
        print(f"\npython edit_document.py {output_path}")
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"\n❌ 변환 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  사용자에 의해 중단되었습니다.")
        sys.exit(1)
