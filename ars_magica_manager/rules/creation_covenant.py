"""Covenant and laboratory creation checks.

A new covenant picks a Power Level (Low 0-300 Build Points, Medium
300-1250, High 1250-2500, Legendary 2500+), which also caps the level of
any Lab Text, Casting Tablet or enchanted effect (25, 40, none) and sets a
minimum age. The baseline is free: aura 3, one Typical income, a standard
laboratory per magus, about a grog and two covenfolk per magus. What the
covenant owns beyond that is priced in Build Points: its library, vis
sources and stocks, enchanted items, starting laboratories, and (with
Covenants in play) money. Its Boons and Hooks must balance.

A starting laboratory: each magus's first standard lab is free, a spare lab costs 50 (a
magus the covenant says goes without one refunds 50), plus Size x 20 and each lab Virtue
(Minor 10, Major 20). Its builder needs Magic Theory 3; Safety is Refinement less the
occupied Size; its Virtues less Flaws fit in Size + Refinement.

Rules: reference/rules-engine-reference.md §14 Covenant creation
baseline; Power level; Build Point costs; Boons and Hooks. §9 Setting up a
laboratory.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .. import book_value, catalog, sourcebooks
from .. import books as bk
from .. import covenant_templates as templates
from .. import enchanted_devices as ed
from .. import inhabitants as inh
from ..covenants import (
    MAJOR_POVERTY,
    MINOR_POVERTY,
    boon_hook_problems,
    covenant_boon_points,
    covenant_hook_points,
    unlinked_resource_hooks,
)
from ..laboratories import (
    LAB_SIZE_BUILD_POINTS,
    lab_base_safety,
    lab_build_points,
    lab_free_virtues,
)
from ..models import INCOME_TYPE_DEFAULTS, Covenant, Laboratory, Saga
from . import options as rule_options
from .creation_base import COVENANT_CHECKS, LABORATORY_CHECKS, Check, Record, check
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Accessible Power "
    "Level (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter"
    "_Six:_Covenants#Accessible_Power_Level)"
)
BOON_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Boons "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Six:"
    "_Covenants#Boons)"
)
LAB_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Build Point Cost "
    "for Starting Laboratories (https://www.redcap.org/page/Ars_Magica_"
    "Definitive_Edition,_Chapter_Eight:_Laboratory#Build_Point_Cost_for_"
    "Starting_Laboratories)"
)
SETUP_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Setting Up a "
    "Laboratory (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Eight:_Laboratory#Setting_Up_a_Laboratory)"
)


@dataclass(frozen=True)
class PowerLevel:
    name: str
    #: The Build Points it spends: at least `least`, at most `most` (None:
    #: no top).
    least: int
    most: int | None
    #: The highest level of any Lab Text, Casting Tablet or enchanted
    #: effect (None: no limit).
    max_level: int | None
    #: Years since the covenant was founded.
    min_age: int


POWER_LEVELS: tuple[PowerLevel, ...] = (
    PowerLevel("Low", 0, 300, 25, 0),
    PowerLevel("Medium", 300, 1250, 40, 10),
    PowerLevel("High", 1250, 2500, None, 50),
    PowerLevel("Legendary", 2500, None, None, 100),
)
POWER_BY_NAME = {p.name: p for p in POWER_LEVELS}


def band(power: PowerLevel) -> str:
    """ "300-1250", or "2500+"."""
    return (
        f"{power.least}-{power.most}" if power.most is not None else f"{power.least}+"
    )


def in_band(power: PowerLevel, points: int) -> bool:
    return points >= power.least and (power.most is None or points <= power.most)


VIS_SOURCE_BP = 5  # a pawn a year
VIS_STOCK_PAWNS = 5  # pawns for 1 BP
EFFECT_LEVELS = 5  # levels of an enchanted effect for 2 BP
MONEY_POUNDS = 10  # pounds for 1 BP (Covenants)
SPARE_LAB = 50
SIZE_BP = LAB_SIZE_BUILD_POINTS
BUILDER_MAGIC_THEORY = 3


@dataclass(frozen=True)
class Cost:
    """One line of a covenant's Build Points."""

    label: str
    points: int
    #: The Build tab's row it belongs to (a CATEGORIES entry).
    category: str = ""
    #: The record this line prices (a Book, vis Possession, EnchantedDevice,
    #: Laboratory or Inhabitant), or None for a pool, the spare labs or
    #: money.
    item: Any = field(default=None, compare=False, repr=False)


