"""The Fourth Edition stat block, and one plain function, `convert`,
that turns it into the StatBlock Builder.stats reads: the Definitive
Edition's conversion appendix (DE pp. 537-538) as a short pipeline of
plain functions, one for each of its steps (Virtues and Flaws,
Abilities, spells, Twilight), applied to each printed magus. It is an
Adapter, though a function is all it needs.

The readings every Fourth Edition pack shares:

- Age: the printed age is kept. The appendix's +20% only sets the age a
  character is built from, and these are printed, not built.
- Characteristics and Arts as printed; no rebalancing.
- Virtues and Flaws at the catalog's tier under their Fifth Edition
  names (a Personality Flaw with both tiers in the catalog is Major at
  -2 or worse, Minor at -1; a Story Flaw is Major, DE p. 537); those with no Fifth Edition counterpart dropped, and
  Quaesitor, an office of House Guernicus rather than a Virtue (DE pp.
  67-68), dropped with the office noted.
- Abilities kept at their scores and renamed. A 4e total is a fifth of
  the 5e total for the same score, so the experience of a removed Ability
  goes, at 5e cost, to its replacement (DE p. 538), with no cap on what
  that buys: Certamen, which has no Ability now (DE p. 537), to
  Penetration; Legend Lore to Area Lore, where DE puts legends (DE p.
  159); Disputatio to Teaching; a storyteller's Ability to his best
  Living Language (DE p. 168). An Affinity Ability's points go to the Art
  it served, at the same cost, as 4e prices Abilities as 5e prices Arts.
- A Talent DE keeps as a Supernatural Ability brings its Virtue
  (Curse-Throwing, Hex, Shapeshifter).
- Spells at the catalog's level and Art. A spell the catalog lacks stays,
  as the magus's own at its printed level; only what Hermetic magic can no
  longer do is swapped, for a spell of the same level (DE p. 538). A
  magus whose book lists no spells, only the Arts he knows "all listed
  formulaics" in, knows the Definitive Edition's spells of those Arts
  within his Lab Total (`listed`), mastered where the book says so.
- Warping: Twilight Points / 3, rounded down (DE p. 6).
- Confidence: the Definitive Edition's baseline, not the old score (DE p.
  29): Score 1 and 3 Points; Self-Confident gives 2 and 5; a Tytalus
  apprenticeship adds 1 to the Score.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Any

from ..models import Creature, CreatureAttack, Saga
from ..rules.xp import (
    ABILITY_FACTOR,
    ART_FACTOR,
    ability_xp,
    art_xp,
    score_from_xp,
)
from .builder import StatBlock, _catalog_spells, _spell_key, paragraphs
from .builder import _ability as block_ability

#: The Definitive Edition's Confidence: (Score, Points) for an important
#: character, and with Self-Confident (DE pp. 29, 107).
CONFIDENCE = (1, 3)
SELF_CONFIDENT = (2, 5)


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
    #: Trained in House Tytalus, which adds 1 to the Confidence Score.
    tytalus: bool = False
    #: The Mastery Score of every spell, where the book says all are
    #: mastered.
    mastery: int = 0


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
    "Mage-Smith": "Verditius Magic",
    "Magical Affinity": "Affinity with {art}",
    "Affinity": "Affinity with {art}",
    "Felines": "Special Circumstances",
    "Cyclic Magic (+)": "Cyclic Magic (Positive)",
    "Cyclic Magic (-)": "Cyclic Magic (Negative)",
    "Feeble Communication": "Poor {characteristic}",
    "Sidhe Blood": "Faerie Blood",
    "Non-combatant": "Noncombatant",
    "Dependant": "Dependent",
    "Magic Affinity": "Minor Magical Focus",
    "Great Intelligence": "Great {characteristic}",
    "Incredible Intelligence": "Great {characteristic}",
    "Purifying Touch": "Lesser Purifying Touch",
    "Strong-willed": "Strong-Willed",
    "Well-traveled": "Well-Traveled",
    "Susceptible to Divine Power": "Susceptibility to Divine Power",
    "Minor Magic Deficiency": "Deficient Form",
    "Major Magic Deficiency": "Deficient Form",
    "Enemy": "Enemies",
    "Public vis source": "Public Vis Source",
    "Major Magical Deficiency": "Deficient Form",
    "Magical Deficiency": "Deficient Form",
    "Poor Communication": "Poor {characteristic}",
    "Great Characteristic": "Great {characteristic}",
    "Fury": "Wrathful",
    "Knack with Enigma": "Affinity with {ability}",
    "Special circumstances": "Special Circumstances",
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
    "Great {characteristic}": "characteristic",
    "Faerie Blood": "blood",
    "Lesser Purifying Touch": "disease",
    "Deficient Form": "form",
    "Affinity with {ability}": "ability",
    "Incompatible Arts": "arts",
    "Deleterious Circumstances": "circumstance",
    "Delusion": "detail",
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
    "Deep Sleeper": "not in the catalog",
    "Weak Parma": "the catalog's Flawed Parma Magica is weak against one "
    "Form, not when unaware",
    "Indenture": "a Fourth Edition Redcap's promise of service, kept as story",
    "Whitlams": "the Fourth Edition Redcap's devices, folded into Redcap",
    "Quaesitor": "an office of House Guernicus, not a Virtue now; the office is noted",
    "Follower of Bjornaer": "House Bjornaer's Heartbeast Virtue, which the "
    "Definitive Edition gives every member, takes its place",
    "Follower of Criamon": "House Criamon's Enigmatic Wisdom, given by the House",
    "Volkhv": "the Volkhvy tradition record carries the priest's magic",
    "Emerged Latent Magical Ability": "his heart-beast is described, not a Virtue",
    "Herbalism": "a Fourth Edition Virtue; the Ability is kept",
    "Faerie Enmity": "not in the catalog",
    "Sense of Doom": "not in the catalog",
    "Deft Art": "the Definitive Edition's Deft Form covers a Form only, not a "
    "Technique",
}
#: The Techniques, as a printed Deficiency names one.
TECHNIQUE_NAMES = {"Creo", "Intellego", "Muto", "Perdo", "Rego"}
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
    "True Love",
}
#: Flaws with both tiers that are Story Flaws, so Major (DE p. 537).
STORY_FLAWS = {"True Love"}
#: How many copies a printed entry becomes (ArM4's -4 Feeble Communication
#: is two steps of Poor Communication, to -5).
COPIES = {"Feeble Communication": 2}

#: A printed Ability's Fifth Edition name.
ABILITIES: dict[str, str] = {
    "Brawling": "Brawl",
    "Hermes Lore": "Organization Lore: Order of Hermes",
    "Hermetic Law": "Code of Hermes",
    "Occult Lore": "Infernal Lore",
    "Levant Lore": "Area Lore: Levant Tribunal",
    "Longshaft Weapon": "Great Weapon",
    "Shield and Weapon": "Single Weapon",
    "Weapon and Shield": "Single Weapon",
    "Climb": "Athletics",
    "Rabbinical Law": "Rabbinic Law",
    "Civil & Canon Law": "Civil and Canon Law",
    "Disputatio": "Teaching",
    "Divination: Astrology": "Artes Liberales",
    "Forgery": "Guile",
    "Read Lips": "Awareness",
    "Craft: Armory": "Craft: Armorer",
    "Craft: Clothiery": "Craft: Clothier",
    "Craft: Jewelry-making": "Craft: Jeweler",
    "Craft: Weapon-smithing": "Craft: Weaponsmith",
    "Greater Alpine Tribunal Lore": "Area Lore: Greater Alps Tribunal",
    "Order of Hermes Lore": "Organization Lore: Order of Hermes",
    "House Jerbiton Lore": "Organization Lore: House Jerbiton",
    "House Criamon Lore": "Organization Lore: House Criamon",
    "Lectio": "Teaching",
    "Play": "Music",
    "Play Lute": "Music",
    "Sing": "Music",
    "Boating": "Profession: Boatman",
    "Wagoneering": "Profession: Teamster",
    "Theology": "Theology: Christian",
    "Disguise": "Guile",
    "Bow": "Bows",
    "Play Harp": "Music",
    "Will Over Form": "Heartbeast",
    "Longshaft Weapons": "Great Weapon",
    "Hermetic Lore": "Organization Lore: Order of Hermes",
    "Herbalism": "Profession: Herbalist",
    "Clan History": "Organization Lore: the Kama clans",
    "Theology: Slavic": "Theology: Pagan",
    "Certamen": "Penetration",
    "Verditius Magic": "Magic Theory",
    "Visions": "Premonitions",
    "Curse": "Curse-Throwing",
}
#: Printed Abilities that are one skill with their replacement, so the
#: better score stands rather than the two adding up.
SAME_SKILL = {"Shield and Weapon", "Weapon and Shield"}
#: The printed Abilities that are a storyteller's, which DE puts in Living
#: Language.
STORYTELLING = {"Storyteller", "Storytelling"}
#: What a printed Affinity served, where that is not an Art's own name.
AFFINITY_ARTS = {
    "birds": "Animal",
    "bones": "Corpus",
    "cloth": "Herbam",
    "emotions": "Mentem",
    "felines": "Animal",
    "illusions of sight": "Imaginem",
    "weather": "Auram",
}
#: The Arts an Affinity with the elements may serve: its magus's best.
ELEMENTS = ("Aquam", "Auram", "Ignem", "Terram")
#: Abilities that come with the Supernatural Virtue of the same name.
VIRTUE_ABILITIES = {"Curse-Throwing", "Hex", "Shapeshifter"}

#: Printed spells the catalog has under another name.
SPELL_RENAMES: dict[str, str] = {
    "Parting the Waves": "Parting of the Waves",
    "The Seven-League Stride": "Seven-League Stride",
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
    "Soothe the Pains of the Beast": "Soothe Pains of the Beast",
    "Sense of Lingering Magic": "Sense of the Lingering Magic",
    "Seven League Stride": "Seven-League Stride",
    "Chirurgeon's Healing Touch": "The Chirurgeon's Healing Touch",
    "Scales of Magical Weight": "Scales of the Magical Weight",
    "Aura of Ennobled Presence": "Aura of the Ennobled Presence",
    "Easing the Strain of Childbirth": "Ease the Suffering of Childbirth",
    "Leap of Homecoming": "The Leap of Homecoming",
    "Circular Ward Against Faeries": "Circular Ward Against Faerie Spirits",
    "Ward Against Faeries of the Water": "Ward Against Faeries of the Waters",
}
#: Printed spells Hermetic magic can no longer cast, as it cannot see the
#: past or the future (DE p. 537), and the spell of the same Technique,
#: Form and level each becomes.
SWAPS: dict[str, str] = {
    "Eyes of the Past": "The Ear for Distant Voices",
    "Eyes of the Future": "Sight of the Blossom, Ears of the Oak",
}


#: A printed spell the catalog lacks, designed by the Definitive Edition's
#: guidelines: level, Range, Duration, Target and the working. General spells
#: and those the guidelines have no place for keep the printed level.
SPELL_DESIGNS: dict[str, tuple[int, str, str, str, str]] = {
    "Beguile the Normal Mind": (
        20,
        "Eye",
        "Sun",
        "Individual",
        "Base 5, +1 Eye, +2 Sun",
    ),
    "Blessing of Antaeus' Fortitude": (
        35,
        "Personal",
        "Sun",
        "Individual",
        "Base 25, +2 Sun",
    ),
    "Breaking the Perpetual Drought": (
        30,
        "Touch",
        "Sun",
        "Boundary",
        "Base 3, +1 Touch, +2 Sun, +4 Boundary",
    ),
    "Breath of Vulcan": (
        35,
        "Voice",
        "Momentary",
        "Room",
        "Base 15, +2 Voice, +2 Room",
    ),
    "Call Aeolus' Servants": (
        25,
        "Voice",
        "Sun",
        "Room",
        "Base 3, +2 Voice, +2 Sun, +2 Room",
    ),
    "Change the River's Path": (
        30,
        "Voice",
        "Concentration",
        "Part",
        "Base 5, +2 Voice, +1 Conc, +1 Part, +1 size",
    ),
    "Circle of the Faerie Stone": (
        30,
        "Voice",
        "Sun",
        "Individual",
        "Base 3, +2 Voice, +2 Sun, +3 size",
    ),
    "Emotion of Reversed Intentions": (
        20,
        "Eye",
        "Sun",
        "Individual",
        "Base 5, +1 Eye, +2 Sun",
    ),
    "Enlarging the Distant Image": (
        10,
        "Sight",
        "Concentration",
        "Individual",
        "Base 2, +3 Sight, +1 Conc",
    ),
    "Eyes of Flame": (
        25,
        "Eye",
        "Momentary",
        "Individual",
        "Base 15, +1 Eye, +1 blinding",
    ),
    "Eyes of the Owl": (
        5,
        "Touch",
        "Sun",
        "Individual",
        "Base 2, +1 Touch, +2 Sun, as Eyes of the Cat",
    ),
    "Eyes of the Serpent": (
        10,
        "Eye",
        "Concentration",
        "Individual",
        "Base 4, +1 Eye, +1 Conc",
    ),
    "Fulgurous Orb": (
        35,
        "Voice",
        "Momentary",
        "Room",
        "Base 20, +2 Voice, +1 thunderclap",
    ),
    "Full Health of Beast and Bird": (
        25,
        "Touch",
        "Momentary",
        "Individual",
        "Base 20, +1 Touch, Ritual",
    ),
    "Gift of the Buoyant Gosling": (
        20,
        "Sight",
        "Sun",
        "Individual",
        "Base 3, +3 Sight, +2 Sun",
    ),
    "Gift of the Hero's Strength": (
        20,
        "Touch",
        "Sun",
        "Individual",
        "Base 5, +1 Touch, +2 Sun",
    ),
    "Glimpse Through the Mystic Veil": (
        20,
        "Personal",
        "Concentration",
        "Vision",
        "Base 3, +1 Conc, +4 Vision, as Piercing the Faerie Veil",
    ),
    "Heat of Hell's Impending Doom": (
        30,
        "Touch",
        "Concentration",
        "Boundary",
        "Base 3, +1 Touch, +1 Conc, +4 Boundary, +1 unnatural, Ritual",
    ),
    "Humility of the Vanquished Knight": (
        20,
        "Eye",
        "Sun",
        "Individual",
        "Base 5, +1 Eye, +2 Sun",
    ),
    "Mastering the Stolid Mundane": (
        35,
        "Eye",
        "Concentration",
        "Individual",
        "Base 25, +1 Eye, +1 Conc",
    ),
    "Mighty Fling of the Menacing Knight": (
        20,
        "Voice",
        "Momentary",
        "Individual",
        "Base 10, +2 Voice",
    ),
    "Origin of the Ancient Object": (
        15,
        "Touch",
        "Concentration",
        "Individual",
        "Base 5, +1 Touch, +1 Conc",
    ),
    "Pain of the Wizard's Gaze": (
        25,
        "Sight",
        "Concentration",
        "Individual",
        "Base 5, +3 Sight, +1 Conc",
    ),
    "Prison of the Zephyrs": (
        25,
        "Voice",
        "Sun",
        "Individual",
        "Base 5, +2 Voice, +2 Sun",
    ),
    "Reveal the Gift": (20, "Voice", "Momentary", "Individual", "Base 10, +2 Voice"),
    "Sense the Magic Root": (
        10,
        "Touch",
        "Momentary",
        "Individual",
        "Base 5, +1 Touch",
    ),
    "Sense the Shadows of the Spheres": (
        20,
        "Personal",
        "Special",
        "Individual",
        "Ritual at the least level",
    ),
    "Spectacle of Abject Terror": (
        20,
        "Voice",
        "Sun",
        "Individual",
        "Base 4, +2 Voice, +2 Sun",
    ),
    "Subtle Shift of the Heart": (
        10,
        "Eye",
        "Sun",
        "Individual",
        "Base 3, +1 Eye, +2 Sun",
    ),
    "The Immaculate Beast": (
        15,
        "Touch",
        "Sun",
        "Individual",
        "Base 4, +1 Touch, +2 Sun",
    ),
    "The Travelling Thistledown": (
        20,
        "Touch",
        "Sun",
        "Individual",
        "Base 5, +1 Touch, +2 Sun",
    ),
    "Tongue of the Beasts": (
        20,
        "Touch",
        "Concentration",
        "Individual",
        "as Tongue of the Fishes",
    ),
    "Tongue of the Birds": (
        25,
        "Personal",
        "Sun",
        "Hearing",
        "Base 4, +2 Sun, +3 Hearing",
    ),
    "Weighing the Turncoat's Silver": (
        20,
        "Eye",
        "Momentary",
        "Individual",
        "Base 15, +1 Eye, as Posing the Silent Question",
    ),
    "Wizard's Sleeve of Practical Tools": (
        15,
        "Touch",
        "Sun",
        "Individual",
        "Base 3, +1 Touch, +2 Sun, +1 metal",
    ),
}


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
        if new == "Deficient Form" and detail in TECHNIQUE_NAMES:
            new = "Deficient Technique"
        if new in TWO_TIERS:
            major = points <= -2 or new in STORY_FLAWS
            new = f"{new} ({'Major' if major else 'Minor'})"
        key = PARAMETER.get(RENAMED.get(name, name)) or PARAMETER.get(new)
        if new == "Deficient Technique":
            key = "technique"
        entry: Any = (new, {key: detail}) if key else new
        entries.extend([entry] * COPIES.get(name, 1))
        shown = (
            new.replace("{art}", detail)
            .replace("{characteristic}", detail)
            .replace("{ability}", detail)
        )
        line = shown if new.startswith(f"{name} (") else f"{name} as {shown}"
        if detail and not key:
            # The catalog entry takes no parameter: the detail is kept here.
            said.append(f"{shown if new == name else line}: {detail}")
        elif new != name:
            said.append(line)
    return entries, said


def _affinity_art(name: str, specialty: str, block: Fourth) -> str:
    """The Art a printed Affinity Ability served, or "" for any other."""
    if name == "Magic Affinity":
        served = specialty
    elif name.startswith("Affinity "):
        served = name.removeprefix("Affinity ")
    else:
        return ""
    if served.lower() == "elements":
        return max(ELEMENTS, key=lambda art: block.arts.get(art, 0))
    return AFFINITY_ARTS.get(served.lower(), served.capitalize())


def _tongue(block: Fourth) -> str:
    """The block's best living language, as a Fifth Edition Ability."""
    spoken = [
        (score, name.removeprefix("Speak "))
        for name, score, _ in block.abilities
        if name.startswith("Speak ") and name != "Speak Latin"
    ]
    return f"Living Language: {max(spoken)[1]}"


