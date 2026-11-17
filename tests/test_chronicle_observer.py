"""The Chronicle's Observer hook (chronicle.Chronicle.subscribe): a reader
of the Chronicle (a Remote seat's event connection, the desktop pane) is
told of each entry as it is added, and can stop listening."""

from __future__ import annotations

from ars_magica_manager import chronicle, viewing
from ars_magica_manager.models import Saga, Session


def _begun() -> chronicle.Chronicle:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.sessions = [Session("s1")]
    return chronicle.begin(saga, saga.sessions[0], by=viewing.HOST)


def test_a_subscriber_is_told_of_each_entry_added_from_then_on() -> None:
    book = _begun()
    told: list[int] = []

    book.subscribe(lambda entry: told.append(entry.number))
    book.add("note", viewing.HOST, chronicle.table(), {})
    book.add("note", viewing.HOST, chronicle.table(), {})

    assert told == [2, 3]


def test_a_subscriber_that_stops_is_told_nothing_more() -> None:
    book = _begun()
    told: list[int] = []

    stop = book.subscribe(lambda entry: told.append(entry.number))
    book.add("note", viewing.HOST, chronicle.table(), {})
    stop()
    book.add("note", viewing.HOST, chronicle.table(), {})

    assert told == [2]
