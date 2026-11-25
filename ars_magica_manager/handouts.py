"""Written Handouts: letters, proclamations and pages the storyguide
writes ahead of a Session, kept in the saga's Handouts list (Saga
content) and Shown to the table on the night (ADR 0021).

A Handout is a title, a Stationery (vellum, a sealed letter, a
proclamation), its text in the app's markup with the six handout tags
(handout_markup.py), up to four pictures, who found it and where, and the
Story it belongs to. The pictures are files already in the saga (a map's,
a portrait) or new ones copied into the handouts folder. Only the
storyguide holds them (viewing.STORYGUIDE_ONLY, seat_view) until one is
Shown.

Pattern: a record kind with its core Form and SectionOps
(forms/handouts.py), its link fields one entry of the links list
(record_links), the text read by one small Interpreter
(handout_markup) and laid on its Stationery for each front-end to draw
(handout_layout)."""

from __future__ import annotations

import hashlib
import shutil
import uuid
from collections.abc import Sequence
from pathlib import Path

from . import handout_layout as layout
from . import handout_markup as hm
from . import picture_files, record_links, scenes, shapes
from .markup import escape
from .models import Handout, HandoutPicture, Saga
from .paths import HANDOUTS, MAPS, PORTRAITS
from .rules import sites

#: The most characters a Handout's text may have.
MOST_TEXT = 20_000
#: The most pictures a Handout may have.
MOST_PICTURES = hm.MOST_PICTURES

#: What each kind of picture is called beside its name, by folder.
PICTURE_KINDS: dict[str, str] = {
    MAPS: "map",
    PORTRAITS: "portrait",
    HANDOUTS: "handout picture",
}

#: A picture reference's prefix for a file chosen on this computer, to be
#: copied into the handouts folder when the Handout is saved.
NEW_FILE = "file"


def new_id() -> str:
    return f"handout-{uuid.uuid4().hex[:8]}"


def find(saga: Saga, handout_id: str) -> Handout | None:
    return next((h for h in saga.handouts if h.id == handout_id), None)


# -- what it may say --


def why_not(title: str, text: str, pictures: int) -> str | None:
    """Why a Handout with this title, text and number of pictures can't be
    kept, or None: the text's length, the pictures' count, and the
    character rule every text the Chronicle carries keeps."""
    if len(text) > MOST_TEXT:
        return (
            f"A Handout's text is at most {MOST_TEXT:,} characters "
            f"(this is {len(text):,})."
        )
    if pictures > MOST_PICTURES:
        return f"A Handout has at most {MOST_PICTURES} pictures."
    return shapes.why_not_words(title) or shapes.why_not_words(text)


# -- its pictures --


def picture_ref(picture: HandoutPicture) -> str:
    """A picture as a form's list holds it: "folder:name"."""
    return f"{picture.folder}:{picture.name}"


def new_picture_ref(path: Path) -> str:
    """A form's reference to a picture file chosen on this computer."""
    return f"{NEW_FILE}:{path}"


def picture_from(ref: str) -> HandoutPicture | None:
    """The picture a form's "folder:name" reference names, or None when it
    isn't one: an unknown folder, or a name that isn't a picture's bare
    file name (picture_files.safe_name)."""
    folder, _, name = ref.partition(":")
    if picture_files.kind(folder) is None or not picture_files.safe_name(name):
        return None
    return HandoutPicture(folder, name)


def new_picture(source: Path) -> HandoutPicture | None:
    """The handouts folder's picture `source` would be kept as, named by a
    hash of its bytes, copying nothing; None when it isn't a picture file
    the app takes (its kind, or too big for the folder), or can't be read."""
    suffix = ".jpg" if source.suffix.lower() == ".jpeg" else source.suffix.lower()
    if suffix not in picture_files.SUFFIXES:
        return None
    try:
        data = source.read_bytes()
    except OSError:
        return None
    if len(data) > picture_files.KINDS[HANDOUTS].cap:
        return None
    return HandoutPicture(HANDOUTS, hashlib.sha256(data).hexdigest()[:20] + suffix)


def store_picture(source: Path) -> HandoutPicture | None:
    """Copy `source` into the handouts folder as new_picture names it
    (kept as it is when that copy is already there); None when it isn't a
    picture the folder takes."""
    picture = new_picture(source)
    if picture is None:
        return None
    folder = picture_files.KINDS[HANDOUTS].directory()
    folder.mkdir(parents=True, exist_ok=True)
    if not (folder / picture.name).is_file():
        shutil.copyfile(source, folder / picture.name)
    return picture


