"""Composite Pattern (structural): uniform coverage queries over block, lecture, and course.

``AnchorBlockNode`` is the leaf. ``LectureNode`` and ``CourseNode`` are composites that
aggregate their children. Callers (the application service, templates, API) can ask any
node for ``total_blocks()``, ``covered_blocks()``, ``coverage_percent()`` and
``find_gaps()`` without knowing which level of the hierarchy they are holding.

Coverage rule (FR-06): a block is covered when it has at least one non-empty fragment or
non-empty merged content. A node with zero blocks reports 0% coverage.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from dataclasses import dataclass, field


class CoverageNode(ABC):
    """Component interface shared by leaves and composites."""

    @abstractmethod
    def total_blocks(self) -> int:
        """Number of anchor blocks contained in this node."""

    @abstractmethod
    def covered_blocks(self) -> int:
        """Number of contained blocks that are covered."""

    @abstractmethod
    def find_gaps(self) -> list[AnchorBlockNode]:
        """Uncovered blocks (blind spots), in child order."""

    def coverage_percent(self) -> float:
        total = self.total_blocks()
        if total == 0:
            return 0.0
        return self.covered_blocks() / total * 100


@dataclass
class AnchorBlockNode(CoverageNode):
    """Leaf: one anchor (topic/slide) block."""

    block_id: int
    topic: str
    fragment_contents: Sequence[str] = field(default_factory=list)
    merged_content: str | None = None

    def is_covered(self) -> bool:
        has_fragment = any(content.strip() for content in self.fragment_contents)
        has_merged = bool(self.merged_content and self.merged_content.strip())
        return has_fragment or has_merged

    def total_blocks(self) -> int:
        return 1

    def covered_blocks(self) -> int:
        return 1 if self.is_covered() else 0

    def find_gaps(self) -> list[AnchorBlockNode]:
        return [] if self.is_covered() else [self]


@dataclass
class CompositeNode(CoverageNode):
    """Shared aggregation behaviour for composite levels."""

    children: list[CoverageNode] = field(default_factory=list)

    def total_blocks(self) -> int:
        return sum(child.total_blocks() for child in self.children)

    def covered_blocks(self) -> int:
        return sum(child.covered_blocks() for child in self.children)

    def find_gaps(self) -> list[AnchorBlockNode]:
        gaps: list[AnchorBlockNode] = []
        for child in self.children:
            gaps.extend(child.find_gaps())
        return gaps


@dataclass(kw_only=True)
class LectureNode(CompositeNode):
    """Composite: a lecture containing anchor block leaves."""

    lecture_id: int
    title: str


@dataclass(kw_only=True)
class CourseNode(CompositeNode):
    """Composite: a course containing lecture composites."""

    course_id: int
    title: str
