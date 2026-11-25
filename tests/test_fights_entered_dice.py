"""Entered dice in fights (STORY-2459): with the saga's "Entered dice
allowed", Next Blow and Next Round offer "I'll roll it", then ask for each
d10 in turn, naming whose roll it is and why, and play the fight from the
faces entered (DE p. 7: a 1 is rolled again and doubled; p. 393: Initiative,
Attack and Defence each take a stress die)."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import fights
from ars_magica_manager.commands import (
    CANCELLED,
    Act,
    Finished,
    Form,
    Question,
    drive,
)
from ars_magica_manager.entered_dice import ENTER
from ars_magica_manager.models import Combatant, Fight, FightSide, Saga
from ars_magica_manager.rules import options

ENTERED = options.ENTERED_DICE_ALLOWED


def _fight() -> tuple[Saga, Fight]:
    quick = Combatant("Quick", id="quick", init=10, defence=3)
    slow = Combatant("Slow", id="slow", attack=2, soak=4)
    fight = Fight(
        "Test fray",
        sides=[
            FightSide("Ours", combatants=[quick]),
            FightSide("Theirs", combatants=[slow]),
        ],
    )
    saga = Saga(id="s", name="S", fights=[fight], rule_options={ENTERED: True})
    return saga, fight


class _Table:
    """A person at the table: chooses "I'll roll it", then answers each
    die prompt with the next face, keeping what each prompt asked."""

    def __init__(self, *faces: int, stop_after: int | None = None) -> None:
        self.faces = list(faces)
        self.asked: list[str] = []
        self.stop_after = stop_after

    def __call__(self, question: Question) -> Any:
        assert isinstance(question, Form)
        keys = [f.key for f in question.fields()]
        if keys == ["face"]:
            self.asked.append(question.title)
            if self.stop_after is not None and len(self.asked) > self.stop_after:
                return CANCELLED
            return {"face": str(self.faces.pop(0))}
        return {"dice": ENTER}


def test_next_blow_offers_the_choice_only_when_the_saga_allows_entered_dice() -> None:
    saga, fight = _fight()
    form = fights.next_blow(saga, fight)
    assert isinstance(form, Form)
    shown = {f.key for f in form.fields()}
    assert "dice" in shown
    saga.rule_options = {}
    form = fights.next_blow(saga, fight)
    assert isinstance(form, Form)
    assert "dice" not in {f.key for f in form.fields()}


def test_next_blow_asks_each_die_by_name_and_plays_the_faces_entered() -> None:
    saga, fight = _fight()
    table = _Table(5, 2, 1, 4, 6)
    outcome = drive(fights.next_blow(saga, fight), table)
    assert table.asked == [
        "Quick's Initiative: stress die",
        "Slow's Initiative: stress die",
        "Quick's Attack: stress die",
        "Quick's Attack: a 1: roll again and double",
        "Slow's Defence: stress die",
    ]
    assert fight.initiative == {"quick": 15, "slow": 2}
    assert isinstance(outcome, Finished)
    told = outcome.end
    assert isinstance(told, list)
    # Both Initiatives, then Attack 0 + 8 against Defence 0 + 6: a hit by 2.
    said = (
        "Stress die 5; Stress die 2; Stress die 1, 4 → 4 × 2 = 8; Stress die 6 "
        "(entered by the storyguide)"
    )
    assert "Attack: +0 + stress die 8 = 8" in told
    assert told.count(said) == 1
    assert said in fight.log[-1].lines


def test_a_name_that_is_itself_a_possessive_is_asked_for_plainly() -> None:
    saga, fight = _fight()
    fight.sides[1].combatants[0].name = "A knight of the Baron's"
    table = _Table(5, 2, 1, stop_after=1)
    drive(fights.next_blow(saga, fight), table)
    assert table.asked == [
        "Quick's Initiative: stress die",
        "Initiative for A knight of the Baron's: stress die",
    ]


def test_a_blow_changes_nothing_until_its_last_die_is_entered() -> None:
    saga, fight = _fight()
    table = _Table(5, 2, 1, stop_after=3)
    drive(fights.next_blow(saga, fight), table)
    assert len(table.asked) == 4
    assert (fight.round, fight.log, fight.order) == (0, [], [])
    slow = fight.sides[1].combatants[0]
    assert slow.wounds.light + slow.wounds.medium + slow.wounds.heavy == 0


def test_next_round_asks_once_then_every_die_of_the_round() -> None:
    saga, fight = _fight()
    step = fights.next_round(saga, fight)
    assert isinstance(step, Form)
    table = _Table(5, 2, 5, 9, 3, 2)
    drive(step, table)
    assert table.asked == [
        "Quick's Initiative: stress die",
        "Slow's Initiative: stress die",
        "Quick's Attack: stress die",
        "Slow's Defence: stress die",
        "Slow's Attack: stress die",
        "Quick's Defence: stress die",
    ]
    assert fight.round == 2


def test_next_round_asks_nothing_when_the_app_rolls() -> None:
    saga, fight = _fight()
    saga.rule_options = {}
    assert isinstance(fights.next_round(saga, fight), Act)


def test_a_fight_is_found_again_when_the_list_changes_mid_entry() -> None:
    saga, fight = _fight()
    other = Fight("Earlier fray")
    saga.fights.insert(0, other)
    faces = [5, 2, 1, 4, 6]

    def ask(question: Question) -> Any:
        assert isinstance(question, Form)
        if [f.key for f in question.fields()] == ["face"]:
            if other in saga.fights:
                saga.fights.remove(other)  # deleted in another window
            return {"face": str(faces.pop(0))}
        return {"dice": ENTER}

    outcome = drive(fights.next_blow(saga, fight), ask)
    assert isinstance(outcome, Finished)
    assert fight.initiative == {"quick": 15, "slow": 2}