#: The covenant Build tab's rows, in order.
CATEGORIES: tuple[str, ...] = (
    "Art Summae",
    "Ability Summae",
    "Tractatus",
    "Lab Texts",
    "Casting Tablets",
    "Pictorial works",
    "Vis sources",
    "Vis stocks",
    "Enchanted items",
    "Laboratories",
    "Specialists",
    "Money",
)
_BOOK_CATEGORY = {
    "Art Summa": "Art Summae",
    "Ability Summa": "Ability Summae",
    "Tractatus": "Tractatus",
    "Lab Text": "Lab Texts",
    "Casting Tablet": "Casting Tablets",
}


def _covenant_labs(
    saga: Saga, covenant: Covenant, *, every: bool = False
) -> list[Laboratory]:
    """The covenant's starting laboratories (`every`: all of them)."""
    return [
        lab
        for lab in saga.laboratories
        if lab.covenant_id == covenant.id and (every or lab.starting)
    ]


def _magi(saga: Saga, covenant: Covenant) -> int:
    return sum(
        1 for c in saga.characters if c.covenant_id == covenant.id and c.type == "magus"
    )


def baseline_covenfolk_note(saga: Saga, covenant: Covenant) -> str:
    """The covenfolk the creation baseline gives for free (about one grog
    and two other covenfolk per magus), to add once the covenant is In
    Play."""
    magi = _magi(saga, covenant)
    if not magi:
        return (
            "The baseline gives about one grog and two other covenfolk per "
            "magus, free of Build Points."
        )
    return (
        f"The baseline gives about {magi} grog(s) and {2 * magi} other "
        "covenfolk (servants, craftsmen) for its "
        f"{magi} magi, free of Build Points: add them on the Inhabitants tab "
        "once the covenant is In Play."
    )


def lab_points(lab: Laboratory) -> int:
    """A laboratory's own Build Points (laboratories.lab_build_points)."""
    return lab_build_points(lab)


def without_lab(saga: Saga, covenant: Covenant) -> int:
    """Magi going without a laboratory (Covenant.magi_without_lab, at
    most the covenant's magi)."""
    return max(0, min(covenant.magi_without_lab, _magi(saga, covenant)))


def spare_labs(saga: Saga, covenant: Covenant, *, every: bool = False) -> int:
    """Starting labs beyond one free lab for each magus who has one (never
    negative: a magus whose lab isn't entered still has the free one)."""
    with_lab = _magi(saga, covenant) - without_lab(saga, covenant)
    return max(0, len(_covenant_labs(saga, covenant, every=every)) - with_lab)


