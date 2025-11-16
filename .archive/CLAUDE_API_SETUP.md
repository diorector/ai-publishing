# Claude API 설정 가이드

## 필수 단계

### 1단계: API 키 취득

1. **Anthropic 콘솔 방문**
   - https://console.anthropic.com

2. **계정 생성 또는 로그인**
   - 이미 계정이 있으면 로그인

3. **API 키 생성**
   - Dashboard → API Keys → Create key

4. **API 키 복사**
   - 생성된 키를 안전하게 복사 (다시 표시 안됨)

---

## 2단계: 환경 설정 (2가지 방법)

### 방법 A: .env 파일 사용 (권장)

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

### 방법 B: 환경 변수 설정

#### Windows (Command Prompt)
```cmd
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

#### Windows (PowerShell)
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxx"
```

#### Mac/Linux
```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
```

---

## 3단계: 의존성 설치

```bash
# requirements.txt에서 필요한 패키지 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install anthropic python-dotenv pdfplumber
```

---

## 4단계: Claude 번역 테스트

```bash
# API 키가 설정된 후 실행
python test_pdf_with_claude.py
```

---

## 예상 결과

성공하면 다음과 같이 표시됩니다:

```
[OK] API key found
[STEP 1] Extract PDF
[STEP 2] Text Preview
[STEP 3] Text Chunking
[STEP 4] Translate with Claude API
[1/2] Translating chunk 1...
  [OK] 2500 characters
[2/2] Translating chunk 2...
  [OK] 2500 characters
```

---

## 문제 해결

### "API key not set" 오류

**해결책**:
1. .env 파일 또는 환경 변수에 API 키 설정 확인
2. API 키 형식 확인 (sk-ant-로 시작)
3. API 키 유효성 확인 (https://console.anthropic.com)

### "anthropic library not installed" 오류

**해결책**:
```bash
pip install anthropic
```

### "Connection error" 오류

**해결책**:
1. 인터넷 연결 확인
2. API 키 유효성 재확인
3. API 서비스 상태 확인

---

## 비용 정보

Claude API 사용:
- **Sonnet 3.5** (현재 사용 모델)
  - 입력: $3/1M 토큰
  - 출력: $15/1M 토큰

- **예상 비용**: PDF 1권 번역 약 $0.10 ~ $0.50

---

## 더 알아보기

- **API 문서**: https://docs.anthropic.com
- **가격 정보**: https://www.anthropic.com/pricing
- **Rate Limits**: 분당 요청 제한 있음 (Pro/Enterprise 계획으로 상향 가능)

---

## 다음 단계

API 키 설정 후:

```bash
# 전체 PDF 번역 (모든 청크)
python translate_full_pdf.py src/translation/laf.pdf

# 배치 처리 (병렬 번역)
python translate_batch.py src/translation/laf.pdf --parallel 5

# 웹 인터페이스 실행
python app.py
```
