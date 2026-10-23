"""Logic behind books and the covenant Library tab -- no UI in here.

Build Point costs and covenant-creation limits (reference/Libraries.md), who
owns a book, which books a covenant's Library lists, the text for list rows
and the details panel, and reading books from a CSV file.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, replace
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import book_kinds, catalog, storage
from . import spells as spl
from .arts import ART_LOOKUP
from .csv_import import parse_rows, read_text_any, skipped_preview
from .markup import PROBLEM_GLYPH, escape, fit, markdown_text, problem
from .models import (
    BOOK_TYPES,
    TEXT_SPELL,
    Book,
    Character,
    Codex,
    Covenant,
    DeviceComponent,
    EnchantedDevice,
    Saga,
    Spell,
)
from .rules.library import (
    POOL_LEVELS,
    POOL_POINTS,
    SPELL_TYPES,
    SUMMA_TYPES,
    Pool,
    book_spell,
    books_owned_by,
    can_read,
    codex_of,
    cost,
    covenant_of,
    effective_quality,
    extended_quality,
    has_quality,
    is_ability_book,
    is_art_book,
    level_of,
    numbers_to_set,
    owner_record,
    pool,
    priced_quality,
    quality_adjustments,
    subject,
)
from .tables import Table


def has_level(book_type: str) -> bool:
    return book_type in SUMMA_TYPES or book_type in SPELL_TYPES


# ------------------------------------------------------- the linked spell


def records_spell(book_type: str, text_kind: str) -> bool:
    """Whether a book of this Type (and, a Lab Text, kind) is of a spell: a
    Casting Tablet, or a Lab Text of a spell -- not one of an enchantment, a
    Longevity Ritual or anything else, which carry their own
    Technique, Form and level. A Lab Text with no kind yet counts as a
    spell's."""
    if book_type == "Lab Text":
        return text_kind in ("", TEXT_SPELL)
    return book_type in SPELL_TYPES


def needs_spell(book: Book) -> bool:
    return records_spell(book.type, book.text_kind)


# ------------------------------------------------------------------- rules


POOL_SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Lab Texts and "
    "Casting Tablets (p. 180)"
)


def pooled(book_type: str) -> bool:
    """Whether books of this type are bought as a pool (see pool())."""
    return book_type in POOL_POINTS


def pool_text(pool_: Pool) -> str:
    """ "12 levels, 3 Build Points (3 levels unspent)"."""
    text = f"{pool_.levels} levels, {pool_.points} Build Points"
    return text + (f" ({pool_.unspent} levels unspent)" if pool_.unspent else "")


def priced(saga: Saga, book: Book) -> bool:
    """Whether the book's Build Points are worth showing: it belongs to a
    covenant that is still In Creation."""
    if book.owner_kind != "covenant":
        return False
    covenant = saga.covenant(book.owner_id)
    return covenant is not None and covenant.in_creation


def cost_formula(book: Book, saga: Saga | None = None) -> str:
    """How `cost` was worked out, e.g. "Level 12 + Quality 10"."""
    level = level_of(book, saga) or 0
    quality = priced_quality(saga, book) or 0
    if book.type == "Art Summa":
        return f"Level {level} + Quality {quality}"
    if book.type == "Ability Summa":
        return f"Quality {quality} + 3 x Level {level}"
    if book.type == "Tractatus":
        return f"Quality {quality}"
    if pooled(book.type):
        return (
            f"{level} levels of the {book.type} pool: "
            f"{POOL_POINTS[book.type]} per {POOL_LEVELS} levels of the pool"
        )
    return "Other books cost nothing"


def quality_limit(book_type: str, level: int) -> int | None:
    """The highest quality allowed at covenant creation, or None if there's no
    limit for this type."""
    if book_type == "Art Summa":
        return min(22, 11 + (20 - level))
    if book_type == "Ability Summa":
        return min(22, 11 + 3 * (8 - level))
    if book_type == "Tractatus":
        return 11
    return None


#: The highest summa level allowed at covenant creation.
LEVEL_LIMITS: dict[str, int] = {"Art Summa": 20, "Ability Summa": 8}


def limit_warnings(book: Book) -> list[str]:
    """Covenant-creation limits this book goes over (plain text). Books found in
    play may exceed them, so these are warnings, never errors. Lab Texts and
    Casting Tablets aren't checked: their limit comes from a power-level
    table not yet provided."""
    warnings: list[str] = []
    level = book.level or 0
    level_limit = LEVEL_LIMITS.get(book.type)
    if level_limit is not None and level > level_limit:
        warnings.append(
            f"Level {level} is over the covenant-creation limit of {level_limit}."
        )
    limit = quality_limit(book.type, level)
    if limit is not None and (book.quality or 0) > limit:
        warnings.append(
            f"Quality {book.quality} is over the covenant-creation limit of {limit}."
        )
    return warnings


# ---------------------------------------------------------------- abilities


@lru_cache(maxsize=1)
def _ability_names() -> tuple[str, ...]:
    return tuple(a.name for a in catalog.load_ability_catalog())


