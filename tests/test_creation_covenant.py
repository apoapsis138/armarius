"""Covenant and laboratory creation (STORY-1312, 1313)."""

from __future__ import annotations

from ars_magica_manager.models import (
    Ability,
    Book,
    Character,
    Covenant,
    LabCharacteristics,
    Laboratory,
    Possession,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation as rules
from ars_magica_manager.rules import creation_covenant as cov


def _saga() -> Saga:
    covenant = Covenant(
        id="cov1", saga_id="s", name="Keep", in_creation=True, year_founded=1215
    )
    return Saga(
        id="s",
        name="S",
        current_year=1220,
        covenants=[covenant],
        characters=[
            Character(id="m1", name="A", type="magus", covenant_id="cov1"),
            Character(id="m2", name="B", type="magus", covenant_id="cov1"),
        ],
    )


def _found(saga, record, step):
    return {c.label: (c.status, c.detail) for c in rules.checks(saga, record, step)}


def test_a_power_level_is_chosen_and_the_covenant_is_old_enough():
    saga = _saga()
    covenant = saga.covenants[0]
    assert _found(saga, covenant, "power")["A Power Level is chosen"] == (
        "warn",
        "none",
    )
    covenant.power_level = "Medium"
    found = _found(saga, covenant, "power")
    assert found["Medium: founded at least 10 years ago"] == ("warn", "5 years")
    covenant.power_level = "Low"
    assert "Low: founded at least 0 years ago" not in _found(saga, covenant, "power")


def test_build_points_price_the_library_vis_items_and_labs():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.power_level = "Low"
    saga.books.append(
        Book(
            id="b1",
            name="Of Fire",
            type="Art Summa",
            art="Ignem",
            level=12,
            quality=10,
            owner_kind="covenant",
            owner_id="cov1",
        )
    )
    covenant.possessions = [
        Possession(id="p1", kind="vis_source", name="Spring", art="Aquam", pawns=4),
        Possession(id="p2", kind="vis_store", name="Chest", art="Vim", pawns=12),
    ]
    # Three starting labs for two magi: one spare; one is Size +2.
    saga.laboratories = [
        Laboratory(id=f"l{i}", covenant_id="cov1", name=f"L{i}", starting=True)
        for i in range(3)
    ]
    saga.laboratories[0].characteristics = LabCharacteristics(size=2)
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Art Summa: Of Fire"] == 22
    assert costs["Vis source: Spring (4 a year)"] == 20
    assert costs["Vis stock: Chest (12 pawns)"] == 3
    assert costs["Laboratory: L0"] == 40
    assert costs["Spare laboratories (1)"] == 50
    assert cov.spent(saga, covenant) == 135
    found = _found(saga, covenant, "build_points")
    assert found["Build Points set within Low's 0-300"] == ("warn", "not set")
    covenant.build_points_budget = 120
    found = _found(saga, covenant, "build_points")
    assert found["Build Points set within Low's 0-300"] == ("pass", "120")
    assert found["Resources bought within the Build Points"] == (
        "warn",
        "135 of 120, 15 too many",
    )
    covenant.build_points_budget = 200
    found = _found(saga, covenant, "build_points")
    assert found["Build Points spent"] == ("advice", "65 unspent")
    saga.laboratories = saga.laboratories[:1]  # one lab for two magi
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Magi without a laboratory (1)"] == -50


def test_texts_above_the_power_levels_cap_and_boons_must_balance():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.power_level = "Low"
    saga.books.append(
        Book(
            id="b2",
            name="Pilum",
            type="Lab Text",
            spell_id="spell_pilum_of_fire",
            owner_kind="covenant",
            owner_id="cov1",
            level=30,
        )
    )
    saga.books[-1].spell_id = None  # the book's own level counts
    found = _found(saga, covenant, "build_points")
    assert found["No text or effect above level 25"] == ("warn", "Pilum (30)")
    covenant.boons_hooks = [VirtueFlawInstance("covbh_boon_minor_edifice")]
    found = _found(saga, covenant, "boons_hooks")
    assert found["Boons balance Hooks"] == ("warn", "1 Boon, 0 Hook points")


def test_a_starting_lab_needs_a_builder_and_room_for_its_virtues():
    saga = _saga()
    builder = saga.characters[0]
    builder.abilities.append(Ability("Magic Theory", "Arcane", 15))  # 2
    lab = Laboratory(
        id="l1",
        covenant_id="cov1",
        name="Tower",
        owner_id="m1",
        in_creation=True,
        starting=True,
        characteristics=LabCharacteristics(size=1),
    )
    saga.laboratories.append(lab)
    found = _found(saga, lab, "setup")
    assert found["Its builder has Magic Theory 3"] == ("warn", "A: 2")
    assert found["Virtues less Flaws within Size + Refinement"] == (
        "pass",
        "room for 1 more (limit 1)",
    )
    assert found["A starting lab's Build Points go to its covenant"] == (
        "pass",
        "20 (Size x 20, Virtues)",
    )


async def _open(pilot, app, node_data, attr):
    from support import wait_until
    from textual.widgets import Button, Tree

    from ars_magica_manager.screens import WorkspaceScreen
    from ars_magica_manager.screens.creation_worksheet import CreationWorksheetScreen

    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def node():
        stack = [tree.root]
        while stack:
            n = stack.pop()
            if n.data == node_data:
                return n
            stack.extend(n.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(pilot, lambda: getattr(workspace, attr) is not None)
    workspace.query_one("#btn-worksheet", Button).press()
    assert await wait_until(
        pilot, lambda: isinstance(app.screen, CreationWorksheetScreen)
    )
    await pilot.pause()
    return app.screen


async def test_the_covenant_worksheet_prices_build_points():
    from support import wait_until
    from textual.widgets import OptionList, Static

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens.workspace.base import NodeKind

    saga = _saga()
    saga.id = "test_saga"
    saga.covenants[0].power_level = "Low"
    saga.covenants[0].build_points_budget = 300
    saga.covenants[0].possessions = [
        Possession(id="p1", kind="vis_source", name="Spring", art="Aquam", pawns=4)
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open(
            pilot, app, (NodeKind.COVENANT, "cov1"), "_covenant_sheet_view"
        )
        steps = screen.query_one("#ws-steps", OptionList)
        assert steps.option_count == 4
        steps.highlighted = 1
        assert await wait_until(pilot, lambda: screen.step == "build_points")
        assert await wait_until(
            pilot,
            lambda: (
                "Build Points spent: -80 of 300"
                in str(screen.query_one("#ws-budget", Static).render())
            ),
        )
        text = str(screen.query_one("#ws-budget", Static).render())
        assert "Vis source: Spring (4 a year): 20" in text
        assert "Magi without a laboratory (2): -100" in text


async def test_the_laboratory_worksheet_toggles_starting():
    from support import wait_until
    from textual.widgets import Static

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens.workspace.base import NodeKind

    saga = _saga()
    saga.id = "test_saga"
    saga.laboratories.append(
        Laboratory(id="l1", covenant_id="cov1", name="Tower", in_creation=True)
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open(
            pilot, app, (NodeKind.LABORATORY, "l1"), "_laboratory_sheet_view"
        )
        assert await wait_until(
            pilot,
            lambda: (
                "Starting laboratory: no"
                in str(screen.query_one("#ws-budget", Static).render())
            ),
        )

        def button():
            return next(
                (
                    b
                    for b in screen.query("#ws-actions Button")
                    if str(b.label) == "Starting lab: yes/no"
                ),
                None,
            )

        assert await wait_until(pilot, lambda: button() is not None)
        button().press()
        assert await wait_until(
            pilot, lambda: storage.load_saga("test_saga").laboratories[0].starting
        )


def test_bought_specialists_and_teachers_cost_build_points():
    from ars_magica_manager.models import Inhabitant

    saga = _saga()
    covenant = saga.covenants[0]
    covenant.inhabitants = [
        Inhabitant(
            id="i1",
            kind="specialist",
            name="Odo",
            linked_ability="Artes Liberales",
            specialist_score=5,
            teacher_communication=2,
            teacher_teaching=4,
        ),
        Inhabitant(
            id="i2",
            kind="specialist",
            name="Hilda",
            linked_ability="Craft: Smith",
            specialist_score=6,
        ),
        # Not bought: a grog assigned as a specialist costs nothing.
        Inhabitant(id="i3", kind="specialist", name="Wat", character_id="g1"),
    ]
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Teacher: Odo, Artes Liberales"] == 11
    assert costs["Specialist: Hilda, Craft: Smith"] == 6
    assert not any("Wat" in label for label in costs)
