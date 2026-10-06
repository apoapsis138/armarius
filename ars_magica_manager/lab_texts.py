"""The Lab Texts database: a laboratory's Lab Texts as a table
that can be filtered, with what each one records and how it stands for one
reader (the laboratory's owner).

A Lab Text is a Book of type "Lab Text" with a kind (models.LAB_TEXT_KINDS).
A spell's text takes its Technique, Form and level from the spell; any other
kind carries its own, with a snapshot of the effect taken when it was
written. Whether a reader can use a raw text is the reader's
(Character.lab_text_access); this module only shows it:

- General use: rewritten by its author, or never raw.
- Own raw text: the reader wrote it.
- Readable: the reader decoded the author's texts, or was taught his
  abbreviations, to at least its level.
- Not decoded: anything else, with the points of a decoding under way.

Copying is the Copy Lab Texts season (Profession: Scribe x 60 levels); the
Copy column only says what share of a season one copy takes.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import books as bk
from .arts import ART_ABBREVIATIONS
from .markup import escape, fit, markdown_inline
from .models import (
    LAB_TEXT_KINDS,
    TEXT_ENCHANTMENT,
    TEXT_LONGEVITY,
    TEXT_OTHER,
    TEXT_SPELL,
    Book,
    Character,
    Saga,
)
from .rules import book_seasons as bs
from .rules import lab_seasons

LAB_TEXT = "Lab Text"

#: A kind as the table's Kind column shows it.
KIND_SHORT: dict[str, str] = {
    TEXT_SPELL: "Spell",
    TEXT_ENCHANTMENT: "Enchant.",
    TEXT_LONGEVITY: "Longevity",
    TEXT_OTHER: "Other",
}

USING_RULE = (
    "[dim]Using a Lab Text: the effect is reproduced in one season if the Lab "
    "Total is at least its level; several texts of one Technique and Form in "
    "a season if their levels add up to no more than the Lab Total.[/]"
)


def is_lab_text(book: Book) -> bool:
    return book.type == LAB_TEXT


def kind(book: Book) -> str:
    """The text's kind (a text from before kinds existed counts by whether
    it names a spell)."""
    if book.text_kind in LAB_TEXT_KINDS:
        return book.text_kind
    return TEXT_SPELL if book.spell_id or book.spell_name else TEXT_OTHER


def texts_of(saga: Saga, owner_kind: str, owner_id: str) -> list[Book]:
    """The Lab Texts an owner keeps, in the saga's order."""
    return [b for b in bk.books_owned_by(saga, owner_kind, owner_id) if is_lab_text(b)]


def other_books_of(saga: Saga, owner_kind: str, owner_id: str) -> list[Book]:
    """The owner's books that aren't Lab Texts."""
    return [
        b for b in bk.books_owned_by(saga, owner_kind, owner_id) if not is_lab_text(b)
    ]


def arts(saga: Saga, book: Book) -> tuple[str, str]:
    """The text's Technique and Form ("" for one not recorded)."""
    return bs.decode_total_arts(saga, book) or (book.technique, book.form)


def level(saga: Saga, book: Book) -> int:
    return bs.text_level(book, saga)


def sigil(saga: Saga, book: Book) -> str:
    """The author's Wizard's Sigil: a character of the saga's; "" for an
    author outside it."""
    author = saga.character(book.author_id)
    return author.hermetic.wizards_sigil.strip() if author is not None else ""


# ------------------------------------------------------------------ status


READABLE, OWN, GENERAL, UNREAD = "Readable", "Own raw", "General use", "Not decoded"


def can_use(reader: Character | None, book: Book) -> bool:
    """Whether `reader` can use the text's writing (anyone can, with no
    reader to ask about)."""
    return reader is None or bs.can_use_lab_text(reader, book)


def short_status(reader: Character | None, book: Book) -> str:
    """The Status column: one of the four states."""
    if not book.raw:
        return GENERAL
    if reader is None:
        return "Raw"
    if book.author_id == reader.id:
        return OWN
    return READABLE if bs.can_use_lab_text(reader, book) else UNREAD


