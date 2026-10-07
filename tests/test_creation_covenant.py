"""Covenant and laboratory creation."""

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
    assert "Magi without a laboratory (1)" not in costs  # B's lab isn't entered


def test_only_magi_said_to_go_without_a_lab_refund():
    """A magus whose lab isn't entered still has the free one; only the
    covenant's magi_without_lab refund 50 each, at creation."""
    saga = _saga()
    covenant = saga.covenants[0]
    saga.characters += [
        Character(id=f"m{i}", name=f"M{i}", type="magus", covenant_id="cov1")
        for i in range(3, 5)
    ]  # four magi, no labs entered: nothing either way
    assert [c for c in cov.costs(saga, covenant) if c.category == "Laboratories"] == []
    covenant.magi_without_lab = 1
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Magi without a laboratory (1)"] == -50
    # Three magi have a free lab: a fourth starting lab is a spare.
    saga.laboratories = [
        Laboratory(id=f"l{i}", covenant_id="cov1", name=f"L{i}", starting=True)
        for i in range(4)
    ]
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Spare laboratories (1)"] == 50
    assert costs["Magi without a laboratory (1)"] == -50
    covenant.magi_without_lab = 9  # no more than the covenant's magi
    assert cov.without_lab(saga, covenant) == 4
    # In play the refund isn't part of the covenant's value.
    labels = [c.label for c in cov.costs(saga, covenant, every_lab=True)]
    assert not any(label.startswith("Magi without") for label in labels)


def test_lab_texts_and_tablets_cost_one_line_per_pool():
    """The Build tab charges each pool once, for its summed levels, and says
    what is unspent; the texts have no line of their own."""
    saga = _saga()
    covenant = saga.covenants[0]
    for i, (kind, level) in enumerate(
        [("Lab Text", 12), ("Lab Text", 20), ("Casting Tablet", 10)]
    ):
        saga.books.append(
            Book(
                id=f"t{i}",
                name=f"Text {i}",
                type=kind,
                level=level,
                owner_kind="covenant",
                owner_id="cov1",
            )
        )
    costs = {c.label: c.points for c in cov.costs(saga, covenant)}
    assert costs["Lab Texts: 32 levels (3 levels unspent)"] == 7
    assert costs["Casting Tablets: 10 levels"] == 4
    assert not any(label.startswith("Lab Text: ") for label in costs)


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
    assert found["Boons cost no more than the Hooks give"] == (
        "warn",
        "1 Boon, 0 Hook points, 1 too many",
    )


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


def _rows(screen) -> list[str]:
    """The worksheet step list's rows as plain text."""
    from support import strip_markup

    from ars_magica_manager.screens import SelectableList

    listing = screen.query_one("#ws-list", SelectableList)
    return [
        " ".join(strip_markup(str(listing.get_option_at_index(i).prompt)).split())
        for i in range(listing.option_count)
    ]


async def _choose(pilot, screen, text: str) -> None:
    from support import strip_markup, wait_until

    from ars_magica_manager.screens import SelectableList

    assert await wait_until(pilot, lambda: any(text in r for r in _rows(screen)))
    listing = screen.query_one("#ws-list", SelectableList)
    listing.focus()
    index = next(
        i
        for i, row in enumerate(screen._rows)
        if not row.heading and text in strip_markup(row.label)
    )
    assert listing.select_data_index(index)
    await pilot.pause()


async def test_the_covenant_worksheet_lists_what_build_points_went_on():
    from support import wait_until
    from textual.widgets import OptionList, Static

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens.fields import FieldsDialog
    from ars_magica_manager.screens.workspace.base import NodeKind

    saga = _saga()
    saga.id = "test_saga"
    saga.covenants[0].power_level = "Low"
    saga.covenants[0].build_points_budget = 300
    saga.covenants[0].magi_without_lab = 2
    saga.covenants[0].possessions = [
        Possession(id="p1", kind="vis_source", name="Spring", art="Aquam", pawns=4)
    ]
    # A book with no level or Quality yet costs nothing, but still shows.
    saga.books.append(
        Book(
            id="b1",
            name="Herbal",
            type="Tractatus",
            owner_kind="covenant",
            owner_id="cov1",
        )
    )
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
                "Build Points: 300, -80 spent, 380 left"
                in str(screen.query_one("#ws-budget", Static).render())
            ),
        )
        rows = _rows(screen)
        assert "Tractatus: Herbal 0 not priced: set its level or Quality" in " ".join(
            rows
        )
        assert any("Vis source: Spring (4 a year) 20" in r for r in rows)
        assert any("Magi without a laboratory (2) -100" in r for r in rows)
        await _choose(pilot, screen, "Herbal")
        assert "Name: Herbal" in str(screen.query_one("#ws-details", Static).render())
        # a adds a book to the covenant's library.
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))
        await pilot.pause()
        assert "Add a Book" in str(app.screen.query_one("#fields-title").render())


