"""What a Session's own page shows, worked out for either front-end: its
title and line under it (planned, under way or played, and its game
date), and its facts (who storyguides it, who is coming and who is Away,
who plays whom, its notes). The Session's later sections (its Scenes, the
evening's account) are drawn under these."""

from __future__ import annotations

from .. import evening
from .. import sessions as ss
from ..models import Saga, Session
from ..references import Fact


def title(session: Session) -> str:
    return ss.title(session)


def state(session: Session) -> str:
    """Planned, Under way or Played."""
    return "Under way" if session.under_way else ss.status(session)


def subtitle(session: Session) -> str:
    """ "Planned  ·  Spring 1221": its state and game date."""
    return "  ·  ".join(p for p in (state(session), ss.game_date(session)) if p)


def facts(saga: Saga, session: Session) -> list[Fact]:
    """Its facts, each "" when not set: who storyguides it, who is
    coming, who is Away, who plays whom and its notes."""
    coming = [ss.player_name(saga, session, i) for i in session.coming]
    away = [ss.player_name(saga, session, i) for i in session.away]
    attendance = ss.attendance_line(saga, session)
    found = [Fact("Storyguide", ss.storyguide_name(saga, session))]
    if attendance == ss.NOT_RECORDED:
        found.append(Fact("Attendance", ss.NOT_RECORDED))
    else:
        found += [Fact("Coming", ", ".join(coming)), Fact("Away", ", ".join(away))]
    return [
        *found,
        Fact("Who plays whom", ss.castings_line(saga, session)),
        Fact("Notes", session.notes.strip()),
    ]


# -- the evening --

EVENING = "The evening"
#: The headings of what came before the first Scene was set, and after one
#: ended but before the next.
BEFORE_SCENES = "Before the first Scene"
BETWEEN_SCENES = "Between Scenes"
NO_EVENING = "Nothing of this evening is kept for you to read."
#: Before End Session: what the tab says.
NOT_YET = "Kept here when the Session ends."


def shows_evening(session: Session) -> bool:
    """Whether the page has "The evening": a played Session (its account
    is End Session's)."""
    return session.played and not session.under_way


def evening_groups(
    saga: Saga, session: Session, who: str
) -> list[tuple[str, list[str]]]:
    """The evening's account as `who` may read it (evening.for_reader), by
    Scene in order, each time a Scene was set its own group: each one's
    heading (the Scene's title, BEFORE_SCENES or BETWEEN_SCENES, or ""
    when no Scene was set all evening) and its lines."""
    lines = evening.for_reader(saga, session, who)
    any_scene = any(line.play for line in lines)
    groups: list[tuple[str, list[str]]] = []
    last: tuple[int, str] | None = None
    for line in lines:
        if line.scene:
            heading = line.scene
        elif line.play:
            heading = BETWEEN_SCENES
        else:
            heading = BEFORE_SCENES if any_scene else ""
        if (line.play, line.scene) != last:
            groups.append((heading, []))
            last = (line.play, line.scene)
        groups[-1][1].append(line.text)
    return groups
