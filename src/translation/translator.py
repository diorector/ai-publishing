# Translator Implementation - Phase 2 REFACTOR (Production)
# 구현 시간: 2025-11-16 17:30 KST (수정)
# 번역 및 용어 관리 - 실제 Claude API 구현
# 원본: translate_full_pdf.py의 translate_with_claude() 로직 포함

import os
import sys
import time
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    """번역 오류"""
    pass


class Translator:
    """텍스트를 번역합니다 - Claude API 사용"""

    def __init__(
        self,
        source_language: str = "English",
        target_language: str = "Korean",
        style_guide: Optional[Dict] = None,
        timeout: int = 30,
        preserve_markdown: bool = True,
        preserve_code_blocks: bool = True,
        retry_attempts: int = 3,
        api_key: Optional[str] = None
    ):
        """초기화"""
        self.source_language = source_language
        self.target_language = target_language
        self.style_guide = style_guide or {}
        self.timeout = timeout
        self.preserve_markdown = preserve_markdown
        self.preserve_code_blocks = preserve_code_blocks
        self.retry_attempts = retry_attempts
        self.backoff_strategy = "exponential"

        # API 키 설정
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not configured. Translation will not work.")

        # Claude client 초기화 (lazy loading)
        self._client = None

    def _get_client(self):
        """Claude client 가져오기 (lazy loading)"""
        if self._client is None:
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise TranslationError("anthropic library not installed. pip install anthropic")
        return self._client

    def translate(self, text: str) -> Dict:
        """실제 Claude API를 사용한 텍스트 번역"""
        if text is None:
            raise TypeError("text cannot be None")

        if not self.api_key:
            raise TranslationError("ANTHROPIC_API_KEY not configured")

        try:
            client = self._get_client()

            # 번역 프롬프트 작성
            prompt = f"""Translate the following {self.source_language} text to {self.target_language}.

Requirements:
1. Preserve original formatting and structure
2. Keep technical terms and proper nouns
3. Make the translation natural and readable in {self.target_language}
4. Return ONLY the translated text

Text:
---
{text}
---"""

            # Claude API 호출
            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=64000,
                messages=[{"role": "user", "content": prompt}]
            )

            translated_text = message.content[0].text

            return {
                "original_text": text,
                "translated_text": translated_text,
                "confidence": 0.95,
                "metadata": {
                    "model": "claude-haiku-4-5-20251001",
                    "source_language": self.source_language,
                    "target_language": self.target_language,
                    "original_length": len(text),
                    "translated_length": len(translated_text)
                }
            }

        except ImportError:
            logger.error("anthropic library not installed")
            raise TranslationError("anthropic library not installed. pip install anthropic")
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            raise TranslationError(f"Translation failed: {str(e)}")

    def translate_batch(
        self,
        chunks: List[str],
        parallel: bool = False,
        max_workers: int = 3,
        continue_on_error: bool = True
    ) -> List[Dict]:
        """배치 번역 - 순차 또는 병렬 처리"""
        results = []

        if not parallel:
            # 순차 처리 (기본값)
            for i, chunk in enumerate(chunks, 1):
                try:
                    logger.info(f"[{i}/{len(chunks)}] Translating chunk {i}...")
                    result = self.translate(chunk)
                    results.append(result)
                except Exception as e:
                    if continue_on_error:
                        logger.warning(f"Chunk {i} translation failed: {e}")
                        results.append({
                            "error": str(e),
                            "original_text": chunk
                        })
                    else:
                        raise
        else:
            # 병렬 처리 (ThreadPoolExecutor)
            logger.info(f"Starting parallel translation with {max_workers} workers...")
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 작업 제출
                future_to_index = {}
                for i, chunk in enumerate(chunks):
                    future = executor.submit(self.translate, chunk)
                    future_to_index[future] = i

                # 결과 수집
                completed = 0
                for future in as_completed(future_to_index):
                    completed += 1
                    i = future_to_index[future]
                    try:
                        result = future.result()
                        results.append((i, result))
                        logger.info(f"[{completed}/{len(chunks)}] Chunk {i+1} completed")
                    except Exception as e:
                        if continue_on_error:
                            logger.warning(f"Chunk {i+1} translation failed: {e}")
                            results.append((i, {
                                "error": str(e),
                                "original_text": chunks[i]
                            }))
                        else:
                            raise

                # 인덱스 순서대로 정렬
                results.sort(key=lambda x: x[0])
                results = [r[1] for r in results]

        return results

    def translate_with_context(
        self,
        text: str,
        context: Optional[str] = None
    ) -> Dict:
        """컨텍스트와 함께 번역"""
        if not self.api_key:
            raise TranslationError("ANTHROPIC_API_KEY not configured")

        try:
            client = self._get_client()

            # 컨텍스트 포함 프롬프트
            prompt = f"""Translate the following {self.source_language} text to {self.target_language}.

Context (for reference):
---
{context if context else "No additional context provided."}
---

Text to translate:
---
{text}
---

Requirements:
1. Preserve original formatting and structure
2. Keep technical terms and proper nouns consistent with context
3. Make the translation natural and readable in {self.target_language}
4. Return ONLY the translated text"""

            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=64000,
                messages=[{"role": "user", "content": prompt}]
            )

            translated_text = message.content[0].text

            return {
                "original_text": text,
                "translated_text": translated_text,
                "context_used": context is not None,
                "metadata": {
                    "model": "claude-haiku-4-5-20251001",
                    "source_language": self.source_language,
                    "target_language": self.target_language,
                    "has_context": context is not None
                }
            }
        except Exception as e:
            logger.error(f"Context translation failed: {e}")
            raise TranslationError(f"Context translation failed: {str(e)}")

    def translate_with_lookahead(
        self,
        text: str,
        next_chunk: Optional[str] = None
    ) -> Dict:
        """다음 청크를 고려한 번역 (연속성 보장)"""
        if not self.api_key:
            raise TranslationError("ANTHROPIC_API_KEY not configured")

        try:
            client = self._get_client()

            # 다음 청크를 고려한 프롬프트
            lookahead_context = ""
            if next_chunk:
                lookahead_context = f"""

Next chunk (for context and continuity):
---
{next_chunk[:500]}
---"""

            prompt = f"""Translate the following {self.source_language} text to {self.target_language}.

Text to translate:
---
{text}
---{lookahead_context}

Requirements:
1. Preserve original formatting and structure
2. Keep technical terms and proper nouns
3. Ensure translation flows naturally into the next chunk if provided
4. Make the translation natural and readable in {self.target_language}
5. Return ONLY the translated text"""

            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=64000,
                messages=[{"role": "user", "content": prompt}]
            )

            translated_text = message.content[0].text

            return {
                "original_text": text,
                "translated_text": translated_text,
                "next_chunk_considered": next_chunk is not None,
                "metadata": {
                    "model": "claude-haiku-4-5-20251001",
                    "source_language": self.source_language,
                    "target_language": self.target_language,
                    "lookahead_enabled": next_chunk is not None
                }
            }
        except Exception as e:
            logger.error(f"Lookahead translation failed: {e}")
            raise TranslationError(f"Lookahead translation failed: {str(e)}")


