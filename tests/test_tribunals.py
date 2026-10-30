"""Tribunal records: the old Tribunal text moved onto them, making and
deleting one, carrying one through an export, and where both front-ends
show them."""

from __future__ import annotations

import os

import pytest
from support import everything_saga, wait_until
from textual.widgets import Collapsible, TabbedContent, Tree

from ars_magica_manager import storage, transfer, tribunal_packages
from ars_magica_manager import tribunals as trib
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.forms import tribunal as tribunal_forms
from ars_magica_manager.models import Covenant, Saga, Tribunal, TribunalDiaryEntry
from ars_magica_manager.sheets import tribunal as tribunal_sheet
from ars_magica_manager.tribunal_packages.normandy import lapsed, prize
from ars_magica_manager.tribunal_packages.normandy import tenures as normandy_tenures
from ars_magica_manager.tribunal_packages.rhine import gilds as rhine_gilds
from ars_magica_manager.tribunal_packages.theban import magi as theban_magi
from ars_magica_manager.tribunal_packages.theban import standing as tokens_standing
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.prompts import MenuScreen


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
    assert [t.id for t in saga.tribunals] == [
        "thebes",
        "normandy",
        "transylvania",
        "alps",
        "hibernia",
    ]
    assert {c.tribunal_id for c in saga.covenants} == {None}


def test_the_sheet_counts_the_covenants_and_the_troupes_votes():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    rhine.covenants_total = 6
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, rhine)}
    assert facts["Covenants"] == "2 recorded of 6"
    assert facts["Praeco"] == "Severinus"
    assert [row[0] for row in tribunal_sheet.roster_grid(saga, rhine).rows] == [
        "✦ Keep",
        "Other covenants",
        "Fengheld",
        "4 unnamed",
    ]
    # The divider row is a heading: no covenant is chosen through it.
    assert tribunal_sheet.roster_grid(saga, rhine).keys == [0, None, 1, 2]


def test_a_covenant_votes_its_magi_and_its_proxies():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    grid = tribunal_sheet.roster_grid(saga, rhine)
    assert grid.rows[2][:5] == ["Fengheld", "Sketch", "3", "4", "1 held"]
    form = tribunal_forms.roster_ops(saga, rhine).edit(1)
    assert isinstance(form, Form)
    form.apply({"proxies": 0})
    assert rhine.proxies == {}
    assert isinstance(tribunal_forms.roster_ops(saga, rhine).edit(5), Refuse)


def test_the_docket_flags_notice_not_given_and_cases_against_yours():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    assert tribunal_sheet.notice_due(rhine) == "Spring 1228"  # a season, as core
    assert tribunal_sheet.season_before(1228, "Spring", 1) == (1227, "Winter")
    grid = tribunal_sheet.cases_grid(saga, rhine)
    assert [row[3] for row in grid.rows] == ["Spring 1228", "not given"]
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
    # The core and the Grand Tribunal's need no book.
    assert [p.key for p in tribunal_packages.offered(saga)] == ["core", "grand"]
    # The one a Tribunal follows stays on offer, whatever its book.
    assert "rhine" in [p.key for p in tribunal_packages.offered(saga, rhine.package)]
    saga.books_in_play = ["GotF"]
    assert "rhine" in [p.key for p in tribunal_packages.offered(saga)]


def test_the_rhine_adds_gilds_and_a_gild_column():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    roster = tribunal_sheet.roster_grid(saga, rhine)
    assert roster.columns[5] == "Gild"
    assert [row[5] for row in roster.rows] == ["Hermetic", "", "Hermetic"]
    ops = tribunal_forms.tribunal_ops(saga, rhine)
    form = ops["section-trib-gilds"].add()
    assert isinstance(form, Form)
    labels = [f.label for f in form.fields()]
    assert labels == [
        "Gild",
        "Agenda",
        "Led by",
        "And by",
        "And by",
        "Keep",
        "Fengheld",
    ]
    form.apply({"name": "Mercantile", "agenda": "", "member_cov_sketch": True})
    assert rhine_gilds(rhine)[-1] == {
        "name": "Mercantile",
        "agenda": "",
        "leader_ids": [],
        "magi": [],
        "members": ["cov_sketch"],
    }
    # An older save's dues are read as the agenda.
    assert rhine_gilds(rhine)[0]["agenda"] == "2 pawns a year"
    assert tribunal_sheet.roster_grid(saga, rhine).rows[2][5] == "Hermetic, Mercantile"


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


