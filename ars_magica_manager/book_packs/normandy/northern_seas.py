"""The Northern Seas, a Spring covenant of six ships, nominally of the
Normandy Tribunal, as of 1220, in paraphrase of Through the Aegis,
chapter two: the covenant, its six magi and Carles's familiar, its
companions and grogs, its fleet, laboratories, devices, library and vis,
and the demon among its crews.

It sails as a fleet, so it has no place of its own: it opens at a sea
Place with an aura of 0 (Missing Aura, Erratically Mobile), and no route
is printed. Barfleur is its home port, a Port of The Region. Stat blocks
are the book's; the rest is a summary, not its words."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import storage
from ...models import CharterClause, CovenantStop, Familiar, ScoredTrait
from ...models.holdings import Possession
from ...models.ships import Ship
from ...models.world import FULL
from ...rules import mobile, sites
from ..builder import (
    Builder,
    StatBlock,
    add_possession,
    arts_from,
    characteristics,
    joined_lines,
    paragraphs,
    vf_ability,
    vf_art,
    vf_great,
    vf_puissant,
    virtue_flaw_from_block,
)

if TYPE_CHECKING:
    from ...models import Character, Covenant
    from . import Normandy

SOURCE = "TtA"
NAME = "The Northern Seas"
TYTALUS = "house_tytalus"
BJORNAER = "house_bjornaer"
EX_MISCELLANEA = "house_ex_miscellanea"
VERDITIUS = "house_verditius"
TREMERE = "house_tremere"
JERBITON = "house_jerbiton"

SHIPBOARD_LAB = {
    "general_quality": -1,
    "safety": -1,
    "aesthetics": -1,
}
SHIPBOARD_WORDS = (
    "Fitted into the rear of the hold, about 20 feet by 25, at the cost of "
    "25 tonnes of cargo. Virtues: Mobile, Extensive Stores. Flaws: Cramped, "
    "Unstable."
)

CARLES: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 2, 0, 0, 0, 0),
    "confidence": (2, 5),
    "warping": (4, 12),
    "apparent_age": 53,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        ("Major Magical Focus", {"focus": "the sea"}),
        ("Ways of the {land}", {"land": "Sea"}),
        "Inspirational",
        "Self-Confident",
        ("True Friend", {"detail": "Ojo"}),
        "Warrior",
        ("Driven", {"detail": "found his own Tribunal"}),
        "Magic Addiction",
        "Infamous",
        ("True Friend", {"detail": "Hilde"}),
    ],
    "traits": {
        "Driven": 6,
        "Gregarious": 3,
        "Loyal to Ojo": 3,
        "Daring": 2,
        "Reluctant to cast magic": 2,
        "Wanderer": 1,
    },
    "reputations": {"Daring scoundrel (Normandy)": 4},
    "abilities": [
        ("Area Lore: The Northern Seas", 5, "geography"),
        ("Artes Liberales", 3, "astronomy"),
        ("Athletics", 3, "climbing"),
        ("Awareness", 2, "alertness"),
        ("Brawl", 2, "bludgeon"),
        ("Code of Hermes", 4, "tribunal procedures"),
        ("Concentration", 4, "controlling Magic Addiction"),
        ("Dominion Lore", 2, "relics"),
        ("Faerie Lore", 3, "naiads"),
        ("Finesse", 3, "casting speed"),
        ("Folk Ken", 2, "magi"),
        ("Infernal Lore", 2, "demons"),
        ("Intrigue", 3, "alliances"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Leadership", 4, "magi"),
        ("Magic Lore", 4, "auras"),
        ("Magic Theory", 7, "Auram"),
        ("Navigation", 4, "at sea"),
        ("Living Language: French", 5, "storytelling"),
        ("Organization Lore: Order of Hermes", 3, "politics"),
        ("Parma Magica", 4, "Mentem"),
        ("Penetration", 4, "Aquam"),
        ("Philosophiae", 1, "natural philosophy"),
        ("Profession: Sailor", 4, "Northern Seas"),
        ("Single Weapon", 4, "kilij"),
        ("Swim", 3, "diving"),
    ],
    "arts": arts_from(
        "Cr 10, In 9, Mu 9, Pe 11, Re 12, An 10, Aq 13, Au 9, Co 11, He 7, "
        "Ig 8, Im 5, Me 8, Te 8, Vi 9"
    ),
    "spells": [
        ("Agony of the Beast", "PeAn", 15, 0),
        ("Clear Sight of the Naiad", "InAq", 5, 0),
        ("Call of the Rushing Waters", "InAq", 15, 0),
        ("Neptune's Imprisoning Arms", "MuAq", 25, 0),
        ("Break the Oncoming Wave", "ReAq", 10, 0),
        ("Ward Against Faeries of the Waters", "ReAq", 20, 1),
        ("Bind Wound", "CrCo", 10, 0),
        ("The Inexorable Search", "InCo", 20, 1),
        ("In Christ's Footsteps", "ReCo", 5, 0),
        ("Piercing Shaft of Wood", "MuHe", 10, 0),
        ("Lamp without Flame", "CrIg", 10, 0),
        ("Hornet Fire", "MuIg(Re)", 10, 0),
        ("Quench the Raging Conflagration", "PeIg", 20, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Unseen Arm", "ReTe", 5, 0),
        ("Sense of Divine Power", "InVi", 2, 0),
        ("Sense of Faerie Power", "InVi", 2, 0),
        ("Sense of Infernal Power", "InVi", 2, 0),
        ("Sense of Magical Power", "InVi", 2, 0),
        ("Scales of the Magical Weight", "InVi", 5, 0),
        ("Sense the Nature of Vis", "InVi", 5, 0),
        ("Demon's Eternal Oblivion", "PeVi", 10, 1),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "masteries": {
        "Ward Against Faeries of the Waters": ["Penetration"],
        "The Inexorable Search": ["Penetration"],
        "Demon's Eternal Oblivion": ["Penetration"],
    },
    "notes": paragraphs(
        "An ageing man of the sea, with a dashing grin and an athletic frame, "
        "weathered and tanned, his blond hair turning grey and thick with "
        "salt. Casting sigil: a wind swirling round the caster. Voting sigil: "
        "a palm-sized crab shell inlaid with silver. Twilight scar: he must "
        "drink brine in place of fresh water, or suffer as a mortal drinking "
        "brine.",
        "Combat: dodge Init +3, Defense +5; kilij Init +4, Attack +12, "
        "Defense +9, Damage +6, including the +3 from Ways of the Sea. Soak "
        "+1. His Longevity Ritual gives -9 to aging rolls. Encumbrance 1.",
        "Talisman: a Turkish kilij with a gilded hilt set with a topaz, "
        "opened with 14 pawns. Effects: Waves of Drowning and Smashing (ReAq "
        "30, 1 a day), Wizard's Leap (ReCo 18, 6 a day), The Wound that Weeps "
        "(PeCo 30, Pen +24, 6 a day), Rusted Decay of Ten Score Years (PeTe "
        "20, Pen +24, 6 a day, on striking metal). Attunements: iron +7 to "
        "harm or repel faeries; sword +4 to harm human and animal bodies; "
        "topaz +4 leadership and +4 strength, courage and pride. Its Lab "
        "Texts are not translated and not available to the covenant.",
        "He holds fixed Arcane Connections to Boulogne, Southampton, La "
        "Charytee and Hilde.",
    ),
}

HILDE: StatBlock = {
    "characteristics": characteristics(1, 0, 3, 0, 2, 0, 0, 2),
    "aging_points": {"intelligence": 1, "presence": 2, "quickness": 2},
    "size": 2,
    "confidence": (1, 3),
    "decrepitude": (1, 0),
    "warping": (4, 20),
    "apparent_age": 50,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flawless Magic",
        "Giant Blood",
        "Mystery of the Epitome",
        "Berserk",
        ("Heartbeast", {"detail": "shark"}),
        "Improved Characteristics",
        "Lightning Reflexes",
        "Chaotic Magic",
        ("Fury", {"detail": "blood in the water"}),
        ("True Friend", {"detail": "Carles"}),
        "Careless Sorcerer",
        "Clumsy Magic",
        "Greedy (Minor)",
    ],
    "traits": {
        "Shark": 3,
        "Angry": 2,
        "Loyal to Carles Magnus": 2,
        "Studious": -1,
    },
    "reputations": {"Afflicted (House Bjornaer)": 3, "Dangerous (Normandy)": 2},
    "abilities": [
        ("Artes Liberales", 3, "ritual magic"),
        ("Athletics", 3, "grace"),
        ("Awareness", 2, "in the water"),
        ("Bjornaer Lore", 5, "modifying initiation scripts"),
        ("Brawl", 4, "bite"),
        ("Carouse", 1, "power drinking"),
        ("Code of Hermes", 3, "tribunal procedures"),
        ("Faerie Lore", 2, "faeries of the sea"),
        ("Finesse", 3, "fast casting"),
        ("Living Language: French", 4, "slang"),
        ("Living Language: German", 5, "slang"),
        ("Heartbeast", 6, "regain human form"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Magic Lore", 3, "giants"),
        ("Magic Theory", 6, "inventing spells"),
        ("Organization Lore: Order of Hermes", 2, "personalities"),
        ("Parma Magica", 5, "Animal"),
        ("Penetration", 5, "Corpus"),
        ("Philosophiae", 3, "ritual magic"),
        ("Swim", 5, "underwater maneuvering"),
    ],
    "arts": arts_from(
        "Cr 10, In 8, Mu 5, Pe 12, Re 7, An 13, Aq 8, Au 5, Co 13, He 11, "
        "Ig 5, Im 3, Me 5, Te 5, Vi 7"
    ),
    "spells": [
        ("Image of the Beast", "InAn", 5, 1),
        ("Hunter's Sense", "InAn", 30, 1),
        ("The Baleful Eye that Pains the Beast", "PeAn", 20, 1),
        ("Cripple the Howling Wolf", "PeAn", 25, 1),
        ("Viper's Gaze", "ReAn", 15, 1),
        ("Subtle Taste of Poison and Purity", "InAq", 5, 1),
        ("The Wound that Weeps", "PeCo", 20, 1),
        ("Grip of the Choking Hand", "PeCo", 25, 1),
        ("The Withering Eye", "PeCo", 25, 1),
        ("Evisceration of a Thousand Knives", "PeCo", 30, 1),
        ("Endurance of the Berserkers", "ReCo", 15, 1),
        ("Demon's Eternal Oblivion", "PeVi", 10, 1),
        ("Dreadful Bane of the Fae", "PeVi", 10, 1),
    ],
    "masteries": {
        "Image of the Beast": ["Penetration"],
        "Hunter's Sense": ["Penetration"],
        "The Baleful Eye that Pains the Beast": ["Penetration"],
        "Cripple the Howling Wolf": ["Penetration"],
        "Viper's Gaze": ["Penetration"],
        "Subtle Taste of Poison and Purity": ["Quiet Casting"],
        "The Wound that Weeps": ["Penetration"],
        "Grip of the Choking Hand": ["Penetration"],
        "The Withering Eye": ["Penetration"],
        "Evisceration of a Thousand Knives": ["Penetration"],
        "Endurance of the Berserkers": ["Fast Casting"],
        "Demon's Eternal Oblivion": ["Penetration"],
        "Dreadful Bane of the Fae": ["Penetration"],
    },
    "notes": paragraphs(
        "Very large, broad in the shoulder and powerful in arm and leg, with "
        "a wide grin of too many teeth. Casting sigil: brine seeps from her "
        "skin with each spell. Voting sigil: a shark's tooth of smooth black "
        "stone. She enchants nothing, wedded to a Bjornaer sense of purity. "
        "Her Longevity Ritual gives -6 to aging rolls.",
        "Combat, the second figure berserk: dodge Init +2, Defense +6/+4; "
        "bite Init +2, Attack +5/+7, Defense +7/+5, Damage +2; bludgeon Init "
        "+2, Attack +6/+8, Defense +6/+4, Damage +4. Soak 0/+2.",
        "Shark heartbeast, Size +3, under Houses of Hermes: Mystery Cults p. "
        "23. Characteristics Int +1, Per -2, Pre -3 (+3 to intimidate), Com "
        "-6, Str +7 (Inner Heartbeast +10), Sta 0, Dex +2, Qik +1. Large "
        "teeth Init 0, Attack +11, Defense +6, Damage +10 (Inner +13). Soak "
        "+2. Brave +3, Greedy +3, Cruel +2. Qualities: Aggressive, Ambush "
        "Predator, Aquatic, Large Teeth, Loathsome Appearance. Mythic Feat: "
        "for a Confidence Point the Inner Heartbeast may inflict a Heavy "
        "Wound on a creature of Size +1 or less on a hit.",
    ),
}

COLUMBA: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 3, -1, 0, -1, -1),
    "confidence": (1, 3),
    "apparent_age": 29,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Secondary Insight",
        "Cautious Sorcerer",
        "Clear Thinker",
        "Good Teacher",
        "Hermetic Prestige",
        vf_puissant("Artes Liberales"),
        "Strong-Willed",
        "Tormenting Master",
        "Waster of Vis",
        "Ambitious (Minor)",
        ("Flawed Parma Magica", {"detail": "Ignem"}),
    ],
    "traits": {"Ambitious": 3, "Strong-willed": 3, "Perfectionist": 1},
    "reputations": {"The maga who turned her back on House Guernicus (Order)": 3},
    "abilities": [
        ("Artes Liberales", 2, "rhetoric"),
        ("Charm", 2, "debate"),
        ("Code of Hermes", 4, "tribunal procedures"),
        ("Finesse", 2, "casting speed"),
        ("Folk Ken", 2, "magi"),
        ("Guile", 2, "debate"),
        ("Intrigue", 2, "debate"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 2, "debate"),
        ("Magic Theory", 4, "binding familiar"),
        ("Living Language: French", 4, "poetry"),
        ("Organization Lore: Order of Hermes", 3, "personalities"),
        ("Parma Magica", 2, "Mentem"),
        ("Penetration", 2, "Mentem"),
        ("Philosophiae", 1, "moral philosophy"),
        ("Living Language: Spanish", 5, "poetry"),
    ],
    "arts": arts_from(
        "Cr 4, In 7, Mu 4, Pe 4, Re 4, An 0, Aq 0, Au 0, Co 4, He 0, Ig 3, "
        "Im 5, Me 6, Te 0, Vi 4"
    ),
    "spells": [
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
        ("Despair of the Quivering Manacles", "ReCo", 15, 0),
        ("Wizard's Leap", "ReCo", 15, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Perception of the Conflicting Motives", "InMe", 15, 0),
        ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
        ("Posing the Silent Question", "InMe", 20, 0),
        ("Loss of But a Moment's Memory", "PeMe", 15, 0),
    ],
    "notes": paragraphs(
        "Dark hair cropped short, dress immaculate, an erect bearing that "
        "gives an illusion of height. Casting sigil: whispers in her own "
        "voice, reciting the incantation. Voting sigil: half an iron manacle, "
        "apparently broken open.",
        "Combat: dodge Init -1, Defense -1; knife Init -1, Attack 0, Defense "
        "-1, Damage +1. Soak 0.",
    ),
}

TIBOR: StatBlock = {
    "characteristics": characteristics(2, 0, 1, 0, 0, 2, 0, 0),
    "confidence": (1, 3),
    "apparent_age": 25,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Life-Linked Spontaneous Magic",
        vf_art("Affinity with {art}", "Rego"),
        ("Minor Magical Focus", {"focus": "certamen"}),
        "Skilled Parens",
        vf_puissant("Philosophiae"),
        "Lycanthrope",
        "Busybody",
        "Hermetic Patron",
        ("Deleterious Circumstances", {"detail": "touching or wearing silver"}),
    ],
    "traits": {"Analytical": 3, "Secretive": 2, "Obedient": 1},
    "reputations": {"Cursed (magi of Coeris)": 2},
    "abilities": [
        ("Artes Liberales", 2, "ceremonial magic"),
        ("Athletics", 1, "grace"),
        ("Awareness", 2, "determining effect"),
        ("Brawl", 2, "knife"),
        ("Concentration", 2, "spell concentration"),
        ("Finesse", 1, "casting speed"),
        ("Folk Ken", 1, "magi"),
        ("Guile", 1, "particular sorts of deception"),
        ("Infernal Lore", 1, "curses"),
        ("Intrigue", 1, "plotting"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 1, "magi"),
        ("Magic Lore", 1, "creatures"),
        ("Magic Theory", 4, "inventing spells"),
        ("Parma Magica", 1, "Mentem"),
        ("Penetration", 2, "Mentem"),
        ("Philosophiae", 2, "ceremonial magic"),
        ("Living Language: Magyar", 5, "storytelling"),
        ("Swim", 1, "long distances"),
    ],
    "arts": arts_from(
        "Cr 0, In 7, Mu 0, Pe 4, Re 13, An 3, Aq 1, Au 0, Co 3, He 0, Ig 2, "
        "Im 1, Me 7, Te 0, Vi 8"
    ),
    "spells": [
        ("Circle of Beast Warding", "ReAn", 5, 0),
        ("Soothe the Ferocious Bear", "ReAn", 10, 0),
        ("Lifting the Dangling Puppet", "ReCo", 15, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Ring of Warding Against Spirits", "ReMe", 15, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Coerce the Spirits of the Night", "ReMe", 20, 0),
        ("Piercing the Magical Veil", "InVi", 20, 0),
        ("Circular Ward Against Demons", "ReVi", 15, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "notes": paragraphs(
        "An intense dark-haired young man with narrow eyes that linger, in "
        "plain austere robes. Casting sigil: the target is bathed in "
        "moonlight. He does not hold his voting sigil.",
        "Combat: dodge Init 0, Defense +2; knife Init 0, Attack +4, Defense "
        "+3, Damage +2. Soak +2.",
        "Wolf form, Size -1: Cun +2, Per 0, Pre +1, Com 0, Str -1, Sta +3, "
        "Dex +2, Qik +2. Teeth Init +2, Attack +11, Defense +9, Damage 0; "
        "claws Init +1, Attack +9, Defense +10, Damage +1. Soak +7. Athletics "
        "5, Awareness 3, Brawl 5, Hunt 4. Reputation Bloodthirsty 4 (local). "
        "Shaggy pale grey fur and a steady yellow gaze.",
    ),
}

MATILDA: StatBlock = {
    "characteristics": characteristics(3, 0, -1, 2, -2, 0, 2, -1),
    "confidence": (1, 3),
    "apparent_age": 30,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Elemental Magic",
        vf_ability("Affinity with {ability}", "Magic Theory"),
        "Inventive Genius",
        vf_puissant("Magic Theory"),
        "Verditius Magic",
        ("Deficient Technique", {"art": "Muto"}),
        "Temperate",
        "Close Family Ties",
        "Susceptibility to Infernal Power",
    ],
    "traits": {"Temperate": 3, "Timid": 3, "Boisterous": -2, "Boastful": -1},
    "abilities": [
        ("Area Lore: Southern England", 2, "geography"),
        ("Artes Liberales", 2, "grammar"),
        ("Awareness", 2, "alertness"),
        ("Code of Hermes", 1, "apprentices"),
        ("Living Language: English", 5, "storytelling"),
        ("Folk Ken", 2, "magi"),
        ("Craft: Painter", 5, "illumination"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 2, "laboratory work"),
        ("Magic Theory", 5, "enchanting items"),
        ("Organization Lore: Order of Hermes", 1, "politics"),
        ("Philosophiae", 3, "enchantments"),
        ("Craft: Scribe", 3, "scrolls"),
        ("Verditius Cult Lore", 2, "initiating others"),
    ],
    "arts": arts_from(
        "Cr 6, In 4, Mu 2, Pe 4, Re 7, An 0, Aq 7, Au 6, Co 2, He 0, Ig 7, "
        "Im 0, Me 0, Te 7, Vi 6"
    ),
    "spells": [
        ("Broom of the Winds", "CrAu", 15, 0),
        ("Whispering Winds", "InAu", 15, 0),
        ("Break the Oncoming Wave", "ReAq", 10, 0),
        ("Lamp without Flame", "CrIg", 10, 0),
        ("Pilum of Fire", "CrIg", 20, 0),
        ("Gloom of Evening", "PeIg", 10, 0),
        ("The Miner's Keen Eye", "InTe", 20, 0),
        ("Eyes of the Eons", "InTe", 10, 0),
        ("Wielding the Invisible Sling", "ReTe", 10, 0),
        ("Sense of Magical Power", "InVi", 2, 0),
        ("Sense of Faerie Power", "InVi", 2, 0),
    ],
    "notes": paragraphs(
        "Thin and pale, fair hair unkempt, ink blotched at her mouth, chin "
        "and the earlobe she clutches in thought. Casting sigil: a tide of "
        "illusory black ink wells up her arms, further with greater spells. "
        "Voting sigil: an old knife, still sharp, from her parens.",
        "Combat: dodge Init -1, Defense -1; knife Init -1, Attack +3, "
        "Defense -1, Damage 0. Soak 0.",
        "Her writing things are her casting tools: the knife that scrapes "
        "ink for Perdo, a loaded quill for Muto. She carries charged scrolls "
        "and keeps their Lab Texts: 3 of Bind Wound (CrCo 10), 1 of Pilum of "
        "Fire (CrIg 20, Pen +20), 1 of Circular Ward Against Demons (ReVi "
        "15, Pen +20), 2 of Wreaths of Foul Smoke (CrAu 10). Each opens on "
        "the illuminated Latin trigger phrase. She has no talisman yet.",
    ),
}

ANDREW: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 2, 0, 0, 0, 0),
    "confidence": (1, 3),
    "apparent_age": 25,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flexible Formulaic Magic",
        "Apt Student",
        "Book Learner",
        "Inspirational",
        ("Social Contacts", {"group": "magi"}),
        "Free Expression",
        "Short-Ranged Magic",
        "Envied Beauty",
        "Carefree",
    ],
    "traits": {"Vain": 2, "Helpful": 1, "Charming": 1},
    "reputations": {"Arrogant poet (Stonehenge magi)": 2},
    "abilities": [
        ("Artes Liberales", 2, "rhetoric"),
        ("Athletics", 2, "running"),
        ("Awareness", 1, "alertness"),
        ("Carouse", 1, "staying sober"),
        ("Charm", 1, "first impressions"),
        ("Living Language: English", 5, "storytelling"),
        ("Etiquette", 2, "court"),
        ("Finesse", 1, "casting speed"),
        ("Folk Ken", 2, "nobles"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Magic Theory", 5, "Corpus"),
        ("Medicine", 2, "physician"),
        ("Parma Magica", 1, "Corpus"),
        ("Penetration", 1, "Corpus"),
        ("Philosophiae", 1, "natural philosophy"),
        ("Craft: Poetry", 3, "chanson de gesta"),
        ("Swim", 1, "long distances"),
    ],
    "arts": arts_from(
        "Cr 6, In 1, Mu 3, Pe 1, Re 7, An 0, Aq 0, Au 0, Co 9, He 0, Ig 0, "
        "Im 0, Me 2, Te 0, Vi 5"
    ),
    "spells": [
        ("The Severed Limb Made Whole", "CrCo", 25, 0),
        ("Physician's Eye", "InCo", 5, 0),
        ("Eyes of the Cat", "MuCo(An)", 5, 0),
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("Preternatural Growth and Shrinking", "MuCo", 15, 0),
        ("The Gift of Vigor", "ReCo", 20, 0),
        ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
        ("Wizard's Leap", "ReCo", 15, 0),
        ("Palm of Flame", "CrIg", 5, 0),
        ("Words of the Unbroken Silence", "CrMe", 10, 0),
    ],
    "notes": paragraphs(
        "Handsome, smiling and fair, with a good voice. His satchel holds "
        "torn parchments, horn cups, a bottle of wine, a blunt pen knife, and "
        "never enough ink. Casting sigil: a sparkling golden sheen that "
        "settles at random on caster, target or a bystander. Voting sigil: a "
        "polished horn cup with a silver rim.",
        "Combat: dodge Init 0, Defense 0. Soak 0. Inspirational and Free "
        "Expression each add +3 to the Aesthetic Quality of his poems "
        "(Art & Academe).",
    ),
}

OTTO: StatBlock = {
    "characteristics": characteristics(2, 0, 0, 2, 0, 0, 1, 0),
    "aging_points": {"intelligence": 1, "communication": 1, "dexterity": 1},
    "confidence": (1, 3),
    "decrepitude": (0, 3),
    "warping": (2, 11),
    "apparent_age": 47,
    "virtues_flaws": [
        "Clerk",
        "Arcane Lore",
        "Relic",
        "Warrior",
        "Well-Traveled",
        "Diabolic Past",
        "Arthritis",
        ("Weakness", {"detail": "adventure"}),
    ],
    "traits": {"Steadfast": 3, "Cynical": 2, "Compassionate": 1},
    "abilities": [
        ("Area Lore: Flanders", 2, "legends"),
        ("Artes Liberales", 3, "logic"),
        ("Athletics", 3, "climbing"),
        ("Awareness", 2, "searching"),
        ("Brawl", 2, "dodge"),
        ("Charm", 2, "being witty"),
        ("Chirurgy", 2, "binding wounds"),
        ("Church Lore", 2, "rites"),
        ("Civil and Canon Law", 2, "as applied to Flanders"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "personalities"),
        ("Dominion Lore", 3, "angels"),
        ("Living Language: English", 3, "prose"),
        ("Faerie Lore", 3, "faeries of death"),
        ("Living Language: Low German", 5, "Flemish"),
        ("Folk Ken", 4, "clergy"),
        ("Living Language: French", 3, "prose"),
        ("Dead Language: Greek", 3, "religious texts"),
        ("Dead Language: Hebrew", 3, "religious texts"),
        ("Infernal Lore", 6, "undead"),
        ("Dead Language: Latin", 5, "academic usage"),
        ("Leadership", 3, "inspiration"),
        ("Magic Lore", 4, "creatures"),
        ("Organization Lore: Order of Hermes", 1, "personalities"),
        ("Philosophiae", 4, "natural philosophy"),
        ("Single Weapon", 4, "long sword"),
        ("Theology", 3, "heresy"),
    ],
    "notes": paragraphs(
        "Rugged and tanned despite the clerk's robes, with an easy smile and "
        "a resolute brow; his armour and sword stay upstairs. He lives at "
        "Boulogne with his housekeeper, the young widow Katarine Tempête, "
        "who sometimes joins his adventures. His office is the covenant's "
        "nominal council chamber, as Normandy's custom requires, and his "
        "four books on the realms never leave it.",
        "Combat: dodge Init -1, Defense +3; long sword Init 0, Attack +10, "
        "Defense +6, Damage +6. Soak +2, in Partial Metal Reinforced Leather. "
        "Encumbrance 2.",
        "He carries a Fennel of Virtue (2 pawns of Vim), whose stroke costs "
        "him a Fatigue level to take 5 Infernal Might from a creature of "
        "Might 25 or less (Pen +35); a Clach Crubain of Virtue (1 pawn of "
        "Perdo) that gives him Lesser Immunity to Arthritis at the price of "
        "Warping; and 5 pawns of Divine Perdo vis in a birch branch an angel "
        "tore from the tree.",
    ),
}

DOLLY: StatBlock = {
    "characteristics": characteristics(2, 0, 3, 0, -1, -1, 0, 0),
    "size": -1,
    "confidence": (1, 3),
    "apparent_age": 30,
    "virtues_flaws": [
        "Merchant",
        "Entrancement",
        "Wealthy",
        ("Protection", {"detail": "Carles Magnus"}),
        ("Temporal Influence", {"detail": "coastal criminals and smugglers"}),
        ("Enemies", {"detail": "Sheriff of Southampton"}),
        ("Greater Malediction", {"detail": "plagued by Infernal entities"}),
        "Busybody",
        "Small Frame",
    ],
    "traits": {"Gregarious": 3, "Unforgiving": 2, "Determined": 1},
    "reputations": {
        "Stay on the right side of Dolly Price (thieves and rogues)": 3,
        "A thief and a rogue (Sheriff of Southampton)": 3,
    },
    "abilities": [
        ("Area Lore: Southampton", 4, "personalities"),
        ("Athletics", 2, "running"),
        ("Awareness", 3, "alertness"),
        ("Bargain", 2, "hard sell"),
        ("Brawl", 2, "dagger"),
        ("Carouse", 4, "power drinking"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "personalities"),
        ("Disguise", 2, "peasants"),
        ("Living Language: English", 5, "slang"),
        ("Entrancement", 5, "questionable commands"),
        ("Folk Ken", 3, "the opposite sex"),
        ("Living Language: French", 4, "slang"),
        ("Guile", 3, "lying to authority"),
        ("Intrigue", 3, "rumormongering"),
        ("Leadership", 4, "intimidation"),
        ("Legerdemain", 1, "picking pockets"),
        ("Organization Lore: Order of Hermes", 1, "personalities"),
        ("Profession: Tavern Owner", 4, "exotic girls"),
        ("Thrown Weapon", 3, "throwing knife"),
    ],
    "notes": paragraphs(
        "A short woman with cascading dark locks, a broad mouth and large "
        "bright eyes, who keeps the Inn on the Wharf at Southampton and "
        "plays captains against the king's men for profit. The covenant's "
        "ally, with agents along the coast; she keeps 5 pawns of Corpus vis "
        "for its magi, each a carved finger bone.",
        "Combat: dodge Init 0, Defense +2; dagger Init 0, Attack +5, Defense "
        "+3, Damage +2; throwing knife Init 0, Attack +5, Defense +4, Damage "
        "+1. Soak -1. Encumbrance 1.",
    ),
}

LASZLO: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 0, 0, 1, 2, 2),
    "confidence": (1, 3),
    "apparent_age": 30,
    "virtues_flaws": [
        "Custos",
        "Animal Ken",
        "Second Sight",
        "Warrior",
        "Well-Traveled",
        "Unbaptized",
        "Nocturnal",
        "Tainted with Evil",
    ],
    "traits": {"Loyal to Tibor": 3, "Pensive": 2, "Tenacious": 1},
    "abilities": [
        ("Animal Handling", 3, "wolves"),
        ("Animal Ken", 5, "wolves"),
        ("Brawl", 4, "dagger"),
        ("Living Language: English", 3, "slang"),
        ("Folk Ken", 2, "peasants"),
        ("Living Language: German", 2, "slang"),
        ("Hunt", 2, "wolves"),
        ("Living Language: Italian", 1, "slang"),
        ("Dead Language: Latin", 3, "Hermetic usage"),
        ("Leadership", 2, "animals"),
        ("Living Language: French", 4, "Norman"),
        ("Second Sight", 5, "illusory disguises"),
        ("Single Weapon", 3, "short sword"),
        ("Living Language: Magyar", 5, "slang"),
        ("Stealth", 2, "natural areas"),
        ("Survival", 2, "woodland"),
        ("Swim", 2, "underwater maneuvering"),
        ("Thrown Weapon", 4, "throwing knife"),
    ],
    "notes": paragraphs(
        "Mid-length white hair, long angular features, scrupulously "
        "clean-shaven, in iron ring mail under a knee-length hooded cloak "
        "that hides his daggers and throwing knives. Tibor's translator, "
        "and the man who oversees his confinement on full-moon nights.",
        "Combat: dodge Init +1, Defense +6; two daggers Init +1, Attack +9, "
        "Defense +8, Damage +3 (the left parries, +1 Defense); throwing knife "
        "Init +1, Attack +8, Defense +7, Damage +2; short sword and buckler "
        "Init +1, Attack +9, Defense +8, Damage +5. Soak +3. Encumbrance 2.",
    ),
}

FEEBLE: StatBlock = {
    "characteristics": characteristics(-1, 0, 0, -1, 0, 0, 3, 2),
    "apparent_age": 25,
    "virtues_flaws": [
        "Covenfolk",
        vf_puissant("Great Weapon"),
        "Warrior",
        ("Afflicted Tongue", {"detail": "stammer"}),
        ("Fear", {"detail": "dogs"}),
    ],
    "traits": {"Brave": 3, "Bashful": 2, "Confused": 1},
    "abilities": [
        ("Area Lore: Hampshire", 3, "taverns"),
        ("Athletics", 3, "running"),
        ("Awareness", 3, "in combat"),
        ("Brawl", 4, "bludgeon"),
        ("Carouse", 3, "drinking"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "personalities"),
        ("Living Language: English", 5, "rude words"),
        ("Etiquette", 2, "magi"),
        ("Fishing", 3, "rod and line"),
        ("Folk Ken", 1, "peasants"),
        ("Great Weapon", 5, "longspear"),
        ("Guile", 2, "avoiding duties"),
        ("Living Language: French", 4, "Norman"),
        ("Survival", 2, "for a short period"),
        ("Swim", 2, "long distances"),
    ],
    "notes": (
        "He stammers and fears dogs, buckles everything wrong, and looks for "
        "someone else to answer for him, but he is deadly with the spear and "
        "holds a task until told to stop. Long spear Init +2, Attack +14, "
        "Defense +11, Damage +7. Soak +4, in Partial Metal Scale. "
        "Encumbrance 3."
    ),
}

BULLCALF: StatBlock = {
    "characteristics": characteristics(-1, -1, 1, -1, 4, 2, 0, 0),
    "size": 1,
    "apparent_age": 30,
    "virtues_flaws": [
        "Covenfolk",
        "Berserk",
        vf_great("Strength"),
        "Large",
        "Missing Ear",
        "Uncontrollable Strength",
        "Wrathful",
    ],
    "traits": {"Brave": 3, "Angry": 1, "Dim": 1},
    "abilities": [
        ("Animal Handling", 1, "pigs"),
        ("Area Lore: Sussex", 2, "streams"),
        ("Athletics", 3, "running"),
        ("Awareness", 3, "attackers"),
        ("Brawl", 4, "kick"),
        ("Carouse", 4, "power drinking"),
        ("Organization Lore: Covenant of the Northern Seas", 2, "personalities"),
        ("Living Language: English", 5, "insults"),
        ("Great Weapon", 5, "warhammer"),
        ("Guile", 2, "apologizing"),
        ("Leadership", 3, "in combat"),
        ("Living Language: French", 3, "Norman"),
        ("Single Weapon", 3, "hammer"),
        ("Survival", 3, "hills"),
        ("Swim", 2, "diving"),
    ],
    "notes": (
        "The backbone of the turb: large, bald, broken-nosed and bearded, "
        "with an ear off, quick to anger and easily outwitted, frightening "
        "to both sides when his fury takes him. Figures with and without "
        "Berserk: warhammer Init 0, Attack +12/+14, Defense +6/+4, Damage "
        "+16. Soak +9, in Full Metal Scale. Encumbrance 0."
    ),
}

SILENCE: StatBlock = {
    "characteristics": characteristics(0, 1, -2, -2, 0, 0, 5, 3),
    "apparent_age": 26,
    "virtues_flaws": [
        "Covenfolk",
        vf_great("Dexterity"),
        vf_great("Dexterity"),
        "Covenant Upbringing",
        "Master of None",
    ],
    "traits": {"Brave": 3, "Disciplined": 2, "Self-Interest": 1, "Honorable": -1},
    "abilities": [
        ("Athletics", 4, "acrobatics"),
        ("Awareness", 3, "search"),
        ("Brawl", 3, "dagger"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "people"),
        ("Disguise", 2, "peasants"),
        ("Living Language: English", 3, "slang"),
        ("Folk Ken", 2, "grogs"),
        ("Dead Language: Latin", 2, "overheard speech"),
        ("Legerdemain", 4, "pilfering"),
        ("Living Language: French", 5, "Norman"),
        ("Stealth", 5, "urban areas"),
        ("Swim", 2, "stay afloat"),
        ("Thrown Weapon", 3, "throwing knife"),
    ],
    "notes": (
        "A fit and wiry thief, used for stealth and sleight of hand, who "
        "prefers his throwing knives and always marks the way out; he works "
        "well with Fang. Dagger Init +2, Attack +11, Defense +7, Damage +3; "
        "throwing knife Init +2, Attack +10, Defense +7, Damage +2. Soak +1. "
        "Encumbrance 1."
    ),
}

SHADOW: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 0, 2, 1, 0, 4),
    "apparent_age": 25,
    "virtues_flaws": [
        "Covenfolk",
        "Improved Characteristics",
        vf_great("Quickness"),
        "Warrior",
        "Covenant Upbringing",
        "Susceptibility to Warping",
        "Unlucky",
    ],
    "traits": {"Brave": 3, "Loyal": 3, "Overconfident": 3},
    "abilities": [
        ("Athletics", 2, "contortions"),
        ("Awareness", 5, "bodyguarding"),
        ("Brawl", 4, "dagger"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "people"),
        ("Living Language: English", 5, ""),
        ("Folk Ken", 3, "townsfolk"),
        ("Dead Language: Latin", 3, "Hermetic usage"),
        ("Leadership", 4, "intimidation"),
        ("Living Language: French", 4, "Norman"),
        ("Single Weapon", 5, "longsword"),
        ("Swim", 2, "stay afloat"),
    ],
    "notes": (
        "A serious shield grog who has vowed never willingly to leave his "
        "magus's side, and who stands between the magus and harm rather than "
        "press an advantage. Neat and polished under an iron helmet, with a "
        "shield very nearly a pavise. Longsword and rectangular shield Init "
        "+5, Attack +10, Defense +15, Damage +8. Soak +10, in Full Chain "
        "Mail. Encumbrance 1."
    ),
}

FANG: StatBlock = {
    "characteristics": characteristics(-2, 1, -1, -2, 1, 2, 3, 2),
    "apparent_age": 28,
    "virtues_flaws": [
        "Covenfolk",
        vf_puissant("Brawl"),
        "Tough",
        "Warrior",
        ("Careless with {ability}", {"ability": "Great Weapon"}),
        ("Social Handicap", {"detail": "unpleasant odor"}),
        ("Weakness", {"detail": "drinking"}),
    ],
    "traits": {"Brave": 3, "Loyal": 2, "Subtle": -2},
    "abilities": [
        ("Area Lore: Area", 2, "brewers"),
        ("Athletics", 2, "climbing"),
        ("Awareness", 3, "in combat"),
        ("Brawl", 5, "bite"),
        ("Carouse", 4, "drinking"),
        ("Charm", 3, "when drunk"),
        ("Chirurgy", 3, "cauterization"),
        ("Organization Lore: Covenant of the Northern Seas", 2, "personalities"),
        ("Living Language: English", 5, "talking about fighting"),
        ("Folk Ken", 1, "magi"),
        ("Great Weapon", 3, "long spear"),
        ("Guile", 3, "lying to magi"),
        ("Music", 2, "drinking songs"),
        ("Ride", 1, "pack horse"),
        ("Single Weapon", 5, "heater shield"),
        ("Survival", 1, "on rivers"),
        ("Swim", 2, "underwater maneuvering"),
    ],
    "notes": (
        "A bearded, hunched and reeking brawler who grapples and bites, "
        "drinks at every chance, and often forgets his axe. Bite Init +2, "
        "Attack +11, Defense +10, Damage +1; axe and heater shield Init +2, "
        "Attack +13, Defense +11, Damage +7. Soak +7. Encumbrance 1."
    ),
}

NED: StatBlock = {
    "characteristics": characteristics(-1, -1, -1, -1, 1, 4, 1, 0),
    "aging_points": {"intelligence": 1, "stamina": 2, "dexterity": 1},
    "decrepitude": (1, 2),
    "apparent_age": 45,
    "virtues_flaws": [
        "Covenfolk",
        vf_great("Stamina"),
        "Rapid Convalescence",
        "Warrior",
        "No Sense of Direction",
        "Weak Characteristics",
        ("Weakness", {"detail": "talking back to magi"}),
    ],
    "traits": {"Loyal": 3, "Cheeky": 2, "Brave": 1},
    "abilities": [
        ("Area Lore: Normandy Coast", 4, "monsters"),
        ("Area Lore: Stonehenge's Southern Coast", 2, "monsters"),
        ("Awareness", 5, "in combat"),
        ("Brawl", 3, "kick"),
        ("Carouse", 3, "with fighting friends"),
        ("Chirurgy", 5, "binding wounds"),
        ("Crossbow", 5, "crossbow"),
        ("Organization Lore: Covenant of the Northern Seas", 1, "personalities"),
        ("Living Language: English", 5, "military talk"),
        ("Folk Ken", 1, "magi"),
        ("Guile", 2, "getting extra rations"),
        ("Leadership", 3, "in combat"),
        ("Living Language: French", 3, "Norman"),
        ("Organization Lore: Order of Hermes", 3, "grogs"),
        ("Single Weapon", 7, "round shield"),
        ("Stealth", 3, "when armored"),
        ("Survival", 1, "when in a group"),
        ("Swim", 1, "staying afloat"),
        ("Thrown Weapon", 4, "knife"),
    ],
    "notes": (
        "Nearly dead three times in the service of magi, with an astounding "
        "constitution and the chirurgy he taught himself; he adds Stamina 4 "
        "and +3 from Rapid Convalescence to Wound Recovery rolls, and prefers "
        "the crossbow now, spanned with a belt hook (Lords of Men p. 138). "
        "Axe and round shield Init -2, Attack +13, Defense +10, Damage +7; "
        "crossbow Init +3, Attack +12, Defense +6, Damage +8. Soak +11. "
        "Encumbrance 4."
    ),
}

MAGI = (
    (
        "carles",
        "Carles Magnus",
        TYTALUS,
        80,
        CARLES,
        "Leader of the covenant, 80 years old, and a sailor all his life: "
        "pragmatic piracy and acquiring things for other magi made him rich "
        "and gave him a mixed name. He plans to found a Tribunal of the "
        "Northern Seas with himself as its Praeco, and means his younger "
        "magi to outgrow him and found ocean covenants of their own. He "
        "suffers Magic Addiction, so he avoids casting where a junior can, "
        "and holds the council's casting vote by age. Holds La Charytee.",
    ),
    (
        "hilde",
        "Hilde Oddfish",
        BJORNAER,
        65,
        HILDE,
        "Carles's old friend, a giant-blooded Bjornaer of Clan Maruhs who "
        "keeps to the sea because her shark heartbeast rages too fiercely to "
        "be safe ashore. She has initiated the Inner Heartbeast and still "
        "bears the scar of meeting her ancestor. The Merfolk revere her since "
        "she killed seven of a warband in shark form. Carles sometimes sends "
        "her with a junior he doubts. Holds the Marie de Bayonne.",
    ),
    (
        "columba",
        "Columba",
        EX_MISCELLANEA,
        29,
        COLUMBA,
        "Apprenticed in House Guernicus, she fled to Carles's ship the day "
        "before her Gauntlet and was accepted into Ex Miscellanea by Benedic "
        "of Oxeney in Stonehenge. Her polemic on founding a Tribunal is the "
        "covenant's legal case. Her former parens, Roman de Troyes, has "
        "never forgiven her and keeps turning up. Holds the Laurens.",
    ),
    (
        "matilda",
        "Matilda Page",
        VERDITIUS,
        30,
        MATILDA,
        "Trained in Stonehenge, she ran to sea to escape a troublesome "
        "family, drawn by the rune-carved wreck of Alfgeir's knarr. An "
        "illuminator whose devices are all script and image, she is the "
        "covenant's quartermaster. She hopes to learn Enchant Casting Tools "
        "and, in secret from her House, her own version of the Rusticani's "
        "Craft Magic. Holds the Trinite.",
    ),
    (
        "tibor",
        "Tibor Milos",
        TREMERE,
        25,
        TIBOR,
        "A new-made Tremere, placed here by his parens, a clerk at Coeris who "
        "guessed Carles's plan, to watch the covenant; he must report by "
        "mundane means for now. He is also a lycanthrope, turning body and "
        "mind to a wolf at the full moon, locked in a cage in his sanctum "
        "under Laszlo's eye. Holds Le Genet.",
    ),
    (
        "andrew",
        "Andrew of Jerbiton",
        JERBITON,
        25,
        ANDREW,
        "A dreamer who wants adventure others will fight through so that he "
        "may record it in chansons de gesta. He supports his fellows, shaping "
        "his spells as Flexible Formulaic Magic allows, is rarely prepared "
        "for the basics, and knows Matilda from Stonehenge. Holds the Black "
        "Bark.",
    ),
)

PEOPLE = (
    (
        "otto",
        "Otto-Pauels",
        "companion",
        47,
        OTTO,
        "A learned Flemish clerk at Boulogne who takes commissions into the "
        "strange and the impossible; outside the Order Carles knows few who "
        "understand the four realms so well, above all the undead.",
    ),
    (
        "dolly",
        "Dolly Price",
        "companion",
        30,
        DOLLY,
        "Keeper of the Inn on the Wharf at Southampton, ally to the covenant "
        "under Carles's protection, with the power of Entrancement.",
    ),
    (
        "laszlo",
        "Laszlo",
        "companion",
        30,
        LASZLO,
        "Tibor's custos and guardian, a loyal servant of House Tremere chosen "
        "for his uncanny way with beasts.",
    ),
    ("feeble", "Young Feeble", "grog", 25, FEEBLE, "A spearman of the turb."),
    ("bullcalf", "Bullcalf", "grog", 30, BULLCALF, "The turb's heavy fighter."),
    ("silence", "Silence", "grog", 26, SILENCE, "The turb's thief."),
    ("shadow", "Shadow", "grog", 25, SHADOW, "A shield grog."),
    ("fang", "Fang", "grog", 28, FANG, "A brawler of the turb."),
    ("ned", "Thrice-Dead Ned", "grog", 45, NED, "The turb's veteran and chirurgeon."),
)

#: name, what she is, Size, tons, quality, her captain and his Traits, words.
FLEET = (
    (
        "La Charytee",
        "Large cog",
        "Excellent",
        125,
        False,
        "Gilot Vallet, shaven-headed, robust and exacting (Exacting +3, "
        "Loyal to Carles +2, Reckless -1)",
        "A tall rear tower with a red-painted balcony; +2 to sailing. The "
        "Long Bone of Saint Epiphanius hangs from her mast.",
    ),
    (
        "Marie de Bayonne",
        "Flat-bottomed hulk",
        "Superior",
        125,
        False,
        "Taupin le Ribaut, a grey-bearded tyrant who runs a decent God-fearing "
        "ship (Merciless +3, Pious +2, Loyal to Hilde +1)",
        "+1 to sailing close to shore, but she leaks. A sea opening in Hilde's "
        "laboratory lets her swim out in shark form.",
    ),
    (
        "The Black Bark",
        "Large hulk",
        "Standard",
        125,
        False,
        "Pierre l'Englais, vibrant and clean-shaven, who loves the adventurous "
        "life (Adventurous +3, Energetic +2, Cautious -1)",
        "Her hull is painted pitch black.",
    ),
    (
        "The Laurens",
        "Large cog",
        "Standard",
        150,
        False,
        "Tiessot, a Breton who walks the ship at night and is silently in "
        "love with Columba (Thoughtful +3, In love with Columba +2, "
        "Protective of his crew +1)",
        "Wide in the beam, slower but stable in rough seas, with 25 tons more "
        "cargo than the others that could become a council chamber.",
    ),
    (
        "Le Genet",
        "Ocean-going cog",
        "Standard",
        125,
        False,
        "Susane la Fèvre, strong-willed, vocal and hard, with no qualms over "
        "piracy (Garrulous +3, Showy +1, Loyal to the Covenant -2)",
        "Patched and repaired many times. Tibor's iron cage stands in her sanctum.",
    ),
    (
        "Trinite",
        "Mediterranean nef",
        "Standard",
        125,
        True,
        "Sarrasin, a Frenchman of Moorish descent (Patient +3, Paternal to his "
        "crew +2, Respectful +1)",
        "Long-bodied with towers fore and aft, once a wreck on the seabed and "
        "a gift of the Merfolk to Carles. Her lateen sails tack close to the "
        "wind, but she takes -1 to damage checks in northern oceans. Matilda "
        "keeps a reading room in the forecastle.",
    ),
)

#: type, name, author, subject, level, quality, what it is.
LIBRARY = (
    (
        "Tractatus",
        "Journal of Unusual Encounters, volume 1",
        "Otto-Pauels",
        "Dominion Lore",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "Journal of Unusual Encounters, volume 2",
        "Otto-Pauels",
        "Faerie Lore",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "Journal of Unusual Encounters, volume 3",
        "Otto-Pauels",
        "Infernal Lore",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "Journal of Unusual Encounters, volume 4",
        "Otto-Pauels",
        "Magic Lore",
        None,
        8,
        "",
    ),
    (
        "Tractatus",
        "The Technique of Precision",
        "Culbard of Bonisagus",
        "Finesse",
        None,
        14,
        "One of two volumes; its partner, The Form of Precision, is much sought after.",
    ),
    (
        "Tractatus",
        "The Hermetic Zodiac",
        "Niall ex Miscellanea",
        "Magic Theory",
        None,
        11,
        "Tables of celestial events and how they bear on casting, in the Hibernian style.",
    ),
    (
        "Tractatus",
        "Methods for the Application of Magic Theory in Enchantment",
        "Bachalo of Verditius",
        "Magic Theory",
        None,
        10,
        "Needlessly elaborate examples of the core tenets.",
    ),
    (
        "Tractatus",
        "The Examples of the Victors",
        "Grawbadger of Tytalus",
        "Penetration",
        None,
        8,
        "Tales of the Schism War; several important pages are gone.",
    ),
    (
        "Tractatus",
        "That Which Was Shared",
        "Gurwen Ex Miscellanea",
        "Parma Magica",
        None,
        11,
        "Glossed in a mundane academic's Latin.",
    ),
    (
        "Tractatus",
        "Tenebris caeli domino",
        "Felix of Tytalus",
        "Spell Mastery: Clouds of Thunderous Might",
        None,
        9,
        "",
    ),
    (
        "Tractatus",
        "Incantatione fulmineus",
        "Felix of Tytalus",
        "Spell Mastery: The Incantation of Lightning",
        None,
        9,
        "",
    ),
    (
        "Tractatus",
        "Domito hastam Ignis",
        "Felix of Tytalus",
        "Spell Mastery: Pilum of Fire",
        None,
        9,
        "",
    ),
    (
        "Tractatus",
        "The Incredible Journey",
        "Fredrick of Münster",
        "Area Lore: The Northern Seas",
        None,
        6,
        "A primer on the ports and weather by a clerk who ran away to sea with Carles.",
    ),
    (
        "Tractatus",
        "On the Dream of Scipio",
        "Macrobius",
        "Artes Liberales",
        None,
        7,
        "Astronomy, as in Art & Academe p. 136.",
    ),
    (
        "Tractatus",
        "Foundations",
        "August Jens-Rasmus of Guernicus",
        "Code of Hermes",
        None,
        8,
        "Dry, but clearly laid out.",
    ),
    (
        "Tractatus",
        "The Authority Granted to the Tribunal by its Members",
        "Columba",
        "Code of Hermes",
        None,
        12,
        "A polemic on the legal grounds for founding a Tribunal.",
    ),
    (
        "Tractatus",
        "The Forms and Uses of Natural Shape and Materials in Magic",
        "Jean-Michel Borel of Verditius",
        "Philosophiae",
        None,
        7,
        "",
    ),
    (
        "Summa",
        "Ship's Log",
        "La Charytee's masters",
        "Profession: Sea Captain",
        2,
        6,
        "In French. La Charytee's logs, treated as Covenant Rolls (Grogs).",
    ),
    (
        "Tractatus",
        "Carta Marina",
        "La Charytee's masters",
        "Area Lore: The Northern Seas",
        None,
        6,
        "In French. Maps improved as she sails; each magus has a copy to update.",
    ),
    (
        "Summa",
        "Emanations Brought on by Hermetic Arts",
        "Breitweiser of Flambeau",
        "Creo",
        9,
        10,
        "",
    ),
    (
        "Tractatus",
        "A Hermetic Methodology for the Investigation of Occurrences",
        "Casagrande of Tremere",
        "Intellego",
        None,
        10,
        "",
    ),
    (
        "Summa",
        "The Decline of Things",
        "Plotinus of Bonisagus of Carthage",
        "Perdo",
        10,
        11,
        "Three dozen tightly wound scrolls in a large chest.",
    ),
    (
        "Summa",
        "On the Unnatural Promotion of Natural Processes",
        "Larroca of Tytalus",
        "Rego",
        11,
        11,
        "Sumptuously illuminated.",
    ),
    (
        "Summa",
        "Comparative Anatomies, volume 1",
        "Avenedus of Bjornaer",
        "Animal",
        11,
        11,
        "Its cover is inlaid with animal bone.",
    ),
    (
        "Tractatus",
        "Deluge",
        "Salvador Blanco of Flambeau",
        "Aquam",
        None,
        11,
        "One of four on the elemental Forms.",
    ),
    (
        "Summa",
        "Comparative Anatomies, volume 2",
        "Avenedus of Bjornaer",
        "Corpus",
        12,
        11,
        "Its cover is inlaid with human bone.",
    ),
    (
        "Tractatus",
        "Conflagration",
        "Salvador Blanco of Flambeau",
        "Ignem",
        None,
        11,
        "One of four on the elemental Forms.",
    ),
    (
        "Tractatus",
        "Tumult",
        "Salvador Blanco of Flambeau",
        "Terram",
        None,
        11,
        "One of four on the elemental Forms.",
    ),
    (
        "Summa",
        "A Discussion on Auras and Their Effects on Our Spells and Rituals",
        "Niall ex Miscellanea",
        "Vim",
        8,
        11,
        "Dry and full of charts.",
    ),
)
ARTS = {
    "Creo", "Intellego", "Perdo", "Rego", "Animal", "Aquam", "Corpus",
    "Ignem", "Terram", "Vim",
}  # fmt: skip

CHARTER = (
    "Membership is by accord of the existing members.",
    "A magus accepted shares his resources with the covenant and receives "
    "his share of its resources.",
    "Each magus swears hospitality to his brothers and sisters in the covenant.",
    "Each magus is master of his own vessel.",
    "Each magus has one vote at council, and the eldest holds the casting vote.",
    "Each magus is sworn for at least a decade, and may then leave with his "
    "rightful share.",
    "After twenty years a magus may take his ship and crew if he funds a replacement.",
    "After thirty years a magus may take his ship and crew with no obligation.",
    "After forty years a magus may claim a shipping route or region of the "
    "sea, is due the respect of a recognized covenant, and may charter others "
    "to himself.",
)


def build(normandy: Normandy) -> None:
    b = normandy.b
    covenant = _covenant(normandy)
    normandy.covenants["northern_seas"] = covenant
    _waters(normandy, covenant)
    people = _people(normandy, covenant)
    _fleet(b, covenant, people)
    _devices(covenant)
    _library(b, covenant)
    _vis(covenant)
    _charter(covenant)
    _ojo(b, people["carles"])
    _demon(b, covenant)


def stats(normandy: Normandy) -> None:
    b = normandy.b
    for key, _name, _kind, _age, block, _summary in (*MAGI, *PEOPLE):
        b.stats(normandy.magi[key], block, source=SOURCE)


def _waters(normandy: Normandy, covenant: Covenant) -> None:
    """The sea it opens at, whose base aura is the book's 0 (Through the
    Aegis p. 11), and Barfleur's harbour, nominally its home port (p. 11):
    Barfleur the town is no Place, and a stop names a Place."""
    b = normandy.b
    sea = b.place(
        NAME,
        summary="The seas the covenant sails, from the Rhine to Hibernia and "
        "from Iceland to Iberia. They have no pervading aura: there are "
        "auras out there, but small and widely scattered, and the magi are "
        "charting them.",
    )
    sea.details[sites.WATERS] = mobile.OPEN_WATER
    covenant.stops.append(CovenantStop(1220, "Spring", sea.id))
    harbour = b.place(
        "The harbour of Barfleur",
        inside=normandy.places["cotentin"],
        summary="The harbour of the town of Barfleur, nominally the home port "
        "of the Northern Seas.",
    )
    harbour.details[sites.WATERS] = mobile.PORT


def _covenant(normandy: Normandy) -> Covenant:
    b, tribunal = normandy.b, normandy.tribunal
    assert tribunal is not None
    covenant = b.covenant(
        NAME,
        tribunal=tribunal,
        founded=1209,
        season="Spring",
        detail=FULL,
        summary=paragraphs(
            "A flotilla of six ships working the seas from the Rhine to "
            "Hibernia and from Iceland to Iberia, its symbol a black cog at "
            "full sail on white. Each magus is master of a ship, with a "
            "captain and crew, and lives, studies and works aboard. Normandy's "
            "claim on it is tenuous: it has stayed out of Tribunal politics "
            "but is still bound by the Peripheral Code, and is expected at the "
            "Hermetic Tourney. Barfleur is its nominal home port, and Otto's "
            "office at Boulogne its nominal council chamber.",
            "Income. Trade and transport earn only 40 Mythic Pounds a year "
            "against about 133 spent, 51 of it on provisions; the stores "
            "aboard and with merchant houses (340 pounds in London, Bruges, "
            "Hamburg, Lübeck, Bergen and Riga) last four or five years. Piracy "
            "is still being debated. Loyalty is -2.",
            "At sea. With no aura and no Aegis the magi work with their ships "
            "at anchor, or trade for a season in a friendly covenant's aura, "
            "and they are charting auras and currents at sea. Their specialists "
            "stay ashore: Clovis the chaplain near St. Malo, Stephen the sail "
            "maker at Cherbourg, Hugh the carpenter, Guerrier the rope maker "
            "at Abbeville, the tax collector Shimon Avraham at Barfleur, and "
            "merchants in Antwerp, London and Paris. Each ship carries about a "
            "dozen sailors and a captain.",
        ),
        what_matters=joined_lines(
            "Build Points: 1088 (devices and laboratories 291, library and "
            "Lab Texts 408, wealth 74, specialists 155, vis 160)",
            "Boon: Mystical Allies (the Merfolk, who revere Hilde)",
            "Boon: Criminals; Difficult Access; Famous Resident (Carles Magnus); "
            "Healthy Feature (the open sea); Informants; Local Ally (Shimon "
            "Avraham, tax collector of Barfleur); Ungoverned",
            "Boon: Sailors (free choice: nearly all the covenfolk)",
            "Hook: Missing Aura; Tribunal Border (Normandy's claim is tenuous)",
            "Hook: Erratically Mobile; Gender Imbalance; Possession Victim "
            "(unsuspected); Poverty (Minor) (one Lesser Income Source, 40 "
            "pounds a year)",
            "Allies: the Merfolk; the covenant of Favonius in Thebes, also "
            "shipborne, but wedded to the Tribunals as they are; John Padbury "
            "of Verditius, a would-be Hermetic shipwright at Smallhythe",
            "Rivals: Waddenzee's pirates; Oculus Septentrionalis, itself eyeing "
            "secession, whose Estrid Danesson might yet join; Captain Folpert "
            "Berlensis of La Main Blanche, a mundane carrier of Hermetic goods",
        ),
        notes=paragraphs(
            "Story seeds. The Magical Whale: Maris of Tytalus tells of a whale "
            "that brings an aura to the surface as it breaches. The First "
            "Contract: a stowaway from Southampton to Riga, fleeing a forced "
            "marriage. The First Act of Piracy: a ship said to hold silver "
            "carries monks and relics instead. The Rusted Bars: Tibor's cage "
            "rusts through overnight. The Fall of the Mercantile Families: "
            "Waddenzee's piracy threatens those who bank the covenant's "
            "silver. The Oyster Prince: the Oyster King's heir wants Hilde's "
            "trophies back.",
            "Storylines. Exploration: Frisland and Icaria, Rupes Nigra, "
            "Estotiland, Drogeo, the Purple Islands, the far south. Lost cities: "
            "Atlantis, Tartessos. A new Tribunal: Carles means to help found "
            "three more ocean covenants, in Stonehenge, Hibernia, and the Rhine "
            "or Loch Leglean, for the twelve magi across four covenants needed "
            "to found one. The covenant is expected at Normandy's Tourney, and "
            "may be courted in the Lotharingian debate.",
            "Magestones (Guardians of the Forests p. 70) would give each "
            "laboratory an aura of 3, if any could be got. Its Tribunal can be "
            "moved to the Rhine, Provence, Stonehenge or Hibernia to suit a saga.",
            "The four younger magi suit players, Carles and Hilde the storyguide.",
        ),
    )
    return covenant


def _people(normandy: Normandy, covenant: Covenant) -> dict[str, Character]:
    b = normandy.b
    found = {}
    for key, name, house, age, _block, summary in MAGI:
        found[key] = normandy.magi[key] = b.magus(
            name, covenant=covenant, house=house, age=age, summary=summary
        )
    for key, name, kind, age, _block, summary in PEOPLE:
        found[key] = normandy.magi[key] = b.magus(
            name, covenant=covenant, house="", age=age, summary=summary, type=kind
        )
    return found


def _fleet(b: Builder, covenant: Covenant, people: dict[str, Character]) -> None:
    masters = ("carles", "hilde", "andrew", "columba", "tibor", "matilda")
    for (name, kind, quality, tons, lateen, captain, words), key in zip(FLEET, masters):
        master = people[key]
        add_possession(
            covenant,
            "ship",
            name,
            description=paragraphs(
                words, f"Master: {master.name}. Captain: {captain}."
            ),
            ship=Ship(
                kind_name=kind,
                size=8,
                tons=tons,
                crew=13,
                lateen=lateen,
                quality=quality,
                home_port="Barfleur",
            ),
        )
        if key == "carles":
            characteristics_, spec, rooms = (
                {
                    "refinement": 2,
                    "general_quality": 1,
                    "upkeep": 3,
                    "safety": 1,
                    "aesthetics": 2,
                },
                {
                    "Experimentation": 2,
                    "Longevity Rituals": 1,
                    "Intellego": 1,
                    "Animal": 1,
                },
                "Dominated by a carved, painted map of the oceans and skies on "
                "floor and ceiling, and guarded at all times. Virtues: Extensive "
                "Stores, Lesser Feature (Map), Specimens, Guard, Highly "
                "Organized, Mobile, Precious Ingredients. Flaws: Cramped, "
                "Unstable. Marker: all five other magi.",
            )
        elif key == "hilde":
            characteristics_, spec, rooms = (
                {
                    "refinement": 1,
                    "general_quality": -1,
                    "upkeep": 1,
                    "aesthetics": 1,
                },
                {"Experimentation": 2, "Animal": 1, "Aquam": 3},
                "Constantly damp, strung with fish, seaweed and driftwood, with "
                "an opening to the sea. Virtues: Mobile, Highly Organized, "
                "Lesser Feature (Running Water), Extensive Stores, Specimens. "
                "Flaws: Cramped, Lesser Focus (Running Water), Unstable. "
                "Marker: Carles Magnus.",
            )
        else:
            characteristics_, spec, rooms = (
                SHIPBOARD_LAB,
                {"Experimentation": 2},
                SHIPBOARD_WORDS,
            )
        b.laboratory(
            covenant,
            f"{master.name}'s laboratory",
            owner=master,
            characteristics=dict(characteristics_),
            specializations=spec,
            source=f"Through the Aegis p. {25 if key != 'hilde' else 26}",
            rooms={"Aboard ship": rooms},
        )


def _devices(covenant: Covenant) -> None:
    for name, words in (
        (
            "The Long Bone of Saint Epiphanius",
            "A relic of Faith Score 3 in a box at La Charytee's mast, with a "
            "Divine Might of 30 that scourges demons within 30 feet. Invoked, "
            "it lets those in the same structure understand each other's speech, "
            "Christians only (Babel Rejoined, InMe 40, Pen +8, 2 a day).",
        ),
        (
            "Brooch of Lungs of the Fish",
            "MuAq 24, constant: the wearer breathes as by Lungs of the Fish. "
            "One, with its Lab Text.",
        ),
        (
            "The Freshwater Barrel",
            "PeAq 20, 1 a day: takes the salt from seawater poured in. Carles "
            "and Hilde each have one, and the Lab Text.",
        ),
        (
            "The Master's Chart",
            "An enchanted map on which carved miniatures of each ship, each an "
            "Arcane Connection, sail to her true position (Finding the Fleet, "
            "InHe 14, and Mark the Fleet, ReHe 11, each 12 a day). Opened with "
            "eight pawns, four used. Carles's; Hilde knows of it and has the "
            "Lab Text, and Matilda suspects.",
        ),
        (
            "Bell of Summoning",
            "CrIm 30, 12 uses a day, Pen +32: rung on La Charytee, it sounds on "
            "all six ships, using six uses, so it can ring twice with effect.",
        ),
        (
            "Magical Astrolabes",
            "InVi 40, unlimited use: gives the direction of an active magical "
            "effect, not its distance, and so finds the Bell. One on each ship.",
        ),
        (
            "The Agile Shields",
            "The two halves of the Oyster King's shell, turned by The Agile "
            "Shield (MuTe 14) into kite shields of Excellent make, +3 Defense "
            "and Load 1, each holding 3 pawns of Lesser Enchantment vis.",
        ),
    ):
        add_possession(covenant, "item", name, description=words)


def _library(b: Builder, covenant: Covenant) -> None:
    for kind, name, author, subject, level, quality, words in LIBRARY:
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
            description=words,
        )


def _vis(covenant: Covenant) -> None:
    for name, art, pawns, season, words in (
        (
            "Fire From the Sky",
            "Terram",
            10,
            "Winter",
            "Fist-sized spheres of burning granite fall in a yearly hail storm "
            "over the northern seas and lose their vis if not gathered that "
            "night. Int + Artes Liberales (astrology) finds where and when.",
        ),
        (
            "The Kraken's Egg",
            "Animal",
            5,
            "Spring",
            "A giant kraken rises each spring two hundred miles south-west of "
            "La Rochelle to feed and lay one egg; taken from the sea the egg "
            "keeps its vis, left there it hatches.",
        ),
        (
            "The Summer Fog",
            "Mentem",
            5,
            "Summer",
            "On the last night of July a fog of nightmares rolls in on Sønder "
            "Vorupør (The Unbidden Horrors, CrMe 20, Pen +10). Gathered in "
            "leather bags, it gives vis and frees the village.",
        ),
        (
            "The Black Horse of Boulogne",
            "Rego",
            4,
            "Autumn",
            "A vast black stallion comes to a secret pool Otto-Pauels knows; "
            "leave it new iron shoes and it casts off the old, a pawn in each. "
            "Tainted by Faerie. A seisin of the covenant under Tribunal law.",
        ),
    ):
        add_possession(
            covenant,
            "vis_source",
            name,
            art=art,
            pawns=pawns,
            season=season,
            description=words,
        )
    for name, art, pawns, words in (
        (
            "Alfgeir's Resting Place",
            "Rego",
            20,
            "Dedicated Rego Aquam vis (RoP: Magic p. 122) in the rune-carved "
            "timbers of a sunken knarr.",
        ),
        (
            "Alfgeir's Bones",
            "Corpus",
            5,
            "Lesser Enchantment vis in his self-animating corpse, chained in "
            "La Charytee's hold (The Animated Corpse, ReCo 24). A season's "
            "taming gives it Dexterity and Single Weapon from its controller's "
            "Intelligence and Finesse.",
        ),
        (
            "The magi's shares",
            "Vim",
            90,
            "Fifteen pawns each, three of each Technique.",
        ),
    ):
        add_possession(
            covenant, "vis_store", name, art=art, pawns=pawns, description=words
        )


def _charter(covenant: Covenant) -> None:
    charter = covenant.charter_of_covenant
    charter.name = "The Charter of the Northern Seas"
    charter.preamble = (
        "Light on detail, with no degrees of membership. It implies that no "
        "right to a route or region is recognized before forty years."
    )
    charter.clauses = [
        CharterClause(number=str(number), text=text)
        for number, text in enumerate(CHARTER, 1)
    ]


def _ojo(b: Builder, carles: Character) -> None:
    ojo = b.creature(
        "Ojo",
        page="p. 12",
        realm="Magic",
        might=13,
        form="Animal",
        size=-2,
        season="Spring",
        source=SOURCE,
        block={
            "characteristics": characteristics(2, 0, -3, 0, -4, 0, 2, 2),
            "abilities": [
                ("Athletics", 5, "climbing"),
                ("Awareness", 4, "predators"),
                ("Brawl", 4, "dodge"),
                ("Finesse", 4, "using magic devices"),
                ("Living Language: French", 3, "sailing terms"),
                ("Dead Language: Latin", 3, "Hermetic"),
                ("Legerdemain", 4, "cutpurse"),
                ("Magic Lore", 4, "auras"),
                ("Magic Theory", 2, "spells"),
                ("Stealth", 3, "hiding"),
                ("Survival", 3, "foraging"),
            ],
            "traits": {
                "Cheerful at Full Moon": 3,
                "Loyal to Carles": 3,
                "Monkey": 3,
                "Mischievous": 2,
                "Brave": -2,
                "Attentive at New Moon": -3,
            },
        },
        attacks=[
            b.attack("Bite", 2, 9, 7, -3),
            b.attack("Dodge", 2, None, 8, None),
        ],
        soak=1,
        fatigue_levels="OK, 0, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Ape the Beast",
                1,
                -1,
                "Animal",
                level=25,
                does="Takes on one minor natural ability of an animal he sees, "
                "at a Might point each sunrise and sunset while he keeps it.",
            ),
            b.power(
                "Mimic the Man",
                0,
                2,
                "Imaginem",
                level=3,
                does="Copies any sound he hears, even speech.",
            ),
        ],
        appearance=(
            "A tailless Barbary macaque with a dark pink face, who wears trousers "
            "and a jacket of eastern silk."
        ),
        notes=(
            "Carles's familiar, freed from a cruel sea captain; an accomplished "
            "thief who can work magic items. Magic Animal, Magical Friend; Learn "
            "Athletics from Mistakes; Baneful Circumstances (new moon), True "
            "Friend (Carles). Gift of Speech is limited to Mimic the Man. Vis: 3 "
            "pawns of Muto in his hands. Bond: Mental Communication, both ways, "
            "unlimited; his silver cord adds to Carles's concentration rolls "
            "against Magic Addiction."
        ),
    )
    saga = b.saga
    saga.familiars.append(
        Familiar(
            id=storage.generate_unique_id("Ojo", [f.id for f in saga.familiars]),
            character_id=carles.id,
            name="Ojo",
            species="A Barbary macaque, a magical beast",
            magic_might=13,
            size=-2,
            virtues_flaws=[virtue_flaw_from_block("True Friend")],
            personality_traits=[ScoredTrait("Loyal to Carles", 3)],
            golden_cord=1,
            silver_cord=2,
            bronze_cord=1,
            characteristics=ojo.characteristics,
            base_soak=ojo.soak,
            natural_weapons=[
                Possession(
                    id=storage.generate_unique_id("Bite", []),
                    kind="weapon",
                    name="Bite",
                    weapon_init=2,
                    weapon_attack=9,
                    weapon_defense=7,
                    weapon_damage=-3,
                )
            ],
        )
    )
    b.link(carles, "creatures", ojo, "his familiar")


def _demon(b: Builder, covenant: Covenant) -> None:
    demon = b.creature(
        "Feliadexter",
        page="p. 28",
        realm="Infernal",
        might=20,
        form="Mentem",
        source=SOURCE,
        order="Tempters",
        hierarchy=0,
        weakness="Love, freely given",
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, -1, 1, 3, 3, 3, 2, 2),
            "abilities": [
                ("Brawl", 3, "whip"),
                ("Charm", 4, "chosen victim"),
                ("Folk Ken", 6, "character faults"),
                ("Guile", 6, "imaginary faults"),
            ],
            "traits": {"Selfish": 5, "Cruel": 4, "Angry": 3, "Spiteful": 3},
            "virtues_flaws": ["Weak-Willed"],
        },
        attacks=[
            b.attack("Claws", 3, 6, 5, 5),
            b.attack("Tongue", 4, 7, 7, 0),
        ],
        soak=3,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power("Possession", 0, 2, "Mentem", does="RoP: The Infernal p. 32."),
            b.power("Coagulation", 2, -1, "Corpus", does="RoP: The Infernal p. 31."),
            b.power(
                "Obsession (Cruelty)",
                1,
                -5,
                "Vim",
                does="1 to 3 points. RoP: The Infernal p. 31.",
            ),
        ],
        appearance=(
            "A spindly, bony man with rips through his skin, his head tipped back "
            "by a mouth forced open round a tongue as thick as a grog's arm, "
            "which he uses as a whip."
        ),
        notes=(
            "A demon of wrath possessing one of the crews, urging the cruel "
            "choice from the back of the crowd. Its Possession Pool of 15 stands "
            "in for its Might and isn't regained; it can pass between hosts and "
            "split off further spirits, and is safe from relics within a host. "
            "Vis: 4 pawns of Mentem vis sordida in its bowels."
        ),
        secrets=f"Aboard {NAME}, on no ship the book names. Carles suspects it.",
    )
    b.link(covenant, "creatures", demon, "among the crews")
