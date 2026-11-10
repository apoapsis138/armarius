"""The desktop's House themes (gui/style/liveries.py, families.py and the
colours in style/palettes.py): text stays readable on every theme's
texture, meaningful colours keep their hues, each House theme has its own
In Creation twin, and every family's form paints."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication

from ars_magica_manager.gui import pictures
from ars_magica_manager.gui.style import families, gilding, liveries, pieces
from ars_magica_manager.gui.style.families import DIALOG, PLAIN, WINDOW
from ars_magica_manager.gui.style.vellum import worst_ground
from ars_magica_manager.style import fonts
from ars_magica_manager.style import palettes as pal


@pytest.fixture(scope="module")
def app() -> QApplication:
    application = QApplication.instance() or QApplication([])
    assert isinstance(application, QApplication)
    pictures.register_fonts()
    return application


def _pages() -> list[tuple[liveries.Theme, pal.Palette]]:
    return [(t, p) for t in liveries.THEMES for p in (t.palette, t.drafting)]


def _hue_gap(a: str, b: str) -> float:
    gap = abs(pal.hue(a) - pal.hue(b))
    return min(gap, 1 - gap)


@pytest.mark.usefixtures("app")
def test_text_stands_out_on_every_themes_paper() -> None:
    """Every text colour stands 4.5:1 against the darkest of each theme's
    paper (lightest on a dark page), texture and all, In Play and In
    Creation."""
    failing = []
    for theme, p in _pages():
        ground = worst_ground(theme.look.paper(p), p.dark)
        for key in pal.TEXT:
            ratio = pal.contrast(p[key], ground)
            if ratio < pal.READABLE:
                failing.append(f"{p.name} {key} {ratio:.2f}")
    assert not failing, failing


class _Blots(families.Bonisagus):
    """A House whose texture would bury the text: ink blots everywhere."""

    def texture(self, painter: QPainter, p: pal.Palette, strength: float) -> None:
        painter.fillRect(QRectF(0, 0, 256, 512), QColor(0, 0, 0, round(230 * strength)))


@pytest.mark.usefixtures("app")
def test_a_texture_that_buries_the_text_is_drawn_fainter_behind_it() -> None:
    look = _Blots(None)
    p = pal.BONISAGUS
    full = QImage(512, 512, QImage.Format.Format_RGB32)
    full.fill(QColor(p["background"]))
    painter = QPainter(full)
    look.texture(painter, p, 1.0)
    painter.end()
    assert not families.readable(full, p)
    assert families.readable(look.paper(p), p)


def test_house_themes_keep_the_meaningful_colours_hues() -> None:
    for p in pal.HOUSES:
        base = pal.SCRIPTORUM_DARK if p.dark else pal.SCRIPTORUM
        for key in pal.MEANINGFUL:
            assert _hue_gap(p[key], base[key]) < 0.02, (p.name, key)
            # Retuned only for contrast: never less readable than before.
            before = pal.contrast(base[key], base["background"])
            assert pal.contrast(p[key], p["background"]) >= min(before, 4.5) - 0.05


def test_each_house_theme_has_its_own_cooled_and_ruled_twin() -> None:
    for theme in liveries.THEMES:
        twin = theme.drafting
        assert twin.ruled and twin.dark == theme.palette.dark
        assert twin.name == f"{theme.name} Drafting"
        assert pal.for_mode(theme.palette, True) is twin
        assert liveries.of_palette(twin) is theme
        # The text, headings and meaningful colours are the theme's own.
        for key in ("foreground", "heading", "accent", *pal.MEANINGFUL):
            assert twin[key] == theme.palette[key], (twin.name, key)
        assert twin["background"] != theme.palette["background"]


def test_the_registry_lists_scriptorum_first_and_every_house_by_family() -> None:
    names = [theme.name for theme in liveries.THEMES]
    assert names[:2] == ["Scriptorum", "Scriptorum Dark"]
    assert len(set(names)) == len(names)
    for theme in liveries.THEMES[2:]:
        assert theme.group in liveries.GROUPS[1:]
        assert theme.mark is not None and theme.mark.exists()
        assert theme.palette in pal.HOUSES
    bonisagus = liveries.named("Bonisagus")
    assert bonisagus is not None and bonisagus.group == liveries.TRUE_LINEAGES
    assert not bonisagus.palette.dark
    assert liveries.named("Nobody") is None


def test_each_family_sets_headings_in_its_own_type() -> None:
    assert families.Look.heading_family == fonts.SERIF
    assert families.TrueLineage.heading_family == fonts.INSCRIPTION
    assert families.MysteryCult.heading_family == fonts.DISPLAY
    # A Societas keeps blackletter for big titles only; its section
    # headings are the book face's small capitals in the heading colour.
    assert families.Societas.title_family == fonts.TITLE
    assert families.Societas.heading_family == fonts.SERIF
    assert families.Societas.always_small_caps
    assert families.Societas.heading_ink == "heading"


@pytest.mark.usefixtures("app")
def test_a_societas_section_heading_is_small_caps_and_its_title_blackletter() -> None:
    p = pal.TYTALUS
    heading = pieces.heading(14, p)
    assert heading.family() == fonts.SERIF
    assert heading.capitalization() == heading.Capitalization.SmallCaps
    assert pieces.title(17, p).family() == fonts.TITLE
    assert pieces.heading_ink(p) == p["heading"]
    assert pieces.heading_ink(pal.SCRIPTORUM) == pal.SCRIPTORUM["foreground"]


def _simulated_luminance(colour: str, matrix: tuple[tuple[float, ...], ...]) -> float:
    """`colour`'s luminance as an eye with that red-green deficiency
    sees it (Machado, Oliveira and Fernandes 2009, severity 1)."""

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    rgb = [lin(int(colour[i : i + 2], 16) / 255) for i in (1, 3, 5)]
    seen = [
        max(0.0, min(1.0, sum(m * c for m, c in zip(row, rgb, strict=True))))
        for row in matrix
    ]
    return 0.2126 * seen[0] + 0.7152 * seen[1] + 0.0722 * seen[2]


def test_tytalus_violet_and_green_part_by_lightness_for_red_green_blindness() -> None:
    """Buliste's amethyst (headings, seal) is far lighter than Harpax's
    verdigris (frame, rules), so the rivalry reads by value alone."""
    deuteranopia = (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    )
    protanopia = (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    )
    p = pal.TYTALUS
    for matrix in (deuteranopia, protanopia):
        violet = _simulated_luminance(p["heading"], matrix)
        green = _simulated_luminance(p["accent"], matrix)
        assert (violet + 0.05) / (green + 0.05) >= 3.0


def test_tytalus_gilds_in_its_own_verdigris_not_scriptorums_gold() -> None:
    gold = {colour for _stop, colour in pal.BURNISH}
    for p in (pal.TYTALUS, pal.IN_CREATION["Tytalus"]):
        assert not gold & {colour for _stop, colour in pal.metal(p)}
    assert pal.metal(pal.SCRIPTORUM) is pal.BURNISH
    assert pal.metal(pal.BONISAGUS) is pal.BURNISH


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("house", ["bonisagus", "criamon", "tytalus"])
def test_the_watermark_is_the_sign_alone_without_its_stone(house: str) -> None:
    """The Inspector's watermark keeps the sign cut into a House's mark
    but not the square stone it is cut from, nor a border round it."""
    ink = pal.TYTALUS["foreground"]
    sign = families._sign(liveries.house_mark(house), ink, 120, 1.0).toImage()
    side = sign.width()

    def inked(x: int, y: int) -> bool:
        return sign.pixelColor(x, y).alpha() > 128

    band = [
        (x, y)
        for x in range(side)
        for y in range(side)
        if min(x, y, side - 1 - x, side - 1 - y) < side * 0.05
    ]
    assert not any(inked(x, y) for x, y in band), house
    assert sum(inked(x, y) for x in range(side) for y in range(side)) > side


@pytest.mark.usefixtures("app")
def test_tytalus_paints_a_names_initial_on_a_quartered_ground() -> None:
    font = QFont(fonts.DISPLAY)
    font.setPointSizeF(24)
    p = pal.TYTALUS
    assert gilding.initial_advance("L", font, p) > gilding.initial_advance(
        "L", font, pal.SCRIPTORUM_DARK
    )
    image = QImage(80, 80, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    gilding.gilt_letter(painter, "L", font, QPointF(4, 60), p)
    painter.end()
    seen = {image.pixelColor(x, y).name() for x in range(80) for y in range(80)}
    # The ground's two pigments are there, under the gold letter.
    pigment = pal.pigments(p)
    assert any(_near(c, pigment["lapis"]) for c in seen)
    assert any(_near(c, pigment["vermilion"]) for c in seen)


def _near(a: str, b: str) -> bool:
    return all(
        abs(int(a[i : i + 2], 16) - int(b[i : i + 2], 16)) <= 24 for i in (1, 3, 5)
    )


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize(
    "form",
    [families.Look, families.TrueLineage, families.MysteryCult, families.Societas],
)
def test_every_family_form_paints_every_piece(form: type[families.Look]) -> None:
    """Each family paints a page of every kind and each ornament without
    error, and draws something for each."""
    look = form(liveries.house_mark("bonisagus"))
    p = pal.BONISAGUS
    for kind in (WINDOW, DIALOG, PLAIN):
        image = QImage(300, 200, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        look.paint_page(painter, QRectF(0, 0, 300, 200), p, kind)
        painter.end()
    for draw in (
        lambda painter: look.heading_rule(painter, 300, 9, p),
        lambda painter: look.short_rule(painter, 300, 13, p),
        lambda painter: look.headpiece_centre(painter, 300, 17, p),
        lambda painter: look.band(painter, 300, 17, 50, p),
        lambda painter: look.tailpiece(painter, 300, p),
        lambda painter: look.corners(painter, QRectF(10, 10, 200, 80), p, 18),
    ):
        image = QImage(300, 100, QImage.Format.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        draw(painter)
        painter.end()
        assert any(
            image.pixelColor(x, y).alpha() for x in range(0, 300, 2) for y in range(100)
        )


@pytest.mark.usefixtures("app")
def test_the_inspectors_watermark_keeps_text_readable() -> None:
    """A House's mark is watermarked in the Inspector only as strongly as
    keeps every text colour readable over it; Scriptorum has none."""
    for theme, p in _pages():
        opacity = theme.look.watermark_opacity(p)
        if theme.mark is None:
            continue
        assert 0 < opacity <= families.WATERMARK, p.name
        ground = pal.mixed(
            worst_ground(theme.look.paper(p), p.dark), p["panel"], 70 / 255
        )
        under = pal.mixed(ground, families.watermark_ink(p), opacity)
        for key in pal.TEXT:
            assert pal.contrast(p[key], under) >= pal.READABLE, (p.name, key)


def test_house_pigments_and_opening_card_follow_the_theme() -> None:
    drafting = pal.IN_CREATION["Bonisagus"]
    for p in (pal.BONISAGUS, drafting):
        assert pal.pigments(p)["vermilion"] != pal.PIGMENTS["vermilion"]
        assert pal.pigments(p)["lapis"] == pal.PIGMENTS["lapis"]
        assert pal.opening_card(p)["dark"] != pal.OPENING_CARD["dark"]
    assert pal.pigments(pal.SCRIPTORUM) == pal.PIGMENTS
    assert pal.opening_card(pal.SCRIPTORUM_DARK) == pal.OPENING_CARD
