"""Hibernia's customs: a covenant votes only while it shows its cathach,
and one being founded is recognised a year after it began holding it."""

from __future__ import annotations

import random

from support import everything_saga

from ars_magica_manager import (
    gifted_children,
    hibernia_meeting,
    meeting,
    tribunal_packages,
    vis,
)
from ars_magica_manager.commands import Form
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import Saga
from ars_magica_manager.models.world import SKETCH
from ars_magica_manager.sheets import tribunal as tribunal_sheet
from ars_magica_manager.tribunal_packages import hibernia


def _hibernian(saga: Saga):
    tribunal = saga.tribunal("rhine")
    assert tribunal is not None
    tribunal.package = hibernia.KEY
    return tribunal


def _save(form, **changes):
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    assert form.validate is None or form.validate(values) is None
    form.apply(values)


def test_the_roster_shows_each_cathach_or_who_took_it():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep = saga.covenant("cov1")
    assert keep is not None
    hibernia.save_covenant(tribunal, "cov1", {"cathach": " The tusks "})
    assert hibernia.cathach_text(saga, tribunal, keep) == "The tusks"
    hibernia.save_covenant(
        tribunal,
        "cov1",
        {"cathach": "The tusks", "taken_by": "Vigil", "taken_year": 1219},
    )
    assert hibernia.cathach_text(saga, tribunal, keep) == "Taken by Vigil (1219)"
    assert hibernia.lacks_cathach(saga, tribunal, keep) == (
        "Its cathach is held by Vigil since 1219"
    )
    grid = tribunal_sheet.roster_grid(saga, tribunal)
    assert "Cathach" in grid.columns
    hibernia.save_covenant(
        tribunal, "cov1", {"cathach": "", "taken_by": "", "taken_year": None}
    )
    assert hibernia.cathach_of(tribunal, "cov1") == {}


def test_a_covenant_being_founded_is_recognised_a_year_on():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep = saga.covenant("cov1")
    assert keep is not None
    saga.current_year = 1220
    hibernia.save_covenant(tribunal, "cov1", {"cathach": "A skull", "since": 1220})
    assert hibernia.cathach_text(saga, tribunal, keep) == "Founding: recognised 1221"
    assert "recognised in 1221" in hibernia.lacks_cathach(saga, tribunal, keep)
    saga.current_year = 1221
    assert hibernia.cathach_text(saga, tribunal, keep) == "A skull"
    assert hibernia.lacks_cathach(saga, tribunal, keep) == ""


def test_a_new_covenant_is_told_what_founding_asks():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    package = tribunal_packages.of(tribunal)
    assert package.covenant_fields is not None
    fields = package.covenant_fields(saga, tribunal, None)
    assert fields[0].kind == "info" and "cattle" in str(fields[0].value)
    keys = [f.key for f in tribunal_forms.package_fields(saga, None)]
    assert f"package_{tribunal.id}_cathach" in keys


def test_a_covenant_without_its_cathach_has_no_vote():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep = saga.covenant("cov1")
    assert keep is not None
    unopened = meeting.record(saga, tribunal)
    before, _ = meeting.hall(saga, tribunal, unopened)
    keeps = sum(meeting.present(saga, tribunal, unopened, keep))
    assert keeps > 0
    hibernia.save_covenant(tribunal, "cov1", {"taken_by": "Vigil"})
    attendance = meeting.hold(saga, tribunal)
    field = next(f for f in attendance.fields() if f.key == "shows_cov1")
    assert field.value is False and "held by Vigil" in field.hint
    _save(attendance)
    after, _ = meeting.hall(saga, tribunal, tribunal.meeting)
    assert after == before - keeps
    row = next(
        r for r in meeting.attendance_grid(saga, tribunal).rows if r[0] == keep.name
    )
    assert row[4] == "0, no cathach"
    step = meeting.steps(tribunal, tribunal.meeting)[0]
    words, _ = step.minutes(saga, tribunal, tribunal.meeting)
    assert f"{keep.name} did not show its cathach" in words


def test_the_storyguide_decides_at_the_meeting_who_shows_it():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep = saga.covenant("cov1")
    assert keep is not None
    _save(meeting.hold(saga, tribunal), shows_cov1=False)
    assert meeting.present(saga, tribunal, tribunal.meeting, keep) == (0, 0)
    assert tribunal.meeting is not None
    tribunal.meeting["done"].remove("attendance")
    _save(meeting.hold(saga, tribunal), shows_cov1=True)
    assert sum(meeting.present(saga, tribunal, tribunal.meeting, keep)) > 0