def status(saga: Saga, reader: Character | None, book: Book) -> str:
    """How the text stands for `reader`, in full."""
    state = short_status(reader, book)
    if reader is None or state in (GENERAL, OWN):
        return {GENERAL: "General use", OWN: "Own raw text"}.get(state, "Raw text")
    author = bs.author_key(book)
    access = reader.lab_text_access.get(author)
    reads = access.level if access is not None else 0
    if state == READABLE:
        how = access.via if access is not None and access.via else "reads"
        return f"Readable ({how} to {reads})"
    points = lab_seasons.project_points_key(
        saga, lab_seasons.decode_key(reader, author)
    )
    if points:
        return f"Not decoded ({max(points, reads)} of {level(saga, book)} points)"
    if reads:
        via = access.via if access is not None and access.via else "reads"
        return f"Not decoded ({via} to {reads})"
    return "Not decoded"


def cant_read_tag(saga: Saga, reader: Character, book: Book) -> str:
    """What a picker adds to a text the reader can't use yet: "" for one he
    can, else " (can't read: decode first)" or " (can't read: decoded to
    15)"."""
    if bs.can_use_lab_text(reader, book):
        return ""
    access = reader.lab_text_access.get(bs.author_key(book))
    if access is not None and access.level:
        return f" (can't read: {access.via or 'reads'} to {access.level})"
    return " (can't read: decode first)"


def copy_text(saga: Saga, reader: Character | None, book: Book) -> str:
    """What one copy costs `reader`, as a share of a Copy Lab Texts season
    (Profession: Scribe x 60 levels): "Copy 1/3 season (20 of 60 levels)"."""
    if reader is None:
        return ""
    if not bs.can_use_lab_text(reader, book):
        return "Copy: decode first"
    budget = 60 * bs.ability_score(reader, "Profession: Scribe")
    if budget <= 0:
        return "Copy: needs Profession: Scribe"
    size = max(1, level(saga, book))
    share = budget // size
    if share < 1:
        return f"Copy: too long for a season ({size} of {budget} levels)"
    season = "1 season" if share == 1 else f"1/{share} season"
    return f"Copy {season} ({size} of {budget} levels)"


def short_copy(saga: Saga, reader: Character | None, book: Book) -> str:
    """The Copy column: "1/3 season", "decode 1st", "-"."""
    text = copy_text(saga, reader, book)
    if text.startswith("Copy 1"):
        return text.split(" (")[0].removeprefix("Copy ")
    if "decode" in text:
        return "decode 1st"
    return "-"


# ------------------------------------------------------------------ filter


@dataclass(frozen=True)
class Filter:
    """What the table is narrowed to ("" / None: anything)."""

    kind: str = ""
    technique: str = ""
    form: str = ""
    min_level: int | None = None
    max_level: int | None = None
    readable: bool = False

    @property
    def active(self) -> bool:
        return self != Filter()

    def describe(self) -> str:
        """ "Spell, Creo, level 10-25, readable" ("" when nothing is set)."""
        parts = [p for p in (self.kind, self.technique, self.form) if p]
        if self.min_level is not None and self.max_level is not None:
            parts.append(f"level {self.min_level}-{self.max_level}")
        elif self.min_level is not None:
            parts.append(f"level {self.min_level}+")
        elif self.max_level is not None:
            parts.append(f"level up to {self.max_level}")
        if self.readable:
            parts.append("readable")
        return ", ".join(parts)


def filter_problem(wanted: Filter) -> str | None:
    if (
        wanted.min_level is not None
        and wanted.max_level is not None
        and wanted.min_level > wanted.max_level
    ):
        return "The lowest level is above the highest."
    return None


