"""Seasonal activities from the supplements, planned on the character
sheet, and what each does beyond experience.

Each gives experience like a study season: a Source Quality in the Ability
(or Art) chosen, the rule's fixed figure or, where the rule depends on the
story (a church's aura, a sermon's Aesthetic Quality, a book's Quality), the
one the storyguide gives, typed on the plan. What else a season does (Labor
Points, a Mystery Virtue, a pilgrimage's progress...) is its outcome; the
rest is written in the Diary for the troupe.

Pattern: Registry. `base` holds the registry and the shared types; each
book's season work is a module here that registers its activities, each
with its outcome and the check that stops a plan, as it is imported. A new
book's seasons are a new module, added to the import below.
"""

from __future__ import annotations

from . import (  # noqa: F401  (each registers its activities as it is imported)
    academe,
    ancient,
    church,
    city_guild,
    covenants,
    definitive,
    initiation,
    lords,
    societates,
)
from .base import REGISTRY, SimpleActivity, SupplementWork, activities, problems, work

#: The long-term events chapter the supplements' seasons extend; each
#: book's module cites its own.
SOURCE = definitive.SOURCE
#: Every supplement activity, as the picker orders them.
ACTIVITIES: tuple[SimpleActivity, ...] = activities()
BY_KEY: dict[str, SimpleActivity] = {a.key: a for a in ACTIVITIES}

__all__ = [
    "ACTIVITIES",
    "BY_KEY",
    "REGISTRY",
    "SOURCE",
    "SimpleActivity",
    "SupplementWork",
    "problems",
    "work",
]
