"""The covenant of Longmist, deep in Winter in Tír Chonaill, as of 1220, in
paraphrase of Through the Aegis, chapter five: its six magi and two
companions, its turb and specialists, its two towers and laboratories,
its devices, library, Lab Texts and vis; Prince Ruadan of the Tuatha Dé;
and its enemy, the nomadic Clan Mac Tire.

The magi live in a tower in a regio of 6 above a site of aura 5 in a
valley of aura 2. The cathach goes to the Tribunal through the `Hibernia`
record. Clan Mac Tire is an unofficial covenant with no cathach, so it is
on no Tribunal's roster. Stat blocks are the book's; the rest is a summary,
not its words. The book says Gaelic and the pack says Irish, for one
language; Lab Text and spell levels of a general spell are kept in words."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...arts import ART_LOOKUP
from ...models import Book, Character, CharterClause, Covenant, as_secrets, secret_words
from ...models.books import TEXT_ENCHANTMENT, TEXT_LONGEVITY, TEXT_OTHER, TEXT_SPELL
from ...models.devices import InstilledEffect
from ...models.world import FULL
from ..builder import (
    Builder,
    StatBlock,
    add_possession,
    arts_from,
    boons_hooks_from,
    characteristics,
    joined_lines,
    paragraphs,
    vf_art,
    vf_great,
    vf_puissant,
    vf_ward,
)

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Hibernia

SOURCE = "TtA"
NAME = "Longmist"
CLAN = "Clan Mac Tire"
BOOK = "Through the Aegis"
EX_MISCELLANEA = "house_ex_miscellanea"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"
TYTALUS = "house_tytalus"
BJORNAER = "house_bjornaer"
LATIN = "Latin"
IRISH = "Irish"

LUGH: StatBlock = {
    "characteristics": characteristics(3, 0, 0, 4, -1, 0, -1, -2),
    "aging_points": {"intelligence": 2, "communication": 2},
    "confidence": (1, 3),
    "decrepitude": (0, 4),
    "warping": (8, 20),
    "apparent_age": 90,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Elemental Magic",
        "Sihr",
        vf_art("Affinity with {art}", "Rego"),
        "Good Teacher",
        vf_great("Communication"),
        ("Minor Magical Focus", {"focus": "elemental spirits"}),
        ("Favors", {"detail": "airy spirit"}),
        "Twilight Prone",
        ("Driven (Minor)", {"detail": "for Hibernia to withdraw from the Order"}),
        ("Flawed Parma Magica", {"detail": "Corpus"}),
        "Slow Caster",
    ],
    "traits": {
        "Driven": 6,
        "Secretive": 3,
        "Unforgiving": 2,
        "Vain": 2,
        "Manipulative": 1,
    },
    "reputations": {
        "Beneficent master (spirits of Ulaid)": 3,
        "Isolationist (Hibernian magi)": 1,
    },
    "abilities": [
        ("Area Lore: Hibernia", 5, "personalities"),
        ("Artes Liberales", 4, "ritual magic"),
        ("Awareness", 3, "determining effect"),
        ("Bargain", 4, "spirits"),
        ("Concentration", 3, "spell concentration"),
        ("Faerie Lore", 3, "faeries of the waterways"),
        ("Finesse", 3, "targeting"),
        ("Guile", 3, "elaborate lies"),
        ("Intrigue", 4, "alliances"),
        ("Living Language: Irish", 5, "prose"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Leadership", 5, "elemental spirits"),
        ("Magic Lore", 5, "creatures"),
        ("Magic Theory", 11, "Longevity Rituals"),
        ("Organization Lore: Covenant of Longmist", 5, "history"),
        ("Organization Lore: Order of Hermes", 5, "politics"),
        ("Parma Magica", 4, "Auram"),
        ("Penetration", 5, "Auram"),
        ("Philosophiae", 4, "ritual magic"),
        ("Sihr", 11, ""),
    ],
    "arts": arts_from(
        "Cr 14, In 8, Mu 8, Pe 18, Re 19, An 5, Aq 18, Au 18, Co 19, He 5, "
        "Ig 17, Im 5, Me 10, Te 17, Vi 14"
    ),
    "spells": [
        ("Master the Airy Spirit of Aquam", "ReAq", 30, 0),
        ("Summon the Airy Spirit of Aquam", "ReAq", 35, 0),
        ("Master the Airy Spirit of Auram", "ReAu", 30, 0),
        ("Summon the Airy Spirit of Auram", "ReAu", 35, 0),
        ("Incantation of the Body Made Whole", "CrCo", 40, 0),
        ("Master the Airy Spirit of Ignem", "ReIg", 30, 0),
        ("Summon the Airy Spirit of Ignem", "ReIg", 35, 0),
        ("Reveal the Lingering Spirit", "InMe", 20, 0),
        ("Lay to Rest the Haunting Spirit", "PeMe", 20, 0),
        ("Coerce the Spirit of Anger", "ReMe", 20, 0),
        ("Coerce the Spirits of the Night", "ReMe", 20, 0),
        ("Master the Airy Spirit of Terram", "ReTe", 30, 0),
        ("Summon the Airy Spirit of Terram", "ReTe", 35, 0),
        ("The Invisible Eye Revealed", "InVi", 30, 0),
        ("Wizard's Communion", "MuVi", 20, 0),
        ("Wizard's Communion", "MuVi", 40, 0),
        ("Demon's Eternal Oblivion", "PeVi", 15, 0),
        ("Circular Ward Against Demons", "ReVi", 25, 0),
        ("Opening the Intangible Tunnel", "ReVi", 35, 0),
    ],
    "notes": paragraphs(
        "In truth an ancient man of bent bones, hollow eyes and cheeks and "
        "withered fingers; by illusion, healthy, robust and energetic, stern "
        "of gaze but pleasant enough. Casting sigil: a misty impression of "
        "the spell's target grows from his hands or device and fades within "
        "a round. Voting sigil: a silver medallion with a polished moonstone "
        "mounted through its middle.",
        "Combat: dodge Init +2, Defense +2; fist Init +2, Attack +1, Defense "
        "+2, Damage +1; staff of Lugh Init +2, Attack +1, Defense +2, Damage "
        "+1. Soak 0. Encumbrance 0. Longevity Ritual +13.",
        "Sihr is an Accelerated Ability. He knows 10 Names of Power, Arcane "
        "Connections to ten airy spirits. Levels of his general spells: "
        "Lay to Rest the Haunting Spirit 20; Wizard's Communion 20 and 40; "
        "Demon's Eternal Oblivion 15; Circular Ward Against Demons 25; "
        "Opening the Intangible Tunnel 35. Coerce the Spirit of Anger is "
        "from Houses of Hermes: Societates p. 99.",
    ),
}

CONCHOBOR: StatBlock = {
    "characteristics": characteristics(2, 1, -1, 2, 0, 2, -1, -1),
    "confidence": (1, 3),
    "warping": (6, 20),
    "apparent_age": 75,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        ("Major Magical Focus", {"focus": "commanding natural forces"}),
        ("Strong Faerie Blood", {"detail": "goblin"}),
        "Faerie Magic",
        "Good Teacher",
        ("Nature Lore", {"detail": "Underworld"}),
        "Second Sight",
        ("Deficient Technique", {"art": "Muto"}),
        ("Favors", {"detail": "Tuatha Dé"}),
        "Difficult Spontaneous Magic",
        ("Hatred (Minor)", {"detail": "Lugh"}),
    ],
    "traits": {"Hateful toward Lugh": 3, "Insular": 3, "Charming": -1},
    "reputations": {"Willing ally (Tuatha Dé)": 4},
    "abilities": [
        ("Area Lore: Ulaid", 4, "legends"),
        ("Artes Liberales", 3, "ceremonial magic"),
        ("Burrow Lore", 5, ""),
        ("Code of Hermes", 3, "Tribunal procedures"),
        ("Concentration", 3, "spell concentration"),
        ("Faerie Lore", 7, "the Tuatha Dé"),
        ("Faerie Magic", 5, "Intellego"),
        ("Finesse", 4, "precision"),
        ("Guile", 3, "lying concerning his magic"),
        ("Living Language: Irish", 5, "poetry"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Magic Lore", 6, "regiones"),
        ("Magic Theory", 10, "Intellego"),
        ("Merinita Cult Lore", 4, "Initiating self"),
        ("Organization Lore: Covenant of Longmist", 4, "history"),
        ("Organization Lore: Order of Hermes", 3, "politics"),
        ("Parma Magica", 6, "Mentem"),
        ("Penetration", 4, "Animal"),
        ("Philosophiae", 3, "ceremonial magic"),
        ("Second Sight", 6, "invisible faeries"),
        ("Underworld Lore", 5, "navigation"),
    ],
    "arts": arts_from(
        "Cr 9, In 18, Mu 12, Pe 9, Re 15, An 14, Aq 7, Au 9, Co 5, He 12, "
        "Ig 6, Im 6, Me 7, Te 9, Vi 11"
    ),
    "spells": [
        ("Image of the Beast", "InAn", 5, 0),
        ("Opening the Tome of the Animal's Mind", "InAn", 25, 0),
        ("To See as Others See", "InAn(Re)", 45, 0),
        ("The Gentle Beast", "ReAn", 25, 0),
        ("Viper's Gaze", "ReAn", 15, 0),
        ("Mastering the Unruly Beast", "ReAn", 25, 0),
        ("Ward Against the Beasts of Legend", "ReAn", 25, 0),
        ("Voice of the Lake", "InAq", 25, 0),
        ("Gathering of the Stormy Might", "ReAu", 40, 0),
        ("Stir the Slumbering Tree", "MuHe(Me)", 25, 0),
        ("Lord of the Trees", "ReHe", 25, 0),
        ("Calling the Council of the Trees", "ReHe(In)", 45, 0),
        ("Tales of the Ashes", "InIg", 5, 0),
        ("Leap of the Fire", "ReIg", 10, 0),
        ("The Obedient Fire", "ReIg", 20, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("Summoning the Distant Image", "InIm", 25, 0),
        ("Veil of Invisibility", "PeIm", 20, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Silence of the Smothered Sound", "PeIm", 20, 0),
        ("Sense the Feet that Tread the Earth", "InTe", 30, 0),
        ("Stone Tell of the Mind that Sits", "InTe", 30, 0),
        ("Earth Shock", "ReTe", 30, 0),
        ("Sense of Faerie Power", "InVi", 2, 0),
        ("Sense of Magical Power", "InVi", 2, 0),
        ("Opening the Intangible Tunnel", "ReVi", 30, 0),
    ],
    "notes": paragraphs(
        "Hunched and wrinkled, with short patchy white hair and hooded eyes "
        "forever watching from their corners. Small horns rise from his "
        "head. His left arm looks to be banded bronze, still youthful, and "
        "its weight drags that side down. Casting sigil: black mist swirls "
        "round his right arm and hand. Voting sigil: a large bronze brooch "
        "embossed and patterned round the edges. Twilight scar: his Parma "
        "Magica does not shield him from the effects of The Gift.",
        "Combat: dodge Init -1, Defense -1; fist Init -1, Attack -1, Defense "
        "-1, Damage 0; bludgeon Init -2, Attack +1, Defense -1, Damage +2. "
        "Soak +2. Encumbrance 1. Longevity Ritual +12.",
        "Strong Goblin Blood gives +1 to stealth totals, and Second Sight "
        "came with it. Nature Lore (Underworld) (Houses of Hermes: Mystery "
        "Cults p. 103) covers the tunnels beneath Longmist and the wider "
        "valley and what lives in them. To See as Others See is from Houses "
        "of Hermes: True Lineages p. 139; its Art is printed In(Re)An. "
        "Opening the Intangible Tunnel at level 30.",
    ),
}

CAILLEACH: StatBlock = {
    "characteristics": characteristics(3, -1, 0, 0, 0, 1, 1, 0),
    "confidence": (1, 3),
    "warping": (2, 1),
    "apparent_age": 31,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        ("Major Magical Focus", {"focus": "metals"}),
        "Adept Laboratory Student",
        "Inventive Genius",
        "Verditius Magic",
        ("Tormenting Master", {"detail": "Lugh-éccnaid and Conchobor"}),
        ("Driven (Minor)", {"detail": "prove her value at Longmist"}),
        ("Ability Block", {"detail": "Martial"}),
    ],
    "traits": {"Driven": 3, "Keen to venture out of the covenant": 2, "Practical": 1},
    "reputations": {
        "An ill-omen (elders and covenfolk of Longmist)": 3,
        "Studious (magi of Hibernia)": 1,
    },
    "abilities": [
        ("Craft: Armorer", 2, "mail"),
        ("Artes Liberales", 3, "ritual magic"),
        ("Craft: Blacksmith", 2, "steel working"),
        ("Code of Hermes", 2, "Tribunal procedures"),
        ("Concentration", 3, "spell concentration"),
        ("Dominion Lore", 1, "saints"),
        ("Faerie Lore", 1, "the Tuatha Dé"),
        ("Finesse", 2, "Craft Magic"),
        ("Infernal Lore", 1, "demons"),
        ("Living Language: Irish", 5, "poetry"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 1, "laboratory work"),
        ("Magic Lore", 1, "Irish magical traditions"),
        ("Magic Theory", 5, "enchanting items"),
        ("Parma Magica", 2, "Vim"),
        ("Penetration", 2, "Vim"),
        ("Philosophiae", 3, "enchantments"),
        ("Craft: Swordsmith", 2, "long sword"),
        ("Verditius Cult Lore", 2, "modifying Initiation scripts"),
    ],
    "arts": arts_from(
        "Cr 5, In 5, Mu 5, Pe 5, Re 5, An 0, Aq 0, Au 0, Co 3, He 0, Ig 0, "
        "Im 0, Me 2, Te 6, Vi 9"
    ),
    "spells": [
        ("A Visible Demand for Repair", "MuIm", 5, 0),
        ("Eyes of the Eons", "InTe", 10, 0),
        ("Rusted Decay of Ten-Score Years", "PeTe", 10, 0),
        ("The Crystal Dart", "MuTe(Re)", 10, 0),
        ("Fist of Shattering", "PeTe", 10, 0),
        ("Unseen Arm", "ReTe", 5, 0),
        ("The Unseen Porter", "ReTe", 10, 0),
        ("Piercing the Magical Veil", "InVi", 20, 0),
        ("Piercing the Faerie Veil", "InVi", 20, 0),
        ("Wizard's Communion", "MuVi", 20, 0),
    ],
    "notes": paragraphs(
        "Small, well-formed and fair, with green eyes and striking red hair, "
        "which goes tied and demurely veiled when she is not feeling "
        "rebellious. Casting sigil: a light red mist swirls round the target "
        "during the casting or device activation. Voting sigil: a highly "
        "polished disk of copper of remarkable clarity and evenness. She "
        "carries her Casting Tools.",
        "Combat: dodge Init 0, Defense 0; fist Init 0, Attack +1, Defense 0, "
        "Damage 0; knife Init 0, Attack +2, Defense 0, Damage +2. Soak +1. "
        "Encumbrance 1. Verditius Magic gives her +4 Shape and Material "
        "bonus (her Philosophiae and specialty) to future enchantments. A "
        "Visible Demand for Repair is from Houses of Hermes: Societates p. "
        "65; The Crystal Dart is printed Mu(Re)Te.",
    ),
}

EOCHAID: StatBlock = {
    "characteristics": characteristics(2, 0, 0, 0, 0, 1, 2, 0),
    "confidence": (1, 3),
    "warping": (2, 3),
    "apparent_age": 32,
    "virtues_flaws": [
        ("Inoffensive to {being}", {"being": "animals"}),
        "The Gift",
        "Hermetic Magus",
        ("Major Magical Focus", {"focus": "visual images"}),
        vf_art("Affinity with {art}", "Imaginem"),
        "Faerie Magic",
        "Difficult Longevity Ritual",
        ("Animal Companion", {"detail": "a mundane magpie"}),
        ("Weakness (Minor)", {"detail": "carousing"}),
    ],
    "traits": {"Convivial": 3, "Honest": 2, "Ambitious": -1},
    "reputations": {
        "Carouser (Longmist covenfolk)": 2,
        "Disobedient (Longmist magi)": 2,
        "Drunkard (magi of Hibernia)": 1,
    },
    "abilities": [
        ("Artes Liberales", 2, "ritual magic"),
        ("Awareness", 2, "determining effect"),
        ("Carouse", 2, "drinking songs"),
        ("Code of Hermes", 1, "Tribunal procedures"),
        ("Concentration", 3, "spell concentration"),
        ("Faerie Lore", 3, "the Tuatha Dé"),
        ("Faerie Magic", 4, "Imaginem"),
        ("Finesse", 2, "Imaginem"),
        ("Folk Ken", 2, "the opposite sex"),
        ("Guile", 2, "lying to authority"),
        ("Living Language: Irish", 5, "storytelling"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Magic Lore", 2, "creatures"),
        ("Magic Theory", 4, "Imaginem"),
        ("Music", 2, "sing"),
        ("Organization Lore: Covenant of Longmist", 2, "politics"),
        ("Organization Lore: Order of Hermes", 1, "politics"),
        ("Parma Magica", 1, "Corpus"),
        ("Philosophiae", 2, "ceremonial magic"),
    ],
    "arts": arts_from(
        "Cr 5, In 5, Mu 5, Pe 5, Re 5, An 0, Aq 0, Au 0, Co 5, He 0, Ig 0, "
        "Im 14, Me 0, Te 0, Vi 0"
    ),
    "spells": [
        ("Phantasmal Animal", "CrIm", 20, 0),
        ("Phantasm of the Human Form", "CrIm", 25, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("Summoning the Distant Image", "InIm", 25, 0),
        ("Notes of a Delightful Sound", "MuIm", 10, 0),
        ("Disguise of the Transformed Image", "MuIm", 15, 0),
        ("Veil of Invisibility", "PeIm", 20, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Wizard's Communion", "MuVi", 10, 0),
    ],
    "notes": paragraphs(
        "Pale skin, very black hair and dark eyes, always ready with a smile, "
        "though among magi he usually looks apologetically contrite. Casting "
        "sigil: mist seeps through the ground round the caster. Voting sigil: "
        "a disk of lead and iron with a horseshoe inscribed on the leaden "
        "side. He squirrels food scraps into a belt pouch for his magpie, and "
        "tries a different would-be talisman each time to see what feels "
        "right.",
        "Combat: dodge Init 0, Defense 0; fist Init 0, Attack +2, Defense 0, "
        "Damage 0. Soak +1. Encumbrance 0.",
    ),
}

DARA: StatBlock = {
    "characteristics": characteristics(1, 0, 3, 2, -1, 0, -1, -1),
    "confidence": (1, 3),
    "warping": (1, 7),
    "apparent_age": 28,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Elemental Magic",
        "Sihr",
        ("Minor Magical Focus", {"focus": "elemental spirits"}),
        vf_puissant("Sihr"),
        ("Cautious with {ability}", {"ability": "Sihr"}),
        (
            "Dark Secret",
            {"detail": "killed a druid while undertaking his macgnímartha"},
        ),
        "Twilight Prone",
        "Fragile Constitution",
        "Humble",
    ],
    "traits": {"Humble": 3, "Questioning": 3, "Impulsive": 2, "Friendly": 1},
    "reputations": {
        "Inexperienced (spirits of Ulaid, druids of Connacht, the Fir Bolg)": 2,
        "Spent time in Connacht (magi of Hibernia)": 1,
    },
    "abilities": [
        ("Area Lore: Connacht", 2, "history"),
        ("Artes Liberales", 1, "ritual magic"),
        ("Athletics", 2, "running"),
        ("Bargain", 4, "summoned spirits"),
        ("Charm", 2, "first impressions"),
        ("Concentration", 3, "spell concentration"),
        ("Faerie Lore", 2, "faerie spirits"),
        ("Living Language: Irish", 5, "storytelling"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Magic Lore", 2, "magical spirits"),
        ("Magic Theory", 4, "Mentem"),
        ("Organization Lore: Covenant of Longmist", 2, "history"),
        ("Organization Lore: Order of Hermes", 1, "history"),
        ("Parma Magica", 2, "Vim"),
        ("Penetration", 2, "Rego"),
        ("Philosophiae", 2, "ritual magic"),
        ("Sihr", 8, "earth spirits"),
    ],
    "arts": arts_from(
        "Cr 2, In 5, Mu 3, Pe 6, Re 6, An 0, Aq 0, Au 3, Co 5, He 0, Ig 0, "
        "Im 0, Me 7, Te 0, Vi 5"
    ),
    "spells": [
        ("Charm Against Putrefaction", "CrCo", 10, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("Words of the Unbroken Silence", "CrMe", 10, 0),
        ("Reveal the Lingering Spirit", "InMe", 20, 0),
        ("Lay to Rest the Haunting Spirit", "PeMe", 10, 0),
        ("Tip of the Tongue", "PeMe", 5, 0),
        ("Wizard's Communion", "MuVi", 15, 0),
        ("Demon's Eternal Oblivion", "PeVi", 10, 0),
        ("Dreadful Bane of the Fae", "PeVi", 10, 0),
        ("Lash the Wayward Spirit", "PeVi", 10, 0),
        ("Circular Ward Against Demons", "ReVi", 10, 0),
    ],
    "notes": paragraphs(
        "A handsome, very slender, well-proportioned man with thick chestnut "
        "hair. The belt of his robe is strung with sticks, rabbit feet, herbs "
        "and old wooden spoons, remnants of Arcane Connections to spirits he "
        "has met. He carries a satchel of vials and flasks, always ready for "
        "samples. Casting sigil: a misty outline of the target forms between "
        "caster and target and fades. Voting sigil: an iron disk, thick and "
        "roughly beaten.",
        "Combat: dodge Init -1, Defense -1; fist Init -1, Attack -1, Defense "
        "-1, Damage -1; knife Init -1, Attack 0, Defense -1, Damage +1; "
        "bludgeon Init -2, Attack +1, Defense -1, Damage +1. Soak 0. "
        "Encumbrance 1. Sihr is 8 and +2 from Puissant.",
    ),
}

MICHEAL: StatBlock = {
    "characteristics": characteristics(2, 0, -1, 2, 0, 3, -1, -2),
    "confidence": (2, 5),
    "warping": (2, 9),
    "apparent_age": 34,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Mercurian Magic",
        "Mystical Choreography",
        vf_puissant("Artes Liberales"),
        vf_puissant("Philosophiae"),
        "Mastered Spells",
        "Self-Confident",
        "Blatant Gift",
        "Pagan (Major)",
        ("Deleterious Circumstances", {"detail": "when not casting from a circle"}),
    ],
    "traits": {
        "Calculating": 3,
        "Hatred for Bjornaer magi": 2,
        "Taciturn": 2,
        "Honest": 1,
    },
    "reputations": {
        "Adherent of tradition (elders of Longmist)": 3,
        "Pagan (magi of Hibernia)": 1,
    },
    "abilities": [
        ("Artes Liberales", 3, "ritual magic"),
        ("Athletics", 2, "running"),
        ("Awareness", 2, "determining effect"),
        ("Brawl", 2, "fist"),
        ("Code of Hermes", 2, "wizards' marches"),
        ("Concentration", 3, "spell concentration"),
        ("Finesse", 3, "precision"),
        ("Infernal Lore", 2, "demons"),
        ("Living Language: Irish", 5, "prose"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 2, "magi"),
        ("Magic Lore", 3, "magical traditions"),
        ("Magic Theory", 5, "Vim"),
        ("Organization Lore: Covenant of Longmist", 2, "history"),
        ("Parma Magica", 2, "Vim"),
        ("Penetration", 3, "Vim"),
        ("Philosophiae", 3, "ceremonial magic"),
    ],
    "arts": arts_from(
        "Cr 6, In 4, Mu 4, Pe 5, Re 6, An 4, Aq 0, Au 1, Co 5, He 0, Ig 1, "
        "Im 0, Me 4, Te 0, Vi 8"
    ),
    "spells": [
        ("Doublet of Impenetrable Silk", "MuAn", 15, 1),
        ("Bind Wound", "CrCo", 10, 1),
        ("The Chirurgeon's Healing Touch", "CrCo", 20, 1),
        ("Disguise of the New Visage", "MuCo", 15, 1),
        ("The Wound that Weeps", "PeCo", 15, 0),
        ("Sight of the Transparent Motive", "InMe", 10, 0),
        ("The Unseen Porter", "ReTe", 10, 1),
        ("Wizard's Communion", "MuVi", 30, 0),
        ("Demon's Eternal Oblivion", "PeVi", 15, 1),
        ("Circular Ward Against Demons", "ReVi", 20, 2),
        ("Watching Ward", "ReVi", 30, 1),
    ],
    "masteries": {
        "Doublet of Impenetrable Silk": ["Ceremonial Casting"],
        "Bind Wound": ["Ceremonial Casting"],
        "The Chirurgeon's Healing Touch": ["Stalwart Casting"],
        "Disguise of the New Visage": ["Ceremonial Casting"],
        "The Unseen Porter": ["Multiple Casting"],
        "Demon's Eternal Oblivion": ["Penetration"],
        "Circular Ward Against Demons": ["Ceremonial Casting", "Penetration"],
        "Watching Ward": ["Stalwart Casting"],
    },
    "notes": paragraphs(
        "Always frowning, in disapproval or deep thought, his hair thin and "
        "short, his robes and white tabard spotless. Under them he bears the "
        "scars of many bites and gashes. Casting sigil: the target trembles "
        "slightly through the casting and sheds a light mist, as shaken "
        "stonework sheds dust. Voting sigil: a small gold disk with the "
        "impression of a crown punched into it.",
        "Combat: dodge Init -2, Defense 0; knife Init -2, Attack +2, Defense "
        "0, Damage +2; fist Init -2, Attack +2, Defense +1, Damage 0. Soak +3, "
        "and a further +3 when Doublet of Impenetrable Silk is cast on his "
        "robe. Encumbrance 0.",
        "Artes Liberales and Philosophiae are each 3 and +2 from Puissant. "
        "Mystical Choreography is in Houses of Hermes: Societates p. 56. His "
        "satchel of prepared props (candles, herbs, auspicious stones, "
        "transcripts of the Vitae Magnae) gives +3 to spells cast "
        "ceremonially as medium props; it holds props for three spells, "
        "chosen before he sets out, or all of them with a packhorse, which "
        "the covenant lacks.",
        "His future talisman is Partholon's Crown, kept by the covenant's Censors.",
    ),
}

BRAN: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 0, 1, 0, 2, 2),
    "size": 1,
    "confidence": (1, 3),
    "warping": (0, 4),
    "apparent_age": 34,
    "virtues_flaws": [
        "Knight",
        "Faeborchless",
        "Large",
        "Reserves of Strength",
        "Warrior",
        "Difficult Underlings",
        "Covenant Upbringing",
        ("Prohibition", {"detail": "must not suffer a dog in his house"}),
    ],
    "traits": {"Daring": 3, "Conflicted Loyalties": 2, "Boastful": 1},
    "abilities": [
        ("Area Lore: Ulaid", 4, "geography"),
        ("Athletics", 3, "running"),
        ("Brawl", 4, "fist"),
        ("Carouse", 2, "games of chance"),
        ("Chirurgy", 3, "setting bones"),
        ("Etiquette", 2, "faeries"),
        ("Great Weapon", 3, "long spear"),
        ("Hunt", 3, "tracking"),
        ("Living Language: Irish", 5, "slang"),
        ("Leadership", 5, "in combat"),
        ("Organization Lore: Covenant of Longmist", 3, "politics"),
        ("Organization Lore: Order of Hermes", 2, "history"),
        ("Ride", 5, "battle"),
        ("Single Weapon", 5, "sparra"),
        ("Survival", 1, "peat bogs"),
        ("Swim", 1, "diving"),
    ],
    "notes": paragraphs(
        "Long-limbed, a head taller than most of the grogs he leads. He has "
        "round shield, full chain mail and a horse; the arms and armor were "
        "handed down and altered to fit, and by City & Guild's rules the "
        "armor has one Damage Level left. He wants new gear for himself and "
        "his men (prices in City & Guild p. 144).",
        "Combat: dodge Init -1, Defense +6; fist Init -1, Attack +7, Defense "
        "+7, Damage +1; dagger Init -1, Attack +8, Defense +6, Damage +4; "
        "sparra and round shield Init 0, Attack +12, Defense +10, Damage +7; "
        "long spear mounted Init +1, Attack +14, Defense +10, Damage +6; long "
        "spear Init +2, Attack +9, Defense +7, Damage +8. Soak +9. "
        "Encumbrance 4.",
        "Faeborchless, the Dancing Shield Feat "
        "(printed among his Virtues before the Minor ones), a Cles learned "
        "from Úathach of Leth Cuinn. He throws his shield or weapon to "
        "defend as many characters as his Single or Great Weapon Ability, "
        "on a Dexterity + that Ability feat check against Ease Factor 9. "
        "On success they are defended and it returns to his hands; on "
        "failure he must fetch it, and may be left defenseless.",
    ),
}

EAMONN: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 3, -1, 0, 0, 0),
    "confidence": (1, 3),
    "warping": (0, 4),
    "apparent_age": 27,
    "virtues_flaws": [
        ("Faerie Blood", {"detail": "Sidhe"}),
        "Bard",
        "Educated (Bardic)",
        "Enchanting Storytelling",
        "Free Expression",
        ("Dependent", {"detail": "his ailing mother"}),
        "Carefree",
    ],
    "traits": {"Confident": 3, "Friendly": 2, "Extroverted": 1},
    "abilities": [
        ("Area Lore: Ulaid", 3, "personalities"),
        ("Art of Memory", 3, "poetry"),
        ("Awareness", 3, "alertness"),
        ("Brawl", 2, "fist"),
        ("Carouse", 2, "drinking songs"),
        ("Charm", 4, "first impressions"),
        ("Enchanting Storytelling", 5, "love"),
        ("Folk Ken", 3, "peasants"),
        ("Living Language: Irish", 5, "storytelling"),
        ("Legerdemain", 4, '"magic" tricks'),
        ("Organization Lore: Covenant of Longmist", 1, "personalities"),
        ("Organization Lore: Uí hEódhasa", 1, "history"),
        ("Poet", 2, "the Ulaidh Cycle"),
        ("Storyteller", 5, "heroic battles"),
        ("Survival", 1, "roadside"),
    ],
    "notes": paragraphs(
        "A handsome young man with the Sidhe's refinement in his blood, "
        "sparkling blue eyes, bouncy blond hair and an easy smile: every "
        "father's nightmare and every husband's fear. Good quality clothes.",
        "Combat: dodge Init 0, Defense +2; fist Init 0, Attack +3, Defense "
        "+3, Damage -1; knife Init 0, Attack +3, Defense +2, Damage +1; "
        "bludgeon Init -1, Attack +4, Defense +2, Damage +1. Soak 0. "
        "Encumbrance 1.",
        "Enchanting Storytelling works as Enchanting Music with stories. His "
        "Dependent is his mother, weak since an illness and likely to lose "
        "her home without him.",
    ),
}

GROG: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 0, 2, 2, 1, 0),
    "warping": (0, 4),
    "apparent_age": 25,
    "virtues_flaws": [
        "Covenfolk",
        "Warrior",
        "Tough",
        "Poor Living Conditions",
        ("Weakness (Minor)", {"detail": "drinking"}),
    ],
    "traits": {"Brave": 3, "Lazy": 2, "Loyal": 1},
    "abilities": [
        ("Area Lore: Longmist lands", 3, "geography"),
        ("Athletics", 3, "climbing"),
        ("Awareness", 3, "keeping watch"),
        ("Brawl", 4, "fist"),
        ("Carouse", 4, "power drinking"),
        ("Chirurgy", 1, "binding wounds"),
        ("Living Language: Irish", 5, "storytelling"),
        ("Organization Lore: Covenant of Longmist", 2, "personalities"),
        ("Single Weapon", 5, "sparra"),
        ("Stealth", 2, "natural areas"),
        ("Survival", 2, "woodland"),
        ("Swim", 3, "diving"),
        ("Thrown Weapon", 4, "throwing ax"),
    ],
    "notes": paragraphs(
        "The block stands for each of the six grogs under Bran. Dirty, in "
        "thick wool against the cold mists, drying their oiled leather shoes "
        "by the fire; they look more like brigands than toll collectors. "
        "They carry partial leather scale armor patched down to one Damage "
        "Level, round shield, sparra, short spear, two throwing axes, eating "
        "knife, warm cloak and light camping gear.",
        "Combat: dodge Init 0, Defense +4; fist Init 0, Attack +6, Defense "
        "+5, Damage +2; kick Init -1, Attack +5, Defense +3, Damage +5; knife "
        "Init 0, Attack +6, Defense +4, Damage +4; sparra and round shield "
        "Init 0, Attack +11, Defense +8, Damage +8; short spear and round "
        "shield Init +1, Attack +8, Defense +7, Damage +7; throwing ax Init "
        "0, Attack +8, Defense +5, Damage +8. Soak +8. Encumbrance 1.",
        "No leader among them: they have trained as a group, but fight as an "
        "untrained one without their captain. Loyal more from habit than "
        "wish, and lazy; they complain of work but are rarely pushed. Poor "
        "Living Conditions is -1 Living Conditions Modifier, from days "
        "spent living off the land.",
    ),
}

MAGI = (
    (
        "lugh",
        "Lugh-éccnaid",
        EX_MISCELLANEA,
        125,
        LUGH,
        "Of the Younger House, atop the greater tower where he watches all "
        "that happens, and in his own eyes the rightful leader. He has "
        "opposed the coming of continental magi for fifty years, and having "
        "lost the argument he stopped going to Tribunal and dropped friends "
        "turned enemies, fearing the native Order will be pushed aside as "
        "the Fir Bolg, the Tuatha Dé and the druids were. Propraetor: he has "
        "the last word on relations outside the covenant and has closed them "
        "to all who take a lenient view. A Corrguineach (Houses of Hermes: "
        "Societates p. 109), he summons spirits as his eyes, ears and "
        "agents, some holding Aegis tokens kept in his sanctum. He is the "
        "covenant's Corpus specialist and maker of its Longevity Rituals. "
        "Vain, he wears youthful illusion.",
        "He has written polemics for Hibernia to secede and set its own "
        "Code, with residency only for magi who can show three generations "
        "in Hibernia; none is in the library or yet circulated, though Dara "
        "knows of them. He has read in the Lebor Feasa Runda that drinkers "
        "of Tobar Segais, on the plain of Mag Mell, on Tir Na nÓg, ruled by "
        "the giant Fomórach, live forever. His age is outrunning his ritual, "
        "and he may soon send his filius for that water.",
    ),
    (
        "conchobor",
        "Conchobor Crosach",
        MERINITA,
        112,
        CONCHOBOR,
        "He keeps sanctum and laboratory underground among the cellars and "
        "cisterns, has not left the covenant in many years, and meets princes "
        "and envoys of the Tuatha Dé there in the dark; those ties, he holds, "
        "make him Longmist's natural leader. An isolationist whose concern "
        "stops at the gates, he shares his allies' enmity for the Fir Bolg "
        "and the Fomórach. Demanding and suspicious of his fellows since a "
        "Twilight left his Parma no shield against The Gift. Praefectus: "
        "nominally the security of the lands outside the Aegis, which he has "
        "been stretching over everything that comes from outside, vis "
        "sources and stocks included.",
        "The Tuatha Dé still hold a powerful Arcane Connection to him, a "
        "coin Ruadan forged from his pain, since he tried to master them "
        "with his glove's first power.",
    ),
    (
        "cailleach",
        "Cailleach Dhé Dherg",
        VERDITIUS,
        31,
        CAILLEACH,
        "Known as the Cailleach to all, and the only maga now at Longmist; "
        "her apprenticeship caused much argument, her parens Tadhg an Tuir "
        "holding firm against the council though it appealed to House "
        "Bonisagus. She is admonished for going with her hair uncovered. "
        "She means to learn to repair and wake the bronze man in the "
        "courtyard, which is close to past repair, and that will take her "
        "outside the walls. These two years she has given to her laboratory, "
        "with its great forge, and her talisman; Lugh dislikes the work. In "
        "her macgnímartha she was laboratory assistant to an itinerant "
        "Verditius called Peter, learning her House's secrets ahead of her "
        "Initiations.",
        "",
    ),
    (
        "dara",
        "Dara Connachtach",
        EX_MISCELLANEA,
        28,
        DARA,
        "Of the Younger House, the youngest and last gauntleted, treated as "
        "an inexperienced junior though only three years behind the "
        "Cailleach. Lugh's former apprentice and a Corrguineach, he summons, "
        "bargains with and controls elemental spirits, and has spent time "
        "among the druids of Connacht and the Fir Bolg. He respects and "
        "fears his parens, but does not share Lugh's view of the Order.",
        "In his beardless years he travelled with Brea, a man schooled in "
        "spirits, and against Brea's advice and out of bravado summoned one "
        "he could not control. It attacked them; Dara ran, and the druid "
        "died. He has told no one at Longmist. Something unseen meddles "
        "with his laboratory, and he fears what it may be.",
    ),
    (
        "eochaid",
        "Eochaid Dubh",
        MERINITA,
        32,
        EOCHAID,
        "Conchobor's former apprentice, an accomplished illusionist who has "
        "put off the Merinita Mysteries for Imaginem and is now warming to "
        "them. Easily led, weak for music and carousing, he is often made to "
        "eat apart for joining the covenfolk's revels. He has no talisman or "
        "familiar yet but has readied his laboratory, and risks more "
        "punishment smuggling scraps to a magpie that visits him. He drank "
        "his way round Hibernia in his macgnímartha, The Gift and the drink "
        "putting him in harm's way more than once. He knows the Tuatha Dé "
        "but does not trust their motives.",
        "",
    ),
    (
        "micheal",
        "Mícheál Amhreaidh",
        TYTALUS,
        34,
        MICHEAL,
        "Censor, master of rituals, who leads the communions and answers for "
        "the younger magi's conduct. The rest are nominally Christian, but "
        "he was taught to venerate the goddess Domnu; he reasons that she is "
        "a primal Kosmokrator (Realms of Power: Magic p. 109) subject to a "
        "greater power, yet keeps his faith, and his devotion is known across "
        "the Tribunal. He hopes to see the old magics of Ireland joined to "
        "Magic Theory. In his macgnímartha, among the old pagan sites, the "
        "Bjornaer of Clan Mac Tire fell on him; a Fir Bolg war band rescued "
        "him gravely wounded, and he has hated all Bjornaer since.",
        "",
    ),
)

PEOPLE: tuple[tuple[str, str, str, int, StatBlock, str, str], ...] = (
    (
        "bran",
        "Bran in Gai Móir",
        "companion",
        34,
        BRAN,
        "Turb captain, who distrusts Conchobor's allies and so favors Lugh. "
        "Trained in the clesa by Úathach of the Tuatha Dé (The Contested "
        "Isle). He is married to Ailbhe, eight years younger; they are "
        "childless, and he blames an enchantment of the magi. His resentment "
        "is growing and he may soon confront them, and they may have to "
        "research fertility magic.",
        "He is under no Longevity Ritual, so their childlessness is not its doing.",
    ),
    (
        "eamonn",
        "Éamonn Cruittire",
        "companion",
        27,
        EAMONN,
        "Éamonn Cruittire mac Aindileas Uí hEódhasa, of the line of Baile Uí "
        "Eódhasa, magical bards of the Ulaidh, whose power to enchant through "
        "story goes from father to son. He carries tales of old battles and "
        "feuds through Ulaid. He values his family's tie to Longmist, finds "
        "Conchobor unsettling and distrusts Lugh far more, scorns the magi's "
        "staid life and their ban on music, is fond of the villagers, and "
        "enjoys his sway over his friend Eochaid.",
        "",
    ),
    (
        "grog",
        "Longmist Grog",
        "grog",
        25,
        GROG,
        "The six grogs of the turb, for the most part on the toll bridge, on "
        "escort to market, or now and then on guard or seeing off giants.",
        "",
    ),
)

#: Covenfolk with no printed block: name, age, what the book says.
FOLK: tuple[tuple[str, str, int | None, str], ...] = (
    (
        "columb",
        "Columb Brathair",
        70,
        "The penitent monk, priest and confessor, a fallen priest whose "
        "diabolic excesses Calvacius and Tadhg an Tuir found out; he threw "
        "himself on their mercy and for reasons unclear they brought him "
        "here. Appears 65. Longevity Ritual -4. Communication +1, Teaching "
        "(Infernal Lore) 6, Infernal Lore 8, Dominion Lore 8. Teacher, 15 "
        "Build Points.",
    ),
    (
        "cathal",
        "Cathal Gobha",
        40,
        "The blacksmith, five years under a Longevity Ritual. Warping has "
        "made him Offensive to Animals, so he leaves farrier work to his son. "
        "His forge is rarely active. Communication +1, Teaching (Blacksmith) "
        "6, Craft: Blacksmith 8. Teacher, 15 Build Points. His workshop, 45 "
        "Build Points, has Innovation +3 and Raw Materials +2 (City & Guild "
        "p. 65), and makes Superior goods. Blacksmith to the voting sigils, "
        "which are always metal.",
    ),
    (
        "cinaed",
        "Cináed mac Cathail",
        None,
        "Cathal's son and only apprentice, who would rather be a grog, has "
        "no love for the English, and hopes Longmist will one day stand "
        "against them. Dexterity +3, Craft: Blacksmith 4. 4 Build Points.",
    ),
    (
        "una",
        "Úna",
        40,
        "The herbwife, who has refused magical help with aging, trusting her "
        "own compounds. Intelligence +1, Profession: Herbalist 7, Chirurgy "
        "5. 7 Build Points. Married to the farmer Cormac; villagers bring "
        "her their knocks and scrapes.",
    ),
    (
        "iomhar",
        "Íomhar",
        36,
        "Librarian since old Thomas passed, frustrated to lack his "
        "predecessors' rigor, and eager for any way to improve. Intelligence "
        "0, Profession: Librarian 7. 7 Build Points.",
    ),
    (
        "maghnus",
        "Maghnus",
        39,
        "The scribe, slovenly in person and workshop, but fluent in Latin, "
        "Greek, Gaelic, French and German. Dexterity +1, Profession: Scribe "
        "7. 7 Build Points.",
    ),
    (
        "piaras",
        "Piaras",
        56,
        "The percamenarius, morose and withdrawn, whose vellum other "
        "covenants have sought. Appears 50. Longevity Ritual -4. Dexterity "
        "+3, Craft: Parchment 9 (uterine vellum). 9 Build Points, with 45 "
        "for his workshop (Innovation +2, Raw Materials +3). Warping has "
        "Disfigured his skin to thin white parchment, veins and pulse "
        "showing through. His four vernacular manuals on the skins of cows, "
        "sheep, goats and magical beasts each add +3 to other parchment "
        "makers' Craft Totals (City & Guild p. 73), 12 Build Points.",
    ),
    (
        "maol_phoil",
        "Maol Phóil",
        None,
        "Piaras's assistant, as morose, and growing jealous and impatient. "
        "Craft: Parchment 5. 5 Build Points.",
    ),
    (
        "fearghal",
        "Fearghal",
        36,
        "The animal handler, last of the team that served Longmist's kennels "
        "and stables when kings hunted here; he tends the rare horse, advises "
        "on sick livestock and keeps the bees. Dexterity +2, Animal Handling "
        "7. 7 Build Points.",
    ),
)
FOLK_SECRETS = {
    "una": "For some years she has been cuckolding Cormac with Fearghal.",
    "fearghal": "He commits adultery with Úna, a sin he forgives himself.",
}

#: covenant key or magus key, name, characteristics, specializations, words.
LABS: tuple[tuple[str, dict[str, int], dict[str, int], int, str], ...] = (
    (
        "lugh",
        {
            "refinement": 5,
            "general_quality": 3,
            "upkeep": 8,
            "safety": 8,
            "health": 1,
            "aesthetics": 7,
        },
        {"Longevity Rituals": 11, "Teaching": 1, "Creo": 1, "Auram": 1},
        116,
        "The top of the greater tower, enlarged across two floors: work below "
        "round a great cauldron, and above a gallery for contemplation, "
        "writing, and his personal library and stores. Highly specialized for "
        "Longevity Rituals. Upkeep 36 Mythic Pounds a year. Virtues: Greater "
        "Feature (Cauldron), Highly Organized, Priceless Ingredients, "
        "Spotless, Spacious, Gallery, Elevated, Greater Expansion. Flaws: "
        "Greater Focus (Cauldron). Size +0 (0). Marker: none added. 60 Build "
        "Points.",
    ),
    (
        "conchobor",
        {
            "refinement": 6,
            "general_quality": 1,
            "safety": 4,
            "warping": 2,
            "health": -1,
            "aesthetics": 3,
        },
        {
            "Experimentation": 2,
            "Binding Familiar": 1,
            "Intellego": 4,
            "Rego": 1,
            "Terram": 2,
        },
        117,
        "Cold, dark and deep, a spacious chamber of rocky steps and platforms "
        "round a slowly turning orb of granite held over a still clear pool. "
        "He claims nothing for the orb, but visitors have glimpsed the world "
        "beyond Longmist in it. Within the Aegis, yet a nearby gateway to the "
        "Otherworld lets pixies, brownies and other fair folk in to watch, "
        "listen and sometimes help unasked. Upkeep 1 Mythic Pound a year. "
        "Virtues: Spacious, Faerie Ingredients, Greater Feature (Orb), Lesser "
        "Feature (Pool). Flaws: Gateway, Subterranean, Gremlins. Size +0 (0). "
        "Marker: none added. 50 Build Points.",
    ),
    (
        "cailleach",
        {
            "size": -2,
            "refinement": 2,
            "general_quality": -1,
            "safety": 3,
            "aesthetics": 2,
        },
        {"Enchanting Items": 8},
        117,
        "A forge dominates, the outer walls pierced by iron hollows and "
        "chimneys, its bellows reverberating as the fire reaches magically "
        "high heats. Cathal Gobha makes and keeps up her superior tools, so "
        "they add no Upkeep. Upkeep 1 Mythic Pound a year. Virtues: Greater "
        "Feature (Forge), Highly Organized, Superior Tools. Flaws: Greater "
        "Focus (Forge). Size +0 (-2). Marker: Conchobor Crosach, "
        "Lugh-éccnaid. 20 Build Points.",
    ),
    (
        "dara",
        {"general_quality": -2, "warping": 1, "aesthetics": 1},
        {"Inventing Spells": 5, "Rego": 2, "Mentem": 2},
        117,
        "Dominated by a summoning circle built into a raised circular dais, "
        "the equipment lining the walls. Upkeep 1 Mythic Pound a year. "
        "Virtues: Greater Feature (Summoning Circle). Flaws: Greater Focus "
        "(Summoning Circle), Haunted. Size +0 (0). Marker: Conchobor Crosach, "
        "Lugh-éccnaid. 20 Build Points.",
    ),
    (
        "eochaid",
        {
            "refinement": 1,
            "general_quality": -1,
            "upkeep": 2,
            "safety": -1,
            "aesthetics": 2,
        },
        {"Imaginem": 10},
        117,
        "Stark brilliant white, walls plastered smooth and painted the most "
        "unnatural white to be had. A near floor-to-ceiling round window in "
        "the curved outer wall is reflected in hand-sized mirrors along the "
        "inner one, each at its own angle or depth. Scores of candles light "
        "it (he has promised something cheaper), and equipment is kept from "
        "the walls, which makes it awkward. Upkeep 3 Mythic Pounds a year. "
        "Virtues: Greater Feature (Mirror), Lesser Feature (Window), "
        "Excessive Lighting, Highly Organized. Flaws: Greater Focus (Mirror), "
        "Awkward Shape. Size +0 (0). Marker: Conchobor Crosach, Lugh-éccnaid. "
        "40 Build Points.",
    ),
    (
        "micheal",
        {
            "refinement": 2,
            "general_quality": 1,
            "safety": 2,
            "aesthetics": 2,
        },
        {"Inventing Spells": 1, "Vim": 1},
        117,
        "A year's enhancement: two seasons' refinement, then a pentagon's "
        "Auspicious Shape and a Summoning Circle engraved in the floor. He "
        "means to add an Antechamber and a Balcony. Upkeep 1 Mythic Pound a "
        "year. Virtues: Auspicious Shape, Highly Organized, Lesser Feature "
        "(Summoning Circle). Size +0 (0). Marker: Conchobor Crosach, "
        "Lugh-éccnaid. 20 Build Points.",
    ),
)
EMPTY_LAB = {
    "size": -1,
    "general_quality": -1,
    "upkeep": -2,
    "safety": -1,
    "aesthetics": -2,
}
MOBILE_LAB = {"upkeep": -1, "safety": -2, "health": -5, "aesthetics": -3}

#: type, name, author, subject, level, quality, language, words.
LIBRARY: tuple[tuple[str, str, str, str, int | None, int, str, str], ...] = (
    (
        "Tractatus",
        "The Llancarfan Saints' Lives",
        "The Monks of Llancarfan",
        "Dominion Lore",
        None,
        6,
        LATIN,
        "A twelfth-century book, so trade went on within the last fifty or so years.",
    ),
    (
        "Tractatus",
        "The Manor of the Túatha Dé Danann",
        "Fergus of Merinita",
        "Faerie Lore",
        None,
        7,
        LATIN,
        "On the Tuatha Dé, and on Ruadan above all.",
    ),
    (
        "Ability Summa",
        "De Operationes Daemonum Dialogus",
        "Michael Psellos",
        "Infernal Lore",
        5,
        12,
        LATIN,
        "Small and clearly old, seemingly in many hands; a strange affliction "
        "does the same to any copy.",
    ),
    (
        "Tractatus",
        "The Wisdom of Fionntan",
        "Fergus of Merinita",
        "Magic Lore",
        None,
        6,
        LATIN,
        "Fergus's Latin record of a talk with an old druid, touching on the "
        "old magic of Hibernia.",
    ),
    (
        "Tractatus",
        "Remembered Ways",
        "Callum of the Younger House",
        "Sihr",
        None,
        8,
        IRISH,
        "Old, and annotated by many later hands.",
    ),
    (
        "Tractatus",
        "Lebor Liathanach",
        "Brea Mac Boru",
        "Sihr",
        None,
        8,
        IRISH,
        "Under 25 years old and clearly not by a Hermetic hand; given to the "
        "covenant by the druid.",
    ),
    (
        "Tractatus",
        "The Ascendence of Hermetic Ways",
        "Lugh-éccnaid",
        "Sihr",
        None,
        10,
        IRISH,
        "Argues that Hermetic methods have eclipsed the ancient ways of summoning.",
    ),
    (
        "Tractatus",
        "In innectis de phylacterium",
        "Cearnach of Verditius",
        "Magic Theory",
        None,
        8,
        LATIN,
        "Casts Magic Theory as a mechanism built of the Arts, and the "
        "Mysteries as mere use of it.",
    ),
    (
        "Tractatus",
        "Bonisagi Apocrypha",
        "Calvacius of Tytalus",
        "Magic Theory",
        None,
        8,
        LATIN,
        "Holds that covenants should research their own enhancements outside "
        "Bonisagus control.",
    ),
    (
        "Tractatus",
        "Codex of Enchantments",
        "Tadhg an Tuir of Verditius",
        "Magic Theory",
        None,
        9,
        LATIN,
        "Principles shown through simple enchantments known across the Order. "
        "It leans on calculations in another text, now missing, at a "
        "three-day distraction.",
    ),
    (
        "Tractatus",
        "Ars Accuratio",
        "Niall of the Younger House",
        "Finesse",
        None,
        7,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Per de Delicatum",
        "Calvacius of Tytalus",
        "Finesse",
        None,
        8,
        LATIN,
        "The reader has the Slow Caster Flaw during the season of study, "
        "copying Calvacius's technique.",
    ),
    (
        "Tractatus",
        "In Demonstratio Vi",
        "Niall of the Younger House",
        "Penetration",
        None,
        7,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Libro Fortitudo",
        "Marcus Cordo of Flambeau",
        "Penetration",
        None,
        8,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Scutum Quod Protegit Nobis",
        "Hannewalt of Tytalus",
        "Parma Magica",
        None,
        8,
        LATIN,
        "A guide to practice; two magi must study it at once.",
    ),
    (
        "Tractatus",
        "In Praesidia Praebuit Per Magica Formae",
        "Marcus Cordo of Flambeau",
        "Parma Magica",
        None,
        8,
        LATIN,
        "On harmonizing Parma Magica with the Forms.",
    ),
    (
        "Tractatus",
        "Occulta Magicis",
        "Dáire Boircech of Vigil",
        "Faerie Magic",
        None,
        7,
        LATIN,
        "On ranges, durations and targets of Faerie Magic.",
    ),
    (
        "Tractatus",
        "Nympharum Magicae",
        "Anonymous",
        "Faerie Magic",
        None,
        6,
        LATIN,
        "On the magic of the wee folk, not the Tuatha Dé.",
    ),
    (
        "Tractatus",
        "Destruet Extremum Preiudicium",
        "Calvacius of Tytalus",
        "Spell Mastery: Demon's Eternal Oblivion 15",
        None,
        8,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Magister Crystállum Pilum",
        "Cearnach of Verditius",
        "Spell Mastery: The Crystal Dart",
        None,
        8,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Multa Partum Vulnera",
        "Marcus Cordo",
        "Spell Mastery: The Wound that Weeps",
        None,
        8,
        LATIN,
        "",
    ),
    (
        "Tractatus",
        "Vita Diedne",
        "Fergus of Merinita",
        "Organization Lore: Order of Hermes",
        None,
        7,
        LATIN,
        "Written in the twenty years before the Schism War, on several "
        "important Diedne of the time.",
    ),
    (
        "Tractatus",
        "The Houses in their Turn",
        "Cearnach of Verditius",
        "Organization Lore: Order of Hermes",
        None,
        7,
        LATIN,
        "Bound in split wood, on each House's character: scorn for Bjornaer, "
        "some understanding for Diedne.",
    ),
    (
        "Tractatus",
        "Responses to the Younger House",
        "Niall of the Younger House",
        "Code of Hermes",
        None,
        6,
        LATIN,
        "How the Code was amended or read to admit House Ex Miscellanea.",
    ),
    (
        "Tractatus",
        "Arguments as to the Founding of Covenants",
        "Fergus of Merinita",
        "Code of Hermes",
        None,
        7,
        LATIN,
        "A surprisingly broad view of the early peripheral code on founding "
        "covenants and residence.",
    ),
    (
        "Tractatus",
        "Accalam na Senorach",
        "Anonymous",
        "Area Lore: Hibernia",
        None,
        8,
        IRISH,
        "History. The Tales of the Elders.",
    ),
    (
        "Tractatus",
        "Lebor Gabala Erenn",
        "Anonymous",
        "Area Lore: Hibernia",
        None,
        9,
        IRISH,
        "History. The Book of the Taking of Ireland: the five great invasions "
        "and the conquests after them.",
    ),
    (
        "Tractatus",
        "Tractatus Ethicorum",
        "Calvacius of Tytalus",
        "Philosophiae",
        None,
        8,
        LATIN,
        "His style imposes Condescending +1 in the season of study and the next.",
    ),
    (
        "Tractatus",
        "Tractatus in Rhetoricæ Orationis",
        "Calvacius of Tytalus",
        "Artes Liberales",
        None,
        8,
        LATIN,
        "His style imposes Argumentative +1 in the season of study and the next.",
    ),
    (
        "Art Summa",
        "Disputatione in Creatio",
        "Fergus of Merinita",
        "Creo",
        14,
        10,
        LATIN,
        "Ten volumes, each mostly on one Form. Hard going: a five-day distraction.",
    ),
    (
        "Tractatus",
        "Factionis Rerum",
        "Beradi of Jerbiton",
        "Creo",
        None,
        8,
        LATIN,
        "As a prop, +3 to the Intelligence + Finesse roll for spells creating "
        "artificial things.",
    ),
    (
        "Art Summa",
        "Disputations",
        "Occulus of Donum Chanuti",
        "Intellego",
        12,
        19,
        LATIN,
        "A prop for Ceremonial Intellego spells, at +3.",
    ),
    (
        "Tractatus",
        "Veritas Caeca",
        "Conchobor Crosach",
        "Intellego",
        None,
        11,
        LATIN,
        "Using Intellego for what would otherwise go unseen.",
    ),
    (
        "Art Summa",
        "Innaturale Forma Quae",
        "Anonymous",
        "Muto",
        13,
        10,
        LATIN,
        "Making unnatural changes to natural forms.",
    ),
    (
        "Tractatus",
        "Mutationes ad Figura Rerum",
        "Bohemond of Paris",
        "Muto",
        None,
        6,
        LATIN,
        "Physical change between natural forms.",
    ),
    (
        "Art Summa",
        "Remotionem Attributa",
        "Ciprian Maxim",
        "Perdo",
        14,
        9,
        LATIN,
        "Removing magical or unusual qualities.",
    ),
    (
        "Tractatus",
        "Occidere Magicis",
        "Cristescu of Tremere",
        "Perdo",
        None,
        8,
        LATIN,
        "Physical wounds by magic.",
    ),
    (
        "Art Summa",
        "In Invisibili Manu",
        "Faventinus of Verditius",
        "Rego",
        12,
        9,
        LATIN,
        "Moving and working the Forms with Rego.",
    ),
    (
        "Tractatus",
        "Adducam de Naturalis Mutata",
        "Lugh-éccnaid",
        "Rego",
        None,
        11,
        LATIN,
        "Natural changes to a Form, notably Mentem.",
    ),
    (
        "Art Summa",
        "Anathomen Lupus",
        "Ualgrimm of Bjornaer",
        "Animal",
        11,
        9,
        LATIN,
        "A detailed anatomy of the wolf, spoils of the author's death.",
    ),
    (
        "Tractatus",
        "Centum Bestiæ",
        "Ualgrimm of Bjornaer",
        "Animal",
        None,
        8,
        LATIN,
        "A bestiary of mundane and magical animals, spoils of the author's death.",
    ),
    (
        "Art Summa",
        "Aquas ex Aquilonis Maria",
        "Aecor of Bjornaer",
        "Aquam",
        14,
        10,
        LATIN,
        "Fresh seawater must be by it every week of study, or the text fades "
        "and cannot be used.",
    ),
    (
        "Tractatus",
        "Praecipitatio",
        "Marcus Pluviam of Bonisagus",
        "Aquam",
        None,
        9,
        LATIN,
        "On Auram and Aquam through what can be observed.",
    ),
    (
        "Art Summa",
        "Auras et Magna Procellis",
        "Tempestas Ventus ex Miscellanea",
        "Auram",
        14,
        10,
        LATIN,
        "A ten-day distraction: certain weather must be present or summoned.",
    ),
    (
        "Tractatus",
        "Controversias ad Aerea Phaenomenon",
        "Anonymous",
        "Auram",
        None,
        10,
        LATIN,
        "A lengthy liber quaestionum.",
    ),
    (
        "Art Summa",
        "Substantia Hominis",
        "Buffon of Jerbiton",
        "Corpus",
        11,
        13,
        LATIN,
        "A magical anatomy of the human form, richly illuminated.",
    ),
    (
        "Tractatus",
        "Vulnerant Humana Forma",
        "Anonymous",
        "Corpus",
        None,
        8,
        LATIN,
        "How magic harms or hinders the human form. The author's name has been "
        "cut out.",
    ),
    (
        "Art Summa",
        "Nota Plantarum Naturale et Non",
        "Quintinus Roboreus",
        "Herbam",
        14,
        9,
        LATIN,
        "A ten-day distraction collecting and investigating fresh plants.",
    ),
    (
        "Tractatus",
        "In Flexibus Mortuus Lignum",
        "Cassano of Verdi",
        "Herbam",
        None,
        8,
        LATIN,
        "A light work on altering dead wood.",
    ),
    (
        "Art Summa",
        "Ars Flambonis",
        "Elaine of Flambeau",
        "Ignem",
        14,
        12,
        LATIN,
        "As in Houses of Hermes: Societates p. 9.",
    ),
    (
        "Tractatus",
        "Punctis ad Quod Materias Ignire",
        "Marcus Cordo of Flambeau",
        "Ignem",
        None,
        9,
        LATIN,
        "Tables of the points at which materials catch fire.",
    ),
    (
        "Art Summa",
        "Illusiones",
        "Fergus of Merinita",
        "Imaginem",
        12,
        12,
        LATIN,
        "Hermetic equivalents to a journey through faerie glamour to a great "
        "treasure, probably apocryphal.",
    ),
    (
        "Tractatus",
        "Procul Videre et Audire",
        "Fergus of Merinita",
        "Imaginem",
        None,
        9,
        LATIN,
        "Gathering species from afar.",
    ),
    (
        "Art Summa",
        "Multa Status Cogitatio",
        "Valdés of Guernicus",
        "Mentem",
        14,
        13,
        LATIN,
        "Quality falls by five unless studied in a laboratory with a test "
        "subject on whom mental states can be cast.",
    ),
    (
        "Tractatus",
        "Somnia et Memoriis Somnia",
        "Wulthric of Criamon",
        "Mentem",
        None,
        8,
        LATIN,
        "On dreams and what is remembered of them.",
    ),
    (
        "Art Summa",
        "Index Lapides",
        "Adamo of Guernicus",
        "Terram",
        12,
        13,
        LATIN,
        "Soils, sands, stones, glass and metals through the Art.",
    ),
    (
        "Tractatus",
        "Vita de Aeramen",
        "Cearnach of Verditius",
        "Terram",
        None,
        9,
        LATIN,
        "On the qualities of bronze.",
    ),
    (
        "Art Summa",
        "Novum Interpretationem",
        "Bastian Özil of Bonisagus",
        "Vim",
        12,
        12,
        LATIN,
        "Predates the Schism War.",
    ),
    (
        "Tractatus",
        "Libro Scientia",
        "Conchobor Crosach",
        "Vim",
        None,
        11,
        LATIN,
        "Vim and the other Forms through Muto Vim effects.",
    ),
)
ARTS = {
    "Creo", "Intellego", "Muto", "Perdo", "Rego", "Animal", "Aquam", "Auram",
    "Corpus", "Herbam", "Ignem", "Imaginem", "Mentem", "Terram", "Vim",
}  # fmt: skip

BOIBEL_LOTH = (
    "Boibel Loth. Sixteen characters whose inscribed forms give Shape and "
    "Material bonuses, in rituals to the casting total, and as distinct "
    "Charms in Charm Magic (Houses of Hermes: Mystery Cults p. 96). A minor "
    "breakthrough (Houses of Hermes: True Lineages p. 26) is needed first. "
    "Boibel (B) +5 inception, +3 sun; Loth (L) +5 fire; Forann (F) +5 "
    "spring; Salia (S) +5 moon, +3 witches; Neiagadon (N) +5 water; Daibhaith "
    "(D) +5 door, +3 travel or passage; Teilmon (T) +5 growth, +3 gain; "
    "Cailep (C) +5 women; Moiria (M) +5 autumn; Gath (G) +5 balance and "
    "even-handedness; Riuben (R) +5 winter, +3 decay; Acab (A) +5 birth, +3 "
    "new life; Ose (O) +5 youth, +3 initiation; Ura (U) +5 maturity, +3 "
    "consummation; Esu (E) +5 aging and old age; Jaichim (I) +5 death."
)

#: name, kind, level, words: the Laboratory Texts.
LAB_TEXTS: tuple[tuple[str, str, int | None, str], ...] = (
    ("Lugh's Longevity Ritual", TEXT_LONGEVITY, 65, "CrCo 65, by Lugh."),
    ("Conchobor's Longevity Ritual", TEXT_LONGEVITY, 60, "CrCo 60, by Lugh."),
    ("Columb Brathair's Longevity Ritual", TEXT_LONGEVITY, 40, "CrCo 40, by Lugh."),
    ("Cathal Gobha's Longevity Ritual", TEXT_LONGEVITY, 40, "CrCo 40, by Lugh."),
    ("Piaras's Longevity Ritual", TEXT_LONGEVITY, 40, "CrCo 40, by Lugh."),
    ("Wizard's Communion", TEXT_SPELL, None, "MuVi at levels 10, 15, 20, 30 and 40."),
    (
        "Demon's Eternal Oblivion and its like",
        TEXT_SPELL,
        15,
        "PeVi 15, with the similar spells against Magic and Faerie beasts.",
    ),
    ("Circular Ward Against Demons", TEXT_SPELL, None, "ReVi 10, 20 and 25."),
    ("Opening the Intangible Tunnel", TEXT_SPELL, None, "ReVi 30 and 35."),
    ("Unseen Arm and The Unseen Porter", TEXT_SPELL, None, "ReTe, various."),
    (
        "Imaginem spells",
        TEXT_SPELL,
        None,
        "Prying Eyes, Summoning the Distant Image, Veil of Invisibility and "
        "Wizard's Sidestep.",
    ),
    (
        "Spells of disguise",
        TEXT_SPELL,
        None,
        "Notes of a Delightful Sound, Disguise of the Transformed Image and "
        "Disguise of the New Visage.",
    ),
    (
        "Creo Corpus healing",
        TEXT_SPELL,
        None,
        "Bind Wound, The Chirurgeon's Healing Touch and Incantation of the "
        "Body Made Whole.",
    ),
    (
        "Intellego Vim senses",
        TEXT_SPELL,
        None,
        "Sense of Faerie Power, Sense of Magical Power, Piercing the Faerie "
        "Veil and Piercing the Magical Veil.",
    ),
    ("Watching Ward", TEXT_SPELL, 30, "ReVi 30."),
    ("Aegis of the Hearth", TEXT_SPELL, 30, "ReVi 30."),
    ("Shroud Magic", TEXT_SPELL, 20, "MuVi 20."),
    ("Maintaining the Demanding Spell", TEXT_SPELL, 25, "ReVi 25."),
    ("Endurance of the Berserkers", TEXT_SPELL, 15, "ReCo 15."),
    (
        "Divine the Heavens' Aspect",
        TEXT_ENCHANTMENT,
        29,
        "InVi 29, for the Observance Bell.",
    ),
    ("Toll the Offices", TEXT_ENCHANTMENT, 12, "ReTe 12, for the Observance Bell."),
    (
        "Toll the Phases of the Moon",
        TEXT_ENCHANTMENT,
        8,
        "ReTe 8, for the Observance Bell.",
    ),
    (
        "Toll the Equinoxes and the Solstices",
        TEXT_ENCHANTMENT,
        8,
        "ReTe 8, for the Observance Bell.",
    ),
    (
        "Tie The Threads That Bind (Bronze Man)",
        TEXT_OTHER,
        32,
        "ReVi 32, Houses of Hermes: Mystery Cults p. 130.",
    ),
    (
        "The Bronze Man's effects",
        TEXT_ENCHANTMENT,
        None,
        "All the device effects needed to make the Bronze Man automaton, "
        "various Arts (Houses of Hermes: Mystery Cults p. 130).",
    ),
    (
        "The Bronze Bull's effects",
        TEXT_ENCHANTMENT,
        None,
        "All the effects needed to make the Bronze Bull automaton, various "
        "Arts (Houses of Hermes: Mystery Cults p. 130).",
    ),
    (
        "Tie The Threads That Bind (Bronze Bull)",
        TEXT_OTHER,
        32,
        "ReVi 32, Houses of Hermes: Mystery Cults p. 130.",
    ),
    (
        "Balance of the Honest Merchant",
        TEXT_ENCHANTMENT,
        8,
        "InTe 8, Pen +0, 6 a day, Touch, Momentary, Individual. A lesser "
        "enchantment once given to teamsters: an iron hook on a short rope; "
        "hooked into a bale or barrel and pulled, it tells the user the "
        "weight to whatever fineness he wants, grain to ton. The device is "
        "lost.",
    ),
    (
        "Honesty of the Unbalanced Merchant",
        TEXT_ENCHANTMENT,
        28,
        "ReMe 28, Pen +20, 6 a day, Touch, Momentary, Individual. A lesser "
        "enchantment in a plain ring, worked by a handshake: the target "
        "leans hard to the truth and blurts out any lie just told unless he "
        "makes an Untruthful or similar Personality roll against Ease Factor "
        "9. Penetration is for traders behind relics or Infernal protection. "
        "The device is lost.",
    ),
    (
        "Cearnach's Distant Twin: Animate this Form",
        TEXT_ENCHANTMENT,
        50,
        "ReHe 50, Pen +0, unlimited, Arcane Connection, Concentration, "
        "Individual. Moves the man-sized articulated figure of wood and "
        "bronze; a Finesse roll under stress. Its Str, Sta, Dex and Qik are "
        "0 and replace the user's. Part of a greater enchantment, enchanted "
        "into a small copy carved from the same wood, which burned soon "
        "after it was finished; said to be made so that Cearnach, who had "
        "the Blatant Gift, could meet people in person.",
    ),
    (
        "Cearnach's Distant Twin: His Sight Is Mine",
        TEXT_ENCHANTMENT,
        60,
        "InIm 60, Pen +0, unlimited, Arcane Connection, Concentration, "
        "Special. All the senses work through the figure.",
    ),
    (
        "Cearnach's Distant Twin: Clothe this Form",
        TEXT_ENCHANTMENT,
        45,
        "MuIm 45, Pen +0, unlimited, Arcane Connection, Concentration, "
        "Individual. The figure gives off the user's species; a Finesse roll "
        "at +3 for its maker. A side effect mirrors the image, a scar on the "
        "left hand showing on the right, though not its movements. The texts "
        "mention a fourth, experimental effect to cast through the figure, "
        "if it was ever finished; no text of it survives.",
    ),
)

#: name, art, pawns, season, kind, level, Build Points, words.
SOURCES: tuple[tuple[str, str, int, str, str, int | None, str], ...] = (
    (
        "Tribute from the Underworld",
        "Corpus",
        4,
        "",
        "",
        None,
        "One pawn a season. Under its pact with Longmist the Tuatha Dé lead "
        "the covenant to a human body each season, to be dug from its grave, "
        "holding a pawn; it lasts while relations are good. 20 Build Points.",
    ),
    (
        "From the Very Walls Themselves",
        "Vim",
        4,
        "",
        "",
        None,
        "One pawn a season, accreting in roof tiles, cobbles and walls of the "
        "lesser tower, which are pockmarked by stones taken away and patched "
        "in haste. A Dwindling Resource: three pawns after three years, two "
        "after five, one after eight, none after ten. 20 Build Points.",
    ),
    (
        "The Swine in the Woods",
        "Herbam",
        4,
        "Autumn",
        "",
        None,
        "Mushrooms and other fungi in woodland near Longmist. Pigs brought for "
        "the purpose sniff them out, and a trained swineherd takes the "
        "morsels before they are eaten. 20 Build Points.",
    ),
    (
        "Gold Teeth from the Pike Pulled",
        "Terram",
        3,
        "Spring",
        "",
        None,
        "A fearsome pike comes to the same water each spring to take a wife; "
        "a quick, brave fisherman can wrestle it ashore barehanded and pull "
        "three gold teeth, a pawn in each. It was once a feast and a contest, "
        "and is now a dangerous chore. 15 Build Points.",
    ),
    (
        "The Leeward Side",
        "Vim",
        8,
        "",
        "",
        None,
        "Two pawns a season: lichen on the side of certain trees away from "
        "the sun, in woods not far off. 40 Build Points.",
    ),
    (
        "The Gifted Blacksmith",
        "Ignem",
        2,
        "",
        "spell_like",
        14,
        "Some seasons a piece of very pure iron in Cathal Gobha's forge gives "
        "off its own heat: glassy black shards too hot to hold, kept in "
        "water, in oil or in the ground. Shard of Iron, CrIg 14, Pen +0, "
        "constant, Personal, Sun, Individual, as Heat of the Searing Forge. "
        "The text says Creo and the summary table spell-like Ignem. 12 "
        "Build Points.",
    ),
    (
        "The Needfire",
        "Creo",
        6,
        "Spring",
        "",
        None,
        "A ritual of the Lebor Feasa Runda: on Beltane night, on land outside "
        "the Aegis, a fire of willow, hazel, alder, birch, rowan, yew, elm, "
        "oak and ash. A living being passed three times through its smoke has "
        "an effect like Cheating the Reaper, Pen +10. Pre-Hermetic: once "
        "known it can be lit each year, only in a Magical aura, and the "
        "Aegis suppresses it. Unused, the charred staves hold the vis. Some "
        "see visions in the smoke, so it may do more. The summary table says "
        "Corpus, the text Creo. 30 Build Points.",
    ),
    (
        "The Black Root",
        "Perdo",
        1,
        "Autumn",
        "",
        None,
        "Each autumn one of Úna's plants, onion or parsley or any other, grows "
        "a black root that poisons those around it if left. Lifted, it loses "
        "its power and keeps a pawn. Rarely another appears, in autumn or "
        "otherwise. A persistent presence means her herbs harm. 5 Build "
        "Points.",
    ),
    (
        "The Floating Stones of Maghera",
        "Rego",
        1,
        "",
        "lesser_enchantment",
        14,
        "Each year a grove five miles north of the Maghera Falls gives a "
        "stone little bigger than a fist, held by a long stony root. Broken "
        "free, it takes men of combined Strength +5 to move and stays where "
        "put, unsupported, holding things aloft (ReTe 14, Pen +0, constant, "
        "Personal, Sun, Individual, like The Unseen Porter). Many float "
        "lecterns, tables and lanterns about the covenant. Outside lands the "
        "Tribunal recognises, so unprotected by the peripheral code. 6 Build "
        "Points.",
    ),
    (
        "The Hunt",
        "",
        6,
        "",
        "",
        None,
        "Six pawns of various Arts, Animal and Herbam most often, in the low "
        "Magical auras of the hills and valleys of western Ulaid; a magus "
        "spends a ten-day distraction across the year finding them. Rarely "
        "done now. Outside lands the Tribunal recognises, so unprotected by "
        "the peripheral code. 30 Build Points.",
    ),
)

RAW_VIS = {
    "Auram": 5,
    "Corpus": 15,
    "Creo": 10,
    "Herbam": 5,
    "Imaginem": 5,
    "Intellego": 10,
    "Muto": 10,
    "Perdo": 10,
    "Rego": 10,
    "Mentem": 5,
    "Terram": 5,
    "Vim": 15,
}

CHARTER = (
    "A council may be called at any time. It is quorate only if every "
    "magus in residence attends, on pain of censure; a proxy may be appointed, "
    "or a magus excused, as for Twilight. Only a quorate session binds.",
    "Each magus has one vote at council on each matter brought before it.",
    "For its help through the covenant's life, the Tuatha Dé hold a seat and "
    "vote at council, which do not count toward the quorum.",
    "Offices: Princeps (held by Tadhg an Tuir, now vacant); Castellanus, "
    "mundane and magical security within the Aegis (vacant); Cancellarius, "
    "the covenant's financial and magical well-being, including accounting "
    "for vis and its use on Longevity Rituals (long vacant); Praefectus, "
    "security of lands and property beyond the Aegis, including the cathach "
    "(Conchobor); Aedilis, planning magical works (long vacant); Censor, "
    "leading rituals and upholding the magi's moral standards (Mícheál); "
    "Propraetor, relations with outside covenants, nobles and the Church "
    "(Lugh).",
    "A magus in an office has one more vote on matters of its responsibility.",
    "An office is filled by a quorate council. Candidates may not vote, and "
    "the matter counts as within every office's responsibility, so holders "
    "cast a second vote.",
    "A magus who has trained an apprentice is treated as an elder, with more "
    "respect, though age gives no power at council.",
    "Every magus has a sanctum; the elder magi must be added to a younger "
    "magus's sanctum marker, and refusal invites censure.",
    "All use one code and script for their Lab Texts.",
    "Voting sigils are made by the covenant's blacksmith, so are always "
    "metal, the apprentice having some say over which.",
    "Magi dress respectfully: a simple belted woolen robe, the hood down at "
    "study and meals and up otherwise. Charms, rings and amulets fit for a "
    "magus are allowed; ornament is not, nor arms and armor unless a "
    "talisman. Hair is short and shaved at the back and sides; women are "
    "exempt but keep theirs covered in public.",
    "No music or singing in the tower; that is for grogs and servants.",
    "All magi in residence eat together at the bell, in silence but for a "
    "reading, in strict rotation among all ranks, on magic, the Order or the "
    "realms. Refusal may be punished. No food between meals.",
    "Magi attend to their Parma Magica at the bell at dawn and dusk.",
    "Study and laboratory work keep to strict hours; a non-standard routine "
    "(Covenants p. 107) or any experimentation needs the council's leave.",
    "Falling short brings private admonishing, the withholding of a meal, "
    "exclusion from a gathering, suspension of all communication, or ten "
    "days of duty. Records show public certamen with a senior magus in the "
    "past, seemingly with vis appointed him; no wayward magus is recorded as "
    "winning, and either outcome seems to have bound.",
    "Twenty-eight iron medallions engraved with a wolf's head are worked into "
    "the Aegis each year, besides any the magi present. A visitor has one "
    "from dawn's Parma to dusk's, and none by night. If visitors outnumber "
    "them they go in order: a magus of the Order, a familiar of the Order, a "
    "beast of Ireland, a mundane lord, a hedge wizard or druid, an "
    "apprentice, a mortal man of Ireland, a foreigner.",
)

OFFICES = (
    "The Offices, for all magi of any rank, rung on the bell by covenfolk "
    "since its magic failed: 02:00 rise; 02:15 a reading from the Vitae "
    "Magnae, then a nap; 05:00 breakfast with a reading, tokens given back "
    "to visitors; dawn, the Parma Magica; 07:00 study, laboratory work or "
    "the covenant's business; 15:00 dinner with a reading; dusk, the Parma "
    "Magica, tokens collected; 19:00 supper with a reading; 20:00 "
    "retirement. The times with dawn and dusk shift, and meals are also given "
    "as midmorning, two hours before dusk and three after."
)


def _arts(printed: str) -> tuple[str, str]:
    """The Technique and Form of "ReCo"."""
    return ART_LOOKUP[printed[:2].lower()], ART_LOOKUP[printed[2:4].lower()]


def _effect(
    name: str,
    arts: str,
    printed: int,
    own: int,
    rdt: tuple[str, str, str],
    uses: str,
    words: str,
    *,
    penetration: int = 0,
    requisites: str = "",
    concentration: bool = False,
    constant: bool = False,
) -> InstilledEffect:
    """An instilled effect as the book prints it: `printed` its finished
    level and `own` the level before the item's modifications."""
    technique, form = _arts(arts)
    reach, duration, target = rdt
    return InstilledEffect(
        id="",
        name=name,
        technique=technique,
        form=form,
        requisites=requisites,
        range=reach,
        duration=duration,
        target=target,
        level=own,
        description=words,
        uses_per_day=uses,
        penetration=penetration,
        maintains_concentration=concentration,
        environmental_trigger=constant,
        trigger="sunrise and sunset" if constant else "",
        modified_level_override=printed,
    )


