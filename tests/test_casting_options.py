"""The spellcasting options and the rules around a cast: fast and
ceremonial casting, Mastery's special abilities, vis limits, Spontaneous
totals from their own score, the Golden Cord, a talisman's attunements,
certamen's Tremere Focus, a Ritual's Fatigue past unconsciousness and a
botch's Warping (DE pp. 213-227, 233, 260)."""

from ars_magica_manager.casting_text import (
    casting_scores_text,
    known_spell_casting_lines,
)
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    EnchantedDevice,
    Familiar,
    KnownSpell,
    MasteryAbility,
    Saga,
    ShapeMaterialBonus,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import casting, certamen, spell_levels
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(**kw) -> Character:
    """Creo 10, Ignem 8, Stamina 2: CrIg Casting Score 20."""
    return Character(
        id="m",
        name="Magus",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(stamina=2, quickness=1, perception=2),
        arts={"creo": ArtScore(xp=art_xp(10)), "ignem": ArtScore(xp=art_xp(8))},
        abilities=[
            Ability("Artes Liberales", xp=ability_xp(2)),
            Ability("Philosophiae", xp=ability_xp(1)),
            Ability("Finesse", xp=ability_xp(3)),
            Ability("Concentration", xp=ability_xp(2)),
        ],
        **kw,
    )


def _saga(magus: Character) -> Saga:
    return Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="c", saga_id="s", name="Keep")],
        characters=[magus],
    )


def test_fast_casting_takes_ten_and_no_vis():
    score = casting.casting_score(_magus(), "Creo", "Ignem", fast=True, vis_pawns=2)
    assert score.total == 20 - 10
    assert casting.botch_dice(fast=True) == 3
    assert casting.fast_casting_speed(_magus()) == 1 + 3


def test_ceremonial_casting_adds_the_learned_abilities_and_props():
    magus = _magus()
    assert casting.can_ceremonial(magus)
    score = casting.casting_score(
        magus, "Creo", "Ignem", spontaneous=True, ceremonial=True, props=7,
        words="None",
    )  # fmt: skip
    # + Artes Liberales 2 + Philosophiae 1 + props (at most 5); no words.
    assert score.total == 20 + 3 + 5
    magus.abilities = [a for a in magus.abilities if a.name != "Philosophiae"]
    magus.abilities[0].xp = 0
    assert not casting.can_ceremonial(magus)


def test_quiet_and_still_casting_mastery():
    abilities = casting.mastery_counts(
        [MasteryAbility("Quiet Casting"), MasteryAbility("Still Casting")]
    )
    score = casting.casting_score(
        _magus(), "Creo", "Ignem", words="Quiet", gestures="None",
        mastery_abilities=abilities,
    )  # fmt: skip
    assert score.total == 20  # -5 words and -5 gestures both taken off
    twice = casting.mastery_counts([MasteryAbility("Quiet Casting")] * 2)
    silent = casting.casting_score(
        _magus(), "Creo", "Ignem", words="None", mastery_abilities=twice
    )
    assert silent.total == 20


def test_method_caster_needs_the_method():
    magus = _magus(virtues_flaws=[VirtueFlawInstance("vf_method_caster")])
    assert casting.casting_score(magus, "Creo", "Ignem").total == 23
    quiet = casting.casting_score(magus, "Creo", "Ignem", words="Quiet")
    assert quiet.total == 20 - 5


def test_a_deficient_requisite_halves_the_total():
    magus = _magus(
        virtues_flaws=[
            VirtueFlawInstance("vf_deficient_technique", params={"technique": "Rego"})
        ]
    )
    magus.arts["rego"] = ArtScore(xp=art_xp(12))
    score = casting.casting_score(magus, "Creo", "Ignem", requisites=["Rego"])
    assert casting.casting_total(score, 0) == 10  # 20 halved


def test_spontaneous_levels_come_from_their_own_score():
    magus = _magus(virtues_flaws=[VirtueFlawInstance("vf_method_caster")])
    own = casting.casting_score(magus, "Creo", "Ignem", spontaneous=True)
    assert casting.spontaneous_total(own) == 4  # 20 / 5, without the +3
    assert casting.spontaneous_total(own, die=6) == 13
    deficient = _magus(
        virtues_flaws=[
            VirtueFlawInstance("vf_deficient_form", params={"form": "Ignem"})
        ]
    )
    own = casting.casting_score(deficient, "Creo", "Ignem", spontaneous=True)
    assert casting.spontaneous_total(own) == 2  # 20 halved, / 5
    text = casting_scores_text(_saga(deficient), deficient)
    assert "Spontaneous levels without Fatigue" in text


def test_vis_is_limited_by_the_art():
    magus = _magus()
    assert casting.vis_limit_problem(magus, "Ignem", 8) == ""
    assert casting.vis_limit_problem(magus, "Ignem", 9) == (
        "9 pawns of Ignem vis: Magus can use at most 8 (the Ignem score)."
    )
    extra = casting.casting_score(magus, "Creo", "Ignem", ritual=True, vis_pawns=2)
    plain = casting.casting_score(magus, "Creo", "Ignem", ritual=True)
    assert extra.total == plain.total + 4


