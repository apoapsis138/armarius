"""The realms as places: the Magic Realm's aura, boundaries, travel and
Twilight Void (RoP: Magic pp. 20-28), entering faerie regiones and the
Faerie Realm's Threshold (RoP: Faerie pp. 16-24), and the Lunar aura of
Dies Irae (pp. 36-38)."""

from __future__ import annotations

import pytest
from support import everything_saga

from ars_magica_manager import catalog, places
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import neighbour as neighbour_forms
from ars_magica_manager.models import Character, Neighbour, Saga, VirtueFlawInstance
from ars_magica_manager.rules import (
    aura_kinds,
    casting,
    faerie_threshold,
    hybrid_magic,
    lunar,
    otherworlds,
    realms,
    sites,
)
from ars_magica_manager.rules import lab as lab_rules


def _drachenfels(saga: Saga) -> Neighbour:
    found = sites.place(saga, "drachenfels")
    assert found is not None
    return found


# -- the Magic Realm (RoP: Magic pp. 20-28) --


def test_a_boundary_adds_to_the_realm_s_ten_and_doubles_for_its_form():
    # Corpus 4: +18 to Corpus effects, +14 to the rest (p. 22).
    assert otherworlds.boundary_bonus(4, "Corpus", ("Rego", "Corpus")) == 18
    assert otherworlds.boundary_bonus(4, "Corpus", ("Rego", "Terram")) == 14
    assert otherworlds.boundary_bonus(1, "", ("Creo", "Ignem")) == 11
    assert otherworlds.boundary_bonus(10, "Aquam", ("Aquam",)) == 30
    assert otherworlds.boundary_botch_dice(4) == 4
    assert otherworlds.boundary_level(14) == 10


def test_a_boundary_gives_vis_by_its_modified_aura():
    # Terram 4 always has two pawns (p. 22).
    assert otherworlds.boundary_vis(4) == 2
    assert otherworlds.boundary_vis(0) == 1
    assert otherworlds.boundary_vis(10) == 2


def test_a_season_there_turns_experience_to_vis():
    assert otherworlds.season_vis(10) == (10, 0)
    assert otherworlds.season_vis(10, 0.5) == (5, 5)
    assert not otherworlds.ages_there(otherworlds.MAGIC_REALM)
    assert otherworlds.ages_there(otherworlds.FAERIE_REALM)
    assert otherworlds.REALM_DURATIONS["Sun"] == "to the season's end"


def test_travel_takes_the_best_familiarity_and_gives_a_speed():
    assert otherworlds.familiarity("Has visited it") == 6
    assert otherworlds.familiarity("Has seen it", {"Area Lore: Magic Realm": 3}) == 9
    assert otherworlds.familiarity("", {"Magic Lore": 4, "Enigmatic Wisdom": 2}) == 4
    assert otherworlds.travel_ease(4) == 18
    assert otherworlds.travel_ease(4, 6) == 12
    speed = otherworlds.speed_level(30, 12)
    assert speed == 18
    assert otherworlds.journey(speed) == "until sunrise or sunset (Sun)"
    # Two botches make a Sun journey a Moon one (p. 23).
    assert otherworlds.journey(otherworlds.speed_level(30, 12, botches=2)) == (
        "a month (Moon)"
    )
    assert otherworlds.journey(-1) == otherworlds.STRANDED
    assert otherworlds.journey(1).startswith("seven years and")
    assert otherworlds.journey(40) == "a moment"
    assert otherworlds.can_travel(False, True, False)
    assert not otherworlds.can_travel(False, False, False)


def test_comprehending_the_void():
    found = otherworlds.void_comprehension(12, 9, 4, has_might=False)
    assert found == otherworlds.Comprehension(True, 1, 8, 4)
    lost = otherworlds.void_comprehension(5, 9, 3, has_might=True)
    assert lost == otherworlds.Comprehension(False, -1, -6, 0)
    assert otherworlds.comprehension_against(3) == 3
    assert otherworlds.comprehension_against(3, might=25) == 5
    assert otherworlds.void_speed(9, 20, 5) == 15
    assert otherworlds.void_speed(18, 20, 5) == 18


