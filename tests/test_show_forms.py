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
    shows,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.form_spec import DialogField
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.forms.more import registry
from ars_magica_manager.models import Character, Player, Saga, Session

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


def _hidden_hilda_form(
    table: FakeTable,
) -> tuple[Saga, Character, commands.Form]:
    """The Show form on Old Hilda, whom the players don't know of yet."""
    saga, session, _book = _begun()
    hilda = saga.characters[2]
    hilda.known = False
    return saga, hilda, show_forms.show_form(saga, session, HOST, table, _hilda_ref())


HILDA = "record:characters:hilda"


def _secrets_field(form: commands.Form) -> DialogField:
    return next(f for f in form.fields() if f.key == show_forms.SECRETS)


def _kept(hilda: Character) -> list[tuple[int, str]]:
    """Hilda's Kept Secret (her second; the first is revealed), ticked."""
    return [(1, shows.secret_mark(hilda.secrets[1]))]


def test_the_form_ticks_the_chosen_records_secrets_not_yet_revealed() -> None:
    table = FakeTable()
    _saga, hilda, form = _hidden_hilda_form(table)
    field = _secrets_field(form)
    assert field.show_if is not None and field.choose is not None
    assert field.show_if({"what": HILDA})
    assert not field.show_if({"what": "picture:maps:rhine.png"})

    chooser = field.choose([], {"what": HILDA})
    assert isinstance(chooser, commands.Form)
    [tick] = [f for f in chooser.fields() if f.kind == "check"]
    assert tick.label == "Kept"  # Seen is revealed already
    assert chooser.apply({tick.key: True}) == commands.Picked(_kept(hilda))

    form.apply(_values(form, **{show_forms.SECRETS: _kept(hilda)}))

    assert table.shown[0].secrets == tuple(_kept(hilda))
    assert table.shown[0].reveal is False


def test_choosing_something_else_clears_the_ticks() -> None:
    _saga, _hilda, form = _hidden_hilda_form(FakeTable())
    what = next(f for f in form.fields() if f.key == "what")
    assert what.fills is not None
    assert what.fills({"what": "picture:maps:rhine.png"})[show_forms.SECRETS] == []


def test_only_the_records_own_storyguide_is_offered_its_secrets() -> None:
    saga, hilda, form = _hidden_hilda_form(FakeTable())
    saga.players.append(Player("gail", "Gail", role=viewing.STORYGUIDE))
    hilda.storyguide_id = "gail"

    field = _secrets_field(form)
    assert field.show_if is not None and not field.show_if({"what": HILDA})
    assert field.choose is not None
    assert isinstance(field.choose([], {"what": HILDA}), commands.Refuse)


def test_show_and_its_more_actions_save_what_they_reveal() -> None:
    assert registry.REFRESH["show_record"].saves
    assert registry.REFRESH["show_at_session"].saves


def test_without_also_reveal_nothing_changes_for_the_troupe() -> None:
    saga, hilda, form = _hidden_hilda_form(FakeTable())
    diary = list(saga.covenants[1].diary)

    form.apply(_values(form, **{show_forms.SECRETS: _kept(hilda)}))

    assert not hilda.known and not hilda.secrets[1].revealed
    assert saga.covenants[1].diary == diary


def test_also_reveal_makes_the_record_known_and_reveals_the_ticked_secrets() -> None:
    table = FakeTable()
    saga, hilda, form = _hidden_hilda_form(table)

    form.apply(
        _values(
            form, **{show_forms.SECRETS: _kept(hilda), show_forms.ALSO_REVEAL: True}
        )
    )

    assert table.shown[0].reveal is True
    assert hilda.known
    kept = hilda.secrets[1]
    assert (kept.revealed_year, kept.revealed_season) == (
        saga.current_year,
        saga.current_season,
    )
    lines = [e.name for e in saga.covenants[1].diary]
    assert "Revealed: Old Hilda" in lines
    assert "Revealed: Old Hilda: Kept" in lines


def test_a_show_the_table_refuses_reveals_nothing() -> None:
    _saga, hilda, form = _hidden_hilda_form(FakeTable(refuse="No."))

    form.apply(
        _values(
            form, **{show_forms.SECRETS: _kept(hilda), show_forms.ALSO_REVEAL: True}
        )
    )

    assert not hilda.known and not hilda.secrets[1].revealed


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


def test_withdraw_chooses_a_show_still_out_then_asks_first() -> None:
    saga, session, book = _begun()
    one = _show(book, saga, session, chronicle.ShowCall("One", _hilda_ref()))
    two = _show(book, saga, session, chronicle.ShowCall("Two", _hilda_ref()))
    shows.withdraw(book, saga, session, one.number, by=HOST)
    table = FakeTable(held=book)

    chooser = show_forms.withdraw_from(saga, session, HOST, table)

    assert isinstance(chooser, commands.Choose)
    [left] = chooser.choices()
    assert (left.label, left.value) == ("Two", two.number)
    asked = chooser.apply(left.value)
    assert isinstance(asked, commands.Confirm) and asked.yes_label == "Withdraw"
    assert table.withdrawn == []
    asked.apply()
    assert table.withdrawn == [two.number]


def test_a_player_is_not_offered_withdraw(monkeypatch: pytest.MonkeyPatch) -> None:
    saga, session, _book = _begun()
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    assert isinstance(show_forms.withdraw_here(saga, session), commands.Refuse)


def test_open_a_show_leaves_out_those_withdrawn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, session, book = _begun()
    gone = _show(book, saga, session, chronicle.ShowCall("Gone", _hilda_ref()))
    _show(book, saga, session, chronicle.ShowCall("Kept", _hilda_ref()))
    shows.withdraw(book, saga, session, gone.number, by=HOST)
    monkeypatch.setattr(chronicle, "here", lambda: "ana")

    chooser = show_forms.open_show(saga, session)

    assert isinstance(chooser, commands.Choose)
    assert [c.label for c in chooser.choices()] == ["Kept"]


def test_the_storyguide_still_opens_a_withdrawn_show_marked_so() -> None:
    saga, session, book = _begun()
    gone = _show(book, saga, session, chronicle.ShowCall("Gone", _hilda_ref()))
    shows.withdraw(book, saga, session, gone.number, by=HOST)

    chooser = show_forms.open_show(saga, session)  # the host's own copy

    assert isinstance(chooser, commands.Choose)
    assert [c.label for c in chooser.choices()] == ["Gone (withdrawn)"]


def test_open_a_show_says_none_is_still_out_once_all_are_withdrawn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, session, book = _begun()
    gone = _show(book, saga, session, chronicle.ShowCall("Gone", _hilda_ref()))
    shows.withdraw(book, saga, session, gone.number, by=HOST)
    monkeypatch.setattr(chronicle, "here", lambda: "ana")

    chooser = show_forms.open_show(saga, session)

    assert isinstance(chooser, commands.Choose)
    assert chooser.empty == "No Show of this Session is still out."


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
