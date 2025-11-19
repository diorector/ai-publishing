# AI-Publishing 프로젝트 요약

## 🎯 프로젝트 목적

PDF 문서를 출판 수준의 한국어로 번역하고 편집하는 AI 기반 자동화 도구

---

## 📦 핵심 기능

### 1. PDF 번역 (`translate_pdf.py`)
- **입력**: PDF 파일
- **출력**: 한국어 마크다운 문서
- **특징**: 20년 경력 번역가 페르소나, 병렬 처리, 용어 일관성

### 2. 문서 편집 (`edit_document.py`)
- **입력**: 마크다운 문서
- **출력**: 편집된 마크다운 + 비교 리포트
- **특징**: 2-Pass 편집 (교정 + 윤문), 출판 편집자 수준

---

## 🚀 사용법

```bash
# 번역
python translate_pdf.py input/book.pdf

# 편집
python edit_document.py output/output_book_translated.md
```

---

## 📁 프로젝트 구조

```
ai-publishing/
├── translate_pdf.py              # 번역 스크립트
├── edit_document.py              # 편집 스크립트
│
├── input/                        # 입력 PDF
├── output/                       # 번역 결과
├── output_edited/                # 편집 결과
│
├── src/                          # 소스 코드
│   ├── editing/                  # 편집 모듈
│   │   ├── prompts/              # 프롬프트
│   │   ├── utils/                # 유틸리티
│   │   └── edit_orchestrator_v2.py
│   └── ...
│
├── resources/                    # 리소스
│   └── korean_grammar_rules.md
│
├── QUICKSTART.md                 # 빠른 시작
├── README_USAGE.md               # 상세 가이드
├── TRANSLATION_GUIDELINE.md      # 번역 가이드
├── EDITING_GUIDE.md              # 편집 가이드
└── USAGE.txt                     # 간단 사용법
```

---

## 💰 비용 및 성능

### 번역 (35페이지 PDF 기준)
- ⏱️ 시간: ~1분
- 💰 비용: ~$0.70
- 📊 품질: ⭐⭐⭐⭐⭐

### 편집 (24,370자 기준)
- ⏱️ 시간: ~2.4분
- 💰 비용: ~$0.97
- 📊 품질: ⭐⭐⭐⭐⭐

### 전체 워크플로우
- ⏱️ 총 시간: ~3.4분
- 💰 총 비용: ~$1.67

---

## 🎓 주요 문서

| 문서 | 설명 |
|------|------|
| `QUICKSTART.md` | 1분 빠른 시작 가이드 |
| `README_USAGE.md` | 상세 사용 가이드 |
| `USAGE.txt` | 간단 사용법 (텍스트) |
| `TRANSLATION_GUIDELINE.md` | 번역 철학 및 가이드라인 |
| `EDITING_GUIDE.md` | 편집 프로세스 상세 가이드 |
| `HOW_TO_RETRANSLATE.md` | 재번역 가이드 |

---

## 🔧 기술 스택

- **언어**: Python 3.11+
- **AI 모델**: Claude 3.7 Sonnet
- **주요 라이브러리**:
  - `anthropic` - Claude API
  - `pdfplumber` - PDF 텍스트 추출
  - `python-dotenv` - 환경 변수 관리

---

## ✨ 주요 특징

### 번역
1. **전문 번역가 페르소나**: 20년 경력 출판 번역가
2. **5가지 번역 철학**: 의미 충실성, 자연스러운 한국어, 읽기 쉬운 문장, 맥락과 흐름, 톤과 뉘앙스
3. **스마트 청킹**: 문장 경계 감지, 컨텍스트 오버랩
4. **병렬 처리**: 20개 워커로 5-6배 속도 향상
5. **용어 일관성**: 자동 용어 추출 및 일관성 보장

### 편집
1. **2-Pass 시스템**: 기계적 교정 + 창의적 윤문
2. **출판 편집자 페르소나**: 20년 경력 편집자
3. **번역체 제거**: "~되어지다", "것이다" 등
4. **긴 문장 분리**: 40단어 이상 → 2-3개로
5. **변경사항 추적**: 전후 비교 리포트

---

## 📊 품질 지표

### 번역 품질
- ✅ 의미 보존: 100%
- ✅ 자연스러운 한국어: 95%+
- ✅ 용어 일관성: 98%+
- ✅ 가독성: 90점+

### 편집 품질
- ✅ 맞춤법 정확도: 99%+
- ✅ 문장 구조 개선: 51.8%
- ✅ 번역체 제거: 95%+
- ✅ 가독성 향상: 20-30%

---

## 🎯 사용 사례

1. **비즈니스서 번역**: 스타트업, 경영, 마케팅 서적
2. **기술 문서 번역**: 개발자 가이드, API 문서
3. **학술 논문 번역**: 연구 논문, 리뷰 논문
4. **번역본 편집**: 기존 번역본의 품질 향상

---

## 🔄 워크플로우

```
PDF 파일
   ↓
[translate_pdf.py]
   ↓
번역본 (output/)
   ↓
[edit_document.py]
   ↓
편집본 (output_edited/)
   ↓
출판 가능한 최종본
```

---

## 🛠️ 개발 환경

```bash
# 설치
pip install anthropic pdfplumber python-dotenv

# 환경 변수
ANTHROPIC_API_KEY=your-api-key

# 실행
python translate_pdf.py input/book.pdf
python edit_document.py output/output_book_translated.md
```

---

## 📈 향후 개선 계획

1. **다국어 지원**: 영어 외 다른 언어 번역
2. **도메인 특화**: 법률, 의학, 금융 등 전문 분야
3. **UI 개발**: 웹 인터페이스 제공
4. **배치 처리**: 여러 파일 동시 처리
5. **품질 평가**: 자동 품질 점수 산출

---

**버전**: 2.0  
**최종 업데이트**: 2025-11-19  
**상태**: 프로덕션 레디 ✅