def _talisman(
    b: Builder,
    covenant: Covenant,
    magus: Character,
    name: str,
    words: str,
    opened: int,
    effects: list[InstilledEffect],
) -> None:
    device = b.device(covenant, name, description=words, effects=effects)
    device.talisman = True
    device.holder_kind, device.holder_id = "character", magus.id
    device.maker_id = magus.id
    device.pawns_opened = opened


def _held(
    b: Builder,
    covenant: Covenant,
    magus: Character,
    name: str,
    words: str,
    effects: list[InstilledEffect],
) -> None:
    device = b.device(covenant, name, description=words, effects=effects)
    device.holder_kind, device.holder_id = "character", magus.id
    device.maker_id = magus.id


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    site = _places(hibernia)
    covenant = _covenant(hibernia, site)
    hibernia.covenants["longmist"] = covenant
    hibernia.cathaigh["longmist"] = {
        "cathach": "The pelt of Ualgrimm, a Bjornaer wolf",
    }
    people = _people(hibernia, covenant)
    labs = _laboratories(b, covenant, people)
    _charter(covenant)
    _history(b, covenant)
    _talismans(b, covenant, people)
    _devices(b, covenant)
    _broken_things(covenant)
    _library(b, covenant)
    _vis(covenant, labs)
    _holdings(covenant)
    _ruadan(hibernia, covenant, site)
    _bronze_man(hibernia, covenant, site)
    _clan(hibernia, covenant)


