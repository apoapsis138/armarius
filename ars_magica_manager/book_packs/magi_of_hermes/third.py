"""Magi of Hermes, chapters eleven to fifteen (pp. 96-145): Petalichus of
Verditius, Ranulf of Flambeau, Scipio of Merinita, Tolides of Flambeau and
Yestin of Jerbiton, every printed block, in the errata's corrected form.

Abilities are written as the book lists them and read by `_abilities`, and
each magus's spells are named from one table, so a block shows only what
it knows at that age. Casting totals are not kept: the sheet works them
out. A spell the catalog holds takes the catalog's level; where a block
prints another level, or a General spell at a set level, its notes say so.
Stat blocks are the book's; the rest is a summary, not its words."""

from __future__ import annotations

import re

from ..builder import (
    StatBlock,
    arts_from,
    characteristics,
    paragraphs,
    vf_ability,
    vf_art,
    vf_puissant,
)
from . import Magus, Printing

VERDITIUS = "house_verditius"
FLAMBEAU = "house_flambeau"
MERINITA = "house_merinita"
JERBITON = "house_jerbiton"

#: The book's bare Ability names, as the sheet's catalog names them.
_ABILITY_NAMES = {
    "Latin": "Dead Language: Latin",
    "Greek": "Living Language: Greek",
    "Constantinople Lore": "Area Lore: Constantinople",
    "Clothiery": "Craft: Clothiery",
    "Weaver": "Craft: Weaver",
    "Verditius Cult Lore": "Mystery Cult Lore: Verditius",
    "Cononites Cult Lore": "Mystery Cult Lore: Cononites",
    "House Merinita Lore": "Mystery Cult Lore: Merinita",
    "Enchanting Music": "Enchanting: Music",
    "High French": "Living Language: High French",
    "French Kingdom Lore": "Area Lore: French Kingdom",
    "Order of Hermes Lore": "Organization Lore: Order of Hermes",
    "Divine Lore": "Dominion Lore",
    "English": "Living Language: English",
    "Norman French": "Living Language: Norman French",
    "Welsh": "Living Language: Welsh",
    "Stonehenge Lore": "Area Lore: Stonehenge",
    "Normandy Lore": "Area Lore: Normandy",
}
_ABILITY = re.compile(
    r"^(?P<name>.+?) (?P<score>\d+)(?:\+\d+)?(?: \(\d+\))?(?: \((?P<spec>[^()]*)\))?$"
)


def _abilities(printed: str) -> list[tuple[str, int, str]]:
    """An Abilities line as the book prints it ("Finesse 1+2 (precision)"):
    the Puissant bonus and the xp in brackets are left out."""
    found = []
    for entry in printed.split(", "):
        match = _ABILITY.match(entry.strip())
        if match is None:
            raise ValueError(f"Unreadable Ability: {entry!r}")
        name = match["name"]
        found.append(
            (_ABILITY_NAMES.get(name, name), int(match["score"]), match["spec"] or "")
        )
    return found


def _spells(
    table: dict[str, tuple[str, int]], names: str
) -> list[tuple[str, str, int, int]]:
    """The spells `names` lists ("Bind Fast:1; Prying Eyes", the number a
    Mastery score), with their Arts and level from `table`."""
    found = []
    for entry in names.split("; "):
        name, _, mastery = entry.strip().partition(":")
        arts, level = table[name]
        found.append((name, arts, level, int(mastery or 0)))
    return found


# Petalichus of Verditius (pp. 96-105)

_PETALICHUS_SPELLS: dict[str, tuple[str, int]] = {
    "Unmake This Cloth": ("PeAn(He)", 10),
    "Bind Fast": ("ReAn(He)", 5),
    "A Day's Worth of Spinning": ("ReAn", 10),
    "A Day's Worth of Weaving": ("ReAn", 10),
    "The Even Hand of The Determined Weaver": ("ReAn(Cr)", 5),
    "The Treacherous Cloak": ("ReAn(He)", 5),
    "The Weaver's Subtle Art": ("ReAn", 5),
    "Arachne's Tuition": ("ReCo", 25),
    "Remain Within Those Walls": ("ReCo", 20),
    "Spasms of the Uncontrolled Hand": ("ReCo", 5),
    "Lamp without Flame": ("CrIg", 10),
    "Tales of the Ashes": ("InIg", 5),
    "Prying Eyes": ("InIm", 5),
    "To See As Though a Plethron Distant": ("InIm", 25),
    "The Unwelcoming Room": ("CrMe", 30),
    "Sight of the Transparent Motive": ("InMe", 10),
    "Recollection of Memories Never Quite Lived": ("MuMe", 4),
    "Aura of Rightful Authority": ("ReMe", 20),
    "Scribe the Perfect Circle": ("ReTe(Cr)", 4),
    "The Unseen Arm": ("ReTe", 5),
    "Scales of the Magical Weight": ("InVi", 5),
    "Sense the Weight of Divine Power": ("InVi", 3),
    "Sense the Weight of Faerie Power": ("InVi", 3),
    "Sense the Weight of Infernal Power": ("InVi", 3),
    "Sense the Weight of Magical Power": ("InVi", 3),
    "A Day's Grace": ("ReVi", 30),
}
_P_GAUNTLET = (
    "Unmake This Cloth; A Day's Worth of Spinning; A Day's Worth of Weaving; "
    "The Even Hand of The Determined Weaver; The Weaver's Subtle Art; "
    "Arachne's Tuition; Spasms of the Uncontrolled Hand; Lamp without Flame; "
    "Tales of the Ashes; Prying Eyes; Sight of the Transparent Motive; "
    "Aura of Rightful Authority; Scales of the Magical Weight"
)
_P_15 = _P_GAUNTLET + "; Bind Fast; The Treacherous Cloak"
_P_30 = _P_15 + (
    "; Remain Within Those Walls; The Unseen Arm; "
    "Sense the Weight of Divine Power; Sense the Weight of Faerie Power; "
    "Sense the Weight of Infernal Power; Sense the Weight of Magical Power"
)
_P_45 = (
    _P_30.replace("Bind Fast", "Bind Fast:1")
    .replace("The Treacherous Cloak", "The Treacherous Cloak:1")
    .replace("Sight of the Transparent Motive", "Sight of the Transparent Motive:1")
) + (
    "; To See As Though a Plethron Distant; The Unwelcoming Room; "
    "Recollection of Memories Never Quite Lived; Scribe the Perfect Circle; "
    "A Day's Grace"
)
_P_CHARACTERISTICS = characteristics(2, 2, 0, 0, -1, 0, 2, -1)
_P_FIRST = [
    "The Gift",
    "Hermetic Magus",
    ("Major Magical Focus", {"focus": "cloth"}),
    "Inventive Genius",
    vf_puissant("Artes Liberales"),
    vf_puissant("Finesse"),
    vf_puissant("Magic Theory"),
    "Self-Confident",
    "Verditius Magic",
    "Weak Spontaneous Magic",
    "Slow Caster",
    ("Driven (Minor)", {"detail": "find the lost works"}),
    "Infamous",
]
_P_ENEMY = ("Enemies", {"detail": "Solar Magnus"})
_P_LATER = [
    "Celestial Magic",
    "Hermetic Numerology",
    "Hermetic Geometry",
    "Items of Quality",
    "Difficult Spontaneous Magic",
    "Hubris",
]
_P_REPUTATION = {"Ill-tempered (Magi of Thebes)": 4}
_P_COMBAT = (
    "Combat: dodge Init -1, Defense +0; fist Init -1, Attack +3, Defense +0, "
    "Damage -1; knife Init -1, Attack +5, Defense +1, Damage +1. Soak +0."
)
_P_SPELL_NOTES = (
    "Spell notes: Arachne's Tuition is ReCo 25 with Touch Range by the "
    "errata, not the 20 and Eye the blocks and p. 101 print; he uses it to "
    "move an apprentice's limbs from within, adding 1 to a season's Source "
    "Quality for physical crafts, at 1 Warping point a year for each two "
    "seasons of it. A Day's Worth of Spinning and of Weaving are Rego Craft "
    "Magic, with Perception + Finesse against the craft's Ease Factor; a "
    "bolt is two paces by one, and Herbam requisites apply to plant cloth."
)
_P_DOOR = (
    "Sanctum door hanging, a tapestry with a white sanctum marker on deep "
    "red, showing damnation and death up close, carried to protect a "
    "temporary sanctum. Come No Further (CrMe 45, Pen +12, constant, "
    "expires after 70 years): those approaching need a Brave stress roll of "
    "9 to touch it. The Weight of All Perdition Be Upon You (Cr(Pe)Me(Co) "
    "35, Pen +20, unlimited, expires after 70 years): touching it burns "
    "with painless agony and demonic voices; a Brave roll of 9 to pass, at "
    "-3 if already affected by Come No Further."
)
_P_SHEARS = (
    "Cloth shears, an Item of Quality invested with The Perfect Fit: +2 to "
    "rolls to make or mend clothing, and the same to Finesse rolls for "
    "their Rego Craft Magic. The book describes no effect by that name."
)
_P_LOOM = (
    "Loom, an Item of Quality: +4 to all mundane weaving, and invested with "
    "A Day's Worth of Weaving twice a day, the bonus aiding its Finesse."
)
_P_DISTAFF = (
    "Talisman: the Distaff of Petalichus, a four-sided black greatstaff with "
    "white symbols set out in mathematical ratios. Attunements: +4 control "
    "things at a distance, +4 destroy things at a distance. The Invisible "
    "Eye Revealed variant (InVi 29, Pen +0, constant) senses every scrying "
    "up to level 30, whether or not it breaches his Parma. The Gaze of "
    "Others (CrIg 17, Pen +0, 50/day), triggered by it, makes some "
    "inscriptions softly glow."
)
_P_OTHER_ITEMS = (
    "Other work, Items of Quality: a Battle Standard for a Byzantine noble "
    "(+2 Leadership in battle, even for whoever captures it); the Cuirass "
    "of Steel, embossed leather at +4 Soak given to his shield grog "
    "Adrastos (partial leather scale, protection 7, load 3). The Cloak of "
    "Authority (ReMe 24, Pen +0, 12/day, Eye through its clasp) holds Aura "
    "of Rightful Authority, made for a Byzantine noble; he beat a charge of "
    "interfering with mundanes by showing its Lab Text had no Penetration."
)
_P_ARMS = (
    "Three candles of The Light of Fell Disease (PeCo 30, Touch, Mom, Room, "
    "Pen +0, one charge each): lit, they give smallpox to all in the room, "
    "not contagiously; a Stamina + Living Conditions + Wound Penalty stress "
    "roll of 9 resists, and weekly Stamina + Medicine rolls of 9 hold or 15 "
    "improve. The spiral inscriptions can be read by those who know them. "
    "One Sheet of Flame, a bedsheet of Dreams You Shall Not Wake From (CrIg "
    "48, Pen +30, 1 charge): lain on, it fills the room with +20 magical "
    "fire, then +10 natural fire a round. The Convenient Door (ReTe(He) 25, "
    "Pen +0, 1/day), a chalk bag: an outline drawn on a wall or floor opens "
    "a way through wood and stone, not metal, for a Diameter."
)
_P_MAP_BOOK = (
    "The Map of Many Places (In(Re)Im(An) 25, Pen +0, 1/day), a woven map "
    "that reweaves itself to the area as seen from 100 paces up, stopping "
    "at city walls; it cuts the Distance Level of Hermetic Geometry spells "
    "by 1. Greater Numerologist's Book, Bonus +8, holding De Astrologia, "
    "Parapegma and Pros Thrasydaion, a focus for numerological and "
    "astrological casting, with Sense the Hour, The Worldly Halysis (InTe "
    "10, Pen +0, 3/day) giving the paces to an Arcane Connection and "
    "cutting Distance Level by 3, and The Bodily Halysis (InCo 32, Pen +30, "
    "3/day) doing the same through Corpus."
)
_P_IDMON = (
    "Familiar: Idmon the spider, Magic Might 10 (Animal), Size -6, bound in "
    "his mid-fifties; Int -3, Per -2, Pre -5, Com -6, Str -10, Sta +1, Dex "
    "+3, Qik +4. Ambush Predator, Grapple, Loathsome Appearance, Venomous; "
    "True Friend (Petalichus), Piercing Gaze, Envious. Sinister +2, Loyal "
    "(Petalichus) +3. Dodge Init +4, Defense +7; teeth Init +4, Attack +10, "
    "Defense +9, Damage -9; grapple Init +4, Attack +6, Defense +7. Soak "
    "+1. Awareness 4, Brawl 3, Climb 5, Hunt 4, Greek 5, Latin 4, "
    "Penetration 4, Stealth 4, Survival 3, Weaver 5. Powers: Panic of the "
    "Trembling Heart (CrMe 15, 2 points, Init +3), Weaver's Trap of Webs "
    "(CrAn 35, 4 points, Init +1). 1 pawn of Rego in its legs. Cords: gold "
    "2, silver 1, bronze 2; Mental Communication both ways, and Shared "
    "Senses from Idmon to him. A large, frail-looking spider with a bright "
    "patterned carapace, sent out at night to fetch Arcane Connections."
)

