"""The Scriptorum palettes, as plain data: aged parchment and iron gall
ink, and a candle in a stone scriptorium, each with its drafting vellum, and
the pigments that are the same in either.

No UI library is imported here. A palette is a dict of the names the
markup and the drawing code use ($label, $text-error...); terminal.py
holds the same colours as Textual themes, and desktop/ draws with them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


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
        # Loyalty above and below zero: apart in lightness, so red-green
        # colour blindness still tells them apart, and unlike any realm's
        # colour.
        "loyalty-high": "#1F6F78",
        "loyalty-low": "#D77A93",
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
        "loyalty-high": "#4FB3B8",
        "loyalty-low": "#F2A0B5",
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

#: The pigments of things drawn on a fight's and a siege's page and on the
#: season medallions (gui/conflicts.py, gui/medallions.py): stone, timber,
#: steel, water, wax and glass are their own colours in either theme.
DRAWN = {
    "lead": "#2A2420",
    "copper": "#5E4410",
    "glass-gold": "#F2C230",
    "turquoise": "#3FA7A0",
    "enamel-white": "#F4F1E8",
    "engraving": "#7A5A14",
    "timber": "#4A3324",
    "snow": "#FFFFFF",
    "stone": "#CDBFA6",
    "stone-dark": "#8C7B62",
    "stone-light": "#E6DAC2",
    "seal-ink": "#3B2414",
    "seal-gold-light": "#F2E3B6",
    "seal-gold": "#C9A55A",
    "seal-grey-light": "#E8DCCB",
    "seal-grey": "#8C7E6E",
    "medium-wound": "#A35A1A",
    "steel-light": "#E9E7E1",
    "steel": "#8C939B",
    "river": "#6E8FB0",
    "river-light": "#A9C1D6",
}

#: Each season's pigments in each set of medallions, by set.
SEASON_PIGMENTS: dict[str, dict[str, Any]] = {
    "glass": {
        "Spring": ("#8FC27A", "#5E9A4C", "#E2C04A", "#D9718C"),
        "Summer": ("#4F86C6", "#2E5E9E", "#C8352B", "#F2C230"),
        "Autumn": ("#D99A45", "#A8642A", "#7A2A22", "#6B3A86"),
        "Winter": ("#3E62A3", "#26437A", "#D9E3EE", "#EEF4FA"),
    },
    "wax": {
        "Spring": "#3F7A3A",
        "Summer": "#B0281E",
        "Autumn": "#8A4A1C",
        "Winter": "#2B4C7E",
    },
    "enamel": {
        "Spring": "#2E7D5B",
        "Summer": "#1F4E9C",
        "Autumn": "#7A2E1E",
        "Winter": "#1B2F66",
    },
    "sky": {
        "Spring": ("#9CC3E0", "#E8F0E0", "#7FA857"),
        "Summer": ("#3F7EC2", "#BFD8EE", "#C9A949"),
        "Autumn": ("#B9A27A", "#EAD9B6", "#8E6A2E"),
        "Winter": ("#7A8FA8", "#D9DFE6", "#F2F2F0"),
    },
    "crowns": {"Spring": "#9CCB6B", "Summer": "#3F7A3A", "Autumn": "#B5652A"},
    "scene": {
        "Spring": "#D9718C",
        "Summer": "#F2C230",
        "Autumn": "#6B3A86",
        "Winter": "#FFFFFF",
    },
    "wash": {
        "Spring": "#7FA857",
        "Summer": "#D9A62E",
        "Autumn": "#B5652A",
        "Winter": "#6F8FB4",
    },
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


#: How strongly a chosen row's gold wash starts, at its left (0 to 255); a
#: row under the pointer takes a fainter one.
WASH, HOVER_WASH = 70, 22


def wash_style(p: Palette, alpha: int = WASH) -> str:
    """A chosen row's background in a style sheet: the accent's gold at
    `alpha` at its left, fading to nothing at its right."""
    gilt = p["accent"].lstrip("#")
    return (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0,"
        f" stop:0 #{alpha:02X}{gilt}, stop:1 #00{gilt})"
    )


#: Murex purple, the drop-downs' ink (choices.py): on parchment, and
#: lighter on the dark page.
MUREX = ("#6B3F9E", "#B993E6")


def murex(p: Palette) -> str:
    """The drop-downs' purple in palette `p`."""
    return MUREX[p.dark]


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
    # A fur is painted as its ground and spots (arms.FURS); this is the
    # ground, for anything that shows one colour for it.
    "Ermine": "#f1ede2",
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
