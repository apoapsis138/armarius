"""Who may roll what at a Session: the Table's rules, asked by every roll."""

from __future__ import annotations

import pytest

from ars_magica_manager import chronicle, table_rules, viewing
from ars_magica_manager.forms import free_roll
from ars_magica_manager.models import Casting, Character, Player, Saga, Session

HOST = viewing.HOST
PUBLIC, PRIVATE, BLIND = table_rules.PUBLIC, table_rules.PRIVATE, table_rules.BLIND
OTHERS = "Roll for a character you play tonight."
NOT_BLIND = "Only the Session's storyguide rolls Blind."


def _saga() -> Saga:
    """Ana plays Aelfric tonight; Ben plays no one; the host runs it."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus"),
        Character(id="gus", name="Gus", type="grog"),
    ]
    saga.sessions = [
        Session(
            "s1",
            coming=["ana", "ben"],
            castings=[Casting(player_id="ana", character_id="aelfric")],
        )
    ]
    return saga


@pytest.mark.parametrize(
    ("who", "character_id", "visibility", "for_no_one", "expected"),
    [
        (HOST, "gus", BLIND, False, None),
        (HOST, "", BLIND, False, None),
        ("ana", "aelfric", PUBLIC, False, None),
        ("ana", "aelfric", PRIVATE, False, None),
        ("ana", "aelfric", BLIND, False, NOT_BLIND),
        ("ana", "gus", PUBLIC, False, OTHERS),
        ("ben", "aelfric", PUBLIC, False, OTHERS),
        ("ana", "", PUBLIC, False, OTHERS),
        ("ana", "", PUBLIC, True, None),
        ("ana", "", BLIND, True, NOT_BLIND),
        (HOST, "nobody", PUBLIC, False, "That character isn't in the saga."),
        (HOST, "gus", "loud", False, "Choose who sees the roll."),
    ],
)
def test_who_may_roll_for_whom(
    who: str, character_id: str, visibility: str, for_no_one: bool, expected: str | None
) -> None:
    saga = _saga()
    assert (
        table_rules.why_not_roll_for(
            saga,
            saga.sessions[0],
            who,
            character_id,
            visibility,
            for_no_one=for_no_one,
        )
        == expected
    )


def test_only_the_storyguide_is_offered_blind_and_rolls_blind_unless_told() -> None:
    saga = _saga()
    session = saga.sessions[0]
    assert [v for _, v in table_rules.visibility_options(True)] == [
        PUBLIC,
        PRIVATE,
        BLIND,
    ]
    assert [v for _, v in table_rules.visibility_options(False)] == [PUBLIC, PRIVATE]
    assert table_rules.default_visibility(saga, session, HOST) == BLIND
    assert table_rules.default_visibility(saga, session, "ana") == PUBLIC


def test_every_rolling_form_starts_at_the_same_default() -> None:
    """The Free roll form used to start the storyguide's roll Public."""
    saga = _saga()
    session = saga.sessions[0]
    for who, expected in ((HOST, BLIND), ("ana", PUBLIC)):
        form = free_roll.free_roll_form(saga, session, who, lambda _request: None)
        field = next(f for f in form.fields() if f.key == "visibility")
        assert field.value == expected


def test_a_form_roll_keeps_to_the_same_rule() -> None:
    """A player's form roll is for a character of theirs (or no one), and a
    character who can't act rolls nothing, as a roll from the sheet."""
    saga = _saga()
    session = saga.sessions[0]
    assert chronicle.why_not_form_roll(saga, session, "gus", PUBLIC, "ana") == OTHERS
    assert chronicle.why_not_form_roll(saga, session, "", PUBLIC, "ana") is None
    assert chronicle.why_not_form_roll(saga, session, "gus", BLIND, HOST) is None
    saga.characters[1].wounds.dead = True
    assert chronicle.why_not_form_roll(saga, session, "gus", BLIND, HOST) == (
        "Gus is dead."
    )


def test_who_plays_whom_tonight() -> None:
    session = _saga().sessions[0]
    assert table_rules.plays(session, "ana") == {"aelfric"}
    assert table_rules.plays(session, "ben") == set()
    assert table_rules.player_of(session, "aelfric") == "ana"
    assert table_rules.player_of(session, "gus") == ""
