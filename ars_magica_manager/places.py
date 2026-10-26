"""Places and regiones: a Place is a neighbour of the kind "place" that
other records sit in. A place can sit inside another (a regio inside a
forest inside a county), and a neighbour, a covenant or a laboratory can
name the place it is in, and which of its levels.

A place's own aura is its mundane level's (the surface). A regio is a
place with levels above the surface, each with its own name, realm and
aura, the roll it takes to see it and to enter it, and notes. A level's
roll, written "Per + Awareness against 9", is checked against the player
covenants' characters' scores to say who can see or enter it without a
die.

A place's effects use the Modifier the Virtues use, so they reach the
totals with no new maths: a lab bonus reaches the Lab Totals of the labs
placed there, an aging or Living Conditions change the aging rolls of
those who live there (a covenant's characters), Warping a season the
yearly Warping, and an aura effect replaces the aura of its level.

A covenant placed somewhere takes its aura from the place (sync); the
aura typed on the covenant is kept, and comes back if it is moved out.

A place may be marked a ruined covenant (a fallen covenant's site,
ruins.py): it shows a ruin, and can be founded anew.

Kept in Neighbour.details: "ruined", "aura", "tethers", "status", "known",
"claimed_by", the aura's kind by its realm ("alignment", "tints" or
"divine_kind", rules.aura_kinds), "levels" (each {"name", "realm", "aura",
"kind", "see", "enter", "notes"} and its aura's kind), the first being Level 1, just above the surface) and "effects"
(each {"what", "amount", "target", "where", "note"}). Where a record is:
its place_id and place_level (0 for the surface).

Pattern: Composite (places in places, walked by inside_of and
within); an effect is a Modifier value, collected by rules.effects like
any Virtue's."""

from __future__ import annotations

import re
from collections.abc import Callable, Collection, Iterator, Mapping
from dataclasses import dataclass
from typing import Any

from . import references
from .commands import SectionOps
from .form_spec import DialogField, pairs
from .grids import Grid
from .markup import escape
from .models import (
    REALMS,
    Character,
    Neighbour,
    Saga,
)
from .neighbour_lists import KindList, list_ops
from .references import Fact
from .rules import aura_kinds, senses
from .rules.sites import (
    EFFECT_TYPES,
    PLACE,
    REGIO_KINDS,
    AuraEffect,
    RegioLevel,
    all_places,
    aura_at,
    aura_kind_at,
    effects,
    is_place,
    kind_effects,
    levels,
    place,
    realm_of,
    regio_kind,
    whole_number,
)
from .sections import EFFECTS_SECTION, LEVELS_SECTION

#: How far the troupe has got with a place, and how widely it is known.
STATUS: tuple[str, ...] = ("Rumoured", "Known", "Visited", "Claimed")
KNOWN: tuple[str, ...] = ("Locally", "In the region", "In the Tribunal", "In the Order")

SURFACE = "Surface"

#: The detail that marks a place as a ruined covenant.
RUINED = "ruined"


#: Each Characteristic, by the names a roll may use.
_CHARACTERISTICS: dict[str, str] = {}
for _name in (
    "intelligence",
    "perception",
    "strength",
    "stamina",
    "presence",
    "communication",
    "dexterity",
    "quickness",
):
    _CHARACTERISTICS[_name] = _name
    _CHARACTERISTICS[_name[:3]] = _name
_CHARACTERISTICS["qik"] = "quickness"


# -- the record --


def is_ruin(record: object) -> bool:
    """Whether `record` is a place marked as a ruined covenant: a fallen
    covenant's site, which shows a ruin and can be founded anew."""
    return (
        isinstance(record, Neighbour)
        and record.kind == PLACE
        and bool(record.details.get(RUINED))
    )


# -- nesting --


def inside_of(saga: Saga, record: Neighbour) -> Iterator[Neighbour]:
    """The places `record` sits in, nearest first (each once)."""
    seen = {record.id}
    above = place(saga, record.place_id)
    while above is not None and above.id not in seen:
        yield above
        seen.add(above.id)
        above = place(saga, above.place_id)


