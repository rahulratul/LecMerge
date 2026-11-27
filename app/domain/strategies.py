"""Strategy Pattern (behavioral): interchangeable rules for picking a canonical fragment.

A merge never invents text and never deletes submissions; a strategy only *selects* one
of the existing fragments. The chosen fragment is the canonical selection under that rule,
not a "verified" or "correct" version.

Adding a new rule (NFR-05): subclass ``MergeStrategy``, implement ``select`` and register
an instance in ``STRATEGIES``. The application service does not change.

Determinism: when the primary score ties, the fragment with the lowest ``id`` wins.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from datetime import datetime
from typing import Any, Protocol, TypeVar


class FragmentLike(Protocol):
    """Minimal shape a strategy needs. ORM rows and plain dataclasses both satisfy it."""

    id: int
    content: str
    created_at: datetime


F = TypeVar("F", bound=FragmentLike)


class EmptyFragmentListError(ValueError):
    """Raised when a merge is requested for a block with no fragments."""


class UnknownStrategyError(KeyError):
    """Raised when a strategy key is not registered."""


def _best_by(fragments: Sequence[F], score: Callable[[F], Any]) -> F:
    """Highest ``score`` wins; ties go to the lowest id (deterministic)."""
    if not fragments:
        raise EmptyFragmentListError("Cannot merge a block that has no fragments.")
    ordered = sorted(fragments, key=lambda fragment: fragment.id)
    # max() returns the first maximal element, i.e. the lowest id among ties.
    return max(ordered, key=score)


class MergeStrategy(ABC):
    """Strategy interface."""

    key: str
    label: str
    description: str

    @abstractmethod
    def select(self, fragments: Sequence[F]) -> F:
        """Return one of ``fragments`` as the canonical choice."""


class MostDetailedStrategy(MergeStrategy):
    key = "most_detailed"
    label = "Most Detailed"
    description = "Selects the fragment with the longest content after trimming whitespace."

    def select(self, fragments: Sequence[F]) -> F:
        return _best_by(fragments, lambda fragment: len(fragment.content.strip()))


class LatestSubmittedStrategy(MergeStrategy):
    key = "latest_submitted"
    label = "Latest Submitted"
    description = "Selects the most recently submitted fragment."

    def select(self, fragments: Sequence[F]) -> F:
        return _best_by(fragments, lambda fragment: fragment.created_at)


STRATEGIES: dict[str, MergeStrategy] = {
    strategy.key: strategy for strategy in (MostDetailedStrategy(), LatestSubmittedStrategy())
}


def get_strategy(key: str) -> MergeStrategy:
    try:
        return STRATEGIES[key]
    except KeyError:
        raise UnknownStrategyError(f"Unknown merge strategy: {key!r}") from None
