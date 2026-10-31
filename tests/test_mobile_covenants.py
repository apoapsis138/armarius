"""A covenant on the move: its stop in force, the aura that follows it,
travelling Places, the Aegis left behind, Advance Season's question, the
route, and a ship apart from the fleet."""

import dataclasses

import pytest

from ars_magica_manager import (
    actions,
    book_packs,
    mobile_covenants,
    packs,
    places,
    transfer,
)
from ars_magica_manager import ships as ship_text
from ars_magica_manager.commands import Confirm, Form, Refuse
from ars_magica_manager.forms import advance
from ars_magica_manager.forms import covenant as covenant_forms
from ars_magica_manager.forms import ships as ship_forms
from ars_magica_manager.models import (
    Character,
    Covenant,
    CovenantStop,
    Laboratory,
    Neighbour,
    Possession,
    RouteStop,
    Saga,
    VirtueFlawInstance,
)
from ars_magica_manager.models.ships import Ship
from ars_magica_manager.rules import lab as lab_rules
from ars_magica_manager.rules import mobile, realms, sites


def _place(id_: str, aura: int = 0, realm: str = "Magic", **details) -> Neighbour:
    return Neighbour(
        id_, id_.title(), kind="place", realm=realm, details={"aura": aura, **details}
    )


def _saga(**covenant) -> Saga:
    saga = Saga(id="s", name="Test", current_year=1220, current_season="Spring")
    saga.covenants.append(Covenant(id="c", saga_id="s", name="Fleet", **covenant))
    saga.neighbours += [
        _place("sea"),
        _place("isle", 3),
        _place("port", 4, "Divine", waters=mobile.PORT),
        _place("cove", 1, waters=mobile.ANCHORAGE),
    ]
    return saga


def _with_ships(saga: Saga) -> Covenant:
    covenant = saga.covenants[0]
    covenant.possessions.append(Possession("ship", "ship", "Cog", ship=Ship()))
    return covenant


# -- the stop in force --


def test_the_latest_stop_not_after_the_date_is_in_force():
    stops = [
        CovenantStop(1219, "Winter", "sea"),
        CovenantStop(1220, "Summer", "isle"),
        CovenantStop(1220, "Spring", "cove"),
    ]
    assert mobile.stop_in_force(stops, 1220, "Spring").place_id == "cove"
    assert mobile.stop_in_force(stops, 1220, "Autumn").place_id == "isle"
    assert mobile.stop_in_force(stops, 1219, "Autumn") is None


def test_a_covenant_with_no_stops_is_unchanged():
    saga = _saga(place_id="isle")
    covenant = saga.covenants[0]
    places.sync(saga)
    assert sites.covenant_place(saga, covenant)[0].id == "isle"
    assert covenant.aura == 3


def test_the_aura_comes_from_the_stop_and_the_typed_one_comes_back():
    saga = _saga(aura=2)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "port"))
    places.sync(saga)
    assert (covenant.aura, covenant.aura_realm) == (4, "Divine")
    covenant.stops.clear()
    places.sync(saga)
    assert (covenant.aura, covenant.aura_realm) == (2, "Magic")


def test_the_home_stays_while_a_stop_is_in_force():
    saga = _saga(place_id="isle")
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    places.sync(saga)
    assert covenant.place_id == "isle" and covenant.aura == 0
    assert [c.id for c in sites.covenants_at(saga, saga.neighbour("sea"))] == ["c"]
    assert not sites.covenants_at(saga, saga.neighbour("isle"))
    assert "Home" in mobile_covenants.summary_text(saga, covenant)


def test_a_stop_at_a_place_deleted_goes_with_it():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    covenant.route.append(RouteStop("sea"))
    saga.neighbours = [n for n in saga.neighbours if n.id != "sea"]
    places.sync(saga)
    assert not covenant.stops and not covenant.route


def test_stops_survive_a_save():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea", 0, "Fog"))
    covenant.route.append(RouteStop("isle", 0, 2))
    saved = Covenant.from_dict(dataclasses.asdict(covenant))
    assert saved.stops == covenant.stops and saved.route == covenant.route


def test_older_saves_load_with_no_stops():
    saved = dataclasses.asdict(_saga().covenants[0])
    for key in ("stops", "route", "route_at", "circuit"):
        del saved[key]
    assert Covenant.from_dict(saved).stops == []