PETALICHUS_GAUNTLET: StatBlock = {
    "characteristics": _P_CHARACTERISTICS,
    "confidence": (2, 5),
    "apparent_age": 25,
    "virtues_flaws": [*_P_FIRST, "Planetary Magic", _P_ENEMY],
    "traits": {"Acquisitive": 1, "Decisive": 1, "Hungry for Knowledge": 2},
    "reputations": _P_REPUTATION,
    "abilities": _abilities(
        "Artes Liberales 3+2 (astronomy), Awareness 1 (searching), Bargain 1 "
        "(enchantments), Brawl 1 (knife), Clothiery 1 (shirts), Code of "
        "Hermes 1 (political intrigue), Constantinople Lore 3 (geography), "
        "Finesse 1+2 (precision), Greek 5 (magical terms), Guile 1 (lying to "
        "authority), Intrigue 1 (alliances), Latin 3 (Hermetic usage), "
        "Leadership 1 (magi), Magic Lore 2 (magical traditions), Magic "
        "Theory 4+2 (enchanting items), Verditius Cult Lore 1 (initiations), "
        "Parma Magica 1 (Ignem), Penetration 1 (Ignem), Philosophiae 2 "
        "(ceremonial magic), Weaver 3 (linen)"
    ),
    "arts": arts_from(
        "Cr 0, In 5, Mu 0, Pe 0, Re 7, An 3, Aq 0, Au 0, Co 6, He 3, Ig 5, "
        "Im 0, Me 3, Te 0, Vi 2"
    ),
    "spells": _spells(_PETALICHUS_SPELLS, _P_GAUNTLET),
    "notes": paragraphs(
        "A handsome young man, pale and intense under slick dark hair, "
        "stooped from years at his crafts, dressed finely in clean, geometric "
        "decoration. Sigil: threads that weave each effect, leaving traces "
        "like frayed edges. Votes with a silver wand shaped like a large "
        "needle. Casting tools: outsized threaded needles pinned in his "
        "cuffs, one to a spell, pulled and pierced through a cloth as he "
        "casts. He rarely carries vis unless sure of needing it.",
        _P_COMBAT + " Equipment: good clothes, wizardly robes, workman's "
        "clothes, a loom.",
        _P_SPELL_NOTES,
    ),
}
PETALICHUS_15: StatBlock = {
    "characteristics": _P_CHARACTERISTICS,
    "confidence": (2, 5),
    "warping": (3, 0),
    "apparent_age": 36,
    "virtues_flaws": [
        *_P_FIRST,
        "Items of Quality",
        "Planetary Magic",
        _P_ENEMY,
        "Hubris",
    ],
    "traits": {
        "Acquisitive": 1,
        "Decisive": 1,
        "Hubris (Arrogant)": 2,
        "Hungry for Knowledge": 2,
    },
    "reputations": _P_REPUTATION,
    "abilities": _abilities(
        "Artes Liberales 4+2 (astronomy), Awareness 1 (searching), Bargain 1 "
        "(enchantments), Brawl 1 (knife), Clothiery 2 (shirts), Code of "
        "Hermes 1 (political intrigue), Constantinople Lore 3 (geography), "
        "Finesse 3+2 (precision), Greek 5 (magical terms), Guile 1 (lying to "
        "authority), Intrigue 1 (alliances), Latin 4 (Hermetic usage), "
        "Leadership 1 (magi), Magic Lore 2 (magical traditions), Magic "
        "Theory 4+2 (enchanting items), Verditius Cult Lore 3 (initiations), "
        "Parma Magica 2 (Ignem), Penetration 2 (Ignem), Philosophiae 4 "
        "(ceremonial magic), Weaver 4 (linen)"
    ),
    "arts": arts_from(
        "Cr 15, In 9, Mu 1, Pe 7, Re 7, An 3, Aq 0, Au 0, Co 9, He 3, Ig 5, "
        "Im 0, Me 9, Te 2, Vi 2"
    ),
    "spells": _spells(_PETALICHUS_SPELLS, _P_15),
    "notes": paragraphs(
        "He now wears a long black beard, bound like his hair into cords "
        "with thread and cloth strips, and temper and pride have made him "
        "stern and disagreeable. He shows his work openly, wearing amulets "
        "and rings that hold pawns of vis, usually Rego.",
        "Since his Gauntlet: his first Verditius initiation, and books and "
        "letters on mathematics, geometry and astrology; the Cononites "
        "watch him unseen. His level 8 longevity ritual is a ritual "
        "unbinding and binding of his beard with prepared cords.",
        _P_COMBAT,
        _P_SHEARS,
        _P_LOOM,
        _P_DOOR,
        _P_SPELL_NOTES,
    ),
}
PETALICHUS_30: StatBlock = {
    "characteristics": _P_CHARACTERISTICS,
    "confidence": (2, 15),
    "warping": (4, 17),
    "apparent_age": 43,
    "virtues_flaws": [*_P_FIRST, *_P_LATER, _P_ENEMY],
    "traits": {
        "Acquisitive": 2,
        "Decisive": 1,
        "Hubris (Arrogant)": 3,
        "Hungry for Knowledge": 2,
    },
    "reputations": _P_REPUTATION,
    "abilities": _abilities(
        "Artes Liberales 4+2 (astronomy), Awareness 1 (searching), Brawl 1 "
        "(knife), Clothiery 2 (shirts), Code of Hermes 1 (political "
        "intrigue), Cononites Cult Lore 4 (initiating others), Constantinople "
        "Lore 3 (geography), Finesse 3+2 (precision), Greek 5 (magical "
        "terms), Guile 1 (lying to authority), Intrigue 1 (alliances), Latin "
        "4 (Hermetic usage), Leadership 1 (magi), Magic Lore 2 (magical "
        "traditions), Magic Theory 5+2 (enchanting items), Verditius Cult "
        "Lore 3 (initiations), Parma Magica 3 (Ignem), Penetration 3 "
        "(Ignem), Philosophiae 4 (ceremonial magic), Weaver 4 (linen)"
    ),
    "arts": arts_from(
        "Cr 15, In 13, Mu 1, Pe 10, Re 13, An 3, Aq 0, Au 1, Co 11, He 3, "
        "Ig 5, Im 13, Me 9, Te 9, Vi 9"
    ),
    "spells": _spells(_PETALICHUS_SPELLS, _P_30),
    "notes": paragraphs(
        "Heavier now and bearing himself as an ageing man despite his ritual, "
        "in weighty robes edged with embossed leather and covered in mystical "
        "and mathematical signs. Twilight scar: his fingers are unnaturally "
        "long. He carries pawns of vis to display his wealth. The Sense the "
        "Weight spells and The Unseen Arm are Hermetic Numerology rotes.",
        "Since the last block: initiated into the Cononites, whose trust he "
        "won quickly, turning from the Verditius Mysteries. His initiations "
        "have left him all but unable to use spontaneous magic, so he leans "
        "on casting tablets from his brother Cononites (Covenants p. 89); "
        "assume any reasonable Intellego spell up to fourth magnitude. He "
        "began to experiment with ligatures (Art & Academe p. 68).",
        _P_COMBAT,
        _P_SHEARS,
        _P_DOOR,
        _P_LOOM,
        _P_DISTAFF,
        _P_SPELL_NOTES,
    ),
}
PETALICHUS_45: StatBlock = {
    "characteristics": _P_CHARACTERISTICS,
    "confidence": (2, 15),
    "warping": (6, 7),
    "apparent_age": 54,
    "virtues_flaws": [*_P_FIRST, *_P_LATER, ("True Friend", {"detail": "Idmon"})],
    "traits": {
        "Acquisitive": 2,
        "Decisive": 1,
        "Hubris (Arrogant)": 4,
        "Hungry for Knowledge": 2,
        "Loyal (Idmon)": 3,
    },
    "reputations": _P_REPUTATION,
    "abilities": _abilities(
        "Artes Liberales 4+2 (astronomy), Awareness 1 (searching), Bargain 1 "
        "(enchantments), Brawl 1 (knife), Clothiery 2 (shirts), Code of "
        "Hermes 1 (political intrigue), Cononites Cult Lore 4 (initiating "
        "others), Constantinople Lore 3 (geography), Finesse 3+2 (precision), "
        "Greek 5 (magical terms), Guile 3 (lying to authority), Intrigue 2 "
        "(alliances), Latin 4 (Hermetic usage), Leadership 2 (magi), Magic "
        "Lore 2 (magical traditions), Magic Theory 7+2 (enchanting items), "
        "Verditius Cult Lore 3 (initiations), Parma Magica 4 (Ignem), "
        "Penetration 4 (Ignem), Philosophiae 4 (ceremonial magic), Weaver 4 "
        "(linen)"
    ),
    "arts": arts_from(
        "Cr 15, In 13, Mu 3, Pe 10, Re 13, An 11, Aq 1, Au 2, Co 11, He 13, "
        "Ig 5, Im 13, Me 12, Te 11, Vi 8"
    ),
    "spells": _spells(_PETALICHUS_SPELLS, _P_45),
    "masteries": {
        "Bind Fast": ["Fast Casting"],
        "The Treacherous Cloak": ["Penetration"],
        "Sight of the Transparent Motive": ["Still Casting"],
    },
    "notes": paragraphs(
        "He looks a man of about fifty-five with the authority of years, his "
        "bound beard greying, his hair receding, his brows heavy, hung with "
        "devices and rings of uncertain origin, his talisman, a great book in "
        "a satchel, and Idmon. Twilight scar: unnaturally long fingers. He "
        "keeps Rego vis to boost the Penetration of his few offensive "
        "spells. The Sense the Weight spells, The Unseen Arm, Scribe the "
        "Perfect Circle and Recollection of Memories Never Quite Lived are "
        "rotes.",
        "Since the last block: he spent much of this time making his "
        "numerologist's book and copies for the cult, and overtly offensive "
        "items, and near his seventieth year finally beat Solar Magnus while "
        "both searched Canterbury for an old text. His future is unsure from "
        "here, though the Cononites may use their influence for him.",
        _P_COMBAT,
        _P_IDMON,
        _P_SHEARS,
        _P_DOOR,
        _P_LOOM,
        _P_MAP_BOOK,
        _P_ARMS,
        _P_OTHER_ITEMS,
        _P_DISTAFF,
        _P_SPELL_NOTES,
    ),
}

# Ranulf of Flambeau (pp. 106-115)

_RANULF_SPELLS: dict[str, tuple[str, int]] = {
    "Coat of Prometheus": ("CrIg", 5),
    "Flash of the Scarlet Flames": ("CrIg", 15),
    "Mien of Helios": ("CrIg", 15),
    "Fasting Hearth": ("CrIg", 20),
    "Pilum of Fire": ("CrIg", 20),
    "Self Immolation": ("CrIg", 30),
    "Stockade of Infernos": ("CrIg", 40),
    "Conflagrative Servant": ("CrIg(Mu,Re)", 40),
    "Tales of the Ashes": ("InIg", 5),
    "Enduring Flame": ("MuIg", 10),
    "Boreal Flames": ("MuIg(Pe)", 15),
    "Petite Phoenix": ("MuIg(Re)", 30),
    "Discriminating Flames": ("ReIg", 25),
    "Ward against Heat and Flames": ("ReIg", 25),
    "Ward Against Immolation": ("ReIg", 35),
    "Unified Flame": ("ReIg", 35),
    "Transmutation of Fire": ("MuTe(Ig,He)", 40),
    "Scales of the Magical Weight": ("InVi", 5),
    "Sense the Nature of Vis": ("InVi", 5),
    "Wizard's Expansion Ignem": ("MuVi", 25),
    "Group Wizard's Boost Ignem": ("MuVi", 30),
    "Wizard's Boost Ignem": ("MuVi", 30),
    "Wizard's Communion": ("MuVi", 30),
    "Wizard's Reach Ignem": ("MuVi", 30),
    "Wizard's Boost (Vim)": ("MuVi", 35),
    "Wind of Mundane Silence": ("PeVi", 40),
    "The Patient Spell": ("ReVi", 20),
    "Maintain the Demanding Spell": ("ReVi", 30),
    "Opening the Intangible Tunnel": ("ReVi", 40),
    "Gather Essence of the Beast": ("ReVi", 15),
}
_R_GAUNTLET = (
    "Coat of Prometheus; Flash of the Scarlet Flames; Fasting Hearth; "
    "Pilum of Fire:4; Tales of the Ashes; Enduring Flame; Boreal Flames; "
    "The Patient Spell; Scales of the Magical Weight; Sense the Nature of Vis"
)
_R_15 = _R_GAUNTLET + "; Mien of Helios; Stockade of Infernos"
_R_30 = _R_15 + (
    "; Ward against Heat and Flames; Wizard's Boost Ignem; Gather Essence of the Beast"
)
_R_45 = _R_30 + (
    "; Conflagrative Servant; Petite Phoenix; Discriminating Flames; "
    "Wizard's Expansion Ignem; Group Wizard's Boost Ignem; "
    "Wizard's Communion; Wizard's Reach Ignem; Maintain the Demanding Spell"
)
_R_60 = _R_45.replace("; Gather Essence of the Beast", "") + (
    "; Self Immolation; Ward Against Immolation; Unified Flame; "
    "Transmutation of Fire; Wizard's Boost (Vim); Wind of Mundane Silence; "
    "Opening the Intangible Tunnel"
)
_R_CHARACTERISTICS = characteristics(2, -2, 1, 0, 1, 2, 1, 1)
_R_MASTERY = {
    "Pilum of Fire": ["Fast Casting", "Defense", "Multiple Casting", "Penetration"]
}
_R_FIRST = [
    "The Gift",
    "Hermetic Magus",
    ("Major Magical Focus", {"focus": "unnatural fires"}),
    vf_art("Affinity with {art}", "Ignem"),
    "Method Caster",
    vf_art("Puissant {art}", "Ignem"),
    vf_puissant("Magic Theory"),
    vf_puissant("Penetration"),
    ("Deficient Technique", {"technique": "Intellego"}),
    "Tormenting Master",
    "Poor Eyesight",
]
_R_CIRCUMSTANCE = (
    "Deleterious Circumstances",
    {"circumstance": "spells of Range Sight or Eye"},
)
_R_LOOK = (
    "A near-constant squint at a world he sees poorly, a reddened face, the "
    "short hair round it bleached by close work over hot fires; ordinary in "
    "build, in layers of wool and leather against the heat."
)
_R_SIGIL = (
    "Casting sigil: brightness; what his spells touch pales, and his fires "
    "burn unusually bright. Voting sigil: an evil-looking dagger, which "
    "embarrasses him more as he ages."
)
_R_COMBAT = (
    "Combat: fist Init +1, Attack +4, Defense +4, Damage +1; dodge Init +1, "
    "Defense +5. Soak +2."
)
_R_SPELL_NOTES = (
    "Spell notes: The Patient Spell here is level 20; it holds another spell "
    "of up to its level + 15 (errata) until released, with an Int + "
    "Concentration roll of 9 to cast alongside it, and he uses it to cast "
    "Boreal Flames with Pilum of Fire. Boreal Flames turns a fire of up to "
    "+15 damage to cold for a moment."
)
_R_GENERAL = (
    "This block prints General spells at set levels the sheet does not "
    "hold: Wizard's Communion 30, Wind of Mundane Silence 40, Opening the "
    "Intangible Tunnel 40."
)
_R_LAB = (
    "Laboratory: his wooden lab is opened as a compound device through its "
    "limestone fireplace, 12 pawns, 7 filled, giving Excessive Heating, "
    "Excessive Lighting, Lesser Feature (Ignem specialization) and Highly "
    "Organized without Upkeep or Safety cost (Covenants pp. 113, 115). Eyes "
    "of the Acolyte (InIg 19 by the errata, Touch, Room, constant) detects "
    "stray fires larger than a lantern. Laboratory that has Learned from "
    "Experience (PeIg 33 by the errata, Special Range, 24/day), triggered "
    "by it, puts them out, up to +20 damage. Facade of Pentecost (Cr(Re)Ig "
    "51 by the errata, Special Range, 50/day, maintains concentration) "
    "calls up to ten fuelless flames anywhere in the lab, +10 damage each."
)
_R_STAFF_BASE = (
    "Talisman: the Staff of Ranulf, a walking-stick length of coiled ash, "
    "hazel and oak bound in iron, with lead and silver tracery and a tiny "
    "ruby in a silver ring, no use as a weapon. Attunements: +6 fire-related "
    "effects, +4 control at a distance, +2 repel things, +3 divination. "
    "Topiary of Flames (ReIg 44, Pen +0, 12/day, maintains concentration) "
    "reshapes a fire of up to 100 Individuals, without adding volume, into "
    "walls, bridges and stairs. Flames of Stone (MuIg(Te) 38, Pen +0, "
    "maintains concentration; 3/day in its header, 6 uses in its "
    "calculation) makes a fire of up to ten Individuals hard as stone. "
    "Shadow of Spring Times Departed (Cr(Mu)He 5, Pen +0, 1/day) slowly "
    "regrows its wood in sun and water. Surfeit of Fuel (CrHe 27, Pen +0, "
    "3/day) conjures several large trees' worth of dry wood."
)
_R_STAFF_LATE = (
    "Opened with 10 more pawns, leaving 4 free, with +4 destroy things at a "
    "distance and +4 affect dead wood. Shriek of the Impending Shafts (InHe "
    "16, Pen +0, 2/day, maintains concentration). Defense of the Roaring "
    "Furnace (CrIg 58, Pen +0, unlimited) burns any fast wooden thing "
    "within a pace of the holder with +35 fire."
)
_R_RIBBON = (
    "Ribbon of Arcane Preservation, an 18-inch silk ribbon made from "
    "hoplites' notes, 3 pawns. Preserved Connection (CrVi 29, Pen +0, "
    "constant): tied round an object, its Arcane Connections decay as if "
    "two steps longer, hours to weeks and days to months, under the book's "
    "new CrVi guidelines (p. 113)."
)

