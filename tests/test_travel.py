"""The Travel calculator's rules (City & Guild pp. 85-90, errata p. 57;
Definitive Edition pp. 403-404, 408) and the words of its inspector."""

import pytest

from ars_magica_manager import atlas
from ars_magica_manager.forms import travel as travel_forms
from ars_magica_manager.models import Character, Covenant, Neighbour, Saga
from ars_magica_manager.rules import journeys as tr

POUND = tr.PENCE_PER_POUND


# -- days --


@pytest.mark.parametrize(
    ("means", "miles", "days"),
    [
        ("foot", 100, (5, 5)),  # DE p. 408: 20 a day
        ("horses", 120, (5, 5)),  # C&G p. 85: about 24
        ("courier", 90, (3, 3)),  # about 30
        ("remounts", 180, (2, 2)),  # up to 90
        ("packhorse", 48, (2, 2)),
        ("cart", 100, (4, 7)),  # 15 to 25
        ("coach", 72, (3, 4)),  # 18 to 24
        ("barge_down", 100, (10, 10)),  # 8 to 10, faster downriver
        ("barge_up", 100, (13, 13)),
        ("ship", 480, (6, 8)),  # 60 to 80
        ("coast", 480, (6, 8)),
    ],
)
def test_every_means_covers_a_route_at_its_pages_speed(means, miles, days):
    journey = tr.journey(means, miles, tr.ROUTE)
    assert journey is not None
    assert journey.days == days


def test_a_direct_distance_uses_page_89s_divisors():
    assert tr.journey("cart", 120, tr.DIRECT).days == (10, 10)  # / 12
    assert tr.journey("packhorse", 120, tr.DIRECT).days == (10, 10)
    assert tr.journey("ship", 600, tr.DIRECT).days == (10, 10)  # / 60
    assert tr.journey("coast", 600, tr.DIRECT).days == (10, 10)


def test_the_errata_swaps_the_river_divisors():
    """8 with the current, 6 against (errata p. 57, correcting p. 89)."""
    down = tr.journey("barge_down", 180, tr.DIRECT)
    up = tr.journey("barge_up", 180, tr.DIRECT)
    assert down.days == (23, 23)
    assert up.days == (30, 30)
    assert "/ 8 with the current" in down.working
    assert "errata p. 57" in down.working
    assert tr.RIVER_WITH_CURRENT == 8 and tr.RIVER_AGAINST_CURRENT == 6


def test_a_direct_distance_on_foot_or_horseback_adds_the_winding_way():
    """p. 89's 20% for winding roads, then the day's miles."""
    walk = tr.journey("foot", 100, tr.DIRECT)
    assert walk.route_miles == pytest.approx(120)
    assert walk.days == (6, 6)
    assert "20%" in walk.working


def test_a_part_day_counts_as_a_day_and_nothing_needs_no_journey():
    assert tr.journey("foot", 21, tr.ROUTE).days == (2, 2)
    assert tr.journey("foot", 1, tr.ROUTE).days == (1, 1)
    assert tr.journey("foot", None) is None
    assert tr.journey("foot", 0) is None
    assert tr.journey("griffin", 50) is None


def test_hurrying_a_courier_takes_the_urgent_pace():
    """DE p. 408: about 30 a day, 50 if urgent."""
    assert tr.journey("courier", 180, tr.ROUTE).days == (6, 6)
    hurried = tr.journey("courier", 180, tr.ROUTE, quick=True)
    assert hurried.days == (4, 4)
    assert "DE p. 408" in hurried.working


def test_the_rough_guide_is_the_definitive_editions():
    assert tr.journey("ship", 600, tr.ROUTE).guide_days == 20  # about 30 a day
    assert tr.journey("cart", 100, tr.ROUTE).guide_days == 5  # 20 is very good
    assert tr.journey("barge_down", 100, tr.ROUTE).guide_days is None


# -- the Naval Trade Tables --


