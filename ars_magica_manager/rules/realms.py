"""Auras and realm interaction: the modifier an aura gives a
supernatural act, by the realm of the power used and the realm of the aura,
and the extra botch dice for acting in another realm's aura.

| Power used \\ Aura | Magic      | Divine     | Faerie     | Infernal   |
|--------------------|------------|------------|------------|------------|
| Magic              | +aura      | -3 x aura  | +1/2 aura  | -aura      |
| Divine             | no effect  | +aura      | no effect  | no effect  |
| Faerie             | +1/2 aura  | -4 x aura  | +aura      | -2 x aura  |
| Infernal           | -aura      | -5 x aura  | -aura      | +aura      |

Half an aura rounds down (decision 23). Hermetic magic is a Magic power: the
modifier goes on the Casting Score, the Lab Total, and Parma/Form Magic
Resistance.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .. import catalog
from ..models import REALMS, Character, Covenant, CovenantBoonHookDef, Saga
from . import effects
from .breakdown import Breakdown
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Realm Interaction, pp. "
    "410-411"
)
COVENANT_AURA_SOURCE = "Covenants, Chapter Two: Boons & Hooks, Aura, p. 8"

#: Hermetic magic's realm.
HERMETIC = "Magic"

#: The table above: (power realm, aura realm) -> multiple of the aura. A
#: half is 0.5 (rounded down after multiplying); 0 is "no effect".
_MULTIPLE: dict[tuple[str, str], float] = {
    ("Magic", "Magic"): 1,
    ("Magic", "Divine"): -3,
    ("Magic", "Faerie"): 0.5,
    ("Magic", "Infernal"): -1,
    ("Divine", "Magic"): 0,
    ("Divine", "Divine"): 1,
    ("Divine", "Faerie"): 0,
    ("Divine", "Infernal"): 0,
    ("Faerie", "Magic"): 0.5,
    ("Faerie", "Divine"): -4,
    ("Faerie", "Faerie"): 1,
    ("Faerie", "Infernal"): -2,
    ("Infernal", "Magic"): -1,
    ("Infernal", "Divine"): -5,
    ("Infernal", "Faerie"): -1,
    ("Infernal", "Infernal"): 1,
}


def _check(realm: str) -> None:
    if realm not in REALMS:
        raise ValueError(f"Unknown realm {realm!r}; must be one of {REALMS}")


def aura_modifier(power_realm: str, aura_realm: str, aura: int) -> int:
    """What an aura adds to (or takes from) an act of `power_realm`."""
    _check(power_realm)
    _check(aura_realm)
    return round_down(_MULTIPLE[power_realm, aura_realm] * aura)


def extra_botch_dice(
    power_realm: str, aura_realm: str, aura: int, *, in_regio: bool = False
) -> int:
    """Extra botch dice for acting in another realm's aura: one per point of
    aura (twice that in a regio of another realm). Divine powers never take
    them, nor does an act in its own realm's aura."""
    _check(power_realm)
    _check(aura_realm)
    if power_realm == aura_realm or power_realm == "Divine" or aura <= 0:
        return 0
    return aura * (2 if in_regio else 1)


def aura_note(aura_realm: str, aura: int, power_realm: str = HERMETIC) -> str:
    """How an aura touches Hermetic magic, when that isn't simply +aura:
    "Hermetic magic -9, +3 botch dice"; "" in a Magic aura."""
    if aura_realm == power_realm or aura == 0:
        return ""
    parts = [f"Hermetic magic {aura_modifier(power_realm, aura_realm, aura):+d}"]
    botch = extra_botch_dice(power_realm, aura_realm, aura)
    if botch:
        parts.append(f"+{botch} botch {'die' if botch == 1 else 'dice'}")
    return ", ".join(parts)


def covenant_aura(covenant: Covenant, catalog_by_id: Mapping[str, Any]) -> Breakdown:
    """The covenant's aura: its base score plus every `covenant_aura`
    modifier its Boons and Hooks carry (each Aura Boon adds 1). What its
    laboratories inherit."""
    found = effects.collect(
        [effects.EffectSource("covenant", covenant.boons_hooks, catalog_by_id)],
        "covenant_aura",
    )
    return effects.combine(
        covenant.aura,
        found,
        base_label="Base aura",
        base_source=COVENANT_AURA_SOURCE,
        rounding=round_down,
    )


def covenant_effective_aura(
    covenant: Covenant, catalog_by_id: Mapping[str, CovenantBoonHookDef]
) -> int:
    """The covenant's Aura score (covenant_aura): its base `aura` plus
    every `covenant_aura` modifier of its Boons/Hooks. This is what its
    laboratories inherit."""
    return int(covenant_aura(covenant, catalog_by_id).total)


def home_in_regio(saga: Saga, character: Character) -> bool:
    """Whether the character's covenant stands on a regio level above the
    mundane one, where a foreign aura's botch dice double (DE p. 421)."""
    covenant = saga.covenant(character.covenant_id)
    return covenant is not None and bool(covenant.place_id) and covenant.place_level > 0


def home_aura(saga: Saga, character: Character) -> tuple[int, str]:
    """The aura (score, realm) a character lives in: their covenant's
    effective Aura (its Boons and Hooks included); 0 Magic without one. The
    one place this is worked out (casting totals, vis study,
    aging and warping all use it)."""
    covenant = saga.covenant(character.covenant_id)
    if covenant is None:
        return 0, HERMETIC
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_effective_aura(covenant, boons), covenant.aura_realm
