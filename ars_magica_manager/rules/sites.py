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
    Character,
    Covenant,
    CovenantStop,
    Laboratory,
    Modifier,
    Neighbour,
    Possession,
    Saga,
    VirtueFlawInstance,
    details_list,
)
from . import aura_kinds, lunar, mobile, otherworlds
from . import effects as fx

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Regiones, pp. "
    "420-422; Realms of Power: The Divine pp. 13-15; Realms of Power: The "
    "Infernal pp. 16-17; Realms of Power: Magic p. 20; Realms of Power: "
    "Faerie p. 16"
)

#: The kind of neighbour a place is.
PLACE = "place"
#: The details that say which covenant a Place travels with (its id), and
#: what it offers ships (rules.mobile.WATERS).
TRAVELS_WITH, WATERS = "travels_with", "waters"


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
    """A level of a regio: its realm and aura, its kind (REGIO_KINDS), and
    what it takes to see and to enter it."""

    name: str
    realm: str
    aura: int
    kind: str
    see: str
    enter: str
    notes: str
    #: The aura's own kind, by its realm (aura_kinds.KIND_KEYS).
    alignment: str
    tints: str
    divine_kind: str
    #: The realm it lies in, when not the mundane world
    #: (otherworlds.WORLDS), and in the Magic Realm its boundary's level.
    world: str
    boundary: int


#: The kinds of regio a realm's books describe: the Divine's terrestrial
#: and celestial regiones (RoP: The Divine pp. 13-15), the Infernal's
#: Tartaran and Abyssal ones (RoP: The Infernal pp. 16-17).
REGIO_KINDS: dict[str, tuple[str, ...]] = {
    "Divine": ("Terrestrial", "Celestial"),
    "Infernal": ("Tartaran", "Abyssal"),
}
REGIO_KIND_SOURCE = (
    "Realms of Power: The Divine, Divine Regiones, pp. 13-15; Realms of "
    "Power: The Infernal, Infernal Regiones, pp. 16-17"
)


def regio_kind(entry: RegioLevel) -> str:
    """The level's kind, when its realm has one by that name ("" if not)."""
    kind = str(entry.get("kind") or "")
    return kind if kind in REGIO_KINDS.get(realm_of(entry.get("realm")), ()) else ""


def celestial_ease(aura: int) -> int:
    """The Ease Factor of a Stamina + Dominion Lore (or Parma Magica, if
    better) roll to act normally in a celestial regio: three times its
    rating; failing, every roll there takes as much as a penalty, and a
    Faith Point spent ignores it (RoP: The Divine pp. 14-15)."""
    return 3 * max(0, aura)


def kind_effects(entry: RegioLevel) -> str:
    """What a regio level does to visitors by its realm and kind, as the
    books give it ("" for one with no rule of its own). Every Infernal
    regio suspends Divine powers; Tartaran and Abyssal ones add their own."""
    aura = max(0, whole_number(entry.get("aura")))
    realm, kind = realm_of(entry.get("realm")), regio_kind(entry)
    if kind == "Celestial":
        ease = celestial_ease(aura)
        return (
            f"to act there, Sta + Dominion Lore (or Parma) against {ease}, or "
            f"-{ease} to every roll (a Faith Point ignores it); after Sta + "
            f"Parma + 3 hours, a Fatigue level an hour, then {aura} Warping "
            "an hour (days, not hours, with True Faith)"
        )
    if realm != "Infernal":
        return ""
    found = (
        "no invoking God, Intercession or Holy Influence; Holy Powers and "
        f"Holy Magic at -{aura}"
    )
    if kind == "Tartaran":
        found += (
            "; all Fatigue is long-term until they leave; hell-fire does +5 "
            "to +35, more by the sum of the victim's sinful traits"
        )
    elif kind == "Abyssal":
        found += (
            f"; every Characteristic -{aura} while there; each day an Int "
            f"roll against {aura} or a madness Flaw"
        )
    return found


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
    names none. An aura may be Lunar (Dies Irae p. 36), so Lunar counts."""
    found = next(
        (r for r in lunar.REALMS if r.casefold() == str(value or "").casefold()), ""
    )
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
    world = otherworlds.world_of(_details_at(place, level).get("world"))
    if world is not None:
        aura, realm = world.aura, world.realm
        if world.name == otherworlds.MAGIC_REALM:
            aura = otherworlds.realm_aura(boundary_at(place, level))
    for effect in effects(place):
        if effect.get("what") == "aura" and _reaches(effect.get("where"), level):
            aura, realm = (
                whole_number(effect.get("amount")),
                realm_of(effect.get("target"), realm),
            )
    return aura, realm


def _details_at(place: Neighbour, level: int) -> dict[str, Any]:
    """The details kept for `level` of `place`: the level's own, or the
    place's for the surface."""
    shown = levels(place)
    return cast(
        dict[str, Any], shown[level - 1] if 0 < level <= len(shown) else place.details
    )


