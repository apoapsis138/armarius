"""Every kind of record's printed sheet: the character's (print_layout),
and here the covenant's, the laboratory's and the familiar's, each laid
out for paper from the same core figures their pages show.

Pattern: LAYOUTS is a registry of builders by record kind (Strategy),
each filling a print_layout.Document with blocks (Builder) that a renderer
draws (gui.print_sheet; the Markdown renderer). The record reaches a
builder through viewing.as_read_by, and the whole document is built while
viewing reads as the copy's reader (viewing.reading_as): the Protection
Proxy in front of every builder, so none of them knows who reads, and a
Player copy holds nothing the players may not read.

On paper nothing carries meaning by colour alone: the core's markup
becomes plain words (bold, italic or struck through where it says so),
the Lab Totals are numbers with the best in bold, and a Specialization's
bar its points.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Sequence
from typing import Any

from . import covenant_charter as cc
from . import enchanted_devices as ed
from . import familiars as fam
from . import lab_texts as lt
from . import saga_overview as ov
from . import troupe, viewing
from .arts import ART_ABBREVIATIONS, FORMS, TECHNIQUES
from .forms import covenant_history
from .forms import world as world_forms
from .markup import plain
from .models import FULL, LINE, Character, Covenant, Familiar, Laboratory, Saga
from .print_layout import (
    DEFAULT_OPTIONS,
    HOUSE_COLOURS,
    Blanks,
    Block,
    Cell,
    Column,
    Columns,
    Document,
    Entry,
    Facts,
    Heading,
    NewPage,
    Paragraph,
    PrintOptions,
    ScoreBoxes,
    Symbol,
    Table,
    Title,
    abilities_blocks,
    character_document,
    condition_from,
    counted,
    fact_pairs,
    paragraphs,
    reader_for,
    secrets_blocks,
    signed,
    stacked,
    traits_blocks,
    virtue_flaw_columns,
)
from .references import Fact
from .rules import library
from .sheets import character as cs
from .sheets import covenant as cvs
from .sheets import familiar as fs
from .sheets import laboratory as ls
from .style.palettes import HOUSES, SCRIPTORUM, SCRIPTORUM_DARK, Palette
from .tables import Table as CoreTable
from .viewing import Viewer

# ---------------------------------------------------------------- core tables

#: A markup tag the core writes ([b], [i $label], [/], ...).
_TAG = re.compile(r"(?<!\\)\[(/?)([^\[\]\n]*)\]")


def _style(text: str) -> str:
    """How a cell's markup sets its words on paper: "struck", "bold",
    "italic" or "" (a colour alone sets nothing)."""
    words = {
        word
        for match in _TAG.finditer(text)
        if not match.group(1)
        for word in match.group(2).split()
    }
    for mark, style in (("s", "struck"), ("b", "bold"), ("i", "italic")):
        if mark in words:
            return style
    return ""


def cell(text: str, markup: bool = True) -> Cell:
    """A table cell from a core table's cell."""
    if not markup:
        return Cell(text)
    return Cell(plain(text), _style(text))


#: The widest and narrowest share a column is given, in characters.
_WIDEST, _NARROWEST = 34, 4


def _widths(table: CoreTable) -> list[float]:
    """Each column's share of the width, by the longest words in it; the
    table's stretching column (the name, usually) gets more."""
    found = []
    for k, title in enumerate(table.columns):
        cells = [plain(row[k]) if table.markup else row[k] for row in table.rows]
        longest = max([len(title), *(len(c) for c in cells)])
        found.append(max(_NARROWEST, min(_WIDEST, longest)))
    if table.columns:
        found[table.stretch] += 6
    total = sum(found) or 1
    return [n / total for n in found]


