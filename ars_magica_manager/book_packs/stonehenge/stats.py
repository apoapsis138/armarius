"""Generated stats for the Tribunal's magi (S11): Heirs to Merlin prints
no statistics, so every magus is built from a profile of the book's
paragraph (book_packs.generated), at the age covenants.py gives, picked
inside the book's band (p. 117: young 0-30 years past Gauntlet, mature
20-70, old 50-100, ancient over 80). Each sheet says it is not an
official write-up. The Redcaps and natural magicians are companion
sketches, as the generator stats only magi."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..generated import Profile, apply

if TYPE_CHECKING:
    from ..records import Records

ENGLISH, WELSH, FRENCH = "English", "Welsh", "Norman French"

PROFILES: dict[str, Profile] = {
    # Blackthorn
    "talion": Profile(
        strong="int sta",
        arts={"Pe": 10, "Vi": 4, "Co": 4},
        abilities={"Leadership": (4, "the Tribunal")},
        native=WELSH,
    ),
    "iudicium": Profile(
        strong="int per",
        arts={"In": 9, "Me": 8},
        abilities={
            "Code of Hermes": (7, "the Peripheral Code"),
            "Intrigue": (4, "Hermetic politics"),
        },
        native=WELSH,
    ),
    "golias": Profile(
        strong="pre com",
        arts={"Im": 5, "Me": 5, "Mu": 4},
        abilities={"Intrigue": (6, "Hermetic politics"), "Guile": (5, "seeming young")},
        native=WELSH,
    ),
    "goliard": Profile(
        strong="int pre",
        arts={"Re": 7, "Te": 6, "Au": 5, "Aq": 4},
        abilities={"Bargain": (5, "covenants"), "Magic Lore": (4, "elementals")},
        native=WELSH,
    ),
    "fornax": Profile(
        strong="int pre",
        weak="com",
        arts={"Re": 7, "Me": 7},
        abilities={"Folk Ken": (3, "servants")},
        native=WELSH,
    ),
    "prelum": Profile(
        strong="int com",
        arts={"Vi": 9, "Re": 4},
        abilities={"Etiquette": (4, "magi")},
        native=WELSH,
    ),
    # Burnham
    "aindread": Profile(
        strong="int sta", arts={"Re": 4, "In": 4, "Vi": 4}, native=ENGLISH
    ),
    "caitlin": Profile(
        strong="com int",
        arts={"Me": 4, "In": 4},
        abilities={"Etiquette": (4, "magi")},
        native=ENGLISH,
    ),
    "focus": Profile(strong="sta int", arts={"Cr": 5, "Ig": 6}, native=ENGLISH),
    "scintilla": Profile(
        strong="int sta", arts={"Cr": 7, "Ig": 10, "Pe": 4}, native="Hungarian"
    ),
    "sachiko": Profile(strong="int pre", arts={"Mu": 4, "Im": 4}, native=ENGLISH),
    "trutina": Profile(
        strong="int per",
        arts={"In": 7, "Me": 6},
        abilities={"Code of Hermes": (6, "quaesitorial neutrality")},
        native=ENGLISH,
    ),
    # Cad Gadu
    "ebroin": Profile(
        strong="int pre",
        arts={"Re": 4, "Me": 4, "Vi": 4},
        abilities={
            "Leadership": (3, "the House"),
            "Intrigue": (3, "the Council of Four"),
        },
        native=FRENCH,
    ),
    "gharad": Profile(
        strong="int sta", weak="per", arts={"In": 5, "Vi": 5, "Im": 4}, native=WELSH
    ),
    "gwrhyr": Profile(
        strong="sta pre", weak="int", arts={"Re": 5, "Vi": 3}, native=WELSH
    ),
    "culhwch": Profile(
        strong="str sta", arts={"Cr": 5, "Ig": 7, "Pe": 4}, native=WELSH
    ),
    "findabair": Profile(
        strong="pre com",
        arts={"Mu": 4, "Co": 4, "Im": 3},
        abilities={"Charm": (4, "seduction"), "Carouse": (3, "feasting")},
        native=WELSH,
    ),
    # Libellus
    "stephen_eruditus": Profile(
        strong="int pre",
        arts={"In": 6, "Me": 5, "Im": 4},
        abilities={"Leadership": (4, "young magi"), "Etiquette": (4, "magi")},
        native="High German",
    ),
    "meles": Profile(native=ENGLISH),
    "gregorius": Profile(native=ENGLISH),
    "lucidia": Profile(arts={"Cr": 4, "Ig": 5}, native=ENGLISH),
    "jonaquil": Profile(native=ENGLISH),
    "justin": Profile(native=ENGLISH),
    "fabricor": Profile(native=ENGLISH),
    # Nigrasaxa
    "maximianus": Profile(
        strong="int sta",
        arts={"Cr": 9, "Co": 10, "Mu": 6, "Pe": 5},
        abilities={
            "Magic Theory": (8, "Corpus"),
            "Intrigue": (3, "the Order's politics"),
        },
        native="Italian",
    ),
    "siffed": Profile(native=ENGLISH),
    "ariel": Profile(arts={"Cr": 4, "Ig": 5}, native=ENGLISH),
    "morlen": Profile(native=ENGLISH),
    "caltis": Profile(native=ENGLISH),
    "herrit": Profile(native=ENGLISH),
    "thamik": Profile(native=ENGLISH),
    # Schola Pythagoranis
    "edward_of_milton": Profile(
        strong="com int",
        arts={"Me": 7, "Pe": 3},
        abilities={
            "Teaching": (7, "apprentices"),
            "Artes Liberales": (5, "disputation"),
            "Theology: Christian": (3, "exorcism"),
        },
        native=ENGLISH,
        shares=(0.4, 0.5, 0.1),
    ),
    "astrolabe": Profile(
        strong="int per",
        arts={"In": 6, "Vi": 5, "Te": 4},
        abilities={
            "Philosophiae": (8, "natural philosophy"),
            "Magic Theory": (7, "its physics"),
        },
        native=ENGLISH,
        shares=(0.45, 0.45, 0.1),
    ),
    "lumen": Profile(
        strong="int per",
        arts={"In": 4, "Im": 4},
        abilities={
            "Profession: Scribe": (4, "copying"),
            "Artes Liberales": (4, "classical authors"),
        },
        native=ENGLISH,
    ),
    "fredegisa": Profile(
        strong="int com",
        arts={"In": 5, "Me": 5},
        abilities={
            "Code of Hermes": (6, "reform"),
            "Civil and Canon Law": (4, "canon law"),
        },
        native=ENGLISH,
    ),
    # Semitae
    "gerfallon": Profile(
        strong="int per",
        arts={"Mu": 6, "Co": 5, "Te": 5, "Me": 5},
        abilities={
            "Enigmatic Wisdom": (7, "the road"),
            "Animal Handling": (3, "horses"),
        },
        native=WELSH,
    ),
    "vanasalus": Profile(
        strong="com pre",
        arts={"Cr": 3, "Me": 3},
        abilities={"Enigmatic Wisdom": (3, "kindness")},
        native=ENGLISH,
    ),
    "junius": Profile(
        strong="int dex",
        arts={"Cr": 6, "Te": 7, "Ig": 5, "Re": 5},
        abilities={
            "Craft: Smith": (6, "wagons"),
            "Magic Theory": (7, "enchanting devices"),
        },
        native=ENGLISH,
    ),
    "edward_the_white": Profile(
        strong="pre com",
        arts={"In": 4, "Re": 4},
        abilities={"Survival": (4, "far lands")},
        virtues=[],
        native=ENGLISH,
    ),
    # Ungulus
    "flavius": Profile(
        strong="int pre",
        arts={"Re": 4, "Vi": 4},
        abilities={"Intrigue": (3, "Hermetic politics")},
        native=ENGLISH,
    ),
    "aquila": Profile(
        strong="per sta",
        arts={"Mu": 6, "An": 7, "Au": 5},
        abilities={"Heartbeast": (6, "the eagle")},
        native=ENGLISH,
    ),
    "sinead": Profile(
        strong="sta qik",
        arts={"Pe": 7, "An": 7, "Cr": 5, "Ig": 5},
        abilities={"Penetration": (6, "Animal")},
        native="Irish",
    ),
    "viator": Profile(
        strong="int com",
        arts={"In": 6, "Me": 6, "Im": 5, "Vi": 5},
        abilities={"Magic Theory": (7, "communication")},
        native=ENGLISH,
    ),
    "espera": Profile(
        strong="int per",
        arts={"Mu": 6, "Co": 6, "Vi": 4},
        abilities={"Faerie Lore": (5, "faerie lords")},
        native=ENGLISH,
    ),
    # Voluntas
    "julia": Profile(
        strong="int com",
        arts={"Co": 7, "Me": 7, "In": 4, "Re": 4},
        abilities={"Intrigue": (7, "Hermetic politics"), "Bargain": (4, "covenants")},
        native=FRENCH,
    ),
    "corvus": Profile(
        strong="per int",
        arts={"In": 8, "An": 5, "Mu": 4},
        abilities={"Heartbeast": (5, "the raven"), "Awareness": (4, "secrets")},
        native=ENGLISH,
    ),
    "kirist": Profile(strong="sta qik", arts={"Cr": 5, "Ig": 7}, native=ENGLISH),
    "phessallia": Profile(
        strong="int sta",
        arts={"Pe": 8, "Au": 5, "Aq": 5},
        abilities={"Faerie Lore": (5, "winter faeries")},
        native=ENGLISH,
    ),
    "desiderius": Profile(
        strong="int sta",
        weak="com",
        arts={"Cr": 5, "Co": 7, "Me": 6, "Re": 5},
        abilities={"Magic Theory": (6, "necromancy")},
        native=FRENCH,
    ),
}


def stats(records: Records) -> None:
    for key, profile in PROFILES.items():
        character = records.magi.get(key)
        if character is not None:
            apply(records.b, character, profile)
