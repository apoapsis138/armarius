"""A magus's research goals as the terminal draws them, and the study
fields the season forms share (season plans themselves are the core's,
season_forms.py)."""

from __future__ import annotations

from functools import partial

from ....forms import character as character_forms
from ....forms.season import study_fields as _study_fields
from ....models import Breakthrough
from ..fields import FieldsDialog

__all__ = ["_study_fields"]


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
