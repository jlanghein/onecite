import pytest

from onecite.evaluate import Example, evaluate
from onecite.models import Source
from tests.fakes import ScriptedScorer

TORQUE = Source(id="s1", text="Tighten the main bolts to 240 Nm.")
OIL = Source(id="s2", text="Change gearbox oil every 5,000 operating hours.")


def example(expected: dict[int, str | None]) -> Example:
    return Example(
        answer="The torque is 240 Nm. Oil changes are due every 5,000 hours.",
        sources=(TORQUE, OIL),
        expected=expected,
    )


def test_perfect_attribution_scores_one():
    scorer = ScriptedScorer({(0, "s1"): 0.95, (1, "s2"): 0.95})
    report = evaluate([example({0: "s1", 1: "s2"})], scorer)

    assert report.precision == 1.0
    assert report.recall == 1.0
    assert report.f1 == 1.0


def test_citing_the_wrong_source_costs_precision():
    scorer = ScriptedScorer({(0, "s2"): 0.95, (1, "s2"): 0.95})
    report = evaluate([example({0: "s1", 1: "s2"})], scorer)

    assert report.cited == 2
    assert report.correct == 1
    assert report.precision == pytest.approx(0.5)


def test_missing_an_available_source_costs_recall():
    scorer = ScriptedScorer({(0, "s1"): 0.95})
    report = evaluate([example({0: "s1", 1: "s2"})], scorer)

    assert report.recall == pytest.approx(0.5)
    assert report.precision == 1.0


def test_correctly_declining_to_cite_is_measured():
    scorer = ScriptedScorer({(0, "s1"): 0.95})
    report = evaluate([example({0: "s1", 1: None})], scorer)

    assert report.should_abstain == 1
    assert report.abstention_accuracy == 1.0


def test_inventing_a_citation_is_caught():
    scorer = ScriptedScorer({(0, "s1"): 0.95, (1, "s1"): 0.95})
    report = evaluate([example({0: "s1", 1: None})], scorer)

    assert report.abstention_accuracy == 0.0
    assert report.precision == pytest.approx(0.5)


def test_labels_that_do_not_match_the_split_are_surfaced():
    scorer = ScriptedScorer({(0, "s1"): 0.95})
    report = evaluate([example({0: "s1"})], scorer)

    assert report.unlabelled == 1
    assert report.claims == 1


def test_a_run_with_nothing_to_abstain_on_scores_one():
    scorer = ScriptedScorer({(0, "s1"): 0.95, (1, "s2"): 0.95})
    assert evaluate([example({0: "s1", 1: "s2"})], scorer).abstention_accuracy == 1.0


def test_an_empty_run_reports_zeroes_rather_than_dividing_by_nothing():
    report = evaluate([], ScriptedScorer())
    assert (report.precision, report.recall, report.f1) == (0.0, 0.0, 0.0)
