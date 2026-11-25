"""Entered dice in sieges and agents (STORY-2470): with the saga's
"Entered dice allowed", Next Siege Event, Impress, Set a Task and Resolve
the Task offer "I'll roll it", ask for each d10 by name, and play the
faces entered. Lords of Men pp. 113-114 (a mine: Intelligence + Sapper +
stress die against the castle's counter-miner + Defense Bonus + stress
die) and p. 24 (Impress: stress die + Presence + Leadership against 6)."""

from __future__ import annotations

from typing import Any

from ars_magica_manager import entered_dice, sieges, viewing
from ars_magica_manager.commands import (
    CANCELLED,
    Act,
    Finished,
    Form,
    Question,
    drive,
)
from ars_magica_manager.entered_dice import ENTER
from ars_magica_manager.forms import agents as agent_forms
from ars_magica_manager.models import (
    Ability,
    Agent,
    Character,
    Player,
    Saga,
    Session,
    Siege,
)
from ars_magica_manager.rules import options
from ars_magica_manager.rules import siege as siege_rules
from ars_magica_manager.rules.xp import ability_xp

ALLOWED = {options.ENTERED_DICE_ALLOWED: True}


class _Table:
    """Chooses I'll roll it, then answers each die prompt with the next
    face (or stops after `stop_after` prompts), keeping what was asked."""

    def __init__(
        self, *faces: int, values: dict[str, Any] | None = None, stop_after: int = 99
    ) -> None:
        self.faces = list(faces)
        self.values = values or {}
        self.asked: list[str] = []
        self.stop_after = stop_after

    def __call__(self, question: Question) -> Any:
        assert isinstance(question, Form)
        if [f.key for f in question.fields()] == ["face"]:
            self.asked.append(question.title)
            if len(self.asked) > self.stop_after:
                return CANCELLED
            return {"face": str(self.faces.pop(0))}
        return {**self.values, "dice": ENTER}


def _siege() -> tuple[Saga, Siege]:
    castle = Siege("S", miners=1, sapper=10, counter_sapper=0)
    return Saga(id="s", name="S", sieges=[castle], rule_options=ALLOWED), castle


def test_a_mine_asks_for_its_dice_and_plays_the_faces_entered() -> None:
    saga, castle = _siege()
    table = _Table(5, 2, values={"event": siege_rules.UNDERMINE, "wall": "0"})
    outcome = drive(sieges.next_event(saga, castle), table)
    assert table.asked == ["Mine Attack: stress die", "Castle Defense: stress die"]
    # 10 + 5 = 15 against 0 + Defense Bonus 2 + 2 = 4: the Defenses fall a step.
    assert castle.defenses == "Shoddy"
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    assert any("(entered by the storyguide)" in line for line in outcome.end)


def test_a_siege_event_changes_nothing_until_its_last_die() -> None:
    saga, castle = _siege()
    table = _Table(
        5, values={"event": siege_rules.UNDERMINE, "wall": "0"}, stop_after=1
    )
    drive(sieges.next_event(saga, castle), table)
    assert (castle.defenses, castle.events, castle.days) == ("Standard", [], 0)


def test_the_siege_offers_no_choice_when_the_app_rolls() -> None:
    saga, castle = _siege()
    saga.rule_options = {}
    form = sieges.next_event(saga, castle)
    assert isinstance(form, Form)
    assert "dice" not in {f.key for f in form.fields()}


def _lord() -> Character:
    """Presence +2, Communication +1, Leadership 3."""
    lord = Character(id="lord", name="Lord Robert", type="companion")
    lord.characteristics.presence = 2
    lord.characteristics.communication = 1
    lord.abilities = [Ability("Leadership", xp=ability_xp(3))]
    lord.agents = [
        Agent("Sir Konrad", resistance=0, impressed=True, bond_trait="Owes", bond=2),
        Agent("Magister Hartwig", status="minor_virtue"),
    ]
    return lord


def test_impress_asks_for_its_die_and_impresses_on_the_face_entered() -> None:
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord], rule_options=ALLOWED)
    step = agent_forms.impress(saga, lord, 1)
    assert isinstance(step, Form)
    table = _Table(4)
    outcome = drive(step, table)
    assert table.asked == ["Impress Magister Hartwig: stress die"]
    # 4 + Presence 2 + Leadership 3 = 9 against 6.
    assert lord.agents[1].impressed
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    assert "Stress die 4, Presence +2, Leadership +3, Gift +0 = 9 vs 6" in " ".join(
        outcome.end
    )


def test_impress_asks_nothing_when_the_app_rolls() -> None:
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord])
    assert isinstance(agent_forms.impress(saga, lord, 1), Act)


def test_set_a_task_asks_for_the_persuasion_die() -> None:
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord], rule_options=ALLOWED)
    values = {
        "ability": "Leadership",
        "task": "secret",
        "timeframe": "day",
        "risk": "death",
    }
    table = _Table(9, values=values)
    outcome = drive(agent_forms.set_task(saga, lord, 0), table)
    assert table.asked == ["Lord Robert's persuasion: stress die"]
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    # 9 + Communication 1 + Leadership 3 + Bond 2 = 15 against 18.
    assert "the die shows 9, + 6 (Leadership) = 15 against 18." in outcome.end[0]


def test_resolve_the_task_asks_for_the_agents_die() -> None:
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord], rule_options=ALLOWED)
    values = {"total": 5, "band": "easy", "ease": 6, "risk": "none"}
    table = _Table(3, values=values)
    outcome = drive(agent_forms.resolve(saga, lord, 0), table)
    assert table.asked == ["Sir Konrad's task: simple die"]
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    assert "The die shows 3, + 5" in " ".join(outcome.end)


# -- review fixes --


def test_a_die_prompt_title_keeps_a_bracketed_name() -> None:
    prompt = entered_dice.die_prompt(
        "Fray", "Hugo [the Bold]'s task: simple die", lambda _face: None
    )
    assert prompt.title == "Hugo \\[the Bold]'s task: simple die"


def test_an_entered_dice_line_names_a_bracketed_player_safely() -> None:
    saga, castle = _siege()
    viewing.use(
        viewing.Viewer(viewing.STORYGUIDE, Player("ann", "Ann [GM]", "storyguide"))
    )
    try:
        table = _Table(5, 2, values={"event": siege_rules.UNDERMINE, "wall": "0"})
        outcome = drive(sieges.next_event(saga, castle), table)
    finally:
        viewing.use(viewing.STORYGUIDE_VIEWER)
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    # Shown as markup, the bracket escaped; kept in the siege's record as written.
    assert any(line.endswith("(entered by Ann \\[GM])") for line in outcome.end)
    assert castle.events[-1].lines[-1].endswith("(entered by Ann [GM])")


def test_impress_refuses_entered_dice_once_a_session_is_under_way() -> None:
    lord = _lord()
    saga = Saga(id="s", name="S", characters=[lord], rule_options=ALLOWED)
    step = agent_forms.impress(saga, lord, 1)

    def ask(question: Question) -> Any:
        assert isinstance(question, Form)
        if [f.key for f in question.fields()] == ["face"]:
            # A Session begins in another window while the die is entered.
            saga.sessions = [Session("evening", under_way=True)]
            return {"face": "4"}
        return {"dice": ENTER}

    outcome = drive(step, ask)
    assert isinstance(outcome, Finished) and isinstance(outcome.end, list)
    assert not lord.agents[1].impressed
    assert "A Session is under way" in " ".join(outcome.end)
