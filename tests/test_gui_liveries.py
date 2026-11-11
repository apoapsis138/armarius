"""The desktop's House themes (gui/style/liveries.py, families.py and the
colours in style/palettes.py): text stays readable on every theme's
texture, meaningful colours keep their hues, each House theme has its own
In Creation twin, and every family's form paints."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtCore import QPoint, QPointF, QRectF
from PySide6.QtGui import QColor, QFont, QImage, QPainter
from PySide6.QtWidgets import QApplication

from ars_magica_manager import artwork
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


@pytest.mark.parametrize(
    "house",
    [
        pal.GUERNICUS,
        pal.MERCERE,
        pal.TREMERE,
        pal.BJORNAER,
        pal.MERINITA,
        pal.VERDITIUS,
        pal.EX_MISCELLANEA,
        pal.FLAMBEAU,
        pal.JERBITON,
        pal.DIEDNE,
    ],
)
def test_a_houses_heading_and_accent_part_by_lightness_for_red_green_blindness(
    house: pal.Palette,
) -> None:
    """A House's two main colours (headings and seal; frame and rules) are
    apart in lightness as well as hue, for an eye that cannot tell red
    from green."""
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
    for matrix in (deuteranopia, protanopia):
        lights = sorted(
            _simulated_luminance(house[key], matrix) for key in ("heading", "accent")
        )
        assert (lights[1] + 0.05) / (lights[0] + 0.05) >= 2.0, house.name


def test_a_house_whose_accent_is_not_gold_gilds_in_its_own_metal() -> None:
    gold = {colour for _stop, colour in pal.BURNISH}
    houses = {p.name: p for p in pal.HOUSES}
    for name in (
        "Tytalus",
        "Guernicus",
        "Mercere",
        "Tremere",
        "Bjornaer",
        "Merinita",
        "Verditius",
        "Ex Miscellanea",
        "Flambeau",
        "Jerbiton",
        "Diedne",
    ):
        for p in (houses[name], pal.IN_CREATION[name]):
            assert not gold & {colour for _stop, colour in pal.metal(p)}, name
    assert pal.metal(pal.SCRIPTORUM) is pal.BURNISH
    assert pal.metal(pal.BONISAGUS) is pal.BURNISH


@pytest.mark.usefixtures("app")
def test_mercere_closes_a_chapter_on_its_mark_in_the_cap_coin_and_triangle() -> None:
    theme = liveries.named("Mercere")
    assert theme is not None
    # Drawn at twice the size, as on a high-density screen, so the coin's
    # few pixels are whole.
    image = QImage(240, 120, QImage.Format.Format_ARGB32)
    image.fill(QColor(theme.palette["background"]))
    painter = QPainter(image)
    painter.translate(-120, 0)
    painter.scale(2, 2)
    theme.look.tailpiece(painter, 240, theme.palette)
    painter.end()
    seen = {image.pixelColor(x, y).name() for x in range(240) for y in range(120)}
    assert any(_near(c, pal.MERCERE_COIN) for c in seen)
    assert any(_near(c, pal.MERCERE_POTSHERD) for c in seen)
    assert any(_near(c, theme.palette["heading"]) for c in seen)


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("house", [t.name for t in liveries.THEMES[2:]])
def test_a_house_closes_a_chapter_on_its_sign_not_a_seal_on_the_frame(
    house: str,
) -> None:
    """A House's sign is the centre of its tailpiece, in its heading ink;
    the foot of a dialog's frame carries no seal."""
    theme = liveries.named(house)
    assert theme is not None
    p = theme.palette
    tail = QImage(300, 60, QImage.Format.Format_ARGB32)
    tail.fill(0)
    painter = QPainter(tail)
    theme.look.tailpiece(painter, 300, p)
    painter.end()
    centre = {
        tail.pixelColor(x, y).name()
        for x in range(150 - 12, 150 + 12)
        for y in range(families.TAIL_Y - 12, families.TAIL_Y + 12)
        if tail.pixelColor(x, y).alpha() > 200
    }
    if house == "Diedne":
        # What is left of Diedne's sign is in the watermark's dark, and
        # none of it in the heading's ink.
        assert not any(_near(c, p["heading"]) for c in centre), house
    else:
        assert any(_near(c, p["heading"]) for c in centre), house
    # The foot of a dialog: paper and frame only, no heading-inked sign.
    page = QImage(300, 120, QImage.Format.Format_ARGB32)
    painter = QPainter(page)
    theme.look.paint_page(painter, QRectF(0, 0, 300, 120), p, DIALOG)
    painter.end()
    foot = {
        page.pixelColor(x, y).name() for x in range(130, 170) for y in range(80, 116)
    }
    assert not any(_near(c, p["heading"]) for c in foot), house


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("house", [t.name for t in liveries.THEMES[2:]])
def test_the_watermark_is_the_sign_alone_without_its_stone(house: str) -> None:
    """The Inspector's watermark keeps the sign cut into a House's mark
    (or drawn on it, for a mark drawn in ink) but not the square stone it
    is cut from, nor the frame round it."""
    theme = liveries.named(house)
    assert theme is not None and theme.mark is not None
    ink = pal.TYTALUS["foreground"]
    cut = families._drawn_sign if theme.look.sign_drawn else families._sign
    sign = cut(theme.mark, ink, 120, 1.0).toImage()
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


def test_ex_miscellanea_dyes_each_pennant_for_a_tradition() -> None:
    """Ex Miscellanea's pennants run through one muted colour for each
    tradition, not the House's two; another Societas keeps its livery."""
    look = families.ExMiscellanea(None)
    p = pal.EX_MISCELLANEA
    dyes = [look.pennant(p, i) for i in range(len(pal.EX_MISCELLANEA_MOTLEY))]
    assert dyes == list(pal.EX_MISCELLANEA_MOTLEY)
    flambeau = families.Flambeau(None)
    assert [flambeau.pennant(pal.FLAMBEAU, i) for i in range(2)] == [
        pal.FLAMBEAU["heading"],
        pal.FLAMBEAU["accent"],
    ]


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
    [
        families.Look,
        families.TrueLineage,
        families.MysteryCult,
        families.Societas,
        # The Houses that draw their own ornaments over their family's.
        families.Bjornaer,
        families.Merinita,
        families.Verditius,
        families.ExMiscellanea,
        families.Flambeau,
        families.Jerbiton,
        families.Diedne,
    ],
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
    """A House's mark (Scriptorum's, the Order's sigil) is watermarked in
    the Inspector only as strongly as keeps every text colour readable
    over it."""
    for theme, p in _pages():
        opacity = theme.look.watermark_opacity(p)
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


def test_diedne_is_renounced_of_no_family_on_scriptorums_form() -> None:
    """Diedne is listed on its own, after the families, under Renounced;
    its look is Scriptorum's form (no family's), with uncial headings and
    its invented sign, a scraped triskelion, drawn in the app."""
    theme = liveries.named("Diedne")
    assert theme is not None and theme.group == liveries.RENOUNCED
    assert liveries.GROUPS[-1] == liveries.RENOUNCED
    assert liveries.THEMES[-1] is theme
    look = theme.look
    assert type(look).__mro__[1] is families.Look
    assert look.heading_family == fonts.DISPLAY
    assert theme.mark is not None and theme.mark.parent.name == "drawn"


@pytest.mark.usefixtures("app")
@pytest.mark.parametrize("theme", ["Scriptorum", "Scriptorum Dark"])
def test_scriptorum_watermarks_the_orders_sigil_and_keeps_its_leaves(
    theme: str,
) -> None:
    """With no House, Scriptorum watermarks the Order of Hermes's sigil at
    the Inspector's foot, faint in the watermark's ink, and still closes a
    chapter on its three leaves."""
    found = liveries.named(theme)
    assert found is not None and found.mark is None
    look, p = found.look, found.palette
    assert look.watermark == artwork.SIGIL
    image = QImage(320, 420, QImage.Format.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    look.inspector_mark(painter, QRectF(0, 0, 320, 420), p)
    painter.end()
    inked = [
        image.pixelColor(x, y)
        for x in range(0, 320, 2)
        for y in range(0, 420, 2)
        if image.pixelColor(x, y).alpha() > 0
    ]
    assert len(inked) > 500
    ink = QColor(families.watermark_ink(p))
    assert all(abs(c.red() - ink.red()) <= 2 for c in inked[:50])
    # The tailpiece is the three leaves, unchanged: no House sign.
    tail = QImage(300, 60, QImage.Format.Format_ARGB32)
    tail.fill(0)
    painter = QPainter(tail)
    look.tailpiece(painter, 300, p)
    painter.end()
    assert any(tail.pixelColor(150, y).alpha() for y in range(60))


@pytest.mark.usefixtures("app")
def test_diedne_sets_its_initials_plain_in_the_headings_ash() -> None:
    """A Diedne name's initial is a plain uncial letter in the heading's
    ash, with no gilt edge; Scriptorum's keeps its gilt."""
    font = QFont(fonts.DISPLAY)
    font.setPointSizeF(40)

    def letter(p: pal.Palette) -> set[str]:
        image = QImage(80, 80, QImage.Format.Format_ARGB32)
        image.fill(QColor(p["background"]))
        painter = QPainter(image)
        gilding.gilt_letter(painter, "L", font, QPointF(8, 66), p)
        painter.end()
        return {image.pixelColor(x, y).name() for x in range(80) for y in range(80)}

    gilt = (pal.PIGMENTS["gold"], pal.PIGMENTS["gold-light"])
    seen = letter(pal.DIEDNE)
    assert any(_near(c, pal.DIEDNE["heading"]) for c in seen)
    assert not any(_near(c, g) for c in seen for g in gilt)
    assert any(_near(c, g) for c in letter(pal.SCRIPTORUM) for g in gilt)


@pytest.mark.usefixtures("app")
def test_diedne_wears_its_rules_and_frames_but_no_other_house_does() -> None:
    """Diedne's rules, band and frames are broken off in gaps along them
    (the Inspector's frame too, through Look.worn); another House's are
    whole."""
    diedne = liveries.named("Diedne")
    other = liveries.named("Bonisagus")
    assert diedne is not None and other is not None
    frame = QRectF(10, 10, 300, 400)
    worn = diedne.look.worn(frame)
    assert worn is not None and other.look.worn(frame) is None
    top = [worn.contains(QPoint(x, 10)) for x in range(10, 310)]
    assert not all(top) and sum(top) > len(top) * 0.7

    def rule(theme: liveries.Theme) -> list[bool]:
        image = QImage(600, 40, QImage.Format.Format_ARGB32)
        image.fill(0)
        painter = QPainter(image)
        theme.look.heading_rule(painter, 600, 20, theme.palette)
        painter.end()
        return [image.pixelColor(x, 20).alpha() > 0 for x in range(40, 300)]

    assert not all(rule(diedne)) and all(rule(other))
