"""Full stats for the magi Guardians of the Forests prints stat blocks for."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import Character
from ..builder import Builder, StatBlock

if TYPE_CHECKING:
    from . import Rhine

FAST = "Fast Casting"
MULTIPLE = "Multiple Casting"
PENETRATION = "Penetration"
QUIET = "Quiet Casting"
STILL = "Still Casting"


def _stats(
    b: Builder,
    character: Character,
    block: StatBlock,
    *,
    masteries: dict[str, tuple[str, ...]] | None = None,
) -> None:
    """`b.stats`, with the Mastery Abilities bought on each spell."""
    b.stats(character, {**block, "masteries": masteries or {}})


def build(rhine: Rhine) -> None:
    b = rhine.b
    _stats(
        b,
        rhine.magi["philippus_niger"],
        {
            "characteristics": {
                "intelligence": 5,
                "perception": -2,
                "presence": -1,
                "communication": 1,
                "strength": -1,
                "stamina": 2,
                "dexterity": -2,
                "quickness": -1,
            },
            "aging_points": {"strength": 1, "stamina": 2, "dexterity": 2},
            "size": 0,
            "confidence": (3, 5),
            "decrepitude": (2, 2),
            "warping": (8, 5),
            "apparent_age": 90,
            "virtues_flaws": [
                "The Gift",
                "Archmage (Rhine Tribunal)",
                "Mythic Blood",
                ("Affinity with {ability}", {"ability": "penetration"}),
                ("Affinity with {art}", {"art": "perdo"}),
                ("Great {characteristic}", {"characteristic": "intelligence"}),
                ("Great {characteristic}", {"characteristic": "intelligence"}),
                ("Minor Magical Focus", {"focus": "dispelling"}),
                ("Puissant {art}", {"art": "perdo"}),
                "Driven",
                "Enemies",
                "Ambitious (Minor)",
                ("Deficient Form", {"form": "imaginem"}),
            ],
            "traits": {
                "Alarmist": 3,
                "Condescending": 3,
                "Obsessive": 2,
                "Cool-Tempered": -1,
                "Cheerful": -3,
            },
            "reputations": {
                "Master of Perdo (Hermetic)": 5,
                "Archmage (Hermetic)": 4,
                "Don't Mess with this Magus (Hermetic)": 4,
            },
            "abilities": [
                ("Awareness", 2, "when alone"),
                ("Artes Liberales", 3, "scribing"),
                ("Brawl", 3, "dagger"),
                ("Chirurgy", 2, "magical wounds"),
                ("Code of Hermes", 4, "hedge wizards"),
                ("Concentration", 4, "maintaining spells"),
                ("Dominion Lore", 2, "divine creatures"),
                ("Organization Lore: Durenmar", 3, "tractatus"),
                ("Faerie Lore", 2, "Norse fae"),
                ("Finesse", 6, "Perdo"),
                ("Folk Ken", 3, "body language"),
                ("Living Language: High German", 5, "orders"),
                ("Guile", 2, "peasants"),
                ("Infernal Lore", 4, "earthly demons"),
                ("Intrigue", 3, "Hermetic"),
                ("Dead Language: Latin", 5, "speeches"),
                ("Leadership", 2, "grogs"),
                ("Magic Lore", 5, "Norse wizards"),
                ("Magic Theory", 8, "inventing spells"),
                ("Organization Lore: Order of Hermes", 4, "Flambeau"),
                ("Parma Magica", 7, "Corpus"),
                ("Penetration", 8, "Perdo"),
                ("Philosophiae", 4, "metaphysics"),
                ("Profession: Scribe", 3, "about Vim"),
                ("Ride", 2, "speed"),
                ("Single Weapon", 3, "long sword"),
                ("Teaching", 4, "Arts"),
                ("Theology: Christian", 3, "souls"),
                ("Living Language: East Norse", 2, "threats"),
            ],
            "arts": {
                "Creo": 10,
                "Intellego": 15,
                "Muto": 10,
                "Perdo": 35,
                "Rego": 12,
                "Animal": 7,
                "Aquam": 7,
                "Auram": 7,
                "Corpus": 15,
                "Herbam": 7,
                "Ignem": 8,
                "Imaginem": 5,
                "Mentem": 15,
                "Terram": 7,
                "Vim": 20,
            },
            "spells": [
                ("Agony of the Beast", "PeAn", 15, 0),
                ("Cripple the Howling Wolf", "PeAn", 25, 1),
                ("Curse of the Desert", "PeAq", 25, 0),
                ("Chaos of the Angry Waves", "ReAq", 30, 0),
                ("Sight of the True Form", "InCo", 15, 0),
                ("The Wound That Weeps", "PeCo", 15, 0),
                ("Bane of the Decrepit Body", "PeCo", 25, 0),
                ("Curse of the Leprous Flesh", "PeCo", 25, 0),
                ("Evisceration of a Thousand Knives", "PeCo", 30, 0),
                ("Clenching Grasp of the Crushed Heart", "PeCo", 40, 2),
                ("The Leap of Homecoming", "ReCo", 35, 0),
                ("The Great Rot", "PeHe", 25, 0),
                ("Wizard's Icy Grip", "PeIg", 30, 1),
                ("Ward Against Heat and Flames", "ReIg", 25, 0),
                ("Blessing of Childlike Bliss", "PeMe", 25, 0),
                ("Passion's Lost Feeling", "PeMe", 25, 1),
                ("Lay to Rest the Haunting Spirit", "PeMe", 30, 0),
                ("Aura of Rightful Authority", "ReMe", 20, 2),
                ("Scent of Peaceful Slumber", "ReMe", 20, 0),
                ("Pit of the Gaping Earth", "PeTe", 15, 0),
                ("End of the Mighty Castle", "PeTe", 25, 0),
                ("Flaws of the Weaponsmith", "PeTe", 30, 1),
                ("Demon's Eternal Oblivion", "PeVi", 50, 2),
                ("The Heathen Witch Reborn", "PeVi", 25, 0),
                ("Wind of Mundane Silence", "PeVi", 50, 3),
                ("Dreadful Bane of the Fae", "PeVi", 50, 1),
                ("Sap the Griffon's Strength", "PeVi", 50, 1),
                ("Shattering the Malicious Thurisaz", "PeVi", 30, 1),
                ("Shattering the Malicious Kauno", "PeVi", 50, 1),
            ],
            "notes": (
                "Equipment: clothes, a dagger and a long sword; "
                "Encumbrance 1 (1). Talisman: the Knife of Human Bone; he "
                "also owns the Wizard's Bridle and the Subtle Chain. "
                "Familiar: Sordus, a basilisk. Twilight Scars: he seems to "
                "swell when angry, his shadow sometimes moves of itself, he "
                "knows true gold from false, only boys are born where he "
                "has lived a year, he sours wine, loud noise pains him, "
                "black animals gather round him outdoors, and flames dim "
                "when he comes in. His focus and his Ambitious Flaw come "
                "with his Mythic Blood, whose feat lets him smell magic. "
                "Chaos of the Angry Waves came from a Twilight. He knows "
                "Demon's Eternal Oblivion and Wind of Mundane Silence at "
                "levels 25 and 50, and Dreadful Bane of the Fae and Sap the "
                "Griffon's Strength at 30 and 50. His two Shattering spells "
                "are versions of Shattering the Malicious (Rune), each "
                "aimed at one rune. From forty years past his Gauntlet he "
                "learned his spells as laboratory projects. The book prints "
                "Encumbrance 3 (3), Chaos of the Angry Waves 20, Flaws of "
                "the Weaponsmith 25 and one Shattering the Malicious Rune "
                "(30 and 50); the errata correct them."
            ),
        },
        masteries={
            "Cripple the Howling Wolf": (MULTIPLE,),
            "Clenching Grasp of the Crushed Heart": (FAST, PENETRATION),
            "Wizard's Icy Grip": (FAST,),
            "Passion's Lost Feeling": (MULTIPLE,),
            "Aura of Rightful Authority": (QUIET, STILL),
            "Flaws of the Weaponsmith": (FAST,),
            "Demon's Eternal Oblivion": (PENETRATION, FAST),
            "Wind of Mundane Silence": (PENETRATION, FAST, STILL),
            "Dreadful Bane of the Fae": (PENETRATION,),
            "Sap the Griffon's Strength": (PENETRATION,),
            "Shattering the Malicious Thurisaz": (FAST,),
            "Shattering the Malicious Kauno": (FAST,),
        },
    )
    _stats(
        b,
        rhine.magi["imanitos_mendax"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 1,
                "presence": 2,
                "communication": 2,
                "strength": -1,
                "stamina": 1,
                "dexterity": -1,
                "quickness": -2,
            },
            "aging_points": {"quickness": 1},
            "size": 0,
            "confidence": (2, 5),
            "decrepitude": (0, 2),
            "warping": (4, 3),
            "apparent_age": 39,
            "virtues_flaws": [
                "The Gift",
                "Master (Rhine Tribunal)",
                "Gentle Gift",
                ("Affinity with {ability}", {"ability": "finesse"}),
                ("Affinity with {ability}", {"ability": "guile"}),
                ("Affinity with {art}", {"art": "mentem"}),
                ("{gild} Trained", {"gild": "Apple Gild"}),
                ("Minor Magical Focus", {"focus": "deception"}),
                "Quiet Magic",
                "Self-Confident",
                "Social Contacts",
                "Subtle Magic",
                "Dark Secret",
                "Lecherous",
                "Compulsion (Minor)",
                ("Deficient Form", {"form": "animal"}),
                ("Deficient Form", {"form": "ignem"}),
                "Lesser Malediction",
            ],
            "traits": {"Lustful": 3, "Scheming": 2, "Brave": -1},
            "reputations": {
                "Amoral (Hermetic)": 2,
                "Master of minor Mentem spells (Hermetic)": 2,
            },
            "abilities": [
                ("Artes Liberales", 3, "forging handwriting"),
                ("Awareness", 1, "in crowds"),
                ("Bargain", 1, "ladies of negotiable affection"),
                ("Brawl", 1, "dagger"),
                ("Carouse", 1, "staying sober"),
                ("Charm", 4, "women"),
                ("Code of Hermes", 2, "oaths"),
                ("Concentration", 3, "Mentem spells"),
                ("Etiquette", 2, "nobility"),
                ("Organization Lore: Fengheld", 1, "master magi"),
                ("Finesse", 3, "Mentem"),
                ("Living Language: French", 2, "langue d'oc"),
                ("Folk Ken", 3, "nobility"),
                ("Living Language: Low German", 6, "Saxon"),
                ("Guile", 7, "plots"),
                ("Infernal Lore", 2, "servile demons"),
                ("Intrigue", 3, "Hermetic politics"),
                ("Dead Language: Latin", 5, "sycophancy"),
                ("Leadership", 1, "employees"),
                ("Area Lore: Lübeck", 3, "corruption"),
                ("Magic Theory", 5, "inventing spells"),
                ("Music", 1, "lute"),
                ("Organization Lore: Order of Hermes", 2, "Lindengilde"),
                ("Parma Magica", 4, "Mentem"),
                ("Penetration", 2, "Mentem"),
                ("Philosophiae", 1, "morals"),
                ("Profession: Tavern/Brothel Owner", 1, "accounts"),
                ("Profession: Scribe", 2, "copying books"),
                ("Ride", 1, "keeping level"),
                ("Teaching", 1, "Arts"),
                ("Organization Lore: Waddenzee", 2, "piracy"),
                ("Living Language: West Slavonic", 2, "Sorbian"),
            ],
            "arts": {
                "Creo": 6,
                "Intellego": 9,
                "Muto": 7,
                "Perdo": 8,
                "Rego": 9,
                "Animal": 3,
                "Aquam": 5,
                "Auram": 5,
                "Corpus": 5,
                "Herbam": 3,
                "Ignem": 4,
                "Imaginem": 9,
                "Mentem": 17,
                "Terram": 5,
                "Vim": 11,
            },
            "spells": [
                ("Whispering Winds", "InAu", 15, 0),
                ("Prying Eyes", "InIm", 5, 0),
                ("Aura of the Ennobled Presence", "MuIm", 10, 1),
                ("Disguise of the Transformed Image", "MuIm", 15, 0),
                ("Invisibility of the Standing Wizard", "PeIm", 15, 0),
                ("Rising Passion", "CrMe", 15, 1),
                ("Gossip of the Marketplace", "CrMe(Re)", 20, 0),
                ("Weight of a Thousand Hells", "CrMe", 25, 0),
                ("Perception of the Conflicting Motives", "InMe", 15, 0),
                ("Frosty Breath of the Spoken Lie", "InMe", 20, 0),
                ("Posing the Silent Question", "InMe", 20, 1),
                ("Recollection of Memories Never Quite Lived", "MuMe", 4, 0),
                ("Seed of Betrayal", "MuMe", 15, 0),
                ("The Blinded Sentry", "PeMe", 5, 0),
                ("Trust of Childlike Faith", "PeMe", 10, 0),
                ("Loss of But a Moment's Memory", "PeMe", 15, 0),
                ("The Invisible Eye Revealed", "InVi", 20, 0),
                ("Clear Breath of the Consummate Liar", "MuVi(Me)", 20, 0),
                ("Masking the Odor of Magic", "PeVi", 20, 0),
            ],
            "notes": (
                "Equipment: fashionable fine clothes and costly jewellery; "
                "Encumbrance 0 (0). Twilight Scars: a forked tongue he keeps "
                "hidden, a voice people want to hear, and a faint smell of "
                "funeral incense. His Affinity with Finesse came from a "
                "Twilight, and his Compulsion is lying. He means to make his "
                "serpent-and-ruby ring his talisman. His longevity ritual "
                "gives only +2, but his apparent age rises only on an aging "
                "roll of 7 or more."
            ),
        },
        masteries={
            "Aura of the Ennobled Presence": (QUIET,),
            "Rising Passion": (QUIET,),
            "Posing the Silent Question": (QUIET,),
        },
    )
    _stats(
        b,
        rhine.magi["falke"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 2,
                "presence": 4,
                "communication": 2,
                "strength": -2,
                "stamina": -1,
                "dexterity": 0,
                "quickness": -1,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "warping": (3, 16),
            "apparent_age": 45,
            "virtues_flaws": [
                "The Gift",
                "Master (Rhine Tribunal)",
                ("Major Magical Focus", {"focus": "bodies of water"}),
                ("Affinity with {art}", {"art": "aquam"}),
                "Famous",
                ("Great {characteristic}", {"characteristic": "presence"}),
                "Heartbeast",
                "Improved Characteristics",
                "Inspirational",
                ("{gild} Trained", {"gild": "Linden Gild"}),
                "Piercing Gaze",
                "Optimistic",
                "Study Requirement",
                "Covenant Upbringing",
                ("Deficient Form", {"form": "ignem"}),
                "Slow Caster",
            ],
            "traits": {"Committed to an Ideal": 3, "Cheerful": 2, "Humble": 1},
            "reputations": {
                "Prima of House Bjornaer (Hermetic)": 5,
                "Master of Aquam Magic (Hermetic)": 1,
            },
            "abilities": [
                ("Artes Liberales", 3, "rhetoric"),
                ("Awareness", 2, "vision"),
                ("Bargain", 2, "contracts"),
                ("Charm", 3, "mundanes"),
                ("Code of Hermes", 2, "attitude towards mundanes"),
                ("Concentration", 2, "Aquam spells"),
                ("Dominion Lore", 1, "miracles"),
                ("Folk Ken", 3, "peers"),
                ("Living Language: French", 1, "Norman"),
                ("Living Language: Low German", 5, "Saxon"),
                ("Guile", 1, "good intentions"),
                ("Heartbeast", 3, "in haste"),
                ("Intrigue", 3, "House Bjornaer"),
                ("Dead Language: Latin", 4, "speeches"),
                ("Leadership", 3, "Harmonists"),
                ("Magic Lore", 3, "shapeshifters"),
                ("Magic Theory", 5, "Aquam"),
                ("Organization Lore: Order of Hermes", 4, "House Bjornaer"),
                ("Parma Magica", 3, "Corpus"),
                ("Philosophiae", 2, "ritual spells"),
                ("Swim", 2, "lakes"),
                ("Teaching", 1, "Magic Theory"),
                ("Theology: Christian", 1, "debate"),
                ("Living Language: East Norse", 2, "Danish"),
                ("Living Language: West Slavonic", 2, "Sorbian"),
            ],
            "arts": {
                "Creo": 7,
                "Intellego": 8,
                "Muto": 9,
                "Perdo": 5,
                "Rego": 7,
                "Animal": 5,
                "Aquam": 16,
                "Auram": 6,
                "Corpus": 7,
                "Herbam": 5,
                "Ignem": 4,
                "Imaginem": 6,
                "Mentem": 6,
                "Terram": 5,
                "Vim": 6,
            },
            "spells": [
                ("Mighty Torrent of Water", "CrAq", 20, 0),
                ("Voice of the Lake", "InAq", 25, 0),
                ("Sculpt the Living Water", "MuAq", 20, 0),
                ("Neptune's Imprisoning Arms", "MuAq", 30, 0),
                ("Appease the Queen of Winter", "MuAq", 65, 0),
                ("Break the Oncoming Wave", "ReAq", 10, 0),
                ("Breath of Winter", "ReAq", 15, 0),
                ("Still the Raging Waters", "ReAq", 15, 0),
                ("Chaos of the Angry Waves", "ReAq", 30, 0),
                ("Parting of the Waves", "ReAq", 30, 0),
                ("Broom of the Winds", "CrAu", 15, 0),
                ("In Christ's Footsteps", "ReCo", 5, 0),
                ("Eyes of the Eagle", "InIm", 25, 0),
                ("Aura of the Ennobled Presence", "MuIm", 10, 0),
            ],
            "notes": (
                "Prima of House Bjornaer, Famous since she took the post; "
                "her heartbeast is a silver-grey falcon. Equipment: her "
                "talisman, a silver anklet set with crystal and amber "
                "(attuned +5 to water effects, +3 Corpus), which turns into "
                "a leg-band when she changes shape and can read a person's "
                "motives; Encumbrance 0 (0). Twilight Scar: her feet are "
                "always wet and leave puddles."
            ),
        },
    )
    _stats(
        b,
        rhine.magi["ioannes_acer"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 0,
                "presence": 1,
                "communication": 0,
                "strength": 1,
                "stamina": 1,
                "dexterity": 1,
                "quickness": 0,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "warping": (0, 0),
            "apparent_age": 23,
            "virtues_flaws": [
                "The Gift",
                "Journeyman (Rhine Tribunal)",
                "Flawless Magic",
                ("Deft Form", {"form": "herbam"}),
                ("{gild} Trained", {"gild": "Elder Gild"}),
                "Knight",
                "Skilled Parens",
                ("Special Circumstances", {"circumstance": "when riding"}),
                "Creative Block",
                ("Deleterious Circumstances", {"circumstance": "in a city"}),
                "Reckless (Minor)",
                "Short-Lived Magic",
                "Vow (Minor)",
            ],
            "traits": {"Brave": 3, "Honorable": 3, "Deep Thinker": -2},
            "abilities": [
                ("Animal Handling", 2, "steeds"),
                ("Artes Liberales", 1, "writing poetry"),
                ("Brawl", 3, "punch"),
                ("Charm", 1, "ladies"),
                ("Code of Hermes", 1, "fae"),
                ("Concentration", 1, "Herbam spells"),
                ("Etiquette", 2, "fae"),
                ("Faerie Lore", 2, "knights"),
                ("Faerie Magic", 2, "Herbam spells"),
                ("Finesse", 1, "Rego"),
                ("Living Language: High German", 5, "flowery language"),
                ("Great Weapon", 2, "lance"),
                ("Dead Language: Latin", 4, "about plants"),
                ("Magic Theory", 4, "recognizing spells"),
                ("Organization Lore: Order of Hermes", 2, "Elder Gild"),
                ("Parma Magica", 2, "Rego spells"),
                ("Penetration", 1, "Rego"),
                ("Ride", 2, "Kervus"),
            ],
            "arts": {
                "Creo": 6,
                "Intellego": 1,
                "Muto": 7,
                "Rego": 10,
                "Animal": 3,
                "Corpus": 3,
                "Herbam": 10,
                "Imaginem": 1,
                "Terram": 6,
                "Vim": 3,
            },
            "spells": [
                ("Soothe the Ferocious Bear", "ReAn", 10, 1),
                ("Bind Wound", "CrCo", 10, 1),
                ("Bridge of Wood", "CrHe", 20, 1),
                ("Transformation of the Thorny Staff", "MuHe", 10, 1),
                ("Piercing Shaft of Wood", "MuHe(Re)", 10, 1),
                ("Repel the Wooden Shafts", "ReHe", 10, 1),
                ("Strike of the Angered Branch", "ReHe", 15, 1),
                ("The Treacherous Spear", "ReHe", 25, 1),
                ("Coils of the Entangling Plants", "ReHe", 20, 1),
                ("Eyes of the Treacherous Terrain", "InTe", 15, 1),
                ("Wielding the Invisible Sling", "ReTe", 10, 1),
            ],
            "notes": (
                "Equipment: bronze half scale mail, a great sword and a "
                "lance; Encumbrance 2 (3). No Twilight Scars. Also: the "
                "Flaw Magical Animal Companion, Kervus, the great faerie "
                "stag who is his caricature and steed. A faerie court, not "
                "a mundane lord, knighted him, and his Vow is to chivalry."
            ),
        },
        masteries={
            "Soothe the Ferocious Bear": (FAST,),
            "Bind Wound": (MULTIPLE,),
            "Bridge of Wood": (STILL,),
            "Transformation of the Thorny Staff": (FAST,),
            "Piercing Shaft of Wood": (MULTIPLE,),
            "Repel the Wooden Shafts": (FAST,),
            "Strike of the Angered Branch": (MULTIPLE,),
            "The Treacherous Spear": (FAST,),
            "Coils of the Entangling Plants": (FAST,),
            "Eyes of the Treacherous Terrain": (STILL,),
            "Wielding the Invisible Sling": (MULTIPLE,),
        },
    )


def peregrinatores(rhine: Rhine) -> None:
    """The two wandering magi of the chapter on the Rhine Tribunal, made
    once the Tribunal is finished."""
    b = rhine.b
    _stats(
        b,
        rhine.magi["tabanus"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 3,
                "presence": -1,
                "communication": -1,
                "strength": 0,
                "stamina": 2,
                "dexterity": -2,
                "quickness": 0,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "warping": (2, 15),
            "apparent_age": 38,
            "virtues_flaws": [
                "The Gift",
                "Journeyman (Rhine Tribunal)",
                ("Affinity with {ability}", {"ability": "folk ken"}),
                "Clear Thinker",
                "Hermetic Prestige",
                "Intuition",
                "Premonitions",
                ("Puissant {art}", {"art": "intellego"}),
                "Skilled Parens",
                "Meddler (Major)",
                ("{gild} Enmity", {"gild": "Hawthorn Gild"}),
                ("Incompatible Arts", {"arts": "Perdo Imaginem"}),
                "Infamous",
            ],
            "traits": {"Law Abiding": 3, "Tenacious": 3, "Honorable": 2},
            "reputations": {
                "Meddlesome Upstart (Hermetic)": 4,
                "Quaesitor (Hermetic)": 3,
            },
            "abilities": [
                ("Artes Liberales", 2, "logic"),
                ("Athletics", 1, "stamina"),
                ("Awareness", 2, "things out of place"),
                ("Concentration", 1, "Intellego spells"),
                ("Code of Hermes", 4, "regarding scrying"),
                ("Folk Ken", 6, "unusual behavior"),
                ("Area Lore: Germany", 3, "safe roads"),
                ("Great Weapon", 2, "staff"),
                ("Living Language: High German", 2, "Swiss"),
                ("Living Language: Italian", 5, "Apulian"),
                ("Dead Language: Latin", 4, "Hermetic usage"),
                ("Magic Theory", 4, "identifying spells"),
                ("Organization Lore: Order of Hermes", 3, "Rhine covenants"),
                ("Parma Magica", 3, "Mentem"),
                ("Penetration", 2, "Intellego spells"),
                ("Premonitions", 2, "crime"),
                ("Living Language: Romansch", 1, "southern Alps"),
                ("Survival", 2, "bad weather"),
            ],
            "arts": {
                "Creo": 4,
                "Intellego": 10,
                "Muto": 2,
                "Perdo": 2,
                "Rego": 3,
                "Animal": 1,
                "Aquam": 4,
                "Auram": 3,
                "Corpus": 4,
                "Herbam": 1,
                "Ignem": 3,
                "Imaginem": 8,
                "Mentem": 8,
                "Terram": 6,
                "Vim": 8,
            },
            "spells": [
                ("Image of the Beast", "InAn", 5, 0),
                ("Comfort of the Drenched Traveler", "PeAq", 5, 0),
                ("Whispers Through the Black Gate", "InCo(Me)", 15, 0),
                ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
                ("Discern the Images of Truth and Falsehood", "InIm", 25, 0),
                ("Taste of the Spices and Herbs", "MuIm", 5, 0),
                ("Sight of the Transparent Motive", "InMe", 10, 1),
                ("Frosty Breath of the Spoken Lie", "InMe", 20, 1),
                ("Perceive the Eyes of Knives", "InMe", 20, 0),
                ("Trust of Childlike Faith", "PeMe", 10, 0),
                ("Eyes of the Eons", "InTe", 10, 0),
                ("Tracks of the Faerie Glow", "InTe", 25, 0),
                ("The Invisible Eye Revealed", "InVi", 20, 0),
                ("Reveal the Magical Deception", "InVi", 25, 0),
                ("Sense of the Lingering Magic", "InVi", 30, 0),
            ],
            "notes": (
                "Equipment: a stout blackthorn staff, the knout he carries "
                "as a walking stick and is thinking of enchanting; "
                "Encumbrance 2 (2). No Twilight Scars. Gauntleted at 23 "
                "after training at Magvillus under Jart, the leading "
                "Traditionalist of his House. The book's block gives "
                "Intellego as 10+3 with Puissant Intellego; the sheet holds "
                "the 10 and the Virtue adds the 3."
            ),
        },
        masteries={
            "Sight of the Transparent Motive": (QUIET,),
            "Frosty Breath of the Spoken Lie": (PENETRATION,),
        },
    )
    _stats(
        b,
        rhine.magi["felicia"],
        {
            "characteristics": {
                "intelligence": 2,
                "perception": 0,
                "presence": 0,
                "communication": 0,
                "strength": 0,
                "stamina": 1,
                "dexterity": 2,
                "quickness": 0,
            },
            "size": 0,
            "confidence": (1, 3),
            "decrepitude": (0, 0),
            "warping": (0, 0),
            "apparent_age": 24,
            "virtues_flaws": [
                "The Gift",
                "Journeyman (Rhine Tribunal)",
                ("Major Magical Focus", {"focus": "weather"}),
                ("Cyclic Magic (Positive)", {"cycle": "the winter months"}),
                "Free Study",
                ("{gild} Trained", {"gild": "Linden Gild"}),
                "Personal Vis Source",
                ("Puissant {ability}", {"ability": "intrigue"}),
                "Skilled Parens",
                "Favors",
                "Study Requirement",
                "Busybody",
                ("Cyclic Magic (Negative)", {"cycle": "the summer months"}),
            ],
            "traits": {"Loner": 2, "Self-Reliant": 1, "Suspicious": -2},
            "abilities": [
                ("Artes Liberales", 2, "Latin script"),
                ("Athletics", 1, "sprinting"),
                ("Awareness", 1, "ambushes"),
                ("Bargain", 2, "food"),
                ("Area Lore: Bavaria", 1, "woods"),
                ("Chirurgy", 1, "sprains"),
                ("Civil and Canon Law", 1, "vagabond laws"),
                ("Concentration", 2, "Auram"),
                ("Dominion Lore", 1, "roadside shrines"),
                ("Faerie Lore", 1, "weather spirits"),
                ("Finesse", 1, "Auram"),
                ("Folk Ken", 3, "travelers"),
                ("Guile", 2, "disguise as a man"),
                ("Area Lore: Harz Mountains", 2, "sites to study"),
                ("Living Language: High German", 5, "disguising accent"),
                ("Hunt", 1, "small game"),
                ("Intrigue", 2, "Hermetic"),
                ("Dead Language: Latin", 4, "Hermetic usage"),
                ("Magic Theory", 4, "weather spells"),
                ("Music", 1, "flute"),
                ("Organization Lore: Order of Hermes", 2, "covenants"),
                ("Parma Magica", 2, "Corpus"),
                ("Penetration", 1, "Auram"),
                ("Area Lore: Rhine", 1, "towns"),
                ("Area Lore: Saxony", 1, "safe roads"),
                ("Survival", 2, "summer"),
                ("Swim", 1, "rivers"),
            ],
            "arts": {
                "Creo": 9,
                "Intellego": 2,
                "Muto": 2,
                "Perdo": 2,
                "Rego": 7,
                "Animal": 1,
                "Aquam": 7,
                "Auram": 9,
                "Corpus": 1,
                "Vim": 2,
            },
            "spells": [
                ("Ward Against Faeries of the Waters", "ReAq", 15, 0),
                ("Chaos of the Angry Waves", "ReAq", 30, 0),
                ("Jupiter's Resounding Blow", "CrAu", 10, 0),
                ("Stench of the Twenty Corpses", "CrAu", 10, 0),
                ("Broom of the Winds", "CrAu", 15, 0),
                ("Clouds of Rain and Thunder", "CrAu", 25, 0),
                ("Ward Against Rain", "ReAu", 10, 0),
                ("Ward Against Faeries of the Air", "ReAu", 15, 0),
                ("Clouds of Thunderous Might", "ReAu", 30, 0),
            ],
            "notes": (
                "Equipment: good quality clothes; Encumbrance 0 (0). No "
                "Twilight Scars. Her Favors are owed to Fengheld. Her magic "
                "is strongest in the winter months, when she overwinters at "
                "a covenant, and weakest in summer, when she travels to "
                "study natural wonders. The book's block gives Intrigue as "
                "2+2 with Puissant Intrigue; the sheet holds the 2 and the "
                "Virtue adds the other 2. Story seed, A Peace Emissary: she "
                "comes to winter at the player covenant to make peace "
                "between it and an enemy covenant she visited first, and "
                "the magi may suspect a motive she does not have."
            ),
        },
    )
