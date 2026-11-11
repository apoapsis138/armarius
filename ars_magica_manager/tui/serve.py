"""The host for players: browsers with textual-serve, and, with
--ssh-port, SSH clients too.

    python -m ars_magica_manager.tui.serve [--host ADDRESS] [--port N] [--ssh-port N]

Each browser tab or SSH session gets its own copy of the app (a separate
process), all using this computer's data folder. It listens on localhost
unless another address is given -- the storyguide's Tailscale or ZeroTier
address, never a public one. Who each player is comes from the app's own
sign-in (its Players node). tools/serve.py runs it in a terminal; the
core's hosting.HOST runs it as a process of its own for Host for Players.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from aiohttp import web
from textual_serve import server as serve_module
from textual_serve.server import Server

from .. import hosting as core_hosting
from ..remote.identity import NoKeychainError
from . import hosting

MAIN = Path(__file__).resolve().parent.parent.parent / "main.py"

# textual-serve builds each browser copy's service by this name.
setattr(serve_module, "AppService", hosting.HostedAppService)  # noqa: B010 (pyright: not exported)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Host the app for players.")
    parser.add_argument(
        "--host",
        default=core_hosting.LOCALHOST,
        help="address to listen on (localhost)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=core_hosting.DEFAULT_PORT,
        help=f"browser port ({core_hosting.DEFAULT_PORT})",
    )
    parser.add_argument(
        "--ssh-port",
        type=int,
        default=None,
        help="also take SSH clients on this port "
        f"(off unless given; try {core_hosting.DEFAULT_SSH_PORT})",
    )
    args = parser.parse_args(argv)
    command = f'"{sys.executable}" "{MAIN}"'
    server = Server(command, host=args.host, port=args.port, title="Armarius")
    server.initialize_logging()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if args.ssh_port is not None:
            try:
                loop.run_until_complete(
                    hosting.start_ssh_server(command, args.host, args.ssh_port)
                )
            except (NoKeychainError, ValueError) as problem:
                sys.exit(f"Can't take SSH clients: {problem}")
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
            "This computer's addresses: "
            f"{', '.join(core_hosting.addresses()) or 'none found'}.\n"
            "Use one of those (your Tailscale or ZeroTier one to reach players), "
            "or another --port / --ssh-port if that one is in use."
        )


if __name__ == "__main__":
    main()
