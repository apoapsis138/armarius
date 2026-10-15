"""The pieces every record of the saga's world shares: how much of it is
written down (its detail level), its attitude toward each player covenant
and the reasons behind it, the favours owed, and its links to other
records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields
from .traits import new_instance_id

#: How much of a character or covenant is written down: a line, a sketch
#: (the statblock that matters), or the full record. Only a Full record
#: takes part in play (world.takes_part_in_play).
LINE = "Line"
SKETCH = "Sketch"
FULL = "Full"
DETAIL_LEVELS: tuple[str, ...] = (LINE, SKETCH, FULL)

#: An attitude's least and greatest score.
ATTITUDE_RANGE = (-3, 3)


@dataclass
class Reason:
    """Why an attitude moved: what happened, by how much (+1, -1 or more),
    and the season it was entered."""

    what: str
    change: int
    year: int | None = None
    season: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class Attitude:
    """A record's attitude toward one player covenant (`covenant_id`): the
    score it started at, and every reason it has moved since. The current
    score is worked out (world.attitude_score), never stored."""

    covenant_id: str
    start: int = 0
    reasons: list[Reason] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Attitude:
        d = known_fields(cls, data)
        d["reasons"] = [Reason(**known_fields(Reason, r)) for r in d.get("reasons", [])]
        return cls(**d)


@dataclass
class Favour:
    """A favour owed: `owed_by` (a name, or a record's id) owes `owed_to`
    for `what`, since a season; repaid in a later one, or still open."""

    what: str
    owed_by: str = ""
    owed_to: str = ""
    year: int | None = None
    season: str = ""
    repaid_year: int | None = None
    repaid_season: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


#: The kinds of record a Link can point at, as the saga lists them.
LINK_KINDS: tuple[str, ...] = (
    "characters",
    "covenants",
    "books",
    "possessions",
    "familiars",
    "places",
)


@dataclass
class Link:
    """A link to another record (`kind`, one of LINK_KINDS, and its
    `target_id`) with a short note. The link back is worked out
    (world.links_to), never stored twice."""

    kind: str
    target_id: str
    note: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)
