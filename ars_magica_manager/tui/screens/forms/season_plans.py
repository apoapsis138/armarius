"""Planning a season on the terminal: the Plan Season form, a grog's
Yearly Update (their fields and the plan they build are in the core's
season_forms.py) and a magus's research goals."""

from __future__ import annotations

from functools import partial
from typing import Any

from .... import sourcebooks
from ....forms import character as character_forms
from ....forms import season as season_forms
from ....forms.season import study_fields as _study_fields
from ....models import Breakthrough, Character, GrogYear, Saga, SeasonPlan
from ....rules import creation_characteristics
from ....rules.vf_eligibility import VirtueFlawChooser
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
            chooser=VirtueFlawChooser.for_character(character, books),
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


def _breakthrough_dialog(existing: Breakthrough | None) -> FieldsDialog[Breakthrough]:
    """A magus's Arcane Discovery goal (character_forms.research_goal_fields):
    what it is, the kind of Breakthrough sought (its target follows, and the
    storyguide may type a secret one), and what reaching it grants; a new
    goal may start from an integration breakthrough the books name."""
    return FieldsDialog(
        "Add Research Goal" if existing is None else "Edit Research Goal",
        character_forms.research_goal_fields(existing),
        save_label="Add" if existing is None else "Save",
        build=partial(character_forms.research_goal_from, existing),
        validate=character_forms.research_goal_problem,
    )


def _season_plan_dialog(
    saga: Saga,
    character: Character,
    existing: SeasonPlan | None,
    when: season_forms.When | None = None,
) -> FieldsDialog[dict[str, Any]]:
    """Plan `character`'s season `when` (the current one by default;
    season_forms.season_plan_fields): the line above Save shows what the
    season will give, worked out as the form is filled in. It returns the
    values, for season_forms.save_season."""
    dialog = FieldsDialog(
        season_forms.season_plan_title(saga, character, when),
        season_forms.season_plan_fields(
            saga, character, existing, vf_picker=_vf_picker, when=when
        ),
        validate=lambda values: season_forms.season_plan_problem(
            saga, character, values, existing, when
        ),
        live=lambda values: season_forms.season_plan_live(
            saga, character, values, existing, when
        ),
        build=dict,
    )
    dialog.help_id = "plan-season"
    return dialog
