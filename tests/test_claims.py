from onecite.claims import split, strip_existing_markers


def texts(answer: str) -> list[str]:
    return [c.text for c in split(answer)]


def test_sentences_become_separate_claims():
    assert texts("The torque is 240 Nm. The interval is 5,000 hours.") == [
        "The torque is 240 Nm.",
        "The interval is 5,000 hours.",
    ]


def test_an_abbreviation_does_not_end_a_claim():
    assert texts("The corpus holds approx. 4,900 manuals across nine makers.") == [
        "The corpus holds approx. 4,900 manuals across nine makers."
    ]


def test_list_items_are_claims_in_their_own_right():
    answer = "Check these:\n- Bolt torque is 240 Nm\n- Oil change every 5,000 hours"
    assert texts(answer) == ["Bolt torque is 240 Nm", "Oil change every 5,000 hours"]


def test_numbered_list_markers_are_removed():
    assert texts("1. Bolt torque is 240 Nm\n2. Oil change every 5,000 hours") == [
        "Bolt torque is 240 Nm",
        "Oil change every 5,000 hours",
    ]


def test_fragments_too_short_to_check_are_dropped():
    assert texts("Yes. The torque is 240 Nm.") == ["The torque is 240 Nm."]


def test_markers_the_model_already_wrote_are_stripped():
    assert strip_existing_markers("The torque is 240 Nm. [3]") == "The torque is 240 Nm."
    assert strip_existing_markers("The torque is 240 Nm. [1, 2, 3]") == "The torque is 240 Nm."


def test_stripping_leaves_an_uncited_claim_alone():
    assert strip_existing_markers("The torque is 240 Nm.") == "The torque is 240 Nm."


def test_claims_are_indexed_in_order():
    claims = split("The torque is 240 Nm. The interval is 5,000 hours.")
    assert [c.index for c in claims] == [0, 1]


def test_an_empty_answer_yields_no_claims():
    assert split("") == ()
    assert split("   \n\n  ") == ()


def test_a_line_introducing_a_list_is_not_a_claim():
    from onecite.claims import is_lead_in

    assert is_lead_in("Check these:")
    assert is_lead_in("The required steps are:")
    assert not is_lead_in("The torque is 240 Nm.")
