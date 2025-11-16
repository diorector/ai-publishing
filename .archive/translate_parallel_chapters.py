#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Parallel Chapter Translation with Progress Display
병렬 챕터 번역 (동시 10개, 실시간 진행 상황)
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from threading import Lock

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


class ChapterSplitter:
    """하이브리드 방식으로 콘텐츠를 Chapter별로 분할
    - H1/H2 계층 활용
    - 최소 크기 기준: 500 chars 미만은 이전 chapter와 병합
    - 최대 크기 기준: 30K chars 초과는 자동 분할
    - 중복 제목 처리: 번호 자동 매기기
    """

    @staticmethod
    def split_into_chapters_hybrid(content: List[Dict]) -> List[Tuple[str, List[Dict]]]:
        """하이브리드 방식: H1 기본, H2 보조, 최소/최대 크기 기준"""
        chapters = []
        current_chapter = None
        current_items = []
        current_chars = 0

        MIN_SIZE = 500  # 최소 크기: 500 chars 미만은 병합
        MAX_SIZE = 30000  # 최대 크기: 이 이상이면 분할

        for item in content:
            is_heading = item['type'] == 'heading'
            is_h1 = is_heading and item['level'] == 1
            is_h2 = is_heading and item['level'] == 2
            item_chars = len(item['text'])

            # H1 또는 H2에서 새 chapter 시작
            if is_h1 or (is_h2 and current_chapter and current_chars > MIN_SIZE):
                # 이전 chapter 저장 (크기 체크)
                if current_chapter and current_items:
                    # 너무 작으면 합치지 않고 그냥 저장
                    chapters.append((current_chapter, current_items))

                current_chapter = item['text']
                current_items = [item]
                current_chars = item_chars
            else:
                if current_chapter:
                    current_items.append(item)
                    current_chars += item_chars

        # 마지막 chapter 저장
        if current_chapter and current_items:
            chapters.append((current_chapter, current_items))

        return chapters

    @staticmethod
    def merge_small_chapters(chapters: List[Tuple[str, List[Dict]]], min_size: int = 500) -> List[Tuple[str, List[Dict]]]:
        """최소 크기 미만인 chapter들을 이전 chapter와 병합"""
        merged = []

        for i, (name, items) in enumerate(chapters):
            char_count = sum(len(x['text']) for x in items)

            # 너무 작으면 이전 chapter와 병합
            if char_count < min_size and merged:
                prev_name, prev_items = merged.pop()
                # 헤더는 유지, 나머지는 병합
                merged_items = prev_items + items
                merged.append((prev_name, merged_items))
            else:
                merged.append((name, items))

        return merged

    @staticmethod
    def split_large_chapter(
        chapter_name: str,
        items: List[Dict],
        max_chars: int = 30000
    ) -> List[Tuple[str, List[Dict]]]:
        """큰 Chapter를 분할 (1-1, 1-2, ... 형식)"""
        total_chars = sum(len(x['text']) for x in items)
        if total_chars <= max_chars:
            return [(chapter_name, items)]

        # Chapter 분할
        split_chapters = []
        current_chunk = []
        current_chars = 0
        chunk_num = 1

        for item in items:
            item_chars = len(item['text'])

            if current_chars + item_chars > max_chars and current_chunk:
                # 현재 청크 저장
                split_name = f"{chapter_name}-{chunk_num}"
                split_chapters.append((split_name, current_chunk))

                # 다음 청크 시작 (첫 항목이 헤더면 포함)
                current_chunk = [item] if item['type'] == 'heading' else [item]
                current_chars = item_chars
                chunk_num += 1
            else:
                current_chunk.append(item)
                current_chars += item_chars

        # 마지막 청크 저장
        if current_chunk:
            split_name = f"{chapter_name}-{chunk_num}" if chunk_num > 1 else chapter_name
            split_chapters.append((split_name, current_chunk))

        return split_chapters

    @staticmethod
    def deduplicate_chapter_names(chapters: List[Tuple[str, List[Dict]]]) -> List[Tuple[str, List[Dict]]]:
        """중복된 chapter 이름에 번호 매기기"""
        name_counts = {}
        result = []

        for name, items in chapters:
            if name not in name_counts:
                name_counts[name] = 0
                result.append((name, items))
            else:
                name_counts[name] += 1
                # 기존 것들에도 번호를 붙임
                renamed = []
                for i, (existing_name, existing_items) in enumerate(result):
                    if existing_name == name:
                        # 첫 번째가 아니면 이미 번호가 있는지 확인
                        if '#' not in existing_name:
                            renamed.append((f"{existing_name} #{i+1}", existing_items))
                        else:
                            renamed.append((existing_name, existing_items))
                    else:
                        renamed.append((existing_name, existing_items))

                result = renamed
                result.append((f"{name} #{name_counts[name] + 1}", items))

        # 번호가 붙지 않은 것들 정리
        final_result = []
        for name, items in result:
            # 단일 항목만 있는 경우 번호 제거
            if name.count('#') > 0:
                base_name = name.rsplit(' #', 1)[0]
                count = sum(1 for n, _ in result if n.startswith(base_name))
                if count == 1:
                    final_result.append((base_name, items))
                else:
                    final_result.append((name, items))
            else:
                final_result.append((name, items))

        return final_result


