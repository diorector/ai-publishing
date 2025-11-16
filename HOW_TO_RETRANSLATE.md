# 고품질 PDF 번역 가이드

## 📌 개요

**Lost and Founder** 한국어 번역 프로젝트의 출판 품질 재번역 가이드입니다.

- **현재 상태**: 35페이지 PDF 완전 번역됨 (향상된 품질 기준 적용)
- **프로세스**: Claude API + 출판 가이드라인 기반
- **소요 시간**: ~4-5분 (11개 청크)
- **품질 수준**: 출판 수준

---

## 🚀 빠른 시작

### 요구사항

```bash
# 필수 라이브러리
- anthropic >= 0.25.0
- pdfplumber >= 0.10.0
- python-dotenv >= 1.0.0

# 설치
pip install anthropic pdfplumber python-dotenv
```

### API 키 설정

```bash
# .env 파일 생성 또는 환경 변수 설정
export ANTHROPIC_API_KEY=sk-ant-...

# 또는 .env 파일
ANTHROPIC_API_KEY=sk-ant-...
```

### 번역 실행

```bash
# 가장 간단한 방법
python translate_full_pdf.py

# 출력
# - output_laf_full_translated.md (한국어 번역본)
```

---

## 📋 번역 프로세스

### Phase 1: PDF 추출

```
laf.pdf (35페이지)
  ↓
텍스트 추출 (50,898자)
  ↓
메타데이터 수집
```

### Phase 2: 텍스트 청킹

```
전체 텍스트 (50,898자)
  ↓
5,000자 단위로 분할
  ↓
11개 청크 생성
```

### Phase 3: 고품질 번역

```
각 청크 (i/11)
  ↓
향상된 프롬프트 적용 (출판 기준)
  ↓
Claude Haiku API 호출
  ↓
한국어 번역 (존댓말, 일관성 있는 용어)
```

### Phase 4: 마크다운 생성

```
11개 번역 청크
  ↓
마크다운 형식 통합
  ↓
output_laf_full_translated.md
```

---

## 🎯 출판 품질 기준

### 적용된 가이드라인

`TRANSLATION_GUIDELINE.md`를 따릅니다:

```
【톤】
✅ 존댓말 통일: "~습니다", "~합니다"
✅ 전문적이면서 접근 가능함
✅ 저자의 개인 이야기 + 조언 균형

【용어 사전】
startup → 스타트업
founder → 창업자
entrepreneur → 기업가
venture capital → 벤처캐피탈
investor → 투자자
... (총 30개)

【문장 기준】
✅ 평균 20-30단어
✅ 명확하고 읽기 쉬움
✅ 원문 포맷 유지
```

---

## 📂 프로젝트 구조

```
ai-publishing/
├── translate_full_pdf.py           ⭐ 메인 번역 스크립트
├── TRANSLATION_GUIDELINE.md        ⭐ 출판 가이드라인
├── HOW_TO_RETRANSLATE.md          (이 파일)
├── output_laf_full_translated.md   ⭐ 번역 결과
│
├── src/
│   ├── translation/translator.py   ⭐ Translator 클래스 (Claude API)
│   ├── orchestrator.py             ⭐ 파이프라인 조율
│   ├── pdf_processor/              PDF 추출
│   ├── chunking/                   청킹 로직
│   ├── quality/                    품질 검사
│   └── markdown/                   마크다운 생성
│
├── .archive/                       정리된 파일들
└── tests/                          테스트 케이스 (225개)
```

---

## 🔄 번역 다시 실행하기

### 상황 1: 프롬프트 수정 후 재번역

```python
# translate_full_pdf.py의 translate_with_claude() 함수 수정
prompt = f"""당신은 출판용 한국어 번역 전문가입니다.

【필수 번역 기준】
1. 톤: 모든 문장을 존댓말("~습니다", "~합니다")로 통일
2. ...
"""

# 실행
python translate_full_pdf.py
```

### 상황 2: 특정 섹션만 재번역

```python
from src.translation import Translator

translator = Translator(
    source_language="English",
    target_language="Korean"
)

# 개별 섹션 번역
result = translator.translate("번역할 텍스트...")
print(result["translated_text"])
```

### 상황 3: 병렬 번역 활성화

```python
from src.translation import Translator

translator = Translator()

# 병렬 처리 (3개 워커)
results = translator.translate_batch(
    chunks,
    parallel=True,
    max_workers=3
)
```

