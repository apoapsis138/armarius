"""Always-on Virtue and Flaw bonuses the catalog carries as modifiers:
scores, Characteristics, Size, Soak, penalties, aging, Magic Resistance,
casting and character creation."""

import random

import pytest

from ars_magica_manager import catalog, seasons
from ars_magica_manager.models import Ability, ArtScore, Character, Saga, Wounds
from ars_magica_manager.models import VirtueFlawInstance as V
from ars_magica_manager.rules import (
    aging,
    casting,
    creation_access,
    creation_character,
    creation_finish,
    creation_magus,
    derived,
    penetration,
    scores,
)
from ars_magica_manager.rules import creation_characteristics as cch
from ars_magica_manager.rules import creation_virtues as cv
from ars_magica_manager.rules.xp import ability_xp, art_xp
from ars_magica_manager.tui.screens.prompts import param_choices


@pytest.mark.parametrize(
    ("virtue", "ability", "bonus"),
    [
        (V("vf_student_of_realm", {"realm": "divine"}), "Dominion Lore", 2),
        (V("vf_student_of_realm", {"realm": "divine"}), "Magic Lore", 0),
        (V("vf_student_of_realm", {"realm": "magic"}), "Magic Lore", 2),
        (V("vf_student_of_realm", {"realm": "faerie"}), "Faerie Lore", 2),
        (V("vf_student_of_realm", {"realm": "infernal"}), "Infernal Lore", 2),
        (V("vf_faerie_blood", {"blood": "dwarf"}), "Craft: Smith", 1),
        (V("vf_faerie_blood", {"blood": "dwarf"}), "Crafter's Healing", 0),
        (V("vf_faerie_blood", {"blood": "sidhe"}), "Craft: Smith", 0),
        (V("vf_faerie_blood", {"blood": "goblin"}), "Stealth", 1),
        (V("vf_strong_faerie_blood", {"blood": "dwarf"}), "Craft: Jeweler", 1),
        (V("vf_strong_faerie_blood"), "Craft: Jeweler", 0),
        (V("vf_dhampir"), "Faerie Lore", 1),
        (V("vf_keen_sense_of_smell_quality"), "Hunt", 2),
    ],
)
def test_a_virtue_raises_the_score_it_names(virtue, ability, bonus):
    assert scores.ability_bonus([virtue], ability)[0] == bonus


def test_the_realm_and_the_blood_are_chosen_from_a_list():
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    realms = param_choices(by_id["vf_student_of_realm"])["realm"]
    assert [value for _, value in realms] == ["divine", "faerie", "infernal", "magic"]
    bloods = param_choices(by_id["vf_strong_faerie_blood"])["blood"]
    assert ("Dwarf", "dwarf") in bloods


