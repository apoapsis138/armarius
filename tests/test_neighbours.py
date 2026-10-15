"""The Region's neighbours: the kinds and the books they need, making,
editing and deleting one, how the Region shows them, and both
front-ends' pages."""

from __future__ import annotations

import os
import random

import pytest
from support import everything_saga, wait_until
from textual.widgets import Tree

from ars_magica_manager import (
    churches,
    factions,
    lords,
    neighbour_filter,
    neighbour_forms,
    neighbours,
    region_sheet,
    storage,
    threats,
    towns,
    universities,
)
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.models import Attitude, Link, Neighbour, Reason, Saga
from ars_magica_manager.rules import dice
from ars_magica_manager.sections import NEIGHBOUR_INFO_SECTION
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import WorkspaceScreen


def test_new_neighbour_offers_the_kinds_whose_book_is_in_play():
    saga = everything_saga()
    saga.books_in_play = ["LoM"]
    command = neighbour_forms.new_neighbour(saga)
    assert isinstance(command, Choose)
    assert [c.value for c in command.choices()] == [
        "lord",
        "faction",
        "threat",
        "place",
    ]
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
        "universities",  # the Studium is in it
        "factions",
        "threats",
        "places",
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
    assert facts["Neighbours"] == "6, 1 warm, 1 wary"
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
        assert [n.data for n in lords.children] == [
            (NodeKind.NEIGHBOUR, "gottfried"),
            (NodeKind.NEIGHBOUR, "soest"),
        ]
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
    assert any("Lords and Towns (2)" in title for title in titles)
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    page = NeighbourPage(saga, gottfried, PALETTES[0])
    assert page.chapters() == ["Fief", "Standing"]
    words = [label.text() for label in page.findChildren(QLabel)]
    assert any("Archbishop of Cologne" in w for w in words)


def test_the_region_s_lists_narrow_to_a_region_and_a_kind():
    saga = everything_saga()
    soest = saga.neighbour("soest")
    assert soest is not None
    soest.place_id = "drachenfels"  # inside the Siebengebirge, two deep
    assert [r.id for r in neighbour_filter.regions(saga)] == ["siebengebirge"]
    assert [k.key for k in neighbour_filter.kinds(saga)][:2] == ["lord", "town"]
    form = neighbour_forms.filter_form(saga)
    assert [f.label for f in form.fields()] == ["Region", "Kind"]
    form.apply({"region": "siebengebirge", "kind": None})
    assert region_sheet.group_title(saga, "lords") == "Lords and Towns (1 of 2)"
    assert [row[0] for row in region_sheet.group_grid(saga, "lords").rows] == ["Soest"]
    # The region itself shows among the places, beside what it holds.
    assert [row[0] for row in region_sheet.group_grid(saga, "places").rows] == [
        "The Siebengebirge",
        "The Drachenfels",
    ]
    # Edit acts on the row shown, not on the list as entered.
    edit = neighbour_forms.group_ops(saga, "lords").edit(0)
    assert isinstance(edit, Form) and edit.fields()[0].value == "Soest"
    facts = {f.label: f.value for f in region_sheet.facts(saga)}
    assert facts["Showing"] == "in The Siebengebirge"
    assert "Showing" not in {f.label for f in region_sheet.facts(saga, False)}
    form = neighbour_forms.filter_form(saga)
    form.apply({"region": "siebengebirge", "kind": "lord"})
    assert region_sheet.group_grid(saga, "lords").rows == []
    assert region_sheet.group_grid(saga, "lords").empty == "None match the filter."
    assert neighbour_filter.describe(saga, neighbour_filter.current(saga)) == (
        "Lord, in The Siebengebirge"
    )
    neighbour_filter.choose(saga, neighbour_filter.Filter())
    assert region_sheet.group_title(saga, "lords") == "Lords and Towns (2)"


def test_the_desktop_filter_bar_narrows_the_region_s_cards():
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication, QLabel

    from ars_magica_manager.gui.pages import NeighbourFilterBar, SagaPage
    from ars_magica_manager.gui.themes import PALETTES

    QApplication.instance() or QApplication([])
    saga = everything_saga()
    page = SagaPage(saga, PALETTES[0], lambda _id: None)
    bar = page.findChild(NeighbourFilterBar)
    assert bar is not None
    bar.kind.setCurrentIndex(bar.kind.findData("town"))
    assert neighbour_filter.current(saga).kind == "town"
    titles = [label.text() for label in page.findChildren(QLabel)]
    assert any("Lords and Towns (1 of 2)" in title for title in titles)
    assert not any("The Church" in title for title in titles)