def inside_text(saga: Saga, record: Neighbour) -> str:
    """ "The Siebengebirge, inside the County of Berg": where a place
    sits, outward (its level in the nearest named); "" for nowhere."""
    chain = list(inside_of(saga, record))
    if not chain:
        return ""
    nearest = where_text(saga, record.place_id, record.place_level)
    return ", inside ".join([nearest, *(p.name for p in chain[1:])])


def within(saga: Saga, outer: Neighbour) -> set[str]:
    """The ids of every place inside `outer`, however deep."""
    return {p.id for p in all_places(saga) if outer in inside_of(saga, p)}


def here_records(saga: Saga, outer: Neighbour) -> list[Any]:
    """The records placed in `outer`, places last."""
    found: list[Any] = [c for c in saga.covenants if c.place_id == outer.id]
    found += [lab for lab in saga.laboratories if lab.place_id == outer.id]
    found += [n for n in saga.neighbours if n.place_id == outer.id and not is_place(n)]
    found += [c for c in saga.creatures if c.place_id == outer.id]
    return found + [p for p in all_places(saga) if p.place_id == outer.id]


def here(saga: Saga, outer: Neighbour) -> list[str]:
    """The names of the records placed in `outer`, places last."""
    return [record.name for record in here_records(saga, outer)]


# -- where a record is --


def level_name(place: Neighbour, level: int) -> str:
    """ "Level 2: The Vine Terraces", or "Surface"."""
    shown = levels(place)
    if level <= 0 or level > len(shown):
        return SURFACE
    name = shown[level - 1].get("name") or ""
    return f"Level {level}: {name}" if name else f"Level {level}"


def where_value(place_id: str | None, level: int = 0) -> str | None:
    """A place and level as one choice's value: "drachenfels@2"."""
    if place_id is None:
        return None
    return f"{place_id}@{level}" if level else place_id


def split(value: str | None) -> tuple[str | None, int]:
    if not value:
        return None, 0
    found, _, level = value.partition("@")
    return found, whole_number(level)


def where_text(saga: Saga, place_id: str | None, level: int = 0) -> str:
    """ "The Drachenfels, Level 2: The Vine Terraces"; "" for nowhere."""
    found = place(saga, place_id)
    if found is None:
        return ""
    if level <= 0:
        return found.name
    return f"{found.name}, {level_name(found, level)}"


def where_options(saga: Saga, leave_out: Collection[str] = ()) -> list[tuple[str, str]]:
    """Each place and each of its levels, as a choice."""
    options: list[tuple[str, str]] = []
    for found in all_places(saga):
        if found.id in leave_out:
            continue
        options.append((escape(found.name), found.id))
        for level in range(1, len(levels(found)) + 1):
            options.append(
                (
                    escape(f"{found.name}, {level_name(found, level)}"),
                    f"{found.id}@{level}",
                )
            )
    return options


def where_field(
    saga: Saga,
    record: Any,
    label: str = "Place",
    hint: str = "",
    leave_out: Collection[str] = (),
) -> DialogField:
    """The field that places `record`: a place, or one of its levels."""
    return DialogField(
        "where",
        label,
        "select",
        where_value(record.place_id, record.place_level) if record else None,
        options=where_options(saga, leave_out),
        allow_blank=True,
        placeholder="(nowhere entered)",
        hint=hint,
    )


def put(record: Any, value: str | None) -> None:
    """Place `record` where the field `where_field` chose."""
    record.place_id, record.place_level = split(value)


# -- auras --


def aura_text(place: Neighbour, level: int = 0) -> str:
    aura, realm = aura_at(place, level)
    return f"{realm} {aura}"


