"""Jardin, a Summer covenant of the Provençal Tribunal near Cahors, as of
1220, in paraphrase of Through the Aegis, chapter three: the covenant, its
six magi and three familiars, its autocrat, turb captain and specialists,
its garden regio and the quest for the Heart's Desire, its laboratories,
library, Lab Texts, vis and device, Belfort du Quercy and the neighbours
it deals with.

Stat blocks are the book's, with the errata's correction to Lexora's Aegis
of the Hearth (level 20); the rest is a summary, not its words. Faith &
Flame does not name Jardin, so its links to the Tribunal's other magi are
this book's."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import catalog, storage
from ...arts import ART_LOOKUP
from ...models import CharterClause, Familiar, InstilledEffect, ScoredTrait
from ...models.books import TEXT_SPELL
from ...models.holdings import Possession
from ...models.world import FULL
from ..builder import (
    Builder,
    StatBlock,
    add_possession,
    arts_from,
    characteristics,
    joined_lines,
    paragraphs,
    secrets,
    titled,
    vf_art,
    vf_great,
    vf_minor,
    vf_puissant,
    virtue_flaw_from_block,
)

if TYPE_CHECKING:
    from ...models import Character, Covenant, Neighbour
    from . import Provence

SOURCE = "TtA"
NAME = "Jardin"
JERBITON = "house_jerbiton"
BJORNAER = "house_bjornaer"
CRIAMON = "house_criamon"
TREMERE = "house_tremere"
TRIANOMA = "house_bonisagus"

JOIA: StatBlock = {
    "characteristics": characteristics(1, -1, 5, 2, -2, 0, 1, 0),
    "size": -1,
    "confidence": (1, 3),
    "warping": (5, 6),
    "apparent_age": 50,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Gentle Gift",
        ("Affinity with {ability}", {"ability": "Charm"}),
        "Educated",
        "Venus' Blessing",
        "Free Expression",
        vf_great("Presence"),
        vf_great("Presence"),
        ("Social Contacts", {"group": "Troubadours"}),
        "Privileged Upbringing",
        ("Deficient Technique", {"art": "Perdo"}),
        "Envied Beauty",
        ("Ability Block", {"detail": "Martial"}),
        ("Higher Purpose (Minor)", {"detail": "save Toulouse from the French"}),
        "Loose Magic",
        "Small Frame",
    ],
    "traits": {"Patriotic": 3, "Romantic": 3, "Vain": 2},
    "reputations": {
        "Beautiful Chatelaine (nobles)": 4,
        "Patroness of Troubadours (troubadours)": 3,
        "Cultured (magi)": 2,
    },
    "abilities": [
        ("Area Lore: County of Toulouse", 3, "nobles"),
        ("Artes Liberales", 4, "astronomy"),
        ("Awareness", 1, "alertness"),
        ("Charm", 4, "troubadours"),
        ("Code of Hermes", 1, "interpreting interfering with mundanes"),
        ("Concentration", 1, "maintaining spells"),
        ("Craft: Gardener", 4, "flowers"),
        ("Craft: Winemaking", 2, "black wines"),
        ("Etiquette", 4, "Toulouse courtly manners"),
        ("Finesse", 1, "creating flowers"),
        ("Folk Ken", 1, "covenfolk"),
        ("Guile", 2, "answering questions"),
        ("Hunt", 1, "hawking"),
        ("Intrigue", 2, "romantic liaisons"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Leadership", 2, "magi"),
        ("Magic Lore", 1, "magical plants"),
        ("Magic Theory", 6, "Mentem"),
        ("Music", 1, "flute"),
        ("Living Language: Occitan", 5, "poetry"),
        ("Organization Lore: Jardin", 2, "history"),
        ("Organization Lore: Order of Hermes", 1, "magi of Provençal"),
        ("Parma Magica", 2, "Mentem"),
        ("Penetration", 1, "Herbam"),
        ("Philosophiae", 1, "natural philosophy"),
        ("Profession: Scribe", 1, "copying"),
        ("Profession: Viticulturist", 2, "care of vines"),
        ("Ride", 1, "horses"),
        ("Teaching", 4, "apprentices"),
    ],
    "past_xp": {
        "Charm": 17,
        "Code of Hermes": 7,
        "Craft: Winemaking": 7,
        "Folk Ken": 6,
        "Guile": 2,
        "Intrigue": 2,
        "Leadership": 2,
        "Magic Theory": 5,
        "Music": 4,
        "Organization Lore: Order of Hermes": 7,
        "Parma Magica": 4,
        "Profession: Viticulturist": 5,
        "Teaching": 11,
    },
    "arts": arts_from(
        "Cr 7, In 5, Mu 5, Pe 7, Re 11, An 5, Aq 5, Au 6, Co 9, He 19, Ig 6, "
        "Im 9, Me 11, Te 5, Vi 11"
    ),
    "spells": [
        ("Soothe the Ferocious Bear", "ReAn", 10, 0),
        ("Gentle Touch of the Purified Body", "CrCo", 20, 0),
        ("Disguise of the New Visage", "MuCo", 15, 1),
        ("Rise of the Feathery Body", "ReCo", 10, 0),
        ("Endurance of the Berserkers", "ReCo", 15, 0),
        ("The Healthy Vine", "CrHe", 5, 0),
        ("The Well Tended Vine", "CrHe", 5, 0),
        ("Create the Flowers of the Moon", "CrHe", 15, 0),
        ("Trap of the Entwining Vines", "CrHe", 15, 0),
        ("Converse with Plant and Tree", "InHe", 25, 0),
        ("Coils of the Entangling Plants", "ReHe", 20, 0),
        ("Ward Against Faeries of the Wood", "ReHe", 25, 0),
        ("The Treacherous Spear", "ReHe", 25, 0),
        ("Freeing the Striding Tree", "ReHe", 30, 0),
        ("Prison of Flames", "MuIg", 20, 0),
        ("Aura of the Ennobled Presence", "MuIm", 10, 0),
        ("Sight of the Transparent Motive", "InMe", 10, 0),
        ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
        ("Calm the Motion of the Heart", "PeMe", 15, 0),
        ("Enchantment of Detachment", "PeMe", 15, 0),
        ("Loss of But a Moment's Memory", "PeMe", 15, 0),
        ("Confusion of the Numbed Will", "ReMe", 15, 0),
        ("The Call to Slumber", "ReMe", 10, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Cool the Lover's Ardor", "ReMe", 20, 0),
        ("Detect the Gift", "InVi", 20, 0),
        ("The Invisible Eye Revealed", "InVi", 15, 0),
        ("Piercing the Magical Veil", "InVi", 20, 0),
        ("Watching Ward", "ReVi", 30, 0),
    ],
    "masteries": {"Disguise of the New Visage": ["Fast Casting"]},
    "notes": paragraphs(
        "A very petite woman whose charms outlast her years, her hair always "
        "flecked with spring blossom. Casting sigil: the delicate perfume of "
        "summer flowers. Twilight Scars: flowers grow where she sleeps; she "
        "smells faintly of summer flowers; blossom appears in her hair. Her "
        "Longevity Ritual gives -6 to aging rolls. Encumbrance 0.",
        "Combat: dodge Init 0, Defense 0; fist Init 0, Attack +1, Defense 0, "
        "Damage -2; gardening trowel Init -1, Attack +2, Defense -1, Damage "
        "-1. Soak 0.",
        "Level of a General spell: Ward Against Faeries of the Wood 25, The "
        "Invisible Eye Revealed 15, Watching Ward 30.",
        "Talisman: an iron gardening trowel with a hazel handle, capacity 20 "
        "pawns, 2 invested, 17 effect levels. Effect: Rope of Bronze (MuHe "
        "17, Pen 0, 3 a day, Touch, Sun, Individual, as ArM5 p. 137). "
        "Attunements: +7 harm or repel faeries, +2 building, +3 divination.",
    ),
}

LEXORA: StatBlock = {
    "characteristics": characteristics(1, 0, 1, 0, 3, 1, 2, 1),
    "confidence": (2, 5),
    "warping": (4, 10),
    "apparent_age": 56,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Animal Ken",
        ("Heartbeast", {"detail": "lioness"}),
        "Improved Characteristics",
        "Improved Characteristics",
        vf_puissant("Brawl"),
        "Reserves of Strength",
        "Self-Confident",
        "Sensory Magic",
        "Subtle Magic",
        "Unbound Tongue",
        "Wilderness Sense",
        "Pagan",
        "Proud",
        ("Weak Magic Resistance", {"detail": "when in human form"}),
        "Weak Enchanter",
    ],
    "traits": {"Proud": 6, "Leonine": 2, "Difficult": 1},
    "reputations": {"Animalistic (magi)": 1},
    "abilities": [
        ("Animal Ken", 1, "predators"),
        ("Area Lore: County of Toulouse", 2, "wilds"),
        ("Artes Liberales", 2, "grammar"),
        ("Athletics", 1, "jumping"),
        ("Awareness", 3, "smell"),
        ("Brawl", 3, "dodge"),
        ("Code of Hermes", 1, "Certamen"),
        ("Concentration", 1, "maintaining effects"),
        ("Craft: Woodworking", 1, "figurines"),
        ("Hunt", 1, "falconry"),
        ("Etiquette", 3, "pulling rank"),
        ("Finesse", 1, "targeting"),
        ("Heartbeast", 2, "transforming back"),
        ("Dead Language: Latin", 4, "writing"),
        ("Leadership", 2, "Jardin"),
        ("Magic Lore", 1, "Greek myths"),
        ("Magic Theory", 5, "Animal"),
        ("Living Language: Occitan", 5, "courtly"),
        ("Organization Lore: House Bjornaer", 4, "Initiating self"),
        ("Organization Lore: Jardin", 2, "politics"),
        ("Organization Lore: Order of Hermes", 1, "Bjornaer"),
        ("Parma Magica", 4, "Mentem"),
        ("Penetration", 2, "Ignem"),
        ("Philosophiae", 1, "rituals"),
        ("Profession: Scribe", 2, "copying"),
        ("Stealth", 1, "stalking"),
        ("Survival", 1, "forest"),
        ("Swim", 1, "rivers"),
        ("Teaching", 3, "apprentices"),
        ("Wilderness Sense", 1, "mountains"),
    ],
    "past_xp": {
        "Area Lore: County of Toulouse": 2,
        "Brawl": 6,
        "Code of Hermes": 7,
        "Craft: Woodworking": 4,
        "Etiquette": 6,
        "Heartbeast": 12,
        "Leadership": 10,
        "Magic Theory": 5,
        "Organization Lore: Jardin": 5,
        "Organization Lore: Order of Hermes": 7,
        "Parma Magica": 1,
        "Penetration": 8,
        "Teaching": 3,
        "Wilderness Sense": 2,
    },
    "arts": arts_from(
        "Cr 5, In 5, Mu 5, Pe 9, Re 12, An 17, Aq 5, Au 6, Co 10, He 5, Ig 6, "
        "Im 7, Me 10, Te 5, Vi 9"
    ),
    "spells": [
        ("True Rest of the Injured Brute", "CrAn", 20, 0),
        ("Shiver of the Lycanthrope", "InAn", 10, 0),
        ("The Fur That Turns Blades", "MuAn", 15, 0),
        ("Lion of Outlandish Size", "MuAn", 15, 0),
        ("Transformation of the Ravenous Beast to the Torpid Toad", "MuAn", 25, 0),
        ("The Gentle Beast", "ReAn", 25, 0),
        ("Mastering the Unruly Beast", "ReAn", 25, 0),
        ("Commanding the Harnessed Beast", "ReAn", 30, 0),
        ("The Lamb Lies Down With the Lion", "ReAn", 30, 0),
        ("The Inexorable Search", "InCo", 20, 0),
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("Endurance of the Lion", "ReCo", 20, 0),
        ("The Gift of Vigor", "ReCo", 20, 0),
        ("Breath of Flames", "CrIg", 20, 0),
        ("The Invisible Predator", "PeMe", 30, 0),
        ("The Roar That Induces Terror", "CrMe", 20, 0),
        ("Aura of Regal Authority", "ReMe", 30, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
        ("Aegis of the Hearth", "ReVi", 20, 0),
    ],
    "notes": paragraphs(
        "A rough mane of uncontrollable blonde hair, brown eyes and a courtly "
        "gown. Casting sigil: warm sunlight; under Intellego Vim her spells "
        "wear a dazzling golden aura, and what they touch may feel warm or "
        "look brighter. Twilight Scars: she can eat only raw meat; she seems "
        "to grow when angry; her hair is a wild mane. Her Longevity Ritual "
        "gives -6 to aging rolls. Encumbrance 0.",
        "Combat: dodge Init +1, Defense +7; fist Init +1, Attack +7, Defense "
        "+6, Damage +3; kick Init 0, Attack +7, Defense +5, Damage +6. Soak "
        "+1.",
        "Level of a General spell: Gather the Essence of the Beast 15, Aegis "
        "of the Hearth 20 (the errata's correction of the 15 printed). The "
        "book lists Fur That Turns Blades at 15 and Endurance of the Lion as "
        "ReCo in her block; their own entries give MuAn 20 and ReAn 20.",
        "Sensory Magic: Sound and Spectacle are Targets from that Mystery "
        "(Sound, all who hear the caster; Spectacle, all who see her), which "
        "only those Initiated can design or cast.",
        "Lioness form, Size +2: Int +1, Per 0, Pre +1, Com 0, Str +6, Sta +3, "
        "Dex +2, Qik +1. The shape adds Ferocity (self-defense), Tough and "
        "Weakness (submission). Qualities: Aggressive, Ambush Predator, "
        "Crafty, Good Jumper, Hardy, Imposing Appearance, Large Claws, Large "
        "Teeth, Tough Hide, Vocal. Claws Init +1, Attack +15, Defense +12, "
        "Damage +10; bite Init +1, Attack +13, Defense +9, Damage +9. Soak +8 "
        "(+2 from Tough Hide). Fatigue OK, 0/0, -1, -3, -5, Unconscious. "
        "Changed Abilities: Area Lore: County of Toulouse 1 (7) (wilds), "
        "Athletics 5 (pouncing), Awareness 2 (smell), Brawl 5+2 (1) (claws), "
        "Hunt 4 (deer), Stealth 4 (stalking), Survival 5 (arid climates). "
        "Weak Magic Resistance does not apply in this form. Add 2 to her "
        "casting totals in it, from Stamina.",
        "With Lion of Outlandish Size she is Size +3, Str +8, Qik 0: claws "
        "Init +1, Attack +15, Defense +11, Damage +12; bite Init +1, Attack "
        "+13, Defense +8, Damage +11.",
    ),
}

XENOPHANES: StatBlock = {
    "characteristics": characteristics(-3, 2, 0, 0, 0, 3, 0, 0),
    "aging_points": {"stamina": 2},
    "confidence": (1, 3),
    "decrepitude": (0, 3),
    "warping": (6, 23),
    "apparent_age": 61,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Elemental Magic",
        "Gentle Gift",
        "Adept Laboratory Student",
        "Book Learner",
        "Free Expression",
        "Inspirational",
        "Inventive Genius",
        "Life Boost",
        "The Enigma",
        "Quiet Magic",
        "Skilled Parens",
        "Subtle Magic",
        ("True Friend", {"detail": "Hypatia"}),
        "Overconfident",
        "Pious",
        "Short-Ranged Magic",
        "Disjointed Magic",
        "Nocturnal",
        "Noncombatant",
        ("Social Handicap", {"detail": "unworldly"}),
        ("Vow (Minor)", {"detail": "help the injured"}),
        "Weak Characteristics",
    ],
    "traits": {
        "Pious": 6,
        "Overconfident": 6,
        "Compassionate": 3,
        "Loyal to Hypatia": 3,
    },
    "reputations": {"Weird Ascetic (magi)": 2},
    "abilities": [
        ("Animal Handling", 1, "cats"),
        ("Artes Liberales", 1, "grammar"),
        ("Athletics", 3, "running"),
        ("Awareness", 3, "by moonlight"),
        ("Charm", 3, "Cathars"),
        ("Climb", 1, "retrieve cat from tree"),
        ("Concentration", 5, "meditation"),
        ("Craft: Gardener", 3, "mazes"),
        ("Enigmatic Wisdom", 7, "interpreting omens"),
        ("Etiquette", 2, "knowing my place"),
        ("Finesse", 2, "fast casting"),
        ("Folk Ken", 3, "peasants"),
        ("Living Language: High German", 5, "Alpine"),
        ("Dead Language: Latin", 5, "writing"),
        ("Magic Lore", 3, "legends"),
        ("Magic Theory", 6, "familiars"),
        ("Living Language: Occitan", 3, "rustic"),
        ("Organization Lore: Cathar Church", 2, "Toulouse diocese"),
        (
            "Organization Lore: House Criamon",
            6,
            "Initiating in Path of Walking Backwards",
        ),
        ("Organization Lore: Jardin", 2, "The Garden of Love"),
        ("Parma Magica", 1, "Ignem"),
        ("Penetration", 1, "Vim"),
        ("Profession: Scribe", 1, "copying"),
        ("Survival", 3, "foraging"),
        ("Swim", 3, "rivers"),
        ("Teaching", 4, "cats"),
        ("Theology: Cathar", 3, "debating"),
    ],
    "past_xp": {
        "Charm": 8,
        "Craft: Gardener": 12,
        "Enigmatic Wisdom": 6,
        "Etiquette": 4,
        "Magic Theory": 11,
        "Living Language: Occitan": 13,
        "Organization Lore: Jardin": 4,
        "Parma Magica": 1,
        "Theology: Cathar": 4,
    },
    "arts": arts_from(
        "Cr 11, In 8, Mu 5, Pe 11, Re 9, An 9, Aq 13, Au 9, Co 7, He 6, Ig 8, "
        "Im 7, Me 5, Te 11, Vi 16"
    ),
    "spells": [
        ("Air's Ghostly Form", "CrAu", 5, 0),
        ("Jupiter's Resounding Blow", "CrAu", 10, 0),
        ("Stench of the Twenty Corpses", "CrAu", 10, 0),
        ("Charge of the Angry Winds", "CrAu", 15, 0),
        ("Mighty Torrent of Water", "CrAq", 20, 0),
        ("Clear Sight of the Naiad", "InAq", 5, 0),
        ("Subtle Taste of Poison and Purity", "InAq", 5, 0),
        ("Call of the Rushing Waters", "InAq", 15, 0),
        ("Comfort of the Drenched Traveler", "PeAq", 5, 0),
        ("Cloak of the Duck's Feathers", "ReAq", 5, 0),
        ("Breath of Winter", "ReAq", 15, 0),
        ("The Chirurgeon's Healing Touch", "CrCo", 20, 0),
        ("Physician's Eye", "InCo", 5, 0),
        ("Revealed Flaws of Mortal Flesh", "InCo", 10, 0),
        ("Touch of the Goose Feather", "PeCo", 5, 0),
        ("Curse of the Unruly Tongue", "ReCo", 5, 0),
        ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
        ("Rise of the Feathery Body", "ReCo", 10, 0),
        ("Endurance of the Berserkers", "ReCo", 15, 0),
        ("The Healthy Vine", "CrHe", 5, 0),
        ("Converse with Plant and Tree", "InHe", 25, 0),
        ("Moonbeam", "CrIg", 3, 0),
        ("Charm Against Putrefaction", "CrCo", 10, 0),
        ("Heat of the Searing Forge", "CrIg", 10, 0),
        ("Lamp Without Flame", "CrIg", 10, 0),
        ("Tales of the Ashes", "InIg", 5, 0),
        ("Hornet Fire", "MuIg(Re)", 10, 0),
        ("Aura of the Ennobled Presence", "MuIm", 10, 0),
        ("Eyes of the Eons", "InTe", 10, 0),
        ("Supple Iron and Rigid Rope", "MuTe", 10, 0),
        ("The Unseen Porter", "ReTe", 10, 0),
        ("Detect the Gift", "InVi", 15, 0),
        ("The Invisible Eye Revealed", "InVi", 15, 0),
        ("Piercing the Magical Veil", "InVi", 20, 0),
        ("Demon's Eternal Oblivion", "PeVi", 10, 0),
        ("Disenchant", "PeVi", 25, 0),
        ("Aegis of the Hearth", "ReVi", 20, 0),
        ("Watching Ward", "ReVi", 25, 0),
    ],
    "notes": paragraphs(
        "A white-haired, ruddy man in bright peasant clothes, boots, leather "
        "gloves and a wide-brimmed hat, with a scarf to hide the tattoos on "
        "his neck; fifteen tattoos cover him in all. Casting sigil: a soft "
        "feeling of bliss, which even things his spells touch seem to share. "
        "Twilight Scars: his tattoos writhe and change; a leaf or blade of "
        "grass in his hair comes back whenever removed; cats befriend him at "
        "once; people feel calm near him; he purrs loudly in his sleep; vis "
        "on his person crackles and glows. His Longevity Ritual gives -6 to "
        "aging rolls, -5 in his unhealthy laboratory. Encumbrance 0.",
        "Combat: dodge Init 0, Defense 0. Soak +3. He carries a small bronze sickle.",
        "From the Path of Walking Backwards (Houses of Hermes: Mystery Cults "
        "pp. 70-71): Gentle Gift from the Avenue of Surrender and the Station "
        "of Service to Harmony; Pious and Vow from the Avenue of Healing and "
        "the Station of Rice and Honey; Free Expression and Inspirational "
        "from the Avenue of Adulation and the Station of Expression, by which "
        "Enigmatic Wisdom can replace Craft: Flower Arranging.",
        "Level of a General spell: Disenchant 25, Demon's Eternal Oblivion "
        "10, The Invisible Eye Revealed 15, Aegis of the Hearth 20, Watching "
        "Ward 25. The book calls The Healthy Vine Health of the Vine here, "
        "and lists Detect the Gift at 15 here and at 20 under Joia.",
        "Talisman: a small bronze sickle, 7 pawns invested, 60 effect levels. "
        "Effects: Well Without Light (PeIg 25, Pen 0, 1 a day, Touch, Sun, "
        "Structure, ArM5 p. 142); Break the Hard Soil (ReTe 7, Pen 0, 6 a "
        "day, Touch, Momentary, Part: readies a circle of soil 15 paces "
        "across); Beckoning in the Unwelcome Twilight (CrVi 25, Pen +20, 1 a "
        "day, Touch, Momentary, Individual: two Warping Points to the one "
        "touched, and a Twilight roll for a magus). Attunements: +3 Terram, "
        "+5 Darkness, +2 Harvesting. These bonuses are in the book's totals "
        "for his Terram spells.",
    ),
}

BEATRIZ: StatBlock = {
    "characteristics": characteristics(1, -1, -1, 3, 1, 1, -2, 0),
    "aging_points": {"stamina": 1},
    "decrepitude": (0, 1),
    "warping": (3, 12),
    "apparent_age": 41,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Gentle Gift",
        "Adept Laboratory Student",
        vf_art("Affinity with {art}", "Imaginem"),
        "Educated",
        "Harnessed Magic",
        ("Minor Magical Focus", {"focus": "changing own appearance"}),
        ("Social Contacts", {"group": "Troubadours"}),
        ("Deficient Technique", {"art": "Perdo"}),
        "Low Self-Esteem",
        "Depressed",
        "Weak Characteristics",
    ],
    "traits": {"Depressed": 3, "Stubborn": 2, "Bitter": 1},
    "reputations": {
        "Moody (troubadours)": 2,
        "Victim of the Garden (Jardin)": 3,
    },
    "abilities": [
        ("Area Lore: County of Toulouse", 1, "troubadours"),
        ("Artes Liberales", 4, "astronomy"),
        ("Awareness", 1, "alertness"),
        ("Carouse", 1, "hard drinking"),
        ("Code of Hermes", 1, "apprentices"),
        ("Concentration", 1, "maintaining spells"),
        ("Etiquette", 2, "Toulouse courtly manners"),
        ("Finesse", 1, "creating images"),
        ("Living Language: French", 5, "poetry"),
        ("Dead Language: Latin", 5, "Hermetic usage"),
        ("Magic Lore", 1, "lycanthropes"),
        ("Magic Theory", 5, "Imaginem"),
        ("Music", 2, "flute"),
        ("Organization Lore: Jardin", 2, "history"),
        ("Organization Lore: Order of Hermes", 1, "magi of Provençal"),
        ("Parma Magica", 1, "Mentem"),
        ("Penetration", 1, "Corpus"),
        ("Philosophiae", 1, "natural philosophy"),
        ("Profession: Scribe", 1, "copying"),
        ("Teaching", 2, "magi"),
    ],
    "past_xp": {
        "Artes Liberales": 8,
        "Code of Hermes": 7,
        "Etiquette": 1,
        "Magic Theory": 20,
        "Music": 1,
        "Organization Lore: Order of Hermes": 7,
        "Teaching": 5,
    },
    "arts": arts_from(
        "Cr 9, In 6, Mu 5, Pe 5, Re 8, An 3, Aq 3, Au 4, Co 5, He 4, Ig 4, "
        "Im 14, Me 7, Te 3, Vi 10"
    ),
    "spells": [
        ("Disguise of the Putrid Aroma", "ReAn", 5, 0),
        ("Soothe the Ferocious Bear", "ReAn", 10, 0),
        ("Viper's Gaze", "ReAn", 15, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Sight of the True Form", "InCo", 10, 0),
        ("Rise of the Feathery Body", "ReCo", 10, 0),
        ("Endurance of the Berserkers", "ReCo", 15, 0),
        ("Conjure the Sturdy Vine", "CrHe", 5, 0),
        ("Hunt for the Wild Herb", "InHe", 5, 0),
        ("Phantasm of the Human Form", "CrIm", 25, 0),
        ("Discern Own Illusions", "InIm", 15, 0),
        ("Taste of the Spices and Herbs", "MuIm", 5, 0),
        ("Aura of the Ennobled Presence", "MuIm", 10, 0),
        ("Disguise of the Transformed Image", "MuIm", 15, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Removal of the Conspicuous Sigil", "PeIm", 20, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "notes": paragraphs(
        "A plain woman who wears her dark hair in a severe bun, never smiles, "
        "and changes her looks by magic as her mood shifts. Casting sigil: an "
        "absence of red, drained from all her spells touch; she cannot create "
        "true red by magic, though ruddy skin is allowed. Twilight Scars: her "
        "reflection never quite matches her; red things fade at her touch. "
        "Her Longevity Ritual gives -5 to aging rolls. Encumbrance 0 (burden "
        "1).",
        "Combat: dodge Init 0, Defense 0; fist Init 0, Attack -2, Defense 0, "
        "Damage +1; kick Init -1, Attack -2, Defense -1, Damage +4; short "
        "sword Init +1, Attack +1, Defense +1, Damage +6. Soak +1.",
        "Level of a General spell: Sight of the True Form 10, Gather the "
        "Essence of the Beast 15.",
        "Talisman: a simple wooden necklace with an amber bead carved with a "
        "crown, worn at all times, 7 pawns invested, 54 effect levels. "
        "Effects: The Ever Changing Guise (MuIm 14, Pen 0, 12 a day, "
        "Personal, Sun, Individual, as Disguise of the New Visage; outside "
        "the covenant she never appears as herself, and she spares the night "
        "and her sanctum, so it does not warp her); The Invisible Eye "
        "Revealed (InVi 25, Pen 0, 1 a day, Personal, Concentration, Touch, "
        "shows scrying up to level 50); Whispers Through The Black Gate "
        "(InCo(Me) 15, Pen 0, 1 a day, Touch, Concentration, Individual). "
        "Attunements: +3 Corpus, +4 affect breathing and speaking, +4 affect "
        "dead wood. These bonuses are in the book's totals for her spells "
        "marked T: Bind Wound, Sight of the True Form, Rise of the Feathery "
        "Body, Endurance of the Berserkers, Conjure the Sturdy Vine.",
    ),
}

AHENOBARBUS: StatBlock = {
    "characteristics": characteristics(3, 0, 0, 1, 0, 2, 1, -1),
    "aging_points": {"stamina": 1},
    "confidence": (1, 3),
    "decrepitude": (0, 1),
    "warping": (5, 5),
    "apparent_age": 34,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Cautious Sorcerer",
        ("Deft Form", {"form": "Mentem"}),
        "Improved Characteristics",
        "Inventive Genius",
        ("Minor Magical Focus (House)", {"focus": "certamen"}),
        vf_art("Puissant {art}", "Mentem"),
        vf_puissant("Leadership"),
        vf_art("Puissant {art}", "Rego"),
        "Unaging",
        ("True Friend", {"detail": "Nec"}),
        "Ambitious",
        "Feud",
        "Loose Magic",
        "Proud (Minor)",
    ],
    "traits": {
        "Ambitious": 6,
        "Proud": 3,
        "Loyal to Nec": 3,
        "Loyal to Coeris": 2,
    },
    "reputations": {"Hoplite (Order of Hermes)": 1},
    "abilities": [
        ("Artes Liberales", 1, "rhetoric"),
        ("Area Lore: Transylvania", 3, "House Tremere"),
        ("Athletics", 1, "jumping"),
        ("Awareness", 2, "clues"),
        ("Bargain", 3, "information"),
        ("Brawl", 3, "dodging"),
        ("Code of Hermes", 3, "Wizards' War"),
        ("Concentration", 3, "maintaining spells"),
        ("Finesse", 3, "Terram"),
        ("Guile", 2, "spur of the moment"),
        ("Intrigue", 3, "plots"),
        ("Dead Language: Latin", 5, "academic terms"),
        ("Leadership", 3, "soldiers"),
        ("Magic Theory", 6, "Mentem"),
        ("Organization Lore: Church", 3, "church officials"),
        ("Organization Lore: Order of Hermes", 2, "outlaw wizards"),
        ("Parma Magica", 3, "Mentem"),
        ("Penetration", 4, "Mentem"),
        ("Profession: Scribe", 3, "copying"),
        ("Profession: Notary", 4, "court cases"),
        ("Living Language: South Slavonic", 5, "Bulgarian dialect"),
    ],
    "arts": arts_from(
        "Cr 7, In 6, Mu 6, Pe 6, Re 20+3, An 5, Aq 5, Au 5, Co 12, He 5, Ig 5, "
        "Im 5, Me 20+3, Te 12, Vi 5"
    ),
    "spells": [
        ("Mighty Viper's Gaze", "ReAn", 20, 0),
        ("Endurance of the Berserkers", "ReCo", 15, 0),
        ("Lifting the Dangling Puppet", "ReCo", 15, 0),
        ("Awaken the Slumbering Corpse", "ReCo", 25, 0),
        ("The Leap of Homecoming", "ReCo", 35, 2),
        ("Coils of the Entangling Plants", "ReHe", 20, 0),
        ("Ward Against Heat and Flames", "ReIg", 25, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
        ("The Call to Slumber", "ReMe", 10, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Coerce the Spirits of the Night", "ReMe", 20, 0),
        ("Enslave the Mortal Mind", "ReMe", 40, 0),
        ("The Shrouded Glen", "ReMe", 45, 0),
        ("Wielding the Invisible Sling", "ReTe", 10, 0),
        ("The Tremere Trench", "ReTe", 25, 0),
        ("Watching Ward", "ReVi", 20, 0),
    ],
    "masteries": {"The Leap of Homecoming": ["Fast Casting", "Still Casting"]},
    "notes": paragraphs(
        "Casting sigil: zig-zag lines; even his Circle spells show jagged "
        "edges under Intellego Vim, and his earthworks zig-zag sharply. "
        "Twilight Scar: people feel slightly awed after talking to him. His "
        "Longevity Ritual gives -6 to aging rolls. He wears wizardly robes. "
        "Encumbrance 0.",
        "Combat: dodge Init -1, Defense +3; kick Init -2, Attack +4, Defense "
        "+1, Damage +3; dagger Init -1, Attack +7, Defense +3, Damage +3. "
        "Soak +2.",
        "Mighty Viper's Gaze is Viper's Gaze raised a magnitude for animals "
        "up to Size +4. The book lists The Tremere Trench at 25 in his block "
        "and 20 in its entry, and The Shrouded Glen at 45. Level of a General "
        "spell: Watching Ward 20.",
        "Talisman: a wand tipped with amber, with a hollow in the handle for "
        "an Arcane Connection to his laboratory, 9 pawns invested, 86 effect "
        "levels. Effects: The Touch Of Morpheus (ReMe 47, Pen +64, 24 a day, "
        "Touch, Sun, Individual, a Touch version of The Call to Slumber); "
        "Take Me Home! (ReCo 39, Pen +8, 1 a day, Personal, Momentary, "
        "Individual, as The Leap of Homecoming). Attunements: wand +4 control "
        "things at a distance; amber +3 Corpus. These bonuses are in the "
        "book's totals for his spells marked T: all his Corpus, Herbam, "
        "Terram and Rego Mentem spells but Aura of Rightful Authority and The "
        "Shrouded Glen, and Mighty Viper's Gaze.",
        "The Collars of Slavery: two small iron collars, invested devices of "
        "Enslave the Mortal Mind (ReMe 44, Pen 0, 2 a day, Environmental "
        "Trigger, Touch, Sun, Individual). The wearer has no will of his own "
        "and takes any suggestion, and remembers it all once freed. One is "
        "for captives, who then lose the memory to his spells; the other he "
        "may give to Protendus.",
    ),
}

ALYSSA: StatBlock = {
    "characteristics": characteristics(3, 1, 1, 1, 0, 1, 0, 0),
    "size": -1,
    "confidence": (2, 5),
    "warping": (4, 2),
    "apparent_age": 44,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Gentle Gift",
        ("Cyclic Magic (Positive)", {"detail": "spring and summer"}),
        "Improved Characteristics",
        vf_art("Puissant {art}", "Corpus"),
        vf_puissant("Intrigue"),
        "Self-Confident",
        ("True Friend", {"detail": "Fauconrouge"}),
        "Well-Traveled",
        "Meddler (Major)",
        "Close Family Ties",
        "Optimistic (Minor)",
        "Susceptibility to Faerie Power",
        "Small Frame",
        "Unpredictable Magic",
    ],
    "traits": {
        "Meddler": 6,
        "Optimistic": 3,
        "Loyal to Fauconrouge": 3,
        "Compassionate": 1,
    },
    "reputations": {
        "Educated noble (Nobles)": 2,
        "Trouble on two legs (Order of Hermes)": 2,
    },
    "abilities": [
        ("Animal Handling", 1, "falcons"),
        ("Living Language: Arabic", 3, "Iberian"),
        ("Area Lore: Toulouse", 3, "magi"),
        ("Area Lore: Provence", 2, "nobility"),
        ("Artes Liberales", 3, "astronomy"),
        ("Athletics", 1, "climbing"),
        ("Awareness", 2, "magic"),
        ("Bargain", 1, "trading favors"),
        ("Brawl", 2, "dodging"),
        ("Carouse", 1, "nobles"),
        ("Charm", 3, "nobles"),
        ("Code of Hermes", 4, "interfering with mundanes"),
        ("Concentration", 2, "maintaining spells"),
        ("Etiquette", 2, "nobles"),
        ("Finesse", 3, "Rego craft magic"),
        ("Folk Ken", 3, "detecting lies"),
        ("Guile", 3, "complex lies"),
        ("Intrigue", 5, "scheming"),
        ("Dead Language: Latin", 5, "academic terms"),
        ("Leadership", 2, "magi"),
        ("Magic Theory", 5, "Corpus"),
        ("Living Language: Occitan", 5, "nobles"),
        ("Organization Lore: Order of Hermes", 2, "covenants"),
        ("Parma Magica", 5, "Ignem"),
        ("Penetration", 2, "Corpus"),
        ("Philosophiae", 2, "ritual magic"),
        ("Profession: Scribe", 1, "copying"),
        ("Ride", 2, "riding fast"),
    ],
    "arts": arts_from(
        "Cr 5, In 5, Mu 5, Pe 5, Re 15, An 9, Aq 0, Au 0, Co 17+3, He 0, Ig 0, "
        "Im 5, Me 5, Te 5, Vi 5"
    ),
    "spells": [
        ("Panic of the Elephant's Mouse", "ReAn", 15, 0),
        ("Bind Wound", "CrCo", 10, 0),
        ("Cheating the Reaper", "CrCo", 30, 0),
        ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
        ("The Inexorable Search", "InCo", 20, 0),
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("The Mistaken Step", "ReCo", 30, 0),
        ("Seven League Stride", "ReCo", 30, 0),
        ("The Leap of Homecoming", "ReCo", 35, 0),
        ("Aura of the Ennobled Presence", "MuIm", 10, 0),
        ("Wizard's Sidestep", "ReIm", 10, 0),
        ("Confusion of the Numbed Will", "ReMe", 15, 0),
        ("Trackless Step", "ReTe", 10, 0),
        ("The Unseen Porter", "ReTe", 10, 0),
        ("Wielding the Invisible Sling", "ReTe", 10, 0),
        ("Scales of the Magical Weight", "InVi", 5, 0),
        ("Circle of Protection against Demons", "ReVi", 10, 0),
        ("Gather the Essence of the Beast", "ReVi", 15, 0),
    ],
    "notes": paragraphs(
        "A petite woman of almost childlike looks, with a kind smile and "
        "hazel hair and eyes. She travels in practical men's clothes and "
        "around the covenant wears a tatty black cloak and a peacock-feathered "
        "hat over a peasant's dress. Casting sigil: the smell of goat's "
        "cheese. Twilight Scar: goats find her Gift pleasant and calming. "
        "Encumbrance 0.",
        "Combat: dodge Init 0, Defense +3; kick Init -1, Attack +2, Defense "
        "+1, Damage +3. Soak +1.",
        "Level of a General spell: Gather the Essence of the Beast 15.",
        "Talisman: a golden ring on her right hand, 10 pawns invested, 24 "
        "effect levels. Effect: Endure Pain & Fatigue (ReCo 24, Pen 0, 12 a "
        "day, Touch, Diameter, as Endurance of the Berserkers), which she "
        "gives to grogs when a fight looks near. Attunements: +4 affect "
        "wealth, +2 constant effect.",
    ),
}

SERENA: StatBlock = {
    "characteristics": characteristics(0, 0, 3, 1, 0, 0, 0, 0),
    "size": -1,
    "apparent_age": 31,
    "virtues_flaws": [
        "Wealthy",
        "Gentleman/Woman",
        "Inspirational",
        vf_puissant("Profession: Autocrat"),
        ("Social Contacts", {"group": "French knights"}),
        "Strong-Willed",
        "Temporal Influence",
        "Ambitious",
        "Difficult Underlings",
        "Covenant Upbringing",
        "Envious (Minor)",
        "Small Frame",
    ],
    "traits": {"Ambitious": 6, "Envious": 3, "Proud": 2},
    "abilities": [
        ("Area Lore: County of Toulouse", 2, "nobility"),
        ("Awareness", 2, "attractive knights"),
        ("Bargain", 2, "wine"),
        ("Charm", 4, "suitors"),
        ("Civil and Canon Law", 2, "manorial rights"),
        ("Concentration", 2, "brooding"),
        ("Etiquette", 5, "nobility"),
        ("Folk Ken", 1, "covenfolk's failings"),
        ("Living Language: French", 3, "noble"),
        ("Guile", 3, "lying to magi"),
        ("Hunt", 2, "falconry"),
        ("Intrigue", 6, "causing distrust"),
        ("Dead Language: Latin", 4, "Hermetic usage"),
        ("Leadership", 3, "covenfolk"),
        ("Music", 2, "singing"),
        ("Organization Lore: Church", 1, "heresy"),
        ("Organization Lore: Jardin", 2, "politics"),
        ("Organization Lore: Order of Hermes", 1, "Provençal Quaesitors"),
        ("Profession: Autocrat", 4, "threats of punishment"),
        ("Ride", 2, "fast escapes"),
        ("Living Language: Occitan", 5, "romantic poetry"),
    ],
    "past_xp": {"Area Lore: County of Toulouse": 5},
    "notes": paragraphs(
        "Pale-skinned and auburn-haired, a great beauty who looks like Joia "
        "yet is still outshone by her. Noble clothing in the latest styles. "
        "Worth 6 Build Points to the covenant. Encumbrance 0.",
        "Combat: dodge Init 0, Defense 0; fist Init 0, Attack 0, Defense 0, "
        "Damage 0; kick Init -1, Attack 0, Defense -1, Damage +3. Soak 0.",
    ),
}

ROSAMONDE: StatBlock = {
    "characteristics": characteristics(0, 0, 2, 0, 1, 1, 1, 1),
    "aging_points": {"stamina": 1, "dexterity": 1, "quickness": 1},
    "decrepitude": (0, 3),
    "apparent_age": 40,
    "virtues_flaws": [
        ("Affinity with {ability}", {"ability": "Great Weapon"}),
        "Custos",
        "Inspirational",
        "Arthritis",
        ("Poor Memory", {"detail": "faces"}),
        "No Sense of Direction",
    ],
    "traits": {"Homeloving": 3, "Loyal": 2, "Weary": 1},
    "abilities": [
        ("Awareness", 3, "bodyguarding"),
        ("Brawl", 3, "dodge"),
        ("Bows", 3, "short bow"),
        ("Carouse", 3, "warriors"),
        ("Craft: Gardening", 1, "roses"),
        ("Craft: Weaponry", 3, "polearms"),
        ("Etiquette", 2, "nobility"),
        ("Folk Ken", 3, "peasants"),
        ("Great Weapon", 8, "pole arm"),
        ("Guile", 1, "lying to authority"),
        ("Intrigue", 1, "gossip"),
        ("Leadership", 5, "grogs"),
        ("Dead Language: Latin", 3, "Hermetic usage"),
        ("Living Language: Occitan", 5, "cursing"),
        ("Organization Lore: Jardin", 3, "personalities"),
        ("Thrown Weapon", 3, "javelin"),
        ("Teaching", 4, "Great Weapon"),
        ("Swim", 2, "pool"),
        ("Stealth", 1, "covenant grounds"),
        ("Survival", 1, "when lost"),
    ],
    "notes": paragraphs(
        "Still a muscular woman, though her greying hair and creaking bones "
        "show her age. Worth 8 Build Points to the covenant. Her Heart's "
        "Desire: to live out her years at Belfort du Quercy.",
        "Combat: dodge Init -1, Defense +5; fist Init -1, Attack +4, Defense "
        "+4, Damage +2; kick Init -2, Attack +4, Defense +3, Damage +5; "
        "dagger Init -1, Attack +6, Defense +4, Damage +5; javelin Init -1, "
        "Attack +7, Defense +5, Damage +7; pole axe Init +2, Attack +14, "
        "Defense +11, Damage +10; short bow Init -2, Attack +8, Defense +5, "
        "Damage +7. Soak +10, in Full Chain Mail (Protection 9). Encumbrance "
        "3 (burden 4). She carries six arrows.",
    ),
}

JOHN: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 2, 0, 0, 0, 0),
    "abilities": [
        ("Animal Handling", 2, "mules"),
        ("Athletics", 2, "contortions"),
        ("Awareness", 1, "unusual plants"),
        ("Bargain", 1, "plants"),
        ("Brawl", 2, "fist"),
        ("Carouse", 1, "seduction of betters"),
        ("Charm", 1, "female magi"),
        ("Craft: Gardener", 5, "topiary"),
        ("Craft: Winemaking", 4, "black wines"),
        ("Etiquette", 2, "magi"),
        ("Folk Ken", 1, "covenfolk"),
        ("Dead Language: Latin", 4, "speaking to magi"),
        ("Leadership", 1, "in gardens"),
        ("Living Language: Occitan", 5, "gardening terms"),
        ("Organization Lore: Jardin", 2, "gardens"),
        ("Profession: Viticulturist", 4, ""),
        ("Teaching", 3, ""),
        ("Swim", 2, "diving"),
    ],
    "notes": "The book prints only his Communication and Abilities. Worth 5 "
    "Build Points to the covenant.",
}

BOHELLA: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 3, 0, 0, 0, 0),
    "abilities": [
        ("Profession: Librarian", 9, "preserve books"),
        ("Organization Lore: Jardin", 8, "history"),
    ],
    "notes": "The book names these two among her many Abilities, with her "
    "Communication. Worth 9 Build Points to the covenant.",
}

SICART: StatBlock = {
    "characteristics": characteristics(0, 0, 0, 1, 0, 0, 0, 0),
    "abilities": [
        ("Teaching", 4, "apprentices"),
        ("Profession: Scribe", 6, "copying"),
    ],
    "notes": "The book prints only these and his Communication. Worth 11 "
    "Build Points to the covenant.",
}

#: key, name, House, age, block, summary, secrets.
MAGI = (
    (
        "joia",
        "Joia du Lua",
        JERBITON,
        68,
        JOIA,
        "First Maga and chatelaine in the eyes of the world, born Joia "
        "Montdumerc on this very ridge, and the most celebrated patroness of "
        "the troubadours. Over the years she has reshaped the covenant into "
        "the Garden of Love of their songs. A patriot of Occitania, she "
        "backs Count Raimond, stands quietly against the French and the de "
        "Montforts, and shelters faidits who love Toulouse. Many have adored "
        "her in fin amor; none has ever been her lover in fact. She treated "
        "her French-born apprentice Beatriz poorly for her birth. She alone "
        "holds the key to the Door Marked Summer.",
        [
            titled("Joia's charmed look", "Her charmed look is sorcery."),
            titled(
                "The aura's turn to Faerie",
                "The aura's turn to Faerie at Jardin, which she did not mean, is "
                "her doing.",
            ),
            titled(
                "Where Joia's politics lead",
                "Sooner or later her politics will bring armies down on the "
                "covenant, as they came to Bellaquin and Lariander.",
            ),
            titled(
                "The questers' fates",
                "The magi hide the fates of questers she let into the Night "
                "Garden, altering memories where they must.",
            ),
        ],
    ),
    (
        "lexora",
        "Lexora",
        BJORNAER,
        70,
        LEXORA,
        "Second Maga, and furious to be so: slightly older than Joia and "
        "Gauntleted with her, but outranked by family. A proud Bjornaer of "
        "Clan Maruhs, lioness in heart, she opposes whatever Joia proposes "
        "and roams the country in beast shape to wear off her temper. She "
        "holds Androcles's site sacred and despises the Garden and its "
        "faeries, but she and Joia grew up together and quarrel like sisters "
        "who would close ranks against an outsider. She has Initiated "
        "Sensory Magic (Houses of Hermes: Mystery Cults p. 27) and means to "
        "visit Crintera for more. Her paganism is a vague classical one, and "
        "she bows to no one. Her Heart's Desire, to rule over magi: first "
        "Jardin, then a Tribunal as Praeco, then House Bjornaer as Prima. "
        "Only Hypatia's friendship keeps her and Xenophanes speaking.",
        [
            titled(
                "Lexora and Serena",
                "She alone sees the threat in Serena, and suspects her of "
                "sympathy with the crusade.",
            ),
            titled(
                "Lexora and Ara Maxima Nova",
                "She talks at Ara Maxima Nova as if Joia were mad and dangerous, "
                "and secretly copied Joia's tractatus on viticulture for them.",
            ),
        ],
    ),
    (
        "xenophanes",
        "Xenophanes",
        CRIAMON,
        80,
        XENOPHANES,
        "The fool of a Criamon experiment in teaching wisdom to the simple: "
        "highly educated, capable in the laboratory, and without common "
        "sense, trained at the Cave of Twisting Shadows and sent to the "
        "Tribunal in 1179. A gentle soul who tends the garden by moonlight "
        "while his familiar Hypatia prowls beside him and keeps him out of "
        "trouble. His Heart's Desire was a True Friend, and he found her. "
        "He is fond of the local Cathars and has written on them, but each "
        "time he nears renouncing his House for the Gorgiastic Cathars he "
        "talks to Father Augustine and comes away too muddled to leave the "
        "Church. He stands at the third station of the Path of Walking "
        "Backwards.",
        [
            titled(
                "Xenophanes's books",
                "Two of his three books could bring the Church down on Jardin.",
            ),
        ],
    ),
    (
        "beatriz",
        "Beatriz",
        JERBITON,
        43,
        BEATRIZ,
        "Joia's French-born former apprentice, who stayed on at the covenant "
        "though the two despise each other. She escaped the massacre at "
        "Béziers in 1209, and a few years ago quested for her Heart's "
        "Desire, fought her own stubbornness on the Lake as a magic mule, "
        "and lost. She is the broken thing the quest left: bitter, friendless "
        "by choice, taking and discarding lovers in a mockery of fin amor. "
        "Most of the magi pity her. She is obsessed with old shapeshifters "
        "and backs Ahenobarbus when he seeks reform, though she mistrusts "
        "Serena.",
        [
            titled(
                "Beatriz's vision",
                "She claims a terrible vision of Tolosa Paratge's future and "
                "will not tell it.",
            ),
            titled(
                "How Skullface got in",
                "Her failure let Skullface slip through the Aegis.",
            ),
        ],
    ),
    (
        "ahenobarbus",
        "Ahenobarbus",
        TREMERE,
        65,
        AHENOBARBUS,
        "A Rego specialist of ambition, trained for war by indirection, who "
        "has enslaved hedge wizards and dabbled in necromancy, and made "
        "enemies by both. Sent to the Tribunal in 1209 after Lariander fell, "
        "to help covenants hide and hold, he found Jardin badly exposed and "
        "has improved its grogs' armour and made the Shield of Dismissal. He "
        "thinks the Garden a reckless folly and wants to steer clear of "
        "crusaders and southern lords alike. He is smitten with Serena. He "
        "has never entered the Night Garden.",
        [
            titled(
                "Why Ahenobarbus came",
                "Coeris sent him to prove Protendus incompetent, for his parens "
                "Janus's politics at home.",
            ),
            titled(
                "Ahenobarbus's sigil",
                "His parens holds his sigil, and he avoids reporting to "
                "Protendus for as long as he can.",
            ),
            titled(
                "Serena's love",
                "Serena's love is real, but he has not seen how far her ambition goes.",
            ),
            titled(
                "Ahenobarbus's views",
                "He agrees with Serena that Lexora and Xenophanes should be "
                "eased out of the Tribunal, and that Jardin should side with "
                "the Whites and expel its heretics.",
            ),
        ],
    ),
    (
        "alyssa",
        "Alyssa",
        TRIANOMA,
        57,
        ALYSSA,
        "A cheerful maga Trianomae, born noble near Narbonne and taken as an "
        "apprentice at nine, who roams France and Iberia settling local "
        "problems and seeking out Islamic wizards; her Gentle Gift opens "
        "doors, and her meddling has annoyed a couple of covenants. She "
        "reached Jardin in 1214 after the civil war at Tolosa Paratge, her "
        "former home, and is last in precedence. She usually votes with "
        "Xenophanes, for her soft spot for odd magi and for the Cathars, "
        "dislikes Serena's cruelty, and respects Lexora enough to back her "
        "against Joia. She wants peace at home and has not yet quested.",
        [
            titled(
                "Alyssa's scrying",
                "She has been scrying the Whites unseen and means to force a way "
                "into the regio to save the Gorgiastic Cathars.",
            ),
            titled(
                "Alyssa's stolen vis",
                "She raids the Whites' vis, a flat breach of the Code, and holds "
                "30 or more pawns of it to tempt magi into Wizard's War against "
                "Carolus St. Tropez.",
            ),
            titled(
                "Whom Alyssa loves",
                "She is in love with Carolus St. Tropez.",
            ),
        ],
    ),
)

#: key, name, kind, age, block, summary, secrets.
PEOPLE = (
    (
        "serena",
        "Serena Montdumerc",
        "companion",
        31,
        SERENA,
        "Joia's niece, born in 1189 to Esquiva and the merchant Ramundus, "
        "last of the Montdumerc line and heir to the lady's title. She serves "
        "as autocrat from rooms on the tower's ground floor, and takes her "
        "frustration out on the covenfolk with threats and rages. Vain, she "
        "bitterly resents Joia's beauty.",
        [
            titled(
                "Serena's Heart's Desire",
                "Her Heart's Desire is to take back her rightful home and title "
                "from the magi.",
            ),
            titled(
                "What holds Serena back",
                "She may yet turn to crusaders or southern lords to win back her "
                "home and title, and only her love for Ahenobarbus, whom she "
                "pretends is her pawn, holds her back.",
            ),
        ],
    ),
    (
        "rosamonde",
        "Rosamonde Unaud",
        "grog",
        40,
        ROSAMONDE,
        "Captain of the turb, slowing with arthritis, who holds on for want "
        "of a woman to succeed her and will not go more than a day from "
        "home.",
        "",
    ),
    (
        "john",
        "John the Gardener",
        "grog",
        27,
        JOHN,
        "A cheerful, handsome young man with an eye for the ladies, who "
        "keeps the gardens and treats the magi as his equals. Serena has a "
        "soft spot for him. His big ginger tom is Auranja.",
        "",
    ),
    (
        "bohella",
        "Bohella the Librarian",
        "grog",
        52,
        BOHELLA,
        "Librarian for twenty-five years, watching every visitor from her "
        "little desk. Only Joia and Lexora know the covenant's past better. "
        "She gets about two seasons' study a year from the mundane books, "
        "and the covenant keeps her as Wealthy.",
        "",
    ),
    (
        "sicart",
        "Sicart the Scribe",
        "grog",
        48,
        SICART,
        "A short-sighted former tinker and grog, who makes the inks, vellum "
        "and bindings in his old pots and pans and teaches the scribe's "
        "trade.",
        "",
    ),
)

#: kind, name, author, subject, level, quality, language, what it is.
LIBRARY = (
    (
        "Ability Summa",
        "The History and Topography of the Provençal Tribunal",
        "Humbert de Cavirac",
        "Area Lore: Provençal Tribunal",
        4,
        12,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "Principles of Grammar",
        "Humbert de Cavirac",
        "Artes Liberales",
        3,
        10,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "The Laws of the Hermes",
        "Roderic of Castille",
        "Code of Hermes",
        2,
        12,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "On the Pleasing Art of Conversation",
        "Humbert de Cavirac",
        "Etiquette",
        4,
        16,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "The Golden Tongue",
        "Humbert de Cavirac",
        "Charm",
        4,
        16,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "Further Notes on Magical Notation",
        "Janus of Bonisagus",
        "Magic Theory",
        7,
        14,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "The Golden Flowers of Toulouse",
        "Raimond Saissac",
        "Living Language: Occitan",
        5,
        20,
        "Latin",
        "",
    ),
    (
        "Ability Summa",
        "The Poetry of Latin",
        "Joia du Lua",
        "Dead Language: Latin",
        2,
        8,
        "Occitan",
        "A primer for Occitan readers learning Latin.",
    ),
    (
        "Tractatus",
        "The Imperfections of Magic Theory",
        "Joia du Lua",
        "Magic Theory",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "Would The Order Be Better Without Parma Magica?",
        "Joia du Lua",
        "Parma Magica",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Claws of Magic",
        "Lexora",
        "Penetration",
        None,
        6,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Art of Viticulture",
        "Joia du Lua",
        "Profession: Viticulturist",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "On The Training of Apprentices",
        "Joia du Lua",
        "Teaching",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Simple Christians",
        "Xenophanes",
        "Theology: Cathar",
        None,
        6,
        "Latin",
        secrets(
            "A basic primer on Cathar belief, sympathetic though no endorsement.",
            "It also discusses the Gorgiastic Cathars of Ex Miscellanea, so "
            "it could show the Order sheltering heretics. Visitors have "
            "copied it.",
        ),
    ),
    (
        "Ability Summa",
        "The Mystery of the Stones",
        "Androcles of Bjornaer",
        "Organization Lore: House Bjornaer",
        4,
        15,
        "Gothic",
        secrets(
            "Chained in the mundane room in Visigothic uncials anyone can "
            "read, in words almost no one knows. Forbidden except to Joia, "
            "Lexora and those they authorize; Lexora urges Bjornaer visitors "
            "who have Gothic to read it.",
            "It rests on Androcles's reading of the stones by the pool, with "
            "Initiation Scripts drawn from them and House Bjornaer's secrets "
            "up to 1150. Without at least 1 experience point of Organization "
            "Lore: House Bjornaer it reads as gibberish.",
        ),
    ),
    (
        "Art Summa",
        "Perceiving the Unseen World",
        "Septerella Gascoigne",
        "Intellego",
        7,
        8,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Way of the Chrysalis",
        "Pantalone Maximus",
        "Muto",
        18,
        13,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Scepter of Order",
        "Rufus Pons of Arles",
        "Rego",
        12,
        15,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Way of All Flesh",
        "Catugno the Surgeon",
        "Perdo",
        11,
        15,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Rugen Bestiary",
        "Androcles of Bjornaer",
        "Animal",
        15,
        16,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Flow of the Rhone",
        "Martin of Stella Durus",
        "Aquam",
        13,
        18,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "Blood, Bone and Bile",
        "Catugno the Surgeon",
        "Corpus",
        10,
        15,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "Antonius' Herbal",
        "Antonius of Merinita",
        "Herbam",
        20,
        11,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "On Accidents and the Appearance of Things",
        "Pythonus Minor",
        "Imaginem",
        13,
        15,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "A Primer on the Mysteries of Memory",
        "Humbert de Cavirac",
        "Mentem",
        13,
        18,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "Metamagica",
        "Oswald of York",
        "Vim",
        13,
        18,
        "Latin",
        "",
    ),
    (
        "Art Summa",
        "The Joy of Flowers",
        "Joia du Lua",
        "Herbam",
        9,
        8,
        "Occitan",
        "",
    ),
    (
        "Art Summa",
        "The Succulent Grapes of Love",
        "Joia du Lua",
        "Herbam",
        7,
        8,
        "Occitan",
        "",
    ),
    (
        "Tractatus",
        "Out of Nothing Springs Forth Joy",
        "Joia du Lua",
        "Creo",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "Epistemology and Empiricism",
        "Chretien de Paris",
        "Intellego",
        None,
        10,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Keys of Bonisagus: Authority Explicated",
        "Gustavus of Mainz",
        "Rego",
        None,
        7,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "Like the Seasons, Like the Wind",
        "Marcus of Ghent",
        "Muto",
        None,
        10,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Choleric Beasts",
        "Aella of Bjornaer",
        "Animal",
        None,
        11,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Sanguine Beasts",
        "Aella of Bjornaer",
        "Animal",
        None,
        10,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Melancholy Beasts",
        "Aella of Bjornaer",
        "Animal",
        None,
        9,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The Heart of the Eagle",
        "Androcles of Bjornaer",
        "Animal",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "Mastering The Mistral",
        "Anonymous",
        "Auram",
        None,
        10,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "Why Does Flame Consume?",
        "Lucius Delvander",
        "Ignem",
        None,
        8,
        "Latin",
        "",
    ),
    (
        "Tractatus",
        "The World Beneath Our Feet",
        "Xenophanes",
        "Terram",
        None,
        6,
        "Latin",
        "Uncontroversial, unlike his other two.",
    ),
    (
        "Tractatus",
        "God Within Us",
        "Xenophanes",
        "Vim",
        None,
        6,
        "Latin",
        secrets(
            "A simple tractatus on Vim.",
            "It treats The Gift as shards of the Divine, broken by the Fall "
            "and longing to return. The Church would call that heresy.",
        ),
    ),
    (
        "Tractatus",
        "Joia's Book of Vines",
        "Joia du Lua",
        "Herbam",
        None,
        8,
        "Occitan",
        "",
    ),
)
ARTS = {
    "Creo", "Intellego", "Muto", "Perdo", "Rego", "Animal", "Aquam", "Auram",
    "Corpus", "Herbam", "Ignem", "Imaginem", "Mentem", "Terram", "Vim",
}  # fmt: skip

#: The Lab Texts by Form, as the book names them: (name, arts, level).
LAB_TEXTS = (
    ("Soothe Pains of the Beast", "CrAn", 20),
    ("True Rest of the Injured Brute", "CrAn", 20),
    ("The Wizard's Mount", "CrAn", 35),
    ("Opening the Tome of the Animal's Mind", "InAn", 25),
    ("Beast of Outlandish Size", "MuAn", 15),
    ("Disguise of the Putrid Aroma", "ReAn", 5),
    ("Soothe the Ferocious Bear", "ReAn", 10),
    ("Viper's Gaze", "ReAn", 15),
    ("The Gentle Beast", "ReAn", 25),
    ("Mastering the Unruly Beast", "ReAn", 25),
    ("Commanding the Harnessed Beast", "ReAn", 30),
    ("Subtle Taste of Poison and Purity", "InAq", 5),
    ("Comfort of the Drenched Traveler", "PeAq", 5),
    ("Cloak of the Duck's Feathers", "ReAq", 5),
    ("Breath of Winter", "ReAq", 15),
    ("Jupiter's Resounding Blow", "CrAu", 10),
    ("Charge of the Angry Winds", "CrAu", 15),
    ("The Cloudless Sky Returned", "PeAu", 45),
    ("Bind Wound", "CrCo", 10),
    ("The Chirurgeon's Healing Touch", "CrCo", 20),
    ("Gentle Touch of the Purified Body", "CrCo", 20),
    ("Cheating the Reaper", "CrCo", 30),
    ("Restoration of the Defiled Body", "CrCo", 25),
    ("Sight of the True Form", "InCo", 10),
    ("Revealed Flaws of Mortal Flesh", "InCo", 10),
    ("The Inexorable Search", "InCo", 20),
    ("The Eye of the Sage", "InCo", 30),
    ("Disguise of the New Visage", "MuCo", 15),
    ("Gift of the Bear's Fortitude", "MuCo", 25),
    ("Rise of the Feathery Body", "ReCo", 10),
    ("Endurance of the Berserkers", "ReCo", 15),
    ("The Gift of Vigor", "ReCo", 20),
    ("Hunt for the Wild Herb", "InHe", 5),
    ("Conjure the Sturdy Vine", "CrHe", 5),
    ("The Healthy Vine", "CrHe", 5),
    ("The Well Tended Vine", "CrHe", 5),
    ("Create the Flowers of the Moon", "CrHe", 15),
    ("Trap of the Entwining Vines", "CrHe", 15),
    ("Bridge of Wood", "CrHe", 20),
    ("The Bountiful Feast", "CrHe", 35),
    ("Coils of the Entangling Plants", "ReHe", 20),
    ("Converse with Plant and Tree", "InHe", 25),
    ("Freeing the Striding Tree", "ReHe", 30),
    ("Heat of the Searing Forge", "CrIg", 10),
    ("Tales of the Ashes", "InIg", 5),
    ("The Many-Hued Conflagration", "MuIg", 5),
    ("Show of the Flames and Smoke", "MuIg", 10),
    ("Prison of Flames", "MuIg", 20),
    ("Trapping the Fire", "MuIg", 25),
    ("Light Shaft of the Night", "ReIg", 20),
    ("Ward Against Heat and Flames", "ReIg", 25),
    ("Phantasm of the Human Form", "CrIm", 25),
    ("Discern Own Illusions", "InIm", 15),
    ("Discern the Images of Truth and Falsehood", "InIm", 30),
    ("Taste of the Spices and Herbs", "MuIm", 5),
    ("Aura of the Ennobled Presence", "MuIm", 10),
    ("Disguise of the Transformed Image", "MuIm", 15),
    ("Veil of Invisibility", "PeIm", 20),
    ("Wizard's Sidestep", "ReIm", 10),
    ("Black Whisper", "PeMe", 40),
    ("Vision of the Haunting Spirits", "MuMe", 40),
    ("Calm the Motion of the Heart", "PeMe", 15),
    ("Enchantment of Detachment", "PeMe", 15),
    ("Loss of But a Moment's Memory", "PeMe", 15),
    ("Passion's Lost Feeling", "PeMe", 25),
    ("Frosty Breath of the Spoken Lie", "InMe", 20),
    ("Posing the Silent Question", "InMe", 20),
    ("Trust of Childlike Faith", "PeMe", 10),
    ("Confusion of the Numbed Will", "PeMe", 15),
    ("The Call to Slumber", "ReMe", 10),
    ("Aura of Rightful Authority", "ReMe", 20),
    ("Cool the Lover's Ardor", "ReMe", 20),
    ("Eyes of the Treacherous Terrain", "InTe", 15),
    ("The Enigma's Gift", "CrVi", 30),
    ("The Invisible Eye Revealed", "InVi", 15),
    ("Detect the Gift", "InVi", 20),
    ("Piercing the Faerie Veil", "InVi", 20),
    ("Piercing the Magical Veil", "InVi", 20),
    ("Wizard's Boost (Mentem)", "MuVi", 25),
    ("Wizard's Reach (Mentem)", "MuVi", 25),
    ("Wizard's Communion", "MuVi", 30),
    ("Wind of Mundane Silence", "PeVi", 20),
    ("Unraveling the Fabric of Mentem", "PeVi", 30),
    ("Gather the Essence of the Beast", "ReVi", 15),
    ("Aegis of the Hearth", "ReVi", 25),
    ("Maintaining the Demanding Spell", "ReVi", 25),
    ("Suppressing the Wizard's Handiwork", "ReVi", 25),
    ("Opening the Intangible Tunnel", "ReVi", 30),
    ("Watching Ward", "ReVi", 30),
)
JOIAS_TEXTS = {
    "The Healthy Vine",
    "The Well Tended Vine",
    "Create the Flowers of the Moon",
    "Cool the Lover's Ardor",
}
#: A Lab Text the catalog files under a general name.
CATALOG_NAMES = {
    "Wizard's Boost (Mentem)": "Wizard's Boost (Form)",
    "Wizard's Reach (Mentem)": "Wizard's Reach (Form)",
    "Unraveling the Fabric of Mentem": "Unravelling the Fabric of (Form)",
}

CHARTER = (
    "Each maga spends one season a year in the covenant's service. What "
    "counts may be widened by Council vote, and a later vote may withdraw it.",
    "Standing services, needing only a declaration: writing Lab Texts, "
    "tractatus or summae for the library; copying these to trade with other "
    "covenants; making enchanted devices for the covenant, vineyards or "
    "gardens; maintaining the gardens or vineyards; making one's own "
    "longevity ritual; setting up a new laboratory; extracting vis, or "
    "collecting it for the stocks if that takes over ten days; training an "
    "apprentice; teaching spells, Arts or Abilities to magi or covenfolk.",
    "By tradition a maga may skip the service for a year, and is then assigned no vis.",
    "A maga in good standing has four pawns of vis a year, plus what her "
    "covenant enchanting needs, the Aegis and the grogs, the library, and "
    "five pounds of silver.",
    "An apprentice of the covenant who leaves to found a new covenant has a "
    "pawn of vis for each year trained here, fifty pounds of silver, and up "
    "to two years' free copying; one who joins an existing covenant does not.",
    "Resident magae help collect the vis sources and attend Council when present.",
    "Magae obey the Code of Hermes; one convicted of a Low Crime by a lawful "
    "Tribunal is asked to leave. This has never happened.",
    "Magae swear never to declare Wizard's War on a fellow member, nor to "
    "use Certamen to overturn a ruling of Council. Added in 1219 over "
    "Ahenobarbus's and Lexora's votes; it binds only those who swear the "
    "charter hereafter, and so none of the present members.",
)


def build(provence: Provence) -> None:
    b = provence.b
    site, wood = _places(provence)
    covenant = _covenant(provence, site)
    provence.covenants["jardin"] = covenant
    people = _people(provence, covenant)
    _laboratories(b, covenant, people)
    _device(b, covenant)
    _library(b, covenant)
    _lab_texts(b, covenant, people["joia"])
    _vis(covenant)
    _charter(covenant)
    _village(provence, site)
    _creatures(b, covenant, site, wood, people)
    _familiars(b, people)
    _links(provence, covenant, people)


def finish(provence: Provence) -> None:
    """Where this book's dates differ from the Tribunal book's it wins, with
    it on: Bellaquin's fall in 1202 and Lariander's in 1209 (p. 41), and the
    war at Tolosa Paratge before Alyssa left it in 1214 (p. 48)."""
    tribunal = provence.tribunal
    assert tribunal is not None
    for entry in tribunal.diary:
        if entry.title == "Bellaquin falls":
            entry.year = 1202
        elif entry.title == "Montgey and the fall of Lariander":
            entry.year = 1209
        elif entry.title == "Wizard's Wars at Tolosa Paratge":
            entry.details = paragraphs(
                entry.details,
                "Through the Aegis has the civil war already broken out by "
                "1214, when it drove Alyssa from the covenant to Jardin.",
            )


def stats(provence: Provence) -> None:
    b = provence.b
    for key, _name, _kind, _age, block, _summary, _secrets in (*MAGI, *PEOPLE):
        character = b.stats(provence.magi[key], block, source=SOURCE)
        past = block.get("past_xp", {})
        for ability in character.abilities:
            ability.xp += past.get(ability.name, 0)
    # The book prints his Mastery of The Leap of Homecoming as 2 (5).
    for known in provence.magi["ahenobarbus"].spells_known:
        if known.mastery_score == 2:
            known.mastery_xp += 5


def _places(provence: Provence) -> tuple[Neighbour, Neighbour]:
    b = provence.b
    vineyards = provence.places["cahors_vineyards"]
    site = b.place(
        "The Fort at Belfort",
        inside=vineyards,
        realm="Faerie",
        aura=4,
        known="In the Tribunal",
        summary=paragraphs(
            "A rocky bluff in the vineyards a day south of Cahors, a mile from "
            "the Toulouse road, ringed by old earth ramparts that now terrace "
            "the vines. Within the crumbling walls of a Visigothic fort stand "
            "a red-brick library under a green copper dome and a golden brick "
            "tower, among lawns, sandy paths, pools, a fountain and shade "
            "trees, all laid out as one garden of colour and scent. Strange "
            "talking animals and butterflies that turn with the mood of "
            "those who rest there come and go; only clergy seem proof against "
            "the place, thinking of Eden.",
            "The tower has four floors on a spiral stair: Serena's rooms and "
            "a guard chamber, Beatriz's laboratory, Joia's sanctum, and Joia's "
            "laboratory at the top. The guesthouse, the Montdumerc manor of "
            "red brick, has rooms for guests, four great bedchambers above, "
            "and at the top the sancta of Alyssa and Ahenobarbus. The brick "
            "kitchen doubles as a bakehouse. The other laboratories are stone "
            "buildings against the fort's walls. One corner, the bower, is a "
            "tangle of wild roses over mossy rocks, where lovers go and Joia "
            "sits sewing.",
            "In the wall is a sky-blue door. From the corner of the eye it "
            "opens on high summer. It stays locked, and Joia keeps the key.",
        ),
        tethers="The Door Marked Summer, in the fort's wall, opens on the first "
        "level. The maze on that level leads to the second.",
        levels=[
            b.level(
                "The Summer Garden",
                5,
                "Faerie",
                see="Through the corner of the eye, at the Door Marked Summer",
                enter="Joia's key, given only to one she judges a true lover",
                notes=paragraphs(
                    "A walled garden that mirrors the fort: a great pool where "
                    "the library stands, a maze of dark hedges at the tower, "
                    "avenues of shade, statues of classical goddesses and the "
                    "sun always high. Joia holds her masked entertainments "
                    "here, dazzling her guests with open magic. The bower is "
                    "here too, mirrored, deeper and stranger.",
                    "The pool, gone from the mundane world, is a strong "
                    "initiatory site for Bjornaer with sanguine Heartbeasts, "
                    "its mossy rocks holding Visigothic magic of an old "
                    "shapechanging tradition; many shapechangers hold it holy.",
                    "The maze is Xenophanes's topiary. At its heart stands a "
                    "tree of shining fruit that no mundane way can reach, and "
                    "the fruit is deadly poison. To pass on, simply become "
                    "lost in it.",
                ),
            ),
            b.level(
                "The Night Garden",
                7,
                "Faerie",
                enter="Get lost in the maze of the Summer Garden",
                notes=secrets(
                    paragraphs(
                        "A full moon over a warm night, distant walls, tangled "
                        "briar and tree, paths among mossy rocks, bluebell "
                        "clearings, and brooks that end in deep pools. The magi "
                        "avoid it and do not tend it. Its shy, deadly monsters "
                        "and strange beings take forms that suit the quester, "
                        "and the book leaves them to the storyguide: several "
                        "must be overcome on any quest.",
                        "The Lake: only one seeking a first Heart's Desire finds "
                        "the path. Black, still water, with the bower on an "
                        "island and a one-person boat with a paddle. Other ways "
                        "across work, but leave the crosser alone. Some who "
                        "entered the water have drowned for ever. Mist takes the "
                        "crosser, and her own emotion attacks; True Love passes "
                        "free.",
                    ),
                    paragraphs(
                        "The fight's outcome. Dead: gone, perhaps drowned. "
                        "Incapacitated: wakes in the Garden with a Major Flaw "
                        "or two Minor (Curse of Venus, Fury, Low Self-Esteem, "
                        "Lost Love; or Compulsion, Delusion, Depressed, Obsessed, "
                        "Oversensitive, Pessimistic, Weakness, Weak Willed, "
                        "Wrathful), and darker Traits. Worst wound Heavy, enemy "
                        "beaten: one new Minor Personality Flaw of the player's "
                        "choice, replacing like for like if the Trait fought was "
                        "a Flaw. Medium: a Confidence Point, and the Flaw behind "
                        "the Trait may go. Light: the same, with 3 Confidence "
                        "Points. Unwounded: Self-Confident (a grog gains "
                        "Confidence 1).",
                        "The Bower of Your Heart's Desire: on the island a pale "
                        "maiden in noble dress kisses the quester once and "
                        "whispers the secret, and she wakes in the bower of the "
                        "Garden with it. The player chooses the Desire, which "
                        "may bring a Personality Flaw and at most one Virtue. "
                        "Those Tainted with Evil may find ghastly things. Perdo "
                        "Mentem sometimes takes away what a broken quester "
                        "learned. No magus knows if the Desire is true or a "
                        "faerie ploy.",
                    ),
                ),
            ),
        ],
        secrets=[
            titled(
                "The aura's turn to Faerie",
                "The Fort at Belfort was Magic until Joia built the troubadours' "
                "garden there. Over the last decade the song has taken hold: "
                "Magic gave way to Faerie, two strong Faerie regiones replaced "
                "the old magical ones, and the wild hilltop Androcles sought was "
                "tamed.",
            ),
            titled(
                "A Clan Maruhs ancestor site",
                "The Fort at Belfort was once a Clan Maruhs ancestor site, where "
                "Panthera the Terrible was sometimes found.",
            ),
        ],
        detail=FULL,
    )
    wood = b.place(
        "The Wood of the Highest Tree",
        inside=vineyards,
        realm="Faerie",
        aura=3,
        known="Locally",
        summary="A small faerie wood on a hilltop some sixteen miles east of "
        "Jardin, under a tall tree of a kind unknown in the region. Minor "
        "goblin fae harass anyone who walks in, so visitors usually reach the "
        "treetop by magic.",
    )
    return site, wood


def _covenant(provence: Provence, site: Neighbour) -> Covenant:
    b, tribunal = provence.b, provence.tribunal
    assert tribunal is not None
    return b.covenant(
        NAME,
        tribunal=tribunal,
        founded=1164,
        season="Summer",
        detail=FULL,
        place=site,
        aura=4,
        realm="Faerie",
        summary=paragraphs(
            "La Jardin stands on a bluff among the vineyards south of Cahors, "
            "behind the walls of a fallen Visigothic fort, and its symbol is a "
            "single rose in bloom. Its six magi live among gardens where, by "
            "custom and perhaps by the magic of the place, women rule and men "
            "are courteously obedient. Most of the Tribunal knows it only by "
            "rumour, as an odd, old-fashioned place where three nights' stay "
            "shows a guest his heart's true desire; even Redcaps hurry on.",
            "Humbert de Cavirac of Jerbiton came here as tutor to the "
            "widowed Audiarda Montdumerc's daughters, having seen The Gift in "
            "young Joia and power in the site, and founded the covenant of "
            "Belfort in 1164 with her as his apprentice. He became Audiarda's "
            "lover. The Bjornaer Androcles soon followed with his apprentice "
            "Lexora. Joia's dream of the Garden of Love grew until, after "
            "Humbert's Final Twilight and Androcles's death, she renamed the "
            "covenant. Audiarda died in 1198, and Joia's sister Esquiva, with "
            "her merchant husband Ramundus, took on Belfort and the black wine.",
            "The covenant keeps open house on the Cahors road for poets, "
            "knights errant and great lords, and turns quietly inward. It has "
            "missed four Tribunals since Humbert's death. A grog at the gate "
            "sends the wrong sort away.",
        ),
        what_matters=joined_lines(
            "Build Points: 1466 (device 15, laboratories 170, Lab Texts 333, "
            "library 722, money 30, specialists 39, vis 157)",
            "Boon: Autocephalous (the customs of Toulouse: fealty to no noble "
            "but Serena)",
            "Boon: Aura (Minor) (4, over the whole fortress; too low to warp "
            "the covenfolk); Edifice (the library); Edifice (the tower); Loyal "
            "Covenfolk; Prestige (Minor) (Reputation 3 among troubadours and "
            "local nobles); Vivid Environment; Wealth (Minor)",
            "Hook: Regio (Major) (The Garden of Love); War Zone (the crusade)",
            "Hook: Crumbling; Faerie Aura; Non-magical Regio (the book's Faerie "
            "Regio, counted as well as the Regio); Road (Minor) (the busy "
            "Cahors to Toulouse road)",
            "Income: 250 Mythic Pounds a year from the vineyards, against 218 "
            "spent, for a surplus of 32 (the expenses printed add to 216: "
            "buildings 22, consumables 28, laboratories 8, tithes 50, "
            "provisions 70, wages 28, weapons and armor 1, writing materials 8, "
            "sundries 1). The tithes are a tenth each to Church and Cathars. "
            "The costs allow for about two visiting nobles and retinues. 300 "
            "pounds in a locked chest in the manor house",
            "Loyalty: +4 (53: base 30 from Loyal Covenfolk, turb captain +7, "
            "autocrat +6, living conditions +10). It does not apply to disputes "
            "between the magi, and Serena's threats could erode it; a steward "
            "and a chamberlain would help (Covenants pp. 30-39)",
            "Council: at least once a season in the library's chamber, one "
            "vote each. Precedence runs from first residence, not the Gauntlet, "
            "and orders vis, books and resources: Joia, Lexora, Xenophanes, "
            "Beatriz, Ahenobarbus (1209), Alyssa (1214)",
            "Library: guests may copy for a season or more for a summa of equal "
            "or greater value, with no guest expenses; Lab Texts are open one "
            "season a year for the usual contribution and as many spell levels "
            "given as copied. Only one maga reads a book at a time, and Council "
            "rules when two want it",
            "Votes: 6 at Tribunal, unused for four meetings. Spare laboratory "
            "room for three or four more magi; Council would likely stop at nine",
            "Allies: Stella Durus; Bellaquin, now distant; Ostal des Exiles, "
            "through Joia and Gilbert",
            "Rivals: Miniata Sophia; the Coenobium, since Joia's jibe at Alazais",
        ),
        notes=paragraphs(
            "Relations. Aedes Mercurii barely notices Jardin; only Lexora "
            "visits, and her support of the Cults of Mercury, Mars and Vulcan "
            "ruffles Castra Solis. Ara Maxima Nova's pagans are her friends "
            "and may turn away Jardin magi who come without her. Castra Solis "
            "has treated Jardin as an arm of Bellaquin; Lexora and Ahenobarbus "
            "want closer ties, Joia is a friend of Garus and Troya, and Lexora's "
            "Mercurian links and Xenophanes's pacifism get in the way. At the "
            "Ostal des Exiles Joia respected Gilbert in his wilderness years; "
            "Alyssa's last visit split her hosts, and Popilia may declare war "
            "or tell the Whites. Ahenobarbus wants Garsenda under his wing and "
            "she will not answer. Miniata Sophia's Leonarda shares Xenophanes's "
            "parens and Path, called him insanity, and refused him in 1179, a "
            "dispassionate, mystical hatred. At Stella Durus, Jean Marie writes "
            "to Joia on Courtly Love; with Bellaquin they could vote as a bloc. "
            "At Tolosa Paratge Mariola was a friend of Humbert and Joia, and "
            "now cannot be reached: Joia leans to negotiating, Xenophanes to "
            "rescue without bloodshed, Ahenobarbus to the Whites. Valgravian "
            "of Bellaquin is Joia's friend, and Ahenobarbus respects Artemis "
            "by reputation.",
            "Other companions, not detailed: a Jewish banker of Cahors, a "
            "troubadour besotted with Joia, and a faidit turned bandit who hides "
            "within the walls. The turb: three in partial leather with bows, "
            "shield and short spear as scouts, three in partial scale with "
            "poleaxes and daggers as shield grogs. The servants are efficient, "
            "but Serena's rages have hurt morale.",
            "Story seeds, Joia. The Jealous Trobairitz: the unknown Titbores "
            "sings that Joia is a warty crone kept up by sorcery, and she does "
            "use sorcery. Star Crossed Lovers: Rogier Bernard of Foix and Guida "
            "of Rodez, each betrothed elsewhere, elope from a Summer Garden "
            "party and threaten the South's unity. Joia's Heart: she falls "
            "for a young knight who proves to be Amalric de Montfort; Alyssa "
            "knows him at once.",
            "Story seeds, Lexora. The Pride of Lions: she seeks a deed, legal "
            "and heroic, to shame Joia from the lead. The Handsome Huntsman: a "
            "young Aragonese noble chases her lioness and vanishes. The Return "
            "of Panthera: the Great Beast comes back to his corrupted pool.",
            "Story seeds, Xenophanes and Hypatia. The Dance of Death: a village "
            "two days off suffers a dancing fever, God's curse for a hidden "
            "sin. Sibling Rivalry: Leonarda stages a Criamon riddle as a trap. "
            "Hypatia's Lover: her nights with Auranja leave Xenophanes "
            "unguarded and foolish. The Spy in the Undergrowth: Auranja passes "
            "the door and his gossip reaches the minstrel Izarns through his "
            "cat Tibout, and Joia is blamed.",
            "Story seeds, Beatriz. A Stolen Kiss: Jordas, great-nephew of Count "
            "Raimond and a rebel captain, deserts to moon after her, and Joia's "
            "magic fails on him. Fangs in the Night: the pool's old shapeshifting "
            "witches, allied to Birna's Pomeranian tradition, may have come back "
            "to Belfort. Dreaming Beatriz Back Together: Lexora learns Dream "
            "Magic at Crintera to enter Beatriz's dreams.",
            "Story seeds, Ahenobarbus and Nec. His Master's Voice: Janus of "
            "Tremere (Against the Dark p. 28), Secretary for Contingencies, "
            "sets him Plan Black Olive (leverage on Cathar bishops), Gold Olive "
            "(Montségur and its treasure), Faded Rose (how to take Jardin), Lost "
            "Children (what really happened at Lariander), Buried Talents (30 "
            "pawns to invest for seven years), Mountain Witch (a Sorginak coven "
            "holds Tremere papers) and High Mercury (is Protendus a traitor?). "
            "The Wolves in the Woods: Nec's spy pack is blamed for killings by "
            "Galhart the miller, a cursed wolf by night and her lover.",
            "Story seeds, Alyssa and Fauconrouge. Guerrilla Warfare: she recruits "
            "for her secret war on the Whites. The Curse of Venus: she plans to "
            "kidnap Carolus St. Tropez from Castle Pujol for the Night Garden. "
            "A Hint of Lavender: Muslim wizards on the Isles d'Yf, whom she "
            "means to have recognized.",
            "Story seeds, the covenant. No More Gardening?: Lexora moves to "
            "strike gardening from service, and neglected love sours the aura, "
            "reverting it to Magic in time. Heresy in the Library?: a papal "
            "legate reads Xenophanes. The Facechanger: Skullface returns. The "
            "Mercenaries: unpaid routiers billet on Belfort and take the wine. "
            "The Walls of Jardin: Ahenobarbus's repairs bring Alix de Montfort "
            "to look. Unwelcome Guests: the gate grog admits the wrong nobles.",
            "Storylines. The Heart's Desire and romantic love, in chaste longing "
            "and adultery alike; Joia against Lexora, with Serena behind them, "
            "and a slide to Winter on Tolosa's pattern; the crusade, and Count "
            "Raimond coming for advice; the faith, should Father Augustine or "
            "the Unauds be replaced or the Bishop of Cahors look closely; the "
            "faeries, stronger each year, creeping out when the Aegis is weak; "
            "and questers broken by the Garden, many of them lords of the South.",
            "Alyssa, Beatriz, Ahenobarbus and Xenophanes suit replacing by "
            "player magi, in that order. Lexora, Xenophanes and Ahenobarbus "
            "have each lately trained an apprentice, begun in that order, so "
            "new magi of those Houses fit, ranked by their parens; a second "
            "apprentice of Joia's costs her 150 points. The covenant can move: "
            "Normandy needs least change, and Stonehenge has Fair Rosamund's "
            "maze at Woodstock.",
        ),
        secrets=[
            titled(
                "The legends are wrong",
                "The legends are wrong: the visitor's three nights do nothing, "
                "and the Heart's Desire is a quest made through the Door.",
            ),
            titled(
                "If the aura's change were known",
                "Scholars of the Order would flock to Jardin if the aura's change "
                "were known.",
            ),
            titled(
                "Jardin's dangers",
                "Serena is Jardin's greatest danger, and Lexora its open one.",
            ),
            titled(
                "Past the Aegis",
                "Skullface and lesser faeries already get past Jardin's Aegis.",
            ),
        ],
    )


def _people(provence: Provence, covenant: Covenant) -> dict[str, Character]:
    b = provence.b
    found = {}
    for key, name, house, age, _block, summary, hidden in MAGI:
        found[key] = provence.magi[key] = b.magus(
            name,
            covenant=covenant,
            house=house,
            age=age,
            summary=summary,
            secrets=hidden,
        )
    for key, name, kind, age, _block, summary, hidden in PEOPLE:
        found[key] = provence.magi[key] = b.magus(
            name,
            covenant=covenant,
            house="",
            age=age,
            summary=summary,
            secrets=hidden,
            type=kind,
        )
    return found


def _laboratories(b: Builder, covenant: Covenant, people: dict[str, Character]) -> None:
    source = "Through the Aegis p. 59"
    for key, title, characteristics_, specializations, room, words in (
        (
            "joia",
            "Joia du Lua's laboratory",
            {
                "refinement": 3,
                "general_quality": 1,
                "upkeep": 1,
                "safety": 4,
                "aesthetics": 5,
            },
            {"Auram": 3, "Herbam": 1},
            "Top of the tower",
            "Humbert's, renovated: a circular room 25 feet across and 500 "
            "square feet, under the dome, its high carved beams brightly "
            "painted, a glazed window over the Garden of Love, flowers heady "
            "everywhere, and all immaculately kept. Virtues: Elevated, Highly "
            "Organized, Superior Construction, Lesser Feature (Lofty Ceiling), "
            "Lesser Feature (Window), Potted Plants. Four fewer botch dice, as "
            "printed. Cost 30 Build Points.",
        ),
        (
            "lexora",
            "Lexora's laboratory",
            {
                "refinement": 2,
                "general_quality": 1,
                "upkeep": 1,
                "safety": 1,
                "health": -1,
                "aesthetics": -2,
            },
            {"Perdo": 1, "Animal": 3},
            "Against the fort's wall",
            "A filthy menagerie of a place, with birds in the rafters, cats "
            "and dogs by the fire, a small pond and a pen for wolves, boars or "
            "a stag, and in truth perfectly ordered. Virtues: Highly Organized, "
            "Lesser Feature (Animal Pen), Menagerie. Flaw: Dirty. One fewer "
            "botch die; -1 to Recovery in a year of two seasons here. Cost 20 "
            "Build Points.",
        ),
        (
            "xenophanes",
            "Xenophanes's laboratory",
            {
                "refinement": 1,
                "general_quality": 1,
                "health": -2,
                "aesthetics": -2,
            },
            {},
            "Against the fort's wall",
            "Austere: he sleeps here on a straw mat beside a single stool. "
            "Flaw: Living Quarters. -2 to Recovery and -1 to aging rolls. Cost "
            "10 Build Points.",
        ),
        (
            "beatriz",
            "Beatriz's laboratory",
            {
                "refinement": 2,
                "general_quality": 2,
                "upkeep": -3,
                "health": -1,
            },
            {"Imaginem": 2, "Creo": 1},
            "Second floor of the tower",
            "The room of her apprenticeship, its murals painted over, spotless "
            "and spare, with a bed, table and chairs, and a magnificent "
            "full-length curved mirror that subtly distorts. Virtues: Highly "
            "Organized, Spotless, Greater Feature (Mirror). Flaws: Living "
            "Quarters, Missing Equipment (Binding Familiar, Teaching), Missing "
            "Ingredients (Perdo), Undecorated. No binding a familiar or "
            "teaching here; Perdo totals are halved until supplies come from "
            "Toulouse or Cahors, a few days' work. -1 to Recovery. Cost 10 "
            "Build Points.",
        ),
        (
            "ahenobarbus",
            "Ahenobarbus's laboratory",
            {},
            {},
            "Between Xenophanes's and Lexora's",
            "A standard laboratory in every respect, not yet improved.",
        ),
        (
            "alyssa",
            "Alyssa's laboratory",
            {},
            {},
            "Near the main gate",
            "Very ordinary, personalized to the usual standard; she travels "
            "too much to improve it, and might lend it, at a price in favours.",
        ),
    ):
        b.laboratory(
            covenant,
            title,
            owner=people[key],
            characteristics=characteristics_,
            specializations=specializations,
            source=source,
            rooms={room: words},
        )
    for title, words in (
        (
            "The stocked guest laboratory",
            "A stone building like the others, stocked as a standard "
            "laboratory, for visiting magi or a new recruit.",
        ),
        (
            "The bare guest laboratory",
            "Very basic: -3 to Laboratory Totals as it stands, put right by a "
            "season's work. The two guest laboratories cost 100 Build Points.",
        ),
    ):
        b.laboratory(
            covenant,
            title,
            characteristics={},
            specializations={},
            source="Through the Aegis p. 60",
            rooms={"Against the fort's wall": words},
        )


def _device(b: Builder, covenant: Covenant) -> None:
    b.device(
        covenant,
        "Shield of Dismissal",
        description="A shield embossed with panpipes in gold leaf, carried by "
        "the grog at the gate, made by Ahenobarbus. Those of rank or wealth "
        "are always let in; troublemakers, nobodies, the French and friends of "
        "the crusade are sent away. Cost 15 Build Points.",
        effects=[
            InstilledEffect(
                id="",
                name="Subtle Shift of the Intended Destination",
                technique="Rego",
                form="Mentem",
                range="Voice",
                duration="Sun",
                target="Group",
                level=35,
                description="The user slaps the panpipes and calls to visible "
                "targets, who feel the urge to leave the covenant and seek some "
                "place dear to them, and later recall meaning to come but not "
                "why they did not. ReMe 37 with its uses (base 5, +2 Voice, +2 "
                "Sun, +2 Group; +2 for 3 a day).",
                uses_per_day="3",
                penetration=0,
            )
        ],
    )


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
            language=language,
            author=author,
            description=words,
        )


def _lab_texts(b: Builder, covenant: Covenant, joia: Character) -> None:
    by_name = {spell.name.casefold(): spell for spell in catalog.load_spell_catalog()}
    for name, arts, level in LAB_TEXTS:
        spell = by_name.get(CATALOG_NAMES.get(name, name).casefold())
        ours = name in JOIAS_TEXTS
        book = b.book(
            covenant,
            name,
            "Lab Text",
            level=level,
            author=joia.name if ours else "",
            description="In its Form's locked chest under the dome.",
        )
        book.text_kind = TEXT_SPELL
        book.spell_name = name
        book.spell_id = spell.id if spell is not None else None
        book.technique = ART_LOOKUP[arts[:2].lower()]
        book.form = ART_LOOKUP[arts[2:4].lower()]
        if ours:
            book.author_id = joia.id


def _vis(covenant: Covenant) -> None:
    for name, art, pawns, season, words in (
        (
            "The Black Grapes",
            "Perdo",
            6,
            "Autumn",
            "At sunset on the last day of harvest, All Hallows' Eve, one bunch "
            "takes the vis, and it must be the last cut, the one the chatelaine "
            "names by the villagers' old custom. Cut it with a copper sickle "
            "into a copper bowl, and no hand may touch it until it leaves the "
            "vineyard. Sometimes it goes wrong.",
        ),
        (
            "The Reflection of Beatriz's Lover",
            "Imaginem",
            2,
            "Spring",
            "Lovers who kiss in true passion before a mirror burn the image "
            "into it until the next dawn or dusk, when the vis must be moved "
            "to something else. Only Serena, Joia and Beatriz own mirrors, "
            "and Beatriz's is the great one.",
        ),
        (
            "The Heart of a Lover",
            "Corpus",
            1,
            "Summer",
            "On a summer evening in the bower a lover gives his lady a rose, "
            "which pricks him; the drop of blood she catches is the pawn.",
        ),
        (
            "The Fiery Liquor",
            "Ignem",
            3,
            "Spring",
            "Three barrels of Vazerac's best vintage hold flames in their ruby "
            "depths. The village's twelve consuls know which, and set a price "
            "each year, usually a magical favour, sometimes a pound of silver. "
            "They know nothing of vis, will not haggle, and threaten to sell "
            "to other magicians.",
        ),
        (
            "The Highest Leaf",
            "Muto",
            1,
            "Autumn",
            "The topmost leaf of the Highest Tree turns a gold that sparkles "
            "with every colour.",
        ),
        (
            "Change of Heart (Mentem)",
            "Mentem",
            3,
            "",
            "The first quester each year wholly changed by her Heart's Desire "
            "imbues some item when she first shows it to others, here or far "
            "away. Someone must be there to take the vis before sunset melts "
            "it. With 1 pawn of Muto.",
        ),
        (
            "Change of Heart (Muto)",
            "Muto",
            1,
            "",
            "The same quester's item; with 3 pawns of Mentem.",
        ),
        (
            "The Fur of the Saturated Beast",
            "Aquam",
            3,
            "Summer",
            "On St. John's Day the Lion's pool is charged. A sanguine beast, "
            "most predators, swims in it and shakes itself, and the drops are "
            "the vis. Lexora usually catches them in a sheet for the covenant.",
        ),
        (
            "Blood on the Talons",
            "Animal",
            3,
            "Summer",
            "One early summer day a white dove flies over and perches on the "
            "tower. The magi loose their falcons; if one brings it down, the "
            "blood on its talons is the vis.",
        ),
        (
            "The Blooming of Love",
            "Herbam",
            4,
            "Spring",
            "A pawn in each of four plants in the Night Garden: a tall tree of "
            "yellow blossom; a small green herb whose vapour forces a Stamina "
            "+ Concentration stress roll against 9 or sleep; black berries on "
            "a purple creeper over a grave, where nightingales sing; a red "
            "spiky shrub with razor leaves, taken only after at least two pairs "
            "of lovers dance a folk dance round it. Grogs escort four newly "
            "adult men and four women before dawn. The places and the "
            "resistance change each year.",
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
            "The Rainbow Leaves",
            "Muto",
            7,
            "Golden leaves from the Highest Tree.",
        ),
        (
            "The Indigo Pawns of Toulouse",
            "Rego",
            7,
            "Indigo wooden chess pawns from Tolosa Paratge, not yet used.",
        ),
        (
            "The Beast's Bath Water",
            "Aquam",
            5,
            "Handkerchief-sized linen cloths that never dry.",
        ),
        (
            "The Sanguine Roses",
            "Animal",
            9,
            "Coin-sized wooden roses of a blood-red hue that Xenophanes carves "
            "to hold the blood from the talons.",
        ),
        (
            "Sands of the Mistral",
            "Auram",
            15,
            "Pinkish sand in tiny glass vials, from a great fall the wind "
            "brought from Africa, traded round the Tribunal by the Coenobium "
            "and Stella Durus.",
        ),
        (
            "The Fiery Liquor of Vazerac",
            "Ignem",
            2,
            "Tiny wax-stopped bottles of a strong spirit like liquid fire.",
        ),
        (
            "The Wondrous Poems",
            "Imaginem",
            8,
            "Clay flasks each holding a troubadour's poem, which whispers "
            "itself to the wind when opened. From Tolosa Paratge in better "
            "days.",
        ),
        (
            "The Frozen Kisses",
            "Imaginem",
            2,
            "Beatriz's embrace, moved onto two pieces of yellow silk.",
        ),
        (
            "The Pawns of Healing",
            "Corpus",
            25,
            "Small bone chess pieces, traded from Redcaps.",
        ),
        (
            "The Changing Hearts",
            "Mentem",
            4,
            "Coin-sized stitched hearts of rose petal that beat in the hand and "
            "change with the holder's mood.",
        ),
        (
            "The Perfumed Spirals",
            "Vim",
            25,
            "Purple metal spirals distilled from the aura, smelling of violets "
            "and delicious to lick, in a leather bag; vermin, and once grogs, "
            "have tried to eat them.",
        ),
    ):
        add_possession(
            covenant,
            "vis_store",
            name,
            art=art,
            pawns=pawns,
            description=f"{words} In locked chests in the council chamber.",
        )


def _charter(covenant: Covenant) -> None:
    charter = covenant.charter_of_covenant
    charter.name = "The Charter of Jardin"
    charter.preamble = (
        "Under the Provençal Peripheral Code a sworn charter binds in law, and "
        "breaking it can be tried as a Low Crime at Tribunal, so outsiders may "
        "be asked to rule on it."
    )
    charter.clauses = [
        CharterClause(number=str(number), text=text)
        for number, text in enumerate(CHARTER, 1)
    ]


def _village(provence: Provence, site: Neighbour) -> None:
    b = provence.b
    vineyards = provence.places["cahors_vineyards"]
    village = b.town(
        "Belfort du Quercy",
        place=vineyards,
        population=96,
        ruler="Joia du Lua, as chatelaine",
        answers_to=None,
        summary=paragraphs(
            "A prosperous village of well-built cottages on the slopes a mile "
            "from the Toulouse road, grown round the manor the Montdumercs "
            "built in 1130. Most of its people are the covenant's folk, who "
            "tend market gardens, vines and sheep and who hold themselves Lady "
            "Joia's subjects. They know, or guess, that she is a magician, and "
            "keep it from outsiders. There is no inn, but cottagers will take a "
            "respectable traveller for a few coins.",
            "Three-quarters are Cathars, the rest faithful to the Church, and "
            "the line runs through families without quarrel. Even the curé "
            "would shelter the heretics, and the Cathars file into church for "
            "the Bishop of Cahors's visitation to help him. The village has a "
            "Dominion aura of 1.",
        ),
    )
    chapel = b.church(
        "Chapel of Saint Desiderius",
        place=vineyards,
        summary="A tiny red-brick chapel to the Merovingian bishop of Cahors, "
        "showing what the grape has earned. Father Augustine says Sunday mass "
        "to a small flock and hears confession at Easter, Christmas and the "
        "saint's day, November 15th. Every magus but Lexora comes on Easter "
        "Sunday. Dominion aura 2, 4 at the altar, 1 in the graveyard, where "
        "goats graze.",
    )
    barn = b.place(
        "The Unaud Barn",
        inside=vineyards,
        realm="Divine",
        aura=3,
        known="Locally",
        summary="A barn of stone and wood by the Unaud house, where the Cathars "
        "have long prayed; hence its Dominion aura of 3. Raissa Unaud, the "
        "family's ancient matriarch, is a Perfecta and a good friend of "
        "Xenophanes, though she mildly disapproves of magic. Other Perfecti "
        "stay with the clan.",
    )
    vazerac = b.town(
        "Vazerac",
        place=vineyards,
        council=12,
        summary="A black-wine village west of Jardin with no lord: twelve "
        "consuls, men and women born there, run it. They know a little of the "
        "Order.",
    )
    b.link(site, "places", village, "The village below")
    b.link(site, "places", chapel, "The village's chapel")
    b.link(site, "places", barn, "The Cathars' meeting place")
    b.link(site, "places", vazerac, "Sells The Fiery Liquor")


def _creatures(
    b: Builder,
    covenant: Covenant,
    site: Neighbour,
    wood: Neighbour,
    people: dict[str, Character],
) -> None:
    emotion = b.creature(
        "The Emotion on the Lake",
        page="p. 58",
        realm="Faerie",
        might=50,
        place=site,
        level=2,
        tires=False,
        appearance="An allegory of what bars the quester from Love: a knight "
        "in red armor for wrath, a succubus for lust, a green-eyed monster for "
        "envy.",
        notes=paragraphs(
            "Built from the Personality Trait the player judges the greatest "
            "obstacle (or Intelligence, as Reason, if none fits): Initiative "
            "equal to the Trait, Attack 3 times it, Defense 9 + it, Damage "
            "equal to it, Soak it + 1. No Fatigue Levels; Body Levels OK, 0 "
            "(1-5), -3 (6-10), -5 (11-15), Dead (16+).",
            "An ordinary fight in which spells can be cast, but hand to hand. "
            "The quester uses weapon statistics, without the weapon Ability: "
            "any Ability, Virtue or Trait that opposes the emotion stands in "
            "(a Minor Virtue counts 3, a Major 9). Armor gives no Protection; "
            "Soak and shields work.",
            "Beatriz, Stubborn +3, met a mule: Init +3, Attack +9, Defense "
            "+12, Damage +3, Soak +4. Her Minor Magical Focus stood in for "
            "Single Weapon at 3, and she lost.",
        ),
    )
    panthera = b.creature(
        "Panthera the Terrible",
        page="pp. 41, 44",
        realm="Magic",
        place=site,
        appearance="An immense, red-toothed predator.",
        notes="A Great Beast of Clan Maruhs. The book gives no statistics.",
        secrets=[
            titled(
                "Who Panthera was",
                "A lion-heartbeast Bjornaer who took the pool from shapeshifters "
                "in the early tenth century, then passed into Final Twilight "
                "at the pool.",
            ),
            titled(
                "Androcles's hunt",
                "Androcles came hunting Panthera's ancestor site.",
            ),
            titled(
                "Lexora's search",
                "Lexora means to seek Panthera for the House's Inner Mysteries.",
            ),
            titled(
                "Panthera's return",
                "He may return and find his pool corrupted.",
            ),
        ],
    )
    skullface = b.creature(
        "Skullface",
        page="p. 67",
        realm="Faerie",
        form="Imaginem",
        appearance="Her true form is unknown; a loved one's face turns to a "
        "hideous skull.",
        notes="A relatively powerful spirit of the County of Toulouse. She "
        "makes a loved face look like a skull to her victim, drives the pair "
        "apart with her Guide power, then helps a new love of equal strength "
        "to grow. Some Merinita say she is why fortunetellers read death as "
        "change. The book gives no statistics.",
        secrets=[
            titled(
                "Skullface's return",
                "She escaped through the Aegis on the night Beatriz failed, "
                "and has come back to Jardin for a new victim.",
            ),
        ],
    )
    auranja = b.creature(
        "Auranja",
        page="p. 46",
        realm="Magic",
        appearance="A big ginger tom who basks on the stable roof.",
        notes="John the Gardener's cat, a magical cat of unknown powers and "
        "Hypatia's lover. The book gives no statistics.",
        secrets=[
            titled(
                "Auranja and the Door",
                "A power lets him walk through the Door Marked Summer, and he "
                "gossips with the cats of the region about what he hears there.",
            ),
        ],
    )
    tibout = b.creature(
        "Tibout",
        page="p. 46",
        realm="Magic",
        notes="The magical cat companion of the bearded minstrel Izarns. The "
        "book gives no statistics.",
        secrets=[
            titled(
                "Tibout's gossip",
                "He tells his master the low gossip he picks up from cats.",
            ),
        ],
    )
    b.link(covenant, "creatures", emotion, "On the Lake of the Night Garden")
    b.link(covenant, "creatures", panthera, "Great Beast of the pool")
    b.link(covenant, "creatures", skullface, "Escaped from the Garden")
    b.link(covenant, "creatures", auranja, "Lives in the stables")
    b.link(people["john"], "creatures", auranja, "His cat")
    b.link(auranja, "creatures", tibout, "Gossips with him")
    b.link(wood, "covenants", covenant, "Jardin gathers the Highest Leaf here")


def _familiars(b: Builder, people: dict[str, Character]) -> None:
    hypatia = b.creature(
        "Hypatia",
        page="p. 45",
        realm="Magic",
        might=10,
        form="Vim",
        size=-3,
        season="Summer",
        source=SOURCE,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(0, 1, -2, -4, -7, 0, 3, 4),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Friend",
                "Common Sense",
                "Perfect Balance",
                vf_puissant("Awareness"),
                "Sharp Ears",
                "Tough",
                ("True Friend", {"detail": "Xenophanes"}),
                "Unaffected by The Gift",
                "Nocturnal",
                ("Poor {characteristic}", {"characteristic": "Communication"}),
                "Weak Characteristics",
                "Weak Characteristics",
                "Weak Characteristics",
                "Greater Power",
                "Improved Abilities",
                "Improved Powers",
                "Lesser Power",
                "Lesser Power",
            ],
            "abilities": [
                ("Area Lore: Cahors", 3, "hunting spots"),
                ("Athletics", 5, "jumping"),
                ("Awareness", 7, "at night"),
                ("Brawl", 4, "bite"),
                ("Living Language: High German", 5, "Alpine"),
                ("Hunt", 6, "mice"),
                ("Dead Language: Latin", 5, "creative insults"),
                ("Magic Lore", 3, "animals"),
                ("Magic Theory", 3, "spells"),
                ("Living Language: Occitan", 3, "ask for food"),
                ("Organization Lore: Jardin", 5, "animals"),
                ("Organization Lore: Order of Hermes", 3, "familiars"),
                ("Penetration", 5, "Mentem"),
                ("Stealth", 7, "stalking"),
                ("Survival", 4, "shelter"),
            ],
            "traits": {
                "Loyal to Xenophanes": 3,
                "Cat": 3,
                "Sardonic": 2,
                "Curious": 1,
            },
        },
        attacks=[
            b.attack("Dodge", 4, None, 10, None),
            b.attack("Bite", 4, 12, 11, -6),
        ],
        soak=3,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Aura of Rightful Authority",
                2,
                2,
                "Mentem",
                rtd=("Eye", "Sun", "Individual"),
                does="Inclines humans to obey and steadies them at the shock "
                "of a talking cat (ArM5 p. 151).",
            ),
            b.power(
                "Humans Are Easily Misplaced",
                0,
                -3,
                "Corpus",
                rtd=("Arcane Connection", "Concentration", "Individual"),
                penetration_bonus=10,
                does="A feline Inexorable Search (ArM5 p. 131), by a map of "
                "scents and textures; she rubs on humans to mark them. 4 "
                "Mastery points reduced its Might cost.",
            ),
            b.power(
                "Master of the Undergrowth",
                2,
                0,
                "Herbam",
                rtd=("Touch", "Sun", "Group"),
                does="A feline Intuition of the Forest (ArM5 p. 136).",
            ),
            b.power(
                "Pass the Unyielding Portal",
                1,
                2,
                "Herbam",
                rtd=("Touch", "Diameter", "Individual"),
                does="For doors with no human to open them (ArM5 p. 137).",
            ),
            b.power(
                "Prying Eyes",
                1,
                2,
                "Imaginem",
                rtd=("Touch", "Concentration", "Room"),
                penetration_bonus=5,
                does="Looks inside buildings, a cat on the roof seeing through "
                "it (ArM5 p. 144).",
            ),
            b.power(
                "The Wise Guide",
                0,
                2,
                "Mentem",
                rtd=("Voice", "Concentration", "Group"),
                level=30,
                penetration_bonus=10,
                does="Nudges Xenophanes to act sensibly, as if he had Common "
                "Sense, with no compulsion and no Warping, being tailored to "
                "him. ReMe 30 (base 5, +2 Voice, +1 Concentration, +2 Group; 3 "
                "Mastery points on cost, 1 on Init).",
            ),
        ],
        appearance="An unremarkable female black cat with a snub nose, green "
        "eyes and a kink in her tail, older and leaner than the village cats.",
        notes="A sardonic commentator with far more wits than her magus. Vis: "
        "2 pawns of Vim. Bond: Mental Communication, both ways, complex "
        "thoughts, unlimited; Speech, unlimited and maintaining concentration, "
        "which Xenophanes can withdraw for a time. She knows not to speak "
        "before visitors unless they wear red caps. Awareness carries +2 from "
        "Puissant Awareness.",
    )
    nec = b.creature(
        "Nec",
        page="p. 49",
        realm="Magic",
        might=10,
        form="Animal",
        size=1,
        season="Summer",
        source=SOURCE,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(1, 3, 1, 1, 2, 2, 2, 2),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Friend",
                "Improved Characteristics",
                "Improved Characteristics",
                "Improved Characteristics",
                "Improved Characteristics",
                "Improved Characteristics",
                "Long-Winded",
                "Sharp Ears",
                ("True Friend", {"detail": "Ahenobarbus"}),
                "Unaffected by The Gift",
                "Black Sheep",
                "Proud",
                ("Careless with {ability}", {"ability": "Stealth"}),
                "Gigantic",
                "Greater Power",
                "Improved Abilities",
                "Improved Abilities",
                "Improved Abilities",
                "Improved Abilities",
                "Improved Attack",
                "Improved Attack",
                "Improved Damage",
                "Improved Damage",
                "Improved Damage",
                "Improved Defense",
                "Improved Defense",
                "Improved Fatigue",
                "Improved Fatigue",
                "Improved Fatigue",
                "Improved Initiative",
                "Improved Powers",
                "Improved Powers",
                "Improved Powers",
                "Improved Powers",
                "Improved Soak",
                vf_minor("Tough"),
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
                "Reduced Might",
            ],
            "abilities": [
                ("Area Lore: Cahors", 6, "covenant lands"),
                ("Area Lore: Coeris Region", 6, "pack territory"),
                ("Athletics", 3, "running"),
                ("Brawl", 6, "bite"),
                ("Faerie Lore", 1, "wolves"),
                ("Folk Ken", 3, "Tremere magi"),
                ("Hunt", 7, "in a pack"),
                ("Dead Language: Latin", 5, "Hermetic usage"),
                ("Magic Lore", 1, "wolves"),
                ("Magic Theory", 4, "Mentem"),
                ("Living Language: Occitan", 4, "peasant speech"),
                ("Organization Lore: Jardin", 4, "familiars"),
                ("Organization Lore: Order of Hermes", 3, "House Tremere"),
                ("Penetration", 5, "Mentem"),
                ("Living Language: South Slavonic", 5, "Bulgarian dialect"),
                ("Stealth", 6, "forests"),
                ("Swim", 1, "lakes"),
                ("Survival", 6, "forests"),
            ],
            "traits": {"Loyal to Ahenobarbus": 3, "Wolf": 3},
        },
        attacks=[
            b.attack("Dodge", 2, None, 5, None),
            b.attack("Bite", 5, 16, 14, 12),
        ],
        soak=7,
        fatigue_levels="OK, 0/0, -1/-1, -3/-3, -5, Unconscious",
        powers=[
            b.power(
                "Theft of Voice",
                1,
                10,
                "Mentem",
                does="Steals the voice of a human who meets her eye until the "
                "next sunrise, as The Captive Voice (ArM5 p. 147).",
            ),
            b.power(
                "Eyes Like Lanterns",
                1,
                7,
                "Mentem",
                rtd=("Eye", "Concentration", ""),
                level=10,
                does="Holding eye contact, paralyzes a victim who fails a Brave "
                "roll against 9; if attacked, shaken or distracted he may roll "
                "against 6 each round to break free. ReMe 10 (base 4, +1 Eye, "
                "+1 Concentration).",
            ),
            b.power(
                "Leave No Trace",
                0,
                2,
                "Terram",
                does="She leaves no tracks when running, as The Trackless Step "
                "(ArM5 p. 155).",
            ),
        ],
        appearance="A magnificent white she-wolf with large eyes, far bigger "
        "than any natural wolf.",
        notes="Of the white wolves of Houses of Hermes: True Lineages p. 129. "
        "She came from Transylvania to escape trouble in her pack, which may "
        "yet follow; she allows Ahenobarbus no superiority and longs to outdo "
        "Lexora's heartbeast. She leads a small wolf pack that spies for him, "
        "and the villagers think her a big friendly dog. She understands "
        "Latin and South Slavonic but cannot speak them. Careless with Stealth "
        "is from Grogs p. 77. Vis: 2 pawns of Animal in her tail. Bond: Mental "
        "Communication, both ways, complex thoughts, unlimited.",
    )
    falcon = b.creature(
        "Fauconrouge",
        page="p. 52",
        realm="Magic",
        might=24,
        form="Corpus",
        size=-3,
        season="Summer",
        source=SOURCE,
        confidence=(2, 5),
        block={
            "characteristics": characteristics(-1, 3, -1, 0, -6, 2, 2, 6),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Friend",
                "Improved Characteristics",
                "Improved Characteristics",
                "Improved Characteristics",
                "Keen Vision",
                ("True Friend", {"detail": "Alyssa"}),
                ("Fish Out of Water {terrain}", {"terrain": "flying"}),
                "Fragile Constitution",
                "Reckless (Minor)",
                "Gift of Speech",
                "Improved Abilities",
                "Improved Confidence",
                "Improved Defense",
                "Improved Defense",
                "Improved Defense",
                "Improved Initiative",
                "Improved Initiative",
                "Improved Initiative",
                "Improved Fatigue",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Might",
                "Improved Soak",
                "Personal Power",
                "Personal Power",
            ],
            "abilities": [
                ("Living Language: Arabic", 3, "Iberian"),
                ("Area Lore: County of Toulouse", 2, "flight routes"),
                ("Athletics", 7, "swift flight"),
                ("Awareness", 6, "spotting prey"),
                ("Brawl", 4, "talons"),
                ("Hunt", 5, "game birds"),
                ("Magic Lore", 1, "animals"),
                ("Magic Theory", 2, "spells"),
                ("Living Language: Occitan", 5, "nobles"),
                ("Organization Lore: Jardin", 2, "familiars"),
                ("Organization Lore: Order of Hermes", 1, "House Bonisagus"),
                ("Dead Language: Latin", 5, "academic terms"),
                ("Survival", 3, "cold climes"),
            ],
        },
        attacks=[
            b.attack("Beak", 6, 9, 11, -5),
            b.attack("Talons", 14, 9, 20, -4),
        ],
        soak=0,
        fatigue_levels="OK, 0/0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Human Shape",
                1,
                4,
                "Corpus",
                rtd=("", "Sun", ""),
                does="Takes human shape (Realms of Power: Magic p. 39).",
            ),
            b.power(
                "Iron Grip of the Raptor",
                0,
                4,
                "Terram",
                rtd=("Touch", "Sun", ""),
                level=15,
                does="Handles and carries things as with human hands and "
                "Strength +5, concentrating for anything but carrying, even to "
                "let go. ReTe 15 (base 3, +1 Touch, +2 Sun, +1 Const); Personal "
                "Power of 15 levels, cost reduced by 2.",
            ),
        ],
        appearance="A magnificent red gyrfalcon.",
        notes="Fish Out of Water (flying) is from Grogs p. 80. Vis: 5 pawns of "
        "Corpus in his talons. Bond: Mental Communication, constant, complex "
        "images and emotions. Binding Total 35.",
    )
    saga = b.saga
    for creature, key, species, cords, total in (
        (hypatia, "xenophanes", "A black cat, a magical beast", (1, 3, 0), 0),
        (nec, "ahenobarbus", "A white wolf, a magical beast", (2, 2, 2), 0),
        (falcon, "alyssa", "A gyrfalcon, a magical beast", (1, 2, 2), 35),
    ):
        partner = people[key]
        attacks = [a for a in creature.attacks if a.attack is not None]
        familiar = Familiar(
            id=storage.generate_unique_id(
                creature.name, [f.id for f in saga.familiars]
            ),
            character_id=partner.id,
            name=creature.name,
            species=species,
            magic_might=creature.might,
            size=creature.size,
            virtues_flaws=[
                virtue_flaw_from_block(("True Friend", {"detail": partner.name}))
            ],
            personality_traits=[ScoredTrait(f"Loyal to {partner.name}", 3)],
            golden_cord=cords[0],
            silver_cord=cords[1],
            bronze_cord=cords[2],
            binding_lab_total=total,
            characteristics=creature.characteristics,
            base_soak=creature.soak,
            abilities=list(creature.abilities),
            natural_weapons=[
                Possession(
                    id=storage.generate_unique_id(a.name, []),
                    kind="weapon",
                    name=a.name,
                    weapon_init=a.init,
                    weapon_attack=a.attack,
                    weapon_defense=a.defense,
                    weapon_damage=a.damage,
                )
                for a in attacks
            ],
        )
        saga.familiars.append(familiar)
        b.link(partner, "creatures", creature, "Familiar")


def _person(provence: Provence, name: str) -> Character:
    """The pack's character of that name, made by any part."""
    for character in provence.b.saga.characters:
        if character.name == name:
            return character
    raise LookupError(f"No character named {name!r} yet")


