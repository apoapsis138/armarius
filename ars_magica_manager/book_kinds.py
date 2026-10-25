"""The kinds of books beyond summa and tractatus, and what each does -- no UI
in here (Covenants, Chapter Seven: Library, "Secondary Functions" and
"Opus Types"; Houses of Hermes: True Lineages, "Folios").

A registry, one entry per kind, in the style of the activity registry: an
entry carries its Quality modifier and whether that counts toward the
book's Build Point cost, so a new kind is one entry, not another branch in
the study or cost code. Three registries, by what they describe:

- OPUS_TYPES: what kind of work a book is (a Commentary).
- PHYSICAL_FORMS: how the copy is made (an Exemplar, a Flap-bound book...).
- COLLECTIONS: what a codex binding several books is (a Florilegium, a
  Folio).

Each kind names the book it comes from, and a form offers only the kinds
whose book the saga has in play (a book already of that kind keeps it).
"""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass

from . import sourcebooks

SOURCE = "Covenants, Chapter Seven: Library, pp. 84-102"


@dataclass(frozen=True)
class Kind:
    """One kind of book, opus or collection."""

    name: str
    #: What it does to the Quality a reader studies at.
    quality: int = 0
    #: Whether that change counts toward its Build Point cost (a
    #: commentary's +1 doesn't; an exemplar's -3 does).
    priced: bool = True
    #: One line for the form and the details panel.
    summary: str = ""
    #: Several readers can study it in the same season (a congregational
    #: book), an exception to one reader a season.
    many_readers: bool = False
    #: It raises its library's research value on its subject one level (a
    #: long correspondence between experts).
    research_level: int = 0
    #: The sourcebook it comes from.
    book: str = "Covenants"


COMMENTARY = "Commentary"
CORRESPONDENCE = "Correspondence"
EXPERT_CORRESPONDENCE = "Expert correspondence"
LECTURE_COMMENTARY = "Lecture commentary"
REALIA = "Realia"

#: What kind of work the book is, beyond summa and tractatus.
OPUS_TYPES: dict[str, Kind] = {
    COMMENTARY: Kind(
        COMMENTARY,
        quality=1,
        priced=False,
        summary="Read like a tractatus, only after a season studying its summa; "
        "+1 Quality, which its Build Point cost ignores.",
    ),
    CORRESPONDENCE: Kind(
        CORRESPONDENCE,
        summary="Letters bound in order, at least 24 from each writer: read "
        "as a tractatus of Quality = the two writers' Communication added.",
    ),
    EXPERT_CORRESPONDENCE: Kind(
        EXPERT_CORRESPONDENCE,
        research_level=1,
        summary="A correspondence of 120 or more letters from each of two "
        "experts: read like one, and it raises its library's research on "
        "the subject one level.",
    ),
    LECTURE_COMMENTARY: Kind(
        LECTURE_COMMENTARY,
        summary="A teacher's lectures recorded by a scribe (Art & Academe): "
        "Quality = the teacher's Communication + Scribe / 2; not counted "
        "against the tractatus the teacher may write.",
        book="A&A",
    ),
    REALIA: Kind(
        REALIA,
        research_level=1,
        many_readers=True,
        summary="A collection of objects studied as a tractatus: Quality 1 "
        "for one quintessential piece, 1 more each time the pieces double "
        "(6 for 32); each reader studies it as many times as its Quality; "
        "readers sharing it in a season split it (-1 Quality for two, -2 up "
        "to four, -3 up to eight); +1 to its library's research on the "
        "subject.",
    ),
}

#: Realia (Covenants p. 102; Against the Dark p. 59): Quality from its
#: pieces, studied up to Quality times by each reader, split among readers
#: sharing it in one season. Bought at covenant creation at the Art
#: column's cost for its Quality (1, 3, 6, 10, 15, 21). A realia on an Art
#: is the Art's presence for Study Requirement and Study Bonus while the
#: reader's score is under REALIA_PRESENCE_ART (Against the Dark p. 61).
REALIA_SOURCE = "Covenants, Chapter Seven: Library, Realia, p. 102"
SHARED_REALIA_SOURCE = "Against the Dark, Tablinum, Studying from Exhibits, p. 59"
REALIA_PRESENCE_SOURCE = "Against the Dark, Tablinum, The Art Exhibits, p. 61"
REALIA_PRESENCE_ART = 15


def realia_quality(pieces: int) -> int:
    """A realia collection's Quality from its unique, highly informative
    pieces: 1 for one, 2 for two, 3 for four... (0 for none)."""
    return max(0, pieces).bit_length()


