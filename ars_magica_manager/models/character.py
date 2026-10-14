"""The Character and its Art scores."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..rules import xp as xp_rules
from .common import CharacterType, FatigueLevel, Handedness, known_fields
from .holdings import Possession
from .laboratory import DiaryEntry
from .traits import Ability, Characteristics, KnownSpell, Spell, VirtueFlawInstance


@dataclass
class ArtScore:
    """A magus's score in one Art: the total xp spent is stored, the score
    derived from it (rules.xp)."""

    xp: int = 0

    @property
    def level(self) -> int:
        """The score the xp buys."""
        return xp_rules.score_from_xp(self.xp, xp_rules.ART_FACTOR)

    @property
    def progress(self) -> xp_rules.Progress:
        return xp_rules.progress(self.xp, xp_rules.ART_FACTOR)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArtScore:
        d = dict(data)
        if "level" in d:
            # Older saves typed the score beside the xp.
            d["xp"], _ = xp_rules.migrate_level_xp(
                d.pop("level"), d.get("xp", 0), xp_rules.ART_FACTOR
            )
        return cls(**known_fields(cls, d))


@dataclass
class Background:
    """Character-sheet page 1's biographical block (not the paper sheet's
    "Description" box -- see Description below for that)."""

    player: str = ""
    #: The saga Player who plays this character (players.py):
    #: when they sign in to a hosted saga, they may change it. None: no one
    #: but the storyguide.
    player_id: str | None = None
    setting: str = ""
    size: int = 0
    confidence_score: int = 0
    confidence_points: int = 0
    #: True Faith (faith.py): a Score only with the True Faith Virtue;
    #: anyone may hold Faith Points.
    true_faith_score: int = 0
    faith_points: int = 0
    birth_name: str = ""
    year_born: int | None = None
    race_nationality: str = ""
    place_of_origin: str = ""
    religion: str = ""
    title_profession: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Background:
        d = dict(data)
        if "confidence" in d and "confidence_score" not in d:
            # Older saves used a single "confidence"; migrate on load
            # so existing characters don't become unreadable over the split.
            d["confidence_score"] = d.pop("confidence")
        return cls(**known_fields(cls, d))


@dataclass
class Description:
    height: float | None = None
    weight: float | None = None
    hair: str = ""
    eyes: str = ""
    handedness: Handedness = "right"
    physical_description: str = ""
    #: Free-text biography, distinct from physical_description (the paper
    #: sheet's short free-text box), shown in the Biographical
    #: Detail section.
    biography: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Description:
        return cls(**known_fields(cls, data))


@dataclass
class Aging:
    """Decrepitude and Warping. Warping is tracked as Score/Points; both are
    typed for now (deriving the Score is Phase 4)."""

    decrepitude: int = 0
    effects: str = ""
    warping_score: int = 0
    warping_points: int = 0
    #: A Longevity Ritual: its modifier to aging rolls (0: none),
    #: the year it was made and who made it.
    longevity_modifier: int = 0
    longevity_year: int | None = None
    longevity_by: str = ""
    #: Aging: Decrepitude points (the score is worked out from
    #: them and kept in `decrepitude`), Aging Points per Characteristic, the
    #: apparent age (None: the actual age), and the season spent recovering
    #: from an Aging Crisis ("Spring 1221").
    decrepitude_points: int = 0
    aging_points: dict[str, int] = field(default_factory=dict)
    apparent_age: int | None = None
    recovering: str = ""
    #: Wizard's Twilight: the last season it takes ("Winter
    #: 1224"); no activity can be planned until after it.
    twilight_until: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aging:
        aging = cls(**known_fields(cls, data))
        if aging.decrepitude and "decrepitude_points" not in data:
            # A typed Decrepitude score: the points that give it.
            thresholds = (0, 5, 15, 30, 50, 75)
            aging.decrepitude_points = thresholds[max(0, min(aging.decrepitude, 5))]
        return aging


@dataclass
class Wounds:
    """Simple per-severity counts, not individual wound records -- matches
    checking boxes on the paper sheet, not the calculated Wound Penalty."""

    light: int = 0
    medium: int = 0
    heavy: int = 0
    incapacitated: bool = False
    dead: bool = False
    #: A character's typed adjustment on top of the Soak worked out from
    #: Stamina, armour and Virtues (rules.derived.soak); a
    #: familiar's wounds leave it 0 (a familiar has base_soak).
    soak: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wounds:
        return cls(**known_fields(cls, data))


@dataclass
class ScoredTrait:
    """A name + integer score. Shared shape for Personality Traits and
    Reputations -- both are just a label and a score on the character sheet."""

    name: str
    score: int
    #: Covenant Reputations only: whether the covenant is aware of this
    #: reputation (an unknown bad Reputation can't yet hurt Loyalty -- see
    #: inhabitants.reputation_loyalty_penalty). Always True and never edited
    #: for a Character's own Personality Traits/Reputations.
    known: bool = True


@dataclass
class HermeticBackground:
    """Magus-only Hermetic lineage block. `house` is a house_catalog.json id;
    no mechanical bonus is modeled for it yet, same as an unencoded
    Virtue/Flaw -- see VirtueFlawDef.modifiers."""

    house: str | None = None
    domus_magna: str = ""
    primus: str = ""
    parens: str = ""
    covenant_of_apprenticeship: str = ""
    #: Blank/unset means unknown, same convention as Background.year_born.
    age_of_apprenticeship: int | None = None
    wizards_sigil: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HermeticBackground:
        return cls(**known_fields(cls, data))


@dataclass
class Ordeal:
    """An Ordeal suffered in a Mystery Initiation: its size ("Minor",
    "Medium" or "Major") and the Initiations undergone since, which it makes
    easier until the third."""

    size: str
    initiations_since: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Ordeal:
        return cls(**known_fields(cls, data))


@dataclass
class Progress:
    """Progress carried from season to season on something a character is
    working at: an excellent item, a pilgrimage, taming
    an animal, a work of art, a formula, years at university."""

    kind: str
    name: str
    target: int = 0
    points: int = 0
    done: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Progress:
        return cls(**known_fields(cls, data))


@dataclass
class GrogYear:
    """A grog's yearly update (Grogs Ch. 5), applied in Winter:
    the vocational training (7 xp, or the teacher's Source Quality), 4 xp of
    practice and two 2 xp of exposure, less a season for each story award
    this year."""

    vocational: str = ""
    vocational_xp: int = 7
    practice: str = ""
    exposure: str = ""
    exposure_2: str = ""
    story_awards: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GrogYear:
        return cls(**known_fields(cls, data))


@dataclass
class Breakthrough:
    """A magus's original research goal: what it is, its kind and
    target (the storyguide may type a secret one), the points gained, what
    reaching it grants, a Discovery waiting to be stabilized, and insights
    waiting to be invented."""

    name: str
    kind: str = "Minor"  # Minor / Major / Hermetic
    target: int = 30
    points: int = 0
    description: str = ""
    #: What reaching it grants: "Ability" (the points become its xp),
    #: "Virtue" (a catalog id in `grant`), "Parameter" or "" (the troupe's).
    grant_kind: str = ""
    grant: str = ""
    #: The Discovery to stabilize: its magnitude, the seasons, Lab Total,
    #: risk and vis of the experiment that made it, and the move of the chart
    #: roll (repeated when stabilizing).
    pending_magnitude: int = 0
    discovery_seasons: int = 1
    discovery_lab_total: int = 0
    discovery_risk: int = 0
    discovery_vis: int = 0
    discovery_vis_art: str = ""
    discovery_shift: int = 0
    #: The Technique and Form of that experiment (its Lab Text's).
    discovery_technique: str = ""
    discovery_form: str = ""
    #: Stabilizing: the seasons done of the current attempt.
    stabilizing_seasons: int = 0
    #: Insights gained and not yet invented.
    insights: int = 0
    reached: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Breakthrough:
        return cls(**known_fields(cls, data))


@dataclass
class CreationXp:
    """xp spent at a creation step, already added to
    the Ability or Art it names: the Creation Worksheet's record of where a
    character's starting xp came from, checked against each step's budget."""

    #: The worksheet step: "childhood", "later_life", "virtue", "free",
    #: "apprenticeship" or "gauntlet".
    step: str
    #: An Ability's name ("Area Lore: Rhine") or an Art ("Creo").
    target: str
    xp: int
    #: "native" for the childhood Native Language; the Virtue (vf_id) whose
    #: xp a "virtue" entry spends; the package a "package" entry comes from.
    note: str = ""
    #: The xp actually added to the Ability or Art (an Affinity adds half
    #: again); None: `xp`.
    applied: int | None = None


@dataclass
class CreationConditions:
    """A magus's years past Gauntlet at creation: the seasons
    that went to lab work, the working conditions the storyguide set (used
    for lab work and pre-play aging), and the age pre-play aging has been
    rolled up to (None: not yet)."""

    lab_seasons: int = 0
    aura: int = 3
    lab_quality: int = 0
    living_conditions: int = 1
    aged_to: int | None = None


@dataclass
class LabTextAccess:
    """How far a magus can read one author's raw Lab Texts: up to `level`, and how that
    was gained -- "decoded", "taught" (the author's abbreviations) or "" (not
    recorded)."""

    level: int = 0
    via: str = ""


@dataclass
class Character:
    id: str
    name: str
    type: CharacterType
    covenant_id: str | None = None
    characteristics: Characteristics = field(default_factory=Characteristics)
    arts: dict[str, ArtScore] = field(default_factory=dict)
    abilities: list[Ability] = field(default_factory=list)
    virtues_flaws: list[VirtueFlawInstance] = field(default_factory=list)
    #: Spells known, each with its own Spell Mastery.
    spells_known: list[KnownSpell] = field(default_factory=list)
    #: Spells this magus invented: they live with the magus, not the catalog
    #: (see Spell). Invention itself comes with the lab activities.
    invented_spells: list[Spell] = field(default_factory=list)
    #: Personal gear -- Possession records scoped to kind in
    #: {"weapon", "armor", "item"} (a character-scale subset of what the
    #: covenant Possessions tab holds; no sanctums/vis on a character sheet).
    inventory: list[Possession] = field(default_factory=list)
    #: Silver carried, in pounds, as a covenant's Wealth is counted: what a
    #: character takes with them when they leave a covenant or join one.
    silver: int = 0
    assigned_lab_id: str | None = None
    background: Background = field(default_factory=Background)
    description: Description = field(default_factory=Description)
    aging: Aging = field(default_factory=Aging)
    wounds: Wounds = field(default_factory=Wounds)
    fatigue_level: FatigueLevel = "fresh"
    personality_traits: list[ScoredTrait] = field(default_factory=list)
    reputations: list[ScoredTrait] = field(default_factory=list)
    raw_vis: dict[str, int] = field(default_factory=dict)  # Art -> pawns
    hermetic: HermeticBackground = field(default_factory=HermeticBackground)
    #: What the character did season by season: written when a season is
    #: applied, and editable like a laboratory's Diary.
    diary: list[DiaryEntry] = field(default_factory=list)
    #: Tractatus already studied (book ids): each gives its xp only once
    #: (DE Ch. 10, Studying Tractatus).
    tractatus_read: list[str] = field(default_factory=list)
    #: Summae studied for at least a season (book ids), recorded as seasons
    #: are applied: a commentary is read only after its summa (Covenants,
    #: Other Opus Types).
    summae_read: list[str] = field(default_factory=list)
    #: Whose raw Lab Texts this magus can read, and up to what level
    #: (decoded, or taught the author's abbreviations), by the
    #: author's character id -- or name, for an author outside the saga
    #: (rules.book_seasons.author_key).
    lab_text_access: dict[str, LabTextAccess] = field(default_factory=dict)
    #: Original research goals.
    breakthroughs: list[Breakthrough] = field(default_factory=list)
    #: A grog's yearly update; None until set up.
    grog_year: GrogYear | None = None
    #: The supplements' sub-systems: Labor Points and a
    #: workshop's scores (City & Guild), progress records, experimental
    #: philosophy formulas known, and the Ordeals still lowering the Target
    #: of a later Initiation.
    labor_points: int = 0
    workshop_innovation: int = 0
    workshop_raw_materials: int = 0
    progress: list[Progress] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    ordeals: list[Ordeal] = field(default_factory=list)
    #: Being created by the book: the creation checks run and
    #: the Creation Worksheet is offered. New records start In Creation;
    #: older saves load In Play (False).
    in_creation: bool = False
    #: Where the starting xp went, step by step.
    creation_xp: list[CreationXp] = field(default_factory=list)
    #: Years past Gauntlet and pre-play aging.
    creation_conditions: CreationConditions = field(default_factory=CreationConditions)
    #: The portrait's file name in the save folder's portraits folder ("":
    #: none; older saves load with none).
    portrait: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        d = dict(data)
        d["characteristics"] = Characteristics.from_dict(d.get("characteristics") or {})
        d["arts"] = {
            art: ArtScore.from_dict(score) for art, score in d.get("arts", {}).items()
        }
        d["abilities"] = [Ability.from_dict(a) for a in d.get("abilities", [])]
        d["virtues_flaws"] = [
            VirtueFlawInstance(**known_fields(VirtueFlawInstance, vf))
            for vf in d.get("virtues_flaws", [])
        ]
        d["background"] = Background.from_dict(d.get("background") or {})
        d["description"] = Description.from_dict(d.get("description") or {})
        d["aging"] = Aging.from_dict(d.get("aging") or {})
        d["wounds"] = Wounds.from_dict(d.get("wounds") or {})
        d["personality_traits"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("personality_traits", [])
        ]
        d["reputations"] = [
            ScoredTrait(**known_fields(ScoredTrait, t))
            for t in d.get("reputations", [])
        ]
        d["hermetic"] = HermeticBackground.from_dict(d.get("hermetic") or {})
        d["invented_spells"] = [
            Spell.from_dict(sp) for sp in d.get("invented_spells", [])
        ]
        d["inventory"] = [
            # Older saves held plain description strings.
            Possession(id=f"{data['id']}-inv-{i}", kind="item", name=item)
            if isinstance(item, str)
            else Possession(**known_fields(Possession, item))
            for i, item in enumerate(d.get("inventory", []))
        ]
        d["spells_known"] = [
            # Older saves held bare spell ids.
            KnownSpell(spell_id=entry)
            if isinstance(entry, str)
            else KnownSpell.from_dict(entry)
            for entry in d.get("spells_known", [])
        ]
        d["diary"] = [DiaryEntry.from_dict(e) for e in d.get("diary", [])]
        d["breakthroughs"] = [
            Breakthrough.from_dict(b) for b in d.get("breakthroughs", [])
        ]
        if d.get("grog_year") is not None:
            d["grog_year"] = GrogYear.from_dict(d["grog_year"])
        d["progress"] = [Progress.from_dict(p) for p in d.get("progress", [])]
        d["ordeals"] = [Ordeal.from_dict(o) for o in d.get("ordeals", [])]
        # Older saves kept only the last Ordeal.
        if d.get("ordeal"):
            d["ordeals"].append(
                Ordeal(d["ordeal"], d.get("initiations_since_ordeal", 0))
            )
        d["creation_conditions"] = CreationConditions(
            **known_fields(CreationConditions, d.get("creation_conditions") or {})
        )
        d["creation_xp"] = [
            CreationXp(**known_fields(CreationXp, x)) for x in d.get("creation_xp", [])
        ]
        d["lab_text_access"] = {
            # In older saves an author's entry was just the level.
            author: (
                LabTextAccess(level=int(entry))
                if isinstance(entry, int)
                else LabTextAccess(**known_fields(LabTextAccess, entry))
            )
            for author, entry in (d.get("lab_text_access") or {}).items()
        }
        return cls(**known_fields(cls, d))


def character_age(year_born: int | None, current_year: int) -> int | None:
    """The character's age this saga-year, or None if Year Born isn't set.

    Not a Character property -- Character has no back-reference to the Saga
    that holds `current_year`, so this takes it explicitly instead, the same
    way an XP-to-Level formula would (see ArtScore's docstring).
    """
    return None if year_born is None else current_year - year_born
