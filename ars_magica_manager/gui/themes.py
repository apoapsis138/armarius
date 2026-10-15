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
    #: Whether the paper is ruled, as a draft is (In Creation).
    ruled: bool = False

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
        # An aura's realm.
        "realm-Magic": "#2F5D8A",
        "realm-Divine": "#B8860B",
        "realm-Faerie": "#4A7A5C",
        "realm-Infernal": "#8B0000",
        # A book's binding: the brown its leather is tanned toward, the gilt
        # of its tooling, and the light and shade on its bands.
        "leather": "#4A3324",
        "gilt": "#E8D9A8",
        "binding-light": "#FFFFFF",
        "binding-ink": "#000000",
        # A bookcase's back wall and its planks.
        "shelf-back": "#644A20",
        "shelf-plank": "#705220",
        # The page's paper: its darker flecks and fibres, its lighter grain,
        # and the shade its edges and every shadow fall into.
        "paper-fleck": "#6E5032",
        "paper-sheen": "#FFFFFF",
        "shadow": "#1E0F00",
        # The soft line under and beside a button, a shadow it casts.
        "button-shadow": "#A39D97",
        # The bond's three Cords, in their metals.
        "cord-golden": "#B8860B",
        "cord-silver": "#8C939B",
        "cord-bronze": "#9C5B26",
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
        "realm-Magic": "#6E9BD1",
        "realm-Divine": "#E3C25A",
        "realm-Faerie": "#74B08A",
        "realm-Infernal": "#F87171",
        # A book's binding: the brown its leather is tanned toward, the gilt
        # of its tooling, and the light and shade on its bands.
        "leather": "#4A3324",
        "gilt": "#E8D9A8",
        "binding-light": "#FFFFFF",
        "binding-ink": "#000000",
        "shelf-back": "#2C220E",
        "shelf-plank": "#644D1F",
        # Vellum by candlelight: dark flecks, pale fibres, a black shade.
        "paper-fleck": "#000000",
        "paper-sheen": "#C8BEA0",
        "shadow": "#000000",
        "button-shadow": "#3A4150",
        "cord-golden": "#E3C25A",
        "cord-silver": "#C3CAD2",
        "cord-bronze": "#C9844A",
    },
)

PALETTES = (SCRIPTORUM, SCRIPTORUM_DARK)


def _drafting(base: Palette, colours: dict[str, str]) -> Palette:
    return Palette(
        f"{base.name} Drafting", base.dark, {**base.colours, **colours}, ruled=True
    )


#: A record In Creation is drawn on drafting vellum: the same inks on a
#: cooler, greyer skin, ruled.
DRAFTING = _drafting(
    SCRIPTORUM,
    {
        "background": "#ECEEE7",
        "surface": "#E1E5DC",
        "panel": "#CBD4CA",
        "rule": "#A9B5AD",
        "selection": "#D8DFD4",
        "label": "#4E5853",
        "dim": "#5C6560",
        "paper-fleck": "#3C4E56",
        "shadow": "#0E1A20",
        "button-shadow": "#98A09C",
    },
)

DRAFTING_DARK = _drafting(
    SCRIPTORUM_DARK,
    {
        "background": "#0F1A1C",
        "surface": "#16252A",
        "panel": "#1E343A",
        "rule": "#2F4A50",
        "button-shadow": "#2F4A50",
        "selection": "#1A2D31",
        "label": "#9AA39C",
        "paper-sheen": "#A8BAC2",
    },
)

#: Each palette's In Creation counterpart, by name.
IN_CREATION: dict[str, Palette] = {
    SCRIPTORUM.name: DRAFTING,
    SCRIPTORUM_DARK.name: DRAFTING_DARK,
}


def for_mode(p: Palette, in_creation: bool) -> Palette:
    """`p` as a record in that mode is drawn: drafting vellum while it is
    In Creation, `p` itself In Play."""
    return IN_CREATION.get(p.name, p) if in_creation else p


#: An illuminated initial's pigments (illumination.py): the same in either
#: theme, as a painted letter is the same colours on any page.
PIGMENTS = {
    "lapis": "#1E3F8A",
    "lapis-deep": "#132A5E",
    "vermilion": "#B3261E",
    "vermilion-deep": "#7E1712",
    "verdigris": "#2F7A55",
    "verdigris-light": "#A9D8B8",
    "ink": "#2A1A0C",
    "lead-white": "#FBF6E9",
    # The knotwork band's ground, darker than the lapis so the gold shows.
    "knot-ground": "#10203F",
    "gold": "#E3B341",
    "gold-light": "#FFE9A0",
    "gold-dark": "#7A5212",
    "garnet-light": "#F08A80",
    "glow": "#F2C94C",
}

