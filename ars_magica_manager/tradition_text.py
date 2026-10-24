"""A tradition chapter's rules text: how the character casts (each of
the tradition's casting rules, with the character's Casting Scores in
their home aura), the Magical Defenses they have, and the tradition's
seasons (Opening, initiation, advancement and its own work), its bonds,
Warping and pools. Like the other domain modules it returns markup, which
both front-ends show."""

from __future__ import annotations

from dataclasses import dataclass

from .markup import escape
from .models import CastingRule, Character, Saga, TraditionDef
from .rules import hedge_casting as hc
from .rules import hedge_effects as he
from .rules import hedge_warping as hw
from .rules import tradition_seasons as ts
from .rules.realms import home_aura
from .tables import Table

#: Characteristic abbreviations, as the books print them.
_ABBREVIATIONS = {
    "Intelligence": "Int",
    "Perception": "Per",
    "Strength": "Str",
    "Stamina": "Sta",
    "Presence": "Pre",
    "Communication": "Com",
    "Dexterity": "Dex",
    "Quickness": "Qik",
}


def _die_words(rule: CastingRule) -> str:
    if rule.lab or rule.die == "none":
        return "no die"
    return f"a {rule.die} die"


def total_words(rule: CastingRule) -> str:
    """How a rule's total is made and what it must reach."""
    if rule.lab:
        made = "Lab Total, no die"
    elif rule.divisor > 1:
        made = f"(Casting Score + {_die_words(rule)}) / {rule.divisor}"
    else:
        made = f"Casting Score + {_die_words(rule)}"
    against = rule.against or "level"
    words = f"{made}, against the {against}"
    if rule.failure_margin:
        words += (
            f"; up to {rule.failure_margin} short it still works, for a "
            "Fatigue level, and further short it fails"
        )
    return words + "."


def vis_words(rule: CastingRule) -> str:
    if rule.vis_cap == "none":
        return ""
    cap = {
        "arts": "each Art's score",
        "score": "the score used",
        "forms": "the sum of the Forms",
    }[rule.vis_cap]
    words = f"+{rule.vis_per_pawn} a pawn, up to {cap}"
    if rule.vis:
        words += f"; {rule.vis}"
    if not rule.ungifted_vis:
        words += " (Gifted only)"
    return words + "."


def _grid(
    character: Character,
    tradition: TraditionDef,
    rule: CastingRule,
    aura: int,
    realm: str,
) -> list[str]:
    """An art_pair rule's Casting Scores, Techniques down, Forms across."""
    rows = [t for t in hc.techniques(tradition, rule) if hc.holds(character, t)]
    cols = [f for f in hc.forms(tradition, rule) if hc.holds(character, f)]
    if not rows or not cols:
        return ["[dim]Needs a Technique and a Form.[/]"]
    width = max(len(hc.short_name(f)) for f in cols) + 2
    label = max(len(hc.short_name(t)) for t in rows) + 2
    lines = [" " * label + "".join(f"{hc.short_name(f):>{width}}" for f in cols)]
    for technique in rows:
        cells = []
        for form in cols:
            score = hc.casting_score(
                character,
                tradition,
                rule,
                (technique, form),
                aura=aura,
                aura_realm=realm,
            )
            cells.append(f"{int(score.total):>{width}}")
        lines.append(f"{escape(hc.short_name(technique)):<{label}}" + "".join(cells))
    return lines


