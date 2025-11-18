# 편집 모듈 패키지
# 작성일: 2025-11-18
# 목적: 한국어 문서 자동 편집 (교정, 교열, 윤문)

from .edit_proofreading import ProofreadingModule
from .edit_fact_checking import FactCheckingModule
from .models import (
    Document,
    DocumentStructure,
    EditResult,
    EditStage,
    Change,
    DocumentMetadata,
    EditStatistics,
    ProofreadingConfig,
    FactCheckingConfig,
    CopywritingConfig,
)

__all__ = [
    "ProofreadingModule",
    "FactCheckingModule",
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

__version__ = "0.1.0"