def stats(hibernia: Hibernia) -> None:
    b = hibernia.b
    for key, _name, _kind, _age, block, *_ in (*MAGI, *PEOPLE):
        b.stats(hibernia.magi[key], block, source=SOURCE)
    _spell_words(hibernia)


def _overwrites(hibernia: Hibernia) -> None:
    """Where this book differs from the Tribunal book it wins, with it on:
    Cú Chonnacht leads Clan Mac Tire, and Tir na nÓg is an island ruled by
    the Fomórach, with Mag Mell and Tobar Segais on it."""
    saga = hibernia.b.saga
    for character in saga.characters:
        if character.name.startswith("Cú Chonnacht"):
            character.secrets = as_secrets(
                secret_words(character.secrets).replace(
                    "The book says nothing more of him. ", ""
                )
            )
    for neighbour in saga.neighbours:
        if neighbour.name == "Tír na nÓg, the Otherworld":
            neighbour.summary = paragraphs(
                "An island ruled by the Fomórach, with the plain of Mag Mell "
                "and the well of Tobar Segais upon it.",
                neighbour.summary,
            )


def finish(hibernia: Hibernia) -> None:
    """Tie Longmist to the parts built after it."""
    b, w, m = hibernia.b, hibernia.world, hibernia.magi
    covenant = hibernia.covenants["longmist"]
    _overwrites(hibernia)
    for key, note in (
        ("tuatha_de", "Old allies, with a seat and vote at its council"),
        ("fir_bolg", "Longmist's name carries weight with them"),
        ("druids", "Respected it of old, and traded it Gifted children"),
    ):
        if key in w:
            b.link(w[key], "covenants", covenant, note)
    if "ordo_hiberniae" in w:
        b.link(
            w["ordo_hiberniae"],
            "characters",
            m["lugh"],
            "Argues for its independence",
        )
    if "baile_ui_eodhasa" in w:
        b.link(w["baile_ui_eodhasa"], "characters", m["eamonn"], "Of its line")
    if "peter" in m:
        b.link(
            m["cailleach"],
            "characters",
            m["peter"],
            "She assisted an itinerant Verditius of this name",
        )
    leth_cuinn = hibernia.covenants.get("leth_cuinn")
    if leth_cuinn is not None:
        b.link(m["bran"], "covenants", leth_cuinn, "Learned his Cles from Úathach")


