"""Scenes: the saga's library of reusable Scenes, and each Session's uses
of them.

A Scene is built once and reused (one Covenant Scene for every evening
of covenant business). It has a title; a place, which is a saga Place and
one of its levels, a covenant, or a name typed for somewhere that is no
record; an aura and realm, which start as the place's (through the sites
rules, so a regio's level gives its own) and may be changed; the actors
usually there (saga characters, Bestiary creatures, neighbours who are
people); the open story it plays; a map already in the saga; what to show
from it; and the storyguide's notes, the prep sheet.

A Session holds its uses of Scenes, in the order they are to be played:
each names its Scene, has its own state and who is present this time
(tonight's cast and the Scene's regulars to start with), and its own notes
for the evening. The same Scene can be used in many Sessions, or twice in
one.

A use is Prepared, Playing or Ended, and what the storyguide may do to one
depends on which: a Prepared use can be changed, put elsewhere in the
order, moved to another planned Session or taken out; a Playing one can
change who is present but not move or be taken out; an Ended one keeps who
was there, and only its notes change.

Setting a Scene plays it and ends the one playing; End scene ends it; an
Ended one can be set again (MOVES). Those moves are the Table's verbs
(scene_play.py), written to the Chronicle, which a Remote seat can reach
and the saga file can't: while the Session is Under way a use's state is
the one kept on it with the Chronicle's moves replayed over it (replay),
and End Session writes where they ended back to the use.

Pattern: State, as a field on the use, one table of moves (MOVES) and one
of what each state allows (ALLOWS), not a class per state; a use names its
Scene, and a Scene its actors and what to show, by id, resolved when
shown, as a chapter names its story."""

from __future__ import annotations

import uuid
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass

from . import catalog, open_stories, places, references, story_chapters
from . import sessions as ss
from .markup import escape
from .models import REALMS, Saga, Scene, SceneUse, Session
from .record_links import CHARACTERS, CREATURES, MAPS_KIND, NEIGHBOURS, SHOWABLE
from .rules.lunar import LUNAR
from .rules.realms import covenant_effective_aura
from .rules.sites import aura_at, levels, place

PREPARED, PLAYING, ENDED = "prepared", "playing", "ended"
STATES: tuple[str, ...] = (PREPARED, PLAYING, ENDED)
STATE_LABELS: dict[str, str] = {
    PREPARED: "Prepared",
    PLAYING: "Playing",
    ENDED: "Ended",
}


@dataclass(frozen=True)
class Allows:
    """What the storyguide may do to a use of a Scene in one state: change
    who is present, move it (in the order, or to another Session) and take
    it out. Its notes can always change."""

    present: bool
    move: bool
    take_out: bool


#: What each state allows.
ALLOWS: dict[str, Allows] = {
    PREPARED: Allows(present=True, move=True, take_out=True),
    PLAYING: Allows(present=True, move=False, take_out=False),
    ENDED: Allows(present=False, move=False, take_out=False),
}


#: A use's states as the Chronicle has moved them this evening, by the
#: use's id (scene_play.now); empty outside a Session Under way.
Now = Mapping[str, str]

#: The moves: setting a Scene, and ending it.
SET, END = "set", "end"

#: Where each move takes a use from each state it may be made in.
MOVES: dict[tuple[str, str], str] = {
    (PREPARED, SET): PLAYING,
    (ENDED, SET): PLAYING,
    (PLAYING, END): ENDED,
}


def why_not_move(current: str, move: str) -> str | None:
    """Why `move` can't be made from the state `current`, or None."""
    if (current, move) in MOVES:
        return None
    return (
        "This Scene is already playing." if move == SET else "This Scene isn't playing."
    )


