"""What a season does to a character: experience, its Diary entry,
warping and aging."""

from __future__ import annotations

import random
from collections.abc import Sequence

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
from ..rules import (
    divine_state,
    grog_discipline,
    harm,
    medicine,
    mysticism,
    realm_warping,
    sites,
    tmre_alchemy,
    work_virtues,
)
from ..rules import hybrid_magic as hybrid
from ..rules import living as living_rules
from ..rules import warping as warping_rules
from ..rules import xp as xp_rules
from ..rules.realms import home_aura
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
    if plan.by_default:
        name += " (default)"
    lines = [_gain_line(g, names) for g in worked.gains]
    lines += worked.notes
    if worked.lab_work is not None:
        lines.append(work_text(worked.lab_work, plan) + ".")
    book = worked.effect_of(rules.BookEffect)
    if book is not None:
        lines.append(book_text(book.work, plan) + ".")
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


#: The Living Conditions modifier aging uses, for the rules outside a
#: season's aging (pre-play aging from the Grogs Aging Chart).
living_conditions = living_rules.living_conditions


#: How gain_warping writes the realm a Warping Point came from.
REALM_LINE = "Realm: "


def _warped_this_year(saga: Saga, character: Character) -> set[str]:
    """The realms events gave the character Warping Points from this year
    (gain_warping writes each in the Diary with its realm; an older entry
    without one counts as Magic)."""
    found: set[str] = set()
    for entry in character.diary:
        if entry.year != saga.current_year or not (
            entry.name.startswith("Warping +")
            or entry.name in realm_warping.NAMES.values()
        ):
            continue
        realm = next(
            (
                line.removeprefix(REALM_LINE).strip()
                for line in entry.details.splitlines()
                if line.startswith(REALM_LINE)
            ),
            "Magic",
        )
        found.add(realm or "Magic")
    return found


def _yearly_warping(saga: Saga, character: Character) -> str:
    """A year's automatic Warping Points: +1 for a Longevity
    Ritual, and living in a strong aura of another realm (a magus gains none
    from a Magic aura, a holy or chthonic magus none from his other realm's),
    the Virtues and Flaws that give one a year, each constant effect on the
    character (DE p. 391), and with Susceptibility to
    Warping one more for each realm that gave any this year (DE p. 146: a
    Longevity Ritual's count as Magic, an aura's or a place's as its
    realm, a Virtue's as its own realm, and an event's as the realm
    recorded with it). Returns what was added ("" for nothing)."""
    gained: list[str] = []
    # The points from each realm: for Susceptibility to Warping, and
    # counted toward the Warping's main source.
    by_realm: dict[str, int] = {}

    def add(realm_of: str, each: int, what: str) -> None:
        by_realm[realm_of] = by_realm.get(realm_of, 0) + each
        gained.append(what)

    if warping_rules.immune(character):
        return ""
    if character.aging.longevity_modifier:
        add("Magic", 1, "Longevity Ritual 1")
    aura, realm = home_aura(saga, character)
    # A non-magus's Virtue at Warping Score 5 stops points from auras of its
    # kind: the realm most of their Warping came from.
    attuned = (
        not warping_rules.opened_to_arts(character)
        and character.aging.warping_score >= warping_rules.ATTUNED_SCORE
        and realm == realm_warping.main_realm(saga, character)
    )
    if hybrid.warps_from_aura(character, realm) and not attuned:
        from_aura = warping_rules.aura_points(
            aura, character.aging.aura_time, saga.current_year
        )
        if from_aura:
            add(realm, from_aura, f"{realm} aura {aura}: {from_aura}")
    from_place = sites.warping_per_year(saga, character)
    if from_place:
        where = sites.character_place(saga, character)
        name = where[0].name if where is not None else "Where they live"
        add(realm, from_place, f"{name}: {from_place}")
    for name, each, realm_of in work_virtues.yearly_warping(character):
        add(realm_of, each, f"{name} {each}")
    for effect in character.constant_effects:
        each = warping_rules.constant_points(effect)
        add(
            effect.realm or "Magic",
            each,
            f"{effect.name or 'A constant effect'} {each}",
        )
    realms_ = {r for r, each in by_realm.items() if each} | _warped_this_year(
        saga, character
    )
    points = sum(by_realm.values())
    if work_virtues.susceptible(character) and realms_:
        points += len(realms_)
        gained.append(f"Susceptibility to Warping {len(realms_)}")
    if not points:
        return ""
    before = character.aging.warping_score
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    for realm_of, each in by_realm.items():
        realm_warping.record(character, realm_of, each)
    text = f"Warping Points +{points} ({', '.join(gained)}); Warping Score now {character.aging.warping_score}."
    return " ".join([text, *_warped_effects(saga, character, before, points)])


