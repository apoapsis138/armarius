"""The Storyguide's side of Remote seats, as the desktop's Host for Players
window draws it: hosting for Remote seats, Issue Invite, the requests to
approve or reject, the seats with Revoke, the idle-expiry setting, Rotate
Host Key, and the audit log.

Every action is a command (commands.py) the window runs: a Form, or a
Confirm that asks first (approve, reject, revoke, rotate), as the app's
other storyguide-only actions do. The window draws the rows this module
gives it and decides nothing itself. Nothing here changes the saga: the
Remote seat files live in the host's data folder (remote/folder.py).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .. import hosting, players
from ..commands import Command, Confirm, Form, Picked, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Player, Saga
from ..remote import audit, control
from ..remote.audit import AuditLog, audit_path
from ..remote.devices import MAX_IDLE_DAYS, DeviceBook, devices_path
from ..remote.identity import (
    HostIdentity,
    KeychainStore,
    KeyStore,
    NoKeychainError,
    load_or_create,
)
from ..remote.invites import InviteBook, InviteError, book_path, encode_invite
from ..remote.passcodes import RemotePasscodes, passcodes_path
from ..remote.plan import TUNNELS, RemotePlan, identity_name, last_plan, url_problem
from ..remote.words import host_words, two_lines

#: What each audit event is called in the Log.
EVENT_LABELS: dict[str, str] = {
    audit.INVITE_ISSUED: "Invite issued",
    audit.INVITE_REDEEMED: "Invite redeemed",
    audit.REQUEST_APPROVED: "Request approved",
    audit.REQUEST_REJECTED: "Request rejected",
    audit.DEVICE_ENROLLED: "Device given its seat",
    audit.SIGNED_IN: "Signed in",
    audit.SIGN_IN_FAILED: "Wrong passcode",
    audit.DEVICE_LOCKED: "Device locked out for a while",
    audit.DEVICE_REVOKED: "Seat revoked",
    audit.DEVICE_EXPIRED: "Seat expired (unused)",
    audit.HOST_KEY_ROTATED: "Host key rotated",
}


def when(moment: float) -> str:
    """A clock time as the window shows it: 8 Nov 2026, 07:30."""
    shown = time.localtime(moment)
    return f"{shown.tm_mday} {time.strftime('%b %Y, %H:%M', shown)}"


def day(moment: float) -> str:
    """A clock time's day: 8 Nov 2026."""
    shown = time.localtime(moment)
    return f"{shown.tm_mday} {time.strftime('%b %Y', shown)}"


