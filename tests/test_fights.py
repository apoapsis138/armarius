"""Fights played blow by blow (rules.fight, fights.py): Initiative, a
blow's wound onto a character's sheet, a group's blows spread over the
other group, a group splitting when its vanguard falls, scuffles, special
effects, disengaging, Next Round ending a fight, the Diaries it writes and
Restart. The dice are scripted: each test says what each d10 shows."""

import random

from ars_magica_manager import fights
from ars_magica_manager.models import (
    CREATURE_FIGHTER,
    Ability,
    ArtScore,
    Character,
    Characteristics,
    Combatant,
    Covenant,
    Fight,
    FightGroup,
    FightSide,
    Possession,
    Saga,
)
from ars_magica_manager.rules import fight as rules
from ars_magica_manager.rules.xp import ability_xp


class Scripted(random.Random):
    """A d10 that throws the faces given, in order (then 5s)."""

    def __init__(self, *faces: int) -> None:
        super().__init__(0)
        self.faces = list(faces)

    def randrange(self, *args, **kwargs):  # type: ignore[override]
        return self.faces.pop(0) if self.faces else 5


def typed(name: str, **figures: int) -> Combatant:
    return Combatant(name, id=name.lower().replace(" ", "-"), **figures)


def fight_of(first: list[Combatant], second: list[Combatant], **kw) -> Fight:
    return Fight(
        "Test fray",
        sides=[
            FightSide("Ours", combatants=first, **kw),
            FightSide("Theirs", combatants=second),
        ],
    )


def saga_with(*fighting: Fight, characters=(), covenants=()) -> Saga:
    return Saga(
        id="s",
        name="S",
        fights=list(fighting),
        characters=list(characters),
        covenants=list(covenants),
    )


def test_initiative_is_rolled_once_and_the_highest_acts_first():
    fight = fight_of([typed("Slow", init=0)], [typed("Quick", init=10)])
    saga = saga_with(fight)
    rules.roll_initiative(saga, fight, Scripted(5, 2))
    assert fight.order == ["quick", "slow"]
    assert fight.initiative == {"slow": 5, "quick": 12}
    assert (fight.round, fight.turn) == (1, 0)


def test_a_hit_writes_its_wound_onto_the_characters_sheet():
    grog = Character(id="g1", name="Hugo", type="grog")
    fight = fight_of(
        [Combatant("Hugo", "character", "g1", id="hugo")],
        [typed("Bandit", init=5, attack=3, damage=0)],
    )
    saga = saga_with(fight, characters=[grog])
    # Initiative 2 and 5; the bandit's Attack 3 + 5 against Hugo's 0 + 2.
    played = rules.play(saga, fight, rules.Blow(), Scripted(2, 5, 5, 2))
    w = grog.wounds
    assert w.light + w.medium + w.heavy == 1
    assert "Hugo takes a" in played.text


def test_a_groups_blows_spread_with_the_vanguard_taking_most():
    attackers = [typed(f"A{n}", attack=5, damage=0, defence=0) for n in (1, 2, 3)]
    defenders = [typed(f"D{n}", defence=0, soak=0) for n in (1, 2)]
    fight = fight_of(attackers, defenders)
    fight.sides[0].groups = [FightGroup("Pack", [c.id for c in attackers], id="pack")]
    fight.sides[1].groups = [FightGroup("Pair", [c.id for c in defenders], id="pair")]
    saga = saga_with(fight)
    # Initiative 5 and 2; Attack 5 + 2 against Defence 0 + 2: 5 through, Light.
    rules.play(saga, fight, rules.Blow(), Scripted(5, 2, 2, 2))
    assert [d.wounds.light for d in defenders] == [2, 1]


def test_a_group_splits_when_its_vanguard_falls():
    defenders = [typed("D1"), typed("D2")]
    fight = fight_of([typed("Giant", attack=30, damage=30)], defenders)
    fight.sides[1].groups = [FightGroup("Pair", ["d1", "d2"], id="pair")]
    saga = saga_with(fight)
    rules.play(saga, fight, rules.Blow(), Scripted(5, 2, 2, 2))
    assert defenders[0].wounds.dead
    assert fight.sides[1].groups == []
    assert "d2" in fight.order and "pair" not in fight.order


