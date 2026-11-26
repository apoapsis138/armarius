"""The evening's account (evening.py): End Session folds the Chronicle into
a line for each Scene set, Roll request, roll, outcome note and Show, by
Scene, each keeping who may read it; Struck rolls, Strikes, Messages and
Whispers leave none. Each kind says its own line (Kind.account)."""

from __future__ import annotations

import pytest
from chronicle_support import HOST, Faces, begun, every_kind

from ars_magica_manager import (
    chronicle,
    evening,
    players,
    scene_play,
    seat_view,
    storage,
    transfer,
    viewing,
)
from ars_magica_manager.models import AccountLine, Player, Saga, Session
from ars_magica_manager.sheets import session as session_sheet

BANNER = {"use": "u", "title": "The ford", "place": "A ford"}


def test_a_scripted_evening_reads_by_scene() -> None:
    saga, session, book = begun()
    chronicle.free_roll(
        book,
        saga,
        session,
        chronicle.RollRequest(for_what="Weather"),
        by=HOST,
        rng=Faces(7),
    )
    book.add(chronicle.SCENE_SET, HOST, chronicle.table(), BANNER)
    call = chronicle.RollCall(
        ("aelfric",), "Perception", visibility=chronicle.PUBLIC, for_what="Tracks"
    )
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    chronicle.answer(
        book, saga, session, request.number, "aelfric", by="ana", rng=Faces(6)
    )
    chronicle.note_outcome(book, session, request.number, "They follow.", by=HOST)
    chronicle.message(book, saga, session, "Nice.", by="ben")
    book.add(
        chronicle.SCENE_ENDED,
        HOST,
        chronicle.table(),
        {"use": "u", "title": "The ford"},
    )

    found = evening.account_of(book)

    assert [(line.scene, line.kind, line.text) for line in found] == [
        ("", "roll", "Storyguide (Weather): Stress die 7, +0 = 7"),
        ("The ford", "scene set", "Scene: The ford, at A ford"),
        ("The ford", "request", "Roll request: Perception for Aelfric (Tracks)"),
        ("The ford", "roll", "Aelfric (Tracks): Stress die 6, Perception +0 = 6"),
        (
            "The ford",
            "outcome",
            "Outcome of Perception for Aelfric (Tracks): They follow.",
        ),
    ]


def test_a_struck_roll_and_its_strike_leave_no_line() -> None:
    saga, session, book = begun()
    roll = chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(4)
    )
    chronicle.strike(book, session, roll.number, "Wrong die", by=HOST, saga=saga)

    assert evening.account_of(book) == []


def test_each_line_keeps_who_may_read_it() -> None:
    saga, session, book = begun()
    blind = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.BLIND)
    chronicle.free_roll(book, saga, session, blind, by=HOST, rng=Faces(5))
    private = chronicle.RollRequest(
        character_id="aelfric", visibility=chronicle.PRIVATE
    )
    chronicle.free_roll(book, saga, session, private, by="ana", rng=Faces(3))

    found = evening.account_of(book)

    assert [(line.audience, line.players) for line in found] == [
        (chronicle.STORYGUIDE, []),
        (chronicle.CHOSEN, ["ana"]),
    ]
    assert found[0].text.endswith("[Blind]") and found[1].text.endswith("[Private]")


def test_every_kind_says_its_account_line_or_none() -> None:
    """Strategy in the kind registry: a Scene set, Roll request, roll,
    form roll, Confidence spend, outcome and Show each give a line (a Show
    withdrawn none); every other kind none."""
    saga, session, book = begun()
    every_kind(saga, session, book)
    struck = chronicle.voided(book)

    giving = {
        e.kind
        for e in book.entries
        if e.number not in struck
        and chronicle.KINDS[e.kind].account(e, book) is not None
    }

    assert giving == {
        chronicle.SCENE_SET,
        chronicle.REQUEST,
        chronicle.ROLL,
        chronicle.FORM_ROLL,
        chronicle.CONFIDENCE,
        chronicle.OUTCOME,
    }
    assert {line.kind for line in evening.account_of(book)} == giving


