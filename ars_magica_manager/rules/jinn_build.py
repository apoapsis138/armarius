"""A jinni built by the book (The Cradle and the Crescent, Chapter Four:
The Jinn, pp. 62-80): what every jinni shares whatever its realm, and what
each realm's jinn add.

- Every jinni has the free Jinni Virtue and a True Name that can be
  learned, even at low Might; speaks Arabic (or has Faerie Speech or Gift
  of Tongues); knows Theology: Islam (jinn); and has some power to stay
  hidden: invisibility, immateriality, an illusory form or an animal shape
  (p. 62). There are no Divine jinn: only angels (p. 62).
- To take a body a Magic jinni needs Donning the Corporeal Veil, an
  Infernal one Coagulation, a Faerie one a power like Loosely Material,
  unless it is one of the lesser jinn locked in a body (the jann, the
  ghul) (p. 63).
- Many have Second Sight, and a Greater Malediction that binds them to a
  bargain until the other side breaks it (p. 63).
- A jinni with a Might Score is summoned, dispelled and controlled with
  Vim, whatever its realm (p. 79).

Advice, never refusals: each jinni is an individual (p. 62).

Pattern: the same shape as rules.faerie_build (one function per realm
over the creature, no new class).
"""

from __future__ import annotations

from ..models import Creature

SOURCE = "The Cradle and the Crescent, Chapter Four: The Jinn, pp. 62-80"

JINNI = "vf_jinni"
#: What lets a jinni speak to anyone.
SPEECH = ("vf_faerie_speech", "vf_gift_of_tongues")
#: Words in a power's or Virtue's name that hide a jinni (p. 62).
HIDING_WORDS = (
    "invisib",
    "immaterial",
    "intangible",
    "eidolon",
    "illusion",
    "shape",
    "skinchanger",
    "change form",
    "loosely material",
)
#: The power each realm's jinni takes a body with (p. 63).
BODY_POWERS: dict[str, tuple[str, ...]] = {
    "Magic": ("donning the corporeal veil",),
    "Infernal": ("coagulation",),
    "Faerie": ("loosely material", "humanoid", "faerie beast", "hybrid form"),
}


def is_jinni(creature: Creature) -> bool:
    return any(vf.vf_id == JINNI for vf in creature.virtues_flaws)


def _has_ability(creature: Creature, start: str) -> bool:
    return any(a.name.casefold().startswith(start) for a in creature.abilities)


def _names(creature: Creature) -> list[str]:
    return [p.name.casefold() for p in creature.powers] + [
        vf.vf_id.casefold() for vf in creature.virtues_flaws
    ]


def problems(creature: Creature) -> list[str]:
    """What a jinni built by The Cradle and the Crescent would have that
    this one lacks (advice)."""
    if not is_jinni(creature):
        return []
    found: list[str] = []
    if creature.realm == "Divine":
        found.append("There are no Divine jinn, only angels (p. 62).")
    ids = {vf.vf_id for vf in creature.virtues_flaws}
    if not (_has_ability(creature, "arabic") or ids & set(SPEECH)):
        found.append("A jinni speaks Arabic, or has Faerie Speech (pp. 62-63).")
    if not _has_ability(creature, "theology: islam"):
        found.append("A jinni knows Theology: Islam (jinn) (p. 62).")
    names = _names(creature)
    if not any(word in name for name in names for word in HIDING_WORDS):
        found.append(
            "A jinni has some power to stay hidden: invisibility, "
            "immateriality, an illusion or an animal shape (p. 62)."
        )
    body = BODY_POWERS.get(creature.realm, ())
    if body and not any(word in name for name in names for word in body):
        found.append(
            f"A {creature.realm} jinni takes a body with "
            f"{BODY_POWERS[creature.realm][0].title()} or the like, unless locked "
            "in one (p. 63)."
        )
    return found


def notes(creature: Creature) -> list[str]:
    if not is_jinni(creature):
        return []
    found = ["its True Name can be learned, whatever its Might (p. 62)"]
    if creature.might:
        found.append("Vim magic summons, dispels and controls it (p. 79)")
    return found
