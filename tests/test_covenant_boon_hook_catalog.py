from collections import Counter

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.models import (
    COVENANT_BOON_HOOK_CATEGORIES,
    VIRTUE_FLAW_TIER_COST,
    Covenant,
    CovenantBoonHookDef,
    ScoredTrait,
    VirtueFlawInstance,
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
)

CASTLE = "covbh_hook_major_castle"


def test_catalog_loads_and_ids_are_unique():
    entries = catalog.load_covenant_boon_hook_catalog()
    assert entries
    ids = [entry.id for entry in entries]
    assert len(ids) == len(set(ids))


def test_catalog_counts_by_tier_after_merging_the_covenants_book():
    # 37 entries from the core chapter + 171 from Covenants Chapter Two.
    entries = catalog.load_covenant_boon_hook_catalog()
    assert len(entries) == 208
    counts = Counter((entry.type, entry.tier) for entry in entries)
    assert counts == {
        ("Hook", "Minor"): 85,
        ("Hook", "Major"): 40,
        ("Boon", "Minor"): 46,
        ("Boon", "Major"): 24,
        ("Boon", "Free"): 13,  # the book's cost-free "Free Choices"
    }


#: The original 37 entries (core rulebook chapter). The merge must update these
#: in place -- keep their ids, tiers and costs -- never duplicate them.
ORIGINAL_IDS = [
    "covbh_hook_minor_contested_resource",
    "covbh_hook_minor_favors",
    "covbh_hook_minor_hermetic_politics",
    "covbh_hook_minor_monster",
    "covbh_hook_minor_poverty",
    "covbh_hook_minor_protector",
    "covbh_hook_minor_regio",
    "covbh_hook_minor_rival",
    "covbh_hook_minor_road",
    "covbh_hook_minor_superiors",
    "covbh_hook_minor_urban",
    "covbh_hook_major_beholden",
    "covbh_hook_major_castle",
    "covbh_hook_major_monster",
    "covbh_hook_major_mundane_politics",
    "covbh_hook_major_poverty",
    "covbh_hook_major_regio",
    "covbh_hook_major_rival",
    "covbh_hook_major_road",
    "covbh_hook_major_superiors",
    "covbh_hook_major_unknown",
    "covbh_hook_major_urban",
    "covbh_boon_minor_aura",
    "covbh_boon_minor_edifice",
    "covbh_boon_minor_hidden_resources",
    "covbh_boon_minor_important_building",
    "covbh_boon_minor_prestige",
    "covbh_boon_minor_regio",
    "covbh_boon_minor_seclusion",
    "covbh_boon_minor_shell_keep",
    "covbh_boon_minor_tower_keep",
    "covbh_boon_minor_wealth",
    "covbh_boon_major_aura",
    "covbh_boon_major_curtain_walls_and_mural_towers",
    "covbh_boon_major_prestige",
    "covbh_boon_major_regio",
    "covbh_boon_major_wealth",
]


def test_original_entries_were_updated_in_place_not_duplicated():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert len(ORIGINAL_IDS) == 37
    for entry_id in ORIGINAL_IDS:
        assert entry_id in by_id, entry_id
    # No two entries share (type, tier, name): a duplicate would show up here.
    keys = [(e.type, e.tier, e.name.lower()) for e in by_id.values()]
    assert len(keys) == len(set(keys))


def test_every_entry_has_one_of_the_books_types_except_unknown():
    entries = catalog.load_covenant_boon_hook_catalog()
    untyped = [entry.id for entry in entries if not entry.category]
    assert untyped == ["covbh_hook_major_unknown"]  # only described in the intro
    assert {e.category for e in entries if e.category} == set(
        COVENANT_BOON_HOOK_CATEGORIES
    )
    for category in COVENANT_BOON_HOOK_CATEGORIES:
        assert any(e.category == category for e in entries), category