def test_a_lord_works_out_his_fief_from_the_lower_figures():
    saga = everything_saga()
    gottfried = saga.neighbour("gottfried")
    assert gottfried is not None
    facts = {f.label: f.value for f in lords.facts(saga, gottfried)}
    assert facts["Income"] == "1000 pounds a year"
    assert facts["To spend"] == "100 pounds a year"
    assert facts["Owes"] == (
        "Archbishop of Cologne: 50 knights for 40 days, or 100 pounds scutage"
    )
    assert facts["Aids"] == "50 pounds; relief 100 pounds"
    assert lords.army_of("duke", "Wealthy").knights == 75
    landed = Neighbour("k", "Sir Konrad", kind="lord", details={"manors": 1})
    facts = {f.label: f.value for f in lords.facts(saga, landed)}
    assert facts["To spend"] == "2 pounds a year"
    assert facts["Free time"] == "2 seasons"
    assert "Owes" not in facts
    assert lords.relief(landed) == 5
    assert lords.earns(4) == "5 for knighthood or freedom"
    assert lords.earns(6) == "Knighthood or freedom; 10 for a manor"
    assert lords.earns(25) == "A barony"


def test_new_lord_keeps_its_title_in_its_details():
    saga = everything_saga()
    form = neighbour_forms.new_neighbour_form(saga, "lord")
    keys = [f.key for f in form.fields()]
    assert keys[:5] == ["name", "title", "wealth", "manors", "seat"]
    assert form.validate is not None
    assert form.validate({"manors": -1}) == "Manors can't be fewer than none."
    form.apply(
        {"name": "Wolfram", "title": "baron", "wealth": "Poor", "manors": 20}
        | {"seat": "Hachen", "summary": "", "detail": "Sketch", "ruler": ""}
        | {"answers_to": None, "realm": None}
    )
    made = saga.neighbours[-1]
    assert made.details == {
        "title": "baron",
        "wealth": "Poor",
        "manors": 20,
        "seat": "Hachen",
    }
    assert not hasattr(made, "seat")


def test_a_town_shows_its_size_and_rolls_its_fairs_income():
    saga = everything_saga()
    soest = saga.neighbour("soest")
    assert soest is not None
    facts = {f.label: f.value for f in towns.facts(saga, soest)}
    assert facts["Population"] == "5,000 (large town)"
    assert facts["Guilds"] == "1 recorded; a town its size has 0 to 3 in 1220"
    effects = {
        towns.effect_of(dice.DieResult(value, (value,))): value
        for value in (0, 2, 5, 9, 12, 24)
    }
    assert list(effects) == [
        "Contraction",
        "Stagnation",
        "Status Quo",
        "Growth",
        "Expansion",
        "Boom",
    ]
    botch = dice.DieResult(0, (0,), botch_faces=(0,))
    assert towns.effect_of(botch) == "Slump"
    roll = towns.roll_fair(saga, soest, 0, random.Random(14))  # an 18
    assert isinstance(roll, Confirm)
    assert "Expansion (x1.2). Its income goes from 40 to 48" in roll.question
    roll.apply()
    fair = towns.fairs(soest)[0]
    assert (fair["income"], fair["last"]) == (48, "1220: Expansion x1.2, 40 to 48")
    fair["covenant_id"] = None
    assert isinstance(towns.roll_fair(saga, soest, 0), Refuse)
    soest.details["charter"] = fair["season"] = None  # left blank
    assert {f.label: f.value for f in towns.facts(saga, soest)}["Charter"] == ""
    assert towns.fairs_grid(saga, soest).rows[0][2] == ""