def test_a_theban_tribunal_votes_by_magi_present_and_marks_the_ostracised():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    facts = {f.label: f.value for f in tribunal_sheet.facts(saga, thebes)}
    assert facts["Customs"] == "Theban: The Polity"
    # Tokens are merit, not votes: the votes are counted as under the core.
    assert facts["Your votes"] == tribunal_sheet.your_votes_text(saga, thebes)
    assert "token" not in facts["Your votes"]
    package = tribunal_packages.of(thebes)
    assert package.meeting_steps == (
        "assembly",
        "apprentice_presentation",
        "ostrakismos",
        "sentences",
        "conduct_of_archai",
        "common_vis",
        "end_of_term",
        "sortition",
        "archon_polemarch",
        "propitiation",
    )
    tokens = package.tabs[0].lists[0].grid(saga, thebes)
    assert tokens.columns[2] == "Status"
    assert [row[2] for row in tokens.rows] == ["Polites", "Polites"]
    assert [row[5] for row in tokens.rows] == ["0", "1"]
    assert [row[6] for row in tokens.rows] == ["Archon", "Ostracised to 1225"]
    archai = package.tabs[0].lists[1].grid(saga, thebes)
    assert [row[1] for row in archai.rows] == ["Leandro", "vacant"]
    saga.current_year = 1226
    assert tokens_standing(saga, thebes, theban_magi(thebes)[1]) == ""


def test_a_theban_save_that_says_liturgies_reads_them_as_services():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    entry = thebes.package_data["theban"]["magi"][1]
    entry["liturgies"] = entry.pop("services")
    assert theban_magi(thebes)[1]["services"] == 1
    assert "liturgies" not in theban_magi(thebes)[1]


def test_a_theban_metoikos_holds_no_tokens_or_shards():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    assert thebes is not None
    ops = tribunal_packages.of(thebes).tabs[0].lists[0].ops(saga, thebes)
    form = ops.add()
    assert form.validate is not None
    guest = {"character_id": "mag1", "status": "metoikos", "tokens": 0, "shards": 0}
    assert form.validate(guest) is None
    assert form.validate({**guest, "shards": 1}) == (
        "A metoikos holds no tokens or shards."
    )


def test_a_theban_covenant_keeps_its_phyle():
    saga = everything_saga()
    thebes = saga.tribunal("thebes")
    keep = saga.covenant("cov1")
    assert thebes is not None and keep is not None
    package = tribunal_packages.of(thebes)
    column = package.columns[0]
    assert column.title == "Phyle"
    assert column.value(saga, thebes, keep) == "Aegean"
    assert column.save is not None
    column.save(thebes, keep, "Kretan")
    assert column.value(saga, thebes, keep) == "Kretan"
    assert package.save_covenant is not None
    package.save_covenant(thebes, keep.id, {"phyle": ""})
    assert column.value(saga, thebes, keep) == ""


