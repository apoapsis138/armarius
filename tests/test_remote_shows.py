"""Shows over real connections (remote/showing.py): a storyguide's seat
Shows through the host, which makes the copy; a seat fetches a Show's copy
and picture only while its Player sees the Show."""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from typing import Any, cast

import pytest
import pytest_asyncio
from test_remote_events import PASSCODE, Table, _gather

from ars_magica_manager import (
    chronicle,
    handout_arrangement,
    paths,
    references,
    show_copy,
    shows,
    storage,
    viewing,
)
from ars_magica_manager.forms import show as show_forms
from ars_magica_manager.handout_arrangement import Arrange
from ars_magica_manager.models import (
    SEALED_LETTER,
    AtlasMap,
    Handout,
    HandoutPicture,
    Secret,
)
from ars_magica_manager.remote import showing
from ars_magica_manager.remote.client import RemoteClient, ShowRefused
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.protocol import Body
from ars_magica_manager.remote.seat_session import SeatSession, handout_pictures
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


async def test_a_seat_fetches_its_own_handouts_and_no_other_players(
    table: Table,
) -> None:
    anna_id, bea_id = table.id_of("Anna"), table.id_of("Bea")
    _host_show(
        table,
        chronicle.ShowCall(
            "Aelfric", references.Ref("characters", "aelfric", ""), to=(anna_id,)
        ),
    )
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        mine = await anna.handouts(anna_id)
        with pytest.raises(ShowRefused):
            await bea.handouts(anna_id)
        theirs = await bea.handouts(bea_id)
    finally:
        await anna.close()
        await bea.close()

    assert [k.title for k in mine] == ["Aelfric"]
    assert theirs == []


async def test_a_seat_arranges_its_own_handouts_and_no_one_elses(
    table: Table,
) -> None:
    anna_id = table.id_of("Anna")
    _host_show(
        table,
        chronicle.ShowCall(
            "Aelfric", references.Ref("characters", "aelfric", ""), to=(anna_id,)
        ),
    )
    key = "characters:aelfric"
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        await anna.arrange_handouts(anna_id, Arrange(key, title="Mine", pinned=True))
        kept = await anna.handout_arrangement(anna_id)
        with pytest.raises(ShowRefused, match="Only you"):
            await bea.arrange_handouts(anna_id, Arrange(key, title="Hers"))
        with pytest.raises(ShowRefused, match="Only you"):
            await bea.handout_arrangement(anna_id)
        with pytest.raises(ShowRefused, match="isn't in your list"):
            await anna.arrange_handouts(anna_id, Arrange("nothing:here", pinned=True))
        found = await anna.search_handouts(anna_id, "aelfric")
        with pytest.raises(ShowRefused):
            await bea.search_handouts(anna_id, "aelfric")
    finally:
        await anna.close()
        await bea.close()

    [place] = kept.places
    assert (place.key, place.title, place.pinned) == (key, "Mine", True)
    assert found == {key}
    on_file = handout_arrangement.load(table.saga.id, anna_id)
    assert on_file.places[0].title == "Mine"


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


LETTER = "[heading] Hail\n[script] fetch http://x\n[picture 1]"


def _letter(table: Table) -> None:
    """A written Handout with the Rhine map, kept in the host's saga."""
    table.saga.handouts = [
        Handout(
            "letter",
            "A letter",
            stationery=SEALED_LETTER,
            text=LETTER,
            pictures=[HandoutPicture(paths.MAPS, "rhine.png")],
        )
    ]
    storage.save_saga(table.saga)


async def test_a_written_handouts_copy_and_pictures_reach_only_the_seats_shown(
    table: Table,
) -> None:
    _letter(table)
    entry = _host_show(
        table,
        chronicle.ShowCall("A letter", handout="letter", to=(table.id_of("Bea"),)),
    )
    show_id = str(entry.body["show"])
    [name] = entry.body["pictures"]
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        kept = await bea.show_copy(show_id)
        for_bea = await bea.picture(shows.FOLDER, name)
        with pytest.raises(ShowRefused):
            await anna.show_copy(show_id)
        for_anna = await anna.picture(shows.FOLDER, name)
    finally:
        await anna.close()
        await bea.close()

    assert (kept["stationery"], kept["text"]) == (SEALED_LETTER, LETTER)
    assert for_bea == PICTURE and for_anna is None


async def test_a_seat_opens_a_written_handout_with_its_pictures_on_one_connection(
    table: Table, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The copy and all its pictures come on the one connection opened for
    it, so opening a few Handouts can't use up the seat's connections; a
    picture the host hasn't got is a placeholder."""
    _letter(table)
    table.saga.handouts[0].pictures += [
        HandoutPicture(paths.MAPS, "rhine.png"),
        HandoutPicture(paths.MAPS, "gone.png"),
    ]
    storage.save_saga(table.saga)
    entry = _host_show(table, chronicle.ShowCall("A letter", handout="letter"))
    async with await table.seat("Anna"):
        pass
    seat = SeatSession(
        f"ws://127.0.0.1:{table.port}{PATH}", table.pin, table.vaults["Anna"]
    )
    await asyncio.to_thread(seat.connect)
    await asyncio.to_thread(seat.sign_in, PASSCODE)
    connections: list[int] = []
    real = seat._connect_own  # pyright: ignore[reportPrivateUsage]

    async def counted() -> Any:
        connections.append(1)
        return await real()

    monkeypatch.setattr(seat, "_connect_own", counted)
    try:
        opened = await asyncio.to_thread(
            seat.table(chronicle.SeatChronicle()).open_show, entry
        )
    finally:
        await asyncio.to_thread(seat.close)

    assert len(connections) == 1
    assert isinstance(opened, shows.Shown)
    assert opened.written and opened.stationery == SEALED_LETTER
    assert opened.pictures == (PICTURE, PICTURE, None)
    words = show_forms.copy_form(opened).fields()[0].value
    assert "[b]Hail[/]" in str(words) and "\\[script] fetch" in str(words)


async def test_a_storyguides_seat_shows_a_written_handout(table: Table) -> None:
    _letter(table)
    bea_id = table.id_of("Bea")
    table.saga.sessions[0].storyguide_id = bea_id
    storage.save_saga(table.saga)
    bea = await table.seat("Bea")
    try:
        number = await bea.show(chronicle.ShowCall("A letter", handout="letter"))
    finally:
        await bea.close()

    book = chronicle.read(table.saga, table.saga.sessions[0])
    book.refresh()
    entry = next(e for e in book.entries if e.number == number)
    assert (entry.author, entry.body["handout"]) == (bea_id, "letter")
    assert shows.opened(table.saga.id, entry).text == LETTER


class _SlowHost:
    """A client whose first picture comes at once and the rest never."""

    def __init__(self) -> None:
        self.asked: list[str] = []

    async def picture(self, _folder: str, name: str) -> bytes | None:
        self.asked.append(name)
        if len(self.asked) > 1:
            await asyncio.sleep(60)
        return PICTURE


async def test_a_copys_pictures_share_one_deadline_and_late_ones_are_placeholders() -> (
    None
):
    host = _SlowHost()
    started = time.monotonic()

    found = await handout_pictures(
        cast(RemoteClient, host), ["a-1.png", "", "a-3.png", "a-4.png"], wait=0.2
    )

    assert time.monotonic() - started < 2
    assert found == (PICTURE, None, None, None)
    assert host.asked == ["a-1.png", "a-3.png"]


def test_a_seats_show_carries_the_handout_it_names() -> None:
    call = showing.call_of({"title": "T", "handout": "letter"})
    assert (call.handout, call.record, call.picture) == ("letter", None, None)


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
