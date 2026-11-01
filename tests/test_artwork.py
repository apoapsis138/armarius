"""The artwork registry: every Art and House has a symbol, every icon the
registry names is bundled, nothing bundled is unnamed, and every SVG is
one colour a front-end can tint. And the credits for all of it are in
NOTICE.md."""

import xml.etree.ElementTree as ET
from pathlib import Path

from armarius_style import fonts

from ars_magica_manager import ROOT, artwork, catalog
from ars_magica_manager.arts import ARTS
from ars_magica_manager.models import Character

SVG = "{http://www.w3.org/2000/svg}"
SVGS = sorted(artwork.ASSETS.rglob("*.svg"))


def test_every_art_has_a_symbol():
    assert set(artwork.ART_SYMBOLS) == set(ARTS)
    assert artwork.art_symbol("Creo").name == "creo.svg"


def test_every_house_has_a_symbol_guernicus_the_quaesitors():
    houses = {house.id for house in catalog.load_house_catalog()}
    assert set(artwork.HOUSE_SYMBOLS) == houses
    assert artwork.house_symbol("house_guernicus").name == "quaesitor.svg"
    assert artwork.house_symbol(None) is None
    assert artwork.house_symbol("house_diedne") is None


def test_every_tradition_has_a_symbol_and_a_person_shows_theirs():
    traditions = {t.id for t in catalog.load_tradition_catalog()}
    assert set(artwork.TRADITION_SYMBOLS) == traditions
    witch = Character("c1", "Agnes", "companion", traditions=["trad_folk_witches"])
    assert artwork.person_symbol(witch) == artwork.tradition_symbol("trad_folk_witches")
    magus = Character("c2", "Hrafn", "magus", traditions=["trad_vitkir"])
    magus.hermetic.house = "house_bjornaer"
    assert artwork.person_symbol(magus) == artwork.house_symbol("house_bjornaer")
    assert artwork.person_symbol(Character("c3", "Odo", "grog")) is None


def _registered() -> set[Path]:
    return (
        set(artwork.ART_SYMBOLS.values())
        | set(artwork.HOUSE_SYMBOLS.values())
        | set(artwork.TRADITION_SYMBOLS.values())
        | {artwork.SAGA_CULT_SYMBOL}
        | {artwork.icon(concept) for concept in artwork.ICON_NAMES}
        | {artwork.APP_ICON, artwork.SIGIL}
        | {path for paths in artwork.FONTS.values() for path in paths}
        | set(artwork.SOUNDS.values())
        | set(artwork.CHARGE_DRAWINGS.values())
        | set(artwork.DRAWN_ICONS.values())
    )


def test_every_registered_file_exists():
    missing = sorted(str(path) for path in _registered() if not path.is_file())
    assert not missing


def test_every_bundled_picture_and_font_is_registered():
    bundled = {
        path
        for path in artwork.ASSETS.rglob("*")
        if path.suffix in {".svg", ".png", ".ico", ".ttf", ".wav"}
    }
    assert bundled - _registered() == set()


def test_no_bundled_file_carries_a_content_credential():
    """A file passed through some tools gains a C2PA manifest saying an AI
    may have made it; the app's art is drawn in code or freely licensed,
    so no shipped file may carry one."""
    stamped = sorted(
        path.name
        for path in artwork.ASSETS.rglob("*")
        if path.is_file() and b"c2pa" in path.read_bytes()
    )
    assert not stamped


def test_there_are_svgs_to_check():
    assert len(SVGS) > 40


def _svg_faults(path: Path) -> list[str]:
    """What keeps the SVG at `path` from being one colour sized by its
    viewBox."""
    root = ET.parse(path).getroot()
    faults: list[str] = []
    if root.tag != f"{SVG}svg":
        faults.append(f"its root is {root.tag}")
    if len(root.get("viewBox", "").split()) != 4:
        faults.append("it has no viewBox")
    fills = {
        element.get("fill")
        for element in root.iter()
        if element.get("fill") is not None
    }
    if fills != {"currentColor"}:
        faults.append(f"its fills are {sorted(map(str, fills))}")
    if 'stroke="#' in path.read_text(encoding="utf-8"):
        faults.append("it strokes in a fixed colour")
    return faults


def test_every_svg_is_one_colour_sized_by_its_viewbox():
    faults = [
        f"{path.relative_to(artwork.ASSETS)}: {', '.join(found)}"
        for path in SVGS
        if (found := _svg_faults(path))
    ]
    assert not faults, "; ".join(faults)


def test_notice_credits_the_artwork_icons_fonts_and_sounds():
    notice = " ".join((ROOT / "NOTICE.md").read_text(encoding="utf-8").split())
    for credit in (
        "assets/symbols/",
        "Changes made:** the symbols were trimmed",
        "Phosphor Icons",
        "SIL Open Font License",
        "EB Garamond",
        "Uncial Antiqua",
        "assets/sounds/",
        "Freesound",
    ):
        assert credit in notice
    assert "CC0" in (artwork.SOUNDS_DIR / "LICENSE.txt").read_text(encoding="utf-8")
    assert (artwork.ICONS / "LICENSE.txt").is_file()
    for family in artwork.FONTS:
        licence = fonts.ASSETS / "fonts" / f"{family.replace(' ', '')}-OFL.txt"
        assert "SIL Open Font License" in licence.read_text(encoding="utf-8")
