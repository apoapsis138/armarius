"""Using a base covenant template (rules.base_covenants) on a covenant:
its Power Level and Build Points, and its books and vis as placeholders
for the troupe to choose the subjects and Arts of."""

from __future__ import annotations

from . import books as bk
from .models import Covenant, Possession, Saga, new_instance_id
from .rules.base_covenants import (
    ABILITY_SUMMA,
    ART_SUMMA,
    TRACTATUS,
    VIS_SOURCE,
    VIS_STOCK,
    BaseCovenant,
    placeholders,
)


def summary(base: BaseCovenant) -> str:
    """One line: what the template buys."""
    parts = [
        f"{len(base.art_summae)} Art summae",
        f"{len(base.ability_summae)} Ability summae",
        f"{len(base.tractatus)} tractatus",
        f"{base.lab_text_levels} levels of Lab Texts",
        f"{base.vis_pawns} pawns of vis a year",
    ]
    if base.vis_stock:
        parts.append(f"{base.vis_stock} pawns in store")
    if base.enchanted_levels:
        parts.append(f"{base.enchanted_levels} levels of enchanted items")
    return ", ".join(parts)


def _pawns(total: int, count: int) -> list[int]:
    """`total` pawns shared out over `count` sources, as evenly as can be."""
    base, extra = divmod(total, count)
    return [base + (1 if i < extra else 0) for i in range(count)]


def apply(saga: Saga, covenant: Covenant, base: BaseCovenant) -> None:
    """Use `base` for the covenant: its Power Level and Build Points, and
    its books and vis as placeholders (any placeholders an earlier template
    left unfilled are removed first; what the user chose stays)."""
    books, vis = placeholders(saga, covenant)
    for book in books:
        saga.books.remove(book)
    for possession in vis:
        covenant.possessions.remove(possession)
    covenant.base_covenant = base.key
    covenant.power_level = base.power_level
    covenant.build_points_budget = base.build_points

    def add(name: str, kind: str, level: int | None, quality: int) -> None:
        book = bk.add_book(saga, name, kind)
        book.owner_kind, book.owner_id = "covenant", covenant.id
        book.level, book.quality = level, quality

    for level, quality in base.art_summae:
        add(ART_SUMMA, "Art Summa", level, quality)
    for level, quality in base.ability_summae:
        add(ABILITY_SUMMA, "Ability Summa", level, quality)
    for quality in base.tractatus:
        add(TRACTATUS, "Tractatus", None, quality)
    for pawns in _pawns(base.vis_pawns, base.vis_sources):
        covenant.possessions.append(
            Possession(
                id=new_instance_id(), kind="vis_source", name=VIS_SOURCE, pawns=pawns
            )
        )
    if base.vis_stock:
        covenant.possessions.append(
            Possession(
                id=new_instance_id(),
                kind="vis_store",
                name=VIS_STOCK,
                pawns=base.vis_stock,
                location_kind="covenant",
                location_id=covenant.id,
            )
        )
