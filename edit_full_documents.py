#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Document Editing Pipeline
완전한 문서 편집 파이프라인 (교정 + 교열 + 윤문)

번역 도구(translate_full_pdf.py)와 동일한 사용 방식:
- python edit_full_documents.py laf      # LAF 문서만 편집
- python edit_full_documents.py saf      # SAF 문서만 편집
- python edit_full_documents.py soshr    # SOSHR 문서만 편집
- python edit_full_documents.py cs       # CS 문서만 편집
- python edit_full_documents.py all      # 모든 문서 순차 편집
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
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


# 문서 설정: 파일경로, 도메인, 대상독자
DOCUMENTS_CONFIG = {
    'laf': {
        'input_file': 'output/output_laf_translated.md',
        'output_file': 'output/output_laf_translated_edited.md',
        'report_file': 'output/laf_editing_report.json',
        'domain': 'legal',
        'target_audience': 'practitioners',
        'title': 'LAF (Law and Frameworks)',
        'description': '법률 및 프레임워크 - 법학 전문가 대상'
    },
    'saf': {
        'input_file': 'output/output_saf_full_translated.md',
        'output_file': 'output/output_saf_full_translated_edited.md',
        'report_file': 'output/saf_editing_report.json',
        'domain': 'finance',
        'target_audience': 'general',
        'title': 'SAF (Standards and Frameworks)',
        'description': '기준 및 프레임워크 - 일반 독자 대상'
    },
    'soshr': {
        'input_file': 'output/output_soshr_full_translated.md',
        'output_file': 'output/output_soshr_full_translated_edited.md',
        'report_file': 'output/soshr_editing_report.json',
        'domain': 'general',
        'target_audience': 'general',
        'title': 'SOSHR (Social and Human Resources)',
        'description': '사회 및 인사 - 일반 대중 대상'
    },
    'cs': {
        'input_file': 'output/output_cs_full_translated.md',
        'output_file': 'output/output_cs_full_translated_edited.md',
        'report_file': 'output/cs_editing_report.json',
        'domain': 'technology',
        'target_audience': 'developers',
        'title': 'CS (Computer Science)',
        'description': '컴퓨터 과학 - 개발자/기술자 대상'
    }
}


def print_header():
    """헤더 출력"""
    print("\n" + "=" * 80)
    print("📝 포괄적 문서 편집 파이프라인 (Comprehensive Document Editing Pipeline)")
    print("=" * 80)
    print("2025년 11월 기준 최신 한국어 규칙 적용")
    print("교정(Proofreading) + 교열(Fact-checking) + 윤문(Copywriting)")
    print("=" * 80 + "\n")


def print_usage():
    """사용법 출력"""
    print("사용법 (Usage):")
    print("  python edit_full_documents.py [문서명]")
    print("\n가능한 문서명:")
    print("  laf      - LAF (법률) 문서")
    print("  saf      - SAF (기준) 문서")
    print("  soshr    - SOSHR (사회) 문서")
    print("  cs       - CS (컴퓨터과학) 문서")
    print("  all      - 모든 문서 순차 편집")
    print("\n예시:")
    print("  python edit_full_documents.py laf")
    print("  python edit_full_documents.py all")


def check_file_exists(file_path: str) -> bool:
    """파일 존재 확인"""
    if not Path(file_path).exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다 - {file_path}")
        return False
    return True


