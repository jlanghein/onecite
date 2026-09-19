# Getting Started

## Install

```bash
uv add onecite
```

Python 3.13 or later. No runtime dependencies.

## Bring your own judgement

The one thing `onecite` does not decide is whether a source supports a claim.
That is a modelling question, so it sits behind a Protocol:

```python
from onecite import Claim, Scorer, Source


class CrossEncoderScorer:
    def __init__(self, model):
        self._model = model

    def score(self, claim: Claim, source: Source) -> float:
        return self._model.predict([(source.text, claim.text)])[0]
```

Anything with that method works: a cross-encoder, an NLI model, an LLM asked
to answer yes or no. Scores must fall in `0..1` — `onecite` checks on every
call and raises `ScorerError` rather than producing verdicts from numbers
nobody can trust.

!!! warning "The bundled scorer is a baseline"
    `LexicalScorer` compares content words. It cannot tell *"the torque is
    240 Nm"* from *"the torque is **not** 240 Nm"*, so it should not be behind
    anything a person acts on. It exists so the pipeline runs deterministically
    in tests and so you can see the shape of the output before wiring up a
    model.

## Attribute an answer

```python
from onecite import LexicalScorer, Source, attribute

sources = [
    Source(id="s1", text="Tighten the main bolts to 240 Nm.", locator="V47 manual p.112"),
    Source(id="s2", text="Change gearbox oil every 5,000 hours.", locator="p.88"),
]

result = attribute(answer, sources, LexicalScorer())
```

`Source.locator` is where a reader would go to check — a page, a section, a
URL. It may be empty, and empty is a smell: a citation nobody can follow is
decoration.

## Read the result

```python
for a in result.attributions:
    if a.is_cited:
        print(f"{a.claim.text}  [{a.source.locator}]  {a.score:.2f}")
    else:
        print(f"{a.claim.text}  — unsupported")

print(f"{result.grounded_fraction:.0%} of claims carry a citation")
```

`result.unsupported` is the number that matters. Claims nothing in the sources
backs are claims the model produced from its own weights.

## Tune the policy

```python
from onecite import Policy

Policy(support_threshold=0.70)  # demand stronger support
Policy(contest_margin=0.15)  # be fussier about near-ties
Policy(allow_contested_citation=False)  # show nothing rather than an arguable citation
```

Thresholds are yours because they depend on your scorer. A number tuned for a
cross-encoder is meaningless for a lexical baseline.

## Handle the two errors

```python
from onecite import NoSourcesError, ScorerError

try:
    result = attribute(answer, sources, scorer)
except NoSourcesError:
    ...  # retrieval returned nothing and the answer was generated anyway
except ScorerError:
    ...  # the scorer is broken; stop rather than trust the verdicts
```

Everything else is a *result*. A claim nothing supports is an ordinary outcome
that callers must handle — raising on it would push them toward catching and
ignoring it.
