"""The figures a graphical Familiar sheet draws, without a front-end.

The terminal sheet's text is in familiars.py; these are the same facts as
plain values (character_sheet.Fact, its cards and tables), so the desktop
page can give each its own type.
"""

from __future__ import annotations

from dataclasses import dataclass

from .. import familiars as fam
from .. import possessions as pos
from .. import sheet_text as st
from ..models import Familiar, Saga
from ..rules import derived
from . import character as cs
from . import covenant as cvs
from .character import Fact


def subtitle(saga: Saga, familiar: Familiar) -> str:
    """The line under the name: whose familiar, what it is, when it was
    bound, and the saga's season."""
    magus = fam.magus_of(saga, familiar)
    parts = [f"Familiar of {magus.name}" if magus else "Familiar"]
    if familiar.species:
        parts.append(familiar.species)
    if familiar.season_bound and familiar.year_bound is not None:
        parts.append(f"bound {familiar.season_bound} {familiar.year_bound}")
    parts.append(f"{saga.current_season} {saga.current_year}")
    return "  ·  ".join(parts)


def might_pool(familiar: Familiar) -> str:
    """The Might pool left, as the seal's caption gives it ("" untracked)."""
    if familiar.might_pool is None:
        return ""
    return f"{familiar.might_pool} of {familiar.magic_might} in the pool"


def header_facts(familiar: Familiar) -> list[Fact]:
    return [
        Fact("Size", f"{familiar.size:+d}" if familiar.size else "0"),
        Fact("Wound Multiplier", f"×{familiar.wound_multiplier}"),
        Fact("Base Soak", str(familiar.base_soak)),
        Fact("Magic Resistance", str(familiar.magic_resistance)),
    ]


def binding_facts(familiar: Familiar) -> list[Fact]:
    """How the bond was made: typed in, not worked out."""
    f = familiar
    arts = " / ".join(a for a in (f.binding_technique, f.binding_form) if a)
    return [
        Fact("Binding Arts", arts),
        Fact("Binding Lab Total", str(f.binding_lab_total)),
        Fact("Target Binding Level", str(f.target_binding_level)),
        Fact("Vis Spent on Binding", f"{f.vis_spent_binding} pawns"),
    ]


@dataclass(frozen=True)
class Cord:
    """One of the bond's three Cords: its score (0 to 5), what it cost and
    what it does."""

    name: str
    score: int
    cost: int
    effect: str


def cords(familiar: Familiar) -> list[Cord]:
    return [
        Cord(label, score, fam.cord_cost(score), effect)
        for attribute, label, effect in fam.CORDS
        for score in [getattr(familiar, attribute)]
    ]


def vf_cards(familiar: Familiar, side: str) -> list[cs.VirtueFlawCard]:
    return cs.vf_cards(familiar.virtues_flaws, side)


def vf_points(familiar: Familiar, side: str) -> float:
    return st.vf_points(familiar.virtues_flaws, side)


def ability_table(familiar: Familiar) -> list[cs.AbilityRow]:
    return cs.abilities_table(familiar.abilities, familiar.virtues_flaws)


def wound_track(familiar: Familiar) -> list[cs.WoundBand]:
    return cs.damage_table(familiar.wounds, familiar.size)


def fatigue_track(familiar: Familiar) -> list[tuple[str, int, bool]]:
    return cs.fatigue_levels(familiar.fatigue_level, familiar.virtues_flaws)


def health_facts(familiar: Familiar) -> list[Fact]:
    """The typed-in Soak and Magic Resistance, and the penalties wounds and
    Fatigue give."""
    vfs = familiar.virtues_flaws
    wounds = derived.wound_penalty(familiar.wounds, vfs)
    fatigue = derived.fatigue_penalty(familiar.fatigue_level, vfs)
    return [
        Fact("Base Soak", str(familiar.base_soak)),
        Fact("Magic Resistance", str(familiar.magic_resistance)),
        Fact("Wound Penalty", f"{wounds:+d}"),
        Fact("Total Penalty", f"{wounds + fatigue:+d}"),
    ]


def natural_weapons(familiar: Familiar) -> cvs.Table:
    """Its natural weapons' combat figures; the gear columns a covenant's
    weapons have (type, quality, load) mean nothing for talons."""
    return cvs.Table(
        ["Attack", "Init", "Atk", "Def", "Dmg"],
        [
            [
                w.name or "(unnamed)",
                pos.signed(w.weapon_init),
                pos.signed(w.weapon_attack),
                pos.signed(w.weapon_defense),
                pos.signed(w.weapon_damage),
            ]
            for w in familiar.natural_weapons
        ],
    )


@dataclass(frozen=True)
class BondPowerCard:
    """One Bond Power as a card: `index` into the familiar's powers, its
    Arts (for the Form's symbol) and its figures."""

    index: int
    name: str
    level: int
    technique: str
    form: str
    uses_per_day: int
    penetration: int

    @property
    def arts(self) -> str:
        return " ".join(a for a in (self.technique, self.form) if a)


def bond_power_cards(familiar: Familiar) -> list[BondPowerCard]:
    return [
        BondPowerCard(
            index,
            power.name or "(unnamed)",
            power.level,
            power.technique,
            power.form,
            power.uses_per_day,
            power.penetration,
        )
        for index, power in enumerate(familiar.bond_powers)
    ]


@dataclass(frozen=True)
class FamiliarCard:
    """A familiar as a card among its covenant's people or on its magus's
    sheet."""

    id: str
    name: str
    subtitle: str
    detail: str


def familiar_card(saga: Saga, familiar: Familiar) -> FamiliarCard:
    magus = fam.magus_of(saga, familiar)
    detail = [f"Magic Might {familiar.magic_might}"]
    if familiar.bond_powers:
        detail.append(f"{len(familiar.bond_powers)} Bond Powers")
    return FamiliarCard(
        familiar.id,
        familiar.name or "(unnamed)",
        "  ·  ".join(
            [f"Familiar of {magus.name}" if magus else "Familiar"]
            + ([familiar.species] if familiar.species else [])
        ),
        "  ·  ".join(detail),
    )


def familiars_in(saga: Saga, covenant_id: str | None) -> list[Familiar]:
    """The familiars of the magi who belong to a covenant (None: to none)."""
    return [
        f
        for f in saga.familiars
        for magus in [fam.magus_of(saga, f)]
        if magus is not None and magus.covenant_id == covenant_id
    ]
