"""Seasonal activities: which activities a character may plan for
a season, and what a planned season gives.

A plan is what the user typed (models.SeasonPlan); its outcome is always
worked out here from the saga as it stands, never stored. Advancing the
season works out every plan's outcome first and only then applies them
(ars_magica_manager.seasons), so a season's results never change that same
season's figures.

Who plans a season (DE Ch. 10, Assigning Seasons): a magus has four free
seasons a year; a companion (Mythic or not) works two seasons a year,
earning Exposure in their job, and has two free ones. Grogs aren't planned
season by season: they're updated once a year (Grogs, Ch. 5).

Activities built so far, each an Advancement Total (rules.study):

- Work / Exposure: Source Quality 2 in an Ability or Art used that season,
  or 1 each in two.
- Practice: Source Quality 4 in one Ability (languages among native
  speakers 8, Area Lore 5-7, forced practice of a trade 5: typed), or 5 in
  a spell's Mastery. Arts can't be practised.
- Adventure: Source Quality 5-10, split among the Abilities and Arts used,
  at most 5 to each.
- Read a book: a summa's Quality up to its Level, a tractatus's
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
from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass, field, replace

from .. import book_kinds, catalog, sourcebooks, vis
from ..arts import ART_BY_NAME, ARTS
from ..models import (
    SEASONS,
    Book,
    Character,
    Saga,
    SeasonPlan,
    TraditionDef,
    XpAllocation,
    character_age,
)
from . import activity_groups as groups
from . import (
    aging,
    apprentice_seasons,
    book_seasons,
    casting,
    derived,
    dice,
    effects,
    enchant_seasons,
    experiment,
    familiar_seasons,
    lab_seasons,
    lab_stats,
    lab_virtues,
    laboratory_seasons,
    languages,
    library,
    realms,
    scores,
    study,
    study_virtues,
    supplement_seasons,
    supplement_work,
    tamed,
    tradition_seasons,
    xp,
)
from . import (
    creation_access as access,
)
from . import hybrid_magic as hybrid
from . import lab as lab_rules
from .breakdown import Line
from .scores import ability_level
from .study import StudyResult, season_of_study

ASSIGNING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Assigning Seasons, p. "
    "376"
)
EXPOSURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Exposure, p. 376"
)
PRACTICE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Practice, p. 377"
)
ADVENTURE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Adventure, p. 376"
)
BOOKS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Books, pp. 378-379"
)
TEACHING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Teaching, p. 378"
)
TRAINING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Training, p. 377"
)
VIS_SOURCE = "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Vis, p. 378"
DISTRACTION_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long Term Events, Distractions, p. 379"
)

#: The rule behind seasons as a whole (every rules module cites one).
SOURCE = ASSIGNING_SOURCE

#: The character types planned season by season (grogs are updated yearly).
PLANNED_TYPES: tuple[str, ...] = ("magus", "companion", "mythic companion")
#: The types that work two seasons a year (Assigning Seasons).
WORKING_TYPES: tuple[str, ...] = ("companion", "mythic companion")
#: Working seasons a companion owes each year, before Virtues and Flaws
#: (working_seasons).
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
    #: Lab work: planned on the laboratory's Planning tab, not
    #: the character sheet.
    lab: bool = False
    #: Lab work also offered on the character sheet, in a laboratory that
    #: isn't the character's yet (taking one over).
    sheet: bool = False
    #: Planned for the character by someone else's lab work (the subject of
    #: a Longevity Ritual), not picked from the menu.
    hidden: bool = False
    #: The sourcebook it comes from ("" for the core book): offered only
    #: while the saga has that book in play.
    book: str = ""
    #: A tradition's own work: offered only to its members (a catalog
    #: id), or "*" to a member of any tradition.
    tradition: str = ""
    #: What the season is for (activity_groups): the picker's Type.
    group: str = ""


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
            group=groups.WORK,
        ),
        Activity(
            PRACTICE,
            "Practice",
            "Practising one Ability (Source Quality 4; languages among native "
            "speakers 8, Area Lore 5-7, forced practice of a trade 5), or a "
            "spell's Mastery (5). Arts can't be practised.",
            PRACTICE_SOURCE,
            distractable=True,
            group=groups.STUDY,
        ),
        Activity(
            READ,
            "Read a book",
            "A season with a summa (its Quality, up to its Level) or a "
            "tractatus (its Quality, once), from the covenant's library or "
            "the reader's own books.",
            BOOKS_SOURCE,
            distractable=True,
            group=groups.STUDY,
        ),
        Activity(
            TAUGHT,
            "Be taught",
            "Taught by another character, who plans Teach: Communication + "
            "Teaching + 3, +6 for one student, +3 for two; up to their score.",
            TEACHING_SOURCE,
            distractable=True,
            group=groups.STUDY,
        ),
        Activity(
            TEACH,
            "Teach",
            "Teaching someone who plans Be taught: Exposure (2 xp) in Teaching "
            "or the language used.",
            TEACHING_SOURCE,
            group=groups.TEACHING,
        ),
        Activity(
            TRAINED,
            "Be trained",
            "Trained in an Ability by a master: their score + 3, up to their "
            "score. The master can earn a living meanwhile.",
            TRAINING_SOURCE,
            distractable=True,
            group=groups.STUDY,
        ),
        Activity(
            VIS_STUDY,
            "Study from vis",
            "Studying an Art from its raw vis: a stress die + the aura, using "
            "ceil(Art / 5) pawns, with as many botch dice.",
            VIS_SOURCE,
            who=("magus",),
            distractable=True,
            group=groups.STUDY,
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
            group=groups.INVENTING,
        ),
        Activity(
            lab_seasons.LAB_TEXT,
            "Invent from a Lab Text",
            "Working from a Lab Text: one season, if the Lab Total is at least "
            "the spell's level.",
            lab_seasons.LAB_TEXT_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.INVENTING,
        ),
        Activity(
            lab_seasons.TAUGHT_SPELLS,
            "Learn spells from a teacher",
            "A season learning spells from a magus who knows them and spends "
            "the season teaching: at most his highest Lab Total in levels, his "
            "Lab Total in each Technique and Form, and no spell above your own "
            "Lab Total for it.",
            lab_seasons.spell_teaching.SOURCE,
            who=("magus",),
            lab=True,
            group=groups.INVENTING,
        ),
        Activity(
            lab_seasons.EXTRACT,
            "Extract vis",
            "Extracting vis from the aura: Creo Vim Lab Total / 10 pawns of "
            "Vim, rounded up. Only in a Magic aura.",
            lab_seasons.EXTRACT_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.TEXTS_AND_VIS,
        ),
        Activity(
            lab_seasons.FIX_AC,
            "Fix an Arcane Connection",
            "Making an Arcane Connection permanent: a season in the laboratory "
            "and 1 pawn of Vim vis.",
            lab_seasons.FIX_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.TEXTS_AND_VIS,
        ),
        Activity(
            lab_seasons.LONGEVITY,
            "Longevity Ritual",
            "A Longevity Ritual: Creo Corpus Lab Total / 5 off aging rolls (/ 10 "
            "for a mundane subject); vis = the subject's age / 5.",
            lab_seasons.LONGEVITY_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.INVENTING,
        ),
        Activity(
            enchant_seasons.OPEN,
            "Open an item for enchantment",
            "Preparing an invested device: a season and its capacity in pawns "
            "of Vim vis (a talisman may be opened a few pawns at a time).",
            enchant_seasons.OPEN_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
        ),
        Activity(
            enchant_seasons.INSTIL,
            "Instil an effect",
            "Instilling an effect in an opened device: Lab Total above its "
            "level, Lab Total - level points a season; its vis in the first.",
            enchant_seasons.INSTIL_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
        ),
        Activity(
            enchant_seasons.LESSER_WORK,
            "Make a lesser enchantment",
            "A lesser enchanted device: one season, Lab Total at least twice "
            "the effect's level; level / 10 pawns of vis.",
            enchant_seasons.LESSER_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
        ),
        Activity(
            enchant_seasons.CHARGED_WORK,
            "Make a charged item",
            "A charged item: one season, Lab Total at least the level, no "
            "vis; (Lab Total - level) / 5 charges, at least 1.",
            enchant_seasons.CHARGED_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
        ),
        Activity(
            enchant_seasons.ATTUNE,
            "Attune a talisman",
            "Attuning an invested device you opened as your talisman: one "
            "season, no Lab Total needed; one talisman at a time.",
            enchant_seasons.ATTUNE_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
        ),
        Activity(
            enchant_seasons.INVESTIGATE,
            "Investigate an enchanted item",
            "Intellego Vim Lab Total + a stress die against each hidden power, "
            "weakest first; the first failure ends the season.",
            enchant_seasons.INVESTIGATE_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.ENCHANTING,
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
            group=groups.TEXTS_AND_VIS,
        ),
        Activity(
            lab_seasons.TAMING,
            "Tame a magical beast",
            "Hermetic taming: Rego + the creature's Form Lab Total (+ Animal "
            "Handling + Animal Ken, + 1 for every 5 levels of the best taming "
            "Lab Text of its Form at hand) - its Might each season, until the "
            "points reach its Might; they last only over consecutive seasons "
            "(DE p. 384). Tamed, a creature of the saga gains Loyal +0 to the "
            "magus; a Lab Text of it.",
            lab_seasons.TAMING_SOURCE,
            who=("magus",),
            lab=True,
            book="RoP:M",
            group=groups.FAMILIAR,
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
            group=groups.INVENTING,
        ),
        Activity(
            laboratory_seasons.BUILD,
            "Set up the laboratory",
            "Setting up a laboratory: two seasons (Magic Theory 3); after the "
            "first it works with the Basic Flaw, which the second removes.",
            laboratory_seasons.SOURCE,
            who=("magus",),
            lab=True,
            group=groups.LABORATORY,
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
            group=groups.LABORATORY,
        ),
        Activity(
            laboratory_seasons.TAKE_OVER,
            "Take over the laboratory",
            "Rearranging another's laboratory, which becomes yours: rolled "
            "like refining; Refinement at most Magic Theory - 3; the "
            "Predecessor may linger.",
            laboratory_seasons.TAKE_OVER_SOURCE,
            who=("magus",),
            lab=True,
            sheet=True,
            book="Covenants",
            group=groups.LABORATORY,
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
            book="Covenants",
            group=groups.LABORATORY,
        ),
        Activity(
            familiar_seasons.BIND,
            "Bind or strengthen a familiar",
            "Binding the familiar: Lab Total at least 25 + Might + 5 x Size, "
            "one season; it buys the cords; Lab Total / 5 pawns of vis.",
            familiar_seasons.BIND_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.FAMILIAR,
        ),
        Activity(
            familiar_seasons.EMPOWER,
            "Empower the familiar's bond",
            "Instilling a bond power like an enchantment: Lab Total above its "
            "level, Lab Total - level points a season; its vis in the first.",
            familiar_seasons.EMPOWER_SOURCE,
            who=("magus",),
            lab=True,
            group=groups.FAMILIAR,
        ),
        Activity(
            "aging",
            "Aging",
            "The yearly aging roll, made in Winter (a Diary entry, not a plan).",
            aging.SOURCE,
            who=(*PLANNED_TYPES, "grog"),
            gives_xp=False,
            hidden=True,
            group=groups.REST,
        ),
        Activity(
            lab_seasons.LONGEVITY_SUBJECT,
            "Subject of a Longevity Ritual",
            "Spending the season with the magus making your Longevity Ritual.",
            lab_seasons.LONGEVITY_SOURCE,
            gives_xp=False,
            hidden=True,
            group=groups.REST,
        ),
        Activity(
            book_seasons.WRITE_SUMMA,
            "Write a summa",
            "Writing a summa: Communication + language points a season until "
            "its Level (5 x Level for an Ability); Quality Communication + 6.",
            book_seasons.SOURCE,
            distractable=True,
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.WRITE_TRACTATUS,
            "Write a tractatus",
            "Writing a tractatus: one season, Quality Communication + 6.",
            book_seasons.SOURCE,
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.COPY_BOOK,
            "Copy a book",
            "Copying: carefully a tractatus, or 6 + Scribe summa points, a "
            "season; quickly three times as much at 1 Quality lower.",
            book_seasons.COPY_SOURCE,
            distractable=True,
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.TRANSLATE_BOOK,
            "Translate a book",
            "Translating: a tractatus in a season, a summa at Communication + "
            "the source language points a season; 2 Quality lower (1 on an Art).",
            book_seasons.TRANSLATE_SOURCE,
            book="A&A",
            distractable=True,
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.REWRITE_TEXTS,
            "Rewrite Lab Texts for general use",
            "Rewriting your own raw Lab Texts so others can use them: Latin x "
            "20 levels a season.",
            book_seasons.LAB_TEXT_SOURCE,
            who=("magus",),
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.COPY_TEXTS,
            "Copy Lab Texts",
            "Copying a readable Lab Text or a Casting Tablet: Profession: "
            "Scribe x 60 levels a season.",
            book_seasons.LAB_TEXT_SOURCE,
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.EDIT_FLORILEGIUM,
            "Edit a florilegium",
            "Binding tractatus on one subject, as many as you could write on "
            "it, from a collection twice that size: each read at +1 Quality "
            "(+2 for an authority's, from a peerless collection).",
            book_kinds.SOURCE,
            book="Covenants",
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.WRITE_TABLET,
            "Write Casting Tablets",
            "Tablets of a spell you have mastered, from a season's pool of "
            "Latin x 20 levels: as many as it holds.",
            casting.TABLET_SOURCE,
            who=("magus",),
            group=groups.WRITING,
        ),
        Activity(
            book_seasons.TEACH_ABBREVIATIONS,
            "Teach Lab Text abbreviations",
            "A season writing with a student: he can then read your texts up "
            "to Latin x 20 levels.",
            book_seasons.DECODE_SOURCE,
            who=("magus",),
            group=groups.TEACHING,
        ),
        Activity(
            apprentice_seasons.SEARCH,
            "Search for an apprentice",
            "A season searching: stress die + Perception against 9 finds a "
            "Gifted child.",
            apprentice_seasons.SEARCH_SOURCE,
            who=("magus",),
            group=groups.TEACHING,
        ),
        Activity(
            apprentice_seasons.OPEN_ARTS,
            "Open an apprentice's Arts",
            "A season: the apprentice gains a score of 0 in all fifteen Arts, "
            "and a Deficiency in each Art where yours is below 5.",
            apprentice_seasons.SOURCE,
            who=("magus",),
            group=groups.TEACHING,
        ),
        Activity(
            apprentice_seasons.TEACH_VIRTUE,
            "Teach a Hermetic Virtue",
            "A season with one Gifted student: Communication + Teaching + 9 "
            "against 15 (Minor) or 21 (Major), + 3 per Minor and 9 per Major "
            "Hermetic Virtue the student has.",
            apprentice_seasons.VIRTUE_SOURCE,
            who=("magus",),
            group=groups.TEACHING,
        ),
        Activity(
            experiment.INTEGRATE,
            "Seek an insight",
            "A season studying a source (a text, a relic, a teacher, a site): "
            "stress die + Intelligence + Magic Theory (+3 Inventive Genius) "
            "against 18.",
            experiment.RESEARCH_SOURCE,
            who=("magus",),
            group=groups.STUDY,
        ),
        Activity(
            laboratory_seasons.NEW,
            "Set up a new laboratory",
            "A laboratory where you have none: it is made in your covenant and "
            "works, with the Basic Flaw, after this season (Magic Theory 3); a "
            "second season in it, as its lab work, removes the Flaw. Exposure "
            "in Magic Theory.",
            laboratory_seasons.SOURCE,
            who=("magus",),
            group=groups.ORDER,
        ),
        Activity(
            laboratory_seasons.ASSIST,
            "Assist in a laboratory",
            "Helping a magus with his lab work: + Intelligence + Magic Theory "
            "to his Lab Total; Exposure in Magic Theory.",
            laboratory_seasons.ASSIST_SOURCE,
            group=groups.ORDER,
        ),
        Activity(
            ADVENTURE,
            "Adventure",
            "Adventure experience: the storyguide's Source Quality (5-10), "
            "split among the Abilities and Arts used, at most 5 to each.",
            ADVENTURE_SOURCE,
            group=groups.ADVENTURE,
        ),
        Activity(
            OTHER,
            "Other",
            "Anything else the season is spent on, logged in the Diary with "
            "your notes. No experience is worked out for it.",
            ASSIGNING_SOURCE,
            gives_xp=False,
            group=groups.REST,
        ),
    )
}


# The supplement activities, before Other in the menu.
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
            book=a.book,
            hidden=a.retired,
            group=a.group,
        )
        for a in supplement_seasons.ACTIVITIES
    }
)
OPEN_TRADITION = tradition_seasons.OPEN
HEDGE_SOURCE = "Hedge Magic, Revised Edition, Chapters Two to Seven, pp. 17-141"
ACTIVITIES[tradition_seasons.OPEN] = Activity(
    tradition_seasons.OPEN,
    "Open a student's Gift to a tradition",
    "A season with a Gifted student: the Opening Total against twice his "
    "Supernatural Abilities and Arts (+12 if already Opened).",
    tradition_seasons.SOURCE,
    book="HMRE",
    tradition="*",
    group=groups.TRADITION,
)


def _tradition_book(tradition: TraditionDef) -> tuple[str, str]:
    """The book a tradition's own seasons come from (the first its record
    cites) and their citation."""
    book = next(iter(sourcebooks.books_of(tradition.source.split(";")[0])), "HMRE")
    if book == "HMRE":
        return book, HEDGE_SOURCE
    title = sourcebooks.SOURCEBOOKS.get(book, book)
    return book, f"{title}, {tradition.name}"


#: Each tradition's own seasons (its catalog record's activities).
TRADITION_ACTIVITIES: tuple[str, ...] = tuple(
    a.key for t in catalog.load_tradition_catalog() for a in t.activities
)
ACTIVITIES.update(
    {
        a.key: Activity(
            a.key,
            a.label,
            a.summary + " Exposure in the Art or Ability worked.",
            _tradition_book(t)[1],
            working=True,
            distractable=True,
            book=_tradition_book(t)[0],
            tradition=t.id,
            group=groups.TRADITION,
        )
        for t in catalog.load_tradition_catalog()
        for a in t.activities
    }
)
ACTIVITIES[OTHER] = _OTHER_ACTIVITY


#: Fluctuating Fortune: Wealthy one year, Poor the next (DE p. 130);
#: which years are the Wealthy ones is the character's own (Background
#: fortune_wealthy_in, even by default).
FLUCTUATING_FORTUNE = "vf_fluctuating_fortune"


def working_seasons(character: Character, year: int | None = None) -> int:
    """The working seasons a companion owes each year: two, one fewer with
    Wealthy or License of Absence, one more if Poor (DE Ch. 4), between
    none and all four; with Fluctuating Fortune, one fewer in a Wealthy
    `year` and one more in a Poor one."""
    found = effects.collect(
        [scores.character_source(character.virtues_flaws)], "working_seasons"
    )
    owed = WORKING_SEASONS_PER_YEAR + int(effects.amount_total(found))
    if year is not None and any(
        vf.vf_id == FLUCTUATING_FORTUNE for vf in character.virtues_flaws
    ):
        wealthy = (year % 2 == 0) == (character.background.fortune_wealthy_in != "odd")
        owed += -1 if wealthy else 1
    return max(0, min(len(SEASONS), owed))


def is_planned(character: Character) -> bool:
    """Whether `character` is planned season by season (not a grog)."""
    return character.type in PLANNED_TYPES


def activities_for(
    character: Character,
    *,
    lab: bool = False,
    books: Collection[str] | None = None,
    keep: str = "",
) -> list[Activity]:
    """The activities `character` may plan, in menu order: lab work (on the
    laboratory's Planning tab) or everything else (on the character sheet,
    with the lab work that takes over a laboratory not yet theirs).
    With `books` (sourcebooks.saga_books), a supplement's activities only
    while it is in play -- except `keep`, a plan's activity already chosen,
    so editing that plan still shows it."""
    return [
        a
        for a in ACTIVITIES.values()
        if character.type in a.who
        and (a.lab == lab or (a.sheet and not lab))
        and not a.hidden
        and (a.key == keep or sourcebooks.in_play(a.book, books))
        and _member(character, a.tradition)
    ]


def _member(character: Character, tradition: str) -> bool:
    if not tradition:
        return True
    if tradition == "*":
        return bool(character.traditions)
    return tradition in character.traditions


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
    """xp per score step: Arts 1, Mastery 5, an Ability its table's (5,
    or 1 for an Accelerated Ability or a hedge Art on the Art table)."""
    kind, name = _split(subject)
    if kind == "art":
        return xp.ART_FACTOR
    if kind == "ability":
        return access.ability_factor(name)
    return xp.ABILITY_FACTOR


# -- checking and working out a plan -----------------------------------------


def source_quality(plan: SeasonPlan) -> int | None:
    """The plan's Source Quality where it doesn't depend on anyone else:
    typed, or the rule's default."""
    if plan.source_quality is not None:
        return plan.source_quality
    if plan.activity in (EXPOSURE, TEACH):
        return EXPOSURE_QUALITY
    if plan.activity == PRACTICE:
        # Split between subjects, it is the lowest of their qualities (DE p.
        # 377): 5 only if every one is a spell's Mastery.
        chosen = [a for a in plan.allocations if a.subject]
        mastery = bool(chosen) and all(
            _split(a.subject)[0] == "mastery" for a in chosen
        )
        return MASTERY_PRACTICE_QUALITY if mastery else PRACTICE_QUALITY
    return None


