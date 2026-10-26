"""What the Bestiary and a creature's sheet show, worked out from the
saga's records for either front-end: the Bestiary's facts and list, and
a creature's facts, Characteristics, combat, powers and vis, and its
whole stat block as the books print one."""

from __future__ import annotations

from .. import connections, creatures, places, references
from .. import possessions as pos
from ..forms import virtue as virtue_forms
from ..grids import Grid
from ..markup import escape
from ..models import REALMS, Creature, Saga
from ..references import Fact
from ..rules import (
    creature_build,
    divine_build,
    faerie_build,
    infernal_build,
    jinn_build,
    magic_build,
    sites,
    spirit_build,
    vis_kinds,
)
from . import character as cs

#: The Characteristics as a stat block abbreviates them, in its order.
CHARACTERISTICS: tuple[tuple[str, str], ...] = (
    ("Int", "intelligence"),
    ("Per", "perception"),
    ("Pre", "presence"),
    ("Com", "communication"),
    ("Str", "strength"),
    ("Sta", "stamina"),
    ("Dex", "dexterity"),
    ("Qik", "quickness"),
)


def characteristic_labels(creature: Creature) -> tuple[tuple[str, str], ...]:
    """Its Characteristics' abbreviations: Cun in place of Int for a
    creature with animal intelligence."""
    if not creature.cunning:
        return CHARACTERISTICS
    return (("Cun", "intelligence"), *CHARACTERISTICS[1:])


def _signed(value: int) -> str:
    return f"{value:+d}"


# -- the Bestiary --


def bestiary_title(saga: Saga) -> str:
    return f"Creatures ({len(saga.creatures)})"


def bestiary_facts(saga: Saga) -> list[Fact]:
    """How many creatures, and how many of each realm."""
    found = saga.creatures
    by_realm = [
        f"{sum(1 for c in found if c.realm == realm)} {realm}"
        for realm in REALMS
        if any(c.realm == realm for c in found)
    ]
    mundane = sum(1 for c in found if not c.realm)
    if mundane:
        by_realm.append(f"{mundane} mundane")
    placed = sum(1 for c in found if c.place_id)
    return [
        Fact("Creatures", str(len(found))),
        Fact("By realm", ", ".join(by_realm)),
        Fact("Found at a place", str(placed)),
    ]


def bestiary_grid(saga: Saga) -> Grid:
    """Every creature, by name: its Might, Size and where it is found."""
    rows = [
        [
            c.name + (" (many)" if c.many else ""),
            creatures.might_text(c),
            _signed(c.size),
            places.where_text(saga, c.place_id, c.place_level),
        ]
        for c in creatures.listed(saga)
    ]
    return Grid(
        ["Name", "Might", "Size", "Found at"],
        rows,
        list(range(len(rows))),
        "None yet: add a beast, a spirit, a faerie or a demon here.",
        caps=[28, 28, 4, 0],
    )


# -- a creature --


def subtitle(creature: Creature) -> str:
    """The line under its name: its Might, and how many there are."""
    parts = [creatures.might_text(creature)]
    if creature.many:
        parts.append(creature.how_many or "Many of a kind")
    return "  ·  ".join(parts)


def facts(saga: Saga, creature: Creature) -> list[Fact]:
    c = creature
    pool = (
        [Fact("Might Pool", f"{c.might_pool} of {c.might}")]
        if creatures.has_might(c) and c.might_pool is not None
        else []
    )
    return [
        Fact("Might", creatures.might_text(c)),
        *pool,
        *magic_vis_facts(saga, c),
        *build_facts(c),
        *infernal_facts(c),
        *faerie_role_facts(c),
        Fact("Size", _signed(c.size)),
        Fact("Season", c.season),
        *([Fact("Warping", str(c.warping_score))] if c.warping_score else []),
        *([Fact("Age", c.age)] if c.age else []),
        *([Fact("Confidence", confidence_text(c))] if confidence_text(c) else []),
        Fact("How many", c.how_many if c.many else "One"),
        Fact(
            "Found at",
            places.where_text(saga, c.place_id, c.place_level),
            references.refs(sites.place(saga, c.place_id)),
        ),
        Fact("Detail", c.detail),
        Fact("Source", c.source),
        *connections.rules_facts(saga, c),
        *connections.links_back(saga, c),
    ]


