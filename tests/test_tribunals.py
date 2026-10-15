"""Tribunal records: the old Tribunal text moved onto them, making and
deleting one, carrying one through an export, and where both front-ends
show them."""

from __future__ import annotations

import os

import pytest
from support import everything_saga, screen_lines, wait_until
from textual.widgets import Collapsible, TabbedContent, Tree

from ars_magica_manager import (
    storage,
    transfer,
    tribunal_forms,
    tribunal_packages,
    tribunal_sheet,
)
from ars_magica_manager import tribunals as trib
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.models import Covenant, Saga, Tribunal, TribunalDiaryEntry
from ars_magica_manager.tribunal_packages.rhine import gilds as rhine_gilds
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
    assert [row[0] for row in tribunal_sheet.roster_grid(saga, rhine).rows] == [
        "Keep",
        "Fengheld",
        "4 unnamed",
    ]


def test_a_covenant_votes_its_magi_and_its_proxies():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    grid = tribunal_sheet.roster_grid(saga, rhine)
    assert grid.rows[1][:5] == ["Fengheld", "Sketch", "3", "4", "1 held"]
    form = tribunal_forms.roster_ops(saga, rhine).edit(1)
    assert isinstance(form, Form)
    form.apply({"proxies": 0})
    assert rhine.proxies == {}
    assert isinstance(tribunal_forms.roster_ops(saga, rhine).edit(5), Refuse)


def test_the_docket_flags_notice_not_given_and_cases_against_yours():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    assert tribunal_sheet.notice_due(rhine) == "Summer 1227"  # the Rhine's year
    assert tribunal_sheet.season_before(1228, "Spring", 1) == (1227, "Winter")
    grid = tribunal_sheet.cases_grid(saga, rhine)
    assert [row[3] for row in grid.rows] == ["Summer 1227", "not given"]
    rhine.package = "core"
    assert tribunal_sheet.notice_due(rhine) == "Spring 1228"
    assert grid.styles[(0, 0)] == "$text-error"  # against Keep, the troupe's
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, rhine)}
    assert facts["Cases"] == "2 (1 against you)"


def test_withdraw_moves_a_case_to_the_past_rulings():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    step = tribunal_forms.withdraw_case(rhine, 1)
    assert isinstance(step, Confirm)
    step.apply()
    assert [c.title for c in tribunal_sheet.open_cases(rhine)] == ["Fengheld v. Keep"]
    past = tribunal_sheet.past_grid(rhine)
    assert [(row[0], row[3]) for row in past.rows] == [
        ("Gild dues", "withdrawn"),
        ("Oakheart's founding", "granted 1214"),
    ]


def test_treasury_add_chooses_the_kind_then_its_form():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    choose = tribunal_forms.treasury_ops(rhine).add()
    assert isinstance(choose, Choose)
    assert [c.value for c in choose.choices()] == ["vis", "silver", "loan", "fine"]
    form = choose.apply("fine")
    assert isinstance(form, Form)
    labels = [f.label for f in form.fields()]
    assert "From the case" in labels and "Paid" in labels
    form.apply({"who": "Fengheld", "amount": 5, "paid": True})
    assert dict(tribunal_sheet.balance_lines(rhine))["Silver in hand"] == (
        "35 pounds"  # 40, less the loan of 10 still out, and the fine of 5 in
    )


def test_the_diary_lists_newest_first_by_its_own_index():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    rhine.diary.append(TribunalDiaryEntry(1214, "Summer", "The Tribunal of 1214"))
    grid = tribunal_sheet.diary_grid(rhine)
    assert [row[1] for row in grid.rows] == [
        "The Tribunal of 1221",
        "The Tribunal of 1214",
    ]
    assert grid.keys == [0, 1]
    rhine.diary.append(TribunalDiaryEntry(1228, "Summer", "The Tribunal of 1228"))
    assert tribunal_sheet.diary_grid(rhine).keys == [2, 0, 1]


def test_a_package_is_offered_while_its_book_is_in_play():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    saga.books_in_play = []
    assert [p.key for p in tribunal_packages.offered(saga)] == ["core"]
    # The one a Tribunal follows stays on offer, whatever its book.
    assert "rhine" in [p.key for p in tribunal_packages.offered(saga, rhine.package)]
    saga.books_in_play = ["GotF"]
    assert "rhine" in [p.key for p in tribunal_packages.offered(saga)]


