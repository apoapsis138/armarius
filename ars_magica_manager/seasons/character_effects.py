"""What a season does to a character: experience, its Diary entry,
warping and aging."""

from __future__ import annotations

import random

from ..covenants import home_aura
from ..familiars import familiar_of
from ..models import (
    Ability,
    ArtScore,
    Character,
    DiaryEntry,
    Saga,
    SeasonRecordLine,
    next_season,
)
from ..rules import activities as rules
from ..rules import aging as aging_rules
from ..rules import creation_access as access
from ..rules import effects
from ..rules import warping as warping_rules
from ..rules import xp as xp_rules
from ..rules.rounding import round_down
from .plans import _cite, _gain_line, book_text, plan_subject, spell_names, work_text


def _add_xp(character: Character, subject: str, amount: int) -> None:
    kind, _, name = subject.partition(":")
    if kind == "ability":
        ability = next((a for a in character.abilities if a.name == name), None)
        if ability is None:
            # Taught, trained or read in an Ability they didn't have yet.
            ability = Ability(name, xp_table=access.ability_xp_table(name))
            character.abilities.append(ability)
        ability.xp += amount
    elif kind == "art":
        character.arts.setdefault(name.lower(), ArtScore()).xp += amount
    elif kind == "mastery":
        known = next(k for k in character.spells_known if k.spell_id == name)
        known.mastery_xp += amount
        # Mastery's score and xp are both typed on the sheet: the xp can only
        # raise the score, never lower one typed higher.
        known.mastery_score = max(
            known.mastery_score,
            xp_rules.score_from_xp(known.mastery_xp, xp_rules.ABILITY_FACTOR),
        )


def diary_entry(saga: Saga, character: Character, worked: rules.Outcome) -> DiaryEntry:
    """The character Diary entry recording an applied season."""
    plan = worked.plan
    activity = worked.activity
    names = spell_names(saga, character)
    # The Diary's Activity column names the activity already.
    name = plan_subject(saga, character, plan) or (
        activity.label if activity else plan.activity
    )
    if worked.gains:
        total = sum(g.result.xp for g in worked.gains)
        name += f" (+{total} xp)"
    lines = [_gain_line(g, names) for g in worked.gains]
    lines += worked.notes
    if worked.lab_work is not None:
        lines.append(work_text(worked.lab_work, plan) + ".")
    if worked.book_work is not None:
        lines.append(book_text(worked.book_work, plan) + ".")
    if plan.days_away:
        lines.append(f"{plan.days_away} days away from the laboratory.")
    if plan.months_lost and activity and activity.distractable:
        lines.append(f"{plan.months_lost} month(s) lost to distractions.")
    if plan.details.strip() and activity and activity.gives_xp:
        lines.append(f"Notes: {plan.details.strip()}")
    elif plan.details.strip():
        lines.append(plan.details.strip())
    if activity is not None:
        lines.append(f"Rule: {_cite(activity.source)}")
    return DiaryEntry(
        year=plan.year,
        season=plan.season,
        name=name,
        details="\n".join(lines),
        activity=activity.label if activity else plan.activity,
    )


#: A laboratory's Health / LAB_HEALTH_DIVISOR, rounded down, adds to its
#: magus's Living Conditions.
LAB_HEALTH_DIVISOR = 2


LAB_HEALTH_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Health "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Eight:"
    "_Laboratory#Health)"
)


def _living_conditions(saga: Saga, character: Character) -> int:
    """The Living Conditions modifier: the covenant's for magi or mundanes,
    plus half the Health of a magus's laboratory, rounded down (negative
    Health too: -3 gives -2), per LAB_HEALTH_SOURCE."""
    covenant = saga.covenant(character.covenant_id)
    living = 0
    if covenant is not None:
        living = (
            covenant.living_conditions_magi
            if character.type == "magus"
            else covenant.living_conditions_mundane
        )
    lab = saga.laboratory(character.assigned_lab_id)
    if lab is not None and character.type == "magus":
        from .. import catalog
        from ..laboratories import lab_characteristic_total

        health = lab_characteristic_total(
            lab, catalog.load_lab_virtue_flaw_catalog_by_id(), "health"
        )[3]
        living += round_down(health / LAB_HEALTH_DIVISOR)
    from .. import places

    here = places.character_effects(saga, character, "living_conditions")
    return living + int(effects.amount_total(here))


