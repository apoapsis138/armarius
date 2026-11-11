"""The Lab Total.

    Lab Total = Technique + Form + Intelligence + Magic Theory + aura modifier
                + the lab's General Quality + its Specializations that apply
                + assistants' Intelligence + Magic Theory - distractions
                + Virtue/Flaw effects

A Specialization in an Art adds to every Lab Total using that Art; an
activity Specialization only to that activity (Spells to inventing spells,
Items to enchanting...). The aura modifier is Hermetic magic's (a Magic
power) in the lab's aura, from the realm interaction table. Per-activity
modifiers (similar spells, shape and material bonuses...) are added by
each activity. A holy magus uses Holy Magic for Magic Theory, and Holy or
Chthonic Magic changes the aura's modifier (rules.hybrid_magic).

No screen uses seasons_to_invent(), lab_text_usable(), lowest_total() yet:
they are the rules for screens still to come, and only the tests call them.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import TypedDict, Unpack

from .. import catalog
from ..models import (
    Character,
    Covenant,
    CovenantBoonHookDef,
    Familiar,
    Laboratory,
    LabVirtueFlawDef,
    Saga,
    SeasonPlan,
)
from . import aura_kinds, effects, house_mastery, lab_virtues, realms, scores, sites
from . import hybrid_magic as hybrid
from .breakdown import Breakdown, Line
from .lab_stats import (
    lab_aura_total,
    lab_characteristic_total,
    lab_safety,
    laboratory_source,
    specialization_scores,
)
from .realms import covenant_effective_aura
from .rounding import round_down, round_up
from .scores import ability_score

HELP_SOURCE = "Ars Magica Definitive Edition, Help in the Laboratory, pp. 264-265"
SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Basic Laboratory Activities, "
    "Help in the Laboratory, Distractions from Lab Work, pp. 249, 264-265"
)
QUALITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, General Quality and "
    "Laboratory Specializations, pp. 288-291"
)

#: The activity Specialization that adds to each Lab Total activity.
ACTIVITY_SPECIALIZATIONS: dict[str, str] = {
    "invent_spells": "Spells",
    "enchant_items": "Items",
    "extract_vis": "Vis Extraction",
    "longevity_ritual": "Longevity Rituals",
    "bind_familiar": "Familiar",
    "learn_from_lab_text": "Texts",
}
EXPERIMENTATION = "Experimentation"
#: The activity of working from someone else's Lab Text.
TEXT_ACTIVITY = "learn_from_lab_text"
#: Virtues and Flaws whose Lab Total effect the book gives "when not using a
#: Lab Text" (Inventive Genius: +3; Creative Block: -3 "unless using a Lab
#: Text"): left out of any work done from a text.
NOT_FROM_A_TEXT: frozenset[str] = frozenset(
    {"vf_inventive_genius", "vf_creative_block"}
)
ACTIVITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Inventing Spells, Laboratory "
    "Texts, Longevity Rituals, Vis Extraction, Shape and Material, pp. 250-263, 282-285"
)


def art_score(magus: Character, art: str) -> tuple[int, int]:
    """An Art's score and its fixed bonus (Puissant)."""
    score = magus.arts.get(art.lower())
    bonus, _ = scores.art_bonus(magus.virtues_flaws, art)
    return (score.level if score else 0), bonus


def max_assistants(magus: Character) -> int:
    """How many helpers the lead may use: his Leadership, at least 1 (a
    bound familiar may always help besides)."""
    score, bonus = ability_score(magus, "Leadership")
    return max(1, score + bonus)


def distraction_penalty(days_missed: int) -> int | None:
    """The Lab Total penalty for days away in a season: none for up to 10,
    then 10 + 2 per day past 10 (-12 at 11 days, -30 at 20); None past 20,
    when no lab activity is possible that season."""
    if days_missed <= 10:
        return 0
    if days_missed > 20:
        return None
    return -(10 + 2 * (days_missed - 10))


