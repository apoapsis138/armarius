"""Tribunal records: the old Tribunal text moved onto them, making and
deleting one, carrying one through an export, and where both front-ends
show them."""

from __future__ import annotations

import os

import pytest
from support import everything_saga, wait_until
from textual.widgets import Tree

from ars_magica_manager import storage, transfer, tribunal_forms, tribunal_sheet
from ars_magica_manager import tribunals as trib
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Form
from ars_magica_manager.models import Covenant, Saga, Tribunal
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, WorkspaceScreen


def _old_save() -> dict:
    covenant = {"saga_id": "s"}
    return {
        "id": "s",
        "name": "S",
        "covenants": [
            {**covenant, "id": "a", "name": "Arnhaven", "tribunal": "Rhine"},
            {**covenant, "id": "b", "name": "Fengheld", "tribunal": " rhine "},
            {**covenant, "id": "c", "name": "Crintera", "tribunal": "Normandy"},
            {**covenant, "id": "d", "name": "Oakheart", "tribunal": ""},
        ],
    }


def test_each_typed_tribunal_name_becomes_one_tribunal():
    saga = Saga.from_dict(_old_save())
    assert [(t.id, t.name, t.package) for t in saga.tribunals] == [
        ("rhine", "Rhine", "core"),
        ("normandy", "Normandy", "core"),
    ]
    assert [c.tribunal_id for c in saga.covenants] == [
        "rhine",
        "rhine",
        "normandy",
        None,
    ]


def test_a_typed_name_joins_a_tribunal_already_saved():
    data = _old_save()
    data["tribunals"] = [{"id": "rhenish", "name": "RHINE", "meets_every": 5}]
    saga = Saga.from_dict(data)
    assert [t.id for t in saga.tribunals] == ["rhenish", "normandy"]
    assert saga.covenants[0].tribunal_id == "rhenish"
    assert saga.tribunals[0].meets_every == 5


def test_a_migrated_saga_saves_and_loads_unchanged():
    saga = Saga.from_dict(_old_save())
    storage.save_saga(saga)
    again = storage.load_saga("s")
    assert [t.name for t in again.tribunals] == ["Rhine", "Normandy"]
    assert [c.tribunal_id for c in again.covenants] == [
        c.tribunal_id for c in saga.covenants
    ]


def test_a_tribunal_reads_as_one_in_a_sentence():
    assert trib.title(Tribunal("r", "Rhine")) == "Rhine Tribunal"
    assert trib.title(Tribunal("r", "The Rhine Tribunal")) == "The Rhine Tribunal"


def test_new_tribunal_adds_one_and_edit_changes_it():
    saga = Saga(id="s", name="S")
    form = tribunal_forms.new_tribunal_form(saga)
    form.apply({"name": "Rhine", "meets_every": 7, "next_year": 1228})
    rhine = saga.tribunals[0]
    assert (rhine.id, rhine.next_year, rhine.next_season) == ("rhine", 1228, "Summer")
    assert tribunal_forms.tribunal_problem({"meets_every": 0}) is not None
    assert tribunal_forms.tribunal_problem({"magi_total": -1}) is not None
    edit = tribunal_forms.edit_tribunal_form(saga, rhine)
    assert isinstance(edit, Form)
    edit.apply({"meeting_place": "Durenmar"})
    assert tribunal_sheet.next_meeting(rhine) == "Summer 1228, at Durenmar"


def test_deleting_a_tribunal_names_and_frees_its_covenants():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    assert trib.deletion_consequences(saga, rhine) == [
        "Keep, Fengheld will belong to no Tribunal; nothing else about them changes."
    ]
    trib.delete(saga, rhine)
    assert saga.tribunals == []
    assert {c.tribunal_id for c in saga.covenants} == {None}


def test_the_sheet_counts_the_covenants_and_the_troupes_votes():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    rhine.covenants_total = 6
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, rhine)}
    assert facts["Covenants"] == "2 recorded of 6"
    assert facts["Praeco"] == "Severinus"
    assert [row[0] for row in tribunal_sheet.roster_rows(saga, rhine)] == [
        "Keep",
        "Fengheld",
    ]


def _export(saga: Saga) -> dict:
    return transfer.export_data(saga, saga.covenants[0])


def test_an_exported_covenant_joins_the_tribunal_of_its_name():
    source = everything_saga()
    target = Saga(id="t", name="T", tribunals=[Tribunal("rhenish", "rhine")])
    plan = transfer.plan_import(target, _export(source))
    assert plan.tribunals == []
    assert plan.covenants[0].tribunal_id == "rhenish"
    assert "Tribunal rhine (matched by name)" in plan.matched


def test_an_exported_covenant_brings_its_tribunal_where_there_is_none():
    source = everything_saga()
    target = Saga(id="t", name="T")
    plan = transfer.plan_import(target, _export(source))
    transfer.apply(target, plan)
    assert [t.name for t in target.tribunals] == ["Rhine"]
    assert target.covenants[0].tribunal_id == target.tribunals[0].id
    assert "Tribunal: Rhine" in transfer.preview(plan)


# -- the terminal --


def _walk(node):
    yield node
    for child in node.children:
        yield from _walk(child)


async def _workspace(pilot, app) -> WorkspaceScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    return app.screen


async def test_the_region_holds_each_tribunal_and_the_covenants_not_played():
    saga = everything_saga()
    saga.covenants.append(
        Covenant(id="lone", saga_id="s", name="Lone", played=False, detail="Line")
    )
    storage.save_saga(saga)
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        tree = workspace.query_one("#nav-tree", Tree)
        top = [n.data for n in tree.root.children]
        assert top[0] == (NodeKind.COVENANT, "cov1")
        assert top[1] == (NodeKind.REGION,)
        region = tree.root.children[1]
        assert [n.data for n in region.children] == [
            (NodeKind.TRIBUNAL, "rhine"),
            (NodeKind.COVENANT, "lone"),
        ]
        assert [n.data for n in region.children[0].children] == [
            (NodeKind.COVENANT, "cov_sketch")
        ]
        assert region.children[1].allow_expand is False  # a line with nothing


async def test_new_tribunal_opens_it_and_d_deletes_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        workspace.action_create_tribunal()
        await pilot.pause()
        app.screen.query_one("#fld-name").value = "Normandy"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._tribunal_sheet_view) is not None
                and view.tribunal.name == "Normandy"
            ),
        )
        workspace.query_one("#nav-tree", Tree).focus()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [t.name for t in storage.load_saga("test_saga").tribunals] == ["Rhine"]
            ),
        )


# -- the desktop --


def test_the_desktop_shows_a_tribunal_and_lists_them_on_the_saga():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    from ars_magica_manager.gui.pages import SagaPage
    from ars_magica_manager.gui.themes import PALETTES
    from ars_magica_manager.gui.tribunal import TribunalPage

    QApplication.instance() or QApplication([])
    saga = everything_saga()
    page = TribunalPage(saga, saga.tribunals[0], PALETTES[0])
    assert page.chapters() == ["Roster"]
    saga_page = SagaPage(saga, PALETTES[0], lambda _id: None)
    titles = [label.text() for label in saga_page.findChildren(QLabel)]
    assert any("Tribunals (1)" in title for title in titles)
