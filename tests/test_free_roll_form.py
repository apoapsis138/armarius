"""The Free roll form (forms/free_roll.py): one commands.Form, drawn by the
desktop's Chronicle pane (and, from a seat, sent to the host as a roll
request). It offers only the characters the roller may roll for, and Blind
only to the Session's storyguide."""

from __future__ import annotations

from typing import Any

import pytest

from ars_magica_manager import chronicle, commands, viewing
from ars_magica_manager.forms import free_roll
from ars_magica_manager.models import Casting, Character, Player, Saga, Session

HOST = viewing.HOST


def _saga() -> tuple[Saga, Session]:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana")]
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus"),
        Character(id="gus", name="Gus", type="grog"),
    ]
    session = Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    saga.sessions = [session]
    return saga, session


def _form(who: str) -> tuple[commands.Form, list[chronicle.RollRequest]]:
    saga, session = _saga()
    sent: list[chronicle.RollRequest] = []

    def submit(request: chronicle.RollRequest) -> str | None:
        sent.append(request)
        return None

    return free_roll.free_roll_form(saga, session, who, submit), sent


def _options(form: commands.Form, key: str) -> list[str]:
    return [
        value
        for _label, value in next(f for f in form.fields() if f.key == key).options
    ]


def _answer(form: commands.Form, values: dict[str, Any]) -> object:
    fields = {f.key: f.value for f in form.fields()}
    fields.update(values)
    problem = form.validate(fields) if form.validate else None
    assert problem is None, problem
    return form.apply(fields)


def test_a_player_rolls_for_the_characters_they_play_tonight() -> None:
    form, _sent = _form("ana")

    assert _options(form, "character_id") == ["aelfric"]
    assert _options(form, "visibility") == [chronicle.PUBLIC, chronicle.PRIVATE]


def test_the_storyguide_rolls_for_anyone_or_no_one_and_may_roll_blind() -> None:
    form, _sent = _form(HOST)

    assert _options(form, "character_id") == ["", "aelfric", "gus"]
    assert chronicle.BLIND in _options(form, "visibility")


def test_the_form_sends_what_to_roll_never_a_number() -> None:
    form, sent = _form("ana")

    _answer(
        form,
        {
            "die": "stress",
            "modifier": 9,
            "botch_dice": 2,
            "ease_factor": 12,
            "for_what": "Climb the wall",
            "character_id": "aelfric",
            "visibility": chronicle.PRIVATE,
        },
    )

    assert sent == [
        chronicle.RollRequest(
            stress=True,
            modifier=9,
            botch_dice=2,
            ease_factor=12,
            for_what="Climb the wall",
            character_id="aelfric",
            visibility=chronicle.PRIVATE,
        )
    ]


def test_a_simple_die_has_no_botch_dice() -> None:
    form, sent = _form(HOST)

    _answer(form, {"die": "simple", "modifier": 2, "botch_dice": 3})

    assert sent[0].stress is False and sent[0].botch_dice == 0


@pytest.mark.parametrize("botch_dice", [-1, 11])
def test_botch_dice_are_kept_between_none_and_ten(botch_dice: int) -> None:
    form, _sent = _form(HOST)
    fields = {f.key: f.value for f in form.fields()} | {"botch_dice": botch_dice}

    assert form.validate is not None and form.validate(fields)


def test_a_refused_roll_says_why() -> None:
    saga, session = _saga()
    form = free_roll.free_roll_form(saga, session, HOST, lambda _r: "The host is away.")

    assert _answer(form, {}) == commands.notes("The host is away.")