def _warped_effects(
    saga: Saga, character: Character, before: int, points: int = 0
) -> list[str]:
    """What a non-magus's higher Warping Score brings, for the Diary,
    coloured by the realm most of it came from (a magus's Warping means
    Twilight instead: DE p. 391; a tradition's members have its own; a
    mystic's is the Divine Ascent, and in the Divine Gloom each point
    gained is experience: The Church p. 23)."""
    if divine_state.path(character):
        return mysticism.gloom_lines(character, points)
    if (
        warping_rules.opened_to_arts(character)
        or character.traditions
        or realm_warping.holy(character)
    ):
        return []
    return realm_warping.effects(
        before,
        character.aging.warping_score,
        realm_warping.main_realm(saga, character),
    )


def gain_warping(
    saga: Saga,
    character: Character,
    points: int,
    rng: random.Random,
    *,
    opened: bool = False,
    aura: int | None = None,
    enter: bool = False,
    realm: str = "Magic",
    at_once: bool = True,
    lines: Sequence[str] = (),
) -> list[str]:
    """Add Warping Points from one event (`realm`'s, counted toward the
    main source); 2 or more set off the character's answer to them
    (realm_warping.response_realm): Wizard's Twilight for a magus (with
    `opened`, anyone whose Arts are opened), the Divine Ascent,
    Vituperation or a Faerie Calling for a tradition's member, rolled
    against the aura where it happened (`aura`; where they live when not
    given), or entered at once (`enter`). Points that come apart
    (`at_once` False: transits, leaving Faerie) set off nothing. `lines`
    go first in the Diary entry. Writes a Diary entry and returns its
    lines. A character with a Might score (Demonic Blood) is immune."""
    if warping_rules.immune(character):
        return [f"{character.name} is immune to Warping (a Might score)."]
    before = character.aging.warping_score
    warping_rules.set_total(character, warping_rules.total_points(character) + points)
    realm_warping.record(character, realm, points)
    notes = [
        *lines,
        f"+{points} Warping Points; Warping Score {character.aging.warping_score}.",
        *_warped_effects(saga, character, before, points),
    ]
    name = f"Warping +{points}"
    answer = realm_warping.response_realm(character, opened=opened)
    source = warping_rules.TWILIGHT_SOURCE
    if answer is not None and at_once and points >= divine_state.trigger(character):
        if aura is None:
            aura, _ = home_aura(saga, character)
        result = realm_warping.respond(
            answer, character, points, aura, rng, saga, enter=enter
        )
        source = realm_warping.SOURCES[answer]
        notes += result.notes
        if result.entered:
            name = realm_warping.NAMES[answer]
            if answer == realm_warping.MAGIC and (
                lost := medicine.lose_eucrasia(
                    character, saga.current_year, "Wizard's Twilight"
                )
            ):
                notes.append(lost)
            warping_rules.set_total(
                character, warping_rules.total_points(character) + result.extra_points
            )
            realm_warping.record(character, answer, result.extra_points)
            if result.seasons:
                season, year = saga.current_season, saga.current_year
                for _ in range(result.seasons - 1):
                    season, year = next_season(season, year)
                character.aging.twilight_until = f"{season} {year}"
                notes.append(
                    f"{name} lasts through {season} {year}: no seasons can be "
                    "planned until then."
                )
    character.diary.append(
        DiaryEntry(
            year=saga.current_year,
            season=saga.current_season,
            name=name,
            details="\n".join(notes)
            + f"\n{REALM_LINE}{realm}"
            + f"\nRule: {_cite(source)}",
            activity="Aging",
        )
    )
    return notes


def _camp_disease(
    saga: Saga, character: Character, year: int, rng: random.Random
) -> list[str]:
    """After a whole year in a campaigning army, a Disease Avoidance roll
    (Lords of Men p. 102) against the camp's disease, the Bloody Flux unless
    a plan names another (Art & Academe pp. 46-47)."""
    if living_rules.campaign_seasons(character, year) < living_rules.CAMPAIGN_YEAR:
        return []
    named = next(
        (
            p.camp_disease
            for p in saga.season_plans
            if p.character_id == character.id and p.year == year and p.camp_disease
        ),
        CAMP_DISEASE,
    )
    caught = harm.catch_disease(saga, character, {"aa_disease": named}, rng)
    return [f"A year with the army: {named}: " + " ".join(caught.lines)]