def costs(saga: Saga, covenant: Covenant, *, every_lab: bool = False) -> list[Cost]:
    """What the covenant's Build Points went on, line by line. At creation
    only its starting laboratories count; `every_lab` counts all of them
    (the covenant's Build Point value in play)."""
    lines: list[Cost] = []
    library = [b for b in bk.books_owned_by(saga, "covenant", covenant.id)]
    for book in library:
        points = bk.cost(book, saga)
        if points:
            # "Lab Text: Pilum of Fire" is already named for its type.
            label = (
                book.name
                if book.name.startswith(book.type)
                else f"{book.type}: {book.name}"
            )
            lines.append(Cost(label, points, _BOOK_CATEGORY.get(book.type, ""), book))
    for book_type in bk.POOL_POINTS:
        pool = bk.pool(library, book_type, saga)
        if pool.levels:
            lines.append(
                Cost(
                    f"{_BOOK_CATEGORY[book_type]}: {pool.levels} levels"
                    + (f" ({pool.unspent} levels unspent)" if pool.unspent else ""),
                    pool.points,
                    _BOOK_CATEGORY[book_type],
                )
            )
    for subject in covenant.pictorial_works:
        lines.append(
            Cost(
                f"Pictorial works: {subject}",
                book_value.PICTORIAL_BP,
                "Pictorial works",
            )
        )
    for possession in covenant.possessions:
        if possession.kind == "vis_source" and possession.pawns:
            lines.append(
                Cost(
                    f"Vis source: {possession.name} ({possession.pawns} a year)",
                    VIS_SOURCE_BP * possession.pawns,
                    "Vis sources",
                    possession,
                )
            )
        elif possession.kind == "vis_store" and possession.pawns:
            lines.append(
                Cost(
                    f"Vis stock: {possession.name} ({possession.pawns} pawns)",
                    round_up(possession.pawns / VIS_STOCK_PAWNS),
                    "Vis stocks",
                    possession,
                )
            )
    for device in ed.held_by(saga, "covenant", covenant.id):
        for effect in device.effects:
            level = ed.modified_level(device, effect)
            lines.append(
                Cost(
                    f"Enchanted: {device.name}, {effect.name} (level {level})",
                    2 * round_up(level / EFFECT_LEVELS),
                    "Enchanted items",
                    device,
                )
            )
    for lab in _covenant_labs(saga, covenant, every=every_lab):
        points = lab_points(lab)
        if points:
            lines.append(Cost(f"Laboratory: {lab.name}", points, "Laboratories", lab))
    spare = spare_labs(saga, covenant, every=every_lab)
    if spare:
        lines.append(
            Cost(f"Spare laboratories ({spare})", SPARE_LAB * spare, "Laboratories")
        )
    none = without_lab(saga, covenant)
    if none and not every_lab:
        # A refund at creation only: it isn't part of a covenant's value.
        lines.append(
            Cost(
                f"Magi without a laboratory ({none})",
                -SPARE_LAB * none,
                "Laboratories",
            )
        )
    for person in covenant.inhabitants:
        points = specialist_cost(
            person.specialist_score,
            person.teacher_communication,
            person.teacher_teaching,
        )
        if points is not None and not person.departed:
            what = "Teacher" if person.teacher_teaching is not None else "Specialist"
            ability = f", {person.linked_ability}" if person.linked_ability else ""
            lines.append(
                Cost(f"{what}: {person.name}{ability}", points, "Specialists", person)
            )
    books_in_play = sourcebooks.saga_books(saga)
    wealth = covenant.economics.wealth
    if wealth and sourcebooks.in_play("Covenants", books_in_play):
        lines.append(
            Cost(f"Money ({wealth} pounds)", round_up(wealth / MONEY_POUNDS), "Money")
        )
    elif covenant.converted_pounds:
        # Without Covenants money isn't bought, but Build Points already
        # turned into money stay spent.
        pounds = covenant.converted_pounds
        lines.append(
            Cost(
                f"Money from Build Points left over ({pounds} pounds)",
                round_up(pounds / MONEY_POUNDS),
                "Money",
            )
        )
    return lines


def specialist_cost(
    score: int | None, communication: int | None = None, teaching: int | None = None
) -> int | None:
    """A bought specialist's Build Points: the score in the Ability used for
    the covenant; a teacher adds Communication + Teaching (the score is then
    the highest Ability taught). None for someone not bought."""
    if score is None:
        return None
    if teaching is None:
        return score
    return score + (communication or 0) + teaching


def spent(saga: Saga, covenant: Covenant) -> int:
    return sum(c.points for c in costs(saga, covenant))


def remaining(saga: Saga, covenant: Covenant) -> int:
    """Build Points the covenant has not spent (0 with no budget set)."""
    budget = covenant.build_points_budget
    if budget is None:
        return 0
    return max(budget - spent(saga, covenant), 0)


def leftover_note(saga: Saga, covenant: Covenant) -> str:
    """What moving to In Play does with unspent Build Points, for the
    confirmation ("" with none left)."""
    left = remaining(saga, covenant)
    if not left:
        return ""
    return (
        f"It has {left} Build Points left. Moving it to In Play turns them into "
        f"{left * MONEY_POUNDS} Mythic Pounds, added to its Wealth (one Build "
        f"Point buys {MONEY_POUNDS} pounds)."
    )


def convert_remaining(saga: Saga, covenant: Covenant) -> int:
    """Turn unspent Build Points into pounds in the covenant's Wealth, as it
    moves to In Play; the pounds added."""
    pounds = remaining(saga, covenant) * MONEY_POUNDS
    covenant.economics.wealth += pounds
    covenant.converted_pounds += pounds
    return pounds


def category_totals(found: list[Cost]) -> dict[str, int]:
    """Build Points by Build-tab row, every row present, in order."""
    totals = dict.fromkeys(CATEGORIES, 0)
    for cost in found:
        if cost.category in totals:
            totals[cost.category] += cost.points
    return totals


