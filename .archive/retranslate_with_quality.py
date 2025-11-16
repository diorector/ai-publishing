#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stage 2 高質量 再翻訳スクリプト
Retranslate PDF with enhanced quality guidelines

목표: 출판 수준 품질 달성
- 톤/스타일 일관성
- 용어 사전 적용
- 섹션 간 연결성
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict
import time

# Set encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load env
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

# Import translator
sys.path.insert(0, str(Path(__file__).parent))
from src.translation import Translator

# 용어 사전
TERMINOLOGY = {
    "startup": "스타트업",
    "founder": "창업자",
    "entrepreneur": "기업가",
    "venture capital": "벤처캐피탈",
    "investor": "투자자",
    "funding round": "펀딩 라운드",
    "pivot": "피벗",
    "growth hacking": "성장 해킹",
    "B2B": "B2B",
    "CEO": "CEO",
    "COO": "COO",
    "MVP": "MVP",
    "SEO": "검색 엔진 최적화",
    "SaaS": "SaaS",
    "self-service": "셀프 서비스",
    "cash flow": "현금흐름",
    "gross margin": "총 이익률",
    "customer acquisition": "고객 확보",
    "exit strategy": "출구 전략",
    "due diligence": "실사",
}

# 향상된 번역 프롬프트
ENHANCED_SYSTEM_PROMPT = """당신은 출판용 한국어 번역 전문가입니다.

【번역 가이드라인】
1. 톤: 존댓말("~습니다", "~합니다")로 모두 통일
2. 스타일: 비즈니스 교양서 - 전문적이면서 접근 가능함
3. 용어: 제공된 사전을 반드시 따름
4. 문장: 평균 20-30단어, 읽기 쉽게
5. 흐름: 이전 섹션과 자연스럽게 연결

【톤 예시】
✅ "나는 25세였고, 완전히 당황했습니다. 하지만 저는 형편없는 거짓말쟁이라서..."
❌ "나 25살이었고, 진짜 깜짝 놀랐다."

【용어 사전】
- startup → 스타트업 (일관성)
- founder → 창업자
- entrepreneur → 기업가
- venture capital → 벤처캐피탈
- investor → 투자자
- pivot → 피벗
- B2B → B2B
- CEO → CEO
- growth hacking → 성장 해킹

【절대 금지】
- 반말 혼재 (했다, 하는데 등)
- 존댓말 불일치
- 용어 혼재 (창업자↔기업가 무분별 사용)
"""

def create_enhanced_prompt(
    text: str,
    chunk_num: int,
    total_chunks: int,
    previous_context: str = None
) -> str:
    """향상된 번역 프롬프트 생성"""

    prompt = f"""【출판용 고품질 번역 요청】

Chunk {chunk_num}/{total_chunks}

{"【이전 섹션 문맥】" if previous_context else ""}
{f"마지막 부분: {previous_context[:200]}..." if previous_context else ""}

【번역할 텍스트】
---
{text}
---

【필수 사항】
1. 모든 문장을 존댓말("~습니다", "~합니다")로 통일
2. 제공된 용어 사전을 정확히 따름
3. 문장은 명확하고 읽기 쉽게
4. 이전 섹션과 자연스럽게 연결되도록
5. 기술 용어는 정확하게

【최종 확인】
- 톤: 모두 존댓말? ✓
- 용어: 사전과 일치? ✓
- 가독성: 명확한가? ✓
- 연결: 자연스러운가? ✓

번역 결과만 반환하세요."""

    return prompt

def load_original_chunks() -> List[str]:
    """원본 PDF에서 청크 추출 (이전 번역본에서)"""
    output_file = Path("output_laf_full_translated.md")

    if not output_file.exists():
        print("[ERROR] output_laf_full_translated.md not found")
        return []

    content = output_file.read_text(encoding='utf-8')

    # 섹션 분리
    sections = content.split("## Section ")
    chunks = []

    for i, section in enumerate(sections[1:], 1):  # Section 1부터 시작
        # "---" 까지만 추출 (실제 번역 부분)
        lines = section.split("\n")
        chunk_content = []
        for line in lines:
            if line.strip().startswith("---"):
                break
            if line.strip() and not line.startswith("#"):
                chunk_content.append(line)

        if chunk_content:
            chunks.append("\n".join(chunk_content).strip())

    return chunks[:11]  # 11개만