def from_table(table: CoreTable) -> Table:
    """A core table (tables.Table, what the desktop draws) as a printed
    one. A row with no key heads the rows after it, as a group; a footed
    table's last row is set in bold."""
    widths = _widths(table)
    columns = tuple(
        Column(title, width, "l" if k == 0 or k == table.stretch else "c")
        for k, (title, width) in enumerate(zip(table.columns, widths, strict=True))
    )
    rows: list[tuple[Cell, ...]] = []
    groups: list[tuple[int, str]] = []
    for k, row in enumerate(table.rows):
        if table.keys is not None and table.keys[k] is None:
            groups.append((len(rows), plain(row[0]) if table.markup else row[0]))
            continue
        cells = tuple(cell(c, table.markup) for c in row)
        if table.footed and k == len(table.rows) - 1:
            cells = tuple(Cell(c.text, "bold") for c in cells)
        rows.append(cells)
    return Table(columns, tuple(rows), tuple(groups))


def table_blocks(title: str, table: CoreTable, level: int = 2) -> list[Block]:
    """A titled core table, left off when it has no rows."""
    if not table.rows:
        return []
    return [Heading(title, level), from_table(table)]


def facts_block(found: Sequence[Fact], columns: int = 4) -> list[Block]:
    pairs = fact_pairs(found)
    return (
        [Facts(tuple((label, plain(value)) for label, value in pairs), columns)]
        if pairs
        else []
    )


def text_blocks(markup_text: str) -> list[Block]:
    """Core markup as paragraphs of plain words."""
    return paragraphs(plain(markup_text))


# ---------------------------------------------------------------- a covenant


def _boons_hooks(covenant: Covenant) -> list[Block]:
    boons, hooks = cvs.boon_hook_points(covenant)
    sides = []
    for kind, points, word in (("Boon", boons, "spent"), ("Hook", hooks, "provided")):
        cards = stacked(
            cvs.boon_hook_cards(covenant, kind),
            lambda c: (c.name, c.tier, c.category, c.note),
        )
        sides.append(
            (
                Heading(f"{kind}s · {points:g} points {word}", 2),
                *(
                    Entry(
                        counted(card.name, n),
                        " · ".join(p for p in (card.tier, card.category) if p),
                        card.note,
                    )
                    for card, n in cards
                ),
            )
            if cards
            else ()
        )
    if not any(sides):
        return []
    return [Columns(sides[0], sides[1])]


def _overview(saga: Saga, covenant: Covenant) -> list[Block]:
    blocks: list[Block] = []
    if covenant.notes.strip():
        blocks += [Heading("The Covenant", 2), *paragraphs(covenant.notes)]
    reputations = cvs.reputations(covenant)
    if reputations:
        blocks += [
            Heading("Reputations", 2),
            Facts(
                tuple(
                    (
                        r.name + ("" if r.known else " (not known to it)"),
                        signed(r.score),
                    )
                    for r in reputations
                )
            ),
        ]
    blocks += _boons_hooks(covenant)
    return [Heading("Overview"), *blocks] if blocks else []


def _charter(saga: Saga, covenant: Covenant) -> list[Block]:
    charter = cc.charter_of(covenant)
    blocks: list[Block] = [Heading(cc.charter_title(charter))]
    blocks += facts_block(cc.facts(saga, covenant))
    blocks += paragraphs(charter.preamble)
    for name, found in cc.grouped(charter):
        if name:
            blocks.append(Heading(name, 2))
        for index in found:
            clause = charter.clauses[index]
            broken = clause.status == cc.CLAUSE_BROKEN
            blocks.append(
                Entry(
                    cc.clause_mark(clause),
                    cc.status_words(clause) if broken else "",
                    clause.text.strip(),
                )
            )
    return blocks if len(blocks) > 1 else []