RANULF_GAUNTLET: StatBlock = {
    "characteristics": _R_CHARACTERISTICS,
    "confidence": (1, 3),
    "apparent_age": 24,
    "virtues_flaws": [
        *_R_FIRST,
        "Mastered Spells",
        (
            "Deleterious Circumstances",
            {"circumstance": "casting spells with Range Sight or Eye"},
        ),
    ],
    "traits": {
        "Inquisitive": 2,
        "Sensitive to Insult": 2,
        "Belligerent": 1,
        "Brave": 1,
        "Loquacious": -1,
    },
    "reputations": {"Did not pass gauntlet (Flambeau)": 3},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial casting), Athletics 2 (running), "
        "Awareness 1 (searching), Brawl 3 (dodge), Carouse 2 (staying sober), "
        "Guile 1 (lying to strangers), Concentration 1 (spells), Dead "
        "Language: Latin 4 (Hermetic usage), Living Language: Castillian 5 "
        "(candles), Magic Theory 4+2 (inventing spells), Organization Lore: "
        "Order of Hermes 1 (personalities), Parma Magica 1 (Corpus), "
        "Penetration 2+2 (Ignem), Profession: Candle Maker 2 (speed), Stealth "
        "2 (hide)"
    ),
    "arts": arts_from(
        "Cr 5, In 0, Mu 5, Pe 4, Re 4, An 0, Aq 0, Au 0, Co 0, He 0, Ig 10+3, "
        "Im 0, Me 0, Te 0, Vi 6"
    ),
    "spells": _spells(_RANULF_SPELLS, _R_GAUNTLET),
    "masteries": _R_MASTERY,
    "notes": paragraphs(_R_LOOK, _R_SIGIL, _R_COMBAT, _R_SPELL_NOTES),
}
RANULF_15: StatBlock = {
    "characteristics": _R_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (1, 0),
    "apparent_age": 37,
    "virtues_flaws": [*_R_FIRST, "Mastered Spells", _R_CIRCUMSTANCE, "Miles"],
    "traits": {
        "Inquisitive": 2,
        "Sensitive to Insult": 2,
        "Brave": 1,
        "Loquacious": -1,
    },
    "reputations": {
        "Did not pass gauntlet (Flambeau)": 3,
        "Aspiring Hoplite (Quaesitors)": 2,
    },
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial casting), Athletics 2 (running), "
        "Awareness 1 (searching), Brawl 3 (dodge), Carouse 1 (staying sober), "
        "Guile 1 (lying to strangers), Code of Hermes 1 (Wizard's Marches), "
        "Concentration 3 (spells), Dead Language: Latin 4 (Hermetic usage), "
        "Finesse 2 (Ignem), Living Language: Castillian 5 (candles), Magic "
        "Theory 6+2 (inventing spells), Organization Lore: Order of Hermes 1 "
        "(personalities), Parma Magica 3 (Corpus), Penetration 4+2 (5) "
        "(Ignem), Philosophiae 2 (ritual magic), Profession: Candle Maker 2 "
        "(speed), Stealth 2 (hide)"
    ),
    "arts": arts_from(
        "Cr 11, In 3, Mu 7, Pe 4, Re 8, An 0, Aq 0, Au 0, Co 0, He 5, Ig 14+3, "
        "Im 0, Me 0, Te 0, Vi 9"
    ),
    "spells": _spells(_RANULF_SPELLS, _R_15),
    "masteries": _R_MASTERY,
    "notes": paragraphs(
        _R_LOOK,
        _R_SIGIL,
        "Vis: 2 pawns of Ignem as a pouch of ashes that grow hot each sunset.",
        "Since his Gauntlet: study, and fending off his former mentor's "
        "political attacks. He swore the code of Garus and joined the Milites "
        "(Houses of Hermes: Societates p. 31) from belief and for allies "
        "against her. He enchanted his wooden laboratory against fire: a "
        "season to open it, one on Eyes of the Acolyte, three on Facade of "
        "Pentecost, two on Laboratory that has Learned from Experience, one "
        "integrating. He invented Mien of Helios in one season and Stockade "
        "of Infernos in three, and spent two getting his longevity ritual "
        "from another magus. He gained 180 xp in Abilities and 160 in Arts, "
        "plus 16 from his Ignem affinity.",
        _R_COMBAT,
        _R_LAB,
        _R_SPELL_NOTES,
    ),
}
RANULF_30: StatBlock = {
    "characteristics": _R_CHARACTERISTICS,
    "confidence": (2, 4),
    "warping": (3, 5),
    "apparent_age": 38,
    "virtues_flaws": [*_R_FIRST, _R_CIRCUMSTANCE, "Miles"],
    "traits": {
        "Inquisitive": 2,
        "Sensitive to Insult": 1,
        "Brave": 2,
        "Loquacious": -1,
    },
    "reputations": {
        "In feud with Parens (tribunal)": 3,
        "Did not pass gauntlet (Flambeau)": 1,
        "Hoplite (Quaesitors)": 1,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial casting), Athletics 2 (running), "
        "Awareness 1 (searching), Brawl 3 (dodge), Carouse 1 (staying sober), "
        "Guile 1 (lying to strangers), Code of Hermes 1 (Wizard's Marches), "
        "Concentration 4 (spells), Dead Language: Latin 5 (Hermetic usage), "
        "Finesse 3 (Ignem), Living Language: Castillian 5 (candles), Magic "
        "Theory 7+2 (5) (inventing spells), Organization Lore: Order of "
        "Hermes 1 (personalities), Parma Magica 4 (Corpus), Penetration 4+2 "
        "(5) (Ignem), Philosophiae 2 (ritual magic), Profession: Candle "
        "Maker 2 (speed), Stealth 2 (hide)"
    ),
    "arts": arts_from(
        "Cr 13, In 8, Mu 9, Pe 4, Re 8, An 0, Aq 1, Au 2, Co 4, He 7, Ig 18+3, "
        "Im 0, Me 5, Te 6, Vi 11"
    ),
    "spells": _spells(_RANULF_SPELLS, _R_30),
    "masteries": _R_MASTERY,
    "notes": paragraphs(
        _R_LOOK,
        _R_SIGIL,
        "Vis: 5 pawns of Creo as seeds in a pouch at his neck, which bud "
        "vis-less copies of themselves about monthly; 2 pawns of Ignem as "
        "ashes on his belt that grow hot each sunset. This block's Virtues "
        "leave out Mastered Spells, though he keeps his Mastery.",
        "Since the last block: still keen on martial magic, he is warming to "
        "peaceful uses of Ignem. A season each to learn Ward Against Heat "
        "and Flames, invent Wizard's Boost Ignem from notes, and invent "
        "Gather Essence of the Beast. A season to open his staff, one to "
        "attune it, two on Topiary of Flames, three on Flames of Stone, one "
        "each on Surfeit of Fuel and Shadow of Spring Times Departed. He "
        "gained 130 xp in Abilities and 230 in Arts, plus 22 from affinity.",
        _R_COMBAT,
        _R_LAB,
        _R_STAFF_BASE,
        _R_SPELL_NOTES,
    ),
}
RANULF_45: StatBlock = {
    "characteristics": _R_CHARACTERISTICS,
    "confidence": (2, 4),
    "warping": (4, 15),
    "apparent_age": 40,
    "virtues_flaws": [*_R_FIRST, "Mastered Spells", _R_CIRCUMSTANCE, "Miles"],
    "traits": {
        "Inquisitive": 2,
        "Sensitive to Insult": 1,
        "Brave": 2,
        "Loquacious": -1,
    },
    "reputations": {
        "In feud with Parens (tribunal)": 3,
        "Did not pass gauntlet (Flambeau)": 1,
        "Hoplite (Order)": 1,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial casting), Athletics 2 (running), "
        "Awareness 1 (searching), Brawl 3 (dodge), Carouse 1 (staying sober), "
        "Guile 1 (lying to strangers), Code of Hermes 2 (Wizard's Marches), "
        "Concentration 4 (spells), Dead Language: Latin 5 (Hermetic usage), "
        "Finesse 3 (Ignem), Living Language: Castillian 5 (candles), Magic "
        "Theory 8+2 (inventing spells), Organization Lore: Order of Hermes 1 "
        "(personalities), Parma Magica 5 (Corpus), Penetration 4+2 (5) "
        "(Ignem), Philosophiae 2 (ritual magic), Profession: Candle Maker 2 "
        "(speed), Stealth 2 (hide), Teaching 2 (apprentices)"
    ),
    "arts": arts_from(
        "Cr 13, In 9, Mu 11, Pe 8, Re 9, An 5, Aq 5, Au 5, Co 5, He 10, Ig "
        "21+3, Im 5, Me 5, Te 6, Vi 16"
    ),
    "spells": _spells(_RANULF_SPELLS, _R_45),
    "masteries": _R_MASTERY,
    "notes": paragraphs(
        _R_LOOK,
        _R_SIGIL,
        "Twilight scar: nearby fires lean straight away from him as if he "
        "breathed a slight breeze; smoke does not.",
        "Vis: 6 pawns of Vim moved into a ring on his right hand; 3 of Ignem "
        "as ashes on his belt that grow hot each sunset; 2 of Creo as seeds "
        "at his neck that bud vis-less copies about monthly; 2 of Muto as "
        "cocoons that shift colour over minutes.",
        "Since the last block: his power now brings the hoplite's duties he "
        "once wanted, when he has other interests. His mentor no longer "
        "denies he is a magus, but the feud goes on. A season on the Ribbon "
        "from notes; a season each learning Maintain the Demanding Spell, "
        "Wizard's Reach and Wizard's Communion from notes; a season each "
        "inventing Petite Phoenix and Discriminating Flames, two each on "
        "Conflagrative Servant and Wizard's Expansion; a season reopening his "
        "talisman. He gained 80 xp in Abilities and 240 in Arts, plus 22 from "
        "affinity.",
        _R_COMBAT,
        _R_LAB,
        _R_STAFF_BASE,
        _R_RIBBON,
        _R_SPELL_NOTES,
        "This block prints Wizard's Communion at level 30, a General spell "
        "whose level the sheet does not hold. Conflagrative Servant is "
        "Cr(Re)Ig 45 on p. 111, Cr(Mu,Re)Ig 40 here, and Petite Phoenix ReIg "
        "on p. 112, Mu(Re)Ig here.",
    ),
}
RANULF_60: StatBlock = {
    "characteristics": _R_CHARACTERISTICS,
    "confidence": (2, 6),
    "warping": (5, 20),
    "apparent_age": 45,
    "virtues_flaws": [*_R_FIRST, "Mastered Spells", _R_CIRCUMSTANCE, "Miles"],
    "traits": {"Inquisitive": 2, "Brave": 2, "Loquacious": -1},
    "reputations": {"Hoplite (Order)": 1, "Deficient in Intellego (Flambeau)": 1},
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial casting), Athletics 2 (running), "
        "Awareness 1 (searching), Brawl 3 (dodge), Carouse 1 (staying sober), "
        "Guile 1 (lying to strangers), Code of Hermes 2 (Wizard's Marches), "
        "Concentration 4 (spells), Dead Language: Latin 5 (Hermetic usage), "
        "Finesse 3 (Ignem), Leadership 1 (grogs), Living Language: Castillian "
        "5 (candles), Magic Theory 8+2 (inventing spells), Organization "
        "Lore: Order of Hermes 1 (personalities), Parma Magica 6 (Corpus), "
        "Penetration 4+2 (5) (Ignem), Philosophiae 2 (ritual magic), "
        "Profession: Candle Maker 2 (speed), Stealth 2 (hide), Teaching 2 "
        "(apprentices)"
    ),
    "arts": arts_from(
        "Cr 14, In 10, Mu 12, Pe 10, Re 10, An 5, Aq 5, Au 5, Co 5, He 10, Ig "
        "25+3, Im 5, Me 5, Te 8, Vi 18"
    ),
    "spells": _spells(_RANULF_SPELLS, _R_60),
    "masteries": _R_MASTERY,
    "notes": paragraphs(
        _R_LOOK,
        _R_SIGIL,
        "Twilight scar: nearby fires lean straight away from him as if he "
        "breathed a slight breeze; smoke does not.",
        "Vis: 8 pawns of Vim in a ring on his right hand; 8 of Ignem as ashes "
        "on his belt that grow hot each sunset; 4 of Muto as snakeskins.",
        "Since the last block: he took an apprentice, a talent with Ignem, 14 "
        "seasons of training and one of searching. His mentor passed into "
        "Twilight very old, and he gave the castellan of Castra Solis a "
        "fixed Arcane Connection to himself, made by his apprentice, to fill "
        "her place (Houses of Hermes: Societates p. 13). A certamen at a "
        "Flambeau tournament exposed his weak Intellego. He now explores "
        "fires that are Arcane Connections to one another. Two seasons each "
        "on Shriek of the Impending Shafts and Defense of the Roaring "
        "Furnace, one on the Chest; a season each learning Wind of Mundane "
        "Silence and Opening the Intangible Tunnel from notes; inventing "
        "Self Immolation (1), Ward Against Immolation (2), Unified Flame "
        "(1), Wizard's Boost (Vim) (3), Transmutation of Fire (3). He gained "
        "35 xp in Abilities and 175 in Arts, plus 35 from affinity.",
        "He and his apprentice speak through Discourse of Glowing Tongues "
        "(ReIg 10), cast spontaneously on fires joined by Unified Flame: the "
        "apprentice kindles one each sunset from a coal in the Chest. Self "
        "Immolation burns the caster too, so he casts Ward Against "
        "Immolation first and must renew it in time. Petite Phoenix and "
        "Transmutation of Fire together move doors and sections of wall. The "
        "block calls that spell Transformation of Fire; it is the MuTe "
        "spell of p. 113. Conflagrative Servant is Cr(Re)Ig 45 on p. 111, "
        "Cr(Mu,Re)Ig 40 in the blocks, and Petite Phoenix ReIg there and "
        "Mu(Re)Ig here. This block does not list Gather Essence of the Beast.",
        _R_COMBAT,
        _R_LAB,
        _R_STAFF_BASE,
        _R_STAFF_LATE,
        _R_RIBBON,
        "Chest of the Ember Seed, an apple-sized stone box lined with fired "
        "clay and strapped shut, 4 pawns. Bed of the Resting Coal (CrIg 34, "
        "Pen +0, constant) keeps what is in it red-hot, so coals stay Arcane "
        "Connections to their fire, for Months. It grows very hot and must "
        "be cooled.",
        _R_SPELL_NOTES,
        _R_GENERAL,
    ),
}