def replay(session: Session, moves: Iterable[tuple[str, str]]) -> dict[str, str]:
    """Each of `session`'s uses' states after `moves` (a use's id and
    SET or END, in order), from those kept on them: setting one ends the
    one playing. A move this table refuses, or of a use no longer in the
    Session, is passed over, so the Chronicle always reads back."""
    found = {u.id: state(session, u) for u in session.scenes}
    for use_id, move in moves:
        if use_id not in found or why_not_move(found[use_id], move):
            continue
        if move == SET:
            for other, current in found.items():
                if current == PLAYING:
                    found[other] = ENDED
        found[use_id] = MOVES[found[use_id], move]
    return found


def state(session: Session, use: SceneUse, now: Now | None = None) -> str:
    """`use`'s state as it stands: as `now` has it while the Session is
    Under way, else as kept on it. One left Playing in a played Session is
    Ended, and a state this copy doesn't know counts as Ended too, so
    nothing played is lost."""
    if now and use.id in now:
        return now[use.id]
    if use.state not in ALLOWS or (session.played and use.state == PLAYING):
        return ENDED
    return use.state


def allows(session: Session, use: SceneUse, now: Now | None = None) -> Allows:
    """What `use`'s state allows (state)."""
    return ALLOWS[state(session, use, now)]


def state_label(session: Session, use: SceneUse, now: Now | None = None) -> str:
    return STATE_LABELS[state(session, use, now)]


def new_scene_id() -> str:
    return f"scene-{uuid.uuid4().hex[:8]}"


def new_use_id() -> str:
    return f"use-{uuid.uuid4().hex[:8]}"


def find(saga: Saga, scene_id: str) -> Scene | None:
    return next((s for s in saga.scenes if s.id == scene_id), None)


def title(saga: Saga, use: SceneUse) -> str:
    """The use's Scene's title; "(a Scene since deleted)" if it is gone."""
    scene = find(saga, use.scene_id)
    if scene is None:
        return "(a Scene since deleted)"
    return scene.title or "(untitled)"


# -- where it is --

#: The prefixes of a place choice's value: "place:<id>@<level>" for a
#: Place (and level), "covenant:<id>" for a covenant.
PLACE, COVENANT = "place", "covenant"


def where_value(scene: Scene | None) -> str | None:
    """`scene`'s place as one choice's value; None for a typed place."""
    if scene is None:
        return None
    if scene.covenant_id:
        return f"{COVENANT}:{scene.covenant_id}"
    found = places.where_value(scene.place_id, scene.place_level)
    return f"{PLACE}:{found}" if found else None


def where_options(saga: Saga) -> list[tuple[str, str]]:
    """Each covenant, then each Place and each of its levels, as a choice."""
    covenants = [(escape(c.name), f"{COVENANT}:{c.id}") for c in saga.covenants]
    return covenants + [
        (label, f"{PLACE}:{value}") for label, value in places.where_options(saga)
    ]


def put_where(scene: Scene, value: str | None) -> None:
    """Place `scene` where the choice `value` says (None: a typed place)."""
    kind, _, rest = (value or "").partition(":")
    scene.covenant_id = rest if kind == COVENANT else ""
    scene.place_id, scene.place_level = places.split(rest if kind == PLACE else None)


def aura_of(saga: Saga, value: str | None) -> tuple[int, str] | None:
    """The aura and realm the place chosen as `value` gives, or None for a
    typed place (or one since deleted)."""
    kind, _, rest = (value or "").partition(":")
    if kind == COVENANT:
        covenant = saga.covenant(rest)
        if covenant is None:
            return None
        total = covenant_effective_aura(
            covenant, catalog.load_covenant_boon_hook_catalog_by_id()
        )
        return total, covenant.aura_realm
    if kind == PLACE:
        place_id, level = places.split(rest)
        found = place(saga, place_id)
        if found is None:
            return None
        return aura_at(found, min(level, len(levels(found))))
    return None


def place_text(saga: Saga, scene: Scene) -> str:
    """Where `scene` is, as the storyguide reads it: "The Drachenfels,
    Level 1: The Vine Terraces", a covenant's name, or what was typed."""
    if scene.covenant_id:
        covenant = saga.covenant(scene.covenant_id)
        if covenant is not None:
            return covenant.name
    if scene.place_id and place(saga, scene.place_id) is not None:
        return places.where_text(saga, scene.place_id, scene.place_level)
    return scene.place_name


