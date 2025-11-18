# SPEC-PUB-EDIT-COMPREHENSIVE-001: 수용 기준 및 테스트 시나리오

**Version**: 1.0.0
**Status**: DRAFT
**Created**: 2025-11-18

---

## 📋 개요

이 문서는 포괄적 편집 도구의 완성도를 검증하기 위한 **구체적인 수용 기준과 테스트 시나리오**를 정의합니다. 각 기준은 Given-When-Then 형식의 자동화된 테스트로 검증 가능해야 합니다.

---

## 🎯 품질 게이트 (Quality Gates)

### 1단계: 단위 테스트 (Unit Tests)

**요구사항**:
- 모든 모듈 최소 80% 코드 커버리지
- 모든 단위 테스트 통과 (0 실패)
- 평균 응답 시간 <5초/요청

**체크리스트**:
```python
# tests/test_orchestrator.py
def test_document_loading():
    """마크다운 파일 로드 및 파싱"""
    doc = load_document("test_doc.md")
    assert doc.title is not None
    assert len(doc.content) > 0
    assert doc.word_count > 0

def test_document_analysis():
    """문서 분석 및 도메인 분류"""
    doc = create_test_document(domain="startup")
    analysis = orchestrator.analyze_document(doc)
    assert analysis.domain == "startup"
    assert len(analysis.issues) > 0

def test_checkpoint_saving():
    """체크포인트 저장 및 복구"""
    doc = create_test_document()
    orchestrator.save_checkpoint(doc, "proofreading")
    restored = orchestrator.load_checkpoint(doc.id, "proofreading")
    assert restored.id == doc.id
```

### 2단계: 통합 테스트 (Integration Tests)

**요구사항**:
- 3개 모듈 모두 정상 동작
- 각 단계 간 데이터 전달 무결성
- 오류 발생 시 적절한 복구

**체크리스트**:
```python
# tests/test_integration.py
@pytest.mark.asyncio
async def test_proofreading_only():
    """교정만 실행"""
    doc = load_test_document("startup", size="small")
    result = await orchestrator.edit_comprehensive(
        doc,
        stages=[EditStage.PROOFREADING]
    )
    assert result.quality_score >= 75
    assert len(result.changes) > 0

@pytest.mark.asyncio
async def test_all_stages_sequential():
    """3단계 순차 실행"""
    doc = load_test_document("startup", size="medium")
    result = await orchestrator.edit_comprehensive(doc)
    assert result.quality_score >= 80
    # 각 단계 결과 확인
    assert result.proofreading_score >= 75
    assert result.fact_checking_score >= 75
    assert result.copywriting_score >= 75

@pytest.mark.asyncio
async def test_error_recovery():
    """오류 발생 및 복구"""
    doc = load_test_document()
    # 의도적으로 오류 주입
    with patch("anthropic.Anthropic.messages.create") as mock:
        mock.side_effect = APIError("Service unavailable")

        try:
            await orchestrator.edit_comprehensive(doc)
        except APIError:
            pass

        # 복구 가능한지 확인
        checkpoint = orchestrator.load_checkpoint(doc.id)
        assert checkpoint is not None
```

### 3단계: 엔드-투-엔드 테스트 (E2E Tests)

**요구사항**:
- 실제 데이터로 전체 파이프라인 테스트
- 최종 결과 품질 ≥90점
- 처리 시간 기준 내 완료

**체크리스트**:
```python
# tests/test_e2e.py
@pytest.mark.asyncio
async def test_laf_document_editing():
    """LAF 문서 전체 편집 (실제 데이터)"""
    # LAF 실제 파일 로드
    doc = load_document("input/laf_translated.md")

    # 전체 편집
    start = time.time()
    result = await orchestrator.edit_comprehensive(doc)
    elapsed = time.time() - start

    # 품질 검증
    assert result.quality_score >= 90, "품질 점수 미달"
    assert result.proofreading_errors < 10, "교정 오류 초과"
    assert result.fact_check_issues < 5, "교열 이슈 초과"
    assert result.copywriting_score >= 85, "윤문 점수 미달"

    # 성능 검증
    word_count = len(doc.content.split())
    expected_time = (word_count / 10000) * 7200  # 10K단어당 2시간
    assert elapsed < expected_time * 1.2, "처리 시간 초과"

    # 결과 저장
    save_result(result, "output/laf_edited.md")
```