def allocations(plan: SeasonPlan) -> list[XpAllocation]:
    """The plan's subjects with the Source Quality each gets where that's
    known from the plan alone: Exposure's 2 points go to one subject, or 1
    each to two; Teaching's to its one subject; Practice's to its one
    subject, or as typed when split; Adventure's are as typed. Study from a teacher, a master or vis names one subject
    (its Source Quality is worked out in outcome())."""
    chosen = [a for a in plan.allocations if a.subject]
    if plan.activity == EXPOSURE:
        each = EXPOSURE_QUALITY // max(1, len(chosen[:2]))
        return [XpAllocation(a.subject, each) for a in chosen[:2]]
    if plan.activity == PRACTICE and len(chosen) > 1:
        return chosen
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
    mastery = book_kinds.mastery_subject(book.ability, book.spell_id)
    if mastery is not None:
        return mastery
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
    """How many this teacher teaches this season, whatever the subject:
    the +6 and +3 for one or two students, and the Arts' one-on-one rule,
    count them all (DE p. 378)."""
    return sum(
        1
        for p in plans_this_season(saga, plan)
        if p.activity == TAUGHT and p.teacher_id == plan.teacher_id
    )


#: A language at this score reads a book or teaches in it (DE p. 378).
READING_LANGUAGE = 4


