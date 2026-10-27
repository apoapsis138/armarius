"""A Criamon magus's Enigma: the path he walks, his guide, when he reached
each station, and his stigmata (Houses of Hermes: Mystery Cults pp. 50-51,
58-73). Which stations he holds is read from his Virtues; the rules are
rules.criamon's."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import SEASONS, known_fields
from .traits import new_instance_id

#: The guides who are no character of the saga: the one the House provides
#: (Presence + House Criamon Lore 6, the printed Scripts' assumption), and
#: one of the ghostly Primi at the Cave of Twisting Shadows (House Criamon
#: Lore 9, p. 60).
HOUSE_GUIDE = "house"
GHOST_GUIDE = "primus"

#: What a stigma marks (p. 50), by key: the label the form offers.
STIGMA_KINDS: dict[str, str] = {
    "riddle": "The Riddle of the Magus answered",
    "station": "A station reached",
    "wisdom": "Enigmatic Wisdom risen",
    "inner": "An Inner Mystery learned",
    "twilight": "Twilight",
    "apprentice": "An apprentice begun or finished",
    "familiar": "A familiar sought or bound",
    "work": "A great work of the Art",
    "other": "Something else",
}


def _check_int(record: str, d: dict[str, Any], *keys: str) -> None:
    """Raise ValueError naming `record` when a whole number isn't one."""
    for key in keys:
        value = d.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{record}: {key} {value!r} isn't a whole number.")


def _check_season(record: str, d: dict[str, Any]) -> None:
    season = d.get("season") or ""
    if season and season not in SEASONS:
        raise ValueError(f"{record}: season {season!r} isn't a season.")


@dataclass
class StationReached:
    """When a station was reached: its Virtue (a Virtue/Flaw catalog id)
    and the season, kept when an Initiation season gives it."""

    vf_id: str
    season: str = ""
    year: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StationReached:
        d = known_fields(cls, data)
        record = f"The station reached {d.get('vf_id')!r}"
        if not isinstance(d.get("vf_id"), str) or not d["vf_id"]:
            raise ValueError(f"{record}: it names no station's Virtue.")
        _check_int(record, d, "year")
        _check_season(record, d)
        return cls(**d)


@dataclass
class Stigma:
    """One stigma: where on the body, the mark, what it marks (a
    STIGMA_KINDS key, and the particular: "the Station of True Sight") and
    when it appeared."""

    where: str
    mark: str
    why: str = "other"
    detail: str = ""
    season: str = ""
    year: int | None = None
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Stigma:
        d = known_fields(cls, data)
        record = f"The stigma {d.get('mark') or d.get('where')!r}"
        for key in ("where", "mark", "detail", "season"):
            if key in d and not isinstance(d[key], str):
                raise ValueError(f"{record}: {key} {d[key]!r} isn't text.")
        if d.get("why", "other") not in STIGMA_KINDS:
            raise ValueError(f"{record}: what it marks {d.get('why')!r} isn't known.")
        _check_int(record, d, "year")
        _check_season(record, d)
        d.setdefault("where", "")
        d.setdefault("mark", "")
        return cls(**d)


@dataclass
class Enigma:
    """A Criamon magus's path (a rules.criamon.PATHS key; "" for the one
    his stations show), his guide (a character id, HOUSE_GUIDE,
    GHOST_GUIDE, or "" for the House's), a ghostly Primus's Presence when
    one guides him, the path a head bound in infancy (or a like
    modification) gives him an aptitude for ("" for none, p. 51), when he
    reached his stations, his stigmata and notes."""

    path: str = ""
    guide_id: str = ""
    primus_presence: int = 0
    aptitude_path: str = ""
    reached: list[StationReached] = field(default_factory=list)
    stigmata: list[Stigma] = field(default_factory=list)
    notes: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Enigma:
        d = known_fields(cls, data)
        record = "The Enigma"
        for key in ("path", "guide_id", "aptitude_path", "notes"):
            if key in d and not isinstance(d[key], str):
                raise ValueError(f"{record}: {key} {d[key]!r} isn't text.")
        _check_int(record, d, "primus_presence")
        d["reached"] = [StationReached.from_dict(r) for r in d.get("reached") or []]
        d["stigmata"] = [Stigma.from_dict(s) for s in d.get("stigmata") or []]
        return cls(**d)
