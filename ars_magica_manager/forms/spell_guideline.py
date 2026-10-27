"""The spell design's Guideline picker, independent of how it is drawn:
the supplements' Hermetic spell guidelines (rules.spell_guidelines) to
take a spell's Arts and base level from, listed by Form."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..arts import FORMS, TECHNIQUES
from ..commands import Choice, Choose, Picked, not_offered
from ..markup import escape
from ..models import Saga, SpellDesign, SpellGuidelineDef
from ..rules import spell_guidelines as sg

#: The filters above the list: each guideline's Form, then its Technique.
FORM, TECHNIQUE = "Form", "Technique"
#: What the picker shows with no guideline chosen.
NONE_CHOSEN = "(none: type the base level)"


def _choice(guideline: SpellGuidelineDef) -> Choice:
    return Choice(
        escape(sg.label(guideline)),
        guideline.id,
        escape(f"{guideline.summary} ({sg.cite(guideline)})"),
        search=f"{sg.arts(guideline)} {guideline.summary}",
        facets=((FORM, guideline.form), (TECHNIQUE, guideline.technique)),
    )


def _order(guideline: SpellGuidelineDef) -> tuple[int, int, int]:
    """By Form, then Technique, then level, as the books list them."""
    return (
        FORMS.index(guideline.form),
        TECHNIQUES.index(guideline.technique),
        guideline.level,
    )


def choose_guideline(
    saga: Saga,
    current: str | None = None,
    apply: Callable[[Any], Any] = Picked,
) -> Choose:
    """The guideline a spell's design takes its Arts and base level from,
    under its Form (filter by Form or Technique); the guidelines of books
    out of play only on asking. `current` is the one chosen now."""

    def choices() -> list[Choice]:
        return [_choice(g) for g in sorted(sg.offered(saga), key=_order)]

    return Choose(
        "Base the spell on a guideline...",
        choices,
        apply,
        empty="No spell guidelines are in play.",
        others=lambda: [
            not_offered(_choice(g), "book not in play")
            for g in sorted(sg.not_offered(saga), key=_order)
        ],
        filters=(FORM, TECHNIQUE),
        help_id="invent-spell-guideline",
    )


def guideline_label(guideline_id: str | None) -> str:
    """How the Guideline field shows its value."""
    found = sg.find(guideline_id)
    return sg.label(found) if found is not None else NONE_CHOSEN


def design_guideline(design: SpellDesign | None) -> str | None:
    """The catalog guideline a design's Base effect names, if any (as
    choosing one writes it)."""
    found = sg.matching(design.base_effect) if design is not None else None
    return found.id if found is not None else None


def guideline_values(values: dict[str, Any]) -> dict[str, Any]:
    """The design fields the chosen guideline fills in (a DialogField's
    fills): nothing when the field is cleared, so typed figures stay."""
    found = sg.find(values.get("guideline"))
    return sg.design_values(found) if found is not None else {}