def _people(saga: Saga, covenant: Covenant) -> list[Block]:
    blocks: list[Block] = []
    for title, people in ov.people_groups(saga, covenant.id):
        blocks += [
            Heading(f"{title} ({len(people)})", 2),
            Table(
                (Column("Name", 0.3), Column("Who", 0.7)),
                tuple(
                    (Cell(c.name, "bold"), Cell(cs.subtitle(saga, c)))
                    for c in viewing.shown(people)
                ),
            ),
        ]
    familiars = fs.familiars_in(saga, covenant.id)
    if familiars:
        blocks += [
            Heading(f"Familiars ({len(familiars)})", 2),
            Table(
                (Column("Name", 0.3), Column("Who", 0.7)),
                tuple(
                    (Cell(card.name, "bold"), Cell(f"{card.subtitle} · {card.detail}"))
                    for card in (fs.familiar_card(saga, f) for f in familiars)
                ),
            ),
        ]
    return [Heading("People"), *blocks] if blocks else []


def _covenfolk(saga: Saga, covenant: Covenant) -> list[Block]:
    loyalty = cvs.loyalty(saga, covenant)
    blocks: list[Block] = [
        Heading("Covenfolk"),
        Facts(
            (
                ("Governance", loyalty.governance or "—"),
                ("Base Loyalty", signed(loyalty.base)),
                ("Modifiers", signed(loyalty.modifiers)),
                ("Loyalty Points", signed(loyalty.points)),
                ("Prevailing Loyalty", signed(loyalty.score)),
            ),
            5,
        ),
    ]
    for group in cvs.inhabitant_groups(saga, covenant):
        blocks += table_blocks(group.title, group.table)
    return blocks


def _laboratories(saga: Saga, covenant: Covenant) -> list[Block]:
    labs = ov.lab_cards(saga, covenant.id)
    if not labs:
        return []
    return [
        Heading(f"Laboratories ({len(labs)})"),
        Table(
            (
                Column("Laboratory", 0.32),
                Column("Whose", 0.32),
                *(Column(f.label, 0.09, "c") for f in labs[0].facts),
            ),
            tuple(
                (
                    Cell(lab.name, "bold"),
                    Cell(lab.subtitle),
                    *(Cell(f.value) for f in lab.facts),
                )
                for lab in labs
            ),
        ),
    ]


def _library(saga: Saga, covenant: Covenant) -> list[Block]:
    shelves = cvs.shelves(saga, covenant)
    if not shelves:
        return []
    count = len(library.books_in_covenant(saga, covenant))
    blocks: list[Block] = [Heading(f"Library ({count})")]
    for title, spines in shelves:
        blocks += [
            Heading(f"{title} ({len(spines)})", 2),
            Table(
                (
                    Column("Title", 0.46),
                    Column("Type", 0.18),
                    Column("Subject", 0.18),
                    Column("Level", 0.09, "c"),
                    Column("Quality", 0.09, "c"),
                ),
                tuple(
                    (
                        Cell(
                            s.book.name,
                            "italic",
                            Symbol("art", s.art)
                            if s.art in FORMS + TECHNIQUES
                            else None,
                        ),
                        Cell(s.book.type),
                        Cell(s.subject),
                        Cell("" if s.level is None else str(s.level)),
                        Cell("" if s.quality is None else str(s.quality)),
                    )
                    for s in spines
                ),
            ),
        ]
    return blocks


def _treasury(saga: Saga, covenant: Covenant) -> list[Block]:
    figures = cvs.treasury(saga, covenant)
    blocks: list[Block] = [
        Heading(f"Treasury · {saga.current_year}"),
        Facts(
            (
                ("Annual Income", f"{figures.income} £"),
                ("Annual Expense", f"{figures.expenditure} £"),
                (
                    "Surplus" if figures.balance >= 0 else "Deficit",
                    f"{figures.balance:+d} £",
                ),
            ),
            3,
        ),
    ]
    if figures.settling:
        blocks.append(Paragraph(figures.settling, "italic"))
    if figures.status:
        blocks.append(Paragraph(plain(figures.status), "bold"))
    blocks += [Heading("Wealth", 2), *facts_block(figures.wealth, 5)]
    blocks += [Heading("What the Year Is Reckoned On", 2)]
    blocks += facts_block(figures.reckoned, 3)
    for group in figures.groups:
        blocks += table_blocks(group.title, group.table)
    blocks += table_blocks("Covering the Deficit", figures.ways_out)
    blocks += table_blocks("Craft by Craft", figures.crafts)
    blocks += table_blocks(figures.purchases.title, figures.purchases.table)
    return blocks


