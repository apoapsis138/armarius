"""The saga's two stores: the Armarium, every book in the saga, and the
Custodia Mirabilium, every enchanted device, each held by a covenant, a
laboratory or a character, or by nobody (Unassigned).

An armarius is a locked book closet (Covenants p. 92): the Armarium is
the saga's, holding every Book record (lab texts, casting tablets and a
codex's volumes, each a row of its own). The Custodia Mirabilium is "the
keeping of wonders".

Each store is a `Store` (Strategy, as a pair of values): what differs
between books and devices is held there, so a front-end draws either
store with one view and never asks which it is. A `Filter` narrows a
store to one holder, or to the Unassigned, and to one type. The
storyguide alone reads either store (viewing.STORYGUIDE_ONLY).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Any

from . import books as bk
from . import enchanted_devices as ed
from . import vis
from .grids import Grid
from .markup import escape
from .models import (
    BOOK_TYPES,
    DEVICE_TYPES,
    Book,
    Character,
    Covenant,
    EnchantedDevice,
    Laboratory,
    Saga,
)
from .references import Fact, ref
from .rules import enchantment, library
from .sections import ARMARIUM_SECTION, CUSTODIA_SECTION

Holder = Character | Laboratory | Covenant

ARMARIUM, CUSTODIA = "armarium", "custodia"

#: The holder filter's value for what nobody holds; "" is every item.
UNASSIGNED = "unassigned"
#: What a row and the filter call an item nobody holds.
UNASSIGNED_WORDS = "Unassigned"


@dataclass(frozen=True)
class Filter:
    """What a store shows: `holder` "" for every item, UNASSIGNED for
    those nobody holds, or one holder ("kind:id"); `kind` "" for any type,
    else one book or device type."""

    holder: str = ""
    kind: str = ""


@dataclass(frozen=True)
class Store:
    """One of the two stores, as both front-ends draw it."""

    key: str
    title: str
    #: The line under its title on its page and card.
    subtitle: str
    #: Its list section's id (sections, help topic, actions).
    section: str
    #: What Give gives from its list (a giving.GIVERS key).
    gives: str
    #: What it holds, one and many: "book", "books".
    noun: str
    nouns: str
    #: Its list's heading: "Books", "Enchanted Devices".
    heading: str
    #: The artwork concept for its card and page.
    icon: str
    #: Every item it holds, in list order.
    items: Callable[[Saga], list[Any]]
    #: The record that holds an item, None for none.
    holder: Callable[[Saga, Any], Holder | None]
    #: An item's type (a book's Type, a device's).
    kind: Callable[[Any], str]
    #: Every type an item can have.
    kinds: tuple[str, ...]
    #: Its list's column titles and an item's cells (plain words).
    columns: tuple[str, ...]
    cells: Callable[[Saga, Any], list[str]]
    #: The details of an item (markup), for its details panel.
    details: Callable[[Saga, Any], str]
    #: How wide each column may be on a padded line (the terminal).
    caps: tuple[int, ...]
    empty: str


# -- what each store holds --


def _book_holder(saga: Saga, book: Book) -> Holder | None:
    return library.owner_record(saga, book)


def _device_holder(saga: Saga, device: EnchantedDevice) -> Holder | None:
    if not device.holder_kind:
        return None
    return vis.find_holder(saga, device.holder_kind, device.holder_id)


def holder_name(holder: Holder | None) -> str:
    """The holder's name, or Unassigned."""
    return holder.name if holder is not None else UNASSIGNED_WORDS


def _book_name(saga: Saga, book: Book) -> str:
    """A book's name, and the codex it is bound in."""
    name = book.name or "(untitled)"
    codex = library.codex_of(saga, book)
    return f"{name} (in {codex.name})" if codex is not None else name


def _book_cells(saga: Saga, book: Book) -> list[str]:
    return [
        _book_name(saga, book),
        book.type,
        library.subject(book, saga) or "-",
        holder_name(_book_holder(saga, book)),
    ]


def effects_text(device: EnchantedDevice) -> str:
    """A device's first effect and how many more: "Pilum of Fire +2 more";
    "-" for none."""
    if not device.effects:
        return "-"
    first = enchantment.effect_name(device.effects[0])
    more = len(device.effects) - 1
    return f"{first} +{more} more" if more else first


def device_type(device: EnchantedDevice) -> str:
    """A device's type as its row shows it (Invested, Lesser, Charged): a
    talisman says so."""
    if enchantment.is_talisman(device):
        return "Talisman"
    return ed.TYPE_WORDS.get(device.type, device.type)


def _device_cells(saga: Saga, device: EnchantedDevice) -> list[str]:
    return [
        device.name or "(unnamed)",
        device_type(device),
        effects_text(device),
        holder_name(_device_holder(saga, device)),
    ]


def _device_details(saga: Saga, device: EnchantedDevice) -> str:
    """The device, then every effect it holds."""
    parts = [ed.device_info_text(saga, device)]
    parts += [ed.effect_info_text(device, effect, saga) for effect in device.effects]
    return "\n\n".join(parts)


def _books(saga: Saga) -> list[Book]:
    return bk.grouped(saga, list(saga.books))


def _devices(saga: Saga) -> list[EnchantedDevice]:
    return list(saga.enchanted_devices)


