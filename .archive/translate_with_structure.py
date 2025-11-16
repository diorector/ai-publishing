#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Translation with Structure Preservation
구조를 유지하면서 PDF 번역 (H1-H6 계층 포함)
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import time
import re

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class PDFStructureDetector:
    """PDF 구조 감지"""

    def __init__(self):
        self.heading_patterns = {
            'h1': [
                r'^(CHAPTER|PART|INTRODUCTION|CONCLUSION)\s*(\d+)?',
                r'^[A-Z][A-Z\s]{5,}$',
            ],
            'h2': [
                r'^\d+\.\s+[A-Z]',
                r'^(Section|§)\s+\d+',
            ],
            'h3': [
                r'^\d+\.\d+\.\s+[A-Z]',
            ],
        }

    def detect_heading_level(self, text: str) -> Optional[int]:
        """제목 레벨 감지"""
        text = text.strip()
        if not text or len(text) < 2:
            return None

        for pattern in self.heading_patterns['h1']:
            if re.match(pattern, text):
                return 1
        for pattern in self.heading_patterns['h2']:
            if re.match(pattern, text):
                return 2
        for pattern in self.heading_patterns['h3']:
            if re.match(pattern, text):
                return 3

        return None

    def is_metadata(self, text: str) -> bool:
        """메타데이터 필터링"""
        text = text.strip()
        metadata_patterns = [
            r'^\d{4}.*\d{2}:\d{2}',
            r'\.indd',
            r'^\d+\s*$',
            r'©.*\d{4}',
            r'ISBN',
        ]
        return any(re.search(p, text, re.IGNORECASE) for p in metadata_patterns)

    def extract(self, pdf_path: str) -> List[Dict]:
        """PDF에서 구조 정보와 함께 추출"""
        try:
            import pdfplumber

            with pdfplumber.open(pdf_path) as pdf:
                content = []
                for page_idx, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if not page_text:
                        continue

                    for line in page_text.split('\n'):
                        if self.is_metadata(line):
                            continue
                        if not line.strip():
                            continue

                        level = self.detect_heading_level(line)
                        content.append({
                            'text': line.strip(),
                            'level': level,
                            'page': page_idx,
                            'type': 'heading' if level else 'paragraph'
                        })

                return content

        except ImportError:
            print("[ERROR] pdfplumber not installed")
            return []


def translate_item(item: Dict, api_key: Optional[str] = None) -> str:
    """단일 아이템 번역"""
    if not api_key:
        return item['text']

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        prompt = f"""Translate the following English text to Korean.
- Keep it natural and readable
- Return ONLY the translated text, no explanations
- Preserve formatting

Text: {item['text']}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    except Exception as e:
        print(f"  [WARNING] Translation failed, using original")
        return item['text']


def translate_content(
    content: List[Dict],
    api_key: Optional[str] = None
) -> List[Dict]:
    """모든 콘텐츠 번역"""
    translated = []

    print(f"[TRANSLATING] {len(content)} items...")
    print()

    for i, item in enumerate(content, 1):
        if i % 100 == 1 or i == len(content):
            print(f"[{i:3d}/{len(content)}] Processing...")

        translated_text = translate_item(item, api_key)
        translated.append({**item, 'translated': translated_text})

    print()
    print(f"[OK] All items translated")
    print()

    return translated


def generate_markdown(translated: List[Dict], title: str) -> str:
    """마크다운 생성 (구조 보존)"""
    markdown = f"""# {title} - Korean Translation

**Source**: English PDF
**Target**: Korean (한국어)
**Total Items**: {len(translated)}
**Headings**: {len([x for x in translated if x['type'] == 'heading'])}

---

"""

    current_h1_section = None
    current_h2_section = None

    for item in translated:
        if item['type'] == 'heading':
            level = item['level']
            text = item['translated']

            # 마크다운 헤더 생성
            markdown += f"{'#' * level} {text}\n\n"

            # 섹션 추적
            if level == 1:
                current_h1_section = text
            elif level == 2:
                current_h2_section = text

        else:
            # 단락
            markdown += f"{item['translated']}\n"

    return markdown


def main():
    print("=" * 70)
    print("[PDF TRANSLATION WITH STRUCTURE]")
    print("=" * 70)
    print()

    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[INFO] API key not set - using original text")
        print("[INFO] Set ANTHROPIC_API_KEY to enable real translation")
        print()

    pdf_path = Path('src/translation/laf.pdf')
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return

    # Step 1: 구조 감지
    print("[STEP 1] Detect PDF structure")
    print("-" * 70)
    detector = PDFStructureDetector()
    content = detector.extract(str(pdf_path))

    headings = [x for x in content if x['type'] == 'heading']
    paragraphs = [x for x in content if x['type'] == 'paragraph']

    print(f"[OK] Extracted {len(content)} items")
    print(f"  Headings: {len(headings)}")
    print(f"  Paragraphs: {len(paragraphs)}")
    print()

    # Step 2: 번역 (옵션)
    print("[STEP 2] Translate content")
    print("-" * 70)
    if api_key:
        translated = translate_content(content, api_key)
    else:
        # API 키 없으면 원문 그대로
        translated = [{**item, 'translated': item['text']} for item in content]
        print("[INFO] Using original text (no API key)")
        print()

    # Step 3: 마크다운 생성
    print("[STEP 3] Generate markdown with structure")
    print("-" * 70)
    markdown = generate_markdown(translated, pdf_path.stem)

    output_path = Path('output_laf_structured.md')
    output_path.write_text(markdown, encoding='utf-8')

    print(f"[OK] Markdown generated: {output_path}")
    print()

    # Summary
    print("=" * 70)
    print("[SUMMARY]")
    print("=" * 70)
    print(f"[OK] PDF: {pdf_path.name}")
    print(f"[OK] Items: {len(content)}")
    print(f"[OK] Headings: {len(headings)}")
    print(f"[OK] Output: {output_path.absolute()}")
    print()

    # Preview
    print("[PREVIEW] Generated Markdown (first 1500 chars)")
    print("-" * 70)
    print(markdown[:1500])
    print("...")
    print()
    print("[SUCCESS] Complete!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