def _abilities(
    block: Fourth, area: str
) -> tuple[list[tuple[str, int, str]], dict[str, int], dict[str, int], list[str]]:
    """The block's Abilities in Fifth Edition terms, merged where two
    became one; the experience past each new score; the Art points its
    Affinities give; and what moved. Printings of one skill (Scribe in
    each language; a weapon Ability and its weapon-and-shield form) count
    once, at the best score; any other Ability moved in adds its
    experience. `area` is the pack's Area Lore, for Legend Lore."""
    same_skill = {ABILITIES[name] for name in SAME_SKILL}
    moved: dict[str, int] = {}
    best: dict[str, int] = {}
    specialty: dict[str, str] = {}
    art_points: dict[str, int] = {}
    said: list[str] = []
    for name, score, spec in block.abilities:
        art = _affinity_art(name, spec, block)
        if art:
            points = ability_xp(score) // ABILITY_FACTOR
            art_points[art] = art_points.get(art, 0) + points
            said.append(f"{name} {score} to {art}, {points} xp")
            continue
        one_skill = False
        if name.startswith("Scribe "):
            new, one_skill = "Artes Liberales", True
        elif name.startswith("Speak "):
            tongue = name.removeprefix("Speak ")
            new = (
                "Dead Language: Latin"
                if tongue == "Latin"
                else (f"Living Language: {tongue}")
            )
        elif name == "Legend Lore":
            new, spec = f"Area Lore: {area}", "legends"
        elif name in STORYTELLING:
            new = _tongue(block)
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
    abilities: list[tuple[str, int, str]] = []
    spare: dict[str, int] = {}
    for new, spec in specialty.items():
        total = ability_xp(best[new]) + moved[new]
        score = score_from_xp(total, ABILITY_FACTOR)
        abilities.append((new, score, spec))
        if total > ability_xp(score):
            spare[new] = total - ability_xp(score)
    return abilities, spare, art_points, said