def _listed(
    character: Character,
    tradition: TraditionDef,
    rule: CastingRule,
    aura: int,
    realm: str,
) -> list[str]:
    """An ability or rune rule's Casting Scores, one per score."""
    found = hc.castings(character, tradition, rule)
    if not found:
        needs = " or ".join(hc.rule_scores(tradition, rule)) or "its Abilities"
        return [f"[dim]Needs {escape(needs)}.[/]"]
    cells: list[tuple[str, str]] = []
    for casting in found:
        score = hc.casting_score(
            character, tradition, rule, casting.uses, aura=aura, aura_realm=realm
        )
        characteristic = hc.characteristic_for(rule, casting.uses)
        tag = f" ({_ABBREVIATIONS.get(characteristic, characteristic)})"
        if rule.kind == "rune":
            tag = ""
        level = hc.equivalent_level(rule, hc.score(character, casting.uses[0]))
        extra = f"  as level {level}" if level is not None else ""
        cells.append((f"{escape(casting.label)}{tag}", f"{int(score.total)}{extra}"))
    if rule.kind == "rune":
        # Twenty-four runes read better four to a line.
        lines = []
        for start in range(0, len(cells), 4):
            row = cells[start : start + 4]
            lines.append("".join(f"{name:<10}{value:>3}   " for name, value in row))
        return lines
    name_width = max(len(name) for name, _ in cells) + 2
    return [f"{name:<{name_width}}{value}" for name, value in cells]


def _shared_terms(
    character: Character,
    tradition: TraditionDef,
    rule: CastingRule,
    aura: int,
    realm: str,
) -> str:
    """The terms every score of the rule adds besides its Arts."""
    parts = []
    if rule.characteristic and not rule.characteristics:
        value = getattr(character.characteristics, rule.characteristic.lower(), 0)
        parts.append(f"{rule.characteristic} {value:+d}")
    elif rule.characteristics:
        parts.append("its Characteristic")
    for name in rule.adds:
        parts.append(f"{escape(name)} {hc.score(character, name):+d}")
    if rule.best_of:
        best = max(rule.best_of, key=lambda n: hc.score(character, n))
        parts.append(f"{escape(best)} {hc.score(character, best):+d}")
    parts.append(f"aura ({realm} {aura}) {hc.aura_modifier(tradition, aura, realm):+d}")
    applies = "lab" if rule.lab else "casting"
    for _, being in hw.bound(character, tradition.id):
        if being.applies_to == applies and being.bonus:
            parts.append(f"{escape(being.name)} (bound) {being.bonus:+d}")
    return ", ".join(parts)


@dataclass(frozen=True)
class CastingPart:
    """One block of the Casting section: a title, a table padded into
    columns (fixed-width type; "" for none) and the notes under it."""

    title: str
    table: str
    notes: str


def rule_part(
    saga: Saga, character: Character, tradition: TraditionDef, rule: CastingRule
) -> CastingPart:
    aura, realm = home_aura(saga, character)
    draw = _grid if rule.kind == "art_pair" else _listed
    table = draw(character, tradition, rule, aura, realm)
    lines = [
        "Each adds: " + _shared_terms(character, tradition, rule, aura, realm) + ".",
        "Total: " + total_words(rule),
    ]
    if rule.fatigue:
        lines.append(f"Fatigue: {escape(rule.fatigue)}.")
    vis = vis_words(rule)
    if vis:
        lines.append("Vis: " + escape(vis))
    if rule.penetrates and not rule.lab:
        bonus = hc.penetration_bonus(character)
        against = "Ease Factor" if rule.against == "Ease Factor" else "level"
        lines.append(f"Penetration: Total {bonus:+d} (Penetration) - the {against}.")
    if rule.resistance:
        lines.append(f"Resisted: {escape(rule.resistance)}.")
    if rule.notes:
        lines.append(f"[dim]{escape(rule.notes)}[/]")
    return CastingPart(escape(rule.name), "\n".join(table), "\n".join(lines))


