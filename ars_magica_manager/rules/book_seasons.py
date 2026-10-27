"""Seasons spent on books and Lab Texts.

Books, planned on the character sheet:

- Writing a summa: needs the subject at 5 (an Art) or 2 (an Ability) and
  the language at 5. Level at most half the score; Quality Communication
  + 6, +1 per Level below the most (+3 for an Ability), that bonus at most
  the base Quality. Communication + language points a season, until they
  reach the Level (5 x Level for an Ability).
- Writing a tractatus: one season, Quality Communication + 6; at most
  score / 5 (an Art) or score / 2 (an Ability) tractatus on a subject,
  rounded up.
- Copying a book: carefully 1 tractatus, or 6 + Profession: Scribe summa
  points a season (keeps its Quality); quickly three times as much, the
  copy 1 Quality lower. Needs the language at 3 (Magic Theory 1 for a
  book on an Art).
- Translating a book: both languages at 5 and Artes Liberales 2 (1 between
  languages of one alphabet); a tractatus in one season, a summa at
  Communication + the source language points a season until its Level;
  the translation 1 Quality lower for the languages (none with both at
  6) and 1 for the culture, unless the plan says he has the source
  culture's Area Lore at 3, or the text is Hermetic and he is a magus
  (A&A p. 87).

Lab Texts:

- A magus's own Lab Texts are written raw: only he (and whoever has
  decoded them, or been taught his abbreviations) can use them.
- Rewriting his own texts for general use: Latin x 20 levels a season.
- Copying readable Lab Texts: Profession: Scribe x 60 levels a season.
- Decoding another magus's texts (in the laboratory): the Lab Total in the
  text's Technique and Form each season, until the points reach its level;
  then all that magus's texts up to that level are readable.
- Teaching abbreviations: a season writing with a student lets him read the
  magus's texts up to Latin x 20 levels.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from .. import book_kinds, book_value, catalog
from ..arts import ART_BY_NAME
from ..models import (
    TEXT_LONGEVITY,
    Book,
    Character,
    LabTextAccess,
    Saga,
    SeasonPlan,
)
from . import effects, lab_stats, library, options, scholarship
from .rounding import round_down, round_up
from .scores import ability_level, character_source
from .study import after_distraction, supernatural_ability

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Writing Books, pp. "
    "379-380"
)
COPY_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 10: Long-Term Events, Copying Books, p. 380"
)
TRANSLATE_SOURCE = (
    "Art & Academe, Chapter Six: Institutional Education, Translation, p. 87"
)
LAB_TEXT_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Using Laboratory Texts, p. "
    "262"
)
DECODE_SOURCE = (
    "Ars Magica Definitive Edition, Chapter 8: Laboratory, Translating Laboratory "
    "Texts, p. 263"
)

WRITE_SUMMA = "write_summa"
WRITE_TRACTATUS = "write_tractatus"
COPY_BOOK = "copy_book"
TRANSLATE_BOOK = "translate_book"
REWRITE_TEXTS = "rewrite_lab_texts"
COPY_TEXTS = "copy_lab_texts"
WRITE_TABLET = "write_casting_tablet"
EDIT_FLORILEGIUM = "edit_florilegium"
TEACH_ABBREVIATIONS = "teach_abbreviations"
DECODE_TEXT = "decode_lab_text"
#: Planned on the character sheet (decoding is lab work).
SHEET_ACTIVITIES: tuple[str, ...] = (
    WRITE_SUMMA,
    WRITE_TRACTATUS,
    COPY_BOOK,
    TRANSLATE_BOOK,
    REWRITE_TEXTS,
    COPY_TEXTS,
    WRITE_TABLET,
    EDIT_FLORILEGIUM,
    TEACH_ABBREVIATIONS,
)
#: Book work that can take several seasons, points carried between them.
MULTI_SEASON: tuple[str, ...] = (WRITE_SUMMA, COPY_BOOK, TRANSLATE_BOOK)
SUMMA_TYPES = ("Art Summa", "Ability Summa")
#: The Ability every activity gives Exposure in (None: the book's language).
EXPOSURE_IN = {
    COPY_BOOK: "Profession: Scribe",
    COPY_TEXTS: "Profession: Scribe",
    TEACH_ABBREVIATIONS: "Teaching",
}


@dataclass
class BookWork:
    """What a season of book work does."""

    points_before: int = 0
    points_gained: int = 0
    needed: int = 0
    #: The book written, copied or translated when this season finishes it
    #: (not yet in the saga), and how many copies.
    made: Book | None = None
    copies: int = 0
    #: Lab Texts rewritten for general use this season.
    rewritten: list[str] = field(default_factory=list)
    #: Who can now read whose Lab Texts, up to what level:
    #: (reader id, author name, level).
    access: tuple[str, str, int] | None = None
    #: A florilegium edited: (its name, the tractatus bound in it, its
    #: Quality bonus).
    florilegium: tuple[str, list[str], int] | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def points_after(self) -> int:
        return self.points_before + self.points_gained

    @property
    def finished(self) -> bool:
        return self.points_after >= self.needed


# -- scores -----------------------------------------------------------------------


#: Covenants' extended rules printed +3 Quality for books off the Arts and
#: Arcane Abilities; Atlas Games' errata to Covenants p. 88 delete it, so
#: the bonus is 0.
MUNDANE_SUBJECT_BONUS = 0


def magical_subject(subject: str) -> bool:
    """Whether a book's subject is an Art or an Arcane Ability (the
    extended rules' magical subjects, Covenants p. 88)."""
    kind, _, name = subject.partition(":")
    if kind == "art":
        return True
    base = name.split(":")[0].split(" (")[0].strip()
    return any(
        d.category == "Arcane" and d.name.split(":")[0].split(" (")[0] == base
        for d in catalog.load_ability_catalog()
    )


