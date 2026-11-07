"""Magi of Hermes, chapters one to five: Alexander and Aurulentus of Jerbiton,
Conscientia of Bonisagus, Gwidion of Verditius and Hugh of Flambeau, at every
age the book prints. Stat blocks are the book's, with the errata applied (MoH
pp. 6-51; Errata pp. 12, 69-72); the rest is a summary, not its words.

A spell a block prints under a misspelt name goes in under the catalog's. Each
magus's spells are one table saying from which block a spell is known, since
they keep what they learn; casting totals have no place on the sheet."""

from __future__ import annotations

import re
from typing import Any, NamedTuple

from ..builder import (
    StatBlock,
    arts_from,
    characteristics,
    paragraphs,
    titled,
    vf_ability,
    vf_art,
    vf_focus,
    vf_great,
    vf_puissant,
)
from . import Magus, Printing

#: The book's short names for Abilities, as the sheet names them.
_ABILITY_NAMES = {
    "Arabic": "Living Language: Arabic",
    "Ethiopian": "Living Language: Ethiopian",
    "French": "Living Language: French",
    "Greek": "Living Language: Greek",
    "High German": "Living Language: High German",
    "Native Language": "Living Language: (Native)",
    "Sicilian": "Living Language: Sicilian",
    "Welsh": "Living Language: Welsh",
    "Latin": "Dead Language: Latin",
    "(Apprenticeship Covenant) Lore": "Area Lore: (Apprenticeship Covenant)",
    "(Area) Lore": "Area Lore: (Area)",
    "(Home Covenant) Lore": "Area Lore: (Home Covenant)",
    "Ethiopian Lore": "Area Lore: Ethiopia",
    "North Africa Lore": "Area Lore: North Africa",
    "Legion of Mithras Lore": "Organization Lore: Legion of Mithras",
    "Order of Hermes Lore": "Organization Lore: Order of Hermes",
    "Masonry": "Craft: Masonry",
}
_ABILITY = re.compile(r"(.+?) (\d+)(?:\+\d+)? \((.+)\)")


class _Spell(NamedTuple):
    """A spell in a magus's table: known from block `since` (0 is the first
    the book prints) to block `until`."""

    name: str
    arts: str
    level: int
    since: int
    masteries: tuple[str, ...]
    until: int


def _s(
    name: str,
    arts: str,
    level: int,
    since: int = 0,
    *masteries: str,
    until: int = 99,
) -> _Spell:
    return _Spell(name, arts, level, since, masteries, until)


def _words(text: str) -> str:
    """`text` as one line, however it was wrapped in the source."""
    return " ".join(text.split())


def _abilities(text: str) -> list[tuple[str, int, str]]:
    """The Abilities of a block, "Name 3 (specialty); ...": a "+2" after a
    score is the Puissant Virtue's, which the sheet adds itself."""
    found = []
    for entry in _words(text).split(";"):
        match = _ABILITY.fullmatch(entry.strip())
        if match is None:
            raise ValueError(f"Not an Ability: {entry!r}")
        name, score, specialty = match.groups()
        found.append((_ABILITY_NAMES.get(name, name), int(score), specialty))
    return found


def _rules(text: str) -> dict[str, str]:
    """A table of new spells, a blank line between entries, each "Name =
    what it does"."""
    found = {}
    for entry in text.strip().split("\n\n"):
        name, _, words = entry.partition(" = ")
        found[_words(name)] = _words(words)
    return found


def _stat(
    common: StatBlock,
    spells: tuple[_Spell, ...],
    index: int,
    rules: dict[str, str],
    **own: Any,
) -> StatBlock:
    """Block `index` of a magus: what all their blocks share, its own
    entries, the spells known by then, and the rules of the new ones."""
    known = [s for s in spells if s.since <= index <= s.until]
    block = {**common, **own}
    block["spells"] = [(s.name, s.arts, s.level, len(s.masteries)) for s in known]
    block["masteries"] = {s.name: list(s.masteries) for s in known if s.masteries}
    entries = [f"{s.name}: {rules[s.name]}" for s in known if s.name in rules]
    if entries:
        block["notes"] = paragraphs(
            block.get("notes", ""), "New spells:\n" + "\n".join(entries)
        )
    return block


# Alexander of Jerbiton (pp. 6-14)