def _places(hibernia: Hibernia) -> Neighbour:
    b, p = hibernia.b, hibernia.places
    valley = b.place(
        "The Valley of the Long Mists",
        inside=p.get("tir_chonaill") or p.get("ulster"),
        aura=2,
        summary=paragraphs(
            "A valley between Lough Beagh and the smaller Lough Inshagh in "
            "Donegal, nearly always under a low unnatural mist. Its "
            "weather-beaten hills bear few trees, with some woodland along "
            "the lakes; winters are mild and wet and summers warm, with "
            "midges. Sheep, goats and hardy cattle graze behind robust "
            "drystone walls. A market lies a long day's round trip away.",
            "Rules. Magic aura 2. Devices and spells once cleared or steered "
            "the mist for visitors; they are lost or broken, and the magi "
            "have no wish to replace them. Giants come down when weather is "
            "harsh or food short (Realms of Power: Faerie p. 98 for faerie "
            "giants, Realms of Power: Magic p. 86, Barcas, for magical "
            "ones), blundering through the village after sheep and now and "
            "then cattle; food or a shiny bauble moves them on. Ruadan "
            "speaks for the covenant to faerie giants, but not to magical "
            "beasts.",
        ),
    )
    p["longmist_valley"] = valley
    site = b.place(
        "Longmist",
        inside=valley,
        aura=5,
        detail=FULL,
        summary=paragraphs(
            "Two intersecting oval courtyards round a small white tower, the "
            "walls' plaster cracked, dirty and flaking. The larger court's "
            "two iron lattice gates are rusted shut and two bronze warrior "
            "women, once their keepers, have seized with them, each bigger "
            "than a man, plaited and circleted, in a coat of plates with a "
            "small sparra at her belt, hauling on chains. The paved yard has "
            "buckled over roots, its fountain is dry, and broken carts, "
            "barrels, crates and sacks sit under sheds along the walls. "
            "Beside the fountain a bronze man larger than life, dressed as a "
            "smith and said to stand for the Fir Bolg in their glory, gazes "
            "toward the gates, some say wistfully; follow his gaze and he is "
            "looking at one of the warrior women.",
            "The smaller rear courtyard, behind humble wooden gates, is the "
            "way in now, with its troughs and chicken runs, the stables, and "
            "the workshops of Piaras and Cathal. The courts have room to "
            "build. The village lies to the south, on the way to the rear, "
            "homes of the same white stone, where the covenfolk and Columb's "
            "chapel are. Twelve servants live there, eight women who do the "
            "tower's chores and kitchens and four men who labor under the "
            "specialists, with four laborers and four teamsters.",
            "The lesser tower has four levels and a cellar, with a front door "
            "on the second level up steps from the great court, a rear door "
            "through the kitchens, and a wooden belfry on top. Once its "
            "laboratories housed the first magi; now it is workspace and "
            "grogs' guardhouse. The cathach hangs outside the Aegis on a "
            "great X-shaped frame staked and roped against the valley winds, "
            "inside a circular ward, under guard of Ruadan's warriors.",
            "Rules. Magic aura 5; the lesser tower is what the mortal world "
            "sees. An enchanted door leads to the greater tower. The Hibernia "
            "Code's cathach must be kept outside the Aegis.",
        ),
        levels=[
            b.level(
                "The greater tower",
                6,
                see="Thirteen stories rising and sinking into cellars, almost "
                "always unseen and unheard from below. Every level seems to "
                "stand above the mists, with glimpses and sounds of the "
                "mundane covenant below.",
                enter="The enchanted door in the lesser tower, by touch, "
                "without Second Sight or Warping.",
                notes="Lugh at the top in the sky, Conchobor at the bottom in "
                "the dark, the other magi a level each, several levels empty; "
                "a large hall, the library in two levels above it joined by "
                "a spiral stair, its shelves spoking out like a cartwheel. A "
                "round casting chamber of polished white stone inscribed with "
                "circles, with mirrors and hanging braziers, gives +5 to "
                "casting totals, and ceremonial magic there takes one minute "
                "a magnitude (Houses of Hermes: Societates pp. 58-60). The "
                "regio fell to 6 nearly thirty years ago, some say for ties "
                "to the Tuatha Dé, others for the Cailleach's arrival, others "
                "for unsanctioned experiments. Raised by ritual in Longmist's "
                "long summer by a long-dead Verditius.",
            )
        ],
    )
    p["longmist"] = site
    p["longmist_chapel"] = b.place(
        "Columb's Chapel",
        inside=site,
        realm="Divine",
        aura=4,
        summary=(
            "A small chapel in the village, built and provisioned in earlier "
            "times, Divine aura 4, where Columb Brathair is priest. It keeps a "
            "Bible, the parish register and the clapper of Saint Patrick's "
            "bell."
        ),
    )
    hibernia.world["inniskil"] = b.town(
        "Inniskil",
        place=p.get("ulster"),
        summary=(
            "The nearest market, where Longmist's teamsters sell fish and buy "
            "food and supplies. Some merchants know what the covenant is; "
            "most take it for a monastery or hermitage."
        ),
    )
    return site


