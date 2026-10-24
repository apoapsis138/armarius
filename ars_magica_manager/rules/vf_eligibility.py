"""Who may take a character Virtue or Flaw from the catalog: the
picker's structural eligibility rules (The Gift, grogs, animals, the
audiences an entry is for, the books in play, what the saga hides).
Prose prerequisites ("requires Demonic Blood") are left to the
description."""

from __future__ import annotations

from dataclasses import dataclass

from .. import catalog, sourcebooks
from ..models import Character, Creature, Familiar, VirtueFlawDef
from . import animal_grogs, creation_access

SOURCE = (
    "Ars Magica Definitive Edition, Chapter 4: Virtues and Flaws, Virtues and Flaws "
    "Rules and Guidelines, p. 63"
)

#: Each audience as named in an "only for ..." note.
_AUDIENCE_PLURALS: dict[str, str] = {
    "faerie": "faeries",
    "magic being": "magic beings",
    "corrupted beast": "corrupted beasts",
    "animal": "animals",
    "mythic companion": "Mythic Companions",
}


@dataclass(frozen=True)
class VirtueFlawChooser:
    """Who is choosing from the character Virtue/Flaw catalog, for the
    picker's structural eligibility rules; prose prerequisites
    ("requires Demonic Blood") are left to the description.

    `audiences` are the VIRTUE_FLAW_AUDIENCES this chooser belongs to (an
    entry with an audience is only for those); `books` the sourcebooks in
    play, or None for every book.
    """

    grog: bool = False
    gifted: bool = False
    audiences: frozenset[str] = frozenset()
    books: frozenset[str] | None = None
    #: An animal grog: nothing about human society, and its free Flaws and
    #: Major Personality Flaws (taken as Minor) despite being a grog.
    animal: bool = False

    @classmethod
    def for_character(
        cls, character: Character, books: frozenset[str] | None = None
    ) -> VirtueFlawChooser:
        """A magus counts as Gifted before The Gift is added (the book
        makes every magus take it); anyone else once they hold it."""
        held = {vf.vf_id for vf in character.virtues_flaws}
        mythic = character.type == "mythic companion"
        animal = character.animal is not None
        audiences = frozenset({"mythic companion"}) if mythic else frozenset()
        return cls(
            grog=character.type == "grog",
            gifted=character.type == "magus" or bool(held & catalog.GIFT_IDS),
            audiences=frozenset({"animal"}) if animal else audiences,
            books=books,
            animal=animal,
        )

    @classmethod
    def for_familiar(
        cls, familiar: Familiar, books: frozenset[str] | None = None
    ) -> VirtueFlawChooser:
        held = {vf.vf_id for vf in familiar.virtues_flaws}
        return cls(
            gifted=bool(held & catalog.GIFT_IDS),
            audiences=catalog.FAMILIAR_AUDIENCES,
            books=books,
        )

    @classmethod
    def for_creature(
        cls, creature: Creature, books: frozenset[str] | None = None
    ) -> VirtueFlawChooser:
        held = {vf.vf_id for vf in creature.virtues_flaws}
        return cls(
            gifted=bool(held & catalog.GIFT_IDS),
            audiences=catalog.CREATURE_AUDIENCES,
            books=books,
        )

    def refusal(self, definition: VirtueFlawDef) -> str:
        """Why this chooser can't take `definition`, as a short note ("needs
        The Gift"), or "" if it can."""
        if definition.audience and not self.audiences & set(definition.audience):
            names = [_AUDIENCE_PLURALS[who] for who in definition.audience]
            return "only for " + " or ".join(names)
        if self.grog and definition.id in catalog.GIFT_IDS:
            return "not for grogs"
        if self.animal:
            refused = animal_grogs.refusal(definition, creation_access.OPENS)
            if refused:
                return refused
        elif self.grog and definition.tier == "Major":
            return "not for grogs: Major"
        if self.grog and catalog.needs_the_gift(definition):
            return "not for grogs: Hermetic"
        if not self.gifted and catalog.needs_the_gift(definition):
            return "needs The Gift"
        if not sourcebooks.in_play(definition.source, self.books):
            return "book not in play"
        if catalog.hidden(definition):
            return "hidden in this saga"
        return ""
