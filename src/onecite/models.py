"""The records this library passes between its layers.

Dataclasses rather than dictionaries: every one of these crosses a module
boundary, and a mapping at a boundary is a missing type.
"""

from dataclasses import dataclass
from enum import StrEnum


class Support(StrEnum):
    """How well a source backs a claim."""

    SUPPORTED = "supported"
    """One source clears the bar. Exactly one citation is attached."""

    UNSUPPORTED = "unsupported"
    """Nothing clears the bar. No citation is attached, and that is the point."""

    CONTESTED = "contested"
    """Several sources clear the bar and disagree too little to separate.

    Named because it is the case that silently becomes over-citation. A caller
    may accept the best source, ask a human, or widen retrieval — but it should
    be a decision, not a default.
    """


@dataclass(frozen=True, slots=True)
class Source:
    """One retrieved passage a claim might be attributed to."""

    id: str
    text: str
    locator: str = ""
    """Where a reader would go to check: a page, a section, a URL.

    Empty is allowed and is a smell. A citation a reader cannot follow is
    decoration.
    """


@dataclass(frozen=True, slots=True)
class Claim:
    """One assertion pulled out of a generated answer."""

    index: int
    text: str


@dataclass(frozen=True, slots=True)
class Score:
    """How strongly one source supports one claim."""

    source_id: str
    value: float


@dataclass(frozen=True, slots=True)
class Attribution:
    """What one claim was attributed to, and why."""

    claim: Claim
    support: Support
    source: Source | None
    score: float
    runners_up: tuple[Score, ...] = ()
    """The other sources that cleared the bar, best first.

    Kept rather than discarded so a caller can show its work, and so
    `CONTESTED` can be explained rather than merely reported.
    """

    @property
    def is_cited(self) -> bool:
        return self.source is not None


@dataclass(frozen=True, slots=True)
class AttributedAnswer:
    """A whole answer, claim by claim."""

    attributions: tuple[Attribution, ...]

    @property
    def unsupported(self) -> tuple[Attribution, ...]:
        """Claims nothing in the sources backs.

        The number that matters. An answer with unsupported claims is one the
        model produced from its own weights, and in a domain where somebody
        acts on the answer that is the failure worth catching.
        """
        return tuple(a for a in self.attributions if a.support is Support.UNSUPPORTED)

    @property
    def contested(self) -> tuple[Attribution, ...]:
        return tuple(a for a in self.attributions if a.support is Support.CONTESTED)

    @property
    def citation_count(self) -> int:
        return sum(1 for a in self.attributions if a.is_cited)

    @property
    def grounded_fraction(self) -> float:
        """Share of claims that carry a citation, between 0 and 1."""
        if not self.attributions:
            return 0.0
        return self.citation_count / len(self.attributions)