_ALEXANDER: StatBlock = {
    "characteristics": characteristics(2, 0, 0, 1, 0, 2, 0, 0),
    "confidence": (1, 3),
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        vf_focus("Major Magical Focus", "transforming humans into animals"),
        "Subtle Magic",
        "Well-Traveled",
        ("Deficient Technique", {"technique": "Perdo"}),
        "Weak Enchanter",
    ],
}
_ALEXANDER_SPELLS = (
    _s("Recruiting A Tiny Phalanx", "CrAn(Re)", 35, 2),
    _s("Sailor's Foretaste of the Morrow", "InAn", 20, 4),
    _s("Opening the Tome of the Animal's Mind", "MuAn", 25, 4),
    _s("The Voice of the Bjornaer Magus", "MuAn", 15),
    _s("Beast of Miniscule Proportions", "MuAn", 20),
    _s("Scales of the Scorpions", "MuAn", 40, 2),
    _s("Circle of Beast Warding", "ReAn", 5),
    _s("The Gentle Beast", "ReAn", 25, 2),
    _s("Bag of Teeth", "MuAq(An)", 20, 5),
    _s("Cloak of the Duck's Feathers", "ReAq", 5),
    _s("Movement Within the Sirocco", "ReAu", 25, 3),
    _s("Ward Against the Sirocco", "ReAu", 25, 3),
    _s("Bind Wound", "CrCo", 10),
    _s("Whispers Through the Black Gate", "InCo(Me)", 15, 4),
    _s("Eyes of the Housecats", "MuCo(An)", 20, 2),
    _s("The Guardian of the Tombs", "MuCo(An)", 20),
    _s("The Desert Wanderer", "MuCo(An)", 25),
    _s("The Lurker in the Rushes", "MuCo(An)", 30, 2),
    _s("The Shadow on the Sand", "MuCo(An)", 30, 1, "Quiet Casting"),
    _s("Retreat As Flying Vermin", "MuAn(Co)", 35, 4),
    _s("A Punishment for Brigands", "MuCo(An)", 40, 1, "Penetration"),
    _s("A Source of Tremendous Pride", "MuCo(An)", 45, 2),
    _s("Bag of Feathers", "MuHe(An)", 35, 5),
    _s("Conflagratious Lanyard", "MuIg(An)", 30, 5),
    _s("A Place of Recuperation", "PeIg", 15, 5),
    _s("A Time For Slumber", "PeIg", 5, 5),
    _s("The False Dune", "MuIm", 5, 5),
    _s("Disguise of the Transformed Image", "MuIm", 15),
    _s("The Petrine Deception", "MuIm", 15, 5),
    _s("Avoiding the Blame", "MuMe", 15, 5),
    _s("Mind of the Beast", "MuMe(An)", 30, 5),
    _s("Rapid Excavations", "MuTe(Aq)", 30, 5),
    _s("Unseen Arm", "ReTe", 5),
    _s("Trackless Step", "ReTe", 10, 1),
    _s("Wizard's Reach (Animal)", "MuVi", 30, 4),
)
_ALEXANDER_RULES = _rules(
    """
Recruiting A Tiny Phalanx = R Touch, D Sun, T Group. Makes a human's weight of
scorpions, with a Rego requisite so he can order them; a swarm attacking does
+10 damage a round, Soaked as usual. He pours them between two Circles of
Beast Warding round a camp. The blocks print level 35, its own entry 30 (Base
5, +1 Touch, +2 Sun, +1 Group, +1 requisite).

Scales of the Scorpions = R Voice, D Diam, T Group. Plates friendly animals,
transformed grogs included, in chitin for +3 Soak.

Bag of Teeth = R Touch, D Moon, T Ind. Turns a pool, up to nearly a hundred
cubic feet, into an animal tooth; when the spell ends the water returns and
bursts any closed container. His emergency water on expeditions.

Movement Within the Sirocco = R Touch, D Sun, T Ind. Lets the target act in
the worst sandstorm.

Ward Against the Sirocco = R Touch, D Ring, T Circle. Repels the dust-laden
breezes, keeping out the strongest sandstorm.

Eyes of the Housecats = R Voice, D Sun, T Group. Cat's sight, for normal
action in low light; he likes to march at night.

The Guardian of the Tombs = R Per, D Sun, T Ind. Takes cobra shape: feels
movement through the ground and has a poisonous bite; poison bitten into
something hollow stays after he changes back, and grogs use it on arrows. A
serpent-skin wristband is his focus to end it at will. The blocks print "A
Guardian of the Tombs".

The Desert Wanderer = R Per, D Sun, T Ind. Arabian camel shape, with the
camel's nose for water; a camel-leather belt ends it at will.

The Lurker in the Rushes = R Touch, D Sun, T Ind. Crocodile shape, for him or
one he touches; a crocodile-skin scabbard ends it at will. The blocks print
level 30, its own entry 40 (Base 20, +1 Touch, +2 Sun, +1 size).

The Shadow on the Sand = R Per, D Sun, T Ind. Vulture shape, with keen sight;
a strand of vulture feathers ends it at will.

Retreat As Flying Vermin = R Voice, D Sun, T Circle. Turns a group and their
animal-made gear into bats; other gear is lost. Needs a circle drawn. Bat
leather in his trinket bag is the prop. The block prints MuAn(Co), its own
entry Mu(Co)An; the blocks and chapter file it among the Corpus spells.

A Punishment for Brigands = R Voice, D Sun, T Ind. Turns a human into a mouse,
which Circle of Beast Warding can then pen.

A Source of Tremendous Pride = R Voice, D Sun, T Group. Turns servants into a
pride of straight-maned lions; a tail spur in his pouch can end it. The males
are lazy, so the covenant has a small cadre of women fighters.

Bag of Feathers = R Touch, D Moon, T Group. Turns carried food into feathers
of a colour for each kind; it does not spoil, and returns only when the spell
ends.

Conflagratious Lanyard = R Touch, D Moon. Turns a large campfire into a leather
item; when the spell ends it burns again, +5 damage a round to a wearer while
it has fuel. Made to avenge a slight.

A Time For Slumber = R Touch, D Ring, T Circle. Dims the desert sun over a
camp so men and beasts can sleep.

A Place of Recuperation = R Touch, D Ring, T Circle. Cools a camp to a mild
summer's day.

The False Dune = R Touch, D Ring, T Circle. Makes the camp look and sound like
a dune or copse.

Avoiding the Blame = R Eye, D Sun, T Ind. Rewrites the target's memories of a
span of time, for the day only.

The Petrine Deception = R Voice, D Conc, T Group. Grogs look and sound like
small rocks until his concentration lapses.

Rapid Excavations = Turns a hundred cubic yards of sand to water, which soon
dissipates; digs out buried sites or drowns foes' footing. Finesse shapes it.
"""
)
_ALEXANDER_KIT = (
    "Equipment: cheap gear he can abandon if he wanders off in animal shape; "
    "his clothes are all animal products, so they change with him. "
    "Encumbrance 0. No Twilight Scars."
)
_ALEXANDER_COMBAT = (
    "Combat, in human shape: fist Init 0, Attack +1, Defense +1, Damage 0; "
    "bludgeon Init 0, Attack +3, Defense +1, Damage +2. Soak +2."
)
_ALEXANDER_COMBAT_LATER = (
    "Combat, in human shape: fist Init 0, Attack +3, Defense +3, Damage 0; "
    "bludgeon Init 0, Attack +5, Defense +3, Damage +2. Soak +2."
)
_ALEXANDER_SHAPES = _words(
    """
Animal shapes (pp. 10-12, generic beasts, with the errata's changes to their
Qualities). Asp: venomous, its bite takes effect if its Attack Advantage
exceeds armor Protection; Bat: Size -9, echo-sight; in famine he turns his
party to bats, fed on insects, to stretch supplies; Camel: smells water two
miles off, two weeks without drinking; Crocodile: Roll Attack, dragging a
bitten victim under or tearing flesh for +6; Lion: claws +15 Attack, +10
Damage. His attendants wear quilted wool armor pinned with bone, and carry
bone, horn or ivory weapons at -2 Damage (daggers and knives -1) that break on
botches. Water in skins does not transform and is lost: he has found no cure.
"""
)
_ALEXANDER_PRINTINGS = (
    Printing(
        "Gauntlet",
        21,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            0,
            _ALEXANDER_RULES,
            apparent_age=21,
            traits={"Curious": 3, "Practical": 1},
            abilities=_abilities(
                """Arabic 3 (traveling); Artes Liberales 1 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 1
                (walking long distances); Awareness 1 (ambush); Bargain 2 (for
                food and lodging); Brawl 1 (in camel form); Carouse 1 (sailors);
                Charm 1 (merchants); Chirurgy 1 (self); Etiquette 1
                (transformations into animals, and vice versa); Folk Ken 2
                (festivals); Guile 1 (about origin); Latin 4 (writing); Magic
                Theory 3 (human transformations into animals); North Africa
                Lore 2 (covenants); Order of Hermes Lore 1 (folktales of magi);
                Parma Magica 1 (Terram); Sicilian 5 (pleasantries); Survival 1
                (desert); Swim 1 (rivers)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 9, Pe 0, Re 5, An 5, Aq 0, Au 0, Co 5, He 0, "
                "Ig 0, Im 0, Me 0, Te 0, Vi 0"
            ),
            notes=paragraphs(
                "An athletic young man of Mediterranean looks, in cheap, easily "
                "replaced clothes.",
                "Sigil: a shimmering haze round his spells, like air over hot "
                "stones. He votes with a small ebony Thoth.",
                _ALEXANDER_COMBAT,
                _ALEXANDER_KIT,
                "Voice of the Bjornaer Magus: the block's total allows for "
                "casting without speech; Subtle Magic spares him gestures.",
                "Design totals: Abilities 300, Arts 135, Spells 115.",
            ),
        ),
    ),
    Printing(
        "+15",
        36,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            1,
            _ALEXANDER_RULES,
            apparent_age=35,
            traits={"Curious": 3, "Practical": 2},
            reputations={"Noted writer of travel journals (House Jerbiton)": 1},
            abilities=_abilities(
                """Arabic 5 (traveling); Artes Liberales 1 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 1
                (walking long distances); Awareness 1 (ambush); Bargain 2 (for
                food and lodging); Brawl 1 (in camel form); Carouse 1 (sailors);
                Charm 1 (merchants); Chirurgy 1 (self); Etiquette 1 (magi);
                Ethiopian 1 (traders' speech); Folk Ken 2 (festivals); Guile 1
                (about origin); Latin 4 (writing); Magic Theory 4 (human
                transformations into animals); North Africa Lore 5 (covenants);
                Order of Hermes Lore 1 (folktales of magi); Parma Magica 3
                (Terram); Sicilian 5 (pleasantries); Survival 1 (desert); Swim 1
                (rivers)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 15, Pe 5, Re 5, An 10, Aq 0, Au 0, Co 10, He 0, "
                "Ig 0, Im 0, Me 0, Te 0, Vi 0"
            ),
            notes=paragraphs(
                "An athletic young man of Mediterranean looks, in cheap, easily "
                "replaced clothes.",
                _ALEXANDER_COMBAT,
                _ALEXANDER_KIT,
                "Experience towards the next score: Mu 15.",
                "These fifteen years: he builds travelling spells and skills, "
                "and earns his first longevity ritual with two seasons on a "
                "dangerous quest for its Verditius maker, which leaves him 40 xp "
                "short of a stay-at-home magus.",
                "Design totals: Abilities 460, Arts 305, Spells 200.",
            ),
        ),
    ),
    Printing(
        "+30",
        51,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            2,
            _ALEXANDER_RULES,
            apparent_age=40,
            warping=(1, 3),
            traits={"Curious": 3, "Practical": 2},
            reputations={"Noted writer of travel journals (House Jerbiton)": 2},
            abilities=_abilities(
                """Arabic 5 (traveling); Artes Liberales 1 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 2
                (walking long distances); Awareness 2 (ambush); Bargain 3 (for
                food and lodging); Brawl 3 (in animal form); Carouse 1 (sailors);
                Charm 2 (merchants); Chirurgy 2 (self); Etiquette 2 (magi);
                Ethiopian 3 (traders' speech); Ethiopian Lore 3 (churches); Folk
                Ken 2 (festivals); Guile 1 (about origin); (Home Covenant) Lore 2
                (local mundanes); Intrigue 1 (about magi); Latin 4 (writing);
                Leadership 2 (grogs); Magic Theory 5 (human transformations into
                animals); North Africa Lore 5 (covenants); Order of Hermes Lore 1
                (folktales of magi); Parma Magica 3 (Terram); Sicilian 5
                (pleasantries); Survival 2 (desert); Swim 1 (rivers)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 15, Pe 5, Re 5, An 16, Aq 0, Au 0, Co 10, He 0, "
                "Ig 0, Im 0, Me 0, Te 0, Vi 0"
            ),
            notes=paragraphs(
                "An athletic man of Mediterranean looks, in cheap clothes made "
                "only of animal products.",
                _ALEXANDER_COMBAT_LATER,
                _ALEXANDER_KIT,
                "Experience towards the next score: Mu 15, An 9.",
                "These fifteen years: he joins a well-resourced covenant, works "
                "on spells and skills for leading grogs, and goes on preparing "
                "for an expedition to Ethiopia.",
                _ALEXANDER_SHAPES,
                "Design totals: Abilities 655, Arts 395, Spells 395; 20 xp more "
                "than an average magus in this period.",
            ),
        ),
    ),
    Printing(
        "+45",
        66,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            3,
            _ALEXANDER_RULES,
            apparent_age=47,
            warping=(2, 1),
            traits={"Curious": 3, "Practical": 2},
            reputations={
                "Noted writer about North African customs (House Jerbiton)": 3
            },
            abilities=_abilities(
                """Arabic 5 (traveling); Artes Liberales 2 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 2
                (walking long distances); Awareness 2 (ambush); Bargain 4 (for
                food and lodging); Brawl 3 (in animal form); Carouse 1 (sailors);
                Charm 2 (merchants); Chirurgy 2 (self); Etiquette 2 (magi);
                Ethiopian 3 (traders' speech); Ethiopian Lore 3 (churches); Folk
                Ken 2 (festivals); Guile 1 (about origin); (Home Covenant) Lore 3
                (local mundanes); Intrigue 1 (about magi); Latin 5 (writing);
                Leadership 2 (grogs); Magic Theory 5 (human transformations into
                animals); North Africa Lore 5 (covenants); Order of Hermes Lore 1
                (folktales of magi); Parma Magica 4 (Terram); Sicilian 5
                (pleasantries); Survival 2 (desert); Swim 1 (rivers); Teaching 3
                (apprentices)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 18, Pe 5, Re 10, An 16, Aq 5, Au 6, Co 14, He 5, "
                "Ig 5, Im 5, Me 5, Te 5, Vi 5"
            ),
            notes=paragraphs(
                "An athletic man of Mediterranean looks, in cheap clothes made "
                "only of animal products.",
                _ALEXANDER_COMBAT_LATER,
                _ALEXANDER_KIT,
                "Experience towards the next score: An 9, Au 3.",
                "These fifteen years: a would-be familiar dies before the ritual "
                "ends; he broadens his Arts to take an apprentice, and has "
                "trained a child for eight years by this block. A year of "
                "errands pays for a stronger longevity ritual, and he makes "
                "short trips to Kushite ruins.",
                _ALEXANDER_SHAPES,
                "Design totals: Abilities 790, Arts 638, Spells 445.",
            ),
        ),
    ),
    Printing(
        "+60",
        81,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            4,
            _ALEXANDER_RULES,
            apparent_age=55,
            warping=(2, 5),
            traits={"Curious": 3, "Practical": 2},
            reputations={
                "Noted writer about North African customs (House Jerbiton)": 4
            },
            abilities=_abilities(
                """Arabic 5 (traveling); Artes Liberales 3 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 2
                (walking long distances); Awareness 2 (ambush); Bargain 4 (for
                food and lodging); Brawl 3 (in animal form); Carouse 1 (sailors);
                Charm 2 (merchants); Chirurgy 2 (self); Etiquette 2 (magi);
                Ethiopian 4 (traders' speech); Ethiopian Lore 5 (churches); Folk
                Ken 3 (festivals); Guile 1 (about origin); (Home Covenant) Lore 3
                (local mundanes); Intrigue 1 (about magi); Latin 5 (writing);
                Leadership 3 (grogs); Magic Theory 5 (human transformations into
                animals); North Africa Lore 5 (covenants); Order of Hermes Lore 1
                (folktales of magi); Parma Magica 4 (Terram); Sicilian 5
                (pleasantries); Survival 3 (desert); Swim 1 (rivers); Teaching 4
                (apprentices)"""
            ),
            arts=arts_from(
                "Cr 5, In 9, Mu 19, Pe 5, Re 10, An 17, Aq 5, Au 10, Co 15, He 5, "
                "Ig 5, Im 5, Me 5, Te 5, Vi 5"
            ),
            notes=paragraphs(
                "An older man, lean and Mediterranean, in cheap clothes made "
                "only of animal products.",
                _ALEXANDER_COMBAT_LATER,
                _ALEXANDER_KIT,
                "These fifteen years: his apprentice finishes, and he keeps to "
                "spells for expeditions. His travels badly cut his study.",
                _ALEXANDER_SHAPES,
                "Clouds of Obscuring Sand (CrAu 30, R Sight, D Sun, T Group; a "
                "sandstorm a thousand paces across) is among his new spells but "
                "in no block's list.",
                "Design totals: Abilities 935, Arts 753, Spells 570.",
            ),
        ),
    ),
    Printing(
        "+75",
        96,
        _stat(
            _ALEXANDER,
            _ALEXANDER_SPELLS,
            5,
            _ALEXANDER_RULES,
            apparent_age=62,
            warping=(2, 5),
            traits={"Curious": 3, "Practical": 2},
            reputations={
                "Noted writer about North African and Kushite ruins (House Jerbiton)": 4
            },
            abilities=_abilities(
                """Arabic 5 (traveling); Artes Liberales 4 (geography);
                (Apprenticeship Covenant) Lore 1 (workshops); Athletics 3
                (walking long distances); Awareness 2 (ambush); Bargain 4 (for
                food and lodging); Brawl 3 (in animal form); Carouse 1 (sailors);
                Charm 2 (merchants); Chirurgy 2 (self); Concentration 3
                (maintaining Muto spells); Etiquette 2 (magi); Ethiopian 4
                (traders' speech); Ethiopian Lore 5 (churches); Finesse 3 (Muto);
                Folk Ken 3 (festivals); Guile 1 (about origin); (Home Covenant)
                Lore 3 (local mundanes); Intrigue 1 (about magi); Latin 5
                (writing); Leadership 3 (grogs); Magic Theory 5 (human
                transformations into animals); North Africa Lore 5 (covenants);
                Order of Hermes Lore 1 (folktales of magi); Parma Magica 6
                (Terram); Sicilian 5 (pleasantries); Survival 5 (desert); Swim 1
                (rivers); Teaching 4 (apprentices)"""
            ),
            arts=arts_from(
                "Cr 5, In 9, Mu 20, Pe 5, Re 10, An 17, Aq 5, Au 10, Co 15, He 5, "
                "Ig 5, Im 5, Me 5, Te 5, Vi 5"
            ),
            notes=paragraphs(
                "An elderly, weathered man, in cheap clothes made only of animal "
                "products.",
                _ALEXANDER_COMBAT_LATER,
                _ALEXANDER_KIT,
                "These fifteen years: he nearly gives up improving his Arts, "
                "working instead on skills and spells for exploring.",
                _ALEXANDER_SHAPES,
                "Clouds of Obscuring Sand (CrAu 30, R Sight, D Sun, T Group; a "
                "sandstorm a thousand paces across) is among his new spells but "
                "in no block's list.",
                "Design totals: Abilities 1145, Arts 773, Spells 775.",
            ),
        ),
    ),
)

# Aurulentus of Jerbiton (pp. 15-24)

