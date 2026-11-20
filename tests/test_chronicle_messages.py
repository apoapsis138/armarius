"""Messages and Whispers in a Session's Chronicle (chronicle.py; glossary:
Message, Whisper, Audience): who may send one, to whom, and who sees it."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ars_magica_manager import chronicle, references, shows, viewing
from ars_magica_manager.models import (
    Casting,
    Character,
    Neighbour,
    Player,
    Saga,
    Session,
)
from ars_magica_manager.remote import events

HOST = viewing.HOST


def _begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    """Ana, Ben and Cara are at the Session, Dai is Away; the host runs it."""
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [
        Player("ana", "Ana"),
        Player("ben", "Ben"),
        Player("cara", "Cara"),
        Player("dai", "Dai"),
    ]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    session = Session(
        "s1",
        coming=["ana", "ben", "cara"],
        away=["dai"],
        castings=[Casting(player_id="ana", character_id="aelfric")],
    )
    saga.sessions = [session]
    return saga, session, chronicle.begin(saga, session, by=HOST)


def test_a_message_to_the_table_is_seen_by_everyone_at_the_session() -> None:
    saga, session, book = _begun()

    entry = chronicle.message(book, saga, session, "We ride at dawn.", by="ana")

    assert entry.kind == chronicle.MESSAGE
    assert entry.body["words"] == "We ride at dawn."
    for who in ("ana", "ben", "cara", HOST):
        assert chronicle.sees(entry, who, session, saga)


def test_a_whisper_is_seen_by_its_writer_those_chosen_and_the_storyguide() -> None:
    saga, session, book = _begun()

    entry = chronicle.message(
        book, saga, session, "The abbot lied.", to=("ben",), by="ana"
    )

    assert {
        w
        for w in ("ana", "ben", "cara", HOST)
        if chronicle.sees(entry, w, session, saga)
    } == {"ana", "ben", HOST}
    assert entry.body["author_name"] == "Ana"
    assert entry.body["to_names"] == ["Ben"]


def test_the_storyguide_may_whisper_to_one_player() -> None:
    saga, session, book = _begun()

    entry = chronicle.message(
        book, saga, session, "You hear bells.", to=("cara",), by=HOST
    )

    assert chronicle.sees(entry, "cara", session, saga)
    assert not chronicle.sees(entry, "ana", session, saga)
    assert entry.body["author_name"] == "the storyguide"


def test_a_player_may_whisper_to_the_storyguide_alone() -> None:
    saga, session, book = _begun()

    entry = chronicle.message(
        book, saga, session, "Can I sneak off?", to=(HOST,), by="ben"
    )

    assert {
        w
        for w in ("ana", "ben", "cara", HOST)
        if chronicle.sees(entry, w, session, saga)
    } == {"ben", HOST}


@pytest.mark.parametrize(
    ("words", "to", "who", "why"),
    [
        ("Hello", (), "dai", "Only someone at the Session sends a Message."),
        ("Hello", (), "", "Only someone at the Session sends a Message."),
        ("   ", (), "ana", "Write the Message."),
        ("x" * 2001, (), "ana", "A Message holds at most 2000 characters."),
        ("Hello", ("dai",), "ana", "Whisper only to people at the Session."),
        ("Hello", ("ana",), "ana", "Whisper to someone besides yourself."),
    ],
)
def test_a_message_is_refused_with_why(
    words: str, to: tuple[str, ...], who: str, why: str
) -> None:
    saga, session, book = _begun()

    assert chronicle.why_not_message(saga, session, words, to, who) == why
    with pytest.raises(ValueError, match=why):
        chronicle.message(book, saga, session, words, to=to, by=who)
    assert [e.kind for e in book.entries] == ["begin"]


def test_a_message_with_an_emoji_is_refused() -> None:
    saga, session, _book = _begun()

    problem = chronicle.why_not_message(
        saga, session, f"Huzzah {chr(0x1F389)}", (), "ana"
    )

    assert problem is not None and "Emoji" in problem


def test_no_message_once_the_session_has_ended() -> None:
    saga, session, book = _begun()
    chronicle.end(saga, session, by=HOST)

    with pytest.raises(ValueError, match="closed"):
        chronicle.message(book, saga, session, "Too late", by="ana")


# -- record links --


def _with_neighbours(saga: Saga) -> tuple[Neighbour, Neighbour]:
    """The abbey the players know, and a hidden diabolist they don't."""
    abbey = Neighbour(id="abbey", name="St Gall")
    hidden = Neighbour(id="diabolist", name="Brother Wido")
    hidden.known = False
    saga.neighbours = [abbey, hidden]
    return abbey, hidden