def test_a_show_gives_a_line_until_it_is_withdrawn() -> None:
    *_, book = begun()
    shown = {"show": "x", "title": "A map"}
    show = book.add(chronicle.SHOW, HOST, chronicle.table(), shown)

    assert [x.text for x in evening.account_of(book)] == ["The storyguide shows: A map"]
    withdrawn = {"withdraws": show.number, "title": "A map"}
    book.add(chronicle.WITHDRAWN, HOST, chronicle.table(), withdrawn)
    assert evening.account_of(book) == []


def test_confidence_spent_on_a_roll_is_told_with_its_new_total() -> None:
    saga, session, book = begun()
    saga.characters[0].background.confidence_points = 3
    saga.characters[0].background.confidence_score = 1
    asked = chronicle.RollRequest(character_id="aelfric", ease_factor=9)
    roll = chronicle.free_roll(book, saga, session, asked, by="ana", rng=Faces(7))
    chronicle.spend_confidence(book, saga, session, roll.number, 1, by="ana")

    assert [x.text for x in evening.account_of(book)][-1] == (
        f"Aelfric spends 1 Confidence on roll {roll.number}: +3, now 10, "
        "succeeds, margin 1"
    )


def _scene(book: chronicle.Chronicle, title: str) -> None:
    banner = {"use": title.lower(), "title": title, "place": "A ford"}
    book.add(chronicle.SCENE_SET, HOST, chronicle.table(), banner)


def _ended(book: chronicle.Chronicle, title: str) -> None:
    ended = {"use": title.lower(), "title": title}
    book.add(chronicle.SCENE_ENDED, HOST, chronicle.table(), ended)


def _rolled(saga: Saga, session: Session, book: chronicle.Chronicle, die: int) -> None:
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(die)
    )


def test_lines_between_scenes_and_a_scene_played_twice_read_in_order() -> None:
    saga, session, book = begun()
    _scene(book, "The ford")
    _rolled(saga, session, book, 2)
    _ended(book, "The ford")
    _rolled(saga, session, book, 3)
    _scene(book, "The ford")
    _rolled(saga, session, book, 4)
    scene_play.end_session(saga, session, by=HOST)

    assert [g for g, _ in session_sheet.evening_groups(saga, session, "ben")] == [
        "The ford",
        session_sheet.BETWEEN_SCENES,
        "The ford",
    ]


def test_a_kind_must_say_its_account_line() -> None:
    with pytest.raises(TypeError):
        chronicle.Kind(  # type: ignore[call-arg]
            "handout",
            lambda _body: "A handout.",
            for_whom=chronicle.for_whom,
            held_back=(),
            body=chronicle.NoBody,
        )


def _blind_and_private() -> tuple[Saga, Session]:
    saga, session, book = begun()
    blind = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.BLIND)
    chronicle.free_roll(book, saga, session, blind, by=HOST, rng=Faces(5))
    private = chronicle.RollRequest(
        character_id="aelfric", visibility=chronicle.PRIVATE
    )
    chronicle.free_roll(book, saga, session, private, by="ana", rng=Faces(3))
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(2)
    )
    chronicle.message(book, saga, session, "Psst.", to=("ana",), by="ben")
    scene_play.end_session(saga, session, by=HOST)
    return saga, session


def test_end_session_writes_the_account_onto_the_session() -> None:
    _saga, session = _blind_and_private()

    assert session.played and len(session.account) == 3


@pytest.mark.parametrize(
    ("who", "tags"),
    [(HOST, ["Blind", "Private", ""]), ("ana", ["Private", ""]), ("ben", [""])],
)
def test_each_reader_reads_the_lines_their_audience_allows(
    who: str, tags: list[str]
) -> None:
    saga, session = _blind_and_private()

    found = evening.for_reader(saga, session, who)

    assert [
        chronicle.visibility_tag(chronicle.Audience(x.audience)) for x in found
    ] == (tags)


