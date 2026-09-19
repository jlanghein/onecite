# The three failures

A grounded answer is only worth more than an ungrounded one if the citations
are right. Three things go wrong, and conflating them is why most systems fix
none of them.

## Over-citation

A paragraph touches four topics, four retrieved chunks look relevant, and all
four get cited. It reads as diligence. A reader following any one of them may
find it says nothing about the sentence it was attached to.

```python
support, qualified = decide(scores, policy)  # never returns "cite these four"
```

`decide()` returns one source or none. **Over-citation is not a formatting
choice, it is the absence of a decision** — and the fix is to make the decision
rather than to render fewer markers.

This is also why claims are split before attribution. A citation attaches to an
assertion, not a paragraph; attributing whole paragraphs is where over-citation
begins.

## Topically related is not supporting

A chunk about bolt torque scores well against a question about bolt torque
while never stating the figure. This is the failure mode that survives good
retrieval, because retrieval optimises for exactly the similarity that produces
it.

Citing it is worse than citing nothing. A missing citation tells a reader to go
and check; a wrong one tells them it was already checked.

```python
Policy(support_threshold=0.70)
```

The threshold is the line between the two, and it is yours — a cross-encoder
and a lexical baseline do not produce comparable numbers, so a value tuned for
one is meaningless for the other.

## A claim nothing supports

The failure that matters when somebody acts on the answer.

```python
if result.unsupported:
    ...  # these sentences came from the model's weights, not your corpus
```

`Support.UNSUPPORTED` attaches no citation. The claim still appears in the
result with its text, so a caller can show the answer with a warning, refuse to
show it, or widen retrieval and try again. What it cannot do is quietly acquire
a citation.

## And one that hides between them

```python
Support.CONTESTED
```

Two sources clear the bar and the scorer is not really separating them. Taking
the top one is a coin toss presented as a judgement, so it is named.

A contested claim still gets its best source by default, with the others in
`runners_up` so the result can show its work. `Policy(allow_contested_citation=False)`
suits a caller who would rather display no citation than an arguable one.

!!! note "Why the ordering is stable"
    Ties break on source id, not on whichever the scorer emitted first. Without
    that, two runs over the same answer cite different sources — and a citation
    that moves is one nobody trusts.