def casting_parts(
    saga: Saga, character: Character, tradition: TraditionDef
) -> list[CastingPart]:
    """Every way the tradition casts, with the character's scores, then
    its dispellings and group castings."""
    parts = [rule_part(saga, character, tradition, r) for r in tradition.casting]
    for rule in tradition.dispels:
        multiple = "" if rule.multiple == 1 else f"{rule.multiple} x "
        parts.append(
            CastingPart(
                f"{escape(rule.name)} ({escape(rule.uses)})",
                "",
                f"Needs {multiple}the effect's "
                f"{'level' if rule.total == 'level' else 'Casting Total'}"
                + (f"; {escape(rule.notes)}" if rule.notes else "")
                + ".",
            )
        )
    for group in tradition.groups:
        parts.append(CastingPart(escape(group.name), "", escape(group.notes)))
    return parts


def casting_text(saga: Saga, character: Character, tradition: TraditionDef) -> str:
    """The Casting section as one block of text (casting_parts)."""
    if not tradition.casting:
        return "[dim]The tradition has no casting totals.[/]"
    return "\n\n".join(
        "\n".join(x for x in (f"[b]{part.title}[/]", part.table, part.notes) if x)
        for part in casting_parts(saga, character, tradition)
    )


def defenses_text(character: Character, tradition: TraditionDef) -> str:
    """The Magical Defenses the character has from the tradition."""
    if not tradition.defenses:
        return "[dim]The tradition gives no Magical Defenses.[/]"
    held = {vf.vf_id for vf in character.virtues_flaws}
    if hc.NO_DEFENSES in held:
        return "No Magical Defenses (the Flaw)."
    rows = hc.magical_defenses(character, tradition)
    if not rows:
        return "[dim]None yet: each comes with one of the tradition's Arts or Abilities.[/]"
    lines = [
        f"[b]{escape(row.kind)}[/] {row.bonus:+d} from {escape(row.source)}, "
        f"against {escape(row.against)}: {escape(row.effect)}."
        for row in rows
    ]
    if hc.GREATER_DEFENSES in held:
        lines.append("Doubled by Greater Magical Defenses.")
    lines.append(
        "[dim]Only the best one applies to an effect; never against Personal range.[/]"
    )
    return "\n".join(lines)


def _opening_lines(
    saga: Saga, character: Character, tradition: TraditionDef
) -> list[str]:
    rule = tradition.opening
    if rule is None:
        return ["[b]Opening[/] The tradition doesn't Open its students' Gift."]
    aura, realm = home_aura(saga, character)
    total = ts.opening_total(character, tradition, aura, realm)
    terms = ", ".join(
        f"{escape(line.label)} {int(line.amount or 0):+d}" for line in total.lines
    )
    lines = [
        f"[b]Opening[/] a Gifted student's Gift: a season. Opening Total "
        f"{int(total.total)} ({terms}).",
        "Against 2 x the student's Supernatural Abilities and Arts (+12 if his "
        "Gift was Opened before); with none it always works. Up to twice that "
        "he loses them; beyond it he keeps them.",
    ]
    if tradition not in ts.openable(character):
        lines.append("[dim]Only a Gifted member Opened to the tradition can Open.[/]")
    low = [
        a for a in tradition.training.opening if hc.score(character, a) < ts.COMPETENT
    ]
    if low and tradition in ts.openable(character):
        lines.append(
            f"Below {ts.COMPETENT} in {escape(', '.join(low))}: each gives the "
            "student a Flaw."
        )
    if rule.notes:
        lines.append(f"[dim]{escape(rule.notes)}[/]")
    return lines


def _initiation_lines(character: Character, tradition: TraditionDef) -> list[str]:
    rule = tradition.initiation
    if rule is None:
        return []
    lore = rule.lore or "Lore"
    lines = [
        f"[b]Initiation[/] Total: {rule.characteristic} + {escape(lore)} + the "
        f"Script's bonus, against its Ease Factor"
        + ("" if rule.self_initiation else "; no self-initiation")
        + ". A Mystagogue who doesn't have the power adds 3 to the Ease Factor "
        "for a Minor Virtue, 9 for a Major (Hedge Magic Revised Edition p. 13). "
        "As Mystagogue:"
    ]
    for script in rule.scripts:
        total = ts.initiation_total(character, tradition, script.bonus)
        who = f" ({script.who})" if script.who else ""
        lines.append(
            f"  {escape(script.name)}{who}: {total} vs {script.ease_factor}; "
            f"gains {escape(script.gains)}; Ordeal {escape(script.ordeal)}."
        )
        if script.notes:
            lines.append(f"    [dim]{escape(script.notes)}[/]")
    if rule.notes:
        lines.append(f"[dim]{escape(rule.notes)}[/]")
    return lines


