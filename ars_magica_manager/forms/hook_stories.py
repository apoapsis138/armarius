"""More's Suggest a Story on a covenant's Hooks: a Hook proposes a story
drawn from it, which the storyguide accepts or not. Accepted, it is an
open Story Event in the covenant's Diary, linked to the Hook, and an entry
on Ahead in the season it is set for.

The suggestion is made from the Hook as the saga records it (its name,
the detail and description typed on it, else the catalog's text): the
app writes no story of its own. Hooks are the troupe's story ideas (DE
p. 181).
"""

from __future__ import annotations

from typing import Any

from .. import catalog
from ..commands import Command, Form, Refuse, notes
from ..form_spec import DialogField
from ..markup import escape
from ..models import (
    SEASONS,
    STORY_EVENT,
    CalendarEntry,
    Covenant,
    CovenantDiaryEntry,
    Saga,
    VirtueFlawInstance,
    next_season,
)

TITLE = "Suggest a Story"
HELP_ID = "hook-story"
SOURCE = "Ars Magica Definitive Edition, Hooks, p. 181"


def hooks(covenant: Covenant) -> list[VirtueFlawInstance]:
    """The covenant's Hooks (catalog entries with a negative cost)."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return [
        bh
        for bh in covenant.boons_hooks
        if bh.vf_id in by_id and by_id[bh.vf_id].type == "Hook"
    ]


def _name(hook: VirtueFlawInstance) -> str:
    entry = catalog.load_covenant_boon_hook_catalog_by_id()[hook.vf_id]
    detail = str(hook.params.get("detail") or "").strip()
    return f"{entry.name} ({entry.tier})" + (f": {detail}" if detail else "")


def suggestion(hook: VirtueFlawInstance) -> tuple[str, str]:
    """The story a Hook suggests: a title and what it draws on."""
    entry = catalog.load_covenant_boon_hook_catalog_by_id()[hook.vf_id]
    detail = str(hook.params.get("detail") or "").strip()
    described = str(hook.params.get("description") or "").strip()
    title = f"A story of the {entry.name} Hook" + (f": {detail}" if detail else "")
    said = described or entry.description
    return title, said


def fields(saga: Saga, covenant: Covenant) -> list[DialogField]:
    found = hooks(covenant)
    season, year = next_season(saga.current_season, saga.current_year)
    return [
        DialogField(
            "hook",
            "Hook",
            "select",
            found[0].id,
            options=[(escape(_name(h)), h.id) for h in found],
            fills=lambda v: {"title": _title_of(covenant, v)},
        ),
        DialogField(
            "title",
            "The story",
            "text",
            suggestion(found[0])[0],
            hint="The Hook's suggestion: change it as you like.",
        ),
        DialogField(
            "season", "Set in", "select", season, options=[(s, s) for s in SEASONS]
        ),
        DialogField("year", "Year", "int", year),
    ]


def _hook(covenant: Covenant, values: dict[str, Any]) -> VirtueFlawInstance | None:
    return next((h for h in hooks(covenant) if h.id == values.get("hook")), None)


def _title_of(covenant: Covenant, values: dict[str, Any]) -> str:
    hook = _hook(covenant, values)
    return suggestion(hook)[0] if hook is not None else ""


def live(covenant: Covenant) -> Any:
    def inspect(values: dict[str, Any]) -> str:
        hook = _hook(covenant, values)
        if hook is None:
            return ""
        _, said = suggestion(hook)
        return (
            f"[$label]From the Hook[/] {escape(_name(hook))}\n{escape(said)}\n\n"
            "[dim]Accepted, it is an open Story Event in the Diary, linked to the "
            "Hook, and on Ahead in its season.[/]"
        )

    return inspect


def apply(saga: Saga, covenant: Covenant, values: dict[str, Any]) -> list[str]:
    hook = _hook(covenant, values)
    assert hook is not None
    title = str(values.get("title") or "").strip() or suggestion(hook)[0]
    _, said = suggestion(hook)
    season = str(values.get("season") or saga.current_season)
    year = int(values.get("year") or saga.current_year)
    covenant.diary.append(
        CovenantDiaryEntry(
            year,
            season,
            title,
            f"{said}\nRules: {SOURCE}",
            category=STORY_EVENT,
            status="Open",
            boon_hook_id=hook.id,
        )
    )
    saga.calendar.append(
        CalendarEntry(title, year, season, note=said, covenant_id=covenant.id)
    )
    return notes(
        f"{escape(title)}: an open Story Event in {escape(covenant.name)}'s Diary, "
        f"and on Ahead in {season} {year}."
    )


def story_form(saga: Saga, covenant: Covenant | None) -> Command:
    if covenant is None:
        return Refuse(TITLE, "Choose a covenant first.")
    if not hooks(covenant):
        return Refuse(
            TITLE, f"{escape(covenant.name)} has no Hooks to draw a story from."
        )
    return Form(
        f"{TITLE}: {escape(covenant.name)}",
        lambda: fields(saga, covenant),
        lambda values: apply(saga, covenant, values),
        live=live(covenant),
        save_label="Accept",
        help_id=HELP_ID,
    )