@dataclass
class LabTotal(Breakdown):
    """A Lab Total's breakdown, plus anything that stops or limits it.
    `flat` is the sum before any halving, and `multipliers` the halvings
    (a Deficiency, Weak Enchanter...), kept apart so that whatever is
    added to the total later is halved with the rest (with_lines)."""

    notes: list[str] | None = None
    flat: float | None = None
    multipliers: list[Line] = field(default_factory=list)


def _halved(flat: float, multipliers: Sequence[Line]) -> int:
    """The flat sum with every halving applied, rounded down once."""
    total = flat
    for line in multipliers:
        if line.multiplier is not None:
            total *= line.multiplier
    return round_down(total)


def with_lines(
    total: LabTotal,
    extra: Sequence[Line] = (),
    halvings: Sequence[Line] = (),
    notes: Sequence[str] = (),
) -> LabTotal:
    """`total` with more terms: `extra` added to its flat sum and `halvings`
    to its multipliers, so every halving -- a Deficiency, Weak Enchanter,
    Environmental Magic Condition -- applies to the whole Lab Total, last
    (DE pp. 125, 152)."""
    if not extra and not halvings and not notes:
        return total
    flat = (total.flat if total.flat is not None else total.total) + sum(
        line.amount or 0 for line in extra
    )
    multipliers = [*total.multipliers, *halvings]
    plain = [line for line in total.lines if line.multiplier is None]
    return replace(
        total,
        total=_halved(flat, multipliers),
        lines=[*plain, *extra, *multipliers],
        notes=[*(total.notes or []), *notes] or None,
        flat=flat,
        multipliers=multipliers,
    )


def _art_line(magus: Character, art: str) -> Line:
    score, bonus = art_score(magus, art)
    label = art if not bonus else f"{art} ({score}{bonus:+d})"
    return Line(label, amount=score + bonus, source=SOURCE)


class LabTotalTerms(TypedDict, total=False):
    """The keyword terms of `lab_total`, all optional."""

    activity: str | None
    assistants: Sequence[Character]
    familiar: Familiar | None
    days_missed: int
    experimenting: bool
    similar_spell_level: int | None
    shape_material: int
    from_lab_text: bool
    others_text: bool
    hermetic_text: bool


def lab_total(
    saga: Saga,
    magus: Character,
    technique: str,
    form: str,
    lab: Laboratory,
    **terms: Unpack[LabTotalTerms],
) -> LabTotal:
    """The Lab Total for `technique` + `form` in `lab` (the keywords of
    `LabTotalTerms`), for an `activity`
    (a totals.ACTIVITIES_BY_TYPE["lab_total"] key) or none. Experimenting
    adds the Experimentation Specialization (the die is rolled separately);
    working `from_lab_text` adds the Texts Specialization to the activity's
    and drops the Virtues and Flaws that only count "when not using a Lab
    Text" (NOT_FROM_A_TEXT); from `others_text` -- a text someone else
    wrote -- it also takes the ones for working from others' Lab Texts
    (Adept Laboratory Student, Weak Scholar), and a holy magus's total is
    halved when it is a `hermetic_text` (RoP: The Divine p. 67);
    inventing or enchanting adds the magnitude of the highest similar spell
    known (`similar_spell_level`); enchanting adds shape and material
    bonuses, capped at Magic Theory."""
    activity = terms.get("activity")
    experimenting = terms.get("experimenting", False)
    from_lab_text = terms.get("from_lab_text", False)
    others_text = terms.get("others_text", False)
    covenant = saga.covenant(lab.covenant_id)
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    applies = {technique, form, ACTIVITY_SPECIALIZATIONS.get(activity or "")}
    if experimenting:
        applies.add(EXPERIMENTATION)
    if from_lab_text:
        applies.add(ACTIVITY_SPECIALIZATIONS[TEXT_ACTIVITY])
    notes: list[str] = []
    lines = [
        *_magus_lines(magus, technique, form),
        _aura_line(saga, magus, lab, covenant, boons),
        *_aligned_lines(saga, lab, covenant, boons, technique, form),
        *_quality_lines(saga, lab, lab_catalog, applies),
        *_helper_lines(
            magus, terms.get("assistants", ()), terms.get("familiar"), notes
        ),
        *_activity_lines(
            magus,
            activity,
            terms.get("similar_spell_level"),
            terms.get("shape_material", 0),
        ),
        *_distraction_lines(terms.get("days_missed", 0), notes),
    ]
    base = sum(line.amount or 0 for line in lines)
    found = _virtue_effects(
        saga,
        magus,
        lab,
        lab_catalog,
        covenant,
        boons,
        technique,
        form,
        activity,
        experimenting=experimenting,
        from_lab_text=from_lab_text,
        others_text=others_text,
    )
    flat_effects = [e for e in found if e.amount is not None]
    combined = effects.combine(base, flat_effects)
    multipliers = [
        Line(e.name, multiplier=e.modifier.multiplier, source=e.kind)
        for e in found
        if e.modifier.multiplier is not None
    ]
    if (
        others_text
        and terms.get("hermetic_text", True)
        and hybrid.halves_hermetic_texts(magus)
    ):
        multipliers.append(
            Line(
                "Holy Magic, from a Hermetic Lab Text",
                multiplier=0.5,
                source=hybrid.HOLY_SOURCE,
            )
        )
    return LabTotal(
        total=_halved(combined.total, multipliers),
        lines=lines + combined.lines[1:] + multipliers,
        notes=notes,
        flat=combined.total,
        multipliers=multipliers,
    )


