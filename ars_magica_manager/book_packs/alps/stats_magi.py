"""The printed stat blocks, converted from the Fourth Edition (A15), and
everyone else's generated stats (A16).

Four magi: Kentigern (p. 47), Miklos (p. 60), Ragoneda (p. 71) and Andru
(p. 82), each written here as the book prints it, a `fourth.Fourth`, and
converted by `fourth.convert` with the readings that module lists:
printed ages kept, Confidence at the Definitive Edition's baseline (DE
p. 29; Ragoneda +1 for her Tytalus apprenticeship), Twilight Points / 3
as Warping, Certamen dropped as no Ability now. Kentigern's four Minor
Magic Deficiencies are Deficient Form on Auram, Aquam, Terram and Ignem
(DE p. 125), Ragoneda's two Major ones Deficient Form on Imaginem and
Mentem. A 4e Affinity with a subject that is not an Art (cloth, bones,
sight illusions) is a Minor Magical Focus. Public Vis Source is the pack's
Virtue.

The magi's own spells are re-derived by the Definitive Edition's
guidelines (DE pp. 315-366), Near read as Voice and Far as Sight, "Sun/
Perm" as Sun and a destructive "Sun/Instant" as Momentary; OWN_SPELLS
gives each one's Range, Duration, Target and the working, and says where
no guideline fits and the printed level stands. Catalog spells take the
catalog's level. Andru's 1182 Primacy fixes his age at 81 (HoH:S
p. 52).

Cymena the Redcap (p. 76) is a companion with DE's Redcap Virtue, her
abilities renamed and her devices in her biography. Crucifixo, Andru's
cat, is his familiar, the bond worked out again by DE pp. 266-267 from
Andru's Lab Total. Kentigern's faerie hound Tobias has no printed stats
(the book sends the reader to Faeries), so he is a line in Kentigern's
biography, not a familiar record.

Everyone else the book describes gets generated stats from a profile of
its paragraph (book_packs.generated), at the age the assumptions page
gives."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ... import storage
from ...models import BondPower, Familiar, Possession, ScoredTrait
from ...rules import lab
from ..builder import StatBlock, _virtue_flaw, characteristics, paragraphs
from ..fourth import Fourth, arts, convert
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character
    from .state import Alps

KENTIGERN = Fourth(
    age=99,
    apparent=58,
    characteristics=characteristics(3, 0, 0, 0, 1, 1, 0, -1),
    confidence=6,
    twilight=9,
    decrepitude=0,
    virtues=[
        ("Visual Eidetic Memory", 3),
        ("Affinity", 3, "Animal"),
        ("Animal Ken", 1),
        ("Clear Thinker", 1),
        ("Quaesitor", 0),
        ("Susceptible to Divine Power", -4),
        ("Minor Magic Deficiency", -1, "Auram"),
        ("Minor Magic Deficiency", -1, "Aquam"),
        ("Minor Magic Deficiency", -1, "Terram"),
        ("Minor Magic Deficiency", -1, "Ignem"),
    ],
    abilities=[
        ("Athletics", 3, "hiking"),
        ("Awareness", 3, "people"),
        ("Bargain", 3, "magi"),
        ("Brawling", 1, "with animals"),
        ("Certamen", 3, "Mentem"),
        ("Civil and Canon Law", 5, "contracts"),
        ("Concentration", 5, "divination"),
        ("Crossbow", 1, "quarry"),
        ("Etiquette", 2, "magi"),
        ("Faerie Lore", 1, "dwarfs"),
        ("Finesse", 2, "hunting spells"),
        ("Folk Ken", 4, "Bavarians"),
        ("Greater Alpine Tribunal Lore", 4, "traditional exchanges"),
        ("Guile", 1, "detecting lies"),
        ("Hermetic Law", 3, "the Alpine Peripheral Code"),
        ("Hunt", 2, "tracking"),
        ("Intrigue", 1, "detecting"),
        ("Leadership", 1, "hunting parties"),
        ("Legend Lore", 3, "quarry"),
        ("Magic Affinity", 8, "Animal"),
        ("Magic Theory", 4, "magic for criminal purposes"),
        ("Occult Lore", 1, "demons one can hunt"),
        ("Order of Hermes Lore", 4, "Alpine agreements"),
        ("Parma Magica", 7, "Perdo"),
        ("Penetration", 2, "Animal"),
        ("Philosophiae", 1, "natural"),
        ("Scribe Latin", 5, "letters"),
        ("Single Weapon", 2, "sword"),
        ("Speak Latin", 5, "magi"),
        ("Speak Irish", 4, "peasants"),
        ("Speak High German", 4, "merchants"),
    ],
    arts=arts(19, 15, 15, 12, 20, 30, 0, 18, 9, 9, 0, 6, 3, 6, 10),
    spells=[
        ("Soothe the Pains of the Beast", "CrAn", 20),
        ("Call the Basilisk", "CrAn(Re,Vi)", 65),
        ("The Foes of the Ibis", "CrAn(Au,Re,Vi)", 75),
        ("Daughter of Zephyrs", "CrAn(Au,Re,Vi)", 70),
        ("Vision of the Marauding Beast", "InAn", 15),
        ("To Know the Owner as Might His Hound", "InAn", 25),
        ("Opening the Tome of the Animal's Mind", "InAn", 25),
        ("Circle of Beast Warding", "ReAn", 25),
        ("Mastering the Unruly Beast", "ReAn", 25),
        ("Commanding the Harnessed Beast", "ReAn", 30),
        ("Ward Against the Beasts of Legend", "ReAn", 30),
        ("True Sight of the Air", "InAu", 15),
        ("Chirurgeon's Healing Touch", "CrCo", 20),
        ("The Inexorable Search", "InCo", 20),
        ("Converse with Plant and Tree", "InHe", 25),
        ("Eyes of the Past", "InIm", 20),
        ("Veil of Invisibility", "PeIm", 10),
        ("Perception of the Conflicting Motives", "InIm", 25),
        ("Liar's Chime", "InMe(Im)", 25),
        ("Peering Into the Mortal Mind", "InMe", 30),
        ("The Thief of Memory", "PeMe", 20),
        ("Aura of Rightful Authority", "ReMe", 20),
        ("Scales of Magical Weight", "InVi", 5),
        ("Sense the Nature of Vis", "InVi", 5),
        ("Sense of Lingering Magic", "InVi", 30),
    ],
    traits={"Brave": 3, "Enjoys hunting": 2},
    notes=(
        "A quaesitor, an office of House Guernicus he holds though he is "
        "of Ex Miscellanea. Equipment: a bought longevity charm (-14), a "
        "light crossbow, a longsword, and padded leather riding clothes, "
        "weightless, warm in the sky and as quilted armour (Protection 2); "
        "the covenant's quaesitorial blindfold, which helps detect deceit "
        "and reason clearly, borrowed until his own spells are better; he "
        "is weighing a self-loading crossbow as his talisman. He knows a "
        "greater Soothe the Pains of the Beast that heals six wound levels "
        "(DE: heal all wounds, Base 35, +1 Touch = CrAn 40, Ritual).\n"
        "His familiar is Tobias, a faerie hound who leads his pack, can "
        "command other animals, can cast Soothe the Pains of the Beast with "
        "his tongue, carries Animal vis on his collar, and through the bond "
        "gave Kentigern flight by running and immunity to wind chill. The "
        "book prints no stats for him (it points to the Fourth Edition's "
        "Faeries), so he has no familiar record here.\n"
        "His Deficiencies leave only Auram biting: the book's Auram totals, "
        "such as True Sight of the Air's +34, use the whole score, and "
        "Deficient Form halves them."
    ),
)

MIKLOS = Fourth(
    age=40,
    apparent=28,
    characteristics=characteristics(2, 0, 2, 1, 0, 0, 1, 1),
    confidence=4,
    twilight=2,
    decrepitude=0,
    virtues=[
        ("Light Touch", 2),
        ("Sidhe Blood", 2, "Sidhe"),
        ("Magic Affinity", 1, "cloth"),
        ("Free Expression", 1),
        ("Gentle Gift", 1),
        ("Social Contacts", 1, "House Jerbiton"),
        ("Well-traveled", 1),
        ("True Love", 1, "Lyndsay of Journeys End"),
        ("Weak Parma", -3, "when naked"),
        ("Non-combatant", -2),
        ("Dependant", -1, "his children"),
        ("Cyclic Magic (-)", -1, "summer"),
        ("Deep Sleeper", -1),
        ("Obsession", -1, "a hopeless romantic"),
    ],
    abilities=[
        ("Artes Liberales", 2, "music"),
        ("Bargain", 6, "nobility"),
        ("Certamen", 3, "Creo"),
        ("Charm", 4, "noblemen"),
        ("Concentration", 5, "spellcasting"),
        ("Craft: Tailor", 5, "for magi"),
        ("Disputatio", 2, "with older magi"),
        ("Etiquette", 4, "nobles"),
        ("Faerie Lore", 2, "sirens"),
        ("Finesse", 4, "cloth"),
        ("Folk Ken", 3, "the covenant"),
        ("Greater Alpine Tribunal Lore", 3, "fashion"),
        ("Guile", 1, "flattery"),
        ("Hermetic Law", 1, "contracts"),
        ("House Jerbiton Lore", 1, "who wears what and why"),
        ("Lectio", 3, "pretending to listen"),
        ("Legend Lore", 1, "Spanish"),
        ("Magic Affinity", 5, "cloth"),
        ("Magic Theory", 5, "Herbam"),
        ("Order of Hermes Lore", 2, "House Jerbiton"),
        ("Parma Magica", 3, "Animal"),
        ("Philosophiae", 1, "metaphysics"),
        ("Play", 5, "mandolin"),
        ("Ride", 1, "horse"),
        ("Scribe Latin", 5, "the Arts"),
        ("Speak Latin", 5, "magi"),
        ("Speak Iberian", 4, "grogs"),
        ("Speak Langue d'Oc", 5, "merchants"),
    ],
    arts=arts(10, 10, 0, 0, 0, 20, 0, 0, 9, 12, 0, 11, 5, 0, 6),
    spells=[
        ("The Finch Flourish", "CrAn(Im)", 10),
        ("Blizzard of Down", "CrAn", 30),
        ("The Scold's Bridle", "CrAn", 40),
        ("Cocoon of the Mulberry Worm", "CrAn", 30),
        ("Panic of the Elephant's Mouse", "ReAn", 15),
        ("The Gentle Beast", "ReAn", 20),
        ("Chirurgeon's Healing Touch", "CrCo", 20),
        ("The Couturier's Art", "CrAn(He,Im)", 35),
        ("The Ninth Stitch", "CrAn(He,Im)", 30),
        ("Aura of Ennobled Presence", "MuIm", 10),
        ("Disguise of the Transformed Image", "MuIm", 15),
        ("Thoughts Within Babble", "InMe", 25),
        ("Posing the Silent Question", "InMe", 20),
    ],
    traits={"Brave": 3, "Easily distracted in conversation": 2},
    reputations={
        "A lovesick puppy (the old and cynical)": 2,
        "A dashing romantic (the young and romantic)": 1,
    },
    notes=(
        "Equipment: anything a dashing young troubadour, safely married, "
        "might have. His mandolin, won in Arcadia, works like Aura of "
        "Rightful Authority and lets him speak with living things, but only "
        "through a song's lyrics; a flute like it, which commands the "
        "elements, is said to be hidden somewhere. A pet spider that can "
        "look like a puppy, which he means to make his familiar before it "
        "dies of age. His Non-combatant flaw is defined as being unable to "
        "harm others by combat magic."
    ),
)

RAGONEDA = Fourth(
    age=56,
    apparent=28,
    tytalus=True,
    characteristics=characteristics(5, 0, 1, 0, 0, 0, 0, 0),
    confidence=6,
    twilight=7,
    decrepitude=0,
    virtues=[
        ("Incredible Intelligence", 4, "Intelligence"),
        ("Purifying Touch", 2, "arthritis"),
        ("Clear Thinker", 1),
        ("Magic Affinity", 1, "bones"),
        ("Secret Vis Source", 1, "Corpus"),
        ("Strong-willed", 1),
        ("Susceptible to Divine Power", -4),
        ("Major Magic Deficiency", -3, "Imaginem"),
        ("Major Magic Deficiency", -3, "Mentem"),
        ("Public vis source", 2),
    ],
    abilities=[
        ("Artes Liberales", 3, "geometry"),
        ("Awareness", 2, "hostile magic"),
        ("Bargain", 3, "magi"),
        ("Boating", 2, "not getting wet"),
        ("Brawling", 1, "not being held"),
        ("Certamen", 3, "Creo"),
        ("Charm", 1, "magi"),
        ("Chirurgy", 2, "fractures"),
        ("Concentration", 6, "study"),
        ("Disputatio", 7, "apprentices"),
        ("Etiquette", 3, "magi"),
        ("Faerie Lore", 2, "Danu"),
        ("Faerie Lore", 1, "gnomes"),
        ("Finesse", 4, "bones"),
        ("Folk Ken", 5, "Bavarians"),
        ("Greater Alpine Tribunal Lore", 3, "what magi want"),
        ("Guile", 1, "detecting"),
        ("Hermetic Law", 1, "orbi"),
        ("Intrigue", 3, "against Tytalus magi"),
        ("Leadership", 3, "grogs"),
        ("Lectio", 3, "apprentices"),
        ("Legend Lore", 1, "Normandy"),
        ("Magic Affinity", 12, "bones"),
        ("Magic Theory", 9, "magic for criminal purposes"),
        ("Medicine", 4, "the skeleton"),
        ("Occult Lore", 3, "animated dead"),
        ("Order of Hermes Lore", 2, "House Tytalus"),
        ("Parma Magica", 7, "Corpus"),
        ("Penetration", 4, "bone magic"),
        ("Philosophiae", 2, "natural"),
        ("Scribe Latin", 5, "spells"),
        ("Speak Latin", 5, "magi"),
        ("Speak Norman French", 4, "grogs"),
        ("Speak High German", 4, "merchants"),
        ("Swim", 1, "when encumbered"),
    ],
    arts=arts(25, 23, 14, 6, 6, 11, 6, 6, 30, 6, 6, 6, 6, 6, 14),
    spells=[
        ("Recreating the Inner Sea", "CrAq(Co)", 25),
        ("Chirurgeon's Healing Touch", "CrCo", 20),
        ("Shower of Needles", "CrCo(Re)", 20),
        ("Tempest of Needles", "CrCo(Re)", 30),
        ("Eyes of the Owl", "MuCo", 5),
        ("Rack of Thorns", "MuCo", 20),
        ("Preternatural Growth and Shrinking", "MuCo", 20),
        ("Easing the Strain of Childbirth", "MuCo", 20),
        ("The Hidden Skin of the Serpent", "MuCo(An)", 30),
        ("The Suffering of the Seer", "MuCo", 30),
        ("Statue of Bone", "MuCo", 45),
        ("Shattered Leg", "PeCo", 25),
        ("Nagging Curse", "PeCo", 25),
        ("Grip of the Choking Hand", "PeCo", 15),
        ("Intestinal Suffering", "PeCo", 40),
        ("Rise of the Feathery Body", "ReCo", 5),
        ("Leap of Homecoming", "ReCo", 35),
        ("Seven League Stride", "ReCo", 35),
    ],
    traits={"Brave": 3, "Yearns for challenges": 3, "Secretive": 1},
    reputations={
        "A rising star (some Tytalus magi)": 2,
        "Profoundly annoying (other Tytalus magi)": 2,
    },
    notes=(
        "Equipment: few devices yet, since she has been building her Arts. "
        "Her talisman is a bone spindle, opened for every shape and "
        "material bonus and enchanted to snap human and animal limbs. A pet "
        "marmot with some magical abilities; no familiar yet. Her longevity "
        "potion (-13) has washed her body to her sigil's bone colour, which "
        "may return when the potion fails. Her Public Vis Source came after "
        "her Gauntlet, and buys her a chair of her own."
    ),
)

ANDRU = Fourth(
    age=81,
    apparent=35,
    characteristics=characteristics(4, 0, 0, 1, 0, 0, 0, 0),
    confidence=7,
    twilight=5,
    decrepitude=0,
    virtues=[
        ("Charmed Life", 3),
        ("Visual Eidetic Memory", 3),
        ("Great Intelligence", 2, "Intelligence"),
        ("Gentle Gift", 1),
        ("Magic Affinity", 1, "illusions of sight"),
        ("Free Expression", 1),
        ("True Love", 1, "Carmine"),
        ("Social Contacts", 1, "the great clerics"),
        ("Magic Items", 1),
        ("Relic", 1, "the fingerbone of Saint Cyprian"),
        ("Susceptible to Divine Power", -4),
        ("Driving Goal", -1, "to reconcile the Church and the Order"),
        ("Dutybound", -1, "religious"),
        ("Enemy", -2, "Yselt of Journeys End"),
    ],
    abilities=[
        ("Artes Liberales", 5, "logic"),
        ("Athletics", 1, "hiking"),
        ("Awareness", 2, "assassins"),
        ("Bargain", 6, "magi"),
        ("Brawling", 1, "with drunkards"),
        ("Carouse", 1, "keeping sober"),
        ("Certamen", 5, "Mentem"),
        ("Charm", 2, "magi"),
        ("Civil and Canon Law", 2, "Church courts"),
        ("Climb", 1, "stairs"),
        ("Craft: Woodworker", 1, "mending a lute"),
        ("Concentration", 8, "while plotting"),
        ("Disputatio", 3, "Mentem"),
        ("Enigmatic Wisdom", 1, "understanding Criamon magi"),
        ("Etiquette", 4, "magi"),
        ("Faerie Lore", 2, "weaknesses"),
        ("Finesse", 4, "illusions"),
        ("Folk Ken", 6, "local festivals"),
        ("Forgery", 1, "documents"),
        ("Greater Alpine Tribunal Lore", 4, "magi"),
        ("Guile", 4, "magi"),
        ("Hermetic Law", 3, "self-defence"),
        ("House Jerbiton Lore", 8, "what you wish he didn't know"),
        ("Hunt", 2, "faeries"),
        ("Intrigue", 5, "magi"),
        ("Leadership", 5, "magi"),
        ("Lectio", 4, "Mentem"),
        ("Legerdemain", 1, "detecting"),
        ("Legend Lore", 5, "the local region"),
        ("Magic Affinity", 5, "emotions"),
        ("Magic Theory", 7, "Imaginem"),
        ("Occult Lore", 2, "detection"),
        ("Order of Hermes Lore", 4, "House Jerbiton"),
        ("Parma Magica", 6, "Mentem"),
        ("Penetration", 4, "Muto"),
        ("Philosophiae", 3, "ethics"),
        ("Play Lute", 1, "comedy"),
        ("Ride", 1, "horses"),
        ("Scribe Latin", 7, "obscure clues"),
        ("Sing", 1, "hymns"),
        ("Single Weapon", 1, "waving swords impressively"),
        ("Speak Latin", 5, "magi"),
        ("Speak Greek", 4, "magi"),
        ("Storyteller", 1, "about magi"),
        ("Survival", 1, "the Alps"),
        ("Swim", 1, "the Alps"),
        ("Theology", 3, "magic"),
    ],
    arts=arts(9, 10, 20, 10, 20, 10, 6, 6, 8, 6, 6, 25, 20, 6, 6),
    spells=[
        ("Chirurgeon's Healing Touch", "CrCo", 20),
        ("Eyes of the Cat", "MuCo", 15),
        ("Thaumaturgical Transformation of Plants to Iron", "MuHe(Te)", 15),
        ("Phantasm of the Skilled Musician", "CrIm", 20),
        ("Phantom Magic", "CrIm", 40),
        ("Aura of Ennobled Presence", "MuIm", 10),
        ("Image Phantom", "MuIm", 25),
        ("Visions Beatific", "ReMe(Im)", 30),
        ("Phantasmal Images", "MuIm", 40),
        ("Restore the Image Transferred", "MuIm", 40),
        ("Wizard's Sidestep", "ReIm", 10),
        ("Disguise of the Transformed Image", "MuIm", 15),
        ("The Captive Voice", "ReIm", 15),
        ("Haunt of the Living Ghost", "ReIm", 35),
        ("Tickling the Humors", "CrMe", 15),
        ("Tickling the Humors (Group)", "CrMe", 25),
        ("Gift of Reason", "CrMe", 25),
        ("Return of Mental Lucidity", "CrMe", 35),
        ("Trail of the Lost Ways", "InMe", 25),
        ("Aura of Rightful Authority", "ReMe", 20),
        ("Call of Morpheus", "ReMe", 25),
        ("Time Unmans All Foes", "PeTe", 25),
        ("Circle of Warriors", "ReTe", 10),
        ("Wielding the Invisible Sling", "ReTe", 10),
        ("Circular Ward Against Demons", "ReVi", 35),
        ("Circular Ward Against Faeries", "ReVi", 35),
        ("Opening the Intangible Tunnel", "ReVi", 35),
        ("Watching Ward", "ReVi", 30),
    ],
    traits={"Cunning": 3, "Brave": 2, "Pious": 2, "Sneaky": 2},
    reputations={
        "Helpful (major clerics)": 2,
        "Rising political power (elderly magi)": 1,
        "Mysterious (major clerics)": 1,
    },
    notes=(
        "He learnt most of his spells from books Valnastium's library trades "
        "for, and avoids inventing his own. He knows Eyes of the Cat in a "
        "form the book changes to Near, Sun or Year and Group. He does not "
        "brew his own longevity potion (-14). He borrows the House's devices, "
        "which come to it when a magus dies with no sodalis of his master's "
        "master: masks of Disguise of the New Visage or Image Phantom for his "
        "agents, and the Standard of the Shadowy Men, carried against the "
        "Fanes, with group Seven-League Stride, invisibility and grog-"
        "strengthening enchantments. He will not use Enslave the Mortal Mind "
        "or its like. His relic is a flake of Saint Cyprian's fingerbone sewn "
        "into white silk, to which he wrongly credits his luck. His talisman "
        "is a flame-red wedding veil (HoH:S p. 52; Sanctuary of Ice makes it "
        "Carmine's sigil, kept by him, as his gold and amethyst ring is kept "
        "by her). He and Carmine married by the Greek rite with pagan "
        "Hermetic symbols, which they keep quiet."
    ),
)

#: The printed blocks, by magus key.
BLOCKS: dict[str, Fourth] = {
    "kentigern": KENTIGERN,
    "miklos": MIKLOS,
    "ragoneda": RAGONEDA,
    "andru": ANDRU,
}

#: The printed longevity modifiers (carried across, DE p. 391) and who made
#: each, where the book says.
LONGEVITY: dict[str, tuple[int, str]] = {
    "kentigern": (14, ""),
    "ragoneda": (13, "Ragoneda"),
    "andru": (14, ""),
}

#: The magi's own spells: Range, Duration, Target, page, and the working.
OWN_SPELLS: dict[str, tuple[str, str, str, str, str]] = {
    "Call the Basilisk": (
        "Touch",
        "Sun",
        "Individual",
        "48",
        "Creates a basilisk, which Kentigern made to study them safely: they "
        "are oddly common near Basel and Vienna, where an egg laid in a dung "
        "heap is said to be enough, and he suspects a magus makes them. "
        "Spell focus a toad, or being where basilisks are common (+1). DE: "
        "create a magical beast, Base 50 (with Vim for its magical nature), "
        "+1 Touch, +2 Sun = 65; the book's level 50.",
    ),
    "The Foes of the Ibis": (
        "Touch",
        "Sun",
        "Group",
        "48",
        "Creates a small flock of iaculi, winged snakes; one of Kentigern's "
        "favourite combat spells, often made invisible. Magi think iaculi "
        "ill-omened and able to slip Hermetic protections, which is untrue "
        "and which he does not correct. Spell focus a dead ibis (+5). DE: "
        "Base 50, +1 Touch, +2 Sun, +2 Group = 75; the book's level 40.",
    ),
    "Daughter of Zephyrs": (
        "Touch",
        "Sun",
        "Individual",
        "48",
        "Creates a magical horse that gallops through the air as others do "
        "on land; Kentigern has used vis to keep one for good. Spell focus "
        "silver horseshoes (+3). DE: Base 50, +1 Touch, +2 Sun, +1 size = 70; "
        "the book's level 45.",
    ),
    "To Know the Owner as Might His Hound": (
        "Touch",
        "Sun",
        "Individual",
        "49",
        "Senses what an animal senses, cast on domestic beasts or on one of "
        "his flying serpents. DE: read an animal's surface thoughts, Base 10, "
        "+1 Touch, +2 Sun = 25, as printed.",
    ),
    "Liar's Chime": (
        "Eye",
        "Sun",
        "Individual",
        "49",
        "Frosty Breath of the Spoken Lie with an Imaginem requisite: a bell "
        "rings when the target lies, since all breath looks frosty in the "
        "Alps. DE: Base 10, +1 Eye, +2 Sun = 25, as printed.",
    ),
    "The Thief of Memory": (
        "Eye",
        "Momentary",
        "Individual",
        "49",
        "Removes all memory of one person, place or event; the target often "
        "knows something is missing. Made to suppress the Gift of untrained "
        "children or take away their memories of home; the Quaesitores use it "
        "to tidy up after Hermetic criminals. Spell focus a burning "
        "forget-me-not (+3). DE: remove a major or long memory, Base 15, +1 "
        "Eye = 20; the book's level 25.",
    ),
    "The Finch Flourish": (
        "Touch",
        "Momentary",
        "Individual",
        "60",
        "The book names it and gives no description, so its level stands as printed.",
    ),
    "Blizzard of Down": (
        "Voice",
        "Diameter",
        "Group",
        "61",
        "A great wad of down pours over a group, blinding them while it lasts "
        "and leaving them buried in feathers, 5 - Strength rounds to dig out. "
        "Spell focus a down pillow (+1). DE: create an animal product, Base 5, "
        "+2 Voice (the book's Near), +1 Diameter, +2 Group = 30; the book's "
        "level 20.",
    ),
    "The Scold's Bridle": (
        "Voice",
        "Sun",
        "Individual",
        "61",
        "A scold's bridle, a gag of leather and metal, forms round the "
        "victim's head, so that a magus must cast silently; its lead appears in "
        "the caster's hand if close. Spell focus a horse's bit (+3). DE: "
        "processed leather is two magnitudes above the dead animal, Base 20, "
        "+2 Voice (Near), +2 Sun = 40; the book's level 20.",
    ),
    "Cocoon of the Mulberry Worm": (
        "Sight",
        "Sun",
        "Individual",
        "61",
        "Wraps the target in many layers of silk, thin about the head, cut "
        "free with a blade in 10 - Strength rounds or broken on one Strength "
        "roll of 12+. Aimed -1. Spell focus a silk handkerchief. DE: create an "
        "animal product, Base 5, +3 Sight, +2 Sun = 30, as printed.",
    ),
    "The Couturier's Art": (
        "Touch",
        "Sun",
        "Individual",
        "61",
        "Creates a whole set of clothes with their accessories, metal parts "
        "mocked up with bone and bright colours. Spell focus dressmaker's pins "
        "(+1). DE: processed cloth and leather, Base 20, +1 Touch, +2 Sun = "
        "35; the book's level 10.",
    ),
    "The Ninth Stitch": (
        "Touch",
        "Sun",
        "Individual",
        "61",
        "Mends an item of clothing, simulating metal parts with metallic dyes. "
        "Spell focus a silver needle (+1). DE: treated thread and leather, "
        "Base 15, +1 Touch, +2 Sun = 30; the book's level 10.",
    ),
    "Recreating the Inner Sea": (
        "Touch",
        "Sun",
        "Individual",
        "72",
        "Fills a container with a liquid that keeps severed human flesh alive; "
        "without vis the flesh decays the moment it is taken out. Spell focus "
        "the whites of a dozen eggs (+1). The pack has no Creo Aquam guideline "
        "to re-derive it by, so the book's level stands.",
    ),
    "Shower of Needles": (
        "Sight",
        "Momentary",
        "Individual",
        "72",
        "Showers the target with needles of bone for +10 damage. Aimed 0. "
        "Spell focus a wishbone (+1). No Definitive Edition guideline sets "
        "the damage of created bone, so the book's level stands.",
    ),
    "Tempest of Needles": (
        "Sight",
        "Momentary",
        "Group",
        "71",
        "As Shower of Needles, on a group: its level 20 +2 Group = 30; the "
        "book's level 25.",
    ),
    "Rack of Thorns": (
        "Voice",
        "Momentary",
        "Part",
        "72",
        "Warps the ribcage to grow thorns of bone inward, which tear the "
        "lungs on the next breath and vanish, usually killing by bleeding "
        "within. One forewarned who holds his breath needs Stamina 6+ not to "
        "gasp; one unwarned, 9+. Spell focus a white rose (+2). DE: add body "
        "parts that are not human, Base 5, +2 Voice (Near), +1 Part = 20, as "
        "printed.",
    ),
    "The Hidden Skin of the Serpent": (
        "Touch",
        "Sun",
        "Individual",
        "72",
        "Turns the lower skin to bony plates like a reptile's osteoderms, for "
        "+10 Soak. Spell focus a snakeskin (+1). The Definitive Edition's "
        "guidelines stop at +5 Soak, so the book's level stands.",
    ),
    "The Suffering of the Seer": (
        "Sight",
        "Sun",
        "Part",
        "72",
        "Plates of bone slide down over the victim's eyes and fuse to the "
        "cheeks, in pain and blindness. Spell focus a white blindfold (+1). "
        "DE: add body parts, Base 5, +3 Sight (the book's Far), +2 Sun, +1 "
        "Part = 30; the book's level 35.",
    ),
    "Statue of Bone": (
        "Voice",
        "Sun",
        "Individual",
        "73",
        "Calcifies an enemy into a statue of bone, with no Terram requisite; "
        "made in haste before a Tribunal, so every statue falls over. Spell "
        "focus an ivory statuette (+3). DE: turn a human into a solid "
        "inanimate thing, Base 25, +2 Voice (Near), +2 Sun = 45; the book's "
        "level 50.",
    ),
    "Nagging Curse": (
        "Sight",
        "Momentary",
        "Individual",
        "73",
        "Cracks the enamel of a tooth, costing a Fatigue level that only "
        "magical healing or pulling the tooth restores, and no more than one. "
        "Spell focus a piece of hard candy (+1). DE: the loss of a Fatigue "
        "level, Base 10, +3 Sight = 25; the book's level 20.",
    ),
    "Intestinal Suffering": (
        "Arcane Connection",
        "Momentary",
        "Individual",
        "73",
        "A sharp shard of bone forms in the victim's gut and in time "
        "perforates it, killing; Stamina 12+ recovers in a fortnight. Spell "
        "focus the target's tooth (+5). DE: as inflicting a major disease, "
        "Base 20, +4 Arcane Connection = 40, as printed.",
    ),
    "Tickling the Humors": (
        "Eye",
        "Sun",
        "Individual",
        "85",
        "Variants of Rising Ire with other emotions: one makes the target "
        "hysterically happy near a chosen thing, another intensely curious. "
        "DE: Base 4, +1 Eye, +2 Sun = 15; the book's level 20.",
    ),
    "Tickling the Humors (Group)": (
        "Eye",
        "Sun",
        "Group",
        "85",
        "The group variants: hysteria, courage, or counsel of chastity. DE: "
        "Base 4, +1 Eye, +2 Sun, +2 Group = 25, as printed.",
    ),
    "Visions Beatific": (
        "Voice",
        "Sun",
        "Individual",
        "85",
        "Visions of the Infernal Terrors made beautiful: everything the "
        "target sees seems sublime, and a Stamina roll with fitting traits "
        "decides whether he takes those near him for angels (0 or less), "
        "gapes helplessly (1-9), dances as with Saint Vitus's dance (-6, "
        "10-15), or acts at -3 (16+). Spell focus an ergot-blighted stalk of "
        "grain (+5). DE: as Visions of the Infernal Terrors, Rego Mentem, "
        "Base 10, +2 Voice (Near), +2 Sun = 30; the book's MuIm(Me) 30.",
    ),
    "Phantasmal Images": (
        "Sight",
        "Sun",
        "Group",
        "84",
        "Image Phantom on a whole group at a distance. DE: Base 5, +3 Sight "
        "(the book's Far), +2 Sun, +2 Group = 40; the book's level 35.",
    ),
    "Call of Morpheus": (
        "Sight",
        "Momentary",
        "Group",
        "84",
        "The Call to Slumber on a group in sight. DE: Base 4, +3 Sight, +2 "
        "Group = 25, as printed.",
    ),
    "Time Unmans All Foes": (
        "Sight",
        "Momentary",
        "Group",
        "84",
        "The Rusted Decay of Ten Score Years on a whole group's arms and "
        "armour in sight. The pack has no Perdo Terram guideline to re-derive "
        "it by, so the book's level stands.",
    ),
    "Shattered Leg": (
        "Voice",
        "Momentary",
        "Individual",
        "72",
        "Breaks the target's leg. DE: cripple a limb, Base 15, +2 Voice (the "
        "book's Near) = 25; the book's level 15.",
    ),
    "Vision of the Marauding Beast": (
        "",
        "",
        "",
        "47",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Phantasm of the Skilled Musician": (
        "",
        "",
        "",
        "82",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Phantom Magic": (
        "",
        "",
        "",
        "82",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Restore the Image Transferred": (
        "",
        "",
        "",
        "84",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Return of Mental Lucidity": (
        "",
        "",
        "",
        "84",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Trail of the Lost Ways": (
        "",
        "",
        "",
        "84",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Circle of Warriors": (
        "",
        "",
        "",
        "84",
        "A Fourth Edition spell the book lists without a description and the "
        "catalog lacks, with no catalog spell of its Arts and level to stand in "
        "for it; its printed level is kept.",
    ),
    "Haunt of the Living Ghost": (
        "Voice",
        "Sun",
        "Individual",
        "84",
        "A Fourth Edition Rego Imaginem spell the book extends to Sun; it "
        "prints no description, so its level stands.",
    ),
}


def build(alps: Alps) -> None:
    """Nothing to build: the magi are the covenant part's records, and
    their stats go in last, in `stats`."""
    del alps


def stats(alps: Alps) -> None:
    b = alps.b
    for key, block in BLOCKS.items():
        character = alps.magi.get(key)
        if character is None:
            continue
        stat, age = convert(key, block)
        b.stats(character, stat)
        character.background.year_born = b.year - age
        _own_spells(character)
        printed = LONGEVITY.get(key)
        if printed is not None:
            character.aging.longevity_modifier, character.aging.longevity_by = printed
    _cymena(alps)
    _crucifixo(alps)
    for key, profile in PROFILES.items():
        character = alps.magi.get(key)
        if character is not None:
            apply(b, character, profile)


def _own_spells(character: Character) -> None:
    for spell in character.invented_spells:
        own = OWN_SPELLS.get(spell.name)
        if own is None:
            continue
        spell.range, spell.duration, spell.target, spell.page = own[:4]
        spell.source = "SoI"
        spell.description = own[4]


# -- Cymena --

CYMENA: StatBlock = {
    "characteristics": characteristics(1, 2, 0, 0, 0, 2, 0, 0),
    "size": -1,
    "confidence": (1, 3),
    "apparent_age": 28,
    "virtues_flaws": ["Redcap", "Premonitions", "Small Frame"],
    "abilities": [
        ("Animal Handling", 5, "equines"),
        ("Athletics", 5, "hiking"),
        ("Awareness", 3, "dangers on the road"),
        ("Bargain", 3, "mundane supplies"),
        ("Brawl", 2, "with animals"),
        ("Profession: Boatman", 2, "rough rivers"),
        ("Bows", 2, "wild animals"),
        ("Carouse", 3, "staying sober"),
        ("Chirurgy", 1, "herself"),
        ("Craft: Leatherworker", 2, "repairs"),
        ("Etiquette", 2, "covenfolk"),
        ("Faerie Lore", 2, "avoiding them"),
        ("Finesse", 2, "Seven-League Stride"),
        ("Folk Ken", 5, "Unterwalden"),
        ("Area Lore: Greater Alps Tribunal", 6, "safe roads between covenants"),
        ("Guile", 1, "passing as a pilgrim"),
        ("Code of Hermes", 1, "Redcaps"),
        ("Organization Lore: Order of Hermes", 2, "magi's characters"),
        ("Hunt", 2, "cattle stealing"),
        ("Legerdemain", 2, "guarding against it"),
        ("Magic Lore", 2, "dangerous places"),
        ("Infernal Lore", 2, "self-defence"),
        ("Premonitions", 5, "using Seven-League Stride"),
        ("Ride", 3, "mule"),
        ("Artes Liberales", 4, "concise letters"),
        ("Great Weapon", 3, "alpenstock"),
        ("Dead Language: Latin", 5, "with magi"),
        ("Living Language: High German", 4, "peasants"),
        ("Living Language: Langue d'Oc", 3, "peasants"),
        ("Living Language: Italian", 3, "peasants"),
        ("Living Language: Romansch", 2, "peasants"),
        ("Stealth", 3, "the Alpine wilds"),
        ("Charm", 1, "anecdotes"),
        ("Survival", 4, "the Alps"),
        ("Swim", 1, "very cold water"),
        ("Profession: Teamster", 4, "repairs"),
    ],
    "traits": {"Brave": 3, "Cautious": 2},
    "reputations": {"Level-headed (magi of Mercere)": 3},
    "notes": (
        "Converted from the Fourth Edition block (p. 76): age 48 as printed, "
        "looks in her late twenties; Confidence at the Definitive Edition's "
        "baseline, not the old 3. Her Redcap, Indenture and Whitlams Virtues "
        "fold into the Definitive Edition's Redcap (DE p. 105), which gives "
        "Well-Traveled; Climb is Athletics, Disguise and Guile are Guile, "
        "Storytelling is Charm, Scribe Latin is Artes Liberales.\n"
        "Her devices: a warm copper triangle pin (CrIg 6, constant) that also "
        "gives her Eyes of the Cat once a day (MuCo(An) 10); a golden "
        "lickstone, a small plate that clings to the palate and hides itself, "
        "holding the Seven-League Stride 24 times a day (ReCo 35), which the "
        "Rorschach magi let her trade for the Leap of Homecoming she has no use "
        "for, living at home; and a copper leaf in each boot, each a pawn of "
        "Rego vis, which lets her reroll any die that would give blisters or a "
        "turned ankle. She has not had them totalled against the Redcap "
        "Virtue's 50 levels and two a year since. Boots of an Alpine "
        "dragonette's skin, which she killed herself. A longevity potion, -5."
    ),
}


def _cymena(alps: Alps) -> None:
    cymena = alps.magi.get("cymena")
    if cymena is None:
        return
    alps.b.stats(cymena, CYMENA)
    cymena.aging.longevity_modifier, cymena.aging.longevity_by = 5, "Rogitien"


# -- Crucifixo --

#: The bond qualities the book gives Crucifixo, as invested powers: name,
#: Technique, Form, level (with unlimited uses), cosmetic trait.
BOND_POWERS = (
    (
        "Mental Communication",
        "Creo",
        "Mentem",
        15,
        "Andru's curiosity and the cat's composure traded",
    ),
    (
        "The Cat's Veil",
        "Perdo",
        "Imaginem",
        30,
        "the cat's quiet tread",
    ),
    (
        "Princes of Cats",
        "Creo",
        "Mentem",
        25,
        "a liking for warm windowsills",
    ),
)


#: How the bond was rebuilt, for the familiar's Bestiary entry.
BOND_NOTE = (
    "Rebuilt by the Definitive Edition's familiar rules (DE pp. 266-267) "
    "from Andru's Lab Total, not copied from the Fourth Edition bond. The "
    "book's cords were Gold +2, Silver +2, Bronze 0; the Lab Total buys +2 "
    "for the bronze cord too. Its bond qualities are invested powers: Mental "
    "Communication (CrMe, DE's own example), an invisibility like the Veil "
    "of Invisibility (PeIm 20, +10 for unlimited use), and making people love "
    "cats and wish to serve them as princes (CrMe, as Panic of the Trembling "
    "Heart, 15, +10 for unlimited use). He could talk before the binding, so "
    "the book's Attunement of Speech is not needed."
)


def _crucifixo(alps: Alps) -> None:
    """Crucifixo as Andru's familiar, bound by DE's rules: Lab Total the
    best Technique and Form he has, Muto 20 and Imaginem 25, + Int 4 +
    Magic Theory 7 + aura 3 = 59; binding level Might 10 + 25 + 5 x Size
    0 = 35; cords of +2, +2 and +2 (45 points); 12 pawns of vis."""
    andru, cat = alps.magi.get("andru"), alps.creatures.get("crucifixo")
    if andru is None or cat is None:
        return
    saga = alps.b.saga
    if any(f.character_id == andru.id for f in saga.familiars):
        return
    technique = max(
        ("Creo", "Intellego", "Muto", "Perdo", "Rego"), key=lambda a: _art(andru, a)
    )
    form = max(
        (
            "Animal",
            "Aquam",
            "Auram",
            "Corpus",
            "Herbam",
            "Ignem",
            "Imaginem",
            "Mentem",
            "Terram",
            "Vim",
        ),
        key=lambda a: _art(andru, a),
    )
    aura = 3
    total = (
        _art(andru, technique)
        + _art(andru, form)
        + andru.characteristics.intelligence
        + lab.ability_score(andru, "Magic Theory")[0]
        + aura
    )
    familiar = Familiar(
        id=storage.generate_unique_id("Crucifixo", [f.id for f in saga.familiars]),
        character_id=andru.id,
        name="Crucifixo",
        species="A small aristocratic black cat of the Black Lineage",
        magic_might=10,
        size=0,
        virtues_flaws=[_virtue_flaw("True Friend")],
        personality_traits=[ScoredTrait("Curious", 3), ScoredTrait("Loyal (Andru)", 3)],
        binding_technique=technique,
        binding_form=form,
        binding_lab_total=total,
        target_binding_level=10 + 25,
        vis_spent_binding=math.ceil(total / 5),
        golden_cord=2,
        silver_cord=2,
        bronze_cord=2,
        characteristics=cat.characteristics,
        base_soak=cat.soak,
        magic_resistance=10,
        natural_weapons=[
            Possession(
                id=storage.generate_unique_id("Claws and teeth", []),
                kind="weapon",
                name="Claws and teeth",
                weapon_init=5,
                weapon_attack=5,
                weapon_defense=7,
                weapon_damage=-3,
            )
        ],
        bond_powers=[
            BondPower(
                id=storage.generate_unique_id(name, []),
                name=name,
                level=level,
                technique=tech,
                form=frm,
                target_controller="Magus and familiar",
                vis_spent=math.ceil(level / 10),
                cosmetic_trait=trait,
            )
            for name, tech, frm, level, trait in BOND_POWERS
        ],
    )
    saga.familiars.append(familiar)
    cat.notes = paragraphs(cat.notes, BOND_NOTE)
    if not any(v.vf_id == "vf_true_friend" for v in andru.virtues_flaws):
        andru.virtues_flaws.append(_virtue_flaw("True Friend"))
    alps.b.link(andru, "creatures", cat, "his familiar, Crucifixo")


def _art(character: Character, art: str) -> int:
    return lab.art_score(character, art)[0]


# -- generated stats --

#: The magi the book describes without a block, read off its paragraphs.
#: Ages the book does not give are chosen from rank and standing, and
#: listed on the assumptions page.
PROFILES: dict[str, Profile] = {
    # The Cave of Twisting Shadows
    "muscaria": Profile(
        strong="int com",
        arts={"Cr": 6, "He": 6, "Re": 4, "Mu": 3},
        abilities={
            "Leadership": (4, "the covenant"),
            "Enigmatic Wisdom": (3, "service"),
        },
        native="Romansch",
    ),
    "circum_perfico": Profile(
        strong="int per",
        arts={"Re": 6, "Vi": 6, "Te": 4},
        abilities={
            "Enigmatic Wisdom": (5, "the stars"),
            "Artes Liberales": (4, "astronomy"),
        },
        age=120,
        native="Italian",
    ),
    "darius": Profile(
        strong="int sta",
        arts={"Mu": 8, "Me": 8, "In": 5, "He": 5},
        abilities={"Carouse": (4, "drinking"), "Craft: Brewer": (5, "spirits")},
        age=90,
    ),
    "echo": Profile(
        strong="int pre",
        arts={"Me": 8, "In": 4, "Re": 4},
        abilities={"Enigmatic Wisdom": (3, "ghosts")},
        native="Italian",
    ),
    "esther": Profile(
        strong="int per",
        arts={"Im": 8, "Cr": 4, "Mu": 4},
        abilities={"Enigmatic Wisdom": (3, "illusion")},
        age=60,
    ),
    "fortuito": Profile(
        strong="int per",
        arts={"In": 8, "Me": 5, "Vi": 4},
        abilities={"Premonitions": (2, "disasters"), "Ride": (3, "long journeys")},
        virtues=["Well-Traveled", ("Obsessed (Minor)", {"detail": "how seers know"})],
        age=50,
        native="Italian",
    ),
    "gunther": Profile(
        strong="sta com",
        arts={"Cr": 4, "He": 4, "Ig": 3},
        abilities={"Profession: Baker": (6, "bread")},
        age=70,
    ),
    "hagen": Profile(
        strong="int pre",
        arts={"Re": 6, "Vi": 6, "Im": 5},
        abilities={"Music": (6, "atonal composition"), "Magic Lore": (3, "spirits")},
        age=60,
    ),
    "latrunculus": Profile(
        strong="int per",
        arts={"Te": 8, "In": 6, "Re": 5},
        abilities={
            "Artes Liberales": (4, "geometry"),
            "Area Lore: Roman roads": (4, "surveying"),
        },
        age=55,
        native="Italian",
    ),
    "pellam": Profile(
        strong="sta qik",
        arts={"In": 5, "Re": 4, "Co": 4},
        abilities={"Athletics": (4, "ball games")},
        age=30,
    ),
    "phalene": Profile(
        strong="int per",
        arts={"Mu": 7, "An": 7, "In": 4},
        abilities={"Animal Ken": (3, "moths")},
        age=50,
    ),
    "regina": Profile(
        strong="int com",
        arts={"Cr": 6, "Re": 6, "Vi": 6},
        abilities={"Magic Theory": (6, "regiones")},
        age=70,
    ),
    "siobhan": Profile(
        strong="int pre",
        arts={"Vi": 5, "Im": 3, "In": 3},
        abilities={"Faerie Lore": (5, "Bright Summer")},
        age=55,
        native="Irish",
    ),
    "viscus": Profile(
        strong="int per",
        arts={"In": 8, "An": 7, "Co": 4},
        abilities={"Medicine": (4, "entrails"), "Magic Lore": (3, "beasts")},
        age=60,
    ),
    # The Covenant of the Icy North
    "athena": Profile(
        strong="int per",
        arts={"In": 9, "Me": 7, "Vi": 3},
        abilities={
            "Code of Hermes": (7, "contracts of trade"),
            "Bargain": (4, "vis"),
            "Area Lore: Greater Alps Tribunal": (4, "listed sites"),
        },
        native="Russian",
    ),
    "cato": Profile(
        strong="per com",
        arts={"Im": 8, "Mu": 6, "In": 5, "Me": 5},
        abilities={
            "Code of Hermes": (6, "investigation"),
            "Guile": (5, "disguise"),
            "Stealth": (4, "eavesdropping"),
        },
        age=90,
        native="Italian",
    ),
    "adrasteia": Profile(
        strong="per qik",
        arts={"Pe": 6, "Re": 6, "Im": 4, "Co": 4},
        abilities={
            "Code of Hermes": (5, "the Peripheral Code"),
            "Stealth": (4, "ambush"),
            "Survival": (3, "mountains"),
        },
        age=60,
    ),
    "vincent": Profile(
        strong="int sta",
        arts={"Pe": 8, "Vi": 8, "Co": 6, "Me": 5},
        abilities={"Enigmatic Wisdom": (5, "violence"), "Penetration": (5, "Vim")},
        age=110,
        native="Italian",
    ),
    "katrina": Profile(
        strong="str sta",
        arts={"Mu": 6, "An": 6, "Re": 4},
        abilities={
            "Heartbeast": (5, "the wolverine"),
            "Brawl": (4, "claws"),
            "Survival": (4, "snow"),
        },
        age=32,
    ),
    "mary": Profile(
        strong="int com",
        arts={"Im": 8, "Mu": 5, "Re": 5},
        abilities={"Magic Theory": (6, "enchanting devices")},
        age=90,
    ),
    "rogitien": Profile(
        strong="int com",
        arts={"Cr": 7, "Co": 7, "He": 4},
        abilities={"Ride": (4, "long journeys"), "Medicine": (3, "longevity")},
        age=60,
    ),
    "pietro": Profile(
        strong="int qik",
        arts={"Cr": 8, "Au": 10, "Re": 5},
        abilities={"Leadership": (5, "a March"), "Intrigue": (3, "Hermetic politics")},
        age=120,
        native="Portuguese",
    ),
    "jacinta": Profile(
        strong="int sta",
        arts={"Pe": 10, "Te": 5, "Co": 4, "Ig": 4},
        abilities={
            "Magic Theory": (6, "suboptimal spells"),
            "Infernal Lore": (3, "vampires"),
        },
        age=118,
        native="Portuguese",
    ),
    # The Covenant Where Journeys End
    "yselt": Profile(
        strong="int pre",
        arts={"Pe": 6, "Au": 6, "Im": 6, "Mu": 4},
        abilities={
            "Faerie Lore": (6, "Bright Winter"),
            "Leadership": (4, "the covenant"),
        },
        age=100,
        native="Italian",
    ),
    "carlo": Profile(
        strong="sta per",
        arts={"Au": 7, "Te": 6, "Re": 5},
        abilities={"Survival": (4, "snow")},
        virtues=[("Faerie Blood", {"blood": "barbegazi"}), "Faerie Upbringing"],
        age=60,
        native="Italian",
    ),
    "charlotte": Profile(
        strong="int dex",
        arts={"Mu": 6, "An": 5, "Im": 4},
        abilities={"Faerie Lore": (3, "geese")},
        age=35,
    ),
    "giselle": Profile(
        strong="int pre",
        arts={"Aq": 8, "Mu": 5, "Pe": 5},
        abilities={"Bargain": (4, "magi"), "Faerie Lore": (3, "elementals")},
        age=55,
    ),
    "capra": Profile(
        strong="sta per",
        arts={"Cr": 4, "Co": 5, "An": 4},
        abilities={"Medicine": (5, "births"), "Faerie Lore": (4, "faerie children")},
        shares=(0.35, 0.5, 0.15),
        age=50,
        native="Italian",
    ),
    "eginhard": Profile(
        strong="int per",
        arts={"Mu": 6, "An": 6, "In": 4},
        abilities={
            "Folk Ken": (5, "what people want"),
            "Intrigue": (3, "stirring trouble"),
        },
        age=55,
    ),
    "kamilla": Profile(
        strong="per sta",
        arts={"Mu": 6, "An": 7, "Re": 3},
        abilities={"Awareness": (4, "from the air")},
        age=50,
    ),
    # Sinews of Knowledge
    "philomena": Profile(
        strong="int per",
        arts={"Cr": 10, "Co": 10, "Pe": 6, "In": 5},
        abilities={"Medicine": (6, "faerie bodies"), "Magic Theory": (8, "longevity")},
        age=140,
    ),
    "paxon": Profile(
        strong="int com",
        arts={"Cr": 10, "Co": 10, "He": 5},
        abilities={"Magic Theory": (9, "longevity rituals"), "Bargain": (5, "magi")},
        age=130,
    ),
    "hubert": Profile(
        strong="int per",
        arts={"Cr": 6, "Co": 6, "An": 5, "Vi": 5},
        abilities={
            "Magic Lore": (4, "hedge longevity"),
            "Magic Theory": (6, "familiars"),
        },
        age=70,
    ),
    "balbina": Profile(
        strong="int dex",
        arts={"Cr": 8, "Vi": 8, "Aq": 4},
        abilities={
            "Magic Theory": (7, "repairing devices"),
            "Craft: Smith": (4, "machinery"),
        },
        age=60,
    ),
    "sabastien": Profile(
        strong="per qik",
        arts={"Re": 8, "Vi": 8, "In": 5},
        abilities={
            "Parma Magica": (8, "Vim"),
            "Legerdemain": (4, "locks"),
            "Stealth": (4, "sancta"),
        },
        age=65,
        native="Norman French",
    ),
    "cara": Profile(
        strong="sta per",
        arts={"Mu": 6, "An": 7, "Aq": 6},
        abilities={"Heartbeast": (5, "the piest"), "Swim": (5, "cold water")},
        age=45,
        native="English",
    ),
    # Valnastium
    "constance": Profile(
        strong="int dex",
        arts={"Cr": 7, "Te": 7, "Vi": 6, "Re": 5},
        abilities={
            "Magic Theory": (9, "laboratories"),
            "Craft: Smith": (5, "fine work"),
        },
        native="Italian",
    ),
    "angela": Profile(
        strong="int dex",
        arts={"Cr": 6, "Im": 6, "Vi": 5},
        abilities={
            "Craft: Instrument maker": (6, "strings"),
            "Bargain": (4, "the Fair"),
        },
        age=70,
        native="Italian",
    ),
    "sourdine": Profile(
        strong="pre com",
        arts={"Me": 8, "Im": 7, "In": 5},
        abilities={
            "Guile": (5, "posing as a servant"),
            "Intrigue": (5, "the Emperor's court"),
        },
        age=70,
        native="Italian",
    ),
    "sirocco": Profile(
        strong="int com",
        arts={"In": 5, "Me": 5, "Im": 4},
        abilities={
            "Living Language: Arabic": (4, "diplomacy"),
            "Etiquette": (4, "Moorish courts"),
        },
        age=40,
        native="Greek",
    ),
    "grazia": Profile(
        strong="per sta",
        arts={"An": 9, "Re": 6, "Cr": 5},
        abilities={"Animal Handling": (6, "horses"), "Animal Ken": (3, "hounds")},
        age=60,
        native="Italian",
    ),
    "kalliope": Profile(
        strong="int per",
        arts={"In": 6, "An": 4, "He": 4},
        abilities={
            "Profession: Librarian": (7, "mundane research"),
            "Artes Liberales": (5, "grammar"),
        },
        age=55,
        native="Greek",
    ),
    "bronwyn": Profile(
        strong="int com",
        arts={"Im": 7, "Me": 5, "Vi": 4},
        abilities={"Music": (4, "verse"), "Magic Theory": (6, "spell words")},
        age=75,
        native="Welsh",
    ),
    "carmine": Profile(
        strong="pre dex",
        arts={"Cr": 6, "Ig": 9, "Te": 6, "Pe": 4},
        abilities={"Music": (5, "song"), "Single Weapon": (3, "sword")},
        age=70,
        native="Castilian",
    ),
}
