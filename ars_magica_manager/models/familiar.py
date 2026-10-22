"""The Familiar and its bond."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .character import ScoredTrait, Wounds
from .common import (
    ExperimentalEffect,
    FatigueLevel,
    experimental_effects,
    known_fields,
)
from .holdings import Possession
from .traits import Ability, Characteristics, VirtueFlawInstance

#: A Cord's score (0-5) -> its point cost from the binding Lab Total, per the
#: Familiar rules (see familiars.py). An exact table, not a formula.
CORD_SCORE_COSTS: dict[int, int] = {0: 0, 1: 5, 2: 15, 3: 30, 4: 50, 5: 75}


@dataclass
class BondPower:
    """One Empowered Bond Power (invested effect) on a Familiar -- typed in,
    no Lab Total formula computed (see DESIGN.md's "tracker, not rules
    engine" stance)."""

    id: str
    name: str = ""
    level: int = 0
    technique: str = ""  # one of TECHNIQUES, or ""
    form: str = ""  # one of FORMS, or ""
    #: e.g. "Magus (controlled by Familiar)" -- free text, not a fixed enum.
    target_controller: str = ""
    uses_per_day: int = 0
    penetration: int = 0
    vis_spent: int = 0
    cosmetic_trait: str = ""
    #: Points instilled so far while it is being instilled as lab work;
    #: None when finished.
    instilling_progress: int | None = None
    #: What the experiments that instilled it left on it.
    experimental_effects: list[ExperimentalEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BondPower:
        d = dict(data)
        effects = experimental_effects(d.get("experimental_effects"))
        # Older saves wrote them after the cosmetic trait, in brackets.
        found = _OLD_EFFECTS.search(str(d.get("cosmetic_trait", "")))
        if found:
            d["cosmetic_trait"] = d["cosmetic_trait"][: found.start()].rstrip()
            effects += experimental_effects(found.group(1).split("; "))
        d["experimental_effects"] = effects
        return cls(**known_fields(cls, d))


_OLD_EFFECTS = re.compile(r"\(((?:Side|Modified) effect: [^()]*)\)\s*$")


@dataclass
class Familiar:
    """A magus's bound familiar (ArM5 Familiars). One per magus at a time,
    nested under its magus in the nav tree, but its own top-level entity
    (own sheet) rather than a field on Character.

    `character_id` is the magus who bound it: required, set once at
    creation, and never reassigned to a different magus.

    Built in slices, all now landed onto this one dataclass, the
    same way Character grew over many stories.

    `virtues_flaws`/`personality_traits` reuse Character's own shapes
    (VirtueFlawInstance/ScoredTrait) -- True Friend and Loyal (Partner) +3
    are added automatically (to both partners) when the Familiar is
    created, not left for the user to type in.

    The three Cords (golden/silver/bronze) are typed-in scores 0-5; their
    point cost is looked up from CORD_SCORE_COSTS, not stored separately.
    """

    id: str
    character_id: str
    name: str = ""
    #: The sheet's single "Species / Description" free-text line.
    species: str = ""
    season_bound: str = ""  # one of SEASONS, or "" if unset
    year_bound: int | None = None
    magic_might: int = 0
    might_pool: int | None = None  # None = not yet tracked, like year_born
    size: int = 0
    wound_multiplier: int = 1
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    personality_traits: list[ScoredTrait] = field(default_factory=list)
    reputations: list[ScoredTrait] = field(default_factory=list)
    #: Binding details -- typed in, no Lab Total formula computed.
    binding_technique: str = ""  # one of TECHNIQUES, or ""
    binding_form: str = ""  # one of FORMS, or ""
    binding_lab_total: int = 0
    target_binding_level: int = 0
    vis_spent_binding: int = 0
    golden_cord: int = 0  # 0-5
    silver_cord: int = 0  # 0-5
    bronze_cord: int = 0  # 0-5
    characteristics: Characteristics = field(default_factory=Characteristics)
    #: Both typed in, no formula computed -- same "tracker, not rules engine"
    #: treatment as Wounds.soak (see DESIGN.md).
    base_soak: int = 0
    magic_resistance: int = 0
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    #: Bite/Claws/Dodge etc. -- a free list of weapon-kind Possessions (same
    #: shape as Character.inventory's weapons), not a fixed
    #: 3-row table.
    natural_weapons: list[Possession] = field(default_factory=list)
    #: Same shape/catalog as Character.abilities -- Languages are just
    #: ordinary Abilities here too (per the rules, a familiar shares its
    #: magus's Language scores automatically, so none need typing in
    #: unless the user wants to note an exception).
    abilities: list[Ability] = field(default_factory=list)
    bond_powers: list[BondPower] = field(default_factory=list)
    #: What experimenting on the binding left on the bond.
    experimental_effects: list[ExperimentalEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Familiar:
        d = dict(data)
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        d["personality_traits"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("reputations", [])
        ]
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["natural_weapons"] = [
            Possession(**known_fields(Possession, w))
            for w in d.get("natural_weapons", [])
        ]
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["bond_powers"] = [BondPower.from_dict(p) for p in d.get("bond_powers", [])]
        d["experimental_effects"] = experimental_effects(d.get("experimental_effects"))
        return cls(**known_fields(cls, d))


# -- Enchanted Devices & Talismans (DE ch. 8, Enchantments) --
