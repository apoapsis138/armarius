"""A magic spirit or ghost built by the book (Realms of Power: Magic,
Chapter Seven: Magic Spirits, pp. 100-118): what every spirit has, the
common spirit Powers' costs and Initiatives, and the vis and Presence its
Might gives.

- Every spirit has the Magic Spirit Virtue and the Magical Air Flaw
  (p. 100); a Daimon has a Confidence Score of at least 1 (p. 102).
- A ghost (a creature with Magic Spirit whose Order or Virtues say ghost)
  has one of the magical Social Statuses (Magical Champion, Covenfolk,
  Master, Monster or Friend) and should have a Major Personality or Story
  Flaw for its tie to the world (pp. 116-117).
- The common Powers, each with its cost and Initiative by Quickness:
  Control Human 2, Qik; Donning the Corporeal Veil 5, Qik - 3 (Lesser) or
  0, Qik - 1 (Greater); Eidolon 0, Qik; Ghost Touch and Manifestation by
  the points spent (Qik - points); Material Anchor 1 to 4, Qik - 2 x cost;
  Presence 0, constant; Regio 15, Qik - 30; Stasis 10, Qik - 20
  (pp. 101-103). Regio and Stasis spend Might for good, and Regio needs
  Presence.
- A spirit's body holds a pawn of vis a magnitude of Might, none below
  Might 5 (p. 101). Presence makes it present in a Room (Might 5-10), a
  Structure (15-25) or a Boundary (30+), and its domain yields Might / 10
  pawns a year (p. 103).

The Definitive Edition's spirits aren't written this way, so a creature is
checked only when it has the Magic Spirit Virtue; advice, never refusals.

Pattern: the same shape as rules.faerie_build and rules.infernal_build
(one function per realm over the creature, no new class).
"""

from __future__ import annotations

from collections.abc import Callable

from .. import catalog
from ..models import Creature, CreaturePower
from .rounding import round_down, round_up

SOURCE = "Realms of Power: Magic, Chapter Seven: Magic Spirits, pp. 100-118"

MAGIC_SPIRIT = "vf_magic_spirit"
MAGICAL_AIR = "vf_magical_air"
DAIMON = "vf_daimon"
#: A ghost's Social Status: one of these (p. 117).
GHOST_STATUSES = (
    "vf_magical_champion",
    "vf_magical_covenfolk",
    "vf_magical_master",
    "vf_magical_monster",
    "vf_magical_friend",
)

#: Each common spirit Power: (cost, Initiative from Quickness and cost)
#: by its name; None for a cost the spirit chooses (pp. 101-103).
COMMON_POWERS: dict[str, tuple[int | None, Callable[[int, int], int]]] = {
    "Control Human": (2, lambda q, c: q),
    "Eidolon": (0, lambda q, c: q),
    "Ghost Touch": (None, lambda q, c: q - c),
    "Manifestation": (None, lambda q, c: q - c),
    "Material Anchor": (None, lambda q, c: q - 2 * c),
    "Regio": (15, lambda q, c: q - 30),
    "Stasis": (10, lambda q, c: q - 20),
}
#: Donning the Corporeal Veil, by the Quality it is bought with (p. 102).
VEIL = "Donning the Corporeal Veil"
VEIL_FIGURES: dict[str, tuple[int, int]] = {
    "Lesser Power": (5, -3),
    "Greater Power": (0, -1),
}
PRESENCE = "Presence"
#: Powers that spend Might for good, like a Ritual spell (p. 101, 103).
PERMANENT = ("Regio", "Stasis")


def _ids(creature: Creature) -> set[str]:
    return {vf.vf_id for vf in creature.virtues_flaws}


def is_spirit(creature: Creature) -> bool:
    return MAGIC_SPIRIT in _ids(creature)


def is_ghost(creature: Creature) -> bool:
    text = f"{creature.order} {creature.name} {creature.notes}".casefold()
    return is_spirit(creature) and "ghost" in text


def spirit_vis(might: int) -> int:
    """The pawns of vis in a spirit's body: one a magnitude of Might, none
    below 5 (p. 101)."""
    return 0 if might < 5 else round_up(might / 5)


def presence_area(might: int) -> str:
    """Where a spirit with Presence is present, by its Might (p. 103)."""
    if might >= 30:
        return "a Boundary"
    if might >= 15:
        return "a Structure"
    if might >= 5:
        return "a Room"
    return "nowhere yet (Might 5 or more)"


def presence_vis(might: int) -> int:
    """The pawns its domain yields a year, harvested without harm (p. 103)."""
    return round_down(max(0, might) / 10)


def _power(creature: Creature, name: str) -> CreaturePower | None:
    wanted = name.casefold()
    return next((p for p in creature.powers if p.name.casefold() == wanted), None)


def power_figures(creature: Creature, power: CreaturePower) -> tuple[int, int] | None:
    """The cost and Initiative the book gives a common spirit Power (None
    for any other)."""
    qik = creature.characteristics.quickness
    if power.name.casefold() == VEIL.casefold():
        figures = VEIL_FIGURES.get(power.quality)
        return None if figures is None else (figures[0], qik + figures[1])
    for name, (cost, init) in COMMON_POWERS.items():
        if power.name.casefold() == name.casefold():
            spent = power.might_cost if cost is None else cost
            return spent, init(qik, spent)
    return None


def problems(creature: Creature) -> list[str]:
    """What a magic spirit built by Realms of Power: Magic would have that
    this one lacks (advice)."""
    if not is_spirit(creature):
        return []
    ids = _ids(creature)
    found: list[str] = []
    if MAGICAL_AIR not in ids:
        found.append("Every spirit has the Magical Air Flaw (p. 100).")
    if DAIMON in ids and (creature.confidence_score or 0) < 1:
        found.append("A Daimon has a Confidence Score of at least 1 (p. 102).")
    if is_ghost(creature):
        if not ids & set(GHOST_STATUSES):
            found.append(
                "A ghost has a magical Social Status: Magical Champion, "
                "Covenfolk, Master, Monster or Friend (p. 117)."
            )
        by_id = catalog.load_virtue_flaw_catalog_by_id()
        tie = any(
            (e := by_id.get(v)) is not None
            and e.type == "Flaw"
            and (
                e.category == "Story"
                or (e.category == "Personality" and e.tier == "Major")
            )
            for v in ids
        )
        if not tie:
            found.append(
                "Most ghosts have a Major Personality or Story Flaw for their "
                "tie to the world (p. 117)."
            )
    for power in creature.powers:
        figures = power_figures(creature, power)
        if figures is not None and figures != (power.might_cost, power.init):
            found.append(
                f"{power.name}: the book gives cost {figures[0]}, Init "
                f"{figures[1]:+d} (typed {power.might_cost}, {power.init:+d}; "
                "pp. 101-103)."
            )
    if _power(creature, "Regio") is not None and _power(creature, PRESENCE) is None:
        found.append("Only a spirit with Presence can have Regio (p. 103).")
    return found


def notes(creature: Creature) -> list[str]:
    """What its Might gives a spirit: its vis, and its Presence's reach."""
    if not is_spirit(creature):
        return []
    might = max(0, creature.might)
    found = [f"about {spirit_vis(might)} pawn(s) of vis in its body (p. 101)"]
    if _power(creature, PRESENCE) is not None:
        found.append(
            f"present throughout {presence_area(might)}, whose yield is "
            f"{presence_vis(might)} pawn(s) a year; its Might counts double as "
            "a tether (p. 103)"
        )
    if any(_power(creature, name) is not None for name in PERMANENT):
        found.append("Regio and Stasis spend its Might Score for good (p. 103)")
    return found
