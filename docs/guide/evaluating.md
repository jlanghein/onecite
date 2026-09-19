# Measuring citations

Retrieval benchmarks answer whether the right chunk came back. That is the
easier question: a system can retrieve perfectly and still cite the wrong
passage for every sentence.

```python
from onecite import Example, Source, evaluate

examples = [
    Example(
        answer="The torque is 240 Nm. The warranty runs for seven years.",
        sources=(torque_chunk, oil_chunk),
        expected={0: "s1", 1: None},
    )
]

report = evaluate(examples, scorer)
```

## Three numbers, because three things go wrong

| | Question | What it catches |
|---|---|---|
| `precision` | Of the claims we cited, how many cited the right source? | Confident citations a reader cannot verify |
| `recall` | Of the claims with a correct source available, how many did we find? | Grounded answers presented as ungrounded |
| `abstention_accuracy` | Of the claims with no correct source, how many did we correctly leave uncited? | A citation invented for a claim nothing supports |

## Abstention accuracy is the one nobody measures

It needs the dataset to label the claims where **no** correct source exists —
`expected={1: None}` above. That labelling is the work most datasets skip,
because it means reading answers for sentences the corpus does not back rather
than harvesting positive pairs.

It is also the only number that moves when a system starts inventing citations.
Precision and recall are both computed over claims that *had* an answer;
abstention accuracy is computed over the ones that did not.

## Unlabelled claims are reported, not ignored

```python
report.unlabelled  # claims the split produced that the labels do not mention
```

A non-zero value usually means segmentation changed and the labels are now
attached to the wrong indices. Silently skipping those would leave every other
number quietly measuring the wrong thing, so they are counted and surfaced.

## Reading a report

```python
print(
    f"precision {report.precision:.2f}  "
    f"recall {report.recall:.2f}  "
    f"abstention {report.abstention_accuracy:.2f}"
)
```

High precision with low abstention accuracy is the characteristic shape of a
system that cites well when it can and invents a citation when it cannot. It is
the failure a single F1 number hides, which is why `f1` is offered but the three
are reported separately.