@dataclass
class SeatsDesk:
    """A saga's Remote seats as the Storyguide manages them. `store` is
    where the host key is kept (the OS keychain; a stand-in in tests)."""

    saga: Saga
    store: KeyStore = field(default_factory=KeychainStore)
    clock: Callable[[], float] = time.time

    # -- the books, read from their files each time ------------------------

    def log(self) -> AuditLog:
        return AuditLog(audit_path(self.saga.name), self.clock)

    def invites(self) -> InviteBook:
        return InviteBook(book_path(self.saga.name), self.clock, self.log())

    def devices(self) -> DeviceBook:
        return DeviceBook(devices_path(self.saga.name), self.clock, self.log())

    def passcodes(self) -> RemotePasscodes:
        return RemotePasscodes(passcodes_path(self.saga.name))

    def identity(self) -> HostIdentity:
        """The saga's host key (made on first use). NoKeychainError with no
        keychain."""
        return load_or_create(self.store, identity_name(self.saga.id))

    def plan(self) -> RemotePlan:
        return last_plan(self.saga.id, self.saga.name)

    def name_of(self, player_id: str) -> str:
        player = players.player_by_id(self.saga, player_id)
        return player.name if player is not None else "(a deleted player)"

    # -- what the window shows -----------------------------------------------

    def words(self) -> tuple[str, str]:
        """The host's six words (two lines of three) and its pin."""
        pin = self.identity().pin
        return two_lines(host_words(pin)), pin

    def hosting_remotely(self) -> bool:
        plan = hosting.HOST.plan
        return (
            hosting.HOST.running
            and isinstance(plan, RemotePlan)
            and plan.saga_id == self.saga.id
        )

    def requests(self) -> list[RequestRow]:
        return [
            RequestRow(
                r.id, self.name_of(r.player_id), r.device, r.words, when(r.created)
            )
            for r in self.invites().pending()
        ]

    def seats(self) -> list[SeatRow]:
        book = self.devices()
        rows = []
        for device in book.devices():
            if device.ended:
                state = f"{_ENDED.get(device.end_reason, 'Ended')} {day(device.ended)}"
            else:
                state = f"Expires {day(book.expires_at(device))} if unused"
            rows.append(
                SeatRow(
                    device.id,
                    self.name_of(device.player_id),
                    device.name,
                    device.words,
                    when(device.last_seen),
                    state,
                    live=not device.ended,
                )
            )
        return rows

    def log_rows(self, player_id: str | None = None) -> list[LogRow]:
        """The audit log, newest first; with `player_id`, that player's only."""
        devices = {d.id: d.name for d in self.devices().devices()}
        rows = []
        for entry in reversed(self.log().entries()):
            if player_id is not None and entry.player_id != player_id:
                continue
            rows.append(
                LogRow(
                    when(entry.when),
                    EVENT_LABELS.get(entry.event, entry.event),
                    self.name_of(entry.player_id) if entry.player_id else "",
                    devices.get(entry.device_id, "") if entry.device_id else "",
                )
            )
        return rows

    def log_players(self) -> list[tuple[str, str]]:
        """The players the Log can be narrowed to: (name, id)."""
        return [(p.name, p.id) for p in self.saga.players if p.role == players.PLAYER]

    def idle_days(self) -> int:
        return self.devices().idle_days

    # -- the commands ------------------------------------------------------

    def host_form(self) -> Form:
        return remote_host_form(self)

    def issue_invite(self) -> Command:
        return issue_invite(self)

    def approve(self, request_id: str) -> Command:
        return _decide(self, request_id, approve=True)

    def reject(self, request_id: str) -> Command:
        return _decide(self, request_id, approve=False)

    def revoke(self, device_id: str) -> Command:
        return revoke_seat(self, device_id)

    def rotate(self) -> Command:
        return rotate_host_key(self)

    def idle_form(self) -> Form:
        return idle_days_form(self)


_ENDED = {"revoked": "Revoked", "expired": "Expired"}


@dataclass(frozen=True)
class RequestRow:
    id: str
    player: str
    device: str
    words: str
    asked: str


@dataclass(frozen=True)
class SeatRow:
    id: str
    player: str
    device: str
    words: str
    last_seen: str
    state: str
    live: bool


@dataclass(frozen=True)
class LogRow:
    when: str
    event: str
    player: str
    device: str


@dataclass(frozen=True)
class IssuedInvite:
    """What Issue Invite ends with: the line to send, shown this once."""

    player: str
    line: str
    host_words: str
    expires: str


# -- hosting for Remote seats ------------------------------------------------------


def _plan_of(desk: SeatsDesk, values: dict[str, Any]) -> RemotePlan:
    return RemotePlan(
        desk.saga.id,
        desk.saga.name,
        str(values.get("public_url") or "").strip().rstrip("/"),
        values.get("port") or 0,
        values.get("tunnel") or "cloudflare",
    )


def _host_problem(desk: SeatsDesk, values: dict[str, Any]) -> str | None:
    plan = _plan_of(desk, values)
    problem = url_problem(plan.public_url)
    if problem is not None:
        return problem
    if not 1024 <= plan.port <= 65535:
        return "The port is a number from 1024 to 65535."
    return None


def _host_live(desk: SeatsDesk, values: dict[str, Any]) -> str:
    plan = _plan_of(desk, values)
    if _host_problem(desk, values) is not None:
        return f"Point your tunnel at {escape(plan.tunnel_target())}."
    return (
        f"Point your tunnel at {escape(plan.tunnel_target())}. "
        f"Invites will send players to {escape(plan.invite_url())}."
    )


