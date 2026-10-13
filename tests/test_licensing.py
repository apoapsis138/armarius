"""The Ars Magica Open License obligations: every catalog
carries Atlas's attribution line, and Help's About this App shows the licences
and credits."""

import json
import sys

import pytest
from support import screen_lines, wait_until
from textual.widgets import OptionList

from ars_magica_manager import DATA_DIR, ROOT, catalog
from ars_magica_manager.tui.app import ArsMagicaManagerApp
from ars_magica_manager.tui.screens.help import HelpScreen
from ars_magica_manager.tui.screens.saga_picker import SagaPickerScreen

#: The attribution statement Atlas Games asks for, word for word.
ATLAS = (
    "Based on the material for Ars Magica, ©1993–2024, licensed by Trident, "
    "Inc. d/b/a Atlas Games®, under Creative Commons Attribution-ShareAlike "
    '4.0 International license 4.0 ("CC-BY-SA 4.0").'
)
CATALOGS = sorted(DATA_DIR.glob("*_catalog.json"))


def test_there_are_catalogs_to_check():
    assert len(CATALOGS) >= 7


@pytest.mark.parametrize("path", CATALOGS, ids=lambda path: path.name)
def test_every_catalog_carries_atlas_attribution(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    assert data["attribution"].endswith(ATLAS)


def test_spell_catalog_builder_writes_the_same_attribution():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import build_spell_catalog
    finally:
        sys.path.remove(str(ROOT / "tools"))
    data = json.loads(catalog.SPELL_CATALOG_PATH.read_text(encoding="utf-8"))
    assert build_spell_catalog.ATTRIBUTION == data["attribution"]


def test_catalog_loads_a_bare_list_or_an_attributed_file(tmp_path):
    entry = {"id": "house_x", "name": "X", "description": "An X."}
    bare = tmp_path / "bare.json"
    bare.write_text(json.dumps([entry]), encoding="utf-8")
    attributed = tmp_path / "attributed.json"
    attributed.write_text(
        json.dumps({"attribution": ATLAS, "entries": [entry]}), encoding="utf-8"
    )
    assert catalog.load_house_catalog(bare) == catalog.load_house_catalog(attributed)
    assert catalog.load_house_catalog(bare)[0].name == "X"


def test_notice_names_the_licences_and_trademarks():
    notice = " ".join((ROOT / "NOTICE.md").read_text(encoding="utf-8").split())
    assert ATLAS in notice
    assert "GNU General Public License, version 3" in notice
    assert "Paradox Interactive AB and are used with permission." in notice
    assert "GNU GENERAL PUBLIC LICENSE" in (ROOT / "LICENSE").read_text(
        encoding="utf-8"
    )


async def test_saga_picker_footer_shows_help_at_the_right():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
        await wait_until(pilot, lambda: "? Help" in screen_lines(app)[-1])
        footer = screen_lines(app)[-1]
        assert footer.index("q Quit") < footer.index("? Help")
        assert footer.index("? Help") < footer.index("^p palette")
        # Right-justified: a gap between Quit and Help.
        assert " " * 10 in footer[footer.index("q Quit") : footer.index("? Help")]


async def _open_about(pilot, app) -> None:
    """? on the saga picker, then Help's About this App (About
    moved into Help)."""
    await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))
    await pilot.press("question_mark")
    await wait_until(pilot, lambda: isinstance(app.screen, HelpScreen))
    topics = app.screen.query_one("#help-topics", OptionList)
    topics.highlighted = topics.get_option_index("ref:about")
    await wait_until(pilot, lambda: app.screen.topic_id == "about")


async def test_help_holds_about_and_escape_shuts_it():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(120, 45)) as pilot:
        await _open_about(pilot, app)
        await wait_until(
            pilot,
            lambda: "Licences, credits and trademarks" in "\n".join(screen_lines(app)),
        )
        assert "Armarius v" in "\n".join(screen_lines(app))

        await pilot.press("escape")
        await wait_until(pilot, lambda: isinstance(app.screen, SagaPickerScreen))


async def test_about_shows_the_attribution_further_down():
    app = ArsMagicaManagerApp()
    async with app.run_test(size=(140, 70)) as pilot:
        await _open_about(pilot, app)
        page = app.screen.query_one("#help-scroll")
        await wait_until(pilot, lambda: page.max_scroll_y > 0)
        page.scroll_end(animate=False)
        await wait_until(
            pilot, lambda: "licensed by Trident" in "\n".join(screen_lines(app))
        )
