"""Holding a Tribunal: the meeting being held, kept on its Tribunal
(Tribunal.meeting) and saved after every step, so leaving it and holding
it again later resumes at the step in hand.

The steps run in a fixed order (Template Method: `Step` is the template,
each kind of step fills in its form and what it works out): the
Opening, Attendance and proxies, each case and motion on the day it is
heard, the package's own steps (the Theban elections), Rulings and
fines, Treasury and vis, and the Closing, which writes the meeting into
the Tribunal's Diary and ends it. A package can add a step, never
reorder the rest.

The record is a plain dict, so a save holds it as it is:
{"year", "season", "place", "days", "done": [step keys held],
"day_of": {case id: day}, "attendance": {covenant id: {"absent",
"proxies", "ruling"}}, "notes": {step key: words}}."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import tribunal_packages, tribunal_sheet, tribunals, world
from .character_sheet import Fact
from .commands import Command, Confirm, Form, Refuse, SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    CASE_DECIDED,
    CASE_OPEN,
    Case,
    Covenant,
    Saga,
    Tribunal,
    TribunalDiaryEntry,
)
from .sections import ATTENDANCE_SECTION, BUSINESS_SECTION

#: How many days a meeting lasts unless the storyguide says otherwise.
DEFAULT_DAYS = 3

#: What the Presiding Quaesitor rules on a covenant's proxies.
ALLOWED = "Allowed"
SET_ASIDE = "Set aside"
RULINGS = (ALLOWED, SET_ASIDE)

_ORDINALS = (
    "First",
    "Second",
    "Third",
    "Fourth",
    "Fifth",
    "Sixth",
    "Seventh",
    "Eighth",
    "Ninth",
    "Tenth",
)


def day_name(day: int) -> str:
    """ "The Second Day"."""
    if 1 <= day <= len(_ORDINALS):
        return f"The {_ORDINALS[day - 1]} Day"
    return f"Day {day}"


def _begin(saga: Saga, tribunal: Tribunal) -> dict[str, Any]:
    """A new meeting record: when the Tribunal is due to meet (or now),
    where, and its cases spread over the days but the last."""
    meeting: dict[str, Any] = {
        "year": tribunal.next_year
        if tribunal.next_year is not None
        else saga.current_year,
        "season": tribunal.next_season or saga.current_season,
        "place": tribunal.meeting_place.strip(),
        "days": DEFAULT_DAYS,
        "done": [],
        "day_of": {},
        "attendance": {},
        "notes": {},
    }
    meeting["day_of"] = _spread(business(tribunal), DEFAULT_DAYS)
    return meeting


def _spread(cases: list[Case], days: int) -> dict[str, int]:
    """Each case's day: spread in docket order over every day but the
    last, which is kept for the rulings and the closing."""
    open_days = max(1, days - 1)
    count = max(1, len(cases))
    return {c.id: 1 + i * open_days // count for i, c in enumerate(cases)}


def business(tribunal: Tribunal) -> list[Case]:
    """The cases and motions the meeting hears: those still open."""
    return [c for c in tribunal.cases if c.status == CASE_OPEN]


def days(meeting: dict[str, Any]) -> int:
    return max(1, int(meeting.get("days") or DEFAULT_DAYS))


def day_of(meeting: dict[str, Any], case: Case) -> int:
    """The day `case` is heard: as the Opening set it, else the first."""
    day = meeting.get("day_of", {}).get(case.id, 1)
    return max(1, min(days(meeting), int(day)))


# -- attendance --


def _attendance(meeting: dict[str, Any], covenant: Covenant) -> dict[str, Any]:
    return meeting.get("attendance", {}).get(covenant.id, {})


def absent(meeting: dict[str, Any], covenant: Covenant) -> int:
    return int(_attendance(meeting, covenant).get("absent") or 0)


def carried(tribunal: Tribunal, meeting: dict[str, Any], covenant: Covenant) -> int:
    """The proxies `covenant` carries into the hall: as attendance
    recorded them, else as the Tribunal's roster holds them."""
    entry = _attendance(meeting, covenant)
    if "proxies" in entry:
        return int(entry.get("proxies") or 0)
    return tribunal_sheet.proxies(tribunal, covenant)


def ruling(meeting: dict[str, Any], covenant: Covenant) -> str:
    return _attendance(meeting, covenant).get("ruling") or ALLOWED