def test_a_reader_gets_a_link_to_a_record_they_may_open() -> None:
    saga, session, book = _begun()
    abbey, _ = _with_neighbours(saga)
    link = references.Ref("neighbours", abbey.id, abbey.name)

    entry = chronicle.message(
        book, saga, session, "We go to St Gall.", links=(link,), by="ana"
    )
    fact = chronicle.message_fact(entry, saga, viewing.viewer_for(saga.players[1]))

    assert fact.value == "We go to St Gall."
    assert fact.refs == (link,)
    assert fact.label == "Ana"


def test_a_record_the_reader_may_not_open_is_the_name_as_written() -> None:
    saga, session, book = _begun()
    _, hidden = _with_neighbours(saga)
    link = references.Ref("neighbours", hidden.id, hidden.name)

    entry = chronicle.message(
        book,
        saga,
        session,
        "Brother Wido watches Ben.",
        to=("ana",),
        links=(link,),
        by=HOST,
    )
    as_ana = chronicle.message_fact(entry, saga, viewing.viewer_for(saga.players[0]))
    as_storyguide = chronicle.message_fact(entry, saga, viewing.STORYGUIDE_VIEWER)

    assert as_ana.value == "Brother Wido watches Ben."
    assert as_ana.refs == ()
    assert as_ana.label == "The storyguide, whispering to Ana"
    assert as_storyguide.refs == (link,)


def test_a_writer_links_only_records_they_may_open_and_name() -> None:
    saga, session, _book = _begun()
    abbey, hidden = _with_neighbours(saga)
    unknown = references.Ref("neighbours", hidden.id, hidden.name)
    unnamed = references.Ref("neighbours", abbey.id, abbey.name)

    assert (
        chronicle.why_not_message(
            saga, session, "Brother Wido!", (), "ana", links=(unknown,)
        )
        == "Link only records you may open."
    )
    assert (
        chronicle.why_not_message(
            saga, session, "To the abbey.", (), "ana", links=(unnamed,)
        )
        == "A linked record's name must be in the Message."
    )
    assert (
        chronicle.why_not_message(
            saga, session, "Brother Wido!", (), HOST, links=(unknown,)
        )
        is None
    )


def test_the_chronicle_text_shows_a_message_and_a_whisper() -> None:
    saga, session, book = _begun()
    chronicle.message(book, saga, session, "We ride at dawn.", by="ana")
    chronicle.message(book, saga, session, "Bring rope.", to=("ben",), by="cara")

    shown = chronicle.text(book.entries, book)

    assert "Ana: We ride at dawn." in shown
    assert "Cara, whispering to Ben: Bring rope." in shown


def test_a_whisper_calls_the_attention_of_those_it_is_to_alone() -> None:
    saga, session, book = _begun()
    whisper = chronicle.message(book, saga, session, "Psst.", to=("ben",), by="ana")
    to_all = chronicle.message(book, saga, session, "Hello all.", by="ana")

    def called(entry: chronicle.Entry, who: str) -> bool:
        return chronicle.calls_attention(entry, who, session, saga)

    assert called(whisper, "ben")
    assert not called(whisper, "ana")  # its writer
    assert not called(whisper, HOST)  # the storyguide sees it, but it isn't to them
    assert not called(to_all, "ben")


