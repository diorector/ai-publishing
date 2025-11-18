# 편집 모듈 데이터 모델
# 작성일: 2025-11-18
# 목적: 문서, 편집 결과, 메타데이터 등의 데이터 구조 정의

from .document import Document, DocumentStructure
from .edit_result import EditResult, EditStage, Change
from .metadata import DocumentMetadata, EditStatistics
from .config import ProofreadingConfig, FactCheckingConfig, CopywritingConfig

__all__ = [
    "Document",
    "DocumentStructure",
    "EditResult",
    "EditStage",
    "Change",
    "DocumentMetadata",
    "EditStatistics",
    "ProofreadingConfig",
    "FactCheckingConfig",
    "CopywritingConfig",
]