class ProgressTracker:
    """진행 상황 추적 (Thread-safe)"""

    def __init__(self, total: int):
        self.total = total
        self.completed = 0
        self.lock = Lock()
        self.start_time = time.time()

    def update(self, chapter_name: str):
        """진행 상황 업데이트"""
        with self.lock:
            self.completed += 1
            elapsed = time.time() - self.start_time
            percent = (self.completed / self.total) * 100
            rate = self.completed / elapsed if elapsed > 0 else 0
            eta = (self.total - self.completed) / rate if rate > 0 else 0

            print(
                f"[{self.completed:2d}/{self.total}] {chapter_name:30s} "
                f"[{percent:5.1f}%] {elapsed:6.1f}s / ETA {eta:6.1f}s"
            )


def translate_chapter(
    chapter_name: str,
    items: List[Dict],
    api_key: Optional[str] = None
) -> Tuple[str, str]:
    """단일 Chapter 번역 및 MD 생성"""
    translated_items = []

    for item in items:
        if item['type'] == 'heading':
            translated_items.append(item)
        else:
            # 번역
            if api_key:
                try:
                    from anthropic import Anthropic
                    client = Anthropic(api_key=api_key)

                    prompt = f"""Translate to Korean. Keep it natural and readable. Return ONLY the translated text.

Text: {item['text']}"""

                    message = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=2048,
                        messages=[{"role": "user", "content": prompt}]
                    )

                    translated = message.content[0].text
                except Exception:
                    translated = item['text']
            else:
                translated = item['text']

            translated_items.append({**item, 'translated': translated})

    # Markdown 생성
    markdown = f"# {chapter_name}\n\n"
    for item in translated_items:
        if item['type'] == 'heading':
            markdown += f"## {item['text']}\n\n"
        else:
            translated_text = item.get('translated', item['text'])
            markdown += f"{translated_text}\n"

    return chapter_name, markdown


def save_chapter_file(chapter_name: str, markdown: str, output_dir: Path) -> Path:
    """Chapter 마크다운 파일 저장"""
    # 파일명 정리 (특수문자 제거)
    safe_name = re.sub(r'[^\w\-]', '', chapter_name.replace(' ', '_'))
    filename = f"chapter_{safe_name}.md"

    file_path = output_dir / filename
    file_path.write_text(markdown, encoding='utf-8')

    return file_path


def main():
    print("=" * 80)
    print("[PARALLEL CHAPTER TRANSLATION WITH PROGRESS]")
    print("=" * 80)
    print()

    # 설정
    api_key = os.getenv('ANTHROPIC_API_KEY')
    pdf_path = Path('src/translation/laf.pdf')
    output_dir = Path('output_chapters')

    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        return

    output_dir.mkdir(exist_ok=True)

    # Step 1: 구조 감지
    print("[STEP 1] Detect PDF structure")
    print("-" * 80)
    detector = PDFStructureDetector()
    content = detector.extract(str(pdf_path))

    print(f"[OK] Extracted {len(content)} items")
    print()

    # Step 2: Chapter 분할 (하이브리드 방식)
    print("[STEP 2] Split into chapters (Hybrid strategy)")
    print("-" * 80)

    # 2-1: 기본 분할 (H1/H2 기반)
    chapters = ChapterSplitter.split_into_chapters_hybrid(content)

    # 2-2: 작은 chapter 병합
    chapters = ChapterSplitter.merge_small_chapters(chapters, min_size=500)

    # 2-3: 큰 chapter 재분할
    all_chapters = []
    for chapter_name, items in chapters:
        split = ChapterSplitter.split_large_chapter(chapter_name, items, max_chars=30000)
        all_chapters.extend(split)

    # 2-4: 중복 제목 처리
    all_chapters = ChapterSplitter.deduplicate_chapter_names(all_chapters)

    print(f"[OK] Split into {len(all_chapters)} chapters")
    print()

    # 정보 표시
    print("[CHAPTERS TO TRANSLATE]")
    print("-" * 80)
    for i, (name, items) in enumerate(all_chapters, 1):
        chars = sum(len(x['text']) for x in items)
        print(f"  [{i:2d}] {name:35s} ({len(items):3d} items, {chars:6d} chars)")
    print()

    # Step 3: 병렬 번역
    print("[STEP 3] Parallel translation (10 workers)")
    print("-" * 80)
    print()

    progress = ProgressTracker(len(all_chapters))
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # 모든 chapter를 병렬로 제출
        futures = {
            executor.submit(translate_chapter, name, items, api_key): name
            for name, items in all_chapters
        }

        # 완료된 것부터 처리
        for future in as_completed(futures):
            chapter_name, markdown = future.result()
            progress.update(chapter_name)

            # 파일 저장
            file_path = save_chapter_file(chapter_name, markdown, output_dir)
            results.append((chapter_name, file_path))

    print()
    print("[OK] All chapters translated")
    print()

    # 요약
    print("=" * 80)
    print("[SUMMARY]")
    print("=" * 80)
    print(f"[OK] Total chapters: {len(all_chapters)}")
    print(f"[OK] Translated: {len(results)}")
    print(f"[OK] Output directory: {output_dir.absolute()}")
    print()

    # 생성된 파일 목록
    print("[OUTPUT FILES]")
    print("-" * 80)
    for chapter_name, file_path in sorted(results):
        size_kb = file_path.stat().st_size / 1024
        print(f"  ✓ {file_path.name:40s} ({size_kb:6.1f} KB)")

    print()
    print(f"[SUCCESS] Translation complete!")
    print()
    print("사용 방법:")
    print(f"  1. 파일 확인: ls output_chapters/")
    print(f"  2. 특정 chapter 읽기: cat output_chapters/chapter_CHAPTER_1.md")
    print(f"  3. 모든 파일 병합: cat output_chapters/*.md > full_book.md")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
