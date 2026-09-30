from dataclasses import asdict

from ars_magica_manager.laboratories import (
    lab_aura_total,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_net_vf_points,
    lab_occupied_size,
)
from ars_magica_manager.models import (
    BOON_HOOK_DESCRIPTION,
    BOON_HOOK_DETAIL,
    BOON_HOOK_UNKNOWN,
    Character,
    Covenant,
    LabCharacteristics,
    Laboratory,
    LabVirtueFlawDef,
    Modifier,
    Saga,
    VirtueFlawInstance,
    add_raw_vis,
    assign_laboratory,
    assign_laboratory_owner,
    boon_hook_params,
    character_age,
    next_season,
    replace_raw_vis,
)


def test_character_age_computes_from_year_born():
    assert character_age(year_born=1180, current_year=1220) == 40


def test_character_age_is_none_without_year_born():
    assert character_age(year_born=None, current_year=1220) is None


def test_character_from_dict_migrates_legacy_inventory_strings():
    # Pre-STORY-203 saves held Inventory as plain description strings.
    character = Character.from_dict(
        {
            "id": "char_1",
            "name": "Leandro",
            "type": "magus",
            "inventory": ["Fine wool cloak", "A dagger"],
        }
    )
    assert [item.name for item in character.inventory] == [
        "Fine wool cloak",
        "A dagger",
    ]
    assert all(item.kind == "item" for item in character.inventory)


def test_character_from_dict_migrates_legacy_spells_known_ids():
    # Pre-STORY-203 saves held spells_known as bare spell ids.
    character = Character.from_dict(
        {
            "id": "char_1",
            "name": "Leandro",
            "type": "magus",
            "spells_known": ["spell_pilum_of_fire"],
        }
    )
    assert len(character.spells_known) == 1
    known = character.spells_known[0]
    assert known.spell_id == "spell_pilum_of_fire"
    assert known.mastery_score == 0
    assert known.mastery_abilities == []


def test_character_from_dict_migrates_legacy_confidence():
    # Pre-STORY-208 saves held a single "confidence" instead of the
    # Score/Points pair.
    character = Character.from_dict(
        {
            "id": "char_1",
            "name": "Leandro",
            "type": "magus",
            "background": {"confidence": 3},
        }
    )
    assert character.background.confidence_score == 3
    assert character.background.confidence_points == 0


def test_laboratory_from_dict_migrates_legacy_size_and_drops_legacy_aura():
    # Simulates a save from before this session: flat "size", and "aura"
    # which has since moved to Covenant.
    lab = Laboratory.from_dict(
        {
            "id": "lab_1",
            "covenant_id": "cov_1",
            "name": "Obsidian Crucible",
            "size": 2,
            "aura": 3,
        }
    )
    assert lab.characteristics.size == 2
    assert not hasattr(lab, "aura")


_LAB_VF_CATALOG = {
    "labvf_superior_construction": LabVirtueFlawDef(
        id="labvf_superior_construction",
        name="Superior Construction",
        type="Virtue",
        category="Structure",
        tier="Free",
        cost=0,
        modifiers=[
            Modifier("lab_characteristic", amount=1, target="safety"),
            Modifier("lab_characteristic", amount=1, target="aesthetics"),
        ],
    ),
    "labvf_deformed": LabVirtueFlawDef(
        id="labvf_deformed",
        name="Deformed",
        type="Flaw",
        category="Structure",
        tier="Free",
        cost=0,
        modifiers=[
            Modifier("lab_characteristic", amount=-1, target="safety"),
            Modifier("lab_characteristic", amount=-1, target="aesthetics"),
        ],
    ),
    "labvf_extensive_stores": LabVirtueFlawDef(
        id="labvf_extensive_stores",
        name="Extensive Stores",
        type="Virtue",
        category="Structure",
        tier="Minor",
        cost=1,
        modifiers=[Modifier("lab_characteristic", amount=2, target="safety")],
    ),
}


