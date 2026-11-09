"""The listener for Remote seats, as a process of its own.

    python -m ars_magica_manager.remote.serve --saga ID [--port N] [--tunnel KIND]

hosting.HOST starts it from a remote.plan.RemotePlan when the Storyguide
hosts for Remote seats. It runs apart from the Storyguide's window so that
the one part of the app that reads strangers' messages can fail, or be
ended, without the window (threat model, section 4). It listens on this
computer only; the Storyguide's tunnel brings players to it.

It shares the saga's Remote seat files with the window (folder.SharedFile):
the window issues, approves and revokes; this process redeems and signs in.
A device the window revokes is cut off here within a second (`watch`), and
before then each message checks the device first.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from collections.abc import Callable

from .. import players, storage
from ..models import Player
from .audit import AuditLog, audit_path
from .changes import SeatChanges
from .devices import DeviceBook, devices_path
from .host import RemoteHost
from .identity import KeychainStore, KeyStore, NoKeychainError, load_or_create
from .invites import InviteBook, book_path
from .limits import Limits
from .passcode_change import passcode_specs
from .passcodes import RemotePasscodes, passcodes_path
from .plan import CLOUDFLARE, DEFAULT_PORT, LISTEN_ADDRESS, TUNNELS, identity_name
from .records import SeatSnapshots, picture_from_disk, seat_registry
from .redemption import door_registry

#: How often the listener looks for devices the window has revoked.
WATCH_EVERY = 1.0


class SagaPlayers:
    """The saga's Players as the file holds them now: read again only when
    the file has changed, since a lookup comes with every message."""

    def __init__(self, saga_id: str) -> None:
        self._saga_id = saga_id
        self._stamp = -1
        self._players: dict[str, Player] = {}

    def get(self, player_id: str) -> Player | None:
        """The Player of that id, or None (no such player, or the saga's
        file is gone: nobody signs in to a saga that isn't there)."""
        try:
            stamp = os.stat(storage.saga_path(self._saga_id)).st_mtime_ns
        except OSError:
            return None
        if stamp != self._stamp:
            saga = storage.load_saga(self._saga_id)
            self._players = {p.id: p for p in saga.players if p.role == players.PLAYER}
            self._stamp = stamp
        return self._players.get(player_id)


def build(
    saga_id: str,
    tunnel: str = CLOUDFLARE,
    store: KeyStore | None = None,
    player_of: Callable[[str], Player | None] | None = None,
) -> tuple[RemoteHost, DeviceBook]:
    """The listener for `saga_id` and the devices book it checks. Raises
    NoKeychainError with no keychain, OSError or ValueError if the saga
    or one of its Remote seat files can't be read."""
    name = storage.load_saga(saga_id).name
    log = AuditLog(audit_path(name))
    book = InviteBook(book_path(name), log=log)
    devices = DeviceBook(devices_path(name), log=log)
    passcodes = RemotePasscodes(passcodes_path(name))
    identity = load_or_create(store or KeychainStore(), identity_name(saga_id))
    limits = Limits()
    registry = door_registry(
        limits.max_message,
        book,
        devices,
        player_of or SagaPlayers(saga_id).get,
        lambda: identity.pin,
        passcodes,
    )
    snapshots = SeatSnapshots(saga_id, log)
    host = RemoteHost(
        identity,
        registry,
        limits,
        members=seat_registry(
            snapshots,
            picture_from_disk,
            SeatChanges(saga_id, log),
            more=passcode_specs(saga_id, passcodes, log),
        ),
        # Only the tunnel, on this computer, can reach the listener, so the
        # address it passes on is the player's own (threat model, section 4).
        trust_forwarded_address=True,
        forwarded_header=TUNNELS[tunnel][1],
    )
    return host, devices


async def watch(
    host: RemoteHost, devices: DeviceBook, every: float = WATCH_EVERY
) -> None:
    """Cut off, at once, every open connection whose device has ended (the
    window revoked it, or the host key was rotated)."""
    while True:
        for device_id in host.connected():
            if not devices.is_live(device_id):
                await host.disconnect(device_id)
        await asyncio.sleep(every)


async def _serve(host: RemoteHost, devices: DeviceBook, port: int) -> None:
    await host.start(port, LISTEN_ADDRESS)
    try:
        await watch(host, devices)
    finally:
        await host.stop()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Host a saga for Remote seats.")
    parser.add_argument("--saga", required=True, help="the saga's id")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--tunnel", choices=sorted(TUNNELS), default=CLOUDFLARE)
    args = parser.parse_args(argv)
    try:
        host, devices = build(args.saga, args.tunnel)
    except NoKeychainError as error:
        sys.exit(str(error))
    except (OSError, ValueError) as error:
        sys.exit(f"Can't host the saga for Remote seats: {error}")
    try:
        asyncio.run(_serve(host, devices, args.port))
    except OSError as error:
        sys.exit(
            f"Can't listen on port {args.port} ({error.strerror or error}). "
            "Another program may have it: choose another port."
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
