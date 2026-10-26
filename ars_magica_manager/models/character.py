"""The Character and its Art scores."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..rules import xp as xp_rules
from .agents import Agent
from .common import (
    CharacterType,
    ExperimentalEffect,
    FatigueLevel,
    Handedness,
    experimental_effects,
    known_fields,
    move_secrets,
)
from .holdings import Possession
from .laboratory import DiaryEntry
from .philosophy import Formula
from .traits import (
    Ability,
    Characteristics,
    KnownSpell,
    ScoredTrait,
    Spell,
    VirtueFlawInstance,
    new_instance_id,
    reputation_from_dict,
)
from .world import FULL, Link


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
    #: The Church office or crown the Divine protects ("Pope", "King"...,
    #: penetration.OFFICES), or "" (DE p. 420; Commanding Aura, p. 74).
    church_rank: str = ""
    #: Fluctuating Fortune: whether the character is Wealthy in "even" or
    #: "odd" years (Poor in the others); the book doesn't say (DE p. 130).
    fortune_wealthy_in: str = "even"
    #: The Faith score of the one relic the character relies on (0: none);
    #: its bearer gains ten times it as Magic Resistance (DE p. 419).
    relic_faith: int = 0
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
    #: Art & Academe's complexion (pp. 40-41): one of the four, or a
    #: compound "principal-secondary" ("" for none recorded), and a minor
    #: aspect of a third ("" for none).
    complexion: str = ""
    complexion_minor: str = ""

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
    #: What experimenting on the ritual left on it.
    longevity_effects: list[ExperimentalEffect] = field(default_factory=list)
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
    #: Aging Points still to be placed in a Characteristic of the
    #: storyguide's choice, each with what brought it ("Survived the Ague's
    #: Crisis", Art & Academe p. 47).
    aging_due: list[str] = field(default_factory=list)
    #: How much of their time they spend in the aura where they live
    #: (rules.warping.AURA_TIMES: "always", "half", "frequent", "away").
    aura_time: str = "always"
    #: A physician's regimen (Art & Academe): its bonus to Living
    #: Conditions (0: none), the physician (a character's id) and the
    #: year it began.
    regimen: int = 0
    regimen_by: str = ""
    regimen_since: int | None = None
    #: The Warping Points gained from each realm ("Divine": 7), counted
    #: as they come; what the Warping's effects reflect (the main source).
    #: Empty for points gained before they were counted.
    warping_realms: dict[str, int] = field(default_factory=dict)
    #: A magus with Miraculous Abilities whose troupe chose the Divine
    #: Ascent as his one form of Warping in place of Twilight.
    seeks_ascent: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Aging:
        aging = cls(**known_fields(cls, data))
        aging.longevity_effects = experimental_effects(aging.longevity_effects)
        aging.warping_realms = _realm_counts(aging.warping_realms)
        if aging.longevity_modifier < 0:
            # The Levant pack once stored the ritual's bonus negated: it is
            # always a bonus, taken off the aging roll.
            aging.longevity_modifier = -aging.longevity_modifier
        if aging.decrepitude and "decrepitude_points" not in data:
            # A typed Decrepitude score: the points that give it.
            thresholds = (0, 5, 15, 30, 50, 75)
            aging.decrepitude_points = thresholds[max(0, min(aging.decrepitude, 5))]
        return aging


def _realm_counts(data: object) -> dict[str, int]:
    """A saved Warping-by-realm count, checked: each realm's name and a
    whole number of points."""
    if not isinstance(data, dict):
        raise ValueError(f"Warping by realm must be a mapping, not {data!r}")
    found: dict[str, int] = {}
    for realm, points in data.items():
        if not isinstance(realm, str) or isinstance(points, bool):
            raise ValueError(f"Bad Warping by realm entry {realm!r}: {points!r}")
        if not isinstance(points, int):
            raise ValueError(
                f"Warping Points from {realm} must be a number: {points!r}"
            )
        found[realm] = points
    return found


#: Where a wound came from: an injury heals with Chirurgy, the rest with
#: Medicine (DE p. 405).
WOUND_SOURCES: tuple[str, ...] = ("injury", "disease", "poison", "deprivation")
#: A wound's severities, least first; "incapacitating" is the
#: incapacitated flag's.
WOUND_SEVERITIES: tuple[str, ...] = ("light", "medium", "heavy", "incapacitating")
#: A bruise's severities (Lords of Men p. 132).
BRUISE_SEVERITIES: tuple[str, ...] = (
    "light",
    "medium",
    "heavy",
    "incapacitating",
    "fatal",
)


@dataclass
class WoundState:
    """What one wound carries beyond its severity: where it came from, and
    the +3s its stable Recovery rolls have built up (DE p. 405), and the
    Chirurgy of whoever gave it first aid (Art & Academe's medicine; 0:
    none)."""

    severity: str = "light"
    source: str = "injury"
    bonus: int = 0
    first_aid: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WoundState:
        return cls(**known_fields(cls, data))


@dataclass
class Disease:
    """A disease the character has, with Art & Academe's medicine on (pp.
    45-51): its stage now and the one it began at, its Severity at that
    first stage, its Ease Factors (None: none, as for a lifelong one) and
    the time between its Recovery rolls ("week", "month", "season",
    "lifelong"); whether it gives a Disease Penalty (False: Flaws instead),
    the +3s its stable rolls have built up and, in a Crisis, the
    cumulative -1 of its rolls so far, and a successful surgery's +3 to
    its next Recovery roll."""

    name: str
    level: str = "Minor"
    first_level: str = "Minor"
    severity: int = 6
    stable: int | None = 6
    improve: int | None = 12
    interval: str = "week"
    penalty: bool = True
    bonus: int = 0
    crisis: int = 0
    notes: str = ""
    surgery: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Disease:
        return cls(**known_fields(cls, data))


@dataclass
class Wounds:
    """Per-severity counts -- the boxes on the paper sheet -- with, for each
    wound, its source and stable-roll bonus in `states` (lined up with the
    counts by rules.recovery.states; a wound with none is an injury with no
    bonus)."""

    light: int = 0
    medium: int = 0
    heavy: int = 0
    incapacitated: bool = False
    dead: bool = False
    #: A character's typed adjustment on top of the Soak worked out from
    #: Stamina, armour and Virtues (rules.derived.soak); a
    #: familiar's wounds leave it 0 (a familiar has base_soak).
    soak: int = 0
    states: list[WoundState] = field(default_factory=list)
    #: Magical aid to every Recovery roll, typed (a Zenodochium's +9, a
    #: Purification of the Festering Wound).
    aid: int = 0
    #: For an Incapacitating wound, the cumulative -1 of its rolls so far.
    crisis: int = 0
    #: Bruises by severity (Lords of Men's option): they heal within hours
    #: and leave a residual wound.
    bruises: dict[str, int] = field(default_factory=dict)
    #: Diseases as their own records (Art & Academe's medicine), and the
    #: conditions the patient heals in (rules.disease.CONDITIONS keys),
    #: each a Recovery Modifier with its extra botch die.
    diseases: list[Disease] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Wounds:
        d = dict(data)
        d["states"] = [WoundState.from_dict(s) for s in d.get("states") or []]
        d["bruises"] = {
            k: int(v) for k, v in (d.get("bruises") or {}).items() if int(v) > 0
        }
        d["diseases"] = [Disease.from_dict(x) for x in d.get("diseases") or []]
        d["conditions"] = [str(x) for x in d.get("conditions") or []]
        return cls(**known_fields(cls, d))

    def with_counts(self, **counts: Any) -> Wounds:
        """These wounds with new counts (Edit Wounds), keeping each
        remaining wound's state and the aid."""
        return Wounds(
            **counts,
            states=list(self.states),
            aid=self.aid,
            crisis=self.crisis,
            bruises=dict(self.bruises),
            diseases=list(self.diseases),
            conditions=list(self.conditions),
        )


