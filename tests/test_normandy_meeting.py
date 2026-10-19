"""Normandy's meeting steps: the eldest magus named Praeco when the seat
is vacant, and the next host drawn by lot with one redraw."""

from __future__ import annotations

from support import everything_saga

from ars_magica_manager import meeting
from ars_magica_manager.commands import Form
from ars_magica_manager.models import Character, Covenant, Saga, Tribunal
from ars_magica_manager.sheets import tribunal as tribunal_sheet


def _normandy(saga: Saga) -> Tribunal:
    tribunal = saga.tribunal("normandy")
    assert tribunal is not None
    for cid, name, magi in (
        ("cunfin", "Cunfin", [("celeres", "Celeres", 1101)]),
        ("lapis", "Lapis Crudus", [("somnifer", "Somnifer", 1120)]),
        ("montverte", "Montverte", [("geirlaug", "Geirlaug", 1135)]),
    ):
        saga.covenants.append(
            Covenant(id=cid, saga_id=saga.id, name=name, tribunal_id="normandy")
        )
        for mid, mname, born in magi:
            magus = Character(id=mid, name=mname, type="magus", covenant_id=cid)
            magus.background.year_born = born
            saga.characters.append(magus)
    return tribunal


def _step(tribunal: Tribunal, key: str) -> meeting.Step:
    return next(s for s in meeting.steps(tribunal, tribunal.meeting) if s.key == key)


def _hold(saga: Saga, tribunal: Tribunal, key: str, **changes) -> None:
    form = meeting.step_form(saga, tribunal, _step(tribunal, key))
    assert isinstance(form, Form)
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(changes)
    form.apply(values)


def _opened(saga: Saga) -> Tribunal:
    tribunal = _normandy(saga)
    form = meeting.hold(saga, tribunal)
    assert isinstance(form, Form)
    form.apply({f.key: f.value for f in form.fields() if f.kind != "info"})
    return tribunal


def test_the_steps_come_in_their_places():
    saga = everything_saga()
    tribunal = _opened(saga)
    keys = [s.key for s in meeting.steps(tribunal, tribunal.meeting)]
    assert keys[:3] == ["opening", "attendance", "succession"]
    assert keys[-2:] == ["host_by_lot", "closing"]
    assert keys.index("tourney") < keys.index("rulings")


def test_a_vacant_seat_shows_on_the_sheet():
    saga = everything_saga()
    tribunal = _normandy(saga)
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, tribunal)}
    assert facts["Praeco"] == "Vacant"
    rhine = saga.tribunal("rhine")
    assert rhine is not None
    rhine.praeco_id = None
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, rhine)}
    assert facts["Praeco"] == "(not chosen)"


def test_the_eldest_magus_is_offered_then_the_next():
    saga = everything_saga()
    tribunal = _opened(saga)
    form = meeting.step_form(saga, tribunal, _step(tribunal, "succession"))
    assert isinstance(form, Form)
    (praeco,) = [f for f in form.fields() if f.key == "praeco"]
    assert praeco.value == "celeres"
    assert [v for _label, v in praeco.options] == ["celeres", "somnifer", "geirlaug"]
    # Celeres is set aside: Somnifer is named.
    _hold(saga, tribunal, "succession", praeco="somnifer")
    assert tribunal.praeco_id == "somnifer"
    entry = tribunal.diary[-1]
    assert "Somnifer was named Praeco, Celeres being set aside." in entry.details
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, tribunal)}
    assert facts["Praeco"] == "Somnifer"


def test_with_a_praeco_there_is_no_succession():
    saga = everything_saga()
    tribunal = _opened(saga)
    tribunal.praeco_id = "geirlaug"
    form = meeting.step_form(saga, tribunal, _step(tribunal, "succession"))
    assert isinstance(form, Form)
    assert "praeco" not in {f.key for f in form.fields()}


def test_the_next_host_is_drawn_by_lot_with_one_redraw():
    saga = everything_saga()
    tribunal = _opened(saga)
    tribunal.meeting["lot"] = ["lapis", "montverte"]
    step = _step(tribunal, "host_by_lot")
    form = meeting.step_form(saga, tribunal, step)
    assert isinstance(form, Form)
    shown = {f.key: f for f in form.fields()}
    assert shown["drawn"].value == "The lot falls on Lapis Crudus."
    assert form.live is not None
    assert form.live({"redraw": True}) == "Next host: Montverte."
    _hold(saga, tribunal, "host_by_lot", redraw=True)
    assert tribunal.meeting_place == "Montverte"
    assert "fell on the second draw on Montverte" in tribunal.diary[-1].details


def test_the_lot_is_drawn_once():
    saga = everything_saga()
    tribunal = _opened(saga)
    step = _step(tribunal, "host_by_lot")
    meeting.step_form(saga, tribunal, step).fields()
    drawn = list(tribunal.meeting["lot"])
    assert len(drawn) == 2 and set(drawn) <= {"cunfin", "lapis", "montverte"}
    meeting.step_form(saga, tribunal, step).fields()
    assert tribunal.meeting["lot"] == drawn


def test_founding_in_normandy_names_the_vis_it_needs():
    from ars_magica_manager.forms import creation as creation_forms
    from ars_magica_manager.tribunal_packages import normandy

    saga = everything_saga()
    (told,) = [
        f
        for f in creation_forms.new_covenant_fields(saga)
        if f.key == "package_normandy_founding"
    ]
    assert told.kind == "info" and told.value == normandy.FOUNDING
    assert told.show_if is not None and told.show_if({"tribunal_id": "normandy"})
    assert not told.show_if({"tribunal_id": "rhine"})