def kept_refs(refs: Sequence[str]) -> list[tuple[str, HandoutPicture]]:
    """The form's picture references a Handout keeps, each with the
    picture it is kept as, in order: anything that isn't a picture the
    app takes left out, and each picture once (two files with the same
    bytes are one). Save and Preview both go by this, so a Preview's
    picture numbers are the saved Handout's. Nothing is copied."""
    found: list[tuple[str, HandoutPicture]] = []
    for ref in dict.fromkeys(refs):
        kind, _, rest = ref.partition(":")
        picture = new_picture(Path(rest)) if kind == NEW_FILE else picture_from(ref)
        if picture is not None and all(picture != held for _, held in found):
            found.append((ref, picture))
    return found


def pictures_from(refs: list[str]) -> list[HandoutPicture]:
    """A form's picture references as the Handout keeps them (kept_refs),
    each new file copied into the handouts folder."""
    found: list[HandoutPicture] = []
    for ref, picture in kept_refs(refs):
        kind, _, rest = ref.partition(":")
        stored = store_picture(Path(rest)) if kind == NEW_FILE else picture
        if stored is not None:
            found.append(stored)
    return found


def picture_choices(saga: Saga) -> list[tuple[str, str]]:
    """The pictures already in the saga, as (label, "folder:name"): the
    maps', the portraits, then the handouts' own, each once."""
    found: dict[str, str] = {}
    for atlas_map in saga.maps:
        if atlas_map.picture:
            found.setdefault(f"{MAPS}:{atlas_map.picture}", f"{atlas_map.name} (map)")
    for character in saga.characters:
        if character.portrait:
            found.setdefault(
                f"{PORTRAITS}:{character.portrait}", f"{character.name} (portrait)"
            )
    for handout in saga.handouts:
        for picture in handout.pictures:
            if picture.folder == HANDOUTS:
                found.setdefault(
                    picture_ref(picture), f"{picture.name} (handout picture)"
                )
    return [(label, ref) for ref, label in found.items()]


def picture_name(saga: Saga, picture: HandoutPicture) -> str:
    """What a picture is called: its map's or portrait's owner, else its
    file name."""
    if picture.folder == MAPS:
        found = next((m for m in saga.maps if m.picture == picture.name), None)
        if found is not None:
            return found.name
    if picture.folder == PORTRAITS:
        held = next((c for c in saga.characters if c.portrait == picture.name), None)
        if held is not None:
            return held.name
    return picture.name


def ref_name(saga: Saga, ref: str) -> str:
    """What a form's picture reference is shown by on the page: its map's
    or portrait's owner, else its file's name."""
    kind, _, rest = ref.partition(":")
    if kind == NEW_FILE:
        return Path(rest).name
    picture = picture_from(ref)
    return "(picture)" if picture is None else picture_name(saga, picture)


def ref_file(ref: str) -> Path | None:
    """Where on this computer the picture a form's reference names is, or
    None when it isn't there (or isn't a picture's reference)."""
    kind, _, rest = ref.partition(":")
    if kind == NEW_FILE:
        found = Path(rest)
    else:
        picture = picture_from(ref)
        if picture is None:
            return None
        found = picture_files.KINDS[picture.folder].directory() / picture.name
    return found if found.is_file() else None


def ref_label(saga: Saga, ref: str) -> str:
    """A form's picture reference as its list shows it."""
    kind, _, rest = ref.partition(":")
    if kind == NEW_FILE:
        return f"{Path(rest).name} (new)"
    picture = picture_from(ref)
    if picture is None:
        return ref
    return f"{picture_name(saga, picture)} ({PICTURE_KINDS.get(picture.folder, '')})"


# -- who found it, where, and its story --


def finder_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(c.name), c.id) for c in saga.characters]


def place_options(saga: Saga) -> list[tuple[str, str]]:
    return [(escape(p.name), p.id) for p in sites.all_places(saga)]


def finder_name(saga: Saga, handout: Handout) -> str:
    """Who found it: the character, or the name kept once they're gone."""
    found = saga.character(handout.found_by_id) if handout.found_by_id else None
    return found.name if found is not None else handout.found_by


def place_name(saga: Saga, handout: Handout) -> str:
    """Where it was found: the Place, or the name kept once it's gone."""
    found = saga.neighbour(handout.place_id) if handout.place_id else None
    return found.name if found is not None else handout.place_name


def listed(saga: Saga, story_id: str = "") -> list[Handout]:
    """The Handouts, in the order written; with `story_id`, only that
    Story's."""
    if not story_id:
        return list(saga.handouts)
    return [h for h in saga.handouts if h.story_id == story_id]


#: Each saga's chosen Story ("": every story), by the saga's id, while the
#: app runs. Pattern: Specification, as neighbour_filter's: kept here in
#: the core, so the list, its title and the rows Edit and Delete act on
#: always agree, whichever front-end's control chose it.
_STORY: dict[str, str] = {}


