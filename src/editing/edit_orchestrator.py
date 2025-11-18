# 편집 오케스트레이터
# 작성일: 2025-11-18
# 목적: 교정, 교열, 윤문 3단계를 조율하는 전체 파이프라인 오케스트레이션

import os
import time
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from .edit_proofreading import ProofreadingModule
from .edit_fact_checking import FactCheckingModule
from .edit_copywriting import CopywritingModule
from .models.document import Document, DocumentStructure

# 모델별 가격(USD per 1M tokens)
PRICING_USD_PER_MTOK = {
    "claude-haiku-4-5-20251001": {
        "input": float(os.getenv("CLAUDE_HAIKU_45_INPUT_MTOK", "1.00")),
        "output": float(os.getenv("CLAUDE_HAIKU_45_OUTPUT_MTOK", "5.00")),
    },
    "claude-3-5-sonnet-20240620": {
        "input": float(os.getenv("CLAUDE_SONNET_35_INPUT_MTOK", "3.00")),
        "output": float(os.getenv("CLAUDE_SONNET_35_OUTPUT_MTOK", "15.00")),
    },
}

def _get_model_pricing(model_name: str) -> dict:
    """모델별 가격 정보를 반환"""
    return PRICING_USD_PER_MTOK.get(model_name, {"input": 0.0, "output": 0.0})


