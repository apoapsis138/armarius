"""commands.steps / drive: how a run of steps ends, with no screen. One
scripted `ask` answers each step; the Outcome says what a front-end does."""

from pathlib import Path

from ars_magica_manager import commands as c
from ars_magica_manager.references import Ref


def _form(apply) -> c.Form:
    return c.Form("T", list, apply)


def _drive(first, *answers):
    asked = []
    queue = list(answers)

    def ask(question):
        asked.append(question)
        return queue.pop(0) if queue else c.CANCELLED

    return c.drive(first, ask), asked


def test_a_form_then_its_next_step_finish_with_what_the_last_returned():
    first = _form(lambda v: c.Confirm("Sure?", lambda: ["done"]))
    outcome, asked = _drive(first, {"a": 1}, True)
    assert outcome == c.Finished(["done"])
    assert [type(q) for q in asked] == [c.Form, c.Confirm]


def test_an_act_runs_at_once_and_asks_nothing():
    ran = []
    outcome, asked = _drive(c.Act(lambda: ran.append(1) or None))
    assert outcome == c.Finished(None) and ran == [1] and asked == []


def test_cancelling_any_step_ends_the_run_and_nothing_more_is_applied():
    applied = []
    first = _form(lambda v: c.Confirm("?", lambda: applied.append("yes")))
    outcome, asked = _drive(first, {})  # the confirm is not answered
    assert outcome == c.CANCELLED and applied == [] and len(asked) == 2
    assert not c.saves(outcome)


def test_an_empty_list_ends_the_run_with_the_reason_and_asks_nothing():
    choose = c.Choose("Pick", list, lambda v: None, empty="Nothing here")
    outcome, asked = _drive(choose)
    assert outcome == c.Empty("Pick", "Nothing here") and asked == []
    assert not c.saves(outcome)


def test_a_chooser_applies_the_chosen_value_and_a_file_its_path():
    got = []
    choose = c.Choose(
        "Pick",
        lambda: [c.Choice("A", "a")],
        lambda v: c.ChooseFile("F", ".csv", Path("."), lambda p: got.append((v, p))),
    )
    outcome, _ = _drive(choose, "a", Path("x.csv"))
    assert got == [("a", Path("x.csv"))] and outcome == c.Finished(None)


def test_refuse_and_go_change_nothing_so_nothing_is_saved():
    refuse = c.Refuse("No", "because")
    go = c.Go(Ref("character", "c1", "C"))
    assert _drive(refuse)[0] is refuse and not c.saves(refuse)
    assert _drive(go)[0] is go and not c.saves(go)


def test_a_step_that_ends_in_refuse_after_a_form_is_still_not_saved():
    first = _form(lambda v: c.Refuse("No", "why"))
    outcome, _ = _drive(first, {})
    assert outcome == c.Refuse("No", "why") and not c.saves(outcome)


def test_then_saves_and_hands_back_the_next_step_to_run():
    nxt = c.Act(lambda: None)
    first = _form(lambda v: c.Then(nxt))
    outcome, _ = _drive(first, {})
    assert outcome == c.Then(nxt) and c.saves(outcome)


def test_finished_with_picked_or_notes_saves():
    assert c.saves(c.Finished(c.Picked(3)))
    assert c.saves(c.Finished(["a note"]))
    assert c.saves(c.Finished(None))
