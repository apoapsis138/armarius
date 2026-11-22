"""A covenant's library in one subject, read as a whole -- no UI in here.

- The **Holding**: with the Large Library rule (Transforming Mythic Europe,
  Rules for a Large Library, p. 105) the shared library's Level and Quality
  in the subject, from its best summa raised by the books near it; without
  it, the best summa's own Level and Quality.
- What each book does in it (`roles`): the rule's roles
  (`tme_books.ROLE_*`) for the shared library's books, and `KEPT` for one
  a magus keeps, or keeps in a laboratory, which isn't in it.
- The subject's research bonus (book_value).

The book inspector and the Library's subjects both draw from this.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import book_value as bv
from . import settings
from .arts import ARTS
from .markup import escape, fit
from .models import Book, Covenant, Saga
from .rules import activities, tme_books
from .rules import options as rule_options
from .rules.library import SUMMA_TYPES, books_in_covenant, covenant_of, owner_record
from .tables import Table

SOURCE = "Transforming Mythic Europe, Rules for a Large Library, p. 105"

#: A book's role when a magus keeps it, or keeps it in a laboratory.
KEPT = "kept"


@dataclass(frozen=True)
class Holding:
    """The covenant's library in one subject ("art:Vim")."""

    covenant: Covenant
    subject: str
    name: str  # the Art or Ability, as a book names it ("Vim")
    large_library: bool  # the rule is on, so the books add up
    best: Book | None  # the best summa in the shared library
    level: int | None  # None: no summa, no Holding
    quality: int | None
    books: list[Book]  # every book on it at the covenant, kept ones too
    roles: dict[str, str]  # book id to role (tme_books.ROLE_* or KEPT)
    research: str  # the research bonus as text ("" for none)
    research_level: int  # the library's own bonus (book_value.library_level)

    @property
    def kind(self) -> str:
        """ "art", "ability" or "mastery": the subject key's kind."""
        return self.subject.split(":", 1)[0]

    def shared(self) -> list[Book]:
        return [b for b in self.books if self.roles.get(b.id) != KEPT]

    def kept(self) -> list[Book]:
        return [b for b in self.books if self.roles.get(b.id) == KEPT]

    def figures(self) -> str:
        """ "Level 14, Quality 11", or "none: the library has no summa on it"."""
        if self.level is None:
            return "none: the library has no summa on it"
        return f"Level {self.level}, Quality {self.quality}"


def subject_holding(
    saga: Saga, covenant: Covenant, subject: str, books: list[Book] | None = None
) -> Holding:
    """The covenant's library in `subject` (activities.book_subject's key);
    `books`: every book on it at the covenant, when already gathered."""
    if books is None:
        books = [
            b
            for b in books_in_covenant(saga, covenant)
            if activities.book_subject(b) == subject
        ]
    on = rule_options.is_on(saga, rule_options.LARGE_LIBRARY)
    shared = [b for b in books if b.owner_kind == "covenant"]
    roles = {b.id: KEPT for b in books if b.owner_kind != "covenant"}
    best: Book | None = None
    level = quality = None
    if on:
        score = tme_books.library_score(shared)
        if score is not None:
            best = next(b for b in shared if b.id == score.best)
            level, quality = score.level, score.quality
            roles |= score.roles
    else:
        summae = [b for b in shared if b.type in SUMMA_TYPES]
        if summae:
            best = max(
                summae,
                key=lambda b: ((b.level or 0) + (b.quality or 0), b.quality or 0),
            )
            level, quality = best.level, best.quality
    name = bv.subject_of(books[0]) if books else ""
    research_level = bv.library_level(saga, covenant, name) if name else 0
    research = (
        bv.subject_research_text(saga, covenant, name, research_level) if name else ""
    )
    return Holding(
        covenant,
        subject,
        name,
        on,
        best,
        level,
        quality,
        books,
        roles,
        research,
        research_level,
    )


#: The kinds of subject, in the order the Library lists them, by key prefix.
_KINDS: dict[str, str] = {"art": "Arts", "ability": "Abilities", "mastery": "Mastery"}


def _order(holding: Holding) -> tuple[int, int, str]:
    """Arts in Hermetic order (Techniques, then Forms), then Abilities and
    Mastery books by name."""
    kind = holding.kind
    rank = list(_KINDS).index(kind) if kind in _KINDS else len(_KINDS)
    art = ARTS.index(holding.name) if kind == "art" and holding.name in ARTS else 0
    return rank, art, holding.name.lower()