def _inventory(saga: Saga, covenant: Covenant) -> list[Block]:
    """The vis sources, stores and every other possession, then the
    enchanted devices. Raw vis keeps its table even when empty, with
    lines to pencil in."""
    blocks: list[Block] = []
    for group in cvs.possession_groups(saga, covenant):
        blocks += table_blocks(group.title, group.table)
    devices = ed.device_table(saga, "covenant", covenant.id)
    blocks += table_blocks("Enchanted Devices", devices)
    return [Heading("Inventory"), *blocks] if blocks else []


def _diary(covenant: Covenant) -> list[Block]:
    cards = cvs.diary_cards(covenant.diary)
    if not cards:
        return []
    return [
        Heading(f"Diary ({len(cards)})"),
        Table(
            (
                Column("When", 0.15),
                Column("Entry", 0.42),
                Column("Kind", 0.17),
                Column("Amounts", 0.16),
                Column("", 0.10),
            ),
            tuple(
                (
                    Cell(card.when),
                    Cell(card.name or "—", "bold"),
                    Cell(card.category),
                    Cell(card.amounts),
                    Cell(card.status, "italic"),
                )
                for card in cards
            ),
        ),
    ]


def _history(saga: Saga, covenant: Covenant) -> list[Block]:
    found = covenant_history.shown(saga, covenant)
    rows: list[tuple[Cell, ...]] = []
    groups: list[tuple[int, str]] = []
    for name, years, row in found.lines:
        if row is None:
            groups.append((len(rows), f"{name}  {years}".strip() if years else name))
            continue
        rows.append((Cell(row.when), Cell(row.text)))
    if not rows:
        return []
    return [
        Heading(f"History ({len(rows)})"),
        Table(
            (Column("When", 0.18), Column("What happened", 0.82)),
            tuple(rows),
            tuple((i, name) for i, name in groups if name),
        ),
    ]


def _sketch(saga: Saga, covenant: Covenant) -> list[Block]:
    """A Line or Sketch covenant: who it is to the saga, its magi and what
    matters to it."""
    blocks: list[Block] = [*facts_block(cvs.sketch_facts(saga, covenant))]
    if covenant.summary.strip():
        blocks += [Heading("In the Saga", 2), *paragraphs(covenant.summary)]
    if covenant.detail != LINE:
        blocks += table_blocks(
            world_forms.magi_title(saga, covenant),
            world_forms.magi_table(saga, covenant),
        )
        if covenant.what_matters:
            blocks += [
                Heading("What Matters", 2),
                *text_blocks(world_forms.what_matters_text(covenant)),
            ]
    return blocks


def covenant_document(
    saga: Saga,
    covenant: Covenant,
    options: PrintOptions = DEFAULT_OPTIONS,
    reader: Viewer = viewing.STORYGUIDE_VIEWER,
) -> Document:
    """A covenant's whole printed record: its Overview, Charter, People
    and Covenfolk, Laboratories a line each, Library, Treasury and
    Inventory, then its Diary, History and the Secrets the copy may hold.
    Seasons, Build and Manage are for the screen. A Line or Sketch
    covenant prints what it is to the saga, its Charter and its Diary."""
    subtitle = plain(cvs.subtitle(saga, covenant))
    aura = cvs.aura(covenant)
    blocks: list[Block] = [
        Title(covenant.name, subtitle),
        Facts(
            (
                ("Aura", f"{aura.total} {aura.realm}"),
                *fact_pairs(cvs.charter_facts(saga, covenant), reader),
            )
        ),
    ]
    if covenant.detail != FULL:
        blocks += _sketch(saga, covenant)
        blocks += _charter(saga, covenant)
        blocks += _diary(covenant)
    else:
        blocks += _overview(saga, covenant)
        blocks += _charter(saga, covenant)
        blocks += _people(saga, covenant)
        blocks += _covenfolk(saga, covenant)
        blocks += _laboratories(saga, covenant)
        blocks += _library(saga, covenant)
        blocks += _treasury(saga, covenant)
        blocks += _inventory(saga, covenant)
        blocks += _diary(covenant)
        blocks += _history(saga, covenant)
    secrets = secrets_blocks(covenant)
    if secrets:
        blocks += [NewPage(soft=True), *secrets]
    return Document(covenant.name, subtitle, blocks)


