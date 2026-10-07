"""Base covenant templates: the three sets of starting resources the book
offers (Weak, Medium, Powerful), as ready-made Build Point spends.

A template sets the covenant's Power Level and Build Points and fills it
with placeholders: books with their level and quality but no subject, and
vis sources and stocks with their pawns but no Art. The troupe chooses
those, "based on the interests of the player character magi". Lab Texts
and enchanted items only exist once a spell or an item is named, so the
template gives them as an allowance of levels (template_allowances), which
the Resources step shows against what has been chosen.

Rules: Ars Magica Definitive Edition, Chapter Six: Covenants, Base Covenant
Resources.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from . import books as bk
from . import enchanted_devices as ed
from .models import Book, Covenant, Possession, Saga, new_instance_id

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Base Covenant "
    "Resources (https://www.redcap.org/page/Ars_Magica_Definitive_Edition,"
    "_Chapter_Six:_Covenants#Base_Covenant_Resources)"
)

#: The names of a template's placeholders, which say what is still to choose.
ART_SUMMA = "Art Summa (Art to choose)"
ABILITY_SUMMA = "Ability Summa (Ability to choose)"
TRACTATUS = "Tractatus (subject to choose)"
VIS_SOURCE = "Vis source (Art to choose)"
VIS_STOCK = "Vis stock (Art to choose)"
PLACEHOLDER_NAMES = (ART_SUMMA, ABILITY_SUMMA, TRACTATUS, VIS_SOURCE, VIS_STOCK)


@dataclass(frozen=True)
class BaseCovenant:
    """One of the book's base covenants."""

    key: str
    name: str
    power_level: str
    build_points: int
    #: (level, quality) of each Art and Ability summa.
    art_summae: tuple[tuple[int, int], ...]
    ability_summae: tuple[tuple[int, int], ...]
    #: Each tractatus's quality.
    tractatus: tuple[int, ...]
    lab_text_levels: int
    #: How many vis sources and their pawns a year in all.
    vis_sources: int
    vis_pawns: int
    vis_stock: int
    enchanted_levels: int
    #: What the book also says about it, shown when choosing.
    notes: tuple[str, ...] = field(default=())


def _times(count: int, entry: tuple[int, int]) -> tuple[tuple[int, int], ...]:
    return (entry,) * count


BASE_COVENANTS: tuple[BaseCovenant, ...] = (
    BaseCovenant(
        key="weak",
        name="Weak Covenant",
        power_level="Low",
        build_points=200,
        art_summae=((15, 12), (12, 12), (6, 21)),
        ability_summae=((4, 10),),
        tractatus=(11, 10, 10, 9),
        lab_text_levels=200,
        vis_sources=1,
        vis_pawns=4,
        vis_stock=0,
        enchanted_levels=0,
        notes=(
            "Lab Texts: none over level 25.",
            "Suits a Spring covenant, or the resources a Winter covenant can reach.",
        ),
    ),
    BaseCovenant(
        key="medium",
        name="Medium Covenant",
        power_level="Medium",
        build_points=800,
        art_summae=(*_times(3, (16, 15)), *_times(5, (6, 21))),
        ability_summae=((5, 20), *_times(2, (6, 15))),
        tractatus=(11, 11, 10, 10, 10, 10, 9),
        lab_text_levels=1000,
        vis_sources=3,
        vis_pawns=20,
        vis_stock=100,
        enchanted_levels=200,
        notes=(
            "Lab Texts: none over level 40.",
            "Vis: each source a different Art; the stocks may all be one Art.",
            "Enchanted items: highest effect level 40; at least 100 levels on "
            "lesser devices with effects of level 20 or lower.",
            "Suits a covenant in early Summer, or what young magi can reach in "
            "an Autumn covenant.",
        ),
    ),
    BaseCovenant(
        key="powerful",
        name="Powerful Covenant",
        power_level="High",
        build_points=2000,
        art_summae=(
            (20, 11),
            (18, 13),
            *_times(5, (16, 15)),
            *_times(10, (6, 21)),
        ),
        ability_summae=(*_times(3, (6, 17)), *_times(3, (5, 20))),
        tractatus=(11,) * 12 + (10,) * 9 + (9,) * 9,
        lab_text_levels=2500,
        vis_sources=5,
        vis_pawns=50,
        vis_stock=250,
        enchanted_levels=500,
        notes=(
            "Art summae: at least one in each Art.",
            "Vis: each source a different Art.",
            "Enchanted items: at least one effect over level 30; at least 100 "
            "levels on lesser devices with effects of level 20 or lower.",
            "Suits a covenant in high Summer, a relatively weak Autumn "
            "covenant, or what young magi can reach in a very powerful Autumn "
            "covenant.",
        ),
    ),
)
BASE_BY_KEY = {base.key: base for base in BASE_COVENANTS}


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


def placeholders(saga: Saga, covenant: Covenant) -> tuple[list[Book], list[Possession]]:
    """The template placeholders still waiting for their subject or Art."""
    books = [
        b
        for b in bk.books_owned_by(saga, "covenant", covenant.id)
        if b.name in PLACEHOLDER_NAMES and not (b.art or b.ability)
    ]
    vis = [p for p in covenant.possessions if p.name in PLACEHOLDER_NAMES and not p.art]
    return books, vis


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


@dataclass(frozen=True)
class Allowance:
    """Levels a template gives that only exist once named: how many, and
    how many the covenant has chosen so far."""

    what: str
    levels: int
    chosen: int


def allowances(saga: Saga, covenant: Covenant) -> list[Allowance]:
    """The covenant's template's Lab Text and enchanted item levels against
    what it has (none without a template)."""
    base = BASE_BY_KEY.get(covenant.base_covenant)
    if base is None:
        return []
    library = bk.books_owned_by(saga, "covenant", covenant.id)
    lab_texts = bk.pool(library, "Lab Text", saga).levels
    found = [Allowance("Lab Texts", base.lab_text_levels, lab_texts)]
    if base.enchanted_levels:
        levels = sum(
            ed.modified_level(device, effect)
            for device in ed.held_by(saga, "covenant", covenant.id)
            for effect in device.effects
        )
        found.append(Allowance("Enchanted items", base.enchanted_levels, levels))
    return found
