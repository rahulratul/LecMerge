"""Builder Pattern: Markdown study-sheet assembly."""

import pytest

from app.domain.study_sheet import StudySheet, StudySheetBuilder


def full_sheet() -> StudySheet:
    return (
        StudySheetBuilder()
        .with_title("Lecture 3: Design Patterns", course_label="CSE 3206 — Software Engineering")
        .add_coverage_summary(covered=2, total=3)
        .add_block_section(1, "Composite Pattern", merged_content="Treat parts and wholes uniformly.", fragment_count=2)
        .add_block_section(2, "Strategy Pattern", merged_content=None, fragment_count=0)
        .add_block_section(
            3,
            "Newton",
            merged_content="F = ma",
            fragment_count=2,
            conflict_lines=["F = ma", "F = m a^2"],
        )
        .build()
    )


def test_generates_title_and_ordered_block_headings() -> None:
    md = full_sheet().to_markdown()
    assert md.startswith("# Lecture 3: Design Patterns\n")
    assert "CSE 3206 — Software Engineering" in md
    first = md.index("### 1. Composite Pattern")
    second = md.index("### 2. Strategy Pattern")
    third = md.index("### 3. Newton")
    assert first < second < third


def test_includes_merged_content_when_present() -> None:
    assert "Treat parts and wholes uniformly." in full_sheet().to_markdown()


def test_includes_placeholder_for_empty_block() -> None:
    md = full_sheet().to_markdown()
    section = md[md.index("### 2. Strategy Pattern"):md.index("### 3. Newton")]
    assert "Blind spot" in section


def test_includes_status_for_unmerged_block_with_fragments() -> None:
    md = StudySheetBuilder().with_title("L").add_block_section(1, "Open", None, fragment_count=3).build_markdown()
    assert "Not merged yet" in md
    assert "3 fragment(s)" in md


def test_includes_warning_for_potential_formula_conflict() -> None:
    sheet = full_sheet()
    md = sheet.to_markdown()
    assert "Potential formula conflict — review required" in md
    assert "`F = m a^2`" in md
    assert len(sheet.warnings) == 1
    assert "3. Newton" in sheet.warnings[0]
    # Merging (block 3 has merged content) must not erase the warning.
    newton_section = md[md.index("### 3. Newton"):]
    assert "Potential formula conflict — review required" in newton_section


def test_coverage_summary_is_rendered() -> None:
    md = full_sheet().to_markdown()
    assert "## Coverage" in md
    assert "2 / 3 blocks covered (66.7%)" in md


def test_empty_lecture_produces_readable_markdown() -> None:
    md = StudySheetBuilder().with_title("Empty").add_coverage_summary(0, 0).build_markdown()
    assert md.startswith("# Empty\n")
    assert "0 / 0 blocks covered (0.0%)" in md
    assert "This lecture has no blocks yet." in md
    assert "## Warnings" not in md
    assert md.endswith("\n")
    assert "\n\n\n" not in md


def test_non_empty_markdown_has_no_triple_blank_lines() -> None:
    md = full_sheet().to_markdown()
    assert "\n\n\n" not in md
    assert md.endswith("\n")


def test_extra_warnings_are_listed() -> None:
    md = StudySheetBuilder().with_title("L").add_warnings(["Manual note"]).build_markdown()
    assert "## Warnings" in md
    assert "- Manual note" in md


def test_build_without_title_raises() -> None:
    with pytest.raises(ValueError):
        StudySheetBuilder().build()
