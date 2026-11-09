"""Teaching requests: a student asking another Player's character to teach
them in a season.

Being taught takes the teacher's season too (seasons.pairs writes the
teacher's Teach). When the student's Player doesn't play or steward the
teacher (and isn't a storyguide), the student's plan can't write the
teacher's season, so it becomes an ask instead: the student's season
shows "Waiting for Bruno", the teacher's Player sees it on the teacher's
page (More's Teaching Requests) and on The Troupe, and Accept writes both
plans; Decline clears it with a note to the student. Storyguides see open
asks on Needs You.

Pattern: State. A request is Asked, then Accepted (it becomes the two
plans and goes) or Declined (kept, with its note, until the student
clears it)."""

from __future__ import annotations

import uuid

from .commands import Choice, Choose, Command, Form, Refuse, notes
from .form_spec import DialogField
from .markup import escape
from .models import Character, Saga, SeasonPlan, TeachRequest, XpAllocation
from .rules import activities as rules
from .seasons.pairs import make_pairs
from .seasons.plans import plan_for, set_plan, waiting_text

ASKED, DECLINED = "asked", "declined"
TITLE = "Teaching Requests"
HELP_ID = "teaching-requests"


def subject_name(subject: str) -> str:
    return rules.subject_label(subject, {})


def ask(
    saga: Saga,
    student: Character,
    teacher: Character,
    subject: str,
    season: str,
    year: int,
) -> TeachRequest:
    """Ask `teacher` to teach `student` `subject` that season."""
    request = TeachRequest(
        f"teach-{uuid.uuid4().hex[:8]}",
        student.id,
        teacher.id,
        subject,
        season,
        year,
    )
    saga.teach_requests.append(request)
    return request


def asked_of(saga: Saga, character: Character) -> list[TeachRequest]:
    """The open asks to `character` to teach."""
    return [
        r
        for r in saga.teach_requests
        if r.teacher_id == character.id and r.status == ASKED
    ]


def asked_by(saga: Saga, character: Character) -> list[TeachRequest]:
    """`character`'s own asks, open or declined."""
    return [r for r in saga.teach_requests if r.student_id == character.id]


def waiting(saga: Saga, character: Character, season: str, year: int) -> str:
    """ "Waiting for Bruno to teach Latin." for the student's season, or ""."""
    return waiting_text(saga, character, season, year)


def line(saga: Saga, request: TeachRequest) -> str:
    """ "Aelfric asks Bruno to teach Latin, Summer 1222" (plain text)."""
    student = saga.character(request.student_id)
    teacher = saga.character(request.teacher_id)
    return (
        f"{student.name if student else '(gone)'} asks "
        f"{teacher.name if teacher else '(gone)'} to teach "
        f"{subject_name(request.subject)}, {request.season} {request.year}"
    )


def accept(saga: Saga, request: TeachRequest) -> list[str]:
    """Write the student's Taught plan, and with it the teacher's Teach
    (seasons.pairs); the ask goes."""
    student = saga.character(request.student_id)
    teacher = saga.character(request.teacher_id)
    if student is None or teacher is None:
        saga.teach_requests.remove(request)
        return notes("One of them is gone: the ask is cleared.")
    plan = SeasonPlan(
        student.id,
        request.year,
        request.season,
        rules.TAUGHT,
        [XpAllocation(request.subject)],
        teacher_id=teacher.id,
    )
    set_plan(saga, plan)
    make_pairs(saga, student, plan)
    saga.teach_requests.remove(request)
    return notes(
        escape(
            f"{teacher.name} teaches {student.name} in {request.season} {request.year}."
        )
    )


def decline(saga: Saga, request: TeachRequest, note: str) -> list[str]:
    request.status = DECLINED
    request.note = note.strip()
    return notes("Declined: the student is told.")


def busy(saga: Saga, teacher: Character, season: str, year: int) -> str | None:
    """Why the teacher can't take the season, or None."""
    plan = plan_for(saga, teacher, season, year)
    if plan is not None:
        return f"{teacher.name}'s {season} {year} is already planned."
    return None


def requests_command(saga: Saga, character: Character) -> Command:
    """More's Teaching Requests on a character: the asks to teach them
    (Accept or Decline) and their own (Clear)."""
    to_me = asked_of(saga, character)
    mine = asked_by(saga, character)
    if not to_me and not mine:
        return Refuse(TITLE, f"No one has asked {escape(character.name)} to teach.")

    def choices() -> list[Choice]:
        return [
            *(Choice(escape(line(saga, r)), ("answer", r.id)) for r in to_me),
            *(
                Choice(
                    escape(line(saga, r))
                    + (" (declined)" if r.status == DECLINED else " (waiting)"),
                    ("clear", r.id),
                )
                for r in mine
            ),
        ]

    def chosen(value: tuple[str, str]) -> Command | list[str]:
        what, request_id = value
        request = next((r for r in saga.teach_requests if r.id == request_id), None)
        if request is None:
            return notes("That ask is gone.")
        if what == "clear":
            saga.teach_requests.remove(request)
            return notes("The ask is cleared.")
        return _answer(saga, request)

    return Choose(TITLE, choices, chosen, help_id=HELP_ID)


ACCEPT, DECLINE = "accept", "decline"


def _answer(saga: Saga, request: TeachRequest) -> Form:
    teacher = saga.character(request.teacher_id)

    def problem(values: dict[str, object]) -> str | None:
        if values.get("answer") == ACCEPT and teacher is not None:
            return busy(saga, teacher, request.season, request.year)
        return None

    def apply(values: dict[str, object]) -> list[str]:
        if values.get("answer") == ACCEPT:
            return accept(saga, request)
        return decline(saga, request, str(values.get("note") or ""))

    return Form(
        escape(line(saga, request)),
        lambda: [
            DialogField(
                "answer",
                "Answer",
                "select",
                ACCEPT,
                options=[("Accept: plan both seasons", ACCEPT), ("Decline", DECLINE)],
            ),
            DialogField(
                "note",
                "Note to the student",
                "text",
                "",
                show_if=lambda v: v.get("answer") == DECLINE,
            ),
        ],
        apply,
        validate=problem,
        help_id=HELP_ID,
    )