def aura_text(scene: Scene) -> str:
    """ "Magic 3", "2, no realm", or "none" for no aura."""
    if not scene.aura and not scene.realm:
        return "none"
    if not scene.realm:
        return f"{scene.aura}, no realm"
    return f"{scene.realm} {scene.aura}"


#: The realms a Scene's aura may be of: the four, and the Moon's (an aura
#: a place can have, Dies Irae p. 36; rules.lunar).
REALM_CHOICES: tuple[str, ...] = (*REALMS, LUNAR)


# -- actors and what to show: "kind:id" --

#: The kinds of neighbour that can be in a Scene as an actor.
ACTOR_NEIGHBOURS = frozenset({"lord", "faction", "threat"})


def ref_of(kind: str, record_id: str) -> str:
    return f"{kind}:{record_id}"


def record_of(saga: Saga, ref: str) -> object | None:
    """The record a "kind:id" reference names, or None when it is gone."""
    kind, _, record_id = ref.partition(":")
    if kind == MAPS_KIND:
        return next((m for m in saga.maps if m.id == record_id), None)
    return references.find(saga, kind, record_id)


def name_of(saga: Saga, ref: str) -> str:
    found = record_of(saga, ref)
    name = getattr(found, "name", "") if found is not None else ""
    return name or "(gone)"


def actor_names(
    saga: Saga, refs: Sequence[str], use: SceneUse | None = None
) -> list[str]:
    """The actors' names: as the saga has them now, else as `use` wrote
    them (one since deleted, in a played Session); those with neither are
    left out."""
    written = use.names if use is not None else {}
    found = []
    for ref in refs:
        record = record_of(saga, ref)
        name = getattr(record, "name", "") if record is not None else written.get(ref)
        if name:
            found.append(name)
    return found


def keep_names(saga: Saga, use: SceneUse) -> None:
    """Write each present actor's name into `use` as it stands, so a played
    Session still names them after they are deleted."""
    for ref in use.present:
        record = record_of(saga, ref)
        name = getattr(record, "name", "") if record is not None else ""
        if name:
            use.names[ref] = name
    use.names = {r: n for r, n in use.names.items() if r in use.present}


def actor_choices(saga: Saga) -> list[tuple[str, str]]:
    """Every actor a Scene may hold, as (name, "kind:id"): the saga's
    characters, then its creatures, then its neighbours who are people."""
    found = [(c.name, ref_of(CHARACTERS, c.id)) for c in saga.characters]
    found += [(c.name, ref_of(CREATURES, c.id)) for c in saga.creatures]
    found += [
        (n.name, ref_of(NEIGHBOURS, n.id))
        for n in saga.neighbours
        if n.kind in ACTOR_NEIGHBOURS
    ]
    return found


#: How a kind of record a Scene may show is headed in its chooser (any
#: other: its kind's name).
SHOWABLE_HEADINGS: dict[str, str] = {
    MAPS_KIND: "Maps",
    NEIGHBOURS: "Neighbours and Places",
}


def showable_heading(kind: str) -> str:
    return SHOWABLE_HEADINGS.get(kind, kind.title())


def showable_choices(saga: Saga) -> list[tuple[str, str, str]]:
    """Everything a Scene may show, as (heading, name, "kind:id"): its
    maps first, then each kind of record with a page."""
    found = [
        (showable_heading(MAPS_KIND), m.name, ref_of(MAPS_KIND, m.id))
        for m in saga.maps
    ]
    for kind in SHOWABLE:
        if kind == MAPS_KIND:
            continue
        found += [
            (showable_heading(kind), r.name, ref_of(kind, r.id))
            for r in getattr(saga, kind)
        ]
    return found


# -- its story and picture --


