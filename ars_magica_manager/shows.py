"""Show (the glossary's): while a Session is Under way, its storyguide
shows a record with a page, or a picture already in the saga, to the
Table or chosen Players. Each is told by a "show" entry in the Chronicle,
whose card opens the copy.

One copy for everyone shown, made once, at the moment of Showing, and
never changed: the record as the players read it (through viewing's
Player view, so no unrevealed Secret, private note or unknown record's
name), or a picture's bytes as they were. It is kept beside the saga, at
`shows/<saga id>/<show id>.json` with the picture next to it (ADR 0020),
so it is in no Export or Content pack, which carry the saga file and the
pictures its records name.

Who may open a copy is the Chronicle's audience filter: someone who sees
the Show's entry. A Remote seat asks for it by the Show's id, and the
host sends it only then (`seen`, `shows_picture`).

Pattern: a Memento-like snapshot (the frozen copy). The copy's text is
made by the copier the caller gives (show_copy.player_copy), since the
printed sheet it draws on sits a layer above the Chronicle's verbs."""

from __future__ import annotations

import contextlib
import hashlib
import json
import secrets
from collections.abc import Callable, Generator, Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from . import (
    chronicle,
    paths,
    picture_files,
    record_links,
    references,
    shapes,
    table_rules,
    viewing,
    world,
)
from .models import (
    Character,
    Covenant,
    Familiar,
    Laboratory,
    Saga,
    Secret,
    Session,
)

FOLDER = paths.SHOWS
#: The most a shown picture may be: a map's most (picture_files.KINDS).
PICTURE_CAP = picture_files.KINDS[picture_files.MAPS].cap
#: The most a copy's file may be read back as.
COPY_CAP = 5 * 1024 * 1024
#: The records that may be shown: those with a printed sheet to copy
#: (print_records.LAYOUTS).
SHOWABLE: tuple[type, ...] = (Character, Covenant, Laboratory, Familiar)

#: Makes a record's copy: its sheet as the players read it, as Markdown,
#: with the Secrets at the places ticked as if revealed.
Copier = Callable[[Saga, Any, tuple[int, ...]], str]

_CHOOSE = "Choose a record or picture to show."
NOT_A_SECRET = (
    "Tick only the record's Secrets not yet revealed; if they have just "
    "changed, tick them again."
)
NOT_YOURS = "Only the record's own storyguide sends its Secrets."
#: Why a withdrawn Show's copy isn't opened.
WITHDRAWN_NOTE = "This Show was withdrawn."
#: Why a Show isn't opened while the Chronicle can't be read to check it.
UNREAD_NOTE = "This Show can't be opened just now: try again in a moment."


def secret_mark(secret: Secret) -> str:
    """A short mark of a Secret's words, sent with its place when it is
    ticked, so a list changed since is refused rather than another Secret
    sent in its place."""
    words = f"{secret.title}\n{secret.text}".encode()
    return hashlib.sha256(words).hexdigest()[:12]


@dataclass(frozen=True)
class Shown:
    """A Show's copy as its reader opens it: its title, and the record's
    text (Markdown) or the picture's bytes and file name."""

    title: str
    text: str = ""
    picture: bytes | None = None
    picture_name: str = ""


def folder_of(saga_id: str) -> Path:
    """Where `saga_id`'s Show copies are kept."""
    if not shapes.is_plain_id(saga_id):
        raise ValueError(f"A saga id can't name a folder: {saga_id!r}")
    return paths.data_dir() / FOLDER / saga_id


def files_of(saga_id: str) -> list[Path]:
    """Every Show copy and picture of the saga `saga_id`, for its backups:
    none for an id no folder could be named by."""
    if not shapes.is_plain_id(saga_id):
        return []
    folder = paths.data_dir() / FOLDER / saga_id
    return sorted(p for p in folder.iterdir() if p.is_file()) if folder.is_dir() else []


# -- what may be shown --


def records(saga: Saga) -> list[references.Ref]:
    """The records that may be shown, by name."""
    found = [
        references.Ref(kind, record.id, record.name)
        for cls, kind in references.KINDS.items()
        if cls in SHOWABLE
        for record in getattr(saga, kind)
        if record.name
    ]
    return sorted(found, key=lambda r: r.name)


