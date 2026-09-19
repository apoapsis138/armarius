import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import LAB_CHARACTERISTICS, LabVirtueFlawDef


def test_lab_catalog_loads_and_ids_are_unique():
    entries = catalog.load_lab_virtue_flaw_catalog()
    assert entries
    ids = [entry.id for entry in entries]
    assert len(ids) == len(set(ids))


def test_lab_catalog_covers_all_three_categories():
    entries = catalog.load_lab_virtue_flaw_catalog()
    assert {entry.category for entry in entries} == {
        "Structure",
        "Outfittings",
        "Supernatural",
    }


def test_lab_catalog_modifier_keys_are_valid_characteristics():
    entries = catalog.load_lab_virtue_flaw_catalog()
    for entry in entries:
        for characteristic in entry.characteristic_modifiers:
            assert characteristic in LAB_CHARACTERISTICS


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
            characteristic_modifiers={"not_a_real_characteristic": 1},
        )
