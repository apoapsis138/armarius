"""The Sessions list's forms, independent of how they are drawn: Add,
Edit and Delete a Session (sessions.py).

A Session is entered in two steps. The first asks when it is (a real day,
a game season and year), whether it has been played, who storyguides it
and, unless the saga is Solo, whether each Player is coming or Away. The
second asks who played whom: one "Played by" choice per character, so a
character has one person at most that evening while a Player may play
several. It comes prefilled from who usually plays whom: a character is
given to its Player when exactly one of its Players is coming, and left
for the storyguide to choose when two or more are (a shared character,
or one everyone in the troupe plays).

Pattern: the core Form, chained (the first step's apply returns the
second), with Add, Edit and Delete as one commands.SectionOps."""

from __future__ import annotations

from typing import Any

from .. import cast_sheet, recap, story_aftermath, viewing, what_changed
from .. import players as pl
from .. import sessions as ss
from ..commands import Confirm, Form, SectionOps, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import Casting, Character, Player, Saga, Session
from ..seasons import defaults

#: The keys of a Player's attendance choice and a character's "Played by"
#: choice, before the Player's or character's id.
ATTEND = "attend_"
PLAYED_BY = "played_by_"

COMING, AWAY = "coming", "away"
ATTENDANCE = [("Coming", COMING), ("Away", AWAY)]

SESSIONS_HELP = "tab-content-sessions"


def title(existing: Session | None) -> str:
    if existing is None:
        return "Add a Session"
    return f"Edit the Session of {escape(ss.when(existing))}"


def storyguide_options(saga: Saga) -> list[tuple[str, str]]:
    """Any Player may storyguide an evening; blank is the saga's own."""
    own = saga.storyguide or "the saga's storyguide"
    return [(f"(the saga's own: {escape(own)})", "")] + [
        (escape(p.name), p.id) for p in saga.players
    ]


def first_fields(saga: Saga, existing: Session | None) -> list[DialogField]:
    """When the Session is, whether it was played, who storyguides it and,
    unless Solo, who is coming."""
    fields = [
        DialogField(
            "real_date",
            "Date",
            "text",
            existing.real_date if existing else "",
            placeholder="2026-11-14",
            hint="The real day you meet, year-month-day; blank if not set yet.",
        ),
        DialogField(
            "played",
            "Played",
            "check",
            existing.played if existing else False,
            hint="Tick once the evening has been played.",
        ),
        DialogField(
            "season",
            "Game season",
            "select",
            existing.season if existing else "",
            options=ss.season_choices(),
        ),
        DialogField(
            "year",
            "Game year",
            "optint",
            existing.year if existing else None,
            hint="The game date it is set in, if any; it may span seasons.",
        ),
        DialogField(
            "storyguide_id",
            "Storyguide",
            "select",
            existing.storyguide_id if existing else "",
            options=storyguide_options(saga),
        ),
    ]
    if not ss.is_solo(saga) and not (existing is not None and existing.solo):
        fields.extend(_attendance_fields(saga, existing))
    fields.append(
        DialogField("notes", "Notes", "area", existing.notes if existing else "")
    )
    return fields


def _attendance_fields(saga: Saga, existing: Session | None) -> list[DialogField]:
    def now(player: Player) -> str:
        if existing is not None and player.id in existing.away:
            return AWAY
        return COMING

    return [
        DialogField(
            f"{ATTEND}{p.id}",
            escape(p.name),
            "select",
            now(p),
            options=ATTENDANCE,
        )
        for p in ss.table_players(saga)
    ]


def first_problem(values: dict[str, Any]) -> str | None:
    return ss.date_problem(values.get("real_date") or "")


def _coming(saga: Saga, values: dict[str, Any], solo: bool) -> list[str]:
    if solo:
        return []
    return [
        p.id
        for p in ss.table_players(saga)
        if values.get(f"{ATTEND}{p.id}", COMING) == COMING
    ]


# -- who played whom --


def cast_candidates(saga: Saga, coming: list[str]) -> list[Character]:
    """The characters the second step offers: those a coming Player plays
    first, then the rest of the troupe's characters and those with a
    Steward, in the saga's order."""
    troupe = {c.id for c in pl.troupe_characters(saga)}
    offered = [
        c
        for c in saga.characters
        if c.id in troupe or c.background.steward_id or c.background.everyone_plays
    ]
    present = [p for p in saga.players if p.id in coming]

    def theirs(character: Character) -> bool:
        return any(pl.plays(character.background, p) for p in present)

    return [c for c in offered if theirs(c)] + [c for c in offered if not theirs(c)]


def prefilled(saga: Saga, character: Character, coming: list[str]) -> str:
    """Who plays `character` this evening before anyone chooses: its one
    coming Player, or "" when none or several of its Players are coming."""
    players = [
        p for p in saga.players if p.id in coming and pl.plays(character.background, p)
    ]
    return players[0].id if len(players) == 1 else ""


def cast_fields(
    saga: Saga, existing: Session | None, coming: list[str]
) -> list[DialogField]:
    """One "Played by" choice per character: one of the Players coming, or
    no one."""
    people = [p for p in saga.players if p.id in coming]
    options = [("(not played)", "")] + [(escape(p.name), p.id) for p in people]
    cast = {c.character_id: c.player_id for c in existing.castings} if existing else {}
    return [
        DialogField(
            f"{PLAYED_BY}{c.id}",
            escape(c.name),
            "select",
            cast[c.id]
            if c.id in cast and cast[c.id] in {p.id for p in people}
            else prefilled(saga, c, coming),
            options=options,
        )
        for c in cast_candidates(saga, coming)
    ]


