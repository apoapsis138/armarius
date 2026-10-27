"""More's War's End on a Tribunal's docket: how a Wizard's War on it came
out, and what it earns. The war leaves the docket, kept among the past
rulings with its outcome; a magus of the saga who keeps House Acclaim
earns it for winning (twice the foe's highest Reputation) and for having
fought bravely (1 to 3), as House Flambeau's table gives them (HoH:
Societates p. 31); both magi's Diaries, and the Tribunal's, record it.

Pattern: a commands.Form over the case, as Withdraw is; the Acclaim goes
through rules.acclaim's own apply.
"""

from __future__ import annotations

from typing import Any

from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import (
    CASE_DECIDED,
    Case,
    Character,
    DiaryEntry,
    Saga,
    Tribunal,
    TribunalDiaryEntry,
)
from ..rules import acclaim as ac
from ..rules import hermetic_law
from ..sheets import tribunal as tribunal_sheet
from . import acclaim as acclaim_forms

TITLE = "War's End"
HELP_ID = "wars-end"
SOURCE = (
    "Ars Magica Definitive Edition, Wizard's War, p. 21; Houses of Hermes: "
    "Societates, House Acclaim, p. 31"
)
#: How a war ends, by key: what it says.
OUTCOMES: dict[str, str] = {
    "ran_out": "The month of war ran out, both alive",
    "declarer_won": "The declarer slew his foe",
    "foe_won": "The foe slew the declarer",
    "peace": "They made peace before it was fought",
}


def _named(saga: Saga, name: str) -> Character | None:
    wanted = name.strip().casefold()
    return next((c for c in saga.characters if c.name.casefold() == wanted), None)


def _highest(character: Character | None) -> int:
    return max((r.score for r in character.reputations), default=0) if character else 0


def fields(saga: Saga, case: Case) -> list[DialogField]:
    declarer, foe = _named(saga, case.brought_by), _named(saga, case.against)
    found = [
        DialogField(
            "outcome",
            "How it ended",
            "select",
            "ran_out",
            options=[(label, key) for key, label in OUTCOMES.items()],
        ),
        DialogField(
            "account",
            "What happened",
            "area",
            "",
            hint="A line or two for the record: the blows struck, who was hurt.",
        ),
    ]
    for key, who, other in (("declarer", declarer, foe), ("foe", foe, declarer)):
        if who is None or not _keeps_flambeau_acclaim(who):
            continue
        found += [
            DialogField(
                f"{key}_brave",
                f"{escape(who.name)} fought bravely (Acclaim, 1 to 3; 0 for none)",
                "int",
                0,
            ),
            DialogField(
                f"{key}_foe_reputation",
                "His foe's highest Reputation (for a win: twice it)",
                "int",
                _highest(other),
            ),
        ]
    return found


def _keeps_flambeau_acclaim(who: Character | None) -> bool:
    """Whether his House Acclaim follows House Flambeau's table, which
    rewards a Wizard's War."""
    return who is not None and acclaim_forms.offers_flambeau(who)


def _winner_key(outcome: str) -> str:
    return {"declarer_won": "declarer", "foe_won": "foe"}.get(outcome, "")


def _acclaim(who: Character, points: int, why: str) -> str:
    held = ac.acclaim_of(who) or ac.start(who, ac.house_of(who) or ac.FLAMBEAU)
    change = ac.apply(who, held, points)
    return (
        f"{who.name}: {why} {points:+d}, House Acclaim {change.before} to "
        f"{change.after}."
    )


def apply(
    saga: Saga, tribunal: Tribunal, case: Case, values: dict[str, Any]
) -> list[str]:
    outcome = str(values.get("outcome") or "ran_out")
    said = OUTCOMES[outcome]
    account = str(values.get("account") or "").strip()
    case.status = CASE_DECIDED
    case.outcome = said + (f": {account}" if account else "")
    lines = [f"{case.title}: {said}."]
    people = {
        "declarer": _named(saga, case.brought_by),
        "foe": _named(saga, case.against),
    }
    winner = _winner_key(outcome)
    for key, who in people.items():
        if who is None or not _keeps_flambeau_acclaim(who):
            continue
        brave = max(0, min(3, int(values.get(f"{key}_brave") or 0)))
        if brave:
            lines.append(_acclaim(who, brave, "fought bravely"))
        if key == winner:
            won = ac.worth(
                ac.DEEDS["won_war"], int(values.get(f"{key}_foe_reputation") or 0)
            )
            if won:
                lines.append(_acclaim(who, won, "won the war"))
    for who in people.values():
        if who is not None:
            who.diary.append(
                DiaryEntry(
                    saga.current_year,
                    saga.current_season,
                    f"{TITLE}: {case.title}",
                    "\n".join(
                        [*lines, *([account] if account else []), f"Rules: {SOURCE}"]
                    ),
                )
            )
    tribunal.diary.append(
        TribunalDiaryEntry(
            saga.current_year,
            saga.current_season,
            f"{TITLE}: {case.title}",
            " ".join(lines),
        )
    )
    return notes(*map(escape, lines))


def end_form(saga: Saga, tribunal: Tribunal, index: int) -> Command:
    pending = tribunal_sheet.open_cases(tribunal)
    if not 0 <= index < len(pending) or pending[index].kind != hermetic_law.WAR:
        return Refuse(TITLE, "Choose a Wizard's War on the docket first.")
    case = pending[index]
    return Form(
        f"{TITLE}: {escape(case.title)}",
        lambda: fields(saga, case),
        lambda values: apply(saga, tribunal, case, values),
        help_id=HELP_ID,
    )


def is_war(tribunal: Tribunal, index: int) -> bool:
    """Whether the docket's row `index` is a Wizard's War."""
    pending = tribunal_sheet.open_cases(tribunal)
    return 0 <= index < len(pending) and pending[index].kind == hermetic_law.WAR
