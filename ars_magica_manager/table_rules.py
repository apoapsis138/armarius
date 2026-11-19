"""Who may roll what at a Session: the Table's rules, in one place.

A player rolls only for a character they play tonight; the Session's
storyguide rolls for any character or none; only the storyguide rolls
Blind; a character who can't act rolls nothing. The Chronicle's verbs,
the rolling forms and the sheet's Roll button all ask here, so the rule is
written once.

Pattern: Strategy reduced to plain functions over one table of choices:
each verb asks `why_not_roll_for` and adds only what is its own."""

from __future__ import annotations

from . import viewing
from .models import Character, Saga, Session

#: Who sees a roll: everyone at the Session, its roller and the
#: storyguide, or the storyguide alone (the roller's player is told only
#: that it was rolled).
PUBLIC = "public"
PRIVATE = "private"
BLIND = "blind"
VISIBILITIES = (PUBLIC, PRIVATE, BLIND)


def storyguide_of(session: Session, saga: Saga | None = None) -> str:
    """Who runs `session`, as a person at it: the Player named as its
    storyguide, else the host (the saga's own storyguide). Given the saga,
    a storyguide no longer among its Players counts as none, so a Session
    never waits on someone who can't end it."""
    named = session.storyguide_id
    if named and saga is not None and named not in {p.id for p in saga.players}:
        named = ""
    return named or viewing.HOST


def plays(session: Session, who: str) -> set[str]:
    """The characters `who` plays tonight, by id."""
    return {c.character_id for c in session.castings if c.player_id == who}


def player_of(session: Session, character_id: str) -> str:
    """Who plays `character_id` tonight, or "" for no one."""
    return next(
        (c.player_id for c in session.castings if c.character_id == character_id), ""
    )


def why_not_act(character: Character) -> str | None:
    """Why `character` can take no action now (DE p. 404: Incapacitated;
    an Unconscious or dead character neither), or None."""
    if character.wounds.dead:
        return f"{character.name} is dead."
    if character.wounds.incapacitated:
        return f"{character.name} is Incapacitated: no actions."
    if character.fatigue_level == "unconscious":
        return f"{character.name} is Unconscious."
    return None


def why_not_roll_for(
    saga: Saga,
    session: Session,
    who: str,
    character_id: str,
    visibility: str,
    *,
    for_no_one: bool = False,
) -> str | None:
    """Why `who` may not roll for `character_id` ("" for no one), seen as
    `visibility` says, or None: the who-may rule every roll shares. A
    player rolls for no one only where `for_no_one` allows it (a form's
    roll on a table). Whether the character can act is `why_not_act`'s."""
    if visibility not in VISIBILITIES:
        return "Choose who sees the roll."
    if character_id and character_id not in {c.id for c in saga.characters}:
        return "That character isn't in the saga."
    if who == storyguide_of(session, saga):
        return None
    if visibility == BLIND:
        return "Only the Session's storyguide rolls Blind."
    if not character_id and for_no_one:
        return None
    if character_id not in plays(session, who):
        return "Roll for a character you play tonight."
    return None


def visibility_options(storyguide: bool) -> list[tuple[str, str]]:
    """Who may see a roll, as its roller chooses: Blind for the storyguide
    alone."""
    shown = [
        ("Public: everyone at the Session", PUBLIC),
        ("Private: you and the storyguide", PRIVATE),
    ]
    if storyguide:
        shown.append(("Blind: the number is yours alone", BLIND))
    return shown


def default_visibility(saga: Saga, session: Session, who: str) -> str:
    """Who sees a roll unless its roller says: the storyguide's are Blind,
    a player's Public."""
    return BLIND if who == storyguide_of(session, saga) else PUBLIC
