"""Set scene and End scene (the Virtual Tabletop preview): the Session's
storyguide plays one of the Scenes loaded into the Session, from the
host's computer or a Remote seat (scene_play.py).

The Set scene form asks which Scene (one Prepared, or Ended to go back
to it: the next Prepared after the one playing to start with) and whether
to tell the table its aura. End scene asks first, then ends the one
playing.

Where it goes: the Table this copy acts at (host_table.here): the host's
own Chronicle, or the host through a Remote seat's connection.

Pattern: the core Form (a FieldsDialog builder), its apply a Command for
the Table to carry out (Remote Proxy), as the Show form's does; what may
be set is the State's own rule (scenes.MOVES)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .. import (
    chronicle,
    host_table,
    paths,
    references,
    scene_play,
    scenes,
    shows,
    table_rules,
    viewing,
)
from ..at_table import Table
from ..commands import Confirm, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import AtlasMap, Saga, SceneUse, Session
from . import show as show_forms

HELP_ID = "scenes"
SET_TITLE = "Set Scene"
END_TITLE = "End Scene"


def held(
    saga: Saga, session: Session, who: str
) -> tuple[Table, chronicle.HasEntries | None]:
    """The Table this copy acts at, and the Chronicle of `session` it holds
    (None when it holds another Session's: a Remote seat holds only the
    one its host feeds it)."""
    table = host_table.here(saga, session, who)
    book = table.held()
    if isinstance(book, chronicle.SeatChronicle) and book.session_id != session.id:
        book = None
    return table, book


def settable(saga: Saga, session: Session, now: scenes.Now) -> list[SceneUse]:
    """The uses that may be set now: those whose state allows it and whose
    Scene is still in the library, in the evening's order."""
    return [
        u
        for u in session.scenes
        if scenes.why_not_move(scenes.state(session, u, now), scenes.SET) is None
        and scenes.find(saga, u.scene_id) is not None
    ]


def first_choice(session: Session, now: scenes.Now, offered: list[SceneUse]) -> str:
    """The use Set scene starts on: the first Prepared one after the one
    playing (or at all), else the first offered."""
    order = session.scenes
    playing = next(
        (i for i, u in enumerate(order) if now.get(u.id) == scenes.PLAYING), -1
    )
    after = [
        u
        for u in order[playing + 1 :]
        if u in offered and scenes.state(session, u, now) == scenes.PREPARED
    ]
    prepared = [u for u in offered if scenes.state(session, u, now) == scenes.PREPARED]
    found = (after or prepared or offered or [None])[0]
    return found.id if found is not None else ""


def _choice_label(saga: Saga, session: Session, use: SceneUse, now: scenes.Now) -> str:
    scene = scenes.find(saga, use.scene_id)
    where = scenes.place_text(saga, scene) if scene is not None else ""
    label = scenes.title(saga, use) + (f", {where}" if where else "")
    if scenes.state(session, use, now) == scenes.ENDED:
        label += " (played: set it again)"
    return escape(label)


def set_form(
    saga: Saga,
    session: Session,
    who: str,
    table: Table,
    book: chronicle.HasEntries | None,
    preset: str = "",
) -> Form:
    """Set scene by `who` at `session`, handed to `table`; `preset` is the
    use it starts on (else first_choice)."""
    now = scene_play.now(session, book)
    offered = settable(saga, session, now)
    first = preset if any(u.id == preset for u in offered) else ""

    def aura_of(use_id: str) -> str:
        use = next((u for u in session.scenes if u.id == use_id), None)
        scene = scenes.find(saga, use.scene_id) if use is not None else None
        return scenes.aura_text(scene) if scene is not None else "none"

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "scene",
                "Scene",
                "select",
                first or first_choice(session, now, offered),
                options=[(_choice_label(saga, session, u, now), u.id) for u in offered],
                hint="Setting it ends the Scene playing. One already played is "
                "set again as a new banner.",
            ),
            DialogField(
                "tell_aura",
                "Tell the table the aura",
                "check",
                False,
                hint="Unticked, the banner leaves the aura out: only you know it.",
            ),
        ]

    def call(values: dict[str, Any]) -> chronicle.SceneCall:
        return chronicle.SceneCall(
            str(values.get("scene") or ""), tell_aura=bool(values.get("tell_aura"))
        )

    def validate(values: dict[str, Any]) -> str | None:
        return scene_play.why_not_set(saga, session, call(values), who, book)

    def apply(values: dict[str, Any]) -> list[str]:
        refused = table.set_scene(call(values))
        return notes(refused) if refused else []

    return Form(
        SET_TITLE,
        fields,
        apply,
        validate=validate,
        save_label="Set Scene",
        help_id=HELP_ID,
        live=lambda values: escape(
            f"Its aura: {aura_of(str(values.get('scene') or ''))}"
        ),
    )