def remote_host_form(desk: SeatsDesk) -> Form:
    """Host for Remote seats: the tunnel's address, which tunnel, the port
    on this computer it points at; then start the listener."""
    last = desk.plan()

    def apply(values: dict[str, Any]) -> list[str] | Refuse:
        plan = _plan_of(desk, values)
        problem = hosting.HOST.start(plan)
        if problem is not None:
            return Refuse("Host for Players", escape(problem))
        return notes(
            "Hosting for Remote seats. Players connect through your tunnel at "
            f"{escape(plan.public_url)}.",
            "Stop Hosting ends it; so does closing the app.",
        )

    return Form(
        "Host for Remote Seats",
        lambda: [
            DialogField(
                "_what",
                "Remote seats",
                "info",
                "Players use Armarius on their own computers and connect over the "
                "internet through your own tunnel (Cloudflare Tunnel, for one). "
                "Only the tunnel can reach the app: it listens on this computer "
                "alone.",
            ),
            DialogField(
                "public_url",
                "Tunnel address",
                "text",
                last.public_url,
                required=True,
                placeholder="https://saga.example.com",
                hint="The https address your tunnel gives you.",
            ),
            DialogField(
                "tunnel",
                "Tunnel",
                "select",
                last.tunnel,
                options=[(label, key) for key, (label, _header) in TUNNELS.items()],
                hint="So each player's own address is known, for the limits on "
                "connections.",
            ),
            DialogField(
                "port",
                "Port",
                "int",
                last.port,
                required=True,
                hint="The port on this computer your tunnel points at.",
            ),
        ],
        apply,
        validate=lambda values: _host_problem(desk, values),
        live=lambda values: _host_live(desk, values),
        save_label="Host",
        help_id="host-remote-seats",
    )


# -- Issue Invite ----------------------------------------------------------------


def remote_problem(desk: SeatsDesk, player: Player) -> str | None:
    """Why `player` can't be given an Invite, or None if they can."""
    if not player.passcode_hash:
        return "has no passcode yet"
    if not desk.passcodes().allows(player):
        return (
            f"passcode under {players.MIN_PASSCODE} characters, or not set "
            "again since: set a new one on Players"
        )
    return None


def issue_invite(desk: SeatsDesk) -> Command:
    """Issue Invite: choose a Player, then see the line to send them and the
    host's six words to read out on the call."""
    plan = desk.plan()
    if not plan.public_url:
        return Refuse(
            "Issue Invite",
            "An Invite says where to connect: host for Remote seats once, with "
            "your tunnel's address, first.",
        )
    seats = [p for p in desk.saga.players if p.role == players.PLAYER]
    if not seats:
        return Refuse(
            "Issue Invite", "Add the players first, on Saga Content's Players."
        )
    able = [p for p in seats if remote_problem(desk, p) is None]
    unable = [p for p in seats if remote_problem(desk, p) is not None]
    if not able:
        return Refuse(
            "Issue Invite",
            "No player can sign in from a Remote seat yet: "
            + "; ".join(f"{escape(p.name)} {remote_problem(desk, p)}" for p in unable)
            + ".",
        )
    try:
        identity = desk.identity()
    except NoKeychainError as error:
        return Refuse("Issue Invite", escape(str(error)))

    def apply(values: dict[str, Any]) -> Picked:
        player = players.player_by_id(desk.saga, str(values["player"]))
        if player is None:
            raise LookupError("The player chosen is gone.")
        book = desk.invites()
        code = book.issue(player.id)
        return Picked(
            IssuedInvite(
                player.name,
                encode_invite(plan.invite_url(), identity.pin, code),
                two_lines(host_words(identity.pin)),
                when(book.expires(code)),
            )
        )

    fields = [
        DialogField(
            "player",
            "Player",
            "select",
            able[0].id,
            options=[(p.name, p.id) for p in able],
            hint="Each Invite works once, for one device, for 24 hours.",
        )
    ]
    if unable:
        fields.append(
            DialogField(
                "_unable",
                "Not offered",
                "info",
                "; ".join(f"{p.name}: {remote_problem(desk, p)}" for p in unable) + ".",
            )
        )
    return Form(
        "Issue Invite",
        lambda: fields,
        apply,
        save_label="Issue",
        help_id="issue-invite",
    )


# -- approving, rejecting, revoking, rotating --------------------------------------


