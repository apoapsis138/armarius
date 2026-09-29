"""Casting Scores and Casting Totals (STORY-802)."""

import pytest

from ars_magica_manager.casting_text import known_spell_casting_lines
from ars_magica_manager.models import (
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Covenant,
    KnownSpell,
    Possession,
    Saga,
    Spell,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import casting
from ars_magica_manager.rules.xp import ability_xp, art_xp


def _magus(**kw) -> Character:
    return Character(
        id="m",
        name="Magus",
        type="magus",
        covenant_id="c",
        characteristics=Characteristics(stamina=2),
        arts={
            "creo": ArtScore(xp=art_xp(10)),
            "ignem": ArtScore(xp=art_xp(8)),
            "rego": ArtScore(xp=art_xp(4)),
        },
        abilities=[
            Ability("Artes Liberales", xp=ability_xp(2)),
            Ability("Philosophiae", xp=ability_xp(1)),
        ],
        **kw,
    )


def test_the_casting_score():
    score = casting.casting_score(_magus(), "Creo", "Ignem", aura=3)
    assert score.total == 10 + 8 + 2 + 3


def test_words_gestures_encumbrance_mastery_and_vis():
    magus = _magus(
        inventory=[Possession(id="a", kind="armor", name="Chain", load=6)]
    )  # Burden 3, Str 0: Encumbrance 3
    score = casting.casting_score(
        magus,
        "Creo",
        "Ignem",
        words="None",
        gestures="Exaggerated",
        mastery=2,
        vis_pawns=3,
    )
    assert score.total == 18 + 2 - 3 - 10 + 1 + 2 + 6


def test_a_requisite_counts_at_the_lower_art():
    score = casting.casting_score(_magus(), "Creo", "Ignem", requisites=["Rego"])
    assert score.total == 4 + 8 + 2
    assert score.lines[0].label == "Creo (requisite Rego)"


def test_a_ritual_adds_artes_liberales_and_philosophiae_not_words():
    score = casting.casting_score(_magus(), "Creo", "Ignem", ritual=True, words="None")
    assert score.total == 18 + 2 + 2 + 1


def test_a_divine_aura_hinders_casting():
    assert (
        casting.casting_score(
            _magus(), "Creo", "Ignem", aura=3, aura_realm="Divine"
        ).total
        == 20 - 9
    )


def test_deficient_form_halves_the_total_die_included():
    magus = _magus(
        virtues_flaws=[
            VirtueFlawInstance(vf_id="vf_deficient_form", params={"form": "ignem"})
        ]
    )
    score = casting.casting_score(magus, "Creo", "Ignem")
    assert score.total == 20  # the score itself isn't halved
    assert casting.casting_total(score, 7) == 13  # (20 + 7) / 2 rounded down
    assert casting.casting_total(casting.casting_score(magus, "Creo", "Vim"), 7) == 19


@pytest.mark.parametrize(
    ("total", "level", "cast", "fatigue"),
    [(20, 20, True, 0), (15, 20, True, 1), (10, 20, True, 1), (9, 20, False, 1)],
)
def test_formulaic_outcome(total, level, cast, fatigue):
    outcome = casting.formulaic_outcome(total, level)
    assert (outcome.cast, outcome.fatigue) == (cast, fatigue)


@pytest.mark.parametrize(
    ("short", "cast", "fatigue"),
    [(0, True, 1), (5, True, 2), (10, True, 3), (15, False, 4), (16, False, 5)],
)
def test_ritual_outcome(short, cast, fatigue):
    outcome = casting.ritual_outcome(30 - short, 30)
    assert (outcome.cast, outcome.fatigue, outcome.long_term) == (cast, fatigue, True)


def test_spontaneous_totals_round_down():
    assert casting.spontaneous_fatiguing(20, 7) == 13
    assert casting.spontaneous_non_fatiguing(24) == 4


def test_botch_dice():
    assert casting.botch_dice() == 1
    assert casting.botch_dice(vis_pawns=4) == 5
    assert casting.botch_dice(aura_realm="Divine", aura=3) == 4
    assert casting.botch_dice(fast=True, mastery=3) == 0  # Mastery can reach 0
    assert casting.botch_dice(vis_pawns=2, golden_cord=5) == 1  # the cord can't


def test_the_spell_details_say_what_the_die_must_reach():
    magus = _magus()
    saga = Saga(
        id="s",
        name="S",
        covenants=[Covenant(id="c", saga_id="s", name="C", aura=3)],
        characters=[magus],
    )
    pilum = Spell(
        id="p", name="Pilum of Fire", technique="Creo", form="Ignem", level=20
    )
    lines = known_spell_casting_lines(saga, magus, KnownSpell(spell_id="p"), pilum)
    assert lines[0].startswith("[b]Casting Score:[/] 23")
    assert "always cast without Fatigue" in lines[1]
    ritual = Spell(
        id="r", name="Ward", technique="Rego", form="Ignem", level=30, ritual=True
    )
    lines = known_spell_casting_lines(saga, magus, KnownSpell(spell_id="r"), ritual)
    # Rego 4 + Ignem 8 + Sta 2 + aura 3 + AL 2 + Phil 1 = 20: 10 short
    assert lines[1] == (
        "Ritual, stress die: 10+ for 1, 5+ for 2, 0+ for 3 long-term Fatigue "
        "levels; 7 botch dice."
    )


def test_infernal_vis_doubles_the_botch_dice_or_uses_the_harsher_option():
    from ars_magica_manager.models import Saga

    assert casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2) == 6
    harsh = Saga(id="s", name="S", rule_options={"harsher_infernal_vis": True})
    assert casting.botch_dice(vis_pawns=2, infernal_vis_pawns=2, saga=harsh) == 7


def test_casting_flaws_and_virtues_by_spell_type():
    magus = _magus(
        virtues_flaws=[
            VirtueFlawInstance(vf_id="vf_poor_formulaic_magic"),
            VirtueFlawInstance(vf_id="vf_method_caster"),
        ]
    )
    assert casting.casting_score(magus, "Creo", "Ignem").total == 20 - 5 + 3
    assert casting.casting_score(magus, "Creo", "Ignem", ritual=True).total == 23 + 3
    assert casting.casting_score(magus, "Creo", "Ignem", spontaneous=True).total == 20
