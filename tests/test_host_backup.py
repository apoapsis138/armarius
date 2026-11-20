"""admin backup: the saga and its Remote seat files, whole, kept to N, and
never the host key."""

from __future__ import annotations

import datetime
import json
import stat
import sys
import threading
import zipfile
from pathlib import Path

import pytest
from admin_support import FakeConsole, ok, refused

from ars_magica_manager import chronicle, host_backup, shows, storage, viewing
from ars_magica_manager import players as pl
from ars_magica_manager.models import Saga, Session
from ars_magica_manager.remote.devices import devices_path
from ars_magica_manager.remote.folder import lock_of
from ars_magica_manager.remote.invites import InviteBook, book_path
from ars_magica_manager.remote.plan import RemotePlan


@pytest.fixture
def saga() -> Saga:
    saga = Saga(id="dammerstein", name="Dammerstein")
    pl.add(saga, {"name": "Ana", "role": pl.PLAYER})
    storage.save_saga(saga)
    InviteBook(book_path(saga.name)).issue(saga.players[0].id)
    RemotePlan(saga.id, saga.name, "https://saga.example.com").remember()
    return saga


@pytest.fixture
def folder(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return tmp_path_factory.mktemp("backups")


def _clock(*moments: str):
    times = iter(
        datetime.datetime.fromisoformat(m).replace(tzinfo=datetime.UTC) for m in moments
    )
    return lambda: next(times)


def test_a_backup_holds_the_sagas_chronicles(saga: Saga, folder: Path) -> None:
    """ADR 0020: a saga's backup includes its Sessions' Chronicle files."""
    saga.sessions = [Session("s1")]
    chronicle.begin(saga, saga.sessions[0], by=viewing.HOST)

    made = host_backup.take(saga.id, saga.name, folder)

    with zipfile.ZipFile(made.path) as archive:
        kept = archive.read("chronicles/dammerstein/s1.jsonl").decode()
    assert json.loads(kept.splitlines()[0])["kind"] == "begin"


def test_a_backup_holds_the_sagas_show_copies(saga: Saga, folder: Path) -> None:
    """ADR 0020: a saga's backup includes its Shows' copies."""
    kept = shows.folder_of(saga.id)
    kept.mkdir(parents=True)
    (kept / "abc.json").write_text('{"title": "A letter"}', encoding="utf-8")

    made = host_backup.take(saga.id, saga.name, folder)

    with zipfile.ZipFile(made.path) as archive:
        copy = json.loads(archive.read("shows/dammerstein/abc.json"))
    assert copy["title"] == "A letter"


def test_a_backup_holds_the_saga_and_its_seat_files(saga: Saga, folder: Path) -> None:
    made = host_backup.take(saga.id, saga.name, folder)
    assert made.path.name.startswith("dammerstein-") and made.path.suffix == ".zip"
    with zipfile.ZipFile(made.path) as archive:
        names = set(archive.namelist())
        assert names == {
            "sagas/dammerstein.json",
            "remote/Dammerstein-invites.json",
            "remote/Dammerstein-host.json",
        }
        restored = storage.saga_from_data(
            json.loads(archive.read("sagas/dammerstein.json"))
        )
    assert restored.players[0].name == "Ana"


def test_another_sagas_files_stay_out(saga: Saga, folder: Path) -> None:
    """A saga whose name starts the same ("Dammerstein Gold") isn't swept in."""
    InviteBook(book_path("Dammerstein Gold")).issue("x")
    made = host_backup.take(saga.id, saga.name, folder)
    assert not any("Gold" in name for name in made.files)


def test_the_newest_are_kept(saga: Saga, folder: Path) -> None:
    clock = _clock(
        "2026-11-14T01:00:00",
        "2026-11-14T02:00:00",
        "2026-11-14T02:00:00",
        "2026-11-14T03:00:00",
    )
    for _ in range(4):
        made = host_backup.take(saga.id, saga.name, folder, keep=2, now=clock)
    kept = [p.name for p in host_backup.saga_backups(folder, saga.id)]
    assert kept == [
        "dammerstein-20261114T020000Z-1.zip",
        "dammerstein-20261114T030000Z.zip",
    ]
    assert len(made.removed) == 1


def test_other_files_in_the_folder_are_left_alone(saga: Saga, folder: Path) -> None:
    (folder / "notes.txt").write_text("mine", encoding="utf-8")
    (folder / "rhine-20261114T010000Z.zip").write_bytes(b"another saga's")
    host_backup.take(saga.id, saga.name, folder, keep=1)
    host_backup.take(saga.id, saga.name, folder, keep=1)
    assert (folder / "notes.txt").exists() and (
        folder / "rhine-20261114T010000Z.zip"
    ).exists()


def test_a_backup_waits_for_a_save_in_progress(saga: Saga, folder: Path) -> None:
    """Taken under the saga's lock: while another program holds it, the
    backup waits, then copies the file as that save left it."""
    started = threading.Event()
    release = threading.Event()

    path = storage.saga_path(saga.id)

    def saving() -> None:
        """Another program's save: it holds the lock while it writes."""
        with storage._saga_lock(saga.id):
            started.set()
            release.wait(5)
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text.replace('"description": ""', '"description": "after the save"'),
                encoding="utf-8",
            )

    writer = threading.Thread(target=saving)
    writer.start()
    started.wait(5)
    result: list[host_backup.Backup] = []
    backup = threading.Thread(
        target=lambda: result.append(host_backup.take(saga.id, saga.name, folder))
    )
    backup.start()
    backup.join(0.3)
    assert backup.is_alive()  # waiting on the lock
    release.set()
    writer.join(5)
    backup.join(5)
    with zipfile.ZipFile(result[0].path) as archive:
        assert b"after the save" in archive.read("sagas/dammerstein.json")