MERCURIAN_MAGIC = "vf_mercurian_magic"


#: The styles of certamen, by id; their rules are rows in
#: rules.certamen_styles (HoH: True Lineages pp. 135-139).
CERTAMEN_STYLES: tuple[str, ...] = (
    "gladiator",
    "andabatus",
    "bestiarius",
    "bone_biting",
    "charon",
    "essedarius",
    "gladiatrix",
    "hoplomachus",
    "laquerius",
    "provocator",
    "pumilius",
    "retiarius",
    "saggitarius",
    "scissor",
    "velitus",
)


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
    #: House Tremere: the magus holds his own voting sigil (won from his
    #: parens in certamen); otherwise a parens holds it (rules.sigils).
    holds_own_sigil: bool = False
    #: House Tremere: the magus has made his one challenge for his sigil at
    #: a time of his choosing; later ones wait for the House's Decennials
    #: (rules.sigils, HoH: TL p. 123).
    sigil_challenged: bool = False
    #: The school of certamen he was trained in, one of CERTAMEN_STYLES
    #: ("" for none recorded; HoH: TL p. 135).
    certamen_school: str = ""
    #: A Mercurian magus has learned Road Magic's Ranges and Targets, a
    #: season's teaching with no further Virtue (TMRE p. 116).
    road_magic: bool = False
    #: Cast out of the Order by a Wizard's March: the year, and the
    #: Tribunal (and case) that renounced him (rules.hermetic_law).
    renounced_year: int | None = None
    renounced_by: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HermeticBackground:
        hermetic = cls(**known_fields(cls, data))
        school = hermetic.certamen_school
        if school and school not in CERTAMEN_STYLES:
            raise ValueError(f"Unknown school of certamen {school!r}")
        return hermetic


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
class Investment:
    """A merchant's investment still open (City & Guild pp. 110-122,
    rules.merchants): its kind, what it is in, the Labor Points put in
    and the year, what it pays back (an introduction's, once, in its
    due year; a smuggling sponsor's, each Winter) and when. A charity
    keeps the Labor Points given in all, the last gift and its year, the
    Reputation experience already gained from it, that Reputation, and
    the kind of merchant giving (rules.merchants.STATUS_MULTIPLIER)."""

    kind: str
    name: str = ""
    lp: int = 0
    year: int = 0
    returns: int = 0
    due_year: int | None = None
    paid: int = 0
    reputation: str = ""
    merchant: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Investment:
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
    #: The last season worked on it ("" and None: not recorded), for work
    #: whose points last only over consecutive seasons (taming).
    last_season: str = ""
    last_year: int | None = None

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
class Discipline:
    """A reward, punishment or pension given to one of the covenfolk
    (Grogs pp. 23-26; rules.grog_discipline): when it began, its kind
    (grog_discipline.KINDS), how many seasons it lasts (0: less than a
    season, or done at once; None: for good), the rank he holds after a
    promotion or a reduction in rank, and a note."""

    year: int
    season: str = "Spring"  # one of SEASONS
    kind: str = ""
    seasons: int | None = 0
    rank: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Discipline:
        return cls(**known_fields(cls, data))


