"""Strategy Pattern: choosing the canonical fragment for a block."""

from dataclasses import dataclass
from datetime import datetime

import pytest

from app.domain.strategies import (
    STRATEGIES,
    EmptyFragmentListError,
    LatestSubmittedStrategy,
    MostDetailedStrategy,
    UnknownStrategyError,
    get_strategy,
)


@dataclass
class Frag:
    id: int
    content: str
    created_at: datetime


T0 = datetime(2026, 11, 28, 9, 0, 0)
T1 = datetime(2026, 11, 28, 9, 5, 0)
T2 = datetime(2026, 11, 28, 9, 10, 0)


def test_most_detailed_selects_longest_trimmed_content() -> None:
    short = Frag(1, "F = ma", T0)
    padded = Frag(2, "   F=ma     \n\n\n      ", T1)  # long only because of whitespace
    detailed = Frag(3, "F = ma, where m is mass and a is acceleration", T2)
    assert MostDetailedStrategy().select([short, padded, detailed]) is detailed


def test_most_detailed_ignores_surrounding_whitespace() -> None:
    a = Frag(1, "abcdef", T0)
    b = Frag(2, "    abc    ", T1)
    assert MostDetailedStrategy().select([b, a]) is a


def test_latest_submitted_selects_latest_timestamp() -> None:
    old, newest, middle = Frag(1, "old", T0), Frag(2, "new", T2), Frag(3, "mid", T1)
    assert LatestSubmittedStrategy().select([old, newest, middle]) is newest


def test_most_detailed_tie_selects_lowest_id() -> None:
    a, b = Frag(7, "same", T0), Frag(4, "four", T1)
    assert MostDetailedStrategy().select([a, b]) is b


def test_latest_submitted_tie_selects_lowest_id() -> None:
    a, b = Frag(9, "x", T2), Frag(3, "y", T2)
    assert LatestSubmittedStrategy().select([a, b]) is b


@pytest.mark.parametrize("strategy", [MostDetailedStrategy(), LatestSubmittedStrategy()])
def test_empty_fragment_list_raises_domain_exception(strategy) -> None:
    with pytest.raises(EmptyFragmentListError):
        strategy.select([])


def test_registry_exposes_both_strategies_by_key() -> None:
    assert set(STRATEGIES) == {"most_detailed", "latest_submitted"}
    assert isinstance(get_strategy("most_detailed"), MostDetailedStrategy)
    assert isinstance(get_strategy("latest_submitted"), LatestSubmittedStrategy)
    assert get_strategy("most_detailed").label == "Most Detailed"


def test_unknown_strategy_key_raises() -> None:
    with pytest.raises(UnknownStrategyError):
        get_strategy("upvotes")
