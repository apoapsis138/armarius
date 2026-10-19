"""Forms for a covenant's records that the terminal draws its own way:
Improve Income and Buy a Specialist. The rest (inhabitants, possessions,
vis and income sources, the covenant's own details) are the core's
(inhabitant_forms.py, possession_forms.py, covenant_forms.py), imported
here under the names the terminal uses."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .... import economics as eco
from .... import possessions as pos
from ....form_spec import DialogField, pairs
from ....forms.covenant import covenant_fields as _covenant_fields
from ....forms.inhabitant import inhabitant_fields as _inhabitant_fields
from ....forms.possession import contested_fields as _contested_fields
from ....forms.possession import possession_fields as _possession_fields
from ....forms.possession import possession_live
from ....markup import escape
from ....models import (
    INCOME_EFFECTS,
    IncomeSource,
)
from ..fields import FieldsDialog
from ..prompts import ConfirmScreen

__all__ = [
    "_contested_fields",
    "_covenant_fields",
    "_improve_income_dialog",
    "_inhabitant_fields",
    "_possession_dialog",
    "_possession_fields",
]


def _possession_dialog(
    title: str,
    kind: str,
    entry: pos.PossessionEntry | None,
    *,
    natural: bool = False,
    places: Sequence[tuple[str, str]] = (),
    place: str = "",
) -> FieldsDialog[dict[str, Any]]:
    """The add/edit form for one kind of possession (a covenant's, a
    character's Personal Gear, or -- `natural` -- a familiar's Natural
    Weapons). A weapon or armor form shows the chosen book entry in its live
    line. A Raw Vis Store's asks where it is kept: one of `places`
    (vis.location_options), `place` to start with."""
    return FieldsDialog(
        title,
        _possession_fields(kind, entry, natural=natural, places=places, place=place),
        validate=pos.form_problem,
        live=possession_live(kind),
    )


def _improve_income_dialog(
    source: IncomeSource, current_year: int
) -> FieldsDialog[tuple[int, str]]:
    """Manually simulates a year's Income Modification (yearly advancement
    isn't automated): choosing an Effect shows the Multiplier and Projected
    Income live. Commit asks to confirm, then builds (new income, the Note
    to record)."""
    current = source.current_income

    def live(values: dict[str, Any]) -> str:
        effect = values.get("effect") or "Status Quo"
        return (
            f"Income Multiplier {eco.income_multiplier_text(effect)}. "
            f"Projected Income {eco.projected_income(current, effect)}"
        )

    def build(values: dict[str, Any]) -> tuple[int, str]:
        effect = values["effect"]
        projected = eco.projected_income(current, effect)
        note = eco.improvement_note(
            current_year, source.name, effect, current, projected
        )
        return projected, note

    def confirm(values: dict[str, Any]) -> ConfirmScreen:
        projected = eco.projected_income(current, values["effect"])
        name = escape(source.name or "this source of income")
        return ConfirmScreen(
            f"Update {name}'s income from {current} to {projected}?",
            yes_label="Update",
        )

    return FieldsDialog(
        f"Improve {escape(source.name or 'this source of income')}",
        [
            DialogField("name", "Name", "info", source.name or "(unnamed)"),
            DialogField("current", "Current Income", "info", str(current)),
            DialogField(
                "effect",
                "Annual Improvement Effect",
                "select",
                "Status Quo",
                options=pairs(INCOME_EFFECTS),
                required=True,
            ),
            # A Note is a sentence or two: shown under its label, wrapped.
            DialogField(
                "note",
                "Note",
                "info",
                "" if source.note.strip() else "(none)",
                hint=escape(source.note.strip()),
            ),
        ],
        live=live,
        save_label="Commit",
        build=build,
        confirm=confirm,
    )