def test_a_scuffle_takes_fatigue_instead_of_a_wound():
    target = typed("Drunk", soak=0)
    fight = fight_of([typed("Watchman", attack=5, damage=0)], [target])
    saga = saga_with(fight)
    played = rules.play(saga, fight, rules.Blow(rules.SCUFFLE), Scripted(5, 2, 2, 2))
    assert target.fatigue_level == "winded"
    assert target.wounds.light == 0
    assert "Fatigue level" in played.text


def test_a_special_effect_needs_its_attack_advantage_and_deals_no_damage():
    target = typed("Duellist", soak=0)
    fight = fight_of([typed("Master", attack=20, damage=10)], [target])
    saga = saga_with(fight)
    played = rules.play(saga, fight, rules.Blow("Disarm"), Scripted(5, 2, 2, 2))
    assert played.text.endswith("done.")
    assert target.wounds.light + target.wounds.medium + target.wounds.heavy == 0
    weak = fight_of([typed("Novice", attack=0)], [typed("Wall", defence=9)])
    played = rules.play(
        saga_with(weak), weak, rules.Blow("Disarm"), Scripted(5, 2, 2, 2)
    )
    assert "fails" in played.text or "misses" in played.text


def test_an_unattacked_fighter_disengages_freely_and_its_side_loses():
    runner = typed("Runner", init=9)
    fight = fight_of([runner], [typed("Guard")])
    saga = saga_with(fight)
    played = rules.play(saga, fight, rules.Blow(rules.DISENGAGE), Scripted(5, 2))
    assert runner.out == "Disengaged"
    assert "disengages" in played.text
    assert fight.over == "Theirs win the fight."


def test_next_round_plays_to_the_end_and_writes_the_diaries():
    grog = Character(id="g1", name="Hugo", type="grog", covenant_id="cov1")
    keep = Covenant(id="cov1", saga_id="s", name="Keep")
    fight = fight_of(
        [typed("Champion", init=20, attack=30, damage=30)],
        [Combatant("Hugo", "character", "g1", id="hugo")],
        covenant_id="cov1",
    )
    saga = saga_with(fight, characters=[grog], covenants=[keep])
    told = fights.next_round(saga, fight, Scripted(5, 2, 5, 2)).apply()
    assert fight.over == "Ours win the fight."
    assert told[-1] == "Written in 2 Diaries."
    assert (grog.diary[-1].name, keep.diary[-1].name) == ("Test fray", "Test fray")
    assert grog.diary[-1].details.startswith("Ours win the fight. (1 round")
    # Once only: asking again writes nothing more.
    assert fights.record_ending(saga, fight) == []


def test_restart_clears_the_order_and_chronicle_but_keeps_wounds():
    target = typed("Target")
    fight = fight_of([typed("Giant", init=20, attack=30, damage=30)], [target])
    saga = saga_with(fight)
    fights.next_round(saga, fight, Scripted(5, 2, 5, 2)).apply()
    assert fight.over
    rules.restart(fight)
    assert (fight.round, fight.order, fight.log, fight.over) == (0, [], [], "")
    assert not fight.recorded
    assert target.wounds.dead


def test_a_botch_leaves_a_negative_base_where_it_was():
    # A botch adds nothing: a negative base Defence stays negative (DE p. 393).
    lines: list[str] = []
    assert rules._roll(
        Scripted(0, 0), Saga(id="s", name="S"), "Defence", -3, lines
    ) == (
        -3,
        True,
    )
    assert rules._roll(Scripted(0, 0), Saga(id="s", name="S"), "Defence", 4, lines) == (
        0,
        True,
    )


# -- range, riding, shield grogs, grappling, splitting, magic --


