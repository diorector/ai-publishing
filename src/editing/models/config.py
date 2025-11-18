# 편집 설정 모델
# 작성일: 2025-11-18
# 목적: 편집 단계별 설정 및 규칙 정의

from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ProofreadingConfig:
    """교정 설정"""
    check_spacing: bool = True
    check_spelling: bool = True
    check_foreign_language: bool = True
    check_numbers: bool = True
    check_symbols: bool = True
    check_consistency: bool = True
    intensity: str = "standard"  # minimal, standard, strict
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def get_active_checks(self) -> List[str]:
        """활성화된 검사 목록"""
        checks = []
        if self.check_spacing:
            checks.append("spacing")
        if self.check_spelling:
            checks.append("spelling")
        if self.check_foreign_language:
            checks.append("foreign_language")
        if self.check_numbers:
            checks.append("numbers")
        if self.check_symbols:
            checks.append("symbols")
        if self.check_consistency:
            checks.append("consistency")
        return checks


@dataclass
class FactCheckingConfig:
    """교열 설정"""
    verify_statistics: bool = True
    verify_dates: bool = True
    verify_organizations: bool = True
    verify_people_names: bool = True
    check_outdated_info: bool = True
    use_context7: bool = True  # Context7 MCP 사용
    reference_year: int = 2025
    intensity: str = "standard"  # light, standard, deep
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def get_active_verifications(self) -> List[str]:
        """활성화된 검증 목록"""
        verifications = []
        if self.verify_statistics:
            verifications.append("statistics")
        if self.verify_dates:
            verifications.append("dates")
        if self.verify_organizations:
            verifications.append("organizations")
        if self.verify_people_names:
            verifications.append("people_names")
        if self.check_outdated_info:
            verifications.append("outdated_info")
        return verifications


@dataclass
class CopywritingConfig:
    """윤문 설정"""
    improve_clarity: bool = True
    improve_readability: bool = True
    maintain_tone: bool = True
    improve_flow: bool = True
    preserve_intent: bool = True
    intensity: str = "standard"  # light, standard, strong
    target_grade_level: int = 12  # 12학년 이상
    custom_rules: Dict[str, Any] = field(default_factory=dict)

    def get_active_improvements(self) -> List[str]:
        """활성화된 개선 항목 목록"""
        improvements = []
        if self.improve_clarity:
            improvements.append("clarity")
        if self.improve_readability:
            improvements.append("readability")
        if self.maintain_tone:
            improvements.append("tone")
        if self.improve_flow:
            improvements.append("flow")
        if self.preserve_intent:
            improvements.append("intent_preservation")
        return improvements


@dataclass
class EditingConfig:
    """전체 편집 설정"""
    document_domain: str = "general"  # startup, finance, law, education, etc
    target_audience: str = "general_public"
    proofreading: ProofreadingConfig = field(default_factory=ProofreadingConfig)
    fact_checking: FactCheckingConfig = field(default_factory=FactCheckingConfig)
    copywriting: CopywritingConfig = field(default_factory=CopywritingConfig)
    max_chunk_size: int = 3000  # 교정용 청크 크기
    fact_check_section_size: int = 5000  # 교열용 섹션 크기
    max_workers: int = 5  # 병렬 처리 워커 수
    enable_parallel_processing: bool = True
    preserve_formatting: bool = True
    custom_terminology: Dict[str, str] = field(default_factory=dict)  # 맞춤 용어
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_settings_summary(self) -> Dict[str, Any]:
        """설정 요약"""
        return {
            "document_domain": self.document_domain,
            "target_audience": self.target_audience,
            "proofreading_checks": self.proofreading.get_active_checks(),
            "fact_checking_verifications": self.fact_checking.get_active_verifications(),
            "copywriting_improvements": self.copywriting.get_active_improvements(),
            "max_chunk_size": self.max_chunk_size,
            "max_workers": self.max_workers,
            "enable_parallel_processing": self.enable_parallel_processing,
        }