---

## ✅ 기능별 수용 기준

### A. 교정(Proofreading) 모듈

#### A.1 기본 교정 기능

**시나리오 1: 띄어쓰기 오류 교정**

```gherkin
Given: 띄어쓰기 오류가 있는 한글 텍스트
When: 교정 모듈 실행
Then:
  ✅ 모든 띄어쓰기 오류 수정
  ✅ 원문과 수정본 명확히 제시
  ✅ 변경 사항 로그 기록
```

**테스트 데이터**:
```python
test_cases = [
    ("한글맞춤법", "한글 맞춤법"),
    ("이를테면이렇게", "이를테면 이렇게"),
    ("Google회사", "Google 회사"),
]

@pytest.mark.parametrize("original,expected", test_cases)
async def test_spacing_correction(original, expected):
    agent = FormatExpertAgent(config)
    result = await agent.process_chunk(original)
    assert expected in result.edited_text
```

#### A.2 외국어 표기법 일관성

**시나리오 2: 기업명 표기 일관성**

```gherkin
Given: 같은 기업명이 여러 방식으로 표기된 문서
When: 교정 모듈 실행
Then:
  ✅ 모든 "Google" → "구글" 통일
  ✅ "Amazon" → "아마존" 통일
  ✅ 불가지 표기법 플래그 표시
```

**테스트 케이스**:
```python
async def test_notation_consistency():
    """외국어 표기법 일관성"""
    text = """Google은 검색 엔진으로 유명합니다.
구글은 AI에도 투자하고 있습니다.
GOOGLE의 자회사도 있습니다."""

    result = await agent.process_chunk(text)

    # 모두 같은 표기법으로 통일되어야 함
    google_count = result.edited_text.count("구글")
    other_forms = result.edited_text.count("Google") + \
                   result.edited_text.count("GOOGLE")

    assert other_forms == 0, "표기법 미통일"
    assert google_count == 3, "모든 표기 통일 확인"
```

#### A.3 품질 기준

```python
class ProofreadingAcceptanceCriteria:
    """교정 모듈 수용 기준"""

    def validate(self, result: EditResult) -> bool:
        checks = {
            "spelling_accuracy": result.spelling_errors < 1,  # <1% 오류
            "spacing_consistency": result.spacing_score > 0.95,
            "notation_uniformity": result.notation_score > 0.95,
            "processing_time": result.processing_time < 300,  # <5분/청크
            "quality_score": result.quality_score >= 85,
        }

        return all(checks.values())
```

---

### B. 교열(Fact-checking) 모듈

#### B.1 팩트 검증 기능

**시나리오 3: 통계 검증**

```gherkin
Given: 통계 수치가 포함된 텍스트
When: 교열 모듈 실행
Then:
  ✅ Context7로 2025년 최신 정보 검색
  ✅ 정보의 신뢰도 평점 제시
  ✅ 구식 정보 식별 및 주석 추가
```

**테스트 케이스**:
```python
@pytest.mark.asyncio
async def test_statistics_verification():
    """통계 수치 검증"""
    text = """
    2023년 통계에 따르면 스타트업은 5,000개 이상이었습니다.
    전 세계 AI 시장은 5조 달러 규모입니다.
    """

    fact_checker = FactCheckerAgent(config)
    result = await fact_checker.process_chunk(text)

    # 검증 결과 확인
    assert len(result.verified_items) >= 2, "검증 항목 부족"
    assert all(item.source is not None for item in result.verified_items)
    assert all(item.confidence >= 0.7 for item in result.verified_items)
```

#### B.2 구식 정보 식별

**시나리오 4: 구식 정보 주석**

```gherkin
Given: 2023년 이전 정보가 포함된 문서
When: 교열 모듈 실행
Then:
  ✅ 구식 정보 감지
  ✅ 2025년 최신 정보와 함께 주석 추가
  ✅ 원문은 유지하되 주석으로 표시
```

