"""A covenant's Hermetic Projects: the great works its magi and
craftsmen raise over many seasons. Each project is of a kind (a Great
Tower now); a tower keeps a ledger of the works done on it (rituals
cast, a master mason's seasons, repairs, stress checks) and the craft
devices that speed its building. What those add up to (its height,
quality, damage levels, the mason's rate) is rules.hermetic_projects'.

Hermetic Projects pp. 36-41."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .checked import one_of as _one_of
from .checked import text as _text
from .checked import whole as _whole
from .common import SEASONS, known_fields
from .menagerie import MENAGERIE, Beast, Breeding, beasts_from, breedings_from
from .traits import new_instance_id

GREAT_TOWER = "Great Tower"
#: The kinds of project a covenant can begin: a Great Tower (HP pp.
#: 36-41) or a Menagerie of magical beasts (HP pp. 119-142).
PROJECT_KINDS: tuple[str, ...] = (GREAT_TOWER, MENAGERIE)

#: The quality of a piece of work, worst first (City & Guild p. 67).
SHODDY, STANDARD, SUPERIOR, EXCELLENT = "Shoddy", "Standard", "Superior", "Excellent"
QUALITIES: tuple[str, ...] = (SHODDY, STANDARD, SUPERIOR, EXCELLENT)

#: What a work on a tower is: a Creo ritual, a master mason's building
#: seasons, a season repairing a damage level, a season rebuilding a
#: shoddy section as standard, a stress check, or anything else.
RITUAL, BUILDING, REPAIR, REBUILD, STRESS, OTHER = (
    "ritual",
    "building",
    "repair",
    "rebuild",
    "stress",
    "other",
)
WORK_KINDS: tuple[str, ...] = (RITUAL, BUILDING, REPAIR, REBUILD, STRESS, OTHER)
WORK_KIND_LABELS: dict[str, str] = {
    RITUAL: "Ritual",
    BUILDING: "Mason's building",
    REPAIR: "Repair",
    REBUILD: "Rebuild a shoddy section",
    STRESS: "Stress check",
    OTHER: "Other",
}

#: A stress check's outcome.
HELD, DAMAGED, BOTCHED = "Held", "Damaged", "Botched"
STRESS_OUTCOMES: tuple[str, ...] = (HELD, DAMAGED, BOTCHED)

#: What a craft device adds (HP pp. 39-41): +1 to the mason's Craft: Mason
#: for how fast he builds (each kind of device once), +1 to stress checks
#: for each Flying Buttress, or +1 Innovation (the Water Wheel).
CRAFT, BUTTRESS, INNOVATION = "craft", "buttress", "innovation"
DEVICE_KINDS: tuple[str, ...] = (CRAFT, BUTTRESS, INNOVATION)
DEVICE_KIND_LABELS: dict[str, str] = {
    CRAFT: "+1 Craft: Mason (building rate)",
    BUTTRESS: "+1 to stress checks (a Flying Buttress)",
    INNOVATION: "+1 Innovation (the Water Wheel)",
}


@dataclass
class ProjectWork:
    """One work done on a project, in its ledger: when, what kind, the
    levels it added and their quality, and for a stress check its
    outcome and the damage levels lost."""

    id: str = field(default_factory=new_instance_id)
    kind: str = RITUAL
    name: str = ""
    season: str = "Spring"
    year: int = 1220
    #: Levels of the tower it added (20 ft each); 0 for none.
    levels: int = 0
    #: The quality of what it built (QUALITIES), "" for a work that built
    #: nothing. A ritual whose Finesse roll failed is Shoddy (HP p. 39).
    quality: str = ""
    #: A mason's building: how many seasons the entry covers.
    seasons: int = 1
    #: Who did it: the caster or the mason (a character id), "" for none.
    who: str = ""
    #: A rebuild: the work whose shoddy section it made standard (HP p. 38).
    rebuilt: str = ""
    #: A stress check: Held, Damaged or Botched, and the damage levels lost.
    outcome: str = ""
    damage: int = 0
    #: The roll, as worked out (the ledger's line).
    details: str = ""
    #: Anything else: a tether made, a story it began.
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], what: str) -> ProjectWork:
        if not isinstance(data, dict):
            raise ValueError(f"{what}: a work should be a mapping, not {data!r}.")
        d = known_fields(cls, data)
        label = f"{what}, work {d.get('name') or d.get('id') or '?'}"
        d["kind"] = _one_of(d.get("kind", RITUAL), WORK_KINDS, f"{label}: its kind")
        d["season"] = _one_of(d.get("season", "Spring"), SEASONS, f"{label}: season")
        d["year"] = _whole(d.get("year", 1220), f"{label}: year", None)
        d["levels"] = _whole(d.get("levels", 0), f"{label}: levels")
        d["seasons"] = _whole(d.get("seasons", 1), f"{label}: seasons", 1)
        d["damage"] = _whole(d.get("damage", 0), f"{label}: damage levels")
        quality = d.get("quality") or ""
        if quality:
            _one_of(quality, QUALITIES, f"{label}: quality")
        d["quality"] = quality
        outcome = d.get("outcome") or ""
        if outcome:
            _one_of(outcome, STRESS_OUTCOMES, f"{label}: outcome")
        d["outcome"] = outcome
        for key in ("name", "who", "rebuilt", "details", "note"):
            d[key] = _text(d.get(key), f"{label}: {key}")
        return cls(**d)


@dataclass
class CraftDevice:
    """An enchanted device that helps the building (HP pp. 39-41): what it
    is, its effect, and what it adds."""

    id: str = field(default_factory=new_instance_id)
    name: str = ""
    #: Its effect, as the book gives it ("ReHe 40").
    effect: str = ""
    #: What it is made as ("a crane", "a leather glove").
    shape: str = ""
    kind: str = CRAFT
    #: Flying Buttresses: how many stand (each +1 to stress checks).
    count: int = 1
    description: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], what: str) -> CraftDevice:
        if not isinstance(data, dict):
            raise ValueError(f"{what}: a device should be a mapping, not {data!r}.")
        d = known_fields(cls, data)
        label = f"{what}, device {d.get('name') or d.get('id') or '?'}"
        d["kind"] = _one_of(d.get("kind", CRAFT), DEVICE_KINDS, f"{label}: its kind")
        d["count"] = _whole(d.get("count", 1), f"{label}: count", 1)
        for key in ("name", "effect", "shape", "description"):
            d[key] = _text(d.get(key), f"{label}: {key}")
        return cls(**d)


@dataclass
class HermeticProject:
    """One Hermetic Project of a covenant: its name and kind, when it was
    begun, its master mason and its place, and the building operation's
    Innovation and Raw Materials (the whole operation is the master
    mason's workshop, HP p. 37); with its works and its craft devices."""

    id: str = field(default_factory=new_instance_id)
    name: str = ""
    kind: str = GREAT_TOWER
    season: str = "Spring"
    year: int = 1220
    #: The master mason (a character id), "" for none yet.
    mason_id: str = ""
    #: The place it stands (a place neighbour's id), whose aura its
    #: rituals' tethers feed; "" for none.
    place_id: str = ""
    #: The workshop's Innovation and Raw Materials, up to +3 each.
    innovation: int = 0
    raw_materials: int = 0
    description: str = ""
    works: list[ProjectWork] = field(default_factory=list)
    devices: list[CraftDevice] = field(default_factory=list)
    # A Menagerie (HP pp. 119-142): its handlers (character ids), its
    # owner and the name of the Reputation it earns him (p. 138), its
    # beasts and the breedings of their pairs.
    handler_ids: list[str] = field(default_factory=list)
    owner_id: str = ""
    reputation: str = ""
    beasts: list[Beast] = field(default_factory=list)
    breedings: list[Breeding] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any], covenant: str = "") -> HermeticProject:
        if not isinstance(data, dict):
            raise ValueError(
                f"{covenant}: a Hermetic Project should be a mapping, not {data!r}."
            )
        d = known_fields(cls, data)
        label = f"{covenant}'s project {d.get('name') or d.get('id') or '?'}"
        d["kind"] = _one_of(d.get("kind", GREAT_TOWER), PROJECT_KINDS, f"{label}: kind")
        d["season"] = _one_of(d.get("season", "Spring"), SEASONS, f"{label}: season")
        d["year"] = _whole(d.get("year", 1220), f"{label}: year", None)
        d["innovation"] = _whole(d.get("innovation", 0), f"{label}: Innovation")
        d["raw_materials"] = _whole(
            d.get("raw_materials", 0), f"{label}: Raw Materials"
        )
        for key in ("name", "mason_id", "place_id", "description"):
            d[key] = _text(d.get(key), f"{label}: {key}")
        works = d.get("works") or []
        devices = d.get("devices") or []
        if not isinstance(works, list) or not isinstance(devices, list):
            raise ValueError(f"{label}: its works and devices should be lists.")
        d["works"] = [ProjectWork.from_dict(w, label) for w in works]
        d["devices"] = [CraftDevice.from_dict(x, label) for x in devices]
        # A Menagerie's staff, owner, beasts and breedings.
        handlers = d.get("handler_ids") or []
        if not isinstance(handlers, list):
            raise ValueError(f"{label}: its handlers should be a list.")
        d["handler_ids"] = [_text(h, f"{label}: a handler") for h in handlers]
        for key in ("owner_id", "reputation"):
            d[key] = _text(d.get(key), f"{label}: {key}")
        d["beasts"] = beasts_from(d.get("beasts"), label)
        d["breedings"] = breedings_from(d.get("breedings"), label)
        return cls(**d)


def projects_from(value: Any, covenant: str) -> list[HermeticProject]:
    """A covenant's saved projects, checked (an older save has none)."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{covenant}: its Hermetic Projects should be a list.")
    return [HermeticProject.from_dict(p, covenant) for p in value]
