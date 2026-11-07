"""What a covenant's page shows, independent of how it is drawn: its
charter (aura, Aegis, living conditions, Boons and Hooks, Reputations),
its Loyalty, its inhabitants and possessions as tables, its treasury, its
library as shelves, its Diary and its Build Points.

Plain values rather than markup where a graphical page gives each its own
type; the tables have the terminal sheet's columns, and the longer passages (an inhabitant's details, a Boon's rules)
are the same markup the terminal sheet shows.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from .. import catalog, goods, tribunal_packages, tribunals, vassals, viewing, world
from .. import covenant_build as cov_build
from .. import covenant_diary as cov_diary
from .. import economics as eco
from .. import inhabitants as inh
from .. import possessions as pos
from ..covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
    contested_now,
    covenant_boon_points,
    covenant_hook_points,
    resource_standing,
)
from ..forms import world as world_forms
from ..markup import escape
from ..models import (
    INHABITANT_KINDS,
    LINE,
    POSSESSION_KINDS,
    Book,
    Covenant,
    CovenantDiaryEntry,
    IncomeSource,
    Possession,
    Saga,
)
from ..references import Fact
from ..rules import covenfolk, library, living, realms
from ..rules.realms import covenant_effective_aura
from ..rules.rounding import round_away_from_zero
from ..tables import Table
from .laboratory import Aura


def subtitle(saga: Saga, covenant: Covenant) -> str:
    """The line under the name: its Tribunal, season, founding and now."""
    parts = [
        f"{covenant.covenant_season} {tribunal_packages.place_word(saga, covenant)}"
    ]
    tribunal = tribunals.title_of(saga, covenant)
    if tribunal:
        parts.insert(0, tribunal)
    if covenant.year_founded is not None:
        parts.append(f"founded {covenant.year_founded}")
    parts.append(f"{saga.current_season} {saga.current_year}")
    return "  ·  ".join(parts)


def aura(covenant: Covenant) -> Aura:
    """The covenant's aura: its own, what its Boons add, and the total."""
    total = covenant_effective_aura(
        covenant, catalog.load_covenant_boon_hook_catalog_by_id()
    )
    return Aura(
        covenant.aura,
        total - covenant.aura,
        total,
        covenant.aura_realm,
        realms.aura_note(covenant.aura_realm, total),
        "from Boons",
    )


def charter_facts(saga: Saga, covenant: Covenant) -> list[Fact]:
    facts = [
        Fact("Aegis of the Hearth", str(covenant.aegis_of_the_hearth)),
        Fact("Aegis' Penetration", str(covenant.aegis_penetration)),
        Fact("Living (Magi)", living.living_text(covenant, magi=True)),
        Fact("Living (Mundane)", living.living_text(covenant, magi=False)),
    ]
    if covenant.in_creation:
        facts.append(Fact("Build Points", cov_build.summary(saga, covenant)))
    return facts + [Fact(label, value) for label, value in vassals.rows(saga, covenant)]


def sketch_facts(saga: Saga, covenant: Covenant) -> list[Fact]:
    """A Line or Sketch covenant's facts under its name."""
    tribunal = tribunals.of(saga, covenant)
    facts = [Fact("Tribunal", tribunal.name if tribunal is not None else "(not set)")]
    facts += [Fact(label, value) for label, value in vassals.rows(saga, covenant)]
    if covenant.detail != LINE:
        founded = covenant.year_founded
        facts += [
            Fact("Founded", "(not set)" if founded is None else str(founded)),
            Fact("Season", covenant.covenant_season),
            Fact("Magi", world_forms.magi_title(saga, covenant).removeprefix("Magi ")),
            Fact("Votes", world.votes_text(saga, covenant)),
        ]
    facts.append(Fact("Detail", covenant.detail))
    return facts


# Boons, Hooks and Reputations


@dataclass(frozen=True)
class BoonHookCard:
    index: int  # into covenant.boons_hooks
    name: str
    tier: str  # "Free", "Minor", "Major"
    category: str  # "Site", "Resources"... or ""
    points: float  # what it costs (a Boon) or provides (a Hook)
    note: str  # "Unknown", a pool's state, or ""


