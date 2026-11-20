"""The Chronicle sent to Remote seats, over real connections (protocol 2,
remote/events.py; ADR 0019): each seat is sent only what its Player may
see, catches up from the last entry it holds, rolls through the host, and
an older seat is told to update."""

from __future__ import annotations

import asyncio
import json
import random
from collections.abc import AsyncIterator
from pathlib import Path

import pytest
import pytest_asyncio

from ars_magica_manager import chronicle, players, references, storage, viewing
from ars_magica_manager.models import (
    Ability,
    Casting,
    Character,
    Characteristics,
    Neighbour,
    Saga,
    Session,
)
from ars_magica_manager.remote import events, protocol
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote.client import (
    MessageRefused,
    RemoteClient,
    RollRefused,
    new_device_secret,
)
from ars_magica_manager.remote.events import ROLLS_PER_MINUTE
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.invites import InviteBook, book_path
from ars_magica_manager.remote.passcodes import RemotePasscodes, passcodes_path
from ars_magica_manager.remote.plan import identity_name
from ars_magica_manager.remote.serve import build
from ars_magica_manager.remote.vault import DeviceVault

PASSCODE = "a long enough passcode"
HOST = viewing.HOST


class Faces(random.Random):
    def __init__(self, *faces: int) -> None:
        super().__init__()
        self.faces = list(faces)

    def randrange(self, *_args: object, **_kwargs: object) -> int:  # type: ignore[override]
        return self.faces.pop(0)


def _saga() -> Saga:
    """Anna plays Aelfric and Bea plays Brigit tonight."""
    saga = Saga(id="fengheld", name="Fengheld")
    anna = players.add(
        saga, {"name": "Anna", "role": players.PLAYER, "passcode": PASSCODE}
    )
    bea = players.add(
        saga, {"name": "Bea", "role": players.PLAYER, "passcode": PASSCODE}
    )
    saga.characters = [
        Character(id="aelfric", name="Aelfric", type="magus"),
        Character(id="brigit", name="Brigit", type="companion"),
    ]
    saga.sessions = [
        Session(
            "s1",
            castings=[
                Casting(player_id=anna.id, character_id="aelfric"),
                Casting(player_id=bea.id, character_id="brigit"),
            ],
        )
    ]
    return saga


class Table:
    """The saga hosted by the real listener, the Session begun in the
    window (this process), and two seats to sign in."""

    def __init__(self) -> None:
        self.saga = _saga()
        for player in self.saga.players:
            RemotePasscodes(passcodes_path(self.saga.name)).note(player, PASSCODE)
        self.book = chronicle.begin(self.saga, self.saga.sessions[0], by=HOST)
        storage.save_saga(self.saga)
        self.store = ident.MemoryStore()
        self.host, _devices = build(self.saga.id, store=self.store)
        self.host._events_every = 0.05  # look often, so the tests are quick
        self.pin = ident.load_or_create(self.store, identity_name(self.saga.id)).pin
        self.invites = InviteBook(book_path(self.saga.name))
        self.vaults: dict[str, DeviceVault] = {}
        self.port = 0

    def id_of(self, name: str) -> str:
        found = players.find(self.saga, name)
        assert found is not None
        return found.id

    async def client(self) -> RemoteClient:
        return await RemoteClient.connect(f"ws://127.0.0.1:{self.port}{PATH}", self.pin)

    async def seat(self, name: str) -> RemoteClient:
        """A signed-in connection for `name`, approved the first time."""
        if name not in self.vaults:
            vault = self.vaults[name] = DeviceVault(ident.MemoryStore())
            secret = new_device_secret()
            async with await self.client() as client:
                await client.redeem(
                    self.invites.issue(self.id_of(name)), name, secret, vault
                )
                self.invites.approve(self.invites.pending()[0].id)
                await client.request_status(secret, vault)
        client = await self.client()
        await client.sign_in(PASSCODE, self.vaults[name])
        return client

    def roll(self, **asked: object) -> None:
        request = chronicle.RollRequest(**asked)  # type: ignore[arg-type]
        chronicle.free_roll(
            self.book, self.saga, self.saga.sessions[0], request, by=HOST, rng=Faces(5)
        )