def test_the_golden_cord_lowers_spell_botch_dice():
    magus = _magus()
    saga = _saga(magus)
    saga.familiars = [Familiar(id="f", name="Cat", character_id="m", golden_cord=2)]
    assert casting.golden_cord(saga, magus) == 2
    saga.spells = [Spell("blaze", "Blaze", "Creo", "Ignem", level=30, ritual=True)]
    known = KnownSpell("blaze")
    lines = known_spell_casting_lines(saga, magus, known, saga.spells[0])
    # 1 die + 6 pawns of vis, less the cord's 2.
    assert "5 botch dice" in lines[-1]


def test_a_talismans_attunements_are_listed_best_first():
    magus = _magus()
    saga = _saga(magus)
    saga.enchanted_devices = [
        EnchantedDevice(
            "staff",
            "Staff",
            talisman=True,
            maker_id="m",
            attunements=[
                ShapeMaterialBonus(2, "fire", "Ash"),
                ShapeMaterialBonus(4, "destroy at a distance", "Staff"),
            ],
        )
    ]
    assert casting.talisman_attunements(saga, magus) == [
        (4, "destroy at a distance"),
        (2, "fire"),
    ]
    score = casting.casting_score(magus, "Creo", "Ignem", talisman=4)
    assert score.total == 24
    assert "Talisman, while touching it" in casting_scores_text(saga, magus)


def test_mastery_lines_name_what_the_abilities_do():
    magus = _magus()
    saga = _saga(magus)
    saga.spells = [Spell("bolt", "Bolt", "Creo", "Ignem", level=15)]
    known = KnownSpell(
        "bolt",
        mastery_score=2,
        mastery_abilities=[
            MasteryAbility("Penetration"),
            MasteryAbility("Fast Casting"),
        ],
    )
    lines = known_spell_casting_lines(saga, magus, known, saga.spells[0])
    assert lines[-1].startswith("[b]Mastery:[/] fast-cast at -10")
    assert "+2 to Penetration" in lines[-1]


def test_the_tremere_focus_doubles_the_lower_art_in_certamen():
    magus = _magus()
    plain = certamen.certamen_totals(magus, "Creo", "Ignem")
    magus.hermetic.house = "house_tremere"
    focused = certamen.certamen_totals(magus, "Creo", "Ignem")
    assert focused.attack_form == plain.attack_form + 8  # Ignem 8 doubled
    assert focused.attack_technique == plain.attack_technique


def test_a_rituals_fatigue_past_unconsciousness_is_a_wound():
    # Two levels left, three lost: unconscious and a Light wound (DE p. 213).
    assert casting.ritual_fatigue(2, 3) == (2, "light")
    assert casting.ritual_fatigue(2, 2) == (2, None)
    assert casting.ritual_fatigue(0, 5) == (0, "incapacitating")


def test_a_botchs_zeros_are_warping_points():
    assert casting.botch_warping(1) == (1, False)
    assert casting.botch_warping(2) == (2, True)
    assert casting.botch_dice(distracted=True) == 2


def test_a_ritual_at_its_floor_carries_no_extra_magnitudes():
    # Base 5, Touch/Mom/Ind works out to 10; a Ritual is listed at 20.
    assert spell_levels.extra_magnitudes(5, "Touch", "Momentary", "Individual", 20) == 2
    found = spell_levels.extra_magnitudes(
        5, "Touch", "Momentary", "Individual", 20, ritual=True
    )
    assert found == 0
    design = spell_levels.spell_level(5, "Personal", "Momentary", "Room")
    assert design is not None
    assert (
        "A Personal Range spell can't have a Room Target (DE p. 303)." in design.notes
    )


def test_flaws_that_change_spontaneous_magic():
    # DE pp. 76, 122, 126, 149, 153.
    def score(*vfs: str, spontaneous: bool = True) -> int:
        magus = _magus(virtues_flaws=[VirtueFlawInstance(v) for v in vfs])
        return int(
            casting.casting_score(magus, "Creo", "Ignem", spontaneous=spontaneous).total
        )

    assert score() == 20
    assert score("vf_ceremonial_spontaneous_magic") == 23  # + AL 2 + Phil 1
    assert score("vf_unstructured_caster", spontaneous=False) == 23
    plain = casting.casting_score(_magus(), "Creo", "Ignem", spontaneous=True)
    weak = _magus(virtues_flaws=[VirtueFlawInstance("vf_weak_spontaneous_magic")])
    hard = _magus(virtues_flaws=[VirtueFlawInstance("vf_difficult_spontaneous_magic")])
    both = _magus(
        virtues_flaws=[
            VirtueFlawInstance("vf_weak_spontaneous_magic"),
            VirtueFlawInstance("vf_difficult_spontaneous_magic"),
        ]
    )
    diedne = _magus(virtues_flaws=[VirtueFlawInstance("vf_diedne_magic")])
    assert casting.non_fatiguing_level(weak, plain) == 4
    assert casting.non_fatiguing_level(hard, plain) is None
    assert casting.spontaneous_mode(both) == casting.NO_SPONTANEOUS
    assert casting.non_fatiguing_level(diedne, plain) == 10
    assert "Difficult Spontaneous" in casting_scores_text(_saga(hard), hard)
