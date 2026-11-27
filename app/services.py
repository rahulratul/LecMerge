"""Shared application service layer used by both GUI routes and REST API routes."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.composite import AnchorBlockNode, CourseNode, LectureNode
from app.domain.conflict_detector import ConflictReport, detect_potential_conflict
from app.domain.strategies import (
    EmptyFragmentListError,
    UnknownStrategyError,
    get_strategy,
)
from app.domain.study_sheet import StudySheetBuilder
from app.models import AnchorBlock, Course, Lecture, NoteFragment
from app.repository import LecMergeRepository


class NotFoundError(LookupError):
    """Raised when a requested course, lecture, or anchor block does not exist."""


class ValidationError(ValueError):
    """Raised when input or domain preconditions fail validation."""


@dataclass(frozen=True)
class BlockAnalysis:
    block_id: int
    order_index: int
    topic: str
    fragment_count: int
    has_merged_content: bool
    merged_content: str | None
    is_blind_spot: bool
    has_potential_conflict: bool
    conflict_lines: list[str]
    status: str


@dataclass(frozen=True)
class LectureAnalysis:
    lecture_id: int
    lecture_title: str
    course_id: int
    course_code: str
    course_title: str
    total_blocks: int
    covered_blocks: int
    coverage_percent: float
    blind_spot_ids: list[int]
    blocks: list[BlockAnalysis]


@dataclass(frozen=True)
class CourseCoverage:
    course_id: int
    total_blocks: int
    covered_blocks: int
    coverage_percent: float
    blind_spot_count: int


@dataclass(frozen=True)
class MergeResult:
    block_id: int
    strategy_key: str
    strategy_label: str
    selected_fragment_id: int
    selected_author: str
    merged_content: str
    fragment_count: int
    has_potential_conflict: bool
    conflict_lines: list[str]


@dataclass(frozen=True)
class StudySheetResult:
    lecture_id: int
    lecture_title: str
    course_code: str
    course_title: str
    total_blocks: int
    covered_blocks: int
    coverage_percent: float
    warnings: list[str]
    markdown: str
    filename: str


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "study-sheet"


def _block_status(is_blind_spot: bool, has_merged: bool, has_conflict: bool) -> str:
    if is_blind_spot:
        return "BLIND SPOT"
    if has_conflict and not has_merged:
        return "POTENTIAL CONFLICT"
    if has_merged:
        return "MERGED"
    return "OPEN"


def _to_block_node(block: AnchorBlock) -> AnchorBlockNode:
    return AnchorBlockNode(
        block_id=block.id,
        topic=block.topic,
        fragment_contents=[fragment.content for fragment in block.fragments],
        merged_content=block.merged_content,
    )


def _to_lecture_node(lecture: Lecture) -> LectureNode:
    return LectureNode(
        lecture_id=lecture.id,
        title=lecture.title,
        children=[_to_block_node(block) for block in lecture.blocks],
    )


def _to_course_node(course: Course) -> CourseNode:
    return CourseNode(
        course_id=course.id,
        title=course.title,
        children=[_to_lecture_node(lecture) for lecture in course.lectures],
    )


class LecMergeService:
    """Orchestrates LecMerge use cases across domain logic and persistence."""

    def __init__(self, repository: LecMergeRepository) -> None:
        self._repo = repository

    # --- Courses ---

    def list_courses(self) -> list[Course]:
        return self._repo.list_courses()

    def create_course(self, code: str, title: str) -> Course:
        clean_code = code.strip().upper()
        clean_title = title.strip()
        if not clean_code:
            raise ValidationError("Course code is required.")
        if not clean_title:
            raise ValidationError("Course title is required.")
        if self._repo.get_course_by_code(clean_code) is not None:
            raise ValidationError(f"Course code '{clean_code}' already exists.")
        return self._repo.create_course(clean_code, clean_title)

    def get_course(self, course_id: int) -> Course:
        course = self._repo.get_course(course_id)
        if course is None:
            raise NotFoundError(f"Course {course_id} not found.")
        return course

    def get_course_coverage(self, course_id: int) -> CourseCoverage:
        course = self.get_course(course_id)
        node = _to_course_node(course)
        return CourseCoverage(
            course_id=course.id,
            total_blocks=node.total_blocks(),
            covered_blocks=node.covered_blocks(),
            coverage_percent=round(node.coverage_percent(), 1),
            blind_spot_count=len(node.find_gaps()),
        )

    # --- Lectures & Blocks ---

    def create_lecture(
        self,
        course_id: int,
        title: str,
        block_topics: Sequence[str],
        lecture_date: str | None = None,
    ) -> Lecture:
        self.get_course(course_id)
        clean_title = title.strip()
        if not clean_title:
            raise ValidationError("Lecture title is required.")
        clean_topics = [topic.strip() for topic in block_topics if topic.strip()]
        clean_date = lecture_date.strip() if lecture_date and lecture_date.strip() else None
        return self._repo.create_lecture_with_blocks(
            course_id=course_id,
            title=clean_title,
            block_topics=clean_topics,
            lecture_date=clean_date,
        )

    def get_lecture(self, lecture_id: int) -> Lecture:
        lecture = self._repo.get_lecture(lecture_id)
        if lecture is None:
            raise NotFoundError(f"Lecture {lecture_id} not found.")
        return lecture

    def get_block(self, block_id: int) -> AnchorBlock:
        block = self._repo.get_block(block_id)
        if block is None:
            raise NotFoundError(f"Anchor block {block_id} not found.")
        return block

    # --- Fragments ---

    def submit_fragment(self, block_id: int, author_name: str, content: str) -> NoteFragment:
        self.get_block(block_id)
        clean_author = author_name.strip()
        clean_content = content.strip()
        if not clean_author:
            raise ValidationError("Contributor name is required.")
        if not clean_content:
            raise ValidationError("Fragment content cannot be empty.")
        return self._repo.add_fragment(block_id, clean_author, clean_content)

    # --- Analysis ---

    def analyze_block_entity(self, block: AnchorBlock) -> BlockAnalysis:
        node = _to_block_node(block)
        report: ConflictReport = detect_potential_conflict([f.content for f in block.fragments])
        is_blind_spot = not node.is_covered()
        has_merged = bool(block.merged_content and block.merged_content.strip())
        return BlockAnalysis(
            block_id=block.id,
            order_index=block.order_index,
            topic=block.topic,
            fragment_count=len(block.fragments),
            has_merged_content=has_merged,
            merged_content=block.merged_content,
            is_blind_spot=is_blind_spot,
            has_potential_conflict=report.has_potential_conflict,
            conflict_lines=report.candidate_lines if report.has_potential_conflict else [],
            status=_block_status(is_blind_spot, has_merged, report.has_potential_conflict),
        )

    def analyze_lecture(self, lecture_id: int) -> LectureAnalysis:
        lecture = self.get_lecture(lecture_id)
        lecture_node = _to_lecture_node(lecture)
        gaps = {gap.block_id for gap in lecture_node.find_gaps()}
        block_analyses = [self.analyze_block_entity(block) for block in lecture.blocks]
        return LectureAnalysis(
            lecture_id=lecture.id,
            lecture_title=lecture.title,
            course_id=lecture.course.id,
            course_code=lecture.course.code,
            course_title=lecture.course.title,
            total_blocks=lecture_node.total_blocks(),
            covered_blocks=lecture_node.covered_blocks(),
            coverage_percent=round(lecture_node.coverage_percent(), 1),
            blind_spot_ids=[b.block_id for b in block_analyses if b.block_id in gaps],
            blocks=block_analyses,
        )

    # --- Merge ---

    def merge_block(self, block_id: int, strategy_key: str) -> MergeResult:
        block = self.get_block(block_id)
        try:
            strategy = get_strategy(strategy_key)
        except UnknownStrategyError as exc:
            raise ValidationError(str(exc)) from exc

        try:
            selected = strategy.select(block.fragments)
        except EmptyFragmentListError as exc:
            raise ValidationError(str(exc)) from exc

        updated = self._repo.save_merged_content(block.id, selected.content)
        if updated is None:
            raise NotFoundError(f"Anchor block {block_id} not found.")

        report = detect_potential_conflict([f.content for f in updated.fragments])
        return MergeResult(
            block_id=updated.id,
            strategy_key=strategy.key,
            strategy_label=strategy.label,
            selected_fragment_id=selected.id,
            selected_author=selected.author_name,
            merged_content=updated.merged_content or selected.content,
            fragment_count=len(updated.fragments),
            has_potential_conflict=report.has_potential_conflict,
            conflict_lines=report.candidate_lines if report.has_potential_conflict else [],
        )

    # --- Study sheet export ---

    def generate_study_sheet(self, lecture_id: int) -> StudySheetResult:
        analysis = self.analyze_lecture(lecture_id)
        builder = (
            StudySheetBuilder()
            .with_title(
                analysis.lecture_title,
                course_label=f"{analysis.course_code} — {analysis.course_title}",
            )
            .add_coverage_summary(
                covered=analysis.covered_blocks,
                total=analysis.total_blocks,
                blind_spots=len(analysis.blind_spot_ids),
            )
        )
        for block in analysis.blocks:
            builder.add_block_section(
                position=block.order_index,
                topic=block.topic,
                merged_content=block.merged_content,
                fragment_count=block.fragment_count,
                conflict_lines=block.conflict_lines if block.has_potential_conflict else (),
            )
        sheet = builder.build()
        filename = f"{_slugify(analysis.course_code)}-{_slugify(analysis.lecture_title)}-study-sheet.md"
        return StudySheetResult(
            lecture_id=analysis.lecture_id,
            lecture_title=analysis.lecture_title,
            course_code=analysis.course_code,
            course_title=analysis.course_title,
            total_blocks=analysis.total_blocks,
            covered_blocks=analysis.covered_blocks,
            coverage_percent=analysis.coverage_percent,
            warnings=list(sheet.warnings),
            markdown=sheet.to_markdown(),
            filename=filename,
        )
