"""What a book is worth and what a library is good for -- no UI in here.

- A summa's or tractatus's category of value (Covenants, Chapter Seven:
  Library, "Hermetic Books: Definition of Categories of Value") and a guide
  to its price ("Prices for Books"). The book only gives bands around
  typical figures; the boundaries between them are this app's reading.
- A library's research bonus per subject ("Use: Research"): a level the
  troupe sets for the covenant from the book's descriptions, and each
  encyclopedia's own bonus, +1 per tractatus on the subject (Art &
  Academe, "Encyclopedias", p. 26).

Everything here is worked out from the books, except the research levels
the troupe chooses (Covenant.library_research).
"""

from __future__ import annotations

from dataclasses import dataclass

from . import book_kinds
from .models import SUPERNATURAL_CATEGORIES, Book, Covenant, Saga
from .rules import library, options
from .rules.creation_access import ability_category
from .rules.rounding import round_up

SOURCE = "Covenants, Chapter Seven: Library, pp. 84-102"
#: The book research values come from.
SOURCE_BOOK = "Covenants"
ENCYCLOPEDIA_SOURCE = "Art & Academe, Chapter Three: Philosophiae, Encyclopedias, p. 26"

EXCELLENT, SOUND, VAIN, DISCARDED = "Excellent", "Sound", "Vain", "Discarded"

#: A summa's score for its category: Quality + Level, the scale Covenants
#: gives the bands on ("quality (31 - level)"); an Ability summa's Level
#: counts three times, as in its Build Point cost.
_SUMMA_BANDS: tuple[tuple[int, str], ...] = (
    (32, EXCELLENT),  # about 35 - level; never above 41 - level
    (26, SOUND),  # 28 to 31 - level
    (19, VAIN),  # 25 - level or below
    (0, DISCARDED),  # 15 to 18 - level: damaged, stripped of resonances
)
#: A tractatus's: excellent about 14, sound about 11, vain about 6,
#: damaged ones as low as 1.
_TRACTATUS_BANDS: tuple[tuple[int, str], ...] = (
    (13, EXCELLENT),
    (9, SOUND),
    (4, VAIN),
    (0, DISCARDED),
)


def summa_score(book: Book) -> int | None:
    """Quality + Level (+ 3 x Level for an Ability summa), or None."""
    if (
        book.type not in library.SUMMA_TYPES
        or book.quality is None
        or book.level is None
    ):
        return None
    factor = 3 if book.type == "Ability Summa" else 1
    return book.quality + factor * book.level


def category(book: Book) -> str | None:
    """Excellent, Sound, Vain or Discarded, for a summa or tractatus with
    its numbers set; None for any other book."""
    if library.numbers_to_set(book):
        return None
    if book.type == "Tractatus" and book.quality is not None:
        value, bands = book.quality, _TRACTATUS_BANDS
    else:
        score = summa_score(book)
        if score is None:
            return None
        value, bands = score, _SUMMA_BANDS
    return next(name for floor, name in bands if value >= floor)


def is_hermetic(book: Book) -> bool:
    """A book on an Art, an Arcane Ability or a supernatural power: traded
    among magi for vis. Any other book is a mundane one, bought for money."""
    if library.is_art_book(book.type, book.subject_kind):
        return True

    kind = ability_category(book.ability) if book.ability else "General"
    return kind == "Arcane" or kind in SUPERNATURAL_CATEGORIES


def price_text(book: Book) -> str:
    """A guide to what the book trades for (plain text), or "" when it has
    no category."""
    kind = category(book)
    if kind is None:
        return ""
    if not is_hermetic(book):
        return "about a pound (a mundane book)"
    if kind == EXCELLENT:
        return "not sold: a gift (Cow and Calf Oath)"
    if book.type == "Tractatus":
        return {
            SOUND: "about 2 pawns of vis (3 for a copy at once)",
            VAIN: "about a pawn of vis",
            DISCARDED: "under a pawn of vis",
        }[kind]
    level = book.level or 0
    if kind == SOUND:
        now = level + level // 5  # up to 20% more for a spare copy
        return f"about {level} pawns of vis ({now} for a copy at once)"
    if kind == VAIN:
        return f"about {max(1, round_up(level / 2))} pawns of vis"
    return "about a pawn of vis"


# ---------------------------------------------------------------- research

#: The research bonus levels a troupe chooses from, per subject.
RESEARCH_LEVELS: tuple[tuple[int, str], ...] = (
    (0, "None"),
    (1, "+1 a few books"),
    (2, "+2 a respectable collection (like a Summer covenant)"),
    (3, "+3 a broad, deep collection (like an Autumn covenant)"),
    (4, "+4 specialized"),
    (5, "+5 peerless collection (one of the best in the world)"),
)


def subject_of(book: Book) -> str:
    """The Art or Ability a summa or tractatus is on ("" for other books)."""
    if book.type not in (*library.SUMMA_TYPES, "Tractatus"):
        return ""
    return library.subject(book)


