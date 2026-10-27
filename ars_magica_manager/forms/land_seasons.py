"""The season form's field for shaping the land -- no UI in here: which of
the covenants' land projects the season casts the Rituals of; it also
shows the season form's "Vis from" choice (PAYS_VIS). The rules and their
pages are rules.land_shaping's (Transforming Mythic Europe pp. 54-77); the
season is rules.season_work.land_shaping's."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..form_spec import ChoiceReads, DialogField
from ..markup import escape
from ..models import Saga, SeasonPlan
from ..rules import land_shaping as ls
from ..rules.season_work import land_shaping as lw

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]

#: The seasons that pay vis, from the pool the form's "Vis from" names.
PAYS_VIS = lw.PAYS_VIS


def _options(saga: Saga) -> list[tuple[str, str]]:
    found = []
    for covenant in saga.covenants:
        for project in covenant.land_projects:
            left = len(ls.remaining(saga, project))
            found.append(
                (
                    f"{escape(project.name)} ({escape(covenant.name)}; "
                    f"{left} Ritual(s) left)",
                    project.name,
                )
            )
    return found


def fields(
    saga: Saga, plan: SeasonPlan | None, activity_is: ActivityIs
) -> list[DialogField]:
    """The land project worked on."""
    ours = plan is not None and plan.activity == lw.SHAPE_LAND
    return [
        DialogField(
            "land_project",
            "Land project",
            "select",
            (plan.title if plan and ours else "") or None,
            options=_options(saga),
            allow_blank=True,
            placeholder="(none: plan one with More's Shape the Land)",
            show_if=activity_is(lw.SHAPE_LAND),
            hint="Its Rituals are cast in order, as far as the vis goes "
            "(TME pp. 54-77).",
        )
    ]


#: The plan's fields this season sets from the form (as _SEASON_READS).
READS: ChoiceReads = (
    (
        (lw.SHAPE_LAND,),
        lambda v: {"title": str(v.get("land_project") or "").strip()},
    ),
)