def test_a_bad_stop_in_a_file_is_named():
    with pytest.raises(ValueError, match="Fleet"):
        Covenant.from_dict(
            {"id": "c", "saga_id": "s", "name": "Fleet", "stops": [{"year": "soon"}]}
        )


# -- travelling Places --


def _travelling(saga: Saga, aura: int = 2) -> Neighbour:
    ship = _place("ship", aura, travels_with="c")
    ship.details["levels"] = [{"name": "Hold", "realm": "Magic", "aura": 3}]
    saga.neighbours.append(ship)
    covenant = saga.covenants[0]
    covenant.place_id = "ship"
    return ship


@pytest.mark.parametrize(
    "stop, aura, realm",
    [
        ("sea", 2, "Magic"),  # its own beats none
        ("port", 4, "Divine"),  # a stronger port holds sway
        ("cove", 2, "Magic"),
    ],
)
def test_the_stronger_aura_holds_sway_on_a_travelling_place(stop, aura, realm):
    saga = _saga()
    ship = _travelling(saga)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", stop))
    places.sync(saga)
    assert ship.place_id == stop
    assert (covenant.aura, covenant.aura_realm) == (aura, realm)


def test_a_tie_keeps_its_own():
    saga = _saga()
    _travelling(saga, 4)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "port"))
    places.sync(saga)
    assert (covenant.aura, covenant.aura_realm) == (4, "Magic")


def test_inside_its_regio_only_the_regio_counts():
    saga = _saga()
    ship = _travelling(saga)
    saga.covenants[0].stops.append(CovenantStop(1220, "Spring", "port"))
    places.sync(saga)
    lab = Laboratory(
        id="l", name="Hold", covenant_id="c", place_id="ship", place_level=1
    )
    saga.laboratories.append(lab)
    assert lab_rules.lab_aura(saga, lab) == (3, "Magic")
    assert sites.aura_here(saga, ship, 1) == (3, "Magic")


def test_a_fixed_place_inside_another_keeps_its_own_aura():
    saga = _saga()
    inner = _place("glade", 1)
    inner.place_id = "port"
    saga.neighbours.append(inner)
    assert sites.aura_here(saga, inner) == (1, "Magic")


def test_a_place_can_be_made_of_a_typed_aura():
    saga = _saga(aura=2)
    covenant = saga.covenants[0]
    form = mobile_covenants.add_stop(saga, covenant)
    form.apply(
        {
            "year": 1220,
            "season": "Spring",
            "where": "isle",
            "note": "",
            "carries": True,
        }
    )
    own = sites.place(saga, covenant.place_id)
    assert sites.travels(own) and own.details["aura"] == 2
    assert own.place_id == "isle" and covenant.aura == 3


# -- the Aegis --


def test_a_recorded_move_drops_the_aegis_with_a_diary_entry():
    saga = _saga(aegis_of_the_hearth=25, aegis_penetration=5, place_id="isle")
    covenant = saga.covenants[0]
    mobile_covenants.add_stop(saga, covenant).apply(
        {"year": 1220, "season": "Spring", "where": "sea", "note": ""}
    )
    assert covenant.aegis_of_the_hearth == 0 and covenant.aegis_penetration == 0
    entry = covenant.diary[-1]
    assert entry.category == "Defence & Magic" and "25" in entry.details


def test_a_stop_where_it_already_is_keeps_the_aegis():
    saga = _saga(aegis_of_the_hearth=25, place_id="isle")
    covenant = saga.covenants[0]
    mobile_covenants.add_stop(saga, covenant).apply(
        {"year": 1220, "season": "Spring", "where": "isle", "note": ""}
    )
    assert covenant.aegis_of_the_hearth == 25


def test_a_past_stop_logged_late_keeps_the_aegis():
    saga = _saga(aegis_of_the_hearth=25)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    mobile_covenants.add_stop(saga, covenant).apply(
        {"year": 1219, "season": "Summer", "where": "sea", "note": ""}
    )
    assert covenant.aegis_of_the_hearth == 25
    assert covenant.stops[0].place_id == "sea"


@pytest.mark.parametrize(
    "where, refused", [("port", False), ("cove", True), ("sea", True)]
)
def test_a_ship_covenant_holds_an_aegis_only_at_a_port(where, refused):
    saga = _saga()
    covenant = _with_ships(saga)
    covenant.stops.append(CovenantStop(1220, "Spring", where))
    problem = mobile_covenants.aegis_problem(
        saga, covenant, {"aegis_of_the_hearth": 20}
    )
    assert bool(problem) is refused