def test_transformations_and_magic_realm_magic():
    assert otherworlds.transformations(4) == [otherworlds.VIS_TRANSFORMATIONS[0]]
    assert len(otherworlds.transformations(30)) == 7
    # A base 25 Creo effect makes a level 1 boundary (p. 27).
    assert otherworlds.created_boundary(25) == 1
    assert otherworlds.created_boundary(15) == 0
    assert otherworlds.insight_magnitude(3) == 3


def test_a_place_in_the_magic_realm_takes_its_aura_and_boundary():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    drachenfels.details.update(world="Magic Realm", boundary=4, alignment="Terram")
    assert sites.aura_at(drachenfels, 0) == (14, "Magic")
    assert sites.world_at(drachenfels, 0) == otherworlds.MAGIC_REALM
    assert sites.boundary_at(drachenfels, 0) == 4
    assert sites.aura_kind_at(drachenfels, 0) == "Terram"
    # Only the boundary counts again for its Form.
    assert aura_kinds.art_bonus("Terram", "Magic", 14, ("Creo", "Terram")) == 4
    assert aura_kinds.art_bonus("Terram", "Magic", 6, ("Creo", "Terram")) == 6
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura"] == "Magic 14"
    assert facts["Lies in"].startswith("the Magic Realm: Magic 10 + a boundary of 4")
    assert "2 pawns of Terram vis a season" in facts["Lies in"]
    assert "slowly warp" not in facts["Aura kind"]
    # With no boundary there is nothing to add again.
    drachenfels.details["boundary"] = 0
    assert sites.aura_kind_at(drachenfels, 0) == ""
    # The levels keep their own auras.
    assert sites.aura_at(drachenfels, 1) == (6, "Faerie")


def test_a_boundary_adds_botch_dice_to_casting_and_the_lab():
    # A boundary adds its level in botch dice to every roll the Magic aura
    # helps, casting and lab work among them (RoP: Magic p. 22).
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    drachenfels.details.update(world="Magic Realm", boundary=4)
    keep = saga.covenant("cov1")
    assert keep is not None
    magus = next(c for c in saga.characters if c.name == "Leandro")
    before = lab_rules.botch_conditions(saga, magus)
    assert sites.character_boundary_botch_dice(saga, magus) == 0
    keep.place_id, keep.place_level = "drachenfels", 0
    assert sites.boundary_botch_dice((drachenfels, 0)) == 4
    assert sites.character_boundary_botch_dice(saga, magus) == 4
    lab = saga.laboratories[0]
    assert sites.lab_boundary_botch_dice(saga, lab) == 4
    assert sites.boundary_botch_dice((drachenfels, 1)) == 0  # a Faerie level
    aura, safety = lab_rules.botch_conditions(saga, magus)
    assert aura == lab_rules.lab_aura(saga, lab)[0] + 4
    assert (aura, safety) != before
    plain = casting.botch_dice(aura_realm="Magic", aura=14)
    assert casting.botch_dice(aura_realm="Magic", aura=14, boundary_dice=4) == plain + 4
    # Only while the aura there is Magic.
    faerie = casting.botch_dice(aura_realm="Faerie", aura=10)
    assert casting.botch_dice(aura_realm="Faerie", aura=10, boundary_dice=4) == faerie


def test_a_regio_level_can_open_into_faerieland():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    sites.levels(drachenfels)[1]["world"] = "Faerie Realm"
    assert sites.aura_at(drachenfels, 2) == (10, "Faerie")
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert "Level 2: the Faerie Realm: Faerie 10" in facts["Within"]


def test_the_place_forms_offer_the_worlds_with_their_books():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    keys = [f.key for f in places.fields(saga, drachenfels)]
    assert {"world", "boundary"} <= set(keys)
    level_keys = [f.key for f in places.level_fields(saga, drachenfels, None)]
    assert {"world", "boundary"} <= set(level_keys)
    saga.books_in_play = []
    keys = [f.key for f in places.fields(saga, drachenfels)]
    assert not {"world", "boundary"} & set(keys)
    saga.books_in_play = ["RoP:F"]
    (world,) = [f for f in places.fields(saga, drachenfels) if f.key == "world"]
    assert [value for _label, value in world.options] == ["Faerie Realm"]


def test_a_world_s_realm_shows_its_kind_fields():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    alignment = next(
        f for f in places.fields(saga, drachenfels) if f.key == "alignment"
    )
    assert alignment.show_if is not None
    assert alignment.show_if({"realm": "Faerie", "world": "Magic Realm"})
    assert not alignment.show_if({"realm": "Magic", "world": "Faerie Realm"})


