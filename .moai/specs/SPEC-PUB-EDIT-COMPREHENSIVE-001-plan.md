# SPEC-PUB-EDIT-COMPREHENSIVE-001: 구현 계획

**Version**: 1.0.0
**Status**: DRAFT
**Created**: 2025-11-18
**Target Completion**: 2025-12-20

---

## 📅 실행 계획 개요

포괄적 편집 도구의 구현을 **5개 단계**로 분해합니다. 각 단계는 독립적 가치를 제공하며, 단계별로 테스트 및 검증 가능합니다.

```
Phase 1: 기반 인프라 구축 (1주)
   ↓
Phase 2: 교정 모듈 개발 (2주)
   ↓
Phase 3: 교열 모듈 개발 (2주)
   ↓
Phase 4: 윤문 모듈 개발 (2주)
   ↓
Phase 5: 통합 및 최적화 (1주)
```

**전체 예상 기간**: 8주 (2025-11-18 ~ 2025-01-12)

---

## 🏗️ Phase 1: 기반 인프라 구축 (1주)

**목표**: 편집 도구의 핵심 아키텍처 및 데이터 구조 완성

### 1.1 프로젝트 구조 설계

**생성 파일**:
```
editing/
├── __init__.py
├── config.json                    # 편집 설정
├── edit_orchestrator.py           # 메인 오케스트레이터
├── edit_types.py                  # 타입 및 데이터 구조
├── models/
│   ├── __init__.py
│   ├── document.py                # 문서 모델
│   ├── edit_result.py             # 편집 결과 모델
│   └── metadata.py                # 메타데이터 모델
├── utils/
│   ├── __init__.py
│   ├── file_handler.py            # 파일 I/O
│   ├── formatter.py               # 마크다운 포맷팅
│   ├── progress_tracker.py        # 진행률 추적
│   └── diff_generator.py          # 변경사항 비교
├── agents/
│   ├── __init__.py
│   ├── format_expert.py           # 교정 에이전트
│   ├── fact_checker.py            # 교열 에이전트
│   ├── copywriting_expert.py      # 윤문 에이전트
│   └── base_agent.py              # 에이전트 기본 클래스
└── tests/
    ├── __init__.py
    ├── test_orchestrator.py
    ├── test_proofreading.py
    ├── test_fact_checking.py
    └── test_copywriting.py
```

**주요 의존성**:
```bash
# requirements.txt
anthropic>=0.28.0
pydantic>=2.5.0
python-dotenv>=1.0.0
pdfplumber>=0.10.3  # 기존 번역 도구와 일관성
```

### 1.2 데이터 모델 정의

**문서 모델** (`models/document.py`):
```python
class Document:
    """편집 대상 문서"""
    id: str                          # 문서 ID (UUID)
    title: str                       # 제목
    content: str                     # 전체 내용
    domain: str                      # 도메인 (startup, finance, law, etc)
    target_audience: str             # 대상 독자
    word_count: int                  # 단어 수
    structure: DocumentStructure     # 문서 구조 (장/절/단락)
    metadata: Dict[str, Any]         # 추가 메타데이터
    created_at: datetime
    updated_at: datetime

class EditResult:
    """편집 결과"""
    document_id: str
    stage: EditStage                 # PROOFREADING / FACT_CHECKING / COPYWRITING
    original_text: str               # 원본
    edited_text: str                 # 편집본
    changes: List[Change]            # 변경 사항 목록
    quality_score: float             # 0-100
    processing_time: float           # 초 단위
    metadata: Dict[str, Any]
```

### 1.3 설정 관리

