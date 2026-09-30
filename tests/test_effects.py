"""The shared effect lookup (STORY-804): one collector over characters,
laboratories and covenants, how flat amounts and multipliers stack, the lab
catalog on the shared Modifier shape, and Puissant as a character effect."""

import pytest

from ars_magica_manager import catalog, sheet_text
from ars_magica_manager.laboratories import lab_characteristic_total
from ars_magica_manager.models import (
    Ability,
    Laboratory,
    LabVirtueFlawDef,
    Modifier,
    VirtueFlawDef,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import effects, scores


def _entry(id_: str, type_: str, *modifiers: Modifier, **kw) -> VirtueFlawDef:
    return VirtueFlawDef(
        id=id_,
        name=kw.pop("name", id_),
        type=type_,  # type: ignore[arg-type]
        category="General",
        tier="Minor",
        cost=1 if type_ == "Virtue" else -1,
        modifiers=list(modifiers),
        **kw,
    )


CATALOG = {
    "bonus": _entry("bonus", "Virtue", Modifier("study_total", amount=3)),
    "reading": _entry(
        "reading", "Virtue", Modifier("study_total", amount=2, activity="reading")
    ),
    "affinity": _entry(
        "affinity",
        "Virtue",
        Modifier("art_xp_gain", multiplier=1.5, target="{art}"),
        parameters=["art"],
    ),
    "penalty": _entry("penalty", "Flaw", Modifier("study_total", amount=-1)),
}


def _source(*vf_ids: str, params=None) -> effects.EffectSource:
    return effects.EffectSource(
        "character",
        [VirtueFlawInstance(vf_id=v, params=params or {}) for v in vf_ids],
        CATALOG,
    )


def test_each_instance_counts_so_repeated_entries_stack():
    found = effects.collect([_source("bonus", "bonus")], "study_total")
    assert effects.amount_total(found) == 6


def test_activity_narrows_but_general_modifiers_always_count():
    source = _source("bonus", "reading")
    assert effects.amount_total(effects.collect([source], "study_total")) == 5
    teaching = effects.collect([source], "study_total", activity="teaching")
    assert [e.entry.id for e in teaching] == ["bonus"]


def test_target_is_resolved_from_the_instances_parameters():
    source = _source("affinity", params={"art": "creo"})
    assert effects.collect([source], "art_xp_gain", target="Creo")
    assert not effects.collect([source], "art_xp_gain", target="Vim")


def test_sources_are_combined_and_unknown_entries_skipped():
    other = effects.EffectSource(
        "laboratory", [VirtueFlawInstance(vf_id="missing")], CATALOG
    )
    found = effects.collect([_source("bonus"), other], "study_total")
    assert [e.kind for e in found] == ["character"]


def test_flat_amounts_are_added_before_multipliers():
    # The DE advancement pipeline: 10 + 3 = 13, x1.5 = 19.5 (Affinity then
    # rounds up to 20, but rounding is the owning rule's call).
    bonus = effects.collect([_source("bonus")], "study_total")
    affinity = effects.collect(
        [_source("affinity", params={"art": "creo"})], "art_xp_gain", target="creo"
    )
    result = effects.combine(10, bonus + affinity)
    assert result.total == 19.5
    assert [(line.amount, line.multiplier) for line in result.lines] == [
        (10, None),
        (3, None),
        (None, 1.5),
    ]


def test_several_multipliers_multiply_and_rounding_is_applied_last():
    double = _entry("double", "Virtue", Modifier("vis_extraction", multiplier=2))
    half = _entry("half", "Flaw", Modifier("vis_extraction", multiplier=0.5))
    source = effects.EffectSource(
        "character",
        [VirtueFlawInstance(vf_id="double"), VirtueFlawInstance(vf_id="half")],
        {"double": double, "half": half, **CATALOG},
    )
    found = effects.collect([source], "vis_extraction")
    assert effects.combine(7, found).total == 7
    assert effects.combine(3, found[1:], rounding=int).total == 1


def test_lab_catalog_effects_are_modifiers():
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    superior = by_id["labvf_superior_construction"]
    assert [(m.applies_to, m.target, m.amount) for m in superior.modifiers] == [
        ("lab_characteristic", "safety", 1),
        ("lab_characteristic", "aesthetics", 1),
    ]
    total = sum(
        1
        for entry in by_id.values()
        for m in entry.modifiers
        if m.applies_to == "lab_characteristic"
    )
    assert total == 254  # every value of the old characteristic map


def test_an_old_characteristic_map_still_loads():
    entry = LabVirtueFlawDef.from_dict(
        {
            "id": "labvf_old",
            "name": "Old",
            "type": "Virtue",
            "category": "Structure",
            "tier": "Free",
            "cost": 0,
            "characteristic_modifiers": {"safety": 2},
        }
    )
    assert entry.characteristic_modifiers == {"safety": 2}
    assert entry.modifiers[0].applies_to == "lab_characteristic"


def test_lab_characteristics_come_through_the_collector():
    lab = Laboratory(id="lab", covenant_id=None, name="Lab")
    lab.characteristics.safety = 1
    lab.virtues_flaws = [
        VirtueFlawInstance(vf_id="labvf_superior_construction"),
        VirtueFlawInstance(vf_id="labvf_deformed"),
    ]
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    # manual 1, Superior Construction +1, Deformed -1.
    assert lab_characteristic_total(lab, by_id, "safety") == (1, 1, -1, 1)


@pytest.mark.parametrize(
    ("vf_id", "params", "bonus"),
    [("vf_puissant_art", {"art": "creo"}, 3), ("vf_puissant_ability", {}, 0)],
)
def test_puissant_art_adds_to_the_score(vf_id, params, bonus):
    virtues = [VirtueFlawInstance(vf_id=vf_id, params=params)]
    assert scores.art_bonus(virtues, "Creo")[0] == bonus
    assert scores.art_bonus(virtues, "Vim")[0] == 0


def test_a_fixed_bonus_or_penalty_shows_base_then_adjusted():
    # STORY-212: "Magic Theory 5 (7)"; a Flaw's penalty the same way.
    assert sheet_text.adjusted_score(5, 2) == "5 (7)"
    assert sheet_text.adjusted_score(5, -1) == "5 (4)"
    assert sheet_text.adjusted_score(5, 0) == "5"


def test_puissant_ability_shows_base_then_adjusted():
    virtues = [
        VirtueFlawInstance(vf_id="vf_puissant_ability", params={"ability": "Brawl"})
    ]
    abilities = [Ability(name="Brawl", category="Martial", xp=50)]
    assert scores.ability_bonus(virtues, "brawl")[0] == 2
    assert sheet_text.ability_rows(abilities, virtues) == [
        (None, "Martial"),
        (0, "Brawl 4 (6) 50/75"),
    ]
    info = sheet_text.ability_info_text(abilities, 0, virtues)
    assert "Used at:[/] 6 (+2 from Puissant Brawl)" in info


#: Rules modules that hold no rule of their own (plumbing).
_PLUMBING = {"__init__", "breakdown", "effects"}


def test_every_rules_module_cites_its_source():
    import importlib
    import pkgutil

    from ars_magica_manager import rules

    for module in pkgutil.iter_modules(rules.__path__):
        if module.name in _PLUMBING:
            continue
        loaded = importlib.import_module(f"ars_magica_manager.rules.{module.name}")
        source = getattr(loaded, "SOURCE", "")
        assert "redcap.org" in str(source), f"rules.{module.name} cites no source"


def test_a_virtue_s_ability_or_characteristic_is_chosen_from_a_list():
    # STORY-712: the valid values, leaving out one already taken as often as
    # the book allows; the picked value reaches the totals.
    from ars_magica_manager import catalog
    from ars_magica_manager.screens.prompts import param_choices

    by_id = catalog.load_virtue_flaw_catalog_by_id()
    puissant = by_id["vf_puissant_ability"]
    taken = [VirtueFlawInstance("vf_puissant_ability", params={"ability": "brawl"})]
    values = [v for _, v in param_choices(puissant, taken, ["Latin"])["ability"]]
    assert "magic theory" in values and "latin" in values
    assert "brawl" not in values
    poor = param_choices(by_id["vf_poor_characteristic"])["characteristic"]
    assert [v for _, v in poor][:2] == ["intelligence", "perception"]
    assert len(param_choices(by_id["vf_deficient_form"])["form"]) == 10
    chosen = [
        VirtueFlawInstance("vf_puissant_ability", params={"ability": "magic theory"})
    ]
    assert scores.ability_bonus(chosen, "Magic Theory")[0] == 2
