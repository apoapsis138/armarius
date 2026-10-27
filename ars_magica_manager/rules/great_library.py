"""The Great Library of Durenmar (Guardians of the Forests: The Rhine
Tribunal pp. 55-57), as plain rules over the dice: who may study there,
the credit a contribution earns, and what a search of its floors finds.

- Access (p. 55): those who study from the Great Library must contribute
  to it. Each new contribution the librarian accepts (a tractatus or a
  new spell is welcomed; a low-level or mediocre summa, or a common
  spell, is not wanted) gives two seasons of free study there, more for
  an exceptional one at his say; a copy will do. A season copying gives
  one season. A "donation" of vis is quietly taken instead of a
  contribution, never acknowledged. Consulting lab notes or the Tribunal
  records needs no credit, and House Bonisagus and the members of
  Durenmar are exempt from it all. Two magi wanting the same book in a
  season: rank decides, then Bonisagus and Durenmar's own, then
  certamen. Books never leave the tower: a book found is lent only for
  the seasons of credit paid for it, and never copied or traded.
- Lab notes (p. 56): a season, and Intelligence + Magic Theory against
  the troupe's Ease Factor; a named author's notes are found in a few
  days, with no roll.
- Tribunal records (p. 56): a season extracts every entry on a narrow
  subject, with no roll; one entry takes an Intelligence + Order of
  Hermes Lore roll a day against the Ease Factor, -1 for each day after
  the first.
- Spells' Lab Texts (pp. 56-57): a stress die against 3 for a standard
  spell (the core book's), 6 for a version of a general standard spell
  up to level 40, 6 to 21 for any other. A standard spell's failure: a
  magus of higher rank has the text this season; its botch: the library
  has none. Any other's failure: none; its botch: one with a serious
  flaw. Exactly the Ease Factor: a magus of equal rank wants it too, and
  certamen decides. Each full six over it: a tractatus on the spell's
  Mastery, of Quality a simple die + 2.
- Enchanted devices' Lab Texts (p. 57): a stress die against 6 to 21:
  meeting it finds a text for a very similar enchantment, beating it by
  6 the very one.
- Tractatus (p. 57): no roll to find one. Quality: a simple die + 2, and
  Durenmar Lore if the reader wishes, -1 for each earlier use of it in
  the same Art; 12 at most is suggested (14 the absolute limit, which the
  storyguide may raise it to).
- Summae (p. 57): on an Art, a simple die + 10 (+3 for a master, a
  Bonisagus or a member of Durenmar, +6 for an archmage), at most 20,
  against the level wanted; failure: none so high (every Art has one of
  level 17 at least) or, likelier, a magus of higher rank has it this
  season; exactly: certamen. On an Arcane Ability, a simple die alone
  against the level; failure: none. Quality: a simple die + 5, + Durenmar
  Lore with the same penalty, at most 30 - the level, or 24, whichever is
  lower (28 the absolute limit, which the storyguide may raise it to).

The Errata (pp. 42-43) correct nothing on pp. 55-57, and the Definitive
Edition has no rule for the Great Library."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from ..models import Character, Saga
from . import dice, rhine_ranks
from .lab import ability_score

SOURCE = (
    "Guardians of the Forests: The Rhine Tribunal pp. 55-57 (Studying in the "
    "Great Library, The Contents of the Great Library); Errata (Ars Magica 5th "
    "Edition) pp. 42-43, nothing on these pages"
)

# -- access and credit (p. 55) --

#: What a magus gives the library for credit.
BOOK, GREAT, COPYING, VIS = "book", "great", "copying", "vis"
CONTRIBUTIONS: tuple[tuple[str, str], ...] = (
    ("A book or Lab Text (2 seasons)", BOOK),
    ("An exceptional work (the librarian's say)", GREAT),
    ("A season copying (1 season)", COPYING),
    ('A vis "donation"', VIS),
)
#: The seasons of free study each earns: two for a contribution, one for
#: a season copying (p. 55). An exceptional work earns more at the
#: librarian's discretion and a vis "donation" stands in for a
#: contribution; the defaults for those two are the form's, to change.
CONTRIBUTION_NAMES = {value: label for label, value in CONTRIBUTIONS}
CREDIT: dict[str, int] = {BOOK: 2, GREAT: 3, COPYING: 1, VIS: 2}

#: The House and the covenant whose magi study without credit (p. 55).
BONISAGUS = "house_bonisagus"
DURENMAR = "Durenmar"
#: Durenmar Lore, as the app names a covenant's lore (TtA writes
#: "Organization Lore: Durenmar"; GotF calls it Durenmar Lore).
DURENMAR_LORE = ("Organization Lore: Durenmar", "Durenmar Lore")


def is_durenmar_member(saga: Saga, magus: Character) -> bool:
    """Whether the magus belongs to Durenmar."""
    covenant = saga.covenant(magus.covenant_id) if magus.covenant_id else None
    return covenant is not None and DURENMAR.lower() in covenant.name.lower()


def is_exempt(saga: Saga, magus: Character) -> bool:
    """House Bonisagus and Durenmar's members study without credit
    (p. 55)."""
    return magus.hermetic.house == BONISAGUS or is_durenmar_member(saga, magus)


def durenmar_lore(magus: Character) -> int:
    """The magus's Durenmar Lore (with any fixed bonus), 0 without it."""
    best = 0
    for name in DURENMAR_LORE:
        score, bonus = ability_score(magus, name)
        best = max(best, score + bonus if score else 0)
    return best


