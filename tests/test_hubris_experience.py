"""Hubris and lasting Sympathy Traits gain experience by themselves, and a
Hubris written with its flavour, "Hubris (Arrogant)", is Hubris everywhere.

Hubris builds like an Ability, its flavour noted in brackets after it (DE
p. 241; Houses of Hermes: Mystery Cults p. 119). Sympathy Traits rise with
experience like Abilities, a negative one at 10, 15, 20 xp a step (Realms
of Power: Faerie p. 103), on through 0 (Errata p. 68); a temporary one
can't be raised (RoP:F p. 127)."""

from __future__ import annotations

import random
from dataclasses import asdict

from test_verditius import _magus, _saga

from ars_magica_manager import form_spec
from ars_magica_manager import sheet_text as st
from ars_magica_manager.forms import hubris as hubris_forms
from ars_magica_manager.forms import trait as trait_forms
from ars_magica_manager.models import Character, ScoredTrait, SeasonPlan
from ars_magica_manager.models.traits import is_hubris
from ars_magica_manager.rules import faerie_dealings, lab_virtues, verditius
from ars_magica_manager.rules.faerie_sympathy import SYMPATHY, TEMPORARY


def test_hubris_is_known_with_or_without_its_flavour() -> None:
    for name in ("Hubris", "Hubris (Arrogant)", "Hubris (Proud)"):
        assert is_hubris(ScoredTrait(name, 1)), name
    for name in ("Hubristic", "Hubris-ish", "Proud", "My Hubris"):
        assert not is_hubris(ScoredTrait(name, 1)), name


def test_a_flavoured_hubris_adds_to_its_lab_totals() -> None:
    magus = _magus(verditius.HUBRIS_FLAW, verditius.BIND_MAGICAL_CREATURES)
    magus.personality_traits = [ScoredTrait("Hubris (Arrogant)", 2)]
    saga = _saga(magus)
    total = verditius.binding_total(saga, magus, saga.laboratories[0])
    assert ("Hubris", 2) in [(line.label, line.amount) for line in total.lines]
    lines, _ = lab_virtues.option_lines(
        magus,
        SeasonPlan(
            character_id=magus.id, year=1220, season="Spring", activity="enchant_item"
        ),
        enchanting=True,
        talisman=True,
        binding=False,
        horoscope_score=0,
    )
    assert ("Hubris", 2) in [(line.label, line.amount) for line in lines]


def test_more_hubris_adds_to_a_flavoured_hubris_without_a_second() -> None:
    magus = _magus(verditius.HUBRIS_FLAW)
    magus.personality_traits = [ScoredTrait("Hubris (Arrogant)", 1, gains_xp=True)]
    saga = _saga(magus)
    hubris_forms.record(
        saga,
        magus,
        {"what": "Winning a vendetta"},
        random.Random(1),
    )
    assert [(t.name, t.score, t.deeds) for t in magus.personality_traits] == [
        ("Hubris (Arrogant)", 1, 3)
    ]


def test_hubris_is_made_gaining_experience() -> None:
    # The first Inner Mystery's Ordeal: Hubris 1 (DE p. 241), 1 experience
    # for a Minor Inner Mystery (DE p. 242).
    magus = _magus()
    verditius.apply_hubris(magus, 1, 1, 0)
    (hubris,) = magus.personality_traits
    assert (hubris.name, hubris.score, hubris.deeds, hubris.gains_xp) == (
        "Hubris",
        1,
        1,
        True,
    )
    # The Increased Hubris Ordeal on one who has none yet (HoH:MC p. 121).
    risen = _magus()
    verditius.apply_hubris(risen, 0, 0, 1)
    assert [t.gains_xp for t in risen.personality_traits] == [True]


# -- Sympathy Traits --------------------------------------------------------


def _shown_keys(existing: ScoredTrait, **changes: object) -> list[str]:
    fields = trait_forms.scored_trait_fields(
        "", existing, include_sympathy=True, include_xp=True
    )
    values = {f.key: f.value for f in fields} | changes
    return [f.key for f in fields if form_spec.shown(f, values)]


def test_a_lasting_sympathy_trait_always_gains_experience() -> None:
    winter = ScoredTrait("Winter", 1, deeds=2, type=SYMPATHY, gains_xp=True)
    shown = _shown_keys(winter)
    # The box is locked on: it isn't offered, and XP stands in for Score.
    assert "gains_xp" not in shown and "score" not in shown and "xp" in shown
    saved = trait_forms.trait_from(
        {"name": "Winter", "xp": 7, "sympathy": True, "temporary": False}, winter
    )
    assert (saved.score, saved.deeds, saved.gains_xp, saved.type) == (
        1,
        2,
        True,
        SYMPATHY,
    )


def test_ticking_sympathy_turns_experience_on() -> None:
    brave = ScoredTrait("Brave", 2)
    (tick,) = [
        f
        for f in trait_forms.scored_trait_fields(
            "", brave, include_sympathy=True, include_xp=True
        )
        if f.key == "sympathy"
    ]
    assert tick.fills is not None
    assert tick.fills({"sympathy": True, "score": 2}) == {"xp": 15}


def test_a_temporary_sympathy_trait_gains_none() -> None:
    oak = ScoredTrait("Oak", 2, type=TEMPORARY)
    shown = _shown_keys(oak)
    assert "gains_xp" not in shown and "xp" not in shown and "score" in shown
    saved = trait_forms.trait_from(
        {"name": "Oak", "score": 2, "sympathy": True, "temporary": True}, oak
    )
    assert not saved.gains_xp


