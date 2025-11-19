# 개선된 편집 오케스트레이터 V2
# 출판 편집자 수준의 2-Pass 편집 시스템

import os
import time
import json
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .prompts.proofreading_prompt import get_proofreading_prompt
from .prompts.polishing_prompt import get_polishing_prompt
from .utils.diff_generator import DiffGenerator, generate_markdown_diff
from .models.document import Document

# 모델별 가격
PRICING_USD_PER_MTOK = {
    "claude-3-5-sonnet-20241022": {
        "input": float(os.getenv("CLAUDE_SONNET_35_INPUT_MTOK", "3.00")),
        "output": float(os.getenv("CLAUDE_SONNET_35_OUTPUT_MTOK", "15.00")),
    },
    "claude-3-5-sonnet-20240620": {
        "input": float(os.getenv("CLAUDE_SONNET_35_INPUT_MTOK", "3.00")),
        "output": float(os.getenv("CLAUDE_SONNET_35_OUTPUT_MTOK", "15.00")),
    },
    "claude-3-7-sonnet-20250219": {
        "input": float(os.getenv("CLAUDE_SONNET_37_INPUT_MTOK", "3.00")),
        "output": float(os.getenv("CLAUDE_SONNET_37_OUTPUT_MTOK", "15.00")),
    },
    "claude-haiku-4-5-20251001": {
        "input": float(os.getenv("CLAUDE_HAIKU_45_INPUT_MTOK", "1.00")),
        "output": float(os.getenv("CLAUDE_HAIKU_45_OUTPUT_MTOK", "5.00")),
    },
}


def _get_model_pricing(model_name: str) -> dict:
    """모델별 가격 정보"""
    return PRICING_USD_PER_MTOK.get(model_name, {"input": 0.0, "output": 0.0})


