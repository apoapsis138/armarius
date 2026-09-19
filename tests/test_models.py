from ars_magica_manager.models import (
    Aging,
    Background,
    Character,
    Description,
    HermeticBackground,
    LabCharacteristics,
    Laboratory,
    LabVirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
    character_age,
    lab_base_safety,
    lab_characteristic_total,
    lab_free_virtues,
    lab_net_vf_points,
    lab_occupied_size,
)


def test_character_age_computes_from_year_born():
    assert character_age(year_born=1180, current_year=1220) == 40


def test_character_age_is_none_without_year_born():
    assert character_age(year_born=None, current_year=1220) is None


def test_character_from_dict_defaults_new_fields_for_pre_existing_saves():
    # Simulates a save written before this session's fields existed -- none
    # of the new keys are present, so everything should fall back to
    # dataclass defaults rather than raising.
    character = Character.from_dict(
        {"id": "char_1", "name": "Leandro", "type": "magus"}
    )
    assert character.background == Background()
    assert character.description == Description()
    assert character.aging == Aging()
    assert character.wounds == Wounds()
    assert character.fatigue_level == "fresh"
    assert character.personality_traits == []
    assert character.reputations == []
    assert character.raw_vis == {}
    assert character.hermetic == HermeticBackground()


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
        characteristic_modifiers={"safety": 1, "aesthetics": 1},
    ),
    "labvf_deformed": LabVirtueFlawDef(
        id="labvf_deformed",
        name="Deformed",
        type="Flaw",
        category="Structure",
        tier="Free",
        cost=0,
        characteristic_modifiers={"safety": -1, "aesthetics": -1},
    ),
    "labvf_extensive_stores": LabVirtueFlawDef(
        id="labvf_extensive_stores",
        name="Extensive Stores",
        type="Virtue",
        category="Structure",
        tier="Minor",
        cost=1,
        characteristic_modifiers={"safety": 2},
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
