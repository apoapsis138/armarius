"""A storyguide's Remote seat over a real connection: it reads the whole
saga, changes it as a whole (saga_delta.py), advances the season with the
host's backup first, and the host keeps its Players (ADR 0014)."""

from __future__ import annotations

import copy
from collections.abc import AsyncIterator
from dataclasses import asdict

import pytest
import pytest_asyncio
from test_remote_records import Hosted
from test_seat_view import LEAKS, hidden_saga

from ars_magica_manager import players, storage
from ars_magica_manager.remote import audit
from ars_magica_manager.remote.audit import AuditLog, audit_path
from ars_magica_manager.remote.client import AlreadyAdvanced, ChangeNotSaved
from ars_magica_manager.saga_delta import saga_delta


@pytest_asyncio.fixture
async def hosted() -> AsyncIterator[Hosted]:
    saga = hidden_saga()
    anna = players.find(saga, "Anna")
    assert anna is not None
    anna.role = players.STORYGUIDE
    serving = Hosted(saga)
    serving.port = await serving.host.start()
    yield serving
    await serving.host.stop()


async def test_a_storyguides_seat_reads_everything_but_the_passcodes(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _revision, saga = await client.read_saga()
    finally:
        await client.close()
    assert saga is not None
    text = str(saga)
    assert all(word in text for word in LEAKS.values())
    assert all(not p.passcode_hash for p in saga.players)


async def test_a_storyguide_advances_the_season_and_the_host_backs_up_first(
    hosted: Hosted,
) -> None:
    client = await hosted.signed_in()
    try:
        _revision, saga = await client.read_saga()
        assert saga is not None
        base = asdict(saga)
        now = copy.deepcopy(base)
        now["current_season"] = "Summer"
        now["neighbours"][0]["name"] = "Renamed by the storyguide"
        assert await client.send_saga(*saga_delta(base, now)) == []
        # A second advance made from the old date is refused, naming who.
        with pytest.raises(AlreadyAdvanced) as first:
            await client.send_saga(*saga_delta(base, now))
    finally:
        await client.close()
    assert first.value.who == "Anna" and first.value.now.startswith("Summer")
    host = storage.load_saga(hosted.saga.id)
    assert host.current_season == "Summer"
    assert host.neighbours[0].name == "Renamed by the storyguide"
    assert storage.backup_path(hosted.saga.id).exists()
    events = [e.event for e in AuditLog(audit_path(hosted.saga.name)).entries()]
    assert audit.SEASON_ADVANCED in events


async def test_a_storyguide_undoes_the_season_on_the_host(hosted: Hosted) -> None:
    client = await hosted.signed_in()
    try:
        _revision, saga = await client.read_saga()
        assert saga is not None
        assert await client.undo_offer() is None  # nothing advanced yet
        base = asdict(saga)
        now = copy.deepcopy(base)
        now["current_season"] = "Summer"
        await client.send_saga(*saga_delta(base, now))
        found = await client.undo_offer()
        assert found is not None and found[0].startswith("Spring")
        assert await client.undo_season("Autumn 1066") == ""  # not the season now
        said = await client.undo_season(found[1])
    finally:
        await client.close()
    assert "back to Spring" in said
    assert storage.load_saga(hosted.saga.id).current_season == "Spring"
    events = [e.event for e in AuditLog(audit_path(hosted.saga.name)).entries()]
    assert audit.SEASON_UNDONE in events


async def test_the_players_stay_the_hosts(hosted: Hosted) -> None:
    client = await hosted.signed_in()
    try:
        _revision, saga = await client.read_saga()
        assert saga is not None
        base = asdict(saga)
        now = copy.deepcopy(base)
        now["players"][0]["name"] = "Renamed"
        with pytest.raises(ChangeNotSaved):
            await client.send_saga(*saga_delta(base, now))
    finally:
        await client.close()


async def test_a_players_seat_cannot_change_the_whole_saga(hosted: Hosted) -> None:
    saga = storage.load_saga(hosted.saga.id)
    anna = players.find(saga, "Anna")
    assert anna is not None
    anna.role = players.PLAYER
    storage.save_saga(saga)
    client = await hosted.signed_in()
    try:
        base = asdict(saga)
        now = copy.deepcopy(base)
        now["current_season"] = "Summer"
        with pytest.raises(ChangeNotSaved):
            await client.send_saga(*saga_delta(base, now))
    finally:
        await client.close()
    assert storage.load_saga(hosted.saga.id).current_season == saga.current_season