def test_existing_entries_received_their_types_from_the_book():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    expected = {
        "covbh_boon_minor_edifice": "Fortifications",  # "Edifices" in the book
        "covbh_boon_minor_important_building": "Fortifications",
        "covbh_hook_major_castle": "Fortifications",
        "covbh_boon_minor_wealth": "Resources",
        "covbh_hook_minor_poverty": "Resources",
        "covbh_boon_minor_regio": "Site",
        "covbh_hook_minor_road": "Site",
        "covbh_boon_minor_prestige": "External Relations",
        "covbh_hook_major_beholden": "External Relations",
        "covbh_hook_minor_superiors": "Residents",
        "covbh_hook_minor_protector": "Surroundings",
        # Listed under Site AND Surroundings; the existing wording is the
        # Surroundings one, so that's the type it takes (not duplicated).
        "covbh_hook_major_monster": "Surroundings",
    }
    for entry_id, category in expected.items():
        assert by_id[entry_id].category == category, entry_id


def test_free_choices_are_cost_free_boons_in_fortifications_and_residents():
    free = [e for e in catalog.load_covenant_boon_hook_catalog() if e.tier == "Free"]
    assert len(free) == 13
    assert {e.type for e in free} == {"Boon"}
    assert {e.cost for e in free} == {0}
    assert {e.category for e in free} == {"Fortifications", "Residents"}
    by_id = {e.id: e for e in free}
    assert "covbh_boon_free_manor_house" in by_id
    assert "covbh_boon_free_theocracy" in by_id  # a Style of Governance


def test_new_entries_record_prerequisites_and_flags_from_the_text():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert by_id["covbh_boon_free_ringwork"].requires == [CASTLE]
    assert (
        "any other soldier type"
        in by_id["covbh_boon_major_magical_soldiers"].description
    )
    for entry_id in (
        "covbh_boon_minor_secondary_income",
        "covbh_hook_minor_flawed_resource",
        "covbh_hook_minor_illusory_resources",
        "covbh_boon_minor_inhuman_residents",
    ):
        assert by_id[entry_id].repeatable, entry_id


def test_descriptions_dropped_the_anecdotes_but_kept_the_rules():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    everything = " ".join(e.description for e in by_id.values())
    assert "Marco" not in everything and "Belinda" not in everything
    assert "Crisp Winds" not in everything and "Calebais" not in everything
    assert "\ufffd" not in everything  # no encoding damage
    assert by_id["covbh_boon_minor_vast_aura"].description.startswith(
        "The covenant's aura fills an enormous area"
    )


def test_unknown_category_is_rejected():
    with pytest.raises(ValueError, match="category"):
        CovenantBoonHookDef(
            id="covbh_bogus_cat",
            name="Bogus",
            type="Boon",
            tier="Minor",
            cost=1,
            category="Weather",
        )


def test_weak_aura_hook_subtracts_from_the_covenant_aura():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert _effects(by_id["covbh_hook_minor_weak_aura"]) == [
        ("covenant_aura", None, -1)
    ]
    covenant = Covenant(id="c", saga_id="s", name="C", aura=3)
    covenant.boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_hook_minor_weak_aura"),
        VirtueFlawInstance(vf_id="covbh_hook_minor_weak_aura"),
    ]
    assert covenant_effective_aura(covenant, by_id) == 2  # 3 + 1 - 1 - 1


def test_every_entry_has_a_description():
    for entry in catalog.load_covenant_boon_hook_catalog():
        assert entry.description.strip(), entry.id


def test_costs_follow_tier_and_type():
    # Same 0/1/3 tiers as Virtues & Flaws; Boons spend points (+), Hooks
    # provide them (-).
    for entry in catalog.load_covenant_boon_hook_catalog():
        magnitude = VIRTUE_FLAW_TIER_COST[entry.tier]
        expected = magnitude if entry.type == "Boon" else -magnitude
        assert entry.cost == expected, entry.id


def test_names_can_repeat_across_type_and_tier():
    entries = catalog.load_covenant_boon_hook_catalog()
    regios = [entry for entry in entries if entry.name == "Regio"]
    assert {(e.type, e.tier) for e in regios} == {
        ("Hook", "Minor"),
        ("Hook", "Major"),
        ("Boon", "Minor"),
        ("Boon", "Major"),
    }
    # Distinct ids, even though the names are identical.
    assert len({e.id for e in regios}) == 4


