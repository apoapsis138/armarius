"""Hosting the app for players: the pieces serve.py runs.

Each player gets their own copy of the app, a separate process running
Textual's web driver, which talks to this process in packets: terminal
output and input as data, resizes and the like as meta. textual-serve's
AppService drives such a copy; here it is adapted for Windows and shared
by the two ways in:

- a browser (textual-serve's web page);
- an SSH client: an SSH server in this process, no accounts
  on the host; each session is one app copy, its terminal bytes passed
  straight through.

Either way, who the player is comes from the app's own sign-in
(players.py), never from the connection.
"""

from __future__ import annotations

import asyncio
import sys
from collections.abc import Awaitable, Callable, Mapping
from pathlib import Path

import asyncssh
from aiohttp import web
from aiohttp.typedefs import Middleware
from textual_serve.app_service import AppService
from textual_serve.download_manager import DownloadManager

from .. import paths
from ..hosting import TRANSPORT_VAR, request_allowed
from ..remote.identity import KeychainStore, KeyStore


class HostedAppService(AppService):
    """One hosted copy of the app.

    Ends the copy when its connection goes: textual-serve asks the copy to
    quit and waits forever, but on Windows
    the copy never quits, so each closed tab left a copy running. Here it
    gets a moment to quit, then it is ended."""

    #: What TRANSPORT_VAR says to the copy.
    transport = "web"

    def _build_environment(self, width: int = 80, height: int = 24) -> dict[str, str]:
        environment = super()._build_environment(width, height)
        environment[TRANSPORT_VAR] = self.transport
        return environment

    async def stop(self) -> None:
        if self._task is None:
            return
        await self._download_manager.cancel_app_downloads(
            app_service_id=self.app_service_id
        )
        await self.send_meta({"type": "quit"})
        try:
            await asyncio.wait_for(asyncio.shield(self._task), timeout=2)
        except TimeoutError:
            process = self._process
            if process is not None and process.returncode is None:
                if sys.platform == "win32":
                    # The command runs through a shell: end the whole tree.
                    killer = await asyncio.create_subprocess_exec(
                        "taskkill",
                        "/PID",
                        str(process.pid),
                        "/T",
                        "/F",
                        stdout=asyncio.subprocess.DEVNULL,
                        stderr=asyncio.subprocess.DEVNULL,
                    )
                    await killer.wait()
                else:
                    process.kill()
            await self._task
        self._task = None
        process = self._process
        if process is not None:
            # Its pipes are done with (the stderr one was still open):
            # close them now rather than when they're collected.
            transport = getattr(process, "_transport", None)
            if transport is not None:
                transport.close()


class _SshAppService(HostedAppService):
    transport = "ssh"


# -- the web host's requests -------------------------------------------------

#: What a request not addressed to the host is told.
_NOT_ADDRESSED = "This host answers only its own address."

type _Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


def addressed_to(allowed: frozenset[str]) -> Middleware:
    """An aiohttp middleware (one more link in its Chain of Responsibility,
    in front of textual-serve's handlers) that refuses a request whose
    Host isn't one of `allowed`, and an app connection (/ws) whose Origin
    isn't the host's own page (core_hosting.request_allowed)."""

    @web.middleware
    async def check(request: web.Request, handler: _Handler) -> web.StreamResponse:
        if not request_allowed(
            request.headers.get("Host"),
            request.headers.get("Origin"),
            request.path == "/ws",
            allowed,
        ):
            raise web.HTTPForbidden(text=_NOT_ADDRESSED)
        return await handler(request)

    return check


# -- SSH ---------------------------------------------------------------------

#: The size an SSH client gets when it asked for no terminal.
_DEFAULT_SIZE = (80, 24)


