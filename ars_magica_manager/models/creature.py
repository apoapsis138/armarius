"""A creature of the Bestiary: a beast, spirit, faerie, demon or angel
written up as a stat block, linkable to the places it is found."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .character import ScoredTrait, Wounds
from .common import FatigueLevel, known_fields
from .traits import Ability, Characteristics, VirtueFlawInstance, new_instance_id
from .world import SKETCH, Link


@dataclass
class CreatureAttack:
    """One line of a creature's Combat: "Kick: Init +4, Attack +4, Defense
    +8, Damage +5", typed as the book prints the totals. A None Attack or
    Damage is the book's n/a."""

    name: str
    init: int = 0
    attack: int | None = 0
    defense: int = 0
    damage: int | None = 0
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class CreaturePower:
    """One of a creature's Powers: what it costs in Might Points, its
    Initiative modifier and Form, its Range, Duration and Target, the
    effect level it was designed as (None when the book gives none), any
    Penetration bonus beyond its Might, and what it does. Its Penetration
    is worked out (creatures.penetration)."""

    name: str
    might_cost: int = 0
    init: int = 0
    form: str = ""
    range: str = ""
    duration: str = ""
    target: str = ""
    level: int | None = None
    penetration_bonus: int = 0
    description: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class BodyVis:
    """Vis in a creature's body: "2 pawns of Animal, in its head"."""

    pawns: int
    art: str = ""
    where: str = ""
    id: str = field(default_factory=new_instance_id, compare=False)


@dataclass
class Creature:
    """A creature of the Bestiary. Composed of the trait value objects a
    Character and a Familiar use (Characteristics, Ability,
    VirtueFlawInstance with Qualities and Inferiorities, ScoredTrait,
    Wounds), not a kind of Character: it has no Arts, laboratory, aging or
    experience. Combat and Soak are typed as the book prints them.

    `many` marks a stat block for many of a kind (the boglins, a swarm of
    mice), with `how_many` saying how many there are. A creature with no
    `realm` is mundane and has no Might.
    """

    id: str
    name: str
    many: bool = False
    how_many: str = ""
    #: One of common.REALMS, or "" for a mundane beast.
    realm: str = ""
    might: int = 0
    #: The Form its Might is aligned to; one of FORMS, or "".
    might_form: str = ""
    #: Might Points left now; None when not tracked.
    might_pool: int | None = None
    #: A demon's Order ("Prince of the False Gods"), its Hierarchy score
    #: (None when not given) and its Weakness, as Realms of Power: The
    #: Infernal prints them; only an Infernal creature has them.
    order: str = ""
    hierarchy: int | None = None
    weakness: str = ""
    characteristics: Characteristics = field(default_factory=Characteristics)
    #: Animal intelligence: its Intelligence is a Cunning score (Cun).
    cunning: bool = False
    size: int = 0
    #: Its age as the book prints it, the apparent age in brackets
    #: ("200 (40)", "n/a (30)"), or "".
    age: str = ""
    #: Its Confidence Score (None when it has none) and Confidence Points.
    confidence_score: int | None = None
    confidence_points: int = 0
    #: A magical creature's season (one of SEASONS), or "".
    season: str = ""
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    personality_traits: list[ScoredTrait] = field(default_factory=list)
    reputations: list[ScoredTrait] = field(default_factory=list)
    attacks: list[CreatureAttack] = field(default_factory=list)
    soak: int = 0
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    #: Its Fatigue levels as the book prints them, when they differ from a
    #: person's ("OK, 0, -1, -3, -5, Unconscious"); "" for a person's.
    fatigue_levels: str = ""
    #: False for a creature that never tires, or cannot be wounded.
    tires: bool = True
    can_be_wounded: bool = True
    #: Its Encumbrance with its Burden in brackets ("0 (0)"), or "".
    encumbrance: str = ""
    abilities: list[Ability] = field(default_factory=list)
    powers: list[CreaturePower] = field(default_factory=list)
    vis: list[BodyVis] = field(default_factory=list)
    equipment: str = ""
    appearance: str = ""
    notes: str = ""
    #: Where the stat block is printed: "Guardians of the Forests p. 34".
    source: str = ""
    #: How much of it is written down (world.DETAIL_LEVELS).
    detail: str = SKETCH
    #: The place it is found (a place neighbour's id) and which of its
    #: levels (0 for the surface).
    place_id: str | None = None
    place_level: int = 0
    links: list[Link] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Creature:
        d = known_fields(cls, data)
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        for key in ("personality_traits", "reputations"):
            d[key] = [
                ScoredTrait(**known_fields(ScoredTrait, t)) for t in d.get(key, [])
            ]
        d["attacks"] = [
            CreatureAttack(**known_fields(CreatureAttack, a))
            for a in d.get("attacks", [])
        ]
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["powers"] = [
            CreaturePower(**known_fields(CreaturePower, p)) for p in d.get("powers", [])
        ]
        d["vis"] = [BodyVis(**known_fields(BodyVis, v)) for v in d.get("vis", [])]
        d["links"] = [Link(**known_fields(Link, x)) for x in d.get("links", [])]
        return cls(**d)