#: What a tradition's member knows or makes, as the books name them:
#: effects cast, and items made in a season.
TRADITION_EFFECT_KINDS: tuple[str, ...] = (
    "spell",
    "charm",
    "rune script",
    "rite",
    "power",
)
TRADITION_ITEM_KINDS: tuple[str, ...] = (
    "amulet",
    "charta",
    "fetish",
    "potion",
    "tattoo",
    "wondrous item",
)


@dataclass
class TraditionEffect:
    """A hedge tradition's spell, charm, rune script or other effect the
    character knows, or an item they made (an amulet, a fetish, a
    potion): the casting rule it uses (one of the tradition's
    CastingRules, by name), the Arts, Ability or runes it uses, its
    level, and an item's charges."""

    name: str
    tradition: str = ""
    kind: str = "spell"
    rule: str = ""
    uses: list[str] = field(default_factory=list)
    level: int = 0
    #: Range, Duration and Target, or what it does, in the book's words.
    parameters: str = ""
    #: An item's charges or doses left (0: none counted).
    charges: int = 0
    notes: str = ""
    #: The tradition's guideline it is built on (TraditionDef.guidelines,
    #: by name), its Range, Duration and Target (one of the tradition's
    #: EffectParameters, by name), and further magnitudes (size,
    #: complexity): with a guideline the level is worked out from them
    #: (rules.hedge_effects.effect_level), and `level` is kept for an
    #: effect that names none.
    guideline: str = ""
    range: str = ""
    duration: str = ""
    target: str = ""
    magnitudes: int = 0

    def __post_init__(self) -> None:
        kinds = TRADITION_EFFECT_KINDS + TRADITION_ITEM_KINDS
        if self.kind not in kinds:
            raise ValueError(f"Unknown kind {self.kind!r}; must be one of {kinds}")

    @property
    def item(self) -> bool:
        return self.kind in TRADITION_ITEM_KINDS

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> TraditionEffect:
        return cls(**known_fields(cls, d))


