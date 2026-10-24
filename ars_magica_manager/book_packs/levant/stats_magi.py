"""The eight printed stat blocks, converted from the Fourth Edition (B&S
ch06, SiS): Sharaf al-Din 'Umar, Amber the Golden, Felix, Esther,
Guillaume de Bourne, Rufus de Clary and Spiral from Secrets in Sand, and
Wardat al-Quds from Blood and Sand's chapter 6; and Luigi, Amber's cat,
bound to her as her Familiar (L14), as Transylvania's Silexa is.

Each block is written here as the book prints it, a `Fourth`, in the
Fourth Edition's own names, and one plain function, `convert`, turns it
into the StatBlock Builder.stats reads (an Adapter, though a function is
all it needs), by the Definitive Edition's appendix and L11: age +20%,
apparent age as printed; Characteristics and Arts unchanged; each Virtue
and Flaw at the catalog's tier under its Fifth Edition name (a Flaw
with both tiers in the catalog is Major at -2 or worse, Minor at -1),
those with no Fifth Edition counterpart dropped; Abilities kept at their
scores and renamed, a dropped Ability's experience moved to its
replacement (Scribe to Artes Liberales at the best Scribe score, since a
language now carries its letters; Disputatio and Divination: Astrology
to Artes Liberales, Forgery to Guile, Read Lips to Awareness, Climb to
Athletics, the weapon-and-shield Abilities into the one weapon Ability;
Certamen, the Affinity Abilities and Verditius Magic dropped, as they are
Virtues or gone); spells at the catalog's level and Art, and each one
the catalog lacks swapped for a catalog spell of the same Technique,
Form and level (L17; Eyes of the Past and of the Future, impossible now,
for same-level Intellego spells); Twilight Points / 3 as Warping;
Confidence 4 as 2 (5 points) and 3 as 1 (3 points); no rebalancing, and
no House Virtue added beyond what a printed Virtue or Ability becomes.
Each sheet's biography lists what the conversion did to it, with the
block's equipment, sigils and Twilight scars. Longevity rituals are
worked out again at a Definitive Edition Lab Total from the converted
scores. 'Umar's spells are the catalog's Hermetic ones; his own Islamic
spell, The Wrath of Allah, keeps its Islamic Range, Duration and Target
(L12), and SiS's sample, Convocation of the Faithful, is the saga's own
spell, as no printed magus knows it.

Wardat (L13 as revised): a maga of Ex Miscellanea in the Hermetic
Sahirs (traditions ["trad_hermetic_sahirs"]), with its package (Sihr,
a Minor Magical Focus in jinn, Twilight Prone), Sihr 6 on the Art
table, and no Arts, as printed; her two jinn, al-Manqa'i and Sharif,
are bound beings of the tradition's "Bound jinni" bond, linked to their
Bestiary entries (Q1), and her other Familiarities are in her
biography, linked.

The magi are major_covenants.py's records, magi["umar"], ["amber"],
["felix"], ["esther"], ["guillaume"], ["rufus"], ["spiral"] and
["wardat"]; Luigi is bestiary.py's creatures["luigi"]. A record not yet
made is skipped."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ... import storage
from ...models import (
    Ability,
    BondPower,
    BoundBeing,
    Familiar,
    Possession,
    ScoredTrait,
    Spell,
)
from ...rules import creation_access as access
from ...rules import lab
from ...rules.xp import ability_xp, score_from_xp
from ..builder import (
    StatBlock,
    _catalog_spells,
    _spell_key,
    _virtue_flaw,
    characteristics,
)

if TYPE_CHECKING:
    from ...models import Character
    from . import Levant

SIS = "SiS"
SAHIRS = "trad_hermetic_sahirs"
AGE_FACTOR = 1.2
#: The Fourth Edition's Confidence and the Definitive Edition's (Score,
#: Points) for it (L11).
CONFIDENCE = {4: (2, 5), 3: (1, 3), 2: (1, 3), 1: (1, 3), 0: (0, 0)}

#: A Virtue or Flaw as the book prints it: (name, points) or (name,
#: points, detail), the detail being what the book puts in brackets.
Printed = tuple[Any, ...]


@dataclass(frozen=True)
class Fourth:
    """A Fourth Edition stat block as the book prints it, in its names."""

    age: int
    apparent: int | None
    characteristics: dict[str, int]
    confidence: int
    twilight: int
    decrepitude: int
    virtues: Sequence[Printed]
    abilities: Sequence[tuple[str, int, str]]
    arts: dict[str, int]
    spells: Sequence[tuple[str, str, int]]
    traits: dict[str, int]
    reputations: dict[str, int] = field(default_factory=dict)
    size: int = 0
    notes: str = ""
    #: Virtues the Definitive Edition gives with what the block prints
    #: (the tradition's package), before the printed ones.
    granted: Sequence[str | tuple[str, dict[str, str]]] = ()
    traditions: Sequence[str] = ()


# -- the conversion tables --

#: A printed Virtue or Flaw's Fifth Edition name, where it was renamed.
RENAMED: dict[str, str] = {
    "Elementalist": "Elemental Magic",
    "Jack of All Trades": "Jack-of-All-Trades",
    "Well Traveled": "Well-Traveled",
    "Obligations": "Dutybound",
    "Obsession": "Obsessed",
    "Driving Goal": "Driven",
    "Veteran": "Warrior",
    "Common Fear": "Fear",
    "Terrors": "Fear",
    "Secret Vis Source": "Personal Vis Source",
    "Lack of Control": "Unpredictable Magic",
    "Well Known": "Famous",
    "Silent Magic": "Quiet Magic",
    "Diabolic upbringing": "Diabolic Past",
    "Plagued by Jinni": "Plagued by Supernatural Entity",
    "Knack with Certamen": "Minor Magical Focus",
    "Quaesitor": "Hermetic Prestige",
    "Mage-Smith": "Verditius Magic",
    "Magical Affinity": "Affinity with {art}",
    "Affinity": "Affinity with {art}",
    "Felines": "Special Circumstances",
    "Cyclic Magic (+)": "Cyclic Magic (Positive)",
    "Cyclic Magic (-)": "Cyclic Magic (Negative)",
    "Feeble Communication": "Poor {characteristic}",
}
#: The parameter a renamed entry takes from the printed detail.
PARAMETER = {
    "Minor Magical Focus": "focus",
    "Affinity with {art}": "art",
    "Special Circumstances": "circumstance",
    "Social Contacts": "group",
    "Cyclic Magic (Positive)": "cycle",
    "Cyclic Magic (Negative)": "cycle",
    "Poor {characteristic}": "characteristic",
}
#: Printed Virtues and Flaws with no Fifth Edition counterpart, and why.
DROPPED: dict[str, str] = {
    "No Sigil": "the voting sigil is a token, not a Flaw now",
    "Twilight Points": "its points are in the Warping",
    "Old": "the age itself carries it",
    "Decrepit": "the Decrepitude score carries it",
    "Read Lips": "no Fifth Edition Virtue; the Ability went to Awareness",
    "Outsider Trained in Order": "a sahir joins by the tradition, in Ex Miscellanea",
    "Visual Eidetic Memory": "not in the catalog",
    "Weak Parma Magica": "the catalog's Flawed Parma Magica is weak against "
    "one Form, not when unaware",
    "Bad Reputation": "kept as the Reputation it printed",
    "Follower of Verditius": "folded into Verditius Magic",
}
#: Flaws the catalog has at both tiers.
TWO_TIERS = {
    "Obsessed",
    "Driven",
    "Vow",
    "Overconfident",
    "Oversensitive",
    "Weakness",
    "Wrathful",
    "Proud",
}
#: How many copies a printed entry becomes (ArM4's -4 Feeble Communication
#: is two steps of Poor Communication, to -5).
COPIES = {"Feeble Communication": 2}

#: A printed Ability's Fifth Edition name.
ABILITIES: dict[str, str] = {
    "Brawling": "Brawl",
    "Hermes Lore": "Organization Lore: Order of Hermes",
    "Hermetic Law": "Code of Hermes",
    "Legend Lore": "Magic Lore",
    "Occult Lore": "Infernal Lore",
    "Levant Lore": "Area Lore: Levant Tribunal",
    "Longshaft Weapon": "Great Weapon",
    "Shield and Weapon": "Single Weapon",
    "Weapon and Shield": "Single Weapon",
    "Climb": "Athletics",
    "Rabbinical Law": "Rabbinic Law",
    "Civil & Canon Law": "Civil and Canon Law",
    "Disputatio": "Artes Liberales",
    "Divination: Astrology": "Artes Liberales",
    "Forgery": "Guile",
    "Read Lips": "Awareness",
    "Craft: Armory": "Craft: Armorer",
    "Craft: Clothiery": "Craft: Clothier",
    "Craft: Jewelry-making": "Craft: Jeweler",
    "Craft: Weapon-smithing": "Craft: Weaponsmith",
}
#: Printed Abilities that are one skill with their replacement, so the
#: better score stands rather than the two adding up.
SAME_SKILL = {"Shield and Weapon", "Weapon and Shield"}
#: Printed Abilities the Definitive Edition has no place for.
NO_ABILITY = {"Certamen", "Verditius Magic"}

#: Printed spells the catalog has under another name.
SPELL_RENAMES: dict[str, str] = {
    "Parting the Waves": "Parting of the Waves",
    "The Seven-League Stride": "Seven-League Stride",
    "Circle of Encompassing Flames": "Circle of Encompassing Flame",
    "Confusion of the Numbed Will": "Confusion of the Numb Will",
    "Transformation of the Ravenous Beast to a Torpid Toad": (
        "Transformation Of The Ravenous Beast To The Torpid Toad"
    ),
    "Ear for the Distant Voice": "The Ear for Distant Voices",
    "The Demon's Eternal Oblivion": "Demon's Eternal Oblivion",
    "Sense the Lingering Magic": "Sense of the Lingering Magic",
    "Mirror of Opposition (Corpus)": "Mirror of Opposition (Form)",
    "Mirror of Opposition (Mentem)": "Mirror of Opposition (Form)",
    "Mirror of Opposition (Vim)": "Mirror of Opposition (Form)",
    "Wizard's Boost (Vim)": "Wizard's Boost (Form)",
    "Wizard's Boost (Mentem)": "Wizard's Boost (Form)",
}
#: Each spell the catalog lacks, and the catalog spell of the same
#: Technique, Form and level it becomes.
SWAPS: dict[str, str] = {
    # ArM4 core spells
    "Breaking the Perpetual Drought": "Wizard's Flood",
    "Full Health of Beast and Bird": "Flight Perfected",
    "Subtle Shift of the Heart": "Distraction of the Magpie",
    "Circle of the Faerie Stone": "Silvery Scales of the Knight",
    "Heat of Hell's Impending Doom": "Rainbow Bridge",
    "Emotion of Reversed Intentions": "My Old and Dear Friend",
    # impossible now: Hermetic magic cannot see the past or the future
    "Eyes of the Past": "The Ear for Distant Voices",
    "Eyes of the Future": "Sight of the Blossom, Ears of the Oak",
    # Wizard's Grimoire Revised
    "Change the River's Path": "Chaos of the Angry Waves",
    "Fulgurous Orb": "Catapult of the Mighty Winds",
    "The Travelling Thistledown": "Embracing the Downy Arms of the Nephelae",
    "Call Aeolus' Servants": "Movement Within the Sirocco",
    "Prison of the Zephyrs": "Ward Against the Sirocco",
    "Breath of Vulcan": "Self Immolation",
    "Curse of the Attraction of the Fire": "Unified Flame",
    "Blessing of Antaeus' Fortitude": "Stance of the Patient Tree",
    "Gift of the Buoyant Gosling": "Cloak of Fins and Scales",
    "Humility of the Vanquished Knight": "My Old and Dear Friend",
    "Weighing the Turncoat's Silver": "Frosty Breath of the Spoken Lie",
    "Mastering the Stolid Mundane": "Lay Your Burdens on Me",
    "Beguile the Normal Mind": "Enchantment of my Lover's Eye",
    "Sense the Magic Root": "Intuition of the Forest",
    "Wizard's Sleeve of Practical Tools": "Breath of the Glassworker",
    "Origin of the Ancient Object": "Eyes of the Treacherous Terrain",
    "Gift of the Hero's Strength": "High Tree or Small Boulder",
    "Mighty Fling of the Menacing Knight": "Jump of the Lynx",
    "Enlarging the Distant Image": "Aura of the Ennobled Presence",
    "Eyes of the Serpent": "Rise of the Feathery Body",
    "Eyes of Flame": "Circle of Encompassing Flame",
    "Pain of the Wizard's Gaze": "Bane of the Decrepit Body",
    "Spectacle of Abject Terror": "Convince a Man he has an Enemy",
    "Spell Analysis": "Impression of the Faded Sigil",
    "Sense the Shadows of the Spheres": "Sense the Hour",
    "Wizard's Focus": "Reveal the Lurking Watchers",
    "Glimpse Through the Mystic Veil": "Piercing the Faerie Veil",
    "Reveal the Gift": "See the Light of Magic",
    "Warping the Magical Veil": "Clear Breath of the Consummate Liar",
    "Hammer of Thaumaturgical Shattering": "Snipping the Thread of Power",
    "Wizard's Wait": "The Patient Spell",
}
#: Swaps made otherwise for one magus: Felix already knows The Ear for
#: Distant Voices, and Guillaume's Curse is the book's level 30, not
#: 'Umar's 35.
SECOND_SWAPS = {
    ("felix", "Eyes of the Past"): "Frosty Breath of the Spoken Lie",
    ("guillaume", "Curse of the Attraction of the Fire"): "Petite Phoenix",
}
#: The magi's own spells, which no catalog prints: the book's Range,
#: Duration and Target, page and source, and a description.
OWN_SPELLS: dict[str, tuple[str, str, str, str, str, str]] = {
    "The Wrath of Allah": (
        "Voice",
        "Shahada",
        "Group",
        "B&S",
        "65",
        "An Islamic spell (Aimed 0). A stream of pebble-sized balls of "
        "burning rock strikes each of a group for +30 damage; anyone struck "
        "who fails a Strength stress roll against 12 falls and is "
        "flung 5 - Strength paces. Jinn, half made of magical fire, take only "
        "+20. At Voice the caster needs only name or describe the group, "
        "but an unseen target is hit on 9+, not 3+. (The book's rationale: "
        "moving stone very fast and accurately, ReTe(Ig) 30, a Creo requisite "
        "to make the stones, the Islamic Range, Duration and Target, and "
        "Group: ReTe(Cr, Ig) 35.)",
    ),
    "Shape of the Barnyard Creeper": (
        "Touch",
        "Sun",
        "Individual",
        SIS,
        "7",
        "With a cat skin laid over the target, turns caster or another into "
        "a cat, who may change back at will, ending the spell. Spell focus a "
        "cat's claw (+2). DE: Base 10 (a person into an animal), +1 Touch, "
        "+2 Sun = 25, as printed.",
    ),
    "Shape of the Spotted Stalker": (
        "Touch",
        "Sun",
        "Individual",
        SIS,
        "7",
        "As Shape of the Barnyard Creeper, but with a leopard skin, into a "
        "leopard. Spell focus a leopard's tooth (+4). DE: Base 10, +1 Touch, "
        "+2 Sun = 25, as printed.",
    ),
    "From Cat to Cat": (
        "Touch",
        "Sun",
        "Individual",
        SIS,
        "7",
        "Turns a cat into a leopard, which may turn back at will; Amber "
        "mostly casts it on Luigi. Spell focus a leopard's tooth (+4). DE: "
        "Base 5 (an animal into another), +1 Touch, +2 Sun = 20, as printed.",
    ),
}
#: SiS's sample Islamic spell, which no printed magus knows.
CONVOCATION = Spell(
    id="spell_convocation_of_the_faithful",
    name="Convocation of the Faithful",
    technique="Rego",
    form="Mentem",
    level=35,
    range="Touch",
    duration="Salat",
    target="Minaret",
    source=SIS,
    page="2",
    description=(
        "An Islamic spell, cast at a minaret. Everyone within the area its "
        "call to prayer reaches feels a growing, unexplained need to go to "
        "it. A Muslim shrugs it off on Int + Concentration of 12+, anyone "
        "else on 9+ (traits such as Pious, and Strong-Willed, modify the "
        "roll); success only holds the urge off for an hour, when the roll "
        "is made again. Those who fail go as soon as they sensibly can; a "
        "botch sends them running heedless of everything. It ends at the "
        "next call to prayer. Meant for gathering a town in an emergency. "
        "With an Intellego requisite the caster can call only one kind of "
        "person, named aloud in six words at most, and only those who think "
        "they belong to it come. (The book's rationale: the urge to go to "
        "the minaret, ReMe 20, the Islamic Range, Duration and Target, "
        "Minaret +15 = ReMe 35.)"
    ),
)


# -- the conversion --


def _virtues(block: Fourth) -> tuple[list[Any], list[str]]:
    """The block's Virtues and Flaws in Fifth Edition terms, and what was
    renamed or dropped."""
    entries: list[Any] = ["The Gift", "Hermetic Magus", *block.granted]
    said: list[str] = []
    for printed in block.virtues:
        name, points, detail = (*printed, "")[:3]
        points = int(points)
        if name in DROPPED:
            said.append(f"{name} dropped ({DROPPED[name]})")
            continue
        new = RENAMED.get(name, name)
        if new in TWO_TIERS:
            new = f"{new} ({'Major' if points <= -2 else 'Minor'})"
        key = PARAMETER.get(RENAMED.get(name, name))
        entry: Any = (new, {key: detail}) if key else new
        entries.extend([entry] * COPIES.get(name, 1))
        shown = new.replace("{art}", detail).replace("{characteristic}", detail)
        line = shown if new.startswith(f"{name} (") else f"{name} as {shown}"
        if detail and not key:
            # The catalog entry takes no parameter: the detail is kept here.
            said.append(f"{shown if new == name else line}: {detail}")
        elif new != name:
            said.append(line)
    return entries, said


def _abilities(block: Fourth) -> tuple[list[tuple[str, int, str]], list[str]]:
    """The block's Abilities in Fifth Edition terms, merged where two
    became one, and what moved. Printings of one skill (Scribe in each
    language; a weapon Ability and its weapon-and-shield form) count once,
    at the best score; any other Ability moved in adds its experience."""
    same_skill = {ABILITIES[name] for name in SAME_SKILL}
    moved: dict[str, int] = {}
    best: dict[str, int] = {}
    specialty: dict[str, str] = {}
    said: list[str] = []
    for name, score, spec in block.abilities:
        if name in NO_ABILITY or name.startswith("Affinity "):
            said.append(f"{name} {score} dropped")
            continue
        if name.startswith("Scribe "):
            new, one_skill = "Artes Liberales", True
        elif name.startswith("Speak "):
            tongue = name.removeprefix("Speak ")
            new = (
                "Dead Language: Latin"
                if tongue == "Latin"
                else (f"Living Language: {tongue}")
            )
            one_skill = False
        else:
            new = ABILITIES.get(name, name)
            one_skill = name in SAME_SKILL or name in same_skill
        specialty.setdefault(new, spec)
        moved.setdefault(new, 0)
        best.setdefault(new, 0)
        if one_skill:
            best[new] = max(best[new], score)
        else:
            moved[new] += ability_xp(score)
        if new != name and not name.startswith("Speak "):
            said.append(f"{name} {score} to {new}")
    abilities = [
        (new, score_from_xp(ability_xp(best[new]) + moved[new], 5), spec)
        for new, spec in specialty.items()
    ]
    return abilities, said


def _spells(
    key: str, block: Fourth
) -> tuple[list[tuple[str, str, int | None, int]], list[str]]:
    """The block's spells as the catalog has them, each rename and swap
    named, and each spell whose catalog level or Art differs listed."""
    known: list[tuple[str, str, int | None, int]] = []
    seen: set[str] = set()
    said: list[str] = []
    changed: list[str] = []
    printings = _catalog_spells()
    for name, arts, level in block.spells:
        swap = SECOND_SWAPS.get((key, name)) or SWAPS.get(name)
        new = swap or SPELL_RENAMES.get(name, name)
        if new in seen:
            # The (Form) spells: one general spell for each printed Form.
            continue
        seen.add(new)
        if swap:
            said.append(f"{name} for {new}")
        elif new != name and not new.endswith("(Form)"):
            said.append(f"{name} as {new}")
        found = printings.get(_spell_key(new))
        if found and not swap:
            spell = next((s for s in found if s.source == "DE"), found[0])
            short = spell.technique[:2] + spell.form[:2]
            if spell.level != level or short != arts[:4]:
                now = "general" if spell.level is None else spell.level
                changed.append(f"{name} {arts} {level} to {short} {now}")
        known.append((new, arts, level, 0))
    if changed:
        said.append("At the catalog's level or Art: " + "; ".join(changed))
    return known, said


def convert(key: str, block: Fourth) -> tuple[StatBlock, int]:
    """A Fourth Edition block as a Definitive Edition StatBlock (L11),
    with the converted age; the biography lists what changed."""
    age = round(block.age * AGE_FACTOR)
    virtues, said_virtues = _virtues(block)
    abilities, said_abilities = _abilities(block)
    spells, said_spells = _spells(key, block)
    warping = block.twilight // 3
    confidence = CONFIDENCE[block.confidence]
    lines = [
        f"Converted from the Fourth Edition block by the Definitive "
        f"Edition's appendix: age {block.age} + 20% = {age}"
        + (f" (looks {block.apparent})" if block.apparent else "")
        + f"; Twilight Points {block.twilight} / 3 = Warping {warping}; "
        f"Confidence {block.confidence} = {confidence[0]} ({confidence[1]} "
        "points). Characteristics and Arts as printed; no rebalancing.",
    ]
    if said_virtues:
        lines.append("Virtues and Flaws: " + "; ".join(said_virtues) + ".")
    if said_abilities:
        lines.append("Abilities: " + "; ".join(said_abilities) + ".")
    if said_spells:
        lines.append("Spells: " + "; ".join(said_spells) + ".")
    stat: StatBlock = {
        "characteristics": dict(block.characteristics),
        "size": block.size,
        "confidence": confidence,
        "decrepitude": (block.decrepitude, 0),
        "warping": (warping, 0),
        "virtues_flaws": virtues,
        "abilities": abilities,
        "arts": dict(block.arts),
        "traits": dict(block.traits),
        "reputations": dict(block.reputations),
        "spells": spells,
        "traditions": list(block.traditions),
        "notes": "\n".join([block.notes.strip(), *lines]).strip(),
    }
    if block.apparent:
        stat["apparent_age"] = block.apparent
    return stat, age


def _arts(cr: int, in_: int, mu: int, pe: int, re: int, *forms: int) -> dict[str, int]:
    """Arts in the book's order: Techniques, then An Aq Au Co He Ig Im Me
    Te Vi."""
    names = ("Animal", "Aquam", "Auram", "Corpus", "Herbam", "Ignem")
    names += ("Imaginem", "Mentem", "Terram", "Vim")
    return {
        "Creo": cr,
        "Intellego": in_,
        "Muto": mu,
        "Perdo": pe,
        "Rego": re,
        **dict(zip(names, forms)),
    }


# -- the blocks, as printed --

UMAR = Fourth(
    age=72,
    apparent=54,
    characteristics=characteristics(3, 3, 0, 3, 0, -1, -1, -2),
    confidence=4,
    twilight=14,
    decrepitude=0,
    virtues=[
        ("Elementalist", 5),
        ("Jack of All Trades", 2),
        ("Clear Thinker", 1),
        ("Well Traveled", 1),
        ("Obligations", -2, "to the Ayyubid sultans"),
        ("Clumsy Magic", -2),
        ("Dark Secret", -1, "servant of the Ayyubids"),
        ("Vow", -1, "fealty to the Ayyubids"),
        ("The Faerie Problem", -1),
        ("Poorly-Meshed Hermetic-Islamic Magic", -1),
        ("Obsession", -1, "the counter-Crusade"),
        ("Driving Goal", -1, "rare longevity ingredients"),
    ],
    abilities=[
        ("Affinity Elements", 5, "in combat"),
        ("Awareness", 4, "ambushes"),
        ("Bargain", 4, "with nobles"),
        ("Brawling", 3, "fist"),
        ("Certamen", 3, "Ignem"),
        ("Charm", 4, "being mysterious"),
        ("Concentration", 4, "reciting"),
        ("Etiquette", 3, "nobility"),
        ("Finesse", 4, "precision"),
        ("Folk Ken", 4, "nobles"),
        ("Guile", 4, "elaborate lies"),
        ("Hermes Lore", 4, "history"),
        ("Hermetic Law", 3, "treaty law"),
        ("Hunt", 3, "laying traps"),
        ("Intrigue", 4, "long-term plans"),
        ("Islamic Law", 3, "magic"),
        ("Leadership", 4, "at Tribunal"),
        ("Legend Lore", 4, "heroes"),
        ("Levant Lore", 4, "magical sites"),
        ("Longshaft Weapon", 4, "staff"),
        ("Magic Theory", 6, "inventing items"),
        ("Parma Magica", 5, "Mentem"),
        ("Penetration", 5, "Terram"),
        ("Ride", 3, "speed"),
        ("Scribe Arabic", 4, "fine hand"),
        ("Scribe Latin", 4, "neatness"),
        ("Speak Arabic", 5, "eloquence"),
        ("Speak French", 3, "eavesdropping"),
        ("Speak Latin", 4, "eloquence"),
        ("Survival", 3, "desert"),
        ("Theology: Islam", 3, "magic"),
    ],
    arts=_arts(15, 11, 9, 7, 21, 8, 14, 13, 16, 10, 16, 3, 6, 15, 10),
    spells=[
        ("The Earth's Carbuncle", "ReTe", 15),
        ("Crest of the Earth Wave", "ReTe", 25),
        ("Earth Shock", "ReTe", 25),
        ("The Earth Split Asunder", "ReTe", 30),
        ("Wall of Protecting Stone", "CrTe", 30),
        ("Circling Winds of Protection", "ReAu", 15),
        ("Charge of the Angry Winds", "CrAu", 15),
        ("The Wrath of Allah", "ReTe(Cr,Ig)", 35),
        ("Breaking the Perpetual Drought", "CrAq", 35),
        ("Parting the Waves", "ReAq", 35),
        ("Pull of the Watery Grave", "ReAq", 25),
        ("Clouds of Rain and Thunder", "CrAu", 20),
        ("The Incantation of Lightning", "CrAu", 35),
        ("Wings of the Soaring Wind", "ReAu", 20),
        ("Gathering of the Stormy Might", "ReAu", 30),
        ("Pull of the Skybound Winds", "ReAu", 30),
        ("The Chirurgeon's Healing Touch", "CrCo", 25),
        ("Sight of the True Form", "InCo", 25),
        ("The Seven-League Stride", "ReCo", 35),
        ("Arc of Fiery Ribbons", "CrIg", 25),
        ("Ball of Abysmal Flame", "CrIg", 35),
        ("Circle of Encompassing Flames", "CrIg", 35),
        ("Burst of the Sweeping Flames", "ReIg", 20),
        ("Ward Against Heat and Flames", "ReIg", 30),
        ("Conjuring the Mystic Tower", "CrTe", 35),
        ("Creeping Chasm", "ReTe", 30),
        ("Change the River's Path", "ReAq", 30),
        ("Fulgurous Orb", "CrAu", 35),
        ("The Travelling Thistledown", "ReAu", 25),
        ("Call Aeolus' Servants", "ReAu", 25),
        ("Prison of the Zephyrs", "ReAu", 25),
        ("Breath of Vulcan", "CrIg(Au,Te)", 30),
        ("Curse of the Attraction of the Fire", "ReIg", 35),
        ("Gift of the Bear's Fortitude", "MuCo(An)", 25),
        ("Voice of the Lake", "InAq", 25),
        ("Eyes of the Bat", "InAu", 25),
        ("Heat of Hell's Impending Doom", "MuAu(Re,Ig)", 30),
        ("Stone Tell of the Mind that Sits", "InTe", 35),
        ("Sense the Feet that Tread the Earth", "InTe", 30),
    ],
    traits={"Brave": 3, "Calm": 3, "Careful": 3, "Pious": 3, "Wild": 1},
    reputations={
        "Trustworthy (Ayyubid sultans)": 3,
        "Threat to peace (quaesitores)": 3,
        "Untrustworthy (Hermetic magi)": 2,
    },
    notes=(
        "Every spell he knows the book writes with Islamic Ranges, Durations "
        "and Targets; here they are the catalog's Hermetic ones, which his "
        "Poorly-Meshed Hermetic-Islamic Magic lets a troupe cast the Islamic "
        "way (SiS gives both levels). His own The Wrath of Allah keeps its "
        "Islamic terms.\n"
        "Equipment: his quarterstaff, a talisman attuned to repelling (+2), "
        "to hurling missiles (+3) and to moving (+4) and destroying (+4) "
        "things at a distance, holding two effects of six uses a day: tapped "
        "twice on the ground it turns aside wooden and metal weapons that "
        "come within reach (ReHe(Te), the book's level 35 in Islamic terms), "
        "and tapped three times it carries him as the Seven-League Stride "
        "(ReCo 30). A plain brass ring is his voting sigil; a shadow crosses "
        "his face whenever he casts. His last longevity ritual needed four "
        "rare ingredients: his first milk tooth, dust from where he cast his "
        "first spell, chips of his parents' bones and stone from the ruins "
        "of the house he grew up in.\n"
        "Afflictions as printed: visibly aging, sore knees. Twilight has "
        "cost him his Gentle Gift (now plainly Gifted), made his magic "
        "clumsy, and once added to his Penetration."
    ),
)

AMBER = Fourth(
    age=54,
    apparent=37,
    size=-1,
    characteristics=characteristics(3, 2, -2, 0, 0, 0, 0, 0),
    confidence=3,
    twilight=5,
    decrepitude=0,
    virtues=[
        ("Knack with Certamen", 4, "certamen"),
        ("Piercing Gaze", 2),
        ("Mentor", 2, "Catullus of Tremere"),
        ("Lightning Reflexes", 2),
        ("Strong-Willed", 1),
        ("Felines", 1, "magic on cats and other felines"),
        ("Small Frame", -3),
        ("Curse of Venus", -2),
        ("No Sigil", -1),
        ("Twilight Points", -1),
        ("Oversensitive", -1, "being controlled"),
        ("Disfigured", -1, "golden skin"),
        ("Bad Reputation", -1, "undisciplined, in House Tremere"),
    ],
    abilities=[
        ("Affinity Felines", 4, "domestic cats"),
        ("Animal Handling", 3, "cats"),
        ("Awareness", 2, "sounds"),
        ("Brawling", 4, "in cat form"),
        ("Certamen", 4, "Animal"),
        ("Charm", 2, "seduction"),
        ("Concentration", 3, "on watch"),
        ("Finesse", 3, "grace"),
        ("Folk Ken", 3, "magi"),
        ("Guile", 3, "tight corners"),
        ("Hermes Lore", 3, "politics"),
        ("Hermetic Law", 2, "loopholes"),
        ("Hunt", 3, "stalking"),
        ("Intrigue", 3, "gossip"),
        ("Legend Lore", 2, "beasts"),
        ("Levant Lore", 2, "personalities"),
        ("Magic Theory", 5, "inventing spells"),
        ("Parma Magica", 4, "Mentem"),
        ("Penetration", 3, "Corpus"),
        ("Scribe Arabic", 2, "reading"),
        ("Scribe Latin", 3, "illumination"),
        ("Speak Arabic", 2, "Syrian"),
        ("Speak Italian", 4, "Florentine"),
        ("Speak Latin", 5, "Hermetic usage"),
        ("Stealth", 6, "hunting"),
        ("Swim", 2, "rough water"),
        ("Theology: Islam", 1, "women"),
    ],
    arts=_arts(11, 14, 15, 10, 11, 18, 7, 9, 17, 8, 11, 8, 12, 7, 9),
    spells=[
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Thoughts Within Babble", "InMe", 25),
        ("Opening the Tome of the Animal's Mind", "InAn", 25),
        ("Viper's Gaze", "ReAn", 15),
        ("Panic of the Trembling Heart", "CrMe", 15),
        ("Trust of Childlike Faith", "PeMe", 10),
        ("Calm the Motion of the Heart", "PeMe", 15),
        ("Confusion of the Numbed Will", "ReMe", 15),
        ("Full Health of Beast and Bird", "CrAn", 25),
        ("Soothe Pains of the Beast", "CrAn", 20),
        ("Weaver's Trap of Webs", "CrAn", 20),
        ("Hunter's Sense", "InAn", 30),
        ("The Beast Remade", "MuAn(Co)", 25),
        ("Cripple the Howling Wolf", "PeAn", 20),
        ("Panic of the Elephant's Mouse", "ReAn", 15),
        ("The Gentle Beast", "ReAn", 20),
        ("Circle of Beast Warding", "ReAn", 25),
        ("Commanding the Harnessed Beast", "ReAn", 30),
        ("The Chirurgeon's Healing Touch", "CrCo", 20),
        ("Sight of the True Form", "InCo", 25),
        ("Whispers Through the Black Gate", "InCo(Me)", 15),
        ("The Inexorable Search", "InCo", 20),
        ("Shape of the Woodland Prowler", "MuCo(An)", 25),
        ("Strings of the Unwilling Marionette", "ReCo", 25),
        ("Gift of the Bear's Fortitude", "MuCo(An)", 25),
        ("Cloak of Black Feathers", "MuCo(An,Au)", 30),
        ("Steed of Vengeance", "MuAn", 30),
        ("Transformation of the Ravenous Beast to a Torpid Toad", "MuAn", 30),
        ("Curse of Circe", "MuCo(An)", 35),
        ("Mind of the Beast", "MuMe(An)", 30),
        ("Blessing of Antaeus' Fortitude", "MuCo", 35),
        ("Gift of the Buoyant Gosling", "MuCo", 35),
        ("Humility of the Vanquished Knight", "MuMe", 20),
        ("Preternatural Growth and Shrinking", "MuCo", 20),
        ("Shape of the Barnyard Creeper", "MuCo(An)", 25),
        ("Shape of the Spotted Stalker", "MuCo(An)", 25),
        ("From Cat to Cat", "MuAn", 20),
    ],
    traits={
        "Curious": 4,
        "Independent": 3,
        "Cat": 3,
        "Cruel to enemies": 1,
        "Brave": 1,
    },
    reputations={
        "Undisciplined (House Tremere)": 2,
        "Threat to peace (quaesitores)": 2,
    },
    notes=(
        "Her voting sigil, a ruby bracelet, is in her parens Catullus's "
        "keeping; her eyes flash gold when she casts. She carries props for "
        "changing shape. A reagent mixed wrongly in her apprenticeship blew "
        "up, threw her briefly into Twilight and left her skin, hair and "
        "eyes golden; binding Luigi slit her pupils like a cat's. She has "
        "invented and mastered three spells of her own, the cat and leopard "
        "shapes and From Cat to Cat.\n"
        "Her Virtues outweigh her Flaws, as printed; the pack does not trim "
        "them (L11). The familiar bond gives her True Friend and Loyal "
        "(Luigi) +3."
    ),
)

FELIX = Fourth(
    age=48,
    apparent=45,
    characteristics=characteristics(4, 4, 0, 0, 2, 3, 0, -2),
    confidence=3,
    twilight=1,
    decrepitude=0,
    virtues=[
        ("Cautious Sorcerer", 2),
        ("Clear Thinker", 1),
        ("Quaesitor", 1),
        ("Veteran", 1),
        ("Common Sense", 1),
        ("Social Contacts", 1, "Kabbalists"),
        ("Premonitions", 1),
        ("Tough", 1),
        ("Well Traveled", 1),
        ("Old", -3),
        ("Painful Magic", -3),
        ("Lame", -2),
        ("Common Fear", -2, "fire"),
    ],
    abilities=[
        ("Animal Handling", 2, "horses"),
        ("Awareness", 2, "ambushes"),
        ("Bargain", 2, "military supplies"),
        ("Brawling", 2, "fist and kick"),
        ("Carouse", 2, "drinking songs"),
        ("Charm", 2, "first impressions"),
        ("Concentration", 2, "on guard"),
        ("Etiquette", 2, "magi"),
        ("Folk Ken", 2, "magi"),
        ("Guile", 2, "quick lies"),
        ("Hermes Lore", 2, "House Criamon"),
        ("Hermetic Law", 3, "hedge wizards"),
        ("Hunt", 2, "snares"),
        ("Intrigue", 2, "subtle plots"),
        ("Judaic Lore", 2, "famous rabbis"),
        ("Levant Lore", 2, "the Holy Land"),
        ("Magic Theory", 4, "potions"),
        ("Parma Magica", 2, "Mentem"),
        ("Premonitions", 2, "ambushes"),
        ("Rabbinical Law", 2, "magic"),
        ("Scribe Hebrew", 2, "neatness"),
        ("Scribe Latin", 3, "neatness"),
        ("Shield and Weapon", 3, "mace and round shield"),
        ("Speak Arabic", 4, "soldiers' talk"),
        ("Speak French", 2, "the Latin states"),
        ("Speak Latin", 5, "Hermetic usage"),
        ("Theology: Judaism", 2, "rituals"),
    ],
    arts=_arts(6, 11, 5, 0, 3, 0, 0, 0, 6, 0, 0, 12, 11, 0, 2),
    spells=[
        ("Eyes of the Past", "InIm", 20),
        ("Ear for the Distant Voice", "InIm", 20),
        ("Summoning the Distant Image", "InIm", 25),
        ("Discern Images of Truth and Falsehood", "InIm", 30),
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Thoughts Within Babble", "InMe", 25),
        ("The Chirurgeon's Healing Touch", "CrCo", 20),
        ("Whispers Through the Black Gate", "InCo(Me)", 15),
        ("The Inexorable Search", "InCo", 20),
        ("Lifting the Dangling Puppet", "ReCo", 15),
        ("Panic of the Trembling Heart", "CrMe", 15),
        ("Emotion of Reversed Intentions", "MuMe", 20),
        ("Trust of Childlike Faith", "PeMe", 10),
        ("Aura of Rightful Authority", "ReMe", 20),
    ],
    traits={"Sensible": 3, "Diligent": 3, "Fair": 3, "Brave": 2, "Honest": 1},
    reputations={"Fair (Order of Hermes)": 3},
    notes=(
        "Equipment: his gold sigil ring, bearing House Guernicus's sign, and "
        "a walking staff. His magic hurts him to cast, which is his wizard's "
        "sigil as well as his Flaw. Tau of Flambeau made his longevity "
        "ritual. Afflictions as printed: stiff joints, visible aging, "
        "hearing going."
    ),
)

ESTHER = Fourth(
    age=43,
    apparent=39,
    characteristics=characteristics(3, 0, 3, 0, -3, 0, 0, -1),
    confidence=3,
    twilight=3,
    decrepitude=0,
    virtues=[
        ("Jack of All Trades", 2),
        ("Intuition", 2),
        ("Mage-Smith", 2),
        ("Inventive Genius", 1),
        ("Social Contacts", 1, "merchants"),
        ("Well Traveled", 1),
        ("Secret Vis Source", 1, "Terram"),
        ("Weak Parma Magica", -3, "when unaware"),
        ("Noncombatant", -2),
        ("Enemies", -2, "the magi of al-Arama"),
        ("Follower of Verditius", -1),
        ("Driving Goal", -1, "wealth"),
        ("Dark Secret", -1, "selling magic items to mundanes"),
    ],
    abilities=[
        ("Awareness", 2, "towns"),
        ("Bargain", 4, "magic items"),
        ("Carouse", 2, "staying sober"),
        ("Charm", 3, "asking favours"),
        ("Concentration", 3, "long stretches"),
        ("Craft: Armory", 2, "chain mail"),
        ("Craft: Clothiery", 4, "cloaks"),
        ("Craft: Jewelry-making", 3, "rings"),
        ("Craft: Weapon-smithing", 2, "swords"),
        ("Etiquette", 2, "merchants"),
        ("Finesse", 2, "precision"),
        ("Folk Ken", 3, "merchants"),
        ("Guile", 3, "selling"),
        ("Forgery", 3, "letters"),
        ("Hermes Lore", 2, "famous magic items"),
        ("Hermetic Law", 1, "magic items"),
        ("Intrigue", 3, "trade"),
        ("Legend Lore", 1, "famous magic items"),
        ("Levant Lore", 3, "merchants' quarters"),
        ("Magic Theory", 7, "items"),
        ("Parma Magica", 3, "Vim"),
        ("Penetration", 2, "Mentem"),
        ("Scribe Latin", 2, "lab texts"),
        ("Speak Arabic", 2, "merchants"),
        ("Speak English", 4, "colourful phrases"),
        ("Speak Latin", 5, "nuances"),
        ("Verditius Magic", 5, "Vim"),
    ],
    arts=_arts(10, 11, 10, 10, 10, 5, 5, 5, 10, 7, 5, 9, 10, 10, 11),
    spells=[
        ("Gather the Essence of the Beast", "MuVi", 15),
        ("Shroud Magic", "MuVi", 25),
        ("Eyes of the Eons", "InTe", 10),
        ("The Miner's Keen Eye", "InTe", 20),
        ("Subtle Shift of the Heart", "MuMe", 10),
        ("Emotion of Reversed Intentions", "MuMe", 20),
        ("Posing the Silent Question", "InMe", 20),
        ("Whispers Through the Black Gate", "InCo(Me)", 15),
        ("Edge of the Razor", "MuTe", 5),
        ("Sight of the Transparent Motive", "InMe", 10),
        ("Weighing the Turncoat's Silver", "InMe", 20),
        ("Disenchant", "PeVi", 20),
        ("Masking the Odor of Magic", "PeVi", 20),
        ("Thoughts Within Babble", "InMe", 25),
        ("The Gift of Vigor", "ReCo", 20),
        ("Aura of Rightful Authority", "ReMe", 20),
        ("Mastering the Stolid Mundane", "ReMe", 20),
        ("Wall of Protecting Stone", "CrTe", 25),
        ("Circle of the Faerie Stone", "CrTe(Vi)", 30),
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Sense the Magic Root", "InHe(Vi)", 10),
        ("Eyes of the Future", "InIm", 30),
        ("Beguile the Normal Mind", "ReMe", 20),
        ("Wizard's Sleeve of Practical Tools", "CrTe", 15),
        ("Origin of the Ancient Object", "InTe", 15),
        ("Stone Tell of the Mind that Sits", "InTe", 30),
        ("Watching Ward", "ReVi", 30),
    ],
    traits={
        "Avaricious": 3,
        "Professional": 3,
        "Friendly": 2,
        "Subtle": 2,
        "Mercenary": 2,
    },
    reputations={"Professional (local merchants)": 1},
    notes=(
        "Equipment: tools and spell foci; her sigil, a gold circlet (a "
        "faint tension in the air marks her casting); and a cloak that, "
        "while its hood is up, keeps its wearer unseen and unheard even on "
        "the move, without limit of uses (the book's PeIm 5; the nearest "
        "catalog effect is the Veil of Invisibility, PeIm 20, with silence "
        "added). Affliction as printed: slowing reactions."
    ),
)

GUILLAUME = Fourth(
    age=43,
    apparent=39,
    size=1,
    characteristics=characteristics(2, 1, -2, -1, 3, 3, 1, 1),
    confidence=3,
    twilight=5,
    decrepitude=0,
    virtues=[
        ("Magical Affinity", 3, "ignem"),
        ("Large", 3),
        ("Lightning Reflexes", 2),
        ("Enduring Constitution", 1),
        ("Fury", -3, "when wounded"),
        ("Overconfident", -2),
        ("Blatant Gift", -1),
        ("Loose Magic", -1),
        ("Obsessed", -1, "the Crusade"),
        ("Disfigured", -1, "a scar"),
    ],
    abilities=[
        ("Affinity Ignem", 5, "Creo"),
        ("Athletics", 2, "stamina"),
        ("Awareness", 3, "ambushes"),
        ("Brawling", 3, "fist and kick"),
        ("Climb", 2, "cliffs"),
        ("Concentration", 2, "ignoring pain"),
        ("Hermes Lore", 2, "history"),
        ("Hermetic Law", 1, "mundane interference"),
        ("Hunt", 3, "desert"),
        ("Leadership", 2, "grogs"),
        ("Legend Lore", 2, "jinn"),
        ("Levant Lore", 3, "politics"),
        ("Magic Theory", 4, "potions"),
        ("Parma Magica", 4, "Ignem"),
        ("Scribe Latin", 2, "speed"),
        ("Single Weapon", 5, "long sword"),
        ("Shield and Weapon", 5, "long sword and shield"),
        ("Speak Arabic", 2, "the Holy Land"),
        ("Speak French", 4, "Norman"),
        ("Speak Latin", 5, "Hermetic usage"),
        ("Stealth", 3, "ambushing"),
        ("Survival", 3, "desert"),
        ("Swim", 3, "rough water"),
    ],
    arts=_arts(12, 5, 8, 10, 5, 5, 5, 5, 12, 5, 19, 5, 7, 5, 5),
    spells=[
        ("Ball of Abysmal Flame", "CrIg", 35),
        ("Arc of Fiery Ribbons", "CrIg", 25),
        ("Pilum of Fire", "CrIg", 20),
        ("Blade of the Virulent Flame", "CrIg", 20),
        ("Prison of Flames", "MuIg", 15),
        ("Well Without Light", "PeIg", 30),
        ("Tremulous Vault of the Torch's Flame", "ReIg", 5),
        ("Words of the Flickering Flame", "InIg", 25),
        ("Leap of the Fire", "ReIg", 20),
        ("Burst of the Sweeping Flames", "ReIg", 25),
        ("Ward Against Heat and Flames", "ReIg", 25),
        ("The Chirurgeon's Healing Touch", "CrCo", 20),
        ("Panic of the Elephant's Mouse", "ReAn", 15),
        ("Whispers Through the Black Gate", "InCo(Me)", 15),
        ("Wizard's Sidestep", "ReIm", 10),
        ("Panic of the Trembling Heart", "CrMe", 15),
        ("Gift of the Hero's Strength", "MuCo(Cr)", 20),
        ("Mighty Fling of the Menacing Knight", "ReCo", 20),
        ("Curse of the Attraction of the Fire", "ReIg", 30),
        ("Enlarging the Distant Image", "MuIm", 10),
        ("The Crystal Dart", "MuTe(Re)", 10),
        ("Eyes of the Serpent", "ReCo", 10),
        ("Cripple the Howling Wolf", "PeAn", 20),
        ("Eyes of Flame", "CrIg", 35),
        ("The Severed Limb Made Whole", "CrCo", 30),
        ("Preternatural Growth and Shrinking", "MuCo", 20),
    ],
    traits={"Overconfident": 3, "Pious": 3, "Brave": 3, "Hot-tempered": 2},
    reputations={
        "Great warrior (Crusader magi)": 2,
        "Threat to peace (quaesitores)": 2,
    },
    notes=(
        "Equipment: long sword, kite shield (a Heater Shield), reinforced "
        "leather hauberk (Metal Reinforced Leather); his longsword is his "
        "sigil, and sparks leap from his fingertips when he casts. Twilight "
        "once deepened his grasp of Ignem: he may write on it up to two "
        "thirds of his score."
    ),
)

RUFUS = Fourth(
    age=45,
    apparent=36,
    characteristics=characteristics(3, 2, 2, 1, -2, -1, -1, -1),
    confidence=3,
    twilight=2,
    decrepitude=1,
    virtues=[
        ("Silent Magic", 5),
        ("Subtle Magic", 2),
        ("Inspirational", 1),
        ("Read Lips", 1),
        ("Strong-Willed", 1),
        ("Decrepit", -2, "childhood abuse"),
        ("Diabolic upbringing", -2),
        ("Terrors", -2, "demons"),
        ("Driving Goal", -1, "magical power"),
        ("Obsessed", -1, "the Crusade"),
        ("Dark Secret", -1, "son of diabolists"),
        ("Fragile Constitution", -1),
    ],
    abilities=[
        ("Awareness", 2, "details"),
        ("Brawling", 2, "dagger"),
        ("Certamen", 3, "Mentem"),
        ("Charm", 4, "first impressions"),
        ("Civil & Canon Law", 2, "the Crusade"),
        ("Concentration", 2, "long stretches"),
        ("Disputatio", 2, "debate"),
        ("Finesse", 3, "precision"),
        ("Folk Ken", 3, "magi"),
        ("Guile", 4, "quick lies"),
        ("Hermes Lore", 4, "personalities"),
        ("Hermetic Law", 3, "mundane interference"),
        ("Intrigue", 4, "plotting"),
        ("Leadership", 3, "magi"),
        ("Levant Lore", 2, "politics"),
        ("Magic Theory", 4, "inventing spells"),
        ("Occult Lore", 2, "demons"),
        ("Parma Magica", 4, "Mentem"),
        ("Penetration", 3, "Mentem"),
        ("Read Lips", 3, "at a distance"),
        ("Scribe Latin", 2, "a bad hand"),
        ("Speak Arabic", 3, "the Holy Land"),
        ("Speak French", 4, "Provencal"),
        ("Speak Latin", 5, "whispers"),
    ],
    arts=_arts(8, 11, 5, 17, 5, 5, 5, 5, 16, 5, 5, 6, 12, 3, 8),
    spells=[
        ("Trust of Childlike Faith", "PeMe", 10),
        ("Loss of But a Moment's Memory", "PeMe(In)", 10),
        ("Black Whisper", "PeMe", 35),
        ("Blessing of Childlike Bliss", "PeMe", 25),
        ("Grip of the Choking Hand", "PeCo", 15),
        ("The Wound that Weeps", "PeCo", 15),
        ("Aura of Rightful Authority", "ReMe", 20),
        ("Veil of Invisibility", "PeIm", 10),
        ("Silence of the Smothered Sound", "PeIm", 10),
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Thoughts Within Babble", "InMe", 25),
        ("Pain of the Wizard's Gaze", "PeCo", 25),
        ("Spectacle of Abject Terror", "CrMe", 20),
        ("Weighing the Turncoat's Silver", "InMe", 20),
        ("The Demon's Eternal Oblivion", "PeVi", 20),
        ("Circular Ward Against Demons", "ReVi", 15),
        ("The Inexorable Search", "InCo", 20),
        ("Incantation of the Milky Eyes", "PeCo", 30),
        ("The Chirurgeon's Healing Touch", "CrCo", 20),
        ("Panic of the Elephant's Mouse", "ReAn", 15),
        ("Whispers Through the Black Gate", "InCo(Me)", 15),
        ("Whispering Winds", "InAu", 15),
        ("Eyes of the Past", "InIm", 20),
        ("Conjuration of the Indubitable Cold", "PeIg", 20),
        ("Clenching Grasp of the Crushed Heart", "PeCo", 40),
    ],
    traits={
        "Power-hungry": 3,
        "Manipulative": 3,
        "Heartless": 2,
        "Vulnerable": 1,
    },
    reputations={
        "Dangerous (magi whose secrets he knows)": 2,
        "Threat to peace (quaesitores)": 2,
    },
    notes=(
        "Equipment: a dagger, and his sigil, a silver pendant engraved with "
        "House Tytalus's sign; his casting shows no wizard's sigil at all. "
        "Afflictions as printed: a stoop and aching joints, and the "
        "Decrepitude his childhood's abuse left him. ArM4's Silent Magic "
        "(+5) is Quiet Magic here, taken once."
    ),
)

SPIRAL = Fourth(
    age=53,
    apparent=42,
    characteristics=characteristics(3, 1, -3, -5, 0, 1, 0, 0),
    confidence=3,
    twilight=6,
    decrepitude=0,
    granted=["The Enigma"],
    virtues=[
        ("Affinity", 3, "vim"),
        ("Visual Eidetic Memory", 3),
        ("Magic Sensitivity", 1),
        ("Strong-Willed", 1),
        ("Well Known", 1, "the Sufis of Baghdad"),
        ("Rapid Convalescence", 1),
        ("Feeble Communication", -4, "communication"),
        ("Lack of Control", -2),
        ("Disfigured", -1, "tattoos"),
        ("Blatant Gift", -1),
        ("Incomprehensible", -1),
        ("Obsessed", -1, "Islam's magic"),
    ],
    abilities=[
        ("Affinity Vim", 5, "Intellego"),
        ("Awareness", 2, "magic"),
        ("Concentration", 3, "long stretches"),
        ("Enigmatic Wisdom", 6, "Twilight"),
        ("Finesse", 3, "precision"),
        ("Hermes Lore", 3, "Criamon"),
        ("Hermetic Law", 2, "treaties"),
        ("Islamic Law", 2, "treaties"),
        ("Levant Lore", 2, "famous mages"),
        ("Magic Sensitivity", 3, "the Magic realm"),
        ("Magic Theory", 5, "inventing spells"),
        ("Parma Magica", 3, "Vim"),
        ("Penetration", 2, "Vim"),
        ("Scribe Arabic", 2, "obscure texts"),
        ("Scribe Latin", 3, "obscure texts"),
        ("Speak Arabic", 2, "a wide vocabulary"),
        ("Speak Latin", 5, "Hermetic usage"),
        ("Speak Scots Gaelic", 4, "colourful phrases"),
        ("Survival", 1, "desert"),
        ("Theology: Islam", 2, "magic"),
    ],
    arts=_arts(12, 20, 15, 14, 15, 7, 3, 3, 14, 3, 5, 12, 13, 3, 23),
    spells=[
        ("Sense the Lingering Magic", "InVi", 30),
        ("The Invisible Eye Revealed", "InVi", 30),
        ("Shell of Opaque Mysteries", "CrVi", 25),
        ("Shell of False Determinations", "CrVi", 25),
        ("Spell Analysis", "InVi", 30),
        ("Sense the Shadows of the Spheres", "InVi(Me)", 10),
        ("Sight of the Active Magics", "InVi", 40),
        ("Shroud Magic", "MuVi", 35),
        ("Wizard's Communion", "MuVi", 35),
        ("Mirror of Opposition (Corpus)", "MuVi", 35),
        ("Mirror of Opposition (Mentem)", "MuVi", 35),
        ("Mirror of Opposition (Vim)", "MuVi", 35),
        ("Wizard's Boost (Vim)", "MuVi", 35),
        ("Wizard's Boost (Mentem)", "MuVi", 35),
        ("The Demon's Eternal Oblivion", "PeVi", 35),
        ("Masking the Odor of Magic", "PeVi", 35),
        ("Aegis of the Hearth", "ReVi", 35),
        ("Circular Ward Against Demons", "ReVi", 35),
        ("Maintaining the Demanding Spell", "ReVi", 35),
        ("Wind of Mundane Silence", "PeVi", 35),
        ("Watching Ward", "ReVi", 35),
        ("Wizard's Focus", "InVi(Me)", 30),
        ("Glimpse Through the Mystic Veil", "InVi", 20),
        ("Reveal the Gift", "InVi", 30),
        ("Warping the Magical Veil", "MuVi", 20),
        ("Hammer of Thaumaturgical Shattering", "PeVi(In)", 35),
        ("Wizard's Wait", "ReVi", 35),
        ("Discern Images of Truth and Falsehood", "InIm", 30),
        ("Summoning the Distant Image", "InIm", 25),
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Thoughts Within Babble", "InMe", 25),
        ("Gift of Reason", "CrMe", 25),
        ("Emotion of Reversed Intentions", "MuMe", 20),
        ("Aura of Rightful Authority", "ReMe", 20),
        ("Eyes of the Future", "InIm", 30),
        ("Beguile the Normal Mind", "ReMe", 20),
    ],
    traits={"Enthusiastic": 3, "Naive": 3, "Obsessive": 3, "Obscure": 3},
    reputations={
        "Wise (the Sufis of Baghdad)": 2,
        "Peacemaker (quaesitores and Muslim rulers)": 1,
        "Interfering do-gooder (Crusader and counter-Crusader magi)": 1,
    },
    notes=(
        "His sigil, after some rummaging in his robes, turns out to be a "
        "small mummified toad; his hair stands on end when he casts. "
        "Twilight once deepened his grasp of Vim: he may write on it up to "
        "two thirds of his score. He knows Mirror of Opposition (Form) for "
        "Corpus, Mentem and Vim, and Wizard's Boost (Form) for Vim and "
        "Mentem, each at level 35; the general spells the Aegis of the "
        "Hearth, the Watching Ward and the rest he knows at 35 as well. "
        "ArM4's Feeble Communication (-4) is two steps of Poor "
        "Communication, which take him to -5."
    ),
)

WARDAT = Fourth(
    age=33,
    apparent=None,
    characteristics=characteristics(0, -2, 3, 2, 1, 3, -2, -2),
    confidence=3,
    twilight=0,
    decrepitude=0,
    granted=[
        "Sihr",
        ("Minor Magical Focus", {"focus": "jinn"}),
        "Twilight Prone",
        "Magic Sensitivity",
        "Second Sight",
    ],
    traditions=[SAHIRS],
    virtues=[
        ("Entrancement", 4),
        ("Outsider Trained in Order", 2),
        ("Cyclic Magic (+)", 2, "the moon, waxing to full"),
        ("Strong-Willed", 1),
        ("Plagued by Jinni", -4, "al-Abyad"),
        ("Cyclic Magic (-)", -2, "the moon, waning to dark"),
        ("Obsessed", -1, "the counter-Crusade"),
        ("Driving Goal", -1, "to defeat al-Abyad"),
        ("Reclusive", -1),
    ],
    abilities=[
        ("Awareness", 3, "alertness"),
        ("Bargain", 2, "jinn"),
        ("Brawling", 2, "fist and kick"),
        ("Charm", 1, "ulterior motives"),
        ("Concentration", 4, "long stretches"),
        ("Scribe Arabic", 3, "old texts"),
        ("Divination: Astrology", 5, "the planets"),
        ("Entrancement", 3, "the curious"),
        ("Folk Ken", 2, "peasants"),
        ("Guile", 3, "lying to the powerful"),
        ("Hermes Lore", 2, "exotic magi"),
        ("Islamic Law", 1, "sorcerers"),
        ("Leadership", 5, "intimidation"),
        ("Legend Lore", 5, "jinn"),
        ("Levant Lore", 2, "the Holy Land"),
        ("Magic Sensitivity", 2, "spirits"),
        ("Occult Lore", 5, "ghosts"),
        ("Second Sight", 4, "jinn"),
        ("Sihr", 6, "research"),
        ("Speak Arabic", 5, "the Holy Land"),
        ("Speak Latin", 2, "Hermetic usage"),
        ("Survival", 3, "desert"),
    ],
    arts={},
    spells=[],
    traits={"Reclusive": 3, "Determined": 3, "Pious": 3, "Brave": 1},
    reputations={
        "Hedge witch (Order of Hermes)": 3,
        "Threat to peace (quaesitores)": 1,
    },
    notes=(
        "A sahira of the Hermetic Sahirs, the House Ex Miscellanea tradition "
        "of Houses of Hermes: Societates, whose package (Sihr, a Minor "
        "Magical Focus in jinn, Twilight Prone) she takes in place of the "
        "Fourth Edition's sahir rules; that tradition is Iberian and rare in "
        "the Levant, so she is an outlier. She keeps no Arts and no Parma "
        "Magica, as printed (ArM4's sahirs could not learn Parma; HoH:S's "
        "have Arts). Her Sihr is 6 on the Art table: modest. ArM4 gave every "
        "sahir Magic Sensitivity and Second Sight, which are on her sheet.\n"
        "Her Familiarities, the old rules' knowledge of particular beings "
        "that eased their summoning: 'Aziza 3 (her grandmother's ghost), "
        "Hiss 2 (an airy fire spirit), Lucius 3 (a demon, whom she may call "
        "but never command), al-Manqa'i 3 and Sharif 3 (jinn of the Ghul and "
        "Marid tribes, her bound jinn), and the planets Mars (al-Mirrikh) 3, "
        "Jupiter (al-Mushtari) 4 and the Sun (al-Shams) 4. Her planetary "
        "invocations stretch a spell's Range, Duration or Target as vis once "
        "could for a magus: a power of the sahirs that Hermetic magic no "
        "longer has, kept as story.\n"
        "The jinni al-Abyad, the White, has plagued her since she was a "
        "child; finding how to beat him is her life's work, and she leaves "
        "her rooms only when the fight against the Crusaders needs her. Her "
        "sigil is a copper bracelet; a faint smell of roses rises as she "
        "works."
    ),
)

BLOCKS: dict[str, tuple[Fourth, str]] = {
    "umar": (UMAR, SIS),
    "amber": (AMBER, SIS),
    "felix": (FELIX, SIS),
    "esther": (ESTHER, SIS),
    "guillaume": (GUILLAUME, SIS),
    "rufus": (RUFUS, SIS),
    "spiral": (SPIRAL, SIS),
    "wardat": (WARDAT, ""),
}

#: The covenant each magus brews in, its aura as L8 gives it (a Divine
#: aura counts against), and the lab's modifier as the block prints it.
LABS: dict[str, tuple[str, int, int]] = {
    "umar": ("aedes_veritatis", 4, 1),
    "amber": ("aedes_veritatis", 4, 1),
    "felix": ("domus_pacis", 1, 0),
    "esther": ("domus_pacis", 1, 0),
    "guillaume": ("foothold", 2, -1),
    "rufus": ("foothold", 2, -1),
    "spiral": ("embassy", -2, 0),
}
#: Who made each ritual, where not the magus.
RITUAL_BY = {"felix": "tau"}


def build(levant: Levant) -> None:
    """Nothing to build: the magi are the covenant parts' records, and
    their stats go in last, in `stats`."""
    del levant


def stats(levant: Levant) -> None:
    """Enter the eight converted blocks, their longevity rituals, Wardat's
    bound jinn and Amber's familiar."""
    b = levant.b
    if not any(s.id == CONVOCATION.id for s in b.saga.spells):
        b.saga.spells.append(CONVOCATION)
    for key, (block, source) in BLOCKS.items():
        character = levant.magi.get(key)
        if character is None:
            continue
        stat, age = convert(key, block)
        b.stats(character, stat, source=source)
        character.background.year_born = b.year - age
        _own_spells(character)
        if key in LABS:
            _longevity(levant, key, character)
        if key == "amber":
            character.virtues_flaws.append(_virtue_flaw("True Friend"))
            character.personality_traits.append(ScoredTrait("Loyal (Luigi)", 3))
    _wardat(levant)
    _luigi(levant)


