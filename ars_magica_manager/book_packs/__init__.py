"""Book packs: the content packs built from the Tribunal sourcebooks and
shipped with the app (data/packs/*.amm.json), one module per book.

A book's module assembles a Saga in code with a `Builder` (builder.py),
one record at a time -- the Tribunal with its package's customs filled
in, its covenants and their magi, the places, towns and neighbours of
the region, its Peripheral Code, its open cases and its history -- and
registers a `BookPack` here naming the book it comes from. The pack
writer (packs.py) then turns that saga into a pack file, so the shipped
file can be rebuilt after a format change (tools/build_packs.py) and a
test can check it still imports clean.

Importing a book pack puts its book in play for the saga (the Tribunal
record carries its package already), so the book's neighbour kinds and
catalog entries show.

The text in a book's module is a paraphrase of the book, never its
words; the pack carries a `source` line crediting the book and its
licence, and NOTICE.md the credit."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import DATA_DIR, packs, transfer
from ..models import Saga

#: Where the shipped packs live.
PACKS_DIR = DATA_DIR / "packs"


@dataclass(frozen=True)
class BookPack:
    """One sourcebook's pack: its key (the file's stem), the book's
    abbreviation (sourcebooks.SOURCEBOOKS), the pack's name as the user
    sees it, the function that builds its saga, and the credit line."""

    key: str
    book: str
    name: str
    build: Callable[[], Saga]
    source: str


PACKS: dict[str, BookPack] = {}


def register(pack: BookPack) -> None:
    PACKS[pack.key] = pack


def data(pack: BookPack) -> dict[str, Any]:
    """The pack as JSON-ready data: everything its saga holds, with the
    book it comes from and its credit line."""
    saga = pack.build()
    found = packs.pack_data(
        saga, pack.name, saga.tribunals, saga.covenants, saga.neighbours
    )
    return {**found, "book": pack.book, "source": pack.source}


def path_of(pack: BookPack, folder: Path = PACKS_DIR) -> Path:
    return folder / f"{pack.key}{transfer.SUFFIX}"


def write_all(folder: Path = PACKS_DIR) -> list[Path]:
    """Build every registered pack and write it to `folder`."""
    folder.mkdir(parents=True, exist_ok=True)
    return [packs.write(path_of(pack, folder), data(pack)) for pack in PACKS.values()]


from . import rhine  # noqa: F401