def test_normandy_ranks_its_tourney_and_marks_lapsed_tenures():
    saga = everything_saga()
    normandy = saga.tribunal("normandy")
    assert normandy is not None
    package = tribunal_packages.of(normandy)
    assert package.meeting_steps == ("succession", "library", "tourney", "host_by_lot")
    tourney = package.tabs[1].lists[0].grid(saga, normandy)
    # The highest points first; teams level keep the order entered.
    assert [(r[1], r[2], r[4], r[5]) for r in tourney.rows] == [
        ("1", "Mont Saint Michel", "31", "Siege of Normandy"),
        ("2", "Fudarus", "24", "Siege of Valor"),
        ("3", "Visitors of Iberia", "18", ""),
    ]
    assert tourney.keys == [1, 0, 2]
    assert (prize(21), prize(22)) == ("6, and 6 to give", "0")
    saga.current_year = 1220
    assert [lapsed(saga, t) for t in normandy_tenures(normandy)] == [True, False]
    tenure = package.tabs[0].lists[0].grid(saga, normandy)
    assert tenure.rows[0][1:4] == ["the Tribunal", "Tropaeum", "1220"]


def test_a_package_without_data_is_a_note_on_the_peripheral_code():
    saga = everything_saga()
    rhine = saga.tribunals[0]
    assert tribunal_sheet.customs_note(Tribunal("x", "X")) == ""
    rhine.package = "provence"
    assert "found a covenant" in tribunal_sheet.customs_note(rhine)
    assert tribunal_packages.of(rhine).tabs == ()
    rhine.package = "hibernia"
    assert "Hill of Tara" in tribunal_sheet.customs_note(rhine)
    saga.books_in_play = ["F&F"]
    assert [p.key for p in tribunal_packages.offered(saga)] == [
        "core",
        "grand",
        "provence",
    ]


def test_the_levant_package_is_the_treaty_of_baghdad_as_a_note():
    saga = everything_saga()
    tribunal = saga.tribunals[0]
    tribunal.package = "levant"
    package = tribunal_packages.of(tribunal)
    assert tribunal_packages.label(package) == "Levant: The Treaty of Baghdad"
    # Renewing the Treaty is a motion with a term: no step of its own.
    assert package.book == "B&S" and package.tabs == () and not package.meeting_steps
    note = tribunal_sheet.customs_note(tribunal)
    assert "Treaty of Baghdad" in note and "Guernicus" in note
    saga.books_in_play = ["B&S"]
    assert [p.key for p in tribunal_packages.offered(saga)] == [
        "core",
        "grand",
        "levant",
    ]


def test_the_alps_package_counts_chairs_and_ostracises_by_the_sherds():
    from ars_magica_manager.tribunal_packages import alps

    saga = everything_saga()
    tribunal = saga.tribunals[0]
    tribunal.package = "alps"
    package = tribunal_packages.of(tribunal)
    assert tribunal_packages.label(package) == "Greater Alps: Chairs and ostracism"
    covenant = saga.covenants[0]
    covenant.tribunal_id = tribunal.id
    alps.save_chairs(tribunal, covenant, 3)
    magi = sum(
        1 for c in saga.characters if c.covenant_id == covenant.id and c.type == "magus"
    )
    (column,) = package.columns
    assert column.value(saga, tribunal, covenant) == f"3 of {magi}"
    # One sherd in four must name him; the exile runs twenty-one years.
    assert alps.ostracism_problem({"sherds": 10, "voters": 41}) is not None
    assert alps.ostracism_problem({"sherds": 11, "voters": 41}) is None
    assert alps.ostracism_problem({"sherds": 5, "voters": 4}) is not None
    magus = next(
        c for c in saga.characters if c.covenant_id == covenant.id and c.type == "magus"
    )
    alps.ostracised(tribunal).append(
        {
            "character_id": magus.id,
            "year": saga.current_year,
            "sherds": 30,
            "voters": 90,
        }
    )
    (entry,) = alps.ostracised(tribunal)
    assert alps.until(entry) == saga.current_year + 21
    ((label, says),) = tribunal_packages.magus_facts(saga, magus)
    assert label == "Ostracised" and str(saga.current_year + 21) in says
    grid = package.lists[0].grid(saga, tribunal)
    assert grid.rows[0][2] == "30 of 90"
    saga.books_in_play = ["SoI"]
    assert "alps" in [p.key for p in tribunal_packages.offered(saga)]