**테스트 케이스**:
```python
@pytest.mark.asyncio
async def test_deprecated_annotation():
    """구식 정보 주석"""
    text = "2023년 기준 비트코인은 3만 달러였습니다."

    result = await fact_checker.process_chunk(text)

    # 구식 정보 주석이 추가되어야 함
    assert "편집자 주" in result.edited_text or \
           "2025년 기준" in result.edited_text

    # 원문은 유지
    assert "2023년" in result.edited_text
    assert "3만 달러" in result.edited_text
```

#### B.3 Context7 통합 검증

**시나리오 5: Context7 검색**

```gherkin
Given: 검증 필요 항목 목록
When: Context7 MCP로 정보 검색
Then:
  ✅ 2025년 기준 최신 정보 반환
  ✅ 여러 출처 제시
  ✅ 신뢰도 점수 제공
```

**테스트 케이스**:
```python
@pytest.mark.asyncio
async def test_context7_integration():
    """Context7 통합"""
    query = "한국 스타트업 현황 2025"

    context7 = Context7Client(config)
    results = await context7.search(
        query=query,
        domain="startup",
        year=2025
    )

    # Context7 응답 검증
    assert len(results) > 0, "검색 결과 없음"
    assert all(r.source is not None for r in results)
    assert all(r.confidence is not None for r in results)
    assert max(r.confidence for r in results) > 0.8, "신뢰도 낮음"
```

#### B.4 품질 기준

```python
class FactCheckingAcceptanceCriteria:
    """교열 모듈 수용 기준"""

    def validate(self, result: EditResult) -> bool:
        checks = {
            "verification_coverage": result.verified_items / \
                                   result.total_items > 0.9,
            "confidence_threshold": result.avg_confidence > 0.7,
            "deprecated_flagging": len(result.deprecated_items) > 0 or \
                                  result.no_issues,
            "processing_time": result.processing_time < 600,  # <10분/섹션
            "quality_score": result.quality_score >= 80,
        }

        return all(checks.values())
```

---

### C. 윤문(Copywriting) 모듈

#### C.1 문장 개선

**시나리오 6: 복문 단문화**

```gherkin
Given: 복잡한 복문이 있는 텍스트
When: 윤문 모듈 실행
Then:
  ✅ 복문을 2-3개 단문으로 분해
  ✅ 의미 손실 없음 (100% 보존)
  ✅ 가독성 점수 개선
```

**테스트 케이스**:
```python
@pytest.mark.asyncio
async def test_sentence_simplification():
    """복문 단순화"""
    original = "우리가 개발한 AI 모델은 기존 모델 대비 \
30% 더 빠르면서도 정확도는 5% 높아서 시장에서 경쟁력이 있다."

    copywriter = CopywritingExpertAgent(config)
    result = await copywriter.process_paragraph(original)

    # 검증
    sentence_count = len(result.edited_text.split('.'))
    assert sentence_count > 1, "분해 안 됨"

    # 의미 동등성 검증 (의미론적 유사도 >0.9)
    similarity = semantic_similarity(original, result.edited_text)
    assert similarity > 0.9, "의미 손실"

    # 가독성 개선 (flesch score 증가)
    assert result.readability_score > \
           calculate_flesch_score(original), "가독성 미개선"
```

#### C.2 톤앤매너 일관성

**시나리오 7: 존댓말 일관성**

```gherkin
Given: 존댓말과 반말이 섞인 문서
When: 윤문 모듈 실행
Then:
  ✅ 모든 문장을 존댓말로 통일
  ✅ 저자 의도 보존
  ✅ 전문성 유지
```

**테스트 케이스**:
```python
@pytest.mark.asyncio
async def test_tone_consistency():
    """톤앤매너 일관성"""
    text = """
    스타트업은 빠르게 성장한다. 그들은 혁신적이고,
    시장에 새로운 가치를 제시합니다.
    """

    result = await copywriter.process_paragraph(text)

    # 존댓말 일관성 검증
    tone_score = evaluate_tone_consistency(result.edited_text)
    assert tone_score > 0.95, "톤앤매너 미통일"

    # 존댓말만 사용 확인
    assert "-습니다" in result.edited_text or \
           "-합니다" in result.edited_text or \
           "-니다" in result.edited_text
```

#### C.3 번역체 제거

**시나리오 8: 번역체 표현 제거**

