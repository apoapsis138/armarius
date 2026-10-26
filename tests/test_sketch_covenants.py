"""Line and Sketch covenants: votes, What Matters, the attitude, favour and
link sections every world record shares, Promote and Demote, and the
sheets on both front-ends."""

from __future__ import annotations

import os

import pytest
from support import screen_lines, wait_until
from textual.widgets import Collapsible, Tree

from ars_magica_manager import connections, storage, world
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Choose, Confirm, Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import world as world_forms
from ars_magica_manager.models import (
    FULL,
    LINE,
    SKETCH,
    Attitude,
    Character,
    Covenant,
    Favour,
    Reason,
    Saga,
)
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import (
    ConfirmScreen,
    FieldsDialog,
    SelectableList,
    WorkspaceScreen,
)
from ars_magica_manager.tui.screens.prompts import MenuScreen


def _saga(detail: str = SKETCH) -> Saga:
    arnhaven = Covenant(id="arn", saga_id="s", name="Arnhaven")
    fengheld = Covenant(
        id="fen",
        saga_id="s",
        name="Fengheld",
        detail=detail,
        played=False,
        unnamed_magi=2,
        what_matters="Vis: the Ahse ford, 3 Aquam\nAn old seat in the Gild",
        attitudes=[
            Attitude("arn", 0, [Reason("Claimed the ford", -1, 1218, "Autumn")])
        ],
        favours=[
            Favour("Hid a grog", "Fengheld", "Arnhaven"),
            Favour("Lent a book", "Arnhaven", "Fengheld"),
        ],
    )
    magi = [
        Character(id="sev", name="Severinus", type="magus", covenant_id="fen"),
        Character(id="the", name="Theodric", type="magus", covenant_id="fen"),
        Character(id="grog", name="Hugo", type="grog", covenant_id="fen"),
    ]
    return Saga(
        id="test_saga", name="Saga", covenants=[arnhaven, fengheld], characters=magi
    )


# -- the core --


def test_votes_count_named_and_unnamed_magi():
    saga = _saga()
    fengheld = saga.covenants[1]
    assert (
        world.votes(saga, fengheld) == 4
    )  # two named magi (not the grog), two unnamed
    assert world.votes_text(saga, fengheld) == "4 (2 named, 2 unnamed)"
    fengheld.unnamed_magi = 0
    assert world.votes_text(saga, fengheld) == "2"


def test_what_matters_reads_one_entry_a_line():
    assert world.what_matters_rows("Vis: the ford\n\n• An old seat\n") == [
        ("Vis", "the ford"),
        ("", "An old seat"),
    ]


def test_a_reason_moves_the_attitude_and_where_it_started_cannot_be_deleted():
    saga = _saga()
    fengheld = saga.covenants[1]
    ops = world_forms.attitude_ops(saga, fengheld)
    assert ops.rows() == ["where it started toward Arnhaven", "Claimed the ford"]
    step = ops.add()
    assert isinstance(step, Form)
    step.apply(
        {
            "covenant": "arn",
            "what": "Shared vis",
            "change": 2,
            "year": 1220,
            "season": "",
        }
    )
    assert world.attitude_score(fengheld.attitudes[0]) == 1
    assert isinstance(ops.remove(0), Refuse)
    start = ops.edit(0)
    assert isinstance(start, Form)
    start.apply({"start": -3})
    assert world.attitude_score(fengheld.attitudes[0]) == -2
    delete = ops.remove(2)
    assert isinstance(delete, Confirm)
    delete.apply()
    assert [r.what for r in fengheld.attitudes[0].reasons] == ["Claimed the ford"]


def test_an_attitude_toward_a_covenant_with_none_yet_starts_at_zero():
    saga = _saga()
    saga.covenants.append(Covenant(id="third", saga_id="s", name="Third"))
    fengheld = saga.covenants[1]
    ops = world_forms.attitude_ops(saga, fengheld)
    assert ops.rows()[-1] == "where it started toward Third"
    step = ops.add("third")
    assert isinstance(step, Form)
    step.apply({"covenant": "third", "what": "Met", "change": 1})
    assert world.attitude_score(world.attitude_toward(fengheld, "third")) == 1


def test_a_link_is_made_by_kind_then_record_and_shows_from_the_other_side():
    saga = _saga()
    fengheld = saga.covenants[1]
    ops = world_forms.link_ops(saga, fengheld)
    choose = ops.add()
    assert isinstance(choose, Choose)
    assert [c.value for c in choose.choices()] == ["characters", "covenants"]
    form = choose.apply("covenants")
    assert isinstance(form, Form)
    targets = {v: k for k, v in form.fields()[0].options}
    assert targets == {"arn": "Arnhaven"}  # never itself
    form.apply({"target_id": "arn", "note": "Rivals"})
    assert ops.rows() == ["Arnhaven: Rivals"]
    linked = {f.label: f.value for f in connections.facts(saga, saga.covenants[0])}
    assert linked["Linked from"] == "Fengheld (Rivals)"


