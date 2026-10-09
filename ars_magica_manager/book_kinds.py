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
"""

from __future__ import annotations

from dataclasses import dataclass

SOURCE = (
    "Covenants, Chapter Seven: Library "
    "(https://www.redcap.org/page/Covenants_Chapter_Seven:_Library)"
)


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


COMMENTARY = "Commentary"
CORRESPONDENCE = "Correspondence"
EXPERT_CORRESPONDENCE = "Expert correspondence"
LECTURE_COMMENTARY = "Lecture commentary"

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
    ),
}

#: Experience a season of useful correspondence adds (one correspondence's
#: a season, on a theme of the magus's research or reading, with at least
#: one letter received).
CORRESPONDENCE_XP = 1

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
