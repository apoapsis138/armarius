"""Logic behind a covenant's Economics tab -- no UI in here.

Works out the covenant's finances from the rest of the sheet, following the
ArM5 "Covenant Finances" rules (SOURCE; reference/Economics.md): the points of
inhabitants, laboratories and weapons and armor, each category of yearly
expenditure, the cost savings from laborers, craftspeople and the like, and the
totals. Nothing here is stored; only what the user types lives in
`Covenant.economics`.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from . import catalog, storage
from . import inhabitants as inh
from . import possessions as pos
from .covenants import contested_now, covenant_modifiers
from .markup import aligned, escape, markdown_text, problem, todo
from .models import (
    INCOME_EFFECT_MULTIPLIERS,
    INCOME_TYPE_DEFAULTS,
    SANCTUM_USAGES,
    Covenant,
    CovenantBoonHookDef,
    CovenantDiaryEntry,
    Economics,
    EnchantedDevice,
    IncomeSource,
    Laboratory,
    Modifier,
    Saga,
)
from .rules import covenfolk, enchantment, grog_discipline, tme_books
from .rules.breakdown import Breakdown
from .rules.lab_stats import lab_characteristic_total
from .rules.rounding import round_away_from_zero, round_down
from .world import covenant_magi, takes_part_in_play

# --------------------------------------------------------------- the rules

SOURCE = (
    "Covenants, Chapter Five: Wealth & Poverty, pp. 56-71; fractions round away from "
    "zero (covenant finances)"
)

#: Points of one laboratory by its Upkeep score, from -5 to +5.
_LAB_POINTS = {
    -5: 1,
    -4: 2,
    -3: 3,
    -2: 5,
    -1: 7,
    0: 10,
    1: 15,
    2: 30,
    3: 60,
    4: 100,
    5: 150,
}

#: The multiplier of a sanctum's Usage on its laboratory's points (light,
#: standard, heavy).
USAGE_MULTIPLIERS: dict[str, float] = dict(zip(SANCTUM_USAGES, (0.5, 1.0, 1.5)))

#: Wages follow the covenant's salary (Loyalty > Money).
WAGE_MULTIPLIERS: dict[str, float] = {
    "No salary": 0.0,
    "Half salary": 0.5,
    "Standard salary": 1.0,
    "Generous salary": 1.5,
    "Lavish salary": 2.0,
}

#: A craftsperson's field of work -> (the expenditure row it saves on, the most
#: any one craft may save, as a share of that row's cost).
CRAFT_SAVINGS: dict[str, tuple[str, float]] = {
    "Building": ("buildings", 0.5),
    "Consumables": ("consumables", 0.2),
    "Laboratories": ("laboratories", 0.2),
    "Provisions": ("provisions", 0.2),
    "Weapons and Armor": ("weapons", 0.5),
    "Writing Materials": ("writing", 0.5),
}

#: Laborers may save at most half of the Provisions cost.
LABORER_LIMIT = 0.5
#: At a Prevailing Loyalty of -6 the covenfolk's productivity is halved
#: (inhabitants.PRODUCTIVITY_SOURCE).
PRODUCTIVITY_HALVED = 0.5
#: Writing materials: a pound a year for every magus, scribe, bookbinder or
#: illuminator (DE p. 194). Binders and illuminators are craftspeople
#: working on Books; a scribe is a specialist (DE p. 190), known by the
#: Ability they serve with or their responsibility.
WRITING_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Writing Materials, "
    "p. 194; Covenfolk Categories, p. 190"
)
_BOOK_WORDS = ("scribe", "binder", "illuminat", "copyist")


def is_book_specialist(entry: covenfolk.InhabitantEntry) -> bool:
    """A specialist who writes or makes books: Profession: Scribe (or a
    bookbinding or illumination Ability), or a responsibility naming it."""
    text = f"{entry.linked_ability} {entry.responsibility}".casefold()
    return any(word in text for word in _BOOK_WORDS)


def upkeep_points(score: int) -> int:
    """Points of a laboratory with this Upkeep score. Beyond +5 it is ten times
    the experience needed to buy an Art of that score (n * (n + 1) / 2)."""
    if score <= -5:
        return _LAB_POINTS[-5]
    if score <= 5:
        return _LAB_POINTS[score]
    return 5 * score * (score + 1)


def laboratory_points(saga: Saga, covenant: Covenant) -> int:
    """Points of Laboratories: for each sanctum, its laboratory's Upkeep score
    (a manual sanctum uses the Upkeep typed on it, blank counting as 0) turned
    into points, times its Usage's multiplier."""
    lab_catalog = catalog.load_lab_virtue_flaw_catalog_by_id()
    total = 0.0
    for entry in pos.entries_for_kind(saga, covenant, "sanctum"):
        if entry.lab is not None:
            score = lab_characteristic_total(entry.lab, lab_catalog, "upkeep", saga)[3]
        else:
            score = entry.upkeep or 0
        total += upkeep_points(score) * USAGE_MULTIPLIERS.get(entry.usage, 1.0)
    return round_away_from_zero(total)


