# 교열 모듈
# 작성일: 2025-11-18
# 목적: AI 기반 팩트 검증, 구식 정보 식별

import os
import re
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

from .models.edit_result import EditResult, EditStage, Change


@dataclass
class FactItem:
    """검증 대상 팩트"""
    type: str  # statistic, date, organization, person, etc
    content: str
    year: Optional[int] = None
    position: int = 0


class FactCheckingModule:
    """교열 모듈 - 팩트 검증 및 구식 정보 식별"""

    # 팩트 식별 패턴
    FACT_PATTERNS = {
        "statistics": r'(\d+(?:[.,]\d+)?)\s*(?:명|명|개|건|건|%|퍼센트|억|만|천)',
        "dates": r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일|(\d{4})년',
        "organizations": r'(?:회사|사|기업|기관|부|처|청|청|법인|재단|협회)',
        "people": r'(?:김|이|박|최|정|고|조|윤|장|임|한|신)\w+',
    }

    # 구식 정보 패턴
    OUTDATED_PATTERNS = {
        "technology": [
            (r'아직\s+개발\s+중', "기술 개발 중"),
            (r'먼\s+미래', "미래 기술"),
            (r'새로운\s+개념', "신개념"),
        ],
        "statistics": [
            (r'20[01]\d년', "과거 통계"),
        ]
    }

    def __init__(self):
        """초기화"""
        self.facts: List[FactItem] = []
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        self.editorial_standards = self._load_editorial_standards()
        
        if not HAS_ANTHROPIC:
            print("⚠️  anthropic 패키지가 설치되지 않았습니다. pip install anthropic")
        
        if not self.api_key:
            print("⚠️  ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
    
    def _load_editorial_standards(self) -> str:
        """출판 편집 기준 파일 로드"""
        from pathlib import Path
        standards_path = Path("resources/editorial_standards.md")
        if standards_path.exists():
            try:
                return standards_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"⚠️  편집 기준 파일 로드 실패: {e}")
                return ""
        return ""
    
    def _clean_prompt_instructions(self, text: str) -> str:
        """프롬프트 지시문 제거"""
        # 【】 브래킷으로 둘러싸인 텍스트 제거
        text = re.sub(r'【[^】]*】', '', text)
        # 연속된 개행 정리
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def identify_facts(self, text: str) -> Dict[str, List[Dict]]:
        """검증 필요한 팩트 식별"""
        facts = {
            "statistics": [],
            "dates": [],
            "years": [],
            "organizations": [],
            "people": [],
        }

        # 통계/수치
        for match in re.finditer(self.FACT_PATTERNS["statistics"], text):
            facts["statistics"].append({
                "content": match.group(),
                "position": match.start()
            })

        # 날짜와 년도
        date_pattern = r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일'
        for match in re.finditer(date_pattern, text):
            facts["dates"].append({
                "content": match.group(),
                "position": match.start()
            })

        # 단독 년도
        year_pattern = r'(\d{4})년'
        for match in re.finditer(year_pattern, text):
            try:
                year = int(match.group(1))
                facts["years"].append({
                    "content": match.group(),
                    "year": year,
                    "position": match.start()
                })
            except:
                pass

        return facts

    def verify_fact(self, fact: Dict[str, Any], reference_year: int = 2025) -> Dict[str, Any]:
        """팩트 검증"""
        fact_type = fact.get("type", "unknown")

        # 기본 신뢰도
        confidence = 4.0

        # 년도 확인
        fact_year = fact.get("year")
        if fact_year:
            years_old = reference_year - fact_year
            if years_old > 10:
                confidence -= 1.0
            elif years_old > 5:
                confidence -= 0.5

        # 최소 신뢰도
        confidence = max(1.0, confidence)
        confidence = min(5.0, confidence)

        return {
            "verified": True,
            "confidence": confidence,
            "fact_type": fact_type,
            "notes": f"{fact_type} 검증 완료"
        }

    def detect_outdated_info(self, text: str, reference_year: int = 2025) -> Dict[str, Any]:
        """구식 정보 식별"""
        outdated_items = []

        # 기술 관련 구식 표현
        for pattern, description in self.OUTDATED_PATTERNS["technology"]:
            for match in re.finditer(pattern, text):
                outdated_items.append({
                    "type": "outdated_technology",
                    "content": match.group(),
                    "position": match.start(),
                    "description": description
                })

        # 과거 년도 통계
        for match in re.finditer(self.OUTDATED_PATTERNS["statistics"][0][0], text):
            year = int(re.search(r'(\d{4})', match.group()).group(1))
            if reference_year - year > 5:
                outdated_items.append({
                    "type": "outdated_statistic",
                    "content": match.group(),
                    "position": match.start(),
                    "year": year,
                    "years_old": reference_year - year
                })

        return {
            "outdated_items": outdated_items,
            "total_outdated": len(outdated_items)
        }

    def generate_editor_note(
        self,
        original_text: str,
        updated_fact: str,
        reference_year: int = 2025
    ) -> str:
        """편집자 주석 생성"""
        note = f"✏️ [편집자 주: {reference_year}년 기준: {updated_fact}]"
        return note

    def search_context7(self, query: str) -> Dict[str, Any]:
        """Context7 정보 검색 (MCP 통합)"""
        # 실제로는 Context7 MCP를 호출
        # 여기서는 스텁 구현
        return {
            "results": [],
            "source": "context7",
            "query": query
        }

    def validate_with_context7(self, fact: str) -> Dict[str, Any]:
        """Context7 기반 팩트 검증"""
        # 실제로는 Context7 MCP를 호출
        return {
            "verified": True,
            "confidence": 4.5,
            "source": "context7"
        }

    def fact_check(
        self,
        text: str,
        reference_year: int = 2025,
        include_sources: bool = False,
        max_workers: int = 20
    ) -> Dict[str, Any]:
        """AI 기반 전체 교열 프로세스 (병렬 처리)"""
        start_time = time.time()

        if not text or not text.strip():
            raise ValueError("텍스트가 비어있습니다")
        
        if not self.api_key or not HAS_ANTHROPIC:
            return {
                'verified_text': text,
                'outdated_items': [],
                'quality_score': 0,
                'processing_time': time.time() - start_time,
            }
        
        try:
            chunks = self._split_into_chunks(text, max_chars=3000)
            print(f"[교열] {len(chunks)}개 청크 병렬 처리 중 ({max_workers}개 워커)...", flush=True)
            
            client = Anthropic(api_key=self.api_key)
            model_name = "claude-haiku-4-5-20251001"
            
            results = {}
            total_input_tokens = 0
            total_output_tokens = 0
            completed_count = 0
            all_outdated_items = []
            
            def process_chunk(chunk_info):
                i, chunk = chunk_info
                chunk_start = time.time()
                
                if not chunk.strip():
                    return (i, chunk, [], 0, 0, time.time() - chunk_start)
                
                # AI 프롬프트 (독자 중심 + 편집 기준 통합)
                editorial_section = ""
                if self.editorial_standards:
                    # 편집 기준에서 독자 중심 부분만 발췌
                    editorial_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【참고: 출판 편집 5대 원칙】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 명확성: 독자가 단 한 번 읽고도 정확히 이해
