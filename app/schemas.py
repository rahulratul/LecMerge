"""Pydantic request and response schemas for the versioned LecMerge REST API."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _require_non_blank(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank.")
    return cleaned


class ErrorResponse(BaseModel):
    detail: str = Field(..., examples=["Course 99 not found."])


class CourseCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=32, examples=["CSE 3206"])
    title: str = Field(..., min_length=1, max_length=200, examples=["Software Engineering Sessional"])

    @field_validator("code")
    @classmethod
    def _clean_code(cls, value: str) -> str:
        return _require_non_blank(value, "Course code")

    @field_validator("title")
    @classmethod
    def _clean_title(cls, value: str) -> str:
        return _require_non_blank(value, "Course title")


class CourseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    title: str
    created_at: datetime


class AnchorBlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lecture_id: int
    order_index: int
    topic: str
    merged_content: str | None = None
    created_at: datetime


class LectureCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, examples=["Lecture 4: Design Patterns"])
    lecture_date: str | None = Field(default=None, max_length=32, examples=["2026-11-28"])
    block_topics: list[str] = Field(
        default_factory=list,
        examples=[["Composite Pattern", "Strategy Pattern", "Builder Pattern"]],
    )

    @field_validator("title")
    @classmethod
    def _clean_title(cls, value: str) -> str:
        return _require_non_blank(value, "Lecture title")


class LectureOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    lecture_date: str | None = None
    created_at: datetime
    blocks: list[AnchorBlockOut] = Field(default_factory=list)


class FragmentCreate(BaseModel):
    author_name: str = Field(..., min_length=1, max_length=120, examples=["Amina"])
    content: str = Field(..., min_length=1, examples=["F = ma\nApplies to constant mass systems."])

    @field_validator("author_name")
    @classmethod
    def _clean_author(cls, value: str) -> str:
        return _require_non_blank(value, "Contributor name")

    @field_validator("content")
    @classmethod
    def _clean_content(cls, value: str) -> str:
        return _require_non_blank(value, "Fragment content")


class FragmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    block_id: int
    author_name: str
    content: str
    created_at: datetime


class BlockAnalysisOut(BaseModel):
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


class LectureAnalysisOut(BaseModel):
    lecture_id: int
    lecture_title: str
    course_id: int
    course_code: str
    course_title: str
    total_blocks: int
    covered_blocks: int
    coverage_percent: float
    blind_spot_ids: list[int]
    blocks: list[BlockAnalysisOut]


class MergeRequest(BaseModel):
    strategy: Literal["most_detailed", "latest_submitted"] = Field(
        default="most_detailed",
        description="Merge strategy key used to select one canonical fragment.",
        examples=["most_detailed"],
    )


class MergeResponse(BaseModel):
    block_id: int
    strategy_key: str
    strategy_label: str
    selected_fragment_id: int
    selected_author: str
    merged_content: str
    fragment_count: int
    has_potential_conflict: bool
    conflict_lines: list[str]


class StudySheetOut(BaseModel):
    lecture_id: int
    lecture_title: str
    course_code: str
    course_title: str
    total_blocks: int
    covered_blocks: int
    coverage_percent: float
    warnings: list[str]
    filename: str
    markdown: str
