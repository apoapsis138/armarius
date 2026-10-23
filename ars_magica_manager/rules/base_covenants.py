"""Base covenant templates: the three sets of starting resources the book
offers (Weak, Medium, Powerful), as ready-made Build Point spends.

A template sets the covenant's Power Level and Build Points and fills it
with placeholders: books with their level and quality but no subject, and
vis sources and stocks with their pawns but no Art. The troupe chooses
those, "based on the interests of the player character magi". Lab Texts
and enchanted items only exist once a spell or an item is named, so the
template gives them as an allowance of levels (allowances), which the
Resources step shows against what has been chosen. Using a template on a
covenant is covenant_templates.apply."""

from __future__ import annotations

from dataclasses import dataclass, field

from ..models import Book, Covenant, Possession, Saga
from . import enchantment
from . import library as book_rules

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


def placeholders(saga: Saga, covenant: Covenant) -> tuple[list[Book], list[Possession]]:
    """The template placeholders still waiting for their subject or Art."""
    books = [
        b
        for b in book_rules.books_owned_by(saga, "covenant", covenant.id)
        if b.name in PLACEHOLDER_NAMES and not (b.art or b.ability)
    ]
    vis = [p for p in covenant.possessions if p.name in PLACEHOLDER_NAMES and not p.art]
    return books, vis


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
    library = book_rules.books_owned_by(saga, "covenant", covenant.id)
    lab_texts = book_rules.pool(library, "Lab Text", saga).levels
    found = [Allowance("Lab Texts", base.lab_text_levels, lab_texts)]
    if base.enchanted_levels:
        levels = sum(
            enchantment.modified_level(device, effect)
            for device in enchantment.covenant_devices(saga, covenant.id)
            for effect in device.effects
        )
        found.append(Allowance("Enchanted items", base.enchanted_levels, levels))
    return found
