"""Fights played blow by blow (rules.fight, fights.py): Initiative, a
blow's wound onto a character's sheet, a group's blows spread over the
other group, a group splitting when its vanguard falls, scuffles, special
effects, disengaging, Next Round ending a fight, the Diaries it writes and
Restart. The dice are scripted: each test says what each d10 shows."""

import random

from ars_magica_manager import fights
from ars_magica_manager.models import (
    Character,
    Combatant,
    Covenant,
    Fight,
    FightGroup,
    FightSide,
    Saga,
)
from ars_magica_manager.rules import fight as rules


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
