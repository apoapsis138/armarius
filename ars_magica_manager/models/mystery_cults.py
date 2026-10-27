"""A saga's own Mystery Cults (The Mysteries Revised Edition pp. 13-19,
Inventing Your Own Cult pp. 18-19): the cult, its Lore, its degrees, each
teaching one Mystery Virtue, and the Initiation Script of each degree,
written out as its components (pp. 15-16).

The saga keeps them (Saga.custom_cults). Each is offered as a tradition of
the tradition catalog (as_tradition), so the Initiation season lists its
Scripts beside the catalog's cults, and its Lore as an Ability of the
Ability catalog (lore_ability), as the saga's own Virtues join theirs.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from .common import known_fields
from .definitions import (
    TRADITION_REALMS,
    AbilityDef,
    InitiationRule,
    InitiationScript,
    TraditionDef,
    VirtueFlawDef,
)
from .world import Attitude

#: A saga cult's id starts with this, which tells it from the catalog's.
SAGA_CULT_PREFIX = "custom_cult_"
#: The Ability catalog's Mystery Cult Lore, which already names any cult:
#: a cult whose Lore is written this way needs no Ability of its own.
CATALOG_LORE_PREFIX = "Mystery Cult Lore:"
#: The Characteristic an Initiation Total adds (Presence, TMRE p. 13; a
#: cult may choose another, as some hedge traditions do).
CULT_CHARACTERISTICS: tuple[str, ...] = ("Presence", "Communication", "Intelligence")
#: Who may join: Hermetic magi, or anyone (an unGifted Initiate then needs
#: an Ordeal in every Initiation, Hedge Magic Revised Edition p. 14).
CULT_GIFTED, CULT_ANYONE = "gifted", "any"
CULT_WHO: tuple[str, ...] = (CULT_GIFTED, CULT_ANYONE)

#: The kinds of Script component, by their key in rules.mysteries'
#: components table, as the cult's lists name them; "virtue_replaced" is
#: the Minor Virtue the Initiated Major Virtue replaces (+3, TMRE p. 15),
#: "rite" the lump bonus of a rite proposed by experiment, until its
#: components are written out, and "flawed_ordeal" the extra Ordeal Flaw
#: an experiment's major flaw adds, with no bonus (TMRE p. 18).
COMPONENT_KINDS: dict[str, str] = {
    "place": "Special place and time",
    "quest": "Quest",
    "unique_quest": "Unique Quest",
    "ordeal_minor": "Minor Ordeal",
    "ordeal_medium": "Medium Ordeal",
    "ordeal_major": "Major Ordeal",
    "virtue_replaced": "A Minor Virtue replaced",
    "goods": "Sacrifice of goods",
    "time": "Season of service",
    "great_sacrifice": "Great sacrifice",
    "mystagogue_time": "The Mystagogue's time",
    "sympathy": "Sympathy",
    "rite": "The rite as proposed",
    "flawed_ordeal": "An experiment's Ordeal Flaw",
}
#: The Ordeal components and the size of each.
ORDEAL_KINDS: dict[str, str] = {
    "ordeal_minor": "Minor",
    "ordeal_medium": "Medium",
    "ordeal_major": "Major",
}
#: The kinds that inflict a Flaw: the Ordeals and an experiment's flaw.
FLAW_KINDS: tuple[str, ...] = (*ORDEAL_KINDS, "flawed_ordeal")
#: The Initiation Target of a Virtue the Mystagogue knows, by tier (DE p.
#: 387): a saga cult's Script has it as its Ease Factor, and the
#: Initiation season adds 3 or 9 when the Mystagogue lacks the Virtue.
KNOWN_TARGETS: dict[str, int] = {"Minor": 15, "Major": 21}
#: The Lore an Initiate needs: at least 1 for any Initiation; the second
#: and later Initiations typically need 3, a guideline the troupe may set
#: aside (TMRE pp. 11, 13; DE p. 387).
FIRST_LORE, LATER_LORE = 1, 3


def _strings(value: Any, what: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{what} isn't a list.")
    return [str(v) for v in value]


def _int(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise ValueError(f"{what} {value!r} isn't a whole number.")
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"{what} {value!r} isn't a whole number.") from None


@dataclass
class CultComponent:
    """One component of a Script: its kind (COMPONENT_KINDS), the bonus it
    gives, what it is ("a thread of a faerie's gown") and, for an
    Ordeal, the Flaw it inflicts (a Virtue/Flaw catalog id)."""

    key: str
    bonus: int = 0
    note: str = ""
    flaw_id: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CultComponent:
        d = known_fields(cls, data)
        key = str(d.get("key") or "")
        if key not in COMPONENT_KINDS:
            raise ValueError(
                f"A cult Script's component {key!r} isn't a kind it knows."
            )
        d["key"] = key
        d["bonus"] = _int(d.get("bonus") or 0, "A cult Script component's bonus")
        d["note"] = str(d.get("note") or "")
        d["flaw_id"] = str(d.get("flaw_id") or "")
        return cls(**d)

    @property
    def kind(self) -> str:
        return COMPONENT_KINDS[self.key]


@dataclass
class CultScript:
    """A degree's Initiation Script: its name and its components; its
    bonus is theirs added up (TMRE p. 15). A Script found by experiment
    also keeps what the experiment wrote into it (TMRE p. 18): the
    Personality Traits it gives the Initiate ("Devoted to the cult +1"),
    the Virtues a major benefit added (Virtue/Flaw catalog ids), and the
    different Virtue a modified effect Initiates instead of the degree's
    own ("" for the degree's)."""

    name: str
    components: list[CultComponent] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    virtues: list[str] = field(default_factory=list)
    initiates: str = ""

    @property
    def bonus(self) -> int:
        return sum(c.bonus for c in self.components)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CultScript:
        d = known_fields(cls, data)
        d["name"] = str(d.get("name") or "")
        d["components"] = [
            CultComponent.from_dict(c) for c in d.get("components") or []
        ]
        where = f"The cult Script {d['name']!r}"
        d["traits"] = _strings(d.get("traits") or [], f"{where}: its traits")
        d["virtues"] = _strings(d.get("virtues") or [], f"{where}: its Virtues")
        d["initiates"] = str(d.get("initiates") or "")
        return cls(**d)


@dataclass
class CultDegree:
    """A degree of Initiation: its name ("Weaver"), the Mystery Virtue it
    teaches (a Virtue/Flaw catalog id, the saga's own included) and its
    Script (None until one is written, or found by experiment)."""

    id: str
    name: str
    virtue_id: str = ""
    #: What a Virtue that names something names: {"art": "imaginem"}.
    virtue_params: dict[str, str] = field(default_factory=dict)
    script: CultScript | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CultDegree:
        d = known_fields(cls, data)
        d["id"] = str(d.get("id") or "")
        d["name"] = str(d.get("name") or "")
        d["virtue_id"] = str(d.get("virtue_id") or "")
        params = d.get("virtue_params") or {}
        if not isinstance(params, dict):
            raise ValueError(
                f"The degree {d['name']!r}: its Virtue's details aren't a mapping."
            )
        d["virtue_params"] = {str(k): str(v) for k, v in params.items()}
        if d.get("script") is not None:
            d["script"] = CultScript.from_dict(d["script"])
        return cls(**d)


@dataclass
class MysteryCult:
    """A Mystery Cult of the saga's own: its name, its Lore (an Ability),
    its realm, the Characteristic its Initiation Total adds, who may join,
    its founder and the year, what it is, and its degrees in order."""

    id: str
    name: str
    lore: str
    realm: str = "Magic"
    characteristic: str = "Presence"
    who: str = CULT_GIFTED
    #: The founder (a character id; "" for none named) and the year.
    founder_id: str = ""
    founded: int | None = None
    description: str = ""
    degrees: list[CultDegree] = field(default_factory=list)
    #: As a secret society, a faction in the Order's politics: what it
    #: works for, and its attitudes toward the troupe's covenants, which
    #: its members' covenants lean by at a Tribunal (older saves load with
    #: none).
    agenda: str = ""
    attitudes: list[Attitude] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MysteryCult:
        d = known_fields(cls, data)
        name = str(d.get("name") or "")
        where = f"The Mystery Cult {name or d.get('id')!r}"
        d["name"] = name
        d["lore"] = str(d.get("lore") or "")
        if not str(d.get("id") or "").startswith(SAGA_CULT_PREFIX):
            raise ValueError(f"{where}: its id must start with {SAGA_CULT_PREFIX!r}.")
        if d.get("realm", "Magic") not in TRADITION_REALMS:
            raise ValueError(f"{where}: unknown realm {d.get('realm')!r}.")
        if d.get("characteristic", "Presence") not in CULT_CHARACTERISTICS:
            raise ValueError(
                f"{where}: unknown Characteristic {d.get('characteristic')!r}."
            )
        if d.get("who", CULT_GIFTED) not in CULT_WHO:
            raise ValueError(f"{where}: unknown membership {d.get('who')!r}.")
        if d.get("founded") is not None:
            d["founded"] = _int(d["founded"], f"{where}: the year founded")
        d["degrees"] = [CultDegree.from_dict(g) for g in d.get("degrees") or []]
        d["attitudes"] = [Attitude.from_dict(a) for a in d.get("attitudes") or []]
        return cls(**d)


def is_saga_cult(tradition_id: str) -> bool:
    """Whether a tradition id is one of a saga's own cults."""
    return tradition_id.startswith(SAGA_CULT_PREFIX)


def needs_lore_ability(cult: MysteryCult) -> bool:
    """Whether the cult's Lore is an Ability of its own: not one the
    catalog's "Mystery Cult Lore: (cult)" already names, nor blank."""
    lore = cult.lore.strip()
    return bool(lore) and not lore.startswith(CATALOG_LORE_PREFIX)


def lore_ability(cult: MysteryCult) -> AbilityDef:
    """The cult's Lore as an Ability: a General Lore, as the catalog's
    Mystery Cult Lore (the storyguide creates it, TMRE p. 18)."""
    return AbilityDef(
        id=f"{cult.id}_lore",
        name=cult.lore.strip(),
        category="General",
        description=(
            f"The Lore of {cult.name}, the saga's own Mystery Cult: its "
            "legends, rites and secrets, and for a Mystagogue the Initiation "
            "of others (The Mysteries Revised Edition pp. 13, 18-19)."
        ),
        source="",
    )


def _ordeal_words(script: CultScript, virtues: Mapping[str, VirtueFlawDef]) -> str:
    found = []
    for component in script.components:
        if component.key not in FLAW_KINDS and not component.flaw_id:
            continue
        flaw = virtues.get(component.flaw_id)
        name = flaw.name if flaw is not None else "a Flaw"
        size = ORDEAL_KINDS.get(component.key)
        found.append(f"{name} ({size} Ordeal)" if size else f"{name} (Ordeal)")
    return ", ".join(found)


def _named(virtue: VirtueFlawDef, params: Mapping[str, str]) -> str:
    named = virtue.name
    for key, value in params.items():
        named = named.replace(f"{{{key}}}", value.title())
    return named


def _gains(
    degree: CultDegree, script: CultScript, virtues: Mapping[str, VirtueFlawDef]
) -> tuple[str, str]:
    """What following the Script gives, and the tier its Target is set by:
    the degree's Virtue (or the one a modified effect Initiates instead),
    any Virtue a major benefit added, and its Personality Traits."""
    instead = virtues.get(script.initiates) if script.initiates else None
    virtue = instead or virtues.get(degree.virtue_id)
    tier = (
        virtue.tier if virtue is not None and virtue.tier in KNOWN_TARGETS else "Minor"
    )
    params = {} if instead is not None else degree.virtue_params
    parts = [f"{_named(virtue, params)} ({tier})"] if virtue is not None else []
    for extra in script.virtues:
        found = virtues.get(extra)
        if found is not None:
            parts.append(f"{found.name} ({found.tier})")
    parts += [f"Personality Trait {t}" for t in script.traits]
    return ", ".join(parts), tier


def as_tradition(
    cult: MysteryCult, virtues: Mapping[str, VirtueFlawDef]
) -> TraditionDef:
    """The cult as a tradition of the catalog: its Lore and Virtues, and
    an Initiation rule whose Scripts are its degrees' (a degree with no
    Script has none to follow). A Script's Ease Factor is the Target for
    a Mystagogue who knows the Virtue, 15 or 21 by its tier; its Initiate
    needs the Lore at 1 (TMRE p. 13: the 3 that later Initiations typically
    need is the season's warning, not a requirement)."""
    scripts = []
    for degree in cult.degrees:
        if degree.script is None:
            continue
        gains, tier = _gains(degree, degree.script, virtues)
        scripts.append(
            InitiationScript(
                name=f"{degree.name}: {degree.script.name}",
                ease_factor=KNOWN_TARGETS[tier],
                bonus=degree.script.bonus,
                gains=gains,
                ordeal=_ordeal_words(degree.script, virtues),
                who=CULT_GIFTED if cult.who == CULT_GIFTED else "",
                requires=((cult.lore, FIRST_LORE),) if cult.lore else (),
                components=tuple(
                    (f"{c.kind}: {c.note}" if c.note else c.kind, c.bonus)
                    for c in degree.script.components
                ),
            )
        )
    return TraditionDef(
        id=cult.id,
        name=cult.name,
        source="",
        realm=cult.realm,
        description=cult.description,
        abilities=[cult.lore] if cult.lore else [],
        virtues=[d.virtue_id for d in cult.degrees if d.virtue_id],
        notes="The saga's own Mystery Cult (The Mysteries Revised Edition pp. 18-19).",
        initiation=InitiationRule(
            characteristic=cult.characteristic,
            lore=cult.lore,
            self_initiation=True,
            scripts=scripts,
            notes="The Initiation Total is the Mystagogue's "
            f"{cult.characteristic} + {cult.lore or 'the Lore'} + the Script "
            "(The Mysteries Revised Edition p. 13).",
        ),
    )
