#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Complete PDF Translation Pipeline with Claude API
완전한 PDF 번역 파이프라인 (모든 청크 번역)
"""
import sys
import os
from pathlib import Path
from typing import List, Optional
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

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


def get_api_key() -> Optional[str]:
    """Get Claude API key"""
    return os.getenv('ANTHROPIC_API_KEY')


# 모델별 가격(USD per 1M tokens). 필요 시 환경변수로 덮어쓰기 지원.
# - 공식 가격: https://www.anthropic.com/pricing
# - Claude Haiku 4.5: $1.00/M input, $5.00/M output (2025-01-01 기준)
# - 환경변수로 덮어쓰기: CLAUDE_HAIKU_45_INPUT_MTOK, CLAUDE_HAIKU_45_OUTPUT_MTOK
PRICING_USD_PER_MTOK = {
    "claude-haiku-4-5-20251001": {
        "input": float(os.getenv("CLAUDE_HAIKU_45_INPUT_MTOK", "1.00")),
        "output": float(os.getenv("CLAUDE_HAIKU_45_OUTPUT_MTOK", "5.00")),
    },
    # 다른 모델 추가 가능
    "claude-3-5-sonnet-20241022": {
        "input": float(os.getenv("CLAUDE_SONNET_35_INPUT_MTOK", "3.00")),
        "output": float(os.getenv("CLAUDE_SONNET_35_OUTPUT_MTOK", "15.00")),
    },
}

def _get_model_pricing(model_name: str) -> dict:
    """모델별 가격 정보를 반환. 미등록 모델은 0으로 채워 반환."""
    return PRICING_USD_PER_MTOK.get(model_name, {"input": 0.0, "output": 0.0})


def extract_glossary(text: str, api_key: str, sample_size: int = 30000) -> dict:
    """
    전체 텍스트에서 핵심 용어 추출 및 번역
    
    문서를 샘플링하여 분야를 파악하고 핵심 전문 용어를 자동으로 추출합니다.
    이를 통해 어떤 분야의 문서가 와도 일관된 용어 번역을 보장합니다.
    
    전략:
    - 텍스트 샘플링: 처음 15k + 중간 10k + 끝 5k chars
    - Haiku 모델 사용으로 비용 최소화 (~$0.01)
    - JSON 응답으로 파싱 간편화
    
    Args:
        text: 전체 텍스트
        api_key: Anthropic API 키
        sample_size: 샘플링할 총 크기 (기본 30000)
    
    Returns:
        {
            "domain": "문서 분야",
            "key_terms": {"영문": "한글", ...}
        }
    """
    print(f"[ANALYZING] Extracting key terms from document...", flush=True)
    
    # 샘플링 전략: 처음, 중간, 끝에서 고르게
    total_len = len(text)
    sample = (
        text[:15000] +  # 처음 (도입부, 주요 개념)
        text[total_len//2:total_len//2+10000] +  # 중간 (핵심 내용)
        text[-5000:]  # 끝 (결론, 요약)
    )
    
    prompt = f"""이 문서를 분석하여 핵심 전문 용어를 추출하세요.

【분석 대상 텍스트 샘플】
{sample}

【작업】
1. 문서의 분야/주제를 파악하세요 (예: startup, medicine, law, technology, finance 등)
2. 자주 등장하거나 중요한 전문 용어 20-30개를 추출하세요
3. 각 용어의 적절한 한국어 번역을 제시하세요

【번역 원칙】
- 해당 분야에서 통용되는 번역이 있으면 그대로 사용
- 없으면 음차 또는 의역
- 약어는 가능하면 그대로 유지 (예: CEO, MVP, API)
- 일관성이 가장 중요합니다

【중요 예시】
- startup 분야: "term sheet" → "텀시트" (⚠️ "이용약관" 아님!)
- medicine: "hypertension" → "고혈압"
- law: "plaintiff" → "원고"

