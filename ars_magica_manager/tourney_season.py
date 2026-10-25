"""More's Tournament on a character's Reputations: a season on the
tourney circuit, as a knight or as its patron, counted toward his
Prudhomme Reputation and written in the Diary -- no UI in here. The rules
are rules.tournament's and rules.nobility's."""

from __future__ import annotations

from typing import Any

from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, DiaryEntry, Saga, ScoredTrait
from .rules import confidence, nobility, tournament

TITLE = "Tournament"

#: The Reputation choice that starts a new Prudhomme Reputation.
NEW = "new"


def _hosting(values: dict[str, Any]) -> bool:
    return bool(values.get("hosting"))


def tourney_fields(character: Character) -> list[DialogField]:
    """Which Reputation is his Prudhomme, what he did as a knight, what he
    did as patron, and any ransom he left unpaid."""
    reps = character.reputations
    chosen = nobility.prudhomme_index(reps)
    reputation = DialogField(
        "reputation",
        "Prudhomme Reputation",
        "select",
        str(chosen) if chosen is not None else NEW,
        options=[
            *((f"{escape(r.name)} ({r.score:+d})", str(i)) for i, r in enumerate(reps)),
            ("Start one: Prudhomme, Noble (1 if his first Noble Reputation)", NEW),
        ],
        required=True,
        hint="The deeds below are experience points in it (Lords of Men "
        "pp. 25-26, 68).",
    )
    deeds = [
        DialogField(key, f"{label} ({xp} xp)", "check", False)
        for key, (label, xp) in tournament.KNIGHT_DEEDS.items()
    ]
    patron = [
        DialogField(
            "hosting",
            "As patron",
            "select",
            "",
            options=[(label, key) for key, (label, _) in tournament.HOSTING.items()],
            hint="1 experience point, 2 if lavish (Lords of Men p. 69).",
        ),
        DialogField(
            "artist",
            "An artist's record: its aesthetic quality",
            "optint",
            None,
            show_if=_hosting,
            hint="1 more point if it is at least his Prudhomme.",
        ),
        DialogField(
            "patrons",
            "Patrons hosting together",
            "int",
            1,
            show_if=_hosting,
            hint="They share the points equally.",
        ),
    ]
    bad = [(f"{escape(r.name)} ({r.score:+d})", str(i)) for i, r in enumerate(reps)]
    ransom = [
        DialogField("unpaid", "Ransoms he didn't pay", "int", 0),
        DialogField(
            "unpaid_to",
            "Counted toward",
            "select",
            None,
            options=bad,
            allow_blank=True,
            placeholder="(add the bad Reputation first)",
            show_if=lambda v: int(v.get("unpaid") or 0) > 0,
            hint="Each is an experience point toward a fitting bad "
            "Reputation (Lords of Men p. 67).",
        ),
    ]
    return [reputation, *deeds, *patron, *ransom]


def _problem(values: dict[str, Any]) -> str | None:
    if int(values.get("patrons") or 1) < 1:
        return "At least one patron hosts it."
    if int(values.get("unpaid") or 0) < 0:
        return "Ransoms can't be fewer than none."
    return None


def _prudhomme(character: Character, choice: str) -> ScoredTrait:
    """The chosen Reputation, or a new Noble one: at 1 when it is his first
    Noble Reputation, the 1 a man gains entering feudal life (Lords of Men
    p. 25); else at 0, so the season's points aren't counted twice."""
    if choice != NEW:
        return character.reputations[int(choice)]
    first = not any(r.type == nobility.NOBLE for r in character.reputations)
    started = ScoredTrait(nobility.PRUDHOMME, 1 if first else 0, type=nobility.NOBLE)
    character.reputations.append(started)
    return started


def apply_season(saga: Saga, character: Character, values: dict[str, Any]) -> list[str]:
    """Count the season toward his Reputations; the notes, also in the
    Diary."""
    unpaid_to = values.get("unpaid_to")
    unpaid_rep = (
        character.reputations[int(unpaid_to)] if unpaid_to not in (None, "") else None
    )
    rep = _prudhomme(character, str(values.get("reputation") or NEW))
    lines = [] if values.get("reputation") != NEW else [f"Started {rep.name} at 1."]
    done = [k for k in tournament.KNIGHT_DEEDS if values.get(k)]
    as_knight = tournament.knight_xp(done)
    hosting = str(values.get("hosting") or "")
    whole = tournament.patron_xp(hosting, values.get("artist"), rep.score)
    as_patron = tournament.share(whole, int(values.get("patrons") or 1))
    gained = as_knight + as_patron
    before = rep.score
    if gained:
        confidence.add_deeds(rep, gained)
    parts = [f"{as_knight} as a knight"] if done else []
    if hosting:
        parts.append(f"{as_patron} as patron")
    lines.append(
        f"{rep.name}: {gained} experience point(s)"
        + (f" ({'; '.join(parts)})" if parts else "")
        + (
            f", {before:+d} to {rep.score:+d}."
            if rep.score != before
            else f", {rep.deeds} toward the next level."
        )
    )
    unpaid = int(values.get("unpaid") or 0)
    if unpaid > 0 and unpaid_rep is not None:
        was = unpaid_rep.score
        confidence.add_deeds(unpaid_rep, unpaid * tournament.UNPAID_RANSOM_XP)
        lines.append(
            f"{unpaid_rep.name}: {unpaid} unpaid ransom(s), {was:+d} to "
            f"{unpaid_rep.score:+d}."
        )
    lines += _reckoning(character, rep.score)
    character.diary.append(
        DiaryEntry(
            saga.current_year,
            saga.current_season,
            "A season at the tourney",
            "\n".join([*lines, f"Rules: {tournament.SOURCE}"]),
        )
    )
    return notes(*lines)


def _reckoning(character: Character, prudhomme: int) -> list[str]:
    """What his Prudhomme and arms are worth on the circuit."""
    per_season = tournament.labor_per_season(character)
    seasons = tournament.seasons_to_live(character)
    lines = [
        f"As patron he should spend {tournament.patron_spend(prudhomme)} pounds "
        f"on a tournament; a prize for him is worth about "
        f"{tournament.prize_value(prudhomme)}."
    ]
    if seasons is not None:
        lines.append(
            f"On the circuit he makes {per_season} Labor Points a season: "
            f"{seasons} season(s) a year keep an errant knight "
            f"({tournament.LIVING_LABOR} a year)."
        )
    return lines


def tourney_form(saga: Saga, character: Character | None) -> Command:
    if character is None:
        return Refuse(TITLE, "Choose a character first.")
    return Form(
        f"{TITLE}: {escape(character.name)}",
        lambda: tourney_fields(character),
        lambda values: apply_season(saga, character, values),
        validate=_problem,
        help_id="end-of-session",
    )
