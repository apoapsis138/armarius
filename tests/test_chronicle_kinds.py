"""Every kind of Chronicle entry held to the same rules: a ratchet over
chronicle.KINDS, as test_more_action_registered.py is over the More menu.
Each kind says which keys of its body hold typed text, or why none do;
each declares its body's type, and every key it writes; and an entry of
any kind whose body is damaged (a key missing, a value of the wrong type)
is passed over by every reader, never breaking one."""

from __future__ import annotations

import typing

import pytest
from chronicle_support import HOST, begun, every_kind, whole
from chronicle_support import evening_with_damage as _evening
from chronicle_support import written as _written

from ars_magica_manager import chronicle, handout_list, scene_play, shows
from ars_magica_manager.models import Saga, Session
from ars_magica_manager.remote import events

PEOPLE = (HOST, "ana", "ben")


# -- what each kind declares --


def test_every_kind_names_its_typed_text_or_says_why_it_has_none() -> None:
    for name, spec in chronicle.KINDS.items():
        assert bool(spec.typed) != bool(spec.untyped), name
    assert set(chronicle.TYPED) | set(chronicle.UNTYPED) == set(chronicle.KINDS)
    assert not set(chronicle.TYPED) & set(chronicle.UNTYPED)


def test_every_kinds_typed_keys_are_in_its_body() -> None:
    for name, spec in chronicle.KINDS.items():
        keys = typing.get_type_hints(spec.body)
        assert all(key in keys for key in spec.typed), name


def test_a_kind_must_say_its_body() -> None:
    with pytest.raises(TypeError):
        chronicle.Kind(  # type: ignore[call-arg]
            "handout",
            lambda _body: "A handout.",
            for_whom=chronicle.for_whom,
            held_back=(),
            account=lambda _entry, _book: None,
        )


def test_no_kind_is_named_as_a_damaged_entry_is() -> None:
    assert chronicle.DAMAGED not in chronicle.KINDS


def test_every_key_a_kind_writes_is_declared_and_a_seat_gets_a_whole_body() -> None:
    """One of each kind, as written and as a seat is sent it (less what
    the kind holds back), fits the kind's body."""
    saga, session, book = begun()
    every_kind(saga, session, book)

    for entry in book.entries:
        keys = typing.get_type_hints(chronicle.KINDS[entry.kind].body)
        assert set(entry.body) <= set(keys), entry.kind
        assert chronicle.body_problem(entry.kind, entry.body) is None, entry.kind
        sent = chronicle.stamped(entry, "ana", session, saga)
        assert chronicle.body_problem(entry.kind, sent.body) is None, entry.kind


def test_the_chronicle_never_writes_a_body_of_the_wrong_shape() -> None:
    *_, book = begun()

    with pytest.raises(ValueError, match="outcome entry of the wrong shape: request"):
        book.add(chronicle.OUTCOME, HOST, chronicle.table(), {"text": "It gives."})
    assert [e.kind for e in book.entries] == [chronicle.BEGIN]


def test_nor_an_entry_written_with_another_of_the_wrong_shape() -> None:
    """The entry that belongs with another (`then`: a Blind roll's line, a
    Roll request's kept Ease Factor) is held to its kind's body too."""
    *_, book = begun()

    def kept(entry: chronicle.Entry) -> chronicle.Written:
        return (chronicle.REQUEST_EASE, HOST, chronicle.storyguide_only(), {})

    with pytest.raises(ValueError, match="request_ease entry of the wrong shape"):
        book.add(
            chronicle.OUTCOME,
            HOST,
            chronicle.table(),
            {"request": 1, "text": "It gives."},
            then=kept,
        )
    assert chronicle.REQUEST_EASE not in [e.kind for e in book.entries]


