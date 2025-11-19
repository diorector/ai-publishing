# 🚀 빠른 시작 가이드

📖 문서 읽는 순서
처음: QUICKSTART.md (1분)
자세히: README_USAGE.md
구조 이해: PROJECT_STRUCTURE.md
번역 개선: TRANSLATION_GUIDELINE.md
편집 개선: EDITING_GUIDE.md

## 1분 안에 시작하기

### 1️⃣ 설치

```bash
# 패키지 설치
pip install anthropic pdfplumber python-dotenv

# API 키 설정
echo "ANTHROPIC_API_KEY=your-api-key-here" > .env
```

### 2️⃣ PDF 번역

```bash
# PDF 파일을 input/ 폴더에 넣기
cp your-book.pdf input/

# 번역 실행
python translate_pdf.py your-book.pdf

# 결과 확인
# output/output_your-book_translated.md
```

### 3️⃣ 문서 편집

```bash
# 번역본 편집
python edit_document.py output/output_your-book_translated.md

# 결과 확인
# output_edited/output_your-book_translated/output_your-book_translated_edited.md
```

---

## 📋 체크리스트

- [ ] Python 3.11+ 설치됨
- [ ] 필요한 패키지 설치됨
- [ ] `.env` 파일에 API 키 설정됨
- [ ] `input/` 폴더에 PDF 파일 있음

---

## 💰 예상 비용

| 작업 | 35페이지 PDF | 비용 |
|------|-------------|------|
| 번역 | ~1분 | ~$0.70 |
| 편집 | ~2.4분 | ~$0.97 |
| **총합** | **~3.4분** | **~$1.67** |

---

## 🆘 문제 발생 시

### API 키 오류
```bash
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### 패키지 오류
```bash
pip install --upgrade anthropic pdfplumber python-dotenv
```

### 자세한 도움말
```bash
python translate_pdf.py --help
python edit_document.py --help
```

---

**더 자세한 가이드**: [README_USAGE.md](README_USAGE.md)