async def test_changing_a_neighbours_kind_rebuilds_its_sheet():
    storage.save_saga(everything_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        await pilot.pause()
        app.screen.query_one("#saga-list").focus()
        await pilot.press("enter")
        assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
        workspace = app.screen
        tree = workspace.query_one("#nav-tree", Tree)
        node = next(
            n
            for n in tree.root.children[1].children
            if n.data == (NodeKind.NEIGHBOUR_GROUP, "lords")
        ).children[0]
        tree.select_node(node)
        assert await wait_until(
            pilot, lambda: workspace._neighbour_sheet_view is not None
        )
        assert workspace.query("#section-nb-castles")
        workspace.saga.neighbour("gottfried").kind = "town"
        workspace._commit(NEIGHBOUR_INFO_SECTION, tree=True)
        assert await wait_until(
            pilot, lambda: bool(workspace.query("#section-nb-fairs"))
        )


def test_a_church_grows_its_dominion_as_a_rule_option():
    saga = everything_saga()
    cologne = saga.neighbour("cologne")
    assert cologne is not None
    assert churches.aura_text(saga, cologne) == "Dominion 5"
    saga.rule_options["dominion_growth"] = True
    assert churches.aura(saga, cologne) == 7  # a relic of 7 Faith Points
    cologne.details["relics"] = []
    cologne.details["founded"] = 1215
    assert churches.aura_text(saga, cologne) == "Dominion 4, worship since 1215"
    cologne.details["church"] = "Chapel"
    cologne.details["founded"] = 1100
    assert churches.aura(saga, cologne) == 3
    cologne.details["church"] = "Parish church"
    cologne.details |= {"founded": 1205, "abandoned": 1215}  # 4, over 10 years
    assert churches.aura_text(saga, cologne) == "Dominion 2, fading since 1215"
    saga.current_year = 1230
    assert churches.aura(saga, cologne) == 0
    assert churches.problem({"founded": 1210, "abandoned": 1200}) is not None
    saga.books_in_play = ["TC"]  # without Realms of Power: The Divine
    assert churches.aura(saga, cologne) == 4
    assert [f.key for f in churches.fields(saga, cologne)] == ["church", "order"]
    assert churches.relics_grid(saga, cologne).rows == []


def test_a_university_grants_its_faculties_degrees():
    saga = everything_saga()
    studium = saga.neighbour("studium")
    assert studium is not None
    facts = {f.label: f.value for f in universities.facts(saga, studium)}
    assert facts["Degrees"] == "Baccalaureus, Magister in Artibus, Doctor in Theology"
    assert facts["Fees"] == "4 pounds a year"
    assert universities.masters_grid(saga, studium).rows == [
        ["Master Gerard", "Doctor", "Theology", "3"]
    ]
    assert universities.faculties_grid(saga, studium).rows[1][3] == "1"
    studium.details["school"] = "Rural parish school"
    facts = {f.label: f.value for f in universities.facts(saga, studium)}
    assert (facts["Fees"], facts["Teaches up to"]) == ("0.1 pounds a year", "2")
    assert "Degrees" not in facts
    assert universities._master_problem({"name": " ", "who": None}) is not None


def test_a_faction_counts_its_linked_members():
    saga = everything_saga()
    coven = saga.neighbour("coven")
    assert coven is not None
    coven.links.append(Link("character", "mag1", "member"))
    facts = {f.label: f.value for f in factions.facts(saga, coven)}
    assert facts["Members"] == "7, 1 linked"
    coven.details["faction"] = None  # left blank
    assert {f.label: f.value for f in factions.facts(saga, coven)}["Faction"] == ""


def test_a_threats_stage_is_worked_out_from_the_date():
    saga = everything_saga()
    crown = saga.neighbour("crown")
    assert crown is not None
    at = threats.reached(saga, crown)
    assert at.current is not None and at.current["title"] == "Cattle go missing"
    assert at.next is not None and at.next["title"] == "The ford floods"
    assert region_sheet.threat_due(saga) == "The Hollow Crown, Winter 1220"
    saga.current_season = "Winter"
    assert threats.reached(saga, crown).current["title"] == "The ford floods"
    stages = threats.stages(crown)
    stages[1]["outcome"] = "Stopped"
    at = threats.reached(saga, crown)
    assert at.current["title"] == "Cattle go missing"
    assert at.next["title"] == "The crowning"
    stages[2]["outcome"] = "Happened"  # before its date
    assert threats.reached(saga, crown).current["title"] == "The crowning"
    assert threats.reached(saga, crown).next is None
    assert region_sheet.threat_due(saga) == ""


def test_a_threat_on_a_track_moves_with_its_position():
    saga = everything_saga()
    omen = Neighbour(
        "omen",
        "The Black Dog",
        kind="threat",
        details={
            "moves": "An omen count",
            "position": 2,
            "stages": [{"title": "Howling", "at": 1}, {"title": "A death", "at": 3}],
        },
    )
    saga.neighbours.append(omen)
    facts = {f.label: f.value for f in threats.facts(saga, omen)}
    assert facts["Stage reached"] == "Howling"
    assert facts["Next"] == "A death, at 3"
    assert facts["Position"] == "2"
    assert threats.due(saga, omen) is None  # not dated: not in Threat due
    keys = [f.key for f in threats.stage_fields(saga, omen, None)]
    assert "at" in keys and "year" not in keys
