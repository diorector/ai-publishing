#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
출판 편집자 수준의 문서 편집 파이프라인 V2
2-Pass 편집 시스템: 기계적 교정 + 창의적 윤문

사용법:
  python edit_full_documents_v2.py output/output_laf_translated.md
  python edit_full_documents_v2.py output/output_laf_translated.md --pass1-only
"""

import sys
import os
from pathlib import Path
import argparse
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

from src.editing.edit_orchestrator_v2 import EditOrchestratorV2


def print_header():
    """헤더 출력"""
    print("\n" + "=" * 80)
    print("📝 출판 편집자 수준의 문서 편집 시스템 V2")
    print("=" * 80)
    print("Pass 1: 기계적 교정 (맞춤법, 띄어쓰기, 문장부호)")
    print("Pass 2: 창의적 윤문 (문장 구조, 가독성, 리듬감)")
    print("=" * 80 + "\n")


def parse_args():
    """명령행 인자 파싱"""
    parser = argparse.ArgumentParser(
        description='출판 편집자 수준의 문서 편집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python edit_full_documents_v2.py output/output_laf_translated.md
  python edit_full_documents_v2.py output/output_laf_translated.md --pass1-only
  python edit_full_documents_v2.py output/output_laf_translated.md --workers 5
        """
    )
    
    parser.add_argument('file', help='편집할 파일 경로')
    parser.add_argument('--pass1-only', action='store_true',
                       help='Pass 1 (교정)만 실행 (윤문 생략)')
    parser.add_argument('--workers', type=int, default=10,
                       help='병렬 처리 워커 수 (기본: 10)')
    parser.add_argument('--no-diff', action='store_true',
                       help='비교 리포트 생성 안 함')
    
    return parser.parse_args()


def main():
    """메인 함수"""
    print_header()
    
    # 인자 파싱
    args = parse_args()
    file_path = Path(args.file)
    
    # 파일 존재 확인
    if not file_path.exists():
        print(f"❌ 오류: 파일을 찾을 수 없습니다")
        print(f"   경로: {file_path}")
        sys.exit(1)
    
    print(f"📄 입력 파일: {file_path.name}")
    print(f"   경로: {file_path.absolute()}")
    
    if args.pass1_only:
        print(f"   모드: Pass 1만 실행 (교정)")
    else:
        print(f"   모드: 2-Pass 편집 (교정 + 윤문)")
    
    print(f"   워커: {args.workers}개")
    print()
    
    # 오케스트레이터 초기화
    orchestrator = EditOrchestratorV2()
    
    # 문서 로드
    try:
        doc = orchestrator.load_document(
            file_path=str(file_path),
            domain='business',
            target_audience='general'
        )
    except Exception as e:
        print(f"❌ 문서 로드 실패: {e}")
        sys.exit(1)
    
    # 진행률 콜백
    def progress_callback(stage: str, progress: float):
        """진행률 추적"""
        stages = {
            'pass1_proofread': '📝 Pass 1: 교정',
            'pass2_polish': '✨ Pass 2: 윤문',
        }
        stage_name = stages.get(stage, stage)
        if progress == 0.0:
            print(f"\n{stage_name} 시작...")
        elif progress == 1.0:
            print(f"{stage_name} 완료!")
    
    # 편집 실행
    try:
        result = orchestrator.edit_document(
            doc,
            enable_pass2=not args.pass1_only,
            max_workers=args.workers,
            progress_callback=progress_callback
        )
    except Exception as e:
        print(f"\n❌ 편집 실패: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 출력 폴더 구조 생성
    # output_edited/
    #   ├── 파일명/
    #   │   ├── 파일명_edited.md
    #   │   ├── 파일명_diff_report.md
    #   │   └── 파일명_pass1.md (pass1-only인 경우)
    
    output_base_dir = Path('output_edited')
    output_dir = output_base_dir / file_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 출력 파일 경로
    if args.pass1_only:
        output_file = output_dir / f"{file_path.stem}_edited_pass1.md"
        pass1_file = None
    else:
        output_file = output_dir / f"{file_path.stem}_edited.md"
        # Pass 1 결과도 별도 저장
        pass1_file = output_dir / f"{file_path.stem}_pass1.md"
    
    # 편집본 저장
    print("\n" + "=" * 80)
    print("💾 파일 저장")
    print("=" * 80)
    
    try:
        # 최종 편집본 저장
        output_file.write_text(result['final_text'], encoding='utf-8')
        file_size = output_file.stat().st_size
        print(f"\n✅ 최종 편집본 저장")
        print(f"   경로: {output_file}")
        print(f"   크기: {file_size:,} bytes")
        
        # Pass 1 결과도 저장 (2-Pass인 경우)
        if pass1_file and result.get('pass1_text'):
            pass1_file.write_text(result['pass1_text'], encoding='utf-8')
            pass1_size = pass1_file.stat().st_size
            print(f"\n✅ Pass 1 결과 저장 (참고용)")
            print(f"   경로: {pass1_file}")
            print(f"   크기: {pass1_size:,} bytes")
        
    except Exception as e:
        print(f"\n❌ 저장 실패: {e}")
        sys.exit(1)
    
    # 비교 리포트 생성
    if not args.no_diff:
        print(f"\n📊 비교 리포트 생성 중...")
        
        diff_file = output_dir / f"{file_path.stem}_diff_report.md"
        
        try:
            orchestrator.generate_comparison_report(
                result['original_text'],
                result['final_text'],
                output_path=diff_file
            )
        except Exception as e:
            print(f"⚠️  비교 리포트 생성 실패: {e}")
    
    # 최종 요약
    print("\n" + "=" * 80)
    print("✨ 편집 완료!")
    print("=" * 80)
    
    diff_stats = result.get('diff_stats', {})
    
    print(f"\n📊 편집 통계:")
    print(f"   원본 라인: {diff_stats.get('total_lines_original', 0):,}개")
    print(f"   편집 라인: {diff_stats.get('total_lines_edited', 0):,}개")
    print(f"   변경 라인: {diff_stats.get('lines_changed', 0):,}개")
    print(f"   유사도: {diff_stats.get('similarity_ratio', 0)*100:.1f}%")
    
    print(f"\n💰 비용:")
    print(f"   총 비용: ${result.get('total_cost', 0):.4f} USD")
    
    print(f"\n⏱️  시간:")
    print(f"   총 소요: {result.get('processing_time', 0):.1f}초")
    
    print(f"\n📁 출력 폴더: {output_dir}")
    print(f"\n📄 생성된 파일:")
    print(f"   ├─ {output_file.name} (최종 편집본)")
    if pass1_file and result.get('pass1_text'):
        print(f"   ├─ {pass1_file.name} (Pass 1 결과)")
    if not args.no_diff:
        print(f"   └─ {diff_file.name} (비교 리포트)")
    
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