class EditOrchestratorV2:
    """
    출판 편집자 수준의 2-Pass 편집 시스템
    
    Pass 1: 기계적 교정 (맞춤법, 띄어쓰기, 문장부호)
    Pass 2: 창의적 윤문 (문장 구조, 가독성, 리듬감)
    """
    
    def __init__(self):
        """초기화"""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.diff_generator = DiffGenerator()
        
        if not HAS_ANTHROPIC:
            print("⚠️  anthropic 패키지가 설치되지 않았습니다.")
        
        if not self.api_key:
            print("⚠️  ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    
    def load_document(self, file_path: str, domain: str = "business", 
                     target_audience: str = "general") -> Document:
        """문서 로드"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        # 파일 읽기
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp949') as f:
                content = f.read()
        
        # 제목 추출
        title = "Untitled"
        if content.startswith('# '):
            title = content.split('\n')[0].replace('# ', '').strip()
        
        doc = Document(
            id=file_path.stem,
            title=title,
            content=content,
            domain=domain,
            target_audience=target_audience,
        )
        
        return doc
    
    def _split_into_chunks(self, text: str, max_chars: int = 4000) -> List[str]:
        """
        텍스트를 청크로 분할
        
        마크다운 구조를 유지하면서 분할:
        - ## Section 단위로 우선 분할
        - 너무 크면 단락 단위로 추가 분할
        """
        # Section 단위로 분할
        sections = []
        current_section = []
        
        lines = text.split('\n')
        
        for line in lines:
            # Section 헤더 감지
            if line.startswith('## Section'):
                if current_section:
                    sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        if current_section:
            sections.append('\n'.join(current_section))
        
        # 너무 큰 섹션은 추가 분할
        chunks = []
        for section in sections:
            if len(section) <= max_chars:
                chunks.append(section)
            else:
                # 단락 단위로 분할
                paragraphs = section.split('\n\n')
                current_chunk = ""
                
                for para in paragraphs:
                    if len(current_chunk) + len(para) + 2 <= max_chars:
                        current_chunk += para + '\n\n'
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = para + '\n\n'
                
                if current_chunk:
                    chunks.append(current_chunk.strip())
        
        return chunks
    
    def _call_claude(self, prompt: str, model: str = "claude-3-7-sonnet-20250219",
                    temperature: float = 0.3) -> tuple:
        """
        Claude API 호출
        
        Returns:
            (응답 텍스트, input_tokens, output_tokens)
        """
        if not self.api_key or not HAS_ANTHROPIC:
            return ("", 0, 0)
        
        try:
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model=model,
                max_tokens=16000,
                temperature=temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # 토큰 사용량 추출
            input_tok = 0
            output_tok = 0
            try:
                usage_obj = getattr(response, "usage", None)
                if usage_obj:
                    input_tok = int(getattr(usage_obj, "input_tokens", 0) or 0)
                    output_tok = int(getattr(usage_obj, "output_tokens", 0) or 0)
            except:
                pass
            
            result_text = response.content[0].text
            
            # 마크다운 코드블록 제거
            if "```" in result_text:
                # ```markdown 또는 ``` 로 감싸진 경우
                import re
                match = re.search(r'```(?:markdown)?\n(.*?)\n```', result_text, re.DOTALL)
                if match:
                    result_text = match.group(1)
            
            return (result_text.strip(), input_tok, output_tok)
            
        except Exception as e:
            print(f"⚠️  Claude API 호출 실패: {e}")
            return ("", 0, 0)
    
    def pass1_proofread(self, text: str, max_workers: int = 10) -> Dict[str, Any]:
        """
        Pass 1: 기계적 교정
        
        맞춤법, 띄어쓰기, 문장부호만 수정
        문장 구조는 변경하지 않음
        """
        print("\n" + "=" * 80)
        print("📝 Pass 1: 기계적 교정 (맞춤법, 띄어쓰기, 문장부호)")
        print("=" * 80)
        
        start_time = time.time()
        
        # 청크 분할
        chunks = self._split_into_chunks(text, max_chars=4000)
        print(f"\n[교정] {len(chunks)}개 청크 병렬 처리 중 ({max_workers}개 워커)...")
        
        # 병렬 처리
        results = {}
        total_input_tokens = 0
        total_output_tokens = 0
        completed_count = 0
        
        def process_chunk(chunk_info):
            i, chunk = chunk_info
            chunk_start = time.time()
            
            if not chunk.strip():
                return (i, chunk, 0, 0, time.time() - chunk_start)
            
            prompt = get_proofreading_prompt(chunk)
            corrected, input_tok, output_tok = self._call_claude(
                prompt,
                model="claude-3-7-sonnet-20250219",
                temperature=0.2  # 낮은 temperature로 일관성 확보
            )
            
            if not corrected:
                corrected = chunk
            
            elapsed = time.time() - chunk_start
            return (i, corrected, input_tok, output_tok, elapsed)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_chunk, (i, chunk)): i
                for i, chunk in enumerate(chunks)
            }
            
            for future in as_completed(futures):
                i, corrected, input_tok, output_tok, elapsed = future.result()
                completed_count += 1
                pending = len(chunks) - completed_count
                
                results[i] = corrected
                total_input_tokens += input_tok
                total_output_tokens += output_tok
                
                print(f"  ✓ [{completed_count:2d}/{len(chunks)}] 청크 {i+1:2d} 완료 "
                      f"({len(corrected):5d} chars, {elapsed:5.1f}s) | 남은작업: {pending:2d}",
                      flush=True)
        
        # 재결합
        corrected_text = '\n\n'.join([results[i] for i in range(len(chunks))])
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ Pass 1 완료 ({processing_time:.1f}초)")
        
        return {
            'text': corrected_text,
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'processing_time': processing_time,
            'model': 'claude-3-7-sonnet-20250219'
        }
    
    def pass2_polish(self, text: str, max_workers: int = 10) -> Dict[str, Any]:
        """
        Pass 2: 창의적 윤문
        
        문장 구조, 가독성, 리듬감 개선
        번역체 제거, 긴 문장 분리
        """
        print("\n" + "=" * 80)
        print("✨ Pass 2: 창의적 윤문 (문장 구조, 가독성, 리듬감)")
        print("=" * 80)
        
        start_time = time.time()
        
        # 청크 분할
        chunks = self._split_into_chunks(text, max_chars=4000)
        print(f"\n[윤문] {len(chunks)}개 청크 병렬 처리 중 ({max_workers}개 워커)...")
        
        # 병렬 처리
        results = {}
        total_input_tokens = 0
        total_output_tokens = 0
        completed_count = 0
        
        def process_chunk(chunk_info):
            i, chunk = chunk_info
            chunk_start = time.time()
            
            if not chunk.strip():
                return (i, chunk, 0, 0, time.time() - chunk_start)
            
            prompt = get_polishing_prompt(chunk)
            polished, input_tok, output_tok = self._call_claude(
                prompt,
                model="claude-3-7-sonnet-20250219",
                temperature=0.5  # 약간 높은 temperature로 창의성 확보
            )
            
            if not polished:
                polished = chunk
            
            elapsed = time.time() - chunk_start
            return (i, polished, input_tok, output_tok, elapsed)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_chunk, (i, chunk)): i
                for i, chunk in enumerate(chunks)
            }
            
            for future in as_completed(futures):
                i, polished, input_tok, output_tok, elapsed = future.result()
                completed_count += 1
                pending = len(chunks) - completed_count
                
                results[i] = polished
                total_input_tokens += input_tok
                total_output_tokens += output_tok
                
                print(f"  ✓ [{completed_count:2d}/{len(chunks)}] 청크 {i+1:2d} 완료 "
                      f"({len(polished):5d} chars, {elapsed:5.1f}s) | 남은작업: {pending:2d}",
                      flush=True)
        
        # 재결합
        polished_text = '\n\n'.join([results[i] for i in range(len(chunks))])
        
        processing_time = time.time() - start_time
        
        print(f"\n✅ Pass 2 완료 ({processing_time:.1f}초)")
        
        return {
            'text': polished_text,
            'input_tokens': total_input_tokens,
            'output_tokens': total_output_tokens,
            'processing_time': processing_time,
            'model': 'claude-3-7-sonnet-20250219'
        }
    
    def edit_document(self, doc: Document, enable_pass2: bool = True,
                     max_workers: int = 10, progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        전체 편집 프로세스
        
        Args:
            doc: 문서 객체
            enable_pass2: Pass 2 (윤문) 활성화 여부
            max_workers: 병렬 처리 워커 수
            progress_callback: 진행률 콜백
        
        Returns:
            편집 결과 딕셔너리
        """
        print("\n" + "=" * 80)
        print("📚 출판 편집자 수준의 2-Pass 편집 시스템")
        print("=" * 80)
        print(f"\n문서: {doc.title}")
        print(f"단어 수: {doc.word_count:,}개")
        print(f"문자 수: {len(doc.content):,}자")
        
        start_time = time.time()
        original_text = doc.content
        
        # Pass 1: 기계적 교정
        if progress_callback:
            progress_callback('pass1_proofread', 0.0)
        
        pass1_result = self.pass1_proofread(original_text, max_workers=max_workers)
        corrected_text = pass1_result['text']
        
        if progress_callback:
            progress_callback('pass1_proofread', 1.0)
        
        # Pass 2: 창의적 윤문
        polished_text = corrected_text
        pass2_result = None
        
        if enable_pass2:
            if progress_callback:
                progress_callback('pass2_polish', 0.0)
            
            pass2_result = self.pass2_polish(corrected_text, max_workers=max_workers)
            polished_text = pass2_result['text']
            
            if progress_callback:
                progress_callback('pass2_polish', 1.0)
        
        # 통계 계산
        total_time = time.time() - start_time
        
        # 토큰 사용량 집계
        usage_by_model = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0})
        
        model = pass1_result['model']
        usage_by_model[model]["input_tokens"] += pass1_result['input_tokens']
        usage_by_model[model]["output_tokens"] += pass1_result['output_tokens']
        usage_by_model[model]["requests"] += 1
        
        if pass2_result:
            model = pass2_result['model']
            usage_by_model[model]["input_tokens"] += pass2_result['input_tokens']
            usage_by_model[model]["output_tokens"] += pass2_result['output_tokens']
            usage_by_model[model]["requests"] += 1
        
        # 비용 계산
        print("\n" + "=" * 80)
        print("💰 토큰 사용량 및 예상 비용")
        print("=" * 80)
        
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
            cost = (inp / 1_000_000.0) * price["input"] + (outp / 1_000_000.0) * price["output"]
            grand_cost += cost
            
            print(f"\n{model} ({reqs}회 호출)")
            print(f"  Input:  {inp:>10,} tokens × ${price['input']:.2f}/M = ${(inp/1_000_000)*price['input']:.4f}")
            print(f"  Output: {outp:>10,} tokens × ${price['output']:.2f}/M = ${(outp/1_000_000)*price['output']:.4f}")
            print(f"  소계: ${cost:.4f}")
        
        print(f"\n💰 총 예상 비용: ${grand_cost:.4f} USD")
        print(f"   (Input: {grand_input:,} tok | Output: {grand_output:,} tok)")
        print(f"\n⏱️  총 소요시간: {total_time:.1f}초")
        print("=" * 80)
        
        # 변경사항 통계
        diff_stats = self.diff_generator.generate_summary(original_text, polished_text)
        
        return {
            'final_text': polished_text,
            'original_text': original_text,
            'pass1_text': corrected_text,
            'pass2_text': polished_text if enable_pass2 else None,
            'processing_time': total_time,
            'usage_summary': dict(usage_by_model),
            'total_cost': grand_cost,
            'diff_stats': diff_stats,
            'quality_score': 90.0,  # 기본 품질 점수
        }
    
    def generate_comparison_report(self, original: str, edited: str, 
                                   output_path: Optional[Path] = None) -> str:
        """
        편집 전후 비교 리포트 생성
        
        Args:
            original: 원본 텍스트
            edited: 편집된 텍스트
            output_path: 저장 경로 (선택)
        
        Returns:
            마크다운 형식의 비교 리포트
        """
        report = generate_markdown_diff(original, edited, title="편집 전후 비교")
        
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
            print(f"\n📊 비교 리포트 저장: {output_path}")
        
        return report
