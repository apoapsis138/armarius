"""The Merinita Mysteries: the House's Mystery Cult, Initiation gates and
Ordeals, and the Inner Mysteries' rules (Houses of Hermes: Mystery Cults
pp. 85-106; DE pp. 236-240; Errata p. 55)."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.models.mystery_scripts import ScriptPart
from ars_magica_manager.rules import merinita, spell_levels
from ars_magica_manager.rules import supplement_work as sw
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules.season_work import initiation
from ars_magica_manager.rules.xp import ability_xp, art_xp

LORE = merinita.CULT_LORE
TRADITION = merinita.CULT_TRADITION


def _magus(
    *vf_ids: str,
    id_: str = "m",
    name: str = "Mari",
    lore: int = 0,
    faerie_magic: int = 3,
) -> Character:
    magus = Character(id=id_, name=name, type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=3, presence=1, perception=2)
    magus.virtues_flaws = [VirtueFlawInstance("vf_faerie_magic")] + [
        VirtueFlawInstance(v) for v in vf_ids
    ]
    magus.abilities = [
        Ability("Magic Theory", xp=ability_xp(5)),
        Ability("Faerie Magic", xp=ability_xp(faerie_magic)),
    ]
    if lore:
        magus.abilities.append(Ability(LORE, xp=ability_xp(lore)))
    return magus


def _saga(*characters: Character) -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Grove")],
        characters=list(characters),
        laboratories=[
            Laboratory(id="lab", covenant_id="cov", name="Bower", owner_id="m")
        ],
    )


def _initiation(script: str, effect_id: str, **kw: object) -> SeasonPlan:
    base: dict[str, object] = {
        "teacher_id": "v",
        "title": "",
        "hedge_script": f"{TRADITION}/{script}",
        "effect_id": effect_id,
    }
    return SeasonPlan("m", 1220, "Spring", "undergo_initiation", [], **(base | kw))  # type: ignore[arg-type]


# -- The Mystery Cult (pp. 85-88) ------------------------------------------------


def test_the_house_s_scripts_are_offered_to_its_magi():
    initiate = _magus(lore=1)
    keys = [key for _, key in ts.script_options(_saga(initiate), initiate)]
    assert f"{TRADITION}/Shadow-Masters: Glamour" in keys
    assert ts.belongs(initiate, TRADITION)
    found = ts.hedge_script(f"{TRADITION}/Line of Quendalon: Animae Magic")
    assert found is not None
    script = found[1]
    # The book's Script bonus is the sum of its components (p. 96).
    assert (script.ease_factor, script.bonus) == (21, 16)
    assert sum(b for _, b in script.components) == 16
    for _, other in [ts.hedge_script(k) for k in keys if k.startswith(TRADITION)]:  # type: ignore[misc]
        assert sum(b for _, b in other.components) == other.bonus
    stranger = Character(id="x", name="Stranger", type="magus")
    assert TRADITION not in str(ts.script_options(_saga(stranger), stranger))


def test_what_an_inner_mystery_needs():
    no_lore = _magus()
    assert "Lore 1" in merinita.inner_mystery_problem(no_lore, "vf_charm_magic")
    initiate = _magus(lore=1)
    assert merinita.inner_mystery_problem(initiate, "vf_charm_magic") == ""
    outsider = Character(id="x", name="Outsider", type="magus")
    outsider.abilities = [Ability(LORE, xp=ability_xp(2))]
    assert "Faerie Magic" in merinita.inner_mystery_problem(outsider, "vf_glamour")
    # The Nature Mysteries need Nature Lore, not the House's Lore.
    assert "Nature Lore" in merinita.inner_mystery_problem(initiate, "vf_wilding")
    nature = _magus("vf_nature_lore")
    assert merinita.inner_mystery_problem(nature, "vf_wilding") == ""
    # Binding the Gift is the House's own: only the Lore.
    assert merinita.inner_mystery_problem(outsider, "vf_binding_the_gift") == ""
    assert merinita.inner_mystery_problem(no_lore, "vf_puissant_art") == ""
    initiate.abilities[-1].name = "House Merinita Lore"
    assert merinita.cult_lore(initiate) == 1


def test_an_inner_mystery_initiated_by_a_lineage_s_script():
    initiate = _magus(lore=1)
    mystagogue = _magus("vf_charm_magic", id_="v", name="Ambrosius", lore=5)
    mystagogue.characteristics.presence = 2
    saga = _saga(initiate, mystagogue)
    plan = _initiation("Heirs to Merlin: Charm Magic", "vf_charm_magic")
    assert sw.problems(saga, initiate, plan) == []
    # Ease 15 (known); Presence 2 + Lore 5 + Script 8 = 15.
    assert sw.initiation_target(saga, initiate, plan) == 15
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == ["vf_charm_magic"]


def test_glamour_always_brings_vulnerable_magic():
    initiate = _magus(lore=2)
    mystagogue = _magus("vf_glamour", id_="v", name="Pendule", lore=8)
    mystagogue.characteristics.presence = 3
    saga = _saga(initiate, mystagogue)
    plan = _initiation("Shadow-Masters: Glamour", "vf_glamour")
    # Presence 3 + Lore 8 + Script 15 = 26 against 21.
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert done.initiated
    assert [vf.vf_id for vf in done.add_vfs] == ["vf_glamour", "vf_vulnerable_magic"]
    assert done.ordeal == "Major"
    assert any("Vulnerable Magic" in n for n in done.notes)
    # A plan naming the Flaw as its own Ordeal gains it once.
    named = _initiation(
        "Shadow-Masters: Glamour",
        "vf_glamour",
        ordeal_kind="gain",
        device_id="vf_vulnerable_magic",
    )
    done = sw.work(saga, initiate, named, random.Random(1))
    assert [vf.vf_id for vf in done.add_vfs].count("vf_vulnerable_magic") == 1


def test_glamours_vulnerable_magic_has_a_new_condition():
    # Vulnerable Magic is taken again only with a different condition
    # (HoH:MC p. 87), and Glamour always brings it (p. 102).
    initiate = _magus(lore=2)
    mystagogue = _magus("vf_glamour", id_="v", name="Pendule", lore=8)
    saga = _saga(initiate, mystagogue)
    plan = _initiation("Shadow-Masters: Glamour", "vf_glamour")
    assert "Name the condition" in sw.problems(saga, initiate, plan)[0]
    plan.ordeal_condition = "when touching iron"
    assert sw.problems(saga, initiate, plan) == []
    done = sw.work(saga, initiate, plan, random.Random(1))
    flaw = next(vf for vf in done.add_vfs if vf.vf_id == "vf_vulnerable_magic")
    assert flaw.params == {"condition": "when touching iron"}
    initiate.virtues_flaws.append(
        VirtueFlawInstance("vf_vulnerable_magic", {"condition": "When touching iron"})
    )
    assert "different condition" in sw.problems(saga, initiate, plan)[0]
    plan.ordeal_condition = "when crossing running water"
    assert sw.problems(saga, initiate, plan) == []
    # A plan naming the Flaw as its own Ordeal checks that Flaw's condition.
    named = _initiation(
        "Shadow-Masters: Glamour",
        "vf_glamour",
        ordeal_kind="gain",
        device_id="vf_vulnerable_magic",
        ordeal_params={"condition": "when touching iron"},
    )
    assert "different condition" in sw.problems(saga, initiate, named)[0]


def test_the_lore_typed_under_another_name_scores():
    # The Ability catalog's name and the book's House Merinita Lore (p. 88)
    # are one Lore for a written-out Script's Initiation Total.
    initiate = _magus(lore=2)
    mystagogue = _magus("vf_charm_magic", id_="v", name="Pendule")
    mystagogue.abilities.append(Ability("House Merinita Lore", xp=ability_xp(5)))
    saga = _saga(initiate, mystagogue)
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        "undergo_initiation",
        [],
        teacher_id="v",
        title=LORE,
        effect_id="vf_charm_magic",
    )
    assert sw.problems(saga, initiate, plan) == []
    done = sw.work(saga, initiate, plan, random.Random(1))
    assert any("Initiation Total 6" in n for n in done.notes)


def test_a_written_out_glamour_script_counts_its_major_ordeal():
    initiate = _magus(lore=2)
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        "undergo_initiation",
        [],
        title=LORE,
        effect_id="vf_glamour",
        script_components=[ScriptPart("place")],
    )
    lines = initiation.script_lines(initiate, plan)
    assert any("Vulnerable Magic" in line.label and line.amount == 9 for line in lines)


def test_perpetuity_notes_its_usual_flaw():
    assert "Unnatural Magic" in merinita.initiation_notes("vf_perpetuity")[0]
    assert merinita.ordeal_flaw("vf_perpetuity") is None


# -- Faerie familiars and their cords (pp. 89-90) -------------------------------


def test_a_faerie_familiar_s_shared_powers_and_fatigue():
    assert merinita.can_bind_faerie(_magus())
    assert merinita.might_per_fatigue(10) == 2
    assert [merinita.fatigue_cost(10, lvl) for lvl in ("winded", "weary")] == [2, 4]
    with pytest.raises(ValueError):
        merinita.fatigue_cost(10, "fresh")


def test_the_faerie_cords_age_and_balance():
    positive = {"golden": 3, "silver": 1, "bronze": 0}
    # No negative cords: the highest positive one ages (p. 89).
    assert merinita.cord_to_age(positive, {}) == "golden"
    # Balanced sides don't age; the heavier side's highest does (p. 90).
    assert merinita.cord_to_age(positive, {"leaden": 4}) == ""
    assert merinita.cord_to_age(positive, {"iron": 3, "tin": 3}) == "iron"
    # +3 falls to +2 after four years, +1 three more, 0 two more.
    assert merinita.aged_cord(3, 4) == (2, 0)
    assert merinita.aged_cord(3, 9) == (0, 0)
    assert merinita.aged_cord(3, 3) == (3, 3)
    assert merinita.bond_breaks({"golden": 0, "silver": 0, "bronze": 0})
    assert merinita.familiar_slave_level(10) == 25
    assert merinita.familiar_slave_level(2) == 20


def test_binding_the_gift_s_cords_on_social_rolls():
    cords = {"golden": 2, "silver": 3, "bronze": 1, "iron": 2, "tin": 1}
    assert merinita.binding_gift_modifier(cords, ["faerie", "magical"]) == 3
    assert merinita.binding_gift_modifier(cords, ["faerie", "infernal"]) == 1
    assert merinita.binding_gift_modifier(cords, ["mundane"]) == -1


# -- Arcadian Travel, Animae, Becoming (pp. 92-96) ---------------------------------


def test_arcadian_travel():
    assert merinita.trod_ease(merinita.REGIO, 4) == 12
    assert merinita.trod_ease(merinita.TO_ARCADIA, 3) == 30
    assert merinita.trod_ease(merinita.LEAVE_ARCADIA, 0, arcane_connection=True) == 33
    with pytest.raises(ValueError):
        merinita.trod_ease("Rome")
    magus = _magus()
    magus.abilities.append(Ability("Music", xp=ability_xp(4)))
    assert merinita.travel_total(magus, "Music", 3).total == 2 + 4 + 3
    assert merinita.trod_companions(magus) == 3


def test_animae_levels():
    # A faerie insect of Might 1 is a base 11 Creo Animal effect (p. 94).
    assert merinita.animae_base(10, 1) == 11
    assert merinita.vis_anima_might(3) == 15
    assert merinita.animae_problem(_magus(), "Creo").startswith("Mari hasn't")
    assert merinita.animae_problem(_magus("vf_animae_magic"), "Rego")
    assert merinita.animae_problem(_magus("vf_animae_magic"), "Muto") == ""


def test_becoming_s_rituals():
    magus = _magus("vf_becoming")
    magus.arts = {"creo": ArtScore(xp=art_xp(10)), "vim": ArtScore(xp=art_xp(8))}
    magus.aging.decrepitude = 1
    assert merinita.ritual_level(magus, merinita.BODY, age=60) == 30
    assert merinita.ritual_level(magus, merinita.SPIRIT) == 18
    assert merinita.ritual_level(magus, merinita.MIND) == 8
    # A Major Ordeal's reductions, 9, 6, 3, take 45, 30, 15 off.
    assert merinita.with_ordeals(50, 9) == 5
    magus.aging.warping_score = 2
    assert merinita.total_limit(magus) == 6
    saga = _saga(magus)
    capped = merinita.becoming_total(saga, magus, "Creo", "Vim", saga.laboratories[0])
    assert capped.total == 6 and "Capped" in capped.lines[-1].label
    free = merinita.becoming_total(
        saga, magus, "Creo", "Vim", saga.laboratories[0], has_might=True
    )
    assert free.total > 6
    assert merinita.becoming_problems(magus, 30, 6)
    assert merinita.faerie_might(31) == 15
    # The Empowered Faerie: twice the level costs nothing (p. 96).
    assert merinita.empowered_cost(20, 20) == 4
    assert merinita.empowered_cost(20, 30) == 2
    assert merinita.empowered_cost(20, 40) == 0


# -- Charms, Story Magic and Symbolic Magic (pp. 88, 96-99) ---------------------------


def test_charm_magic():
    charms = [("magus", "Character"), ("Darius", "Character"), ("winter", "Event")]
    # +3 for three charms, +2 for two categories (p. 97).
    assert merinita.charm_bonus(charms) == 5
    assert merinita.charm_bonus([("enemy", "Character")]) == 2
    assert merinita.charm_multiplier(charms[1:]) == 3
    with pytest.raises(ValueError):
        merinita.charm_bonus([("x", "Colour")])
    assert merinita.charm_ease(3) == 12
    assert merinita.charm_ease(permanent=True) == 9
    magus = _magus("vf_charm_magic", faerie_magic=2)
    assert "at most 2" in merinita.charm_problems(magus, charms)[0]
    assert merinita.charm_mastery_xp(30) == 6


def test_symbolic_magic():
    charms = [("flies", "Aspect"), ("dark", "Aspect"), ("hears", "Adage")]
    # Three charms and two categories, doubled: +10 (p. 99).
    assert merinita.device_charm_bonus(charms) == 10
    magus = _magus("vf_symbolic_magic")
    line = merinita.device_charm_line(magus, charms)
    assert line is not None and line.amount == 10
    assert merinita.symbol_problems(magus, "Symbol", "Momentary", "Individual") == []
    found = merinita.symbol_problems(magus, "Symbol", "Symbol", "Individual")
    assert "Faerie Magic 6" in found[0]
    assert spell_levels.steps_of("range", "Symbol") == 4
    assert spell_levels.needs_ritual("target", "Symbol")
    assert spell_levels.virtue_needed(set(), "Symbol", "Momentary", "Individual") == [
        "Symbol Range needs Symbolic Magic."
    ]


def test_glamour_magnitudes():
    assert merinita.glamour_magnitudes(intricate=True, directed=True) == 3


# -- The Nature Mysteries (pp. 102-106) ----------------------------------------------


def test_nature_lore_and_awakening():
    assert merinita.nature_lore_score(5, at_home=False) == 2
    assert len(merinita.nature_lore_effects(3)) == 4
    # Might 5, Size -3: 15; an aura of 5 over an area of +5: 50 (p. 104).
    assert merinita.awakening_level(might=5, size=-3) == 15
    assert merinita.awakening_level(aura=5, area_size=5, spirit=True) == 50
    assert merinita.awakening_vis(16) == 4
    assert merinita.awakened_might(4) == 20
    assert merinita.power_levels_cap(3) == 30
    assert merinita.power_might_cost(25, pawns=5) == 2
    magus = _magus("vf_nature_lore")
    magus.abilities.append(Ability("Forest Lore", xp=ability_xp(3)))
    magus.arts = {"creo": ArtScore(xp=art_xp(5))}
    assert (
        merinita.awakening_total(magus, "Forest Lore", "Creo", "Herbam", 4).total == 15
    )
    assert merinita.wilding_pawns(3) == 6
    assert merinita.guardian_ease(4, 3) == 12
