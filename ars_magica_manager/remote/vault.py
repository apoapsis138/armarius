"""The player's side: where a Device credential is kept.

Only in the operating system's keychain, one entry per host (named by the
host key's pin). With no keychain the app refuses to enrol, before the
Invite is spent, and says why; there is no file to fall back on, because a
credential in a file is a credential any program on the computer could copy.
"""

from __future__ import annotations

from .identity import KeychainStore, KeyStore, NoKeychainError, normalise_pin

_PROBE = "probe"
_PREFIX = "credential:"


class DeviceVault:
    """Device credentials, by host."""

    def __init__(self, store: KeyStore | None = None) -> None:
        self._store = store if store is not None else KeychainStore()

    def ensure_available(self) -> None:
        """Raise NoKeychainError now if credentials cannot be kept."""
        self._store.get(_PROBE)

    def save(self, pin: str, credential: str) -> None:
        self._store.set(_PREFIX + normalise_pin(pin), credential)

    def load(self, pin: str) -> str | None:
        return self._store.get(_PREFIX + normalise_pin(pin))

    def forget(self, pin: str) -> None:
        self._store.delete(_PREFIX + normalise_pin(pin))


__all__ = ["DeviceVault", "NoKeychainError"]
