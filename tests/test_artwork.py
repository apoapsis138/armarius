"""The artwork registry: every Art and House has a symbol, every icon the
registry names is bundled, nothing bundled is unnamed, and every SVG is
one colour a front-end can tint. And the credits for all of it are in
NOTICE.md."""

import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from ars_magica_manager import ROOT, artwork, catalog
from ars_magica_manager.arts import ARTS

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


def _registered() -> set[Path]:
    return (
        set(artwork.ART_SYMBOLS.values())
        | set(artwork.HOUSE_SYMBOLS.values())
        | {artwork.icon(concept) for concept in artwork.ICON_NAMES}
        | {artwork.APP_ICON, artwork.SIGIL}
        | {path for paths in artwork.FONTS.values() for path in paths}
        | set(artwork.SOUNDS.values())
        | set(artwork.CHARGE_DRAWINGS.values())
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


def test_there_are_svgs_to_check():
    assert len(SVGS) > 40


@pytest.mark.parametrize(
    "path", SVGS, ids=lambda path: str(path.relative_to(artwork.ASSETS))
)
def test_svg_is_one_colour_sized_by_its_viewbox(path):
    root = ET.parse(path).getroot()
    assert root.tag == f"{SVG}svg"
    assert len(root.get("viewBox", "").split()) == 4
    fills = {
        element.get("fill")
        for element in root.iter()
        if element.get("fill") is not None
    }
    assert fills == {"currentColor"}
    assert 'stroke="#' not in path.read_text(encoding="utf-8")


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
        licence = artwork.ASSETS / "fonts" / f"{family.replace(' ', '')}-OFL.txt"
        assert "SIL Open Font License" in licence.read_text(encoding="utf-8")
