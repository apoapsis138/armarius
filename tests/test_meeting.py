"""Holding a Tribunal: opening a meeting, its order of business by day,
attendance and proxies, leaving and resuming at the step in hand, and
closing it into the Diary."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import meeting, storage
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.models import CASE_DECIDED, Saga


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
    assert "defender" not in {f.key for f in motion.fields(saga, rhine, rhine.meeting)}


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
    assert len(rhine.diary) == diary + 1
    assert rhine.diary[-1].title == "The Tribunal met at Durenmar"
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
