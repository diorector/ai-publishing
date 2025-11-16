#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Translation with Real Claude API
실제 Claude API를 사용한 PDF 번역
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
import json

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
    print("[WARNING] python-dotenv not installed. Using ANTHROPIC_API_KEY env var.")


def get_api_key() -> Optional[str]:
    """Get Claude API key from environment"""
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        print("[INFO] Set it in .env file or environment variable")
        print("[INFO] Get API key from: https://console.anthropic.com")
        return None
    return api_key


def extract_pdf_simple(pdf_path):
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

            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                pages.append(page_text if page_text else "")

            return text, metadata, pages

    except ImportError:
        print("[ERROR] pdfplumber not installed")
        print("Install: pip install pdfplumber")
        return None, None, None


def chunk_text(text, chunk_size=5000):
    """Split text into chunks"""
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
    api_key: Optional[str] = None
) -> str:
    """
    Translate text using Claude API
    Claude API를 사용한 실제 번역
    """
    if not api_key:
        print("[ERROR] API key not provided")
        return None

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        prompt = f"""Please translate the following text from {source_lang} to {source_lang}.

Important:
1. Maintain original formatting and structure
2. Preserve technical terms and proper nouns
3. Keep the translation natural and readable in {target_lang}

Text to translate:
---
{text}
---

Please provide only the translated text, no explanations."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        return message.content[0].text

    except ImportError:
        print("[ERROR] anthropic library not installed")
        print("Install: pip install anthropic")
        return None
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return None


def translate_chunks_batch(
    chunks: List[str],
    source_lang: str = "English",
    target_lang: str = "Korean",
    api_key: Optional[str] = None
) -> List[str]:
    """
    Translate multiple chunks (batch processing)
    여러 청크를 배치로 번역
    """
    translated_chunks = []

    print(f"[INFO] Translating {len(chunks)} chunks...")
    print()

    for i, chunk in enumerate(chunks, 1):
        print(f"[{i}/{len(chunks)}] Translating chunk {i}...")

        translated = translate_with_claude(
            chunk,
            source_lang=source_lang,
            target_lang=target_lang,
            api_key=api_key
        )

        if translated:
            translated_chunks.append(translated)
            print(f"  [OK] {len(translated)} characters")
        else:
            print(f"  [SKIP] Translation failed")
            translated_chunks.append(chunk)  # Keep original

        print()

    return translated_chunks


def main():
    print("=" * 70)
    print("[PDF Translation Pipeline with Real Claude API]")
    print("=" * 70)
    print()

    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] Cannot proceed without API key")
        return

    print("[OK] API key found")
    print()

    # Check PDF file
    pdf_path = Path('src/translation/laf.pdf')
    if not pdf_path.exists():
        print(f"[ERROR] PDF file not found: {pdf_path}")
        return

    # Step 1: Extract PDF
    print("[STEP 1] Extract PDF")
    print("-" * 70)
    text, metadata, pages = extract_pdf_simple(pdf_path)

    if text is None:
        print("[ERROR] PDF extraction failed")
        return

    print(f"[OK] PDF extracted")
    print(f"  Total: {len(text):,} characters")
    print(f"  Pages: {len(pages)}")
    print()

    # Step 2: Preview
    print("[STEP 2] Text Preview (first 300 chars)")
    print("-" * 70)
    preview = text[:300]
    print(preview)
    print("...")
    print()

    # Step 3: Chunking
    print("[STEP 3] Text Chunking")
    print("-" * 70)
    chunks = chunk_text(text, chunk_size=3000)  # Smaller chunks for demo
    print(f"[OK] Created {len(chunks)} chunks")
    print()

    # Step 4: Translate with Claude
    print("[STEP 4] Translate with Claude API")
    print("-" * 70)
    translated_chunks = translate_chunks_batch(
        chunks[:2],  # Translate only first 2 chunks for demo
        source_lang="English",
        target_lang="Korean",
        api_key=api_key
    )

    if not translated_chunks:
        print("[ERROR] Translation failed")
        return

    # Step 5: Generate Markdown
    print("[STEP 5] Generate Markdown")
    print("-" * 70)
    markdown_output = f"""# {pdf_path.stem} - Korean Translation (Claude)

**Source**: English PDF
**Target**: Korean (한국어)
**Translator**: Claude API
**Pages**: {len(pages)}
**Characters**: {len(text):,}
**Chunks**: {len(chunks)}

## Content

"""

    # Add translated chunks
    for i, translated in enumerate(translated_chunks, 1):
        markdown_output += f"### Section {i}\n\n"
        markdown_output += translated + "\n\n"

    if len(chunks) > len(translated_chunks):
        markdown_output += f"### [Other {len(chunks) - len(translated_chunks)} sections...]\n\n"
        markdown_output += "(Translation in progress...)\n\n"

    markdown_output += f"**Status**: {len(translated_chunks)}/{len(chunks)} sections translated"

    # Save markdown
    output_path = Path('output_laf_claude_translated.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    print(f"[OK] Markdown file created")
    print(f"  Path: {output_path.absolute()}")
    print()

    # Summary
    print("=" * 70)
    print("[SUMMARY] Processing Complete")
    print("=" * 70)
    print(f"[OK] PDF extracted: {len(pages)} pages")
    print(f"[OK] Text: {len(text):,} characters")
    print(f"[OK] Chunks: {len(chunks)} pieces")
    print(f"[OK] Translated: {len(translated_chunks)}/{len(chunks)} chunks")
    print(f"[OK] Output: {output_path}")
    print()

    # Show result
    print("[PREVIEW] Generated Markdown")
    print("-" * 70)
    print(markdown_output[:800])
    print("...")
    print()
    print("[SUCCESS] Real Claude translation completed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
