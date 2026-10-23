"""Lab work as a season: inventing a spell, from scratch or from
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

One-season lab work:

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

from collections.abc import MutableMapping
from dataclasses import dataclass, field, replace

from .. import catalog, vis
from ..models import (
    SUPERNATURAL_CATEGORIES,
    TEXT_LONGEVITY,
    ArcaneConnection,
    BondPower,
    Book,
    Character,
    EnchantedDevice,
    ExperimentalEffect,
    Familiar,
    InstilledEffect,
    Laboratory,
    Saga,
    SeasonPlan,
    Spell,
    SpellDesign,
)
from . import (
    book_seasons,
    enchant_seasons,
    enchantment,
    experiment,
    familiar_seasons,
    lab,
    lab_virtues,
    laboratory_seasons,
    library,
    sites,
    spell_levels,
)
from .breakdown import Line
from .casting import _lowest
from .rounding import round_down, round_up

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

TAMING = "hermetic_taming"
TAMING_SOURCE = (
    "Realms of Power: Magic, Chapter Five: Magic Animals, Taming Animals "
    "(https://www.redcap.org/page/Realms_of_Power:_Magic_Chapter_Five:"
    "_Magic_Animals#Taming_Animals)"
)
INVENT = "invent_spell"
LAB_TEXT = "lab_text_spell"
EXTRACT = "extract_vis"
FIX_AC = "fix_arcane_connection"
LONGEVITY = "longevity_ritual"
#: Being the subject of someone's Longevity Ritual (planned for the subject
#: when the ritual is scheduled; not lab work of their own).
LONGEVITY_SUBJECT = "longevity_subject"
LAB_ACTIVITIES: tuple[str, ...] = (
    INVENT,
    LAB_TEXT,
    EXTRACT,
    FIX_AC,
    LONGEVITY,
    *enchant_seasons.ACTIVITIES,
    book_seasons.DECODE_TEXT,
    TAMING,
    experiment.STABILIZE,
    *laboratory_seasons.ACTIVITIES,
    *familiar_seasons.ACTIVITIES,
)
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
DIFFICULT_LONGEVITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Four: Virtues and Flaws, Difficult "
    "Longevity Ritual (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Four:_Virtues_and_Flaws#Difficult_Longevity_Ritual)"
)


@dataclass
class LabWork:
    """What a season of lab work does: the Lab Total and, for inventing, the
    points before and after. One-season work without a spell
    has `spell` None, level 0 and is finished; its results are below."""

    spell: Spell | None
    lab_total: lab.LabTotal
    level: int
    points_before: int = 0
    points_gained: int = 0
    finished: bool = False
    notes: list[str] = field(default_factory=list)
    #: Extracting vis: pawns gained, and of which Art (Vim, or a Form
    #: with Hermetic Alchemy or an Extractor Virtue).
    vis_gained: int = 0
    vis_gained_art: str = "Vim"
    #: Waster of Vis: the pawns wasted on top of vis_cost (Art -> pawns).
    vis_wasted: dict[str, int] = field(default_factory=dict)
    #: Vis paid for the work: Art -> pawns.
    vis_cost: dict[str, int] = field(default_factory=dict)
    #: A Longevity Ritual: its subject and aging-roll modifier.
    subject: Character | None = None
    longevity: int = 0
    #: Enchanting: the device and effect worked on, a charged
    #: item's charges, and the effects an investigation found.
    device: EnchantedDevice | None = None
    effect: InstilledEffect | None = None
    charges: int = 0
    revealed: list[str] = field(default_factory=list)
    #: Familiar work: the familiar, and the bond power instilled.
    familiar: Familiar | None = None
    power: BondPower | None = None
    #: Decoding: (reader id, the author's key -- see
    #: book_seasons.author_key --, level) readable when done.
    access: tuple[str, str, int] | None = None
    #: Work on the laboratory: setting up its second season, the
    #: Refinement it will have (and had), and the Virtues/Flaws the season's
    #: roll gains or loses.
    second_season: bool = False
    refinement: int = 0
    old_refinement: int = 0
    gains_vf: list[str] = field(default_factory=list)
    loses_vf: list[str] = field(default_factory=list)
    #: Stabilizing: the Discovery's magnitude.
    research_magnitude: int = 0
    #: Experimental effects an invention carries to its spell.
    carried_effects: list[ExperimentalEffect] = field(default_factory=list)
    research_warping: int = 0
    #: Experimenting: the season's Extraordinary Results.
    experiment: experiment.Extraordinary | None = None
    #: Experimenting with a Lab Total too low for the work: why. The
    #: season makes no progress, but the chart is still rolled and any vis
    #: paid is lost.
    too_low: str = ""

    @property
    def points_after(self) -> int:
        return self.points_before + self.points_gained


def laboratory(saga: Saga, magus: Character, plan: SeasonPlan) -> Laboratory | None:
    return saga.laboratory(plan.lab_id) if plan.lab_id else None


def the_spell(saga: Saga, plan: SeasonPlan) -> Spell | None:
    return catalog.find_spell(saga, plan.spell_id)


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
        and library.can_read(saga, magus, b)
        and book_seasons.can_use_lab_text(magus, b)
    ]


def lab_texts_at_hand(saga: Saga, magus: Character) -> list[Book]:
    """Every spell's Lab Text `magus` can get at and doesn't know the spell
    of -- readable or not (a picker shows them all, tagging the ones to
    decode first)."""
    known = {k.spell_id for k in magus.spells_known}
    return [
        b
        for b in saga.books
        if b.type == "Lab Text"
        and b.spell_id
        and b.spell_id not in known
        and library.can_read(saga, magus, b)
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


def same_spell(a: Spell, b: Spell) -> bool:
    """Whether two spells are the same spell: name, Arts, level and
    parameters (one left blank is a design's first step)."""
    fields_ = ("name", "technique", "form", "level")
    steps = {"range": "Personal", "duration": "Momentary", "target": "Individual"}
    return (
        all(getattr(a, f) == getattr(b, f) for f in fields_)
        and all(
            (getattr(a, f) or first) == (getattr(b, f) or first)
            for f, first in steps.items()
        )
        and sorted(a.requisites) == sorted(b.requisites)
    )


def requisite_arts(magus: Character, spell: Spell) -> tuple[str, str]:
    """The Technique and Form a spell's Lab Total uses: each the lowest of
    the Art and its requisites of the same kind."""
    technique, _ = _lowest(magus, spell.technique, spell.requisites)
    form, _ = _lowest(magus, spell.form, spell.requisites)
    return technique, form


def _chosen_spell(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], Spell | None]:
    """The spell a season of inventing or working from a Lab Text is
    for, or what stops it being chosen."""
    if plan.activity == LAB_TEXT:
        text = lab_text_of(saga, plan)
        if text is None:
            return ["Choose the Lab Text to work from."], None
        if not library.can_read(saga, magus, text):
            return [f"{magus.name} can't get at {text.name}."], None
        if not book_seasons.can_use_lab_text(magus, text):
            return [
                f"{text.name} is {book_seasons.author_name(saga, text)}'s raw "
                "text: decode it first (or have it rewritten for general use)."
            ], None
        spell = catalog.find_spell(saga, text.spell_id)
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
    return [], spell


