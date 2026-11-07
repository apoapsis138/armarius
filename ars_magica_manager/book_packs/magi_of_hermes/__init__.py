"""Magi of Hermes: fifteen magi written to drop into any saga, each printed
at Gauntlet and every fifteen years after. A pack of its own with no
Tribunal: the importer chooses who comes, and at which age.

A magus the book ties to a covenant joins it if the saga has it, and one
a Tribunal pack holds as a sketch replaces that sketch (packs.HOMES,
packs.REPLACES). Stat blocks are the book's; the rest is a summary, not
its words."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder, Secrets, StatBlock

NAME = "Magi of Hermes"
SOURCE_BOOK = "MoH"
SOURCE = (
    "Magi of Hermes, by Atlas Games; statistics as printed, the rest "
    "summarised, not quoted."
)
#: The age a magus starts on in the import form: the book gives no dates,
#: and +30 is a settled mid-career magus.
DEFAULT_LABEL = "+30"
PARTS = ("first", "second", "third")


@dataclass(frozen=True)
class Printing:
    """One of a magus's printed blocks: its heading ("Gauntlet", "+15"),
    the age it gives, and the block."""

    label: str
    age: int
    block: StatBlock


@dataclass(frozen=True)
class Magus:
    """One magus of the book: `home` is the covenant the book ties them to,
    `sketch` the name a Tribunal pack holds them under as a sketch, and
    `printings` every block the book prints, in order."""

    name: str
    house: str
    summary: str
    printings: tuple[Printing, ...]
    secrets: Secrets = ()
    home: str = ""
    sketch: str = ""
    label: str = DEFAULT_LABEL


def _default(magus: Magus) -> Printing:
    return next(
        (p for p in magus.printings if p.label == magus.label),
        magus.printings[-1],
    )


def _add(b: Builder, magus: Magus) -> None:
    """The magus at the starting age, and every printing as a variant the
    import form can swap in."""
    chosen = _default(magus)
    character = b.magus(
        magus.sketch or magus.name,
        covenant=None,
        house=magus.house,
        age=chosen.age,
        summary=magus.summary,
        secrets=magus.secrets,
    )
    blank = deepcopy(character)
    versions: list[dict[str, Any]] = []
    for printing in magus.printings:
        version = b.stats(deepcopy(blank), printing.block, source=SOURCE_BOOK)
        versions.append(
            {
                "label": printing.label,
                "age": printing.age,
                "character": asdict(version),
            }
        )
    b.stats(character, chosen.block, source=SOURCE_BOOK)
    b.variants[character.id] = versions
    if magus.home:
        b.homes[character.id] = magus.home
    if magus.sketch:
        b.replaces[character.id] = magus.sketch


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK)
    for name in PARTS:
        for magus in importlib.import_module(f"{__name__}.{name}").MAGI:
            _add(b, magus)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("magi_of_hermes", SOURCE_BOOK, NAME, assemble, SOURCE))