def _own_spells(character: Character) -> None:
    """Give the magus's own spells the book's Range, Duration, Target,
    page and words."""
    for spell in character.invented_spells:
        own = OWN_SPELLS.get(spell.name)
        if own is None:
            continue
        spell.range, spell.duration, spell.target, spell.source, spell.page = own[:5]
        spell.description = own[5]


def _art(character: Character, art: str) -> int:
    return lab.art_score(character, art)[0]


def _ability(character: Character, name: str) -> int:
    return lab.ability_score(character, name)[0]


def _longevity(levant: Levant, key: str, character: Character) -> None:
    """A longevity ritual at the Definitive Edition's Lab Total, Int +
    Magic Theory + Creo + Corpus + aura + the lab's modifier, made by the
    magus or by whoever the book says made it."""
    covenant_key, aura, lab_mod = LABS[key]
    maker = levant.magi.get(RITUAL_BY.get(key, key)) or character
    covenant = levant.covenants.get(covenant_key)
    if covenant is not None and covenant.aura:
        aura = covenant.aura if covenant.aura_realm == "Magic" else -covenant.aura
    total = (
        maker.characteristics.intelligence
        + _ability(maker, "Magic Theory")
        + _art(maker, "Creo")
        + _art(maker, "Corpus")
        + aura
        + lab_mod
    )
    character.aging.longevity_modifier = lab.longevity_modifier(max(total, 0))
    character.aging.longevity_by = maker.name


