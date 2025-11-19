# AI-Publishing 사용 가이드

> PDF 번역 및 편집을 위한 AI 기반 출판 도구

---

## 🚀 빠른 시작

### 필수 요구사항

```bash
# Python 3.11+
python --version

# 필요한 패키지 설치
pip install anthropic pdfplumber python-dotenv

# API 키 설정
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

---

## 📚 주요 기능

### 1️⃣ PDF 번역 (`translate_pdf.py`)

**출판 수준의 전문 번역**
- 20년 경력 번역가 페르소나
- 5가지 번역 철학 적용
- 병렬 처리로 빠른 속도
- 용어 일관성 보장

#### 사용법

```bash
# 기본 사용 (input/laf.pdf 번역)
python translate_pdf.py

# 특정 파일 번역
python translate_pdf.py book.pdf

# 절대 경로 지정
python translate_pdf.py /path/to/file.pdf
```

#### 출력

```
output/
└── output_파일명_translated.md
```

#### 예상 비용 및 시간

| PDF 크기 | 예상 비용 | 처리 시간 |
|---------|----------|----------|
| 10페이지 | ~$0.20 | ~30초 |
| 35페이지 | ~$0.70 | ~1분 |
| 100페이지 | ~$2.00 | ~3분 |

**자세한 가이드**: [TRANSLATION_GUIDELINE.md](TRANSLATION_GUIDELINE.md)

---

### 2️⃣ 문서 편집 (`edit_document.py`)

**출판 편집자 수준의 2-Pass 편집**
- Pass 1: 기계적 교정 (맞춤법, 띄어쓰기)
- Pass 2: 창의적 윤문 (문장 구조, 가독성)

#### 사용법

```bash
# 전체 2-Pass 편집 (교정 + 윤문)
python edit_document.py output/output_laf_translated.md

# Pass 1만 실행 (교정만)
python edit_document.py output/output_laf_translated.md --pass1-only

# 병렬 처리 워커 수 조정
python edit_document.py output/output_laf_translated.md --workers 5

# 비교 리포트 생략
python edit_document.py output/output_laf_translated.md --no-diff
```

#### 출력

```
output_edited/
└── 파일명/
    ├── 파일명_edited.md         # 최종 편집본
    ├── 파일명_pass1.md          # Pass 1 결과 (참고용)
    └── 파일명_diff_report.md    # 변경사항 비교
```

#### 예상 비용 및 시간

| 문서 크기 | 예상 비용 | 처리 시간 |
|----------|----------|----------|
| 1,000자 | ~$0.05 | ~10초 |
| 10,000자 | ~$0.50 | ~1분 |
| 50,000자 | ~$2.50 | ~5분 |

**자세한 가이드**: [EDITING_GUIDE.md](EDITING_GUIDE.md)

---

## 🔄 전체 워크플로우

### 단계별 가이드

```bash
# 1. PDF를 한국어로 번역
python translate_pdf.py input/book.pdf

# 2. 번역본 편집
python edit_document.py output/output_book_translated.md

# 3. 결과 확인
# - 번역본: output/output_book_translated.md
# - 편집본: output_edited/output_book_translated/output_book_translated_edited.md
```

### 예시: "Lost and Founder" 번역 및 편집

```bash
# 1단계: 번역 (35페이지 PDF)
python translate_pdf.py input/laf.pdf
# ⏱️  소요: ~1분
# 💰 비용: ~$0.70
# 📄 출력: output/output_laf_translated.md

# 2단계: 편집 (24,370자)
python edit_document.py output/output_laf_translated.md
# ⏱️  소요: ~2.4분
# 💰 비용: ~$0.97
# 📄 출력: output_edited/output_laf_translated/output_laf_translated_edited.md