```gherkin
Given: 번역체 표현이 있는 한글 문서
When: 윤문 모듈 실행
Then:
  ✅ "~되어지다", "~것이다" 등 제거
  ✅ 자연스러운 한국어로 변환
  ✅ 원의미 완벽 보존
```

**테스트 케이스**:
```python
@pytest.mark.parametrize("translated,natural", [
    ("시스템에 의해 자동으로 처리되어진다",
     "시스템이 자동으로 처리한다"),
    ("이것이 핵심이다",
     "이것이 핵심입니다"),
    ("~하는 것이 중요하다",
     "~하는 것이 중요합니다"),
])
async def test_remove_translation_style(translated, natural):
    """번역체 제거"""
    result = await copywriter.process_paragraph(translated)

    # 번역체 표현 제거 확인
    translation_style = [
        "~되어지다", "~된다", "것이다", "~에 의해"
    ]
    for style in translation_style:
        assert style not in result.edited_text, f"{style} 남아있음"

    # 자연스러운 표현 확인
    assert similar(result.edited_text, natural) > 0.8
```

#### C.4 품질 기준

```python
class CopywritingAcceptanceCriteria:
    """윤문 모듈 수용 기준"""

    def validate(self, result: EditResult) -> bool:
        checks = {
            "readability_improvement": \
                result.readability_score > \
                result.original_readability + 10,
            "tone_consistency": result.tone_score > 0.95,
            "intent_preservation": result.semantic_similarity > 0.95,
            "translation_style_removed": \
                result.translation_style_count == 0,
            "processing_time": result.processing_time < 180,  # <3분/단락
            "quality_score": result.quality_score >= 85,
        }

        return all(checks.values())
```

---

## 📊 통합 시나리오 (Integration Scenarios)

### 시나리오 9: 단일 문서 전체 편집

```gherkin
Given: 번역 완료된 50K 단어 문서 (LAF)
When: 전체 편집 파이프라인 실행
Then:
  ✅ 1단계: 교정 완료 (2-3시간)
  ✅ 2단계: 교열 완료 (2-3시간)
  ✅ 3단계: 윤문 완료 (2-3시간)
  ✅ 최종 품질: ≥90점
  ✅ 모든 변경사항 기록됨
  ✅ 최종 마크다운 생성됨
```

**구현 테스트**:
```python
@pytest.mark.asyncio
async def test_single_document_full_edit():
    """단일 문서 전체 편집"""
    doc = load_test_document("laf", size="50K")

    start = time.time()
    result = await orchestrator.edit_comprehensive(doc)
    elapsed = time.time() - start

    # 품질 검증
    assert result.quality_score >= 90, \
        f"품질 점수 미달: {result.quality_score}"

    # 시간 검증 (예상 8시간, 최대 10시간)
    max_time = 36000  # 10시간
    assert elapsed < max_time, \
        f"처리 시간 초과: {elapsed/3600:.1f}시간"

    # 각 단계별 점수 검증
    assert result.proofreading_score >= 85
    assert result.fact_checking_score >= 80
    assert result.copywriting_score >= 85

    # 변경사항 기록 검증
    assert len(result.all_changes) > 0
    assert result.audit_log is not None

    # 최종 파일 생성 검증
    output_path = f"output/{doc.id}_edited.md"
    assert Path(output_path).exists()
```

### 시나리오 10: 배치 처리 (4개 문서)

```gherkin
Given: 4개 번역 완료 문서 (LAF, SAF, SOSHR, CS)
When: 배치 처리 모드 실행
Then:
  ✅ 공통 용어집 자동 생성
  ✅ 문서별 순차 처리
  ✅ 모든 문서 품질 ≥90점
  ✅ 문서 간 용어 일관성 ≥95%
```

**구현 테스트**:
```python
@pytest.mark.asyncio
async def test_batch_processing():
    """배치 처리"""
    documents = [
        load_test_document("laf", size="100K"),
        load_test_document("saf", size="80K"),
        load_test_document("soshr", size="60K"),
        load_test_document("cs", size="50K"),
    ]

    start = time.time()
    results = await orchestrator.batch_process(documents)
    elapsed = time.time() - start

    # 공통 용어집 검증
    glossary = orchestrator.get_shared_glossary()
    assert len(glossary) > 100, "용어집 부족"

    # 문서별 품질 검증
    for result in results:
        assert result.quality_score >= 90, \
            f"{result.doc_id}: 품질 점수 미달"

    # 용어 일관성 검증
    consistency = calculate_term_consistency(results)
    assert consistency >= 0.95, \
        f"용어 일관성 부족: {consistency:.2%}"

    # 처리 시간 검증 (순차: ~40시간)
    max_time = 144000  # 40시간
    assert elapsed < max_time
```