def test_a_land_covenant_can_cast_at_any_stop():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "cove"))
    assert not mobile_covenants.aegis_problem(
        saga, covenant, {"aegis_of_the_hearth": 20}
    )


def test_edit_covenant_refuses_an_aegis_at_anchor():
    saga = _saga()
    covenant = _with_ships(saga)
    covenant.stops.append(CovenantStop(1220, "Spring", "cove"))
    form = covenant_forms.covenant_form(saga, covenant)
    assert "anchor" in form.validate({"aegis_of_the_hearth": 20, "name": "Fleet"})


# -- the route --


def test_a_circuit_goes_round():
    covenant = Covenant(
        id="c",
        saga_id="s",
        name="C",
        route=[RouteStop("a"), RouteStop("b")],
        circuit=True,
    )
    seen = []
    for _ in range(4):
        seen.append(mobile.next_leg(covenant).place_id)
        mobile.step_route(covenant)
    assert seen == ["a", "b", "a", "b"]


def test_a_route_that_is_no_circuit_ends():
    covenant = Covenant(
        id="c", saga_id="s", name="C", route=[RouteStop("a")], circuit=False
    )
    mobile.step_route(covenant)
    assert mobile.next_leg(covenant) is None


def test_plan_route_saves_the_legs_and_circuit():
    saga = _saga()
    covenant = saga.covenants[0]
    form = mobile_covenants.plan_route(saga, covenant)
    form.apply(
        {
            "circuit": True,
            "leg_0": "sea",
            "seasons_0": 2,
            "leg_1": None,
            "leg_2": "isle",
            "seasons_2": 1,
        }
    )
    assert covenant.route == [RouteStop("sea", 0, 2), RouteStop("isle", 0, 1)]
    assert covenant.circuit
    assert "round again" in mobile_covenants.route_text(saga, covenant)


# -- Advance Season --


def _answered(saga: Saga, values: dict) -> tuple:
    """The Moves Advance Season's question gives for `values`."""
    held: list = []
    step = mobile_covenants.season_step(saga, held.append)
    assert isinstance(step, Form)
    step.apply(values)
    return held[0]


def _next_season(saga: Saga) -> None:
    saga.current_season = "Summer"


def test_only_a_covenant_on_the_move_is_asked():
    saga = _saga()
    assert mobile_covenants.asked(saga) == []
    saga.covenants[0].stops.append(CovenantStop(1220, "Spring", "sea"))
    assert [a.covenant.id for a in mobile_covenants.asked(saga)] == ["c"]


def test_a_sketch_covenant_is_not_asked():
    saga = _saga(played=False)
    saga.covenants[0].stops.append(CovenantStop(1220, "Spring", "sea"))
    assert mobile_covenants.asked(saga) == []


def test_a_stop_already_logged_for_next_season_is_not_asked_again():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops += [
        CovenantStop(1220, "Spring", "sea"),
        CovenantStop(1220, "Summer", "isle"),
    ]
    assert mobile_covenants.asked(saga) == []


def test_move_on_logs_the_next_leg_and_steps_the_route():
    saga = _saga(aegis_of_the_hearth=15)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    covenant.route = [RouteStop("isle"), RouteStop("cove")]
    moves = _answered(saga, {"what_0": mobile_covenants.MOVE_ON})
    _next_season(saga)
    mobile_covenants.log_moves(saga, moves)
    assert covenant.stops[-1] == CovenantStop(1220, "Summer", "isle")
    assert covenant.route_at == 1 and covenant.aura == 3
    assert covenant.aegis_of_the_hearth == 0


def test_stay_logs_a_stop_at_the_same_place_and_keeps_the_aegis():
    saga = _saga(aegis_of_the_hearth=15)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    moves = _answered(saga, {"what_0": mobile_covenants.STAY})
    _next_season(saga)
    mobile_covenants.log_moves(saga, moves)
    assert covenant.stops[-1] == CovenantStop(1220, "Summer", "isle")
    assert covenant.aegis_of_the_hearth == 15