def realia_sharing_penalty(readers: int) -> int:
    """What sharing a realia in one season takes from its Quality: 1 for two
    readers, 2 for up to four, 3 for up to eight..."""
    return max(0, readers - 1).bit_length()


def realia_cost(quality: int) -> int:
    """Build Points for a realia of `quality`: the Art column of the
    Advancement Table (1, 3, 6, 10, 15, 21)."""
    return max(0, quality) * (max(0, quality) + 1) // 2


#: Experience a season of useful correspondence adds (one correspondence's
#: a season, on a theme of the magus's research or reading, with at least
#: one letter received).
CORRESPONDENCE_XP = 1
CORRESPONDENCE_SOURCE = "Covenants, Chapter Seven: Library, Other Opus Types, p. 90"

#: How the copy is made. Those that change Quality by a set amount do so
#: here; for the others (a damaged book, an edition de luxe) enter the
#: Quality the copy has.
PHYSICAL_FORMS: dict[str, Kind] = {
    k.name: k
    for k in (
        Kind(
            "Exemplar",
            quality=-3,
            summary="A miniature template for distant scribes: cheap to make "
            "and carry; -3 Quality.",
        ),
        Kind(
            "Flap-bound",
            quality=-1,
            summary="Leather flaps for covers; -1 Quality, no resonant "
            "materials on the covers, and it buckles as it ages.",
        ),
        Kind(
            "Juvenilia",
            quality=-3,
            summary="A swift copy by an apprentice, unbound and unilluminated; "
            "-3 Quality.",
        ),
        Kind(
            "Edition de luxe",
            summary="A sumptuous gift copy, heavy to study from: Quality "
            "reduced by up to (Scribe + Binder + Illuminator) / 2 -- enter it "
            "as reduced.",
        ),
        Kind(
            "Treasure-bound",
            summary="An edition de luxe's outside only; the text is ordinary.",
        ),
        Kind(
            "Ex libris",
            summary="A cheap copy for visitors, with no resonant materials; "
            "often damaged -- enter the Quality it has.",
        ),
        Kind(
            "Holographic",
            summary="Written in the author's own hand: an Arcane Connection to "
            "the author for a year, until their opinion changes.",
        ),
        Kind(
            "Huge codex",
            summary="Physically immense, needing magic or assistants to read.",
        ),
        Kind(
            "Congregational",
            many_readers=True,
            summary="A huge codex written to be read by several magi of similar "
            "Intelligence and talent at once: no one-reader limit.",
        ),
        Kind(
            "Unbound",
            summary="Loose sheets not yet bound: no resonances, easily damaged.",
        ),
        Kind(
            "Damaged",
            summary="Worn or broken; enter the Quality it has left.",
        ),
    )
}

FLORILEGIUM, FOLIO = "Florilegium", "Folio"

#: What a codex of several books is.
COLLECTIONS: dict[str, Kind] = {
    FLORILEGIUM: Kind(
        FLORILEGIUM,
        priced=False,
        summary="Tractatus on one topic bound together: each still read on "
        "its own, at +1 Quality (+2 when edited by an authority).",
    ),
    FOLIO: Kind(
        FOLIO,
        summary="A society's best Lab Texts and tractatus: reading one also "
        "teaches Order of Hermes Lore.",
        book="HoH:TL",
    ),
}

#: An epitome, a book enchanted as an item: its material (level 2) and
#: size (x4) on the Material and Size tables, and the shape whose bonuses
#: it has (shape_material_catalog "sm_book"). Only its own resonant
#: materials help its enchantment, unless it is on a mundane subject.
EPITOME_MATERIAL, EPITOME_SIZE, EPITOME_SHAPE = "leather", "large", "Book"

#: The Ability a folio also teaches, and the experience a season of reading
#: one of its books gives in it.
FOLIO_LORE = "Organization Lore: Order of Hermes"
FOLIO_LORE_XP = 1

#: Writing and copying a folio (Houses of Hermes: True Lineages p. 23):
#: what it holds is the sum of its Lab Texts' magnitudes and its tractatus'
#: Qualities, at most the Colentes' combined Magic Theory; a Colens copies
#: 12 magnitudes of Lab Texts into it a season for each point of
#: Profession: Scribe. A scribe copies a whole folio as a summa, carefully at
#: 6 + Scribe points a season or quickly at 18 + 3 x Scribe (its tractatus
#: 1 Quality lower and no Order of Hermes Lore), until the points reach
#: the Colentes' combined Magic Theory.
FOLIO_SOURCE = "Houses of Hermes: True Lineages, Bonisagus, Folios, pp. 22-23"
FOLIO_TEXT_MAGNITUDES = 12


