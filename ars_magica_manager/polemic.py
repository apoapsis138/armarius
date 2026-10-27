"""A Tribunal's arguments read against the saga: each text's book,
Quality and level, who circulates it, the Argument Total and the debate
bonus it buys, and the bonuses a hearing gives each side (Transforming
Mythic Europe pp. 27-35; the rules are rules.polemic's).

A text is a link to a book in the saga's library: its Quality and level
are read from the book each time, so correcting the book corrects the
argument."""

from __future__ import annotations

from . import catalog
from .models import (
    Argument,
    Book,
    Case,
    Character,
    PolemicText,
    Saga,
    Tribunal,
)
from .models.polemic import AGAINST, FOR, LOST, POLEMIC, WON
from .rules import polemic as rules

#: A text's kind, as the sheet names it.
KIND_NAMES: dict[str, str] = {
    "polemic": "Polemic",
    "diatribe": "Diatribe",
    "apologia": "Apologia",
}

#: The books a text may be: a summa or tractatus on an Ability (TME p. 28).
TEXT_BOOK_TYPES: tuple[str, ...] = ("Ability Summa", "Tractatus")


#: Another name a book may give an Ability the suggestions name.
_ALIASES: dict[str, str] = {
    "organization lore: order of hermes": "order of hermes lore",
}


def knowledge_abilities() -> list[str]:
    """The Abilities an argument may be written on (TME p. 28): the
    book's suggestions first, then the catalog's other knowledge
    Abilities, a templated one ("Area Lore: {region}") by its family's
    name."""
    found = list(rules.SUGGESTED_ABILITIES)
    for entry in catalog.load_ability_catalog():
        if not rules.is_knowledge(entry.category, entry.name):
            continue
        name = entry.name.split(":")[0].strip() if entry.parameters else entry.name
        if name not in found:
            found.append(name)
    return found


def same_ability(wanted: str, written: str) -> bool:
    """Whether a book on `written` is on the argument's Ability `wanted`:
    the same Ability, or one of its family ("Area Lore: the Rhine" for
    "Area Lore")."""
    wanted, written = (
        _ALIASES.get(n.strip().casefold(), n.strip().casefold())
        for n in (wanted, written)
    )
    if written == wanted:
        return True
    return written.startswith(wanted) and written[len(wanted)] in ": ("


def book_of(saga: Saga, text: PolemicText) -> Book | None:
    return next((b for b in saga.books if b.id == text.book_id), None)


def text_books(saga: Saga) -> list[Book]:
    """The saga's summae and tractatus on an Ability: what a text may be."""
    return [b for b in saga.books if b.type in TEXT_BOOK_TYPES]


def quality(saga: Saga, text: PolemicText) -> int:
    book = book_of(saga, text)
    return (book.quality or 0) if book is not None else 0


def level(saga: Saga, text: PolemicText) -> int:
    """The text's level for circulating it (a tractatus counts 5)."""
    book = book_of(saga, text)
    if book is None:
        return 0
    return rules.text_level(book.type, book.level)


def book_words(saga: Saga, text: PolemicText) -> str:
    """ "Tractatus, Code of Hermes Q9", "Summa, Code of Hermes L4 Q11", or
    that its book is gone."""
    book = book_of(saga, text)
    if book is None:
        return "(its book is no longer in the library)"
    on = book.ability or book.art or "?"
    q = f"Q{book.quality}" if book.quality is not None else "Q?"
    if book.type == "Tractatus":
        return f"Tractatus, {on} {q}"
    return f"Summa, {on} L{book.level or 0} {q}"


def author(saga: Saga, text: PolemicText) -> Character | None:
    return saga.character(text.author_id)


def circulator(saga: Saga, text: PolemicText) -> Character | None:
    """Who circulates the text: its sponsor, or its author (TME p. 29)."""
    return saga.character(text.circulated_by_id) or author(saga, text)


def name_of(saga: Saga, character_id: str | None, missing: str = "(no one)") -> str:
    found = saga.character(character_id)
    return found.name if found is not None else missing


def wisdom(argument: Argument) -> int:
    return rules.prevailing_wisdom(argument.reach, argument.magus_reputation)


def counted(saga: Saga, argument: Argument) -> list[rules.Counted]:
    return [
        rules.Counted(t.kind, quality(saga, t), t.circulated) for t in argument.texts
    ]


def total(saga: Saga, argument: Argument) -> int | None:
    """The Argument Total, or None until its polemic is out."""
    return rules.argument_total(wisdom(argument), counted(saga, argument))


