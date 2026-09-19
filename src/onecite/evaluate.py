"""Measuring whether the citations are right.

Most retrieval systems report whether the right chunk was retrieved. That is a
different question from whether the citation attached to a sentence actually
supports it, and it is the easier one — a system can retrieve perfectly and
still cite the wrong passage for every claim.

Three numbers, because three things go wrong:

- **Precision** — of the claims we cited, how many cited the right source. Low
  precision means confident citations a reader cannot verify, which is worse
  than no citation at all.
- **Recall** — of the claims that had a correct source available, how many we
  found. Low recall means a grounded answer presented as ungrounded.
- **Abstention accuracy** — of the claims with no correct source, how many we
  correctly declined to cite. This is the one nobody measures, and it is where
  a system hallucinating a citation is caught.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from onecite.attribute import attribute
from onecite.models import Source
from onecite.policy import Policy
from onecite.scoring import Scorer


@dataclass(frozen=True, slots=True)
class Example:
    """One labelled answer.

    `expected` maps a claim's index to the id of the source that supports it,
    or `None` where nothing in `sources` does. Labelling the `None` cases is
    the work most datasets skip, and they are what abstention accuracy needs.
    """

    answer: str
    sources: tuple[Source, ...]
    expected: dict[int, str | None]


@dataclass(frozen=True, slots=True)
class Report:
    """What the run measured."""

    claims: int
    cited: int
    correct: int
    should_cite: int
    should_abstain: int
    abstained_correctly: int
    unlabelled: int
    """Claims the split produced that the labels do not mention.

    Surfaced rather than ignored: it usually means the segmentation changed and
    the labels are now attached to the wrong indices, which quietly corrupts
    every number above.
    """

    @property
    def precision(self) -> float:
        """Of the claims cited, the share citing the right source."""
        return self.correct / self.cited if self.cited else 0.0

    @property
    def recall(self) -> float:
        """Of the claims with a correct source available, the share found."""
        return self.correct / self.should_cite if self.should_cite else 0.0

    @property
    def abstention_accuracy(self) -> float:
        """Of the claims nothing supported, the share correctly left uncited."""
        if not self.should_abstain:
            return 1.0
        return self.abstained_correctly / self.should_abstain

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0


def evaluate(
    examples: Sequence[Example], scorer: Scorer, *, policy: Policy | None = None
) -> Report:
    """Run the attributor over labelled examples and count what it got right."""
    claims = cited = correct = should_cite = should_abstain = abstained = unlabelled = 0

    for example in examples:
        result = attribute(example.answer, example.sources, scorer, policy=policy)
        for attribution in result.attributions:
            index = attribution.claim.index
            if index not in example.expected:
                unlabelled += 1
                continue

            claims += 1
            wanted = example.expected[index]
            got = attribution.source.id if attribution.source else None

            if wanted is None:
                should_abstain += 1
                abstained += got is None
            else:
                should_cite += 1

            if got is not None:
                cited += 1
                correct += got == wanted

    return Report(
        claims=claims,
        cited=cited,
        correct=correct,
        should_cite=should_cite,
        should_abstain=should_abstain,
        abstained_correctly=abstained,
        unlabelled=unlabelled,
    )