### 시나리오 11: 사용자 피드백 반영

```gherkin
Given: 편집 완료 문서 + 사용자 수정 요청
When: 부분 재편집 실행
Then:
  ✅ 해당 부분만 재처리
  ✅ 전체 일관성 재검수
  ✅ 최종 품질 ≥85점
```

**구현 테스트**:
```python
@pytest.mark.asyncio
async def test_partial_reediting():
    """부분 재편집"""
    # 먼저 전체 편집
    doc = load_test_document()
    edited_doc = await orchestrator.edit_comprehensive(doc)

    # 사용자 피드백 (3개 부분 수정 요청)
    feedback = [
        {"section": "intro", "feedback": "더 친근하게"},
        {"section": "chapter2", "feedback": "명확히"},
        {"section": "conclusion", "feedback": "간결하게"},
    ]

    # 부분 재편집
    revised_doc = await orchestrator.partial_reediting(
        edited_doc,
        feedback
    )

    # 검증
    assert revised_doc.quality_score >= 85
    assert len(revised_doc.all_changes) > \
           len(edited_doc.all_changes)  # 변경사항 증가

    # 일관성 재검수
    consistency = orchestrator.verify_consistency(revised_doc)
    assert consistency >= 0.95
```

### 시나리오 12: 오류 복구

```gherkin
Given: 편집 진행 중 API 오류 발생
When: 시스템이 오류 감지
Then:
  ✅ 즉시 중단 (진행 상황 보존)
  ✅ 오류 원인 명확히 기록
  ✅ 체크포인트에서 복구 가능
  ✅ 해당 부분만 재처리
```

**구현 테스트**:
```python
@pytest.mark.asyncio
async def test_error_recovery():
    """오류 복구"""
    doc = load_test_document()

    # 의도적 오류 주입
    with patch("anthropic.Anthropic.messages.create") as mock:
        # 처음 10회는 성공, 11회부터 실패
        call_count = 0
        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count > 10:
                raise APIError("Service unavailable")
            return create_mock_response()

        mock.side_effect = side_effect

        # 편집 실행 (오류 발생)
        try:
            await orchestrator.edit_comprehensive(doc)
        except APIError:
            pass

        # 복구 검증
        checkpoint = orchestrator.load_checkpoint(doc.id)
        assert checkpoint is not None, "체크포인트 없음"
        assert checkpoint.stage == "proofreading"
        assert checkpoint.chunk_num == 10

        # 계속 진행 가능한지 확인
        mock.side_effect = None  # 오류 해제
        result = await orchestrator.resume_editing(doc.id)
        assert result is not None
```

---

## 📈 성능 테스트

### 성능 벤치마크

```python
class PerformanceBenchmarks:
    """성능 벤치마크"""

    @pytest.mark.benchmark
    async def test_proofreading_speed(self, benchmark):
        """교정 속도"""
        agent = FormatExpertAgent(config)
        doc = create_test_document(size="small")

        def run():
            return asyncio.run(agent.process(doc))

        result = benchmark(run)
        assert result.quality_score >= 80

    @pytest.mark.benchmark
    async def test_fact_checking_speed(self, benchmark):
        """교열 속도"""
        agent = FactCheckerAgent(config)
        doc = create_test_document(size="small")

        def run():
            return asyncio.run(agent.process(doc))

        result = benchmark(run)
        # Context7 호출 포함, 시간이 다소 걸림
        assert result is not None

    @pytest.mark.benchmark
    async def test_copywriting_speed(self, benchmark):
        """윤문 속도"""
        agent = CopywritingExpertAgent(config)
        doc = create_test_document(size="small")

        def run():
            return asyncio.run(agent.process(doc))

        result = benchmark(run)
        assert result.quality_score >= 80
```

### 확장성 테스트

