"""Hosting the app for SSH clients: a real SSH client gets a
real copy of the app, with the saga list and sign-in a browser gets."""

from __future__ import annotations

import asyncio
import re
import sys
from pathlib import Path

import asyncssh
import pytest

from ars_magica_manager import hosting as core_hosting
from ars_magica_manager import players as pl
from ars_magica_manager import storage
from ars_magica_manager.models import Saga
from ars_magica_manager.remote.identity import MemoryStore
from ars_magica_manager.tui import hosting

MAIN = Path(__file__).resolve().parent.parent / "main.py"

#: Terminal control sequences, so the app's screen can be read as text.
_ESCAPES = re.compile(r"\x1b(\[[0-9;?]*[ -/]*[@-~]|\][^\x07]*\x07|[@-Z\\-_])")


def _text(output: bytes) -> str:
    return _ESCAPES.sub("", output.decode("utf-8", "replace"))


async def _read_until(process, wanted: str, timeout: float = 20.0) -> str:
    seen = b""
    deadline = asyncio.get_running_loop().time() + timeout
    while wanted not in _text(seen):
        left = deadline - asyncio.get_running_loop().time()
        assert left > 0, f"never saw {wanted!r} in:\n{_text(seen)[-2000:]}"
        try:
            seen += await asyncio.wait_for(process.stdout.read(4096), timeout=left)
        except asyncio.IncompleteReadError:
            break
    return _text(seen)


@pytest.fixture
def hosted_data(tmp_path, monkeypatch):
    """A data folder with one saga and one player, used by the app copies
    the SSH server starts (they read the environment, not this process's
    monkeypatched storage), and by this process's host key."""
    data = tmp_path / "hosted"
    monkeypatch.setenv(hosting.paths.ENV_VAR, str(data))
    monkeypatch.setattr(hosting.paths, "_in_use", data)
    monkeypatch.setattr(hosting.paths, "data_dir", lambda: data)
    saga = Saga(id="dammerstein", name="Dammerstein")
    pl.add(saga, {"name": "Ana", "role": pl.PLAYER, "passcode": "rosemary and rue"})
    storage.save_saga(saga)
    return data


async def test_an_ssh_client_gets_the_app_and_signs_in(hosted_data):
    command = f'"{sys.executable}" "{MAIN}"'
    store = MemoryStore()
    server = await hosting.start_ssh_server(command, "127.0.0.1", 0, store)
    port = server.sockets[0].getsockname()[1]
    # Made on the first host, in the keychain, never in the synced folder.
    assert store.get(hosting.HOST_KEY_NAME)
    assert not any(hosted_data.glob("*host_key*"))
    try:
        async with asyncssh.connect(
            "127.0.0.1", port, username="anyone", known_hosts=None
        ) as conn:
            process = await conn.create_process(
                term_type="xterm-256color", term_size=(140, 60), encoding=None
            )
            # The saga list, as a browser sees it: sign in, no New/Delete.
            screen = await _read_until(process, "Select a saga to open and sign in.")
            assert "Dammerstein" in screen
            assert "New Saga" not in screen
            process.stdin.write(b"\r")  # open it: the sign-in dialog
            screen = await _read_until(process, "Sign in to Dammerstein")
            for keys in (b"Ana", b"\t", b"rosemary and rue", b"\t", b"\r"):  # as typed
                process.stdin.write(keys)
                await asyncio.sleep(0.2)
            screen = await _read_until(process, "| Ana")  # signed in: the header
            assert "Players" not in screen  # a player doesn't see who else can
            process.stdin.write(b"q")
            await asyncio.wait_for(process.wait(), timeout=10)
    finally:
        server.close()
        await server.wait_closed()
        # Let the app copy's pipes finish closing before the loop goes, or
        # Windows' asyncio warns of an unclosed transport.
        await asyncio.sleep(0.5)


def test_an_old_host_key_file_moves_into_the_keychain(hosted_data):
    """A key an older version left in the synced data folder is kept (so
    players' SSH clients still know the host), moved to the keychain, and
    the file deleted."""
    old = asyncssh.generate_private_key("ssh-ed25519")
    hosting.old_host_key_path().write_bytes(old.export_private_key())
    store = MemoryStore()
    key = hosting.host_key(store)
    assert key.export_public_key() == old.export_public_key()
    assert not hosting.old_host_key_path().exists()
    again = hosting.host_key(store)  # read back from the keychain
    assert again.export_public_key() == old.export_public_key()


def test_an_unreadable_host_key_is_reported(hosted_data):
    store = MemoryStore()
    store.set(hosting.HOST_KEY_NAME, "not a key")
    with pytest.raises(ValueError, match="cannot be read"):
        hosting.host_key(store)


def test_a_copy_knows_how_it_is_reached(monkeypatch):
    monkeypatch.delenv(core_hosting.TRANSPORT_VAR, raising=False)
    monkeypatch.delenv(core_hosting.OLD_TRANSPORT_VAR, raising=False)
    assert core_hosting.transport() == ""
    # The variable's name before the rename is still read.
    monkeypatch.setenv(core_hosting.OLD_TRANSPORT_VAR, "web")
    assert core_hosting.transport() == "web"
    monkeypatch.setenv(core_hosting.TRANSPORT_VAR, "ssh")
    assert core_hosting.transport() == "ssh"

    async def nothing(*_args) -> None:
        pass

    service = hosting._SshAppService(
        "python",
        write_bytes=nothing,
        write_str=nothing,
        close=nothing,
        download_manager=hosting.DownloadManager(),
    )
    environment = service._build_environment(120, 45)
    assert environment[hosting.TRANSPORT_VAR] == "ssh"
    assert environment["COLUMNS"] == "120"
