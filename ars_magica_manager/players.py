"""The saga's players and signing in (STORY-1403).

When the storyguide hosts the app (tools/serve.py), each browser copy asks
who is there before opening a saga: a name from the saga's player list and
that player's passcode. The storyguide's own window -- the app run on their
computer, not in a browser -- never asks. The list lives in the saga, where
the storyguide keeps it on the Players node.

Passcodes are never stored: only a salted scrypt hash of each.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any

from . import storage
from .markup import escape, fit
from .models import Player, Saga

PLAYER = "player"
STORYGUIDE = "storyguide"
ROLES: tuple[str, ...] = (PLAYER, STORYGUIDE)
ROLE_LABELS: dict[str, str] = {PLAYER: "Player", STORYGUIDE: "Storyguide"}

#: scrypt's cost settings: fast enough to sign in, slow enough to make
#: guessing from a stolen saga file expensive.
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}

_NAME_WIDTH = 30
_ROLE_WIDTH = 12


def hash_passcode(passcode: str) -> str:
    """`passcode` as it is stored: "scrypt$<salt>$<hash>", both in hex."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(passcode.encode("utf-8"), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def passcode_matches(player: Player, passcode: str) -> bool:
    """Whether `passcode` is `player`'s."""
    try:
        scheme, salt, digest = player.passcode_hash.split("$")
        salt_bytes = bytes.fromhex(salt)
    except ValueError:
        return False
    if scheme != "scrypt":
        return False
    tried = hashlib.scrypt(passcode.encode("utf-8"), salt=salt_bytes, **_SCRYPT)
    return hmac.compare_digest(tried.hex(), digest)


def find(saga: Saga, name: str) -> Player | None:
    """The player called `name` (ignoring case and outer spaces), if any."""
    wanted = name.strip().casefold()
    return next((p for p in saga.players if p.name.casefold() == wanted), None)


def sign_in(saga: Saga, name: str, passcode: str) -> Player | None:
    """The player `name` names, if `passcode` is theirs."""
    player = find(saga, name)
    if player is None or not passcode_matches(player, passcode):
        return None
    return player


def name_problem(saga: Saga, name: str, existing: Player | None) -> str | None:
    """Why `name` can't be a player's name here, or None if it can: each
    name signs one player in, so no two may share it."""
    other = find(saga, name)
    if other is not None and other is not existing:
        return f"There is already a player called {escape(other.name)}."
    return None


def add(saga: Saga, values: dict[str, Any]) -> Player:
    """A new player from a form's values (name, role, passcode)."""
    name = values["name"].strip()
    player = Player(
        id=storage.generate_unique_id(name, [p.id for p in saga.players]),
        name=name,
        role=values.get("role") or PLAYER,
        passcode_hash=hash_passcode(values["passcode"]),
    )
    saga.players.append(player)
    return player


def update(player: Player, values: dict[str, Any]) -> None:
    """Change `player` from a form's values; a blank passcode keeps theirs."""
    player.name = values["name"].strip()
    player.role = values.get("role") or player.role
    if values.get("passcode"):
        player.passcode_hash = hash_passcode(values["passcode"])


def remove(saga: Saga, player: Player) -> None:
    saga.players.remove(player)


def table_header() -> str:
    """The column titles; the two-character indent is the selector marker."""
    return f"  {'Name':<{_NAME_WIDTH}} {'Role':<{_ROLE_WIDTH}}"


def row_label(player: Player) -> str:
    """One row (markup), lined up with `table_header`."""
    return (
        f"{escape(fit(player.name, _NAME_WIDTH))} "
        f"{ROLE_LABELS.get(player.role, player.role):<{_ROLE_WIDTH}}"
    )


def detail_text(player: Player | None) -> str:
    """The details panel (markup) for a chosen player."""
    if player is None:
        return (
            "[dim]Who can sign in to this saga when you host it for a browser: "
            "each signs in with their name and the passcode you give them. "
            "Your own window never asks. For now everyone signed in can change "
            "what you can; limiting players to their own characters comes "
            "later.[/]"
        )
    role = ROLE_LABELS.get(player.role, player.role)
    return "\n".join(
        [
            f"[b]{escape(player.name)}[/]",
            f"[b]Role:[/] {role}",
            "[b]Passcode:[/] set (edit the player to give them a new one)",
        ]
    )
