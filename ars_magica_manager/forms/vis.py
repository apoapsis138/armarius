"""A store of raw vis, independent of how it is drawn: the form for one
Art's pawns and the store's Add, Edit and Delete (commands.SectionOps).

A character and a laboratory both keep raw vis as a pool of Art (stored
lower-case) -> pawns; the ops act on the pool, whoever holds it. Its rows
are the Arts in alphabetical order, so a row's index is its Art's place
in sorted(pool).
"""

from __future__ import annotations

from typing import Any

from ..arts import ARTS
from ..commands import Confirm, Form, SectionOps
from ..form_spec import DialogField
from ..markup import escape
from ..models import add_raw_vis, replace_raw_vis


def raw_vis_fields(existing: tuple[str, int] | None = None) -> list[DialogField]:
    """An Art (stored lower-case) and a number of pawns."""
    return [
        DialogField(
            "art",
            "Art",
            "select",
            existing[0] if existing else None,
            options=[(art, art.lower()) for art in ARTS],
            required=True,
            allow_blank=True,
            placeholder="(choose an Art)",
        ),
        DialogField("pawns", "Pawns", "int", existing[1] if existing else 1),
    ]


def raw_vis_from(values: dict[str, Any]) -> tuple[str, int]:
    """The (art, pawns) a raw vis form saved."""
    return values["art"], values["pawns"]


def raw_vis_rows(pool: dict[str, int]) -> list[str]:
    """The pool's rows, "Art: N pawn(s)", in alphabetical order."""
    return [f"{art.title()}: {pool[art]} pawn(s)" for art in sorted(pool)]


def raw_vis_ops(pool: dict[str, int]) -> SectionOps:
    """Add, Edit and Delete for the raw vis `pool`. Adding an Art already
    held adds to its pawns; editing one onto another Art held merges
    them."""

    def add() -> Form:
        def apply(values: dict[str, Any]) -> None:
            add_raw_vis(pool, *raw_vis_from(values))

        return Form("Add Raw Vis", raw_vis_fields, apply, save_label="Add")

    def edit(index: int) -> Form:
        old_art = sorted(pool)[index]

        def apply(values: dict[str, Any]) -> None:
            replace_raw_vis(pool, old_art, *raw_vis_from(values))

        return Form(
            "Edit Raw Vis", lambda: raw_vis_fields((old_art, pool[old_art])), apply
        )

    def remove(index: int) -> Confirm:
        art = sorted(pool)[index]

        def apply() -> None:
            del pool[art]

        return Confirm(f"Delete {escape(art.title())} vis?", apply)

    return SectionOps(
        add=add, edit=edit, remove=remove, rows=lambda: raw_vis_rows(pool)
    )