def _decide(desk: SeatsDesk, request_id: str, *, approve: bool) -> Command:
    found = next((r for r in desk.requests() if r.id == request_id), None)
    if found is None:
        return Refuse(
            "Approve" if approve else "Reject",
            "That request is no longer waiting: it was decided, or it lapsed "
            "after an hour.",
        )

    def apply() -> list[str] | Refuse:
        book = desk.invites()
        try:
            (book.approve if approve else book.reject)(request_id)
        except InviteError:
            return Refuse(
                "Approve" if approve else "Reject",
                "That request is no longer waiting.",
            )
        if approve:
            return notes(
                f"Approved. {escape(found.device)} collects its seat the next time "
                f"it asks; then {escape(found.player)} signs in with their passcode."
            )
        return notes(f"Rejected. {escape(found.device)} gets no seat.")

    who, device, words = escape(found.player), escape(found.device), escape(found.words)
    if approve:
        question = (
            f"Give {device} {who}'s seat? Approve only if {who} read you these "
            f"words on the call:\n\n[b]{words}[/]"
        )
        return Confirm(question, apply, yes_label="Approve", title="Approve Request")
    question = (
        f"Reject {device}'s request for {who}?\n\n"
        "Its Invite is spent: if it was really theirs, issue a new one."
    )
    return Confirm(question, apply, yes_label="Reject", title="Reject Request")


def revoke_seat(desk: SeatsDesk, device_id: str) -> Command:
    found = next((s for s in desk.seats() if s.id == device_id and s.live), None)
    if found is None:
        return Refuse("Revoke", "That seat has already ended.")

    def apply() -> list[str] | Refuse:
        try:
            control.revoke(desk.devices(), device_id)
        except LookupError:
            return Refuse("Revoke", "That seat has already ended.")
        return notes(
            f"Revoked. {escape(found.device)} is cut off now; {escape(found.player)} "
            "needs a new Invite to come back from it."
        )

    return Confirm(
        f"Revoke {escape(found.player)}'s seat on {escape(found.device)}?\n\n"
        "It is cut off at once, and cannot sign in again without a new Invite.",
        apply,
        yes_label="Revoke",
        title="Revoke Seat",
    )


def rotate_host_key(desk: SeatsDesk) -> Command:
    def apply() -> list[str] | Refuse:
        running = desk.hosting_remotely()
        plan = hosting.HOST.plan if running else None
        try:
            control.rotate(
                desk.store,
                identity_name(desk.saga.id),
                desk.invites(),
                desk.devices(),
                desk.log(),
            )
        except NoKeychainError as error:
            return Refuse("Rotate Host Key", escape(str(error)))
        restarted = ""
        if isinstance(plan, RemotePlan):
            # The listener holds the old key: start it again with the new.
            hosting.HOST.stop()
            problem = hosting.HOST.start(plan)
            restarted = (
                "The host started again with the new key."
                if problem is None
                else f"The host could not start again: {escape(problem)}"
            )
        return notes(
            "The host has a new key. Every Invite and seat has ended: send each "
            "player a new Invite, and read them the new six words.",
            restarted,
        )

    return Confirm(
        "Give the host a new key? Every Invite, waiting request and Remote seat "
        "ends at once, and every player needs a new Invite.",
        apply,
        yes_label="Rotate Host Key",
        title="Rotate Host Key",
    )


def idle_days_form(desk: SeatsDesk) -> Form:
    def problem(values: dict[str, Any]) -> str | None:
        days = values.get("days") or 0
        if not 1 <= days <= MAX_IDLE_DAYS:
            return f"Choose from 1 to {MAX_IDLE_DAYS} days."
        return None

    def apply(values: dict[str, Any]) -> list[str]:
        desk.devices().set_idle_days(int(values["days"]))
        return notes(f"A seat unused for {int(values['days'])} days now stops working.")

    return Form(
        "Idle Expiry",
        lambda: [
            DialogField(
                "days",
                "Days unused",
                "int",
                desk.idle_days(),
                required=True,
                hint="A seat nobody signs in from for this long stops working; "
                "the player then needs a new Invite.",
            )
        ],
        apply,
        validate=problem,
        help_id="remote-seats-list",
    )
