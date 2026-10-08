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


COMMENTARY = "Commentary"

#: What kind of work the book is, beyond summa and tractatus.
OPUS_TYPES: dict[str, Kind] = {
    COMMENTARY: Kind(
        COMMENTARY,
        quality=1,
        priced=False,
        summary="Read like a tractatus, only after a season studying its summa; "
        "+1 Quality, which its Build Point cost ignores.",
    ),
}

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
            summary="Physically immense, needing magic or assistants to read; "
            "a congregational one lets several magi study at once.",
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

#: The Ability a folio also teaches, and the experience a season of reading
#: one of its books gives in it.
FOLIO_LORE = "Organization Lore: Order of Hermes"
FOLIO_LORE_XP = 1


@dataclass(frozen=True)
class Adjustment:
    """One change to the Quality a book is studied at."""

    label: str
    amount: int
    #: Counts toward the Build Point cost.
    priced: bool = True