def boon_hook_cards(covenant: Covenant, kind: str) -> list[BoonHookCard]:
    """The covenant's Boons or Hooks (`kind`), in the order attached."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    cards = []
    for index, instance in enumerate(covenant.boons_hooks):
        definition = by_id.get(instance.vf_id)
        if definition is None or definition.type != kind:
            continue
        points = abs(definition.cost)
        notes = []
        if boon_hook_is_unknown(instance, definition):
            points = UNKNOWN_HOOK_POINTS
            notes.append("Unknown")
        if instance.vf_id in cov_diary.POOLS and instance.id:
            notes.append(cov_diary.pool_short(covenant, instance.id))
        cards.append(
            BoonHookCard(
                index,
                catalog.describe_boon_hook(instance, by_id),
                definition.tier,
                definition.category,
                points,
                ", ".join(notes),
            )
        )
    return cards


def boon_hook_points(covenant: Covenant) -> tuple[float, float]:
    """What the Boons cost and the Hooks provide: they should balance."""
    by_id = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_boon_points(covenant, by_id), covenant_hook_points(covenant, by_id)


@dataclass(frozen=True)
class Reputation:
    index: int
    name: str
    score: int
    known: bool  # by the covenant; one it doesn't know of costs no Loyalty


def reputations(covenant: Covenant) -> list[Reputation]:
    return [
        Reputation(i, r.name, r.score, r.known)
        for i, r in enumerate(covenant.reputations)
    ]


# Loyalty


@dataclass(frozen=True)
class Loyalty:
    governance: str
    base: int
    modifiers: int
    points: int  # base + modifiers
    score: int  # the Prevailing Loyalty Score those points give


def loyalty(saga: Saga, covenant: Covenant) -> Loyalty:
    styles = inh.governance_names(covenant)
    governance = ", ".join(styles) or covenant.loyalty.governance
    base = inh.base_loyalty(saga, covenant)
    modifiers = inh.total_modifiers(saga, covenant)
    points = base + modifiers
    return Loyalty(
        governance, base, modifiers, points, inh.prevailing_loyalty_score(points)
    )


# Tables


def _year(year: int | None) -> str:
    return "" if year is None else str(year)


#: Each kind of inhabitant's columns after its name: a title, and how to
#: read the cell from a covenfolk.InhabitantEntry.
_INHABITANT_COLUMNS: dict[str, tuple[tuple[str, Callable[[Any], str]], ...]] = {
    "magus": (
        ("House", lambda e: inh.house_name(e.house_id)),
        ("Year Born", lambda e: _year(e.year_born)),
        ("Gift", lambda e: e.gift),
    ),
    **dict.fromkeys(
        ("companion", "specialist"),
        (
            ("Responsibility", lambda e: e.responsibility),
            ("Role", lambda e: e.role),
            ("Year Born", lambda e: _year(e.year_born)),
        ),
    ),
    "craftsperson": (
        ("Responsibility", lambda e: e.responsibility),
        ("Score", lambda e: str(e.skill_value)),
        ("Qty", lambda e: str(e.quantity)),
        ("Year Born", lambda e: _year(e.year_born)),
    ),
    "turb": (
        ("Responsibility", lambda e: e.responsibility),
        ("Qty", lambda e: str(e.quantity)),
    ),
    "inhabitant": (
        ("Role", lambda e: e.role),
        ("Qty", lambda e: str(e.quantity)),
    ),
    **dict.fromkeys(
        ("horse", "hound", "livestock"), (("Qty", lambda e: str(e.quantity)),)
    ),
}


def _table(
    columns: tuple[tuple[str, Callable[[Any], str]], ...], entries: Sequence[Any]
) -> Table:
    return Table(
        ["Name", *(title for title, _ in columns)],
        [
            [entry.name or "(unnamed)", *(cell(entry) for _, cell in columns)]
            for entry in entries
        ],
    )


@dataclass(frozen=True)
class Group:
    """One kind of inhabitant or possession: its title, its table and the
    details of each row (markup), in the same order."""

    kind: str
    title: str
    table: Table
    details: list[str]


ARRIVING_KINDS = inh.ARRIVING_KINDS
VARIES = "Varies"


def _with_arrivals(
    saga: Saga, covenant: Covenant, entries: Sequence[Any], table: Table
) -> Table:
    """`table` (plain cells) with a Year Arrived column, as markup: a line
    whose people came in one year shows it; a split line shows Varies and,
    under it, an indented row for each group with its count and year. A
    sub-row chooses its line. Newcomers still growing used to the Gift are
    in italics."""
    founded = covenant.year_founded or 0
    columns = [*table.columns, "Year Arrived"]
    qty = columns.index("Qty") if "Qty" in columns else None
    rows: list[list[str]] = []
    keys: list[int | None] = []
    for index, (row, entry) in enumerate(zip(table.rows, entries, strict=True)):
        cohorts = inh.entry_cohorts(entry, founded)

        def year(came: int, entry: Any = entry) -> str:
            shown = str(came) if came else ""
            new = entry.kind in inh.FAMILIARITY_KINDS and inh.still_new(
                saga, covenant, came
            )
            return f"[i]{shown}[/]" if new and shown else shown

        main = year(cohorts[0][1]) if len(cohorts) == 1 else VARIES
        rows.append([*(escape(cell) for cell in row), main])
        keys.append(index)
        if len(cohorts) < 2:
            continue
        for count, came in cohorts:
            cells = [""] * len(columns)
            if qty is not None:
                cells[qty] = f"[dim]{count}[/]"
            else:
                cells[0] = f"[dim]    {count} of them[/]"
            cells[-1] = f"[dim]{year(came)}[/]"
            rows.append(cells)
            keys.append(index)
    return Table(columns, rows, keys, markup=True)


def inhabitant_groups(saga: Saga, covenant: Covenant) -> list[Group]:
    """Each kind of inhabitant the covenant has, Magi first."""
    groups = []
    for kind in INHABITANT_KINDS:
        entries = covenfolk.entries_for_kind(saga, covenant, kind)
        if not entries:
            continue
        table = _table(_INHABITANT_COLUMNS[kind], entries)
        if kind == "craftsperson":
            # What each saves goes before Year Born (DE pp. 194-195).
            saves = eco.entry_savings(saga, covenant)
            born = table.columns.index("Year Born")
            table = Table(
                [*table.columns[:born], "Saves", *table.columns[born:]],
                [
                    [*row[:born], saved, *row[born:]]
                    for row, saved in zip(table.rows, saves, strict=True)
                ],
            )
        if kind in ARRIVING_KINDS:
            table = _with_arrivals(saga, covenant, entries, table)
        groups.append(
            Group(
                kind,
                f"{inh.KIND_TITLES[kind]} ({covenfolk.headcount(entries)})",
                table,
                [
                    "\n\n".join(
                        part
                        for part in (
                            inh.detail_text(e, saga.current_year),
                            inh.arrival_text(saga, covenant, e),
                        )
                        if part
                    )
                    for e in entries
                ],
            )
        )
    return groups


def _vis_sources_table(
    saga: Saga, covenant: Covenant, entries: Sequence[pos.PossessionEntry]
) -> Table:
    """The vis sources, a contested one as income shows it: its mark, its
    pawns struck through with what it gives beside them, and its standing."""
    plain = pos.table("vis_source", entries)
    pawns = plain.columns.index("Pawns")
    year = saga.current_year
    rows = []
    for row, entry in zip(plain.rows, entries, strict=True):
        source = entry.record
        assert source is not None  # the Possessions list only holds records
        cells = [escape(cell) for cell in row]
        unsettled = contested_now(source, year)
        tone = "$text-error" if unsettled else "$text-success"
        standing = resource_standing(covenant, source, year)
        rows.append(
            [
                cells[0],
                CONTESTED_MARK if unsettled else "",
                *cells[1:pawns],
                f"[s]{cells[pawns]}[/]" if unsettled else cells[pawns],
                "[b $text-error]0[/]" if unsettled else "",
                *cells[pawns + 1 :],
                f"[i {tone}]{escape(standing)}[/]" if standing else "",
            ]
        )
    columns = plain.columns
    return Table(
        [
            columns[0],
            "",
            *columns[1:pawns],
            columns[pawns],
            "",
            *columns[pawns + 1 :],
            "Standing",
        ],
        rows,
        markup=True,
        stretch=len(columns) + 2,
    )


def _standing_line(
    saga: Saga, covenant: Covenant, resource: Possession | IncomeSource
) -> str:
    """A contested resource's standing, opening its details."""
    standing = resource_standing(covenant, resource, saga.current_year)
    return f"[b]{escape(standing)}[/]\n\n" if standing else ""