# -- the Scene playing, as the Chronicle pane's strip shows it --


@dataclass(frozen=True)
class NowPlaying:
    """The Scene playing, as `who` reads it: its title and place from its
    banner, the place's record when they may open it, and for the
    Session's storyguide what its To show list offers (each a name and
    what a Show starts on) and End Scene."""

    title: str
    place: str
    place_link: references.Ref | None = None
    to_show: tuple[tuple[str, show_forms.Showable], ...] = ()
    runs: bool = False


def _place_link(saga: Saga, banner: chronicle.Entry, who: str) -> references.Ref | None:
    found = banner.body.get("place_ref")
    if not isinstance(found, list) or len(found) != 2:
        return None
    record = references.find(saga, str(found[0]), str(found[1]))
    if record is None:
        return None
    if not viewing.readable(chronicle.viewer_of(saga, who), record, saga):
        return None
    return references.Ref(str(found[0]), str(found[1]), record.name)


def _showable(saga: Saga, ref: str) -> tuple[str, show_forms.Showable] | None:
    """A To show entry the Show form can start on: a record with a page to
    copy, or a map's picture."""
    record = scenes.record_of(saga, ref)
    if isinstance(record, AtlasMap):
        return (record.name, (paths.MAPS, record.picture)) if record.picture else None
    if isinstance(record, shows.SHOWABLE):
        name = str(getattr(record, "name", ""))
        kind, _, record_id = ref.partition(":")
        return name, references.Ref(kind, record_id, name)
    return None


def now_playing(
    saga: Saga, session: Session, who: str, book: chronicle.HasEntries | None
) -> NowPlaying | None:
    """The Scene playing at `session`, from `book`'s banners, or None."""
    banner = scene_play.banner_playing(book.entries) if book is not None else None
    if banner is None:
        return None
    runs = table_rules.why_not_lead(saga, session, who, scene_play.ACT) is None
    to_show: list[tuple[str, show_forms.Showable]] = []
    use = next((u for u in session.scenes if u.id == banner.body.get("use")), None)
    scene = scenes.find(saga, use.scene_id) if use is not None else None
    if runs and scene is not None:
        to_show = [f for r in scene.to_show if (f := _showable(saga, r)) is not None]
    return NowPlaying(
        str(banner.body.get("title") or ""),
        str(banner.body.get("place") or ""),
        _place_link(saga, banner, who),
        tuple(to_show),
        runs,
    )


# -- from this copy of the app --


def why_not_set_here(saga: Saga, session: Session) -> str | None:
    """Why whoever uses this copy can't set a Scene at `session` now (not
    its storyguide, not Under way, or nothing loaded to set), or None."""
    who = chronicle.here()
    problem = table_rules.why_not_lead(saga, session, who, scene_play.ACT)
    if problem:
        return problem
    if not session.scenes:
        return "Load a Scene into the Session first."
    if all(scenes.find(saga, u.scene_id) is None for u in session.scenes):
        return "Every Scene loaded has been deleted from the library: load another."
    _table, book = held(saga, session, who)
    if not settable(saga, session, scene_play.now(session, book)):
        return "The only Scene left to set is playing: load another."
    return None


def set_here(saga: Saga, session: Session, preset: str = "") -> Form | Refuse:
    """Set scene by whoever uses this copy, at the Table it acts at."""
    problem = why_not_set_here(saga, session)
    if problem:
        return Refuse(SET_TITLE, escape(problem))
    who = chronicle.here()
    table, book = held(saga, session, who)
    return set_form(saga, session, who, table, book, preset)


def why_not_end_here(saga: Saga, session: Session) -> str | None:
    """Why whoever uses this copy can't end the Scene playing, or None."""
    who = chronicle.here()
    # Asked first, so a Session not Under way never reads its Chronicle.
    problem = table_rules.why_not_lead(saga, session, who, "ends a Scene")
    if problem:
        return problem
    _table, book = held(saga, session, who)
    return scene_play.why_not_end(saga, session, who, book)


def end_here(saga: Saga, session: Session) -> Confirm | Refuse:
    """End scene, asking first: the one playing ends."""
    problem = why_not_end_here(saga, session)
    if problem:
        return Refuse(END_TITLE, escape(problem))
    table, book = held(saga, session, chronicle.here())
    use = scene_play.playing(session, book)
    name = escape(scenes.title(saga, use)) if use is not None else "the Scene"

    def apply() -> list[str]:
        refused = table.end_scene()
        return notes(refused) if refused else []

    return Confirm(
        f"End {name}? The table is told it has ended; it can be set again later.",
        apply,
        yes_label="End Scene",
        title=END_TITLE,
    )