def test_the_forms_check_a_boundary():
    good = {"aura": 0, "world": "Magic Realm", "boundary": 4, "alignment": "Terram"}
    assert places.problem(good) is None
    assert places.problem({**good, "boundary": 11}) is not None
    assert places.problem({**good, "alignment": "Ignem"}) is None
    assert "Form" in (places.problem({**good, "alignment": "Creo"}) or "")
    assert places._level_problem({**good, "boundary": -1}) is not None


# -- into Faerie (RoP: Faerie pp. 16-24) --


@pytest.mark.parametrize(
    ("aura", "realm", "base", "base_realm", "strength"),
    [
        (3, "Faerie", 0, "", 30),
        (3, "Divine", 0, "", 75),
        (5, "Faerie", 0, "", 24),
        (0, "Magic", 0, "", 39),
        # A Faerie regio of 5 over a Faerie aura of 2: a modifier of 7
        # (the book prints 15; its formula gives 18).
        (5, "Faerie", 2, "Faerie", 18),
        # ... but over a Dominion of 3, still 5.
        (5, "Faerie", 3, "Divine", 24),
        (10, "Faerie", 5, "Faerie", 0),
    ],
)
def test_the_threshold_s_strength(
    aura: int, realm: str, base: int, base_realm: str, strength: int
) -> None:
    assert (
        faerie_threshold.threshold_strength(aura, realm, base, base_realm) == strength
    )


def test_threshold_points_gather_from_circumstance():
    # Branoic on Goat Hill: a major life change with a ceremony and a
    # confluence of streams reach Faerie 5's 24 (p. 21).
    personal = faerie_threshold.personal_points(
        life_change="Major, with a religious ceremony (a wedding, a baptism)"
    )
    assert personal == 18
    points = faerie_threshold.threshold_points(
        border="Minor (a crossroads, the edge of a wood, a city wall)",
        personal=personal,
    )
    assert points == 24
    assert faerie_threshold.crosses(
        points, faerie_threshold.threshold_strength(5, "Faerie")
    )
    assert (
        faerie_threshold.threshold_points(
            border="Insignificant (a road, stream or fence)", lost=True, time="Equinox"
        )
        == 15
    )
    # Spirit Away is never the only source.
    assert faerie_threshold.threshold_points(spirit_away=20) == 0
    assert faerie_threshold.threshold_points(time="New moon", spirit_away=20) == 21


def test_personal_points_take_the_best_blood_and_an_emotion():
    assert faerie_threshold.personal_points(minor_virtues=True, faerie_flaws=True) == 3
    assert faerie_threshold.personal_points(minor_virtues=True, major_virtues=True) == 9
    assert faerie_threshold.personal_points(emotion_trait=0) == 3
    assert (
        faerie_threshold.personal_points(
            emotion_trait=faerie_threshold.PERSONALITY_FLAW_TRAIT["Major"]
        )
        == 9
    )


def test_a_character_s_faerie_blood_counts():
    vfs = catalog.load_virtue_flaw_catalog_by_id()
    someone = Character(id="c", name="Branoic", type="companion")
    assert faerie_threshold.character_points(someone, vfs) == 0
    someone.virtues_flaws.append(VirtueFlawInstance("vf_faerie_blood"))
    assert faerie_threshold.faerie_blood(someone, vfs) == (True, False, False)
    someone.virtues_flaws.append(VirtueFlawInstance("vf_strong_faerie_blood"))
    assert faerie_threshold.character_points(someone, vfs) == 9


def test_entrances_charms_guardians_and_spirit_away():
    assert faerie_threshold.guess_ease() == 15
    assert faerie_threshold.guess_ease(narrowed=True) == 3
    assert faerie_threshold.guardian_might(24) == 24
    assert faerie_threshold.charm_total(6, 2, 4, 3) == 15
    assert faerie_threshold.spirit_away_cost(5) == 5
    assert faerie_threshold.spirit_away_cost(sent_away=2) == 6


def test_a_faerie_place_shows_its_threshold_with_the_book():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    # Level 1 is Faerie 6 over a Magic surface, which doesn't count.
    assert facts["Threshold"] == "Level 1: 21 points to cross into the Faerie Realm"
    saga.books_in_play = []
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert "Threshold" not in facts


