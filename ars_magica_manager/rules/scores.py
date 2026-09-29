"""Effective Art and Ability scores: the score the xp buys (rules.xp) plus
flat bonuses from Virtues such as Puissant, which add to the score whenever
it is used but are not part of the xp (the sheet's X+Y notation)."""

from __future__ import annotations

from collections.abc import Sequence

from .. import catalog
from ..models import VirtueFlawInstance
from . import effects

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Three: Characters, Advancement Table "
    "(X+Y(Z): Y is a fixed bonus, usually Puissant, not part of the xp score) "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter_Three:"
    "_Characters#Advancement_Table)"
)


def character_source(
    virtues_flaws: Sequence[VirtueFlawInstance],
) -> effects.EffectSource:
    """A character's (or familiar's) Virtues and Flaws as a source for the
    shared effect lookup."""
    return effects.EffectSource(
        "character", virtues_flaws, catalog.load_virtue_flaw_catalog_by_id()
    )


def _bonus(
    virtues_flaws: Sequence[VirtueFlawInstance], applies_to: str, target: str
) -> tuple[int, list[str]]:
    found = effects.collect(
        [character_source(virtues_flaws)], applies_to, target=target
    )
    # Only targeted bonuses: an untargeted one would raise every score.
    found = [e for e in found if e.target is not None]
    names = [
        catalog.describe_virtue_flaw(
            e.instance, catalog.load_virtue_flaw_catalog_by_id()
        )
        for e in found
    ]
    return int(effects.amount_total(found)), names


def art_bonus(
    virtues_flaws: Sequence[VirtueFlawInstance], art: str
) -> tuple[int, list[str]]:
    """The flat bonus to one Art's score whenever it is used, and the
    Virtues it comes from."""
    return _bonus(virtues_flaws, "art_score_effective", art)


def ability_bonus(
    virtues_flaws: Sequence[VirtueFlawInstance], ability: str
) -> tuple[int, list[str]]:
    """The flat bonus to one Ability's score whenever it is used, and the
    Virtues it comes from."""
    return _bonus(virtues_flaws, "ability_score_effective", ability)
