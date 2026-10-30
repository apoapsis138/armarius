"""The figures a graphical Saga Content page draws, without a front-end.

The terminal view's text is in saga_content.py; these are the same facts
as plain values (character_sheet.Fact, cards, covenant_sheet.Table), so
the desktop page can give each its own type.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any

from .. import book_kinds, book_overviews, sourcebooks, traditions
from .. import house_rules as hr
from .. import own_abilities as oa
from .. import players as pl
from .. import saga_content as sc
from .. import spells as spl
from ..markup import escape
from ..models import AbilityDef, Saga, Spell
from ..models.mystery_cults import is_saga_cult
from ..references import Fact
from ..rules import activities
from ..rules import options as rule_options
from .covenant import Table

ALWAYS, IN_PLAY, OUT_OF_PLAY = "Always", "In play", "Not in play"


def header_facts(saga: Saga) -> list[Fact]:
    every = sc.every_book(saga)
    in_play = sum(1 for b in every if sc.is_in_play(saga, b))
    return [
        Fact("Books in Play", f"{in_play} of {len(every)}"),
        Fact("House Rules", str(len(hr.all_entries(saga)))),
        Fact("The Saga's Spells", str(len(saga.spells))),
        Fact("Hidden Entries", str(len(sc.hidden_entries(saga)))),
    ]


@dataclass(frozen=True)
class BookCard:
    """A book the saga can have in play: its abbreviation, title, whether
    it is in play, whether it is one of the saga's own sources, and what
    it brings (brought), "" for nothing the app counts."""

    book: str
    title: str
    state: str
    own: bool
    brings: str = ""


#: A card's line for a book that brings nothing the app counts.
NOTHING_COUNTED = "Nothing the app counts yet"

#: The books each thing that names one cites, one book-set per thing.
Cited = Callable[[Saga], Iterable[set[str]]]


def _catalog(key: str, own: Callable[[Saga], Sequence[Any]]) -> Cited:
    """A shared catalog's entries and the saga's own of that kind, by the
    books their `source` cites; the catalog is listed once a call."""

    def cited(saga: Saga) -> list[set[str]]:
        entries = (*sc.CATALOGS[key].shared(), *own(saga))
        return [sourcebooks.books_of(e.source) for e in entries]

    return cited


def _named(books: Callable[[], Iterable[str]]) -> Cited:
    """A rules registry whose entries each name one book ("" the core)."""
    return lambda _saga: [{book or sourcebooks.CORE} for book in books()]


#: What a book can bring, each as (one, many, the books its entries cite),
#: in the order a card lists them.
BRINGS: tuple[tuple[str, str, Cited], ...] = (
    (
        "Virtue or Flaw",
        "Virtues & Flaws",
        _catalog("virtues_flaws", lambda s: s.custom_virtues_flaws),
    ),
    (
        "Laboratory Virtue or Flaw",
        "Laboratory Virtues & Flaws",
        _catalog("lab_virtues_flaws", lambda s: s.custom_lab_virtues_flaws),
    ),
    (
        "Boon or Hook",
        "Boons & Hooks",
        _catalog("boons_hooks", lambda s: s.custom_boons_hooks),
    ),
    ("Ability", "Abilities", _catalog("abilities", lambda s: s.custom_abilities)),
    ("spell", "spells", _catalog("spells", lambda s: s.spells)),
    (
        "Shape or Material",
        "Shapes & Materials",
        _catalog("shapes_materials", lambda _s: ()),
    ),
    ("Good", "Goods", _catalog("goods", lambda s: s.custom_goods)),
    (
        "optional rule",
        "optional rules",
        _named(lambda: (o.book for o in rule_options.OPTIONS)),
    ),
    (
        "season activity",
        "season activities",
        _named(
            lambda: (a.book for a in activities.ACTIVITIES.values() if not a.hidden)
        ),
    ),
    (
        "kind of book",
        "kinds of book",
        _named(
            lambda: (
                k.book
                for kinds in (
                    book_kinds.OPUS_TYPES,
                    book_kinds.PHYSICAL_FORMS,
                    book_kinds.COLLECTIONS,
                )
                for k in kinds.values()
            )
        ),
    ),
    (
        "Mystery Cult",
        "Mystery Cults",
        lambda saga: [sourcebooks.books_of(c.source) for c in saga.custom_cults],
    ),
    (
        "tradition",
        "traditions",
        lambda _saga: [
            sourcebooks.books_of(t.source)
            for t in traditions.all_traditions()
            if not is_saga_cult(t.id)
        ],
    ),
)


def brought(saga: Saga) -> dict[str, str]:
    """What each book brings, in plain words ("27 Virtues & Flaws, 4
    Abilities"), the zeros left out; a book bringing nothing counted is
    missing. One pass over each catalog and registry for every book."""
    counts: dict[str, Counter[int]] = {}
    for index, (_one, _many, cited) in enumerate(BRINGS):
        for books in cited(saga):
            for book in books:
                counts.setdefault(book, Counter())[index] += 1
    return {
        book: ", ".join(
            f"{n} {BRINGS[i][0] if n == 1 else BRINGS[i][1]}"
            for i, n in sorted(counted.items())
        )
        for book, counted in counts.items()
    }


def _special_rules(book: str) -> list[str]:
    """What a book adds beyond its catalog entries, as lines (markup): its
    optional rules, and for a supplement its seasons, kinds of book and
    traditions, by name. The core book's seasons are the game's own."""
    named = [
        (
            "Optional rules",
            [
                o.label
                for o in rule_options.OPTIONS
                if (o.book or sourcebooks.CORE) == book
            ],
        ),
    ]
    if book != sourcebooks.CORE:
        kinds = (
            *book_kinds.OPUS_TYPES.values(),
            *book_kinds.PHYSICAL_FORMS.values(),
            *book_kinds.COLLECTIONS.values(),
        )
        named += [
            (
                "Season activities",
                [
                    a.label
                    for a in activities.ACTIVITIES.values()
                    if a.book == book and not a.hidden
                ],
            ),
            ("Kinds of book", [k.name for k in kinds if k.book == book]),
            (
                "Traditions",
                [
                    t.name
                    for t in traditions.all_traditions()
                    if not is_saga_cult(t.id) and book in sourcebooks.books_of(t.source)
                ],
            ),
        ]
    return [
        f"[b]{label}:[/] {escape(', '.join(names))}" for label, names in named if names
    ]


def book_text(saga: Saga, book: str | None) -> str:
    """A book's details (markup): whether it is in play, what it is, how
    much it holds and its special rules. A saga source: what cites it."""
    head = sc.book_detail(saga, book)
    if book is None:
        return head
    holds = brought(saga).get(book, NOTHING_COUNTED)
    if book in sourcebooks.saga_sources(saga):
        cited = ", ".join(e.name for e in hr.citing(saga, book))
        lines = [head, f"[b]Holds:[/] {escape(holds)}"]
        return "\n".join(
            lines + ([f"[b]Cited by:[/] {escape(cited)}"] if cited else [])
        )
    return "\n".join(
        [
            head,
            escape(book_overviews.overview(book)),
            f"[b]Holds:[/] {escape(holds)}",
            *_special_rules(book),
        ]
    )


def book_cards(saga: Saga) -> list[BookCard]:
    own = sourcebooks.saga_sources(saga)
    brings = brought(saga)
    return [
        BookCard(
            book,
            sourcebooks.title_of(book, saga),
            ALWAYS
            if book == sourcebooks.CORE
            else IN_PLAY
            if sc.is_in_play(saga, book)
            else OUT_OF_PLAY,
            book in own,
            brings.get(book, ""),
        )
        for book in sc.every_book(saga)
    ]


@dataclass(frozen=True)
class BookGroup:
    """A heading of the Books chapter and its cards; consecutive groups
    with one `heading` (The Order) differ by `subheading`."""

    heading: str
    subheading: str
    cards: tuple[BookCard, ...]


def book_groups(saga: Saga, cards: Sequence[BookCard]) -> list[BookGroup]:
    """`cards` (book_cards) grouped: the core book, the supplements in
    sourcebooks.BOOK_GROUPS (a group with none of its books in the app
    left out), any supplement no group names, then the saga's own
    sources."""
    by_book = {card.book: card for card in cards}
    groups = [BookGroup("The Core Book", "", (by_book[sourcebooks.CORE],))]
    grouped: set[str] = {sourcebooks.CORE}
    for heading, subheading, books in sourcebooks.BOOK_GROUPS:
        shown = tuple(by_book[b] for b in books if b in by_book)
        grouped.update(books)
        if shown:
            groups.append(BookGroup(heading, subheading, shown))
    rest = tuple(
        by_book[b] for b in sourcebooks.SUPPLEMENTS if b not in grouped and b in by_book
    )
    if rest:
        groups.append(BookGroup("Other Books", "", rest))
    own = tuple(c for c in cards if c.own)
    if own:
        groups.append(BookGroup("The Saga's Own Sources", "", own))
    return groups


def sources_table(saga: Saga) -> Table:
    return Table(
        ["Source", "Title", "Entries"],
        [
            [s.abbreviation, s.title, str(len(hr.citing(saga, s.abbreviation)))]
            for s in saga.sources
        ],
    )


#: A book heading's chip: whether the saga offers its traditions.
ALL_OFFERED, SOME_OFFERED, NONE_OFFERED = "All offered", "Some offered", "None offered"
#: A heading's chip while its book is out of play.
BOOK_OUT = "Book not in play"


@dataclass(frozen=True)
class TraditionRow:
    """A tradition under its book: what kind it is (traditions.type_line)
    and whether the saga offers it."""

    id: str
    name: str
    on: bool
    kind: str


@dataclass(frozen=True)
class TraditionGroup:
    """A book's traditions: its title, whether it is in play (its
    traditions greyed out when not) and how many the saga offers."""

    book: str
    title: str
    in_play: bool
    rows: tuple[TraditionRow, ...]

    @property
    def state(self) -> str:
        if not self.in_play:
            return BOOK_OUT
        on = sum(row.on for row in self.rows)
        if on == len(self.rows):
            return ALL_OFFERED
        return SOME_OFFERED if on else NONE_OFFERED


def tradition_groups(saga: Saga) -> list[TraditionGroup]:
    """Every non-Hermetic tradition under its book, in the Books chapter's
    order, books out of play too."""
    groups: dict[str, list[TraditionRow]] = {}
    for t in traditions.listed(saga):
        groups.setdefault(traditions.book_of(t, saga), []).append(
            TraditionRow(
                t.id, t.name, traditions.is_on(saga, t.id), traditions.type_line(t)
            )
        )
    return [
        TraditionGroup(
            book,
            sourcebooks.title_of(book, saga) or book,
            sc.is_in_play(saga, book),
            tuple(rows),
        )
        for book, rows in groups.items()
    ]


def catalogs_table(saga: Saga) -> Table:
    return Table(
        ["Catalog", "Offered", "Entries", "Hidden"],
        [
            [
                info.label,
                "No" if key in saga.hidden_catalogs else "Yes",
                str(len(info.shared())),
                str(len(sc.hidden_ids(saga, key))),
            ]
            for key, info in sc.CATALOGS.items()
        ],
    )


def hidden_table(saga: Saga) -> Table:
    return Table(
        ["Entry", "Catalog"],
        [
            [entry.name, sc.CATALOGS[key].label]
            for key, entry in sc.hidden_entries(saga)
        ],
    )


@dataclass(frozen=True)
class HouseRuleCard:
    """A user-made entry as a card: `index` into hr.all_entries, what it is
    for, and whether it gives points (a Flaw or Hook) or costs them."""

    index: int
    name: str
    kind: str
    type: str
    tier: str
    category: str
    points: str
    gives: bool


def house_rule_cards(saga: Saga) -> list[HouseRuleCard]:
    return [
        _ability_card(index, entry)
        if isinstance(entry, AbilityDef)
        else HouseRuleCard(
            index,
            entry.name,
            hr.KIND_SHORT[kind],
            entry.type,
            entry.tier,
            entry.category,
            hr.points_text(entry.type, entry.tier),
            entry.type in ("Flaw", "Hook"),
        )
        for index, (kind, entry) in enumerate(hr.all_entries(saga))
    ]


def _ability_card(index: int, ability: AbilityDef) -> HouseRuleCard:
    """One of the saga's own Abilities ("Supernatural Ability"): its realm
    where a Virtue's tier goes, and what it rolls where the points go."""
    return HouseRuleCard(
        index,
        ability.name,
        ability.category,
        "Ability",
        ability.realm or "Ability",
        oa.summary(ability),
        f"Rolls {oa.roll_text(ability)}",
        False,
    )


@dataclass(frozen=True)
class SpellRow:
    """One spell as a table row; `level` is None for a General spell, so
    the table sorts by number."""

    name: str
    arts: str
    form: str
    level: int | None
    rdt: str
    ritual: bool
    source: str

    @property
    def level_text(self) -> str:
        return "Gen" if self.level is None else str(self.level)


def spell_rows(saga: Saga, spells: Sequence[Spell]) -> list[SpellRow]:
    return [
        SpellRow(
            spell.name,
            spl.arts(spell),
            spell.form,
            spell.level,
            spl.rdt_text(spell),
            spell.ritual,
            spl.source_label(saga, spell),
        )
        for spell in spells
    ]


def players_table(saga: Saga) -> Table:
    return Table(
        ["Name", "Role", "Plays"],
        [
            [
                player.name,
                pl.ROLE_LABELS.get(player.role, player.role),
                ", ".join(c.name for c in pl.characters_of(saga, player)),
            ]
            for player in saga.players
        ],
    )
