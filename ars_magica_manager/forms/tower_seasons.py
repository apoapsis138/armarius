"""The season form's field for a master mason's season on a Great Tower
-- no UI in here: whether he builds, repairs a damage level or rebuilds a
shoddy section. The rules and their pages are rules.hermetic_projects'
(Hermetic Projects pp. 36-38); the season is
rules.season_work.hermetic_projects'."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..form_spec import ChoiceReads, DialogField
from ..models import SeasonPlan
from ..rules.season_work import hermetic_projects as tw

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]


def fields(plan: SeasonPlan | None, activity_is: ActivityIs) -> list[DialogField]:
    """The season's work on the tower."""
    ours = plan is not None and plan.activity == tw.BUILD_TOWER
    return [
        DialogField(
            "tower_work",
            "Work on the tower",
            "select",
            tw.work_of(plan) if plan is not None and ours else tw.BUILDING,
            options=[(label, key) for key, label in tw.TOWER_WORKS.items()],
            show_if=activity_is(tw.BUILD_TOWER),
            hint="A repair restores one damage level, with no other building "
            "that season (Hermetic Projects p. 38).",
        )
    ]


#: The plan's fields this season sets from the form (as _SEASON_READS).
READS: ChoiceReads = (
    ((tw.BUILD_TOWER,), lambda v: {"title": v.get("tower_work") or tw.BUILDING}),
)
