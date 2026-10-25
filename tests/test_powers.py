"""A character's powers from their Virtues (DE pp. 81-106): Initiative,
Fatigue and Confidence by kind, the levels each Virtue gives, a Personal
Power's limit, the items a Virtue gives, and the Powers section's form."""

from ars_magica_manager.forms import power as power_forms
from ars_magica_manager.models import (
    LESSER,
    Character,
    Characteristics,
    CharacterPower,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import powers


def person(*vf_ids: str, quickness: int = 2) -> Character:
    c = Character(
        id="c",
        name="Sula",
        type="companion",
        characteristics=Characteristics(quickness=quickness),
    )
    c.virtues_flaws.extend(VirtueFlawInstance(vf_id=v) for v in vf_ids)
    return c


def test_initiative_fatigue_and_confidence_by_kind():
    c = person()
    greater = CharacterPower("Owl", "Greater Power", level=30)
    lesser = CharacterPower("Warmth", "Lesser Power", level=30)
    ritual = CharacterPower("Rite", "Ritual Power", level=20)
    focus = CharacterPower("Fire", "Focus Power", level=10)
    assert powers.initiative(c, greater) == 2 - 3
    assert powers.initiative(c, lesser) == 2 - 12
    assert powers.fatigue(greater) == 1 and powers.fatigue(lesser) == 2
    assert powers.confidence(ritual) == 4 and powers.confidence(greater) == 0
    assert powers.initiative(c, focus) == 0


def test_each_virtue_gives_its_levels_and_problems_say_when_over():
    c = person("vf_lesser_power")
    c.powers = [
        CharacterPower("A", "Lesser Power", level=15, penetration=5),
        CharacterPower("B", "Lesser Power", level=10),
    ]
    assert powers.problems(c) == ["Lesser Power: 30 levels used of 25 (DE p. 90)."]
    c.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_lesser_power"))
    assert powers.problems(c) == []


def test_a_personal_power_must_be_personal_or_constant():
    c = person("vf_personal_power")
    c.powers = [CharacterPower("Grow", "Personal Power", level=10, range="Touch")]
    assert "must be Range Personal or constant" in powers.problems(c)[0]


def test_items_from_virtues_keep_within_their_levels():
    c = person("vf_minor_enchantments")
    found = powers.item_problems(
        c,
        [(powers.MINOR_ENCHANTMENTS, [20, 10], LESSER), (powers.REDCAP, [10], LESSER)],
    )
    assert "Minor Enchantments: 30 levels of 25 (DE p. 98)." in found
    assert "No Redcap Virtue for its items." in found


def test_the_form_adds_a_power_and_its_inspector_counts_the_virtue():
    c = person("vf_greater_power")
    form = power_forms.ops(c).add()
    values = {"name": "Owl", "virtue": "Greater Power", "level": 30, "penetration": 10}
    assert "Greater Power: 40 of 50 levels" in form.live(values)
    form.apply(values)
    assert c.powers[0].name == "Owl" and c.powers[0].penetration == 10