def _picture_path(folder: str, name: str) -> Path | None:
    found = picture_files.kind(folder)
    if found is None or not picture_files.safe_name(name):
        return None
    path = found.directory() / name
    return path if path.is_file() else None


def pictures(saga: Saga) -> list[tuple[str, str]]:
    """The pictures already in the saga that may be shown: those its
    records name that are on this computer, as (folder, file name)."""
    return [p for p in record_links.pictures(saga) if _picture_path(*p) is not None]


def picture_label(saga: Saga, picture: tuple[str, str]) -> str:
    """How a picture is named: its map's name, else its file's."""
    folder, name = picture
    if folder == picture_files.MAPS:
        found = next((m.name for m in saga.maps if m.picture == name), "")
        if found:
            return found
    return name


def unrevealed(record: Any) -> list[int]:
    """The places of `record`'s Secrets not yet revealed, which may go
    with its Show (none for a record that keeps no Secrets)."""
    found = getattr(record, "secrets", None)
    if not isinstance(found, list):
        return []
    return [row for row, secret in enumerate(found) if not secret.revealed]


def sends_secrets(saga: Saga, record: Any, who: str) -> bool:
    """Whether `who` may send `record`'s Secrets with a Show: they read it
    whole, as its storyguide (viewing.holds), never another storyguide's."""
    return viewing.holds(chronicle.viewer_of(saga, who), record, saga)


def _why_not_secrets(
    saga: Saga, record: Any, ticked: tuple[tuple[int, str], ...], who: str
) -> str | None:
    """Why the Secrets `ticked` may not go with `record`'s Show, or None:
    each must be one of its Secrets not yet revealed, its words as when it
    was ticked, and the record `who`'s to send."""
    if record is None:
        return NOT_A_SECRET
    if not sends_secrets(saga, record, who):
        return NOT_YOURS
    open_rows = set(unrevealed(record))
    for row, mark in ticked:
        if row not in open_rows or secret_mark(record.secrets[row]) != mark:
            return NOT_A_SECRET
    return None


@contextlib.contextmanager
def _known_while(record: Any, reveal: bool) -> Generator[None]:
    """While the block runs, `record` reads as known to the players when
    its Show also reveals it, so its copy is as they will know it; then as
    before (the form reveals it once the Show is made)."""
    if not (reveal and viewing.can_be_unknown(record)) or record.known:
        yield
        return
    record.known = True
    try:
        yield
    finally:
        record.known = False


def why_not_show(
    saga: Saga, session: Session, call: chronicle.ShowCall, who: str
) -> str | None:
    """Why `who` may not make Show `call` at `session`, or None: as
    `why_not_ask`, and a picture's file must be on this computer (the
    host's)."""
    problem = why_not_ask(saga, session, call, who)
    if problem is None and call.record is None and call.picture not in pictures(saga):
        return _CHOOSE
    return problem


def why_not_ask(
    saga: Saga, session: Session, call: chronicle.ShowCall, who: str
) -> str | None:
    """Why `who` may not ask for Show `call` at `session`, or None (a
    Remote seat's form asks this of its copy of the saga): only the
    Session's storyguide while it is Under way (table_rules), of a record
    that may be shown or a picture already in the saga, to Players at the
    Session (none: the Table)."""
    problem = table_rules.why_not_lead(saga, session, who, "shows something")
    if problem:
        return problem
    if not call.title.strip():
        return "Give the Show a title."
    words = chronicle.typed_problem(chronicle.SHOW, {"title": call.title})
    if words:
        return words
    record = references.target(saga, call.record) if call.record else None
    if call.record is not None:
        if not isinstance(record, SHOWABLE):
            return _CHOOSE
    elif call.picture is None or call.picture not in record_links.pictures(saga):
        return _CHOOSE
    if call.secrets:
        problem = _why_not_secrets(saga, record, call.secrets, who)
        if problem:
            return problem
    storyguide = table_rules.storyguide_of(session, saga)
    shown = set(chronicle.at_session(saga, session)) - {storyguide}
    if any(t not in shown for t in call.to):
        return "Show only to Players at the Session."
    if call.story_id and world.open_story(saga, call.story_id) is None:
        return "That story isn't open."
    return None


# -- showing --


