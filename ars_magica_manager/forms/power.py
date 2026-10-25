"""A character's supernatural powers (rules.powers): the Powers section's
rows and details, and the form that adds or edits one, with its inspector
saying what the power costs and what its Virtue has left. Both front-ends
draw them.
"""

from __future__ import annotations

from typing import Any

from ..arts import FORMS, TECHNIQUES
from ..commands import Form, SectionOps, delete
from ..form_spec import DialogField, pairs
from ..markup import escape, problem
from ..models import Character, CharacterPower, Saga
from ..rules import enchantment, powers
from ..sections import POWERS_SECTION
from ..tables import Table


def title(character: Character) -> str:
    return f"Powers ({len(character.powers)})"


def _figures(character: Character, power: CharacterPower) -> str:
    """ "Init +1, 1 Fatigue, Pen 5" (and a Ritual Power's Confidence)."""
    parts = [
        f"Init {powers.initiative(character, power):+d}",
        f"{powers.fatigue(power)} Fatigue",
    ]
    if powers.confidence(power):
        parts.append(f"{powers.confidence(power)} Confidence")
    parts.append(f"Pen {power.penetration}")
    return ", ".join(parts)


def table(character: Character) -> Table:
    """The Powers section's rows: name, Virtue, Arts and level, figures."""
    return Table(
        ["Power", "Virtue", "Arts, level", "Init, Fatigue, Penetration"],
        [
            [
                escape(p.name or "(unnamed)"),
                p.virtue,
                f"{p.technique[:2]}{p.form[:2]} {p.level}".strip(),
                _figures(character, p),
            ]
            for p in character.powers
        ],
        markup=True,
    )


def rows(character: Character) -> list[tuple[int | None, str]]:
    """The same as a terminal list's rows: (index, row)."""
    if not character.powers:
        return [
            (
                None,
                "[dim]No powers: a Greater, Lesser, Personal, Ritual or Focus Power Virtue grants them.[/]",
            )
        ]
    return [
        (
            n,
            f"{escape(p.name or '(unnamed)')} [dim]({p.virtue})[/]  "
            f"{p.technique} {p.form} {p.level}  ·  {_figures(character, p)}",
        )
        for n, p in enumerate(character.powers)
    ]


def held_items(saga: Saga, character: Character) -> list[tuple[str, list[int], str]]:
    """The character's devices as rules.powers.item_problems reads them."""
    return [
        (d.granted_by, [enchantment.modified_level(d, e) for e in d.effects], d.type)
        for d in saga.enchanted_devices
        if d.holder_kind == "character" and d.holder_id == character.id
    ]


def budget_lines(character: Character, saga: Saga | None = None) -> list[str]:
    """Each Virtue's levels used of those it gives (in red, from
    rules.powers, where its rules are broken, the items a Virtue gives
    included when the saga is known)."""
    broken = powers.problems(character)
    if saga is not None:
        broken += powers.item_problems(character, held_items(saga, character))
    lines = [
        f"{b.kind.name}: {b.used} of {b.given} "
        + ("points" if b.kind.name == "Focus Power" else "levels")
        + f" (DE p. {b.kind.page})"
        for b in powers.budgets(character)
        if b.given and not b.over
    ]
    return lines + [problem(escape(x)) for x in broken]


def info(character: Character, index: int | None, saga: Saga | None = None) -> str:
    """The details panel: the chosen power in full, then the budgets."""
    lines: list[str] = []
    if index is not None and 0 <= index < len(character.powers):
        p = character.powers[index]
        kind = powers.kind_of(p)
        lines += [
            f"[b]{escape(p.name or '(unnamed)')}[/]  [dim]{p.virtue}, DE p. {kind.page}[/]",
            f"{p.technique} {p.form} {p.level}"
            + (f"  ·  R: {escape(p.range)}" if p.range else "")
            + (f"  D: {escape(p.duration)}" if p.duration else "")
            + (f"  T: {escape(p.target)}" if p.target else "")
            + ("  ·  constant" if p.constant else ""),
            _figures(character, p),
        ]
        if p.description:
            lines.append(escape(p.description))
        lines.append("")
    return "\n".join(lines + budget_lines(character)) or "[dim]No powers.[/]"