def test_a_fleet_that_stays_at_anchor_loses_its_aegis():
    saga = _saga(aegis_of_the_hearth=15)
    covenant = _with_ships(saga)
    covenant.stops.append(CovenantStop(1220, "Spring", "cove"))
    moves = _answered(saga, {"what_0": mobile_covenants.STAY})
    _next_season(saga)
    mobile_covenants.log_moves(saga, moves)
    assert covenant.aegis_of_the_hearth == 0


def test_elsewhere_logs_the_place_named():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    moves = _answered(saga, {"what_0": mobile_covenants.ELSEWHERE, "where_0": "cove"})
    _next_season(saga)
    mobile_covenants.log_moves(saga, moves)
    assert covenant.stops[-1].place_id == "cove"


def test_elsewhere_needs_a_place():
    saga = _saga()
    saga.covenants[0].stops.append(CovenantStop(1220, "Spring", "sea"))
    step = mobile_covenants.season_step(saga, lambda _moves: None)
    assert "Choose where" in step.validate({"what_0": mobile_covenants.ELSEWHERE})


def test_the_question_stays_until_its_planned_seasons_are_up():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    covenant.route = [RouteStop("sea", 0, 2), RouteStop("isle")]
    covenant.route_at = 1
    entry = mobile_covenants.Asked(covenant)
    answers = mobile_covenants._answers(saga, entry)
    assert mobile_covenants._default(saga, entry, answers) == mobile_covenants.STAY
    covenant.stops.insert(0, CovenantStop(1219, "Winter", "sea"))
    assert mobile_covenants._default(saga, entry, answers) == mobile_covenants.MOVE_ON


def test_advance_season_ends_with_the_question_and_logs_the_answer():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    step = advance.play_season(saga)
    assert step.title == mobile_covenants.ASK_TITLE
    played = step.apply({"what_0": mobile_covenants.ELSEWHERE, "where_0": "isle"})
    assert isinstance(played, advance.Played)
    assert saga.current_season == "Summer"
    assert covenant.stops[-1] == CovenantStop(1220, "Summer", "isle")
    assert covenant.aura == 3


def test_a_stop_planned_ahead_comes_in_with_its_season():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Summer", "isle"))
    places.sync(saga)
    assert covenant.aura == 0
    saga.current_season = "Summer"
    mobile_covenants.log_moves(saga, ())
    assert covenant.aura == 3


# -- what the section says --


def test_the_section_shows_with_a_stop_or_a_mobile_hook():
    saga = _saga()
    covenant = saga.covenants[0]
    assert not mobile_covenants.shows(covenant)
    covenant.what_matters = "Hook: Constantly Mobile (a train of wagons)"
    assert mobile_covenants.shows(covenant)
    covenant.what_matters = ""
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    assert mobile_covenants.shows(covenant)


def test_vis_is_named_in_its_season_with_where_it_lies():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.possessions += [
        Possession(
            "egg",
            "vis_source",
            "The Kraken's Egg",
            season="Spring",
            location="off La Rochelle",
        ),
        Possession("fog", "vis_source", "Summer Fog", season="Summer"),
    ]
    words = mobile_covenants.vis_this_season(saga, covenant)
    assert "off La Rochelle" in words and "Fog" not in words


def test_a_fleet_lists_marked_places_first_and_warns_of_others():
    saga = _saga()
    covenant = _with_ships(saga)
    options = [value for _, value in mobile_covenants._choices(saga, covenant)]
    assert set(options[:2]) == {"port", "cove"}
    live = mobile_covenants.stop_live(saga, covenant)
    assert "marked" in live({"where": "isle"})
    assert "marked" not in live({"where": "port"})


def test_two_stops_may_not_share_a_season():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    problem = mobile_covenants.stop_problem(covenant.stops, None)
    assert "already" in problem({"year": 1220, "season": "Spring", "where": "isle"})


# -- a ship apart --


def _fleet() -> tuple[Saga, Covenant, Laboratory, Character]:
    saga = _saga()
    covenant = _with_ships(saga)
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    lab = Laboratory(id="lab", name="Aboard", covenant_id="c")
    magus = Character(id="m", name="Carles", type="magus", covenant_id="c")
    magus.assigned_lab_id = "lab"
    saga.laboratories.append(lab)
    saga.characters.append(magus)
    covenant.possessions[0].lab_id = "lab"
    places.sync(saga)
    return saga, covenant, lab, magus


