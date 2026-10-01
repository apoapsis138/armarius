"""Logic behind books and the covenant Library tab -- no UI in here.

Build Point costs and covenant-creation limits (reference/Libraries.md), who
owns a book, which books a covenant's Library lists, the text for list rows
and the details panel, and reading books from a CSV file.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from . import catalog, storage
from . import spells as spl
from .arts import ART_LOOKUP
from .csv_import import parse_rows, read_text_any, skipped_preview
from .markup import escape, fit, markdown_inline
from .models import (
    BOOK_TYPES,
    Book,
    Character,
    Covenant,
    Saga,
    Spell,
    round_away_from_zero,
)

#: Book types whose subject is an Art / an Ability (a Tractatus depends on its
#: `subject_kind`).
SUMMA_TYPES: tuple[str, ...] = ("Art Summa", "Ability Summa")
#: Book types that record a spell (name + level) instead of an Art or Ability.
SPELL_TYPES: tuple[str, ...] = ("Lab Text", "Casting Tablet")


def is_art_book(book_type: str, subject_kind: str = "") -> bool:
    return book_type == "Art Summa" or (
        book_type == "Tractatus" and subject_kind == "Art"
    )


def is_ability_book(book_type: str, subject_kind: str = "") -> bool:
    return book_type == "Ability Summa" or (
        book_type == "Tractatus" and subject_kind == "Ability"
    )


def has_level(book_type: str) -> bool:
    return book_type in SUMMA_TYPES or book_type in SPELL_TYPES


def has_quality(book_type: str) -> bool:
    return book_type in SUMMA_TYPES or book_type == "Tractatus"


# ------------------------------------------------------- the linked spell


def book_spell(saga: Saga, book: Book) -> Spell | None:
    """A Lab Text's or Casting Tablet's spell: the one its `spell_id` names,
    else the one its typed `spell_name` matches (how imported books link).
    None for other books, or when nothing matches."""
    if book.type not in SPELL_TYPES:
        return None
    if book.spell_id:
        found = spl.find_spell(saga, book.spell_id)
        if found is not None:
            return found
    return spl.find_spell_by_name(saga, book.spell_name)


def level_of(book: Book, saga: Saga | None = None) -> int | None:
    """The book's Level. A Lab Text's or Casting Tablet's is its spell's,
    unless the spell is General-level (or unknown), when the book's own
    `level` counts. Without a saga the stored level is all there is."""
    if saga is not None and book.type in SPELL_TYPES:
        spell = book_spell(saga, book)
        if spell is not None and spell.level is not None:
            return spell.level
    return book.level


# ------------------------------------------------------------------- rules


def cost(book: Book, saga: Saga | None = None) -> int:
    """Build Points the book costs at covenant creation. A blank level or
    quality counts as 0; Other books cost nothing. Given the saga, a Lab
    Text or Casting Tablet uses its spell's level (see level_of)."""
    level = level_of(book, saga) or 0
    quality = book.quality or 0
    if book.type == "Art Summa":
        return level + quality
    if book.type == "Ability Summa":
        return quality + 3 * level
    if book.type == "Tractatus":
        return quality
    if book.type == "Lab Text":
        return round_away_from_zero(level / 5)
    if book.type == "Casting Tablet":
        return round_away_from_zero(2 * level / 5)
    return 0


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
    quality = book.quality or 0
    if book.type == "Art Summa":
        return f"Level {level} + Quality {quality}"
    if book.type == "Ability Summa":
        return f"Quality {quality} + 3 x Level {level}"
    if book.type == "Tractatus":
        return f"Quality {quality}"
    if book.type == "Lab Text":
        return f"1 per 5 levels of a level {level} spell, rounded up"
    if book.type == "Casting Tablet":
        return f"2 per 5 levels of a level {level} spell, rounded up"
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
    or Casting Tablet whose spell can't be found."""
    if (
        is_ability_book(book.type, book.subject_kind)
        and book.ability
        and canonical_ability(book.ability) is None
    ):
        return [
            f"Unknown ability: {book.ability!r} isn't in the ability list; "
            "edit the book to choose one."
        ]
    if saga is not None and book.type in SPELL_TYPES and book_spell(saga, book) is None:
        named = (
            f"{book.spell_name!r} isn't in the spell list"
            if book.spell_name
            else "no spell chosen"
        )
        return [f"Unknown spell: {named}; edit the book to choose one."]
    return []


