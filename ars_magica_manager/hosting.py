"""Hosting the app for players, as either front-end starts it.

One service, `HOST`, starts and stops the host: a separate process
running tui/serve.py's server, which gives each browser tab (and, with
an SSH port, each SSH session) its own copy of the terminal app. The
desktop starts it from Saga Management, the terminal from More or by
running tools/serve.py itself; neither needs to know how the server is
built (a Facade). It runs as its own process because the server is the
terminal front-end's code, which the core and the desktop never import,
and so that it can be ended whole, with every player's copy.

Whatever starts it, the host listens only on the address given: the
storyguide's own network, Tailscale or ZeroTier, never a public one.
"""

from __future__ import annotations

import atexit
import errno
import ipaddress
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import IO, ClassVar, Protocol

from . import paths, settings

#: How a hosted copy is reached, told to it in this environment variable:
#: "web" (a browser) or "ssh".
TRANSPORT_VAR = "ARMARIUS_TRANSPORT"
#: The variable's name before the app was Armarius, still read.
OLD_TRANSPORT_VAR = "ARS_MAGICA_MANAGER_TRANSPORT"

DEFAULT_PORT = 8000
DEFAULT_SSH_PORT = 2222
LOCALHOST = "localhost"

#: The module the host process runs (python -m), from the package's folder.
SERVER_MODULE = "ars_magica_manager.tui.serve"
_PACKAGE_PARENT = Path(__file__).resolve().parent.parent

#: How long a starting host has to begin listening (the server loads
#: Textual's web driver first).
START_TIMEOUT = 20.0
#: How long a stopping host has to end before it is killed.
STOP_TIMEOUT = 3.0

#: Tailscale gives each computer an address in this range.
_TAILSCALE = ipaddress.ip_network("100.64.0.0/10")


def transport() -> str:
    """How this copy of the app is reached: "web", "ssh", or "" for the
    storyguide's own window."""
    return os.environ.get(TRANSPORT_VAR) or os.environ.get(OLD_TRANSPORT_VAR, "")


def is_hosted_copy() -> bool:
    """Whether this copy is a player's, run by a host: it never hosts."""
    return bool(transport())


class Hosting(Protocol):
    """A way of hosting the saga (Strategy): the process HOST starts, the
    address and ports it listens on, and how it remembers itself for next
    time. Plan is the browser and SSH host; remote.plan.RemotePlan the
    listener for Remote seats."""

    module: ClassVar[str]

    @property
    def address(self) -> str: ...

    def arguments(self) -> list[str]: ...

    def ports(self) -> list[int]: ...

    def remember(self) -> None: ...


@dataclass(frozen=True)
class Plan:
    """Where a host listens: `address`, its browser `port`, and an SSH
    port, or None for browsers only."""

    address: str = LOCALHOST
    port: int = DEFAULT_PORT
    ssh_port: int | None = None

    module: ClassVar[str] = SERVER_MODULE

    def ports(self) -> list[int]:
        return [self.port] + ([self.ssh_port] if self.ssh_port is not None else [])

    def remember(self) -> None:
        settings.update_settings(
            hosting={
                "address": self.address,
                "port": self.port,
                "ssh_port": self.ssh_port,
            }
        )

    def browser_url(self) -> str:
        return f"http://{self.address}:{self.port}"

    def ssh_command(self) -> str:
        return f"ssh -p {self.ssh_port} player@{self.address}" if self.ssh_port else ""

    def arguments(self) -> list[str]:
        """The server's command-line arguments (tools/serve.py's own)."""
        found = ["--host", self.address, "--port", str(self.port)]
        if self.ssh_port is not None:
            found += ["--ssh-port", str(self.ssh_port)]
        return found


def addresses() -> list[str]:
    """This computer's IPv4 addresses, loopback left out."""
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return []
    found = {str(info[4][0]) for info in infos}
    return sorted(a for a in found if not a.startswith("127."))


def address_label(address: str) -> str:
    """`address` as a host form offers it: "100.101.1.2 (Tailscale)"."""
    if address == LOCALHOST:
        return "localhost (this computer only)"
    try:
        ip = ipaddress.ip_address(address)
    except ValueError:
        return address
    if ip in _TAILSCALE:
        return f"{address} (Tailscale)"
    if ip.is_private:
        return f"{address} (a private network)"
    return f"{address} (reachable from the internet: don't)"


def last_plan() -> Plan:
    """Where the storyguide last hosted, or the defaults: an address on
    Tailscale if this computer has one, else localhost."""
    saved = settings.load_settings().get("hosting")
    if isinstance(saved, dict):
        try:
            ssh = saved.get("ssh_port")
            return Plan(
                str(saved.get("address") or LOCALHOST),
                int(saved.get("port") or DEFAULT_PORT),
                int(ssh) if ssh else None,
            )
        except TypeError, ValueError:
            pass
    tailscale = [a for a in addresses() if ipaddress.ip_address(a) in _TAILSCALE]
    return Plan(tailscale[0] if tailscale else LOCALHOST)


