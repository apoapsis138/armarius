"""The Hyperborean hymns (Ancient Magic pp. 103-118, errata p. 58): Power
level costs and Ease Factors, the levels a hymn holds, recitation
modifiers, relics, choirs and Illumination, checked against the book's
own examples."""

import pytest

from ars_magica_manager import catalog, tradition_text
from ars_magica_manager.models import (
    Character,
    Characteristics,
    Saga,
    TraditionDef,
    TraditionEffect,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import creation_tradition as ct
from ars_magica_manager.rules import hedge_casting as hc
from ars_magica_manager.rules import hyperborean as hy
from ars_magica_manager.rules import tradition_seasons as ts
from ars_magica_manager.rules import tradition_totals as tt
from ars_magica_manager.rules.xp import xp_for_score


def _t() -> TraditionDef:
    return catalog.load_tradition_catalog_by_id()[hy.TRADITION_ID]


def _hymnist(gifted: bool = True, **chars: int) -> Character:
    character = Character(
        id="c",
        name="Abaris",
        type="companion",
        characteristics=Characteristics(**chars),
    )
    character.traditions = [hy.TRADITION_ID]
    character.virtues_flaws = [VirtueFlawInstance("vf_the_gift")] if gifted else []
    ct.open_tradition(character)
    return character


def _set(character: Character, name: str, score: int) -> None:
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        ability = ct.opened_ability(name)
        character.abilities.append(ability)
    ability.xp = xp_for_score(score, ability.factor)


def _power(name: str, hymn: str, level: int, rule: str = hy.INFUSE) -> TraditionEffect:
    return TraditionEffect(
        name,
        tradition=hy.TRADITION_ID,
        kind="power",
        rule=rule,
        uses=[hymn],
        level=level,
    )


# ---------------------------------------------------------------------------
# The catalog


def test_every_hymn_has_its_principles_and_the_numina():
    tradition = _t()
    for hymn in hy.hymns_of(tradition):
        principles = [g for g in tradition.guidelines if g.arts == [hymn]]
        assert principles and all(g.general for g in principles), hymn
    assert any(g.name.startswith("Numina of Apollo") for g in tradition.guidelines)
    assert all(g.page and 103 <= g.page <= 118 for g in tradition.guidelines)


def test_the_recitation_adds_the_dead_language():
    tradition = _t()
    character = _hymnist(communication=1)
    _set(character, "Hymn Psyrinpheu", 1)
    _set(character, "Dead Language: Hyperborean", 3)
    rule = next(r for r in tradition.casting if r.name == hy.INFUSE)
    total = hc.casting_score(
        character, tradition, rule, ["Hymn Psyrinpheu"], aura=2
    ).total
    assert total == 1 + 1 + 3 + 2


# ---------------------------------------------------------------------------
# Power level costs and Ease Factors (pp. 110-118, errata p. 58)

SAMPLES = [
    # (name, base, keyword arguments, level cost, Ease Factor)
    ("Apollo's Luminescent Blessing", 4,
     {"range_": "Touch", "duration": "Concentration", "penetration": 4, "uses_per_day": 6}, 15, 5),
    ("Sovereignty of Phoebus Apollo", 5,
     {"range_": "Sight", "duration": "Sun", "levels": 4}, 34, 12),
    ("Defy the Hound Cerebus", 15,
     {"range_": "Arcane Connection", "duration": "Concentration", "penetration": 10}, 45, 15),
    ("False Dream", 2,
     {"range_": "Arcane Connection", "duration": "Sun", "penetration": 4}, 22, 8),
    ("Demeter's Blessing", 1,
     {"range_": "Touch", "duration": "Year", "target": "Boundary", "magnitudes": 1}, 35, 12),
    ("Bestow Fecundity", 30, {"range_": "Touch"}, 35, 12),
    ("The Gift of Far-sighted Apollo", 3, {"duration": "Sun", "target": "Vision"}, 25, 9),
    ("Opening the Hidden Eyes", 5,
     {"range_": "Touch", "duration": "Concentration", "target": "Vision", "magnitudes": 1}, 40, 14),
    ("The Unseen Traveler", 4, {"duration": "Sun", "magnitudes": 1}, 15, 5),
    ("Ride the Arrow of Abaris", 35, {"range_": "Sight"}, 50, 17),
    ("Punishment of Marsyas", 20, {"range_": "Touch", "levels": 4, "uses_per_day": 2}, 30, 10),
    ("Fortitude of Cadmus", 5, {"duration": "Sun"}, 15, 5),
    ("Victory of the Lapiths", 10, {"duration": "Diameter"}, 15, 5),
    ("Courage of the Python Slayer", 4,
     {"range_": "Voice", "duration": "Sun", "penetration": 2, "uses_per_day": 12}, 25, 9),
    ("Slaying of Niobe's Children", 20,
     {"range_": "Voice", "penetration": 4, "uses_per_day": 6}, 35, 12),
    ("Eternal Youth of the Sun", 40, {"duration": hy.NINETEEN_YEARS}, 65, 22),
    ("Thalia's Relief", 4, {"range_": "Touch", "duration": "Sun"}, 15, 5),
    ("Divination of True Intent", 15,
     {"range_": "Eye", "penetration": 4, "uses_per_day": 6}, 25, 9),
    # Relic Powers (pp. 117-118).
    ("Protection of the Bright Lightener", 20,
     {"range_": "Touch", "duration": "Sun", "magnitudes": 3, "uses_per_day": 2,
      "penetration": 20, "environmental": True}, 64, 22),
    ("Apollo's Soothing Relief", 15, {"range_": "Touch", "uses_per_day": 6}, 23, 8),
    ("Lifting Apollo's Curse", 4,
     {"range_": "Touch", "duration": "Moon", "uses_per_day": 6}, 23, 8),
    ("Sight of the Pythian Oracle", 2,
     {"range_": "Arcane Connection", "duration": "Sun", "target": "Room",
      "uses_per_day": 2, "environmental": True}, 34, 12),
    # The enchantment example, as the errata corrects it.
    ("Obelisk of Thalia's Relief", 4,
     {"range_": "Touch", "duration": "Sun", "target": "Boundary"}, 35, 12),
]  # fmt: skip


@pytest.mark.parametrize(("name", "base", "kw", "cost", "ease"), SAMPLES)
def test_the_books_powers_cost_and_ease(
    name: str, base: int, kw: dict, cost: int, ease: int
) -> None:
    assert hy.power_cost(base, **kw) == cost, name
    assert hy.recitation_ease(cost) == ease, name


def test_the_ease_factor_rounds_up_where_the_book_misprints():
    # Cleansing Libation costs 55 (with its Touch Range); the book prints 18.
    cost = hy.power_cost(
        5, range_="Touch", duration=hy.NINETEEN_YEARS, target="Boundary"
    )
    assert cost == 55 and hy.recitation_ease(cost) == 19


def test_nineteen_years_is_a_magnitude_above_year():
    assert hy.magnitudes_of(duration=hy.NINETEEN_YEARS) == 5
    with pytest.raises(ValueError):
        hy.magnitudes_of(duration="Forever")


def test_night_invocation_and_numina():
    assert hy.night_minutes(9) == 135
    assert hy.numina_resistance(20) == 15
    assert hy.numina_resistance(3) == 0


# ---------------------------------------------------------------------------
# Levels held, infused and left (pp. 104, 107-109)


def test_levels_per_point_ignore_puissant():
    character = _hymnist()
    _set(character, "Hymn Psyrinpheu", 2)
    character.virtues_flaws.append(
        VirtueFlawInstance("vf_puissant_ability", params={"ability": "Hymn Psyrinpheu"})
    )
    assert hy.hymn_levels(character, "Hymn Psyrinpheu") == 30
    assert hc.score(character, "Hymn Psyrinpheu") == 4
    character.tradition_effects = [
        _power("Victory of the Lapiths", "Hymn Psyrinpheu", 15),
        _power("A relic's Power", "Hymn Psyrinpheu", 20, rule=hy.RELIC),
    ]
    assert hy.infused_levels(character, "Hymn Psyrinpheu") == 15
    assert hy.levels_left(character, "Hymn Psyrinpheu") == 15
    assert hy.levels_left(character, "Hymn Psyrinpheu", hy.vis_levels(5)) == 20
    assert hy.vis_levels(5, pawns_per_level=2) == 2


def test_recitation_modifiers():
    character = _hymnist()
    character.virtues_flaws.append(VirtueFlawInstance("vf_hyperborean_descent_major"))
    found = dict(
        hy.recitation_modifiers(
            character,
            devotional_seasons=5,
            days_without=30,
            traits={"Honourable Minor Personality Flaw": 1},
        )
    )
    assert found == {
        "Devotional behaviour, 3 seasons": 9,
        "20 days without reciting": -20,
        "Hyperborean Descent": 4,
        "Honourable Minor Personality Flaw": 1,
    }
    relic = dict(hy.recitation_modifiers(character, devotional_seasons=2, relic=True))
    assert relic == {"Hyperborean Descent": 4}


def test_the_recitation_example_infuses_victory_of_the_lapiths():
    # Moratamis: Com 1 + Psyrinpheu 1 + devotion 3 + aura 2 = 7 (p. 107).
    character = _hymnist(communication=1)
    _set(character, "Hymn Psyrinpheu", 1)
    total = (
        1
        + 1
        + sum(n for _, n in hy.recitation_modifiers(character, devotional_seasons=1))
        + 2
    )
    assert total == 7
    assert hy.recitation_ease(15) <= total
    assert hy.most_levels(total) == 21


# ---------------------------------------------------------------------------
# Relics and choirs (pp. 114-118)


def test_relic_warping_is_two_a_pawn():
    # The obelisk: level 35 needs 4 pawns, its opening 20 (p. 118).
    assert hy.relic_vis(35) == 4
    assert hy.relic_warping(35, opening_pawns=20) == 48
    assert hy.relic_warping(35) == 8


def test_the_choir_example():
    # Level 60 plague, one hymn: Ease Factor 20 and 20 pawns (p. 115).
    level = hy.choir_level(60, hymns=1)
    ease = hy.recitation_ease(level)
    assert ease == 20 and hy.choir_vis(ease) == 20
    # The focus's 8, five helpers of Com 1 + Iao 4 led with Ceremony 5.
    assert hy.choir_total(8, [5] * 5, leader_ceremony=5, days=1) == 33
    # Two hymns add 5 levels; a leader with Ceremony 3 counts three helpers.
    assert hy.choir_level(60, hymns=2) == 65
    assert hy.choir_total(8, [5] * 5, leader_ceremony=3) == 23
    # No leader: -1 for each participant, the five helpers (the focus
    # stands apart from the "five participants" of the example).
    assert hy.choir_total(8, [5] * 5, leader_ceremony=None) == 8 + 25 - 5


@pytest.mark.parametrize(
    ("days", "bonus"), [(0, 0), (1, 0), (3, 1), (6, 1), (7, 2), (21, 4), (60, 5)]
)
def test_choir_days(days: int, bonus: int) -> None:
    assert hy.choir_days_bonus(days) == bonus


# ---------------------------------------------------------------------------
# Illumination (pp. 105-106)


def _abaris() -> Character:
    character = _hymnist(stamina=2)
    character.aging.warping_score = 8
    character.aging.warping_points = 43  # 223 points in all
    character.virtues_flaws.append(VirtueFlawInstance("vf_hyperborean_descent_major"))
    _set(character, "Concentration", 5)
    _set(character, "Hymn Azai", 11)
    character.tradition_effects = [_power("Powers", "Hymn Azai", 450)]
    return character


def test_the_illumination_example():
    abaris = _abaris()
    assert hy.illumination_applies(abaris)
    assert hy.illumination_control(abaris) == 18
    assert hy.illumination_modifiers(abaris) == -4 + 15
    assert hy.updated_score(abaris, 3) == 9
    assert hy.illumination_ease(abaris, 3, aura=3) == 26
    assert hy.illumination_ease(abaris, 2, aura=3) == 0
    assert hy.transformed_hours(abaris, 3) == 226
    # The updated score 9, after the 3 points gained: 9 + 3 - 4 + 15.
    assert hy.bright_lightening(abaris, 3, aura=3) == 23
    assert hy.return_ease(9, 3, 11, failures=2) == 25


def test_illumination_is_not_for_the_ungifted_or_magi():
    assert not hy.illumination_applies(_hymnist(gifted=False))
    magus = _abaris()
    magus.type = "magus"
    assert not hy.illumination_applies(magus)


# ---------------------------------------------------------------------------
# The chapter's text and seasons


def test_the_season_notes_and_chapter_text():
    character = _hymnist(communication=2)
    character.virtues_flaws.append(VirtueFlawInstance("vf_hyperborean_descent"))
    _set(character, "Hymn Semesilam", 2)
    character.tradition_effects = [_power("Thalia's Relief", "Hymn Semesilam", 15)]
    saga = Saga(id="s", name="S", characters=[character])
    notes = tt.season_notes(saga, character, "hymnist_infuse_power", 4)
    assert notes[0] == "With Hyperborean Descent (+2): 6."
    assert "up to 18 levels" in notes[1]
    assert "Hymn Semesilam 2: 30 levels, 15 infused, 15 left." in notes
    relic = tt.season_notes(saga, character, "hymnist_enchant_relic", 4)
    assert "costs 4 Warping Points" in relic[-1]
    pools = tradition_text.pools_text(character, _t())
    assert "Hymn Semesilam 2: 30 levels, 15 infused, 15 left." in pools
    warping = tradition_text.warping_text(saga, character, _t())
    assert "Apollonian Personality Trait +0" in warping
    assert "Control: Sta + Concentration + highest Hymn = 2" in warping


def test_a_season_of_recitation_reports_its_total():
    character = _hymnist(communication=1)
    _set(character, "Hymn Psyrinpheu", 1)
    saga = Saga(id="s", name="S", characters=[character])
    found = ts.activity("hymnist_infuse_power")
    assert found is not None
    total = ts.lab_total(character, found[0], hy.INFUSE, "Hymn Psyrinpheu", 0, "Magic")
    assert total == ("Hymn Psyrinpheu", 2)
    assert "up to 6 levels" in tt.season_notes(saga, character, found[1].key, 2)[0]


def test_infused_levels_are_totalled_over_every_hymn():
    # Illumination's +1 a 30 levels counts all his hymns' Powers together
    # (p. 106: 450 levels with a highest Hymn of 11), relics aside.
    character = _hymnist()
    _set(character, "Hymn Azai", 2)
    _set(character, "Hymn Iaó", 2)
    character.tradition_effects = [
        _power("One", "Hymn Azai", 20),
        _power("Two", "Hymn Iaó", 20),
        _power("A relic's Power", "Hymn Iaó", 30, rule=hy.RELIC),
    ]
    assert hy.infused_levels(character) == 40
    assert hy.illumination_modifiers(character) == 1  # 40 / 30, not 0 + 0
