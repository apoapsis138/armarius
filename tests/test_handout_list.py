"""Each Player's Handouts (handout_list.py): every Show leaves a Handout
with each Player shown, worked out from the Shows the Chronicles keep:
newest first, a repeat Show of the same thing a dated copy under the same
Handout, a withdrawn Show on no list."""

from __future__ import annotations

import pytest
from test_shows import _begun, _hilda_ref, _show

from ars_magica_manager import (
    chronicle,
    commands,
    handout_list,
    host_table,
    shows,
    viewing,
    virtual_tabletop,
)
from ars_magica_manager.forms import player_handouts
from ars_magica_manager.models import Session

HOST = viewing.HOST


def test_a_show_to_chosen_players_is_a_handout_for_each_and_no_one_else() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ana",)))

    [kept] = handout_list.of_player(saga, "ana")
    assert kept.title == "Hilda"
    assert [c.show_id for c in kept.copies] == [str(book.entries[-1].body["show"])]
    assert handout_list.of_player(saga, "ben") == []


def test_a_show_to_the_table_is_a_handout_for_each_player_at_the_session() -> None:
    saga, session, book = _begun()
    _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )

    assert [k.title for k in handout_list.of_player(saga, "ana")] == ["The Rhine"]
    assert [k.title for k in handout_list.of_player(saga, "ben")] == ["The Rhine"]
    assert handout_list.of_player(saga, "cara") == []  # Away that evening


def test_showing_the_same_thing_again_adds_a_dated_copy_newest_first() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )
    _show(book, saga, session, chronicle.ShowCall("Hilda again", _hilda_ref()))

    found = handout_list.of_player(saga, "ana")

    assert [k.title for k in found] == ["Hilda again", "The Rhine"]
    hilda = found[0]
    assert [c.title for c in hilda.copies] == ["Hilda again", "Hilda"]
    assert all(c.time for c in hilda.copies)
    assert hilda.kind == handout_list.RECORD and found[1].kind == handout_list.PICTURE


def test_handouts_are_kept_across_sessions() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    chronicle.end(saga, session, by=HOST)
    later = Session("s2", coming=["ana"], castings=list(session.castings))
    saga.sessions.append(later)
    tonight = chronicle.begin(saga, later, by=HOST)
    _show(
        tonight,
        saga,
        later,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )

    found = handout_list.of_player(saga, "ana")

    assert [(k.title, k.copies[0].session_id) for k in found] == [
        ("The Rhine", "s2"),
        ("Hilda", "s1"),
    ]


def test_a_withdrawn_show_leaves_every_list() -> None:
    saga, session, book = _begun()
    shown = _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    _show(book, saga, session, chronicle.ShowCall("Hilda again", _hilda_ref()))
    shows.withdraw(book, saga, session, shown.number, by=HOST)

    [hilda] = handout_list.of_player(saga, "ana")
    assert [c.title for c in hilda.copies] == ["Hilda again"]


def test_a_list_travels_as_plain_data_and_a_wrong_shape_is_refused() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )
    found = handout_list.of_player(saga, "ana")

    assert handout_list.from_data(handout_list.to_data(found)) == found
    with pytest.raises(ValueError, match="copies"):
        handout_list.from_data([{"key": "k", "kind": "record", "copies": "x"}])
    with pytest.raises(ValueError):
        handout_list.from_data({"key": "k"})


def test_the_host_table_gives_a_reader_only_a_list_they_may_read() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ben",)))

    ben = host_table.HostTable(saga, session, "ben").handouts("ben")
    assert isinstance(ben, list) and [k.title for k in ben] == ["Hilda"]
    assert host_table.HostTable(saga, session, "ana").handouts("ben") == (
        handout_list.NOT_YOURS
    )
    host = host_table.HostTable(saga, session, HOST).handouts("ben")
    assert isinstance(host, list) and len(host) == 1


def test_a_player_opens_their_handouts_from_a_character_they_play(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    virtual_tabletop.set_on(True)
    saga, session, book = _begun()
    saga.characters[0].background.player_ids = ["ana"]  # Aelfric
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    _show(book, saga, session, chronicle.ShowCall("Hilda again", _hilda_ref()))
    monkeypatch.setattr(chronicle, "here", lambda: "ana")

    assert player_handouts.offered_on(saga, saga.characters[0])
    assert not player_handouts.offered_on(saga, saga.characters[1])  # Ben's
    listed = player_handouts.mine(saga, saga.characters[0])
    assert isinstance(listed, commands.Choose)
    search, only = listed.choices()
    assert search.value == player_handouts.SEARCH
    assert only.label.startswith("Hilda again (shown 2 times")
    what = listed.apply(only.value)  # the player's own: Open or arrange it
    assert isinstance(what, commands.Choose)
    copies = what.apply(player_handouts.OPEN)
    assert isinstance(copies, commands.Choose)
    assert [c.label.split(": ")[1] for c in copies.choices()] == [
        "Hilda again",
        "Hilda",
    ]
    opened = copies.apply(1)
    assert isinstance(opened, commands.Form)
    assert "Old Hilda" in str(opened.fields()[0].value)


def test_the_storyguide_opens_any_players_handouts_from_their_row() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ben",)))

    listed = player_handouts.of_player(saga, 1)  # Ben, on the host's copy

    assert isinstance(listed, commands.Choose)
    assert listed.title == "Ben's Handouts"
    [only] = listed.choices()
    opened = listed.apply(only.value)
    assert isinstance(opened, commands.Form)
    assert isinstance(player_handouts.of_player(saga, None), commands.Refuse)


def test_a_player_is_refused_another_players_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, _session, _book = _begun()
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    assert isinstance(player_handouts.of_player(saga, 1), commands.Refuse)


def test_the_storyguide_reads_every_players_list_and_a_player_only_their_own() -> None:
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref(), to=("ben",)))

    assert handout_list.readable(saga, "ben", HOST)
    assert handout_list.readable(saga, "ben", "ben")
    assert not handout_list.readable(saga, "ben", "ana")
