"""A Diary's forms, independent of how they are drawn. A character, a
laboratory and a covenant each keep a Diary: the first two of
DiaryEntry (a season's activity), a covenant's of CovenantDiaryEntry (its
events, with the money, vis, Loyalty and Build Points they bring).

`diary_ops` is any Diary's Add, Edit and Delete (commands.SectionOps),
given how to build its entry form; `entry_ops` and `covenant_diary_ops`
are the two kinds of Diary's. Edit and Delete take the entry's index
into the diary list itself, whatever order a sheet shows them in.
"""

from __future__ import annotations

from collections.abc import Callable, MutableSequence, Sequence
from typing import Any

from .. import catalog, covenant_diary, open_stories
from ..arts import ARTS
from ..commands import Form, SectionOps, delete
from ..form_spec import EMPHASIS_HINT, DialogField, attr, pairs
from ..markup import escape
from ..models import (
    COVENANT_DIARY_CATEGORIES,
    LAB_ACTIVITIES,
    SEASONS,
    STORY_EVENT,
    STORY_EVENT_STATUSES,
    Covenant,
    CovenantDiaryEntry,
    DiaryEntry,
    Saga,
)
from ..rules import activities as season_rules


def character_activities() -> list[str]:
    """A character's Diary's Activity Types: the seasonal activities."""
    return [a.label for a in season_rules.ACTIVITIES.values()]


def entry_title(existing: object | None) -> str:
    return "Add a Diary Entry" if existing is None else "Edit a Diary Entry"


def _date_fields(existing: Any, default_year: int, default_season: str):
    return [
        DialogField("year", "Year", "int", attr(existing, "year", default_year)),
        DialogField(
            "season",
            "Season",
            "select",
            attr(existing, "season", default_season),
            options=pairs(SEASONS),
        ),
    ]


# A character's or a laboratory's Diary


def entry_fields(
    default_year: int,
    existing: DiaryEntry | None = None,
    default_season: str = SEASONS[0],
    activities: Sequence[str] = LAB_ACTIVITIES,
) -> list[DialogField]:
    """A Diary entry: a laboratory's (`activities` the lab activities) or a
    character's (the seasonal activities)."""
    return [
        *_date_fields(existing, default_year, default_season),
        DialogField(
            "activity",
            "Activity Type",
            "select",
            attr(existing, "activity", "") or None,
            options=pairs(activities),
            allow_blank=True,
        ),
        DialogField("name", "Name", "text", attr(existing, "name", ""), required=True),
        DialogField(
            "details",
            "Details",
            "area",
            attr(existing, "details", ""),
            hint=EMPHASIS_HINT,
        ),
    ]


def entry_from(values: dict[str, Any]) -> DiaryEntry:
    return DiaryEntry(**{**values, "activity": values["activity"] or ""})


# A covenant's Diary


class _CovenantEntryForm:
    """What a covenant Diary entry's form shows, checks and builds: Status,
    the linked Boon/Hook and Revisit for a Story Event only, and a Build
    Points field for the pool of the Boon or Hook linked."""

    def __init__(self, covenant: Covenant, existing: CovenantDiaryEntry | None):
        self.covenant = covenant
        self.existing = existing
        # The entry being edited, left out of its pool's points so far.
        self.skip = next(
            (i for i, e in enumerate(covenant.diary) if e is existing), None
        )

    @staticmethod
    def story(values: dict[str, Any]) -> bool:
        return values.get("category") == STORY_EVENT

    def pool(self, values: dict[str, Any]) -> covenant_diary.Pool | None:
        if not self.story(values):
            return None
        return covenant_diary.pool_of(self.covenant, values.get("boon_hook_id"))

    def hidden(self, values: dict[str, Any]) -> bool:
        return (
            self.pool(values) == covenant_diary.POOLS[covenant_diary.HIDDEN_RESOURCES]
        )

    def illusory(self, values: dict[str, Any]) -> bool:
        return (
            self.pool(values) == covenant_diary.POOLS[covenant_diary.ILLUSORY_RESOURCES]
        )

    @staticmethod
    def points(values: dict[str, Any]) -> dict[str, Any]:
        """One Build Points value, whichever pool's field it was typed in."""
        values = dict(values)
        illusory_points = values.pop("illusory_points", None)
        if illusory_points is not None:
            values["build_points"] = illusory_points
        return values

    def problem(self, values: dict[str, Any]) -> str | None:
        return covenant_diary.points_problem(
            self.covenant, self.points(values), self.skip
        )

    def build(self, values: dict[str, Any]) -> CovenantDiaryEntry:
        values = {**self.points(values), "category": values["category"] or ""}
        values["vis_art"] = values.get("vis_art") or ""
        if self.story(values):
            values["status"] = values.get("status") or STORY_EVENT_STATUSES[0]
            values["concerns"] = values.get("concerns") or (
                self.existing.concerns if self.existing is not None else ""
            )
            # The threat a story grew into is kept: the form doesn't edit it.
            if self.existing is not None:
                values["threat_id"] = self.existing.threat_id
        else:
            values.pop("concerns", None)
        return CovenantDiaryEntry(**values)


