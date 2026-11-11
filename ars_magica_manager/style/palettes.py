"""The Scriptorum palettes, as plain data: aged parchment and iron gall
ink, and a candle in a stone scriptorium, each with its drafting vellum, and
the pigments that are the same in either.

No UI library is imported here. A palette is a dict of the names the
markup and the drawing code use ($label, $text-error...); terminal.py
holds the same colours as Textual themes, and desktop/ draws with them.
"""

from __future__ import annotations

import colorsys
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


# -- House themes' colours ---------------------------------------------------


def luminance(colour: str) -> float:
    """`colour`'s relative luminance (WCAG 2), 0 for black to 1 for white."""
    channels = []
    for i in (1, 3, 5):
        c = int(colour[i : i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(a: str, b: str) -> float:
    """The contrast ratio of two colours (WCAG 2), 1 to 21."""
    light, dark = sorted((luminance(a), luminance(b)), reverse=True)
    return (light + 0.05) / (dark + 0.05)


def hue(colour: str) -> float:
    """`colour`'s hue, 0 to 1 round the colour wheel."""
    rgb = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return colorsys.rgb_to_hls(*rgb)[0]


def _hls(colour: str) -> tuple[float, float, float]:
    rgb = [int(colour[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return colorsys.rgb_to_hls(*rgb)


def _from_hls(h: float, lightness: float, s: float) -> str:
    rgb = colorsys.hls_to_rgb(h, min(max(lightness, 0.0), 1.0), s)
    return "#" + "".join(f"{round(c * 255):02X}" for c in rgb)


def mixed(a: str, b: str, t: float) -> str:
    """The colour `t` of the way from `a` to `b` (as `b` laid over `a` at
    opacity `t`)."""
    channels = (
        round(int(a[i : i + 2], 16) * (1 - t) + int(b[i : i + 2], 16) * t)
        for i in (1, 3, 5)
    )
    return "#" + "".join(f"{c:02X}" for c in channels)


def retuned(colour: str, ground: str, ratio: float) -> str:
    """`colour` in its own hue, made lighter or darker only as far as it
    must be to stand `ratio` against `ground` (or as near as it can)."""
    if contrast(colour, ground) >= ratio:
        return colour
    h, lightness, s = _hls(colour)
    step = 0.01 if luminance(ground) < 0.18 else -0.01
    best = colour
    while 0.0 <= lightness <= 1.0:
        lightness += step
        best = _from_hls(h, lightness, s)
        if contrast(best, ground) >= ratio:
            return best
    return best


#: The colours that mean something (a season's kind, a realm, Loyalty, an
#: error or warning): every theme keeps their hues, retuned only for
#: contrast against its own page.
MEANINGFUL = (
    "text-error",
    "text-warning",
    "text-success",
    "season-lab",
    "season-study",
    "season-writing",
    "season-work",
    "season-adventure",
    "season-rest",
    "season-other",
    "realm-Magic",
    "realm-Divine",
    "realm-Faerie",
    "realm-Infernal",
    "loyalty-high",
    "loyalty-low",
)

#: Text colours that must stand 4.5:1 against the page.
TEXT = ("foreground", "label", "heading", "text-error", "text-warning", "text-success")
#: The contrast text keeps against its page (WCAG AA).
READABLE = 4.5
#: The contrast a House theme's text colours are given against its plain
#: page: above READABLE, so a texture and a watermark have room under it.
HEADROOM = 5.5


def house(name: str, base: Palette, colours: dict[str, str]) -> Palette:
    """A House theme's palette: `base` (Scriptorum or Scriptorum Dark, for
    its mood) with `colours` laid over it, as a prototype is copied and
    changed. Its meaningful colours keep `base`'s hues, each retuned only
    as far as it needs to stand against the new page as well as it did on
    `base`'s (text at least HEADROOM)."""
    merged = {**base.colours, **colours}
    ground = merged["background"]
    for key in MEANINGFUL:
        if key in colours:
            continue
        before = contrast(base[key], base["background"])
        wanted = max(min(before, 7.0), HEADROOM if key in TEXT else 0.0)
        merged[key] = retuned(base[key], ground, wanted)
    return Palette(name, base.dark, merged)


#: The colours a draft's page changes: its skin, rules and the inks of its
#: labels; the text, headings and meaningful colours stay.
_COOLED = (
    "background",
    "surface",
    "panel",
    "rule",
    "selection",
    "label",
    "dim",
    "paper-fleck",
    "shadow",
    "button-shadow",
)
#: The hue a draft cools toward: the grey-green of drafting vellum.
_COOL_HUE = 150 / 360


def cooled(p: Palette) -> Palette:
    """`p`'s In Creation twin, made from its own colours as DRAFTING is
    from SCRIPTORUM: its page turned toward cool grey-green and greyer,
    ruled; its inks, headings and meaningful colours as they were."""
    colours = dict(p.colours)
    for key in _COOLED:
        h, lightness, s = _hls(p[key])
        # Halfway round to the cool hue, the shorter way, and half as rich.
        turn = ((_COOL_HUE - h + 0.5) % 1.0) - 0.5
        colours[key] = _from_hls((h + turn * 0.6) % 1.0, lightness, s * 0.45)
    for key in ("label", "dim"):
        colours[key] = retuned(colours[key], colours["background"], READABLE)
    return Palette(f"{p.name} Drafting", p.dark, colours, ruled=True)


#: House Bonisagus: the theorists' and Trianoma's House, keepers of the
#: Order (DE p. 13; Houses of Hermes: True Lineages p. 4, two keys
#: crossed). A clean, cool vellum and lapis ink, gold for the keys.
BONISAGUS = house(
    "Bonisagus",
    SCRIPTORUM,
    {
        "background": "#F1EEE5",
        "surface": "#E8E3D4",
        "panel": "#D9D2BC",
        "foreground": "#1D2230",
        "primary": "#1E3F8A",
        "accent": "#A07C1E",
        "heading": "#1E3F8A",
        "label": "#4A5062",
        "rule": "#C4BCA4",
        "dim": "#5A5F6E",
        "text-accent": "#6A5412",
        "selection": "#DCE1EA",
        "paper-fleck": "#465066",
        "paper-sheen": "#FFFFFF",
        "shadow": "#0A1428",
        "button-shadow": "#A3A29C",
    },
)

#: House Criamon: seekers of the Enigma, who mark their skin with arcane
#: signs and hold that time is a circle (DE p. 13; Houses of Hermes:
#: Mystery Cults p. 44, the Loop of the Infinite in the Eye of Time; the
#: domus magna is the Cave of Twisting Shadows). A cave's violet dark,
#: bone-pale ink and the amber of a lamp.
CRIAMON = house(
    "Criamon",
    SCRIPTORUM_DARK,
    {
        "background": "#15131C",
        "surface": "#1D1A26",
        "panel": "#272333",
        "foreground": "#DDD5C4",
        "primary": "#E3B07A",
        "accent": "#B98A4E",
        "heading": "#E3B07A",
        "label": "#A99DB5",
        "rule": "#3B344D",
        "dim": "#9A90A7",
        "text-accent": "#CFA36C",
        "selection": "#2D2740",
        "paper-fleck": "#000000",
        "paper-sheen": "#B9AECB",
        "shadow": "#000000",
        "button-shadow": "#3B344D",
    },
)

#: House Tytalus: masters of conflict, growing through struggle (DE p. 17;
#: Houses of Hermes: Societates p. 71, "from conflict, growth", the spira
#: of four turns; Fudarus on its storm-beaten island in sea mist). Storm
#: slate, its headings and seal in Buliste's violet, a bright amethyst,
#: and its frame and rules in Harpax's green, a deep, dark verdigris: the
#: two claimants' colours set against each other in lightness as well as
#: hue, so they read as opposed to an eye that cannot tell the hues apart.
TYTALUS = house(
    "Tytalus",
    SCRIPTORUM_DARK,
    {
        "background": "#121619",
        "surface": "#1A1F23",
        "panel": "#232A2F",
        "foreground": "#D8D6CC",
        "primary": "#D4B6FF",
        "accent": "#28654F",
        "heading": "#D4B6FF",
        "label": "#9EA7AD",
        "rule": "#33404A",
        "dim": "#8F989E",
        "text-accent": "#8CC79A",
        "selection": "#2A2437",
        "paper-fleck": "#000000",
        "paper-sheen": "#A9B7C2",
        "shadow": "#000000",
        "button-shadow": "#33404A",
    },
)

#: House Guernicus: the Order's judges, a true lineage, "the law above the
#: will"; Guernicus an earth wizard, the House's roots in Rome (DE pp.
#: 14-15; Houses of Hermes: True Lineages pp. 35-36, the scales of justice
#: balanced on a sword). A Roman court by day: cool marble, iron-black
#: ink, indigo headings and the scales' bronze.
GUERNICUS = house(
    "Guernicus",
    SCRIPTORUM,
    {
        "background": "#ECEAE4",
        "surface": "#E2DFD6",
        "panel": "#D3CFC3",
        "foreground": "#1C1B1A",
        "primary": "#2E2A55",
        "accent": "#9C7A3C",
        "heading": "#2E2A55",
        "label": "#4C4A47",
        "rule": "#B9B4A8",
        "dim": "#5B5955",
        "text-accent": "#6B5222",
        "selection": "#DDDCE6",
        "paper-fleck": "#4A4A55",
        "paper-sheen": "#FFFFFF",
        "shadow": "#14121C",
        "button-shadow": "#A3A19B",
    },
)

#: House Mercere: the Redcaps, the Order's messengers, a true lineage (DE
#: p. 15; Houses of Hermes: True Lineages p. 78, a red cap with a yellow
#: circle inscribed with a blue triangle: duty, a coin for commerce, a
#: potsherd from a crossroads for travel). Road-dust parchment, the cap's
#: deep red for headings and the triangle's blue, a deep woad rather than
#: a bright sky, for frame and rules, the red far darker than the blue.
MERCERE = house(
    "Mercere",
    SCRIPTORUM,
    {
        "background": "#F2ECDD",
        "surface": "#E9E0CB",
        "panel": "#DCD0B4",
        "foreground": "#221C14",
        "primary": "#6E1414",
        "accent": "#4F78BA",
        "heading": "#6E1414",
        "label": "#55493A",
        "rule": "#C9BB98",
        "dim": "#645849",
        "text-accent": "#2F5596",
        "selection": "#DFE4EE",
        "paper-fleck": "#5A4A30",
        "paper-sheen": "#FFFFFF",
        "shadow": "#1E1408",
        "button-shadow": "#ABA28F",
    },
)

#: House Tremere: judgment, strategy and dignity, soldiers who hold war
#: inevitable, a true lineage (DE p. 16; Houses of Hermes: True Lineages
#: p. 110, Mars incised with a square, the square a flagstone of a Roman
#: road). A war room by night: iron, pale steel headings and a dried-blood
#: rust, steel far lighter than rust; cold where its rival Tytalus storms.
TREMERE = house(
    "Tremere",
    SCRIPTORUM_DARK,
    {
        "background": "#15171B",
        "surface": "#1C1F24",
        "panel": "#262A31",
        "foreground": "#D9DCDF",
        "primary": "#C8D3E0",
        "accent": "#7A3328",
        "heading": "#C8D3E0",
        "label": "#9AA1AA",
        "rule": "#343A42",
        "dim": "#8C939C",
        "text-accent": "#D9907F",
        "selection": "#2A2E36",
        "paper-fleck": "#000000",
        "paper-sheen": "#AEB8C4",
        "shadow": "#000000",
        "button-shadow": "#343A42",
    },
)

#: House Bjornaer: the shapechangers, each with a heartbeast, a cult of
#: the ancestors whose spirits give the power to change shape (DE p. 13;
#: Houses of Hermes: Mystery Cults p. 7, the cone, which casts a
#: triangle's shadow or a circle's but never both; the Founder Birna, "she-
#: bear"). Daylight on a pale hide: pine headings and a bear-brown ochre,
#: the pine far darker than the ochre.
BJORNAER = house(
    "Bjornaer",
    SCRIPTORUM,
    {
        "background": "#EEEADF",
        "surface": "#E4DECF",
        "panel": "#D6CEBA",
        "foreground": "#25211B",
        "primary": "#22402C",
        "accent": "#A9773C",
        "heading": "#22402C",
        "label": "#504A3F",
        "rule": "#BFB59E",
        "dim": "#5F584C",
        "text-accent": "#6B4719",
        "selection": "#DCE2D6",
        "paper-fleck": "#4A3F2E",
        "paper-sheen": "#FFFFFF",
        "shadow": "#14100A",
        "button-shadow": "#A8A08E",
    },
)

#: House Merinita: the House of faeries, as strange as what it studies,
#: turned to Arcadia by Quendalon (DE p. 16; Houses of Hermes: Mystery
#: Cults p. 75, an oak within a circle; the Founder a white-haired woman
#: dressed in green). Twilight in a faerie wood: moss-dark page,
#: moonlit green-silver headings and a heather violet, the green-silver far
#: lighter than the violet.
MERINITA = house(
    "Merinita",
    SCRIPTORUM_DARK,
    {
        "background": "#111813",
        "surface": "#18211A",
        "panel": "#212C23",
        "foreground": "#D8DDD0",
        "primary": "#CDE3BE",
        "accent": "#7E5E9C",
        "heading": "#CDE3BE",
        "label": "#9EAA98",
        "rule": "#2C3A2E",
        "dim": "#8E9A88",
        "text-accent": "#BBA4D8",
        "selection": "#262430",
        "paper-fleck": "#000000",
        "paper-sheen": "#AFC4A4",
        "shadow": "#000000",
        "button-shadow": "#2C3A2E",
    },
)

#: House Verditius: unsurpassed makers of enchanted items, craftsmen
#: first (DE p. 17; Houses of Hermes: Mystery Cults p. 107, a hand with a
#: ring on each finger, the five rings Verditius made; Hephaestus's
#: forge). A forge at night: soot, the rings' own gold for headings and a
#: hot copper, the gold far lighter than the copper.
VERDITIUS = house(
    "Verditius",
    SCRIPTORUM_DARK,
    {
        "background": "#17130F",
        "surface": "#201A15",
        "panel": "#2A231C",
        "foreground": "#DCD3C6",
        "primary": "#E6B866",
        "accent": "#8E4A2A",
        "heading": "#E6B866",
        "label": "#A69A8A",
        "rule": "#3A3029",
        "dim": "#978B7B",
        "text-accent": "#E29C70",
        "selection": "#2E241C",
        "paper-fleck": "#000000",
        "paper-sheen": "#C9B49A",
        "shadow": "#000000",
        "button-shadow": "#3A3029",
    },
)

#: House Ex Miscellanea: a large, diverse gathering of wizards of many
#: traditions, founded by Pralix (DE p. 14; Houses of Hermes: Societates
#: p. 101, the crooked staff; "the whole is composed of many parts"; Cad
#: Gadu an island in a mist-shrouded lake). Morning mist on the lake: a
#: warm linen page, the homespun the patchwork is sewn from (warm, so it
#: never reads as a draft's cool grey-green vellum), lake-slate headings
#: and a lichen ochre, the slate far darker than the ochre.
EX_MISCELLANEA = house(
    "Ex Miscellanea",
    SCRIPTORUM,
    {
        "background": "#EEE6DD",
        "surface": "#E4DACE",
        "panel": "#D6C9B9",
        "foreground": "#1F1D1B",
        "primary": "#24384E",
        "accent": "#A3884A",
        "heading": "#24384E",
        "label": "#504A42",
        "rule": "#C0B3A3",
        "dim": "#5F584F",
        "text-accent": "#6B5524",
        "selection": "#DCE1E8",
        "paper-fleck": "#4C4238",
        "paper-sheen": "#FFFFFF",
        "shadow": "#1A120A",
        "button-shadow": "#ABA290",
    },
)

#: The traditions gathered in Ex Miscellanea, one muted colour each, for
#: its pennants: moss, madder, woad, ochre, heather and stone, apart in
#: lightness as well as hue.
EX_MISCELLANEA_MOTLEY = (
    "#5E7A55",
    "#9C5F4A",
    "#46607E",
    "#B39A5C",
    "#76628E",
    "#8E8A7E",
)

#: House Flambeau: fire and destruction magic, the Order's knights, with a
#: tradition of honour and chivalry (DE p. 14; Houses of Hermes:
#: Societates p. 6, the hourglass; "Unto death, let us charge"). Embers
#: after a battle: an ember-black page, flame headings and a deep crimson,
#: the flame far lighter than the crimson.
FLAMBEAU = house(
    "Flambeau",
    SCRIPTORUM_DARK,
    {
        "background": "#1A1210",
        "surface": "#231916",
        "panel": "#2D211D",
        "foreground": "#E2D6CB",
        "primary": "#F2A65A",
        # Lifted from the deep crimson of blood (#6E1A12), which all but
        # vanishes on the ember-black, to a crimson a frame's rule shows in.
        "accent": "#8E2418",
        "heading": "#F2A65A",
        "label": "#AE9C90",
        "rule": "#3E2C26",
        "dim": "#A08E82",
        "text-accent": "#EE9A7A",
        "selection": "#33201A",
        "paper-fleck": "#000000",
        "paper-sheen": "#D9A27A",
        "shadow": "#000000",
        "button-shadow": "#3E2C26",
    },
)

#: House Jerbiton: the arts and the mundane world, custodians of a magical
#: culture from the cities of the Eastern Empire (DE p. 15; Houses of
#: Hermes: Societates p. 39, a pennant flown from a tower, often marked
#: with mercury's sign; "Beauty is all that pleases"). A Byzantine
#: scriptorium by day: fine cream vellum, imperial purple headings and a
#: mosaic teal, the purple far darker than the teal.
JERBITON = house(
    "Jerbiton",
    SCRIPTORUM,
    {
        "background": "#F5F0E5",
        "surface": "#ECE4D2",
        "panel": "#DED3BA",
        "foreground": "#221C22",
        "primary": "#56204D",
        "accent": "#3E8C88",
        "heading": "#56204D",
        "label": "#544A52",
        "rule": "#CDBFA6",
        "dim": "#625860",
        "text-accent": "#2A6461",
        "selection": "#E8DDE6",
        "paper-fleck": "#4A3E48",
        "paper-sheen": "#FFFFFF",
        "shadow": "#160A14",
        "button-shadow": "#ADA493",
    },
)

#: The stones set at Verditius's frame corners beside the family's rings:
#: a sapphire's light facet and its deep, apart from the copper and gold
#: in lightness.
VERDITIUS_GEM, VERDITIUS_GEM_DEEP = "#A9C4EC", "#24406E"

#: The colours of Mercere's mark in its seal, the book's own (Houses of
#: Hermes: True Lineages p. 78): the coin's yellow and the potsherd's
#: blue, on the cap's red (the theme's heading).
MERCERE_COIN, MERCERE_POTSHERD = "#E2B83C", "#2C5AA0"

#: The House themes' palettes, in the order the Settings window lists them.
HOUSES: tuple[Palette, ...] = (
    BONISAGUS,
    GUERNICUS,
    MERCERE,
    TREMERE,
    BJORNAER,
    CRIAMON,
    MERINITA,
    VERDITIUS,
    EX_MISCELLANEA,
    FLAMBEAU,
    JERBITON,
    TYTALUS,
)

#: Each House theme's In Creation twin, made from its own colours.
for _house in HOUSES:
    IN_CREATION[_house.name] = cooled(_house)

#: The pigments an illuminated initial takes in a House's theme, over
#: PIGMENTS: its ground's two colours (lapis and vermilion in Scriptorum).
HOUSE_PIGMENTS: dict[str, dict[str, str]] = {
    # Lapis and a deep sea-green, cool as the House's ink.
    BONISAGUS.name: {
        "vermilion": "#1F6A6E",
        "vermilion-deep": "#0F3E42",
    },
    # The violet of the cave and the verdigris of Kronos's serpent coils.
    CRIAMON.name: {
        "lapis": "#4A3478",
        "lapis-deep": "#271B45",
        "vermilion": "#2F7A68",
        "vermilion-deep": "#16443A",
        "knot-ground": "#140E22",
    },
    # The two claimants' colours, quartered against each other: a light
    # amethyst against a dark verdigris, apart in lightness as in hue.
    TYTALUS.name: {
        "lapis": "#8A62D0",
        "lapis-deep": "#5A3A96",
        "vermilion": "#1F5243",
        "vermilion-deep": "#0C2620",
        "knot-ground": "#0E1215",
    },
    # The judges' indigo and the scales' bronze.
    GUERNICUS.name: {
        "lapis": "#2E2A55",
        "lapis-deep": "#1A1733",
        "vermilion": "#9C7A3C",
        "vermilion-deep": "#5E4720",
        "knot-ground": "#14122A",
    },
    # The Redcap's red and the potsherd's blue.
    MERCERE.name: {
        "lapis": "#3F69B0",
        "lapis-deep": "#284880",
        "vermilion": "#6E1414",
        "vermilion-deep": "#4A0C0C",
    },
    # Pale steel over dried-blood rust, a light and a dark ground.
    TREMERE.name: {
        "lapis": "#5C6B7E",
        "lapis-deep": "#36404D",
        "vermilion": "#7A3328",
        "vermilion-deep": "#4A1C15",
        "knot-ground": "#101216",
    },
    # The pine and the bear-brown ochre.
    BJORNAER.name: {
        "lapis": "#22402C",
        "lapis-deep": "#12261A",
        "vermilion": "#A9773C",
        "vermilion-deep": "#6A4820",
        "knot-ground": "#13241A",
    },
    # Moonlit green-silver against heather violet, a light and a dark
    # ground.
    MERINITA.name: {
        "lapis": "#8FAE80",
        "lapis-deep": "#4F6B45",
        "vermilion": "#7E5E9C",
        "vermilion-deep": "#4A3460",
        "knot-ground": "#0C120D",
    },
    # Hot copper and a soot-blue steel.
    VERDITIUS.name: {
        "lapis": "#2E3A48",
        "lapis-deep": "#19212B",
        "vermilion": "#8E4A2A",
        "vermilion-deep": "#552A16",
        "knot-ground": "#100C09",
    },
    # The lake's slate and the lichen's ochre.
    EX_MISCELLANEA.name: {
        "lapis": "#24384E",
        "lapis-deep": "#142233",
        "vermilion": "#A3884A",
        "vermilion-deep": "#665429",
        "knot-ground": "#101A26",
    },
    # Crimson and flame, quartered as a knight's shield.
    FLAMBEAU.name: {
        "lapis": "#6E1A12",
        "lapis-deep": "#420D08",
        "vermilion": "#E08A3C",
        "vermilion-deep": "#A2561C",
        "knot-ground": "#120B09",
    },
    # Imperial purple and the mosaic's teal.
    JERBITON.name: {
        "lapis": "#56204D",
        "lapis-deep": "#36122F",
        "vermilion": "#3E8C88",
        "vermilion-deep": "#245654",
        "knot-ground": "#2A0F25",
    },
}


def pigments(p: Palette) -> dict[str, str]:
    """An illuminated initial's pigments on palette `p`'s page."""
    own = HOUSE_PIGMENTS.get(p.name.removesuffix(" Drafting"), {})
    return {**PIGMENTS, **own}


#: A House theme's metal for the frames, rods and rims the desktop gilds,
#: (stop, colour) as BURNISH: a House whose accent is not gold works them
#: in its own accent, so no Scriptorum gold strays onto its page.
HOUSE_METAL: dict[str, tuple[tuple[float, str], ...]] = {
    # Harpax's verdigris, burnished: dark, its accent, a pale glint, back.
    TYTALUS.name: (
        (0.00, "#0C2620"),
        (0.25, "#28654F"),
        (0.45, "#6FA894"),
        (0.60, "#28654F"),
        (1.00, "#0C2620"),
    ),
    # The scales' bronze, burnished.
    GUERNICUS.name: (
        (0.00, "#4E3712"),
        (0.25, "#9C7A3C"),
        (0.45, "#D9BE86"),
        (0.60, "#9C7A3C"),
        (1.00, "#4E3712"),
    ),
    # The yellow of the Redcap's coin, the House's only warm metal.
    MERCERE.name: (
        (0.00, "#7A5A10"),
        (0.25, "#D6AE34"),
        (0.45, "#F8E39A"),
        (0.60, "#D6AE34"),
        (1.00, "#7A5A10"),
    ),
    # Polished steel.
    TREMERE.name: (
        (0.00, "#2B3038"),
        (0.25, "#7E8894"),
        (0.45, "#DDE4EC"),
        (0.60, "#7E8894"),
        (1.00, "#2B3038"),
    ),
    # Bear-brown ochre, worn like an oiled hide.
    BJORNAER.name: (
        (0.00, "#5A3C16"),
        (0.25, "#A9773C"),
        (0.45, "#DDBB8A"),
        (0.60, "#A9773C"),
        (1.00, "#5A3C16"),
    ),
    # Moonlit green-silver.
    MERINITA.name: (
        (0.00, "#3A4A36"),
        (0.25, "#8FAE80"),
        (0.45, "#E4F0DA"),
        (0.60, "#8FAE80"),
        (1.00, "#3A4A36"),
    ),
    # The rings' own gold, warmer and deeper than Scriptorum's gilt.
    VERDITIUS.name: (
        (0.00, "#6A3E14"),
        (0.25, "#C68E3A"),
        (0.45, "#F0CB86"),
        (0.60, "#C68E3A"),
        (1.00, "#6A3E14"),
    ),
    # Lichen ochre.
    EX_MISCELLANEA.name: (
        (0.00, "#5A4820"),
        (0.25, "#A3884A"),
        (0.45, "#DCCB9C"),
        (0.60, "#A3884A"),
        (1.00, "#5A4820"),
    ),
    # Flame, from ember to white heat.
    FLAMBEAU.name: (
        (0.00, "#5A1E0C"),
        (0.25, "#D9772E"),
        (0.45, "#FFD9A0"),
        (0.60, "#D9772E"),
        (1.00, "#5A1E0C"),
    ),
    # Glazed teal tesserae.
    JERBITON.name: (
        (0.00, "#1C4442"),
        (0.25, "#3E8C88"),
        (0.45, "#A8DCD8"),
        (0.60, "#3E8C88"),
        (1.00, "#1C4442"),
    ),
}


def metal(p: Palette) -> tuple[tuple[float, str], ...]:
    """The metal palette `p`'s theme gilds with: BURNISH, or its House's
    own."""
    return HOUSE_METAL.get(p.name.removesuffix(" Drafting"), BURNISH)


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

#: A House theme's opening card, over OPENING_CARD: the same cover page in
#: the House's own metal and night.
HOUSE_CARDS: dict[str, dict[str, str]] = {
    BONISAGUS.name: {
        "gold": "#E6CD7E",
        "parchment": "#E8E4D6",
        "numbers": "#B9BBAE",
        "button": "#D7B95C",
        "button-text": "#121A2C",
        "dark": "#0E1730",
        "darker": "#04070F",
    },
    CRIAMON.name: {
        "gold": "#E3B07A",
        "parchment": "#E2DACA",
        "numbers": "#B2A6BE",
        "button": "#C9955A",
        "button-text": "#1A1320",
        "dark": "#14101C",
        "darker": "#040306",
    },
    TYTALUS.name: {
        "gold": "#D9C27E",
        "parchment": "#DCD8CC",
        "numbers": "#A9B3B9",
        "button": "#9C78C8",
        "button-text": "#0E1215",
        "dark": "#101519",
        "darker": "#030506",
    },
    GUERNICUS.name: {
        "gold": "#D9BE86",
        "parchment": "#E6E3DA",
        "numbers": "#B5B1A6",
        "button": "#B8975A",
        "button-text": "#14121C",
        "dark": "#16142A",
        "darker": "#05040B",
    },
    MERCERE.name: {
        "gold": "#E2B83C",
        "parchment": "#EDE5D2",
        "numbers": "#C2B596",
        "button": "#E2B83C",
        "button-text": "#221C14",
        "dark": "#2A0E0E",
        "darker": "#0A0303",
    },
    TREMERE.name: {
        "gold": "#C8D3E0",
        "parchment": "#D9DCDF",
        "numbers": "#9AA1AA",
        "button": "#8E9AA8",
        "button-text": "#101216",
        "dark": "#14161A",
        "darker": "#040506",
    },
    BJORNAER.name: {
        "gold": "#DDBB8A",
        "parchment": "#E9E3D5",
        "numbers": "#B8AF9C",
        "button": "#A9773C",
        "button-text": "#14100A",
        "dark": "#14261A",
        "darker": "#050A06",
    },
    MERINITA.name: {
        "gold": "#CDE3BE",
        "parchment": "#D8DDD0",
        "numbers": "#9EAA98",
        "button": "#9C82BA",
        "button-text": "#0C120D",
        "dark": "#111813",
        "darker": "#030504",
    },
    VERDITIUS.name: {
        "gold": "#E6B866",
        "parchment": "#DCD3C6",
        "numbers": "#A69A8A",
        "button": "#C68E3A",
        "button-text": "#17130F",
        "dark": "#1E1611",
        "darker": "#060403",
    },
    EX_MISCELLANEA.name: {
        "gold": "#DCCB9C",
        "parchment": "#E6E7E1",
        "numbers": "#B1B4AC",
        "button": "#A3884A",
        "button-text": "#0C1218",
        "dark": "#18222E",
        "darker": "#05080C",
    },
    FLAMBEAU.name: {
        "gold": "#F2A65A",
        "parchment": "#E2D6CB",
        "numbers": "#AE9C90",
        "button": "#D9772E",
        "button-text": "#1A1210",
        "dark": "#1E1210",
        "darker": "#070403",
    },
    JERBITON.name: {
        "gold": "#A8DCD8",
        "parchment": "#F0EADC",
        "numbers": "#C2B6A0",
        "button": "#3E8C88",
        "button-text": "#160A14",
        "dark": "#2A1026",
        "darker": "#0B040A",
    },
}


def opening_card(p: Palette) -> dict[str, str]:
    """The opening card's colours under palette `p`'s theme."""
    own = HOUSE_CARDS.get(p.name.removesuffix(" Drafting"), {})
    return {**OPENING_CARD, **own}
