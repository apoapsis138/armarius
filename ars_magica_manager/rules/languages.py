"""Related languages: a character who knows a language close to another
can understand it at a penalty, which falls on both speakers. The three
Tribunal books give the pairs for their lands: The Sundered Eagle p. 42,
Against the Dark p. 10 and Guardians of the Forests p. 138; the same
language in another dialect is -1 in all three. The Definitive Edition
has no such table, so nothing here disagrees with it.

Reading is the same: a Theban magus, Romaic Greek his native tongue,
reads the Classical Greek of the Tribunal's books at Romaic Greek less
2, so he needs Romaic Greek 6 for the effective 4 a book needs (The
Sundered Eagle p. 29). Writing needs the language itself at 5, so a
related one never counts toward it.

A pack names Romaic Greek "Greek" (a Living Language), so both names are
the same language here."""

from __future__ import annotations

from dataclasses import dataclass

from ..models import Character

SOURCE = (
    "The Sundered Eagle p. 42; Against the Dark p. 10; Guardians of the Forests p. 138"
)

#: The penalty for the same language in another dialect.
DIALECT_PENALTY = 1


@dataclass(frozen=True)
class Related:
    """Two related languages, the penalty to understand one through the
    other, and a dialect of `first` that halves the gap (Low German's
    Saxon with East Norse), with its smaller penalty."""

    first: str
    second: str
    penalty: int
    source: str
    dialect: str = ""
    dialect_penalty: int = 0


RELATED: tuple[Related, ...] = (
    Related("romaic greek", "classical greek", 2, "The Sundered Eagle p. 42"),
    Related("vlach", "latin", 3, "The Sundered Eagle p. 42; Against the Dark p. 10"),
    Related("italian", "latin", 3, "The Sundered Eagle p. 42"),
    Related("veneto", "french", 2, "The Sundered Eagle p. 42"),
    Related("veneto", "italian", 3, "The Sundered Eagle p. 42"),
    Related("lingua franca", "veneto", 2, "The Sundered Eagle p. 42"),
    Related("lingua franca", "occitan", 2, "The Sundered Eagle p. 42"),
    Related("kipchak", "oghur", 2, "Against the Dark p. 10"),
    Related("kipchak", "oghuz", 2, "Against the Dark p. 10"),
    Related(
        "low german",
        "high german",
        2,
        "Against the Dark p. 10; Guardians of the Forests p. 138",
    ),
    # Against the Dark gives -3 flat; Guardians of the Forests -2 for
    # the Friesian dialect.
    Related(
        "low german",
        "english",
        3,
        "Against the Dark p. 10; Guardians of the Forests p. 138",
        dialect="friesian",
        dialect_penalty=2,
    ),
    Related(
        "low german",
        "east norse",
        3,
        "Guardians of the Forests p. 138",
        dialect="saxon",
        dialect_penalty=2,
    ),
    Related("high german", "east norse", 4, "Guardians of the Forests p. 138"),
    Related("high german", "english", 4, "Guardians of the Forests p. 138"),
)

#: Other names a language goes by in a save.
ALIASES = {"greek": "romaic greek", "romaic": "romaic greek"}


def language_of(ability_name: str) -> str:
    """The language an Ability names ("Living Language: Greek" -> "romaic
    greek"), in lower case."""
    name = ability_name.strip().lower()
    if ":" in name:
        name = name.split(":", 1)[1].strip()
    return ALIASES.get(name, name)


def penalty(known: str, wanted: str, specialty: str | None = None) -> int | None:
    """The penalty to understand `wanted` through `known` (None: they are
    not related); `specialty` is the known language's dialect."""
    a, b = language_of(known), language_of(wanted)
    if a == b:
        return 0
    dialect = (specialty or "").strip().lower()
    for pair in RELATED:
        if {a, b} != {pair.first, pair.second}:
            continue
        if pair.dialect and a == pair.first and dialect == pair.dialect:
            return pair.dialect_penalty
        return pair.penalty
    return None


def understanding_score(character: Character, language: str) -> int:
    """The character's best effective score in `language`: his own, or a
    related language's less its penalty."""
    best = 0
    for ability in character.abilities:
        if "language" not in ability.name.lower() and ":" in ability.name:
            continue
        lost = penalty(ability.name, language, ability.specialty)
        if lost is not None:
            best = max(best, ability.level - lost)
    return best
