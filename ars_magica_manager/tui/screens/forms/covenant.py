"""Forms for a covenant's records that the terminal draws its own way:
Improve Income and Buy a Specialist. The rest (inhabitants, possessions,
vis and income sources, the covenant's own details) are the core's
(inhabitant_forms.py, possession_forms.py, covenant_forms.py), imported
here under the names the terminal uses."""

from __future__ import annotations

from collections.abc import Collection, Sequence
from typing import Any

from .... import possessions as pos
from ....forms.covenant import covenant_fields as _covenant_fields
from ....forms.inhabitant import inhabitant_fields as _inhabitant_fields
from ....forms.possession import contested_fields as _contested_fields
from ....forms.possession import possession_fields as _possession_fields
from ....forms.possession import possession_live
from ..fields import FieldsDialog

__all__ = [
    "_contested_fields",
    "_covenant_fields",
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
    books: Collection[str] | None = None,
) -> FieldsDialog[dict[str, Any]]:
    """The add/edit form for one kind of possession (a covenant's, a
    character's Personal Gear, or -- `natural` -- a familiar's Natural
    Weapons). A weapon or armor form shows the chosen book entry in its live
    line. A Raw Vis Store's asks where it is kept: one of `places`
    (vis.location_options), `place` to start with. A weapon is chosen
    from the `books` in play (sourcebooks.saga_books; None: every book)."""
    return FieldsDialog(
        title,
        _possession_fields(
            kind, entry, natural=natural, places=places, place=place, books=books
        ),
        validate=pos.form_problem,
        live=possession_live(kind),
    )
