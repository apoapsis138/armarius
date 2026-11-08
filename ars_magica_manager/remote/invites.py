"""Invites: a one-time enrolment token, and the request it becomes.

A Storyguide issues an Invite for one Player. It is 128 random bits, good
once and for 24 hours; the host keeps only a hash of it, so a copy of the
host's files does not give one away. Redeeming it asks for a Remote seat: a
pending request that shows the Storyguide the Player's name and the
device's three words. The Storyguide approves or rejects it; the player's
app learns the outcome by presenting the secret it made for the request.

This module holds the book of Invites and requests and the rules; it
knows nothing of the network. A refusal is always one `InviteError`: the
reason (unknown, used, expired) is for the caller's log and is never sent
to the person asking.

The book is a small file in the host's data folder, outside the saga file,
so the saga (which players receive parts of) never holds it.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import secrets
import string
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlsplit

from .. import paths, players
from ..files import write_atomic
from ..models import Saga
from .identity import normalise_pin
from .words import device_words

INVITE_TTL = 24 * 3600.0
#: How long a request waits for the Storyguide before it lapses.
REQUEST_TTL = 3600.0
#: How long a decided request is kept, for the player's app to learn it.
DECIDED_KEEP = 7 * 24 * 3600.0
_CODE_BYTES = 16
_SECRET_MIN = 32
_SECRET_MAX = 64
PENDING, APPROVED, REJECTED = "pending", "approved", "rejected"
_MAX_URL = 300
INVITE_PREFIX = "ARM1"


class InviteError(Exception):
    """An Invite or request cannot be used. `reason` is for logs only."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class Request:
    """A player's device asking for a Remote seat."""

    id: str  # hash of the device's secret; safe to show and to name in a list
    player_id: str
    device: str
    words: str  # the device's three words, for the Storyguide to compare
    created: float
    state: str = PENDING
    decided: float = 0.0


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _clean_code(code: str) -> str:
    return "".join(code.split()).replace("-", "").upper()


def new_code() -> str:
    """128 random bits as seven groups of letters and digits."""
    raw = base64.b32encode(secrets.token_bytes(_CODE_BYTES)).decode().rstrip("=")
    return "-".join(raw[i : i + 4] for i in range(0, len(raw), 4))


