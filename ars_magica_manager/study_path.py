"""Study path: how a character reaches a score in an Art or Ability by a
year, season by season, from what is to hand: the books they may read
(their covenant's and their own), vis study for an Art (a magus, with the
pawns), practice for an Ability, and the teachers of their covenant.

Each season still unplanned up to the goal takes whichever source gives
the most experience then, worked out from the character as the path has
left them (a summa only to its Level; a tractatus once; a teacher only to
their own score; a book another character holds that season, never: see
book_holds.py). A vis study's Source Quality is counted at 6 plus the
aura, a stress die's usual worth. A teacher's season is the teacher's
own, so it is suggested, and written for both only when whoever plans
may plan the teacher too; otherwise it becomes an ask (teaching.py).

Pattern: Strategy. Each kind of source answers "what would a season of
you give now?" (SOURCES, a list of functions), and the path takes the
best answer each season."""

from __future__ import annotations

import copy
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from . import book_holds, seat, teaching
from .commands import Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import (
    SEASONS,
    Book,
    Character,
    Saga,
    SeasonPlan,
    XpAllocation,
    next_season,
    season_order,
)
from .rules import activities as rules
from .rules import library, realms, study
from .rules import xp as xp_rules
from .seasons.character_effects import _add_xp
from .seasons.pairs import make_pairs
from .seasons.plans import plan_for, set_plan

#: A vis study's die counted at its usual worth (a stress die's mean, near 6).
VIS_DIE = 6


@dataclass(frozen=True)
class Step:
    """One season of the path: when, what (an activity and its source),
    the experience it gives and the score it leaves. `teacher` is set for a
    season of being taught."""

    season: str
    year: int
    activity: str
    label: str
    xp: int
    score: int
    book_id: str | None = None
    teacher_id: str | None = None


@dataclass
class Path:
    """The path to a goal: the steps, and whether it reaches it."""

    subject: str
    goal: int
    steps: list[Step] = field(default_factory=list)
    reached: bool = False


@dataclass(frozen=True)
class Option:
    """What one source would give this season."""

    activity: str
    label: str
    xp: int
    book_id: str | None = None
    teacher_id: str | None = None


Source = Callable[[Saga, Character, str, str, int, set[str]], list[Option]]


def _is_art(subject: str) -> bool:
    return subject.startswith("art:")


def _name(subject: str) -> str:
    return subject.partition(":")[2]


def score(character: Character, subject: str) -> int:
    name = _name(subject)
    if _is_art(subject):
        art = character.arts.get(name.lower())
        return xp_rules.score_from_xp(art.xp, xp_rules.ART_FACTOR) if art else 0
    found = next((a for a in character.abilities if a.name == name), None)
    return found.level if found is not None else 0


def _books(
    saga: Saga, student: Character, subject: str, season: str, year: int, read: set[str]
) -> list[Option]:
    found = []
    for book in saga.books:
        if not library.can_read(saga, student, book) or book.id in read:
            continue
        if not book_holds.free(saga, book.id, season, year, student.id):
            continue
        result = study.reading(student, book)
        if result is None or result.xp <= 0 or not _about(book, subject):
            continue
        found.append(
            Option(rules.READ, f"reads {book.name}", result.xp, book_id=book.id)
        )
    return found


def _about(book: Book, subject: str) -> bool:
    name = _name(subject)
    if _is_art(subject):
        return book.art.lower() == name.lower()
    return book.ability == name


def _practice(
    _saga: Saga,
    student: Character,
    subject: str,
    _season: str,
    _year: int,
    _read: set[str],
) -> list[Option]:
    if _is_art(subject):
        return []  # The Arts aren't practised (DE p. 377).
    result = study.season_of_study(
        student,
        _name(subject),
        rules.PRACTICE_QUALITY,
        activity="practice",
        is_art=False,
    )
    return [Option(rules.PRACTICE, "practises", result.xp)] if result.xp > 0 else []


def _vis(
    saga: Saga,
    student: Character,
    subject: str,
    _season: str,
    _year: int,
    _read: set[str],
) -> list[Option]:
    if not _is_art(subject) or student.type != "magus":
        return []
    art = _name(subject).lower()
    pawns = study.season_vis_pawns(student, score(student, subject))
    asking = SeasonPlan(student.id, _year, _season, rules.VIS_STUDY)
    held = rules.vis_pool(saga, student, asking).get(art, 0)
    if held < pawns:
        return []
    aura, _realm = realms.home_aura(saga, student)
    result = study.season_of_study(
        student,
        _name(subject).title(),
        VIS_DIE + aura,
        activity="vis_study",
        is_art=True,
    )
    return [Option(rules.VIS_STUDY, f"studies {pawns} pawn(s) of vis", result.xp)]


def _teachers(
    saga: Saga,
    student: Character,
    subject: str,
    season: str,
    year: int,
    _read: set[str],
) -> list[Option]:
    found = []
    mine = score(student, subject)
    for teacher in saga.characters:
        if teacher is student or teacher.covenant_id != student.covenant_id:
            continue
        theirs = score(teacher, subject)
        if theirs <= mine or plan_for(saga, teacher, season, year) is not None:
            continue
        result = study.season_of_study(
            student,
            _name(subject).title() if _is_art(subject) else _name(subject),
            study.teaching_quality(teacher),
            activity="taught",
            is_art=_is_art(subject),
            gain_limit=theirs,
        )
        if result.xp > 0:
            found.append(
                Option(
                    rules.TAUGHT,
                    f"taught by {teacher.name}",
                    result.xp,
                    teacher_id=teacher.id,
                )
            )
    return found