@pytest_asyncio.fixture
async def table() -> AsyncIterator[Table]:
    found = Table()
    found.port = await found.host.start()
    yield found
    await found.host.stop()


async def _gather(
    client: RemoteClient, since: int, count: int, session_id: str = ""
) -> list[tuple[str, chronicle.Entry]]:
    """The first `count` events after `since`; fewer if no more come."""
    got: list[tuple[str, chronicle.Entry]] = []
    stream = client.events(since, session_id)
    try:
        while len(got) < count:
            got.append(await asyncio.wait_for(anext(stream), timeout=2))
    except TimeoutError:
        pass
    return got


async def test_a_seat_is_sent_what_is_already_there_and_what_comes(
    table: Table,
) -> None:
    table.roll(modifier=3, for_what="The weather")
    seat = await table.seat("Anna")
    try:
        stream = seat.events(0)
        first = [await asyncio.wait_for(anext(stream), 2) for _ in range(2)]
        table.roll(modifier=4)
        later = await asyncio.wait_for(anext(stream), 2)
    finally:
        await seat.close()

    assert [(s, e.kind, e.number) for s, e in first] == [
        ("s1", "begin", 1),
        ("s1", "roll", 2),
    ]
    assert first[1][1].body["faces"] == [5] and first[1][1].body["total"] == 8
    assert later[1].number == 3


async def test_a_private_or_blind_marker_never_reaches_another_seat(
    table: Table,
) -> None:
    """ADR 0019: who may see an entry is decided at the host; an entry a
    seat may not see is never sent to it."""
    anna_id = table.id_of("Anna")
    roller = await table.seat("Anna")
    try:
        await roller.roll(
            chronicle.RollRequest(
                character_id="aelfric",
                visibility=chronicle.PRIVATE,
                for_what="MARKER-PRIVATE",
            )
        )
    finally:
        await roller.close()
    table.roll(
        character_id="brigit", visibility=chronicle.BLIND, for_what="MARKER-BLIND"
    )
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        for_anna = await _gather(anna, 0, 10)
        for_bea = await _gather(bea, 0, 10)
    finally:
        await anna.close()
        await bea.close()

    seen_by_bea = repr([(e.kind, e.body) for _s, e in for_bea])
    assert "MARKER-PRIVATE" not in seen_by_bea
    assert [e.kind for _s, e in for_bea] == ["begin", "rolled"]
    assert "total" not in for_bea[-1][1].body  # Bea learns only that it was rolled
    seen_by_anna = repr([(e.kind, e.body, e.author) for _s, e in for_anna])
    assert "MARKER-BLIND" not in seen_by_anna
    assert [e.kind for _s, e in for_anna] == ["begin", "roll"]
    assert for_anna[-1][1].author == anna_id


async def test_each_seat_is_told_for_you_on_exactly_its_entries(table: Table) -> None:
    """The host works "for you" out for each seat it sends to (ADR 0031):
    live and on catching up after a drop, through the one stamp."""
    anna_id, bea_id = table.id_of("Anna"), table.id_of("Bea")
    session = table.saga.sessions[0]
    table.roll(character_id="aelfric", visibility=chronicle.BLIND)  # 2, 3
    chronicle.message(
        table.book, table.saga, session, "Psst.", to=(anna_id,), by=bea_id
    )  # 4
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        anna_stream, bea_stream = anna.events(0), bea.events(0)
        caught_up_anna = [
            await asyncio.wait_for(anext(anna_stream), 2) for _ in range(3)
        ]
        caught_up_bea = [await asyncio.wait_for(anext(bea_stream), 2) for _ in range(2)]
        call = chronicle.RollCall(
            ("brigit",), "Perception", visibility=chronicle.PUBLIC
        )
        chronicle.request_rolls(table.book, table.saga, session, call, by=HOST)  # 5
        live_anna = await asyncio.wait_for(anext(anna_stream), 2)
        live_bea = await asyncio.wait_for(anext(bea_stream), 2)
    finally:
        await anna.close()
        await bea.close()

    def told(got: list[tuple[str, chronicle.Entry]]) -> list[tuple[int, bool | None]]:
        return [(e.number, e.for_you) for _s, e in got]

    assert told([*caught_up_anna, live_anna]) == [
        (1, False),
        (3, True),  # the line that the storyguide rolled for Aelfric
        (4, True),  # Bea's Whisper to her
        (5, False),
    ]
    assert told([*caught_up_bea, live_bea]) == [
        (1, False),
        (4, False),  # her own Whisper is not for her
        (5, True),  # a Roll request offered to Brigit
    ]


