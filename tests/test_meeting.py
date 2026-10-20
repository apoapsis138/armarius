"""Holding a Tribunal: the roll call that opens a meeting, its order of
business by day, each step opening the next and saying what it works
out, leaving and resuming at the step in hand, and closing it into the
Diary."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import acta, meeting, storage
from ars_magica_manager import print_layout as pl
from ars_magica_manager.commands import ChooseFile, Confirm, Form, Refuse, Then
from ars_magica_manager.models import CASE_DECIDED, Saga
from ars_magica_manager.rules import debate


def _rhine(saga: Saga):
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    return tribunal


def _values(form: Form, **changes):
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    return values


def _save(form, **changes):
    assert isinstance(form, Form)
    values = _values(form, **changes)
    assert form.validate is None or form.validate(values) is None
    return form.apply(values)


def _opening(saga: Saga, tribunal) -> Form:
    """Call the roll, which opens the meeting; the Opening's form, which
    follows it."""
    following = _save(meeting.hold(saga, tribunal))
    assert isinstance(following, Then) and isinstance(following.step, Form)
    return following.step


def test_before_it_opens_the_hall_shows_the_order_it_would_hold():
    saga = everything_saga()
    rhine = _rhine(saga)
    grid = meeting.business_grid(saga, rhine)
    titles = [row[0] for row in grid.rows]
    assert titles[:2] == ["The roll call and proxies", "Opening and the oaths"]
    assert "Fengheld v. Keep" in titles and "Motion: Gild dues" in titles
    assert titles[-3:] == ["Rulings and fines", "Treasury and vis", "Closing"]
    assert grid.rows[0][1] == "The First Day"
    assert rhine.meeting is None
    assert meeting.title(saga, rhine) == "The Next Meeting: Summer 1228"


def test_hold_calls_the_roll_and_each_step_opens_the_next():
    saga = everything_saga()
    rhine = _rhine(saga)
    roll = meeting.hold(saga, rhine)
    assert isinstance(roll, Form) and roll.save_label == "Call the roll"
    head = [f.value for f in roll.fields() if f.kind == "info"]
    assert str(head[0]).startswith("Step 1 of 9. Saving holds it and opens")
    assert any("Worked out for you" in str(v) for v in head)
    assert any("What you enter changes" in str(v) for v in head)
    opening = _opening(saga, rhine)
    assert rhine.meeting is not None
    assert opening.save_label == "Open"
    assert opening.title == "Step 2 of 9: The First Day, Opening and the oaths"
    labels = [f.label for f in opening.fields()]
    assert "Days" in labels and "Fengheld v. Keep" in labels
    case = rhine.cases[0]
    following = _save(opening, days=2, **{f"day_{case.id}": 1})
    assert isinstance(following, Then)
    assert following.step.title.endswith("Fengheld v. Keep")
    assert rhine.meeting["days"] == 2 and meeting.days(rhine.meeting) == 2
    # Saved with the saga, the meeting is still there when it is loaded.
    storage.save_saga(saga)
    again = storage.load_saga(saga.id).tribunal("rhine")
    assert again is not None and again.meeting == rhine.meeting
    # Holding it again resumes at the step in hand: the first hearing.
    step = meeting.hold(saga, rhine)
    assert isinstance(step, Form) and step.title.endswith("Fengheld v. Keep")
    assert meeting.business_grid(saga, rhine).rows[2][2] == "▶ in hand"
    assert meeting.now_text(rhine, rhine.meeting) == (
        "The First Day › Fengheld v. Keep"
    )
    facts = {f.label: f.value for f in meeting.facts(saga, rhine)}
    assert facts["Now"] == "Step 3 of 9: The First Day › Fengheld v. Keep"
    assert facts["Then"] == "The vote: Fengheld v. Keep"


def test_holding_an_earlier_step_again_goes_on_to_the_step_in_hand():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(_opening(saga, rhine))
    roll = meeting.step_form(saga, rhine, meeting.steps(rhine, rhine.meeting)[0])
    following = _save(roll)
    assert isinstance(following, Then)
    assert following.step.title.endswith("Fengheld v. Keep")


def test_a_day_out_of_range_is_refused():
    saga = everything_saga()
    rhine = _rhine(saga)
    opening = _opening(saga, rhine)
    case = rhine.cases[0]
    values = _values(opening, days=2, **{f"day_{case.id}": 3})
    assert "day from 1 to 2" in (opening.validate(values) or "")
    assert "at least a day" in (opening.validate(_values(opening, days=0)) or "")


def test_the_roll_call_ticks_who_is_present_and_sets_the_votes():
    saga = everything_saga()
    rhine = _rhine(saga)
    roll = meeting.hold(saga, rhine)
    keys = {f.key for f in roll.fields()}
    assert {"all_cov1", "present_cov1_mag1", "unnamed_cov_sketch"} <= keys
    assert {"proxies_cov_sketch", "ruling_cov_sketch"} <= keys
    _save(roll)
    # Everyone present; Severinus is Praeco, so doesn't vote: Leandro's
    # one, Fengheld's two unnamed magi and its proxy.
    assert meeting.hall(saga, rhine, rhine.meeting) == (4, 1)
    roll = meeting.step_form(saga, rhine, meeting.steps(rhine, rhine.meeting)[0])
    _save(
        roll,
        all_cov1=False,
        present_cov1_mag1=False,
        all_cov_sketch=False,
        unnamed_cov_sketch=1,
        proxies_cov_sketch=2,
        ruling_cov_sketch=meeting.SET_ASIDE,
    )
    assert meeting.hall(saga, rhine, rhine.meeting) == (1, 0)
    keep = saga.covenant("cov1")
    assert keep is not None
    assert meeting.named_present(saga, rhine.meeting, keep) == []
    assert rhine.proxies["cov_sketch"] == 2
    rows = {r[0]: r for r in meeting.attendance_grid(saga, rhine).rows}
    assert rows["Fengheld"][2] == "1" and rows["Fengheld"][3] == "2 (set aside)"
    assert rows["Keep"][2] == "1"
    assert "Keep: 1 absent (Leandro)." in rhine.diary[-1].details
    assert meeting.quorum(saga, rhine, rhine.meeting) == (
        "2 magi from 1 covenant, and no Quaesitor: not quorate (it needs 12 "
        "magi and 4 covenants and a Quaesitor)"
    )


def test_an_older_save_with_only_a_count_absent_still_reads():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(_opening(saga, rhine))
    assert rhine.meeting is not None
    rhine.meeting["attendance"] = {"cov_sketch": {"absent": 1, "proxies": 0}}
    fengheld = saga.covenant("cov_sketch")
    assert fengheld is not None
    assert meeting.in_person(saga, rhine.meeting, fengheld) == 2
    assert meeting.absent(saga, rhine.meeting, fengheld) == 1


def test_a_hearing_chooses_its_speakers_from_the_magi_present():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(_opening(saga, rhine))
    steps = meeting.steps(rhine, rhine.meeting)
    index = next(i for i, s in enumerate(steps) if s.title == "Fengheld v. Keep")
    ops = meeting.business_ops(saga, rhine)
    assert ops.edit is not None
    hearing = ops.edit(index)
    assert isinstance(hearing, Form)
    fields = {f.key: f for f in hearing.fields()}
    # Severinus is the case's prosecutor; Keep is a covenant, so its magus
    # present defends it.
    assert (fields["prosecutor"].value, fields["defender"].value) == (
        "mag_sketch",
        "mag1",
    )
    assert ("Leandro (Keep)", "mag1") in fields["defender"].options
    assert (meeting._SPEAKERS[meeting.ADVOCATE], meeting.ADVOCATE) in fields[
        "defender"
    ].options
    assert (
        meeting._SPEAKERS[meeting.QUAESITOR],
        meeting.QUAESITOR,
    ) in fields["prosecutor"].options
    _save(hearing, defender=meeting.ADVOCATE, skill_defender=debate.FORMIDABLE)
    case = rhine.cases[0]
    assert case.defender == "A Guernicus advocate"
    assert rhine.meeting["debates"][case.id]["skills"][1] == debate.FORMIDABLE
    motion = next(s for s in steps if s.title == "Motion: Gild dues")
    found = {f.key: f for f in motion.fields(saga, rhine, rhine.meeting)}
    assert found["defender"].label == "Speaks against it"
    assert found["defender"].value == meeting.THE_TRIBUNAL
    assert "settled" not in found and "proposal" in found


def test_an_absent_accused_is_defended_by_a_guernicus_advocate():
    saga = everything_saga()
    rhine = _rhine(saga)
    roll = meeting.hold(saga, rhine)
    _save(roll, all_cov1=False, present_cov1_mag1=False)
    case = rhine.cases[0]
    case.defender = ""
    assert rhine.meeting is not None
    assert (
        meeting.default_speaker(saga, rhine, rhine.meeting, case, meeting.AGAINST)
        == meeting.ADVOCATE
    )


def test_a_speaker_with_no_scores_debates_at_a_skill():
    able = debate.debater("A Guernicus advocate", None, debate.ABLE)
    assert (able.communication, able.attacks["Intrigue"]) == (1, 4)
    middling = debate.debater("Nobody", None)
    assert middling.attacks["Folk Ken"] == debate.AVERAGE_ABILITY
    saga = everything_saga()
    leandro = saga.character("mag1")
    assert leandro is not None and not debate.has_scores(leandro)
    assert not debate.debater("Leandro", leandro, debate.FORMIDABLE).found
    leandro.characteristics.communication = 2
    assert debate.debater("Leandro", leandro, debate.FORMIDABLE).communication == 2


def test_a_case_settled_at_the_private_hearing_has_no_debate_or_vote():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(_opening(saga, rhine))
    case = rhine.cases[0]
    hearing = meeting.step_form(saga, rhine, _step(rhine, f"case:{case.id}"))
    following = _save(hearing, settled=True)
    assert meeting.settled(rhine.meeting, case)
    keys = [s.key for s in meeting.steps(rhine, rhine.meeting)]
    assert f"vote:{case.id}" not in keys
    # The next step is the motion's hearing, not this case's vote.
    assert isinstance(following, Then)
    assert following.step.title.endswith("Motion: Gild dues")
    assert "settled before the Presiding Quaesitor" in rhine.diary[-1].details
    rulings = meeting.step_form(saga, rhine, _step(rhine, "rulings"))
    assert _values(rulings)[f"outcome_{case.id}"] == "Settled at the private hearing."


def test_closing_writes_the_diary_and_sets_the_next_meeting():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(meeting.hold(saga, rhine))
    found = meeting.steps(rhine, rhine.meeting)
    rulings = next(s for s in found if s.key == "rulings")
    _save(
        meeting.step_form(saga, rhine, rulings),
        **{f"outcome_{rhine.cases[0].id}": "Keep pays 3 pawns of Aquam"},
    )
    diary = len(rhine.diary)
    closing = meeting.step_form(saga, rhine, found[-1])
    assert closing.save_label == "Close"
    _save(closing)
    assert rhine.meeting is None
    assert rhine.cases[0].status == CASE_DECIDED
    assert rhine.cases[1].status == "open"
    # The Closing's own minutes, then the Acta.
    assert len(rhine.diary) == diary + 2
    assert rhine.diary[-1].title == "Acta of the Rhine Tribunal, Summer 1228"
    assert rhine.next_year == 1235


def test_abandon_asks_and_needs_a_meeting():
    saga = everything_saga()
    rhine = _rhine(saga)
    ops = meeting.business_ops(saga, rhine)
    assert ops.remove is not None
    assert isinstance(ops.remove(0), Refuse)
    _save(meeting.hold(saga, rhine))
    confirm = ops.remove(0)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert rhine.meeting is None


def test_elections_give_each_office_its_holder_and_term():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    _save(meeting.hold(saga, thebes))
    elections = meeting.Elections("elections", "Elections", 1)
    form = meeting.step_form(saga, thebes, elections)
    _save(form, holder_1="mag1", term_1=1232)
    office = thebes.package_data["theban"]["archai"][1]
    assert (office["holder_id"], office["term_ends"]) == ("mag1", 1232)


# -- the debate and the vote --


def _open(saga: Saga):
    rhine = _rhine(saga)
    _save(_opening(saga, rhine))
    return rhine


def _step(rhine, key: str):
    return next(s for s in meeting.steps(rhine, rhine.meeting) if s.key == key)


def test_each_case_has_its_debate_then_its_vote():
    saga = everything_saga()
    rhine = _open(saga)
    titles = [s.title for s in meeting.steps(rhine, rhine.meeting)]
    at = titles.index("Fengheld v. Keep")
    assert titles[at + 1] == "The vote: Fengheld v. Keep"


def test_testimony_bonus_follows_who_gives_it():
    assert debate.testimony_bonus("Fengheld's register") == 1
    assert debate.testimony_bonus("The apprentice saw it") == 2
    assert debate.testimony_bonus("A magus of Durenmar") == 3
    assert debate.testimony_bonus("A peer, examined by a Quaesitor") == 6


def test_a_debate_runs_until_a_side_is_knocked_out_or_the_rounds_end():
    strong = debate.Debater(
        "Severinus",
        communication=3,
        presence=3,
        attacks={"Intrigue": 6},
        defences={"Guile": 6},
    )
    weak = debate.Debater("Novice")
    held = debate.run((strong, weak), ([3], []), 10, random.Random(4))
    assert held.victor == 0
    assert held.lost[1] >= debate.KNOCKED_OUT or held.rounds == 10
    assert held.lines and held.lines[0].startswith("Round 1:")
    assert held.strength == held.lost[1] - held.lost[0]
    # However hard the last blow, a side loses no more than five levels.
    for seed in range(30):
        held = debate.run((strong, weak), ([3], []), 10, random.Random(seed))
        assert max(held.lost) <= debate.KNOCKED_OUT


def test_argument_strength_sways_neutral_then_hostile_votes():
    # Societates' example: Upper Hand wins 20% of 25 neutral votes.
    assert debate.swayed(3, 25, 20) == (5, 0)
    # A Triumphant Victory also wins 10% of the other side.
    assert debate.swayed(5, 25, 20) == (10, 2)
    assert debate.sway(9)[0] == "Landslide Victory"
    assert debate.swayed(1, 25, 20) == (0, 0)


def test_leanings_default_from_the_parties_and_attitude():
    saga = everything_saga()
    rhine = _open(saga)
    case = rhine.cases[0]
    lean = meeting.leanings(saga, rhine, rhine.meeting, case)
    # Fengheld brings it, Keep defends it.
    assert lean == {"cov1": meeting.AGAINST, "cov_sketch": meeting.FOR}


def test_entered_levels_decide_the_debate_and_the_vote_is_called_in_order():
    saga = everything_saga()
    rhine = _open(saga)
    case = rhine.cases[0]
    hearing = meeting.step_form(saga, rhine, _step(rhine, f"case:{case.id}"))
    _save(hearing, lost_for=0, lost_against=3)
    assert meeting.strength(rhine.meeting, case) == (meeting.FOR, 3)
    assert "Upper Hand" in meeting.debate_text(rhine.meeting, case)
    vote = meeting.step_form(saga, rhine, _step(rhine, f"vote:{case.id}"))
    assert vote.live is not None
    # Severinus is Praeco, so Fengheld has three votes: its two unnamed
    # magi and its proxy.
    assert vote.live(_values(vote)).startswith("For 3, against 1")
    hints = {f.key: f.hint for f in vote.fields()}
    assert hints["lean_cov1"] == "Of itself: the case is against it."
    called = list(meeting.call_the_vote(saga, rhine, rhine.meeting, case))
    assert [c.covenant.name for c in called] == ["Keep", "Fengheld"]
    assert called[0].tally == (0, 1, 0) and called[-1].tally == (3, 1, 0)
    # Keep undecided: an Upper Hand wins 20% of its one vote, rounded.
    lean = {"cov1": meeting.UNDECIDED, "cov_sketch": meeting.FOR}
    assert meeting.tally(saga, rhine, rhine.meeting, case, lean) == (3, 0, 1)
    _save(vote)
    assert rhine.meeting["votes"][case.id]["for"] == 3
    rulings = meeting.step_form(saga, rhine, _step(rhine, "rulings"))
    assert _values(rulings)[f"outcome_{case.id}"] == "Carried, 3 to 1"


def test_a_tie_is_broken_by_the_praeco():
    assert meeting.passes((2, 2, 0)) is None
    assert meeting.passes((2, 2, 0), meeting.FOR) is True
    assert meeting.tally_text((2, 2, 1), meeting.AGAINST) == (
        "For 2, against 2, 1 abstaining: a tie: the Praeco casts against it, "
        "and it fails"
    )
    saga = everything_saga()
    rhine = _open(saga)
    case = rhine.cases[0]
    vote = meeting.step_form(saga, rhine, _step(rhine, f"vote:{case.id}"))
    tie = next(f for f in vote.fields() if f.key == "tie")
    assert tie.show_if is not None
    # Keep against (1), Fengheld undecided: no tie; Fengheld against too:
    # still none; both undecided: 0 to 0, a tie.
    both = {"lean_cov1": meeting.UNDECIDED, "lean_cov_sketch": meeting.UNDECIDED}
    assert tie.show_if(both)
    assert not tie.show_if(_values(vote))
    _save(vote, **both, tie=meeting.FOR)
    assert meeting.vote_outcome(rhine.meeting, case) == (
        "Carried, 0 to 0 on the Praeco's casting vote"
    )


def test_a_rolled_debate_uses_the_dice(monkeypatch):
    saga = everything_saga()
    rhine = _open(saga)
    case = rhine.cases[0]
    monkeypatch.setattr(meeting, "rng", lambda: random.Random(7))
    _save(meeting.step_form(saga, rhine, _step(rhine, f"case:{case.id}")))
    held = rhine.meeting["debates"][case.id]
    assert not held["entered"] and held["lines"]
    form = meeting.step_form(saga, rhine, _step(rhine, f"case:{case.id}"))
    assert "both sides" in (form.validate(_values(form, lost_for=1)) or "")


def test_an_alteration_costs_a_motion_argument_strength():
    saga = everything_saga()
    rhine = _open(saga)
    motion = rhine.cases[1]
    form = meeting.step_form(saga, rhine, _step(rhine, f"case:{motion.id}"))
    _save(
        form,
        prosecutor="mag1",
        defender="mag_sketch",
        proposal="Alteration",
        lost_for=0,
        lost_against=4,
    )
    assert meeting.strength(rhine.meeting, motion) == (meeting.FOR, 1)


def _rulings(saga, rhine, **values):
    _save(meeting.hold(saga, rhine))
    found = meeting.steps(rhine, rhine.meeting)
    rulings = next(s for s in found if s.key == "rulings")
    _save(meeting.step_form(saga, rhine, rulings), **values)
    return found


def test_each_step_held_writes_its_minutes_once():
    saga = everything_saga()
    rhine = _rhine(saga)
    before = len(rhine.diary)
    opening = _opening(saga, rhine)
    assert rhine.diary[-1].title == "¶ The First Day: The roll call and proxies"
    _save(opening)
    entry = rhine.diary[-1]
    assert len(rhine.diary) == before + 2
    assert entry.title == "¶ The First Day: Opening and the oaths"
    assert "the oaths were sworn" in entry.details
    assert entry.margin == "3 days"
    # Held again, its entry is rewritten, not added to.
    opening = meeting.step_form(saga, rhine, meeting.steps(rhine, rhine.meeting)[1])
    _save(opening, days=2)
    assert len(rhine.diary) == before + 2
    assert rhine.diary[-1].margin == "2 days"


def test_closing_writes_the_fine_the_code_and_the_attitude():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    fengheld = saga.covenant("cov_sketch")
    assert fengheld is not None
    reasons = len(fengheld.attitudes[0].reasons)
    treasury, code = len(rhine.treasury), len(rhine.rulings)
    found = _rulings(
        saga,
        rhine,
        **{
            f"outcome_{case.id}": "Keep pays 3 pawns of Aquam",
            f"fine_{case.id}": 3.0,
            f"art_{case.id}": "Aquam",
            f"code_{case.id}": True,
            f"attitude_{case.id}": "-2",
        },
    )
    _save(meeting.step_form(saga, rhine, found[-1]))
    fine = rhine.treasury[treasury]
    assert (fine.kind, fine.amount, fine.art, fine.who) == (
        "fine",
        3.0,
        "Aquam",
        "Keep",
    )
    assert len(rhine.rulings) == code + 1
    assert rhine.rulings[-1].says == "Keep pays 3 pawns of Aquam"
    moved = fengheld.attitudes[0].reasons
    assert len(moved) == reasons + 1 and moved[-1].change == -2
    assert "Fengheld v. Keep" in moved[-1].what


def test_the_acta_is_built_from_the_meeting():
    saga = everything_saga()
    rhine = _rhine(saga)
    case = rhine.cases[0]
    _rulings(
        saga,
        rhine,
        **{f"outcome_{case.id}": "Keep pays", f"fine_{case.id}": 10.0},
    )
    text = meeting.acta_text(saga, rhine, rhine.meeting)
    assert text.startswith("The Rhine Tribunal, gathered")
    assert "In the matter of Fengheld v. Keep, the Tribunal ruled: Keep pays; " in text
    assert "Keep pays; Keep is to pay a fine of 10 pounds." in text
    assert "Witnessed by Severinus." in text


def test_a_fine_must_be_more_than_nothing():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(meeting.hold(saga, rhine))
    rulings = next(s for s in meeting.steps(rhine, rhine.meeting) if s.key == "rulings")
    form = meeting.step_form(saga, rhine, rulings)
    assert isinstance(form, Form) and form.validate is not None
    values = _values(form, **{f"fine_{rhine.cases[0].id}": 0.0})
    assert (
        form.validate(values) == "A fine is more than nothing; leave it blank for none."
    )


def test_an_acta_prints_and_the_minutes_do_not(tmp_path):
    saga = everything_saga()
    rhine = _rhine(saga)
    found = _rulings(saga, rhine, **{f"outcome_{rhine.cases[0].id}": "Keep pays"})
    _save(meeting.step_form(saga, rhine, found[-1]))
    written = rhine.diary[-1]
    printed = []
    step = acta.print_entry(
        rhine, "Rhine Tribunal", written, lambda doc, path: printed.append(doc) or 2
    )
    assert isinstance(step, ChooseFile) and step.save
    assert step.start.name == "Acta of the Rhine Tribunal, Summer 1228.pdf"
    assert step.apply(tmp_path / "acta.pdf") == [
        f"2 pages saved to {tmp_path / 'acta.pdf'}."
    ]
    doc = printed[0]
    assert doc.blocks[0] == pl.Title("Acta", "Rhine Tribunal, Summer 1228")
    assert any(
        isinstance(b, pl.Paragraph) and b.text.startswith("In the matter of")
        for b in doc.blocks
    )
    minutes = rhine.diary[-2]
    assert isinstance(
        acta.print_entry(rhine, "Rhine Tribunal", minutes, lambda d, p: 1), Refuse
    )
