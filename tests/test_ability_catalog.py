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


def test_the_storm_wizards_abilities_match_their_virtues():
    """Against the Dark's storm Abilities load, follow the book, and are
    granted by the Virtues of the same name."""
    by_id = catalog.load_ability_catalog_by_id()
    vfs = catalog.load_virtue_flaw_catalog_by_id()
    for name in ("Storm Calling", "Storm Riding", "Storm Fighting"):
        slug = name.lower().replace(" ", "_")
        ability, virtue = by_id[f"ab_{slug}"], vfs[f"vf_{slug}"]
        assert (ability.name, ability.category) == (name, "Supernatural")
        assert ability.source == virtue.source == "AtD"
        assert sourcebooks.in_play(ability.source, ["AtD"])
        assert not sourcebooks.in_play(ability.source, ["HMRE"])
        holder = Character(id="c", name="C", type="companion")
        assert not creation_access.may_learn(holder, name)
        holder.virtues_flaws.append(VirtueFlawInstance(vf_id=virtue.id))
        assert creation_access.may_learn(holder, name)


def test_a_supernatural_or_hedge_ability_needs_the_virtue_that_grants_it():
    magus = Character(id="m", name="M", type="magus")
    assert not creation_access.may_learn(magus, "Kabbalah")
    assert not creation_access.may_learn(magus, "Elementalist Fire")
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_kabbalah"))
    assert creation_access.may_learn(magus, "Kabbalah")


def test_church_lore_is_in_the_catalog():
    entry = catalog.load_ability_catalog_by_id()["ab_church_lore"]
    assert entry.name == "Church Lore" and entry.category == "General"


def test_theology_zoroastrian_follows_its_book():
    theology = catalog.load_ability_catalog_by_id()["ab_theology_zoroastrian"]
    assert (theology.name, theology.category) == ("Theology: Zoroastrian", "Academic")
    assert theology.source == "TC&TC" and theology.description
    assert sourcebooks.in_play(theology.source, ["TC&TC"])
    assert not sourcebooks.in_play(theology.source, [])
    assert creation_access.ability_category("Theology: Zoroastrian") == "Academic"