def work(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], LabWork | None]:
    """The problems with a lab plan, or what it does."""
    found, made = _work(saga, magus, plan)
    if made is not None and made.vis_cost:
        why = _waste(saga, magus, plan, made)
        if why:
            return [why], None
    if made is not None and seeking(plan):
        goal = experiment.find_goal(magus, plan.research)
        name = made_name(made)
        if goal is not None and name and name in goal.discovered_from:
            return [
                f"{name.title()} already gave a Discovery toward {goal.name}: "
                "seek another with a different spell or enchantment."
            ], None
    return found, made


def _work(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], LabWork | None]:
    lab_ = laboratory(saga, magus, plan)
    if lab_ is None:
        if plan.activity == laboratory_seasons.TAKE_OVER:
            return ["Choose the laboratory to take over."], None
        return ["Lab work needs a laboratory."], None
    taking = plan.activity == laboratory_seasons.TAKE_OVER and (
        laboratory_seasons.vacant(saga, lab_)
    )
    if lab_.owner_id != magus.id and not taking:
        if plan.activity == laboratory_seasons.TAKE_OVER:
            owner = saga.character(lab_.owner_id)
            who = owner.name if owner else "someone"
            return [
                f"{lab_.name} is {who}'s laboratory: only one with no owner "
                "can be taken over."
            ], None
        return [f"{magus.name} doesn't work in {lab_.name}."], None
    vf_ids = {vf.vf_id for vf in magus.virtues_flaws}
    if plan.experimenting:
        if plan.activity not in EXPERIMENTAL:
            return ["This lab work can't be done experimenting."], None
        if experiment.AVERSE in vf_ids:
            return [f"{magus.name} is Averse to Risk: no experimenting."], None
        # Seeking a Discovery limits the risk by Magic Theory; otherwise 0-3.
        most = (
            experiment.max_risk(laboratory_seasons.magic_theory(magus))
            if seeking(plan)
            else experiment.MAX_RISK
        )
        if not 0 <= plan.risk <= most:
            return [
                f"The risk modifier is 0 to +{most}"
                + (" (by Magic Theory, seeking a Discovery)." if seeking(plan) else ".")
            ], None
    elif plan.activity in EXPERIMENTAL and experiment.PRONE in vf_ids:
        return [
            f"{magus.name} is Prone to Chance: this lab work must be experimental."
        ], None
    if plan.activity == experiment.STABILIZE:
        return _stabilize(saga, magus, plan)
    if plan.activity == TAMING:
        return _taming(saga, magus, plan, lab_)
    if plan.activity in laboratory_seasons.ACTIVITIES:
        return laboratory_seasons.work(saga, magus, plan, lab_)

    def options(
        m: Character, p: SeasonPlan, technique: str, form: str, total: lab.LabTotal
    ):
        return _with_options(m, p, technique, form, total, saga)

    if plan.activity in enchant_seasons.ACTIVITIES:
        return enchant_seasons.work(saga, magus, plan, lab_, options)
    if plan.activity in familiar_seasons.ACTIVITIES:
        return familiar_seasons.work(saga, magus, plan, lab_, options)
    if plan.activity == book_seasons.DECODE_TEXT:
        return _decode(saga, magus, plan, lab_)
    if plan.activity not in SPELL_ACTIVITIES:
        return _one_season_work(saga, magus, plan, lab_)
    found, spell = _chosen_spell(saga, magus, plan)
    if spell is None:
        return found, None
    if any(k.spell_id == spell.id for k in magus.spells_known):
        return [f"{magus.name} already knows {spell.name}."], None
    source = catalog.find_spell(
        saga, plan.design.source_spell_id if plan.design else None
    )
    if (
        source is not None
        and any(k.spell_id == source.id for k in magus.spells_known)
        and same_spell(source, spell)
    ):
        return [
            f"{magus.name} already knows {source.name}: change the design "
            "to invent a variant of it."
        ], None
    similar = catalog.find_spell(saga, plan.similar_spell_id)
    # Disjointed Magic: no benefit from a similar spell known.
    if similar is not None and (
        not any(k.spell_id == similar.id for k in magus.spells_known)
        or lab_virtues.has(magus, lab_virtues.DISJOINTED)
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
        experimenting=plan.experimenting,
        similar_spell_level=(
            similar.level if similar is not None and plan.activity == INVENT else None
        ),
    )
    total = _with_options(magus, plan, technique, form, total, saga)
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
        why = (
            f"Lab Total {lab_total} isn't above {spell.name}'s level "
            f"{level}: it can't be invented yet"
        )
        if not plan.experimenting:
            return [f"{why}."], None
        result.points_before = project_points(saga, magus, spell.id)
        result.too_low = experiment.too_low(why)
        return [], result
    result.points_before = project_points(saga, magus, spell.id)
    result.points_gained = lab.points_per_season(lab_total, level)
    result.finished = result.points_after >= level
    return [], result


