from collections import Counter

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
    covenant_boon_points,
    covenant_effective_aura,
    covenant_hook_points,
)
from ars_magica_manager.models import (
    BOON_HOOK_UNKNOWN,
    COVENANT_BOON_HOOK_CATEGORIES,
    Covenant,
    CovenantBoonHookDef,
    VirtueFlawInstance,
)

CASTLE = "covbh_hook_major_castle"


def test_catalog_counts_by_tier_after_merging_the_covenants_book():
    # 37 entries from the core chapter + 179 from Covenants Chapter Two
    # (checked entry by entry against
    # reference/covenants-boons-and-hooks-ref.md).
    entries = catalog.load_covenant_boon_hook_catalog()
    assert len(entries) == 216
    counts = Counter((entry.type, entry.tier) for entry in entries)
    assert counts == {
        ("Hook", "Minor"): 87,
        ("Hook", "Major"): 41,
        ("Boon", "Minor"): 46,
        ("Boon", "Major"): 24,
        ("Boon", "Free"): 18,  # the book's cost-free "Free Choices"
    }


def test_the_entries_story_705_found_missing_are_present():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    for entry_id in (
        "covbh_boon_minor_writ_of_crenellation",
        "covbh_hook_minor_haunted",
        "covbh_hook_minor_non_magical_regio",
        "covbh_hook_major_monster_surroundings",
        "covbh_boon_free_hall_keep",
        "covbh_boon_free_courtyard_castle",
        "covbh_boon_free_gatehouse_keep",
        "covbh_boon_free_chemise",
        "covbh_boon_free_barbican_and_moat",
    ):
        assert entry_id in by_id, entry_id
    # "Historical" was the Crossbows sidebar's weapon stats, not a Boon.
    assert "covbh_boon_minor_historical" not in by_id
    # The Writ is a legal right to fortify: no Buildings cost (user, 2026-09-27).
    writ = by_id["covbh_boon_minor_writ_of_crenellation"]
    assert writ.requires == [CASTLE]
    assert writ.modifiers == []


def test_every_entry_names_its_source_book():
    for entry in catalog.load_covenant_boon_hook_catalog():
        assert entry.source in ("ArM5; Covenants", "Covenants"), entry.id
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert by_id["covbh_boon_minor_aura"].source == "ArM5; Covenants"
    assert by_id["covbh_hook_minor_haunted"].source == "Covenants"


def test_repeat_limits_and_requires_any():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert by_id["covbh_boon_minor_aura"].max_count == 7
    assert by_id["covbh_boon_minor_healthy_feature"].max_count == 3
    assert by_id["covbh_boon_minor_edifice"].max_count is None  # no limit
    soldiers = by_id["covbh_boon_major_magical_soldiers"].requires_any
    assert "covbh_boon_major_heavy_cavalry" in soldiers
    assert "covbh_boon_free_peasants" in soldiers
    assert by_id["covbh_hook_minor_non_magical_regio"].requires_any == [
        "covbh_hook_minor_regio",
        "covbh_hook_major_regio",
    ]
    with pytest.raises(ValueError, match="max_count"):
        CovenantBoonHookDef(
            id="covbh_x", name="X", type="Boon", tier="Minor", cost=1, max_count=2
        )


def test_only_minor_hooks_may_be_unknown():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    unknown = [e for e in by_id.values() if e.unknown]
    assert {(e.type, e.tier) for e in unknown} == {("Hook", "Minor")}
    assert by_id["covbh_hook_minor_rival"].unknown
    assert by_id["covbh_hook_minor_favors"].unknown  # ArM5's text allows it
    assert not by_id["covbh_hook_minor_road"].unknown


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
    # No two entries share (type, tier, name, category): a duplicate would show
    # up here. (The two Major Monster Hooks differ by category.)
    keys = [(e.type, e.tier, e.name.lower(), e.category) for e in by_id.values()]
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
        # The table lists a Major Monster under Site and under Surroundings;
        # both are in the catalog.
        "covbh_hook_major_monster": "Site",
        "covbh_hook_major_monster_surroundings": "Surroundings",
    }
    for entry_id, category in expected.items():
        assert by_id[entry_id].category == category, entry_id