def _magus_lines(magus: Character, technique: str, form: str) -> list[Line]:
    """The Arts, Intelligence and Magic Theory."""
    label, theory = hybrid.theory(magus)
    # Its fixed bonus (Puissant) shown apart, as an Art's is, so the line
    # agrees with the score the Diary gives.
    name = label.removesuffix(" (for Magic Theory)")
    score, bonus = ability_score(magus, name)
    if bonus and score + bonus == theory:
        label = f"{label} ({score}{bonus:+d})"
    return [
        _art_line(magus, technique),
        _art_line(magus, form),
        Line("Intelligence", amount=magus.characteristics.intelligence, source=SOURCE),
        Line(label, amount=theory, source=SOURCE),
    ]


def _aura_line(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    covenant: Covenant | None,
    boons: Mapping[str, CovenantBoonHookDef],
) -> Line:
    """The aura the lab sits in, as a Lab Total line."""
    aura, realm = _place_aura(saga, lab, covenant, boons)
    label, amount = hybrid.aura_label(magus, realm, aura)
    return Line(label, amount=amount, source=realms.SOURCE)


def _aligned_lines(
    saga: Saga,
    lab: Laboratory,
    covenant: Covenant | None,
    boons: Mapping[str, CovenantBoonHookDef],
    technique: str,
    form: str,
) -> list[Line]:
    """The aura again, when the lab's Magic aura is aligned with the
    total's Technique or Form (RoP: Magic p. 16)."""
    kind = sites.kind_where(saga, sites.lab_place(saga, lab))
    if not kind:
        return []
    aura, realm = _place_aura(saga, lab, covenant, boons)
    return aura_kinds.aligned_lines(kind, realm, aura, (technique, form))


def _place_aura(
    saga: Saga,
    lab: Laboratory,
    covenant: Covenant | None,
    boons: Mapping[str, CovenantBoonHookDef],
) -> tuple[int, str]:
    """The aura the lab sits in (score, realm): its own place's, else its
    covenant's, with the lab's own modifier."""
    covenant_aura = covenant_effective_aura(covenant, boons) if covenant else 0
    realm = covenant.aura_realm if covenant else realms.HERMETIC
    own = sites.lab_aura(saga, lab)
    if own is not None:
        covenant_aura, realm = own
    return lab_aura_total(lab, covenant_aura), realm