def holdings(saga: Saga, covenant: Covenant) -> list[Holding]:
    """Every subject the covenant's summae and tractatus are on, kept books
    included, in the Library's order (_order). The books are gathered by
    subject in one pass."""
    by_subject: dict[str, list[Book]] = {}
    for book in books_in_covenant(saga, covenant):
        subject = activities.book_subject(book)
        if subject is not None:
            by_subject.setdefault(subject, []).append(book)
    return sorted(
        (subject_holding(saga, covenant, s, b) for s, b in by_subject.items()),
        key=_order,
    )


def _plural(count: int, one: str, many: str) -> str:
    return f"{count} {one if count == 1 else many}"


def _books_cell(holding: Holding) -> str:
    shared = holding.shared()
    summae = sum(1 for b in shared if b.type in SUMMA_TYPES)
    tracts = sum(1 for b in shared if b.type == "Tractatus")
    parts = [
        *([_plural(summae, "summa", "summae")] if summae else []),
        *([f"{tracts} tractatus"] if tracts else []),
        *([f"{len(holding.kept())} kept by its magi"] if holding.kept() else []),
    ]
    return " · ".join(parts)


def _cells(holding: Holding) -> list[str]:
    """A subject's row (plain text): its name, Holding, best summa, books
    and research bonus."""
    return [
        holding.name,
        f"L{holding.level} Q{holding.quality}" if holding.level is not None else "—",
        holding.best.name if holding.best else "no summa",
        _books_cell(holding),
        f"+{holding.research_level}" if holding.research_level else "—",
    ]


def _dim(holding: Holding, markup: str) -> str:
    """`markup` greyed for a subject with no Holding."""
    return markup if holding.level is not None else f"[dim]{markup}[/]"


def subjects_table(found: list[Holding]) -> Table:
    """The Library by subject: each subject's Holding, best summa, books and
    research bonus, under a heading for each kind (Arts, Abilities,
    Mastery). A subject with no Holding is greyed. Its keys index `found`."""
    rows: list[list[str]] = []
    keys: list[int | None] = []
    heading = ""
    for i, holding in enumerate(found):
        kind = _KINDS.get(holding.kind, "")
        if kind != heading:
            heading = kind
            rows.append([kind, "", "", "", ""])
            keys.append(None)
        rows.append([_dim(holding, escape(cell)) for cell in _cells(holding)])
        keys.append(i)
    return Table(
        ["Subject", "Holding", "Best summa", "Books", "Research"],
        rows,
        keys,
        markup=True,
        stretch=2,
    )


#: The terminal list's columns and their widths (subjects_table's, in text).
SUBJECT_COLUMNS: tuple[tuple[str, int], ...] = (
    ("Subject", 22),
    ("Holding", 9),
    ("Best summa", 30),
    ("Books", 26),
    ("Research", 10),
)


def _columns(cells: list[str]) -> str:
    """`cells` in SUBJECT_COLUMNS, each fitted with a space after it."""
    return "".join(
        fit(cell, width - 1) + " "
        for cell, (_, width) in zip(cells, SUBJECT_COLUMNS, strict=True)
    ).rstrip()


def subject_header() -> str:
    """The terminal list's column titles (plain text)."""
    return _columns([title for title, _ in SUBJECT_COLUMNS])


def subject_label(holding: Holding) -> str:
    """A subject's row in the terminal list (markup): subjects_table's
    cells in columns, greyed without a Holding."""
    return _dim(holding, escape(_columns(_cells(holding))))


#: What a book does for the Holding, as its role's words.
ROLE_WORDS: dict[str, str] = {
    tme_books.ROLE_LEVEL: "adds to its Level",
    tme_books.ROLE_QUALITY: "adds to its Quality",
    tme_books.ROLE_FAR: "adds nothing: more than 3 from the Holding",
    tme_books.ROLE_COPY: "adds nothing: a copy of a book it has",
}


def keeper(saga: Saga, book: Book, kept: str = "Kept") -> str:
    """ "Kept by Corvinus" or "Kept in Corvinus's Laboratory": who keeps a
    book outside the shared library (`kept`, its first word)."""
    owner = owner_record(saga, book)
    where = "in" if book.owner_kind == "laboratory" else "by"
    return f"{kept} {where} {owner.name if owner else ''}"