def _advancement_lines(tradition: TraditionDef) -> list[str]:
    rules = tradition.advancement
    said = [
        "its Arts may be practised"
        if rules.practice_arts
        else "its Arts can't be practised",
        "studied from vis" if rules.vis_study else "not studied from vis",
    ]
    lines = ["[b]Advancement[/] " + "; ".join(said).capitalize() + "."]
    if tradition.working_seasons:
        lines.append(
            f"Works {tradition.working_seasons} seasons a year"
            + (f", {tradition.working_xp} xp a year." if tradition.working_xp else ".")
        )
    if rules.notes:
        lines.append(f"[dim]{escape(rules.notes)}[/]")
    return lines


def _activity_lines(
    saga: Saga, character: Character, tradition: TraditionDef
) -> list[str]:
    if not tradition.activities:
        return []
    aura, realm = home_aura(saga, character)
    lines = ["[b]Seasons of work[/] (planned on This Season):"]
    for activity in tradition.activities:
        line = f"  {escape(activity.label)}: {escape(activity.summary)}"
        if activity.lab_rule:
            best = ts.lab_total(
                character, tradition, activity.lab_rule, "", aura, realm
            )
            if best is not None:
                line += (
                    f" Best {escape(activity.lab_rule)}: {best[1]} ({escape(best[0])})."
                )
        lines.append(line)
    return lines


def seasons_text(saga: Saga, character: Character, tradition: TraditionDef) -> str:
    """The tradition's seasons: Opening a student, its initiations (with
    the character's Initiation Total as Mystagogue), how its Arts advance,
    and its own seasons of work."""
    parts = [
        _opening_lines(saga, character, tradition),
        _initiation_lines(character, tradition),
        _advancement_lines(tradition),
        _activity_lines(saga, character, tradition),
    ]
    return "\n\n".join("\n".join(part) for part in parts if part)


def _effect_cells(
    saga: Saga, character: Character, tradition: TraditionDef
) -> list[list[str]]:
    aura, realm = home_aura(saga, character)
    rows = []
    for _, effect in he.of_tradition(character, tradition.id):
        found = he.effect_total(character, tradition, effect, aura, realm)
        rows.append(
            [
                escape(effect.name),
                effect.kind,
                str(effect.level) if effect.level else "",
                escape(" + ".join(hc.short_name(u) for u in effect.uses)),
                escape(he.total_words(found, effect)),
            ]
        )
    return rows


def effect_table(saga: Saga, character: Character, tradition: TraditionDef) -> Table:
    """The tradition's effects and items the character has, each chosen
    by its position among them."""
    return Table(
        ["Name", "Kind", "Level", "Uses", "Total"],
        _effect_cells(saga, character, tradition),
        markup=True,
    )


def effect_rows(
    saga: Saga, character: Character, tradition: TraditionDef
) -> list[tuple[int | None, str]]:
    """The same as a list's rows: (position, row)."""
    rows = _effect_cells(saga, character, tradition)
    if not rows:
        return [(None, "[dim]None recorded.[/]")]
    return [
        (
            n,
            f"{name} ({kind}{', level ' + level if level else ''}): "
            f"{uses + '; ' if uses else ''}{total}",
        )
        for n, (name, kind, level, uses, total) in enumerate(rows)
    ]