def record_initial(saga: Saga, covenant: Covenant) -> None:
    """Keep what the covenant's Build Points were spent on as it moves to
    In Play: the Build tab's Initial column."""
    covenant.initial_build_points = category_totals(costs(saga, covenant))


def over_level(saga: Saga, covenant: Covenant, max_level: int) -> list[str]:
    """Lab Texts, Casting Tablets and enchanted effects above `max_level`."""
    found = []
    for book in bk.books_owned_by(saga, "covenant", covenant.id):
        if book.type in bk.SPELL_TYPES:
            level = bk.level_of(book, saga) or 0
            if level > max_level:
                found.append(f"{book.name} ({level})")
    for device in ed.held_by(saga, "covenant", covenant.id):
        for effect in device.effects:
            level = ed.modified_level(device, effect)
            if level > max_level:
                found.append(f"{device.name}: {effect.name} ({level})")
    return found


def _c(step: str, label: str, ok: bool, detail: str, source=SOURCE, *, advice=False):
    status = "pass" if ok else ("advice" if advice else "warn")
    return Check(step, label, status, detail, source)


INCOME_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Covenant "
    "Finances, Baseline (https://www.redcap.org/page/Ars_Magica_Definitive_"
    "Edition,_Chapter_Six:_Covenants#Baseline_2)"
)
AURA_SOURCE = "Covenants, Chapter Two: Boons and Hooks, Faerie Aura"
MINOR_WEALTH = "covbh_boon_minor_wealth"
MAJOR_WEALTH = "covbh_boon_major_wealth"
SECONDARY_INCOME = "covbh_boon_minor_secondary_income"
FAERIE_AURA = "covbh_hook_minor_faerie_aura"
#: The starting income assumes six magi; with the optional rule a source
#: gains or loses this much a year per magus over or under six.
INCOME_MAGI = 6
INCOME_PER_MAGUS: dict[str, int] = {"Typical": 15, "Lesser": 6}


@dataclass(frozen=True)
class IncomeChoice:
    """A way to start the covenant's income: its label and each source's
    (type, pounds a year)."""

    label: str
    sources: tuple[tuple[str, int], ...]


def _income_amount(saga: Saga, covenant: Covenant, kind: str) -> int:
    amount = INCOME_TYPE_DEFAULTS[kind]
    if kind in INCOME_PER_MAGUS and rule_options.is_on(saga, "income_per_magus"):
        amount += INCOME_PER_MAGUS[kind] * (_magi(saga, covenant) - INCOME_MAGI)
    return max(amount, 0)


def income_choices(saga: Saga, covenant: Covenant) -> list[IncomeChoice]:
    """How the covenant may start its income: one Typical source, or two
    Lesser for the sake of diversity; a Wealth Boon upgrades the Typical
    source (Greater, Legendary), each Secondary Income Boon adds another
    Typical source, and a Poverty Hook allows one Lesser source (Minor) or
    none (Major)."""
    held = {bh.vf_id for bh in covenant.boons_hooks}
    if MAJOR_POVERTY in held:
        return [IncomeChoice("No source of income (Poverty, Major Hook)", ())]
    lesser = ("Lesser", _income_amount(saga, covenant, "Lesser"))
    if MINOR_POVERTY in held:
        return [IncomeChoice(f"One Lesser source ({lesser[1]} pounds)", (lesser,))]
    typical = ("Typical", _income_amount(saga, covenant, "Typical"))
    extra = sum(bh.vf_id == SECONDARY_INCOME for bh in covenant.boons_hooks)
    also = (typical,) * extra
    plus = f", plus {extra} Typical ({typical[1]} pounds)" if extra else ""
    if MAJOR_WEALTH in held or MINOR_WEALTH in held:
        kind = "Legendary" if MAJOR_WEALTH in held else "Greater"
        amount = _income_amount(saga, covenant, kind)
        return [
            IncomeChoice(
                f"One {kind} source ({amount} pounds){plus}", ((kind, amount), *also)
            )
        ]
    return [
        IncomeChoice(
            f"One Typical source ({typical[1]} pounds){plus}", (typical, *also)
        ),
        IncomeChoice(
            f"Two Lesser sources ({lesser[1]} pounds each){plus}",
            (lesser, lesser, *also),
        ),
    ]