STORES: dict[str, Store] = {
    ARMARIUM: Store(
        key=ARMARIUM,
        title="The Armarium",
        subtitle="Every book in the saga, held or unassigned",
        section=ARMARIUM_SECTION,
        gives="book",
        noun="book",
        nouns="books",
        heading="Books",
        icon="library",
        items=_books,
        holder=_book_holder,
        kind=lambda book: book.type,
        kinds=BOOK_TYPES,
        columns=("Name", "Type", "Subject", "Holder"),
        cells=_book_cells,
        details=bk.detail_text,
        caps=(30, 14, 18, 0),
        empty="No books yet: Add makes one with no holder.",
    ),
    CUSTODIA: Store(
        key=CUSTODIA,
        title="The Custodia Mirabilium",
        subtitle="The keeping of wonders: every enchanted device, held or unassigned",
        section=CUSTODIA_SECTION,
        gives="device",
        noun="enchanted device",
        nouns="enchanted devices",
        heading="Enchanted Devices",
        icon="enchanted_item",
        items=_devices,
        holder=_device_holder,
        kind=lambda device: device.type,
        kinds=DEVICE_TYPES,
        columns=("Name", "Type", "Effect", "Holder"),
        cells=_device_cells,
        details=_device_details,
        caps=(28, 9, 28, 0),
        empty="No enchanted devices yet: Add makes one with no holder.",
    ),
}

#: Each store by its list section's id.
BY_SECTION: dict[str, Store] = {store.section: store for store in STORES.values()}


# -- holders and the filter --


def holder_value(holder: Holder | None) -> str:
    """A holder as the filter's and the forms' "kind:id" ("" for none)."""
    if holder is None:
        return ""
    return bk.owner_value(vis.kind_of(holder), holder.id)


def holder_label(holder: Holder) -> str:
    """ "Covenant: Fengheld", "Laboratory: Tower", "Leandro (magus)"."""
    if isinstance(holder, Covenant):
        return f"Covenant: {holder.name}"
    if isinstance(holder, Laboratory):
        return f"Laboratory: {holder.name}"
    return f"{holder.name} ({holder.type})"


def holder_choices(saga: Saga, store: Store) -> list[tuple[str, str]]:
    """The holder filter's (label, value): All, Unassigned, then each
    record holding at least one of the store's items, by label."""
    held: dict[str, str] = {}
    for item in store.items(saga):
        holder = store.holder(saga, item)
        if holder is not None:
            held[holder_value(holder)] = holder_label(holder)
    return [
        ("All holders", ""),
        (UNASSIGNED_WORDS, UNASSIGNED),
        *sorted(((label, value) for value, label in held.items()), key=_label_key),
    ]


def _label_key(choice: tuple[str, str]) -> str:
    return choice[0].casefold()


def kind_choices(store: Store) -> list[tuple[str, str]]:
    """The type filter's (label, value): any, then each type."""
    return [("Any type", ""), *((kind, kind) for kind in store.kinds)]


def passes(saga: Saga, store: Store, item: Any, wanted: Filter) -> bool:
    if wanted.kind and store.kind(item) != wanted.kind:
        return False
    if not wanted.holder:
        return True
    holder = store.holder(saga, item)
    if wanted.holder == UNASSIGNED:
        return holder is None
    return holder_value(holder) == wanted.holder


#: Every item, held or not, of any type.
EVERY = Filter()


def shown(saga: Saga, store: Store, wanted: Filter = EVERY) -> list[Any]:
    """The store's items the filter lets through, in list order."""
    return [item for item in store.items(saga) if passes(saga, store, item, wanted)]


def unassigned(saga: Saga, store: Store) -> list[Any]:
    return shown(saga, store, Filter(holder=UNASSIGNED))


# -- what a front-end shows --


def title(saga: Saga, store: Store, listed: Sequence[Any]) -> str:
    """The list's title, counting what it shows: "Books (3 of 12)"."""
    every = len(store.items(saga))
    count = str(every) if len(listed) == every else f"{len(listed)} of {every}"
    return f"{store.heading} ({count})"


def grid(saga: Saga, store: Store, listed: Sequence[Any]) -> Grid:
    """The items `listed` as a list's columns; each row's key is its
    index in `listed`."""
    return Grid(
        list(store.columns),
        [store.cells(saga, item) for item in listed],
        list(range(len(listed))),
        store.empty,
        caps=list(store.caps),
        stretch=0,
    )


def card_facts(saga: Saga, store: Store) -> list[Fact]:
    """A store's card on the saga page: how many it holds, how many of
    them are held and how many are unassigned."""
    every = len(store.items(saga))
    loose = len(unassigned(saga, store))
    return [
        Fact(store.heading, str(every)),
        Fact("Held", str(every - loose)),
        Fact(UNASSIGNED_WORDS, str(loose)),
    ]


def holder_fact(saga: Saga, store: Store, item: Any) -> Fact:
    """Who holds the item, as a fact whose name opens the holder."""
    holder = store.holder(saga, item)
    found = ref(holder) if holder is not None else None
    return Fact(
        "Holder", holder_name(holder), refs=(found,) if found is not None else ()
    )


def details(saga: Saga, store: Store, item: Any | None) -> str:
    """The details panel for `item` (markup); a hint with none chosen."""
    if item is None:
        article = "an" if store.noun[:1] in "aeiou" else "a"
        return f"[$label]Choose {article} {escape(store.noun)} to see its details.[/]"
    return store.details(saga, item)


def subtitle(saga: Saga, store: Store, item: Any) -> str:
    """The inspector's line under the item's name: its type and holder."""
    return f"{store.kind(item)}  ·  {holder_name(store.holder(saga, item))}"