def test_the_stonehenge_and_novgorod_packages_are_notes():
    saga = everything_saga()
    tribunal = saga.tribunals[0]
    for key, words in (("stonehenge", "Blackthorn"), ("novgorod", "Royal Embargo")):
        tribunal.package = key
        package = tribunal_packages.of(tribunal)
        assert package.tabs == () and not package.columns
        assert words in tribunal_sheet.customs_note(tribunal)


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
            (NodeKind.TRIBUNAL, "thebes"),
            (NodeKind.TRIBUNAL, "normandy"),
            (NodeKind.TRIBUNAL, "transylvania"),
            (NodeKind.TRIBUNAL, "alps"),
            (NodeKind.TRIBUNAL, "hibernia"),
            (NodeKind.COVENANT, "lone"),
            (NodeKind.NEIGHBOUR_GROUP, "lords"),
            (NodeKind.NEIGHBOUR_GROUP, "church"),
            (NodeKind.NEIGHBOUR_GROUP, "universities"),
            (NodeKind.NEIGHBOUR_GROUP, "factions"),
            (NodeKind.NEIGHBOUR_GROUP, "threats"),
            (NodeKind.NEIGHBOUR_GROUP, "places"),
        ]
        assert [n.data for n in region.children[0].children] == [
            (NodeKind.COVENANT, "cov_sketch")
        ]
        assert region.children[6].allow_expand is False  # a line with nothing


async def test_new_tribunal_opens_it_and_d_deletes_it():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _workspace(pilot, app)
        workspace.action_create_tribunal()
        await pilot.pause()
        app.screen.query_one("#fld-name").value = "Provence"
        app.screen.query_one("#btn-save").press()
        assert await wait_until(
            pilot,
            lambda: (
                (view := workspace._tribunal_sheet_view) is not None
                and view.tribunal.name == "Provence"
            ),
        )
        workspace.query_one("#nav-tree", Tree).focus()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [t.name for t in storage.load_saga("test_saga").tribunals]
                == [
                    "Rhine",
                    "Theban",
                    "Normandy",
                    "Transylvania",
                    "Greater Alps",
                    "Hibernia",
                ]
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
        # More offers Withdraw and War's End for a chosen case.
        await pilot.press("m")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("w")
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
        "History",
        "Docket",
        "Arguments",
        "Meeting",
        "Peripheral Code",
        "Treasury",
        "Gilds",
        "Great Library",
        "Diary",
        "Secrets",
    ]
    saga_page = SagaPage(saga, PALETTES[0], lambda _id: None)
    titles = [label.text() for label in saga_page.findChildren(QLabel)]
    assert not any("Tribunals (6)" in title for title in titles)
    # The Region is built when first opened, and leads with the Tribunals.
    saga_page.codex.open_chapter("The Region")
    titles = [label.text() for label in saga_page.findChildren(QLabel)]
    assert any("Tribunals (6)" in title for title in titles)


def test_choosing_a_ruling_a_gild_or_a_diary_entry_shows_it_in_the_inspector():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QTableView

    from ars_magica_manager.gui.markup_html import plain
    from ars_magica_manager.gui.themes import PALETTES
    from ars_magica_manager.gui.tribunal import TribunalPage

    QApplication.instance() or QApplication([])
    saga = everything_saga()
    tribunal = next(t for t in saga.tribunals if t.rulings and t.diary)
    page = TribunalPage(saga, tribunal, PALETTES[0])
    codex = page.codex

    def choose(chapter: str, row: int = 0) -> str:
        index = codex.chapters().index(chapter)
        view = codex.pages.widget(index).findChildren(QTableView)[0]
        view.setCurrentIndex(view.model().index(row, 0))
        return plain(codex.inspector.body.text())

    ruling = tribunal.rulings[0]
    assert ruling.says.strip().splitlines()[-1] in choose("Peripheral Code")
    assert codex.inspector.title.text() == ruling.title
    choose("Diary")
    assert codex.inspector.title.text() in {e.title for e in tribunal.diary}
    if "Gilds" in codex.chapters():
        assert "Members" in choose("Gilds")


