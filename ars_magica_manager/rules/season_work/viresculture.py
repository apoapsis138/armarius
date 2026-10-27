"""Legends of Hermes' seasons: Hermetic Viresculture's two laboratory
activities, Vitalizing a Stirps and Invigorating one (pp. 72-75).

Each plan names the Stirps (its title) and its Magic Might, or its Lesser
Enchantment Vis's effect level (its book_level), and any others worked on
in the same season (more_stirpes); Invigorating also names the Stirps'
Form (its form). Vitalizing pays its Vim from the pool the plan's
vis_from names. A Stirps being Vitalized keeps its points in
a Progress record ("vitalization"); an Invigorated one keeps its breeding
seasons left ("invigorated stirps", no target).
"""

from __future__ import annotations

import random

from ... import vis
from ...arts import FORMS
from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from .. import lab
from .. import viresculture as vc
from .base import MAGI, SimpleActivity, SupplementWork, progress_of, register, source

VITALIZATION = source("Legends of Hermes, Vitalizing Vis, pp. 72-73", "LoH")
INVIGORATION = source(
    "Legends of Hermes, Invigorating a Stirps and Caring for Vis, pp. 73-75", "LoH"
)


def _level(plan: SeasonPlan) -> int:
    return vc.vitalization_level(plan.book_level or 0)


def _stirpes(plan: SeasonPlan) -> list[tuple[str, int]]:
    """The Stirpes worked on this season, (name, Level) each: the one the
    plan names, then any others (Multiple Laboratory Activities)."""
    return [(plan.title.strip(), _level(plan))] + [
        (name, vc.vitalization_level(might))
        for name, might in plan.more_stirpes.items()
    ]


def _vitalization_vis(character: Character, plan: SeasonPlan) -> int:
    """Pawns of Vim this season pays: each Stirps' own, with its first
    season (one still being Vitalized has paid already)."""
    return vc.vitalization_vis_for(
        [
            level
            for name, level in _stirpes(plan)
            if (record := progress_of(character, vc.VITALIZING, name)) is None
            or record.done
        ]
    )


