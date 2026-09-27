"""Logic behind a Familiar's sheet -- no UI in here.

All five slices of STORY-206 (Identity & Cords, Characteristics, Combat &
Health, Abilities, Bond Powers) are built.
"""

from __future__ import annotations

from . import books as bk
from . import catalog
from . import possessions as pos
from .markup import escape
from .models import (
    ABILITY_CATEGORIES,
    CORD_SCORE_COSTS,
    AbilityDef,
    Character,
    Familiar,
    Saga,
)
from .totals import describe_modifier


def familiar_of(saga: Saga, character_id: str) -> Familiar | None:
    """The one Familiar bound to `character_id`, if any."""
    return next((f for f in saga.familiars if f.character_id == character_id), None)


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
    """Int/Per/Str/Sta then Pre/Com/Dex/Qik, plus the two derived-defense
    figures -- same signed/right-justified formatting as the Character
    sheet's own _characteristics_text(). Base Soak and Magic Resistance are
    typed in, not computed (see Familiar.base_soak/magic_resistance)."""
    c = familiar.characteristics

    def val(n: int) -> str:
        s = f"+{n}" if n > 0 else str(n)
        return f"{s:>2}"

    row1 = "   ".join(
        f"{label}: {val(value)}"
        for label, value in (
            ("Int", c.intelligence),
            ("Per", c.perception),
            ("Str", c.strength),
            ("Sta", c.stamina),
        )
    )
    row2 = "   ".join(
        f"{label}: {val(value)}"
        for label, value in (
            ("Pre", c.presence),
            ("Com", c.communication),
            ("Dex", c.dexterity),
            ("Qik", c.quickness),
        )
    )
    return (
        f"{row1}\n{row2}\n\n"
        f"Base Soak: {familiar.base_soak}    "
        f"Magic Resistance: {familiar.magic_resistance}"
    )


def vf_rows(familiar: Familiar, vf_type: str) -> list[tuple[int, str]]:
    """The familiar's attached Virtues or Flaws (`vf_type`) as (true index
    into familiar.virtues_flaws, label) pairs -- same shape as the Character
    sheet's own _vf_rows()."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return [
        (
            index,
            f"{escape(catalog.describe_virtue_flaw(vf, vf_catalog))} "
            f"({definition.tier})",
        )
        for index, vf in enumerate(familiar.virtues_flaws)
        if (definition := vf_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
    ]


def vf_info_text(familiar: Familiar, index: int | None) -> str:
    """The details panel for the attached Virtue/Flaw at `index` -- same
    shape as the Character sheet's own _vf_info_text()."""
    if index is None:
        return "[dim]Select a Virtue or Flaw to read its rules.[/]"
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    instance = familiar.virtues_flaws[index]
    definition = vf_catalog.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")

    lines = [
        f"[b]Name:[/] {escape(catalog.describe_virtue_flaw(instance, vf_catalog))}"
    ]
    if definition.category:
        lines.append(f"[b]Category:[/] {definition.category}")
    lines.append(f"[b]Tier:[/] {definition.tier}")
    for modifier in definition.modifiers:
        effect = describe_modifier(
            modifier.applies_to,
            modifier.activity,
            modifier.amount,
            modifier.multiplier,
        )
        lines.append(f"[b]Effect:[/] {escape(effect)}")
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    return "\n".join(lines)


def personality_trait_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (i, f"{escape(t.name)}: {t.score:+d}")
        for i, t in enumerate(familiar.personality_traits)
    ]


def reputation_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (i, f"{escape(t.name)}: {t.score:+d}")
        for i, t in enumerate(familiar.reputations)
    ]


def wounds_text(familiar: Familiar) -> str:
    """Same shape as the Character sheet's own _wounds_text()."""
    w = familiar.wounds
    return "\n".join(
        [
            f"Light Wounds:  {w.light} (-1 each)",
            f"Medium Wounds: {w.medium} (-3 each)",
            f"Heavy Wounds:  {w.heavy} (-5 each)",
            f"Incapacitated: {'yes' if w.incapacitated else 'no'}",
            f"Dead: {'yes' if w.dead else 'no'}",
        ]
    )


def fatigue_text(familiar: Familiar) -> str:
    return f"Fatigue Level: {familiar.fatigue_level.title()}"


def natural_weapon_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (index, pos.row_label(pos.PossessionEntry("weapon", weapon)))
        for index, weapon in enumerate(familiar.natural_weapons)
    ]


def natural_weapon_info_text(familiar: Familiar, index: int | None) -> str:
    if index is None:
        return "[dim]Select an attack for its details.[/]"
    weapon = familiar.natural_weapons[index]
    return pos.detail_text(pos.PossessionEntry("weapon", weapon))


def ability_rows(familiar: Familiar) -> list[tuple[int | None, str]]:
    """Same shape as CharacterSheetView._ability_rows() -- one selectable
    list for every Ability, with a non-selectable header row before each
    non-empty category."""
    rows: list[tuple[int | None, str]] = []
    for category in ABILITY_CATEGORIES:
        indexed = [
            (i, a) for i, a in enumerate(familiar.abilities) if a.category == category
        ]
        if not indexed:
            continue
        rows.append((None, category))
        for index, ability in indexed:
            specialty = f" ({ability.specialty})" if ability.specialty else ""
            rows.append(
                (
                    index,
                    f"{escape(ability.name)}{escape(specialty)} "
                    f"{ability.level} {ability.xp}/{ability.xp_to_next}",
                )
            )
    return rows


def _ability_definition(name: str) -> AbilityDef | None:
    canonical = bk.canonical_ability(name)
    if canonical is None:
        return None
    for entry in catalog.load_ability_catalog():
        if entry.name == canonical:
            return entry
        if "{" in entry.name and canonical.startswith(entry.name.split("{", 1)[0]):
            return entry
    return None


def ability_info_text(familiar: Familiar, index: int | None) -> str:
    if index is None:
        return "[dim]Select an Ability for its description.[/]"
    ability = familiar.abilities[index]
    definition = _ability_definition(ability.name)
    if definition is None or not definition.description:
        return "[dim](no catalog description)[/]"
    return escape(definition.description)


def bond_power_rows(familiar: Familiar) -> list[tuple[int, str]]:
    return [
        (index, escape(power.name) or "(unnamed)")
        for index, power in enumerate(familiar.bond_powers)
    ]


def bond_power_info_text(familiar: Familiar, index: int | None) -> str:
    if index is None:
        return "[dim]Select a Bond Power for its details.[/]"
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
