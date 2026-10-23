"""Season plans, lab projects and season records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .common import (
    SEASONS,
    Change,
    ExperimentalEffect,
    experimental_effects,
    known_fields,
)


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
    #: Free text: what "Other" was, or notes kept with the Diary entry.
    details: str = ""
    #: Reading: the book studied.
    book_id: str | None = None
    #: Being taught / trained: the teacher or master.
    teacher_id: str | None = None
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
    theory_specialty: bool = False
    other_modifier: int = 0
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
    #: Fixing an Arcane Connection: the laboratory's connection fixed.
    connection_id: str | None = None
    #: Enchanting: the enchanted device worked on, the effect
    #: instilled (or made), and the shape and material bonus that applies.
    device_id: str | None = None
    effect_id: str | None = None
    shape_bonus: int = 0
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

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> SeasonPlan:
        d = dict(data)
        d["allocations"] = [XpAllocation.from_dict(a) for a in d.get("allocations", [])]
        if d.get("design") is not None:
            d["design"] = SpellDesign.from_dict(d["design"])
        return cls(**known_fields(cls, d))


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