# ---------------------------------------------------------------- a laboratory


#: How many of the best Lab Totals are set in bold.
BEST = 5


def _lab_totals(saga: Saga, lab: Laboratory) -> list[Block]:
    """The owner's Lab Total for each Technique and Form, as the Casting
    Scores are set, the best few in bold (on screen a heat map)."""
    totals = ls.lab_totals(saga, lab)
    if totals is None:
        return []
    values = {key: int(total.total) for key, total in totals.items()}
    best = sorted(set(values.values()), reverse=True)[:BEST]
    return [
        Heading("Lab Totals"),
        Table(
            (Column("", 0.17),)
            + tuple(Column(ART_ABBREVIATIONS[f], 0.083, "c") for f in FORMS),
            tuple(
                (Cell(t, "italic", Symbol("art", t)),)
                + tuple(
                    Cell(str(values[(t, f)]), "bold" if values[(t, f)] in best else "")
                    for f in FORMS
                )
                for t in TECHNIQUES
            ),
        ),
        Paragraph(
            f"Lab Total before any season's own bonuses; the {BEST} best in bold.",
            "italic",
            "small",
        ),
    ]


def _lab_virtues_flaws(saga: Saga, lab: Laboratory) -> list[Block]:
    stream = virtue_flaw_columns(
        [
            (label, ls.virtue_flaw_cards(lab, side, saga), None)
            for side, label in (("Virtue", "Virtues"), ("Flaw", "Flaws"))
        ]
    )
    return [Heading("Virtues & Flaws"), *stream] if stream else []


def _named(title: str, entries: Sequence[Any]) -> list[Block]:
    """Rooms or Equipment & Stores: each by name, with its description."""
    if not entries:
        return []
    blocks: list[Block] = [Heading(f"{title} ({len(entries)})", 2)]
    for entry in entries:
        words = entry.description.strip()
        blocks.append(Paragraph(f"{entry.name}{': ' + words if words else ''}"))
    return blocks


def _specializations(saga: Saga, lab: Laboratory) -> list[Block]:
    rows = ls.specializations(saga, lab)
    features = ls.feature_cards(lab)
    items = ls.item_cards(saga, lab)
    blocks: list[Block] = []
    if rows:
        blocks += [
            Heading("Specializations", 2),
            Table(
                (
                    Column("Specialization", 0.5),
                    Column("Kind", 0.25),
                    Column("Points", 0.25, "c"),
                ),
                tuple(
                    (
                        Cell(s.name),
                        Cell(s.kind),
                        Cell(
                            signed(s.points) + ("" if s.counts else " (off)"),
                            "bold" if s.counts else "struck",
                        ),
                    )
                    for s in rows
                ),
            ),
        ]
    if features:
        blocks += [
            Heading(f"Features ({len(features)})", 2),
            *(Entry(f.name, f.kind, f.problem) for f in features),
        ]
    if items:
        blocks += [
            Heading(f"Magic Items ({len(items)})", 2),
            *(Entry(i.name, "", i.gives) for i in items),
        ]
    blocks += _named("Rooms", lab.rooms)
    return [Heading("Specializations, Features & Rooms"), *blocks] if blocks else []