def story_options(saga: Saga) -> list[tuple[str, str]]:
    """The troupe's open stories, as choices. A story given no id yet is
    offered as "#<covenant id>#<index>", given one only when chosen
    (story_from)."""
    found: list[tuple[str, str]] = []
    for story in open_stories.stories(saga):
        entry = story.entry
        value = entry.id or f"#{story.covenant.id}#{story.index}"
        found.append(
            (escape(f"{entry.name or '(unnamed)'} ({story.covenant.name})"), value)
        )
    return found


def story_from(saga: Saga, value: str | None) -> str:
    """The story id a choice of story_options names, given one now if the
    story has none yet; "" for none."""
    if not value:
        return ""
    if not value.startswith("#"):
        return value
    _, covenant_id, index = value.split("#")
    covenant = saga.covenant(covenant_id)
    if covenant is None or not index.isdigit() or int(index) >= len(covenant.diary):
        return ""
    return story_chapters.story_id(covenant.diary[int(index)])


def story_name(saga: Saga, story_id: str) -> str:
    """The name of the story `story_id`, or "" when it is gone."""
    if not story_id:
        return ""
    for covenant in saga.covenants:
        for entry in covenant.diary:
            if entry.id == story_id and story_chapters.is_story(entry):
                return entry.name or "(unnamed)"
    return ""


def picture_options(saga: Saga) -> list[tuple[str, str]]:
    """The saga's maps that have a picture, as choices of the picture."""
    return [(escape(m.name), m.picture) for m in saga.maps if m.picture]


def picture_name(saga: Saga, picture: str) -> str:
    """The map a picture belongs to, by name; the file name if no map."""
    found = next((m for m in saga.maps if m.picture == picture), None)
    return found.name if found is not None else picture


# -- the library --


def uses_of(saga: Saga, scene: Scene) -> list[tuple[Session, SceneUse]]:
    """Every use of `scene`, with the Session it is in."""
    return [(s, u) for s in saga.sessions for u in s.scenes if u.scene_id == scene.id]


def why_not_delete(saga: Saga, scene: Scene, now: Now | None = None) -> str | None:
    """Why `scene` can't be deleted (a Session plays or played it), or None."""
    held = [s for s, u in uses_of(saga, scene) if state(s, u, now) != PREPARED]
    if not held:
        return None
    return (
        f"{scene.title or '(untitled)'} has been played in the Session of "
        f"{ss.when(held[0])}: it stays, to read what happened there."
    )


def delete(saga: Saga, scene: Scene) -> None:
    """Take `scene` out of the library, and its planned uses with it."""
    saga.scenes[:] = [s for s in saga.scenes if s is not scene]
    for session in saga.sessions:
        session.scenes[:] = [u for u in session.scenes if u.scene_id != scene.id]


# -- loading into a Session --

#: The Load a Scene chooser's first choice: make a new Scene there.
NEW_SCENE = "__new__"


def cast_refs(session: Session) -> list[str]:
    """Tonight's cast as actors, each once, in the order cast."""
    return list(
        dict.fromkeys(ref_of(CHARACTERS, c.character_id) for c in session.castings)
    )


def load(saga: Saga, session: Session, scene: Scene) -> SceneUse:
    """Load `scene` into `session`, last: Prepared, with tonight's cast and
    the Scene's regulars present."""
    use = SceneUse(
        id=new_use_id(),
        scene_id=scene.id,
        state=PREPARED,
        present=list(dict.fromkeys([*cast_refs(session), *scene.regulars])),
    )
    keep_names(saga, use)
    session.scenes.append(use)
    return use


def put_after(session: Session, use: SceneUse, after_id: str | None) -> None:
    """Put `use` just after the use `after_id` in `session`'s order
    (""/None: first). An `after_id` no longer there puts it last."""
    rest = [u for u in session.scenes if u is not use]
    if not after_id:
        session.scenes[:] = [use, *rest]
        return
    index = next((i for i, u in enumerate(rest) if u.id == after_id), len(rest) - 1)
    rest.insert(index + 1, use)
    session.scenes[:] = rest