async def test_a_whisper_reaches_its_seats_without_any_players_id(
    table: Table,
) -> None:
    """A seat is told only whether an entry is for it, never who else it
    is for (ADR 0031): a Whisper keeps its recipients' names, which its card
    shows, and leaves their Player ids at the host."""
    anna_id, bea_id = table.id_of("Anna"), table.id_of("Bea")
    session = table.saga.sessions[0]
    chronicle.message(
        table.book, table.saga, session, "Both of you.", to=(anna_id, bea_id), by=HOST
    )
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        for_anna = await _gather(anna, 1, 1)
        for_bea = await _gather(bea, 1, 1)
    finally:
        await anna.close()
        await bea.close()

    for got in (for_anna, for_bea):
        whisper = got[0][1]
        sent = json.dumps(whisper.body)
        assert anna_id not in sent and bea_id not in sent
        assert "to" not in whisper.body
        assert whisper.body["to_names"] == ["Anna", "Bea"]
        assert whisper.for_you is True
    chronicle.forget_open()
    on_file = chronicle.read(table.saga, session).entries[-1]
    assert on_file.body["to"] == [anna_id, bea_id]  # the host keeps them


async def test_a_players_whisper_sends_no_recipients_id_to_any_seat(
    table: Table,
) -> None:
    """Anna Whispers to Bea from her seat: neither seat's frame names Bea
    by id anywhere. The author (Anna, whose name the card shows) travels,
    as every entry's does: Player ids are not secrets (threat model)."""
    anna_id, bea_id = table.id_of("Anna"), table.id_of("Bea")
    anna = await table.seat("Anna")
    try:
        number = await anna.say("Psst.", to=(bea_id,))
    finally:
        await anna.close()
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        for_anna = await _gather(anna, number - 1, 1)
        for_bea = await _gather(bea, number - 1, 1)
    finally:
        await anna.close()
        await bea.close()

    for got in (for_anna, for_bea):
        whisper = got[0][1]
        assert whisper.number == number and whisper.author == anna_id
        assert bea_id not in repr((whisper.audience, whisper.body))
        assert whisper.body["to_names"] == ["Bea"]
    assert [got[0][1].for_you for got in (for_anna, for_bea)] == [False, True]


async def test_a_seat_that_reconnects_catches_up_from_what_it_holds(
    table: Table,
) -> None:
    held = chronicle.SeatChronicle()
    seat = await table.seat("Anna")
    try:
        for session_id, entry in await _gather(seat, 0, 1):
            held.take(session_id, entry)
    finally:
        await seat.close()
    table.roll(modifier=1)
    table.roll(modifier=2)

    again = await table.seat("Anna")
    try:
        for session_id, entry in await _gather(again, held.last, 5, held.session_id):
            held.take(session_id, entry)
    finally:
        await again.close()

    assert [e.number for e in held.entries] == [1, 2, 3]


async def test_a_seat_rolls_only_for_its_character_tonight(table: Table) -> None:
    seat = await table.seat("Anna")
    try:
        number = await seat.roll(chronicle.RollRequest(character_id="aelfric"))
        with pytest.raises(RollRefused) as refused:
            await seat.roll(chronicle.RollRequest(character_id="brigit"))
        with pytest.raises(RollRefused):
            await seat.roll(
                chronicle.RollRequest(
                    character_id="aelfric", visibility=chronicle.BLIND
                )
            )
    finally:
        await seat.close()

    assert number == 2
    assert refused.value.why == "Roll for a character you play tonight."
    entry = chronicle.read(table.saga, table.saga.sessions[0]).refresh()[-1]
    assert entry.author == table.id_of("Anna") and entry.kind == "roll"


