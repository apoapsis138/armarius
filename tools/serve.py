"""Host the app for players' browsers (STORY-1402 spike).

    uv run python tools/serve.py [--host ADDRESS] [--port N]

Serves the app with textual-serve: each browser tab that opens the page gets
its own copy of the app (a separate process), all using this computer's data
folder. It listens on localhost unless another address is given -- the
storyguide's Tailscale or ZeroTier address, never a public one. There is no
sign-in yet (STORY-1403), so anyone who can reach the address has the app.
"""

from __future__ import annotations

import argparse
import asyncio
import socket
import sys
from pathlib import Path

from textual_serve import server as serve_module
from textual_serve.app_service import AppService
from textual_serve.server import Server

MAIN = Path(__file__).resolve().parent.parent / "main.py"


class _AppService(AppService):
    """Ends the app copy when its browser tab goes. textual-serve asks the
    copy to quit and waits for it forever, but on Windows (seen in the
    STORY-1402 spike) the copy never quits, so each closed tab left a copy
    running. Here it gets a moment to quit, then it is ended."""

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


# textual-serve builds each copy's service by this name.
setattr(serve_module, "AppService", _AppService)  # noqa: B010 (pyright: not exported)


def main() -> None:
    parser = argparse.ArgumentParser(description="Host the app for players' browsers.")
    parser.add_argument(
        "--host", default="localhost", help="address to listen on (localhost)"
    )
    parser.add_argument("--port", type=int, default=8000, help="port (8000)")
    args = parser.parse_args()
    command = f'"{sys.executable}" "{MAIN}"'
    try:
        Server(
            command, host=args.host, port=args.port, title="Ars Magica Manager"
        ).serve()
    except OSError as error:
        sys.exit(
            f"Can't listen on {args.host}:{args.port} ({error.strerror or error}).\n"
            f"This computer's addresses: {', '.join(_addresses()) or 'none found'}.\n"
            "Use one of those (your Tailscale or ZeroTier one to reach players), "
            "or another --port if that one is in use."
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
