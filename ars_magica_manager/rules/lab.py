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
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .. import catalog
from ..covenants import covenant_effective_aura
from ..laboratories import (
    lab_aura_total,
    lab_characteristic_total,
    laboratory_source,
    specialization_scores,
)
from ..models import (
    Character,
    Covenant,
    CovenantBoonHookDef,
    Familiar,
    Laboratory,
    LabVirtueFlawDef,
    Saga,
)
from . import effects, realms, scores
from . import hybrid_magic as hybrid
from .breakdown import Breakdown, Line
from .rounding import round_down, round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Basic Laboratory "
    "Activities, Help in the Laboratory, Distractions from Lab Work "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Basic_Laboratory_Activities)"
)
QUALITY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, General Quality and "
    "Laboratory Specializations "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Laboratory_Specializations)"
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
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Inventing Spells, "
    "Laboratory Texts, Longevity Rituals, Vis Extraction, Shape and Material "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Inventing_Spells)"
)


def ability_score(character: Character | Familiar, name: str) -> tuple[int, int]:
    """An Ability's score and its fixed bonus (Puissant), 0 if absent."""
    ability = next((a for a in character.abilities if a.name == name), None)
    if ability is None:
        return 0, 0
    bonus, _ = scores.ability_bonus(character.virtues_flaws, name)
    return ability.level, bonus


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
    """A Lab Total's breakdown, plus anything that stops or limits it."""

    notes: list[str] | None = None


def _art_line(magus: Character, art: str) -> Line:
    score, bonus = art_score(magus, art)
    label = art if not bonus else f"{art} ({score}{bonus:+d})"
    return Line(label, amount=score + bonus, source=SOURCE)


def lab_total(
    saga: Saga,
    magus: Character,
    technique: str,
    form: str,
    lab: Laboratory,
    *,
    activity: str | None = None,
    assistants: Sequence[Character] = (),
    familiar: Familiar | None = None,
    days_missed: int = 0,
    experimenting: bool = False,
    similar_spell_level: int | None = None,
    shape_material: int = 0,
    from_lab_text: bool = False,
    others_text: bool = False,
) -> LabTotal:
    """The Lab Total for `technique` + `form` in `lab`, for an `activity`
    (a totals.ACTIVITIES_BY_TYPE["lab_total"] key) or none. Experimenting
    adds the Experimentation Specialization (the die is rolled separately);
    working `from_lab_text` adds the Texts Specialization to the activity's
    and drops the Virtues and Flaws that only count "when not using a Lab
    Text" (NOT_FROM_A_TEXT); from `others_text` -- a text someone else
    wrote -- it also takes the ones for working from others' Lab Texts
    (Adept Laboratory Student, Weak Scholar);
    inventing or enchanting adds the magnitude of the highest similar spell
    known (`similar_spell_level`); enchanting adds shape and material
    bonuses, capped at Magic Theory."""
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
        *_quality_lines(lab, lab_catalog, applies),
        *_helper_lines(magus, assistants, familiar, notes),
        *_activity_lines(magus, activity, similar_spell_level, shape_material),
        *_distraction_lines(days_missed, notes),
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
    combined = effects.combine(base, found, rounding=round_down)
    return LabTotal(total=combined.total, lines=lines + combined.lines[1:], notes=notes)


def _magus_lines(magus: Character, technique: str, form: str) -> list[Line]:
    """The Arts, Intelligence and Magic Theory."""
    label, theory = hybrid.theory(magus)
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
    boons: dict[str, CovenantBoonHookDef],
) -> Line:
    """The aura the lab sits in: its own place's, else its covenant's."""
    covenant_aura = covenant_effective_aura(covenant, boons) if covenant else 0
    realm = covenant.aura_realm if covenant else realms.HERMETIC
    from .. import places  # places reads the sheets, which read this

    own = places.lab_aura(saga, lab)
    if own is not None:
        covenant_aura, realm = own
    aura = lab_aura_total(lab, covenant_aura)
    label, amount = hybrid.aura_label(magus, realm, aura)
    return Line(label, amount=amount, source=realms.SOURCE)


def _quality_lines(
    lab: Laboratory,
    lab_catalog: dict[str, LabVirtueFlawDef],
    applies: set[str | None],
) -> list[Line]:
    """General Quality, and the lab's Specializations that `applies` names."""
    lines: list[Line] = []
    quality = lab_characteristic_total(lab, lab_catalog, "general_quality")[3]
    if quality:
        lines.append(Line("General Quality", amount=quality, source=QUALITY_SOURCE))
    for spec in specialization_scores(lab):
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
    if similar_spell_level and activity in ("invent_spells", "enchant_items"):
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
    lab_catalog: dict[str, LabVirtueFlawDef],
    covenant: Covenant | None,
    boons: dict[str, CovenantBoonHookDef],
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
    from .. import places  # places reads the sheets, which read this

    sources = [
        scores.character_source(magus.virtues_flaws),
        laboratory_source(lab, lab_catalog),
    ]
    if covenant is not None:
        sources.append(effects.EffectSource("covenant", covenant.boons_hooks, boons))
    sources.append(places.lab_source(saga, lab))
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
    10, rounded up."""
    return max(1, round_up(lab_total / 10))


def vis_limit(magus: Character) -> int:
    """The most raw vis a magus can use in one season's project: twice
    Magic Theory (Holy Magic for a holy magus)."""
    return 2 * hybrid.theory(magus)[1]


def shape_material_cap(magus: Character) -> int:
    """Shape and material bonuses to one enchanted effect are capped at the
    magus's Magic Theory (Holy Magic for a holy magus)."""
    return hybrid.theory(magus)[1]


def lowest_total(totals: Sequence[int]) -> int:
    """Several activities in one season use the lowest of their Lab Totals
    (against the sum of their levels)."""
    return min(totals)
