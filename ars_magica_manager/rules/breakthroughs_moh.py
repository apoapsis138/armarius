"""Magi of Hermes' breakthroughs, and the rules that come with them.

- A fertile Longevity Ritual (p. 20): Aurulentus' Minor Breakthrough, a
  Longevity Ritual that leaves its subject fertile. Without it every
  Longevity Ritual leaves its subject permanently sterile (DE p. 261).
  Like any Minor Breakthrough it is usable by any Hermetic magus with a
  Lab Text for an effect using it, or trained by the discoverer (DE
  p. 281): the app can't tell which Longevity Lab Text uses it, so the
  ritual's plan asks.
- Hermetic Metamorphosis (pp. 82-83): Marcus' Major Breakthrough, the
  Minor Hermetic Virtue of grafting organs onto an animal. Its ritual,
  Harmonic Metamorphosis of the Beast, needs a Dexterity + Chirurgy roll
  against 9, +3 for an organ transposed (added rather than swapped) and
  +3 more to give a Virtue rather than an anatomical change: failing, the
  animal soon dies; a botch makes a monster. A donor that loses a Virtue
  gains Enfeebled, and a transposed organ's donor dies.
- Exciting Experimentation (p. 26, Errata p. 12): two dice on every
  experimentation table, rules.experiment's TWO_DICE.

The research itself is the Definitive Edition's (rules.experiment, DE
pp. 277-281), which the book's examples follow (True Lineages pp. 26-30).

Pattern: the breakthroughs are data (rules.integrations' entries); the
rest are plain functions.
"""

from __future__ import annotations

from ..models import Character

SOURCE = (
    "Magi of Hermes, Aurulentus, Longevity Breakthrough (p. 20); Marcus, "
    "Original Research and Hermetic Metamorphosis (pp. 82-84); Conscientia, "
    "Exciting Experimentation (p. 26; Errata p. 12); Ars Magica Definitive "
    "Edition, Longevity Rituals (p. 261), Minor Breakthroughs (p. 281)"
)
MOH = "Magi of Hermes"

FERTILE_LONGEVITY = "Fertile Longevity Ritual"
METAMORPHOSIS = "Hermetic Metamorphosis"
METAMORPHOSIS_VIRTUE = "vf_hermetic_metamorphosis"

SURGERY_EASE = 9
TRANSPOSED = 3
GRANTS_VIRTUE = 3


def reached(character: Character, name: str) -> bool:
    """Whether the magus has reached the breakthrough called `name`."""
    key = name.strip().lower()
    return any(b.reached and b.name.lower() == key for b in character.breakthroughs)


def leaves_fertile(magus: Character, *, from_lab_text: bool = False) -> bool:
    """Whether a Longevity Ritual `magus` makes leaves its subject fertile:
    the magus reached the Minor Breakthrough, or (`from_lab_text`) works
    from a Lab Text for an effect using it or was trained by its
    discoverer, which the app can't tell from the text, so the plan says
    so (DE p. 281; MoH p. 20)."""
    return from_lab_text or reached(magus, FERTILE_LONGEVITY)


def longevity_note(
    magus: Character, subject: Character, *, from_lab_text: bool = False
) -> str:
    """What a Longevity Ritual does to its subject's fertility."""
    if reached(magus, FERTILE_LONGEVITY):
        return (
            f"The ritual leaves {subject.name} fertile ({FERTILE_LONGEVITY}, "
            f"{MOH} p. 20)."
        )
    if from_lab_text:
        return (
            f"The ritual leaves {subject.name} fertile ({FERTILE_LONGEVITY} "
            f"from a Lab Text using it, or taught by its discoverer: {MOH} "
            "p. 20, DE p. 281)."
        )
    return (
        f"The ritual leaves {subject.name} permanently sterile (DE p. 261; "
        f"the {FERTILE_LONGEVITY} breakthrough would not, {MOH} p. 20)."
    )


def surgery_ease(*, transposed: bool = False, grants_virtue: bool = False) -> int:
    """Harmonic Metamorphosis' surgery: 9, +3 for an organ transposed, +3
    for a Virtue given rather than an anatomical change."""
    return (
        SURGERY_EASE
        + (TRANSPOSED if transposed else 0)
        + (GRANTS_VIRTUE if grants_virtue else 0)
    )


def surgery_outcome(roll_total: int, ease: int, *, botched: bool = False) -> str:
    """What the surgery roll (Dexterity + Chirurgy + stress die) did."""
    if botched:
        return "Botch: the spell makes some dreadful monster instead."
    if roll_total >= ease:
        return f"{roll_total} against {ease}: the graft takes."
    return f"{roll_total} against {ease}: the animal dies soon after the casting."


def reminders(magus: Character) -> list[str]:
    """What the magus's breakthrough Virtues add at the moment of casting,
    a sentence each (plain text)."""
    if not any(vf.vf_id == METAMORPHOSIS_VIRTUE for vf in magus.virtues_flaws):
        return []
    return [
        "Hermetic Metamorphosis: Harmonic Metamorphosis of the Beast grafts an "
        "organ onto an animal; its surgery is Dexterity + Chirurgy against "
        f"{surgery_ease()}, +{TRANSPOSED} for an organ added, +{GRANTS_VIRTUE} "
        "to give a Virtue; failing, the animal dies, and a botch makes a "
        f"monster ({MOH} p. 83)."
    ]
