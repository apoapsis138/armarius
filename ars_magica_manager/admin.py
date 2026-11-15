"""The host's chores from a plain terminal, for a host with no window.

    python main.py admin [--saga SAGA] GROUP VERB ...
    (in a container: docker exec -it armarius python main.py admin ...)

What the Host for Players window does on a desktop, for a headless host
(a server or a NAS container, ADR 0022): the saga's players and their
passcodes, Invites and the requests they bring, seats, the Log, the host
key, and bringing a saga in or deleting it. Nothing goes over the wire: it
reads and writes the same files the listener does, on the same computer.

Each verb is one function in a table (Command, as main.py's words are).
The verbs don't carry rules of their own: they run the very commands the
window runs (forms.remote_seats.SeatsDesk, the player form), answering
each Form with the values given on the command line and each Confirm by
asking here, through commands.drive. A passcode is asked for with its
typing hidden, never taken from the command line, where other users of
the computer and the shell's history would see it.
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import host_backup, players, storage
from .commands import (
    Cancelled,
    Confirm,
    Empty,
    Finished,
    Form,
    Go,
    Picked,
    Question,
    Refuse,
    Then,
    drive,
)
from .form_spec import FieldError, result
from .forms.remote_seats import IssuedInvite, SeatsDesk, remote_problem
from .markup import plain
from .models import Player, Saga
from .remote.identity import NoKeychainError
from .remote.passcodes import RemotePasscodes, passcodes_path, read_notes
from .remote.plan import CLOUDFLARE, SAGA_VARIABLE, TUNNELS, RemotePlan, url_problem

#: A saga id that is safe as a file name: an imported file can't name a
#: path outside the sagas folder.
_SAFE_ID = re.compile(r"[A-Za-z0-9_-]+")
#: How many Log entries `log` prints unless told.
LOG_SHOWN = 50


class AdminError(Exception):
    """A verb can't act: the message says why, and nothing was changed."""


def _to_stderr(line: str) -> None:
    print(line, file=sys.stderr)


@dataclass
class Console:
    """Where the verbs read and write: the real terminal, or a test's.
    Why a verb couldn't act goes to `err` (stderr), so a script piping
    its output gets only what it asked for."""

    out: Callable[[str], None] = print
    err: Callable[[str], None] = _to_stderr
    ask: Callable[[str], str] = input
    secret: Callable[[str], str] = getpass.getpass

    def say(self, *lines: str) -> None:
        for line in lines:
            self.out(line)


# -- finding the saga and its records ----------------------------------------------


def saga_id_for(wanted: str | None) -> str:
    """The id of the saga `wanted` names (its id, or its name in any case);
    with none, ARMARIUS_SAGA's, else the only saga there is."""
    wanted = (wanted or os.environ.get(SAGA_VARIABLE, "")).strip()
    ids = storage.list_sagas()
    if not wanted:
        if len(ids) == 1:
            return ids[0]
        raise AdminError(
            "Say which saga with --saga (its id or name): "
            + (", ".join(ids) if ids else "there are none yet")
            + "."
        )
    if wanted in ids:
        return wanted
    for saga_id in ids:
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError:
            continue
        if name.casefold() == wanted.casefold():
            return saga_id
    raise AdminError(f"There is no saga {wanted!r} here.")


def load(wanted: str | None) -> Saga:
    saga_id = saga_id_for(wanted)
    try:
        return storage.load_saga(saga_id)
    except (OSError, ValueError) as error:
        raise AdminError(storage.unreadable_note(saga_id, error)) from error


def player_named(saga: Saga, name: str) -> Player:
    player = players.find(saga, name)
    if player is None:
        known = ", ".join(p.name for p in saga.players) or "none yet"
        raise AdminError(f"No player is called {name!r} (players: {known}).")
    return player


def one_of(ids: list[str], wanted: str, what: str) -> str:
    """The id in `ids` that `wanted` is, or starts (as long as only one
    does): ids are long, and the lists print them whole."""
    if wanted in ids:
        return wanted
    found = [i for i in ids if i.startswith(wanted)] if wanted else []
    if len(found) == 1:
        return found[0]
    if found:
        raise AdminError(f"{wanted!r} starts more than one {what}: give more of it.")
    raise AdminError(f"There is no {what} {wanted!r}.")