def _sample_lab(**overrides) -> Laboratory:
    defaults = {
        "id": "lab_1",
        "covenant_id": "cov_1",
        "name": "Test Lab",
        "characteristics": LabCharacteristics(size=1, safety=-1),
        "virtues_flaws": [
            VirtueFlawInstance(vf_id="labvf_superior_construction"),
            VirtueFlawInstance(vf_id="labvf_deformed"),
        ],
    }
    defaults.update(overrides)
    return Laboratory(**defaults)


def test_lab_characteristic_total_sums_manual_virtue_and_flaw():
    lab = _sample_lab()
    manual, virtue_sum, flaw_sum, total = lab_characteristic_total(
        lab, _LAB_VF_CATALOG, "safety"
    )
    assert (manual, virtue_sum, flaw_sum, total) == (-1, 1, -1, -1)


def test_lab_characteristic_total_for_a_characteristic_with_no_modifiers():
    lab = _sample_lab()
    assert lab_characteristic_total(lab, _LAB_VF_CATALOG, "warping") == (0, 0, 0, 0)


def test_lab_net_vf_points_sums_catalog_costs():
    lab = _sample_lab(
        virtues_flaws=[VirtueFlawInstance(vf_id="labvf_extensive_stores")]
    )
    assert lab_net_vf_points(lab, _LAB_VF_CATALOG) == 1


def test_lab_occupied_size_and_free_virtues_and_base_safety():
    lab = _sample_lab(
        characteristics=LabCharacteristics(size=2, refinement=0),
        virtues_flaws=[VirtueFlawInstance(vf_id="labvf_extensive_stores")],
    )
    # net VF points = 1, refinement = 0
    assert lab_occupied_size(lab, _LAB_VF_CATALOG) == 1
    # (size + refinement) - net VF points = (2 + 0) - 1
    assert lab_free_virtues(lab, _LAB_VF_CATALOG) == 1
    # refinement - max(occupied_size, 0) = 0 - 1
    assert lab_base_safety(lab, _LAB_VF_CATALOG) == -1


def test_lab_aura_total_adds_the_modifier_to_the_covenant_aura():
    lab = Laboratory(id="lab_1", covenant_id="cov_1", name="Lab", aura_modifier=2)
    assert lab_aura_total(lab, covenant_aura=3) == 5
    lab.aura_modifier = -4
    assert lab_aura_total(lab, covenant_aura=3) == -1


def test_next_season_steps_through_the_year_and_rolls_over_after_winter():
    assert next_season("Spring", 1220) == ("Summer", 1220)
    assert next_season("Summer", 1220) == ("Autumn", 1220)
    assert next_season("Autumn", 1220) == ("Winter", 1220)
    assert next_season("Winter", 1220) == ("Spring", 1221)


def test_covenant_modifiers_count_every_instance_and_filter_by_activity():
    from ars_magica_manager import catalog
    from ars_magica_manager.covenants import (
        covenant_effective_aura,
        covenant_modifier_total,
        covenant_modifiers,
    )
    from ars_magica_manager.models import (
        Covenant,
        VirtueFlawInstance,
    )

    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    cov = Covenant(id="c", saga_id="s", name="C", aura=3)
    cov.boons_hooks = [
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_aura"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice"),
        VirtueFlawInstance(vf_id="covbh_boon_minor_edifice"),
        VirtueFlawInstance(vf_id="not_in_the_catalog"),
    ]
    assert covenant_effective_aura(cov, by_id) == 5  # 3 + 1 + 1: they stack
    pairs = covenant_modifiers(cov, by_id, "covenant_expense", "buildings")
    assert [entry.name for entry, _ in pairs] == ["Edifice", "Edifice"]
    assert covenant_modifier_total(cov, by_id, "covenant_expense", "buildings") == 4
    assert covenant_modifier_total(cov, by_id, "lab_total") == 0


def _saga_with_two_labs() -> Saga:
    return Saga(
        id="s",
        name="Saga",
        characters=[
            Character(id="a", name="A", type="magus", assigned_lab_id="lab1"),
            Character(id="b", name="B", type="magus"),
        ],
        laboratories=[
            Laboratory(id="lab1", covenant_id="c", name="One", owner_id="a"),
            Laboratory(id="lab2", covenant_id="c", name="Two"),
        ],
    )


