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

import json
import secrets
from collections.abc import Callable, Iterator
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
    world,
)
from .models import Character, Covenant, Familiar, Laboratory, Saga, Session

FOLDER = paths.SHOWS
#: The most a shown picture may be: a map's most (picture_files.KINDS).
PICTURE_CAP = picture_files.KINDS[picture_files.MAPS].cap
#: The most a copy's file may be read back as.
COPY_CAP = 5 * 1024 * 1024
#: The records that may be shown: those with a printed sheet to copy
#: (print_records.LAYOUTS).
SHOWABLE: tuple[type, ...] = (Character, Covenant, Laboratory, Familiar)

#: Makes a record's copy: its sheet as the players read it, as Markdown.
Copier = Callable[[Saga, Any], str]

_CHOOSE = "Choose a record or picture to show."


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
    if call.record is not None:
        if not isinstance(references.target(saga, call.record), SHOWABLE):
            return _CHOOSE
    elif call.picture is None or call.picture not in record_links.pictures(saga):
        return _CHOOSE
    storyguide = table_rules.storyguide_of(session, saga)
    shown = set(chronicle.at_session(saga, session)) - {storyguide}
    if any(t not in shown for t in call.to):
        return "Show only to Players at the Session."
    if call.story_id and world.open_story(saga, call.story_id) is None:
        return "That story isn't open."
    return None


# -- showing --


def _copy_record(saga: Saga, ref: references.Ref, copier: Copier) -> dict[str, Any]:
    """The record's copy; ValueError when it can't be made (a record with
    no printed sheet, or a lookup in its sheet's builders that finds
    nothing)."""
    record = references.target(saga, ref)
    if record is None:
        raise ValueError(_CHOOSE)
    try:
        text = copier(saga, record)
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
        kept |= _copy_record(saga, call.record, copier)
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


def _shows(saga: Saga) -> Iterator[tuple[Session, chronicle.Entry]]:
    """Every Show in the saga's Chronicles, each with its Session, read
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
        for entry in book.entries:
            if entry.kind == chronicle.SHOW:
                yield session, entry


def seen(saga: Saga, show_id: str, who: str) -> chronicle.Entry | None:
    """Show `show_id`'s entry, when `who` sees it; else None."""
    if not shapes.is_plain_id(show_id):
        return None
    for session, entry in _shows(saga):
        if entry.body.get("show") == show_id:
            return entry if chronicle.sees(entry, who, session, saga) else None
    return None


def shows_picture(saga: Saga, name: str, who: str) -> bool:
    """Whether `name` is the picture of a Show `who` sees: a Show's picture
    is named for the Show (its id and the picture's suffix)."""
    entry = seen(saga, PurePosixPath(name).stem, who) if name else None
    return entry is not None and entry.body.get("picture") == name
