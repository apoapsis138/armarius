"""The saga's index of records, for Find: every record a page can open,
with its name, what kind it is and where it is, and the other words it
can be found by.

Each kind of record lists itself: a function from the saga to its
entries, kept in KINDS by the kind's name (Strategy, reduced to a dict of
functions, as references.py keeps its openers). A front-end builds the
index once when its finder opens (`entries`) and asks `search` again on
each keystroke, so neither front-end knows how a kind is found.

A record is found by its name first; then a faction by its members'
names, a record by the place it is in, and by the Tribunal whose lands
that place is (places.lands_of). Secrets, notes and descriptions are not
searched, nor season records or the calendar.

Books, spells and enchanted devices have no page of their own: each
opens the page that holds it (its owner, the magus who knows it, its
holder) at its row, the entry's Spot, and one held by nobody is left out.
A Spot names the list, not a front-end's tab or chapter: each front-end
keeps its own table of where a page shows each list (a parameter object
the openers take, as Help's Go there takes a place)."""

from __future__ import annotations

import unicodedata
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from functools import cache
from typing import Any

from . import catalog, memberships, neighbours, places, references
from . import enchanted_devices as ed
from . import familiars as fam
from .models import Character, Saga
from .references import Ref
from .rules import sites

#: What a match's place and the words after it are joined with.
SEPARATOR = " · "

#: The lists a Spot names, on the page its entry opens.
BOOKS, DEVICES, SPELLS = "books", "devices", "spells"


@dataclass(frozen=True)
class Spot:
    """Where on the page it opens an entry is: the list (BOOKS, DEVICES,
    SPELLS) and the record's id, to choose its row."""

    list: str
    record_id: str


@dataclass(frozen=True)
class Entry:
    """One record as Find lists it: the Ref that opens it (a book's is
    its owner's), its name, what kind it is ("Lord", "Book"), where it is
    ("" for nowhere), and the other words it is found by, each with the
    reason shown beside a match on it."""

    ref: Ref
    name: str
    kind: str
    place: str = ""
    #: (how a match on them is shown, the words), each how one of
    #: _ALSO_RANKS.
    also: tuple[tuple[str, str], ...] = ()
    #: The row it is on that page, for a record shown on another's.
    spot: Spot | None = None

    @property
    def line(self) -> str:
        """ "Gottfried of Arnsberg · Lord · The Drachenfels"."""
        return SEPARATOR.join(
            part for part in (self.name, self.kind, self.place) if part
        )


@dataclass(frozen=True)
class Match:
    """An entry a search found, and why when it wasn't by its name
    ("member: Gottfried of Arnsberg"); `rank` orders the matches."""

    entry: Entry
    rank: int
    why: str = ""
    #: The words matched, when not the name.
    words: str = ""

    @property
    def note(self) -> str:
        """Why, as a list shows it beside the match: "" when the place
        shown already says it (a match at The Drachenfels, there)."""
        return "" if self.words and self.words in self.entry.place else self.why

    @property
    def line(self) -> str:
        return self.entry.line


# -- where a record is --


def _where(saga: Saga, place_id: str | None, level: int = 0) -> str:
    return places.where_text(saga, place_id, level)


def _lands(saga: Saga, record: Any) -> tuple[tuple[str, str], ...]:
    """The Tribunal whose lands `record` lies in, as words to find it by."""
    tribunal = places.lands_of(saga, record)
    return (("in the lands of", tribunal.name),) if tribunal is not None else ()


def _placed(place: str) -> tuple[tuple[str, str], ...]:
    return (("at", place),) if place else ()


# -- each kind of record --


def _characters(saga: Saga) -> Iterator[Entry]:
    for character in saga.characters:
        home = saga.covenant(character.covenant_id)
        place = home.name if home is not None else ""
        found = references.ref(character)
        assert found is not None
        yield Entry(
            found,
            character.name,
            character.type.title(),
            place,
            _placed(place) + _lands(saga, character),
        )


def _covenants(saga: Saga) -> Iterator[Entry]:
    for covenant in saga.covenants:
        at = sites.covenant_place(saga, covenant)
        place = _where(saga, at[0].id, at[1]) if at is not None else ""
        found = references.ref(covenant)
        assert found is not None
        yield Entry(
            found,
            covenant.name,
            "Covenant",
            place,
            _placed(place) + _lands(saga, covenant),
        )


