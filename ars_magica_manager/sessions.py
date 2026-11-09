"""Sessions: the evenings of play at the table, kept on the saga.

A Session holds when it is (a real day, a game season and year, both
optional), whether it has been played, who storyguides it, which Players
are coming and which are Away, and who played whom (a Casting). On any
one evening a character is played by one person at most, though a
character may have several Players and a Player may play several
characters that evening.

A saga is Solo while no Player holds the player role: a Session made then
records no attendance, and shows "Attendance not recorded" if players
join later.

The Steward of a character with no named Players (a pooled grog, even one
everyone in the troupe plays) is kept on its Biographical Detail
(Background.steward_id); `stewarded` lists a Player's.

This module knows only the records; who plays whom (players.py) is asked
by the forms and Needs You, which sit above it, so players.remove can cut
a deleted Player's links through `forget_player`.

Pattern: a plain dataclass (models.Session) with helpers beside it, as
troupe.py keeps The Troupe's."""

from __future__ import annotations

import uuid
from datetime import date

from .markup import escape, fit
from .models import SEASONS, Character, Player, Saga, Session

#: How a Session made while the saga was Solo shows its attendance once
#: the saga has players.
NOT_RECORDED = "Attendance not recorded"

#: The Player role (players.PLAYER), named here so this module needs
#: nothing above the records.
_PLAYER_ROLE = "player"


def new_id() -> str:
    return f"session-{uuid.uuid4().hex[:8]}"


def table_players(saga: Saga) -> list[Player]:
    """The Players in the player role: those whose attendance is asked."""
    return [p for p in saga.players if p.role == _PLAYER_ROLE]


def is_solo(saga: Saga) -> bool:
    """Whether no Player holds the player role (a storyguide's record
    doesn't end it)."""
    return not table_players(saga)


def real_day(session: Session) -> date | None:
    """The Session's real day, or None when it has none (or it can't be
    read as one)."""
    try:
        return date.fromisoformat(session.real_date) if session.real_date else None
    except ValueError:
        return None


def date_problem(text: str) -> str | None:
    """Why `text` can't be a Session's real date ("" may be), or None."""
    if not text.strip():
        return None
    try:
        date.fromisoformat(text.strip())
    except ValueError:
        return "Write the date as year-month-day, such as 2026-11-14."
    return None


def planned(saga: Saga) -> list[Session]:
    """The Sessions not yet played, soonest first: those with a real date
    by date, then the undated in the order they were added."""
    waiting = [s for s in saga.sessions if not s.played]
    dated = sorted(
        (s for s in waiting if real_day(s) is not None),
        key=lambda s: real_day(s) or date.min,
    )
    return dated + [s for s in waiting if real_day(s) is None]


def played(saga: Saga) -> list[Session]:
    """The Sessions played, newest first: dated ones by date, the undated
    after them, the latest added first."""
    done = [s for s in saga.sessions if s.played]
    dated = sorted(
        (s for s in done if real_day(s) is not None),
        key=lambda s: real_day(s) or date.min,
        reverse=True,
    )
    return dated + [s for s in reversed(done) if real_day(s) is None]


def in_order(saga: Saga) -> list[Session]:
    """Every Session as the list shows them: planned (soonest first), then
    played (newest first)."""
    return planned(saga) + played(saga)


def next_planned(saga: Saga) -> Session | None:
    """The next planned Session: the earliest unplayed one."""
    found = planned(saga)
    return found[0] if found else None


def last_played(saga: Saga) -> Session | None:
    found = played(saga)
    return found[0] if found else None


def player_name(saga: Saga, session: Session, player_id: str) -> str:
    """A Player's name: as the saga has it now, else as the Session wrote
    it (a Player since deleted), else "(gone)"."""
    found = next((p for p in saga.players if p.id == player_id), None)
    if found is not None:
        return found.name
    return session.names.get(player_id) or "(gone)"


def storyguide_name(saga: Saga, session: Session) -> str:
    """Who storyguides the Session: a Player, or the saga's own."""
    if session.storyguide_id:
        return player_name(saga, session, session.storyguide_id)
    return saga.storyguide or "The saga's storyguide"


def game_date(session: Session) -> str:
    """ "Spring 1221", "1221", or "" when it has no game date."""
    if session.year is None:
        return ""
    return f"{session.season} {session.year}" if session.season else str(session.year)


def when(session: Session) -> str:
    """The real date, or "No date yet"."""
    day = real_day(session)
    return day.strftime("%d %b %Y").lstrip("0") if day else "No date yet"


def attendance_line(saga: Saga, session: Session) -> str:
    """Who is coming and who is Away (plain text); "" in a Solo saga."""
    if is_solo(saga) and session.solo:
        return ""
    if session.solo:
        return NOT_RECORDED
    coming = [player_name(saga, session, i) for i in session.coming]
    away = [player_name(saga, session, i) for i in session.away]
    parts = []
    if coming:
        parts.append("Coming: " + ", ".join(coming))
    if away:
        parts.append("Away: " + ", ".join(away))
    return "; ".join(parts)


