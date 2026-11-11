"""The desktop's themes, by name: Scriptorum and Scriptorum Dark, and a
House theme for each House that has one.

A theme is its palette (shared data, `style.palettes`) and its drafting
twin, the group the Settings window lists it under (the House family, or
Scriptorum's own) and its look (families.py), which paints its pages and
carries its House's mark. The registry is a plain tuple read in order: the Settings
window lists it, and a page asks which theme a palette belongs to
(`of_palette`), so a new House theme appears everywhere once it is added
here.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ...artwork import SYMBOLS
from ...style.palettes import (
    BJORNAER,
    BONISAGUS,
    CRIAMON,
    DRAFTING,
    DRAFTING_DARK,
    EX_MISCELLANEA,
    FLAMBEAU,
    GUERNICUS,
    IN_CREATION,
    JERBITON,
    MERCERE,
    MERINITA,
    SCRIPTORUM,
    SCRIPTORUM_DARK,
    TREMERE,
    TYTALUS,
    VERDITIUS,
    Palette,
)
from . import families
from .families import Look

#: The groups the themes are listed under, in order: Scriptorum's own,
#: then the three House families (DE p. 12).
SCRIPTORUM_GROUP = "Scriptorum"
TRUE_LINEAGES = "True Lineages"
MYSTERY_CULTS = "Mystery Cults"
SOCIETATES = "Societates"
GROUPS = (SCRIPTORUM_GROUP, TRUE_LINEAGES, MYSTERY_CULTS, SOCIETATES)


@dataclass(frozen=True)
class Theme:
    """One theme the desktop can be drawn in."""

    #: Its colours In Play.
    palette: Palette
    #: Its colours for a record In Creation (its drafting twin).
    drafting: Palette
    #: The group it is listed under (GROUPS).
    group: str
    #: How it paints a page (families.py): Scriptorum's own look, or a
    #: House family's form with the House's texture and mark.
    look: Look
    #: A few words on its look, for the Settings window.
    blurb: str = ""

    @property
    def name(self) -> str:
        return self.palette.name

    @property
    def mark(self) -> Path | None:
        """Its House's mark (an SVG in currentColor), or None."""
        return self.look.mark


def house_mark(house: str) -> Path:
    """The SVG of `house`'s symbol (Guernicus's is the Quaesitor's)."""
    name = "quaesitor" if house == "guernicus" else house
    return SYMBOLS / "houses" / f"{name}.svg"


#: Scriptorum's look, shared by its two themes and a printed page.
SCRIPTORUM_LOOK = Look()

THEMES: tuple[Theme, ...] = (
    Theme(
        SCRIPTORUM,
        DRAFTING,
        SCRIPTORUM_GROUP,
        SCRIPTORUM_LOOK,
        "Aged parchment and iron gall ink",
    ),
    Theme(
        SCRIPTORUM_DARK,
        DRAFTING_DARK,
        SCRIPTORUM_GROUP,
        SCRIPTORUM_LOOK,
        "Vellum by candlelight",
    ),
    Theme(
        BONISAGUS,
        IN_CREATION[BONISAGUS.name],
        TRUE_LINEAGES,
        families.Bonisagus(house_mark("bonisagus")),
        "Clean vellum, lapis ink and the crossed keys",
    ),
    Theme(
        GUERNICUS,
        IN_CREATION[GUERNICUS.name],
        TRUE_LINEAGES,
        families.Guernicus(house_mark("guernicus")),
        "Veined marble, indigo and the bronze scales",
    ),
    Theme(
        MERCERE,
        IN_CREATION[MERCERE.name],
        TRUE_LINEAGES,
        families.Mercere(house_mark("mercere")),
        "Folded letters, the cap, coin and triangle",
    ),
    Theme(
        TREMERE,
        IN_CREATION[TREMERE.name],
        TRUE_LINEAGES,
        families.Tremere(house_mark("tremere")),
        "Iron by night and Roman flagstones",
    ),
    Theme(
        BJORNAER,
        IN_CREATION[BJORNAER.name],
        MYSTERY_CULTS,
        families.Bjornaer(house_mark("bjornaer")),
        "A stitched hide, fur and feathers, pine and the cone",
    ),
    Theme(
        CRIAMON,
        IN_CREATION[CRIAMON.name],
        MYSTERY_CULTS,
        families.Criamon(house_mark("criamon")),
        "A cave's dark, bone-pale ink and the Eye of Time",
    ),
    Theme(
        MERINITA,
        IN_CREATION[MERINITA.name],
        MYSTERY_CULTS,
        families.Merinita(house_mark("merinita")),
        "Oak leaves at twilight, green-silver and heather",
    ),
    Theme(
        VERDITIUS,
        IN_CREATION[VERDITIUS.name],
        MYSTERY_CULTS,
        families.Verditius(house_mark("verditius")),
        "A forge by night, the five rings, gems and tools",
    ),
    Theme(
        EX_MISCELLANEA,
        IN_CREATION[EX_MISCELLANEA.name],
        SOCIETATES,
        families.ExMiscellanea(house_mark("ex_miscellanea")),
        "Patchwork pages in mist, the crooked staff, motley pennants",
    ),
    Theme(
        FLAMBEAU,
        IN_CREATION[FLAMBEAU.name],
        SOCIETATES,
        families.Flambeau(house_mark("flambeau")),
        "Embers and scorch, flame and crimson, the hourglass",
    ),
    Theme(
        JERBITON,
        IN_CREATION[JERBITON.name],
        SOCIETATES,
        families.Jerbiton(house_mark("jerbiton")),
        "Cream vellum and a tapestry's weave, purple and teal",
    ),
    Theme(
        TYTALUS,
        IN_CREATION[TYTALUS.name],
        SOCIETATES,
        families.Tytalus(house_mark("tytalus")),
        "Storm and sea mist, the spira, violet set against green",
    ),
)

#: Each theme by its name, and by the name of its drafting twin.
_BY_NAME: dict[str, Theme] = {
    **{theme.name: theme for theme in THEMES},
    **{theme.drafting.name: theme for theme in THEMES},
}


def named(name: str | None) -> Theme | None:
    """The theme called `name`, or None when there is none."""
    return _BY_NAME.get(name or "")


def of_palette(p: Palette) -> Theme:
    """The theme palette `p` is drawn from (In Play or In Creation);
    Scriptorum's for a palette no theme has (a printed page's)."""
    return _BY_NAME.get(p.name, THEMES[0])


def for_mode(theme: Theme, in_creation: bool) -> Palette:
    """`theme`'s palette for a record in that mode."""
    return theme.drafting if in_creation else theme.palette


def look(p: Palette) -> Look:
    """How a page in palette `p` is painted: its theme's look."""
    return of_palette(p).look
