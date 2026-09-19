"""Deciding what gets cited, as pure functions.

The whole judgement of this library, and none of it calls anything. These rules
are what separate a citation a reader can check from one that merely looks
diligent, so they are exercised without a model, a corpus or a network.
"""

from dataclasses import dataclass
from typing import Final

from onecite.models import Score, Support

SUPPORT_THRESHOLD: Final[float] = 0.45
"""Below this, a source is topically related rather than supporting.

The distinction this library exists for. A chunk about bolt torque scores well
against a question about bolt torque while saying nothing about the specific
figure a reader wants to check, and citing it is worse than citing nothing:
it tells the reader the claim was verified.
"""

CONTEST_MARGIN: Final[float] = 0.05
"""How much the best source must beat the runner-up by to win outright.

Within this margin the scorer is not actually distinguishing them, and picking
the top one is a coin toss presented as a judgement.
"""


@dataclass(frozen=True, slots=True)
class Policy:
    """The thresholds a caller may disagree with.

    Supplied rather than fixed, because the right values depend on the scorer.
    A cross-encoder and a lexical baseline do not produce comparable numbers,
    and a threshold tuned for one is meaningless for the other.
    """

    support_threshold: float = SUPPORT_THRESHOLD
    contest_margin: float = CONTEST_MARGIN
    allow_contested_citation: bool = True
    """Whether a contested claim still gets its best source attached.

    True attaches it and reports the contest. False attaches nothing, which
    suits a caller who would rather show no citation than an arguable one.
    """


def rank(scores: tuple[Score, ...]) -> tuple[Score, ...]:
    """Scores best first, ties broken by source id so the order is stable.

    Stability matters: an unstable order makes two runs of the same answer cite
    different sources, and a citation that moves is one nobody trusts.
    """
    return tuple(sorted(scores, key=lambda s: (-s.value, s.source_id)))


def decide(scores: tuple[Score, ...], policy: Policy) -> tuple[Support, tuple[Score, ...]]:
    """The verdict for one claim, and the sources that cleared the bar.

    Returns at most one winner's worth of certainty: this function never says
    "cite these four". Over-citation is not a formatting choice, it is the
    absence of a decision.
    """
    qualified = tuple(s for s in rank(scores) if s.value >= policy.support_threshold)
    if not qualified:
        return Support.UNSUPPORTED, ()
    if len(qualified) == 1:
        return Support.SUPPORTED, qualified

    best, second = qualified[0], qualified[1]
    if best.value - second.value < policy.contest_margin:
        return Support.CONTESTED, qualified
    return Support.SUPPORTED, qualified
