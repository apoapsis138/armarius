import pytest

from ars_magica_manager import catalog, sourcebooks
from ars_magica_manager.models import (
    ABILITY_CATEGORIES,
    AbilityDef,
    Character,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access


def test_seed_catalog_loads_and_covers_all_categories():
    entries = catalog.load_ability_catalog()
    assert entries
    assert {entry.category for entry in entries} == set(ABILITY_CATEGORIES)


def test_resolve_ability_name_fills_placeholder():
    entry = catalog.load_ability_catalog_by_id()["ab_craft"]
    assert entry.parameters == ["craft"]
    assert catalog.resolve_ability_name(entry, {"craft": "blacksmith"}) == (
        "Craft: Blacksmith"
    )


def test_resolve_ability_name_without_placeholder_is_unchanged():
    entry = catalog.load_ability_catalog_by_id()["ab_athletics"]
    assert catalog.resolve_ability_name(entry, {}) == "Athletics"


def test_unknown_category_is_rejected():
    with pytest.raises(ValueError, match="category"):
        AbilityDef(id="ab_bogus", name="Bogus", category="Not A Real Category")


def test_a_held_ability_is_not_offered_again_unless_templated():
    offered = {e.id for e in catalog.abilities_to_offer({"Athletics", "Craft: Smith"})}
    assert "ab_athletics" not in offered
    assert "ab_craft" in offered  # "Craft: {craft}": another Craft is fine
    assert "ab_awareness" in offered
    assert len(catalog.abilities_to_offer(set())) == len(catalog.load_ability_catalog())


def test_supplement_abilities_follow_the_sourcebooks_in_play():
    by_id = catalog.load_ability_catalog_by_id()
    kabbalah, elementalist = by_id["ab_kabbalah"], by_id["ab_elementalist_fire"]
    assert (kabbalah.category, elementalist.category) == ("Supernatural", "Hedge Art")
    assert sourcebooks.in_play(kabbalah.source, ["RoP:D"])
    assert not sourcebooks.in_play(kabbalah.source, ["HMRE"])
    assert not sourcebooks.in_play(elementalist.source, [])
    assert sourcebooks.in_play(by_id["ab_athletics"].source, [])


def test_a_supernatural_or_hedge_ability_needs_the_virtue_that_grants_it():
    magus = Character(id="m", name="M", type="magus")
    assert not creation_access.may_learn(magus, "Kabbalah")
    assert not creation_access.may_learn(magus, "Elementalist Fire")
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_kabbalah"))
    assert creation_access.may_learn(magus, "Kabbalah")