# ------------------------------------------------------------------ owners


def owner_record(saga: Saga, book: Book):
    """The covenant, laboratory or character that owns the book, or None
    (unowned, or the owner no longer exists)."""
    records = {
        "covenant": saga.covenants,
        "laboratory": saga.laboratories,
        "character": saga.characters,
    }.get(book.owner_kind or "", [])
    return next((r for r in records if r.id == book.owner_id), None)


def is_unassigned(saga: Saga, book: Book) -> bool:
    return owner_record(saga, book) is None


def unassigned_books(saga: Saga) -> list[Book]:
    """Books filed under the saga: no owner, or one that no longer exists."""
    return [b for b in saga.books if is_unassigned(saga, b)]


def books_owned_by(saga: Saga, kind: str, owner_id: str) -> list[Book]:
    return [b for b in saga.books if b.owner_kind == kind and b.owner_id == owner_id]


def covenant_of(saga: Saga, book: Book) -> str | None:
    """The id of the covenant the book is kept in: its owner, or the covenant
    of the laboratory or character that owns it."""
    owner = owner_record(saga, book)
    if owner is None:
        return None
    if book.owner_kind == "covenant":
        return owner.id
    return owner.covenant_id


def can_read(saga: Saga, character: Character, book: Book) -> bool:
    """Whether `character` may study `book` (STORY-902, Hedda 2026-09-29): a
    book in the covenant's library (owned by the covenant) is open to
    everyone of that covenant; a book someone keeps (in their inventory, or
    in their laboratory) only to them. A book with no owner is in nobody's
    library."""
    owner = owner_record(saga, book)
    if owner is None:
        return False
    if book.owner_kind == "covenant":
        return character.covenant_id == owner.id
    if book.owner_kind == "laboratory":
        return owner.owner_id == character.id
    return owner.id == character.id


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


def books_in_covenant(saga: Saga, covenant: Covenant) -> list[Book]:
    """Everything the covenant's Library lists: books it owns, and books owned
    by its laboratories and characters, in the order added."""
    return [b for b in saga.books if covenant_of(saga, b) == covenant.id]


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


# -------------------------------------------------------------------- text


def subject(book: Book, saga: Saga | None = None) -> str:
    """The Art, Ability or spell the book is about ("" if not set)."""
    if book.type in SPELL_TYPES:
        spell = book_spell(saga, book) if saga is not None else None
        return spell.name if spell is not None else book.spell_name
    if is_art_book(book.type, book.subject_kind):
        return book.art
    if is_ability_book(book.type, book.subject_kind):
        return book.ability
    return ""


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
SUBJECT_MIN_WIDTH = 17
SUBJECT_MAX_WIDTH = 40
#: Everything in a row but the Subject column: the columns, their spacing,
#: and room for a scrollbar.
_ROW_WIDTH_WITHOUT_SUBJECT = (
    (_NAME_WIDTH + 1 + _TYPE_WIDTH + 1 + 1 + _LEVEL_WIDTH + _QUALITY_WIDTH + 2)
    + _LOCATION_WIDTH
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
        f"{escape(fit(book.name or '(untitled)', _NAME_WIDTH))} "
        f"{escape(fit(book.type, _TYPE_WIDTH))} "
        f"{escape(fit(subject(book, saga) or '-', subject_cols))} "
        f"{_number(level_of(book, saga)):>{_LEVEL_WIDTH}}"
        f"{_number(book.quality):>{_QUALITY_WIDTH}}  "
        f"{escape(location)}"
    )
    return f"[$text-error]{row}[/]" if status_problems(book, saga) else row


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