def test_the_rhine_adds_gilds_and_a_gild_column():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    roster = tribunal_sheet.roster_grid(saga, rhine)
    assert roster.columns[5] == "Gild"
    assert [row[5] for row in roster.rows] == ["Hermetic", "Hermetic"]
    ops = tribunal_forms.tribunal_ops(saga, rhine)
    form = ops["section-trib-gilds"].add()
    assert isinstance(form, Form)
    labels = [f.label for f in form.fields()]
    assert labels == ["Gild", "Dues", "Keep", "Fengheld"]
    form.apply({"name": "Mercantile", "dues": "", "member_cov_sketch": True})
    assert rhine_gilds(rhine)[-1] == {
        "name": "Mercantile",
        "dues": "",
        "members": ["cov_sketch"],
    }
    assert tribunal_sheet.roster_grid(saga, rhine).rows[1][5] == "Hermetic, Mercantile"


def test_switching_customs_hides_the_old_ones_and_keeps_them():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    tribunal_forms.edit_tribunal_form(saga, rhine).apply({"package": "core"})
    assert "Gild" not in tribunal_sheet.roster_grid(saga, rhine).columns
    assert "section-trib-gilds" not in tribunal_forms.tribunal_ops(saga, rhine)
    storage.save_saga(saga)
    again = storage.load_saga(saga.id).tribunals[0]
    assert again.package_data["rhine"]["gilds"][0]["name"] == "Hermetic"
    again.package = "rhine"
    assert tribunal_sheet.roster_grid(saga, again).rows[0][5] == "Hermetic"


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


async def test_the_docket_keys_act_on_the_chosen_case():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        tree = workspace.query_one("#nav-tree", Tree)
        node = next(
            n for n in _walk(tree.root) if n.data == (NodeKind.TRIBUNAL, "rhine")
        )
        tree.select_node(node)
        assert await wait_until(
            pilot, lambda: workspace._tribunal_sheet_view is not None
        )
        view = workspace._tribunal_sheet_view
        view.query_one(TabbedContent).active = "tab-trib-docket"
        assert await wait_until(pilot, lambda: bool(view.query("#trib-cases")))
        view.query_one("#section-trib-cases", Collapsible).focus_section()
        assert await wait_until(
            pilot, lambda: workspace._active_section() == "section-trib-cases"
        )
        await pilot.press("down")
        assert await wait_until(pilot, lambda: "m Withdraw" in screen_lines(app)[-1])
        await pilot.press("m")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [c.status for c in storage.load_saga("test_saga").tribunals[0].cases]
                == ["open", "withdrawn", "decided"]
            ),
        )
        assert await wait_until(
            pilot,
            lambda: "Gild dues" in str(view.query_one("#trib-past")._rows),
        )
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        assert "Fengheld v. Keep" in str(
            app.screen.query_one("#confirm-message").render()
        )


async def test_switching_customs_redraws_the_sheets_tabs():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        tree = workspace.query_one("#nav-tree", Tree)
        node = next(
            n for n in _walk(tree.root) if n.data == (NodeKind.TRIBUNAL, "rhine")
        )
        tree.select_node(node)
        assert await wait_until(
            pilot, lambda: workspace._tribunal_sheet_view is not None
        )
        assert workspace._tribunal_sheet_view.query("#tab-trib-gilds")
        workspace._core_verb("section-trib-info", "edit")
        assert await wait_until(pilot, lambda: bool(app.screen.query("#fld-package")))
        app.screen.query_one("#fld-package").value = "core"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._tribunal_sheet_view) is not None
                and view.package.key == "core"
                and not view.query("#tab-trib-gilds")
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
    assert page.chapters() == [
        "Roster",
        "Docket",
        "Peripheral Code",
        "Treasury",
        "Gilds",
        "Diary",
    ]
    saga_page = SagaPage(saga, PALETTES[0], lambda _id: None)
    titles = [label.text() for label in saga_page.findChildren(QLabel)]
    assert any("Tribunals (1)" in title for title in titles)