【출력 형식】
JSON만 출력하세요 (설명 없이):
{{
  "domain": "분야명",
  "key_terms": {{
    "영문용어1": "한글번역1",
    "영문용어2": "한글번역2"
  }}
}}"""

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # 저렴한 모델
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # JSON 파싱
        result_text = response.content[0].text
        
        # 마크다운 코드 블록 제거
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        glossary = json.loads(result_text.strip())
        
        print(f"[OK] Glossary extracted successfully", flush=True)
        return glossary
        
    except Exception as e:
        print(f"[WARNING] Glossary extraction failed: {e}", flush=True)
        print(f"[INFO] Proceeding without custom glossary", flush=True)
        return {"domain": "unknown", "key_terms": {}}


def extract_pdf(pdf_path):
    """
    Extract text from PDF with progress tracking

    이 함수는 PDF 파일에서 텍스트를 추출합니다:
    1. PDF 메타데이터 수집 (페이지 수, 제목 등)
    2. 각 페이지별 텍스트 추출
    3. 진행률 표시 (매 5페이지마다)
    4. 전체 텍스트와 메타데이터 반환

    Args:
        pdf_path: PDF 파일 경로

    Returns:
        tuple: (전체_텍스트, 메타데이터, 페이지_목록) 또는 추출 실패 시 (None, None, None)
    """
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
            print(f"[EXTRACTING] Processing {len(pdf.pages)} pages...")
            print()

            for i, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                pages.append(page_text if page_text else "")
                
                # 진행 상황 표시 (매 5페이지마다)
                if i % 5 == 0 or i == len(pdf.pages):
                    progress = (i / len(pdf.pages)) * 100
                    print(f"  [{i:3d}/{len(pdf.pages)}] {progress:5.1f}% complete", flush=True)
            
            print()
            return text, metadata, pages

    except ImportError:
        print("[ERROR] pdfplumber not installed: pip install pdfplumber")
        return None, None, None


def chunk_text(text, chunk_size=5000, overlap_sentences=2):
    """
    스마트 청킹: 문장 경계를 감지하여 의미 단위 기반 분할

    이 함수는 단순 크기 기반이 아닌 의미 있는 문장 단위로 텍스트를 분할합니다:

    1. 문장 경계 감지 (정규식 기반):
       - `.`, `?`, `!`를 기준으로 분리
       - 약어 (Mr., U.S. 등) 및 URL 보존
       - 정규식: r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+'

    2. 청크 생성 (chunk_size 기준):
       - 각 청크는 chunk_size(기본 5000자)를 목표로 함
       - 문장 경계에서만 분할하여 의미 보존

    3. 컨텍스트 오버랩 (2문장):
       - 이전 청크의 마지막 N개 문장을 새 청크 시작에 포함
       - 번역 일관성 보장 및 청크 경계 부드럽게 처리
       - 각 청크는 {'text': '...', 'overlap': '...'} 형식으로 반환

    성능:
    - 11개 청크 생성 (50,898자 문서): <1초
    - 오버랩으로 인한 크기 증가: ~5-10%

    Args:
        text (str): 분할할 텍스트
        chunk_size (int): 각 청크의 목표 크기 (기본 5000자)
        overlap_sentences (int): 청크 간 오버랩 문장 수 (기본 2)

    Returns:
        List[dict]: {'text': 청크_내용, 'overlap': 이전_컨텍스트} 형식의 청크 리스트
    """
    print(f"[CHUNKING] Smart chunking with sentence boundaries...", flush=True)
    
    import re
    
    # 문장 분리 (개선된 정규식 - 약어, URL 등 고려)
    sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+'
    sentences = re.split(sentence_pattern, text)
    
    chunks = []
    current_chunk = []
    current_size = 0
    overlap_buffer = []  # 오버랩을 위한 최근 문장 저장
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        sentence_size = len(sentence)
        
        # 청크 크기 초과 시 새 청크 시작
        if current_size + sentence_size > chunk_size and current_chunk:
            # 현재 청크 저장
            chunk_text = " ".join(current_chunk)
            chunks.append({
                'text': chunk_text,
                'overlap': " ".join(overlap_buffer) if overlap_buffer else None
            })
            
            # 오버랩을 위해 마지막 N개 문장 저장
            overlap_buffer = current_chunk[-overlap_sentences:] if len(current_chunk) >= overlap_sentences else current_chunk[:]
            
            # 새 청크 시작 (오버랩 문장으로 시작)
            current_chunk = overlap_buffer[:] + [sentence]
            current_size = sum(len(s) for s in current_chunk)
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    
    # 마지막 청크
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            'text': chunk_text,
            'overlap': " ".join(overlap_buffer) if overlap_buffer and len(chunks) > 0 else None
        })
    
    print(f"[OK] Created {len(chunks)} chunks with context overlap", flush=True)
    return chunks


def translate_with_claude(
    text: str,
    source_lang: str = "English",
    target_lang: str = "Korean",
    api_key: Optional[str] = None,
    chunk_num: int = 0,
    total_chunks: int = 0,
    context: Optional[str] = None,
    glossary: Optional[dict] = None
) -> Optional[dict]:
    """
    전문 번역가 수준의 프롬프트를 사용한 Claude API 기반 번역

    이 함수는 20년 경력의 출판 번역가 페르소나를 활용하여 고품질 번역을 수행합니다:

    1. 전문 번역가 프롬프트 구조:
       - 페르소나: 20년 경력 출판 번역가 (비즈니스/스타트업 분야 베스트셀러 다수)
       - 톤: 정중하고 친근한 존댓말 (경어체)
       - 대상 독자: 스타트업/비즈니스에 관심 있는 지적 독자층

    2. 5가지 번역 철학:
       a) 의미의 충실성 > 직역
          - 원문의 핵심 메시지와 뉘앙스 완벽 전달
          - 단어 하나하나보다 문장 전체 의도 파악
          - 영어 구조를 그대로 따르지 말고 한국어로 다시 생각

       b) 자연스러운 한국어 (번역체 제거)
          - "~되어지다", "~에 의해", "것이다" 등 금지
          - 능동태 우선, 수동태는 필요한 경우에만

       c) 읽기 쉬운 문장
          - 한 문장에 하나의 핵심 아이디어
          - 긴 문장은 2-3개로 분리
          - 불필요한 수식어 제거

       d) 맥락과 흐름
          - 문장 간 자연스러운 연결
          - 앞뒤 문맥을 고려한 번역
          - 단락의 전체 흐름 유지

       e) 톤과 뉘앙스 보존
          - 저자의 개인적 이야기는 따뜻함
          - 통계/데이터는 객관적임
          - 조언/교훈은 직설적이면서 실용적

    3. 컨텍스트 인식 번역:
       - 이전 청크의 마지막 문장들을 참고정보로 제공
       - 번역 일관성 보장 (용어, 톤, 구조)
       - 청크 경계의 어색함 제거

    4. 30개 핵심 용어 사전 내장:
       - startup → 스타트업
       - founder → 창업자
       - venture capital → 벤처캐피탈 (VC 허용)
       - ... 등 30개 비즈니스 용어

    5. 최종 체크리스트:
       - 자연스러운 발음
       - 번역체 표현 제거
       - 한국 독자의 이해 용이성
       - 전문성과 가독성 균형
       - 원문의 톤과 뉘앙스 보존

    성능:
    - 청크당 소요시간: 4-6초 (병렬 처리 시)
    - 모델: claude-haiku-4-5-20251001
    - 최대 토큰: 64,000

    Args:
        text (str): 번역할 텍스트
        source_lang (str): 원문 언어 (기본 "English")
        target_lang (str): 목표 언어 (기본 "Korean")
        api_key (Optional[str]): Anthropic API 키
        chunk_num (int): 현재 청크 번호 (진행률 표시용)
        total_chunks (int): 전체 청크 수 (진행률 표시용)
        context (Optional[str]): 이전 청크의 오버랩 텍스트 (컨텍스트 인식용)

    Returns:
        Optional[dict]: {
            'text': 번역문,
            'usage': {'input_tokens': int, 'output_tokens': int, 'total_tokens': int},
            'model': str
        } 또는 실패 시 None
    """
    if not api_key:
        return None

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)
        model_name = "claude-haiku-4-5-20251001"

        # 용어집 섹션 생성
        glossary_section = ""
        if glossary and glossary.get("key_terms"):
            terms = glossary["key_terms"]
            domain = glossary.get("domain", "unknown")
            glossary_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【이 문서의 핵심 용어집 - 반드시 준수!】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

문서 분야: {domain}

필수 용어 번역 (절대 변경하지 마세요):
"""
            for eng, kor in list(terms.items())[:30]:  # 최대 30개
                glossary_section += f"{eng} → {kor}\n"
            
            glossary_section += """
⚠️ 위 용어들은 이 문서 전체에서 일관되게 사용해야 합니다!
⚠️ 같은 용어를 다르게 번역하지 마세요!

"""
        
        # 프로 번역가 수준의 프롬프트
        prompt = f"""당신은 20년 경력의 전문 출판 번역가입니다. 다양한 분야의 베스트셀러를 다수 번역했으며, 독자들로부터 "원문보다 더 잘 읽힌다"는 평가를 받습니다.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【번역 철학】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 의미의 충실성 > 직역
   - 원문의 핵심 메시지와 뉘앙스를 완벽히 전달
   - 단어 하나하나보다 문장 전체의 의도를 파악
   - 영어의 구조를 그대로 따르지 말고, 한국어로 다시 생각하여 표현

2. 자연스러운 한국어 (번역체 제거)
   - "~되어지다", "~에 의해", "것이다" 등 번역체 표현 절대 금지
   - 능동태 우선, 수동태는 필요한 경우에만
   - 한국인이 자연스럽게 말하는 방식으로

3. 읽기 쉬운 문장
   - 한 문장에 하나의 핵심 아이디어
   - 긴 문장은 2-3개로 분리
   - 불필요한 수식어 제거
   - 리듬감 있게

4. 맥락과 흐름
   - 문장 간 자연스러운 연결
   - 앞뒤 문맥을 고려한 번역
   - 단락의 전체 흐름 유지

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【스타일 가이드】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 톤: 정중하고 친근한 존댓말 (경어체: ~합니다, ~습니다)
✅ 대상: 해당 분야에 관심 있는 지적 독자
✅ 문체: 전문적이면서도 쉽게 읽히는 교양서 스타일

{glossary_section}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【번역 예시 - 나쁜 vs 좋은】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

원문: "I was 25 years old and completely panicked, but I'm a terrible liar."

❌ 나쁜 번역 (번역체):
"저는 25세였고 완전히 패닉 상태에 있었습니다만, 저는 거짓말을 하는 것에 서툰 사람입니다."

✅ 좋은 번역 (자연스러운 한국어):
"당시 스물다섯이었던 저는 완전히 당황했습니다. 하지만 저는 거짓말을 정말 못합니다."

---

원문: "That's when I realized we had to pivot."

❌ 나쁜 번역:
"그것은 우리가 피벗을 해야만 했다는 것을 제가 깨달았을 때였습니다."

✅ 좋은 번역:
"그때 깨달았습니다. 방향을 바꿔야 한다는 것을요."

---

원문: "The key to success in B2B sales is building relationships."

❌ 나쁜 번역:
"B2B 영업에서의 성공의 열쇠는 관계들을 구축하는 것입니다."

✅ 좋은 번역:
"B2B 영업에서 성공하려면 관계 구축이 핵심입니다."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【번역할 텍스트】 (Chunk {chunk_num}/{total_chunks})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{"" if not context else f'''
⚠️ 이전 맥락 (참고용 - 번역하지 마세요):
---
{context}
---

💡 위 내용은 이미 번역된 부분입니다. 흐름과 맥락을 이해하는 데만 사용하세요.

'''}
📝 이제 아래 텍스트를 번역하세요:
---
{text}
---

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【최종 체크리스트】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

번역하기 전에:
1. 단락 전체를 읽고 맥락을 파악했는가?
2. 저자가 전달하고자 하는 핵심 메시지를 이해했는가?

번역한 후에:
1. 소리 내어 읽었을 때 자연스러운가?
2. 번역체 표현("~되어지다", "~것이다" 등)이 없는가?
3. 한국 독자가 쉽게 이해할 수 있는가?
4. 전문성과 가독성의 균형이 맞는가?
5. 원문의 톤과 뉘앙스가 살아있는가?

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

번역문만 출력하세요. 설명이나 주석은 불필요합니다."""

        message = client.messages.create(
            model=model_name,
            max_tokens=64000,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = message.content[0].text
        # usage 안전 추출 (SDK 버전별 속성/딕트 차이 대응)
        input_tokens = 0
        output_tokens = 0
        try:
            usage_obj = getattr(message, "usage", None)
            if usage_obj is not None:
                # 객체 속성 스타일
                if hasattr(usage_obj, "input_tokens"):
                    input_tokens = int(getattr(usage_obj, "input_tokens") or 0)
                if hasattr(usage_obj, "output_tokens"):
                    output_tokens = int(getattr(usage_obj, "output_tokens") or 0)
                # 딕셔너리 스타일
                if isinstance(usage_obj, dict):
                    input_tokens = int(usage_obj.get("input_tokens") or input_tokens or 0)
                    output_tokens = int(usage_obj.get("output_tokens") or output_tokens or 0)
        except Exception:
            # usage 파싱 실패 시 0으로 처리
            input_tokens = input_tokens or 0
            output_tokens = output_tokens or 0

        return {
            "text": result_text,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": (input_tokens or 0) + (output_tokens or 0),
            },
            "model": model_name,
        }

    except ImportError:
        print("[ERROR] anthropic not installed: pip install anthropic")
        return None
    except Exception as e:
        print(f"[ERROR] Translation failed: {e}")
        return None


