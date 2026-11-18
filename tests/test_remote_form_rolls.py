"""A Table roll made from a form at a Remote seat, over real connections
(remote/events.py, table_rolls.py; ADR 0018 as amended): the seat works
the form's rule, but each die it asks for is drawn by the host, one at a
time, and recorded there; the seat sends back only the form's result
line. A seat that drops or cancels after drawing leaves its dice.

Pattern: Remote Proxy. The seat's die source looks like any other; each
face comes from the host."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
import pytest_asyncio
from test_remote_events import PASSCODE, Faces, Table

from ars_magica_manager import chronicle, storage, table_rolls
from ars_magica_manager.remote import protocol
from ars_magica_manager.remote.client import RollRefused
from ars_magica_manager.remote.events import DICE_PER_MINUTE
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.seat_session import SeatSession
from ars_magica_manager.rules import dice

PUBLIC = table_rolls.Opening("Cast a Power", "aelfric", chronicle.PUBLIC)


@pytest.fixture(autouse=True)
def host_faces() -> Iterator[None]:
    """The host's dice show 1, 4, 0, 7, ... in turn."""
    table_rolls.host_source = lambda: Faces(1, 4, 0, 7, 3, 3, 3, 3, 3, 3)
    yield
    table_rolls.host_source = table_rolls.system_source


@pytest_asyncio.fixture
async def table() -> AsyncIterator[Table]:
    found = Table()
    found.port = await found.host.start()
    yield found
    await found.host.stop()


def _form_rolls(table: Table) -> list[chronicle.Entry]:
    book = chronicle.Chronicle(table.book.path, [])
    book.refresh()
    return [e for e in book.entries if e.kind == chronicle.FORM_ROLL]


async def _settled(table: Table, count: int) -> list[chronicle.Entry]:
    """The form rolls on file, once `count` are (the host writes a
    dropped seat's after the connection closes)."""
    for _ in range(100):
        found = _form_rolls(table)
        if len(found) >= count:
            return found
        await asyncio.sleep(0.02)
    return _form_rolls(table)


async def test_each_die_is_drawn_by_the_host_and_written_with_the_result(
    table: Table,
) -> None:
    seat = await table.seat("Anna")
    try:
        faces = [await seat.form_die(PUBLIC, 0, 10) for _ in range(2)]
        number = await seat.form_done(["Cast a Power: 8 against 6, it works."])
    finally:
        await seat.close()

    [entry] = _form_rolls(table)
    assert faces == [1, 4]
    assert entry.number == number
    assert entry.author == table.id_of("Anna")
    assert entry.audience == chronicle.table()
    assert entry.body["form"] == "Cast a Power"
    assert entry.body["faces"] == [1, 4]
    assert entry.body["lines"] == ["Cast a Power: 8 against 6, it works."]
    assert not entry.body["cancelled"]


async def test_a_die_of_any_size_is_drawn_within_its_range(table: Table) -> None:
    table_rolls.host_source = table_rolls.system_source
    seat = await table.seat("Anna")
    try:
        faces = [await seat.form_die(PUBLIC, 1, 7) for _ in range(20)]
        await seat.form_done([])
    finally:
        await seat.close()

    assert all(1 <= face <= 6 for face in faces)
    assert _form_rolls(table)[0].body["faces"] == faces


async def test_a_seat_that_cancels_after_drawing_leaves_its_dice(
    table: Table,
) -> None:
    seat = await table.seat("Anna")
    try:
        await seat.form_die(PUBLIC, 0, 10)
        await seat.form_cancel()
    finally:
        await seat.close()

    [entry] = _form_rolls(table)
    assert entry.body["faces"] == [1]
    assert entry.body["cancelled"]


async def test_a_seat_that_drops_after_drawing_leaves_its_dice(table: Table) -> None:
    seat = await table.seat("Anna")
    await seat.form_die(PUBLIC, 0, 10)
    await seat.form_die(PUBLIC, 0, 10)
    await seat.close()

    [entry] = await _settled(table, 1)
    assert entry.body["faces"] == [1, 4]
    assert entry.body["cancelled"]