def _spells(
    key: str, block: Fourth, second_swaps: Mapping[tuple[str, str], str]
) -> tuple[list[tuple[str, str, int | None, int]], list[str]]:
    """The block's spells as the catalog has them, each rename and swap
    named, and each spell whose catalog level or Art differs listed."""
    known: list[tuple[str, str, int | None, int]] = []
    seen: set[str] = set()
    said: list[str] = []
    changed: list[str] = []
    printings = _catalog_spells()
    for name, arts, level in block.spells:
        swap = second_swaps.get((key, name)) or SWAPS.get(name)
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
        design = SPELL_DESIGNS.get(new)
        if design and design[0] != level:
            changed.append(f"{name} {arts} {level} to level {design[0]}")
        known.append((new, arts, design[0] if design else level, block.mastery))
    if changed:
        said.append("At the catalog's level or Art: " + "; ".join(changed))
    return known, said


def convert(
    key: str,
    block: Fourth,
    second_swaps: Mapping[tuple[str, str], str] | None = None,
    *,
    area: str,
) -> tuple[StatBlock, int]:
    """A Fourth Edition block as a Definitive Edition StatBlock, with its
    age; the biography lists what changed. `second_swaps` are a pack's
    swaps made otherwise for one magus, by (key, printed spell); `area`
    is the pack's Area Lore, which takes the block's Legend Lore."""
    virtues, said_virtues = _virtues(block)
    abilities, spare, art_points, said_abilities = _abilities(block, area)
    held = {v if isinstance(v, str) else v[0] for v in virtues}
    virtues += sorted({n for n, _, _ in abilities} & VIRTUE_ABILITIES - held)
    arts, spare_art = _with_art_points(block.arts, art_points)
    spells, said_spells = _spells(key, block, second_swaps or {})
    warping = block.twilight // 3
    score, points = confidence(block, virtues)
    lines = [
        f"Converted from the Fourth Edition block by the Definitive "
        f"Edition's appendix: age {block.age} as printed"
        + (f" (looks {block.apparent})" if block.apparent else "")
        + f"; Twilight Points {block.twilight} / 3 = Warping {warping}; "
        f"Confidence {score} ({points} points), the Definitive Edition's "
        + ("Self-Confident" if points == SELF_CONFIDENT[1] else "baseline")
        + (", +1 for a Tytalus apprenticeship" if block.tytalus else "")
        + f", not the old {block.confidence}. Characteristics and Arts as "
        "printed; no rebalancing.",
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
        "confidence": (score, points),
        "decrepitude": (block.decrepitude, 0),
        "warping": (warping, 0),
        "virtues_flaws": virtues,
        "abilities": abilities,
        "arts": arts,
        "spare_xp": spare,
        "spare_art_xp": spare_art,
        "spell_designs": SPELL_DESIGNS,
        "traits": dict(block.traits),
        "reputations": dict(block.reputations),
        "spells": spells,
        "traditions": list(block.traditions),
        "notes": "\n".join([block.notes.strip(), *lines]).strip(),
    }
    if block.apparent:
        stat["apparent_age"] = block.apparent
    return stat, block.age


