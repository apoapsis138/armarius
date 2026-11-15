"""Where a saga is hosted for Remote seats: the tunnel's public address,
which tunnel it is, and the port on this computer the tunnel points at.

The listener (remote/serve.py) runs as a process of its own, started by
hosting.HOST from a RemotePlan as the browser host is started from a
hosting.Plan: two ways of hosting behind one Host (Strategy), so whatever
starts or stops it needn't know which is running.

The plan is remembered per saga in the host's remote folder, not the saga.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar
from urllib.parse import urlsplit

from .. import launch
from ..files import write_atomic
from .folder import remote_file

#: The one path the listener speaks the protocol on.
PATH = "/remote"
#: The port the tunnel points at unless the Storyguide chose another.
DEFAULT_PORT = 8790
LISTEN_ADDRESS = "127.0.0.1"

CLOUDFLARE, OTHER_TUNNEL = "cloudflare", "other"
#: Each tunnel the listener knows: its label, and the header it puts the
#: player's real address in. The listener takes only connections from this
#: computer, so the header can only come from the tunnel and is trusted.
TUNNELS: dict[str, tuple[str, str]] = {
    CLOUDFLARE: ("Cloudflare Tunnel", "CF-Connecting-IP"),
    OTHER_TUNNEL: ("Another tunnel (ngrok, Tailscale Funnel...)", "X-Forwarded-For"),
}


def identity_name(saga_id: str) -> str:
    """The name the saga's host key is kept under in the keychain: one key
    per saga, so rotating one saga's key leaves the others' Invites alone."""
    return f"host-key:{saga_id}"


def url_problem(text: str) -> str | None:
    """Why `text` can't be the tunnel's public address, or None if it can:
    an https address with a host name and nothing after it."""
    pieces = urlsplit(text.strip())
    if pieces.scheme != "https" or not pieces.hostname:
        return "Type the tunnel's https address, such as https://saga.example.com."
    if pieces.path not in ("", "/") or pieces.query or pieces.fragment:
        return "Give the tunnel's address only, with nothing after the name."
    if pieces.username or pieces.password:
        return "The address can't carry a name or password."
    return None


@dataclass(frozen=True)
class RemotePlan:
    """Host `saga_id` for Remote seats: listen on this computer's `port`,
    which the Storyguide's tunnel at `public_url` points at."""

    saga_id: str
    saga_name: str
    public_url: str
    port: int = DEFAULT_PORT
    tunnel: str = CLOUDFLARE

    word: ClassVar[str] = launch.SEATS

    @property
    def address(self) -> str:
        """Where the listener listens: this computer only."""
        return LISTEN_ADDRESS

    def arguments(self) -> list[str]:
        """The listener's command-line arguments (serve.py's own)."""
        return [
            "--saga",
            self.saga_id,
            "--port",
            str(self.port),
            "--tunnel",
            self.tunnel,
        ]

    def ports(self) -> list[int]:
        return [self.port]

    def invite_url(self) -> str:
        """The address an Invite carries: the tunnel's, as a secure
        WebSocket, at the listener's one path."""
        host = urlsplit(self.public_url.strip()).netloc
        return f"wss://{host}{PATH}"

    def tunnel_target(self) -> str:
        """What the Storyguide points the tunnel at."""
        return f"http://localhost:{self.port}"

    def remember(self) -> None:
        write_atomic(
            plan_path(self.saga_name),
            json.dumps(
                {
                    "public_url": self.public_url,
                    "port": self.port,
                    "tunnel": self.tunnel,
                },
                indent=1,
            ),
        )


def plan_path(saga_name: str) -> Path:
    return remote_file(saga_name, "host.json")


def last_plan(saga_id: str, saga_name: str) -> RemotePlan:
    """The saga's plan as last used, or the defaults (no address yet). A
    file that can't be read gives the defaults: it holds no secret, and the
    form shows what will be used before anything starts."""
    try:
        data = json.loads(plan_path(saga_name).read_text(encoding="utf-8"))
    except OSError, ValueError:
        data = None
    if not isinstance(data, dict):
        return RemotePlan(saga_id, saga_name, "")
    url, port, tunnel = data.get("public_url"), data.get("port"), data.get("tunnel")
    return RemotePlan(
        saga_id,
        saga_name,
        url if isinstance(url, str) else "",
        port if isinstance(port, int) and 1 <= port <= 65535 else DEFAULT_PORT,
        tunnel if isinstance(tunnel, str) and tunnel in TUNNELS else CLOUDFLARE,
    )