async def test_the_covenant_worksheet_lists_boons_and_hooks():
    from support import wait_until
    from textual.widgets import OptionList, Static

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens import ConfirmScreen
    from ars_magica_manager.screens.workspace.base import NodeKind

    saga = _saga()
    saga.id = "test_saga"
    saga.covenants[0].boons_hooks = [
        VirtueFlawInstance("covbh_hook_minor_monster", id="h1")
    ]
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open(
            pilot, app, (NodeKind.COVENANT, "cov1"), "_covenant_sheet_view"
        )
        screen.query_one("#ws-steps", OptionList).highlighted = 2
        assert await wait_until(pilot, lambda: screen.step == "boons_hooks")
        assert await wait_until(pilot, lambda: "Hooks" in _rows(screen))
        assert any(
            r.startswith("○ Monster") and r.endswith(" 1") for r in _rows(screen)
        )
        await _choose(pilot, screen, "Monster")
        details = str(screen.query_one("#ws-details", Static).render())
        assert "Rules:" in details
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: storage.load_saga("test_saga").covenants[0].boons_hooks == [],
        )


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


# -- the Build tab --


def test_the_build_tab_keeps_initial_and_follows_current():
    from ars_magica_manager import covenant_build, creation

    saga = _saga()
    covenant = saga.covenants[0]
    covenant.power_level = "Low"
    covenant.build_points_budget = 200
    covenant.possessions = [
        Possession(id="p1", kind="vis_source", name="Spring", art="Aquam", pawns=4)
    ]
    saga.laboratories = [
        Laboratory(id="l1", covenant_id="cov1", name="L1", starting=True),
        Laboratory(id="l2", covenant_id="cov1", name="L2", starting=True),
    ]
    assert covenant_build.title(saga, covenant) == "Build Points (20 of 200)"
    assert covenant_build.summary(saga, covenant) == "20/200"
    table = covenant_build.table_text(saga, covenant)
    assert "Vis sources                20       20" in table  # the same In Creation
    assert "Storyguide's Build Points: 200" in table

    creation.set_in_creation(saga, covenant, False)
    assert covenant.initial_build_points["Vis sources"] == 20
    covenant.possessions[0].pawns = 6  # found more in play
    saga.laboratories.append(  # a lab built in play counts in the current value
        Laboratory(
            id="l3",
            covenant_id="cov1",
            name="L3",
            characteristics=LabCharacteristics(size=1),
        )
    )
    table = covenant_build.table_text(saga, covenant)
    assert "Vis sources                20       30" in table
    assert "Laboratories                0       70" in table  # Size +1, and spare
    assert "Total                      20      100" in table
    assert covenant_build.title(saga, covenant) == "Build Points (100)"
    assert "Spring (6 a year): 30" in covenant_build.items_text(saga, covenant)

    creation.set_in_creation(saga, covenant, True)  # back: Initial is live again
    assert covenant.initial_build_points is None


def test_a_covenant_in_play_before_tracking_has_no_initial():
    from ars_magica_manager import covenant_build

    saga = _saga()
    covenant = saga.covenants[0]
    covenant.in_creation = False
    table = covenant_build.table_text(saga, covenant)
    assert "Total                       -        0" in table
    assert "Initial wasn't recorded" in table


def test_a_labs_build_points_are_worked_out():
    from ars_magica_manager.laboratories import lab_build_points

    lab = Laboratory(
        id="l1",
        covenant_id="cov1",
        name="Tower",
        characteristics=LabCharacteristics(size=2),
    )
    assert lab_build_points(lab) == 40


async def test_the_laboratory_worksheet_lists_its_virtues_and_flaws():
    from support import wait_until
    from textual.widgets import Static

    from ars_magica_manager import storage
    from ars_magica_manager.app import ArsMagicaManagerApp
    from ars_magica_manager.screens.workspace.base import NodeKind

    saga = _saga()
    saga.id = "test_saga"
    saga.laboratories.append(
        Laboratory(
            id="l1",
            covenant_id="cov1",
            name="Tower",
            in_creation=True,
            virtues_flaws=[VirtueFlawInstance("labvf_superior_construction")],
        )
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        screen = await _open(
            pilot, app, (NodeKind.LABORATORY, "l1"), "_laboratory_sheet_view"
        )
        assert await wait_until(pilot, lambda: "Virtues" in _rows(screen))
        await _choose(pilot, screen, "Superior Construction")
        assert "Superior Construction" in str(
            screen.query_one("#ws-details", Static).render()
        )
