"""Attributing an answer to its sources.

Orchestration and nothing else: the decisions live in `policy`, the judgement
in the caller's `scorer`, the splitting in `claims`.
"""

from collections.abc import Sequence

from onecite.claims import split
from onecite.errors import NoSourcesError
from onecite.models import AttributedAnswer, Attribution, Claim, Score, Source, Support
from onecite.policy import Policy, decide
from onecite.scoring import Scorer, check


def attribute(
    answer: str,
    sources: Sequence[Source],
    scorer: Scorer,
    *,
    policy: Policy | None = None,
) -> AttributedAnswer:
    """Attribute each claim in an answer to at most one source.

    At most one. A claim backed by three sources gets the best of them, not all
    three — and a claim backed by none gets nothing at all, which is the
    outcome this library exists to make visible.
    """
    if not sources:
        message = "attribute() needs at least one source; retrieval returned none"
        raise NoSourcesError(message)

    active = policy or Policy()
    by_id = {s.id: s for s in sources}

    return AttributedAnswer(
        attributions=tuple(
            _attribute_claim(claim, sources, by_id, scorer, active) for claim in split(answer)
        )
    )


def _attribute_claim(
    claim: Claim,
    sources: Sequence[Source],
    by_id: dict[str, Source],
    scorer: Scorer,
    policy: Policy,
) -> Attribution:
    scores = tuple(
        Score(source_id=s.id, value=check(scorer.score(claim, s), scorer)) for s in sources
    )
    support, qualified = decide(scores, policy)

    if support is Support.UNSUPPORTED:
        return Attribution(claim=claim, support=support, source=None, score=0.0)

    best = qualified[0]
    cite = support is Support.SUPPORTED or policy.allow_contested_citation
    return Attribution(
        claim=claim,
        support=support,
        source=by_id[best.source_id] if cite else None,
        score=best.value,
        runners_up=qualified[1:],
    )