def _laboratories(saga: Saga) -> Iterator[Entry]:
    for lab in saga.laboratories:
        place = _where(saga, lab.place_id)
        if not place:
            home = saga.covenant(lab.covenant_id)
            place = home.name if home is not None else ""
        found = references.ref(lab)
        assert found is not None
        yield Entry(
            found, lab.name, "Laboratory", place, _placed(place) + _lands(saga, lab)
        )


def _familiars(saga: Saga) -> Iterator[Entry]:
    for familiar in saga.familiars:
        magus = fam.magus_of(saga, familiar)
        place = f"of {magus.name}" if magus is not None else ""
        also = ()
        if magus is not None:
            also = (("familiar of", magus.name), *_lands(saga, magus))
        found = references.ref(familiar)
        assert found is not None
        name = familiar.name or familiar.species or "(an unnamed familiar)"
        yield Entry(found, name, "Familiar", place, also)


def _tribunals(saga: Saga) -> Iterator[Entry]:
    for tribunal in saga.tribunals:
        found = references.ref(tribunal)
        assert found is not None
        yield Entry(found, tribunal.name, "Tribunal")


def _neighbours(saga: Saga) -> Iterator[Entry]:
    for neighbour in saga.neighbours:
        place = _where(saga, neighbour.place_id, neighbour.place_level)
        members: tuple[tuple[str, str], ...] = ()
        if neighbour.kind == "faction":
            members = tuple(
                ("member", member.name)
                for member, _ in memberships.members(saga, neighbour)
            )
        found = references.ref(neighbour)
        assert found is not None
        yield Entry(
            found,
            neighbour.name,
            neighbours.kind_of(neighbour).name,
            place,
            members + _placed(place) + _lands(saga, neighbour),
        )


def _creatures(saga: Saga) -> Iterator[Entry]:
    for creature in saga.creatures:
        place = _where(saga, creature.place_id)
        found = references.ref(creature)
        assert found is not None
        yield Entry(
            found,
            creature.name,
            "Creature",
            place,
            _placed(place) + _lands(saga, creature),
        )


#: A book's or device's owner kind (models.BOOK_OWNER_KINDS,
#: DEVICE_HOLDER_KINDS) as the saga's list of them.
_HOLDERS: dict[str, Callable[[Saga, str | None], Any]] = {
    "covenant": Saga.covenant,
    "laboratory": Saga.laboratory,
    "character": Saga.character,
}


def _holder(saga: Saga, kind: str | None, holder_id: str | None) -> Any | None:
    look_up = _HOLDERS.get(kind or "")
    return look_up(saga, holder_id) if look_up is not None else None


def _held(
    saga: Saga, record: Any, kind: str, holder: Any | None, listed: str
) -> Entry | None:
    """An entry for a book or device, opening its holder's page at its
    row of the `listed` list."""
    opens = references.ref(holder)
    if holder is None or opens is None:
        return None
    return Entry(
        opens,
        record.name,
        kind,
        holder.name,
        (("held by", holder.name), *_lands(saga, holder)),
        Spot(listed, record.id),
    )


def _books(saga: Saga) -> Iterator[Entry]:
    for book in saga.books:
        holder = _holder(saga, book.owner_kind, book.owner_id)
        entry = _held(saga, book, "Book", holder, BOOKS)
        if entry is not None:
            yield entry


def _devices(saga: Saga) -> Iterator[Entry]:
    for device in saga.enchanted_devices:
        holder = _holder(saga, device.holder_kind, device.holder_id)
        entry = _held(saga, device, "Enchanted device", holder, DEVICES)
        if entry is not None:
            yield entry


def _spells(saga: Saga) -> Iterator[Entry]:
    """Each spell a character knows or invented, opening their page."""
    for character in saga.characters:
        seen: set[str] = set()
        known = (catalog.find_spell(saga, k.spell_id) for k in character.spells_known)
        for spell in (*known, *character.invented_spells):
            if spell is None or spell.id in seen:
                continue
            seen.add(spell.id)
            found = references.ref(character)
            assert found is not None
            yield Entry(
                found,
                spell.name,
                "Spell",
                f"known by {character.name}",
                (("known by", character.name), *_lands(saga, character)),
                Spot(SPELLS, spell.id),
            )


#: Each kind of record Find lists, in the order a search with no words
#: lists them.
KINDS: dict[str, Callable[[Saga], Iterable[Entry]]] = {
    "characters": _characters,
    "covenants": _covenants,
    "laboratories": _laboratories,
    "familiars": _familiars,
    "tribunals": _tribunals,
    "neighbours": _neighbours,
    "creatures": _creatures,
    "books": _books,
    "spells": _spells,
    "enchanted devices": _devices,
}