async def test_rolls_are_limited_per_seat(table: Table) -> None:
    seat = await table.seat("Anna")
    asked = chronicle.RollRequest(character_id="aelfric")
    try:
        for _ in range(ROLLS_PER_MINUTE):
            await seat.roll(asked)
        with pytest.raises(RollRefused) as refused:
            await seat.roll(asked)
    finally:
        await seat.close()

    assert refused.value.why == "Too many rolls: wait a minute."


async def test_an_entry_of_a_kind_the_seat_doesnt_know_still_arrives(
    table: Table,
) -> None:
    table.book.add("handout", HOST, chronicle.table(), {"picture": "map.png"})
    seat = await table.seat("Anna")
    try:
        got = await _gather(seat, 1, 1)
    finally:
        await seat.close()

    entry = got[0][1]
    assert entry.kind == "handout"
    assert chronicle.text([entry], chronicle.Chronicle(table.book.path, [entry]))
    assert chronicle.UNKNOWN in chronicle.text(
        [entry], chronicle.Chronicle(table.book.path, [entry])
    )


async def test_a_seat_speaking_protocol_1_is_told_to_update(table: Table) -> None:
    async with await table.client() as client:
        reply = await client.request("hello", {"protocol": 1})

    assert reply.type == protocol.UPDATE
    assert reply.body["message"] == protocol.UPDATE_MESSAGE


async def test_no_events_before_a_session_is_under_way(table: Table) -> None:
    chronicle.end(table.saga, table.saga.sessions[0], by=HOST)
    storage.save_saga(table.saga)
    seat = await table.seat("Anna")
    try:
        assert await _gather(seat, 0, 1) == []
    finally:
        await seat.close()


def test_an_entry_too_large_to_send_whole_goes_as_one_the_seat_cant_show() -> None:
    entry = chronicle.Entry(4, "", "show", HOST, chronicle.table(), {"x": "y" * 9000})

    found = events.frame("s1", entry)

    assert found.body["kind"] == events.TOO_LARGE and found.body["body"] == "{}"
    _session, back = events.entry_of(found.body)
    assert chronicle.UNKNOWN in chronicle.text(
        [back], chronicle.Chronicle(Path("x"), [])
    )


async def test_a_seat_rolls_from_the_sheet_with_the_hosts_scores(table: Table) -> None:
    aelfric = table.saga.characters[0]
    aelfric.characteristics = Characteristics(dexterity=2)
    aelfric.abilities = [Ability("Athletics", xp=30, specialty="climbing")]
    aelfric.background.confidence_score = 1
    aelfric.background.confidence_points = 2
    storage.save_saga(table.saga)
    seat = await table.seat("Anna")
    try:
        number = await seat.roll(
            chronicle.RollRequest(
                character_id="aelfric",
                sheet=chronicle.SheetRoll("Dexterity", "Athletics", specialty=True),
            )
        )
        spent = await seat.confidence(number, 1)
        with pytest.raises(RollRefused) as refused:
            await seat.confidence(number, 1)
    finally:
        await seat.close()

    entries = chronicle.read(table.saga, table.saga.sessions[0]).refresh()
    roll = next(e for e in entries if e.number == number)
    assert chronicle.terms_of(roll.body) == [
        ("Dexterity", 2),
        ("Athletics", 3),
        ("Specialty (climbing)", 1),
    ]
    confidence = next(e for e in entries if e.number == spent)
    assert confidence.kind == chronicle.CONFIDENCE
    assert confidence.body["total"] == roll.body["total"] + 3
    assert refused.value.why == "At most 1 on one roll (the Confidence Score)."


