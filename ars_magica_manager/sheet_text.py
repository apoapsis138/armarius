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
    VirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
)
from .rules import xp as xp_rules
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


def score_text(progress: xp_rules.Progress) -> str:
    """A score and its total xp against the total the next score needs,
    e.g. "5 85/105": score 5, 85 xp spent, score 6 at 105."""
    return f"{progress.score} {progress.total}/{progress.next_total}"


def xp_line(progress: xp_rules.Progress) -> str:
    """The details-panel line for an Art or Ability's score and total xp."""
    return (
        f"[b]Score:[/] {progress.score}    [b]XP:[/] {progress.total} "
        f"(score {progress.score + 1} at {progress.next_total} xp)"
    )


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
                    f"{score_text(ability.progress)}",
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
        return "[dim]Select an Ability to see its details.[/]"
    ability = abilities[index]
    definition = ability_definition(ability.name)
    if definition is None or not definition.description:
        description = "[dim](no catalog description)[/]"
    else:
        description = escape(definition.description)
    return "\n\n".join([xp_line(ability.progress), description])


def vf_rows(
    instances: Sequence[VirtueFlawInstance], vf_type: str
) -> list[tuple[int | None, str]]:
    """The attached Virtues or Flaws (`vf_type`) as (true index into
    `instances`, label) pairs, so a filtered list still maps back to the
    real entry. Qualities list with the Virtues, Inferiorities with the
    Flaws (VirtueFlawDef.side)."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return [
        (
            index,
            f"{escape(catalog.describe_virtue_flaw(vf, vf_catalog))} "
            f"({definition.tier})",
        )
        for index, vf in enumerate(instances)
        if (definition := vf_catalog.get(vf.vf_id)) is not None
        and definition.side == vf_type
    ]


def vf_points(instances: Sequence[VirtueFlawInstance], vf_type: str) -> float:
    """The points the attached Virtues or Flaws (`vf_type`, Qualities and
    Inferiorities included) come to: Minor 1, Major 3, Free 0 each (entries
    not in the catalog count nothing)."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return sum(
        abs(definition.cost)
        for vf in instances
        if (definition := vf_catalog.get(vf.vf_id)) is not None
        and definition.side == vf_type
    )


def vf_repeat_text(definition: VirtueFlawDef) -> str:
    """How often a character may take a repeatable Virtue/Flaw, e.g. "May be
    taken up to 2 times, for a different Art each time", or "" if once."""
    if not definition.repeatable:
        return ""
    head = (
        f"May be taken up to {definition.max_count} times"
        if definition.max_count
        else "May be taken more than once"
    )
    if not definition.parameters or definition.max_per_parameter is None:
        return head + "."
    what = " and ".join(p.title() for p in definition.parameters)
    if definition.max_per_parameter == 1:
        return f"{head}, for a different {what} each time."
    return f"{head}, at most {definition.max_per_parameter} times for the same {what}."


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
        return "[dim]Select a Virtue or Flaw to see its details.[/]"
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    instance = instances[index]
    definition = vf_catalog.get(instance.vf_id)
    if definition is None:
        return escape(f"{instance.vf_id} (not in catalog)")

    lines = [
        f"[b]Name:[/] {escape(catalog.describe_virtue_flaw(instance, vf_catalog))}"
    ]
    if definition.category:
        lines.append(f"[b]Category:[/] {escape(definition.category_label)}")
    lines.append(f"[b]Tier:[/] {definition.tier}")
    if repeat := vf_repeat_text(definition):
        lines.append(f"[dim]{repeat}[/]")
    lines += effect_lines(definition.modifiers)
    lines += ["", "[b]Rules:[/]", escape(definition.description)]
    if definition.source:
        lines += ["", f"[dim]Source: {escape(definition.source)}[/]"]
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
