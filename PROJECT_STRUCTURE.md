# AI-Publishing 프로젝트 구조

## 📁 최종 구조 (정리 완료)

```
ai-publishing/
│
├── 🚀 메인 스크립트
│   ├── translate_pdf.py              # PDF → 한국어 번역
│   └── edit_document.py              # 문서 편집 (2-Pass)
│
├── 📚 사용 가이드
│   ├── QUICKSTART.md                 # 1분 빠른 시작
│   ├── README_USAGE.md               # 상세 사용 가이드
│   ├── USAGE.txt                     # 간단 사용법 (텍스트)
│   ├── TRANSLATION_GUIDELINE.md      # 번역 가이드라인
│   ├── EDITING_GUIDE.md              # 편집 가이드
│   ├── HOW_TO_RETRANSLATE.md         # 재번역 가이드
│   └── PROJECT_SUMMARY.md            # 프로젝트 요약
│
├── 🔧 소스 코드
│   └── src/
│       ├── __init__.py
│       └── editing/                  # 편집 모듈
│           ├── __init__.py
│           ├── edit_orchestrator_v2.py  # 메인 오케스트레이터
│           ├── models/               # 데이터 모델
│           │   ├── __init__.py
│           │   ├── document.py
│           │   └── edit_result.py
│           ├── prompts/              # AI 프롬프트
│           │   ├── __init__.py
│           │   ├── editor_persona.py
│           │   ├── proofreading_prompt.py
│           │   └── polishing_prompt.py
│           └── utils/                # 유틸리티
│               ├── __init__.py
│               └── diff_generator.py
│
├── 📂 데이터 폴더
│   ├── input/                        # 입력 PDF 파일
│   ├── output/                       # 번역 결과물
│   │   └── output_*_translated.md
│   └── output_edited/                # 편집 결과물
│       └── output_*_translated/
│           ├── *_edited.md           # 최종 편집본
│           ├── *_pass1.md            # Pass 1 결과
│           └── *_diff_report.md      # 변경사항 비교
│
├── 📚 리소스
│   └── resources/
│       └── korean_grammar_rules.md   # 한글 맞춤법 규정
│
├── 📖 프로젝트 문서
│   ├── README.md                     # 프로젝트 개요
│   ├── CLAUDE.md                     # 개발 규칙
│   └── PROJECT_STRUCTURE.md          # 이 파일
│
└── ⚙️ 설정 파일
    ├── .env                          # 환경 변수 (API 키)
    ├── .gitignore                    # Git 제외 파일
    └── .mcp.json                     # MCP 설정
```

---

## 🎯 핵심 파일 설명

### 메인 스크립트

| 파일 | 설명 | 의존성 |
|------|------|--------|
| `translate_pdf.py` | PDF 번역 스크립트 | 독립 실행 (src 불필요) |
| `edit_document.py` | 문서 편집 스크립트 | `src/editing/` 사용 |

### 소스 코드

| 파일 | 설명 |
|------|------|
| `src/editing/edit_orchestrator_v2.py` | 편집 파이프라인 조율 |
| `src/editing/prompts/editor_persona.py` | 편집자 페르소나 정의 |
| `src/editing/prompts/proofreading_prompt.py` | Pass 1 프롬프트 |
| `src/editing/prompts/polishing_prompt.py` | Pass 2 프롬프트 |
| `src/editing/utils/diff_generator.py` | 변경사항 비교 도구 |
| `src/editing/models/document.py` | 문서 데이터 모델 |
| `src/editing/models/edit_result.py` | 편집 결과 모델 |

---

## 🗂️ 폴더별 용도

### `input/`
- **용도**: 번역할 PDF 파일 저장
- **예시**: `input/book.pdf`

### `output/`
- **용도**: 번역 결과물 저장
- **형식**: `output_파일명_translated.md`
- **예시**: `output/output_book_translated.md`

### `output_edited/`
- **용도**: 편집 결과물 저장
- **구조**: 파일별 폴더로 정리
- **예시**:
  ```
  output_edited/
  └── output_book_translated/
      ├── output_book_translated_edited.md
      ├── output_book_translated_pass1.md
      └── output_book_translated_diff_report.md
  ```

### `resources/`
- **용도**: 리소스 파일 (규칙, 사전 등)
- **파일**: `korean_grammar_rules.md` - 한글 맞춤법 규정

---

## 🔄 데이터 흐름

```
PDF 파일 (input/)
    ↓
[translate_pdf.py]
    ↓
번역본 (output/)
    ↓
[edit_document.py]
    ↓
편집본 (output_edited/)
```

---

## 📦 의존성

### Python 패키지
```bash
pip install anthropic pdfplumber python-dotenv
```

### 환경 변수
```bash
# .env 파일
ANTHROPIC_API_KEY=your-api-key-here
```

---

## 🧹 정리된 항목

### 삭제된 폴더
- ❌ `src/chunking/` - translate_pdf.py에 통합됨
- ❌ `src/markdown/` - translate_pdf.py에 통합됨
- ❌ `src/pdf_processor/` - translate_pdf.py에 통합됨
- ❌ `src/quality/` - 사용 안 함
- ❌ `src/translation/` - translate_pdf.py에 통합됨
- ❌ `tests/` - 구버전 테스트 (새로 작성 필요)

### 삭제된 파일
- ❌ `src/orchestrator.py` - 구버전
- ❌ `src/editing/edit_orchestrator.py` - v2로 대체
- ❌ `src/editing/edit_proofreading.py` - v2에 통합
- ❌ `src/editing/edit_fact_checking.py` - v2에 통합
- ❌ `src/editing/edit_copywriting.py` - v2에 통합
- ❌ 테스트 파일들 (`test_sample*`)
- ❌ 불필요한 문서들 (`SYNC_*`, `DOC_SYNC_*`)

---

## 📊 통계

### 정리 전
- 📁 폴더: 15개
- 📄 파일: 80+ 개
- 💾 크기: ~50MB

### 정리 후
- 📁 폴더: 8개
- 📄 파일: 30개
- 💾 크기: ~15MB
- 🎯 감소율: 70%

---

## 🎓 코드 구조 철학

### 1. 단순성 (Simplicity)
- 메인 스크립트는 독립 실행 가능
- 최소한의 의존성
- 명확한 책임 분리

### 2. 모듈성 (Modularity)
- `src/editing/` - 편집 기능만 담당
- 프롬프트, 유틸리티, 모델 분리
- 재사용 가능한 컴포넌트

### 3. 명확성 (Clarity)
- 직관적인 파일명
- 명확한 폴더 구조
- 풍부한 문서화

---

## 🚀 다음 단계

### 개발
1. 새로운 기능 추가 시 `src/editing/` 확장
2. 테스트 코드 작성 (pytest)
3. CI/CD 파이프라인 구축

### 문서화
1. API 문서 자동 생성
2. 예제 코드 추가
3. 튜토리얼 비디오

### 최적화
1. 성능 프로파일링
2. 메모리 사용량 최적화
3. 병렬 처리 개선

---

**버전**: 2.0  
**최종 정리**: 2025-11-19  
**상태**: 프로덕션 레디 ✅