def test_other_customs_ask_for_no_cathach():
    saga = everything_saga()
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    keys = {f.key for f in meeting.hold(saga, rhine).fields()}
    assert not any(k.startswith("shows_") for k in keys)


def test_hibernia_refuses_a_vassal_in_its_tribunal():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep, other = saga.covenant("cov1"), saga.covenant("cov_sketch")
    assert keep is not None and other is not None
    assert other.tribunal_id == keep.tribunal_id == tribunal.id
    form = covenant_forms.covenant_form(saga, keep)
    assert form.validate is not None
    problem = form.validate({"tribunal_id": tribunal.id, "liege_id": other.id})
    assert problem is not None and "no vassal covenants" in problem
    assert form.validate({"tribunal_id": tribunal.id, "liege_id": None}) is None
    # Leaving for a Tribunal without that custom, the oath may be sworn.
    assert form.validate({"tribunal_id": None, "liege_id": other.id}) is None
    tribunal.package = "rhine"
    assert form.validate({"tribunal_id": tribunal.id, "liege_id": other.id}) is None


# -- ambassadors, treaties and the tithe --


def _held_to(saga: Saga, tribunal, key: str) -> None:
    """Hold the meeting's steps until the one keyed `key` is in hand."""
    _save(meeting.hold(saga, tribunal))
    while meeting.current(tribunal, tribunal.meeting).key != key:
        _save(meeting.hold(saga, tribunal))


def _ambassadors(tribunal) -> None:
    ops = hibernia.ambassador_ops(None, tribunal)  # type: ignore[arg-type]
    assert ops.add is not None
    _save(ops.add(), faction="The Tuatha Dé", name="Fothaid")
    _save(ops.add(), faction="The Coill Trí", name="", confirmed=False)


def test_confirmed_ambassadors_vote_beside_the_covenants():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    _save(meeting.hold(saga, tribunal))
    before, _ = meeting.hall(saga, tribunal, tribunal.meeting)
    _ambassadors(tribunal)
    grid = hibernia.ambassadors_grid(saga, tribunal)
    assert grid.rows == [
        ["The Tuatha Dé", "Fothaid", "Confirmed"],
        ["The Coill Trí", "", ""],
    ]
    assert meeting.hall(saga, tribunal, tribunal.meeting)[0] == before + 1
    names = [v.name for v in meeting.voters(saga, tribunal, tribunal.meeting)]
    assert names[-1] == "Fothaid"
    # The Sacred Council confirms both: two more votes, each called.
    council = meeting.hold(saga, tribunal)
    while meeting.current(tribunal, tribunal.meeting).key != "sacred_council":
        _save(council)
        council = meeting.hold(saga, tribunal)
    ids = [a["id"] for a in hibernia.ambassadors(tribunal)]
    _save(council, **{f"confirm_{ids[1]}": True}, disputes="A stolen cow")
    assert meeting.hall(saga, tribunal, tribunal.meeting)[0] == before + 2
    case = tribunal.cases[0]
    called = list(meeting.call_the_vote(saga, tribunal, tribunal.meeting, case))
    assert [c.covenant.name for c in called][-2:] == ["Fothaid", "The Coill Trí"]
    assert called[-1].tally[2] >= 2
    step = meeting.steps(tribunal, tribunal.meeting)[2]
    words, margin = step.minutes(saga, tribunal, tribunal.meeting)
    assert "Fothaid for The Tuatha Dé" in words and "A stolen cow" in words
    assert margin == "2 ambassadors"


def test_a_treaty_is_kept_with_its_witness():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    ops = hibernia.treaty_ops(saga, tribunal)
    assert ops.add is not None
    _save(
        ops.add(),
        title="The Treaty of Cnoc Maol Réidh",
        parties="The Order; the Coill Trí",
        year=1110,
        witness="A Quaesitor",
        ends="Never",
    )
    grid = hibernia.treaties_grid(saga, tribunal)
    assert grid.rows[0][:3] == [
        "The Treaty of Cnoc Maol Réidh",
        "The Order; the Coill Trí",
        "1110",
    ]


def test_the_generator_makes_seven_children_one_per_tuath():
    rng = random.Random(4)
    children = gifted_children.tithe(rng, [("Túath Saidhbh", "Saidhbh")], 1220)
    assert len(children) == 7
    assert children[0]["tuath"] == "Túath Saidhbh"
    assert children[1]["tuath"] == "The Second Túath"
    for child in children:
        assert gifted_children.YOUNGEST <= child["age"] <= gifted_children.ELDEST
        assert child["gift"] in gifted_children.GIFTS
        assert child["born"] == 1220 - child["age"]
        assert 1 <= len(child["hints"]) <= 2
    again = gifted_children.tithe(random.Random(4), [("Túath Saidhbh", "")], 1220)
    assert [c["name"] for c in again] == [c["name"] for c in children]