def _owners(saga: Saga) -> tuple[dict, dict]:
    return (
        {c.id: c.assigned_lab_id for c in saga.characters},
        {lab.id: lab.owner_id for lab in saga.laboratories},
    )


def test_assign_laboratory_moves_a_magus_and_frees_the_old_lab():
    saga = _saga_with_two_labs()
    assign_laboratory(saga, saga.characters[0], "lab2")
    assert _owners(saga) == ({"a": "lab2", "b": None}, {"lab1": None, "lab2": "a"})


def test_assign_laboratory_takes_a_lab_from_its_previous_owner():
    saga = _saga_with_two_labs()
    assign_laboratory(saga, saga.characters[1], "lab1")
    assert _owners(saga) == ({"a": None, "b": "lab1"}, {"lab1": "b", "lab2": None})


def test_assign_laboratory_none_just_frees_the_lab():
    saga = _saga_with_two_labs()
    assign_laboratory(saga, saga.characters[0], None)
    assert _owners(saga) == ({"a": None, "b": None}, {"lab1": None, "lab2": None})


def test_assign_laboratory_owner_works_from_the_labs_side():
    saga = _saga_with_two_labs()
    assign_laboratory_owner(saga, saga.laboratories[1], "a")
    assert _owners(saga) == ({"a": "lab2", "b": None}, {"lab1": None, "lab2": "a"})
    assign_laboratory_owner(saga, saga.laboratories[1], None)
    assert _owners(saga) == ({"a": None, "b": None}, {"lab1": None, "lab2": None})


def test_add_and_replace_raw_vis_merge_into_an_art_already_held():
    pool = {"creo": 2}
    add_raw_vis(pool, "creo", 3)
    add_raw_vis(pool, "vim", 1)
    assert pool == {"creo": 5, "vim": 1}
    replace_raw_vis(pool, "vim", "creo", 4)
    assert pool == {"creo": 9}
    replace_raw_vis(pool, "creo", "ignem", 2)
    assert pool == {"ignem": 2}


def test_boon_hook_params_keeps_other_keys_and_only_non_empty_text():
    base = {"other": "kept", BOON_HOOK_DETAIL: "old"}
    assert boon_hook_params(" Tower ", "", base) == {
        "other": "kept",
        BOON_HOOK_DETAIL: "Tower",
    }
    assert boon_hook_params("", " Tall ") == {BOON_HOOK_DESCRIPTION: "Tall"}


def test_boon_hook_params_sets_and_clears_the_unknown_mark():
    marked = boon_hook_params("", "", {"other": "kept"}, unknown=True)
    assert marked == {"other": "kept", BOON_HOOK_UNKNOWN: "yes"}
    assert boon_hook_params("", "", marked) == {"other": "kept"}


def test_a_stale_key_or_a_null_section_does_not_make_a_save_unloadable():
    # B15: these from_dicts passed every key through, so a field removed in a
    # later version (or a null where a section was expected) raised.
    saga = Saga(id="s", name="S")
    saga.covenants = [Covenant(id="c", saga_id="s", name="C")]
    saga.characters = [Character(id="ch", name="A", type="magus")]
    saga.laboratories = [Laboratory(id="l", covenant_id="c", name="L")]
    data = asdict(saga)
    covenant = data["covenants"][0]
    covenant["loyalty"] = None
    covenant["population"] = None
    covenant["economics"] = {
        "income_sources": [
            {"id": "i", "name": "Rents", "type": "Typical", "retired": 1}
        ]
    }
    covenant["possessions"] = [
        {"id": "p", "kind": "item", "name": "Chest", "retired": 1}
    ]
    data["characters"][0]["retired"] = 1
    data["laboratories"][0]["retired"] = 1

    loaded = Saga.from_dict(data)
    assert loaded.characters[0].name == "A"
    assert loaded.laboratories[0].name == "L"
    loaded_covenant = loaded.covenants[0]
    assert loaded_covenant.economics.income_sources[0].name == "Rents"
    assert loaded_covenant.possessions[0].name == "Chest"
    assert loaded_covenant.loyalty == Covenant(id="x", saga_id="s", name="X").loyalty
