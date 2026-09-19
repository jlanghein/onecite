# onecite

Cite one source per fact, and refuse to cite a source that does not support it.

```python
from onecite import LexicalScorer, Source, attribute

sources = [
    Source(id="s1", text="Tighten the main bolts to 240 Nm.", locator="V47 manual p.112"),
    Source(id="s2", text="Change gearbox oil every 5,000 hours.", locator="p.88"),
]

result = attribute(
    "The torque is 240 Nm. The warranty runs for seven years.",
    sources,
    LexicalScorer(),
)

for a in result.attributions:
    mark = a.source.locator if a.source else "— nothing supports this"
    print(f"{a.claim.text}  [{mark}]")

print(f"{len(result.unsupported)} unsupported claims")
```

## Why this exists

A grounded answer is only worth more than an ungrounded one if the citations
are right. Three things go wrong, and they are different problems.

### Over-citation

A paragraph touches four topics, four retrieved chunks look relevant, and all
four get cited. A reader following any one of them may find it says nothing
about the sentence it was attached to.

`decide()` never returns "cite these four". It returns one source or none —
because over-citation is not a formatting choice, it is the absence of a
decision.

### Topically related is not supporting

A chunk about bolt torque scores well against a question about bolt torque
while never stating the figure. Citing it is worse than citing nothing: it
tells the reader the claim was checked.

The support threshold is the line between the two, and it lives on a `Policy`
you supply, because a cross-encoder and a lexical baseline do not produce
comparable numbers.

### A claim nothing supports

The failure that matters when somebody acts on the answer. `Support.UNSUPPORTED`
attaches no citation and appears in `result.unsupported`, so a caller can
refuse to show the answer, flag it, or widen retrieval — deliberately.

### And one that hides between them

`Support.CONTESTED`: two sources clear the bar and the scorer is not really
separating them. Picking the top one is a coin toss presented as a judgement,
so it is named and reported rather than resolved silently.

## Measuring it

```python
from onecite import Example, evaluate

report = evaluate(examples, scorer)
print(report.precision, report.recall, report.abstention_accuracy)
```

Retrieval benchmarks answer whether the right chunk came back. That is the
easier question — a system can retrieve perfectly and cite the wrong passage
every time.

| Number | What it catches |
|---|---|
| **Precision** | Confident citations a reader cannot verify |
| **Recall** | Grounded answers presented as ungrounded |
| **Abstention accuracy** | A citation invented for a claim nothing supports |

The third is the one nobody measures. It requires labelling the claims where
*no* correct source exists, which is the work most datasets skip.

## Design

```
errors ──► models ──► claims ──┐
                      policy ──┴──► scoring ──► attribute ──► evaluate
```

`claims`, `policy` and `scoring` are pure. The judgement — does this source
support this claim — is yours, behind a `Scorer` Protocol: a cross-encoder, an
NLI model, an LLM asked to answer yes or no.

**No runtime dependencies.** Deciding which source supports which claim does
not need a model, a vector store or a network. `LexicalScorer` ships so the
pipeline runs and is testable before anyone pays for inference — it is a
baseline and says so, since it cannot tell *"the torque is 240 Nm"* from
*"the torque is not 240 Nm"*.

## Install

```bash
uv add onecite
```

## Development

```bash
uv sync --extra dev
uv run --extra dev ruff format .
uv run --extra dev ruff check --fix .
uv run --extra dev ty check src
uv run --extra dev pytest
```

Run the tools through `uv run`, not `uvx` — `uvx` pins nothing and resolves the
newest release on every invocation, so the checks can change behaviour with
nothing in the repository changing.

See [`AGENTS.md`](AGENTS.md) for the conventions CI enforces.

## Licence

MIT