def test_a_magus_added_to_a_sketch_is_a_line_in_play_nowhere():
    saga = _saga()
    fengheld = saga.covenants[1]
    ops = world_forms.magus_ops(saga, fengheld)
    step = ops.add()
    assert isinstance(step, Form)
    step.apply({"name": "Ulla", "house": None, "detail": LINE, "summary": ""})
    ulla = saga.characters[-1]
    assert (ulla.covenant_id, ulla.detail, ulla.in_creation) == ("fen", LINE, False)
    assert world.votes(saga, fengheld) == 5


def test_a_sketch_covenant_is_left_out_of_play():
    saga = _saga()
    assert [c.name for c in saga.covenants if world.takes_part_in_play(c)] == [
        "Arnhaven"
    ]


@pytest.mark.parametrize(
    ("detail", "offered"),
    [
        (LINE, ["Promote"]),
        (SKETCH, ["Promote", "Demote"]),
        (FULL, ["In Creation / In Play", "Demote"]),
    ],
)
def test_more_offers_a_covenant_what_its_level_allows(detail, offered):
    page = menu_forms.page_for(_saga(detail), NodeKind.COVENANT, covenant_id="fen")
    labels = [item.label for item in menu_forms.more_items(page)]
    wanted = {"Promote", "Demote", "In Creation / In Play"}
    assert [label for label in labels if label in wanted] == offered


def test_promoting_a_sketch_covenant_starts_its_creation():
    saga = _saga()
    fengheld = saga.covenants[1]
    step = menu_forms.change_detail(saga, fengheld, FULL)
    assert isinstance(step, Confirm) and "full covenant" in step.question
    step.apply()
    assert (fengheld.detail, fengheld.in_creation, fengheld.played) == (
        FULL,
        True,
        False,
    )
    assert fengheld.what_matters  # nothing lost


# -- the terminal --


async def _open(pilot, app) -> WorkspaceScreen:
    await pilot.press("enter")
    assert await wait_until(pilot, lambda: isinstance(app.screen, WorkspaceScreen))
    workspace = app.screen
    tree = workspace.query_one("#nav-tree", Tree)

    def node():
        stack = [tree.root]
        while stack:
            n = stack.pop()
            if n.data == (NodeKind.COVENANT, "fen"):
                return n
            stack.extend(n.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(
        pilot,
        lambda: (
            (view := workspace._covenant_sheet_view) is not None
            and view.covenant.id == "fen"
            and view.initial_tab_seen
        ),
    )
    return workspace


async def test_the_terminal_opens_a_sketch_on_its_overview_and_edits_the_chosen_favour():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app)
        view = workspace._covenant_sheet_view
        assert view.tab_ids == [
            "tab-cov-overview",
            "tab-cov-charter",
            "tab-cov-diary",
            "tab-secrets",
        ]
        text = "\n".join(screen_lines(app))
        assert "4 (2 named, 2 unnamed)" in text
        assert "Toward Arnhaven" in text
        favours = view.query_one("#favours-list", SelectableList)
        view.query_one("#section-favours", Collapsible).focus_section()
        await pilot.pause()
        favours.select_data_index(1)
        await pilot.pause()
        await pilot.press("d")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                [f.what for f in storage.load_saga("test_saga").covenants[1].favours]
                == ["Hid a grog"]
            ),
        )
        await pilot.press("a")
        assert await wait_until(pilot, lambda: isinstance(app.screen, FieldsDialog))


async def test_the_terminal_promotes_a_sketch_covenant_to_a_full_sheet():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app)
        workspace._covenant_sheet_view.query_one(
            "#section-cov-info", Collapsible
        ).focus_section()
        await pilot.pause()
        await pilot.press("m")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("p")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot,
            lambda: (
                (v := workspace._covenant_sheet_view) is not None
                and "tab-cov-build" in v.tab_ids
            ),
        )
        saved = storage.load_saga("test_saga").covenants[1]
        assert (saved.detail, saved.in_creation) == (FULL, True)


# -- the desktop --


@pytest.mark.parametrize(
    ("detail", "chapters"),
    [
        (LINE, ["Sketch", "Charter", "Diary", "Secrets", "Manage"]),
        (SKETCH, ["Sketch", "Charter", "Diary", "Secrets", "Manage"]),
    ],
)
def test_the_desktop_draws_a_sketch_covenant_on_one_chapter(detail, chapters):
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.covenant import CovenantPage
    from ars_magica_manager.gui.manage import RecordControls
    from ars_magica_manager.gui.themes import PALETTES

    QApplication.instance() or QApplication([])
    saga = _saga(detail)
    page = menu_forms.page_for(saga, NodeKind.COVENANT, covenant_id="fen")
    controls = RecordControls(
        page,
        lambda *_: None,
        lambda: None,
        lambda *_: None,
        lambda *_: None,
        lambda: None,
    )
    covenant_page = CovenantPage(
        saga, "fen", PALETTES[0], lambda _id: None, lambda _id: None, controls=controls
    )
    assert covenant_page.chapters() == chapters
