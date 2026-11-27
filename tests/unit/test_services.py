"""Unit tests for LecMergeService using a mocked LecMergeRepository (no SQLite)."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.repository import LecMergeRepository
from app.services import LecMergeService, NotFoundError, ValidationError


def _make_fragment(fid: int, author: str, content: str, minute: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        id=fid,
        block_id=10,
        author_name=author,
        content=content,
        created_at=datetime(2026, 11, 28, 10, minute, 0),
    )


def _make_block(
    bid: int,
    order_index: int,
    topic: str,
    fragments: list[SimpleNamespace] | None = None,
    merged_content: str | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        id=bid,
        lecture_id=100,
        order_index=order_index,
        topic=topic,
        merged_content=merged_content,
        fragments=fragments if fragments is not None else [],
    )


def _make_lecture(blocks: list[SimpleNamespace]) -> SimpleNamespace:
    course = SimpleNamespace(id=1, code="CSE 3206", title="Software Engineering", lectures=[])
    lecture = SimpleNamespace(
        id=100,
        course_id=1,
        title="Design Patterns",
        lecture_date="2026-11-28",
        course=course,
        blocks=blocks,
    )
    course.lectures.append(lecture)
    return lecture


@pytest.fixture
def mock_repo() -> MagicMock:
    return MagicMock(spec=LecMergeRepository)


@pytest.fixture
def service(mock_repo: MagicMock) -> LecMergeService:
    return LecMergeService(mock_repo)


def test_create_course_normalizes_and_calls_repo(service: LecMergeService, mock_repo: MagicMock) -> None:
    mock_repo.get_course_by_code.return_value = None
    expected = SimpleNamespace(id=1, code="CSE 3206", title="Software Engineering")
    mock_repo.create_course.return_value = expected

    result = service.create_course("  cse 3206 ", " Software Engineering ")

    assert result is expected
    mock_repo.get_course_by_code.assert_called_once_with("CSE 3206")
    mock_repo.create_course.assert_called_once_with("CSE 3206", "Software Engineering")


def test_create_course_rejects_blank_or_duplicate(service: LecMergeService, mock_repo: MagicMock) -> None:
    with pytest.raises(ValidationError):
        service.create_course("   ", "Title")
    with pytest.raises(ValidationError):
        service.create_course("CSE 3206", "   ")

    mock_repo.get_course_by_code.return_value = SimpleNamespace(id=1, code="CSE 3206")
    with pytest.raises(ValidationError, match="already exists"):
        service.create_course("CSE 3206", "Duplicate")


def test_missing_records_raise_not_found(service: LecMergeService, mock_repo: MagicMock) -> None:
    mock_repo.get_course.return_value = None
    mock_repo.get_lecture.return_value = None
    mock_repo.get_block.return_value = None

    with pytest.raises(NotFoundError):
        service.get_course(999)
    with pytest.raises(NotFoundError):
        service.get_lecture(999)
    with pytest.raises(NotFoundError):
        service.get_block(999)


def test_create_lecture_filters_blank_topics(service: LecMergeService, mock_repo: MagicMock) -> None:
    mock_repo.get_course.return_value = SimpleNamespace(id=1, code="CSE 3206", title="SE")
    service.create_lecture(1, "  Lecture 1 ", [" Composite ", "", "   ", "Strategy"])
    mock_repo.create_lecture_with_blocks.assert_called_once_with(
        course_id=1,
        title="Lecture 1",
        block_topics=["Composite", "Strategy"],
        lecture_date=None,
    )


def test_submit_fragment_validates_and_persists(service: LecMergeService, mock_repo: MagicMock) -> None:
    mock_repo.get_block.return_value = _make_block(10, 1, "Composite")
    expected = _make_fragment(1, "Amina", "F = ma")
    mock_repo.add_fragment.return_value = expected

    result = service.submit_fragment(10, " Amina ", " F = ma ")

    assert result is expected
    mock_repo.add_fragment.assert_called_once_with(10, "Amina", "F = ma")


def test_submit_fragment_rejects_empty_author_or_content(service: LecMergeService, mock_repo: MagicMock) -> None:
    mock_repo.get_block.return_value = _make_block(10, 1, "Composite")

    with pytest.raises(ValidationError):
        service.submit_fragment(10, "  ", "Some content")
    with pytest.raises(ValidationError):
        service.submit_fragment(10, "Amina", "   \n ")
    mock_repo.add_fragment.assert_not_called()


def test_merge_block_selects_via_strategy_and_saves_canonical_content(
    service: LecMergeService, mock_repo: MagicMock
) -> None:
    short = _make_fragment(1, "Amina", "F = ma", minute=1)
    detailed = _make_fragment(2, "Tariq", "F = m * a^2 (detailed explanation here)", minute=2)
    block = _make_block(10, 1, "Newton", fragments=[short, detailed])
    updated_block = _make_block(10, 1, "Newton", fragments=[short, detailed], merged_content=detailed.content)
    mock_repo.get_block.return_value = block
    mock_repo.save_merged_content.return_value = updated_block

    result = service.merge_block(10, "most_detailed")

    mock_repo.save_merged_content.assert_called_once_with(10, detailed.content)
    assert result.selected_fragment_id == 2
    assert result.selected_author == "Tariq"
    assert result.strategy_label == "Most Detailed"
    assert result.fragment_count == 2
    assert result.has_potential_conflict is True


def test_merge_block_rejects_empty_block_and_unknown_strategy(
    service: LecMergeService, mock_repo: MagicMock
) -> None:
    mock_repo.get_block.return_value = _make_block(10, 1, "Empty", fragments=[])

    with pytest.raises(ValidationError, match="no fragments"):
        service.merge_block(10, "most_detailed")
    with pytest.raises(ValidationError, match="Unknown merge strategy"):
        service.merge_block(10, "votes")
    mock_repo.save_merged_content.assert_not_called()


def test_analyze_lecture_and_generate_study_sheet(service: LecMergeService, mock_repo: MagicMock) -> None:
    f1 = _make_fragment(1, "Amina", "F = ma")
    f2 = _make_fragment(2, "Tariq", "F = m * a^2")
    b1 = _make_block(10, 1, "Composite", fragments=[f1, f2], merged_content="F = m * a^2")
    b2 = _make_block(11, 2, "Strategy", fragments=[])
    lecture = _make_lecture([b1, b2])
    mock_repo.get_lecture.return_value = lecture

    analysis = service.analyze_lecture(100)
    assert analysis.total_blocks == 2
    assert analysis.covered_blocks == 1
    assert analysis.coverage_percent == 50.0
    assert analysis.blind_spot_ids == [11]
    assert analysis.blocks[0].status == "MERGED"
    assert analysis.blocks[0].has_potential_conflict is True
    assert analysis.blocks[1].status == "BLIND SPOT"

    sheet = service.generate_study_sheet(100)
    assert "Potential formula conflict — review required" in sheet.markdown
    assert "Blind spot" in sheet.markdown
    assert sheet.filename == "cse-3206-design-patterns-study-sheet.md"


def test_course_coverage_uses_composite(service: LecMergeService, mock_repo: MagicMock) -> None:
    b1 = _make_block(10, 1, "B1", fragments=[_make_fragment(1, "A", "notes")])
    b2 = _make_block(11, 2, "B2", fragments=[])
    lecture = _make_lecture([b1, b2])
    mock_repo.get_course.return_value = lecture.course

    cov = service.get_course_coverage(1)
    assert cov.total_blocks == 2
    assert cov.covered_blocks == 1
    assert cov.coverage_percent == 50.0
    assert cov.blind_spot_count == 1