def income_check(saga: Saga, covenant: Covenant) -> Check:
    """Whether the covenant's sources of income are one of its starting
    choices (by type)."""
    choices = income_choices(saga, covenant)
    have = sorted(s.type for s in covenant.economics.income_sources)
    ok = any(sorted(kind for kind, _ in c.sources) == have for c in choices)
    listed = ", ".join(have) if have else "none"
    return _c(
        "power",
        "Starting income: " + " or ".join(c.label for c in choices),
        ok,
        listed,
        INCOME_SOURCE,
        advice=True,
    )


@check("power", COVENANT_CHECKS)
def power_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Covenant)
    covenant = record
    power = POWER_BY_NAME.get(covenant.power_level)
    found = [
        _c(
            "power",
            "A Power Level is chosen",
            power is not None,
            covenant.power_level or "none",
        )
    ]
    found.append(income_check(saga, covenant))
    if power is None:
        return found
    if power.min_age:
        founded = covenant.year_founded
        years = saga.current_year - founded if founded is not None else None
        found.append(
            _c(
                "power",
                f"{power.name}: founded at least {power.min_age} years ago",
                years is not None and years >= power.min_age,
                f"{years} years" if years is not None else "set Year Founded",
            )
        )
    return found


@check("build_points", COVENANT_CHECKS)
def build_point_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Covenant)
    covenant = record
    power = POWER_BY_NAME.get(covenant.power_level)
    total = spent(saga, covenant)
    if power is None:
        return [
            _c(
                "build_points",
                "Build Points against a Power Level",
                False,
                f"{total} spent",
            )
        ]
    found = []
    budget = covenant.build_points_budget
    found.append(
        _c(
            "build_points",
            f"Build Points set within {power.name}'s {band(power)}",
            budget is not None and in_band(power, budget),
            f"{budget}" if budget is not None else "not set",
        )
    )
    if budget is not None:
        found.append(
            _c(
                "build_points",
                "Resources bought within the Build Points",
                total <= budget,
                f"{total} of {budget}"
                + (f", {total - budget} too many" if total > budget else ""),
            )
        )
        if total < budget:
            found.append(
                _c(
                    "build_points",
                    "Build Points spent",
                    False,
                    f"{budget - total} unspent",
                    advice=True,
                )
            )
    found += _template_checks(saga, covenant)
    if power.max_level is not None:
        over = over_level(saga, covenant, power.max_level)
        found.append(
            _c(
                "build_points",
                f"No text or effect above level {power.max_level}",
                not over,
                ", ".join(over) or "none above",
            )
        )
    return found


def _template_checks(saga: Saga, covenant: Covenant) -> list[Check]:
    """A base covenant's placeholders still to fill in, and the Lab Text
    and enchanted item levels it gives still to choose (advice)."""
    found = []
    books, vis = templates.placeholders(saga, covenant)
    if books or vis:
        parts = []
        if books:
            parts.append(f"{len(books)} book(s) need a subject")
        if vis:
            parts.append(f"{len(vis)} vis source(s) or stock(s) need an Art")
        found.append(
            _c(
                "build_points",
                "The base covenant's placeholders are filled in",
                False,
                ", ".join(parts),
                templates.SOURCE,
                advice=True,
            )
        )
    for allowance in templates.allowances(saga, covenant):
        found.append(
            _c(
                "build_points",
                f"The base covenant's {allowance.what} chosen",
                allowance.chosen >= allowance.levels,
                f"{allowance.chosen} of {allowance.levels} levels",
                templates.SOURCE,
                advice=True,
            )
        )
    return found