**edit_config.json**:
```json
{
  "proofreading": {
    "enabled": true,
    "model": "claude-haiku-4-5-20251001",
    "chunk_size": 3000,
    "max_workers": 20,
    "timeout_seconds": 30,
    "rules": {
      "spelling": true,
      "spacing": true,
      "foreign_notation": true,
      "symbols": true
    }
  },
  "fact_checking": {
    "enabled": true,
    "model": "claude-haiku-4-5-20251001",
    "section_size": 5000,
    "max_workers": 20,
    "context7_enabled": true,
    "timeout_seconds": 60,
    "verification_items": [
      "statistics", "dates", "organizations", "facts"
    ]
  },
  "copywriting": {
    "enabled": true,
    "model": "claude-haiku-4-5-20251001",
    "paragraph_based": true,
    "max_workers": 20,
    "timeout_seconds": 45,
    "improvements": [
      "clarity", "flow", "tone_consistency", "readability"
    ]
  },
  "quality_gates": {
    "proofreading_min_score": 75,
    "fact_checking_min_score": 75,
    "copywriting_min_score": 75,
    "overall_min_score": 80
  },
  "batch_processing": {
    "sequential": true,
    "shared_glossary": true,
    "parallel_documents": false,
    "max_documents": 10
  }
}
```

### 1.4 기본 인터페이스 설계

**edit_orchestrator.py의 핵심 클래스**:

```python
class EditOrchestrator:
    """편집 전체 프로세스 오케스트레이션"""

    async def load_document(self, file_path: str) -> Document:
        """문서 로드 및 분석"""
        # 파일 형식 자동 감지
        # 메타데이터 추출
        # 구조 분석
        # 도메인 분류
        pass

    async def analyze_document(self, doc: Document) -> AnalysisReport:
        """문서 분석 (문제점 식별)"""
        # 맞춤법 오류 패턴
        # 팩트 검증 필요 항목
        # 문체 문제점
        pass

    async def edit_comprehensive(
        self,
        doc: Document,
        stages: List[EditStage] = [PROOFREADING, FACT_CHECKING, COPYWRITING]
    ) -> Document:
        """전체 편집 프로세스 실행"""
        for stage in stages:
            doc = await self._execute_stage(doc, stage)
            await self._save_checkpoint(doc, stage)
        return doc

    async def batch_process(
        self,
        file_paths: List[str]
    ) -> BatchProcessResult:
        """여러 문서 배치 처리"""
        # 공통 용어집 생성
        # 문서별 순차 처리
        # 진행률 추적
        pass

    async def _execute_stage(
        self,
        doc: Document,
        stage: EditStage
    ) -> Document:
        """각 편집 단계 실행"""
        if stage == EditStage.PROOFREADING:
            agent = FormatExpertAgent()
        elif stage == EditStage.FACT_CHECKING:
            agent = FactCheckerAgent()
        else:  # COPYWRITING
            agent = CopywritingExpertAgent()

        return await agent.process(doc)
```

### 1.5 로깅 및 추적 시스템

**progress_tracker.py**:
```python
class ProgressTracker:
    """편집 진행률 실시간 추적"""

    def track_stage(self, doc_id: str, stage: str, progress: float):
        """단계별 진행률 기록"""
        pass

    def log_change(self, doc_id: str, change: Change):
        """변경사항 기록 (감사 추적)"""
        pass

    def estimate_completion(self) -> datetime:
        """예상 완료 시간 계산"""
        pass
```

### 1.6 에러 처리 및 복구

**메커니즘**:
- 체크포인트: 각 단계 완료 후 자동 저장
- 오류 격리: 실패한 청크만 재처리
- 상태 유지: 전체 진행 상황 보존

---

## 📝 Phase 2: 교정(Proofreading) 모듈 개발 (2주)

**목표**: 한국어 맞춤법, 외국어 표기법 완벽 교정

### 2.1 FormatExpertAgent 구현

**agents/format_expert.py**:

```python
class FormatExpertAgent:
    """교정 전문가 에이전트"""

    def __init__(self, config: ProofreadingConfig):
        self.model = "claude-haiku-4-5-20251001"
        self.config = config
        self.rules_db = self._load_rules()

    async def process(self, doc: Document) -> Document:
        """문서 교정"""
        chunks = self._chunk_document(
            doc.content,
            self.config.chunk_size
        )

        # 병렬 처리
        edited_chunks = await self._process_parallel(
            chunks,
            self.config.max_workers
        )

        # 청크 통합
        edited_content = self._merge_chunks(edited_chunks)

        return Document(**{
            **doc.dict(),
            "content": edited_content,
            "edit_results": edited_chunks
        })

    async def _process_single_chunk(
        self,
        chunk: str,
        chunk_num: int
    ) -> EditResult:
        """단일 청크 교정"""
        prompt = self._build_proofreading_prompt(chunk)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}]
        )

        # 결과 파싱
        return self._parse_result(response)

    def _build_proofreading_prompt(self, text: str) -> str:
        """교정 프롬프트 작성"""
        return f"""당신은 20년 경력의 출판 교정 전문가입니다.
2025년 11월 기준의 최신 한국어 맞춤법 규칙을 정확히 적용합니다.

【교정 항목】
1. 띄어쓰기 (한글-한글, 한글-숫자, 한글-외국어)
2. 맞춤법 (원칙/예외 모두 숙지)
3. 오타 및 중복 제거
4. 외국어 표기법 일관성
5. 숫자/단위/기호 규칙

【원문】
{text}

【출력 형식 (JSON)】
{{
  "corrected_text": "수정된 전체 텍스트",
  "changes": [
    {{
      "original": "원문",
      "corrected": "수정본",
      "reason": "수정 이유",
      "type": "spelling|spacing|notation|typo|duplication"
    }}
  ],
  "quality_score": 85.5,
  "summary": "주요 수정 사항 요약"
}}"""
```

### 2.2 교정 규칙 데이터베이스

**data/proofreading_rules.json**:
```json
{
  "spacing_rules": [
    {
      "category": "korean_spacing",
      "examples": [
        {"wrong": "한글 맞춤법", "correct": "한글맞춤법", "context": ""}
      ]
    }
  ],
  "notation_rules": [
    {
      "language": "english",
      "rules": [
        {"company": "Google", "variations": ["구글"]},
        {"company": "Amazon", "variations": ["아마존"]}
      ]
    }
  ],
  "symbol_rules": [
    {"symbol": "%", "spacing": "no_space_before", "korean": "퍼센트"}
  ]
}
```

### 2.3 테스트 및 검증

**tests/test_proofreading.py**:

```python
class TestProofreading:
    """교정 모듈 테스트"""

    @pytest.mark.asyncio
    async def test_spacing_correction(self):
        """띄어쓰기 교정 테스트"""
        agent = FormatExpertAgent(config)
        result = await agent.process_chunk("한글맞춤법테스트")
        assert "한글 맞춤법" in result.edited_text

    @pytest.mark.asyncio
    async def test_notation_consistency(self):
        """표기법 일관성 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_parallel_processing(self):
        """병렬 처리 테스트"""
        pass
```

### 2.4 성능 최적화

- **청크 크기**: 5,000자 (테스트로 최적화)
- **워커 수**: 20개 (Haiku 속도 최적)
- **타임아웃**: 30초/청크
- **캐싱**: 규칙 DB 메모리 로드

---

## 🔍 Phase 3: 교열(Fact-checking) 모듈 개발 (2주)

**목표**: 2025년 기준 팩트 검증, Context7 MCP 통합

### 3.1 FactCheckerAgent 구현

**agents/fact_checker.py**:

