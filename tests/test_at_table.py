"""The Table's two adapters keep one contract: the same verb by the same
Player gives the same answer at the host's own computer and from a Remote
seat over a real connection."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from test_remote_events import PASSCODE, Table

from ars_magica_manager import at_table, chronicle, host_table
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.seat_session import SeatSession, SeatTable

OTHERS = "Roll for a character you play tonight."


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Table]:
    found = Table()
    found.port = await found.host.start()
    try:
        yield found
    finally:
        await found.host.stop()


async def _seat_table(hosted: Table) -> tuple[SeatTable, SeatSession]:
    async with await hosted.seat("Anna"):
        pass  # approved, and its credential kept
    seat = SeatSession(
        f"ws://127.0.0.1:{hosted.port}{PATH}", hosted.pin, hosted.vaults["Anna"]
    )
    await asyncio.to_thread(seat.connect)
    await asyncio.to_thread(seat.sign_in, PASSCODE)
    return seat.table(chronicle.SeatChronicle()), seat


async def _table(
    hosted: Table, where: str
) -> tuple[at_table.Table, SeatSession | None]:
    if where == "seat":
        return await _seat_table(hosted)
    session = hosted.saga.sessions[0]
    return host_table.HostTable(hosted.saga, session, hosted.id_of("Anna")), None


@pytest.mark.parametrize("where", ["host", "seat"])
async def test_each_verb_answers_the_same_at_the_host_and_from_a_seat(
    hosted: Table, where: str
) -> None:
    table, seat = await _table(hosted, where)
    try:
        answers = [
            await asyncio.to_thread(
                table.roll, chronicle.RollRequest(character_id="aelfric")
            ),
            await asyncio.to_thread(
                table.roll, chronicle.RollRequest(character_id="brigit")
            ),
            await asyncio.to_thread(table.say, "Hail, all.", (), ()),
            await asyncio.to_thread(table.spend, 99, 1),
            await asyncio.to_thread(table.answer, 99, "aelfric", False),
        ]
    finally:
        if seat is not None:
            await asyncio.to_thread(seat.close)

    assert answers == [
        None,
        OTHERS,
        None,
        "There is no such roll.",
        "There is no such Roll request.",
    ]
    book = chronicle.read(hosted.saga, hosted.saga.sessions[0])
    book.refresh()
    written = book.entries
    anna = hosted.id_of("Anna")
    assert [(e.kind, e.author) for e in written[-2:]] == [
        (chronicle.ROLL, anna),
        (chronicle.MESSAGE, anna),
    ]


def test_the_host_table_is_the_default_until_a_seat_is_attached() -> None:
    hosted = Table()
    session = hosted.saga.sessions[0]
    assert isinstance(host_table.here(hosted.saga, session, "x"), host_table.HostTable)
    seated = object.__new__(SeatTable)
    at_table.use_seat(seated)
    try:
        assert host_table.here(hosted.saga, session, "x") is seated
    finally:
        at_table.use_seat(None)
