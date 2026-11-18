"""The app's own rolling forms as Table rolls while a Session is Under way
(table_rolls.py): a form takes the host's dice, shows who sees the roll,
hides its typed die, and posts; a roll made outside a form (a place's roll
table) posts too. Outside a Session they roll as before."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from support import everything_saga

from ars_magica_manager import chronicle, place_events, table_rolls, viewing
from ars_magica_manager.commands import Confirm, Form
from ars_magica_manager.form_spec import shown
from ars_magica_manager.forms import trait_roll
from ars_magica_manager.models import Character, Saga, ScoredTrait, Session
from tests.test_chronicle import Faces

HOST = viewing.HOST


@pytest.fixture
def host_faces() -> Iterator[Any]:
    def use(*faces: int) -> None:
        table_rolls.host_source = lambda: Faces(*faces)

    yield use
    table_rolls.host_source = table_rolls.system_source


def _saga() -> tuple[Saga, Character]:
    saga = Saga(id="fengheld", name="Fengheld")
    brave = Character(id="aelfric", name="Aelfric", type="companion")
    brave.personality_traits = [ScoredTrait("Brave", 3)]
    saga.characters = [brave]
    saga.sessions = [Session("s1")]
    return saga, brave


def _form_rolls(book: chronicle.Chronicle) -> list[chronicle.Entry]:
    return [e for e in book.entries if e.kind == chronicle.FORM_ROLL]


def _keys(form: Form) -> list[str]:
    values = {f.key: f.value for f in form.fields()}
    return [f.key for f in form.fields() if shown(f, values)]


def test_a_trait_roll_outside_a_session_keeps_its_typed_die() -> None:
    saga, brave = _saga()

    form = trait_roll.roll_form(saga, brave)

    assert "die" in _keys(form)
    assert table_rolls.VISIBILITY not in _keys(form)


def test_a_trait_roll_at_the_table_takes_the_hosts_dice_and_posts(
    host_faces: Any,
) -> None:
    saga, brave = _saga()
    book = chronicle.begin(saga, saga.sessions[0], by=HOST)
    host_faces(7)

    form = trait_roll.roll_form(saga, brave)
    lines = form.apply(
        {
            "kind": trait_roll.TRAIT,
            "trait": "0",
            "ease": 9,
            table_rolls.VISIBILITY: chronicle.PUBLIC,
        }
    )

    assert "die" not in _keys(form)
    assert table_rolls.VISIBILITY in _keys(form)
    [entry] = _form_rolls(book)
    assert entry.body["faces"] == [7]
    assert entry.body["character_name"] == "Aelfric"
    assert entry.body["lines"] == [
        "Stress die 7, Brave +3, Silver Cord +0 = 10 vs 9: succeeds by 1. It holds."
    ]
    assert lines == entry.body["lines"]  # it says its own dice: no second line


def test_a_places_roll_table_posts_blind_for_the_storyguide(host_faces: Any) -> None:
    saga = everything_saga()
    saga.sessions.append(Session("tonight"))
    book = chronicle.begin(saga, saga.sessions[-1], by=HOST)
    coven = next(n for n in saga.neighbours if n.id == "coven")
    coven.details["tables"] = [
        {"name": "Rumours", "die": "Simple die", "rows": "1-5: Riders\n6+: A letter"}
    ]
    host_faces(6)

    command = place_events.roll_table(saga, coven, 0)

    assert isinstance(command, Confirm)
    [entry] = _form_rolls(book)
    assert entry.audience == chronicle.storyguide_only()
    assert entry.body["faces"] == [6]
    assert entry.body["lines"] == ["6, A letter"]


def test_a_places_roll_table_outside_a_session_uses_the_dice_given() -> None:
    saga = everything_saga()
    coven = next(n for n in saga.neighbours if n.id == "coven")
    coven.details["tables"] = [
        {"name": "Rumours", "die": "Simple die", "rows": "1-5: Riders\n6+: A letter"}
    ]

    command = place_events.roll_table(saga, coven, 0, Faces(2))

    assert isinstance(command, Confirm)
    assert "Riders" in command.question