def lab_aura(saga: Saga, lab: Laboratory) -> tuple[int, str]:
    """The aura (score, realm) `lab` sits in, the one its Lab Totals use."""
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return _place_aura(saga, lab, saga.covenant(lab.covenant_id), boons)


def botch_conditions(
    saga: Saga, character: Character, lab: Laboratory | None = None
) -> tuple[int, int]:
    """The aura and Safety a lab roll's botch dice count: those of `lab`,
    else of the character's own laboratory; with none, the covenant's aura
    and Safety 0. In the Magic Realm the aura counted takes the
    boundary's level on top, as a boundary adds that many botch dice to
    every roll the Magic aura helps (RoP: Magic p. 22)."""
    lab = lab or saga.laboratory(character.assigned_lab_id)
    if lab is None:
        aura, _ = realms.home_aura(saga, character)
        return aura + sites.character_boundary_botch_dice(saga, character), 0
    aura, _ = lab_aura(saga, lab)
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    aura += sites.lab_boundary_botch_dice(saga, lab)
    return aura, lab_safety(lab, by_id, saga)


def _quality_lines(
    saga: Saga,
    lab: Laboratory,
    lab_catalog: Mapping[str, LabVirtueFlawDef],
    applies: set[str | None],
) -> list[Line]:
    """General Quality, and the lab's Specializations that `applies` names."""
    lines: list[Line] = []
    quality = lab_characteristic_total(lab, lab_catalog, "general_quality", saga)[3]
    if quality:
        lines.append(Line("General Quality", amount=quality, source=QUALITY_SOURCE))
    for spec in specialization_scores(saga, lab):
        if spec.counts and spec.name in applies:
            lines.append(
                Line(
                    f"{spec.name} Specialization",
                    amount=spec.points,
                    source=QUALITY_SOURCE,
                )
            )
    return lines


def _helper_lines(
    magus: Character,
    assistants: Sequence[Character],
    familiar: Familiar | None,
    notes: list[str],
) -> list[Line]:
    """Each assistant's and the familiar's Intelligence + Magic Theory; a
    note in `notes` when there are more assistants than Leadership allows."""
    lines: list[Line] = []
    helpers = [*assistants]
    if len(helpers) > max_assistants(magus):
        notes.append(
            f"{len(helpers)} assistants, but {magus.name}'s Leadership allows "
            f"{max_assistants(magus)}."
        )
    for helper in helpers:
        score, bonus = ability_score(helper, "Magic Theory")
        lines.append(
            Line(
                f"{helper.name} (assistant)",
                amount=helper.characteristics.intelligence + score + bonus,
                source=SOURCE,
            )
        )
    if familiar is not None:
        score, bonus = ability_score(familiar, "Magic Theory")
        lines.append(
            Line(
                f"{familiar.name} (familiar)",
                amount=familiar.characteristics.intelligence + score + bonus,
                source=SOURCE,
            )
        )
    return lines


def _activity_lines(
    magus: Character,
    activity: str | None,
    similar_spell_level: int | None,
    shape_material: int,
) -> list[Line]:
    """Inventing's and enchanting's similar spell, and enchanting's shape
    and material bonus, capped at Magic Theory."""
    lines: list[Line] = []
    if similar_spell_level and activity in (
        "invent_spells",
        "enchant_items",
        "bind_familiar",
    ):
        lines.append(
            Line(
                f"Similar spell (level {similar_spell_level})",
                amount=round_up(similar_spell_level / 5),
                source=ACTIVITY_SOURCE,
            )
        )
    if shape_material and activity == "enchant_items":
        capped = min(shape_material, shape_material_cap(magus))
        label = "Shape and material" + (
            f" ({shape_material}, capped by Magic Theory)"
            if capped < shape_material
            else ""
        )
        lines.append(Line(label, amount=capped, source=ACTIVITY_SOURCE))
    return lines


