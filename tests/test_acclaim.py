"""House Acclaim (HoH: True Lineages pp. 21-23; HoH: Societates p. 31;
Legends of Hermes p. 45), Jerbiton's leagues and Rhaetian (HoH:
Societates pp. 53-55), Flambeau's tournaments (HoH: Societates pp. 20-22)
and the Reputation roll (DE p. 28)."""

from __future__ import annotations

import random

from ars_magica_manager.forms import acclaim as forms
from ars_magica_manager.models import (
    Ability,
    Character,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import acclaim as ac
from ars_magica_manager.rules import activities, languages
from ars_magica_manager.rules import creation_virtues as cv
from ars_magica_manager.rules import flambeau_tournament as ft


class Rigged(random.Random):
    """Every d10 comes up `face` (a stress die's 1 doubles, so avoid it)."""

    def __init__(self, face: int) -> None:
        super().__init__(0)
        self.face = face

    def randrange(self, *args: int, **kwargs: int) -> int:
        return self.face


def magus(house: str = ac.BONISAGUS, *reps: ScoredTrait) -> Character:
    character = Character(id="m", name="Ludovicus", type="magus")
    character.hermetic.house = house
    character.reputations = list(reps)
    return character


def saga_with(character: Character) -> Saga:
    saga = Saga(id="s", name="Test")
    saga.characters.append(character)
    return saga


# -- House Bonisagus --


def test_research_points_follow_the_table():
    r = ac.RESEARCH
    assert ac.worth(r["tractatus"], 7) == 3
    assert ac.worth(r["tractatus"], 7, in_folio=True) == 6
    assert ac.worth(r["summa"], 12) == 6
    assert ac.worth(r["summa"], 12, in_folio=True) == 6  # a summa isn't a folio text
    assert ac.worth(r["spell"], 4) == 4
    assert ac.worth(r["experiment"], 4) == 8
    assert ac.worth(r["familiar"], 25) == 5
    assert ac.worth(r["stabilize"], 3) == 9
    assert ac.worth(r["talisman"]) == 2
    assert ac.worth(r["apprentice"]) == 3
    assert ac.worth(r["minor_breakthrough"]) == 15
    assert ac.worth(r["major_breakthrough"]) == 30


def test_conciattas_virtues_are_worth_breakthroughs():
    assert ac.worth(ac.RESEARCH["conciatta_minor"]) == 15
    assert ac.worth(ac.RESEARCH["conciatta_realms"]) == 30


def test_acclaim_rises_like_an_ability_through_the_ranks():
    # 5, 15, 30 and 50 Acclaim points reach 1 to 4 (TL p. 22).
    for points, score, title in (
        (4, 0, "no rank"),
        (5, 1, "Boukoloi"),
        (15, 2, "Daduchos"),
        (30, 3, "Cannophori"),
        (50, 4, "Dendrophori"),
    ):
        character = magus()
        reputation = ac.start(character, ac.BONISAGUS)
        ac.apply(character, reputation, points)
        assert (reputation.score, ac.rank(reputation.score)) == (score, title)
    assert ac.rank(6) == "Dendrophori"


def test_bonisagus_acclaim_is_known_in_the_house():
    character = magus()
    reputation = ac.start(character, ac.BONISAGUS)
    assert (reputation.name, reputation.type, reputation.reach) == (
        "House Acclaim",
        "Hermetic",
        "House Bonisagus",
    )
    assert ac.acclaim_of(character) is reputation


def test_apprentice_search_with_acclaim():
    # The core search's Ease Factor, 9 (DE p. 269), with Acclaim added.
    assert ac.APPRENTICE_EASE == 9
    assert "as normal" in ac.apprentice_search(9, False)
    taken = ac.apprentice_search(5, False)
    assert "from another magus" in taken and "antagonized" not in taken
    assert "antagonized" in ac.apprentice_search(4, False)
    assert "Enemies" in ac.apprentice_search(15, True)


def test_the_season_search_adds_a_ranked_bonisagus_acclaim():
    character = magus(ac.BONISAGUS, ScoredTrait("House Acclaim", 2, type="Hermetic"))
    character.characteristics.perception = 1
    saga = saga_with(character)
    plan = SeasonPlan(
        character_id="m",
        year=1220,
        season="Spring",
        activity="search_apprentice",
        die=5,
    )
    outcome = activities.outcome(character, plan, saga, random.Random(0))
    assert any(
        "House Acclaim 2 + die 5 = 8 against 9" in note and "from another magus" in note
        for note in outcome.notes
    )


def test_no_acclaim_keeps_the_core_search():
    character = magus(ac.FLAMBEAU, ScoredTrait("House Acclaim", 2, type="Hermetic"))
    assert ac.apprentice_bonus(character) == 0
    assert ac.apprentice_bonus(magus()) == 0


def test_trianomas_cipher():
    assert ac.cipher_ease(2, 3) == 11
    assert ac.cipher_bonus(3, 4, False) == 7
    assert ac.cipher_bonus(3, 4, True) == 10
    # It must be higher than the Ease Factor.
    tie = ac.decode_cipher(Rigged(4), 7, 11)
    assert tie.total == 11 and "holds" in tie.said
    assert "decoded" in ac.decode_cipher(Rigged(5), 7, 11).said


def test_folio_argument_takes_the_higher_total():
    assert "won" in ac.folio_argument(Rigged(5), 4, 8).said
    assert "neither" in ac.folio_argument(Rigged(4), 4, 8).said
    assert "lost" in ac.folio_argument(Rigged(3), 4, 8).said


def test_benefits_say_where_acclaim_adds():
    character = magus(ac.BONISAGUS, ScoredTrait("House Acclaim", 3))
    said = " ".join(ac.benefits(character, character.reputations[0]))
    assert "Cannophori" in said and "+3 to social rolls" in said
    assert "certamen" in said


# -- House Flambeau --


def test_flambeau_deeds():
    d = ac.DEEDS
    assert ac.worth(d["march"]) == 1
    assert ac.worth(d["won_senior"]) == 2
    assert ac.worth(d["won_war"], 3) == 6
    assert ac.worth(d["renounced"], 2) == 6
    assert ac.worth(d["beast"], 30) == 6
    assert ac.worth(d["gauntlet"], 9) == 5
    assert ac.worth(d["brave"], 0) == 1
    assert ac.worth(d["idle"]) == -1
    assert ac.worth(d["lost_junior"]) == -2
    assert ac.worth(d["dishonest"], 2) == -2
    assert {k: v[1] for k, v in ac.TOURNAMENT.items()} == {
        "competed": 1,
        "finalist": 3,
        "champion": 5,
        "dismal": -2,
    }


def test_flambeau_acclaim_starts_with_miles_and_famous():
    character = magus(ac.FLAMBEAU)
    character.virtues_flaws.append(VirtueFlawInstance(ac.MILES))
    reputation = ac.start(character, ac.FLAMBEAU)
    assert (reputation.score, reputation.deeds, reputation.reach) == (
        1,
        0,
        "the Order",
    )
    famous = ac.start(magus(ac.FLAMBEAU), ac.FLAMBEAU, famous=True)
    assert famous.score == 4


def test_losing_acclaim_takes_experience_and_stops_at_zero():
    reputation = ScoredTrait("House Acclaim", 2, deeds=3)  # 18 xp
    assert ac.lose(reputation, 5) == 0
    assert (reputation.score, reputation.deeds) == (1, 8)
    assert ac.lose(reputation, 20) == 7
    assert (reputation.score, reputation.deeds) == (0, 0)


def test_an_ignoble_act_at_zero_starts_a_bad_reputation():
    character = magus(ac.FLAMBEAU)
    reputation = ac.start(character, ac.FLAMBEAU)
    change = ac.apply(character, reputation, -1, "Coward")
    assert change.bad == "Coward"
    coward = next(r for r in character.reputations if r.name == "Coward")
    assert (coward.score, coward.type) == (-1, "Hermetic")
    # Not when Acclaim had points to lose.
    reputation.score = 1
    assert ac.apply(character, reputation, -1, "Liar").bad == ""


# -- the forms --


def test_acclaim_form_records_research_in_the_diary():
    character = magus()
    saga = saga_with(character)
    values = {
        "what": "award",
        "award": "tractatus",
        forms.AMOUNT_KEYS["Quality"]: 10,
        "in_folio": True,
    }
    assert "+10 Acclaim points" in forms.acclaim_lines(character, values)[0]
    said = forms.record(saga, character, values, Rigged(5))
    assert said[0] == "Started House Acclaim at 0."
    reputation = ac.acclaim_of(character)
    assert reputation is not None and (reputation.score, reputation.deeds) == (1, 5)
    assert character.diary[-1].name == "House Acclaim"


def test_acclaim_form_tournament_place():
    character = magus(ac.FLAMBEAU)
    values = {"what": "award", "award": "tournament", "place": "champion"}
    assert forms.points(ac.FLAMBEAU, values) == 5
    forms.record(saga_with(character), character, values, Rigged(5))
    reputation = ac.acclaim_of(character)
    assert reputation is not None and (reputation.score, reputation.deeds) == (1, 0)


def test_acclaim_form_offers_by_house():
    assert forms.offers(Saga(id="s", name="x"), magus(ac.BONISAGUS))
    assert forms.offers(Saga(id="s", name="x"), magus(ac.FLAMBEAU))
    assert not forms.offers(Saga(id="s", name="x"), magus("house_tytalus"))
    held = magus("house_tytalus", ScoredTrait("House Acclaim", 1, reach="the Order"))
    assert (
        forms.offers(Saga(id="s", name="x"), held) and forms.house(held) == ac.FLAMBEAU
    )
    keys = {f.key for f in forms.acclaim_fields(magus(ac.FLAMBEAU))}
    assert "place" in keys and "style" not in keys


def test_folio_argument_form_adds_acclaim():
    character = magus(ac.BONISAGUS, ScoredTrait("House Acclaim", 2))
    character.characteristics.communication = 2
    character.abilities.append(Ability("Artes Liberales", "Academic", xp=30))
    assert forms.folio_bonus(character, {"style": forms.CRAFTY}) == 7


# -- Jerbiton, the Reputation roll, Rhaetian --


def test_league_colleagues_count_reputations_three_higher():
    reputation = ScoredTrait("Painter", 2)
    assert ac.heard_bonus(reputation, False) == 2
    assert ac.heard_bonus(reputation, True) == 5
    assert ac.heard_bonus(ScoredTrait("Liar", -2), False) == 2


def test_heard_of_meets_or_beats_the_ease():
    reputation = ScoredTrait("Painter", 2)
    assert "has heard" in ac.heard_of(Rigged(4), reputation, 6).said
    assert "hasn't" in ac.heard_of(Rigged(3), reputation, 6).said
    assert "has heard" in ac.heard_of(Rigged(3), reputation, 6, colleague=True).said


def test_heard_eases_by_type():
    assert ac.heard_eases("Hermetic") == [
        (0, "Same covenant"),
        (6, "Same Tribunal"),
        (9, "Entire Order"),
    ]
    assert ac.heard_eases("Local")[-1] == (12, "Same country")


def test_reputation_roll_form_records_the_roll():
    character = magus(ac.BONISAGUS, ScoredTrait("Painter", 2, type="Local"))
    saga = saga_with(character)
    values = {"reputation": "0", "ease": "6", "colleague": True}
    assert (
        "Stress die + 5 against 6 (same town)" in forms.roll_lines(character, values)[0]
    )
    said = forms.record_roll(saga, character, values, Rigged(4))
    assert "has heard" in said[0]
    assert character.diary[-1].name == "Reputation Roll"


def test_rhaetian_is_latin_at_three_less():
    assert languages.penalty("Living Language: Rhaetian", "Latin") == 3
    assert languages.penalty("Dead Language: Latin", "Rhaetian") == 3


def test_jerbitons_free_virtue_prefers_a_suited_one():
    character = magus(ac.JERBITON)
    character.virtues_flaws = [
        VirtueFlawInstance("vf_affinity_with_art", {"art": "ignem"}),
        VirtueFlawInstance("vf_gossip"),
    ]
    assert cv.house_benefit(character).free_indices == frozenset({1})


# -- tournaments --


def test_tournament_certamen():
    assert ft.choosers(20, 35) == ("a", "b")
    assert ft.choosers(35, 20) == ("b", "a")
    assert ft.choosers(10, 10) is None
    assert not ft.may_veto(2, vetoed_first=True)
    assert ft.may_veto(2, vetoed_first=False) and ft.may_veto(3, vetoed_first=True)
    assert ft.match_won(2, 1) is True and ft.match_won(1, 2) is False
    assert ft.match_won(1, 1) is None


def test_dimicatio_and_the_melee():
    assert ft.may_enter_dimicatio(2) and not ft.may_enter_dimicatio(1)
    assert ft.forceless(12) == 0 and ft.forceless(-3) == -3
    assert ft.defence_level(35) == 18
    assert ft.melee_damage_allowed(3) and not ft.melee_damage_allowed(4)
    assert not ft.melee_damage_allowed(1, castra_solis=True)