def _with_standing(saga: Saga, covenant: Covenant, entry: pos.PossessionEntry) -> str:
    record = entry.record
    return (
        _standing_line(saga, covenant, record) if record is not None else ""
    ) + pos.detail_text(entry)


def possession_groups(saga: Saga, covenant: Covenant) -> list[Group]:
    """Each kind of possession the covenant has."""
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    groups = []
    for kind in POSSESSION_KINDS:
        entries = pos.entries_for_kind(saga, covenant, kind, by_id)
        if not entries:
            continue
        contested = kind == "vis_source" and any(
            e.record is not None and e.record.contested for e in entries
        )
        groups.append(
            Group(
                kind,
                f"{pos.KIND_TITLES[kind]} ({len(entries)})",
                _vis_sources_table(saga, covenant, entries)
                if contested
                else pos.table(kind, entries),
                [_with_standing(saga, covenant, e) for e in entries],
            )
        )
    return groups


# The treasury


@dataclass(frozen=True)
class Treasury:
    wealth: list[Fact]
    income: int
    expenditure: int
    balance: int  # income less expenditure
    status: str  # running at a deficit or broke, or ""
    groups: list[Group]  # Sources of Income, Yearly Expenditure, Cost Savings
    reckoned: list[Fact]  # the points the costs are worked out from
    settling: str  # what settling its contested income would do, or ""
    ways_out: Table  # how to cover a deficit Wealth can't; no rows otherwise
    crafts: Table
    purchases: Group