def _covenant(hibernia: Hibernia, site: Neighbour) -> Covenant:
    b, tribunal = hibernia.b, hibernia.tribunal
    assert tribunal is not None
    covenant = b.covenant(
        NAME,
        tribunal=tribunal,
        founded=927,
        season="Winter",
        detail=FULL,
        place=site,
        level=1,
        aura=6,
        summary=paragraphs(
            "A mist-bound valley in the north of Ulaid, home to faeries of "
            "the dark underground, to giants, and to a shut-in covenant whose "
            "symbol is a wolf pelt. Two elders hold it between them, one at "
            "the top of the tower in the light and air and the other among "
            "the cellars and cisterns, and four younger magi live by their "
            "rule. No generation stands between them, lost to Twilight or "
            "death, and the seat of princeps stands empty. The younger magi "
            "might yet steer it between its extremes, or go the way of two "
            "generations of feuding.",
            "History. Founded in 927, on land disputed by druids and a "
            "Bjornaer wolf with his followers. Unable to beat either alone, "
            "the first magi turned to the Tuatha Dé on a bargain of which no "
            "record exists, overcame the druids, and held off the Bjornaer "
            "for the year it took to found the covenant, with the shield of "
            "Cú Chulainn as cathach. For seventy years they entertained magi, "
            "faeries and nobles and grew rich. In the Schism War they "
            "withdrew to their new inner tower, and the Bjornaer raided "
            "them, killing a magus and three apprentices and taking the "
            "shield. The Tuatha Dé armed their allies, and in the swift "
            "reprisal Ualgrimm the Bjornaer elder died and the shield "
            "shattered. At their urging his pelt was taken in its place. Then "
            "trade and letters dwindled, until the gates opened only to "
            "covenfolk and the odd Redcap, though druids long brought Gifted "
            "children here first to trade. In the last century foreign "
            "invaders came, and Longmist's call to hound them out was ignored, "
            "which it resents still.",
            "Income. The fishery and toll bridge, a Lesser Income Source, earn "
            "80 Mythic Pounds a year against 84.5 spent: buildings 8, "
            "consumables 13 (16 less 3), laboratories 44.5, wages 16, weapons "
            "and armor 0 (1 less 1), writing materials 3 (7 less 4), tithes "
            "0. Weapons and armor cover the turb and six sets in store. "
            "Wealth makes up the shortfall, as it has for years, and anyone "
            "looking closely can see it. Lugh's laboratory is the great "
            "drain. New income, cuts agreed by Lugh, or craftsmen such as "
            "glass-blowers, silversmiths, masons and a master brewer would "
            "help, at the price of isolation (Covenants ch. 5).",
            "Wealth. 300 Mythic Pounds, little of it money: tapestries, fine "
            "linen, silk, velvet and fur bedding, window glass, silver plate "
            "and cutlery from the days of princely guests, all stored away as "
            "a distraction. Living Standards +1, as for a Winter covenant; a "
            "magus who spends a season putting these things to use makes it "
            "+2.",
            "Loyalty. Prevailing Loyalty 0: base -42.5 from the magi's Gifts, "
            "offset by the covenant's age; the Turb Captain +5; Living "
            "Conditions 0; austerity -1. The total, 4, does not buy a Score "
            "of 1. A steward and chamberlain, both unfilled, would help. The "
            "covenfolk are few, aging without issue, Warping, and split in "
            "loyalty; little is done without a magus's word.",
            "Religion and rule. The magi live an almost ascetic life of set "
            "hours, reading the Vitae Magnae, a Hibernian kind of book telling "
            "a subject through lives of famous magi, mostly on Area Lore: "
            "Hibernia, Code of Hermes or Organization Lore: Order of Hermes. "
            "Before the Parma each recites standing, eyes closed and head "
            "bowed, touching two fingers of each hand to brow, eyes, ears, "
            "nose and lips while naming notable magi of the past, 30 seconds "
            "with no effect. Those who had their Gift opened here share a "
            "light mist in their sigils.",
        ),
        what_matters=joined_lines(
            "Build Points: 2165 (devices and laboratories 502, library and "
            "Lab Texts 1089, wealth 30, specialists 286, vis 278); its vis is "
            "mostly stored, not yearly",
            "Boon: Aura (Major) (6 within the regio of the greater tower, by "
            "the enchanted door)",
            "Boon: Magical Fortress (the greater tower, raised within the "
            "regio by ritual)",
            "Boon: Mystical Allies (the Fir Bolg, airy spirits of land and "
            "sky, the druids of Connacht)",
            "Boon: Aura (Minor) (the covenant's general aura of 5)",
            "Boon: Aura (Minor) (the covenant's general aura of 5)",
            "Boon: Seclusion (Ulaid learned long ago to leave the druids of "
            "the long mists alone)",
            "Boon: Small Tower (free choice: walls that stop no determined foe)",
            "Hook: Divided Loyalty (covenfolk back one elder or the other, "
            "and younger magi are judged the same way)",
            "Hook: Fractured Council (princeps vacant, both elders want it)",
            "Hook: Contested Resource (the cathach, Ualgrimm's pelt, displayed "
            "outside the Aegis, an insult never forgiven)",
            "Hook: Crumbling (flaking plaster and mortar, rusted gates, warped "
            "doors and shutters)",
            "Hook: Deathbed Visitor (the banshee, Realms of Power: Faerie p. "
            "80: her cry over a covenfolk's coming death, which capturing her "
            "may prevent; locals brave the mists to ask the magi's help)",
            "Hook: Dwindling Resource (From the Very Walls Themselves, -10% "
            "a year from the start of play)",
            "Hook: Faerie Court (Tuatha Dé kings and princes watch Conchobor "
            "and his side, serve him, guard the cathach, and ask service back)",
            "Hook: Superiors (Minor) (the younger magi must ask the council "
            "for resources, and an inquorate council or an elder's veto "
            "withholds them)",
            "Allies: the Tuatha Dé, under Ruadan; elemental spirits of Ireland, "
            "well inclined to Lugh and Dara, though some of fire fear and "
            "resent the magi",
            "Rivals: Clan Mac Tire, the only political enemy; the mundane "
            "neighbours who eye the toll bridge",
            "Faded ties: Connacht's druids and the hedge wizards, with no "
            "contacts left; many think it a pity Lugh's and Dara's art was "
            "turned to the Order",
            "Each midsummer's eve a train of faerie merchants comes for three "
            "days and nights, sent by Ruadan, with oxen that talk and no "
            "iron, selling laboratory tools and glasswork for no strange "
            "price; the goods seem wholly mundane and harm no lab work",
            "Option: Hidden Resources, balanced by Contested Resource, adds "
            "250 Build Points of scattered things to win back; none exists "
            "otherwise",
        ),
        notes=paragraphs(
            "Past magi. Niall of the Younger House (927-1011), founder, who "
            "made peace with the druids. Fergus of Merinita (927-1014), "
            "founder, who forged the alliance with the Tuatha Dé. Hannewalt on "
            "Bar (937-1049), first Tytalus here, from England, with magic for "
            "perceiving and crossing boundaries. Marcus Cordo of Flambeau "
            "(967-1002), the only Flambeau, killed with his apprentice in the "
            "raid. Cearnach of Verditius (978-1064), faerie-blooded smith who "
            "wielded the blade that took the pelt, and retired to Verdi once "
            "he had trained an apprentice. Astwick of Bonisagus (1027-1070), "
            "forced out under suspicion of sharing secrets, who took his works "
            "to Durenmar; his lineage is gone. Faventinus of Verditius "
            "(1087-1164), who made the Bronze Man, and fell into Final "
            "Twilight. Calvacius of Tytalus (1125-1218), Mícheál's parens, who "
            "vanished; Conchobor showed it was Final Twilight. Tadhg an Tuir "
            "of Verditius (1128-1218), the Cailleach's parens, who died in an "
            "aging crisis no magic could lift and lies at Qui Sonant Pro "
            "Quieto.",
            OFFICES,
            "Story seeds. The Dwindling Fish: few and small fish in the "
            "withies. Is it overfishing, or new magi upstream looking for a "
            "site? What of the vis? A Service for a Service: Ruadan's people "
            "demand a deed, from facing a danger underground to bringing the "
            "tears of a mother bereft; refuse, and the bargain guarding the "
            "cathach is broken. The Missing Cathach: a Lab Text in the library "
            "describes the cathach exactly, as if the true one were replaced "
            "by an enchantment, and without it the covenant's resources have "
            "no protection. The Cattle Raid: Éamonn saw a mechanical bull in a "
            "Leinster covenant's herd; do the magi go to Tribunal, or raid? "
            "The bronze man looks at one warrior woman: can the Cailleach "
            "free him and let the story play out?",
            "Storylines. The Death of the Elders: one will go first, and the "
            "survivor's side may turn on the other's. Covenant Governance: "
            "win the vacant offices and their votes (Eochaid, Mícheál; Fractured "
            "Council, Divided Loyalty). Rebuilding the Covenant: masonry, "
            "finances, new craftsmen against the elders' word (Crumbling, "
            "Dwindling Resource). Clan Mac Tire: it accepts nothing less than "
            "the pelt, so peace needs a new trophy, or there is escalating "
            "conflict; Mícheál at the center (Contested Resource). Alliance "
            "with the Tuatha Dé: can the magi learn Ruadan's aims and get "
            "free, perhaps as he offers an apprentice of his blood or steers "
            "research to lift the curse that keeps his people from sunlight? "
            "Eochaid and Dara (Faerie Court). Rejoining Hermetic Society: "
            "trade, with naivety to exploit; the Cailleach must find a "
            "Verditius master, and Conchobor, under Ruadan's sway, opposes "
            "(Seclusion, Superiors). Expelling Foreign Magi: a beacon for "
            "like-minded magi, driven by Lugh if he publishes; Dara and "
            "Mícheál may feel threatened, Eochaid and the Cailleach see "
            "chances (Fractured Council, Seclusion).",
            "As a background covenant: others may investigate its silence; "
            "Clan Mac Tire may seek allies against it, or Longmist hire help "
            "to hunt the Clan across Ulaid and into Connacht; its six votes "
            "can be won; Lugh's books may divide the Tribunal; he may secretly "
            "trade covenant wealth through Redcaps for new Magic Theory texts. "
            "Moved elsewhere, its split could be the Rhine's Harmonists and "
            "Wilderists, its isolation the Alps or the Holy Land, and the pelt "
            "still an insult.",
            "Themes: isolation, tradition and conflict. The elders suit the "
            "storyguide, assigning tasks and keeping the younger magi in line; "
            "the four younger magi suit players. Own magi could fill the same "
            "roles: a Verditius to rebuild, a tie to Connacht, a Merinita link "
            "to the valley's faeries, and a keeper of tradition and future "
            "leader.",
        ),
        secrets=paragraphs(
            "Tribute from the Underworld is a sham, unknown to Longmist: the "
            "bodies make no vis, it is put there by the Tuatha Dé's magic, "
            "perhaps to make the magi party to something unseemly and bind "
            "them closer.",
            "Ruadan works against any magus whose doing would take him from "
            "the valley or bring others to it; his reasons are unknown.",
            "A tale keen-eyed apprentices may find says the music ban came "
            "after a faerie princess entranced the whole covenant by her voice.",
            "Visitors from Normandy are said to have stolen tokens and books "
            "many years ago.",
        ),
    )
    covenant.boons_hooks = boons_hooks_from(covenant.what_matters)
    return covenant