def test_the_tables_give_days_between_ports_directly():
    assert tr.voyage("Danzig", "Lubeck") == tr.Voyage(6, ("Danzig", "Lubeck"))
    # Kept as printed, read from the row's port to the column's.
    assert tr.voyage("Bordeaux", "Seville").days == 21
    assert tr.voyage("Seville", "Bordeaux").days == 19


def test_a_voyage_between_regions_adds_the_days_to_each_junction():
    voyage = tr.voyage("Lubeck", "Bruges")
    assert voyage is not None
    # Lubeck to the Skagarek Junction 5, then on to Bruges 9.
    assert voyage.path == ("Lubeck", "Skagarek Junction", "Bruges")
    assert voyage.days == 14


def test_a_voyage_by_the_tables_is_a_journey_by_sea():
    journey = tr.journey(None, None, tr.PORTS, start_port="Genoa", end_port="Pisa")
    assert journey.days == (1, 1)
    assert journey.fatigue is None
    assert tr.journey(None, None, tr.PORTS, start_port="Genoa") is None
    assert tr.voyage("Genoa", "Atlantis") is None
    assert "Junction" not in " ".join(tr.PORTS_LISTED)


# -- costs --


def test_a_fortnight_by_sea_costs_the_party_of_eight_a_pound():
    """Two magi and six grogs, about a ton with their food (C&G p. 85)."""
    journey = tr.journey("ship", 840, tr.ROUTE, travellers=8)
    assert journey.days == (11, 14)
    assert journey.space_tons == 1
    low, high = journey.cost_pence
    assert high == pytest.approx(POUND)
    assert low == pytest.approx(POUND * 11 / 14)


def test_hugging_the_coast_halves_the_space():
    journey = tr.journey("coast", 840, tr.DIRECT, travellers=8)
    assert journey.space_tons == 0.5
    assert journey.cost_pence[0] == pytest.approx(POUND * 0.5)


def test_river_costs_twice_sea_and_road_eight_to_twenty_times():
    river = tr.journey("barge_down", 112, tr.DIRECT, travellers=8)  # 14 days
    assert river.cost_pence == pytest.approx((2 * POUND, 2 * POUND))
    road = tr.journey("cart", 168, tr.DIRECT, travellers=8)  # 14 days
    assert road.cost_pence == pytest.approx((8 * POUND, 20 * POUND))


def test_cargo_takes_its_own_tons():
    journey = tr.journey("ship", 840, tr.DIRECT, travellers=8, cargo=2)
    assert journey.space_tons == 3
    assert journey.cost_pence[0] == pytest.approx(3 * POUND)


def test_a_known_magus_pays_double_aboard_but_not_on_the_road():
    sea = tr.journey("ship", 840, tr.DIRECT, travellers=8, cargo=1, known_magus=True)
    # The passengers' ton doubled; the cargo's ton isn't.
    assert sea.cost_pence[0] == pytest.approx(3 * POUND)
    assert sea.known_magus_doubled
    road = tr.journey("cart", 168, tr.DIRECT, travellers=8, known_magus=True)
    assert road.cost_pence == pytest.approx((8 * POUND, 20 * POUND))
    assert not road.known_magus_doubled


def test_on_foot_or_on_your_own_horses_there_is_no_figure():
    for means in ("foot", "horses", "courier", "remounts"):
        assert tr.journey(means, 100, travellers=4).cost_pence is None


# -- the forced march --


def test_each_hurried_day_costs_a_long_term_fatigue_level():
    """DE p. 408; the levels from p. 403."""
    march = tr.forced_march(3)
    assert march.levels_lost == 3
    assert march.level == "Tired"
    assert march.by_day == ((1, "Winded"), (2, "Weary"), (3, "Tired"))
    assert march.unconscious_on is None
    # One back for each night's rest without hurrying (p. 404).
    assert march.nights_to_recover == 3


def test_a_long_forced_march_ends_unconscious_on_the_fifth_day():
    march = tr.forced_march(8)
    assert march.levels_lost == 5
    assert march.level == "Unconscious"
    assert march.unconscious_on == 5
    assert march.nights_to_recover == 5


