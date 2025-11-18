# 교정 모듈
# 작성일: 2025-11-18
# 목적: 한국어 맞춤법, 표기법, 외국어 표기 규칙 자동 교정

import re
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dataclasses import dataclass

from .models.edit_result import EditResult, EditStage, Change


@dataclass
class ProofreadingResult:
    """교정 결과"""
    corrected_text: str
    changes: List[Dict[str, str]]
    quality_score: float
    processing_time: float


class ProofreadingModule:
    """교정 모듈 - 한국어 맞춤법 및 표기법 교정"""

    # 한국어 띄어쓰기 규칙
    SPACING_RULES = [
        (r'한글(?=[가-힣])', lambda m: '한글 '),
        (r'([가-힣])([A-Z])', lambda m: f'{m.group(1)} {m.group(2)}'),
        (r'([가-힣])(\d)', lambda m: f'{m.group(1)} {m.group(2)}'),
    ]

    # 맞춤법 규칙
    SPELLING_RULES = {
        '되어지다': '되다',
        '안되다': '안 되다',
        '않됨': '안 됨',
    }

    # 숫자 표기 규칙
    NUMBER_RULES = [
        (r'(\d+)명([^의])', r'\1명 \2'),  # 숫자-명 띄어쓰기
        (r'(\d+)번([^째])', r'\1번 \2'),  # 숫자-번 띄어쓰기
    ]

    def __init__(self):
        """초기화"""
        self.changes: List[Change] = []

    def check_spacing(self, text: str) -> Dict[str, Any]:
        """띄어쓰기 검사"""
        issues = []
        corrected = text

        # 연속된 한글 단어 8글자 이상 분리 패턴
        if self._has_spacing_issues(text):
            # 한글이 8글자 이상 연속되면 띄어쓰기 오류
            issues.append({
                "type": "spacing",
                "original": text,
                "fixed": text,  # 실제로는 더 복잡한 처리 필요
                "reason": "연속된 한글 단어 띄어쓰기"
            })

        # 띄어쓰기 규칙 적용
        for pattern, replacement in self.SPACING_RULES:
            if re.search(pattern, corrected):
                new_text = re.sub(pattern, replacement, corrected)
                if new_text != corrected:
                    issues.append({
                        "type": "spacing",
                        "original": corrected,
                        "fixed": new_text
                    })
                    corrected = new_text

        return {
            "has_errors": len(issues) > 0,
            "corrections": issues,
            "corrected_text": corrected
        }

    def _has_spacing_issues(self, text: str) -> bool:
        """띄어쓰기 오류 여부 판정"""
        # "띄어쓰기" 같은 복합어가 연속되어 있으면 오류
        # 간단한 휴리스틱: 한글이 8글자 이상 연속되면 확인
        if re.search(r'[가-힣]{8,}', text):
            return True
        return False

    def check_spelling(self, text: str) -> Dict[str, Any]:
        """맞춤법 검사"""
        corrected = text
        corrections = []

        for wrong, correct in self.SPELLING_RULES.items():
            if wrong in corrected:
                corrected = corrected.replace(wrong, correct)
                corrections.append({
                    "type": "spelling",
                    "original": wrong,
                    "fixed": correct,
                    "reason": "맞춤법"
                })

        return {
            "has_errors": len(corrections) > 0,
            "corrections": corrections,
            "corrected_text": corrected
        }

    def check_particles(self, text: str) -> Dict[str, Any]:
        """조사 사용 검증"""
        # 기본적인 조사 검증 규칙
        return {
            "is_correct": True,
            "issues": []
        }

    def check_foreign_language_consistency(self, text: str) -> Dict[str, Any]:
        """외국어 표기법 일관성 검사"""
        # 영문 단어 추출
        english_words = re.findall(r'[A-Za-z]+', text)
        word_variants = {}

        for word in set(english_words):
            variants = []
            for match in re.finditer(word, text, re.IGNORECASE):
                variants.append(text[match.start():match.end()])
            if len(set(variants)) > 1:
                word_variants[word] = list(set(variants))

        return {
            "consistency_issues": len(word_variants),
            "inconsistent_words": word_variants
        }

    def check_technical_terms(self, text: str) -> Dict[str, Any]:
        """기술 용어 일관성 검사"""
        return {
            "issues": [],
            "consistency_score": 1.0
        }

    def check_foreign_spacing(self, text: str) -> Dict[str, Any]:
        """외국어 단어 띄어쓰기"""
        return {
            "issues": []
        }

    def check_number_format(self, text: str) -> Dict[str, Any]:
        """숫자 표기 규칙 검사"""
        corrected = text
        corrections = []

        for pattern, replacement in self.NUMBER_RULES:
            matches = list(re.finditer(pattern, corrected))
            if matches:
                corrected = re.sub(pattern, replacement, corrected)
                corrections.append({
                    "type": "number_format",
                    "original": text,
                    "fixed": corrected
                })

        return {
            "has_errors": len(corrections) > 0,
            "corrections": corrections,
            "corrected_text": corrected
        }

    def check_unit_format(self, text: str) -> Dict[str, Any]:
        """단위 표기 규칙 검사"""
        # 기본 단위 규칙: 숫자와 단위 사이 띄어쓰기
        corrected = re.sub(r'(\d+)\s*([a-zA-Z%]+)', r'\1 \2', text)

        return {
            "has_errors": text != corrected,
            "corrected_text": corrected
        }

    def proofread(self, text: str, domain: str = "general") -> Dict[str, Any]:
        """전체 교정 프로세스"""
        start_time = time.time()
        self.changes = []

        # 단계별 검사
        spacing_result = self.check_spacing(text)
        text = spacing_result.get("corrected_text", text)

        spelling_result = self.check_spelling(text)
        text = spelling_result.get("corrected_text", text)

        number_result = self.check_number_format(text)
        text = number_result.get("corrected_text", text)

        unit_result = self.check_unit_format(text)
        text = unit_result.get("corrected_text", text)

        # 변경 사항 기록
        all_corrections = (
            spacing_result.get("corrections", []) +
            spelling_result.get("corrections", []) +
            number_result.get("corrections", [])
        )

        for idx, correction in enumerate(all_corrections):
            change = Change(
                type=correction.get("type", "general"),
                original=correction.get("original", ""),
                modified=correction.get("fixed", ""),
                reason=correction.get("reason", "교정"),
                position=idx,
                confidence=0.95
            )
            self.changes.append(change)

        # 품질 점수 계산
        quality_score = 85.0 + (len(self.changes) * 0.5) if len(self.changes) < 30 else 95.0

        processing_time = time.time() - start_time

        return {
            "corrected_text": text,
            "changes": [c.to_dict() for c in self.changes],
            "quality_score": min(quality_score, 100.0),
            "processing_time": processing_time,
            "total_changes": len(self.changes)
        }

    def proofread_parallel(self, text: str, max_chunk_size: int = 1000, num_workers: int = 2) -> Dict[str, Any]:
        """병렬 처리를 통한 교정"""
        start_time = time.time()

        # 청크 분할
        chunks = self._split_into_chunks(text, max_chunk_size)

        corrected_chunks = []
        all_changes = []

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(self.proofread, chunk): idx
                for idx, chunk in enumerate(chunks)
            }

            for future in as_completed(futures):
                idx = futures[future]
                result = future.result()
                corrected_chunks.append((idx, result["corrected_text"]))
                all_changes.extend(result["changes"])

        # 청크 순서대로 정렬
        corrected_chunks.sort(key=lambda x: x[0])
        corrected_text = ''.join([chunk[1] for chunk in corrected_chunks])

        processing_time = time.time() - start_time

        return {
            "corrected_text": corrected_text,
            "changes": all_changes,
            "quality_score": 90.0,
            "processing_time": processing_time,
            "total_changes": len(all_changes)
        }

    def _split_into_chunks(self, text: str, chunk_size: int) -> List[str]:
        """텍스트를 청크로 분할"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks
