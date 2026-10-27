"""Each Ability's mark: a woodcut block with a charge cut out of it, drawn
in code, in its row of the Abilities chapter and large beside it."""

from __future__ import annotations

import os

import pytest

pytest.importorskip("PySide6")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication
from screen_helpers import _sample_saga_with_covenant

from ars_magica_manager import catalog, storage
from ars_magica_manager.gui import marks
from ars_magica_manager.gui.character_sheet import (
    ABILITY_MARK_LARGE,
    ABILITY_ROW,
    CharacterSheet,
)
from ars_magica_manager.gui.mark_charges import (
    CATEGORIES,
    DETAILS,
    IMAGES,
    MARKS,
    PLAIN,
)
from ars_magica_manager.gui.window import MainWindow
from ars_magica_manager.models import AbilityDef, Saga
from ars_magica_manager.models.traits import Ability


@pytest.fixture(scope="module")
def app():
    return QApplication.instance() or QApplication([])


def test_every_catalog_ability_has_its_own_mark():
    missing = [
        a.name
        for a in catalog.load_ability_catalog()
        if marks.key(a.name, a.category) in CATEGORIES
    ]
    assert missing == []


def test_a_named_ability_shares_its_kinds_mark_and_an_unknown_one_its_categorys():
    assert marks.key("Craft: Smith") == "Craft"
    assert marks.key("Area Lore (Normandy)") == "Area Lore"
    assert marks.key("Dead Language: Latin") == "Dead Language"
    assert marks.key("Theology: Christian") == "Theology: Christian"
    assert marks.key("Invented Skill", "Martial") == "Martial"
    assert marks.key("Invented Skill", "No Such Category") == "General"


def test_the_registries_name_only_marks_that_exist():
    drawn = set(MARKS) | set(IMAGES) | set(CATEGORIES)
    assert set(DETAILS) <= drawn
    assert set(PLAIN) <= drawn


@pytest.mark.parametrize("size", [24, ABILITY_MARK_LARGE])
def test_every_mark_is_a_dark_block_with_a_light_charge(app, size):
    names = [*MARKS, *IMAGES, *CATEGORIES]
    for name in names:
        image = marks.pixmap(name, "", "#2c221e", size).toImage()
        side = image.width()
        assert side == size * 2
        corner = image.pixelColor(side // 8, side // 8)
        assert corner.alpha() > 200, name
        # Some of the block is cut away for the charge.
        clear = sum(
            image.pixelColor(x, y).alpha() < 60
            for x in range(side // 5, side * 4 // 5, 2)
            for y in range(side // 5, side * 4 // 5, 2)
        )
        assert clear > 10, name


def test_the_abilities_chapter_shows_each_mark_and_the_chosen_one_large(app):
    saga = _sample_saga_with_covenant()
    saga.characters[0].abilities = [
        Ability("Dead Language: Latin", "Academic", 75, "Hermetic usage"),
        Ability("Parma Magica", "Arcane", 30, "Ignem"),
    ]
    storage.save_saga(saga)
    window = MainWindow(saga_ids=[saga.id])
    window.show_character("char1")
    sheet = window.page()
    assert isinstance(sheet, CharacterSheet)
    sheet.open_chapter("Abilities")
    table = sheet.ability_table
    assert table.sizeHintForRow(0) == ABILITY_ROW
    model = table.model_
    rows = [model.item(g).child(0) for g in range(model.rowCount())]
    assert all(row.icon().isNull() is False for row in rows)
    table.setCurrentIndex(model.indexFromItem(rows[0]))
    symbol = sheet.codex.inspector.symbol
    assert symbol.isVisibleTo(sheet)
    shown = symbol.pixmap()
    assert shown.deviceIndependentSize().width() == ABILITY_MARK_LARGE
    # Drawn in the heading colour.
    image = shown.toImage()
    corner = image.pixelColor(image.width() // 8, image.height() // 8)
    assert corner.rgb() == QColor(window.palette_["heading"]).rgb()
    assert sheet.codex.inspector.title.text() == rows[0].text()


def test_each_rhine_gild_bears_its_tree_cut_as_a_mark(app):
    from ars_magica_manager.gui.gild_charges import GILD_DETAILS, GILD_PLAIN, GILDS
    from ars_magica_manager.tribunal_packages.rhine import GILD_TREES, gild_tree

    assert set(GILDS) == set(GILD_TREES) == set(GILD_DETAILS)
    assert GILD_PLAIN <= set(GILDS)
    assert gild_tree("Oak Gild (Eichengilde)") == "Oak"
    assert gild_tree("The Apple") == "Apple"
    assert gild_tree("Mercantile") is None
    assert gild_tree("Oak Gild, Ash Gild") is None  # a roster cell of two
    assert marks.key("gild:Oak") == "gild:Oak"
    for tree in GILD_TREES:
        image = marks.gild_pixmap(tree, "#2c221e", 64).toImage()
        side = image.width()
        assert image.pixelColor(side // 8, side // 8).alpha() > 200, tree
        clear = sum(
            image.pixelColor(x, y).alpha() < 60
            for x in range(side // 5, side * 4 // 5, 2)
            for y in range(side // 5, side * 4 // 5, 2)
        )
        assert clear > 10, tree


# A saga's own Abilities (HoH:S pp. 103-106).


def test_a_saga_ability_is_drawn_with_its_categorys_mark():
    """Only the saga's own Abilities go without a mark of their own: each
    is drawn with its category's (no art is made for it)."""
    saga = Saga(id="test_saga", name="Saga")
    for name, category in (
        ("Call the Tide", "Supernatural"),
        ("Tide Lore", "Academic"),
    ):
        saga.custom_abilities.append(
            AbilityDef(id=f"custom_ability_{len(name)}", name=name, category=category)
        )
    catalog.use_saga(saga)
    unmarked = [
        a.name
        for a in catalog.load_ability_catalog()
        if marks.key(a.name, a.category) in CATEGORIES
    ]
    assert unmarked == ["Call the Tide", "Tide Lore"]
    assert marks.key("Call the Tide", "Supernatural") == "Supernatural"
    assert marks.key("Tide Lore", "Academic") == "Academic"