def quality_bonus(character: Character) -> int:
    """What the author's Virtues add to the Quality of his books (Good
    Teacher +3, DE p. 83)."""
    return int(
        effects.amount_total(
            effects.collect([character_source(character.virtues_flaws)], "book_quality")
        )
    )


def written_by(book: Book, character: Character) -> bool:
    """Whether `character` wrote `book` (his id, or his name on a book
    with none)."""
    if book.author_id:
        return book.author_id == character.id
    return bool(book.author) and book.author == character.name


def texts_bonus(saga: Saga, character: Character, plan: SeasonPlan) -> int:
    """What the character's laboratory's Texts Specialization adds to
    Profession: Scribe when copying and to the Language when writing (DE
    p. 291), when the season is spent there (the plan's `in_lab`)."""
    if not plan.in_lab:
        return 0
    return lab_stats.texts_bonus(saga, saga.laboratory(character.assigned_lab_id))


def language_score(character: Character, language: str) -> int:
    """The character's score in `language` (a Living or Dead Language
    Ability named for it, or an Ability of that name)."""
    wanted = language.strip().lower()
    return max(
        (
            a.level
            for a in character.abilities
            if a.name.lower() == wanted or a.name.lower().endswith(f": {wanted}")
        ),
        default=0,
    )


def subject_name(saga: Saga, subject: str) -> str:
    """A subject's name to show: the Art or Ability, or "Mastery: <spell>"."""
    kind, _, name = subject.partition(":")
    if kind != "mastery":
        return name
    spell = catalog.find_spell(saga, name)
    return book_kinds.MASTERY_PREFIX + (spell.name if spell else name)


def subject_score(character: Character, subject: str) -> tuple[bool, int]:
    """(is an Art, score) for "art:Creo" / "ability:Latin" / a spell's
    "mastery:<id>"."""
    kind, _, name = subject.partition(":")
    if kind == "art":
        art = character.arts.get(name.lower())
        return True, art.level if art else 0
    if kind == "mastery":
        known = next((k for k in character.spells_known if k.spell_id == name), None)
        return False, known.mastery_score if known else 0
    return False, ability_level(character, name)


def book_subject(book: Book) -> str:
    """The "art:X" / "ability:Y" a summa or tractatus is on ("" if none)."""
    if book.art:
        return f"art:{ART_BY_NAME.get(book.art.lower(), book.art)}"
    mastery = book_kinds.mastery_subject(book.ability, book.spell_id)
    if mastery is not None:
        return mastery
    return f"ability:{book.ability}" if book.ability else ""


