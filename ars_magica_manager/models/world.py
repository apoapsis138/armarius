"""The pieces every record of the saga's world shares: how much of it is
written down (its detail level), its attitude toward each player covenant
and the reasons behind it, the favours owed, and its links to other
records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields, move_secrets
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


def read_standing(d: dict[str, Any]) -> None:
    """Turn a loaded record's attitudes and favours into their classes,
    in place: the standing a neighbour, a covenant, a character or a
    creature holds toward the troupe."""
    d["attitudes"] = [Attitude.from_dict(a) for a in d.get("attitudes") or []]
    d["favours"] = [Favour(**known_fields(Favour, f)) for f in d.get("favours") or []]


#: The kinds of record a Link can point at, as the saga lists them.
LINK_KINDS: tuple[str, ...] = (
    "characters",
    "covenants",
    "books",
    "possessions",
    "familiars",
    "places",
    "creatures",
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


#: Labels older packs gave a faction's kind outside factions.FACTION_KINDS,
#: as the list has them; moved when a saga is loaded.
OLD_FACTION_KINDS: dict[str, str] = {
    "Tribe": "People or tribe",
    "People": "People or tribe",
    "Dynasty": "Family",
    "Nobility": "Family",
    "Church": "Religious community",
    "Holy societas": "Religious community",
    "False gods": "Faith or sect",
}


@dataclass
class Neighbour:
    """Someone or something of the saga's world beyond the covenants: a
    lord, a town, a church, a university, a faction or a threat
    (neighbours.KINDS). Its kind's own fields are kept in `details`.
    Only the name is required."""

    id: str
    name: str
    kind: str = "faction"
    summary: str = ""
    detail: str = SKETCH
    #: Its ruler or leader, as a name.
    ruler: str = ""
    #: The neighbour it answers to (its liege, its bishop), by id.
    answers_to: str | None = None
    #: One of common.REALMS, or "".
    realm: str = ""
    #: The place it is in (a place's: the place it is inside), by id, and
    #: which of that place's levels (0 for the surface; places.py).
    place_id: str | None = None
    place_level: int = 0
    #: What its kind adds, by field.
    details: dict[str, Any] = field(default_factory=dict)
    attitudes: list[Attitude] = field(default_factory=list)
    favours: list[Favour] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)
    #: A lord's, town's or faction's arms (arms.Arms.to_dict); empty for
    #: none.
    arms: dict[str, str] = field(default_factory=dict)
    #: What only the storyguide should read: the record's Secrets
    #: chapter, hidden from players signed in to a hosted copy.
    secrets: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Neighbour:
        # Older saves kept secrets under a heading in the summary.
        d = move_secrets(known_fields(cls, data), "summary")
        read_standing(d)
        d["links"] = [Link(**known_fields(Link, x)) for x in d.get("links", [])]
        d["details"] = dict(d.get("details") or {})
        label = d["details"].get("faction")
        if d.get("kind") == "faction" and label in OLD_FACTION_KINDS:
            d["details"]["faction"] = OLD_FACTION_KINDS[label]
        return cls(**d)


def details_list(neighbour: Neighbour, name: str) -> list[dict[str, Any]]:
    """The list `name` in the neighbour's details, made empty if
    missing."""
    found = neighbour.details.setdefault(name, [])
    if not isinstance(found, list):
        raise ValueError(f"A neighbour's {name} should be a list, not {found!r}.")
    return found
