"""The look: each part of it loads and draws."""

import os
import subprocess
import sys

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_the_plain_modules_load_with_no_ui_library():
    code = (
        "import sys; import ars_magica_manager.style.palettes, ars_magica_manager.style.fonts;"
        "assert not {'PySide6', 'textual'} & set(sys.modules)"
    )
    subprocess.run([sys.executable, "-c", code], check=True)


def test_every_font_is_bundled_with_its_licence():
    from ars_magica_manager.style import fonts

    for paths in fonts.FONTS.values():
        assert all(path.is_file() for path in paths)
    assert (fonts.ASSETS / "fonts" / "EBGaramond-OFL.txt").is_file()
    assert (fonts.ASSETS / "fonts" / "UncialAntiqua-OFL.txt").is_file()


def test_each_drafting_palette_has_every_colour():
    from ars_magica_manager.style import palettes as pal

    for palette in pal.PALETTES:
        drafting = pal.for_mode(palette, True)
        assert drafting.ruled
        assert set(drafting.colours) == set(palette.colours)
        assert pal.for_mode(palette, False) is palette
    assert set(pal.SCRIPTORUM.colours) == set(pal.SCRIPTORUM_DARK.colours)


async def test_the_app_css_parses_under_both_themes():
    pytest.importorskip("textual")
    from textual.app import App

    from ars_magica_manager.tui import style as terminal

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
    from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

    from ars_magica_manager.gui.style import frame, gilding, ornaments, paper, pieces
    from ars_magica_manager.gui.style.fonts import register_fonts
    from ars_magica_manager.gui.style.illumination import IlluminatedInitial
    from ars_magica_manager.gui.style.sheet import style_sheet
    from ars_magica_manager.style import fonts, palettes

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
