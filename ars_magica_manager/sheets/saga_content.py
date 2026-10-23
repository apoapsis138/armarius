"""The figures a graphical Saga Content page draws, without a front-end.

The terminal view's text is in saga_content.py; these are the same facts
as plain values (character_sheet.Fact, cards, covenant_sheet.Table), so
the desktop page can give each its own type.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from .. import house_rules as hr
from .. import players as pl
from .. import saga_content as sc
from .. import sourcebooks, traditions
from .. import spells as spl
from ..models import Saga, Spell
from ..references import Fact
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
    it is in play, and whether it is one of the saga's own sources."""

    book: str
    title: str
    state: str
    own: bool


def book_cards(saga: Saga) -> list[BookCard]:
    own = sourcebooks.saga_sources(saga)
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
        )
        for book in sc.every_book(saga)
    ]


def sources_table(saga: Saga) -> Table:
    return Table(
        ["Source", "Title", "Entries"],
        [
            [s.abbreviation, s.title, str(len(hr.citing(saga, s.abbreviation)))]
            for s in saga.sources
        ],
    )


def traditions_table(saga: Saga) -> Table:
    """The non-Hermetic traditions whose book is in play, and whether the
    saga offers each."""
    return Table(
        ["Tradition", "Book", "Offered"],
        [
            [t.name, t.source, "Yes" if traditions.is_on(saga, t.id) else "No"]
            for t in traditions.in_play(saga)
        ],
    )


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
        HouseRuleCard(
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
            "Saga" if spl.is_own(saga, spell) else spell.source,
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
