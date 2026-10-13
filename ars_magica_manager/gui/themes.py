"""The desktop version's Scriptorum themes: the terminal's palettes (aged
parchment and iron gall ink; a candle in a stone scriptorium), as Qt
style sheets.

The colours are the terminal themes' own, so the two front-ends look like
one app; a palette is a dict of the same names the app's markup uses
($label, $text-error...), which markup_html reads too.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Palette:
    name: str
    dark: bool
    colours: dict[str, str]

    def __getitem__(self, key: str) -> str:
        return self.colours[key]


SCRIPTORUM = Palette(
    "Scriptorum",
    dark=False,
    colours={
        "background": "#F4EBE1",
        "surface": "#EDE0CB",
        "panel": "#E0CBA0",
        "foreground": "#2C221E",
        "primary": "#8B0000",
        "accent": "#B8860B",
        "heading": "#8B0000",
        "label": "#5F4F44",
        "rule": "#C9B48A",
        "dim": "#685849",
        "text-error": "#8B0000",
        "text-warning": "#7A4206",
        "text-success": "#4A6741",
        "text-accent": "#6B4E06",
        "selection": "#E3D2B1",
        # A season's kind on the timeline, in manuscript pigments.
        "season-lab": "#A23B2A",
        "season-study": "#2F5D8A",
        "season-writing": "#4A7A5C",
        "season-work": "#A87A22",
        "season-adventure": "#6E4A7E",
        "season-rest": "#8A7F72",
        "season-other": "#A39580",
    },
)

SCRIPTORUM_DARK = Palette(
    "Scriptorum Dark",
    dark=True,
    colours={
        "background": "#15171C",
        "surface": "#1D2027",
        "panel": "#262B35",
        "foreground": "#D9CBA3",
        "primary": "#FCD34D",
        "accent": "#D4AF37",
        "heading": "#FCD34D",
        "label": "#A39A84",
        "rule": "#3A4150",
        "dim": "#9A937F",
        "text-error": "#F87171",
        "text-warning": "#F0954A",
        "text-success": "#6FA287",
        "text-accent": "#D4AF37",
        "selection": "#2B2612",
        "season-lab": "#C8644F",
        "season-study": "#5F8CC4",
        "season-writing": "#62A07A",
        "season-work": "#C99A3E",
        "season-adventure": "#9A7AB6",
        "season-rest": "#7E7A70",
        "season-other": "#5F5B52",
    },
)

PALETTES = (SCRIPTORUM, SCRIPTORUM_DARK)


def style_sheet(p: Palette, serif: str) -> str:
    """The whole window's Qt style sheet in palette `p`; `serif` is the
    headings' family (EB Garamond). The data font is the application's
    (window.py), not set here: a style sheet's font would override every
    widget's own (the fixed-pitch lists, the Arts' italic serif names)."""
    return f"""
    QWidget {{
        background: {p["background"]};
        color: {p["foreground"]};
    }}
    QSplitter::handle {{ background: {p["rule"]}; }}
    QTreeWidget, QListWidget {{
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        outline: none;
    }}
    QTreeWidget::item, QListWidget::item {{ padding: 3px 4px; }}
    QTreeWidget::item:selected, QListWidget::item:selected {{
        background: {p["selection"]};
        color: {p["foreground"]};
        border-left: 2px solid {p["primary"]};
    }}
    QTabWidget::pane {{
        border: none;
        border-top: 1px solid {p["rule"]};
    }}
    QTabBar::tab {{
        font-family: "{serif}";
        font-size: 13pt;
        background: transparent;
        color: {p["label"]};
        padding: 4px 12px;
        border-bottom: 2px solid transparent;
    }}
    QTabBar::tab:selected {{
        color: {p["heading"]};
        border-bottom: 2px solid {p["heading"]};
    }}
    QTabBar::tab:hover {{ color: {p["foreground"]}; }}
    QLabel#sectionTitle {{
        font-family: "{serif}";
        font-size: 14pt;
        font-weight: 600;
        color: {p["foreground"]};
        border-bottom: 1px solid {p["rule"]};
        padding-bottom: 2px;
    }}
    QLabel#sheetName {{
        font-family: "{serif}";
        font-size: 24pt;
        color: {p["foreground"]};
    }}
    QFrame#details {{
        background: {p["panel"]};
        border-radius: 4px;
    }}
    QFrame#details QLabel {{ background: transparent; }}
    QPushButton#crumb {{
        font-family: "{serif}";
        font-size: 12.5pt;
        color: {p["label"]};
        background: transparent;
        border: none;
        padding: 2px 4px;
    }}
    QPushButton#crumb:hover {{ color: {p["heading"]}; }}
    QPushButton#crumb:disabled {{ color: {p["foreground"]}; }}
    QComboBox {{
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        padding: 3px 6px;
    }}
    QScrollArea {{ border: none; }}
    QScrollBar:vertical {{ background: {p["background"]}; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {p["rule"]}; min-height: 24px; }}
    QScrollBar:horizontal {{ background: {p["background"]}; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: {p["rule"]}; min-width: 24px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QTableCornerButton::section {{ background: {p["surface"]}; border: none; }}
    """
