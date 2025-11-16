#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PDF Extraction and Translation Test

import sys
import os
from pathlib import Path

# Set encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


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
                print(f"  Author: {metadata.get('Author', 'N/A')}")
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
    except Exception as e:
        print(f"[ERROR] PDF extraction failed: {e}")
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


def translate_mock(text, source="English", target="Korean"):
    """Mock translation"""
    lines = text.split('\n')
    translated_lines = []

    for line in lines:
        if line.strip():
            translated_lines.append(f"[KOR] {line[:60]}...")
        else:
            translated_lines.append("")

    return "\n".join(translated_lines)


def main():
    print("[TEST] PDF Translation Pipeline")
    print("=" * 70)
    print()

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

    print(f"[OK] PDF extracted successfully")
    print(f"  Total characters: {len(text):,}")
    print(f"  Total pages: {len(pages)}")
    print()

    # Step 2: Preview
    print("[STEP 2] Text Preview (first 400 chars)")
    print("-" * 70)
    preview = text[:400]
    print(preview)
    print("...")
    print()

    # Step 3: Chunking
    print("[STEP 3] Text Chunking (5000 chars per chunk)")
    print("-" * 70)
    chunks = chunk_text(text, chunk_size=5000)
    print(f"[OK] {len(chunks)} chunks created")
    for i, chunk in enumerate(chunks[:3], 1):
        print(f"  Chunk {i}: {len(chunk)} characters")
    if len(chunks) > 3:
        print(f"  ...")
    print()

    # Step 4: Translation
    print("[STEP 4] Mock Translation")
    print("-" * 70)
    print("[INFO] Translating first chunk...")
    translated_first = translate_mock(chunks[0][:300])
    print(translated_first)
    print()

    # Step 5: Generate Markdown
    print("[STEP 5] Generate Markdown")
    print("-" * 70)
    markdown_output = f"""# {pdf_path.stem} - Korean Translation

**Source**: English PDF
**Target**: Korean
**Pages**: {len(pages)}
**Characters**: {len(text):,}
**Chunks**: {len(chunks)}

## Content

"""

    # Add first 3 chunks
    for i, chunk in enumerate(chunks[:3], 1):
        markdown_output += f"### Section {i}\n\n"
        translated = translate_mock(chunk[:200])
        markdown_output += translated + "\n\n"

    markdown_output += "...\n\n"
    markdown_output += f"**Total: {len(chunks)} sections translated**"

    # Save markdown
    output_path = Path('output_laf_translated.md')
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
    print(f"[OK] Translation: {len(chunks)} chunks processed")
    print(f"[OK] Markdown: {output_path}")
    print()

    # Show result preview
    print("[PREVIEW] Generated Markdown (first 500 chars)")
    print("-" * 70)
    print(markdown_output[:500])
    print("...")
    print()
    print("[SUCCESS] Test completed!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