def lore_bonus(lore: int, earlier_uses: int) -> int:
    """What Durenmar Lore adds to a book's Quality: the Lore, -1 for each
    earlier use of it in the same Art or Ability; never below 0, as no one
    adds it to his harm (pp. 57)."""
    return max(0, lore - earlier_uses)


# -- what is sought (pp. 56-57) --

ART_SUMMA, ABILITY_SUMMA, TRACTATUS = "art", "ability", "tractatus"
STANDARD, GENERAL, OTHER_SPELL, DEVICE = "standard", "general", "other", "device"
NOTES, RECORDS = "notes", "records"
SOUGHT: tuple[tuple[str, str], ...] = (
    ("A summa on an Art", ART_SUMMA),
    ("A summa on an Arcane Ability", ABILITY_SUMMA),
    ("A tractatus", TRACTATUS),
    ("A standard spell's Lab Text", STANDARD),
    ("A version of a general standard spell (to level 40)", GENERAL),
    ("Another spell's Lab Text", OTHER_SPELL),
    ("An enchanted device's Lab Text", DEVICE),
    ("Lab notes on a subject", NOTES),
    ("One entry in the Tribunal records", RECORDS),
)
SOUGHT_NAMES = {value: label for label, value in SOUGHT}
#: What needs no credit to consult (p. 55).
FREE = (NOTES, RECORDS)
#: What is a book the planner can study from (summae and tractatus).
BOOKS = (ART_SUMMA, ABILITY_SUMMA, TRACTATUS)
#: The searches whose Ease Factor the troupe sets.
SET_BY_TROUPE = (OTHER_SPELL, DEVICE, NOTES, RECORDS)

#: The fixed Ease Factors of a spell's Lab Text (p. 56).
STANDARD_EASE = 3
GENERAL_EASE = 6
#: A non-standard spell's or a device's Ease Factor: 6 to 21 (pp. 56-57).
LEAST_EASE, MOST_EASE = 6, 21
#: A general spell's version is "standard" up to this level (p. 56).
GENERAL_MAX_LEVEL = 40

#: An Art summa's search: simple die + 10, +3 for a master, a Bonisagus
#: or a member of Durenmar, +6 for an archmage, at most 20 (p. 57).
ART_SEARCH_BASE = 10
PRIVILEGED_BONUS = 3
ARCHMAGE_BONUS = 6
SEARCH_CAP = 20
#: Every Art has a summa of at least this level in the library (p. 57).
EVERY_ART_LEVEL = 17