class InviteBook:
    """The Invites issued and the requests made, kept in one file."""

    def __init__(self, path: Path, clock: Callable[[], float] = time.time) -> None:
        self._path = path
        self._clock = clock
        self._invites: dict[str, dict[str, object]] = {}
        self._requests: dict[str, Request] = {}
        self._load()

    # -- the file ---------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            self._invites = {
                str(k): {
                    "player_id": str(v["player_id"]),
                    "expires": float(v["expires"]),
                    "used": bool(v["used"]),
                }
                for k, v in data["invites"].items()
            }
            self._requests = {str(k): Request(**v) for k, v in data["requests"].items()}
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ValueError(
                f"The invites file {self._path.name} cannot be read."
            ) from exc

    def _save(self) -> None:
        self._forget_old()
        data = {
            "invites": self._invites,
            "requests": {k: asdict(v) for k, v in self._requests.items()},
        }
        write_atomic(self._path, json.dumps(data, indent=1))

    def _forget_old(self) -> None:
        now = self._clock()
        self._invites = {
            k: v
            for k, v in self._invites.items()
            if float(v["expires"]) > now - DECIDED_KEEP  # pyright: ignore[reportArgumentType]
        }
        self._requests = {
            k: r
            for k, r in self._requests.items()
            if now - (r.decided or r.created) < DECIDED_KEEP
        }

    # -- the Storyguide issues ---------------------------------------------

    def issue(self, player_id: str) -> str:
        """A new Invite for `player_id`: the code to send them, shown once."""
        code = new_code()
        self._invites[_hash(_clean_code(code))] = {
            "player_id": player_id,
            "expires": self._clock() + INVITE_TTL,
            "used": False,
        }
        self._save()
        return code

    # -- the player redeems ------------------------------------------------

    def redeem(self, code: str, device: str, secret: str) -> Request:
        """Turn an Invite into a pending request, or raise InviteError."""
        if not _SECRET_MIN <= len(secret) <= _SECRET_MAX or any(
            c not in string.hexdigits for c in secret
        ):
            raise InviteError("secret is not the expected shape")
        invite = self._invites.get(_hash(_clean_code(code)))
        if invite is None:
            raise InviteError("unknown code")
        if invite["used"]:
            raise InviteError("code already used")
        if float(invite["expires"]) <= self._clock():  # pyright: ignore[reportArgumentType]
            raise InviteError("code expired")
        request_id = _hash(secret)
        if request_id in self._requests:
            raise InviteError("secret already used")
        invite["used"] = True
        request = Request(
            id=request_id,
            player_id=str(invite["player_id"]),
            device=device,
            words=" ".join(device_words(secret)),
            created=self._clock(),
        )
        self._requests[request_id] = request
        self._save()
        return request

    def status(self, secret: str) -> Request:
        """The request this secret made, or InviteError."""
        request = self._requests.get(_hash(secret))
        if request is None:
            raise InviteError("unknown request")
        if request.state == PENDING and self._lapsed(request):
            raise InviteError("request lapsed")
        return request

    # -- the Storyguide decides --------------------------------------------

    def _lapsed(self, request: Request) -> bool:
        return self._clock() - request.created >= REQUEST_TTL

    def pending(self) -> list[Request]:
        """Requests waiting for the Storyguide, oldest first."""
        waiting = [
            r
            for r in self._requests.values()
            if r.state == PENDING and not self._lapsed(r)
        ]
        return sorted(waiting, key=lambda r: r.created)

    def _decide(self, request_id: str, state: str) -> Request:
        request = self._requests.get(request_id)
        if request is None or request.state != PENDING or self._lapsed(request):
            raise InviteError("no such pending request")
        request.state = state
        request.decided = self._clock()
        self._save()
        return request

    def approve(self, request_id: str) -> Request:
        return self._decide(request_id, APPROVED)

    def reject(self, request_id: str) -> Request:
        return self._decide(request_id, REJECTED)


# -- helpers that need the saga -----------------------------------------------


def book_path(saga_name: str) -> Path:
    """Where a saga's book lives: the host's data folder, not the saga file."""
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in saga_name)
    return paths.data_dir() / "remote" / f"{safe}-invites.json"


def issue_for(book: InviteBook, saga: Saga, player_name: str) -> str:
    """An Invite for the Player named `player_name`; ValueError if there is
    no such Player (the Storyguide's own seat is not one)."""
    player = players.find(saga, player_name)
    if player is None or player.role != players.PLAYER:
        raise ValueError(f"{player_name!r} is not a Player in this saga.")
    return book.issue(player.id)


# -- the text the Storyguide sends --------------------------------------------


@dataclass(frozen=True)
class InviteText:
    """What an Invite carries: where the host is, its key's pin, the code."""

    url: str
    pin: str
    code: str


def encode_invite(url: str, pin: str, code: str) -> str:
    """One line of plain letters and digits, safe to paste into a chat. The
    code is in the text, never in a link, so a chat app that fetches links
    to preview them never sees it."""
    packed = base64.b32encode(url.encode()).decode().rstrip("=")
    return f"{INVITE_PREFIX}.{packed}.{pin}.{_clean_code(code)}"


def decode_invite(text: str) -> InviteText:
    """The parts of a pasted Invite, or ValueError saying it is not one."""
    parts = "".join(text.split()).split(".")
    if len(parts) != 4 or parts[0] != INVITE_PREFIX:
        raise ValueError("That is not an Armarius invite.")
    packed = parts[1].upper()
    try:
        url = base64.b32decode(packed + "=" * (-len(packed) % 8)).decode()
    except (binascii.Error, UnicodeDecodeError) as exc:
        raise ValueError("That is not an Armarius invite.") from exc
    pieces = urlsplit(url)
    if pieces.scheme not in ("ws", "wss") or not pieces.netloc or len(url) > _MAX_URL:
        raise ValueError("The invite does not name a place to connect to.")
    if pieces.query or pieces.fragment or pieces.username:
        raise ValueError("The invite's address must carry nothing secret.")
    return InviteText(url=url, pin=normalise_pin(parts[2]), code=_clean_code(parts[3]))