# -- the Lunar aura (Dies Irae pp. 36-38) --


def test_the_lunar_realm_table():
    assert lunar.modifier("Magic", lunar.LUNAR, 3) == -15
    assert lunar.modifier("Faerie", lunar.LUNAR, 3) == -15
    assert lunar.modifier("Infernal", lunar.LUNAR, 3) == -3
    assert lunar.modifier("Divine", lunar.LUNAR, 3) == 0
    assert lunar.modifier(lunar.LUNAR, lunar.LUNAR, 3) == 3
    assert lunar.modifier(lunar.LUNAR, "Divine", 2) == -6
    assert lunar.modifier(lunar.LUNAR, "Magic", 2) == -2
    assert lunar.modifier("Magic", "Faerie", 3) == 1
    assert len(lunar.MULTIPLE) == 25
    with pytest.raises(ValueError):
        lunar.modifier("Elysian", "Magic", 1)


def test_durations_fail_and_clearing_moves_the_aura():
    assert lunar.duration_works("Concentration")
    assert not lunar.duration_works("Sun")
    assert lunar.replacement("Moon") == "300 Miles"
    assert lunar.unformalized_magnitudes(2) == 3
    assert lunar.cleared(3, 2) == (1, 2)
    assert lunar.cleared(1, 4) == (0, 1)


def test_a_place_shows_its_lunar_aura():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    drachenfels.realm = lunar.LUNAR
    drachenfels.details["aura"] = 2
    assert sites.aura_at(drachenfels, 0) == (2, lunar.LUNAR)
    facts = {f.label: f.value for f in places.facts(saga, drachenfels)}
    assert facts["Aura"] == "Lunar 2"
    assert facts["Lunar aura"].startswith(
        "Lunar 2: Hermetic and Faerie powers -10, Infernal -2"
    )


def test_lunar_is_a_fifth_realm_in_the_realm_table():
    # The New Realm Interaction Table (Dies Irae p. 37) applies to totals.
    assert realms.aura_modifier("Magic", lunar.LUNAR, 3) == -15
    assert realms.aura_modifier("Faerie", lunar.LUNAR, 3) == -15
    assert realms.aura_modifier("Infernal", lunar.LUNAR, 3) == -3
    assert realms.aura_modifier("Divine", lunar.LUNAR, 3) == 0
    assert realms.aura_modifier(lunar.LUNAR, "Magic", 2) == -2
    assert realms.aura_modifier(lunar.LUNAR, "Divine", 2) == -6
    assert realms.aura_modifier("Magic", "Divine", 2) == -6  # the core rows stay
    for pair in lunar.MULTIPLE:
        assert realms.aura_modifier(*pair, 2) == lunar.modifier(*pair, 2)
    assert realms.extra_botch_dice("Magic", lunar.LUNAR, 3) == 3
    magus = Character(id="m", name="M", type="magus")
    assert hybrid_magic.aura_modifier(magus, lunar.LUNAR, 2) == (-10, "")


def test_the_lunar_realm_is_offered_only_with_dies_irae():
    saga = everything_saga()
    drachenfels = _drachenfels(saga)
    keep = saga.covenant("cov1")
    assert keep is not None

    def offered() -> dict[str, list[str]]:
        found: dict[str, list[str]] = {}
        for name, fields in (
            ("place", neighbour_forms.neighbour_fields(saga, drachenfels, "place")),
            ("level", places.level_fields(saga, drachenfels, None)),
            ("covenant", covenant_forms.covenant_fields(saga, keep)),
        ):
            key = "aura_realm" if name == "covenant" else "realm"
            field = next(f for f in fields if f.key == key)
            found[name] = [value for _label, value in field.options]
        return found

    saga.books_in_play = ["DI"]
    assert all(lunar.LUNAR in realms_ for realms_ in offered().values())
    saga.books_in_play = []
    assert not any(lunar.LUNAR in realms_ for realms_ in offered().values())
    # A creature's realm is never Lunar.
    (realm,) = [
        f
        for f in neighbour_forms.neighbour_fields(saga, drachenfels, "person")
        if f.key == "realm"
    ]
    assert lunar.LUNAR not in [value for _label, value in realm.options]
    # A saved Lunar aura stays shown without the book.
    keep.aura_realm = lunar.LUNAR
    assert lunar.LUNAR in offered()["covenant"]