def matches(saga: Saga, reader: Character | None, book: Book, wanted: Filter) -> bool:
    technique, form = arts(saga, book)
    size = level(saga, book)
    return (
        (not wanted.kind or kind(book) == wanted.kind)
        and (not wanted.technique or technique == wanted.technique)
        and (not wanted.form or form == wanted.form)
        and (wanted.min_level is None or size >= wanted.min_level)
        and (wanted.max_level is None or size <= wanted.max_level)
        and (not wanted.readable or can_use(reader, book))
    )


def filtered(
    saga: Saga, reader: Character | None, texts: list[Book], wanted: Filter
) -> list[Book]:
    return [b for b in texts if matches(saga, reader, b, wanted)]


def title(shown: int, total: int, wanted: Filter) -> str:
    """The section's title: "Lab Texts (7)", or "Lab Texts (3 of 7: Spell,
    readable)" while filtered."""
    if not wanted.active:
        return f"Lab Texts ({total})"
    return f"Lab Texts ({shown} of {total}: {wanted.describe()})"


# ------------------------------------------------------------------- table


NAME_MIN_WIDTH = 14
NAME_MAX_WIDTH = 34
_KIND_WIDTH = 9
_ART_WIDTH = 2
_LEVEL_WIDTH = 3
_AUTHOR_WIDTH = 12
_SIGIL_WIDTH = 10
_STATUS_WIDTH = 11
_COPY_WIDTH = 10
#: Everything in a row but the Name and Sigil columns, with its spacing
#: and room for a scrollbar.
_ROW_WIDTH_WITHOUT_NAME = (
    (1 + _KIND_WIDTH)
    + 2 * (1 + _ART_WIDTH)
    + (1 + _LEVEL_WIDTH)
    + (1 + _AUTHOR_WIDTH)
    + (1 + _STATUS_WIDTH)
    + (1 + _COPY_WIDTH)
    + 2
)


@dataclass(frozen=True)
class Columns:
    """How the table is laid out in the room it has: the Name column's
    width, and whether the Sigil column fits (the details panel always
    shows the Sigil)."""

    name: int = NAME_MIN_WIDTH
    sigil: bool = True


DEFAULT_COLUMNS = Columns()


def columns(row_width: int) -> Columns:
    """The layout for a row `row_width` characters wide (after the list's
    markers): the Sigil column is dropped before the Name gets shorter than
    its least."""
    spare = row_width - _ROW_WIDTH_WITHOUT_NAME
    sigil = spare - (1 + _SIGIL_WIDTH) >= NAME_MIN_WIDTH
    if sigil:
        spare -= 1 + _SIGIL_WIDTH
    return Columns(max(NAME_MIN_WIDTH, min(NAME_MAX_WIDTH, spare)), sigil)


def table_header(layout: Columns = DEFAULT_COLUMNS) -> str:
    """The column titles; the two-character indent is the selector marker."""
    sigil = f"{'Sigil':<{_SIGIL_WIDTH}} " if layout.sigil else ""
    return (
        f"  {'Name':<{layout.name}} {'Kind':<{_KIND_WIDTH}} "
        f"{'Te':<{_ART_WIDTH}} {'Fo':<{_ART_WIDTH}} {'Lvl':>{_LEVEL_WIDTH}} "
        f"{'Author':<{_AUTHOR_WIDTH}} {sigil}"
        f"{'Status':<{_STATUS_WIDTH}} Copy"
    )


def _short_name(book: Book) -> str:
    """The name without the "Lab Text: " every written text starts with (the
    whole table is Lab Texts)."""
    return book.name.removeprefix("Lab Text: ") or "(untitled)"