def _vitalize(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """A season's points toward the Stirps: the Total less its Level (less
    the sum of the Levels for several, which then all finish); the Vim
    vis is paid with its first season."""
    stirpes = _stirpes(plan)
    total = int(vc.vitalization_total(saga, character).total)
    pawns = _vitalization_vis(character, plan)
    if pawns:
        result.vis_cost["Vim"] = pawns
    finished = stirpes
    if len(stirpes) > 1:
        together = sum(level for _, level in stirpes)
        for name, level in stirpes:
            target = max(1, level)
            result.progress.append((vc.VITALIZING, name, target, target))
        names = ", ".join(name for name, _ in stirpes)
        result.notes.append(
            f"Vitalization Total {total} against Levels {together} together "
            f"({vc.vitalization_points(total, together)} points): {names} all "
            "become Stirpes this season (Multiple Laboratory Activities)."
        )
    else:
        name, level = stirpes[0]
        points = vc.vitalization_points(total, level)
        # A Level of 0 still takes its season.
        target = max(1, level)
        result.progress.append((vc.VITALIZING, name, target, points))
        record = progress_of(character, vc.VITALIZING, name)
        so_far = (record.points if record and not record.done else 0) + points
        result.notes.append(
            f"Vitalization Total {total} against Level {level}: {points} "
            f"point(s) toward {name} ({min(so_far, target)}/{target})."
        )
        if so_far < target:
            finished = []
    if pawns:
        result.notes.append(
            f"Pays {pawns} pawn(s) of Vim vis from {vis.payer(character, plan)} "
            "raw vis, fed to it or to the water it grows in (one per ten "
            "levels, LoH p. 73)."
        )
    for name, _ in finished:
        result.notes.append(
            f"{name} is a Stirps: Invigorate it to make it breed vis. Until "
            "then its young are ordinary, and its vis may be transferred out "
            "without harm (but it is no longer a Stirps)."
        )


def _invigorate(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The breeding seasons the Total gives each Stirps (shared among
    several), and each one's yield."""
    stirpes = _stirpes(plan)
    total = int(vc.invigoration_total(saga, character, plan.form).total)
    share = vc.shared_total(total, len(stirpes))
    seasons = vc.breeding_seasons(share)
    used = vc.requisite_form(character, plan.form)
    art = plan.form if used == plan.form else f"{plan.form}, Vim lower"
    if len(stirpes) > 1:
        result.notes.append(
            f"Invigoration Total {total} ({art}) shared among {len(stirpes)} "
            f"Stirpes: {share} each (Multiple Laboratory Activities)."
        )
    for name, level in stirpes:
        pawns = vc.pawns_per_breeding(level)
        result.progress.append((vc.INVIGORATED, name, 0, seasons))
        result.stirpes.append((name, plan.form, level))
        vitalized = progress_of(character, vc.VITALIZING, name)
        if vitalized is None or not vitalized.done:
            result.notes.append(
                f"{name} is taken to be a Stirps already (found, or born of one)."
            )
        result.notes.append(
            f"Invigoration Total {share} ({art}): {name} has {seasons} breeding "
            f"season(s), each giving {pawns} pawn(s) of {plan.form} vis, one in "
            "ten of them a new Stirps."
        )
    result.notes.append(
        f"Keep them in a Magic aura and fed from one; each needs "
        f"{vc.LABOR_PER_STIRPS} Labor Points of care a year (a pawn less for "
        f"every {vc.LABOR_PER_PAWN} short, and for each month unattended). "
        f"{character.name} can tend {vc.score(character)} Stirps."
    )


def _problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if not vc.can_practise(character):
        return [
            f"{character.name} needs a score in {vc.ABILITY} (only those Opened "
            "to the Hermetic Arts have it)."
        ]
    if not plan.title.strip():
        return ["Name the Stirps (the creature, plant or Lesser Enchantment Vis)."]
    if plan.book_level is None or plan.book_level < 0:
        return ["Type its Magic Might (or its Lesser Enchantment Vis's level)."]
    missing = [name for name, might in plan.more_stirpes.items() if might < 0]
    if missing:
        return [
            f"Type a Magic Might for {', '.join(missing)} "
            "(Name: Might, separated by semicolons)."
        ]
    if plan.title.strip() in plan.more_stirpes:
        return [f"{plan.title.strip()} is named twice."]
    return []


def _vitalize_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    found = _problems(saga, character, plan)
    if found:
        return found
    stirpes = _stirpes(plan)
    levels = [level for _, level in stirpes]
    if len(stirpes) > 1:
        total = int(vc.vitalization_total(saga, character).total)
        if not vc.vitalized_together(total, levels):
            return [
                f"Vitalizing several Stirpes in a season needs the Total ({total}) "
                f"to finish them all: at least twice their Levels together "
                f"({2 * sum(levels)}); Vitalize them one at a time instead "
                "(Multiple Laboratory Activities, DE p. 264)."
            ]
    pawns = _vitalization_vis(character, plan)
    limit = lab.vis_limit(character)
    if pawns > limit:
        return [
            f"Vitalizing takes {pawns} pawns of Vim vis; {character.name} can "
            f"handle {limit} in a season (twice Magic Theory)."
        ]
    held = vis.season_pool(saga, character, plan).get("vim", 0)
    if held < pawns:
        return [
            f"Vitalizing takes {pawns} pawn(s) of Vim vis; "
            f"{vis.payer(character, plan)} raw vis has {held}."
        ]
    return []


def _invigorate_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    found = _problems(saga, character, plan)
    if not found and plan.form not in FORMS:
        found.append("Choose the Stirps' Form (its Might's, or its vis's).")
    return found


register(
    SimpleActivity(
        vc.VITALIZE,
        "Vitalize a Stirps (Viresculture)",
        "A season making a living source of vis a Stirps: the Vitalization "
        "Total less its Might in points, until they reach its Might.",
        VITALIZATION,
        "MOH",
        who=MAGI,
        no_xp=True,
        group=groups.WORK,
    ),
    _vitalize,
    _vitalize_problems,
)
register(
    SimpleActivity(
        vc.INVIGORATE,
        "Invigorate a Stirps (Viresculture)",
        "A season letting a Stirps breed vis: a breeding season per ten "
        "points of the Invigoration Total, each a fifth of its Might in pawns.",
        INVIGORATION,
        "MOH",
        who=MAGI,
        no_xp=True,
        group=groups.WORK,
    ),
    _invigorate,
    _invigorate_problems,
)