def summary_texts(books: list[Book], saga: Saga | None = None) -> tuple[str, str]:
    """The Library tab's Summary (markup, read-only): Summae and Tractatus by
    Ability/Art down the left; Lab Texts, Casting Tablets, Other and the
    totals down the right."""

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

    left = rows(
        [
            ("Summae", ability_summae + art_summae),
            ("  • Ability", ability_summae),
            ("  • Art", art_summae),
            ("", ""),
            ("Tractatus", count("Tractatus")),
            ("  • Ability", ability_tracts),
            ("  • Art", art_tracts),
        ]
    )
    right = rows(
        [
            ("Lab Texts", count("Lab Text")),
            ("Casting Tablets", count("Casting Tablet")),
            ("Other", count("Other")),
            ("", ""),
            ("Total Books", len(books)),
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
        _cell("Quality", _number(book.quality)),
    ]
    right = [
        _cell("Language", book.language or not_set),
        _cell("Author", book.author or "(unknown)"),
        _cell("Year Published", year),
        _cell("Owner", owner_label(saga, book)),
    ]
    width = max(w for _, w in left) + 4
    lines = [f"[$text-error][b]{escape(p)}[/b][/]" for p in status_problems(book, saga)]
    lines.append(_cell("Name", book.name or "(untitled)")[0])
    lines += [f"{lm}{' ' * (width - lw)}{rm}" for (lm, lw), (rm, _) in zip(left, right)]
    if priced(saga, book):
        # Build Points matter only while its covenant is being created
        # (STORY-1314); in play they're on the covenant's Build tab.
        lines.append(
            _cell(
                "Cost",
                f"{cost(book, saga)} Build Points ({cost_formula(book, saga)})",
            )[0]
        )
        lines += [f"[$text-error]{escape(w)}[/]" for w in limit_warnings(book)]
    lines += _study_lines(saga, book)
    if book.description.strip():
        lines += ["", "[b]Description:[/]", markdown_inline(book.description.strip())]
    return "\n".join(lines)


def _study_lines(saga: Saga, book: Book) -> list[str]:
    """What a season reading the book gives each magus and companion of
    its covenant (rules.study, STORY-803): nothing for a book that isn't a
    summa or tractatus."""
    from .rules import study

    results = [(c, study.reading(c, book)) for c in readers(saga, book)]
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
    if has_level(book_type):
        book.level = _whole_number(row.get("level", ""), "Level")
        # A Lab Text or Casting Tablet can take its Level from its spell.
        if book.level is None and book_type not in SPELL_TYPES:
            raise ValueError("no Level")
    if has_quality(book_type):
        book.quality = _whole_number(row.get("quality", ""), "Quality")
        if book.quality is None:
            raise ValueError("no Quality")
    if (book.level or 0) < 0 or (book.quality or 0) < 0:
        raise ValueError("a negative Level or Quality")
    return book


def parse_books_csv(text: str) -> CsvImport:
    """Read books from CSV text with a header row (column names in any case
    and order; see CSV_COLUMNS). Raises ValueError if there's no `name` or
    `type` column; a bad row is skipped and reported, not fatal."""
    books, skipped, unused = parse_rows(
        text, ("name", "type"), CSV_COLUMNS, _book_from_row, missing_joiner=" or "
    )
    return CsvImport(books, skipped, unused)


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
    repeats = len(duplicate_names(result.books, existing_names))
    if repeats:
        verb = "has" if repeats == 1 else "have"
        lines.append(
            f"{repeats} {verb} the same name as another book; you'll be asked "
            "whether to add or skip each."
        )
    unknown_abilities = sum(1 for b in result.books if status_problems(b))
    if unknown_abilities:
        verb = "names" if unknown_abilities == 1 else "name"
        lines.append(
            f"[$text-error]{unknown_abilities} {verb} an unknown ability[/] (imported, "
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
    saga: Saga, books: list[Book], covenant: Covenant | None
) -> None:
    """Add imported books: each gets an id, is linked to its spell now that
    the spell can be matched by name, and goes to `covenant` if one is given
    (otherwise it stays unassigned)."""
    ids = [b.id for b in saga.books]
    for book in books:
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
    if values.get("type") in SPELL_TYPES and not values.get("spell_id"):
        return "Choose the spell (use the Spells view to add one of your own)."
    ability = values.get("ability") or ""
    if "{" in ability and not values.get("ability_detail"):
        return f"{ability} needs its Ability detail filled in."
    for key in ("level", "quality"):
        if (values.get(key) or 0) < 0:
            return f"{key.capitalize()} can't be negative."
    return None
