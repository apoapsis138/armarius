"""An Initiation's Script written out as its components (The Mysteries
Revised Edition pp. 15-16), as a list field the Plan Season form carries,
independent of how it is drawn: each component added or edited on its own
form. The rules are rules.mysteries'; which components a plan offers is
rules.supplement_work.components_for's (the House's own for a Verditius).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from ..commands import Form, picked
from ..form_spec import DialogField, ListEditor, attr
from ..markup import escape
from ..models import ScriptPart
from ..rules import mysteries

KEY = "script_components"
TITLE = "Script components"


def _by_key(table: Sequence[mysteries.Component]) -> dict[str, mysteries.Component]:
    return {c.key: c for c in table if c.key}


def row(table: Sequence[mysteries.Component]) -> Callable[[ScriptPart], str]:
    """How the list shows a component (plain text): "Specific Quest +3
    (slay the wyrm)"."""
    by_key = _by_key(table)

    def shown(part: ScriptPart) -> str:
        component = by_key.get(part.key)
        if component is None:
            return f"{part.key} (not offered)"
        text = f"{component.name} {mysteries.component_bonus(component, part):+d}"
        return f"{text} ({part.note})" if part.note else text

    return shown


def part_fields(
    table: Sequence[mysteries.Component], existing: ScriptPart | None
) -> list[DialogField]:
    """One component: which, its size when the troupe sets it, and what it
    is."""
    offered = mysteries.listed_components(table)
    sized = {c.key for c in offered if c.sized}
    key = attr(existing, "key", "") or offered[0].key

    def fills(values: dict[str, Any]) -> dict[str, Any]:
        component = _by_key(table).get(str(values.get("component") or ""))
        return {"bonus": component.bonus} if component is not None else {}

    return [
        DialogField(
            "component",
            "Component",
            "select",
            key,
            options=[(f"{c.name} ({c.bonus:+d})", c.key) for c in offered],
            fills=fills,
            hint="An Ordeal's bonus comes from the plan's Ordeal: it isn't listed.",
        ),
        DialogField(
            "bonus",
            "Its bonus",
            "int",
            attr(existing, "bonus", _by_key(table)[key].bonus),
            show_if=lambda values: values.get("component") in sized,
            hint="A great sacrifice is +3 to +6; the sympathy of the rite -5 to "
            "+5, usually 0 to +3, agreed with the storyguide (TMRE pp. 15-16).",
        ),
        DialogField(
            "note",
            "What it is",
            "text",
            attr(existing, "note", ""),
            placeholder="e.g. the head of the Minotaur",
        ),
    ]


def part_from(
    values: dict[str, Any], table: Sequence[mysteries.Component]
) -> ScriptPart:
    key = str(values.get("component") or "")
    component = _by_key(table).get(key)
    bonus = int(values.get("bonus") or 0)
    if component is not None and not component.sized:
        bonus = component.bonus
    return ScriptPart(key, bonus, str(values.get("note") or "").strip())


def part_form(
    table: Sequence[mysteries.Component],
) -> Callable[[ScriptPart | None], Form]:
    """Add or edit one component, picked as a record."""

    def form(existing: ScriptPart | None) -> Form:
        return Form(
            "Add a Script Component" if existing is None else "Edit a Script Component",
            lambda: part_fields(table, existing),
            picked(lambda values: part_from(values, table)),
            save_label="Add" if existing is None else "Save",
        )

    return form


def components_field(
    table: Sequence[mysteries.Component],
    parts: Sequence[ScriptPart],
    show_if: Callable[[dict[str, Any]], bool] | None = None,
    name: str = "",
) -> DialogField:
    """The list field: the Script's components, each on its own form."""
    shown = row(table)
    return DialogField(
        KEY,
        TITLE,
        "picker",
        list(parts),
        display=lambda chosen: "; ".join(shown(p) for p in chosen) or "(none)",
        items=ListEditor(
            shown,
            part_form(table),
            f"{TITLE}: {escape(name)}" if name else TITLE,
        ),
        show_if=show_if,
        hint="A Hermetic Script written out: its bonus is their sum, with the "
        "Ordeal's, and the Script bonus above is added to them (TMRE pp. 15-16).",
    )