def _people(hibernia: Hibernia, covenant: Covenant) -> dict[str, Character]:
    b = hibernia.b
    found = {}
    for key, name, house, age, _block, summary, hidden in MAGI:
        found[key] = hibernia.magi[key] = b.magus(
            name,
            covenant=covenant,
            house=house,
            age=age,
            summary=summary,
            secrets=hidden,
        )
    for key, name, kind, age, _block, summary, hidden in PEOPLE:
        found[key] = hibernia.magi[key] = b.magus(
            name,
            covenant=covenant,
            house="",
            age=age,
            summary=summary,
            type=kind,
            secrets=hidden,
        )
    for key, name, age, summary in FOLK:
        found[key] = hibernia.magi[key] = b.magus(
            name,
            covenant=covenant,
            house="",
            age=age,
            summary=summary,
            type="companion",
            secrets=FOLK_SECRETS.get(key, ""),
        )
    return found


def _laboratories(
    b: Builder, covenant: Covenant, people: dict[str, Character]
) -> dict[str, str]:
    """The six magi's laboratories and the three empty ones, 360 Build
    Points with 44.5 Mythic Pounds of upkeep a year; each magus's lab id."""
    found = {}
    for key, values, specializations, page, words in LABS:
        magus = people[key]
        lab = b.laboratory(
            covenant,
            f"{magus.name}'s laboratory",
            owner=magus,
            characteristics=dict(values),
            specializations=specializations,
            source=f"{BOOK} p. {page}",
            rooms={"The greater tower": words},
        )
        found[key] = lab.id
    for number in range(1, 4):
        b.laboratory(
            covenant,
            f"Empty laboratory {number}",
            characteristics=dict(EMPTY_LAB),
            specializations={"Perdo": 2},
            source=f"{BOOK} p. 117",
            rooms={
                "The greater tower": "Once a former member's; the valuable "
                "equipment has been reused and what remains is decaying. "
                "Upkeep half a Mythic Pound a year. Size +0 (-1). Flaws: "
                "Missing Equipment, Decaying, Missing Sanctum Marker. "
                "Impossible: Enchanting Items. The three cost 150 Build "
                "Points."
            },
        )
    return found


def _charter(covenant: Covenant) -> None:
    charter = covenant.charter_of_covenant
    charter.name = "The Rule of Longmist"
    charter.preamble = (
        "Council and offices as the charter gives them, with the rule of "
        "conduct the magi keep as tradition. A magus can stall the council "
        "by not leaving his laboratory, since all must attend for a quorum "
        "and only a quorate council can censure him."
    )
    charter.clauses = [
        CharterClause(number=str(number), text=text)
        for number, text in enumerate(CHARTER, 1)
    ]