def world_at(place: Neighbour, level: int = 0) -> str:
    """The realm `level` of `place` lies in (otherworlds.WORLDS), "" for
    the mundane world."""
    found = otherworlds.world_of(_details_at(place, level).get("world"))
    return found.name if found is not None else ""


def boundary_at(place: Neighbour, level: int = 0) -> int:
    """The level of the Magic Realm boundary `level` of `place` lies in (0
    elsewhere)."""
    if world_at(place, level) != otherworlds.MAGIC_REALM:
        return 0
    return otherworlds.boundary_level(_details_at(place, level).get("boundary"))


def aura_kind_at(place: Neighbour, level: int = 0) -> str:
    """The kind of the aura at `level` of `place` (its alignment, tints or
    Divine kind, aura_kinds.KIND_KEYS), read by the realm the aura has
    there; "" for none. In the Magic Realm the alignment is the
    boundary's Form, and counts only while there is a boundary to add
    again (RoP: Magic p. 22)."""
    _, realm = aura_at(place, level)
    details = _details_at(place, level)
    if world_at(place, level) == otherworlds.MAGIC_REALM:
        form = otherworlds.boundary_form(details.get(aura_kinds.KIND_KEYS["Magic"]))
        return form if boundary_at(place, level) and realm == "Magic" else ""
    return aura_kinds.kind_of(details, realm)


def kind_where(saga: Saga, where: tuple[Neighbour, int] | None) -> str:
    """The kind of the aura holding sway at a place and level (from
    lab_place, character_place...); "" for nowhere."""
    return aura_kind_at(*holding(saga, where)) if where is not None else ""


def travels(found: Neighbour) -> bool:
    """Whether a Place travels with a covenant (own aura or regio): each
    stop moves it inside the stop's Place."""
    return bool(found.details.get(TRAVELS_WITH))


def travelling_places(saga: Saga, covenant: Covenant) -> list[Neighbour]:
    """The Places that travel with `covenant`."""
    return [p for p in all_places(saga) if p.details.get(TRAVELS_WITH) == covenant.id]


def waters_of(found: Neighbour) -> str:
    """What a Place offers ships (rules.mobile.WATERS); "" for not said."""
    return str(found.details.get(WATERS) or "")


def covenant_stop(saga: Saga, covenant: Covenant) -> CovenantStop | None:
    """The covenant's stop in force at the saga's date."""
    return mobile.stop_in_force(covenant.stops, saga.current_year, saga.current_season)


def _stop_place(saga: Saga, stop: CovenantStop | None) -> tuple[Neighbour, int] | None:
    if stop is None:
        return None
    found = place(saga, stop.place_id)
    return (found, stop.level) if found is not None else None


def ship_stop(saga: Saga, record: Possession) -> tuple[Neighbour, int] | None:
    """Where a ship apart from the fleet is: her stop in force; None for a
    ship sailing with it."""
    ship = record.ship
    if ship is None:
        return None
    return _stop_place(
        saga, mobile.stop_in_force(ship.stops, saga.current_year, saga.current_season)
    )


def ship_with_lab(saga: Saga, lab: Laboratory) -> Possession | None:
    """The ship of its covenant that carries `lab`, if one does."""
    covenant = saga.covenant(lab.covenant_id)
    if covenant is None:
        return None
    return next(
        (p for p in covenant.possessions if p.ship is not None and p.lab_id == lab.id),
        None,
    )


