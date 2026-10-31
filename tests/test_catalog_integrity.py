"""Every data catalog loads cleanly: entries with unique ids, a description
where the book gives one, and no mis-decoded text. (Each entry's shape --
tiers, costs, categories, targets -- is checked as it loads; see the Defs'
__post_init__ in models/definitions.py. Which books a catalog cites is checked in
test_sourcebooks.py.)"""

import dataclasses
from dataclasses import fields, is_dataclass

import pytest

from ars_magica_manager import catalog


def _catalogs() -> dict[str, list]:
    return {
        "virtues & flaws": catalog.load_virtue_flaw_catalog(),
        "laboratory virtues & flaws": catalog.load_lab_virtue_flaw_catalog(),
        "laboratory features": catalog.load_lab_feature_catalog(),
        "covenant boons & hooks": catalog.load_covenant_boon_hook_catalog(),
        "abilities": catalog.load_ability_catalog(),
        "houses": catalog.load_house_catalog(),
        # One id space: a possession's book entry can be either.
        "weapons & armor": catalog.load_weapon_catalog()
        + catalog.load_armor_catalog()
        + catalog.load_armor_piece_catalog(),
        "spells": catalog.load_spell_catalog(),
        "shapes & materials": catalog.load_shape_material_catalog(),
    }


def _texts(entry) -> list[str]:
    assert is_dataclass(entry)
    return [
        value
        for field in fields(entry)
        if isinstance(value := getattr(entry, field.name), str)
    ]


def test_every_catalog_has_entries_with_unique_ids():
    for name, entries in _catalogs().items():
        ids = [entry.id for entry in entries]
        assert ids, name
        duplicates = {i for i in ids if ids.count(i) > 1}
        assert not duplicates, (name, duplicates)


def test_entries_have_their_descriptions():
    """The book gives no description of a natural weapon; shapes and
    materials have bonuses rather than one."""
    natural = {w.id for w in catalog.load_weapon_catalog(tables=("natural",))}
    for name, entries in _catalogs().items():
        if name in ("shapes & materials", "spells"):
            continue
        for entry in entries:
            if entry.id in natural:
                continue
            assert entry.description.strip(), (name, entry.id)


def test_no_text_was_mis_decoded():
    for name, entries in _catalogs().items():
        for entry in entries:
            for text in _texts(entry):
                assert "�" not in text, (name, entry.id, text)


def test_a_corrected_spell_name_keeps_its_id():
    """Saves hold the id, so fixing a name must leave it alone."""
    spell = catalog.load_spell_catalog_by_id()[
        "spell_ominous_evitation_of_the_weighty_stone"
    ]
    assert spell.name == "Ominous Levitation of the Weighty Stone"
    assert (spell.source, spell.page) == ("HoH:S", "38")


def test_the_shared_catalogs_cannot_be_changed_by_accident():
    """Every caller gets the same cached catalog, so a change would reach
    them all: the by-id maps are read-only and the definitions frozen."""
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    some_id, definition = next(iter(by_id.items()))
    with pytest.raises(TypeError):
        by_id[some_id] = definition  # type: ignore[index]
    with pytest.raises(dataclasses.FrozenInstanceError):
        definition.name = "Changed"  # type: ignore[misc]