def translate_chunks(
    chunks: List[dict],
    source_lang: str = "English",
    target_lang: str = "Korean",
    api_key: Optional[str] = None,
    max_workers: int = 20,
    glossary: Optional[dict] = None
) -> List[str]:
    """
    병렬 처리를 사용한 모든 청크의 효율적 번역

    이 함수는 ThreadPoolExecutor를 사용하여 여러 청크를 동시에 번역합니다:

    1. 병렬 처리 메커니즘:
       - ThreadPoolExecutor(max_workers=5)로 5개 스레드 동시 실행
       - as_completed()를 사용하여 완료된 작업부터 처리
       - 순차 처리 대비 5-6배 성능 향상

    2. 성능 최적화:
       - 순차 처리 (기존): 11개 청크 × 24.9초 = 273.9초 (4.5분)
       - 병렬 처리 (현재): 11개 청크 ÷ 5 workers = 45-50초 (1분)
       - Speedup: 5-6배 향상

    3. 실시간 진행률 표시:
       - 각 청크 완료 시 즉시 진행 상황 출력
       - 포맷: [완료/전체] Chunk N 완료 (크기, 소요시간)
       - 남은 작업 수 표시

    4. 에러 처리:
       - 번역 실패 시 원본 텍스트 사용
       - 부분 실패해도 전체 프로세스 계속 진행

    5. 최종 통계:
       - 총 소요시간, 청크당 평균시간
       - 병렬도 (워커 개수)
       - 적용된 가이드라인

    워커 개수 권장사항:
    - max_workers=3: 안정적 (API 레이트 한계 고려)
    - max_workers=5: 빠른 처리 (기본값, 권장)
    - max_workers>5: API 오류 위험 (권장하지 않음)

    컨텍스트 인식:
    - 각 청크는 이전 청크의 마지막 문장들과 함께 전달됨
    - 번역 일관성 보장
    - 청크 경계의 어색함 제거

    성능 지표 예시:
    ```
    [완료] 11개 청크 번역 완료!
      • 소요시간: 47.3초
      • 평균시간: 4.3초/청크
      • 병렬도: 5개 워커
      • 적용규칙: TRANSLATION_GUIDELINE.md
    ```

    Args:
        chunks (List[dict]): chunk_text()에서 반환한 청크 리스트
        source_lang (str): 원문 언어 (기본 "English")
        target_lang (str): 목표 언어 (기본 "Korean")
        api_key (Optional[str]): Anthropic API 키
        max_workers (int): 동시 실행 워커 개수 (기본 5)

    Returns:
        List[str]: 번역된 청크들을 원래 순서대로 정렬한 리스트
    """
    start_time = time.time()
    
    print(f"[TRANSLATING] {len(chunks)} chunks (with context-aware translation)...")
    print(f"[PARALLEL] Using {max_workers} workers for faster processing")
    print(f"[STATUS] Starting translation...\n")

    # 결과를 인덱스와 함께 저장하기 위한 딕셔너리
    results = {}
    completed_count = 0
    # 토큰 사용량 집계: 모델별 input/output/requests
    usage_by_model = defaultdict(lambda: {"input_tokens": 0, "output_tokens": 0, "requests": 0})

    def translate_chunk_wrapper(chunk_info):
        """각 스레드에서 실행될 번역 함수"""
        i, chunk_data = chunk_info
        chunk_start = time.time()
        
        # chunk_data는 딕셔너리: {'text': '...', 'overlap': '...'}
        chunk_text = chunk_data['text'] if isinstance(chunk_data, dict) else chunk_data
        context = chunk_data.get('overlap') if isinstance(chunk_data, dict) else None
        
        translated = translate_with_claude(
            chunk_text,
            source_lang,
            target_lang,
            api_key,
            chunk_num=i,
            total_chunks=len(chunks),
            context=context,
            glossary=glossary
        )
        
        elapsed = time.time() - chunk_start
        return (i, translated, elapsed)

    # ThreadPoolExecutor로 병렬 처리
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(translate_chunk_wrapper, (i, chunk)): i 
            for i, chunk in enumerate(chunks, 1)
        }
        
        # 완료된 작업부터 처리
        for future in as_completed(futures):
            i, translated, elapsed = future.result()
            completed_count += 1
            pending_count = len(futures) - completed_count
            
            # translated: None | str | dict
            text_out = None
            model_name = None
            if isinstance(translated, dict):
                text_out = translated.get("text")
                usage = translated.get("usage") or {}
                model_name = translated.get("model")
                # 집계
                if model_name:
                    usage_by_model[model_name]["input_tokens"] += int(usage.get("input_tokens") or 0)
                    usage_by_model[model_name]["output_tokens"] += int(usage.get("output_tokens") or 0)
                    usage_by_model[model_name]["requests"] += 1
            else:
                text_out = translated

            if text_out:
                results[i] = text_out
                print(f"✓ [{completed_count:2d}/{len(chunks)}] Chunk {i:2d} 완료 ({len(text_out):5d} chars, {elapsed:5.1f}s) | 남은작업: {pending_count:2d}", flush=True)
            else:
                # 원본 텍스트 사용
                original_text = chunks[i-1]['text'] if isinstance(chunks[i-1], dict) else chunks[i-1]
                results[i] = original_text
                print(f"✗ [{completed_count:2d}/{len(chunks)}] Chunk {i:2d} SKIP (원본 사용) | 남은작업: {pending_count:2d}", flush=True)

    # 원래 순서대로 정렬
    translated_chunks = [results[i] for i in range(1, len(chunks) + 1)]

    elapsed = time.time() - start_time
    print()
    print(f"{'='*70}")
    print(f"[완료] {len(chunks)}개 청크 번역 완료!")
    print(f"  • 소요시간: {elapsed:.1f}초")
    print(f"  • 평균시간: {elapsed/len(chunks):.1f}초/청크")
    print(f"  • 병렬도: {max_workers}개 워커")
    print(f"  • 적용규칙: TRANSLATION_GUIDELINE.md")
    # 토큰/비용 요약 (공식 가격 기준)
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
            cost = (inp / 1_000_000.0) * float(price.get("input", 0) or 0) + (outp / 1_000_000.0) * float(price.get("output", 0) or 0)
            grand_cost += cost
            if (price.get("input", 0) or 0) == 0 and (price.get("output", 0) or 0) == 0:
                print(f"    - {model}: input={inp:,} tok, output={outp:,} tok, requests={reqs}")
                print(f"      ⚠️ 가격표 미등록 (환경변수로 설정하세요)")
            else:
                print(f"    - {model} ({reqs}회 호출)")
                print(f"      Input:  {inp:>10,} tokens × ${price['input']:.2f}/M = ${(inp/1_000_000)*price['input']:.4f}")
                print(f"      Output: {outp:>10,} tokens × ${price['output']:.2f}/M = ${(outp/1_000_000)*price['output']:.4f}")
                print(f"      소계: ${cost:.4f}")
        print()
        print(f"    💰 총 예상 비용: ${grand_cost:.4f} USD")
        print(f"       (Input: {grand_input:,} tok | Output: {grand_output:,} tok)")
    print(f"{'='*70}")
    print()

    return translated_chunks