---

## ✅ 품질 검증 체크리스트

번역 완료 후 이를 확인하세요:

```
□ 톤
  □ 모든 문장이 존댓말인가?
  □ "~습니다", "~합니다"로 일관성 있는가?

□ 용어
  □ TRANSLATION_GUIDELINE의 사전을 따랐는가?
  □ 같은 개념이 항상 같은 용어로 표현되는가?

□ 문장
  □ 평균 20-30단어인가?
  □ 어색한 표현이 없는가?
  □ 한 번에 이해 가능한가?

□ 논리
  □ 섹션 간 전환이 자연스러운가?
  □ 앞뒤가 맞는가?

□ 전문성
  □ 기술 용어가 정확한가?
  □ 비즈니스 개념이 정확하게 번역되었는가?
```

---

## 🛠️ 고급 사용

### 커스텀 용어 사전 추가

```python
# translator.py 수정
TERMINOLOGY = {
    "my_term": "내_용어",
    ...
}

# 또는 프롬프트에 직접 추가
prompt = """
【추가 용어 사전】
my_term → 내_용어
...
"""
```

### 번역 결과 후처리

```python
# 존댓말 통일 (정규식)
import re
text = re.sub(r'(.+?)[다했.]$', r'\1습니다', text)

# 용어 통일 (직접 치환)
text = text.replace("기업가", "창업자")
```

### 성능 모니터링

```python
import time

start = time.time()
result = translator.translate(chunk)
elapsed = time.time() - start

print(f"소요 시간: {elapsed:.1f}s")
print(f"처리량: {len(result['translated_text']) / elapsed:.0f} chars/sec")
```

---

## 📊 성능 지표

### 현재 성능

```
PDF 처리:
- 페이지 수: 35
- 전체 문자 수: 50,898
- 청크 수: 11

번역 성능:
- 총 소요 시간: 273.9초 (~4.5분)
- 청크당 평균: 24.9초
- 처리량: ~186 chars/sec

모드: 순차 처리 (parallel=False)
프롬프트: 향상된 출판 기준 (TRANSLATION_GUIDELINE)
```

### 병렬 처리 성능 (예상)

```
3개 워커 병렬 처리:
- 예상 소요 시간: ~90-120초 (3배 향상)
- 주의: API 레이트 한계 확인 필요
```

---

## 📝 파일별 역할

| 파일 | 역할 | 수정 필요 |
|------|------|---------|
| `translate_full_pdf.py` | 메인 파이프라인 | ⭐ 프롬프트 수정 가능 |
| `src/translation/translator.py` | Claude API 호출 | 🔧 고급 옵션 |
| `src/orchestrator.py` | 병렬화 설정 | 🔧 고급 옵션 |
| `TRANSLATION_GUIDELINE.md` | 번역 기준 | ✏️ 가이드라인 수정 |
| `output_laf_full_translated.md` | 번역 결과 | 📄 읽기용 |

---

## 🚨 문제 해결

### "ANTHROPIC_API_KEY not set" 오류

```bash
# 해결
export ANTHROPIC_API_KEY=sk-ant-...
python translate_full_pdf.py
```

### 번역이 너무 느림

```python
# 해결 1: 병렬 처리 활성화
# translate_full_pdf.py에서:
translated_chunks = translate_chunks(
    chunks,
    parallel=True,
    max_workers=3
)

# 해결 2: 청크 크기 증가 (문맥 손실 가능)
chunks = chunk_text(text, chunk_size=8000)  # 기본 5000
```

### 번역 품질이 낮음

```python
# 해결: 프롬프트 개선
# translate_full_pdf.py의 translate_with_claude() 함수 수정
# TRANSLATION_GUIDELINE 검증
```

---

## 📚 추가 리소스

- `TRANSLATION_GUIDELINE.md` - 상세 번역 기준
- `src/translation/translator.py` - Translator 클래스 구현
- `tests/` - 225개 테스트 케이스 (참고용)
- `.archive/` - 이전 버전 및 실험 파일들

---

## 💡 팁

1. **첫 실행**: 순차 처리로 시작 (안정성)
2. **반복 개선**: 프롬프트 수정 후 재번역
3. **품질 검증**: 체크리스트로 검증
4. **병렬화**: 안정화 후 활성화

---

**마지막 업데이트**: 2025-11-16
**버전**: 2.0 (Stage 2 - 고품질 재번역)
**상태**: 준비 완료 ✅