def test_a_detached_ship_takes_her_lab_and_magus_to_her_stop():
    saga, covenant, lab, magus = _fleet()
    form = mobile_covenants.detach_form(saga, covenant, 0)
    keys = {f.key for f in form.fields()}
    assert "goes_m" in keys
    form.apply({"where": "isle", "note": "", "goes_m": True})
    assert lab_rules.lab_aura(saga, lab) == (3, "Magic")
    assert realms.home_aura(saga, magus) == (3, "Magic")
    assert sites.character_place(saga, magus)[0].id == "isle"
    assert covenant.aura == 0


def test_a_magus_who_stays_keeps_the_fleets_aura():
    saga, covenant, lab, magus = _fleet()
    form = mobile_covenants.detach_form(saga, covenant, 0)
    form.apply({"where": "isle", "note": "", "goes_m": False})
    assert realms.home_aura(saga, magus) == (0, "Magic")
    assert lab_rules.lab_aura(saga, lab) == (3, "Magic")


def test_detach_defaults_to_going_with_her():
    saga, covenant, _lab, _magus = _fleet()
    form = mobile_covenants.detach_form(saga, covenant, 0)
    assert next(f for f in form.fields() if f.key == "goes_m").value is True


def test_rejoin_ends_her_stops():
    saga, covenant, lab, _magus = _fleet()
    mobile_covenants.detach_form(saga, covenant, 0).apply(
        {"where": "isle", "note": "", "goes_m": True}
    )
    step = mobile_covenants.rejoin_form(saga, covenant, 0)
    assert isinstance(step, Confirm)
    step.apply()
    ship = covenant.possessions[0].ship
    assert not ship.stops and not ship.aboard
    assert lab_rules.lab_aura(saga, lab) == (0, "Magic")
    assert "rejoined" in covenant.diary[-1].details


def test_a_ship_can_only_detach_once_and_rejoin_when_apart():
    saga, covenant, _lab, _magus = _fleet()
    assert isinstance(mobile_covenants.rejoin_form(saga, covenant, 0), Refuse)
    covenant.possessions[0].ship.stops.append(CovenantStop(1220, "Spring", "isle"))
    assert isinstance(mobile_covenants.detach_form(saga, covenant, 0), Refuse)


def test_a_sunk_ship_cant_detach():
    _s, covenant, _l, _m = _fleet()
    covenant.possessions[0].ship.fate = "Sunk"
    assert not mobile_covenants.can_detach(covenant, 0)


def test_the_season_asks_about_each_detached_ship():
    saga, covenant, _lab, _magus = _fleet()
    mobile_covenants.detach_form(saga, covenant, 0).apply(
        {"where": "isle", "note": "", "goes_m": True}
    )
    found = mobile_covenants.asked(saga)
    assert [(a.covenant.id, a.record is not None) for a in found] == [
        ("c", False),
        ("c", True),
    ]
    moves = _answered(
        saga,
        {
            "what_0": mobile_covenants.STAY,
            "what_1": mobile_covenants.ELSEWHERE,
            "where_1": "cove",
        },
    )
    _next_season(saga)
    mobile_covenants.log_moves(saga, moves)
    assert covenant.possessions[0].ship.stops[-1].place_id == "cove"


def test_editing_a_ship_keeps_her_stops_and_sets_her_lab():
    saga, covenant, _lab, _magus = _fleet()
    record = covenant.possessions[0]
    record.ship.stops.append(CovenantStop(1220, "Spring", "isle"))
    record.ship.aboard.append("m")
    values = {f.key: f.value for f in ship_forms.ship_fields(saga, covenant, record)}
    values["lab_id"] = None
    ship_forms.save_ship(covenant, record, values)
    assert record.lab_id is None
    assert record.ship.stops and record.ship.aboard == ["m"]


def test_a_pack_keeps_the_stops_route_and_ship_through_an_import():
    saga, covenant, _lab, magus = _fleet()
    covenant.route.append(RouteStop("isle"))
    saga.neighbours.append(_place("deck", 2, travels_with="c"))
    record = covenant.possessions[0]
    record.ship.stops.append(CovenantStop(1220, "Spring", "cove"))
    record.ship.aboard.append(magus.id)
    data = packs.pack_data(saga, "Fleet", [], [covenant], [])
    target = Saga(id="t", name="New", current_year=1220, current_season="Spring")
    transfer.apply(target, transfer.plan_import(target, data))
    fleet = target.covenants[0]
    assert sites.place(target, fleet.stops[0].place_id).name == "Sea"
    assert sites.place(target, fleet.route[0].place_id).name == "Isle"
    assert [p.name for p in sites.travelling_places(target, fleet)] == ["Deck"]
    ship = fleet.possessions[0].ship
    assert sites.place(target, ship.stops[0].place_id).name == "Cove"
    assert ship.aboard == [target.characters[0].id]