def test_a_negative_sympathy_trait_keeps_its_score_and_counts_its_step() -> None:
    # Iron -2: 15 xp raise it to -1 (RoP:F p. 103).
    iron = ScoredTrait("Iron", -2, deeds=4, type=SYMPATHY, gains_xp=True)
    shown = _shown_keys(iron)
    assert "score" in shown and "toward" in shown and "xp" not in shown
    values = {
        "name": "Iron",
        "score": -2,
        "toward": 6,
        "sympathy": True,
        "temporary": False,
    }
    assert trait_forms.score_problem(values, None, None) is None
    saved = trait_forms.trait_from(values, iron)
    assert (saved.score, saved.deeds, saved.gains_xp) == (-2, 6, True)
    assert st.trait_xp(saved) == "6/15"
    # An ordinary trait below 0 still can't gain experience.
    plain_values = {"name": "Dour", "score": -1, "gains_xp": True}
    assert trait_forms.score_problem(plain_values, None, None) == (
        trait_forms.STARTS_AT_ZERO
    )


def test_a_negative_score_being_retyped_stays_on_screen() -> None:
    # Typing "-2" over -3 passes through "-" (no number yet).
    iron = ScoredTrait("Iron", -3, type=SYMPATHY, gains_xp=True)
    shown = _shown_keys(iron, score=None)
    assert "score" in shown and "toward" in shown


def test_a_sympathy_trait_held_at_its_warping_limit_isn_t_raised_by_saving() -> None:
    # Winter +2 at Warping Score 2: 20 xp banked past the 15 its next step
    # costs, the cap holding it at +2 (RoP:F p. 103).
    winter = ScoredTrait("Winter", 2, deeds=20, type=SYMPATHY, gains_xp=True)
    fields = trait_forms.scored_trait_fields(
        "", winter, include_sympathy=True, include_xp=True
    )
    opened = {f.key: f.value for f in fields}
    saved = trait_forms.trait_from(
        {"name": "Winter", "xp": opened["xp"], "sympathy": True, "temporary": False},
        winter,
    )
    assert (saved.score, saved.deeds) == (2, 20)


def test_hubris_on_the_form_always_gains_experience() -> None:
    shown = _shown_keys(ScoredTrait("Hubris (Proud)", 2, gains_xp=True))
    assert "gains_xp" not in shown and "xp" in shown
    saved = trait_forms.trait_from({"name": "Hubris (Proud)", "xp": 18}, None)
    assert (saved.score, saved.deeds, saved.gains_xp) == (2, 3, True)
    # Naming a new trait Hubris moves its typed score into XP.
    (name,) = [
        f
        for f in trait_forms.scored_trait_fields("", None, include_xp=True)
        if f.key == "name"
    ]
    assert name.fills is not None
    assert name.fills({"name": "Hubris", "score": 2, "gains_xp": False}) == {"xp": 15}


def test_only_a_sympathy_trait_counts_steps_below_0() -> None:
    sunk = ScoredTrait("Hubris", -1, gains_xp=True)
    assert st.trait_xp(sunk) == ""


def test_a_score_typed_afresh_on_a_temporary_trait_drops_old_experience() -> None:
    winter = ScoredTrait("Winter", 2, deeds=10, type=SYMPATHY, gains_xp=True)
    saved = trait_forms.trait_from(
        {"name": "Winter", "score": 4, "sympathy": True, "temporary": True}, winter
    )
    assert (saved.score, saved.deeds, saved.gains_xp) == (4, 0, False)


def test_xp_toward_a_negative_step_stays_below_its_cost() -> None:
    # Iron -1: 10 xp raise it to 0 (RoP:F p. 103).
    values = {
        "name": "Iron",
        "score": -1,
        "toward": 10,
        "sympathy": True,
        "temporary": False,
    }
    problem = trait_forms.score_problem(values, None, None)
    assert problem is not None and "10" in problem


def test_a_saved_hubris_or_sympathy_trait_loads_gaining_experience() -> None:
    data = asdict(Character(id="m", name="Hephaestion", type="magus"))
    data["personality_traits"] = [
        {"name": "Hubris (Proud)", "score": 2, "deeds": 3},
        {"name": "Winter", "score": 1, "type": "Sympathy"},
        {"name": "Oak", "score": 2, "type": "Sympathy, temporary"},
        {"name": "Brave", "score": 1},
    ]
    loaded = Character.from_dict(data)
    assert [(t.name, t.gains_xp) for t in loaded.personality_traits] == [
        ("Hubris (Proud)", True),
        ("Winter", True),
        ("Oak", False),
        ("Brave", False),
    ]
    assert [st.trait_xp(t) for t in loaded.personality_traits] == [
        "18/30",
        "5/15",
        "",
        "",
    ]


def test_a_broken_bargain_s_sympathy_trait_gains_experience() -> None:
    magus = _magus()
    trait = faerie_dealings.break_bargain(magus, "Thorns")
    # -3, and 20 xp raise it to -2 (RoP:F pp. 103, 132).
    assert (trait.gains_xp, st.trait_xp(trait)) == (True, "0/20")


def test_climbing_out_of_the_negatives_spends_step_by_step() -> None:
    # From -3, 45 xp is 20 + 15 + 10: it reaches 0 with nothing toward +1,
    # not +3 (RoP:F p. 103; Errata p. 68 lets it rise through 0).
    iron = ScoredTrait("Iron", -3, type=SYMPATHY, gains_xp=True)
    faerie_dealings.trait_experience(iron, 45, 10, limited=True)
    assert (iron.score, st.trait_xp(iron)) == (0, "0/5")
    # From -1, 12 xp: 10 to reach 0, 2 left toward +1 at the Ability rate.
    stone = ScoredTrait("Stone", -1, type=SYMPATHY, gains_xp=True)
    faerie_dealings.trait_experience(stone, 12, 10, limited=True)
    assert (stone.score, stone.deeds, st.trait_xp(stone)) == (0, 2, "2/5")