# Scipio of Merinita (pp. 116-126)

_SCIPIO_SPELLS: dict[str, tuple[str, int]] = {
    "Bridge of Gnomes": ("CrAu", 15),
    "Rainbow Bridge": ("MuAu", 20),
    "Eyes of the Cat": ("MuCo(An)", 5),
    "High Tree or Small Boulder": ("MuCo", 20),
    "Curse of the Unruly Tongue": ("ReCo", 5),
    "Follower's Bane": ("ReCo", 10),
    "Jump of the Lynx": ("ReCo", 20),
    "How God Created Them": ("MuHe(An)", 25),
    "Everlasting Music": ("ReHe(An)", 15),
    "Summer's Blessing": ("MuIg(Te)", 30),
    "Smoke of Escaping": ("CrIm", 5),
    "Book of Images": ("CrIm", 15),
    "Told Story": ("CrIm", 20),
    "Cage of Bronze": ("CrIm", 30),
    "Phantasmal Horse": ("CrIm", 30),
    "Story of Legend": ("CrIm", 35),
    "Doppelganger": ("CrIm(Me)", 40),
    "Image of the Lady": ("CrIm(Me)", 40),
    "Garden of Eden": ("CrIm", 45),
    "Traveler's Foresight": ("InIm", 5),
    "Faerie Flute": ("MuIm", 5),
    "Aura of the Simple Bard": ("MuIm", 15),
    "Rainbow Fire": ("MuIm", 15),
    "Image Phantom": ("MuIm", 20),
    "Safe Haven": ("MuIm", 20),
    "Ogre's Stench": ("MuIm", 30),
    "Blessing the Merchant's Lineage": ("MuIm", 35),
    "Servant of Fire": ("MuIm(Ig,Me)", 45),
    "Hiding the Ill-Bred Bard": ("PeIm", 15),
    "Invisible Arms": ("PeIm(Cr)", 25),
    "Color Explosion": ("ReIm", 15),
    "The Generous Patron": ("MuMe", 15),
    "Stolen Moments": ("PeMe", 35),
    "Sinister Road": ("ReMe", 20),
    "Dancing Mania": ("ReMe", 30),
    "Endless Laughter": ("ReMe", 30),
}
_S_GAUNTLET = (
    "Eyes of the Cat; Curse of the Unruly Tongue; Jump of the Lynx; Told "
    "Story; Aura of the Simple Bard; Faerie Flute; Rainbow Fire; Image "
    "Phantom; Hiding the Ill-Bred Bard"
)
_S_15 = _S_GAUNTLET + (
    "; Follower's Bane; Everlasting Music; Book of Images; Traveler's "
    "Foresight; Color Explosion; The Generous Patron"
)
_S_30 = _S_15 + (
    "; Smoke of Escaping; Phantasmal Horse; Story of Legend; Servant of Fire"
)
_S_45 = _S_30 + "; Cage of Bronze; Doppelganger; Garden of Eden"
_S_60 = _S_45 + (
    "; Summer's Blessing; Blessing the Merchant's Lineage; Invisible Arms; "
    "Dancing Mania"
)
_S_75 = _S_60 + (
    "; Bridge of Gnomes; Rainbow Bridge; Safe Haven; Stolen Moments; Sinister Road"
)
_S_90 = _S_75 + (
    "; High Tree or Small Boulder; How God Created Them; Image of the Lady; "
    "Ogre's Stench; Endless Laughter"
)
_S_CHARACTERISTICS = characteristics(1, 0, 2, 2, -2, 0, 2, 0)
_S_75_CHARACTERISTICS = characteristics(1, -1, 2, 2, -2, 0, 2, -1)
_S_90_CHARACTERISTICS = characteristics(1, -1, 2, 2, -2, -1, 2, -1)
_S_FIRST = [
    "The Gift",
    "Hermetic Magus",
    "Gentle Gift",
    ("Strong Faerie Blood", {"blood": "sidhe"}),
    vf_art("Affinity with {art}", "Imaginem"),
    vf_ability("Enchanting {ability}", "Music"),
    "Faerie Magic",
    "Free Expression",
    ("Performance Magic", {"ability": "Music"}),
    "Plagued by Supernatural Entity",
    ("True Love (Major)", {"detail": "Vinella"}),
    "Careless Sorcerer",
    "Faerie Upbringing",
    ("Lesser Malediction", {"detail": "iron burns like fire"}),
    "Meddler (Minor)",
]
_S_15_VF = [*_S_FIRST, "Spell Timing", "Weird Magic"]
_S_30_VF = [
    *_S_15_VF,
    "Glamour",
    ("Major Magical Focus", {"focus": "Glamour"}),
    ("Vulnerable Magic", {"condition": "iron, Personal"}),
]
_S_TRAITS = {"Meddler": 3, "Wanderlust": 3, "Carefree": 2, "Brave": 1}
_S_LOOK = (
    "An ever-smiling bard with red hair, pointed ears and odd amber eyes; "
    "his sharp face sometimes seems a fox's. He wears motley with "
    "instruments at his belt, and a hat full of bright feathers from faerie "
    "birds."
)
_S_MAGIC = (
    "Performance Magic: singing and playing replace his words and gestures "
    "(The Mysteries: Revised Edition p. 29), and he holds concentration "
    "while performing with no roll."
)
_S_LEVELS = (
    "Where he knows them, the blocks print Faerie Flute at level 5 (p. 125 "
    "has 4), Everlasting Music at 15 (p. 124 has 20), Rainbow Bridge at 20 "
    "(p. 122 has 30) and Servant of Fire at 35 (p. 125 and the errata have "
    "45). Rainbow Fire has no description in the book."
)
_S_GLAMOUR = (
    "Glamour (Houses of Hermes: Mystery Cults pp. 101-102): his illusions "
    "are more than images, stopped by Parma, able to hurt and move things, "
    "and answering only to Imaginem spells; Cage of Bronze, Phantasmal "
    "Horse, Doppelganger, Garden of Eden and Servant of Fire are such "
    "spells. His Twilight gave him the focus on it."
)
_S_LYRE = (
    "Talisman: The Eternally Changing Lyre, of cinnamon wood by a great "
    "French maker, with a magnet and mercury in a glass stone on its face; "
    "+3 to Music rolls; 16 pawns to open, 7 for effects. Attunements: +4 "
    "Imaginem, +5 Muto, +2 Rego. Invisible Musician (ReAn 5, Pen +0, "
    "12/day, maintains concentration; 12 levels in all) plays as he wills. "
    "Unaging Wood (MuHe 5, Pen +0, constant; 14 levels in all) makes it "
    "hard and flexible as sheet metal, -1 to Music rolls. Dance Horror "
    "(ReMe 35, Pen +0, 12/day; 39 levels in all) dances a target until "
    "Fatigue or the Sun runs out, a Stamina roll of 6 each round or lose a "
    "level."
)
_S_FELIX = (
    "Familiar: Felix the Lucky Fox, a Magic Animal of Might 10 (Imaginem), "
    "Size -2, saved by Scipio in Paris from demons' lures when his "
    "wanderings there had weakened him. Int +2, Per 0, Pre +2, Com +3, Str "
    "-3, Sta 0, Dex +2, Qik +4. Magical Friend, Great Quickness, Luck, "
    "Perfect Balance, Puissant Guile, Self-Confident, Well-Traveled; "
    "Wanderlust, Greedy, Nocturnal. Fox +3, Wanderlust +5, Greedy +3, "
    "Carefree +2. Bite Init +4, Attack +5, Defense +7, Damage -2. Soak 0. "
    "Confidence 2 (5). Powers: Perfect Liar (4 points, Init +1, MuCo 20), "
    "+3 to Guile; Grant Luck (5 points, Init -6, Ritual), gives the Luck "
    "Virtue; Human Form (1 point, Init +2, MuCo 20), a red-bearded man with "
    "green eyes. 2 pawns of Imaginem in his twisted tail. Bond: bronze +1, "
    "silver +2, gold +2. Abilities: Athletics 3, Area Lore (Normandy) 3, "
    "Artes Liberales 1, Awareness 3, Bargain 3, Brawl 1, Carouse 3, Charm "
    "3, Folk Ken 3, Guile 5+2, High French 5, Hunt 3, Latin 4, Legerdemain "
    "3, Magic Lore 3, Magic Theory 2, Music 3, Stealth 3, Survival 3."
)
_S_FELIX_15 = (
    "Felix fifteen years on: Improved Abilities x4; Artes Liberales 2, Guile "
    "5+2 (5), Magic Theory 4."
)
_S_FELIX_30 = (
    "Felix thirty years on: Improved Abilities x5, Personal Power x2; Guile "
    "6+2, Magic Theory 5. New power Sight Beyond Sight (1 point, InIm 30): "
    "all five senses reach as far as he can see. Familiar power: Shared "
    "Senses."
)
_S_FELIX_45 = (
    "Felix forty-five years on: Improved Abilities x6; Carouse 4, Magic "
    "Lore 4. Bond: bronze +1, silver +3, gold +3."
)
_S_FELIX_60 = (
    "Felix sixty years on: Improved Abilities x8; Athletics 4, Folk Ken 4, "
    "Guile 7+2, Legerdemain 4, Magic Theory 6."
)
_S_BAG = (
    "The Bottomless Bag, of dragon leather, a lesser device of 4 pawns. Bag "
    "without Bottom (MuIm 20 by the errata, T: Ind, Pen +0, constant): its "
    "Glamour makes room for over 200 liters, weight unchanged; you may have "
    "to climb in to find anything."
)
_S_ACTIVITY_NOTE = "All his spells were made in lab seasons, some by experiment."

SCIPIO_GAUNTLET: StatBlock = {
    "characteristics": _S_CHARACTERISTICS,
    "confidence": (1, 3),
    "apparent_age": 20,
    "virtues_flaws": _S_FIRST,
    "traits": _S_TRAITS,
    "reputations": {"Trouvere (Artist)": 0},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Athletics 1 (running), "
        "Awareness 1 (spotting), Bargain 1 (music payment), Brawl 1 "
        "(dodging), Carouse 1 (drinking songs), Charm 1 (first impressions), "
        "Concentration 1 (spell concentration), Enchanting Music 2 "
        "(friendship), Etiquette 1 (faeries), Faerie Lore 1 (faerie forests), "
        "Faerie Magic 1 (spells), Finesse 1 (Imaginem), Folk Ken 1 (faeries), "
        "Guile 1 (fast talk), High French 5 (music), French Kingdom Lore 1 "
        "(towns), House Merinita Lore 1 (initiations), Intrigue 1 "
        "(rumormongering), Latin 4 (texts), Legerdemain 1 (“magic” tricks), "
        "Magic Lore 1 (forests), Magic Theory 3 (spells), Music 2 (lyre), "
        "Order of Hermes Lore 1 (magi), Parma Magica 1 (Vim), Penetration 1 "
        "(Imaginem), Philosophiae 1 (ceremonial magic), Profession: Trouvere "
        "1 (5) (love songs), Second Sight 1 (faeries), Stealth 1 (sneak), "
        "Survival 1 (finding routes), Swim 1 (rivers)"
    ),
    "arts": arts_from(
        "Cr 5, In 2, Mu 3, Pe 2, Re 6, An 0, Aq 0, Au 0, Co 6, He 1, Ig 0, "
        "Im 11, Me 0, Te 1, Vi 0"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_GAUNTLET),
    "notes": paragraphs(
        _S_LOOK,
        "Casting sigil: a red fox that appears and acts in his spells. Voting "
        "sigil: a red wand with a wooden fox's head.",
        _S_MAGIC,
        _S_LEVELS,
        "Combat: dodging Init 0, Defense +2. Soak +0. Equipment: bard's "
        "outfit, lyre, flute, bag of “magic” tricks.",
    ),
}
SCIPIO_15: StatBlock = {
    "characteristics": _S_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (3, 0),
    "apparent_age": 20,
    "virtues_flaws": _S_15_VF,
    "traits": _S_TRAITS,
    "reputations": {"Trouvere (Artist)": 2, "Faerie Bard (France)": 1},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Athletics 1 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 1 "
        "(dodging), Carouse 2 (drinking songs), Charm 1 (first impressions), "
        "Concentration 2 (spell concentration), Enchanting Music 3 "
        "(friendship), Etiquette 2 (faeries), Faerie Lore 2 (faerie forests), "
        "Faerie Magic 3 (spells), Finesse 1 (Imaginem), Folk Ken 2 (faeries), "
        "Guile 1 (fast talk), High French 5 (music), French Kingdom Lore 1 "
        "(towns), House Merinita Lore 2 (initiations), Intrigue 1 "
        "(rumormongering), Latin 4 (texts), Legerdemain 1 (“magic” tricks), "
        "Magic Lore 1 (forests), Magic Theory 3 (spells), Music 3 (lyre), "
        "Order of Hermes Lore 1 (magi), Parma Magica 3 (Vim), Penetration 1 "
        "(Imaginem), Philosophiae 1 (ceremonial magic), Profession: Trouvere "
        "2 (love songs), Second Sight 1 (faeries), Stealth 1 (sneak), "
        "Survival 1 (finding routes), Swim 1 (rivers)"
    ),
    "arts": arts_from(
        "Cr 9, In 7, Mu 8, Pe 5, Re 9, An 2, Aq 2, Au 2, Co 4, He 4, Ig 2, "
        "Im 14, Me 7, Te 2, Vi 2"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_15),
    "notes": paragraphs(
        _S_LOOK + " He does not seem to age. Twilight scar: his hair always "
        "stirs like a hero's in an old tale.",
        "Since his Gauntlet: two seasons initiating Spell Timing and Weird "
        "Magic, two building his lab, eight on spells; 360 xp from 12 full "
        "years. 170 xp to Abilities (425 total), 190 to Arts (305 total). "
        + _S_ACTIVITY_NOTE,
        "Combat: dodging Init 0, Defense +2. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
    ),
}
SCIPIO_30: StatBlock = {
    "characteristics": _S_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (4, 13),
    "apparent_age": 20,
    "virtues_flaws": _S_30_VF,
    "traits": _S_TRAITS,
    "reputations": {
        "Trouvere (Artist)": 3,
        "Faerie Bard (France)": 2,
        "Troublesome Faerie Guy (Order of Hermes)": 1,
    },
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Athletics 1 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 1 "
        "(dodging), Carouse 2 (drinking songs), Charm 2 (first impressions), "
        "Concentration 2 (spell concentration), Divine Lore 1 (angels), "
        "Enchanting Music 3 (friendship), Etiquette 2 (faeries), Faerie Lore "
        "3 (faerie forests), Faerie Magic 4 (spells), Finesse 2 (Imaginem), "
        "Folk Ken 2 (faeries), Guile 2 (fast talk), High French 5 (music), "
        "French Kingdom Lore 2 (towns), House Merinita Lore 3 (initiations), "
        "Intrigue 1 (rumormongering), Latin 4 (texts), Legerdemain 2 "
        "(“magic” tricks), Magic Lore 2 (forests), Magic Theory 3 (15) "
        "(spells), Music 3 (lyre), Order of Hermes Lore 1 (magi), Parma "
        "Magica 4 (Vim), Penetration 2 (Imaginem), Philosophiae 1 (ceremonial "
        "magic), Profession: Trouvere 2 (love songs), Second Sight 2 "
        "(faeries), Stealth 1 (sneak), Survival 2 (finding routes), Swim 1 "
        "(rivers)"
    ),
    "arts": arts_from(
        "Cr 9, In 7, Mu 10, Pe 5, Re 9, An 4, Aq 4, Au 4, Co 5, He 4, Ig 11, "
        "Im 17, Me 11, Te 4, Vi 4"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_30),
    "notes": paragraphs(
        _S_LOOK + " He does not seem to age, and a red fox rides his shoulder.",
        "Twilight scars: his hair stirs like a hero's in an old tale; at "
        "times his plain illusions turn real as Glamour, but only when that "
        "goes badly for him.",
        "Since the last block: four seasons on his talisman, one finding and "
        "one binding a familiar, two on Mysteries (Glamour, Vulnerable "
        "Magic), seven on spells. An experiment gave 15 xp in Magic Theory. "
        "330 xp from 11 full years. 150 xp to Abilities (575 total), 195 to "
        "Arts (500 total). " + _S_ACTIVITY_NOTE,
        "Combat: dodging Init 0, Defense +2. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
        _S_GLAMOUR,
        _S_LYRE,
        _S_FELIX,
    ),
}
SCIPIO_45: StatBlock = {
    "characteristics": _S_CHARACTERISTICS,
    "confidence": (2, 5),
    "warping": (5, 18),
    "apparent_age": 25,
    "virtues_flaws": _S_30_VF,
    "traits": _S_TRAITS,
    "reputations": {
        "Trouvere (Artist)": 3,
        "Faerie Bard (France)": 3,
        "Troublesome Faerie Guy (Order of Hermes)": 2,
        "Faerie Sorcerer (faeries of Arcadia)": 1,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Athletics 1 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 2 "
        "(dodging), Carouse 2 (drinking songs), Charm 1 (first impressions), "
        "Concentration 2 (spell concentration), Divine Lore 1 (angels), "
        "Enchanting Music 3 (friendship), Etiquette 2 (faeries), Faerie Lore "
        "4 (faerie forests), Faerie Magic 4 (spells), Finesse 3 (Imaginem), "
        "Folk Ken 2 (faeries), Guile 2 (fast talk), High French 5 (music), "
        "French Kingdom Lore 2 (towns), House Merinita Lore 3 (initiations), "
        "Infernal Lore 1 (demons), Intrigue 2 (rumormongering), Latin 4 "
        "(texts), Legerdemain 2 (“magic” tricks), Magic Lore 2 (forests), "
        "Magic Theory 3 (15) (spells), Music 3 (lyre), Order of Hermes Lore "
        "1 (magi), Parma Magica 5 (Vim), Penetration 2 (Imaginem), "
        "Philosophiae 1 (ceremonial magic), Profession: Trouvere 2 (love "
        "songs), Teaching 1 (magi), Second Sight 2 (faeries), Stealth 1 "
        "(sneak), Survival 2 (finding routes), Swim 1 (rivers)"
    ),
    "arts": arts_from(
        "Cr 12, In 7, Mu 10, Pe 5, Re 9, An 5, Aq 5, Au 5, Co 6, He 5, Ig 11, "
        "Im 20, Me 15, Te 5, Vi 5"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_45),
    "notes": paragraphs(
        _S_LOOK + " He does not seem to age, and a red fox rides his shoulder.",
        "Twilight scars: his hair stirs like a hero's in an old tale; at "
        "times his plain illusions turn real as Glamour, but only when that "
        "goes badly for him; little prey animals grow extra nervous near "
        "him.",
        "Since the last block: 15 seasons with an apprentice, one on his "
        "longevity ritual, six on spells. 270 xp from nine full years plus "
        "10 for a half year. 120 xp to Abilities (695 total), 150 to Arts "
        "(650 total). " + _S_ACTIVITY_NOTE,
        "Combat: dodging Init 0, Defense +3. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
        _S_GLAMOUR,
        _S_LYRE,
        _S_FELIX,
        _S_FELIX_15,
    ),
}
SCIPIO_60: StatBlock = {
    "characteristics": _S_CHARACTERISTICS,
    "confidence": (2, 5),
    "warping": (6, 18),
    "apparent_age": 35,
    "virtues_flaws": _S_30_VF,
    "traits": _S_TRAITS,
    "reputations": {
        "Trouvere (Artist)": 4,
        "Faerie Bard (France)": 4,
        "Troublesome Faerie Guy (Order of Hermes)": 3,
        "Faerie Sorcerer (Faeries of Arcadia)": 2,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Athletics 1 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 2 "
        "(dodging), Carouse 2 (drinking songs), Charm 1 (first impressions), "
        "Concentration 2 (spell concentration), Divine Lore 1 (angels), "
        "Enchanting Music 4 (friendship), Etiquette 2 (faeries), Faerie Lore "
        "3 (faerie forests), Faerie Magic 4 (spells), Finesse 4 (Imaginem), "
        "Folk Ken 3 (faeries), Guile 2 (fast talk), High French 5 (music), "
        "French Kingdom Lore 2 (towns), House Merinita Lore 3 (initiations), "
        "Infernal Lore 1 (demons), Intrigue 2 (rumormongering), Latin 4 "
        "(texts), Legerdemain 2 (“magic” tricks), Magic Lore 2 (forests), "
        "Magic Theory 4 (spells), Music 3 (lyre), Order of Hermes Lore 2 "
        "(magi), Parma Magica 5 (Vim), Penetration 2 (Imaginem), Philosophiae "
        "2 (ceremonial magic), Profession: Trouvere 2 (love songs), Teaching "
        "2 (magi), Second Sight 3 (faeries), Stealth 2 (sneak), Survival 2 "
        "(finding routes), Swim 2 (rivers)"
    ),
    "arts": arts_from(
        "Cr 12, In 8, Mu 12, Pe 11, Re 11, An 6, Aq 6, Au 6, Co 6, He 6, Ig "
        "11, Im 25, Me 16, Te 6, Vi 6"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_60),
    "notes": paragraphs(
        _S_LOOK + " He does not seem to age, and a red fox rides his shoulder.",
        "Twilight scars: his hair stirs like a hero's in an old tale; at "
        "times his plain illusions turn real as Glamour, but only when that "
        "goes badly for him; little prey animals grow extra nervous near "
        "him; when he stands still his shadow turns a very dark red.",
        "Since the last block: seven seasons on spells, one enchanting his "
        "familiar. 390 xp from 13 full years. 150 xp to Abilities (840 "
        "total), 240 to Arts (890 total). " + _S_ACTIVITY_NOTE,
        "Combat: dodging Init 0, Defense +3. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
        _S_GLAMOUR,
        _S_LYRE,
        _S_FELIX,
        _S_FELIX_30,
    ),
}
SCIPIO_75: StatBlock = {
    "characteristics": _S_75_CHARACTERISTICS,
    "confidence": (3, 5),
    "decrepitude": (0, 2),
    "warping": (7, 13),
    "apparent_age": 40,
    "virtues_flaws": _S_30_VF,
    "traits": _S_TRAITS,
    "reputations": {
        "Trouvere (Artist)": 5,
        "Faerie Bard (France)": 4,
        "Troublesome Faerie Guy (Order of Hermes)": 4,
        "Faerie Sorcerer (Faeries of Arcadia)": 3,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Athletics 1 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 2 "
        "(dodging), Carouse 2 (drinking songs), Charm 1 (first impressions), "
        "Concentration 2 (spell concentration), Divine Lore 1 (angels), "
        "Enchanting Music 4 (friendship), Etiquette 2 (faeries), Faerie Lore "
        "4 (faerie forests), Faerie Magic 5 (spells), Finesse 4 (Imaginem), "
        "Folk Ken 3 (faeries), Guile 2 (fast talk), High French 5 (music), "
        "French Kingdom Lore 2 (towns), House Merinita Lore 3 (initiations), "
        "Infernal Lore 1 (demons), Intrigue 3 (rumormongering), Latin 4 "
        "(texts), Legerdemain 2 (“magic” tricks), Magic Lore 2 (forests), "
        "Magic Theory 4 (spells), Music 4 (lyre), Order of Hermes Lore 2 "
        "(magi), Parma Magica 6 (Vim), Penetration 2 (Imaginem), Philosophiae "
        "2 (ceremonial magic), Profession: Trouvere 2 (love songs), Teaching "
        "2 (magi), Second Sight 3 (faeries), Stealth 2 (sneak), Survival 2 "
        "(finding routes), Swim 2 (rivers)"
    ),
    "arts": arts_from(
        "Cr 13, In 9, Mu 15, Pe 14, Re 13, An 6, Aq 6, Au 9, Co 9, He 6, Ig "
        "11, Im 27, Me 18, Te 6, Vi 6"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_75),
    "notes": paragraphs(
        _S_LOOK + " He does not seem to age, a red fox rides his shoulder, "
        "and a blue piece of silk from his lady is bound round his arm.",
        "Twilight scars: his hair stirs like a hero's in an old tale; at "
        "times his plain illusions turn real as Glamour, but only when that "
        "goes badly for him; little prey animals grow extra nervous near "
        "him; when he stands still his shadow turns a very dark red; each "
        "hair on his head is a sliver of copper that can be melted down.",
        "Since the last block: seven seasons on spells, one rebuilding a lab "
        "he destroyed by experiment, one reforging his familiar's bond, two "
        "on his talisman, one on a magical item. 360 xp from 12 full years. "
        "155 xp to Abilities (995 total), 205 to Arts (1095 total). "
        + _S_ACTIVITY_NOTE,
        "Combat: dodging Init -1, Defense +2. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
        _S_GLAMOUR,
        _S_LYRE,
        _S_BAG,
        _S_FELIX,
        _S_FELIX_45,
    ),
}
SCIPIO_90: StatBlock = {
    "characteristics": _S_90_CHARACTERISTICS,
    "aging_points": {"presence": 1},
    "confidence": (3, 5),
    "decrepitude": (0, 4),
    "warping": (8, 3),
    "apparent_age": 50,
    "virtues_flaws": _S_30_VF,
    "traits": _S_TRAITS,
    "reputations": {
        "Trouvere (Artist)": 5,
        "Faerie Bard (France)": 4,
        "Troublesome Faerie Guy (Order of Hermes)": 4,
        "Faerie Sorcerer (Faeries of Arcadia)": 3,
        "Faerie Bard (new home tribunal)": 1,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Athletics 2 (running), "
        "Awareness 2 (spotting), Bargain 2 (music payment), Brawl 2 "
        "(dodging), Carouse 3 (drinking songs), Charm 2 (first impressions), "
        "Concentration 3 (spell concentration), Divine Lore 1 (angels), "
        "Enchanting Music 4 (friendship), Etiquette 2 (faeries), Faerie Lore "
        "4 (faerie forests), Faerie Magic 6 (spells), Finesse 4 (Imaginem), "
        "Folk Ken 3 (faeries), Guile 2 (fast talk), High French 5 (music), "
        "French Kingdom Lore 2 (towns), House Merinita Lore 3 (initiations), "
        "Infernal Lore 1 (demons), Intrigue 3 (rumormongering), Latin 4 "
        "(texts), Legerdemain 3 (“magic” tricks), Magic Lore 2 (forests), "
        "Magic Theory 5 (spells), Music 4 (lyre), Order of Hermes Lore 2 "
        "(magi), Parma Magica 7 (Vim), Penetration 2 (Imaginem), Philosophiae "
        "2 (ceremonial magic), Profession: Trouvere 2 (love songs), Teaching "
        "2 (magi), Second Sight 3 (faeries), Stealth 2 (sneak), Survival 2 "
        "(finding routes), Swim 2 (rivers)"
    ),
    "arts": arts_from(
        "Cr 16, In 10, Mu 15, Pe 14, Re 15, An 6, Aq 6, Au 9, Co 10, He 6, Ig "
        "11, Im 28, Me 19, Te 6, Vi 6"
    ),
    "spells": _spells(_SCIPIO_SPELLS, _S_90),
    "notes": paragraphs(
        _S_LOOK.replace("red hair", "copper-red hair")
        + " He does not seem to age, a red fox rides his shoulder, and a "
        "blue piece of silk from his lady is bound round his arm.",
        "Twilight scars: his hair stirs like a hero's in an old tale; at "
        "times his plain illusions turn real as Glamour, but only when that "
        "goes badly for him; little prey animals grow extra nervous near "
        "him; when he stands still his shadow turns a very dark red; each "
        "hair on his head is a sliver of copper that can be melted down.",
        "Since the last block: eight seasons inventing spells, 15 teaching "
        "an apprentice, one on his longevity ritual. 270 xp from 9 full "
        "years. 55 xp to Abilities (1050 total), 200 to Arts (1295 total); "
        "the book's figures do not sum to the 270. " + _S_ACTIVITY_NOTE,
        "Combat: dodging Init -1, Defense +2. Soak +0.",
        _S_MAGIC,
        _S_LEVELS,
        _S_GLAMOUR,
        _S_LYRE,
        _S_BAG,
        _S_FELIX,
        _S_FELIX_60,
        "Also in the chapter but on no block: Living Fire (MuIm 25 by the "
        "errata, Voice, Fire, Ind; calculation Base 3, +2 Voice, +3 Fire, +1 "
        "moving images), which reshapes a fire's image, sound and smell. The "
        "book's Image of the Lady targets an Individual by the errata; "
        "Scipio's images need sleep and illusory meals.",
    ),
}