def shared_language(teacher: Character, student: Character) -> bool:
    """Whether teacher and student share a language at 4 or more, or
    either has none recorded (the troupe hasn't typed them)."""

    def spoken(person: Character) -> set[str]:
        return {
            a.name.partition(": ")[2] or a.name
            for a in person.abilities
            if (
                a.name.startswith(("Living Language:", "Dead Language:"))
                or a.name == "Latin"
            )
            and a.level >= READING_LANGUAGE
        }

    mine, theirs = spoken(student), spoken(teacher)
    return not mine or not theirs or bool(mine & theirs)


#: The raw vis a vis study plan draws on, and whose it is (vis.py).
vis_pool = vis.season_pool
whose_vis = vis.payer


def _gloss_problems(
    saga: Saga, character: Character, book: Book, subject: str
) -> list[str]:
    """Who may gloss a book (Covenants, Other Opus Types): a reader at least
    half as skilled as its Level, with better Communication than its
    author; a gloss can't join resonant materials or clarification."""
    found: list[str] = []
    if book.level is not None and score(character, subject) * 2 < book.level:
        found.append(
            f"A gloss needs a score of at least half {book.name}'s Level "
            f"({book.level}): {character.name} has {score(character, subject)}."
        )
    author = saga.character(book.author_id)
    com = character.characteristics.communication
    if author is not None and com <= author.characteristics.communication:
        found.append(
            f"A gloss needs better Communication than the author: "
            f"{character.name} {com:+d}, {author.name} "
            f"{author.characteristics.communication:+d}."
        )
    if library.extended_quality(saga) and (
        "clarified" in book.craft or any(p in book.craft for p in book_kinds.RESONANCE)
    ):
        found.append(
            "A gloss expresses resonance: it can't join resonant materials or "
            "clarification."
        )
    return found


def _codex_reader_problems(
    saga: Saga, character: Character, plan: SeasonPlan, book: Book
) -> list[str]:
    """One reader a season per codex: another character reading this book,
    or another bound in the same codex, this season (Covenants, Varieties of
    Manuscript)."""
    form = book_kinds.PHYSICAL_FORMS.get(book.physical_form)
    if form is not None and form.many_readers:
        return []
    if book.opus == book_kinds.REALIA:
        return []  # shared, at a lower Quality (_realia_readers)
    for other in plans_this_season(saga, plan):
        if other.character_id == character.id or other.activity != READ:
            continue
        theirs = next((b for b in saga.books if b.id == other.book_id), None)
        if theirs is None or not library.same_codex(saga, book, theirs):
            continue
        reader = saga.character(other.character_id)
        who = reader.name if reader is not None else "Someone else"
        if theirs.id == book.id:
            return [f"{who} is reading {book.name} this season: one reader at a time."]
        return [
            f"{who} is reading {theirs.name} this season, bound in the same codex "
            f"as {book.name}: one reader a season for the whole codex."
        ]
    return []


def _study_problems(
    saga: Saga, character: Character, plan: SeasonPlan, chosen: list[XpAllocation]
) -> list[str]:
    """The problems of the study activities."""
    if plan.activity == READ:
        return _reading_problems(saga, character, plan)
    if not chosen:
        return ["Choose what the experience goes into."]
    subject = chosen[0].subject
    kind = _split(subject)[0]
    if plan.activity == TEACH and kind != "ability":
        return ["A teacher gains Exposure in Teaching or the language used."]
    if plan.activity in (TAUGHT, TRAINED):
        return _taught_problems(saga, character, plan, subject)
    if plan.activity == VIS_STUDY:
        return _vis_study_problems(saga, character, plan, subject)
    return []