def fields(existing: CharacterPower | None) -> list[DialogField]:
    p = existing or CharacterPower()
    return [
        DialogField(
            "name",
            "Name",
            "text",
            p.name,
            required=True,
            placeholder="e.g. Wings of the Owl",
        ),
        DialogField(
            "virtue",
            "Granted by",
            "select",
            p.virtue,
            options=pairs(tuple(powers.KINDS)),
            required=True,
        ),
        DialogField(
            "technique",
            "Technique",
            "select",
            p.technique or None,
            options=pairs(TECHNIQUES),
        ),
        DialogField("form", "Form", "select", p.form or None, options=pairs(FORMS)),
        DialogField(
            "level",
            "Level",
            "int",
            p.level,
            hint="As a Hermetic spell's (a Focus Power's greatest effect).",
        ),
        DialogField(
            "penetration",
            "Penetration",
            "int",
            p.penetration,
            hint="Bought level for level (a Focus Power: a point each); 0 otherwise.",
        ),
        DialogField("range", "Range", "text", p.range, placeholder="e.g. Personal"),
        DialogField("duration", "Duration", "text", p.duration, placeholder="e.g. Sun"),
        DialogField(
            "target", "Target", "text", p.target, placeholder="e.g. Individual"
        ),
        DialogField(
            "constant",
            "Constant",
            "check",
            p.constant,
            hint="A Personal Power must be this or Range Personal (DE p. 102).",
        ),
        DialogField(
            "description",
            "What it does",
            "text",
            p.description,
            placeholder="A Focus Power's field, or the effect",
        ),
    ]


def _made(values: dict[str, Any], existing: CharacterPower | None) -> CharacterPower:
    made = CharacterPower(
        values.get("name") or "",
        values.get("virtue") or "Lesser Power",
        values.get("technique") or "",
        values.get("form") or "",
        max(0, int(values.get("level") or 0)),
        max(0, int(values.get("penetration") or 0)),
        values.get("range") or "",
        values.get("duration") or "",
        values.get("target") or "",
        bool(values.get("constant")),
        values.get("description") or "",
    )
    if existing is not None:
        made.id = existing.id
    return made


def live(character: Character, index: int | None) -> Any:
    """The inspector: the power's Initiative, Fatigue and Penetration, and
    what its Virtue has left once it is counted."""

    def inspect(values: dict[str, Any]) -> str:
        current = character.powers[index] if index is not None else None
        draft = _made(values, current)
        kind = powers.kind_of(draft)
        trial = Character(
            id=character.id,
            name=character.name,
            type=character.type,
            characteristics=character.characteristics,
            virtues_flaws=character.virtues_flaws,
            powers=[
                draft if index is not None and n == index else p
                for n, p in enumerate(character.powers)
            ]
            + ([draft] if index is None else []),
        )
        lines = [
            f"[b]{escape(draft.name or 'This power')}[/]  [$label]{kind.name}, DE p. {kind.page}[/]",
            f"[i]Initiative Quickness {kind.initiative(powers.magnitude(draft.level)):+d}: "
            f"{powers.initiative(character, draft):+d}; "
            f"{powers.fatigue(draft)} Fatigue level(s) a use"
            + (
                f"; {powers.confidence(draft)} Confidence Point(s)"
                if powers.confidence(draft)
                else ""
            )
            + f"; Penetration {draft.penetration}.[/]",
        ]
        lines += budget_lines(trial)
        return "\n".join(lines)

    return inspect


def ops(character: Character) -> SectionOps:
    """Add, Edit and Delete on the Powers section; a row is the power's
    index."""

    def form(index: int | None) -> Form:
        existing = character.powers[index] if index is not None else None

        def apply(values: dict[str, Any]) -> None:
            made = _made(values, existing)
            if index is None:
                character.powers.append(made)
            else:
                character.powers[index] = made

        return Form(
            "Add a Power" if index is None else "Edit a Power",
            lambda: fields(existing),
            apply,
            live=live(character, index),
            save_label="Add" if index is None else "Save",
            help_id=POWERS_SECTION,
            inspector="The Power",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            character.powers, index, character.powers[index].name or "the power"
        ),
        rows=lambda: [p.name for p in character.powers],
    )
