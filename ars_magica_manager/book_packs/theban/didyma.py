"""Didyma, the Oracles of Apollo: an Autumn covenant of the Kretan phyle,
as of 1220, in paraphrase of Through the Aegis, chapter four: the
covenant, its five magi, Alexander's apprentice and three familiars, its
companions and covenfolk, its temples, laboratories, devices, library,
Lab Texts and vis, the Sacred Way and its sphinxes, Miletos and Panormos,
and the demon asleep under the plain.

It builds after Anatolia, whose Thrakesion, Maeander, Emperor of Nicaea
and Orthodox Patriarch it links to, and finishes after the Tribunal,
whose roster of phylai and of magi it then joins. Stat blocks are the
book's; the rest is a summary, not its words."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import storage
from ...models import (
    CHARGED,
    CharterClause,
    EnchantedDevice,
    Familiar,
    InstilledEffect,
    ScoredTrait,
)
from ...models.books import TEXT_ENCHANTMENT, TEXT_SPELL
from ...models.creature import BodyVis
from ...models.holdings import Possession
from ...models.world import FULL
from ...tribunal_packages import theban as package
from ..builder import (
    Builder,
    StatBlock,
    add_possession,
    arts_from,
    characteristics,
    joined_lines,
    paragraphs,
    titled,
    vf_ability,
    vf_art,
    vf_focus,
    vf_great,
    vf_puissant,
    virtue_flaw_from_block,
)

if TYPE_CHECKING:
    from ...models import Character, Covenant, Creature, Neighbour
    from . import Theban

SOURCE = "TtA"
NAME = "Didyma"
EX_MISCELLANEA = "house_ex_miscellanea"
MERINITA = "house_merinita"
JERBITON = "house_jerbiton"
FLAMBEAU = "house_flambeau"
BRANCHIDAE = "trad_branchidae"
GREEK = "Classical Greek"

AOEDE: StatBlock = {
    "characteristics": characteristics(-2, -2, 0, -3, -5, -3, -2, -2),
    "size": -2,
    "confidence": (1, 3),
    "warping": (0, 3),
    "apparent_age": 9,
    "virtues_flaws": [
        "The Gift",
        "Apprentice",
        "Death Prophecy",
        "Branchidae Prophecy",
        "Gossip",
        "Keen Vision",
        "Luck",
        vf_art("Puissant {art}", "Intellego"),
        "Twilight Prone",
        "Weak Spontaneous Magic",
        ("Fear", {"detail": "dark"}),
    ],
    "traits": {"Shy": 3},
    "reputations": {"Apprentice of Alexander (Hermetic)": 1},
    "abilities": [
        ("Artes Liberales", 1, "astronomy"),
        ("Athletics", 1, "climbing"),
        ("Brawl", 2, "fist"),
        ("Dead Language: Classical Greek", 1, "Hermetic usage"),
        ("Guile", 2, "covenfolk"),
        ("Leadership", 1, "Branchidae family"),
        ("Living Language: Romaic Greek", 5, "Hermetic usage"),
        ("Magic Theory", 2, "inventing spells"),
        ("Organization Lore: Didyma", 1, "secrets"),
        ("Stealth", 2, "Didyma"),
    ],
    "arts": arts_from(
        "Cr 3, In 3+3, Mu 0, Pe 0, Re 0, An 3, Aq 0, Au 0, Co 2, He 0, Ig 2, "
        "Im 5, Me 0, Te 0, Vi 0"
    ),
    "spells": [
        ("Moonbeam", "CrIg", 3, 0),
        ("Phantasm of the Talking Head", "CrIm", 10, 0),
        ("Image of the Beast", "InAn", 5, 0),
        ("Prying Eyes", "InIm", 5, 0),
    ],
    "notes": paragraphs(
        "A nervous, shy nine-year-old, often hiding behind Alexander's bulk, "
        "with the -3 age penalty already in her Characteristics. Casting "
        "sigil: an A minor chord rising from the target, as loud as the "
        "spell is strong, a whisper for the first magnitude. In a simple "
        "tunic. No Twilight Scars. Encumbrance 0.",
        "Combat: fist Init +1, Attack +2, Defense +4, Damage -2. Soak -3.",
        "Her parents, Lysias of the turb and the servant Rhea, are both of "
        "the extended Branchidae family. Close to Alexander, under his "
        "shared Parma Magica, she is not usually frightened by the Gifted. "
        "Ariane fascinates her, and she loves riding on Herakles's back, "
        "though she has lately begun to pretend she is too old for it. When "
        "not studying she may invent spells in Alexander's laboratory.",
    ),
}

ALEXANDER: StatBlock = {
    "characteristics": characteristics(2, 1, -2, 2, -2, 1, -1, 1),
    "aging_points": {
        "intelligence": 2,
        "perception": 1,
        "presence": 2,
        "communication": 2,
        "strength": 1,
        "stamina": 1,
        "dexterity": 1,
        "quickness": 1,
    },
    "size": 1,
    "confidence": (1, 3),
    "decrepitude": (2, 1),
    "warping": (8, 37),
    "apparent_age": 99,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Death Prophecy",
        "Branchidae Prophecy",
        "Clear Thinker",
        ("Deft Form", {"form": "Corpus"}),
        "Good Teacher",
        "Improved Characteristics",
        "Large",
        "Method Caster",
        vf_art("Puissant {art}", "Intellego"),
        ("Temporal Influence", {"detail": "the Church, via the Metropolitan"}),
        ("True Friend", {"detail": "Mileta"}),
        ("Driven (Major)", {"detail": "continuity of the Branchidae"}),
        "Pagan (Major)",
        "Weak Spontaneous Magic",
        "Obese",
        "Proud (Minor)",
    ],
    "traits": {"Driven": 6, "Loyal (Mileta)": 3, "Proud": 3},
    "reputations": {"Branchidae patriarch (Hermetic)": 3, "Pagan priest (local)": 4},
    "abilities": [
        ("Area Lore: Miletos", 6, "history"),
        ("Artes Liberales", 2, "astronomy"),
        ("Awareness", 3, "details"),
        ("Bargain", 3, "mundanes"),
        ("Brawl", 2, "fist"),
        ("Civil and Canon Law", 3, "ancient rights"),
        ("Code of Hermes", 3, "apprentices"),
        ("Concentration", 3, "spells"),
        ("Dead Language: Classical Greek", 5, "Hermetic usage"),
        ("Dead Language: Latin", 3, "Hermetic usage"),
        ("Finesse", 3, "Creo"),
        ("Folk Ken", 3, "clergy"),
        ("Guile", 3, "pilgrims"),
        ("Intrigue", 6, "church"),
        ("Leadership", 4, "Branchidae"),
        ("Living Language: Romaic Greek", 5, "poetry"),
        ("Magic Theory", 9, "inventing spells"),
        ("Organization Lore: Byzantine Church", 3, "Miletos"),
        ("Organization Lore: Didyma", 8, "history"),
        ("Organization Lore: Order of Hermes", 4, "Theban Tribunal"),
        ("Pagan Theology", 6, "Anatolia"),
        ("Parma Magica", 6, "Mentem"),
        ("Penetration", 4, "Intellego"),
        ("Teaching", 4, "Hermetic"),
    ],
    "arts": arts_from(
        "Cr 16, In 18+3, Mu 12, Pe 10, Re 12, An 10, Aq 7, Au 9, Co 19, He 7, "
        "Ig 7, Im 9, Me 14, Te 8, Vi 18"
    ),
    "spells": [
        ("Opening the Tome of the Animal's Mind", "InAn", 25, 0),
        ("Voice of the Lake", "InAq", 25, 0),
        ("Enchantment of the Scrying Pool", "InAq", 30, 0),
        ("Sailor's Foretaste of the Morrow", "InAu", 20, 0),
        ("Gentle Touch of the Purified Body", "CrCo", 20, 0),
        ("Purification of the Festering Wounds", "CrCo", 20, 0),
        ("Cheating the Reaper", "CrCo", 30, 0),
        ("Incantation of the Body Made Whole", "CrCo", 40, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("Sight of the True Form", "InCo", 20, 0),
        ("The Inexorable Search", "InCo", 20, 0),
        ("The Eye of the Sage", "InCo(Im)", 30, 0),
        ("Cloak of Black Feathers", "MuCo(An)", 30, 0),
        ("The Leap of Homecoming", "ReCo", 35, 0),
        ("Converse with Plant and Tree", "InHe", 25, 0),
        ("Shadows of the Fires Past", "InIg", 15, 0),
        ("Vision of Heat's Light", "InIg", 20, 0),
        ("Phantasm of the Talking Head", "CrIm", 10, 0),
        ("Aura of the Ennobled Presence", "MuIm", 10, 0),
        ("Peering into the Mortal Mind", "InMe", 30, 0),
        ("Past of Another", "MuMe", 35, 0),
        ("Scent of Peaceful Slumber", "ReMe", 20, 0),
        ("Numbness of the Gift", "InVi", 20, 0),
        ("Piercing the Faerie Veil", "InVi", 20, 0),
        ("Wizard's Communion", "MuVi", 10, 0),
        ("Wizard's Vigil", "MuVi", 40, 0),
        ("Demon's Eternal Oblivion", "PeVi", 10, 0),
        ("End of the Titans", "PeVi", 10, 0),
        ("Faerie Bane", "PeVi", 10, 0),
        ("Unraveling the Fabric of Animal", "PeVi", 15, 0),
        ("Unraveling the Fabric of Aquam", "PeVi", 15, 0),
        ("Unraveling the Fabric of Auram", "PeVi", 15, 0),
        ("Unraveling the Fabric of Corpus", "PeVi", 15, 0),
        ("Unraveling the Fabric of Herbam", "PeVi", 15, 0),
        ("Unraveling the Fabric of Ignem", "PeVi", 15, 0),
        ("Unraveling the Fabric of Imaginem", "PeVi", 15, 0),
        ("Unraveling the Fabric of Mentem", "PeVi", 15, 0),
        ("Unraveling the Fabric of Terram", "PeVi", 15, 0),
        ("Unraveling the Fabric of Vim", "PeVi", 15, 0),
        ("Circular Ward Against Demons", "ReVi", 25, 0),
        ("Aegis of the Hearth", "ReVi", 25, 0),
    ],
    "notes": paragraphs(
        "A huge, bearded, obese old man in a white hooded toga, who seldom "
        "leaves the Temple of Apollo. Twilight scars: those within earshot "
        "feel a deep throbbing hum, and a faint coloured nimbus some two "
        "paces across shows his mood. Casting sigil: the sphere, in every "
        "effect's shape or trappings. Voting sigil: a foot-wide bronze disk "
        "stamped with the Eye of the Branchidae. Patriarch and Librarian of "
        "the covenant. Longevity Ritual -8, Bronze Cord -2. Encumbrance 0.",
        "Combat: fist Init +1, Attack +2, Defense +4, Damage -2. Soak +3 "
        "(Stamina and Bronze Cord).",
        "General spells at the levels printed: Sight of the True Form 20, "
        "Wizard's Communion 10, Wizard's Vigil 40 (as a Communion of 30), "
        "Demon's Eternal Oblivion 10, Circular Ward Against Demons 25, Aegis "
        "of the Hearth 25. End of the Titans and Faerie Bane are the Magic "
        "and Faerie equivalents of Demon's Eternal Oblivion. Printed casting "
        "totals include +3 for Method Caster, without talisman attunements.",
    ),
}

NIKOLA: StatBlock = {
    "characteristics": characteristics(2, 2, 1, 0, 1, 1, -1, 1),
    "aging_points": {
        "intelligence": 1,
        "perception": 1,
        "presence": 1,
        "strength": 1,
        "stamina": 1,
        "quickness": 1,
    },
    "confidence": (2, 5),
    "decrepitude": (1, 2),
    "warping": (7, 3),
    "apparent_age": 78,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Death Prophecy",
        "Branchidae Prophecy",
        "Educated",
        "Hermetic Prestige",
        "Improved Characteristics",
        vf_art("Puissant {art}", "Rego"),
        vf_art("Puissant {art}", "Intellego"),
        "Self-Confident",
        "Warrior",
        "Pagan (Major)",
        "Study Requirement",
        "Weak Spontaneous Magic",
        "Depressed",
    ],
    "traits": {"Sad": 3, "Loyal": 3},
    "reputations": {"Tribunal arche (Hermetic)": 4, "Pagan priest (local)": 4},
    "abilities": [
        ("Area Lore: Miletos", 2, "personalities"),
        ("Artes Liberales", 2, "logic"),
        ("Awareness", 4, "military"),
        ("Bargain", 2, "pilgrims"),
        ("Brawl", 2, "fist"),
        ("Civil and Canon Law", 2, "ancient rights"),
        ("Code of Hermes", 3, "procedures"),
        ("Concentration", 3, "spells"),
        ("Dead Language: Classical Greek", 5, "Hermetic usage"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Finesse", 3, "items"),
        ("Folk Ken", 2, "Branchidae"),
        ("Guile", 4, "Alexander"),
        ("Intrigue", 4, "Branchidae"),
        ("Leadership", 5, "Branchidae"),
        ("Living Language: Romaic Greek", 5, "dialects"),
        ("Magic Theory", 6, "lab refinement"),
        ("Organization Lore: Didyma", 5, "turb"),
        ("Organization Lore: Order of Hermes", 6, "Theban Tribunal"),
        ("Pagan Theology", 3, "Anatolia"),
        ("Parma Magica", 6, "Vim"),
        ("Penetration", 4, "Intellego"),
        ("Single Weapon", 6, "sword"),
        ("Stealth", 2, "temples"),
        ("Teaching", 2, "Hermetic"),
    ],
    "arts": arts_from(
        "Cr 9, In 12+3, Mu 8, Pe 12, Re 18+3, An 9, Aq 6, Au 8, Co 10, He 6, "
        "Ig 5, Im 6, Me 7, Te 8, Vi 20"
    ),
    "spells": [
        ("Opening the Tome of the Animal's Mind", "InAn", 25, 0),
        ("Doublet of Impenetrable Silk", "MuAn", 15, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Purification of the Festering Wounds", "CrCo", 20, 0),
        ("The Chirurgeon's Healing Touch", "CrCo", 20, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("Seven-League Stride", "ReCo", 30, 0),
        ("Tales of the Ashes", "InIg", 5, 0),
        ("The Ear for Distant Voices", "InIm", 20, 0),
        ("Wizard's Sidestep (Touch, Group)", "ReIm", 25, 0),
        ("Posing the Silent Question", "InMe", 20, 0),
        ("Tracks of the Faerie Glow", "InTe", 25, 0),
        ("Unseen Arm", "ReTe", 5, 0),
        ("Sense of Magical Power", "InVi", 2, 0),
        ("Piercing the Faerie Veil", "InVi", 20, 0),
        ("Piercing the Magic Veil", "InVi", 20, 0),
        ("Numbness of the Gift", "InVi", 20, 0),
        ("The Invisible Eye Revealed", "InVi", 20, 0),
        ("Sense of the Lingering Magic", "InVi", 30, 0),
        ("Wizard's Communion", "MuVi", 20, 0),
        ("Wizard's Vigil", "MuVi", 40, 0),
        ("Aegis of the Hearth", "ReVi", 40, 0),
        ("Maintaining the Demanding Spell", "ReVi", 15, 0),
        ("The Spell Persists", "ReVi", 35, 0),
    ],
    "notes": paragraphs(
        "Tall and white-haired with a long face, in a brown hooded stola. "
        "Twilight scars: eyes fixed and blank as those painted on a "
        "sarcophagus, though she sees well, and brown blood mildly acid as "
        "lemon juice, which hurts nobody. Casting sigil: a faint echo exactly "
        "one diameter behind her casting, of her voice or of the effect, with "
        "fainter echoes open to InVi study of sigils. Voting sigil: the "
        "Strategos' sword. Longevity Ritual -5. Encumbrance 0.",
        "Combat: fist Init +1, Attack +2, Defense +4, Damage +1; Strategos' "
        "sword Init +3, Attack +10, Defense +9, Damage +7. Soak +1.",
        "General spells at the levels printed: The Invisible Eye Revealed "
        "20, Wizard's Communion 20, Wizard's Vigil 40, Maintaining the "
        "Demanding Spell 15. She knows Aegis of the Hearth at levels 25 and "
        "40: she casts the covenant's at 40, usually with the others helping "
        "by Wizard's Communion for Penetration, and at 25 when they cannot. "
        "The Spell Persists keeps up a spell of level 30 or less for Sun.",
        "Covenant Strategos; an arche of the Kretan phyle on the Council of "
        "Magistrates, sitting on the Treasury Council as a tutor who finds "
        "Gifted children. Her Study Requirement needs large specimen "
        "collections, at present animal bones, and at least a season to "
        "exchange them. She lives in her laboratory with her husband and "
        "servant Alexios.",
    ),
}

HERAKLES: StatBlock = {
    "characteristics": characteristics(0, -1, 1, -2, 5, 4, 2, 1),
    "aging_points": {"strength": 1},
    "size": 2,
    "confidence": (1, 3),
    "decrepitude": (0, 1),
    "warping": (5, 8),
    "apparent_age": 56,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Giant Blood",
        ("Strong Faerie Blood", {"blood": "Sidhe"}),
        "Faerie Magic",
        vf_great("Strength"),
        "Improved Characteristics",
        "Improved Characteristics",
        "Tough",
        "Proud (Major)",
        ("Deficient Technique", {"technique": "Muto"}),
        "Pagan (Major)",
        "Reckless (Minor)",
    ],
    "traits": {"Proud": 6, "Reckless": 3},
    "reputations": {"The Demigod Hercules (local)": 5},
    "abilities": [
        ("Area Lore: Miletos", 3, "Didyma"),
        ("Artes Liberales", 2, "astronomy"),
        ("Athletics", 3, "jumping"),
        ("Awareness", 3, "ambush"),
        ("Bargain", 4, "spells"),
        ("Brawl", 6, "fist"),
        ("Carouse", 1, "drinking"),
        ("Code of Hermes", 1, "faeries"),
        ("Concentration", 2, "spells"),
        ("Dead Language: Classical Greek", 3, "Hermetic usage"),
        ("Etiquette", 1, "Hermetic"),
        ("Faerie Lore", 4, "monsters"),
        ("Faerie Magic", 2, "vis use"),
        ("Finesse", 1, "Terram"),
        ("Folk Ken", 1, "covenfolk"),
        ("Guile", 2, "faeries"),
        ("Hunt", 3, "monsters"),
        ("Intrigue", 2, "Hermetic"),
        ("Leadership", 1, "faeries"),
        ("Living Language: Romaic Greek", 5, "Hermetic usage"),
        ("Magic Theory", 4, "inventing spells"),
        ("Organization Lore: Didyma", 2, "Merinita"),
        ("Organization Lore: House Merinita", 3, "pagan gods"),
        ("Organization Lore: Order of Hermes", 2, "Thebes Tribunal"),
        ("Parma Magica", 4, "Vim"),
        ("Penetration", 4, "Vim"),
        ("Second Sight", 5, "faeries"),
        ("Single Weapon", 5, "club"),
        ("Swim", 2, "sea"),
    ],
    "arts": arts_from(
        "Cr 8, In 9, Mu 7, Pe 8, Re 9, An 6, Aq 7, Au 7, Co 8, He 5, Ig 6, "
        "Im 5, Me 5, Te 8, Vi 9"
    ),
    "spells": [
        ("Blunt the Viper's Fangs", "PeAn", 15, 0),
        ("Jupiter's Resounding Blow", "CrAu", 10, 0),
        ("Bind Wound (Size +1)", "CrCo", 15, 0),
        ("Footsteps on the Sacred Way", "InCo", 10, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("Preternatural Growth and Shrinking (Personal, Size +1)", "MuCo", 15, 0),
        ("Traitor's Coin", "PeCo", 15, 0),
        ("Gift of the Frog's Legs (Size +1)", "ReCo", 20, 0),
        ("Shriek of the Impending Shafts", "InHe", 15, 0),
        ("Palm of Flame", "CrIg", 5, 0),
        ("Fist of Shattering", "PeTe", 10, 0),
        ("Broken Word Broken Sword", "PeTe", 20, 0),
        ("Unseen Arm", "ReTe", 5, 0),
        ("Sword Ward", "ReTe", 20, 0),
        ("Wizard's Communion", "MuVi", 20, 0),
        ("Wizard's Vigil", "MuVi", 20, 0),
        ("Piercing the Faerie Veil", "InVi", 20, 0),
        ("Demon's Eternal Oblivion", "PeVi", 5, 0),
        ("End of the Titans", "PeVi", 5, 0),
        ("Faerie Bane", "PeVi", 5, 0),
        ("Disenchant", "PeVi", 15, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "notes": paragraphs(
        "A giant strong-man in a lion-skin cloak, with a round shield and "
        "his club, who gives out that he is Zeus's son and his namesake come "
        "again. Twilight scar: a booming voice, Loud reaching 60 paces and "
        "Firm 30; he cannot speak Quiet, though No Voice works as usual. "
        "Casting sigil: heat, the air warming a degree or more by the "
        "effect's strength. Voting sigil: an old Greek silver coin, the "
        "Sacred Spring on one side and Zeus's head on the other. Longevity "
        "Ritual -4. Encumbrance 0 (1).",
        "Combat: fist Init +1, Attack +9, Defense +8, Damage +5; club and "
        "shield Init +2, Attack +12, Defense +12, Damage +8. Soak +7.",
        "General spells at the levels printed: Wizard's Communion 20, "
        "Wizard's Vigil 20, Demon's Eternal Oblivion 5, Disenchant 15, "
        "Gather the Essence of the Beast 15. Deficient Technique halves his "
        "Muto casting totals after the die and the aura.",
        "Herakles's club, by his account carved by Zeus from an ancient oak, "
        "is no magic item but an Excellent one (City & Guild p. 69): Single "
        "Weapon, Init +1, Attack +4, Defense +3, Damage +3, Strength 0, Load "
        "1. He sometimes goes about disguised, by Disguise of the New Visage "
        "and Preternatural Growth and Shrinking, most often as an ancient "
        "crone; his Gift is as plain as ever, but no one knows him. He holds "
        "Lana's effects, and William of Normandy is his guest.",
    ),
}

ARIANE: StatBlock = {
    "characteristics": characteristics(2, 2, 1, 1, -1, 2, 0, 0),
    "aging_points": {"strength": 1},
    "confidence": (1, 3),
    "decrepitude": (0, 1),
    "warping": (4, 7),
    "apparent_age": 39,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        vf_focus("Major Magical Focus", "teleportation"),
        "Arcane Lore",
        "Clear Thinker",
        "Educated",
        "Improved Characteristics",
        "Privileged Upbringing",
        ("Temporal Influence", {"detail": "imperial eunuchs"}),
        ("True Friend", {"detail": "Chloris"}),
        "Pagan (Major)",
        ("Restriction", {"detail": "cannot cast when seen by unGifted humans"}),
        ("Ability Block", {"abilities": "Martial"}),
        ("Fear", {"detail": "Franks"}),
        "Reclusive",
    ],
    "traits": {"Reclusive": 3},
    "reputations": {
        "Pagan priestess (Hermetic)": 1,
        "Pagan priestess (local)": 2,
    },
    "abilities": [
        ("Area Lore: Constantinople", 2, "scholars"),
        ("Area Lore: Miletos", 2, "Didyma"),
        ("Artes Liberales", 2, "astronomy"),
        ("Awareness", 3, "being watched"),
        ("Charm", 2, "scholars"),
        ("Civil and Canon Law", 1, "imperial"),
        ("Code of Hermes", 2, "mundane interference"),
        ("Concentration", 2, "spells"),
        ("Dead Language: Classical Greek", 5, "Hermetic usage"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Etiquette", 2, "Byzantine court"),
        ("Finesse", 2, "spells"),
        ("Folk Ken", 2, "pagans"),
        ("Guile", 2, "magi"),
        ("Intrigue", 3, "Byzantine and Nicaean court"),
        ("Living Language: Romaic Greek", 5, "rituals"),
        ("Magic Theory", 5, "vis use"),
        ("Medicine", 2, "diseases"),
        ("Organization Lore: Didyma", 3, "vis sources"),
        ("Organization Lore: Order of Hermes", 2, "Theban Tribunal"),
        ("Pagan Theology", 2, "Apollo"),
        ("Parma Magica", 3, "Vim"),
        ("Penetration", 4, "Vim"),
        ("Philosophiae", 2, "pagan"),
        ("Stealth", 2, "urban"),
    ],
    "arts": arts_from(
        "Cr 6, In 9, Mu 5, Pe 5, Re 10, An 5, Aq 5, Au 5, Co 14, He 5, Ig 5, "
        "Im 5, Me 6, Te 6, Vi 8"
    ),
    "spells": [
        ("Sense of the Lodestone", "InCo", 5, 0),
        ("Step Sideways", "ReCo", 15, 0),
        ("Ward Against People", "ReCo", 30, 0),
        ("The Leap of Homecoming", "ReCo", 35, 0),
        ("Seven League Travel Circle", "ReCo", 35, 0),
        ("Chill Touch of Exposure", "PeIg", 5, 0),
        ("Palm of Hearing", "InIm", 10, 0),
        ("Palm of Seeing", "InIm", 15, 0),
        ("Palm of Speaking", "CrMe", 5, 0),
        ("Wizard's Communion", "MuVi", 20, 0),
        ("Wizard's Vigil", "MuVi", 20, 0),
        ("Maintaining the Demanding Spell", "ReVi", 15, 0),
        ("Opening the Intangible Tunnel", "ReVi", 15, 0),
        ("Aegis of the Hearth", "ReVi", 25, 0),
    ],
    "notes": paragraphs(
        "Slender and attractive, in a thin white hooded stola, the "
        "covenant's Chancellor. Twilight scar: she seems able to live on "
        "air, with +3 to Deprivation rolls for food and -3 for air. Casting "
        "sigil: a yellow-green fog that puffs from her or her target. Voting "
        "sigil: a coin-sized gold locket holding a copy of the icon of St. "
        "Loukia, patron of Xylinites. Longevity Ritual -4, Bronze Cord -2. "
        "Encumbrance 0.",
        "Combat: fist Init 0, Attack 0, Defense 0, Damage -1. Soak +4 "
        "(Stamina and Bronze Cord).",
        "General spells at the levels printed: Wizard's Communion 20, "
        "Wizard's Vigil 20, Maintaining the Demanding Spell 15, Opening the "
        "Intangible Tunnel 15, Aegis of the Hearth 25. Her Palm spells, Sense "
        "of the Lodestone and Chill Touch of Exposure are learned to cast "
        "down an Intangible Tunnel. The Focus is in the printed totals of "
        "Step Sideways, The Leap of Homecoming and Seven League Travel Circle.",
        "A wealthy Constantinople merchant's daughter, schooled among the "
        "eunuchs of Xylinites, then still Jerbiton. The fall killed her "
        "father and her parens Theoderic, and she fled to Miletos with one "
        "of her father's trading partners. Former classmates, now powerful "
        "in the exiled court at Nicaea, still write to her. Her Restriction "
        "fails if the unGifted close their eyes or look away, but a hidden "
        "watcher stops her; beasts and beings of other realms do not count. "
        "She is married to the turb leader Sebasten, who lives apart and "
        "often visits her bed. She wishes William would go home.",
    ),
}

WILLIAM: StatBlock = {
    "characteristics": characteristics(0, 2, 1, 0, 1, 1, 1, 2),
    "aging_points": {
        "perception": 2,
        "presence": 1,
        "strength": 1,
        "stamina": 1,
        "dexterity": 1,
        "quickness": 2,
    },
    "confidence": (2, 5),
    "decrepitude": (1, 3),
    "warping": (4, 21),
    "apparent_age": 54,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Gentle Gift",
        "Improved Characteristics",
        ("True Friend", {"detail": "Torvus"}),
        vf_art("Puissant {art}", "Perdo"),
        "Quiet Magic",
        "Quiet Magic",
        "Self-Confident",
        "Subtle Magic",
        "Warrior",
        "Well-Traveled",
        ("Ambitious (Major)", {"detail": "greatest monster slayer"}),
        "Difficult Longevity Ritual",
        "Difficult Underlings",
        ("Vow (Minor)", {"detail": "never to kill a man"}),
    ],
    "traits": {"Ambitious": 6, "Brave": 3},
    "reputations": {"Monster Slayer (Hermetic)": 2},
    "abilities": [
        ("Animal Handling", 1, "horse"),
        ("Area Lore: Constantinople", 1, "crusaders"),
        ("Area Lore: Miletos", 2, "creatures"),
        ("Area Lore: Normandy", 3, "nobles"),
        ("Artes Liberales", 1, "astronomy"),
        ("Athletics", 2, "running"),
        ("Awareness", 4, "creatures"),
        ("Bows", 3, "short bow"),
        ("Brawl", 2, "fist"),
        ("Code of Hermes", 1, "vis rights"),
        ("Concentration", 3, "spells"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Etiquette", 1, "nobles"),
        ("Finesse", 2, "items"),
        ("Folk Ken", 2, "nobles"),
        ("Great Weapon", 4, "pole axe"),
        ("Guile", 1, "fast talk"),
        ("Hunt", 4, "mythic creatures"),
        ("Leadership", 5, "combat"),
        ("Living Language: Low German", 2, "military usage"),
        ("Living Language: French", 5, "Norman"),
        ("Living Language: Romaic Greek", 2, "Hermetic usage"),
        ("Magic Lore", 3, "creature weaknesses"),
        ("Magic Theory", 4, "items"),
        ("Organization Lore: Order of Hermes", 2, "monster hunters"),
        ("Parma Magica", 6, "Corpus"),
        ("Penetration", 3, "Vim"),
        ("Ride", 3, "horse"),
        ("Single Weapon", 5, "long sword"),
        ("Stealth", 2, "sneaking"),
        ("Swim", 2, "river"),
    ],
    "arts": arts_from(
        "Cr 7, In 6, Mu 8, Pe 7+3, Re 7, An 6, Aq 5, Au 5, Co 17, He 6, Ig 7, "
        "Im 5, Me 5, Te 7, Vi 7"
    ),
    "spells": [
        ("Image of the Beast", "InAn", 5, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Purification of the Festering Wounds", "CrCo", 20, 0),
        ("The Chirurgeon's Healing Touch", "CrCo", 20, 0),
        ("Eyes of the Cat", "MuCo(An)", 5, 0),
        ("Gift of the Bear's Fortitude", "MuCo", 25, 0),
        ("Grip of the Choking Hand", "PeCo", 25, 0),
        ("Blade of the Virulent Flame", "CrIg", 15, 0),
        ("Quell the Scent", "PeIm", 10, 0),
        ("Words of the Unbroken Silence", "CrMe", 10, 0),
        ("Wizard's Vigil", "MuVi", 20, 0),
        ("Demon's Eternal Oblivion", "PeVi", 5, 0),
        ("End of the Titans", "PeVi", 5, 0),
        ("Faerie Bane", "PeVi", 5, 0),
        ("Personal Ward Against Demons", "ReVi", 10, 0),
        ("Personal Ward Against Faeries", "ReVi", 10, 0),
        ("Personal Ward Against Magic Creatures", "ReVi", 10, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "notes": paragraphs(
        "A Latin knight of Ramius's school, of the Normandy Tribunal, with "
        "wild red hair. Twilight scars: one blue eye, one brown, and hair "
        "crackling with static, flashes of it showing in the dark. Casting "
        "sigil: a showy, harmless discharge of electricity. Voting sigil: a "
        "falcon's feather of silver. Longevity Ritual -2, Bronze Cord -2. "
        "Encumbrance 3 (4).",
        "Combat: fist Init +2, Attack +4, Defense +5, Damage +1; long sword "
        "and shield Init +4, Attack +11, Defense +11, Damage +7; lance and "
        "shield, mounted, Init +4, Attack +13, Defense +12, Damage +6, with "
        "the +3 mounted bonus; pole-axe Init +3, Attack +11, Defense +7, "
        "Damage +12; short bow Init +1, Attack +8, Defense +6, Damage +7. "
        "Soak +13 (Stamina, armour and Bronze Cord).",
        "He has long sword, round shield, pole-axe, lance, short bow and "
        "arrows, breastplate and mail with a helm, and carries only what he "
        "is using; the rest rides on his warhorse Lambert.",
        "General spells at the levels printed: Wizard's Vigil 20, Demon's "
        "Eternal Oblivion 5, Gather the Essence of the Beast 15. The three "
        "Personal Wards are Touch, Sun.",
        "He came east behind the crusaders of 1204, and since that siege "
        "has sworn never again to kill a human. A metoikos of the Tribunal, "
        "guest of Herakles since 1210, he may vote but hold no Tribunal "
        "office, though the covenant's charter counts him a full resident. "
        "He leads four Frankish mercenaries, with whom he and Herakles hunt "
        "faeries on the Sacred Way and Typhon's brood in the mountains. "
        "Unmarried; his soldiers quietly joke about how close he and "
        "Herakles are. Most of his private Lab Texts are back in Normandy.",
    ),
}

PHILIP: StatBlock = {
    "characteristics": characteristics(-1, -1, 1, 1, 1, 2, 2, 2),
    "size": 1,
    "confidence": (1, 3),
    "warping": (0, 3),
    "apparent_age": 31,
    "virtues_flaws": [
        "Custos",
        vf_ability("Affinity with {ability}", "Single Weapon"),
        ("Faerie Blood", {"blood": "Goblin"}),
        "Improved Characteristics",
        "Inspirational",
        "Large",
        vf_puissant("Leadership"),
        ("Driven (Major)", {"detail": "dedicated to the turb"}),
        "Curse of Venus",
        "Temperate",
    ],
    "traits": {"Driven": 6},
    "reputations": {"Didyma leader (local)": 2},
    "abilities": [
        ("Area Lore: Miletos", 3, "Didyma"),
        ("Athletics", 2, "jumping"),
        ("Awareness", 3, "weakness"),
        ("Bows", 5, "short bow"),
        ("Brawl", 2, "fist"),
        ("Carouse", 2, "legends"),
        ("Faerie Lore", 2, "goblins"),
        ("Leadership", 4, "combat"),
        ("Living Language: Romaic Greek", 5, "slang"),
        ("Organization Lore: Didyma", 2, "defenses"),
        ("Single Weapon", 7, "sword"),
        ("Stealth", 4, "ambush"),
        ("Swim", 2, "sea"),
        ("Teaching", 2, "martial"),
    ],
    "notes": paragraphs(
        "Tall, lanky and imposing, with tight black curls and a full beard "
        "flecked with early grey, and surprisingly stealthy for his size. In "
        "mail and helm with longsword, round shield, short bow and quiver. "
        "Encumbrance 2 (4). Printed Leadership 4+2 and Stealth 4+1.",
        "Combat: fist Init +2, Attack +5, Defense +5, Damage +1; longsword "
        "and shield Init +4, Attack +14, Defense +13, Damage +7; short bow "
        "Init +1, Attack +11, Defense +8, Damage +7. Soak +11.",
        "One of the two turb captains and an arche. His grandfather Zotikos "
        "was a faerie goblin in Nicodemus's service, and he is an unGifted "
        "Branchidae. He is grave and bound up in the turb, and the "
        "covenant's women keep trying to draw him off; his reserve only "
        "spurs them on.",
    ),
}

CALLISTA: StatBlock = {
    "characteristics": characteristics(1, 1, 2, 1, 0, 0, 0, 1),
    "confidence": (1, 3),
    "warping": (1, 4),
    "apparent_age": 38,
    "virtues_flaws": [
        "Custos",
        ("Ways of the {land}", {"land": "Town"}),
        "Clear Thinker",
        "Intuition",
        ("Social Contacts", {"group": "Miletos officials"}),
        "Temporal Influence",
        "Compassionate (Major)",
        "Pagan (Major)",
        ("Ability Block", {"abilities": "Martial"}),
        "Generous (Minor)",
    ],
    "traits": {"Kind": 6},
    "reputations": {
        "Representative of Didyma (local)": 4,
        "Practicing pagan (local)": 2,
        "Generous (local)": 1,
    },
    "abilities": [
        ("Area Lore: Miletos", 5, "merchants"),
        ("Artes Liberales", 1, "mathematics"),
        ("Awareness", 2, "quality"),
        ("Bargain", 4, "merchants"),
        ("Charm", 3, "merchants"),
        ("Dead Language: Classical Greek", 3, "Hermetic usage"),
        ("Dead Language: Latin", 2, "Hermetic usage"),
        ("Etiquette", 3, "Miletos"),
        ("Folk Ken", 4, "merchants"),
        ("Guile", 3, "merchants"),
        ("Intrigue", 2, "merchants"),
        ("Leadership", 5, "covenfolk"),
        ("Living Language: Romaic Greek", 5, "trade"),
        ("Magic Theory", 1, "items"),
        ("Organization Lore: Didyma", 4, "business dealings"),
        ("Organization Lore: Order of Hermes", 2, "Theban Tribunal"),
        ("Profession: Merchant", 4, "logistics"),
    ],
    "notes": paragraphs(
        "A tall woman whose long curled black hair is slowly going grey, "
        "with her agenda and warehouse log books. Her Ability Block comes of "
        "Warping. Encumbrance 0.",
        "Combat: fist Init 0, Attack 0, Defense +1, Damage 0. Soak 0.",
        "An arche, she lives in the Delphinion with her husband Cleon, two "
        "teenage children and six servants, and deals for the magi with the "
        "city's officials and merchants. Her open paganism worries parts of "
        "the city but raises her standing as the prophets' voice. She "
        "carries the Warning Flame and uses the Spice Wand.",
    ),
}

ELLA: StatBlock = {
    "characteristics": characteristics(1, 2, 1, 2, 0, 0, 1, 1),
    "aging_points": {"perception": 1, "communication": 1, "quickness": 1},
    "confidence": (1, 3),
    "decrepitude": (0, 3),
    "warping": (1, 6),
    "apparent_age": 43,
    "virtues_flaws": [
        "Custos",
        "Improved Characteristics",
        "Intuition",
        "Lightning Reflexes",
        "Premonitions",
        ("Protection", {"protector": "Apollo Didyma"}),
        "Second Sight",
        "Tough",
        ("Greater Malediction", {"detail": "vis addicted"}),
        "Envious (Major)",
        ("Fear", {"detail": "snakes"}),
        ("Oversensitive (Minor)", {"detail": "accusations of free-loading"}),
        "Visions",
    ],
    "traits": {"Envious": 6},
    "reputations": {"Oracle (local)": 3},
    "abilities": [
        ("Area Lore: Miletos", 3, "Didyma"),
        ("Athletics", 2, "running"),
        ("Awareness", 3, "movement"),
        ("Brawl", 4, "dodge"),
        ("Charm", 3, "pagans"),
        ("Etiquette", 2, "Didyma"),
        ("Faerie Lore", 3, "Olympians"),
        ("Folk Ken", 4, "covenfolk"),
        ("Guile", 4, "covenfolk"),
        ("Intrigue", 4, "Didyma"),
        ("Leadership", 2, "covenfolk"),
        ("Living Language: Romaic Greek", 5, "archaic"),
        ("Organization Lore: Didyma", 4, "history"),
        ("Organization Lore: Order of Hermes", 1, "future"),
        ("Premonitions", 7, "Didyma"),
        ("Second Sight", 7, "faeries"),
    ],
    "notes": paragraphs(
        "A pampered woman in middle age in a priestess's hooded stola, her "
        "scalp shaved to show off a shapely head. Her fear of snakes comes "
        "of Warping. Encumbrance 0.",
        "Combat: dodge Init +1, Defense +6. Soak +3.",
        "Honoured by the covenfolk and given no other work, she bristles at "
        "any whisper of free-loading and talks up her duties, and she "
        "watches Julia warily. Her Malediction: oracle work has addicted "
        "her to vis, and she suffers Deprivation (check each month) unless "
        "she takes it; the Fatigue is Long-Term, and only a pawn of vis "
        "restores it.",
    ),
}

MAGARETHE: StatBlock = {
    "characteristics": characteristics(1, 1, 0, 1, -2, -1, 1, -1),
    "aging_points": {"perception": 1, "strength": 2, "stamina": 1, "quickness": 1},
    "decrepitude": (2, 0),
    "warping": (4, 3),
    "apparent_age": 60,
    "virtues_flaws": [
        "Custos",
        "Common Sense",
        "Premonitions",
        "Blind",
        "Incomprehensible",
        ("Offensive to {being}", {"being": "animals"}),
    ],
    "traits": {"Loyal": 3},
    "reputations": {"Wise Custos (local)": 3},
    "abilities": [
        ("Area Lore: Constantinople", 4, "secrets"),
        ("Area Lore: Miletos", 3, "Didyma"),
        ("Awareness", 6, "hearing"),
        ("Charm", 4, "men"),
        ("Dead Language: Latin", 2, "Hermetic usage"),
        ("Etiquette", 3, "Hermetic"),
        ("Folk Ken", 5, "magi"),
        ("Guile", 4, "magi"),
        ("Intrigue", 6, "covenant"),
        ("Leadership", 4, "covenfolk"),
        ("Living Language: French", 1, "Norman"),
        ("Living Language: Romaic Greek", 5, "cursing"),
        ("Music", 3, "singing"),
        ("Organization Lore: Didyma", 4, "relationships"),
        ("Premonitions", 7, "Ariane"),
        ("Profession: Servant", 5, "Ariane"),
        ("Stealth", 3, "urban"),
        ("Teaching", 2, "covenfolk"),
    ],
    "notes": paragraphs(
        "Old, bent by her years yet agile, in a plain robe. Incomprehensible "
        "and Offensive to Animals come of Warping, the fruit of a lifetime "
        "among magi. Encumbrance 0.",
        "Combat: fist Init -1, Attack +1, Defense -1, Damage -2. Soak -1.",
        "Her eyes were burnt out at Constantinople thirty-five years ago so "
        "she might serve Ariane, whom she followed here. Respected by the "
        "covenfolk, she is archon: the longest serving arche and their "
        "voice and vote on the Council of Magi.",
    ),
}

MARCEL: StatBlock = {
    "characteristics": characteristics(0, 2, 0, -2, 1, 2, 2, 2),
    "aging_points": {
        "perception": 1,
        "communication": 1,
        "stamina": 1,
        "dexterity": 1,
        "quickness": 2,
    },
    "decrepitude": (1, 1),
    "warping": (3, 13),
    "apparent_age": 46,
    "virtues_flaws": [
        "Covenfolk",
        "Improved Characteristics",
        "Warrior",
        "Infamous",
        "Motion Sickness",
        "Reckless (Minor)",
        "Oversensitive (Minor)",
    ],
    "traits": {"Brave": 3, "Reckless": 3, "Loyal": 3},
    "reputations": {"Troublesome Frank (local)": 4},
    "abilities": [
        ("Animal Handling", 3, "horse"),
        ("Area Lore: Constantinople", 1, "crusaders"),
        ("Area Lore: Miletos", 3, "prostitutes"),
        ("Area Lore: Normandy", 3, "bandits"),
        ("Athletics", 3, "running"),
        ("Awareness", 4, "battlefield"),
        ("Bows", 3, "short bow"),
        ("Brawl", 5, "fist"),
        ("Carouse", 2, "debates"),
        ("Charm", 2, "women"),
        ("Chirurgy", 2, "battlefield wounds"),
        ("Etiquette", 1, "military"),
        ("Folk Ken", 3, "soldiers"),
        ("Guile", 3, "superiors"),
        ("Hunt", 4, "tracking"),
        ("Leadership", 2, "combat"),
        ("Living Language: Low German", 2, "military usage"),
        ("Living Language: French", 5, "Norman"),
        ("Living Language: Romaic Greek", 1, "slang"),
        ("Magic Lore", 2, "monsters"),
        ("Ride", 4, "horse"),
        ("Single Weapon", 6, "long sword"),
        ("Stealth", 2, "sneaking"),
        ("Survival", 3, "foraging"),
        ("Swim", 2, "river"),
    ],
    "notes": paragraphs(
        "A hardy Frankish warrior in full chain mail and helm, with long "
        "sword, round shield, lance, short bow and warhorse. Motion Sickness "
        "and Reckless come of Warping. Encumbrance 2 (3).",
        "Combat: fist Init +2, Attack +8, Defense +8, Damage +1; long sword "
        "and shield Init +4, Attack +13, Defense +12, Damage +7; lance and "
        "shield, mounted, Init +4, Attack +15, Defense +13, Damage +6, with "
        "the +3 mounted bonus; short bow Init +1, Attack +9, Defense +6, "
        "Damage +7. Soak +11.",
        "Years in Hermetic service against demons, giants and serpents have "
        "left little to surprise him, and he is very touchy about any hint "
        "of cowardice. Thomas, Alain and Guy are much like him. He lives at "
        "the covenant with his wife Lyra, a goat farmer's lovely young "
        "daughter from an hour's walk away, though they share little speech.",
    ),
}

NIKETAS: StatBlock = {
    "characteristics": characteristics(2, 1, 2, 3, -1, -1, 0, -2),
    "aging_points": {
        "intelligence": 2,
        "presence": 2,
        "communication": 3,
        "strength": 1,
        "stamina": 1,
        "quickness": 2,
    },
    "confidence": (1, 3),
    "decrepitude": (2, 4),
    "warping": (3, 5),
    "apparent_age": 85,
    "virtues_flaws": [
        "Senior Clergy",
        "Educated",
        "Improved Characteristics",
        "Relic",
        "Temporal Influence",
        "Commanding Aura",
        "Crippled",
        "Favors",
        ("Ambitious (Minor)", {"detail": "church politician"}),
    ],
    "traits": {"Ambitious": 3, "Wise": 1},
    "reputations": {
        "Elderly politician and metropolitan of Miletos (local and ecclesiastical)": 4
    },
    "abilities": [
        ("Area Lore: Constantinople", 1, "churches"),
        ("Area Lore: Miletos", 5, "churches"),
        ("Artes Liberales", 3, "logic"),
        ("Awareness", 3, "miracles"),
        ("Bargain", 5, "benefices"),
        ("Charm", 2, "monks"),
        ("Civil and Canon Law", 6, "Greek church"),
        ("Concentration", 4, "prayer"),
        ("Dead Language: Classical Greek", 5, "church use"),
        ("Dead Language: Latin", 5, "church use"),
        ("Etiquette", 4, "church"),
        ("Folk Ken", 4, "clergy"),
        ("Guile", 3, "clergy"),
        ("Intrigue", 5, "church"),
        ("Leadership", 8, "clergy"),
        ("Living Language: Frankish", 1, "crusader use"),
        ("Living Language: Romaic Greek", 5, "written"),
        ("Magic Lore", 1, "magi"),
        ("Music", 3, "hymns"),
        ("Organization Lore: Church", 7, "Miletos diocese"),
        ("Philosophiae", 4, "ancient"),
        ("Teaching", 4, "clergy"),
        ("Theology", 7, "schism"),
    ],
    "notes": paragraphs(
        "An old cripple lost in coarse clerical robes, with crosier and "
        "pallium. He can crawl but not walk, so he sits on his throne in the "
        "episcopal palace or is carried by two strong young monks. Faith "
        "Points 3, +1 from his relic. Longevity Ritual -4. Encumbrance 0.",
        "Combat: dodge Init -2, Defense -2. Soak +1 (Stamina and Commanding Aura).",
        "Commanding Aura: like Aura of Rightful Authority at Voice Range, "
        "free and with no Penetration, plus Magic Resistance 10 and +2 "
        "Soak. Saint Nikephoros' Journey: 3 Faith Points, Init +2, Corpus, "
        "like The Leap of Homecoming, a power of the relic, a fragment of "
        "bone set in his archbishop's ring, of Faith Score 1, which brings "
        "his Magic Resistance to 20.",
        "Once a monk, pious and ambitious, Metropolitan of Miletos since "
        "1172. He respects the magi's skill with the supernatural, and he "
        "and Alexander are old friends who write often.",
    ),
}

BASIL: StatBlock = {
    "characteristics": {"communication": 2},
    "abilities": [
        ("Artes Liberales", 6, "astronomy"),
        ("Dead Language: Classical Greek", 5, "Hermetic usage"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Living Language: Arabic", 4, "trade"),
        ("Philosophiae", 4, "pagan"),
        ("Profession: Scribe", 5, "Hermetic works"),
        ("Teaching", 5, "Dead Language: Classical Greek"),
    ],
    "notes": (
        "A teacher, worth 12 Build Points. Learned and elderly, the oldest "
        "of the covenant who is no magus, an arche and a scribe."
    ),
}

ABBAS: StatBlock = {
    "characteristics": {"communication": 0},
    "abilities": [
        ("Craft: Stonemason", 6, "temples"),
        ("Teaching", 2, "apprentices"),
    ],
    "notes": (
        "A teacher, worth 8 Build Points: a strongman and master mason who "
        "runs the repairs, with three young apprentices (Craft: Stonemason "
        "4, temples; 12 Build Points together), each indentured for ten "
        "years and free then to stay or find work in Miletos."
    ),
}

CLEON: StatBlock = {
    "abilities": [
        ("Civil and Canon Law", 5, "taxation"),
        ("Intrigue", 6, "officialdom"),
    ],
    "notes": (
        "A specialist, worth 6 Build Points: a kommerkiarios of Miletos, "
        "honest and careful with the seals, if incurious about goods that "
        "already bear a colleague's. He goes out once a year to assess the "
        "covenant's tax, a tenth of the oracle fees."
    ),
}

#: key, name, House, age, block, summary, hidden.
MAGI = (
    (
        "alexander",
        "Alexander",
        EX_MISCELLANEA,
        129,
        ALEXANDER,
        "Fourth Patriarch of Didyma and head of the Branchidae family, at "
        "its head since Jason was given up for lost in 1132. His schemes "
        "have made the covenant secure with its neighbours. He rarely leaves "
        "the temples, and his laboratory stands within Apollo's.",
        [
            titled(
                "Alexander's prophecy",
                "Alexander is prophesied to be slain by his apprentice. He has "
                "two left living, Nikola and Aoede.",
            ),
            titled(
                "How Alexander kept the title",
                "Though the title was barely his, Alexander kept the older "
                "Tessa and Damen from Didyma, by the wards cast with Lana.",
            ),
            titled(
                "Alexander and Niketas",
                "Alexander magically fixed Niketas's election in 1172 and made "
                "him a Longevity Ritual.",
            ),
            titled("Storyguide Notes", "Alexander has a Death Prophecy."),
        ],
    ),
    (
        "nikola",
        "Nikola",
        EX_MISCELLANEA,
        90,
        NIKOLA,
        "Strategos of the covenant, Alexander's filia and his heir as "
        "Matriarch, a stateswoman who writes to Tribunal officers and "
        "Redcaps without end and loves to talk Tribunal business. Her "
        "daughters Lydia and Cora drowned in 1205, and she blames Herakles; "
        "she married Alexios soon after.",
        [
            titled(
                "Nikola's prophecy",
                "Nikola is prophesied to die on a full moon.",
            ),
            titled(
                "Nikola's marriage",
                "Alexios has come to think Nikola married him only to escape "
                "her grief, though he denies with a brittle smile that it is "
                "anything but a love match.",
            ),
            titled(
                "Waiting for Alexander",
                "Nikola has waited all her life for Alexander to die and knows "
                "nothing of the wards unless he tells her.",
            ),
            titled("Storyguide Notes", "Nikola has a Death Prophecy."),
        ],
    ),
    (
        "herakles",
        "Herakles",
        MERINITA,
        60,
        HERAKLES,
        "A giant-blooded magus who appeared as a small boy on the Sacred "
        "Way in 1165 claiming Zeus as his father, and was apprenticed to "
        "Nicodemus. Miletos takes him for the demigod, and he believes it, "
        "and flings himself at any peril to prove it. In 1205 he brought a "
        "dozen sea-monsters' heads to Panormos.",
        "",
    ),
    (
        "ariane",
        "Ariane",
        JERBITON,
        46,
        ARIANE,
        "Chancellor of the covenant, a refugee from Constantinople's fall "
        "who came in 1205 and has since turned pagan. She keeps to a "
        "draped temple with her blind maidens, watches the covenant's "
        "interests through Intangible Tunnels and her cat, and is kind to "
        "those who trouble to know her, but fearful of Latin magi.",
        [
            titled(
                "Ariane and William",
                "Ariane suspects William took part in the sack of "
                "Constantinople, and fears him for it.",
            ),
            titled(
                "Ariane's leaning",
                "Ariane leans towards the Children of Olympos.",
            ),
        ],
    ),
    (
        "william",
        "William of Normandy",
        FLAMBEAU,
        55,
        WILLIAM,
        "A Norman knight-magus of the Gentle Gift, liked by mundanes in "
        "spite of his strange looks, who means to be the greatest slayer of "
        "monsters there has been. He hunts with Herakles.",
        [
            titled(
                "William at Constantinople",
                "William claims he took no direct part in the siege of Constantinople.",
            ),
        ],
    ),
)

#: key, name, type, age, block, summary, hidden.
PEOPLE = (
    (
        "philip",
        "Philip",
        "companion",
        31,
        PHILIP,
        "A turb captain and arche, well liked.",
        "",
    ),
    (
        "callista",
        "Callista",
        "companion",
        38,
        CALLISTA,
        "The covenant's representative in Miletos, and an arche.",
        "",
    ),
    (
        "ella",
        "Ella the Oracle",
        "companion",
        44,
        ELLA,
        "The oracle of Didyma, who drinks the draught and speaks the vision.",
        "",
    ),
    (
        "niketas",
        "Niketas II of Miletos",
        "companion",
        88,
        NIKETAS,
        "Metropolitan of Miletos and the covenant's ally, a tie few know "
        "of, even at the covenant.",
        [
            titled(
                "What Niketas owes Alexander",
                "Niketas owes Alexander his election and his long life, and in "
                "return discourages hard questions about the paganism at "
                "Didyma.",
            ),
            titled(
                "Niketas's illness",
                "Niketas convalesced a season in the baths after an illness in 1194.",
            ),
        ],
    ),
    (
        "magarethe",
        "Magarethe",
        "grog",
        60,
        MAGARETHE,
        "Ariane's oldest servant, archon of the Council of Archai.",
        "",
    ),
    (
        "marcel",
        "Marcel the Mercenary",
        "grog",
        46,
        MARCEL,
        "The Frankish mercenary who stands for his band of four.",
        "",
    ),
)

#: name, type, summary: the people the book names with no stat block.
HOUSEHOLD = (
    (
        "Sebasten",
        "grog",
        "Turb captain, arche and Ariane's husband, who visits her often but "
        "lives apart. The Grizzled Veteran (ArM5 p. 21) serves for him.",
    ),
    (
        "Alexios",
        "grog",
        "Nikola's husband and servant, 43, who lives in her laboratory and "
        "is neither Lydia's nor Cora's father.",
    ),
    (
        "Julia",
        "grog",
        "A younger woman with visions who sometimes serves as oracle, to "
        "Ella's jealous unease.",
    ),
    (
        "Nicola",
        "grog",
        "One of Ariane's blind maidens, blinded as a young girl soon after "
        "Ariane came 16 years ago, to leave her free to cast.",
    ),
    (
        "Eleni",
        "grog",
        "One of Ariane's blind maidens, blinded as a young girl soon after "
        "Ariane came 16 years ago, to leave her free to cast.",
    ),
    ("Thomas", "grog", "A Frankish mercenary of William's, much like Marcel."),
    ("Alain", "grog", "A Frankish mercenary of William's, much like Marcel."),
    ("Guy", "grog", "A Frankish mercenary of William's, much like Marcel."),
    ("Lyra", "grog", "Marcel's young wife, a goat farmer's daughter."),
    ("Lysias", "grog", "Of the turb, and Aoede's father."),
    ("Rhea", "grog", "A covenant servant, and Aoede's mother."),
)

#: name, kind, author, subject, level, quality, language, words.
LIBRARY = (
    (
        "The Law of Hermes",
        "Summa",
        "Cletus",
        "Code of Hermes",
        3,
        10,
        GREEK,
        "",
    ),
    (
        "A Bestiary of Anatolia",
        "Summa",
        "Hector",
        "Magic Lore",
        3,
        9,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "On Hermetic Theory",
        "Summa",
        "Alexander",
        "Magic Theory",
        3,
        14,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "A Directory of Enchantments",
        "Summa",
        "Hector",
        "Magic Theory",
        5,
        12,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "The Art of Making",
        "Tractatus",
        "Orion",
        "Magic Theory",
        None,
        8,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Defenses Against Creatures",
        "Summa",
        "William",
        "Parma Magica",
        2,
        9,
        "Latin",
        "Original to Didyma.",
    ),
    (
        "Upon Opposition",
        "Tractatus",
        "Jason",
        "Parma Magica",
        None,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Breaching the Parma",
        "Summa",
        "Anonymous",
        "Penetration",
        3,
        10,
        GREEK,
        "",
    ),
    (
        "Upon the Efficacy of Magic",
        "Tractatus",
        "Alexander",
        "Penetration",
        None,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "An Ancient History of Miletos",
        "Tractatus",
        "Jason",
        "Area Lore: Miletos",
        None,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    ("Elementia", "Summa", "Euclid", "Artes Liberales", 4, 9, GREEK, ""),
    ("Mechanica", "Tractatus", "Heron", "Artes Liberales", None, 7, GREEK, ""),
    ("Categories", "Tractatus", "Aristotle", "Artes Liberales", None, 10, "Latin", ""),
    ("Categories", "Tractatus", "Aristotle", "Artes Liberales", None, 12, GREEK, ""),
    ("Digest", "Summa", "Justinian", "Civil and Canon Law", 5, 7, GREEK, ""),
    (
        "Fated Lives",
        "Tractatus",
        "Alexander",
        "Dead Language: Classical Greek",
        None,
        11,
        GREEK,
        "Original to Didyma, on poetry.",
    ),
    ("al-Hawi", "Summa", "al-Razi", "Medicine", 4, 10, "Arabic", ""),
    (
        "Rites at Didyma",
        "Summa",
        "Nikola",
        "Organization Lore: Didyma",
        2,
        9,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "The Life of Branchos",
        "Tractatus",
        "Soteria",
        "Organization Lore: Didyma",
        None,
        8,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Secrets of the Sacred Way",
        "Summa",
        "Orion",
        "Organization Lore: House Merinita",
        3,
        9,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "The Hermetic Order",
        "Tractatus",
        "Cletus",
        "Organization Lore: Order of Hermes",
        None,
        9,
        GREEK,
        "",
    ),
    (
        "Forge Mysteries",
        "Tractatus",
        "Orion",
        "Organization Lore: House Verditius",
        None,
        8,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Book of Apollo",
        "Summa",
        "Branchos",
        "Pagan Theology",
        9,
        7,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Paths to Olympos",
        "Tractatus",
        "Alexander",
        "Pagan Theology",
        None,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    ("Metaphysics II", "Tractatus", "Aristotle", "Pagan Theology", None, 12, GREEK, ""),
    ("Metaphysics I", "Tractatus", "Aristotle", "Philosophiae", None, 12, GREEK, ""),
    ("Metaphysics III", "Tractatus", "Aristotle", "Philosophiae", None, 12, GREEK, ""),
    (
        "Spontaneous Creation",
        "Summa",
        "Jason",
        "Creo",
        6,
        12,
        GREEK,
        "Original to Didyma.",
    ),
    ("Genesis Magica", "Summa", "Yannis", "Creo", 15, 12, GREEK, ""),
    ("Things that Are", "Tractatus", "Meda", "Creo", None, 9, GREEK, ""),
    ("Creation with Magic", "Tractatus", "Isidoros", "Creo", None, 10, GREEK, ""),
    (
        "The Art of Knowing",
        "Summa",
        "Alexander",
        "Intellego",
        5,
        14,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "That Which is Unseen",
        "Summa",
        "Soteria",
        "Intellego",
        10,
        9,
        GREEK,
        "Original to Didyma.",
    ),
    ("The Knowledge of Thoth", "Summa", "Tessa", "Intellego", 10, 12, GREEK, ""),
    (
        "Oracle Prophecies",
        "Summa",
        "Soteria",
        "Intellego",
        18,
        10,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Seeing the Truth",
        "Tractatus",
        "Nikola",
        "Intellego",
        None,
        6,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Supposition in the Absence of Evidence",
        "Tractatus",
        "Cora",
        "Intellego",
        None,
        7,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Speaking to the Flame",
        "Tractatus",
        "Nicodemus",
        "Intellego",
        None,
        8,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "A Short Study on Intellego",
        "Tractatus",
        "Pompius",
        "Intellego",
        None,
        9,
        "Latin",
        "",
    ),
    ("Metamorphosis", "Summa", "Lykos", "Muto", 7, 13, GREEK, ""),
    ("A Study of Simple Changes", "Tractatus", "Agathe", "Muto", None, 9, GREEK, ""),
    (
        "Last Light",
        "Summa",
        "Nicodemus",
        "Perdo",
        14,
        8,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Meditations on the Void",
        "Tractatus",
        "Egnatius",
        "Perdo",
        None,
        9,
        "Latin",
        "",
    ),
    ("The Great Undoing", "Tractatus", "Thanos", "Perdo", None, 9, "Latin", ""),
    (
        "Book of Control",
        "Summa",
        "Damen",
        "Rego",
        7,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "Ties of Blood",
        "Summa",
        "Lana",
        "Rego",
        13,
        11,
        GREEK,
        "Original to Didyma.",
    ),
    ("Words of Command", "Tractatus", "Diodorus", "Rego", None, 8, GREEK, ""),
    ("Binding Spirits", "Tractatus", "Methodius", "Rego", None, 8, GREEK, ""),
    ("Powers of the Pharaoh", "Tractatus", "Kleopatra", "Rego", None, 9, GREEK, ""),
    ("A Compendium of Animal Magic", "Summa", "Pelagia", "Animal", 6, 14, GREEK, ""),
    ("Creature Magic", "Tractatus", "Herodotus", "Animal", None, 8, GREEK, ""),
    (
        "Studies in Animal Impulse",
        "Tractatus",
        "Domitilla",
        "Animal",
        None,
        9,
        "Latin",
        "",
    ),
    ("A Study of Aquam", "Tractatus", "Hypatia", "Aquam", None, 8, GREEK, ""),
    ("Spirits of the Air", "Tractatus", "Otho", "Auram", None, 9, "Latin", ""),
    ("The Art of Corpus", "Summa", "Nerva", "Corpus", 5, 15, "Latin", ""),
    (
        "The Principles of the Body",
        "Summa",
        "Jason",
        "Corpus",
        8,
        15,
        GREEK,
        "Original to Didyma.",
    ),
    ("Mastery of the Body", "Summa", "Anonymous", "Corpus", 18, 9, GREEK, ""),
    (
        "Bodies in Extremes",
        "Tractatus",
        "Ariane",
        "Corpus",
        None,
        7,
        GREEK,
        "Original to Didyma.",
    ),
    (
        "On Variations of the Longevity Ritual",
        "Tractatus",
        "Anonymous",
        "Corpus",
        None,
        9,
        GREEK,
        "",
    ),
    (
        "Notes on the Hermetic Theory of Corpus",
        "Tractatus",
        "Manlius",
        "Corpus",
        None,
        10,
        "Latin",
        "",
    ),
    (
        "On the Hidden Soul of Trees",
        "Tractatus",
        "Alba",
        "Herbam",
        None,
        8,
        "Latin",
        "",
    ),
    ("The Olive is the Key", "Tractatus", "Anonymous", "Herbam", None, 10, GREEK, ""),
    (
        "Prometheus' Gift",
        "Summa",
        "Nicodemus",
        "Ignem",
        5,
        13,
        GREEK,
        "Original to Didyma.",
    ),
    ("The Secret Fire", "Tractatus", "Nonus", "Ignem", None, 8, "Latin", ""),
    ("Deception with Magic", "Summa", "Myrrine", "Imaginem", 6, 13, GREEK, ""),
    ("Greater Deception", "Summa", "Myrrine", "Imaginem", 12, 15, GREEK, ""),
    ("Amazing Illusions", "Tractatus", "Pantaleon", "Imaginem", None, 9, GREEK, ""),
    (
        "Book of Thought",
        "Summa",
        "Damen",
        "Mentem",
        5,
        12,
        GREEK,
        "Original to Didyma.",
    ),
    ("An Open Mind", "Summa", "Anthea", "Mentem", 10, 11, GREEK, ""),
    (
        "Toward a Theory of Mind",
        "Tractatus",
        "Damen",
        "Mentem",
        None,
        9,
        GREEK,
        "Original to Didyma.",
    ),
    ("On the Shape of the Land", "Summa", "Onesimos", "Terram", 8, 12, GREEK, ""),
    ("On Surfaces", "Tractatus", "Nikandros", "Terram", None, 9, GREEK, ""),
    ("Places of Power", "Summa", "Methodius", "Vim", 5, 15, GREEK, ""),
    (
        "Studies of The Gift",
        "Summa",
        "Bonisagus",
        "Vim",
        12,
        9,
        GREEK,
        "A translation, perhaps not genuine.",
    ),
    (
        "Ancient Magics",
        "Summa",
        "Thoth",
        "Vim",
        19,
        7,
        GREEK,
        "A very poor translation of an original now lost.",
    ),
    (
        "Power from the Gods",
        "Tractatus",
        "Tessa",
        "Vim",
        None,
        9,
        GREEK,
        "Original to Didyma.",
    ),
)
ARTS = {
    "Creo", "Intellego", "Muto", "Perdo", "Rego", "Animal", "Aquam", "Auram",
    "Corpus", "Herbam", "Ignem", "Imaginem", "Mentem", "Terram", "Vim",
}  # fmt: skip

#: Spell Lab Texts in the library: name, Technique, Form, level.
LAB_TEXTS = (
    ("Opening the Tome of the Animal's Mind", "Intellego", "Animal", 25),
    ("Enchantment of the Scrying Pool", "Intellego", "Aquam", 30),
    ("Bind Wound", "Creo", "Corpus", 10),
    ("Purification of the Festering Wounds", "Creo", "Corpus", 20),
    ("The Chirurgeon's Healing Touch", "Creo", "Corpus", 20),
    ("Cheating the Reaper", "Creo", "Corpus", 30),
    ("Incantation of the Body Made Whole", "Creo", "Corpus", 40),
    ("The Eye of the Sage", "Intellego", "Corpus", 30),
    ("Whispers Through the Black Gate", "Intellego", "Corpus", 15),
    ("Disguise of the New Visage", "Muto", "Corpus", 15),
    (
        "Preternatural Growth and Shrinking (Personal, Size +1)",
        "Muto",
        "Corpus",
        15,
    ),
    ("Cloak of Black Feathers", "Muto", "Corpus", 30),
    ("Seven-League Stride", "Rego", "Corpus", 30),
    ("Ward Against People", "Rego", "Corpus", 30),
    ("The Leap of Homecoming", "Rego", "Corpus", 35),
    ("Seven League Travel Circle", "Rego", "Corpus", 35),
    ("Phantasm of the Talking Head", "Creo", "Imaginem", 10),
    ("The Ear for Distant Voices", "Intellego", "Imaginem", 20),
    ("Wizard's Sidestep (Touch, Group)", "Rego", "Imaginem", 25),
    ("Posing the Silent Question", "Intellego", "Mentem", 20),
    ("Past of Another", "Muto", "Mentem", 35),
    ("Tracks of the Faerie Glow", "Intellego", "Terram", 25),
    ("Unseen Arm", "Rego", "Terram", 5),
    ("Sword Ward", "Rego", "Terram", 20),
    ("Numbness of the Gift", "Intellego", "Vim", 20),
    ("Piercing the Faerie Veil", "Intellego", "Vim", 20),
    ("Piercing the Magic Veil", "Intellego", "Vim", 20),
    ("Wizard's Communion", "Muto", "Vim", 10),
    ("Wizard's Communion", "Muto", "Vim", 20),
    ("Wizard's Communion", "Muto", "Vim", 35),
    ("Wizard's Vigil", "Muto", "Vim", 20),
    ("Wizard's Vigil", "Muto", "Vim", 40),
    ("Demon's Eternal Oblivion", "Perdo", "Vim", 5),
    ("Demon's Eternal Oblivion", "Perdo", "Vim", 10),
    ("End of the Titans", "Perdo", "Vim", 5),
    ("End of the Titans", "Perdo", "Vim", 10),
    ("Faerie Bane", "Perdo", "Vim", 5),
    ("Faerie Bane", "Perdo", "Vim", 10),
    ("Disenchant", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Animal", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Aquam", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Auram", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Corpus", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Herbam", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Ignem", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Imaginem", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Mentem", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Terram", "Perdo", "Vim", 15),
    ("Unraveling the Fabric of Vim", "Perdo", "Vim", 15),
    ("Gather the Essence of the Beast", "Rego", "Vim", 15),
    ("Maintaining the Demanding Spell", "Rego", "Vim", 15),
    ("Aegis of the Hearth", "Rego", "Vim", 25),
    ("Aegis of the Hearth", "Rego", "Vim", 40),
)

CHARTER = (
    "The Patriarch or Matriarch is the most senior resident Gifted Branchidae.",
    "All resident magi meet as a Council of Magi at the winter and summer "
    "solstices. A magus becomes resident by a majority vote there or by "
    "taking his Gauntlet under a resident. The Patriarch may revoke "
    "residency at any time, and a magus away for more than five solstices "
    "running has resigned residency and every office.",
    "The Patriarch may call an extraordinary Council on a Moon's notice or more.",
    "Each resident owes a season's service a year, approved by the "
    "Patriarch, or else pays 3 pawns of Vim vis to the coffers. Service may "
    "be put off, but not past the next Tribunal meeting.",
    "At the Council before each Tribunal meeting the Patriarch must lay "
    "before it a prophecy for the covenant.",
    "The Patriarch names a resident Chancellor, who gathers and keeps the "
    "coffers. She may trade vis with resident and visiting magi if the "
    "coffers end no fewer in pawns; the Patriarch and Strategos may "
    "requisition vis; she reports on the coffers to the Council.",
    "The Patriarch names a resident Strategos to answer for all defenses, "
    "with the Aegis of the Hearth, whose tokens only the Strategos may "
    "give. The Strategos nominally leads and trains the turb, a task Nikola "
    "has handed to able servants.",
    "The Patriarch names a resident Librarian, who keeps and copies books "
    "and Lab Texts, settles disputes over access, and finds and trains the "
    "scriptorium's scribes.",
    "The covenfolk rule themselves through a Council of Archai, elected by "
    "them for staggered five-year terms; the longest serving, the archon, "
    "speaks for them at the Council of Magi.",
    "Decisions go by majority. Each resident magus and each office has a "
    "vote; there are no proxies, so a voter must be present.",
)

CALLISTA_WAND = "Carried by Callista at Miletos."


def build(theban: Theban) -> None:
    b = theban.b
    places = _places(theban)
    covenant = _covenant(theban, places["didyma"])
    theban.covenants["didyma"] = covenant
    people = _people(theban, covenant)
    world = _world(theban, places, people)
    _links(theban, covenant, places, world)
    _labs(b, covenant, people)
    _library(b, covenant)
    _lab_texts(b, covenant)
    _devices(b, covenant, people)
    _property(covenant)
    _vis(covenant)
    _charter(covenant)
    _history(b, covenant)
    _familiars(b, people)
    _creatures(b, covenant, places)


def stats(theban: Theban) -> None:
    b = theban.b
    for key, _name, _kind, _age, block, _summary, _hidden in (*MAGI, *PEOPLE):
        b.stats(theban.magi[key], block, source=SOURCE)
    b.stats(_FOUND["aoede"], AOEDE, source=SOURCE)
    b.stats(_FOUND["basil"], BASIL, source=SOURCE)
    b.stats(_FOUND["abbas"], ABBAS, source=SOURCE)
    b.stats(_FOUND["cleon"], CLEON, source=SOURCE)


def _overwrites(theban: Theban) -> None:
    """Where this book differs from the Tribunal book it wins, with it on:
    Nestor, Io and Kaia are Polyaigos's three unnamed magi; Catella trained
    in Constantinople and left around the siege (p. 93); and Miletos lies
    inside Nicaea, in its extreme south-west."""
    saga = theban.b.saga
    theban.covenants["polyaigos"].unnamed_magi = 0
    for character in saga.characters:
        if character.name == "Catella":
            character.summary = character.summary.replace(
                "She came straight from her Gauntlet, two years before "
                "Constantinople fell, while",
                "She trained in Constantinople and left around the time of the "
                "siege, while",
            )
    for neighbour in saga.neighbours:
        if neighbour.name == "Thrakesion":
            neighbour.summary = paragraphs(
                neighbour.summary,
                "Miletos, south of the Maeander's mouth, still lies inside "
                "Nicaea, in its extreme south-west.",
            )


def finish(theban: Theban) -> None:
    """Take Didyma's place in what the Tribunal's own finish rebuilt: its
    phyle (The Sundered Eagle p. 25 lists the Kretan phyle without it,
    Through the Aegis p. 93 with it), and its metoikos and arche."""
    tribunal = theban.tribunal
    assert tribunal is not None
    package.phylai(tribunal)[theban.covenants["didyma"].id] = "Kretan"
    _overwrites(theban)
    theban.b.link(
        theban.world["children_of_olympos"],
        "covenants",
        theban.covenants["didyma"],
        "Would dearly like Herakles, and comes on pilgrimage",
    )
    for entry in package.magi(tribunal):
        if entry["character_id"] == theban.magi["william"].id:
            entry["status"] = "metoikos"
            entry["why"] = (
                "Of the Normandy Tribunal, guest of Herakles since 1210 "
                "(Through the Aegis p. 74)."
            )
        elif entry["character_id"] == theban.magi["nikola"].id:
            entry["why"] = (
                "An arche of the Kretan phyle, on the Treasury Council as a "
                "tutor (Through the Aegis pp. 74, 93). The book gives no "
                "tokens or shards."
            )


#: People made here and used by later steps but not listed on the
#: Tribunal's roster: an apprentice, covenfolk and teachers.
_FOUND: dict[str, Character] = {}


def _places(theban: Theban) -> dict[str, Neighbour]:
    b = theban.b
    thrakesion = theban.places["thrakesion"]
    site = b.place(
        "Didyma",
        inside=thrakesion,
        realm="Faerie",
        aura=4,
        detail=FULL,
        summary=paragraphs(
            "A cluster of crumbling temples ten miles south of Miletos and a "
            "mile from the Anatolian coast, in a craggy hollow split from "
            "the limestone of a flat, dry plain barely 100 paces above the "
            "sea. The hollow, some five paces deep, is ringed by a retaining "
            "wall, and the marble columns rise out of it to throw long black "
            "shadows across the plain.",
            "Most of the temples date from Trajan's rebuilding in 100, though "
            "they have fallen and risen many times. The covenfolk, most of "
            "them of the Branchidae family, make up a sizeable village here.",
        ),
        secrets=[
            titled(
                "How old the cult is",
                "Didyma's cult is not as old as it claims. It has been remade "
                "after each conquest and persecution, last after the "
                "Christians left in the eighth century, so its rites are a "
                "second-hand memory of ancient stories shaped by the faerie "
                "Apollo Didyma, himself a mirror of human tales; its priestly "
                "dress is closer to Rome than to old Greece. Only one who "
                "knows faeries and stories deeply, or the far past by "
                "supernatural means, could see it.",
            ),
        ],
    )
    places = {"didyma": site, "thrakesion": thrakesion}
    for key, name, words in (
        (
            "apollo_temple",
            "The Temple of Apollo",
            "The enormous temple, on a base 50 paces by 100, a stone forest of "
            "over 100 columns each 20 paces tall, seen for miles across the "
            "plain and mostly open to the sky. Its enclosed centre holds "
            "Alexander's and Nikola's laboratories with the library and "
            "scriptorium between them, among them the record of many "
            "thousands of prophecies, most of them long past or trivial. Its "
            "statues and frescoes show gods and, oddly for a Greek temple, "
            "many wild beasts, mythic and mundane, perhaps for those that "
            "follow the Sacred Way.",
        ),
        (
            "athena_temple",
            "The Temple of Athena",
            "Well kept and shrouded in thick black drapes that crack in the "
            "wind and hide all within, which usually overcomes Ariane's "
            "Restriction. Like the smaller temples it stands on a stepped "
            "platform two paces high of some 3,500 square feet, with "
            "10-pace columns about a roofed hall flanked by two large cellae. "
            "It holds Ariane's laboratory and the coffers.",
        ),
        (
            "zeus_temple",
            "The Temple of Zeus",
            "Sound in structure though much chipped, with fantastic bones "
            "littering the ground outside and exotic pelts curing between the "
            "columns. It holds Herakles's and William's laboratories, and the "
            "Frankish mercenaries camp in its central hall.",
        ),
        (
            "dionysus_hermes",
            "The Temples of Dionysus and Hermes",
            "Damaged, with fallen columns and headless or missing statues, "
            "and sometimes used as stores. The Temple of Dionysus held the "
            "laboratories of Lydia and Cora, which are offered to visitors "
            "who need one.",
        ),
        (
            "baths",
            "The Baths",
            "Roman work: a domed central hall, the covenfolk's meeting, "
            "storage and work place, with two wings. The eastern baths are "
            "filled in and house covenfolk; the western are in use, tiled in "
            "fine mosaics of gods and myths, fed from the Sacred Spring, and "
            "heated by the Bath Rock instead of the old boilers. Bathing "
            "there gives the covenfolk a +1 Living Modifier to aging rolls.",
        ),
        (
            "altars",
            "The Round Altars",
            "Two round altars carved with gods and titans before the Temple "
            "of Apollo, their purpose forgotten. Magi duel at certamen on "
            "the rim of the large one, 7 paces across and a pace high. The "
            "small one, 3 paces across, has no use.",
        ),
        (
            "ruins",
            "Hera's Temple and the Church",
            "Two collapsed buildings: Hera's temple, fallen early in the "
            "seventh century, and Theodosius's fifth-century church, heart "
            "of a small colony of monks, brought down by an earthquake in "
            "the late 800s. The monks moved to Miletos. The old monk Basil "
            "and a few young monks live in a corner still standing.",
        ),
        (
            "wall",
            "The Covenant Wall",
            "A stone retaining wall about five paces tall around the hollow, "
            "the Boundary of the Aegis of the Hearth; cavalry cannot pass it. "
            "Climbing it is a Dexterity + Athletics roll against 9, with "
            "armour's encumbrance, and a fall does +10. On the east, five "
            "steps a pace tall, two deep and 50 wide lead up to the plain: "
            "easy on foot, Dexterity + Ride against 6 for a rider. Zeus' Arm "
            "lifts bulky goods in and out.",
        ),
    ):
        places[key] = b.place(name, inside=site, realm="Faerie", aura=4, summary=words)
    places["spring"] = b.place(
        "The Sacred Spring",
        inside=site,
        realm="Faerie",
        aura=4,
        detail=FULL,
        summary=paragraphs(
            "In the open heart of the Temple of Apollo, behind a crumbling "
            "wall, it feeds a square pool of 500 square feet, a pace deep, "
            "and the baths. It is a vis source and the water of prophecy.",
            "A prophecy. The Branchidae chooses a subject, an individual, "
            "place, bloodline (DE p. 93) or nation, with an Arcane Connection "
            "to the individual or to a member of the bloodline, and moves a "
            "pawn of vis of any Art into a draught of the water, a day in a "
            "laboratory or sooner by ReVi. An oracle, who needs the Visions "
            "Flaw but not the Gift, drinks, trances about an hour and tells "
            "the vision. Interpreting it takes about a day and gives the "
            "prophecy text, usually a cryptic phrase, copied like a level 5 "
            "Lab Text, with an expiry, most often a year or a decade.",
            "Anyone who reads or hears the text gains one Prophecy Point, a "
            "one-off +3 like a Confidence Point on a roll about the subject, "
            "or +6 if it concerns faeries, before the expiry. A second reading "
            "gives no second point, but each different prophecy of a subject "
            "gives one. At once a grog may have one valid prophecy, a companion "
            "or magus three, Mythic Blood six, and a place, bloodline or "
            "nation usually one; beyond that the visions repeat. A false "
            "prophecy gives no point, and the Branchidae rarely lie about "
            "them, faithful transmission being their religion.",
        ),
        secrets=[
            titled(
                "Why prophecies of faeries are stronger",
                "The Branchidae put the +6 of a prophecy that concerns "
                "faeries down to Apollo Didyma being a great faerie. The "
                "truth is that prophecies are stories, and faeries work to "
                "fulfil them.",
            ),
        ],
    )
    plain = b.place(
        "The Didyma Plain",
        inside=thrakesion,
        realm="",
        summary=paragraphs(
            "Six small fishing villages on the coast and dozens of farming "
            "hamlets on the plain, each under 100 people, living by grain, "
            "vegetables and goats, with fish on the shore. Nearly all are "
            "Christians who hear Sunday mass in Miletos or Panormos, and many "
            "walk to Didyma once or twice a year for a traditional prophecy. "
            "They think well of the covenant, and think the magi and "
            "oracles very odd.",
        ),
    )
    places["plain"] = plain
    places["sacred_way"] = b.place(
        "The Sacred Way",
        inside=thrakesion,
        realm="Faerie",
        aura=1,
        detail=FULL,
        summary=paragraphs(
            "A road of stone blocks a pace square, five to seven paces wide, "
            "running ten miles from Miletos to the hollow of Didyma, turning "
            "aside for Panormos, about five hours' walk. The old shrines, "
            "sphinxes, statues of patriarchs and tombs of citizens are mostly "
            "gone, and Christian shrines stand each half mile, each with a "
            "Divine aura of 2.",
            "It is also a great way from the faerie realm into the mundane "
            "world, and nearly any faerie may step onto it, sphinxes most of "
            "all. Herakles came by it as a child, and several Merinita have "
            "sought the way back along it, perhaps Orion among them, who "
            "vanished in 1053.",
        ),
    )
    miletos = b.town(
        "Miletos",
        place=thrakesion,
        ruler="Anakletos, Strategos of Miletos",
        answers_to=theban.world["emperor_of_nicaea"],
        summary=paragraphs(
            "An ancient port on a rocky peninsula, sometimes called Palatia "
            "for the old stone temples and halls that fill it, the home of "
            "Thales and the first town of Mythic Europe laid out on a grid. "
            "Walled, with the Sacred and Lion gates towards the land, it has "
            "two harbours, the Lion Harbour behind a gated sea-wall and the "
            "Theatre Harbour, and fresh water still comes down a Roman "
            "aqueduct. Several thousand people live there, far fewer than "
            "of old, so stone and empty ground lie south of the walls.",
            "Greek refugees from Constantinople brought a boom. Greek, "
            "Venetian, Arab and Jewish quarters all use the port as a hub for "
            "goods from Constantinople, North Africa, the East and Europe, and "
            "under the profit runs a hatred of the Venetians that sometimes "
            "breaks out in the streets. All value the covenant's warded "
            "warehouses, and old half-pagan customs survive among the "
            "citizens, among them walking the Sacred Way for a prophecy "
            "before a wedding, a birth or a bargain.",
        ),
    )
    places["miletos"] = miletos
    places["panormos"] = b.town(
        "Panormos",
        place=thrakesion,
        summary=paragraphs(
            "A port of just under a thousand people on the turquoise sea, a "
            "mile north-west of Didyma, whose temples stand in plain view. "
            "Many townsfolk are unGifted Branchidae; the covenant's Christians "
            "come here to mass, and townsfolk walk the other way for "
            "prophecies. The weathered skulls of a dozen sea-monsters hang "
            "from the arch on the main road east, which joins the Sacred Way "
            "just outside town.",
            "Arab traders here are said to buy and sell on what pirates "
            "plunder from the Miletos shipping lanes.",
        ),
    )
    places["delphinion"] = b.place(
        "The Delphinion",
        inside=miletos,
        realm="Faerie",
        aura=4,
        detail=FULL,
        summary=(
            "A plain, well-kept, defunct stone temple behind the warehouses, "
            "where the Sacred Way begins: a lacuna of the Faerie in the "
            "city, and home to Callista's household. Chloris likes to raise "
            "her litters here."
        ),
    )
    places["lion_harbour"] = b.place(
        "The Lion Harbour Warehouses",
        inside=miletos,
        realm="Divine",
        aura=2,
        summary=(
            "Three adjoining warehouses of solid, airy stone under wooden "
            "roofs, 5,000 square feet each, and a dock for large ships, not "
            "under any Aegis. Each is warded against vermin, rot and "
            "pestilence. Usually eight of the turb stand guard, with five "
            "Defender Swords, and a dozen porters and teamsters hired by "
            "Callista, who have seldom seen a magus. One is leased at "
            "present to a Venetian cartel. Here too are the Oracle's Dredge, "
            "two small old cedarwood boats and six Porter's Helpers."
        ),
    )
    places["arab_market"] = b.place(
        "The Arab Market of Miletos",
        inside=miletos,
        realm="",
        summary="The busy, scented spice market, where some goods hold vis.",
    )
    places["fortress"] = b.place(
        "The Strategos' Fortress",
        inside=miletos,
        realm="",
        summary=(
            "Ten towers about a great courtyard on a hill in the middle of "
            "Miletos, over the Theatre Harbour, on the site of the Roman "
            "theatre turned to military use more than 500 years ago. Few "
            "remember the theatre, Apollo Didyma among them."
        ),
    )
    places["aftonsitiron"] = b.place(
        "Aftonsitiron",
        inside=thrakesion,
        realm="",
        summary=(
            "A small village a mile north of Miletos, of rich soil and heavy "
            "barley crops, some of it holding vis."
        ),
    )
    return places


def _covenant(theban: Theban, site: Neighbour) -> Covenant:
    b, tribunal = theban.b, theban.tribunal
    assert tribunal is not None
    covenant = b.covenant(
        NAME,
        tribunal=tribunal,
        founded=990,
        season="Autumn",
        place=site,
        aura=4,
        realm="Faerie",
        aegis=40,
        detail=FULL,
        summary=paragraphs(
            "The temple of Apollo at Didyma has had its oracles, on and off, "
            "for two thousand years, and Miletos was a rival to Athens when "
            "they began. Its symbol is the Eye of the Branchidae. Over a "
            "hundred covenfolk live here, most of them born to the family; "
            "the magi and some of the people go about in the hooded togas "
            "of Roman-era pagan priests, while the rest look and talk like "
            "any Greek of Miletos. Visitors are welcome, pagans above all, "
            "and any magus without a bad name. An arche meets them, Sebasten "
            "or Philip at the temples or Callista in the city, and the "
            "Patriarch or the Strategos comes out to anyone exotic.",
            "The covenant's purpose before the Tribunal is to make and "
            "interpret prophecies. The Greek magi once escaped the worst of "
            "the Schism War on its advice, and magi still come before a "
            "great venture. It lives by fees for prophecy and other rites "
            "from the Christians of Miletos and the villages, a tenth of "
            "them paid to the city, under second-century imperial decrees "
            "still good in law, and by renting warehouses at the Lion "
            "Harbour, at a premium for their wards. It has also dredged "
            "the harbour for over two hundred years.",
        ),
        what_matters=joined_lines(
            "Build Points: 2575 (devices 502, laboratories 360, Lab Texts 271, "
            "library 1125, money 10, specialists 58, vis 249)",
            "Boon: Powerful Ally (Apollo Didyma, the covenant's patron, a "
            "faerie, as all know)",
            "Boon: Powerful Ally (Niketas, Metropolitan of Miletos)",
            "Boon: Aura (Minor) (the book's Increased Aura; the aura is 4)",
            "Boon: Edifice (the Temple of Apollo); Right (granted by Miletos, "
            "to conduct prophecies); Secondary Income (warehouses at the Lion "
            "Harbour, secure and profitable); Veteran Fighters (split between "
            "Didyma and Miletos, enlarged by William's Franks, and quarrelsome "
            "since some of the Greeks fought at Constantinople)",
            "Hook: Road (Major) (the Sacred Way); City (Miletos); Crumbling; "
            "Faerie Aura (4)",
            "Allies: Apollo Didyma; Niketas; the Redcaps of Alexandria; "
            "Ingasia and Aegaea, on good terms",
            "Wealth: 100 Mythic Pounds in mundane goods.",
        ),
        notes=paragraphs(
            "Offices and votes. Ten votes sit on the Council of Magi: "
            "Alexander 3 (Patriarch, Librarian, resident), Nikola 2 (Strategos, "
            "resident), Ariane 2 (Chancellor, resident), Herakles 1, William "
            "1, and Magarethe 1 as archon. The agenda: those present name "
            "themselves and their offices; current prophecies are discussed, "
            "and the Patriarch presents a new one if a Tribunal is next; new "
            "residents are voted on; Chancellor, Strategos, Librarian and "
            "archon report; each maga reports her service for the Patriarch's "
            "approval; he confirms or names officers; other business.",
            "The Council of Archai rules the covenfolk under the magi, "
            "meeting monthly on turb training, laboratory supplies and "
            "mundane dealings. Five archai serve five years each, one "
            "retiring and one elected each midwinter feast, by majority with "
            "equal votes: Magarethe the archon, Callista, Sebasten, Basil and "
            "Philip. Visiting magi are expected to follow their hosts' wishes, "
            "and visiting grogs and companions the archai's direction.",
            "The turb is 18 fighters (the Standard Soldier, ArM5 p. 22) under "
            "two leaders, Philip and Sebasten, and William's four Franks. Two "
            "bands of four are based at the warehouses, one on duty, changing "
            "with a covenant band each week, the Franks taking their turn. "
            "With William leading, the Franks fight as a trained group at "
            "+18, or +9 led by one of their own. The Didyma turb often fight "
            "in pairs, one with a Defender Sword covering both.",
            "Specialists, 58 Build Points in all: Basil (12), Abbas (8), five "
            "young scribes lent by Niketas's monasteries from 15 until each "
            "turns 20, with Artes Liberales 2 (logic) and Scribe 4 (quickly) "
            "(20), three stonemason's apprentices (12) and Cleon (6).",
            "Branchidae beyond Didyma. Unknown numbers of the line of Bastards, "
            "Gifted children of unGifted Branchidae, may be in any House "
            "unaware of their birth-right. One magus of the line of Tessa "
            "and two of the line of Damen live, and in a great crisis may "
            "come to help what is in effect their domus magna. Nikola's "
            "tutor's work, with the Diamond of Hermes, should recover some "
            "of the Bastards.",
            "Earlier residents. Soteria, Basil, Jason, Brasidas, Tessa, Damen, "
            "Lydia and Cora, Branchidae, and Cletus of the Lineage of Pralix; "
            "Orion, Verditius then Merinita, and the Merinita Hector, "
            "Achillios, Lana and Nicodemus. See the Diary for their dates.",
            "Theme: responding to change. The covenant hangs on threads: the "
            "few Branchidae, the tolerance of city and church, the demon's "
            "sleep, Miletos's trade. One breaking may tip it into winter. Any "
            "resident here suits a player, and further magi may be added or "
            "replace them; the oldest Gifted Branchidae holds the title, and "
            "new votes shift the balance from Alexander and Nikola, who "
            "will resent it. Moved elsewhere, it needs a Mediterranean shore "
            "for its temple, or a secret regio; the demon may lie under it "
            "anywhere.",
            "Story seeds. Taxation Audit: Nicaea sends auditors after Leander, "
            "and Cleon, though clean, looks too close to the covenant. Spice "
            "Harvest: the market's vis comes from somewhere, and following it "
            "may anger magi at other markets, or another may cut off the "
            "supply. The Children of Olympos: its members come to worship "
            "and contact the faerie gods, and would dearly like Herakles, who "
            "sympathises but thinks himself a god already; Ariane leans "
            "their way too.",
            "Storyline, A Sanctuary: nothing changes, and the covenant is a "
            "safe, rich base. Herakles and William join adventures, Chloris "
            "spies out Constantinople for Ariane, and Torvus steals things.",
            "Storyline, City, Church and War. Niketas dies, and 35 voters "
            "(quorum 20, two thirds to win) gather: 25 Miletos priests, 3 of "
            "Panormos, 5 abbots and 2 village priests. Father Christos, a "
            "charismatic Christian Branchidae, is Alexander's choice; Father "
            "Yannis, a sarcastic old deacon from Constantinople, would purge "
            "the priests and try the Didyma magi as pagans, and may appeal to "
            "Patriarch Manuel. Or lost decrees of the 300s banning the oracle "
            "come before the Strategos' court, genuine or forged. Or Quaesitors "
            "look into old or new interference. Or Venetians bring in Franks "
            "and grab property; a riot hurts a Latin priest, and if he dies "
            "Templars may come, so the Strategos asks the magi to heal him. "
            "Or Rum strikes the coast; refugees slum outside Miletos, a "
            "starving mob walks to Didyma, the Strategos drafts the turb, and "
            "Omar Allaid of Panormos offers the pagans a Seljuk licence for "
            "magic against Miletos. Neutrality will see the cult outlawed by "
            "whoever wins.",
            "Using it from outside. Theban magi and pagans come for prophecy; "
            "Christians to destroy the cult; Merinita for the Sacred Way; "
            "hunters for a base, with William and Herakles as guides; "
            "travellers to take ship for North Africa; Quaesitors for "
            "interference; officials to see Nikola.",
        ),
        secrets=[
            titled(
                "What sleeps under the plain",
                "Agamenoth, a demon prince, sleeps under the Didyma plain; his "
                "stirring caused the earthquakes.",
            ),
            titled(
                "What Agamenoth wants",
                "Woken by the fall of Constantinople, Agamenoth means only "
                "destruction. Earthquakes wreck Miletos season after season, "
                "leaving a stench of sulphur.",
            ),
            titled(
                "Mileta and Agamenoth",
                "Mileta smells Agamenoth but fears questions, and may suggest "
                "asking Apollo; he would use her past against her.",
            ),
            titled(
                "Agamenoth in the church records",
                "Old church records in Miletos mention Agamenoth.",
            ),
            titled(
                "The Tessa and Damen Wards",
                "Lana, with Alexander, cast two wards after Jason's loss that "
                "barred the lines of Tessa and Damen from Didyma. Their "
                "braziers went out by accident in the 1190s and Alexander "
                "could not recast them, though Lab Texts may lie in Lana's "
                "effects with Herakles.",
            ),
            titled(
                "Didyma and its bishops",
                "Niketas's two predecessors of 1170, hostile to pagans, both "
                "died suddenly after election, and Michael (metropolitan to "
                "1170) was a Branchidae under a Longevity Ritual: the "
                "covenant has long meddled with its bishops.",
            ),
            titled(
                "Storyguide Notes",
                "Hook: Monster (Major, unknown to all): Agamenoth.\n\n"
                "Storyline, The Sleeping Beast. The stench of sulphur may pass "
                "for a sigil. Agamenoth's powers should not pierce the Aegis; "
                "if it fails, laboratories lose the season, and suffer -3 "
                "until a season's tidying. Infernal Lore against 12 knows his "
                "Reputation.\n\n"
                "Storyline, The Branchidae. Alexander dies. The Tessa and "
                "Damen Wards: ReCo(In) 60, Touch, Fire, Boundary, ritual, "
                "Base 15; a bloodline primogenitor's Arcane Connection is "
                "needed. "
                "Nestor of Polyaigos, of Damen's line and older than Nikola, "
                "comes secretly to Miletos, hires agents to put out flames that "
                "are already dead, and claims the title at the solstice, with Io "
                "and Kaia waiting in Panormos. Age and descent can be shown by "
                "Intellego Corpus. Years later Aristocles the Wanderer comes with "
                "three Tremere, Anica, Octavian and Petre, gracious about the "
                "title, with a secret purpose: to slay Apollo Didyma, behind a "
                "declared Wizard War. Apollo sends the trireme Diakopho, with 200 "
                "faerie ghosts of dead Branchidae and a squadron of talkative "
                "dolphins, to fetch Erginos the Argonaut, son of a Branchidae "
                "woman and Poseidon, from the faerie seas in the Apeiro. If the "
                "characters side with Aristocles, Apollo recruits at Panormos.",
            ),
        ],
    )
    covenant.charter_of_covenant.name = "The Charter of the Council of the Magi"
    return covenant


def _people(theban: Theban, covenant: Covenant) -> dict[str, Character]:
    b = theban.b
    found: dict[str, Character] = {}
    for key, name, house, age, _block, summary, hidden in MAGI:
        found[key] = theban.magi[key] = b.magus(
            name,
            covenant=covenant,
            house=house,
            age=age,
            summary=summary,
            secrets=hidden,
            traditions=[BRANCHIDAE] if house == EX_MISCELLANEA else None,
        )
    for key, name, kind, age, _block, summary, hidden in PEOPLE:
        found[key] = theban.magi[key] = b.magus(
            name,
            covenant=covenant,
            house="",
            age=age,
            summary=summary,
            secrets=hidden,
            type=kind,
        )
    # An apprentice: on no Tribunal roster.
    found["aoede"] = _FOUND["aoede"] = b.magus(
        "Aoede",
        covenant=covenant,
        house=EX_MISCELLANEA,
        age=9,
        summary=(
            "Alexander's apprentice and great-granddaughter, born in 1211, "
            "the darling of the Branchidae, though the unGifted resent "
            "that a little. She should take her Gauntlet at Didyma in 1231."
        ),
        secrets=[
            titled("Aoede's prophecy", "Aoede is prophesied to die in the dark."),
            titled("Storyguide Notes", "Aoede has a Death Prophecy."),
        ],
        traditions=[BRANCHIDAE],
    )
    for key, name, words in (
        ("basil", "Basil the Monk", "A monk of Miletos, secretly a pagan for "
         "many years, who lives in the monastic ruins by a dispensation "
         "Niketas arranged and still writes to his brethren."),
        ("abbas", "Abbas", "The covenant's master stonemason."),
        ("cleon", "Cleon", "Callista's husband, the tax official who smooths "
         "the covenant's way with the city."),
    ):  # fmt: skip
        found[key] = _FOUND[key] = b.magus(
            name,
            covenant=covenant,
            house="",
            age=None,
            summary=words,
            type="grog",
        )
    for name, kind, words in HOUSEHOLD:
        b.magus(name, covenant=covenant, house="", age=None, summary=words, type=kind)
    polyaigos = theban.covenants["polyaigos"]
    for key, name, house, words in (
        (
            "nestor",
            "Nestor of Polyaigos",
            EX_MISCELLANEA,
            "Of the Branchidae line of Damen, whose filius he is, "
            "older than Nikola by several years.",
        ),
        (
            "io",
            "Io",
            EX_MISCELLANEA,
            "Nestor's daughter, of the Branchidae line of Damen. He and she "
            "carry Arcane Connections to each other.",
        ),
        (
            "kaia",
            "Kaia",
            FLAMBEAU,
            "A Flambeau ally of Nestor's.",
        ),
    ):
        theban.magi[key] = b.magus(
            name,
            covenant=polyaigos,
            house=house,
            age=None,
            summary=words,
            traditions=[BRANCHIDAE] if house == EX_MISCELLANEA else None,
        )
    b.magus(
        "Aristocles the Wanderer",
        covenant=None,
        house=EX_MISCELLANEA,
        age=None,
        summary=(
            "Filius of Tessa, trained at Alexandria, senior to Nikola but "
            "younger than Nestor. His name and fate are unknown at Didyma: "
            "he wandered far and now lives at the oppidum of Tablinum in "
            "the Transylvanian Tribunal."
        ),
        secrets=[
            titled(
                "What Aristocles means to do",
                "Aristocles has renounced the Branchidae cult and means to end "
                "Apollo Didyma's worship by slaying him, with House Tremere's "
                "research behind him, whether or not it means the deed to be "
                "done.",
            ),
        ],
        traditions=[BRANCHIDAE],
    )
    return found


def _world(
    theban: Theban, places: dict[str, Neighbour], people: dict[str, Character]
) -> dict[str, Neighbour]:
    b = theban.b
    miletos = places["miletos"]
    world = {
        "strategos": b.lord(
            "Anakletos, Strategos of Miletos",
            title="landed",
            seat="The Strategos' Fortress",
            place=miletos,
            answers_to=theban.world["emperor_of_nicaea"],
            summary=paragraphs(
                "The Nicaean governor of a large hinterland that takes in the "
                "covenant, a clever man of middle age, once a young officer "
                "of a rich Constantinople family, raised fast when the army "
                "fell apart. On paper he has ten taxiarchiai of 1,000 and two "
                "moria of 3,000; in truth about 100 foot and 100 horse, with "
                "about 100 Latin mercenaries at the gates and as marines "
                "against pirates. With levies he might raise 3,000 in a season, "
                "leaving the country bare.",
                "Fearing invasion, and with quarrels between Latins and "
                "Greeks on his hands, he leaves the oracles alone. He knew "
                "Ariane in Constantinople, and knows the magi for members of a "
                "league of half-pagan sorcerers.",
            ),
            secrets=[
                titled(
                    "Anakletos's prophecy",
                    "Anakletos, Strategos of Miletos, has had a fearsome "
                    "prophecy of a Muslim invasion.",
                ),
            ],
        ),
        "metropolis": b.church(
            "The Metropolis of Miletos",
            church="Archbishop's cathedral",
            place=miletos,
            ruler="Niketas II",
            answers_to=theban.world["orthodox_patriarch"],
            summary=paragraphs(
                "An old Greek see: its bishop Kaisarios Eusebio sat at Nicaea "
                "in 325, Hyakinthos was raised to archbishop in 538, and "
                "Michael won metropolitan rank in the early eleventh century. "
                "A few Latin clergy serve the Venetian quarter. Niketas II "
                "has held it since 1172, from the episcopal palace, and "
                "before him Nikephoros (965-969), Epiphanios (969-1013), "
                "Michael (1013-1170), Niketas (1170) and Nikephoros II (1170), "
                "with the see empty in 1171 for want of a quorum.",
            ),
        ),
        "kommerkiarioi": b.faction(
            "The Kommerkiarioi of Miletos",
            faction="Other",
            place=miletos,
            ruler="Leander",
            summary=(
                "The tax officials who assess and tax goods at the port at a "
                "tenth, half to Nicaea and half to the local forces and "
                "expenses, and seal them so they are not taxed twice in "
                "imperial cities. A split lot needs an official present; "
                "forging a seal is death, or sometimes a heavy fine. Their "
                "head, Leander, tall, bald and piercing-eyed, is known to be "
                "corrupt, and many merchants pay him, though nothing is "
                "proven at Nicaea. Cleon has the covenant and its warehouses."
            ),
            secrets=[
                titled(
                    "Leander's blackmailer",
                    "Torvus, William's falcon familiar, is blackmailing "
                    "Leander with stolen papers.",
                ),
            ],
        ),
    }
    return world


def _links(
    theban: Theban,
    covenant: Covenant,
    places: dict[str, Neighbour],
    world: dict[str, Neighbour],
) -> None:
    b = theban.b
    b.link(covenant, "places", places["sacred_way"], "its road and faerie route")
    b.link(covenant, "places", places["miletos"], "its city, ten miles north")
    b.link(covenant, "places", places["panormos"], "its nearest port")
    b.link(covenant, "places", places["delphinion"], "Callista's house")
    b.link(covenant, "places", places["lion_harbour"], "its warehouses")
    for key, note in (
        ("alexandria", "Redcaps come often; Tessa's old home"),
        ("polyaigos", "Kretan phyle; Nestor and Io of the line of Damen"),
        ("favonius", "Kretan phyle; its ships sometimes moor at Panormos"),
        ("ingasia", "On good terms"),
        ("aegaea", "On good terms; Herakles's grand-parens came from it"),
    ):
        b.link(covenant, "covenants", theban.covenants[key], note)
    b.link(
        theban.places["maeander"],
        "covenants",
        covenant,
        "Its first spring floods are a vis source of the covenant's",
    )
    b.link(world["strategos"], "covenants", covenant, "Leaves the oracles alone")
    b.link(world["metropolis"], "covenants", covenant, "Allied, largely in secret")


def _labs(b: Builder, covenant: Covenant, people: dict[str, Character]) -> None:
    for key, name, totals, spec, words in (
        (
            "alexander",
            "Alexander's laboratory",
            {
                "size": 1,
                "refinement": 4,
                "general_quality": 1,
                "upkeep": 2,
                "safety": 8,
                "warping": 1,
                "aesthetics": 2,
            },
            {"Intellego": 4, "Teaching": 1},
            "In the Temple of Apollo, watched over by Apollo Didyma, with a "
            "gallery from which Aoede can watch without disturbing the work. "
            "70 Build Points. Virtues: Greater Guardian (Apollo Didyma, +3 "
            "Intellego), Gallery (+1 Teaching), Lesser Expansion (+1 Intellego).",
        ),
        (
            "nikola",
            "Nikola's laboratory",
            {
                "size": 1,
                "refinement": 4,
                "upkeep": 4,
                "safety": 2,
                "aesthetics": 5,
            },
            {"Animal": 1, "Intellego": 8, "Teaching": 2},
            "In the Temple of Apollo, large and luxurious, where she lives "
            "among her work with Alexios and her specimen collections, under "
            "a great statue of Branchos that rather dominates it. 80 Build "
            "Points. Virtues: Greater Feature (Branchos statue, +3 Intellego), "
            "Palatial (+1 Intellego, +2 Teaching), Living Quarters, Specimens "
            "(+1 Animal). Flaws: Greater Focus (Branchos statue, +4 Intellego).",
        ),
        (
            "ariane",
            "Ariane's laboratory",
            {"refinement": 2, "safety": 2, "warping": 1},
            {"Vis Extraction": 3},
            "In the Temple of Athena, dark behind black drapes and lit by "
            "smoky candles, with the vis still she brought from Constantinople "
            "and much plain, good equipment. 40 Build Points. Virtues: Greater "
            "Feature (vis still, +3 vis extraction), Superior Equipment (+1 "
            "vis extraction). Flaws: Defective Lighting, Undecorated (-1 vis "
            "extraction).",
        ),
        (
            "herakles",
            "Herakles's laboratory",
            {
                "refinement": 1,
                "general_quality": -1,
                "upkeep": 1,
                "safety": 3,
                "warping": 2,
                "health": -1,
                "aesthetics": -3,
            },
            {"Rego": 5, "Spells": 1},
            "In the Temple of Zeus, watched over by his father, and kept "
            "going by offerings of mutton fat at solstices and equinoxes. "
            "Cramped for him; to anyone else it is an Awkward Shape, +1 "
            "General Quality and Upkeep without the Spells specialization. 30 "
            "Build Points. Virtues: Greater Guardian (Zeus, +3 Rego), Cramped "
            "(+1 Spells), Sacrifices (+2 Rego).",
        ),
        (
            "william",
            "William's laboratory",
            {
                "refinement": 1,
                "general_quality": -2,
                "upkeep": 1,
                "aesthetics": 4,
            },
            {"Vim": 1, "Items": 7},
            "In the Temple of Zeus, fitted out by Orion in 1020 with the large "
            "forge Hector and Achillios fought over; William wonders if it is "
            "more nuisance than use. 40 Build Points. Virtues: Greater Feature "
            "(forge, +3 Items), Specimens (magic creature skeletons, +1 Vim), "
            "Guard (mercenaries). Flaws: Greater Focus (forge, +4 Items).",
        ),
    ):
        master = people[key]
        b.laboratory(
            covenant,
            name,
            owner=master,
            characteristics=totals,
            specializations=spec,
            source="Through the Aegis p. 88",
            rooms={"As the book describes it": words},
        )
    for name in ("Lydia's old laboratory", "Cora's old laboratory"):
        b.laboratory(
            covenant,
            name,
            characteristics={"general_quality": -3},
            specializations={},
            source="Through the Aegis p. 89",
            rooms={
                "As the book describes it": "In the Temple of Dionysus, a "
                "Basic laboratory stripped of most equipment, offered to "
                "visitors. 50 Build Points."
            },
        )


def _library(b: Builder, covenant: Covenant) -> None:
    for name, kind, author, subject, level, quality, language, words in LIBRARY:
        art, ability = (subject, "") if subject in ARTS else ("", subject)
        if kind == "Summa":
            kind = "Art Summa" if art else "Ability Summa"
        b.book(
            covenant,
            name,
            kind,
            art=art,
            ability=ability,
            level=level,
            quality=quality,
            language=language,
            author=author,
            description=words,
        )


def _lab_texts(b: Builder, covenant: Covenant) -> None:
    for name, technique, form, level in LAB_TEXTS:
        book = b.book(
            covenant,
            f"Lab Text: {name} ({level})",
            "Lab Text",
            level=level,
            language=GREEK,
            description=f"{technique} {form}.",
        )
        book.text_kind = TEXT_SPELL
        book.spell_name = name


def _effect(
    name: str,
    technique: str,
    form: str,
    rtd: tuple[str, str, str],
    level: int,
    words: str,
    *,
    uses: str = "Unlimited",
    penetration: int = 0,
    requisites: str = "",
    constant: bool = False,
    concentrates: bool = False,
) -> InstilledEffect:
    """An effect at its own level, before the book's frequency, Penetration
    and constant-effect additions, which the fields carry."""
    reach, duration, target = rtd
    return InstilledEffect(
        id="",
        name=name,
        technique=technique,
        form=form,
        requisites=requisites,
        range=reach,
        duration=duration,
        target=target,
        level=level,
        description=words,
        uses_per_day="2" if constant else uses,
        penetration=penetration,
        environmental_trigger=constant,
        maintains_concentration=concentrates,
    )


def _device(
    b: Builder,
    covenant: Covenant,
    name: str,
    words: str,
    effects: list[InstilledEffect],
    *,
    opened: int = 0,
    holder: Character | None = None,
    talisman: bool = False,
    lab_text: int = 0,
) -> EnchantedDevice:
    device = b.device(covenant, name, description=words, effects=effects)
    device.pawns_opened = opened
    device.talisman = talisman
    if holder is not None:
        device.holder_kind, device.holder_id = "character", holder.id
    if lab_text:
        book = b.book(
            covenant,
            f"Lab Text: {name}",
            "Lab Text",
            language=GREEK,
            description=f"Worth {lab_text} Build Points.",
        )
        book.text_kind = TEXT_ENCHANTMENT
    return device


def _devices(b: Builder, covenant: Covenant, people: dict[str, Character]) -> None:
    touch_sun_structure = ("Touch", "Sun", "Structure")
    touch_conc = ("Touch", "Concentration", "Individual")
    touch_mom = ("Touch", "Momentary", "Individual")
    _device(
        b,
        covenant,
        "Vermin Wards",
        "Three fist-sized stones carved with rats, at the Miletos warehouses. "
        "Printed Re(In)An 29. 36 Build Points.",
        [
            _effect(
                "Vermin Ward",
                "Rego",
                "Animal",
                touch_sun_structure,
                25,
                "Keeps animals of less than Size -1 out of a Structure.",
                requisites="Intellego",
                constant=True,
            )
        ],
        lab_text=6,
    )
    _device(
        b,
        covenant,
        "Wards Against Rot",
        "Three carved stone irises at the Miletos warehouses. Printed PeAq 34. "
        "42 Build Points.",
        [
            _effect(
                "Ward Against Rot",
                "Perdo",
                "Aquam",
                touch_sun_structure,
                30,
                "Stops stored goods rotting.",
                constant=True,
            )
        ],
        lab_text=7,
    )
    _device(
        b,
        covenant,
        "Pestilence Wards",
        "Three, at the Miletos warehouses. Printed ReVi 34, Pen +12. 42 Build Points.",
        [
            _effect(
                "Pestilence Ward",
                "Rego",
                "Vim",
                touch_sun_structure,
                24,
                "Bars minor demons of Might 10 or less from the Structure.",
                penetration=12,
                constant=True,
            )
        ],
        lab_text=7,
    )
    _device(
        b,
        covenant,
        "Warning Flame",
        f"A wand that lights a brazier at the end of the Sacred Way, just "
        f"outside the Aegis, in an emergency in Miletos; covenfolk then find a "
        f"magus, usually Ariane, who can reach Callista by Intangible Tunnel. "
        f"{CALLISTA_WAND} Printed CrIg 10. 4 Build Points.",
        [
            _effect(
                "Warning Flame",
                "Creo",
                "Ignem",
                ("Arcane", "Momentary", "Individual"),
                10,
                "Lights the brazier.",
                uses="1",
            )
        ],
        holder=people["callista"],
        lab_text=2,
    )
    _device(
        b,
        covenant,
        "Bath Rock",
        "Heats the western baths. Printed CrIg 19. 8 Build Points.",
        [
            _effect(
                "Bath Rock",
                "Creo",
                "Ignem",
                ("Touch", "Sun", "Room"),
                15,
                "Heats the water of the baths.",
                constant=True,
            )
        ],
        lab_text=4,
    )
    _device(
        b,
        covenant,
        "The Oracle's Dredge",
        "A pole about 20 feet long with a scoop on one end. Covenfolk paddle "
        "round the Lion Harbour with it each month, or the Meander's silt "
        "shows within a season and closes the harbour within a decade; city "
        "and merchants know of it. Printed PeTe 15. 6 Build Points.",
        [
            _effect(
                "Destroy the Silt",
                "Perdo",
                "Terram",
                ("Touch", "Momentary", "Part"),
                5,
                "Destroys about 10 cubic paces of mud it touches.",
            )
        ],
        lab_text=3,
    )
    _device(
        b,
        covenant,
        "Porter's Helpers",
        "Six handles at the Miletos warehouses. Printed ReTe 15. 36 Build Points.",
        [
            _effect(
                "Porter's Helper",
                "Rego",
                "Terram",
                touch_conc,
                5,
                "Clamped to a heavy object, lets the user move it as with +5 Strength.",
                uses="24",
                concentrates=True,
            )
        ],
        lab_text=3,
    )
    _device(
        b,
        covenant,
        "Defender Swords",
        "Ten, five usually with the warehouse garrison. Printed ReTe 20. 80 "
        "Build Points. No Concentration roll for watching melee blows, but "
        "one to do anything else, and against 15 to attack while "
        "concentrating.",
        [
            _effect(
                "Defend",
                "Rego",
                "Terram",
                touch_conc,
                10,
                "Automatically parries any number of metal weapons the wielder "
                "knows are coming, so not a stab in the back.",
            )
        ],
        lab_text=4,
    )
    _device(
        b,
        covenant,
        "Zeus' Arm",
        "A wooden crane with a 50-square-foot platform that lifts up to 100 "
        "tons into and out of the hollow. Printed ReTe 30. 12 Build Points.",
        [
            _effect(
                "Lift",
                "Rego",
                "Terram",
                touch_conc,
                15,
                "Lifts what rests on its platform.",
                concentrates=True,
            )
        ],
    )
    _device(
        b,
        covenant,
        "The Spice Wand",
        "Used on the Arab spice market. Printed InVi 12. 6 Build Points.",
        [
            _effect(
                "Vibrate at Vis",
                "Intellego",
                "Vim",
                touch_mom,
                2,
                "Trembles slightly if it touches vis.",
            )
        ],
        holder=people["callista"],
        lab_text=3,
    )
    _device(
        b,
        covenant,
        "Vis Divining Rods",
        "A pair of silver rods held out like a dowser's. Printed InVi 20. 8 "
        "Build Points.",
        [
            _effect(
                "Hear the Vis",
                "Intellego",
                "Vim",
                ("Touch", "Concentration", "Hearing"),
                10,
                "The user hears when within 30 paces of vis; Perception + "
                "Finesse against 6 finds it to within a foot.",
            )
        ],
        lab_text=4,
    )
    _device(
        b,
        covenant,
        "Diamond of Hermes",
        "Nikola made it for her work as a tutor, and lends it to Alexandria's "
        "Redcaps to check rumours of Gifted children. Printed InVi 25. 10 "
        "Build Points.",
        [
            _effect(
                "Glow at the Gift",
                "Intellego",
                "Vim",
                touch_mom,
                15,
                "Glows bright when touched by a Gifted person.",
            )
        ],
        lab_text=5,
    )
    _device(
        b,
        covenant,
        "The Vis Net",
        "Printed ReVi 20. 8 Build Points.",
        [
            _effect(
                "Gather Vis",
                "Rego",
                "Vim",
                touch_mom,
                15,
                "Cast into water with vis in it, gathers it as slimy, "
                "pulsing fist-sized crystals of 1 pawn each.",
                uses="24",
            )
        ],
        lab_text=4,
    )
    _device(
        b,
        covenant,
        "Staff of the Branchidae",
        "Alexander's talisman: a seven-foot wiry hornbeam staff, said to be a "
        "branch of a tree Branchos planted over two thousand years ago. 15 "
        "spaces used. Attunements: +6 Vim against hostile magic, +4 control "
        "at a distance, +4 destroy at a distance, +3 project a bolt or "
        "missile. The snake of its Sticks to Snakes is Size -4, Soak +2, fangs "
        "Init +3, Attack +11, Defense +10, Damage -7, poison Ease Factor 6, "
        "Light Wound (ArM5 p. 180); as the talisman in Grasping the Snake it "
        "has Alexander's Form Magic Resistance. 54 Build Points.",
        [
            _effect(
                "Tongue of Beasts",
                "Intellego",
                "Animal",
                ("Voice", "Diameter", "Individual"),
                25,
                "Lets the caster speak fluently with any animal.",
            ),
            _effect(
                "Sticks to Snakes",
                "Muto",
                "Herbam",
                ("Touch", "Sun", "Individual"),
                25,
                "Turns a stick into a writhing snake.",
                uses="24",
                requisites="Animal",
            ),
            _effect(
                "Grasping the Snake",
                "Muto",
                "Herbam",
                ("Personal", "Sun", "Individual"),
                20,
                "Turns the talisman itself into the snake.",
                uses="24",
                requisites="Animal",
            ),
            _effect(
                "Swarming Bolts of Earth",
                "Muto",
                "Terram",
                ("Sight", "Momentary", "Group"),
                25,
                "Ten crystal spears rise from the ground to impale the "
                "targets, +10 damage each.",
                uses="24",
                penetration=22,
                requisites="Rego",
            ),
        ],
        opened=30,
        holder=people["alexander"],
        talisman=True,
    )
    _device(
        b,
        covenant,
        "Soteria's Hand",
        "Nikola's talisman: the lead-plated skeletal hand of the first "
        "Hermetic Branchidae, which she dug up many years ago. 6 spaces used. "
        "Attunements: +4 destroy the human body, +4 wards. 22 Build Points.",
        [
            _effect(
                "The Wound that Weeps",
                "Perdo",
                "Corpus",
                ("Voice", "Momentary", "Individual"),
                15,
                "As the spell (ArM5 p. 133), with no Penetration, for "
                "frightening mundanes.",
            ),
            _effect(
                "Exorcise the Cursed Room",
                "Perdo",
                "Vim",
                ("Touch", "Momentary", "Room"),
                10,
                "Demons in the Room lose 5 Might.",
                uses="24",
                penetration=22,
            ),
        ],
        opened=10,
        holder=people["nikola"],
        talisman=True,
    )
    _device(
        b,
        covenant,
        "The Strategos' Sword",
        "A long sword of office made by Orion almost 200 years ago. 12 spaces "
        "used. 46 Build Points.",
        [
            _effect(
                "Ward Against Men",
                "Rego",
                "Corpus",
                ("Touch", "Diameter", "Individual"),
                25,
                "Wards the target against people; Nikola must lower her Parma "
                "a moment to use it on herself.",
            ),
            _effect(
                "Arms Multiplied",
                "Creo",
                "Terram",
                ("Touch", "Sun", "Group"),
                35,
                "Makes 10 copies of the sword, plain and fit for mundane "
                "use, but little use against supernatural foes.",
                uses="6",
            ),
            _effect(
                "Demon Bane",
                "Perdo",
                "Vim",
                touch_mom,
                10,
                "Does 15 Might damage to a demon.",
                penetration=40,
            ),
        ],
        opened=15,
        holder=people["nikola"],
    )
    _device(
        b,
        covenant,
        "William's Crusade Armor",
        "William's talisman: an iron eagle welded to a steel breastplate. "
        "Only the eagle is enchanted, but it has armour's shape bonuses "
        "(ArM5 p. 97). 8 spaces used. Attunements: +7 protect the wearer, +7 "
        "repel faeries. 26 Build Points.",
        [
            _effect(
                "The Light Pours Out of Me",
                "Creo",
                "Ignem",
                ("Personal", "Diameter", "Individual"),
                10,
                "Harmless, brilliant light streams from the armor.",
                uses="24",
            ),
            _effect(
                "Iron Ward",
                "Rego",
                "Vim",
                ("Personal", "Diameter", "Individual"),
                5,
                "Wards against faeries of Might 15 or less.",
                penetration=16,
            ),
            _effect(
                "Endurance of the Berserkers",
                "Rego",
                "Corpus",
                ("Touch", "Diameter", "Individual"),
                20,
                "As the spell (ArM5 p. 134), at Diameter.",
                uses="24",
            ),
        ],
        opened=15,
        holder=people["william"],
        talisman=True,
    )
    _device(
        b,
        covenant,
        "The Helm of Zotikos",
        "A bronze helm Nicodemus made for his goblin servant, Philip's "
        "grandfather, and Philip's by inheritance. 4 spaces used. 16 Build "
        "Points.",
        [
            _effect(
                "Death Speaker",
                "Intellego",
                "Corpus",
                ("Eye", "Concentration", "Individual"),
                15,
                "Looking into a corpse's eyes, the wearer speaks to its spirit, "
                "much like Whispers Through the Black Gate.",
                uses="24",
                requisites="Mentem",
            ),
            _effect(
                "Shriek of the Impending Shafts",
                "Intellego",
                "Herbam",
                ("Touch", "Diameter", "Hearing"),
                15,
                "As the spell (ArM5 p. 136).",
                uses="24",
            ),
        ],
        opened=15,
        holder=people["philip"],
    )
    for name, effect, charges, words, cost, text in (
        (
            "Morpheus Arrows",
            _effect(
                "Morpheus Arrow",
                "Rego",
                "Mentem",
                ("Touch", "Momentary", "Group"),
                15,
                "Whoever is hit, with his group, falls into a deep sleep.",
            ),
            3,
            "Three arrows.",
            18,
            3,
        ),
        (
            "Fire Arrows",
            _effect(
                "Fire Arrow",
                "Creo",
                "Ignem",
                touch_mom,
                5,
                "Bursts into flame on impact, +5 damage beside the arrow's own, "
                "and sets alight what it hits, +5 a round until put out.",
            ),
            5,
            "Five arrows.",
            10,
            1,
        ),
        (
            "Bridging Arrows",
            _effect(
                "Bridging Arrow",
                "Creo",
                "Herbam",
                ("Touch", "Diameter", "Individual"),
                15,
                "Shot, makes a pace-wide bridge of twisted wood from bow to "
                "arrowfall, up to 100 paces, for up to Size +4.",
            ),
            2,
            "Two arrows.",
            12,
            3,
        ),
    ):
        device = _device(
            b,
            covenant,
            name,
            f"{words} {cost} Build Points.",
            [effect],
            holder=people["william"],
            lab_text=text,
        )
        device.type, device.charges_made = CHARGED, charges


def _property(covenant: Covenant) -> None:
    add_possession(
        covenant,
        "property",
        "The Lion Harbour warehouses and dock",
        location="Miletos",
        description=(
            "Three stone warehouses and a large dock, a Divine aura of 2, let "
            "to merchants, mostly Greek, one at present to a Venetian cartel."
        ),
    )
    add_possession(
        covenant,
        "property",
        "The Delphinion",
        location="Miletos",
        description="Callista's home, behind the warehouses.",
    )


def _vis(covenant: Covenant) -> None:
    for name, art, pawns, season, words in (
        (
            "Arab Market",
            "Muto",
            5,
            "",
            "Callista searches the spices with the Spice Wand; some years it "
            "gives more than 5 pawns. 25 Build Points.",
        ),
        (
            "Harvest of Aftonsitiron",
            "Creo",
            7,
            "",
            "Grogs walk the barley with the Vis Divining Rods. The farmers are "
            "paid a silver coin a pawn, a fabulous price for a handful of "
            "stalks. 35 Build Points.",
        ),
        (
            "Hunt",
            "",
            0,
            "Summer",
            "Faerie animals leave the Sacred Way each summer and Herakles and "
            "William hunt them. Roll two simple dice three times: the first of "
            "each pair gives the Form (1 Animal, 2 Aquam and so on), the "
            "second the pawns, 3 to 30 in all, Faerie tainted. 80 Build Points.",
        ),
        (
            "Mouth of the Meander River",
            "Aquam",
            3,
            "Spring",
            "The first floods of the delta north of Miletos, caught by grogs "
            "with the Vis Net; Ariane predicts them by Intelligence + Artes "
            "Liberales (astronomy) against 6. 15 Build Points.",
        ),
        (
            "Sacred Springs",
            "Intellego",
            13,
            "",
            "One pawn each full moon, which Ariane takes with the Vis Net. 65 "
            "Build Points.",
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
    for art, pawns in (
        ("Creo", 13),
        ("Intellego", 45),
        ("Muto", 12),
        ("Rego", 3),
        ("Animal", 8),
        ("Aquam", 6),
        ("Auram", 1),
        ("Corpus", 7),
        ("Herbam", 13),
        ("Ignem", 8),
        ("Terram", 5),
        ("Vim", 24),
    ):
        add_possession(
            covenant,
            "vis_store",
            f"The coffers: {art}",
            art=art,
            pawns=pawns,
            description=(
                "In chests in the Temple of Athena, a pawn to a bronze coin "
                "stamped with the Art and the Order's glyph; Orion made about "
                "100 of each to hold vis safely, and Ariane usually moves it "
                "in. Some of it is Faerie tainted."
            ),
        )


def _charter(covenant: Covenant) -> None:
    charter = covenant.charter_of_covenant
    charter.preamble = "Drafted by Soteria in 990 from the old ways of the Branchidae."
    charter.clauses = [
        CharterClause(number=str(number), text=text)
        for number, text in enumerate(CHARTER, 1)
    ]


def _history(b: Builder, covenant: Covenant) -> None:
    for year, title, words in (
        (990, "Soteria joins the Order", "Cletus of the Lineage of Pralix finds "
         "the hidden Branchidae and converts them just before the Schism War."),
        (993, "Basil converts", "Soteria's son, at 18."),
        (1013, "Jason's Gauntlet", "Son of Soteria. Cletus leaves this year."),
        (1020, "Orion arrives", "A Verditius of Ingasia, who joins House "
         "Merinita in 1030."),
        (1035, "Brasidas's Gauntlet", "Son of Basil; Final Twilight in 1083."),
        (1040, "Soteria's Final Twilight", "About this year."),
        (1050, "Hector's Gauntlet", "House Merinita."),
        (1053, "Orion vanishes", "Assumed dead."),
        (1075, "Tessa's Gauntlet", "Granddaughter of Jason, Basil's filia. She "
         "leaves for Alexandria in 1105 and for parts unknown in 1140."),
        (1080, "Achillios's Gauntlet", "House Merinita."),
        (1085, "Damen's Gauntlet", "Great-nephew of Jason. He leaves for "
         "Polyaigos in 1116."),
        (1087, "Basil's Final Twilight", ""),
        (1110, "The last Wizard War", "Achillios kills his parens Hector, "
         "nominally over a laboratory with a great forge. Lana arrives from "
         "Aegaea. Achillios leaves for Ingasia in 1111, joins House Verditius, "
         "and meets Final Twilight in 1170."),
        (1112, "Alexander's Gauntlet", "Great-grandson of Jason."),
        (1130, "Jason's Final Twilight", "As the list of magi dates it; he "
         "is given up for lost in 1132, after five solstices' absence."),
        (1132, "Alexander becomes Patriarch", "In his early forties, somehow "
         "keeping his elders Damen and Tessa from returning."),
        (1145, "Nicodemus's Gauntlet", "House Merinita."),
        (1150, "Nikola's Gauntlet", "Niece of Alexander."),
        (1165, "Herakles appears", "A Giant-blooded boy on the Sacred Way."),
        (1172, "Niketas II elected", "Metropolitan of Miletos."),
        (1178, "Lydia's Gauntlet", "Daughter of Nikola."),
        (1179, "Lana's Final Twilight", ""),
        (1180, "Herakles's Gauntlet", ""),
        (1183, "Cora's Gauntlet", "Daughter of Nikola."),
        (1205, "The sea-monsters of Panormos", "Herakles kills the last, and "
         "Lydia and Cora drown; Lydia's body is never found. Ariane comes "
         "from Xylinites."),
        (1207, "Nicodemus's Final Twilight", ""),
        (1210, "William comes to stay", "From Montverte, in Normandy."),
        (1211, "Aoede born", ""),
    ):  # fmt: skip
        b.chronicle(covenant, year, title, words)


def _bite(name: str, init: int, attack: int, defense: int, damage: int) -> Possession:
    return Possession(
        id=storage.generate_unique_id(name, []),
        kind="weapon",
        name=name,
        weapon_init=init,
        weapon_attack=attack,
        weapon_defense=defense,
        weapon_damage=damage,
    )


def _bind(
    b: Builder,
    master: Character,
    creature: Creature,
    name: str,
    species: str,
    trait: str,
    binding: tuple[str, str, int],
    cords: tuple[int, int, int],
    weapons: list[Possession],
) -> None:
    saga = b.saga
    technique, form, total = binding
    golden, silver, bronze = cords
    saga.familiars.append(
        Familiar(
            id=storage.generate_unique_id(name, [f.id for f in saga.familiars]),
            character_id=master.id,
            name=name,
            species=species,
            magic_might=creature.might,
            size=creature.size,
            virtues_flaws=[virtue_flaw_from_block("True Friend")],
            personality_traits=[ScoredTrait(trait, 3)],
            binding_technique=technique,
            binding_form=form,
            binding_lab_total=total,
            golden_cord=golden,
            silver_cord=silver,
            bronze_cord=bronze,
            characteristics=creature.characteristics,
            base_soak=creature.soak,
            natural_weapons=weapons,
        )
    )
    b.link(master, "creatures", creature, "familiar")


def _familiars(b: Builder, people: dict[str, Character]) -> None:
    mileta = b.creature(
        "Mileta",
        page="p. 76",
        realm="Magic",
        might=14,
        form="Animal",
        size=-1,
        season="Summer",
        source=SOURCE,
        confidence=(2, 5),
        block={
            "characteristics": characteristics(1, 3, -2, -5, 0, 2, 2, 3),
            "virtues_flaws": [
                "Magic Animal",
                ("Greater Immunity", {"hazard": "steel weapons"}),
                "Arcane Lore",
                "Improved Characteristics",
                "Self-Confident",
                ("Student of {realm}", {"realm": "Infernal"}),
                ("True Friend", {"detail": "Alexander"}),
                "Unaffected by The Gift",
                "Dark Secret",
                "Magical Monster",
                "Reclusive",
                "Tainted with Evil",
                "Visions",
                ("Greater Power", {"power": "Aura of Rightful Authority"}),
                ("Greater Power", {"power": "Awaken the Slumbering Corpse"}),
                ("Greater Power", {"power": "Shadow Form"}),
                "Gift of Speech",
                ("Improved Attack", {"detail": "grapple"}),
                ("Lesser Power", {"power": "Viper's Gaze"}),
                ("Personal Power", {"power": "Human Shape"}),
                "Ambush Predator",
                "Crafty",
                "Grapple",
                "Keen Sense of Smell",
                "Slippery",
                "Venomous",
            ],
            "traits": {
                "Loyal (Alexander)": 3,
                "Reclusive": 3,
                "Serpent (essential)": 3,
                "Liar": 1,
            },
            "reputations": {
                "Massive snake (local)": 1,
                "Reclusive laboratory assistant (Hermetic)": 1,
            },
            "abilities": [
                ("Artes Liberales", 1, "logic"),
                ("Awareness", 4, "food"),
                ("Brawl", 4, "grapple"),
                ("Concentration", 3, "Viper's Gaze"),
                ("Dead Language: Classical Greek", 5, "Hermetic usage"),
                ("Dead Language: Latin", 3, "Hermetic usage"),
                ("Guile", 4, "magi"),
                ("Hunt", 4, "rats"),
                ("Infernal Lore", 4, "demonic pacts"),
                ("Intrigue", 4, "plotting"),
                ("Living Language: Romaic Greek", 5, "archaic"),
                ("Magic Theory", 6, "inventing spells"),
                ("Organization Lore: Didyma", 4, "history"),
                ("Stealth", 4, "hiding"),
                ("Survival", 3, "water"),
                ("Swim", 5, "stealthily"),
                ("Teaching", 1, "magic theory"),
            ],
        },
        attacks=[
            b.attack("Grapple", 3, 9, 8, None),
            b.attack("Fangs", 3, 9, 8, 1),
        ],
        soak=4,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Aura of Rightful Authority",
                0,
                5,
                "Mentem",
                level=20,
                does="As the spell (ArM5 p. 151). Greater Power, -2 Might Cost, "
                "+4 Init.",
            ),
            b.power(
                "Awaken the Slumbering Corpse",
                0,
                2,
                "Corpus",
                rtd=("Touch", "Sun", ""),
                level=25,
                does="As the spell (ArM5 p. 134). Greater Power, -3 Might Cost, "
                "+2 Init.",
            ),
            b.power(
                "Human Shape",
                1,
                1,
                "Corpus",
                rtd=("Personal", "Sun", "Individual"),
                level=20,
                does="Takes the shape of a tall, skeletal, hairless woman, "
                "fangs and all, of Corpus and Animal Form at once. Personal "
                "Power, -1 Might Cost (RoP: Magic p. 39).",
            ),
            b.power(
                "Shadow Form",
                0,
                1,
                "Animal",
                rtd=("Personal", "Concentration", "Individual"),
                level=30,
                does="In a shadow big enough to hide her she becomes one, +4 "
                "Stealth and proof against physical harm. Greater Power, -3 "
                "Might Cost, +1 Init.",
            ),
            b.power(
                "Viper's Gaze",
                1,
                -3,
                "Animal",
                level=15,
                does="As the spell (ArM5 p. 120), against humans too (Animal "
                "and Corpus). Lesser Power, -2 Might Cost.",
            ),
            b.power(
                "Location (both ways)",
                0,
                0,
                "",
                does="Invested in the familiar bond (ArM5 p. 105).",
            ),
        ],
        vis=[BodyVis(3, "Animal", "in her venom sac")],
        appearance=(
            "An enormous iridescent snake, 20 feet long and 6 inches through, "
            "or a thin bald woman in a black hooded toga."
        ),
        notes=paragraphs(
            "Alexander's familiar, who hides deep in the Sacred Spring or works "
            "in his laboratory passing as an unGifted Branchidae; few "
            "covenfolk see through that, and fewer know the assistant is the "
            "spring snake. Her fang wound can carry venom, Ease Factor 9, "
            "Incapacitating Wound (ArM5 p. 180). Printed Infernal Lore 4+2.",
            "Bond: Golden +1, Silver +2, Bronze +2, by InMe Lab Total 35.",
        ),
        secrets=[
            titled(
                "What Mileta was",
                "Mileta was a demon, long before she met Alexander, changed "
                "into a creature of Magic she knows not how, perhaps by "
                "miracle or lost magic; she feels no loyalty to Hell, and she "
                "may only be deluded.",
            ),
            titled(
                "Proving Mileta",
                "No Hermetic magic can prove Mileta is no demon, only that a "
                "Demon's Eternal Oblivion did not affect her.",
            ),
            titled("Storyguide Notes", "Mileta's past is her Dark Secret."),
        ],
    )
    _bind(
        b,
        people["alexander"],
        mileta,
        "Mileta",
        "An enormous iridescent snake, a magical beast",
        "Loyal (Alexander)",
        ("Intellego", "Mentem", 35),
        (1, 2, 2),
        [_bite("Fangs", 3, 9, 8, 1)],
    )
    chloris = b.creature(
        "Chloris the Curious",
        page="p. 80",
        realm="Magic",
        might=12,
        form="Animal",
        size=-3,
        season="Summer",
        source=SOURCE,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(0, 1, -2, -4, -7, 0, 3, 4),
            "virtues_flaws": [
                "Magical Friend",
                "Magic Animal",
                "Perfect Balance",
                vf_puissant("Awareness"),
                "Second Sight",
                "Sharp Ears",
                ("Social Contacts", {"group": "cats of Miletos"}),
                ("True Friend", {"detail": "Ariane"}),
                "Unaffected by The Gift",
                "Curse of Venus",
                "Meddler (Major)",
                ("Compulsion (Minor)", {"detail": "curiosity"}),
                "Nocturnal",
                ("Lesser Power", {"power": "Prying Eyes"}),
                ("Lesser Power", {"power": "Whispers Through the Black Gate"}),
                ("Personal Power", {"power": "Cat's Leap"}),
                ("Personal Power", {"power": "Eyes for Power, twice"}),
                ("Personal Power", {"power": "Leap of Homecoming, twice"}),
                "Ambush Predator",
                "Crafty",
                "Good Jumper",
                "Skilled Climber",
                "Thick Fur/Thick Scales",
            ],
            "traits": {
                "Meddler": 6,
                "Curious": 4,
                "Cat (essential)": 3,
                "Timid": 2,
            },
            "reputations": {"Pregnant cat (local)": 1},
            "abilities": [
                ("Area Lore: Constantinople", 1, "alleys"),
                ("Area Lore: Miletos", 3, "alleys"),
                ("Athletics", 3, "jump"),
                ("Awareness", 4, "at night"),
                ("Brawl", 2, "claws"),
                ("Carouse", 1, "at night"),
                ("Charm", 1, "tomcats"),
                ("Concentration", 1, "Prying Eyes"),
                ("Dead Language: Classical Greek", 5, "Hermetic usage"),
                ("Dead Language: Latin", 4, "Hermetic usage"),
                ("Hunt", 4, "mice"),
                ("Intrigue", 1, "gossip"),
                ("Leadership", 2, "cats"),
                ("Living Language: Romaic Greek", 5, "rituals"),
                ("Magic Theory", 2, "Intellego"),
                ("Organization Lore: Didyma", 2, "gossip"),
                ("Second Sight", 3, "regio boundaries"),
                ("Stealth", 4, "stalking"),
                ("Survival", 2, "urban"),
            ],
        },
        attacks=[
            b.attack("Claws", 3, 8, 10, -5),
            b.attack("Teeth", 4, 8, 7, -6),
        ],
        soak=3,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Cat's Leap",
                0,
                2,
                "Animal",
                rtd=("Personal", "", ""),
                level=15,
                does="An Animal version of Gift of the Frog's Legs (ArM5 p. "
                "134). Personal Power, -2 Might Cost.",
            ),
            b.power(
                "Eyes for Power",
                0,
                6,
                "Vim",
                rtd=("Personal", "Constant", "Vision"),
                level=20,
                does="She sees vis. Personal Power twice, -2 Might Cost, +4 Init.",
            ),
            b.power(
                "Leap of Homecoming",
                1,
                0,
                "Animal",
                level=35,
                does="An Animal version of the spell (ArM5 p. 135). Personal "
                "Power twice, -3 Might Cost.",
            ),
            b.power(
                "Mental Communication (both ways)",
                0,
                0,
                "",
                does="Invested in the familiar bond (ArM5 p. 105).",
            ),
            b.power(
                "Prying Eyes",
                0,
                5,
                "Imaginem",
                level=5,
                does="As the spell (ArM5 p. 144). Lesser Power, -1 Might Cost, "
                "+3 Init.",
            ),
            b.power(
                "Whispers Through the Black Gate",
                1,
                -2,
                "Corpus",
                level=15,
                does="As the spell (ArM5 p. 130), -2 Might Cost.",
            ),
        ],
        vis=[BodyVis(3, "Animal", "in her eyes")],
        equipment=(
            "A leather collar stamped with Ariane's sigil and studded with tiny "
            "stones, each a fixed Arcane Connection: three points on the Sacred "
            "Way (the covenant end, the Panormos turning, two miles south of "
            "Miletos), the Delphinion, the Lion Gate, and an alley by "
            "Xylinites. There is room for six more."
        ),
        appearance="A small, harmless-looking tortoiseshell cat.",
        notes=paragraphs(
            "Ariane's familiar, a patient, wayward watcher from dark corners "
            "who tells her mistress of visitors when she pleases and may go "
            "off for seasons. The Curse of Venus keeps her chased by tomcats, "
            "pregnant or nursing; many of Miletos's cats are hers, some "
            "perhaps magical, and she likes the Delphinion for her litters.",
            "Bond: Golden +1, Silver +1, Bronze +2, by InAn Lab Total 26.",
        ),
    )
    _bind(
        b,
        people["ariane"],
        chloris,
        "Chloris the Curious",
        "A tortoiseshell cat, a magical beast",
        "Loyal (Ariane)",
        ("Intellego", "Animal", 26),
        (1, 1, 2),
        [_bite("Claws", 3, 8, 10, -5), _bite("Teeth", 4, 8, 7, -6)],
    )
    torvus = b.creature(
        "Torvus",
        page="p. 82",
        realm="Magic",
        might=12,
        form="Auram",
        size=-3,
        season="Summer",
        source=SOURCE,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(0, 3, -1, 0, -6, -1, 1, 6),
            "virtues_flaws": [
                "Magical Friend",
                "Magic Animal",
                "Educated",
                "Keen Vision",
                ("True Friend", {"detail": "William"}),
                "Unaffected by The Gift",
                "Avaricious (Major)",
                "Blackmail",
                "Fragile Constitution",
                ("Greater Power", {"power": "The Cloudless Sky Returned"}),
                "Gift of Speech",
                ("Lesser Power", {"power": "Sailor's Foretaste of the Morrow"}),
                ("Personal Power", {"power": "Shriek of the Impending Shafts"}),
                ("Personal Power", {"power": "Sight of the True Form, twice"}),
                "Accomplished Flyer",
                "Fast Flyer",
                "Keen Eyesight",
                "Pursuit Predator",
                "Extra Natural Weapons",
            ],
            "traits": {"Hoarder": 6, "Falcon (essential)": 3},
            "reputations": {"Thief (local)": 2},
            "abilities": [
                ("Area Lore: Constantinople", 1, "from above"),
                ("Area Lore: Normandy", 3, "from above"),
                ("Area Lore: Theban Tribunal", 3, "from above"),
                ("Artes Liberales", 1, "astronomy"),
                ("Athletics", 5, "flight"),
                ("Awareness", 4, "prey"),
                ("Brawl", 2, "talons"),
                ("Code of Hermes", 1, "familiars"),
                ("Dead Language: Latin", 4, "Hermetic usage"),
                ("Guile", 1, "magi"),
                ("Faerie Lore", 2, "traditions"),
                ("Legerdemain", 3, "picking pockets"),
                ("Living Language: Low German", 2, "military usage"),
                ("Living Language: French", 5, "Norman"),
                ("Living Language: Romaic Greek", 2, "Hermetic usage"),
                ("Magic Lore", 2, "monsters"),
                ("Magic Theory", 3, "Auram"),
                ("Organization Lore: Didyma", 1, "structures"),
                ("Stealth", 2, "hiding hoard"),
                ("Survival", 3, "cold"),
            ],
        },
        attacks=[
            b.attack("Talons", 5, 6, 12, -4),
            b.attack("Beak", 6, 6, 9, -5),
        ],
        soak=1,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Location (both ways)",
                0,
                0,
                "",
                does="Invested in the familiar bond (ArM5 p. 105).",
            ),
            b.power(
                "Mental Communication (both ways)",
                0,
                0,
                "",
                does="Invested in the familiar bond (ArM5 p. 105).",
            ),
            b.power(
                "Sailor's Foretaste of the Morrow",
                3,
                2,
                "Auram",
                level=20,
                does="As the spell (ArM5 p. 127). Lesser Power, -1 Might Cost.",
            ),
            b.power(
                "Shriek of the Impending Shafts",
                0,
                4,
                "Herbam",
                level=15,
                does="As the spell (ArM5 p. 136). Personal Power, -2 Might Cost.",
            ),
            b.power(
                "Sight of the True Form",
                0,
                4,
                "Corpus",
                level=30,
                does="The spell at level 15, but constant (ArM5 p. 130). "
                "Personal Power twice, -3 Might Cost, +1 Init.",
            ),
            b.power(
                "The Cloudless Sky Returned",
                4,
                1,
                "Auram",
                level=45,
                does="As the spell (ArM5 p. 128). Greater Power, -1 Might Cost.",
            ),
        ],
        vis=[BodyVis(3, "Auram", "in his tail feathers")],
        appearance="A brown falcon with a three-foot wingspan.",
        notes=paragraphs(
            "William's familiar and his eye for miles around, a thief who "
            "hoards curious things on and under the temple roofs. A fast "
            "flyer, +3 on rolls of speed.",
            "Bond: Golden +1, Silver 0, Bronze +2, by InAu Lab Total 20.",
        ),
        secrets=[
            titled(
                "Torvus's hoard",
                "Papers in Torvus's hoard show the corruption of Miletos's tax "
                "officials, and without William's knowledge he is "
                "blackmailing their head, Leander.",
            ),
        ],
    )
    _bind(
        b,
        people["william"],
        torvus,
        "Torvus",
        "A brown falcon, a magical beast",
        "Loyal (William)",
        ("Intellego", "Auram", 20),
        (1, 0, 2),
        [_bite("Talons", 5, 6, 12, -4), _bite("Beak", 6, 6, 9, -5)],
    )


def _creatures(b: Builder, covenant: Covenant, places: dict[str, Neighbour]) -> None:
    apollo = b.creature(
        "Apollo Didyma",
        page="p. 89",
        realm="Faerie",
        place=places["apollo_temple"],
        source=SOURCE,
        appearance=(
            "He showed himself here in ancient times, but not for centuries, "
            "and seems to dwell at several places in the Faerie realm, "
            "Olympos among them."
        ),
        notes=paragraphs(
            "The aspect of Apollo at Didyma: the covenant's patron and the "
            "source of its prophecies, a powerful faerie, which is a rare "
            "thing in a covenant's patron. The book gives him no Might or "
            "statistics.",
            "He seeks the worship of the pagan gods and the undoing of the "
            "titans' servants. He warns the Branchidae by prophecy, now and "
            "then sends an intermediary down the Sacred Way, may grant "
            "Branchidae Prophecy to others, and calls the Order little but "
            "'the priests of Hermes'.",
            "Branchos, the founder (died about 900 BC), built him the first "
            "shrine, and his daughter was the first oracle; some say he lived "
            "for centuries and joined Apollo's retinue on Olympos.",
        ),
    )
    b.link(covenant, "creatures", apollo, "its patron")
    sphinx = b.creature(
        "Sphinx",
        page="p. 89",
        realm="Faerie",
        might=20,
        form="Auram",
        size=2,
        source=SOURCE,
        how_many="commonly seen on the Sacred Way",
        place=places["sacred_way"],
        block={
            "characteristics": characteristics(2, 2, -1, 1, 4, 2, 1, -2),
            "virtues_flaws": [
                "Increased Faerie Might",
                "Faerie Sight",
                "Faerie Speech",
                ("Lesser Power", {"power": "Hound"}),
                "Hybrid Form",
                "Improved Characteristics",
                ("Personal Power", {"power": "Flight"}),
                ("Personal Power", {"power": "Shriek of the Impending Shafts"}),
                "Narrowly Cognizant",
                "Monstrous Appearance",
                ("Sovereign Ward", {"ward": "one who solves her riddle"}),
                "Wrathful",
                "Visions",
                "Accomplished Flyer",
                "Aggressive",
                "Ambush Predator",
                "Tough Hide",
            ],
            "traits": {"Treacherous": 6},
            "reputations": {"Merciless hunter and riddle teller (local)": 3},
            "abilities": [
                ("Athletics", 5, "flying"),
                ("Awareness", 4, "prey"),
                ("Brawl", 5, "claws"),
                ("Faerie Lore", 5, "riddles"),
                ("Faerie Speech", 5, "riddles"),
                ("Hunt", 4, "prey"),
                ("Stealth", 4, "stalking"),
                ("Survival", 3, "Didyma plain"),
            ],
        },
        attacks=[
            b.attack("Claws", -3, 9, 7, 6),
            b.attack("Grapple", -2, 6, -3, None),
            b.attack("Teeth", -2, 9, 4, 5),
        ],
        soak=4,
        powers=[
            b.power(
                "Faerie Sight",
                0,
                0,
                "",
                does="Tells glamour from the mundane, knows another faerie's "
                "glamour and sees Arcane Connections, and whose they are if "
                "that person is present. Perception + Awareness against the "
                "other's Might / 5 reads a faerie's motives (RoP: Faerie p. 50).",
            ),
            b.power(
                "Faerie Speech",
                0,
                0,
                "",
                does="Speaks the language of her human audience (RoP: Faerie p. 50).",
            ),
            b.power(
                "Flight",
                0,
                0,
                "Auram",
                level=25,
                does="Constant. She flies, carrying a rider or a victim up to "
                "Size +1. Personal Power, two intricacy points to Might Cost.",
            ),
            b.power(
                "Hound",
                1,
                -10,
                "Corpus",
                rtd=("Arcane", "Concentration", ""),
                level=25,
                does="She knows the direction and distance of her quarry. "
                "Lesser Power, one intricacy point.",
            ),
            b.power(
                "Shriek of the Impending Shafts",
                0,
                -4,
                "Herbam",
                level=25,
                does="As the spell (ArM5 p. 136). Personal Power, two "
                "intricacy points.",
            ),
        ],
        vis=[BodyVis(4, "Auram", "in her wings")],
        appearance=(
            "A lion's body with a woman's torso and head growing from it, like "
            "a feline centaur, and the wings of an eagle."
        ),
        notes=(
            "She hunts lone travellers, avoiding groups: she swoops, grapples, "
            "climbs 20 feet each round and drops them, +1 damage for each two "
            "feet fallen (ArM5 p. 181). Her Sovereign Ward: she cannot harm one "
            "who solves her riddle, and must offer one if asked. Herakles and "
            "William hunt sphinxes for vis, and one might be a Merinita's "
            "familiar. If she drinks the sacred water she can have Apollo "
            "Didyma's visions."
        ),
    )
    b.link(places["sacred_way"], "creatures", sphinx, "the commonest faerie here")
    agamenoth = b.creature(
        "Agamenoth",
        page="p. 92",
        realm="Infernal",
        might=40,
        form="Terram",
        size=5,
        source=SOURCE,
        place=places["plain"],
        order="Aerial Powers",
        hierarchy=8,
        weakness="Abhors water: it does him no harm, but he must flee it or "
        "spend a Confidence Point to stay by it for a diameter",
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 0, 3, 0, 10, 4, 1, -1),
            "traits": {"Fury": 6},
            "reputations": {"Demon Prince of Earthquakes (infernal)": 3},
            "abilities": [("Athletics", 5, "leap"), ("Brawl", 10, "fist")],
        },
        attacks=[b.attack("Fist", -1, 12, 10, 10)],
        soak=20,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Coagulation",
                3,
                -1,
                "Terram",
                does="Takes physical form (RoP: The Infernal p. 31), a giant "
                "earth elemental or a coal seam.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does="Appears in dreams (RoP: The Infernal p. 32).",
            ),
            b.power(
                "Lord of Moving Earth",
                0,
                -1,
                "Terram",
                does="Duplicates any named non-ritual Creo, Muto or Rego "
                "Terram spell of ArM5, at a Might Cost of its magnitude.",
            ),
            b.power(
                "Move Through Earth",
                0,
                0,
                "Terram",
                does="Constant. Moves through earth or stone unhindered.",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Whoever sins near him may gain Fury +1 (RoP: The "
                "Infernal p. 31). On any botch roll extra botch dice equal to "
                "the trait; a botch on them is a furious rage (ArM5 p. 54).",
            ),
            b.power(
                "Recalcitrance",
                0,
                0,
                "",
                does="Against any Rego effect or ward, of any realm, his Might "
                "counts as 60. Printed with no Init.",
            ),
            b.power(
                "Stir the Sulfurous Earth",
                10,
                -1,
                "Terram",
                does="An earthquake a mile across, stinking of sulphur, lasting a "
                "simple die of rounds. Each round those in it roll Dexterity + "
                "Athletics against 6 to stay standing. Stone buildings make "
                "one stress roll against the rounds of shaking, +3 if over two "
                "storeys, or fall, for +15 damage inside. It is felt 300 miles "
                "off. He must penetrate the area's Magic Resistance, so an "
                "Aegis normally protects a site.",
            ),
        ],
        vis=[BodyVis(8, "Terram", "in his skin")],
        appearance=(
            "A gigantic black mound of earth and rock, leaking sulphur from "
            "its cracks and forming limbs and heads as it needs, or a pitch "
            "black seam of coal several hundred paces wide and long."
        ),
        notes="Prince of the Moving Earth.",
        secrets=[
            titled(
                "The fall of Didyma's church",
                "Agamenoth brought down the church and monastery at Didyma, "
                "and has since slept as coal under the plain.",
            ),
            titled(
                "Agamenoth wakes",
                "The fall of Constantinople woke Agamenoth, and when he is "
                "fully roused his earthquakes will strike Didyma and Miletos.",
            ),
        ],
    )
    b.link(covenant, "creatures", agamenoth, "sleeps unknown beneath it")