# Tolides of Flambeau (pp. 127-135)

_TOLIDES_SPELLS: dict[str, tuple[str, int]] = {
    "Cripple the Howling Wolf": ("PeAn", 25),
    "Evaluate the Facing Opponent": ("InCo", 10),
    "Track By Scent": ("MuCo(An)", 4),
    "Chastise the Unruly Antagonist": ("PeCo", 10),
    "Inner Darkness Unleashed": ("PeCo", 20),
    "Blind the Insurgent Pack": ("PeCo", 25),
    "Lifting the Dangling Puppet": ("ReCo", 15),
    "Retreat into the Shell of Shadow": ("ReCo", 15),
    "The Protesting Adversary Held Still": ("ReCo", 20),
    "Pass the Unyielding Portal": ("MuHe", 5),
    "Gloom of Evening": ("PeIg", 10),
    "Banishment of Warmth": ("PeIg", 15),
    "Extinguish the Abhorrent Flame": ("PeIg", 15),
    "Cloak of Darkness": ("PeIg", 20),
    "Orb of Darkness": ("PeIg", 20),
    "Abyssal Touch": ("PeIg", 25),
    "Well Without Light": ("PeIg", 25),
    "Wizard's Icy Grip": ("PeIg", 30),
    "Domain of Darkness": ("PeIg", 45),
    "Prying Eyes": ("InIm", 5),
    "Chamber of Muffled Passing": ("PeIm", 15),
    "Veil of Invisibility": ("PeIm", 20),
    "Wizard's Sidestep": ("ReIm", 10),
    "Calm the Motion of the Heart": ("PeMe", 15),
    "Stone to Dust": ("PeTe", 20),
    "End of the Mighty Castle": ("PeTe", 25),
    "Hands of the Grasping Earth": ("ReTe(Mu)", 15),
    "Belittle the Ferocious Warlock": ("PeVi", 20),
    "Chastise the Unruly Fiend": ("PeVi", 10),
    "Circular Ward Against Demons": ("ReVi", 20),
}
_T_GAUNTLET = (
    "Lifting the Dangling Puppet; Prying Eyes; Veil of Invisibility; "
    "Wizard's Sidestep; Gloom of Evening; Well Without Light; Wizard's Icy "
    "Grip; Calm the Motion of the Heart; Stone to Dust"
)
_T_15 = _T_GAUNTLET + (
    "; Cripple the Howling Wolf; Evaluate the Facing Opponent; Track By "
    "Scent; Chastise the Unruly Antagonist; Inner Darkness Unleashed; "
    "Retreat into the Shell of Shadow; Pass the Unyielding Portal; "
    "Banishment of Warmth; Extinguish the Abhorrent Flame; Cloak of "
    "Darkness; Chamber of Muffled Passing; Chastise the Unruly Fiend"
)
_T_30 = (
    _T_15.replace("Inner Darkness Unleashed", "Inner Darkness Unleashed:1")
    .replace("Retreat into the Shell of Shadow", "Retreat into the Shell of Shadow:1")
    .replace("Wizard's Icy Grip", "Wizard's Icy Grip:1")
    .replace("Calm the Motion of the Heart", "Calm the Motion of the Heart:1")
    .replace("Stone to Dust", "Stone to Dust:1")
) + (
    "; Blind the Insurgent Pack; The Protesting Adversary Held Still; Orb of "
    "Darkness; Abyssal Touch; End of the Mighty Castle; Hands of the "
    "Grasping Earth; Circular Ward Against Demons"
)
_T_33 = _T_30 + "; Domain of Darkness; Belittle the Ferocious Warlock:2"
_T_MASTERY = {
    "Inner Darkness Unleashed": ["Magic Resistance"],
    "Retreat into the Shell of Shadow": ["Fast Casting"],
    "Wizard's Icy Grip": ["Magic Resistance"],
    "Calm the Motion of the Heart": ["Still Casting"],
    "Stone to Dust": ["Multiple Casting"],
}
_T_CHARACTERISTICS = characteristics(2, 1, 0, -2, 1, 2, 1, 1)
_T_VF = [
    "The Gift",
    "Hermetic Magus",
    vf_art("Affinity with {art}", "Perdo"),
    "See in Darkness",
    "Immunity to Cold",
    "Life Boost",
    "Lightning Reflexes",
    ("Minor Magical Focus", {"focus": "darkness"}),
    vf_art("Puissant {art}", "Perdo"),
    "Quiet Magic",
    "Quiet Magic",
    "Rapid Convalescence",
    "Skilled Parens",
    ("Dark Secret", {"detail": "Diabolism"}),
    ("Deficient Technique", {"technique": "Creo"}),
    "Infamous Master",
    "Nocturnal",
    "Susceptibility to Sunlight",
    ("Warped Magic", {"detail": "darkness unfolds"}),
]
_T_LOOK = (
    "Average in size, short black hair, pallid, with pitch-black sunken eyes "
    "like obsidian that make people look away, and a long scar across his "
    "throat from ear to ear. Among people he sits still as carved stone and "
    "moves slowly, as if arthritic, until the least hostility brings a "
    "cat's speed. His hands wait in his wide black sleeves with a dagger. "
    "Elegant in feature, he talks like one raised among beasts, in a low "
    "rasp, and only when he must."
)
_T_COMBAT = (
    "Combat: dagger Init +1, Attack +5, Defense +3, Damage +4; fist Init +1, "
    "Attack +3, Defense +3, Damage +1. Soak +2."
)
_T_ITEMS = (
    "Torus of Fire Protection, a brown fired-clay pendant, 2 pawns. Quench "
    "the Open Fire (PeIg 15, Pen +0, unlimited): small fires touching it go "
    "out, as do magical flames up to +5 damage; worn over the clothes. "
    "Poniard of Deliverance, 2 pawns, remade after the Quaesitores took its "
    "like. Appliance of Wrath (PeCo 20, Pen +10, 24/day): flicked in the "
    "wrist, it adds a Light Wound on a positive Attack Advantage, armor no "
    "bar. Source of Tranquillity, a tiny obsidian winged figurine, 3 pawns. "
    "Chamber of Void (PeIg 24, Pen +0, constant): no light at all in the "
    "room it is in."
)
_T_ORB = (
    "Talisman: the Orb of Immanent Darkness, a black obsidian orb he has "
    "always treasured for its cool, 4 pawns to open and 2 for its effect. "
    "Attunement: +5 spellcasting involving light's absence. Soothing "
    "Shadows (PeIg 14, Pen +0, constant): deep shadow over his head and "
    "upper body, so that cloaked and hooded he walks under the day's sun "
    "without losing Fatigue, though looking at a sunny land still pains him."
)
_T_GIFTS = (
    "Given away for favors. Arrows of Defeat, six arrows of one charge each "
    "from a Lab Total of 40, for a shady noble: Gaping Maw of the Bottomless "
    "Pit (PeTe 10, Touch), as Pit of the Gaping Earth where each lands. "
    "Sting of the Viper, a human-bone and steel hair pin with a comb, for a "
    "woman he fell to, usable by her alone, 2 pawns: The Fool's Fate (PeCo "
    "20, Pen +0, 3/day), a Medium Wound. Rod of Mutilation, a wand of human "
    "bone shod in iron, invested for a diabolist who aided his longevity "
    "ritual, 6 pawns opened, 4 used, expiring seven years after first use: "
    "Crush the Adversary's Limb (PeCo 33, Pen +10, 6/day) breaks the "
    "touched limb, healing as a Medium Wound."
)
_T_IMP = (
    "Familiar: an imp, a lesser Tempter (Maligenii), Infernal Might 10 "
    "(Vim), Size -5, kitten-sized with leathery wings, reddish-grey skin "
    "and a fanged maw. Int 0, Per +4, Pre -3, Com -1, Str -5, Sta 0, Dex "
    "+2, Qik +5. Confidence 1 (3). Keen Vision, Sharp Ears; Greedy, "
    "Nocturnal. Cruel +2, Brave -2, Enduring -1, Insidious +3, Sneaking +3. "
    "Hierarchy 0. Bite Init +5, Attack +3, Defense +14, Damage -12. Soak 0. "
    "Athletics 1, Awareness 5, Bargain 1, Guile 2, Hunt 3, Stealth 5. "
    "Powers: Coagulation, Obsession (Hopelessness), Petrification (1 point, "
    "Init -10, a stone figurine), See in Darkness, Source of Tranquility (3 "
    "points, Init 0, for a Diameter). Weakness: powerless at midday, and "
    "turned to stone by direct noon sun until dusk. 2 pawns of Vim in its "
    "wings. It came to him offering to watch his back; he bound it with "
    "his Perdo Ignem Lab Total. Cords: gold 1, silver 1, bronze 3."
)
_T_SPELL_NOTES = (
    "This block prints Circular Ward Against Demons at level 20, a General "
    "spell whose level the sheet does not hold."
)

