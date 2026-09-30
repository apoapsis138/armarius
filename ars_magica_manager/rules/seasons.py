"""Seasonal activities (STORY-903): which activities a character may plan for
a season, and what a planned season gives.

A plan is what the user typed (models.SeasonPlan); its outcome is always
worked out here from the saga as it stands, never stored. Advancing the
season works out every plan's outcome first and only then applies them
(ars_magica_manager.seasons), so a season's results never change that same
season's figures.

Who plans a season (DE Ch. 10, Assigning Seasons): a magus has four free
seasons a year; a companion (Mythic or not) works two seasons a year,
earning Exposure in their job, and has two free ones. Grogs aren't planned
season by season: they're updated once a year (Grogs, Ch. 5; STORY-924).

Activities built so far, each an Advancement Total (rules.study):

- Work / Exposure: Source Quality 2 in an Ability or Art used that season,
  or 1 each in two.
- Practice: Source Quality 4 in one Ability (languages among native
  speakers 8, Area Lore 5-7, forced practice of a trade 5: typed), or 5 in
  a spell's Mastery. Arts can't be practised.
- Adventure: Source Quality 5-10, split among the Abilities and Arts used,
  at most 5 to each.
- Read a book (STORY-902): a summa's Quality up to its Level, a tractatus's
  Quality once per reader. Only books in the covenant's library, or the
  reader's own (their inventory, their laboratory), can be read.
- Be taught: the teacher's Communication + Teaching + 3 (+6 for one
  student, +3 for two), up to the teacher's score; the teacher plans Teach
  (Exposure in Teaching or the language). Arts one-on-one; a teacher needs
  2 in an Ability or 5 in an Art, above the student's.
- Be trained: the master's score + 3, up to it; Abilities only; the master
  needs 2 or more, above the trainee's.
- Study from vis (magi): a stress die + the aura's modifier, using
  ceil(Art / 5) pawns (at least 1) of that Art's vis, with as many botch
  dice.
- Other: anything else, logged in the Diary without an automatic result
  until its own story is built.
"""

from __future__ import annotations

import random
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from .. import books
from ..arts import ART_BY_NAME, ARTS
from ..models import SEASONS, Book, Character, Saga, SeasonPlan, XpAllocation
from . import (
    aging,
    apprentice_seasons,
    book_seasons,
    derived,
    dice,
    enchant_seasons,
    experiment,
    familiar_seasons,
    lab_seasons,
    laboratory_seasons,
    realms,
    study,
    supplement_seasons,
    supplement_work,
    xp,
)
from .study import StudyResult, season_of_study

ASSIGNING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Assigning "
    "Seasons (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Ten:_Long-Term_Events#Assigning_Seasons)"
)
EXPOSURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Exposure "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Exposure)"
)
PRACTICE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Practice "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Practice)"
)
ADVENTURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Adventure "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Adventure)"
)
BOOKS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Books "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Books)"
)
TEACHING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Teaching "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Teaching)"
)
TRAINING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Training "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Training)"
)
VIS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Vis "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Vis)"
)
DISTRACTION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Distractions "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Ten:"
    "_Long-Term_Events#Distractions)"
)

#: The rule behind seasons as a whole (every rules module cites one).
SOURCE = ASSIGNING_SOURCE

#: The character types planned season by season (grogs are updated yearly).
PLANNED_TYPES: tuple[str, ...] = ("magus", "companion", "mythic companion")
#: The types that work two seasons a year (Assigning Seasons).
WORKING_TYPES: tuple[str, ...] = ("companion", "mythic companion")
#: Working seasons a companion owes each year.
WORKING_SEASONS_PER_YEAR = 2

OTHER = "other"
EXPOSURE = "exposure"
PRACTICE = "practice"
ADVENTURE = "adventure"
READ = "read"
TAUGHT = "taught"
TEACH = "teach"
TRAINED = "trained"
VIS_STUDY = "vis_study"
#: The activities that need the saga (books, teachers, vis) to work out.
STUDY_ACTIVITIES: tuple[str, ...] = (READ, TAUGHT, TEACH, TRAINED, VIS_STUDY)

#: Exposure's Source Quality, split 1 + 1 between two subjects.
EXPOSURE_QUALITY = 2
PRACTICE_QUALITY = 4
MASTERY_PRACTICE_QUALITY = 5
ADVENTURE_MIN, ADVENTURE_MAX = 5, 10
#: At most this much of an Adventure's Source Quality goes to one subject.
ADVENTURE_PER_SUBJECT = 5
#: How many subjects a plan can name (Adventure's split).
MAX_SUBJECTS = 3


@dataclass(frozen=True)
class Activity:
    """One seasonal activity: who may plan it, and the rule behind it."""

    key: str
    label: str
    summary: str
    source: str
    who: tuple[str, ...] = PLANNED_TYPES
    #: A companion's working season (Assigning Seasons).
    working: bool = False
    #: Whether it gives experience (Other doesn't, until its story).
    gives_xp: bool = True
    #: Whether time lost to distractions lowers it.
    distractable: bool = False
    #: Lab work: planned on the laboratory's Planning tab (STORY-901), not
    #: the character sheet.
    lab: bool = False
    #: Planned for the character by someone else's lab work (the subject of
    #: a Longevity Ritual), not picked from the menu.
    hidden: bool = False


