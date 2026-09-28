"""Logic behind a Familiar's sheet -- no UI in here.

All five slices of STORY-206 (Identity & Cords, Characteristics, Combat &
Health, Abilities, Bond Powers) are built.
"""

from __future__ import annotations

from . import possessions as pos
from . import sheet_text as st
from . import storage
from .markup import escape
from .models import (
    CORD_SCORE_COSTS,
    Character,
    Familiar,
    Saga,
    ScoredTrait,
    VirtueFlawInstance,
)


def familiar_of(saga: Saga, character_id: str) -> Familiar | None:
    """The one Familiar bound to `character_id`, if any."""
    return next((f for f in saga.familiars if f.character_id == character_id), None)


def unbonded_magi(saga: Saga) -> list[Character]:
    """Magi with no Familiar bound yet -- one per magus at a time."""
    bonded = {f.character_id for f in saga.familiars}
    return [c for c in saga.characters if c.type == "magus" and c.id not in bonded]


def bind_familiar(saga: Saga, magus: Character, name: str) -> Familiar:
    """Bind a new Familiar called `name` to `magus` and add it to the saga.
    Both gain the True Friend Virtue and a Loyal (Partner) +3 Personality
    Trait, which the bond grants."""
    familiar = Familiar(
        id=storage.generate_unique_id(name, [f.id for f in saga.familiars]),
        character_id=magus.id,
        name=name,
    )
    for partner in (familiar, magus):
        partner.virtues_flaws.append(VirtueFlawInstance(vf_id="vf_true_friend"))
        partner.personality_traits.append(ScoredTrait(name="Loyal (Partner)", score=3))
    saga.familiars.append(familiar)
    return familiar


def magus_of(saga: Saga, familiar: Familiar) -> Character | None:
    """The magus who bound `familiar`."""
    return saga.character(familiar.character_id)


def cord_cost(score: int) -> int:
    """The point cost of a Cord score (0-5), from the fixed table."""
    return CORD_SCORE_COSTS[score]


def identity_text(saga: Saga, familiar: Familiar) -> str:
    magus = magus_of(saga, familiar)
    lines = [
        f"Magus Partner: {escape(magus.name) if magus is not None else '(unknown)'}",
        f"Species / Description: {escape(familiar.species) or '(not set)'}",
        "Season / Year Bound: "
        + (
            f"{familiar.season_bound} {familiar.year_bound}"
            if familiar.season_bound and familiar.year_bound is not None
            else "(not set)"
        ),
        f"Magic Might Score: {familiar.magic_might}"
        + (
            f" (Current Pool: {familiar.might_pool})"
            if familiar.might_pool is not None
            else ""
        ),
        f"Size: {familiar.size} (Wound Multiplier: {familiar.wound_multiplier})",
    ]
    return "\n".join(lines)


def binding_text(familiar: Familiar) -> str:
    f = familiar
    return "\n".join(
        [
            "Binding Arts Used: "
            + (
                f"{f.binding_technique} / {f.binding_form}"
                if f.binding_technique or f.binding_form
                else "(not set)"
            ),
            f"Initial Binding Lab Total: {f.binding_lab_total}",
            f"Target Binding Level: {f.target_binding_level}",
            f"Cumulative Vis Spent on Binding: {f.vis_spent_binding} pawns",
        ]
    )


#: (attribute, display label, mechanical-effect blurb) for the three Cords,
#: in sheet order.
CORDS: tuple[tuple[str, str, str], ...] = (
    (
        "golden_cord",
        "Golden Cord",
        "Subtracts score from Magic & Lab Botch Dice (min 1 botch die remaining).",
    ),
    (
        "silver_cord",
        "Silver Cord",
        "Bonus to Personality Trait rolls & Mental Resistance. "
        "Mind-Freeing Roll: Stress Die + Score >= 9.",
    ),
    (
        "bronze_cord",
        "Bronze Cord",
        "Bonus to Base Soak, Healing rolls, Deprivation rolls, and Aging rolls.",
    ),
)


def cords_text(familiar: Familiar) -> str:
    lines = []
    for attribute, label, blurb in CORDS:
        score = getattr(familiar, attribute)
        lines.append(f"{label}: +{score} ({cord_cost(score)} pts) -- {blurb}")
    return "\n".join(lines)


def characteristics_text(familiar: Familiar) -> str:
    """The Characteristics as on the Character sheet, plus the two
    derived-defense figures. Base Soak and Magic Resistance are typed in, not
    computed (see Familiar.base_soak/magic_resistance)."""
    return (
        f"{st.characteristics_text(familiar.characteristics)}\n\n"
        f"Base Soak: {familiar.base_soak}    "
        f"Magic Resistance: {familiar.magic_resistance}"
    )


def vf_rows(familiar: Familiar, vf_type: str) -> list[tuple[int | None, str]]:
    return st.vf_rows(familiar.virtues_flaws, vf_type)


def vf_info_text(familiar: Familiar, index: int | None) -> str:
    return st.vf_info_text(familiar.virtues_flaws, index)


def personality_trait_rows(familiar: Familiar) -> list[tuple[int | None, str]]:
    return st.trait_rows(familiar.personality_traits)


def reputation_rows(familiar: Familiar) -> list[tuple[int | None, str]]:
    return st.trait_rows(familiar.reputations)


def wounds_text(familiar: Familiar) -> str:
    return st.wounds_text(familiar.wounds)


def fatigue_text(familiar: Familiar) -> str:
    return st.fatigue_text(familiar.fatigue_level)


def natural_weapon_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (index, pos.row_label(pos.PossessionEntry("weapon", weapon)))
        for index, weapon in enumerate(familiar.natural_weapons)
    ]


def natural_weapon_info_text(familiar: Familiar, index: int | None) -> str:
    if index is None:
        return "[dim]Select an attack to see its details.[/]"
    weapon = familiar.natural_weapons[index]
    return pos.detail_text(pos.PossessionEntry("weapon", weapon))


def ability_rows(familiar: Familiar) -> list[tuple[int | None, str]]:
    return st.ability_rows(familiar.abilities)


def ability_info_text(familiar: Familiar, index: int | None) -> str:
    return st.ability_info_text(familiar.abilities, index)


def bond_power_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (index, escape(power.name) or "(unnamed)")
        for index, power in enumerate(familiar.bond_powers)
    ]


def bond_power_info_text(familiar: Familiar, index: int | None) -> str:
    if index is None:
        return "[dim]Select a Bond Power to see its details.[/]"
    power = familiar.bond_powers[index]
    tech_form = " / ".join(t for t in (power.technique, power.form) if t) or "(none)"
    lines = [
        f"[b]Name:[/] {escape(power.name) or '(unnamed)'}",
        f"[b]Level:[/] {power.level}",
        f"[b]Technique / Form:[/] {escape(tech_form)}",
        f"[b]Target & Controller:[/] {escape(power.target_controller) or '(not set)'}",
        f"[b]Uses/Day:[/] {power.uses_per_day}",
        f"[b]Penetration:[/] {power.penetration}",
        f"[b]Vis Spent:[/] {power.vis_spent}",
        f"[b]Cosmetic Trait:[/] {escape(power.cosmetic_trait) or '(none)'}",
    ]
    return "\n".join(lines)