def project_key(plan: SeasonPlan) -> str:
    """What ties a book's seasons together."""
    if plan.activity == WRITE_SUMMA:
        subject = plan.allocations[0].subject if plan.allocations else ""
        return f"write:{plan.character_id}:{subject}:{plan.book_level}"
    return f"{plan.activity}:{plan.character_id}:{plan.book_id}:{plan.language}"


def project_points(saga: Saga, key: str) -> int:
    return next((p.points for p in saga.lab_projects if p.spell_id == key), 0)


def _book(saga: Saga, book_id: str | None) -> Book | None:
    return next((b for b in saga.books if b.id == book_id), None)


# -- Lab Text access ------------------------------------------------------------------


def can_use_lab_text(character: Character, book: Book) -> bool:
    """Whether `character` can read a Lab Text's writing: a text for general
    use, one of his own, or a raw text by a magus whose texts he has
    decoded (or been taught to read) up to its level."""
    if book.type != "Lab Text" or not book.raw:
        return True
    if book.author_id == character.id:
        return True
    if book.text_kind == TEXT_LONGEVITY and book.ritual_subject == character.name:
        return True  # a Longevity Ritual's subject can read its text
    return access_level(character, author_key(book), -1) >= text_level(book)


def author_key(book: Book) -> str:
    """What a reader's access to a Lab Text's author is filed under: the
    author's character id, or the typed name of one outside the saga."""
    return book.author_id or book.author


def access_level(character: Character, author: str, default: int = 0) -> int:
    """The level up to which `character` reads the raw texts of `author`
    (an author_key)."""
    access = character.lab_text_access.get(author)
    return access.level if access is not None else default


def grant_access(character: Character, author: str, level: int, via: str) -> None:
    """`character` can now read `author`'s raw texts up to `level` (never
    lowering what he had), gained `via` "decoded" or "taught"."""
    if level > access_level(character, author, -1):
        character.lab_text_access[author] = LabTextAccess(level, via)


def author_name(saga: Saga, book: Book) -> str:
    """A book's author as shown: the linked character's current name, else
    the name typed."""
    author = saga.character(book.author_id)
    return author.name if author is not None else book.author


def text_level(book: Book, saga: Saga | None = None) -> int:
    """A Lab Text's level: its spell's, else the book's own."""
    if saga is not None:
        spell = catalog.find_spell(saga, book.spell_id)
        if spell is not None and spell.level is not None:
            return spell.level
    return book.level or 0


# -- the seasons --------------------------------------------------------------------


def work(
    saga: Saga, character: Character, plan: SeasonPlan
) -> tuple[list[str], BookWork | None]:
    """The problems with a season of book work, or what it does."""
    com = character.characteristics.communication
    if plan.activity in (WRITE_SUMMA, WRITE_TRACTATUS):
        return _distracted(plan, *_write(saga, character, plan, com))
    if plan.activity in (COPY_BOOK, TRANSLATE_BOOK):
        return _distracted(plan, *_copy(saga, character, plan, com))
    if plan.activity == EDIT_FLORILEGIUM:
        return _edit_florilegium(saga, character, plan)
    return _lab_texts(saga, character, plan)


def _distracted(
    plan: SeasonPlan, problems: list[str], done: BookWork | None
) -> tuple[list[str], BookWork | None]:
    """A summa's season of writing, copying or translating loses a third
    of its points for each full month lost to distractions (DE p. 379)."""
    if done is not None and done.needed > 1 and plan.months_lost:
        done.points_gained = after_distraction(done.points_gained, plan.months_lost)
    return problems, done


#: Editing a florilegium (Covenants, Other Opus Types): the score an editor
#: needs (Ability, Art) for +1, and an authority's for +2; and how many times
#: the tractatus bound the collection must hold.
FLORILEGIUM_EDITOR = (6, 20)
FLORILEGIUM_AUTHORITY = (10, 35)
FLORILEGIUM_COLLECTION, PEERLESS_COLLECTION = 2, 5