def _wardat(levant: Levant) -> None:
    """Wardat's two jinn as her bound beings, and links to all five of
    her Familiarities."""
    b = levant.b
    wardat = levant.magi.get("wardat")
    if wardat is None:
        return
    for key, bound, note in (
        ("al_manqai", True, "a jinni bound to her service"),
        ("sharif", True, "a jinni bound to her service"),
        ("aziza", False, "her grandmother's ghost, whom she summons"),
        ("hiss", False, "an airy fire spirit she summons"),
        ("lucius", False, "a demon she can summon but not command"),
    ):
        creature = levant.creatures.get(key)
        if creature is None:
            continue
        if bound and not any(
            being.creature_id == creature.id for being in wardat.bound_beings
        ):
            wardat.bound_beings.append(
                BoundBeing(
                    name=creature.name.split(",")[0],
                    tradition=SAHIRS,
                    kind="Bound jinni",
                    creature_id=creature.id,
                    notes="One of her Familiarities (3) in the book.",
                )
            )
        if not any(link.target_id == creature.id for link in wardat.links):
            b.link(wardat, "creatures", creature, note)


#: Luigi's bond, worked out again in Definitive Edition terms (L14): bound
#: with Muto Animal, Lab Total Mu 15 + An 18 + Int 3 + Magic Theory 5 +
#: aura 4 = 45, which buys cords of +2, +2 and +2 (15 points each) and
#: costs 9 pawns of vis (one a five points, rounded up).
BOND_TECHNIQUE, BOND_FORM, BOND_TOTAL = "Muto", "Animal", 45
CORDS = (2, 2, 2)
#: The book's bond qualities that remain as invested powers: name,
#: Technique, Form, level, cosmetic trait.
BOND_POWERS = (
    (
        "Shared Senses",
        "Intellego",
        "Animal",
        25,
        "Amber stares at things, Luigi looks about him",
    ),
    (
        "Mental Communication",
        "Intellego",
        "Mentem",
        15,
        "Amber's curiosity and Luigi's independence traded",
    ),
)


