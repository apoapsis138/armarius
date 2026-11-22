"""Shows over real connections (remote/showing.py): a storyguide's seat
Shows through the host, which makes the copy; a seat fetches a Show's copy
and picture only while its Player sees the Show."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from test_remote_events import PASSCODE, Table, _gather

from ars_magica_manager import (
    chronicle,
    paths,
    references,
    show_copy,
    shows,
    storage,
    viewing,
)
from ars_magica_manager.models import AtlasMap, Secret
from ars_magica_manager.remote import showing
from ars_magica_manager.remote.client import ShowRefused
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.protocol import Body
from ars_magica_manager.remote.seat_session import SeatSession
from ars_magica_manager.remote.showing import OPENS_PER_MINUTE

HOST = viewing.HOST
PICTURE = b"\x89PNG\r\n\x1a\n" + b"map" * 30


@pytest_asyncio.fixture
async def table() -> AsyncIterator[Table]:
    found = Table()
    found.saga.maps = [AtlasMap(id="m", name="The Rhine", picture="rhine.png")]
    maps = paths.data_dir() / paths.MAPS
    maps.mkdir(parents=True, exist_ok=True)
    (maps / "rhine.png").write_bytes(PICTURE)
    storage.save_saga(found.saga)
    found.port = await found.host.start()
    yield found
    await found.host.stop()


def _host_show(table: Table, call: chronicle.ShowCall) -> chronicle.Entry:
    return shows.show(
        table.book,
        table.saga,
        table.saga.sessions[0],
        call,
        by=HOST,
        copier=show_copy.player_copy,
    )


async def test_a_seat_opens_a_show_it_sees_and_no_other(table: Table) -> None:
    entry = _host_show(
        table,
        chronicle.ShowCall(
            "Aelfric",
            references.Ref("characters", "aelfric", ""),
            to=(table.id_of("Anna"),),
        ),
    )
    show_id = str(entry.body["show"])
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        kept = await anna.show_copy(show_id)
        with pytest.raises(ShowRefused):
            await bea.show_copy(show_id)
        with pytest.raises(ShowRefused):
            await anna.show_copy("no-such-show")
    finally:
        await anna.close()
        await bea.close()

    assert kept["title"] == "Aelfric" and "Aelfric" in kept["text"]


async def test_no_seat_can_fetch_a_withdrawn_show(table: Table) -> None:
    """Bea runs the Session from her seat and withdraws the Show she gave
    Anna: Anna's seat is refused its copy and picture from then on."""
    bea_id, anna_id = table.id_of("Bea"), table.id_of("Anna")
    table.saga.sessions[0].storyguide_id = bea_id
    storage.save_saga(table.saga)
    call = chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"), to=(anna_id,))
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        number = await bea.show(call)
        book = chronicle.read(table.saga, table.saga.sessions[0])
        book.refresh()
        entry = next(e for e in book.entries if e.number == number)
        show_id, name = str(entry.body["show"]), str(entry.body["picture"])
        assert (await anna.show_copy(show_id))["title"] == "The Rhine"
        with pytest.raises(ShowRefused, match="storyguide"):
            await anna.withdraw(number)
        await bea.withdraw(number)
        with pytest.raises(ShowRefused):
            await anna.show_copy(show_id)
        assert await anna.picture(shows.FOLDER, name) is None
    finally:
        await anna.close()
        await bea.close()

    book.refresh()
    assert (book.entries[-1].kind, book.entries[-1].author) == (
        chronicle.WITHDRAWN,
        bea_id,
    )


async def test_a_shown_picture_is_fetched_only_by_a_seat_that_sees_its_show(
    table: Table,
) -> None:
    entry = _host_show(
        table,
        chronicle.ShowCall(
            "The Rhine", picture=("maps", "rhine.png"), to=(table.id_of("Bea"),)
        ),
    )
    name = str(entry.body["picture"])
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        for_bea = await bea.picture(shows.FOLDER, name)
        for_anna = await anna.picture(shows.FOLDER, name)
    finally:
        await anna.close()
        await bea.close()

    assert for_bea == PICTURE
    assert for_anna is None


async def test_a_show_reaches_its_seat_for_it_without_any_players_id(
    table: Table,
) -> None:
    anna_id = table.id_of("Anna")
    _host_show(
        table,
        chronicle.ShowCall(
            "Aelfric", references.Ref("characters", "aelfric", ""), to=(anna_id,)
        ),
    )
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        for_anna = await _gather(anna, 1, 1, "s1")
        for_bea = await _gather(bea, 1, 1, "s1")
    finally:
        await anna.close()
        await bea.close()

    [(_s, shown)] = for_anna
    assert shown.kind == chronicle.SHOW and shown.for_you is True
    assert anna_id not in json.dumps(shown.body)
    assert for_bea == []