def _copy_record(
    saga: Saga, call: chronicle.ShowCall, copier: Copier
) -> dict[str, Any]:
    """The copy of the record `call` shows, with the Secrets it ticked, as
    the players will know it; ValueError when it can't be made (a record
    with no printed sheet, or a lookup in its sheet's builders that finds
    nothing)."""
    record = references.target(saga, call.record) if call.record else None
    if record is None:
        raise ValueError(_CHOOSE)
    try:
        with _known_while(record, call.reveal):
            text = copier(saga, record, tuple(row for row, _ in call.secrets))
    except (KeyError, IndexError) as problem:
        raise ValueError(f"{record.name}'s copy couldn't be made.") from problem
    return {"name": record.name, "text": text}


def _copy_picture(
    saga: Saga, show_id: str, picture: tuple[str, str], made: list[Path]
) -> dict[str, Any]:
    """The picture's copy, its file noted in `made` before it is written."""
    source = _picture_path(*picture)
    if source is None:
        raise ValueError(_CHOOSE)
    if source.stat().st_size > PICTURE_CAP:
        raise ValueError("That picture is too large to show.")
    name = show_id + PurePosixPath(picture[1]).suffix.lower()
    made.append(folder_of(saga.id) / name)
    made[-1].write_bytes(source.read_bytes())
    return {"name": picture_label(saga, picture), "picture": name}


def show(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    call: chronicle.ShowCall,
    *,
    by: str,
    copier: Copier,
) -> chronicle.Entry:
    """Make Show `call`: its one copy written beside the saga, then its
    entry, seen by the Players shown (and the storyguide) or the Table."""
    problem = why_not_show(saga, session, call, by)
    if problem:
        raise ValueError(problem)
    show_id = secrets.token_hex(8)
    folder = folder_of(saga.id)
    folder.mkdir(parents=True, exist_ok=True)
    made: list[Path] = []
    try:
        return _show(book, saga, session, call, by, copier, show_id, made)
    except OSError, ValueError:
        for path in made:  # never shown, so its copy goes too
            path.unlink(missing_ok=True)
        raise


def _show(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    call: chronicle.ShowCall,
    by: str,
    copier: Copier,
    show_id: str,
    made: list[Path],
) -> chronicle.Entry:
    """Show's steps, each file it writes noted in `made` first."""
    title = call.title.strip()
    kept: dict[str, Any] = {"show": show_id, "title": title, "time": chronicle.clock()}
    if call.record is not None:
        kept |= _copy_record(saga, call, copier)
        ref = [call.record.kind, call.record.id, kept["name"]]
    else:
        assert call.picture is not None
        kept |= _copy_picture(saga, show_id, call.picture, made)
        ref = []
    made.append(folder_of(saga.id) / f"{show_id}.json")
    made[-1].write_text(json.dumps(kept, ensure_ascii=False), encoding="utf-8")
    to = list(dict.fromkeys(call.to))
    story = world.open_story(saga, call.story_id)
    body: dict[str, Any] = {
        "show": show_id,
        "title": title,
        "ref": ref,
        "picture": kept.get("picture", ""),
        "to": to,
        "to_names": [chronicle.name_at(saga, session, t) for t in to],
        "story": story.name if story is not None else "",
        "story_id": story.id if story is not None else "",
    }
    audience = chronicle.chosen(*to) if to else chronicle.table()
    return book.add(chronicle.SHOW, by, audience, body)


# -- withdrawing --


def withdrawn(book: chronicle.HasEntries) -> set[int]:
    """The Shows of `book` withdrawn, by their entries' numbers; a
    withdrawal that names no number (a damaged line) is passed over."""
    found = set()
    for entry in book.entries:
        number = entry.body.get("withdraws")
        if entry.kind == chronicle.WITHDRAWN and type(number) is int:
            found.add(number)
    return found


def withdraw(
    book: chronicle.Chronicle, saga: Saga, session: Session, number: int, *, by: str
) -> chronicle.Entry:
    """Withdraw Show `number`: an entry, seen by whoever saw the Show, that
    marks it withdrawn; its copy is opened by no Player from then on. Only
    the Session's storyguide, while it is Under way (table_rules)."""
    problem = table_rules.why_not_lead(saga, session, by, "withdraws a Show")
    if problem:
        raise ValueError(problem)
    shown = next((e for e in book.entries if e.number == number), None)
    if shown is None or shown.kind != chronicle.SHOW:
        raise ValueError("There is no such Show.")
    already = "That Show is already withdrawn."
    if number in withdrawn(book):
        raise ValueError(already)
    body = {"withdraws": number, "title": str(shown.body.get("title", ""))}
    # Asked again once caught up under the file's lock: another copy (the
    # host's window, its listener for a seat) may have withdrawn it since.
    return book.add(
        chronicle.WITHDRAWN,
        by,
        shown.audience,
        body,
        guard=lambda: already if number in withdrawn(book) else None,
    )


