"""City & Guild's seasons: working for Labor Points, a workshop's
production and improvement, excellent and wondrous items, moving up in
wealth, repairs and merchant ventures.

- Labor Points: a working season gives (Characteristic + Craft or
  Profession) x the Wealth Multiplier (Poor 2, average 3, Wealthy 6); a
  business costs 36 a year (+5 per point of Raw Materials).
- Workshops: Workshop Total = Characteristic + Craft + Innovation + Raw
  Materials (+ assistants, a manual, a specialty: the plan's Other); the
  quality it reaches (Standard 6, Superior 12, Excellent 15). Exertion adds
  a simple die, rolls the exertion table and an Aging roll. A craft manual
  (Artes Liberales 1, 1 Labor Point) scores Craft / 3.
- Excellent and wondrous items are progress records on the character,
  carried season to season.
- Exertion (City & Guild pp. 73-74; an excellent or wondrous item's
  season too, as Klaus exerts on his wondrous sword, p. 76): + a simple die
  to the Workshop Total, a stress die on the exertion table (a botch is a
  disaster; 6-7 lose the simple die; 9 a simple die of Labor Points toward
  Innovation; 10-11 a simple die of xp in the (Craft) Reputation; 12+ a
  simple die of xp in the Craft), and an Aging roll whatever his age: under
  35 a simple die for the stress die, and a 13 brings no Crisis (DE p.
  392).
- (Craft) Reputation (p. 74): starts at 0 and rises as an Ability; 1 xp a
  season the Workshop Total is 6 or more over the standard goods' Craft
  Level (a wondrous item's season too), and 1 more for making a wondrous
  item; each shoddy season after the first in a row takes 1 xp off, and
  below 0 it becomes a positive Reputation as a bad craftsman (the "bad"
  is in its name, as DE p. 386 scores every Reputation as an Ability).
- A laborer's working season (p. 76): Labor Total = primary Characteristic
  (Strength unless the plan names one, p. 67) + Profession against the
  Profession Level 6, +1 in an Infernal, Faerie or Magic aura as a Craft
  Level is (p. 69): shoddy, standard or superior service (never
  excellent), and a (Profession) Reputation as a craftsman's. His Labor
  Points stay Communication + Profession (p. 38).
"""

from __future__ import annotations

import random

from ...models import (
    Book,
    Character,
    Saga,
    ScoredTrait,
    SeasonPlan,
    VirtueFlawInstance,
    season_order,
)
from .. import activity_groups as groups
from .. import confidence, dice, realms, work_virtues
from ..reputations import LOCAL
from ..rounding import round_down, round_up
from ..scores import ability_level
from .base import (
    CH,
    COMPANIONS,
    SimpleActivity,
    SupplementWork,
    characteristic,
    experience_only,
    multiplier,
    needs_subject,
    progress_of,
    register,
    source,
    subject_ability,
    wealth,
)
from .definitive import kept_points