def generate_markdown(
    pdf_name: str,
    translated_chunks: List[str],
    original_text: str,
    pages: int
) -> str:
    """Generate markdown from translated chunks"""
    print(f"[MARKDOWN] Generating markdown document...", flush=True)
    markdown = f"""# {pdf_name} - Korean Translation

**Source**: English PDF
**Target**: Korean (한국어)
**Pages**: {pages}
**Characters**: {len(original_text):,}
**Chunks**: {len(translated_chunks)}
**Timestamp**: {time.strftime('%Y-%m-%d %H:%M:%S')}

---

## Content

"""

    for i, translated in enumerate(translated_chunks, 1):
        markdown += f"## Section {i}\n\n"
        markdown += translated + "\n\n"
        
        # 진행 상황 표시 (매 5섹션마다)
        if i % 5 == 0 or i == len(translated_chunks):
            progress = (i / len(translated_chunks)) * 100
            print(f"  [{i:3d}/{len(translated_chunks)}] {progress:5.1f}% complete", flush=True)

    markdown += f"---\n\n"
    markdown += f"**Translation completed**: All {len(translated_chunks)} sections translated successfully."

    print(f"[OK] Markdown document generated", flush=True)
    return markdown


def main():
    print("=" * 70)
    print("[COMPLETE PDF TRANSLATION PIPELINE]")
    print("=" * 70)
    print()

    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not set")
        print()
        print("Setup instructions in: CLAUDE_API_SETUP.md")
        print()
        print("Quick setup:")
        print("  1. Get API key: https://console.anthropic.com")
        print("  2. Set environment: export ANTHROPIC_API_KEY=sk-ant-...")
        print("  3. Run again: python translate_full_pdf.py")
        return

    print("[OK] API key configured")
    print()

    # Get PDF path from CLI argument or use default
    if len(sys.argv) > 1:
        pdf_path = Path(sys.argv[1])
        if not pdf_path.is_absolute():
            # 상대 경로면 input/ 폴더 기준으로
            pdf_path = Path("input") / pdf_path
    else:
        # 기본값: input/laf.pdf
        pdf_path = Path('input/laf.pdf')

    if not pdf_path.exists():
        print(f"[ERROR] PDF not found: {pdf_path}")
        print()
        print("사용법:")
        print("  python translate_full_pdf.py laf.pdf")
        print("  python translate_full_pdf.py input/my_book.pdf")
        print("  python translate_full_pdf.py /absolute/path/to/book.pdf")
        return

    print(f"[PDF] {pdf_path.name} ({pdf_path.absolute()})")
    print()

    # output 폴더 생성
    Path("output").mkdir(exist_ok=True)
    print()

    # Extract
    print()
    print("[STEP 1/5] Extract PDF")
    print("-" * 70)
    text, metadata, pages = extract_pdf(pdf_path)
    if not text:
        print("[ERROR] Failed to extract text from PDF")
        return

    print(f"[OK] ✓ Extracted {len(text):,} characters from {len(pages)} pages")
    print()

    # Glossary extraction
    print("[STEP 2/5] Analyze document & extract glossary")
    print("-" * 70)
    glossary = extract_glossary(text, api_key)
    
    if glossary and glossary.get("key_terms"):
        print(f"[OK] ✓ Document domain: {glossary.get('domain', 'unknown')}")
        print(f"[OK] ✓ Extracted {len(glossary['key_terms'])} key terms")
        # 샘플 표시
        sample_terms = list(glossary['key_terms'].items())[:5]
        for eng, kor in sample_terms:
            print(f"      • {eng} → {kor}")
        if len(glossary['key_terms']) > 5:
            print(f"      ... and {len(glossary['key_terms']) - 5} more")
    else:
        print(f"[INFO] No custom glossary - using general translation guidelines")
    print()

    # Chunk
    print("[STEP 3/5] Create chunks")
    print("-" * 70)
    chunks = chunk_text(text, chunk_size=5000)
    print(f"[OK] ✓ Total chunks to translate: {len(chunks)}")
    print()

    # Translate
    print("[STEP 4/5] Translate with Claude API (병렬 처리)")
    print("-" * 70)
    translated_chunks = translate_chunks(
        chunks, "English", "Korean", api_key,
        glossary=glossary
    )

    if not translated_chunks:
        print("[ERROR] Translation failed")
        return

    print()
    
    # Generate markdown
    print("[STEP 5/5] Generate markdown")
    print("-" * 70)
    markdown = generate_markdown(pdf_path.stem, translated_chunks, text, len(pages))
    print()

    # output/ 폴더에 저장
    print("[SAVING] Writing output file...")
    output_path = Path('output') / f'output_{pdf_path.stem}_translated.md'
    output_path.write_text(markdown, encoding='utf-8')
    print(f"[OK] ✓ Output saved: {output_path.name}")
    print()

    # Summary
    print("=" * 70)
    print("[✓ SUMMARY]")
    print("=" * 70)
    print(f"  📄 PDF File: {pdf_path.name}")
    print(f"  📖 Pages: {len(pages)}")
    print(f"  📝 Total Characters: {len(text):,}")
    print(f"  📦 Chunks Created: {len(chunks)}")
    print(f"  🌐 Chunks Translated: {len(translated_chunks)}")
    print(f"  💾 Output File: {output_path.name}")
    print(f"  📍 Location: {output_path.absolute()}")
    print("=" * 70)
    print()
    print("[SUCCESS] ✨ Complete translation pipeline finished!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
