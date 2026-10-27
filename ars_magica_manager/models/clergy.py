"""A character's career in the Church: his grade in holy orders, the
ordinations that brought him there, the petitions he has made to the
Church and the canon-court cases he has stood in (The Church pp. 33-38,
46-48). The rules are rules.clergy's."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import known_fields
from .traits import new_instance_id

#: A cleric's standing: in good standing, Irregular (no Faith Points until
#: he confesses) or Excommunicated (The Church p. 37).
GOOD_STANDING = "good"
IRREGULAR = "irregular"
EXCOMMUNICATED = "excommunicated"
STANDINGS: tuple[str, ...] = (GOOD_STANDING, IRREGULAR, EXCOMMUNICATED)

#: How a petition is made: by letter or in an audience (The Church p. 47).
WRITTEN = "written"
AUDIENCE = "audience"
PETITION_METHODS: tuple[str, ...] = (WRITTEN, AUDIENCE)

#: A canon case's sides, and its verdicts.
ACCUSED = "accused"
ACCUSER = "accuser"
CASE_ROLES: tuple[str, ...] = (ACCUSED, ACCUSER)
PENDING = "pending"
ACQUITTED = "acquitted"
GUILTY = "guilty"
VERDICTS: tuple[str, ...] = (PENDING, ACQUITTED, GUILTY)


def _check_int(record: str, d: dict[str, Any], *keys: str) -> None:
    """Raise ValueError naming `record` when a whole-number value isn't one."""
    for key in keys:
        value = d.get(key)
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{record}: {key} {value!r} isn't a whole number.")


def _check_choice(
    record: str, d: dict[str, Any], key: str, allowed: tuple[str, ...]
) -> None:
    value = d.get(key)
    if value is not None and value not in allowed:
        raise ValueError(
            f"{record}: {key} {value!r} isn't one of {', '.join(allowed)}."
        )


@dataclass
class Ordination:
    """One ordination examination: the grade sought, the Ability examined,
    the roll and what came of it (rules.clergy.EXAM_RESULTS' keys)."""

    grade: str
    season: str = ""
    year: int | None = None
    #: The Ability examined and his Intelligence and score in it then.
    ability: str = ""
    intelligence: int = 0
    score: int = 0
    #: The stress die; a botch is recorded as such, its die 0.
    die: int = 0
    botched: bool = False
    ease: int = 0
    result: str = ""
    examiner: str = ""
    #: Ordained outside his birth diocese, by its bishop's leave (p. 33).
    elsewhere: bool = False
    note: str = ""
    id: str = field(default_factory=new_instance_id)

    @property
    def total(self) -> int:
        """The Examination Total: Intelligence + the Ability + stress die,
        no more than 0 on a botch (as dice.Roll counts it)."""
        base = self.intelligence + self.score
        return min(0, base) if self.botched else base + self.die

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ordination:
        d = dict(data)
        name = f"The ordination as {d.get('grade') or '(no grade)'}"
        _check_int(name, d, "year", "intelligence", "score", "die", "ease")
        return cls(**known_fields(cls, d))


@dataclass
class Petition:
    """A petition to the Church: what was asked, its Ease Factor, how it
    was made, and every modifier (The Church pp. 46-48)."""

    ask: str
    #: The book's example it was likened to (rules.clergy.EXAMPLES' names;
    #: "" for none), which set its Ease Factor.
    example: str = ""
    ease: int = 9
    method: str = WRITTEN
    #: A written petition's scribe: his name, and his Communication +
    #: Church Lore, used instead of the petitioner's (None: his own).
    scribe: str = ""
    scribe_total: int | None = None
    #: The petitioner's Characteristic and Church Lore when it was made.
    characteristic: int = 0
    lore: int = 0
    #: The Gift's penalty, taken off an audience only.
    gift: int = 0
    testimony: bool = False
    evidence: bool = False
    vision: bool = False
    miracle: bool = False
    #: The highest clergy and lay support: +1, +3 or +6 (0: none).
    clergy: int = 0
    lay: int = 0
    donation: int = 0
    #: The arguments put, by Ability (rules.clergy.ARGUMENTS): the bonus
    #: claimed (1 to 3), the Int + Ability + stress die rolled for it, and
    #: whether that roll botched.
    arguments: dict[str, int] = field(default_factory=dict)
    argument_rolls: dict[str, int] = field(default_factory=dict)
    argument_botches: list[str] = field(default_factory=list)
    #: His Reputation with the Church (signed) and spells cast on those
    #: deciding, as the troupe judges them.
    reputation: int = 0
    spells: int = 0
    #: An appeal against another's petition: its Petition Total, and
    #: whether the appeal comes in a later season (-3).
    appeal: bool = False
    original: int | None = None
    late: bool = False
    #: False while it is only planned (no total yet).
    made: bool = True
    season: str = ""
    year: int | None = None
    note: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Petition:
        d = dict(data)
        name = f"The petition {d.get('ask') or '(unnamed)'!r}"
        _check_int(
            name,
            d,
            "ease",
            "scribe_total",
            "characteristic",
            "lore",
            "gift",
            "clergy",
            "lay",
            "donation",
            "reputation",
            "spells",
            "original",
            "year",
        )
        _check_choice(name, d, "method", PETITION_METHODS)
        for key in ("arguments", "argument_rolls"):
            found = d.get(key) or {}
            if not isinstance(found, dict):
                raise ValueError(f"{name}: {key} must be a table of numbers.")
            _check_int(name, found, *found)
            d[key] = {str(k): v for k, v in found.items()}
        d["argument_botches"] = [str(x) for x in d.get("argument_botches") or []]
        return cls(**known_fields(cls, d))


@dataclass
class CanonCase:
    """A case in a canon court, the character accused or accusing
    (The Church pp. 35-38)."""

    charge: str
    #: Whom or what it is about.
    what: str = ""
    role: str = ACCUSED
    court: str = ""
    season: str = ""
    year: int | None = None
    #: About a dozen oath-helpers swore to the accused's good character.
    compurgation: bool = False
    verdict: str = PENDING
    #: rules.clergy.PUNISHMENTS' names; "" while not guilty.
    punishment: str = ""
    note: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CanonCase:
        d = dict(data)
        name = f"The canon case {d.get('charge') or '(no charge)'!r}"
        _check_int(name, d, "year")
        _check_choice(name, d, "role", CASE_ROLES)
        _check_choice(name, d, "verdict", VERDICTS)
        return cls(**known_fields(cls, d))


@dataclass
class ChurchCareer:
    """The character's grade in holy orders and his dealings with the
    Church: empty for a layman who has never petitioned or been tried."""

    #: rules.clergy.GRADES' names ("": a layman).
    grade: str = ""
    #: The diocese he was born in, where he is ordained (The Church p. 33).
    diocese: str = ""
    standing: str = GOOD_STANDING
    #: His benefice, curacy or office: a priest needs one to be ordained.
    benefice: str = ""
    #: A botched examination: he may sit it again only once a petition
    #: lets him (The Church p. 34).
    barred: bool = False
    notes: str = ""
    ordinations: list[Ordination] = field(default_factory=list)
    petitions: list[Petition] = field(default_factory=list)
    cases: list[CanonCase] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChurchCareer:
        d = dict(data)
        _check_choice("The character's holy orders", d, "standing", STANDINGS)
        d["ordinations"] = [Ordination.from_dict(o) for o in d.get("ordinations", [])]
        d["petitions"] = [Petition.from_dict(p) for p in d.get("petitions", [])]
        d["cases"] = [CanonCase.from_dict(c) for c in d.get("cases", [])]
        return cls(**known_fields(cls, d))