# 총 비용: ~$1.67
# 총 시간: ~3.4분
```

---

## 📁 프로젝트 구조

```
ai-publishing/
├── translate_pdf.py              # 📝 PDF 번역 스크립트
├── edit_document.py              # ✏️  문서 편집 스크립트
│
├── input/                        # 📥 입력 PDF 파일
│   └── laf.pdf
│
├── output/                       # 📤 번역 결과물
│   └── output_laf_translated.md
│
├── output_edited/                # ✨ 편집 결과물
│   └── output_laf_translated/
│       ├── output_laf_translated_edited.md
│       ├── output_laf_translated_pass1.md
│       └── output_laf_translated_diff_report.md
│
├── src/                          # 🔧 소스 코드
│   ├── editing/                  # 편집 모듈
│   │   ├── prompts/              # 편집 프롬프트
│   │   ├── utils/                # 유틸리티
│   │   └── edit_orchestrator_v2.py
│   └── ...
│
├── resources/                    # 📚 리소스 파일
│   └── korean_grammar_rules.md
│
├── TRANSLATION_GUIDELINE.md      # 번역 가이드
├── EDITING_GUIDE.md              # 편집 가이드
├── HOW_TO_RETRANSLATE.md         # 재번역 가이드
└── README.md                     # 프로젝트 개요
```

---

## 🎯 편집 품질 예시

### Before (번역본)

```markdown
그것은 우리가 피벗을 해야만 했다는 것을 제가 깨달았을 때였습니다. 
저는 25세였고, 그의 도착으로 인해 방향 감각을 잃었으며, 
그의 외모와 어조에 위협을 느꼈고, 완전히 공황 상태였습니다.
```

### After (편집본)

```markdown
그때 깨달았습니다. 방향을 바꿔야 한다는 것을요. 
저는 25세였습니다. 그가 나타났을 때 당황했습니다. 
그의 외모와 어조가 위협적이었고, 완전히 공황 상태에 빠졌습니다.
```

**개선점**:
- ✅ 번역체 제거 ("그것은...때였습니다")
- ✅ 긴 문장 분리 (1개 → 3개)
- ✅ 자연스러운 한국어
- ✅ 리듬감 추가

---

## 💡 팁 & 트릭

### 번역 팁

1. **용어 일관성**
   - 자동 용어 추출 기능 활용
   - 30개 핵심 비즈니스 용어 사전 내장

2. **청크 크기 조정**
   - 기본: 5,000자
   - 더 정확한 번역: 3,000자
   - 더 빠른 처리: 7,000자

3. **병렬 처리**
   - 기본: 20개 워커
   - API 레이트 한계 주의

### 편집 팁

1. **Pass 1 결과 확인**
   - `*_pass1.md` 파일로 교정 결과 검토
   - 문제 발견 시 Pass 2 전에 수정

2. **비교 리포트 활용**
   - `*_diff_report.md`로 변경사항 검토
   - 과도한 변경 시 원본 복원

3. **워커 수 조정**
   - 빠른 처리: `--workers 15`
   - 안정적 처리: `--workers 5`
   - API 오류 시: `--workers 3`

---

## 🛠️ 문제 해결

### API 키 오류

```bash
⚠️  ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.
```

**해결**:
```bash
# .env 파일 생성
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 모델 오류

```bash
⚠️  Claude API 호출 실패: Error code: 404
```

**해결**: 최신 모델 사용 중인지 확인
- 현재 사용: `claude-3-7-sonnet-20250219`

### 메모리 부족

```bash
MemoryError: Unable to allocate array
```

**해결**: 워커 수 줄이기
```bash
python edit_document.py file.md --workers 3
```

### 느린 처리 속도

**해결**: 워커 수 늘리기
```bash
python edit_document.py file.md --workers 15
```

---

## 📊 성능 벤치마크

### 번역 성능

| 문서 | 페이지 | 문자 수 | 시간 | 비용 | 품질 |
|------|--------|---------|------|------|------|
| Lost and Founder | 35 | 50,898 | 47초 | $0.70 | ⭐⭐⭐⭐⭐ |
| 샘플 문서 | 2 | 455 | 11초 | $0.05 | ⭐⭐⭐⭐⭐ |

### 편집 성능

| 문서 | 문자 수 | 시간 | 비용 | 변경률 | 품질 |
|------|---------|------|------|--------|------|
| Lost and Founder | 24,370 | 143초 | $0.97 | 51.8% | ⭐⭐⭐⭐⭐ |
| 샘플 문서 | 455 | 12초 | $0.04 | 64.3% | ⭐⭐⭐⭐⭐ |

---

## 🎓 추가 학습 자료

### 번역 관련
- [TRANSLATION_GUIDELINE.md](TRANSLATION_GUIDELINE.md) - 번역 가이드라인
- [HOW_TO_RETRANSLATE.md](HOW_TO_RETRANSLATE.md) - 재번역 가이드

### 편집 관련
- [EDITING_GUIDE.md](EDITING_GUIDE.md) - 편집 가이드
- `src/editing/prompts/editor_persona.py` - 편집자 페르소나

### 프로젝트 관련
- [README.md](README.md) - 프로젝트 전체 개요
- `.moai/specs/` - SPEC 문서

---

## 🤝 기여하기

### 개선 제안

1. **번역 품질 개선**
   - `src/editing/prompts/` 프롬프트 수정
   - 용어 사전 추가

2. **편집 규칙 추가**
   - `resources/korean_grammar_rules.md` 업데이트
   - 새로운 편집 패턴 추가

3. **성능 최적화**
   - 청크 크기 조정
   - 병렬 처리 개선

---

## 📝 라이선스

이 프로젝트는 MoAI-ADK (MoAI Agentic Development Kit) 생태계의 일부입니다.

---

## 📞 지원

문제가 발생하면:
1. [문제 해결](#-문제-해결) 섹션 확인
2. GitHub Issues 검색
3. 새 Issue 생성

---

**버전**: 2.0  
**최종 업데이트**: 2025-11-19  
**작성자**: Kiro AI Assistant
