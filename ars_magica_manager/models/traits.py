"""A character's traits: Virtue/Flaw instances, Characteristics,
Abilities, spells and their Mastery."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from ..rules import xp as xp_rules
from .common import ExperimentalEffect, experimental_effects, known_fields


@dataclass
class VirtueFlawInstance:
    """A catalog Virtue/Flaw as attached to a specific Character or Laboratory.

    `id` tells apart two instances of the same Virtue (a lab's two Lesser
    Features), so a LabFeature can point at its own. A laboratory's
    instances always have one (given at load and when added); a character's
    are left "". It isn't compared: two instances of the same Virtue with
    the same params are equal."""

    vf_id: str
    params: dict[str, str] = field(default_factory=dict)
    id: str = field(default="", compare=False)


def new_instance_id() -> str:
    """A fresh id for a VirtueFlawInstance or LabFeature."""
    return uuid.uuid4().hex[:12]


@dataclass
class Characteristics:
    intelligence: int = 0
    perception: int = 0
    strength: int = 0
    stamina: int = 0
    presence: int = 0
    communication: int = 0
    dexterity: int = 0
    quickness: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Characteristics:
        return cls(**known_fields(cls, data))


@dataclass
class Ability:
    """An Ability: its total xp is stored and its score derived from it
    (rules.xp)."""

    name: str
    category: str = "General"
    xp: int = 0
    specialty: str | None = None
    #: The xp table it advances on (common.XP_TABLES), copied from its
    #: catalog entry when it's taken: "art" for an Accelerated Ability.
    xp_table: str = "ability"

    @property
    def factor(self) -> int:
        """xp per score step: the Art table's or the Ability table's."""
        return (
            xp_rules.ART_FACTOR if self.xp_table == "art" else xp_rules.ABILITY_FACTOR
        )

    @property
    def level(self) -> int:
        """The score the xp buys."""
        return xp_rules.score_from_xp(self.xp, self.factor)

    @property
    def progress(self) -> xp_rules.Progress:
        return xp_rules.progress(self.xp, self.factor)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ability:
        d = dict(data)
        if "score" in d and "level" not in d:
            # Pre-Phase-1b saves used "score".
            d["level"] = d.pop("score")
        d.pop("xp_to_next", None)  # typed by hand in older saves
        if "level" in d:
            # Older saves typed the score beside the xp.
            d["xp"], _ = xp_rules.migrate_level_xp(
                d.pop("level"), d.get("xp", 0), xp_rules.ABILITY_FACTOR
            )
        if d.get("name") == "Medicinal Divining":
            # The medicinal kind is a type of the one Divining Art, which
            # advances as an Art: keep the score the old entry had.
            score = xp_rules.score_from_xp(d.get("xp", 0), xp_rules.ABILITY_FACTOR)
            d["name"], d["xp_table"] = "Elementalist Divining", "art"
            d["xp"] = xp_rules.xp_for_score(score, xp_rules.ART_FACTOR)
        return cls(**known_fields(cls, d))


@dataclass
class Spell:
    """A Hermetic spell. The shared catalog (data/spell_catalog.json) holds the
    published ones; `Saga.spells` holds the saga's own (added by hand or
    imported); a magus's `Character.invented_spells` holds theirs. All share
    one id namespace -- catalog.find_spell() resolves an id from any of them.

    `level` is None for a General-level spell (the Aegis of the Hearth, the
    Wards), which is cast at any level. Range/Duration/Target are plain
    strings: the core values (SPELL_RANGES etc.) or a supplement's own.
    `requisites` are extra Arts (Techniques or Forms) the spell also needs.
    Magnitude, the "CrIg 20" shorthand and a Ritual's vis cost and casting time
    are worked out in spells.py, never stored."""

    id: str
    name: str
    technique: str
    form: str
    level: int | None = None
    description: str = ""
    requisites: list[str] = field(default_factory=list)
    range: str = ""
    duration: str = ""
    target: str = ""
    ritual: bool = False
    #: The guideline level before Range/Duration/Target (None if not given).
    base_level: int | None = None
    #: Where it's published: a sourcebooks.SOURCEBOOKS abbreviation, or free
    #: text for the saga's own spells.
    source: str = "ArM5"
    #: The page of `source` it's printed on ("" if not known).
    page: str = ""
    #: Side effects and modified effects from the experiment that invented
    #: it: anyone who learns it learns them too.
    experimental_effects: list[ExperimentalEffect] = field(default_factory=list)
    #: A catalog entry listed without its details (the source page lacks them).
    details_missing: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Spell:
        d = dict(data)
        d["experimental_effects"] = experimental_effects(d.get("experimental_effects"))
        return cls(**known_fields(cls, d))


@dataclass
class MasteryAbility:
    """One Mastery Ability a magus has bought on a known spell (Fast
    Casting, Penetration, ...) -- its own name/level/xp, since some (e.g.
    Multiple Casting) carry a score that matters. No catalog or rules
    validation yet (see DESIGN.md's "tracker, not rules engine" stance)."""

    name: str
    level: int = 0
    xp: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MasteryAbility:
        return cls(**known_fields(cls, data))


@dataclass
class KnownSpell:
    """One spell a character knows, plus their Spell Mastery in it (ArM5
    Chapter Seven): a score/xp track and the Mastery Abilities bought with
    it. `spell_id` resolves through catalog.find_spell() like any other
    spell reference (catalog, saga's own, or the magus's invented spells)."""

    spell_id: str
    mastery_score: int = 0
    mastery_xp: int = 0
    mastery_abilities: list[MasteryAbility] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KnownSpell:
        d = dict(data)
        d["mastery_abilities"] = [
            MasteryAbility.from_dict(m) for m in d.get("mastery_abilities", [])
        ]
        return cls(**known_fields(cls, d))


@dataclass
class ScoredTrait:
    """A name + integer score. Shared shape for Personality Traits and
    Reputations -- both are just a label and a score on the character sheet."""

    name: str
    score: int
    #: Covenant Reputations only: whether the covenant is aware of this
    #: reputation (an unknown bad Reputation can't yet hurt Loyalty -- see
    #: inhabitants.reputation_loyalty). Always True and never edited
    #: for a Character's own Personality Traits/Reputations.
    known: bool = True
    #: Reputations only: the kind of reputation (REPUTATION_TYPES, or "")
    #: and how far it reaches ("the Rhine", "the parish"), both optional.
    type: str = ""
    reach: str = ""
    #: Reputations only: noteworthy deeds counted toward the next level,
    #: each an experience point (rules.confidence.add_deeds).
    deeds: int = 0