CITY_GUILD = source("City & Guild " + CH.format("City_%26_Guild"), "C&G")
SOURCE = "City & Guild, Chapter Two: Labor and Livelihood, pp. 37-40"
#: Craft Levels: an excellent item's at the basic level, and a wondrous
#: item's base before its magnitude and uses (City & Guild pp. 67, 72).
EXCELLENT_LEVEL = 15
WONDROUS_BASE = 12
#: The standard goods' basic Craft Level (City & Guild p. 67), which a
#: wondrous item's season counts its Reputation margin from (p. 74).
STANDARD_LEVEL = 6
TOUCHED_BY_REALM = "vf_touched_by_realm"
#: Touched by (Realm) for horseshoes alone (Grogs p. 76): one Form, powers
#: on the horse or the ground it treads, Craft: Farrier with Intelligence
#: or Dexterity.
MYTHIC_FARRIER = "vf_mythic_farrier"
FARRIER_CHARACTERISTICS = ("intelligence", "dexterity")
BUSINESS_UPKEEP = 36
RAW_MATERIALS_UPKEEP = 5
#: Workshop improvement costs in Labor Points, by the score it reaches.
INNOVATION_COST = {1: 100, 2: 200, 3: 300}
RAW_MATERIALS_COST = {1: 50, 2: 100, 3: 150}
#: Quality reached by a Workshop Total (at the basic Craft Level 6).
QUALITIES: tuple[tuple[int, str], ...] = (
    (15, "Excellent"),
    (12, "Superior"),
    (6, "Standard"),
    (0, "Shoddy"),
)
EXERTION = (
    (3, "no special result"),
    (5, "disappointing ramifications (harder materials, a glut, an enemy)"),
    (7, "no benefit: the simple die isn't added"),
    (8, "a story event"),
    (9, "invention: a simple die of Labor Points toward Innovation"),
    (11, "increased Reputation: a simple die of xp in the Craft Reputation"),
)
EXERTION_SOURCE = "City & Guild, Workshop Exertion, pp. 73-74"
#: Exertion's Aging roll is a young man's under this age: a simple die, and
#: no Crisis on a 13 (City & Guild p. 74).
YOUNG_EXERTION_AGE = 35
REPUTATION_SOURCE = "City & Guild, Reputations, p. 74"
#: A season's Workshop (or Labor) Total this far over the standard goods'
#: Craft Level earns 1 xp in the (Craft) Reputation.
REPUTATION_MARGIN = 6
#: Labor Points banked toward Innovation by an exertion's invention: a
#: progress record with no target, spent by the next Innovation raised.
INNOVATION_KIND = "innovation"
INNOVATION_BANK = "Invention toward Innovation"
#: Written in the season's notes (and so its Diary entry) when the goods
#: or service are shoddy, so the next season can tell it follows one.
SHODDY = "Shoddy work"
LABOR_SOURCE = "City & Guild, Basic Laborer's Service, p. 76"
#: A laborer's Profession Level, and the best service he can give.
PROFESSION_LEVEL = 6
#: A laborer's primary Characteristic when the plan names none (p. 67).
LABORER_CHARACTERISTIC = "strength"
#: The Craft (and Profession) Level's rise in an aura of these realms
#: (City & Guild p. 69; none for a Divine aura).
AURA_LEVEL_REALMS = ("Infernal", "Faerie", "Magic")
AURA_LEVEL_STEP = 1
LABOR_QUALITIES = QUALITIES[1:]
MANUAL_SOURCE = "City & Guild, Chapter Four: Crafts, Craftsman Manuals, p. 73"
#: A craft manual's score: the author's Craft / MANUAL_DIVISOR, rounded up.
MANUAL_DIVISOR = 3
#: Labor Points to move up a step: Poor to average, average to Wealthy,
#: Wealthy to Poor in the next social class (City & Guild p. 38).
STATION_COST = {"poor": 120, "average": 360, "wealthy": 1080}


def workshop_total(character: Character, plan: SeasonPlan, craft: str) -> int:
    return (
        characteristic(character, plan, "dexterity")
        + ability_level(character, craft)
        + character.workshop_innovation
        + character.workshop_raw_materials
        + plan.other_modifier
    )


def quality_for(total: int, craft_level: int) -> str:
    """The best quality the Workshop Total reaches, the thresholds moved
    with the Craft Level (basic 6)."""
    shift = craft_level - 6
    return next(label for top, label in QUALITIES if total >= top + shift)


def labor_quality(total: int) -> str:
    """A laborer's service for his Labor Total against the Profession
    Level 6: Superior at 12, Standard at 6, else Shoddy; never better
    (City & Guild p. 76)."""
    return next(label for top, label in LABOR_QUALITIES if total >= top)


def trade(ability: str) -> str:
    """The trade a Craft or Profession names ("Craft: Smith" -> "Smith"),
    which names its Reputation."""
    return ability.partition(":")[2].strip() or ability


def bad_trade(name: str) -> str:
    """The name of the Reputation as a bad craftsman of `name`'s trade."""
    return f"Shoddy {name}"


def _level_xp(level: int) -> int:
    """The xp a Reputation at `level` holds, on the Ability scale."""
    return confidence.XP_PER_LEVEL * level * (level + 1) // 2


def reputation_xp(reputation: ScoredTrait) -> int:
    """Every xp the Reputation holds: its level's and those toward the
    next."""
    return _level_xp(max(0, reputation.score)) + reputation.deeds


def _set_xp(reputation: ScoredTrait, xp: int) -> None:
    level = 0
    while _level_xp(level + 1) <= xp:
        level += 1
    reputation.score, reputation.deeds = level, xp - _level_xp(level)


