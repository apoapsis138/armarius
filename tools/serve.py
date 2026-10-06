"""Host the app for players (FEAT-14).

    uv run python tools/serve.py [--host ADDRESS] [--port N] [--ssh-port N]

Serves the app for browsers with textual-serve, and, with --ssh-port, for
SSH clients too (STORY-1408). Each browser tab or SSH session gets its own
copy of the app (a separate process), all using this computer's data
folder. It listens on localhost unless another address is given -- the
storyguide's Tailscale or ZeroTier address, never a public one. Who each
player is comes from the app's own sign-in (its Players node).
"""

from __future__ import annotations

import argparse
import asyncio
import socket
import sys
from pathlib import Path

from aiohttp import web
from textual_serve import server as serve_module
from textual_serve.server import Server

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))  # run as a script: the package is beside tools/
from ars_magica_manager import hosting

MAIN = REPO / "main.py"

# textual-serve builds each browser copy's service by this name.
setattr(serve_module, "AppService", hosting.HostedAppService)  # noqa: B010 (pyright: not exported)


def main() -> None:
    parser = argparse.ArgumentParser(description="Host the app for players.")
    parser.add_argument(
        "--host", default="localhost", help="address to listen on (localhost)"
    )
    parser.add_argument("--port", type=int, default=8000, help="browser port (8000)")
    parser.add_argument(
        "--ssh-port",
        type=int,
        default=None,
        help="also take SSH clients on this port (off unless given; try 2222)",
    )
    args = parser.parse_args()
    command = f'"{sys.executable}" "{MAIN}"'
    server = Server(command, host=args.host, port=args.port, title="Ars Magica Manager")
    server.initialize_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if args.ssh_port is not None:
            loop.run_until_complete(
                hosting.start_ssh_server(command, args.host, args.ssh_port)
            )
            print(f"SSH: ssh -p {args.ssh_port} player@{args.host}")
        web.run_app(
            server._make_app(),
            host=args.host,
            port=args.port,
            loop=loop,
            handle_signals=False,
            print=lambda *args: None,
        )
    except OSError as error:
        sys.exit(
            f"Can't listen on {args.host} ({error.strerror or error}).\n"
            f"This computer's addresses: {', '.join(_addresses()) or 'none found'}.\n"
            "Use one of those (your Tailscale or ZeroTier one to reach players), "
            "or another --port / --ssh-port if that one is in use."
        )


def _addresses() -> list[str]:
    """This computer's IPv4 addresses, for the can't-listen message."""
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return []
    return sorted({str(info[4][0]) for info in infos})


if __name__ == "__main__":
    main()