def _with_art_points(
    printed: Mapping[str, int], points: Mapping[str, int]
) -> tuple[dict[str, int], dict[str, int]]:
    """Arts with `points` of experience added, and what is left past each
    new score."""
    scores = dict(printed)
    spare: dict[str, int] = {}
    for art, gained in points.items():
        total = art_xp(scores.get(art, 0)) + gained
        scores[art] = score_from_xp(total, ART_FACTOR)
        if total > art_xp(scores[art]):
            spare[art] = total - art_xp(scores[art])
    return scores, spare


def arts(cr: int, in_: int, mu: int, pe: int, re: int, *forms: int) -> dict[str, int]:
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


def confidence(block: Fourth, virtues: Sequence[Any]) -> tuple[int, int]:
    """The Definitive Edition's Confidence for the converted block: the
    baseline, or Self-Confident's, with 1 more for a Tytalus apprenticeship
    (DE p. 29)."""
    names = {v if isinstance(v, str) else v[0] for v in virtues}
    score, points = SELF_CONFIDENT if "Self-Confident" in names else CONFIDENCE
    return score + (1 if block.tytalus else 0), points


def listed(
    pairs: Sequence[str],
    arts: Mapping[str, int],
    intelligence: int,
    theory: int,
    aura: int,
    *,
    above: int = 0,
) -> list[tuple[str, str, int]]:
    """The Definitive Edition's spells of each Technique and Form in
    `pairs` ("InMe"), each within the magus's Lab Total for it (the lower
    Art where a requisite joins: Technique + Form + Int + Magic Theory +
    aura), and above level `above`: the spells of a magus whose book says
    only that he knows "all listed formulaics" in those Arts."""
    found: list[tuple[str, str, int]] = []
    for printings in _catalog_spells().values():
        spell = next((s for s in printings if s.source == "DE"), None)
        if spell is None or not spell.level or spell.level <= above:
            continue
        short = spell.technique[:2] + spell.form[:2]
        if short not in pairs:
            continue
        technique = min(arts.get(a, 0) for a in (spell.technique, *spell.requisites))
        form = min(arts.get(a, 0) for a in (spell.form, *spell.requisites))
        if spell.level <= technique + form + intelligence + theory + aura:
            requisites = ",".join(r[:2] for r in spell.requisites)
            found.append(
                (
                    spell.name,
                    short + (f"({requisites})" if requisites else ""),
                    spell.level,
                )
            )
    return sorted(found, key=lambda s: (s[1][:4], s[2], s[0]))


