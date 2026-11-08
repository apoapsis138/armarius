"""What the Storyguide can do to Remote seats that already exist.

Two actions, each with an immediate effect on connections that are open
now. The screens call these and decide nothing themselves.

The Storyguide's window runs `revoke` and `rotate`: the listener, a process
of its own, sees the devices file change and cuts the connections (serve.
watch). The async forms do the same with the listener in hand, cutting the
connections themselves.
"""

from __future__ import annotations

from . import audit
from .devices import DeviceBook
from .host import RemoteHost
from .identity import HostIdentity, KeyStore
from .identity import rotate as new_identity
from .invites import InviteBook


def revoke(devices: DeviceBook, device_id: str) -> None:
    """End a device. LookupError if it is not a live device."""
    devices.revoke(device_id)


def rotate(
    store: KeyStore,
    name: str,
    invites: InviteBook,
    devices: DeviceBook,
    log: audit.AuditLog | None,
) -> HostIdentity:
    """Replace the host's key. Every Invite, request and Device credential
    made against the old key is ended. A listener running must be started
    again with the returned identity; players then need new Invites,
    because their apps pin the old key."""
    identity = new_identity(store, name)
    invites.clear()
    devices.revoke_all()
    if log is not None:
        log.record(audit.HOST_KEY_ROTATED)
    return identity


async def revoke_device(
    devices: DeviceBook, host: RemoteHost | None, device_id: str
) -> None:
    """End a device and cut its open connections at once. LookupError if it
    is not a live device."""
    revoke(devices, device_id)
    if host is not None:
        await host.disconnect(device_id)


async def rotate_host_key(
    store: KeyStore,
    name: str,
    invites: InviteBook,
    devices: DeviceBook,
    log: audit.AuditLog | None,
    host: RemoteHost | None = None,
) -> HostIdentity:
    """`rotate`, and the open connections cut at once."""
    identity = rotate(store, name, invites, devices, log)
    if host is not None:
        await host.disconnect_all()
    return identity
