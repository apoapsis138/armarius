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

from .. import catalog, tribunal_packages, tribunals, vassals, world
from .. import covenant_build as cov_build
from .. import covenant_diary as cov_diary
from .. import economics as eco
from .. import inhabitants as inh
from .. import possessions as pos
from ..covenants import (
    UNKNOWN_HOOK_POINTS,
    boon_hook_is_unknown,
    covenant_boon_points,
    covenant_hook_points,
)
from ..forms import world as world_forms
from ..models import (
    INHABITANT_KINDS,
    LINE,
    POSSESSION_KINDS,
    Book,
    Covenant,
    CovenantDiaryEntry,
    Saga,
)
from ..references import Fact
from ..rules import covenfolk, library, realms
from ..rules.realms import covenant_effective_aura
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
        Fact("Living (Magi)", f"{covenant.living_conditions_magi:+d}"),
        Fact("Living (Mundane)", f"{covenant.living_conditions_mundane:+d}"),
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


def inhabitant_groups(saga: Saga, covenant: Covenant) -> list[Group]:
    """Each kind of inhabitant the covenant has, Magi first."""
    groups = []
    for kind in INHABITANT_KINDS:
        entries = covenfolk.entries_for_kind(saga, covenant, kind)
        if not entries:
            continue
        groups.append(
            Group(
                kind,
                f"{inh.KIND_TITLES[kind]} ({covenfolk.headcount(entries)})",
                _table(_INHABITANT_COLUMNS[kind], entries),
                [inh.detail_text(e, saga.current_year) for e in entries],
            )
        )
    return groups


def possession_groups(saga: Saga, covenant: Covenant) -> list[Group]:
    """Each kind of possession the covenant has."""
    by_id = catalog.load_lab_virtue_flaw_catalog_by_id()
    groups = []
    for kind in POSSESSION_KINDS:
        entries = pos.entries_for_kind(saga, covenant, kind, by_id)
        if not entries:
            continue
        groups.append(
            Group(
                kind,
                f"{pos.KIND_TITLES[kind]} ({len(entries)})",
                pos.table(kind, entries),
                [pos.detail_text(e) for e in entries],
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


def _ledger(first: str, rows: list[eco.Row]) -> Table:
    return Table(
        ["Name", first, "Savings", "Notes"],
        [
            [
                r.name + (f" ({r.note})" if r.note else ""),
                eco.money(r.first),
                eco.money(r.savings),
                (r.status or r.notes).replace("\n", " "),
            ]
            for r in rows
        ],
    )


def treasury(saga: Saga, covenant: Covenant) -> Treasury:
    summary = eco.summarize(saga, covenant)
    sources = covenant.economics.income_sources
    groups = [
        Group(
            "income",
            f"Sources of Income ({len(sources)})",
            Table(
                ["Name", "Type", "Income", "Note"],
                [
                    [s.name or "(unnamed)", s.type, str(s.current_income), s.note]
                    for s in sources
                ],
            ),
            [eco.source_detail_text(s) for s in sources],
        ),
        Group(
            "expenditure",
            "Yearly Expenditure",
            _ledger("Cost", summary.expenditure),
            [eco.row_detail_text(r, "Cost") for r in summary.expenditure],
        ),
        Group(
            "savings",
            "Cost Savings",
            _ledger("Quantity", summary.savings),
            [eco.row_detail_text(r, "Quantity") for r in summary.savings],
        ),
    ]
    money = eco.money
    wealth = [
        Fact("Wealth", str(summary.wealth)),
        Fact("Inhabitants", money(summary.inhabitant_points)),
        Fact("Laboratories", money(summary.laboratory_points)),
        Fact("Weapons & Armor", money(summary.gear_points)),
        Fact("Before Savings", money(summary.before_savings)),
        Fact("Cost Savings", money(summary.cost_savings)),
    ]
    return Treasury(
        wealth,
        int(money(summary.income)),
        int(money(summary.total_expenditure)),
        summary.surplus_deficit,
        eco.emergency_status(summary.surplus_deficit, summary.wealth),
        groups,
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
    ]
