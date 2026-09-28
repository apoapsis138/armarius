"""Deleting the saga's top-level records -- a covenant, character or
laboratory -- and what happens to what they own or are linked to (STORY-108).

Nothing that can stand on its own is deleted with its owner: books become
unassigned, a covenant's characters and laboratories become unassigned, a
laboratory loses its owner. What only makes sense attached to the record goes
with it: a magus's Familiar, a magus's or companion's covenant-side extras on
the Inhabitants tab, a laboratory's sanctum extras on the Possessions tab.
A magus's invented spells that anything else still uses (another character
knows one, or a Lab Text or Casting Tablet holds one) are kept as the saga's
own spells.

Each `*_consequences` function says what deleting would do, for the
confirmation prompt; each `delete_*` does it. Nothing here saves."""

from __future__ import annotations

from . import books as bk
from . import familiars as fam
from .inhabitants import AUTO_KINDS
from .models import Character, Covenant, Laboratory, Saga, Spell


def _count(count: int, noun: str, plural: str | None = None) -> str:
    """ "1 book", "3 books"; `plural` for an irregular one."""
    return f"{count} {noun if count == 1 else plural or noun + 's'}"


def _becomes(count: int) -> str:
    return "becomes" if count == 1 else "become"


def _unassign_books(saga: Saga, kind: str, owner_id: str) -> None:
    for book in bk.books_owned_by(saga, kind, owner_id):
        book.owner_kind = None
        book.owner_id = None


# ------------------------------------------------------------------ character


def spells_still_used(saga: Saga, character: Character) -> list[Spell]:
    """The character's invented spells that something other than the character
    uses: another character knows it, or any Lab Text or Casting Tablet (even
    one of the character's own, which outlives them) holds it."""
    invented = {id(s): s for s in character.invented_spells}
    used: dict[int, Spell] = {}
    for other in saga.characters:
        if other is character:
            continue
        for known in other.spells_known:
            spell = next(
                (s for s in character.invented_spells if s.id == known.spell_id), None
            )
            if spell is not None:
                used[id(spell)] = spell
    for book in saga.books:
        spell = bk.book_spell(saga, book)
        if spell is not None and id(spell) in invented:
            used[id(spell)] = spell
    return [s for s in character.invented_spells if id(s) in used]


def character_consequences(saga: Saga, character: Character) -> list[str]:
    lines: list[str] = []
    familiar = fam.familiar_of(saga, character.id)
    if familiar is not None:
        lines.append(f"Their Familiar, {familiar.name}, is deleted too.")
    labs = [lab for lab in saga.laboratories if lab.owner_id == character.id]
    for lab in labs:
        lines.append(f"{lab.name} no longer has an owner.")
    books = bk.books_owned_by(saga, "character", character.id)
    if books:
        n = len(books)
        lines.append(f"{_count(n, 'book')} they own {_becomes(n)} unassigned.")
    kept = spells_still_used(saga, character)
    if kept:
        n = len(kept)
        moves = "moves" if n == 1 else "move"
        lines.append(
            f"{_count(n, 'invented spell')} still in use {moves} to the saga's "
            "own spells."
        )
    return lines


def delete_character(saga: Saga, character: Character) -> None:
    saga.familiars = [f for f in saga.familiars if f.character_id != character.id]
    for lab in saga.laboratories:
        if lab.owner_id == character.id:
            lab.owner_id = None
    _unassign_books(saga, "character", character.id)
    for covenant in saga.covenants:
        # A magus's or companion's record only holds covenant-side extras for
        # their sheet; a grog's copied name and year born stand on their own.
        covenant.inhabitants = [
            r
            for r in covenant.inhabitants
            if not (r.character_id == character.id and r.kind in AUTO_KINDS)
        ]
        for record in covenant.inhabitants:
            if record.character_id == character.id:
                record.character_id = None
    saga.spells.extend(spells_still_used(saga, character))
    saga.characters = [c for c in saga.characters if c is not character]


# ----------------------------------------------------------------- laboratory


def laboratory_consequences(saga: Saga, lab: Laboratory) -> list[str]:
    lines: list[str] = []
    owner = saga.character(lab.owner_id)
    if owner is not None:
        lines.append(f"{owner.name} no longer has a laboratory.")
    books = bk.books_owned_by(saga, "laboratory", lab.id)
    if books:
        n = len(books)
        lines.append(f"{_count(n, 'book')} kept there {_becomes(n)} unassigned.")
    return lines


def delete_laboratory(saga: Saga, lab: Laboratory) -> None:
    for character in saga.characters:
        if character.assigned_lab_id == lab.id:
            character.assigned_lab_id = None
    _unassign_books(saga, "laboratory", lab.id)
    for covenant in saga.covenants:
        covenant.possessions = [p for p in covenant.possessions if p.lab_id != lab.id]
    saga.laboratories = [x for x in saga.laboratories if x is not lab]


# ------------------------------------------------------------------- covenant


def covenant_consequences(saga: Saga, covenant: Covenant) -> list[str]:
    lines: list[str] = []
    characters = [c for c in saga.characters if c.covenant_id == covenant.id]
    labs = [lab for lab in saga.laboratories if lab.covenant_id == covenant.id]
    books = bk.books_owned_by(saga, "covenant", covenant.id)
    for count, noun, plural in (
        (len(characters), "character", None),
        (len(labs), "laboratory", "laboratories"),
    ):
        if count:
            lines.append(f"{_count(count, noun, plural)} {_becomes(count)} unassigned.")
    if books:
        n = len(books)
        lines.append(f"{_count(n, 'book')} it owns {_becomes(n)} unassigned.")
    lines.append(
        "Its Inhabitants, Possessions and Economics entries are deleted with it."
    )
    return lines


def delete_covenant(saga: Saga, covenant: Covenant) -> None:
    for character in saga.characters:
        if character.covenant_id == covenant.id:
            character.covenant_id = None
    for lab in saga.laboratories:
        if lab.covenant_id == covenant.id:
            lab.covenant_id = None
    _unassign_books(saga, "covenant", covenant.id)
    saga.covenants = [c for c in saga.covenants if c is not covenant]
