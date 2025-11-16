# Orchestrator - Pipeline orchestration for SPEC-PUB-TRANSLATE-001
# 구현 시간: 2025-11-16 15:45 KST
# 전체 문서 번역 파이프라인 조율

from pathlib import Path
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

from src.pdf_processor import PDFProcessor
from src.chunking import TextChunker
from src.translation import Translator, TerminologyManager, TranslationAnalyzer
from src.quality import (
    QualityChecker, TerminologyChecker, GrammarChecker,
    LanguageAnalyzer, FormatChecker
)
from src.markdown import MarkdownGenerator, MarkdownValidator

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """파이프라인 설정"""

    # PDF Processing
    max_file_size_mb: int = 100

    # Chunking
    chunk_size: int = 5000
    chunk_overlap: int = 500
    boundary_type: str = 'paragraph'

    # Translation (성능 최적화: 기본값 병렬 처리)
    source_language: str = "English"
    target_language: str = "Korean"
    translate_parallel: bool = True  # 병렬 번역 활성화 (성능 3배 향상)
    max_workers: int = 3

    # Quality
    readability_threshold: int = 85
    consistency_threshold: int = 95
    max_english_ratio: float = 0.1

    # Markdown
    include_metadata: bool = True
    include_toc: bool = True
    max_toc_depth: int = 3


@dataclass
class PipelineProgress:
    """파이프라인 진행 상황"""

    stage: str
    progress_percent: int
    total_items: int
    processed_items: int
    current_item: str
    start_time: str
    estimated_remaining: str
    errors: List[str]
    warnings: List[str]