def _begun(fight: Fight, saga: Saga, *faces: int) -> None:
    rules.roll_initiative(saga, fight, Scripted(*faces))


def test_a_mounted_fighter_adds_ride_up_to_three():
    knight = typed("Knight", attack=10, defence=8, damage=5, soak=4)
    knight.mounted, knight.ride = True, 5
    foe = typed("Foe", attack=6, defence=6, damage=3, soak=3)
    fight = fight_of([knight], [foe])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["knight"], every["foe"], rules.ATTACK)
    assert chances.total("attack") == 13
    back = rules.odds(saga, fight, every["foe"], every["knight"], rules.ATTACK)
    assert back.total("defence") == 11
    assert "Mounted, Ride +3" in rules.tags(saga, fight, every["knight"])


def test_at_range_only_missiles_strike_and_take_minus_three_an_increment():
    fight = fight_of([typed("Brute", attack=8)], [typed("Foe")])
    fight.range = 3
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    assert rules.odds(saga, fight, every["brute"], every["foe"], rules.ATTACK).blocked
    assert rules.actions_for(saga, fight, every["brute"]) == (
        rules.DISENGAGE,
        rules.WAIT,
    )
    assert rules.range_penalty(fight) == -6


def test_a_defended_fighter_cant_be_struck_while_its_shield_grog_stands():
    magus = typed("Magus", attack=0)
    grog = typed("Grog", attack=6, defence=6)
    grog.defends = "magus"
    foe = typed("Foe", init=9, attack=9, damage=6)
    fight = fight_of([magus, grog], [foe])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["foe"], every["magus"], rules.ATTACK)
    assert "defended by Grog" in chances.blocked
    assert rules.default_target(saga, fight, every["foe"]).id == "grog"


def test_a_grapple_holds_and_the_held_one_only_breaks_free():
    wrestler = typed("Wrestler", init=9, attack=8, defence=4, damage=2, soak=3)
    victim = typed("Victim", attack=6, defence=2, damage=4, soak=3)
    fight = fight_of([wrestler], [victim])
    saga = saga_with(fight)
    # Initiative 5 and 5 (Wrestler 14 first); Attack 8 + 7 = 15 against 2 + 3.
    played = rules.play(
        saga, fight, rules.Blow(rules.GRAPPLE, "victim"), Scripted(5, 5, 7, 3)
    )
    assert "grapples Victim (grip 10)" in played.text
    every = rules.units(saga, fight)
    assert rules.actions_for(saga, fight, every["victim"])[0] == rules.BREAK_FREE
    # An Attack chosen while held becomes an escape: 6 + 9 = 15 against 4 + 2.
    played = rules.play(
        saga, fight, rules.Blow(rules.ATTACK, "wrestler"), Scripted(9, 2)
    )
    assert "loosens" in played.text and fight.grips[0].strength == 1
    rules.play(saga, fight, rules.Blow(rules.WAIT), Scripted())
    played = rules.play(saga, fight, rules.Blow(rules.BREAK_FREE), Scripted(9, 2))
    assert "breaks free" in played.text and not fight.grips
    assert wrestler.wounds.light == 1


def test_splitting_a_group_divides_it_in_half():
    foes = [typed(f"Foe {n}", attack=5, defence=3, soak=2) for n in range(4)]
    group = FightGroup("Foes", [f.id for f in foes])
    a, b = typed("A", init=9, attack=8), typed("B", init=8, attack=8)
    fight = Fight(
        "Split",
        sides=[
            FightSide("Ours", combatants=[a, b]),
            FightSide("Theirs", combatants=foes, groups=[group]),
        ],
    )
    saga = saga_with(fight)
    # Initiative: A 14, B 13, the group 6; A's 8 + 5 against 3 + 4.
    played = rules.play(
        saga, fight, rules.Blow(rules.SPLIT, group.id), Scripted(5, 5, 3, 5, 4)
    )
    assert "splits Foes" in played.text
    assert len(group.members) == 2
    assert len(fight.sides[1].groups) == 2