def neglected_laboratories(saga: Saga, covenant: Covenant) -> list[Laboratory]:
    """The covenant's laboratories left unmaintained when it closes a year
    broke (Wealth below 0): after two seasons of neglect each gains a Flaw,
    or loses a Virtue, that lowers its Upkeep (DE p. 288). Which one is the
    troupe's choice, so they are named, not changed."""
    if covenant.economics.wealth >= 0:
        return []
    return [
        entry.lab
        for entry in pos.entries_for_kind(saga, covenant, "sanctum")
        if entry.lab is not None
    ]


def craft_saving_each(entry: covenfolk.InhabitantEntry) -> int:
    """What one craftsperson saves a year: a rare one their skill, a common one
    one plus half of it, rounded down."""
    skill = entry.skill_value
    return skill if entry.rare else 1 + round_down(skill / 2)


# ------------------------------------------------------------------ figures


@dataclass
class Row:
    """One row of the Yearly Expenditure or Cost Savings table. `first` is the
    Cost (expenditure) or the Quantity (savings). Whole numbers throughout --
    see round_away_from_zero()."""

    key: str
    name: str
    rule: str
    first: int
    savings: int
    notes: str
    basis: str = ""
    note: str = ""  # a short tag shown by the name, e.g. "x1.5"
    #: A warning worked out from the figures, shown in the error colour ahead of the notes
    #: (the Emergency Savings row's deficit / broke status).
    status: str = ""
    #: Names of the `Economics` attributes the user types for this row.
    typed: tuple[str, ...] = ()
    #: The most any one craft may save on this row, if a craft may.
    cap: int | None = None


@dataclass(frozen=True)
class CraftLine:
    """One craft's share of the Cost Savings: what its people's work is
    worth, the cap on that craft, and what it saves."""

    name: str
    row: str
    worth: int
    cap: int | None
    saves: int
    note: str


@dataclass
class Summary:
    inhabitant_points: int
    laboratory_points: int
    gear_points: int
    wealth: int
    income: int
    expenditure: list[Row]
    savings: list[Row]
    before_savings: int
    cost_savings: int
    total_expenditure: int
    surplus_deficit: int  # Total Income - Total Expenditure
    crafts: list[CraftLine]


#: The expenditure rows worked out from the covenant: (key, name, rule).
_CALCULATED_ROWS: tuple[tuple[str, str, str], ...] = (
    (
        "buildings",
        "Buildings",
        "1 pound per 10 pts Inhabitants, +2/+5 per Minor/Major building "
        "Boon (50% per craft)",
    ),
    ("consumables", "Consumables", "2 pounds per 10 pts Inhabitants (20% per craft)"),
    ("laboratories", "Laboratories", "1 pound per 10 pts Laboratories (20% per craft)"),
    (
        "provisions",
        "Provisions",
        "5 pounds per 10 pts Inhabitants (50% laborers + 20% per craft)",
    ),
    ("wages", "Wages", "2 pounds per 10 pts Inhabitants, times the salary multiplier"),
    ("weapons", "Weapons", "1 pound per 320 pts Weapons and Armor (50% per craft)"),
    (
        "writing",
        "Writing Materials",
        "1 pound per Magus, scribe, bookbinder or illuminator (50% per craft)",
    ),
)

#: The expenditure rows the user types: (key, name, rule, Economics attribute).
_TYPED_EXPENDITURE_ROWS: tuple[tuple[str, str, str, str], ...] = (
    ("tithes", "Tithes", "Debts and taxes", "tithes"),
    ("inflation", "Inflation", "Increases yearly", "inflation"),
    (
        "sundry",
        "Sundry",
        "At least 1 pound of sundries every year, and the year's purchases",
        "sundry",
    ),
)


def _typed_row(
    eco: Economics,
    key: str,
    name: str,
    rule: str,
    attribute: str,
    *,
    savings: bool = False,
) -> Row:
    """A row whose figure the user types: the Cost of an expenditure row, or
    the Savings of a savings row."""
    value = getattr(eco, attribute)
    first, saved = (0, value) if savings else (value, 0)
    return Row(
        key,
        name,
        rule,
        first,
        saved,
        eco.notes.get(key, ""),
        "typed",
        typed=(attribute,),
    )


def craft_cap(limit: float, cost: float) -> int:
    """The most one craft may save on a row: its share of the row's cost,
    in whole pounds rounded down, as Covenants' worked example does
    (p. 68: 20% of 32 pounds is 6 per craft, 50% of 9 is 4)."""
    return round_down(limit * cost)


def _craft_of(index: int, entry: covenfolk.InhabitantEntry) -> tuple[str, str]:
    """The craft an entry belongs to: a field plus the Ability or work its
    people share."""
    craft = (entry.linked_ability or entry.responsibility).strip().lower()
    return entry.field_of_work, craft or f"#{index}"


def _craft_worth(
    craftspeople: list[covenfolk.InhabitantEntry],
) -> dict[tuple[str, str], float]:
    """What each saving craft's people are worth a year, before its cap."""
    worth: dict[tuple[str, str], float] = {}
    for index, entry in enumerate(craftspeople):
        if entry.field_of_work in CRAFT_SAVINGS:
            key = _craft_of(index, entry)
            worth[key] = worth.get(key, 0.0) + (
                craft_saving_each(entry) * entry.quantity
            )
    return worth


