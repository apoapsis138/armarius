"""Fleet battles (Tales of Power pp. 106-110): a Battle fought at sea with
ships from the covenants' Possessions, its Weight of Numbers by ships,
its pilots' Deployment, and its events at sea."""

import json
from dataclasses import asdict

import pytest
from support import everything_saga

from ars_magica_manager import battles, fleet_battles, form_spec
from ars_magica_manager.commands import Form
from ars_magica_manager.models import (
    Ability,
    Battle,
    BattleEvent,
    BattleSide,
    Character,
    Possession,
    Saga,
    Ship,
)
from ars_magica_manager.rules import battle, fleet_battle
from ars_magica_manager.rules.xp import ability_xp


def _ship(pid: str, name: str, kind: str, crew: int, fighters: float = 0) -> Possession:
    return Possession(
        id=pid,
        kind="ship",
        name=name,
        ship=Ship(kind_name=kind, crew=crew, fighters_tons=fighters),
    )


def _fleet_saga() -> Saga:
    """Leandro's covenant keeps four ships (the large cog carrying 48
    fighting men), and Bjorn, Int +1, Profession: Sailor 6, can pilot."""
    saga = everything_saga()
    covenant = saga.covenants[0]
    covenant.possessions += [
        _ship("nebel", "Nebelkönigin", "Large cog", 18, 6),
        _ship("seehund", "Seehund", "Coastal buss", 8),
        _ship("moewe", "Möwe", "Knarr", 8),
        _ship("grauwal", "Grauwal", "Small cog", 8),
    ]
    bjorn = Character(id="bjorn", name="Bjorn Ironside", type="companion")
    bjorn.characteristics.intelligence = 1
    bjorn.abilities.append(Ability("Profession: Sailor", xp=ability_xp(6)))
    saga.characters.append(bjorn)
    saga.battles = []
    return saga


def _values(form: Form, edits: dict) -> dict:
    """The form's values as the dialog returns them: its defaults with
    `edits`, without the fields hidden for those values."""
    fields = form.fields()
    values = {f.key: f.value for f in fields} | edits
    return {f.key: values[f.key] for f in fields if form_spec.shown(f, values)}


# -- the rules --


def test_crews_make_combat_groups_of_five():
    assert [fleet_battle.crew_groups(n) for n in (0, 4, 5, 82, -3)] == [0, 0, 1, 16, 0]
    assert fleet_battle.deployment_base(1, 6) == 7
    assert fleet_battle.NAPTHA_DAMAGE == 5


def test_weight_of_numbers_counts_ships_at_sea():
    saga = _fleet_saga()
    entry = Battle(
        "Off Terschelling",
        at_sea=True,
        sides=[
            BattleSide(
                covenant_id=saga.covenants[0].id, ships=["nebel", "seehund", "moewe"]
            ),
            BattleSide("Pirates", groups=40, other_ships=2),
        ],
    )
    # 3 ships against 2: +1, though the pirates have far more groups.
    assert battles.weight(entry, saga=saga) == 1
    assert battles.weight(entry, 1, saga=saga) == -1
    assert battles.weight(entry) == battle.weight_of_numbers(0, 40)
    # A wrecked ship no longer counts.
    nebel = saga.covenants[0].possessions[-4].ship
    assert nebel is not None
    nebel.damage_lost = 99
    assert fleet_battles.ship_count(saga, entry.sides[0]) == 2
    assert battles.weight(entry, saga=saga) == 0
    assert battles.ships_text(saga, entry) == "2 v 2"
    assert battles.ships_text(saga, Battle("Werl")) == ""


# -- Edit Battle --


def test_a_fleet_battle_picks_the_covenant_s_ships_and_its_pilot():
    saga = _fleet_saga()
    form = battles.ops(saga).add()
    assert isinstance(form, Form) and form.live is not None
    covenant = saga.covenants[0]
    edits = {
        "name": "Off Terschelling",
        "fought": "sea",
        "army_0": battles.COVENANT + covenant.id,
        "name_1": "Pirates",
        "other_ships_1": 2,
        "ship_0_grauwal": False,
        "pilot_0": "bjorn",
        "bearded_0": True,
    }
    values = _values(form, edits)
    # Every ship of the linked covenant is ticked at first; none of the
    # second army's, which links no covenant.
    assert values["ship_0_nebel"] and "ship_1_nebel" not in values
    live = form.live(values)
    assert "3 ships against 2[/]: Weight of Numbers +1" in live
    assert "82 men, 16 combat groups" in live
    assert "Int +1 + Profession: Sailor 6 = 7 + stress die" in live
    assert "Bearded" in live
    assert form.validate is not None and form.validate(values) is None
    form.apply(values)
    [entry] = saga.battles
    first, second = entry.sides
    assert entry.at_sea
    assert (first.ships, first.pilot_id, first.bearded) == (
        ["nebel", "seehund", "moewe"],
        "bjorn",
        True,
    )
    # Blank groups: the crews' (66 + 8 + 8 men), and baggage for them.
    assert (first.groups, first.baggage) == (16, 2)
    assert (second.other_ships, second.ships) == (2, [])
    info = battles.info(saga, entry)
    assert ", at sea" in info
    assert "Ships: Nebelkönigin, Seehund, Möwe (82 men); pilot Bjorn Ironside" in info
    assert "Weight of Numbers +1 by ships" in info
    assert fleet_battle.SOURCE in info
    # Edit shows the fleets' inspector, the ships still ticked as saved.
    edit = battles.ops(saga).edit(0)
    assert isinstance(edit, Form) and edit.inspector == "The Fleets"
    again = _values(edit, {})
    assert again["fought"] == "sea" and not again["ship_0_grauwal"]