def test_requires_and_excludes_point_at_real_entries():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    for entry in by_id.values():
        for other in (*entry.requires, *entry.excludes):
            assert other in by_id, f"{entry.id} references unknown {other!r}"


def test_castle_dependent_boons_require_the_castle_hook():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert by_id[CASTLE].type == "Hook"
    assert by_id[CASTLE].tier == "Major"
    for entry_id in (
        "covbh_boon_minor_shell_keep",
        "covbh_boon_minor_tower_keep",
        "covbh_boon_major_curtain_walls_and_mural_towers",
    ):
        assert by_id[entry_id].requires == [CASTLE], entry_id


def test_seclusion_excludes_the_road_and_urban_hooks():
    seclusion = catalog.load_covenant_boon_hook_catalog_by_id()[
        "covbh_boon_minor_seclusion"
    ]
    assert set(seclusion.excludes) == {
        "covbh_hook_minor_road",
        "covbh_hook_major_road",
        "covbh_hook_minor_urban",
        "covbh_hook_major_urban",
    }


def test_repeatable_entries_are_flagged():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    for entry_id in (
        "covbh_boon_minor_aura",
        "covbh_boon_minor_prestige",
        "covbh_boon_major_prestige",
        "covbh_hook_minor_contested_resource",
        "covbh_hook_minor_protector",
    ):
        assert by_id[entry_id].repeatable is True, entry_id
    assert by_id["covbh_boon_minor_wealth"].repeatable is False


def _effects(entry) -> list[tuple[str, str | None, float | None]]:
    return [(m.applies_to, m.activity, m.amount) for m in entry.modifiers]


def test_only_the_two_minor_aura_entries_change_the_covenant_aura():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert _effects(by_id["covbh_boon_minor_aura"]) == [("covenant_aura", None, 1)]
    # The Major Aura Boon only raises a limited area, not the covenant's score.
    assert by_id["covbh_boon_major_aura"].modifiers == []
    aura = sorted(
        e.id
        for e in by_id.values()
        if any(m.applies_to == "covenant_aura" for m in e.modifiers)
    )
    # The Minor Aura Boon (+1) and the Weak Aura Hook (-1) are the only ones.
    assert aura == ["covbh_boon_minor_aura", "covbh_hook_minor_weak_aura"]


#: The Boons that add to the size, magnificence or quantity of the covenant's
#: buildings or fortifications (the user's list, 2026-09-23): +2 Minor, +5 Major
#: to the Buildings expense.
BUILDING_BOONS = {
    "covbh_boon_minor_artillery": 2,
    "covbh_boon_major_curtain_walls_and_mural_towers": 5,
    "covbh_boon_minor_edifice": 2,
    "covbh_boon_minor_important_building": 2,
    "covbh_boon_minor_shell_keep": 2,
    "covbh_boon_minor_tower_keep": 2,
}


def test_building_boons_add_to_the_buildings_expense():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    tagged = {
        e.id: m.amount
        for e in by_id.values()
        for m in e.modifiers
        if m.applies_to == "covenant_expense" and m.activity == "buildings"
    }
    assert tagged == BUILDING_BOONS
    for entry_id, amount in BUILDING_BOONS.items():
        assert amount == {"Minor": 2, "Major": 5}[by_id[entry_id].tier], entry_id
    # Edifice and Important Building may be taken several times; each counts.
    assert by_id["covbh_boon_minor_edifice"].repeatable
    assert by_id["covbh_boon_minor_important_building"].repeatable


def test_unknown_modifier_is_rejected():
    with pytest.raises(ValueError, match="applies_to"):
        CovenantBoonHookDef.from_dict(
            {
                "id": "covbh_bogus",
                "name": "Bogus",
                "type": "Boon",
                "tier": "Minor",
                "cost": 1,
                "modifiers": [{"applies_to": "not_a_score", "amount": 1}],
            }
        )
    with pytest.raises(ValueError, match="activity"):
        CovenantBoonHookDef.from_dict(
            {
                "id": "covbh_bogus",
                "name": "Bogus",
                "type": "Boon",
                "tier": "Minor",
                "cost": 1,
                "modifiers": [
                    {"applies_to": "covenant_expense", "activity": "moat", "amount": 1}
                ],
            }
        )