def _luigi(levant: Levant) -> None:
    """Luigi as Amber's bound familiar."""
    amber = levant.magi.get("amber")
    luigi = levant.creatures.get("luigi")
    if amber is None or luigi is None:
        return
    saga = levant.b.saga
    if any(f.character_id == amber.id for f in saga.familiars):
        return
    familiar = Familiar(
        id=storage.generate_unique_id("Luigi", [f.id for f in saga.familiars]),
        character_id=amber.id,
        name="Luigi",
        species="A house cat of ordinary size, white fur tipped with gold",
        magic_might=13,
        size=-3,
        virtues_flaws=[
            _virtue_flaw(name)
            for name in ("Magic Animal", "Lightning Reflexes", "Piercing Gaze")
        ]
        + [_virtue_flaw("True Friend")],
        personality_traits=[
            ScoredTrait("Curious", 4),
            ScoredTrait("Independent", 2),
            ScoredTrait("Cruel to enemies", 1),
            ScoredTrait("Loyal (Amber)", 3),
        ],
        binding_technique=BOND_TECHNIQUE,
        binding_form=BOND_FORM,
        binding_lab_total=BOND_TOTAL,
        target_binding_level=25 + 13 + 5 * -3,
        vis_spent_binding=math.ceil(BOND_TOTAL / 5),
        golden_cord=CORDS[0],
        silver_cord=CORDS[1],
        bronze_cord=CORDS[2],
        characteristics=luigi.characteristics,
        base_soak=luigi.soak,
        magic_resistance=13,
        natural_weapons=[
            Possession(
                id=storage.generate_unique_id("Claws and teeth", []),
                kind="weapon",
                name="Claws and teeth",
                weapon_init=2,
                weapon_attack=5,
                weapon_defense=6,
                weapon_damage=-1,
            )
        ],
        abilities=[
            Ability(
                name=name,
                category=access.ability_category(name),
                xp=ability_xp(score),
                specialty=specialty,
            )
            for name, score, specialty in (
                ("Awareness", 2, "sounds"),
                ("Stealth", 6, "hunting"),
            )
        ],
        bond_powers=[
            BondPower(
                id=storage.generate_unique_id(name, []),
                name=name,
                level=level,
                technique=technique,
                form=form,
                target_controller="Magus and familiar",
                vis_spent=math.ceil(level / 10),
                cosmetic_trait=trait,
            )
            for name, technique, form, level, trait in BOND_POWERS
        ],
    )
    saga.familiars.append(familiar)
    levant.b.link(amber, "creatures", luigi, "her familiar, Luigi")