def _stores(saga: Saga, lab: Laboratory) -> list[Block]:
    """Raw vis (kept, with lines to pencil in, even when there is none),
    equipment and stores, Arcane Connections, Lab Texts and books."""
    vis = {art: n for art, n in lab.raw_vis.items() if n}
    blocks: list[Block] = [Heading("Stores"), Heading("Raw Vis", 2)]
    if vis:
        blocks.append(
            Facts(
                tuple(
                    (art.title(), f"{n} pawn{'' if n == 1 else 's'}")
                    for art, n in sorted(vis.items())
                ),
                5,
            )
        )
    blocks.append(Blanks(1 if vis else 2))
    blocks += _named("Equipment & Stores", lab.inventory_items)
    if lab.arcane_connections:
        blocks += [
            Heading(f"Arcane Connections ({len(lab.arcane_connections)})", 2),
            *(Paragraph(c.to) for c in lab.arcane_connections),
        ]
    for title, books in (
        ("Lab Texts", lt.texts_of(saga, "laboratory", lab.id)),
        ("Books", lt.other_books_of(saga, "laboratory", lab.id)),
    ):
        if books:
            blocks += [
                Heading(f"{title} ({len(books)})", 2),
                Table(
                    (
                        Column("Title", 0.6),
                        Column("Type", 0.25),
                        Column("Level", 0.15, "c"),
                    ),
                    tuple(
                        (
                            Cell(b.name, "italic"),
                            Cell(b.type),
                            Cell(str(b.level) if b.level else ""),
                        )
                        for b in books
                    ),
                ),
            ]
    return blocks


def _lab_diary(lab: Laboratory) -> list[Block]:
    if not lab.diary:
        return []
    return [
        Heading(f"Diary ({len(lab.diary)})"),
        Table(
            (Column("Season", 0.18), Column("Activity", 0.24), Column("Entry", 0.58)),
            tuple(
                (Cell(f"{e.season} {e.year}"), Cell(e.activity or ""), Cell(e.name))
                for e in lab.diary
            ),
        ),
    ]


def laboratory_document(
    saga: Saga,
    lab: Laboratory,
    options: PrintOptions = DEFAULT_OPTIONS,
    reader: Viewer = viewing.STORYGUIDE_VIEWER,
) -> Document:
    """A laboratory's whole printed record: its Characteristics, its
    owner's Lab Totals, Virtues and Flaws, Specializations, Features and
    rooms, its stores and Lab Texts, and its Diary. Planning and Manage
    are for the screen."""
    # The location goes with the facts: a line of prose won't fit the title's.
    subtitle = plain(ls.subtitle(saga, lab)).replace(f"  ·  {lab.location}", "")
    aura = ls.aura(saga, lab)
    characteristics = ls.characteristics(lab, saga)
    blocks: list[Block] = [
        Title(lab.name, subtitle),
        ScoreBoxes(tuple((c.name, signed(c.total)) for c in characteristics)),
        Facts(
            (
                ("Aura", f"{aura.total} {aura.realm}"),
                *fact_pairs(ls.capacity_facts(lab), reader),
            )
        ),
    ]
    if lab.location.strip():
        blocks.append(Paragraph(lab.location.strip(), "italic"))
    blocks += traits_blocks(lab.personality_traits, ())
    blocks += _lab_totals(saga, lab)
    blocks += _lab_virtues_flaws(saga, lab)
    blocks += _specializations(saga, lab)
    blocks += _stores(saga, lab)
    blocks += _lab_diary(lab)
    return Document(lab.name, subtitle, blocks)


# ---------------------------------------------------------------- a familiar