_AURULENTUS: StatBlock = {
    "characteristics": characteristics(2, 0, 3, 2, 0, 1, 0, -2),
    "confidence": (1, 3),
    "traits": {
        "Further family cause": 3,
        "Loyal (wife)": 3,
        "Protective of his offspring": 3,
    },
    "reputations": {"Member of auspicious family (Hermetic)": 2},
}
_AURULENTUS_VIRTUES: list[str | tuple[str, dict[str, str]]] = [
    "The Gift",
    "Hermetic Magus",
    ("Mythic Blood", {"detail": "Nymph of Artemis"}),
    vf_art("Affinity with {art}", "Corpus"),
    vf_art("Affinity with {art}", "Creo"),
    "Improved Characteristics",
    vf_focus("Minor Magical Focus", "fertility"),
    "Privileged Upbringing",
    "Skilled Parens",
    ("Special Circumstances", {"circumstance": "targeting family members"}),
    ("Student of {realm}", {"realm": "Magic"}),
    "Venus' Blessing",
    ("Driven (Major)", {"detail": "fulfill the family prophecy"}),
    ("True Love (Major)", {"detail": "Semira, his wife"}),
    ("Weak Magic Resistance", {"detail": "female casters"}),
    ("Obsessed (Minor)", {"detail": "protect offspring, especially daughters"}),
    "Mentor",
]
_AURULENTUS_UNAGED = [*_AURULENTUS_VIRTUES]
_AURULENTUS_UNAGED.insert(11, ("Unaging", {"detail": "granted by Zeno"}))
_AURULENTUS_SPELLS = (
    _s("Bind Wound", "CrCo", 10),
    _s("The Chirurgeon's Healing Touch", "CrCo", 20),
    _s("Gentle Touch of the Purified Body", "CrCo", 20),
    _s("Purification of the Festering Wounds", "CrCo", 20),
    _s("Widening the River Styx", "CrCo", 20, 1),
    _s("The Severed Limb Made Whole", "CrCo", 25, 3),
    _s("Blissful Sensations", "CrCo", 30, 3),
    _s("Cheating the Reaper", "CrCo", 30),
    _s("Artemis' Fertility", "CrCo", 40, 2),
    _s("Incantation of the Body Made Whole", "CrCo", 40, 3),
    _s("Bestow the Blessing of Apollon", "CrCo", 50, 4),
    _s("Incantation of the Warriors Made Whole", "CrCo", 50, 4),
    _s("Blessing of Artemis' Fertility", "CrCo", 65, 4),
    _s("Revealed Flaws of Mortal Flesh", "InCo", 10),
    _s("Pose Clotho's Question", "InCo", 5, 1),
    _s("Parental Inquisitiveness", "InCo", 10, 4),
    _s("Pose Nona's Question", "InCo", 10, 1),
    _s("The Maculate Noblewoman", "InCo", 15, 1),
    _s("Verifying the Presence of Artemis' Blessing", "InCo", 15, 1),
    _s("Eyes of the Sage", "InCo(Im)", 30, 2),
    _s("Ease the Suffering of Childbirth", "MuCo", 15, 3),
    _s("Bane of the Decrepit Body", "PeCo", 25, 2),
    _s("Rise of the Feathery Body", "ReCo", 10),
    _s("Hold Chur", "ReCo", 30, 3),
    _s("It's Raining Men", "ReCo", 30, 4),
    _s("Warding the Unruly Child", "ReCo", 30, 4),
    _s("Seven-League Stride", "ReCo", 30, 3),
    _s("Seven Leagues Travel", "ReCo", 35, 3),
    _s("The Bountiful Feast", "CrHe", 35, 3),
    _s("Lamp without Flame", "CrIg", 10),
    _s("Phantasmal Troupe", "CrIm", 15),
    _s("Prying Eyes", "InIm", 5, 3),
    _s("Summoning the Distant Image", "InIm", 25, 3),
    _s("Aura of the Ennobled Presence", "MuIm", 10, 3),
    _s("Comeliness of the Crone", "MuIm", 10, 3),
    _s("Disguise of the Transformed Image", "MuIm", 15, 3),
    _s("Ears of a Grateful Father", "PeIm", 20, 4),
    _s("Words of the Unbroken Silence", "CrMe", 10, 3),
    _s("Memory of the Distant Dream", "CrMe", 20, 3),
    _s("Sight of the Transparent Motive", "InMe", 10, 3),
    _s("Posing the Silent Question", "InMe", 20, 3),
    _s("Unseen Arm", "ReTe", 5),
)
_AURULENTUS_RULES = _rules(
    """
Widening the River Styx = Ritual, R Touch, D Mom, T Ind. Settles a minor aging
crisis; the target must still rest out the season.

Blissful Sensations = R Touch, D Sun, T Ind. Takes away pain up to that of a
light wound until sunset, when any remaining cause returns it. Used often it
can addict. His version gives Semira no Warping. Too weak for childbirth.

Artemis' Fertility = R Touch, D Moon, T Ind. Raises the target's fertility; it
cannot promise conception, and other magi doubt it works.

Bestow the Blessing of Apollon = Ritual, R Touch, D Year, T Room. +18 to
Recovery rolls for those under it for the whole interval. A proof of concept,
replaced by the Bed of Rapid Convalescence.

Incantation of the Warriors Made Whole = Ritual, R Touch, D Mom, T Room. Heals
all wounds, not lost limbs, disease or poison, on everyone in the room
throughout. Commissioned by a Tremere; a tent can serve after a battle.

Blessing of Artemis' Fertility = Ritual, R Touch, D Year, T Boundary. Raises
fertility across the boundary, even of those arriving later. Doubted by every
other magus; he gives its Lab Text to anyone who asks.

Pose Clotho's Question = R Touch, D Mom, T Ind. Says if a woman is pregnant;
fails on men.

Parental Inquisitiveness = R Touch, D Mom, T Part. Gives the sex of an unborn
child; fails in the first trimester.

Pose Nona's Question = R Touch, D Mom, T Ind. Pregnancy and the months left;
if none, the exact date in her cycle. Fails on men.

The Maculate Noblewoman = R Touch, D Mom, T Ind. Finds the true cause of a
target's infertility.

Verifying the Presence of Artemis' Blessing = R Touch, D Sun, T Ind. Tells the
caster at once of a conception in the target.

Ease the Suffering of Childbirth = R Touch, D Sun, T Part. Widens the pelvis,
+1 to childbirth rolls (Art & Academe p. 62).

Hold Chur = R Voice, D Sun, T Ind. Holds the target motionless with his eyes
shut. Named for a troublesome grog.

It's Raining Men = R Voice, D Mom, T Group. Throws up to ten people five paces
up to fall (errata: it breaks up a formation only of ten men or fewer).
Commissioned by a Tytalus cavalry commander.

Warding the Unruly Child = The chapter gives a ReCo 30 of this level as House
Arrest of the Unruly Child, and the activities as Housearrest of the Unruly
Child; the block's name is kept. R Touch, D Ring, T Circle: no human may pass
the circle if it penetrates; it keeps children out of, or inside, a room.

Seven Leagues Travel = R Touch, D Mom, T Ind. As Seven-League Stride for a
touched target, with the Int + Finesse 9+ roll against a slightly wrong
arrival; built so it does not Warp Semira.

Comeliness of the Crone = R Touch, D Sun, T Ind. -3 to all rolls to influence,
seduce or please. He tried it on his daughters to test suitors until Semira
forbade it.

Ears of a Grateful Father = R Touch, D Conc, T Group. Brings a group's voices
down to normal conversation. Invented after minding ten screaming infants.

Phantasmal Troupe = R Voice, D Conc, T Ind. Illusory music from a chosen
direction, a full troupe if wished; Finesse sets the quality. Invented by his
parens Altus.
"""
)
_AURULENTUS_LOOK = _words(
    """A tall, handsome man, brown-haired, with a golden glint in his hazel eyes
    and fine features, always clean shaven, in close-fitting clothes that show
    off his athletic build."""
)
_AURULENTUS_POWER = _words(
    """Oh Brother, Where Art Thou? (0 points, Init -2, Corpus): he senses the
    direction, rough distance and health of anyone descended by blood from his
    great-great-grandfather Alexander. No penetration, words or gestures (InCo
    Base 3, +3 Bloodline, +1 health)."""
)
_AURULENTUS_COMBAT = (
    "Combat: fist Init -2, Attack 0, Defense -2, Damage 0. Soak +1. "
    "Equipment: tasteful clothes and a wedding ring. Encumbrance 0."
)
_ZENO = _words(
    """Familiar, bound at 34: Zeno the Tortoise, about 20 cm long, a drab brown
    shell with 15 lumps along it. Magic Might 15; Int 0, Per -2, Pre -5, Com -6,
    Str -1, Sta +5, Dex +2, Qik -5; Size -4; Soak +12. Virtues Enduring
    Constitution, Long-Winded, Tough, Unaging; Flaws Noncombatant, Poor
    Eyesight, Reclusive. Abilities Awareness 2, Brawl 2, High German 5, Latin 5,
    Greek 4, Survival 5. Powers: Retreat of Invulnerability (1 point, Init -5):
    in his shell he is immune to all non-magical harm; Grant Virtue (Unaging) (5
    points, Init -5): one person, for as long as he likes (Guardians of the
    Forests p. 32). Vis: 2 pawns of Creo in his shell. Bond: Bronze +3, Silver
    +1, Gold +1 (CrCo Lab Total 40)."""
)
_ZENO_MIND = (
    "Zeno's bond also carries Mental Communication: he and Aurulentus are in "
    "constant touch by words, images and feeling (CrMe 15)."
)
_AURULENTUS_FIRST_ITEMS = _words(
    """Items of this period. The Face of Paris (PeCo 14, unlimited): a blunt
    razor that takes off body hair; a magus must lower his Resistance to shave.
    Communication of the Lovers (InIm 21, R Arc, 2/day): matching silver amulets,
    each an Arcane Connection to the other, showing and sounding whoever holds
    the twin; no Penetration, so he lowers his Parma, and few magi would risk
    them. Reunion of Lovers (ReCo 40, 24/day): calfskin boots with little wings,
    Seven-League Stride built not to Warp Semira."""
)
_AURULENTUS_LATE_ITEMS = _words(
    """Items of this period. Army of the Infant (invested): painted wooden
    soldiers, with a matching animal set for his daughters, that move (ReHe 20)
    and make their noises (CrIm 20) unlimited a day. Bachelor's Door (invested):
    an antechamber door that reads lust in anyone entering (InMe 24, constant)
    and bars him if it penetrates (ReCo 33, 1/day). Bed of Rapid Convalescence
    (CrCo 34, constant): a leather sick-bed giving +18 to recovery rolls for a
    full interval in it. Comb of Aphrodite (PeAq 15): dries hair at once, a
    birthday gift. Crib with a Mother's Touch (invested): hears a crying baby
    (InIm 8) and rocks it (ReHe 17, 24/day). Guardian of Decency (invested): a
    silver necklace with three beryls that notices a man's touch (InCo 19),
    strips him of lust for any woman (PeMe 30, 3/day, R Voice), helped by a
    humming (CrIm 11). Nappy without Nuisance (PeCo 15): destroys what it
    catches. Soothe the Mother's Anxiety (invested): a handle in the nursery
    hears anything above a whisper (InIm 14) and a mirror apart from it shows
    the room (CrIm 28). Traveller's Comfort (ReAu(Ig) 24, constant): a plain
    cloak that keeps off rain and keeps in warmth."""
)
_AURULENTUS_PRINTINGS = (
    Printing(
        "Gauntlet",
        20,
        _stat(
            _AURULENTUS,
            _AURULENTUS_SPELLS,
            0,
            _AURULENTUS_RULES,
            apparent_age=20,
            virtues_flaws=_AURULENTUS_VIRTUES,
            abilities=_abilities(
                """Artes Liberales 1 (astronomy); (Area) Lore 2 (covenant
                surroundings); Athletics 1 (running); Awareness 1 (searching);
                Carouse 1 (staying sober); Charm 2 (his wife); Code of Hermes 1
                (apprentices); Concentration 2 (spell concentration); Etiquette 1
                (nobility); Finesse 2 (precision); Folk Ken 1 (covenfolk); Guile 1
                (lying to wife); High German 5 (Allemannisch); Intrigue 1
                (gossip); Order of Hermes Lore 1 (personalities); Latin 5
                (Hermetic usage); Magic Lore 2+2 (Artemis); Magic Theory 4
                (Corpus); Parma Magica 1 (Corpus); Penetration 1 (Corpus);
                Philosophiae 1 (moral philosophy); Profession: Scribe 1
                (copying)"""
            ),
            arts=arts_from(
                "Cr 11, In 1, Mu 0, Pe 0, Re 1, An 0, Aq 0, Au 0, Co 11, He 0, "
                "Ig 0, Im 0, Me 5, Te 0, Vi 5"
            ),
            notes=paragraphs(
                _AURULENTUS_LOOK,
                "Casting sigil: Cloak, a shimmer that wraps caster or target, a "
                "guarding cloak or an aggressive armor according to the spell. "
                "Voting sigil: a golden walnut with a tiny sprout.",
                _AURULENTUS_POWER,
                _AURULENTUS_COMBAT,
                "Experience towards the next score: Order of Hermes Lore 5. No "
                "Twilight Scars.",
                "The book assumes a Lab Text for every ArM5 spell he knows; the "
                "rest he invented, but for Phantasmal Troupe.",
            ),
        ),
    ),
    Printing(
        "+15",
        35,
        _stat(
            _AURULENTUS,
            _AURULENTUS_SPELLS,
            1,
            _AURULENTUS_RULES,
            apparent_age=34,
            warping=(3, 5),
            virtues_flaws=_AURULENTUS_UNAGED,
            abilities=_abilities(
                """Artes Liberales 2 (astronomy); (Area) Lore 2 (covenant
                surroundings); Athletics 1 (running); Awareness 1 (searching);
                Carouse 1 (staying sober); Charm 2 (his wife); Code of Hermes 1
                (apprentices); Concentration 2 (spell concentration); Etiquette 1
                (nobility); Finesse 2 (precision); Folk Ken 1 (covenfolk); Guile 1
                (lying to wife); High German 5 (Allemannisch); Intrigue 1
                (gossip); Order of Hermes Lore 2 (personalities); Latin 5
                (Hermetic usage); Magic Lore 2+2 (Artemis); Magic Theory 5
                (Corpus); Parma Magica 1 (Corpus); Penetration 1 (Corpus);
                Philosophiae 1 (moral philosophy); Profession: Scribe 1
                (copying)"""
            ),
            arts=arts_from(
                "Cr 15, In 10, Mu 10, Pe 10, Re 10, An 0, Aq 0, Au 1, Co 15, He 0, "
                "Ig 1, Im 10, Me 5, Te 1, Vi 5"
            ),
            notes=paragraphs(
                _AURULENTUS_LOOK,
                _AURULENTUS_POWER,
                _AURULENTUS_COMBAT,
                "Twilight Scars: his touch cures small children's toothache, and "
                "his beard grows exceptionally strongly.",
                "Experience towards the next score: Me 2.",
                "These fifteen years: thirteen learning and two in the lab. He "
                "binds Zeno at 34, who grants him Unaging. He invents Clotho's "
                "and Nona's Questions in one season, Verifying the Presence, The "
                "Maculate Noblewoman and Widening the River Styx, reinvented "
                "twice in a season, using all of them in his research, and spends "
                "two seasons stabilizing it. Cheating the Reaper dropped out of "
                "this block's print; the errata restores it.",
                _ZENO,
            ),
        ),
    ),
    Printing(
        "+30",
        50,
        _stat(
            _AURULENTUS,
            _AURULENTUS_SPELLS,
            2,
            _AURULENTUS_RULES,
            apparent_age=34,
            decrepitude=(1, 0),
            warping=(4, 19),
            virtues_flaws=_AURULENTUS_UNAGED,
            abilities=_abilities(
                """Artes Liberales 2 (astronomy); (Area) Lore 2 (covenant
                surroundings); Athletics 1 (running); Awareness 2 (searching);
                Carouse 1 (staying sober); Charm 3 (his wife); Code of Hermes 1
                (apprentices); Concentration 2 (spell concentration); Etiquette 1
                (nobility); Finesse 2 (precision); Folk Ken 1 (covenfolk); Greek 4
                (archaic vocabulary); Guile 1 (lying to wife); High German 5
                (Allemannisch); Intrigue 1 (gossip); Order of Hermes Lore 2
                (personalities); Latin 5 (Hermetic usage); Leadership 1 (family
                members); Magic Lore 3+2 (Artemis); Magic Theory 6 (Corpus); Parma
                Magica 2 (Corpus); Penetration 1 (Corpus); Philosophiae 2 (moral
                philosophy); Profession: Scribe 1 (copying); Survival 1 (forests);
                Teaching 1 (one-on-one)"""
            ),
            arts=arts_from(
                "Cr 16, In 10, Mu 10, Pe 10, Re 11, An 5, Aq 5, Au 5, Co 16, He 5, "
                "Ig 5, Im 10, Me 6, Te 5, Vi 7"
            ),
            notes=paragraphs(
                _AURULENTUS_LOOK,
                _AURULENTUS_POWER,
                _AURULENTUS_COMBAT,
                "Twilight Scars: his touch cures small children's toothache, his "
                "beard grows exceptionally strongly, and dogs take him for a cat.",
                "Experience towards the next score: Cr 1, Co 1, Me 2, Vi 6.",
                "These fifteen years: five years in the lab, pressed by Semira's "
                "coming age. Artemis' Fertility takes two seasons and two more "
                "to reinvent twice; he learns and twice reinvents Bane of the "
                "Decrepit Body, reinvents The Maculate Noblewoman three times, "
                "spends four seasons on eight Longevity Rituals and four "
                "stabilizing: the breakthrough holds, and he makes rituals for "
                "himself and Semira that leave them fertile. Then he empowers "
                "Zeno's bond and invents Eyes of the Sage. The last ten years "
                "are learning.",
                _ZENO,
                _ZENO_MIND,
                "The breakthrough is a Minor Hermetic Breakthrough under Houses "
                "of Hermes: True Lineages p. 26; six seasons stabilizing in all.",
            ),
        ),
    ),
    Printing(
        "+45",
        65,
        _stat(
            _AURULENTUS,
            _AURULENTUS_SPELLS,
            3,
            _AURULENTUS_RULES,
            apparent_age=34,
            decrepitude=(1, 0),
            warping=(5, 24),
            virtues_flaws=_AURULENTUS_UNAGED,
            abilities=_abilities(
                """Artes Liberales 2 (astronomy); (Area) Lore 2 (covenant
                surroundings); Athletics 1 (running); Awareness 2 (searching);
                Carouse 1 (staying sober); Charm 3 (his wife); Code of Hermes 1
                (apprentices); Concentration 2 (spell concentration); Etiquette 1
                (nobility); Finesse 3 (precision); Folk Ken 2 (covenfolk); Greek 4
                (archaic vocabulary); Guile 1 (lying to wife); High German 5
                (Allemannisch); Intrigue 2 (gossip); Order of Hermes Lore 2
                (personalities); Latin 5 (Hermetic usage); Leadership 1 (family
                members); Magic Lore 3+2 (Artemis); Magic Theory 7 (Corpus); Parma
                Magica 2 (Corpus); Penetration 2 (Corpus); Philosophiae 2 (moral
                philosophy); Profession: Scribe 1 (copying); Survival 1 (forests);
                Teaching 1 (one-on-one)"""
            ),
            arts=arts_from(
                "Cr 20, In 10, Mu 11, Pe 10, Re 12, An 10, Aq 5, Au 5, Co 20, He 7, "
                "Ig 5, Im 11, Me 10, Te 5, Vi 8"
            ),
            notes=paragraphs(
                _AURULENTUS_LOOK,
                _AURULENTUS_POWER,
                _AURULENTUS_COMBAT,
                "Twilight Scars: his touch cures small children's toothache, his "
                "beard grows exceptionally strongly, dogs take him for a cat, and "
                "he never has a hangover.",
                "Experience towards the next score: Cr 1, Co 1, Me 2, Vi 2.",
                "These fifteen years: his goal reached, he returns to ordinary "
                "Hermetic work: ten years learning, five in the lab, catching up "
                "standard spells from Lab Texts, making three items, and a "
                "season writing up his findings. A few nearby magi take interest.",
                _ZENO,
                _ZENO_MIND,
                _AURULENTUS_FIRST_ITEMS,
            ),
        ),
    ),
    Printing(
        "+60",
        80,
        _stat(
            _AURULENTUS,
            _AURULENTUS_SPELLS,
            4,
            _AURULENTUS_RULES,
            apparent_age=34,
            decrepitude=(1, 2),
            warping=(6, 24),
            virtues_flaws=_AURULENTUS_UNAGED,
            abilities=_abilities(
                """Artes Liberales 2 (astronomy); (Area) Lore 2 (covenant
                surroundings); Athletics 1 (running); Awareness 2 (searching);
                Carouse 1 (staying sober); Charm 3 (his wife); Code of Hermes 2
                (apprentices); Concentration 3 (spell concentration); Etiquette 3
                (nobility); Finesse 2 (precision); Folk Ken 2 (covenfolk); Greek 4
                (archaic vocabulary); Guile 2 (lying to wife); High German 5
                (Allemannisch); Intrigue 2 (gossip); Order of Hermes Lore 3
                (personalities); Latin 5 (Hermetic usage); Leadership 2 (family
                members); Magic Lore 4+2 (Artemis); Magic Theory 8 (Corpus); Parma
                Magica 2 (Corpus); Penetration 2 (Corpus); Philosophiae 2 (moral
                philosophy); Profession: Scribe 1 (copying); Survival 1 (forests);
                Teaching 2 (one-on-one)"""
            ),
            arts=arts_from(
                "Cr 21, In 12, Mu 11, Pe 10, Re 13, An 10, Aq 5, Au 5, Co 21, He 7, "
                "Ig 5, Im 11, Me 11, Te 5, Vi 10"
            ),
            notes=paragraphs(
                _AURULENTUS_LOOK,
                _AURULENTUS_POWER,
                _AURULENTUS_COMBAT,
                "Twilight Scars: his touch cures small children's toothache, his "
                "beard grows exceptionally strongly, dogs take him for a cat, he "
                "never has a hangover, and in anger he speaks in his wife's voice.",
                "Experience towards the next score: Intrigue 10, Magic Lore 5, Me 2.",
                "These fifteen years: eight learning, seven in the lab, mostly "
                "making things for Semira, with two extra seasons of spell work "
                "in all. He invents seven spells and nine items.",
                _ZENO,
                _ZENO_MIND,
                _AURULENTUS_FIRST_ITEMS,
                _AURULENTUS_LATE_ITEMS,
            ),
        ),
    ),
)

