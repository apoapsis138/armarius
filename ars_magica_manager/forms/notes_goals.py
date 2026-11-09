"""A character's Notes & Goals: the player's own notes, and the goals they
set the character, on the Personality tab (the desktop's Description).

Who reads them is viewing.reads_private's to say: the character's players,
its Steward and its storyguide. A goal ticked "Share with the troupe" is
read by anyone who reads the character; nothing else of the section is,
nor that it exists (seat_view.py takes them out of a Remote seat's data and
of an export too). A goal may name an Art or Ability, a score and a year
("Creo 15 by 1230"): Plan the Study Path then opens filled in from it.

The list's first row is the notes, for those who read them; the goals
follow. Pattern: a commands.SectionOps, as every list, with a Form for
each kind of row; the reading rule stays in the Protection Proxy
(viewing.py)."""

from __future__ import annotations

from typing import Any

from .. import storage, study_path, viewing
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField
from ..markup import escape, fit, markdown_text
from ..models import Character, PlayerGoal, Saga
from ..rules import activities as rules
from ..sections import NOTES_SECTION

SECTION = NOTES_SECTION
TITLE = "Notes & Goals"
NOTES_ROW = "Private notes"
PLAN_TITLE = study_path.TITLE

_TEXT_WIDTH = 46


def private(saga: Saga, character: Character) -> bool:
    """Whether whoever is looking reads the notes and every goal."""
    return viewing.reads_private(viewing.current(), character, saga)


def goals_shown(saga: Saga, character: Character) -> list[PlayerGoal]:
    """The goals whoever is looking reads: all, or the shared ones."""
    if private(saga, character):
        return list(character.goals)
    return [g for g in character.goals if g.shared]


def shown(saga: Saga, character: Character) -> bool:
    """Whether the section shows at all: on a character a player plays or
    stewards (or one with notes or goals already), to those who read the
    notes, and to anyone else only while a goal is shared."""
    if any(g.shared for g in character.goals):
        return True
    played = viewing.troupes_own(character) and (
        bool(character.background.player_ids)
        or character.background.everyone_plays
        or bool(character.background.steward_id)
    )
    return private(saga, character) and (
        played or bool(character.private_notes) or bool(character.goals)
    )


def title(saga: Saga, character: Character) -> str:
    return f"{TITLE} ({len(goals_shown(saga, character))})"


def subject_label(subject: str) -> str:
    """ "Creo", "Magic Theory"; "" for none."""
    kind, _, name = subject.partition(":")
    return name.title() if kind == "art" else name


def aim_text(goal: PlayerGoal) -> str:
    """ "Creo 15 by 1230", "" for a goal with no score to reach."""
    if not goal.subject or goal.score <= 0:
        return ""
    by = f" by {goal.by_year}" if goal.by_year else ""
    return f"{subject_label(goal.subject)} {goal.score}{by}"


def _goal_line(goal: PlayerGoal) -> str:
    aim = aim_text(goal)
    mark = "shared" if goal.shared else "private"
    words = fit(goal.text, _TEXT_WIDTH)
    return f"{escape(words):<{_TEXT_WIDTH}}  {escape(aim)}  [$label]{mark}[/]".rstrip()


def rows(saga: Saga, character: Character) -> list[tuple[int | None, str]]:
    """The list: the notes (for those who read them), then each goal."""
    found: list[tuple[int | None, str]] = []
    if private(saga, character):
        found.append((0, f"[b]{NOTES_ROW}[/]  [$label]{escape(_lead(character))}[/]"))
    offset = len(found)
    found += [
        (offset + i, _goal_line(g)) for i, g in enumerate(goals_shown(saga, character))
    ]
    return found


def _lead(character: Character) -> str:
    """The notes' first line, without its emphasis marks, for a list."""
    first = character.private_notes.strip().splitlines()
    return fit(first[0].replace("*", ""), _TEXT_WIDTH) if first else "(none yet)"


def table_rows(saga: Saga, character: Character) -> list[list[str]]:
    """The list as a table's rows (markup): what, the score aimed at, and
    who reads it; the row numbers are `rows`'."""
    found: list[list[str]] = []
    if private(saga, character):
        found.append([f"[b]{NOTES_ROW}[/]: {escape(_lead(character))}", "", "private"])
    found += [
        [
            escape(goal.text),
            escape(aim_text(goal)),
            "the troupe" if goal.shared else "private",
        ]
        for goal in goals_shown(saga, character)
    ]
    return found


def text(saga: Saga, character: Character) -> str:
    """The notes in full and every goal (markup), for the section's text."""
    parts: list[str] = []
    if private(saga, character):
        words = character.private_notes.strip()
        parts.append(
            f"[b]{NOTES_ROW}[/]\n"
            + (markdown_text(words) if words else "[$label](none yet)[/]")
        )
    for goal in goals_shown(saga, character):
        aim = aim_text(goal)
        head = f"[b]{escape(goal.text)}[/]"
        tail = f"  [$label]{escape(aim)}[/]" if aim else ""
        state = "shared with the troupe" if goal.shared else "private"
        parts.append(f"{head}{tail}\n[$label]{state}[/]")
    if not parts:
        return "[$label]No goals yet.[/]"
    return "\n\n".join(parts)


