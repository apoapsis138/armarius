"""The Definitive Edition's creatures (DE pp. 428-492), and the animals
Lords of Men prints (its pets, hounds, horses and hawks, LoM pp. 45-59),
as stat blocks to pick in the Bestiary: each entry of
data/bestiary_catalog.json is a template, copied into the saga when chosen
(the Prototype pattern, as a character template is), never shared. An
entry with a "book" is that book's (a SOURCEBOOKS abbreviation) and is
offered only while the book is in play; one without is the DE's.

An entry gives the block in the Tribunal packs' notation (book_packs.
builder): "characteristics" in the book's order, "virtues_flaws" (with the
Qualities and Inferiorities) by their catalog names, "abilities" as
[name, score, specialty], "traits" and "reputations" as {name: score},
"attacks" as [name, Init, Attack, Defense, Damage] (null for n/a), and
"powers" with their Might cost, Init, Form, Range/Duration/Target and what
they do, in the app's own words.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from typing import Any

from . import DATA_DIR, sourcebooks
from .book_packs.builder import (
    ability_from_block,
    characteristics,
    virtue_flaw_from_block,
)
from .models import (
    FULL,
    BodyVis,
    Characteristics,
    Creature,
    CreatureAttack,
    CreaturePower,
    ScoredTrait,
    new_instance_id,
)

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 13: Bestiary, pp. 428-492; "
    "Lords of Men pp. 45, 50, 55-56, 59 (Errata p. 74)"
)
#: The groups the Bestiary's picker lists the book's creatures under.
GROUPS = ("Mundane Beasts", "Magic", "Faerie", "Infernal", "Divine")


@dataclass(frozen=True)
class BookCreature:
    """One stat block of a book: its key, name, group, the book it is from
    and its printed page, and the entry it is built from."""

    key: str
    name: str
    group: str
    page: int
    entry: dict[str, Any]
    book: str = sourcebooks.CORE

    def page_ref(self) -> str:
        """Its page, with the book named unless it is the DE's."""
        if self.book == sourcebooks.CORE:
            return f"p. {self.page}"
        return f"{self.book} p. {self.page}"

    def label(self) -> str:
        might = self.entry.get("might") or 0
        realm = self.entry.get("realm") or ""
        what = f"{realm} {might}" if realm else "mundane"
        return f"{self.name} ({what}, {self.page_ref()})"


@cache
def catalog() -> tuple[BookCreature, ...]:
    """Every creature of the book, in the book's order."""
    path = DATA_DIR / "bestiary_catalog.json"
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    found: list[BookCreature] = []
    for entry in data["entries"]:
        group = entry.get("group", "")
        if group not in GROUPS:
            raise ValueError(f"{entry.get('key')!r}: unknown group {group!r}")
        book = entry.get("book") or sourcebooks.CORE
        if book not in sourcebooks.SOURCEBOOKS:
            raise ValueError(f"{entry.get('key')!r}: unknown book {book!r}")
        found.append(
            BookCreature(
                entry["key"], entry["name"], group, int(entry["page"]), entry, book
            )
        )
    return tuple(found)


def by_key(key: str) -> BookCreature | None:
    return next((c for c in catalog() if c.key == key), None)


def options(books: frozenset[str] | None = None) -> list[tuple[str, str]]:
    """(label, key) for a picker, group by group: the creatures of the
    books in play (`books`, as sourcebooks.saga_books; None: every book)."""
    return [
        (f"{c.group}: {c.label()}", c.key)
        for c in sorted(catalog(), key=lambda c: GROUPS.index(c.group))
        if sourcebooks.in_play(c.book, books)
    ]


def build(book: BookCreature) -> Creature:
    """A new creature for the saga, a copy of the book's stat block."""
    e = book.entry
    realm = e.get("realm") or ""
    confidence = e.get("confidence")
    creature = Creature(
        id=new_instance_id(),
        name=book.name,
        many=bool(e.get("how_many")),
        how_many=e.get("how_many") or "",
        realm=realm,
        might=int(e.get("might") or 0) if realm else 0,
        might_form=(e.get("form") or "") if realm else "",
        size=int(e.get("size") or 0),
        season=e.get("season") or "",
        cunning=bool(e.get("cunning")),
        age=e.get("age") or "",
        confidence_score=confidence[0] if confidence else None,
        confidence_points=confidence[1] if confidence else 0,
        soak=int(e.get("soak") or 0),
        fatigue_levels=e.get("fatigue_levels") or "",
        tires=e.get("tires", True),
        can_be_wounded=e.get("can_be_wounded", True),
        encumbrance=e.get("encumbrance") or "",
        equipment=e.get("equipment") or "",
        appearance=e.get("appearance") or "",
        notes=e.get("notes") or "",
        order=e.get("order") or "",
        hierarchy=e.get("hierarchy"),
        weakness=e.get("weakness") or "",
        source=(
            f"ArM5 DE p. {book.page}"
            if book.book == sourcebooks.CORE
            else f"{book.book} p. {book.page}"
        ),
        detail=FULL,
    )
    block = e.get("block") or {}
    creature.characteristics = Characteristics(
        **characteristics(*block.get("characteristics", [0] * 8))
    )
    creature.virtues_flaws = [
        virtue_flaw_from_block(v if isinstance(v, str) else (v[0], v[1]))
        for v in block.get("virtues_flaws", [])
    ]
    creature.abilities = [
        ability_from_block(name, score, specialty or "")
        for name, score, specialty in block.get("abilities", [])
    ]
    creature.personality_traits = [
        ScoredTrait(n, s) for n, s in block.get("traits", {}).items()
    ]
    creature.reputations = [
        ScoredTrait(n, s) for n, s in block.get("reputations", {}).items()
    ]
    creature.attacks = [CreatureAttack(*a) for a in e.get("attacks", [])]
    creature.powers = [
        CreaturePower(
            p["name"],
            might_cost=int(p.get("might_cost") or 0),
            init=int(p.get("init") or 0),
            form=p.get("form") or "",
            range=p.get("range") or "",
            duration=p.get("duration") or "",
            target=p.get("target") or "",
            level=p.get("level"),
            penetration_bonus=int(p.get("penetration_bonus") or 0),
            description=p.get("does") or "",
        )
        for p in e.get("powers", [])
    ]
    creature.vis = [BodyVis(int(v[0]), v[1], v[2]) for v in e.get("vis", [])]
    return creature