def test_the_bidding_gives_each_child_to_the_highest_bid():
    children = [
        {"name": "A", "gift": "The Gift"},
        {"name": "B", "gift": "The Gift", "false_gift": True},
        {"name": "C", "gift": "Blatant Gift"},
        {"name": "D", "gift": "The Gift"},
    ]
    rich = gifted_children.Bidder("rich", "Rich", ["m1", "m2"], 40)
    poor = gifted_children.Bidder("poor", "Poor", ["m3"], 2)
    awards = gifted_children.bid(random.Random(1), children, [rich, poor])
    assert awards[0].covenant_id == "rich" and awards[0].master_id == "m1"
    assert awards[0].bids[0] == ("Rich", awards[0].price)
    assert awards[1].covenant_id is None and awards[1].bids == []
    # Each magus takes one child; a covenant pays from what it has left.
    taken = [a.master_id for a in awards if a.master_id]
    assert len(taken) == len(set(taken)) == 3
    assert rich.pawns + poor.pawns == 42 - sum(a.price for a in awards)
    assert all(a.price <= 40 for a in awards)


def test_the_tithe_by_bidding_pays_vis_and_makes_apprentices():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    keep = saga.covenant("cov1")
    assert keep is not None
    vis._credit(keep, "Vim", 30)
    _held_to(saga, tribunal, "tithe")
    tithe = meeting.hold(saga, tribunal)
    assert isinstance(tithe, Form) and tithe.save_label == "Give"
    tithe.fields()
    record = tribunal.meeting["tithe"]
    assert len(record["candidates"]) == 7
    assert all(len(slot) == 3 for slot in record["candidates"])
    for slot in record["candidates"]:
        slot[0]["false_gift"] = False
    values = {f.key: f.value for f in tithe.fields() if f.kind != "info"}
    assert values["how"] == hibernia_meeting.BY_BIDDING
    preview = tithe.live(values) if tithe.live else ""
    assert preview == (tithe.live(values) if tithe.live else "")
    assert "Leandro of Keep" in preview
    _save(tithe)
    given = record["given"]
    won = [g for g in given if g.get("covenant_id") == "cov1"]
    # Keep's one magus takes one child; its price came from its Vim.
    assert len(won) == 1
    paid = won[0]["price"]
    assert sum(h.pawns for h in vis.held(keep)) == 30 - paid
    child = saga.character(won[0]["character_id"])
    assert child is not None and child.detail == SKETCH
    assert child.covenant_id == "cov1" and child.hermetic.parens == "Leandro"
    assert hibernia_meeting.apprenticed(saga, saga.character("mag1"))
    step = meeting.current(tribunal, tribunal.meeting)
    assert step.key == "closing"
    tithe_step = next(
        s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == "tithe"
    )
    words, margin = tithe_step.minutes(saga, tribunal, tribunal.meeting)
    assert "to Leandro of Keep" in words and margin.endswith("apprentice")


def test_the_storyguide_may_give_the_children_by_hand():
    saga = everything_saga()
    tribunal = _hibernian(saga)
    _held_to(saga, tribunal, "tithe")
    tithe = meeting.hold(saga, tribunal)
    assert isinstance(tithe, Form)
    tithe.fields()
    record = tribunal.meeting["tithe"]
    for slot in record["candidates"]:
        for child in slot:
            child["false_gift"] = False
    record["candidates"][0][1]["false_gift"] = True
    values = {f.key: f.value for f in tithe.fields() if f.kind != "info"}
    values.update(how=hibernia_meeting.BY_HAND, child_0="1", claim_0="mag1")
    assert tithe.validate is not None
    assert "no true Gift" in (tithe.validate(values) or "")
    values.update(child_0="0", claim_1="mag1")
    assert tithe.validate(values) == "Each magus takes one child."
    values.update(claim_1=None, claim_2="mag_sketch")
    assert tithe.validate(values) is None
    tithe.apply(values)
    given = record["given"]
    assert given[0]["master_id"] == "mag1" and given[0]["price"] == 0
    assert given[2]["master_id"] == "mag_sketch"
    assert sum(1 for g in given if g.get("master_id")) == 2
    # Holding it again changes only the note: no more apprentices.
    count = len(saga.characters)
    step = next(
        s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == "tithe"
    )
    _save(meeting.step_form(saga, tribunal, step), note="Done")
    assert len(saga.characters) == count
