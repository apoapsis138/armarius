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


def botch_dice_change(
    virtues_flaws: Sequence[VirtueFlawInstance], activities: Sequence[str]
) -> tuple[int, list[str]]:
    """The botch dice Virtues and Flaws add or take away for a roll that is
    any of `activities`, and the Virtues and Flaws they come
    from."""
    found = [
        e
        for e in effects.collect([character_source(virtues_flaws)], "botch_dice")
        if e.modifier.activity in (None, *activities)
    ]
    names = [
        catalog.describe_virtue_flaw(
            e.instance, catalog.load_virtue_flaw_catalog_by_id()
        )
        for e in found
    ]
    return int(effects.amount_total(found)), names


def with_botch_change(count: int, change: int) -> int:
    """`count` botch dice with a Virtue or Flaw's `change`: never below one
    by itself (Cautious Sorcerer), and none stay none (Careless Sorcerer)."""
    if count <= 0 or not change:
        return count
    return max(1, count + change)


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
    bonus, names = _bonus(virtues_flaws, "ability_score_effective", ability)
    extra = _legacy_bonus(virtues_flaws, ability)
    return bonus + extra, names + ["Faerie Legacy"] * bool(extra)


#: A Faerie Blood's Ability benefit Faerie Legacy makes stronger: the
#: kind of blood -> (the Ability, how much more).
LEGACY_ABILITIES: dict[str, tuple[str, int]] = {"goblin": ("Stealth", 1)}
#: The kinds of blood whose Legacy adds 1 more to one favoured Ability of
#: the kind they already raise.
LEGACY_FAVORED: dict[str, str] = {"dwarf": "Craft: ", "brownie": "Profession: "}


def _legacy_bonus(virtues_flaws: Sequence[VirtueFlawInstance], ability: str) -> int:
    legacy = next((vf for vf in virtues_flaws if vf.vf_id == "vf_faerie_legacy"), None)
    if legacy is None:
        return 0
    wanted = ability.casefold()
    favored = legacy.params.get("favored", "").casefold()
    for vf in virtues_flaws:
        if vf.vf_id in ("vf_faerie_blood", "vf_strong_faerie_blood"):
            blood = vf.params.get("blood", "").casefold()
            name, more = LEGACY_ABILITIES.get(blood, ("", 0))
            if name.casefold() == wanted:
                return more
            prefix = LEGACY_FAVORED.get(blood, "").casefold()
            if prefix and wanted.startswith(prefix) and favored == wanted:
                return 1
    return 0
