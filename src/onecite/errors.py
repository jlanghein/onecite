"""The errors a caller has to handle.

Two, and deliberately few. Everything else this library encounters is a
*result*, not an error: a claim nothing supports is an ordinary outcome that
callers must handle, and raising on it would push them toward catching and
ignoring it.
"""


class OneciteError(Exception):
    """Base for everything this library raises."""


class NoSourcesError(OneciteError):
    """Raised when attribution is attempted with no sources at all.

    Distinct from finding no support: with no sources, every claim is trivially
    unsupported and the resulting report says nothing. That is a caller bug —
    retrieval returned nothing and the answer was generated anyway.
    """


class ScorerError(OneciteError):
    """Raised when the supplied scorer fails or returns an impossible score.

    A scorer that returns 1.7, or raises, is broken in a way that makes every
    downstream verdict meaningless. Failing loudly beats attributing an answer
    against numbers nobody can trust.
    """
