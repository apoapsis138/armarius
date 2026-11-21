"""The playing Scene's aura and who is present as defaults (scene_aura.py):
its aura and realm fill in on casting and on Roll from the sheet and Roll
requests for a Supernatural or Hedge Art Ability, taken as Magic, with
one extra botch die per point of a foreign realm's aura (twice that in a
regio of another realm); a mundane roll gets none (DE p. 411, p. 422,
p. 545). Who is present prefills a Roll request's characters and a Show's
recipients, and never limits who may act."""

from __future__ import annotations

import pytest
from test_scene_play import HOST, _begun, _set

from ars_magica_manager import chronicle, commands, scene_aura
from ars_magica_manager.forms import hedge_cast, roll_request, sheet_roll
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.models import Ability, Casting, Character, Saga
from ars_magica_manager.rules import realms

SECOND_SIGHT = "Second Sight"


def _seer(saga: Saga) -> Character:
    """Aelfric holds Second Sight 3 (Supernatural) and Awareness 2."""
    aelfric = saga.characters[0]
    aelfric.abilities = [
        Ability(SECOND_SIGHT, "Supernatural", xp=30),
        Ability("Awareness", xp=15),
    ]
    return aelfric


# -- the aura here now --


def test_no_aura_here_while_no_scene_plays() -> None:
    saga, session, book = _begun()
    assert scene_aura.aura_here(saga, session, HOST, book) is None


def test_the_storyguide_has_the_playing_scenes_aura_told_or_not() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    assert scene_aura.aura_here(saga, session, HOST, book) == scene_aura.AuraHere(
        2, "Faerie"
    )


def test_a_player_has_it_only_when_the_table_was_told() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-ford")
    assert scene_aura.aura_here(saga, session, "ana", book) is None
    _set(book, saga, session, "u-home", tell_aura=True)
    assert scene_aura.aura_here(saga, session, "ana", book) == scene_aura.AuraHere(
        4, "Magic"
    )


def test_a_regio_level_counts_as_a_regio() -> None:
    saga, session, book = _begun()
    saga.scenes[1].place_level = 1
    _set(book, saga, session, "u-hill", tell_aura=True)
    for who in (HOST, "ana"):
        found = scene_aura.aura_here(saga, session, who, book)
        assert found is not None and found.in_regio, who


def test_a_hedge_casting_form_starts_on_the_scenes_aura() -> None:
    saga, session, book = _begun()
    session.scenes[0].present = ["characters:aelfric"]
    _set(book, saga, session, "u-ford")
    fields = {f.key: f.value for f in hedge_cast.fields(saga, saga.characters[0])}
    assert (fields["aura"], fields["aura_realm"]) == (2, "Faerie")


def test_only_those_present_start_on_the_scenes_aura() -> None:
    saga, session, book = _begun()
    aelfric = saga.characters[0]
    session.scenes[0].present = []  # Aelfric stayed at home
    _set(book, saga, session, "u-ford")
    assert scene_aura.aura_now(saga, aelfric) == realms.present_aura(saga, aelfric)
    assert scene_aura.for_character(saga, session, HOST, book, "aelfric") is None


def test_where_who_is_present_isnt_known_the_told_aura_applies() -> None:
    """A player's seat holds no Scenes, so it can't know who is present:
    a told aura starts their forms all the same."""
    saga, session, book = _begun()
    _set(book, saga, session, "u-home", tell_aura=True)
    session.scenes = []  # as a player's copy of the saga holds them
    assert scene_aura.for_character(
        saga, session, "ana", book, "aelfric"
    ) == scene_aura.AuraHere(4, "Magic")


def test_a_seat_holding_another_sessions_chronicle_has_no_aura_here() -> None:
    saga, session, book = _begun()
    _set(book, saga, session, "u-home", tell_aura=True)
    held = chronicle.SeatChronicle()
    held.session_id = "an-earlier-session"
    held.entries = list(book.entries)
    assert scene_aura.book_of(session, held) is None
    held.session_id = session.id
    assert scene_aura.book_of(session, held) is held


def test_a_lunar_scene_aura_is_offered_where_it_starts() -> None:
    saga, session, book = _begun()
    session.scenes[0].present = ["characters:aelfric"]
    _seer(saga)
    saga.scenes[0].realm = "Lunar"
    _set(book, saga, session, "u-ford")
    form = sheet_roll.roll_form(saga, saga.characters[0], ability=SECOND_SIGHT)
    assert isinstance(form, commands.Form)
    realm = next(f for f in form.fields() if f.key == "aura_realm")
    assert realm.value == "Lunar" and "Lunar" in [v for _l, v in realm.options]
    fields = {f.key: f for f in hedge_cast.fields(saga, saga.characters[0])}
    assert "Lunar" in [v for _l, v in fields["aura_realm"].options]