class _Session(asyncssh.SSHServerSession):
    """One SSH session: an app copy whose terminal is the client's."""

    def __init__(self, command: str, downloads: DownloadManager) -> None:
        self._command = command
        self._downloads = downloads
        self._chan: asyncssh.SSHServerChannel | None = None
        self._service: HostedAppService | None = None
        self._focused = False

    def connection_made(self, chan: asyncssh.SSHServerChannel) -> None:
        self._chan = chan

    def pty_requested(
        self,
        term_type: str,
        term_size: tuple[int, int, int, int],
        term_modes: Mapping[int, int],
    ) -> bool:
        return True

    def shell_requested(self) -> bool:
        return True

    def session_started(self) -> None:
        chan = self._chan
        assert chan is not None

        async def write(data: bytes) -> None:
            chan.write(data)
            if not self._focused:
                # The copy starts blurred (nothing has focus) until told the
                # terminal is looked at, as a browser's page says when it is
                # clicked. An SSH client always is: say so once the copy
                # is up, after its start-up blur.
                self._focused = True
                asyncio.create_task(self._focus_soon())

        async def write_str(data: str) -> None:
            pass  # a browser's messages (open a URL, a download): nothing here

        async def close() -> None:
            chan.close()

        self._service = _SshAppService(
            self._command,
            write_bytes=write,
            write_str=write_str,
            close=close,
            download_manager=self._downloads,
        )
        width, height, _, _ = chan.get_terminal_size() or (*_DEFAULT_SIZE, 0, 0)
        asyncio.create_task(self._service.start(width or 80, height or 24))

    async def _focus_soon(self) -> None:
        await asyncio.sleep(0.5)
        if self._service is not None:
            await self._service.focus()

    def data_received(self, data: bytes, datatype: int | None) -> None:
        if self._service is not None:
            asyncio.create_task(self._service.send_bytes(data))

    def terminal_size_changed(
        self, width: int, height: int, pixwidth: int, pixheight: int
    ) -> None:
        if self._service is not None:
            asyncio.create_task(self._service.set_terminal_size(width, height))

    def eof_received(self) -> bool:
        self._end()
        return False

    def connection_lost(self, exc: Exception | None) -> None:
        self._end()

    def _end(self) -> None:
        service, self._service = self._service, None
        if service is not None:
            asyncio.create_task(service.stop())


class _Server(asyncssh.SSHServer):
    """Lets anyone on the private network in: who they are is the app's
    sign-in, as in a browser (players.py). Each session is a _Session."""

    def __init__(self, command: str, downloads: DownloadManager) -> None:
        self._command = command
        self._downloads = downloads

    def begin_auth(self, username: str) -> bool:
        return False  # no SSH-level authentication

    def session_requested(self) -> asyncssh.SSHServerSession:
        return _Session(self._command, self._downloads)


#: The SSH host key's name in the keychain.
HOST_KEY_NAME = "ssh-host-key"


def old_host_key_path() -> Path:
    """Where older versions kept the SSH host key: the data folder, which
    a cloud folder syncs. Read once, moved into the keychain, deleted."""
    return paths.data_dir() / paths.HOST_KEY


def host_key(store: KeyStore) -> asyncssh.SSHKey:
    """The host's SSH key, kept in `store` (the keychain), never in the
    synced data folder; made on the first SSH host. NoKeychainError with
    no keychain."""
    text = store.get(HOST_KEY_NAME)
    if text is None:
        old = old_host_key_path()
        if old.is_file():
            key = asyncssh.import_private_key(old.read_bytes())
        else:
            key = asyncssh.generate_private_key("ssh-ed25519")
        store.set(HOST_KEY_NAME, key.export_private_key().decode("ascii"))
        old.unlink(missing_ok=True)
        return key
    try:
        return asyncssh.import_private_key(text)
    except asyncssh.KeyImportError as exc:
        raise ValueError("The SSH host key in the keychain cannot be read.") from exc


async def start_ssh_server(
    command: str, host: str, port: int, store: KeyStore | None = None
) -> asyncssh.SSHAcceptor:
    """Listen for SSH clients on `host`:`port`; each session runs `command`
    (the app) as its own copy. The host key is kept in `store` (the
    keychain unless given)."""
    downloads = DownloadManager()
    return await asyncssh.create_server(
        lambda: _Server(command, downloads),
        host,
        port,
        server_host_keys=[host_key(store or KeychainStore())],
        encoding=None,
    )
