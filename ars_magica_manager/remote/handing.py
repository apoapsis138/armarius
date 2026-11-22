"""Handouts to and from Remote seats (protocol 4; handout_list.py,
handout_arrangement.py).

A seat asks for a Player's Handouts with `handouts`: its own Player's, or
any Player's from a storyguide's seat, worked out by the host from every
Session's Chronicle, since a seat holds only tonight's. `search_handouts`
finds which of them hold some words, looking through their copies here,
so the copies' words never travel with the list. A Player's own
arrangement (titles, pins, folders) is read with `handout_arrangement` and
changed with `arrange_handouts`, by that Player's seat alone; the host
keeps it. A Handout's copy comes by `show_copy` (showing.py), by its
Show's id, on a Show's terms.

Pattern: Remote Proxy: each verb a seat's Table asks for is carried out
here, under the host's own rules."""

from __future__ import annotations

import json
import time
from collections.abc import Callable

from .. import handout_arrangement, handout_list, storage
from .limits import RateLimiter
from .protocol import Body, Field, MessageSpec, Refused, Reply, Session
from .records import in_parts

#: Lists, searches and arrangements one seat may ask for in a minute: each
#: reads the Chronicles (a search, the copies too).
READS_PER_MINUTE = 30
#: Changes to its Handouts' arrangement one seat may make in a minute.
ARRANGES_PER_MINUTE = 60
#: The longest Player id a seat may name.
PLAYER_ID_MAX = 64
#: The longest search a seat may send.
WORDS_MAX = 200

_TOO_MANY = "Too many asked for: wait a minute."


def handout_specs(
    saga_id: str, clock: Callable[[], float] = time.monotonic
) -> list[MessageSpec]:
    """`handouts`, `search_handouts`, `handout_arrangement` and
    `arrange_handouts`, for a signed-in seat."""
    reads = RateLimiter(READS_PER_MINUTE, 60.0, clock)
    arranging = RateLimiter(ARRANGES_PER_MINUTE, 60.0, clock)

    def handouts(session: Session, body: Body) -> Reply:
        """A Player's Handouts, worked out here from the Chronicles."""
        player_id = str(body["player"])
        if not reads.allow(session.device_id or session.player_id):
            return Reply("show_refused", {"why": _TOO_MANY})
        try:
            saga = storage.load_saga(saga_id)
        except OSError, ValueError:
            raise Refused from None
        if not handout_list.readable(saga, player_id, session.player_id):
            return Reply("show_refused", {"why": handout_list.NOT_YOURS})
        found = handout_list.to_data(handout_list.of_player(saga, player_id))
        blob = json.dumps(found, ensure_ascii=False).encode()
        return in_parts("handouts", blob, {"player": player_id})

    def search(session: Session, body: Body) -> Reply:
        """Which of a Player's Handouts hold the words, from their copies."""
        player_id = str(body["player"])
        if not reads.allow(session.device_id or session.player_id):
            return Reply("show_refused", {"why": _TOO_MANY})
        try:
            saga = storage.load_saga(saga_id)
        except OSError, ValueError:
            raise Refused from None
        if not handout_list.readable(saga, player_id, session.player_id):
            return Reply("show_refused", {"why": handout_list.NOT_YOURS})
        found = sorted(handout_list.matching(saga, player_id, str(body["words"])))
        return Reply("handouts_found", {"keys": "\n".join(found)})

    def arrangement(session: Session, body: Body) -> Reply:
        """A Player's own arrangement, to that Player's seat alone."""
        player_id = str(body["player"])
        if not reads.allow(session.device_id or session.player_id):
            return Reply("show_refused", {"why": _TOO_MANY})
        try:
            found = handout_arrangement.arrangement_of(
                saga_id, player_id, session.player_id
            )
        except ValueError:  # a saga id no folder could be named by
            raise Refused from None
        if isinstance(found, str):
            return Reply("show_refused", {"why": found})
        blob = json.dumps(handout_arrangement.to_data(found), ensure_ascii=False)
        return in_parts("handout_arrangement", blob.encode(), {"player": player_id})

    def arrange(session: Session, body: Body) -> Reply:
        """One change to a Player's own arrangement, from that Player's
        seat alone, carried out here (handout_arrangement.arrange)."""
        if not arranging.allow(session.device_id or session.player_id):
            return Reply("show_refused", {"why": "Too many changes: wait a minute."})
        try:
            saga = storage.load_saga(saga_id)
        except OSError, ValueError:
            return Reply("show_refused", {"why": "The saga can't be read just now."})
        pinned = body.get("pinned")
        call = handout_arrangement.Arrange(
            str(body["key"]),
            title=str(body["title"]) if "title" in body else None,
            pinned=pinned if isinstance(pinned, bool) else None,
            folder=str(body["folder"]) if "folder" in body else None,
        )
        why = handout_arrangement.arrange(
            saga, str(body["player"]), call, by=session.player_id
        )
        return Reply("show_refused", {"why": why}) if why else Reply("arranged", {})

    player = Field(str, max_length=PLAYER_ID_MAX)
    return [
        MessageSpec("handouts", {"player": player}, handouts),
        MessageSpec(
            "search_handouts",
            {"player": player, "words": Field(str, max_length=WORDS_MAX)},
            search,
        ),
        MessageSpec("handout_arrangement", {"player": player}, arrangement),
        MessageSpec(
            "arrange_handouts",
            {
                "player": player,
                "key": Field(str, max_length=600),
                # Each given changes its own; "" puts back the shown title,
                # or takes the Handout out of its folder.
                "title": Field(
                    str, max_length=handout_arrangement.MOST_TITLE, required=False
                ),
                "pinned": Field(bool, required=False),
                "folder": Field(
                    str, max_length=handout_arrangement.MOST_FOLDER, required=False
                ),
            },
            arrange,
        ),
    ]