#: The camp's disease unless a plan names another: "common in towns and
#: campaigning armies" (Art & Academe p. 47).
CAMP_DISEASE = "Bloody Flux"


def age_character(
    saga: Saga,
    character: Character,
    age: int,
    rng: random.Random,
    *,
    living: int | None = None,
    when: tuple[str, int] | None = None,
    label: str = "Aging",
    young: bool = False,
) -> SeasonRecordLine:
    """One character's aging roll: apparent age, Aging Points and
    Characteristics, Decrepitude, a Crisis; written in the Diary. Pre-play
    aging gives its own Living Conditions, the (season, year)
    the roll belongs to, and a label for the Diary; `young` is a young
    craftsman's exertion roll (aging_rules.roll). A being of Magic the
    Great Elixir made immortal makes none (TMRE p. 44)."""
    if character.being_of_magic:
        return SeasonRecordLine(
            character.id,
            character.name,
            character.covenant_id,
            label,
            "",
            "No aging roll: a being of Magic no longer ages (TMRE p. 44).",
        )
    familiar = saga.familiar_of(character.id)
    bronze = familiar.bronze_cord if familiar is not None else 0
    season, year = (
        when if when is not None else (saga.current_season, saga.current_year)
    )
    if living is None:
        # A grog's year on better or worse rations counts for his aging
        # roll only (Grogs pp. 23, 25).
        living = (
            living_rules.living_conditions(saga, character)
            + grog_discipline.rations_living(character, year)
            + living_rules.chevauchee_aging(saga, character)
        )
    result = aging_rules.roll(character, age, living, bronze, rng, saga, young=young)
    aging = character.aging
    camp = _camp_disease(saga, character, year, rng)
    if result.apparent:
        aging.apparent_age = (
            aging.apparent_age if aging.apparent_age is not None else age - 1
        ) + 1
    elif aging.apparent_age is None:
        aging.apparent_age = age - 1
    notes = list(result.notes) + camp
    for name, points in result.points.items():
        notes += aging_rules.add_points(character, name, points)
    if result.points:
        gained = ", ".join(f"{n.title()} {p}" for n, p in result.points.items())
        notes.append(f"Aging Points: {gained}.")
    if result.any_points:
        # The player chooses where they go; their Decrepitude counts now,
        # before any Crisis (DE p. 392).
        aging.decrepitude_points += result.any_points
        aging.aging_due += [
            f"{aging_rules.ANY_POINT}, {season} {year}: any Characteristic "
            f"(suggested: {name.title()})"
            for name in result.suggested
        ]
        notes.append(
            f"{result.any_points} Aging Point(s) in any Characteristic: the "
            "player places them (Place Aging Points)."
        )
    aging.decrepitude = aging_rules.decrepitude_score(aging.decrepitude_points)
    if result.crisis:
        text, ends = aging_rules.crisis(character, age, aging.decrepitude, rng, saga)
        notes.append(text)
        if result.any_points and aging_rules.fatal_crisis(text):
            # The Crisis is rolled with the raised Decrepitude, whichever
            # Characteristics take the points; the survival roll is the
            # table's, after they are placed.
            notes.append(
                "Place the Aging Points before the survival roll: one in "
                "Stamina may lower it."
            )
        if ends:
            aging.longevity_modifier = 0
            # The Lesser Elixir's dose ends with it (TMRE p. 43).
            tmre_alchemy.end_elixir(character)
        harmless = aging_rules.unaging(character) and not aging_rules.fatal_crisis(text)
        if harmless:
            notes.append("Unaging: a Crisis that can't kill does no harm (DE p. 114).")
        else:
            after, after_year = next_season(season, year)
            aging.recovering = f"{after} {after_year}"
        if aging_rules.leper(character):
            character.wounds.heavy += 1
            notes.append("Leprosy: a Heavy Wound with the Crisis (DE p. 135).")
    summary = (
        "no apparent aging"
        if not result.apparent
        else "apparent age +1"
        + (
            f", {sum(result.points.values()) + result.any_points} Aging Point(s)"
            if result.points or result.any_points
            else ""
        )
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
