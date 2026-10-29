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
  names (a Flaw with both tiers in the catalog is Major at -2 or worse,
  Minor at -1); those with no Fifth Edition counterpart dropped, and
  Quaesitor, an office of House Guernicus rather than a Virtue (DE pp.
  67-68), dropped with the office noted.
- Abilities kept at their scores and renamed; a dropped Ability's
  experience moved to its replacement. Certamen has no Ability now (DE p.
  537), so its points are dropped.
- Spells at the catalog's level and Art; each one the catalog lacks
  swapped for a catalog spell of the same Technique, Form and level. A
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
from dataclasses import dataclass, field
from typing import Any

from ..rules.xp import ability_xp, score_from_xp
from .builder import StatBlock, _catalog_spells, _spell_key

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
    "Greater Alpine Tribunal Lore": "Area Lore: Greater Alps Tribunal",
    "Order of Hermes Lore": "Organization Lore: Order of Hermes",
    "House Jerbiton Lore": "Organization Lore: House Jerbiton",
    "House Criamon Lore": "Organization Lore: House Criamon",
    "Lectio": "Teaching",
    "Play": "Music",
    "Play Lute": "Music",
    "Sing": "Music",
    "Storyteller": "Charm",
    "Storytelling": "Charm",
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
}
#: Printed Abilities that are one skill with their replacement, so the
#: better score stands rather than the two adding up.
SAME_SKILL = {"Shield and Weapon", "Weapon and Shield"}
#: Printed Abilities the Definitive Edition has no place for.
NO_ABILITY = {"Certamen", "Verditius Magic", "Magic Affinity", "Visions"}

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
    "Eyes of Flame": "Circle of Encompassing Flames",
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
    "Eyes of the Owl": "Eyes of the Cat",
    # ArM4 core spells the Novgorod magi know
    "Tongue of the Beasts": "Tongue of the Fishes",
    "Tongue of the Birds": "Hunter's Sense",
    "The Immaculate Beast": "Beast of Outlandish Size",
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
            new = f"{new} ({'Major' if points <= -2 else 'Minor'})"
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
        known.append((new, arts, level, block.mastery))
    if changed:
        said.append("At the catalog's level or Art: " + "; ".join(changed))
    return known, said


def convert(
    key: str,
    block: Fourth,
    second_swaps: Mapping[tuple[str, str], str] | None = None,
) -> tuple[StatBlock, int]:
    """A Fourth Edition block as a Definitive Edition StatBlock, with its
    age; the biography lists what changed. `second_swaps` are a pack's
    swaps made otherwise for one magus, by (key, printed spell)."""
    virtues, said_virtues = _virtues(block)
    abilities, said_abilities = _abilities(block)
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
        "arts": dict(block.arts),
        "traits": dict(block.traits),
        "reputations": dict(block.reputations),
        "spells": spells,
        "traditions": list(block.traditions),
        "notes": "\n".join([block.notes.strip(), *lines]).strip(),
    }
    if block.apparent:
        stat["apparent_age"] = block.apparent
    return stat, block.age


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