@check("boons_hooks", COVENANT_CHECKS)
def boon_hook_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Covenant)
    covenant = record
    boons_catalog = catalog.load_covenant_boon_hook_catalog_by_id()
    boons = covenant_boon_points(covenant, boons_catalog)
    hooks = covenant_hook_points(covenant, boons_catalog)
    found = [
        _c(
            "boons_hooks",
            "Boons cost no more than the Hooks give",
            boons <= hooks,
            f"{boons:g} Boon, {hooks:g} Hook points"
            + (f", {boons - hooks:g} too many" if boons > hooks else ""),
            BOON_SOURCE,
        )
    ]
    if boons < hooks:
        found.append(
            _c(
                "boons_hooks",
                "Hook points spent",
                False,
                f"{hooks - boons:g} unspent",
                BOON_SOURCE,
                advice=True,
            )
        )
    held = {bh.vf_id for bh in covenant.boons_hooks}
    realm = covenant.aura_realm or "Magic"
    if realm == "Faerie" or FAERIE_AURA in held:
        found.append(
            _c(
                "boons_hooks",
                "A Faerie aura comes with the Faerie Aura Hook",
                realm == "Faerie" and FAERIE_AURA in held,
                f"aura realm {realm}, "
                + (
                    "Faerie Aura taken"
                    if FAERIE_AURA in held
                    else "no Faerie Aura Hook"
                ),
                AURA_SOURCE,
            )
        )
    elif realm != "Magic":
        found.append(
            _c(
                "boons_hooks",
                "A Magic aura (the creation rules assume one)",
                False,
                f"aura realm {realm}",
                SOURCE,
                advice=True,
            )
        )
    unlinked = unlinked_resource_hooks(covenant, boons_catalog)
    if unlinked:
        found.append(
            _c(
                "boons_hooks",
                "Resource Hooks name the source they're about",
                False,
                ", ".join(unlinked) + " (e on its row, once the source exists)",
                BOON_SOURCE,
                advice=True,
            )
        )
    # What doesn't fit together: Poverty with Wealth, or with its income.
    for problem in boon_hook_problems(covenant, boons_catalog):
        found.append(
            _c(
                "boons_hooks",
                "Boons and Hooks fit together",
                False,
                problem,
                BOON_SOURCE,
            )
        )
    return found


STAFF_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Covenfolk "
    "Categories (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Six:_Covenants#Covenfolk_Categories)"
)


@check("finish", COVENANT_CHECKS)
def staff_checks(saga: Saga, record: Record) -> list[Check]:
    """The servants and teamsters the covenant needs for its inhabitants
    (advice: they cost no Build Points, but fewer than the minimum hurts
    how the covenant runs)."""
    assert isinstance(record, Covenant)
    covenant = record
    found = []
    for role, needed in (
        ("Servant", inh.minimum_servants(saga, covenant)),
        ("Teamster", inh.minimum_teamsters(saga, covenant)),
    ):
        have = inh.other_covenfolk_count(saga, covenant, role)
        short = f", {needed - have} too few" if have < needed else ""
        found.append(
            _c(
                "finish",
                f"Enough {role.lower()}s for its inhabitants",
                have >= needed,
                f"{have} of {needed}{short} (Other Covenfolk on the Inhabitants tab)",
                STAFF_SOURCE,
                advice=True,
            )
        )
    return found


# -- a starting laboratory --


@check("setup", LABORATORY_CHECKS)
def lab_setup_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Laboratory)
    lab = record
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    found = []
    owner = saga.character(lab.owner_id)
    if owner is not None:
        theory = next((a for a in owner.abilities if a.name == "Magic Theory"), None)
        level = theory.level if theory is not None else 0
        found.append(
            _c(
                "setup",
                f"Its builder has Magic Theory {BUILDER_MAGIC_THEORY}",
                level >= BUILDER_MAGIC_THEORY,
                f"{owner.name}: {level}",
                SETUP_SOURCE,
            )
        )
    else:
        found.append(
            _c(
                "setup",
                "Its builder (the owner) is chosen",
                False,
                "no owner",
                SETUP_SOURCE,
                advice=True,
            )
        )
    free = lab_free_virtues(lab, lab_catalog)
    limit = lab.characteristics.size + lab.characteristics.refinement
    found.append(
        _c(
            "setup",
            "Virtues less Flaws within Size + Refinement",
            free >= 0,
            f"room for {free:g} more (limit {limit})"
            if free >= 0
            else f"{-free:g} over (limit {limit})",
            SETUP_SOURCE,
        )
    )
    found.append(
        _c(
            "setup",
            "Safety is Refinement less occupied Size",
            True,
            f"{lab_base_safety(lab, lab_catalog):+g}",
            SETUP_SOURCE,
        )
    )
    if lab.starting:
        found.append(
            _c(
                "setup",
                "A starting lab's Build Points go to its covenant",
                True,
                f"{lab_points(lab)} (Size x {SIZE_BP}, Virtues)",
                LAB_SOURCE,
            )
        )
    return found