def test_a_whisper_calls_attention_at_a_seat_on_the_hosts_word() -> None:
    """A seat's entries come without the Players chosen (ADR 0019), but
    told which are for it (ADR 0031)."""
    saga, session, book = _begun()
    chronicle.message(book, saga, session, "Psst.", to=("ben",), by="ana")

    def called_at_seat(who: str) -> bool:
        found = chronicle.feed(saga, who, session.id, 0)
        assert found is not None
        held = chronicle.SeatChronicle()
        for entry in found.entries:
            held.take(*events.entry_of(events.frame(found.session_id, entry).body))
        reader = chronicle.Reader(held, who, session, saga)
        return reader.calls_attention(held.entries[-1])

    assert called_at_seat("ben")
    assert not called_at_seat("ana")  # its writer


# -- the same rule for every text typed into the Chronicle --

EMOJI = chr(0x1F600)


def test_a_rolls_for_line_takes_no_emoji() -> None:
    saga, session, _book = _begun()
    request = chronicle.RollRequest(for_what=f"Climb {EMOJI}")

    problem = chronicle.why_not_roll(saga, session, request, HOST)

    assert problem is not None and "Emoji" in problem


def test_a_roll_requests_for_line_takes_no_emoji() -> None:
    saga, session, _book = _begun()
    call = chronicle.RollCall(("aelfric",), "Perception", for_what=f"Spot {EMOJI}")

    problem = chronicle.why_not_call(saga, session, call, HOST)

    assert problem is not None and "Emoji" in problem


def test_a_strike_reason_and_an_outcome_take_no_invisible_characters() -> None:
    saga, session, book = _begun()
    roll = chronicle.free_roll(book, saga, session, chronicle.RollRequest(), by=HOST)
    hidden = chr(0x200B)

    with pytest.raises(ValueError, match="Invisible"):
        chronicle.strike(book, session, roll.number, f"wrong{hidden}", by=HOST)
    call = chronicle.RollCall(("aelfric",), "Perception")
    asked = chronicle.request_rolls(book, saga, session, call, by=HOST)
    with pytest.raises(ValueError, match="Invisible"):
        chronicle.note_outcome(book, session, asked.number, f"seen{hidden}", by=HOST)


# -- one check for every text typed into the Chronicle --


@pytest.mark.parametrize(
    ("kind", "key"),
    [(kind, key) for kind, keys in chronicle.TYPED.items() for key in keys],
)
def test_the_chronicle_itself_refuses_typed_text_with_an_emoji(
    kind: str, key: str
) -> None:
    *_, book = _begun()

    with pytest.raises(ValueError, match="Emoji"):
        book.add(kind, HOST, chronicle.table(), {key: f"Huzzah {EMOJI}"})


def test_every_kind_the_chronicle_writes_is_described_once() -> None:
    """Each kind of entry the Chronicle writes has its spec in KINDS (its
    line, its typed words, whether it can be struck, how it is drawn), so
    a new kind can't skip the character rule or show as unknown."""
    source = Path(chronicle.__file__).read_text(encoding="utf-8")
    written = {
        getattr(chronicle, name)
        for pattern in (
            r"\.add\(\s*([A-Z_]+),",  # book.add(KIND, ...)
            r"_write_roll\(\s*book,\s*saga,\s*session,\s*([A-Z_]+),",
            r"\(\s*([A-Z_]+),\s*by,",  # an entry that follows another (then=)
        )
        for name in re.findall(pattern, source)
    }
    # A Show is written beside its copy (shows.py).
    shown = Path(shows.__file__).read_text(encoding="utf-8")
    written |= {
        getattr(chronicle, name)
        for name in re.findall(r"\.add\(\s*chronicle\.([A-Z_]+),", shown)
    }

    assert written == set(chronicle.KINDS)
    assert set(chronicle.TYPED) | chronicle.UNTYPED == set(chronicle.KINDS)
    assert not set(chronicle.TYPED) & chronicle.UNTYPED
    assert all(spec.name == name for name, spec in chronicle.KINDS.items())


