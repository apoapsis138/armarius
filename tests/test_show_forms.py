"""The Show form's core and the terminal's way to a Show's copy
(forms/show.py): what may be shown, who sees the More actions, Open a
Show, and "Open the live record"."""

from __future__ import annotations

import pytest
from fake_table import FakeTable
from test_shows import _begun, _hilda_ref, _show

from ars_magica_manager import (
    at_table,
    chronicle,
    commands,
    paths,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.models import Session

HOST = viewing.HOST


def _values(form: commands.Form, **given: object) -> dict[str, object]:
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values.update(given)
    return values


def test_the_form_offers_showable_records_and_saga_pictures() -> None:
    saga, _session, _book = _begun()
    offered = [value for _label, value in show_forms.what_options(saga)]
    assert "record:characters:hilda" in offered
    assert "picture:maps:rhine.png" in offered
    assert [v for _l, v in show_forms.story_options(saga)] == ["", "tower"]


def test_the_host_offers_only_pictures_it_has_a_seat_every_one_named() -> None:
    saga, _session, _book = _begun()
    (paths.data_dir() / paths.MAPS / "rhine.png").unlink()

    def pictures() -> list[str]:
        return [v for _l, v in show_forms.what_options(saga) if v.startswith("pic")]

    assert pictures() == []
    at_table.use_seat(FakeTable())
    try:
        assert pictures() == ["picture:maps:rhine.png"]
    finally:
        at_table.use_seat(None)


def test_the_form_hands_its_show_to_the_table_named_after_what_is_shown() -> None:
    saga, session, _book = _begun()
    table = FakeTable()
    form = show_forms.show_form(saga, session, HOST, table, _hilda_ref())
    assert isinstance(form, commands.Form)
    values = _values(form, to=["ben"], story="tower")

    assert values["title"] == "Old Hilda"
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)

    [call] = table.shown
    assert call.record == _hilda_ref()
    assert (call.title, call.to, call.story_id) == ("Old Hilda", ("ben",), "tower")


def test_another_list_can_start_the_form_on_a_picture() -> None:
    """A Show starts on whatever it is opened from (a Scene's handouts,
    later), not only a record's page."""
    saga, session, _book = _begun()
    form = show_forms.show_form(
        saga, session, HOST, FakeTable(), ("maps", "rhine.png"), to=("ben", "cara")
    )
    values = _values(form)
    assert (values["what"], values["title"]) == ("picture:maps:rhine.png", "The Rhine")
    assert values["to"] == ["ben"]  # Cara is Away


def test_a_player_is_not_offered_show(monkeypatch: pytest.MonkeyPatch) -> None:
    saga, session, _book = _begun()
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    assert isinstance(show_forms.show_here(saga, session), commands.Refuse)


def test_open_a_show_lists_those_the_reader_sees_and_opens_the_copy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    virtual_tabletop.set_on(True)
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("To Ana", _hilda_ref(), to=("ana",)))
    _show(book, saga, session, chronicle.ShowCall("To Ben", _hilda_ref(), to=("ben",)))
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    monkeypatch.setattr(viewing, "_in_use", chronicle.viewer_of(saga, "ana"))

    chooser = show_forms.open_show(saga, session)
    assert isinstance(chooser, commands.Choose)
    [only] = chooser.choices()
    assert only.label == "To Ana"
    opened = chooser.apply(only.value)

    assert isinstance(opened, commands.Form)
    [field] = opened.fields()
    assert "Old Hilda" in str(field.value)
    assert "KEPT-SECRET" not in str(field.value)


def test_a_seat_opens_no_show_of_a_session_it_doesnt_hold() -> None:
    """A Remote seat holds only the Session its host feeds it: a past
    Session chosen in Sessions lists none of tonight's Shows."""
    saga, session, book = _begun()
    entry = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    held = chronicle.SeatChronicle()
    held.take(session.id, entry)
    other = Session("s0", played=True)
    saga.sessions.insert(0, other)
    at_table.use_seat(FakeTable(held=held))
    try:
        assert show_forms.shows_held(saga, other, HOST)[1] == []
        assert show_forms.shows_held(saga, session, HOST)[1] == [entry]
    finally:
        at_table.use_seat(None)


def test_the_live_record_opens_only_for_one_who_may_read_it_now() -> None:
    saga, session, book = _begun()
    entry = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    assert show_forms.live_record(saga, entry, "ana") == _hilda_ref()

    saga.characters[2].known = False
    assert show_forms.live_record(saga, entry, "ana") is None
    assert show_forms.live_record(saga, entry, HOST) == _hilda_ref()
