"""Limited formula-conflict heuristic (Section 7.4)."""

from app.domain.conflict_detector import (
    CONFLICT_WARNING,
    detect_potential_conflict,
    extract_formula_candidates,
)


def test_two_distinct_formula_lines_trigger_potential_conflict() -> None:
    report = detect_potential_conflict(["Newton: F = ma", "F = m * a^2"])
    assert report.has_potential_conflict is True
    assert report.candidate_lines == ["Newton: F = ma", "F = m * a^2"]


def test_whitespace_only_differences_normalize_to_same_candidate() -> None:
    report = detect_potential_conflict(["F = ma", "F=ma", "  F  =  m a  "])
    assert report.has_potential_conflict is False
    assert report.candidate_lines == ["F = ma"]


def test_no_equals_sign_produces_no_conflict() -> None:
    report = detect_potential_conflict(["Composite treats leaves and groups uniformly.", "Strategy swaps rules."])
    assert report.has_potential_conflict is False
    assert report.candidate_lines == []


def test_empty_fragments_do_not_crash() -> None:
    assert detect_potential_conflict([]).has_potential_conflict is False
    assert detect_potential_conflict(["", "   ", "\n\n"]).has_potential_conflict is False


def test_equals_needs_content_on_both_sides() -> None:
    assert extract_formula_candidates("x =\n= y\n=\n  =  ") == []
    assert extract_formula_candidates("x = 1") == ["x = 1"]


def test_candidates_are_extracted_line_by_line() -> None:
    text = "Intro line\nv = u + at\nmore text\ns = ut + 1/2 at^2"
    assert extract_formula_candidates(text) == ["v = u + at", "s = ut + 1/2 at^2"]


def test_multiple_lines_within_one_block_are_compared() -> None:
    # Documented limitation: different formulas in the same block are flagged for review
    # even if they describe different things.
    report = detect_potential_conflict(["v = u + at\ns = ut + 1/2 at^2"])
    assert report.has_potential_conflict is True


def test_warning_wording_is_cautious() -> None:
    assert CONFLICT_WARNING == "Potential formula conflict — review required"
