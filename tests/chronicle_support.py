"""A Session's Chronicle for tests: a begun Session with Ana and Ben at the
table, one entry of each kind the Chronicle writes, and damaged entries of
each kind."""

from __future__ import annotations

import json
import random
import typing
from dataclasses import asdict, replace
from typing import Any

from ars_magica_manager import chronicle, shapes, viewing
from ars_magica_manager.models import Casting, Character, Player, Saga, Session

HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def begun() -> tuple[Saga, Session, chronicle.Chronicle]:
    saga = Saga(id="fengheld", name="Fengheld")
    saga.players = [Player("ana", "Ana"), Player("ben", "Ben")]
    saga.characters = [Character(id="aelfric", name="Aelfric", type="magus")]
    session = Session("s1", castings=[Casting(player_id="ana", character_id="aelfric")])
    saga.sessions = [session]
    # A new Chronicle, though one test may begin the Session more than once.
    chronicle.forget_open()
    chronicle.path_of(saga, session).unlink(missing_ok=True)
    return saga, session, chronicle.begin(saga, session, by=HOST)


def blind(saga: Saga, session: Session, book: chronicle.Chronicle) -> None:
    request = chronicle.RollRequest(
        character_id="aelfric", visibility=chronicle.BLIND, for_what="Ambush"
    )
    chronicle.free_roll(book, saga, session, request, by=HOST, rng=Faces(5))


def every_kind(saga: Saga, session: Session, book: chronicle.Chronicle) -> None:
    """One entry of each kind the Chronicle writes, with Ana and Ben at the
    table: a Blind roll for Ana's character (and its line for her), a
    Private and a Table roll, a form's roll, a Roll request to Ana's
    character with its Ease Factor kept and her Blind answer (and its
    line), a Strike, a Confidence spend, an
    outcome, a Message to the Table, Whispers each way, a Show to Ana and
    its withdrawal, a Scene set and ended, and the end."""
    blind(saga, session, book)
    rolled = chronicle.RollRequest(character_id="aelfric", visibility=chronicle.PRIVATE)
    chronicle.free_roll(book, saga, session, rolled, by="ana", rng=Faces(3))
    chronicle.free_roll(
        book, saga, session, chronicle.RollRequest(), by=HOST, rng=Faces(2)
    )
    chronicle.form_roll(
        book,
        saga,
        session,
        form="Aging",
        character_id="",
        visibility=chronicle.BLIND,
        faces=[4],
        lines=["No aging crisis."],
        by=HOST,
        whole_dice=[{"face": 4}],
    )
    call = chronicle.RollCall(("aelfric",), "Perception", ease_factor=6, hide_ease=True)
    request = chronicle.request_rolls(book, saga, session, call, by=HOST)
    chronicle.answer(
        book, saga, session, request.number, "aelfric", by="ana", rng=Faces(4)
    )
    book.add(chronicle.VOID, HOST, chronicle.table(), {"strikes": 3, "reason": "Typo"})
    spent = {
        "roll": 3,
        "character_id": "aelfric",
        "character_name": "Aelfric",
        "points": 1,
        "total": 6,
        "ease_factor": None,
        "succeeded": None,
        "margin": None,
    }
    book.add(chronicle.CONFIDENCE, "ana", chronicle.table(), spent)
    book.add(
        chronicle.OUTCOME,
        HOST,
        chronicle.table(),
        {"request": request.number, "text": "The door gives."},
    )
    chronicle.message(book, saga, session, "Evening.", by="ben")
    chronicle.message(book, saga, session, "Psst.", to=("ana",), by="ben")
    chronicle.message(book, saga, session, "Hush.", to=("ben",), by=HOST)
    # Every key shows.py writes (a Show needs a saga's record or picture).
    shown = {
        "show": "x",
        "title": "A map",
        "ref": [],
        "picture": "x.png",
        "pictures": [],
        "source": ["maps", "rhine.png"],
        "handout": "",
        "to": ["ana"],
        "to_names": ["Ana"],
        "story": "",
        "story_id": "",
    }
    show = book.add(chronicle.SHOW, HOST, chronicle.chosen("ana"), shown)
    withdrawn = {"withdraws": show.number, "title": "A map"}
    book.add(chronicle.WITHDRAWN, HOST, chronicle.chosen("ana"), withdrawn)
    banner = {"use": "u", "title": "The ford", "place": "A ford"}
    book.add(chronicle.SCENE_SET, HOST, chronicle.table(), banner)
    ended = {"use": "u", "title": "The ford"}
    book.add(chronicle.SCENE_ENDED, HOST, chronicle.table(), ended)
    chronicle.end(saga, session, by=HOST)


# -- damaged entries --

#: Values of the wrong type for a key: the first that its type refuses.
WRONG: tuple[object, ...] = ({"damaged": [1]}, "damaged", 7.5)


def damaged_bodies(entry: chronicle.Entry) -> list[dict[str, Any]]:
    """`entry`'s body with each key in turn left out, then of the wrong
    type (a key that may be left out leaves a body that is still whole)."""
    keys = typing.get_type_hints(chronicle.KINDS[entry.kind].body)
    found: list[dict[str, Any]] = []
    for key in entry.body:
        found.append({k: v for k, v in entry.body.items() if k != key})
        wrong = next(
            (v for v in WRONG if shapes.why_not_fits(v, keys[key]) is not None), None
        )
        if wrong is not None:
            found.append(entry.body | {key: wrong})
    return found


def evening_with_damage() -> tuple[
    Saga, Session, chronicle.Chronicle, list[chronicle.Entry]
]:
    """An evening with one entry of each kind (every_kind), and every
    damaged variant of each, numbered on from its end (not yet on file:
    `written`)."""
    saga, session, book = begun()
    every_kind(saga, session, book)
    first: dict[str, chronicle.Entry] = {}
    for entry in book.entries:
        first.setdefault(entry.kind, entry)
    assert set(first) == set(chronicle.KINDS)
    variants: list[chronicle.Entry] = []
    for entry in first.values():
        for body in damaged_bodies(entry):
            number = len(book.entries) + len(variants) + 1
            variants.append(replace(entry, number=number, body=body))
    return saga, session, book, variants


def line_of(entry: chronicle.Entry) -> str:
    """`entry` as a line of its Chronicle's file."""
    kept = asdict(entry)
    del kept["for_you"]
    return json.dumps(kept, ensure_ascii=False)


def written(
    saga: Saga,
    session: Session,
    book: chronicle.Chronicle,
    extra: list[chronicle.Entry],
) -> None:
    """The evening's file as `book` wrote it, then `extra`, to be read
    afresh."""
    lines = [line_of(e) for e in book.entries] + [line_of(e) for e in extra]
    book.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    chronicle.forget_open()
    assert len(chronicle.read(saga, session).entries) == len(lines)


def whole(entries: list[chronicle.Entry]) -> list[chronicle.Entry]:
    """Those of `entries` whose body is their kind's."""
    return [e for e in entries if chronicle.body_problem(e.kind, e.body) is None]
