"""Holding a Tribunal: opening a meeting, its order of business by day,
attendance and proxies, leaving and resuming at the step in hand, and
closing it into the Diary."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import acta, meeting, storage
from ars_magica_manager import print_layout as pl
from ars_magica_manager.commands import ChooseFile, Confirm, Form, Refuse
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
    form.apply(values)


def test_before_it_opens_the_hall_shows_the_order_it_would_hold():
    saga = everything_saga()
    rhine = _rhine(saga)
    grid = meeting.business_grid(saga, rhine)
    titles = [row[0] for row in grid.rows]
    assert titles[:2] == ["Opening and the oaths", "Attendance and proxies"]
    assert "Fengheld v. Keep" in titles and "Motion: Gild dues" in titles
    assert titles[-3:] == ["Rulings and fines", "Treasury and vis", "Closing"]
    assert grid.rows[0][1] == "The First Day"
    assert rhine.meeting is None
    assert meeting.title(saga, rhine) == "The Next Meeting: Summer 1228"


def test_hold_opens_the_meeting_and_resumes_at_the_step_in_hand():
    saga = everything_saga()
    rhine = _rhine(saga)
    opening = meeting.hold(saga, rhine)
    assert isinstance(opening, Form) and opening.save_label == "Open"
    labels = [f.label for f in opening.fields()]
    assert "Days" in labels and "Fengheld v. Keep" in labels
    case = rhine.cases[0]
    _save(opening, days=2, **{f"day_{case.id}": 1})
    assert rhine.meeting is not None and rhine.meeting["days"] == 2
    assert meeting.days(rhine.meeting) == 2
    # Saved with the saga, the meeting is still there when it is loaded.
    storage.save_saga(saga)
    again = storage.load_saga(saga.id).tribunal("rhine")
    assert again is not None and again.meeting == rhine.meeting
    # Holding it again resumes at the step in hand: Attendance.
    step = meeting.hold(saga, rhine)
    assert isinstance(step, Form) and step.title.endswith("Attendance and proxies")
    assert meeting.business_grid(saga, rhine).rows[1][2] == "▶ in hand"
    assert meeting.now_text(rhine, rhine.meeting) == (
        "The First Day › Attendance and proxies"
    )


def test_a_day_out_of_range_is_refused():
    saga = everything_saga()
    rhine = _rhine(saga)
    opening = meeting.hold(saga, rhine)
    case = rhine.cases[0]
    values = _values(opening, days=2, **{f"day_{case.id}": 3})
    assert "day from 1 to 2" in (opening.validate(values) or "")
    assert "at least a day" in (opening.validate(_values(opening, days=0)) or "")


def test_attendance_and_proxies_set_the_votes_in_the_hall():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(meeting.hold(saga, rhine))
    votes, proxies = meeting.hall(saga, rhine, rhine.meeting)
    attendance = meeting.hold(saga, rhine)
    keys = {f.key for f in attendance.fields()}
    assert {"absent_cov1", "proxies_cov_sketch", "ruling_cov_sketch"} <= keys
    _save(
        attendance,
        absent_cov1=1,
        proxies_cov_sketch=2,
        ruling_cov_sketch=meeting.SET_ASIDE,
    )
    after, by_proxy = meeting.hall(saga, rhine, rhine.meeting)
    assert by_proxy == 0 and after == votes - proxies - 1
    assert rhine.proxies["cov_sketch"] == 2
    row = next(
        r for r in meeting.attendance_grid(saga, rhine).rows if r[0] == "Fengheld"
    )
    assert row[3] == "2 (set aside)"


def test_a_hearing_takes_its_sides_from_the_case():
    saga = everything_saga()
    rhine = _rhine(saga)
    _save(meeting.hold(saga, rhine))
    steps = meeting.steps(rhine, rhine.meeting)
    index = next(i for i, s in enumerate(steps) if s.title == "Fengheld v. Keep")
    ops = meeting.business_ops(saga, rhine)
    assert ops.edit is not None
    hearing = ops.edit(index)
    assert isinstance(hearing, Form)
    values = _values(hearing)
    assert (values["prosecutor"], values["defender"]) == ("Severinus", "Keep")
    _save(hearing, defender="Leandro")
    assert rhine.cases[0].defender == "Leandro"
    motion = next(s for s in steps if s.title == "Motion: Gild dues")
    labels = [f.label for f in motion.fields(saga, rhine, rhine.meeting)]
    assert "Speaks against it" in labels and "Proposal" in labels


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


def test_the_theban_meeting_holds_elections():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    _save(meeting.hold(saga, thebes))
    found = meeting.steps(thebes, thebes.meeting)
    elections = next(s for s in found if s.key == "elections")
    form = meeting.step_form(saga, thebes, elections)
    _save(form, holder_1="mag1", term_1=1232)
    office = thebes.package_data["theban"]["archai"][1]
    assert (office["holder_id"], office["term_ends"]) == ("mag1", 1232)


# -- the debate and the vote --


def _open(saga: Saga):
    rhine = _rhine(saga)
    _save(meeting.hold(saga, rhine))
    _save(meeting.hold(saga, rhine))
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
    assert vote.live(_values(vote)).startswith("For 4, against 1")
    called = list(meeting.call_the_vote(saga, rhine, rhine.meeting, case))
    assert [c.covenant.name for c in called] == ["Keep", "Fengheld"]
    assert called[0].tally == (0, 1, 0) and called[-1].tally == (4, 1, 0)
    # Keep undecided: an Upper Hand wins 20% of its one vote, rounded.
    lean = {"cov1": meeting.UNDECIDED, "cov_sketch": meeting.FOR}
    assert meeting.tally(saga, rhine, rhine.meeting, case, lean) == (4, 0, 1)
    _save(vote)
    assert rhine.meeting["votes"][case.id]["for"] == 4
    rulings = meeting.step_form(saga, rhine, _step(rhine, "rulings"))
    assert _values(rulings)[f"outcome_{case.id}"] == "Carried, 4 to 1"


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
        prosecutor="Leandro",
        defender="Severinus",
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
    _save(meeting.hold(saga, rhine))
    entry = rhine.diary[-1]
    assert len(rhine.diary) == before + 1
    assert entry.title == "¶ The First Day: Opening and the oaths"
    assert "the oaths were sworn" in entry.details
    assert entry.margin == "3 days"
    # Held again, its entry is rewritten, not added to.
    opening = meeting.step_form(saga, rhine, meeting.steps(rhine, rhine.meeting)[0])
    _save(opening, days=2)
    assert len(rhine.diary) == before + 1
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