def edit_document(doc_key: str, config: Dict) -> Optional[Dict]:
    """
    단일 문서 편집 수행

    Args:
        doc_key: 문서 키 (laf, saf, soshr, cs)
        config: 문서 설정 딕셔너리

    Returns:
        편집 결과 또는 None (실패 시)
    """
    print(f"\n{'=' * 80}")
    print(f"📄 {config['title']}")
    print(f"   {config['description']}")
    print(f"{'=' * 80}")

    input_file = config['input_file']
    output_file = config['output_file']
    report_file = config['report_file']

    # 파일 존재 확인
    if not check_file_exists(input_file):
        return None

    # 오케스트레이터 초기화
    orchestrator = EditOrchestrator()

    # 1. 문서 로드
    print(f"\n📥 파일 로드: {input_file}")
    try:
        doc = orchestrator.load_document(
            file_path=input_file,
            domain=config['domain'],
            target_audience=config['target_audience']
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
    stage_times = {}

    def progress_callback(stage: str, progress: float):
        """진행률 추적 콜백"""
        stages = {
            'analysis': '📊 문서 분석',
            'proofreading': '✏️  교정 (띄어쓰기, 맞춤법)',
            'fact_checking': '🔍 교열 (팩트 검증)',
            'copywriting': '✨ 윤문 (문장 개선)',
            'integration': '🔗 최종 통합'
        }
        stage_name = stages.get(stage, stage)
        bar_length = 40
        filled = int(bar_length * progress / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"{stage_name:25} | {bar} | {progress:3.0f}%", end='\r', flush=True)

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
    print(f"\n📈 편집 결과 분석")
    print("-" * 80)

    statistics = result['statistics']
    quality_metrics = result['quality_metrics']

    print(f"\n📊 편집 통계:")
    print(f"   교정 변경사항: {statistics.get('proofreading_changes', 0):,}개")
    print(f"   교열 팩트 확인: {statistics.get('fact_checks', 0):,}개")
    print(f"   윤문 개선사항: {statistics.get('copywriting_changes', 0):,}개")
    print(f"   총 변경사항: {len(result['changes']):,}개")

    print(f"\n🎯 품질 점수:")
    quality_score = result['quality_score']
    print(f"   최종 품질 점수: {quality_score:.1f}/100점", end='')
    if quality_score >= 90:
        print(" ⭐⭐⭐⭐⭐")
    elif quality_score >= 80:
        print(" ⭐⭐⭐⭐")
    elif quality_score >= 70:
        print(" ⭐⭐⭐")
    else:
        print(" ⭐⭐")

    print(f"   교정 점수: {quality_metrics.get('proofreading_quality', 0):.1f}/100")
    print(f"   교열 점수: {quality_metrics.get('fact_checking_quality', 0):.1f}/100")
    print(f"   윤문 점수: {quality_metrics.get('copywriting_quality', 0):.1f}/100")

    print(f"\n⏱️  처리 시간: {elapsed_time:.2f}초")

    # 4. 변경사항 샘플
    if result['changes']:
        print(f"\n📝 변경사항 샘플 (처음 3개):")
        print("-" * 80)
        for i, change in enumerate(result['changes'][:3], 1):
            print(f"\n{i}. [{change['type'].upper()}]")
            original_preview = change['original'][:50].replace('\n', ' ')
            fixed_preview = change['fixed'][:50].replace('\n', ' ')
            print(f"   원문: {original_preview}...")
            print(f"   수정: {fixed_preview}...")
            if change.get('reason'):
                print(f"   이유: {change['reason']}")

    # 5. 편집본 저장
    print(f"\n{'=' * 80}")
    print(f"💾 편집본 저장")
    print(f"{'=' * 80}")

    try:
        edited_content = result['edited_document'].content
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(edited_content)
        file_size = Path(output_file).stat().st_size
        print(f"\n✅ 편집본 저장 완료: {output_file}")
        print(f"   파일 크기: {file_size:,} bytes")
    except Exception as e:
        print(f"\n❌ 파일 저장 실패: {e}")
        return None

    # 6. 상세 리포트 저장
    print(f"\n📊 상세 리포트 저장...")

    try:
        report = {
            'document': {
                'key': doc_key,
                'title': config['title'],
                'domain': config['domain'],
                'target_audience': config['target_audience'],
                'word_count': word_count,
                'chapter_count': chapter_count
            },
            'editing_results': {
                'quality_score': quality_score,
                'quality_metrics': quality_metrics,
                'statistics': statistics,
                'processing_time': elapsed_time,
                'total_changes': len(result['changes'])
            },
            'changes_by_type': {
                'proofreading': len([c for c in result['changes'] if c['type'] in ['spacing', 'grammar']]),
                'fact_checking': len([c for c in result['changes'] if c['type'] == 'outdated_info']),
                'copywriting': len([c for c in result['changes'] if c['type'] == 'sentence_improvement'])
            }
        }

        Path(report_file).parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ 리포트 저장: {report_file}")
    except Exception as e:
        print(f"⚠️  리포트 저장 실패: {e}")

    return {
        'doc_key': doc_key,
        'title': config['title'],
        'quality_score': quality_score,
        'changes_count': len(result['changes']),
        'processing_time': elapsed_time,
        'output_file': output_file
    }


def main():
    """메인 함수"""
    print_header()

    # 인자 처리
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    doc_target = sys.argv[1].lower()

    # 편집할 문서 결정
    if doc_target == 'all':
        documents_to_edit = ['laf', 'saf', 'soshr', 'cs']
    elif doc_target in DOCUMENTS_CONFIG:
        documents_to_edit = [doc_target]
    else:
        print(f"❌ 알 수 없는 문서: {doc_target}")
        print()
        print_usage()
        sys.exit(1)

    # 편집 수행
    results = []
    for doc_key in documents_to_edit:
        config = DOCUMENTS_CONFIG[doc_key]
        result = edit_document(doc_key, config)
        if result:
            results.append(result)

    # 최종 요약
    if results:
        print(f"\n{'=' * 80}")
        print("📋 편집 완료 요약")
        print(f"{'=' * 80}\n")

        total_time = sum(r['processing_time'] for r in results)
        avg_quality = sum(r['quality_score'] for r in results) / len(results)

        for r in results:
            print(f"✅ {r['title']}")
            print(f"   품질 점수: {r['quality_score']:.1f}/100")
            print(f"   변경사항: {r['changes_count']:,}개")
            print(f"   처리 시간: {r['processing_time']:.2f}초")
            print(f"   저장 위치: {r['output_file']}\n")

        print(f"📊 전체 통계:")
        print(f"   편집된 문서: {len(results)}개")
        print(f"   평균 품질 점수: {avg_quality:.1f}/100")
        print(f"   총 처리 시간: {total_time:.2f}초")

        print(f"\n✨ 모든 편집이 완료되었습니다!")
        print(f"\n다음 단계:")
        print(f"   1. 편집본 검토 (output/ 폴더)")
        print(f"   2. 리포트 확인 (output/*_editing_report.json)")
        print(f"   3. 필요시 추가 수정")
    else:
        print(f"\n❌ 편집 실패")
        sys.exit(1)


if __name__ == "__main__":
    main()
