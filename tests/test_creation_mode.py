"""In Creation / In Play: the mode, the creation checks'
machinery, and the top-panel switch."""

from __future__ import annotations

import json

import pytest
from support import wait_until
from textual.widgets import Button, Tree

from ars_magica_manager import creation, storage
from ars_magica_manager.models import Character, Covenant, Laboratory, Saga
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, WorkspaceScreen


def _saga() -> Saga:
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Keep")],
        characters=[
            Character(id="mag1", name="Leandro", type="magus", covenant_id="cov1")
        ],
        laboratories=[Laboratory(id="lab1", covenant_id="cov1", name="Tower")],
    )


@pytest.fixture
def failing_check(monkeypatch):
    """A must every character In Creation breaks."""

    def broken(saga, record):
        return [rules.Check("concept", "Has a concept", "warn", "none", "test")]

    for step in rules.CHARACTER_CHECKS:
        monkeypatch.setitem(rules.CHARACTER_CHECKS, step, [])
    monkeypatch.setitem(rules.CHARACTER_CHECKS, "concept", [broken])


def test_new_records_start_in_creation_and_old_saves_load_in_play():
    saga = Saga(id="s", name="S")
    covenant = creation.add_covenant(saga, "Keep")
    character = creation.add_character(saga, "Ann", "companion", covenant.id)
    lab = creation.add_laboratory(saga, "Tower", 0, covenant.id)
    assert covenant.in_creation and character.in_creation and lab.in_creation
    # An older save has no mode: it loads In Play.
    data = json.loads(storage.save_saga(saga).read_text(encoding="utf-8"))
    for key in ("covenants", "characters", "laboratories"):
        for record in data[key]:
            del record["in_creation"]
    loaded = Saga.from_dict(data)
    for record in (*loaded.covenants, *loaded.characters, *loaded.laboratories):
        assert not record.in_creation


def test_checks_run_only_in_creation(failing_check):
    saga = _saga()
    magus = saga.characters[0]
    assert rules.checks(saga, magus) == []
    magus.in_creation = True
    assert [c.label for c in rules.checks(saga, magus)] == ["Has a concept"]
    assert rules.checks(saga, magus, "characteristics") == []


def test_strict_rules_stop_a_broken_must_moving_to_play(failing_check):
    saga = _saga()
    magus = saga.characters[0]
    magus.in_creation = True
    assert rules.can_move_to_play(saga, magus)
    saga.rule_options["strict_creation"] = True
    assert not rules.can_move_to_play(saga, magus)


def test_steps_skip_what_a_record_does_not_go_through():
    saga = _saga()
    companion = Character(id="c", name="C", type="companion")
    magus_steps = [s.key for s in rules.steps_for(saga.characters[0])]
    assert "apprenticeship" in magus_steps and "gauntlet" in magus_steps
    assert "apprenticeship" not in [s.key for s in rules.steps_for(companion)]
    assert [s.key for s in rules.steps_for(saga.covenants[0])][-1] == "finish"


def test_summary_counts_warnings_and_advice():
    def check(status):
        return rules.Check("concept", "x", status, "", "")

    assert rules.summary([check("pass")]) == "all checks pass"
    assert rules.summary([]) == "no checks yet"
    found = [check("warn"), check("warn"), check("advice"), check("pass")]
    assert rules.summary(found) == "2 warnings, 1 advice"


async def _open_character(pilot, app) -> WorkspaceScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def node():
        stack = [tree.root]
        while stack:
            n = stack.pop()
            if n.data is not None and n.data[1:] == ("mag1",):
                return n
            stack.extend(n.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(pilot, lambda: workspace._character_sheet_view is not None)
    return workspace


def _tree_labels(workspace) -> list[str]:
    tree = workspace.query_one("#nav-tree", Tree)
    labels, stack = [], [tree.root]
    while stack:
        n = stack.pop()
        labels.append(str(n.label))
        stack.extend(n.children)
    return labels


async def test_the_switch_asks_then_changes_the_mode_and_the_tree_mark():
    saga = _saga()
    saga.characters[0].in_creation = True
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_character(pilot, app)
        button = workspace.query_one("#btn-mode", Button)
        assert str(button.label) == "In Creation"
        assert "Leandro (magus) (creating)" in _tree_labels(workspace)

        button.press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("n")
        assert await wait_until(pilot, lambda: app.screen is workspace)
        assert storage.load_saga("test_saga").characters[0].in_creation

        button.press()
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: not storage.load_saga("test_saga").characters[0].in_creation
        )
        button = workspace.query_one("#btn-mode", Button)
        assert await wait_until(pilot, lambda: str(button.label) == "In Play")
        assert "Leandro (magus)" in _tree_labels(workspace)

        button.press()  # back to In Creation also asks
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: storage.load_saga("test_saga").characters[0].in_creation
        )


async def test_strict_rules_keep_a_broken_record_in_creation(failing_check):
    saga = _saga()
    saga.characters[0].in_creation = True
    saga.rule_options["strict_creation"] = True
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open_character(pilot, app)
        workspace.query_one("#btn-mode", Button).press()
        await pilot.pause()
        assert app.screen is workspace  # refused, nothing asked
        assert storage.load_saga("test_saga").characters[0].in_creation
