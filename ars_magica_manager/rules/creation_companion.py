"""Companion creation checks, registered for their worksheet steps in
rules.creation.

A companion may have The Gift, which is free, and then take Hermetic
Virtues and Flaws; the Definitive Edition says this should be extremely
unusual, mainly for playing through a magus's apprenticeship, and that
without magical training The Gift is almost entirely a Flaw (Chapter
Three, Virtues and Flaws). That is advice, never a must.
"""

from __future__ import annotations

from ..models import Character, Saga
from .creation_base import CHARACTER_CHECKS, Check, Record, check
from .creation_character import DE_CH3, THE_GIFT

SOURCE = DE_CH3


@check("virtues_flaws", CHARACTER_CHECKS)
def gifted_companion_checks(saga: Saga, record: Record) -> list[Check]:
    assert isinstance(record, Character)
    if record.type != "companion" or not any(
        vf.vf_id == THE_GIFT for vf in record.virtues_flaws
    ):
        return []
    return [
        Check(
            "virtues_flaws",
            "A Gifted companion should be extremely unusual",
            "advice",
            "The Gift taken: mainly for playing through a magus's "
            "apprenticeship; without magical training it is almost entirely "
            "a Flaw",
            SOURCE,
        )
    ]
