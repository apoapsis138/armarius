"""The Armarium's and the Custodia Mirabilium's Add, Edit and Delete
(stores.py): the book form and the device form every holder's list uses,
an item added here starting with no holder.

Each counts into the rows as the store's list shows them now (filtered),
so a sheet gives these itself, as the Spells list does.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from .. import books as bk
from .. import stores
from ..commands import Confirm, Form, SectionOps
from ..markup import escape
from ..models import Book, EnchantedDevice, Saga
from . import device as device_forms
from . import library as library_forms


def _book_form(saga: Saga, book: Book | None) -> Form:
    """The book form; a new book has no owner."""
    return library_forms.book_form(saga, book, "")


def _device_form(saga: Saga, device: EnchantedDevice | None) -> Form:
    """The device form; a new device has no holder."""
    if device is None:
        return device_forms.device_form(saga, None, saga.enchanted_devices.append)

    def replaced(edited: EnchantedDevice) -> None:
        devices = saga.enchanted_devices
        devices[devices.index(device)] = edited

    return device_forms.device_form(saga, device, replaced)


def delete_question(saga: Saga, store: stores.Store, item: Any) -> str:
    """ "Delete Wand of Flames, held by Leandro?"; no holder named for an
    unassigned item; a device's effects and a codex's other books said."""
    name = escape(store.cells(saga, item)[0])
    holder = store.holder(saga, item)
    held = f", held by {escape(holder.name)}" if holder is not None else ""
    extra = ""
    if isinstance(item, EnchantedDevice) and item.effects:
        count = len(item.effects)
        extra = f" and its {count} effect{'' if count == 1 else 's'}"
    return f"Delete {name}{held}{extra}?"


def _remove(saga: Saga, item: Any) -> None:
    if isinstance(item, Book):
        if item in saga.books:
            saga.books.remove(item)
            bk.prune_codices(saga)
        return
    if item in saga.enchanted_devices:
        device_forms.remove_target(saga, item, None)


def store_ops(
    saga: Saga, store: stores.Store, listed: Callable[[], Sequence[Any]]
) -> SectionOps:
    """Add, Edit and Delete for `store`'s list, by the row's index in
    `listed()` (the items as the list shows them now)."""
    form = _book_form if store.key == stores.ARMARIUM else _device_form

    def remove(index: int) -> Confirm:
        item = listed()[index]
        return Confirm(delete_question(saga, store, item), lambda: _remove(saga, item))

    return SectionOps(
        add=lambda: form(saga, None),
        edit=lambda index: form(saga, listed()[index]),
        remove=remove,
        rows=lambda: [store.cells(saga, item)[0] for item in listed()],
    )
