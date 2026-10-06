"""Players and signing in (STORY-1403)."""

from __future__ import annotations

from dataclasses import asdict

import pytest
from support import wait_until
from textual.widgets import Button, Input, ListView, Static, Tree

from ars_magica_manager import players as pl
from ars_magica_manager import storage
from ars_magica_manager.app import ArsMagicaManagerApp
from ars_magica_manager.models import Saga
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