def _reputation(character: Character, name: str) -> ScoredTrait | None:
    return next(
        (r for r in character.reputations if r.name.casefold() == name.casefold()),
        None,
    )


def add_trade_reputation(character: Character, name: str, xp: int) -> None:
    """Add `xp` to the (Craft) or (Profession) Reputation of the trade
    `name`, made at 0 if new, rising as an Ability. A negative `xp` takes
    experience off it, and what it can't take goes to a Reputation as a bad
    craftsman, scored positive like any Reputation (City & Guild p. 74;
    DE p. 386)."""
    good = _reputation(character, name)
    if xp >= 0:
        if good is None:
            good = ScoredTrait(name, 0, type=LOCAL)
            character.reputations.append(good)
        confidence.add_deeds(good, xp)
        return
    lost = -xp
    if good is not None:
        held = reputation_xp(good)
        taken = min(held, lost)
        _set_xp(good, held - taken)
        lost -= taken
    if not lost:
        return
    bad = _reputation(character, bad_trade(name))
    if bad is None:
        bad = ScoredTrait(bad_trade(name), 0, type=LOCAL)
        character.reputations.append(bad)
    _set_xp(bad, reputation_xp(bad) + lost)


def banked_innovation(character: Character) -> int:
    """Labor Points an exertion's inventions have put toward Innovation."""
    record = progress_of(character, INNOVATION_KIND, INNOVATION_BANK)
    return record.points if record is not None and not record.done else 0


def innovation_due(character: Character) -> int:
    """The Labor Points raising Innovation a step still costs once the
    banked inventions are counted."""
    cost = INNOVATION_COST[character.workshop_innovation + 1]
    return max(0, cost - banked_innovation(character))


def shoddy_before(character: Character, plan: SeasonPlan, ability: str) -> bool:
    """Whether the season before the plan's made shoddy goods (or gave
    shoddy service) in `ability`, as its Diary entry says."""
    before = season_order(season=plan.season, year=plan.year) - 1
    mark = f"{SHODDY} ({ability})"
    return any(
        season_order(season=entry.season, year=entry.year) == before
        and mark in entry.details
        for entry in character.diary
    )


def _quality_reputation(
    character: Character,
    plan: SeasonPlan,
    ability: str,
    total: int,
    standard: int,
    shoddy: bool,
    result: SupplementWork,
) -> None:
    """A season's Reputation experience from its total: 1 xp 6 or more
    over the standard Level; a shoddy season after a shoddy one, 1 off
    (City & Guild p. 74)."""
    name = trade(ability)
    if total >= standard + REPUTATION_MARGIN:
        result.reputation_xp.append((name, 1))
        result.notes.append(
            f"{REPUTATION_MARGIN} or more over the standard Level "
            f"{standard}: 1 xp in the {name} Reputation (City & Guild p. 74)."
        )
    if shoddy:
        result.notes.append(f"{SHODDY} ({ability}).")
        if shoddy_before(character, plan, ability):
            result.reputation_xp.append((name, -1))
            result.notes.append(
                f"Shoddy two seasons running: 1 xp off the {name} Reputation "
                "(below 0, a Reputation as a bad craftsman; City & Guild p. 74)."
            )


def _age_in(character: Character, year: int) -> int | None:
    born = character.background.year_born
    return None if born is None else year - born


def _exert(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
    craft: str,
) -> int:
    """An exerted season's dice (City & Guild pp. 73-74): the simple die
    it adds to the Workshop Total (0 when not exerting, when the season is
    only previewed, or on No Benefit), its exertion result written into
    `result`, and the Aging roll."""
    if not plan.experimenting:
        return 0
    if rng is None:
        result.notes.append("Exertion: its dice are rolled when the season is played.")
        return 0
    die = dice.simple_die(rng)
    roll = dice.stress_die(rng, 1, saga=saga)
    if roll.botched:
        outcome = "disaster (the storyguide's ruinous event)"
    else:
        outcome = next((text for top, text in EXERTION if roll.value <= top), None) or (
            "increased understanding: a simple die of xp in the Craft"
        )
    if roll.value in (6, 7) and not roll.botched:
        die = 0
    elif roll.value == 9 and not roll.botched:
        points = dice.simple_die(rng)
        result.progress.append((INNOVATION_KIND, INNOVATION_BANK, 0, points))
        outcome += f" ({points})"
    elif roll.value in (10, 11) and not roll.botched:
        points = dice.simple_die(rng)
        result.reputation_xp.append((trade(craft), points))
        outcome += f" ({points})"
    elif roll.value >= 12 and not roll.botched:
        points = dice.simple_die(rng)
        result.ability_xp.append((craft, points))
        outcome += f" ({points})"
    result.aging_roll = True
    age = _age_in(character, plan.year)
    result.aging_young = age is not None and age < YOUNG_EXERTION_AGE
    young = (
        " (under 35: a simple die, and a 13 brings no Crisis)"
        if result.aging_young
        else ""
    )
    result.notes.append(
        f"Exertion: + simple die {die}; the exertion roll {roll.value}: "
        f"{outcome}. An Aging roll this season{young}."
    )
    return die


