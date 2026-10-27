"""The Hermetic spell guidelines the supplements add, which the spell design
form offers as a spell's base level (data/spell_guideline_catalog.json).

- Houses of Hermes: Societates, Perception and Deception (pp. 61-70):
  anamorphs, a Muto Imaginem one changing an existing image and a Creo
  Imaginem one standing free (base 1 for one sense, +1 magnitude for each
  further sense; pp. 65-66, and Magi of Hermes p. 93 files its two-sense
  anamorph as MuIm base 2), synaesthesia (MuIm 2, p. 65), emotions aimed
  at someone (CrMe 4), undirected or aimed at a class (CrMe 5, p. 66),
  diminishing one mental capability (PeMe 4, pp. 66-67; pain,
  proprioception and balance count as capabilities, p. 63), other states
  of consciousness (ReMe 4, p. 67), inscribed memories (CrMe 5, p. 69),
  a memory or emotion made solid (MuMe 5, p. 70) and inclinations (ReMe
  5, p. 70). The chapter's transparencies (as the Perdo Imaginem
  guideline they mimic, p. 64), miniatures (one magnitude over the
  Imaginem base, p. 67) and changed or destroyed thoughts (as memories,
  p. 68) have no level of their own, so they aren't listed.
- Societates' Rego craft table (p. 61): an item made from each raw
  material (bone, gemstone, glass, leather, metal, stone, timber, wood,
  wool) at its level, at Personal Range (Errata p. 59 corrects the book's
  Touch).
- Societates' other new guidelines: ice in a natural shape (CrAq 3,
  p. 34), harmful gases (MuAu 4 and 5, p. 36), destroying one aspect of
  dirt (PeTe 5, p. 37), stone projectiles (ReTe 5 / 10 / 15, p. 38),
  improving all wounds (CrCo 25, p. 100) and a General Rego Vim guideline
  sustaining or suppressing another's magic of a type (p. 129, as Errata
  pp. 12 and 60 reword it).
- Magi of Hermes's New Guideline boxes: repairing a crafted item (CrTe
  15, p. 31), inhuman body parts (MuCo 5, Part Target, p. 49), instant
  transport (ReTe 4, p. 92), preserving an Arcane Connection (CrVi 5 /
  10 / 15, p. 113) and restoring a wooden item (CrHe 15, p. 139).

The Errata (pp. 11-12, 58-60) change only the two noted. The Definitive
Edition prints most of these among its own (pp. 320-370; each entry's
de_page), with the same levels, so those are offered whichever books are
in play; the rest only while their book is. A General guideline has no
level of its own: choosing it leaves the base level as typed. The
Definitive Edition's other guidelines aren't catalogued: the base level is
typed for them.
"""

from __future__ import annotations

from typing import Any

from .. import catalog, sourcebooks
from ..arts import ART_ABBREVIATIONS
from ..models import Saga, SpellGuidelineDef

SOURCE = (
    "Houses of Hermes: Societates, pp. 34-38, Perception and Deception "
    "pp. 61-70, pp. 100, 129; Magi of Hermes, pp. 31, 49, 92, 93, 113, 139; "
    "Errata pp. 11-12, 58-60; Ars Magica Definitive Edition, Chapter 9: "
    "Spells, pp. 307, 320-370"
)


def guidelines() -> list[SpellGuidelineDef]:
    """Every guideline of the catalog, in its order."""
    return catalog.load_spell_guideline_catalog()


def find(guideline_id: str | None) -> SpellGuidelineDef | None:
    if not guideline_id:
        return None
    return catalog.load_spell_guideline_catalog_by_id().get(guideline_id)


def in_play(saga: Saga | None, guideline: SpellGuidelineDef) -> bool:
    """Whether the saga offers `guideline`: the Definitive Edition prints
    it too, or its book is in play."""
    return guideline.de_page is not None or sourcebooks.in_play(
        guideline.source, sourcebooks.saga_books(saga)
    )


def offered(
    saga: Saga | None, technique: str = "", form: str = ""
) -> list[SpellGuidelineDef]:
    """The guidelines `saga` offers, only those of `technique` and `form`
    when given."""
    return [
        g
        for g in guidelines()
        if in_play(saga, g)
        and (not technique or g.technique == technique)
        and (not form or g.form == form)
    ]


def not_offered(saga: Saga | None) -> list[SpellGuidelineDef]:
    """The guidelines of books the saga has out of play."""
    return [g for g in guidelines() if not in_play(saga, g)]


def arts(guideline: SpellGuidelineDef) -> str:
    """Its Arts as a spell's shorthand: "CrTe"."""
    return ART_ABBREVIATIONS[guideline.technique] + ART_ABBREVIATIONS[guideline.form]


def cite(guideline: SpellGuidelineDef) -> str:
    """Its book and page, and the Definitive Edition's where it has it:
    "MoH p. 31; DE p. 359"."""
    found = f"{guideline.source} p. {guideline.page}"
    if guideline.de_page is not None:
        found += f"; {sourcebooks.CORE} p. {guideline.de_page}"
    return found


def level_text(guideline: SpellGuidelineDef) -> str:
    """Its level as the books print it: "15", or "Gen" for a General one."""
    return "Gen" if guideline.general else str(guideline.level)


def label(guideline: SpellGuidelineDef) -> str:
    """How a list names it: "CrTe 15 Repair a crafted item"."""
    return f"{arts(guideline)} {level_text(guideline)} {guideline.name}"


def base_effect(guideline: SpellGuidelineDef) -> str:
    """The design's Base effect once it is chosen: its name, Arts, level
    and book."""
    return (
        f"{guideline.name} ({arts(guideline)} {level_text(guideline)}, "
        f"{cite(guideline)})"
    )


def matching(text: str) -> SpellGuidelineDef | None:
    """The guideline a design's Base effect names, as base_effect() wrote
    it (None for one typed by hand)."""
    text = text.strip()
    if not text:
        return None
    return next((g for g in guidelines() if base_effect(g) == text), None)


def design_values(guideline: SpellGuidelineDef) -> dict[str, Any]:
    """What choosing it puts into a spell design: its Arts, its level as
    the base level (not for a General one, whose level is the
    designer's), its name as the Base effect, and the Target it must have
    (Part, for MoH p. 49's body parts)."""
    found: dict[str, Any] = {
        "technique": guideline.technique,
        "form": guideline.form,
        "base_effect": base_effect(guideline),
    }
    if not guideline.general:
        found["base_level"] = guideline.level
    if guideline.target:
        found["target"] = guideline.target
    return found