#: Quality: a summa's simple die + 5, at most min(30 - level, 24) (28 the
#: absolute limit); a tractatus's simple die + 2, at most 12 (14).
SUMMA_QUALITY_BASE = 5
SUMMA_QUALITY_SUM = 30
SUMMA_QUALITY_CAP = 24
SUMMA_QUALITY_LIMIT = 28
TRACTATUS_QUALITY_BASE = 2
TRACTATUS_QUALITY_CAP = 12
TRACTATUS_QUALITY_LIMIT = 14
#: Each full six over a spell's Ease Factor: a Mastery tractatus (p. 57).
MASTERY_STEP = 6
#: A device's very own text needs the Ease Factor beaten by six (p. 57).
EXACT_DEVICE_MARGIN = 6


def art_search_bonus(saga: Saga, magus: Character) -> int:
    """What the magus adds to the simple die + 10 seeking an Art summa:
    +6 an archmage, +3 a master, a Bonisagus or one of Durenmar's (p. 57).
    The archmage's +6 is his whole bonus, not added to the master's."""
    if rhine_ranks.is_archmage(magus):
        return ARCHMAGE_BONUS
    if rhine_ranks.is_master(magus) or is_exempt(saga, magus):
        return PRIVILEGED_BONUS
    return 0


def bonus_reason(saga: Saga, magus: Character) -> str:
    """Why the magus has that bonus, in a word ("" for none)."""
    if rhine_ranks.is_archmage(magus):
        return "an archmage"
    if rhine_ranks.is_master(magus):
        return "a master"
    if magus.hermetic.house == BONISAGUS:
        return "a Bonisagus"
    if is_durenmar_member(saga, magus):
        return "of Durenmar"
    return ""


def art_search_total(die: int, bonus: int) -> int:
    """The Art summa search's total: die + 10 + bonus, at most 20."""
    return min(SEARCH_CAP, die + ART_SEARCH_BASE + bonus)


def ease_of(sought: str, ease: int | None) -> int | None:
    """The Ease Factor of a search for a spell or device: the book's fixed
    3 or 6, else the troupe's (None when not given)."""
    if sought == STANDARD:
        return STANDARD_EASE
    if sought == GENERAL:
        return GENERAL_EASE
    return ease


def summa_quality_cap(level: int) -> int:
    """The highest Quality suggested for a library summa of `level`."""
    return max(1, min(SUMMA_QUALITY_SUM - level, SUMMA_QUALITY_CAP))


def summa_quality(die: int, lore: int, level: int) -> int:
    """A summa's Quality: simple die + 5 + Lore, at most the cap."""
    return min(die + SUMMA_QUALITY_BASE + lore, summa_quality_cap(level))


def tractatus_quality(die: int, lore: int) -> int:
    """A tractatus's Quality: simple die + 2 + Lore, at most 12."""
    return min(die + TRACTATUS_QUALITY_BASE + lore, TRACTATUS_QUALITY_CAP)


def suggested_quality_cap(sought: str, level: int) -> int:
    """The highest Quality suggested for a book found: a tractatus 12, a
    summa the lower of 30 - its level or 24 (p. 57)."""
    if sought == TRACTATUS:
        return TRACTATUS_QUALITY_CAP
    return summa_quality_cap(level)


def absolute_quality_limit(sought: str) -> int:
    """The absolute limit the storyguide may raise a book found to, above
    the suggested cap: a tractatus 14, a summa 28 (p. 57)."""
    return TRACTATUS_QUALITY_LIMIT if sought == TRACTATUS else SUMMA_QUALITY_LIMIT


def mastery_tractatus(margin: int) -> int:
    """The Mastery tractatus found: one for each full six over the Ease
    Factor."""
    return max(0, margin) // MASTERY_STEP


# -- a search and what it finds --

