"""Splitting an answer into claims, as pure functions.

A citation attaches to an assertion, not to a paragraph. Attributing whole
paragraphs is how over-citation starts: a paragraph touches four topics, four
sources look relevant, and all four get cited whether or not any of them backs
the specific sentence a reader is checking.

Nothing here calls a model. Sentence splitting by model is slower, costs money,
and is not more correct on the prose that generated answers actually contain.
"""

import re
from typing import Final

from onecite.models import Claim

_ABBREVIATIONS: Final[frozenset[str]] = frozenset(
    {
        "e.g",
        "i.e",
        "etc",
        "cf",
        "vs",
        "approx",
        "no",
        "fig",
        "eq",
        "al",
        "mr",
        "mrs",
        "ms",
        "dr",
        "prof",
        "st",
        "inc",
        "ltd",
        "co",
        "gmbh",
    }
)

_BOUNDARY: Final[re.Pattern[str]] = re.compile(r"(?<=[.!?])\s+")
_TRAILING_MARKER: Final[re.Pattern[str]] = re.compile(r"\s*\[\d+(?:,\s*\d+)*\]\s*$")
_LIST_PREFIX: Final[re.Pattern[str]] = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def is_lead_in(text: str) -> bool:
    """Whether a fragment introduces something rather than asserting it.

    "Check these:", "The steps are:", "In summary:". They end in a colon
    because the content is what follows, and attributing them produces a
    citation against a sentence that claims nothing.
    """
    return text.rstrip().endswith(":")


MINIMUM_CLAIM_CHARACTERS: Final[int] = 12
"""Below this, a fragment is not an assertion anyone can check.

"Yes.", "In short:", a stray heading. Attributing them produces citations that
look diligent and mean nothing.
"""


def _ends_in_abbreviation(text: str) -> bool:
    tail = text.rstrip()
    if not tail.endswith("."):
        return False
    last = tail[:-1].rsplit(None, 1)[-1] if tail[:-1].split() else ""
    return last.lower().lstrip("(") in _ABBREVIATIONS


def strip_existing_markers(text: str) -> str:
    """Remove trailing `[1]`-style markers a model already wrote.

    A generated answer often arrives pre-cited, and those markers are exactly
    what this library exists to replace. Left in place they also corrupt
    scoring, because the digits are tokens a scorer will happily match on.
    """
    return _TRAILING_MARKER.sub("", text).rstrip()


def split(answer: str) -> tuple[Claim, ...]:
    """The checkable assertions in an answer, in order.

    Sentence boundaries are taken at terminal punctuation followed by
    whitespace, except after a known abbreviation — "approx. 4,900 manuals" is
    one claim, not two. List items are claims in their own right; a bulleted
    answer is the case where paragraph-level attribution is most obviously
    wrong.
    """
    claims: list[str] = []
    for line in answer.splitlines():
        body = _LIST_PREFIX.sub("", line).strip()
        if not body:
            continue

        buffer = ""
        for part in _BOUNDARY.split(body):
            buffer = f"{buffer} {part}".strip() if buffer else part
            if not _ends_in_abbreviation(buffer):
                claims.append(buffer)
                buffer = ""
        if buffer:
            claims.append(buffer)

    kept = [
        stripped
        for raw in claims
        if len(stripped := strip_existing_markers(raw)) >= MINIMUM_CLAIM_CHARACTERS
        and not is_lead_in(stripped)
    ]
    return tuple(Claim(index=i, text=t) for i, t in enumerate(kept))