def _craft_lines(
    craftspeople: list[covenfolk.InhabitantEntry], costs: dict[str, float]
) -> list[CraftLine]:
    """Each craft as Cost Savings counts it, those that save nothing too."""
    row_names = {key: name for key, name, _ in _CALCULATED_ROWS}
    worth = _craft_worth(craftspeople)
    people: dict[tuple[str, str], list[str]] = {}
    for index, entry in enumerate(craftspeople):
        people.setdefault(_craft_of(index, entry), []).append(
            f"{entry.name or '(unnamed)'}, "
            f"{entry.responsibility or entry.linked_ability} {entry.skill_value}"
        )
    lines = []
    for key, names in people.items():
        name = "; ".join(names)
        if key not in worth:
            lines.append(
                CraftLine(name, key[0] or "None", 0, None, 0, "Saves no costs")
            )
            continue
        row_key, limit = CRAFT_SAVINGS[key[0]]
        value = round_away_from_zero(worth[key])
        cap = craft_cap(limit, costs[row_key])
        spare = value - cap
        note = (
            f"£{spare} over the cap: another {row_names[row_key]} craft could use it"
            if spare > 0
            else ""
        )
        lines.append(
            CraftLine(name, row_names[row_key], value, cap, min(value, cap), note)
        )
    return lines


def entry_savings(saga: Saga, covenant: Covenant) -> list[str]:
    """What each craftsperson entry saves a year, in the craftspeople's list
    order: its worth, or the cap when its craft's cap cuts it."""
    craftspeople = covenfolk.entries_for_kind(saga, covenant, "craftsperson")
    caps = {r.key: r.cap or 0 for r in summarize(saga, covenant).expenditure}
    worth = _craft_worth(craftspeople)
    sharing: dict[tuple[str, str], int] = {}
    for index, entry in enumerate(craftspeople):
        key = _craft_of(index, entry)
        sharing[key] = sharing.get(key, 0) + 1
    shown = []
    for index, entry in enumerate(craftspeople):
        if entry.field_of_work not in CRAFT_SAVINGS:
            shown.append("0")
            continue
        key = _craft_of(index, entry)
        cap = caps[CRAFT_SAVINGS[entry.field_of_work][0]]
        each = craft_saving_each(entry) * entry.quantity
        if round_away_from_zero(worth[key]) <= cap:
            shown.append(str(each))
        elif sharing[key] == 1:
            shown.append(f"{cap} (cap)")
        else:
            shown.append(f"{each} (craft capped at {cap})")
    return shown


def _labor_savings(
    saga: Saga,
    covenant: Covenant,
    craftspeople: list[covenfolk.InhabitantEntry],
    costs: dict[str, float],
) -> tuple[int, float, int, dict[str, float]]:
    """(laborers, their savings, craftspeople counted, craft savings per
    expenditure row), each within its limit of the row's cost."""
    # Craftspeople: each craft (a field plus the Ability or work they share)
    # saves at most its limit of that category's cost.
    craftsmen = sum(
        e.quantity for e in craftspeople if e.field_of_work in CRAFT_SAVINGS
    )
    craft_by_row: dict[str, float] = {}
    for (field_of_work, _), amount in _craft_worth(craftspeople).items():
        row_key, limit = CRAFT_SAVINGS[field_of_work]
        craft_by_row[row_key] = craft_by_row.get(row_key, 0.0) + min(
            amount, craft_cap(limit, costs[row_key])
        )

    laborers = covenfolk.other_covenfolk_count(saga, covenant, "Laborer")
    laborer_savings = min(float(laborers), LABORER_LIMIT * costs["provisions"])
    craft_savings: dict[str, float] = {}
    for row_key, cost in costs.items():
        room = cost - (laborer_savings if row_key == "provisions" else 0.0)
        craft_savings[row_key] = min(craft_by_row.get(row_key, 0.0), max(room, 0.0))
    return laborers, laborer_savings, craftsmen, craft_savings


#: The Magic row's rule (Covenants p. 67; Transforming Mythic Europe pp.
#: 120-121).
MAGIC_RULE = (
    "1 pound a magnitude of each device doing covenfolk's work, 5 a magnitude "
    "of each Ritual cast this year (with the laborers, at most 50% of "
    "Provisions); bread from magical grain; and any typed"
)


def covenant_devices(saga: Saga, covenant: Covenant) -> list[EnchantedDevice]:
    """The enchanted devices the covenant holds: those that may do its
    covenfolk's work."""
    return enchantment.held_by(saga, "covenant", covenant.id)


def saving_devices(saga: Saga, covenant: Covenant) -> list[EnchantedDevice]:
    """The covenant's devices the troupe has marked as doing covenfolk's
    work (a device given away stops counting)."""
    chosen = set(covenant.economics.saving_devices)
    return [d for d in covenant_devices(saga, covenant) if d.id in chosen]


def magic_breakdown(
    saga: Saga,
    covenant: Covenant,
    people: int,
    provisions_room: float,
    labor_room: float | None = None,
) -> Breakdown:
    """How the Magic row's savings are made up (rules.tme_books): its
    devices and Rituals within `labor_room`, what the laborers' half of
    the Provisions leaves (Covenants p. 67)."""
    eco = covenant.economics
    return tme_books.magic_savings(
        eco.magic_savings,
        saving_devices(saga, covenant),
        eco.ritual_magnitudes,
        points=people,
        grain=eco.magic_grain,
        care=eco.grain_care,
        share=eco.bread_share,
        provisions_room=provisions_room,
        labor_room=labor_room,
    )