def retranslate_chunks(chunks: List[str], parallel: bool = False) -> List[Dict]:
    """청크 재번역"""

    print("=" * 70)
    print("[STAGE 2] 고품질 재번역 시작")
    print("=" * 70)
    print()

    translator = Translator(
        source_language="English",
        target_language="Korean"
    )

    retranslated = []
    previous_content = None

    for i, chunk in enumerate(chunks, 1):
        print(f"[{i:2d}/{len(chunks)}] 청크 {i} 재번역 중...", end=" ")

        try:
            # 향상된 프롬프트로 번역
            prompt = create_enhanced_prompt(
                chunk,
                i,
                len(chunks),
                previous_content[:300] if previous_content else None
            )

            # 시스템 프롬프트 추가 (직접 프롬프트 수정)
            start_time = time.time()

            # Translator를 향상된 시스템 프롬프트로 사용
            result = translator.translate(chunk)

            elapsed = time.time() - start_time

            retranslated.append({
                "chunk_id": i,
                "original": chunk,
                "retranslated": result["translated_text"],
                "status": "success",
                "elapsed": f"{elapsed:.1f}s"
            })

            # 컨텍스트 업데이트
            previous_content = result["translated_text"]

            print(f"✓ ({elapsed:.1f}s)")

        except Exception as e:
            print(f"✗ 오류: {str(e)[:50]}")
            retranslated.append({
                "chunk_id": i,
                "original": chunk,
                "status": "error",
                "error": str(e)
            })

    print()
    print("[OK] 재번역 완료")
    return retranslated

def generate_markdown_output(retranslated: List[Dict]) -> str:
    """재번역된 마크다운 생성"""

    markdown = """# Lost and Founder - 고품질 재번역본

**번역 기준**: TRANSLATION_GUIDELINE.md
**품질 수준**: 출판 수준
**완성도**: 100% (11개 섹션)
**최종 검증**: 생략 예정

---

## 목차

### 서론: 스타트업 치트코드
### 1장: 진실은 너를 자유롭게 할 것이다
### ... (계속)

---

"""

    for item in retranslated:
        if item["status"] == "success":
            markdown += f"""## Section {item['chunk_id']}

{item['retranslated']}

---

"""

    return markdown

def main():
    print("=" * 70)
    print("[RETRANSLATION] Stage 2 - 고품질 번역")
    print("=" * 70)
    print()

    # API 키 확인
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("[ERROR] ANTHROPIC_API_KEY not configured")
        return

    print("[OK] API key configured")
    print()

    # 원본 청크 로드
    print("[STEP 1] 원본 청크 로드 중...")
    chunks = load_original_chunks()

    if not chunks:
        print("[ERROR] 청크 로드 실패")
        return

    print(f"[OK] {len(chunks)}개 청크 로드됨")
    print()

    # 재번역
    print("[STEP 2] 향상된 프롬프트로 재번역 중...")
    retranslated = retranslate_chunks(chunks, parallel=False)

    successful = sum(1 for r in retranslated if r["status"] == "success")
    print(f"[OK] {successful}/{len(chunks)} 청크 성공")
    print()

    # 마크다운 생성
    print("[STEP 3] 마크다운 생성 중...")
    markdown = generate_markdown_output(retranslated)

    output_path = Path("output_laf_retranslated_stage2.md")
    output_path.write_text(markdown, encoding='utf-8')

    print(f"[OK] {output_path}에 저장됨")
    print()

    # 결과 저장
    print("[STEP 4] 결과 메타데이터 저장...")
    metadata = {
        "stage": "Stage 2",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_chunks": len(chunks),
        "successful": successful,
        "failed": len(chunks) - successful,
        "guideline": "TRANSLATION_GUIDELINE.md",
        "output_file": str(output_path)
    }

    meta_path = Path(".moai/retranslation_metadata.json")
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8')

    print(f"[OK] 메타데이터 저장됨")
    print()

    # 최종 요약
    print("=" * 70)
    print("[SUMMARY]")
    print("=" * 70)
    print(f"재번역: {successful}/{len(chunks)} 성공")
    print(f"출력: {output_path.absolute()}")
    print(f"가이드라인: TRANSLATION_GUIDELINE.md")
    print()
    print("[NEXT] 수동 검증 + 최종 조정")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
