"""The season form's fields for arithmetic magic's two seasons -- no UI in
here. Inventing Rotes: their Technique and Form and the Rotes ("Name:
level; Name: level (text)"). Binding an enchanted structure: its name,
its highest component effect's level, its Size multiplier and the days
recomputing the components' places takes after a miss; it also
shows the season form's "Vis from" choice (PAYS_VIS). The rules and
their pages are rules.tmre_numerology's (The Mysteries Revised Edition
pp. 91-101); the seasons are rules.season_work.arithmetic's."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..arts import FORMS, TECHNIQUES
from ..form_spec import ChoiceReads, DialogField
from ..models import SeasonPlan
from ..rules import tmre_numerology as tn
from ..rules.season_work import arithmetic as aw

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]

#: The seasons that pay vis, from the pool the form's "Vis from" names.
PAYS_VIS = (aw.BIND_STRUCTURE,)


def fields(plan: SeasonPlan | None, activity_is: ActivityIs) -> list[DialogField]:
    """The Rotes invented, or the structure bound."""
    rotes = plan is not None and plan.activity == aw.INVENT_ROTES
    bind = plan is not None and plan.activity == aw.BIND_STRUCTURE
    size = plan.effect_params.get("size", "") if plan and bind else ""
    rework = plan.effect_params.get("rework_days", "") if plan and bind else ""
    return [
        DialogField(
            "rote_technique",
            "Rotes' Technique",
            "select",
            (plan.technique if plan and rotes else "") or None,
            options=[(t, t) for t in TECHNIQUES],
            allow_blank=True,
            show_if=activity_is(aw.INVENT_ROTES),
        ),
        DialogField(
            "rote_form",
            "Rotes' Form",
            "select",
            (plan.form if plan and rotes else "") or None,
            options=[(f, f) for f in FORMS],
            allow_blank=True,
            show_if=activity_is(aw.INVENT_ROTES),
        ),
        DialogField(
            "rotes",
            "Rotes",
            "text",
            plan.title if plan and rotes else "",
            placeholder="e.g. Ignite the Tinder: 10; Daylight: 10 (text)",
            show_if=activity_is(aw.INVENT_ROTES),
            hint="Each costs twice its level of the Rote Lab Total, its level "
            'with "(text)" from a Lab Text; none above a fifth of the total '
            "(TMRE pp. 92-93).",
        ),
        DialogField(
            "structure_name",
            "Structure",
            "text",
            plan.title if plan and bind else "",
            placeholder="e.g. The Perfected Tower",
            show_if=activity_is(aw.BIND_STRUCTURE),
        ),
        DialogField(
            "structure_level",
            "Highest component effect",
            "optint",
            plan.book_level if plan and bind else None,
            show_if=activity_is(aw.BIND_STRUCTURE),
            hint="Its level: the binding ritual is 5 more, +1 magnitude for a "
            "Structure, +2 for a Boundary (TMRE p. 98).",
        ),
        DialogField(
            "structure_size",
            "Size multiplier",
            "select",
            size or None,
            options=[(f"{n}: {what}", str(n)) for n, what in tn.SIZES.items()],
            allow_blank=True,
            show_if=activity_is(aw.BIND_STRUCTURE),
            hint="One component per point; placing them is 6 + Size (TMRE p. 97).",
        ),
        DialogField(
            "structure_rework",
            "Days to rework a miss",
            "optint",
            int(rework) if rework.isdigit() else None,
            show_if=activity_is(aw.BIND_STRUCTURE),
            hint=f"Each failed placement costs {tn.REWORK_DAYS_LEAST} day "
            f"(posts in a field) to {tn.REWORK_DAYS_MOST} (niches in a "
            "building) of recomputing, and he tries again while the season "
            "lasts; blank is a month (TMRE p. 98).",
        ),
    ]


def _bind_params(values: dict[str, Any]) -> dict[str, str]:
    """The structure's Size multiplier and rework days, as the plan keeps
    them."""
    found: dict[str, str] = {}
    if values.get("structure_size"):
        found["size"] = values["structure_size"]
    if values.get("structure_rework") is not None:
        found["rework_days"] = str(values["structure_rework"])
    return found


#: The plan's fields these seasons set from the form (as _SEASON_READS).
READS: ChoiceReads = (
    (
        (aw.INVENT_ROTES,),
        lambda v: {
            "technique": v.get("rote_technique") or "",
            "form": v.get("rote_form") or "",
            "title": (v.get("rotes") or "").strip(),
        },
    ),
    (
        (aw.BIND_STRUCTURE,),
        lambda v: {
            "title": (v.get("structure_name") or "").strip(),
            "book_level": v.get("structure_level"),
            "effect_params": _bind_params(v),
        },
    ),
)