def test_an_import_keeps_a_ship_whose_laboratory_stays_behind():
    saga, covenant, _lab, _magus = _fleet()
    data = packs.pack_data(saga, "Fleet", [], [covenant], [], with_characters=False)
    target = Saga(id="t", name="New", current_year=1220, current_season="Spring")
    transfer.apply(target, transfer.plan_import(target, data))
    held = target.covenants[0].possessions
    assert [p.name for p in held] == ["Cog"] and held[0].lab_id is None


def test_a_pack_takes_the_places_on_a_route():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "sea"))
    covenant.route.append(RouteStop("isle"))
    _taken, found = packs.contents(saga, [], [covenant])
    assert {"sea", "isle"} <= {n.id for n in found}


# -- the actions --


def test_the_more_items_are_offered_where_they_belong():
    assert actions.MORE_SECTIONS["plan_route"] == mobile_covenants.WHEREABOUTS_SECTION
    assert actions.SECTION_VERBS[mobile_covenants.WHEREABOUTS_SECTION] == frozenset(
        {"add", "edit", "remove"}
    )


# -- the packs --


def test_the_northern_seas_open_at_sea_with_no_aura():
    saga = book_packs.PACKS["normandy"].assemble(("TtA",)).saga
    fleet = next(c for c in saga.covenants if c.name == "The Northern Seas")
    stop = fleet.stops[0]
    sea = sites.place(saga, stop.place_id)
    assert sea.name == "The Northern Seas" and sites.aura_at(sea) == (0, "Magic")
    assert sites.waters_of(sea) == mobile.OPEN_WATER
    assert not fleet.route
    harbour = next(n for n in saga.neighbours if n.name == "The harbour of Barfleur")
    assert sites.waters_of(harbour) == mobile.PORT


def test_favonius_sails_in_travelling_places():
    saga = book_packs.PACKS["theban"].build()
    favonius = next(c for c in saga.covenants if c.name == "Favonius")
    ships = {p.name for p in sites.travelling_places(saga, favonius)}
    assert {"The Philomela", "The Tereus"} <= ships
    assert favonius.aura == 2 and mobile.has_mobile_hook(favonius)
    assert not favonius.stops and not favonius.route
    assert any(
        n.name == "The harbour of Andros" and sites.waters_of(n) == mobile.PORT
        for n in saga.neighbours
    )


def _asked(saga: Saga):
    return mobile_covenants.Asked(saga.covenants[0])


def test_where_next_never_offers_the_place_it_is_at():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    covenant.route = [RouteStop("isle"), RouteStop("cove")]
    answers = mobile_covenants._answers(saga, _asked(saga))
    assert answers[0] == ("Move on to Cove", mobile_covenants.MOVE_ON)
    assert "Isle" not in answers[0][0]


def test_moving_on_from_the_first_leg_goes_to_the_second_and_steps_past_both():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    covenant.route = [
        RouteStop("isle"),
        RouteStop("cove"),
        RouteStop("sea"),
    ]
    mobile_covenants._log_covenant(saga, _asked(saga), mobile_covenants.MOVE_ON, None)
    assert covenant.stops[-1].place_id == "cove" and covenant.route_at == 2


def test_a_route_of_only_the_place_it_is_at_offers_no_move():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    covenant.route, covenant.circuit = [RouteStop("isle")], True
    values = [v for _, v in mobile_covenants._answers(saga, _asked(saga))]
    assert mobile_covenants.MOVE_ON not in values and mobile_covenants.STAY in values


def test_the_first_leg_is_stayed_at_for_its_planned_seasons():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    covenant.route = [RouteStop("isle", seasons=2), RouteStop("cove")]
    assert not mobile_covenants._due_to_move(saga, covenant)
    covenant.stops.insert(0, CovenantStop(1219, "Winter", "isle"))
    assert mobile_covenants._due_to_move(saga, covenant)


def test_the_route_marks_the_next_leg_that_is_a_move():
    saga = _saga()
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    covenant.route = [RouteStop("isle"), RouteStop("cove")]
    assert "[b]Cove[/]" in mobile_covenants.route_text(saga, covenant)


