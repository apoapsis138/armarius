"""Books as the rules read them: a book's level and Quality (with the
saga's options), its Build Point cost and the spell pools Lab Texts and
Casting Tablets share, who may read it, and the codices books are bound
in. The Library tab, its forms and importing books are books.py's."""

from __future__ import annotations

from dataclasses import dataclass

from .. import book_kinds, catalog
from ..book_kinds import Adjustment
from ..models import Book, Character, Codex, Covenant, Saga, Spell
from . import options
from .rounding import round_up

SOURCE = (
    "Ars Magica Definitive Edition, Chapter Six: Covenants, Library "
    "(https://www.redcap.org/page/Ars_Magica_Definitive_Edition,_Chapter"
    "_Six:_Covenants#Library)"
)


#: Book types whose subject is an Art / an Ability (a Tractatus depends on its
#: `subject_kind`).
SUMMA_TYPES: tuple[str, ...] = ("Art Summa", "Ability Summa")


#: Book types that record a spell (name + level) instead of an Art or Ability.
SPELL_TYPES: tuple[str, ...] = ("Lab Text", "Casting Tablet")


def has_quality(book_type: str) -> bool:
    return book_type in SUMMA_TYPES or book_type == "Tractatus"


def numbers_to_set(book: Book) -> list[str]:
    """The figures a summa or tractatus still lacks ("Level", "Quality"):
    a book whose value is variable until it comes into play (imported with
    "var"). It can't be studied until they are set."""
    missing = []
    if book.type in SUMMA_TYPES and book.level is None:
        missing.append("Level")
    if has_quality(book.type) and book.quality is None:
        missing.append("Quality")
    return missing


def book_spell(saga: Saga, book: Book) -> Spell | None:
    """A Lab Text's or Casting Tablet's spell: the one its `spell_id` names,
    else the one its typed `spell_name` matches (how imported books link).
    None for other books, or when nothing matches."""
    if book.type not in SPELL_TYPES:
        return None
    if book.spell_id:
        found = catalog.find_spell(saga, book.spell_id)
        if found is not None:
            return found
    return catalog.find_spell_by_name(saga, book.spell_name)


def level_of(book: Book, saga: Saga | None = None) -> int | None:
    """The book's Level. A Lab Text's or Casting Tablet's is its spell's,
    unless the spell is General-level (or unknown), when the book's own
    `level` counts. Without a saga the stored level is all there is."""
    if saga is not None and book.type in SPELL_TYPES:
        spell = book_spell(saga, book)
        if spell is not None and spell.level is not None:
            return spell.level
    return book.level


#: Lab Texts and Casting Tablets are bought as a pool of levels for the
#: library, not text by text (POOL_SOURCE): POOL_POINTS Build Points buy
#: POOL_LEVELS levels. The pool's levels are summed first; whole Build
#: Points are spent, so the last purchase rounds up and its unused levels
#: are the pool's unspent remainder.
POOL_LEVELS = 5


POOL_POINTS: dict[str, int] = {"Lab Text": 1, "Casting Tablet": 2}


@dataclass(frozen=True)
class Pool:
    """A covenant's Lab Text or Casting Tablet pool."""

    book_type: str
    levels: int
    points: int
    #: Levels bought but not yet used by a text.
    unspent: int


def pool(books: list[Book], book_type: str, saga: Saga | None = None) -> Pool:
    """The `book_type` pool of `books` (a covenant's library): the levels
    summed, the Build Points they take, and the levels left over."""
    levels = sum(level_of(b, saga) or 0 for b in books if b.type == book_type)
    lots = round_up(levels / POOL_LEVELS)
    return Pool(
        book_type, levels, lots * POOL_POINTS[book_type], lots * POOL_LEVELS - levels
    )


def cost(book: Book, saga: Saga | None = None) -> int:
    """Build Points the book costs at covenant creation. A blank level or
    quality counts as 0; Other books cost nothing, and neither does a Lab
    Text or Casting Tablet on its own: those are bought as a pool (pool())."""
    level = level_of(book, saga) or 0
    quality = priced_quality(saga, book) or 0
    if book.type == "Art Summa":
        return level + quality
    if book.type == "Ability Summa":
        return quality + 3 * level
    if book.type == "Tractatus":
        return quality
    return 0


def owner_record(saga: Saga, book: Book):
    """The covenant, laboratory or character that owns the book, or None
    (unowned, or the owner no longer exists)."""
    records = {
        "covenant": saga.covenants,
        "laboratory": saga.laboratories,
        "character": saga.characters,
    }.get(book.owner_kind or "", [])
    return next((r for r in records if r.id == book.owner_id), None)