#: How a search turned out, as the Searches list colours it.
FOUND, CERTAMEN, IN_USE, NONE, FLAWED, SIMILAR = (
    "found",
    "certamen",
    "in use",
    "none",
    "flawed",
    "similar",
)
#: Whether each outcome is good, mixed or bad news.
TONES: dict[str, str] = {
    FOUND: "ok",
    SIMILAR: "ok",
    CERTAMEN: "warn",
    IN_USE: "warn",
    FLAWED: "bad",
    NONE: "bad",
}


@dataclass(frozen=True)
class Search:
    """What is sought: the kind (SOUGHT), its Art, Ability, spell or
    subject, the level wanted, the troupe's Ease Factor where it sets one,
    whether Durenmar Lore is added to the Quality and how many times the
    magus has added it before in the same subject."""

    sought: str
    subject: str = ""
    level: int = 0
    ease: int | None = None
    lore: int = 0
    earlier_uses: int = 0
    use_lore: bool = False


@dataclass
class Result:
    """A search's outcome: the outcome (FOUND...), the roll in short ("4 +
    10 + 3 = 17"), what it means, the Quality of a book found, the Mastery
    tractatus found beside a spell's text, and whether Durenmar Lore was
    added."""

    outcome: str
    roll: str
    lines: list[str] = field(default_factory=list)
    quality: int | None = None
    mastery: list[int] = field(default_factory=list)
    lore_used: bool = False

    @property
    def found(self) -> bool:
        return self.outcome in (FOUND, SIMILAR, FLAWED)

    @property
    def tone(self) -> str:
        return TONES[self.outcome]

    def headline(self) -> str:
        """The outcome in a word or two ("Found: Q 11")."""
        word = {
            FOUND: "Found",
            SIMILAR: "A similar one",
            CERTAMEN: "Certamen",
            IN_USE: "In use",
            NONE: "Not there",
            FLAWED: "Flawed",
        }[self.outcome]
        return f"{word}: Q {self.quality}" if self.quality is not None else word


def _quality(rng: random.Random, search: Search, summa: bool, result: Result) -> str:
    """Roll the Quality of a book found; the sum in short ("3 + 2 + 2")."""
    lore = lore_bonus(search.lore, search.earlier_uses) if search.use_lore else 0
    die = dice.simple_die(rng)
    if summa:
        result.quality = summa_quality(die, lore, search.level)
        base = f"simple die {die} + {SUMMA_QUALITY_BASE}"
        cap = f"at most {summa_quality_cap(search.level)}"
    else:
        result.quality = tractatus_quality(die, lore)
        base = f"simple die {die} + {TRACTATUS_QUALITY_BASE}"
        cap = f"at most {TRACTATUS_QUALITY_CAP}"
    penalty = (
        f", -{min(search.earlier_uses, search.lore)} for earlier uses"
        if search.use_lore and search.earlier_uses
        else ""
    )
    with_lore = f" + Durenmar Lore {lore}{penalty}" if search.use_lore else ""
    result.lore_used = search.use_lore
    limit = TRACTATUS_QUALITY_LIMIT if not summa else SUMMA_QUALITY_LIMIT
    result.lines.append(
        f"Quality: {base}{with_lore}, {cap}: {result.quality}. The storyguide may "
        f"raise it to {limit}, the absolute limit (Edit)."
    )
    added = SUMMA_QUALITY_BASE if summa else TRACTATUS_QUALITY_BASE
    return f"{die} + {added}" + (f" + {lore}" if search.use_lore else "")


def search_art_summa(
    rng: random.Random, search: Search, bonus: int, reason: str
) -> Result:
    die = dice.simple_die(rng)
    total = art_search_total(die, bonus)
    extra = f" + {bonus}" if bonus else ""
    capped = " (at most 20)" if die + ART_SEARCH_BASE + bonus > SEARCH_CAP else ""
    roll = f"{die} + {ART_SEARCH_BASE + bonus} = {total}"
    why = f" ({reason})" if reason else ""
    lines = [
        f"Simple die {die} + {ART_SEARCH_BASE}{extra}{why} = {total}{capped} "
        f"against the level {search.level}."
    ]
    if total > search.level:
        result = Result(FOUND, roll, lines)
        _quality(rng, search, True, result)
        return result
    if total == search.level:
        lines.append(
            "Exactly the level: a magus of equal rank wants it this season too; "
            "certamen decides who reads it."
        )
        return Result(CERTAMEN, roll, lines)
    if search.level <= EVERY_ART_LEVEL:
        lines.append(
            "Every Art has a summa of level 17 at least: a magus of higher rank "
            "or privilege is reading it this season."
        )
        return Result(IN_USE, roll, lines)
    lines.append(
        "Either there is none so high, or (more likely) a magus of higher rank "
        "is reading it this season."
    )
    return Result(IN_USE, roll, lines)