# Conscientia of Bonisagus (pp. 25-32)

_CONSCIENTIA: StatBlock = {
    "characteristics": characteristics(4, 2, 1, 1, -1, -2, 0, 0),
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Adept Laboratory Student",
        vf_art("Affinity with {art}", "Creo"),
        vf_ability("Affinity with {ability}", "Magic Theory"),
        vf_art("Affinity with {art}", "Muto"),
        "Book Learner",
        vf_great("Intelligence"),
        "Inventive Genius",
        "Study Bonus",
        "Skilled Parens",
        "Privileged Upbringing",
        vf_puissant("Magic Theory"),
        "Waster of Vis",
        "Weak Spontaneous Magic",
        "Careless Sorcerer",
        "Difficult Spontaneous Magic",
        "Exciting Experimentation",
        "Poor Formulaic Magic",
    ],
}
_CONSCIENTIA_SPELLS = (
    _s("Doublet of Silk, That's Impenetrable", "MuAn", 15, 1),
    _s("Pests of a Colossal Size", "MuAn", 35, 1),
    _s("Epona's Bane", "ReAn", 25),
    _s("Summon the Eldritch Bond", "ReAn", 35, 2),
    _s("Conjure From the Mist", "MuAu(Te)", 40, 3),
    _s("Be Rid the Tell Tale Smoke", "PeAu", 20),
    _s("Touch of the Blessed Virgin", "CrCo", 20, 2),
    _s("Statim Sessio", "CrHe", 10),
    _s("Fell the Mighty Trunk", "MuHe", 15, 1),
    _s("Evening's Comfort", "CrIg", 5),
    _s("Palm of Odorous Flame", "CrIg", 5),
    _s("Veneficus Enigma", "CrIm", 20),
    _s("Spy the Approaching Grog", "InIm", 5),
    _s("Circle of Undisturbed Rest", "PeIm(Re)", 25),
    _s("Robed in Angelic Beauty", "CrMe(Im)", 25, 2),
    _s("Thoughts Within Speech", "InMe", 30, 3),
    _s("Apollo's Fearful Gaze", "MuMe", 30, 2),
    _s("Slave of Charity", "ReMe", 35, 3),
    _s("Conjure the Ocean's Breath", "MuTe", 15),
    _s("Armatura Vitrea", "MuTe", 20),
    _s("Saving the Apprentice's Time", "PeTe", 10),
    _s("Foras Vim", "ReTe", 15),
    _s("Carve Domain", "PeTe", 20, 2),
)
_CONSCIENTIA_RULES = _rules(
    """
Doublet of Silk, That's Impenetrable = As Doublet of Impenetrable Silk, but the
clothing also really turns to silk.

Pests of a Colossal Size = R Voice, D Sun, T Group. Swells the lice and fleas
on the targets to huge, often hostile, size. The blocks print level 35, its
own entry 30 (Base 4, +2 Sun, +2 Group, +2 Voice).

Epona's Bane = R Voice, D Mom, T Group. Panics a small unit of horses; riders
roll Str + Ride 12+ or are thrown.

Summon the Eldritch Bond = R Voice, D Sun, T Ind. Sends a biting insect to bite
a target and come back, its blood an Arcane Connection. With Pests of a
Colossal Size it reaches further and loses all subtlety.

Conjure From the Mist = R Voice, D Sun, T Part. Makes air into stone of a chosen
shape; complex shapes need Finesse.

Be Rid the Tell Tale Smoke = R Touch, D Ring, T Circle. Destroys all smoke in
the circle. Learned from her parens.

Touch of the Blessed Virgin = Ritual, R Touch, D Mom, T Ind. Restores a woman's
maidenhood.

Statim Sessio = R Touch, D Sun, T Ind. Creates a comfortable wooden chair.

Evening's Comfort = R Touch, D Sun, T Per. Keeps her bed warm until sunrise.

Palm of Odorous Flame = As Palm of Flame, with a random smell at each casting,
most often elderberry.

Veneficus Enigma = R Touch, D Conc, T Ind. An illusory puzzlebox: Int + Artes
Liberales against her Int + Artes Liberales + 5 opens it, often to a prize.

Spy the Approaching Grog = R Touch, D Conc, T Room. Peers into the room beyond
a wall; made to be cast forcelessly so it cannot scry on a magus.

Circle of Undisturbed Rest = R Touch, D Ring, T Circle. Keeps sights and sounds
from leaving a camp, which shows as a silent black patch. Errata: PeIm(Re) 25
(Base 4, +1 Touch, +2 Ring, +1 Rego, +1 changing image), not the book's ReIm 5.

Robed in Angelic Beauty = R Voice, D Conc, T Group. Lends the speaker perfect
beauty and a holy aura. A Gifted speaker is taken for a devil in disguise. The
+30 block prints CrMe 25, the +45 CrMe 30, its own entry CrMe(Im) 25.

Thoughts Within Speech = R Eye, D Mom, T Ind. As Peering Into the Mortal Mind,
but the target unknowingly speaks the thoughts aloud.

Apollo's Fearful Gaze = R Voice, D Sun, T Ind. Light gives pain: moon or candle
-1, torch -3, bonfire -5, daylight Incapacitated. The +30 block and its entry
print level 30, the +45 block 20.

Slave of Charity = R Eye, D Sun, T Ind. As Enslave the Mortal Mind, but any new
order heard takes over until done.

Conjure the Ocean's Breath = R Touch, D Moon, T Part. Turns a patch of dirt to
salt until the Moon ends; quick trade goods.

Armatura Vitrea = R Voice, D Diam, T Ind. Turns armor to glass: Protection 2,
Load 3; a weapon's blow shatters it for an extra simple die of damage.

Foras Vim = R Voice, D Mom, T Group. A choking cloud of grit: casting in it
needs Sta + Concentration 12+. She has long meant to master it for fast casting.

Carve Domain = R Touch, D Mom, T Part. Destroys a channel of up to 10,000 cubic
feet of earth.

Saving the Apprentice's Time = R Touch, D Mom, T Room. An hour's dusting done in
a moment.
"""
)
_CONSCIENTIA_COMBAT = _words(
    """Combat: dodge Init 0, Defense 0; fist Init 0, Attack 0, Defense 0, Damage
    -1; kick Init -1, Attack 0, Defense -1, Damage +2. Soak -2."""
)
_AUREUS = _words(
    """Familiar: Aureus, an exotic red bird with a golden ruff, the gift of a
    grateful patron. Magic Might 20 (Ignem); Int +2, Per +1, Pre +1, Com 0, Str
    -6, Sta 0, Dex +1, Qik +5; Size -3; Soak 0. Cords Gold +2, Silver +0, Bronze
    +2. Abilities Artes Liberales 1, Athletics 6, Bargain 3, Folk Ken 3, French
    5, Latin 4, Magic Theory 3. Loyal +3, Patient +2, Inquisitive +1, Terrified
    of Blue Potions +1. Reincarnation (15 points): dying with 15 or more Might
    he burns and rises within an hour with 1 Might. Bond: Speech, Shared Senses."""
)
_CONSCIENTIA_ITEMS = _words(
    """Items she has made (the book does not date them). Apollo's Lyre: a brass
    lyre with a song on each string (CrIm 10, 3/day), a popular Lab Text.
    Cooking Stone (CrIg 15): boils the water it is dropped in. Cultellus (PeVi
    37, Pen +32, 50/day): a kitchen knife that dispels a Parma of 6 or lower;
    she claims she never finished it and burned her notes. Dico Calculus: a
    stone for a blind Criamon that sees a page (InIm 18) and puts it in the
    user's mind (CrMe 26). Ferramenta Glacies (ReAq 14): a pick that freezes
    water. Hermes' Horn (ReAn 40, 1/day): calms up to 1,000 beasts for the day.
    Mjolnir's Equal (PeTe(He) 25): a hammer that destroys metal or wood it
    touches. Shulpea's Bowl (CrHe 28): refills with clean, dull food every two
    minutes. Traveler's Cloak (MuTe(Ig) 25, 1/day): softens and warms the ground
    till sunrise. Vessel of Etain's Children: a necklace whose fittings turn
    blood to polished stone (MuAq(Te) 23), keeping Arcane Connections. Vulcan's
    Favored (CrTe 29): a seal keeping a tool as new, by her new guideline CrTe
    15, repair a crafted item."""
)
_CONSCIENTIA_CHARGED = _words(
    """Charged items and potions she favors: Pneum Flask (ReAu 5), steals a
    breath as an Arcane Connection; Elixir of Morning's Afterthought (CrCo 20),
    cures a hangover; Magic Spice (MuIm 5), makes any food taste a feast; Ink of
    the Unseen Circle (PeIm 15), hides a ring; Potion of Vulcan's Appeasement
    (PeIg 20), quenches a house fire; Message in a Bottle (CrMe 5), a message
    in the drinker's mind; The Wakeful Nightmare (ReMe 20), bars sleep for a
    Moon, with mounting Fatigue and wounds; Whistle of Warning (ReMe 35),
    Visions of the Infernal Terrors on a group; Door in a Bottle (PeTe 5);
    Disenchanting Concoction (PeVi 40, Pen +30), as Winds of Mundane Silence."""
)
_EXCITING = _words(
    """Exciting Experimentation (Minor, Hermetic): on any experimentation table
    she rolls two dice instead of one (errata), and the storyguide applies the
    more amusing result."""
)
_CONSCIENTIA_PRINTINGS = (
    Printing(
        "Gauntlet",
        20,
        _stat(
            _CONSCIENTIA,
            _CONSCIENTIA_SPELLS,
            0,
            _CONSCIENTIA_RULES,
            apparent_age=20,
            confidence=(1, 3),
            traits={"Inquisitive": 2, "Clever": 3, "Extrovert": -2},
            reputations={"Disaster in the Making": 2, "Brilliant": 1},
            abilities=_abilities(
                """Artes Liberales 1 (correcting mistakes); Awareness 2 (finding
                flaws); Bargain 1 (vis); Charm 2 (begging for favors); Code of
                Hermes 1 (nitpicking details); Etiquette 1 (apologies); Finesse 1
                (getting it right the first time); Folk Ken 2 (magi); French 5
                (explanations); Guile 1 (breaking bad news); Latin 4 (writing);
                Magic Lore 1 (famous mistakes); Magic Theory 5+2 (enchanting
                items); Parma Magica 1 (lab explosions)"""
            ),
            arts=arts_from(
                "Cr 10, In 0, Mu 10, Pe 5, Re 5, An 5, Aq 2, Au 5, Co 0, He 1, "
                "Ig 1, Im 1, Me 0, Te 10, Vi 5"
            ),
            notes=paragraphs(
                "A scruffy, small young woman in robes stained with who knows "
                "what, hair tied back and sleeves pushed up, with an ugly blue "
                "stain on her left cheek from an old experiment.",
                "Sigil: the lines around a target look twisted and broken. "
                "Voting sigil: five curved lines forming a pentagram.",
                _CONSCIENTIA_COMBAT,
                "Equipment: ink-stained robes, more vis than anyone thinks she "
                "needs, and the finest lab gear she could barter for. "
                "Encumbrance 0.",
                _EXCITING,
            ),
        ),
    ),
    Printing(
        "+15",
        35,
        _stat(
            _CONSCIENTIA,
            _CONSCIENTIA_SPELLS,
            1,
            _CONSCIENTIA_RULES,
            apparent_age=35,
            confidence=(1, 3),
            warping=(3, 0),
            traits={
                "Inquisitive": 2,
                "Clever": 3,
                "Extrovert": -2,
                "Loyal (Familiar)": 3,
            },
            reputations={"Disaster in the Making": 3, "Brilliant": 2},
            abilities=_abilities(
                """Artes Liberales 1 (correcting mistakes); Awareness 2 (finding
                flaws); Bargain 3 (vis); Charm 2 (begging for favors); Code of
                Hermes 1 (nitpicking details); Etiquette 1 (apologies); Finesse 1
                (getting it right the first time); French 5 (explanations); Folk
                Ken 2 (magi); Guile 1 (breaking bad news); Latin 4 (writing);
                Magic Lore 1 (famous mistakes); Magic Theory 8+2 (enchanting
                items); Parma Magica 1 (lab explosions); Penetration 1
                (Mentem)"""
            ),
            arts=arts_from(
                "Cr 15, In 1, Mu 15, Pe 5, Re 10, An 10, Aq 10, Au 5, Co 10, He 3, "
                "Ig 1, Im 1, Me 1, Te 10, Vi 5"
            ),
            notes=paragraphs(
                _CONSCIENTIA_COMBAT,
                "Twilight Scars: lights cast shadows of people not in the room.",
                "These fifteen years: she takes a post as librarian in Durenmar's "
                "Great Library, with seven seasons inventing spells and items, "
                "one binding her familiar, and one on a longevity ritual of 10.",
                _AUREUS,
                _EXCITING,
                _CONSCIENTIA_ITEMS,
                _CONSCIENTIA_CHARGED,
            ),
        ),
    ),
    Printing(
        "+30",
        50,
        _stat(
            _CONSCIENTIA,
            _CONSCIENTIA_SPELLS,
            2,
            _CONSCIENTIA_RULES,
            apparent_age=38,
            confidence=(2, 6),
            warping=(4, 24),
            traits={
                "Inquisitive": 2,
                "Clever": 3,
                "Extrovert": -2,
                "Loyal (Familiar)": 3,
                "Wary of Blue Potions": 1,
            },
            reputations={"Disaster": 3, "Brilliant": 2},
            abilities=_abilities(
                """Artes Liberales 1 (correcting mistakes); Awareness 2 (finding
                flaws); Bargain 3 (vis); Charm 2 (begging for favors); Code of
                Hermes 1 (nitpicking details); Etiquette 1 (apologies); Finesse 1
                (getting it right the first time); French 5 (explanations); Folk
                Ken 2 (magi); Greek 1 (caecus); Guile 1 (breaking bad news); Latin
                4 (writing); Magic Lore 1 (famous mistakes); Magic Theory 10+2
                (enchanting items); Parma Magica 1 (lab explosions); Penetration
                1 (Mentem)"""
            ),
            arts=arts_from(
                "Cr 20, In 1, Mu 20, Pe 10, Re 10, An 10, Aq 10, Au 5, Co 10, He 5, "
                "Ig 5, Im 5, Me 5, Te 10, Vi 10"
            ),
            notes=paragraphs(
                _CONSCIENTIA_COMBAT,
                "Twilight Scars: lights cast shadows of people not in the room, "
                "and her reflection is very slightly translucent.",
                "These fifteen years: settled in her post, she gives much time "
                "to her own projects: sixteen seasons inventing spells and "
                "items, and one reinventing her longevity ritual.",
                _AUREUS,
                _EXCITING,
                _CONSCIENTIA_ITEMS,
                _CONSCIENTIA_CHARGED,
            ),
        ),
    ),
    Printing(
        "+45",
        65,
        _stat(
            _CONSCIENTIA,
            _CONSCIENTIA_SPELLS,
            3,
            _CONSCIENTIA_RULES,
            apparent_age=41,
            confidence=(2, 6),
            warping=(6, 13),
            traits={
                "Inquisitive": 2,
                "Clever": 3,
                "Extrovert": -2,
                "Loyal (Familiar)": 3,
                "Wary of Blue Potions": 1,
            },
            reputations={"Disaster": 3, "Brilliant": 2},
            abilities=_abilities(
                """Artes Liberales 3 (correcting mistakes); Awareness 3 (finding
                flaws); Bargain 4 (vis); Charm 3 (begging for favors); Code of
                Hermes 2 (nitpicking details); Etiquette 2 (apologies); Finesse 2
                (getting it right the first time); French 5 (explanations); Folk
                Ken 3 (magi); Greek 1 (caecus); Guile 2 (breaking bad news); Latin
                4 (writing); Magic Lore 2 (famous mistakes); Magic Theory 10+2
                (enchanting items); Parma Magica 2 (lab explosions); Penetration
                1 (Mentem)"""
            ),
            arts=arts_from(
                "Cr 20, In 10, Mu 20, Pe 10, Re 15, An 10, Aq 10, Au 10, Co 10, He 5, "
                "Ig 5, Im 5, Me 10, Te 10, Vi 10"
            ),
            notes=paragraphs(
                _CONSCIENTIA_COMBAT,
                "Twilight Scars: lights cast shadows of people not in the room, "
                "and her reflection is very slightly translucent.",
                "These fifteen years: she takes more time to know other magi, "
                "and still spends twelve seasons inventing spells and items.",
                _AUREUS,
                _EXCITING,
                _CONSCIENTIA_ITEMS,
                _CONSCIENTIA_CHARGED,
            ),
        ),
    ),
)