def test_a_form_bonus_adds_to_soak_against_its_harm():
    magus = Character(id="m", name="Marcus", type="magus")
    magus.arts["animal"] = ArtScore(xp=55)
    wolf = Combatant("Wolf", CREATURE_FIGHTER, "wolf", attack=9, damage=4, id="wolf")
    fight = fight_of([Combatant("Marcus", "character", "m", id="marcus")], [wolf])
    saga = saga_with(fight, characters=[magus])
    every = rules.units(saga, fight)
    chances = rules.odds(saga, fight, every["wolf"], every["marcus"], rules.ATTACK)
    assert [t.label for t in chances.soak] == ["Soak", "Animal Form Bonus"]
    assert chances.soak[1].amount == 2


def test_a_device_without_penetration_is_resisted():
    fight = fight_of([typed("Holder")], [typed("Spirit", resistance=10)])
    saga = saga_with(fight)
    every = rules.units(saga, fight)
    assert (
        rules.device_odds(saga, fight, every["spirit"], rules.Blow(rules.DEVICE))
        is None
    )


def test_a_spontaneous_spell_casts_penetrates_and_burns():
    magus = Character(id="m", name="Marcus", type="magus")
    magus.arts["creo"] = ArtScore(xp=55)
    magus.arts["ignem"] = ArtScore(xp=55)
    fight = fight_of(
        [Combatant("Marcus", "character", "m", id="marcus", init=9)],
        [typed("Brigand", soak=0)],
    )
    saga = saga_with(fight, characters=[magus])
    blow = rules.Blow(
        rules.CAST,
        "brigand",
        spell=rules.SPONTANEOUS,
        arts="Creo Ignem",
        level=5,
        fatiguing=True,
        damage=10,
    )
    # Initiative 5, 2; casting die 6; damage die 5 against soak die 2.
    played = rules.play(saga, fight, blow, Scripted(5, 2, 6, 5, 2))
    assert "strikes Brigand" in played.text
    assert any("Penetration" in line for line in played.lines)
    assert magus.fatigue_level != "fresh"


def test_greek_fire_splashes_round_a_shield_into_soak():
    """The Sundered Eagle p. 47: a hand-held siphon is a missile weapon
    worked with Profession: Naffatun, and a shield's Defence adds to Soak
    against it instead of to Defence."""
    naffatun = Character(
        id="n",
        name="Naffatun",
        type="grog",
        characteristics=Characteristics(dexterity=1),
        abilities=[Ability("Profession: Naffatun", xp=ability_xp(3))],
        inventory=[
            Possession(
                id="siphon",
                kind="weapon",
                name="Siphon",
                gear_id="weapon_greek_fire_siphon",
                weapon_init=-2,
                weapon_attack=4,
                weapon_defense=0,
                weapon_damage=10,
            )
        ],
    )
    shield = Possession(
        id="shield",
        kind="weapon",
        name="Round Shield",
        gear_id="weapon_round_shield",
        weapon_defense=2,
    )
    sailor = Character(id="t", name="Sailor", type="grog", inventory=[shield])
    fight = fight_of(
        [Combatant("Naffatun", "character", "n", id="naffatun")],
        [Combatant("Sailor", "character", "t", id="sailor")],
    )
    saga = saga_with(fight, characters=[naffatun, sailor])
    every = rules.units(saga, fight)
    assert every["naffatun"].vanguard.figures().missile
    chances = rules.odds(saga, fight, every["naffatun"], every["sailor"], rules.ATTACK)
    assert chances.total("attack") == 1 + 3 + 4
    assert chances.total("defence") == 0  # the shield's +2 taken off
    assert [t.amount for t in chances.soak] == [0, 2]
    # Against an ordinary missile the shield defends as usual.
    naffatun.inventory[0].gear_id = "weapon_long_bow"
    chances = rules.odds(saga, fight, every["naffatun"], every["sailor"], rules.ATTACK)
    assert (chances.total("defence"), len(chances.soak)) == (2, 1)
