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

With Dies Irae in play Lunar is a fifth supernatural realm (DI p. 36), and
its New Realm Interaction Table (p. 37) adds a row and a column: a Lunar
aura gives Lunar powers +aura, Magic and Faerie powers -(5 x aura),
Infernal ones -aura and Divine ones nothing; Lunar powers take -aura in
Magic, Faerie and Infernal auras and -(3 x aura) in a Divine one. The
other realms' entries are the core table's. An aura (a place's, a regio
level's, a covenant's) may be Lunar only while the book is in play
(`aura_realms`); records themselves still belong to one of the four realms
(models.REALMS).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .. import catalog, sourcebooks
from ..models import (
    REALMS,
    Character,
    Covenant,
    CovenantBoonHookDef,
    CovenantStop,
    Saga,
)
from . import effects, lunar, sites
from .breakdown import Breakdown
from .rounding import round_down

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Twelve: Realms, Realm Interaction, pp. "
    "410-411"
)
COVENANT_AURA_SOURCE = "Covenants, Chapter Two: Boons & Hooks, Aura, p. 8"

#: Hermetic magic's realm.
HERMETIC = "Magic"
FAERIE = "Faerie"
INFERNAL = "Infernal"
#: Attunes a sahir to Magic and Faerie auras (The Cradle and the Crescent
#: pp. 30-31).
YATU_MAGIC = "vf_yatu_magic"

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
    # Dies Irae's Lunar row and column (p. 37).
    **{
        pair: multiple
        for pair, multiple in lunar.MULTIPLE.items()
        if lunar.LUNAR in pair
    },
}

#: Every realm an aura may have: the four, and Lunar (Dies Irae p. 36).
AURA_REALMS: tuple[str, ...] = (*REALMS, lunar.LUNAR)
LUNAR_SOURCE = "Dies Irae, Magic After the Apocalypse, pp. 36-37"


def _check(realm: str) -> None:
    if realm not in AURA_REALMS:
        raise ValueError(f"Unknown realm {realm!r}; must be one of {AURA_REALMS}")


