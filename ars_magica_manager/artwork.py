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
  released symbol and uses the Quaesitor's.
- icons/: Phosphor Icons at Light weight (MIT), copied by
  tools/fetch_icons.py, for everything else.

app/ holds the app icon, made from the Order of Hermes sigil, and fonts/
the typefaces (SIL Open Font License): EB Garamond for headings (in small
caps) and rules prose, Uncial Antiqua for one decorative flourish. Labels,
numbers and tables use the system's own UI font (Segoe UI on Windows).
"""

from pathlib import Path

from .arts import ARTS

ASSETS = Path(__file__).resolve().parent / "assets"
SYMBOLS = ASSETS / "symbols"
ICONS = ASSETS / "icons"

#: The app's window and taskbar icon (a Windows .ico of several sizes), and
#: the sigil as a picture.
APP_ICON = ASSETS / "app" / "sigil.ico"
SIGIL = ASSETS / "app" / "sigil.png"

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
    "close": "x",
    # A record's Manage chapter, and its In Creation / In Play mode
    "manage": "archive",
    "export": "export",
    "update": "file-arrow-down",
    "in_creation": "feather",
    "in_play": "seal-check",
    "worksheet": "clipboard-text",
}


def icon(concept: str) -> Path:
    """The icon for an app concept; KeyError for one the registry lacks."""
    return ICONS / f"{ICON_NAMES[concept]}.svg"


def art_symbol(art: str) -> Path:
    """An Art's symbol, by its name ("Creo"); KeyError for anything else."""
    return ART_SYMBOLS[art]


def house_symbol(house_id: str | None) -> Path | None:
    """A House's symbol by its catalog id, or None (no House, or one with
    no symbol)."""
    return HOUSE_SYMBOLS.get(house_id or "")
