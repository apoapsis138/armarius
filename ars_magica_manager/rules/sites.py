"""Where a record is, and what its place gives it: a place's regio
levels, its aura at each, and the effects that reach those who live or
work there (Lab Totals, aging, Living Conditions, Warping).

A place is a Neighbour of kind "place", which may sit inside another;
its levels and effects are lists kept in its details. The forms and
sheets that edit places are places.py's; this is what the rules read."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypedDict, cast

from ..models import (
    REALMS,
    Character,
    Covenant,
    Laboratory,
    Modifier,
    Neighbour,
    Saga,
    VirtueFlawInstance,
    details_list,
)
from . import effects as fx

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Regiones "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Twelve:"
    "_Realms#Regiones)"
)

#: The kind of neighbour a place is.
PLACE = "place"


@dataclass(frozen=True)
class EffectType:
    """What a place's effect can change: its name in the lists, the
    Modifier type it is, and who it reaches."""

    key: str
    name: str
    reaches: str


#: The effects a place can have, by Modifier type (totals.MODIFIER_TYPES).
EFFECT_TYPES: dict[str, EffectType] = {
    t.key: t
    for t in (
        EffectType("lab_total", "Lab totals", "Labs here"),
        EffectType("aging_roll", "Aging rolls", "Who lives here"),
        EffectType("living_conditions", "Living Conditions", "Who lives here"),
        EffectType("warping_per_season", "Warping", "Who lives here"),
        EffectType("aura", "The aura", "Everything here"),
    )
}


def is_place(record: object) -> bool:
    return isinstance(record, Neighbour) and record.kind == PLACE


def all_places(saga: Saga) -> list[Neighbour]:
    return [n for n in saga.neighbours if n.kind == PLACE]


def place(saga: Saga, place_id: str | None) -> Neighbour | None:
    found = saga.neighbour(place_id)
    return found if is_place(found) else None


class RegioLevel(TypedDict, total=False):
    """A level of a regio: its realm and aura, and what it takes to see
    and to enter it."""

    name: str
    realm: str
    aura: int
    see: str
    enter: str
    notes: str


def levels(place: Neighbour) -> list[RegioLevel]:
    """Its regio levels, Level 1 (just above the surface) first."""
    return cast(list[RegioLevel], details_list(place, "levels"))


class AuraEffect(TypedDict, total=False):
    """Something at a place that changes its aura or a total there."""

    what: str
    amount: int
    target: str
    where: str
    note: str


def effects(place: Neighbour) -> list[AuraEffect]:
    return cast(list[AuraEffect], details_list(place, "effects"))


def whole_number(value: Any) -> int:
    """A number typed into a place's details (0 for blank or not a
    number)."""
    try:
        return int(value or 0)
    except TypeError, ValueError:
        return 0


def realm_of(value: Any, fallback: str = "Magic") -> str:
    """The realm named by `value`, whatever its case; `fallback` when it
    names none."""
    found = next((r for r in REALMS if r.casefold() == str(value or "").casefold()), "")
    return found or fallback


def _reaches(where: str | None, level: int) -> bool:
    """Whether an effect kept for `where` ("all", "2" or "1+") reaches
    `level`."""
    if not where or where == "all":
        return True
    if where.endswith("+"):
        return level >= whole_number(where[:-1])
    return level == whole_number(where)


def aura_at(place: Neighbour, level: int = 0) -> tuple[int, str]:
    """The aura and its realm at `level` of `place`: the surface's or the
    level's, unless an aura effect there replaces it."""
    shown = levels(place)
    if 0 < level <= len(shown):
        entry = shown[level - 1]
        aura, realm = whole_number(entry.get("aura")), realm_of(entry.get("realm"))
    else:
        aura, realm = whole_number(place.details.get("aura")), realm_of(place.realm)
    for effect in effects(place):
        if effect.get("what") == "aura" and _reaches(effect.get("where"), level):
            aura, realm = (
                whole_number(effect.get("amount")),
                realm_of(effect.get("target"), realm),
            )
    return aura, realm


def lab_place(saga: Saga, lab: Laboratory) -> tuple[Neighbour, int] | None:
    """Where a laboratory is: its own place, or its covenant's."""
    found = place(saga, lab.place_id)
    if found is not None:
        return found, lab.place_level
    covenant = saga.covenant(lab.covenant_id)
    return covenant_place(saga, covenant) if covenant is not None else None


def covenant_place(saga: Saga, covenant: Covenant) -> tuple[Neighbour, int] | None:
    found = place(saga, covenant.place_id)
    return (found, covenant.place_level) if found is not None else None


def character_place(saga: Saga, character: Character) -> tuple[Neighbour, int] | None:
    """Where a character lives: their covenant's place."""
    covenant = saga.covenant(character.covenant_id)
    return covenant_place(saga, covenant) if covenant is not None else None


def lab_aura(saga: Saga, lab: Laboratory) -> tuple[int, str] | None:
    """The aura of a laboratory placed somewhere of its own (a lab built
    in a regio); None when it takes its covenant's."""
    found = place(saga, lab.place_id)
    return aura_at(found, lab.place_level) if found is not None else None


@dataclass(frozen=True)
class _Entry:
    """A place's effect as a catalog entry, for rules.effects."""

    id: str
    name: str
    type: str
    modifiers: list[Modifier] = field(default_factory=list)


def source(where: tuple[Neighbour, int] | None) -> fx.EffectSource:
    """The effects that reach `where` (a place and level), as a source
    for the shared effect lookup; an empty one for nowhere."""
    if where is None:
        return fx.EffectSource("place", [], {})
    found, level = where
    instances: list[VirtueFlawInstance] = []
    catalog: dict[str, _Entry] = {}
    for index, effect in enumerate(effects(found)):
        what = effect.get("what")
        if what not in EFFECT_TYPES or what == "aura":
            continue
        if not _reaches(effect.get("where"), level):
            continue
        amount = whole_number(effect.get("amount"))
        key = f"{found.id}#{index}"
        catalog[key] = _Entry(
            key,
            found.name,
            "Virtue" if amount >= 0 else "Flaw",
            [Modifier(what, amount=amount, target=effect.get("target") or None)],
        )
        instances.append(VirtueFlawInstance(key))
    return fx.EffectSource("place", instances, catalog)


def lab_source(saga: Saga, lab: Laboratory) -> fx.EffectSource:
    return source(lab_place(saga, lab))


def character_effects(
    saga: Saga | None, character: Character, applies_to: str
) -> list[fx.Effect]:
    """The effects of type `applies_to` from where `character` lives."""
    if saga is None:
        return []
    return fx.collect([source(character_place(saga, character))], applies_to)


def warping_per_year(saga: Saga, character: Character) -> int:
    """The Warping Points a year where `character` lives gives: its
    Warping a season, four times."""
    found = character_effects(saga, character, "warping_per_season")
    return 4 * int(fx.amount_total(found))