def search_ability_summa(rng: random.Random, search: Search) -> Result:
    die = dice.simple_die(rng)
    roll = f"{die} vs {search.level}"
    lines = [f"Simple die {die} alone against the level {search.level}."]
    if die > search.level:
        result = Result(FOUND, roll, lines)
        _quality(rng, search, True, result)
        return result
    if die == search.level:
        lines.append(
            "Exactly the level: a magus of equal rank wants it too; certamen decides."
        )
        return Result(CERTAMEN, roll, lines)
    lines.append("The library has no such summa.")
    return Result(NONE, roll, lines)


def search_tractatus(rng: random.Random, search: Search) -> Result:
    result = Result(
        FOUND,
        "",
        ["No roll to find one: there are dozens on every Art."],
    )
    result.roll = f"Q {_quality(rng, search, False, result)}"
    return result


def search_spell(rng: random.Random, search: Search, saga: Saga | None) -> Result:
    ease = ease_of(search.sought, search.ease) or LEAST_EASE
    die = dice.stress_die(rng, saga=saga)
    shown = "0, a botch" if die.botched else str(die.value)
    roll = f"{'botch' if die.botched else die.value} vs {ease}"
    lines = [f"Stress die {shown} against {ease}."]
    standard = search.sought == STANDARD
    if die.botched:
        if standard:
            lines.append("A botch: the library has no text of it.")
            return Result(NONE, roll, lines)
        lines.append(
            "A botch: there is a text, but it is found to have a serious flaw or "
            "to stray from the effect wanted."
        )
        return Result(FLAWED, roll, lines)
    margin = die.value - ease
    if margin < 0:
        lines.append(
            "A magus of higher rank or privilege has the text this season."
            if standard
            else "The library has no text of it."
        )
        return Result(IN_USE if standard else NONE, roll, lines)
    if margin == 0:
        lines.append(
            "Exactly the Ease Factor: a magus of equal rank wants it this season "
            "too; certamen decides."
        )
        return Result(CERTAMEN, roll, lines)
    result = Result(FOUND, roll, lines)
    for _ in range(mastery_tractatus(margin)):
        result.mastery.append(dice.simple_die(rng) + TRACTATUS_QUALITY_BASE)
    if result.mastery:
        qualities = ", ".join(f"Q {q}" for q in result.mastery)
        lines.append(
            f"{margin} over: {len(result.mastery)} tractatus on its Mastery "
            f"({qualities})."
        )
    return result


def search_device(rng: random.Random, search: Search, saga: Saga | None) -> Result:
    ease = search.ease if search.ease is not None else LEAST_EASE
    die = dice.stress_die(rng, saga=saga)
    shown = "0, a botch" if die.botched else str(die.value)
    roll = f"{'botch' if die.botched else die.value} vs {ease}"
    lines = [f"Stress die {shown} against {ease}."]
    if die.botched or die.value < ease:
        lines.append("No text for such an enchantment is found.")
        return Result(NONE, roll, lines)
    if die.value - ease >= EXACT_DEVICE_MARGIN:
        lines.append("Beaten by 6 or more: a Lab Text for the very enchantment.")
        return Result(FOUND, roll, lines)
    lines.append(
        "A Lab Text for an enchantment very like it; only beating the Ease "
        "Factor by 6 finds the very one."
    )
    return Result(SIMILAR, roll, lines)


