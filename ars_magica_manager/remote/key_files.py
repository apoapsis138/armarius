"""A headless host's keys, kept as files in a folder of their own.

A container on a NAS or a small server has no keychain. With
`ARMARIUS_KEYSTORE=file`, and only then, `identity.key_store` keeps the host
key and the SSH host key here instead (ADR 0022): one file per name, mode
0600, in a folder of mode 0700 that sits apart from the saga's data, so the
keys never travel with the saga or its backups.

Each check refuses with a message saying what to do, as ssh refuses a
private key others can read. Windows is refused outright: a desktop keeps
its keys in the keychain.
"""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

from .. import paths
from ..files import write_atomic
from .identity import KeychainStore, KeyStore, NoKeychainError

#: Each key file's name ends with this.
SUFFIX = ".key"
_FILE_MODE = 0o600
_FOLDER_MODE = 0o700
#: The permission bits a group or anyone else would read or write by.
_OPEN_TO_OTHERS = stat.S_IRWXG | stat.S_IRWXO


#: Where the keys go when ARMARIUS_KEYS doesn't say (the container's volume).
DEFAULT_FOLDER = Path("/keys")
#: The variable that picks the store, and its one value besides "keychain".
STORE_VARIABLE = "ARMARIUS_KEYSTORE"
FOLDER_VARIABLE = "ARMARIUS_KEYS"
FILE = "file"
KEYCHAIN = "keychain"

_ON_WINDOWS = (
    "Keeping the host's key in a file is for a headless Linux host. On Windows "
    f"the key lives in Credential Manager: unset {STORE_VARIABLE}."
)


class KeyFolderError(NoKeychainError):
    """The key folder or one of its files can't be used safely, or the
    setting that asks for it is wrong."""


def file_name(name: str) -> str:
    """A key's file name: its name in hex, so a name with ':' or '/' is
    still one plain file name, and the name can be read back from it."""
    return name.encode("utf-8").hex() + SUFFIX


def key_name(file: str) -> str:
    """The key name a file name stands for (the reverse of file_name)."""
    if not file.endswith(SUFFIX):
        raise ValueError(f"{file} is not a key file.")
    return bytes.fromhex(file.removesuffix(SUFFIX)).decode("utf-8")


def _inside(folder: Path, outer: Path) -> bool:
    return folder == outer or outer in folder.parents


class FileKeyStore:
    """The KeyStore protocol over a folder of key files (an Adapter: the
    host key code above it is the same one the keychain serves)."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder

    # -- the guards ----------------------------------------------------------

    def _check_apart_from_data(self) -> None:
        folder = self.folder.resolve()
        data = paths.data_dir().resolve()
        if _inside(folder, data) or _inside(data, folder):
            raise KeyFolderError(
                f"The key folder {self.folder} is inside the data folder {data} "
                "(or holds it), so the keys would travel with the saga and its "
                "backups. Set ARMARIUS_KEYS to a folder of its own, such as /keys."
            )

    def _check_private(self, path: Path, kind: str, mode: int) -> None:
        """Refuse `path` if a group or anyone else may use it, or it isn't
        this user's own: as ssh refuses a private key others can read."""
        if sys.platform == "win32":
            raise KeyFolderError(_ON_WINDOWS)
        info = path.stat()
        me = f"{os.geteuid()}:{os.getegid()}"
        if info.st_uid != os.geteuid():
            raise KeyFolderError(
                f"The key {kind} {path} belongs to user {info.st_uid}, not to the "
                f"user the app runs as ({me}). Run: sudo chown {me} {path} "
                "(for the container image, 10001:10001), then try again."
            )
        if info.st_mode & _OPEN_TO_OTHERS:
            raise KeyFolderError(
                f"The key {kind} {path} can be read by others (mode "
                f"{stat.S_IMODE(info.st_mode):o}). Run: chmod {mode:o} {path}, "
                "then try again."
            )

    def _check_not_root(self) -> None:
        if sys.platform == "win32":
            raise KeyFolderError(_ON_WINDOWS)
        if os.geteuid() == 0:
            raise KeyFolderError(
                "The app is running as root, which may not keep keys in files. "
                "Run it as a user of its own: the container image's (10001), so "
                "remove any `user: root` or `--user 0` from how you start it, or "
                "on a Linux box a user made for it. Then a break-in to the "
                "listener isn't a break-in to the whole computer."
            )

    def _check_exists(self) -> None:
        """Refuse a key folder that isn't there, rather than make one: on an
        encrypted volume not yet unlocked, a folder made in its place would
        take a fresh key, unencrypted, and every Invite would stop working."""
        if sys.platform == "win32":
            raise KeyFolderError(_ON_WINDOWS)
        if not self.folder.is_dir():
            me = f"{os.geteuid()}:{os.getegid()}"
            raise KeyFolderError(
                f"The key folder {self.folder} isn't there. If it is on an "
                "encrypted volume, unlock that first. If it is new, make it: "
                f"sudo install -d -o {me.split(':')[0]} -g {me.split(':')[1]} "
                f"-m 700 {self.folder} (for the container image, the folder "
                "you mount at /keys, owned 10001:10001)."
            )

    def _ready(self) -> None:
        """Every guard passed: the folder is there, private and this
        user's own."""
        self._check_not_root()
        self._check_apart_from_data()
        self._check_exists()
        self._check_private(self.folder, "folder", _FOLDER_MODE)

    def _path(self, name: str) -> Path:
        return self.folder / file_name(name)

    # -- the KeyStore protocol ------------------------------------------------

    def get(self, name: str) -> str | None:
        self._ready()
        path = self._path(name)
        if not path.exists():
            return None
        self._check_private(path, "file", _FILE_MODE)
        return path.read_text(encoding="utf-8")

    def set(self, name: str, value: str) -> None:
        self._ready()
        path = self._path(name)
        # The temp file write_atomic makes is 0600 from the start, so the
        # key is never readable by others, even for a moment.
        write_atomic(path, value)
        os.chmod(path, _FILE_MODE)

    def delete(self, name: str) -> None:
        self._ready()
        self._path(name).unlink(missing_ok=True)


class RefusedStore:
    """A KeyStore that refuses every use, saying why (a Null Object that
    errs): what key_store gives for a setting it doesn't know, so the
    window, the listener and admin each show the reason where they already
    show a missing keychain, instead of failing as the page opens."""

    def __init__(self, why: str) -> None:
        self.why = why

    def get(self, name: str) -> str | None:
        raise KeyFolderError(self.why)

    def set(self, name: str, value: str) -> None:
        raise KeyFolderError(self.why)

    def delete(self, name: str) -> None:
        raise KeyFolderError(self.why)


def key_store() -> KeyStore:
    """Where this host keeps its host key and SSH host key: the keychain,
    or with ARMARIUS_KEYSTORE=file a FileKeyStore in ARMARIUS_KEYS (else
    /keys). Any other value gives a store that refuses every use, never
    quietly the keychain. A player's device credentials don't come through
    here: they stay in the keychain (DeviceVault)."""
    chosen = os.environ.get(STORE_VARIABLE, "").strip()
    if chosen in ("", KEYCHAIN):
        return KeychainStore()
    if chosen == FILE:
        folder = os.environ.get(FOLDER_VARIABLE, "").strip()
        return FileKeyStore(Path(folder) if folder else DEFAULT_FOLDER)
    return RefusedStore(
        f"{STORE_VARIABLE} is set to {chosen!r}, which this app doesn't know. "
        f"Set it to {FILE!r} to keep the host's key in a file (a headless "
        "host), or unset it to use the keychain."
    )