def _history(b: Builder, covenant: Covenant) -> None:
    b.chronicle(covenant, 927, "Longmist founded", "With the shield of Cú Chulainn.")
    b.chronicle(
        covenant,
        1002,
        "The Bjornaer raid",
        "Marcus Cordo and his apprentice die, and the shield is taken.",
    )
    b.chronicle(
        covenant,
        1218,
        "Tadhg an Tuir dies; Calvacius disappears",
        "Tadhg's aging crisis took him though Lugh gave him the Balm of Tír nan "
        "Óg, and Calvacius passed into Final Twilight.",
    )


def _talismans(b: Builder, covenant: Covenant, people: dict[str, Character]) -> None:
    _talisman(
        b,
        covenant,
        people["lugh"],
        "The Staff of Lugh",
        "A slender rowan staff with a lustrous patina of nearly a century's "
        "use, an agate at its head bound with leather and resin. Opened to "
        "20 pawns, 15 spent. Attunements: agate +3 air, +5 protection from "
        "storms; staff +2 repel things, +4 control things at a distance, +4 "
        "destroy things at a distance.",
        20,
        [
            _effect(
                "Perfect Circle",
                "ReHe",
                13,
                3,
                ("Personal", "Momentary", "Individual"),
                "Unlimited",
                "Draws a perfect standard circle unguided; a magus must still "
                "trace a Ring or Circle spell's by hand.",
            ),
            _effect(
                "Lifting the Dangling Puppet",
                "ReCo",
                40,
                15,
                ("Voice", "Concentration", "Individual"),
                "Unlimited",
                "As the spell.",
                penetration=20,
                concentration=True,
            ),
            _effect(
                "Invocation of Weariness",
                "PeCo",
                40,
                20,
                ("Voice", "Momentary", "Individual"),
                "Unlimited",
                "As the spell.",
                penetration=20,
            ),
            _effect(
                "Whispers Through the Black Gate",
                "InCo",
                25,
                15,
                ("Touch", "Concentration", "Individual"),
                "Unlimited",
                "As the spell.",
                requisites="Mentem",
            ),
            _effect(
                "The Youthful Visage",
                "MuIm",
                14,
                5,
                ("Personal", "Sun", "Individual"),
                "12",
                "Gives him the look of a man in his early thirties. He "
                "suspends it when alone, mindful of Warping.",
                concentration=True,
            ),
        ],
    )
    _talisman(
        b,
        covenant,
        people["conchobor"],
        "The Arm of Conchobor",
        "A bronze glove by a smith of the Tuatha Dé, smelted over exotic "
        "citrus woods and supple as calf-leather, each rivet replaced with "
        "iron by Faventinus of Verditius. When Conchobor turned its first "
        "power on the Tuatha Dé, they made it grow and fuse with his flesh "
        "from shoulder to fingertip. Opened with 20 pawns, 13 used. "
        "Attunements: iron +7 harm or repel faeries; glove +4 affect things "
        "by touch, +4 manipulation at a distance; bronze +5 darkness.",
        20,
        [
            _effect(
                "The Guiding Hand",
                "PeCo",
                30,
                15,
                ("Voice", "Concentration", "Individual"),
                "12",
                "Pains people, and creatures Corpus affects, such as faeries "
                "in human form.",
                penetration=22,
            ),
            _effect(
                "Bring the Light",
                "CrIg",
                19,
                10,
                ("Touch", "Concentration", "Individual"),
                "12",
                "As Lamp without Flame: white light about ten paces across.",
                concentration=True,
            ),
            _effect(
                "Banish the Light",
                "PeIg",
                25,
                20,
                ("Touch", "Concentration", "Structure"),
                "1",
                "As Well Without Light; Creo Ignem above level 20 overcomes it.",
                concentration=True,
            ),
            _effect(
                "This Room is Mine to Command",
                "ReTe",
                30,
                15,
                ("Touch", "Concentration", "Room"),
                "Unlimited",
                "Moves things in the room as if with Strength +5; fine work "
                "needs a Finesse stress roll against 12 or more.",
                concentration=True,
            ),
        ],
    )
    _talisman(
        b,
        covenant,
        people["cailleach"],
        "Wand of the Cailleach",
        "A slender wand of gleaming steel twisted like rope round a core of "
        "colored glass, which shows through and glows when power passes. The "
        "steel was once a magical lamp made by a forebear. Capacity 10, all "
        "used. Attunements: wand +2 repel things, +3 project bolt or other "
        "missile, +4 control things at a distance, +4 destroy things at a "
        "distance; lamp +7 produce light, +4 create fire. Light: white for "
        "Dominion, red Infernal, blue Magic, green Faerie, brighter with "
        "stronger auras.",
        10,
        [
            *[
                _effect(
                    f"Sense the Scale of {realm} Power",
                    "InVi",
                    9,
                    5,
                    ("Personal", "Sun", "Touch"),
                    "2",
                    "Gathers the realm and strength of the aura around the "
                    "wand and passes it on to Know the Power, so its wielder "
                    "takes no constant Warping.",
                    constant=True,
                )
                for realm in ("Divine", "Infernal", "Magical", "Faerie")
            ],
            _effect(
                "Know the Power",
                "InVi",
                25,
                3,
                ("Personal", "Momentary", "Individual"),
                "Unlimited",
                "Triggered by the four Sense the Scale effects; gathers what "
                "they learn for later effects.",
            ),
            _effect(
                "The Power's Light",
                "CrIg",
                22,
                4,
                ("Personal", "Concentration", "Individual"),
                "Unlimited",
                "Triggered by Know the Power: the glass glows with the aura's color.",
                concentration=True,
            ),
        ],
    )
    _held(
        b,
        covenant,
        people["conchobor"],
        "Cloak of the Túatha Dé Danann",
        "Wrapped in it, Conchobor passes faerie regiones as easily as the Tuatha "
        "Dé. Nearness to a boundary triggers it, and he chooses whether to "
        "step through. It must penetrate the wearer's Magic Resistance, so "
        "he must suspend his Parma.",
        [
            _effect(
                "Cloak of the Túatha Dé Danann",
                "InVi",
                40,
                20,
                ("Touch", "Momentary", "Vision"),
                "Unlimited",
                "Reveals the way through the boundary.",
                penetration=14,
            )
        ],
    )
    _held(
        b,
        covenant,
        people["conchobor"],
        "Staff of Denial",
        "Dogwood shod with lead, a chain of iron shackles at the top. Dragged "
        "across a surface, it draws a line no faerie of Might 15 or less may "
        "cross; weaker than a circular ward, but it needs no concentration "
        "and serves across an opening or tunnel. Printed 1 a day above a "
        "calculation of 6 a day.",
        [
            _effect(
                "Staff of Denial",
                "ReVi",
                30,
                20,
                ("Touch", "Sun", "Special"),
                "1",
                "Wards the line against faeries of Might 15 or less.",
                penetration=16,
            )
        ],
    )


def _devices(b: Builder, covenant: Covenant) -> None:
    b.device(
        covenant,
        "Ualgrimm's Pelt",
        description=(
            "The covenant's cathach, the pelt of the Bjornaer elder. It came "
            "by this power, they say, through warping at his last stand, and "
            "turns the one it is laid over into a wolf, mind unchanged. 10 "
            "Build Points."
        ),
        effects=[
            _effect(
                "Shape of the Wolf",
                "MuCo",
                25,
                20,
                ("Touch", "Concentration", "Individual"),
                "1",
                "Like Shape of the Woodland Prowler; the target may change "
                "back at will.",
                requisites="Animal",
                concentration=True,
            )
        ],
    )
    b.device(
        covenant,
        "The Enchanted Door",
        description=(
            "Set in a wall of the lesser tower, it opens into the greater "
            "tower across the regio boundary. 12 Build Points."
        ),
        effects=[
            _effect(
                "The Enchanted Door",
                "InVi",
                30,
                20,
                ("Touch", "Momentary", "Vision"),
                "Unlimited",
                "A touch reveals the regio, so covenfolk without Second Sight "
                "pass freely, with no Warping.",
                requisites="Imaginem",
            )
        ],
    )
    b.device(
        covenant,
        "Cearnach's Mount",
        description=(
            "A small wooden horse and rider on a leather thong, worn at the "
            "neck; the thong is brittle and may break if mishandled. 22 Build "
            "Points."
        ),
        effects=[
            _effect(
                "Cearnach's Mount",
                "CrAn",
                51,
                50,
                ("Touch", "Sun", "Group"),
                "2",
                "Makes a living horse and tack, tolerant of The Gift. It tires "
                "and must be fed. A magus may use Finesse for Ride or Animal "
                "Handling with it. Intelligence + Finesse sets the tack's "
                "quality.",
                requisites="Rego, Terram",
            )
        ],
    )
    b.device(
        covenant,
        "The Blade that Slew the Wolf",
        description=(
            "A great sparra five feet tall, its long curved rowan haft ending "
            "in a narrow iron head etched with Irish knotwork and silver-"
            "inlaid Hermetic symbols. Made by Hannewalt of Tytalus and "
            "improved by a Verditius; an arc of mist trails the head, and its "
            "Lab Texts are lost. Only Bran wields it well, and he is not "
            "usually armed with it. Great Weapon, Init +1, Attack +10, "
            "Defense 0, Damage +11; Strength and Load are printed as one "
            "figure, +12. 28 Build Points."
        ),
        effects=[
            _effect(
                "Death with Each Blow",
                "PeAn",
                38,
                15,
                ("Touch", "Momentary", "Individual"),
                "6",
                "On penetrating a beast's Magic Resistance, a Medium wound "
                "beyond the blow's own.",
                penetration=40,
            ),
            _effect(
                "Dull the Stamina of the Wolf",
                "PeAn",
                31,
                5,
                ("Touch", "Momentary", "Individual"),
                "6",
                "Triggered when Death with Each Blow penetrates: the beast "
                "loses a Fatigue Level.",
                penetration=40,
            ),
        ],
    )


def _broken_things(covenant: Covenant) -> None:
    for name, words in (
        (
            "The Broken Shield of Cú Chulainn",
            "Two halves of a wooden shield with a sharpened iron edge, made "
            "for a very large man, shown in the great hall. Once a faerie "
            "weapon that gave skill to its bearer; magically mended, it would "
            "give a Single Weapon Defense Total as if Ability 10. 10 Build "
            "Points.",
        ),
        (
            "The Observance Bell",
            "A cracked and tuneless bronze bell, medium size, in the lesser "
            "tower's belfry. Its magic died nearly forty years ago, and "
            "covenfolk ring it by hand; none knows why, and the magi do not "
            "ask. It was opened with 15 pawns and need not be opened again. "
            "A shallow dent at the crack's top suggests a hammer. Its effects, "
            "whose Lab Texts are in the library: Divine the Heavens' Aspect "
            "(InVi 29, constant, Touch, Sun, Individual, The Mysteries Revised "
            "Edition p. 51), watching the sun, moon, seasons and year to "
            "trigger the rest; Toll the Offices (ReTe 12, 12 a day, Personal, "
            "Diameter, Individual); Toll the Phases of the Moon (ReTe 8, 1 a "
            "day); Toll the Equinoxes and the Solstices (ReTe 8, 1 a day).",
        ),
        (
            "Partholon's Crown",
            "A silver circlet set with diamond, ruby, sapphire and topaz, "
            "said to be of the old times, held by generations of Censors, "
            "each disenchanting it for the next, and now in Mícheál's "
            "wardship. To open it takes at least 20 pawns and Magic Theory "
            "10. Old Lab Texts give effects, which must go in before it is "
            "attuned: Aura of Rightful Authority (ReMe 20), Strings of the "
            "Unwilling Marionette (ReCo 25), Calm the Motion of the Heart "
            "(PeMe 15), Sense the Lingering Magic (InVi 30), Piercing the "
            "Faerie Veil (InVi 20), Haunt of the Living Ghost (CrIm 35). The "
            "elders would frown on another talisman.",
        ),
        (
            "The Warrior Women",
            "Two bronze automata that once opened the main gates on command, "
            "now seized and broken.",
        ),
        (
            "The Clapper of Saint Patrick's Bell",
            "A relic in the chapel, Faith 4 and Divine Might 40: for 5 of its "
            "Might it grants a supplicant the Strong-Willed Virtue for a day. "
            "With it Patrick's iron bell knocked the demon Caoranach from the "
            "sky. The same clapper is said to lie in the Shrine of the Bell "
            "at Armagh, and a Divine relic is there too; that two exist is "
            "surely God's work. 55 Build Points.",
        ),
    ):
        add_possession(covenant, "item", name, description=words)


def _lab_text(
    b: Builder,
    covenant: Covenant,
    name: str,
    kind: str,
    level: int | None,
    words: str,
) -> Book:
    found = b.book(covenant, name, "Lab Text", level=level, description=words)
    found.text_kind = kind
    return found


def _library(b: Builder, covenant: Covenant) -> None:
    for kind, name, author, subject, level, quality, language, words in LIBRARY:
        art, ability = (subject, "") if subject in ARTS else ("", subject)
        b.book(
            covenant,
            name,
            kind,
            art=art,
            ability=ability,
            level=level,
            quality=quality,
            author=author,
            language=language,
            description=words,
        )
    b.codex(
        "De Initio Creaturae",
        [
            b.book(
                covenant,
                "De Initio Creaturae (Dominion Lore)",
                "Tractatus",
                ability="Dominion Lore",
                quality=9,
                author="Aelfric",
                description="One volume holds this and its tractatus on the Infernal.",
            ),
            b.book(
                covenant,
                "De Initio Creaturae (Infernal Lore)",
                "Tractatus",
                ability="Infernal Lore",
                quality=9,
                author="Aelfric",
            ),
        ],
    )
    b.codex(
        "Lebor Feasa Runda",
        [
            b.book(
                covenant,
                "Lebor Feasa Runda (Faerie Lore)",
                "Tractatus",
                ability="Faerie Lore",
                quality=10,
                language=IRISH,
                author="Eochaidh Ollamh Foghla",
                description=paragraphs(
                    "By an ancient High King, translating works from before "
                    "Christ: objects of virtue, rituals that yield vis, and "
                    "powerful bonuses from the sixteen characters of the "
                    "Boibel Loth. No magus has yet brought these into "
                    "Hermetic magic. A most valued possession.",
                    BOIBEL_LOTH,
                ),
            ),
            b.book(
                covenant,
                "Lebor Feasa Runda (Magic Lore)",
                "Tractatus",
                ability="Magic Lore",
                quality=10,
                language=IRISH,
                author="Eochaidh Ollamh Foghla",
                description="Printed as Level 10; a tractatus has only a Quality.",
            ),
        ],
    )
    b.book(
        covenant,
        "The Bible",
        "Tractatus",
        description="Kept in the chapel, as described in The Church p. 49. "
        "The chapel's books cost 53 Build Points.",
    )
    b.book(
        covenant,
        "The Parish Register",
        "Ability Summa",
        ability="Area Lore: Longmist",
        level=1,
        quality=5,
        description="Lately begun, in the chapel.",
    )
    for spell, level, words in (
        (
            "spell_aegis_of_the_hearth",
            60,
            "By Hannewalt of Tytalus; a spell level of 30 and matching "
            "Penetration, printed as ReVi 60. 12 Build Points.",
        ),
        (
            "spell_watching_ward",
            60,
            "By Hannewalt of Tytalus; a spell level of 30 and matching "
            "Penetration, printed as ReVi 60. 12 Build Points.",
        ),
        ("spell_disenchant", 40, "By Hannewalt of Tytalus, PeVi 40. 8 Build Points."),
    ):
        b.tablet(covenant, spell, description=words).level = level
    for name, kind, level, words in LAB_TEXTS:
        _lab_text(b, covenant, name, kind, level, words)


