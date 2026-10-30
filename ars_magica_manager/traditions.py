"""Non-Hermetic magical traditions: which ones a saga offers, which ones a
character belongs to, and which of a character's Abilities make up each
tradition's chapter of the sheet.

A tradition is a catalog record (tradition_catalog.json, a Type Object):
characters name the traditions they belong to, and the tradition says
which Arts and Abilities are its own. A tradition is offered while its
book is in play unless the troupe turns it off (Saga.traditions_off), so
a book put in play brings its traditions on. A character's chapter shows whatever the saga's switches say, so turning a
tradition off never hides what a character already has.
"""

from __future__ import annotations

from . import catalog, sourcebooks
from .models import Ability, Character, Saga, TraditionDef
from .models.mystery_cults import is_saga_cult
from .rules import creation_access as access

#: The sheet ids of a tradition's chapter: its tab, its Arts and Abilities
#: section (the a / e / d section, see actions.SECTION_VERBS), and the
#: section's list.
TAB_PREFIX = "tab-trad-"
SECTION_PREFIX = "section-trad-"
#: The chapter's read-only Casting, Magical Defenses and Seasons sections.
CASTING_PREFIX = "section-tcast-"
DEFENSES_PREFIX = "section-tdef-"
SEASONS_PREFIX = "section-tseas-"
#: The chapter's list of the character's effects and items of the
#: tradition (a / e / d through forms.tradition.effect_ops).
EFFECTS_PREFIX = "section-teff-"
#: The beings bound to the character by the tradition (a / e / d through
#: forms.tradition.bond_ops), the tradition's Warping (read-only), and
#: its pools (Edit, shown only for a tradition that keeps pools).
BONDS_PREFIX = "section-tbond-"
WARPING_PREFIX = "section-twarp-"
POOLS_PREFIX = "section-tpool-"

#: House Ex Miscellanea's catalog id: its magi may belong to its
#: traditions (TraditionDef.hermetic "house").
EX_MISCELLANEA = "house_ex_miscellanea"


def tradition_tab(tradition_id: str) -> str:
    return f"{TAB_PREFIX}{tradition_id}"


def tradition_section(tradition_id: str) -> str:
    return f"{SECTION_PREFIX}{tradition_id}"


def casting_section(tradition_id: str) -> str:
    return f"{CASTING_PREFIX}{tradition_id}"


def defenses_section(tradition_id: str) -> str:
    return f"{DEFENSES_PREFIX}{tradition_id}"


def seasons_section(tradition_id: str) -> str:
    return f"{SEASONS_PREFIX}{tradition_id}"


def effects_section(tradition_id: str) -> str:
    return f"{EFFECTS_PREFIX}{tradition_id}"


def effects_list(tradition_id: str) -> str:
    return f"trad-{tradition_id}-effects"


def bonds_section(tradition_id: str) -> str:
    return f"{BONDS_PREFIX}{tradition_id}"


def bonds_list(tradition_id: str) -> str:
    return f"trad-{tradition_id}-bonds"


def warping_section(tradition_id: str) -> str:
    return f"{WARPING_PREFIX}{tradition_id}"


def pools_section(tradition_id: str) -> str:
    return f"{POOLS_PREFIX}{tradition_id}"


def tradition_list(tradition_id: str) -> str:
    return f"trad-{tradition_id}-list"


def all_traditions() -> list[TraditionDef]:
    """Every tradition in the catalog, in catalog order."""
    return catalog.load_tradition_catalog()


def find(tradition_id: str) -> TraditionDef | None:
    return catalog.load_tradition_catalog_by_id().get(tradition_id)


def in_play(saga: Saga | None) -> list[TraditionDef]:
    """The traditions whose book is in the saga's play: the ones the
    troupe can turn on. The saga's own Mystery Cults aren't among them:
    they are always offered (Saga Content's Mystery Cults tab)."""
    books = sourcebooks.saga_books(saga)
    return [
        t
        for t in all_traditions()
        if sourcebooks.in_play(t.source, books) and not is_saga_cult(t.id)
    ]


def is_on(saga: Saga | None, tradition_id: str) -> bool:
    """Whether the troupe offers the tradition (its book aside): every one
    is, unless turned off."""
    return saga is not None and tradition_id not in saga.traditions_off


def offered(saga: Saga | None) -> list[TraditionDef]:
    """The traditions a character can join in this saga: turned on, and
    their book in play."""
    return [t for t in in_play(saga) if is_on(saga, t.id)]


def joinable(saga: Saga | None, character: Character) -> list[TraditionDef]:
    """The offered traditions the character can be made a member of at
    creation: any for a non-magus; for a magus, the Hermetic societies,
    and House Ex Miscellanea's traditions for one of that House."""
    if character.type != "magus":
        return offered(saga)
    house = character.hermetic.house == EX_MISCELLANEA
    return [
        t
        for t in offered(saga)
        if t.hermetic == "societas" or (house and t.hermetic == "house")
    ]


def set_on(saga: Saga, tradition_id: str, on: bool) -> None:
    """Turn a tradition on or off for the saga, keeping catalog order."""
    off = set(saga.traditions_off)
    if on:
        off.discard(tradition_id)
    else:
        off.add(tradition_id)
    order = [t.id for t in all_traditions()]
    known = [i for i in order if i in off]
    # An id the catalog no longer has stays, at the end, for when it returns.
    saga.traditions_off = known + sorted(off - set(order))


def book_of(tradition: TraditionDef, saga: Saga | None) -> str:
    """The book a tradition is listed under: the first its record cites
    that the saga has in play, else the first it cites (Hedge Magic,
    Revised Edition when it cites none). A tradition is offered through
    any of its books, so it is greyed out only when none is in play."""
    books = sourcebooks.saga_books(saga)
    cited = [sourcebooks.first_book(part) for part in tradition.source.split(";")]
    found = [book for book in cited if book is not None]
    playing = [book for book in found if sourcebooks.in_play(book, books)]
    return (playing or found or ["HMRE"])[0]


def listed(saga: Saga | None) -> list[TraditionDef]:
    """Every non-Hermetic tradition, its book in play or not, by book in
    the Books chapter's order (catalog order within a book). The saga's
    own Mystery Cults aren't among them."""
    shown = [t for t in all_traditions() if not is_saga_cult(t.id)]
    under = {t.id: book_of(t, saga) for t in shown}
    books = sourcebooks.in_order(under.values())
    return [t for book in books for t in shown if under[t.id] == book]


def set_book_on(saga: Saga, book: str, on: bool) -> None:
    """Turn every tradition listed under `book` on or off."""
    for tradition in listed(saga):
        if book_of(tradition, saga) == book:
            set_on(saga, tradition.id, on)


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
