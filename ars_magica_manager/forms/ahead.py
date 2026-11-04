"""Ahead's forms: how far it looks and what it shows (the Seasons top
panel's Edit), and the storyguide's own calendar entries (Add, Edit and
Delete on the Looking Ahead list). A row Ahead worked out from another
record is changed on that record, so Edit and Delete refuse it."""

from __future__ import annotations

from typing import Any

from .. import ahead, attention, world_turns
from ..commands import Command, Confirm, Form, Refuse, SectionOps
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import EVERY, ONCE, REPEATS, SEASONS, CalendarEntry, Covenant, Saga
from ..sections import (
    AHEAD_SECTION,
    ATTENTION_SECTION,
    SEASONS_INFO_SECTION,
    WORLD_TURNS_SECTION,
)

_SPAN_CHOICES = [(ahead.span_label(years), str(years)) for years in ahead.SPANS]


def looking_fields(saga: Saga) -> list[DialogField]:
    span = saga.ahead_span if saga.ahead_span in ahead.SPANS else ahead.DEFAULT_SPAN
    return [
        DialogField(
            "span",
            "Looking ahead",
            "select",
            str(span),
            options=_SPAN_CHOICES,
            required=True,
            hint="Kept with the saga: a number of years, or to the next "
            "Tribunal's meeting.",
        ),
        DialogField(
            "show",
            "Show",
            "select",
            saga.ahead_show if saga.ahead_show in ahead.SHOWS else ahead.EVERYTHING,
            options=pairs(ahead.SHOWS),
            required=True,
            hint="Everything, or only what comes from one kind of record.",
        ),
    ]


def looking_form(saga: Saga) -> Form:
    def apply(values: dict[str, Any]) -> None:
        saga.ahead_span = int(values["span"])
        saga.ahead_show = values["show"]

    return Form("Looking Ahead", lambda: looking_fields(saga), apply)


def calendar_fields(saga: Saga, entry: CalendarEntry | None) -> list[DialogField]:
    e = entry or CalendarEntry("", saga.current_year, saga.current_season)
    return [
        DialogField("title", "What", "text", e.title, required=True),
        DialogField("year", "Year", "int", e.year, required=True),
        DialogField(
            "season",
            "Season",
            "select",
            e.season,
            options=pairs(SEASONS),
            required=True,
        ),
        DialogField(
            "repeats",
            "Comes",
            "select",
            e.repeats if e.repeats in REPEATS else ONCE,
            options=pairs(REPEATS),
            required=True,
            hint="From its season and year on: once, each year, or every so "
            "many years.",
        ),
        DialogField(
            "every",
            "Every how many years",
            "optint",
            e.every,
            hint="For Every N years.",
        ),
        DialogField(
            "covenant_id",
            "For",
            "select",
            e.covenant_id,
            options=[(c.name, c.id) for c in saga.covenants],
            allow_blank=True,
            placeholder="(the whole saga)",
            hint="A covenant's own entries show on its Seasons too.",
        ),
        DialogField("note", "Note", "text", e.note),
    ]


def _calendar_problem(values: dict[str, Any]) -> str | None:
    if values.get("repeats") == EVERY and (values.get("every") or 0) < 1:
        return "Say every how many years it comes (1 or more)."
    return None


def calendar_form(
    saga: Saga, entry: CalendarEntry | None, covenant: Covenant | None = None
) -> Form:
    """Add (`entry` None; for `covenant` when added from its Seasons) or
    Edit a calendar entry."""

    def fields() -> list[DialogField]:
        found = calendar_fields(saga, entry)
        if entry is None and covenant is not None:
            for field in found:
                if field.key == "covenant_id":
                    field.value = covenant.id
        return found

    def apply(values: dict[str, Any]) -> None:
        target = entry
        if target is None:
            target = CalendarEntry(values["title"], values["year"])
            saga.calendar.append(target)
        target.title = values["title"]
        target.year = values["year"]
        target.season = values["season"]
        target.repeats = values["repeats"]
        target.every = values.get("every") if target.repeats == EVERY else None
        target.covenant_id = values.get("covenant_id") or None
        target.note = values.get("note") or ""

    return Form(
        "Add a Calendar Entry" if entry is None else "Edit a Calendar Entry",
        fields,
        apply,
        validate=_calendar_problem,
    )


def _worked_out(entry: ahead.Entry) -> Refuse:
    source = entry.source or "the saga"
    return Refuse(
        "Worked Out",
        f"{escape(entry.title)} is worked out from {escape(source)}: change it there.",
    )


def ahead_ops(saga: Saga, covenant: Covenant | None = None) -> SectionOps:
    """The Looking Ahead list's Add, Edit and Delete: on the storyguide's
    own entries; a worked-out row is changed where it comes from."""

    def chosen(row: int) -> ahead.Entry | None:
        found = ahead.shown(saga, covenant)
        return found[row] if 0 <= row < len(found) else None

    def edit(row: int) -> Command:
        entry = chosen(row)
        if entry is None:
            return Refuse("Nothing Chosen", "Choose an entry first.")
        if entry.calendar is None:
            return _worked_out(entry)
        return calendar_form(saga, saga.calendar[entry.calendar])

    def remove(row: int) -> Command:
        entry = chosen(row)
        if entry is None:
            return Refuse("Nothing Chosen", "Choose an entry first.")
        if entry.calendar is None:
            return _worked_out(entry)
        index = entry.calendar

        def apply() -> None:
            del saga.calendar[index]

        written = saga.calendar[index]
        again = "" if written.repeats == ONCE else " (every time it comes)"
        return Confirm(f"Delete {escape(written.title)}{again}?", apply)

    return SectionOps(
        add=lambda: calendar_form(saga, None, covenant),
        edit=edit,
        remove=remove,
        rows=lambda: [e.title for e in ahead.shown(saga, covenant)],
    )


def seasons_ops(saga: Saga) -> dict[str, SectionOps]:
    """The Seasons sheet: its top panel's Edit, Needs You's Open and the
    Looking Ahead list."""
    return {
        SEASONS_INFO_SECTION: SectionOps(edit=lambda _row: looking_form(saga)),
        ATTENTION_SECTION: attention.ops(saga),
        AHEAD_SECTION: ahead_ops(saga),
        WORLD_TURNS_SECTION: world_turns.turn_ops(saga),
    }
