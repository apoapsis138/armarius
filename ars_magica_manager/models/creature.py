"""A creature of the Bestiary: a beast, spirit, faerie, demon or angel
written up as a stat block, linkable to the places it is found."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .character import Wounds
from .common import FatigueLevel, known_fields, move_secrets
from .traits import (
    Ability,
    Characteristics,
    ScoredTrait,
    VirtueFlawInstance,
    new_instance_id,
)
from .world import SKETCH, Attitude, Favour, Link, read_standing


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
    #: The Magic Quality the power comes from (rules.creature_build.POWERS,
    #: "" for typed figures), which suggests its cost and Initiative.
    quality: str = ""
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
    #: Infernal prints them; only an Infernal creature has them, but for
    #: an angel's Choir in `order` (Realms of Power: The Divine p. 18).
    order: str = ""
    hierarchy: int | None = None
    weakness: str = ""
    #: A faerie's role in the stories it plays (one of rules.faerie_build.
    #: ROLES, or "") and the story it wants, in a line (Realms of Power:
    #: Faerie pp. 40, 140-142); only a Faerie creature has them.
    faerie_role: str = ""
    faerie_story: str = ""
    #: A vampire (a faerie, Against the Dark pp. 115-117): the precautions
    #: that alone stop it forming (all must be met), the limitations it
    #: obeys, and the one way that kills it for good, each chosen from the
    #: book's lists (one to three, one to three, and one); "" when none.
    vampire_precautions: str = ""
    vampire_limitations: str = ""
    vampire_death: str = ""
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
    #: A transformed animal's Warping Score: a creature with Might has
    #: none (Realms of Power: Magic p. 78).
    warping_score: int = 0
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
    #: Its attitude toward each player covenant and the favours owed
    #: between it and the troupe, as a neighbour's are (models.world).
    attitudes: list[Attitude] = field(default_factory=list)
    favours: list[Favour] = field(default_factory=list)
    #: What only the storyguide should read: the record's Secrets
    #: chapter, hidden from players signed in to a hosted copy.
    secrets: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Creature:
        # Older saves kept secrets under a heading in the notes.
        d = move_secrets(known_fields(cls, data), "notes")
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
        read_standing(d)
        return cls(**d)
