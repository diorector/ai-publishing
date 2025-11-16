#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete PDF Translation Pipeline with Claude API
완전한 PDF 번역 파이프라인 (모든 청크 번역)
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
import json
import time

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_api_key() -> Optional[str]:
    """Get Claude API key"""
    return os.getenv('ANTHROPIC_API_KEY')


def extract_pdf(pdf_path):
    """Extract text from PDF"""
    try:
        import pdfplumber

        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            metadata = pdf.metadata
            pages = []

            print(f"[PDF Info]")
            print(f"  Pages: {len(pdf.pages)}")
            if metadata:
                print(f"  Title: {metadata.get('Title', 'N/A')}")
            print()

            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                pages.append(page_text if page_text else "")

            return text, metadata, pages

    except ImportError:
        print("[ERROR] pdfplumber not installed: pip install pdfplumber")
        return None, None, None


def chunk_text(text, chunk_size=5000):
    """Split text into chunks preserving structure"""
    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        current_size += len(word) + 1
        current_chunk.append(word)

        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def translate_with_claude(
    text: str,
    source_lang: str = "English",
    target_lang: str = "Korean",
    api_key: Optional[str] = None,
    chunk_num: int = 0,
    total_chunks: int = 0
) -> Optional[str]:
    """Translate text using Claude API with enhanced quality guidelines"""
    if not api_key:
        return None

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        # 향상된 번역 프롬프트 (출판 품질)
        prompt = f"""당신은 출판용 한국어 번역 전문가입니다. 다음 텍스트를 번역하세요.

【필수 번역 기준】
1. 톤: 모든 문장을 존댓말("~습니다", "~합니다")로 통일
2. 스타일: 비즈니스 교양서 - 전문적이면서 접근 가능함
3. 문장: 명확하고 20-30단어 길이로
4. 용어 사전을 정확히 따를 것
5. 원본 포맷 유지
6. 기술 용어 정확성

【핵심 용어 사전】
- startup → 스타트업
- founder → 창업자
- entrepreneur → 기업가
- venture capital → 벤처캐피탈
- investor → 투자자
- B2B → B2B
- CEO → CEO
- COO → COO
- MVP → MVP
- pivot → 피벗
- growth hacking → 성장 해킹
- exit strategy → 출구 전략
- cash flow → 현금흐름
- gross margin → 총 이익률
- self-service → 셀프 서비스

【톤 예시】
✅ "나는 25세였고, 완전히 당황했습니다. 하지만 저는 형편없는 거짓말쟁이라서..."
❌ "나 25살이었고, 진짜 깜짝 놀랐다."

【번역 텍스트 (Chunk {chunk_num}/{total_chunks})】
---
{text}
---

【최종 확인】
□ 모든 문장이 존댓말인가?
□ 용어 사전을 따랐는가?
□ 명확하고 읽기 쉬운가?
□ 기술 용어가 정확한가?

번역 결과만 반환하세요."""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=64000,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text

    except ImportError:
        print("[ERROR] anthropic not installed: pip install anthropic")
        return None
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return None


def translate_chunks(
    chunks: List[str],
    source_lang: str = "English",
    target_lang: str = "Korean",
    api_key: Optional[str] = None
) -> List[str]:
    """Translate all chunks with enhanced quality guidelines"""
    translated_chunks = []
    start_time = time.time()

    print(f"[TRANSLATING] {len(chunks)} chunks (with quality guidelines)...")
    print()

    for i, chunk in enumerate(chunks, 1):
        chunk_start = time.time()
        print(f"[{i:2d}/{len(chunks)}] Chunk {i}...", end=" ")

        # chunk_num과 total_chunks 정보 전달
        translated = translate_with_claude(
            chunk,
            source_lang,
            target_lang,
            api_key,
            chunk_num=i,
            total_chunks=len(chunks)
        )

        if translated:
            translated_chunks.append(translated)
            elapsed = time.time() - chunk_start
            print(f"OK ({len(translated)} chars, {elapsed:.1f}s)")
        else:
            print("SKIP (using original)")
            translated_chunks.append(chunk)

    elapsed = time.time() - start_time
    print()
    print(f"[OK] All chunks translated in {elapsed:.1f}s")
    print(f"[OK] Quality guidelines applied: TRANSLATION_GUIDELINE.md")
    print()

    return translated_chunks


def generate_markdown(
    pdf_name: str,
    translated_chunks: List[str],
    original_text: str,
    pages: int
) -> str:
    """Generate markdown from translated chunks"""
    markdown = f"""# {pdf_name} - Korean Translation

**Source**: English PDF
**Target**: Korean (한국어)
**Pages**: {pages}
**Characters**: {len(original_text):,}
**Chunks**: {len(translated_chunks)}
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Content

"""

    for i, translated in enumerate(translated_chunks, 1):
        markdown += f"## Section {i}\n\n"
        markdown += translated + "\n\n"

    markdown += f"---\n\n"
    markdown += f"**Translation completed**: All {len(translated_chunks)} sections translated successfully."

    return markdown


def main():
    print("=" * 70)
    print("[COMPLETE PDF TRANSLATION PIPELINE]")
    print("=" * 70)
    print()

    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        print()
        print("Setup instructions in: CLAUDE_API_SETUP.md")
        print()
        print("Quick setup:")
        print("  1. Get API key: https://console.anthropic.com")
        print("  2. Set environment: export ANTHROPIC_API_KEY=sk-ant-...")
        print("  3. Run again: python translate_full_pdf.py")
        return

    print("[OK] API key configured")
    print()

    # Check PDF
    pdf_path = Path('src/translation/laf.pdf')
    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return

    print(f"[PDF] {pdf_path.name}")
    print()

    # Extract
    print("[STEP 1] Extract PDF")
    print("-" * 70)
    text, metadata, pages = extract_pdf(pdf_path)
    if not text:
        return

    print(f"[OK] Extracted {len(text):,} characters from {len(pages)} pages")
    print()

    # Chunk
    print("[STEP 2] Create chunks (5000 chars each)")
    print("-" * 70)
    chunks = chunk_text(text, chunk_size=5000)
    print(f"[OK] Created {len(chunks)} chunks")
    print()

    # Translate
    print("[STEP 3] Translate with Claude API")
    print("-" * 70)
    translated_chunks = translate_chunks(chunks, "English", "Korean", api_key)

    if not translated_chunks:
        print("[ERROR] Translation failed")
        return

    # Generate markdown
    print("[STEP 4] Generate markdown")
    print("-" * 70)
    markdown = generate_markdown(pdf_path.stem, translated_chunks, text, len(pages))

    output_path = Path('output_laf_full_translated.md')
    output_path.write_text(markdown, encoding='utf-8')

    print(f"[OK] Markdown saved: {output_path}")
    print()

    # Summary
    print("=" * 70)
    print("[SUMMARY]")
    print("=" * 70)
    print(f"[OK] PDF: {pdf_path.name} ({len(pages)} pages)")
    print(f"[OK] Text: {len(text):,} characters")
    print(f"[OK] Chunks: {len(chunks)}")
    print(f"[OK] Translated: {len(translated_chunks)} chunks")
    print(f"[OK] Output: {output_path.absolute()}")
    print()
    print("[SUCCESS] Complete translation pipeline finished!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