def _reading_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    """Reading a summa or tractatus: the book is at hand, set, and still has
    something to teach."""
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None:
        return ["Choose the book to study."]
    if not library.can_read(saga, character, book):
        return [
            f"{character.name} can't get at {book.name}: it isn't in their "
            "covenant's library or their own keeping."
        ]
    subject = book_subject(book)
    missing = library.numbers_to_set(book)
    if subject is not None and missing:
        return [
            f"{book.name}'s {' and '.join(missing)} {'are' if len(missing) > 1 else 'is'} "
            "still to be set: edit the book first."
        ]
    if subject is None or book.quality is None:
        return [f"{book.name} isn't a summa or tractatus with a Quality."]
    found: list[str] = []
    if _split(subject)[0] == "art" and character.type != "magus":
        found.append("Only the Gifted study the Arts.")
    if book.type == "Tractatus" and book_seasons.written_by(book, character):
        found.append(
            f"{character.name} wrote {book.name}: nobody gains from studying "
            "a tractatus of his own (DE p. 378)."
        )
    language = book.language or "Latin"
    # A character with no Abilities typed (a stat-less NPC) isn't checked.
    typed = bool(character.abilities)
    # A related language reads at its penalty (Romaic Greek reads
    # Classical Greek at -2, rules.languages).
    reads = max(
        book_seasons.language_score(character, language),
        languages.understanding_score(character, language),
    )
    if typed and reads < READING_LANGUAGE:
        found.append(
            f"Studying {book.name} needs {language} at {READING_LANGUAGE} "
            f"(DE p. 378); {character.name} has {reads}."
        )
    if typed and ability_level(character, "Artes Liberales") < 1:
        found.append(
            f"{character.name} can't read: studying a book needs a score in "
            "Artes Liberales (DE p. 378)."
        )
    if book.opus == book_kinds.REALIA and book.type == "Tractatus":
        studied = character.tractatus_read.count(book.id)
        if studied >= book.quality:
            found.append(
                f"{character.name} has studied {book.name} {studied} "
                f"time{'s' if studied != 1 else ''}: a realia teaches each "
                "reader as many times as its Quality (Covenants p. 102)."
            )
    elif book.type == "Tractatus" and book.id in character.tractatus_read:
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
    found += _codex_reader_problems(saga, character, plan, book)
    if plan.gloss:
        found += _gloss_problems(saga, character, book, subject)
    return found


def _taught_problems(
    saga: Saga, character: Character, plan: SeasonPlan, subject: str
) -> list[str]:
    """Being taught or trained: the teacher or master is someone else, and
    skilled enough."""
    teacher = saga.character(plan.teacher_id)
    role = "teacher" if plan.activity == TAUGHT else "master"
    if teacher is None:
        return [f"Choose the {role}."]
    if teacher.id == character.id:
        return [f"Nobody can be their own {role}."]
    kind, name = _split(subject)
    if (
        kind == "ability"
        and study.learning_supernatural(character, name)
        and hybrid.ABILITY_REALMS.get(name, realms.HERMETIC) == realms.HERMETIC
        and not study.gifted(character)
    ):
        return [
            f"Only the Gifted learn a Supernatural Ability of Magic like {name} "
            "(DE p. 383)."
        ]
    if plan.activity == TRAINED:
        return _trained_problems(character, teacher, subject)
    return _teacher_problems(saga, character, plan, teacher, subject)


def _trained_problems(
    character: Character, master: Character, subject: str
) -> list[str]:
    if _split(subject)[0] != "ability":
        return ["Only Abilities can be trained (DE Ch. 10, Training)."]
    if (
        character.animal is not None
        and score(master, ability_subject("Animal Handling")) < 1
    ):
        return [
            f"Training an animal needs Animal Handling: {master.name} has none "
            "(DE p. 385)."
        ]
    theirs, mine = score(master, subject), score(character, subject)
    if theirs < 2 or theirs <= mine:
        return [
            f"A master needs a score of 2 or more, higher than the "
            f"trainee's: {master.name} has {theirs}, {character.name} {mine}."
        ]
    return []