def test_casting_forms_start_on_the_scenes_aura_else_where_he_is() -> None:
    saga, session, book = _begun()
    session.scenes[0].present = ["characters:aelfric"]
    aelfric = saga.characters[0]
    assert scene_aura.aura_now(saga, aelfric) == realms.present_aura(saga, aelfric)
    _set(book, saga, session, "u-ford")
    assert scene_aura.aura_now(saga, aelfric) == (2, "Faerie")


# -- the term on a supernatural Ability --


def _roll_terms(
    saga: Saga, ability: str, aura: int, realm: str, regio: bool = False
) -> tuple[list[chronicle.Term], int]:
    request = chronicle.RollRequest(
        character_id="aelfric",
        sheet=chronicle.SheetRoll(
            "Perception", ability, aura=aura, aura_realm=realm, in_regio=regio
        ),
    )
    return chronicle.sheet_terms(saga, request)


def test_a_supernatural_ability_takes_the_aura_as_magic() -> None:
    saga, _session, _book = _begun()
    _seer(saga)
    terms, extra = _roll_terms(saga, SECOND_SIGHT, 3, "Magic")
    assert ("Aura, Magic 3", 3) in terms and extra == 0
    terms, extra = _roll_terms(saga, SECOND_SIGHT, 2, "Faerie")
    assert ("Aura, Faerie 2", 1) in terms and extra == 2
    terms, extra = _roll_terms(saga, SECOND_SIGHT, 3, "Divine")
    assert ("Aura, Divine 3", -9) in terms and extra == 3


def test_a_foreign_regio_doubles_the_botch_dice() -> None:
    saga, _session, _book = _begun()
    _seer(saga)
    _terms, extra = _roll_terms(saga, SECOND_SIGHT, 2, "Faerie", regio=True)
    assert extra == 4


def test_a_mundane_ability_or_none_takes_no_aura() -> None:
    saga, _session, _book = _begun()
    _seer(saga)
    for ability in ("Awareness", ""):
        terms, extra = _roll_terms(saga, ability, 3, "Infernal")
        assert not any(label.startswith("Aura") for label, _n in terms)
        assert extra == 0


# -- the forms' defaults --


def test_roll_from_the_sheet_starts_with_the_scenes_aura() -> None:
    saga, session, book = _begun()
    session.scenes[0].present = ["characters:aelfric"]
    _seer(saga)
    _set(book, saga, session, "u-ford")
    form = sheet_roll.roll_form(saga, saga.characters[0], ability=SECOND_SIGHT)
    assert isinstance(form, commands.Form)
    fields = {f.key: f for f in form.fields()}
    assert (fields["aura"].value, fields["aura_realm"].value) == (2, "Faerie")
    shown = fields["aura"].show_if
    assert shown is not None
    assert shown({"ability": SECOND_SIGHT}) and not shown({"ability": "Awareness"})


def test_a_roll_request_starts_on_those_present_and_the_scenes_aura() -> None:
    saga, session, book = _begun()
    saga.characters.append(Character(id="brigit", name="Brigit", type="companion"))
    session.castings.append(Casting("ben", "brigit"))
    session.scenes[0].present = ["characters:brigit"]
    _set(book, saga, session, "u-ford")
    form = roll_request.request_form(saga, session, HOST, book)
    values = {f.key: f.value for f in form.fields()}
    assert values[roll_request.TICK + "aelfric"] is False
    assert values[roll_request.TICK + "brigit"] is True
    assert (values["aura"], values["aura_realm"]) == (2, "Faerie")


def test_an_answer_takes_the_requests_aura_and_players_never_see_it() -> None:
    saga, session, book = _begun()
    _seer(saga)
    call = chronicle.RollCall(
        ("aelfric",),
        "Perception",
        SECOND_SIGHT,
        visibility=chronicle.PUBLIC,
        aura=6,
        aura_realm="Infernal",
    )
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    stamped = chronicle.stamped(request, "ana", session, saga)
    assert "Infernal" not in str(stamped.body)
    rolled = chronicle.answer(book, saga, session, request.number, "aelfric", by="ana")
    assert ["Aura, Infernal 6", -6] in rolled.body["terms"]


def test_a_show_starts_with_the_players_of_those_present() -> None:
    saga, session, book = _begun()
    session.scenes[0].present = ["characters:aelfric"]
    _set(book, saga, session, "u-ford")
    assert show_forms.default_to(saga, session) == ("ana",)
    session.scenes[0].present = []
    assert show_forms.default_to(saga, session) == ()


@pytest.mark.parametrize("who", [HOST, "ana"])
def test_present_never_limits_who_may_roll(who: str) -> None:
    saga, session, book = _begun()
    _seer(saga)
    session.scenes[0].present = []
    _set(book, saga, session, "u-ford")
    request = chronicle.RollRequest(
        character_id="aelfric", sheet=chronicle.SheetRoll("Perception", SECOND_SIGHT)
    )
    assert chronicle.why_not_roll(saga, session, request, who) is None