def sync(saga: Saga) -> None:
    """Give each placed covenant its place's aura, keeping the one typed
    on it; restore that one when it is no longer placed. Records placed
    somewhere since deleted are placed nowhere."""
    for record in [
        *saga.covenants,
        *saga.laboratories,
        *saga.neighbours,
        *saga.creatures,
    ]:
        if record.place_id is not None and place(saga, record.place_id) is None:
            record.place_id, record.place_level = None, 0
    for covenant in saga.covenants:
        found = place(saga, covenant.place_id)
        if found is not None:
            if covenant.own_aura is None:
                covenant.own_aura = covenant.aura
                covenant.own_realm = covenant.aura_realm
            covenant.aura, covenant.aura_realm = aura_at(found, covenant.place_level)
        elif covenant.own_aura is not None:
            covenant.aura = covenant.own_aura
            covenant.aura_realm = covenant.own_realm or "Magic"
            covenant.own_aura, covenant.own_realm = None, ""


# -- effects, as the totals collect them --


# -- who can see or enter a level --


_ROLL = re.compile(
    r"^\s*([a-z]+)\s*\+\s*(.+?)\s+(?:against|vs\.?)\s+(\d+)\s*$", re.IGNORECASE
)


@dataclass(frozen=True)
class Roll:
    """A roll written "Per + Awareness against 9"."""

    characteristic: str
    ability: str
    against: int


def parse_roll(words: str) -> Roll | None:
    """The roll `words` names, or None for a sentence."""
    found = _ROLL.match(words or "")
    if found is None:
        return None
    characteristic = _CHARACTERISTICS.get(found.group(1).casefold())
    if characteristic is None:
        return None
    return Roll(characteristic, found.group(2).strip(), int(found.group(3)))


def roll_total(character: Character, roll: Roll) -> int:
    from .rules.lab import ability_score

    ability = next(
        (
            a.name
            for a in character.abilities
            if a.name.casefold() == roll.ability.casefold()
        ),
        roll.ability,
    )
    score, bonus = ability_score(character, ability)
    return getattr(character.characteristics, roll.characteristic) + score + bonus


def who_can(saga: Saga, words: str) -> list[tuple[str, int]]:
    """The player covenants' characters whose score reaches the roll
    `words` names without a die, best first; [] for a sentence."""
    roll = parse_roll(words)
    if roll is None:
        return []
    played = {c.id for c in saga.covenants if c.played}
    found = [
        (c.name, roll_total(c, roll))
        for c in saga.characters
        if c.covenant_id in played
    ]
    return sorted(
        ((name, total) for name, total in found if total >= roll.against),
        key=lambda pair: -pair[1],
    )


def who_can_text(saga: Saga, words: str) -> str:
    if parse_roll(words) is None:
        return ""
    found = who_can(saga, words)
    return ", ".join(f"{name} ({total})" for name, total in found) or "no one yet"


# -- facts --


def facts(saga: Saga, place: Neighbour) -> list[Fact]:
    d = place.details
    claimed = saga.covenant(d.get("claimed_by"))
    status = ", ".join(
        s.lower() if i else s
        for i, s in enumerate(x for x in (d.get("status"), d.get("known")) if x)
    )
    found = here_records(saga, place)
    shown = levels(place)
    regio = f"{len(shown)} level{'' if len(shown) == 1 else 's'}" if shown else "none"
    seen = [
        f"Level {index}: {who_can_text(saga, entry.get('see', ''))}"
        for index, entry in enumerate(shown, start=1)
        if parse_roll(entry.get("see", "")) is not None
    ]
    hazards = [
        f"Level {index}: {text}"
        for index, entry in enumerate(shown, start=1)
        if (
            text := "; ".join(
                t for t in (kind_effects(entry), level_kind_text(place, index)) if t
            )
        )
    ]
    kind = level_kind_text(place, 0)
    return [
        Fact("Aura", aura_text(place)),
        *([Fact("Aura kind", kind)] if kind else []),
        Fact("Regio", regio),
        *([Fact("Can see", "; ".join(seen))] if seen else []),
        *([Fact("Within", "; ".join(hazards))] if hazards else []),
        Fact("Gazetteer", status),
        Fact(
            "Claimed by",
            claimed.name if claimed is not None else "",
            references.refs(claimed),
        ),
        Fact("Tethers", d.get("tethers", "")),
        Fact("Here", ", ".join(r.name for r in found), references.refs(*found)),
    ]


