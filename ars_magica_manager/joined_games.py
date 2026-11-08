"""The Joined games a Player's desktop remembers: hosted sagas it holds a
Remote seat in, listed on the Sagas shelf beside the Player's own.

Each is the host's address (as the Invite gave it), the host key's pin
and the saga's name and id. None of that is secret (the pin is a
fingerprint every visitor sees), so it is kept in the app's settings. The
Device credential that lets this computer in is kept only in the
keychain (remote/vault.py), never here.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from . import settings

#: The settings key the joined games are kept under.
SETTING = "joined_games"


@dataclass(frozen=True)
class JoinedGame:
    """A hosted saga this computer holds a Remote seat in."""

    saga_id: str
    saga_name: str
    url: str
    pin: str


def listed() -> list[JoinedGame]:
    """Every joined game, in the order joined. An entry that can't be read
    is left out: it holds nothing that can't be had again from an Invite."""
    kept = settings.load_settings().get(SETTING)
    if not isinstance(kept, list):
        return []
    found = []
    for entry in kept:
        if isinstance(entry, dict) and all(
            isinstance(entry.get(k), str)
            for k in ("saga_id", "saga_name", "url", "pin")
        ):
            found.append(
                JoinedGame(
                    entry["saga_id"], entry["saga_name"], entry["url"], entry["pin"]
                )
            )
    return found


def remember(game: JoinedGame) -> None:
    """Keep `game`, in place of any with the same host key and saga."""
    others = [g for g in listed() if (g.pin, g.saga_id) != (game.pin, game.saga_id)]
    settings.update_settings(**{SETTING: [asdict(g) for g in [*others, game]]})


def forget(game: JoinedGame) -> None:
    kept = [g for g in listed() if (g.pin, g.saga_id) != (game.pin, game.saga_id)]
    settings.update_settings(**{SETTING: [asdict(g) for g in kept]})
