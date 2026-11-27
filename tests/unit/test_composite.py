"""Composite Pattern: coverage and gap calculation across block → lecture → course."""

import pytest

from app.domain.composite import AnchorBlockNode, CourseNode, LectureNode


def block(block_id: int, fragments: list[str] | None = None, merged: str | None = None) -> AnchorBlockNode:
    return AnchorBlockNode(
        block_id=block_id,
        topic=f"Topic {block_id}",
        fragment_contents=fragments or [],
        merged_content=merged,
    )


def test_empty_block_is_uncovered() -> None:
    node = block(1)
    assert node.is_covered() is False
    assert node.total_blocks() == 1
    assert node.covered_blocks() == 0
    assert node.find_gaps() == [node]


def test_block_with_whitespace_only_fragment_is_uncovered() -> None:
    assert block(1, ["   \n\t"]).is_covered() is False


def test_block_with_fragment_is_covered() -> None:
    node = block(1, ["F = ma"])
    assert node.is_covered() is True
    assert node.covered_blocks() == 1
    assert node.find_gaps() == []


def test_block_with_only_merged_content_is_covered() -> None:
    assert block(1, [], merged="Canonical notes").is_covered() is True


def test_lecture_with_mixed_blocks_returns_counts_and_percentage() -> None:
    covered_a, empty, covered_b = block(1, ["a"]), block(2), block(3, merged="m")
    lecture = LectureNode(lecture_id=10, title="L1", children=[covered_a, empty, covered_b])
    assert lecture.total_blocks() == 3
    assert lecture.covered_blocks() == 2
    assert lecture.coverage_percent() == pytest.approx(66.6667, rel=1e-4)
    assert lecture.find_gaps() == [empty]


def test_course_aggregates_multiple_lectures() -> None:
    l1 = LectureNode(lecture_id=1, title="L1", children=[block(1, ["x"]), block(2)])
    l2 = LectureNode(lecture_id=2, title="L2", children=[block(3, ["y"]), block(4, ["z"])])
    course = CourseNode(course_id=1, title="CSE 3206", children=[l1, l2])
    assert course.total_blocks() == 4
    assert course.covered_blocks() == 3
    assert course.coverage_percent() == 75.0
    assert [gap.block_id for gap in course.find_gaps()] == [2]


def test_empty_lecture_returns_zero_percent_without_division_error() -> None:
    lecture = LectureNode(lecture_id=1, title="Empty", children=[])
    assert lecture.total_blocks() == 0
    assert lecture.coverage_percent() == 0.0
    assert lecture.find_gaps() == []


def test_empty_course_returns_zero_percent() -> None:
    assert CourseNode(course_id=1, title="Empty", children=[]).coverage_percent() == 0.0


def test_gaps_preserve_child_order() -> None:
    lecture = LectureNode(lecture_id=1, title="L", children=[block(5), block(2, ["x"]), block(9)])
    assert [gap.block_id for gap in lecture.find_gaps()] == [5, 9]