@dataclass
class CharacterPower:
    """A supernatural power a Virtue grants (rules.powers): the Virtue
    ("Greater Power", "Lesser Power", "Personal Power", "Ritual Power",
    "Focus Power"), its Arts, its level (a Focus Power's greatest effect)
    and the Penetration bought for it, its Range, Duration and Target, and
    whether it is constant (a Personal Power must be that or Range
    Personal)."""

    name: str = ""
    virtue: str = "Lesser Power"
    technique: str = ""
    form: str = ""
    level: int = 0
    penetration: int = 0
    range: str = ""
    duration: str = ""
    target: str = ""
    constant: bool = False
    #: A Focus Power's field, or what the power does.
    description: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> CharacterPower:
        return cls(**known_fields(cls, d))


@dataclass
class ConstantEffect:
    """A supernatural effect the character is under all the time (or at
    least half of it), which warps them each year (DE pp. 390-391): its
    realm, whether it is powerful (sixth magnitude or more) and whether it
    was cast by them or designed for them. A Longevity Ritual, Parma
    Magica, the Aegis and a familiar's bond aren't listed: the app counts
    the ritual itself, and the others don't warp."""

    name: str = ""
    realm: str = "Magic"
    powerful: bool = False
    designed_for: bool = False
    description: str = ""
    id: str = field(default_factory=new_instance_id)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> ConstantEffect:
        return cls(**known_fields(cls, d))


#: What a bound being's bond adds to: the master's casting totals, his
#: Lab Totals, or nothing the app works out.
BOND_APPLIES: tuple[str, ...] = ("casting", "lab", "")


@dataclass
class BoundBeing:
    """A being bound to a tradition's member (a familiar, a fetch, a
    spirit, an animated statue): its kind (the tradition's BondRule), the
    Bestiary record it is, if any, and the bonus its bond adds to the
    master's totals of that tradition."""

    name: str
    tradition: str = ""
    kind: str = ""
    creature_id: str = ""
    bonus: int = 0
    applies_to: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if self.applies_to not in BOND_APPLIES:
            raise ValueError(
                f"Unknown applies_to {self.applies_to!r}; must be one of {BOND_APPLIES}"
            )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> BoundBeing:
        return cls(**known_fields(cls, d))


@dataclass
class ResearchAttempt:
    """One season's work toward a research goal, as its Research log shows
    it: what was done, the chart roll (stress die + risk), any move of it,
    and what came of it."""

    year: int
    season: str
    #: "seek" (an experiment seeking a Discovery), "stabilize", "insight"
    #: (a season studying a source) or "invent insight" (its effect).
    kind: str
    #: The spell, enchantment or source worked on.
    work: str = ""
    magnitude: int = 0
    lab_total: int = 0
    risk: int = 0
    #: The stress die (None: no chart roll, as for an insight season).
    die: int | None = None
    #: How many botch dice a 0 would have rolled, and how many came up 0.
    botch_dice: int = 0
    zeroes: int = 0
    #: The move made to the chart roll (0: none).
    move: int = 0
    #: The chart results, in words.
    result: str = ""
    discovery: bool = False
    #: An insight season's source gave its insight.
    insight: bool = False
    #: Breakthrough points gained, and Warping Points taken.
    points: int = 0
    warping: int = 0
    lab_id: str = ""
    #: What the season left on the work (side and modified effects).
    effects: list[ExperimentalEffect] = field(default_factory=list)

    @property
    def roll(self) -> int | None:
        """The chart roll before any move: the die + the risk."""
        return None if self.die is None else self.die + self.risk

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ResearchAttempt:
        d = dict(data)
        d["effects"] = experimental_effects(d.get("effects"))
        return cls(**known_fields(cls, d))


