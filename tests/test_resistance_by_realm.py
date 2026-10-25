"""Magic Resistance and Penetration by place and realm (DE pp. 109, 146,
152, 412, 419-420): Church offices and relics, Strong Angelic Heritage,
Susceptibility to Faerie and Infernal Power, creatures in auras, Weak
Magic in items, and Susceptibility to Warping by realm."""

from ars_magica_manager.creatures import penetration as creature_penetration
from ars_magica_manager.models import (
    ArtScore,
    Character,
    Creature,
    CreaturePower,
    EnchantedDevice,
    InstilledEffect,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import derived, enchantment, penetration


def person(**background: object) -> Character:
    c = Character(id="c", name="Hugh", type="companion")
    for key, value in background.items():
        setattr(c.background, key, value)
    return c


def test_an_archbishop_with_a_relic_adds_them_and_gains_soak():
    c = person(church_rank="Archbishop", relic_faith=2)
    assert penetration.faith_magic_resistance(c) == 30
    assert penetration.resistance_from(c) == "Archbishop 10 + relic 20"
    assert any(
        line.label == "Archbishop" and line.amount == 2
        for line in derived.soak(c).lines
    )


def test_resistances_from_different_sources_dont_add():
    c = person(true_faith_score=4, relic_faith=1)
    assert penetration.faith_magic_resistance(c) == 40


def test_strong_angelic_heritage_gives_divine_might_by_age():
    c = person(year_born=1120)
    c.virtues_flaws.append(
        VirtueFlawInstance(vf_id=penetration.STRONG_ANGELIC_HERITAGE)
    )
    saga = Saga(id="s", name="S", current_year=1220)
    assert penetration.angelic_might(c, saga) == 5


def test_susceptibility_to_faerie_power_halves_resistance_against_faeries():
    m = Character(id="m", name="Marcus", type="magus")
    m.arts["ignem"] = ArtScore(xp=55)
    m.virtues_flaws.append(
        VirtueFlawInstance(vf_id="vf_susceptibility_to_faerie_power")
    )
    full = penetration.magic_resistance(m, "Ignem").total
    halved = penetration.magic_resistance(m, "Ignem", effect_realm="Faerie").total
    assert halved == full // 2


def test_a_creatures_resistance_and_penetration_take_the_aura():
    assert penetration.creature_resistance(10, "Magic", "Magic", 3) == 13
    assert penetration.creature_resistance(10, "Faerie", "Divine", 2) == 2
    wolf = Creature("w", "Wolf", realm="Magic", might=15)
    bite = CreaturePower("Howl", might_cost=1)
    assert creature_penetration(wolf, bite, aura=4, aura_realm="Magic") == (
        creature_penetration(wolf, bite) + 4
    )


def test_weak_magic_buys_penetration_a_level_a_point():
    device = EnchantedDevice("d", "Wand")
    effect = InstilledEffect("e", "Bolt", level=10, uses_per_day="1", penetration=6)
    plain = enchantment.modified_level(device, effect)
    effect.weak_penetration = True
    assert enchantment.modified_level(device, effect) == plain + 3