# Gwidion of Verditius (pp. 33-44)

_GWIDION_COMMON: StatBlock = {
    "size": -1,
    "confidence": (1, 3),
    "traits": {"Acquisitive": 3, "Charming": 3, "Independent": 3},
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        vf_focus("Major Magical Focus", "trees"),
        vf_art("Affinity with {art}", "Herbam"),
        vf_art("Affinity with {art}", "Terram"),
        "Educated",
        ("{gild} Trained", {"gild": "Oak Gild"}),
        "Privileged Upbringing",
        "Skilled Parens",
        "Arcane Lore",
        "Verditius Magic",
        "Curse of Venus",
        "Twilight Prone",
        ("{gild} Enmity", {"gild": "Oak Gild"}),
        "Judged Unfairly",
        "Slow Caster",
        "Small Frame",
    ],
}
_GWIDION_YOUNG = characteristics(3, 0, 0, 0, -1, 2, -1, -1)
_GWIDION_OLD = characteristics(3, 0, 0, 0, -2, 2, -1, -1)
_GWIDION_SPELLS = (
    _s("Voice of the King", "ReAn", 40, 4),
    _s("Circle of Eternal Spring", "CrHe", 4),
    _s("Ladder Of Ivy", "CrHe", 15),
    _s("Fast Grow", "CrHe", 30, 2),
    _s("Fortress of Oak", "CrHe(Mu,Te)", 40, 6),
    _s("Probe Nature's Hidden Lore", "InHe", 4),
    _s("Intuition of the Forest", "InHe", 10),
    _s("Converse with Plant and Tree", "InHe", 25, 1),
    _s("Pass the Unyielding Portal", "MuHe", 5),
    _s("Thaumaturgical Transformation of Plants to Iron", "MuHe", 20, 1),
    _s("Gigantic Growth", "MuHe", 25, 2),
    _s("Razor Thorns", "MuHe(Te)", 25, 3),
    _s("Blades of Grass, Leaves of Cutting", "MuHe", 30, 2),
    _s("Awaken Consciousness of Plant", "MuHe(Me)", 55, 3),
    _s("Prune Plant", "PeHe", 5),
    _s("Wilt", "PeHe", 25, 2),
    _s("Prison Floral", "ReHe", 4),
    _s("Ring of Ever Bloom", "ReHe", 15),
    _s("Controlled Growth", "ReHe", 25, 1),
    _s("Tree Top Walk", "ReHe", 25),
    _s("Command of the Forest", "ReHe(Me)", 55, 6),
    _s("Warmth of the Wood", "CrIg", 4),
    _s("Frosted Timber", "PeIg", 20, 1),
    _s("Sight of the Blossom, Ears of the Oak", "InIm", 30, 3),
    _s("Probe for Pure Silver", "InTe", 4, 4),
    _s("Tilled Soil", "ReTe", 15),
    _s("Mold the Earth within Sight", "ReTe", 25, 1),
)
_GWIDION_RULES = _rules(
    """
Voice of the King = R Voice, D Diam, T Group. Commands whole swarms of bees, as
Commanding the Harnessed Beast; simple orders only, and the hive may resent it.

Circle of Eternal Spring = R Touch, D Ring, T Circle. Plants in the circle grow
well, as The Bountiful Feast.

Ladder Of Ivy = R Voice, D Sun, T Ind. A sturdy ivy ladder about twenty paces
long, gone at sunset or sunrise.

Fast Grow = R Touch, D Sun, T Ind. Brings a plant to full maturity in a day or
night, if cast soon after sunrise or sunset.

Fortress of Oak = Ritual, R Touch, D Mom, T Ind. Printed Cr(Mu)He(Te). Cast on
an acorn: as Conjuring the Mystic Tower, but a living eighty-foot tree with
chambers, earthen floors and hearths, designed at casting.

Gigantic Growth = R Touch, D Sun, T Ind. A plant grows a hundredfold until
sunset or sunrise.

Razor Thorns = R Voice, D Diam, T Group. Thorns spring from plants and things
made of them, +10 damage to up to ten people, and stay about two minutes.

Blades of Grass, Leaves of Cutting = R Voice, D Sun, T Group. Grass and leaves
turn sword-sharp, barring the way even to the armored.

Awaken Consciousness of Plant = Ritual, R Voice, D Year, T Group. As Stir the
Slumbering Tree on a whole grove.

Prune Plant = Printed Pe(Re)He 20 in its own entry, level 5 in the blocks. R
Voice, D Mom, T Ind. Reshapes a plant, as skilled pruning, without adding to it
or killing it.

Wilt = R Voice, D Mom, T Part. A plant wilts and dies. The blocks print level
25, its own entry 35.

Ring of Ever Bloom = R Touch, D Ring, T Circle. Plants keep blooming out of
season.

Controlled Growth = Ritual, R Touch, D Year, T Ind. Shapes a plant's growth for
the year, as a fine gardener would.

Tree Top Walk = R Voice, D Conc, T Group. Branches bend so he can walk from tree
to tree. The +15 block prints level 15, all the others and its entry 25.

Prison Floral = R Touch, D Ring, T Circle. Holds aggressively Warped plants
inside the circle. The blocks print level 4, its own entry 30.

Command of the Forest = Ritual, R Touch, D Sun, T Group. Up to 10,000 plants obey
his orders, even to uproot. Its analysis counts +2 Voice.

Warmth of the Wood = R Touch, D Sun, T Part. Warms bark or planks to the touch.
The blocks print level 4, its own entry 10.

Frosted Timber = R Touch, D Sun, T Part. Cools bark or planks to the touch.

Sight of the Blossom, Ears of the Oak = R Arc, D Sun, T Group. Sees and hears at
a distance through an Arcane Connection; he uses leaves and buds from his
forest.

Tilled Soil = R Voice, D Mom, T Part. Tills 1,000 cubic paces of soil.

Mold the Earth within Sight = R Sight, D Mom, T Part. Shapes earth and stone
equal to a hundred men, not metals or gems. Errata: level 25, +1 stone (the
blocks agree; its own entry prints 30).
"""
)
_GWIDION_COMBAT = _words(
    """Combat: dodge Init -1, Defense -1; fist Init -1, Attack -1, Defense -1,
    Damage 0; kick Init -2, Attack -1, Defense -2, Damage +3. Soak +3."""
)
_GWIDION_KIT = (
    "Equipment: peasant work clothes in his pack, a basic survival kit, and "
    "handmade portable gardening tools. Encumbrance none."
)
_GWIDION_ITEMS = _words(
    """His covenant's works (the book does not date them; every plant is
    enchanted small and then enlarged, so it fits the lab). Staff of Silent
    Forest Stride (PeIm(He) 25): plants it touches make no noise. Stone Disks,
    lesser items: Warmth of Wood (CrIg 24, heats the covenant), Frosted Timber
    (PeIg(He) 39, cools it), Evergreen (CrHe 34), Controlled Growth (ReHe 49).
    Fresh Air Vines (10 vis): Chamber of Spring Breezes (CrAu 39), Gigantic
    Growth (MuHe 29). Water Vines (12 vis): Move Water (ReAq 23), Read Surface
    Thoughts (InMe 34), Gigantic Growth. Wall of Iron Thorns (12 vis): a
    blackberry 1 pace deep and 4 high round the covenant: Plants of Iron
    (MuHe(Te) 34), Single Root System (MuHe 34). Sun Ivy (12 vis): Conjured
    Daylight (CrIg 54; errata T Group, with +2 Group, +1 size), Single Root
    System. Storm Tree: Summon Heavy Rain (ReAu 43, 1/day), Know When Tree Is
    Dry (InHe 8). Poppy Beds (12 vis): Soften Earth and Plants (MuTe(He) 29),
    Single Root System. The Boiling Bush (12 vis): Boil Water (CrIg 25), Single
    Root System. Bath of the Yellow Roses (12 vis): Warm Water (CrIg 19), Single
    Root System. Tree Hive (10 vis, up to 2,000 bees): Living Hive (ReHe 44),
    Friendly Bees (ReAn 39). Ring of Mixed Compost (16 vis): privies flushed by
    the Water Vines feed a chamber ringed by Mixed Compost (ReTe(Co,He) 33,
    1/day). Rings of Basketed Transport (12 vis): four rings move baskets for
    thirty: Move Gigantic Wicker Basket (ReHe 48), Read Surface Thoughts."""
)
_GWIDION_TALISMAN = _words(
    """Talisman: Edward, his Riding Tree, an oak now so Warped that its boughs
    are hands, its roots feet, and a gnarled face on its trunk shows his moods.
    He rides it round his forest, and thinks of building his lab on it. 10 vis
    to open, more later as a talisman. Attunement: +21 Protection from Storms
    (errata; the book prints +7). Effects: Evergreen (CrHe 14), Plants of Iron
    (MuHe(Te) 34), Controlled Growth (ReHe 29), The Movements of a Man (ReHe 48:
    moves the tree as his own body, as Lord of the Trees), Read Surface Thoughts
    (InMe 34), Ward Against Heat and Flames (ReIg 54: +15 Soak against fire, no
    flames within a pace of it or its riders)."""
)
_GWIDION_PRINTINGS = (
    Printing(
        "Gauntlet",
        22,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            0,
            _GWIDION_RULES,
            characteristics=characteristics(3, 0, 0, 0, 0, 2, -1, -1),
            apparent_age=21,
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 1 (lab work); Craft: Gardening 1 (trees); Latin 4
                (Hermetic usages); Leadership 1 (inspiration); Magic Theory 4
                (enchanting items); Masonry 1 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 1 (Herbam); Philosophiae 1 (ritual
                magic); Survival 1 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 5, In 1, Mu 2, Pe 10, Re 18, An 0, Aq 0, Au 0, Co 0, He 10, "
                "Ig 8, Im 0, Me 1, Te 8, Vi 0"
            ),
            notes=paragraphs(
                "Sap on his fingers, a blade of grass in his mouth, dirt on his "
                "knees. His tan sets him apart from other magi, and he dresses "
                "like a prosperous peasant.",
                "Casting sigil: the sound of trees bending in wind, louder with "
                "stronger spells. Voting sigil, when he still voted: the World "
                "Tree of his dreams.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "No Twilight Scars. Errata: a year older than printed at every "
                "stage, and Arcane Lore in place of Well-Traveled.",
            ),
        ),
    ),
    Printing(
        "+15",
        37,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            1,
            _GWIDION_RULES,
            characteristics=_GWIDION_YOUNG,
            apparent_age=36,
            decrepitude=(0, 1),
            warping=(3, 0),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 1 (lab work); Craft: Gardening 1 (trees); Latin 4
                (Hermetic usages); Leadership 1 (inspiration); Magic Theory 5
                (enchanting items); Masonry 1 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 2 (Herbam); Philosophiae 1 (ritual
                magic); Survival 3 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 8, Pe 10, Re 21, An 2, Aq 1, Au 1, Co 1, He 21, "
                "Ig 8, Im 1, Me 1, Te 10, Vi 1"
            ),
            notes=paragraphs(
                "At thirty he swapped the blade of grass for a sturdy walking "
                "stick. His skin begins to wrinkle; he still dresses as a farmer.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "These fifteen years: after long travels he finds an empty "
                "forest of little aura, far from Durenmar, for his covenant, and "
                "brings the villages through drought and famine with magic. 60 "
                "xp in Abilities, 245 in Arts, 145 levels of spells.",
            ),
        ),
    ),
    Printing(
        "+30",
        52,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            2,
            _GWIDION_RULES,
            characteristics=_GWIDION_YOUNG,
            apparent_age=51,
            decrepitude=(0, 2),
            warping=(4, 8),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 5
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 12, Pe 12, Re 21, An 3, Aq 1, Au 2, Co 1, He 21, "
                "Ig 8, Im 3, Me 1, Te 10, Vi 1"
            ),
            notes=paragraphs(
                "Deeply wrinkled now, leaning harder on his stick, the price of "
                "starting a longevity ritual so late.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "These fifteen years: his magic builds the farms that earn the "
                "covenant most of its income. At 50 he serves as a lab assistant "
                "in trade for a longevity ritual: 14 pawns of Creo vis, +5, with "
                "the covenant's +1 an aging modifier of 6. 225 xp in Abilities, "
                "75 in Arts, 120 levels of spells.",
            ),
        ),
    ),
    Printing(
        "+45",
        67,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            3,
            _GWIDION_RULES,
            characteristics=_GWIDION_YOUNG,
            apparent_age=60,
            decrepitude=(0, 2),
            warping=(4, 23),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 5
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 6, In 13, Mu 20, Pe 12, Re 21, An 3, Aq 1, Au 2, Co 1, He 25, "
                "Ig 8, Im 13, Me 2, Te 10, Vi 1"
            ),
            notes=paragraphs(
                "Nearly white-haired, his face a tanned, wrinkled prune, but "
                "still strong and well-muscled.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "These fifteen years: he walks his forest, waking and talking "
                "with the plants. 365 xp in Arts, 115 levels of spells.",
            ),
        ),
    ),
    Printing(
        "+60",
        82,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            4,
            _GWIDION_RULES,
            characteristics=_GWIDION_YOUNG,
            apparent_age=68,
            decrepitude=(0, 2),
            warping=(5, 13),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 7
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 15, In 14, Mu 20, Pe 12, Re 21, An 17, Aq 2, Au 2, Co 2, He 25, "
                "Ig 8, Im 14, Me 7, Te 15, Vi 1"
            ),
            notes=paragraphs(
                "His white hair is thinning and his face scarred by age, but his "
                "stamina beats most men a third his age.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "Twilight Scar: he must stand an hour in sunlight after each meal "
                "or it will not digest.",
                "These fifteen years: bees become his new passion, with notes "
                "sent to Durenmar, and the covenant gains honey all year. 65 xp "
                "in Abilities, 345 in Arts, 40 levels of spells.",
            ),
        ),
    ),
    Printing(
        "+75",
        97,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            5,
            _GWIDION_RULES,
            characteristics=_GWIDION_OLD,
            apparent_age=81,
            decrepitude=(0, 3),
            warping=(5, 29),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 10
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 25, In 14, Mu 22, Pe 12, Re 21, An 17, Aq 2, Au 2, Co 2, He 25, "
                "Ig 8, Im 14, Me 8, Te 20, Vi 1"
            ),
            notes=paragraphs(
                "Bald on top, the hair at the sides left to grow; age has caught "
                "him, and he leans heavily on his stick.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "Twilight Scars: an hour in sunlight after each meal or it will "
                "not digest; a compelling voice.",
                "These fifteen years: in spring of his 93rd year he again trades "
                "service for a longevity ritual: 19 pawns of Creo vis, +9, with "
                "the covenant's +1 an aging modifier of 10. 135 xp in Abilities, "
                "316 in Arts.",
            ),
        ),
    ),
    Printing(
        "+94",
        116,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            6,
            _GWIDION_RULES,
            characteristics=_GWIDION_OLD,
            apparent_age=93,
            decrepitude=(0, 3),
            warping=(6, 18),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 10
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 25, In 14, Mu 22, Pe 12, Re 25, An 17, Aq 2, Au 2, Co 2, He 25, "
                "Ig 8, Im 14, Me 25, Te 25, Vi 1"
            ),
            notes=paragraphs(
                "His scars keep him golden-tanned, wrinkled and nearly bald; "
                "otherwise as he was at ninety-three.",
                _GWIDION_COMBAT,
                _GWIDION_KIT,
                "Twilight Scars: an hour in sunlight after each meal or it will "
                "not digest; a compelling voice; his footsteps leave puddles.",
                "These nineteen years: he devises the great fortress of oak, dirt "
                "and green limbs. 460 xp in Arts, 105 levels of spells.",
            ),
        ),
    ),
    Printing(
        "+105",
        127,
        _stat(
            _GWIDION_COMMON,
            _GWIDION_SPELLS,
            7,
            _GWIDION_RULES,
            characteristics=_GWIDION_OLD,
            apparent_age=101,
            decrepitude=(0, 4),
            warping=(6, 29),
            abilities=_abilities(
                """Artes Liberales 4 (ritual magic); Charm 4 (being witty);
                Concentration 4 (lab work); Craft: Gardening 2 (trees); Latin 4
                (Hermetic usages); Leadership 2 (inspiration); Magic Theory 10
                (enchanting items); Masonry 2 (buildings); Order of Hermes Lore 3
                (politics); Parma Magica 5 (Herbam); Philosophiae 4 (ritual
                magic); Survival 5 (forests); Welsh 5 (storytelling)"""
            ),
            arts=arts_from(
                "Cr 25, In 14, Mu 22, Pe 15, Re 25, An 17, Aq 2, Au 2, Co 2, He 25, "
                "Ig 15, Im 14, Me 25, Te 25, Vi 1"
            ),
            notes=paragraphs(
                "Frail and withered, he cannot now walk unaided.",
                _GWIDION_COMBAT,
                "Equipment: the Riding Tree talisman, and his work clothes, "
                "survival kit and gardening tools. Encumbrance none.",
                "Twilight Scars: an hour in sunlight after each meal or it will "
                "not digest; a compelling voice; his footsteps leave puddles; "
                "people want to listen to him.",
                "These eleven years: he adopts a sapling from the old forest fire "
                "as his talisman, and readies the covenant, forest and hives for "
                "his end. He means to awaken Edward for good and give him powers "
                "to wake other trees, call rain and guard the forest, if he lasts "
                "fifteen more years. 126 xp in Arts, sixteen seasons enchanting.",
                _GWIDION_TALISMAN,
                _GWIDION_ITEMS,
            ),
        ),
    ),
)