def bonus(saga: Saga, argument: Argument) -> int:
    """The debate bonus (or penalty) the argument brings to its next
    debate: none once a debate on it was lost (TME p. 35)."""
    if argument.outcome == LOST:
        return 0
    return rules.debate_bonus(total(saga, argument))


def total_if(saga: Saga, argument: Argument, text: PolemicText) -> int | None:
    """The Argument Total once `text` is out too."""
    texts = [
        rules.Counted(t.kind, quality(saga, t), t.circulated or t is text)
        for t in argument.texts
    ]
    return rules.argument_total(wisdom(argument), texts)


def polemic_of(argument: Argument) -> PolemicText | None:
    """The argument's polemic: the first written."""
    return next((t for t in argument.texts if t.kind == POLEMIC), None)


def case_of(tribunal: Tribunal, argument: Argument) -> Case | None:
    return next((c for c in tribunal.cases if c.id == argument.case_id), None)


def arguments_for(tribunal: Tribunal, case: Case) -> list[Argument]:
    """The arguments that go to `case`."""
    return [a for a in tribunal.arguments if a.case_id and a.case_id == case.id]


def rival(
    tribunal: Tribunal, argument: Argument | None, case_id: str, side: str
) -> Argument | None:
    """Another argument already going to `case_id` for `side`: a case
    hears one argument for each side, since adding several arguments'
    bonuses together is a house rule (TME pp. 31, 33)."""
    if not case_id:
        return None
    return next(
        (
            a
            for a in tribunal.arguments
            if a is not argument and a.case_id == case_id and a.side == side
        ),
        None,
    )


def case_bonuses(saga: Saga, tribunal: Tribunal, case: Case) -> tuple[int, int]:
    """The polemic bonuses at `case`'s hearing: the side for it (its
    prosecutor or proposer), then the side against it. Each side has one
    argument at most; only its first counts."""
    found: dict[str, int] = {}
    for argument in arguments_for(tribunal, case):
        found.setdefault(argument.side, bonus(saga, argument))
    return found.get(FOR, 0), found.get(AGAINST, 0)


def record_outcome(tribunal: Tribunal, case: Case, winner: str | None) -> None:
    """After `case`'s hearing: each argument backing the winning side is
    won, each backing the other lost; with no winner nothing changes
    (TME p. 35)."""
    if winner is None:
        return
    for argument in arguments_for(tribunal, case):
        argument.outcome = WON if argument.side == winner else LOST


def reputation_reach(tribunal: Tribunal, text: PolemicText) -> str:
    """Where a text's Reputation is known: the Tribunal's name, "a House"
    or "the Order"."""
    if text.audience == "tribunal":
        return tribunal.name
    return rules.AUDIENCE_NAMES[text.audience]


def give_reputation(
    tribunal: Tribunal,
    argument: Argument,
    text: PolemicText,
    character: Character | None,
) -> str:
    """Give `character` the text's Reputation (TME pp. 31, 33, 35), unless
    the text has given it him already; what happened, or ""."""
    if character is None or character.id in text.reputation_given:
        return ""
    text.reputation_given.append(character.id)
    name = rules.reputation_name(text.kind, argument.ideal or argument.topic)
    return rules.gain_reputation(character, name, reputation_reach(tribunal, text))


def on_written(
    saga: Saga, tribunal: Tribunal, argument: Argument, text: PolemicText
) -> str:
    """A diatribe's or apologia's Reputation, gained by its author on
    writing it (TME pp. 33, 35); a polemic's waits for its circulation
    (p. 31). What happened, or ""."""
    if not rules.needs_study(text.kind):
        return ""
    return give_reputation(tribunal, argument, text, author(saga, text))


def on_circulated(
    saga: Saga, tribunal: Tribunal, argument: Argument, text: PolemicText
) -> list[str]:
    """The Reputations a text gives once it is out: its author's, unless
    he had it on writing, and for a diatribe or apologia a circulator's
    who isn't its author (TME pp. 31, 33, 35). What happened, in words."""
    given = [give_reputation(tribunal, argument, text, author(saga, text))]
    if rules.needs_study(text.kind):
        given.append(
            give_reputation(
                tribunal, argument, text, saga.character(text.circulated_by_id)
            )
        )
    return [words for words in given if words]


def signed(value: int) -> str:
    """ "+2", "−3", "0"."""
    if value > 0:
        return f"+{value}"
    if value < 0:
        return f"−{-value}"
    return "0"