def _bond_cells(character: Character, tradition: TraditionDef) -> list[list[str]]:
    rows = []
    for _, being in hw.bound(character, tradition.id):
        adds = (
            f"{being.bonus:+d} to {_APPLIES[being.applies_to]}"
            if being.applies_to and being.bonus
            else ""
        )
        rows.append([escape(being.name), escape(being.kind), adds])
    return rows


_APPLIES = {"casting": "casting totals", "lab": "Lab Totals", "": "nothing"}


def bond_table(character: Character, tradition: TraditionDef) -> Table:
    """The beings bound to the character by the tradition, each chosen by
    its position among them."""
    return Table(
        ["Name", "Bond", "Adds"], _bond_cells(character, tradition), markup=True
    )


def bond_rows(
    character: Character, tradition: TraditionDef
) -> list[tuple[int | None, str]]:
    """The same as a list's rows: (position, row)."""
    rows = _bond_cells(character, tradition)
    if not rows:
        return [(None, "[dim]None bound.[/]")]
    return [
        (
            n,
            name + (f" ({kind})" if kind else "") + (f": {adds}" if adds else ""),
        )
        for n, (name, kind, adds) in enumerate(rows)
    ]


def bonds_text(tradition: TraditionDef) -> str:
    """The bonds the tradition's book describes."""
    if not tradition.bonds:
        return "[dim]The tradition's book describes no bond.[/]"
    lines = []
    for bond in tradition.bonds:
        lines.append(f"[b]{escape(bond.name)}[/] {escape(bond.how)}")
        if bond.feeds:
            lines.append(f"  Adds: {escape(bond.feeds)}")
        if bond.notes:
            lines.append(f"  [dim]{escape(bond.notes)}[/]")
    return "\n".join(lines)


def warping_text(character: Character, tradition: TraditionDef) -> str:
    """The tradition's own Warping, with the character's Warping Score
    and, for an elementalist, his elemental Personality Traits. A magus
    in a tradition keeps Wizard's Twilight, with the tradition's own
    response shown after it."""
    score = character.aging.warping_score
    points = character.aging.warping_points
    lines = [f"Warping Score {score} ({points} points)."]
    rule = tradition.warping
    if character.type == "magus" or tradition.social_status == hw.HERMETIC_MAGUS:
        lines.append("A Hermetic magus: Warping and Twilight as for any magus.")
        if rule is None:
            return "\n".join(lines)
    if rule is None:
        lines.append(
            "[dim]No Twilight, and no Warping from a strong magic aura; the "
            "book gives the tradition no response of its own.[/]"
        )
        return "\n".join(lines)
    instead = " in place of Twilight" if rule.replaces_twilight else ""
    lines.append(f"[b]{escape(rule.name)}[/]{instead}.")
    if rule.trigger:
        lines.append(f"When: {escape(rule.trigger)}")
    if rule.kind == "elemental_traits":
        traits = hw.elemental_traits(character)
        if not traits:
            lines.append("No Elementalist Form held, so no elemental Trait.")
        for trait in traits:
            effect = f": {trait.effect}" if trait.effect else ""
            lines.append(
                f"  {trait.trait} {trait.value:+d} ({escape(trait.form)} "
                f"{trait.form_score}){effect}."
            )
    if rule.notes:
        lines.append(f"[dim]{escape(rule.notes)}[/]")
    return "\n".join(lines)


def pools_text(character: Character, tradition: TraditionDef) -> str:
    """The points in each of the tradition's pools, and the book's words
    on each."""
    lines = []
    for pool in tradition.pools:
        points = hw.pool_points(character, tradition, pool.name)
        lines.append(f"[b]{escape(pool.name)}[/] {points}")
        for label, words in (
            ("Fills", pool.income),
            ("Spent on", pool.costs),
            ("Cap", pool.cap),
        ):
            if words:
                lines.append(f"  {label}: {escape(words)}")
        if pool.notes:
            lines.append(f"  [dim]{escape(pool.notes)}[/]")
    return "\n".join(lines)