def level_kind_text(place: Neighbour, level: int) -> str:
    """What the aura's kind does at `level` (0 for the surface), as the
    facts say it; "" for none."""
    aura, realm = aura_at(place, level)
    if not aura_kind_at(place, level):
        return "" if realm != "Divine" else aura_kinds.divine_effects("", aura)
    shown = levels(place)
    details = shown[level - 1] if 0 < level <= len(shown) else place.details
    return aura_kinds.effects_text(dict(details), realm, aura)


# -- the form --


def realm_is(realm: str) -> Callable[[dict[str, Any]], bool]:
    """A show_if for fields of one realm's rule, read from the form's Realm
    (the place's realm while the form has none)."""
    return lambda values: (values.get("realm") or "Magic") == realm


def kind_fields(d: Mapping[str, Any]) -> list[DialogField]:
    """An aura's kind, asked by its realm: a Magic aura's alignment, a
    Faerie one's tints, a Divine one's source (rules.aura_kinds)."""
    keys = aura_kinds.KIND_KEYS
    return [
        DialogField(
            keys["Magic"],
            "Alignment",
            "text",
            d.get(keys["Magic"], ""),
            placeholder="e.g. Ignem, Healing, Luck, Fearful",
            hint="At most one: an Art (its spells and lab work take the aura "
            "again), Healing, Luck, Distracting, or a feeling those without "
            "The Gift take on (RoP: Magic pp. 15-16).",
            show_if=realm_is("Magic"),
        ),
        DialogField(
            keys["Faerie"],
            "Tints",
            "text",
            d.get(keys["Faerie"], ""),
            placeholder="e.g. Drawn to Children +3; Light +2",
            hint="Personality Traits everyone here takes, none above the "
            "aura (RoP: Faerie p. 104).",
            show_if=realm_is("Faerie"),
        ),
        DialogField(
            keys["Divine"],
            "Divine aura",
            "select",
            d.get(keys["Divine"]) or aura_kinds.DOMINION,
            options=pairs(aura_kinds.DIVINE_KINDS),
            hint="The Dominion comes from worship; an Empyreal aura from a "
            "relic, saint, miracle or holy creature. Both wane at night and "
            "wax on holy days (RoP: The Divine pp. 7, 12).",
            show_if=realm_is("Divine"),
        ),
    ]