def magic_vis_facts(saga: Saga, creature: Creature) -> list[Fact]:
    """How fast a Magic Might creature regains Might resting in the Magic
    aura where it is found (RoP: Magic p. 30)."""
    c = creature
    place = sites.place(saga, c.place_id)
    if c.realm != "Magic" or c.might <= 0 or place is None:
        return []
    aura, realm = sites.aura_at(place, c.place_level)
    recovery = vis_kinds.recovery_text(aura, c.might) if realm == "Magic" else ""
    return [Fact("Might recovery", recovery)] if recovery else []


def build_facts(creature: Creature) -> list[Fact]:
    """A magic creature's Quality points, and what doesn't fit the
    creature rules."""
    found: list[Fact] = []
    budget = creature_build.quality_budget(creature)
    if budget is not None:
        over = f", {-budget.left} over" if budget.left < 0 else ""
        found.append(
            Fact(
                "Qualities",
                f"{budget.spent} of {budget.from_might + budget.from_inferiorities} "
                f"points (Might {budget.from_might} + Inferiorities "
                f"{budget.from_inferiorities}{over})",
            )
        )
    problems = creature_build.problems(creature)
    if problems:
        found.append(Fact("Check", " ".join(problems)))
    faerie = faerie_build.problems(creature)
    if faerie:
        found.append(Fact("Faerie design", " ".join(faerie)))
    infernal = infernal_build.problems(creature)
    if infernal:
        found.append(Fact("Infernal design", " ".join(infernal)))
    if infernal_build.order_of(creature) is not None:
        demon = infernal_build.notes(creature)
        found.append(Fact("As a demon", "; ".join(demon) + "."))
    spirit = spirit_build.problems(creature)
    if spirit:
        found.append(Fact("Spirit design", " ".join(spirit)))
    spirit_notes = spirit_build.notes(creature)
    if spirit_notes:
        found.append(Fact("As a spirit", "; ".join(spirit_notes) + "."))
    jinni = jinn_build.problems(creature)
    if jinni:
        found.append(Fact("Jinni design", " ".join(jinni)))
    jinni_notes = jinn_build.notes(creature)
    if jinni_notes:
        found.append(Fact("As a jinni", "; ".join(jinni_notes) + "."))
    magic = magic_build.problems(creature)
    if magic:
        found.append(Fact("Magic design", " ".join(magic)))
    magic_notes = magic_build.notes(creature)
    if magic_notes:
        found.append(Fact("Magic being", "; ".join(magic_notes) + "."))
    # Divine beings and angels (RoP: The Divine pp. 16-26).
    divine = divine_build.problems(creature)
    if divine:
        found.append(Fact("Divine design", " ".join(divine)))
    angel = divine_build.notes(creature)
    if angel:
        found.append(Fact("As an angel", "; ".join(angel) + "."))
    return found


def infernal_facts(creature: Creature) -> list[Fact]:
    """A demon's Order, Hierarchy and Weakness, those it has."""
    c = creature
    found = [
        ("Order", c.order),
        ("Hierarchy", "" if c.hierarchy is None else str(c.hierarchy)),
        ("Weakness", c.weakness),
    ]
    return [Fact(label, value) for label, value in found if value]


def faerie_role_facts(creature: Creature) -> list[Fact]:
    """A faerie's role and the story it wants (RoP: Faerie pp. 140-142)."""
    text = faerie_build.role_text(creature)
    return [Fact("Role", text)] if text else []


def confidence_text(creature: Creature) -> str:
    """ "2 (5)", its Confidence Score and Points, or "" with none."""
    c = creature
    if c.confidence_score is None:
        return ""
    return f"{c.confidence_score} ({c.confidence_points})"


def characteristics_text(creature: Creature) -> str:
    """ "Int 0, Per 0, Pre +2, ..." as a stat block gives them."""
    ch = creature.characteristics
    return ", ".join(
        f"{short} {getattr(ch, name):+d}".replace("+0", "0")
        for short, name in characteristic_labels(creature)
    )