def covenant_entry_fields(
    covenant: Covenant,
    default_year: int,
    existing: CovenantDiaryEntry | None = None,
    default_season: str = SEASONS[0],
    saga: Saga | None = None,
) -> list[DialogField]:
    """A covenant Diary entry. The amounts are optional; Status, the linked
    Boon/Hook, Revisit and (given the saga) what it concerns are shown for
    Story Events only (a hidden field is left out, so it falls back to
    blank)."""
    form = _CovenantEntryForm(covenant, existing)
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    boons_hooks = [
        (
            escape(catalog.describe_boon_hook(bh, by_id))
            + f" ({by_id[bh.vf_id].type if bh.vf_id in by_id else 'Boon/Hook'})",
            bh.id,
        )
        for bh in covenant.boons_hooks
        if bh.id
    ]
    return [
        *_date_fields(existing, default_year, default_season),
        DialogField(
            "category",
            "Category",
            "select",
            attr(existing, "category", "") or None,
            options=pairs(COVENANT_DIARY_CATEGORIES),
            allow_blank=True,
        ),
        DialogField("name", "Name", "text", attr(existing, "name", ""), required=True),
        DialogField(
            "status",
            "Status",
            "select",
            attr(existing, "status", "") or STORY_EVENT_STATUSES[0],
            options=pairs(STORY_EVENT_STATUSES),
            show_if=form.story,
        ),
        DialogField(
            "boon_hook_id",
            "Linked Boon/Hook",
            "select",
            attr(existing, "boon_hook_id", None),
            options=boons_hooks,
            allow_blank=True,
            placeholder="(none)",
            show_if=form.story,
        ),
        *(
            [
                DialogField(
                    "concerns",
                    "Concerns",
                    "select",
                    attr(existing, "concerns", ""),
                    options=open_stories.concerns_options(saga, covenant),
                    show_if=form.story,
                    hint="Who or what the story is about; the Region lists every "
                    "open story, and a character's or laboratory's Connections "
                    "its own.",
                )
            ]
            if saga is not None
            else []
        ),
        DialogField(
            "revisit_year",
            "Revisit in year",
            "optint",
            attr(existing, "revisit_year", None),
            show_if=form.story,
        ),
        DialogField(
            "build_points",
            "Build Points unlocked",
            "optint",
            attr(existing, "build_points", None),
            hint="Of the Hidden Resources Boon's 250; counted once Resolved.",
            show_if=form.hidden,
        ),
        DialogField(
            "illusory_points",
            "Build Points found illusory",
            "optint",
            attr(existing, "build_points", None),
            hint="Of the Illusory Resources Hook's 250; counted once Resolved.",
            show_if=form.illusory,
        ),
        DialogField(
            "pounds",
            "Pounds (+ received, - spent)",
            "optfloat",
            attr(existing, "pounds", None),
        ),
        DialogField(
            "vis_pawns",
            "Vis pawns (+ gained, - spent)",
            "optint",
            attr(existing, "vis_pawns", None),
        ),
        DialogField(
            "vis_art",
            "Vis Art",
            "select",
            attr(existing, "vis_art", "") or None,
            options=pairs(ARTS),
            allow_blank=True,
        ),
        DialogField(
            "loyalty",
            "Loyalty points",
            "optint",
            attr(existing, "loyalty", None),
            hint="Added into the Loyalty block's Actions and Events.",
        ),
        DialogField(
            "details",
            "Details",
            "area",
            attr(existing, "details", ""),
            hint=EMPHASIS_HINT,
        ),
    ]


def covenant_entry_problem(
    covenant: Covenant, existing: CovenantDiaryEntry | None
) -> Callable[[dict[str, Any]], str | None]:
    """The covenant entry form's check: a pool's Build Points not over."""
    return _CovenantEntryForm(covenant, existing).problem


def covenant_entry_from(
    covenant: Covenant, existing: CovenantDiaryEntry | None
) -> Callable[[dict[str, Any]], CovenantDiaryEntry]:
    """What the covenant entry form builds from its values."""
    return _CovenantEntryForm(covenant, existing).build


# Add, Edit and Delete


def diary_ops(
    diary: MutableSequence[Any],
    form: Callable[[Any | None, Callable[[dict[str, Any]], None]], Form],
) -> SectionOps:
    """Any Diary's Add, Edit and Delete. `form(existing, apply)` is its
    entry form for `existing` (None: a new entry), saving through
    `apply`."""

    def add() -> Form:
        return form(None, diary.append)

    def edit(index: int) -> Form:
        def apply(entry: Any) -> None:
            diary[index] = entry

        return form(diary[index], apply)

    return SectionOps(
        add=add,
        edit=edit,
        remove=lambda index: delete(diary, index, diary[index].name or "this entry"),
        rows=lambda: [entry.name or "(unnamed)" for entry in diary],
    )


def entry_ops(
    saga: Saga,
    diary: MutableSequence[DiaryEntry],
    activities: Sequence[str] = LAB_ACTIVITIES,
) -> SectionOps:
    """A character's Diary (`activities` character_activities()) or a
    laboratory's (the lab activities)."""

    def form(existing: DiaryEntry | None, save: Callable[[Any], None]) -> Form:
        return Form(
            entry_title(existing),
            lambda: entry_fields(
                saga.current_year, existing, saga.current_season, activities
            ),
            lambda values: save(entry_from(values)),
        )

    return diary_ops(diary, form)


def covenant_diary_ops(saga: Saga, covenant: Covenant) -> SectionOps:
    """The covenant's Diary."""

    def form(existing: CovenantDiaryEntry | None, save: Callable[[Any], None]) -> Form:
        build = covenant_entry_from(covenant, existing)
        return Form(
            entry_title(existing),
            lambda: covenant_entry_fields(
                covenant, saga.current_year, existing, saga.current_season, saga
            ),
            lambda values: save(build(values)),
            validate=covenant_entry_problem(covenant, existing),
        )

    return diary_ops(covenant.diary, form)