def test_a_seat_file_is_read_under_its_own_lock(saga: Saga, folder: Path) -> None:
    lock = lock_of(book_path(saga.name))
    lock.write_text("", encoding="utf-8")  # another program holds it...
    holder = threading.Timer(0.3, lambda: lock.unlink())
    holder.start()
    made = host_backup.take(saga.id, saga.name, folder)  # ...until it lets go
    holder.join()
    assert "remote/Dammerstein-invites.json" in made.files


def test_no_folder_no_backup(saga: Saga, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(host_backup.BACKUPS_VARIABLE, raising=False)
    assert "--to" in refused(["backup"])


def test_the_key_folder_is_refused(
    saga: Saga, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("ARMARIUS_KEYS", str(folder))
    assert "key folder" in refused(["backup", "--to", str(folder / "inside")])
    assert host_backup.saga_backups(folder / "inside", saga.id) == []


def test_admin_backup_says_where_and_never_holds_a_key(
    saga: Saga, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv(host_backup.BACKUPS_VARIABLE, str(folder))
    text = ok(["backup", "--keep", "3"], FakeConsole()).text
    assert "Backed up Dammerstein to" in text and "host key isn't in it" in text
    (made,) = host_backup.saga_backups(folder, saga.id)
    with zipfile.ZipFile(made) as archive:
        assert not any("key" in name for name in archive.namelist())
    assert "at least one" in refused(["backup", "--keep", "0"])


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX file modes")
def test_a_backup_is_the_owners_alone(saga: Saga, folder: Path) -> None:
    made = host_backup.take(saga.id, saga.name, folder)
    assert stat.S_IMODE(made.path.stat().st_mode) == 0o600


def test_devices_file_included_when_there(saga: Saga, folder: Path) -> None:
    devices_path(saga.name).write_text('{"devices": {}}', encoding="utf-8")
    assert (
        "remote/Dammerstein-devices.json"
        in host_backup.take(saga.id, saga.name, folder).files
    )
