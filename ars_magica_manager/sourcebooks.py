"""The Ars Magica sourcebooks the catalogs cite, and which ones a saga has in
play.

Every catalog entry names its book(s) in `source` ("DE", "RoP:F; TC&TC").
A saga keeps the supplements in play in `Saga.books_in_play` -- None means
every book, the default, so existing sagas don't change. The core book is
always in play. Pickers hide an entry whose books are all out of play (with
a toggle to show them); an entry already attached to a record stays shown.
An entry with no book (a user-made one) is always in play."""

from __future__ import annotations

from collections.abc import Collection, Iterable

from .models import Saga

#: The core book: always in play.
CORE = "DE"

#: Abbreviation -> title, the core book first. The abbreviations are the
#: ones the reference docs use.
SOURCEBOOKS: dict[str, str] = {
    CORE: "Ars Magica Definitive Edition",
    "A&A": "Art & Academe",
    "AM": "Ancient Magic",
    "App": "Apprentices",
    "AtD": "Against the Dark: The Transylvanian Tribunal",
    "C&G": "City & Guild",
    "Cal": "Calebais: The Broken Covenant",
    "Covenants": "Covenants",
    "DI": "Dies Irae",
    "F&F": "Faith & Flame: The Provençal Tribunal",
    "GGHS": "The Grand Grimoire of Hermetic Spells",
    "GotF": "Guardians of the Forests: The Rhine Tribunal",
    "Grogs": "Grogs",
    "HMRE": "Hedge Magic, Revised Edition",
    "HoH:MC": "Houses of Hermes: Mystery Cults",
    "HoH:S": "Houses of Hermes: Societates",
    "HoH:TL": "Houses of Hermes: True Lineages",
    "Hooks": "Hooks",
    "HP": "Hermetic Projects",
    "L&L": "The Lion and the Lily: The Normandy Tribunal",
    "LoH": "Legends of Hermes",
    "LoM": "Lords of Men",
    "ML": "Mythic Locations",
    "MoH": "Magi of Hermes",
    "RM": "Rival Magic",
    "RoP:D": "Realms of Power: The Divine",
    "RoP:F": "Realms of Power: Faerie",
    "RoP:I": "Realms of Power: The Infernal",
    "RoP:M": "Realms of Power: Magic",
    "TC": "The Church",
    "TC&TC": "The Cradle and the Crescent",
    "TCI": "The Contested Isle: The Hibernian Tribunal",
    "TME": "Transforming Mythic Europe",
    "TMRE": "The Mysteries, Revised Edition",
    "ToME": "Tales of Mythic Europe",
    "ToP": "Tales of Power",
    "TSE": "The Sundered Eagle: The Theban Tribunal",
    "TtA": "Through the Aegis",
}

#: Other spellings the catalogs use for the same books (the spell catalog and
#: Boons & Hooks cite the core book as "ArM5").
_ALIASES: dict[str, str] = {
    "ArM5": CORE,
    "HoHTL": "HoH:TL",
    "HoHMC": "HoH:MC",
    "HoHS": "HoH:S",
}

#: The books a saga can take out of play: every one but the core book.
SUPPLEMENTS: tuple[str, ...] = tuple(b for b in SOURCEBOOKS if b != CORE)


def books_of(source: str) -> set[str]:
    """The books a `source` cites, as SOURCEBOOKS abbreviations
    ("ArM5; Covenants" -> {"DE", "Covenants"})."""
    return {
        _ALIASES.get(book.strip(), book.strip())
        for book in source.split(";")
        if book.strip()
    }


def in_play(source: str, books: Collection[str] | None) -> bool:
    """Whether an entry citing `source` is in play with `books` (None: every
    book). In play if it cites no book, or any book in play."""
    if books is None:
        return True
    cited = books_of(source)
    return not cited or bool(cited & {CORE, *books})


def saga_books(saga: Saga | None) -> frozenset[str] | None:
    """The books `saga` has in play, core book included; None for every
    book (no saga, or a saga that hasn't narrowed them)."""
    if saga is None or saga.books_in_play is None:
        return None
    return frozenset({CORE, *saga.books_in_play})


def normalized(books_in_play: Iterable[str] | None) -> list[str] | None:
    """What to store as `Saga.books_in_play`: the chosen supplements in
    SUPPLEMENTS order, or None when every one is chosen (so a book added to
    the list later is in play too)."""
    if books_in_play is None:
        return None
    chosen = set(books_in_play)
    if chosen >= set(SUPPLEMENTS):
        return None
    return [book for book in SUPPLEMENTS if book in chosen]


def summary(books_in_play: Iterable[str] | None) -> str:
    """A short description of a saga's books, for its Edit form and detail
    ("All books", "Core book only", "Core book + 3 supplements")."""
    if books_in_play is None:
        return "All books"
    count = len(set(books_in_play) & set(SUPPLEMENTS))
    if count == len(SUPPLEMENTS):
        return "All books"
    if count == 0:
        return "Core book only"
    return f"Core book + {count} supplement{'s' if count != 1 else ''}"
