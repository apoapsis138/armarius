"""Non-Hermetic magical traditions: which ones a saga offers, which ones a
character belongs to, and which of a character's Abilities make up each
tradition's chapter of the sheet.

A tradition is a catalog record (tradition_catalog.json, a Type Object):
characters name the traditions they belong to, and the tradition says
which Arts and Abilities are its own. The troupe turns each tradition on
for the saga (Saga.traditions); it is offered only while it is on and its
book is in play, so a saga lists just the traditions it uses. A
character's chapter shows whatever the saga's switches say, so turning a
tradition off never hides what a character already has.
"""

from __future__ import annotations

from . import catalog, sourcebooks
from .models import Ability, Character, Saga, TraditionDef
from .rules import creation_access as access

#: The sheet ids of a tradition's chapter: its tab, its Arts and Abilities
#: section (the a / e / d section, see actions.SECTION_VERBS), and the
#: section's list.
TAB_PREFIX = "tab-trad-"
SECTION_PREFIX = "section-trad-"


def tradition_tab(tradition_id: str) -> str:
    return f"{TAB_PREFIX}{tradition_id}"


def tradition_section(tradition_id: str) -> str:
    return f"{SECTION_PREFIX}{tradition_id}"


def tradition_list(tradition_id: str) -> str:
    return f"trad-{tradition_id}-list"


def section_tradition(section: str | None) -> str | None:
    """The tradition whose chapter section `section` is, or None."""
    if section and section.startswith(SECTION_PREFIX):
        return section.removeprefix(SECTION_PREFIX)
    return None


def all_traditions() -> list[TraditionDef]:
    """Every tradition in the catalog, in catalog order."""
    return catalog.load_tradition_catalog()


def find(tradition_id: str) -> TraditionDef | None:
    return catalog.load_tradition_catalog_by_id().get(tradition_id)


def in_play(saga: Saga | None) -> list[TraditionDef]:
    """The traditions whose book is in the saga's play: the ones the
    troupe can turn on."""
    books = sourcebooks.saga_books(saga)
    return [t for t in all_traditions() if sourcebooks.in_play(t.source, books)]


def is_on(saga: Saga | None, tradition_id: str) -> bool:
    """Whether the troupe has turned the tradition on (its book aside)."""
    return saga is not None and tradition_id in saga.traditions


def offered(saga: Saga | None) -> list[TraditionDef]:
    """The traditions a character can join in this saga: turned on, and
    their book in play."""
    return [t for t in in_play(saga) if is_on(saga, t.id)]


def set_on(saga: Saga, tradition_id: str, on: bool) -> None:
    """Turn a tradition on or off for the saga, keeping catalog order."""
    chosen = set(saga.traditions)
    if on:
        chosen.add(tradition_id)
    else:
        chosen.discard(tradition_id)
    order = [t.id for t in all_traditions()]
    known = [i for i in order if i in chosen]
    # An id the catalog no longer has stays, at the end, for when it returns.
    saga.traditions = known + sorted(chosen - set(order))


def of(character: Character) -> list[TraditionDef]:
    """The traditions the character belongs to that the catalog knows."""
    found = (find(i) for i in character.traditions)
    return [t for t in found if t is not None]


def chapter_rows(
    character: Character, tradition: TraditionDef
) -> list[tuple[int, Ability]]:
    """The character's Abilities that belong to the tradition's chapter,
    with their indexes in character.abilities, in the tradition's order."""
    order = {name: n for n, name in enumerate(tradition.abilities)}
    rows = [
        (index, ability)
        for index, ability in enumerate(character.abilities)
        if ability.name in order
    ]
    rows.sort(key=lambda row: (order[row[1].name], row[0]))
    return rows


def claimed(character: Character) -> frozenset[str]:
    """The names of the Abilities the character's tradition chapters show,
    which the Abilities chapter therefore leaves out."""
    return frozenset(
        ability.name
        for tradition in of(character)
        for _, ability in chapter_rows(character, tradition)
    )


#: A tradition chapter's headings, by the role its Arts play (AbilityDef.role);
#: an Ability with no role sits under "Abilities", after the Arts.
ROLE_HEADINGS: dict[str, str] = {
    "Technique": "Techniques",
    "Form": "Forms",
    "Method": "Methods",
    "Power": "Powers",
    "Rune": "Runes",
    "Practice": "Practice Arts",
    "Foe": "Foe Arts",
    "": "Abilities",
}


def chapter_groups(
    character: Character, tradition: TraditionDef
) -> list[tuple[str, list[tuple[int, Ability]]]]:
    """The tradition's chapter as headed groups (sheet_text's
    grouped_ability_rows): its Arts by role, then its other Abilities."""
    groups: dict[str, list[tuple[int, Ability]]] = {}
    for index, ability in chapter_rows(character, tradition):
        entry = access.ability_def(ability.name)
        role = entry.role if entry is not None else ""
        groups.setdefault(ROLE_HEADINGS.get(role, role), []).append((index, ability))
    order = list(ROLE_HEADINGS.values())
    return sorted(
        groups.items(), key=lambda g: order.index(g[0]) if g[0] in order else 0
    )