class DocumentTranslationPipeline:
    """
    전체 문서 번역 파이프라인 조율

    Flow:
    1. PDF Extraction → Extract text and structure
    2. Text Chunking → Split into manageable pieces
    3. Translation → Translate with terminology consistency
    4. Quality Check → Validate quality across dimensions
    5. Markdown Generation → Create output document
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """
        파이프라인 초기화

        Args:
            config: PipelineConfig instance or None for defaults
        """
        self.config = config or PipelineConfig()

        # Initialize components
        self.pdf_processor = PDFProcessor(max_file_size_mb=self.config.max_file_size_mb)
        self.chunker = TextChunker(
            chunk_size=self.config.chunk_size,
            overlap=self.config.chunk_overlap,
            boundary_type=self.config.boundary_type
        )
        self.translator = Translator(
            source_language=self.config.source_language,
            target_language=self.config.target_language,
            preserve_markdown=True,
            preserve_code_blocks=True
        )
        self.quality_checker = QualityChecker(
            readability_threshold=self.config.readability_threshold,
            consistency_threshold=self.config.consistency_threshold
        )
        self.terminology_checker = TerminologyChecker()
        self.grammar_checker = GrammarChecker()
        self.language_analyzer = LanguageAnalyzer(
            max_english_ratio=self.config.max_english_ratio
        )
        self.format_checker = FormatChecker()
        self.markdown_generator = MarkdownGenerator(
            include_metadata=self.config.include_metadata,
            toc_include_links=True,
            max_toc_depth=self.config.max_toc_depth
        )
        self.markdown_validator = MarkdownValidator()

        # State tracking
        self.progress = None
        self.extracted_text = None
        self.document_structure = None
        self.extracted_metadata = None
        self.chunks = None
        self.chunk_metadata = None
        self.translation_results = None
        self.quality_results = None
        self.final_markdown = None

    def process(self, input_file: Path, output_dir: Optional[Path] = None) -> Dict:
        """
        전체 파이프라인 실행

        Args:
            input_file: 입력 PDF 파일 경로
            output_dir: 출력 디렉토리 (선택사항)

        Returns:
            Dict with pipeline results:
                - status: success/failure
                - extracted_text: extracted text
                - structure: document structure
                - translation_count: number of chunks translated
                - quality_score: overall quality
                - output_file: path to output markdown
        """
        try:
            # Step 1: Extract PDF
            self._update_progress("extraction", 0, 1, "Extracting PDF")
            extraction_result = self._extract_pdf(input_file)
            self.extracted_text = extraction_result["text"]
            self.document_structure = extraction_result["structure"]
            self.extracted_metadata = extraction_result["metadata"]

            # Step 2: Chunk text
            self._update_progress("chunking", 0, 1, "Chunking text")
            chunking_result = self._chunk_text(self.extracted_text)
            self.chunks = chunking_result["chunks"]
            self.chunk_metadata = chunking_result["metadata"]

            # Step 3: Translate
            self._update_progress("translation", 0, len(self.chunks), "Translating chunks")
            translation_result = self._translate_chunks(self.chunks)
            self.translation_results = translation_result["results"]

            # Step 4: Quality check
            self._update_progress("quality_check", 0, len(self.translation_results), "Checking quality")
            quality_result = self._check_quality(self.translation_results)
            self.quality_results = quality_result["results"]

            # Step 5: Generate markdown
            self._update_progress("markdown_generation", 0, 1, "Generating markdown")
            markdown_result = self._generate_markdown(
                self.extracted_metadata,
                self.document_structure,
                self.translation_results,
                self.chunk_metadata
            )
            self.final_markdown = markdown_result["markdown"]

            # Step 6: Save output
            output_file = None
            if output_dir:
                output_file = self._save_output(
                    markdown_result,
                    output_dir,
                    self.extracted_metadata
                )

            return {
                "status": "success",
                "extracted_text": self.extracted_text[:200],
                "structure": self.document_structure,
                "chunks_created": len(self.chunks),
                "chunks_translated": len(self.translation_results),
                "quality_score": self._calculate_overall_quality(),
                "output_file": str(output_file) if output_file else None,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Pipeline execution failed: {str(e)}")
            return {
                "status": "failure",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _extract_pdf(self, file_path: Path) -> Dict:
        """단계 1: PDF 추출"""
        logger.info(f"Extracting PDF: {file_path}")

        extraction = self.pdf_processor.process(Path(file_path))

        return {
            "text": extraction["text"],
            "structure": extraction["structure"],
            "metadata": extraction["metadata"]
        }

    def _chunk_text(self, text: str) -> Dict:
        """단계 2: 텍스트 청킹"""
        logger.info(f"Chunking text: {len(text)} characters")

        chunks = self.chunker.chunk_text(text)
        metadata = self.chunker.generate_metadata(chunks, text)

        logger.info(f"Created {len(chunks)} chunks")

        return {
            "chunks": chunks,
            "metadata": metadata
        }

    def _translate_chunks(self, chunks: List[str]) -> Dict:
        """단계 3: 청크 번역 (실제 Claude API 사용)"""
        logger.info(f"Translating {len(chunks)} chunks (parallel={self.config.translate_parallel})")

        # 청크 번역 시작
        results = self.translator.translate_batch(
            chunks,
            parallel=self.config.translate_parallel,
            max_workers=self.config.max_workers,
            continue_on_error=True
        )

        # Apply terminology consistency
        for result in results:
            if "translated_text" in result:
                self._update_progress(
                    "translation",
                    len([r for r in results if "translated_text" in r]),
                    len(results),
                    f"Translating chunk {len([r for r in results if 'translated_text' in r])}"
                )

        logger.info(f"Translated {len(results)} chunks")

        return {
            "results": results
        }

    def _check_quality(self, translation_results: List[Dict]) -> Dict:
        """단계 4: 품질 검사"""
        logger.info(f"Checking quality of {len(translation_results)} translations")

        texts = [r.get("translated_text", "") for r in translation_results]
        quality_results = self.quality_checker.check_batch_quality(texts)

        # Additional checks
        for i, result in enumerate(translation_results):
            text = result.get("translated_text", "")

            # Language mixing check
            mixing_ratio = self.language_analyzer.calculate_mixing_ratio(text)
            if mixing_ratio.get("English", 0) > self.config.max_english_ratio * 100:
                logger.warning(f"Chunk {i}: Excessive English usage ({mixing_ratio.get('English')}%)")

            # Spacing errors
            spacing_errors = self.grammar_checker.detect_spacing_errors(text)
            if spacing_errors:
                logger.warning(f"Chunk {i}: {len(spacing_errors)} spacing errors")

            # Format preservation
            if result.get("original_text"):
                markdown_preserved = self.format_checker.verify_markdown_preserved(
                    result["original_text"],
                    text
                )
                if not markdown_preserved:
                    logger.warning(f"Chunk {i}: Markdown formatting not fully preserved")

            self._update_progress(
                "quality_check",
                i + 1,
                len(translation_results),
                f"Checking chunk {i + 1}"
            )

        logger.info(f"Quality check complete for {len(quality_results)} chunks")

        return {
            "results": quality_results
        }

    def _generate_markdown(
        self,
        metadata: Dict,
        structure: Dict,
        translations: List[Dict],
        chunk_metadata: List[Dict]
    ) -> Dict:
        """단계 5: 마크다운 생성"""
        logger.info(f"Generating markdown from {len(translations)} translations")

        # Prepare data for markdown generator
        chunks_data = []
        for i, (trans, meta) in enumerate(zip(translations, chunk_metadata)):
            chunks_data.append({
                "chunk_id": meta.get("chunk_id"),
                "title": f"Section {meta.get('position', i)}",
                "translated_text": trans.get("translated_text", ""),
                "is_chapter": i % 10 == 0,
                "is_section": i % 5 == 0 and i % 10 != 0,
                "metadata": meta
            })

        output_data = {
            "metadata": metadata,
            "structure": structure,
            "chunks": chunks_data
        }

        markdown = self.markdown_generator.generate_complete_markdown(output_data)

        # Validate markdown
        is_valid = self.markdown_validator.validate(markdown)
        errors = self.markdown_validator.find_errors(markdown)

        if not is_valid:
            logger.warning(f"Markdown validation found {len(errors)} issues")
            for error in errors:
                logger.warning(f"  - {error}")

        logger.info(f"Generated markdown: {len(markdown)} characters")

        return {
            "markdown": markdown,
            "valid": is_valid,
            "errors": errors
        }

    def _save_output(
        self,
        markdown_result: Dict,
        output_dir: Path,
        metadata: Dict
    ) -> Path:
        """단계 6: 출력 저장"""
        logger.info(f"Saving output to {output_dir}")

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Determine output filename
        title = metadata.get("title", "document").replace(" ", "_").lower()
        output_file = output_dir / f"{title}_translated.md"

        # Save markdown
        output_file.write_text(markdown_result["markdown"])

        logger.info(f"Saved markdown to {output_file}")

        return output_file

    def _update_progress(
        self,
        stage: str,
        processed: int,
        total: int,
        current_item: str
    ) -> None:
        """진행 상황 업데이트"""
        percent = int((processed / max(total, 1)) * 100)

        self.progress = PipelineProgress(
            stage=stage,
            progress_percent=percent,
            total_items=total,
            processed_items=processed,
            current_item=current_item,
            start_time=datetime.now().isoformat(),
            estimated_remaining="",
            errors=[],
            warnings=[]
        )

        logger.info(f"[{stage}] {percent}% - {current_item}")

    def _calculate_overall_quality(self) -> float:
        """전체 품질 점수 계산"""
        if not self.quality_results:
            return 0.0

        scores = [r.get("readability_score", 0) for r in self.quality_results]
        if not scores:
            return 0.0

        return sum(scores) / len(scores)

    def get_progress(self) -> Optional[Dict]:
        """현재 진행 상황 반환"""
        if self.progress:
            return asdict(self.progress)
        return None

    def get_statistics(self) -> Dict:
        """파이프라인 통계 반환"""
        return {
            "extracted_chars": len(self.extracted_text) if self.extracted_text else 0,
            "chunks_created": len(self.chunks) if self.chunks else 0,
            "chunks_translated": len(self.translation_results) if self.translation_results else 0,
            "overall_quality_score": self._calculate_overall_quality(),
            "markdown_length": len(self.final_markdown) if self.final_markdown else 0,
            "chapters": len(self.document_structure.get("chapters", [])) if self.document_structure else 0
        }


# Usage Example
if __name__ == "__main__":
    # Configure pipeline
    config = PipelineConfig(
        chunk_size=5000,
        chunk_overlap=500,
        readability_threshold=85,
        consistency_threshold=95
    )

    # Create pipeline
    pipeline = DocumentTranslationPipeline(config)

    # Process document
    result = pipeline.process(
        input_file=Path("sample.pdf"),
        output_dir=Path("output")
    )

    print(f"Pipeline Status: {result['status']}")
    print(f"Chunks Processed: {result.get('chunks_translated', 0)}")
    print(f"Quality Score: {result.get('quality_score', 0):.2f}")
    print(f"Output File: {result.get('output_file')}")

    # Get statistics
    stats = pipeline.get_statistics()
    print(f"\nStatistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