# -- running the window's commands here --------------------------------------------


def run_command(
    first: object,
    console: Console,
    values: dict[str, Any] | None = None,
    *,
    yes: bool = False,
) -> object:
    """Run a command the window would run, to its end: each Form answered
    with its own values and `values` over them (the form's checks still
    apply), each Confirm asked here unless `yes`. Returns what the last
    step returned; AdminError if it refused, was turned down, or a value
    failed a check."""
    given = values or {}

    def answer(question: Question) -> object:
        if isinstance(question, Form):
            try:
                found = result(question.fields(), lambda f: given.get(f.key, f.value))
            except FieldError as error:
                raise AdminError(str(error)) from error
            problem = question.validate(found) if question.validate else None
            if problem:
                raise AdminError(plain(problem))
            return found
        if isinstance(question, Confirm):
            if yes or confirmed(console, plain(question.question), question.yes_label):
                return True
            return Cancelled()
        raise AdminError(f"{type(question).__name__} can't be answered here.")

    outcome = drive(first, answer)
    if isinstance(outcome, Refuse):
        raise AdminError(plain(outcome.why))
    if isinstance(outcome, Cancelled):
        raise AdminError("Nothing was changed.")
    if isinstance(outcome, Empty):
        raise AdminError(plain(outcome.why))
    if isinstance(outcome, Go | Then):
        raise AdminError("That opens a page, which only the window has.")
    assert isinstance(outcome, Finished)
    end = outcome.end
    if isinstance(end, list):
        console.say(*(plain(str(line)) for line in end))
    return end


def confirmed(console: Console, question: str, yes_label: str) -> bool:
    """Ask `question`; only "yes" goes on. No answer (a closed input, as
    when run from a script without --yes) is No."""
    console.say(question, "")
    try:
        answer = console.ask(f"{yes_label}? Type yes to go on: ")
    except EOFError:
        return False
    return answer.strip().casefold() == "yes"


# -- the verbs -----------------------------------------------------------------


def _desk(args: argparse.Namespace) -> SeatsDesk:
    return SeatsDesk(load(args.saga))


def sagas_list(args: argparse.Namespace, console: Console) -> None:
    ids = storage.list_sagas()
    if not ids:
        console.say("No sagas yet: bring one in with admin saga import FILE.")
    for saga_id in ids:
        try:
            name = storage.load_saga(saga_id).name
        except OSError, ValueError:
            name = "(can't be read)"
        console.say(f"{saga_id}  {name}")


