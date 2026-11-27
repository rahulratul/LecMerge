"""Deliberately limited, deterministic formula-conflict heuristic (Section 7.4).

This does NOT understand mathematics. It only notices that a block contains more than one
distinct "formula-like" line and asks a human to review them.

Rule:
1. Inspect every fragment line by line.
2. A line is a candidate when it contains ``=`` with non-whitespace text on both sides of
   the first ``=``.
3. Candidates are compared after removing all whitespace (so ``F = ma`` == ``F=ma``).
4. Two or more distinct normalized candidates in one block → potential conflict.

Known limitations (documented in README/DECISIONS):
- False positives: two different but compatible formulas in the same block (e.g. two
  kinematics equations) are flagged; so are lines such as ``a <= b`` or ``x == y``.
- False negatives: equivalent formulas written differently (``F = ma`` vs ``a = F/m``)
  are reported as different; disagreements written in prose without ``=`` are missed.
- A block with no fragments is a blind spot, never a formula conflict.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

CONFLICT_WARNING = "Potential formula conflict — review required"


@dataclass(frozen=True)
class ConflictReport:
    has_potential_conflict: bool
    candidate_lines: list[str] = field(default_factory=list)


def _normalize(line: str) -> str:
    return "".join(line.split())


def extract_formula_candidates(text: str) -> list[str]:
    """Return formula-like lines (stripped) in their original order."""
    candidates: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if "=" not in line:
            continue
        left, right = line.split("=", 1)
        if left.strip() and right.strip():
            candidates.append(line)
    return candidates


def detect_potential_conflict(fragment_contents: Iterable[str]) -> ConflictReport:
    """Compare formula-like lines across all fragments of one block."""
    unique: dict[str, str] = {}
    for content in fragment_contents:
        for line in extract_formula_candidates(content or ""):
            unique.setdefault(_normalize(line), line)
    lines = list(unique.values())
    return ConflictReport(has_potential_conflict=len(lines) >= 2, candidate_lines=lines)
