"""Between Sand and Sea: Mythic Africa from the Atlantic to Siwa, as of 1220. The pack holds no Tribunal: these lands lie outside every
Hermetic Tribunal. Built in parts: the records shared with the other
African pack (book_packs.hunger), then peoples, coasts, desert, realms. A summary of the book,
not its words."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, hunger, register
from ..builder import Builder

NAME = "Between Sand and Sea"
SOURCE_BOOK = "BS&S"
SOURCE = "Between Sand and Sea, by Atlas Games; summarised, not quoted."
#: The parts, in the order they are built.
PARTS = ("peoples", "coasts", "desert", "realms")


#: Places two parts each made: (the one kept, the one merged into it).
SAME_PLACES = (
    ("The Great Desert", "The Great Desert (As-Sahra al-Kubra)"),
    ("Numidia", "Numidia (Al-Maghrib al-Awsat)"),
    ("Cyrenaica", "Cyrenaica and Tripolitania (Al-Maghrib al-Adna)"),
    ("The Rif", "Er Rif"),
    ("The Tell", "The Tell Plateau"),
    ("The Haruj", "Al-Haruj al-Aswad"),
)


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK, known="In the region")
    hunger.build(b)
    for name in PARTS:
        importlib.import_module(f"{__name__}.{name}").build(b)
    for keep, drop in SAME_PLACES:
        b.absorb(keep, drop)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("africa", SOURCE_BOOK, NAME, assemble, SOURCE))
