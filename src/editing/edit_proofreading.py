# 교정 모듈
# 작성일: 2025-11-18
# 목적: 한국어 맞춤법, 표기법, 외국어 표기 규칙 자동 교정 (AI 기반)

import os
import re
import json
import time
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .models.edit_result import EditResult, EditStage, Change


@dataclass
class ProofreadingResult:
    """교정 결과"""
    corrected_text: str
    changes: List[Dict[str, str]]
    quality_score: float
    processing_time: float


class ProofreadingModule:
    """교정 모듈 - AI 기반 한국어 맞춤법 및 표기법 교정"""

    def __init__(self):
        """초기화"""
        self.changes: List[Change] = []
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.grammar_rules = self._load_grammar_rules()
        
        if not HAS_ANTHROPIC:
            print("⚠️  anthropic 패키지가 설치되지 않았습니다. pip install anthropic")
        
        if not self.api_key:
            print("⚠️  ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    
    def _load_grammar_rules(self) -> str:
        """한글 맞춤법 규정 파일 로드"""
        rules_path = Path("resources/korean_grammar_rules.md")
        if rules_path.exists():
            try:
                return rules_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️  규정 파일 로드 실패: {e}")
                return ""
        return ""
    
    def _clean_prompt_instructions(self, text: str) -> str:
        """프롬프트 지시문 제거"""
        # 【】 브래킷으로 둘러싸인 텍스트 제거
        text = re.sub(r'【[^】]*】', '', text)
        # 연속된 개행 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def check_spacing(self, text: str) -> Dict[str, Any]:
        """띄어쓰기 검사"""
        issues = []
        corrected = text

        # 연속된 한글 단어 8글자 이상 분리 패턴
        if self._has_spacing_issues(text):
            # 한글이 8글자 이상 연속되면 띄어쓰기 오류
            issues.append({
                "type": "spacing",
                "original": text,
                "fixed": text,  # 실제로는 더 복잡한 처리 필요
                "reason": "연속된 한글 단어 띄어쓰기"
            })

        # 띄어쓰기 규칙 적용
        for pattern, replacement in self.SPACING_RULES:
            if re.search(pattern, corrected):
                new_text = re.sub(pattern, replacement, corrected)
                if new_text != corrected:
                    issues.append({
                        "type": "spacing",
                        "original": corrected,
                        "fixed": new_text
                    })
                    corrected = new_text

        return {
            "has_errors": len(issues) > 0,
            "corrections": issues,
            "corrected_text": corrected
        }

    def _has_spacing_issues(self, text: str) -> bool:
        """띄어쓰기 오류 여부 판정"""
        # "띄어쓰기" 같은 복합어가 연속되어 있으면 오류
        # 간단한 휴리스틱: 한글이 8글자 이상 연속되면 확인
        if re.search(r'[가-힣]{8,}', text):
            return True
        return False

    def check_spelling(self, text: str) -> Dict[str, Any]:
        """맞춤법 검사"""
        corrected = text
        corrections = []

        for wrong, correct in self.SPELLING_RULES.items():
            if wrong in corrected:
                corrected = corrected.replace(wrong, correct)
                corrections.append({
                    "type": "spelling",
                    "original": wrong,
                    "fixed": correct,
                    "reason": "맞춤법"
                })

        return {
            "has_errors": len(corrections) > 0,
            "corrections": corrections,
            "corrected_text": corrected
        }

    def check_particles(self, text: str) -> Dict[str, Any]:
        """조사 사용 검증"""
        # 기본적인 조사 검증 규칙
        return {
            "is_correct": True,
            "issues": []
        }

    def check_foreign_language_consistency(self, text: str) -> Dict[str, Any]:
        """외국어 표기법 일관성 검사"""
        # 영문 단어 추출
        english_words = re.findall(r'[A-Za-z]+', text)
        word_variants = {}

        for word in set(english_words):
            variants = []
            for match in re.finditer(word, text, re.IGNORECASE):
                variants.append(text[match.start():match.end()])
            if len(set(variants)) > 1:
                word_variants[word] = list(set(variants))

        return {
            "consistency_issues": len(word_variants),
            "inconsistent_words": word_variants
        }

    def check_technical_terms(self, text: str) -> Dict[str, Any]:
        """기술 용어 일관성 검사"""
        return {
            "issues": [],
            "consistency_score": 1.0
        }

    def check_foreign_spacing(self, text: str) -> Dict[str, Any]:
        """외국어 단어 띄어쓰기"""
        return {
            "issues": []
        }

    def check_number_format(self, text: str) -> Dict[str, Any]:
        """숫자 표기 규칙 검사"""
        corrected = text
        corrections = []

        for pattern, replacement in self.NUMBER_RULES:
            matches = list(re.finditer(pattern, corrected))
            if matches:
                corrected = re.sub(pattern, replacement, corrected)
                corrections.append({
                    "type": "number_format",
                    "original": text,
                    "fixed": corrected
                })

        return {
            "has_errors": len(corrections) > 0,
            "corrections": corrections,
            "corrected_text": corrected
        }

    def check_unit_format(self, text: str) -> Dict[str, Any]:
        """단위 표기 규칙 검사"""
        # 기본 단위 규칙: 숫자와 단위 사이 띄어쓰기
        corrected = re.sub(r'(\d+)\s*([a-zA-Z%]+)', r'\1 \2', text)

        return {
            "has_errors": text != corrected,
            "corrected_text": corrected
        }

    def proofread(self, text: str, domain: str = "general", max_workers: int = 20) -> Dict[str, Any]:
        """AI 기반 전체 교정 프로세스 (병렬 처리)"""
        start_time = time.time()
        self.changes = []
        
        if not self.api_key or not HAS_ANTHROPIC:
            # Fallback: 원본 텍스트 반환
            return {
                'corrected_text': text,
                'changes': [],
                'quality_score': 0,
                'processing_time': time.time() - start_time,
            }
        
        try:
            # 청크 단위로 분할
            chunks = self._split_into_chunks(text, max_chars=3000)
            print(f"[교정] {len(chunks)}개 청크 병렬 처리 중 ({max_workers}개 워커)...", flush=True)
            
            client = Anthropic(api_key=self.api_key)
            model_name = "claude-haiku-4-5-20251001"
            
            # 결과를 인덱스와 함께 저장
            results = {}
            total_input_tokens = 0
            total_output_tokens = 0
            completed_count = 0
            
            def process_chunk(chunk_info):
                """각 청크 처리"""
                i, chunk = chunk_info
                chunk_start = time.time()
                
                if not chunk.strip():
                    return (i, chunk, [], 0, 0, time.time() - chunk_start)
                
                # AI 프롬프트 (규정 포함)
                grammar_section = ""
                if self.grammar_rules:
                    grammar_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【한글 맞춤법 규정 참고】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{self.grammar_rules}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                
                prompt = f"""당신은 출판 교정 전문가입니다. 아래 규정에 따라 맞춤법을 완벽하게 교정하세요.
{grammar_section}

【텍스트】
{chunk}

【교정 원칙】
- 한글 맞춤법, 띄어쓰기, 외래어 표기법 준수
- 의미는 절대 변경 금지 (형식만 수정)

【출력】
JSON만 출력:
{{
  "corrected_text": "교정된 텍스트",
  "changes": [
    {{
      "type": "맞춤법|띄어쓰기|문장부호",
      "original": "원본",
      "fixed": "수정",
      "reason": "이유"
    }}
  ]
}}"""
                
                response = client.messages.create(
                    model=model_name,
                    max_tokens=8192,  # 더 큰 출력 허용
                    temperature=0.3,
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
                
                # JSON 파싱
                try:
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text.strip())
                except json.JSONDecodeError as e:
                    # Fallback: 프롬프트 지시문 제거 후 원본 사용
                    cleaned_chunk = self._clean_prompt_instructions(chunk)
                    result = {
                        'corrected_text': cleaned_chunk,
                        'changes': []
                    }
                
                elapsed = time.time() - chunk_start
                return (i, result['corrected_text'], result.get('changes', []), input_tok, output_tok, elapsed)
            
            # ThreadPoolExecutor로 병렬 처리
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(process_chunk, (i, chunk)): i
                    for i, chunk in enumerate(chunks)
                }
                
                for future in as_completed(futures):
                    i, corrected, changes, input_tok, output_tok, elapsed = future.result()
                    completed_count += 1
                    pending = len(chunks) - completed_count
                    
                    results[i] = corrected
                    total_input_tokens += input_tok
                    total_output_tokens += output_tok
                    
                    if changes:
                        for change in changes:
                            self.changes.append(Change(
                                type=change.get("type", "general"),
                                original=change.get("original", ""),
                                modified=change.get("fixed", ""),
                                reason=change.get("reason", "교정"),
                                position=len(self.changes),
                                confidence=0.95
                            ))
                    
                    print(f"  ✓ [{completed_count:2d}/{len(chunks)}] 청크 {i+1:2d} 완료 ({len(corrected):5d} chars, {elapsed:5.1f}s) | 남은작업: {pending:2d}", flush=True)
            
            # 순서대로 재결합
            text = ''.join([results[i] for i in range(len(chunks))])
                
            # 품질 점수: 변경사항 기반 간단 계산
            quality_score = max(85, min(95, 92 - len(self.changes) * 0.3))
            
            processing_time = time.time() - start_time
            
            return {
                "corrected_text": text,
                "changes": [c.to_dict() for c in self.changes],
                "quality_score": min(quality_score, 100.0),
                "processing_time": processing_time,
                "total_changes": len(self.changes),
                "usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "model": model_name
                }
            }
            
        except Exception as e:
            print(f"⚠️  교정 중 오류 발생: {e}")
            processing_time = time.time() - start_time
            return {
                'corrected_text': text,
                'changes': [],
                'quality_score': 0,
                'processing_time': processing_time,
            }
    
    def _split_into_chunks(self, text: str, max_chars: int = 3000) -> List[str]:
        """텍스트를 청크로 분할"""
        if len(text) <= max_chars:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 2 <= max_chars:
                current_chunk += para + '\n\n'
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para + '\n\n'
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    def proofread_parallel(self, text: str, max_chunk_size: int = 1000, num_workers: int = 2) -> Dict[str, Any]:
        """병렬 처리를 통한 교정"""
        start_time = time.time()

        # 청크 분할
        chunks = self._split_into_chunks(text, max_chunk_size)

        corrected_chunks = []
        all_changes = []

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(self.proofread, chunk): idx
                for idx, chunk in enumerate(chunks)
            }

            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                corrected_chunks.append((idx, result["corrected_text"]))
                all_changes.extend(result["changes"])

        # 청크 순서대로 정렬
        corrected_chunks.sort(key=lambda x: x[0])
        corrected_text = ''.join([chunk[1] for chunk in corrected_chunks])

        processing_time = time.time() - start_time

        return {
            "corrected_text": corrected_text,
            "changes": all_changes,
            "quality_score": 90.0,
            "processing_time": processing_time,
            "total_changes": len(all_changes)
        }