def test_only_travellers_on_land_hurry():
    assert tr.journey("cart", 100, tr.ROUTE, quick=True).fatigue.days == 7
    assert tr.journey("ship", 600, tr.ROUTE, quick=True).fatigue is None
    assert tr.journey("barge_up", 60, tr.ROUTE, quick=True).fatigue is None
    assert tr.journey("cart", 100, tr.ROUTE).fatigue is None
    # Riding remounts to death is always a forced march.
    assert tr.journey("remounts", 180).fatigue.days == 2


# -- the inspector --


def _saga() -> Saga:
    saga = Saga(id="s", name="Test")
    saga.covenants.append(Covenant(id="cov1", saga_id="s", name="Dammerstein"))
    saga.neighbours.append(Neighbour(id="cologne", name="Cologne", kind="town"))
    saga.neighbours.append(Neighbour(id="lorelei", name="The Lorelei", kind="place"))
    saga.neighbours.append(Neighbour(id="lord", name="Count Heinrich", kind="lord"))
    return saga


def test_from_and_to_offer_the_covenants_towns_and_places():
    assert travel_forms.places(_saga()) == [
        ("Dammerstein", "cov1"),
        ("Cologne", "cologne"),
        ("The Lorelei", "lorelei"),
    ]


def test_the_journey_words_the_barge():
    live = travel_forms.travel_live(_saga())
    text = live(
        {
            "start": "cov1",
            "end": "cologne",
            "measure": tr.DIRECT,
            "miles": 180,
            "means": "barge_down",
            "travellers": 8,
            "cargo": 2.0,
        }
    )
    assert "[b]Dammerstein to Cologne[/]" in text
    assert "Days: [b]23[/]" in text
    assert "river travel costs twice sea travel" in text
    assert "3 tons of space" in text
    assert "Forced march" not in text


def test_the_journey_warns_of_the_forced_march():
    live = travel_forms.travel_live(_saga())
    text = live(
        {
            "measure": tr.ROUTE,
            "miles": 300,
            "means": "foot",
            "travellers": 1,
            "quick": True,
        }
    )
    assert "[$text-error]Forced march" in text
    assert "Unconscious on day 5" in text
    assert "no figure in the book" in text


def test_the_journey_asks_for_what_it_lacks():
    live = travel_forms.travel_live(_saga())
    assert "Give the distance" in live({"measure": tr.DIRECT, "means": "foot"})
    assert "Choose two ports" in live({"measure": tr.PORTS})


def _with_travellers() -> Saga:
    saga = _saga()
    saga.current_season, saga.current_year = "Autumn", 1220
    saga.characters.append(Character(id="anna", name="Anna", type="companion"))
    saga.characters.append(Character(id="brun", name="Brun", type="grog"))
    return saga


BARGE = {
    "start": "cov1",
    "end": "cologne",
    "measure": tr.DIRECT,
    "miles": 180,
    "means": "barge_down",
    "who": ["anna", "brun"],
    "travellers": 8,
    "cargo": 2.0,
}


def test_the_form_ends_with_close_or_set_out():
    form = travel_forms.travel(_saga())
    assert (form.save_label, form.cancel_label) == ("Set Out", "Close")
    assert form.inspector == "The Journey"
    assert form.help_id == "travel"


def test_set_out_refuses_figures_below_nothing_no_one_named_or_no_distance():
    problem = travel_forms.travel_problem
    assert problem({**BARGE, "miles": -5}) == "Miles can't be below 0."
    assert problem({**BARGE, "travellers": -1}) is not None
    assert "Name who goes" in problem({**BARGE, "who": []})
    assert "distance" in problem({**BARGE, "miles": None})
    assert "ports" in problem({"measure": tr.PORTS, "who": ["anna"]})
    assert problem(BARGE) is None