def players_list(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    live = {d.player_id for d in desk.devices().devices() if not d.ended}
    if not desk.saga.players:
        console.say("No players yet: add them on the desktop before moving here.")
    for player in desk.saga.players:
        problem = remote_problem(desk, player)
        console.say(
            f"{player.name}  ({players.ROLE_LABELS.get(player.role, player.role)})  "
            + (f"no Remote seat: {problem}" if problem else "may have a Remote seat")
            + ("  [seated]" if player.id in live else "")
        )


def players_set_role(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    role = args.role.strip().casefold()
    if role not in players.ROLES:
        raise AdminError(f"A role is one of: {', '.join(players.ROLES)}.")
    player = player_named(desk.saga, args.player)
    run_command(desk.edit_player(player.id), console, {"role": role}, yes=args.yes)
    console.say(f"{player.name} is now a {players.ROLE_LABELS[role].lower()}.")


def players_set_passcode(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    player = player_named(desk.saga, args.player)
    first = console.secret(f"New passcode for {player.name}: ")
    if (weak := players.passcode_problem(first)) is not None:
        raise AdminError(weak)
    if console.secret("The same again: ") != first:
        raise AdminError("The two passcodes differ: nothing was changed.")
    run_command(desk.edit_player(player.id), console, {"passcode": first})
    console.say(
        f"{player.name}'s passcode is set. Give it to them yourself; seats still "
        "signed in with the old one have ended."
    )


def tunnel(args: argparse.Namespace, console: Console) -> None:
    """Show, or set, the tunnel's address that Invites carry (the window's
    Host for Remote Seats form, without starting anything)."""
    desk = _desk(args)
    last = desk.plan()
    if args.url is None and args.tunnel is None and args.port is None:
        console.say(
            f"Tunnel address: {last.public_url or '(not set)'}",
            f"Tunnel: {TUNNELS[last.tunnel][0]}",
            f"Listener port: {last.port} (point the tunnel at {last.tunnel_target()})",
        )
        return
    plan = RemotePlan(
        desk.saga.id,
        desk.saga.name,
        (args.url if args.url is not None else last.public_url).strip().rstrip("/"),
        args.port if args.port is not None else last.port,
        args.tunnel or last.tunnel,
    )
    if (problem := url_problem(plan.public_url)) is not None:
        raise AdminError(problem)
    if not 1024 <= plan.port <= 65535:
        raise AdminError("The port is a number from 1024 to 65535.")
    plan.remember()
    console.say(
        f"Invites now send players to {plan.invite_url()}.",
        f"Point the tunnel at {plan.tunnel_target()}.",
    )


def words(args: argparse.Namespace, console: Console) -> None:
    lines, pin = _desk(args).words()
    console.say("The host's six words, to read out on the call:", lines, f"Pin: {pin}")


def invites_issue(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    player = player_named(desk.saga, args.player)
    end = run_command(desk.issue_invite(player.id), console, {"player": player.id})
    if not isinstance(end, Picked) or not isinstance(end.value, IssuedInvite):
        raise AdminError("No Invite was issued.")
    issued = end.value
    console.say(
        f"Invite for {issued.player} (works once, on one device, until {issued.expires}):",
        "",
        issued.line,
        "",
        "Send it by a different way from your call. On the call, read all six words:",
        issued.host_words,
    )


#: The fewest characters of an id the lists print: enough to be unique in
#: practice, short enough to type.
SHORT_ID = 8


def short_ids(ids: list[str]) -> dict[str, str]:
    """Each id cut to the fewest characters (SHORT_ID at least, after any
    "reset:"-style prefix) that no other id in `ids` starts with: what a
    list prints for the person to type back."""
    found = {}
    for full in ids:
        head = full.rfind(":") + 1
        length = head + SHORT_ID
        while length < len(full) and any(
            other != full and other.startswith(full[:length]) for other in ids
        ):
            length += 1
        found[full] = full[:length]
    return found


def command_for(*words: str) -> str:
    """How to type an admin command here: inside the container image,
    through docker exec from the host; else from the app's folder."""
    if Path("/.dockerenv").exists():
        return "docker exec -it armarius python main.py admin " + " ".join(words)
    return "python main.py admin " + " ".join(words)


def invites_pending(args: argparse.Namespace, console: Console) -> None:
    rows = _desk(args).requests()
    if not rows:
        console.say("Nothing is waiting.")
        return
    short = short_ids([row.id for row in rows])
    for row in rows:
        console.say(
            f"{row.asks} for {row.player}, from {row.device}, asked {row.asked}",
            *(
                [f"  Its three words: {row.words} (check the player reads you these)"]
                if row.words
                else []
            ),
            f"  To approve: {command_for('approve', short[row.id])}",
            f"  To turn down: {command_for('reject', short[row.id])}",
            "",
        )


def _request(desk: SeatsDesk, wanted: str) -> str:
    return one_of([r.id for r in desk.requests()], wanted, "request")


def approve(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    request = _request(desk, args.request)
    run_command(desk.approve(request), console, yes=args.yes)


def reject(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    request = _request(desk, args.request)
    run_command(desk.reject(request), console, yes=args.yes)


def devices_list(args: argparse.Namespace, console: Console) -> None:
    rows = _desk(args).seats()
    if not rows:
        console.say("No seats yet.")
        return
    short = short_ids([row.id for row in rows])
    for row in rows:
        console.say(
            f"{row.player} on {row.device} ({row.words}): last seen "
            f"{row.last_seen}, {row.state}",
            *(
                [f"  To revoke: {command_for('devices', 'revoke', short[row.id])}"]
                if row.live
                else []
            ),
        )


def devices_revoke(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    device = one_of([s.id for s in desk.seats() if s.live], args.device, "live seat")
    run_command(desk.revoke(device), console, yes=args.yes)


def log(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    player_id = player_named(desk.saga, args.player).id if args.player else None
    rows = desk.log_rows(player_id)[: args.limit]
    if not rows:
        console.say("The Log is empty.")
    for row in rows:
        console.say(
            "  ".join(
                part for part in (row.when, row.event, row.player, row.device) if part
            )
        )


def rotate_key(args: argparse.Namespace, console: Console) -> None:
    desk = _desk(args)
    run_command(desk.rotate(), console, yes=args.yes)
    console.say(
        "Restart the listener so it serves the new key (with Docker: docker "
        "compose restart armarius). Then read everyone the new six words: "
        "admin words."
    )


def saga_import(args: argparse.Namespace, console: Console) -> None:
    """Bring a saga file in, checked as any saga file is when opened."""
    path = Path(args.file)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        saga = storage.saga_from_data(data)
    except OSError as error:
        raise AdminError(f"Can't read {path}: {error.strerror or error}") from error
    except ValueError as error:
        raise AdminError(f"{path} isn't a saga this app can read: {error}") from error
    if not _SAFE_ID.fullmatch(saga.id):
        raise AdminError(f"{path} names its saga {saga.id!r}, which isn't a safe id.")
    if saga.id in storage.list_sagas():
        raise AdminError(
            f"A saga with the id {saga.id!r} is already here. Delete it first "
            "(admin saga delete), or keep the one you have."
        )
    notes: dict[str, str] = {}
    if args.passcodes:
        # Read before anything is saved: a bad file changes nothing.
        notes_path = Path(args.passcodes)
        try:
            notes = read_notes(notes_path)
        except OSError as error:
            raise AdminError(
                f"Can't read {notes_path}: {error.strerror or error}"
            ) from error
        except ValueError as error:
            raise AdminError(
                f"{notes_path} isn't a passcodes file this app can read: {error}"
            ) from error
    storage.save_saga(saga)
    console.say(f"Brought in {saga.name} ({saga.id}).")
    if args.passcodes:
        kept = RemotePasscodes(passcodes_path(saga.name)).carry_over(saga, notes)
        console.say(
            f"Passcodes carried over for: {', '.join(kept)}."
            if kept
            else "No passcode records matched the saga's passcodes."
        )
    console.say(
        "It has a host key of its own here: issue every player a new Invite, "
        "your own desktop's storyguide seat included. admin players list says "
        "whose passcode must be set again (admin players set-passcode)."
    )


def backup(args: argparse.Namespace, console: Console) -> None:
    """Back the saga and its Remote seat files up, while players play."""
    saga = load(args.saga)
    try:
        folder = host_backup.backups_folder(args.to)
        made = host_backup.take(saga.id, saga.name, folder, args.keep)
    except ValueError as error:
        raise AdminError(str(error)) from error
    except OSError as error:
        raise AdminError(f"The backup failed: {error.strerror or error}") from error
    console.say(f"Backed up {saga.name} to {made.path} ({len(made.files)} files).")
    if made.removed:
        console.say(f"Removed {len(made.removed)} older, keeping {args.keep}.")
    console.say(
        "The host key isn't in it: keep the key folder's own backup apart, "
        "encrypted, or none."
    )


def saga_delete(args: argparse.Namespace, console: Console) -> None:
    saga = load(args.saga)
    console.say(
        f"This deletes the saga {saga.name} for good: everything in it. Its "
        "backups and Remote seat files stay.",
        "",
    )
    try:
        typed = console.ask("Type the saga's name to delete it: ")
    except EOFError:
        typed = ""
    if typed.strip() != saga.name:
        raise AdminError("That isn't the saga's name: nothing was deleted.")
    storage.delete_saga(saga.id)
    console.say(f"Deleted {saga.name}.")


# -- the command line ------------------------------------------------------------


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser(
        prog="admin",
        description="Look after a hosted saga from a terminal (a host with no window).",
    )
    saga = argparse.ArgumentParser(add_help=False)
    saga.add_argument(
        "--saga",
        help=f"the saga's id or name (else ${SAGA_VARIABLE}, else the only one)",
    )
    sure = argparse.ArgumentParser(add_help=False)
    sure.add_argument("--yes", action="store_true", help="don't ask before acting")
    groups = top.add_subparsers(dest="group", required=True, metavar="GROUP")

    def verb(
        within: Any, name: str, run: Callable[..., None], text: str, *more: Any
    ) -> argparse.ArgumentParser:
        found = within.add_parser(name, parents=[saga, *more], help=text)
        found.set_defaults(run=run)
        return found

    verb(groups, "sagas", sagas_list, "list the sagas here")

    group = groups.add_parser("players", help="the saga's players").add_subparsers(
        dest="verb", required=True, metavar="VERB"
    )
    verb(group, "list", players_list, "list them, and who may have a Remote seat")
    role = verb(
        group, "set-role", players_set_role, "make one a player or storyguide", sure
    )
    role.add_argument("player")
    role.add_argument("role", help=" or ".join(players.ROLES))
    secret = verb(group, "set-passcode", players_set_passcode, "set one's passcode")
    secret.add_argument("player")

    place = verb(
        groups, "tunnel", tunnel, "show or set the tunnel address Invites carry"
    )
    place.add_argument("--url", help="the tunnel's https address")
    place.add_argument(
        "--tunnel", choices=sorted(TUNNELS), help=f"default {CLOUDFLARE}"
    )
    place.add_argument("--port", type=int, help="the listener's port it points at")

    verb(groups, "words", words, "the host's six words and pin")

    group = groups.add_parser("invites", help="Invites and requests").add_subparsers(
        dest="verb", required=True, metavar="VERB"
    )
    verb(group, "issue", invites_issue, "issue a player an Invite").add_argument(
        "player"
    )
    verb(group, "pending", invites_pending, "what waits: seats and new passcodes asked")

    verb(
        groups, "approve", approve, "give a waiting device its seat", sure
    ).add_argument("request", help="its id from invites pending (the start is enough)")
    verb(groups, "reject", reject, "turn a waiting request down", sure).add_argument(
        "request", help="its id from invites pending (the start is enough)"
    )

    group = groups.add_parser("devices", help="the seats").add_subparsers(
        dest="verb", required=True, metavar="VERB"
    )
    verb(group, "list", devices_list, "list the seats, live and ended")
    verb(group, "revoke", devices_revoke, "end a seat at once", sure).add_argument(
        "device", help="its id from devices list (the start is enough)"
    )

    shown = verb(groups, "log", log, "who did what, newest first")
    shown.add_argument("--player", help="that player's entries only")
    shown.add_argument("--limit", type=int, default=LOG_SHOWN)

    verb(groups, "rotate-key", rotate_key, "give the host a new key", sure)

    kept = verb(groups, "backup", backup, "back the saga and its seat files up")
    kept.add_argument("--to", help=f"the folder (else ${host_backup.BACKUPS_VARIABLE})")
    kept.add_argument(
        "--keep",
        type=int,
        default=host_backup.KEEP,
        help=f"how many of the saga's backups to keep (default {host_backup.KEEP})",
    )

    group = groups.add_parser(
        "saga", help="bring a saga in, or delete one"
    ).add_subparsers(dest="verb", required=True, metavar="VERB")
    brought = verb(group, "import", saga_import, "bring in a saga file")
    brought.add_argument("file")
    brought.add_argument(
        "--passcodes",
        metavar="FILE",
        help="the old host's passcode records (remote/NAME-passcodes.json), so "
        "players keep their passcodes",
    )
    verb(group, "delete", saga_delete, "delete the saga (asks for its name)")
    return top


def run(argv: list[str], console: Console | None = None) -> int:
    """Run one verb; 0 when it did its work, 1 when it couldn't (the
    reason printed), as a shell expects."""
    console = console or Console()
    args = parser().parse_args(argv)
    try:
        args.run(args, console)
    except (AdminError, NoKeychainError) as error:
        console.err(str(error))
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    sys.exit(run(sys.argv[1:] if argv is None else argv))


if __name__ == "__main__":
    main()