def search_notes(
    rng: random.Random, search: Search, magus: Character, saga: Saga | None
) -> Result:
    if search.ease is None:
        return Result(
            FOUND,
            "no roll",
            [
                "A named author's notes: found within a few days of searching, "
                "with no roll (unless access to them is restricted)."
            ],
        )
    intelligence = magus.characteristics.intelligence
    theory = sum(ability_score(magus, "Magic Theory"))
    roll_ = dice.roll(rng, intelligence + theory, ease_factor=search.ease, saga=saga)
    shown = "0, a botch" if roll_.die.botched else str(roll_.die.value)
    roll = f"{roll_.total} vs {search.ease}"
    lines = [
        f"A season's search: Intelligence {intelligence} + Magic Theory {theory} + "
        f"stress die {shown} = {roll_.total} against {search.ease}."
    ]
    if roll_.succeeded:
        lines.append("Notes bearing on the subject are found.")
        return Result(FOUND, roll, lines)
    lines.append("Nothing on the subject is found this season.")
    return Result(NONE, roll, lines)


def search_records(
    rng: random.Random, search: Search, magus: Character, saga: Saga | None
) -> Result:
    if search.ease is None:
        return Result(
            FOUND,
            "a season",
            [
                "A season perusing the records catalogues every entry on the "
                "subject, covenant or magus, with no roll."
            ],
        )
    intelligence = magus.characteristics.intelligence
    lore = sum(ability_score(magus, "Order of Hermes Lore"))
    base = intelligence + lore
    day = 1
    while True:
        # A day's roll: -1 for each day after the first. Once even a 10
        # can't succeed, only a die that explodes could; the search goes on
        # while it could still succeed on a 10.
        modifiers = base - (day - 1)
        attempt = dice.roll(rng, modifiers, ease_factor=search.ease, saga=saga)
        if attempt.succeeded:
            return Result(
                FOUND,
                f"day {day}",
                [
                    f"Intelligence {intelligence} + Order of Hermes Lore {lore} "
                    f"against {search.ease}, -1 a day after the first: found on "
                    f"day {day}."
                ],
            )
        if modifiers + 10 - 1 < search.ease:
            return Result(
                NONE,
                f"{day} days",
                [
                    f"Intelligence {intelligence} + Order of Hermes Lore {lore} "
                    f"against {search.ease}, -1 a day after the first: not found "
                    f"in {day} days. A season extracts every entry on the "
                    "subject with no roll."
                ],
            )
        day += 1


def search(rng: random.Random, saga: Saga, magus: Character, wanted: Search) -> Result:
    """Roll `wanted` for the magus."""
    if wanted.sought == ART_SUMMA:
        return search_art_summa(
            rng, wanted, art_search_bonus(saga, magus), bonus_reason(saga, magus)
        )
    if wanted.sought == ABILITY_SUMMA:
        return search_ability_summa(rng, wanted)
    if wanted.sought == TRACTATUS:
        return search_tractatus(rng, wanted)
    if wanted.sought in (STANDARD, GENERAL, OTHER_SPELL):
        return search_spell(rng, wanted, saga)
    if wanted.sought == DEVICE:
        return search_device(rng, wanted, saga)
    if wanted.sought == NOTES:
        return search_notes(rng, wanted, magus, saga)
    if wanted.sought == RECORDS:
        return search_records(rng, wanted, magus, saga)
    raise ValueError(f"Nothing is sought as {wanted.sought!r} in the Great Library.")


def needs_credit(sought: str) -> bool:
    """Whether studying what is found takes a season of credit: all but
    lab notes and the Tribunal records (p. 55)."""
    return sought not in FREE