def castings_line(saga: Saga, session: Session) -> str:
    """Who played whom (plain text): "Ana as Aelfric, Ana as Brother Tam"."""
    return ", ".join(
        f"{player_name(saga, session, c.player_id)} as "
        f"{_character_name(saga, c.character_id, c.character_name)}"
        for c in session.castings
    )


def _character_name(saga: Saga, character_id: str, written: str) -> str:
    found = saga.character(character_id)
    return found.name if found is not None else written or "(gone)"


def status(session: Session) -> str:
    return "Played" if session.played else "Planned"


def row_cells(saga: Saga, session: Session) -> list[str]:
    """A Session's row (plain text): its real date, game date, status and
    storyguide."""
    return [
        when(session),
        game_date(session) or "-",
        status(session),
        storyguide_name(saga, session),
    ]


_WHEN_WIDTH = 13
_GAME_WIDTH = 14
_STATUS_WIDTH = 8


def table_header() -> str:
    """The terminal list's column titles (after its two-character marker)."""
    return (
        f"{'Date':<{_WHEN_WIDTH}} {'Game date':<{_GAME_WIDTH}} "
        f"{'Status':<{_STATUS_WIDTH}} Storyguide"
    )


def row_label(saga: Saga, session: Session) -> str:
    """One row (markup), lined up with `table_header`."""
    day, game, state, guide = row_cells(saga, session)
    return (
        f"{escape(fit(day, _WHEN_WIDTH)):<{_WHEN_WIDTH}} "
        f"{escape(fit(game, _GAME_WIDTH)):<{_GAME_WIDTH}} "
        f"{state:<{_STATUS_WIDTH}} {escape(guide)}"
    )


def detail_text(saga: Saga, session: Session | None) -> str:
    """The details panel (markup) for a chosen Session."""
    if session is None:
        return "[dim]Choose a Session to see who came and who played whom.[/]"
    return "\n".join(detail_lines(saga, session))


def detail_lines(saga: Saga, session: Session) -> list[str]:
    """The details panel's lines for a Session (markup)."""
    lines = [
        f"[b]{escape(when(session))}[/] ({status(session)})",
        f"[b]Game date:[/] {escape(game_date(session) or 'None set')}",
        f"[b]Storyguide:[/] {escape(storyguide_name(saga, session))}",
    ]
    attendance = attendance_line(saga, session)
    if attendance:
        lines.append(escape(attendance))
    castings = castings_line(saga, session)
    if castings:
        lines.append(f"[b]Who played whom:[/] {escape(castings)}")
    if session.notes.strip():
        lines.append(escape(session.notes.strip()))
    return lines


def keep_names(saga: Saga, session: Session) -> None:
    """Write every named Player's and character's name into the Session as
    it stands, so it still reads right after either is deleted."""
    ids = {*session.coming, *session.away, session.storyguide_id}
    ids |= {c.player_id for c in session.castings}
    for player in saga.players:
        if player.id in ids:
            session.names[player.id] = player.name
    for casting in session.castings:
        casting.player_name = session.names.get(casting.player_id, "")
        found = saga.character(casting.character_id)
        if found is not None:
            casting.character_name = found.name


# -- Stewards --


def may_have_steward(character: Character) -> bool:
    """Whether a Steward may be set: no Players named on it (one everyone
    in the troupe plays may have one)."""
    return not character.background.player_ids


def steward(saga: Saga, character: Character) -> Player | None:
    """The character's Steward, if it has one and may."""
    if not may_have_steward(character):
        return None
    wanted = character.background.steward_id
    return next((p for p in saga.players if p.id == wanted), None) if wanted else None


def stewarded(saga: Saga, player: Player) -> list[Character]:
    """The characters `player` stewards."""
    return [
        c
        for c in saga.characters
        if c.background.steward_id == player.id and may_have_steward(c)
    ]


def has_current_plan(saga: Saga, character: Character) -> bool:
    """Whether the character has a plan for the saga's current season."""
    return any(
        p.character_id == character.id
        and p.year == saga.current_year
        and p.season == saga.current_season
        for p in saga.season_plans
    )


# -- when a Player or a character goes --


def forget_player(saga: Saga, player_id: str) -> None:
    """Cut a deleted Player's links: from the planned Sessions (coming,
    Away, who played whom, storyguide), and as anyone's Steward. Played
    Sessions keep the name as written."""
    for character in saga.characters:
        if character.background.steward_id == player_id:
            character.background.steward_id = ""
    for session in saga.sessions:
        if session.played:
            continue
        session.coming = [i for i in session.coming if i != player_id]
        session.away = [i for i in session.away if i != player_id]
        session.castings = [c for c in session.castings if c.player_id != player_id]
        if session.storyguide_id == player_id:
            session.storyguide_id = ""
        session.names.pop(player_id, None)


def forget_character(saga: Saga, character_id: str) -> None:
    """Take a deleted character out of the planned Sessions' castings;
    played Sessions keep its name as written."""
    for session in saga.sessions:
        if not session.played:
            session.castings = [
                c for c in session.castings if c.character_id != character_id
            ]


def season_choices() -> list[tuple[str, str]]:
    return [("(none)", ""), *((s, s) for s in SEASONS)]
