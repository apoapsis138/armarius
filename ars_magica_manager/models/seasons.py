"""Season plans, lab projects and season records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .artwork import ArtworkPlan
from .common import (
    SEASONS,
    Change,
    ExperimentalEffect,
    experimental_effects,
    known_fields,
)
from .mystery_scripts import ScriptPart


def season_order(*, season: str | None, year: int) -> int:
    """A season as a number that sorts by date (an unknown season counts as
    Spring). Keyword-only, so season and year can't be swapped."""
    return year * len(SEASONS) + (SEASONS.index(season) if season in SEASONS else 0)


def next_season(season: str, year: int) -> tuple[str, int]:
    """The season after (season, year). The ArM5 year begins in Spring, so
    Winter rolls over into Spring of the following year."""
    index = SEASONS.index(season)
    if index == len(SEASONS) - 1:
        return SEASONS[0], year + 1
    return SEASONS[index + 1], year


@dataclass
class XpAllocation:
    """Where some of a season's Source Quality goes: `subject` is
    "ability:<name>", "art:<art>" or "mastery:<spell id>" (see
    rules.activities.subject_label), `points` its share (Adventure splits its
    Source Quality, Exposure may split its 2 points)."""

    subject: str
    points: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> XpAllocation:
        return cls(**known_fields(cls, data))