class _Dice(random.Random):
    """A Random whose d10s come out as given."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5

    def randint(self, a, b):
        return self.faces.pop(0) if self.faces else 5


def _person(**scores: int) -> tuple[Saga, Character]:
    saga = Saga(id="s", name="S", current_year=1220)
    character = Character(id="c", name="Aine", type="companion")
    for key, score in scores.items():
        setattr(character.characteristics, key, score)
    return saga, character


def test_sidhe_blood_adds_a_free_presence_point_up_to_three():
    sidhe = V("vf_faerie_blood", {"blood": "sidhe"})
    saga, aine = _person(presence=2)
    aine.virtues_flaws.append(sidhe)
    cch.apply_virtue(saga, aine, sidhe)
    assert aine.characteristics.presence == 3
    line = next(x for x in cch.lines(saga, aine) if x.key == "presence")
    assert (line.bought, line.free, line.cost) == (2, 1, 3)
    assert cch.removal_changes(saga, aine, sidhe) == [("presence", "Presence", 3, 2)]
    cch.unapply_virtue(saga, aine, sidhe)
    assert aine.characteristics.presence == 2
    # Already at +3: no point past the cap.
    saga, aine = _person(presence=3, strength=1)
    cch.apply_virtue(saga, aine, sidhe)
    assert aine.characteristics.presence == 3
    cch.apply_virtue(saga, aine, V("vf_faerie_blood", {"blood": "dwarf"}))
    cch.apply_virtue(saga, aine, V("vf_faerie_blood_bloodcap"))
    assert (aine.characteristics.presence, aine.characteristics.strength) == (3, 2)


def test_uninspirational_needs_presence_and_communication_at_zero():
    saga, aine = _person(presence=1)
    flaw = V("vf_uninspirational")
    assert cch.virtue_refusal(saga, aine, flaw) == (
        "Uninspirational caps Presence and Communication at 0 (Presence +1)."
    )
    aine.characteristics.presence = 0
    assert cch.virtue_refusal(saga, aine, flaw) == ""


def test_soak_virtues_and_flaws_change_soak():
    _, aine = _person(stamina=1)
    aine.virtues_flaws += [V("vf_improved_soak"), V("vf_shell")]
    soak = derived.soak(aine)
    assert soak.total == 7
    assert [line.label for line in soak.lines] == ["Stamina", "Improved Soak", "Shell"]
    aine.virtues_flaws = [V("vf_reduced_soak")]
    assert derived.soak(aine).total == -1


@pytest.mark.parametrize(
    ("vf_id", "wounds", "fatigue", "expected"),
    [
        ("vf_enduring_constitution", Wounds(light=1), "weary", (0, 0)),
        ("vf_enduring_constitution", Wounds(medium=1), "tired", (-2, -2)),
        ("vf_enduring_constitution", Wounds(), "fresh", (0, 0)),
        ("vf_low_tolerance", Wounds(light=1), "weary", (-2, -2)),
        ("vf_low_tolerance", Wounds(), "winded", (0, 0)),
    ],
)
def test_wound_and_fatigue_penalties_are_one_better_or_worse(
    vf_id, wounds, fatigue, expected
):
    vfs = [V(vf_id)]
    assert (
        derived.wound_penalty(wounds, vfs),
        derived.fatigue_penalty(fatigue, vfs),
    ) == expected


def test_strong_faerie_blood_starts_aging_at_fifty_with_three_off():
    _, aine = _person()
    assert aging.start_age(aine) == 35
    aine.virtues_flaws.append(V("vf_strong_faerie_blood", {"blood": "sidhe"}))
    assert aging.start_age(aine) == 50
    assert not aging.rolls_this_year(aine, 45)
    assert aging.rolls_this_year(aine, 50)
    # Die 8 + age 5 - Living Conditions 1 - 3 = 9.
    result = aging.roll(aine, 50, 1, 0, _Dice(8))
    assert result.total == 9
    assert result.notes == [
        "Aging Total 9 (die 8 + age 5 - Living Conditions +1 - Strong Faerie Blood 3)."
    ]
    assert creation_character.aging_age(aine) == 50


def test_mild_aging_and_poor_living_conditions_change_living_conditions():
    _, aine = _person()
    aine.virtues_flaws.append(V("vf_mild_aging"))
    assert aging.living_conditions(aine, 0) == 1
    text, _ = aging.crisis(aine, 60, 3, _Dice(7))
    assert "Survival: Stamina + Mild Aging 3 stress roll" in text
    aine.virtues_flaws = [V("vf_poor_living_conditions")]
    assert aging.living_conditions(aine, 2) == 1


@pytest.mark.parametrize("vf_id", ["vf_unaging", "vf_demonic_blood"])
def test_unaging_keeps_the_characteristics(vf_id):
    saga, aine = _person(intelligence=3)
    aine.background.year_born = 1170
    aine.virtues_flaws.append(V(vf_id))
    saga.characters.append(aine)
    saga.current_season = "Winter"
    # Faces 1, 8: a doubled 8 = 16; 16 + 5 = 21: points to several.
    seasons.year_end_aging(saga, _Dice(1, 8))
    assert aine.aging.decrepitude_points > 0
    assert aine.characteristics.intelligence == 3
    assert aine.characteristics.presence == 0


def _magus(*vfs: V) -> Character:
    return Character(
        id="m",
        name="M",
        type="magus",
        arts={"ignem": ArtScore(xp=art_xp(8)), "creo": ArtScore(xp=art_xp(5))},
        abilities=[Ability("Parma Magica", xp=ability_xp(3))],
        virtues_flaws=list(vfs),
    )


def test_flawed_parma_and_limited_resistance_weaken_one_form():
    assert penetration.magic_resistance(_magus(), "Ignem").total == 23
    flawed = _magus(V("vf_flawed_parma_magica", {"form": "ignem"}))
    assert penetration.magic_resistance(flawed, "Ignem").total == 15
    assert penetration.magic_resistance(flawed, "Aquam").total == 15
    limited = _magus(V("vf_limited_magic_resistance", {"form": "ignem"}))
    resistance = penetration.magic_resistance(limited, "Ignem")
    assert resistance.total == 15
    assert resistance.lines[0].label == "Ignem (Limited Magic Resistance)"


def test_weak_magic_halves_penetration():
    weak = [V("vf_weak_magic")]
    assert penetration.penetration_total(30, 3, 20, weak) == 6
    assert penetration.penetration_total(10, 0, 20, weak) == -10
    assert penetration.penetration_halved_by(weak) == ["Weak Magic"]


def _voice(magus: Character, **kw) -> dict[str, float | None]:
    score = casting.casting_score(magus, "Creo", "Ignem", **kw)
    return {line.label: line.amount for line in score.lines[4:]}


def test_words_and_gesture_flaws_and_virtues():
    assert _voice(_magus(V("vf_mute"))) == {"Mute": -10}
    assert _voice(_magus(V("vf_mute"), V("vf_quiet_magic"))) == {"Mute": -5}
    assert _voice(_magus(V("vf_no_hands")), gestures="Subtle") == {"No Hands": -5}
    assert _voice(_magus(V("vf_quiet_magic")), words="Quiet") == {}
    assert _voice(_magus(V("vf_subtle_magic")), gestures="None") == {}
    deft = _magus(V("vf_deft_form", {"form": "ignem"}))
    assert _voice(deft, words="None", gestures="None") == {}
    assert casting.casting_score(deft, "Creo", "Aquam", words="None").total < (
        casting.casting_score(deft, "Creo", "Ignem", words="None").total
    )


@pytest.mark.parametrize(
    ("vf_ids", "levels", "activity", "expected"),
    [
        ((), 1, "formulaic", 1),
        (("vf_enfeebled",), 1, "formulaic", 2),
        (("vf_withstand_casting",), 1, "formulaic", 1),
        (("vf_withstand_casting",), 2, "ritual", 1),
        (("vf_vulnerable_casting",), 1, "spontaneous", 2),
        (("vf_mythic_blood",), 1, "formulaic", 0),
        (("vf_mythic_blood",), 1, "spontaneous", 1),
        (("vf_mythic_blood",), 2, "ritual", 0),
        (("vf_enfeebled",), 0, "formulaic", 0),
    ],
)
def test_casting_fatigue(vf_ids, levels, activity, expected):
    vfs = [V(vf_id) for vf_id in vf_ids]
    assert casting.fatigue_levels(levels, vfs, activity) == expected


def test_creation_confidence_and_parens_virtues():
    _, aine = _person()
    aine.virtues_flaws = [V("vf_heroic_personality")]
    assert creation_finish.expected_confidence(aine) == (2, 5)
    aine.virtues_flaws = [V("vf_low_self_esteem")]
    assert creation_finish.expected_confidence(aine) == (0, 0)
    magus = _magus(V("vf_weak_parens"))
    assert (
        creation_magus.xp_budget(magus),
        creation_magus.level_budget(magus),
    ) == (180, 90)


@pytest.mark.parametrize(
    ("vf_id", "xp", "ability"),
    [
        ("vf_master_bard", 240, "Profession: Storyteller"),
        ("vf_senior_bard", 90, "Area Lore: Connacht"),
        ("vf_forge_companion", 50, "Craft: Smith"),
        ("vf_herbalism", 50, "Herbalism"),
        ("vf_gild_trained", 30, "Intrigue"),  # and 60 more on other Abilities and Arts
    ],
)
def test_more_virtues_give_creation_xp(vf_id, xp, ability):
    rule = creation_access.VIRTUE_XP[vf_id]
    assert rule.xp == xp
    assert creation_access.virtue_xp_allows(rule, ability)


def test_faerie_legacy_strengthens_the_blood():
    legacy = V("vf_faerie_legacy")
    goblin = V("vf_faerie_blood", {"blood": "goblin"})
    assert scores.ability_bonus([goblin], "Stealth") == (1, ["Faerie Blood (Goblin)"])
    assert scores.ability_bonus([goblin, legacy], "Stealth") == (
        2,
        ["Faerie Blood (Goblin)", "Faerie Legacy"],
    )
    brownie = V("vf_strong_faerie_blood", {"blood": "brownie"})
    assert scores.ability_bonus([brownie], "Profession: Scribe")[0] == 1
    # Nymph Blood with Faerie Legacy: Communication can reach +4.
    nymph = V("vf_faerie_blood", {"blood": "nymph"})
    saga, aine = _person(communication=3)
    aine.virtues_flaws += [nymph, legacy]
    cch.apply_virtue(saga, aine, nymph)
    assert aine.characteristics.communication == 4
    line = next(x for x in cch.lines(saga, aine) if x.key == "communication")
    assert (line.bought, line.free, line.cost) == (3, 1, 6)


def test_faerie_legacy_adds_to_the_favoured_craft():
    dwarf = V("vf_faerie_blood", {"blood": "dwarf"})
    legacy = V("vf_faerie_legacy", {"favored": "craft: smith"})
    assert scores.ability_bonus([dwarf, legacy], "Craft: Smith")[0] == 2
    assert scores.ability_bonus([dwarf, legacy], "Craft: Jeweler")[0] == 1
    by_id = catalog.load_virtue_flaw_catalog_by_id()
    assert catalog.describe_virtue_flaw(legacy, by_id) == "Faerie Legacy (Craft: Smith)"
    assert catalog.describe_virtue_flaw(V("vf_faerie_legacy"), by_id) == "Faerie Legacy"


def test_a_merinita_untouched_by_the_fay_starts_with_a_warping_point():
    # DE p. 236: the parens gives him one, to qualify him for the Mystery.
    magus = Character(id="m", name="M", type="magus")
    magus.hermetic.house = "house_merinita"
    magus.virtues_flaws = [V("vf_faerie_magic")]
    saga = Saga(id="s", name="S", characters=[magus])

    def warping_check():
        return next(
            c
            for c in creation_finish.finish_checks(saga, magus)
            if "Warping Point" in c.label
        )

    assert warping_check().status == "warn"
    magus.aging.warping_points = 1
    assert warping_check().status == "pass"
    magus.aging.warping_points = 0
    magus.virtues_flaws.append(V("vf_faerie_blood"))
    assert creation_finish.touched_by_the_fay(magus)
    assert not any(
        "Warping Point" in c.label for c in creation_finish.finish_checks(saga, magus)
    )


def test_giant_blood_adds_free_strength_and_stamina_up_to_six():
    # DE p. 83: +1 Strength and +1 Stamina, as high as +6.
    giant = V("vf_giant_blood")
    saga, grog = _person(strength=3, stamina=3)
    grog.virtues_flaws.append(giant)
    cch.apply_virtue(saga, grog, giant)
    assert (grog.characteristics.strength, grog.characteristics.stamina) == (4, 4)
    line = next(x for x in cch.lines(saga, grog) if x.key == "strength")
    assert (line.bought, line.free) == (3, 1)
    assert len(cch.removal_changes(saga, grog, giant)) == 2


def test_faerie_blood_may_learn_faerie_lore():
    # DE p. 79.
    assert "vf_faerie_blood" in creation_access.OPENS_ABILITY


def test_demonic_blood_cannot_be_taken_with_unaging():
    # DE p. 76.
    from_checks = cv.virtue_flaw_checks(
        Saga(id="s", name="S"),
        Character(
            id="c",
            name="C",
            type="companion",
            virtues_flaws=[V("vf_demonic_blood"), V("vf_unaging")],
        ),
    )
    assert any("can't be taken with Unaging" in c.label for c in from_checks)