async def test_a_seat_cannot_finish_a_roll_it_never_drew_for(table: Table) -> None:
    seat = await table.seat("Anna")
    try:
        with pytest.raises(RollRefused) as refused:
            await seat.form_done(["Nothing was rolled."])
    finally:
        await seat.close()

    assert refused.value.why == "No dice were drawn for that roll."
    assert _form_rolls(table) == []


async def test_a_player_cannot_draw_a_blind_form_roll(table: Table) -> None:
    blind = table_rolls.Opening("Cast a Power", "aelfric", chronicle.BLIND)
    seat = await table.seat("Anna")
    try:
        with pytest.raises(RollRefused) as refused:
            await seat.form_die(blind, 0, 10)
    finally:
        await seat.close()

    assert refused.value.why == "Only the Session's storyguide rolls Blind."


async def test_no_die_is_drawn_without_a_session_under_way(table: Table) -> None:
    chronicle.end(
        table.saga,
        table.saga.sessions[0],
        by=chronicle.storyguide_of(table.saga.sessions[0]),
    )
    storage.save_saga(table.saga)
    seat = await table.seat("Anna")
    try:
        with pytest.raises(RollRefused) as refused:
            await seat.form_die(PUBLIC, 0, 10)
    finally:
        await seat.close()

    assert refused.value.why == "No Session is under way."


async def test_dice_are_limited_per_seat(table: Table) -> None:
    table_rolls.host_source = table_rolls.system_source
    seat = await table.seat("Anna")
    try:
        for _ in range(DICE_PER_MINUTE):
            await seat.form_die(PUBLIC, 0, 10)
        with pytest.raises(RollRefused) as refused:
            await seat.form_die(PUBLIC, 0, 10)
        await seat.form_done([])
    finally:
        await seat.close()

    assert refused.value.why == "Too many dice: wait a minute."


# -- the seat's side: its form takes the host's dice --


async def _seat_session(table: Table) -> SeatSession:
    async with await table.seat("Anna"):
        pass  # approved, and its credential kept
    seat = SeatSession(
        f"ws://127.0.0.1:{table.port}{PATH}", table.pin, table.vaults["Anna"]
    )
    await asyncio.to_thread(seat.connect)
    await asyncio.to_thread(seat.sign_in, PASSCODE)
    return seat


async def test_a_seats_form_takes_the_hosts_dice_as_its_own(table: Table) -> None:
    seat = await _seat_session(table)
    try:
        roll = seat.open_form_roll(PUBLIC)

        def work() -> tuple[int, int, str | None]:
            stress = dice.stress_die(roll.dice, 1)  # 1 doubles, then 4
            return stress.value, dice.simple_die(roll.dice), roll.finish(["It works."])

        value, simple, refused = await asyncio.to_thread(work)
    finally:
        await asyncio.to_thread(seat.close)

    [entry] = _form_rolls(table)
    assert (value, simple, refused) == (8, 10, None)  # a 0 reads as 10
    assert entry.body["faces"] == [1, 4, 0]
    assert entry.body["lines"] == ["It works."]


async def test_a_seat_that_cant_reach_the_host_rolls_nothing(table: Table) -> None:
    seat = await _seat_session(table)
    seat.url = f"ws://127.0.0.1:1{PATH}"  # nothing listens there
    try:
        roll = seat.open_form_roll(PUBLIC)
        with pytest.raises(table_rolls.DiceUnavailable, match="can't be reached"):
            await asyncio.to_thread(roll.dice.randrange, 10)
    finally:
        await asyncio.to_thread(seat.close)


async def test_a_seat_speaking_protocol_2_is_told_to_update(table: Table) -> None:
    async with await table.client() as client:
        reply = await client.request("hello", {"protocol": 2})

    assert reply.type == protocol.UPDATE
