"""Seeing what other copies of a hosted saga do."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from support import everything_saga, screen_lines, wait_until
from textual.widgets import Tree

from ars_magica_manager import players as pl
from ars_magica_manager import presence, storage
from ars_magica_manager.models import Character, Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen
from ars_magica_manager.tui.screens.workspace.base import _tree_node_with_data


@contextmanager
def _other_copy() -> Iterator[None]:
    """Act as another copy of the app: its own memory of the saga, and
    saving as Ana."""
    kept, kept_by = storage._last_seen, storage.saved_by
    storage._last_seen, storage.saved_by = {}, "Ana"
    try:
        yield
    finally:
        storage._last_seen, storage.saved_by = kept, kept_by


def _saga() -> Saga:
    saga = everything_saga()
    pl.add(saga, {"name": "Ana", "role": pl.PLAYER, "passcode": "rosemary"})
    return saga


# -- storage.reload_into --


def test_reloading_updates_the_records_this_copy_holds_in_place():
    storage.save_saga(_saga())
    mine = storage.load_saga("test_saga")
    alys = mine.character("comp1")
    assert storage.reload_into(mine) is None  # nobody else saved

    with _other_copy():
        theirs = storage.load_saga("test_saga")
        theirs.character("comp1").name = "Alys the Bold"
        theirs.characters = [c for c in theirs.characters if c.id != "mag1"]
        theirs.characters.append(Character(id="grog2", name="Hugo", type="grog"))
        storage.save_saga(theirs)

    changed = storage.reload_into(mine)
    assert sorted(changed) == [
        ("characters", "comp1"),
        ("characters", "grog2"),
        ("characters", "mag1"),
    ]
    assert mine.character("comp1") is alys  # the same object, updated
    assert alys.name == "Alys the Bold"
    assert mine.character("mag1") is None
    assert mine.character("grog2").name == "Hugo"
    assert mine.saved_by == "Ana"
    assert storage.reload_into(mine) is None  # now up to date


def test_a_save_after_reloading_keeps_the_other_copys_work():
    storage.save_saga(_saga())
    mine = storage.load_saga("test_saga")
    with _other_copy():
        theirs = storage.load_saga("test_saga")
        theirs.character("comp1").name = "Alys the Bold"
        storage.save_saga(theirs)
    storage.reload_into(mine)
    mine.description = "Winter is coming"
    storage.save_saga(mine)
    on_disk = storage.load_saga("test_saga")
    assert on_disk.character("comp1").name == "Alys the Bold"
    assert on_disk.description == "Winter is coming"
    assert on_disk.saved_by == ""  # the storyguide's own window


# -- presence --


def test_presence_says_who_else_has_a_record_open():
    presence.note("me", "test_saga", "", "characters:mag1")
    presence.note("ana", "test_saga", "Ana", "characters:mag1")
    presence.note("ben", "test_saga", "Ben", "characters:comp1")
    presence.note("cid", "other-saga", "Cid", "characters:mag1")
    assert presence.others_on("me", "test_saga", "characters:mag1") == ["Ana"]
    assert presence.others_on("ana", "test_saga", "characters:mag1") == [
        "The storyguide"
    ]
    assert presence.others_on("me", "test_saga", None) == []

    presence.leave("ana")
    assert presence.others_on("me", "test_saga", "characters:mag1") == []

    # A copy that stopped saying it's there (closed, or crashed) drops out.
    stale = storage.sagas_dir() / ".presence" / "ben.json"
    entry = json.loads(stale.read_text(encoding="utf-8"))
    entry["seen"] = time.time() - presence.FRESH - 1
    stale.write_text(json.dumps(entry), encoding="utf-8")
    assert presence.others_on("me", "test_saga", "characters:comp1") == []


# -- the workspace --


async def _open(pilot, app, data: tuple) -> WorkspaceScreen:
    await app.push_screen(WorkspaceScreen(storage.load_saga("test_saga")))
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    ws = app.screen
    tree = ws.query_one("#nav-tree", Tree)
    tree.select_node(_tree_node_with_data(tree, data))
    assert await wait_until(pilot, lambda: ws.selected_kind == data[0])
    await pilot.pause()
    return ws


async def test_the_open_sheet_shows_another_copys_save_in_place():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _open(pilot, app, ("character", "comp1"))
        view = ws._current_sheet_view()
        with _other_copy():
            theirs = storage.load_saga("test_saga")
            theirs.character("comp1").name = "Alys the Bold"
            storage.save_saga(theirs)

        await ws._shared_tick()
        await pilot.pause()
        assert ws._current_sheet_view() is view  # refreshed, not rebuilt
        assert ws.selected_character.name == "Alys the Bold"
        assert any("Alys the Bold" in line for line in screen_lines(app))
        assert any(
            "Ana changed Alys the Bold; reloaded." in n.message
            for n in app._notifications
        )


async def test_the_saga_is_shown_when_the_open_record_is_deleted_elsewhere():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _open(pilot, app, ("character", "comp1"))
        with _other_copy():
            theirs = storage.load_saga("test_saga")
            theirs.characters = [c for c in theirs.characters if c.id != "comp1"]
            storage.save_saga(theirs)
        await ws._shared_tick()
        assert await wait_until(pilot, lambda: ws.selected_kind == "saga")


async def test_two_people_on_one_record_are_told():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _open(pilot, app, ("character", "mag1"))
        presence.note("ana-tab", "test_saga", "Ana", "characters:mag1")
        await ws._shared_tick()
        await ws._shared_tick()  # said once, not every tick
        await pilot.pause()
        told = [n.message for n in app._notifications if "also on" in n.message]
        assert told == ["Ana is also on Leandro."]
    # Closing the saga drops this copy's presence.
    assert presence.others_on("ana-tab", "test_saga", "characters:mag1") == []


async def test_a_saga_without_players_doesnt_look_for_other_copies():
    saga = everything_saga()
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _open(pilot, app, ("saga",))
        assert ws._session is None


async def test_picking_up_another_copys_save_rebuilds_the_footer_at_most_once():
    from test_performance_guards import _check_rebuilds, _footer

    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _open(pilot, app, ("character", "comp1"))
        await pilot.pause()
        before = _footer(app).rebuilds
        with _other_copy():
            theirs = storage.load_saga("test_saga")
            theirs.character("comp1").name = "Alys the Bold"
            storage.save_saga(theirs)
        await ws._shared_tick()
        await pilot.pause()
        await pilot.pause()
        _check_rebuilds(app, before, "picking up another copy's save")


def test_a_damaged_file_is_reported_and_the_next_save_replaces_it():
    storage.save_saga(_saga())
    mine = storage.load_saga("test_saga")
    storage.saga_path("test_saga").write_text("{ not json", encoding="utf-8")
    with pytest.raises(ValueError, match="can't be read"):
        storage.reload_into(mine)
    assert mine.character("comp1") is not None  # this copy keeps its data
    storage.save_saga(mine)
    assert storage.load_saga("test_saga").character("comp1") is not None