@dataclass
class SpellDesign:
    """A spell being invented: started from a spell or from
    nothing, and edited freely. It lives on the plan until the spell is
    invented; only then is it added to the magus's spells."""

    #: Identifies the design across the seasons it takes (its project).
    key: str
    name: str = ""
    technique: str = ""
    form: str = ""
    requisites: list[str] = field(default_factory=list)
    base_level: int | None = None
    range: str = "Personal"
    duration: str = "Momentary"
    target: str = "Individual"
    #: Magnitudes of a Range/Duration/Target the app doesn't know (a
    #: breakthrough, a troupe ruling), by "range"/"duration"/"target".
    custom_steps: dict[str, int] = field(default_factory=dict)
    #: Size, complexity and requisite magnitudes on top.
    extra_magnitudes: int = 0
    ritual: bool = False
    #: A Creo effect that makes something meant to last past its Duration
    #: (a wall that stays, food that feeds): it needs a Ritual (DE p. 311).
    lasting: bool = False
    #: Spell Timing: how often the spell recurs (a
    #: rules.spell_levels.RECURRING key; "" for a spell that doesn't).
    recurring: str = ""
    description: str = ""
    base_effect: str = ""
    #: The spell it was started from, if any.
    source_spell_id: str | None = None
    #: The level as printed, for a spell started from one with no base
    #: level recorded (None: worked out from the base level).
    printed_level: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SpellDesign:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonPlan:
    """What a character will do in one season: typed by the user,
    locked in until the season is applied. Its outcome is always worked out
    (rules.activities.outcome), never stored."""

    character_id: str
    year: int
    season: str  # one of SEASONS
    activity: str  # a rules.activities.ACTIVITIES key
    allocations: list[XpAllocation] = field(default_factory=list)
    #: Practice / Adventure: the Source Quality when it isn't the rule's
    #: default (None: the default).
    source_quality: int | None = None
    #: Full months of the season lost to distractions (0-3).
    months_lost: int = 0
    #: Teaching, training, writing and copying: whether the season is
    #: spent in the laboratory, where its Teaching and Texts
    #: Specializations help (DE p. 291).
    in_lab: bool = True
    #: Free text: what "Other" was, or notes kept with the Diary entry.
    details: str = ""
    #: Reading: the book studied.
    book_id: str | None = None
    #: Working from Lab Texts: the further texts, of the same Technique and
    #: Form, learned in the same season.
    more_book_ids: list[str] = field(default_factory=list)
    #: Being taught / trained: the teacher or master.
    teacher_id: str | None = None
    #: Opening the Arts: keep the apprentice's Supernatural Abilities (an
    #: Intellego Vim Lab Total of at least double their level allows it).
    keep_supernatural: bool = False
    #: Opening the Arts at double the Lab Total needed: the Hermetic Virtues
    #: (ids) the apprentice's Supernatural Abilities become instead, one for
    #: each, of its size (DE p. 271); empty to keep or lose them. A save from
    #: before held one, `convert_to`, read into it at load.
    conversions: list[str] = field(default_factory=list)
    #: Teaching a Hermetic Virtue: a Hermetic Flaw of the teacher's taught
    #: with it (DE p. 271).
    taught_flaw_id: str | None = None
    #: Learning spells from a teacher: the spells taught.
    taught_spell_ids: list[str] = field(default_factory=list)
    #: Vis study: whose raw vis is used ("character" or "laboratory").
    vis_from: str = ""
    #: Vis study: the stress die as rolled at the table (None: the app
    #: rolls it when the season is applied).
    die: int | None = None
    #: Lab work: the laboratory it is done in. A plan with a
    #: laboratory is made on the lab's Planning tab.
    lab_id: str | None = None
    #: Inventing: the spell invented (a Lab Text's spell when working from one).
    spell_id: str | None = None
    #: Inventing: a similar spell the magus knows (adds its magnitude).
    similar_spell_id: str | None = None
    #: Lab work: days away from the laboratory (a short adventure, travel...);
    #: 11-20 lower the Lab Total, more rule lab work out.
    days_away: int = 0
    #: Inventing: the spell being designed (the Invent Spell screen).
    design: SpellDesign | None = None
    #: Lab work: the magus's Magical Focus applies (the lower Art counts
    #: twice), their Magic Theory Specialty applies (+1), and any other
    #: modifier the troupe allows.
    focus: bool = False
    #: The Magical Focus applies when the work's Arts are among those the
    #: focus records (lab_seasons.in_focus), instead of by the tick.
    focus_by_arts: bool = False
    theory_specialty: bool = False
    other_modifier: int = 0
    #: Recreating what an experiment left flawed: the Magic Theory score
    #: the magus had when he experimented, added again (DE p. 274); 0: not.
    recreating_theory: int = 0
    #: The flawed creation recreated (rules.recreating: "spell:<id>",
    #: "effect:<id>", "longevity:<subject id>"); "": none, or a plan from
    #: before it was chosen, whose typed score stands alone.
    recreating: str = ""
    #: Lab work spent on a staged Hermetic Project's stage (a ProjectStage
    #: id): the season goes into the project's works; "" for none.
    project_stage: str = ""
    #: Lab work on a dark or sinister effect: a chthonic magus's Chthonic
    #: Magic stands in for Magic Theory (RoP: The Infernal p. 123).
    chthonic: bool = False
    #: Lab work's Virtue options (rules.lab_virtues): Potent Magic's field,
    #: Cyclic Magic's good time covering the season or its bad time
    #: touching it, Environmental Magic Condition holding; a Laboratory
    #: Horoscope's bonus (+1 to +5, 0: none) and its stress die as rolled
    #: at the table (None: rolled when the season is applied).
    potent: bool = False
    cycle_bonus: bool = False
    cycle_penalty: bool = False
    condition: bool = False
    horoscope: int = 0
    horoscope_die: int | None = None
    #: Extracting vis: the Form extracted ("": Vim), with Hermetic Alchemy
    #: or an Extractor of (Form) Vis.
    extract_form: str = ""
    #: Longevity Ritual: who it is for (the magus when None), the
    #: Art of the vis paid with, and extra pawns (+1 Lab Total each). Being
    #: its subject: the magus making it.
    subject_id: str | None = None
    vis_art: str = ""
    extra_vis: int = 0
    #: Hermetic Viresculture: the Stirpes worked on in the same season
    #: besides the one named in `title` (name -> Magic Might, or a Lesser
    #: Enchantment Vis's level; -1 when none was typed).
    more_stirpes: dict[str, int] = field(default_factory=dict)
    #: Longevity Ritual: made fertile from a Lab Text for an effect using
    #: the Fertile Longevity Ritual breakthrough (or as its discoverer
    #: taught), for a magus who hasn't reached it himself.
    fertile_text: bool = False
    #: Enchanting and familiar work: pawns paid in the work's other Art
    #: (its Form when `vis_art` is its Technique, and the other way round);
    #: the rest are of `vis_art`.
    other_vis: int = 0
    #: Fixing an Arcane Connection: the laboratory's connection fixed.
    connection_id: str | None = None
    #: Enchanting: the enchanted device worked on, the effect
    #: instilled (or made), and the shape and material bonus that applies.
    device_id: str | None = None
    effect_id: str | None = None
    shape_bonus: int = 0
    #: Opening or instilling a talisman: the one attunement it gains this
    #: season, as "<device id>:<index of its Shape & Material bonus>"
    #: (DE p. 259); "" for none.
    attunement: str = ""
    #: Binding a familiar: the Technique and Form used, and the
    #: cords the Lab Total buys (0-5 each).
    technique: str = ""
    form: str = ""
    golden_cord: int = 0
    silver_cord: int = 0
    bronze_cord: int = 0
    #: Writing, copying and translating books: the title, the
    #: summa's Level (None: the most the author can), the language written
    #: or translated into, and a quick copy.
    title: str = ""
    book_level: int | None = None
    language: str = ""
    quick: bool = False
    #: Translating: the translator has (Area) Lore 3 of the source text's
    #: culture, so the translation keeps the culture's Quality point.
    culture_lore: bool = False
    #: Useful correspondence this season (Covenants, Other Opus Types): the
    #: subject it is on (a rules.activities subject, "ability:Magic
    #: Theory"), worth +1 xp in it; "" for none.
    correspondence: str = ""
    #: Reading: the reader glosses the book this season (+1 Quality, once).
    gloss: bool = False
    #: Reading or vis study: the Art's substance is present (Study Bonus's
    #: +2; Study Requirement's condition).
    art_present: bool = False
    #: Secondary Insight: the Arts its bonus experience goes to (empty:
    #: the lowest-scored).
    insight_arts: list[str] = field(default_factory=list)
    #: Editing a florilegium: the subject ("art:Vim", "ability:Medicine")
    #: whose tractatus it binds.
    florilegium_subject: str = ""
    #: Moving a laboratory: by spell (one season, a roll) rather
    #: than mundane means, and where to.
    by_spell: bool = False
    #: Supplement seasons: the Characteristic a total uses.
    characteristic: str = ""
    #: Experimentation: whether the season experiments, its
    #: risk modifier, the simple die added to the Lab Total (None: rolled
    #: when played), and the research goal it seeks a Discovery for.
    experimenting: bool = False
    risk: int = 0
    experiment_die: int | None = None
    research: str = ""
    research_kind: str = "Minor"
    #: Undergoing an Initiation: what the Virtue initiated (effect_id) and
    #: the Flaw an Ordeal gains (device_id) name, as the picker asked for it
    #: ({"art": "Ignem"}); the kind of Ordeal ("gain" a Flaw, "lose" a
    #: Virtue, "raise" a Minor Flaw to Major; "" in an older plan: a Flaw,
    #: its size in research_kind), and the Virtue it takes away or the
    #: Minor Flaw it raises.
    effect_params: dict[str, str] = field(default_factory=dict)
    ordeal_params: dict[str, str] = field(default_factory=dict)
    ordeal_kind: str = ""
    ordeal_lost_id: str | None = None
    ordeal_lost_params: dict[str, str] = field(default_factory=dict)
    #: Undergoing an Initiation that always brings a Flaw with a condition
    #: (Glamour's Vulnerable Magic): the condition, which must be new to
    #: the magus ("" when not named).
    ordeal_condition: str = ""
    #: Undergoing the Ritual of Twelve Years: the Initiate has bound a
    #: familiar at some time (one since dead or released, which the saga no
    #: longer holds), so the Ritual fails.
    familiar_ever_bound: bool = False
    #: Varying the Script this Initiation (rules.mysteries.VARY_EASE: "add",
    #: "change", "remove"; "" for none) and what the change does to its
    #: bonus.
    script_variation: str = ""
    variation_bonus: int = 0
    #: An Initiation by a hedge tradition's Script ("tradition id/Script
    #: name"; "" for a Hermetic Mystery), whether the Mystagogue is known to
    #: have the power (besides holding the Virtue initiated), and an
    #: experimental Script: its sympathy bonus (its risk is `risk`).
    hedge_script: str = ""
    knows_power: bool = False
    experimental_script: bool = False
    script_sympathy: int = 0
    #: The aura where the work is done, when it isn't the character's
    #: home: a folk witches' sabbat's site (always Magic: it caps the
    #: witches who may help), a wondrous item's workshop, with its realm
    #: (`site_realm`, "" for Magic). None: not entered.
    site_aura: int | None = None
    site_realm: str = ""
    #: A plan saved for several seasons: what ties its seasons together
    #: ("" for a single season, and for lab work, which its project ties),
    #: whether it runs until its work is done (its seasons are worked out
    #: again after each), and, on its last season, how many more the work
    #: needs that couldn't be planned (the season after was taken).
    series: str = ""
    until_done: bool = False
    more_needed: int = 0
    #: Paired plans: lab work's assistants (each planned to Assist), the
    #: subject a teacher teaches the student in `subject_id`, and on a plan
    #: made to pair another's, whose plan made it.
    assistant_ids: list[str] = field(default_factory=list)
    student_subject: str = ""
    partner_id: str = ""
    #: Planned by the saga's default for a season with nothing planned.
    by_default: bool = False
    #: Assisting in a stressful laboratory season: the apprentice's
    #: Turbulence check midway through it (rules.turbulence: "none",
    #: "controlled", "uncontrolled", which halves his aid; "" unchecked).
    turbulence: str = ""
    #: Creating a work of art: the piece's kind, bonuses and risks (None:
    #: a season's piece with none of them).
    artwork: ArtworkPlan | None = None
    #: Undergoing an Initiation: the Script written out as its components
    #: (rules.mysteries; empty: the Script bonus alone is typed).
    script_components: list[ScriptPart] = field(default_factory=list)
    #: An Initiation's sacrifice: what is given up ("device:<id>",
    #: "item:<id>", "book:<id>", "familiar:<id>", "apprentice:<id>",
    #: "wealth", "vis", "service"), taken when it's played.
    sacrifice: str = ""
    #: A sacrifice of vis: its Art and pawns, from the plan's vis source.
    sacrifice_art: str = ""
    sacrifice_pawns: int = 0
    #: Campaigning: the disease a whole year in the army risks ("" the
    #: Bloody Flux, common in campaigning armies, A&A p. 47).
    camp_disease: str = ""
    #: Reinventing the Lesser Elixir: its new ingredient (`title`, its bonus
    #: in `book_level`) is one the alchemist devised himself (TMRE p. 42).
    devised: bool = False
    #: Ordination (The Church p. 33): the grade sought is `title`; who
    #: examines him, and whether he is ordained outside his birth diocese.
    examiner: str = ""
    ordained_elsewhere: bool = False
    #: Ordination: take the grade's Social Status in place of his own (the
    #: swap is offered; False leaves his status for the troupe to change).
    swap_status: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonPlan:
        d = dict(data)
        d["script_components"] = [
            ScriptPart.from_dict(p) for p in d.get("script_components") or []
        ]
        d["allocations"] = [XpAllocation.from_dict(a) for a in d.get("allocations", [])]
        if d.get("design") is not None:
            d["design"] = SpellDesign.from_dict(d["design"])
        if d.get("artwork") is not None:
            d["artwork"] = ArtworkPlan.from_dict(d["artwork"])
        d["more_stirpes"] = _stirpes(d.get("more_stirpes"))
        old = d.pop("convert_to", "")
        if old and not d.get("conversions"):
            d["conversions"] = [str(old)]
        d["conversions"] = [str(v) for v in d.get("conversions") or [] if v]
        return cls(**known_fields(cls, d))


