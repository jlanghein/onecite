"""A scorer that returns whatever a test tells it to."""

from dataclasses import dataclass, field

from onecite.models import Claim, Source


@dataclass
class ScriptedScorer:
    """Looks up (claim index, source id) in a table, defaulting to zero."""

    table: dict[tuple[int, str], float] = field(default_factory=dict)
    calls: int = 0

    def score(self, claim: Claim, source: Source) -> float:
        self.calls += 1
        return self.table.get((claim.index, source.id), 0.0)


@dataclass
class BrokenScorer:
    """Returns a value outside 0..1, or a non-number."""

    value: object = 1.7

    def score(self, claim: Claim, source: Source) -> float:
        return self.value  # type: ignore[return-value]
