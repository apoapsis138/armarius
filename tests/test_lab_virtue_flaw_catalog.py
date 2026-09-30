import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import LabVirtueFlawDef, Modifier


def test_lab_catalog_covers_all_three_categories():
    entries = catalog.load_lab_virtue_flaw_catalog()
    assert {entry.category for entry in entries} == {
        "Structure",
        "Outfittings",
        "Supernatural",
    }


def test_repeatable_entries_are_flagged():
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    assert by_id["labvf_lesser_feature"].repeatable is True
    assert by_id["labvf_superior_construction"].repeatable is False


def test_superior_construction_modifiers():
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    entry = by_id["labvf_superior_construction"]
    assert entry.type == "Virtue"
    assert entry.tier == "Free"
    assert entry.cost == 0
    assert entry.characteristic_modifiers == {"safety": 1, "aesthetics": 1}


def test_unknown_characteristic_is_rejected():
    with pytest.raises(ValueError, match="Characteristic"):
        LabVirtueFlawDef(
            id="labvf_bogus",
            name="Bogus",
            type="Virtue",
            category="Structure",
            tier="Minor",
            cost=1,
            modifiers=[
                Modifier(
                    "lab_characteristic", amount=1, target="not_a_real_characteristic"
                )
            ],
        )


def test_lab_catalog_has_every_entry_in_the_book():
    """Covenants, Chapter 9 lists 128 laboratory Virtues and Flaws (STORY-706)."""
    assert len(catalog.load_lab_virtue_flaw_catalog()) == 128


def test_book_order_tiers_and_costs_for_added_entries():
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    palatial = by_id["labvf_palatial"]
    assert (palatial.type, palatial.category, palatial.tier, palatial.cost) == (
        "Virtue",
        "Outfittings",
        "Major",
        3,
    )
    assert palatial.characteristic_modifiers == {
        "general_quality": 1,
        "upkeep": 3,
        "health": 2,
        "aesthetics": 4,
    }
    assert by_id["labvf_precarious"].repeatable is True
    assert by_id["labvf_mental_construct"].characteristic_modifiers == {
        "upkeep": -5,
        "warping": 2,
        "aesthetics": -2,
    }
    # Variable or conditional effects are left to manual adjustments.
    assert by_id["labvf_studio"].characteristic_modifiers == {}
