"""Players and signing in (STORY-1403)."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import everything_saga, wait_until
from textual.widgets import Button, Input, ListView, Select, Static, Tree

from ars_magica_manager import players as pl
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Book, Character, Player, Saga
from ars_magica_manager.screens import SagaPickerScreen, WorkspaceScreen
from ars_magica_manager.screens.fields import FieldsDialog
from ars_magica_manager.screens.workspace.base import NodeKind


def _saga_with(*players: tuple[str, str, str]) -> Saga:
    saga = Saga(id="dammerstein", name="Dammerstein", storyguide="Hedda")
    for name, role, passcode in players:
        pl.add(saga, {"name": name, "role": role, "passcode": passcode})
    return saga


def test_a_passcode_is_kept_only_as_a_salted_hash():
    saga = _saga_with(("Ana", pl.PLAYER, "rosemary"), ("Ben", pl.PLAYER, "rosemary"))
    ana, ben = saga.players
    assert "rosemary" not in ana.passcode_hash
    assert ana.passcode_hash.startswith("scrypt$")
    # Same passcode, different salt: the stored hashes differ.
    assert ana.passcode_hash != ben.passcode_hash
    assert pl.passcode_matches(ana, "rosemary")
    assert not pl.passcode_matches(ana, "Rosemary")
    assert not pl.passcode_matches(ana, "")


def test_signing_in_takes_the_name_in_any_case_and_the_exact_passcode():
    saga = _saga_with(("Ana", pl.PLAYER, "rosemary"))
    assert pl.sign_in(saga, "  ana ", "rosemary") is saga.players[0]
    assert pl.sign_in(saga, "Ana", "thyme") is None
    assert pl.sign_in(saga, "Cid", "rosemary") is None


def test_a_damaged_hash_never_signs_in():
    saga = _saga_with(("Ana", pl.PLAYER, "rosemary"))
    for broken in ("", "rosemary", "md5$00$00", "scrypt$zz$00"):
        saga.players[0].passcode_hash = broken
        assert pl.sign_in(saga, "Ana", "rosemary") is None


def test_no_two_players_share_a_name():
    saga = _saga_with(("Ana", pl.PLAYER, "rosemary"))
    ana = saga.players[0]
    assert pl.name_problem(saga, "ANA", None) is not None
    assert pl.name_problem(saga, "Ana", ana) is None  # editing Ana herself
    assert pl.name_problem(saga, "Ben", None) is None


def test_editing_a_player_keeps_the_passcode_unless_a_new_one_is_given():
    saga = _saga_with(("Ana", pl.PLAYER, "rosemary"))
    ana = saga.players[0]
    pl.update(ana, {"name": "Anna", "role": pl.STORYGUIDE, "passcode": ""})
    assert (ana.name, ana.role) == ("Anna", pl.STORYGUIDE)
    assert pl.passcode_matches(ana, "rosemary")
    pl.update(ana, {"name": "Anna", "role": pl.STORYGUIDE, "passcode": "thyme"})
    assert pl.passcode_matches(ana, "thyme")
    assert not pl.passcode_matches(ana, "rosemary")


def test_players_are_saved_with_the_saga_and_older_saves_have_none():
    saga = _saga_with(("Ana", pl.STORYGUIDE, "rosemary"))
    storage.save_saga(saga)
    loaded = storage.load_saga(saga.id)
    assert [(p.id, p.name, p.role) for p in loaded.players] == [
        ("ana", "Ana", pl.STORYGUIDE)
    ]
    assert pl.sign_in(loaded, "Ana", "rosemary") is not None

    old = asdict(Saga(id="old", name="Old"))
    del old["players"]
    assert Saga.from_dict(old).players == []


# -- the app: a browser copy signs in, the storyguide's own window doesn't --


@pytest.fixture
def in_a_browser(monkeypatch):
    """Run the app as a browser copy of a hosted app (textual-serve)."""
    monkeypatch.setattr(ArsMagicaManagerApp, "is_web", property(lambda self: True))


async def _open_first_saga(pilot, app) -> None:
    picker = app.screen
    assert isinstance(picker, SagaPickerScreen)
    list_view = picker.query_one("#saga-list", ListView)
    assert await wait_until(pilot, lambda: list_view.index == 0)
    list_view.focus()
    await pilot.press("enter")


async def _sign_in(pilot, app, name: str, passcode: str) -> FieldsDialog:
    assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
    dialog = app.screen
    dialog.query_one("#fld-name", Input).value = name
    dialog.query_one("#fld-passcode", Input).value = passcode
    dialog.query_one("#btn-save", Button).press()
    await pilot.pause()
    return dialog


async def test_the_storyguides_own_window_opens_a_saga_without_signing_in():
    storage.save_saga(_saga_with(("Ana", pl.PLAYER, "rosemary")))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        assert app.screen.check_action("create_saga", ()) is True
        await _open_first_saga(pilot, app)
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert app.player is None
        tree = app.screen.query_one(Tree)
        kinds = [n.data[0] for n in tree.root.children]
        assert NodeKind.PLAYERS in kinds


async def test_a_browser_copy_signs_in_before_opening_a_saga(in_a_browser):
    storage.save_saga(
        _saga_with(("Ana", pl.PLAYER, "rosemary"), ("Hedda", pl.STORYGUIDE, "sage"))
    )
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        picker = app.screen
        # Only the storyguide's own window makes or deletes sagas.
        assert picker.check_action("create_saga", ()) is False
        assert picker.check_action("delete_saga", ()) is False
        assert "sign in" in str(picker.query_one("#picker-hint", Static).render())

        await _open_first_saga(pilot, app)
        dialog = await _sign_in(pilot, app, "Ana", "wrong")
        assert app.screen is dialog  # refused: still asking
        assert "don't match" in str(dialog.query_one("#fields-error", Static).render())

        await _sign_in(pilot, app, "ana", "rosemary")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        assert app.player is not None and app.player.name == "Ana"
        assert app.screen.sub_title.endswith("| Ana")
        # A player doesn't see who else can sign in.
        tree = app.screen.query_one(Tree)
        assert NodeKind.PLAYERS not in [n.data[0] for n in tree.root.children]

        # Back to the list signs out.
        app.pop_screen()
        assert await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        assert await wait_until(pilot, lambda: app.player is None)

        # A storyguide signed in from a browser keeps the saga's players.
        await _open_first_saga(pilot, app)
        await _sign_in(pilot, app, "Hedda", "sage")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        tree = app.screen.query_one(Tree)
        assert NodeKind.PLAYERS in [n.data[0] for n in tree.root.children]


async def test_a_saga_with_no_players_cant_be_opened_from_a_browser(in_a_browser):
    storage.save_saga(Saga(id="empty", name="Empty"))
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await _open_first_saga(pilot, app)
        await pilot.pause()
        assert isinstance(app.screen, SagaPickerScreen)
        assert app.player is None


# -- who may change what (STORY-1404) --


def _troupe() -> tuple[Saga, Player, Player]:
    """everything_saga() with Ana playing Leandro (mag1, who owns lab1 and
    the familiar fam1) and Hedda as a storyguide."""
    saga = everything_saga()
    ana = pl.add(saga, {"name": "Ana", "role": pl.PLAYER, "passcode": "rosemary"})
    hedda = pl.add(saga, {"name": "Hedda", "role": pl.STORYGUIDE, "passcode": "sage"})
    saga.character("mag1").background.player_id = ana.id
    return saga, ana, hedda


def test_a_player_may_change_their_characters_and_what_belongs_to_them():
    saga, ana, hedda = _troupe()
    leandro, alys = saga.character("mag1"), saga.character("comp1")
    lab, familiar, covenant = (
        saga.laboratory("lab1"),
        saga.familiars[0],
        saga.covenants[0],
    )
    assert pl.characters_of(saga, ana) == [leandro]
    assert pl.may_change(saga, ana, leandro)
    assert pl.may_change(saga, ana, lab)
    assert pl.may_change(saga, ana, familiar)
    assert not pl.may_change(saga, ana, alys)
    assert not pl.may_change(saga, ana, covenant)
    assert not pl.may_change(saga, ana, None)  # the saga itself
    ana.covenant_rights = True
    assert pl.may_change(saga, ana, covenant)
    for anyone_in_charge in (hedda, None):  # a storyguide, or the own window
        assert pl.may_change(saga, anyone_in_charge, alys)
        assert pl.may_change(saga, anyone_in_charge, None)


def test_removing_a_player_frees_their_characters():
    saga, ana, _ = _troupe()
    pl.remove(saga, ana)
    assert saga.character("mag1").background.player_id is None


def test_the_save_guard_takes_back_what_a_player_may_not_change():
    saga, ana, hedda = _troupe()
    before = asdict(saga)
    saga.character("mag1").name = "Leandro the Wise"  # hers
    saga.character("comp1").name = "Alys the Bold"  # not hers
    saga.current_year += 1  # the saga's
    saga.characters.append(Character(id="new1", name="Hugo", type="grog"))
    saga.books.append(Book(id="bk-new", name="Her notes", type="Tractatus"))
    after = asdict(saga)

    kept, refused = pl.guard_changes(ana, before, after)
    names = {c["id"]: c["name"] for c in kept["characters"]}
    assert names == {"mag1": "Leandro the Wise", "comp1": "Alys"}
    assert kept["current_year"] == before["current_year"]
    assert "bk-new" in {b["id"] for b in kept["books"]}  # books are shared
    assert sorted(refused) == ["characters[comp1]", "characters[new1]", "current_year"]

    # Deleting someone else's character is taken back too.
    after = dict(before)
    after["characters"] = [c for c in before["characters"] if c["id"] != "comp1"]
    kept, refused = pl.guard_changes(ana, before, after)
    assert "comp1" in {c["id"] for c in kept["characters"]}
    assert refused == ["characters[comp1]"]

    assert pl.guard_changes(hedda, before, after) == (after, [])
    assert pl.guard_changes(None, before, after) == (after, [])


async def _workspace_as(app, pilot, saga: Saga, player: Player | None):
    storage.save_saga(saga)
    app.player = player
    await app.push_screen(WorkspaceScreen(storage.load_saga(saga.id)))
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    return app.screen


async def _show(pilot, workspace, data: tuple) -> None:
    tree = workspace.query_one("#nav-tree", Tree)

    def node():
        stack = [tree.root]
        while stack:
            candidate = stack.pop()
            if candidate.data == data:
                return candidate
            stack.extend(candidate.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(pilot, lambda: workspace.selected_kind == data[0])
    await pilot.pause()


_CHANGES = ("add", "edit", "delete", "new", "advance_season")


async def test_a_signed_in_player_changes_only_their_own(in_a_browser):
    saga, ana, _ = _troupe()
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _workspace_as(app, pilot, saga, ana)

        await _show(pilot, ws, ("character", "comp1"))  # Alys: not hers
        ws.query_one("#section-char-info").focus_section()
        await pilot.pause()
        assert [ws.check_action(a, ()) for a in _CHANGES] == [False] * 5
        assert ws._available("export_record")  # reading is fine

        await _show(pilot, ws, ("character", "mag1"))  # Leandro: hers
        ws.query_one("#section-char-info").focus_section()
        await pilot.pause()
        assert ws.check_action("edit", ()) is not False
        assert ws.check_action("new", ()) is False
        assert ws.check_action("advance_season", ()) is False
        assert not ws._available("move_vis")

        await _show(pilot, ws, ("saga",))
        assert ws.check_action("edit", ()) is False
        assert not ws._available("import_data")

        # A save that slipped past the screens still can't change Alys.
        ws.saga.character("comp1").name = "Alys the Bold"
        ws.saga.character("mag1").name = "Leandro the Wise"
        storage.save_saga(ws.saga)
        on_disk = storage.load_saga(saga.id)
        assert on_disk.character("comp1").name == "Alys"
        assert on_disk.character("mag1").name == "Leandro the Wise"

    assert storage.guard is None  # signed out with the saga closed


async def test_only_the_storyguide_says_who_plays_a_character(in_a_browser):
    saga, ana, hedda = _troupe()
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        ws = await _workspace_as(app, pilot, saga, hedda)
        await _show(pilot, ws, ("character", "comp1"))
        ws._edit_biographical_detail()
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-player_id")))
        dialog = app.screen
        played_by = dialog.query_one("#fld-player_id", Select)
        played_by.value = ana.id
        dialog.query_one("#btn-save", Button).press()
        assert await wait_until(pilot, lambda: app.screen is ws)
        assert (
            storage.load_saga(saga.id).character("comp1").background.player_id == ana.id
        )