def books_owned_by(saga: Saga, kind: str, owner_id: str) -> list[Book]:
    return [b for b in saga.books if b.owner_kind == kind and b.owner_id == owner_id]


def can_read(saga: Saga, character: Character, book: Book) -> bool:
    """Whether `character` may study `book`: a
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


#: The Quality lost by each text of a palimpsest (Covenants, Secondary
#: Functions).
PALIMPSEST_PENALTY = 3


def codex_of(saga: Saga, book: Book) -> Codex | None:
    """The codex the book is bound in with others, or None (bound alone)."""
    if not book.codex_id:
        return None
    return next((c for c in saga.codices if c.id == book.codex_id), None)


def same_codex(saga: Saga, a: Book, b: Book) -> bool:
    """Whether two books are one physical codex (or the same book)."""
    return (
        a is b
        or a.id == b.id
        or (codex_of(saga, a) is not None and a.codex_id == b.codex_id)
    )


def extended_quality(saga: Saga | None) -> bool:
    """Whether the saga uses Covenants' extended book Quality rules (its
    craftsmanship counts, an author gives Communication + 3)."""
    return options.is_on(saga, options.EXTENDED_BOOK_QUALITY)


def quality_adjustments(saga: Saga | None, book: Book) -> list[Adjustment]:
    """What changes the Quality the book is studied at, beyond its own: its
    opus type, its physical form, and the codex it is bound in (a
    palimpsest's -3, a florilegium's bonus). See book_kinds."""
    found: list[Adjustment] = []
    opus = book_kinds.OPUS_TYPES.get(book.opus)
    if opus is not None and opus.quality:
        found.append(Adjustment(opus.name.lower(), opus.quality, opus.priced))
    form = book_kinds.PHYSICAL_FORMS.get(book.physical_form)
    if form is not None and form.quality:
        found.append(Adjustment(form.name.lower(), form.quality, form.priced))
    if extended_quality(saga):
        for key in book.craft:
            part = book_kinds.CRAFT.get(key)
            if part is not None:
                found.append(Adjustment(part.name.lower(), part.quality, part.priced))
    if book.glossed:
        gloss = book_kinds.GLOSS
        found.append(Adjustment(gloss.name.lower(), gloss.quality, gloss.priced))
    codex = codex_of(saga, book) if saga is not None else None
    if codex is not None:
        if codex.palimpsest:
            found.append(Adjustment("palimpsest", -PALIMPSEST_PENALTY))
        if codex.collection == book_kinds.FLORILEGIUM and book.type == "Tractatus":
            found.append(
                Adjustment("florilegium", codex.florilegium_bonus, priced=False)
            )
    return found


def effective_quality(saga: Saga | None, book: Book) -> int | None:
    """The Quality a reader studies the book at: its own, with its
    quality_adjustments (never below 0)."""
    if book.quality is None:
        return None
    total = book.quality + sum(a.amount for a in quality_adjustments(saga, book))
    return max(0, total)


def priced_quality(saga: Saga | None, book: Book) -> int | None:
    """The Quality its Build Point cost counts: its own, with the
    adjustments that count toward cost (not a commentary's or a
    florilegium's bonus)."""
    if book.quality is None:
        return None
    adjustments = quality_adjustments(saga, book)
    return max(0, book.quality + sum(a.amount for a in adjustments if a.priced))


def is_art_book(book_type: str, subject_kind: str = "") -> bool:
    return book_type == "Art Summa" or (
        book_type == "Tractatus" and subject_kind == "Art"
    )


def is_ability_book(book_type: str, subject_kind: str = "") -> bool:
    return book_type == "Ability Summa" or (
        book_type == "Tractatus" and subject_kind == "Ability"
    )


def covenant_of(saga: Saga, book: Book) -> str | None:
    """The id of the covenant the book is kept in: its owner, or the covenant
    of the laboratory or character that owns it."""
    owner = owner_record(saga, book)
    if owner is None:
        return None
    if book.owner_kind == "covenant":
        return owner.id
    return owner.covenant_id


def books_in_covenant(saga: Saga, covenant: Covenant) -> list[Book]:
    """Everything the covenant's Library lists: books it owns, and books owned
    by its laboratories and characters, in the order added."""
    return [b for b in saga.books if covenant_of(saga, b) == covenant.id]


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
