"""Roll from the sheet as a More command (forms/sheet_roll.py, through the
More registry of ADR 0006, so the terminal and the desktop do the same):
offered on a character's Abilities and Characteristics while a Session
is Under way and the Virtual Tabletop (Preview) is on, and sending what
to roll, never a number from the sheet."""

from __future__ import annotations

import pytest

from ars_magica_manager import actions, chronicle, commands, viewing, virtual_tabletop
from ars_magica_manager.actions import NodeKind
from ars_magica_manager.forms import menu as menu_forms
from ars_magica_manager.forms import menu_refresh, sheet_roll
from ars_magica_manager.forms import page as page_forms
from ars_magica_manager.models import (
    Ability,
    Casting,
    Character,
    Characteristics,
    Saga,
    Session,
    Wounds,
)

HOST = viewing.HOST


def _saga() -> tuple[Saga, Character]:
    saga = Saga(id="fengheld", name="Fengheld")
    aelfric = Character(id="aelfric", name="Aelfric", type="companion")
    aelfric.characteristics = Characteristics(strength=1, dexterity=2)
    aelfric.abilities = [
        Ability("Athletics", xp=30, specialty="climbing"),
        Ability("Brawl", xp=15),
    ]
    saga.characters = [aelfric]
    saga.sessions = [
        Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    ]
    return saga, aelfric


def _page(
    saga: Saga, character: Character, section: str, row: int | None = None
) -> page_forms.Page:
    return page_forms.Page(
        saga, NodeKind.CHARACTER, character=character, section=section, row=row
    )


def _offered(saga: Saga, character: Character, section: str) -> bool:
    return actions.available("sheet_roll", _page(saga, character, section))


@pytest.fixture
def preview() -> None:
    virtual_tabletop.set_on(True)


def _begin(saga: Saga) -> chronicle.Chronicle:
    return chronicle.begin(saga, saga.sessions[0], by=HOST)


def test_roll_is_not_offered_with_the_preview_off() -> None:
    saga, aelfric = _saga()
    _begin(saga)

    assert not _offered(saga, aelfric, sheet_roll.ABILITIES)


@pytest.mark.usefixtures("preview")
def test_roll_is_offered_on_abilities_and_characteristics_while_under_way() -> None:
    saga, aelfric = _saga()
    assert not _offered(saga, aelfric, sheet_roll.ABILITIES)

    _begin(saga)

    assert _offered(saga, aelfric, sheet_roll.ABILITIES)
    assert _offered(saga, aelfric, sheet_roll.CHARACTERISTICS)
    assert not _offered(saga, aelfric, "section-personality-traits")


@pytest.mark.usefixtures("preview")
def test_an_incapacitated_character_is_offered_roll_and_told_why_not() -> None:
    saga, aelfric = _saga()
    _begin(saga)
    aelfric.wounds = Wounds(incapacitated=True)

    assert _offered(saga, aelfric, sheet_roll.ABILITIES)
    step = menu_forms._COMMANDS["sheet_roll"](
        _page(saga, aelfric, sheet_roll.ABILITIES)
    )
    assert isinstance(step, commands.Refuse)
    assert "Incapacitated" in step.why


@pytest.mark.usefixtures("preview")
def test_the_chosen_row_is_what_the_card_rolls() -> None:
    saga, aelfric = _saga()
    _begin(saga)

    step = menu_forms._COMMANDS["sheet_roll"](
        _page(saga, aelfric, sheet_roll.ABILITIES, row=1)
    )
    assert isinstance(step, commands.Form)
    values = {f.key: f.value for f in step.fields()}
    assert values["ability"] == "Brawl"

    step = menu_forms._COMMANDS["sheet_roll"](
        _page(saga, aelfric, sheet_roll.CHARACTERISTICS, row=6)
    )
    assert isinstance(step, commands.Form)
    values = {f.key: f.value for f in step.fields()}
    assert values["characteristic"] == "Dexterity"
    assert values["ability"] == ""


@pytest.mark.usefixtures("preview")
def test_the_card_offers_untrained_abilities_but_not_asterisked_ones() -> None:
    _saga_unused, aelfric = _saga()

    offered = {value: label for label, value in sheet_roll.ability_options(aelfric)}

    assert offered["Athletics"] == "Athletics 3"
    assert offered["Stealth"] == "Stealth (no score)"
    assert "Magic Theory" not in offered
    assert "Second Sight" not in offered


@pytest.mark.usefixtures("preview")
def test_the_card_rolls_at_the_host_with_the_sheets_scores() -> None:
    saga, aelfric = _saga()
    book = _begin(saga)
    step = menu_forms._COMMANDS["sheet_roll"](
        _page(saga, aelfric, sheet_roll.ABILITIES, row=0)
    )
    assert isinstance(step, commands.Form)

    assert (
        step.apply(
            {
                "characteristic": "Strength",
                "ability": "Athletics",
                "specialty": True,
                "die": "simple",
                "modifier": 0,
                "for_what": "Climb",
                "visibility": chronicle.PUBLIC,
            }
        )
        == []
    )

    roll = book.entries[-1]
    assert roll.kind == chronicle.ROLL
    assert chronicle.terms_of(roll.body) == [
        ("Strength", 1),
        ("Athletics", 3),
        ("Specialty (climbing)", 1),
    ]


@pytest.mark.usefixtures("preview")
def test_the_characteristic_last_rolled_with_an_ability_is_chosen_again() -> None:
    saga, _aelfric = _saga()
    book = _begin(saga)
    request = chronicle.RollRequest(
        character_id="aelfric", sheet=chronicle.SheetRoll("Strength", "Athletics")
    )
    chronicle.free_roll(book, saga, saga.sessions[0], request, by=HOST)

    assert sheet_roll.last_characteristic(book, "aelfric", "Athletics") == "Strength"
    assert sheet_roll.last_characteristic(book, "aelfric", "Brawl") == "Intelligence"


def test_rolling_saves_nothing_of_the_saga() -> None:
    assert menu_refresh.REFRESH["sheet_roll"].saves is False