def entries(saga: Saga) -> list[Entry]:
    """Every record Find can open, kind by kind."""
    return [entry for list_kind in KINDS.values() for entry in list_kind(saga)]


#: A page's Ref kind as the holder kind its device list is kept by.
_HOLDER_KINDS = {
    "characters": "character",
    "covenants": "covenant",
    "laboratories": "laboratory",
}


def device_row(saga: Saga, kind: str, holder_id: str, device_id: str) -> int | None:
    """The data index of a device's row in its holder's device list
    (enchanted_devices.device_targets: a device, then its effects)."""
    targets = ed.device_targets(saga, kind, holder_id)
    return next(
        (
            n
            for n, (device, effect) in enumerate(targets)
            if effect is None and device.id == device_id
        ),
        None,
    )


def spell_row(character: Character, spell_id: str) -> int | None:
    """The data index of a spell's row in a magus's Known Spells."""
    return next(
        (n for n, k in enumerate(character.spells_known) if k.spell_id == spell_id),
        None,
    )


def spot_row(saga: Saga, opens: Ref, spot: Spot) -> int | None:
    """The data index of `spot`'s row in the list both front-ends keep
    in the same order, a holder's devices and a magus's Known Spells;
    None for one not in it, and for books, whose order each page sets."""
    if spot.list == DEVICES and opens.kind in _HOLDER_KINDS:
        return device_row(saga, _HOLDER_KINDS[opens.kind], opens.id, spot.record_id)
    character = saga.character(opens.id) if opens.kind == "characters" else None
    if spot.list == SPELLS and character is not None:
        return spell_row(character, spot.record_id)
    return None


# -- searching --

#: How a match ranks: its name starting with the words, a word of its name
#: starting with them, its name holding them anywhere; then a faction's
#: member, where a record is (or who holds it), and the Tribunal's lands.
_NAME_START, _NAME_WORD, _NAME_ANY = 0, 1, 2
_ALSO_RANKS: dict[str, int] = {
    "member": 3,
    "at": 4,
    "held by": 4,
    "known by": 4,
    "familiar of": 4,
    "in the lands of": 5,
}


#: Words a name may open with that a search passes over: "drach" finds
#: The Drachenfels.
_ARTICLES = ("the ", "a ", "an ")


@cache
def fold(words: str) -> str:
    """`words` as a search compares them: any case, accents dropped
    (Dammerstein finds Dammërstein), spaces run together."""
    plain = unicodedata.normalize("NFKD", words.casefold())
    return " ".join("".join(c for c in plain if not unicodedata.combining(c)).split())


def _bare(name: str) -> str:
    """A folded name without the article it opens with."""
    for article in _ARTICLES:
        if name.startswith(article):
            return name[len(article) :]
    return name


def _name_rank(name: str, needle: str) -> int | None:
    if name.startswith(needle) or _bare(name).startswith(_bare(needle)):
        return _NAME_START
    if any(word.startswith(needle) for word in name.split()):
        return _NAME_WORD
    return _NAME_ANY if needle in name else None


def _exact(entry: Entry, needle: str) -> bool:
    """Whether `needle` is the entry's whole name, its article aside, or
    its name without the kind it ends with ("rhine" is The Rhine
    Tribunal)."""
    name, bare_needle = _bare(fold(entry.name)), _bare(needle)
    return bare_needle in (name, name.removesuffix(" " + fold(entry.kind)))


def _match(entry: Entry, needle: str) -> Match | None:
    rank = _name_rank(fold(entry.name), needle)
    if rank is not None:
        return Match(entry, rank)
    found = [
        Match(entry, _ALSO_RANKS[how], f"{how} {words}", words)
        for how, words in entry.also
        if needle in fold(words)
    ]
    return min(found, key=lambda m: m.rank, default=None)


def search(found: list[Entry], query: str) -> list[Match]:
    """The entries `query` finds (any case, any accents), best first: by
    name, then by member, place and Tribunal; within a rank a name that
    is the words exactly first (The Rhine Tribunal before The Rhine Gorge),
    then alphabetical, a leading "The" passed over. No words: every entry,
    in the index's order."""
    needle = fold(query)
    if not needle:
        return [Match(entry, 0) for entry in found]
    matches = [m for m in (_match(entry, needle) for entry in found) if m is not None]
    return sorted(
        matches,
        key=lambda m: (
            m.rank,
            not _exact(m.entry, needle),
            _bare(fold(m.entry.name)),
        ),
    )
