#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Structure Detection and Extraction
PDF 구조 감지 및 추출 (계층 정보 포함)
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class PDFStructureDetector:
    """PDF 구조 감지 및 계층 분석"""

    def __init__(self):
        self.heading_patterns = {
            'h1': [
                r'^(CHAPTER|PART)\s+(\d+|[IVX]+)',
                r'^[A-Z][A-Z\s]{5,}$',  # 모두 대문자 (3글자 이상)
            ],
            'h2': [
                r'^\d+\.\s+[A-Z]',  # "1. Introduction"
                r'^(Section|§)\s+\d+',
            ],
            'h3': [
                r'^\d+\.\d+\.\s+[A-Z]',  # "1.1. Subsection"
                r'^[A-Z][a-z]+\s+\d+',
            ],
            'h4': [
                r'^\d+\.\d+\.\d+\.\s+[A-Z]',  # "1.1.1. Sub-subsection"
            ],
        }

    def detect_heading_level(self, text: str) -> Optional[int]:
        """텍스트가 제목인지 감지하고 레벨 반환 (1-6, None=제목아님)"""
        text = text.strip()

        if not text or len(text) < 2:
            return None

        # h1 확인
        for pattern in self.heading_patterns['h1']:
            if re.match(pattern, text):
                return 1

        # h2 확인
        for pattern in self.heading_patterns['h2']:
            if re.match(pattern, text):
                return 2

        # h3 확인
        for pattern in self.heading_patterns['h3']:
            if re.match(pattern, text):
                return 3

        # h4 확인
        for pattern in self.heading_patterns['h4']:
            if re.match(pattern, text):
                return 4

        return None

    def is_metadata_line(self, text: str) -> bool:
        """메타데이터 라인인지 확인 (페이지 번호, 인쇄 정보 등)"""
        text = text.strip()

        # 필터링할 패턴들
        metadata_patterns = [
            r'^\d{4}.*\d{2}:\d{2}',  # 시간 정보
            r'\.indd',  # InDesign 파일 정보
            r'^\d+\s*$',  # 순수 숫자 (페이지 번호)
            r'^Page\s+\d+',  # Page number
            r'©.*\d{4}',  # 저작권
            r'ISBN',  # ISBN
            r'^[A-Za-z]+@',  # 이메일
        ]

        for pattern in metadata_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def extract_with_structure(self, pdf_path: str) -> Tuple[List[Dict], str]:
        """
        PDF에서 구조 정보와 함께 텍스트 추출
        Returns: (structured_content, raw_text)
        """
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                structured_content = []
                raw_text = ""
                page_num = 0

                print(f"[Analyzing] {len(pdf.pages)} pages...")
                print()

                for page_idx, page in enumerate(pdf.pages, 1):
                    page_num += 1
                    page_text = page.extract_text()

                    if not page_text:
                        continue

                    lines = page_text.split('\n')

                    for line in lines:
                        # 메타데이터 필터링
                        if self.is_metadata_line(line):
                            continue

                        # 빈 줄 스킵
                        if not line.strip():
                            continue

                        # 제목 레벨 감지
                        heading_level = self.detect_heading_level(line)

                        structured_content.append({
                            'text': line.strip(),
                            'level': heading_level,
                            'page': page_num,
                            'type': 'heading' if heading_level else 'paragraph'
                        })

                        raw_text += line.strip() + '\n'

                return structured_content, raw_text

        except ImportError:
            print("[ERROR] pdfplumber not installed: pip install pdfplumber")
            return [], ""


def generate_markdown_with_structure(
    pdf_name: str,
    structured_content: List[Dict],
    pages: int
) -> str:
    """
    구조 정보를 포함한 마크다운 생성
    """
    markdown = f"""# {pdf_name}

**Pages**: {pages}
**Content Sections**: {len([x for x in structured_content if x['type'] == 'heading'])}
**Paragraphs**: {len([x for x in structured_content if x['type'] == 'paragraph'])}

---

"""

    for item in structured_content:
        if item['type'] == 'heading':
            level = item['level']
            markdown += f"{'#' * level} {item['text']}\n\n"
        else:
            markdown += f"{item['text']}\n"

    return markdown


def analyze_structure(pdf_path: str) -> None:
    """PDF 구조 분석 및 통계"""
    print("=" * 70)
    print("[PDF STRUCTURE ANALYSIS]")
    print("=" * 70)
    print()

    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return

    print(f"[PDF] {pdf_path.name}")
    print()

    # 구조 감지
    detector = PDFStructureDetector()
    structured_content, raw_text = detector.extract_with_structure(str(pdf_path))

    if not structured_content:
        print("[ERROR] No content extracted")
        return

    # 통계
    print("[STATISTICS]")
    print("-" * 70)

    headings = [x for x in structured_content if x['type'] == 'heading']
    paragraphs = [x for x in structured_content if x['type'] == 'paragraph']

    print(f"Total items: {len(structured_content)}")
    print(f"Headings: {len(headings)}")
    print(f"Paragraphs: {len(paragraphs)}")
    print(f"Total characters: {len(raw_text):,}")
    print()

    # 제목 레벨 분포
    print("[HEADING DISTRIBUTION]")
    print("-" * 70)
    for level in range(1, 7):
        count = len([x for x in headings if x['level'] == level])
        if count > 0:
            print(f"H{level}: {count} headings")
    print()

    # 샘플 제목들
    print("[DETECTED HEADINGS (SAMPLES)]")
    print("-" * 70)
    for i, item in enumerate(headings[:10], 1):
        level = item['level']
        text = item['text'][:60]
        print(f"[H{level}] {text}")
    if len(headings) > 10:
        print(f"... and {len(headings) - 10} more headings")
    print()

    # 마크다운 생성
    print("[GENERATING MARKDOWN]")
    print("-" * 70)
    markdown = generate_markdown_with_structure(
        pdf_path.stem,
        structured_content,
        30  # 페이지 수 (임시)
    )

    output_path = Path('output_pdf_structure.md')
    output_path.write_text(markdown, encoding='utf-8')

    print(f"[OK] Markdown generated: {output_path}")
    print()

    # 결과 미리보기
    print("[PREVIEW] Generated Markdown (first 1000 chars)")
    print("-" * 70)
    print(markdown[:1000])
    print("...")
    print()
    print("[SUCCESS] Structure analysis complete!")


if __name__ == "__main__":
    try:
        analyze_structure('src/translation/laf.pdf')
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
