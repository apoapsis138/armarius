"""Which Abilities can be used without experience (DE p. 157): any but
the asterisked ones of the Ability list (DE p. 159), and never a
Supernatural Ability or a hedge Art."""

from __future__ import annotations

import pytest

from ars_magica_manager import catalog
from ars_magica_manager.rules import creation_access

#: The asterisked Abilities of DE p. 159's "Abilities by Type", as the
#: catalog names them (the book's "(Area) Lore" is "Area Lore: {region}").
ASTERISKED = {
    "Area Lore: {region}",
    "Chirurgy",
    "Judaic Lore",
    "Legerdemain",
    "Living Language: {language}",
    "Mystery Cult Lore: {cult}",
    "Organization Lore: {organization}",
    "Art of Memory",
    "Artes Liberales",
    "Civil and Canon Law",
    "Common Law",
    "Dead Language: {language}",
    "Islamic Law",
    "Medicine",
    "Philosophiae",
    "Rabbinic Law",
    "Theology: Christian",
    "Theology: Islam",
    "Theology: Judaism",
    "Code of Hermes",
    "Dominion Lore",
    "Enigmatic Wisdom",
    "Faerie Lore",
    "Faerie Magic",
    "Heartbeast",
    "Infernal Lore",
    "Magic Lore",
    "Magic Theory",
    "Parma Magica",
}

#: The rest of DE p. 159's General, Martial and Arcane lists.
NOT_ASTERISKED = {
    "Animal Handling",
    "Athletics",
    "Awareness",
    "Bargain",
    "Brawl",
    "Carouse",
    "Charm",
    "Concentration",
    "Craft: {craft}",
    "Etiquette",
    "Folk Ken",
    "Guile",
    "Hunt",
    "Intrigue",
    "Leadership",
    "Music",
    "Profession: {profession}",
    "Ride",
    "Stealth",
    "Survival",
    "Swim",
    "Teaching",
    "Bows",
    "Great Weapon",
    "Single Weapon",
    "Thrown Weapon",
    "Finesse",
    "Penetration",
}


def test_the_catalog_marks_the_books_asterisked_abilities() -> None:
    marked = {a.name for a in catalog.load_ability_catalog() if a.needs_experience}
    assert ASTERISKED <= marked, sorted(ASTERISKED - marked)
    assert not NOT_ASTERISKED & marked, sorted(NOT_ASTERISKED & marked)


def test_every_supernatural_ability_and_hedge_art_needs_experience() -> None:
    unmarked = [
        a.name
        for a in catalog.load_ability_catalog()
        if a.category in creation_access.UNTRAINED_NEVER and not a.needs_experience
    ]
    assert not unmarked, unmarked


@pytest.mark.parametrize(
    ("name", "needs"),
    [
        ("Single Weapon", False),
        ("Craft: Blacksmith", False),
        ("Area Lore: Rhine", True),
        ("Magic Theory", True),
        ("Second Sight", True),
        ("Penetration", False),
        ("Something No Book Has", True),
    ],
)
def test_needs_experience_by_name(name: str, needs: bool) -> None:
    assert creation_access.needs_experience(name) is needs