def vis_spent(work_: LabWork) -> dict[str, int]:
    """The pawns a season's work takes from the pool: its cost and any
    Waster of Vis wastes."""
    spent = dict(work_.vis_cost)
    for art, pawns in work_.vis_wasted.items():
        spent[art] = spent.get(art, 0) + pawns
    return spent


def _waste(saga: Saga, magus: Character, plan: SeasonPlan, made: LabWork) -> str:
    """Waster of Vis: the pawns it wastes, noted on the work; why the
    season can't be done when the pool or the magus's limit can't take
    them ("" when it can)."""
    made.vis_wasted = lab_virtues.wasted(magus, made.vis_cost)
    if not made.vis_wasted:
        return ""
    spent = vis_spent(made)
    limit = lab.vis_limit(magus)
    if sum(spent.values()) > limit:
        return (
            f"Waster of Vis: the work takes {sum(spent.values())} pawns with "
            f"those wasted; {magus.name} can handle {limit} in a season."
        )
    pool = vis_pool(saga, magus, plan)
    for art, pawns in spent.items():
        if pool.get(art.lower(), 0) < pawns:
            return (
                f"Waster of Vis: the work takes {pawns} pawns of {art} with "
                f"those wasted; {whose_vis(magus, plan)} raw vis has "
                f"{pool.get(art.lower(), 0)}."
            )
    return ""