def _links(
    provence: Provence, covenant: Covenant, people: dict[str, Character]
) -> None:
    b = provence.b
    for key, note in (
        ("stella_durus", "Excellent relations; a likely voting ally"),
        ("bellaquin", "Old ally, now more distant"),
        ("ostal_des_exiles", "Joia and Gilbert are allies"),
        ("miniata_sophia", "Mystical hostility to Xenophanes"),
        ("coenobium", "Soured by Joia's quarrel with Alazais"),
        ("tolosa_paratge", "A lost ally, now under siege"),
        ("aedes_mercurii", "Only Lexora visits"),
        ("ara_maxima_nova", "Lexora's friends"),
        ("castra_solis", "Lexora and Ahenobarbus want closer ties"),
    ):
        b.link(covenant, "covenants", provence.covenants[key], note)
    b.link(covenant, "characters", _person(provence, "Mariola"), "A friend, cut off")
    for key, name, note in (
        ("ahenobarbus", "Protendus", "His regional commander, whom he avoids"),
        ("ahenobarbus", "Artemis", "Respects her by reputation"),
        ("ahenobarbus", "Garsenda of Lariander", "Wants her under his wing"),
        ("joia", "Gilbert", "Allies"),
        ("joia", "Alazais of Mercere", "Rival beauties"),
        ("joia", "Valgravian", "A friend"),
        ("joia", "Jean Marie of Jerbiton", "Writes to her on Courtly Love"),
        ("joia", "Garus", "A friend"),
        ("joia", "Troya", "A friend"),
        ("xenophanes", "Leonarda", "Sister in the same parens, who detests him"),
        ("alyssa", "Carolus St. Tropez", "Her enemy and her secret love"),
        ("alyssa", "Popilia", "Outraged by her last visit"),
        ("lexora", "Guillermo of Mercere", "She is friends with his covenant"),
    ):
        b.link(people[key], "characters", _person(provence, name), note)
    b.link(people["joia"], "characters", people["beatriz"], "Her former apprentice")
    b.link(people["joia"], "characters", people["serena"], "Her niece")
    b.link(people["ahenobarbus"], "characters", people["serena"], "Loves her")
