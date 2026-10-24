"""Verditius Magic, the Outer Mystery of House Verditius (DE pp. 240-241):
a Verditius who crafts an item from raw materials in its first season of
enchantment gives it Verditius Runes and a mystical link to his Craft.

- Runes: his Philosophiae added to the item's Shape and Material bonuses
  for enchanting it, by anyone, the total still capped by Magic Theory. A
  later Verditius enchanter with a higher Philosophiae raises it.
- Craft: the maker (no one else) adds his current score in the Craft
  Ability he used to every Lab Total for enchanting the item.
- Opening: the maker opens it for his Craft score fewer pawns of Vim vis
  (his Finesse when he shaped it by magic alone), at least one, and it
  counts as opened in full.

A device records that its maker crafted it this way (`verditius_runes`)
and with which Craft Ability (`verditius_craft`; blank for shaping by
magic). Crafting that takes more than a season lengthens the first
season's work; that is the troupe's to track.
"""

from __future__ import annotations

from ..models import Character, EnchantedDevice, Saga
from . import lab, lab_virtues
from .breakdown import Line

SOURCE = "Ars Magica Definitive Edition, House Verditius, Verditius Magic, pp. 240-241"
VERDITIUS_MAGIC = "vf_verditius_magic"
PHILOSOPHIAE = "Philosophiae"
FINESSE = "Finesse"


def is_verditius(magus: Character | None) -> bool:
    return magus is not None and lab_virtues.has(magus, VERDITIUS_MAGIC)


def _score(magus: Character, ability: str) -> int:
    level, bonus = lab.ability_score(magus, ability)
    return level + bonus


def maker_of(saga: Saga, device: EnchantedDevice) -> Character | None:
    return next((c for c in saga.characters if c.id == device.maker_id), None)


def crafts_it(saga: Saga, magus: Character, device: EnchantedDevice) -> bool:
    """Whether `magus` is the Verditius who crafted `device` (or will, the
    season he first works on it)."""
    return (
        device.verditius_runes
        and is_verditius(magus)
        and device.maker_id in (None, magus.id)
    )


def rune_bonus(saga: Saga, magus: Character, device: EnchantedDevice) -> int:
    """The Verditius Runes' addition to each of the item's Shape and
    Material bonuses: the best Philosophiae of its Verditius maker and of
    `magus`, if he is a Verditius too."""
    if not device.verditius_runes:
        return 0
    makers = [m for m in (maker_of(saga, device), magus) if is_verditius(m)]
    return max((_score(m, PHILOSOPHIAE) for m in makers if m), default=0)


def craft_line(saga: Saga, magus: Character, device: EnchantedDevice) -> Line | None:
    """The maker's Craft score on a Lab Total for enchanting his item."""
    if not device.verditius_craft or not crafts_it(saga, magus, device):
        return None
    score = _score(magus, device.verditius_craft)
    if not score:
        return None
    return Line(
        f"{device.verditius_craft} (Verditius Magic)", amount=score, source=SOURCE
    )


def opening_discount(saga: Saga, magus: Character, device: EnchantedDevice) -> int:
    """The pawns the maker saves opening his item: his Craft score, or his
    Finesse when he shaped it by magic. Only in its first season."""
    if device.pawns_opened or not crafts_it(saga, magus, device):
        return 0
    return _score(magus, device.verditius_craft or FINESSE)