def odds(saga: Saga, magus: Character, wanted: Search) -> list[str]:
    """What the search will roll, and what each result means, before the
    dice: the inspector's lines."""
    level = wanted.level
    lore = lore_bonus(wanted.lore, wanted.earlier_uses) if wanted.use_lore else 0
    lore_words = ""
    if wanted.use_lore:
        lore_words = f" + Durenmar Lore {lore}"
        if wanted.earlier_uses:
            lore_words += (
                f" ({wanted.lore}, -{wanted.earlier_uses} for "
                f"{wanted.earlier_uses} earlier use"
                f"{'' if wanted.earlier_uses == 1 else 's'} in this subject)"
            )
    if wanted.sought == ART_SUMMA:
        bonus = art_search_bonus(saga, magus)
        reason = bonus_reason(saga, magus)
        extra = f" + {bonus} ({reason})" if bonus else ""
        need = level - ART_SEARCH_BASE - bonus
        if level >= SEARCH_CAP:
            chance = "it can't be found: the total is at most 20"
        elif need < 1:
            chance = "any die finds it"
        else:
            chance = f"the die must show {need + 1} or more ({need} ties: certamen)"
        return [
            f"Simple die + {ART_SEARCH_BASE}{extra}, at most 20, against the level "
            f"{level}: {chance}.",
            "Fails: none so high, or a magus of higher rank has it this season. "
            "Exactly the level: one of equal rank wants it too; certamen decides.",
            f"Quality: simple die + {SUMMA_QUALITY_BASE}{lore_words}; at most "
            f"{summa_quality_cap(level)} (30 - the level, or 24; 28 the limit).",
            f"Every Art has summae of at least level {EVERY_ART_LEVEL}.",
        ]
    if wanted.sought == ABILITY_SUMMA:
        return [
            f"A simple die alone against the level {level}: "
            + (
                "it can't beat it."
                if level >= 10
                else f"the die must show {level + 1} or more."
            ),
            "Fails: the library has no such summa. Exactly: certamen.",
            f"Quality: simple die + {SUMMA_QUALITY_BASE}{lore_words}; at most "
            f"{summa_quality_cap(level)}.",
        ]
    if wanted.sought == TRACTATUS:
        return [
            f"No roll to find one. Quality: simple die + {TRACTATUS_QUALITY_BASE}"
            f"{lore_words}; {TRACTATUS_QUALITY_CAP} at most suggested "
            f"({TRACTATUS_QUALITY_LIMIT} the limit)."
        ]
    if wanted.sought in (STANDARD, GENERAL, OTHER_SPELL):
        ease = ease_of(wanted.sought, wanted.ease)
        shown = str(ease) if ease is not None else "the troupe's 6 to 21"
        failure = (
            "a failure means a magus of higher rank has it this season; a botch, "
            "that the library hasn't it."
            if wanted.sought == STANDARD
            else "a failure means the library hasn't it; a botch, that it has one "
            "with a serious flaw."
        )
        return [
            f"Stress die against {shown}: {failure}",
            "Exactly the Ease Factor: one of equal rank wants it too; certamen.",
            "Each full 6 over: a tractatus on the spell's Mastery, Quality simple "
            "die + 2.",
        ]
    if wanted.sought == DEVICE:
        shown = str(wanted.ease) if wanted.ease is not None else "the troupe's 6 to 21"
        return [
            f"Stress die against {shown}: meeting it finds a Lab Text for a "
            "similar enchantment; beating it by 6, the very one."
        ]
    if wanted.sought == NOTES:
        if wanted.ease is None:
            return ["A named author's notes: found in a few days, no roll."]
        theory = sum(ability_score(magus, "Magic Theory"))
        return [
            f"A season: Intelligence {magus.characteristics.intelligence} + Magic "
            f"Theory {theory} + stress die against {wanted.ease}. Blank the Ease "
            "Factor for a named author's notes: no roll."
        ]
    lore_score = sum(ability_score(magus, "Order of Hermes Lore"))
    if wanted.ease is None:
        return [
            "A season extracts every entry on the subject, with no roll. Give an "
            "Ease Factor to seek one entry a day instead."
        ]
    return [
        f"Each day: Intelligence {magus.characteristics.intelligence} + Order of "
        f"Hermes Lore {lore_score} + stress die against {wanted.ease}, -1 for "
        "each day after the first."
    ]
