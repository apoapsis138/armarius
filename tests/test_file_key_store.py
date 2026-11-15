"""A headless host's keys in a folder of files (ADR 0022): kept private,
apart from the data folder, chosen only with ARMARIUS_KEYSTORE=file."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

from ars_magica_manager import paths, storage
from ars_magica_manager.commands import Confirm, Refuse
from ars_magica_manager.forms import remote_seats
from ars_magica_manager.models import Saga
from ars_magica_manager.remote import identity as ident
from ars_magica_manager.remote import key_files, serve
from ars_magica_manager.remote.key_files import FileKeyStore, KeyFolderError
from ars_magica_manager.remote.plan import identity_name
from ars_magica_manager.tui import hosting

posix_only = pytest.mark.skipif(
    sys.platform == "win32", reason="file modes and owners are POSIX's"
)
windows_only = pytest.mark.skipif(sys.platform != "win32", reason="Windows refusal")


@pytest.fixture
def keys(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """A key folder apart from the test's data folder: made private on
    POSIX, as the host's owner makes it; not made on Windows."""
    folder = tmp_path_factory.mktemp("keyroot") / "keys"
    if sys.platform != "win32":
        folder.mkdir()
        folder.chmod(0o700)
    return folder


def _mode(path: Path) -> int:
    return stat.S_IMODE(path.stat().st_mode)


# -- names and the factory (every system) -------------------------------------


def test_a_name_with_colons_is_one_plain_file_name_and_comes_back() -> None:
    for name in ("host-key:dammerstein", "ssh-host-key", "a/b:c\\d", "Fürstenberg"):
        file = key_files.file_name(name)
        assert "/" not in file and ":" not in file and "\\" not in file
        assert key_files.key_name(file) == name


def test_a_file_without_the_suffix_is_not_a_key() -> None:
    with pytest.raises(ValueError, match="not a key file"):
        key_files.key_name("notes.txt")


def test_the_keychain_unless_the_file_store_is_asked_for(
    monkeypatch: pytest.MonkeyPatch, keys: Path
) -> None:
    monkeypatch.delenv(key_files.STORE_VARIABLE, raising=False)
    assert isinstance(key_files.key_store(), ident.KeychainStore)
    monkeypatch.setenv(key_files.STORE_VARIABLE, "keychain")
    assert isinstance(key_files.key_store(), ident.KeychainStore)
    monkeypatch.setenv(key_files.STORE_VARIABLE, "file")
    monkeypatch.setenv(key_files.FOLDER_VARIABLE, str(keys))
    store = key_files.key_store()
    assert isinstance(store, FileKeyStore) and store.folder == keys


