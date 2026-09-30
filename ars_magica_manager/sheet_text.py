"""Text for the parts of a sheet that Characters and Familiars share --
Characteristics, Abilities, Virtues & Flaws, Personality Traits and
Reputations, Wounds and Fatigue. Each takes the field it shows rather than
the whole record, so both sheets render them the same way. Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections.abc import Sequence

from . import books as bk
from . import catalog
from . import spells as spl
from .markup import escape
from .models import (
    ABILITY_CATEGORIES,
    Ability,
    AbilityDef,
    Breakthrough,
    Character,
    Characteristics,
    Modifier,
    Possession,
    Saga,
    ScoredTrait,
    VirtueFlawDef,
    VirtueFlawInstance,
    Wounds,
)
from .rules import combat, derived, penetration, scores
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


def score_text(progress: xp_rules.Progress, bonus: int = 0) -> str:
    """A score and its total xp against the total the next score needs,
    e.g. "5 85/105": score 5, 85 xp spent, score 6 at 105. With a fixed
    bonus or penalty (Puissant, a Flaw) the adjusted score follows in
    parentheses: "5 (7) 85/105" (STORY-212)."""
    return (
        f"{adjusted_score(progress.score, bonus)} "
        f"{progress.total}/{progress.next_total}"
    )


def adjusted_score(score: int, bonus: int) -> str:
    """A list row's score: the base, then the score used when a fixed bonus
    or penalty applies: "5 (7)" (Hedda 2026-09-29, STORY-212)."""
    return f"{score} ({score + bonus})" if bonus else str(score)


def bonus_score(score: int, bonus: int) -> str:
    """A score with any fixed bonus beside it: "5", "5+2", "5-1"."""
    return f"{score}{bonus:+d}" if bonus else str(score)


def xp_line(
    progress: xp_rules.Progress, bonus: int = 0, bonus_from: Sequence[str] = ()
) -> str:
    """The details-panel line for an Art or Ability's score and total xp,
    with a line for any fixed bonus and where it comes from."""
    line = (
        f"[b]Score:[/] {bonus_score(progress.score, bonus)}    "
        f"[b]XP:[/] {progress.total} "
        f"(score {progress.score + 1} at {progress.next_total} xp)"
    )
    if bonus:
        line += (
            f"\n[b]Used at:[/] {progress.score + bonus} "
            f"({bonus:+d} from {escape(', '.join(bonus_from))})"
        )
    return line


def ability_rows(
    abilities: Sequence[Ability], virtues_flaws: Sequence[VirtueFlawInstance] = ()
) -> list[tuple[int | None, str]]:
    """One selectable list for every Ability, with a header (non-selectable)
    row before each non-empty category -- unlike Virtues/Flaws, Abilities
    has too many categories for side-by-side lists. `virtues_flaws` are the
    owner's, for fixed bonuses such as Puissant."""
    rows: list[tuple[int | None, str]] = []
    for category in ABILITY_CATEGORIES:
        indexed = [(i, a) for i, a in enumerate(abilities) if a.category == category]
        if not indexed:
            continue
        rows.append((None, category))
        for index, ability in indexed:
            specialty = f" ({ability.specialty})" if ability.specialty else ""
            bonus, _ = scores.ability_bonus(virtues_flaws, ability.name)
            rows.append(
                (
                    index,
                    f"{escape(ability.name)}{escape(specialty)} "
                    f"{score_text(ability.progress, bonus)}",
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


def ability_info_text(
    abilities: Sequence[Ability],
    index: int | None,
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
) -> str:
    if index is None:
        return "[dim]Select an Ability to see its details.[/]"
    ability = abilities[index]
    definition = ability_definition(ability.name)
    if definition is None or not definition.description:
        description = "[dim](no catalog description)[/]"
    else:
        description = escape(definition.description)
    bonus, bonus_from = scores.ability_bonus(virtues_flaws, ability.name)
    return "\n\n".join([xp_line(ability.progress, bonus, bonus_from), description])


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


def known_spell_rows(saga: Saga, character: Character) -> list[tuple[int | None, str]]:
    """A magus's Known Spells as (index, label) rows: the spell's table row
    (a catalog spell or one of the saga's own) and its Mastery score, or
    the stored id when the spell can't be found."""
    rows: list[tuple[int | None, str]] = []
    for index, known in enumerate(character.spells_known):
        spell = spl.find_spell(saga, known.spell_id)
        if spell is None:
            rows.append((index, f"{escape(known.spell_id)} (unknown spell)"))
            continue
        label = spl.row_label(saga, spell)
        if known.mastery_score:
            label += f"  [b]Mastery {known.mastery_score}[/]"
        rows.append((index, label))
    return rows


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


def combat_text(character: Character, weapon: Possession) -> str:
    """A weapon's combat totals for the character, before the die."""
    totals = combat.combat_totals(character, weapon)

    def show(breakdown) -> str:
        if breakdown is None:
            return "n/a"
        return f"{int(breakdown.total):+d}"

    lines = [
        "[b]Combat totals[/] (add a stress die):",
        f"Initiative {show(totals.initiative)}   Attack {show(totals.attack)}   "
        f"Defence {show(totals.defence)}   Damage {show(totals.damage)}",
        f"Soak {int(derived.soak(character).total):+d}",
    ]
    if totals.ability is None:
        lines.append(
            "[dim]Typed in by hand, so no Combat Ability is counted: choose it "
            "from the weapon catalog to add one.[/]"
        )
    else:
        lines.append(f"[dim]Combat Ability: {escape(totals.ability)}.[/]")
    return "\n".join(lines)


def faith_score_text(character: Character) -> str:
    """The True Faith Score, with the Magic Resistance it gives (x10)."""
    score = character.background.true_faith_score
    if score <= 0:
        return str(score)
    return f"{score} (Magic Resistance {penetration.faith_magic_resistance(character)})"


def size_text(character: Character) -> str:
    """The character's Size, with its base and Virtues when they differ."""
    breakdown = derived.size(character)
    total = int(breakdown.total)
    if len(breakdown.lines) == 1:
        return str(total)
    base = int(breakdown.lines[0].amount or 0)
    rest = ", ".join(f"{line.label} {line.amount:+g}" for line in breakdown.lines[1:])
    return f"{total} (base {base}, {rest})"


def character_wounds_text(character: Character) -> str:
    """A character's Health column: Soak and Encumbrance worked out, the
    Wound Penalty, then the wounds as typed."""
    soak = derived.soak(character)
    load = derived.carried_load(character.inventory)
    burden = derived.burden(load)
    strength = character.characteristics.strength
    encumbrance = derived.encumbrance(load, strength)
    enc_terms = f"Load {load}, Burden {burden}"
    if strength > 0 and burden:
        enc_terms += f", Str {strength:+d}"
    lines = [
        f"Soak: {int(soak.total)} ({derived.terms(soak)})",
        f"Encumbrance: {encumbrance} ({enc_terms})",
        f"Wound Penalty: {derived.wound_penalty(character.wounds):+d}",
        "",
        wounds_text(character.wounds),
    ]
    return "\n".join(lines)


def character_fatigue_text(character: Character) -> str:
    """A character's Fatigue with its penalty, the combined penalty, and
    the Damage Table for the character's Size."""
    level = character.fatigue_level
    fatigue = derived.fatigue_penalty(level)
    wounds = derived.wound_penalty(character.wounds)
    size = int(derived.size(character).total)
    bands = [
        f"{name} {low}+" if high is None else f"{name} {low}-{high}"
        for name, low, high in derived.wound_ranges(size)
    ]
    return "\n".join(
        [
            f"Fatigue Level: {level.title()} ({fatigue:+d})",
            f"Total Penalty: {wounds + fatigue:+d} (wounds, fatigue)",
            "",
            f"Damage Table (Size {size}):",
            f"{bands[0]}, {bands[1]},",
            f"{bands[2]}, {bands[3]},",
            bands[4],
        ]
    )


def fatigue_text(fatigue_level: str) -> str:
    return f"Fatigue Level: {fatigue_level.title()}"


def goal_row(goal: Breakthrough) -> str:
    """A research goal's row (STORY-916): its name, kind, points toward its
    target, and what waits on it."""
    extras = []
    if goal.reached:
        extras.append("reached")
    if goal.pending_magnitude:
        extras.append(f"Discovery to stabilize ({goal.pending_magnitude})")
    if goal.insights:
        extras.append(f"{goal.insights} insight(s) to invent")
    tail = f"  [dim]{'; '.join(extras)}[/]" if extras else ""
    return (
        f"{escape(goal.name)} ({goal.kind}): {goal.points}/{goal.target} points" + tail
    )


def goal_text(goal: Breakthrough) -> str:
    """A research goal's details panel."""
    grants = {
        "Ability": f"the Ability {goal.grant} (its points as xp)",
        "Virtue": f"the Virtue {goal.grant}",
        "Parameter": f"a new parameter: {goal.grant}",
    }.get(goal.grant_kind, "whatever the troupe decides")
    if goal.grant_kind == "Virtue":
        found = catalog.load_virtue_flaw_catalog_by_id().get(goal.grant)
        grants = f"the Virtue {found.name if found else goal.grant}"
    lines = [
        f"[b]{escape(goal.name)}[/]: a {goal.kind} Breakthrough, "
        f"{goal.points}/{goal.target} points" + (" (reached)" if goal.reached else ""),
        f"Reaching it grants {escape(grants)}.",
    ]
    if goal.pending_magnitude:
        lines.append(
            f"A Discovery (magnitude {goal.pending_magnitude}) waits to be "
            f"stabilized: {goal.discovery_seasons} season(s) at Lab Total "
            f"{goal.discovery_lab_total}, risk +{goal.discovery_risk}"
            + (f", {goal.discovery_vis} pawn(s) of vis" if goal.discovery_vis else "")
            + (
                f" ({goal.stabilizing_seasons} done)"
                if goal.stabilizing_seasons
                else ""
            )
            + "."
        )
    if goal.insights:
        lines.append(
            f"{goal.insights} insight(s) to invent: each effect invented adds "
            "its magnitude."
        )
    if goal.description.strip():
        lines += ["", escape(goal.description.strip())]
    return "\n".join(lines)