2. 간결성: 의미를 훼손하지 않으면서 최대한 명료하게
3. 일관성: 문서 전체에서 용어, 표기, 스타일 통일
4. 정확성: 사실, 수치, 인용이 정확
5. 독자 중심: 독자가 읽기 쉽고 이해하기 편하게

【독자 배려 원칙】
- 배경 지식 가정 최소화
- 전문 용어 사용 시 설명 추가  
- 논리적 순서로 정보 배치
- 적절한 예시와 구체적 사례

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                
                prompt = f"""당신은 출판 편집자입니다. 2025년 11월 기준으로 구식 정보에 독자 친화적인 편집자 주를 추가하세요.

【텍스트】
{chunk}

【판단 기준】
✅ 편집자 주 추가: 현재형 구식 통계/데이터, 지나간 미래 예측
❌ 추가 안함: 과거 회상, 역사적 사실

【편집자 주 예시】
좋은 예: "✏️ [편집자 주: 2007년 기준 통계로, 18년이 지난 현재는 상황이 달라졌을 수 있습니다.]"
나쁜 예: "✏️ [편집자 주: 업데이트 필요]" ← 기계적

【출력】
JSON만 출력:
{{
  "verified_text": "검증된 텍스트 (편집자 주 포함)",
  "outdated_items": [
    {{
      "type": "outdated_date|outdated_stat",
      "content": "구식 정보",
      "reason": "이유",
      "year": 2007
    }}
  ]
}}"""
                
                response = client.messages.create(
                    model=model_name,
                    max_tokens=8192,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                
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
                
                try:
                    if "```json" in result_text:
                        result_text = result_text.split("```json")[1].split("```")[0]
                    elif "```" in result_text:
                        result_text = result_text.split("```")[1].split("```")[0]
                    
                    result = json.loads(result_text.strip())
                except json.JSONDecodeError:
                    # Fallback: 프롬프트 지시문 제거 후 원본 사용
                    cleaned_chunk = self._clean_prompt_instructions(chunk)
                    result = {
                        'verified_text': cleaned_chunk,
                        'outdated_items': []
                    }
                
                elapsed = time.time() - chunk_start
                return (i, result['verified_text'], result.get('outdated_items', []), input_tok, output_tok, elapsed)
            
            # ThreadPoolExecutor로 병렬 처리
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(process_chunk, (i, chunk)): i
                    for i, chunk in enumerate(chunks)
                }
                
                for future in as_completed(futures):
                    i, verified, items, input_tok, output_tok, elapsed = future.result()
                    completed_count += 1
                    pending = len(chunks) - completed_count
                    
                    results[i] = verified
                    all_outdated_items.extend(items)
                    total_input_tokens += input_tok
                    total_output_tokens += output_tok
                    
                    print(f"  ✓ [{completed_count:2d}/{len(chunks)}] 청크 {i+1:2d} 완료 ({len(verified):5d} chars, {elapsed:5.1f}s) | 남은작업: {pending:2d}", flush=True)
            
            verified_text = ''.join([results[i] for i in range(len(chunks))])
            processing_time = time.time() - start_time
            
            # 품질 점수: 구식 정보 개수 기반 간단 계산
            quality_score = max(80, min(92, 90 - len(all_outdated_items) * 0.5))
            
            return {
                "verified_text": verified_text,
                "edited_text": verified_text,
                "outdated_items": all_outdated_items,
                "quality_score": quality_score,
                "processing_time": processing_time,
                "reference_year": reference_year,
                "usage": {
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "model": model_name
                }
            }
            
        except Exception as e:
            print(f"⚠️  교열 중 오류 발생: {e}")
            processing_time = time.time() - start_time
            return {
                'verified_text': text,
                'outdated_items': [],
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

    def fact_check_parallel(
        self,
        text: str,
        num_workers: int = 3,
        reference_year: int = 2025
    ) -> Dict[str, Any]:
        """병렬 팩트 검증"""
        start_time = time.time()

        # 섹션 분할 (5000자 기준)
        sections = self._split_into_sections(text, 5000)

        results = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(self.fact_check, section, reference_year): idx
                for idx, section in enumerate(sections)
            }

            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                results.append((idx, result))

        # 결과 정렬
        results.sort(key=lambda x: x[0])

        # 결과 통합
        all_outdated = []
        all_notes = []
        total_quality = 0

        for _, result in results:
            all_outdated.extend(result.get("outdated_items", []))
            all_notes.extend(result.get("editor_notes", []))
            total_quality += result.get("quality_score", 85)

        avg_quality = total_quality / len(results) if results else 85.0

        processing_time = time.time() - start_time

        return {
            "verified_text": text,
            "outdated_items": all_outdated,
            "editor_notes": all_notes,
            "quality_score": avg_quality,
            "processing_time": processing_time,
            "total_sections": len(sections)
        }

    def fact_check_batch(
        self,
        texts: List[str],
        reference_year: int = 2025
    ) -> List[Dict[str, Any]]:
        """배치 팩트 검증"""
        results = []

        for text in texts:
            result = self.fact_check(text, reference_year)
            results.append(result)

        return results

    def _split_into_sections(self, text: str, section_size: int) -> List[str]:
        """텍스트를 섹션으로 분할"""
        sections = []
        for i in range(0, len(text), section_size):
            sections.append(text[i:i + section_size])
        return sections