# -- creatures --
#
# DE pp. 537-538 say only that combat was rewritten, so these rules are the
# app's own, measured on creatures printed in both editions (the lion,
# Medieval Bestiary Revised p. 37 and DE p. 434; the bear, the wolf, the
# griffin). The 4e sheet (ArM4 p. 261) puts Size into Soak and Damage and
# takes it from Defense; 5e carries it in Strength, Quickness and the wound
# ranges (DE p. 437), and gives beasts the combat skill 4e left implicit.

#: What a printed Attack lacks beside a 5e one: the measured gap, wolf +7,
#: lion +8, bear +9, griffin +10.
ATTACK_GAP = 8
#: The combat Ability a creature's printed Attack may give, a 5e beast's
#: range (DE pp. 429-435; the adult griffon, Legends of Hermes p. 134).
COMBAT_SKILL = (3, 8)
#: Improved Damage, RoP:M p. 40, and how many times a creature takes it.
IMPROVED_DAMAGE = 3
MOST_IMPROVED = 4
#: Old Protection kept whole, and the Stamina that counts whole for Soak.
WHOLE_PROTECTION = 4
WHOLE_STAMINA = 8
#: The Realms whose powers are priced by the RoP tables: RoP:M p. 36 and
#: RoP:F p. 55 agree. The Infernal keeps a printed cost.
PRICED_REALMS = ("Magic", "Faerie")