def waste_note(work_: LabWork) -> str:
    """ "Waster of Vis: 1 pawn(s) of Vim wasted." ("" for none)."""
    if not work_.vis_wasted:
        return ""
    return (
        "Waster of Vis: "
        + ", ".join(f"{n} pawn(s) of {art}" for art, n in work_.vis_wasted.items())
        + " wasted."
    )


def vis_pool(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> MutableMapping[str, int]:
    """The raw vis a lab plan pays with (or extracted vis goes to): the
    laboratory's, the magus's own, or the vis stores of the laboratory's
    covenant (the magus's, for a lab with none)."""
    lab_ = saga.laboratory(plan.lab_id) if plan.lab_id else None
    if plan.vis_from == "laboratory":
        return lab_.raw_vis if lab_ is not None else {}
    if plan.vis_from == "covenant":
        covenant_id = (lab_.covenant_id if lab_ is not None else None) or (
            magus.covenant_id
        )
        return vis.covenant_pool(saga, covenant_id, magus.name)
    return magus.raw_vis


def whose_vis(magus: Character, plan: SeasonPlan) -> str:
    if plan.vis_from == "covenant":
        return "the covenant's"
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
    return not any(a.category in SUPERNATURAL_CATEGORIES for a in character.abilities)


def age_of(saga: Saga, character: Character) -> int | None:
    born = character.background.year_born
    return None if born is None else saga.current_year - born


def longevity_vis(age: int) -> int:
    """Pawns a Longevity Ritual takes: the subject's age / 5, rounded up."""
    return max(0, round_up(age / 5))


def _extraction(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory, days: int
) -> tuple[list[str], LabWork | None]:
    """Extracting vis in a Magic aura: Vim, or a Form's with Hermetic
    Alchemy or its Extractor Virtue."""
    form = plan.extract_form
    if form and form not in lab_virtues.extraction_forms(magus):
        return [
            f"{magus.name} extracts only Vim vis: Form vis needs Hermetic "
            f"Alchemy or Extractor of {form} Vis."
        ], None
    # Form vis: the Creo Vim total with the Form as a requisite.
    art = "Vim"
    if form and sum(lab.art_score(magus, form)) < sum(lab.art_score(magus, "Vim")):
        art = form
    total = lab.lab_total(
        saga,
        magus,
        "Creo",
        art,
        lab_,
        activity=_TOTAL_ACTIVITY[EXTRACT],
        days_missed=days,
        experimenting=plan.experimenting,
    )
    if lab_virtues.has(magus, lab_virtues.ALCHEMY) and plan.shape_bonus > 0:
        capped = min(plan.shape_bonus, lab.shape_material_cap(magus))
        total = replace(
            total,
            total=total.total + capped,
            lines=[
                *total.lines,
                Line(
                    "Shape and material (Hermetic Alchemy)",
                    amount=capped,
                    source=lab_virtues.ALCHEMY_SOURCE,
                ),
            ],
        )
    total = _with_options(magus, plan, "Creo", art, total, saga)
    lab_total = max(0, int(total.total))
    if form:
        divisor = lab_virtues.form_extraction_divisor(magus, form)
        pawns = max(1, round_up(lab_total / divisor))
    else:
        pawns = lab.vis_extracted(lab_total)
    return [], LabWork(
        None,
        total,
        0,
        finished=True,
        vis_gained=pawns,
        vis_gained_art=form or "Vim",
    )


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
                f"{whose_vis(magus, plan)} raw vis has none."
            ], None
        total = lab.LabTotal(total=0, lines=[])
        return [], LabWork(None, total, 0, finished=True, vis_cost={"Vim": 1})
    if plan.activity == EXTRACT:
        covenant = saga.covenant(lab_.covenant_id)
        realm = covenant.aura_realm if covenant is not None else "Magic"

        own = sites.lab_aura(saga, lab_)
        if own is not None:
            realm = own[1]
        if realm != "Magic":
            return [
                f"Vis is extracted only in a Magic aura; {lab_.name}'s is {realm}."
            ], None
        return _extraction(saga, magus, plan, lab_, days)
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
        experimenting=plan.experimenting,
    )
    total = _with_options(magus, plan, "Creo", "Corpus", total, saga)
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
        # Halves the Lab Total; no rounding stated, so down (rounding.py).
        halved = round_down(int(total.total) / 2)
        total = replace(
            total,
            total=halved,
            lines=[
                *total.lines,
                Line(
                    f"Difficult Longevity Ritual ({subject.name}): halved",
                    multiplier=0.5,
                    source=DIFFICULT_LONGEVITY_SOURCE,
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
            f"{whose_vis(magus, plan)} raw vis has {held}."
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


@dataclass(frozen=True)
class RitualAgain:
    """A Longevity Ritual performed again from its Lab Text:
    who it is for, the aging-roll modifier it restores, and the vis."""

    subject: Character
    modifier: int
    pawns: int


def ritual_subject(saga: Saga, text: Book) -> Character | None:
    """The character a Longevity Ritual's text was written for."""
    return next((c for c in saga.characters if c.name == text.ritual_subject), None)


def ritual_again(
    saga: Saga,
    magus: Character,
    lab_: Laboratory,
    text: Book,
    vis_art: str,
    vis_from: str,
) -> tuple[list[str], RitualAgain | None]:
    """Performing a Longevity Ritual again from its Lab Text: no season,
    only the vis (the subject's age / 5 pawns, and the extra vis it was
    first made with, which must be spent every time). It is the same
    ritual, for the same subject, at the Lab Total it was made with (the
    text's level)."""
    if text.type != "Lab Text" or text.text_kind != TEXT_LONGEVITY:
        return [f"{text.name} isn't the Lab Text of a Longevity Ritual."], None
    if not library.can_read(saga, magus, text) and not lab_virtues.remembers(
        magus, text
    ):
        return [f"{magus.name} can't get at {text.name}."], None
    if not book_seasons.can_use_lab_text(magus, text):
        return [
            f"{text.name} is {book_seasons.author_name(saga, text)}'s raw text: "
            "decode it first (or have it rewritten for general use)."
        ], None
    subject = ritual_subject(saga, text)
    if subject is None:
        named = text.ritual_subject or "no one"
        return [
            f"{text.name} is for {named}, who isn't a character of this saga: "
            "a ritual is made for one person."
        ], None
    age = age_of(saga, subject)
    if age is None:
        return [f"Set {subject.name}'s Year Born: the ritual's vis is by age."], None
    if vis_art not in LONGEVITY_VIS_ARTS:
        return ["Choose the vis to pay with: Creo, Corpus or Vim."], None
    pawns = longevity_vis(age) + max(0, text.ritual_extra_vis)
    limit = lab.vis_limit(magus)
    if pawns > limit:
        return [
            f"The ritual takes {pawns} pawns of vis; {magus.name} can handle "
            f"{limit} at once (twice Magic Theory)."
        ], None
    plan = SeasonPlan(
        magus.id,
        saga.current_year,
        saga.current_season,
        LONGEVITY,
        lab_id=lab_.id,
        vis_from=vis_from,
    )
    held = vis_pool(saga, magus, plan).get(vis_art.lower(), 0)
    if held < pawns:
        return [
            f"The ritual takes {pawns} pawns of {vis_art} vis; "
            f"{whose_vis(magus, plan)} raw vis has {held}."
        ], None
    modifier = lab.longevity_modifier(
        max(0, book_seasons.text_level(text, saga)), mundane=is_mundane(subject)
    )
    return [], RitualAgain(subject, modifier, pawns)


def made_name(work_: LabWork) -> str:
    """The lower-case name of the spell or enchantment a lab work makes
    ("" for other work): what a Discovery is recorded against."""
    made = work_.spell or work_.effect
    return (getattr(made, "name", "") or "").strip().lower()


def made_arts(work_: LabWork, plan: SeasonPlan) -> tuple[str, str]:
    """The Technique and Form a lab work uses: its spell's, effect's or
    power's, Creo Corpus for a Longevity Ritual, else the plan's (Vim
    when none is named). A Discovery's experience goes to one of them."""
    made = work_.spell or work_.effect or work_.power
    technique = getattr(made, "technique", "") or ""
    form = getattr(made, "form", "") or ""
    if not (technique and form) and plan.activity == LONGEVITY:
        return "Creo", "Corpus"
    return (
        technique or plan.technique or "Vim",
        form or plan.form or "Vim",
    )


def seeking(plan: SeasonPlan) -> bool:
    """Whether an experiment seeks a Discovery (it names a research goal)."""
    return plan.experimenting and bool(plan.research.strip())


def _stabilize(
    saga: Saga, magus: Character, plan: SeasonPlan
) -> tuple[list[str], LabWork | None]:
    """Stabilizing a Discovery: the experiment that made it, repeated
    exactly: its seasons, Lab Total, risk and vis (in the first season)."""
    found = experiment.find_goal(magus, plan.research)
    if found is None or not found.pending_magnitude:
        return ["Choose a research goal with a Discovery to stabilize."], None
    if found.retry_season and (plan.season, plan.year) != (
        found.retry_season,
        found.retry_year,
    ):
        return [
            "A failed stabilization must be tried again the next season "
            f"({found.retry_season} {found.retry_year}); later, the Discovery "
            "is lost."
        ], None
    cost: dict[str, int] = {}
    if not found.stabilizing_seasons and found.discovery_vis:
        art = found.discovery_vis_art or "Vim"
        held = vis_pool(saga, magus, plan).get(art.lower(), 0)
        if held < found.discovery_vis:
            return [
                f"The experiment takes {found.discovery_vis} pawns of {art} vis; "
                f"{whose_vis(magus, plan)} raw vis has {held}."
            ], None
        cost = {art: found.discovery_vis}
    total = lab.LabTotal(
        total=found.discovery_lab_total,
        lines=[
            Line(
                "The Discovery's experiment, repeated",
                amount=found.discovery_lab_total,
                source=experiment.RESEARCH_SOURCE,
            )
        ],
    )
    seasons_ = max(1, found.discovery_seasons)
    work_ = LabWork(
        None,
        total,
        seasons_,
        points_before=found.stabilizing_seasons,
        points_gained=1,
        finished=found.stabilizing_seasons + 1 >= seasons_,
        vis_cost=cost,
    )
    work_.research_magnitude = found.pending_magnitude
    return [], work_


def _taming(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> tuple[list[str], LabWork | None]:
    """Hermetic taming (Realms of Power: Magic): the creature housed in the
    lab; Rego + its Form Lab Total (+ Animal Handling + Animal Ken) - its
    Might each season, until the points reach its Might."""
    if not plan.title.strip():
        return ["Name the creature."], None
    if not plan.form:
        return ["Choose the creature's Form."], None
    might = plan.book_level or 0
    if might <= 0:
        return ["Type the creature's Might."], None
    total = lab.lab_total(
        saga,
        magus,
        "Rego",
        plan.form,
        lab_,
        days_missed=max(0, plan.days_away),
        experimenting=plan.experimenting,
    )
    extra = [
        Line(name, amount=score, source=TAMING_SOURCE)
        for name in ("Animal Handling", "Animal Ken")
        if (score := sum(lab.ability_score(magus, name)))
    ]
    if extra:
        total = replace(
            total,
            total=total.total + sum(line.amount or 0 for line in extra),
            lines=[*total.lines, *extra],
        )
    total = _with_options(magus, plan, "Rego", plan.form, total, saga)
    gained = int(total.total) - might
    if gained <= 0:
        return [
            f"Lab Total {int(total.total)} isn't above the creature's Might {might}."
        ], None
    record = next(
        (
            p
            for p in magus.progress
            if p.kind == "taming" and p.name == plan.title.strip() and not p.done
        ),
        None,
    )
    before = record.points if record is not None else 0
    return [], LabWork(
        None,
        total,
        might,
        points_before=before,
        points_gained=gained,
        finished=before + gained >= might,
    )


def decode_key(magus: Character, author: str) -> str:
    return f"decode:{magus.id}:{author}"


def _decode(
    saga: Saga, magus: Character, plan: SeasonPlan, lab_: Laboratory
) -> tuple[list[str], LabWork | None]:
    """Decoding another magus's Lab Texts: the Lab Total in the text's
    Technique + Form each season, until the points reach its level; points
    start at the highest level of his already decoded."""
    text = lab_text_of(saga, plan)
    if text is None or text.type != "Lab Text":
        return ["Choose the Lab Text to decode."], None
    if not library.can_read(saga, magus, text):
        return [f"{magus.name} can't get at {text.name}."], None
    if book_seasons.can_use_lab_text(magus, text):
        return [f"{magus.name} can already read {text.name}."], None
    arts = book_seasons.decode_total_arts(saga, text)
    if arts is None:
        return [f"{text.name} doesn't record its Technique and Form."], None
    level = book_seasons.text_level(text, saga)
    total = lab.lab_total(
        saga,
        magus,
        arts[0],
        arts[1],
        lab_,
        activity="learn_from_lab_text",
        days_missed=max(0, plan.days_away),
        experimenting=plan.experimenting,
    )
    total = _with_options(magus, plan, arts[0], arts[1], total, saga)
    if lab.distraction_penalty(max(0, plan.days_away)) is None:
        return [
            f"{plan.days_away} days away from the laboratory: no lab work is "
            "possible this season (more than 20)."
        ], None
    author = book_seasons.author_key(text)
    before = max(
        project_points_key(saga, decode_key(magus, author)),
        book_seasons.access_level(magus, author),
    )
    gained = max(0, int(total.total))
    if gained <= 0:
        return ["The Lab Total is 0: no progress is possible."], None
    return [], LabWork(
        None,
        total,
        level,
        points_before=before,
        points_gained=gained,
        finished=before + gained >= level,
        access=(magus.id, author, level),
    )


def project_points_key(saga: Saga, key: str) -> int:
    return next((p.points for p in saga.lab_projects if p.spell_id == key), 0)


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
    magus: Character,
    plan: SeasonPlan,
    technique: str,
    form: str,
    total: lab.LabTotal,
    saga: Saga | None = None,
) -> lab.LabTotal:
    """The Lab Total with the plan's options: a Magical Focus counts the
    lower Art twice, a Magic Theory Specialty that applies adds 1, any
    other modifier the troupe allows, and the Virtues and Flaws of
    rules.lab_virtues (Potent Magic, a Laboratory Horoscope... and the
    halvings, last)."""
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
    if plan.experimenting and plan.activity in EXPERIMENTAL:
        die = plan.experiment_die
        # Seeking a Discovery, the risk goes on the chart roll only.
        risk = 0 if seeking(plan) else plan.risk
        extra.append(
            Line(
                f"Experimentation (simple die {die if die is not None else '?'}"
                + (f" + risk {risk})" if risk else ")"),
                amount=(die or 0) + risk,
                source=experiment.SOURCE,
            )
        )
    if saga is not None:
        helpers = laboratory_seasons.assistants(saga, magus, plan)
        for helper in helpers[: lab.max_assistants(magus)]:
            extra.append(
                Line(
                    f"{helper.name} (assistant)",
                    amount=helper.characteristics.intelligence
                    + laboratory_seasons.magic_theory(helper),
                    source=laboratory_seasons.ASSIST_SOURCE,
                )
            )
    virtues, notes = lab_virtues.option_lines(
        magus,
        plan,
        enchanting=plan.activity in _ENCHANTING,
        talisman=_in_own_talisman(saga, magus, plan),
        binding=plan.activity == familiar_seasons.BIND,
        horoscope_score=lab_virtues.horoscope_score(magus),
    )
    extra += virtues
    halvings = lab_virtues.halving_lines(magus, plan, _design_range(saga, plan))
    if not extra and not halvings and not notes:
        return total
    summed = int(total.total + sum(line.amount or 0 for line in extra))
    return replace(
        total,
        total=lab_virtues.halved(summed, halvings),
        lines=[*total.lines, *extra, *halvings],
        notes=[*(total.notes or []), *notes] or None,
    )


#: Lab work that makes an enchanted device (Planetary Magic's horoscope).
_ENCHANTING: tuple[str, ...] = (
    enchant_seasons.INSTIL,
    enchant_seasons.LESSER_WORK,
    enchant_seasons.CHARGED_WORK,
)


def _in_own_talisman(saga: Saga | None, magus: Character, plan: SeasonPlan) -> bool:
    """Instilling an effect in the magus's own talisman (Hubris's)."""
    if saga is None or plan.activity != enchant_seasons.INSTIL:
        return False
    device = enchant_seasons.device_of(saga, plan)
    return (
        device is not None
        and device.talisman
        and enchantment.talisman_magus_id(device) == magus.id
    )


def _design_range(saga: Saga | None, plan: SeasonPlan) -> str | None:
    """The Range of the spell or effect a season designs (Short-Ranged
    Magic's), or None for work that designs nothing."""
    if plan.activity == INVENT:
        if plan.design is not None:
            return plan.design.range
        spell = the_spell(saga, plan) if saga is not None else None
        return spell.range if spell is not None else None
    if saga is not None and plan.activity in _ENCHANTING:
        device = enchant_seasons.device_of(saga, plan)
        effect = enchant_seasons.effect_of(device, plan) if device else None
        return effect.range if effect is not None else None
    return None


#: Lab work that can be done experimenting (not from a Lab Text).
EXPERIMENTAL: tuple[str, ...] = (
    INVENT,
    LONGEVITY,
    enchant_seasons.INSTIL,
    enchant_seasons.LESSER_WORK,
    enchant_seasons.CHARGED_WORK,
    enchant_seasons.INVESTIGATE,
    familiar_seasons.BIND,
    familiar_seasons.EMPOWER,
    TAMING,
)
#: Lab work that can take several seasons, points carried between them.
MULTI_SEASON: tuple[str, ...] = (
    experiment.STABILIZE,
    TAMING,
    INVENT,
    enchant_seasons.INSTIL,
    familiar_seasons.EMPOWER,
    book_seasons.DECODE_TEXT,
)


def seasons_left(work_: LabWork) -> int:
    """Seasons still needed after this one (0 when this one finishes it)."""
    if work_.finished or not work_.points_gained:
        return 0
    remaining = work_.level - work_.points_after
    return round_up(remaining / work_.points_gained)
