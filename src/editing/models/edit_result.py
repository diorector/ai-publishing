# 편집 결과 모델
# 작성일: 2025-11-18
# 목적: 편집 단계별 결과 기록 및 변경 사항 추적

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum


class EditStage(Enum):
    """편집 단계"""
    PROOFREADING = "proofreading"      # 교정
    FACT_CHECKING = "fact_checking"    # 교열
    COPYWRITING = "copywriting"        # 윤문


@dataclass
class Change:
    """변경 사항"""
    type: str                          # 변경 유형 (spacing, spelling, formatting 등)
    original: str                      # 원본
    modified: str                      # 수정본
    reason: str                        # 수정 이유
    position: int = 0                  # 문서 내 위치
    confidence: float = 0.9            # 신뢰도 (0-1)
    category: str = ""                 # 카테고리

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "type": self.type,
            "original": self.original,
            "modified": self.modified,
            "reason": self.reason,
            "position": self.position,
            "confidence": self.confidence,
            "category": self.category,
        }


@dataclass
class EditResult:
    """편집 결과"""
    document_id: str
    stage: EditStage
    original_text: str
    edited_text: str
    changes: List[Change] = field(default_factory=list)
    quality_score: float = 0.0         # 품질 점수 (0-100)
    processing_time: float = 0.0       # 처리 시간 (초)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_change(self, change: Change) -> None:
        """변경 사항 추가"""
        self.changes.append(change)

    def calculate_quality_score(self) -> float:
        """품질 점수 계산"""
        if not self.edited_text:
            self.quality_score = 0.0
            return self.quality_score

        # 기본 점수는 신뢰도의 평균
        if self.changes:
            confidences = [c.confidence for c in self.changes]
            avg_confidence = sum(confidences) / len(confidences)
            # 신뢰도를 점수로 변환 (90-100 범위)
            self.quality_score = 90 + (avg_confidence * 10)
        else:
            # 변경 없으면 높은 점수
            self.quality_score = 95.0

        # 상한선 100
        self.quality_score = min(100.0, self.quality_score)
        return self.quality_score

    def get_summary(self) -> Dict[str, Any]:
        """편집 결과 요약"""
        return {
            "document_id": self.document_id,
            "stage": self.stage.value,
            "total_changes": len(self.changes),
            "quality_score": self.quality_score,
            "processing_time": self.processing_time,
            "change_types": self._get_change_type_counts(),
            "created_at": self.created_at.isoformat(),
        }

    def _get_change_type_counts(self) -> Dict[str, int]:
        """변경 유형별 개수"""
        type_counts = {}
        for change in self.changes:
            type_counts[change.type] = type_counts.get(change.type, 0) + 1
        return type_counts

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "document_id": self.document_id,
            "stage": self.stage.value,
            "original_text": self.original_text,
            "edited_text": self.edited_text,
            "changes": [c.to_dict() for c in self.changes],
            "quality_score": self.quality_score,
            "processing_time": self.processing_time,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class BatchEditResult:
    """배치 편집 결과"""
    document_results: List[EditResult] = field(default_factory=list)
    total_processing_time: float = 0.0
    average_quality_score: float = 0.0
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    def add_result(self, result: EditResult) -> None:
        """결과 추가"""
        self.document_results.append(result)
        self._update_statistics()

    def _update_statistics(self) -> None:
        """통계 업데이트"""
        if not self.document_results:
            return

        # 총 처리 시간
        self.total_processing_time = sum(r.processing_time for r in self.document_results)

        # 평균 품질 점수
        quality_scores = [r.quality_score for r in self.document_results]
        self.average_quality_score = sum(quality_scores) / len(quality_scores)

    def mark_completed(self) -> None:
        """완료 표시"""
        self.completed_at = datetime.now()

    def get_summary(self) -> Dict[str, Any]:
        """배치 결과 요약"""
        return {
            "total_documents": len(self.document_results),
            "total_processing_time": self.total_processing_time,
            "average_quality_score": self.average_quality_score,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "documents": [r.get_summary() for r in self.document_results],
        }
