"""The season form's fields for reinventing the Lesser Elixir -- no UI in
here: the special ingredient added, its Shape and Material bonus, whether
the alchemist devised it himself, and the Art of the dose's vis; it also
shows the season form's "Vis from" choice (PAYS_VIS). The rules and their
pages are rules.tmre_alchemy's (The Mysteries Revised Edition pp. 42-43);
the season is rules.season_work.alchemy's."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..form_spec import ChoiceReads, DialogField
from ..models import SeasonPlan
from ..rules.season_work import alchemy as aw

ActivityIs = Callable[..., Callable[[dict[str, Any]], bool]]

#: The seasons that pay vis, from the pool the form's "Vis from" names.
PAYS_VIS = (aw.REINVENT_ELIXIR,)


def fields(plan: SeasonPlan | None, activity_is: ActivityIs) -> list[DialogField]:
    """The ingredient added, and the dose's vis."""
    ours = plan is not None and plan.activity == aw.REINVENT_ELIXIR
    shown = activity_is(aw.REINVENT_ELIXIR)
    return [
        DialogField(
            "elixir_ingredient",
            "Ingredient added",
            "text",
            plan.title if plan and ours else "",
            placeholder="e.g. bloodstone",
            show_if=shown,
        ),
        DialogField(
            "elixir_bonus",
            "Its Shape and Material bonus",
            "optint",
            plan.book_level if plan and ours else None,
            show_if=shown,
            hint="Fitting the potion's form and function (Creo, Corpus, "
            "longevity, healing) or the alchemist's own magic; no ingredient "
            "counts above Magic Theory (TMRE p. 42).",
        ),
        DialogField(
            "elixir_devised",
            "He devised it himself (Vulgar Alchemy)",
            "check",
            bool(plan.devised) if plan and ours else False,
            show_if=shown,
            hint="Its Elixir Points are doubled.",
        ),
        DialogField(
            "elixir_vis",
            "The dose's vis",
            "select",
            (plan.vis_art if plan and ours else "") or "Vim",
            options=[(art, art) for art in aw.DOSE_ARTS],
            show_if=shown,
            hint="A dose of his Longevity Ritual: a pawn for every five years "
            "of his age (DE p. 261).",
        ),
    ]


#: The plan's fields this season sets from the form (as _SEASON_READS).
READS: ChoiceReads = (
    (
        (aw.REINVENT_ELIXIR,),
        lambda v: {
            "title": (v.get("elixir_ingredient") or "").strip(),
            "book_level": v.get("elixir_bonus"),
            "devised": bool(v.get("elixir_devised")),
            "vis_art": v.get("elixir_vis") or "Vim",
        },
    ),
)
