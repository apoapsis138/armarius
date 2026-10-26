"""Warping by realm: effects by the main source, the realms' answers to 2
or more points at once, leaving Faerie and instant travel."""

import random

import pytest

from ars_magica_manager import seasons
from ars_magica_manager.forms import character as character_forms
from ars_magica_manager.models import (
    Ability,
    Aging,
    Character,
    Characteristics,
    Covenant,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.rules import hybrid_magic, realm_warping, warping
from ars_magica_manager.sheets.character import aging_text


class _Dice(random.Random):
    """Faces in order (0-9 each), then 5s."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):
        return self.faces.pop(0) if self.faces else 5


def _saga(kind: str = "companion", realm: str = "Magic", aura: int = 3) -> Saga:
    covenant = Covenant(id="cov", saga_id="s", name="Keep", aura_realm=realm)
    covenant.aura = aura
    person = Character(id="p", name="Brother Anselm", type=kind, covenant_id="cov")
    person.characteristics = Characteristics(
        stamina=1, presence=2, perception=1, intelligence=1
    )
    person.background.year_born = 1180
    person.aging = Aging()
    saga = Saga(id="s", name="S", covenants=[covenant], characters=[person])
    saga.current_season = "Spring"
    saga.current_year = 1220
    return saga


def _holy_power() -> str:
    _, powers = hybrid_magic.methods_and_powers("Divine")
    return min(powers)


# --- counting by realm, and effects by the main source ---------------------


def test_points_are_counted_by_realm_and_the_most_is_the_main_source():
    saga = _saga(realm="Faerie")
    person = saga.characters[0]
    assert realm_warping.main_realm(saga, person) == "Faerie"  # nothing counted
    realm_warping.record(person, "Divine", 3)
    realm_warping.record(person, "Infernal", 2)
    realm_warping.record(person, "Divine", 1)
    assert person.aging.warping_realms == {"Divine": 4, "Infernal": 2}
    assert realm_warping.main_realm(saga, person) == "Divine"
    realm_warping.record(person, "Faerie", 4)  # a tie goes to the home aura
    assert realm_warping.main_realm(saga, person) == "Faerie"


def test_each_realm_colours_the_effects_of_warping():
    infernal = realm_warping.effects(0, 6, "Infernal")
    assert [line.split(" (")[0] for line in infernal] == [
        "Warping Score 1",
        "Warping Score 3",
        "Warping Score 5",
        "Warping Score 6",
    ]
    assert "Aptitude for (Sin)" in infernal[2]  # the Errata's name
    assert "Tainted with Evil" in infernal[1]
    divine = realm_warping.effects(4, 6, "Divine")
    assert "no more Warping from Divine auras" in divine[0]
    assert "Pious (Major)" in divine[1]
    faerie = realm_warping.effects(0, 1, "Faerie")
    assert "glamour" in faerie[0] and "Reputation" in faerie[0]
    # The glamour's Sympathy points alternate from 6.
    assert "-1 Sympathy Trait" in realm_warping.effects(5, 6, "Faerie")[0]
    assert "+1 Sympathy point" in realm_warping.effects(6, 7, "Faerie")[0]
    assert "-1 Sympathy point" in realm_warping.effects(7, 8, "Faerie")[0]
    assert "Minor Flaw from the main source" in realm_warping.effects(0, 1, "Magic")[0]


def test_an_event_s_warping_takes_its_realm_s_effects_for_a_non_magus():
    saga = _saga()
    person = saga.characters[0]
    notes = seasons.gain_warping(saga, person, 3, _Dice(), realm="Infernal")
    assert notes == ["+3 Warping Points; Warping Score 0."]
    assert person.aging.warping_realms == {"Infernal": 3}
    notes = seasons.gain_warping(saga, person, 2, _Dice(), realm="Infernal")
    assert any("Warping Score 1 (Infernal Warping)" in line for line in notes)
    assert person.diary[-1].name == "Warping +2"
    assert "Realm: Infernal" in person.diary[-1].details


def test_the_attuned_virtue_stops_only_its_own_realm_s_aura():
    saga = _saga(realm="Divine", aura=8)
    person = saga.characters[0]
    warping.set_total(person, warping.points_for(5))
    realm_warping.record(person, "Infernal", 75)
    note = seasons.character_effects._yearly_warping(saga, person)
    assert "Divine aura 8: 2" in note  # Infernal is the main source
    person.aging.warping_realms = {"Divine": 75}
    assert seasons.character_effects._yearly_warping(saga, person) == ""


def test_yearly_warping_is_counted_by_its_realm():
    saga = _saga(realm="Faerie", aura=8)
    person = saga.characters[0]
    person.aging.longevity_modifier = 2
    seasons.character_effects._yearly_warping(saga, person)
    assert person.aging.warping_realms == {"Magic": 1, "Faerie": 2}


def test_the_sheet_shows_the_count_and_the_main_source():
    saga = _saga()
    person = saga.characters[0]
    assert "Warping by realm" not in aging_text(person, saga)
    realm_warping.record(person, "Divine", 2)
    assert "Warping by realm: Divine 2 (main source: Divine)" in aging_text(
        person, saga
    )


def test_a_saved_count_is_checked_on_load():
    assert Aging.from_dict({"warping_realms": {"Faerie": 4}}).warping_realms == {
        "Faerie": 4
    }
    assert Aging.from_dict({}).warping_realms == {}
    with pytest.raises(ValueError, match="Faerie"):
        Aging.from_dict({"warping_realms": {"Faerie": "four"}})


# --- the answer to 2 or more points at once --------------------------------


def test_who_answers_with_what():
    saga = _saga()
    person = saga.characters[0]
    assert realm_warping.response_realm(person) is None
    person.traditions = ["trad_wise_folk"]
    assert realm_warping.response_realm(person) == "Faerie"
    person.traditions = ["trad_wise_folk", "trad_strigae"]
    assert realm_warping.response_realm(person) == "Infernal"  # before Faerie
    person.traditions = []
    person.abilities.append(Ability(_holy_power(), xp=5))
    assert realm_warping.response_realm(person) == "Divine"
    person.type = "magus"  # a magus goes into Twilight, True Faith or not
    assert realm_warping.response_realm(person) == "Magic"


def test_a_magus_goes_into_twilight_unless_something_takes_its_place():
    saga = _saga(kind="magus")
    magus = saga.characters[0]
    assert realm_warping.response_realm(magus) == "Magic"
    assert not realm_warping.may_seek_ascent(magus)
    magus.aging.seeks_ascent = True  # no Miraculous Abilities: still Twilight
    assert realm_warping.response_realm(magus) == "Magic"
    magus.abilities.append(Ability(_holy_power(), xp=5))
    assert realm_warping.may_seek_ascent(magus)
    assert realm_warping.response_realm(magus) == "Divine"  # the troupe's choice
    magus.aging.seeks_ascent = False
    assert realm_warping.response_realm(magus) == "Magic"
    # An infernalist (the False Gift, RoP: The Infernal p. 124).
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_the_false_gift"))
    assert realm_warping.response_realm(magus) == "Infernal"
    magus.virtues_flaws.clear()
    magus.traditions = ["trad_strigae"]
    assert realm_warping.response_realm(magus) == "Infernal"
    magus.traditions = ["trad_wise_folk"]  # a Faerie tradition alone: Twilight
    assert realm_warping.response_realm(magus) == "Magic"
    # A homunculus wizard (RoP: Faerie p. 118).
    magus.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_homunculus_wizard"))
    assert realm_warping.response_realm(magus) == "Faerie"


def test_the_form_offers_the_ascent_only_to_a_magus_with_miraculous_abilities():
    saga = _saga(kind="magus")
    magus = saga.characters[0]
    names = [f.key for f in character_forms.aging_fields(magus.aging, saga, magus)]
    assert "seeks_ascent" not in names
    magus.abilities.append(Ability(_holy_power(), xp=5))
    fields = character_forms.aging_fields(magus.aging, saga, magus)
    ascent = next(f for f in fields if f.key == "seeks_ascent")
    assert ascent.label == "Seeks Divine Ascent instead of Twilight"
    values = {f.key: f.value for f in fields}
    values["seeks_ascent"] = True
    character_forms.apply_aging(saga, magus, values, _Dice())
    assert magus.aging.seeks_ascent
    assert Aging.from_dict({"seeks_ascent": True}).seeks_ascent
    assert not Aging.from_dict({}).seeks_ascent


def test_ascent_time_counts_days_then_months():
    # Dominia: Score 0, 13 points in all, True Faith 1 (RoP: The Divine p. 63).
    assert realm_warping.ascent_time(0, 13, 1) == (12, "days", 0)
    assert realm_warping.ascent_time(0, 1, 3) == (1, "days", 0)
    assert realm_warping.ascent_time(6, 3, 0) == (9, "months", 3)


def test_a_holy_character_fails_the_ascension_and_ascends():
    saga = _saga(realm="Divine", aura=5)
    person = saga.characters[0]
    person.traditions = ["trad_ascetics"]
    person.background.true_faith_score = 1
    # His die 5: 2 + 5 = 7; theirs 8: 0 + 3 + 1 + 5 + 8 = 17; margin 10.
    notes = seasons.gain_warping(saga, person, 3, _Dice(5, 8), realm="Divine")
    assert warping.total_points(person) == 13
    assert any("ascends for 12 days, +10 more" in line for line in notes)
    assert person.diary[-1].name == "Divine Ascent"
    assert "Realms of Power: The Divine" in person.diary[-1].details
    assert person.aging.warping_realms == {"Divine": 13}
    assert not person.aging.twilight_until  # days: less than a season


def test_the_holy_character_s_own_die_may_botch():
    saga = _saga()
    person = saga.characters[0]
    person.traditions = ["trad_ascetics"]
    # His die a 0 with its botch die a 0; the Warping's die never botches.
    notes = seasons.gain_warping(saga, person, 2, _Dice(0, 0, 0, 5))
    assert any("Divine Ascension: 2" in line and "(botched)" in line for line in notes)
    assert person.diary[-1].name == "Divine Ascent"


def test_a_holy_character_who_resists_stays():
    saga = _saga()
    person = saga.characters[0]
    person.traditions = ["trad_ascetics"]
    notes = seasons.gain_warping(saga, person, 2, _Dice(9, 2))
    assert any("does not ascend" in line for line in notes)
    assert person.diary[-1].name == "Warping +2"


def test_an_infernalist_s_vituperation_hardens_his_confidence_once_over():
    saga = _saga(realm="Infernal", aura=4)
    person = saga.characters[0]
    person.traditions = ["trad_strigae"]
    warping.set_total(person, warping.points_for(3))
    # His die 2: 1 + 0 + 0 + 2 = 3, far below the Warping's side.
    notes = seasons.gain_warping(saga, person, 2, _Dice(2, 5), realm="Infernal")
    assert person.diary[-1].name == "Vituperation"
    assert any("Aging roll adding his Warping Score (3)" in line for line in notes)
    # RoP: The Infernal p. 95: the Points come at once (they wait on
    # nothing); the Score's rise waits on the ordeal and its Aging roll.
    due = next(line for line in notes if "Confidence Points" in line)
    assert "+2 Confidence Points, given now" in due
    assert "rises from 0 to 1 (below his Warping Score 3)" in due
    assert person.background.confidence_score == 0
    assert person.background.confidence_points == 2


def test_vituperation_s_confidence_rise_may_wait_on_decrepitude():
    saga = _saga()
    person = saga.characters[0]
    person.background.confidence_score = 2
    person.aging.decrepitude = 1
    due = realm_warping.confidence_due(person, 3, botched=False)
    assert "+3 Confidence Points" in due
    assert "rises by 1 only if that Aging roll leaves his Decrepitude" in due


def test_a_botched_vituperation_gives_no_confidence_points():
    saga = _saga()
    person = saga.characters[0]
    person.traditions = ["trad_strigae"]
    notes = seasons.gain_warping(saga, person, 2, _Dice(0, 0, 5))  # a 0, then a botch
    assert any("No Confidence Points (the avoidance roll botched)" in n for n in notes)
    assert person.background.confidence_points == 0


def test_a_faerie_calling_says_from_which_rank_it_is_good():
    saga = _saga()
    person = saga.characters[0]
    person.traditions = ["trad_wise_folk"]
    warping.set_total(person, warping.points_for(2))
    # Perception 1 + Concentration 0 + die 5 = 6 against 3 x (2 - Rank):
    # good from Rank 1 (6 > 3).
    notes = seasons.gain_warping(saga, person, 2, _Dice(5), realm="Faerie")
    assert person.diary[-1].name == "Faerie Calling"
    assert any("against 12" in line for line in notes)  # 3 x (2 + 2)
    assert any("Faerie Rank of 1 or more" in line for line in notes)
    assert realm_warping.good_calling_rank(2, 6) == 1
    assert realm_warping.good_calling_rank(2, 5) == 1
    assert realm_warping.good_calling_rank(2, 3) == 2  # 3 > 3 x 0 needs Rank 2


def test_a_faerie_calling_s_resolving_die_may_botch():
    saga = _saga()
    person = saga.characters[0]
    person.traditions = ["trad_wise_folk"]
    notes = seasons.gain_warping(saga, person, 2, _Dice(0, 0), realm="Faerie")
    assert any("stress die 1 (botched)" in line for line in notes)


def test_a_non_magus_outside_any_tradition_has_no_episode():
    saga = _saga()
    person = saga.characters[0]
    seasons.gain_warping(saga, person, 5, _Dice())
    assert person.diary[-1].name == "Warping +5"


def test_points_that_come_apart_bring_no_twilight():
    saga = _saga(kind="magus")
    magus = saga.characters[0]
    seasons.gain_warping(saga, magus, 6, _Dice(), at_once=False)
    assert magus.diary[-1].name == "Warping +6"
    assert warping.total_points(magus) == 6


# --- leaving Faerie ---------------------------------------------------------


def test_leaving_faerie_by_fable_score_and_warping_taken():
    # Branoic: three days at fable score 2, takes 2 points (RoP: Faerie p. 30).
    back = realm_warping.leaving_faerie(3, 2, 2)
    assert (back.effective, back.each_day, back.passed) == (0, "an hour", "3 hours")
    # Four days at fable score 5: four months, or four days taking 3.
    assert realm_warping.leaving_faerie(4, 5).passed == "4 months"
    assert realm_warping.leaving_faerie(4, 5, 3).passed == "4 days"
    # Aethelbald: 140 days at fable score 8, a year a day.
    assert realm_warping.leaving_faerie(140, 8).passed == "140 years"
    assert realm_warping.matching_points(5, 2) == 3
    assert realm_warping.matching_points(1, 2) == 0


def test_the_form_s_leaving_faerie_brings_no_twilight():
    saga = _saga(kind="magus")
    magus = saga.characters[0]
    values = {
        "decrepitude": 0,
        "effects": "",
        "warping_score": 0,
        "warping_points": 0,
        "aura_time": "always",
        "gain_warping": 3,
        "warping_cause": character_forms.LEAVING_FAERIE,
        "faerie_days": 4,
        "fable_score": 5,
        "warping_realm": "Magic",
    }
    notes = character_forms.apply_aging(saga, magus, values, _Dice())
    assert "each day lasted a day, 4 days in the mundane world" in notes[0]
    assert magus.diary[-1].name == "Warping +3"
    assert "Realm: Faerie" in magus.diary[-1].details
    assert magus.aging.warping_realms == {"Faerie": 3}


# --- instant travel ---------------------------------------------------------


def test_instant_transport_warps_unless_made_for_them_or_a_portal():
    assert realm_warping.transit_points(40) == 1
    assert realm_warping.transit_points(25) == 0
    assert realm_warping.transit_points(40, designed_for=True) == 0
    assert realm_warping.transit_points(40, cast_by_target=True) == 0
    assert realm_warping.transit_points(75, portal=True) == 0


def test_the_form_s_transits_are_points_apart_with_travel_flaws():
    saga = _saga(kind="magus")
    magus = saga.characters[0]
    values = {
        "decrepitude": 0,
        "effects": "",
        "warping_score": 0,
        "warping_points": 0,
        "aura_time": "always",
        "gain_warping": 5,
        "warping_cause": character_forms.TRANSITS,
    }
    notes = character_forms.apply_aging(saga, magus, values, _Dice())
    assert notes[0].startswith("5 instant transit(s)")
    assert any("Motion Sickness" in line for line in notes)
    assert magus.diary[-1].name == "Warping +5"  # no Twilight
    assert magus.aging.warping_score == 1
    assert realm_warping.travel_effects(1, 3) == [
        "Instant transport (TME p. 114): the second Flaw may be another of those."
    ]
