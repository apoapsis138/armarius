"""Divination & Augury and Hermetic Astrology (The Mysteries Revised
Edition pp. 47-63, Errata p. 50; DE pp. 219-220): the divination totals,
methods and results, the astrological reckonings, the armillary sphere's
season and Celestial Magic's horoscope opening a device."""

from __future__ import annotations

import random

import pytest

from ars_magica_manager.actions import NodeKind, available
from ars_magica_manager.commands import Form, Refuse
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import tmre_divination as forms
from ars_magica_manager.models import (
    INVESTED,
    Ability,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    Laboratory,
    Saga,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_access, dice, enchant_seasons
from ars_magica_manager.rules import penetration as pen
from ars_magica_manager.rules import tmre_divination as td
from ars_magica_manager.rules.season_work import REGISTRY
from ars_magica_manager.rules.season_work import base as season_base
from ars_magica_manager.rules.xp import ability_xp


class Faces(random.Random):
    """A d10 that shows the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *_args, **_kwargs) -> int:  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def _augur(*vf: str, method: str = "Pyromancy", divination: int = 7) -> Character:
    """Numera-like: Intelligence 3, Perception 1, Presence 2, Divination 7,
    Artes Liberales 4."""
    magus = Character(id="m", name="Numera", type="magus", covenant_id="cov")
    magus.characteristics = Characteristics(intelligence=3, perception=1, presence=2)
    magus.virtues_flaws = [
        VirtueFlawInstance("vf_divination_and_augury", {"method": method}),
        *(VirtueFlawInstance(v) for v in vf),
    ]
    magus.abilities = [
        Ability("Divination", "Supernatural", xp=ability_xp(divination)),
        Ability("Artes Liberales", "Academic", xp=ability_xp(4)),
        Ability("Magic Theory", "Arcane", xp=ability_xp(5)),
        Ability("Penetration", "Arcane", xp=ability_xp(2)),
    ]
    return magus


def _saga(*characters: Character) -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="cov", saga_id="s", name="Keep", aura=5)],
        characters=list(characters),
        laboratories=[Laboratory(id="lab", covenant_id="cov", name="Tower")],
    )


# -- Divination's totals (pp. 60-62) -------------------------------------------


def test_the_example_ceremonial_total():
    """Numera (p. 62): Int 3, Divination 7, aura 5, ceremonial +4, magical
    +4 (a level 35 effect), sympathy +3 (rock, lasting years) +2 (a
    picture): die + 28. The book sums its bonuses as 5 + 4 + 5 = die + 29,
    with the ceremonial +4 it gave just above written as 5."""
    numera = _augur(method="Numerology")
    divination = td.Divination(
        kind=td.CEREMONIAL,
        ease=20,
        aura=5,
        method="Numerology",
        ceremonial=4,
        arcane_connection="Years or decades",
        sympathies=(pen.Sympathy("Symbolic representation", 2),),
        device_level=35,
    )
    assert td.total(numera, divination).total == 28


def test_casual_uses_perception_and_the_omens_but_no_ceremonial_bonus():
    augur = _augur()
    divination = td.Divination(
        kind=td.CASUAL,
        ease=10,
        aura=3,
        omens=2,
        ceremonial=5,
        arcane_connection="Indefinitely",
        device_level=40,
    )
    # Perception 1 + Divination 7 + aura 3 + omens 2; Errata p. 50 keeps
    # the ceremony's bonuses out of a casual divination.
    assert td.total(augur, divination).total == 13


def test_horoscopes_count_only_for_an_astrologer():
    augur = _augur()
    daily = pen.Sympathy("Target's horoscope for today", 1)
    pyro = td.Divination(sympathies=(daily,), method="Pyromancy")
    stars = td.Divination(sympathies=(daily,), method="Astrology")
    assert td.total(augur, stars).total - td.total(augur, pyro).total == 1


def test_a_divine_aura_hinders_and_adds_botch_dice():
    divination = td.Divination(aura=2, aura_realm="Divine")
    lines = td.total(_augur(), divination).lines
    assert any(line.amount == -6 for line in lines)
    assert td.botch_dice(divination) == 3
    assert td.botch_dice(td.Divination(aura=5)) == 1


def test_the_scrying_device_and_the_ceremony_s_length():
    assert td.magical_bonus(31) == 4
    assert td.magical_bonus(35) == 4
    assert td.magical_bonus(0) == 0
    assert td.ceremony_minutes(20) == 60
    assert td.ceremony_minutes(4) == 15
    assert td.ceremony_minutes(21) == 75


def test_penetration_is_the_total_plus_the_bonus_less_the_ease():
    assert td.penetration(30, 20, 6) == 16


def test_methods_come_from_the_virtues_and_the_table():
    augur = _augur("vf_hermetic_dream_interpreter", method="pyromancy")
    augur.virtues_flaws.append(
        VirtueFlawInstance("vf_additional_divination_method", {"method": "Astrology"})
    )
    assert td.methods(augur) == ["Pyromancy", "Astrology", "Dream Interpretation"]
    assert "Planetary Magic" in td.method_problem(augur, "Astrology")
    augur.virtues_flaws.append(VirtueFlawInstance("vf_planetary_magic"))
    assert td.method_problem(augur, "Astrology") == ""
    assert td.method_text(td.METHODS[-4]) == "Pyromancy (flames): Ignem +5"
    assert len(td.METHODS) == 34


def test_symbolic_readings_follow_the_ease_factor_table():
    assert "nothing" in td.symbolic_reading(8)
    assert td.symbolic_reading(9) == "an outline of the dreamer's state"
    assert "underlying" in td.symbolic_reading(21)


def test_a_symbolic_reading_ignores_the_aura_and_dream_calling_uses_presence():
    dreamer = _augur("vf_hermetic_dream_interpreter")
    symbolic = td.Divination(kind=td.SYMBOLIC, aura=5)
    calling = td.Divination(kind=td.DREAM_CALLING, aura=5)
    assert td.total(dreamer, symbolic).total == 10
    assert td.total(dreamer, calling).total == 14
    assert td.ease_of(calling) == 6


def test_the_outcome_says_whether_it_answers():
    divination = td.Divination(ease=15)
    hit = dice.roll(Faces(6), 10, ease_factor=15)
    miss = dice.roll(Faces(4), 10, ease_factor=15)
    botch = dice.roll(Faces(0, 0), 10, ease_factor=15)
    assert "answers truly" in td.outcome(divination, hit)
    assert "no answer" in td.outcome(divination, miss)
    assert "botch" in td.outcome(divination, botch)


# -- Hermetic Astrology (pp. 47-54) ---------------------------------------------


def test_astrological_duration_ease_factors():
    # Erratus's ten Hours: 6 + 10 = 16 (p. 49).
    assert td.duration_ease(10) == 16
    assert td.duration_ease(10, daily_horoscope=True, measured=True) == 10
    assert td.duration_ease(10, precision=True, sphere=True) == 9
    assert td.duration_ease(1, daily_horoscope=True, measured=True) == 1
    assert td.calm_calculation(measured=True, daily_horoscope=False, sphere=True)
    assert not td.calm_calculation(measured=False, daily_horoscope=True, sphere=True)


def test_a_missed_duration_is_out_by_the_shortfall():
    rolled = dice.Roll(modifiers=7, die=dice.DieResult(4, (4,)), ease_factor=16)
    said = td.duration_outcome(rolled, 10, "Astrological Hours")
    assert "from 5 to 15" in said


def test_favorable_hour_and_its_time():
    assert td.favorable_hour_ease(4) == 12
    # 9 x 10 + 10 = 100 -> 25: rerolled; then 2 x 10 + 3 = 23 -> 6.
    assert td.favorable_hour(Faces(9, 0, 2, 3)) == 6


def test_periapt_and_linked_enchantments():
    augur = _augur()
    assert td.periapt_charges(21) == 5
    assert td.periapt_max_level(augur) == 20
    # Notara's talisman (+4) and her Nativity Horoscope (+2), p. 50.
    assert td.linked_bonus("Indefinitely") == 6
    assert td.cycle_frequency(3, 7) == 10
    assert td.cycle_frequency(3, -7) is None
    assert td.OPPOSED[td.element_of("Leo")] == "Water"


def test_the_sphere_s_ease_factors_and_crafts():
    assert td.design_ease() == 12
    assert td.design_ease(by_another=True) == 15
    assert td.craft_ease(by_another=True, copying=True) == 12
    smith = _augur()
    smith.abilities.append(Ability("Craft: Blacksmith", xp=ability_xp(5)))
    assert td.best_craft(smith) == ("Craft: Blacksmith", 2, 3)
    smith.abilities.append(Ability("Craft: Clocks", xp=ability_xp(3)))
    assert td.best_craft(smith) == ("Craft: Clocks", 3, 0)


def test_the_armillary_sphere_season_rolls_design_and_craft():
    maker = _augur()
    maker.characteristics.dexterity = 2
    saga = _saga(maker)
    plan = SeasonPlan("m", 1220, "Spring", "make_armillary_sphere", [])
    entry = REGISTRY["make_armillary_sphere"]
    assert entry.check(saga, maker, plan)
    maker.abilities.append(Ability("Craft: Mechanisms", xp=ability_xp(5)))
    assert entry.check(saga, maker, plan) == []
    result = season_base.SupplementWork()
    entry.outcome(saga, maker, plan, Faces(9, 9), result)
    assert "design is sound" in result.notes[0]
    assert "mechanism is sound" in result.notes[1]
    assert "15 pawns" in result.notes[2]
    preview = season_base.SupplementWork()
    entry.outcome(saga, maker, plan, None, preview)
    assert "against 12" in preview.notes[0]


def test_celestial_magic_s_horoscope_takes_pawns_off_opening():
    magus = _augur("vf_celestial_magic")
    plan = SeasonPlan("m", 1220, "Spring", "open_device", [], horoscope=3)
    assert td.horoscope_opening(magus, plan)[0] == 0
    plan.horoscope_die = 7
    assert td.horoscope_opening(magus, plan)[0] == 3
    plan.horoscope_die = 1
    assert td.horoscope_opening(magus, plan) == (0, "")
    assert td.horoscope_opening(_augur(), plan) == (0, "")


def test_opening_a_device_pays_less_with_a_sound_horoscope():
    magus = _augur("vf_celestial_magic")
    saga = _saga(magus)
    device = EnchantedDevice(
        "d",
        "Sphere",
        INVESTED,
        holder_kind="character",
        holder_id="m",
        maker_id="m",
        capacity_override=6,
    )
    saga.enchanted_devices.append(device)
    plan = SeasonPlan(
        "m",
        1220,
        "Spring",
        enchant_seasons.OPEN,
        [],
        device_id="d",
        horoscope=2,
        horoscope_die=8,
    )
    found, work = enchant_seasons.work(
        saga, magus, plan, saga.laboratories[0], lambda *args: args[-1]
    )
    assert not found and work is not None
    assert work.vis_cost["Vim"] == 4
    assert any("Celestial Magic" in n for n in work.notes)


# -- creation and the More forms --------------------------------------------------


def test_the_virtues_open_divination_at_creation():
    augur = _augur()
    assert "Divination" in creation_access.granted_supernatural(augur)
    assert "Divination" not in creation_access.granted_supernatural(
        Character(id="x", name="X", type="magus")
    )


def test_more_offers_divination_and_astrology_to_those_with_them():
    augur = _augur()
    saga = _saga(augur)
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert available("tmre_divination", page)
    assert not available("tmre_astrology", page)
    assert isinstance(menu_forms.command(page, "tmre_divination"), Form)
    augur.virtues_flaws.append(VirtueFlawInstance("vf_planetary_magic"))
    page = menu_forms.page_for(saga, NodeKind.CHARACTER, character_id="m")
    assert available("tmre_astrology", page)
    placed = {i.action for i in menu_forms.placed(page, "Abilities")}
    assert {"tmre_divination", "tmre_astrology"} <= placed
    plain = Character(id="p", name="Plain", type="magus")
    assert isinstance(forms.divination_form(saga, plain), Refuse)
    assert isinstance(forms.astrology_form(saga, plain), Refuse)


def _values(character: Character, saga: Saga, **kw: object) -> dict[str, object]:
    values: dict[str, object] = {
        f.key: f.value for f in forms.divination_fields(saga, character)
    }
    return values | kw


def test_the_divination_form_rolls_and_writes_the_diary():
    augur = _augur()
    saga = _saga(augur)
    values = _values(augur, saga, ease=15, ceremonial=5, resistance=10)
    assert values["aura"] == 5
    assert forms.divination_problem(augur)(values) is None
    lines = forms.divination_lines(augur, values)
    assert "Intelligence +3" in lines[0]
    assert any("Pyromancy (flames)" in line for line in lines)
    said = forms.apply_divination(saga, augur, values, Faces(5))
    assert "answers truly" in said[0]
    assert "Penetrat" in said[1]
    assert augur.diary[-1].name == "Divination"


def test_the_divination_form_refuses_what_the_rules_do():
    augur = _augur()
    saga = _saga(augur)
    problem = forms.divination_problem(augur)
    assert problem(_values(augur, saga, ease=0))
    assert problem(_values(augur, saga, ease=10, ceremonial=6))
    assert problem(_values(augur, saga, kind=td.CASUAL, ease=10, omens=6))
    assert problem(_values(augur, saga, ease=10, method="Astrology"))


def test_the_astrology_form_reckons_a_duration_with_a_simple_die():
    star = _augur("vf_celestial_magic")
    saga = _saga(star)
    values = {f.key: f.value for f in forms.astrology_fields(star)} | {
        "what": forms.DURATION,
        "units": 10,
        "measured": True,
        "sphere": True,
        "calm": True,
    }
    assert forms.astrology_problem(star)(values) is None
    assert "a simple die against 6" in forms.astrology_lines(star, values)[0]
    said = forms.apply_astrology(saga, star, values, Faces(0))
    assert "lasts 10 Astrological Hours" in said[0]
    assert star.diary[-1].name == "Astrology"
    values["calm"], values["sphere"] = True, False
    assert forms.astrology_problem(star)(values)


@pytest.mark.parametrize(
    ("what", "said"),
    [
        (forms.DAILY, "Daily Horoscope is sound"),
        (forms.NATIVITY, "Nativity Horoscope is sound"),
        (forms.ADJUST, "setting is sound"),
    ],
)
def test_the_horoscopes(what: str, said: str):
    star = _augur("vf_planetary_magic")
    saga = _saga(star)
    values = {f.key: f.value for f in forms.astrology_fields(star)} | {"what": what}
    assert said in forms.apply_astrology(saga, star, values, Faces(5))[0]


def test_a_periapt_horoscope_counts_charges_and_a_favorable_hour_its_time():
    star = _augur("vf_celestial_magic", "vf_periapt")
    saga = _saga(star)
    fields = {f.key: f.value for f in forms.astrology_fields(star)}
    periapt = fields | {"what": forms.PERIAPT_ROLL, "lab_total": 21, "level": 25}
    assert forms.astrology_problem(star)(periapt)
    periapt["level"] = 20
    assert "5 charge(s)" in forms.apply_astrology(saga, star, periapt, Faces(5))[0]
    hour = fields | {"what": forms.HOUR, "bonus": 2}
    said = forms.apply_astrology(saga, star, hour, Faces(5, 2, 3))[0]
    assert "+2 to spells" in said and "hour 6 after midnight" in said
