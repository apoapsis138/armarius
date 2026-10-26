"""Lords of Men's seasons: an errant knight's tournament circuit (Labor
Points, as a working season) and recruiting or using agents."""

from __future__ import annotations

from .. import activity_groups as groups
from .base import (
    CH,
    COMPANIONS,
    SimpleActivity,
    experience_only,
    needs_subject,
    register,
    source,
)
from .city_guild import _working_season

LORDS = source("Lords of Men " + CH.format("Lords_of_Men"), "LoM")

register(
    SimpleActivity(
        "tournament",
        "Tournament circuit",
        "An errant knight's season: Labor Points from Dexterity + Weapon. Exposure 2.",
        LORDS,
        "919",
        who=COMPANIONS,
        group=groups.ADVENTURE,
    ),
    _working_season,
    needs_subject,
)
register(
    SimpleActivity(
        "use_agents",
        "Recruit or use agents",
        "Information once a season per agent. Exposure 2.",
        LORDS,
        "919",
        who=COMPANIONS,
        group=groups.ORDER,
    ),
    experience_only,
)