ACTIVITIES: dict[str, Activity] = {
    a.key: a
    for a in (
        Activity(
            EXPOSURE,
            "Work / Exposure",
            "A season working, or using Abilities or Arts without studying: "
            "2 xp in one, or 1 each in two. A companion's working season.",
            EXPOSURE_SOURCE,
            working=True,
            distractable=True,
        ),
        Activity(
            PRACTICE,
            "Practice",
            "Practising one Ability (Source Quality 4; languages among native "
            "speakers 8, Area Lore 5-7, forced practice of a trade 5), or a "
            "spell's Mastery (5). Arts can't be practised.",
            PRACTICE_SOURCE,
            distractable=True,
        ),
        Activity(
            READ,
            "Read a book",
            "A season with a summa (its Quality, up to its Level) or a "
            "tractatus (its Quality, once), from the covenant's library or "
            "the reader's own books.",
            BOOKS_SOURCE,
            distractable=True,
        ),
        Activity(
            TAUGHT,
            "Be taught",
            "Taught by another character, who plans Teach: Communication + "
            "Teaching + 3, +6 for one student, +3 for two; up to their score.",
            TEACHING_SOURCE,
            distractable=True,
        ),
        Activity(
            TEACH,
            "Teach",
            "Teaching someone who plans Be taught: Exposure (2 xp) in Teaching "
            "or the language used.",
            TEACHING_SOURCE,
        ),
        Activity(
            TRAINED,
            "Be trained",
            "Trained in an Ability by a master: their score + 3, up to their "
            "score. The master can earn a living meanwhile.",
            TRAINING_SOURCE,
            distractable=True,
        ),
        Activity(
            VIS_STUDY,
            "Study from vis",
            "Studying an Art from its raw vis: a stress die + the aura, using "
            "ceil(Art / 5) pawns, with as many botch dice.",
            VIS_SOURCE,
            who=("magus",),
            distractable=True,
        ),
        Activity(
            lab_seasons.INVENT,
            "Invent a spell",
            "Inventing a spell in the laboratory: the Lab Total must be above "
            "its level; each season adds Lab Total - level points until they "
            "reach it.",
            lab_seasons.SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            lab_seasons.LAB_TEXT,
            "Invent from a Lab Text",
            "Working from a Lab Text: one season, if the Lab Total is at least "
            "the spell's level.",
            lab_seasons.LAB_TEXT_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            lab_seasons.EXTRACT,
            "Extract vis",
            "Extracting vis from the aura: Creo Vim Lab Total / 10 pawns of "
            "Vim, rounded up. Only in a Magic aura.",
            lab_seasons.EXTRACT_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            lab_seasons.FIX_AC,
            "Fix an Arcane Connection",
            "Making an Arcane Connection permanent: a season in the laboratory "
            "and 1 pawn of Vim vis.",
            lab_seasons.FIX_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            lab_seasons.LONGEVITY,
            "Longevity Ritual",
            "A Longevity Ritual: Creo Corpus Lab Total / 5 off aging rolls (/ 10 "
            "for a mundane subject); vis = the subject's age / 5.",
            lab_seasons.LONGEVITY_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.OPEN,
            "Open an item for enchantment",
            "Preparing an invested device: a season and its capacity in pawns "
            "of Vim vis (a talisman may be opened a few pawns at a time).",
            enchant_seasons.OPEN_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.INSTIL,
            "Instil an effect",
            "Instilling an effect in an opened device: Lab Total above its "
            "level, Lab Total - level points a season; its vis in the first.",
            enchant_seasons.INSTIL_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.LESSER_WORK,
            "Make a lesser enchantment",
            "A lesser enchanted device: one season, Lab Total at least twice "
            "the effect's level; level / 10 pawns of vis.",
            enchant_seasons.LESSER_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.CHARGED_WORK,
            "Make a charged item",
            "A charged item: one season, Lab Total at least the level, no "
            "vis; (Lab Total - level) / 5 charges, at least 1.",
            enchant_seasons.CHARGED_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.ATTUNE,
            "Attune a talisman",
            "Attuning an invested device you opened as your talisman: one "
            "season, no Lab Total needed; one talisman at a time.",
            enchant_seasons.ATTUNE_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            enchant_seasons.INVESTIGATE,
            "Investigate an enchanted item",
            "Intellego Vim Lab Total + a stress die against each hidden power, "
            "weakest first; the first failure ends the season.",
            enchant_seasons.INVESTIGATE_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            book_seasons.DECODE_TEXT,
            "Decode another magus's Lab Texts",
            "Decoding a raw Lab Text: the Lab Total in its Technique and Form "
            "each season until it reaches the level; then every text of that "
            "magus up to it can be read.",
            book_seasons.DECODE_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            lab_seasons.TAMING,
            "Tame a magical beast",
            "Hermetic taming: Rego + the creature's Form Lab Total (+ Animal "
            "Handling + Animal Ken) - its Might each season, until the points "
            "reach its Might; a Lab Text of it.",
            lab_seasons.TAMING_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            experiment.STABILIZE,
            "Stabilize a Discovery",
            "Repeating the experiment that made a Discovery: unless the chart "
            "roll is harmful, its magnitude goes to the research goal; Warping "
            "= magnitude - a simple die.",
            experiment.RESEARCH_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            laboratory_seasons.BUILD,
            "Set up the laboratory",
            "Setting up a laboratory: two seasons (Magic Theory 3); after the "
            "first it works with the Basic Flaw, which the second removes.",
            laboratory_seasons.SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            laboratory_seasons.REFINE,
            "Refine the laboratory",
            "+1 Refinement (Magic Theory at least the new Refinement + 3); a "
            "stress die + Int + Magic Theory: 12+ Highly Organized, 15+ finds a "
            "Hidden Defect, a botch adds one.",
            laboratory_seasons.REFINE_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            laboratory_seasons.TAKE_OVER,
            "Take over the laboratory",
            "Rearranging another's laboratory: rolled like refining; Refinement "
            "at most Magic Theory - 3; the Predecessor may linger.",
            laboratory_seasons.TAKE_OVER_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            laboratory_seasons.MOVE,
            "Move the laboratory",
            "By mundane means: a season packing and two reassembling (the "
            "journey breaks two years' maintenance). By spell: one season, "
            "Perception + Finesse against 9 + 3 x Refinement.",
            laboratory_seasons.MOVE_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            familiar_seasons.BIND,
            "Bind or strengthen a familiar",
            "Binding the familiar: Lab Total at least 25 + Might + 5 x Size, "
            "one season; it buys the cords; Lab Total / 5 pawns of vis.",
            familiar_seasons.BIND_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            familiar_seasons.EMPOWER,
            "Empower the familiar's bond",
            "Instilling a bond power like an enchantment: Lab Total above its "
            "level, Lab Total - level points a season; its vis in the first.",
            familiar_seasons.EMPOWER_SOURCE,
            who=("magus",),
            lab=True,
        ),
        Activity(
            "aging",
            "Aging",
            "The yearly aging roll, made in Winter (a Diary entry, not a plan).",
            aging.SOURCE,
            who=(*PLANNED_TYPES, "grog"),
            gives_xp=False,
            hidden=True,
        ),
        Activity(
            lab_seasons.LONGEVITY_SUBJECT,
            "Subject of a Longevity Ritual",
            "Spending the season with the magus making your Longevity Ritual.",
            lab_seasons.LONGEVITY_SOURCE,
            gives_xp=False,
            hidden=True,
        ),
        Activity(
            book_seasons.WRITE_SUMMA,
            "Write a summa",
            "Writing a summa: Communication + language points a season until "
            "its Level (5 x Level for an Ability); Quality Communication + 6.",
            book_seasons.SOURCE,
        ),
        Activity(
            book_seasons.WRITE_TRACTATUS,
            "Write a tractatus",
            "Writing a tractatus: one season, Quality Communication + 6.",
            book_seasons.SOURCE,
        ),
        Activity(
            book_seasons.COPY_BOOK,
            "Copy a book",
            "Copying: carefully a tractatus, or 6 + Scribe summa points, a "
            "season; quickly three times as much at 1 Quality lower.",
            book_seasons.COPY_SOURCE,
        ),
        Activity(
            book_seasons.TRANSLATE_BOOK,
            "Translate a book",
            "Translating: a tractatus in a season, a summa at Communication + "
            "the source language points a season; 2 Quality lower (1 on an Art).",
            book_seasons.TRANSLATE_SOURCE,
        ),
        Activity(
            book_seasons.REWRITE_TEXTS,
            "Rewrite Lab Texts for general use",
            "Rewriting your own raw Lab Texts so others can use them: Latin x "
            "20 levels a season.",
            book_seasons.LAB_TEXT_SOURCE,
            who=("magus",),
        ),
        Activity(
            book_seasons.COPY_TEXTS,
            "Copy Lab Texts",
            "Copying a readable Lab Text: Profession: Scribe x 60 levels a season.",
            book_seasons.LAB_TEXT_SOURCE,
        ),
        Activity(
            book_seasons.TEACH_ABBREVIATIONS,
            "Teach Lab Text abbreviations",
            "A season writing with a student: he can then read your texts up "
            "to Latin x 20 levels.",
            book_seasons.DECODE_SOURCE,
            who=("magus",),
        ),
        Activity(
            apprentice_seasons.SEARCH,
            "Search for an apprentice",
            "A season searching: stress die + Perception against 9 finds a "
            "Gifted child.",
            apprentice_seasons.SEARCH_SOURCE,
            who=("magus",),
        ),
        Activity(
            apprentice_seasons.OPEN_ARTS,
            "Open an apprentice's Arts",
            "A season: the apprentice gains a score of 0 in all fifteen Arts, "
            "and a Deficiency in each Art where yours is below 5.",
            apprentice_seasons.SOURCE,
            who=("magus",),
        ),
        Activity(
            apprentice_seasons.TEACH_VIRTUE,
            "Teach a Hermetic Virtue",
            "A season with one Gifted student: Communication + Teaching + 9 "
            "against 15 (Minor) or 21 (Major), + 3 per Minor and 9 per Major "
            "Hermetic Virtue the student has.",
            apprentice_seasons.VIRTUE_SOURCE,
            who=("magus",),
        ),
        Activity(
            experiment.INTEGRATE,
            "Seek an insight",
            "A season studying a source (a text, a relic, a teacher, a site): "
            "stress die + Intelligence + Magic Theory against 18.",
            experiment.RESEARCH_SOURCE,
            who=("magus",),
        ),
        Activity(
            laboratory_seasons.ASSIST,
            "Assist in a laboratory",
            "Helping a magus with his lab work: + Intelligence + Magic Theory "
            "to his Lab Total; Exposure in Magic Theory.",
            laboratory_seasons.ASSIST_SOURCE,
        ),
        Activity(
            ADVENTURE,
            "Adventure",
            "Adventure experience: the storyguide's Source Quality (5-10), "
            "split among the Abilities and Arts used, at most 5 to each.",
            ADVENTURE_SOURCE,
        ),
        Activity(
            OTHER,
            "Other",
            "Anything else the season is spent on, logged in the Diary with "
            "your notes. No experience is worked out for it.",
            ASSIGNING_SOURCE,
            gives_xp=False,
        ),
    )
}


