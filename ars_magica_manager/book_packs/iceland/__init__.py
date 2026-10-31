"""Land of Fire & Ice, with The Icelandic Wars: Mythic Iceland as of 1220.
A Fourth Edition region book, converted by book_packs.fourth, as Blood
and Sand is. The pack holds no Tribunal: the island lies outside every
Tribunal, and Vindolanda is a covenant with none. Built in parts: land,
people, law_church, magic, saga, vindolanda, adventures, characters, wars.
A summary of the books, not their words.

The parts enter a printed creature at the block's totals, with its old
Fatigue column left out or in the notes; `fourth.reconvert` then works
Might, Combat, Soak and powers out again by the pack's rules for creatures
(fourth.py), as the Definitive Edition's appendix (DE pp. 537-538) gives no
step for them. A kind the book raises from another (Kollbjorn, Drit)
starts from these same totals.

- Powers: a cost printed as "varies", or not at all, is entered as 0 with
  the sum in its words. A printed level is kept and priced by the table.
- Might Form: none is printed. One is set only where the block's vis or
  its nature supports it, and the record says it is this pack's reading.
  Otherwise there is none.
- Confidence: a creature with a name has the Definitive Edition's baseline
  (DE p. 426); a printed score is not carried over."""

from __future__ import annotations

from ...models import Saga
from .. import BookPack, register
from ..builder import Builder
from ..fourth import Kin, reconvert

NAME = "Land of Fire and Ice"
SOURCE_BOOK = "LFI"
SOURCE = (
    "Land of Fire & Ice and The Icelandic Wars, by Atlas Games; converted to "
    "the Definitive Edition and summarised, not quoted."
)
#: Might set by the standing rule; a unique being keeps its printed score.
MIGHT = {
    "Troll": 12,
    "Giant": 28,
    "Serpent of Thoth": 30,
    "Walking Corpses": 9,
    "Infernal Rat Swarm": 5,
    "Disease Spirits": 5,
    "The Guardian Host": 10,
}
#: A giant's Sta +20 has no 5e equivalent (RoP:M p. 86).
KIN = {
    "Giant": Kin(3, 9, "the typical giant, RoP:M p. 86"),
    "Thorkel Red-Cloak's Son": Kin(8, None, "the greatest of the 5e giant-kin"),
    "Gull Hellirsson": Kin(8, None, "the greatest of the 5e giant-kin"),
}
#: Norse giants take their clan's element (RoP:M p. 86; clans, LFI pp. 30-31):
#: Hrym's frost is Aquam, Geirrod's fire Ignem, and the giants of the
#: Bergelmir clan, the commonest in the hills, Terram.
FORMS = {
    "Giant": "Terram",
    "Thorkel Red-Cloak's Son": "Aquam",
    "Geirrod": "Ignem",
    "Gudmund of Glasvellir": "Ignem",
}
#: Demons by order and Hierarchy (RoP:I p. 30): a Might past its order's
#: range is the rank's.
ORDERS: dict[str, tuple[str, int | None]] = {
    "Ammon, Master of the Hidden Revels": ("Lord of the Spirits of Deceit", 5),
    "Whisper": ("Deluders", None),
}
PERSONAL = ("Personal", "Sun", "Individual")
#: Powers by the Definitive Edition's guidelines; those not here stand as
#: printed. A power's level only prices it (DE p. 426).
DESIGNS: dict[tuple[str, str], tuple[int, tuple[str, str, str]]] = {
    ("Serpent of Thoth", "Knowledge of the Subterranean"): (
        40,
        ("Personal", "Concentration", "Vision"),
    ),
    ("Whisper", "Swift Flight"): (20, PERSONAL),
    ("Whisper", "Mythic Perception"): (40, ("Personal", "Concentration", "Vision")),
    ("Whisper", "Eye Peck"): (30, ("Touch", "Momentary", "Part")),
    ("Hlokk", "Grant Fertility"): (30, ("Touch", "Moon", "Individual")),
    ("Hlokk", "Hamfaring"): (30, ("Personal", "Concentration", "Individual")),
    ("Disease Spirits", "Slay the Unborn"): (10, ("Touch", "Momentary", "Individual")),
    ("The Golden Sphinxes", "Regeneration"): (
        30,
        ("Personal", "Momentary", "Individual"),
    ),
    ("The Golden Sphinxes", "Sense Intents"): (
        30,
        ("Personal", "Concentration", "Vision"),
    ),
    ("The Golden Sphinxes", "Binding Word"): (30, ("Voice", "Sun", "Group")),
    ("The Golden Sphinxes", "Thoughts Within the Babble"): (
        25,
        ("Personal", "Concentration", "Hearing"),
    ),
    ("Pan Caudarax, Dragon of Hekla", "Fiery Breath"): (
        50,
        ("Voice", "Momentary", "Individual"),
    ),
    ("Vindsvall", "Spiritual Form"): (40, PERSONAL),
    ("The Gray Bull", "Shapeshift"): (40, PERSONAL),
    ("The Gray Bull", "Spiritual Form"): (40, PERSONAL),
    ("The Guardian Host", "Spiritual Form"): (40, PERSONAL),
    ("The Guardian Host", "Shapeshift"): (20, PERSONAL),
}
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
    reconvert(b.saga, MIGHT, kin=KIN, forms=FORMS, orders=ORDERS, designs=DESIGNS)
    return b


def build() -> Saga:
    return assemble().saga


register(BookPack("iceland", SOURCE_BOOK, NAME, assemble, SOURCE))