async def test_a_seat_answers_a_request_and_never_learns_a_hidden_ease(
    table: Table,
) -> None:
    session = table.saga.sessions[0]
    request = chronicle.request_rolls(
        table.book,
        table.saga,
        session,
        chronicle.RollCall(
            characters=("aelfric", "brigit"),
            characteristic="Perception",
            ease_factor=17,
            hide_ease=True,
            visibility=chronicle.PRIVATE,
        ),
        by=HOST,
    )
    anna = await table.seat("Anna")
    try:
        number = await anna.answer(request.number, "aelfric", False)
        with pytest.raises(RollRefused) as refused:
            await anna.answer(request.number, "brigit", False)
    finally:
        await anna.close()
    watcher = await table.seat("Anna")
    try:
        frames = await _gather(watcher, 0, 10)
    finally:
        await watcher.close()

    assert refused.value.why == "Another Player rolls for that character."
    kinds = [e.kind for _s, e in frames]
    assert chronicle.REQUEST_EASE not in kinds
    assert all(e.body.get("ease_factor") is None for _s, e in frames)
    assert all("17" not in str(e.body) for _s, e in frames)
    assert number in [e.number for _s, e in frames]


async def test_a_seat_sends_a_message_the_host_writes(table: Table) -> None:
    seat = await table.seat("Anna")
    try:
        number = await seat.say("We ride at dawn.")
    finally:
        await seat.close()

    entry = chronicle.read(table.saga, table.saga.sessions[0]).refresh()[-1]
    assert entry.number == number and entry.kind == chronicle.MESSAGE
    assert entry.author == table.id_of("Anna")
    assert entry.body["words"] == "We ride at dawn."


async def test_a_whisper_marker_never_reaches_another_seat(table: Table) -> None:
    """ADR 0019: a Whisper goes only to those it names and the storyguide."""
    anna = await table.seat("Anna")
    try:
        await anna.say("MARKER-WHISPER", to=(HOST,))
    finally:
        await anna.close()
    bea = await table.seat("Bea")
    try:
        for_bea = await _gather(bea, 0, 10)
    finally:
        await bea.close()

    assert "MARKER-WHISPER" not in repr([(e.kind, e.body) for _s, e in for_bea])
    assert [e.kind for _s, e in for_bea] == ["begin"]


async def test_a_seats_message_is_refused_with_why(table: Table) -> None:
    seat = await table.seat("Anna")
    try:
        with pytest.raises(MessageRefused) as refused:
            await seat.say(f"Huzzah {chr(0x1F389)}")
    finally:
        await seat.close()

    assert "Emoji" in refused.value.why


async def test_a_link_renamed_on_the_host_is_refused_with_its_new_name(
    table: Table,
) -> None:
    table.saga.neighbours = [Neighbour(id="abbey", name="Abbey of St Gall")]
    storage.save_saga(table.saga)
    stale = references.Ref("neighbours", "abbey", "St Gall")
    seat = await table.seat("Anna")
    try:
        with pytest.raises(MessageRefused) as refused:
            await seat.say("To St Gall!", links=(stale,))
    finally:
        await seat.close()

    assert (
        refused.value.why
        == "St Gall is now Abbey of St Gall on the host: link it again."
    )


async def test_a_seats_form_roll_with_hidden_characters_is_refused_and_its_dice_kept(
    table: Table,
) -> None:
    hidden = chr(0x202E)
    seat = await table.seat("Anna")
    try:
        named = await seat.request(
            "form_die",
            {
                "form": f"Aegis{hidden}",
                "character_id": "aelfric",
                "visibility": chronicle.PUBLIC,
                "start": 0,
                "stop": 10,
                "step": 1,
            },
        )
        drawn = await seat.request(
            "form_die",
            {
                "form": "Personality Trait",
                "character_id": "aelfric",
                "visibility": chronicle.PUBLIC,
                "start": 0,
                "stop": 10,
                "step": 1,
            },
        )
        done = await seat.request("form_done", {"lines": f"Brave{hidden} holds."})
    finally:
        await seat.close()

    assert named.type == "roll_refused" and "Invisible" in str(named.body["why"])
    assert drawn.type == "die"
    assert done.type == "roll_refused" and "Invisible" in str(done.body["why"])
    last = chronicle.read(table.saga, table.saga.sessions[0]).refresh()[-1]
    assert last.kind == chronicle.FORM_ROLL and last.body["cancelled"]