# The supplement activities (STORY-913, 918-923), before Other in the menu.
_OTHER_ACTIVITY = ACTIVITIES.pop(OTHER)
ACTIVITIES.update(
    {
        a.key: Activity(
            a.key,
            a.label,
            a.summary,
            a.source,
            who=a.who,
            gives_xp=not a.no_xp,
        )
        for a in supplement_seasons.ACTIVITIES
    }
)
ACTIVITIES[OTHER] = _OTHER_ACTIVITY


def is_planned(character: Character) -> bool:
    """Whether `character` is planned season by season (not a grog)."""
    return character.type in PLANNED_TYPES


def activities_for(character: Character, *, lab: bool = False) -> list[Activity]:
    """The activities `character` may plan, in menu order: lab work (on the
    laboratory's Planning tab) or everything else (on the character sheet)."""
    return [
        a
        for a in ACTIVITIES.values()
        if character.type in a.who and a.lab == lab and not a.hidden
    ]


# -- subjects: what a season's experience goes into ---------------------------


def _split(subject: str) -> tuple[str, str]:
    kind, _, name = subject.partition(":")
    return kind, name


def ability_subject(name: str) -> str:
    return f"ability:{name}"


def art_subject(art: str) -> str:
    return f"art:{ART_BY_NAME.get(art.lower(), art)}"