def _magic_row(
    saga: Saga,
    covenant: Covenant,
    people: int,
    provisions_room: float,
    labor_room: float | None = None,
) -> Row:
    """The Magic row: the typed pounds and what the covenant's magic saves,
    its working shown as the basis."""
    eco = covenant.economics
    working = magic_breakdown(saga, covenant, people, provisions_room, labor_room)
    return Row(
        "magic",
        "Magic",
        MAGIC_RULE,
        0,
        round_away_from_zero(working.total),
        eco.notes.get("magic", ""),
        tme_books.breakdown_text(working) or "typed",
        typed=("magic_savings",),
    )


def _basis_texts(
    covenant: Covenant,
    people: int,
    labs: int,
    gear: int,
    wage_multiplier: float,
    rewarded_pay: float,
    building_boons: Sequence[tuple[CovenantBoonHookDef, Modifier]],
    writers: tuple[int, int, int],
) -> dict[str, str]:
    """The working shown beside each calculated row: what its Cost is made of.
    `writers` are the magi, book craftspeople and scribe specialists."""
    eco = covenant.economics
    magi, book_crafts, scribes = writers
    return {
        "buildings": f"{people} pts of inhabitants / 10"
        + (
            " + "
            + ", ".join(
                f"{entry.name} {modifier.amount:+g}"
                for entry, modifier in building_boons
            )
            if building_boons
            else ""
        ),
        "consumables": f"{people} pts of inhabitants x 2 / 10",
        "laboratories": f"{labs} pts of laboratories / 10",
        "provisions": f"{people} pts of inhabitants x 5 / 10",
        "wages": f"{people} pts of inhabitants x 2 / 10 x {wage_multiplier:g} "
        f"({covenant.loyalty.money}, from Loyalty)"
        + (f" + {eco.soldier_pay} for soldiers' daily pence" if eco.soldier_pay else "")
        + (
            f" + {covenant.loyalty.pensioners} pensioner(s) at half Wages"
            if covenant.loyalty.pension and covenant.loyalty.pensioners
            else ""
        )
        + (
            f" {rewarded_pay:+.2f} for Pay and a Half and retirees"
            if rewarded_pay
            else ""
        ),
        "weapons": f"{gear} pts of weapons and armor / 320",
        "writing": f"{magi} magi + {book_crafts} book craftspeople"
        + (f" + {scribes} scribe specialist(s)" if scribes else ""),
    }


def _labor_rows(
    eco: Economics,
    laborers: int,
    laborer_savings: float,
    craftsmen: int,
    craft_savings: Mapping[str, float],
    productivity: str,
) -> list[Row]:
    """The Laborers and Craftspeople rows of the savings."""
    return [
        Row(
            "laborers",
            "Laborers",
            "1 pound per person (at most 50% of Provisions)",
            laborers,
            round_away_from_zero(laborer_savings),
            eco.notes.get("laborers", ""),
            "Laborer-tagged entries on the Other Covenfolk list"
            + (f"; {productivity}" if productivity else ""),
        ),
        Row(
            "craftspeople",
            "Craftspeople",
            "1 + (Ability / 2) pounds each, or the Ability if rare; each craft "
            "saves at most its limit of the category",
            craftsmen,
            round_away_from_zero(sum(craft_savings.values())),
            eco.notes.get("craftspeople", ""),
            "Craftspeople with a field of work (Books saves nothing)"
            + (f"; {productivity}" if productivity else ""),
        ),
    ]


def income_now(saga: Saga, source: IncomeSource, loyalty: int) -> float:
    """What a source gives this year. A contested one gives nothing until
    it is secured; one the covenfolk work for is halved with their
    productivity."""
    if contested_now(source, saga.current_year):
        return 0
    if source.covenfolk_work and loyalty <= -inh.PRODUCTIVITY_LOYALTY:
        return source.current_income * PRODUCTIVITY_HALVED
    return source.current_income


def _income(saga: Saga, eco: Economics, loyalty: int) -> int:
    """The year's income."""
    return round_away_from_zero(
        sum(income_now(saga, s, loyalty) for s in eco.income_sources)
    )


def purchases_total(eco: Economics) -> int:
    """The year's purchases in whole pounds, as they go onto Sundry."""
    return round_away_from_zero(sum(p.pounds for p in eco.purchases))