class EditOrchestrator:
    """편집 전체 파이프라인 오케스트레이션"""

    def __init__(self, config_path: Optional[str] = None):
        """초기화"""
        self.proofread_module = ProofreadingModule()
        self.fact_check_module = FactCheckingModule()
        self.copywrite_module = CopywritingModule()

        # 설정 로드
        self.config = self._load_config(config_path)

        # 진행 상황 추적
        self.progress_callbacks: List[Callable] = []
        self.current_stage = None
        self.current_progress = 0.0

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """설정 로드"""
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return json.load(f)
        return {
            'enable_parallel': False,
            'chunk_size': 3000,
            'max_workers': 5,
        }

    def load_document(self, file_path: str, domain: str, target_audience: str) -> Document:
        """문서 로드 및 분석"""
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

        # 파일 읽기 (인코딩 문제 처리)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp949') as f:
                content = f.read()

        # 제목 추출 (마크다운 H1)
        title = "Untitled"
        if content.startswith('# '):
            title = content.split('\n')[0].replace('# ', '').strip()

        # 문서 객체 생성
        doc = Document(
            id=file_path.stem,
            title=title,
            content=content,
            domain=domain,
            target_audience=target_audience,
        )

        return doc

    def analyze_document(self, doc: Document) -> Dict[str, Any]:
        """문서 분석"""
        # 통계 수집
        stats = doc.get_statistics()

        # 문제점 식별
        issues = {
            'spacing_issues': self._detect_spacing_issues(doc.content),
            'outdated_info': self.fact_check_module.detect_outdated_info(doc.content),
            'tone_issues': self.copywrite_module.check_tone_consistency(doc.content),
        }

        return {
            'statistics': stats,
            'issues': issues,
            'estimated_time': self._estimate_editing_time(doc),
        }

    def _detect_spacing_issues(self, text: str) -> Dict[str, Any]:
        """띄어쓰기 문제 감지"""
        result = self.proofread_module.check_spacing(text)
        return result.get('corrections', [])

    def _estimate_editing_time(self, doc: Document) -> float:
        """편집 소요 시간 예측"""
        # 간단한 휴리스틱: 단어 수 / 1000 * 60초
        return doc.word_count / 1000 * 60

    def proofread_document(self, doc: Document) -> Dict[str, Any]:
        """문서 교정"""
        self._update_progress('proofreading', 0.0)

        start_time = time.time()
        result = self.proofread_module.proofread(doc.content)

        self._update_progress('proofreading', 1.0)

        return {
            'corrected_text': result.get('corrected_text'),
            'changes': result.get('changes', []),
            'quality_score': result.get('quality_score', 0),
            'processing_time': time.time() - start_time,
        }

    def fact_check_document(self, doc: Document) -> Dict[str, Any]:
        """문서 교열"""
        self._update_progress('fact_checking', 0.0)

        start_time = time.time()
        result = self.fact_check_module.fact_check(doc.content)

        self._update_progress('fact_checking', 1.0)

        return {
            'verified_text': result.get('verified_text', doc.content),
            'outdated_items': result.get('outdated_items', []),
            'quality_score': result.get('quality_score', 0),
            'processing_time': time.time() - start_time,
        }

    def copywrite_document(self, doc: Document) -> Dict[str, Any]:
        """문서 윤문"""
        self._update_progress('copywriting', 0.0)

        start_time = time.time()
        result = self.copywrite_module.copywrite(
            doc.content,
            domain=doc.domain,
            target_audience=doc.target_audience
        )

        self._update_progress('copywriting', 1.0)

        return {
            'improved_text': result.get('improved_text'),
            'changes': result.get('changes', []),
            'quality_score': result.get('quality_score', 0),
            'processing_time': time.time() - start_time,
        }

    def proofread_and_factcheck_document(self, doc: Document) -> Dict[str, Any]:
        """교정 + 교열"""
        proofread_result = self.proofread_document(doc)
        doc.update_content(proofread_result['corrected_text'])

        factcheck_result = self.fact_check_document(doc)

        return {
            'text': factcheck_result['verified_text'],
            'quality_score': (proofread_result['quality_score'] + factcheck_result['quality_score']) / 2,
        }

    def edit_comprehensive(
        self,
        doc: Document,
        stages: Optional[List[str]] = None,
        track_progress: bool = False,
        enable_parallel: bool = False,
        progress_callback: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """전체 편집 파이프라인"""
        if stages is None:
            stages = ['proofreading', 'fact_checking', 'copywriting']

        if progress_callback:
            self.progress_callbacks.append(progress_callback)

        start_time = time.time()
        current_doc = doc
        all_changes = []
        quality_scores = {}
        
        # 토큰 사용량 집계
        usage_by_model = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0})

        # 각 단계별 처리
        for stage in stages:
            if stage == 'proofreading':
                result = self.proofread_document(current_doc)
                current_doc.update_content(result['corrected_text'])
                all_changes.extend(result.get('changes', []))
                quality_scores['proofreading'] = result.get('quality_score', 0)
                
                # 토큰 집계
                usage = result.get('usage', {})
                if usage:
                    model = usage.get('model', 'unknown')
                    usage_by_model[model]["input_tokens"] += usage.get('input_tokens', 0)
                    usage_by_model[model]["output_tokens"] += usage.get('output_tokens', 0)
                    usage_by_model[model]["requests"] += 1

            elif stage == 'fact_checking':
                result = self.fact_check_document(current_doc)
                current_doc.update_content(result['verified_text'])
                all_changes.extend(result.get('outdated_items', []))
                quality_scores['fact_checking'] = result.get('quality_score', 0)
                
                # 토큰 집계
                usage = result.get('usage', {})
                if usage:
                    model = usage.get('model', 'unknown')
                    usage_by_model[model]["input_tokens"] += usage.get('input_tokens', 0)
                    usage_by_model[model]["output_tokens"] += usage.get('output_tokens', 0)
                    usage_by_model[model]["requests"] += 1

            elif stage == 'copywriting':
                result = self.copywrite_document(current_doc)
                current_doc.update_content(result['improved_text'])
                all_changes.extend(result.get('changes', []))
                quality_scores['copywriting'] = result.get('quality_score', 0)
                
                # 토큰 집계
                usage = result.get('usage', {})
                if usage:
                    model = usage.get('model', 'unknown')
                    usage_by_model[model]["input_tokens"] += usage.get('input_tokens', 0)
                    usage_by_model[model]["output_tokens"] += usage.get('output_tokens', 0)
                    usage_by_model[model]["requests"] += 1

        processing_time = time.time() - start_time

        # 최종 품질 점수
        final_quality = sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0
        
        # 토큰/비용 계산
        print("\n" + "=" * 70)
        print("[완료] 편집 완료!")
        print(f"  • 소요시간: {processing_time:.1f}초")
        print(f"  • 총 변경사항: {len(all_changes)}개")
        
        if usage_by_model:
            print(f"  • 토큰 사용량 및 예상 비용 (Anthropic 공식 가격 기준):")
            grand_input = 0
            grand_output = 0
            grand_cost = 0.0
            
            for model, agg in usage_by_model.items():
                inp = agg["input_tokens"]
                outp = agg["output_tokens"]
                reqs = agg["requests"]
                grand_input += inp
                grand_output += outp
                
                price = _get_model_pricing(model)
                cost = (inp / 1_000_000.0) * price.get("input", 0) + (outp / 1_000_000.0) * price.get("output", 0)
                grand_cost += cost
                
                if price.get("input", 0) == 0 and price.get("output", 0) == 0:
                    print(f"    - {model}: input={inp:,} tok, output={outp:,} tok")
                    print(f"      ⚠️  가격표 미등록")
                else:
                    print(f"    - {model} ({reqs}회 호출)")
                    print(f"      Input:  {inp:>10,} tokens × ${price['input']:.2f}/M = ${(inp/1_000_000)*price['input']:.4f}")
                    print(f"      Output: {outp:>10,} tokens × ${price['output']:.2f}/M = ${(outp/1_000_000)*price['output']:.4f}")
                    print(f"      소계: ${cost:.4f}")
            
            print()
            print(f"    💰 총 예상 비용: ${grand_cost:.4f} USD")
            print(f"       (Input: {grand_input:,} tok | Output: {grand_output:,} tok)")
        print("=" * 70)
        print()

        return {
            'final_text': current_doc.content,
            'quality_score': min(final_quality, 100),
            'quality_breakdown': quality_scores,
            'changes_summary': {
                'total_changes': len(all_changes),
                'changes': all_changes,
            },
            'processing_time': processing_time,
            'document': current_doc,
            'usage_summary': dict(usage_by_model)
        }

    def edit_custom_stages(
        self,
        doc: Document,
        stages: List[str],
    ) -> Dict[str, Any]:
        """커스텀 단계 선택 편집"""
        return self.edit_comprehensive(doc, stages=stages)

    def get_document_statistics(self, doc: Document) -> Dict[str, Any]:
        """문서 통계"""
        return {
            'word_count': doc.word_count,
            'character_count': len(doc.content),
            'chapter_count': len(doc.structure.chapters) if doc.structure else 0,
            'section_count': doc.structure.total_sections if doc.structure else 0,
        }

    def batch_process_documents(
        self,
        file_paths: List[str],
        domain: str,
        target_audience: str,
        stages: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """배치 문서 처리"""
        if stages is None:
            stages = ['proofreading', 'fact_checking', 'copywriting']

        results = []

        for i, file_path in enumerate(file_paths):
            self._update_progress(f'batch_document_{i+1}', float(i) / len(file_paths))

            try:
                # 문서 로드
                doc = self.load_document(file_path, domain, target_audience)

                # 편집 실행
                result = self.edit_comprehensive(doc, stages=stages)

                results.append({
                    'file_path': file_path,
                    'status': 'success',
                    'result': result,
                })
            except Exception as e:
                results.append({
                    'file_path': file_path,
                    'status': 'error',
                    'error': str(e),
                })

        self._update_progress('batch', 1.0)

        return results

    def _update_progress(self, stage: str, progress: float):
        """진행 상황 업데이트"""
        self.current_stage = stage
        self.current_progress = progress

        # 콜백 실행
        for callback in self.progress_callbacks:
            try:
                callback(stage, progress)
            except:
                pass

    def generate_report(self, result: Dict[str, Any]) -> str:
        """편집 결과 리포트 생성"""
        report = f"""
# 편집 결과 리포트

## 처리 결과
- 최종 품질 점수: {result.get('quality_score', 0):.1f}/100
- 소요 시간: {result.get('processing_time', 0):.1f}초

## 품질 분석
"""
        quality_breakdown = result.get('quality_breakdown', {})
        for stage, score in quality_breakdown.items():
            report += f"- {stage}: {score:.1f}/100\n"

        changes = result.get('changes_summary', {})
        report += f"\n## 변경 사항\n- 총 변경 건수: {changes.get('total_changes', 0)}\n"

        return report
