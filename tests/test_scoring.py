from onecite.models import Claim, Source
from onecite.scoring import LexicalScorer, Scorer, tokens
from tests.fakes import ScriptedScorer


def claim(text: str) -> Claim:
    return Claim(index=0, text=text)


def test_the_lexical_scorer_satisfies_the_protocol():
    assert isinstance(LexicalScorer(), Scorer)


def test_a_scripted_scorer_satisfies_the_same_protocol():
    assert isinstance(ScriptedScorer(), Scorer)


def test_stopwords_do_not_count_as_overlap():
    assert tokens("the torque is 240 Nm") == {"torque", "240", "nm"}


def test_german_stopwords_are_removed_too():
    assert tokens("das Drehmoment ist 240 Nm") == {"drehmoment", "240", "nm"}


def test_a_source_stating_the_claim_scores_high():
    scorer = LexicalScorer()
    value = scorer.score(
        claim("torque 240 Nm"), Source(id="s", text="Tighten to a torque of 240 Nm.")
    )
    assert value == 1.0


def test_a_source_sharing_words_but_not_the_figure_scores_lower():
    scorer = LexicalScorer()
    with_figure = scorer.score(claim("torque 240 Nm"), Source(id="a", text="torque of 240 Nm"))
    without = scorer.score(claim("torque 240 Nm"), Source(id="b", text="torque of 190 Nm"))
    assert without < with_figure


def test_an_unrelated_source_scores_zero():
    scorer = LexicalScorer()
    assert scorer.score(claim("torque 240 Nm"), Source(id="s", text="Safety notes.")) == 0.0


def test_a_claim_of_only_stopwords_scores_zero_rather_than_dividing_by_nothing():
    scorer = LexicalScorer()
    assert scorer.score(claim("it is the"), Source(id="s", text="anything")) == 0.0