def canonical_ability(name: str) -> str | None:
    """The ability catalog's spelling of `name` -- a catalog name, or a
    templated family with its blank filled in ("area lore: rhine" ->
    "Area Lore: rhine") -- matched regardless of case; None if it isn't one."""
    wanted = name.strip().lower()
    for known in _ability_names():
        if "{" not in known:
            if known.lower() == wanted:
                return known
            continue
        prefix = known.split("{", 1)[0]
        detail = name.strip()[len(prefix) :].strip()
        if wanted.startswith(prefix.lower()) and detail:
            return prefix + detail
    return None


def status_problems(book: Book, saga: Saga | None = None) -> list[str]:
    """Things about the book the user should fix (the row shows in the error colour): an
    Ability that isn't in the ability catalog (typically from an import),
    which studying from the book will need; and, given the saga, a Lab Text
    or Casting Tablet whose spell can't be found; and a summa or tractatus
    whose Level or Quality is still to be set (numbers_to_set)."""
    if (
        is_ability_book(book.type, book.subject_kind)
        and book.ability
        and canonical_ability(book.ability) is None
    ):
        return [
            f"Unknown ability: {book.ability!r} isn't in the ability list; "
            "edit the book to choose one."
        ]
    missing = numbers_to_set(book)
    if missing:
        return [
            f"{' and '.join(missing)} to be set: edit the book to give "
            f"{'them' if len(missing) > 1 else 'it'} once it comes into play."
        ]
    if saga is not None and needs_spell(book) and book_spell(saga, book) is None:
        named = (
            f"{book.spell_name!r} isn't in the spell list"
            if book.spell_name
            else "no spell chosen"
        )
        return [f"Unknown spell: {named}; edit the book to choose one."]
    return []


# ------------------------------------------------------------------ owners


def is_unassigned(saga: Saga, book: Book) -> bool:
    return owner_record(saga, book) is None


def unassigned_books(saga: Saga) -> list[Book]:
    """Books filed under the saga: no owner, or one that no longer exists."""
    return [b for b in saga.books if is_unassigned(saga, b)]


def readers(saga: Saga, book: Book) -> list[Character]:
    """The magi and companions who may study `book`."""
    return [c for c in saga.characters if c.type != "grog" and can_read(saga, c, book)]


def studyable_books(saga: Saga, character: Character) -> list[Book]:
    """The summae and tractatus `character` may study (see can_read)."""
    return [
        b
        for b in saga.books
        if b.type in ("Art Summa", "Ability Summa", "Tractatus")
        and can_read(saga, character, b)
    ]


def owner_value(kind: str | None, owner_id: str | None) -> str:
    """The Owner select's value for an owner ("" for none)."""
    return f"{kind}:{owner_id}" if kind and owner_id else ""


def parse_owner_value(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    kind, _, owner_id = value.partition(":")
    return kind, owner_id


def owner_options(saga: Saga) -> list[tuple[str, str]]:
    """(label, value) for every possible owner: each covenant, laboratory and
    character of the saga, then nobody."""
    options = [
        (f"Covenant: {c.name}", owner_value("covenant", c.id)) for c in saga.covenants
    ]
    options += [
        (f"Laboratory: {lab.name}", owner_value("laboratory", lab.id))
        for lab in saga.laboratories
    ]
    options += [
        (f"Character: {c.name}", owner_value("character", c.id))
        for c in saga.characters
    ]
    options.append(("(none - unassigned)", ""))
    return options


def owner_label(saga: Saga, book: Book) -> str:
    owner = owner_record(saga, book)
    if owner is None or book.owner_kind is None:
        return "(none - unassigned)"
    return f"{book.owner_kind.capitalize()}: {owner.name}"


def location_label(saga: Saga, book: Book) -> str:
    """Where the book is kept: the covenant's library, a laboratory, or on the
    character who owns it."""
    owner = owner_record(saga, book)
    if owner is None:
        return "Unassigned"
    if book.owner_kind == "covenant":
        return "Covenant Library"
    if book.owner_kind == "laboratory":
        return f"Lab: {owner.name}"
    return owner.name


# ------------------------------------------------------------------ codices


def codex_books(saga: Saga, book: Book) -> list[Book]:
    """Every book bound in the same codex as `book`, itself included, in the
    order added; just [book] when it is bound alone."""
    if codex_of(saga, book) is None:
        return [book]
    return [b for b in saga.books if b.codex_id == book.codex_id]


def new_codex(saga: Saga, name: str) -> Codex:
    """A new codex, added to the saga."""
    codex = Codex(
        id=storage.generate_unique_id(name or "codex", [c.id for c in saga.codices]),
        name=name,
    )
    saga.codices.append(codex)
    return codex


def set_owner(
    saga: Saga, book: Book, owner_kind: str | None, owner_id: str | None
) -> None:
    """Give `book` a new owner. A codex's books are kept together, so the
    others bound with it move too."""
    for mate in codex_books(saga, book):
        mate.owner_kind, mate.owner_id = owner_kind, owner_id
        device = epitome_device(saga, mate)
        if device is not None:
            device.holder_kind, device.holder_id = owner_kind, owner_id


def epitome_device(saga: Saga, book: Book) -> EnchantedDevice | None:
    """The enchanted device a book is, when it is an epitome."""
    if not book.device_id:
        return None
    return next((d for d in saga.enchanted_devices if d.id == book.device_id), None)


def enchant_as_epitome(saga: Saga, book: Book) -> EnchantedDevice:
    """Make `book` an epitome: a new invested device, the book itself
    (material level 2, size x4), held where the book is kept."""
    device = EnchantedDevice(
        id=storage.generate_unique_id(
            f"{book.name} epitome", [d.id for d in saga.enchanted_devices]
        ),
        name=book.name or "Epitome",
        description="An epitome: this book, enchanted (Covenants, Secondary "
        "Functions). Only its own resonant materials help its enchantment.",
        holder_kind=book.owner_kind,
        holder_id=book.owner_id,
        components=[
            DeviceComponent(
                "the book", book_kinds.EPITOME_MATERIAL, book_kinds.EPITOME_SIZE
            )
        ],
    )
    saga.enchanted_devices.append(device)
    book.device_id = device.id
    return device


def prune_codices(saga: Saga) -> None:
    """Drop the codices no book is bound in any more."""
    used = {b.codex_id for b in saga.books if b.codex_id}
    saga.codices = [c for c in saga.codices if c.id in used]
    for book in saga.books:
        if book.codex_id and book.codex_id not in used:
            book.codex_id = None


def craft_warnings(saga: Saga, book: Book) -> list[str]:
    """Under the extended rules: craftsmanship that can't go together, and
    a Quality over what an Art book effectively reaches (35 - Level for a
    summa, 17 for a tractatus). Warnings, not refusals."""
    if not extended_quality(saga) or book.quality is None:
        return []
    codex = codex_of(saga, book)
    found = book_kinds.craft_problems(
        book.craft,
        book.physical_form,
        codex.collection if codex else "",
        glossed=book.glossed,
    )
    quality = effective_quality(saga, book) or 0
    if book.type == "Art Summa" and book.level is not None:
        ceiling = book_kinds.ART_SUMMA_CEILING - book.level
        if quality > ceiling:
            found.append(
                f"Quality {quality} is over the {ceiling} (35 - Level) an Art summa "
                "effectively reaches."
            )
    if book.type == "Tractatus" and book.subject_kind == "Art":
        ceiling = book_kinds.ART_TRACTATUS_CEILING
        if quality > ceiling:
            found.append(
                f"Quality {quality} is over the {ceiling} an Art tractatus "
                "effectively reaches."
            )
    return found


def grouped(saga: Saga, books: list[Book]) -> list[Book]:
    """`books` in the order given, except that the books of one codex are
    listed together, where its first one comes."""
    placed: set[str] = set()
    result: list[Book] = []
    for book in books:
        if book.codex_id and codex_of(saga, book) is not None:
            if book.codex_id in placed:
                continue
            placed.add(book.codex_id)
            result += [b for b in books if b.codex_id == book.codex_id]
        else:
            result.append(book)
    return result


def codex_label(saga: Saga, book: Book) -> str:
    """ "Codex: name (palimpsest)" for the details panel, or "" when the
    book is bound alone."""
    codex = codex_of(saga, book)
    if codex is None:
        return ""
    kinds = []
    if codex.collection == book_kinds.FLORILEGIUM:
        kinds.append(f"florilegium, +{codex.florilegium_bonus}")
    elif codex.collection:
        kinds.append(codex.collection.lower())
    if codex.palimpsest:
        kinds.append("palimpsest")
    return codex.name + (f" ({'; '.join(kinds)})" if kinds else "")


def kind_text(saga: Saga, book: Book) -> str:
    """The book's opus type and physical form for the details panel
    ("Commentary on Physics · Exemplar"), or ""."""
    parts = []
    if book.opus:
        summa = next((b for b in saga.books if b.id == book.commentary_on), None)
        parts.append(f"{book.opus} on {summa.name}" if summa else book.opus)
    if book.physical_form:
        parts.append(book.physical_form)
    return " · ".join(parts)


# -------------------------------------------------------------------- text


def subject_title(book: Book) -> str:
    """What the Art/Ability/Spell field is called for this book."""
    if book.type in SPELL_TYPES:
        return "Spell"
    if is_art_book(book.type, book.subject_kind):
        return "Art"
    if is_ability_book(book.type, book.subject_kind):
        return "Ability"
    return "Subject"


_NAME_WIDTH = 20
_TYPE_WIDTH = 14
_LEVEL_WIDTH = 5
_QUALITY_WIDTH = 8
_LOCATION_WIDTH = 17
#: The Subject column (Art, Ability or spell) takes whatever room the list
#: has, between these two widths (see subject_width).
SUBJECT_MIN_WIDTH = 12
SUBJECT_MAX_WIDTH = 40
#: Everything in a row but the Subject column: the columns, their spacing,
#: room for a flagged row's problem mark, and room for a scrollbar.
_ROW_WIDTH_WITHOUT_SUBJECT = (
    (_NAME_WIDTH + 1 + _TYPE_WIDTH + 1 + 1 + _LEVEL_WIDTH + _QUALITY_WIDTH + 2)
    + _LOCATION_WIDTH
    + len(f" {PROBLEM_GLYPH}")
    + 2
)


def subject_width(row_width: int) -> int:
    """How wide the Subject column can be in a row `row_width` characters wide
    (after the list's markers)."""
    spare = row_width - _ROW_WIDTH_WITHOUT_SUBJECT
    return max(SUBJECT_MIN_WIDTH, min(SUBJECT_MAX_WIDTH, spare))


def table_header(subject_cols: int = SUBJECT_MIN_WIDTH) -> str:
    """The column titles above the book list; the two-character indent is the
    list's selector marker. Long values are cut short with an ellipsis."""
    return (
        f"  {'Name':<{_NAME_WIDTH}} {'Type':<{_TYPE_WIDTH}} "
        f"{'Subject':<{subject_cols}} {'Level':>{_LEVEL_WIDTH}}"
        f"{'Quality':>{_QUALITY_WIDTH}}  Location"
    )


def _number(value: int | None) -> str:
    return "-" if value is None else str(value)


def row_label(saga: Saga, book: Book, subject_cols: int = SUBJECT_MIN_WIDTH) -> str:
    """One list row (markup), columns lined up with `table_header`; in the
    theme's error colour when the book has a status problem (see
    status_problems)."""
    location = fit(location_label(saga, book), _LOCATION_WIDTH).rstrip()
    row = (
        f"{escape(fit(_codex_mark(saga, book) + (book.name or '(untitled)'), _NAME_WIDTH))} "
        f"{escape(fit(book.type, _TYPE_WIDTH))} "
        f"{escape(fit(subject(book, saga) or '-', subject_cols))} "
        f"{_number(level_of(book, saga)):>{_LEVEL_WIDTH}}"
        f"{_number(effective_quality(saga, book)):>{_QUALITY_WIDTH}}  "
        f"{escape(location)}"
    )
    if status_problems(book, saga):
        return f"[$text-error]{row} {PROBLEM_GLYPH}[/]"
    return row


def book_table(saga: Saga, books: Sequence[Book]) -> Table:
    """`books` as a table (markup) with row_label's columns, whole; a
    book with a status problem in the theme's error colour."""
    rows = []
    for book in books:
        cells = [
            escape(_codex_mark(saga, book) + (book.name or "(untitled)")),
            escape(book.type),
            escape(subject(book, saga) or "-"),
            _number(level_of(book, saga)),
            _number(effective_quality(saga, book)),
            escape(location_label(saga, book)),
        ]
        if status_problems(book, saga):
            cells[-1] += f" {PROBLEM_GLYPH}"
            cells = [f"[$text-error]{cell}[/]" for cell in cells]
        rows.append(cells)
    return Table(
        ["Name", "Type", "Subject", "Level", "Quality", "Location"], rows, markup=True
    )


#: What a row's name starts with when the book is bound in a codex with
#: others (grouped() lists them together).
CODEX_MARK = "│ "


def _codex_mark(saga: Saga, book: Book) -> str:
    return CODEX_MARK if codex_of(saga, book) is not None else ""


def _quality_text(saga: Saga, book: Book) -> str:
    """The details panel's Quality: what it is read at, and how, when
    anything changes it ("10 (written 9; commentary +1)")."""
    adjustments = quality_adjustments(saga, book)
    if book.quality is None or not adjustments:
        return _number(book.quality)
    parts = ", ".join(f"{a.label} {a.amount:+d}" for a in adjustments)
    return (
        f"{_number(effective_quality(saga, book))} "
        f"(written {_number(book.quality)}; {parts})"
    )


def _codex_lines(saga: Saga, book: Book) -> list[str]:
    """The details panel's codex: its name, how many books it binds (listed
    together above), and that it has one reader a season."""
    codex = codex_of(saga, book)
    if codex is None:
        return []
    count = len(codex_books(saga, book))
    return [
        f"[b]Codex:[/] {escape(codex_label(saga, book))} [dim]({count} books, "
        "one reader a season)[/]"
    ]


def _level_text(saga: Saga, book: Book) -> str:
    """The details panel's Level: a Lab Text's or Casting Tablet's says
    whether it comes from the spell or is the book's own (General spell)."""
    level = _number(level_of(book, saga))
    if book.type not in SPELL_TYPES:
        return level
    spell = book_spell(saga, book)
    if spell is None:
        return level
    return (
        f"{level} (the spell's)"
        if spell.level is not None
        else f"{level} (General spell)"
    )


def _cell(label: str, value: object) -> tuple[str, int]:
    """A "Label: value" cell as (markup, plain-text width)."""
    text = str(value)
    return f"[b]{label}:[/] {escape(text)}", len(label) + 2 + len(text)


def summary_texts(
    books: list[Book], saga: Saga | None = None, *, research: str = ""
) -> tuple[str, str]:
    """The Library tab's Summary (markup, read-only): Summae and Tractatus
    (each split into Ability and Art), Other and the total down the left;
    Lab Texts, Casting Tablets, any codices and `research` (a covenant
    library's research bonuses, book_value.research_count) down the right."""

    def count(book_type: str, subject_kind: str | None = None) -> int:
        return sum(
            1
            for b in books
            if b.type == book_type
            and (
                subject_kind is None
                or (book_type == "Tractatus" and b.subject_kind == subject_kind)
            )
        )

    ability_summae, art_summae = count("Ability Summa"), count("Art Summa")
    ability_tracts, art_tracts = (
        count("Tractatus", "Ability"),
        count("Tractatus", "Art"),
    )

    def rows(pairs: list[tuple[str, object]]) -> str:
        """Values lined up in one column; indented rows are sub-counts (not
        bold); ("", "") is a blank line."""
        width = max(len(label) for label, _ in pairs) + 2
        lines = []
        for label, value in pairs:
            text = f"{label}:".ljust(width) if label else ""
            if label and not label.startswith(" "):
                text = f"[b]{text}[/]"
            lines.append(f"{text}{value}")
        return "\n".join(lines)

    # Kept to four rows a column, so the book list below keeps its room.
    left = rows(
        [
            (
                "Summae",
                f"{ability_summae + art_summae} "
                f"(Ability {ability_summae}, Art {art_summae})",
            ),
            (
                "Tractatus",
                f"{count('Tractatus')} (Ability {ability_tracts}, Art {art_tracts})",
            ),
            ("Other", count("Other")),
            ("Total Books", len(books)),
        ]
    )
    codices = (
        {b.codex_id for b in books if codex_of(saga, b) is not None}
        if saga is not None
        else set()
    )
    right = rows(
        [
            ("Lab Texts", count("Lab Text")),
            ("Casting Tablets", count("Casting Tablet")),
            *([("Codices", len(codices))] if codices else []),
            *([("Research", escape(research))] if research else []),
        ]
    )
    return left, right


def detail_text(saga: Saga, book: Book | None) -> str:
    """The details panel (markup): every field of the book in the sheet's
    order -- Name; then Type, Art/Ability/Spell, Level, Quality down the left
    and Language, Author, Year Published, Owner down the right; then Cost,
    any covenant-creation limit warnings, and the Description."""
    if book is None:
        return "[dim]Select a book to see its details.[/]"
    not_set = "(not set)"
    subject_text = subject(book, saga)
    spell = book_spell(saga, book)
    if spell is not None:
        subject_text = f"{spell.name} ({spl.shorthand(spell)})"
    if book.type == "Tractatus" and book.subject_kind:
        subject_text = f"{subject_text or not_set} ({book.subject_kind})"
    year = "(unknown)" if book.year_published is None else book.year_published
    left = [
        _cell("Type", book.type),
        _cell(subject_title(book), subject_text or not_set),
        _cell("Level", _level_text(saga, book)),
        _cell("Quality", _quality_text(saga, book)),
    ]
    right = [
        _cell("Language", book.language or not_set),
        _cell("Author", book.author or "(unknown)"),
        _cell("Year Published", year),
        _cell("Owner", owner_label(saga, book)),
    ]
    width = max(w for _, w in left) + 4
    lines = [problem(f"[b]{escape(p)}[/b]") for p in status_problems(book, saga)]
    lines.append(_cell("Name", book.name or "(untitled)")[0])
    lines += _codex_lines(saga, book)
    device = epitome_device(saga, book)
    if device is not None:
        from . import enchanted_devices as ed

        lines.append(
            f"[b]Epitome:[/] {escape(device.name)} [dim]({escape(device.type)}, "
            f"{escape(ed.capacity_text(saga, device))})[/]"
        )
    kind = kind_text(saga, book)
    if kind:
        lines.append(f"[b]Kind:[/] {escape(kind)}")
    lines += [f"{lm}{' ' * (width - lw)}{rm}" for (lm, lw), (rm, _) in zip(left, right)]
    if priced(saga, book):
        # Build Points matter only while its covenant is being created;
        # in play they're on the covenant's Build tab.
        if numbers_to_set(book):
            text = "to be set, with its numbers"
        elif pooled(book.type):
            library = books_owned_by(saga, "covenant", book.owner_id or "")
            text = (
                f"{level_of(book, saga) or 0} levels of the {book.type} pool "
                f"({pool_text(pool(library, book.type, saga))})"
            )
        else:
            text = f"{cost(book, saga)} Build Points ({cost_formula(book, saga)})"
        lines.append(_cell("Cost", text)[0])
        lines += [problem(escape(w)) for w in limit_warnings(book)]
    lines += [problem(escape(w)) for w in craft_warnings(saga, book)]
    lines += _value_lines(book)
    lines += _tablet_lines(saga, book)
    lines += _research_lines(saga, book)
    lines += _study_lines(saga, book)
    if book.description.strip():
        lines += ["", "[b]Description:[/]", markdown_text(book.description.strip())]
    return "\n".join(lines)


def _value_lines(book: Book) -> list[str]:
    """The details panel's category of value and price guide (book_value),
    for a summa or tractatus with its numbers."""
    from . import book_value

    kind = book_value.category(book)
    if kind is None:
        return []
    return [
        f"[b]Value:[/] {kind} [dim]· price guide: "
        f"{escape(book_value.price_text(book))}[/]"
    ]


def _tablet_lines(saga: Saga, book: Book) -> list[str]:
    """A Casting Tablet: how each magus who can get at it casts from it
    (casting_text.tablet_casting_line)."""
    if book.type != "Casting Tablet":
        return []
    spell = book_spell(saga, book)
    if spell is None or spell.level is None:
        return []
    from . import casting_text

    magi = [c for c in readers(saga, book) if c.type == "magus"]
    if not magi:
        return []
    return ["", "[b]Casting from it:[/]"] + [
        casting_text.tablet_casting_line(saga, magus, spell) for magus in magi
    ]


def _research_lines(saga: Saga, book: Book) -> list[str]:
    """The details panel's research on the book's subject in the covenant
    library it is kept in, when it has a bonus or an encyclopedia."""
    from . import book_value

    covenant = saga.covenant(covenant_of(saga, book))
    subject = book_value.subject_of(book)
    if covenant is None or not subject:
        return []
    text = book_value.subject_research_text(saga, covenant, subject)
    return [f"[b]Research ({escape(subject)}):[/] {escape(text)}"] if text else []


def _study_lines(saga: Saga, book: Book) -> list[str]:
    """What a season reading the book gives each magus and companion of
    its covenant (rules.study): nothing for a book that isn't a
    summa or tractatus."""
    from .rules import study

    results = [
        (c, study.reading(c, book, effective_quality(saga, book)))
        for c in readers(saga, book)
    ]
    results = [(c, r) for c, r in results if r is not None]
    if not results:
        return []
    lines = ["", "[b]A season's reading:[/]"]
    for reader, result in results:
        text = f"{escape(reader.name)}: {result.xp} xp"
        extras = [
            f"{escape(line.label)} {line.amount:+g}"
            for line in result.lines[1:]
            if line.amount is not None
        ] + [
            f"{escape(line.label)} x{line.multiplier:g}"
            for line in result.lines
            if line.multiplier is not None
        ]
        if extras:
            text += f" ({', '.join(extras)})"
        if result.notes:
            text += f"; {escape(' '.join(result.notes))}"
        lines.append(text)
    return lines


# ------------------------------------------------------------ CSV import

#: Every spelling of a book type an import accepts (lower case), e.g. the
#: plural "Art Summae" used by the rulebook's headings.
_TYPE_ALIASES: dict[str, str] = {t.lower(): t for t in BOOK_TYPES} | {
    "art summae": "Art Summa",
    "ability summae": "Ability Summa",
    "lab texts": "Lab Text",
    "laboratory text": "Lab Text",
    "laboratory texts": "Lab Text",
    "casting tablets": "Casting Tablet",
}

#: Art names by lower-case name or abbreviation ("ignem", "ig" -> "Ignem").
#: Columns an import reads. `owner` and `cost` are recognised but not used:
#: imported books all go to one place, and cost is always calculated.
CSV_COLUMNS: tuple[str, ...] = (
    "name",
    "type",
    "language",
    "author",
    "year_published",
    "description",
    "art",
    "ability",
    "level",
    "quality",
    "tractatus_type",
    "spell",
    "codex",
    "encyclopedia",
    "opus",
    "physical_form",
)
CSV_UNUSED_COLUMNS: tuple[str, ...] = ("owner", "cost")


@dataclass
class CsvImport:
    """What a CSV file holds: the books it describes (not yet given ids or an
    owner), the rows that couldn't be read and why, and the columns that
    were not used."""

    books: list[Book] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    unused_columns: list[str] = field(default_factory=list)
    #: The codex names an encyclopedia column marked (yes / true / 1).
    encyclopedias: set[str] = field(default_factory=set)


#: What a CSV's Level or Quality cell says for "to be set later": the value
#: varies until the book comes into play (see numbers_to_set).
VARIABLE_WORDS: tuple[str, ...] = ("var", "variable", "varies")


def _is_variable(raw: str) -> bool:
    return raw.strip().lower() in VARIABLE_WORDS


def _whole_number(raw: str, label: str) -> int | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{label} {raw!r} isn't a whole number") from None


def _book_from_row(row: dict[str, str]) -> Book:
    """One CSV row as a Book, or ValueError saying what's wrong with it."""
    name = row.get("name", "").strip()
    if not name:
        raise ValueError("no name")
    raw_type = row.get("type", "").strip()
    book_type = _TYPE_ALIASES.get(" ".join(raw_type.lower().split()))
    if book_type is None:
        raise ValueError(f"unknown type {raw_type!r}" if raw_type else "no type")
    book = Book(
        id="",
        name=name,
        type=book_type,
        language=row.get("language", "").strip() or "Latin",
        author=row.get("author", "").strip(),
        description=row.get("description", "").strip(),
        year_published=_whole_number(row.get("year_published", ""), "Year"),
    )
    art = row.get("art", "").strip()
    ability = row.get("ability", "").strip()
    if book_type == "Tractatus":
        kind = row.get("tractatus_type", "").strip().capitalize()
        if not kind:  # not given: whichever subject the row fills in
            kind = "Art" if art and not ability else "Ability" if ability else ""
        if kind not in ("Art", "Ability"):
            raise ValueError("a Tractatus needs a tractatus_type of Art or Ability")
        book.subject_kind = kind
    if is_art_book(book_type, book.subject_kind):
        if art.lower() not in ART_LOOKUP:
            raise ValueError(f"unknown Art {art!r}" if art else "no Art")
        book.art = ART_LOOKUP[art.lower()]
    elif is_ability_book(book_type, book.subject_kind):
        if not ability:
            raise ValueError("no Ability")
        # Kept even if unknown: the book is flagged for the user to fix.
        book.ability = canonical_ability(ability) or ability
    elif book_type in SPELL_TYPES:
        book.spell_name = row.get("spell", "").strip()
        if not book.spell_name:
            raise ValueError("no spell")
    level_raw, quality_raw = row.get("level", ""), row.get("quality", "")
    if has_level(book_type):
        variable = _is_variable(level_raw) and book_type not in SPELL_TYPES
        book.level = None if variable else _whole_number(level_raw, "Level")
        # A Lab Text or Casting Tablet can take its Level from its spell.
        if book.level is None and book_type not in SPELL_TYPES and not variable:
            raise ValueError("no Level")
    if has_quality(book_type):
        variable = _is_variable(quality_raw)
        book.quality = None if variable else _whole_number(quality_raw, "Quality")
        if book.quality is None and not variable:
            raise ValueError("no Quality")
    if (book.level or 0) < 0 or (book.quality or 0) < 0:
        raise ValueError("a negative Level or Quality")
    # Until add_imported_books binds it: the name of the codex the rows that
    # share it are bound in.
    book.codex_id = row.get("codex", "").strip() or None
    _kinds_from_row(row, book)
    return book


def _kinds_from_row(row: dict[str, str], book: Book) -> None:
    """A CSV row's opus type and physical form (book_kinds), onto `book`;
    ValueError for one that isn't known."""
    opus = row.get("opus", "").strip().capitalize()
    if opus:
        if opus not in book_kinds.OPUS_TYPES or book.type != "Tractatus":
            raise ValueError(f"opus {opus!r} isn't a kind of tractatus")
        book.opus = opus
    form = row.get("physical_form", "").strip()
    if form:
        known = {k.lower(): k for k in book_kinds.PHYSICAL_FORMS}
        if form.lower() not in known:
            raise ValueError(f"unknown physical form {form!r}")
        book.physical_form = known[form.lower()]


def parse_books_csv(text: str) -> CsvImport:
    """Read books from CSV text with a header row (column names in any case
    and order; see CSV_COLUMNS). Raises ValueError if there's no `name` or
    `type` column; a bad row is skipped and reported, not fatal."""
    encyclopedias: set[str] = set()

    def from_row(row: dict[str, str]) -> Book:
        book = _book_from_row(row)
        flag = row.get("encyclopedia", "").strip().lower()
        if book.codex_id and flag in ("yes", "y", "true", "1", "x"):
            encyclopedias.add(book.codex_id)
        return book

    books, skipped, unused = parse_rows(
        text, ("name", "type"), CSV_COLUMNS, from_row, missing_joiner=" or "
    )
    return CsvImport(books, skipped, unused, encyclopedias)


def read_books_csv(path: Path) -> CsvImport:
    """parse_books_csv on a file: UTF-8 (with or without Excel's byte-order
    mark), falling back to Windows-1252 for older spreadsheets."""
    return parse_books_csv(read_text_any(path))


def duplicate_names[T: Book | Spell](
    books: list[T], existing_names: set[str], key: Callable[[str], str] = str
) -> list[T]:
    """The books (or spells) whose name is already taken: by one in the saga,
    or by one earlier in `books` (a file listing the same title twice). Names
    are compared by `key` (spells use `spells.name_key`: any case)."""
    seen = {key(name) for name in existing_names}
    repeats = []
    for book in books:
        if key(book.name) in seen:
            repeats.append(book)
        seen.add(key(book.name))
    return repeats


def import_preview(
    result: CsvImport, file_name: str, destination: str, existing_names: set[str]
) -> str:
    """The confirmation shown before importing (markup): how many books go
    where (`destination`, e.g. "into Dammerstein's library"), and anything
    worth knowing first."""
    count = len(result.books)
    lines = [
        f"Import {count} book{'s' if count != 1 else ''} from "
        f"[b]{escape(file_name)}[/] {escape(destination)}?"
    ]
    unused = [c for c in result.unused_columns if c in CSV_UNUSED_COLUMNS]
    if unused:
        plural = "s" if len(unused) > 1 else ""
        lines.append(
            f"[dim]Not used: the {' and '.join(unused)} column{plural} (where "
            "imported books go is set by the import; cost is calculated).[/]"
        )
    unknown = [c for c in result.unused_columns if c not in CSV_UNUSED_COLUMNS]
    if unknown:
        lines.append(
            f"[dim]Unrecognised columns ignored: {escape(', '.join(unknown))}.[/]"
        )
    bound = {b.codex_id for b in result.books if b.codex_id}
    if bound:
        lines.append(
            f"{len(bound)} codex{'es' if len(bound) != 1 else ''}: the books "
            "sharing a codex name are bound together."
        )
    repeats = len(duplicate_names(result.books, existing_names))
    if repeats:
        verb = "has" if repeats == 1 else "have"
        lines.append(
            f"{repeats} {verb} the same name as another book; you'll be asked "
            "whether to add or skip each."
        )
    to_set = sum(1 for b in result.books if numbers_to_set(b))
    if to_set:
        verb = "has" if to_set == 1 else "have"
        lines.append(
            f'{to_set} {verb} a Level or Quality to be set ("var"): imported, '
            "highlighted until you give them their numbers."
        )
    unknown_abilities = sum(
        1 for b in result.books if status_problems(b) and not numbers_to_set(b)
    )
    if unknown_abilities:
        verb = "names" if unknown_abilities == 1 else "name"
        lines.append(
            problem(f"{unknown_abilities} {verb} an unknown ability") + " (imported, "
            "highlighted to fix)."
        )
    over = sum(1 for b in result.books if limit_warnings(b))
    if over:
        verb = "goes" if over == 1 else "go"
        lines.append(
            f"{over} {verb} over covenant-creation limits (flagged on the book, "
            "not blocked)."
        )
    lines += skipped_preview(result.skipped)
    return "\n".join(lines)


# ------------------------------------------------------------------ adding


def add_book(saga: Saga, name: str, book_type: str) -> Book:
    """A new book, added to `saga.books` with no owner."""
    book = Book(
        id=storage.generate_unique_id(name, [b.id for b in saga.books]),
        name=name,
        type=book_type,
    )
    saga.books.append(book)
    return book


def add_imported_books(
    saga: Saga,
    books: list[Book],
    covenant: Covenant | None,
    encyclopedias: set[str] | None = None,
) -> None:
    """Add imported books: each gets an id, is linked to its spell now that
    the spell can be matched by name, and goes to `covenant` if one is given
    (otherwise it stays unassigned). Books whose `codex` column named the
    same codex are bound in one new codex of that name (an encyclopedia when
    its name is in `encyclopedias`)."""
    ids = [b.id for b in saga.books]
    codices: dict[str, Codex] = {}
    for book in books:
        if book.codex_id:
            name = book.codex_id
            if name not in codices:
                codices[name] = new_codex(saga, name)
                codices[name].encyclopedia = name in (encyclopedias or set())
            book.codex_id = codices[name].id
        spell = book_spell(saga, book)
        if spell is not None:
            book.spell_id = spell.id
        book.id = storage.generate_unique_id(book.name, ids)
        ids.append(book.id)
        if covenant is not None:
            book.owner_kind, book.owner_id = "covenant", covenant.id
        saga.books.append(book)


def form_problem(values: dict[str, Any]) -> str | None:
    """What's wrong with a book form's values, if anything."""
    if records_spell(
        values.get("type") or "", values.get("text_kind") or ""
    ) and not values.get("spell_id"):
        return "Choose the spell (use the Spells view to add one of your own)."
    ability = values.get("ability") or ""
    if "{" in ability and not values.get("ability_detail"):
        return f"{ability} needs its Ability detail filled in."
    for key in ("level", "quality"):
        if (values.get(key) or 0) < 0:
            return f"{key.capitalize()} can't be negative."
    return None


# ------------------------------------------------- buying a book at creation


def creation_refusals(saga: Saga, book: Book, max_level: int | None) -> list[str]:
    """Why a new covenant can't buy `book` with Build Points (plain text;
    none: it can): the creation limits on summae and tractatus, and for a
    Lab Text or Casting Tablet its Power Level's highest level
    (`max_level`, None: no limit)."""
    reasons = limit_warnings(book)
    if book.type in SPELL_TYPES and max_level is not None:
        level = level_of(book, saga) or 0
        if level > max_level:
            reasons.append(
                f"Level {level} is over the Power Level's limit of {max_level}."
            )
    return reasons


def copy_to(saga: Saga, book: Book, owner_kind: str, owner_id: str) -> Book:
    """A copy of `book` for a new owner (the original stays where it is),
    on its own: not bound into the original's codex."""
    copy = replace(
        book,
        id=storage.generate_unique_id(book.name, [b.id for b in saga.books]),
        owner_kind=owner_kind,
        owner_id=owner_id,
        codex_id=None,
    )
    saga.books.append(copy)
    return copy