def _castings(saga: Saga, values: dict[str, Any]) -> list[Casting]:
    found = []
    for character in saga.characters:
        who = values.get(f"{PLAYED_BY}{character.id}") or ""
        if who:
            found.append(Casting(player_id=who, character_id=character.id))
    return found


def session_form(saga: Saga, existing: Session | None) -> Form:
    """Add (None) or Edit a Session: the first step, whose Next goes on to
    who played whom when a Player is coming (Solo, or with no one coming,
    it saves straight away)."""

    def apply(values: dict[str, Any]) -> Form | list[str]:
        solo = existing.solo if existing is not None else ss.is_solo(saga)
        coming = _coming(saga, values, solo)
        if solo or not (coming and cast_candidates(saga, coming)):
            return _store(saga, existing, values, coming, solo, None)
        return Form(
            "Who Played Whom",
            lambda: cast_fields(saga, existing, coming),
            lambda cast: _store(saga, existing, values, coming, solo, cast),
            help_id=SESSIONS_HELP,
        )

    return Form(
        title(existing),
        lambda: first_fields(saga, existing),
        apply,
        validate=first_problem,
        save_label="Save"
        if (existing.solo if existing is not None else ss.is_solo(saga))
        else "Next",
        help_id=SESSIONS_HELP,
    )


def _store(
    saga: Saga,
    existing: Session | None,
    values: dict[str, Any],
    coming: list[str],
    solo: bool,
    cast: dict[str, Any] | None,
) -> list[str]:
    session = existing or Session(id=ss.new_id(), solo=solo)
    was_played = existing is not None and existing.played
    session.real_date = (values.get("real_date") or "").strip()
    session.played = bool(values.get("played"))
    session.season = values.get("season") or ""
    session.year = values.get("year")
    session.storyguide_id = values.get("storyguide_id") or ""
    session.notes = values.get("notes") or ""
    if not solo:
        session.coming = coming
        session.away = [p.id for p in ss.table_players(saga) if p.id not in coming]
    session.castings = _castings(saga, cast) if cast is not None else []
    ss.keep_names(saga, session)
    if existing is None:
        saga.sessions.append(session)
    _keep_copies(saga, session)
    if session.played and not was_played:
        return _unclosed(saga, session)
    return []


def _unclosed(saga: Saga, session: Session) -> list[str]:
    """A reminder of the Session's chapters whose aftermath is not yet
    asked (Close the Chapter, on Needs You)."""
    names = [
        entry.name or "(unnamed)"
        for _covenant, entry in story_aftermath.open_chapters(saga)
        if entry.session_id == session.id
    ]
    if not names:
        return []
    return notes(
        escape(
            "Chapters played this evening are not closed yet: "
            + ", ".join(names)
            + ". Close each from Needs You, to give the cast their Adventure."
        )
    )


#: How many played Sessions keep a copy of the player characters.
KEPT_COPIES = 2


def _keep_copies(saga: Saga, session: Session) -> None:
    """A Session newly marked Played keeps the player characters as they
    stand (what_changed.keep); unticked, it drops its copy. Only the latest
    KEPT_COPIES played Sessions keep theirs."""
    if not session.played:
        session.kept = {}
        session.played_season, session.played_year = "", None
    elif not session.kept:
        session.played_season = saga.current_season
        session.played_year = saga.current_year
        played = [c for c in saga.characters if defaults.is_player_character(c)]
        session.kept = what_changed.keep_all(saga, played)
    keeping = {s.id for s in ss.played(saga)[:KEPT_COPIES]}
    for other in saga.sessions:
        if other.id not in keeping:
            other.kept = {}


def since_last_session(saga: Saga, character: Character) -> Form:
    """What changed in `character` since the last played Session that kept
    a copy of them, shown to read (Close only)."""
    found = next((s for s in ss.played(saga) if character.id in s.kept), None)
    if found is None:
        words = (
            "No played Session has a copy of them yet: one is kept when a "
            "Session is marked Played."
        )
    else:
        words = (
            f"Since the Session of {ss.when(found)}: "
            f"{what_changed.text(saga, found.kept[character.id], character)}"
        )
    return Form(
        f"What Changed: {escape(character.name)}",
        lambda: [DialogField("_changed", "", "info", escape(words))],
        lambda _values: None,
        save_label="Close",
        help_id=SESSIONS_HELP,
    )


def delete_session(saga: Saga, session: Session) -> Confirm:
    def apply() -> None:
        saga.sessions.remove(session)

    return Confirm(f"Delete the Session of {escape(ss.when(session))}?", apply)


def session_ops(saga: Saga) -> SectionOps:
    """Add, Edit and Delete for the Sessions, in the order the list shows
    them (planned soonest first, then played newest first)."""
    return SectionOps(
        add=lambda: session_form(saga, None),
        edit=lambda index: session_form(saga, ss.in_order(saga)[index]),
        remove=lambda index: delete_session(saga, ss.in_order(saga)[index]),
        rows=lambda: [ss.when(s) for s in ss.in_order(saga)],
    )


def cast_glance(saga: Saga, session: Session) -> Form:
    """The cast at a glance for a Session (cast_sheet.py), to read."""
    cast = cast_sheet.session_cast(saga, session.id)
    return Form(
        f"The Cast: {escape(ss.when(session))}",
        lambda: [DialogField("_cast", "", "info", cast_sheet.text(saga, cast))],
        lambda _values: None,
        save_label="Close",
        help_id="cast-glance",
    )


def previously_on(saga: Saga) -> Form:
    """Previously On (recap.py), to read aloud: as the Player view for
    anyone but a storyguide."""
    players = not viewing.current().is_storyguide
    return Form(
        recap.TITLE,
        lambda: [DialogField("_recap", "", "info", recap.text(saga, players))],
        lambda _values: None,
        save_label="Close",
        help_id="previously-on",
    )