@dataclass(frozen=True)
class Weapon:
    """A Definitive Edition weapon's modifiers (DE pp. 408-409, 440)."""

    ability: str
    init: int
    attack: int
    defense: int
    damage: int
    natural: bool = False


WEAPONS: dict[str, Weapon] = {
    "Fist": Weapon("Brawl", 0, 0, 0, 0, True),
    "Kick": Weapon("Brawl", -1, 0, -1, 3, True),
    "Teeth": Weapon("Brawl", 0, 3, 1, 1, True),
    "Large teeth": Weapon("Brawl", 0, 4, 1, 3, True),
    "Claws": Weapon("Brawl", -1, 2, 3, 2, True),
    "Large claws": Weapon("Brawl", 0, 5, 3, 4, True),
    "Hooves": Weapon("Brawl", 2, 2, 2, 1, True),
    "Large horns": Weapon("Brawl", 2, 3, 2, 3, True),
    "Dagger": Weapon("Brawl", 0, 2, 0, 3),
    "Club": Weapon("Single Weapon", 1, 2, 1, 3),
    "Axe": Weapon("Single Weapon", 1, 4, 0, 6),
    "Long sword": Weapon("Single Weapon", 2, 4, 1, 6),
    "Long sword and round shield": Weapon("Single Weapon", 2, 4, 3, 6),
    "Lance": Weapon("Single Weapon", 2, 4, 0, 5),
    "Short spear": Weapon("Single Weapon", 2, 2, 0, 5),
    "Great sword": Weapon("Great Weapon", 2, 5, 2, 9),
    "Long spear": Weapon("Great Weapon", 3, 3, 1, 7),
    "Warhammer": Weapon("Great Weapon", 0, 6, 0, 12),
    "Composite bow": Weapon("Bows", -2, 4, 0, 7),
    "Stone": Weapon("Thrown Weapon", 0, 1, 0, 2),
}
#: The weapon an attack's printed name means, the first word found, or the
#: fist. A large creature's claws and teeth are the large ones.
WEAPON_WORDS: tuple[tuple[str, str], ...] = (
    ("shield", "Long sword and round shield"),
    ("long sword", "Long sword"),
    ("longsword", "Long sword"),
    ("great sword", "Great sword"),
    ("greatsword", "Great sword"),
    ("long spear", "Long spear"),
    ("lance", "Lance"),
    ("spear", "Short spear"),
    ("bow", "Composite bow"),
    ("warhammer", "Warhammer"),
    ("axe", "Axe"),
    ("club", "Club"),
    ("dagger", "Dagger"),
    ("rock", "Stone"),
    ("boulder", "Stone"),
    ("kick", "Hooves"),
    ("hoof", "Hooves"),
    ("gore", "Large horns"),
    ("horn", "Large horns"),
    ("maul", "Large claws"),
    ("claw", "Claws"),
    ("talon", "Claws"),
    ("bite", "Teeth"),
    ("teeth", "Teeth"),
    ("beak", "Teeth"),
)
LARGER = {"Claws": "Large claws", "Teeth": "Large teeth"}
#: Printed attacks that are powers, not weapons: left for their power.
NOT_WEAPONS = ("breath", "molten", "spiritual form")