#: A contested resource's mark in a table, as an accountant's in the margin.
CONTESTED_MARK = "[b $text-error]![/]"


def _income_table(saga: Saga, covenant: Covenant) -> Table:
    """The sources of income; a source that gives less than its income
    this year shows that struck through with what it gives beside it, and
    a contested one its mark and standing."""
    sources = covenant.economics.income_sources
    year = saga.current_year
    loyalty = inh.prevailing_loyalty(saga, covenant)
    rows = []
    for s in sources:
        now = round_away_from_zero(eco.income_now(saga, s, loyalty))
        short = now != s.current_income
        open_contest = contested_now(s, year)
        tone = "$text-error" if open_contest else "$text-success"
        standing = resource_standing(covenant, s, year)
        rows.append(
            [
                escape(s.name or "(unnamed)"),
                CONTESTED_MARK if open_contest else "",
                escape(s.type),
                f"[s]{s.current_income}[/]" if short else str(s.current_income),
                f"[b $text-error]{now}[/]" if short else "",
                f"[i {tone}]{escape(standing)}[/]" if standing else escape(s.note),
            ]
        )
    return Table(
        ["Name", "", "Type", "Income", "", "Standing"], rows, markup=True, stretch=5
    )


def _expenditure_table(rows: list[eco.Row], purchased: int) -> Table:
    def working(row: eco.Row) -> str:
        how = "" if row.basis == "typed" else row.basis
        if row.key == "provisions":
            saved = round_away_from_zero(row.first * eco.LABORER_LIMIT)
            how += f"; laborers may save {saved}"
        if row.key == "sundry":
            how = f"£{row.first - purchased} a year"
            how += f" + £{purchased} of the year's purchases" if purchased else ""
        return " ".join(part for part in (how, row.notes) if part).replace("\n", " ")

    return Table(
        ["Name", "Cost", "Cap per Craft", "Savings", "Total", "How It's Reckoned"],
        [
            [
                r.name + (f" ({r.note})" if r.note else ""),
                eco.money(r.first),
                "-" if r.cap is None else str(r.cap),
                eco.money(r.savings),
                eco.money(r.first - r.savings),
                working(r),
            ]
            for r in rows
        ],
        stretch=5,
    )


def _savings_table(rows: list[eco.Row]) -> Table:
    return Table(
        ["Name", "Quantity", "Savings", "Notes"],
        [
            [
                r.name,
                eco.money(r.first),
                eco.money(r.savings),
                r.notes.replace("\n", " "),
            ]
            for r in rows
        ],
    )


def _crafts_table(lines: list[eco.CraftLine]) -> Table:
    return Table(
        ["Name", "Row", "Worth", "Cap", "Saves", "Notes"],
        [
            [
                c.name,
                c.row,
                str(c.worth),
                "-" if c.cap is None else str(c.cap),
                str(c.saves),
                c.note,
            ]
            for c in lines
        ],
        stretch=5,
    )


def _settling_text(saga: Saga, covenant: Covenant, balance: int) -> str:
    """What the unsettled income would bring, if any is."""
    waiting = [
        s
        for s in covenant.economics.income_sources
        if contested_now(s, saga.current_year)
    ]
    gain = sum(s.current_income for s in waiting)
    if not gain:
        return ""
    after = balance + gain
    result = f"a £{after} surplus" if after >= 0 else f"a £{-after} deficit"
    names = " and ".join(s.name or "(unnamed)" for s in waiting)
    return f"Settling {names} would bring £{gain} a year and make this {result}."


def _purchases_group(summary: eco.Summary, covenant: Covenant) -> Group:
    """The year's purchases, then the sundries every year has, which is
    not a line to choose."""
    economics = covenant.economics
    entries = economics.purchases
    rows = [[p.season, p.name, p.kind, goods.number(p.pounds)] for p in entries]
    rows.append(["All year", ENUMERUS, "Always", str(economics.sundry)])
    return Group(
        "purchases",
        "The Year's Purchases",
        Table(
            ["When", "What", "Kind", "£"],
            rows,
            [*range(len(entries)), None],
            stretch=1,
        ),
        [
            "\n".join(
                line
                for line in (
                    f"[b]{escape(p.kind)}[/], {escape(p.season)}: "
                    f"£{goods.number(p.pounds)}",
                    escape(p.note),
                )
                if line
            )
            for p in entries
        ],
    )


