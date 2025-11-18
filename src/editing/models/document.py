# 편집 대상 문서 모델
# 작성일: 2025-11-18
# 목적: 문서 구조, 메타데이터, 콘텐츠 관리

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional
import re


@dataclass
class Chapter:
    """문서의 장"""
    number: int
    title: str
    level: int = 1
    start_pos: int = 0
    end_pos: int = 0
    sections: List['Section'] = field(default_factory=list)


@dataclass
class Section:
    """문서의 절"""
    number: int
    title: str
    level: int = 2
    start_pos: int = 0
    end_pos: int = 0
    content: str = ""


@dataclass
class DocumentStructure:
    """문서 구조"""
    chapters: List[Chapter] = field(default_factory=list)
    total_sections: int = 0
    total_paragraphs: int = 0
    headings: Dict[int, List[str]] = field(default_factory=dict)

    def analyze(self, content: str) -> None:
        """마크다운 문서 구조 분석"""
        self.chapters = []
        self.total_paragraphs = len(content.split('\n\n'))
        self.headings = {}

        lines = content.split('\n')
        current_chapter = None
        current_section = None
        section_num = 0

        for line in lines:
            if line.startswith('# '):
                # 장 수준
                chapter_num = len(self.chapters) + 1
                title = line.replace('# ', '').strip()
                current_chapter = Chapter(
                    number=chapter_num,
                    title=title,
                    level=1
                )
                self.chapters.append(current_chapter)
                self.headings[1] = self.headings.get(1, []) + [title]
                section_num = 0

            elif line.startswith('## '):
                # 절 수준
                if current_chapter:
                    section_num += 1
                    title = line.replace('## ', '').strip()
                    section = Section(
                        number=section_num,
                        title=title,
                        level=2
                    )
                    current_chapter.sections.append(section)
                    current_section = section
                    self.total_sections += 1
                    self.headings[2] = self.headings.get(2, []) + [title]

        self.total_sections = sum(len(ch.sections) for ch in self.chapters)


@dataclass
class Document:
    """편집 대상 문서"""
    id: str
    title: str
    content: str
    domain: str
    target_audience: str
    word_count: int = 0
    structure: Optional[DocumentStructure] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """초기화 후 처리"""
        # 단어 수 계산
        if self.word_count == 0:
            self.word_count = len(self.content.split())

        # 구조 분석
        if self.structure is None:
            self.structure = DocumentStructure()
            self.structure.analyze(self.content)

        # 메타데이터에 기본 정보 추가
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = self.created_at.isoformat()
        if "domain" not in self.metadata:
            self.metadata["domain"] = self.domain
        if "target_audience" not in self.metadata:
            self.metadata["target_audience"] = self.target_audience

    def get_chapter_content(self, chapter_num: int) -> str:
        """특정 장의 콘텐츠 추출"""
        if not self.structure or chapter_num > len(self.structure.chapters):
            return ""

        chapter = self.structure.chapters[chapter_num - 1]
        start = chapter.start_pos
        end = chapter.end_pos if chapter.end_pos > 0 else len(self.content)
        return self.content[start:end]

    def get_section_content(self, chapter_num: int, section_num: int) -> str:
        """특정 절의 콘텐츠 추출"""
        if not self.structure or chapter_num > len(self.structure.chapters):
            return ""

        chapter = self.structure.chapters[chapter_num - 1]
        if section_num > len(chapter.sections):
            return ""

        section = chapter.sections[section_num - 1]
        return section.content

    def update_content(self, new_content: str) -> None:
        """문서 내용 업데이트"""
        self.content = new_content
        self.word_count = len(new_content.split())
        self.updated_at = datetime.now()

        # 구조 재분석
        if self.structure:
            self.structure.analyze(new_content)

    def get_statistics(self) -> Dict[str, Any]:
        """문서 통계"""
        return {
            "id": self.id,
            "title": self.title,
            "word_count": self.word_count,
            "domain": self.domain,
            "target_audience": self.target_audience,
            "chapters": len(self.structure.chapters) if self.structure else 0,
            "sections": self.structure.total_sections if self.structure else 0,
            "paragraphs": self.structure.total_paragraphs if self.structure else 0,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
