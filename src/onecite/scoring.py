"""How strongly a source supports a claim.

The judgement itself is the caller's: a cross-encoder, a natural-language
inference model, an LLM asked to answer yes or no. This module declares what
such a scorer must look like and ships one that needs nothing, so the library
is testable and usable before anyone has paid for inference.
"""

import math
import re
from typing import Final, Protocol, runtime_checkable

from onecite.errors import ScorerError
from onecite.models import Claim, Source

_WORD: Final[re.Pattern[str]] = re.compile(r"[A-Za-zÀ-ÿ0-9]+")

STOPWORDS: Final[frozenset[str]] = frozenset(
    [
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "has",
        "have",
        "in",
        "is",
        "it",
        "its",
        "of",
        "on",
        "or",
        "that",
        "the",
        "to",
        "was",
        "were",
        "with",
        "which",
        "this",
        "these",
        "those",
        "der",
        "die",
        "das",
        "und",
        "ist",
        "sind",
        "für",
        "von",
        "mit",
        "den",
        "dem",
    ]
)


@runtime_checkable
class Scorer(Protocol):
    """Scores how strongly a source supports a claim, from 0 to 1."""

    def score(self, claim: Claim, source: Source) -> float: ...


def check(value: float, scorer: object) -> float:
    """The score, or `ScorerError` if it is not a number between 0 and 1.

    Checked on every call rather than trusted. A scorer drifting out of range —
    an un-normalised logit, a NaN from an empty input — produces verdicts that
    are wrong in a way no downstream report reveals.
    """
    if not isinstance(value, int | float) or math.isnan(value):
        message = f"{type(scorer).__name__} returned {value!r}, which is not a number"
        raise ScorerError(message)
    if not 0.0 <= value <= 1.0:
        message = f"{type(scorer).__name__} returned {value}, outside 0..1"
        raise ScorerError(message)
    return float(value)


def tokens(text: str) -> set[str]:
    """Content words, lowercased, stopwords removed."""
    return {w for m in _WORD.finditer(text.lower()) if (w := m.group()) not in STOPWORDS}


class LexicalScorer:
    """Overlap between a claim's content words and a source's.

    A baseline, and honest about it: it cannot tell "the torque is 240 Nm" from
    "the torque is not 240 Nm", so it should not be the scorer behind anything
    a person acts on. It exists so the pipeline can be tested deterministically
    and so a caller can see the shape of the output before wiring up a model.

    Numbers are weighted heavily. In technical corpora the figure is usually
    the claim — a source that shares every word except the measurement is the
    single most dangerous thing to cite.
    """

    numeral_weight: Final[float] = 2.0

    def score(self, claim: Claim, source: Source) -> float:
        wanted = tokens(claim.text)
        if not wanted:
            return 0.0
        available = tokens(source.text)

        def weigh(word: str) -> float:
            return self.numeral_weight if any(c.isdigit() for c in word) else 1.0

        total = sum(weigh(w) for w in wanted)
        found = sum(weigh(w) for w in wanted if w in available)
        return found / total
