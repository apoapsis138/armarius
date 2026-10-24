"""Text for the parts of a sheet that Characters and Familiars share --
Characteristics, Abilities, Virtues & Flaws, Personality Traits and
Reputations, Wounds and Fatigue. Each takes the field it shows rather than
the whole record, so both sheets render them the same way. Like the other
domain modules it returns markup text, never widgets."""

from __future__ import annotations

from collections.abc import Collection, Sequence

from . import books as bk
from . import catalog, sourcebooks
from . import spells as spl
from .markup import escape, problem
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
    WoundState,
)
from .rules import (
    combat,
    derived,
    disease,
    equipment,
    penetration,
    recovery,
    research,
    scores,
    senses,
    travel,
)
from .rules import xp as xp_rules
from .rules.breakdown import Breakdown
from .totals import describe_modifier


def characteristics_text(c: Characteristics, *, cunning: bool = False) -> str:
    """Int/Per/Str/Sta then Pre/Com/Dex/Qik, each value signed (a plain "0"
    rather than "+0") and right-justified so the columns align; an
    animal's (`cunning`) first is Cun."""

    def val(n: int) -> str:
        s = f"+{n}" if n > 0 else str(n)
        return f"{s:>2}"

    row1 = "   ".join(
        f"{label}: {val(value)}"
        for label, value in (
            ("Cun" if cunning else "Int", c.intelligence),
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
    parentheses: "5 (7) 85/105"."""
    return (
        f"{adjusted_score(progress.score, bonus)} "
        f"{progress.total}/{progress.next_total}"
    )


def adjusted_score(score: int, bonus: int) -> str:
    """A list row's score: the base, then the score used when a fixed bonus
    or penalty applies: "5 (7)"."""
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


def live_score(xp: int | None, factor: int, bonus: int = 0) -> str:
    """What a typed total xp buys, for a form to show as it changes: the
    score and the total xp the next one needs, "Score 2 · Score 3 at 30
    xp" (a total, like the field it sits beside), "Score 2 (4) · ..." with
    a fixed bonus. `factor` is xp_rules' ABILITY_FACTOR or ART_FACTOR; an
    xp that isn't a whole number of 0 or more (yet) shows "Score ?"."""
    if xp is None or xp < 0:
        return "Score ?"
    progress = xp_rules.progress(xp, factor)
    return (
        f"Score {adjusted_score(progress.score, bonus)} · "
        f"Score {progress.score + 1} at {progress.next_total} xp"
    )


def ability_rows(
    abilities: Sequence[Ability],
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
    leave_out: Collection[str] = (),
) -> list[tuple[int | None, str]]:
    """One selectable list for every Ability, with a header (non-selectable)
    row before each non-empty category -- unlike Virtues/Flaws, Abilities
    has too many categories for side-by-side lists. `virtues_flaws` are the
    owner's, for fixed bonuses such as Puissant; the Abilities named in
    `leave_out` (those a tradition's own chapter shows) are left out.

    Scores and xp line up in columns, named once on the first header row,
    with the xp quieter than the score; an adjusted score sits in its own
    slot after the base, so the base scores still line up."""
    groups = [
        (
            category,
            [
                (i, a)
                for i, a in enumerate(abilities)
                if a.category == category and a.name not in leave_out
            ],
        )
        for category in ABILITY_CATEGORIES
    ]
    return grouped_ability_rows(abilities, groups, virtues_flaws)


def grouped_ability_rows(
    abilities: Sequence[Ability],
    groups: Sequence[tuple[str, Sequence[tuple[int, Ability]]]],
    virtues_flaws: Sequence[VirtueFlawInstance] = (),
) -> list[tuple[int | None, str]]:
    """ability_rows' list for Abilities already put in headed groups (a
    heading, then (index in `abilities`, Ability) pairs); an empty group
    is skipped. A tradition's chapter groups its Arts this way."""
    shown = [a for _, group in groups for _, a in group]
    names = {
        id(a): a.name + (f" ({a.specialty})" if a.specialty else "") for a in shown
    }
    width = max([len(name) for name in names.values()] + [_ABILITY_NAME_MIN]) + 2
    rows: list[tuple[int | None, str]] = []
    for heading, indexed in groups:
        if not indexed:
            continue
        columns = (
            f"[$label]{'Score':>{_SCORE_WIDTH}}{' ' * _ADJUSTED_WIDTH}"
            f"{'XP':>{_XP_WIDTH}}[/]"
            if not rows
            else ""
        )
        # a header has no row marker, so it's padded past one
        rows.append((None, _pad(heading, width + _ROW_MARKER) + columns))
        for index, ability in indexed:
            bonus, _ = scores.ability_bonus(virtues_flaws, ability.name)
            progress = ability.progress
            adjusted = f" ({progress.score + bonus})" if bonus else ""
            xp = f"{progress.total}/{progress.next_total}"
            rows.append(
                (
                    index,
                    f"{_pad(names[id(ability)], width)}"
                    f"{progress.score:>{_SCORE_WIDTH}}"
                    f"{adjusted:<{_ADJUSTED_WIDTH}}"
                    f"[$label]{xp:>{_XP_WIDTH}}[/]",
                )
            )
    return rows


#: The Abilities list's columns (ability_rows): the name column is at least
#: this wide, then the score (right-aligned under "Score"), room for an
#: adjusted score " (12)", and the xp "105/120".
_ABILITY_NAME_MIN = 20
#: A selectable row's marker and its space ("○ ", SelectableList).
_ROW_MARKER = 2
_SCORE_WIDTH = 5
_ADJUSTED_WIDTH = 5
_XP_WIDTH = 8


def _pad(text: str, width: int) -> str:
    """`text` escaped for markup and padded with spaces to `width` columns
    (padding counts the text as shown, not its escapes)."""
    return escape(text) + " " * max(width - len(text), 0)


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
    parts = [xp_line(ability.progress, bonus, bonus_from), description]
    ease = senses.ease_text(ability.name)
    if ease:
        parts.append(escape(ease))
    return "\n\n".join(parts)


def ability_entry_text(definition: AbilityDef) -> str:
    """A catalog Ability as the picker shows it under the list: its
    category, what it needs naming, what it covers and its book."""
    lines = [f"[b]Category:[/] {escape(definition.category)}"]
    if definition.parameters:
        lines.append(f"[b]Needs:[/] {escape(', '.join(definition.parameters))}")
    lines += ["", escape(definition.description) or "[dim](no description)[/]"]
    lines += ["", f"[dim]Source: {escape(sourcebooks.titles(definition.source))}[/]"]
    return "\n".join(lines)


def vf_rows(
    instances: Sequence[VirtueFlawInstance],
    vf_type: str,
    free: Collection[int] = (),
) -> list[tuple[int | None, str]]:
    """The attached Virtues or Flaws (`vf_type`) as (true index into `instances`, label)
    pairs, so a filtered list still maps back to the real entry. Qualities list with the
    Virtues, Inferiorities with the Flaws (VirtueFlawDef.side). Indices in `free` (a
    magus's House Virtue) are marked Free."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return [
        (
            index,
            f"{escape(catalog.describe_virtue_flaw(vf, vf_catalog))} "
            f"({definition.tier}{', Free' if index in free else ''})",
        )
        for index, vf in enumerate(instances)
        if (definition := vf_catalog.get(vf.vf_id)) is not None
        and definition.side == vf_type
    ]


def vf_points(
    instances: Sequence[VirtueFlawInstance],
    vf_type: str,
    free: Collection[int] = (),
) -> float:
    """The points the attached Virtues or Flaws (`vf_type`, Qualities and
    Inferiorities included) come to: Minor 1, Major 3, Free 0 each (entries
    not in the catalog, and indices in `free`, count nothing)."""
    vf_catalog = catalog.load_virtue_flaw_catalog_by_id()
    return sum(
        abs(definition.cost)
        for index, vf in enumerate(instances)
        if index not in free
        and (definition := vf_catalog.get(vf.vf_id)) is not None
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
    """Personality Traits or Reputations as (index, "Name: +2") rows; a
    Reputation's kind and reach follow in brackets when set."""
    rows: list[tuple[int | None, str]] = []
    for index, t in enumerate(traits):
        row = f"{escape(t.name)}: {t.score:+d}"
        where = ", ".join(x for x in (t.type, t.reach) if x)
        if where:
            row += f" [$label]({escape(where)})[/]"
        rows.append((index, row))
    return rows


def known_spell_rows(saga: Saga, character: Character) -> list[tuple[int | None, str]]:
    """A magus's Known Spells as (index, label) rows: the spell's table row
    (a catalog spell or one of the saga's own) and its Mastery score, or
    the stored id when the spell can't be found."""
    rows: list[tuple[int | None, str]] = []
    for index, known in enumerate(character.spells_known):
        spell = catalog.find_spell(saga, known.spell_id)
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

    def show(breakdown: Breakdown | None) -> str:
        if breakdown is None:
            return "n/a"
        return f"{int(breakdown.total):+d}"

    with_shield = (
        f" (with {escape(totals.shield.name)})" if totals.shield is not None else ""
    )
    lines = [
        f"[b]Combat totals[/]{with_shield} (add a stress die):",
        f"Initiative {show(totals.initiative)}   Attack {show(totals.attack)}   "
        f"Defence {show(totals.defence)}   Damage {show(totals.damage)}",
        f"Soak {int(derived.soak(character).total):+d}   Defence against missiles "
        f"{show(totals.missile_defence)} (only a shield counts)",
    ]
    least = combat.minimum_strength(weapon)
    strength = character.characteristics.strength
    for item, need in (
        (weapon, least),
        *(
            ((totals.shield, combat.minimum_strength(totals.shield)),)
            if totals.shield is not None
            else ()
        ),
    ):
        if need is not None and strength < need:
            lines.append(
                problem(
                    f"{escape(item.name)} needs Strength {need:+d}; "
                    f"{escape(character.name)} has {strength:+d} (DE p. 400)."
                )
            )
    if totals.ability is not None and not any(
        a.name == totals.ability and a.xp > 0 for a in character.abilities
    ):
        lines.append(
            f"[dim]No score in {escape(totals.ability)}: used untrained, with "
            "three more botch dice"
            + (" (not for a crossbow)" if totals.ability == combat.CROSSBOW else "")
            + ".[/]"
        )
    skill = scores.ability_level(character, totals.ability) if totals.ability else 0
    types = equipment.damage_types(weapon)
    lines.append(
        f"[dim]{equipment.damage_levels(weapon)} damage level(s)"
        + (f", damage {types}" if types else "")
        + ". If a botch or an odd use may break it: stress die "
        f"{equipment.stress_check_bonus(weapon, skill):+d} against "
        f"{equipment.STRESS_EASE} (City & Guild p. 77); in the optional Clash "
        f"of Weapons, stress die {skill:+d} against "
        f"{equipment.breakage_ease(weapon)} (Lords of Men p. 138).[/]"
    )
    if weapon.make == equipment.SHODDY:
        lines.append(
            "[dim]Shoddy: destroyed the first time it fails a stress check.[/]"
        )
    riding = combat.mounted(character, weapon)
    if riding is not None:
        charge = (
            f"; charging, Attack {riding.charge:+d} (the horse spends the "
            "Fatigue level)"
            if riding.charge is not None
            else ""
        )
        attack = "n/a" if riding.attack is None else f"{riding.attack:+d}"
        lines.append(
            f"Mounted (Ride +{riding.ride}): Attack {attack}   Defence "
            f"{riding.defence:+d}{charge}."
        )
    if weapon.gear_id == combat.LANCE:
        lines.append(
            "[dim]A lance is wielded from horseback: on foot these totals are a "
            "Long Spear's.[/]"
        )
    counted = combat.counted_text(totals)
    if counted:
        lines.append(f"[dim]Counted: {escape(counted)}.[/]")
    if totals.ability is None:
        lines.append(
            "[dim]Typed in by hand, so no Combat Ability is counted: choose it "
            "from the weapon catalog to add one.[/]"
        )
    else:
        lines.append(f"[dim]Combat Ability: {escape(totals.ability)}.[/]")
    return "\n".join(lines)


def faith_score_text(character: Character, saga: Saga | None = None) -> str:
    """The True Faith Score, with the Magic Resistance it gives (x10, or
    the Dominion option's where that is more)."""
    score = character.background.true_faith_score
    resistance = penetration.faith_magic_resistance(character, saga)
    if score <= 0 and not resistance:
        return str(score)
    return f"{score} (Magic Resistance {resistance})"


def size_text(character: Character) -> str:
    """The character's Size, with its base and Virtues when they differ."""
    breakdown = derived.size(character)
    total = int(breakdown.total)
    if len(breakdown.lines) == 1:
        return str(total)
    base = int(breakdown.lines[0].amount or 0)
    rest = ", ".join(f"{line.label} {line.amount:+g}" for line in breakdown.lines[1:])
    return f"{total} (base {base}, {rest})"


def recovery_lines(saga: Saga | None, character: Character) -> list[str]:
    """What the wounds carry beyond their counts (each one's source and
    stable-roll bonus, bruises, magical aid) and the Recovery Total for an
    injury and for anything healed with Medicine (DE p. 405)."""
    found = recovery.states(character.wounds)
    lines: list[str] = []
    marked = [
        f"{s.severity.title()}"
        + (f" ({s.source}" if s.source != recovery.INJURY else " (")
        + (f", +{s.bonus}" if s.bonus else "")
        + ")"
        for s in found
        if s.source != recovery.INJURY or s.bonus
    ]
    if marked:
        lines.append("Wounds: " + ", ".join(m.replace("(, ", "(") for m in marked))
    bruises = character.wounds.bruises
    if bruises:
        lines.append(
            "Bruises: " + ", ".join(f"{n} {k.title()}" for k, n in bruises.items() if n)
        )
    lines += [disease.describe(d) for d in character.wounds.diseases]
    modifiers = disease.condition_lines(saga, character)
    if modifiers:
        lines.append(
            "Recovery Modifiers: "
            + ", ".join(f"{line.label} {line.amount:+g}" for line in modifiers)
        )
    if not found:
        return lines
    sources = {s.source == recovery.INJURY for s in found}
    for injury in sorted(sources, reverse=True):
        state = WoundState("light", recovery.INJURY if injury else "disease")
        total = recovery.total(saga, character, state)
        terms = ", ".join(
            f"{escape(line.label)} {line.amount:+g}" for line in total.lines
        )
        what = "Injuries" if injury else "Disease, poison, deprivation"
        lines.append(f"Recovery ({what}): {int(total.total)} + stress die ({terms})")
    return lines


def character_wounds_text(character: Character, saga: Saga | None = None) -> str:
    """A character's Health column: Soak and Encumbrance worked out, the
    Wound Penalty, the wounds as typed, and their recovery."""
    soak = derived.soak(character)
    load = derived.carried_load(character.inventory)
    burden = derived.burden(load)
    strength = character.characteristics.strength
    encumbrance = derived.encumbrance(load, strength)
    enc_terms = f"Load {load}, Burden {burden}"
    walk = derived.walking_pace(character)
    carry, lift, drag = equipment.carrying(character)
    if strength > 0 and burden:
        enc_terms += f", Str {strength:+d}"
    lines = [
        f"Soak: {int(soak.total)} ({derived.terms(soak)})",
        f"Encumbrance: {encumbrance} ({enc_terms})",
        f"Moves: {walk} paces a round walking, {2 * walk} hurrying, {4 * walk} running",
        f"Carries: Load {carry} (about {carry * equipment.POUNDS_PER_LOAD} lb); "
        f"lifts {lift}, drags {drag}",
        f"Pushing hard: {travel.forced_march(character)} miles a day on foot, "
        f"{travel.forced_ride(character)} riding (Grogs p. 51)",
        "Wound Penalty: "
        f"{derived.wound_penalty(character.wounds, character.virtues_flaws):+d}",
        "",
        wounds_text(character.wounds),
    ]
    extra = recovery_lines(saga, character)
    if extra:
        lines += ["", *extra]
    return "\n".join(lines)


def character_fatigue_text(character: Character) -> str:
    """A character's Fatigue with its penalty, the combined penalty, and
    the Damage Table for the character's Size."""
    level = character.fatigue_level
    fatigue = derived.fatigue_penalty(level, character.virtues_flaws)
    wounds = derived.wound_penalty(character.wounds, character.virtues_flaws)
    size = int(derived.size(character).total)
    bands = [
        f"{name} {low}+" if high is None else f"{name} {low}-{high}"
        for name, low, high in derived.wound_ranges(size)
    ]
    return "\n".join(
        [
            f"Fatigue Level: {level.title()} ({fatigue:+d})"
            + (
                f", {character.long_term_fatigue} long-term"
                if character.long_term_fatigue
                else ""
            ),
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
    """A research goal's row: its name, kind, points toward its
    target, and what waits on it."""
    extras = []
    if goal.reached:
        extras.append("reached")
    if goal.pending_magnitude:
        extras.append(f"Discovery to stabilize ({goal.pending_magnitude})")
    if goal.insights:
        extras.append(f"{goal.insights} insight(s) to invent")
    tail = f"  [dim]{'; '.join(extras)}[/]" if extras else ""
    return f"{escape(goal.name)} ({goal.kind}): {research.target_text(goal)}" + tail


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
        f"{research.target_text(goal)}" + (" (reached)" if goal.reached else ""),
        f"Stage: {research.stage(goal).value}.",
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
    if goal.pending_magnitude and goal.retry_season:
        lines.append(
            "Its stabilization failed: try again in "
            f"{goal.retry_season} {goal.retry_year}, or the Discovery is lost."
        )
    if goal.discovered_from:
        lines.append(
            "Already gave a Discovery (each gives one): "
            + escape(", ".join(goal.discovered_from))
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