def summarize(saga: Saga, covenant: Covenant) -> Summary:
    """The covenant's year: what each row costs and saves, and the surplus or
    deficit left."""
    eco = covenant.economics
    people = covenfolk.inhabitant_points(saga, covenant)
    labs = laboratory_points(saga, covenant)
    gear = pos.gear_points(saga, covenant)
    wage_multiplier = WAGE_MULTIPLIERS.get(covenant.loyalty.money, 1.0)
    # Pay and a Half, and retirees' pensions or rent (Grogs pp. 23-26).
    rewarded_pay = grog_discipline.wage_adjustment(saga, covenant, wage_multiplier)
    magi = covenfolk.headcount(covenfolk.entries_for_kind(saga, covenant, "magus"))
    craftspeople = covenfolk.entries_for_kind(saga, covenant, "craftsperson")
    book_crafts = sum(e.quantity for e in craftspeople if e.field_of_work == "Books")
    scribes = sum(
        e.quantity
        for e in covenfolk.entries_for_kind(saga, covenant, "specialist")
        if is_book_specialist(e)
    )

    # Boons that add to the size, magnificence or quantity of the covenant's
    # buildings or fortifications: +2 per Minor, +5 per Major, carried on the
    # Boons themselves as covenant_expense/buildings modifiers (each instance
    # counts, so a Boon taken twice adds twice).
    boon_catalog = catalog.load_covenant_boon_hook_catalog_by_id()
    building_boons = covenant_modifiers(
        covenant, boon_catalog, "covenant_expense", "buildings"
    )
    building_surcharge = sum(m.amount or 0 for _, m in building_boons)

    costs = {
        "buildings": people / 10 + building_surcharge,
        "consumables": people * 2 / 10,
        "laboratories": labs / 10,
        "provisions": people * 5 / 10,
        # A pound for each penny paid daily to professional soldiers, and
        # half Wages (1 point of covenfolk) for each pensioner.
        "wages": people * 2 / 10 * wage_multiplier
        + eco.soldier_pay
        + (covenant.loyalty.pensioners * 2 / 10 / 2 if covenant.loyalty.pension else 0)
        + rewarded_pay,
        "weapons": gear / 320,
        "writing": float(magi + book_crafts + scribes),
    }
    laborers, laborer_savings, craftsmen, craft_savings = _labor_savings(
        saga, covenant, craftspeople, costs
    )
    # At a Prevailing Loyalty of -6 the savings that rely on covenfolk are
    # halved; at +6 productivity rises by no set amount (only noted).
    loyalty = inh.prevailing_loyalty(saga, covenant)
    productivity = inh.productivity_note(loyalty)
    if loyalty <= -inh.PRODUCTIVITY_LOYALTY:
        laborer_savings *= PRODUCTIVITY_HALVED
        craft_savings = {k: v * PRODUCTIVITY_HALVED for k, v in craft_savings.items()}
    row_savings = {
        key: craft_savings[key] + (laborer_savings if key == "provisions" else 0.0)
        for key in costs
    }

    # Round every row's final Cost/Savings to a whole number here (the ratios
    # above stay precise floats so the craft/laborer-limit math is exact); a
    # Row's `first`/`savings` are always integers from this point on, so
    # summing them can't drift from summing the already-rounded numbers.
    cost = {k: round_away_from_zero(v) for k, v in costs.items()}
    saved = {k: round_away_from_zero(v) for k, v in row_savings.items()}

    basis = _basis_texts(
        covenant,
        people,
        labs,
        gear,
        wage_multiplier,
        rewarded_pay,
        building_boons,
        (magi, book_crafts, scribes),
    )
    caps = {
        row_key: craft_cap(limit, costs[row_key])
        for row_key, limit in CRAFT_SAVINGS.values()
    }
    expenditure = [
        Row(
            key,
            name,
            rule,
            cost[key],
            saved[key],
            eco.notes.get(key, ""),
            basis[key],
            note=f"x{wage_multiplier:g}" if key == "wages" else "",
            cap=caps.get(key),
        )
        for key, name, rule in _CALCULATED_ROWS
    ] + [_typed_row(eco, *row) for row in _TYPED_EXPENDITURE_ROWS]
    sundry = next(row for row in expenditure if row.key == "sundry")
    sundry.first += purchases_total(eco)

    savings = [
        *_labor_rows(
            eco, laborers, laborer_savings, craftsmen, craft_savings, productivity
        ),
        # Magic doing laborers' work shares their half of the Provisions
        # (Covenants p. 67).
        _magic_row(
            saga,
            covenant,
            people,
            cost["provisions"] - saved["provisions"],
            LABORER_LIMIT * costs["provisions"] - laborer_savings,
        ),
        _typed_row(
            eco,
            "emergency_savings",
            "Emergency Savings",
            "Drawn from Wealth to cover a deficit (press e), or entered by hand",
            "emergency_savings",
            savings=True,
        ),
    ]

    before = sum(row.first for row in expenditure)
    # Laborer and craft savings sit in the expenditure rows; Magic and
    # Emergency Savings aren't tied to a category, so they only reduce the
    # total.
    magic = next(r for r in savings if r.key == "magic")
    cost_savings = sum(saved.values()) + magic.savings + eco.emergency_savings
    income = _income(saga, eco, loyalty)
    total_expenditure = before - cost_savings
    surplus_deficit = income - total_expenditure
    emergency = next(r for r in savings if r.key == "emergency_savings")
    emergency.status = emergency_status(surplus_deficit, eco.wealth)
    return Summary(
        inhabitant_points=people,
        laboratory_points=labs,
        gear_points=gear,
        wealth=eco.wealth,
        income=income,
        expenditure=expenditure,
        savings=savings,
        before_savings=before,
        cost_savings=cost_savings,
        total_expenditure=total_expenditure,
        surplus_deficit=surplus_deficit,
        crafts=_craft_lines(craftspeople, costs),
    )


# ----------------------------------------------------- deficits and the year

DEFICIT_STATUS = "Covenant operating at a deficit"
BROKE_STATUS = (
    "Covenant is broke - see rulebook for narrative and mechanical consequences"
)


#: The expenditure a covenant in trouble may leave unpaid (DE p. 196).
NEGLECTED_ROWS = ("buildings", "laboratories", "weapons")

#: A row of the ways out of a deficit: what to do, what it saves, its price.
WayOut = tuple[str, str, str]