def weapon_of(name: str, size: int) -> Weapon:
    """The Definitive Edition weapon a printed attack's name means."""
    lowered = name.lower()
    found = next((w for word, w in WEAPON_WORDS if word in lowered), "Fist")
    if size > 0:
        found = LARGER.get(found, found)
    return WEAPONS[found]


def soak_of(old_protection: int, stamina: int) -> int:
    """Soak from a Stamina and the Protection the old Soak held: 4e Soak ran
    higher, so past +4 of Protection half counts, and past +8 of Stamina half
    (a giant's Sta +20 has no 5e equivalent; RoP:M pp. 86-87 tops out near
    Soak +14)."""
    whole = min(old_protection, WHOLE_PROTECTION)
    protection = whole + (old_protection - whole + 1) // 2
    return (
        min(stamina, WHOLE_STAMINA) + max(stamina - WHOLE_STAMINA, 0) // 2 + protection
    )


def rebuild_combat(creature: Creature, *, printed: bool = True) -> None:
    """Works a creature's Combat and Soak out again from the Fourth Edition
    totals it holds: a combat Ability from its printed Attack, or a higher
    score the block has, and the DE formulas for the totals. `printed` is False for a record whose Damage
    and Soak an earlier reading already took Size out of."""
    traits = creature.characteristics
    size, qik = creature.size, traits.quickness
    if size < 0:
        # 5e builds smallness into Quickness (DE p. 437); 4e put it in Defense.
        qik -= size
        creature.characteristics = replace(traits, quickness=qik)
    said: list[str] = []
    skills = {a.name: score_from_xp(a.xp, ABILITY_FACTOR) for a in creature.abilities}
    rebuilt: list[CreatureAttack] = []
    wanted: dict[str, int] = {}
    for line in creature.attacks:
        if line.attack is None or any(w in line.name.lower() for w in NOT_WEAPONS):
            continue
        weapon = weapon_of(line.name, size)
        worked = line.attack + ATTACK_GAP - traits.dexterity - weapon.attack
        worked = max(COMBAT_SKILL[0], min(COMBAT_SKILL[1], worked))
        wanted[weapon.ability] = max(wanted.get(weapon.ability, 0), worked)
    for line in creature.attacks:
        if line.attack is None or any(w in line.name.lower() for w in NOT_WEAPONS):
            rebuilt.append(line)
            continue
        weapon = weapon_of(line.name, size)
        skill = max(skills.get(weapon.ability, 0), wanted[weapon.ability])
        improved = 0
        if printed and weapon.natural and line.damage is not None:
            beyond = line.damage - traits.strength - size - weapon.damage
            improved = min(max(beyond, 0) // IMPROVED_DAMAGE, MOST_IMPROVED)
        rebuilt.append(
            replace(
                line,
                init=qik + weapon.init,
                attack=traits.dexterity + skill + weapon.attack,
                defense=qik + skill + weapon.defense,
                damage=None
                if line.damage is None
                else traits.strength + weapon.damage + improved * IMPROVED_DAMAGE,
            )
        )
        said.append(
            f"{line.name} Init {line.init:+d}, Attack {line.attack:+d}, Defense "
            f"{line.defense:+d}, Damage "
            + ("n/a" if line.damage is None else f"{line.damage:+d}")
        )
    protection = creature.soak - traits.stamina - (size if printed else 0)
    if creature.can_be_wounded and (creature.soak or creature.attacks):
        said.append(f"Soak {creature.soak:+d}")
        creature.soak = soak_of(max(protection, 0), traits.stamina)
    creature.attacks = rebuilt
    held = {a.name: a for a in creature.abilities}
    for ability, score in wanted.items():
        if ability not in held:
            creature.abilities.append(block_ability(ability, score, ""))
        elif skills[ability] < score:
            held[ability].xp = ability_xp(score)
    if said:
        creature.notes = paragraphs(
            creature.notes, f"As printed in Fourth Edition: {'; '.join(said)}."
        ).strip()


def reprice_powers(creature: Creature) -> None:
    """Prices a creature's powers by the table for its Realm (RoP:M p. 36,
    RoP:F p. 55): a formulaic or Personal power of a known level costs half
    its magnitude, with Init Qik less the same, a Focus Power keeps its cost
    of a point a magnitude with Init Qik less the magnitude, and a power
    printed at no cost stays free, as Improved Powers makes a constant one
    (RoP:M p. 41). An Infernal power keeps its printed cost."""
    if creature.realm not in PRICED_REALMS:
        return
    qik = creature.characteristics.quickness
    for power in creature.powers:
        if power.level is None:
            continue
        magnitude = max(1, power.level // 5)
        if "non-Ritual" in power.description or "Focus Power" in power.description:
            power.init = qik - magnitude
            continue
        half = (magnitude + 1) // 2
        power.init = qik - half
        if power.might_cost and power.might_cost != half:
            power.description = (
                f"{power.description} Fourth Edition: {power.might_cost} points."
            ).strip()
            power.might_cost = half


@dataclass(frozen=True)
class Kin:
    """What a creature takes from its Fifth Edition kin: its Stamina, and
    its Soak, or None to work Soak out again from that Stamina."""

    stamina: int
    soak: int | None
    source: str


def take_kin(creature: Creature, like: Kin) -> None:
    """A creature with its kin's Stamina and Soak, saying so."""
    if like.soak is None:
        held = soak_of(0, creature.characteristics.stamina)
        creature.soak = max(creature.soak - held + soak_of(0, like.stamina), 0)
    else:
        creature.soak = like.soak
    creature.characteristics = replace(creature.characteristics, stamina=like.stamina)
    creature.notes = paragraphs(creature.notes, f"Stamina and Soak as {like.source}.")


def reconvert(
    saga: Saga,
    might: Mapping[str, int],
    *,
    kin: Mapping[str, Kin] | None = None,
    printed: bool = True,
    forms: Mapping[str, str] | None = None,
    orders: Mapping[str, tuple[str, int | None]] | None = None,
    designs: Mapping[tuple[str, str], tuple[int, tuple[str, str, str]]] | None = None,
) -> None:
    """Every creature of a Fourth Edition pack in Definitive Edition terms.
    `might` holds the Might of each creature set by the standing rule: a
    unique being keeps its printed score, a creature with 5e kin takes the
    kin's, a demon RoP:I p. 30, a dragon RoP:M p. 74, a faerie RoP:F p. 47,
    and anything else its role and power on the chart of RoP:M p. 34. A
    power never raises it. `forms` are Might Forms this conversion sets,
    `orders` a demon's order and Hierarchy (RoP:I p. 30), and `designs` a
    power's level, Range, Duration and Target by the guidelines, by
    (creature, power)."""
    for creature in saga.creatures:
        new = might.get(creature.name)
        if new is not None and new != creature.might:
            creature.notes = paragraphs(
                creature.notes, f"Might {creature.might} as printed."
            )
            creature.might = new
        rebuild_combat(creature, printed=printed)
        like = (kin or {}).get(creature.name)
        if like is not None:
            take_kin(creature, like)
        creature.might_form = (forms or {}).get(creature.name, creature.might_form)
        order = (orders or {}).get(creature.name)
        if order is not None:
            creature.order, creature.hierarchy = order
        for power in creature.powers:
            design = (designs or {}).get((creature.name, power.name))
            if design is not None:
                power.level = design[0]
                power.range, power.duration, power.target = design[1]
        reprice_powers(creature)