#: Each kind of source, asked every season (Strategy, as a list).
SOURCES: list[Source] = [_books, _vis, _practice, _teachers]


def find(
    saga: Saga, character: Character, subject: str, goal: int, by_year: int
) -> Path:
    """The path to `goal` in `subject` by the end of `by_year`."""
    student = copy.deepcopy(character)
    path = Path(subject, goal)
    read: set[str] = set(student.tractatus_read)
    season, year = saga.current_season, saga.current_year
    end = season_order(season=SEASONS[-1], year=by_year)
    while season_order(season=season, year=year) <= end:
        if score(student, subject) >= goal:
            path.reached = True
            break
        if plan_for(saga, character, season, year) is None:
            options = [
                option
                for source in SOURCES
                for option in source(saga, student, subject, season, year, read)
            ]
            if options:
                best = max(options, key=lambda o: o.xp)
                _add_xp(student, subject, best.xp)
                if best.book_id is not None:
                    found = next(b for b in saga.books if b.id == best.book_id)
                    if found.type == "Tractatus":
                        read.add(found.id)
                path.steps.append(
                    Step(
                        season,
                        year,
                        best.activity,
                        best.label,
                        best.xp,
                        score(student, subject),
                        best.book_id,
                        best.teacher_id,
                    )
                )
        season, year = next_season(season, year)
    path.reached = path.reached or score(student, subject) >= goal
    return path


def plan_of(character: Character, step: Step, subject: str) -> SeasonPlan:
    """The season plan a step writes."""
    allocations = (
        [XpAllocation(subject, rules.PRACTICE_QUALITY)]
        if step.activity == rules.PRACTICE
        else [XpAllocation(subject)]
    )
    return SeasonPlan(
        character.id,
        step.year,
        step.season,
        step.activity,
        [] if step.activity == rules.READ else allocations,
        book_id=step.book_id,
        teacher_id=step.teacher_id,
    )


# -- the form --

TITLE = "Study Path"
HELP_ID = "study-path"


def subject_options(character: Character) -> list[tuple[str, str]]:
    arts = (
        [(a.title(), f"art:{a}") for a in sorted(character.arts)]
        if character.type == "magus"
        else []
    )
    abilities = [
        (a.name, f"ability:{a.name}")
        for a in sorted(character.abilities, key=lambda a: a.name)
    ]
    return arts + abilities


def path_text(saga: Saga, character: Character, path: Path) -> str:
    """The path, a season a line (markup)."""
    label = rules.subject_label(path.subject, {})
    lines = [
        f"{escape(character.name)} reaches {escape(label)} {path.goal}"
        if path.reached
        else f"{escape(character.name)} falls short of {escape(label)} {path.goal}: "
        f"{path.steps[-1].score if path.steps else score(character, path.subject)} "
        "by then, with what is to hand."
    ]
    for step in path.steps:
        mark = " (asks the teacher)" if step.teacher_id else ""
        lines.append(
            f"{step.season} {step.year}: {escape(step.label)}, +{step.xp} xp "
            f"({escape(label)} {step.score}){mark}"
        )
    if not path.steps:
        lines.append("No season left unplanned gives anything towards it.")
    return "\n".join(lines)


def study_path_form(saga: Saga, character: Character) -> Command:
    if not rules.is_planned(character):
        return Refuse(TITLE, f"{escape(character.name)} doesn't plan seasons.")
    options = subject_options(character)
    if not options:
        return Refuse(TITLE, f"{escape(character.name)} has no Art or Ability yet.")

    def fields() -> list[DialogField]:
        return [
            DialogField(
                "subject", "Art or Ability", "select", options[0][1], options=options
            ),
            DialogField("goal", "Score wanted", "int", 5),
            DialogField(
                "by_year",
                "By the end of",
                "int",
                saga.current_year + 3,
                hint="The seasons already planned stay as they are.",
            ),
        ]

    def problem(values: dict[str, Any]) -> str | None:
        if int(values.get("by_year") or 0) < saga.current_year:
            return "Choose this year or a later one."
        return None

    def apply(values: dict[str, Any]) -> Command:
        path = find(
            saga,
            character,
            str(values["subject"]),
            int(values["goal"]),
            int(values["by_year"]),
        )
        return Form(
            TITLE,
            lambda: [
                DialogField("_path", "", "info", path_text(saga, character, path))
            ],
            lambda _values: accept(saga, character, path),
            save_label="Plan These Seasons" if path.steps else "Close",
            help_id=HELP_ID,
        )

    return Form(
        TITLE, fields, apply, validate=problem, save_label="Find", help_id=HELP_ID
    )


def accept(saga: Saga, character: Character, path: Path) -> list[str]:
    """Write the path's seasons: each a plan (a teacher's, with the
    teacher's Teach, when whoever plans may plan the teacher; else an ask
    of the teacher's Player)."""
    planned, asked = 0, 0
    for step in path.steps:
        teacher = saga.character(step.teacher_id) if step.teacher_id else None
        if teacher is not None and not seat.may_plan(saga, teacher):
            teaching.ask(saga, character, teacher, path.subject, step.season, step.year)
            asked += 1
            continue
        plan = plan_of(character, step, path.subject)
        set_plan(saga, plan)
        make_pairs(saga, character, plan)
        planned += 1
    lines = [f"{planned} season{'' if planned == 1 else 's'} planned."]
    if asked:
        lines.append(
            f"{asked} teacher{'' if asked == 1 else 's'} asked: see Teaching Requests."
        )
    return notes(*lines)
