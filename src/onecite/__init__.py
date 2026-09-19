"""Cite one source per fact, and refuse to cite a source that does not support it."""

from onecite.attribute import attribute
from onecite.claims import split
from onecite.errors import NoSourcesError, OneciteError, ScorerError
from onecite.evaluate import Example, Report, evaluate
from onecite.models import (
    AttributedAnswer,
    Attribution,
    Claim,
    Score,
    Source,
    Support,
)
from onecite.policy import Policy
from onecite.scoring import LexicalScorer, Scorer

__all__ = [
    "AttributedAnswer",
    "Attribution",
    "Claim",
    "Example",
    "LexicalScorer",
    "NoSourcesError",
    "OneciteError",
    "Policy",
    "Report",
    "Score",
    "Scorer",
    "ScorerError",
    "Source",
    "Support",
    "attribute",
    "evaluate",
    "split",
]