def familiar_document(
    saga: Saga,
    familiar: Familiar,
    options: PrintOptions = DEFAULT_OPTIONS,
    reader: Viewer = viewing.STORYGUIDE_VIEWER,
) -> Document:
    """A familiar's printed sheet: who it is and whose; its
    Characteristics; Might, Size and combat; the Cords and the binding;
    its Bond Powers, Abilities, Virtues and Flaws and Personality Traits."""
    subtitle = plain(fs.subtitle(saga, familiar))
    magus = fam.magus_of(saga, familiar)
    name = familiar.name or "Familiar"
    pool = fs.might_pool(familiar)
    blocks: list[Block] = [
        Title(name, subtitle),
        ScoreBoxes(
            tuple(
                (label, signed(getattr(familiar.characteristics, label.lower())))
                for label in (
                    "Intelligence",
                    "Perception",
                    "Strength",
                    "Stamina",
                    "Presence",
                    "Communication",
                    "Dexterity",
                    "Quickness",
                )
            )
        ),
        Facts(
            (
                ("Master", magus.name if magus else "—"),
                ("Species", familiar.species or "—"),
                (
                    "Magic Might",
                    str(familiar.magic_might) + (f" ({pool})" if pool else ""),
                ),
                *fact_pairs(fs.header_facts(familiar), reader),
            )
        ),
    ]
    blocks += [
        Heading("Cords & Binding"),
        Table(
            (
                Column("Cord", 0.2),
                Column("Score", 0.1, "c"),
                Column("Cost", 0.1, "c"),
                Column("What it does", 0.6),
            ),
            tuple(
                (
                    Cell(c.name, "bold"),
                    Cell(str(c.score)),
                    Cell(str(c.cost)),
                    Cell(c.effect),
                )
                for c in fs.cords(familiar)
            ),
        ),
        *facts_block(fs.binding_facts(familiar)),
    ]
    blocks += _bond_powers(familiar)
    blocks += _familiar_combat(familiar)
    blocks += abilities_blocks(fs.ability_table(familiar))
    columns = virtue_flaw_columns(
        [
            (label, fs.vf_cards(familiar, side), fs.vf_points(familiar, side))
            for side, label in (("Virtue", "Virtues"), ("Flaw", "Flaws"))
        ]
    )
    if columns:
        blocks += [Heading("Virtues & Flaws"), *columns]
    blocks += traits_blocks(familiar.personality_traits, familiar.reputations)
    return Document(name, subtitle, blocks)


def _bond_powers(familiar: Familiar) -> list[Block]:
    powers = fs.bond_power_cards(familiar)
    if not powers:
        return []
    return [
        Heading("Bond Powers"),
        Table(
            (
                Column("Power", 0.4),
                Column("Arts", 0.2),
                Column("Level", 0.13, "c"),
                Column("Uses / day", 0.14, "c"),
                Column("Penetration", 0.13, "c"),
            ),
            tuple(
                (
                    Cell(
                        p.name,
                        "bold",
                        Symbol("art", p.form) if p.form in FORMS else None,
                    ),
                    Cell(p.arts),
                    Cell(str(p.level)),
                    Cell(str(p.uses_per_day)),
                    Cell(str(p.penetration)),
                )
                for p in powers
            ),
        ),
    ]


def _familiar_combat(familiar: Familiar) -> list[Block]:
    return [
        Heading("Combat & Condition"),
        condition_from(fs.fatigue_track(familiar), fs.wound_track(familiar)),
        # Soak and Magic Resistance are already under its name.
        *facts_block(
            [
                f
                for f in fs.health_facts(familiar)
                if f.label not in ("Base Soak", "Magic Resistance")
            ]
        ),
        *table_blocks("Natural Weapons", fs.natural_weapons(familiar)),
    ]


# ---------------------------------------------------------------- the registry

#: A layout: the saga, the record (as the copy's reader may read it), the
#: options, and the reader, for facts that name other records.
Layout = Callable[[Saga, Any, PrintOptions, Viewer], Document]

#: Each record kind's printed sheet, by transfer's kind names.
LAYOUTS: dict[str, Layout] = {
    "character": character_document,
    "covenant": covenant_document,
    "laboratory": laboratory_document,
    "familiar": familiar_document,
}


