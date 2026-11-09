"""The saga's players and signing in.

When the storyguide hosts the app (hosting.py), each browser copy asks
who is there before opening a saga: a name from the saga's player list and
that player's passcode. The storyguide's own window -- the app run on their
computer, not in a browser -- never asks. The list lives in the saga, where
the storyguide keeps it on the Saga Content view's Players tab.

Passcodes are never stored: only a salted scrypt hash of each.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Sequence
from typing import Any, cast

from . import storage
from .markup import escape, fit
from .models import (
    Background,
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Neighbour,
    Player,
    Saga,
    Tribunal,
)

PLAYER = "player"
STORYGUIDE = "storyguide"
ROLES: tuple[str, ...] = (PLAYER, STORYGUIDE)
ROLE_LABELS: dict[str, str] = {PLAYER: "Player", STORYGUIDE: "Storyguide"}

#: scrypt's cost settings: fast enough to sign in, slow enough to make
#: guessing from a stolen saga file expensive.
_SCRYPT = {"n": 2**14, "r": 8, "p": 1}

_NAME_WIDTH = 30
_ROLE_WIDTH = 12


#: The shortest passcode a new one may be. A Remote seat's host sends the
#: stored salt, so a fake host can guess a weak passcode offline; length is
#: the defence.
MIN_PASSCODE = 14


def passcode_problem(passcode: str) -> str | None:
    """Why `passcode` is too weak to set, or None if it is long enough."""
    if len(passcode) < MIN_PASSCODE:
        return f"A passcode needs at least {MIN_PASSCODE} characters."
    return None


def passcode_digest(passcode: str, salt: bytes) -> bytes:
    """The scrypt digest of `passcode` under `salt`."""
    return hashlib.scrypt(passcode.encode("utf-8"), salt=salt, **_SCRYPT)


def hash_passcode(passcode: str) -> str:
    """`passcode` as it is stored: "scrypt$<salt>$<hash>", both in hex."""
    salt = secrets.token_bytes(16)
    return f"scrypt${salt.hex()}${passcode_digest(passcode, salt).hex()}"


def stored_parts(stored: str) -> tuple[bytes, bytes]:
    """The salt and digest inside a stored hash, or ValueError."""
    scheme, salt, digest = stored.split("$")
    if scheme != "scrypt":
        raise ValueError("Unknown passcode scheme.")
    return bytes.fromhex(salt), bytes.fromhex(digest)


def passcode_matches(player: Player, passcode: str) -> bool:
    """Whether `passcode` is `player`'s."""
    try:
        salt, digest = stored_parts(player.passcode_hash)
    except ValueError:
        return False
    return hmac.compare_digest(passcode_digest(passcode, salt), digest)


def set_passcode(player: Player, passcode: str) -> None:
    """Store `passcode` for `player`. Whether it may be used from a Remote
    seat is noted by the host, outside the saga (remote/passcodes.py)."""
    player.passcode_hash = hash_passcode(passcode)


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
        covenant_rights=bool(values.get("covenant_rights")),
    )
    set_passcode(player, values["passcode"])
    saga.players.append(player)
    return player


def update(player: Player, values: dict[str, Any]) -> None:
    """Change `player` from a form's values; a blank passcode keeps theirs."""
    player.name = values["name"].strip()
    player.role = values.get("role") or player.role
    player.covenant_rights = bool(values.get("covenant_rights"))
    if values.get("passcode"):
        set_passcode(player, values["passcode"])


def remove(saga: Saga, player: Player) -> None:
    """Delete `player`; they no longer play any character."""
    saga.players.remove(player)
    for character in saga.characters:
        ids = character.background.player_ids
        if player.id in ids:
            ids.remove(player.id)


# -- who may change what --


def player_by_id(saga: Saga, player_id: str | None) -> Player | None:
    return next((p for p in saga.players if p.id == player_id), None)


def plays(background: object, player: Player) -> bool:
    """Whether `player` plays the character with this Biographical Detail
    (a Background, or one as plain data, which may be a player's change of
    any shape: anything but a record plays no one): named among its
    players, or a player of the troupe when everyone plays it."""
    if isinstance(background, Background):
        ids, everyone = background.player_ids, background.everyone_plays
    elif isinstance(background, dict):
        found = cast(dict[str, Any], background)
        ids = found.get("player_ids")
        ids = ids if isinstance(ids, list) else []
        everyone = found.get("everyone_plays") is True
    else:
        return False
    return player.id in ids or (everyone and player.role == PLAYER)


def played_by(background: Background, players: Sequence[Player]) -> str:
    """Who plays the character, in words: "Everyone in the troupe", the
    players' names, or "(no one)"."""
    if background.everyone_plays:
        return "Everyone in the troupe"
    names = [p.name for p in players if p.id in background.player_ids]
    return ", ".join(names) or "(no one)"


def has_players(background: Background) -> bool:
    """Whether any saga Player plays the character."""
    return bool(background.player_ids) or background.everyone_plays


def players_of(saga: Saga, character: Character) -> list[Player]:
    """The players who play `character`."""
    return [p for p in saga.players if plays(character.background, p)]


def characters_of(saga: Saga, player: Player) -> list[Character]:
    """The characters `player` plays."""
    return [c for c in saga.characters if plays(c.background, player)]


def may_change(
    saga: Saga,
    player: Player | None,
    record: Character | Familiar | Laboratory | Covenant | Tribunal | Neighbour | None,
) -> bool:
    """Whether `player` may change `record` (None: something of the whole
    saga). A storyguide may change anything; a player their own characters,
    those characters' familiars and laboratories, and the covenants if the
    storyguide gave them covenant rights. `player` None is the storyguide's
    own window."""
    if player is None or player.role == STORYGUIDE:
        return True
    mine = {c.id for c in characters_of(saga, player)}
    if isinstance(record, Character):
        return record.id in mine
    if isinstance(record, Familiar):
        return record.character_id in mine
    if isinstance(record, Laboratory):
        return record.owner_id in mine
    if isinstance(record, Covenant):
        return player.covenant_rights
    return False