def _stirpes(raw: object) -> dict[str, int]:
    """A saved plan's other Stirpes, checked: names to whole numbers."""
    if not raw:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f"A season plan's other Stirpes aren't a mapping: {raw!r}")
    found: dict[str, int] = {}
    for name, might in raw.items():
        if not isinstance(might, int) or isinstance(might, bool):
            raise ValueError(
                f"Stirps {name!r} in a season plan has a Might that isn't a "
                f"whole number: {might!r}"
            )
        found[str(name)] = might
    return found


@dataclass
class LabProject:
    """Lab work that runs over several seasons: the points a
    magus has put into inventing a spell so far."""

    character_id: str
    spell_id: str
    points: int = 0
    #: Experimental side effects and modified effects so far.
    effects: list[ExperimentalEffect] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LabProject:
        d = dict(data)
        d["effects"] = experimental_effects(d.get("effects"))
        return cls(**known_fields(cls, d))


#: How often a storyguide's calendar entry repeats.
ONCE, YEARLY, EVERY = "Once", "Each year", "Every N years"
REPEATS: tuple[str, ...] = (ONCE, YEARLY, EVERY)


@dataclass
class CalendarEntry:
    """Something the storyguide wrote into the saga's calendar, for Ahead
    to show: in its season, once, each year or every `every` years (see
    REPEATS), for one covenant or (None) the whole saga."""

    title: str
    year: int
    season: str = "Spring"
    repeats: str = ONCE
    every: int | None = None
    note: str = ""
    covenant_id: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CalendarEntry:
        return cls(**known_fields(cls, data))


@dataclass
class WorldTurn:
    """One yearly step (world_turns.py): the lines applied when Winter
    was played, and the changes they made, so deleting it undoes them."""

    year: int
    season: str = "Winter"
    lines: list[str] = field(default_factory=list)
    changes: list[Change] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldTurn:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonRecordLine:
    """One person's line in a season's record: kept as the text
    it showed, so it still reads right after the character is renamed or
    deleted."""

    character_id: str
    name: str
    covenant_id: str | None = None
    #: The activity's label; "" when nothing was planned.
    activity: str = ""
    #: What it was on ("Latin", Other's notes...).
    what: str = ""
    #: The result ("Latin +4 xp"), or why the plan wasn't carried out.
    result: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonRecordLine:
        return cls(**known_fields(cls, data))


@dataclass
class SeasonRecord:
    """What happened in one season, saved when it is applied if the saga
    keeps season records."""

    year: int
    season: str
    lines: list[SeasonRecordLine] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonRecord:
        d = dict(data)
        d["lines"] = [SeasonRecordLine.from_dict(line) for line in d.get("lines", [])]
        return cls(**known_fields(cls, d))