def move_to(use: SceneUse, source: Session, target: Session) -> None:
    """Move `use` from `source` to the end of `target`'s Scenes."""
    if source is target:
        return
    source.scenes[:] = [u for u in source.scenes if u is not use]
    target.scenes.append(use)


def sessions_to_move_to(saga: Saga, session: Session) -> list[Session]:
    """The Sessions a Prepared use of `session` can be in: its own, then
    the other planned ones."""
    return [session, *(s for s in ss.planned(saga) if s is not session)]


# -- as the lists show them --

#: The columns of the library's table and of a Session's Scenes'.
SCENE_COLUMNS = ["Title", "Place", "Aura", "Regulars"]
USE_COLUMNS = ["Scene", "State", "Place", "Present"]


def scene_cells(saga: Saga, scene: Scene) -> list[str]:
    """A Scene's row of the library's table (plain text)."""
    return [
        scene.title or "(untitled)",
        place_text(saga, scene) or "-",
        aura_text(scene),
        ", ".join(actor_names(saga, scene.regulars)) or "-",
    ]


def use_cells(
    saga: Saga, session: Session, use: SceneUse, now: Now | None = None
) -> list[str]:
    """A use's row of a Session's Scenes' table (plain text)."""
    scene = find(saga, use.scene_id)
    return [
        title(saga, use),
        state_label(session, use, now),
        (place_text(saga, scene) if scene is not None else "") or "-",
        ", ".join(actor_names(saga, use.present, use)) or "-",
    ]


def scene_detail(saga: Saga, scene: Scene | None) -> str:
    """The library's details panel (markup) for a chosen Scene."""
    if scene is None:
        return "[dim]Choose a Scene to see it; a adds one.[/]"
    lines = [
        f"[b]{escape(scene.title or '(untitled)')}[/]",
        f"[$label]Place:[/] {escape(place_text(saga, scene) or '(not set)')}",
        f"[$label]Aura:[/] {escape(aura_text(scene))}",
        "[$label]Regulars:[/] "
        + escape(", ".join(actor_names(saga, scene.regulars)) or "no one"),
    ]
    story = story_name(saga, scene.story_id)
    if story:
        lines.append(f"[$label]Story:[/] {escape(story)}")
    if scene.picture:
        lines.append(f"[$label]Picture:[/] {escape(picture_name(saga, scene.picture))}")
    shown = [name_of(saga, r) for r in scene.to_show]
    if shown:
        lines.append(f"[$label]To show:[/] {escape(', '.join(shown))}")
    if scene.notes:
        lines.append(escape(scene.notes))
    lines.append(f"[$label]Used in {len(uses_of(saga, scene))} Session(s).[/]")
    return "\n".join(lines)


def use_row(saga: Saga, session: Session, use: SceneUse, now: Now | None = None) -> str:
    """A use's row (markup): its Scene's title, state and place."""
    scene = find(saga, use.scene_id)
    where = place_text(saga, scene) if scene is not None else ""
    return (
        f"{escape(title(saga, use))}  [dim]{state_label(session, use, now)}"
        + (f" · {escape(where)}" if where else "")
        + "[/]"
    )


def use_detail(
    saga: Saga, session: Session, use: SceneUse | None, now: Now | None = None
) -> str:
    """A Session's Scenes' details panel (markup) for a chosen use: its
    Scene, then who is present this time and the evening's notes."""
    if use is None:
        return "[dim]Choose a Scene to see it; a loads one.[/]"
    scene = find(saga, use.scene_id)
    lines = [scene_detail(saga, scene) if scene else escape(title(saga, use))]
    lines.append(f"[$label]State:[/] {state_label(session, use, now)}")
    lines.append(
        "[$label]Present:[/] "
        + escape(", ".join(actor_names(saga, use.present, use)) or "no one yet")
    )
    if use.notes:
        lines.append(f"[$label]Tonight:[/] {escape(use.notes)}")
    return "\n".join(lines)