def present(
    saga: Saga, tribunal: Tribunal, meeting: dict[str, Any], covenant: Covenant
) -> tuple[int, int]:
    """`covenant`'s votes in the hall: its magi present, and the proxies
    it carries that the Quaesitor allowed."""
    magi = max(0, world.votes(saga, covenant) - absent(meeting, covenant))
    proxies = carried(tribunal, meeting, covenant)
    allowed = proxies if ruling(meeting, covenant) == ALLOWED else 0
    return magi, allowed


def hall(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> tuple[int, int]:
    """Every vote in the hall, and how many of them are proxies."""
    magi = proxies = 0
    for covenant in tribunals.covenants_of(saga, tribunal):
        m, p = present(saga, tribunal, meeting, covenant)
        magi += m
        proxies += p
    return magi + proxies, proxies


def present_text(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
    """ "23 votes, 3 by proxy"."""
    votes, proxies = hall(saga, tribunal, meeting)
    words = f"{votes} vote{'' if votes == 1 else 's'}"
    return f"{words}, {proxies} by proxy" if proxies else words


# -- the steps (Template Method) --


@dataclass
class Step:
    """One step of the order of business: its key in the record, what the
    list calls it and the day it is held. `fields`, `apply` and `text`
    are the parts each kind fills in; holding a step (`hold`) is the
    same for all: its form, then the step marked held and the record
    saved with the saga."""

    key: str
    title: str
    day: int

    def fields(
        self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]
    ) -> list[DialogField]:
        return [_note_field(meeting, self.key)]

    def validate(self, meeting: dict[str, Any], values: dict[str, Any]) -> str | None:
        return None

    def apply(
        self,
        saga: Saga,
        tribunal: Tribunal,
        meeting: dict[str, Any],
        values: dict[str, Any],
    ) -> None:
        _keep_note(meeting, self.key, values)

    def text(self, saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
        return _note_text(meeting, self.key)

    def save_label(self) -> str:
        return "Hold"


def _note_field(meeting: dict[str, Any], key: str) -> DialogField:
    return DialogField(
        "note",
        "Note",
        "area",
        meeting.get("notes", {}).get(key, ""),
        hint="Anything said or decided at this step, in your own words.",
    )


def _keep_note(meeting: dict[str, Any], key: str, values: dict[str, Any]) -> None:
    note = (values.get("note") or "").strip()
    notes = meeting.setdefault("notes", {})
    if note:
        notes[key] = note
    else:
        notes.pop(key, None)


def _note_text(meeting: dict[str, Any], key: str) -> str:
    note = meeting.get("notes", {}).get(key, "")
    return f"[$label]Note:[/] {escape(note)}" if note else ""


def _join(*parts: str) -> str:
    return "\n".join(p for p in parts if p)


class Opening(Step):
    """The day count, where it is held, and the day each case is heard."""

    def fields(self, saga, tribunal, meeting):
        cases = business(tribunal)
        found = [
            DialogField(
                "place",
                "Held at",
                "text",
                meeting.get("place", ""),
                placeholder=tribunal.meeting_place.strip() or "a covenant",
            ),
            DialogField(
                "days",
                "Days",
                "int",
                days(meeting),
                required=True,
                hint="How long the meeting lasts; the last day is kept for "
                "the rulings and the closing.",
            ),
        ]
        if cases:
            found.append(DialogField("days_note", "", "info", "The day each is heard:"))
        found += [
            DialogField(
                f"day_{c.id}", c.title, "int", day_of(meeting, c), required=True
            )
            for c in cases
        ]
        return found

    def validate(self, meeting, values):
        count = values.get("days") or 0
        if count < 1:
            return "A meeting lasts at least a day."
        for key, value in values.items():
            if key.startswith("day_") and not 1 <= (value or 0) <= count:
                return f"Each case is heard on a day from 1 to {count}."
        return None

    def apply(self, saga, tribunal, meeting, values):
        meeting["place"] = values.get("place", "")
        meeting["days"] = values["days"]
        meeting["day_of"] = {
            key.removeprefix("day_"): value
            for key, value in values.items()
            if key.startswith("day_")
        }

    def text(self, saga, tribunal, meeting):
        roll = ", ".join(c.name for c in tribunals.covenants_of(saga, tribunal))
        return _join(
            f"[$label]Held at:[/] {escape(meeting.get('place') or '(not set)')}",
            f"[$label]Days:[/] {days(meeting)}",
            f"[$label]The roll of covenants:[/] {escape(roll or '(none recorded)')}",
        )

    def save_label(self):
        return "Open"


class Attendance(Step):
    """Who is absent and the proxies each covenant carries, with the
    Presiding Quaesitor's ruling on them."""

    def fields(self, saga, tribunal, meeting):
        found: list[DialogField] = []
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            magi = world.votes(saga, covenant)
            name = covenant.name
            found += [
                DialogField(
                    f"absent_{cid}",
                    f"{name}: absent",
                    "int",
                    absent(meeting, covenant),
                    hint=f"Of its {magi} {'magus' if magi == 1 else 'magi'}.",
                ),
                DialogField(
                    f"proxies_{cid}",
                    f"{name}: proxies",
                    "int",
                    carried(tribunal, meeting, covenant),
                    hint="The sigils it carries for magi not in the hall.",
                ),
                DialogField(
                    f"ruling_{cid}",
                    f"{name}: Quaesitor",
                    "select",
                    ruling(meeting, covenant),
                    options=pairs(RULINGS),
                    required=True,
                    hint="Whether the Presiding Quaesitor allows its proxies.",
                    show_if=lambda v, cid=cid: (v.get(f"proxies_{cid}") or 0) > 0,
                ),
            ]
        if not found:
            found.append(
                DialogField(
                    "none", "", "info", "No covenant belongs to this Tribunal yet."
                )
            )
        return found

    def validate(self, meeting, values):
        if any(
            (v or 0) < 0
            for k, v in values.items()
            if k.startswith(("absent_", "proxies_"))
        ):
            return "Absent magi and proxies can't be fewer than none."
        return None

    def apply(self, saga, tribunal, meeting, values):
        attendance = meeting.setdefault("attendance", {})
        for covenant in tribunals.covenants_of(saga, tribunal):
            cid = covenant.id
            proxies = values.get(f"proxies_{cid}") or 0
            attendance[cid] = {
                "absent": min(
                    values.get(f"absent_{cid}") or 0, world.votes(saga, covenant)
                ),
                "proxies": proxies,
                "ruling": values.get(f"ruling_{cid}") or ALLOWED,
            }
            if proxies:
                tribunal.proxies[cid] = proxies
            else:
                tribunal.proxies.pop(cid, None)

    def text(self, saga, tribunal, meeting):
        return f"[$label]Present:[/] {escape(present_text(saga, tribunal, meeting))}"


class Hearing(Step):
    """A charge or appeal (prosecutor and defender) or a motion (one who
    speaks for it), chosen from the case's own."""

    def __init__(self, case: Case, day: int) -> None:
        motion = case.kind == "motion"
        title = f"Motion: {case.title}" if motion else case.title
        super().__init__(f"case:{case.id}", title, day)
        self.case = case

    def fields(self, saga, tribunal, meeting):
        case = self.case
        motion = case.kind == "motion"
        found = [
            DialogField(
                "prosecutor",
                "Speaks for it" if motion else "Prosecutor",
                "text",
                case.prosecutor or case.brought_by,
            )
        ]
        if not motion:
            found.append(
                DialogField(
                    "defender", "Defender", "text", case.defender or case.against
                )
            )
        return [*found, _note_field(meeting, self.key)]

    def apply(self, saga, tribunal, meeting, values):
        self.case.prosecutor = values.get("prosecutor", "")
        if "defender" in values:
            self.case.defender = values.get("defender", "")
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        # The details panel names the step: the case's own heading goes.
        lines = tribunal_sheet.case_text(saga, tribunal, self.case).split("\n")
        return _join(*lines[1:], _note_text(meeting, self.key))


class Elections(Step):
    """The Tribunal's offices, each given a holder and a term (only when
    its customs have offices: the Theban archai)."""

    def _offices(self, tribunal: Tribunal) -> list[dict[str, Any]]:
        return tribunal_packages.entries(tribunal, tribunal.package, "archai")

    def fields(self, saga, tribunal, meeting):
        offices = self._offices(tribunal)
        magi = [
            (m.name, m.id)
            for c in tribunals.covenants_of(saga, tribunal)
            for m in world.covenant_magi(saga, c)
        ]
        found: list[DialogField] = []
        for index, office in enumerate(offices):
            found += [
                DialogField(
                    f"holder_{index}",
                    office.get("office") or "(an office)",
                    "select",
                    office.get("holder_id"),
                    options=magi,
                    allow_blank=True,
                ),
                DialogField(
                    f"term_{index}", "Term ends", "optint", office.get("term_ends")
                ),
            ]
        if not offices:
            found.append(
                DialogField(
                    "none", "", "info", "No offices recorded: add them on its tab."
                )
            )
        return [*found, _note_field(meeting, self.key)]

    def apply(self, saga, tribunal, meeting, values):
        for index, office in enumerate(self._offices(tribunal)):
            if f"holder_{index}" in values:
                office["holder_id"] = values[f"holder_{index}"]
                office["term_ends"] = values.get(f"term_{index}")
        _keep_note(meeting, self.key, values)


class Rulings(Step):
    """The ruling on each case heard (the words the Tribunal decided)."""

    def fields(self, saga, tribunal, meeting):
        cases = business(tribunal)
        found = [
            DialogField(f"outcome_{c.id}", c.title, "text", c.outcome) for c in cases
        ]
        if not cases:
            found.append(DialogField("none", "", "info", "No case was heard."))
        return [*found, _note_field(meeting, self.key)]

    def apply(self, saga, tribunal, meeting, values):
        for case in business(tribunal):
            if f"outcome_{case.id}" in values:
                case.outcome = values[f"outcome_{case.id}"]
        _keep_note(meeting, self.key, values)

    def text(self, saga, tribunal, meeting):
        lines = [
            f"[b]{escape(c.title)}:[/] {escape(c.outcome or '(no ruling yet)')}"
            for c in business(tribunal)
        ]
        return _join(*lines, _note_text(meeting, self.key))


class Treasury(Step):
    """The treasury as it stands, and the loans that fall due this year."""

    def _due(self, tribunal: Tribunal, meeting: dict[str, Any]) -> list[str]:
        year = meeting.get("year")
        return [
            f"{e.who or 'a loan'}: {tribunal_sheet.amount_text(e)}"
            for e in tribunal.treasury
            if e.kind == "loan" and not e.paid and e.due_year == year
        ]

    def fields(self, saga, tribunal, meeting):
        found = [
            DialogField("balance", "", "info", f"{label}: {words}")
            for label, words in tribunal_sheet.balance_lines(tribunal)
        ]
        due = self._due(tribunal, meeting)
        if due:
            found.append(DialogField("due", "", "info", "Loans due: " + "; ".join(due)))
        return [*found, _note_field(meeting, self.key)]

    def text(self, saga, tribunal, meeting):
        balance = [
            f"[$label]{escape(label)}:[/] {escape(words)}"
            for label, words in tribunal_sheet.balance_lines(tribunal)
        ]
        due = self._due(tribunal, meeting)
        return _join(
            *balance,
            f"[$label]Loans due:[/] {escape('; '.join(due))}" if due else "",
            _note_text(meeting, self.key),
        )


class Closing(Step):
    """Ends the meeting: each case with a ruling is decided, the meeting
    goes into the Diary, and the next one is set."""

    def fields(self, saga, tribunal, meeting):
        return [
            DialogField("what", "", "info", closing_text(saga, tribunal, meeting)),
            _note_field(meeting, self.key),
        ]

    def text(self, saga, tribunal, meeting):
        return escape(closing_text(saga, tribunal, meeting))

    def save_label(self):
        return "Close"


def _next(tribunal: Tribunal, meeting: dict[str, Any]) -> int:
    return int(meeting.get("year") or 0) + max(1, tribunal.meets_every)


def closing_text(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> str:
    """What closing the meeting does."""
    decided = sum(bool(c.outcome.strip()) for c in business(tribunal))
    words = f"{decided} case{'' if decided == 1 else 's'}"
    return (
        f"Closing ends the meeting: {words} with a ruling are decided, it "
        f"goes into the Diary, and the next meeting is set for "
        f"{meeting.get('season', 'Summer')} {_next(tribunal, meeting)}."
    )


#: The package steps the core knows how to hold, by name.
_PACKAGE_STEPS = {"elections": ("Elections", Elections)}


def steps(tribunal: Tribunal, meeting: dict[str, Any]) -> list[Step]:
    """The order of business, in the order it is held."""
    last = days(meeting)
    found: list[Step] = [
        Opening("opening", "Opening and the oaths", 1),
        Attendance("attendance", "Attendance and proxies", 1),
    ]
    cases = sorted(business(tribunal), key=lambda c: day_of(meeting, c))
    found += [Hearing(c, day_of(meeting, c)) for c in cases]
    for name in tribunal_packages.of(tribunal).meeting_steps:
        title, kind = _PACKAGE_STEPS.get(name, (name.title(), Step))
        found.append(kind(name, title, last))
    found += [
        Rulings("rulings", "Rulings and fines", last),
        Treasury("treasury", "Treasury and vis", last),
        Closing("closing", "Closing", last),
    ]
    return found


def held(meeting: dict[str, Any], step: Step) -> bool:
    return step.key in meeting.get("done", [])


def current(tribunal: Tribunal, meeting: dict[str, Any]) -> Step:
    """The step in hand: the first not yet held."""
    found = steps(tribunal, meeting)
    return next((s for s in found if not held(meeting, s)), found[-1])


def now_text(tribunal: Tribunal, meeting: dict[str, Any]) -> str:
    """ "The Second Day › Fengheld v. Arnhaven"."""
    step = current(tribunal, meeting)
    return f"{day_name(step.day)} › {step.title}"


# -- holding a step --


def _close(saga: Saga, tribunal: Tribunal, meeting: dict[str, Any]) -> None:
    heard = business(tribunal)
    for case in heard:
        if case.outcome.strip():
            case.status = CASE_DECIDED
    lines = [s.title for s in steps(tribunal, meeting) if held(meeting, s)]
    place = meeting.get("place") or ""
    tribunal.diary.append(
        TribunalDiaryEntry(
            int(meeting.get("year") or saga.current_year),
            meeting.get("season", ""),
            f"The Tribunal met at {place}" if place else "The Tribunal met",
            "; ".join(lines),
        )
    )
    tribunal.next_year = _next(tribunal, meeting)
    tribunal.next_season = meeting.get("season") or tribunal.next_season
    tribunal.meeting = None


def step_form(
    saga: Saga,
    tribunal: Tribunal,
    step: Step,
    meeting: dict[str, Any] | None = None,
) -> Form:
    """Hold `step` of the meeting being held (or of `meeting`, a new one
    its Opening begins): its form; on saving it the step is marked held
    and the Closing ends the meeting."""
    record = meeting if meeting is not None else tribunal.meeting
    assert record is not None

    def apply(values: dict[str, Any]) -> None:
        tribunal.meeting = record
        step.apply(saga, tribunal, record, values)
        done = record.setdefault("done", [])
        if step.key not in done:
            done.append(step.key)
        if isinstance(step, Closing):
            _close(saga, tribunal, record)

    heading = (
        f"Hold Tribunal: {tribunals.title(tribunal)}"
        if meeting is not None
        else f"{day_name(step.day)}: {step.title}"
    )
    return Form(
        heading,
        lambda: step.fields(saga, tribunal, record),
        apply,
        validate=lambda values: step.validate(record, values),
        save_label=step.save_label(),
        help_id="hold-tribunal",
    )


def hold(saga: Saga, tribunal: Tribunal) -> Command:
    """Hold Tribunal: the step in hand, or (with no meeting being held)
    a new meeting's Opening; cancelling that holds none."""
    if tribunal.meeting is not None:
        return step_form(saga, tribunal, current(tribunal, tribunal.meeting))
    meeting = _begin(saga, tribunal)
    return step_form(saga, tribunal, steps(tribunal, meeting)[0], meeting)


# -- what the hall shows --


def record(saga: Saga, tribunal: Tribunal) -> dict[str, Any]:
    """The meeting being held, or the one Hold Tribunal would open (not
    kept): what the hall shows before it opens."""
    return tribunal.meeting if tribunal.meeting is not None else _begin(saga, tribunal)


def title(saga: Saga, tribunal: Tribunal) -> str:
    """ "The Meeting: Summer 1228", or "The Next Meeting: Summer 1228"."""
    meeting = record(saga, tribunal)
    words = "The Meeting" if tribunal.meeting is not None else "The Next Meeting"
    return f"{words}: {meeting.get('season', '')} {meeting.get('year', '')}"


def facts(saga: Saga, tribunal: Tribunal) -> list[Fact]:
    """Where it is held, the step in hand and the votes in the hall."""
    meeting = record(saga, tribunal)
    held_at = meeting.get("place") or "(not set)"
    if tribunal.meeting is None:
        return [
            Fact("Held at", held_at),
            Fact("Now", "Not yet opened: hold any step (e) to open it"),
        ]
    return [
        Fact("Held at", held_at),
        Fact("Now", now_text(tribunal, meeting)),
        Fact("Present", present_text(saga, tribunal, meeting)),
    ]


def business_title(saga: Saga, tribunal: Tribunal) -> str:
    count = days(record(saga, tribunal))
    return f"Order of Business ({count} day{'' if count == 1 else 's'})"


def business_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each step and its day (named on the day's first step): held ✓,
    the one in hand ▶, the rest to come."""
    meeting = record(saga, tribunal)
    found = steps(tribunal, meeting)
    now = current(tribunal, meeting).key if tribunal.meeting is not None else None
    rows: list[list[str]] = []
    styles: dict[tuple[int, int], str] = {}
    shown_day = 0
    for index, step in enumerate(found):
        if held(meeting, step):
            mark = "✓ held"
        elif step.key == now:
            mark = "▶ in hand"
            for column in range(3):
                styles[(index, column)] = "b"
        else:
            mark = ""
        day = day_name(step.day) if step.day != shown_day else ""
        rows.append([step.title, day, mark])
        shown_day = step.day
    return Grid(
        ["Step", "Day", ""],
        rows,
        list(range(len(rows))),
        "",
        styles,
        caps=[44, 17, 9],
    )


def attendance_title(saga: Saga, tribunal: Tribunal) -> str:
    votes, _ = hall(saga, tribunal, record(saga, tribunal))
    return f"Attendance ({votes} vote{'' if votes == 1 else 's'} in the hall)"


def attendance_grid(saga: Saga, tribunal: Tribunal) -> Grid:
    """Each covenant's magi, those absent, the proxies it carries and the
    votes it has in the hall."""
    meeting = record(saga, tribunal)
    rows = []
    for covenant in tribunals.covenants_of(saga, tribunal):
        proxies = carried(tribunal, meeting, covenant)
        magi, allowed = present(saga, tribunal, meeting, covenant)
        set_aside = proxies and ruling(meeting, covenant) == SET_ASIDE
        rows.append(
            [
                covenant.name,
                str(world.votes(saga, covenant)),
                str(absent(meeting, covenant) or ""),
                f"{proxies} (set aside)" if set_aside else str(proxies or ""),
                str(magi + allowed),
            ]
        )
    return Grid(
        ["Covenant", "Magi", "Absent", "Proxies", "Votes"],
        rows,
        list(range(len(rows))),
        "No covenant belongs to this Tribunal yet.",
        caps=[22, 4, 6, 13, 5],
    )


def step_text(saga: Saga, tribunal: Tribunal, index: int | None) -> str:
    """The details panel: the chosen step, what was entered at it and
    what it worked out."""
    meeting = record(saga, tribunal)
    found = steps(tribunal, meeting)
    if index is None or index >= len(found):
        return "[$label]Choose a step to read what was entered at it.[/]"
    step = found[index]
    if tribunal.meeting is None:
        state = "the meeting is not yet open"
    else:
        state = "held" if held(meeting, step) else "to come"
    heading = f"[b]{escape(step.title)}[/]  {day_name(step.day)}, {state}"
    body = step.text(saga, tribunal, meeting) if tribunal.meeting is not None else ""
    return _join(heading, body or "[$label]Hold it with Edit (e).[/]")


def business_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """Edit holds the chosen step (again, if it was held; with no meeting
    open, the Opening); Delete abandons the meeting, keeping what its
    steps changed."""

    def edit(row: int) -> Command:
        if tribunal.meeting is None:
            return hold(saga, tribunal)
        found = steps(tribunal, tribunal.meeting)
        return step_form(saga, tribunal, found[min(row, len(found) - 1)])

    def remove(_row: int) -> Command:
        if tribunal.meeting is None:
            return Refuse("Abandon", "No meeting is being held.")

        def apply() -> None:
            tribunal.meeting = None

        return Confirm(
            "Abandon this meeting? What its steps changed stays as it is.",
            apply,
            yes_label="Abandon",
        )

    return SectionOps(
        edit=edit,
        remove=remove,
        rows=lambda: [s.title for s in steps(tribunal, record(saga, tribunal))],
    )


def attendance_ops(saga: Saga, tribunal: Tribunal) -> SectionOps:
    """Edit holds Attendance and proxies (opening the meeting first if
    it isn't open)."""

    def edit(_row: int) -> Command:
        if tribunal.meeting is None:
            return hold(saga, tribunal)
        return step_form(saga, tribunal, steps(tribunal, tribunal.meeting)[1])

    return SectionOps(
        edit=edit,
        rows=lambda: [c.name for c in tribunals.covenants_of(saga, tribunal)],
    )


def ops(saga: Saga, tribunal: Tribunal) -> dict[str, SectionOps]:
    """The hall's sections the core edits, by id."""
    return {
        BUSINESS_SECTION: business_ops(saga, tribunal),
        ATTENDANCE_SECTION: attendance_ops(saga, tribunal),
    }