def table_header() -> str:
    """The column titles; the two-character indent is the selector marker."""
    return f"  {'Name':<{_NAME_WIDTH}} {'Role':<{_ROLE_WIDTH}}"


def row_label(player: Player) -> str:
    """One row (markup), lined up with `table_header`."""
    return (
        f"{escape(fit(player.name, _NAME_WIDTH))} "
        f"{ROLE_LABELS.get(player.role, player.role):<{_ROLE_WIDTH}}"
    )


def detail_text(saga: Saga, player: Player | None) -> str:
    """The details panel (markup) for a chosen player."""
    if player is None:
        return "[dim]Choose a player to see what they play; a adds one.[/]"
    role = ROLE_LABELS.get(player.role, player.role)
    return "\n".join(
        [
            f"[b]{escape(player.name)}[/]",
            f"[b]Role:[/] {role}",
            "[b]Passcode:[/] set (edit the player to give them a new one)",
        ]
    )


#: Parts of a saga anyone signed in may change: the libraries and spells
#: their characters use, enchanted items. Each still sits on a sheet only
#: its owner can change. Season plans and lab work are each a character's,
#: so only that character's player may change them.
_SHARED_PARTS = frozenset(
    {
        "books",
        "spells",
        "enchanted_devices",
        "app_version",
    }
)

#: How a record of each list is named, where it has no id: a season plan
#: by its character and season, a lab project by its character and spell.
_NATURAL_KEYS: dict[str, tuple[str, ...]] = {
    "season_plans": ("character_id", "year", "season"),
    "lab_projects": ("character_id", "spell_id"),
}


def _key_of(key: str) -> Any:
    fields = _NATURAL_KEYS.get(key)
    if fields is None:
        return lambda r: r["id"]
    return lambda r: tuple(r.get(f) for f in fields)


def guard_changes(
    player: Player | None, before: dict[str, Any], after: dict[str, Any]
) -> tuple[dict[str, Any], list[str]]:
    """`after` (a saga as plain data) with the changes `player` may not make
    since `before` taken back, and what was taken back ("characters[mag1]",
    "current_year"...). The last guard in front of saving: the
    screens already offer a player only what they may change."""
    if player is None or player.role == STORYGUIDE:
        return after, []
    mine = {
        c["id"]
        for c in before.get("characters", [])
        if plays(c.get("background"), player)
    }
    owner_of = {
        "characters": lambda r: r.get("id") in mine,
        "laboratories": lambda r: r.get("owner_id") in mine,
        "familiars": lambda r: r.get("character_id") in mine,
        "covenants": lambda r: player.covenant_rights,
        "season_plans": lambda r: r.get("character_id") in mine,
        "lab_projects": lambda r: r.get("character_id") in mine,
    }
    kept = dict(after)
    refused: list[str] = []
    for key in [*before, *(k for k in after if k not in before)]:
        old, new = before.get(key), after.get(key)
        if old == new or key in _SHARED_PARTS:
            continue
        may = owner_of.get(key)
        if may is None:
            kept[key] = old
            refused.append(key)
        else:
            kept[key] = _guard_records(key, old or [], new or [], may, refused)
    if "characters" in kept:
        kept["characters"] = _same_players(
            before.get("characters") or [], kept["characters"], refused
        )
    return kept, refused


_WHO_PLAYS = ("player_ids", "everyone_plays")


def _same_players(
    old: list[dict[str, Any]], new: list[dict[str, Any]], refused: list[str]
) -> list[dict[str, Any]]:
    """`new` characters with who plays each as it was: only the storyguide
    says who plays a character (a player can't add themselves to another's,
    nor hand theirs on)."""

    def background_of(record: object) -> dict[str, Any]:
        found = record.get("background") if isinstance(record, dict) else None
        return cast(dict[str, Any], found) if isinstance(found, dict) else {}

    was = {r.get("id"): background_of(r) for r in old}
    kept = []
    for record in new:
        if not isinstance(record, dict):
            kept.append(record)  # refused later by the shape check
            continue
        background = background_of(record)
        earlier = was.get(record.get("id"))
        if earlier is not None and any(
            background.get(k) != earlier.get(k) for k in _WHO_PLAYS
        ):
            background = {**background, **{k: earlier.get(k) for k in _WHO_PLAYS}}
            record = {**record, "background": background}
            refused.append(f"characters[{record.get('id')}].background.player_ids")
        kept.append(record)
    return kept


def _guard_records(
    key: str, old: list, new: list, may: Any, refused: list[str]
) -> list:
    """`new` records with each change to one `may` refuses undone: a record
    is the player's to change while it is theirs before and after (a lab
    can't be handed to another's magus)."""
    key_of = _key_of(key)
    old_by_id = {key_of(r): r for r in old}
    kept = []
    for record in new:
        before = old_by_id.get(key_of(record))
        if before is None:
            if may(record):
                kept.append(record)
            else:
                refused.append(f"{key}[{key_of(record)}]")
        elif record == before or (may(before) and may(record)):
            kept.append(record)
        else:
            kept.append(before)
            refused.append(f"{key}[{key_of(record)}]")
    new_ids = {key_of(r) for r in new}
    for record in old:
        if key_of(record) not in new_ids and not may(record):
            kept.append(record)
            refused.append(f"{key}[{key_of(record)}]")
    return kept