@dataclass
class Breakthrough:
    """A magus's Arcane Discovery goal: what it is, its kind and
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
    #: After a failed stabilization, the season it must be retried in
    #: (consecutive seasons only; "" when none failed).
    retry_season: str = ""
    retry_year: int = 0
    #: The spells and enchantments (lower-case names) that gave a Discovery
    #: toward it: each gives one at most.
    discovered_from: list[str] = field(default_factory=list)
    #: Insights gained and not yet invented.
    insights: int = 0
    reached: bool = False
    #: The storyguide keeps the target secret: the sheet shows the points
    #: gained, not how many are needed.
    hidden_target: bool = False
    #: Every season's work toward it, oldest first.
    log: list[ResearchAttempt] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Breakthrough:
        values = known_fields(cls, data)
        values["log"] = [ResearchAttempt.from_dict(a) for a in values.get("log", [])]
        return cls(**values)


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
    rolled up to (None: not yet). A grog's pre-play aging may instead come
    from the Grogs Aging Chart: the kind of aging taken ("mild", "average"
    or "harsh"; "" when it wasn't used) and how far it moved the Ability
    cap at creation."""

    lab_seasons: int = 0
    aura: int = 3
    lab_quality: int = 0
    living_conditions: int = 1
    aged_to: int | None = None
    aging_chart: str = ""
    aging_chart_cap: int = 0
    #: A young character's parent's vocation: the Ability the same-sex
    #: parent earns a living by ("Craft: Smith"; "" for none given) and
    #: the parent's score in it, which caps the child's to age 14 at half.
    vocation: str = ""
    vocation_score: int = 0


@dataclass
class AnimalForm:
    """What makes a grog an animal (Grogs, Chapter 7, Horses & Hounds):
    the bestiary's kind it belongs to (rules.animal_grogs.KINDS: "clawed",
    "hoofed", "bird" or "fish"), its species ("Dog"), the Language its
    kind speaks ("Dog", fixed at 2) and, for a species the storyguide
    gives its own average lifespan, that lifespan in years (None: the
    kind's own)."""

    kind: str = "clawed"
    species: str = ""
    language: str = ""
    lifespan: int | None = None
    #: Its fur, feathers or scales: Protection of at least 1 for most
    #: animals (Grogs p. 137), before the Qualities that add more.
    protection: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnimalForm:
        return cls(**known_fields(cls, data))


