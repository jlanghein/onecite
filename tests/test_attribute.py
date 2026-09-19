import pytest

from onecite.attribute import attribute
from onecite.errors import NoSourcesError, ScorerError
from onecite.models import Source, Support
from onecite.policy import Policy
from tests.fakes import BrokenScorer, ScriptedScorer

TORQUE = Source(id="s1", text="Tighten the main bolts to 240 Nm.", locator="V47 manual p.112")
OIL = Source(id="s2", text="Change gearbox oil every 5,000 operating hours.", locator="p.88")
NOISE = Source(id="s3", text="General safety notes for maintenance work.", locator="p.4")

ANSWER = "The torque is 240 Nm. Oil changes are due every 5,000 hours."


def test_each_claim_gets_at_most_one_source():
    scorer = ScriptedScorer({(0, "s1"): 0.92, (0, "s2"): 0.61, (0, "s3"): 0.55})
    result = attribute("The torque is 240 Nm.", [TORQUE, OIL, NOISE], scorer)

    assert result.citation_count == 1
    assert result.attributions[0].source is TORQUE


def test_the_others_that_qualified_are_kept_as_runners_up():
    scorer = ScriptedScorer({(0, "s1"): 0.92, (0, "s2"): 0.61})
    result = attribute("The torque is 240 Nm.", [TORQUE, OIL], scorer)

    assert [s.source_id for s in result.attributions[0].runners_up] == ["s2"]


def test_a_claim_nothing_supports_is_not_cited():
    scorer = ScriptedScorer({(0, "s1"): 0.10})
    result = attribute("The warranty runs for seven years.", [TORQUE], scorer)

    attribution = result.attributions[0]
    assert attribution.support is Support.UNSUPPORTED
    assert attribution.source is None
    assert not attribution.is_cited
    assert result.unsupported == (attribution,)


def test_unsupported_claims_are_the_headline_number():
    scorer = ScriptedScorer({(0, "s1"): 0.92})
    result = attribute(ANSWER, [TORQUE], scorer)

    assert len(result.unsupported) == 1
    assert result.grounded_fraction == pytest.approx(0.5)


def test_sources_too_close_to_separate_are_contested():
    scorer = ScriptedScorer({(0, "s1"): 0.71, (0, "s2"): 0.69})
    result = attribute("The torque is 240 Nm.", [TORQUE, OIL], scorer)

    assert result.contested == result.attributions
    assert result.attributions[0].source is TORQUE


def test_a_caller_may_refuse_to_cite_a_contested_claim():
    scorer = ScriptedScorer({(0, "s1"): 0.71, (0, "s2"): 0.69})
    result = attribute(
        "The torque is 240 Nm.",
        [TORQUE, OIL],
        scorer,
        policy=Policy(allow_contested_citation=False),
    )

    assert result.attributions[0].support is Support.CONTESTED
    assert result.attributions[0].source is None


def test_every_source_is_scored_against_every_claim():
    scorer = ScriptedScorer()
    attribute(ANSWER, [TORQUE, OIL, NOISE], scorer)
    assert scorer.calls == 6


def test_attributing_with_no_sources_is_a_caller_bug():
    with pytest.raises(NoSourcesError):
        attribute(ANSWER, [], ScriptedScorer())


@pytest.mark.parametrize("bad", [1.7, -0.2, float("nan"), "high", None])
def test_a_scorer_returning_nonsense_fails_loudly(bad: object):
    with pytest.raises(ScorerError):
        attribute("The torque is 240 Nm.", [TORQUE], BrokenScorer(value=bad))


def test_an_answer_with_no_claims_attributes_to_nothing():
    result = attribute("Yes.", [TORQUE], ScriptedScorer())
    assert result.attributions == ()
    assert result.grounded_fraction == 0.0