def mastery_subject(spell_id: str) -> str:
    return f"mastery:{spell_id}"


def subjects(
    character: Character, spell_names: dict[str, str]
) -> list[tuple[str, str]]:
    """(label, subject) for everything `character` could gain experience in:
    their Abilities, then (magi) the Arts, then (magi) the Mastery of each
    known spell. `spell_names` maps spell ids to names."""
    options = [
        (ability.name, ability_subject(ability.name)) for ability in character.abilities
    ]
    if character.type == "magus":
        options += [(art, art_subject(art)) for art in ARTS]
        options += [
            (
                f"Mastery: {spell_names.get(known.spell_id, known.spell_id)}",
                mastery_subject(known.spell_id),
            )
            for known in character.spells_known
        ]
    return options


def subject_label(subject: str, spell_names: dict[str, str]) -> str:
    kind, name = _split(subject)
    if kind == "mastery":
        return f"Mastery: {spell_names.get(name, name)}"
    return name


def has_subject(character: Character, subject: str) -> bool:
    """Whether `character` has `subject` to gain experience in."""
    kind, name = _split(subject)
    if kind == "ability":
        return any(a.name == name for a in character.abilities)
    if kind == "art":
        return character.type == "magus" and name.lower() in ART_BY_NAME
    if kind == "mastery":
        return any(k.spell_id == name for k in character.spells_known)
    return False


def subject_xp(character: Character, subject: str) -> int:
    """The total xp `character` has in `subject` (0 if none yet)."""
    kind, name = _split(subject)
    if kind == "ability":
        ability = next((a for a in character.abilities if a.name == name), None)
        return ability.xp if ability else 0
    if kind == "art":
        score = character.arts.get(name.lower())
        return score.xp if score else 0
    if kind == "mastery":
        known = next((k for k in character.spells_known if k.spell_id == name), None)
        return known.mastery_xp if known else 0
    return 0


def subject_factor(subject: str) -> int:
    """xp per score step: Arts 1, Abilities and Mastery 5."""
    return xp.ART_FACTOR if _split(subject)[0] == "art" else xp.ABILITY_FACTOR


# -- checking and working out a plan -----------------------------------------


def source_quality(plan: SeasonPlan) -> int | None:
    """The plan's Source Quality where it doesn't depend on anyone else:
    typed, or the rule's default."""
    if plan.source_quality is not None:
        return plan.source_quality
    if plan.activity in (EXPOSURE, TEACH):
        return EXPOSURE_QUALITY
    if plan.activity == PRACTICE:
        mastery = any(_split(a.subject)[0] == "mastery" for a in plan.allocations)
        return MASTERY_PRACTICE_QUALITY if mastery else PRACTICE_QUALITY
    return None


def allocations(plan: SeasonPlan) -> list[XpAllocation]:
    """The plan's subjects with the Source Quality each gets where that's
    known from the plan alone: Exposure's 2 points go to one subject, or 1
    each to two; Practice's and Teaching's to their one subject; Adventure's
    are as typed. Study from a teacher, a master or vis names one subject
    (its Source Quality is worked out in outcome())."""
    chosen = [a for a in plan.allocations if a.subject]
    if plan.activity == EXPOSURE:
        each = EXPOSURE_QUALITY // max(1, len(chosen[:2]))
        return [XpAllocation(a.subject, each) for a in chosen[:2]]
    if plan.activity in (PRACTICE, TEACH):
        quality = source_quality(plan) or 0
        return [XpAllocation(a.subject, quality) for a in chosen[:1]]
    if plan.activity == ADVENTURE:
        return chosen
    if plan.activity in (TAUGHT, TRAINED, VIS_STUDY, *supplement_seasons.BY_KEY):
        return [XpAllocation(a.subject, 0) for a in chosen[:1]]
    return []


def book_subject(book: Book) -> str | None:
    """What a summa or tractatus teaches, as a subject ("art:Ignem",
    "ability:Latin"), or None for another kind of book."""
    if book.type not in ("Art Summa", "Ability Summa", "Tractatus"):
        return None
    is_art = book.type == "Art Summa" or (
        book.type == "Tractatus" and book.subject_kind == "Art"
    )
    if is_art:
        return art_subject(book.art) if book.art else None
    return ability_subject(book.ability) if book.ability else None


def score(character: Character, subject: str) -> int:
    """`character`'s score in `subject` (0 without it)."""
    return xp.score_from_xp(subject_xp(character, subject), subject_factor(subject))


def plans_this_season(saga: Saga, plan: SeasonPlan) -> list[SeasonPlan]:
    """Every plan for the same season as `plan`."""
    return [
        p for p in saga.season_plans if (p.season, p.year) == (plan.season, plan.year)
    ]


def students_of(saga: Saga, plan: SeasonPlan) -> int:
    """How many are being taught this subject by this teacher this season."""
    subject = next((a.subject for a in plan.allocations if a.subject), "")
    return sum(
        1
        for p in plans_this_season(saga, plan)
        if p.activity == TAUGHT
        and p.teacher_id == plan.teacher_id
        and any(a.subject == subject for a in p.allocations)
    )


def vis_pool(saga: Saga, character: Character, plan: SeasonPlan) -> dict[str, int]:
    """The raw vis a vis study plan draws on: the magus's own, or their
    laboratory's."""
    if plan.vis_from == "laboratory":
        lab = saga.laboratory(character.assigned_lab_id)
        return lab.raw_vis if lab is not None else {}
    return character.raw_vis


