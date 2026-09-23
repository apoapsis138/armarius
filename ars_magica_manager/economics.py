"""Logic behind a covenant's Economics tab -- no UI in here.

Works out the covenant's finances from the rest of the sheet, following the
ArM5 "Covenant Finances" rules (reference/Covenant Finances.md): the points of
inhabitants, laboratories and weapons and armor, each category of yearly
expenditure, the cost savings from laborers, craftspeople and the like, and the
totals. Nothing here is stored; only what the user types lives in
`Covenant.economics`.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import catalog
from . import inhabitants as inh
from . import possessions as pos
from .markup import escape, markdown_inline
from .models import (
    INCOME_EFFECT_MULTIPLIERS,
    INCOME_TYPE_DEFAULTS,
    SANCTUM_USAGES,
    Covenant,
    IncomeSource,
    Saga,
    lab_characteristic_total,
    round_away_from_zero,
)

# --------------------------------------------------------------- the rules

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
            score = lab_characteristic_total(entry.lab, lab_catalog, "upkeep")[3]
        else:
            score = entry.upkeep or 0
        total += upkeep_points(score) * USAGE_MULTIPLIERS.get(entry.usage, 1.0)
    return round_away_from_zero(total)


def craft_saving_each(entry: inh.InhabitantEntry) -> int:
    """What one craftsperson saves a year: a rare one their skill, a common one
    one plus half of it, rounded down."""
    skill = entry.skill_value
    return skill if entry.rare else 1 + skill // 2


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
    #: Names of the `Economics` attributes the user types for this row.
    typed: tuple[str, ...] = ()


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


def summarize(saga: Saga, covenant: Covenant) -> Summary:
    eco = covenant.economics
    people = inh.inhabitant_points(saga, covenant)
    labs = laboratory_points(saga, covenant)
    gear = pos.gear_points(saga, covenant)
    wage_multiplier = WAGE_MULTIPLIERS.get(covenant.loyalty.money, 1.0)
    magi = inh.headcount(inh.entries_for_kind(saga, covenant, "magus"))
    craftspeople = inh.entries_for_kind(saga, covenant, "craftsperson")
    writers = magi + sum(e.quantity for e in craftspeople if e.field_of_work == "Books")

    costs = {
        "buildings": people / 10,
        "consumables": people * 2 / 10,
        "laboratories": labs / 10,
        "provisions": people * 5 / 10,
        "wages": people * 2 / 10 * wage_multiplier,
        "weapons": gear / 320,
        "writing": float(writers),
    }

    # Craftspeople: each craft (a field plus the Ability or work they share)
    # saves at most its limit of that category's cost.
    per_craft: dict[tuple[str, str], float] = {}
    craftsmen = 0
    for index, entry in enumerate(craftspeople):
        if entry.field_of_work not in CRAFT_SAVINGS:
            continue
        craftsmen += entry.quantity
        craft = (entry.linked_ability or entry.responsibility).strip().lower()
        key = (entry.field_of_work, craft or f"#{index}")
        per_craft[key] = per_craft.get(key, 0.0) + (
            craft_saving_each(entry) * entry.quantity
        )
    craft_by_row: dict[str, float] = {}
    for (field_of_work, _), amount in per_craft.items():
        row_key, limit = CRAFT_SAVINGS[field_of_work]
        craft_by_row[row_key] = craft_by_row.get(row_key, 0.0) + min(
            amount, limit * costs[row_key]
        )

    laborers = inh.other_covenfolk_count(saga, covenant, "Laborer")
    laborer_savings = min(float(laborers), LABORER_LIMIT * costs["provisions"])
    craft_savings: dict[str, float] = {}
    for row_key, cost in costs.items():
        room = cost - (laborer_savings if row_key == "provisions" else 0.0)
        craft_savings[row_key] = min(craft_by_row.get(row_key, 0.0), max(room, 0.0))
    row_savings = {
        key: craft_savings[key] + (laborer_savings if key == "provisions" else 0.0)
        for key in costs
    }

    def note(key: str) -> str:
        return eco.notes.get(key, "")

    # Round every row's final Cost/Savings to a whole number here (the ratios
    # above stay precise floats so the craft/laborer-limit math is exact); a
    # Row's `first`/`savings` are always integers from this point on, so
    # summing them can't drift from summing the already-rounded numbers.
    cost = {k: round_away_from_zero(v) for k, v in costs.items()}
    saved = {k: round_away_from_zero(v) for k, v in row_savings.items()}

    expenditure = [
        Row(
            "buildings",
            "Buildings",
            "1 pound per 10 pts Inhabitants (50% per craft)",
            cost["buildings"],
            saved["buildings"],
            note("buildings"),
            f"{people} pts of inhabitants / 10",
        ),
        Row(
            "consumables",
            "Consumables",
            "2 pounds per 10 pts Inhabitants (20% per craft)",
            cost["consumables"],
            saved["consumables"],
            note("consumables"),
            f"{people} pts of inhabitants x 2 / 10",
        ),
        Row(
            "laboratories",
            "Laboratories",
            "1 pound per 10 pts Laboratories (20% per craft)",
            cost["laboratories"],
            saved["laboratories"],
            note("laboratories"),
            f"{labs} pts of laboratories / 10",
        ),
        Row(
            "provisions",
            "Provisions",
            "5 pounds per 10 pts Inhabitants (50% laborers + 20% per craft)",
            cost["provisions"],
            saved["provisions"],
            note("provisions"),
            f"{people} pts of inhabitants x 5 / 10",
        ),
        Row(
            "wages",
            "Wages",
            "2 pounds per 10 pts Inhabitants, times the salary multiplier",
            cost["wages"],
            saved["wages"],
            note("wages"),
            f"{people} pts of inhabitants x 2 / 10 x {wage_multiplier:g} "
            f"({covenant.loyalty.money}, from Loyalty)",
            note=f"x{wage_multiplier:g}",
        ),
        Row(
            "weapons",
            "Weapons",
            "1 pound per 320 pts Weapons and Armor (50% per craft)",
            cost["weapons"],
            saved["weapons"],
            note("weapons"),
            f"{gear} pts of weapons and armor / 320",
        ),
        Row(
            "writing",
            "Writing Materials",
            "1 pound per Magus and book specialist (50% per craft)",
            cost["writing"],
            saved["writing"],
            note("writing"),
            f"{magi} magi + {writers - magi} book craftspeople",
        ),
        Row(
            "tithes",
            "Tithes",
            "Debts and taxes",
            eco.tithes,
            0,
            note("tithes"),
            "typed",
            typed=("tithes",),
        ),
        Row(
            "inflation",
            "Inflation",
            "Increases yearly",
            eco.inflation,
            0,
            note("inflation"),
            "typed",
            typed=("inflation",),
        ),
        Row(
            "sundry",
            "Sundry",
            "At least 1 pound of sundries every year",
            eco.sundry,
            0,
            note("sundry"),
            "typed",
            typed=("sundry",),
        ),
    ]

    savings = [
        Row(
            "laborers",
            "Laborers",
            "1 pound per person (at most 50% of Provisions)",
            laborers,
            round_away_from_zero(laborer_savings),
            note("laborers"),
            "Laborer-tagged entries on the Other Covenfolk list",
        ),
        Row(
            "craftspeople",
            "Craftspeople",
            "1 + (Ability / 2) pounds each, or the Ability if rare; each craft "
            "saves at most its limit of the category",
            craftsmen,
            round_away_from_zero(sum(craft_savings.values())),
            note("craftspeople"),
            "Craftspeople with a field of work (Books saves nothing)",
        ),
        Row(
            "magic",
            "Magic",
            "The rules give items and Ritual castings different rates "
            "(1 or 5 pounds per magnitude) -- work out the total and enter it",
            0,
            eco.magic_savings,
            note("magic"),
            "typed",
            typed=("magic_savings",),
        ),
        Row(
            "emergency_savings",
            "Emergency Savings",
            "Reduced privileges, cut wages, layoffs... (no formula yet)",
            0,
            eco.emergency_savings,
            note("emergency_savings"),
            "typed",
            typed=("emergency_savings",),
        ),
    ]

    before = sum(row.first for row in expenditure)
    # Laborer and craft savings sit in the expenditure rows; Magic and
    # Emergency Savings aren't tied to a category, so they only reduce the
    # total.
    cost_savings = sum(saved.values()) + eco.magic_savings + eco.emergency_savings
    income = sum(s.current_income for s in eco.income_sources)
    total_expenditure = before - cost_savings
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
        surplus_deficit=income - total_expenditure,
    )


# --------------------------------------------------------------------- text


def money(value: float) -> str:
    """A pounds or points figure as a whole number (see
    models.round_away_from_zero) -- safe to call on an already-rounded int
    too."""
    return str(round_away_from_zero(value))


def _aligned(rows: list[tuple[str, str]]) -> str:
    width = max(len(label) for label, _ in rows)
    return "\n".join(f"{label + ':':<{width + 1}} {value}" for label, value in rows)


def wealth_texts(summary: Summary) -> tuple[str, str]:
    """The Wealth section as two columns."""
    left = _aligned(
        [
            ("Points of Inhabitants", money(summary.inhabitant_points)),
            ("Points of Laboratories", money(summary.laboratory_points)),
            ("Points of Weapons and Armor", money(summary.gear_points)),
            ("Wealth", str(summary.wealth)),
        ]
    )
    surplus_color = "red" if summary.surplus_deficit < 0 else "cyan"
    right = _aligned(
        [
            ("Total Income", money(summary.income)),
            ("Expenditure (Before Cost Savings)", money(summary.before_savings)),
            ("Cost Savings", money(summary.cost_savings)),
            ("Total Expenditure", money(summary.total_expenditure)),
            (
                "Surplus/Deficit",
                f"[{surplus_color}]{summary.surplus_deficit:+d}[/]",
            ),
        ]
    )
    return left, right


_NAME_WIDTH = 20
_FIRST_WIDTH = 8
_SAVINGS_WIDTH = 9
_NOTES_WIDTH = 34


def table_header(first_title: str) -> str:
    """The column titles above a table's rows; the two-character indent is the
    list's selector marker."""
    return (
        f"  {'':<{_NAME_WIDTH}}{first_title:>{_FIRST_WIDTH}}"
        f"{'Savings':>{_SAVINGS_WIDTH}}  Notes"
    )


