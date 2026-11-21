"""Scenes over real connections (remote/scening.py): a storyguide's seat
sets and ends a Scene through the host, which writes the banner; a hidden
aura reaches no player's seat, in the banner or the saga it is sent; a
seat fetches the banner's picture, a map of the Atlas, by the picture
request."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from test_remote_events import PASSCODE, Table, _gather

from ars_magica_manager import chronicle, paths, scene_play, storage, viewing
from ars_magica_manager.models import AtlasMap, Scene, SceneUse
from ars_magica_manager.remote.client import SceneRefused
from ars_magica_manager.remote.host import PATH
from ars_magica_manager.remote.seat_session import SeatSession
from ars_magica_manager.seat_view import seat_view

HOST = viewing.HOST
PICTURE = b"\x89PNG\r\n\x1a\n" + b"ford" * 30
SECRET_AURA = "Infernal 6"


@pytest_asyncio.fixture
async def table() -> AsyncIterator[Table]:
    """The ford (Infernal 6, with a map of the Atlas) and the tower are
    loaded into tonight's Session."""
    found = Table()
    found.saga.maps = [AtlasMap(id="m", name="The ford", picture="ford.png")]
    maps = paths.data_dir() / paths.MAPS
    maps.mkdir(parents=True, exist_ok=True)
    (maps / "ford.png").write_bytes(PICTURE)
    found.saga.scenes = [
        Scene(
            "ford",
            title="The ford",
            place_name="A ford",
            aura=6,
            realm="Infernal",
            picture="ford.png",
        ),
        Scene("tower", title="The tower", place_name="A tower"),
    ]
    found.saga.sessions[0].scenes = [
        SceneUse("u-ford", scene_id="ford"),
        SceneUse("u-tower", scene_id="tower"),
    ]
    storage.save_saga(found.saga)
    found.port = await found.host.start()
    yield found
    await found.host.stop()


def _host_set(table: Table, use_id: str, *, tell_aura: bool = False) -> None:
    scene_play.set_scene(
        table.book,
        table.saga,
        table.saga.sessions[0],
        chronicle.SceneCall(use_id, tell_aura=tell_aura),
        by=HOST,
    )


async def test_a_storyguides_seat_sets_and_ends_a_scene_through_the_host(
    table: Table,
) -> None:
    """Bea runs the Session from her seat: the host writes the banner and
    the end as hers; Anna, a player, is refused."""
    bea_id = table.id_of("Bea")
    table.saga.sessions[0].storyguide_id = bea_id
    storage.save_saga(table.saga)
    call = chronicle.SceneCall("u-ford")
    anna, bea = await table.seat("Anna"), await table.seat("Bea")
    try:
        with pytest.raises(SceneRefused, match="storyguide"):
            await anna.set_scene(call)
        set_number = await bea.set_scene(call)
        with pytest.raises(SceneRefused, match="already playing"):
            await bea.set_scene(call)
        ended_number = await bea.end_scene()
        with pytest.raises(SceneRefused, match="No Scene is playing"):
            await bea.end_scene()
    finally:
        await anna.close()
        await bea.close()

    book = chronicle.read(table.saga, table.saga.sessions[0])
    book.refresh()
    written = {e.number: e for e in book.entries}
    assert (written[set_number].kind, written[set_number].author) == (
        chronicle.SCENE_SET,
        bea_id,
    )
    assert written[ended_number].kind == chronicle.SCENE_ENDED


async def test_a_hidden_aura_is_in_no_players_frames(table: Table) -> None:
    _host_set(table, "u-ford")
    _host_set(table, "u-tower", tell_aura=True)
    anna = await table.seat("Anna")
    try:
        got = await _gather(anna, 1, 3, "s1")
    finally:
        await anna.close()

    banners = [e for _s, e in got if e.kind == chronicle.SCENE_SET]
    assert [e.body["title"] for e in banners] == ["The ford", "The tower"]
    assert SECRET_AURA not in json.dumps([e.body for _s, e in got])
    assert banners[1].body["aura"] == "none"


def test_a_players_seat_is_sent_no_scene_but_the_storyguides_is() -> None:
    """The Scenes library and a Session's Scenes are the storyguide's prep:
    a player's copy of the saga holds neither."""
    table = Table()
    table.saga.scenes = [Scene("ford", title="The ford", aura=6, realm="Infernal")]
    table.saga.sessions[0].scenes = [SceneUse("u-ford", scene_id="ford")]
    anna = next(p for p in table.saga.players if p.name == "Anna")
    sent = seat_view(table.saga, viewing.viewer_for(anna, hosts=False))
    assert sent.scenes == [] and sent.sessions[0].scenes == []
    whole = seat_view(table.saga, viewing.STORYGUIDE_VIEWER)
    assert whole.scenes == table.saga.scenes


async def test_a_banners_picture_comes_by_the_picture_request(table: Table) -> None:
    _host_set(table, "u-ford")
    anna = await table.seat("Anna")
    try:
        found = await anna.picture(paths.MAPS, "ford.png")
    finally:
        await anna.close()

    assert found == PICTURE


async def test_a_seat_table_sets_and_ends_a_scene(table: Table) -> None:
    table.saga.sessions[0].storyguide_id = table.id_of("Anna")
    storage.save_saga(table.saga)
    async with await table.seat("Anna"):
        pass  # approved, and its credential kept
    seat = SeatSession(
        f"ws://127.0.0.1:{table.port}{PATH}", table.pin, table.vaults["Anna"]
    )
    await asyncio.to_thread(seat.connect)
    await asyncio.to_thread(seat.sign_in, PASSCODE)
    try:
        at = seat.table(chronicle.SeatChronicle())
        answers = [
            await asyncio.to_thread(at.set_scene, chronicle.SceneCall("u-tower")),
            await asyncio.to_thread(at.end_scene),
            await asyncio.to_thread(at.end_scene),
        ]
    finally:
        await asyncio.to_thread(seat.close)

    assert answers == [None, None, "No Scene is playing."]