def fields(saga: Saga, place: Neighbour | None) -> list[DialogField]:
    """What New Place and Edit add to the common fields."""
    d = place.details if place is not None else {}
    return [
        DialogField(
            RUINED,
            "Ruined covenant",
            "check",
            bool(d.get(RUINED)),
            hint="A fallen covenant's site: it shows a ruin, and Found a "
            "Covenant Here (More) raises a new one on it.",
        ),
        DialogField(
            "aura",
            "Aura",
            "int",
            d.get("aura", 0),
            hint="Its surface's aura; its realm is the Realm below.",
        ),
        *kind_fields(d),
        DialogField(
            "tethers",
            "Tethers",
            "text",
            d.get("tethers", ""),
            placeholder="e.g. The dragon's bones, an Ignem source",
            hint="With Auras change on, end each with (natural 1-2) or "
            "(preternatural 1-5) to give its base aura (RoP: Magic p. 8).",
        ),
        DialogField(
            "status",
            "Status",
            "select",
            d.get("status") or None,
            options=pairs(STATUS),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField(
            "known",
            "Known",
            "select",
            d.get("known") or None,
            options=pairs(KNOWN),
            allow_blank=True,
            placeholder="(not said)",
        ),
        DialogField(
            "claimed_by",
            "Claimed by",
            "select",
            d.get("claimed_by"),
            options=[(escape(c.name), c.id) for c in saga.covenants],
            allow_blank=True,
            placeholder="(no one)",
        ),
    ]


def problem(values: dict[str, Any]) -> str | None:
    if (values.get("aura") or 0) < 0:
        return "An aura can't be below 0."
    return aura_kinds.problem(values)


# -- regio levels --


def levels_title(_saga: Saga, place: Neighbour) -> str:
    return f"Regio Levels ({len(levels(place))})"


def levels_grid(saga: Saga, place: Neighbour) -> Grid:
    """Each level, deepest first (the surface's aura is the place's own):
    its aura, the Ease Factor to see into it from the level below (its own
    roll's, else the book's, DE p. 421), how to enter it, and who can enter
    it without a die (who can see it is among the place's facts)."""
    shown = levels(place)
    rows = []
    keys: list[int | None] = []  # deepest first, so each row's own index
    for index in reversed(range(len(shown))):
        entry = shown[index]
        kind = regio_kind(entry)
        rows.append(
            [
                f"Level {index + 1}",
                f"{entry.get('name', '')} ({kind.lower()})"
                if kind
                else entry.get("name", ""),
                aura_text(place, index + 1),
                see_in_text(place, index + 1),
                entry.get("enter", ""),
                who_can_text(saga, entry.get("enter", "")),
            ]
        )
        keys.append(index)
    return Grid(
        ["Level", "Name", "Aura", "See", "To enter", "Can enter"],
        rows,
        keys,
        "No regio: add its levels, from just above the surface upward.",
        caps=[7, 18, 9, 5, 14, 0],
        stretch=4,
    )


def see_in_text(place: Neighbour, level: int) -> str:
    """The Ease Factor to see into `level` from the one below: the level's
    own roll's when it names one, else the book's from the two auras."""
    own = parse_roll(levels(place)[level - 1].get("see", ""))
    if own is not None:
        return str(own.against)
    below_aura, below_realm = aura_at(place, level - 1)
    aura, realm = aura_at(place, level)
    return f"{senses.regio_sight_ease(below_aura, below_realm, aura, realm)} DE"


def level_fields(
    _saga: Saga, place: Neighbour, entry: RegioLevel | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField("name", "Name", "text", e.get("name", ""), required=True),
        DialogField(
            "realm",
            "Realm",
            "select",
            e.get("realm") or place.realm or "Magic",
            options=pairs(REALMS),
            required=True,
        ),
        DialogField(
            "aura",
            "Aura",
            "int",
            e.get("aura", whole_number(place.details.get("aura")) + 1),
        ),
        *kind_fields(e),
        DialogField(
            "kind",
            "Kind",
            "select",
            e.get("kind", ""),
            options=[("None", "")]
            + [
                (f"{kind} ({realm})", kind)
                for realm, kinds in REGIO_KINDS.items()
                for kind in kinds
            ],
            hint="A Divine regio is terrestrial or celestial (RoP: The Divine "
            "p. 13), an Infernal one Tartaran or Abyssal (RoP: The Infernal "
            "p. 16); a kind not of its realm is ignored.",
        ),
        DialogField(
            "see",
            "To see it",
            "text",
            e.get("see", ""),
            placeholder="e.g. Per + Awareness against 9",
            hint='A roll ("Per + Awareness against 9") says who can; or a sentence.',
        ),
        DialogField(
            "enter",
            "To enter it",
            "text",
            e.get("enter", ""),
            placeholder="e.g. walk the ring backward at dusk",
        ),
        DialogField("notes", "Notes", "text", e.get("notes", "")),
    ]


def _level_problem(values: dict[str, Any]) -> str | None:
    if (values.get("aura") or 0) < 0:
        return "An aura can't be below 0."
    return aura_kinds.problem(values)


def level_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        place,
        "levels",
        "Regio Level",
        level_fields,
        lambda e: e.get("name") or "the level",
        validate=_level_problem,
        after=lambda: sync(saga),
    )