def list_role(saga: Saga, holding: Holding, book: Book) -> str:
    """A book's role in the subject's list of books (plain text): with the
    Large Library rule, what it does for the Holding; a kept book's keeper
    either way; "" when it has none."""
    role = holding.roles.get(book.id)
    if role == KEPT:
        return f"{keeper(saga, book, 'kept')}: not in the shared library"
    if role == tme_books.ROLE_BEST:
        return "the best summa: sets the Holding"
    return ROLE_WORDS.get(role or "", "")


def prototype(holding: Holding) -> Book:
    """A new book's starting fields for the subject: a summa on it, in the
    covenant's library (forms.library.book_form's `like`)."""
    art = holding.kind == "art"
    return Book(
        "",
        "",
        "Art Summa" if art else "Ability Summa",
        art=holding.name if art else "",
        ability="" if art else holding.name,
        owner_kind="covenant",
        owner_id=holding.covenant.id,
    )


# -- which view the Library opens on -----------------------------------------

#: The app setting holding it, and its two values.
LIBRARY_VIEW = "library_view"
SHELVES, SUBJECTS = "shelves", "subjects"


def library_view() -> str:
    """The Library's view last chosen: SHELVES (the default) or SUBJECTS."""
    return (
        SUBJECTS if settings.load_settings().get(LIBRARY_VIEW) == SUBJECTS else SHELVES
    )


def remember_library_view(view: str) -> None:
    settings.update_settings(**{LIBRARY_VIEW: view})


def role_text(holding: Holding, book: Book) -> str:
    """What `book` does for the Holding (plain text), e.g. "this is its best
    summa (2 of its 4 tractatus add to it)"; "" without a role."""
    role = holding.roles.get(book.id)
    if role == tme_books.ROLE_BEST:
        return "this is its best summa" + _adders(holding)
    words = ROLE_WORDS.get(role or "")
    return f"this book {words}" if words else ""


def _adders(holding: Holding) -> str:
    """ " (2 of its 4 tractatus add to it)": how many of the other books add."""
    shared = [b for b in holding.shared() if b is not holding.best]
    roles = holding.roles
    parts: list[tuple[int, str]] = []
    summae = [b for b in shared if b.type in SUMMA_TYPES]
    if summae:
        adding = sum(1 for b in summae if roles.get(b.id) == tme_books.ROLE_LEVEL)
        noun = "other summa" if len(summae) == 1 else "other summae"
        parts.append((adding, f"{adding} of its {len(summae)} {noun}"))
    tracts = [b for b in shared if b.type == "Tractatus"]
    if tracts:
        adding = sum(1 for b in tracts if roles.get(b.id) == tme_books.ROLE_QUALITY)
        parts.append((adding, f"{adding} of its {len(tracts)} tractatus"))
    if not parts:
        return ""
    if not any(adding for adding, _ in parts):
        return " (no other book adds to it)"
    verb = "adds" if len(parts) == 1 and parts[0][0] == 1 else "add"
    return f" ({' and '.join(text for _, text in parts)} {verb} to it)"


def book_lines(saga: Saga, book: Book) -> list[str]:
    """The book inspector's block on its covenant's library in its subject
    (markup): the Holding with what this book does in it (with the Large
    Library rule), and the research bonus. A book a magus keeps says it
    isn't in the shared library; a book on no subject, or at no covenant,
    has no block."""
    subject = activities.book_subject(book)
    covenant = saga.covenant(covenant_of(saga, book))
    if subject is None or covenant is None:
        return []
    if book.owner_kind != "covenant":
        return [
            f"[b]{escape(keeper(saga, book))}:[/] not in "
            f"{escape(covenant.name)}'s shared library"
        ]
    holding = subject_holding(saga, covenant, subject)
    lines = [f"[b]{escape(covenant.name)}'s {escape(holding.name)} library[/]"]
    if holding.large_library:
        role = role_text(holding, book)
        figures = holding.figures() + (f" · {role}" if role else "")
        lines.append(f"  [b]Holding:[/] {escape(figures)}")
    elif not holding.research:
        return []
    lines.append(f"  [b]Research:[/] {escape(holding.research or 'none')}")
    return lines