def test_travellers_follows_who_goes_and_keeps_the_others():
    fields = {f.key: f for f in travel_forms.travel_fields(_with_travellers())}
    fills = fields["who"].fills
    assert fills is not None
    assert fills({"who": ["anna"], "travellers": 0}) == {"travellers": 1}
    # Five unnamed others counted, then a second named: one more.
    assert fills({"who": ["anna", "brun"], "travellers": 6}) == {"travellers": 7}
    assert fills({"who": ["anna"], "travellers": 7}) == {"travellers": 6}
    assert fills({"who": [], "travellers": 0}) == {"travellers": 0}


def test_set_out_writes_each_travellers_diary_and_the_arrival():
    saga = _with_travellers()
    told = travel_forms.travel(saga).apply(BARGE)
    for name in ("anna", "brun"):
        entry = saga.character(name).diary[-1]
        assert (entry.year, entry.season, entry.name) == (1220, "Autumn", "Travel")
        assert entry.details.startswith("From Dammerstein to Cologne, by barge")
        assert "23 days" in entry.details
        assert "about" in entry.details  # the passage's cost
    arrival = saga.calendar[-1]
    assert arrival.title == "Anna, Brun arrive at Cologne"
    # 23 days: the same season.
    assert (arrival.season, arrival.year) == ("Autumn", 1220)
    assert "Arriving Autumn 1220" in told[-1]


def test_a_forced_march_costs_each_traveller_a_level_a_day():
    saga = _with_travellers()
    values = {
        **BARGE,
        "measure": tr.ROUTE,
        "miles": 60,
        "means": "foot",
        "quick": True,
    }
    travel_forms.travel(saga).apply(values)
    for name in ("anna", "brun"):
        traveller = saga.character(name)
        assert traveller.long_term_fatigue == 3
        assert traveller.fatigue_level == "tired"
        assert "3 Long-Term Fatigue levels lost" in traveller.diary[-1].details


def test_a_long_journey_arrives_seasons_later():
    assert tr.arrival("Autumn", 1220, 90) == ("Autumn", 1220)
    assert tr.arrival("Autumn", 1220, 91) == ("Winter", 1220)
    assert tr.arrival("Winter", 1220, 200) == ("Summer", 1221)
    saga = _with_travellers()
    travel_forms.travel(saga).apply(
        {
            "measure": tr.PORTS,
            "start_port": "London",
            "end_port": "Acre",
            "who": ["anna"],
            "travellers": 1,
        }
    )
    arrival = saga.calendar[-1]
    assert arrival.title == "Anna arrives at Acre"
    assert (
        saga.character("anna")
        .diary[-1]
        .details.startswith("From London to Acre, by sea")
    )


def test_close_records_nothing():
    """Close is the form's cancel: no step runs, so the saga is as it was;
    the what-if is only the inspector's."""
    saga = _with_travellers()
    live = travel_forms.travel_live(saga)
    text = live(BARGE)
    assert "Set Out: Anna, Brun; arriving Autumn 1220" in text
    assert saga.calendar == []
    assert all(not c.diary for c in saga.characters)


def test_from_and_to_fill_the_miles_from_the_atlas():
    saga = Saga(
        "s",
        "S",
        covenants=[Covenant("cov", "s", "Durenmar")],
        neighbours=[Neighbour("town", "Basel", kind="town")],
    )
    fields = {f.key: f for f in travel_forms.travel_fields(saga, "cov")}
    fills = fields["end"].fills
    assert fills is not None
    values = {"start": "cov", "end": "town", "measure": tr.ROUTE}
    assert fills(values) == {}
    m = atlas.add_map(saga, "The Rhine", None, width=4, height=2)
    atlas.place_pin(saga, m.id, "covenants", "cov", 0.0, 0.5)
    atlas.place_pin(saga, m.id, "neighbours", "town", 0.5, 0.5)
    assert fills(values) == {}
    atlas.set_scale(m, (0.0, 1.0), (0.25, 1.0), 10, "miles")
    assert fills(values) == {"miles": 20, "measure": tr.DIRECT}
    assert fields["start"].fills is not None
