"""The package stands alone, and each part of it loads and draws."""

import ast
import os
import subprocess
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src" / "armarius_style"
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _imports(path: Path) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            names |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_only_the_front_end_parts_import_a_ui_library():
    wrong = []
    for path in SRC.rglob("*.py"):
        found = _imports(path)
        if "ars_magica_manager" in found:
            wrong.append(f"{path.name} imports Armarius")
        allowed = (
            {"PySide6"}
            if "desktop" in path.parts
            else {"textual"}
            if path.name == "terminal.py"
            else set()
        )
        ui = found & {"PySide6", "textual", "rich"}
        if ui - allowed:
            wrong.append(f"{path.name} imports {sorted(ui - allowed)}")
    assert not wrong, wrong


def test_the_plain_modules_load_with_no_ui_library():
    code = (
        "import sys; import armarius_style.palettes, armarius_style.fonts;"
        "assert not {'PySide6', 'textual'} & set(sys.modules)"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_every_font_is_bundled_with_its_licence():
    from armarius_style import fonts

    for paths in fonts.FONTS.values():
        assert all(path.is_file() for path in paths)
    assert (fonts.ASSETS / "fonts" / "EBGaramond-OFL.txt").is_file()
    assert (fonts.ASSETS / "fonts" / "UncialAntiqua-OFL.txt").is_file()


def test_each_drafting_palette_has_every_colour():
    from armarius_style import palettes as pal

    for palette in pal.PALETTES:
        drafting = pal.for_mode(palette, True)
        assert drafting.ruled
        assert set(drafting.colours) == set(palette.colours)
        assert pal.for_mode(palette, False) is palette
    assert set(pal.SCRIPTORUM.colours) == set(pal.SCRIPTORUM_DARK.colours)


async def test_the_app_css_parses_under_both_themes():
    pytest.importorskip("textual")
    from armarius_style import terminal
    from textual.app import App

    class Sample(App[None]):
        CSS = terminal.APP_CSS

        def get_theme_variable_defaults(self) -> dict[str, str]:
            return terminal.app_variable_defaults(self.current_theme)

        def on_mount(self) -> None:
            self.register_theme(terminal.SCRIPTORUM)
            self.register_theme(terminal.SCRIPTORUM_DARK)

    app = Sample()
    async with app.run_test() as pilot:
        for name in ("scriptorum", "scriptorum-dark"):
            app.theme = name
            await pilot.pause()
            assert app.theme == name


def test_every_page_piece_paints():
    pytest.importorskip("PySide6")
    from armarius_style import fonts, palettes
    from armarius_style.desktop import frame, gilding, ornaments, paper, pieces
    from armarius_style.desktop.fonts import register_fonts
    from armarius_style.desktop.illumination import IlluminatedInitial
    from armarius_style.desktop.sheet import style_sheet
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    app = QApplication.instance() or QApplication([])
    assert register_fonts() == []
    for palette in (*palettes.PALETTES, palettes.DRAFTING):
        app.setStyleSheet(style_sheet(palette, fonts.SERIF))  # pyright: ignore
        window = QWidget()
        column = QVBoxLayout(window)
        card = pieces.Card(palette, edge=palette["text-success"])
        card.column.addWidget(pieces.text("Fresh", palette["foreground"]))
        for piece in (
            frame.WindowButtons(window, palette),
            ornaments.Headpiece(palette),
            pieces.display_name("Valnastium", palette),
            IlluminatedInitial("V", palette),
            pieces.chapter_title("Vis Stocks", palette),
            ornaments.InspectorFrame("Gloss", palette),
            pieces.card_grid([card]),
            pieces.chip("Unhurt", palette["label"]),
            pieces.badge("Major", palette["heading"], palette),
            pieces.scrolling_page(palette, ornaments.ShortRule(palette)),
        ):
            column.addWidget(piece)
        window.resize(500, 900)
        assert not window.grab().isNull()
        assert not paper.paper(palette).isNull()
        assert gilding.wash(palette, 0, 100) is not None
        window.close()