def test_the_dice_lines_maths_signs_are_typed_text_the_chronicle_keeps() -> None:
    *_, book = _begun()
    line = f"1 {chr(0x2192)} 4 {chr(0xD7)} 2 {chr(0x2212)} 1"

    entry = book.add(chronicle.OUTCOME, HOST, chronicle.table(), {"text": line})

    assert entry.body["text"] == line


# -- from the review --


def test_a_form_rolls_name_takes_no_invisible_characters() -> None:
    saga, session, book = _begun()
    hidden = chr(0x202E)

    with pytest.raises(ValueError, match="Invisible"):
        chronicle.form_roll(
            book,
            saga,
            session,
            form=f"Aegis{hidden}lived",
            character_id="aelfric",
            visibility=chronicle.BLIND,
            faces=[5],
            lines=["Done."],
            by=HOST,
        )
    assert [e.kind for e in book.entries] == ["begin"]


def test_a_message_too_big_for_a_seat_is_refused() -> None:
    """Quotes double when the entry is sent, so 2,000 characters and twenty
    links can outgrow a seat's frame."""
    saga, session, _book = _begun()
    saga.neighbours = [
        Neighbour(id=f"n{i}", name=f"N{i:02}" + '"' * 95) for i in range(20)
    ]
    links = tuple(references.Ref("neighbours", n.id, n.name) for n in saga.neighbours)
    words = " ".join(n.name for n in saga.neighbours)
    assert len(words) <= chronicle.MESSAGE_LIMIT

    problem = chronicle.why_not_message(saga, session, words, (), HOST, links=links)

    assert problem == "This Message is too long to send to the seats."


def test_a_message_links_at_most_twenty_records_once_each() -> None:
    saga, session, _book = _begun()
    saga.neighbours = [Neighbour(id=f"n{i}", name=f"N{i}") for i in range(21)]
    links = tuple(references.Ref("neighbours", n.id, n.name) for n in saga.neighbours)
    words = " ".join(n.name for n in saga.neighbours)

    assert (
        chronicle.why_not_message(saga, session, words, (), HOST, links=links)
        == "A Message links at most 20 records."
    )
    twice = (links[0], links[0])
    assert (
        chronicle.why_not_message(saga, session, "N0", (), HOST, links=twice)
        == "Link each record once."
    )


def test_a_player_who_runs_the_session_is_at_it_once() -> None:
    saga, session, _book = _begun()
    session.storyguide_id = "ana"

    assert chronicle.at_session(saga, session).count("ana") == 1


def test_links_are_shown_in_the_order_their_names_are_written() -> None:
    saga, session, book = _begun()
    saga.neighbours = [Neighbour(id="abbey", name="St Gall")]
    gall = references.Ref("neighbours", "abbey", "St Gall")
    aelfric = references.Ref("characters", "aelfric", "Aelfric")

    entry = chronicle.message(
        book, saga, session, "Aelfric rides to St Gall.", links=(gall, aelfric), by=HOST
    )
    fact = chronicle.message_fact(entry, saga, viewing.STORYGUIDE_VIEWER)

    assert fact.refs == (aelfric, gall)


def test_someone_with_no_seat_reads_as_the_table() -> None:
    saga, *_ = _begun()

    assert chronicle.viewer_of(saga, "").kind == viewing.TABLE
    assert chronicle.viewer_of(saga, HOST).is_storyguide


def test_a_linked_name_must_be_a_whole_word_in_the_message() -> None:
    saga, session, _book = _begun()
    saga.players.append(Player("x", "X"))
    saga.characters.append(Character(id="ben", name="Ben", type="grog"))
    ben = references.Ref("characters", "ben", "Ben")

    assert (
        chronicle.why_not_message(
            saga, session, "Benedict rides.", (), HOST, links=(ben,)
        )
        == "A linked record's name must be in the Message."
    )
    assert (
        chronicle.why_not_message(saga, session, "Ben rides.", (), HOST, links=(ben,))
        is None
    )