def current_story(saga: Saga) -> str:
    """The Story the list is narrowed to; one since gone narrows nothing."""
    chosen = _STORY.get(saga.id, "")
    return chosen if chosen and scenes.story_name(saga, chosen) else ""


def choose_story(saga: Saga, story_id: str) -> None:
    if story_id:
        _STORY[saga.id] = story_id
    else:
        _STORY.pop(saga.id, None)


def shown(saga: Saga) -> list[Handout]:
    """The Handouts the list shows: the chosen Story's, or every one."""
    return listed(saga, current_story(saga))


def title(saga: Saga) -> str:
    """ "Handouts (3)", or "Handouts (1 of 3)" while narrowed."""
    total = len(saga.handouts)
    if not current_story(saga):
        return f"Handouts ({total})"
    return f"Handouts ({len(shown(saga))} of {total})"


def story_filters(saga: Saga) -> list[tuple[str, str]]:
    """The Stories the Handouts belong to, as (name, id): what the list can
    be narrowed to."""
    found: dict[str, str] = {}
    for handout in saga.handouts:
        name = scenes.story_name(saga, handout.story_id)
        if name:
            found.setdefault(handout.story_id, name)
    return [(name, story_id) for story_id, name in found.items()]


# -- as the lists show it --


def row(handout: Handout) -> str:
    """A Handout's row (plain text): its title and Stationery."""
    return f"{handout.title or '(untitled)'} ({handout.stationery})"


COLUMNS = ["Title", "Stationery", "Found by", "Story"]


def cells(saga: Saga, handout: Handout) -> list[str]:
    """A Handout's row of the desktop's table (plain text)."""
    return [
        handout.title or "(untitled)",
        handout.stationery.capitalize(),
        finder_name(saga, handout) or "-",
        scenes.story_name(saga, handout.story_id) or "-",
    ]


def text_markup(saga: Saga, handout: Handout) -> str:
    """The Handout's text as the terminal shows it (markup): a heading in
    bold, a flourish as a line of tildes, each picture named."""
    lines: list[str] = []
    for block in hm.blocks(handout.text, len(handout.pictures)):
        if block.kind == hm.HEADING:
            lines.append(f"[b]{block.text}[/]")
        elif block.kind == hm.FLOURISH:
            lines.append("~ ~ ~")
        elif block.kind == hm.PICTURE:
            picture = handout.pictures[block.picture - 1]
            name = escape(picture_name(saga, picture))
            lines.append(f"(picture {block.picture}: {name})")
        else:
            lines.append(block.text)
    return "\n".join(lines)


def detail(saga: Saga, handout: Handout | None) -> str:
    """The details panel (markup) for a chosen Handout: what it is, then
    its text under its Stationery's name."""
    if handout is None:
        return "[dim]Choose a Handout to read it; a writes one.[/]"
    lines = [
        f"[b]{escape(handout.title or '(untitled)')}[/]",
        f"[$label]Stationery:[/] {escape(handout.stationery.capitalize())}",
    ]
    finder, where = finder_name(saga, handout), place_name(saga, handout)
    if finder:
        at = f", at {where}" if where else ""
        lines.append(f"[$label]Found by:[/] {escape(finder + at)}")
    elif where:
        lines.append(f"[$label]Found at:[/] {escape(where)}")
    if handout.pictures:
        named = "; ".join(
            f"{n}. {ref_label(saga, picture_ref(p))}"
            for n, p in enumerate(handout.pictures, 1)
        )
        lines.append(f"[$label]Pictures:[/] {escape(named)}")
    story = scenes.story_name(saga, handout.story_id)
    if story:
        lines.append(f"[$label]Story:[/] {escape(story)}")
    if handout.text.strip():
        lines += ["", text_markup(saga, handout)]
    return "\n".join(lines)


def preview(
    saga: Saga, title: str, stationery: str, text: str, refs: Sequence[str]
) -> layout.Preview:
    """A Handout as its form holds it (its pictures as the form's
    references, a new file's among them) laid on its Stationery, with
    where each picture's file is: what the form's Preview draws."""
    refs = [ref for ref, _picture in kept_refs(refs)]
    return layout.Preview(
        layout.lay_out(title, stationery, text, [ref_name(saga, r) for r in refs]),
        tuple(ref_file(r) for r in refs),
    )


def preview_of(saga: Saga, handout: Handout) -> layout.Preview:
    """A saved Handout laid on its Stationery, with its pictures' files."""
    return preview(
        saga,
        handout.title,
        handout.stationery,
        handout.text,
        [picture_ref(p) for p in handout.pictures],
    )


def delete(saga: Saga, handout: Handout) -> list[record_links.Change]:
    """Take `handout` out of the saga. Nothing names a Handout (a Show
    keeps its own copy), so nothing else changes; its picture files stay."""
    saga.handouts = [h for h in saga.handouts if h is not handout]
    return []