def row_label(
    saga: Saga, reader: Character | None, book: Book, layout: Columns = DEFAULT_COLUMNS
) -> str:
    """One row (markup), lined up with `table_header`; dim for a text the
    reader can't use yet."""
    technique, form = arts(saga, book)
    mark = (
        f"{escape(fit(sigil(saga, book) or '-', _SIGIL_WIDTH))} "
        if layout.sigil
        else ""
    )
    row = (
        f"{escape(fit(_short_name(book), layout.name))} "
        f"{KIND_SHORT[kind(book)]:<{_KIND_WIDTH}} "
        f"{ART_ABBREVIATIONS.get(technique, '-'):<{_ART_WIDTH}} "
        f"{ART_ABBREVIATIONS.get(form, '-'):<{_ART_WIDTH}} "
        f"{level(saga, book):>{_LEVEL_WIDTH}} "
        f"{escape(fit(bs.author_name(saga, book) or '-', _AUTHOR_WIDTH))} "
        f"{mark}"
        f"{short_status(reader, book):<{_STATUS_WIDTH}} "
        f"{short_copy(saga, reader, book)}"
    ).rstrip()
    return row if can_use(reader, book) else f"[dim]{row}[/]"


def detail_text(saga: Saga, reader: Character | None, book: Book | None) -> str:
    """The details panel (markup) for a chosen text: what it records, its
    author and sigil, how it stands for the reader, and the rule for using
    one."""
    if book is None:
        return "[dim]Select a Lab Text to see its details.[/]\n" + USING_RULE
    technique, form = arts(saga, book)
    spell = bk.book_spell(saga, book)
    what = kind(book)
    if spell is not None:
        what = f"{what}: {spell.name}"
    elif book.spell_name:
        what = f"{what}: {book.spell_name}"
    head = [
        f"[b]{escape(book.name or '(untitled)')}[/]",
        f"[b]Kind:[/] {escape(what)}   [b]Arts:[/] "
        f"{escape(technique or '(not set)')} {escape(form or '(not set)')}   "
        f"[b]Level:[/] {level(saga, book)}",
    ]
    extra = [
        (label, value)
        for label, value in (
            ("Range / Duration / Target", book.effect_rdt),
            ("Device", book.device_type),
            ("Shape and material", book.shape_material),
            ("Subject", book.ritual_subject),
            (
                "Extra vis each time",
                str(book.ritual_extra_vis) if book.ritual_extra_vis else "",
            ),
        )
        if value
    ]
    if extra:
        head.append(
            "   ".join(f"[b]{label}:[/] {escape(value)}" for label, value in extra)
        )
    author = bs.author_name(saga, book) or "(unknown)"
    mark = sigil(saga, book)
    head.append(
        f"[b]Author:[/] {escape(author)}"
        + (f"   [b]Sigil:[/] {escape(mark)}" if mark else "")
        + (
            f"   [b]Written:[/] {book.year_published}"
            if book.year_published is not None
            else ""
        )
    )
    who = f" for {escape(reader.name)}" if reader is not None else ""
    standing = f"[b]Status{who}:[/] {escape(status(saga, reader, book))}"
    copying = copy_text(saga, reader, book)
    if copying:
        standing += f"   {escape(copying)}"
    head.append(standing)
    if book.description.strip():
        head.append(markdown_inline(book.description.strip()))
    head.append(USING_RULE)
    return "\n".join(head)


# ------------------------------------------------- a reader's access, shown


def access_rows(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """Whose raw Lab Texts `character` reads, as (author key, "Jacobus of
    Tytalus to 20 (decoded)"), by author name."""
    rows = []
    for author, access in character.lab_text_access.items():
        linked = saga.character(author)
        name = linked.name if linked is not None else author
        how = f" ({access.via})" if access.via else ""
        rows.append((author, f"{name} to {access.level}{how}"))
    return sorted(rows, key=lambda row: row[1].lower())


def access_text(saga: Saga, character: Character) -> str:
    """The Hermetic Background lines (markup) under Wizard's Sigil."""
    rows = access_rows(saga, character)
    if not rows:
        return "Reads Lab Texts of: (no one else's)"
    return "Reads Lab Texts of:\n" + "\n".join(
        f"  {escape(label)}" for _, label in rows
    )


def author_options(saga: Saga, character: Character) -> list[tuple[str, str]]:
    """The saga's other magi as (name, id): whose texts access can be set
    for by choosing (an author outside the saga is typed)."""
    return [
        (c.name, c.id)
        for c in saga.characters
        if c.type == "magus" and c.id != character.id
    ]