def test_writing_checks_only_the_entries_new_since_the_file_was_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Each entry written catches up with the file first; what was checked
    when it was read isn't checked again (a long Session would else check
    every earlier entry with each one written)."""
    saga, session, book = begun()
    for number in range(20):
        chronicle.message(book, saga, session, f"Line {number}.", by="ben")
    checked: list[str] = []
    real = chronicle.body_problem

    def counted(kind: str, body: dict[str, object]) -> str | None:
        checked.append(kind)
        return real(kind, body)

    monkeypatch.setattr(chronicle, "body_problem", counted)

    chronicle.message(book, saga, session, "One more.", by="ben")

    assert checked == [chronicle.MESSAGE]


# -- a damaged entry of each kind --


def _sent(saga: Saga, session: Session, who: str) -> chronicle.SeatChronicle:
    """What `who`'s seat holds: the host's feed, through the wire's frames."""
    held = chronicle.SeatChronicle()
    found = chronicle.feed(saga, who, session.id, 0)
    assert found is not None
    for entry in found.entries:
        held.take(*events.entry_of(events.frame(found.session_id, entry).body))
    return held


def _as_read(reader: chronicle.Reader) -> list[object]:
    """Everything `reader` gives of its book: each entry read, its line and
    whether it calls the pane, and each Roll request's answers."""
    struck = chronicle.voided(reader.book)
    said: list[object] = []
    for entry in reader.entries():
        said.append((entry.number, chronicle.line(entry, struck)))
        said.append(reader.calls_attention(entry))
        if entry.kind == chronicle.REQUEST:
            said.append(reader.kept_ease(entry))
            said.append(reader.answer_result(entry, "aelfric"))
            said.append(reader.may_answer(entry, "aelfric"))
    return said


def _everything_read(saga: Saga, session: Session) -> list[object]:
    """What every reader of the Chronicle gives, from its file as it
    stands: each person's own, at the host and at a seat, Read the
    Chronicle's text, the Scenes' moves, Confidence spent, the Shows and
    each Player's Handouts."""
    chronicle.forget_open()
    book = chronicle.read(saga, session)
    said: list[object] = []
    for who in PEOPLE:
        said += _as_read(chronicle.Reader(book, who, session, saga))
        said += _as_read(
            chronicle.Reader(_sent(saga, session, who), who, session, saga)
        )
        said.append(
            chronicle.text(chronicle.for_reader(book, who, session, saga), book)
        )
        said.append(handout_list.of_player(saga, who))
        said.append(shows.seen(saga, "x", who))
    said.append(shows.withdrawn(book))
    said.append([(s.id, e.number, gone) for s, e, gone in shows.every_show(saga)])
    said.append(scene_play.moves(book.entries))
    said.append(scene_play.banner_playing(book.entries))
    said.append(chronicle.confidence_spent(book, "aelfric"))
    return said


def test_every_reader_passes_over_a_damaged_entry_of_any_kind() -> None:
    """The same Chronicle file read with every damaged variant of every
    kind in it, and with only those still whole: every reader gives the
    same, and none breaks."""
    saga, session, book, variants = _evening()
    assert len(variants) > len(whole(variants))  # some are damaged

    _written(saga, session, book, whole(variants))
    expected = _everything_read(saga, session)
    _written(saga, session, book, variants)

    assert _everything_read(saga, session) == expected


def test_a_damaged_entry_is_held_by_its_number_and_read_by_no_one() -> None:
    saga, session, book, variants = _evening()
    _written(saga, session, book, variants)

    held = chronicle.read(saga, session).entries
    damaged = [e for e in held if e.kind == chronicle.DAMAGED]
    assert [e.number for e in held] == list(range(1, len(held) + 1))
    assert len(damaged) == len(variants) - len(whole(variants))
    assert not any(chronicle.sees(e, HOST, session, saga) for e in damaged)


def test_a_seat_passes_over_a_damaged_entry_its_host_sends() -> None:
    """A seat checks what its host sends as the host checks its file: an
    entry whose body isn't its kind's is read by no one there either."""
    saga, session, book, variants = _evening()

    def seat(extra: list[chronicle.Entry]) -> list[object]:
        held = chronicle.SeatChronicle()
        for entry in [*book.entries, *extra]:
            held.take(*events.entry_of(events.frame(session.id, entry).body))
        return _as_read(chronicle.Reader(held, "ana", session, saga))

    assert seat(variants) == seat(whole(variants))