```python
class FactCheckerAgent:
    """교열 전문가 에이전트"""

    def __init__(self, config: FactCheckingConfig):
        self.model = "claude-3-5-sonnet-20241022"
        self.context7_client = self._init_context7()
        self.config = config

    async def process(self, doc: Document) -> Document:
        """문서 교열"""
        # 검증 필요 항목 식별
        verification_items = await self._identify_items(doc.content)

        # Context7로 팩트 검증
        verification_results = await self._verify_facts(verification_items)

        # 구식 정보 식별
        deprecated_items = await self._identify_deprecated(verification_results)

        # 편집자 주석 생성
        annotated_content = self._generate_annotations(
            doc.content,
            verification_results,
            deprecated_items
        )

        return Document(**{
            **doc.dict(),
            "content": annotated_content,
            "fact_checking_results": verification_results
        })

    async def _identify_items(self, text: str) -> List[VerificationItem]:
        """검증 필요 항목 식별"""
        prompt = f"""다음 텍스트에서 팩트 검증이 필요한 항목을 식별하세요:
- 통계/수치 (년도, 숫자)
- 기관명/인물명
- 역사적 사실
- 기술/과학 정보

【텍스트】
{text}

【출력 형식 (JSON)】
{{
  "items": [
    {{
      "text": "검증할 텍스트",
      "type": "statistic|date|organization|person|fact|technology",
      "context": "앞뒤 문맥"
    }}
  ]
}}"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_items(response)

    async def _verify_facts(
        self,
        items: List[VerificationItem]
    ) -> List[VerificationResult]:
        """Context7 MCP를 활용한 팩트 검증"""
        results = []

        for item in items:
            # Context7 검색
            search_results = await self.context7_client.search(
                query=item.text,
                domain=self.config.domain,
                year=2025
            )

            # 신뢰도 평가
            verification = {
                "item": item,
                "status": self._assess_reliability(search_results),
                "sources": search_results,
                "confidence": self._calculate_confidence(search_results)
            }

            results.append(verification)

        return results

    async def _identify_deprecated(
        self,
        results: List[VerificationResult]
    ) -> List[DeprecatedItem]:
        """구식 정보 식별"""
        deprecated = []

        for result in results:
            if result["status"] == "OUTDATED":
                # 2025년 기준 최신 정보 검색
                current_info = await self._get_current_info(
                    result["item"],
                    result["sources"]
                )

                deprecated.append({
                    "original": result["item"].text,
                    "outdated": result["item"].text,
                    "current": current_info,
                    "confidence": result["confidence"]
                })

        return deprecated

    def _generate_annotations(
        self,
        content: str,
        results: List[VerificationResult],
        deprecated: List[DeprecatedItem]
    ) -> str:
        """편집자 주석 생성"""
        annotated = content

        for item in deprecated:
            old_text = item["original"]
            annotation = f"""{old_text}
✏️ [편집자 주: 2025년 기준: {item["current"]}]"""

            annotated = annotated.replace(old_text, annotation)

        return annotated
```

### 3.2 Context7 MCP 통합

**utils/context7_integration.py**:

```python
class Context7Client:
    """Context7 MCP 클라이언트"""

    async def search(
        self,
        query: str,
        domain: str,
        year: int = 2025
    ) -> List[SearchResult]:
        """Context7로 정보 검색"""
        # MCP 호출
        results = await self._mcp_call(
            "context7.search",
            {
                "query": query,
                "domain": domain,
                "year": year,
                "max_results": 5,
                "confidence_threshold": 0.8
            }
        )

        return results

    async def verify_fact(
        self,
        fact: str,
        context: str
    ) -> VerificationResult:
        """팩트 검증"""
        # MCP 호출
        result = await self._mcp_call(
            "context7.verify",
            {
                "fact": fact,
                "context": context,
                "year": 2025
            }
        )

        return result
```

### 3.3 팩트 검증 규칙

**data/fact_checking_rules.json**:
```json
{
  "verification_types": {
    "statistics": {
      "keywords": ["통계", "수치", "비율", "%", "개"],
      "priority": "high",
      "context7_search": true
    },
    "dates": {
      "keywords": ["년", "월", "일", "시간"],
      "pattern": "\\d{4}년|\\d{1,2}월",
      "priority": "high"
    },
    "organizations": {
      "keywords": ["회사", "기관", "협회", "정부"],
      "priority": "medium",
      "context7_search": true
    }
  },
  "reliability_scoring": {
    "official_source": 1.0,
    "academic_source": 0.9,
    "news_source": 0.7,
    "outdated_source": 0.3
  }
}
```

### 3.4 테스트

**tests/test_fact_checking.py**:

```python
class TestFactChecking:
    """교열 모듈 테스트"""

    @pytest.mark.asyncio
    async def test_identify_verification_items(self):
        """검증 필요 항목 식별 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_context7_integration(self):
        """Context7 통합 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_deprecated_identification(self):
        """구식 정보 식별 테스트"""
        pass
```

---

## ✍️ Phase 4: 윤문(Copywriting) 모듈 개발 (2주)

**목표**: 문체 통일, 명확성 개선, 자연스러운 한국어

### 4.1 CopywritingExpertAgent 구현

**agents/copywriting_expert.py**:

```python
class CopywritingExpertAgent:
    """윤문 전문가 에이전트"""

    def __init__(self, config: CopywritingConfig):
        self.model = "claude-3-5-sonnet-20241022"
        self.config = config

    async def process(self, doc: Document) -> Document:
        """문서 윤문"""
        # 단락 기반 처리
        paragraphs = self._split_paragraphs(doc.content)

        # 병렬 윤문
        improved_paragraphs = await self._improve_parallel(
            paragraphs,
            self.config.max_workers
        )

        # 일관성 검증
        await self._verify_consistency(improved_paragraphs)

        # 단락 재통합
        improved_content = "\n\n".join(improved_paragraphs)

        return Document(**{
            **doc.dict(),
            "content": improved_content,
            "copywriting_results": improved_paragraphs
        })

    async def _improve_single_paragraph(
        self,
        paragraph: str,
        context: str = None
    ) -> str:
        """단락 윤문"""
        prompt = self._build_copywriting_prompt(paragraph, context)

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._extract_improved_text(response)

    def _build_copywriting_prompt(
        self,
        paragraph: str,
        context: str = None
    ) -> str:
        """윤문 프롬프트 작성"""
        return f"""당신은 20년 경력의 출판 윤문 전문가입니다.
원저자의 의도와 톤을 완벽히 보존하면서 가독성을 높입니다.

【윤문 철학】
1. 의미의 충실성 > 구조 변경
   - 저자의 메시지 완벽 전달
   - 뉘앙스와 의도 보존
2. 자연스러운 한국어
   - 번역체 표현 제거
   - 한국 독자 이해 최적화
3. 읽기 쉬운 문장
   - 한 문장 한 개념
   - 긴 문장은 2-3개로 분리

【원문】
{paragraph}

{'【앞뒤 문맥】' + context if context else ''}

【개선본】
(개선된 텍스트만 출력)

【변경 사항】
(주요 개선 사항 설명)"""

    async def _verify_consistency(self, paragraphs: List[str]) -> float:
        """전체 문체 일관성 검증"""
        prompt = f"""다음 문단들이 문체적으로 일관성 있는지 평가하세요.
일관성 점수(0-100)를 제시하세요.

【문단들】
{chr(10).join(paragraphs[:5])}  # 샘플로 처음 5개만

【평가 기준】
- 존댓말 일관성
- 톤앤매너 일관성
- 문체 통일
- 전문성과 친근함의 균형

【출력 형식】
일관성 점수: XX점
주요 문제: [있으면 나열]
개선 제안: [있으면 나열]"""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_score(response)
```

### 4.2 윤문 지침

**data/copywriting_guidelines.json**:
```json
{
    "sentence_structure": {
    "max_length": "40-50자",
    "complexity": "최대 2개 절",
    "passive_ratio": "20% 이하"
  },
  "readability": {
    "grade_level": "고등학교 3학년",
    "flesch_kincaid": 12,
    "improvements": [
      "문단 분해",
      "연결사 명확화",
      "리스트 활용"
    ]
  }
}
```

### 4.3 테스트

**tests/test_copywriting.py**:

```python
class TestCopywriting:
    """윤문 모듈 테스트"""

    @pytest.mark.asyncio
    async def test_sentence_structure_improvement(self):
        """문장 구조 개선 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_tone_consistency(self):
        """톤앤매너 일관성 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_author_intent_preservation(self):
        """저자 의도 보존 테스트"""
        pass

    @pytest.mark.asyncio
    async def test_parallel_processing(self):
        """병렬 처리 테스트"""
        pass
```

---

## 🔧 Phase 5: 통합 및 최적화 (1주)

**목표**: 전체 파이프라인 통합, 성능 최적화, 파일럿 실행

### 5.1 end-to-end 통합

**edit_orchestrator.py 완성**:
```python
async def edit_comprehensive(
    self,
    doc: Document,
    stages: List[EditStage] = None
) -> Document:
    """전체 편집 프로세스"""
    if stages is None:
        stages = [
            EditStage.PROOFREADING,
            EditStage.FACT_CHECKING,
            EditStage.COPYWRITING
        ]

    current_doc = doc

    for stage in stages:
        logger.info(f"Starting {stage.name}...")
        current_doc = await self._execute_stage(current_doc, stage)
        await self._save_checkpoint(current_doc, stage)
        logger.info(f"Completed {stage.name}")

    # 최종 검수
    final_score = await self._final_quality_check(current_doc)

    return current_doc
```