def _listen_problem(address: str, port: int) -> str | None:
    """Why the host couldn't listen on `address`:`port`, or None if it can."""
    try:
        infos = socket.getaddrinfo(address, port, socket.AF_INET, socket.SOCK_STREAM)
    except OSError:
        return f"{address} isn't an address this computer knows."
    for info in infos:
        probe = socket.socket(info[0], info[1])
        if sys.platform != "win32":
            # As the server's own socket does, so a port a stopped host
            # used a moment ago counts as free.
            probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind(info[4])
        except OSError as error:
            if error.errno in _IN_USE:
                return (
                    f"Port {port} is in use: another program (or a host left "
                    "running) has it. Choose another port."
                )
            return f"Can't listen on {address} ({error.strerror or error})."
        finally:
            probe.close()
    return None


#: The errors a port already taken gives (Windows has its own number).
_IN_USE = {errno.EADDRINUSE, 10048}


def _listening(address: str, port: int) -> bool:
    try:
        with socket.create_connection((address, port), timeout=0.2):
            return True
    except OSError:
        return False


def _python() -> str:
    """The Python to run the server with: never pythonw, whose copies
    would have no console streams for the server to hand on."""
    executable = Path(sys.executable)
    if executable.stem.lower() == "pythonw":
        console = executable.with_name("python" + executable.suffix)
        if console.exists():
            return str(console)
    return str(executable)


class Host:
    """The host for players, if this copy of the app has started one."""

    def __init__(self) -> None:
        self._process: subprocess.Popen[bytes] | None = None
        self._errors: IO[bytes] | None = None
        self.plan: Hosting | None = None

    @property
    def running(self) -> bool:
        process = self._process
        if process is not None and process.poll() is not None:
            self._forget()
        return self._process is not None

    def start(self, plan: Hosting) -> str | None:
        """Start hosting as `plan` says, waiting until the host listens.
        Returns why it couldn't (plain text), or None once it does."""
        if self.running:
            return "The saga is already hosted. Stop Hosting first."
        if is_hosted_copy():
            return "Only the storyguide's own window can host."
        ports = plan.ports()
        if len(set(ports)) < len(ports):
            return "The browser port and the SSH port must differ."
        for port in ports:
            problem = _listen_problem(plan.address, port)
            if problem is not None:
                return problem
        errors = tempfile.TemporaryFile()  # noqa: SIM115 (kept while the host runs)
        try:
            process = subprocess.Popen(
                [_python(), "-m", plan.module, *plan.arguments()],
                cwd=_PACKAGE_PARENT,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=errors,
                creationflags=_CREATION_FLAGS,
                start_new_session=sys.platform != "win32",
                # The host uses the data folder this copy uses.
                env={**os.environ, paths.ENV_VAR: str(paths.data_dir())},
            )
        except OSError as error:
            errors.close()
            return f"Couldn't start the host ({error.strerror or error})."
        self._process, self._errors, self.plan = process, errors, plan
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            if process.poll() is not None:
                said = self._said()
                self._forget()
                return said or "The host stopped as it started."
            if _listening(plan.address, ports[0]):
                plan.remember()
                return None
            time.sleep(0.1)
        self.stop()
        return "The host didn't start listening in time."

    def stop(self) -> None:
        """Stop hosting, ending every player's copy with the host."""
        process = self._process
        if process is None:
            return
        if process.poll() is None:
            _end(process)
        self._forget()

    def _said(self) -> str:
        """What the host wrote before it stopped (its last lines)."""
        errors = self._errors
        if errors is None:
            return ""
        errors.seek(0)
        said = errors.read().decode("utf-8", "replace").strip()
        return "\n".join(said.splitlines()[-4:])

    def _forget(self) -> None:
        if self._errors is not None:
            self._errors.close()
        self._process = self._errors = None
        self.plan = None


#: A host on Windows is its own process group with no console window of
#: its own (elsewhere, its own session), so it can be ended whole.
_CREATION_FLAGS = (
    subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
    if sys.platform == "win32"
    else 0
)


def _end(process: subprocess.Popen[bytes]) -> None:
    """End the host and the players' copies it started."""
    if sys.platform == "win32":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW,
            check=False,
        )
    else:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
    try:
        process.wait(STOP_TIMEOUT)
    except subprocess.TimeoutExpired:
        if sys.platform != "win32":
            os.killpg(process.pid, signal.SIGKILL)
        process.kill()
        process.wait()


#: This copy's host. A host outlives nothing: closing the app stops it.
HOST = Host()
atexit.register(HOST.stop)