TOLIDES_GAUNTLET: StatBlock = {
    "characteristics": _T_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (1, 0),
    "apparent_age": 21,
    "virtues_flaws": _T_VF,
    "traits": {"Sinister": 2, "Temperate": 2, "Depressed": 1, "Emotional": -1},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Athletics 1 (tumbling), "
        "Awareness 2 (alertness), Brawl 2 (dodge), Chirurgy 1 (treat wounds), "
        "Concentration 1 (spell casting), Dead Language: Latin 4 (Hermetic "
        "usage), Finesse 1 (precision), Infernal Lore 2 (demons), Leadership "
        "1 (intimidation), Living Language: West Slavonic 5 (curses), Magic "
        "Theory 3 (Perdo), Parma Magica 1 (Corpus), Penetration 2 (Perdo), "
        "Stealth 2 (rural areas)"
    ),
    "arts": arts_from(
        "Cr 0, In 2, Mu 4, Pe 12+3, Re 6, An 2, Aq 0, Au 0, Co 6, He 0, Ig 9, "
        "Im 3, Me 2, Te 2, Vi 2"
    ),
    "spells": _spells(_TOLIDES_SPELLS, _T_GAUNTLET),
    "notes": paragraphs(
        _T_LOOK,
        "Sigil: black writhing vapor round the caster, heightened by Warped "
        "Magic. Voting sigil: an obsidian wand, kept so no one else can use "
        "it, never used by him.",
        _T_COMBAT + " Equipment: dagger in a forearm sheath, obsidian pellet.",
        "The block prints Lesser Immunity: Cold and Lesser Malediction "
        "(Susceptibility to Sunlight); both are the book's own new Virtue "
        "and Flaw on p. 128. The second costs him Fatigue under a hot sun "
        "and -2 to sight in bright light.",
    ),
}
TOLIDES_15: StatBlock = {
    "characteristics": _T_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (3, 5),
    "apparent_age": 36,
    "virtues_flaws": _T_VF,
    "traits": {
        "Cunning": 2,
        "Sinister": 2,
        "Temperate": 2,
        "Depressed": 1,
        "Emotional": -1,
    },
    "abilities": _abilities(
        "Area Lore: Eastern Europe 1 (geography), Artes Liberales 1 "
        "(ceremonial magic), Athletics 2 (tumbling), Awareness 2 (alertness), "
        "Brawl 3 (dodge), Bargain 1 (Infernal powers), Chirurgy 2 (treat "
        "wounds), Code of Hermes 1 (Quaesitores and Hoplites), Concentration "
        "2 (spell casting), Dead Language: Latin 4 (Hermetic usage), Finesse "
        "1 (precision), Folk Ken 1 (peasants), Hunt 1 (covering tracks), "
        "Infernal Lore 3 (demons), Leadership 1 (intimidation), Living "
        "Language: East Slavonic 2 (curses), Living Language: West Slavonic "
        "5 (curses), Magic Lore 1 (creatures), Magic Theory 4 (Perdo), "
        "Medicine 1 (anatomy), Parma Magica 3 (Corpus), Penetration 3 "
        "(Perdo), Philosophiae 1 (ritual magic), Stealth 2 (rural areas), "
        "Survival 1 (wooded mountains)"
    ),
    "arts": arts_from(
        "Cr 0, In 2, Mu 4, Pe 14+3, Re 9, An 2, Aq 0, Au 0, Co 11, He 2, Ig "
        "11, Im 5, Me 2, Te 2, Vi 2"
    ),
    "spells": _spells(_TOLIDES_SPELLS, _T_15),
    "notes": paragraphs(
        _T_LOOK,
        "Hierarchy Score 1 (Realms of Power: The Infernal p. 94).",
        "Since his Gauntlet: surviving in Eastern Europe taught him practical "
        "skills. 180 xp in Abilities and 120 in Arts. In 20 lab seasons he "
        "learned and made spells and items, trading two items for favors, "
        "one for help with his longevity ritual, a season's work; he "
        "enchanted and attuned his talisman.",
        _T_COMBAT + " Equipment: dagger in a forearm sheath, obsidian pellet.",
        _T_ITEMS,
        _T_ORB,
        _T_GIFTS,
    ),
}
TOLIDES_30: StatBlock = {
    "characteristics": _T_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (5, 6),
    "apparent_age": 42,
    "virtues_flaws": _T_VF,
    "traits": {
        "Cunning": 2,
        "Sinister": 3,
        "Temperate": 2,
        "Depressed": 1,
        "Emotional": -1,
    },
    "abilities": _abilities(
        "Area Lore: Eastern Europe 2 (geography), Artes Liberales 1 "
        "(ceremonial magic), Athletics 2 (tumbling), Awareness 2 (alertness), "
        "Brawl 3 (dodge), Bargain 2 (Infernal powers), Chirurgy 2 (treat "
        "wounds), Code of Hermes 1 (Quaesitores and Hoplites), Concentration "
        "3 (spell casting), Dead Language: Latin 4 (Hermetic usage), Divine "
        "Lore 1 (Divine creatures), Finesse 1 (precision), Folk Ken 1 "
        "(peasants), Hunt 2 (covering tracks), Infernal Lore 3 (demons), "
        "Leadership 1 (intimidation), Living Language: East Slavonic 2 "
        "(curses), Living Language: West Slavonic 5 (curses), Magic Lore 1 "
        "(creatures), Magic Theory 5 (Perdo), Medicine 1 (anatomy), Parma "
        "Magica 4 (Corpus), Penetration 4 (Perdo), Philosophiae 1 (ritual "
        "magic), Stealth 2 (rural areas), Survival 1 (wooded mountains), "
        "True Name of Balthazar 1"
    ),
    "arts": arts_from(
        "Cr 0, In 2, Mu 4, Pe 17+3, Re 9, An 2, Aq 2, Au 3, Co 11, He 2, Ig "
        "14, Im 5, Me 2, Te 8, Vi 5"
    ),
    "spells": _spells(_TOLIDES_SPELLS, _T_30),
    "masteries": _T_MASTERY,
    "notes": paragraphs(
        _T_LOOK,
        "Twilight scar: light dims slightly round him wherever he stays over "
        "two minutes, recovering once he leaves. Hierarchy Score 3. True "
        "Name of Balthazar: Realms of Power: The Infernal p. 34.",
        "Since the last block: 140 xp in Abilities, 160 in Arts, 25 on "
        "mastering spells and 5 on a demon's True Name. An imp approached "
        "him and he bound it. His Infernal dealings came out and he was "
        "Marched; he escaped the Order's assault, probably with Infernal "
        "help, and made a new home in a stronger aura (level 4), a season to "
        "prepare the lab, 16 seasons of lab work in all. Infernal auras and "
        "dealings gave him much Warping.",
        _T_COMBAT + " Equipment: dagger in a forearm sheath, obsidian pellet.",
        _T_IMP,
        _T_ITEMS,
        _T_ORB,
        _T_GIFTS,
        _T_SPELL_NOTES,
    ),
}
TOLIDES_33: StatBlock = {
    "characteristics": _T_CHARACTERISTICS,
    "confidence": (1, 3),
    "warping": (5, 12),
    "apparent_age": 43,
    "virtues_flaws": _T_VF,
    "traits": {
        "Cunning": 2,
        "Sinister": 3,
        "Temperate": 2,
        "Depressed": 1,
        "Emotional": -1,
    },
    "abilities": _abilities(
        "Area Lore: Eastern Europe 2 (geography), Artes Liberales 1 "
        "(ceremonial magic), Athletics 2 (tumbling), Awareness 2 (alertness), "
        "Brawl 3 (dodge), Bargain 2 (Infernal powers), Chirurgy 2 (treat "
        "wounds), Code of Hermes 1 (Quaesitores and Hoplites), Concentration "
        "3 (spell casting), Dead Language: Latin 4 (Hermetic usage), Divine "
        "Lore 1 (Divine creatures), Finesse 1 (precision), Folk Ken 1 "
        "(peasants), Hunt 2 (covering tracks), Infernal Lore 3 (demons), "
        "Leadership 1 (intimidation), Living Language: East Slavonic 2 "
        "(curses), Living Language: West Slavonic 5 (curses), Magic Lore 1 "
        "(creatures), Magic Theory 5 (Perdo), Medicine 1 (anatomy), Parma "
        "Magica 4 (Corpus), Penetration 4 (Perdo), Philosophiae 1 (ritual "
        "magic), Stealth 2 (rural areas), Survival 1 (wooded mountains), "
        "True Name of Balthazar 1, True Name of Ilkazar 1"
    ),
    "arts": arts_from(
        "Cr 0, In 2, Mu 4, Pe 17+3, Re 10, An 2, Aq 2, Au 3, Co 11, He 2, Ig "
        "14, Im 5, Me 2, Te 8, Vi 5"
    ),
    "spells": _spells(_TOLIDES_SPELLS, _T_33),
    "masteries": {
        **_T_MASTERY,
        "Belittle the Ferocious Warlock": ["Fast Casting", "Magic Resistance"],
    },
    "notes": paragraphs(
        _T_LOOK,
        "Twilight scars: light dims slightly round him wherever he stays over "
        "two minutes, recovering once he leaves; small flames near him "
        "flicker as if in a cold draught, threatening to go out. Hierarchy "
        "Score 4.",
        "Since the last block: three seasons on Domain of Darkness, his "
        "greatest work, which he means to grow into a regio of his own; "
        "nearly three years in his lab, learning a second True Name and "
        "tuning his spells against the Hoplites who hunt him.",
        _T_COMBAT + " Equipment: dagger in a forearm sheath, obsidian pellet.",
        _T_IMP,
        _T_ITEMS,
        _T_ORB,
        _T_GIFTS,
        _T_SPELL_NOTES + " It also prints Track By Scent at level 5, where "
        "p. 131 and the earlier blocks have 4.",
    ),
}

# Yestin of Jerbiton (pp. 136-144)

_YESTIN_SPELLS: dict[str, tuple[str, int]] = {
    "The Magic Flute": ("CrHe", 5),
    "Heal Thy Broken Voice": ("CrHe", 20),
    "Mend Thy Broken Strings": ("ReHe", 20),
    "Let This Fire Sing You to Sleep": ("MuIg(Im)", 25),
    "Let the Sun Not Bother Me This Day": ("PeIg", 10),
    "Prying Eyes": ("InIm", 5),
    "Confound the Rival Singer": ("MuIm", 4),
    "Notes of a Delightful Sound": ("MuIm", 10),
    "The Welcome Stranger": ("CrMe", 15),
    "Orpheus' Ballad": ("CrMe", 20),
    "To Sing of Good Meat and Drink": ("CrMe", 25),
    "The Call to Slumber": ("ReMe", 10),
    "Lay Your Burdens on Me": ("ReMe", 20),
    "The Wisdom of Sleep": ("InTe(Vi)", 25),
    "The Well-Trodden Path": ("ReTe", 10),
    "Nature's Kindest Seat": ("ReTe", 25),
    "Sense of Faerie Power": ("InVi", 2),
    "Sense of Infernal Power": ("InVi", 2),
    "Sense of Magical Power": ("InVi", 2),
    "A Song of All These Faerie Places": ("InVi(Cr,Im)", 25),
    "A Song of All These Infernal Places": ("InVi(Cr,Im)", 25),
    "A Song of All These Magical Places": ("InVi(Cr,Im)", 25),
}
_Y_GAUNTLET = (
    "The Magic Flute; Heal Thy Broken Voice; Let the Sun Not Bother Me This "
    "Day; Prying Eyes; Confound the Rival Singer; Notes of a Delightful "
    "Sound; The Welcome Stranger; To Sing of Good Meat and Drink; The Call "
    "to Slumber; The Well-Trodden Path; Sense of Faerie Power; Sense of "
    "Infernal Power; Sense of Magical Power"
)
_Y_15 = _Y_GAUNTLET.replace("The Welcome Stranger", "The Welcome Stranger:1") + (
    "; Mend Thy Broken Strings; Orpheus' Ballad; Nature's Kindest Seat"
)
_Y_30 = _Y_15 + "; Let This Fire Sing You to Sleep; The Wisdom of Sleep"
_Y_45 = _Y_30.replace("The Welcome Stranger:1", "The Welcome Stranger:2") + (
    "; Lay Your Burdens on Me; A Song of All These Faerie Places; A Song of "
    "All These Infernal Places; A Song of All These Magical Places"
)
_Y_CHARACTERISTICS = characteristics(2, 0, 1, 2, -1, 0, 1, 0)
_Y_VF = [
    "The Gift",
    "Hermetic Magus",
    "Gentle Gift",
    vf_art("Affinity with {art}", "Imaginem"),
    "Free Expression",
    ("Minor Magical Focus", {"focus": "music"}),
    ("Performance Magic", {"ability": "Music"}),
    vf_puissant("Music"),
    "Well-Traveled",
    ("Plagued by Supernatural Entity", {"detail": "Taliesin"}),
    "Twilight Prone",
    (
        "Delusion",
        {"detail": "thinks himself part of a forgotten pre-Diedne lineage"},
    ),
    "Noncombatant",
]
_Y_COMBAT = (
    "Combat: dodge Init +0, Defense +0; fist Init +0, Attack +1, Defense +0, "
    "Damage -1; kick Init -1, Attack +1, Defense -1, Damage +2; bludgeon "
    "Init -1, Attack +3, Defense +0, Damage +1. Soak +0."
)
_Y_SIGIL = (
    "Sigil: a moment of calm, like an indrawn breath, before each spell or "
    "device takes effect. Voting sigil: a plain, highly polished wooden "
    "flute."
)
_Y_SPELL_NOTES = (
    "Spell notes: The Magic Flute conjures a flute for as long as he plays "
    "it; Heal Thy Broken Voice is a Ritual, under a new CrHe 15 guideline "
    "for restoring a made wooden item (p. 139). To Sing of Good Meat and "
    "Drink makes a room hungry and thirsty, and he casts it forcelessly so "
    "it cannot touch magi. Confound the Rival Singer is level 5 on p. 140, "
    "level 4 in every block."
)
_Y_VIS = (
    "He carries a small pouch of Creo and Herbam vis for the rituals that "
    "repair his crwth."
)
_Y_CLOAK = (
    "Cloak of Wilderness Refuge, a lesser enchanted woollen cloak. An "
    "Instant Roof (MuAn 15, Conc, Pen +0, 1/day, item maintains "
    "concentration): at a Welsh tongue-twister it becomes a tent for three, "
    "its bone toggle the poles."
)
_Y_CRWTH = (
    "Talisman: the Crwth of Yestin, of rowan, with its bow, a gift from his "
    "mater before his Gauntlet. Attunements: +3 create sounds, +5 affect "
    "music, +4 protection against malicious magic, +1 Vim. A Song to Banish "
    "the Darkness (ReVi 41, Conc, Room, Pen +22, 1/day, item maintains "
    "concentration): a level 20 ward holding Infernal creatures from a "
    "room, or within it. A Song to Banish the Impish does so for Faerie, A "
    "Song to Banish the Mystical for Magic, both at the same figures. Your "
    "Voice and Mine (CrIm 15, Pen +0, 12/day, Yestin only): the crwth sings "
    "with him, sometimes changing words to the song's gain, for reasons "
    "unknown. Adelbert the Tyrolean of Yestin's covenant suspects a "
    "supernatural agent was in the lab."
)
_Y_SPEAR = (
    "Spear of Lleu, commissioned for his shield grog from a Verditius on the "
    "Isle of Oxney. Neither Rock nor Steel (PeTe 26, Pen +22, 1/day): "
    "plunged into metal armor it ignores its Soak and halves it after. The "
    "Telling Blow (PeCo 34, Pen +22, 6/day): at a twist of the haft, a "
    "Heavy Wound on a target of up to Size +1, blood or no blood."
)
_Y_STONES = (
    "Song Stones, bright small stones, each a charge of Store the Song in "
    "Stone (CrIm 3, Diameter, Pen +0): holds a song of quality Com + Music "
    "until asked, once, in any voice he can mimic with Finesse. He gives "
    "them freely, an idea from a Lab Text of Phessalia of Voluntas that "
    "Taliesin showed him, and a first step toward the bardic magic he seeks."
)