def _distraction_lines(days_missed: int, notes: list[str]) -> list[Line]:
    """The penalty for days away, or a note in `notes` that too many days
    leave no lab work possible."""
    penalty = distraction_penalty(days_missed)
    if penalty is None:
        notes.append(f"{days_missed} days away: no lab work is possible this season.")
        return []
    if penalty:
        return [
            Line(f"Distractions ({days_missed} days)", amount=penalty, source=SOURCE)
        ]
    return []


def _virtue_effects(
    saga: Saga,
    magus: Character,
    lab: Laboratory,
    lab_catalog: Mapping[str, LabVirtueFlawDef],
    covenant: Covenant | None,
    boons: Mapping[str, CovenantBoonHookDef],
    technique: str,
    form: str,
    activity: str | None,
    *,
    experimenting: bool,
    from_lab_text: bool,
    others_text: bool,
) -> list[effects.Effect]:
    """The magus's, lab's, covenant's and place's Virtues and Flaws that
    change this Lab Total."""

    sources = [
        scores.character_source(magus.virtues_flaws),
        laboratory_source(lab, lab_catalog),
    ]
    if covenant is not None:
        sources.append(effects.EffectSource("covenant", covenant.boons_hooks, boons))
    sources.append(sites.lab_source(saga, lab))
    found = _pair_effects(sources, technique, form, activity, experimenting)
    if from_lab_text:
        found = [e for e in found if e.entry.id not in NOT_FROM_A_TEXT]
    if others_text and activity != TEXT_ACTIVITY:
        found += [
            e
            for e in _pair_effects(sources, technique, form, TEXT_ACTIVITY)
            if e.modifier.activity == TEXT_ACTIVITY
        ]
    return found


def similar_spell_level(
    saga: Saga | None, magus: Character, spell_id: str | None
) -> int | None:
    """The level of the similar spell a plan names, if the magus knows it
    and Disjointed Magic doesn't take the bonus away (DE pp. 126, 260)."""
    if saga is None or not spell_id:
        return None
    spell = catalog.find_spell(saga, spell_id)
    if spell is None or spell.level is None:
        return None
    if not any(k.spell_id == spell.id for k in magus.spells_known):
        return None
    if lab_virtues.has(magus, lab_virtues.DISJOINTED):
        return None
    return spell.level


def lab_mastery_lines(
    saga: Saga | None, magus: Character, spell_id: str | None
) -> list[Line]:
    """Lab Mastery on the similar spell the plan names: its Mastery score
    on top of the similar spell's bonus (Houses of Hermes: True Lineages
    p. 100)."""
    if similar_spell_level(saga, magus, spell_id) is None:
        return []
    known = next((k for k in magus.spells_known if k.spell_id == spell_id), None)
    if known is None or not known.mastery_score:
        return []
    if not any(
        a.name.strip().casefold() == house_mastery.LAB_MASTERY
        for a in known.mastery_abilities
    ):
        return []
    return [
        Line("Lab Mastery", amount=known.mastery_score, source=house_mastery.SOURCE)
    ]


def helper_lines(
    helper: Character | Familiar,
    technique: str,
    form: str,
    activity: str | None,
    *,
    experimenting: bool = False,
    label: str = "assistant",
) -> list[Line]:
    """What one helper adds: Intelligence + Magic Theory, then each of their
    Virtues and Flaws that change this Lab Total, as the primary magus's
    would (DE p. 264: Inventive Genius is the book's example). Only the
    amounts count, not a helper's halvings."""
    score, bonus = ability_score(helper, "Magic Theory")
    lines = [
        Line(
            f"{helper.name} ({label})",
            amount=helper.characteristics.intelligence + score + bonus,
            source=HELP_SOURCE,
        )
    ]
    found = _pair_effects(
        [scores.character_source(helper.virtues_flaws)],
        technique,
        form,
        activity,
        experimenting,
    )
    for effect in found:
        if effect.amount:
            lines.append(Line(f"{helper.name}: {effect.name}", amount=effect.amount))
    return lines