def test_free_choices_are_cost_free_boons_in_fortifications_and_residents():
    free = [e for e in catalog.load_covenant_boon_hook_catalog() if e.tier == "Free"]
    assert len(free) == 18
    assert {e.type for e in free} == {"Boon"}
    assert {e.cost for e in free} == {0}
    assert {e.category for e in free} == {"Fortifications", "Residents"}
    by_id = {e.id: e for e in free}
    assert "covbh_boon_free_manor_house" in by_id
    assert "covbh_boon_free_theocracy" in by_id  # a Style of Governance
    # The keep alternatives and barbican/moat come with Curtain Walls.
    curtain = "covbh_boon_major_curtain_walls_and_mural_towers"
    assert by_id["covbh_boon_free_hall_keep"].requires == [curtain]


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
        for other in (*entry.requires, *entry.requires_any, *entry.excludes):
            assert other in by_id, f"{entry.id} references unknown {other!r}"


def test_castle_dependent_boons_require_the_castle_hook():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    assert by_id[CASTLE].type == "Hook"
    assert by_id[CASTLE].tier == "Major"
    for entry_id in (
        "covbh_boon_minor_shell_keep",
        "covbh_boon_minor_tower_keep",
        "covbh_boon_major_curtain_walls_and_mural_towers",
        # Only the book's table says so for these.
        "covbh_boon_minor_artillery",
        "covbh_boon_minor_bedrock",
        "covbh_boon_major_superior_engineering",
        "covbh_hook_minor_crumbling",
        "covbh_hook_minor_outbuildings",
        "covbh_hook_minor_wooden",
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
#: buildings or fortifications (the user's list, 2026-09-23, extended
#: 2026-09-27 with Bedrock, Vast and Labyrinthine, Natural Fortress, Magical
#: Fortress and Superior Engineering): +2 Minor, +5 Major to the Buildings
#: expense.
BUILDING_BOONS = {
    "covbh_boon_minor_artillery": 2,
    "covbh_boon_minor_bedrock": 2,
    "covbh_boon_major_curtain_walls_and_mural_towers": 5,
    "covbh_boon_minor_edifice": 2,
    "covbh_boon_minor_important_building": 2,
    "covbh_boon_major_magical_fortress": 5,
    "covbh_boon_major_natural_fortress": 5,
    "covbh_boon_minor_shell_keep": 2,
    "covbh_boon_major_superior_engineering": 5,
    "covbh_boon_minor_tower_keep": 2,
    "covbh_boon_minor_vast_and_labyrinthine": 2,
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


def test_an_unknown_minor_hook_counts_as_major():
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    unknown = {BOON_HOOK_UNKNOWN: "yes"}
    rival = VirtueFlawInstance(vf_id="covbh_hook_minor_rival", params=unknown)
    # Not in the book's "may be Unknown" list: a stale mark counts nothing.
    road = VirtueFlawInstance(vf_id="covbh_hook_minor_road", params=unknown)
    assert by_id["covbh_hook_minor_rival"].unknown
    assert not by_id["covbh_hook_minor_road"].unknown
    assert boon_hook_is_unknown(rival, by_id[rival.vf_id])
    assert not boon_hook_is_unknown(road, by_id[road.vf_id])

    covenant = Covenant(id="c", saga_id="s", name="C")
    covenant.boons_hooks = [rival, road]
    assert covenant_hook_points(covenant, by_id) == UNKNOWN_HOOK_POINTS + 1


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


def test_boon_hook_sort_key_orders_by_type_then_tier_then_name():
    entries = sorted(
        catalog.load_covenant_boon_hook_catalog(), key=catalog.boon_hook_sort_key
    )
    keys = [catalog.boon_hook_sort_key(e) for e in entries]
    assert keys == sorted(keys)
    tiers = [e.tier for e in entries if e.category == entries[0].category]
    assert tiers == sorted(tiers, key=["Free", "Minor", "Major"].index)
