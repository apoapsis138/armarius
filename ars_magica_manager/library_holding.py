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
from .markup import escape
from .models import Book, Covenant, Saga
from .rules import activities, tme_books
from .rules import options as rule_options
from .rules.library import SUMMA_TYPES, books_in_covenant, covenant_of, owner_record

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

    def shared(self) -> list[Book]:
        return [b for b in self.books if self.roles.get(b.id) != KEPT]


def subject_holding(saga: Saga, covenant: Covenant, subject: str) -> Holding:
    """The covenant's library in `subject` (activities.book_subject's key)."""
    on = rule_options.is_on(saga, rule_options.LARGE_LIBRARY)
    books = [
        b
        for b in books_in_covenant(saga, covenant)
        if activities.book_subject(b) == subject
    ]
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
    research = bv.subject_research_text(saga, covenant, name) if name else ""
    return Holding(
        covenant, subject, name, on, best, level, quality, books, roles, research
    )


def role_text(holding: Holding, book: Book) -> str:
    """What `book` does for the Holding (plain text), e.g. "this is its best
    summa (2 of its 4 tractatus add to it)"; "" without a role."""
    role = holding.roles.get(book.id)
    if role == tme_books.ROLE_BEST:
        return "this is its best summa" + _adders(holding)
    return {
        tme_books.ROLE_LEVEL: "this book adds to its Level",
        tme_books.ROLE_QUALITY: "this book adds to its Quality",
        tme_books.ROLE_FAR: "this book adds nothing: more than 3 from the Holding",
        tme_books.ROLE_COPY: "this book adds nothing: a copy of a book it has",
    }.get(role or "", "")


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
        owner = owner_record(saga, book)
        who = "Kept in" if book.owner_kind == "laboratory" else "Kept by"
        return [
            f"[b]{who} {escape(owner.name if owner else '')}:[/] not in "
            f"{escape(covenant.name)}'s shared library"
        ]
    holding = subject_holding(saga, covenant, subject)
    lines = [f"[b]{escape(covenant.name)}'s {escape(holding.name)} library[/]"]
    if holding.large_library:
        if holding.level is None:
            figures = "none: the library has no summa on it"
        else:
            figures = f"Level {holding.level}, Quality {holding.quality}"
            role = role_text(holding, book)
            if role:
                figures += f" · {role}"
        lines.append(f"  [b]Holding:[/] {escape(figures)}")
    elif not holding.research:
        return []
    lines.append(f"  [b]Research:[/] {escape(holding.research or 'none')}")
    return lines
