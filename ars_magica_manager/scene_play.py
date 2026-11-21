"""Setting and ending a Scene at the table (the Virtual Tabletop preview).

While a Session is Under way its storyguide sets one of the Session's
Scenes (scenes.py): a banner posts to the Table with its title, its place
as the players know it, its picture, and its aura only if the storyguide
tells the table. Setting a Scene ends the one playing; End scene ends it;
an Ended one can be set again, a new banner. End Session ends the one
playing and writes each use's state back to the Session.

The Chronicle is where the moves are kept: a Remote seat's verbs reach
the host's Chronicle, never its saga file, so while the Session is Under
way each use's state is the one kept on the Session with the Chronicle's
moves replayed over it (`now`, scenes.replay), and a restart of the app
loses nothing.

Pattern: State (scenes.MOVES decides each move); the banner is a
Protection Proxy, written with only what the players may read: the place
as viewing names it to them, and the aura when told."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from . import chronicle, scenes, table_rules, viewing
from .models import Saga, Scene, SceneUse, Session
from .rules.sites import place

#: What only the Session's storyguide does (table_rules.why_not_lead).
ACT = "sets a Scene"
#: How the banner names a place the players don't know of, with no
#: description typed for it.
UNKNOWN_PLACE = "an unknown place"

#: Each kind of entry that is a move, and the move it is.
_MOVES = {chronicle.SCENE_SET: scenes.SET, chronicle.SCENE_ENDED: scenes.END}


def moves(entries: Iterable[chronicle.Entry]) -> list[tuple[str, str]]:
    """The Scenes' moves `entries` hold, in order: a use's id and the move."""
    return [
        (str(e.body.get("use", "")), _MOVES[e.kind])
        for e in entries
        if e.kind in _MOVES
    ]


def now(session: Session, book: chronicle.HasEntries | None) -> dict[str, str]:
    """Each use's state as `book` (the Session's Chronicle, as this copy
    holds it) has moved it, while the Session is Under way; else empty,
    and the states kept on the uses stand."""
    if not session.under_way or book is None:
        return {}
    return scenes.replay(session, moves(book.entries))


def playing(session: Session, book: chronicle.HasEntries | None) -> SceneUse | None:
    """The use playing now, if any."""
    found = now(session, book)
    return next((u for u in session.scenes if found.get(u.id) == scenes.PLAYING), None)


def banner_playing(entries: Iterable[chronicle.Entry]) -> chronicle.Entry | None:
    """The banner of the Scene playing, from the entries alone: what a
    player's seat, which holds no Scenes, reads it from."""
    found: chronicle.Entry | None = None
    for entry in entries:
        if entry.kind == chronicle.SCENE_SET:
            found = entry
        elif entry.kind == chronicle.END or (
            entry.kind == chronicle.SCENE_ENDED
            and found is not None
            and entry.body.get("use") == found.body.get("use")
        ):
            found = None
    return found


# -- the banner: as the players read it --


def place_for_players(saga: Saga, scene: Scene) -> str:
    """Where `scene` is, as the players know it: a Place or covenant they
    don't know of reads as the description typed for it, or "an unknown
    place"; a known Place by its name alone, never its regio level's,
    which the players may not have found."""
    record = (
        saga.covenant(scene.covenant_id)
        if scene.covenant_id
        else place(saga, scene.place_id)
    )
    if record is None or not viewing.is_known(record):
        return scene.place_name or UNKNOWN_PLACE
    return record.name or UNKNOWN_PLACE


def _known_place(saga: Saga, scene: Scene) -> list[str]:
    """The Place or covenant `scene` is at, as [kind, id], when the
    players know of it (so a banner may link it); else empty."""
    if scene.covenant_id:
        record, kind = saga.covenant(scene.covenant_id), "covenants"
    else:
        record, kind = place(saga, scene.place_id), "neighbours"
    if record is None or not viewing.is_known(record):
        return []
    return [kind, record.id]


def banner(saga: Saga, use: SceneUse, scene: Scene, tell_aura: bool) -> dict[str, Any]:
    """A banner's body: the use, the Scene's title, place (and the record
    it is, when the players know of it) and picture, and its aura only
    when the table is told it."""
    body: dict[str, Any] = {
        "use": use.id,
        "title": scene.title or "(untitled)",
        "place": place_for_players(saga, scene),
    }
    if known := _known_place(saga, scene):
        body["place_ref"] = known
    if scene.picture:
        body["picture"] = scene.picture
    if tell_aura:
        body["aura"] = scenes.aura_text(scene)
        # As numbers too, for the rolls that take it (scene_aura.py).
        body["aura_score"] = scene.aura
        body["aura_realm"] = scene.realm
        body["regio"] = bool(scene.place_id and scene.place_level)
    return body


# -- the verbs --


def why_not_set(
    saga: Saga,
    session: Session,
    call: chronicle.SceneCall,
    who: str,
    book: chronicle.HasEntries | None,
) -> str | None:
    """Why `who` may not set the Scene `call` names, or None: only the
    Session's storyguide, while it is Under way, a use loaded into it whose
    Scene is still in the library, and not the one playing."""
    problem = table_rules.why_not_lead(saga, session, who, ACT)
    if problem:
        return problem
    use = next((u for u in session.scenes if u.id == call.use_id), None)
    if use is None:
        return "That Scene isn't loaded into this Session."
    if scenes.find(saga, use.scene_id) is None:
        return "That Scene has been deleted from the library."
    return scenes.why_not_move(
        scenes.state(session, use, now(session, book)), scenes.SET
    )


def set_scene(
    book: chronicle.Chronicle,
    saga: Saga,
    session: Session,
    call: chronicle.SceneCall,
    *,
    by: str,
) -> chronicle.Entry:
    """Set the Scene `call` names: its banner, to the Table. The one
    playing ends with it (scenes.replay)."""
    book.refresh()
    problem = why_not_set(saga, session, call, by, book)
    if problem:
        raise ValueError(problem)
    use = next(u for u in session.scenes if u.id == call.use_id)
    scene = scenes.find(saga, use.scene_id)
    assert scene is not None
    body = banner(saga, use, scene, call.tell_aura)
    return book.add(chronicle.SCENE_SET, by, chronicle.table(), body)


def why_not_end(
    saga: Saga, session: Session, who: str, book: chronicle.HasEntries | None
) -> str | None:
    """Why `who` may not end the Scene playing, or None."""
    problem = table_rules.why_not_lead(saga, session, who, "ends a Scene")
    if problem:
        return problem
    return None if playing(session, book) is not None else "No Scene is playing."


def end_scene(
    book: chronicle.Chronicle, saga: Saga, session: Session, *, by: str
) -> chronicle.Entry:
    """End the Scene playing, saying so to the Table."""
    book.refresh()
    problem = why_not_end(saga, session, by, book)
    if problem:
        raise ValueError(problem)
    use = playing(session, book)
    assert use is not None
    body = {"use": use.id, "title": scenes.title(saga, use)}
    return book.add(chronicle.SCENE_ENDED, by, chronicle.table(), body)


def end_session(saga: Saga, session: Session, *, by: str) -> chronicle.Chronicle:
    """End Session (chronicle.end), ending the Scene playing first, then
    keeping each use's state on it: the Chronicle's moves are done."""
    problem = chronicle.why_not_end(session, by, saga)
    if problem:
        raise ValueError(problem)
    book = chronicle.read(saga, session)
    book.refresh()
    if playing(session, book) is not None:
        end_scene(book, saga, session, by=by)
    states = now(session, book)
    chronicle.end(saga, session, by=by)
    for use in session.scenes:
        use.state = states.get(use.id, use.state)
    return book
