"""What a Session's own page shows, worked out for either front-end: its
title and line under it (planned, under way or played, and its game
date), and its facts (who storyguides it, who is coming and who is Away,
who plays whom, its notes). The Session's later sections (its Scenes, the
evening's account) are drawn under these."""

from __future__ import annotations

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