def _study_problems(
    saga: Saga, character: Character, plan: SeasonPlan, chosen: list[XpAllocation]
) -> list[str]:
    """The problems of the study activities (STORY-902)."""
    found: list[str] = []
    if plan.activity == READ:
        book = next((b for b in saga.books if b.id == plan.book_id), None)
        if book is None:
            return ["Choose the book to study."]
        if not books.can_read(saga, character, book):
            return [
                f"{character.name} can't get at {book.name}: it isn't in their "
                "covenant's library or their own keeping."
            ]
        subject = book_subject(book)
        if subject is None or book.quality is None:
            return [f"{book.name} isn't a summa or tractatus with a Quality."]
        if _split(subject)[0] == "art" and character.type != "magus":
            found.append("Only the Gifted study the Arts.")
        if book.type == "Tractatus" and book.id in character.tractatus_read:
            found.append(
                f"{character.name} has already studied {book.name}: a tractatus "
                "teaches each reader once (DE Ch. 10, Studying Tractatus)."
            )
        if (
            book.type != "Tractatus"
            and book.level is not None
            and score(character, subject) >= book.level
        ):
            found.append(
                f"{book.name} (Level {book.level}) has nothing more to teach "
                f"{character.name}."
            )
        return found
    if not chosen:
        return ["Choose what the experience goes into."]
    subject = chosen[0].subject
    kind = _split(subject)[0]
    if plan.activity == TEACH and kind != "ability":
        found.append("A teacher gains Exposure in Teaching or the language used.")
    if plan.activity in (TAUGHT, TRAINED):
        teacher = saga.character(plan.teacher_id)
        role = "teacher" if plan.activity == TAUGHT else "master"
        if teacher is None:
            return [f"Choose the {role}."]
        if teacher.id == character.id:
            return [f"Nobody can be their own {role}."]
        theirs, mine = score(teacher, subject), score(character, subject)
        if plan.activity == TRAINED:
            if kind != "ability":
                found.append("Only Abilities can be trained (DE Ch. 10, Training).")
            elif theirs < 2 or theirs <= mine:
                found.append(
                    f"A master needs a score of 2 or more, higher than the "
                    f"trainee's: {teacher.name} has {theirs}, {character.name} {mine}."
                )
        else:
            teacher_plan = next(
                (
                    p
                    for p in plans_this_season(saga, plan)
                    if p.character_id == teacher.id
                ),
                None,
            )
            if teacher_plan is None or teacher_plan.activity != TEACH:
                found.append(
                    f"{teacher.name} hasn't planned to Teach this season "
                    "(teaching takes the teacher's season too)."
                )
            needed = 5 if kind == "art" else 2
            if theirs < needed or theirs <= mine:
                found.append(
                    f"A teacher needs a score of {needed} or more, higher than "
                    f"the student's: {teacher.name} has {theirs}, "
                    f"{character.name} {mine}."
                )
            students = students_of(saga, plan)
            if kind == "art" and students > 1:
                found.append("The Arts are taught one student at a time.")
            elif students > study.max_students(teacher):
                found.append(
                    f"{teacher.name} can teach {study.max_students(teacher)} "
                    f"student(s) at once; {students} are planned."
                )
    if plan.activity == VIS_STUDY:
        if kind != "art":
            found.append("Vis is studied for an Art.")
        else:
            art = _split(subject)[1]
            pawns = study.vis_pawns(score(character, subject))
            held = vis_pool(saga, character, plan).get(art.lower(), 0)
            if held < pawns:
                whose = (
                    "the laboratory's"
                    if plan.vis_from == "laboratory"
                    else f"{character.name}'s"
                )
                found.append(
                    f"Studying {art} takes {pawns} pawn(s) of {art} vis; "
                    f"{whose} raw vis has {held}."
                )
        if plan.die is not None and plan.die < 0:
            found.append("A die roll can't be negative.")
    return found