```python
@pytest.mark.asyncio
async def test_scalability_large_document():
    """대용량 문서 처리"""
    doc = load_test_document("laf", size="200K")  # 200K 단어

    start = time.time()
    result = await orchestrator.edit_comprehensive(doc)
    elapsed = time.time() - start

    # 선형 확장성 검증
    # 50K → 8시간이면, 200K → 32시간 예상
    expected_max = 32 * 3600 * 1.5  # 1.5배 여유
    assert elapsed < expected_max, "확장성 문제"

    assert result.quality_score >= 85
```

---

## 🎓 데이터 기반 검증

### 품질 메트릭 정의

**교정 메트릭**:
```python
class ProofreadingMetrics:
    spelling_errors: int          # 발견된 맞춤법 오류
    spacing_errors: int           # 띄어쓰기 오류
    notation_inconsistencies: int # 표기법 불일치
    typos: int                    # 오타
    duplicates: int               # 중복 표현
    accuracy_rate: float          # = (발견+수정) / 총_문자수
```

**교열 메트릭**:
```python
class FactCheckingMetrics:
    verified_items: int           # 검증된 항목 수
    confidence_score: float       # 평균 신뢰도 (0-1)
    deprecated_items: int         # 구식 정보 수
    sources_cited: int            # 인용 출처 수
    coverage_rate: float          # 검증율 (검증항목/전체항목)
```

**윤문 메트릭**:
```python
class CopywritingMetrics:
    readability_improvement: int  # 가독성 증분
    tone_consistency: float       # 톤 일관성 (0-1)
    intent_preservation: float    # 의도 보존율 (0-1)
    sentence_simplification: int  # 단순화된 문장 수
    translation_style_count: int  # 번역체 표현 수 (0이어야 함)
```

---

## ✅ 최종 수용 체크리스트

```markdown
## Phase 1: 기반 인프라
- [ ] 프로젝트 구조 완성
- [ ] 모든 데이터 모델 정의
- [ ] 설정 시스템 구현
- [ ] 로깅 및 추적 시스템 구현

## Phase 2: 교정 모듈
- [ ] FormatExpertAgent 구현
- [ ] 띄어쓰기 교정 ≥95% 정확도
- [ ] 외국어 표기법 ≥95% 일관성
- [ ] 단위 테스트 ≥80% 커버리지
- [ ] 성능: 청크당 <5초

## Phase 3: 교열 모듈
- [ ] FactCheckerAgent 구현
- [ ] Context7 MCP 통합
- [ ] 팩트 검증 ≥90% 커버리지
- [ ] 구식 정보 식별 ≥80% 정확도
- [ ] 단위 테스트 ≥80% 커버리지

## Phase 4: 윤문 모듈
- [ ] CopywritingExpertAgent 구현
- [ ] 가독성 개선 ≥10점
- [ ] 톤 일관성 ≥95%
- [ ] 의도 보존 ≥95%
- [ ] 단위 테스트 ≥80% 커버리지

## Phase 5: 통합 및 최적화
- [ ] 전체 E2E 테스트 통과
- [ ] 배치 처리 동작
- [ ] 오류 복구 메커니즘 동작
- [ ] LAF 파일럿 완료
- [ ] 최종 문서화 완료

## 최종 품질 게이트
- [ ] 전체 품질 점수 ≥90점
- [ ] 오류율 <1%
- [ ] 모든 자동화 테스트 통과
- [ ] 수동 검수 완료
- [ ] 프로덕션 배포 승인
```

---

## 📋 다음 단계

1. ✅ 3개 SPEC 문서 작성 완료
   - spec.md: 요구사항 (EARS 형식)
   - plan.md: 구현 계획 (5 Phase)
   - acceptance.md: 수용 기준 (Given-When-Then)

2. ⏳ Phase 1 구현 시작
3. ⏳ 주간 진행 상황 리뷰
4. ⏳ 파일럿 테스트 (LAF)
5. ⏳ 최종 배포 및 확대

---

## 🔗 참고 자료

- [EARS Format Guide](https://www.incose.org/products-and-publications/products/requirements-format-guide)
- [Given-When-Then Testing](https://cucumber.io/docs/gherkin/)
- [Anthropic Claude API](https://docs.anthropic.com)
- [Context7 MCP Documentation](https://context7.upstash.com)