# Hugh of Flambeau (pp. 45-51)

_HUGH: StatBlock = {
    "characteristics": characteristics(1, -2, -1, 0, 2, 3, 1, 0),
}
_HUGH_TRAITS = {"Recklessly Brave": 3, "Argumentative": 2, "Belligerent": 2}
_HUGH_LATER_TRAITS = {"Loyal to Bathild": 3, **_HUGH_TRAITS}
_HUGH_VIRTUES_FIRST: list[str | tuple[str, dict[str, str]]] = [
    "The Gift",
    "Hermetic Magus",
    ("Mythic Blood", {"detail": "valkyrie"}),
    vf_art("Affinity with {art}", "Rego"),
    vf_focus("Minor Magical Focus", "arms and armor"),
    vf_puissant("Great Weapon"),
    ("Puissant {art}", {"art": "Perdo"}),
    "Rapid Convalescence",
    "Skilled Parens",
    ("Special Circumstances", {"circumstance": "in melee combat"}),
    "Tough",
    "Warrior",
    "Magic Addiction",
    "Ambitious (Major)",
    "Short-Ranged Magic",
    "Poor Hearing",
    "Reckless (Minor)",
]
_HUGH_VIRTUES_INITIATE: list[str | tuple[str, dict[str, str]]] = [
    "The Gift",
    "Hermetic Magus",
    ("Mythic Blood", {"detail": "valkyrie"}),
    vf_art("Affinity with {art}", "Rego"),
    vf_focus("Minor Magical Focus", "arms and armor"),
    vf_puissant("Great Weapon"),
    ("Puissant {art}", {"art": "Perdo"}),
    "Rapid Convalescence",
    "Skilled Parens",
    ("Special Circumstances", {"circumstance": "in melee combat"}),
    "Strong-Willed",
    "Tough",
    ("True Friend", {"detail": "from Familiar"}),
    "Warrior",
    "Magic Addiction",
    "Ambitious (Major)",
    "Short-Ranged Magic",
    "Dutybound",
    "Poor Hearing",
    "Reckless (Minor)",
]
_HUGH_VIRTUES_BRIDE = [*_HUGH_VIRTUES_INITIATE]
_HUGH_VIRTUES_BRIDE.insert(4, "Clear Thinker")
_HUGH_SPELLS = (
    _s("Doublet of Impenetrable Silk", "MuAn", 15),
    _s("Blunt the Viper's Fangs", "PeAn", 15),
    _s("Circle of Beast Warding", "ReAn", 5),
    _s("Bind Wound", "CrCo", 10),
    _s("Assume the Stature of the Giants of Eld", "MuCo", 10, 1),
    _s("Avalanche of Flesh and Steel", "MuCo", 10, 1),
    _s("Gift of the Bear's Fortitude", "MuCo", 25, 1),
    _s("The Blessing of Starkad", "MuCo", 25, 2),
    _s("Turb of Giants", "MuCo", 25, 2),
    _s("Dust to Dust", "PeCo", 15),
    _s("Rise of the Feathery Body", "ReCo", 10),
    _s("Endurance of the Berserkers", "ReCo", 15),
    _s("Curse of the Rotted Wood", "PeHe", 5),
    _s("Repel the Wooden Shafts", "ReHe", 10),
    _s("Halt the Piercing Shafts", "ReHe(Te)", 25, 2),
    _s("Aura of the Ennobled Presence", "MuIm", 10),
    _s("Breaking the Captain's Baton", "PeMe", 10, 1),
    _s("Blunting the Iron's Bite", "MuTe", 10, 2),
    _s("Edge of the Razor", "MuTe", 20, 0, "Penetration"),
    _s("The Wizard's Parry", "ReTe", 5, 1, "Fast Casting"),
    _s("Disarm the Warrior", "ReTe", 10, 2),
    _s("The Instant Ring Fort", "ReTe", 15, 1),
    _s("Circular Wall of Shields", "ReTe", 30, 1),
    _s("Maintaining the Demanding Spell", "ReVi", 20, 0, "Fast Casting", until=1),
    _s(
        "Maintaining the Demanding Spell",
        "ReVi",
        20,
        2,
        "Fast Casting",
        "Imperturbable",
    ),
)
_HUGH_RULES = _rules(
    """
Assume the Stature of the Giants of Eld = R Per, D Diam, T Ind. +3 Size with
gear, wounds every 8 points, Characteristics unchanged; An, He and Te casting
requisites usually needed for gear.

Avalanche of Flesh and Steel = R Touch, D Conc, T Group. Up to ten men run as
fast as a horse, adding their Athletics, up to +3, to the first Attack.

The Blessing of Starkad = R Touch, D Sun, T Part. Two more arms: +3 to climbing
and Strength tasks, and a second set of weapons, two attacks a round alone or
an extra uncounted member in a group. By a new guideline: MuCo 5, add or take
away human parts so the target no longer looks human, T Part.

Turb of Giants = R Touch, D Diam, T Group. As the Stature of the Giants on ten
men up to Size +1.

Halt the Piercing Shafts = R Per, D Diam, T Ind. Wood and metal missiles fall at
his feet.

Breaking the Captain's Baton = R Voice, D Mom, T Ind. The leader forgets how to
coordinate a Trained Group, until he relearns it by practice; the squad fights
Untrained unless another takes over.

Blunting the Iron's Bite = R Voice, D Diam, T Ind. A blade's total damage,
Attack Advantage included, is halved, rounded up; Magic Resistance can block
it, so he often casts it forcelessly.

The Wizard's Parry = Errata: R Voice, D Mom, T Ind, no gestures, without penalty.
Deflects one melee blow he is aware of, wholly away from him; his fast-cast
defense (Base 2, +2 Voice, +1 no gestures). Herbam requisite for wooden weapons.

Disarm the Warrior = R Voice, D Mom, T Ind. Pulls an object to him with Strength
+5, opposed if held; Dex + Athletics 9+ to catch it.

The Instant Ring Fort = R Touch, D Mom, T Part. Throws up a ring of packed earth
four paces across, two thick, eight feet high, from a ditch around him.

Circular Wall of Shields = R Touch, D Sun, T Group. Up to twenty shields orbit
up to ten people, cover against missiles and, by Per + Finesse plus the shield's
Defense, melee. A shield has Soak 3 and breaks at over 10 points in a blow.
"""
)
_GIRD = _words(
    """Gird the Warrior (0 points, Init 0, Terram): with a few words and a sweep
    of his hands his clothes become full metal scale, Protection 7, Load 7,
    until he dismisses it (MuAn(He,Te) 30, R Touch, D Conc, T Group)."""
)
_TONATRIS = _words(
    """Tonatris, a Roman caestus of iron-plated leather, opened with 10 pawns,
    five used. Thumb between ring and little fingers: Night-Time Thunder (ReMe
    20, Pen +12, 12/day, D Diam) puts the target to sleep. Thumb between middle
    and ring fingers: Vaulting Lightning (ReCo 30, Pen +12, 12/day) throws the
    target 5 paces for +8 damage, doubled by a wall or hard landing."""
)
_TROLLS_WIFE = _words(
    """Talisman: Troll's Wife, a long bearded axe of steel and silver on a holly
    haft banded in brass, carved with horses, eagles and wolves, six discs of
    amber and bloodstone near the head. Only the haft is enchanted, so Magic
    Resistance does not stop the blade. Excellent quality (City & Guild pp.
    69-70): +3 Attack and Defense; otherwise a pole axe. 12 pawns to open, now
    full. Attunements: +3 Corpus, +4 blood and wounds, +4 demons and angels, +7
    harm or repel faeries."""
)
_TROLLS_WIFE_FIRST = (
    "Its first effect: Fell the Faerie (PeVi 23, Pen 20, 6/day): on the words "
    '"ferrum et fraxinus", a haft strike costs a faerie 15 Might.'
)
_TROLLS_WIFE_LATER = _words(
    """Later effects: Wood that Neither Bends Nor Breaks (MuHe(Te) 14, constant);
    Hew the Hell-Beast (PeVi 23, Pen 20, 6/day): on "os et orichalcum", 15 Might
    from an Infernal being; Sharpening the Wizard's Blade of Vim (MuVi 28,
    24/day): on "acuere", +10 Penetration to an effect of level 10 or less in
    the axe."""
)
_BATHILD = _words(
    """Familiar: Bathild, a magical roan charger the colour of dried blood, who
    claims Sleipnir's descent; Hugh won her from an einheri by starting a war
    between two villages, deep in the supposed Order of Odin's lands. Bond (ReTe
    Lab Total 43): Gold +1, Silver +1, Bronze +3. Magic Might 8 (Animal); Int
    -3, Per +1, Pre 0, Com -4, Str +4, Sta +3, Dex -1, Qik +2; Size +2; Season
    Summer; Confidence 2 (6). Kick Init +7, Attack +8, Defense +9, Damage +5;
    Soak +5. Loyal to Hugh +3, Vain +3, Brave +2, Chatty +1. Abilities Athletics
    4, Awareness 3, Brawl 4, Concentration 2, Faerie Lore 2, Folk Ken 3, Local
    Area Lore 3, Magic Lore 3, Order of Hermes Lore 2, Leadership 3, Swim 2,
    Wilderness Sense 4. Vis: 2 Animal, in her hooves. Power: Beast and Rider As
    One (4 points, Init -2): the rider's legs meld to her and their minds work
    together; no Ride rolls, no limit of +3 on his Ride bonus in combat, no
    falling off or dismounting."""
)
_RIDE = _words(
    """Bond power Ride of the Einherjar (ReAn 27, 3/day): she runs on air until
    her feet touch ground."""
)
_GIRD_STEED = _words(
    """Bond power Gird the Steed for War (CrTe(An) 30, 1/day, D Sun): metal scale
    barding, Protection 7."""
)
_HUGH_FACE = _words(
    """A tall, broad-shouldered man, heavy-browed, squat-featured and
    broken-nosed, in excellent condition. Short hair, no beard, though he often
    forgets to shave for days; he could pass for a common soldier."""
)
_HUGH_PRINTINGS = (
    Printing(
        "Gauntlet",
        29,
        _stat(
            _HUGH,
            _HUGH_SPELLS,
            0,
            _HUGH_RULES,
            apparent_age=29,
            confidence=(1, 3),
            virtues_flaws=_HUGH_VIRTUES_FIRST,
            traits=_HUGH_TRAITS,
            abilities=_abilities(
                """Artes Liberales 2 (copying); Athletics 1 (in armor); Awareness
                2 (at night); Brawl 4 (punch); Code of Hermes 1 (high crimes);
                Concentration 2 (in battle); Criminal Lore 1 (local town);
                Finesse 2 (Rego); Great Weapon 5+2 (pole axe); Latin 4 (shouting);
                Leadership 2 (soldiers); Magic Theory 4 (Rego effects); Native
                Language 5 (criminal argot); Order of Hermes Lore 1 (House
                Flambeau); Parma Magica 1 (Corpus); Penetration 2 (Corpus); Ride
                2 (in battle)"""
            ),
            arts=arts_from(
                "Cr 3, In 1, Mu 4, Pe 6+3, Re 12, An 2, Aq 1, Au 1, Co 6, He 4, "
                "Ig 0, Im 0, Me 2, Te 5, Vi 6"
            ),
            notes=paragraphs(
                _HUGH_FACE,
                "Casting sigil: Weapons, clashing arms or a keen edge. Voting "
                "sigil: a hand axe engraved with House Flambeau's symbol.",
                "Combat: fist Init -1, Attack +6, Defense +4, Damage +2; pole axe "
                "Init 0, Attack +14, Defense +7, Damage +13. Soak 13 in armor, +3 "
                "with Doublet of Impenetrable Silk. No Twilight Scars.",
                "Equipment: pole axe, 2 throwing axes. Encumbrance -1 (Load 9, "
                "Burden 3).",
                _GIRD,
            ),
        ),
    ),
    Printing(
        "+15",
        44,
        _stat(
            _HUGH,
            _HUGH_SPELLS,
            1,
            _HUGH_RULES,
            apparent_age=37,
            confidence=(1, 3),
            warping=(3, 0),
            virtues_flaws=_HUGH_VIRTUES_FIRST,
            traits=_HUGH_TRAITS,
            reputations={"Hoplite (Hermetic)": 2},
            abilities=_abilities(
                """Artes Liberales 2 (copying); Athletics 2 (in armor); Awareness
                2 (at night); Brawl 4 (punch); Code of Hermes 1 (high crimes);
                Concentration 2 (in battle); Criminal Lore 1 (local town);
                Finesse 2 (Rego); Great Weapon 5+2 (pole axe); Latin 4 (shouting);
                Leadership 2 (soldiers); Magic Theory 5 (Rego effects); Native
                Language 5 (criminal argot); Order of Hermes Lore 1 (House
                Flambeau); Parma Magica 4 (Corpus); Penetration 4 (Corpus); Ride
                2 (in battle)"""
            ),
            arts=arts_from(
                "Cr 5, In 4, Mu 6, Pe 9+3, Re 14, An 5, Aq 1, Au 1, Co 10, He 6, "
                "Ig 3, Im 3, Me 6, Te 8, Vi 8"
            ),
            notes=paragraphs(
                _HUGH_FACE,
                "Combat: Tonatris Init 0, Attack +6, Defense +6, Damage +4; pole "
                "axe Init +1, Attack +14, Defense +8, Damage +13. Soak 13 in "
                "armor, +3 with Gift of the Bear's Fortitude, +3 with Doublet of "
                "Impenetrable Silk. No Twilight Scars.",
                "Equipment: Tonatris, pole axe. Encumbrance -1 (Load 9, Burden 3).",
                "Experience towards the next score: Magic Theory 1.",
                _GIRD,
                "These fifteen years: four seasons on his gauntlet, one on his "
                "longevity ritual; 105 levels of spells, 194 xp in Arts, 121 in "
                "Abilities.",
                _TONATRIS,
            ),
        ),
    ),
    Printing(
        "+30",
        59,
        _stat(
            _HUGH,
            _HUGH_SPELLS,
            2,
            _HUGH_RULES,
            apparent_age=46,
            confidence=(2, 6),
            warping=(4, 10),
            virtues_flaws=_HUGH_VIRTUES_INITIATE,
            traits=_HUGH_LATER_TRAITS,
            reputations={"Hoplite (Hermetic)": 3},
            abilities=_abilities(
                """Artes Liberales 2 (copying); Athletics 2 (in armor); Awareness
                2 (at night); Brawl 4 (punch); Code of Hermes 1 (high crimes);
                Concentration 2 (in battle); Criminal Lore 1 (local town);
                Finesse 2 (Rego); Great Weapon 6+2 (pole axe); Latin 4 (shouting);
                Leadership 3 (soldiers); Magic Theory 6 (Rego effects); Legion of
                Mithras Lore 1 (initiation); Native Language 5 (criminal argot);
                Order of Hermes Lore 2 (House Flambeau); Parma Magica 5 (Corpus);
                Penetration 5 (Corpus); Ride 2 (in battle); Teaching 1 (Arts)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 6, Pe 10+3, Re 15, An 7, Aq 5, Au 5, Co 10, He 5, "
                "Ig 5, Im 5, Me 5, Te 8, Vi 11"
            ),
            notes=paragraphs(
                _HUGH_FACE + " He is growing grizzled, with a few small scars.",
                "Combat: Tonatris Init 0, Attack +6, Defense +6, Damage +4; "
                "Troll's Wife Init +1, Attack +18, Defense +12, Damage +13, from "
                "horseback Attack +21, Defense +15. Soak 16 in armor with the "
                "Bronze Cord, +3 with Gift of the Bear's Fortitude, +3 with "
                "Doublet of Impenetrable Silk. No Twilight Scars.",
                "Equipment: Troll's Wife, Tonatris. Encumbrance -1 (Load 9, Burden 3).",
                "Experience towards the next score: Pe 8.",
                "From the Legion of Mithras: Strong-Willed, Dutybound. From his "
                "familiar: True Friend. The block prints Puissant Brawl where "
                "earlier blocks have Puissant Great Weapon; the +2 stays on "
                "Great Weapon, so this is taken as a misprint.",
                _GIRD,
                "These fifteen years: a familiar, a talisman and an apprentice. "
                "One season forging the bond, two empowering it with Ride of the "
                "Einherjar, four on Troll's Wife, five training the apprentice; "
                "90 levels of spells, 116 xp in Arts, 154 in Abilities.",
                _BATHILD,
                _RIDE,
                _TROLLS_WIFE,
                _TROLLS_WIFE_FIRST,
                _TONATRIS,
            ),
        ),
    ),
    Printing(
        "+45",
        74,
        _stat(
            _HUGH,
            _HUGH_SPELLS,
            3,
            _HUGH_RULES,
            aging_points={"dexterity": 1},
            apparent_age=54,
            decrepitude=(0, 1),
            confidence=(2, 6),
            warping=(5, 15),
            virtues_flaws=_HUGH_VIRTUES_BRIDE,
            traits=_HUGH_LATER_TRAITS,
            reputations={"Hoplite (Hermetic)": 3},
            abilities=_abilities(
                """Artes Liberales 2 (copying); Athletics 2 (in armor); Awareness
                2 (at night); Brawl 4 (punch); Code of Hermes 2 (high crimes);
                Concentration 3 (in battle); Criminal Lore 1 (local town);
                Finesse 3 (Rego); Great Weapon 7+2 (pole axe); Latin 4 (shouting);
                Leadership 4 (soldiers); Legion of Mithras Lore 2 (initiation);
                Magic Theory 7 (Rego effects); Native Language 5 (criminal argot);
                Order of Hermes Lore 2 (House Flambeau); Parma Magica 5 (Corpus);
                Penetration 5 (Corpus); Ride 2 (in battle); Teaching 3 (Arts)"""
            ),
            arts=arts_from(
                "Cr 5, In 5, Mu 8, Pe 13+3, Re 17, An 7, Aq 5, Au 5, Co 12, He 7, "
                "Ig 5, Im 5, Me 5, Te 10, Vi 12"
            ),
            notes=paragraphs(
                "A tall, broad-shouldered man, heavy-browed, squat-featured and "
                "broken-nosed, in excellent condition; a scarred, grizzled "
                "veteran with short greying hair, often unshaven.",
                "Combat: Tonatris Init 0, Attack +6, Defense +6, Damage +4; "
                "Troll's Wife Init +1, Attack +19, Defense +13, Damage +13, from "
                "horseback Attack +22, Defense +16, one more each with Beast and "
                "Rider As One. Soak 16 in armor with the Bronze Cord, +3 with "
                "Gift of the Bear's Fortitude, +3 with Doublet of Impenetrable "
                "Silk. No Twilight Scars.",
                "Equipment: Troll's Wife, Tonatris. Encumbrance -1 (Load 9, Burden 3).",
                "Experience towards the next score: Re 3.",
                "From the Legion of Mithras: Clear Thinker, Strong-Willed, "
                "Dutybound. From his familiar: True Friend. The block prints "
                "Puissant Brawl; the +2 stays on Great Weapon, so this is taken as a "
                "misprint.",
                _GIRD,
                "These fifteen years: four seasons adding three talisman effects, "
                "four on a second bond power, and ten finishing his apprentice, "
                "now a magus. 135 xp in Arts, 165 in Abilities.",
                _BATHILD,
                _RIDE,
                _GIRD_STEED,
                _TROLLS_WIFE,
                _TROLLS_WIFE_FIRST,
                _TROLLS_WIFE_LATER,
                _TONATRIS,
            ),
        ),
    ),
)

MAGI: tuple[Magus, ...] = (
    Magus(
        name="Alexander of Jerbiton",
        house="house_jerbiton",
        summary=paragraphs(
            "A Jerbiton of average height, olive-skinned and dark-haired, who "
            "gives his life to exploring the North African deserts. As an "
            "apprentice he dreamed of the ruins there, and his easy-going master "
            "gave him the skills to find trouble without those to escape it, "
            "which he mends later. Scrawny when young and wiry with age, leathered "
            "by the Egyptian sun, he dresses as the locals do.",
            "He turns himself and his attendants into animals to cross hard "
            "country, leads grogs on expeditions, and writes journals his House "
            "values. Story seeds: an expedition to Ethiopia or the Kushite ruins "
            "and their wind guardians; a rival whose ship was lost, some say "
            "after his clothes burned from a Conflagratious Lanyard.",
        ),
        printings=_ALEXANDER_PRINTINGS,
    ),
    Magus(
        name="Aurulentus of Jerbiton",
        house="house_jerbiton",
        summary=paragraphs(
            "A magus from a family of mages: the fifth straight generation of "
            "seventh sons, under a prophecy that the seventh son of the seventh "
            "generation will reshape magic. The line began when Askanius loved a "
            "nymph of Artemis in Greece, and each father has sired seven sons his "
            "own way: charm (Alexander, Antipater), passive Corpus magic (Alboin), "
            "love magic (Altus). Aurulentus means to father all seven on one "
            "woman, his true love Semira, so he devotes his career to health, "
            "fertility and children, and makes a Longevity Ritual that leaves "
            "its users fertile.",
            "His own seventh son, Arbus Tutus, has two daughters and shows little "
            "wish for more, or for women, so the grandson the prophecy needs is "
            "in doubt. His spells and devices for mothers and children fill his "
            "covenant. Story seeds: magi who want the fertile Longevity Ritual; "
            "the covenant's unusual birth rate.",
        ),
        secrets=[
            titled(
                "Whether the prophecy is real",
                "The prophecy may be nothing: the priest and the nymph could have "
                "been faeries wagering they could fool seven generations of magi.",
            ),
        ],
        printings=_AURULENTUS_PRINTINGS,
    ),
    Magus(
        name="Conscientia of Bonisagus",
        house="house_bonisagus",
        home="Durenmar",
        summary=paragraphs(
            "A village girl from near Carcassonne, a prodigy of theory whose "
            "simplest spells fizzled. Her Tytalus master raged at her until a "
            "Bonisagus saw what she was and took her to Durenmar. She assisted in "
            "high experiments, the last of which wrecked the lab and sent her "
            "parens into Twilight. Since her Gauntlet she has stayed in that "
            "lab, awaiting his return, and later takes a librarian's post in the "
            "Great Library.",
            "She makes Lab Texts, casting tablets and items to order, bartering "
            "for equipment and supplies. She pads her estimates so she can "
            "finish early and seem a miracle worker, or spends the spare time on "
            "the spell her parens was developing, whose nature the storyguide "
            "decides. Story seeds: the unfinished spell; a patron's item with a "
            "side effect.",
        ),
        secrets=[
            titled(
                "Cultellus",
                "Cultellus, the Parma-dispelling knife she says she never finished, "
                "is listed among her works; its patron never came back for it.",
            ),
        ],
        printings=_CONSCIENTIA_PRINTINGS,
    ),
    Magus(
        name="Gwidion of Verditius",
        house="house_verditius",
        summary=paragraphs(
            "Gwidion Griffith, a four-foot, curly-haired Welshman, tanned and "
            "weathered from a life with his hands in the soil, who looks a "
            "peasant but for his rune-cut staff and satchel. Once a rising star "
            "of his gild and House, he broke with his master at Tribunal, voted "
            "against the gild on vis rights, earned its enmity, and left "
            "Durenmar in disgust for the woods and farms of Wales.",
            "Defending villagers from bandits threw him into Twilight and a "
            "vision of the World Tree. He settled in a nearly empty wood to "
            "study it and has not left. His covenant, a living tree, runs on "
            "enchanted plants, with farmland, then honey, for income. Story "
            "seeds: an old feud with the Oak Gild; a forest of awakened trees; "
            "what happens to it all at his death or Final Twilight.",
        ),
        printings=_GWIDION_PRINTINGS,
    ),
    Magus(
        name="Hugh of Flambeau",
        house="house_flambeau",
        summary=paragraphs(
            "Hugh Hostis was found at fourteen working as a street gang's "
            "heavy, frightening people with his Gift, and trained in the School "
            "of Ramius, which pairs mundane attacks with magical defense. An "
            "excellent soldier, half-deaf from blows to the head, he believes "
            "his mother's tale of valkyrie blood and their armor. Always in the "
            "front line, he casts defenses on his fellows; grogs respect his "
            "skill and fear his temper. His favorite trick is to wound a "
            "supernatural foe, then use the blood on his blade as an Arcane "
            "Connection.",
            "After nearly fifty years he is a prominent member of his Tribunal, "
            "hunting Marched magi with loyal grogs. Story seeds: a Wizard's March "
            "that needs a hoplite; his bargain with an einheri; the supposed "
            "Order of Odin.",
        ),
        secrets=[
            titled(
                "Hugh in the Legion of Mithras",
                "Two decades out of apprenticeship he was initiated into the Legion "
                "of Mithras (The Mysteries Revised pp. 118-122), and holds its "
                "second rank, the Bride.",
            ),
            titled(
                "The Legion's errands",
                "The Legion of Mithras's errands take Hugh beyond the Order's "
                "lands after rumored hostile magicians; he has slain several hedge "
                "wizards and thinks none was a real threat, but obeys.",
            ),
        ],
        printings=_HUGH_PRINTINGS,
    ),
)