def fatigue_levels_text(creature: Creature) -> str:
    if not creature.tires:
        return "none: it never tires"
    return creature.fatigue_levels or "as a person's"


def combat_facts(creature: Creature) -> list[Fact]:
    encumbrance = (
        [Fact("Encumbrance", creature.encumbrance)] if creature.encumbrance else []
    )
    return [
        Fact("Soak", _signed(creature.soak)),
        Fact("Fatigue levels", fatigue_levels_text(creature)),
        *encumbrance,
    ]


def vf_rows(creature: Creature) -> list[tuple[int | None, str]]:
    """Its Virtues, Flaws, Qualities and Inferiorities, in the order taken."""
    rows: list[tuple[int | None, str]] = [
        (index, escape(virtue_forms.vf_name(creature, index)))
        for index in range(len(creature.virtues_flaws))
    ]
    return rows or [(None, "[$label]None yet.[/]")]


def ability_table(creature: Creature) -> list[cs.AbilityRow]:
    return cs.abilities_table(creature.abilities, creature.virtues_flaws)


def attacks_grid(creature: Creature) -> Grid:
    rows = [
        [
            a.name or "(unnamed)",
            pos.signed(a.init),
            pos.signed(a.attack),
            pos.signed(a.defense),
            pos.signed(a.damage),
        ]
        for a in creature.attacks
    ]
    return Grid(
        ["Attack", "Init", "Atk", "Def", "Dam"],
        rows,
        list(range(len(rows))),
        "No attacks yet.",
    )


def wound_track(creature: Creature) -> list[cs.WoundBand]:
    return cs.damage_table(creature.wounds, creature.size)


def wounds_text(creature: Creature) -> str:
    """ "-1 (1-7), -3 (8-14), -5 (15-21), Incapacitated (22-28), Dead
    (29+)", its Wound Penalties as a stat block gives them."""
    if not creature.can_be_wounded:
        return "none: it cannot be wounded"
    parts = []
    for band in wound_track(creature):
        span = f"{band.low}+" if band.high is None else f"{band.low}-{band.high}"
        name = str(band.penalty) if band.penalty else band.name
        parts.append(f"{name} ({span})")
    return ", ".join(parts)


def fatigue_track(creature: Creature) -> list[tuple[str, int, bool]]:
    return cs.fatigue_levels(creature.fatigue_level, creature.virtues_flaws)


def power_rtd(reach: str, duration: str, target: str) -> str:
    """ "R: Per, D: Sun, T: Ind", leaving out what isn't entered."""
    parts = [
        f"{key}: {value}"
        for key, value in (("R", reach), ("D", duration), ("T", target))
        if value
    ]
    return ", ".join(parts)


def powers_grid(creature: Creature) -> Grid:
    """Its powers: what each costs, its Init and Form, and its
    Penetration (worked out)."""
    rows = [
        [
            p.name or "(unnamed)",
            f"{p.might_cost} pts",
            _signed(p.init),
            p.form,
            power_rtd(p.range, p.duration, p.target),
            str(creatures.penetration(creature, p)),
        ]
        for p in creature.powers
    ]
    return Grid(
        ["Power", "Cost", "Init", "Form", "Range, Duration, Target", "Pen"],
        rows,
        list(range(len(rows))),
        "No powers yet.",
        caps=[26, 7, 4, 9, 30, 0],
    )


def power_text(creature: Creature, index: int) -> str:
    """One power as markup for a details panel: its line, then what it
    does."""
    if not 0 <= index < len(creature.powers):
        return ""
    p = creature.powers[index]
    figures = [f"{p.might_cost} points", f"Init {_signed(p.init)}"]
    if p.form:
        figures.append(p.form)
    figures.append(f"Penetration {creatures.penetration(creature, p)}")
    lines = [f"[b]{escape(p.name)}[/], {escape(', '.join(figures))}"]
    rtd = power_rtd(p.range, p.duration, p.target)
    if rtd:
        lines.append(escape(rtd))
    if p.description:
        lines.append(escape(p.description))
    if p.level is not None:
        lines.append(f"[$label]Level {p.level} effect.[/]")
    return "\n".join(lines)