def test_the_file_store_defaults_to_the_keys_volume(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(key_files.STORE_VARIABLE, "file")
    monkeypatch.delenv(key_files.FOLDER_VARIABLE, raising=False)
    store = key_files.key_store()
    assert isinstance(store, FileKeyStore) and store.folder == Path("/keys")


def test_an_unknown_store_setting_is_refused_not_ignored(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A misspelt setting gives a store that refuses every use, saying why:
    never the keychain instead, and nothing fails until the key is used."""
    monkeypatch.setenv(key_files.STORE_VARIABLE, "files")
    store = key_files.key_store()
    for call in (
        lambda: store.get("x"),
        lambda: store.set("x", "y"),
        lambda: store.delete("x"),
    ):
        with pytest.raises(KeyFolderError, match="doesn't know") as refused:
            call()
        assert isinstance(refused.value, ident.NoKeychainError)  # callers show it
    assert ident.KeychainStore().get("x") is None  # nothing went to the keychain


def test_a_misspelt_setting_is_shown_where_a_missing_keychain_is(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The Host for Players window opens and says why, and the listener
    stops with the reason, instead of either failing as it starts."""
    monkeypatch.setenv(key_files.STORE_VARIABLE, "files")
    saga = Saga(id="dammerstein", name="Dammerstein")
    storage.save_saga(saga)
    desk = remote_seats.SeatsDesk(saga)  # builds: the window can open
    with pytest.raises(KeyFolderError, match="doesn't know"):
        desk.words()
    refused = desk.rotate()
    assert isinstance(refused, Confirm)
    shown = refused.apply()
    assert isinstance(shown, Refuse) and "doesn't know" in shown.why
    with pytest.raises(SystemExit) as stopped:
        serve.main(["--saga", "dammerstein"])
    assert "doesn't know" in str(stopped.value.code)


def test_no_keychain_names_the_headless_setting() -> None:
    assert "ARMARIUS_KEYSTORE=file" in ident._NO_KEYCHAIN


def test_the_listener_takes_its_store_from_the_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    storage.save_saga(Saga(id="dammerstein", name="Dammerstein"))
    store = ident.MemoryStore()
    monkeypatch.setattr(serve, "key_store", lambda: store)
    serve.build("dammerstein")
    assert store.get(identity_name("dammerstein")) is not None


async def test_the_ssh_host_key_comes_from_the_factory(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store = ident.MemoryStore()
    monkeypatch.setattr(hosting, "key_store", lambda: store)
    server = await hosting.start_ssh_server("true", "127.0.0.1", 0)
    try:
        assert store.get(hosting.HOST_KEY_NAME) is not None
    finally:
        server.close()
        await server.wait_closed()


@windows_only
def test_windows_refuses_the_file_store(keys: Path) -> None:
    store = FileKeyStore(keys)
    for call in (
        lambda: store.get("x"),
        lambda: store.set("x", "y"),
        lambda: store.delete("x"),
    ):
        with pytest.raises(KeyFolderError, match="Credential Manager"):
            call()
    assert not keys.exists()


# -- the store itself (POSIX) -------------------------------------------------


@posix_only
def test_round_trip(keys: Path) -> None:
    store = FileKeyStore(keys)
    assert store.get("host-key:dammerstein") is None
    store.set("host-key:dammerstein", "secret")
    assert store.get("host-key:dammerstein") == "secret"
    store.set("host-key:dammerstein", "newer")
    assert store.get("host-key:dammerstein") == "newer"
    store.delete("host-key:dammerstein")
    assert store.get("host-key:dammerstein") is None
    store.delete("host-key:dammerstein")  # nothing there: fine


@posix_only
def test_each_key_is_0600(keys: Path) -> None:
    old = os.umask(0o022)  # a umask that would leave a file readable
    try:
        FileKeyStore(keys).set("host-key:x", "secret")
    finally:
        os.umask(old)
    (file,) = keys.iterdir()
    assert _mode(file) == 0o600
    assert file.name == key_files.file_name("host-key:x")


@posix_only
def test_a_key_others_can_read_is_refused(keys: Path) -> None:
    store = FileKeyStore(keys)
    store.set("k", "secret")
    path = keys / key_files.file_name("k")
    path.chmod(0o644)
    with pytest.raises(KeyFolderError, match="chmod 600"):
        store.get("k")


@posix_only
def test_a_folder_others_can_open_is_refused(keys: Path) -> None:
    keys.chmod(0o755)
    with pytest.raises(KeyFolderError, match="chmod 700"):
        FileKeyStore(keys).get("k")


@posix_only
def test_a_missing_folder_is_refused_not_made(keys: Path) -> None:
    """An encrypted volume not yet unlocked looks like a missing folder: a
    folder made in its place would take a fresh key, unencrypted."""
    keys.rmdir()
    store = FileKeyStore(keys)
    for call in (
        lambda: store.get("k"),
        lambda: store.set("k", "secret"),
        lambda: store.delete("k"),
    ):
        with pytest.raises(KeyFolderError, match="isn't there.*unlock that first"):
            call()
    assert not keys.exists()


@posix_only
def test_a_locked_volume_s_bare_mount_point_is_refused(
    keys: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the volume locked, the folder left is the mount point, owned
    by root: refused as another user's, so no key is written there."""
    me = os.geteuid()
    monkeypatch.setattr(key_files.os, "geteuid", lambda: me + 1)
    with pytest.raises(KeyFolderError, match="belongs to user"):
        FileKeyStore(keys).set("k", "secret")
    assert not any(keys.iterdir())


@posix_only
def test_a_folder_in_the_data_folder_is_refused() -> None:
    inside = paths.data_dir() / "keys"
    with pytest.raises(KeyFolderError, match="inside the data folder"):
        FileKeyStore(inside).set("k", "secret")
    assert not inside.exists()


@posix_only
def test_a_folder_holding_the_data_folder_is_refused() -> None:
    with pytest.raises(KeyFolderError, match="inside the data folder"):
        FileKeyStore(paths.data_dir().parent).get("k")


@posix_only
def test_a_link_into_the_data_folder_is_refused(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    target = paths.data_dir() / "hidden"
    target.mkdir(mode=0o700)
    link = tmp_path_factory.mktemp("elsewhere") / "keys"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises(KeyFolderError, match="inside the data folder"):
        FileKeyStore(link).set("k", "secret")
    assert not any(target.iterdir())


@posix_only
def test_running_as_root_is_refused(
    keys: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(key_files.os, "geteuid", lambda: 0)
    with pytest.raises(KeyFolderError, match="running as root"):
        FileKeyStore(keys).get("k")


@posix_only
def test_a_key_owned_by_someone_else_is_refused(
    keys: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    store = FileKeyStore(keys)
    store.set("k", "secret")
    me = os.geteuid()
    monkeypatch.setattr(key_files.os, "geteuid", lambda: me + 1)
    with pytest.raises(
        KeyFolderError, match=f"belongs to user {me}.*sudo chown {me + 1}:"
    ):
        store.get("k")


@posix_only
def test_the_listener_keeps_its_key_in_the_folder_when_asked(
    monkeypatch: pytest.MonkeyPatch, keys: Path
) -> None:
    monkeypatch.setenv(key_files.STORE_VARIABLE, "file")
    monkeypatch.setenv(key_files.FOLDER_VARIABLE, str(keys))
    storage.save_saga(Saga(id="dammerstein", name="Dammerstein"))
    serve.build("dammerstein")
    path = keys / key_files.file_name(identity_name("dammerstein"))
    assert _mode(path) == 0o600
    stored = path.read_text(encoding="utf-8")
    serve.build("dammerstein")  # a restart reads the same key back
    assert path.read_text(encoding="utf-8") == stored