def _teacher_problems(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    teacher: Character,
    subject: str,
) -> list[str]:
    """A teacher who is teaching this season, skilled enough, and not
    over their number of students."""
    found: list[str] = []
    kind = _split(subject)[0]
    theirs, mine = score(teacher, subject), score(character, subject)
    teacher_plan = next(
        (p for p in plans_this_season(saga, plan) if p.character_id == teacher.id),
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
    if not shared_language(teacher, character):
        found.append(
            f"{teacher.name} and {character.name} share no language at "
            f"{READING_LANGUAGE} (DE p. 378)."
        )
    students = students_of(saga, plan)
    if kind == "art" and students > 1:
        found.append(
            "The Arts are taught one student at a time, and "
            f"{teacher.name} has {students} this season."
        )
    elif students > study.max_students(teacher):
        found.append(
            f"{teacher.name} can teach {study.max_students(teacher)} "
            f"student(s) at once; {students} are planned."
        )
    return found


def _vis_study_problems(
    saga: Saga, character: Character, plan: SeasonPlan, subject: str
) -> list[str]:
    """Studying vis: for an Art, with enough pawns of it to hand."""
    found: list[str] = []
    kind, art = _split(subject)
    if kind != "art":
        found.append("Vis is studied for an Art.")
    else:
        pawns = study.season_vis_pawns(character, score(character, subject))
        held = vis_pool(saga, character, plan).get(art.lower(), 0)
        if held < pawns:
            found.append(
                f"Studying {art} takes {pawns} pawn(s) of {art} vis; "
                f"{whose_vis(character, plan)} raw vis has {held}."
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
    # Each family of activities checks its own plans (HANDLERS).
    return HANDLERS[plan.activity].problems(saga, character, plan)


@dataclass
class XpGain:
    """Experience a season gives one subject: the working and the totals
    before and after."""

    subject: str
    result: StudyResult
    before: int  # total xp before the season
    #: The Virtue that shared this experience from the season's own subject
    #: (Secondary Insight); "" for the season's own Advancement Total.
    via: str = ""

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
    #: That tractatus is a realia: each season studying it is recorded
    #: (it may be studied as many times as its Quality).
    realia: bool = False
    #: Reading a summa: its id, to record it was studied (a commentary on
    #: it can then be read).
    summa: str | None = None
    #: Glossing while reading: the book glossed.
    glossed: str | None = None
    #: Vis study still to roll (a preview made without a die).
    pending_roll: bool = False
    #: Lab work: what the season in the laboratory does.
    lab_work: lab_seasons.LabWork | None = None
    #: Book work: what the season does to books.
    book_work: book_seasons.BookWork | None = None
    #: Apprentice work.
    apprentice_work: apprentice_seasons.ApprenticeWork | None = None
    #: An Opening to a hedge tradition, or a tradition's own work.
    tradition_work: tradition_seasons.TraditionWork | None = None
    #: Seeking an insight: whether one was gained.
    insight: bool = False
    #: Faith Points gained (Good Works).
    faith: int = 0
    #: What a supplement season does besides experience (decision 38).
    supplement: supplement_work.SupplementWork | None = None
    #: Setting up a new laboratory: its id, once the season is applied.
    new_lab_id: str | None = None
    #: A botch's Warping Points (one per zero) and the aura it happened in,
    #: given when the season is applied (and Twilight checked at 2+).
    warping: int = 0
    warping_aura: int = 0

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
    bonuses: Sequence[Line] = (),
    year: int | None = None,
    hermetic_halved: bool = False,
) -> XpGain:
    """The xp a season gives in `subject`; `year`, the season's, gives the
    student's age for the Virtues that read it; `hermetic_halved`, a holy
    magus reading a Hermetic book."""
    kind, name = _split(subject)
    result = season_of_study(
        character,
        name,
        quality,
        activity=activity,
        is_art=kind == "art",
        gain_limit=gain_limit,
        months_lost=months,
        mastery=kind == "mastery",
        bonuses=bonuses,
        age=None
        if year is None
        else character_age(character.background.year_born, year),
        hermetic_halved=hermetic_halved,
    )
    return XpGain(subject, result, subject_xp(character, subject))


def _lab_teaching(saga: Saga, teacher: Character) -> list[Line]:
    """The teacher's laboratory's Teaching Specialization, for teaching or
    training done there (DE p. 291; the plan's `in_lab`). Teaching a spell
    is a Lab Total, which the Spells Specialization helps instead."""
    bonus = lab_stats.teaching_bonus(saga, saga.laboratory(teacher.assigned_lab_id))
    if not bonus:
        return []
    return [
        Line(
            "Teaching Specialization (in the laboratory)",
            amount=bonus,
            source=lab_stats.SPECIALIZATION_SOURCE,
        )
    ]


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
    """Experimenting: the simple die joins the Lab Total, then
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
    aura, safety = lab_rules.botch_conditions(
        saga, character, saga.laboratory(plan.lab_id)
    )
    art, _ = lab_seasons.made_arts(work, plan)
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
    # Stabilizing repeats the Discovery's experiment: its risk, not the plan's.
    risk = goal.discovery_risk if stabilizing and goal is not None else plan.risk
    chart = experiment.chart(
        roll_rng,
        risk,
        aura,
        art,
        saga,
        character=character,
        seeking=seeks,
        shift=shift,
        stabilizing=stabilizing,
        safety=safety,
    )
    work.experiment = chart
    settle_chart(result, character, saga)
    if stabilizing:
        assert result.lab_work is not None
        result.lab_work.research_warping = max(
            0, result.lab_work.research_magnitude - dice.simple_die(roll_rng)
        )


def _lab_hazards(
    result: Outcome, character: Character, saga: Saga, rng: random.Random
) -> None:
    """An unsafe or Warping laboratory's rolls on the season's work: added
    to the experiment's chart, or standing alone (`lab_only`) for the
    storyguide's Experiment results step."""
    work = result.lab_work
    lab = saga.laboratory(result.plan.lab_id)
    if work is None or lab is None:
        return
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    safety = lab_stats.lab_safety(lab, by_id, saga)
    warping = max(0, lab_stats.lab_characteristic_total(lab, by_id, "warping", saga)[3])
    chart = work.experiment
    hazards = experiment.lab_hazards(
        rng,
        character,
        safety,
        warping,
        saga=saga,
        botch_count=chart.botch_dice if chart is not None else None,
    )
    if hazards is None:
        return
    if chart is not None:
        experiment.add_hazards(chart, hazards)
    else:
        hazards.lab_only = True
        work.experiment = chart = hazards
    chart.item_at_risk = result.plan.activity == enchant_seasons.INVESTIGATE and (
        experiment.harms_item(chart)
    )
    _note_chart(result, chart)


_CHART_NOTES = ("Extraordinary Results: ", "Laboratory: ")


def _note_chart(result: Outcome, chart: experiment.Extraordinary) -> None:
    """The season's note of its chart roll (or its laboratory's rolls),
    replacing any made before."""
    label = _CHART_NOTES[1] if chart.lab_only else _CHART_NOTES[0]
    result.notes = [n for n in result.notes if not n.startswith(_CHART_NOTES)] + [
        label + " ".join(chart.results)
    ]


def settle_chart(result: Outcome, character: Character, saga: Saga) -> None:
    """The work as the season's chart roll leaves it: with No Benefit the
    die and risk are lost (a Discovery may still come with it), and the
    work is abandoned if it is now too low; and the roll noted. Run again
    when the storyguide chooses the other of two rolls."""
    work = result.lab_work
    assert work is not None and work.experiment is not None
    chart = work.experiment
    plan = result.plan
    if chart.no_benefit and plan.activity != experiment.STABILIZE:
        # Only the die and the risk are lost: the work is still an
        # experiment (Inventive Genius, an Experimentation Specialization).
        _, plain = lab_seasons.work(
            saga, character, replace(plan, experiment_die=0, risk=0)
        )
        if plain is None or plain.too_low:
            chart.wasted = chart.abandoned = True
            chart.discovery = False
            chart.discovery_shift = None
        else:
            plain.experiment = chart
            result.lab_work = plain
    chart.item_at_risk = (
        plan.activity == enchant_seasons.INVESTIGATE and experiment.harms_item(chart)
    )
    _note_chart(result, chart)


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
    if plan.activity in ADVANCEMENT_ACTIVITIES and not result.problems:
        _master_of_none(saga, character, plan, result)
        _share(character, plan, result)
    if plan.correspondence and not result.problems:
        result.gains.append(_correspondence(character, plan.correspondence))
        result.notes.append(
            "Useful correspondence: +1 xp (Covenants, Other Opus Types; at "
            "least one letter received this season)."
        )
    if (
        not result.problems
        and result.gains
        and derived.wound_penalty(character.wounds, character.virtues_flaws)
        <= study.WOUNDED_STUDY
    ):
        # The halving is in each gain's Advancement Total (rules.study).
        result.notes.append(
            "Wounded (-3 to -5): the season's Advancement Total is halved."
        )
    return result


#: Craft and business seasons that a -3 Wound Penalty rules out (lab work too).
_CRAFT = (
    "working_season",
    "workshop_production",
    "make_excellent_item",
    "make_wondrous_item",
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
    penalty = derived.wound_penalty(character.wounds, character.virtues_flaws)
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


#: The activities whose experience is an Advancement Total in the subjects
#: chosen (Master of None's, and the Virtues that share it: rules.study_virtues).
ADVANCEMENT_ACTIVITIES: tuple[str, ...] = (
    *STUDY_ACTIVITIES,
    EXPOSURE,
    PRACTICE,
    ADVENTURE,
)


def _raised_earlier(
    saga: Saga | None, character: Character, plan: SeasonPlan
) -> set[str]:
    """Subjects an Advancement Total has raised, or a plan still to be
    played will raise, earlier in the plan's year."""
    raised = study_virtues.raised_this_year(character, plan.year)
    if saga is None:
        return raised
    for earlier in saga.season_plans:
        if (
            earlier.character_id != character.id
            or earlier.year != plan.year
            or SEASONS.index(earlier.season) >= SEASONS.index(plan.season)
            or earlier.activity not in ADVANCEMENT_ACTIVITIES
        ):
            continue
        raised |= {a.subject for a in allocations(earlier)}
        book = next((b for b in saga.books if b.id == earlier.book_id), None)
        subject = book_subject(book) if book is not None else None
        if earlier.activity == READ and subject:
            raised.add(subject)
    return raised


def _master_of_none(
    saga: Saga | None, character: Character, plan: SeasonPlan, result: Outcome
) -> None:
    """Master of None: an Advancement Total's xp in a subject already raised
    this year is lost (DE Ch. 4)."""
    if not study_virtues.has(character, study_virtues.MASTER_OF_NONE):
        return
    raised = _raised_earlier(saga, character, plan)
    for gain in result.gains:
        if gain.via or gain.subject not in raised or not gain.result.xp:
            continue
        name = _split(gain.subject)[1]
        gain.result.notes.append(
            f"Master of None: {name} was already raised this year; "
            f"{gain.result.xp} xp lost."
        )
        gain.result.xp = 0


def _share(character: Character, plan: SeasonPlan, result: Outcome) -> None:
    """Experience the character's Virtues share from the season's subject
    with others (Secondary Insight, Elemental Magic...)."""
    kind = _STUDY_KIND[plan.activity]
    for gain in list(result.gains):
        subject_kind, name = _split(gain.subject)
        if gain.via or subject_kind not in ("art", "ability"):
            continue
        season = study_virtues.Studied(
            character,
            subject_kind,
            name,
            kind,
            gain.result.advancement_total,
            gain.result.xp,
            plan.insight_arts,
        )
        for each in study_virtues.shared(season):
            line = Line(each.via, amount=each.xp, source=study_virtues.SOURCE)
            notes = [each.note.strip()] if each.note else []
            result.gains.append(
                XpGain(
                    each.subject,
                    StudyResult(0, each.xp, [line], notes),
                    subject_xp(character, each.subject),
                    via=each.via,
                )
            )


def _fixed_gain(
    character: Character, subject: str, amount: int, via: str, source: str
) -> XpGain:
    """Experience a rule grants as a set number of points, not an Advancement
    Total: Affinity, Savantism, wounds, a Gain Limit and Master of None leave
    it alone, and no Virtue shares it (`via` names the rule)."""
    line = Line(via, amount=amount, source=source)
    return XpGain(
        subject,
        StudyResult(0, amount, [line], []),
        subject_xp(character, subject),
        via=via,
    )


def _correspondence(character: Character, subject: str) -> XpGain:
    """A season of useful correspondence: book_kinds.CORRESPONDENCE_XP in
    its subject, a fixed gain (Covenants p. 90)."""
    return _fixed_gain(
        character,
        subject,
        book_kinds.CORRESPONDENCE_XP,
        "Useful correspondence",
        book_kinds.CORRESPONDENCE_SOURCE,
    )


def _outcome(
    character: Character,
    plan: SeasonPlan,
    saga: Saga | None,
    rng: random.Random | None,
    result: Outcome,
    activity: Activity,
) -> Outcome:
    """The season's gains (outcome() without the wound rule), from the
    activity's family (HANDLERS)."""
    HANDLERS[plan.activity].outcome(saga, character, plan, rng, result)
    return result


# -- the activity families ----------------------------------------
#
# Each family of activities says what stops a plan and what the season gives,
# in one Handler; HANDLERS maps every activity that gives experience to its
# family. problems() and outcome() above do the checks every activity shares
# (who may plan it, Twilight, wounds) and hand the rest to the family.

#: What a family that works from the saga says when there is none.
NEEDS_SAGA = "This activity needs the saga to be worked out."

ProblemsFn = Callable[[Saga | None, Character, SeasonPlan], list[str]]
OutcomeFn = Callable[
    [Saga | None, Character, SeasonPlan, random.Random | None, Outcome], None
]


@dataclass(frozen=True)
class Handler:
    """How one family of activities is checked and worked out."""

    problems: ProblemsFn
    outcome: OutcomeFn


def _with_saga(
    problems_: Callable[[Saga, Character, SeasonPlan], list[str]],
    outcome_: Callable[
        [Saga, Character, SeasonPlan, random.Random | None, Outcome], None
    ],
    *,
    no_saga: str = NEEDS_SAGA,
) -> Handler:
    """A Handler for a family that works from the saga: without one, its
    plans can't be checked (`no_saga`); its outcome is only asked for once
    they have been."""

    def checked(saga: Saga | None, character: Character, plan: SeasonPlan):
        return [no_saga] if saga is None else problems_(saga, character, plan)

    def worked(
        saga: Saga | None,
        character: Character,
        plan: SeasonPlan,
        rng: random.Random | None,
        result: Outcome,
    ) -> None:
        assert saga is not None, "outcome() is worked out after problems()"
        outcome_(saga, character, plan, rng, result)

    return Handler(checked, worked)


def _pending(plan: SeasonPlan, rng: random.Random | None) -> bool:
    """A roll left for when the season is played: no die typed on the plan
    and nothing to roll it with (a preview)."""
    return plan.die is None and rng is None


def _exposure(character: Character, ability: str, year: int | None = None) -> XpGain:
    """Exposure in `ability` (DE Ch. 10, Exposure)."""
    return _gain(
        character, ability_subject(ability), EXPOSURE_QUALITY, "exposure", 0, year=year
    )


# Lab work: its own rules module, and Exposure in Magic
# Theory.


def _lab_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    found, _ = lab_seasons.work(saga, character, plan)
    if plan.days_away < 0:
        found.append("Days away can't be negative.")
    return found


def _lab_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    if _horoscope_botched(saga, character, plan, rng, result):
        return
    plan = result.plan
    _, result.lab_work = lab_seasons.work(saga, character, plan)
    if result.lab_work is not None and result.lab_work.vis_wasted:
        result.notes.append(lab_seasons.waste_note(result.lab_work))
    if result.lab_work is not None and result.lab_work.lab_total.notes:
        result.notes += [
            n
            for n in result.lab_work.lab_total.notes
            if n.startswith("Laboratory Horoscope")
        ]
    if plan.activity == enchant_seasons.INVESTIGATE and result.lab_work is not None:
        if _pending(plan, rng):
            result.pending_roll = True
        else:
            result.notes += enchant_seasons.investigate(
                result.lab_work, plan, rng or random.Random(), saga
            )
    if result.lab_work is not None and (
        plan.experimenting or plan.activity == experiment.STABILIZE
    ):
        _experiment(result, character, saga, rng)
    if result.lab_work is not None and rng is not None:
        _lab_hazards(result, character, saga, rng)
    if result.lab_work is not None and result.lab_work.too_low:
        result.notes.append(result.lab_work.too_low)
    rolled = plan.activity in laboratory_seasons.ROLLED and (
        plan.activity != laboratory_seasons.MOVE or plan.by_spell
    )
    if rolled and result.lab_work is not None:
        result.notes += result.lab_work.notes
        if _pending(plan, rng):
            result.pending_roll = True
        else:
            result.notes += laboratory_seasons.roll(
                result.lab_work, character, plan, rng or random.Random(), saga
            )
    result.gains.append(_exposure(character, "Magic Theory", year=plan.year))


def _horoscope_botched(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> bool:
    """A Laboratory Horoscope to roll as the season is played: the stress
    die joins the plan (as one typed at the table would); a botch wastes
    the season (The Mysteries, Planetary Magic)."""
    if not plan.horoscope or plan.horoscope_die is not None or rng is None:
        return False
    enchanting = plan.activity in (
        enchant_seasons.INSTIL,
        enchant_seasons.LESSER_WORK,
        enchant_seasons.CHARGED_WORK,
    )
    if not lab_virtues.horoscope_applies(character, plan.activity, enchanting):
        return False
    wanted = min(plan.horoscope, lab_virtues.HOROSCOPE_MAX)
    die = dice.stress_die(rng, wanted, saga=saga)
    result.plan = replace(plan, horoscope_die=die.value)
    if die.botches:
        result.problems.append(
            f"The Laboratory Horoscope botched ({die.botches} on {wanted} botch "
            "dice): the season's lab work is wasted."
        )
        return True
    return False


# Writing and copying books: Exposure in the writing's
# Ability.


def _book_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    found, _ = book_seasons.work(saga, character, plan)
    return found


def _book_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    _, result.book_work = book_seasons.work(saga, character, plan)
    result.gains.append(
        _exposure(
            character, book_seasons.exposure_ability(character, plan), year=plan.year
        )
    )


# Hedge traditions: Opening a student gives Exposure in Teaching; a
# tradition's own work gives Exposure in the Art or Ability worked.


def _tradition_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    if plan.activity == tradition_seasons.OPEN:
        found, _ = tradition_seasons.open_work(saga, character, plan)
        return found
    chosen = [a for a in plan.allocations if a.subject]
    if not chosen:
        return ["Choose the Art or Ability worked."]
    kind, name = _split(chosen[0].subject)
    if kind != "ability":
        return ["Choose the Art or Ability worked."]
    found, _ = tradition_seasons.work(saga, character, plan, name)
    return found


def _tradition_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    if plan.activity == tradition_seasons.OPEN:
        _, work = tradition_seasons.open_work(saga, character, plan)
        result.gains.append(_exposure(character, "Teaching", year=plan.year))
    else:
        chosen = next(a for a in plan.allocations if a.subject)
        name = _split(chosen.subject)[1]
        _, work = tradition_seasons.work(saga, character, plan, name)
        result.gains.append(
            _gain(
                character,
                ability_subject(name),
                EXPOSURE_QUALITY,
                "exposure",
                _months(plan),
                year=plan.year,
            )
        )
    result.tradition_work = work
    if work is not None:
        result.notes += work.notes


# Apprentices: teaching gives Exposure in Teaching; searching for
# a Gifted child is a roll.


def _apprentice_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    found, _ = apprentice_seasons.work(saga, character, plan)
    return found


def _apprentice_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    _, work = apprentice_seasons.work(saga, character, plan)
    result.apprentice_work = work
    if work is not None:
        result.notes += work.notes
        if plan.activity == apprentice_seasons.TEACH_VIRTUE:
            result.notes.append(
                f"Source Quality {work.quality} against {work.target}: "
                + ("taught." if work.succeeds else "not learned.")
            )
    if plan.activity != apprentice_seasons.SEARCH:
        result.gains.append(_exposure(character, "Teaching", year=plan.year))
        return
    if _pending(plan, rng):
        result.pending_roll = True
        return
    botched = False
    if plan.die is not None:
        die = plan.die
    else:
        rolled = dice.stress_die(rng or random.Random(), 1, saga=saga)
        die, botched = rolled.value, rolled.botched
    total = character.characteristics.perception + die
    if botched:
        # A botch dupes the searcher (DE p. 269).
        result.notes.append(
            "Perception + a botch: the magus thinks he has found a Gifted "
            "child, but is duped, by the child or by a power that has "
            "replaced it with its servant (the storyguide decides)."
        )
        return
    result.notes.append(
        f"Perception + die {die} = {total} against "
        f"{apprentice_seasons.SEARCH_EASE}: "
        + (
            "a Gifted child is found (add them as a character)."
            if total >= apprentice_seasons.SEARCH_EASE
            else "no apprentice found this season."
        )
    )


# Integrating an insight into Arcane Discovery: a roll.


def _integrate_problems(
    saga: Saga | None, character: Character, plan: SeasonPlan
) -> list[str]:
    return [] if plan.research.strip() else ["Name the research goal."]


def _integrate_outcome(
    saga: Saga | None,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    if _pending(plan, rng):
        result.pending_roll = True
        return
    theory = laboratory_seasons.magic_theory(character)
    result.insight, note = experiment.insight_roll(
        character, plan, rng or random.Random(), theory, saga
    )
    result.notes.append(note)


# The supplements' study-like activities: their Source
# Quality, and what they do besides (supplement_work).


def _supplement_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    simple = supplement_seasons.BY_KEY[plan.activity]
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


def _supplement_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    simple = supplement_seasons.BY_KEY[plan.activity]
    quality = plan.source_quality if plan.source_quality is not None else simple.quality
    subject = allocations(plan)[0].subject
    kind = "exposure" if quality == EXPOSURE_QUALITY else "practice"
    if not simple.xp_to_work:
        result.gains.append(
            _gain(character, subject, quality or 0, kind, 0, year=plan.year)
        )
    result.faith = simple.faith
    result.supplement = supplement_work.work(saga, character, plan, rng)
    result.notes += result.supplement.notes


# Assisting in another's laboratory: Exposure in Magic Theory.


def _assist_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    return laboratory_seasons.assist_problems(saga, character, plan)


def _assist_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    result.gains.append(_exposure(character, "Magic Theory", year=plan.year))


# Setting up a new laboratory: Exposure in Magic Theory.


def _new_lab_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    return laboratory_seasons.new_lab_problems(saga, character, plan)


def _new_lab_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    result.notes.append(
        f"{laboratory_seasons.new_lab_name(character, plan)} is made, with the "
        "Basic Flaw until a second season's work in it."
    )
    result.gains.append(_exposure(character, "Magic Theory", year=plan.year))


# Study from books, teachers, training and vis (DE Ch. 10).


def _months_problem(plan: SeasonPlan) -> list[str]:
    return [] if 0 <= plan.months_lost <= 3 else ["Months lost must be 0 to 3."]


def _study_family_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    chosen = [a for a in plan.allocations if a.subject]
    found = _months_problem(plan) + _study_problems(saga, character, plan, chosen)
    found += _virtue_problems(saga, character, plan)
    if plan.activity != READ:
        for allocation in chosen[:1]:
            if not has_subject(character, allocation.subject):
                kind, name = _split(allocation.subject)
                if kind != "ability" or plan.activity == TEACH:
                    found.append(f"{character.name} doesn't have {name}.")
    return found


def _virtue_problems(
    saga: Saga | None, character: Character, plan: SeasonPlan
) -> list[str]:
    """What the student's Virtues and Flaws rule out (rules.study_virtues):
    an Ability they can't learn, an Art away from its substance."""
    if plan.activity == TEACH:
        return []
    subjects = [a.subject for a in plan.allocations if a.subject]
    if plan.activity == READ and saga is not None:
        book = next((b for b in saga.books if b.id == plan.book_id), None)
        subject = book_subject(book) if book is not None else None
        subjects = [subject] if subject else []
    kind = _STUDY_KIND[plan.activity]
    abilities = [_split(s)[1] for s in subjects if _split(s)[0] == "ability"]
    found = study_virtues.learning_problems(character, abilities, kind)
    if any(_split(s)[0] == "art" for s in subjects):
        present = plan.art_present or (
            saga is not None and _realia_present(saga, character, plan)
        )
        found += study_virtues.presence_problems(character, kind, True, present)
    return found


def _realia_present(saga: Saga, character: Character, plan: SeasonPlan) -> bool:
    """Reading a realia exhibit of hundreds of objects on an Art is studying
    in the Art's presence, for Study Requirement and Study Bonus, until the
    reader's score in it reaches book_kinds.REALIA_PRESENCE_ART (Against
    the Dark p. 61); a smaller realia isn't, since the objects needed grow
    with the Art (DE p. 145)."""
    if plan.activity != READ:
        return False
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None or book.opus != book_kinds.REALIA or not book.exhibit:
        return False
    subject = book_subject(book)
    if subject is None or _split(subject)[0] != "art":
        return False
    return score(character, subject) < book_kinds.REALIA_PRESENCE_ART


def _reading_lines(
    saga: Saga, character: Character, plan: SeasonPlan, book: Book, quality: int
) -> list[Line]:
    """What adds to a book's Quality as read this season: Study Bonus with
    the Art present (a realia on it counts), less a shared realia's split."""
    subject = book_subject(book) or ""
    present = plan.art_present or _realia_present(saga, character, plan)
    found = study_virtues.presence_lines(
        character, _STUDY_KIND[plan.activity], _split(subject)[0] == "art", present
    )
    if book.opus == book_kinds.REALIA:
        found += _realia_shared(saga, plan, book, quality)
    return found


def _realia_shared(
    saga: Saga, plan: SeasonPlan, book: Book, quality: int
) -> list[Line]:
    """What sharing the realia `book` this season takes from its Quality
    (none when the reader has it alone)."""
    readers = _realia_readers(saga, plan, book)
    penalty = book_kinds.realia_sharing_penalty(readers)
    if not penalty:
        return []
    return [
        Line(
            f"Realia shared by {readers} readers",
            amount=-min(penalty, quality),
            source=book_kinds.SHARED_REALIA_SOURCE,
        )
    ]


def _realia_readers(saga: Saga, plan: SeasonPlan, book: Book) -> int:
    """How many study the realia `book` this season, this plan's reader
    included (Against the Dark p. 59)."""
    others = {
        p.character_id
        for p in plans_this_season(saga, plan)
        if p.activity == READ
        and p.book_id == book.id
        and p.character_id != plan.character_id
    }
    return 1 + len(others)


def _months(plan: SeasonPlan) -> int:
    """Months lost to distractions, for an activity they lower."""
    return plan.months_lost if ACTIVITIES[plan.activity].distractable else 0


def _book_kind_notes(saga: Saga, character: Character, book: Book) -> list[str]:
    """What the book's kind says about reading it: a commentary is read only
    after a season on its summa (a note, not a refusal: seasons before the
    app recorded them aren't known)."""
    if book.opus != book_kinds.COMMENTARY:
        return []
    summa = next((b for b in saga.books if b.id == book.commentary_on), None)
    if summa is None:
        return [
            f"{book.name} is a commentary: it is read only after a season "
            "studying its summa (Covenants, Other Opus Types)."
        ]
    if summa.id in character.summae_read:
        return []
    return [
        f"{book.name} is a commentary on {summa.name}, which {character.name} "
        "has no season studying on record: a commentary is read only after "
        "one (Covenants, Other Opus Types)."
    ]


def _study_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    months = _months(plan)
    kind = _STUDY_KIND[plan.activity]
    if plan.activity == READ:
        book = next(b for b in saga.books if b.id == plan.book_id)
        subject = book_subject(book)
        quality = library.effective_quality(saga, book)
        assert subject is not None and quality is not None
        limit = book.level if book.type != "Tractatus" else None
        bonuses = _reading_lines(saga, character, plan, book, quality)
        result.realia = book.opus == book_kinds.REALIA
        result.gains.append(
            _gain(
                character,
                subject,
                quality,
                kind,
                months,
                gain_limit=limit,
                bonuses=bonuses,
                year=plan.year,
                hermetic_halved=hybrid.halves_study(
                    character, book, hybrid.hermetic_source(saga, book)
                ),
            )
        )
        if book.type == "Tractatus":
            result.tractatus = book.id
        else:
            result.summa = book.id
        result.notes += _book_kind_notes(saga, character, book)
        if plan.gloss:
            result.glossed = book.id
            if book.glossed:
                result.notes.append(
                    f"{book.name} is already glossed: another gloss adds no Quality."
                )
            elif book.author_id is None:
                result.notes.append(
                    "Its author isn't a character of the saga: check the "
                    "glosser's Communication is the better at the table."
                )
        codex = library.codex_of(saga, book)
        if codex is not None and codex.collection == book_kinds.FOLIO:
            result.gains.append(
                _fixed_gain(
                    character,
                    ability_subject(book_kinds.FOLIO_LORE),
                    book_kinds.FOLIO_LORE_XP,
                    "A folio's notes on its author",
                    book_kinds.FOLIO_SOURCE,
                )
            )
        return
    if plan.activity in (TAUGHT, TRAINED):
        teacher = saga.character(plan.teacher_id)
        assert teacher is not None
        subject = allocations(plan)[0].subject
        if plan.activity == TAUGHT:
            quality = study.teaching_quality(teacher, students_of(saga, plan))
        else:
            quality = score(teacher, subject) + 3 + study.teacher_bonus(teacher)
        name = _split(subject)[1]
        first = _split(subject)[0] == "ability" and study.learning_supernatural(
            character, name
        )
        if first:
            penalty = study.supernatural_penalty(character, name)
            if penalty:
                quality -= penalty
                result.notes.append(
                    f"A first season in {name}: -{penalty} for the student's "
                    "other Supernatural Abilities and opened Arts (DE p. 383)."
                )
        gain = _gain(
            character,
            subject,
            max(0, quality),
            kind,
            months,
            gain_limit=score(teacher, subject),
            bonuses=[
                *study.gift_lines(teacher, character),
                *(_lab_teaching(saga, teacher) if plan.in_lab else []),
            ],
            year=plan.year,
        )
        if first and gain.result.xp < study.SUPERNATURAL_FIRST_XP:
            result.notes.append(
                f"{gain.result.xp} xp is short of the {study.SUPERNATURAL_FIRST_XP} "
                f"a first season in {name} must give: nothing is learned."
            )
            gain.result.xp = 0
        if (
            plan.activity == TRAINED
            and character.animal is not None
            and not score(character, subject)
            and not _animal_learns(saga, character, name, rng, result)
        ):
            gain.result.xp = 0
        result.gains.append(gain)
        return
    if plan.activity == VIS_STUDY:
        _vis_study_outcome(saga, character, plan, rng, result, kind, months)
        return
    _plain_outcome(saga, character, plan, rng, result)


#: A tamed animal trained in an Ability it lacks makes a Loyalty test
#: against this at the season's end; failing, it learns nothing (DE p.
#: 385).
NEW_ABILITY_LOYALTY = 6


def _animal_learns(
    saga: Saga | None,
    animal: Character,
    ability: str,
    rng: random.Random | None,
    result: Outcome,
) -> bool:
    """A tamed animal's Loyalty test for a new Ability: Loyal + stress
    die against 6 (DE p. 385); a preview says it will be rolled."""
    if rng is None:
        result.notes.append(
            f"{ability} is new to {animal.name}: a Loyalty test (Loyal "
            f"{tamed.loyalty(animal):+d} + stress die) against {NEW_ABILITY_LOYALTY} "
            "at the season's end, or the season is wasted (DE p. 385)."
        )
        return True
    die = dice.stress_die(rng, 1, saga=saga)
    total = tamed.loyalty(animal) + die.value
    passed = not die.botched and total >= NEW_ABILITY_LOYALTY
    result.notes.append(
        f"Loyalty test for {ability}: Loyal {tamed.loyalty(animal):+d} + die "
        f"{die.value} = {total} against {NEW_ABILITY_LOYALTY}: "
        + ("it learns." if passed else "the season is wasted.")
        + " (DE p. 385)"
    )
    return passed


def _vis_study_outcome(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
    kind: str,
    months: int,
) -> None:
    subject = allocations(plan)[0].subject
    art = _split(subject)[1]
    pawns = study.season_vis_pawns(character, score(character, subject))
    # Studied where it is usually done, in the student's laboratory, with
    # that laboratory's aura (DE p. 378); else where they live.
    lab = saga.laboratory(character.assigned_lab_id)
    if lab is not None:
        aura, realm = lab_rules.lab_aura(saga, lab)
        in_regio = bool(lab.place_id) and lab.place_level > 0
    else:
        aura, realm = realms.home_aura(saga, character)
        in_regio = realms.home_in_regio(saga, character)
    aura_mod, _ = hybrid.aura_modifier(character, realm, aura)
    botch_dice = pawns + hybrid.foreign_botch_dice(
        character, realm, aura, in_regio=in_regio
    )
    result.vis_spent = (plan.vis_from or "character", art, pawns)
    result.notes.append(
        f"Source Quality: stress die + aura {aura_mod:+d} ({aura} {realm}); "
        f"{pawns} pawn(s) of {art} vis; {botch_dice} botch dice."
    )
    if _pending(plan, rng):
        result.pending_roll = True
        return
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
        # A Warping Point for each zero, as for any supernatural botch (DE
        # p. 390); two or more bring the Twilight check (DE pp. 228, 378).
        result.warping, result.warping_aura = botches, aura
        result.notes.append(
            f"Botch: {botches} zero(s) on the botch dice: {botches} Warping "
            "Point(s)"
            + (
                "; a double botch may bring on Wizard's Twilight."
                if botches >= 2
                else "."
            )
        )
    quality = max(0, die_value + aura_mod)
    bonuses = study_virtues.presence_lines(character, kind, True, plan.art_present)
    result.gains.append(
        _gain(
            character, subject, quality, kind, months, bonuses=bonuses, year=plan.year
        )
    )


# Exposure, Practice and Adventure (DE Ch. 10): experience in the subjects
# chosen, from the plan's own figures.


def _plain_problems(
    saga: Saga | None, character: Character, plan: SeasonPlan
) -> list[str]:
    found = _months_problem(plan)
    chosen = [a for a in plan.allocations if a.subject]
    if not chosen:
        found.append("Choose what the experience goes into.")
    for allocation in chosen:
        if not has_subject(character, allocation.subject):
            found.append(
                f"{character.name} doesn't have {_split(allocation.subject)[1]}."
            )
    if len({a.subject for a in chosen}) < len(chosen):
        found.append("The same subject is named twice.")
    found += _virtue_problems(saga, character, plan)
    if plan.activity == EXPOSURE and len(chosen) > 2:
        found.append("Exposure goes into one subject, or is split between two.")
    if plan.activity == PRACTICE:
        found += _practice_split_problems(character, plan, chosen)
        if any(_split(a.subject)[0] == "art" for a in chosen):
            found.append(
                "Arts can't be practised: study them from vis or books "
                "(DE Ch. 10, Practice)."
            )
        for allocation in chosen:
            kind, name = _split(allocation.subject)
            hedge = (
                tradition_seasons.practice_forbidden(character, name)
                if kind == "ability"
                else None
            )
            if hedge is not None:
                found.append(f"The {hedge.name}' Arts can't be practised.")
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
        elif sum(a.points for a in chosen) != quality + study.season_bonus(
            character, "adventure"
        ):
            whole = quality + study.season_bonus(character, "adventure")
            found.append(
                f"Split all {whole} points of Source Quality"
                + (
                    f" ({quality} + {whole - quality} from Independent Study)"
                    if whole != quality
                    else ""
                )
                + f": {sum(a.points for a in chosen)} are split."
            )
        if any(not 1 <= a.points <= ADVENTURE_PER_SUBJECT for a in chosen):
            found.append(
                f"Each subject gets 1 to {ADVENTURE_PER_SUBJECT} points of an "
                "Adventure's Source Quality."
            )
    return found


#: Practice among native speakers is worth this until the language reaches
#: NATIVE_PRACTICE_UNTIL (DE p. 377).
NATIVE_PRACTICE_QUALITY, NATIVE_PRACTICE_UNTIL = 8, 5


def _practice_split_problems(
    character: Character, plan: SeasonPlan, chosen: Sequence[XpAllocation]
) -> list[str]:
    """Practice split between Abilities shares one Source Quality, the
    lowest of theirs; a language's 8 among native speakers lasts only
    until its score is 5 (DE p. 377)."""
    found: list[str] = []
    quality = source_quality(plan)
    if quality == NATIVE_PRACTICE_QUALITY:
        fluent = [
            name
            for kind, name in (_split(a.subject) for a in chosen)
            if kind == "ability"
            and "Language" in name
            and ability_level(character, name) >= NATIVE_PRACTICE_UNTIL
        ]
        if fluent:
            found.append(
                f"{', '.join(fluent)} is already {NATIVE_PRACTICE_UNTIL} or more: "
                f"practice among native speakers is worth {NATIVE_PRACTICE_QUALITY} "
                f"only below it, and {PRACTICE_QUALITY} after (DE p. 377)."
            )
    if len(chosen) > 1 and quality is not None:
        split = sum(a.points for a in chosen)
        if any(a.points < 1 for a in chosen):
            found.append("Give each subject at least 1 point of the Source Quality.")
        elif split != quality:
            found.append(
                f"Split all {quality} points of Source Quality (the lowest of the "
                f"subjects'): {split} are split (DE p. 377)."
            )
    return found


def _plain_outcome(
    saga: Saga | None,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: Outcome,
) -> None:
    months = _months(plan)
    kind = _STUDY_KIND[plan.activity]
    if plan.activity == ADVENTURE:
        # Its Virtues add to the season's Source Quality, already split.
        kind = study.SPLIT_ADVENTURE
    for allocation in allocations(plan):
        result.gains.append(
            _gain(
                character,
                allocation.subject,
                allocation.points,
                kind,
                months,
                year=plan.year,
            )
        )


def _handlers() -> dict[str, Handler]:
    """Every activity that gives experience, mapped to its family."""
    lab = _with_saga(
        _lab_problems, _lab_outcome, no_saga="Lab work needs the saga to be worked out."
    )
    families: list[tuple[Handler, Sequence[str]]] = [
        (lab, [key for key, a in ACTIVITIES.items() if a.lab]),
        (_with_saga(_book_problems, _book_outcome), book_seasons.SHEET_ACTIVITIES),
        (
            _with_saga(_apprentice_problems, _apprentice_outcome),
            tuple(apprentice_seasons.ACTIVITIES),
        ),
        (
            _with_saga(_tradition_problems, _tradition_outcome),
            (tradition_seasons.OPEN, *TRADITION_ACTIVITIES),
        ),
        (Handler(_integrate_problems, _integrate_outcome), (experiment.INTEGRATE,)),
        (
            _with_saga(_supplement_problems, _supplement_outcome),
            tuple(supplement_seasons.BY_KEY),
        ),
        (
            _with_saga(_assist_problems, _assist_outcome),
            (laboratory_seasons.ASSIST,),
        ),
        (
            _with_saga(_new_lab_problems, _new_lab_outcome),
            (laboratory_seasons.NEW,),
        ),
        (_with_saga(_study_family_problems, _study_outcome), STUDY_ACTIVITIES),
        (Handler(_plain_problems, _plain_outcome), (EXPOSURE, PRACTICE, ADVENTURE)),
    ]
    handlers: dict[str, Handler] = {}
    for handler, keys in families:
        for key in keys:
            assert key not in handlers, f"{key} is in two families"
            handlers[key] = handler
    return handlers


#: The family each activity that gives experience belongs to.
HANDLERS: dict[str, Handler] = _handlers()


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