def test_a_fleet_battle_needs_ships_on_both_sides():
    saga = _fleet_saga()
    form = battles.ops(saga).add()
    assert isinstance(form, Form) and form.validate is not None
    values = _values(
        form,
        {
            "name": "Empty sea",
            "fought": "sea",
            "army_0": "covenant:" + saga.covenants[0].id,
        },
    )
    assert "second army has none" in (form.validate(values) or "")
    assert "fewer than none" in (form.validate(values | {"other_ships_1": -1}) or "")
    # On land the fleet's fields are hidden and nothing is asked of them.
    land = _values(form, {"name": "Werl", "fought": "land"})
    assert "pilot_0" not in land and form.validate(land) is None
    assert "Weight of Numbers" in (form.live(land) if form.live else "")


def test_a_land_battle_keeps_its_groups_and_its_form():
    saga = everything_saga()
    form = battles.ops(saga).edit(0)
    assert isinstance(form, Form) and form.inspector == "The Armies"
    values = _values(form, {})
    assert values["fought"] == "land" and "other_ships_0" not in values
    form.apply(values)
    assert not saga.battles[0].at_sea


# -- Battle Event at sea --


def _at_sea(saga: Saga) -> Battle:
    entry = Battle(
        "Off Terschelling",
        at_sea=True,
        sides=[
            BattleSide(
                covenant_id=saga.covenants[0].id,
                groups=16,
                ships=["nebel", "seehund", "moewe", "grauwal"],
            ),
            BattleSide("Pirates", groups=20, other_ships=2),
        ],
    )
    saga.battles = [entry]
    return entry


def test_an_event_at_sea_counts_only_the_ships_engaged():
    saga = _fleet_saga()
    entry = _at_sea(saga)
    form = battles.event_form(saga, entry)
    assert isinstance(form, Form)
    assert (
        form.title.startswith("Battle Event 1 at sea") and form.inspector == "The Event"
    )
    first = _values(form, {"who": "comp1"})
    # At first every ship is engaged: 4 against 2.
    assert all(first[f"eng_{p}"] for p in ("nebel", "seehund", "moewe", "grauwal"))
    assert first["eng_other_1"] == 2
    assert battles.event_of(saga, entry, first).weight == 2  # type: ignore[union-attr]
    edits = {
        "who": "comp1",
        "deed": "cut",
        "eng_moewe": False,
        "eng_grauwal": False,
        "eng_other_1": 1,
        "naptha": True,
        "size": "Outnumbered",
        "result": "won",
    }
    values = _values(form, edits)
    live = battles.event_live(saga, entry, values)
    assert "Engaged: 2 against 1: Weight of Numbers [b]+2[/]" in live
    assert "Naptha: +5 damage" in live
    assert "Engaged, Ease Factor 9" in live
    assert form.validate is not None and form.validate(values) is None
    assert "2 other ships" in (form.validate(values | {"eng_other_1": 3}) or "")
    form.apply(values)
    [event] = entry.events
    assert (event.deed, event.engaged_ships, event.engaged_other, event.naptha) == (
        "cut",
        ["nebel", "seehund"],
        [0, 1],
        True,
    )
    # Outnumbered (2) x the event's Weight of Numbers (2).
    assert (event.losses, entry.sides[1].groups) == (4, 16)
    assert "Cut off part of their fleet, with naptha bombs" in battles.info(saga, entry)
    # The next event starts from the ships engaged last time.
    second = _values(battles.event_form(saga, entry), {"who": "comp1"})  # type: ignore[arg-type]
    assert second["eng_nebel"] and not second["eng_moewe"]
    assert second["eng_other_1"] == 1


def test_an_event_on_land_asks_nothing_of_ships():
    saga = everything_saga()
    form = battles.event_form(saga, saga.battles[0])
    assert isinstance(form, Form) and form.validate is None and not form.inspector
    assert "deed" not in [f.key for f in form.fields()]


# -- saved battles --


def test_a_fleet_battle_survives_a_save_and_older_saves_load_on_land():
    saga = _fleet_saga()
    entry = _at_sea(saga)
    entry.sides[0].pilot_id = "bjorn"
    entry.events.append(
        BattleEvent(
            "comp1", deed="board", engaged_ships=["nebel"], engaged_other=[0, 2]
        )
    )
    loaded = Saga.from_dict(json.loads(json.dumps(asdict(saga))))
    again = loaded.battles[0]
    assert again.at_sea and again.sides[0].ships == entry.sides[0].ships
    assert (again.sides[1].other_ships, again.sides[0].pilot_id) == (2, "bjorn")
    assert again.events[0].engaged_other == [0, 2]
    old = Battle.from_dict({"name": "Werl", "sides": [{"groups": 3}], "events": [{}]})
    assert not old.at_sea and old.sides[0].ships == [] and old.events[0].deed == ""


@pytest.mark.parametrize(
    "side",
    [{"name": "Pirates", "other_ships": -1}, {"name": "Pirates", "ships": "nebel"}],
)
def test_a_bad_saved_side_is_reported_by_name(side: dict):
    with pytest.raises(ValueError, match="Pirates"):
        BattleSide.from_dict(side)


def test_a_bad_saved_event_count_is_reported():
    with pytest.raises(ValueError, match="other ships engaged"):
        BattleEvent.from_dict({"engaged_other": [1, "two"]})
