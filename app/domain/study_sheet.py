"""Builder Pattern (creational): step-by-step assembly of a Markdown study sheet.

``StudySheetBuilder`` collects optional parts (course label, coverage summary, ordered
block sections, warnings) through small fluent methods and produces an immutable
``StudySheet``. The builder knows nothing about FastAPI, Jinja2, or SQLAlchemy; the
application service feeds it plain values.

Output layout:

    # <lecture title>
    _Course: <course label>_
    ## Coverage
    ## Warnings        (only when there are warnings)
    ## Notes
    ### 1. <topic>
    ...
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from app.domain.conflict_detector import CONFLICT_WARNING


@dataclass(frozen=True)
class StudySheet:
    """Product: a finished study sheet."""

    title: str
    course_label: str | None
    coverage_lines: tuple[str, ...]
    sections: tuple[str, ...]
    warnings: tuple[str, ...] = field(default_factory=tuple)

    def to_markdown(self) -> str:
        parts: list[str] = [f"# {self.title}"]
        if self.course_label:
            parts.append(f"_Course: {self.course_label}_")
        if self.coverage_lines:
            parts.append("## Coverage\n\n" + "\n".join(self.coverage_lines))
        if self.warnings:
            parts.append("## Warnings\n\n" + "\n".join(f"- {warning}" for warning in self.warnings))
        notes_body = "\n\n".join(self.sections) if self.sections else "_This lecture has no blocks yet._"
        parts.append("## Notes\n\n" + notes_body)
        return "\n\n".join(parts) + "\n"


class StudySheetBuilder:
    """Fluent builder for ``StudySheet``."""

    def __init__(self) -> None:
        self._title: str | None = None
        self._course_label: str | None = None
        self._coverage_lines: list[str] = []
        self._sections: list[str] = []
        self._warnings: list[str] = []

    def with_title(self, title: str, course_label: str | None = None) -> StudySheetBuilder:
        self._title = title.strip()
        self._course_label = course_label
        return self

    def add_coverage_summary(self, covered: int, total: int, blind_spots: int | None = None) -> StudySheetBuilder:
        percent = (covered / total * 100) if total else 0.0
        self._coverage_lines = [f"- {covered} / {total} blocks covered ({percent:.1f}%)"]
        gaps = (total - covered) if blind_spots is None else blind_spots
        self._coverage_lines.append(f"- Blind spots (blocks with no notes): {gaps}")
        return self

    def add_block_section(
        self,
        position: int,
        topic: str,
        merged_content: str | None,
        fragment_count: int,
        conflict_lines: Sequence[str] = (),
    ) -> StudySheetBuilder:
        heading = f"### {position}. {topic}"
        if merged_content and merged_content.strip():
            body = merged_content.strip()
        elif fragment_count > 0:
            body = (
                f"_Not merged yet — {fragment_count} fragment(s) submitted. "
                "Choose a merge strategy in LecMerge to select a canonical version._"
            )
        else:
            body = "_Blind spot — no notes submitted yet._"

        chunks = [heading, body]
        if conflict_lines:
            candidates = "\n".join(f">   - `{line}`" for line in conflict_lines)
            chunks.append(f"> **{CONFLICT_WARNING}.** Candidate formula lines:\n>\n{candidates}")
            self._warnings.append(f"{position}. {topic}: {CONFLICT_WARNING}")
        self._sections.append("\n\n".join(chunks))
        return self

    def add_warnings(self, warnings: Iterable[str]) -> StudySheetBuilder:
        self._warnings.extend(warning for warning in warnings if warning.strip())
        return self

    def build(self) -> StudySheet:
        if not self._title:
            raise ValueError("A study sheet requires a title; call with_title() first.")
        return StudySheet(
            title=self._title,
            course_label=self._course_label,
            coverage_lines=tuple(self._coverage_lines),
            sections=tuple(self._sections),
            warnings=tuple(self._warnings),
        )

    def build_markdown(self) -> str:
        return self.build().to_markdown()
