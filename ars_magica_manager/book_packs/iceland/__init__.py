"""Land of Fire & Ice, with The Icelandic Wars: Mythic Iceland as of 1220.
A Fourth Edition region book, converted by book_packs.fourth, as Blood
and Sand is. The pack holds no Tribunal: the island lies outside every
Tribunal, and Vindolanda is a covenant with none. Built in parts: land,
people, law_church, magic, saga, vindolanda, adventures, characters, wars.
A summary of the books, not their words.

The Definitive Edition's appendix (DE pp. 537-538) has steps for
Characteristics, Virtues and Flaws, Abilities, Arts, spells and Twilight,
and says combat was rewritten, but gives no step for combat totals, Might
or creature powers. So every part reads a printed creature one way:

- Combat: the block's printed totals and Soak stay, with its old Fatigue
  column left out or in the notes. No Ability or weapon is worked back
  from them. A kind the book raises from another (Kollbjorn, Drit) starts
  from these same totals.
- Powers: the printed Might cost stays. A creature power has no level and
  its cost is not set by its strength, only its Penetration and how often
  it can be used (DE pp. 426, 428). A printed level stays for reference. A
  cost printed as "varies", or not at all, is entered as 0 with the sum in
  its words. No Init is printed, so Init is Quickness less the cost.
- Might Form: none is printed. One is set only where the block's vis or
  its nature supports it, and the record says it is this pack's reading.
  Otherwise there is none.
- Confidence: a creature with a name has the Definitive Edition's baseline
  (DE p. 426); a printed score is not carried over."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder

NAME = "Land of Fire and Ice"
SOURCE_BOOK = "LFI"
SOURCE = (
    "Land of Fire & Ice and The Icelandic Wars, by Atlas Games; converted to "
    "the Definitive Edition and summarised, not quoted."
)
#: The parts, in the order they are built.
PARTS = (
    "land",
    "people",
    "law_church",
    "magic",
    "saga",
    "vindolanda",
    "adventures",
    "characters",
    "wars",
)


def assemble(supplements: tuple[str, ...] = ()) -> Builder:
    import importlib

    b = Builder(NAME, source=SOURCE_BOOK, known="In the region")
    for name in PARTS:
        importlib.import_module(f"{__name__}.{name}").build(b)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("iceland", SOURCE_BOOK, NAME, assemble, SOURCE))