def problems(
    character: Character, plan: SeasonPlan, saga: Saga | None = None
) -> list[str]:
    """Why `plan` can't be carried out as it stands (empty when it can).
    The study activities need the saga (books, teachers, vis)."""
    activity = ACTIVITIES.get(plan.activity)
    if not is_planned(character):
        return [
            "Grogs aren't planned season by season: they're updated once a "
            "year (Grogs, Chapter 5)."
        ]
    if activity is None:
        return [f"Unknown activity {plan.activity!r}."]
    until = character.aging.twilight_until
    if until:
        season, _, year = until.partition(" ")
        if (plan.year, SEASONS.index(plan.season)) <= (
            int(year),
            SEASONS.index(season),
        ):
            return [f"{character.name} is lost in Wizard's Twilight until {until}."]
    if character.aging.recovering == f"{plan.season} {plan.year}":
        return [
            f"{character.name} spends {plan.season} {plan.year} recovering from "
            "an Aging Crisis."
        ]
    if character.type not in activity.who:
        return [f"A {character.type} can't do {activity.label}."]
    wounded = _wound_problem(character, plan, activity)
    if wounded:
        return [wounded]
    if not activity.gives_xp:
        if saga is not None and plan.activity in supplement_seasons.BY_KEY:
            return supplement_work.problems(saga, character, plan)
        return []
    if activity.lab:
        if saga is None:
            return ["Lab work needs the saga to be worked out."]
        found_lab, _ = lab_seasons.work(saga, character, plan)
        if plan.days_away < 0:
            found_lab.append("Days away can't be negative.")
        return found_lab
    if plan.activity in book_seasons.SHEET_ACTIVITIES:
        if saga is None:
            return ["This activity needs the saga to be worked out."]
        found_books, _ = book_seasons.work(saga, character, plan)
        return found_books
    if plan.activity == laboratory_seasons.ASSIST:
        if saga is None:
            return ["This activity needs the saga to be worked out."]
        return laboratory_seasons.assist_problems(saga, character, plan)
    if plan.activity == experiment.INTEGRATE:
        return [] if plan.research.strip() else ["Name the research goal."]
    simple = supplement_seasons.BY_KEY.get(plan.activity)
    if simple is not None:
        assert saga is not None
        found_work = supplement_work.problems(saga, character, plan)
        if found_work:
            return found_work
        if not [a for a in plan.allocations if a.subject]:
            return ["Choose what the experience goes into."]
        if simple.quality is None and plan.source_quality is None:
            return [f"Type the Source Quality: {simple.hint}."]
        if plan.source_quality is not None and plan.source_quality < 0:
            return ["The Source Quality can't be negative."]
        return []
    if plan.activity in apprentice_seasons.ACTIVITIES:
        if saga is None:
            return ["This activity needs the saga to be worked out."]
        found_apprentice, _ = apprentice_seasons.work(saga, character, plan)
        return found_apprentice
    found: list[str] = []
    chosen = [a for a in plan.allocations if a.subject]
    if not 0 <= plan.months_lost <= 3:
        found.append("Months lost must be 0 to 3.")
    if plan.activity in STUDY_ACTIVITIES:
        if saga is None:
            return ["This activity needs the saga to be worked out."]
        found += _study_problems(saga, character, plan, chosen)
        if plan.activity != READ:
            for allocation in chosen[:1]:
                if not has_subject(character, allocation.subject):
                    kind, name = _split(allocation.subject)
                    if kind != "ability" or plan.activity == TEACH:
                        found.append(f"{character.name} doesn't have {name}.")
        return found
    if not chosen:
        found.append("Choose what the experience goes into.")
    for allocation in chosen:
        if not has_subject(character, allocation.subject):
            found.append(
                f"{character.name} doesn't have {_split(allocation.subject)[1]}."
            )
    if len({a.subject for a in chosen}) < len(chosen):
        found.append("The same subject is named twice.")
    if plan.activity == EXPOSURE and len(chosen) > 2:
        found.append("Exposure goes into one subject, or is split between two.")
    if plan.activity == PRACTICE:
        if len(chosen) > 1:
            found.append("Practice improves one subject.")
        if any(_split(a.subject)[0] == "art" for a in chosen):
            found.append(
                "Arts can't be practised: study them from vis or books "
                "(DE Ch. 10, Practice)."
            )
        quality = source_quality(plan)
        if quality is not None and quality < 1:
            found.append("Source Quality must be at least 1.")
    if plan.activity == ADVENTURE:
        quality = plan.source_quality
        if quality is None or not ADVENTURE_MIN <= quality <= ADVENTURE_MAX:
            found.append(
                f"An Adventure's Source Quality is {ADVENTURE_MIN} to "
                f"{ADVENTURE_MAX} (the storyguide's choice)."
            )
        elif sum(a.points for a in chosen) != quality:
            found.append(
                f"Split all {quality} points of Source Quality: "
                f"{sum(a.points for a in chosen)} are split."
            )
        if any(not 1 <= a.points <= ADVENTURE_PER_SUBJECT for a in chosen):
            found.append(
                f"Each subject gets 1 to {ADVENTURE_PER_SUBJECT} points of an "
                "Adventure's Source Quality."
            )
    return found


@dataclass
class XpGain:
    """Experience a season gives one subject: the working and the totals
    before and after."""

    subject: str
    result: StudyResult
    before: int  # total xp before the season

    @property
    def after(self) -> int:
        return self.before + self.result.xp


@dataclass
class Outcome:
    """What a planned season gives, worked out from the saga before the
    season: nothing is applied here."""

    character_id: str
    plan: SeasonPlan
    activity: Activity | None
    gains: list[XpGain] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    #: How the Source Quality is (or was) worked out, rolls, botches.
    notes: list[str] = field(default_factory=list)
    #: Vis study: (pool "character"/"laboratory", art, pawns) to spend.
    vis_spent: tuple[str, str, int] | None = None
    #: Reading a tractatus: its id, to mark it read.
    tractatus: str | None = None
    #: Vis study still to roll (a preview made without a die).
    pending_roll: bool = False
    #: Lab work: what the season in the laboratory does.
    lab_work: lab_seasons.LabWork | None = None
    #: Book work (STORY-910, 914): what the season does to books.
    book_work: book_seasons.BookWork | None = None
    #: Apprentice work (STORY-917).
    apprentice_work: apprentice_seasons.ApprenticeWork | None = None
    #: Seeking an insight (STORY-916): whether one was gained.
    insight: bool = False
    #: Faith Points gained (Good Works).
    faith: int = 0
    #: What a supplement season does besides experience (decision 38).
    supplement: supplement_work.SupplementWork | None = None

    @property
    def ok(self) -> bool:
        return not self.problems


def _gain(
    character: Character,
    subject: str,
    quality: int,
    activity: str,
    months: int,
    gain_limit: int | None = None,
) -> XpGain:
    kind, name = _split(subject)
    result = season_of_study(
        character,
        name,
        quality,
        activity=activity,
        is_art=kind == "art",
        gain_limit=gain_limit,
        months_lost=months,
    )
    return XpGain(subject, result, subject_xp(character, subject))


#: The study_total activity (rules.study's Virtue lookups) of each activity.
_STUDY_KIND: dict[str, str] = {
    EXPOSURE: "exposure",
    PRACTICE: "practice",
    ADVENTURE: "adventure",
    READ: "reading",
    TAUGHT: "teaching",
    TEACH: "exposure",
    TRAINED: "training",
    VIS_STUDY: "vis_study",
}


