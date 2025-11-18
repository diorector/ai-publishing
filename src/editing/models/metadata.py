# 메타데이터 모델
# 작성일: 2025-11-18
# 목적: 문서 메타데이터 및 편집 통계 관리

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional


@dataclass
class DocumentMetadata:
    """문서 메타데이터"""
    author: str
    title: str
    domain: str
    created_date: datetime
    page_count: int = 0
    word_count: int = 0
    language: str = "ko"
    version: str = "1.0"
    tags: list = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "author": self.author,
            "title": self.title,
            "domain": self.domain,
            "created_date": self.created_date.isoformat(),
            "page_count": self.page_count,
            "word_count": self.word_count,
            "language": self.language,
            "version": self.version,
            "tags": self.tags,
            "custom_fields": self.custom_fields,
        }


@dataclass
class EditStatistics:
    """편집 통계"""
    total_changes: int = 0
    spacing_errors: int = 0
    spelling_errors: int = 0
    foreign_language_issues: int = 0
    formatting_issues: int = 0
    fact_checking_items: int = 0
    outdated_items: int = 0
    copywriting_improvements: int = 0

    def get_summary(self) -> Dict[str, Any]:
        """통계 요약"""
        return {
            "total_changes": self.total_changes,
            "spacing_errors": self.spacing_errors,
            "spelling_errors": self.spelling_errors,
            "foreign_language_issues": self.foreign_language_issues,
            "formatting_issues": self.formatting_issues,
            "fact_checking_items": self.fact_checking_items,
            "outdated_items": self.outdated_items,
            "copywriting_improvements": self.copywriting_improvements,
        }

    def get_error_distribution(self) -> Dict[str, float]:
        """오류 분포 (백분율)"""
        if self.total_changes == 0:
            return {}

        return {
            "spacing": (self.spacing_errors / self.total_changes) * 100,
            "spelling": (self.spelling_errors / self.total_changes) * 100,
            "foreign_language": (self.foreign_language_issues / self.total_changes) * 100,
            "formatting": (self.formatting_issues / self.total_changes) * 100,
        }


@dataclass
class ProofreadingStatistics(EditStatistics):
    """교정 통계"""
    consistency_issues: int = 0
    number_formatting_issues: int = 0
    unit_formatting_issues: int = 0

    def get_summary(self) -> Dict[str, Any]:
        """교정 통계 요약"""
        base_summary = super().get_summary()
        base_summary.update({
            "consistency_issues": self.consistency_issues,
            "number_formatting_issues": self.number_formatting_issues,
            "unit_formatting_issues": self.unit_formatting_issues,
        })
        return base_summary


@dataclass
class FactCheckingStatistics(EditStatistics):
    """교열 통계"""
    verified_items: int = 0
    suspicious_items: int = 0
    error_items: int = 0
    editor_notes: int = 0

    def get_verification_rate(self) -> float:
        """검증률"""
        if self.fact_checking_items == 0:
            return 0.0
        return (self.verified_items / self.fact_checking_items) * 100

    def get_summary(self) -> Dict[str, Any]:
        """교열 통계 요약"""
        base_summary = super().get_summary()
        base_summary.update({
            "verified_items": self.verified_items,
            "suspicious_items": self.suspicious_items,
            "error_items": self.error_items,
            "editor_notes": self.editor_notes,
            "verification_rate": self.get_verification_rate(),
        })
        return base_summary


@dataclass
class CopywritingStatistics(EditStatistics):
    """윤문 통계"""
    clarity_improvements: int = 0
    readability_improvements: int = 0
    tone_consistency_improvements: int = 0
    flow_improvements: int = 0

    def get_summary(self) -> Dict[str, Any]:
        """윤문 통계 요약"""
        base_summary = super().get_summary()
        base_summary.update({
            "clarity_improvements": self.clarity_improvements,
            "readability_improvements": self.readability_improvements,
            "tone_consistency_improvements": self.tone_consistency_improvements,
            "flow_improvements": self.flow_improvements,
        })
        return base_summary