def folio_size(
    text_magnitudes: Collection[int], tractatus_qualities: Collection[int]
) -> int:
    """What a folio holds: its Lab Texts' magnitudes and its tractatus'
    Qualities, summed."""
    return sum(text_magnitudes) + sum(tractatus_qualities)


def folio_capacity(magic_theory_scores: Collection[int]) -> int:
    """The most a folio may hold: its Colentes' Magic Theory, summed."""
    return sum(max(0, s) for s in magic_theory_scores)


def folio_copy_points(scribe: int, *, quick: bool = False) -> int:
    """A season's points copying a folio whole."""
    return 18 + 3 * scribe if quick else 6 + scribe


#: Craftsmanship under Covenants' extended Quality rules (the
#: extended_book_quality rule option): each adds to the Quality, and to the
#: Build Point cost. A professional is skilled with a Profession score of 6.
CRAFT: dict[str, Kind] = {
    "scribe": Kind("Skilled scribe", quality=1),
    "binder": Kind("Skilled binder", quality=1),
    "illuminator": Kind("Skilled illuminator", quality=1),
    "resonance": Kind("Resonant materials (bought)", quality=1),
    "story_resonance": Kind("Resonant materials (from a story)", quality=2),
    "clarified": Kind("Clarified", quality=1),
}

#: A gloss's Quality bonus (once, however often glossed).
GLOSS = Kind("Glossed", quality=1)
#: The books the codex flags and an epitome come from.
PALIMPSEST_BOOK = "Covenants"
ENCYCLOPEDIA_BOOK = "A&A"
EPITOME_BOOK = "Covenants"


def offered(
    kinds: dict[str, Kind], books: Collection[str] | None, keep: str = ""
) -> list[Kind]:
    """The kinds a form offers with `books` in play (sourcebooks.saga_books),
    and `keep`, the kind a book already is, whatever its book."""
    return [
        k
        for k in kinds.values()
        if k.name == keep or sourcebooks.in_play(k.book, books)
    ]


RESONANCE = ("resonance", "story_resonance")
#: The extended rules' author base: Communication + 3 (the core rules' + 6).
EXTENDED_AUTHOR_BASE = 3
#: The effective most an Art summa's Quality reaches (35 - Level) and an Art
#: tractatus's (17) under the extended rules.
ART_SUMMA_CEILING = 35
ART_TRACTATUS_CEILING = 17


def craft_problems(
    book_craft: list[str], form: str, collection: str, glossed: bool = False
) -> list[str]:
    """What the extended rules say can't go together in a book's
    craftsmanship (warnings, not refusals)."""
    found: list[str] = []
    resonant = any(key in book_craft for key in RESONANCE)
    if "resonance" in book_craft and "story_resonance" in book_craft:
        found.append("Resonant materials count once: bought (+1) or from a story (+2).")
    if "clarified" in book_craft and not resonant:
        found.append("Clarification works through resonant materials: it needs them.")
    if glossed and (resonant or "clarified" in book_craft):
        found.append(
            "A gloss expresses resonance: it can't be combined with resonant "
            "materials or clarification."
        )
    if collection == FLORILEGIUM and (resonant or "clarified" in book_craft):
        found.append(
            "A florilegium expresses resonance: no resonant materials or clarification."
        )
    if form in ("Juvenilia", "Unbound", "Ex libris") and resonant:
        found.append(f"{form} copies have no resonances.")
    if form in ("Juvenilia", "Unbound") and "binder" in book_craft:
        found.append(f"{form} copies aren't bound: no binder's bonus.")
    return found


@dataclass(frozen=True)
class Adjustment:
    """One change to the Quality a book is studied at."""

    label: str
    amount: int
    #: Counts toward the Build Point cost.
    priced: bool = True


#: A book on a spell's Mastery Ability names it "Mastery: <spell>" and links
#: the spell by its id (DE pp. 378-379: books may be written on any Ability,
#: a spell's Mastery included).
MASTERY_PREFIX = "Mastery: "


def mastery_subject(ability: str, spell_id: str | None) -> str | None:
    """The "mastery:<spell id>" a book on a spell's Mastery teaches, or None
    for any other book."""
    if ability.startswith(MASTERY_PREFIX) and spell_id:
        return f"mastery:{spell_id}"
    return None