YESTIN_GAUNTLET: StatBlock = {
    "characteristics": _Y_CHARACTERISTICS,
    "confidence": (1, 3),
    "apparent_age": 25,
    "virtues_flaws": _Y_VF,
    "traits": {"Gregarious": 2, "Cheerful": 1, "Determined": 1},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Carouse 2 (entertaining), "
        "Charm 2 (with song), Concentration 2 (spell concentration), English "
        "2 (poetry), Etiquette 1 (court), Finesse 2 (Imaginem), Folk Ken 2 "
        "(judging the mood of the audience), Latin 4 (Hermetic usage), Magic "
        "Theory 4 (Imaginem), Music 2+2 (sing), Norman French 2 (poetry), "
        "Parma Magica 1 (Mentem), Penetration 1 (Mentem), Philosophiae 1 "
        "(ceremonial magic), Stonehenge Lore 1 (legends), Welsh 5 "
        "(storytelling)"
    ),
    "arts": arts_from(
        "Cr 10, In 2, Mu 1, Pe 2, Re 7, An 2, Aq 0, Au 0, Co 1, He 2, Ig 0, "
        "Im 4, Me 10, Te 0, Vi 1"
    ),
    "spells": _spells(_YESTIN_SPELLS, _Y_GAUNTLET),
    "notes": paragraphs(
        "Fair hair brushed forward, a plain open face and bright eyes, nearly "
        "always smiling. Simple traveling clothes, but bright many-coloured "
        "wizard's robes, and always his crwth and bow in a fitted satchel.",
        _Y_SIGIL,
        "He usually carries a handful of mixed vis to give or pay to magi he knows.",
        _Y_COMBAT,
        _Y_SPELL_NOTES,
    ),
}
YESTIN_15: StatBlock = {
    "characteristics": _Y_CHARACTERISTICS,
    "confidence": (1, 10),
    "warping": (3, 0),
    "apparent_age": 36,
    "virtues_flaws": _Y_VF,
    "traits": {"Gregarious": 2, "Cheerful": 1, "Determined": 1},
    "abilities": _abilities(
        "Artes Liberales 1 (ceremonial magic), Carouse 2 (entertaining), "
        "Charm 2 (with song), Code of Hermes 1 (mundane relations), "
        "Concentration 2 (spell concentration), English 2 (poetry), Etiquette "
        "1 (court), Finesse 2 (Imaginem), Folk Ken 2 (judging the mood of the "
        "audience), Latin 4 (Hermetic usage), Magic Theory 4 (Imaginem), "
        "Music 2+2 (sing), Norman French 2 (poetry), Parma Magica 2 "
        "(Mentem), Penetration 1 (Mentem), Philosophiae 1 (ceremonial magic), "
        "Welsh 5 (storytelling), Stonehenge Lore 1 (legends)"
    ),
    "arts": arts_from(
        "Cr 10, In 10, Mu 8, Pe 2, Re 13, An 11, Aq 0, Au 0, Co 10, He 11, Ig "
        "2, Im 6, Me 10, Te 7, Vi 2"
    ),
    "spells": _spells(_YESTIN_SPELLS, _Y_15),
    "masteries": {"The Welcome Stranger": ["Still Casting"]},
    "notes": paragraphs(
        "He looks young for his age from his ritual, though not uncannily. "
        "Twilight scar: his eyes glitter with many colours.",
        _Y_SIGIL,
        _Y_VIS,
        "Since his Gauntlet: mostly his Arts, with years toward new spells. "
        "His longevity ritual is a short song he must sing each morning.",
        _Y_COMBAT,
        _Y_SPELL_NOTES,
    ),
}
YESTIN_30: StatBlock = {
    "characteristics": _Y_CHARACTERISTICS,
    "confidence": (1, 15),
    "warping": (4, 10),
    "apparent_age": 43,
    "virtues_flaws": _Y_VF,
    "traits": {"Gregarious": 2, "Cheerful": 1, "Determined": 1},
    "reputations": {"Fine Singer (Stonehenge)": 1},
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Carouse 2 (entertaining), "
        "Charm 2 (with song), Code of Hermes 1 (mundane relations), "
        "Concentration 2 (spell concentration), English 2 (poetry), Etiquette "
        "2 (court), Finesse 2 (Imaginem), Folk Ken 2 (judging the mood of the "
        "audience), Latin 4 (Hermetic usage), Magic Theory 6 (Imaginem), "
        "Music 3+2 (sing), Norman French 2 (poetry), Parma Magica 3 "
        "(Mentem), Penetration 2 (Mentem), Philosophiae 2 (ceremonial magic), "
        "Welsh 5 (storytelling), Stonehenge Lore 2 (legends)"
    ),
    "arts": arts_from(
        "Cr 10, In 15, Mu 12, Pe 3, Re 13, An 11, Aq 0, Au 1, Co 10, He 11, "
        "Ig 10, Im 10, Me 10, Te 10, Vi 10"
    ),
    "spells": _spells(_YESTIN_SPELLS, _Y_30),
    "masteries": {"The Welcome Stranger": ["Still Casting"]},
    "notes": paragraphs(
        "Twilight scars: his eyes glitter with their own light, and his hair "
        "seems threaded with shining copper.",
        _Y_SIGIL,
        _Y_VIS,
        "Since the last block: practising his music and making items; he "
        "opened and attuned his crwth and bow as his talisman and enchanted "
        "in all its effects, and added a few spells only of late.",
        _Y_COMBAT,
        _Y_CLOAK,
        _Y_CRWTH,
        _Y_SPELL_NOTES,
    ),
}
YESTIN_45: StatBlock = {
    "characteristics": _Y_CHARACTERISTICS,
    "confidence": (1, 15),
    "warping": (5, 15),
    "apparent_age": 54,
    "virtues_flaws": _Y_VF,
    "traits": {"Determined": 2, "Gregarious": 0, "Cheerful": 1},
    "reputations": {
        "Fine Singer (Stonehenge & Normandy)": 2,
        "Diedne Sympathizer (Stonehenge)": 2,
    },
    "abilities": _abilities(
        "Artes Liberales 2 (ceremonial magic), Carouse 2 (entertaining), "
        "Charm 2 (with song), Code of Hermes 2 (mundane relations), "
        "Concentration 3 (spell concentration), English 2 (poetry), Etiquette "
        "2 (court), Finesse 3 (Imaginem), Folk Ken 3 (judging the mood of the "
        "audience), Latin 4 (Hermetic usage), Magic Theory 8 (Imaginem), "
        "Music 4+2 (sing), Normandy Lore 2 (personalities), Norman French 3 "
        "(poetry), Parma Magica 3 (Mentem), Penetration 3 (Mentem), "
        "Philosophiae 2 (ceremonial magic), Welsh 5 (storytelling), "
        "Stonehenge Lore 2 (legends)"
    ),
    "arts": arts_from(
        "Cr 10, In 15, Mu 12, Pe 4, Re 15, An 11, Aq 0, Au 2, Co 10, He 11, "
        "Ig 10, Im 10, Me 15, Te 10, Vi 15"
    ),
    "spells": _spells(_YESTIN_SPELLS, _Y_45),
    "masteries": {"The Welcome Stranger": ["Quiet Casting", "Still Casting"]},
    "notes": paragraphs(
        "He looks a man in his mid-fifties in rude health, his eyes still "
        "glittering in the light, the copper showing more in his greying "
        "hair. Twilight scars as before.",
        _Y_SIGIL,
        _Y_VIS,
        "Since the last block: he drew away from the Order as word of his "
        "beliefs spread, yet hired a Verditius to make a spear for his new "
        "shield grog and made Song Stones as gifts. His own study went only "
        "to spells easing him and his companions across regio boundaries.",
        _Y_COMBAT,
        _Y_CLOAK,
        _Y_CRWTH,
        _Y_SPEAR,
        _Y_STONES,
        _Y_SPELL_NOTES,
    ),
}

MAGI: tuple[Magus, ...] = (
    Magus(
        name="Petalichus of Verditius",
        house=VERDITIUS,
        summary=(
            "Petalichus the Weaver, last of Arachne's Children, a dwindling "
            "cult of Verditius weavers who put magic into humble cloth while "
            "others forged swords and rings. His learning in philosophy and "
            "the artes liberales drew the Cononites, a secret Hermetic cult "
            "guarding the esoteric works of Conon of Samos, Euclid, "
            "Apollonius and Archimedes; they taught him their magic and he "
            "made their tools. Modest in his crafts and lofty in his aims, "
            "he is secretive, manipulative and vindictive, working from "
            "hiding through agents and proxies, and a long feud with Solar "
            "Magnus of Tytalus runs through his life."
        ),
        secrets=(
            "Quaesitor Valeria of Donum Chanuti found evidence that he "
            "killed Thomas Roxbury, a notary of House Guernicus, with a "
            "Light of Fell Disease candle while hunting Solar Magnus at "
            "Canterbury. He destroyed Solar Magnus there with a Dreams You "
            "Shall Not Wake From sheet, having learned when the Tytalus's "
            "cyclic magic left his resistance weakest. He bought Let the Sun "
            "Not Bother Me This Day from Yestin of Jerbiton for use in that "
            "feud."
        ),
        printings=(
            Printing("Gauntlet", 25, PETALICHUS_GAUNTLET),
            Printing("+15", 40, PETALICHUS_15),
            Printing("+30", 55, PETALICHUS_30),
            Printing("+45", 70, PETALICHUS_45),
        ),
    ),
    Magus(
        name="Ranulf of Flambeau",
        house=FLAMBEAU,
        summary=(
            "Son of candle makers, poor of sight, apprenticed into Flambeau "
            "and bent on mastering Ignem and Vim, with a wide range of new "
            "fire magic, more and more of it peaceful. His parens passed "
            "into Twilight during his Gauntlet, and two other Flambeau who "
            "saw him meet its challenges approved him as a magus after some "
            "months. Three years on she returned and demanded he repeat it; "
            "each took the refusal as an insult, and they never made peace. "
            "He dreamed of being a feared hoplite with Pilum of Fire, and "
            "the dream fades just as the work finds him."
        ),
        printings=(
            Printing("Gauntlet", 24, RANULF_GAUNTLET),
            Printing("+15", 39, RANULF_15),
            Printing("+30", 54, RANULF_30),
            Printing("+45", 69, RANULF_45),
            Printing("+60", 84, RANULF_60),
        ),
    ),
    Magus(
        name="Scipio of Merinita",
        house=MERINITA,
        summary=(
            "Once Pierre, son of a poor peasant woman and a faerie king of "
            "bright summer, carried off soon after birth to his father's "
            "court, where he learned music and illusion and fell in love "
            "with Vinella, a girl fostered there. The jealous king sold him "
            "to a Merinita maga, who made him a magus. He wanders in search "
            "of Vinella, watching for his father's men.\n\n"
            "Story seeds. At Gauntlet: he seeks a covenant as a base and "
            "draws his sodales in; he has tricked faeries and entered a "
            "nearby regio, enemy or ally to the fey; a Quaesitor asks "
            "whether those who help him molested the faeries. At +15: he "
            "needs help into a secure regio where a faerie holds a clue, at "
            "a price; his Book of Images catches magi doing ill, or the "
            "king's men forge it; he sells new vis sources for aid. At +30: "
            "he finds Vinella's tower in Faerie, guarded by the king's men; "
            "a Quaesitor devotes himself to catching him; he frees her, and "
            "a faerie queen claiming to be her mother takes her. At +45: he "
            "seeks an Ignem or ice magus against that queen of dark winter; "
            "he allies the covenant with a faerie court unasked; he wants a "
            "ward against iron, and the king's men arrive. At +60: he plays "
            "two warring courts and the Quaesitores to escape with Vinella, "
            "perhaps bringing a Wizard's March, and they flee to somewhere "
            "like Scotland, Russia or the Levant. At +75: they hide far from "
            "towns behind his illusions, yet wanderlust takes him out, "
            "seeking an apprentice, vis and young heroes to help. At +90: "
            "his second apprentice shames a lord with his silly spells; "
            "covenants hunt the notorious artist for Image of the Lady."
        ),
        printings=(
            Printing("Gauntlet", 25, SCIPIO_GAUNTLET),
            Printing("+15", 40, SCIPIO_15),
            Printing("+30", 55, SCIPIO_30),
            Printing("+45", 70, SCIPIO_45),
            Printing("+60", 85, SCIPIO_60),
            Printing("+75", 100, SCIPIO_75),
            Printing("+90", 115, SCIPIO_90),
        ),
    ),
    Magus(
        name="Tolides of Flambeau",
        house=FLAMBEAU,
        summary=(
            "Born a Silesian bond-slave, he served an Infernalist master in "
            "terrorising eastern Europe until he was as evil as his victims "
            "thought him; when the master was Marched he helped the "
            "Quaesitores. That left him a sinister husk of a young magus, "
            "unable to live with freedom, fit in anywhere, or bear the sun, "
            "on the edge of society with his studies, hoping for oblivion. "
            "Flambeau in name, he holds to no politics, and his House is not "
            "keen to claim him. He has the mind of a cornered beast, a "
            "predator wanting peace through his art and no more power than "
            "survival needs, and he seems bound for a March as his master was."
        ),
        secrets=(
            "He is a practising diabolist, raised to see the Church as his "
            "enemy, with demons about him waiting for his fall; salvation "
            "does not occur to him. His imp familiar is unlikely to have "
            "come by chance. Around +30 his dealings are found out and he is "
            "Marched, and survives."
        ),
        printings=(
            Printing("Gauntlet", 21, TOLIDES_GAUNTLET),
            Printing("+15", 36, TOLIDES_15),
            Printing("+30", 51, TOLIDES_30),
            Printing("+33", 54, TOLIDES_33),
        ),
    ),
    Magus(
        name="Yestin of Jerbiton",
        house=JERBITON,
        summary=(
            "Yestin Ap Llewelyn, a travelling bard, an upbeat, friendly "
            "dreamer sure that something grander lies just out of reach, "
            "who plays for prince, magus and peasant alike across Europe. "
            "His magic serves his travels, his music, and the riddles the "
            "faerie spirit Taliesin leads him into, where he rights others' "
            "wrongs in return for a promise to learn at last the secrets of "
            "his bardic lineage. He stays close to his mater, Ffanci ferch "
            "Fflam of Jerbiton."
        ),
        printings=(
            Printing("Gauntlet", 25, YESTIN_GAUNTLET),
            Printing("+15", 40, YESTIN_15),
            Printing("+30", 55, YESTIN_30),
            Printing("+45", 70, YESTIN_45),
        ),
    ),
)