def _experiment(
    result: Outcome, character: Character, saga: Saga, rng: random.Random | None
) -> None:
    """Experimenting (STORY-916): the simple die joins the Lab Total, then
    the Extraordinary Results chart; stabilizing rolls the chart too."""
    plan = result.plan
    stabilizing = plan.activity == experiment.STABILIZE
    if rng is None and (stabilizing or plan.experiment_die is None):
        result.pending_roll = True
        return
    roll_rng = rng or random.Random()
    if not stabilizing:
        die = (
            plan.experiment_die
            if plan.experiment_die is not None
            else dice.simple_die(roll_rng)
        )
        plan = replace(plan, experiment_die=die)
        result.plan = plan
        _, result.lab_work = lab_seasons.work(saga, character, plan)
    work = result.lab_work
    if work is None:
        return
    aura, _ = _home_aura(saga, character)
    art = work.spell.technique if work.spell is not None else "Vim"
    goal = experiment.find_goal(character, plan.research) if plan.research else None
    # With an insight waiting, the experiment invents it (integration);
    # otherwise it seeks a Discovery, keeping the move made before.
    integrating = goal is not None and goal.insights > 0 and not stabilizing
    seeks = lab_seasons.seeking(plan) and not integrating and not stabilizing
    shift = (
        goal.discovery_shift
        if goal is not None and goal.discovery_shift and (seeks or stabilizing)
        else None
    )
    chart = experiment.chart(
        roll_rng,
        plan.risk,
        aura,
        art,
        saga,
        character=character,
        seeking=seeks or (stabilizing and shift is not None),
        shift=shift,
    )
    if chart.no_benefit and not stabilizing:
        _, plain = lab_seasons.work(saga, character, replace(plan, experimenting=False))
        if chart.discovery_shift is not None:
            # Asked before it counts: kept aside in case the move isn't taken.
            chart.fallback = plain
        elif plain is None:
            chart.wasted = True
        else:
            result.lab_work = work = plain
    assert work is not None
    work.experiment = chart
    if stabilizing:
        work.research_warping = max(
            0, work.research_magnitude - dice.simple_die(roll_rng)
        )
    result.notes += ["Extraordinary Results: " + " ".join(chart.results)]


def outcome(
    character: Character,
    plan: SeasonPlan,
    saga: Saga | None = None,
    rng: random.Random | None = None,
) -> Outcome:
    """What `plan` gives `character`, from their current figures. Vis study
    rolls a stress die (or uses the one typed on the plan); without `rng`
    and a typed die it is a preview, `pending_roll`."""
    activity = ACTIVITIES.get(plan.activity)
    found = problems(character, plan, saga)
    result = Outcome(character.id, plan, activity, problems=found)
    if (
        not found
        and activity is not None
        and not activity.gives_xp
        and saga is not None
        and plan.activity in supplement_seasons.BY_KEY
    ):
        result.supplement = supplement_work.work(saga, character, plan, rng)
        result.notes += result.supplement.notes
    if found or activity is None or not activity.gives_xp:
        return result
    result = _outcome(character, plan, saga, rng, result, activity)
    if not result.problems and derived.wound_penalty(character.wounds) <= -3:
        # Study at -3 to -5 is halved (DE Ch. 11, Activities While Injured).
        for gain in result.gains:
            gain.result.xp //= 2
        if result.gains:
            result.notes.append("Wounded (-3 to -5): the season's xp is halved.")
    return result


#: Craft and business seasons that a -3 Wound Penalty rules out (lab work too).
_CRAFT = (
    "working_season",
    "workshop_production",
    "make_excellent_item",
    "repair_item",
    "improve_workshop",
    "produce_remedies",
    "apothecary",
    "create_art",
)


def _wound_problem(character: Character, plan: SeasonPlan, activity: Activity) -> str:
    """What the character's wounds rule out (DE Ch. 11, Activities While
    Injured): -3 to -5 no lab or craft work; -6 or worse, or Incapacitated,
    nothing productive."""
    penalty = derived.wound_penalty(character.wounds)
    if plan.activity in (OTHER, "convalesce", "travel") or not activity.gives_xp:
        return ""
    if character.wounds.incapacitated or penalty <= -6:
        return (
            f"{character.name}'s wounds ({penalty}) allow nothing productive: "
            "plan Convalesce."
        )
    if penalty <= -3 and (activity.lab or plan.activity in _CRAFT):
        return f"{character.name}'s wounds ({penalty}) allow no lab or craft work."
    return ""