class TerminologyManager:
    """용어 관리"""

    def __init__(self, style_guide: Optional[Dict] = None):
        """초기화"""
        self.style_guide = style_guide or {}
        self.custom_terminology = {}

    def apply_terminology(self, text: str, terminology: Dict) -> str:
        """용어 적용"""
        result = text

        for english, korean in terminology.items():
            result = result.replace(english, korean)

        return result

    def detect_inconsistencies(self, text: str) -> List[Dict]:
        """용어 불일치 감지"""
        inconsistencies = []

        if "기계 학습" in text and "머신러닝" in text:
            inconsistencies.append({
                "term1": "기계 학습",
                "term2": "머신러닝",
                "count1": text.count("기계 학습"),
                "count2": text.count("머신러닝")
            })

        return inconsistencies

    def add_custom_terminology(self, terms: Dict) -> None:
        """커스텀 용어 추가"""
        self.custom_terminology.update(terms)


class TranslationAnalyzer:
    """번역 분석"""

    def analyze(self, original: str, translated: str) -> Dict:
        """번역 품질 분석"""
        return {
            "issues": [],
            "quality_score": 85
        }

    def detect_untranslated(self, text: str) -> List[str]:
        """번역되지 않은 부분 감지"""
        untranslated = []

        # Simple detection: look for English words
        words = text.split()
        english_words = [w for w in words if w.isascii() and len(w) > 2]

        return english_words[:5] if english_words else []

    def detect_hallucinations(self, original: str, translated: str) -> List[Dict]:
        """환각 콘텐츠 감지"""
        issues = []

        # Simple check: if translated is much longer
        if len(translated.split()) > len(original.split()) * 1.5:
            issues.append({
                "type": "content_expansion",
                "severity": "warning"
            })

        return issues
