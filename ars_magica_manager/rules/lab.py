"""The Lab Total (STORY-801).

    Lab Total = Technique + Form + Intelligence + Magic Theory + aura modifier
                + the lab's General Quality + its Specializations that apply
                + assistants' Intelligence + Magic Theory - distractions
                + Virtue/Flaw effects

A Specialization in an Art adds to every Lab Total using that Art; an
activity Specialization only to that activity (Spells to inventing spells,
Items to enchanting...). The aura modifier is Hermetic magic's (a Magic
power) in the lab's aura, from the realm interaction table. Per-activity
modifiers (similar spells, shape and material bonuses...) are STORY-816.
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
from ..models import Character, Familiar, Laboratory, Saga
from . import effects, realms, scores
from .breakdown import Breakdown, Line
from .rounding import round_down

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
) -> LabTotal:
    """The Lab Total for `technique` + `form` in `lab`, for an `activity`
    (a totals.ACTIVITIES_BY_TYPE["lab_total"] key) or none. Experimenting
    adds the Experimentation Specialization (the die is rolled separately);
    inventing or enchanting adds the magnitude of the highest similar spell
    known (`similar_spell_level`); enchanting adds shape and material
    bonuses, capped at Magic Theory."""
    lines = [_art_line(magus, technique), _art_line(magus, form)]
    lines.append(
        Line("Intelligence", amount=magus.characteristics.intelligence, source=SOURCE)
    )
    theory, theory_bonus = ability_score(magus, "Magic Theory")
    lines.append(Line("Magic Theory", amount=theory + theory_bonus, source=SOURCE))

    covenant = saga.covenant(lab.covenant_id)
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    covenant_aura = covenant_effective_aura(covenant, boons) if covenant else 0
    aura = lab_aura_total(lab, covenant_aura)
    realm = covenant.aura_realm if covenant else realms.HERMETIC
    lines.append(
        Line(
            f"Aura ({realm} {aura})",
            amount=realms.aura_modifier(realms.HERMETIC, realm, aura),
            source=realms.SOURCE,
        )
    )

    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    quality = lab_characteristic_total(lab, lab_catalog, "general_quality")[3]
    if quality:
        lines.append(Line("General Quality", amount=quality, source=QUALITY_SOURCE))
    applies = {technique, form, ACTIVITY_SPECIALIZATIONS.get(activity or "")}
    if experimenting:
        applies.add(EXPERIMENTATION)
    for spec in specialization_scores(lab):
        if spec.counts and spec.name in applies:
            lines.append(
                Line(
                    f"{spec.name} Specialization",
                    amount=spec.points,
                    source=QUALITY_SOURCE,
                )
            )

    notes: list[str] = []
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

    if similar_spell_level and activity in ("invent_spells", "enchant_items"):
        lines.append(
            Line(
                f"Similar spell (level {similar_spell_level})",
                amount=-(-similar_spell_level // 5),
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

    penalty = distraction_penalty(days_missed)
    if penalty is None:
        notes.append(f"{days_missed} days away: no lab work is possible this season.")
    elif penalty:
        lines.append(
            Line(f"Distractions ({days_missed} days)", amount=penalty, source=SOURCE)
        )

    base = sum(line.amount or 0 for line in lines)
    sources = [
        scores.character_source(magus.virtues_flaws),
        laboratory_source(lab, lab_catalog),
    ]
    if covenant is not None:
        sources.append(effects.EffectSource("covenant", covenant.boons_hooks, boons))
    found = _pair_effects(sources, technique, form, activity, experimenting)
    combined = effects.combine(base, found, rounding=round_down)
    return LabTotal(total=combined.total, lines=lines + combined.lines[1:], notes=notes)


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
    return -(-level // points)


def lab_text_usable(lab_total: int, level: int) -> bool:
    """A Lab Text's effect is reproduced in one season if the Lab Total at
    least equals its level."""
    return lab_total >= level


def longevity_modifier(lab_total: int, *, mundane: bool = False) -> int:
    """A Longevity Ritual's aging-roll modifier: the Creo Corpus Lab Total
    / 5 (/ 10 for a mundane subject), rounded up."""
    return -(-lab_total // (10 if mundane else 5))


def vis_extracted(lab_total: int) -> int:
    """Pawns of Vim vis from a season of extraction: Creo Vim Lab Total /
    10, rounded up."""
    return max(1, -(-lab_total // 10))


def vis_limit(magus: Character) -> int:
    """The most raw vis a magus can use in one season's project: twice
    Magic Theory."""
    return 2 * sum(ability_score(magus, "Magic Theory"))


def shape_material_cap(magus: Character) -> int:
    """Shape and material bonuses to one enchanted effect are capped at the
    magus's Magic Theory."""
    return sum(ability_score(magus, "Magic Theory"))


def lowest_total(totals: Sequence[int]) -> int:
    """Several activities in one season use the lowest of their Lab Totals
    (against the sum of their levels)."""
    return min(totals)