def library_subjects(saga: Saga, covenant: Covenant) -> dict[str, list[Book]]:
    """Each subject the covenant's library has a summa or tractatus on, with
    those books, in order of first appearance."""
    found: dict[str, list[Book]] = {}
    for book in library.books_in_covenant(saga, covenant):
        subject = subject_of(book)
        if subject:
            found.setdefault(subject, []).append(book)
    return found


@dataclass(frozen=True)
class EncyclopediaBonus:
    name: str  # the encyclopedia (its codex)
    bonus: int  # +1 per tractatus on the subject


def encyclopedias(
    saga: Saga, covenant: Covenant, subject: str
) -> list[EncyclopediaBonus]:
    """The encyclopedias in the covenant's library that aid research on
    `subject`, each with its bonus, best first."""
    counts: dict[str, int] = {}
    for book in library.books_in_covenant(saga, covenant):
        codex = library.codex_of(saga, book)
        if (
            codex is not None
            and codex.encyclopedia
            and book.type == "Tractatus"
            and subject_of(book) == subject
        ):
            counts[codex.name] = counts.get(codex.name, 0) + 1
    found = [EncyclopediaBonus(name, n) for name, n in counts.items()]
    return sorted(found, key=lambda e: -e.bonus)


def guide_text(saga: Saga, covenant: Covenant, subject: str, books: list[Book]) -> str:
    """What the library holds on `subject`, to choose its level by: how many
    summae (the best one) and tractatus, and its encyclopedias."""
    summae = [b for b in books if b.type in library.SUMMA_TYPES]
    tracts = [b for b in books if b.type == "Tractatus"]
    parts = []
    if summae:
        best = max(summae, key=lambda b: (b.level or 0, b.quality or 0))
        parts.append(
            f"{len(summae)} summa{'e' if len(summae) != 1 else ''} (best Level "
            f"{best.level if best.level is not None else '?'} Quality "
            f"{best.quality if best.quality is not None else '?'})"
        )
    if tracts:
        parts.append(f"{len(tracts)} tractatus")
    text = ", ".join(parts)
    found = encyclopedias(saga, covenant, subject)
    if found:
        text += "; encyclopedias: " + ", ".join(f"{e.name} +{e.bonus}" for e in found)
    return text


#: The most a library's research bonus reaches (a peerless collection).
RESEARCH_MOST = 5
#: Build Points for a group of pictorial works on one Ability.
PICTORIAL_BP = 10


def library_level(saga: Saga, covenant: Covenant, subject: str) -> int:
    """The library's research bonus on `subject`: the level the troupe set,
    one more for its pictorial works and for a long expert correspondence
    on it, at most +5."""
    return research_level(
        saga,
        covenant,
        subject,
        covenant.library_research.get(subject, 0),
        subject in covenant.pictorial_works,
    )


def research_level(
    saga: Saga, covenant: Covenant, subject: str, chosen: int, pictorial: bool
) -> int:
    """The research bonus on `subject` the `chosen` level would give, with
    pictorial works or not: one more for them; one more for a long expert
    correspondence (a level up, Covenants p. 90) or a realia collection (up
    to +1, p. 102) in the library, each kind once, and both only when the
    troupe's house rule lets them stack (the book doesn't say); at most +5."""
    level = chosen + (1 if pictorial else 0)
    kinds = {
        book.opus
        for book in library_subjects(saga, covenant).get(subject, [])
        if book.opus in book_kinds.OPUS_TYPES
    }
    aids = sum(book_kinds.OPUS_TYPES[k].research_level for k in kinds)
    if not options.is_on(saga, options.RESEARCH_AIDS_STACK):
        aids = min(aids, 1)
    return min(RESEARCH_MOST, level + aids)


def subject_research_text(saga: Saga, covenant: Covenant, subject: str) -> str:
    """Research on `subject` in the covenant's library (plain text), e.g.
    "library +2 · Natural Histories +8"; "" when it has neither a bonus nor
    an encyclopedia."""
    level = library_level(saga, covenant, subject)
    parts = [f"library +{level}"] if level else []
    parts += [f"{e.name} +{e.bonus}" for e in encyclopedias(saga, covenant, subject)]
    return " · ".join(parts)


def research_count(saga: Saga, covenant: Covenant) -> str:
    """The Library Summary's Research row (plain text): how many subjects
    the library aids research on, by a bonus set or an encyclopedia, e.g.
    "6 subjects"; "" when none. The details panel and Set Up Research
    Library give each one."""
    count = sum(
        1
        for subject in library_subjects(saga, covenant)
        if library_level(saga, covenant, subject)
        or encyclopedias(saga, covenant, subject)
    )
    if not count:
        return ""
    return f"{count} subject{'s' if count != 1 else ''}"