def vis_rows(creature: Creature) -> list[tuple[int | None, str]]:
    rows: list[tuple[int | None, str]] = [
        (index, escape(creatures.vis_text(v))) for index, v in enumerate(creature.vis)
    ]
    return rows or [(None, "[$label]No vis in its body.[/]")]


def _stat_block_head(creature: Creature) -> list[tuple[str, str]]:
    """A stat block's lines down to its Confidence: its Might, Order,
    Characteristics, Size, season and age."""
    c = creature
    lines: list[tuple[str, str]] = []
    if creatures.has_might(c):
        lines.append(
            (
                f"{c.realm} Might",
                f"{c.might}" + (f" ({c.might_form})" if c.might_form else ""),
            )
        )
    if c.order:
        lines.append(("Order", c.order))
    lines.append(("Characteristics", characteristics_text(c)))
    lines.append(("Size", _signed(c.size)))
    if c.season:
        lines.append(("Season", c.season))
    if c.age:
        lines.append(("Age", c.age))
    if c.warping_score:
        lines.append(("Warping Score", str(c.warping_score)))
    if confidence_text(c):
        lines.append(("Confidence Score", confidence_text(c)))
    return lines


def stat_block(saga: Saga, creature: Creature) -> list[tuple[str, str]]:
    """The creature as the books print a stat block: each heading and
    what follows it, leaving out what isn't entered."""
    c = creature
    lines = _stat_block_head(c)
    if c.virtues_flaws:
        names = [virtue_forms.vf_name(c, i) for i in range(len(c.virtues_flaws))]
        lines.append(("Virtues and Flaws", "; ".join(names)))
    if c.personality_traits:
        lines.append(
            (
                "Personality Traits",
                ", ".join(f"{t.name} {_signed(t.score)}" for t in c.personality_traits),
            )
        )
    if c.reputations:
        lines.append(
            (
                "Reputations",
                ", ".join(f"{t.name} {t.score}" for t in c.reputations),
            )
        )
    if c.hierarchy is not None:
        lines.append(("Hierarchy", str(c.hierarchy)))
    for a in c.attacks:
        lines.append(
            (
                a.name or "Attack",
                f"Init {pos.signed(a.init)}, Attack {pos.signed(a.attack)}, "
                f"Defense {pos.signed(a.defense)}, Damage {pos.signed(a.damage)}",
            )
        )
    lines.append(("Soak", _signed(c.soak)))
    lines.append(("Wound Penalties", wounds_text(c)))
    if c.fatigue_levels or not c.tires:
        lines.append(("Fatigue Levels", fatigue_levels_text(c)))
    if c.abilities:
        lines.append(
            (
                "Abilities",
                ", ".join(
                    f"{a.name} {a.level}" + (f" ({a.specialty})" if a.specialty else "")
                    for a in c.abilities
                ),
            )
        )
    for p in c.powers:
        rtd = power_rtd(p.range, p.duration, p.target)
        words = [f"{p.might_cost} points", f"Init {_signed(p.init)}"]
        if p.form:
            words.append(p.form)
        words.append(f"Pen {creatures.penetration(c, p)}")
        text = ", ".join(words) + (f"; {rtd}" if rtd else "")
        if p.description:
            text += f". {p.description}"
        lines.append((f"Power: {p.name}", text))
    if c.equipment:
        lines.append(("Equipment", c.equipment))
    if c.encumbrance:
        lines.append(("Encumbrance", c.encumbrance))
    if c.weakness:
        lines.append(("Weakness", c.weakness))
    if c.vis:
        lines.append(("Vis", "; ".join(creatures.vis_text(v) for v in c.vis)))
    if c.appearance:
        lines.append(("Appearance", c.appearance))
    where = places.where_text(saga, c.place_id, c.place_level)
    if where:
        lines.append(("Found at", where))
    return lines


def stat_block_text(saga: Saga, creature: Creature | None) -> str:
    """The stat block as markup, for a details panel."""
    if creature is None:
        return "[$label]Choose a creature to see its stat block.[/]"
    head = f"[b]{escape(creature.name)}[/]"
    body = [
        f"[$label]{escape(label)}:[/] {escape(value)}"
        for label, value in stat_block(saga, creature)
    ]
    return "\n".join([head, *body])