def _played_before_accounts() -> tuple[Saga, Session]:
    """A saga whose Session was played before accounts were kept, saved."""
    saga, session = _blind_and_private()
    session.account, session.account_kept = [], False
    storage.save_saga(saga)
    chronicle.forget_open()
    return saga, session


def test_a_session_played_before_accounts_gets_one_when_the_saga_opens() -> None:
    saga, _session = _played_before_accounts()

    opened = storage.load_saga(saga.id)

    assert len(opened.sessions[0].account) == 3
    assert opened.sessions[0].account_kept
    storage.save_saga(opened)  # kept by the next save, as a change
    assert len(storage.load_saga(saga.id).sessions[0].account) == 3


def test_an_evening_folded_once_is_never_read_again(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An evening with nothing to tell keeps no lines, yet its Chronicle
    isn't read again each time the saga opens."""
    saga, session = _played_before_accounts()
    session.account_kept = True
    storage.save_saga(saga)
    reads: list[str] = []
    monkeypatch.setattr(chronicle, "read", lambda *_a: reads.append("read"))

    storage.load_saga(saga.id)

    assert reads == []


def test_an_unreadable_chronicle_gives_no_account_and_is_tried_again() -> None:
    saga, session = _played_before_accounts()
    chronicle.path_of(saga, session).write_text("not json\n{}\n", encoding="utf-8")

    opened = storage.load_saga(saga.id).sessions[0]

    assert opened.account == [] and not opened.account_kept


def test_the_page_groups_the_evening_by_scene() -> None:
    saga, session, book = begun()
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(7)
    )
    book.add(chronicle.SCENE_SET, HOST, chronicle.table(), BANNER)
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(2)
    )
    scene_play.end_session(saga, session, by=HOST)

    assert session_sheet.evening_groups(saga, session, "ben") == [
        (session_sheet.BEFORE_SCENES, ["Storyguide: Stress die 7, +0 = 7"]),
        (
            "The ford",
            ["Scene: The ford, at A ford", "Storyguide: Stress die 2, +0 = 2"],
        ),
    ]


def test_an_evening_with_no_scene_has_one_group_without_a_heading() -> None:
    saga, session = _blind_and_private()

    assert [g for g, _ in session_sheet.evening_groups(saga, session, "ben")] == [""]


def test_an_export_carries_the_account_and_a_players_only_their_lines() -> None:
    """The saga's export keeps the account (never a Message, which leaves
    no line); a player's export, like what their seat is sent, keeps only
    the lines they may read."""
    saga, _session = _blind_and_private()
    ana = viewing.viewer_for(saga.players[0])

    whole = transfer.export_saga_data(saga)["saga"]["sessions"][0]["account"]
    hers = seat_view.seat_view(saga, ana).sessions[0].account

    assert [line["kind"] for line in whole] == ["roll", "roll", "roll"]
    assert [line.audience for line in hers] == [chronicle.CHOSEN, chronicle.TABLE]


def test_a_seat_holds_no_one_elses_player_id() -> None:
    saga, session = _blind_and_private()
    session.account[1].players = ["ana", "ben"]
    ana = viewing.viewer_for(saga.players[0])

    hers = seat_view.seat_view(saga, ana).sessions[0]

    assert [line.players for line in hers.account] == [["ana"], []]
    assert len(evening.for_reader(saga, hers, "ana")) == 2  # still read there


def test_another_storyguide_reads_no_blind_line_of_this_session() -> None:
    """A storyguide who reads every record is still a player at another's
    Session: its Blind lines stay out of their seat and their export."""
    saga, _session = _blind_and_private()
    saga.players.append(Player("cora", "Cora", role=players.STORYGUIDE))
    cora = viewing.viewer_for(saga.players[-1])
    assert viewing.reads_everything(cora, saga)

    hers = seat_view.seat_view(saga, cora).sessions[0].account

    assert [line.audience for line in hers] == [chronicle.TABLE]


def test_a_line_round_trips_through_the_save() -> None:
    line = AccountLine("roll", "Hi", chronicle.CHOSEN, ["ana"], "The ford", True)

    assert AccountLine.from_dict(vars(line)) == line