def row_label(row: Row) -> str:
    """One table row (markup), columns lined up with `table_header`."""
    name = row.name + (f" ({row.note})" if row.note else "")
    notes = row.notes.replace("\n", " ")
    if len(notes) > _NOTES_WIDTH:
        notes = notes[: _NOTES_WIDTH - 1] + "…"
    return (
        f"{escape(name.ljust(_NAME_WIDTH))}{money(row.first):>{_FIRST_WIDTH}}"
        f"{money(row.savings):>{_SAVINGS_WIDTH}}  {escape(notes)}"
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
    if row.notes.strip():
        lines += ["", "[b]Notes:[/]", escape(row.notes.strip())]
    return "\n".join(lines)


def source_row_label(source: IncomeSource) -> str:
    parts = [
        f"{escape(source.name or '(unnamed)')} | Type: {escape(source.type)}"
        f" | Current Income: {source.current_income}"
    ]
    if source.note.strip():
        parts.append(escape(source.note.strip()))
    return " | ".join(parts)


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
    if source.note.strip():
        lines += ["", "[b]Note:[/]", escape(source.note.strip())]
    if source.description.strip():
        lines += ["", "[b]Description:[/]", markdown_inline(source.description.strip())]
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
    current_year: int, name: str, effect: str, previous_income: int, new_income: int
) -> str:
    """The Note recorded on a source of income after an "Improve" action."""
    name = name or "This source of income"
    if effect == "Status Quo":
        return (
            f"{current_year} - {name} experienced no growth or setbacks. "
            f"{effect} maintained."
        )
    return (
        f"{current_year} - {name} experienced {effect} changing Income "
        f"from {previous_income} to {new_income}."
    )
