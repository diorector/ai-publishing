#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Document Editing Pipeline
완전한 문서 편집 파이프라인 (교정 + 교열 + 윤문)

파일 경로를 지정하면 편집 수행:
  python edit_full_documents.py output/output_laf_translated.md
  python edit_full_documents.py output/output_saf_full_translated.md
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict
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

from src.editing.edit_orchestrator import EditOrchestrator


def print_header():
    """헤더 출력"""
    print("\n" + "=" * 80)
    print("📝 문서 편집 파이프라인 (Document Editing Pipeline)")
    print("=" * 80)
    print("2025년 11월 기준 한국어 맞춤법, 팩트 검증, 문장 개선")
    print("=" * 80 + "\n")


def print_usage():
    """사용법 출력"""
    print("사용법:")
    print("  python edit_full_documents.py <파일경로>")
    print("\n예시:")
    print("  python edit_full_documents.py output/output_laf_translated.md")
    print("  python edit_full_documents.py output/translated_file.md")


def check_file_exists(file_path: str) -> bool:
    """파일 존재 확인"""
    if not Path(file_path).exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다")
        print(f"   경로: {file_path}")
        return False
    return True


def edit_document(file_path: str) -> Optional[Dict]:
    """
    문서 편집 수행

    Args:
        file_path: 편집할 파일 경로

    Returns:
        편집 결과 또는 None (실패 시)
    """
    # 파일 경로 정규화
    file_path = str(Path(file_path).resolve())

    # 파일 존재 확인
    if not check_file_exists(file_path):
        return None

    # 파일명 추출
    file_name = Path(file_path).name
    file_stem = Path(file_path).stem

    # 출력 파일 경로 자동 생성
    output_file = file_path.replace('.md', '_edited.md')
    report_file = file_path.replace('.md', '_editing_report.json')

    print(f"{'=' * 80}")
    print(f"📄 {file_name}")
    print(f"{'=' * 80}")

    # 오케스트레이터 초기화
    orchestrator = EditOrchestrator()

    # 1. 문서 로드
    print(f"\n📥 파일 로드")
    print(f"   입력: {file_path}")
    try:
        doc = orchestrator.load_document(
            file_path=file_path,
            domain='general',
            target_audience='general'
        )
        word_count = len(doc.content.split())
        chapter_count = len(doc.structure.chapters) if doc.structure.chapters else 0
        print(f"✅ 로드 완료")
        print(f"   - 단어 수: {word_count:,}개")
        print(f"   - 장 수: {chapter_count}개")
    except Exception as e:
        print(f"❌ 로드 실패: {e}")
        return None

    # 2. 편집 수행
    print(f"\n🔄 편집 파이프라인 시작...")
    print("-" * 80)

    start_time = time.time()

    def progress_callback(stage: str, progress: float):
        """진행률 추적 콜백"""
        stages = {
            'analysis': '📊 문서 분석',
            'proofreading': '✏️  교정',
            'fact_checking': '🔍 교열',
            'copywriting': '✨ 윤문',
            'integration': '🔗 통합'
        }
        stage_name = stages.get(stage, stage)
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"{stage_name:20} | {bar} | {progress:3.0f}%", end='\r', flush=True)

    try:
        result = orchestrator.edit_comprehensive(
            doc,
            progress_callback=progress_callback
        )
        elapsed_time = time.time() - start_time
        print("\n" + "-" * 80)
        print(f"✅ 편집 완료!")
    except Exception as e:
        print(f"\n❌ 편집 실패: {e}")
        return None

    # 3. 결과 분석
    print(f"\n📈 편집 결과")
    print("-" * 80)

    statistics = result['statistics']
    quality_metrics = result['quality_metrics']

    print(f"\n📊 변경사항:")
    print(f"   교정: {statistics.get('proofreading_changes', 0):,}개")
    print(f"   교열: {statistics.get('fact_checks', 0):,}개")
    print(f"   윤문: {statistics.get('copywriting_changes', 0):,}개")
    print(f"   총합: {len(result['changes']):,}개")

    print(f"\n🎯 품질 점수:")
    quality_score = result['quality_score']
    print(f"   최종: {quality_score:.1f}/100", end='')
    if quality_score >= 90:
        print(" ⭐⭐⭐⭐⭐")
    elif quality_score >= 80:
        print(" ⭐⭐⭐⭐")
    elif quality_score >= 70:
        print(" ⭐⭐⭐")
    else:
        print(" ⭐⭐")

    print(f"   교정: {quality_metrics.get('proofreading_quality', 0):.1f}/100")
    print(f"   교열: {quality_metrics.get('fact_checking_quality', 0):.1f}/100")
    print(f"   윤문: {quality_metrics.get('copywriting_quality', 0):.1f}/100")

    print(f"\n⏱️  처리 시간: {elapsed_time:.2f}초")

    # 4. 변경사항 샘플
    if result['changes']:
        print(f"\n📝 변경사항 샘플 (처음 3개):")
        print("-" * 80)
        for i, change in enumerate(result['changes'][:3], 1):
            print(f"\n{i}. [{change['type'].upper()}]")
            original_preview = change['original'][:50].replace('\n', ' ')
            fixed_preview = change['fixed'][:50].replace('\n', ' ')
            print(f"   원: {original_preview}...")
            print(f"   수: {fixed_preview}...")

    # 5. 편집본 저장
    print(f"\n{'=' * 80}")
    print(f"💾 파일 저장")
    print(f"{'=' * 80}")

    try:
        edited_content = result['edited_document'].content
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(edited_content)
        file_size = Path(output_file).stat().st_size
        print(f"\n✅ 편집본 저장")
        print(f"   경로: {output_file}")
        print(f"   크기: {file_size:,} bytes")
    except Exception as e:
        print(f"\n❌ 저장 실패: {e}")
        return None

    # 6. 리포트 저장
    print(f"\n📊 리포트 저장...")

    try:
        report = {
            'file': {
                'input': file_path,
                'output': output_file,
                'word_count': word_count,
                'chapter_count': chapter_count
            },
            'results': {
                'quality_score': quality_score,
                'quality_metrics': quality_metrics,
                'statistics': statistics,
                'processing_time': elapsed_time,
                'total_changes': len(result['changes'])
            }
        }

        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 리포트 저장: {report_file}")
    except Exception as e:
        print(f"⚠️  리포트 저장 실패: {e}")

    return {
        'input_file': file_path,
        'output_file': output_file,
        'quality_score': quality_score,
        'changes_count': len(result['changes']),
        'processing_time': elapsed_time
    }


def main():
    """메인 함수"""
    print_header()

    # 인자 처리
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    file_path = sys.argv[1]

    # 편집 수행
    result = edit_document(file_path)

    if result:
        print(f"\n{'=' * 80}")
        print("✨ 편집 완료!")
        print(f"{'=' * 80}")
        print(f"\n입력 파일: {result['input_file']}")
        print(f"출력 파일: {result['output_file']}")
        print(f"품질 점수: {result['quality_score']:.1f}/100")
        print(f"변경사항: {result['changes_count']:,}개")
        print(f"처리 시간: {result['processing_time']:.2f}초")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
