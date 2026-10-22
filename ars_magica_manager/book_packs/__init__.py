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
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .. import DATA_DIR, packs, transfer
from ..models import Saga

if TYPE_CHECKING:
    from .builder import Builder

#: Where the shipped packs live.
PACKS_DIR = DATA_DIR / "packs"


@dataclass(frozen=True)
class BookPack:
    """One sourcebook's pack: its key (the file's stem), the book's
    abbreviation (sourcebooks.SOURCEBOOKS), the pack's name as the user
    sees it, the function that assembles its saga with a Builder, and the
    credit line."""

    key: str
    book: str
    name: str
    assemble: Callable[[], Builder]
    source: str

    def build(self) -> Saga:
        return self.assemble().saga


PACKS: dict[str, BookPack] = {}


def register(pack: BookPack) -> None:
    PACKS[pack.key] = pack


def data(pack: BookPack) -> dict[str, Any]:
    """The pack as JSON-ready data: everything its saga holds (its
    wandering magi and its whole bestiary too), with the
    book it comes from, its credit line, and the sketch of each magus
    whose stats were generated (packs.GENERATED), and the help topic
    naming its assumptions (packs.ASSUMPTIONS)."""
    b = pack.assemble()
    saga = b.saga
    found = packs.pack_data(
        saga,
        pack.name,
        saga.tribunals,
        saga.covenants,
        saga.neighbours,
        characters_besides=[c for c in saga.characters if not c.covenant_id],
        creatures_besides=saga.creatures,
    )
    held = {c["id"] for c in found["saga"]["characters"]}
    sketches = {i: asdict(c) for i, c in b.sketches.items() if i in held}
    extra = {packs.GENERATED: sketches} if sketches else {}
    return {
        **found,
        "book": pack.book,
        "source": pack.source,
        packs.ASSUMPTIONS: assumptions_topic(pack),
        **extra,
    }


def assumptions_topic(pack: BookPack) -> str:
    """The help topic listing what the pack inferred from its book or
    chose where the book is silent."""
    return f"pack-assumptions-{pack.key}"


def path_of(pack: BookPack, folder: Path = PACKS_DIR) -> Path:
    return folder / f"{pack.key}{transfer.SUFFIX}"


def write_all(folder: Path = PACKS_DIR) -> list[Path]:
    """Build every registered pack and write it to `folder`."""
    folder.mkdir(parents=True, exist_ok=True)
    return [packs.write(path_of(pack, folder), data(pack)) for pack in PACKS.values()]


from . import (  # noqa: F401
    hibernia,
    levant,
    normandy,
    provence,
    rhine,
    theban,
    transylvania,
)