def test_a_rhine_covenant_s_own_form_ticks_its_gilds():
    from ars_magica_manager.forms import covenant as covenant_forms
    from ars_magica_manager.forms import creation as creation_forms
    from ars_magica_manager.tribunal_packages import rhine as rhine_package

    saga = everything_saga()
    rhine = saga.tribunals[0]
    rhine_package.gilds(rhine)[:] = [
        {"name": "Oak Gild", "members": [], "dues": ""},
        {"name": "Ash Gild", "members": [], "dues": ""},
    ]
    covenant = saga.covenants[0]
    covenant.tribunal_id = rhine.id
    form = covenant_forms.covenant_form(saga, covenant)
    fields = form.fields()
    ticks = [f for f in fields if f.label in {"Oak Gild", "Ash Gild"}]
    values = {f.key: f.value for f in fields}
    assert len(ticks) == 2 and all(t.show_if(values) for t in ticks)
    # Shown only while a Tribunal with gilds is chosen.
    assert not ticks[0].show_if({**values, "tribunal_id": None})
    values[ticks[1].key] = True
    form.apply({k: v for k, v in values.items() if k != "where"})
    assert rhine_package.gilds_of(rhine, covenant) == ["Ash Gild"]
    # New Covenant asks the Tribunal too, and its gilds.
    new = creation_forms.new_covenant_form(saga)
    fields = new.fields()
    values = {f.key: f.value for f in fields} | {"name": "Waldheim"}
    values["tribunal_id"] = rhine.id
    values[next(f.key for f in fields if f.label == "Oak Gild")] = True
    new.apply(values)
    added = saga.covenants[-1]
    assert added.tribunal_id == rhine.id
    assert rhine_package.gilds_of(rhine, added) == ["Oak Gild"]


def test_the_sheet_shows_in_the_saga_s_first_paragraph_and_the_rest_with_history():
    tribunal = Tribunal(id="t", name="T", summary="One.\nStill one.\n\n Two.\n\nThree.")
    assert tribunal_sheet.summary_parts(tribunal) == (
        "One.\nStill one.",
        "Two.\n\nThree.",
    )
    assert tribunal_sheet.summary_parts(
        Tribunal(id="t", name="T", summary="Short.")
    ) == (
        "Short.",
        "",
    )
    assert tribunal_sheet.summary_parts(Tribunal(id="t", name="T")) == ("", "")


async def test_hold_tribunal_opens_each_step_after_the_one_saved():
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
        await view.build_all_tabs()
        rows = view.query_one("#meeting-business", SelectableList)
        rows.select_data_index(0)
        assert await wait_until(pilot, lambda: rows.selected_data_index == 0)
        workspace._core_verb("section-meeting-business", "edit")
        assert await wait_until(
            pilot, lambda: "Hold Tribunal" in str(getattr(app.screen, "title_text", ""))
        )
        roll = app.screen
        assert await wait_until(pilot, lambda: bool(roll.query("#btn-save")))
        roll.query_one("#btn-save").press()
        # Saved, the roll call opens the meeting and the Opening follows.
        assert await wait_until(
            pilot,
            lambda: (
                app.screen is not roll
                and "Opening and the oaths"
                in str(getattr(app.screen, "title_text", ""))
            ),
        )
        assert storage.load_saga("test_saga").tribunals[0].meeting is not None
        opening = app.screen
        assert await wait_until(pilot, lambda: bool(opening.query("#btn-cancel")))
        opening.query_one("#btn-cancel").press()
        assert await wait_until(pilot, lambda: app.screen is workspace)
