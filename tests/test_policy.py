import pytest

from onecite.models import Score, Support
from onecite.policy import Policy, decide, rank

DEFAULT = Policy()


def scores(*pairs: tuple[str, float]) -> tuple[Score, ...]:
    return tuple(Score(source_id=i, value=v) for i, v in pairs)


def test_nothing_clearing_the_bar_is_unsupported():
    support, qualified = decide(scores(("a", 0.30), ("b", 0.11)), DEFAULT)
    assert support is Support.UNSUPPORTED
    assert qualified == ()


def test_one_clear_winner_is_supported():
    support, qualified = decide(scores(("a", 0.91), ("b", 0.20)), DEFAULT)
    assert support is Support.SUPPORTED
    assert qualified[0].source_id == "a"


def test_a_clear_margin_over_a_qualifying_runner_up_still_wins():
    support, _ = decide(scores(("a", 0.90), ("b", 0.60)), DEFAULT)
    assert support is Support.SUPPORTED


def test_sources_too_close_to_separate_are_contested():
    support, qualified = decide(scores(("a", 0.71), ("b", 0.69)), DEFAULT)
    assert support is Support.CONTESTED
    assert len(qualified) == 2


def test_the_threshold_is_inclusive():
    support, _ = decide(scores(("a", 0.45)), DEFAULT)
    assert support is Support.SUPPORTED


def test_a_caller_may_demand_stronger_support():
    strict = Policy(support_threshold=0.80)
    assert decide(scores(("a", 0.60)), strict)[0] is Support.UNSUPPORTED
    assert decide(scores(("a", 0.60)), DEFAULT)[0] is Support.SUPPORTED


def test_a_caller_may_widen_what_counts_as_contested():
    fussy = Policy(contest_margin=0.40)
    assert decide(scores(("a", 0.90), ("b", 0.60)), fussy)[0] is Support.CONTESTED


def test_ranking_is_best_first():
    assert [s.source_id for s in rank(scores(("a", 0.2), ("b", 0.9)))] == ["b", "a"]


def test_ties_break_on_source_id_so_the_order_never_moves():
    once = rank(scores(("b", 0.7), ("a", 0.7)))
    twice = rank(scores(("a", 0.7), ("b", 0.7)))
    assert [s.source_id for s in once] == [s.source_id for s in twice] == ["a", "b"]


@pytest.mark.parametrize("value", [0.0, 1.0])
def test_the_extremes_are_handled(value: float):
    decide(scores(("a", value)), DEFAULT)