# -- the forms --


def notes_form(character: Character) -> Form:
    def apply(values: dict[str, Any]) -> None:
        character.private_notes = str(values.get("notes") or "")

    return Form(
        f"{NOTES_ROW} of {escape(character.name)}",
        lambda: [
            DialogField(
                "notes",
                "Notes",
                "area",
                character.private_notes,
                hint="Only you (and any other player of the character), its "
                "Steward and its storyguide read these.",
            )
        ],
        apply,
        help_id=SECTION,
    )


def goal_fields(character: Character, goal: PlayerGoal | None) -> list[DialogField]:
    options = study_path.subject_options(character)
    return [
        DialogField(
            "text",
            "Goal",
            "text",
            goal.text if goal is not None else "",
            required=True,
            placeholder="e.g. Become the covenant's finest enchanter",
        ),
        DialogField(
            "shared",
            "Share with the troupe",
            "check",
            goal.shared if goal is not None else False,
            hint="Unticked: only those who read your notes read it.",
        ),
        DialogField(
            "subject",
            "Art or Ability",
            "select",
            (goal.subject or None) if goal is not None else None,
            options=options,
            allow_blank=True,
            hint="For a score to reach: Plan the Study Path opens from it.",
        ),
        DialogField(
            "score",
            "Score",
            "int",
            goal.score if goal is not None else 0,
            show_if=lambda values: bool(values.get("subject")),
        ),
        DialogField(
            "by_year",
            "By the end of",
            "int",
            goal.by_year if goal is not None else None,
            show_if=lambda values: bool(values.get("subject")),
        ),
    ]


def goal_problem(values: dict[str, Any]) -> str | None:
    if values.get("subject") and int(values.get("score") or 0) <= 0:
        return "Give the score to reach, or no Art or Ability."
    return None


def goal_form(character: Character, goal: PlayerGoal | None) -> Form:
    def apply(values: dict[str, Any]) -> None:
        subject = str(values.get("subject") or "")
        year = values.get("by_year")
        changed = {
            "text": str(values["text"]).strip(),
            "shared": bool(values.get("shared")),
            "subject": subject,
            "score": int(values.get("score") or 0) if subject else 0,
            "by_year": int(year) if subject and year else None,
        }
        if goal is None:
            character.goals.append(
                PlayerGoal(
                    id=storage.generate_unique_id(
                        changed["text"] or "goal", [g.id for g in character.goals]
                    ),
                    **changed,
                )
            )
        else:
            for key, value in changed.items():
                setattr(goal, key, value)

    verb = "New Goal" if goal is None else "Edit Goal"
    return Form(
        f"{verb} for {escape(character.name)}",
        lambda: goal_fields(character, goal),
        apply,
        validate=goal_problem,
        help_id=SECTION,
    )


def _goal_at(saga: Saga, character: Character, row: int) -> PlayerGoal | None:
    """The goal a row of the list shows (None: the notes' row)."""
    index = row - (1 if private(saga, character) else 0)
    found = goals_shown(saga, character)
    return found[index] if 0 <= index < len(found) else None


def delete_goal(character: Character, goal: PlayerGoal) -> Confirm:
    def apply() -> None:
        character.goals.remove(goal)

    return Confirm(f"Delete the goal {escape(goal.text)}?", apply)


def ops(saga: Saga, character: Character) -> dict[str, SectionOps]:
    """Notes & Goals' Add (a goal), Edit (the notes or a goal) and Delete
    (a goal)."""

    def edit(row: int) -> Command:
        goal = _goal_at(saga, character, row)
        return notes_form(character) if goal is None else goal_form(character, goal)

    def remove(row: int) -> Command:
        goal = _goal_at(saga, character, row)
        if goal is None:
            return Refuse(TITLE, "Edit the notes to clear them.")
        return delete_goal(character, goal)

    return {
        SECTION: SectionOps(
            add=lambda: goal_form(character, None),
            edit=edit,
            remove=remove,
            rows=lambda: [label for _i, label in rows(saga, character)],
        )
    }


# -- Plan the Study Path from a goal --


def plans(saga: Saga, character: Character, row: int | None) -> bool:
    """Whether Plan the Study Path applies to the goal at `row`: one that
    names an Art or Ability and a score, on a character who plans seasons."""
    if row is None:
        return False
    goal = _goal_at(saga, character, row)
    return goal is not None and bool(aim_text(goal)) and rules.is_planned(character)


def plan_form(saga: Saga, character: Character, row: int | None) -> Command:
    """Plan the Study Path, filled in from the goal at `row`."""
    goal = _goal_at(saga, character, row) if row is not None else None
    if goal is None or not aim_text(goal):
        return Refuse(PLAN_TITLE, "Choose a goal with an Art or Ability and a score.")
    return study_path.study_path_form(
        saga,
        character,
        subject=goal.subject,
        goal=goal.score,
        by_year=goal.by_year,
    )