def florilegium_candidates(
    saga: Saga, character: Character, subject: str
) -> list[Book]:
    """The tractatus on `subject` the editor can get at, not yet bound in a
    codex, best Quality first."""
    found = [
        b
        for b in saga.books
        if b.type == "Tractatus"
        and book_subject(b) == subject
        and b.quality is not None
        and library.codex_of(saga, b) is None
        and library.can_read(saga, character, b)
    ]
    return sorted(found, key=lambda b: -(b.quality or 0))


def _edit_florilegium(
    saga: Saga, character: Character, plan: SeasonPlan
) -> tuple[list[str], BookWork | None]:
    """A season binding tractatus on one subject into a florilegium: as
    many as the editor could write on it, from a collection twice that size;
    each read at +1 Quality, +2 when an authority edits from a peerless
    collection (five times the size)."""
    subject = plan.florilegium_subject
    if not subject:
        return ["Choose the subject whose tractatus it binds."], None
    is_art, score = subject_score(character, subject)
    name = subject.partition(":")[2]
    need, authority = FLORILEGIUM_EDITOR[is_art], FLORILEGIUM_AUTHORITY[is_art]
    if score < need:
        return [
            f"Editing a florilegium on {name} needs a score of {need} "
            f"({character.name} has {score})."
        ], None
    most = round_up(score / 5) if is_art else round_up(score / 2)
    found = florilegium_candidates(saga, character, subject)
    peerless = min(most, len(found) // PEERLESS_COLLECTION)
    if score >= authority and peerless >= 1:
        bound, bonus = found[:peerless], 2
    else:
        bound, bonus = found[: min(most, len(found) // FLORILEGIUM_COLLECTION)], 1
    if not bound:
        return [
            f"A florilegium needs a collection of at least twice the tractatus it "
            f"binds: {character.name} can get at {len(found)} on {name}, not "
            "bound in a codex."
        ], None
    title = plan.title.strip() or f"Florilegium of {name}"
    return [], BookWork(
        points_gained=1, needed=1, florilegium=(title, [b.id for b in bound], bonus)
    )


def _write(
    saga: Saga, character: Character, plan: SeasonPlan, com: int
) -> tuple[list[str], BookWork | None]:
    subject = plan.allocations[0].subject if plan.allocations else ""
    if not subject:
        return ["Choose the Art or Ability the book is on."], None
    is_art, score = subject_score(character, subject)
    name = subject_name(saga, subject)
    if score < (5 if is_art else 2):
        return [
            f"Writing on {name} needs a score of {5 if is_art else 2} "
            f"({character.name} has {score})."
        ], None
    language = plan.language or "Latin"
    if language_score(character, language) < 5:
        return [f"Writing in {language} needs it at 5."], None
    # Covenants' extended rules: the author gives Communication + 3, the
    # scribe, binder and illuminator the rest (the book form records them).
    extended = options.is_on(saga, options.EXTENDED_BOOK_QUALITY)
    # Good Teacher's +3 is part of the base the summa's bonus is capped at
    # (DE pp. 83, 380). The extended rules give the author Communication +
    # 3 on a summa or a tractatus, whatever the subject (Covenants p. 88,
    # as its errata correct it: the tractatus gains the +3 and the +3
    # for non-magical subjects is gone).
    base = com + quality_bonus(character)
    if not extended:
        base += 6
    else:
        base += book_kinds.EXTENDED_AUTHOR_BASE
    if extended and not magical_subject(subject):
        base += MUNDANE_SUBJECT_BONUS
    kind = ("Art " if is_art else "Ability ") + "Summa"
    if plan.activity == WRITE_TRACTATUS:
        limit = round_up(score / 5) if is_art else round_up(score / 2)
        # Only his own originals count, not copies or translations of them.
        written = sum(
            1
            for b in saga.books
            if b.type == "Tractatus"
            and b.opus != book_kinds.LECTURE_COMMENTARY
            and b.copy_of is None
            and written_by(b, character)
            and book_subject(b) == subject
        )
        if written >= limit:
            return [
                f"{character.name} has written {written} tractatus on {name}, the "
                f"most a score of {score} allows."
            ], None
        made = _new_book(saga, character, plan, "Tractatus", subject, None, base)
        return [], BookWork(points_gained=1, needed=1, made=made)
    most = round_down(score / 2)
    level = plan.book_level if plan.book_level is not None else most
    if not 1 <= level <= most:
        return [f"The summa's Level is 1 to {most} (half the score)."], None
    bonus = min(base, (most - level) * (1 if is_art else 3))
    quality = base + bonus
    needed = level if is_art else 5 * level
    gained = max(
        0,
        com + language_score(character, language) + texts_bonus(saga, character, plan),
    )
    if gained <= 0:
        return ["Communication + the language is 0: no progress is possible."], None
    made = _new_book(saga, character, plan, kind, subject, level, quality)
    return [], BookWork(
        points_before=project_points(saga, project_key(plan)),
        points_gained=gained,
        needed=needed,
        made=made,
    )


def _new_book(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    kind: str,
    subject: str,
    level: int | None,
    quality: int,
) -> Book:
    sort, _, name = subject.partition(":")
    mastery = sort == "mastery"
    spell = catalog.find_spell(saga, name) if mastery else None
    if mastery:
        name = book_kinds.MASTERY_PREFIX + (spell.name if spell else name)
    title = plan.title.strip() or f"{kind} on {name}"
    return Book(
        id=_book_id(saga, title),
        name=title,
        type=kind,
        language=plan.language or "Latin",
        author=character.name,
        author_id=character.id,
        owner_kind="character",
        owner_id=character.id,
        year_published=plan.year,
        art=name if sort == "art" else "",
        ability=name if sort in ("ability", "mastery") else "",
        spell_id=spell.id if spell else None,
        spell_name=spell.name if spell else "",
        subject_kind="Art"
        if sort == "art" and kind == "Tractatus"
        else ("Ability" if kind == "Tractatus" else ""),
        level=level,
        quality=quality,
    )


def _book_id(saga: Saga, name: str) -> str:
    base = "book_" + "".join(c if c.isalnum() else "_" for c in name.lower())[:40]
    ids = {b.id for b in saga.books}
    book_id, n = base, 2
    while book_id in ids:
        book_id, n = f"{base}_{n}", n + 1
    return book_id


def _copy(
    saga: Saga, character: Character, plan: SeasonPlan, com: int
) -> tuple[list[str], BookWork | None]:
    book = _book(saga, plan.book_id)
    if book is None:
        return ["Choose the book."], None
    if book.type not in (*SUMMA_TYPES, "Tractatus"):
        return [f"{book.name} isn't a summa or tractatus."], None
    if not library.can_read(saga, character, book):
        return [f"{character.name} can't get at {book.name}."], None
    if library.lent(book):
        return [
            f"{book.name} is the Great Library's: it may not be copied without "
            "the librarian's leave (Guardians of the Forests p. 55)."
        ], None
    source = language_score(character, book.language or "Latin")
    is_summa = book.type in SUMMA_TYPES
    is_art = bool(book.art)
    level = book.level or 0
    needed = (level if is_art else 5 * level) if is_summa else 1
    if plan.activity == COPY_BOOK:
        if source < 3:
            return [f"Copying needs {book.language} at 3."], None
        if (is_art or book.ability == PARMA) and ability_level(
            character, "Magic Theory"
        ) < 1:
            return [
                f"Copying a book on {book.art or PARMA} needs Magic Theory 1."
            ], None
        if supernatural_ability(book.ability) and not _can_copy_supernatural(
            character, book.ability
        ):
            return [
                f"Copying a book on {book.ability} needs it, or a Realm Lore, at 1."
            ], None
        scribe = ability_level(character, "Profession: Scribe") + texts_bonus(
            saga, character, plan
        )
        quick = plan.quick
        quality = (book.quality or 0) - (1 if quick else 0)
        copy = _copy_of(saga, character, book, quality, book.language)
        if not is_summa:
            return [], BookWork(
                points_gained=1, needed=1, made=copy, copies=3 if quick else 1
            )
        gained = (18 + 3 * scribe) if quick else (6 + scribe)
        return [], BookWork(
            points_before=project_points(saga, project_key(plan)),
            points_gained=gained,
            needed=needed,
            made=copy,
            copies=1,
        )
    # Translating.
    target = plan.language.strip()
    if not target or target.lower() == (book.language or "Latin").lower():
        return ["Choose the language to translate into."], None
    if source < 5 or language_score(character, target) < 5:
        return [f"Translating needs {book.language} and {target} at 5."], None
    artes = scholarship.translation_artes(book.language or "Latin", target)
    if ability_level(character, "Artes Liberales") < artes:
        return [
            f"Translating from {book.language} into {target} needs Artes "
            f"Liberales {artes} (A&A p. 87)."
        ], None
    # The app can't tell which Area Lore is the source culture's, so the
    # plan says whether he knows it at 3. A Hermetic text (an Art, an
    # Arcane Ability or a supernatural power) translated by a magus never
    # loses the culture's point.
    hermetic = book_value.is_hermetic(book) and character.type == "magus"
    loss = scholarship.translation_loss(
        source,
        language_score(character, target),
        hermetic,
        culture_lore=plan.culture_lore,
    )
    copy = _copy_of(saga, character, book, (book.quality or 0) - loss, target)
    if not is_summa:
        return [], BookWork(points_gained=1, needed=1, made=copy, copies=1)
    return [], BookWork(
        points_before=project_points(saga, project_key(plan)),
        points_gained=max(1, com + source),
        needed=level,
        made=copy,
        copies=1,
    )


#: Without Magic Theory 1 a book on the Arts or Parma Magica is copied
#: corrupt; one on a Supernatural Ability needs it or its Realm Lore at 1
#: (DE p. 381).
PARMA = "Parma Magica"
REALM_LORES = ("Magic Lore", "Faerie Lore", "Dominion Lore", "Infernal Lore")


def _can_copy_supernatural(character: Character, ability: str) -> bool:
    """Whether the scribe has the Ability, or a Realm Lore (the catalog
    doesn't say which realm an Ability belongs to, so any counts), at 1."""
    return any(ability_level(character, name) >= 1 for name in (ability, *REALM_LORES))


def _copy_of(
    saga: Saga, character: Character, book: Book, quality: int, language: str
) -> Book:
    return Book(
        id=_book_id(saga, book.name),
        name=book.name if language == book.language else f"{book.name} ({language})",
        type=book.type,
        language=language,
        author=book.author,
        owner_kind="character",
        owner_id=character.id,
        year_published=book.year_published,
        description=book.description,
        subject_kind=book.subject_kind,
        art=book.art,
        ability=book.ability,
        level=book.level,
        quality=max(0, quality),
        spell_name=book.spell_name,
        spell_id=book.spell_id,
        raw=book.raw,
        author_id=book.author_id,
        copy_of=book.copy_of or book.id,
        text_kind=book.text_kind,
        technique=book.technique,
        form=book.form,
        effect_rdt=book.effect_rdt,
        device_type=book.device_type,
        shape_material=book.shape_material,
        ritual_subject=book.ritual_subject,
        ritual_extra_vis=book.ritual_extra_vis,
        experimental_effects=[replace(e) for e in book.experimental_effects],
    )


def _write_tablet(
    saga: Saga, character: Character, plan: SeasonPlan, latin: int
) -> tuple[list[str], BookWork | None]:
    """Writing Casting Tablets of a spell the magus has mastered: from the
    pool of levels a season of writing Lab Texts gives (Latin x 20), as many
    copies as it holds (DE Chapter Eight, Casting Tablets)."""
    known = next(
        (k for k in character.spells_known if k.spell_id == plan.spell_id), None
    )
    spell = catalog.find_spell(saga, plan.spell_id)
    if known is None or spell is None:
        return ["Choose the spell, one the magus knows."], None
    if known.mastery_score < 1:
        return [
            f"Casting Tablets are written only for a mastered spell: "
            f"{character.name} has no Mastery in {spell.name}."
        ], None
    level = max(1, spell.level or 0)
    copies = round_down(20 * latin / level)
    if copies <= 0:
        return [
            f"Latin x 20 = {20 * latin} levels a season: not enough for a level "
            f"{level} tablet."
        ], None
    made = Book(
        id=_book_id(saga, f"Casting Tablet: {spell.name}"),
        name=f"Casting Tablet: {spell.name}",
        type="Casting Tablet",
        language="Latin",
        author=character.name,
        author_id=character.id,
        owner_kind="character",
        owner_id=character.id,
        year_published=plan.year,
        spell_id=spell.id,
        spell_name=spell.name,
    )
    return [], BookWork(points_gained=1, needed=1, made=made, copies=copies)


def _lab_texts(
    saga: Saga, character: Character, plan: SeasonPlan
) -> tuple[list[str], BookWork | None]:
    latin = language_score(character, "Latin") + texts_bonus(saga, character, plan)
    if plan.activity == REWRITE_TEXTS:
        mine = [
            b
            for b in saga.books
            if b.type == "Lab Text" and b.raw and b.author_id == character.id
        ]
        if not mine:
            return [f"{character.name} has no raw Lab Texts to rewrite."], None
        budget = 20 * latin
        if budget <= 0:
            return ["Rewriting Lab Texts needs Latin."], None
        done: list[str] = []
        for book in sorted(mine, key=lambda b: (b.year_published or 0, b.name)):
            level = text_level(book, saga)
            if level > budget:
                break
            budget -= level
            done.append(book.id)
        if not done:
            return [
                f"Latin x 20 = {20 * latin} levels a season: not enough for the "
                "next text."
            ], None
        return [], BookWork(points_gained=1, needed=1, rewritten=done)
    if plan.activity == WRITE_TABLET:
        return _write_tablet(saga, character, plan, latin)
    if plan.activity == COPY_TEXTS:
        book = _book(saga, plan.book_id)
        if book is None or book.type not in ("Lab Text", "Casting Tablet"):
            return ["Choose the Lab Text or Casting Tablet to copy."], None
        if not library.can_read(saga, character, book):
            return [f"{character.name} can't get at {book.name}."], None
        if not can_use_lab_text(character, book):
            return [
                f"{book.name} is {author_name(saga, book)}'s raw text: "
                f"{character.name} must decode it first (or have it rewritten "
                "for general use)."
            ], None
        scribe = ability_level(character, "Profession: Scribe") + texts_bonus(
            saga, character, plan
        )
        level = max(1, text_level(book, saga))
        copies = round_down(60 * scribe / level)
        if copies <= 0:
            return [
                f"Profession: Scribe x 60 = {60 * scribe} levels a season: not "
                f"enough for a level {level} text."
            ], None
        copy = _copy_of(saga, character, book, book.quality or 0, book.language)
        return [], BookWork(points_gained=1, needed=1, made=copy, copies=copies)
    # Teaching abbreviations.
    student = saga.character(plan.subject_id)
    if student is None or student is character:
        return ["Choose the student."], None
    if ability_level(student, "Magic Theory") < 1:
        return [f"{student.name} needs Magic Theory 1 to learn abbreviations."], None
    if latin <= 0:
        return ["Teaching abbreviations needs Latin."], None
    return [], BookWork(
        points_gained=1,
        needed=1,
        access=(student.id, character.id, 20 * latin),
    )


def exposure_ability(character: Character, plan: SeasonPlan) -> str:
    """The Ability a season of book work gives Exposure in: the language
    written (the character's own Ability for it), Profession: Scribe for
    copying, Teaching for teaching abbreviations."""
    fixed = EXPOSURE_IN.get(plan.activity)
    if fixed is not None:
        return fixed
    language = "Latin" if plan.activity == REWRITE_TEXTS else plan.language or "Latin"
    if plan.activity == COPY_BOOK:
        language = plan.language or "Latin"
    wanted = language.lower()
    for ability in character.abilities:
        name = ability.name.lower()
        if name == wanted or name.endswith(f": {wanted}"):
            return ability.name
    return f"Dead Language: {language}" if wanted == "latin" else language


def decode_total_arts(saga: Saga, book: Book) -> tuple[str, str] | None:
    """A Lab Text's Technique and Form: its spell's, else the text's own
    (an enchantment, a Longevity Ritual, a taming or a Discovery)."""
    spell = catalog.find_spell(saga, book.spell_id)
    if spell is not None and spell.technique and spell.form:
        return spell.technique, spell.form
    if book.technique and book.form:
        return book.technique, book.form
    return None
