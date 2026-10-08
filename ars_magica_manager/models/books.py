"""Books, Lab Texts and the Hermetic range/duration/target tables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..arts import ART_BY_NAME
from .common import known_fields

#: Standard Hermetic Ranges, Durations and Targets (ArM5 Chapter Nine), in the
#: book's order. Supplements add their own (Road, Bargain...), kept as typed.
SPELL_RANGES: tuple[str, ...] = (
    "Personal",
    "Touch",
    "Eye",
    "Voice",
    "Sight",
    "Arcane Connection",
)
SPELL_DURATIONS: tuple[str, ...] = (
    "Momentary",
    "Concentration",
    "Diameter",
    "Sun",
    "Ring",
    "Moon",
    "Year",
)
SPELL_TARGETS: tuple[str, ...] = (
    "Individual",
    "Circle",
    "Part",
    "Group",
    "Room",
    "Structure",
    "Boundary",
    "Taste",
    "Touch",
    "Smell",
    "Hearing",
    "Vision",
)
#: The kinds of book a library holds (reference/Libraries.md).
BOOK_TYPES: tuple[str, ...] = (
    "Art Summa",
    "Ability Summa",
    "Tractatus",
    "Lab Text",
    "Casting Tablet",
    "Other",
)
#: What a Lab Text records (`Book.text_kind`): a spell, an
#: enchanted device's effect, a Longevity Ritual, or anything else (a tamed
#: creature, a Discovery, a familiar's bond power).
TEXT_SPELL = "Spell"
TEXT_ENCHANTMENT = "Enchantment"
TEXT_LONGEVITY = "Longevity Ritual"
TEXT_OTHER = "Other"
LAB_TEXT_KINDS: tuple[str, ...] = (
    TEXT_SPELL,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
)
#: What a Tractatus is written on.
TRACTATUS_SUBJECTS: tuple[str, ...] = ("Art", "Ability")
#: Who can own a book (`Book.owner_kind`). A book with no owner is unassigned
#: and files under the saga.
BOOK_OWNER_KINDS: tuple[str, ...] = ("covenant", "laboratory", "character")


@dataclass
class Book:
    """One book. Fields a type doesn't use stay blank: `art` is for Art Summae
    and Art Tractatus, `ability` for Ability Summae and Ability Tractatus,
    `spell_id`/`spell_name` for Lab Texts and Casting Tablets. The Build Point
    cost is always calculated (books.cost)."""

    id: str
    name: str
    type: str  # one of BOOK_TYPES
    language: str = "Latin"
    author: str = ""
    owner_kind: str | None = None  # one of BOOK_OWNER_KINDS, or None
    owner_id: str | None = None
    year_published: int | None = None
    description: str = ""
    subject_kind: str = ""  # a Tractatus's TRACTATUS_SUBJECTS entry
    art: str = ""
    ability: str = ""
    level: int | None = None
    quality: int | None = None
    spell_name: str = ""
    #: A Lab Text's / Casting Tablet's spell (any spell id; see Spell). Its
    #: Level comes from the spell, unless the spell is General-level, when
    #: `level` is the book's own. `spell_name` stays as typed (imported books
    #: link by it until a spell is chosen).
    spell_id: str | None = None
    #: A Lab Text written raw by its author: only he, and whoever
    #: decoded his texts or learned his abbreviations, can use it until he
    #: rewrites it for general use. `author_id`: the author, when a
    #: character of the saga.
    raw: bool = False
    author_id: str | None = None
    #: A Lab Text's kind (one of LAB_TEXT_KINDS; "" for any other book),
    #: and what it records of an effect with no spell to take it from:
    #: its Technique and Form (a spell's text takes both, and
    #: its level, from the spell), and a snapshot taken when it was written
    #: -- an enchantment's Range / Duration / Target, kind of device and
    #: shape and material, or a Longevity Ritual's subject (not `subject`:
    #: that key marks a pre-Library-tab save, see from_dict).
    text_kind: str = ""
    technique: str = ""
    form: str = ""
    effect_rdt: str = ""
    device_type: str = ""
    shape_material: str = ""
    ritual_subject: str = ""
    #: A Longevity Ritual's extra vis: the pawns beyond age / 5 it was first
    #: made with, which must be spent again each time it is performed.
    ritual_extra_vis: int = 0
    #: The codex the book is bound in with other books (a Codex id); None:
    #: bound on its own.
    codex_id: str | None = None
    #: Its opus type beyond summa and tractatus (book_kinds.OPUS_TYPES:
    #: "Commentary"), or "".
    opus: str = ""
    #: A commentary's summa (a book id), when it is in the saga.
    commentary_on: str | None = None
    #: How the copy is made (book_kinds.PHYSICAL_FORMS: "Exemplar",
    #: "Flap-bound"...), or "" for an ordinary bound book.
    physical_form: str = ""

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], spell_names: dict[str, str] | None = None
    ) -> Book:
        d = dict(data)
        if d.get("type") == "Lab Text" and not d.get("text_kind"):
            # In older saves a Lab Text has no kind.
            d["text_kind"] = (
                TEXT_SPELL if d.get("spell_id") or d.get("spell_name") else TEXT_OTHER
            )
        if "subject" in d:
            # The pre-Library-tab stub: Summa/Tractatus/Lab Text on one `subject`.
            subject = str(d.pop("subject") or "")
            art = ART_BY_NAME.get(subject.lower())
            old_type = d.get("type")
            if old_type == "Summa":
                d["type"] = "Art Summa" if art else "Ability Summa"
            if old_type in ("Summa", "Tractatus"):
                if art:
                    d["art"] = art
                else:
                    d["ability"] = subject
            if old_type == "Tractatus":
                d["subject_kind"] = "Art" if art else "Ability"
            if old_type == "Lab Text":
                d["spell_name"] = (spell_names or {}).get(d.get("spell_id") or "", "")
            d.setdefault("name", d.get("spell_name") or subject)
            if d.get("notes"):
                d.setdefault("description", d["notes"])
        return cls(**known_fields(cls, d))


@dataclass
class Codex:
    """One physical tome binding several books together (Covenants,
    Varieties of Manuscript). Each book in it is still studied on its own,
    but only one reader can use the codex in a season, and its books are
    always kept together: they share one owner. The books point to it by
    `Book.codex_id`; a book with none is a codex of its own.

    A palimpsest is a codex whose first text was scraped away and written
    over: both texts can be read, each at -3 Quality."""

    id: str
    name: str
    palimpsest: bool = False
    #: An encyclopedia: a series of tractatus, each studied on its own, that
    #: also aids research like a library of its own (+1 per tractatus on
    #: the subject; Art & Academe, Encyclopedias).
    encyclopedia: bool = False
    #: A collection (book_kinds.COLLECTIONS): "Florilegium" (tractatus on
    #: one topic, each +florilegium_bonus Quality) or "Folio" (Lab Texts and
    #: tractatus that also teach Order of Hermes Lore); "" for neither.
    collection: str = ""
    #: A florilegium's Quality bonus: +1, or +2 edited by an authority.
    florilegium_bonus: int = 1

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Codex:
        return cls(**known_fields(cls, data))