# -- opening --


def _read_copy(saga_id: str, show_id: str) -> dict[str, Any]:
    """The copy kept for Show `show_id`; ValueError when it can't be read."""
    if not shapes.is_plain_id(show_id):
        raise ValueError("No such Show.")
    path = folder_of(saga_id) / f"{show_id}.json"
    try:
        if path.stat().st_size > COPY_CAP:
            raise ValueError("This Show's copy is too large.")
        found = json.loads(path.read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, json.JSONDecodeError:
        raise ValueError("This Show's copy can't be read.") from None
    if not isinstance(found, dict):
        raise ValueError("This Show's copy can't be read.")
    return found


def copy_text(saga_id: str, show_id: str) -> bytes:
    """Show `show_id`'s copy as its file keeps it, to send a seat."""
    return json.dumps(_read_copy(saga_id, show_id), ensure_ascii=False).encode()


def from_copy(data: dict[str, Any], picture: bytes | None = None) -> Shown:
    """A copy as a reader opens it, from its kept form (and its picture)."""
    return Shown(
        str(data.get("title", "")),
        str(data.get("text", "")),
        picture,
        str(data.get("picture", "")),
    )


def picture_bytes(saga_id: str, name: str) -> bytes | None:
    """A shown picture's bytes, by its file name in the Show folder."""
    if not picture_files.safe_name(name):
        return None
    path = folder_of(saga_id) / name
    try:
        if path.stat().st_size > PICTURE_CAP:
            return None
        return path.read_bytes()
    except OSError:
        return None


def opened(saga_id: str, entry: chronicle.Entry) -> Shown:
    """Show `entry`'s copy, read from the host's own folder; ValueError
    when it can't be."""
    found = _read_copy(saga_id, str(entry.body.get("show", "")))
    name = str(found.get("picture", ""))
    picture = picture_bytes(saga_id, name) if name else None
    if name and picture is None:
        raise ValueError("This Show's picture can't be read.")
    return from_copy(found, picture)


# -- who may open one --


def _shows(saga: Saga) -> Iterator[tuple[Session, chronicle.Entry, bool]]:
    """Every Show in the saga's Chronicles, each with its Session and
    whether it was withdrawn, read
    from the files as they stand: the Session under way's first, where
    tonight's Shows are, then the others, newest first, each read only if
    the ones before didn't hold what was sought. A Chronicle that can't be
    read is passed over, so one damaged file hides only its own Shows."""
    under_way = chronicle.under_way(saga)
    order = [s for s in reversed(saga.sessions) if s is not under_way]
    for session in ([under_way] if under_way is not None else []) + order:
        if not chronicle.has_chronicle(saga, session):
            continue
        try:
            book = chronicle.Chronicle(chronicle.path_of(saga, session), [])
            book.refresh()
        except OSError, ValueError:
            continue
        gone = withdrawn(book)
        for entry in book.entries:
            if entry.kind == chronicle.SHOW:
                yield session, entry, entry.number in gone


def seen(saga: Saga, show_id: str, who: str) -> chronicle.Entry | None:
    """Show `show_id`'s entry, when `who` sees it and may open it still
    (a withdrawn Show only its Session's storyguide); else None."""
    if not shapes.is_plain_id(show_id):
        return None
    for session, entry, gone in _shows(saga):
        if entry.body.get("show") != show_id:
            continue
        if gone and who != table_rules.storyguide_of(session, saga):
            return None
        return entry if chronicle.sees(entry, who, session, saga) else None
    return None


def shows_picture(saga: Saga, name: str, who: str) -> bool:
    """Whether `name` is the picture of a Show `who` sees: a Show's picture
    is named for the Show (its id and the picture's suffix)."""
    entry = seen(saga, PurePosixPath(name).stem, who) if name else None
    return entry is not None and entry.body.get("picture") == name