#: Magi who give up their better living cost 3 points each (DE p. 190).
IMPOVERISHED_MAGUS_POINTS = 3
#: A miserly salary: half Wages (Covenants p. 38).
MISERLY_SALARY = "Half salary"


def ways_out(saga: Saga, covenant: Covenant, summary: Summary) -> list[WayOut]:
    """How a covenant short of silver may cut its outgoings (DE pp. 195-196),
    with this covenant's figures where the book gives a way to work them
    out. Nothing unless Wealth can't cover the deficit."""
    if summary.wealth + summary.surplus_deficit >= 0:
        return []
    ways: list[WayOut] = []
    multiplier = WAGE_MULTIPLIERS.get(covenant.loyalty.money, 1.0)
    miserly = WAGE_MULTIPLIERS[MISERLY_SALARY]
    if multiplier > miserly:
        points = inh.base_loyalty(saga, covenant) + inh.total_modifiers(saga, covenant)
        lost = inh.MONEY_LOYALTY_POINTS.get(
            covenant.loyalty.money, 0
        ) - inh.MONEY_LOYALTY_POINTS.get(MISERLY_SALARY, 0)
        saved = summary.inhabitant_points * 2 / 10 * (multiplier - miserly)
        ways.append(
            (
                "Miserly wages",
                f"about £{round_down(saved)}",
                f"-{lost} Loyalty points: Prevailing "
                f"{inh.prevailing_loyalty_score(points):+d} falls to "
                f"{inh.prevailing_loyalty_score(points - lost):+d}",
            )
        )
    magi = covenfolk.headcount(covenfolk.entries_for_kind(saga, covenant, "magus"))
    spare = covenfolk.kind_points("magus", covenant) - IMPOVERISHED_MAGUS_POINTS
    if magi and spare > 0:
        ways.append(
            (
                "Magi give up their comforts",
                f"about £{magi * spare}",
                "No better Living Conditions; as low as covenfolk, a poor "
                "Reputation spreads",
            )
        )
    ways.append(
        (
            "Let covenfolk go",
            "varies",
            "Disgruntled vagabonds with a grudge; mind the Servants and "
            "Teamsters needed",
        )
    )
    largest = max(r.first for r in summary.expenditure if r.key in NEGLECTED_ROWS)
    ways.append(
        (
            "Neglect a whole category",
            f"up to £{largest}",
            "Buildings, Laboratories or Weapons go unmaintained",
        )
    )
    return ways


def emergency_status(surplus_deficit: int, wealth: int) -> str:
    """The Emergency Savings row's warning: none without a deficit; broke when
    Wealth can't cover the deficit; otherwise a plain deficit."""
    if surplus_deficit >= 0:
        return ""
    return BROKE_STATUS if wealth < -surplus_deficit else DEFICIT_STATUS


def emergency_draw(summary: Summary) -> int:
    """How much drawing from Wealth would put into Emergency Savings: the
    whole deficit, or all the Wealth there is if that's less."""
    if summary.surplus_deficit >= 0:
        return 0
    return max(0, min(-summary.surplus_deficit, summary.wealth))


def draw_from_wealth(covenant: Covenant, amount: int) -> None:
    """Move `amount` pounds from Wealth into this year's Emergency Savings."""
    covenant.economics.emergency_savings += amount
    covenant.economics.wealth -= amount


def inflation_rise(eco: Economics, spent: int) -> int:
    """What a year's spending adds to Inflation: a pound per hundred, unless
    spending fell or this is the first year on record (DE p. 193)."""
    if eco.last_expenditure is None or spent < eco.last_expenditure:
        return 0
    return round_down(spent / INFLATION_PER)


def _file_purchases(saga: Saga, covenant: Covenant) -> None:
    """The year's purchases into the Diary, leaving the list empty."""
    eco = covenant.economics
    for purchase in eco.purchases:
        covenant.diary.append(
            CovenantDiaryEntry(
                saga.current_year,
                purchase.season,
                purchase.name,
                purchase.note or purchase.kind,
                category="Purchases & Sales",
                pounds=-purchase.pounds,
            )
        )
    eco.purchases = []


def close_year(saga: Saga, covenant: Covenant) -> int:
    """The end of the year (Winter -> Spring): add the year's surplus to
    Wealth, or take a deficit the Emergency Savings didn't cover from it
    (DE p. 189: "subtract it from the covenant's stores"; letting Wealth
    fall below 0, the covenant broke, is a house rule); grow
    inflation by a pound per hundred of the year's expenditure, unless
    spending fell (DE p. 193); start the new year's Emergency Savings at 0.
    Returns the change to Wealth."""
    summary = summarize(saga, covenant)
    eco = covenant.economics
    change = summary.surplus_deficit
    eco.wealth += change
    spent = summary.total_expenditure
    eco.inflation += inflation_rise(eco, spent)
    eco.last_expenditure = spent
    eco.emergency_savings = 0
    _file_purchases(saga, covenant)
    # The year's Ritual castings are spent; the store of magical grain is
    # eaten and rots (Transforming Mythic Europe p. 121).
    eco.ritual_magnitudes = 0
    if eco.magic_grain:
        eco.magic_grain = tme_books.grain_after_year(
            eco.magic_grain, summary.inhabitant_points, eco.grain_care
        )
    return change


# --------------------------------------------------------------------- text