def ship_aboard(saga: Saga, character: Character) -> Possession | None:
    """The ship apart from the fleet that `character` went with, if any."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return None
    return next(
        (
            p
            for p in covenant.possessions
            if p.ship is not None and p.ship.stops and character.id in p.ship.aboard
        ),
        None,
    )


def lab_ship_place(saga: Saga, lab: Laboratory) -> tuple[Neighbour, int] | None:
    """Where the ship carrying `lab` is, while she is apart from the
    fleet."""
    record = ship_with_lab(saga, lab)
    return ship_stop(saga, record) if record is not None else None


def lab_place(saga: Saga, lab: Laboratory) -> tuple[Neighbour, int] | None:
    """Where a laboratory is: aboard a ship apart from the fleet, its own
    place, or its covenant's."""
    apart = lab_ship_place(saga, lab)
    if apart is not None:
        return apart
    found = place(saga, lab.place_id)
    if found is not None:
        return found, lab.place_level
    covenant = saga.covenant(lab.covenant_id)
    return covenant_place(saga, covenant) if covenant is not None else None


def covenant_place(saga: Saga, covenant: Covenant) -> tuple[Neighbour, int] | None:
    """Where a covenant is now: a Place that travels with it, wherever
    that has got to; else its stop in force; else its own place."""
    own = place(saga, covenant.place_id)
    if own is not None and own.details.get(TRAVELS_WITH) == covenant.id:
        return own, covenant.place_level
    return _stop_place(saga, covenant_stop(saga, covenant)) or (
        (own, covenant.place_level) if own is not None else None
    )


def covenants_at(saga: Saga, found: Neighbour) -> list[Covenant]:
    """The covenants at `found` now."""
    return [
        c
        for c in saga.covenants
        if (where := covenant_place(saga, c)) is not None and where[0].id == found.id
    ]


def character_place(saga: Saga, character: Character) -> tuple[Neighbour, int] | None:
    """Where a character lives: aboard a ship apart from the fleet, or
    their covenant's place."""
    record = ship_aboard(saga, character)
    apart = ship_stop(saga, record) if record is not None else None
    if apart is not None:
        return apart
    covenant = saga.covenant(character.covenant_id)
    return covenant_place(saga, covenant) if covenant is not None else None


def holding(saga: Saga, where: tuple[Neighbour, int]) -> tuple[Neighbour, int]:
    """Whose aura holds sway at a place and level. On the surface of a
    Place travelling with a covenant, the stronger of its own and the
    aura of the Place around it, and a tie keeps its own (DE p. 410, the
    stronger realm); inside its regio, and at any fixed Place, its own."""
    found, level = where
    around = place(saga, found.place_id)
    if level or around is None or not travels(found):
        return where
    theirs = aura_at(around, found.place_level)[0]
    return (around, found.place_level) if theirs > aura_at(found)[0] else where


def aura_here(saga: Saga, found: Neighbour, level: int = 0) -> tuple[int, str]:
    """The aura that holds sway at `level` of `found`, and its realm."""
    return aura_at(*holding(saga, (found, level)))


def boundary_botch_dice(saga: Saga, found: tuple[Neighbour, int] | None) -> int:
    """The extra botch dice a Magic Realm boundary adds, at a place and
    level, to every roll the Magic aura helps: its level, while the aura
    there is Magic (RoP: Magic p. 22); 0 elsewhere or for no place."""
    if found is None:
        return 0
    where, level = holding(saga, found)
    if aura_at(where, level)[1] != "Magic":
        return 0
    return otherworlds.boundary_botch_dice(boundary_at(where, level))


def character_boundary_botch_dice(saga: Saga, character: Character) -> int:
    """A boundary's botch dice where the character lives (their covenant's
    place), for the rolls their home aura helps, such as casting."""
    return boundary_botch_dice(saga, character_place(saga, character))


def lab_boundary_botch_dice(saga: Saga, lab: Laboratory) -> int:
    """A boundary's botch dice where `lab` stands: its own place, else its
    covenant's."""
    return boundary_botch_dice(saga, lab_place(saga, lab))


def lab_aura(saga: Saga, lab: Laboratory) -> tuple[int, str] | None:
    """The aura of a laboratory placed somewhere of its own (a lab built
    in a regio, or aboard a ship apart from the fleet); None when it takes
    its covenant's."""
    apart = lab_ship_place(saga, lab)
    if apart is not None:
        return aura_here(saga, *apart)
    found = place(saga, lab.place_id)
    return aura_here(saga, found, lab.place_level) if found is not None else None


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
