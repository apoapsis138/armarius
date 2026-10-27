"""A Menagerie of magical beasts (Hermetic Projects pp. 119-142), the
second kind of Hermetic Project: the beasts it keeps and the breedings
of their pairs. The project's record (models.hermetic_projects) holds
them with its staff and owner; what they add up to (upkeep, how many the
staff can tend, a young beast's Might, the breeding rolls) is
rules.menagerie's."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .checked import one_of, text, whole
from .common import SEASONS, known_fields
from .traits import new_instance_id

MENAGERIE = "Menagerie"

#: The three kinds of magical beast (HP p. 124): a Beast of Virtue, a
#: Beast of Legend, or a Transformed Animal (no Might, never breeds true).
BEAST_OF_VIRTUE, BEAST_OF_LEGEND, TRANSFORMED = (
    "Beast of Virtue",
    "Beast of Legend",
    "Transformed Animal",
)
BEAST_KINDS: tuple[str, ...] = (BEAST_OF_VIRTUE, BEAST_OF_LEGEND, TRANSFORMED)

MALE, FEMALE, BOTH = "male", "female", "both"
SEXES: tuple[str, ...] = (MALE, FEMALE, BOTH)

HERBIVORE, CARNIVORE = "herbivore", "carnivore"
DIETS: tuple[str, ...] = (HERBIVORE, CARNIVORE)

#: What a breeding aims at (HP pp. 141-142): just young, the best of a
#: breed (selective breeding), or a new line (crossbreeding).
YOUNG, BEST, BEAST = "", "best", "beast"
AIMS: tuple[str, ...] = (YOUNG, BEST, BEAST)
AIM_LABELS: dict[str, str] = {
    YOUNG: "Just for young",
    BEST: "For the best (the same breed)",
    BEAST: "For the beast (a new line)",
}

#: Most magical beasts take five years to grow (HP p. 134).
MATURITY_YEARS = 5


@dataclass
class Beast:
    """One row of a menagerie's beasts: one beast, or several alike
    (`count`), with what the menagerie's rules read from it. `creature_id`
    ties it to a creature of the saga's Bestiary, for its full
    statistics."""

    id: str = field(default_factory=new_instance_id)
    name: str = ""
    kind: str = BEAST_OF_VIRTUE
    #: Its kind of animal ("Goat", "Lion"): a kind holds several breeds
    #: (HP p. 131), and the Breeding Roll's -3 is for the only pair of
    #: their kind (HP p. 141).
    animal: str = ""
    #: Its breed ("Goat of Virtue"): a realia counts breeds (HP p. 123).
    breed: str = ""
    creature_id: str = ""
    #: Its Magic Might when grown, and the Form it is of.
    might: int = 0
    form: str = "Animal"
    size: int = 0
    #: An animal intellect (Cunning): only such a beast can be tamed.
    cunning: bool = True
    sex: str = FEMALE
    count: int = 1
    diet: str = HERBIVORE
    #: Tamed by hand (a taming season in the app marks it too).
    tamed: bool = False
    #: Who is taming it (a character id), "" for no one.
    tamer_id: str = ""
    #: The year it was born in the menagerie; None for a beast grown.
    born: int | None = None
    #: Years it takes to grow (HP p. 134).
    maturity: int = MATURITY_YEARS
    #: Its Ferocity (an aggressive beast's Personality Trait), taken off
    #: the Breeding Roll (HP p. 140).
    ferocity: int = 0
    #: Its enchanted brands, one a line (HP pp. 130-131).
    brands: list[str] = field(default_factory=list)
    #: A crossbred dam that resembles her dam: +3 to her later breedings
    #: for the beast (HP p. 142).
    cross_bonus: bool = False
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], what: str) -> Beast:
        if not isinstance(data, dict):
            raise ValueError(f"{what}: a beast should be a mapping, not {data!r}.")
        d = known_fields(cls, data)
        label = f"{what}, beast {d.get('name') or d.get('id') or '?'}"
        d["kind"] = one_of(
            d.get("kind", BEAST_OF_VIRTUE), BEAST_KINDS, f"{label}: kind"
        )
        d["sex"] = one_of(d.get("sex", FEMALE), SEXES, f"{label}: sex")
        d["diet"] = one_of(d.get("diet", HERBIVORE), DIETS, f"{label}: diet")
        d["might"] = whole(d.get("might", 0), f"{label}: Might")
        d["size"] = whole(d.get("size", 0), f"{label}: Size", None)
        d["count"] = whole(d.get("count", 1), f"{label}: count", 1)
        d["maturity"] = whole(
            d.get("maturity", MATURITY_YEARS), f"{label}: maturity", 1
        )
        d["ferocity"] = whole(d.get("ferocity", 0), f"{label}: Ferocity")
        born = d.get("born")
        d["born"] = None if born is None else whole(born, f"{label}: born", None)
        for key in ("cunning", "tamed", "cross_bonus"):
            value = d.get(key, key == "cunning")
            if not isinstance(value, bool):
                raise ValueError(f"{label}: {key} should be true or false.")
            d[key] = value
        for key in (
            "name",
            "animal",
            "breed",
            "creature_id",
            "form",
            "tamer_id",
            "note",
        ):
            d[key] = text(d.get(key), f"{label}: {key}")
        brands = d.get("brands") or []
        if not isinstance(brands, list):
            raise ValueError(f"{label}: its brands should be a list.")
        d["brands"] = [text(b, f"{label}: a brand") for b in brands]
        return cls(**d)


@dataclass
class Breeding:
    """One season's breeding of a pair (HP pp. 140-142), as rolled: the
    pair, what it aimed at, the Breeding Roll's total and outcome, the
    young born and the offspring roll's result."""

    id: str = field(default_factory=new_instance_id)
    season: str = "Spring"
    year: int = 1220
    sire_id: str = ""
    dam_id: str = ""
    #: The pair's names when bred ("Bock × Geiß").
    pair: str = ""
    aim: str = YOUNG
    #: The Breeding Roll's total and the botch dice that showed 0.
    total: int = 0
    botches: int = 0
    #: How many young were born (0: none).
    young: int = 0
    #: The outcome in a few words ("No young", "Two young: hardy").
    result: str = ""
    #: The rolls as worked out.
    details: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any], what: str) -> Breeding:
        if not isinstance(data, dict):
            raise ValueError(f"{what}: a breeding should be a mapping, not {data!r}.")
        d = known_fields(cls, data)
        label = f"{what}, breeding {d.get('pair') or d.get('id') or '?'}"
        d["season"] = one_of(d.get("season", "Spring"), SEASONS, f"{label}: season")
        d["year"] = whole(d.get("year", 1220), f"{label}: year", None)
        d["aim"] = one_of(d.get("aim", YOUNG), AIMS, f"{label}: aim")
        d["total"] = whole(d.get("total", 0), f"{label}: total", None)
        d["botches"] = whole(d.get("botches", 0), f"{label}: botches")
        d["young"] = whole(d.get("young", 0), f"{label}: young")
        for key in ("sire_id", "dam_id", "pair", "result", "details", "note"):
            d[key] = text(d.get(key), f"{label}: {key}")
        return cls(**d)


def beasts_from(value: Any, what: str) -> list[Beast]:
    """A menagerie's saved beasts, checked (a project saved before the
    Menagerie, or a tower, has none)."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{what}: its beasts should be a list.")
    return [Beast.from_dict(b, what) for b in value]


def breedings_from(value: Any, what: str) -> list[Breeding]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{what}: its breedings should be a list.")
    return [Breeding.from_dict(b, what) for b in value]