def _pair_effects(
    sources: list[effects.EffectSource],
    technique: str,
    form: str,
    activity: str | None,
    experimenting: bool = False,
) -> list[effects.Effect]:
    """The `lab_total` effects that apply to a Technique + Form pair and the
    activity: general ones, the activity's own, and when experimenting the
    experimentation ones, which replace the same Virtue's activity bonus
    (Inventive Genius: +3 inventing, "+6 instead" when experimenting). A
    targeted effect applies when its target is either Art."""
    wanted = {None, activity} | ({"experimentation"} if experimenting else set())
    found = [
        e
        for e in effects.collect(sources, "lab_total")
        if e.modifier.activity in wanted
        and (
            e.target is None
            or e.target.casefold() in (technique.casefold(), form.casefold())
        )
    ]
    if experimenting:
        replacing = {
            e.entry.id for e in found if e.modifier.activity == "experimentation"
        }
        found = [
            e
            for e in found
            if e.entry.id not in replacing
            or e.modifier.activity in (None, "experimentation")
        ]
    return found


def points_per_season(lab_total: int, level: int) -> int:
    """Inventing a spell: each season adds Lab Total - level points (none
    unless the Lab Total is greater); done when they reach the level."""
    return max(0, lab_total - level)


def seasons_to_invent(lab_total: int, level: int) -> int | None:
    """How many seasons inventing takes (None when the Lab Total isn't
    above the level). One season when the Lab Total is at least twice it."""
    points = points_per_season(lab_total, level)
    if points <= 0:
        return None
    return round_up(level / points)


def lab_text_usable(lab_total: int, level: int) -> bool:
    """A Lab Text's effect is reproduced in one season if the Lab Total at
    least equals its level."""
    return lab_total >= level


def longevity_modifier(lab_total: int, *, mundane: bool = False) -> int:
    """A Longevity Ritual's aging-roll modifier: the Creo Corpus Lab Total
    / 5 (/ 10 for a mundane subject), rounded up."""
    return round_up(lab_total / (10 if mundane else 5))


def vis_extracted(lab_total: int) -> int:
    """Pawns of Vim vis from a season of extraction: Creo Vim Lab Total /
    10, rounded up; none from a total of 0 or less (DE p. 250)."""
    return max(0, round_up(lab_total / 10))


def vis_limit(magus: Character) -> int:
    """The most raw vis a magus can use in one season's project: twice
    Magic Theory (Holy Magic for a holy magus)."""
    return 2 * hybrid.theory(magus)[1]


#: Where a Longevity Ritual's vis is limited when it is performed from its
#: Lab Text (a rebrew), and when it is designed in a season.
RITUAL_VIS_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Longevity Rituals, "
    "p. 261; The Mysteries Revised Edition, Longevity Ritual Vis Limits, p. 42"
)


def ritual_vis_problem(magus: Character, art: str, pawns: int) -> str:
    """Why `pawns` of `art` vis is more than the magus can use performing a
    Longevity Ritual from its Lab Text: as for casting a ritual spell, each
    Art's vis at most his score in that Art (DE p. 261; TMRE p. 42). ""
    when it isn't."""
    score = art_score(magus, art)[0]
    if pawns <= score:
        return ""
    return (
        f"The ritual takes {pawns} pawns of {art} vis; performed from its Lab "
        f"Text, {magus.name} can use at most his {art} score ({score}) of it, "
        f"as for a ritual spell ({RITUAL_VIS_SOURCE})."
    )


def shape_material_cap(magus: Character) -> int:
    """Shape and material bonuses to one enchanted effect are capped at the
    magus's Magic Theory (Holy Magic for a holy magus)."""
    return hybrid.theory(magus)[1]


def lowest_total(totals: Sequence[int]) -> int:
    """Several activities in one season use the lowest of their Lab Totals
    (against the sum of their levels)."""
    return min(totals)


#: Adds a season plan's options (a Magical Focus, a Magic Theory
#: Specialty, the troupe's other modifiers) to the Lab Total for a
#: Technique and Form.
LabOptions = Callable[[Character, SeasonPlan, str, str, LabTotal], LabTotal]