def test_wrong_cost_sign_or_magnitude_is_rejected():
    with pytest.raises(ValueError, match="Hooks provide"):
        CovenantBoonHookDef(
            id="covbh_bad_hook", name="Bad", type="Hook", tier="Minor", cost=1
        )
    with pytest.raises(ValueError, match="Boons cost"):
        CovenantBoonHookDef(
            id="covbh_bad_boon", name="Bad", type="Boon", tier="Minor", cost=-1
        )
    with pytest.raises(ValueError, match="cost"):
        CovenantBoonHookDef(
            id="covbh_bad_tier", name="Bad", type="Boon", tier="Major", cost=1
        )


def test_free_tier_is_supported_even_though_the_chapter_lists_none():
    entry = CovenantBoonHookDef(
        id="covbh_free", name="Free One", type="Boon", tier="Free", cost=0
    )
    assert entry.cost == 0


def test_effective_aura_adds_every_attached_aura_boon():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    covenant = Covenant(id="cov1", saga_id="s", name="C", aura=3)
    assert covenant_effective_aura(covenant, by_id) == 3

    covenant.boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_wealth"),  # no aura effect
        VirtueFlawInstance(vf_id="covbh_boon_major_aura"),  # limited area only
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),
        VirtueFlawInstance(vf_id="covbh_not_in_catalog"),  # ignored, not an error
    ]
    assert covenant_effective_aura(covenant, by_id) == 5


def test_covenant_boons_hooks_round_trip_through_from_dict():
    covenant = Covenant.from_dict(
        {
            "id": "cov1",
            "saga_id": "s",
            "name": "C",
            "boons_hooks": [{"vf_id": "covbh_boon_minor_aura", "params": {}}],
        }
    )
    assert covenant.boons_hooks == [VirtueFlawInstance(vf_id="covbh_boon_minor_aura")]
    # A pre-existing save with no boons_hooks key still loads.
    assert (
        Covenant.from_dict({"id": "c", "saga_id": "s", "name": "C"}).boons_hooks == []
    )


def test_boon_and_hook_points_are_totalled_separately_and_both_positive():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    covenant = Covenant(id="c", saga_id="s", name="C")
    assert covenant_boon_points(covenant, by_id) == 0
    assert covenant_hook_points(covenant, by_id) == 0

    covenant.boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),  # 1
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),  # 1
        VirtueFlawInstance(vf_id="covbh_boon_major_wealth"),  # 3
        VirtueFlawInstance(vf_id="covbh_hook_minor_rival"),  # 1
        VirtueFlawInstance(vf_id="covbh_hook_major_castle"),  # 3
        VirtueFlawInstance(vf_id="covbh_not_in_catalog"),  # ignored
    ]
    assert covenant_boon_points(covenant, by_id) == 5
    assert covenant_hook_points(covenant, by_id) == 4


def test_describe_boon_hook_appends_the_optional_detail():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    plain = VirtueFlawInstance(vf_id="covbh_boon_minor_edifice")
    named = VirtueFlawInstance(
        vf_id="covbh_boon_minor_edifice",
        params={"detail": " Tower of the Silver Iris "},
    )
    blank = VirtueFlawInstance(
        vf_id="covbh_boon_minor_edifice", params={"detail": "  "}
    )
    assert catalog.describe_boon_hook(plain, by_id) == "Edifice"
    assert (
        catalog.describe_boon_hook(named, by_id) == "Edifice - Tower of the Silver Iris"
    )
    assert catalog.describe_boon_hook(blank, by_id) == "Edifice"
    unknown = VirtueFlawInstance(vf_id="covbh_gone")
    assert "not in catalog" in catalog.describe_boon_hook(unknown, by_id)


def test_covenant_reputations_round_trip_and_default_empty_for_old_saves():
    covenant = Covenant.from_dict(
        {
            "id": "c",
            "saga_id": "s",
            "name": "C",
            "reputations": [{"name": "Feared", "score": 2}],
        }
    )
    assert covenant.reputations == [ScoredTrait(name="Feared", score=2)]
    assert (
        Covenant.from_dict({"id": "c", "saga_id": "s", "name": "C"}).reputations == []
    )
