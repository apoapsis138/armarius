"""The supernatural effects a character is under all the time
(rules.warping.constant_points): the Constant Effects section's rows and
details, and the form that adds or edits one, with its inspector saying
the Warping it gives. Both front-ends draw them.
"""

from __future__ import annotations

import random
from typing import Any

from .. import seasons
from ..commands import Form, SectionOps, delete
from ..form_spec import DialogField, pairs
from ..markup import escape
from ..models import REALMS, Character, ConstantEffect, Saga
from ..rules import warping
from ..sections import CONSTANT_EFFECTS_SECTION
from ..tables import Table


def title(character: Character) -> str:
    return f"Constant Effects ({len(character.constant_effects)})"


def _kind(effect: ConstantEffect) -> str:
    """ "powerful, not made for them" and the like."""
    power = "powerful" if effect.powerful else "low power"
    made = "theirs or made for them" if effect.designed_for else "not made for them"
    return f"{power}, {made}"


def _warping(effect: ConstantEffect) -> str:
    each = warping.constant_points(effect)
    return f"{each} Warping a year" + (" (1, and 1 a season)" if each > 1 else "")


def table(character: Character) -> Table:
    """The section's rows: the effect, its realm and kind, its Warping."""
    return Table(
        ["Effect", "Realm", "Kind", "Warping"],
        [
            [escape(e.name or "(unnamed)"), e.realm, _kind(e), _warping(e)]
            for e in character.constant_effects
        ],
        markup=True,
    )


EMPTY = (
    "[dim]None: a spell or item that affects them all the time warps them "
    "each year (DE pp. 390-391).[/]"
)


def rows(character: Character) -> list[tuple[int | None, str]]:
    """The same as a terminal list's rows: (index, row)."""
    if not character.constant_effects:
        return [(None, EMPTY)]
    return [
        (
            n,
            f"{escape(e.name or '(unnamed)')} [dim]({e.realm}, {_kind(e)})[/]"
            f"  ·  {_warping(e)}",
        )
        for n, e in enumerate(character.constant_effects)
    ]


def total_line(character: Character) -> str:
    """What the constant effects give together each year."""
    total = sum(warping.constant_points(e) for e in character.constant_effects)
    if not total:
        return ""
    return f"{total} Warping Point(s) a year from constant effects, added each Winter."


def info(character: Character, index: int | None) -> str:
    """The details panel: the chosen effect in full."""
    if index is None or not 0 <= index < len(character.constant_effects):
        return EMPTY
    e = character.constant_effects[index]
    lines = [
        f"[b]{escape(e.name or '(unnamed)')}[/]  [dim]{e.realm}[/]",
        f"{_kind(e).capitalize()}: {_warping(e)} (DE p. 391).",
    ]
    if e.description:
        lines.append(escape(e.description))
    return "\n".join(lines)


def fields(existing: ConstantEffect | None) -> list[DialogField]:
    e = existing or ConstantEffect()
    return [
        DialogField(
            "name",
            "Effect",
            "text",
            e.name,
            required=True,
            placeholder="e.g. Wings of the Soaring Wind, worn as a ring",
        ),
        DialogField("realm", "Realm", "select", e.realm, options=pairs(REALMS)),
        DialogField(
            "powerful",
            "Powerful",
            "check",
            e.powerful,
            hint="Sixth magnitude or more (level 30 and up, as a Hermetic spell).",
        ),
        DialogField(
            "designed_for",
            "Cast by them or designed for them",
            "check",
            e.designed_for,
            hint="A special version of a spell invented for them, as a "
            "Longevity Ritual is.",
        ),
        DialogField(
            "description",
            "Notes",
            "text",
            e.description,
            placeholder="Where it comes from, how long it lasts",
        ),
    ]


def _made(values: dict[str, Any], existing: ConstantEffect | None) -> ConstantEffect:
    made = ConstantEffect(
        values.get("name") or "",
        values.get("realm") or "Magic",
        bool(values.get("powerful")),
        bool(values.get("designed_for")),
        values.get("description") or "",
    )
    if existing is not None:
        made.id = existing.id
    return made


def live(existing: ConstantEffect | None) -> Any:
    """The inspector: the Warping the effect gives, and when."""

    def inspect(values: dict[str, Any]) -> str:
        draft = _made(values, existing)
        lines = [
            f"[b]{escape(draft.name or 'This effect')}[/]  [$label]{draft.realm}[/]",
            f"[i]{_kind(draft).capitalize()}: {_warping(draft)}, added each "
            "Winter with the year's other Warping.[/]",
        ]
        if warping.first_point(draft) and existing is None:
            lines.append("And 1 Warping Point now, as it begins (DE p. 390).")
        lines.append(
            "[dim]Parma Magica, the Aegis of the Hearth and a familiar's bond "
            "don't warp; a Longevity Ritual is counted already.[/]"
        )
        return "\n".join(lines)

    return inspect


def ops(saga: Saga, character: Character) -> SectionOps:
    """Add, Edit and Delete on the Constant Effects section; a row is the
    effect's index. A powerful effect not made for them gives its first
    Warping Point when it is added."""

    def form(index: int | None) -> Form:
        existing = character.constant_effects[index] if index is not None else None

        def apply(values: dict[str, Any]) -> list[str] | None:
            made = _made(values, existing)
            if index is not None:
                character.constant_effects[index] = made
                return None
            character.constant_effects.append(made)
            if warping.first_point(made):
                return seasons.gain_warping(
                    saga,
                    character,
                    warping.first_point(made),
                    random.Random(),
                    realm=made.realm,
                )
            return None

        return Form(
            "Add a Constant Effect" if index is None else "Edit a Constant Effect",
            lambda: fields(existing),
            apply,
            live=live(existing),
            save_label="Add" if index is None else "Save",
            help_id=CONSTANT_EFFECTS_SECTION,
            inspector="The Effect",
        )

    return SectionOps(
        add=lambda: form(None),
        edit=form,
        remove=lambda index: delete(
            character.constant_effects,
            index,
            character.constant_effects[index].name or "the effect",
        ),
        rows=lambda: [e.name for e in character.constant_effects],
    )
