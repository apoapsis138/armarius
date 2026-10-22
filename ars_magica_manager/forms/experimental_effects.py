"""The experimental effects a creation keeps (a spell, an instilled effect,
a bond power), as a list field any form can carry, independent of how it
is drawn: each entry added or edited by its own form.

An entry whose Range, Duration or Target is new or changed gives it to
the creation when the form is saved (keep); its level never changes.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from ..commands import Form, picked
from ..form_spec import DialogField, ListEditor, attr, pairs
from ..markup import escape
from ..models import (
    EXPERIMENTAL_KINDS,
    SPELL_DURATIONS,
    SPELL_RANGES,
    SPELL_TARGETS,
    ExperimentalEffect,
)
from ..rules import experiment as ex

KEY = "experimental_effects"
_KINDS = {
    "side": "Side effect",
    "modified": "Modified effect",
    "special": "The creation changed (special result)",
}
_PARAMETERS = (
    ("range", "Range", SPELL_RANGES),
    ("duration", "Duration", SPELL_DURATIONS),
    ("target", "Target", SPELL_TARGETS),
)


def row(effect: ExperimentalEffect) -> str:
    """An experimental effect as its list shows it (plain text)."""
    return ex.describe(effect)


def effect_fields(existing: ExperimentalEffect | None) -> list[DialogField]:
    """One experimental effect: what the chart gave, what it is, whether it
    is a fatal flaw, and any new Range, Duration, Target or potency."""
    kind = attr(existing, "kind", "side")
    fields = [
        DialogField(
            "kind",
            "Kind",
            "select",
            kind,
            options=[(_KINDS[k], k) for k in EXPERIMENTAL_KINDS],
        ),
        DialogField(
            "result",
            "What the chart gave",
            "text",
            attr(existing, "result", ""),
            placeholder="e.g. minor flaw",
        ),
        DialogField(
            "description",
            "What it is",
            "text",
            attr(existing, "description", ""),
            placeholder="e.g. the spell smells of cinnamon",
        ),
        DialogField(
            "fatal",
            "A fatal flaw",
            "check",
            attr(existing, "fatal", False),
            hint="Marked on the creation's sheet.",
        ),
    ]
    for key, label, standard in _PARAMETERS:
        fields.append(
            DialogField(
                key,
                f"New {label}",
                "select",
                attr(existing, key, "") or None,
                options=pairs(standard),
                allow_blank=True,
                placeholder="(unchanged)",
            )
        )
    fields.append(
        DialogField(
            "potency",
            "Potency (steps)",
            "int",
            attr(existing, "potency", 0),
            hint="Each step is 5 points of the Lab Total behind it (1 of a "
            "Longevity Ritual's modifier): the app's reading, as the rules "
            "give no size.",
        )
    )
    return fields


def effect_from(
    values: dict[str, Any], existing: ExperimentalEffect | None
) -> ExperimentalEffect:
    """The entry the form's values make; when it was seen before, the
    season it came from and the Magic Theory then are kept."""
    return ExperimentalEffect(
        kind=values.get("kind") or "side",
        result=(values.get("result") or "").strip(),
        description=(values.get("description") or "").strip(),
        range=values.get("range") or "",
        duration=values.get("duration") or "",
        target=values.get("target") or "",
        potency=int(values.get("potency") or 0),
        fatal=bool(values.get("fatal")),
        year=attr(existing, "year", None),
        season=attr(existing, "season", ""),
        magic_theory=attr(existing, "magic_theory", None),
    )


def effect_form(existing: ExperimentalEffect | None) -> Form:
    """Add or edit one experimental effect, picked as a record."""
    return Form(
        "Add an Experimental Effect"
        if existing is None
        else "Edit an Experimental Effect",
        lambda: effect_fields(existing),
        picked(lambda values: effect_from(values, existing)),
        save_label="Add" if existing is None else "Save",
    )


def effects_field(effects: Sequence[ExperimentalEffect], name: str = "") -> DialogField:
    """The list field: the creation's experimental effects, each edited on
    its own form."""
    return DialogField(
        KEY,
        "Experimental effects",
        "picker",
        list(effects),
        display=lambda chosen: "; ".join(row(e) for e in chosen) or "(none)",
        items=ListEditor(
            row,
            effect_form,
            f"Experimental effects: {escape(name)}" if name else "Experimental effects",
        ),
        hint="What experimenting left on it, warts and all. A new Range, "
        "Duration or Target is given to it on saving; its level never changes.",
    )


def keep(made: Any, values: dict[str, Any]) -> None:
    """Save the list on `made` (a spell, an instilled effect, a bond
    power); an entry whose Range, Duration or Target is new gives it to
    `made`."""
    if KEY not in values:
        return
    before = list(made.experimental_effects)
    after = list(values[KEY])
    made.experimental_effects = after
    ex.apply_changes(made, [e for e in after if e not in before])