async def test_a_storyguides_seat_shows_through_the_host(table: Table) -> None:
    """Bea runs the Session from her seat: the host makes the copy and
    writes the Show as hers; Anna, a player, is refused."""
    bea_id = table.id_of("Bea")
    table.saga.sessions[0].storyguide_id = bea_id
    storage.save_saga(table.saga)
    call = chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png"))
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        with pytest.raises(ShowRefused, match="storyguide"):
            await anna.show(call)
        number = await bea.show(call)
    finally:
        await anna.close()
        await bea.close()

    book = chronicle.read(table.saga, table.saga.sessions[0])
    book.refresh()
    entry = next(e for e in book.entries if e.number == number)
    assert (entry.kind, entry.author) == (chronicle.SHOW, bea_id)
    assert shows.opened(table.saga.id, entry).picture == PICTURE


async def test_a_storyguides_seat_sends_the_secrets_it_ticked(table: Table) -> None:
    """Bea, a storyguide, runs the Session from her seat and Shows Aelfric
    with his second Secret, revealing him as she does."""
    bea_id = table.id_of("Bea")
    next(p for p in table.saga.players if p.id == bea_id).role = viewing.STORYGUIDE
    table.saga.sessions[0].storyguide_id = bea_id
    aelfric = table.saga.character("aelfric")
    assert aelfric is not None
    aelfric.secrets = [Secret("Kept", "KEPT-SECRET"), Secret("Other", "OTHER-SECRET")]
    storage.save_saga(table.saga)
    other = (1, shows.secret_mark(aelfric.secrets[1]))
    call = chronicle.ShowCall(
        "Aelfric",
        references.Ref("characters", "aelfric", ""),
        secrets=(other,),
        reveal=True,
    )
    bea = await table.seat("Bea")
    try:
        number = await bea.show(call)
    finally:
        await bea.close()

    book = chronicle.read(table.saga, table.saga.sessions[0])
    book.refresh()
    entry = next(e for e in book.entries if e.number == number)
    text = shows.opened(table.saga.id, entry).text
    assert "OTHER-SECRET" in text and "KEPT-SECRET" not in text


def test_a_seats_show_carries_its_ticks_and_reveal_and_refuses_a_bad_tick() -> None:
    body: Body = {"title": "T", "kind": "characters", "id": "a", "reveal": True}
    body["secrets"] = "1:ab\n3:cd"
    call = showing.call_of(body)
    assert call.secrets == ((1, "ab"), (3, "cd")) and call.reveal
    for bad in ("1", "-1:ab", "x:ab", "1:ab\n\n2", "1:"):
        with pytest.raises(ValueError, match=shows.NOT_A_SECRET):
            showing.call_of({"title": "T", "kind": "characters", "secrets": bad})


async def test_a_seat_table_opens_the_copy_of_a_show_it_holds(table: Table) -> None:
    entry = _host_show(
        table,
        chronicle.ShowCall("The Rhine", picture=("maps", "rhine.png")),
    )
    async with await table.seat("Anna"):
        pass
    seat = SeatSession(
        f"ws://127.0.0.1:{table.port}{PATH}", table.pin, table.vaults["Anna"]
    )
    await asyncio.to_thread(seat.connect)
    await asyncio.to_thread(seat.sign_in, PASSCODE)
    try:
        opened = await asyncio.to_thread(
            seat.table(chronicle.SeatChronicle()).open_show, entry
        )
    finally:
        await asyncio.to_thread(seat.close)

    assert isinstance(opened, shows.Shown)
    assert (opened.title, opened.picture) == ("The Rhine", PICTURE)


async def test_opening_show_copies_is_limited_per_seat(table: Table) -> None:
    entry = _host_show(
        table,
        chronicle.ShowCall("Aelfric", references.Ref("characters", "aelfric", "")),
    )
    show_id = str(entry.body["show"])
    anna = await table.seat("Anna")
    try:
        for _ in range(OPENS_PER_MINUTE):
            await anna.show_copy(show_id)
        with pytest.raises(ShowRefused, match="Too many"):
            await anna.show_copy(show_id)
    finally:
        await anna.close()
