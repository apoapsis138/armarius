"""The Region's neighbours: the kinds and the books they need, making,
editing and deleting one, how the Region shows them, and both
front-ends' pages."""

from __future__ import annotations

import os

import pytest
from support import everything_saga, wait_until
from textual.widgets import Tree

from ars_magica_manager import (
    neighbour_forms,
    neighbours,
    region_sheet,
    storage,
)
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form
from ars_magica_manager.models import Attitude, Neighbour, Reason, Saga
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen


def test_new_neighbour_offers_the_kinds_whose_book_is_in_play():
    saga = everything_saga()
    saga.books_in_play = ["LoM"]
    command = neighbour_forms.new_neighbour(saga)
    assert isinstance(command, Choose)
    assert [c.value for c in command.choices()] == ["lord", "faction", "threat"]
    assert command.others is not None
    shown = [c.value for c in command.others()]
    assert shown == ["town", "church", "university"]
    form = command.apply("lord")
    assert isinstance(form, Form)
    assert form.fields()[0].label == "Name"
    assert [f.key for f in form.fields()].count("kind") == 0
    form.apply({"name": "Wolfram", "answers_to": "gottfried", "realm": None})
    made = saga.neighbours[-1]
    assert (made.kind, made.answers_to, made.realm) == ("lord", "gottfried", "")


def test_a_group_with_one_kind_in_play_opens_its_form_at_once():
    saga = everything_saga()
    assert isinstance(neighbour_forms.new_neighbour(saga, "factions"), Form)
    assert isinstance(neighbour_forms.new_neighbour(saga, "lords"), Choose)
    saga.books_in_play = []
    assert [g.key for g in neighbours.groups_shown(saga)] == [
        "lords",  # Gottfried is in it, though Lords of Men isn't in play
        "church",
        "factions",
        "threats",
    ]


def test_deleting_a_liege_frees_those_who_answered_to_it():
    saga = everything_saga()
    cologne = saga.neighbour("cologne")
    assert cologne is not None
    assert neighbours.deletion_consequences(saga, cologne) == [
        "Gottfried of Arnsberg will answer to no one; nothing else changes."
    ]
    ops = neighbour_forms.region_ops(saga)["section-region-church"]
    assert ops.remove is not None
    confirm = ops.remove(0)
    assert isinstance(confirm, Confirm)
    confirm.apply()
    assert saga.neighbour("cologne") is None
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None and gottfried.answers_to is None


def test_the_region_counts_the_warm_and_the_wary():
    saga = everything_saga()
    facts = {f.label: f.value for f in region_sheet.facts(saga)}
    assert facts["Neighbours"] == "3, 1 warm, 1 wary"
    assert facts["Player covenant"] == "Keep"
    assert facts["Next Tribunal"] == "Summer 1228"
    grid = region_sheet.group_grid(saga, "lords")
    assert grid.rows[0][3] == "◉ −1 Wary"
    assert grid.styles[(0, 3)] == "$text-warning"
    gottfried = saga.neighbour("gottfried")
    text = region_sheet.details_text(saga, gottfried)
    assert "Started at 0; −1 The mill undercuts his own" in text
    assert "Safe passage for the wool carts" in text


def test_a_neighbour_keeps_its_standing_through_a_save():
    saga = Saga(id="n", name="N")
    saga.neighbours.append(
        Neighbour(
            "soest",
            "Soest",
            kind="town",
            attitudes=[Attitude("cov1", 1, [Reason("Bought the fleece", 1)])],
            details={"population": 5000},
        )
    )
    storage.save_saga(saga)
    again = storage.load_saga("n").neighbours[0]
    assert again.attitudes[0].reasons[0].what == "Bought the fleece"
    assert again.details == {"population": 5000}
    assert neighbours.kind_of(again).name == "Town"
    again.kind = "gone"
    assert neighbours.kind_of(again).key == "faction"


async def test_the_tree_lists_neighbours_and_new_neighbour_opens_the_new_one():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#saga-list").focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        region = tree.root.children[1]
        lords = next(
            n for n in region.children if n.data == (NodeKind.NEIGHBOUR_GROUP, "lords")
        )
        assert [n.data for n in lords.children] == [(NodeKind.NEIGHBOUR, "gottfried")]
        workspace.saga.books_in_play = []  # only factions and threats
        workspace.action_create_neighbour()
        await pilot.pause()
        await pilot.press("enter")  # the first kind offered: Faction
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-name")))
        app.screen.query_one("#fld-name").value = "The Wool Gild"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._neighbour_sheet_view) is not None
                and view.neighbour.name == "The Wool Gild"
            ),
        )


def test_the_desktop_lists_neighbours_and_opens_one():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    from ars_magica_manager.gui.pages import SagaPage
    from ars_magica_manager.gui.region import NeighbourPage
    from ars_magica_manager.gui.themes import PALETTES

    QApplication.instance() or QApplication([])
    saga = everything_saga()
    opened: list[str] = []
    saga_page = SagaPage(
        saga, PALETTES[0], lambda _id: None, open_neighbour=opened.append
    )
    titles = [label.text() for label in saga_page.findChildren(QLabel)]
    assert any("Lords and Towns (1)" in title for title in titles)
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    page = NeighbourPage(saga, gottfried, PALETTES[0])
    assert page.chapters() == ["Standing"]
    words = [label.text() for label in page.findChildren(QLabel)]
    assert any("Archbishop of Cologne" in w for w in words)
