"""Text for the parts of a sheet that Characters and Familiars share --
Characteristics, Abilities, Virtues & Flaws, Personality Traits and
Reputations, Wounds and Fatigue. Each takes the field it shows rather than
the whole record, so both sheets render them the same way. Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections.abc import Sequence

from . import books as bk
from . import catalog
from .markup import escape
from .models import (
    ABILITY_CATEGORIES,
    Ability,
    AbilityDef,
    Characteristics,
    Modifier,
    ScoredTrait,
    VirtueFlawInstance,
    Wounds,
)
from .totals import describe_modifier


def characteristics_text(c: Characteristics) -> str:
    """Int/Per/Str/Sta then Pre/Com/Dex/Qik, each value signed (a plain "0"
    rather than "+0") and right-justified so the columns align."""

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
    return f"{row1}\n{row2}"


def ability_rows(abilities: Sequence[Ability]) -> list[tuple[int | None, str]]:
    """One selectable list for every Ability, with a header (non-selectable)
    row before each non-empty category -- unlike Virtues/Flaws, Abilities
    has too many categories for side-by-side lists."""
    rows: list[tuple[int | None, str]] = []
    for category in ABILITY_CATEGORIES:
        indexed = [(i, a) for i, a in enumerate(abilities) if a.category == category]
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


def ability_definition(name: str) -> AbilityDef | None:
    """The ability catalog entry matching `name`, resolving a templated
    family ("Area Lore: Rhine" -> "Area Lore: {region}") the same way
    books.canonical_ability() does; None if it isn't a known ability."""
    canonical = bk.canonical_ability(name)
    if canonical is None:
        return None
    for entry in catalog.load_ability_catalog():
        if entry.name == canonical:
            return entry
        if "{" in entry.name and canonical.startswith(entry.name.split("{", 1)[0]):
            return entry
    return None


def ability_info_text(abilities: Sequence[Ability], index: int | None) -> str:
    if index is None:
        return "[dim]Select an Ability for its description.[/]"
    definition = ability_definition(abilities[index].name)
    if definition is None or not definition.description:
        return "[dim](no catalog description)[/]"
    return escape(definition.description)


def vf_rows(
    instances: Sequence[VirtueFlawInstance], vf_type: str
) -> list[tuple[int | None, str]]:
    """The attached Virtues or Flaws (`vf_type`) as (true index into
    `instances`, label) pairs, so a filtered list still maps back to the
    real entry."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return [
        (
            index,
            f"{escape(catalog.describe_virtue_flaw(vf, vf_catalog))} "
            f"({definition.tier})",
        )
        for index, vf in enumerate(instances)
        if (definition := vf_catalog.get(vf.vf_id)) is not None
        and definition.type == vf_type
    ]


def effect_lines(modifiers: Sequence[Modifier]) -> list[str]:
    """One "Effect:" details-panel line per catalog modifier."""
    return [
        "[b]Effect:[/] "
        + escape(describe_modifier(m.applies_to, m.activity, m.amount, m.multiplier))
        for m in modifiers
    ]


def vf_info_text(instances: Sequence[VirtueFlawInstance], index: int | None) -> str:
    """The details panel for the attached Virtue/Flaw at `index`: its name,
    category, tier, effects, and the official rules text."""
    if index is None:
        return "[dim]Select a Virtue or Flaw to read its rules.[/]"
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    instance = instances[index]
    definition = vf_catalog.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")

    lines = [
        f"[b]Name:[/] {escape(catalog.describe_virtue_flaw(instance, vf_catalog))}"
    ]
    if definition.category:
        lines.append(f"[b]Category:[/] {definition.category}")
    lines.append(f"[b]Tier:[/] {definition.tier}")
    lines += effect_lines(definition.modifiers)
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    return "\n".join(lines)


def trait_rows(traits: Sequence[ScoredTrait]) -> list[tuple[int | None, str]]:
    """Personality Traits or Reputations as (index, "Name: +2") rows."""
    return [
        (index, f"{escape(t.name)}: {t.score:+d}") for index, t in enumerate(traits)
    ]


def wounds_text(w: Wounds, *, with_soak: bool = False) -> str:
    lines = [f"Soak: {w.soak}"] if with_soak else []
    lines += [
        f"Light Wounds:  {w.light} (-1 each)",
        f"Medium Wounds: {w.medium} (-3 each)",
        f"Heavy Wounds:  {w.heavy} (-5 each)",
        f"Incapacitated: {'yes' if w.incapacitated else 'no'}",
        f"Dead: {'yes' if w.dead else 'no'}",
    ]
    return "\n".join(lines)


def fatigue_text(fatigue_level: str) -> str:
    return f"Fatigue Level: {fatigue_level.title()}"