def money(value: float) -> str:
    """A pounds or points figure as a whole number (see
    rounding.round_away_from_zero) -- safe to call on an already-rounded int
    too."""
    return str(round_away_from_zero(value))


def wealth_texts(summary: Summary) -> tuple[str, str]:
    """The Wealth section as two columns."""
    left = aligned(
        [
            ("Points of Inhabitants", money(summary.inhabitant_points)),
            ("Points of Laboratories", money(summary.laboratory_points)),
            ("Points of Weapons and Armor", money(summary.gear_points)),
            ("Wealth", str(summary.wealth)),
        ]
    )
    right = aligned(
        [
            ("Total Income", money(summary.income)),
            ("Expenditure (Before Cost Savings)", money(summary.before_savings)),
            ("Cost Savings", money(summary.cost_savings)),
            ("Total Expenditure", money(summary.total_expenditure)),
            (
                "Surplus/Deficit",
                (
                    f"[$text-error]{summary.surplus_deficit:+d}[/]"
                    if summary.surplus_deficit < 0
                    else f"{summary.surplus_deficit:+d}"
                ),
            ),
        ]
    )
    return left, right


_NAME_WIDTH = 20
_FIRST_WIDTH = 8
_SAVINGS_WIDTH = 9
_NOTES_WIDTH = 34
#: A status warning may run longer than a note (it fits a 140-wide terminal).
_STATUS_WIDTH = 48


def table_header(first_title: str) -> str:
    """The column titles above a table's rows; the two-character indent is the
    list's selector marker."""
    return (
        f"  {'':<{_NAME_WIDTH}}{first_title:>{_FIRST_WIDTH}}"
        f"{'Savings':>{_SAVINGS_WIDTH}}  Notes"
    )


def row_label(row: Row) -> str:
    """One table row (markup), columns lined up with `table_header`. A status
    warning takes the Notes column, in the error colour (the notes are in the panel)."""
    name = row.name + (f" ({row.note})" if row.note else "")
    notes = (row.status or row.notes).replace("\n", " ")
    width = _STATUS_WIDTH if row.status else _NOTES_WIDTH
    if len(notes) > width:
        notes = notes[: width - 1] + "…"
    notes = f"[$text-error]{escape(notes)}[/]" if row.status else escape(notes)
    return (
        f"{escape(name.ljust(_NAME_WIDTH))}{money(row.first):>{_FIRST_WIDTH}}"
        f"{money(row.savings):>{_SAVINGS_WIDTH}}  {notes}"
    )


def row_detail_text(row: Row | None, first_title: str) -> str:
    """The details panel (markup) for a chosen table row."""
    if row is None:
        return "[dim]Select a source of income or a row to see its details.[/]"
    lines = [
        f"[b]Name:[/] {escape(row.name)}",
        f"[b]Rule:[/] {escape(row.rule)}",
        f"[b]{first_title}:[/] {money(row.first)}    [b]Savings:[/] {money(row.savings)}",
        f"[b]Worked out from:[/] {escape(row.basis)}"
        if row.basis != "typed"
        else "[b]Entered by hand:[/] press e to change it",
    ]
    if row.status:
        lines.append(problem(f"[b]{escape(row.status)}[/b]"))
    if row.notes.strip():
        lines += ["", "[b]Notes:[/]", escape(row.notes.strip())]
    return "\n".join(lines)


_INCOME_TYPE_WIDTH = 10


def source_table_header() -> str:
    """The column titles above the Sources of Income list; the two-character
    indent is the list's selector marker."""
    return (
        f"  {'':<{_NAME_WIDTH}}{'Type':<{_INCOME_TYPE_WIDTH}}"
        f"{'Income':>{_FIRST_WIDTH}}  Note"
    )


def source_row_label(source: IncomeSource) -> str:
    """One Sources of Income row (markup), columns lined up with
    `source_table_header`."""
    name = escape((source.name or "(unnamed)").ljust(_NAME_WIDTH))
    type_ = escape(source.type.ljust(_INCOME_TYPE_WIDTH))
    note = escape(source.note.strip()) if source.note.strip() else ""
    row = f"{name}{type_}{money(source.current_income):>{_FIRST_WIDTH}}  {note}"
    return row.rstrip()


def source_detail_text(source: IncomeSource | None) -> str:
    if source is None:
        return "[dim]Select a source of income or a row to see its details.[/]"
    default = INCOME_TYPE_DEFAULTS[source.type]
    income = str(source.current_income)
    if source.income is None:
        income += f" (the usual for {source.type})"
    elif source.income != default:
        income += f" (typed; {source.type} is usually {default})"
    lines = [
        f"[b]Name:[/] {escape(source.name or '(unnamed)')}",
        f"[b]Type:[/] {escape(source.type)}",
        f"[b]Current Income:[/] {income}",
    ]
    if source.covenfolk_work:
        lines.append(
            "Relies on the covenfolk's work: halved while Prevailing Loyalty "
            "is -6 (DE p. 185)."
        )
    if source.note.strip():
        lines += ["", "[b]Note:[/]", escape(source.note.strip())]
    if source.description.strip():
        lines += ["", "[b]Description:[/]", markdown_text(source.description.strip())]
    return "\n".join(lines)


# ------------------------------------------------------------- improvement