#: Burnished gold along a gradient, (stop, colour): dark ochre, bright
#: yellow, a white glint, and back, so the gold seems to catch the light.
BURNISH = (
    (0.00, "#7A5212"),
    (0.18, "#C9971F"),
    (0.32, "#F7DA6A"),
    (0.40, "#FFF6C8"),
    (0.48, "#F2C94C"),
    (0.66, "#B07D18"),
    (0.80, "#E8BF45"),
    (0.90, "#FFE89A"),
    (1.00, "#8A5D14"),
)


def style_sheet(p: Palette, serif: str) -> str:
    """The whole window's Qt style sheet in palette `p`; `serif` is the
    headings' family (EB Garamond). The data font is the application's
    (window.py), not set here: a style sheet's font would override every
    widget's own (the fixed-pitch lists, the Arts' italic serif names)."""
    return f"""
    QWidget {{
        background: transparent;
        color: {p["foreground"]};
    }}
    QMenu, QToolTip, QDialog, QComboBox QAbstractItemView {{
        background: {p["background"]};
    }}
    QSplitter::handle {{ background: {p["rule"]}; }}
    QCheckBox::indicator {{
        width: 13px;
        height: 13px;
        border: 1px solid {p["label"]};
        border-radius: 2px;
        background: {p["background"]};
    }}
    QCheckBox::indicator:checked {{
        background: {p["primary"]};
        border-color: {p["primary"]};
    }}
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
    QComboBox#quiet {{
        background: transparent;
        border: none;
        border-bottom: 1px solid {p["rule"]};
        color: {p["label"]};
        font-family: "{serif}";
        font-size: 11pt;
        font-style: italic;
        padding: 1px 4px;
    }}
    QComboBox#quiet:hover {{ color: {p["heading"]}; }}
    QLineEdit, QPlainTextEdit {{
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        border-radius: 3px;
        padding: 3px 6px;
        selection-background-color: {p["selection"]};
        selection-color: {p["foreground"]};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border: 1px solid {p["accent"]};
    }}
    QPushButton {{
        font-family: "{serif}";
        font-size: 11pt;
        color: {p["label"]};
        background: transparent;
        border: 1px solid transparent;
        border-right-color: {p["button-shadow"]};
        border-bottom-color: {p["button-shadow"]};
        border-radius: 4px;
        padding: 2px 8px;
    }}
    QPushButton:hover {{
        color: {p["heading"]};
        background: {p["panel"]};
    }}
    QPushButton:disabled {{
        color: {p["dim"]};
        border-color: transparent;
    }}
    QDialog QPushButton {{ font-size: 12pt; padding: 3px 14px; }}
    QDialog QPushButton:default {{ color: {p["heading"]}; }}
    QPushButton#picker {{
        color: {p["foreground"]};
        background: {p["surface"]};
        border: 1px solid {p["rule"]};
        border-radius: 3px;
    }}
    QPushButton#picker:hover {{ border: 1px solid {p["accent"]}; }}
    QScrollArea {{ border: none; }}
    QScrollBar:vertical {{ background: transparent; width: 10px; }}
    QScrollBar::handle:vertical {{ background: {p["rule"]}; min-height: 24px; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; }}
    QScrollBar::handle:horizontal {{ background: {p["rule"]}; min-width: 24px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
    QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}
    QTableCornerButton::section {{ background: {p["surface"]}; border: none; }}
    """


#: The colour each heraldic tincture (arms.TINCTURES) is painted in, the
#: same in every theme: arms are the bearer's, not the theme's.
TINCTURES: dict[str, str] = {
    "Or": "#d4a72c",
    "Argent": "#f1ede2",
    "Gules": "#b8282e",
    "Azure": "#2556a8",
    "Vert": "#2e8540",
    "Sable": "#262322",
    "Purpure": "#6b3f9e",
}


#: The opening card's colours: gold and parchment on the dark of the hall,
#: whatever the theme, as a cover page would be.
OPENING_CARD: dict[str, str] = {
    "gold": "#e7c56a",
    "parchment": "#e9dcc0",
    "numbers": "#c9b98f",
    "button": "#d9b04a",
    "button-text": "#2a1d0a",
    "dark": "#1e1610",
    "darker": "#080604",
}