def test_whereabouts_shows_the_aura_in_effect_with_boons_and_a_travelling_place():
    saga = _saga(place_id="deck")
    covenant = saga.covenants[0]
    saga.neighbours.append(_place("deck", 2, travels_with="c"))
    covenant.stops += [
        CovenantStop(1219, "Winter", "cove"),
        CovenantStop(1220, "Spring", "isle"),
    ]
    places.sync(saga)
    auras = [row[2] for row in mobile_covenants.grid(saga, covenant).rows]
    assert auras == ["Magic 3", "Magic 2"]
    assert realms.aura_of(covenant) == (3, "Magic")
    assert mobile_covenants.where_now(saga, covenant).endswith("Magic 3")


def test_whereabouts_keeps_a_covenants_own_regio_aura_at_every_stop():
    saga = _saga(place_id="deck", place_level=1)
    covenant = saga.covenants[0]
    saga.neighbours.append(
        _place("deck", 2, travels_with="c", levels=[{"aura": 3, "realm": "Magic"}])
    )
    covenant.stops.append(CovenantStop(1220, "Spring", "port"))
    places.sync(saga)
    assert mobile_covenants.grid(saga, covenant).rows[0][2] == "Magic 3"


def test_a_ship_apart_says_so_on_her_card_and_row():
    saga = _saga()
    covenant = _with_ships(saga)
    record = covenant.possessions[0]
    assert ship_text.card(record, saga).apart == ""
    assert ship_text.APART not in ship_text.row_label(record, saga)
    record.ship.stops.append(CovenantStop(1220, "Spring", "isle"))
    saga.characters.append(
        Character(id="m", name="Cassius", type="magus", covenant_id="c")
    )
    record.ship.aboard.append("m")
    assert ship_text.card(record, saga).apart == (
        "Apart from the fleet: at Isle, Magic 3; aboard: Cassius"
    )
    assert ship_text.APART in ship_text.row_label(record, saga)


def test_a_stop_logged_ahead_leaves_the_aegis_behind_when_it_comes_due():
    saga = _saga(place_id="isle", aegis_of_the_hearth=15)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Summer", "cove"))
    saga.current_season = "Summer"
    lines = mobile_covenants.log_moves(saga, ())
    assert covenant.aegis_of_the_hearth == 0
    assert "left behind" in lines[0] and covenant.diary[-1].category


def test_a_stop_logged_ahead_at_the_same_place_keeps_the_aegis():
    saga = _saga(place_id="port", aegis_of_the_hearth=15)
    covenant = saga.covenants[0]
    covenant.stops.append(CovenantStop(1220, "Summer", "port"))
    saga.current_season = "Summer"
    assert mobile_covenants.log_moves(saga, ()) == []
    assert covenant.aegis_of_the_hearth == 15


def _aura_boons(covenant: Covenant) -> None:
    covenant.boons_hooks = [
        VirtueFlawInstance(mobile_covenants.AURA_BOON, {"detail": "site"}),
        VirtueFlawInstance(mobile_covenants.AURA_BOON, {"detail": "site"}),
        VirtueFlawInstance("covbh_hook_major_constantly_mobile", {}),
    ]


def test_aura_boons_stay_at_home_without_an_anchor():
    saga = _saga(place_id="home")
    saga.neighbours.append(_place("home", 3))
    covenant = saga.covenants[0]
    _aura_boons(covenant)
    places.sync(saga)
    assert realms.aura_of(covenant) == (5, "Magic")
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    places.sync(saga)
    assert realms.aura_of(covenant) == (3, "Magic")
    assert not covenant.aura_boons_apply
    assert "Aura Boon isn't reaching" in mobile_covenants.summary_text(saga, covenant)


def test_aura_boons_raise_a_travelling_anchor_against_the_aura_around_it():
    saga = _saga(place_id="deck")
    saga.neighbours.append(_place("deck", 2, travels_with="c"))
    covenant = saga.covenants[0]
    _aura_boons(covenant)
    covenant.stops.append(CovenantStop(1220, "Spring", "isle"))
    places.sync(saga)
    assert realms.aura_of(covenant) == (4, "Magic")
    assert mobile_covenants.grid(saga, covenant).rows[0][2] == "Magic 4"
    assert "Aura Boon" not in mobile_covenants.summary_text(saga, covenant)