def _outcome(
    character: Character,
    plan: SeasonPlan,
    saga: Saga | None,
    rng: random.Random | None,
    result: Outcome,
    activity: Activity,
) -> Outcome:
    """The season's gains (outcome() without the wound rule)."""
    if activity.lab:
        assert saga is not None
        _, result.lab_work = lab_seasons.work(saga, character, plan)
        if plan.activity == enchant_seasons.INVESTIGATE and result.lab_work is not None:
            if plan.die is None and rng is None:
                result.pending_roll = True
            else:
                result.notes += enchant_seasons.investigate(
                    result.lab_work, plan, rng or random.Random(), saga
                )
        if result.lab_work is not None and (
            plan.experimenting or plan.activity == experiment.STABILIZE
        ):
            _experiment(result, character, saga, rng)
        rolled = plan.activity in laboratory_seasons.ROLLED and (
            plan.activity != laboratory_seasons.MOVE or plan.by_spell
        )
        if rolled and result.lab_work is not None:
            result.notes += result.lab_work.notes
            if plan.die is None and rng is None:
                result.pending_roll = True
            else:
                result.notes += laboratory_seasons.roll(
                    result.lab_work, character, plan, rng or random.Random(), saga
                )
        # Lab work gives Exposure in Magic Theory (DE Ch. 10, Exposure).
        result.gains.append(
            _gain(character, ability_subject("Magic Theory"), 2, "exposure", 0)
        )
        return result
    if plan.activity in book_seasons.SHEET_ACTIVITIES:
        assert saga is not None
        _, result.book_work = book_seasons.work(saga, character, plan)
        # Writing and copying give Exposure (DE Ch. 10, Exposure).
        result.gains.append(
            _gain(
                character,
                ability_subject(book_seasons.exposure_ability(character, plan)),
                2,
                "exposure",
                0,
            )
        )
        return result
    if plan.activity in apprentice_seasons.ACTIVITIES:
        assert saga is not None
        _, work = apprentice_seasons.work(saga, character, plan)
        result.apprentice_work = work
        if work is not None:
            result.notes += work.notes
            if plan.activity == apprentice_seasons.TEACH_VIRTUE:
                result.notes.append(
                    f"Source Quality {work.quality} against {work.target}: "
                    + ("taught." if work.succeeds else "not learned.")
                )
        if plan.activity == apprentice_seasons.SEARCH:
            if plan.die is None and rng is None:
                result.pending_roll = True
            else:
                die = (
                    plan.die
                    if plan.die is not None
                    else dice.stress_die(rng or random.Random(), 1, saga=saga).value
                )
                total = character.characteristics.perception + die
                result.notes.append(
                    f"Perception + die {die} = {total} against "
                    f"{apprentice_seasons.SEARCH_EASE}: "
                    + (
                        "a Gifted child is found (add them as a character)."
                        if total >= apprentice_seasons.SEARCH_EASE
                        else "no apprentice found this season."
                    )
                )
        else:
            # Teaching gives Exposure in Teaching (DE Ch. 10, Exposure).
            result.gains.append(
                _gain(character, ability_subject("Teaching"), 2, "exposure", 0)
            )
        return result
    if plan.activity == experiment.INTEGRATE:
        if plan.die is None and rng is None:
            result.pending_roll = True
        else:
            theory = laboratory_seasons.magic_theory(character)
            result.insight, note = experiment.insight_roll(
                character, plan, rng or random.Random(), theory, saga
            )
            result.notes.append(note)
        return result
    simple = supplement_seasons.BY_KEY.get(plan.activity)
    if simple is not None:
        quality = (
            plan.source_quality if plan.source_quality is not None else simple.quality
        )
        subject = allocations(plan)[0].subject
        kind = "exposure" if quality == EXPOSURE_QUALITY else "practice"
        result.gains.append(_gain(character, subject, quality or 0, kind, 0))
        result.faith = simple.faith
        assert saga is not None
        result.supplement = supplement_work.work(saga, character, plan, rng)
        result.notes += result.supplement.notes
        return result
    if plan.activity == laboratory_seasons.ASSIST:
        # Lab work gives Exposure in Magic Theory (DE Ch. 10, Exposure).
        result.gains.append(
            _gain(character, ability_subject("Magic Theory"), 2, "exposure", 0)
        )
        return result
    months = plan.months_lost if activity.distractable else 0
    kind = _STUDY_KIND[plan.activity]
    if plan.activity == READ:
        assert saga is not None
        book = next(b for b in saga.books if b.id == plan.book_id)
        subject = book_subject(book)
        assert subject is not None and book.quality is not None
        limit = book.level if book.type != "Tractatus" else None
        result.gains.append(
            _gain(character, subject, book.quality, kind, months, gain_limit=limit)
        )
        if book.type == "Tractatus":
            result.tractatus = book.id
        return result
    if plan.activity in (TAUGHT, TRAINED):
        assert saga is not None
        teacher = saga.character(plan.teacher_id)
        assert teacher is not None
        subject = allocations(plan)[0].subject
        if plan.activity == TAUGHT:
            quality = study.teaching_quality(teacher, students_of(saga, plan))
        else:
            quality = score(teacher, subject) + 3
        result.gains.append(
            _gain(
                character,
                subject,
                quality,
                kind,
                months,
                gain_limit=score(teacher, subject),
            )
        )
        return result
    if plan.activity == VIS_STUDY:
        assert saga is not None
        subject = allocations(plan)[0].subject
        art = _split(subject)[1]
        pawns = study.vis_pawns(score(character, subject))
        aura, realm = _home_aura(saga, character)
        aura_mod = realms.aura_modifier(realms.HERMETIC, realm, aura)
        botch_dice = pawns + realms.extra_botch_dice(realms.HERMETIC, realm, aura)
        result.vis_spent = (plan.vis_from or "character", art, pawns)
        result.notes.append(
            f"Source Quality: stress die + aura {aura_mod:+d} ({aura} {realm}); "
            f"{pawns} pawn(s) of {art} vis; {botch_dice} botch dice."
        )
        if plan.die is None and rng is None:
            result.pending_roll = True
            return result
        if plan.die is not None and plan.die > 0:
            die_value, botches = plan.die, 0
            result.notes.append(f"Die {plan.die} (as rolled at the table).")
        else:
            roll_rng = rng or random.Random()
            if plan.die == 0:
                faces = [roll_rng.randrange(10) for _ in range(botch_dice)]
                die_value, botches = 0, faces.count(0)
            else:
                die = dice.stress_die(roll_rng, botch_dice, saga=saga)
                die_value, botches = die.value, die.botches
            result.notes.append(f"Die rolled: {die_value}.")
        if botches:
            result.notes.append(
                f"Botch: {botches} zero(s) on the botch dice"
                + (
                    "; a double botch may bring on Wizard's Twilight (DE Ch. 10, Vis)."
                    if botches >= 2
                    else "."
                )
            )
        quality = max(0, die_value + aura_mod)
        result.gains.append(_gain(character, subject, quality, kind, months))
        return result
    for allocation in allocations(plan):
        result.gains.append(
            _gain(character, allocation.subject, allocation.points, kind, months)
        )
    return result


def _home_aura(saga: Saga, character: Character) -> tuple[int, str]:
    from ..casting_text import home_aura

    return home_aura(saga, character)


def outcomes(
    saga: Saga, plans: Sequence[SeasonPlan], rng: random.Random | None = None
) -> list[Outcome]:
    """Every plan's outcome, all worked out before any is applied (a plan
    for a character no longer in the saga is skipped)."""
    worked: list[Outcome] = []
    for plan in plans:
        character = saga.character(plan.character_id)
        if character is not None:
            worked.append(outcome(character, plan, saga, rng))
    return worked
