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
storyguide's own network, Tailscale or ZeroTier. An address the internet
can reach is refused unless the storyguide insists (`is_public`), and the
web host answers only requests addressed to it (`request_allowed`).
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
from urllib.parse import urlsplit

from . import paths, settings, shapes

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
    port, or None for browsers only. `public_ok`: the storyguide insists on
    an address the internet can reach (never remembered: asked each time)."""

    address: str = LOCALHOST
    port: int = DEFAULT_PORT
    ssh_port: int | None = None
    public_ok: bool = False

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
        if self.public_ok:
            found.append(ALLOW_PUBLIC)
        return found


#: The server's flag for an address the internet can reach.
ALLOW_PUBLIC = "--allow-public"

#: Addresses that mean "every address this computer has", a public one
#: among them.
_EVERY_ADDRESS = frozenset({"", "0.0.0.0", "::", "*"})
_LOOPBACK_NAMES = frozenset({LOCALHOST, "127.0.0.1", "::1"})


def _global(text: str) -> bool:
    try:
        ip = ipaddress.ip_address(text.split("%")[0])
    except ValueError:
        return False
    return ip.is_global or ip.is_unspecified


def is_public(address: str, *, resolve: bool = True) -> bool:
    """Whether hosting on `address` lets the internet in: an address the
    internet routes to, or every address this computer has. Tailscale's
    and private networks' addresses aren't. A name is looked up unless
    `resolve` is False (then only a typed address is judged)."""
    address = address.strip()
    if address in _EVERY_ADDRESS:
        return True
    if address in _LOOPBACK_NAMES:
        return False
    try:
        ipaddress.ip_address(address.split("%")[0])
    except ValueError:
        if not resolve:
            return False
        try:
            infos = socket.getaddrinfo(address, None)
        except OSError:
            return False  # not an address at all: listening will say so
        return any(_global(str(info[4][0])) for info in infos)
    return _global(address)


#: How the Host for Players form insists on a public address.
INSIST = "tick “I know this is reachable from the internet”"


def public_refusal(address: str, *, insist: str = INSIST) -> str:
    """Why hosting on `address` is refused until the storyguide insists
    (`insist` says how)."""
    shown = address.strip() or "every address"
    return (
        f"{shown} can be reached from the internet: anyone there could open "
        "the app and try passcodes, and nothing they send or see is "
        "encrypted. Host on your Tailscale or ZeroTier address instead, or "
        f"{insist}."
    )


def allowed_hosts(address: str, port: int) -> frozenset[str]:
    """What a browser may send as the Host of a request to a host on
    `address`:`port` (and as the Origin of the page's own connection):
    that address, with loopback's other names for localhost, or this
    computer's addresses when it listens on all of them."""
    address = address.strip()
    if address in _EVERY_ADDRESS:
        names = {*_LOOPBACK_NAMES, *addresses()}
    elif address in _LOOPBACK_NAMES:
        names = set(_LOOPBACK_NAMES)
    else:
        names = {address}
    shown = {f"[{n}]" if ":" in n else n for n in names}
    found = {f"{n}:{port}" for n in shown}
    if port == 80:
        found |= shown  # a browser leaves the default port out
    return frozenset(n.lower() for n in found)


def request_allowed(
    host: str | None, origin: str | None, websocket: bool, allowed: frozenset[str]
) -> bool:
    """Whether the web host answers a request: its Host must be one of
    `allowed` (so a name that a hostile site points at this computer gets
    nothing), and the app's own connection (`websocket`) must come from
    the host's own page (so a page from another site can't open a copy)."""
    if (host or "").strip().lower() not in allowed:
        return False
    if not websocket:
        return True
    parts = urlsplit(origin or "")
    return parts.scheme in ("http", "https") and parts.netloc.lower() in allowed


#: How a hosted copy names its exports folder, instead of its place on
#: the host's disk.
EXPORTS_SHOWN = "exports"


class ConfinedFolder:
    """A folder a file chooser can't leave (a Proxy for the file system):
    a hosted copy's chooser shows only the exports folder and what is
    below it, and names them from there, never by their place on the
    host's disk."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()

    def holds(self, path: Path) -> bool:
        """Whether `path` (links followed) is the folder or inside it."""
        return path.resolve().is_relative_to(self.root)

    def find(self, typed: str) -> Path | None:
        """The file or folder `typed` names, as `show` writes it or as a
        path below the folder; None if it is outside."""
        text = typed.strip().strip('"').replace("\\", "/")
        if text == EXPORTS_SHOWN or text.startswith(EXPORTS_SHOWN + "/"):
            text = text[len(EXPORTS_SHOWN) :].lstrip("/")
        path = (self.root / text).resolve()
        return path if self.holds(path) else None

    def start(self, wanted: Path) -> Path:
        """`wanted` if it is inside, else the folder itself."""
        return wanted if wanted.is_dir() and self.holds(wanted) else self.root

    def up(self, folder: Path) -> Path:
        """The folder above `folder`, never above the folder itself."""
        parent = folder.resolve().parent
        return parent if self.holds(parent) else self.root

    def show(self, path: Path) -> str:
        """`path` named from the folder: "exports/Characters"."""
        inside = path.resolve().relative_to(self.root).as_posix()
        return EXPORTS_SHOWN if inside == "." else f"{EXPORTS_SHOWN}/{inside}"


def confined_chooser() -> ConfinedFolder | None:
    """In a hosted copy, the folder its file chooser keeps to (the exports
    folder, made if missing); None in the storyguide's own window, which
    may browse the whole computer."""
    if not is_hosted_copy():
        return None
    root = paths.data_dir() / paths.EXPORTS
    root.mkdir(parents=True, exist_ok=True)
    return ConfinedFolder(root)


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
        ssh = shapes.whole(saved.get("ssh_port"))
        return Plan(
            str(saved.get("address") or LOCALHOST),
            shapes.whole(saved.get("port"), DEFAULT_PORT),
            ssh or None,
        )
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
        if isinstance(plan, Plan) and not plan.public_ok and is_public(plan.address):
            return public_refusal(plan.address)
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
