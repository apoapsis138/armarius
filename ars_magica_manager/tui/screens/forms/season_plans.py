"""Planning a season on the terminal: the Plan Season form, a grog's
Yearly Update (their fields and the plan they build are in the core's
season_forms.py) and a magus's research goals."""

from __future__ import annotations

from dataclasses import replace
from functools import partial
from typing import Any

from .... import catalog, season_forms, sourcebooks
from ....form_spec import DialogField
from ....markup import escape
from ....models import Breakthrough, Character, GrogYear, Saga, SeasonPlan
from ....rules import creation_characteristics, experiment
from ....season_forms import study_fields as _study_fields
from ..fields import FieldsDialog
from ..pickers import VirtueFlawPickerScreen

__all__ = ["_study_fields"]


def _vf_picker(saga: Saga, character: Character, side: str) -> Any:
    """The catalog picker for the season form's Virtue and Flaw fields."""

    def picker(_current: Any) -> VirtueFlawPickerScreen:
        books = sourcebooks.saga_books(saga)
        return VirtueFlawPickerScreen(
            character.virtues_flaws,
            side=side,
            chooser=catalog.VirtueFlawChooser.for_character(character, books),
            own_abilities=[a.name for a in character.abilities],
            refusal=partial(creation_characteristics.virtue_refusal, saga, character),
        )

    return picker


def _grog_year_dialog(
    character: Character, existing: GrogYear | None
) -> FieldsDialog[GrogYear]:
    """A grog's yearly update (season_forms.grog_year_fields)."""
    dialog = FieldsDialog(
        season_forms.grog_year_title(character),
        season_forms.grog_year_fields(character, existing),
        build=season_forms.grog_year_from,
    )
    dialog.help_id = "grog-year"
    return dialog


#: What reaching a research goal grants (Breakthrough.grant_kind).
GRANT_KINDS = [
    ("An Ability (the points become its xp)", "Ability"),
    ("A Virtue", "Virtue"),
    ("A new parameter (the troupe records it)", "Parameter"),
]


def _breakthrough_dialog(existing: Breakthrough | None) -> FieldsDialog[Breakthrough]:
    """A magus's original research goal: what it
    is, the kind of Breakthrough sought (Minor, Major, Hermetic; its target
    follows, and the storyguide may type a secret one), and what reaching it
    grants."""
    virtues = sorted(
        (d for d in catalog.load_virtue_flaw_catalog() if d.type == "Virtue"),
        key=lambda d: d.name,
    )
    grant_kind = existing.grant_kind if existing else ""

    def grant(kind: str) -> str:
        return existing.grant if existing and grant_kind == kind else ""

    def build(values: dict[str, Any]) -> Breakthrough:
        kind = values.get("grant_kind") or ""
        made = replace(existing) if existing else Breakthrough(name="")
        made.name = values["name"]
        made.description = values.get("description") or ""
        made.kind = values["kind"]
        made.target = values["target"]
        made.points = values.get("points") or 0
        made.grant_kind = kind
        made.grant = values.get(f"grant_{kind.lower()}") or "" if kind else ""
        made.reached = made.reached and made.points >= made.target
        return made

    def problem(values: dict[str, Any]) -> str | None:
        if (values.get("target") or 0) < 1:
            return "The target is at least 1 point."
        if (values.get("points") or 0) < 0:
            return "The points gained can't be negative."
        return None

    return FieldsDialog(
        "Add Research Goal" if existing is None else "Edit Research Goal",
        [
            DialogField(
                "name",
                "Goal",
                "text",
                existing.name if existing else "",
                required=True,
                placeholder="e.g. Penetrating the Aegis",
            ),
            DialogField(
                "description",
                "What it is",
                "area",
                existing.description if existing else "",
            ),
            DialogField(
                "kind",
                "Breakthrough",
                "select",
                existing.kind if existing else "Minor",
                options=[
                    (f"{kind} ({points} points)", kind)
                    for kind, points in experiment.KINDS.items()
                ],
                required=True,
                fills=lambda values: {
                    "target": experiment.KINDS.get(values.get("kind") or "", 30)
                },
            ),
            DialogField(
                "target",
                "Target",
                "int",
                existing.target if existing else experiment.KINDS["Minor"],
                hint="The storyguide may set a secret target.",
            ),
            DialogField(
                "points",
                "Points so far",
                "int",
                existing.points if existing else 0,
            ),
            DialogField(
                "grant_kind",
                "Reaching it grants",
                "select",
                grant_kind or None,
                options=GRANT_KINDS,
                allow_blank=True,
                placeholder="(the troupe decides)",
            ),
            DialogField(
                "grant_ability",
                "Ability",
                "text",
                grant("Ability"),
                show_if=lambda values: values.get("grant_kind") == "Ability",
            ),
            DialogField(
                "grant_virtue",
                "Virtue",
                "select",
                grant("Virtue") or None,
                options=[(escape(d.name), d.id) for d in virtues],
                allow_blank=True,
                show_if=lambda values: values.get("grant_kind") == "Virtue",
            ),
            DialogField(
                "grant_parameter",
                "Parameter",
                "text",
                grant("Parameter"),
                show_if=lambda values: values.get("grant_kind") == "Parameter",
            ),
        ],
        save_label="Add" if existing is None else "Save",
        build=build,
        validate=problem,
    )


def _season_plan_dialog(
    saga: Saga, character: Character, existing: SeasonPlan | None
) -> FieldsDialog[SeasonPlan]:
    """Plan `character`'s current season (season_forms.season_plan_fields):
    the line above Save shows what the season will give, worked out as
    the form is filled in."""
    dialog = FieldsDialog(
        season_forms.season_plan_title(saga, character),
        season_forms.season_plan_fields(
            saga, character, existing, vf_picker=_vf_picker
        ),
        validate=lambda values: season_forms.season_plan_problem(
            saga, character, values, existing
        ),
        live=lambda values: season_forms.season_plan_live(
            saga, character, values, existing
        ),
        build=lambda values: season_forms.season_plan_from(
            saga, character, values, existing
        ),
    )
    dialog.help_id = "plan-season"
    return dialog