def _yearly_warping(saga: Saga, character: Character) -> str:
    """A year's automatic Warping Points: +1 for a Longevity
    Ritual, and living in a strong aura of another realm (a magus gains none
    from a Magic aura). Returns what was added ("" for nothing)."""
    gained: list[str] = []
    points = 0
    if character.aging.longevity_modifier:
        points += 1
        gained.append("Longevity Ritual 1")
    aura, realm = home_aura(saga, character)
    if not (character.type == "magus" and realm == "Magic"):
        from_aura = warping_rules.aura_points(aura)
        if from_aura:
            points += from_aura
            gained.append(f"{realm} aura {aura}: {from_aura}")
    from .. import places

    from_place = places.warping_per_year(saga, character)
    if from_place:
        points += from_place
        where = places.character_place(saga, character)
        name = where[0].name if where is not None else "Where they live"
        gained.append(f"{name}: {from_place}")
    if not points:
        return ""
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    return f"Warping Points +{points} ({', '.join(gained)}); Warping Score now {character.aging.warping_score}."


def gain_warping(
    saga: Saga, character: Character, points: int, rng: random.Random
) -> list[str]:
    """Add Warping Points from one event; 2 or more take a
    magus to the edge of Wizard's Twilight. Writes a Diary entry and returns
    its lines."""
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    notes = [
        f"+{points} Warping Points; Warping Score {character.aging.warping_score}."
    ]
    name = f"Warping +{points}"
    if character.type == "magus" and points >= 2:
        aura, _ = home_aura(saga, character)
        result = warping_rules.twilight(character, points, aura, rng, saga)
        notes += result.notes
        if result.entered:
            name = "Wizard's Twilight"
            warping_rules.set_total(
                character, warping_rules.total_points(character) + result.extra_points
            )
            if result.seasons:
                season, year = saga.current_season, saga.current_year
                for _ in range(result.seasons - 1):
                    season, year = next_season(season, year)
                character.aging.twilight_until = f"{season} {year}"
                notes.append(
                    f"Lost in Twilight through {season} {year}: no seasons can be "
                    "planned until then."
                )
    character.diary.append(
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            name=name,
            details="\n".join(notes)
            + f"\nRule: {_cite(warping_rules.TWILIGHT_SOURCE)}",
            activity="Aging",
        )
    )
    return notes


def age_character(
    saga: Saga,
    character: Character,
    age: int,
    rng: random.Random,
    *,
    living: int | None = None,
    when: tuple[str, int] | None = None,
    label: str = "Aging",
) -> SeasonRecordLine:
    """One character's aging roll: apparent age, Aging Points and
    Characteristics, Decrepitude, a Crisis; written in the Diary. Pre-play
    aging gives its own Living Conditions, the (season, year)
    the roll belongs to, and a label for the Diary."""
    familiar = familiar_of(saga, character.id)
    bronze = familiar.bronze_cord if familiar is not None else 0
    if living is None:
        living = _living_conditions(saga, character)
    season, year = (
        when if when is not None else (saga.current_season, saga.current_year)
    )
    result = aging_rules.roll(character, age, living, bronze, rng, saga)
    aging = character.aging
    if result.apparent:
        aging.apparent_age = (
            aging.apparent_age if aging.apparent_age is not None else age - 1
        ) + 1
    elif aging.apparent_age is None:
        aging.apparent_age = age - 1
    notes = list(result.notes)
    for name, points in result.points.items():
        aging.aging_points[name] = aging.aging_points.get(name, 0) + points
        aging.decrepitude_points += points
        score = getattr(character.characteristics, name)
        if aging.aging_points[name] > abs(score) and not aging_rules.unaging(character):
            setattr(character.characteristics, name, score - 1)
            aging.aging_points[name] = 0
            notes.append(f"{name.title()} falls to {score - 1:+d}.")
    if result.points:
        gained = ", ".join(f"{n.title()} {p}" for n, p in result.points.items())
        notes.append(f"Aging Points: {gained}.")
    aging.decrepitude = aging_rules.decrepitude_score(aging.decrepitude_points)
    if result.crisis:
        text, ends = aging_rules.crisis(character, age, aging.decrepitude, rng, saga)
        notes.append(text)
        if ends:
            aging.longevity_modifier = 0
        after, after_year = next_season(season, year)
        aging.recovering = f"{after} {after_year}"
    summary = (
        "no apparent aging"
        if not result.apparent
        else "apparent age +1"
        + (f", {sum(result.points.values())} Aging Point(s)" if result.points else "")
        + (", an Aging Crisis" if result.crisis else "")
    )
    character.diary.append(
        DiaryEntry(
            year=year,
            season=season,
            name=f"{label}: {summary}",
            details="\n".join(notes) + f"\nRule: {_cite(aging_rules.SOURCE)}",
            activity="Aging",
        )
    )
    return SeasonRecordLine(
        character.id,
        character.name,
        character.covenant_id,
        label,
        "",
        summary,
    )