### 5.2 배치 처리 최적화

**최적화 전략**:
1. 문서별 순차 처리 (병렬로는 API 비용 증가)
2. 중간 체크포인트 저장
3. 에러 복구 메커니즘

### 5.3 성능 벤치마크

**테스트 시나리오**:
```python
@pytest.mark.asyncio
async def test_performance_benchmark():
    """성능 벤치마크"""
    test_doc = load_test_document(size="50K_words")

    start = time.time()
    result = await orchestrator.edit_comprehensive(test_doc)
    elapsed = time.time() - start

    assert elapsed < 600  # 10분 이내
    assert result.quality_score >= 90
```

**예상 처리 시간**:
- 50K 단어: 6-8시간
  - 교정: 2-3시간
  - 교열: 2-3시간
  - 윤문: 2-3시간

### 5.4 LAF 문서 파일럿

**파일럿 진행**:
1. LAF 원본 문서 로드
2. 전체 편집 파이프라인 실행
3. 결과 검수 및 평가
4. 병목 지점 식별
5. 최적화

### 5.5 최종 배포 및 문서화

- README.md 작성
- API 문서 생성
- 사용자 가이드 작성
- 트러블슈팅 가이드

---

## 🚀 마일스톤 요약

| Phase | 작업 | 예상 기간 | 산출물 |
|-------|------|---------|--------|
| **1** | 기반 인프라 | 1주 | 프로젝트 구조, 모델, 설정 |
| **2** | 교정 모듈 | 2주 | FormatExpertAgent, 테스트 |
| **3** | 교열 모듈 | 2주 | FactCheckerAgent, Context7 통합 |
| **4** | 윤문 모듈 | 2주 | CopywritingExpertAgent, 테스트 |
| **5** | 통합/최적화 | 1주 | 배치 처리, 파일럿, 문서화 |
| **Total** | | **8주** | **프로덕션 준비 완료** |

---

## 🔑 주요 의사결정 및 트레이드오프

### 1. 모델 선택

**Haiku vs Sonnet 결정**:
- ✅ 교정: Haiku (빠르고 저렴)
- ✅ 교열: Sonnet (깊이 있는 분석)
- ✅ 윤문: Sonnet (창의성 필요)

**근거**: 비용 최적화 + 품질 우선순위

### 2. 병렬 vs 순차 처리

**선택**:
- 청크 내: 병렬 (최대 20 워커)
- 문서 간: 순차 (API 안정성)

**근거**: API 레이트 한계 고려

### 3. Context7 통합 수준

**선택**: 교열 단계에만 전력 투입

**근거**:
- 팩트 검증이 핵심 가치
- 다른 단계는 LLM 기본 기능으로 충분

---

## 📊 리소스 요청

**개발 리소스**:
- Python 개발자 1명 (풀타임)
- QA 테스터 0.5명

**외부 API**:
- Anthropic Claude API (충분한 크레딧)
- Context7 MCP (활성화)

**인프라**:
- 로컬 개발: MacBook Pro M1+ 권장
- 테스트 데이터: 4개 PDF (200K+ 단어)

---

## 🎯 성공 기준

1. **기술적 성공**:
   - ✅ 4개 단계 모두 구현 완료
   - ✅ 단위 테스트 커버리지 ≥80%
   - ✅ E2E 테스트 모두 통과

2. **성능 기준**:
   - ✅ 50K 단어 문서 6-8시간 처리
   - ✅ 품질 점수 ≥90점
   - ✅ 오류율 <1%

3. **비즈니스 성공**:
   - ✅ LAF 문서 완성 및 출판 가능
   - ✅ 사용자 만족도 ≥4.5/5점
   - ✅ 반복 적용 가능 (SAF, SOSHR, CS)

---

## 📋 다음 단계

1. ✅ 이 구현 계획 검토 및 승인
2. ⏳ Phase 1 시작 (2025-11-18)
3. ⏳ 주간 진행 상황 리뷰
4. ⏳ Phase별 완료 검증
5. ⏳ LAF 문서 파일럿 실행
6. ⏳ 최종 배포 및 다른 문서 적용
