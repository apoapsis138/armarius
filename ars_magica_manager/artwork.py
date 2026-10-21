"""The app's artwork and where it lives: the registry of its symbols,
icons, app icon and fonts, shared by every front-end.

A front-end asks for a concept ("covenant", "edit") or an Art or House by
name and gets the path of an SVG, so no screen names an image file and
the two front-ends cannot drift apart. The terminal front-end draws no
pictures today; the desktop one does.

Every SVG here is one colour, drawn in currentColor, so a front-end tints
it to its theme. Two sets:

- symbols/: Atlas Games's released Technique, Form and House symbols,
  traced from their TIFFs by tools/trace_symbols.py (CC BY-SA 4.0, see
  NOTICE.md). They are woodcut tiles: the ink is the tile and its frame,
  and the symbol shows through as the background. House Guernicus has no
  released symbol and uses the Quaesitor's. symbols/traditions/ holds the
  hedge traditions' symbols, drawn in the same manner by
  tools/draw_traditions.py.
- charges/: heraldic charges from Wikimedia Commons (see NOTICE.md),
  cleaned by tools/clean_charge.py into layers (silhouette, line work,
  claws), each tinted by arms.py's tincture rules.
- drawn/: icons the app draws itself, after a Phosphor one (a ruin is
  the covenant's turret broken), each made by a script in tools/.
- icons/: Phosphor Icons at Light weight (MIT), copied by
  tools/fetch_icons.py, for everything else.

app/ holds the app icon, made from the Order of Hermes sigil, and fonts/
the typefaces (SIL Open Font License): EB Garamond for headings (in small
caps) and rules prose, Uncial Antiqua for one decorative flourish. Labels,
numbers and tables use the system's own UI font (Segoe UI on Windows).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .arts import ARTS

if TYPE_CHECKING:
    from .models import Character

ASSETS = Path(__file__).resolve().parent / "assets"
SYMBOLS = ASSETS / "symbols"
ICONS = ASSETS / "icons"
SOUNDS_DIR = ASSETS / "sounds"
CHARGES = ASSETS / "charges"
DRAWN = ASSETS / "drawn"

#: The heraldic charges drawn from a file (Wikimedia Commons drawings,
#: credited in NOTICE.md), by charge name.
CHARGE_DRAWINGS: dict[str, Path] = {
    "Lion": CHARGES / "lion.svg",
    "Lion, tail knotted": CHARGES / "lion-tail-knotted.svg",
    "Eagle": CHARGES / "eagle.svg",
    "Fleur-de-lis": CHARGES / "fleur-de-lis.svg",
    "Tower": CHARGES / "tower.svg",
    "Cross": CHARGES / "cross.svg",
    "Crescent": CHARGES / "crescent.svg",
    "Star": CHARGES / "star.svg",
    "Tree": CHARGES / "tree.svg",
}

#: The app's window and taskbar icon (a Windows .ico of several sizes), and
#: the sigil as a picture.
APP_ICON = ASSETS / "app" / "sigil.ico"
SIGIL = ASSETS / "app" / "sigil.png"

#: The desktop version's sounds, by cue (CC0 recordings from Freesound,
#: credited in NOTICE.md): a page for a chapter and a longer one for a
#: record, a quill for a saved form, coins for the Treasury, a chest for
#: the Inventory, a wax seal for Advance Season, a knock for a refusal.
SOUNDS: dict[str, Path] = {
    cue: SOUNDS_DIR / f"{cue}.wav"
    for cue in ("page", "page-long", "quill", "coins", "chest", "seal", "tock")
}

#: The bundled typefaces' files, by family name.
FONTS: dict[str, tuple[Path, ...]] = {
    "EB Garamond": (
        ASSETS / "fonts" / "EBGaramond-wght.ttf",
        ASSETS / "fonts" / "EBGaramond-Italic-wght.ttf",
    ),
    "Uncial Antiqua": (ASSETS / "fonts" / "UncialAntiqua-Regular.ttf",),
}

#: Each Art's symbol.
ART_SYMBOLS: dict[str, Path] = {
    art: SYMBOLS / "arts" / f"{art.lower()}.svg" for art in ARTS
}

#: Each House's symbol, by its house_catalog.json id.
HOUSE_SYMBOLS: dict[str, Path] = {
    f"house_{name}": SYMBOLS / "houses" / f"{name}.svg"
    for name in (
        "bjornaer",
        "bonisagus",
        "criamon",
        "ex_miscellanea",
        "flambeau",
        "jerbiton",
        "mercere",
        "merinita",
        "tremere",
        "tytalus",
        "verditius",
    )
} | {"house_guernicus": SYMBOLS / "houses" / "quaesitor.svg"}

#: Each tradition's symbol, by its tradition_catalog.json id, for a
#: character of a tradition as a House's is for a magus: drawn by
#: tools/draw_traditions.py in the House symbols' manner.
TRADITION_SYMBOLS: dict[str, Path] = {
    f"trad_{name}": SYMBOLS / "traditions" / f"{name}.svg"
    for name in (
        "elementalists",
        "folk_witches",
        "gruagachan",
        "learned_magicians",
        "nightwalkers",
        "vitkir",
        "ollamhain",
        "volkhvy",
        "wise_folk",
        "borrowers",
        "faerie_doctors",
        "homunculus_wizards",
        "caerflorons_line",
        "wordsmiths",
        "ascetics",
        "cantores",
        "sufis",
        "baal_shem",
        "kabbalists",
        "sol_invictus",
        "priory_of_saint_nerius",
        "zoroastrians",
        "karaites",
        "celi_de",
        "mobeds",
        "hesychasts",
        "society_of_cyprian_and_justina",
        "kassalan_exorcists",
        "luciferans",
        "strigae",
        "witch_hammers",
        "dark_gnostics",
        "dread_host",
        "mulhidun",
        "damhadh_duidsan",
        "ordo_vagorum",
        "witches_of_thessaly",
        "cailleach_phiseogach",
        "stringla",
        "paulicians",
        "baal_ov",
        "beast_masters",
        "tempestaria",
        "scinnfolk",
        "columbae",
        "donatores_requietis_aeternae",
        "pharmacopoeians",
        "lineage_of_pralix",
        "rustic_magi",
        "hermetic_sahirs",
        "seirenes",
        "hermetic_sorginak",
        "gorgiastic_cathars",
        "sahirs",
        "nizari_mustajibs",
        "soban_alchemists",
        "cult_of_dedun",
        "lector_priests",
        "settuten_berber",
        "settuten_tuareg",
        "imhergi",
        "inenden",
        "bouda",
        "bedouin_hakima",
        "murabitin",
        "sorginak",
        "forest_paths",
        "branchidae",
        "corrguineach",
        "children_of_olympos",
        "amazon_sorceresses",
        "augustan_brotherhood",
        "muspelli",
        "soqotran_sorcerers",
        "canaanite_necromancers",
        "defixio_cults",
        "heronic_mechanici",
        "hyperborean_hymnists",
        "storm_wizards",
        "hunters",
        "fectores",
    )
}

#: An app concept to its Phosphor icon's name (the file is
#: icons/<name>.svg).
ICON_NAMES: dict[str, str] = {
    # Records and places
    "saga": "book-bookmark",
    "covenant": "castle-turret",
    "character": "person",
    "laboratory": "flask",
    "library": "book-open",
    "lab_text": "scroll",
    "familiar": "paw-print",
    "players": "users-three",
    # A Tribunal: the magi of a region in council.
    "tribunal": "users-three",
    # The Region beyond the covenants, and each kind of neighbour in it.
    "region": "shield",
    "lord": "sword",
    "town": "coins",
    "church": "church",
    "university": "book-open",
    "faction": "users-three",
    "threat": "skull",
    "place": "sparkle",
    "enchanted_item": "magic-wand",
    # Time and resources
    "season": "hourglass-medium",
    "year": "calendar",
    "vis": "drop-half",
    "income": "coins",
    "give": "hand-arrow-up",
    "silver": "hand-coins",
    # Magic and its dangers
    "warping": "lightning",
    "twilight": "moon-stars",
    "magic": "sparkle",
    "divine": "church",
    "faerie": "mask-happy",
    "infernal": "skull",
    # Combat
    "combat": "sword",
    "soak": "shield",
    # The verbs, the More and New menus, and the app's own controls
    "add": "plus",
    "edit": "pencil-simple",
    "delete": "trash",
    "more": "dots-three",
    "new": "file-plus",
    "filter": "funnel",
    "search": "magnifying-glass",
    "help": "question",
    "theme": "palette",
    "sounds_on": "speaker-high",
    "sounds_off": "speaker-slash",
    "close": "x",
    # A record's Manage chapter, and its In Creation / In Play mode
    "manage": "archive",
    "export": "export",
    "update": "file-arrow-down",
    "in_creation": "feather",
    "in_play": "seal-check",
    "worksheet": "clipboard-text",
    # A record's Secrets chapter, for the storyguide's eyes.
    "secrets": "keyhole",
}

#: An app concept to an icon the app draws itself (drawn/), in place of
#: a Phosphor one: a ruined covenant's broken turret (tools/draw_ruin.py).
DRAWN_ICONS: dict[str, Path] = {"ruin": DRAWN / "ruin.svg"}


def icon(concept: str) -> Path:
    """The icon for an app concept; KeyError for one the registry lacks."""
    if concept in DRAWN_ICONS:
        return DRAWN_ICONS[concept]
    return ICONS / f"{ICON_NAMES[concept]}.svg"


def art_symbol(art: str) -> Path:
    """An Art's symbol, by its name ("Creo"); KeyError for anything else."""
    return ART_SYMBOLS[art]


def house_symbol(house_id: str | None) -> Path | None:
    """A House's symbol by its catalog id, or None (no House, or one with
    no symbol)."""
    return HOUSE_SYMBOLS.get(house_id or "")


def tradition_symbol(tradition_id: str | None) -> Path | None:
    """A hedge tradition's symbol, or None for an id without one."""
    return TRADITION_SYMBOLS.get(tradition_id or "")


def person_symbol(character: Character) -> Path | None:
    """The symbol a person is shown by: a magus's House's, else the first
    of their traditions that has one, else None."""
    if character.type == "magus":
        house = house_symbol(character.hermetic.house)
        if house is not None:
            return house
    for tradition_id in character.traditions:
        symbol = tradition_symbol(tradition_id)
        if symbol is not None:
            return symbol
    return None
