# 병렬 Chapter 번역 가이드

## 개요

`translate_parallel_chapters.py`는 PDF를 Chapter별로 분할한 후 **동시에 10개씩 병렬 번역**하여 시간을 10배 단축합니다.

- ⚡ **동시 번역**: 10개 Chapter 동시 처리
- 📊 **실시간 진행**: 진행 상황 실시간 표시
- 📁 **독립 파일**: 각 Chapter별 별개 MD 파일 생성
- 🔀 **자동 분할**: 큰 Chapter는 1-1, 1-2로 자동 분할

---

## 설치 및 준비

### 1단계: 의존성 설치

```bash
pip install -r requirements.txt
# 또는
pip install pdfplumber anthropic python-dotenv
```

### 2단계: API 키 설정 (선택)

```bash
# .env 파일에 추가
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

API 키가 없으면 원문 그대로 처리됩니다.

---

## 실행 방법

### 기본 실행

```bash
python translate_parallel_chapters.py
```

### 실행 결과

```
================================================================================
[PARALLEL CHAPTER TRANSLATION WITH PROGRESS]
================================================================================

[STEP 1] Detect PDF structure
-----------...
[OK] Extracted 827 items

[STEP 2] Split into chapters
-----------...
[OK] Split into 12 chapters

[CHAPTERS TO TRANSLATE]
-----------...
  [ 1] CHAPTER 1                          ( 65 items,  45000 chars)
  [ 2] CHAPTER 1-2                        ( 58 items,  42000 chars)
  [ 3] CHAPTER 2                          ( 70 items,  50000 chars)
  ...
  [12] CHAPTER 5                          ( 45 items,  32000 chars)

[STEP 3] Parallel translation (10 workers)
-----------...

[ 1/12] CHAPTER 1                    [ 8.3%]      5.2s / ETA   57.1s
[ 2/12] CHAPTER 2                    [16.7%]     10.4s / ETA   51.9s
[ 3/12] CHAPTER 1-2                  [25.0%]     12.1s / ETA   36.4s
[ 4/12] CHAPTER 3                    [33.3%]     15.8s / ETA   31.6s
...
[12/12] CHAPTER 5                    [100.0%]    45.2s / ETA    0.0s

[OK] All chapters translated

================================================================================
[SUMMARY]
================================================================================
[OK] Total chapters: 12
[OK] Translated: 12
[OK] Output directory: C:\Users\dio9\Desktop\moaicamp\ai-publishing\output_chapters

[OUTPUT FILES]
-----------...
  ✓ chapter_CHAPTER_1.md                         ( 45.2 KB)
  ✓ chapter_CHAPTER_1_2.md                       ( 42.1 KB)
  ✓ chapter_CHAPTER_2.md                         ( 50.3 KB)
  ✓ chapter_CHAPTER_3.md                         ( 38.5 KB)
  ...
  ✓ chapter_CHAPTER_5.md                         ( 32.8 KB)

[SUCCESS] Translation complete!
```

---

## 출력 파일 사용

### 개별 Chapter 확인

```bash
# Chapter 1 확인
cat output_chapters/chapter_CHAPTER_1.md

# Chapter 1-2 (분할된 부분) 확인
cat output_chapters/chapter_CHAPTER_1_2.md
```

### 모든 파일 병합 (선택)

```bash
# 모든 chapter를 순서대로 병합
cat output_chapters/*.md > full_book.md

# Windows에서
type output_chapters\*.md > full_book.md
```

### 파일 목록 확인

```bash
# 생성된 파일 확인
ls -lh output_chapters/

# Windows에서
dir output_chapters\
```

---

## 파일명 규칙

| Chapter 이름 | 파일명 | 설명 |
|-------------|--------|------|
| CHAPTER 1 | chapter_CHAPTER_1.md | 기본 Chapter |
| CHAPTER 1 (분할-1) | chapter_CHAPTER_1_1.md | 첫 번째 분할 |
| CHAPTER 1 (분할-2) | chapter_CHAPTER_1_2.md | 두 번째 분할 |
| INTRODUCTION | chapter_INTRODUCTION.md | 소개 섹션 |

---

## 성능 비교

| 방식 | 시간 | 병렬도 |
|------|------|--------|
| 순차 번역 | ~450초 | 1개 |
| **병렬 번역** | **~45초** | **10개** |
| **시간 단축** | **90%** | **10배** |

---

## 진행 상황 표시 설명

```
[ 1/12] CHAPTER 1                    [ 8.3%]      5.2s / ETA   57.1s
│      │                             │         │          │
│      │                             │         │          └─ 남은 예상 시간
│      │                             │         └─ 경과 시간
│      │                             └─ 진행률 (%)
│      └─ Chapter 이름 (30자 고정)
└─ 진행 상황 (완료/전체)
```

---

## 트러블슈팅

### API 키 없음 경고

```
[WARNING] No API key set - using original text
```

**해결**: .env 파일에 `ANTHROPIC_API_KEY=sk-ant-xxxxx` 추가

### PDF 읽기 오류

```
[ERROR] pdfplumber not installed
```

**해결**: `pip install pdfplumber`

### 느린 번역

- 첫 몇 개 Chapter는 느릴 수 있습니다 (Claude API 워밍업)
- 이후 속도 개선됩니다

---

## 고급 사용법

### Chapter 크기 수정

`translate_parallel_chapters.py`의 `split_large_chapter()` 함수에서:

```python
split_large_chapter(chapter_name, items, max_chars=20000)
#                                        ^^^^^^
#                                        여기 수정 (작을수록 더 분할)
```

### 병렬 워커 수 변경

```python
with ThreadPoolExecutor(max_workers=10) as executor:
#                               ^^
#                               여기 수정 (더 많으면 빠르지만 CPU/API 사용 증가)
```

---

## 다음 단계

1. ✅ **PDF 구조 감지**
2. ✅ **병렬 번역**
3. ✅ **Chapter별 파일 생성**
4. ⏳ **파일 병합** (필요시)
5. ⏳ **최종 정리** (표지, 목차 등)

---

## 문의

질문이나 문제 발생 시:
1. 터미널 출력 확인
2. API 키 설정 확인
3. PDF 파일 유효성 확인