#: A pound of petty costs nobody can account for (Covenants p. 70).
ENUMERUS = "The Pound of Enumerus"


def treasury(saga: Saga, covenant: Covenant) -> Treasury:
    summary = eco.summarize(saga, covenant)
    sources = covenant.economics.income_sources
    groups = [
        Group(
            "income",
            f"Sources of Income ({len(sources)})",
            _income_table(saga, covenant),
            [
                _standing_line(saga, covenant, s) + eco.source_detail_text(s)
                for s in sources
            ],
        ),
        Group(
            "expenditure",
            "Yearly Expenditure",
            _expenditure_table(
                summary.expenditure, eco.purchases_total(covenant.economics)
            ),
            [eco.row_detail_text(r, "Cost") for r in summary.expenditure],
        ),
        Group(
            "savings",
            "Cost Savings",
            _savings_table(summary.savings),
            [eco.row_detail_text(r, "Quantity") for r in summary.savings],
        ),
    ]
    money = eco.money
    rise = eco.inflation_rise(covenant.economics, summary.total_expenditure)
    wealth = [
        Fact("Wealth", f"{summary.wealth} £"),
        Fact("Before Savings", money(summary.before_savings)),
        Fact("Cost Savings", money(summary.cost_savings)),
        # A covenant can afford about a point for each pound (DE p. 191).
        Fact("Can Afford", f"about {money(summary.income)} points"),
        Fact("Next Year's Inflation", f"+{rise}"),
    ]
    reckoned = [
        Fact("Points of Inhabitants", money(summary.inhabitant_points)),
        Fact("Points of Laboratories", money(summary.laboratory_points)),
        Fact("Points of Weapons & Armor", money(summary.gear_points)),
    ]
    return Treasury(
        wealth,
        int(money(summary.income)),
        int(money(summary.total_expenditure)),
        summary.surplus_deficit,
        eco.emergency_status(summary.surplus_deficit, summary.wealth),
        groups,
        reckoned,
        _settling_text(saga, covenant, summary.surplus_deficit),
        Table(
            ["Way Out", "Saves", "What It Costs"],
            [list(way) for way in eco.ways_out(saga, covenant, summary)],
            stretch=2,
        ),
        _crafts_table(summary.crafts),
        _purchases_group(summary, covenant),
    )


# The library


#: The library's shelves, in order: a title and the book types on it.
SHELVES = (
    ("Summae", ("Art Summa", "Ability Summa")),
    ("Tractatus", ("Tractatus",)),
    ("Laboratory Texts", ("Lab Text",)),
    ("Casting Tablets", ("Casting Tablet",)),
    ("Other Books", ("Other",)),
)


@dataclass(frozen=True)
class Spine:
    """A book as it stands on the shelf."""

    book: Book
    subject: str  # the Art or Ability it teaches, the spell it records, or ""
    art: str  # an Art, for its symbol, or ""
    level: int | None
    quality: int | None


def _spine(saga: Saga, book: Book) -> Spine:
    art = book.art or book.form
    subject = book.art or book.ability or book.spell_name
    return Spine(
        book,
        subject.title() if subject == book.art else subject,
        art.title(),
        library.level_of(book, saga),
        library.effective_quality(saga, book),
    )


def shelves(saga: Saga, covenant: Covenant) -> list[tuple[str, list[Spine]]]:
    """The covenant's books on their shelves, each shelf that has any."""
    books = library.books_in_covenant(saga, covenant)
    result = []
    for title, types in SHELVES:
        spines = [_spine(saga, b) for b in books if b.type in types]
        if spines:
            result.append((title, spines))
    return result


# The Diary


@dataclass(frozen=True)
class DiaryCard:
    index: int  # into covenant.diary
    when: str  # "Spring 1220"
    category: str
    name: str
    status: str  # a Story Event's Open or Resolved, or ""
    amounts: str  # "-12 £, +3 Vim vis", or ""


def diary_cards(diary: list[CovenantDiaryEntry]) -> list[DiaryCard]:
    """The Diary, newest first."""
    return [
        DiaryCard(
            i,
            f"{diary[i].season} {diary[i].year}",
            diary[i].category,
            diary[i].name,
            diary[i].status,
            cov_diary.amounts(diary[i]),
        )
        for i in reversed(cov_diary.date_order(diary))
        if viewing.shows_entry(diary[i])
    ]