def excellent_bonus(total: int, level: int, craft: int) -> int | None:
    """An excellent item's bonus: +1 for every 3 points the Workshop Total
    is over its Craft Level, at most the Craft / 3, rounded up (City &
    Guild p. 69); None when the total falls short."""
    if total < level:
        return None
    return min((total - level) // 3, round_up(craft / 3))


def touched_realm(character: Character) -> str:
    """The realm a wondrous craftsman's power comes from, as his Touched by
    (Realm) or Mythic Farrier names it: one of the four realms (City &
    Guild p. 71; a farrier most likely Magic or Faerie, Grogs p. 76); ""
    when it names none of them."""
    for vf in character.virtues_flaws:
        if vf.vf_id in (TOUCHED_BY_REALM, MYTHIC_FARRIER):
            named = str(vf.params.get("realm", "")).strip().title()
            named = {"Magical": realms.HERMETIC}.get(named, named)
            return named if named in realms.REALMS else ""
    return ""


def wondrous_aura(character: Character, plan: SeasonPlan) -> int:
    """The aura's modifier to a wondrous item's Workshop Total: the aura the
    craftsman works in (the plan's), by the Realm Interaction table for
    his power's realm (City & Guild p. 72; DE pp. 410-411)."""
    aura, aura_realm = plan.site_aura or 0, plan.site_realm or realms.HERMETIC
    realm = touched_realm(character)
    if aura <= 0 or aura_realm not in realms.REALMS or not realm:
        return 0
    return realms.aura_modifier(realm, aura_realm, aura)


# -- checks --------------------------------------------------------------------


def _craft_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    if not subject_ability(plan):
        return ["Choose the Craft."]
    return []


def _improve_workshop_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    step = plan.title.strip().lower()
    if step not in ("innovation", "raw materials"):
        return ["Choose Innovation or Raw Materials to improve."]
    score = (
        character.workshop_innovation
        if step == "innovation"
        else character.workshop_raw_materials
    )
    costs = INNOVATION_COST if step == "innovation" else RAW_MATERIALS_COST
    if score >= 3:
        return [f"{step.title()} is already at its most (3)."]
    due = innovation_due(character) if step == "innovation" else costs[score + 1]
    if character.labor_points < due:
        banked = banked_innovation(character) if step == "innovation" else 0
        counted = f" ({banked} banked by inventions)" if banked else ""
        return [
            f"Raising {step.title()} to {score + 1} costs {costs[score + 1]} "
            f"Labor Points{counted}; {character.name} has "
            f"{character.labor_points}."
        ]
    return []


def _improve_station_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    cost = STATION_COST[wealth(character)]
    if character.labor_points < cost:
        return [
            f"Moving up from {wealth(character)} costs {cost} Labor Points "
            f"(City & Guild p. 38); {character.name} has "
            f"{character.labor_points}."
        ]
    return []


def _wondrous_problems(saga: Saga, character: Character, plan: SeasonPlan) -> list[str]:
    held = {vf.vf_id for vf in character.virtues_flaws}
    if not held & {TOUCHED_BY_REALM, MYTHIC_FARRIER}:
        return [
            f"Only a craftsman Touched by (Realm) makes wondrous items "
            f"(City & Guild p. 70); {character.name} isn't."
        ]
    if (
        TOUCHED_BY_REALM not in held
        and (plan.characteristic or "dexterity") not in FARRIER_CHARACTERISTICS
    ):
        return [
            "A Mythic Farrier's Craft Total is Intelligence or Dexterity + "
            "Craft: Farrier (Grogs p. 76)."
        ]
    if not touched_realm(character):
        return [
            "Name the realm of his Touched by (Realm) or Mythic Farrier "
            "Virtue: Magic, Faerie, Divine or Infernal (City & Guild p. 71; "
            "a farrier most likely Magic or Faerie, Infernal possible, Grogs "
            "p. 76)."
        ]
    if plan.teacher_id == character.id:
        return ["The assistant is someone other than the craftsman."]
    return []


# -- outcomes ------------------------------------------------------------------


def _working_season(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    wm = multiplier(character)
    craft = subject_ability(plan)
    default = {
        "working_season": "communication"
        if craft.startswith("Profession")
        else "dexterity",
        "tournament": "dexterity",
        "apothecary": "intelligence",
    }[plan.activity]
    penalty = work_virtues.aura_penalty(saga, character, craft)
    laborer = plan.activity == "working_season" and craft.startswith("Profession")
    # A laborer's Labor Points are always Communication + Profession (p. 38):
    # the plan's Characteristic is his primary one, for the Labor Total.
    used = (default if laborer else (plan.characteristic or default)).lower()
    lp = (
        getattr(character.characteristics, used, 0)
        + ability_level(character, craft)
        + penalty
    ) * wm
    result.labor_points = lp
    away = f" {penalty:+d} (Necessary Realm Aura)" if penalty else ""
    result.notes.append(
        f"Labor Points: ({used.title()} + {craft}{away}) x "
        f"{wm} ({wealth(character)}) = {lp}."
    )
    if laborer:
        _laborers_service(saga, character, plan, craft, penalty, result)


def profession_level(saga: Saga, character: Character) -> int:
    """A laborer's Profession Level where he lives: 6, +1 in an Infernal,
    Faerie or Magic aura (City & Guild pp. 69, 76)."""
    aura, realm = realms.home_aura(saga, character)
    raised = aura > 0 and realm in AURA_LEVEL_REALMS
    return PROFESSION_LEVEL + (AURA_LEVEL_STEP if raised else 0)


def labor_total(character: Character, plan: SeasonPlan, profession: str) -> int:
    """A laborer's Labor Total: his primary Characteristic (the plan's,
    else Strength) + Profession (City & Guild pp. 67, 76)."""
    name = plan.characteristic or LABORER_CHARACTERISTIC
    return getattr(character.characteristics, name.lower(), 0) + ability_level(
        character, profession
    )


def _laborers_service(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    profession: str,
    penalty: int,
    result: SupplementWork,
) -> None:
    """A laborer's season: his Labor Total against the Profession Level,
    the service it gives, and his (Profession) Reputation (City & Guild
    p. 76)."""
    total = labor_total(character, plan, profession) + penalty
    level = profession_level(saga, character)
    quality = labor_quality(total - (level - PROFESSION_LEVEL))
    primary = (plan.characteristic or LABORER_CHARACTERISTIC).title()
    raised = " (+1 for the aura, p. 69)" if level > PROFESSION_LEVEL else ""
    result.notes.append(
        f"Labor Total {total} ({primary} + {profession}) against Profession "
        f"Level {level}{raised}: {quality} service (City & Guild p. 76)."
    )
    _quality_reputation(
        character,
        plan,
        profession,
        total,
        level,
        quality == "Shoddy",
        result,
    )


def _workshop_production(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    wm = multiplier(character)
    name = plan.title.strip()
    craft = subject_ability(plan)
    total = workshop_total(character, plan, craft)
    level = plan.book_level if plan.book_level is not None else 6
    total += _exert(saga, character, plan, rng, result, craft)
    penalty = work_virtues.aura_penalty(saga, character, craft)
    total += penalty
    quality = quality_for(total, level)
    lp = (
        characteristic(character, plan, "dexterity")
        + ability_level(character, craft)
        + penalty
    ) * wm
    result.labor_points = lp
    result.notes.append(
        f"Workshop Total {total} against Craft Level {level}: {quality} goods. "
        f"Labor Points {lp}."
    )
    if penalty:
        result.notes.append(
            f"Necessary Realm Aura for {craft}: {penalty} to the total and the "
            "Labor Points outside its aura."
        )
    if note := work_virtues.independent_note(character, craft):
        result.notes.append(note)
    _quality_reputation(
        character, plan, craft, total, level, quality == "Shoddy", result
    )
    if plan.quick:
        if ability_level(character, "Artes Liberales") < 1:
            result.notes.append("No craft manual: it needs Artes Liberales 1.")
        else:
            score = round_up(ability_level(character, craft) / MANUAL_DIVISOR)
            result.labor_points -= 1
            result.books.append(
                Book(
                    id=f"manual_{character.id}_{plan.year}_{plan.season.lower()}",
                    name=name or f"{craft} manual",
                    type="Other",
                    author=character.name,
                    owner_kind="character",
                    owner_id=character.id,
                    year_published=plan.year,
                    description=f"A craft manual on {craft}: +{score} to a "
                    "literate reader's Workshop Total (City & Guild).",
                )
            )
            result.notes.append(
                f"A craft manual written (+{score}), for 1 Labor Point."
            )


def _make_excellent_item(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """An excellent item: made in the one season if the Workshop Total
    reaches its Craft Level (15 at the basic level)."""
    name = plan.title.strip() or "an excellent item"
    craft = subject_ability(plan)
    level = plan.book_level if plan.book_level is not None else EXCELLENT_LEVEL
    total = workshop_total(character, plan, craft)
    total += _exert(saga, character, plan, rng, result, craft)
    bonus = excellent_bonus(total, level, ability_level(character, craft))
    # The standard goods' Craft Level the Reputation counts from: this
    # item's level moved down as excellent's 15 is from standard's 6.
    standard = level - (EXCELLENT_LEVEL - 6)
    if bonus is None:
        result.notes.append(
            f"Workshop Total {total} is below the Craft Level {level}: no "
            "excellent item this season."
        )
    else:
        result.progress.append(("item", name, 1, 1))
        result.notes.append(
            f"Workshop Total {total} against Craft Level {level}: {name} is "
            f"made, +{bonus} to a feature (City & Guild p. 69)."
        )
    _quality_reputation(character, plan, craft, total, standard, False, result)


def _improve_station(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """A season moving up: Poor to average (120 Labor Points), average to
    Wealthy (360); from Wealthy (1,080) to Poor in the next social class,
    whose Social Status the troupe changes by hand."""
    now = wealth(character)
    cost = STATION_COST[now]
    result.labor_points = -cost
    if now == "poor":
        result.remove_vfs.append(VirtueFlawInstance("vf_poor"))
        result.notes.append(f"Poor to average, for {cost} Labor Points.")
    elif now == "average":
        result.add_vfs.append(VirtueFlawInstance("vf_wealthy"))
        result.notes.append(f"Average to Wealthy, for {cost} Labor Points.")
    else:
        result.remove_vfs.append(VirtueFlawInstance("vf_wealthy"))
        result.add_vfs.append(VirtueFlawInstance("vf_poor"))
        result.notes.append(
            f"Wealthy to Poor in the next social class, for {cost} Labor "
            "Points: change the Social Status Virtue on the Virtues tab."
        )


def _make_wondrous_item(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """A wondrous item: each season the Workshop Total is over its Craft
    Level (12 + the effect's magnitude + its uses a day) adds the difference
    toward it, until the points equal the Craft Level (City & Guild pp.
    71-72)."""
    name = plan.title.strip() or "a wondrous item"
    craft = subject_ability(plan)
    level = plan.book_level if plan.book_level is not None else WONDROUS_BASE
    total = workshop_total(character, plan, craft)
    parts: list[str] = []
    exerted = _exert(saga, character, plan, rng, result, craft)
    if exerted:
        total += exerted
        parts.append(f"exertion +{exerted}")
    aura = wondrous_aura(character, plan)
    if aura:
        total += aura
        parts.append(f"aura {aura:+d}")
    if plan.site_aura is None:
        result.notes.append(
            "No aura entered where he works: none counted (City & Guild p. 72)."
        )
    helper = saga.character(plan.teacher_id) if plan.teacher_id else None
    if helper is not None:
        helped = round_down(ability_level(helper, craft) / 2)
        total += helped
        parts.append(f"{helper.name}'s help +{helped}")
    gained = max(0, total - level)
    result.progress.append(("item", name, level, gained))
    why = f" ({', '.join(parts)})" if parts else ""
    result.notes.append(
        f"Workshop Total {total}{why} - Craft Level {level} = {gained} toward it. "
        "One assistant at most (City & Guild p. 72): count no other in Other."
    )
    # Both Reputation points can come in one season: "any season" 6 or more
    # over the standard goods' Craft Level earns 1, and making a wondrous
    # item "also" grants 1 (City & Guild p. 74).
    _quality_reputation(character, plan, craft, total, STANDARD_LEVEL, False, result)
    held = kept_points(progress_of(character, "item", name), plan.season, plan.year)
    if gained and held + gained >= level:
        result.reputation_xp.append((trade(craft), 1))
        result.notes.append(
            f"A wondrous item made: 1 xp in the {trade(craft)} Reputation "
            "(City & Guild p. 74)."
        )
    if not any(vf.vf_id == TOUCHED_BY_REALM for vf in character.virtues_flaws):
        result.notes.append(
            "Mythic Farrier: horseshoes only, in the one Form chosen, their "
            "power on the horse or the ground it treads (Grogs p. 76)."
        )


def _merchant_venture(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    lp = plan.other_modifier
    result.labor_points = lp
    result.notes.append(f"Labor Points from the venture: {lp}.")


def _improve_workshop(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    name = plan.title.strip()
    step = name.lower()
    banked = 0
    if step == "innovation":
        cost = INNOVATION_COST[character.workshop_innovation + 1]
        result.innovation = 1
        banked = min(cost, banked_innovation(character))
        if banked:
            result.progress.append((INNOVATION_KIND, INNOVATION_BANK, 0, -banked))
    else:
        cost = RAW_MATERIALS_COST[character.workshop_raw_materials + 1]
        result.raw_materials = 1
    result.labor_points = -(cost - banked)
    result.notes.append(f"{step.title()} +1, for {cost} Labor Points.")
    if banked:
        result.notes.append(
            f"{banked} of them banked by inventions (City & Guild p. 74)."
        )


register(
    SimpleActivity(
        "working_season",
        "Working season (earn a living)",
        "Labor Points = (Characteristic + Craft/Profession) x wealth; "
        "Exposure 2 in the craft.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _working_season,
    needs_subject,
)
register(
    SimpleActivity(
        "workshop_production",
        "Craft workshop production",
        "Workshop Total against the Craft Level; items a season. Exposure 2.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _workshop_production,
    _craft_problems,
)
register(
    SimpleActivity(
        "improve_workshop",
        "Improve the workshop",
        "A season raising Innovation (100, 200, 300 Labor Points) or Raw "
        "Materials (50, 100, 150): no production; Practice.",
        CITY_GUILD,
        "919",
        4,
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _improve_workshop,
    _improve_workshop_problems,
)
register(
    SimpleActivity(
        "make_excellent_item",
        "Make an excellent item",
        "One season, if the Workshop Total reaches the Craft Level (15): +1 "
        "to a feature for every 3 points over it, at most Craft / 3 rounded "
        "up. Exposure 2.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _make_excellent_item,
)
register(
    SimpleActivity(
        "improve_station",
        "Improve wealth or status",
        "A season and Labor Points: Poor to average 120, average to Wealthy "
        "360, Wealthy to Poor in the next social class 1,080. No production.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _improve_station,
    _improve_station_problems,
)
register(
    SimpleActivity(
        "make_wondrous_item",
        "Make a wondrous item",
        "Touched by (Realm): the Workshop Total must beat the Craft Level (12 "
        "+ the effect's magnitude + its uses a day); the excess accumulates "
        "each season until the points equal the Craft Level, with no other "
        "workshop work. One effect: Range Personal or Touch, Duration up to "
        "Sun, Target Individual, of the two Forms chosen at creation; one "
        "assistant at most (City & Guild pp. 70-72). Exposure 2.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _make_wondrous_item,
    _wondrous_problems,
)
register(
    SimpleActivity(
        "repair_item",
        "Repair an item",
        "A season restoring an item. Exposure 2.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "merchant_venture",
        "Merchant venture, investment or legal action",
        "Labor Points or money, by the venture. Exposure 2.",
        CITY_GUILD,
        "919",
        who=COMPANIONS,
        group=groups.WORK,
    ),
    _merchant_venture,
)
