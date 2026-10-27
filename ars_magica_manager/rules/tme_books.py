"""Transforming Mythic Europe's books made by magic, and the savings a
covenant makes by replacing its costs with magic. Plain rule functions;
the season is rules.season_work.transforming's, the savings are shown on
the covenant's Economics tab (economics.py).

Copying books by magic (TME pp. 98-103):

- Rego craft magic copies a page at a time: The First Furrow Guides the
  Second lays the page's image on a blank sheet, The Copyist's Puissant
  Quill makes the ink follow it. Magic neither reads nor understands, so
  the copy is a facsimile: no language, Magic Theory or Realm Lore is
  needed to copy a text without corrupting it (p. 98).
- The Quill's Ease Factor is 9 for a book of Quality 6 or less, 12 for 7
  to 9, 15 for 10 or more (p. 100). Over a whole book the caster's Finesse
  Total, + 3 at Ease Factor 9 and - 3 at 15, gives the copy's Quality on
  the table (p. 100): 11 or more equal to the original, 9 two lower, 7
  four lower, 5 six lower, less no readable book.
- TME gives the total as Intelligence + Finesse; the Definitive Edition's
  Rego craft magic roll is Perception + Finesse (DE p. 307), and the DE
  wins, so the total here is Perception + Finesse with the Wound, Fatigue
  and Flaw penalties (rules.craft_magic.roll_base).
- A copy made by magic loses the original's resonances (resonant
  materials, clarification; p. 101) and is loose sheets until bound
  (p. 101). Binding the Mundane Codex binds it, its caster needing a
  Finesse Total of 6, and a book so bound has the sound binding's +1
  under the extended Quality rules (p. 103; the Errata, p. 84, lowers
  the device's effect to level 7, base 1, no size modifier).
- A tractatus is about 160 pages; a summa 25 pages a point of Level; a
  Lab Text about a page a level of its effect (pp. 101, 103). A mundane
  scribe copies four pages a day, and spends another tidying and
  illuminating them (p. 101).
- TME gives no rate for casting the spells page by page, so the plan says
  how many copies the season makes. A copying device (the Superb
  Scrinium, pp. 101-103) needs a separate activation of The First Furrow
  Guides the Second for each text, and of Binding the Mundane Codex to
  bind it, so its effects' uses a day cap the books it copies (3 a day
  each: 3 books a day).
- A Lab Text must be copied flawlessly or it is useless (a botched page
  corrupts it, found only when it is used): a Finesse Total of 11 copies
  a month's worth of a scribe's work (120 levels) flawlessly, 14 a
  season's (360 levels) (p. 103), and 17 a year's (1,440 levels), as Rego
  craft magic's Ease Factor rises 3 from a season's work to a year's (DE
  p. 307). Past a year's worth no book gives a figure: the troupe decides. The optional rules: Hazardous Lab
  Texts (an extra Experimentation roll, its risk modifier half the pages
  spoiled in ten, each time the copy is used) and No Magical Copying of
  Lab Texts (pp. 103-104), both saga options.
- A large library (p. 105, an insert): each subject's best summa, raised
  by the other summae as experience in its Level and by the tractatus as
  experience in its Quality, both as Arts; a book counts only within
  three points of the library's figure. Studying from it gives Quality +
  3 below its Level, Quality at or above it (for Quality more seasons).

Technological savings (TME pp. 120-121; Covenants pp. 66-69):

- A pound spent on a point of inhabitants is 10 shillings of provisions,
  4 of wages, 4 of consumables and 2 of the fabric (p. 120).
- Half to three quarters of the provisions is bread: grain made by magic
  saves 5 to 7½ shillings of every such pound (p. 120). A point of
  inhabitants eats 24 bushels a year (p. 121); a store loses a twentieth
  to a tenth a year at best, a fifth when only covered (p. 121). Fill the
  Capacious Silo makes 20,000 bushels (p. 120).
- An item replacing covenfolk saves a pound a year a magnitude of its
  effect; a Ritual spell's casting about five pounds a magnitude
  (Covenants p. 67; TME p. 120: The Instant Harvest does seven laborers'
  work -- nine at the Errata's level 45, p. 84 -- and The Elfin Baker
  replaces a baker for at least four pounds). Magic doing covenfolk's
  work is treated as laborers for cost saving (Covenants p. 67), so the
  items and Rituals save at most what laborers may: half the Provisions,
  less what the covenant's laborers already save.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from ..models import (
    BREAD_SHARES,
    GRAIN_CARE,
    Book,
    Character,
    EnchantedDevice,
    InstilledEffect,
)
from . import craft_magic
from .breakdown import Breakdown, Line
from .journeys import SEASON_DAYS
from .powers import magnitude
from .rounding import round_down

COPY_SOURCE = (
    "Transforming Mythic Europe, The Copying of a Book, pp. 98-103 (Errata p. 84); "
    "the Rego craft magic roll, Ars Magica Definitive Edition p. 307"
)
LIBRARY_SOURCE = "Transforming Mythic Europe, Rules for a Large Library, p. 105"
SAVINGS_SOURCE = (
    "Transforming Mythic Europe, Reducing Covenant Costs, pp. 120-121 (Errata "
    "pp. 84-85); Covenants, Cost Saving, Magic, p. 67"
)
SOURCE = f"{COPY_SOURCE}; {LIBRARY_SOURCE}; {SAVINGS_SOURCE}"

# -- copying books by magic ----------------------------------------------------

#: The spells that copy a page (p. 100), and the one that binds the sheets
#: (Covenants p. 97; TME p. 103).
IMAGE_SPELL = "The First Furrow Guides the Second"
QUILL_SPELL = "The Copyist's Puissant Quill"
BINDING_SPELL = "Binding the Mundane Codex"
COPY_SPELLS: tuple[str, ...] = (IMAGE_SPELL, QUILL_SPELL)

#: The Quill's Ease Factor by the original's Quality (p. 100): (the
#: highest Quality, its Ease Factor); higher still is 15.
QUILL_EASE: tuple[tuple[int, int], ...] = ((6, 9), (9, 12))
HARDEST_EASE = 15
#: The Ease Factor the table assumes (p. 100).
TABLE_EASE = 12
#: The table (p. 100): (the lowest Finesse Total, pages spoiled in ten,
#: Quality lost); below the last row, eight pages in ten spoiled and no
#: readable book.
COPY_TABLE: tuple[tuple[int, int, int], ...] = (
    (11, 0, 0),
    (9, 2, 2),
    (7, 4, 4),
    (5, 6, 6),
)
RUINED_SPOILED = 8

#: Binding the Mundane Codex needs a Finesse Total of 6 (p. 103).
BINDING_FINESSE = 6
#: What a magical copy loses of the original's craftsmanship: its
#: resonances and clarification (p. 101), and its binding (loose sheets).
LOST_CRAFT: tuple[str, ...] = ("resonance", "story_resonance", "clarified", "binder")
#: The physical form of a copy left as loose sheets (book_kinds).
UNBOUND = "Unbound"

#: Pages: a tractatus, a summa's for each point of Level, a Lab Text's for
#: each level of its effect (pp. 101, 103).
TRACTATUS_PAGES = 160
SUMMA_PAGES_PER_LEVEL = 25
LAB_TEXT_PAGES_PER_LEVEL = 1

#: A mundane scribe's pages a day (p. 101).
SCRIBE_PAGES_PER_DAY = 4

#: A Lab Text copied flawlessly (p. 103): (the most levels, the Finesse
#: Total needed). A year's worth (four seasons') + 3 more, as Rego craft
#: magic's Ease Factor rises from a season's work to a year's (DE p. 307);
#: past that no book gives a figure.
LAB_TEXT_FLAWLESS: tuple[tuple[int, int], ...] = ((120, 11), (360, 14), (1440, 17))
LAB_TEXT_YEAR = LAB_TEXT_FLAWLESS[-1][0]

#: The effects of a copying device whose uses a day cap its books (p. 102).
DEVICE_COPY_EFFECT = IMAGE_SPELL
DEVICE_BIND_EFFECT = BINDING_SPELL


def finesse_total(magus: Character) -> int:
    """The copyist's Finesse Total: Perception + Finesse with the Wound,
    Fatigue and Flaw penalties (DE p. 307, over TME's Intelligence)."""
    return craft_magic.roll_base(magus, craft_magic.REGO)


def quill_ease(quality: int) -> int:
    """The Copyist's Puissant Quill's Ease Factor for a book of `quality`."""
    for highest, ease in QUILL_EASE:
        if quality <= highest:
            return ease
    return HARDEST_EASE


@dataclass(frozen=True)
class CopyOutcome:
    """What copying a book page by page by magic gives: the total read on
    the table, the pages spoiled in ten, and the copy's Quality (None: no
    readable book)."""

    total: int
    table_total: int
    ease: int
    spoiled: int
    quality: int | None

    @property
    def readable(self) -> bool:
        return self.quality is not None


def copy_outcome(original_quality: int, total: int) -> CopyOutcome:
    """The table (p. 100): the Finesse Total, + 3 at Ease Factor 9 and - 3
    at 15, against the rows; a total between two rows reads the lower."""
    ease = quill_ease(original_quality)
    on_table = total + TABLE_EASE - ease
    for lowest, spoiled, lost in COPY_TABLE:
        if on_table >= lowest:
            return CopyOutcome(
                total, on_table, ease, spoiled, max(0, original_quality - lost)
            )
    return CopyOutcome(total, on_table, ease, RUINED_SPOILED, None)


def spoiled_pages(total: int, quality: int = 7) -> int:
    """Pages spoiled in ten at `total` (a Lab Text has no Quality: the
    table's own Ease Factor of 12)."""
    return copy_outcome(quality, total).spoiled


def book_pages(book: Book, lab_text_level: int = 0) -> int | None:
    """About how many pages the book has (None: a kind the rule gives no
    figure for)."""
    if book.type == "Tractatus":
        return TRACTATUS_PAGES
    if book.type in ("Art Summa", "Ability Summa"):
        return SUMMA_PAGES_PER_LEVEL * max(1, book.level or 0)
    if book.type in ("Lab Text", "Casting Tablet"):
        return LAB_TEXT_PAGES_PER_LEVEL * max(1, lab_text_level)
    return None


def lab_text_needed(levels: int) -> int | None:
    """The Finesse Total that copies `levels` of Lab Texts flawlessly
    (None past a year's worth, 1,440 levels: no book gives a figure)."""
    for most, total in LAB_TEXT_FLAWLESS:
        if levels <= most:
            return total
    return None


def scribe_days(pages: int) -> int:
    """The days a mundane scribe takes to copy `pages` (p. 101), before
    as many again tidying and illuminating them."""
    return -(-max(0, pages) // SCRIBE_PAGES_PER_DAY)


def _effect(device: EnchantedDevice, name: str) -> InstilledEffect | None:
    return next(
        (
            e
            for e in device.effects
            if e.known
            and e.instilling_progress is None
            and e.name.strip().casefold() == name.casefold()
        ),
        None,
    )


def copies_books(device: EnchantedDevice) -> bool:
    """Whether the device copies a book: it has The First Furrow Guides the
    Second instilled (p. 102)."""
    return _effect(device, DEVICE_COPY_EFFECT) is not None


def binds_books(device: EnchantedDevice) -> bool:
    """Whether the device binds the copies itself (Binding the Mundane
    Codex instilled, p. 103)."""
    return _effect(device, DEVICE_BIND_EFFECT) is not None


def device_books_a_day(device: EnchantedDevice, *, bound: bool) -> int | None:
    """The books a copying device copies a day: one a use of its First
    Furrow, and, binding them with its own Binding the Mundane Codex, the
    fewer of the two (pp. 102-103; None: unlimited uses, or not a copying
    device)."""
    names = [DEVICE_COPY_EFFECT] + ([DEVICE_BIND_EFFECT] if bound else [])
    found = [_effect(device, name) for name in names]
    counts = [
        int(e.uses_per_day) for e in found if e is not None and e.uses_per_day.isdigit()
    ]
    return min(counts) if counts else None


def device_season_books(device: EnchantedDevice, *, bound: bool) -> int | None:
    """The most books a copying device copies in a season of work (its
    books a day for the season's days; None: no cap)."""
    a_day = device_books_a_day(device, bound=bound)
    return None if a_day is None else a_day * SEASON_DAYS


def hazard_risk(spoiled: int) -> int:
    """Hazardous Lab Texts: the extra Experimentation roll's risk modifier,
    half the pages spoiled in ten (p. 103: four in ten is +2)."""
    return round_down(spoiled / 2)


def can_bind(total: int) -> bool:
    """Whether Binding the Mundane Codex binds the sheets for this caster."""
    return total >= BINDING_FINESSE


def magic_copy(
    book: Book,
    quality: int | None,
    owner_kind: str,
    owner_id: str,
    *,
    bound: bool,
) -> Book:
    """The copy: the original's text exactly (a raw Lab Text stays raw, in
    its author's code), at `quality`, without its resonances or binding;
    bound by Binding the Mundane Codex, it has the sound binding's +1
    (extended Quality rules) and is a bound codex of its own."""
    craft = [key for key in book.craft if key not in LOST_CRAFT]
    if bound:
        craft.append("binder")
    return replace(
        book,
        id=f"{book.id}_magic_copy",
        owner_kind=owner_kind,
        owner_id=owner_id,
        quality=book.quality if quality is None else quality,
        craft=craft,
        physical_form="" if bound else UNBOUND,
        copy_of=book.copy_of or book.id,
        codex_id=None,
        device_id=None,
        experimental_effects=[replace(e) for e in book.experimental_effects],
    )


# -- a large library -------------------------------------------------------------


def art_score(xp: int) -> int:
    """The score an Art's experience buys (1, 3, 6, 10...)."""
    score = 0
    while (score + 1) * (score + 2) // 2 <= xp:
        score += 1
    return score


def art_xp(score: int) -> int:
    """The experience an Art's score needs."""
    return score * (score + 1) // 2


@dataclass(frozen=True)
class LibraryScore:
    """A large library's figures in one subject: its Level and Quality,
    from its best summa (`best`, a book id) and the books that count."""

    level: int
    quality: int
    best: str
    summae: int
    tractatus: int


def library_score(books: list[Book]) -> LibraryScore | None:
    """The library's Level and Quality in a subject from its `books` on it
    (None: no summa, so no score). The best summa (highest Level +
    Quality) sets the base; each other summa within three points of the
    library's Level + Quality is a point of experience in its Level, each
    tractatus within three of its Quality one in its Quality, both rising
    as Arts. A copy of a book already counted adds nothing."""
    seen: set[str] = set()
    unique: list[Book] = []
    for book in books:
        original = book.copy_of or book.id
        if original not in seen:
            seen.add(original)
            unique.append(book)
    summae = [b for b in unique if b.type in ("Art Summa", "Ability Summa")]
    if not summae:
        return None
    best = max(summae, key=lambda b: ((b.level or 0) + (b.quality or 0), b.quality))
    level_xp = art_xp(best.level or 0)
    quality_xp = art_xp(best.quality or 0)
    counted_summae = counted_tractatus = 0
    others = sorted(
        (b for b in summae if b is not best),
        key=lambda b: -((b.level or 0) + (b.quality or 0)),
    )
    for book in others:
        library = art_score(level_xp) + art_score(quality_xp)
        if abs((book.level or 0) + (book.quality or 0) - library) <= 3:
            level_xp += 1
            counted_summae += 1
    tractatus = sorted(
        (b for b in unique if b.type == "Tractatus"), key=lambda b: -(b.quality or 0)
    )
    for book in tractatus:
        if abs((book.quality or 0) - art_score(quality_xp)) <= 3:
            quality_xp += 1
            counted_tractatus += 1
    return LibraryScore(
        art_score(level_xp),
        art_score(quality_xp),
        best.id,
        counted_summae,
        counted_tractatus,
    )


def library_study(score: int, library: LibraryScore) -> tuple[int, int | None]:
    """A season studying the subject from the library: (experience, the
    seasons it can go on giving that once the student's score reaches the
    library's Level; None while below it). Below its Level, Quality + 3;
    at or above it, its Quality, for Quality more seasons."""
    if score < library.level:
        return library.quality + 3, None
    return library.quality, library.quality


# -- technological savings ----------------------------------------------------

SHILLINGS_PER_POUND = 20
#: A pound a point of inhabitants, in shillings (p. 120).
POUND_SPLIT: dict[str, int] = {
    "provisions": 10,
    "wages": 4,
    "consumables": 4,
    "buildings": 2,
}
#: Shillings saved on every pound a point of inhabitants costs when the
#: covenant's bread is of grain made by magic (p. 120), by the share of
#: its provisions that is bread.
BREAD_SHILLINGS: dict[str, float] = dict(zip(BREAD_SHARES, (5.0, 7.5)))
#: The share of a store of grain lost each year (p. 121), by its keeping.
GRAIN_LOSS: dict[str, float] = dict(zip(GRAIN_CARE, (0.05, 0.10, 0.20)))
#: A point of inhabitants eats this many bushels a year (p. 121).
BUSHELS_PER_POINT = 24
#: Fill the Capacious Silo's grain (p. 120).
SILO_BUSHELS = 20_000
#: Pounds saved a year for each magnitude of an item doing covenfolk's
#: work, and for each magnitude of a Ritual spell cast (Covenants p. 67).
ITEM_POUNDS = 1
RITUAL_POUNDS = 5


def year_need(points: int) -> int:
    """Bushels the covenant eats in a year."""
    return BUSHELS_PER_POINT * max(0, points)


def grain_after_year(stock: int, points: int, care: str) -> int:
    """The store a year on: what was eaten, if it fed the covenant, and
    the year's loss on what was there at its start (p. 121's example)."""
    need = year_need(points)
    eaten = need if stock >= need > 0 else 0
    lost = stock * GRAIN_LOSS[care]
    return max(0, round_down(stock - eaten - lost))


def grain_years(stock: int, points: int, care: str) -> int:
    """How many years the store feeds the covenant its bread."""
    need = year_need(points)
    if need <= 0:
        return 0
    years = 0
    while stock >= need:
        years += 1
        stock = grain_after_year(stock, points, care)
    return years


def bread_saving(points: int, share: str) -> float:
    """Pounds a year the covenant saves while its bread is grain made by
    magic."""
    return max(0, points) * BREAD_SHILLINGS[share] / SHILLINGS_PER_POUND


def device_magnitudes(device: EnchantedDevice) -> int:
    """The magnitudes of a device's finished, known effects."""
    return sum(
        magnitude(effect.level)
        for effect in device.effects
        if effect.known and effect.instilling_progress is None
    )


def magic_savings(
    typed: int,
    devices: list[EnchantedDevice],
    ritual_magnitudes: int,
    *,
    points: int,
    grain: int,
    care: str,
    share: str,
    provisions_room: float,
    labor_room: float | None = None,
) -> Breakdown:
    """The Magic row of the Cost Savings: the pounds typed, a pound a
    magnitude of each item doing covenfolk's work, five a magnitude of the
    Ritual spells cast this year, and the bread a store of magical grain
    saves while it lasts the year (no more than the Provisions still
    bought). The items and Rituals do laborers' work, so together they
    save at most `labor_room`, what the laborers' limit leaves (half the
    Provisions, less the laborers' own saving; Covenants p. 67)."""
    lines: list[Line] = []
    if typed:
        lines.append(Line("typed", typed))
    for device in devices:
        mags = device_magnitudes(device)
        if mags:
            lines.append(
                Line(
                    f"{device.name}, {mags} magnitude(s)",
                    ITEM_POUNDS * mags,
                    source=SAVINGS_SOURCE,
                )
            )
    if ritual_magnitudes:
        lines.append(
            Line(
                f"Ritual spells, {ritual_magnitudes} magnitude(s)",
                RITUAL_POUNDS * ritual_magnitudes,
                source=SAVINGS_SOURCE,
            )
        )
    labor = sum(line.amount or 0 for line in lines[1 if typed else 0 :])
    if labor_room is not None and labor > max(0.0, labor_room):
        lines.append(
            Line(
                "over half the Provisions with the laborers",
                max(0.0, labor_room) - labor,
                source=SAVINGS_SOURCE,
            )
        )
    if grain and grain >= year_need(points) > 0:
        saved = min(bread_saving(points, share), max(0.0, provisions_room))
        years = grain_years(grain, points, care)
        lines.append(
            Line(
                f"magical grain, {grain} bushels (bread for {years} year(s))",
                saved,
                source=SAVINGS_SOURCE,
            )
        )
    return Breakdown(sum(line.amount or 0 for line in lines), lines)


def breakdown_text(breakdown: Breakdown) -> str:
    """The Magic row's working, one term after another."""
    return "; ".join(
        f"{line.label} {line.amount:g}" for line in breakdown.lines if line.amount
    )