def document(
    saga: Saga,
    kind: str,
    record: Any,
    options: PrintOptions = DEFAULT_OPTIONS,
    viewer: Viewer | None = None,
) -> Document:
    """The printed sheet of `record`, a record of `kind`, in the copy
    `options` chooses for `viewer` (by default whoever is looking): built
    while viewing reads as that copy's reader, from the record as they may
    read it. KeyError for a kind that can't be printed."""
    reader = reader_for(options.copy, viewer or viewing.current(), saga)
    with viewing.reading_as(reader, saga):
        shown = viewing.as_read_by(record, reader, saga)
        return LAYOUTS[kind](saga, shown, options, reader)


# ---------------------------------------------------------------- themes

#: The themes a sheet can be printed in, by name, in the Settings order.
THEME_PALETTES: tuple[Palette, ...] = (SCRIPTORUM, SCRIPTORUM_DARK, *HOUSES)
THEME_NAMES = tuple(p.name for p in THEME_PALETTES)
#: A dark theme's light twin, printed on plain white.
LIGHT_TWINS = {SCRIPTORUM_DARK.name: SCRIPTORUM.name}


def _letters(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower().replace("æ", "ae"))


def magus_of(saga: Saga, record: Any) -> Character | None:
    """The magus whose House colours `record` prints in: a magus, the
    owner of a laboratory, the master of a familiar; else None."""
    if isinstance(record, Laboratory):
        record = saga.character(record.owner_id) if record.owner_id else None
    elif isinstance(record, Familiar):
        record = fam.magus_of(saga, record)
    return record if isinstance(record, Character) and record.type == "magus" else None


def theme_for(saga: Saga | None, record: Any, choice: str) -> str:
    """The theme `record` of `saga` prints in: the one `choice` names, or
    with HOUSE_COLOURS its magus's House theme (Scriptorum for a covenant,
    a companion or grog, a House with no theme, or no record at all, as a
    session's handout)."""
    if choice != HOUSE_COLOURS:
        return choice if choice in THEME_NAMES else SCRIPTORUM.name
    magus = magus_of(saga, record) if saga is not None else None
    house = cs.house_name(magus) if magus is not None else None
    if house:
        for name in THEME_NAMES:
            if _letters(name) == _letters(house):
                return name
    return SCRIPTORUM.name


def printed_palette(theme: str, textured: bool) -> Palette:
    """The colours a sheet in `theme` is printed in: the theme's own; on
    plain white a dark theme's light twin, so no pale ink is put on white
    (Scriptorum's colours for a dark House theme, which has none yet)."""
    palette = next((p for p in THEME_PALETTES if p.name == theme), SCRIPTORUM)
    if textured or not palette.dark:
        return palette
    twin = LIGHT_TWINS.get(palette.name, SCRIPTORUM.name)
    return next(p for p in THEME_PALETTES if p.name == twin)


def file_stem(name: str) -> str:
    """`name` as a file name: without the characters Windows refuses."""
    return re.sub(r'[\\/:*?"<>|]', "", name).strip() or "Untitled"


def troupe_sheets(
    saga: Saga,
    options: PrintOptions = DEFAULT_OPTIONS,
    viewer: Viewer | None = None,
) -> list[tuple[Document, str]]:
    """Each player character's sheet (troupe.player_characters' order, by
    covenant) with the theme it prints in, for one PDF of the troupe: the
    copy, sheet and theme `options` choose, for `viewer`."""
    return [
        (
            document(saga, "character", character, options, viewer),
            theme_for(saga, character, options.theme),
        )
        for _covenant, members in troupe.player_characters(saga)
        for character in members
    ]


#: The record each LAYOUTS kind prints.
KINDS: tuple[tuple[str, type], ...] = (
    ("character", Character),
    ("covenant", Covenant),
    ("laboratory", Laboratory),
    ("familiar", Familiar),
)


def kind_of(record: Any) -> str | None:
    """The LAYOUTS kind `record` prints as; None for a record that has no
    printed sheet."""
    return next((kind for kind, cls in KINDS if isinstance(record, cls)), None)
