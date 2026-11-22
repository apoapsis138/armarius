"""A player's own arrangement of their Handouts (handout_arrangement.py):
their titles, pins and folders, one level deep, kept in a file of theirs
beside the saga that only they may read or change."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from test_shows import _begun, _hilda_ref, _show

from ars_magica_manager import (
    chronicle,
    commands,
    handout_arrangement,
    handout_list,
    host_table,
    sessions,
    shows,
    viewing,
)
from ars_magica_manager.forms import player_handouts
from ars_magica_manager.handout_arrangement import Arrange
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import handing

HOST = viewing.HOST


def _two() -> tuple[Saga, list[handout_list.Kept]]:
    """Ana's two Handouts: Old Hilda's record, then the Rhine map."""
    saga, session, book = _begun()
    _show(book, saga, session, chronicle.ShowCall("Hilda", _hilda_ref()))
    _show(
        book,
        saga,
        session,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )
    return saga, handout_list.of_player(saga, "ana")


def test_a_player_renames_pins_and_files_a_handout_and_it_is_kept() -> None:
    saga, found = _two()
    hilda = next(k for k in found if k.title == "Hilda")

    for call in (
        Arrange(hilda.key, title="Hilda, the herbwife"),
        Arrange(hilda.key, pinned=True),
        Arrange(hilda.key, folder="People"),
    ):
        assert handout_arrangement.arrange(saga, "ana", call, by="ana") is None

    kept = handout_arrangement.load(saga.id, "ana")
    [place] = kept.places
    assert (place.key, place.title, place.pinned, place.folder) == (
        hilda.key,
        "Hilda, the herbwife",
        True,
        "People",
    )
    assert kept.folders == ["People"]


def test_the_list_reads_as_arranged_pinned_first_with_the_players_titles() -> None:
    saga, found = _two()
    hilda = next(k for k in found if k.title == "Hilda")
    handout_arrangement.arrange(saga, "ana", Arrange(hilda.key, pinned=True), by="ana")
    handout_arrangement.arrange(
        saga, "ana", Arrange(hilda.key, title="Herbwife", folder="People"), by="ana"
    )

    shown = handout_arrangement.arranged(
        found, handout_arrangement.load(saga.id, "ana")
    )

    # Unfiled first, then each folder, pinned first within each.
    assert [(s.title, s.folder, s.pinned) for s in shown] == [
        ("The Rhine", "", False),
        ("Herbwife", "People", True),
    ]
    assert shown[1].kept is hilda


def test_pinned_handouts_come_first_within_their_folder() -> None:
    saga, found = _two()
    rhine, hilda = found  # newest first: the Rhine, then Hilda
    handout_arrangement.arrange(saga, "ana", Arrange(hilda.key, pinned=True), by="ana")

    shown = handout_arrangement.arranged(
        found, handout_arrangement.load(saga.id, "ana")
    )

    assert [s.kept for s in shown] == [hilda, rhine]


def test_an_empty_title_or_folder_puts_back_the_shown_one() -> None:
    saga, found = _two()
    key = found[0].key
    handout_arrangement.arrange(
        saga, "ana", Arrange(key, title="Mine", folder="F"), by="ana"
    )
    handout_arrangement.arrange(
        saga, "ana", Arrange(key, title="", folder=""), by="ana"
    )

    [shown, _other] = handout_arrangement.arranged(
        found, handout_arrangement.load(saga.id, "ana")
    )
    assert (shown.title, shown.folder) == (found[0].title, "")
    assert handout_arrangement.load(saga.id, "ana").folders == []


def test_only_that_player_reads_or_changes_their_arrangement() -> None:
    saga, found = _two()
    call = Arrange(found[0].key, title="Mine")

    assert handout_arrangement.arrange(saga, "ana", call, by="ben") == (
        handout_arrangement.NOT_YOURS
    )
    assert handout_arrangement.arrange(saga, "ana", call, by=HOST) == (
        handout_arrangement.NOT_YOURS
    )
    assert handout_arrangement.load(saga.id, "ana").places == []
    assert handout_arrangement.readable("ana", "ana")
    assert not handout_arrangement.readable("ana", "ben")
    assert not handout_arrangement.readable("ana", HOST)


def test_titles_and_folders_keep_the_character_rule_and_their_length() -> None:
    saga, found = _two()
    key = found[0].key

    for call in (
        Arrange(key, title="Bad\x07title"),
        Arrange(key, folder="(no folder)"),
        Arrange(key, folder="x" * 81),
        Arrange(key, title="y" * 201),
        Arrange("nothing:shown", pinned=True),
    ):
        assert handout_arrangement.arrange(saga, "ana", call, by="ana") is not None
    assert handout_arrangement.load(saga.id, "ana").places == []


def test_the_host_table_arranges_for_its_reader_alone() -> None:
    saga, found = _two()
    session = saga.sessions[0]
    call = Arrange(found[0].key, pinned=True)

    assert host_table.HostTable(saga, session, "ben").arrange("ana", call) == (
        handout_arrangement.NOT_YOURS
    )
    assert host_table.HostTable(saga, session, "ben").arrangement("ana") == (
        handout_arrangement.NOT_YOURS
    )
    ana = host_table.HostTable(saga, session, "ana")
    assert ana.arrange("ana", call) is None
    kept = ana.arrangement("ana")
    assert isinstance(kept, handout_arrangement.Arrangement)
    assert kept.places[0].pinned


def test_an_arrangement_travels_as_plain_data_and_a_wrong_shape_is_refused() -> None:
    kept = handout_arrangement.Arrangement(
        ["People"], [handout_arrangement.Place("k", "People", "Mine", True)]
    )
    assert handout_arrangement.from_data(handout_arrangement.to_data(kept)) == kept
    with pytest.raises(ValueError):
        handout_arrangement.from_data({"folders": "x", "places": []})


# -- the list, as the player arranges it --


def _mine(saga: Saga, monkeypatch: pytest.MonkeyPatch) -> commands.Choose:
    monkeypatch.setattr(chronicle, "here", lambda: "ana")
    listed = player_handouts.handouts(player_handouts.here(saga), saga, "ana")
    assert isinstance(listed, commands.Choose)
    return listed


def _choice(listed: commands.Choose, starts: str) -> commands.Choice:
    return next(c for c in listed.choices() if c.label.startswith(starts))


def test_the_players_list_filters_by_folder_session_kind_and_story_and_searches_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, found = _two()
    hilda = next(k for k in found if k.title == "Hilda")
    handout_arrangement.arrange(
        saga, "ana", Arrange(hilda.key, folder="People", pinned=True), by="ana"
    )

    listed = _mine(saga, monkeypatch)

    assert listed.filters == player_handouts.FILTERS
    search, rhine, hilda = listed.choices()
    assert search.value == player_handouts.SEARCH
    assert rhine.label.startswith("The Rhine") and hilda.label.startswith("Hilda")
    facets = dict(hilda.facets)
    assert facets["Folder"] == "People"
    assert facets["Kind"] == "Record"
    assert facets["Session"] == f"1. {sessions.title(saga.sessions[0])}"
    assert dict(rhine.facets)["Kind"] == "Picture"
    assert dict(rhine.facets)["Folder"] == ""  # unfiled: no heading
    assert "Old Hilda" not in hilda.search  # words are searched on the host


def test_searching_the_words_lists_the_handouts_whose_copies_hold_them(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, _found = _two()
    listed = _mine(saga, monkeypatch)

    asked = listed.apply(player_handouts.SEARCH)
    assert isinstance(asked, commands.Form)
    found = asked.apply({"words": "old hilda"})

    assert isinstance(found, commands.Choose)
    assert [c.label.split(" (")[0] for c in found.choices()] == ["Hilda"]


def test_the_host_searches_each_copy_once_and_a_list_reads_no_copy(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, _found = _two()
    read: list[str] = []
    real = shows.read_copy

    def counted(saga_id: str, show_id: str) -> dict[str, object]:
        read.append(show_id)
        return real(saga_id, show_id)

    monkeypatch.setattr(shows, "read_copy", counted)
    handout_list.of_player(saga, "ana")
    assert read == []  # the list carries titles alone
    first = handout_list.matching(saga, "ana", "hilda")
    again = handout_list.matching(saga, "ana", "rhine")

    assert len(read) == 2  # each copy read once, then kept
    assert first == {"characters:hilda"}
    assert again == set()  # a picture has no words; its title is searched locally


def test_the_list_and_its_menu_read_the_arrangement_afresh_after_a_change(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, _found = _two()
    listed = _mine(saga, monkeypatch)
    hilda = _choice(listed, "Hilda")
    what = listed.apply(hilda.value)
    assert isinstance(what, commands.Choose)

    what.apply(player_handouts.PIN)

    assert "Unpin" in [c.label for c in what.choices()]
    assert [c.label.split(" (")[0] for c in listed.choices()][1:] == [
        "Hilda",
        "The Rhine",
    ]
    what.apply(player_handouts.PIN)
    [place] = handout_arrangement.load(saga.id, "ana").places or [None]
    assert place is None  # unpinned again: nothing left to keep


def test_choosing_a_handout_offers_open_rename_pin_and_move(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    saga, _found = _two()
    listed = _mine(saga, monkeypatch)

    what = listed.apply(_choice(listed, "The Rhine").value)

    assert isinstance(what, commands.Choose)
    assert [c.value for c in what.choices()] == [
        player_handouts.OPEN,
        player_handouts.RENAME,
        player_handouts.PIN,
        player_handouts.MOVE,
    ]
    rename = what.apply(player_handouts.RENAME)
    assert isinstance(rename, commands.Form)
    rename.apply({"title": "The river"})
    pinned = what.apply(player_handouts.PIN)
    assert pinned is not None
    move = what.apply(player_handouts.MOVE)
    assert isinstance(move, commands.Form)
    move.apply({"folder": "", "new_folder": "Maps"})

    [place] = handout_arrangement.load(saga.id, "ana").places
    assert (place.title, place.pinned, place.folder) == ("The river", True, "Maps")


def test_a_pinned_handout_offers_unpin(monkeypatch: pytest.MonkeyPatch) -> None:
    saga, found = _two()
    handout_arrangement.arrange(
        saga, "ana", Arrange(found[0].key, pinned=True), by="ana"
    )
    listed = _mine(saga, monkeypatch)

    what = listed.apply(listed.choices()[1].value)  # after Search their words

    assert isinstance(what, commands.Choose)
    labels = [c.label for c in what.choices()]
    assert "Unpin" in labels and "Pin" not in labels


def test_the_storyguide_reads_a_players_list_but_never_their_arrangement() -> None:
    saga, found = _two()
    handout_arrangement.arrange(
        saga, "ana", Arrange(found[0].key, title="Secret title"), by="ana"
    )

    listed = player_handouts.of_player(saga, 0)  # Ana, on the host's copy

    assert isinstance(listed, commands.Choose)
    assert listed.filters == ()
    assert not any("Secret title" in c.label for c in listed.choices())


def test_a_player_id_no_file_could_be_named_by_is_refused_not_raised() -> None:
    saga, found = _two()
    bad = "../ana"
    assert (
        handout_arrangement.arrange(
            saga, bad, Arrange(found[0].key, pinned=True), by=bad
        )
        == handout_arrangement.NO_FILE
    )
    table = host_table.HostTable(saga, saga.sessions[0], bad)
    assert table.arrangement(bad) == handout_arrangement.NO_FILE


def test_a_seat_reading_its_arrangement_is_limited_too() -> None:
    saga, _found = _two()
    specs = {s.name: s for s in handing.handout_specs(saga.id, clock=lambda: 0.0)}
    seat = SimpleNamespace(player_id="ana", device_id="d")
    read = specs["handout_arrangement"].handler
    replies = [
        read(seat, {"player": "ana"})  # type: ignore[arg-type]
        for _ in range(handing.READS_PER_MINUTE + 1)
    ]
    assert replies[-1].type == "show_refused"


def test_a_damaged_file_reads_as_no_arrangement_and_a_bad_id_names_no_file() -> None:
    saga, _found = _two()
    path = handout_arrangement.path_of(saga.id, "ana")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not json", encoding="utf-8")

    assert handout_arrangement.load(saga.id, "ana").places == []
    with pytest.raises(ValueError):
        handout_arrangement.path_of(saga.id, "../ana")
