"""Line and Sketch characters: the statblock, what their sheet leaves out,
and Promote and Demote."""

from __future__ import annotations

import os

import pytest
from support import screen_lines, wait_until
from textual.widgets import Collapsible, Tree

from ars_magica_manager import storage, world
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.commands import Confirm
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.models import (
    FULL,
    LINE,
    SKETCH,
    Ability,
    ArtScore,
    Character,
    Covenant,
    Saga,
    ScoredTrait,
)
from ars_magica_manager.sheets import character as cs
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens import ConfirmScreen, WorkspaceScreen
from ars_magica_manager.tui.screens.prompts import MenuScreen


def _saga(detail: str = SKETCH) -> Saga:
    severinus = Character(
        id="mag1",
        name="Severinus",
        type="magus",
        covenant_id="cov1",
        detail=detail,
        summary="Fengheld's prosecutor.",
        abilities=[Ability("Code of Hermes", xp=105, specialty="Rhine customs")],
        arts={"rego": ArtScore(xp=171), "mentem": ArtScore(xp=120)},
        personality_traits=[ScoredTrait("Proud", 3)],
    )
    return Saga(
        id="test_saga",
        name="Saga",
        covenants=[Covenant(id="cov1", saga_id="test_saga", name="Fengheld")],
        characters=[severinus],
    )


# -- the statblock --


def test_a_sketch_reads_as_the_books_print_an_npc():
    saga = _saga()
    block = dict(cs.statblock(saga, saga.characters[0]))
    assert block["In the Saga"] == "Fengheld's prosecutor."
    assert block["Characteristics"].startswith("Int 0, Per 0, Pre 0")
    assert block["Arts"] == "Rego 18, Mentem 15"
    assert block["Abilities"] == (
        f"Code of Hermes 6 (Rhine customs)\n[$label]{cs.UNLISTED_ABILITIES}[/]"
    )
    assert block["Personality"] == "Proud: +3"
    assert "Reputations" not in block  # empty parts are left out


def test_a_line_character_is_only_who_they_are():
    saga = _saga(LINE)
    assert cs.statblock(saga, saga.characters[0]) == [
        ("In the Saga", "Fengheld's prosecutor.")
    ]
    saga.characters[0].summary = ""
    assert "Not written yet" in cs.statblock_text(saga, saga.characters[0])


def test_only_line_and_sketch_characters_have_a_statblock():
    character = _saga(FULL).characters[0]
    assert not cs.has_statblock(character)
    assert "Detail" not in cs.info_right_text(_saga(FULL), character)
    sketch = _saga().characters[0]
    assert cs.has_statblock(sketch)
    assert "Sketch" in cs.info_right_text(_saga(), sketch)


def test_a_sketchs_info_form_asks_who_they_are():
    saga = _saga()
    character = saga.characters[0]
    keys = [f.key for f in character_forms.character_info_fields(saga, character)]
    assert keys[:2] == ["name", "summary"]
    full = _saga(FULL)
    keys = [
        f.key for f in character_forms.character_info_fields(full, full.characters[0])
    ]
    assert "summary" not in keys


# -- Promote and Demote --


def test_promote_and_demote_step_one_level():
    assert [world.promoted(d) for d in (LINE, SKETCH, FULL)] == [SKETCH, FULL, None]
    assert [world.demoted(d) for d in (LINE, SKETCH, FULL)] == [None, LINE, SKETCH]


@pytest.mark.parametrize(
    ("detail", "offered"),
    [
        (LINE, ["Promote"]),
        (SKETCH, ["Promote", "Demote"]),
        (FULL, ["In Creation / In Play", "Demote"]),
    ],
)
def test_more_offers_what_the_level_allows(detail, offered):
    page = menu_forms.page_for(_saga(detail), NodeKind.CHARACTER, character_id="mag1")
    labels = [item.label for item in menu_forms.more_items(page)]
    wanted = {"Promote", "Demote", "In Creation / In Play"}
    assert [label for label in labels if label in wanted] == offered


def test_promoting_a_sketch_to_full_starts_its_creation():
    saga = _saga()
    character = saga.characters[0]
    step = menu_forms.change_detail(saga, character, FULL)
    assert isinstance(step, Confirm) and "Creation Worksheet" in step.question
    step.apply()
    assert (character.detail, character.in_creation) == (FULL, True)
    assert character.arts["rego"].xp == 171  # nothing copied or lost

    step = menu_forms.change_detail(saga, character, SKETCH)
    assert "Demote" in step.question
    step.apply()
    assert (character.detail, character.in_creation) == (SKETCH, False)


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
            if n.data == (NodeKind.CHARACTER, "mag1"):
                return n
            stack.extend(n.children)
        return None

    assert await wait_until(pilot, lambda: node() is not None)
    tree.select_node(node())
    assert await wait_until(
        pilot,
        lambda: (
            workspace._character_sheet_view is not None
            and workspace._character_sheet_view.initial_tab_seen
        ),
    )
    return workspace


async def test_the_terminal_opens_a_sketch_on_its_statblock_and_promotes_it():
    storage.save_saga(_saga())
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 60)) as pilot:
        workspace = await _open(pilot, app)
        view = workspace._character_sheet_view
        assert view.tab_ids == [
            "tab-statblock",
            "tab-description",
            "tab-abilities",
            "tab-vf",
            "tab-hermetic",
            "tab-diary",
            "tab-secrets",
        ]
        text = "\n".join(screen_lines(app))
        assert "Abilities not listed count as 0." in text
        assert "Code of Hermes 6 (Rhine customs)" in text

        view.query_one("#section-char-info", Collapsible).focus_section()
        await pilot.pause()
        await pilot.press("m")
        assert await wait_until(pilot, lambda: isinstance(app.screen, MenuScreen))
        await pilot.press("p")
        assert await wait_until(pilot, lambda: isinstance(app.screen, ConfirmScreen))
        await pilot.press("y")
        assert await wait_until(
            pilot, lambda: storage.load_saga("test_saga").characters[0].detail == FULL
        )
        assert await wait_until(
            pilot,
            lambda: (
                (v := workspace._character_sheet_view) is not None
                and "tab-planning" in v.tab_ids
            ),
        )
        assert storage.load_saga("test_saga").characters[0].in_creation


# -- the desktop --


@pytest.mark.parametrize(
    ("detail", "chapters"),
    [
        (LINE, ["Statblock", "Description", "Diary", "Secrets"]),
        (
            SKETCH,
            [
                "Statblock",
                "Description",
                "Abilities",
                "Virtues & Flaws",
                "Hermetic Magic",
                "Diary",
                "Secrets",
            ],
        ),
        (
            FULL,
            [
                "Description",
                "Abilities",
                "Virtues & Flaws",
                "Hermetic Magic",
                "Inventory",
                "Planning",
                "Diary",
                "Secrets",
            ],
        ),
    ],
)
def test_the_desktop_sheet_has_the_chapters_of_its_level(detail, chapters):
    pytest.importorskip("PySide6")
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication

    from ars_magica_manager.gui.character_sheet import CharacterSheet
    from ars_magica_manager.gui.themes import PALETTES

    QApplication.instance() or QApplication([])
    saga = _saga(detail)
    sheet = CharacterSheet(saga, saga.characters[0], PALETTES[0])
    assert sheet.chapters() == chapters