def aura_realms(saga: Saga | None, current: str = "") -> tuple[str, ...]:
    """The realms an aura may be given in `saga`'s forms: the four, and
    Lunar while Dies Irae is in play (or while `current` is already Lunar,
    so a saved choice stays shown)."""
    if current == lunar.LUNAR or sourcebooks.in_play(
        "DI", sourcebooks.saga_books(saga)
    ):
        return AURA_REALMS
    return REALMS


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
    found = (
        ()
        if not covenant.aura_boons_apply
        else effects.collect(
            [effects.EffectSource("covenant", covenant.boons_hooks, catalog_by_id)],
            "covenant_aura",
        )
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
    if covenant is None:
        return False
    where = sites.covenant_place(saga, covenant)
    return where is not None and where[1] > 0


def home_aura(saga: Saga, character: Character) -> tuple[int, str]:
    """The aura (score, realm) a character lives in: their covenant's
    effective Aura (its Boons and Hooks included); 0 Magic without one. The
    one place this is worked out (casting totals, vis study,
    aging and warping all use it)."""
    ship = sites.ship_aboard(saga, character)
    apart = sites.ship_stop(saga, ship) if ship is not None else None
    if apart is not None:
        return sites.aura_here(saga, *apart)
    return aura_of(saga.covenant(character.covenant_id))


def aura_of(covenant: Covenant | None) -> tuple[int, str]:
    """A covenant's effective Aura (its Boons and Hooks included) and its
    realm; 0 Magic for none."""
    if covenant is None:
        return 0, HERMETIC
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    return covenant_effective_aura(covenant, boons), covenant.aura_realm


def _boon_points(covenant: Covenant) -> int:
    """What its Boons and Hooks add to an aura of its own."""
    boons = catalog.load_covenant_boon_hook_catalog_by_id()
    found = effects.collect(
        [effects.EffectSource("covenant", covenant.boons_hooks, boons)],
        "covenant_aura",
    )
    return int(effects.combine(0, found, rounding=round_down).total)


def _in_force(
    covenant: Covenant, mine: tuple[int, str] | None, theirs: tuple[int, str]
) -> tuple[int, str, bool]:
    """The aura in force, its realm and whether the covenant's Boons act on
    it: `theirs` is the aura around it, and `mine` the aura of a Place
    travelling with it, which takes its Boons and holds sway unless the
    aura around it is stronger (DE p. 410). With no such Place, the Boons
    stay behind."""
    if mine is None:
        return *theirs, False
    boosted = mine[0] + _boon_points(covenant)
    if theirs[0] > boosted:
        return *theirs, False
    return mine[0], mine[1], True


def settled_aura(saga: Saga, covenant: Covenant) -> tuple[int, str, bool]:
    """The aura where `covenant` is now, its realm, and whether its Boons
    and Hooks act on it: at its own Place, or a Place travelling with it.
    Without one of those a covenant on the move has none of their aura:
    an aura needs something to anchor it (Covenants p. 8; The Sundered
    Eagle p. 84)."""
    where = sites.covenant_place(saga, covenant)
    assert where is not None
    found, level = where
    if found.id != covenant.place_id:
        return *sites.aura_here(saga, found, level), False
    around = sites.place(saga, found.place_id)
    if level or around is None or not sites.travels(found):
        return *sites.aura_at(found, level), True
    return _in_force(
        covenant, sites.aura_at(found), sites.aura_at(around, found.place_level)
    )


def aura_at_stop(saga: Saga, covenant: Covenant, stop: CovenantStop) -> tuple[int, str]:
    """A covenant's effective Aura at a stop, past or planned, and its
    realm: what aura_of gives while the stop is in force."""
    found = sites.place(saga, stop.place_id)
    if found is None:
        return 0, ""
    theirs = sites.aura_at(found, stop.level)
    own = sites.place(saga, covenant.place_id)
    if own is None or not sites.travels(own):
        if stop.place_id != covenant.place_id:
            return theirs
        return theirs[0] + _boon_points(covenant), theirs[1]
    mine = sites.aura_at(own, covenant.place_level)
    if covenant.place_level:
        return mine[0] + _boon_points(covenant), mine[1]
    aura, realm, applies = _in_force(covenant, mine, theirs)
    return (aura + _boon_points(covenant) if applies else aura), realm


def host(saga: Saga, character: Character) -> Covenant | None:
    """The covenant the character is staying at as a guest, if any
    (guest_stays.py)."""
    stay = character.stay
    return saga.covenant(stay.host_id) if stay is not None else None


def present_aura(saga: Saga, character: Character) -> tuple[int, str]:
    """The aura (score, realm) a character is in now: the place he is
    at, or the aura typed, when he is away; else the covenant he is a
    guest at's, while he is one; else his home's. Casting,
    Penetration and the like use it; his seasons, aging and warping his
    home's (DE pp. 410-411)."""
    if character.away_place_id:
        place = sites.place(saga, character.away_place_id)
        if place is not None:
            return sites.aura_at(place)
    if character.away_aura is not None:
        return character.away_aura, character.away_realm or HERMETIC
    staying = host(saga, character)
    if staying is not None:
        return aura_of(staying)
    return home_aura(saga, character)


def present_aura_kind(saga: Saga, character: Character) -> str:
    """The kind of the aura he is in now (rules.aura_kinds): the place
    he is at's, none for an aura typed, else his home's."""
    if character.away_place_id:
        place = sites.place(saga, character.away_place_id)
        if place is not None:
            return sites.aura_kind_at(place)
    if character.away_aura is not None:
        return ""
    staying = host(saga, character)
    if staying is not None:
        return sites.kind_where(saga, sites.covenant_place(saga, staying))
    return home_aura_kind(saga, character)


def away(character: Character) -> bool:
    """Whether he is away from home (a place or an aura set)."""
    return bool(character.away_place_id) or character.away_aura is not None


def home_aura_kind(saga: Saga, character: Character) -> str:
    """The kind of the aura a character lives in (rules.aura_kinds: a
    Magic aura's alignment, a Faerie one's tints, a Divine one's source),
    read from their covenant's place; "" when it isn't placed."""
    return sites.kind_where(saga, sites.character_place(saga, character))


#: The realm of a Supernatural Virtue or Flaw whose name doesn't say it
#: (DE p. 64: every one has a realm, Magic unless it says otherwise).
VIRTUE_REALMS: dict[str, str] = {
    # Resurrected by a miracle (DE p. 142).
    "vf_raised_from_the_dead": "Divine",
    # "Most often associated with the Infernal realm" (DE p. 85).
    "vf_hex": "Infernal",
}
_REALM_WORDS = (
    ("Faerie", "Faerie"),
    ("Fae", "Faerie"),
    ("Infernal", "Infernal"),
    ("Demonic", "Infernal"),
    ("Divine", "Divine"),
    ("Angelic", "Divine"),
    ("Holy", "Divine"),
)


def virtue_realm(vf_id: str, name: str = "", *, tainted: bool = False) -> str:
    """A Virtue or Flaw's realm: its own where the table names one, a
    Tainted one's Infernal, a name's realm word (Faerie Blood: Faerie),
    else Magic (DE p. 64)."""
    if vf_id in VIRTUE_REALMS:
        return VIRTUE_REALMS[vf_id]
    if tainted:
        return "Infernal"
    for word, realm in _REALM_WORDS:
        if word in name or word.casefold() in vf_id:
            return realm
    return HERMETIC
