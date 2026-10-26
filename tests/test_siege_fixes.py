"""A mounted lance in a fight, the timing of a stockade's supplies rolls,
and the walls' fixed measure once mines lower the Defenses (DE pp.
400-401; Lords of Men pp. 111-116, 126). The dice are scripted: each test
says what each d10 shows."""

import random
from dataclasses import asdict

from ars_magica_manager import sieges, storage
from ars_magica_manager.models import (
    Ability,
    Character,
    Combatant,
    Fight,
    FightSide,
    Possession,
    Saga,
    Siege,
    SiegeEvent,
)
from ars_magica_manager.rules import combat
from ars_magica_manager.rules import fight as fight_rules
from ars_magica_manager.rules import siege as rules
from ars_magica_manager.rules.xp import ability_xp


class Scripted(random.Random):
    """A d10 that throws the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


# -- a mounted lance --

LANCE = Possession(
    id="lance",
    kind="weapon",
    name="Lance",
    gear_id="weapon_lance",
    weapon_init=2,
    weapon_attack=4,
    weapon_damage=5,
)


def _knight_fight(*, mounted: bool) -> tuple[Saga, Fight, fight_rules.Fighter]:
    knight = Character(id="k", name="Sir Konrad", type="companion")
    knight.abilities += [
        Ability("Single Weapon", xp=ability_xp(5)),
        Ability("Great Weapon", xp=ability_xp(1)),
        Ability("Ride", xp=ability_xp(2)),
    ]
    knight.inventory.append(LANCE)
    rider = Combatant(
        "Sir Konrad", "character", "k", weapon_id="lance", mounted=mounted, id="kn"
    )
    foe = Combatant("Bandit", id="bandit")
    fight = Fight(
        "Joust",
        sides=[
            FightSide("Ours", combatants=[rider]),
            FightSide("Theirs", combatants=[foe]),
        ],
    )
    saga = Saga(id="s", name="S", fights=[fight], characters=[knight])
    return saga, fight, fight_rules.Fighter(saga, rider)


def test_a_mounted_lance_fights_as_a_single_weapon():
    _, _, rider = _knight_fight(mounted=True)
    figures = rider.figures()
    assert figures.ability == 5  # Single Weapon, not Great Weapon
    assert rider.character is not None
    totals = combat.combat_totals(rider.character, LANCE, mounted_=True)
    assert totals.ability == "Single Weapon"
    assert totals.attack is not None
    assert figures.attack == int(totals.attack.total)


def test_on_foot_the_lance_is_a_long_spear():
    _, _, walker = _knight_fight(mounted=False)
    assert walker.figures().ability == 1  # Great Weapon, as a long spear


def test_ride_is_added_to_a_mounted_blow_once():
    saga, fight, rider = _knight_fight(mounted=True)
    every = fight_rules.units(saga, fight)
    me, them = every["kn"], every["bandit"]
    chances = fight_rules.odds(saga, fight, me, them, fight_rules.ATTACK)
    mounted_terms = [t for t in chances.attack if t.label == "Mounted"]
    assert [t.amount for t in mounted_terms] == [2]
    attack = chances.total("attack")
    assert attack == rider.figures().attack + 2
    assert rider.character is not None
    on_horse = combat.mounted(rider.character, LANCE)
    assert on_horse is not None and on_horse.attack == attack


def test_an_incapacitating_wound_takes_an():
    victim = fight_rules.Fighter(Saga(id="s", name="S"), Combatant("Bandit"))
    told = fight_rules._land([victim], 1, 16, scuffle=False)
    assert told == ["Bandit takes an Incapacitating Wound"]
    heavy = fight_rules.Fighter(Saga(id="s", name="S"), Combatant("Robber"))
    assert fight_rules._land([heavy], 1, 11, scuffle=False) == [
        "Robber takes a Heavy Wound"
    ]


# -- supplies rolls --


def _stockade(**kw) -> Siege:
    # 25 groups: Weight of Numbers +3, a roll against 6.
    return Siege("S", garrison=25, besieger_walls=[1, 1, 1, 0], **kw)


def test_a_failed_roll_at_standard_brings_the_next_a_week_later_not_backdated():
    castle = _stockade(days=29)
    # Events every week; the first roll is due on day 30: 3 + 2 against 6.
    told = rules.pass_interval(castle, Scripted(2))
    assert castle.days == 36
    assert told == ["Supplies roll: 5 against 6", "Supplies fall to Shoddy."]
    assert (castle.supply_rolls, castle.next_supply_day) == (1, 37)
    # The next week brings the roll of day 37, and only that one.
    told = rules.pass_interval(castle, Scripted(9))
    assert told == ["Supplies roll: 10 against 6"]
    assert (castle.supply_rolls, castle.next_supply_day) == (2, 44)


def test_failures_one_after_another_surrender_on_the_right_day():
    castle = _stockade(days=36)
    told = rules.supplies_rolls(castle, Scripted(2, 2))
    # Day 30 fails (Standard to Shoddy), day 37 hasn't come yet.
    assert castle.supplies == "Shoddy" and not castle.ended
    assert castle.supply_rolls == 1
    castle.days = 37
    told = rules.supplies_rolls(castle, Scripted(2))
    assert castle.ended == "Surrendered"
    assert castle.supply_rolls == 2
    assert told[-1] == "The supplies are gone: the castle surrenders."


def test_intervals_without_a_stockade_pass_with_no_roll_to_make_up():
    castle = Siege("S", garrison=25, days=100)
    assert rules.supplies_rolls(castle, Scripted()) == []
    assert castle.next_supply_day == 120
    castle.besieger_walls = [1, 1, 1, 0]
    castle.days = 125
    assert rules.supplies_rolls(castle, Scripted(9)) == ["Supplies roll: 12 against 6"]
    assert castle.supply_rolls == 1


# -- the walls --


def test_after_a_mine_no_wall_shows_more_than_its_whole():
    castle = Siege("S", miners=1, sapper=10, engines={"Trebuchet": 1}, gunner=20)
    assert rules.full_wall(castle) == 8  # Standard (+2) x 4 at Size +9
    rules.bombard(castle, 1, Scripted(5, 2))
    rules.undermine(castle, 0, Scripted(5, 2))
    assert castle.defenses == "Shoddy"
    assert rules.full_wall(castle) == 8
    assert rules.walls(castle) == [8, 7, 8, 8]
    assert all(n <= rules.full_wall(castle) for n in rules.walls(castle))


def test_a_mine_before_any_blow_keeps_the_walls_whole():
    castle = Siege("S", miners=1, sapper=10)
    rules.undermine(castle, 0, Scripted(5, 2))
    assert castle.defenses == "Shoddy"
    assert (castle.wall_max, rules.walls(castle)) == (8, [8, 8, 8, 8])
    # The lower Defenses show in the Defense Bonus, not the walls.
    assert rules.wall_bonus(castle, 0) == 1


def test_a_wall_at_zero_stays_at_zero_after_a_mine():
    castle = Siege("S", miners=1, sapper=10, engines={"Trebuchet": 5}, gunner=30)
    for _ in range(2):
        rules.bombard(castle, 2, Scripted(5, 2))
    assert rules.walls(castle)[2] == 0
    rules.undermine(castle, 2, Scripted(5, 2))
    assert rules.walls(castle)[2] == 0
    assert rules.wall_bonus(castle, 2) == 0


def test_seal_the_breach_restores_five_levels_up_to_the_original_whole():
    castle = Siege("S", walls=[8, 1, 8, 8], wall_max=8)
    played = rules.seal_breach(castle, 1)
    assert rules.walls(castle)[1] == 6
    assert "5 damage levels restored, 6 of 8" in played.text
    rules.seal_breach(castle, 1)
    assert rules.walls(castle)[1] == 8
    assert "no breach to seal" in rules.seal_breach(castle, 1).text


def test_seal_the_breach_is_a_siege_event():
    castle = Siege("S", walls=[8, 0, 8, 8], wall_max=8)
    saga = Saga(id="s", name="S", sieges=[castle])
    sieges.next_event(saga, castle, Scripted()).apply(
        {"event": rules.SEAL, "wall": "1"}
    )
    assert rules.walls(castle)[1] == 5
    assert castle.events[-1].kind == rules.SEAL


def test_the_edit_form_caps_a_wall_at_its_whole():
    castle = Siege("S", walls=[8, 2, 8, 8], wall_max=8)
    saga = Saga(id="s", name="S", sieges=[castle])
    form = sieges.ops(saga).edit(0)
    values = {f.key: f.value for f in form.fields() if f.kind != "info"}
    values["walls_1"] = 30
    form.apply(values)
    assert castle.walls == [8, 8, 8, 8]


# -- older saves --


def _loaded(siege: Siege) -> Siege:
    data = asdict(Saga(id="s", name="S", sieges=[siege]))
    for key in ("wall_max", "next_supply_day"):
        del data["sieges"][0][key]
    return storage._from_data(data).sieges[0]


def test_an_older_siege_gets_its_walls_measure_and_its_next_supplies_roll():
    old = Siege(
        "S",
        defenses="Shoddy",
        walls=[8, 3, 8, 8],
        supplies="Standard",
        days=40,
        supply_rolls=1,
        events=[SiegeEvent(40, rules.UNDERMINE, "A mine")],
    )
    loaded = _loaded(old)
    # A mine took Standard to Shoddy (+1, 4 levels): the walls kept 8.
    assert loaded.wall_max == 8
    assert loaded.next_supply_day == 60


def test_an_older_siege_with_intervals_unrolled_is_due_after_today():
    loaded = _loaded(Siege("S", days=100, events=[SiegeEvent(100, "x", "x")]))
    assert loaded.next_supply_day == 120
    assert loaded.wall_max == 8


def test_a_siege_not_yet_begun_keeps_its_measure_open():
    loaded = _loaded(Siege("S"))
    assert (loaded.wall_max, loaded.next_supply_day) == (None, None)
    loaded.defenses = "Excellent"
    assert rules.full_wall(loaded) == 16
