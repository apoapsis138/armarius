"""Lab work as a season (STORY-901): inventing a spell, from scratch or from
a Lab Text, in the magus's laboratory.

- The Lab Total is the spell's Technique + Form total (each Art at the
  lowest of it and its requisites), with the lab's "Spells" (or "Texts")
  Specialization, the magnitude of a similar spell the magus knows, and
  days away from the lab (0-10 nothing; 11-20 -10 to -30; more rules lab
  work out).
- Inventing: the Lab Total must be above the spell's level; each season
  adds Lab Total - level points, and the spell is invented when they reach
  its level (so in one season when the Lab Total is at least twice it).
- From a Lab Text: one season, if the Lab Total is at least the level.
- Every lab season gives Exposure (2 xp) in Magic Theory.

One-season lab work (STORY-907):

- Extracting vis: Creo Vim Lab Total / 10 pawns of Vim (rounded up), only
  in a Magic aura.
- Fixing an Arcane Connection: a season and 1 pawn of Vim; no Lab Total.
- A Longevity Ritual: the Creo Corpus Lab Total (+1 per extra pawn, halved
  for a subject with Difficult Longevity Ritual) / 5 is the aging-roll
  modifier (/ 10 for a mundane subject); 30+ to make one for someone else;
  vis = the subject's age / 5 (Creo, Corpus or Vim), within the vis limit.
  The subject spends the season with the magus.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .. import books
from .. import spells as spl
from ..models import (
    ArcaneConnection,
    Book,
    Character,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
)
from . import lab, spell_levels
from .breakdown import Line
from .casting import _lowest

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Inventing Spells "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Inventing_Spells)"
)
LAB_TEXT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Using Laboratory "
    "Texts (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Using_Laboratory_Texts)"
)

EXTRACT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Vis Extraction "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Vis_Extraction)"
)
FIX_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Fixing Arcane "
    "Connections (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Fixing_Arcane_Connections)"
)
LONGEVITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Longevity Rituals "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Longevity_Rituals)"
)

INVENT = "invent_spell"
LAB_TEXT = "lab_text_spell"
EXTRACT = "extract_vis"
FIX_AC = "fix_arcane_connection"
LONGEVITY = "longevity_ritual"
#: Being the subject of someone's Longevity Ritual (planned for the subject
#: when the ritual is scheduled; not lab work of their own).
LONGEVITY_SUBJECT = "longevity_subject"
LAB_ACTIVITIES: tuple[str, ...] = (INVENT, LAB_TEXT, EXTRACT, FIX_AC, LONGEVITY)
#: Lab work about a spell (the rest take one season and make no spell).
SPELL_ACTIVITIES: tuple[str, ...] = (INVENT, LAB_TEXT)
#: The lab_total activity (Specializations, Virtues) of each lab activity.
_TOTAL_ACTIVITY = {
    INVENT: "invent_spells",
    LAB_TEXT: "learn_from_lab_text",
    EXTRACT: "extract_vis",
    LONGEVITY: "longevity_ritual",
}
#: The Arts a Longevity Ritual's vis may be.
LONGEVITY_VIS_ARTS: tuple[str, ...] = ("Creo", "Corpus", "Vim")
#: A Longevity Ritual for someone else needs at least this Lab Total.
LONGEVITY_FOR_OTHERS = 30
DIFFICULT_LONGEVITY = "vf_difficult_longevity_ritual"


@dataclass
class LabWork:
    """What a season of lab work does: the Lab Total and, for inventing, the
    points before and after. One-season work without a spell (STORY-907)
    has `spell` None, level 0 and is finished; its results are below."""

    spell: Spell | None
    lab_total: lab.LabTotal
    level: int
    points_before: int = 0
    points_gained: int = 0
    finished: bool = False
    notes: list[str] = field(default_factory=list)
    #: Extracting vis: pawns of Vim gained.
    vis_gained: int = 0
    #: Vis paid for the work: Art -> pawns.
    vis_cost: dict[str, int] = field(default_factory=dict)
    #: A Longevity Ritual: its subject and aging-roll modifier.
    subject: Character | None = None
    longevity: int = 0

    @property
    def points_after(self) -> int:
        return self.points_before + self.points_gained


def laboratory(saga: Saga, magus: Character, plan: SeasonPlan) -> Laboratory | None:
    return saga.laboratory(plan.lab_id) if plan.lab_id else None


def the_spell(saga: Saga, plan: SeasonPlan) -> Spell | None:
    return spl.find_spell(saga, plan.spell_id)


def lab_text_of(saga: Saga, plan: SeasonPlan) -> Book | None:
    return next((b for b in saga.books if b.id == plan.book_id), None)


def lab_texts(saga: Saga, magus: Character) -> list[Book]:
    """The Lab Texts `magus` may work from: readable (their covenant's
    library, their own, their laboratory's) and naming a spell they don't
    know yet."""
    known = {k.spell_id for k in magus.spells_known}
    return [
        b
        for b in saga.books
        if b.type == "Lab Text"
        and b.spell_id
        and b.spell_id not in known
        and books.can_read(saga, magus, b)
    ]


def project_points(saga: Saga, magus: Character, spell_id: str | None) -> int:
    return next(
        (
            p.points
            for p in saga.lab_projects
            if p.character_id == magus.id and p.spell_id == spell_id
        ),
        0,
    )


def design_level(design: SpellDesign) -> int | None:
    """A design's level: worked out from its base level and parameters, or
    as printed when it was started from a spell with no base level."""
    if design.base_level is not None:
        worked = spell_levels.spell_level(
            design.base_level,
            design.range,
            design.duration,
            design.target,
            extra_magnitudes=design.extra_magnitudes,
            ritual=design.ritual,
            custom_steps=design.custom_steps,
        )
        return worked.level if worked is not None else None
    return design.printed_level


def design_spell(design: SpellDesign) -> Spell:
    """The spell a design describes (not yet in the saga: it's added when
    invented)."""
    return Spell(
        id=f"design:{design.key}",
        name=design.name or "(unnamed spell)",
        technique=design.technique,
        form=design.form,
        level=design_level(design),
        description=design.description,
        requisites=list(design.requisites),
        range=design.range,
        duration=design.duration,
        target=design.target,
        ritual=design.ritual,
        base_level=design.base_level,
    )


def requisite_arts(magus: Character, spell: Spell) -> tuple[str, str]:
    """The Technique and Form a spell's Lab Total uses: each the lowest of
    the Art and its requisites of the same kind."""
    technique, _ = _lowest(magus, spell.technique, spell.requisites)
    form, _ = _lowest(magus, spell.form, spell.requisites)
    return technique, form


def work(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], LabWork | None]:
    """The problems with a lab plan, or what it does."""
    lab_ = laboratory(saga, magus, plan)
    if lab_ is None:
        return ["Lab work needs a laboratory."], None
    if lab_.owner_id != magus.id:
        return [f"{magus.name} doesn't work in {lab_.name}."], None
    if plan.activity not in SPELL_ACTIVITIES:
        return _one_season_work(saga, magus, plan, lab_)
    if plan.activity == LAB_TEXT:
        text = lab_text_of(saga, plan)
        if text is None:
            return ["Choose the Lab Text to work from."], None
        if not books.can_read(saga, magus, text):
            return [f"{magus.name} can't get at {text.name}."], None
        spell = spl.find_spell(saga, text.spell_id)
        if spell is None:
            return [f"{text.name} doesn't record a spell."], None
    elif plan.design is not None:
        design = plan.design
        if not design.name.strip():
            return ["Name the spell."], None
        if not design.technique or not design.form:
            return ["Choose the spell's Technique and Form."], None
        spell = design_spell(design)
        if spell.level is None:
            return [
                "Give the spell a base level (its level is worked out from it "
                "and the Range, Duration and Target)."
            ], None
    else:
        spell = the_spell(saga, plan)
        if spell is None:
            return ["Choose the spell to invent."], None
        if spell.level is None:
            return [f"{spell.name} is a General spell: choose its level."], None
    if any(k.spell_id == spell.id for k in magus.spells_known):
        return [f"{magus.name} already knows {spell.name}."], None
    similar = spl.find_spell(saga, plan.similar_spell_id)
    if similar is not None and not any(
        k.spell_id == similar.id for k in magus.spells_known
    ):
        similar = None
    technique, form = requisite_arts(magus, spell)
    total = lab.lab_total(
        saga,
        magus,
        technique,
        form,
        lab_,
        activity=_TOTAL_ACTIVITY[plan.activity],
        days_missed=max(0, plan.days_away),
        similar_spell_level=(
            similar.level if similar is not None and plan.activity == INVENT else None
        ),
    )
    total = _with_options(magus, plan, technique, form, total)
    if lab.distraction_penalty(max(0, plan.days_away)) is None:
        return [
            f"{plan.days_away} days away from the laboratory: no lab work is "
            "possible this season (more than 20)."
        ], None
    level = spell.level
    if level is None:
        return [f"{spell.name} has no level."], None
    lab_total = int(total.total)
    result = LabWork(spell, total, level)
    if plan.activity == LAB_TEXT:
        if lab_total < level:
            return [
                f"Lab Total {lab_total} is below {spell.name}'s level "
                f"{level}: the Lab Text can't be used yet."
            ], None
        result.finished = True
        return [], result
    if lab_total <= level:
        return [
            f"Lab Total {lab_total} isn't above {spell.name}'s level "
            f"{level}: it can't be invented yet."
        ], None
    result.points_before = project_points(saga, magus, spell.id)
    result.points_gained = lab.points_per_season(lab_total, level)
    result.finished = result.points_after >= level
    return [], result


def vis_pool(saga: Saga, magus: Character, plan: SeasonPlan) -> dict[str, int]:
    """The raw vis a lab plan pays with (or extracted vis goes to): the
    laboratory's or the magus's own."""
    if plan.vis_from == "laboratory":
        lab_ = saga.laboratory(plan.lab_id) if plan.lab_id else None
        return lab_.raw_vis if lab_ is not None else {}
    return magus.raw_vis


def _whose_vis(magus: Character, plan: SeasonPlan) -> str:
    return "the laboratory's" if plan.vis_from == "laboratory" else f"{magus.name}'s"


def connection_of(saga: Saga, plan: SeasonPlan) -> ArcaneConnection | None:
    """The laboratory's Arcane Connection a plan fixes."""
    lab_ = saga.laboratory(plan.lab_id) if plan.lab_id else None
    if lab_ is None or not plan.connection_id:
        return None
    return next(
        (c for c in lab_.arcane_connections if c.id == plan.connection_id), None
    )


def subject_of(saga: Saga, magus: Character, plan: SeasonPlan) -> Character | None:
    """A Longevity Ritual's subject: the magus unless someone else is named."""
    if plan.subject_id and plan.subject_id != magus.id:
        return saga.character(plan.subject_id)
    return magus


def is_mundane(character: Character) -> bool:
    """Whether a Longevity Ritual works at half strength for `character`:
    neither a magus nor someone with a Supernatural Ability."""
    if character.type == "magus":
        return False
    return not any(a.category == "Supernatural" for a in character.abilities)


def age_of(saga: Saga, character: Character) -> int | None:
    born = character.background.year_born
    return None if born is None else saga.current_year - born


def longevity_vis(age: int) -> int:
    """Pawns a Longevity Ritual takes: the subject's age / 5, rounded up."""
    return max(0, -(-age // 5))


def _one_season_work(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> tuple[list[str], LabWork | None]:
    """Extracting vis, fixing an Arcane Connection or a Longevity Ritual."""
    days = max(0, plan.days_away)
    if lab.distraction_penalty(days) is None:
        return [
            f"{plan.days_away} days away from the laboratory: no lab work is "
            "possible this season (more than 20)."
        ], None
    pool = vis_pool(saga, magus, plan)
    if plan.activity == FIX_AC:
        connection = connection_of(saga, plan)
        if connection is None:
            return [
                "Choose the Arcane Connection to fix (they're kept on the "
                "laboratory's Inventory tab)."
            ], None
        if connection.fixed:
            return [f"The Arcane Connection to {connection.to} is already fixed."], None
        if pool.get("vim", 0) < 1:
            return [
                f"Fixing an Arcane Connection takes 1 pawn of Vim vis; "
                f"{_whose_vis(magus, plan)} raw vis has none."
            ], None
        total = lab.LabTotal(total=0, lines=[])
        return [], LabWork(None, total, 0, finished=True, vis_cost={"Vim": 1})
    if plan.activity == EXTRACT:
        covenant = saga.covenant(lab_.covenant_id)
        realm = covenant.aura_realm if covenant is not None else "Magic"
        if realm != "Magic":
            return [
                f"Vis is extracted only in a Magic aura; {lab_.name}'s is {realm}."
            ], None
        total = lab.lab_total(
            saga,
            magus,
            "Creo",
            "Vim",
            lab_,
            activity=_TOTAL_ACTIVITY[EXTRACT],
            days_missed=days,
        )
        total = _with_options(magus, plan, "Creo", "Vim", total)
        pawns = lab.vis_extracted(max(0, int(total.total)))
        return [], LabWork(None, total, 0, finished=True, vis_gained=pawns)
    # A Longevity Ritual.
    subject = subject_of(saga, magus, plan)
    if subject is None:
        return ["Choose who the Longevity Ritual is for."], None
    if subject is not magus:
        busy = next(
            (
                p
                for p in saga.season_plans
                if p.character_id == subject.id
                and (p.season, p.year) == (plan.season, plan.year)
                and not (p.activity == LONGEVITY_SUBJECT and p.subject_id == magus.id)
            ),
            None,
        )
        if busy is not None:
            return [
                f"{subject.name} has other plans for {plan.season} {plan.year}: "
                "the subject spends the season with the magus."
            ], None
    age = age_of(saga, subject)
    if age is None:
        return [f"Set {subject.name}'s Year Born: the ritual's vis is by age."], None
    if plan.vis_art not in LONGEVITY_VIS_ARTS:
        return ["Choose the vis to pay with: Creo, Corpus or Vim."], None
    if plan.extra_vis < 0:
        return ["Extra vis can't be negative."], None
    total = lab.lab_total(
        saga,
        magus,
        "Creo",
        "Corpus",
        lab_,
        activity=_TOTAL_ACTIVITY[LONGEVITY],
        days_missed=days,
    )
    total = _with_options(magus, plan, "Creo", "Corpus", total)
    extra: list[Line] = []
    if plan.extra_vis:
        extra.append(Line("Extra vis", amount=plan.extra_vis, source=LONGEVITY_SOURCE))
    if extra:
        total = replace(
            total,
            total=total.total + plan.extra_vis,
            lines=[*total.lines, *extra],
        )
    if any(vf.vf_id == DIFFICULT_LONGEVITY for vf in subject.virtues_flaws):
        halved = int(total.total) // 2
        total = replace(
            total,
            total=halved,
            lines=[
                *total.lines,
                Line(
                    f"Difficult Longevity Ritual ({subject.name}): halved",
                    multiplier=0.5,
                    source=LONGEVITY_SOURCE,
                ),
            ],
        )
    lab_total = int(total.total)
    if subject is not magus and lab_total < LONGEVITY_FOR_OTHERS:
        return [
            f"Lab Total {lab_total}: a Longevity Ritual for someone else needs "
            f"{LONGEVITY_FOR_OTHERS}."
        ], None
    pawns = longevity_vis(age) + plan.extra_vis
    limit = lab.vis_limit(magus)
    if pawns > limit:
        return [
            f"The ritual takes {pawns} pawns of vis; {magus.name} can handle "
            f"{limit} in a season (twice Magic Theory)."
        ], None
    held = pool.get(plan.vis_art.lower(), 0)
    if held < pawns:
        return [
            f"The ritual takes {pawns} pawns of {plan.vis_art} vis; "
            f"{_whose_vis(magus, plan)} raw vis has {held}."
        ], None
    result = LabWork(
        None,
        total,
        0,
        finished=True,
        vis_cost={plan.vis_art: pawns},
        subject=subject,
        longevity=lab.longevity_modifier(
            max(0, lab_total), mundane=is_mundane(subject)
        ),
    )
    return [], result


FOCUS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Major "
    "Magical Focus (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Four:_Virtues_and_Flaws#Major_Magical_Focus)"
)


def has_focus(magus: Character) -> bool:
    """Whether the magus has a Magical Focus (Major or Minor)."""
    return any("magical_focus" in vf.vf_id for vf in magus.virtues_flaws)


def theory_specialty(magus: Character) -> str:
    """The magus's Magic Theory Specialty ("" without one)."""
    ability = next((a for a in magus.abilities if a.name == "Magic Theory"), None)
    return (ability.specialty or "") if ability else ""


def _with_options(
    magus: Character, plan: SeasonPlan, technique: str, form: str, total: lab.LabTotal
) -> lab.LabTotal:
    """The Lab Total with the plan's options: a Magical Focus counts the
    lower Art twice, a Magic Theory Specialty that applies adds 1, and any
    other modifier the troupe allows."""
    extra: list[Line] = []
    if plan.focus and has_focus(magus):
        lower = min(
            sum(lab.art_score(magus, technique)), sum(lab.art_score(magus, form))
        )
        extra.append(
            Line("Magical Focus (lower Art again)", amount=lower, source=FOCUS_SOURCE)
        )
    if plan.theory_specialty and theory_specialty(magus):
        extra.append(
            Line(
                f"Magic Theory Specialty ({theory_specialty(magus)})",
                amount=1,
                source=lab.SOURCE,
            )
        )
    if plan.other_modifier:
        extra.append(Line("Other", amount=plan.other_modifier, source=""))
    if not extra:
        return total
    return replace(
        total,
        total=total.total + sum(line.amount or 0 for line in extra),
        lines=[*total.lines, *extra],
    )


def seasons_left(work_: LabWork) -> int:
    """Seasons still needed after this one (0 when this one finishes it)."""
    if work_.finished or not work_.points_gained:
        return 0
    remaining = work_.level - work_.points_after
    return -(-remaining // work_.points_gained)