@dataclass
class LabTextAccess:
    """How far a magus can read one author's raw Lab Texts: up to `level`, and how that
    was gained -- "decoded", "taught" (the author's abbreviations) or "" (not
    recorded); "assisted": helped make the text (DE p. 263)."""

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
    #: The non-Hermetic traditions the character belongs to
    #: (tradition_catalog.json ids); each has its own chapter of the sheet.
    traditions: list[str] = field(default_factory=list)
    #: What the character knows or made of their traditions' magic.
    tradition_effects: list[TraditionEffect] = field(default_factory=list)
    #: The supernatural powers its Virtues grant (rules.powers).
    powers: list[CharacterPower] = field(default_factory=list)
    #: Supernatural effects on the character all the time (Warping each
    #: year).
    constant_effects: list[ConstantEffect] = field(default_factory=list)
    #: Beings bound to the character by a tradition, and the points in
    #: each of their traditions' pools ("<tradition id>:<pool name>").
    bound_beings: list[BoundBeing] = field(default_factory=list)
    tradition_pools: dict[str, int] = field(default_factory=dict)
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
    #: How many of the Fatigue levels lost are long-term (DE p. 404): the
    #: more serious levels count as short-term.
    long_term_fatigue: int = 0
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
    #: Arcane Discovery goals.
    breakthroughs: list[Breakthrough] = field(default_factory=list)
    #: A grog's yearly update; None until set up.
    grog_year: GrogYear | None = None
    #: An animal grog's kind, species and Language; None for a person
    #: (older saves load as people).
    animal: AnimalForm | None = None
    #: The supplements' sub-systems: Labor Points and a
    #: workshop's scores (City & Guild), progress records, experimental
    #: philosophy formulas known, and the Ordeals still lowering the Target
    #: of a later Initiation.
    labor_points: int = 0
    #: The band of the business's income (City & Guild p. 37: "trivial"
    #: ... "legendary"); "" takes it from the Social Status Virtue.
    income_band: str = ""
    investments: list[Investment] = field(default_factory=list)
    workshop_innovation: int = 0
    workshop_raw_materials: int = 0
    progress: list[Progress] = field(default_factory=list)
    formulas: list[str] = field(default_factory=list)
    #: Experimental philosophy: each formula's kind, level and Laboratory
    #: Text (older saves load with none).
    formula_designs: list[Formula] = field(default_factory=list)
    ordeals: list[Ordeal] = field(default_factory=list)
    #: Master of None: each subject ("art:Ignem") an Advancement Total
    #: raised, and the last year it did.
    advanced: dict[str, int] = field(default_factory=dict)
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
    #: How much of the character is written down (world.DETAIL_LEVELS):
    #: a Line or Sketch character is part of the world but not of play.
    #: Older saves load as Full.
    detail: str = FULL
    #: A paragraph about the character in the saga.
    summary: str = ""
    #: What only the storyguide should read: the record's Secrets
    #: chapter, hidden from players signed in to a hosted copy.
    secrets: str = ""
    links: list[Link] = field(default_factory=list)
    #: The people he controls through personal bonds, and the Agency
    #: experience not yet spent on them (Lords of Men pp. 22-25).
    agents: list[Agent] = field(default_factory=list)
    agency_xp: int = 0
    #: The rewards, punishments and pension of one of the covenfolk.
    discipline: list[Discipline] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        # Older saves kept secrets under a heading in the summary.
        d = move_secrets(dict(data), "summary")
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
        d["reputations"] = [reputation_from_dict(t) for t in d.get("reputations", [])]
        d["hermetic"] = HermeticBackground.from_dict(d.get("hermetic") or {})
        if "road_magic" not in (data.get("hermetic") or {}) and any(
            vf.get("vf_id") == MERCURIAN_MAGIC for vf in data.get("virtues_flaws", [])
        ):
            # Saves from before Road Magic needed learning: a Mercurian
            # magus keeps the Road Ranges and Targets he had.
            d["hermetic"].road_magic = True
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
        d["powers"] = [CharacterPower.from_dict(x) for x in d.get("powers", [])]
        d["constant_effects"] = [
            ConstantEffect.from_dict(x) for x in d.get("constant_effects", [])
        ]
        d["tradition_effects"] = [
            TraditionEffect.from_dict(e) for e in d.get("tradition_effects", [])
        ]
        d["bound_beings"] = [BoundBeing.from_dict(b) for b in d.get("bound_beings", [])]
        if d.get("grog_year") is not None:
            d["grog_year"] = GrogYear.from_dict(d["grog_year"])
        if d.get("animal") is not None:
            d["animal"] = AnimalForm.from_dict(d["animal"])
        d["progress"] = [Progress.from_dict(p) for p in d.get("progress", [])]
        d["investments"] = [Investment.from_dict(i) for i in d.get("investments", [])]
        d["links"] = [Link(**known_fields(Link, x)) for x in d.get("links", [])]
        d["agents"] = [Agent.from_dict(a) for a in d.get("agents", [])]
        d["discipline"] = [Discipline.from_dict(x) for x in d.get("discipline", [])]
        d["ordeals"] = [Ordeal.from_dict(o) for o in d.get("ordeals", [])]
        d["formula_designs"] = [
            Formula.from_dict(f) for f in d.get("formula_designs", [])
        ]
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
