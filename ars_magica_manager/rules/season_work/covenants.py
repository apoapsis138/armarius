"""Covenants' library seasons: studying a significato or a realia
collection, an inspeximus on one's own summa, binding a library catalog
and library research."""

from __future__ import annotations

import random

from ... import book_value
from ...models import Character, Saga, SeasonPlan
from .. import activity_groups as groups
from ..rounding import round_down
from ..scores import ability_level
from .base import (
    MAGI,
    SimpleActivity,
    SupplementWork,
    experience_only,
    register,
    source,
    subject_ability,
)

COVENANTS = source("Covenants, Chapter Seven: Library, pp. 84-102", "Covenants")


def _inspeximus_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    book = next((b for b in saga.books if b.id == plan.book_id), None)
    if book is None or book.type not in ("Art Summa", "Ability Summa"):
        return ["Choose the summa to annotate."]
    if book.author != character.name:
        return ["An inspeximus annotates the author's own summa."]
    return []


def _commentary_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    return [
        "Plan Read a book instead: it now adds a commentary's, a "
        "florilegium's or a gloss's Quality bonus itself."
    ]


def _bind_catalog_problems(
    saga: Saga, character: Character, plan: SeasonPlan
) -> list[str]:
    if character.raw_vis.get("vim", 0) < 1:
        return [f"Binding the catalog takes 1 pawn of Vim; {character.name} has none."]
    return []


def _inspeximus(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    book = next(b for b in saga.books if b.id == plan.book_id)
    art = (book.art or "").lower()
    now = (
        character.arts[art].level
        if art in character.arts
        else ability_level(character, book.ability)
    )
    then = plan.book_level if plan.book_level is not None else (book.level or 0) * 2
    new = min(
        (book.level or 0) + round_down(max(0, now - then) / 3), round_down(now / 2)
    )
    result.summa_level = (book.id, new)
    result.notes.append(f"{book.name} annotated: Level {book.level} -> {new}.")


def _bind_catalog(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    result.notes.append(
        "The library catalog bound: an Arcane Connection to the library and "
        "each book in it, for 1 pawn of Vim."
    )


def _library_research(
    saga: Saga,
    character: Character,
    plan: SeasonPlan,
    rng: random.Random | None,
    result: SupplementWork,
) -> None:
    """The research roll's total before the die: Intelligence + the Ability
    + the better of the covenant library's bonus for it and its best
    encyclopedia's (Covenants, Use: Research; Art & Academe,
    Encyclopedias)."""
    name = subject_ability(plan)
    if not name:
        return
    covenant = saga.covenant(character.covenant_id)
    found = (
        book_value.encyclopedias(saga, covenant, name) if covenant is not None else []
    )
    library = (
        book_value.library_level(saga, covenant, name) if covenant is not None else 0
    )
    best = max([library, *(e.bonus for e in found)])
    cited = ""
    if best:
        cited = (
            f"the library +{library}"
            if best == library
            else f"{found[0].name} +{found[0].bonus}"
        )
    total = (
        character.characteristics.intelligence + ability_level(character, name) + best
    )
    text = f"Research roll: Intelligence + {name}"
    text += f" + {cited}" if cited else " (no library bonus)"
    result.notes.append(
        f"{text} = {total} + a die, against the storyguide's Ease Factor."
    )


register(
    SimpleActivity(
        "study_significato",
        "Study a significato",
        "A mystical event studied like vis: the storyguide's Source Quality "
        "(a stress die + the aura).",
        COVENANTS,
        "913",
        None,
        "a stress die + the aura, as for vis",
        MAGI,
        group=groups.STUDY,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "study_realia",
        "Study a realia collection",
        "A collection outside the library (another covenant's exhibit): "
        "read like a tractatus at its Quality, less 1 for two readers "
        "sharing it, 2 up to four...; studied at most Quality times. One the "
        "covenant owns is a library record (a tractatus of the Realia kind), "
        "read with Read a book.",
        COVENANTS,
        "913",
        None,
        "the collection's Quality",
        group=groups.STUDY,
    ),
    experience_only,
)
register(
    SimpleActivity(
        "read_commentary",
        "Read a commentary, florilegium or glossed book",
        "Retired: Read a book adds a commentary's, florilegium's or gloss's "
        "bonus itself.",
        COVENANTS,
        "913",
        None,
        "the book's Quality + the opus bonus",
        retired=True,
        group=groups.STUDY,
    ),
    experience_only,
    _commentary_problems,
)
register(
    SimpleActivity(
        "inspeximus",
        "Write an inspeximus",
        "Annotating your own summa: its Level rises by (your score now - "
        "your score when you wrote it) / 3, up to half your score.",
        COVENANTS,
        "913",
        group=groups.WRITING,
    ),
    _inspeximus,
    _inspeximus_problems,
)
register(
    SimpleActivity(
        "bind_catalog",
        "Bind a library catalog",
        "A season and 1 pawn of Vim: the catalog becomes an Arcane Connection "
        "to the library and each book in it.",
        COVENANTS,
        "913",
        who=MAGI,
        group=groups.WRITING,
    ),
    _bind_catalog,
    _bind_catalog_problems,
)
register(
    SimpleActivity(
        "library_research",
        "Library research",
        "A season searching lab notes or records: Intelligence + the Ability "
        "+ the library's research bonus against the storyguide's Ease "
        "Factor (Exposure 2 in the Ability used).",
        COVENANTS,
        "913",
        group=groups.STUDY,
    ),
    _library_research,
)
