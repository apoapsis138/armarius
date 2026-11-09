"""Per-record changes over a real connection: a Remote seat changes its
own character, the host merges and saves it with nothing hidden lost, and
a change that isn't the Player's is refused, logged and counted."""

from __future__ import annotations

import secrets
import zlib
from collections.abc import AsyncIterator
from dataclasses import asdict

import pytest
import pytest_asyncio
from test_remote_records import Hosted
from test_seat_view import hidden_saga

from ars_magica_manager import players, storage
from ars_magica_manager.models import Character, Secret
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.changes import (
    CHANGE_PART,
    MAX_CHANGE,
    change_messages,
    pack_change,
    unpack_change,
)
from ars_magica_manager.remote.client import ChangeNotSaved
from ars_magica_manager.remote.protocol import Refused


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Hosted]:
    saga = hidden_saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    saga.characters[0].background.player_ids = [anna.id]
    saga.characters[0].secrets.append(Secret("Hers", "LEAK-CHARSECRET"))
    saga.characters.append(Character(id="other", name="Bertrand", type="magus"))
    hosted = Hosted(saga)
    hosted.port = await hosted.host.start()
    yield hosted
    await hosted.host.stop()


async def test_a_seat_changes_its_character_and_hidden_data_survives(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _, view = await client.read_saga()
        assert view is not None
        before = asdict(view.characters[0])
        after = {**before, "name": "Leandro the Bold"}
        assert await client.send_change("characters", before["id"], before, after) == []
        _, again = await client.read_saga()
        assert again is not None and again.characters[0].name == "Leandro the Bold"
    finally:
        await client.close()
    saved = storage.load_saga(hosted.saga.id)
    magus = saved.characters[0]
    assert magus.name == "Leandro the Bold"
    assert "LEAK-CHARSECRET" in str(magus.secrets) and "LEAK-LINK" in str(magus.links)
    assert saved.saved_by == "Anna"
    log = AuditLog(audit_path(hosted.saga.name))
    changed = [e for e in log.entries() if e.event == audit.RECORD_CHANGED]
    assert [e.record for e in changed] == [f"characters:{magus.id}"]


async def test_another_players_character_is_refused_logged_and_counted(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _, view = await client.read_saga()
        assert view is not None
        theirs = asdict(next(c for c in view.characters if c.id == "other"))
        with pytest.raises(ChangeNotSaved):
            await client.send_change(
                "characters", "other", theirs, {**theirs, "name": "X"}
            )
    finally:
        await client.close()
    assert storage.load_saga(hosted.saga.id).characters[-1].name == "Bertrand"
    log = AuditLog(audit_path(hosted.saga.name))
    assert [e.record for e in log.entries() if e.event == audit.CHANGE_REFUSED] == [
        "characters:other"
    ]


async def test_a_change_larger_than_one_message_arrives_in_parts(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _, view = await client.read_saga()
        assert view is not None
        before = asdict(view.characters[0])
        # Words that don't compress, so the change needs several parts.
        notes = secrets.token_hex(CHANGE_PART)
        after = {**before, "background": {**before["background"], "setting": notes}}
        assert len(change_messages("characters", before["id"], before, after)) > 1
        await client.send_change("characters", before["id"], before, after)
    finally:
        await client.close()
    assert storage.load_saga(hosted.saga.id).characters[0].background.setting == notes


async def test_a_record_of_the_wrong_shape_is_refused_not_crashed_on(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _, view = await client.read_saga()
        assert view is not None
        before = asdict(view.characters[0])
        broken = {**before, "background": "not a background"}
        with pytest.raises(ChangeNotSaved):
            await client.send_change("characters", before["id"], before, broken)
        assert (await client.request("ping")).type == "pong"  # still talking
    finally:
        await client.close()


def test_a_change_too_large_unpacked_is_refused() -> None:
    bomb = pack_change(None, {"id": "x", "text": "a" * (MAX_CHANGE + 1)})
    with pytest.raises(Refused):
        unpack_change(bomb)


@pytest.mark.parametrize(
    "shape",
    [b"[1, 2]", b'{"before": 1, "after": null}', b'{"after": {}}', b"not json"],
)
def test_a_change_of_the_wrong_shape_is_refused(shape: bytes) -> None:
    with pytest.raises(Refused):
        unpack_change(zlib.compress(shape))
