"""Creation rules from Virtues and Flaws (DE pp. 56, 58, 84, 96, 105,
110, 130-131, 143-144, 151, 158): feral, sheltered and foreign
upbringings, Savantism, Student of (Realm), a Redcap's 300 xp, Warped by
Magic, Academic Abilities and their language, Mastered Spells, the
Nephilim, a Devil Child's free points, Fluctuating Fortune and the
Guardian Angel."""

from ars_magica_manager.models import (
    Ability,
    Character,
    KnownSpell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import (
    activities,
    creation_access,
    creation_rest,
    creation_virtues,
    creation_xp,
    derived,
    penetration,
)


def person(*vfs: VirtueFlawInstance, kind: str = "companion") -> Character:
    c = Character(id="c", name="Hugh", type=kind)
    c.virtues_flaws.extend(vfs)
    return c


def vf(vf_id: str, **params: str) -> VirtueFlawInstance:
    return VirtueFlawInstance(vf_id=vf_id, params=dict(params))


def test_a_feral_child_buys_only_the_wild_abilities():
    c = person(vf("vf_feral_upbringing"))
    assert creation_xp.childhood_allows("Hunt", c)
    assert creation_xp.childhood_allows("Area Lore: Black Forest", c)
    assert not creation_xp.childhood_allows("Charm", c)
    assert not creation_xp.childhood_allows("Living Language: German", c)


def test_sheltered_upbringing_bars_the_social_abilities_at_creation():
    c = person(vf("vf_sheltered_upbringing"))
    assert not creation_access.may_learn(c, "Charm")
    assert creation_access.may_learn(c, "Awareness")


def test_foreign_upbringing_halves_local_caps_and_savantism_caps_at_three():
    foreign = person(vf("vf_foreign_upbringing"))
    assert creation_access.ability_cap_for(foreign, 25, "Area Lore: Rhine") == 3
    assert creation_access.ability_cap_for(foreign, 25, "Awareness") == 5
    savant = person(vf("vf_savantism", ability="Animal Handling"))
    assert creation_access.ability_cap_for(savant, 40, "Brawl") == 3
    assert creation_access.ability_cap_for(savant, 40, "Animal Handling") == 6
    assert creation_xp.childhood_xp(savant) == creation_xp.CHILDHOOD_XP // 2


def test_student_of_realm_opens_only_its_own_lore():
    c = person(vf("vf_student_of_realm", realm="Faerie"))
    assert creation_access.opened_by_virtues(c) == {"Faerie Lore"}


def _checks(c: Character) -> dict[str, str]:
    return {x.label: x.status for x in creation_rest.rest_checks(None, c)}  # type: ignore[arg-type]


def test_academic_abilities_want_a_written_language_at_three():
    c = person(vf("vf_educated"))
    c.abilities.append(Ability("Artes Liberales", xp=5))
    labels = _checks(c)
    assert (
        labels.get("Academic Abilities need Latin, Greek, Hebrew or Arabic at 3")
        == "advice"
    )
    c.abilities.append(Ability("Dead Language: Latin", xp=30))
    assert "Academic Abilities need Latin, Greek, Hebrew or Arabic at 3" not in _checks(
        c
    )


def test_mastered_spells_gives_fifty_xp_of_mastery():
    m = person(vf("vf_mastered_spells"), kind="magus")
    m.spells_known.append(KnownSpell("s1", mastery_xp=60))
    assert _checks(m)["Mastered Spells: 50 xp of Spell Mastery"] == "advice"


def test_nephilim_need_both_great_characteristics():
    c = person(
        vf("vf_nephilim"), vf("vf_great_characteristic", characteristic="Stamina")
    )
    assert _checks(c)["Nephilim take Great Stamina and Great Strength"] == "warn"


def test_a_devil_child_takes_three_virtue_points_free():
    plain = person(kind="mythic companion")
    devil = person(vf("vf_devil_child"), kind="mythic companion")
    assert creation_virtues.virtue_allowance(devil, 5)[1] == (
        creation_virtues.virtue_allowance(plain, 5)[1] + 3
    )


def test_fluctuating_fortune_alternates_working_seasons():
    c = person(vf("vf_fluctuating_fortune"))
    assert activities.working_seasons(c, 1220) == 1
    assert activities.working_seasons(c, 1221) == 3


def test_a_guardian_angel_adds_to_true_faith_and_soak():
    c = person(vf("vf_guardian_angel"))
    c.background.true_faith_score = 1
    assert penetration.faith_magic_resistance(c) == 25
    assert penetration.resistance_from(c) == "True Faith + Guardian Angel"
    assert any(line.label == "Guardian Angel" for line in derived.soak(c).lines)


def test_fluctuating_fortunes_wealthy_years_can_be_the_odd_ones():
    c = person(vf("vf_fluctuating_fortune"))
    c.background.fortune_wealthy_in = "odd"
    assert activities.working_seasons(c, 1221) == 1
    assert activities.working_seasons(c, 1220) == 3


def test_a_virtues_realm_comes_from_its_name_or_the_table():
    from ars_magica_manager.rules import realms

    assert realms.virtue_realm("vf_raised_from_the_dead") == "Divine"
    assert realms.virtue_realm("vf_faerie_blood", "Faerie Blood") == "Faerie"
    assert realms.virtue_realm("vf_x", "Anything", tainted=True) == "Infernal"
    assert realms.virtue_realm("vf_immortality_of_the_forest") == "Magic"


def test_susceptibility_to_warping_counts_each_realm_of_the_years_events():
    import random

    from ars_magica_manager.models import Saga
    from ars_magica_manager.seasons import character_effects as ce

    c = person(vf("vf_susceptibility_to_warping"))
    saga = Saga(id="s", name="S", characters=[c])
    ce.gain_warping(saga, c, 1, random.Random(1), realm="Faerie")
    ce.gain_warping(saga, c, 1, random.Random(1), realm="Infernal")
    assert ce._warped_this_year(saga, c) == {"Faerie", "Infernal"}
    assert "Susceptibility to Warping 2" in ce._yearly_warping(saga, c)