# -- effects --


def where_choices(place: Neighbour) -> list[tuple[str, str]]:
    choices = [("Every level", "all"), (SURFACE, "0")]
    count = len(levels(place))
    for level in range(1, count + 1):
        choices.append((f"Level {level}", str(level)))
        if level < count:
            choices.append((f"Level {level} and up", f"{level}+"))
    return choices


def _where_label(place: Neighbour, where: str | None) -> str:
    found = {value: label for label, value in where_choices(place)}
    return found.get(where or "all") or str(where or "")


def amount_text(effect: AuraEffect) -> str:
    what = effect.get("what")
    amount = whole_number(effect.get("amount"))
    target = effect.get("target") or ""
    if what == "aura":
        return f"{realm_of(target)} {amount}"
    text = f"{amount:+d}"
    if what == "warping_per_season":
        return f"{text} a season"
    return f"{text} {target}".strip()


def effects_title(_saga: Saga, place: Neighbour) -> str:
    return f"Effects ({len(effects(place))})"


def effects_grid(_saga: Saga, place: Neighbour) -> Grid:
    rows = []
    for effect in effects(place):
        kind = EFFECT_TYPES.get(effect.get("what") or "")
        rows.append(
            [
                kind.name if kind is not None else str(effect.get("what")),
                amount_text(effect),
                _where_label(place, effect.get("where")),
                kind.reaches if kind is not None else "",
                effect.get("note", ""),
            ]
        )
    return Grid(
        ["Effect", "Amount", "Where", "Applies to", "Note"],
        rows,
        list(range(len(rows))),
        "No effects: a lab bonus, Warping, an aging change or an aura that "
        "replaces a level's.",
        caps=[17, 12, 14, 15, 0],
        stretch=4,
    )


def effect_fields(
    _saga: Saga, place: Neighbour, entry: AuraEffect | None
) -> list[DialogField]:
    e = entry or {}
    return [
        DialogField(
            "what",
            "Effect",
            "select",
            e.get("what", "lab_total"),
            options=[(t.name, t.key) for t in EFFECT_TYPES.values()],
            required=True,
        ),
        DialogField(
            "amount",
            "Amount",
            "int",
            e.get("amount", 1),
            hint="Added to the total; Warping a season; for the aura, the new aura.",
        ),
        DialogField(
            "target",
            "Art or realm",
            "text",
            e.get("target", ""),
            placeholder="e.g. Herbam",
            hint="For lab totals, the Art it helps (blank for all); for the "
            "aura, its realm.",
        ),
        DialogField(
            "where",
            "Where",
            "select",
            e.get("where", "all"),
            options=where_choices(place),
            required=True,
        ),
        DialogField("note", "Note", "text", e.get("note", "")),
    ]


def _effect_problem(values: dict[str, Any]) -> str | None:
    target = (values.get("target") or "").strip()
    if values.get("what") == "aura":
        if (values.get("amount") or 0) < 0:
            return "An aura can't be below 0."
        if target and realm_of(target, "") == "":
            return f"The aura's realm is one of {', '.join(REALMS)}."
    if values.get("what") == "lab_total" and target:
        from .arts import ARTS

        if target.casefold() not in (a.casefold() for a in ARTS):
            return "Name an Art for a lab bonus, or leave it blank for every one."
    return None


def effect_ops(saga: Saga, place: Neighbour) -> SectionOps:
    return list_ops(
        saga,
        place,
        "effects",
        "Effect",
        effect_fields,
        lambda e: f"the {amount_text(e)} effect",
        validate=_effect_problem,
        after=lambda: sync(saga),
    )


#: The lists on a place's Regio tab (place_events adds its triggers).
LISTS = (
    KindList(LEVELS_SECTION, levels_title, levels_grid, level_ops),
    KindList(EFFECTS_SECTION, effects_title, effects_grid, effect_ops),
)