def _vis(covenant: Covenant, labs: dict[str, str]) -> None:
    for name, art, pawns, season, kind, level, words in SOURCES:
        add_possession(
            covenant,
            "vis_source",
            name,
            art=art,
            pawns=pawns,
            season=season,
            vis_kind=kind,
            effect_level=level,
            dwindling=name == "From the Very Walls Themselves",
            description=words,
        )
    for art, pawns in RAW_VIS.items():
        add_possession(
            covenant,
            "vis_store",
            f"{art} vis in the stores",
            art=art,
            pawns=pawns,
            description="Built up over the years, dusty and forgotten in the "
            "bottoms of chests; unusual for a Hibernian covenant.",
        )
    stores: tuple[tuple[str, str, int, str, int | None, str, str, str], ...] = (
        (
            "Maghera Stones",
            "Rego",
            25,
            "lesser_enchantment",
            14,
            "Spread about the covenant as floating furniture.",
            "",
            "",
        ),
        (
            "Metal Shards",
            "Ignem",
            25,
            "spell_like",
            14,
            "Pieces from Cathal Gobha's forge.",
            "",
            "",
        ),
        (
            "Fleas of Saint Nannan",
            "Animal",
            15,
            "spell_like",
            20,
            "Soil in linen in glass jars, from a Connacht meadow where Saint "
            "Nannan swept a village's fleas, which Giraldus Cambrensis "
            "describes; no one can stay long there. Each pawn scattered on "
            "any ground raises 1000 natural fleas, unaffected by Magic "
            "Resistance (ReAn 20, Touch, Momentary, Group). 3 Build Points "
            "for each 5 pawns.",
            "",
            "",
        ),
        (
            "Destroy the Fleas of Saint Nannan",
            "Animal",
            5,
            "spell_like",
            45,
            "Soil in linen in glass jars, from the Connacht village where no "
            "flea can live. Each pawn scattered kills animals up to a "
            "standard group, of any type, so take care (PeAn 45, Touch, "
            "Momentary, Group). 6 Build Points for each 5 pawns.",
            "",
            "",
        ),
        (
            "The Burning Hand",
            "Ignem",
            5,
            "lesser_enchantment",
            9,
            "A macabre gift of the Tuatha Dé: a left hand cut from a corpse. A "
            "candle between its fingers lights and burns on with magical "
            "flame until removed (CrIg 9, constant). 2 Build Points.",
            "laboratory",
            "conchobor",
        ),
        (
            "The Balm of Tír nan Óg",
            "Creo",
            20,
            "spell_like",
            40,
            "A faerie gift, five doses left of four pawns each; splitting a "
            "dose loses its magic. Applied to a stricken target it holds off "
            "age, so that the target overcomes a terminal aging crisis (CrCo "
            "40, Touch, Momentary, Individual). A dose failed Tadhg an Tuir. "
            "20 Build Points.",
            "laboratory",
            "lugh",
        ),
        (
            "The Ax of Cú Roí mac Dáire",
            "Mentem",
            10,
            "accrued",
            None,
            "A faerie weapon in the great hall, too large for an ordinary man, "
            "said to be the Ulaidh king's. It is a Pole Ax, but anyone with "
            "Brave +3 or more, which replaces its Strength +1 requirement, "
            "gains the Heroic Combat pretense and wields it one-handed as at "
            "Ability 10. Penetration +10 against the wielder's own Magic "
            "Resistance (Realms of Power: Faerie pp. 19, 62). 10 Build Points.",
            "",
            "",
        ),
    )
    for name, art, pawns, kind, level, words, where, keeper in stores:
        add_possession(
            covenant,
            "vis_store",
            name,
            art=art,
            pawns=pawns,
            vis_kind=kind,
            effect_level=level,
            location_kind=where,
            location_id=labs[keeper] if keeper else None,
            description=words,
        )


def _holdings(covenant: Covenant) -> None:
    add_possession(
        covenant,
        "property",
        "The Fish Runs",
        location="The stream feeding Lough Beagh",
        description="Looping channels cut into the banks, set with fish "
        "traps, feeding the covenant with a surplus sold at Inniskil. With "
        "the toll bridge, a Lesser Income Source of 80 Mythic Pounds.",
    )
    add_possession(
        covenant,
        "property",
        "The Toll Bridge",
        location="South of Lough Beagh",
        description="Held by the grogs. A larger English bridge further south "
        "is drawing the traffic, so it may stop paying in five years: from "
        "the start of play, take 8 Mythic Pounds a year off earned income. "
        "Jealous eyes weigh up its guards.",
    )


def _ruadan(hibernia: Hibernia, covenant: Covenant, site: Neighbour) -> None:
    b = hibernia.b
    ruadan = b.creature(
        "Ruadan mac Goibhniu",
        page="p. 119",
        realm="Faerie",
        might=40,
        form="Terram",
        source=SOURCE,
        place=site,
        confidence=(4, 3),
        block={
            "characteristics": characteristics(2, 0, 0, 0, 1, 0, 3, 0),
            "virtues_flaws": [
                "Highly Cognizant",
                "Humanoid Faerie",
                "Faerie Sight",
                "Faerie Speech",
                "Lesser Power",
                (
                    "Time or Place of Power",
                    {"detail": "the Otherworld burrows beneath Longmist"},
                ),
                "Reputation as Confidence",
                "Ritual Power",
                "Ritual Power",
                "Negative Reaction",
                vf_ward("The Dominion"),
            ],
            "abilities": [
                ("Area Lore: Ulaid", 6, "sites of historic significance"),
                ("Artes Liberales", 3, "rhetoric"),
                ("Animal Handling", 2, "faerie hounds"),
                ("Athletics", 6, "running"),
                ("Awareness", 2, "ambushes"),
                ("Bargain", 7, "magi"),
                ("Brawl", 6, "knife"),
                ("Craft: Weapons and Armor", 9, "swords"),
                ("Etiquette", 7, "maintaining the dignity of the Tuatha Dé"),
                ("Faerie Speech", 6, "poetry"),
                ("Faerie Weapons", 7, "great swords"),
                ("Guile", 3, "men"),
                ("Intrigue", 4, "against magi"),
                ("Leadership", 6, "in warfare"),
                ("Organization Lore: Covenant of Longmist", 5, "history"),
                ("Organization Lore: Order of Hermes", 5, "conflicts"),
                ("Penetration", 6, "using Arcane Connections"),
                ("Teaching", 6, "crafting weapons and armor"),
            ],
            "traits": {"Regal": 3, "Manipulative": 2, "Forgiving": -2},
            "reputations": {
                "Crafter of Arms and Armor": 4,
                "Prince of the Otherworld": 3,
                "Descendant of Goibhniu": 2,
                "Protector of Longmist": 1,
            },
        },
        attacks=[
            b.attack("Dodge", -2, None, 6, None),
            b.attack("Fist", -2, 9, 6, 1),
            b.attack("Mortal Blades", -2, 11, 6, 3),
            b.attack("Knife of Sorrows", -2, 16, 7, 3),
            b.attack("Great Sword of the Moon", 0, 20, 9, 10),
        ],
        soak=14,
        powers=[
            b.power(
                "Binding Oath",
                10,
                -20,
                "Vim",
                does="Enforces a solemn oath or contract between parties. "
                "Realms of Power: Faerie p. 56. Init is Qik - 20.",
            ),
            b.power(
                "The Blood of Goibhniu",
                1,
                -2,
                "Vim",
                does="Variable points, Init Qik - twice the points. Crafts "
                "faerie arms and armor of strange stuff such as moonlight, "
                "song, loss, anger or a storm's power, for 1 point of Might "
                "Score and up to 9 more to enchant up to 45 levels, one "
                "effect under the usual modifiers. Those points return only "
                "by consuming faerie Vim vis or smelting the weapon back.",
            ),
            b.power(
                "Grant Puissance in Craft Arms and Armor",
                2,
                -2,
                "Corpus",
                does="For each Might point spent, +3 to one person's totals "
                "for making weapons and armor, the points regained only when "
                "it is withdrawn. Must penetrate when given.",
            ),
        ],
        equipment=(
            "Armor forged from tempered night (Protection +14), a long slender "
            "sword of purest moonlight, and a dagger poisoned with loss."
        ),
        vis=[],
        appearance=(
            "A tall, handsome man seemingly in his early thirties, attractive "
            "but for bright blue skin and red eyes, with lustrous blond hair "
            "and oil-black armor that fascinates in torchlight."
        ),
        notes=paragraphs(
            "A prince and druid of the Tuatha Dé, descended from Goibhniu the "
            "smith, whose craft he has, though his counsel serves the "
            "covenant more than his magic. He mediates with the faerie world, "
            "his soldiers guard the cathach, and the charter gives him a seat "
            "at council, where his chief ally is Conchobor. He always counsels "
            "keeping the valley shut.",
            "Might +10 in his place of power, the labyrinth beneath Longmist, "
            "where his forge's exotic supplies and magical fires add +2 to "
            "make Superior arms and armor, and Excellent swords (City & Guild "
            "p. 69). His combat figures assume his faerie weapons; the "
            "abilities are pretenses, and Faerie Weapons covers all faerie-"
            "made or -touched weapons, mortal ones being no better than "
            "bludgeons in his hands. The great sword and knife need his "
            "training, and then give +5 to attack. Wounds: -1 (1-5), -3 "
            "(6-10), -5 (11-15), Incapacitated (16-20), Dead (21+). Vis: 8 "
            "pawns of Rego, +2 in the Otherworld.",
            "Great Sword of the Moon: MuCo 45, Pen +20, unlimited, Sight, "
            "Concentration, Group: those who count themselves his allies see "
            "it glow and can see in darkness as under a full moon. The Knife "
            "of Sorrows: CrMe 45, Pen +50, 1 a day, Touch, Moon, Individual: "
            "poisons the mind with loss for a Moon; each day a Personality "
            "roll against Ease Factor 9 holds it off, failure bringing -3 to "
            "all totals.",
        ),
        secrets=(
            "He may only now be ready to act on a plan of centuries for Longmist."
        ),
    )
    b.link(covenant, "creatures", ruadan, "Mediator, seated at its council")


def _bronze_man(hibernia: Hibernia, covenant: Covenant, site: Neighbour) -> None:
    b = hibernia.b
    man = b.creature(
        "The Bronze Man",
        page="pp. 122, 124",
        realm="Magic",
        might=17,
        size=2,
        source=SOURCE,
        place=site,
        tires=False,
        block={
            "characteristics": characteristics(0, 0, 0, 0, 1, 0, 1, 0),
            "abilities": [("Craft: Blacksmith", 5, "")],
        },
        attacks=[
            b.attack("Dodge", 0, None, 0, None),
            b.attack("Fist", 0, 1, 0, 1),
            b.attack("Bludgeon", 0, 3, 0, 3),
        ],
        soak=25,
        powers=[
            b.power(
                "Freedom of Movement",
                0,
                0,
                "Terram",
                rtd=("Personal", "Sun", "Part"),
                level=29,
                does="ReTe(Me), constant: walks as directed, careful of people "
                "and things.",
            ),
            b.power(
                "Dexterity of the Master",
                0,
                0,
                "Terram",
                rtd=("Personal", "Sun", "Part"),
                level=29,
                does="CrTe, constant: Dexterity +1.",
            ),
            b.power(
                "Strength of the Master",
                0,
                0,
                "Terram",
                rtd=("Personal", "Sun", "Part"),
                level=29,
                does="CrTe, constant: Strength +1.",
            ),
            b.power(
                "The Master At Work",
                0,
                0,
                "Terram",
                rtd=("Personal", "Sun", "Part"),
                level=49,
                does="ReTe(Me), constant: Craft: Blacksmith 5.",
            ),
        ],
        appearance=(
            "A bare-chested bearded craftsman in bronze, larger than life and "
            "classical of face, though the complex joints betray him."
        ),
        notes=paragraphs(
            "An automaton of Faventinus of Verditius, the Cailleach's "
            "grand-parens, who used it at the forge until something made him "
            "send it into the courtyard for good; most now take it for a "
            "statue. Mute, it has seen and heard everything in the courtyard "
            "for 80 years. Opened with 17 pawns, 14 used, room for up to 30 "
            "levels more. Its powers are constant, and it can suspend them on "
            "command. 48 Build Points.",
            "Its Might is damaged: effective Might 6, -5 to any Ability roll. "
            "Repair needs the Verditius Automata Inner Mystery (Houses of "
            "Hermes: Mystery Cults p. 128); investigating its powers is a "
            "standard laboratory action, and reveals the command words. "
            "Working, it follows instructions of any complexity about its "
            "smithing, and any others needing neither positive Intelligence "
            "nor an Ability but Craft: Blacksmith. Soak +25 applies to Damage "
            "Checks, with 4 Damage Levels (City & Guild p. 77).",
        ),
    )
    b.link(covenant, "creatures", man, "In the great courtyard")


def _clan(hibernia: Hibernia, longmist: Covenant) -> None:
    b, m = hibernia.b, hibernia.magi
    clan = b.covenant(
        CLAN,
        founded=None,
        detail=FULL,
        season="",
        unnamed_magi=5,
        summary=paragraphs(
            "A nomadic line of seven Bjornaer, an unofficial covenant that "
            "moves through Hibernia with the seasons, setting up mobile "
            "laboratories in booley villages, simple dwellings lived in for "
            "a season or two. It seeks those with Magical auras, many on lake "
            "islands, some with regiones. It robs other covenants and shelters "
            "outlaws. Its founder Ualgrimm was killed and skinned for "
            "Longmist's cathach, and its leader Cú Chonnacht Cluasach Mac "
            "Tire has vowed to put that right.",
            "Income. Robbery, raiding and hiring out to other magi and "
            "covenants; the grogs thieve enough to pay for provisions.",
            "Now. Cú Chonnacht is old and weak, and too many failures to win "
            "back the pelt have shaken the clan's faith. His junior Bán wants "
            "to strike the pelt's protectors, Prince Ruadan and his subjects, "
            "not the pelt. The clan lacks raw magical power, but commands a "
            "large band of robbers and mercenaries, enough to challenge the "
            "faeries guarding the cathach, and an assault will soon come.",
        ),
        what_matters=joined_lines(
            "Boon: Criminals (raids other covenants, shelters outlaws)",
            "Boon: Difficult Access (booleys on lake islands, some in regiones)",
            "Boon: Informants (robbers across Ulaid)",
            "Boon: Hidden Resources (stored in booleys they often visit, so "
            "not always to hand)",
            "Boon: Hidden Ways (the best paths round their regular camps, as "
            "wolves and magi)",
            "Hook: Indiscreet Resource (Major) (theft, robbery and coercion)",
            "Hook: Erratically Mobile (sometimes a season in each booley)",
            "Hook: Infamous (known to covenants across Hibernia)",
            "Peace: it accepts nothing less than the pelt, and Longmist needs "
            "a new trophy before it can give that up",
        ),
        notes=(
            "Troupes may detail the Clan as far as they need. It may seek "
            "allies against Longmist with a share of the spoils; Longmist "
            "may hire others to track it through Ulaid and into Connacht, and "
            "an enemy of both could bring a truce."
        ),
        secrets=(
            "Bán feels no tie to the cathach, and means to use the clan's "
            "wound to strip Cú Chonnacht of his leadership."
        ),
    )
    clan.boons_hooks = boons_hooks_from(clan.what_matters)
    hibernia.covenants["clan_mac_tire"] = clan
    m["ban"] = b.magus(
        "Bán Mac Tire",
        covenant=clan,
        house=BJORNAER,
        age=None,
        summary="Cú Chonnacht's junior, whose heartbeast is a white wolf, and "
        "who grows impatient with the old man. The book gives no stat block.",
    )
    b.laboratory(
        clan,
        "A Mac Tire mobile laboratory",
        characteristics=dict(MOBILE_LAB),
        specializations={"Animal": 1, "Experimentation": 2, "Mentem": 1},
        source=f"{BOOK} p. 120",
        rooms={
            "A booley": "Each of the seven has one like it, packed for carriage "
            "by servants and soldiers, and doubling as his living quarters, of "
            "which the younger magi often complain. Size +0 (0). Virtues: "
            "Lesser Feature (cauldron), Living Quarters, Mobile, Specimens, "
            "Servant (Intelligence +2, a learned clerk, loyal from fear). "
            "Flaws: Hovel. Marker: none added."
        },
    )
    b.link(longmist, "covenants", clan, "Its sworn enemy, for Ualgrimm's pelt")
    b.link(clan, "covenants", longmist, "Holds Ualgrimm's pelt")
    leader = m.get("cu_chonnacht")
    if leader is not None:
        b.link(clan, "characters", leader, "Its leader")


#: Words for the spells the book adds, by name: Range, Duration, Target,
#: base level, description.
_MASTER = (
    "Commands an airy spirit of the Form for a Moon. If it penetrates, a "
    "stress roll of Com + Leadership shows how far the spirit is controlled."
)
_SUMMON = (
    "Brings the airy spirit to the caster, by Arcane Connection. Nothing makes it stay."
)
NEW_SPELLS: dict[str, tuple[str, str, str, int, str]] = {
    "Lash the Wayward Spirit": (
        "Voice",
        "Momentary",
        "Individual",
        0,
        "As Demon's Eternal Oblivion, for magical spirits.",
    ),
    **{
        f"Master the Airy Spirit of {form}": (
            "Voice",
            "Moon",
            "Individual",
            5,
            _MASTER,
        )
        for form in ("Aquam", "Auram", "Ignem", "Terram")
    },
    **{
        f"Summon the Airy Spirit of {form}": (
            "Arcane",
            "Momentary",
            "Individual",
            15,
            _SUMMON,
        )
        for form in ("Aquam", "Auram", "Ignem", "Terram")
    },
}


def _spell_words(hibernia: Hibernia) -> None:
    """The book's own words for the spells its blocks add, after `stats`
    has made them."""
    for magus in hibernia.magi.values():
        for spell in magus.invented_spells:
            printed = NEW_SPELLS.get(spell.name)
            if printed is None or spell.source != SOURCE:
                continue
            spell.range, spell.duration, spell.target = printed[:3]
            spell.base_level = printed[3] or None
            spell.description = printed[4]
