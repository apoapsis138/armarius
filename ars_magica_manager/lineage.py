"""A magus's line (gap 4): his parens and theirs back as far as the saga
knows them, and his filii and theirs below, from each character's Parens
(Hermetic Background). Shown on the character's sheet as Lineage, for a
magus or apprentice with a parens or a filius in the saga.

Pattern: the tree is a Composite of characters, walked by two plain
functions (up and down).
"""

from __future__ import annotations

from .markup import escape
from .models import Character, Saga

SECTION = "section-char-lineage"
#: How far up and down the line the section goes.
MOST_GENERATIONS = 6


def _named(saga: Saga, name: str) -> Character | None:
    wanted = name.strip().casefold()
    return next((c for c in saga.characters if c.name.casefold() == wanted), None)


def ancestors(saga: Saga, character: Character) -> list[str]:
    """His parens, then theirs, as far as the saga names them (a parens
    who isn't a character of the saga ends the line, by name)."""
    found: list[str] = []
    seen = {character.id}
    name = character.hermetic.parens.strip()
    while name and len(found) < MOST_GENERATIONS:
        found.append(name)
        parent = _named(saga, name)
        if parent is None or parent.id in seen:
            break
        seen.add(parent.id)
        name = parent.hermetic.parens.strip()
    return found


def filii(saga: Saga, character: Character) -> list[Character]:
    """Those who name him as their parens."""
    name = character.name.strip().casefold()
    return [
        c
        for c in saga.characters
        if c is not character and c.hermetic.parens.strip().casefold() == name
    ]


def shown(saga: Saga, character: Character) -> bool:
    return bool(character.hermetic.parens.strip() or filii(saga, character))


def _descent(saga: Saga, character: Character, depth: int, seen: set[str]) -> list[str]:
    lines: list[str] = []
    for child in filii(saga, character):
        if child.id in seen or depth >= MOST_GENERATIONS:
            continue
        seen.add(child.id)
        status = "" if child.type == "magus" else " [dim](apprentice)[/]"
        lines.append(f"{'  ' * depth}- {escape(child.name)}{status}")
        lines += _descent(saga, child, depth + 1, seen)
    return lines


def text(saga: Saga, character: Character) -> str:
    """The line, as markup: the parentes above, the filii below."""
    up = ancestors(saga, character)
    lines: list[str] = []
    if up:
        lines.append("[$label]Parens[/] " + " ← ".join(escape(n) for n in up))
    down = _descent(saga, character, 0, {character.id})
    if down:
        lines.append("[$label]Filii[/]")
        lines += down
    return "\n".join(lines) or "[dim]No parens or filii in the saga.[/]"