def income_multiplier_text(effect: str) -> str:
    """ "x0.5"/"x1"/"x1.05"... for an Income Modification Effect."""
    return f"x{INCOME_EFFECT_MULTIPLIERS[effect]:g}"


def projected_income(current_income: int, effect: str) -> int:
    """Current Income times the Effect's multiplier (Income Modification),
    rounded to a whole number."""
    return round_away_from_zero(current_income * INCOME_EFFECT_MULTIPLIERS[effect])


def improvement_note(
    current_year: int,
    name: str,
    effect: str,
    previous_income: int,
    new_income: int,
    *,
    magic: bool = False,
) -> str:
    """The Note recorded on a source of income after an "Improve" action
    (`magic`: the change was the magi's doing)."""
    name = name or "This source of income"
    by_magic = " by magic" if magic else ""
    if effect == "Status Quo":
        return (
            f"{current_year} - {name} experienced no growth or setbacks"
            f"{by_magic}. {effect} maintained."
        )
    return (
        f"{current_year} - {name} experienced {effect}{by_magic} changing Income "
        f"from {previous_income} to {new_income}."
    )


#: Wealth made by magic: several Tribunals limit a covenant to 2 pounds of
#: silver (or its equivalent) a magus a year (Covenants p. 57, citing
#: Houses of Hermes: True Lineages p. 87); the storyguide picks the
#: multiplier a magical improvement merits (pp. 57-58).
MAGIC_SILVER_PER_MAGUS = 2
MAGIC_SOURCE = (
    "Covenants, Chapter Five: Wealth & Poverty, Magical Improvement, pp. 57-58, "
    "and Inflation, p. 65; City & Guild, Creating Wealth Using Magic, p. 130"
)


def magi_count(saga: Saga, covenant: Covenant) -> int:
    """The covenant's magi, named or not."""
    return len(covenant_magi(saga, covenant)) + covenant.unnamed_magi


def magic_limit(saga: Saga, covenant: Covenant) -> int:
    """The most a covenant may make by magic a year where its Tribunal
    has limited it: 2 pounds a magus."""
    return MAGIC_SILVER_PER_MAGUS * magi_count(saga, covenant)


def magic_wealth_text(made: int, limit: int, magi: int) -> str:
    """What an improvement by magic means (markup): the wealth it makes a
    year against the Tribunals' limit, and the inflation it feeds."""
    text = (
        f"Made by magic: {made} pound(s) a year. Where its Tribunal has passed "
        f"the limit, a covenant makes at most {MAGIC_SILVER_PER_MAGUS} pounds of "
        f"silver (or its like) a magus a year: {limit} for {magi} magi "
        "(Covenants p. 57; Houses of Hermes: True Lineages p. 87)."
    )
    if made > limit:
        text += " " + todo(
            "Over the limit: expect the Redcaps to notice, and the Quaesitores, "
            "or irate merchants and nobles, to follow."
        )
    return text + (
        " Spending it feeds the covenant's Inflation (Covenants p. 65; City & "
        "Guild p. 130)."
    )


# ------------------------------------------------------------------ changes


def add_income_source(covenant: Covenant, values: dict[str, Any]) -> IncomeSource:
    sources = covenant.economics.income_sources
    source = IncomeSource(
        id=storage.generate_unique_id(values["name"], [s.id for s in sources]),
        **values,
    )
    sources.append(source)
    return source


#: The Magic row form's key for a device's "does covenfolk's work" tick.
SAVES_PREFIX = "saves__"


def apply_row_edit(economics: Economics, row_key: str, values: dict[str, Any]) -> None:
    """Apply an expenditure/savings row's form: its typed figures, and its
    note (an empty note removes it)."""
    values = dict(values)
    notes = values.pop("notes")
    marks = {k: values.pop(k) for k in list(values) if k.startswith(SAVES_PREFIX)}
    if marks:
        # The Magic row's devices: those ticked do covenfolk's work; a
        # device not on the form (given away) keeps its mark.
        shown = {k.removeprefix(SAVES_PREFIX) for k in marks}
        kept = [d for d in economics.saving_devices if d not in shown]
        ticked = [k.removeprefix(SAVES_PREFIX) for k, on in marks.items() if on]
        economics.saving_devices = kept + ticked
    for attribute, value in values.items():
        setattr(economics, attribute, value)
    if notes:
        economics.notes[row_key] = notes
    else:
        economics.notes.pop(row_key, None)


def covenants_in_deficit(saga: Saga) -> list[tuple[str, int]]:
    """(name, surplus/deficit) for each covenant spending more than it earns."""
    results = [
        (c.name, summarize(saga, c).surplus_deficit)
        for c in filter(takes_part_in_play, saga.covenants)
    ]
    return [(name, d) for name, d in results if d < 0]


#: Inflation grows a pound for each this many pounds spent in a year.
INFLATION_PER = 100


def close_all_years(saga: Saga) -> list[tuple[str, int]]:
    """Close the year for every covenant (see close_year): (name, the
    change to its Wealth)."""
    return [
        (c.name, close_year(saga, c))
        for c in filter(takes_part_in_play, saga.covenants)
    ]


def row_problem(row_key: str, values: dict[str, Any]) -> str | None:
    """What's wrong with an expenditure/savings row form's values, if anything."""
    if row_key == "sundry" and values.get("sundry", 1) < 1:
        return "There's a cost of at least 1 pound of sundries every year."
    return None
