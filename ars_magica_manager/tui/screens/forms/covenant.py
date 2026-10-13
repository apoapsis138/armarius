"""Forms for a covenant's records that the terminal draws its own way:
Improve Income and Buy a Specialist. The rest (inhabitants, possessions,
vis and income sources, the covenant's own details) are the core's
(inhabitant_forms.py, possession_forms.py, covenant_forms.py), imported
here under the names the terminal uses."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .... import economics as eco
from .... import inhabitants as inh
from .... import possessions as pos
from .... import sheet_text as st
from ....covenant_forms import covenant_fields as _covenant_fields
from ....form_spec import DialogField, pairs
from ....inhabitant_forms import inhabitant_fields as _inhabitant_fields
from ....markup import escape
from ....models import (
    CRAFT_FIELDS,
    INCOME_EFFECTS,
    Ability,
    IncomeSource,
)
from ....possession_forms import contested_fields as _contested_fields
from ....possession_forms import possession_fields as _possession_fields
from ....possession_forms import possession_live
from ..fields import FieldsDialog
from ..pickers import AbilityPickerScreen
from ..prompts import ConfirmScreen

__all__ = [
    "_buy_specialist_dialog",
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


def _bought_ability(value: Any) -> tuple[str, str]:
    """The (name, category) of a Buy a Specialist form's Ability: an
    Ability from the picker, or a name."""
    if isinstance(value, Ability):
        return value.name, value.category
    name = str(value or "")
    definition = st.ability_definition(name)
    return name, definition.category if definition else ""


def _buy_specialist_dialog(
    books: frozenset[str] | None = None,
) -> FieldsDialog[tuple[str, dict[str, Any]]]:
    """Someone bought with Build Points for a new covenant: an NPC defined
    by the Ability they serve with, from the Ability picker. A teacher costs
    Communication + Teaching + the highest Ability taught; anyone else their
    score. Which covenfolk category they join follows from the Ability
    (inhabitants.bought_kind): a Craft makes a craftsperson, a Martial
    Ability the turb. Builds (kind, an Inhabitant's fields)."""

    def teacher(values: dict[str, Any]) -> bool:
        return bool(values.get("teacher"))

    def kind(values: dict[str, Any]) -> str:
        name, category = _bought_ability(values.get("linked_ability"))
        return inh.bought_kind(name, category, teacher=teacher(values))

    def cost(values: dict[str, Any]) -> int:
        total = values.get("specialist_score") or 0
        if teacher(values):
            total += (values.get("teacher_communication") or 0) + (
                values.get("teacher_teaching") or 0
            )
        return total

    def live(values: dict[str, Any]) -> str:
        if not values.get("linked_ability"):
            return f"Costs {cost(values)} Build Points"
        return (
            f"Joins the {inh.KIND_TITLES[kind(values)]}. "
            f"Costs {cost(values)} Build Points"
        )

    def problem(values: dict[str, Any]) -> str | None:
        if not values.get("linked_ability"):
            return "Choose the Ability they serve the covenant with."
        if values["specialist_score"] < 0:
            return "The score can't be negative."
        return None

    def build(values: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        which = kind(values)
        name, _ = _bought_ability(values["linked_ability"])
        is_teacher = values.pop("teacher")
        rare = values.pop("rare", False)
        field = values.pop("field_of_work", None) or "None"
        values["linked_ability"] = name
        if not is_teacher:
            values["teacher_communication"] = None
            values["teacher_teaching"] = None
        else:
            values["role"] = "Teacher"
        if which == "craftsperson":
            values["rare"] = bool(rare)
            values["field_of_work"] = field
            values["skill_value"] = values["specialist_score"]
        return which, values

    def craft(values: dict[str, Any]) -> bool:
        return kind(values) == "craftsperson"

    def picker(current: Any) -> AbilityPickerScreen:
        return AbilityPickerScreen(books=books, ask_details=False)

    return FieldsDialog(
        "Buy a Specialist",
        [
            DialogField("name", "Name", "text", "", required=True),
            DialogField("teacher", "A teacher", "check", False),
            DialogField(
                "linked_ability",
                "Ability used for the covenant",
                "picker",
                None,
                placeholder="(choose an Ability)",
                picker=picker,
                display=lambda value: _bought_ability(value)[0],
                hint="A teacher: the highest Ability taught.",
            ),
            DialogField("specialist_score", "Its score", "int", 1),
            DialogField("rare", "A rare craft", "check", False, show_if=craft),
            DialogField(
                "field_of_work",
                "Saves money on",
                "select",
                "None",
                options=pairs(CRAFT_FIELDS),
                show_if=craft,
            ),
            DialogField(
                "teacher_communication", "Communication", "int", 0, show_if=teacher
            ),
            DialogField("teacher_teaching", "Teaching", "int", 1, show_if=teacher),
            DialogField("year_born", "Year Born", "optint", None),
        ],
        validate=problem,
        live=live,
        save_label="Buy",
        build=build,
    )
