"""The printed stat blocks, converted from the Fourth Edition (N9), and
everyone else's generated stats (N10).

Nine magi: Andrei Soitkchin (p. 114), Yury Beslav (p. 115), Zashya
Miyovna (p. 117), Malincka Capcek (p. 124), Nastassia Baramov (p. 127),
Rehamchi Danichev (p. 129), Yellina Ozwry (p. 134), Stanis Chechenko (p.
140) and Yannes Kolski (p. 143), each written here as the book prints
it, a `fourth.Fourth`, and converted by `fourth.convert` with the
readings that module lists: printed ages kept, Confidence at the
Definitive Edition's baseline (DE p. 29), Twilight Points / 3 as
Warping, Certamen's experience moved to Penetration. A 4e Magical Affinity with
an Art is Affinity with that Art; with something else (weather, birds) a
Minor Magical Focus. A Major Magical Deficiency in a Technique is
Deficient Technique. Follower of Bjornaer gives way to the House's
Heartbeast, Will Over Form to the Heartbeast Ability.

Five of them print no spells, only the Arts in which they know "all
listed formulaics" (Andrei, Yury, Zashya, Yellina, Stanis, and Yannes,
whose magic is broken): they know the Definitive Edition's spells of
those Arts within their Lab Totals in their covenant's aura
(`fourth.listed`), mastered where the book says they are. Malincka's
four aura spells and Nastassia's Echo of the Firebird are their own, at
their printed levels (N12); the book leaves open whether aura-making can
work (p. 120).

Rehamchi is a Volkhv and a magus of Ex Miscellanea: his Fourth Edition
Disciplines, Pagan Conviction and principal god are in his biography,
not converted (N11, N18).

Everyone else the book describes gets generated stats from a profile of
its paragraph (book_packs.generated), at the age the book gives or the
one assumed here, except Batiba an Khatiba, a Cuman shaman whose magic
has no tradition record and is no Hermetic magic to generate, so he
stays a sketch (N11)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ..builder import characteristics
from ..fourth import Fourth, arts, convert, listed
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character
    from ..records import Records

#: The Area Lore that takes a block's Legend Lore.
AREA = "Novgorod Tribunal"

ANDREI = Fourth(
    age=122,
    apparent=None,
    characteristics=characteristics(2, 2, 1, 1, -1, -2, 0, 2),
    confidence=4,
    twilight=16,
    decrepitude=1,
    size=-1,
    virtues=[
        ("Quaesitor", 1),
        ("Magical Affinity", 4, "Intellego"),
        ("Strong-willed", 1),
        ("Visual Eidetic Memory", 3),
        ("Creative Block", -1),
        ("Weak Parma Magica", -3, "music"),
        ("Non-combatant", -2),
        ("Small Frame", -3),
    ],
    abilities=[
        ("Area Lore: Novgorod District", 5, "politics"),
        ("Awareness", 2, "searching"),
        ("Certamen", 7, "Intellego"),
        ("Civil and Canon Law", 4, "north Russian"),
        ("Concentration", 6, "reading"),
        ("Disputatio", 4, "debate"),
        ("Finesse", 4, "Mentem"),
        ("Folk Ken", 4, "magi"),
        ("Hermes Lore", 6, "history"),
        ("Hermetic Law", 6, "Tribunal procedures"),
        ("Intrigue", 3, "alliances"),
        ("Magic Theory", 9, "inventing spells"),
        ("Magic Affinity", 4, "Intellego"),
        ("Parma Magica", 6, "Mentem"),
        ("Penetration", 5, "Intellego"),
        ("Ride", 3, "speed"),
        ("Scribe Latin", 5, "copying"),
        ("Scribe Cyrillic", 4, "copying"),
        ("Speak Latin", 6, "Hermetic"),
        ("Speak Russian", 5, "Novgorod dialect"),
    ],
    arts=arts(12, 28, 10, 19, 26, 7, 8, 9, 26, 9, 12, 23, 30, 10, 22),
    spells=[],
    traits={"Patient": 2, "Scrupulous": 3, "Severe": 2},
    reputations={
        "Impartial Judge (Order of Hermes)": 4,
        "Over-formal (Novgorod magi)": 2,
    },
    mastery=1,
    notes=(
        "Chief Quaesitor, an office of House Guernicus. Rheumatism and a "
        "leg weakened in Twilight. His Cloak of Silken Steel, made by "
        "Nicollo decades ago, is a formal robe of dark blue and grey silk "
        "that turns violence like supple mail: Protection 10, no Load. "
        "The book has him master every listed spell of InMe, InIm, PeIm, "
        "ReCo, ReIm, ReMe and ReVi, with enhanced truth, lie-detection and "
        "compulsion spells of his own, and defensive spells of invisibility, "
        "teleportation and mind domination."
    ),
)

YURY = Fourth(
    age=117,
    apparent=None,
    characteristics=characteristics(2, 1, 2, 2, 1, 0, 1, -2),
    confidence=4,
    twilight=20,
    decrepitude=1,
    virtues=[
        ("Gentle Gift", 1),
        ("Quiet Magic", 2),
        ("Well Traveled", 1),
        ("Subtle Magic", 2),
        ("Temporal Influence", 2),
        (
            "Deleterious Circumstances",
            -4,
            "alone: magic works only with two or more people present",
        ),
        ("Incompatible Arts", -1, "Muto and Corpus"),
        ("Deep Sleeper", -1),
        ("Clumsy", -2),
    ],
    abilities=[
        ("Area Lore: Novgorod Trade Territories", 3, "geography"),
        ("Area Lore: Novgorod District", 5, "personalities"),
        ("Artes Liberales", 3, "music"),
        ("Bargain", 5, "forest products"),
        ("Brawling", 3, "dodge"),
        ("Carouse", 3, "games of chance"),
        ("Certamen", 5, "Mentem"),
        ("Charm", 3, "first impressions"),
        ("Civil and Canon Law", 4, "north Russian"),
        ("Concentration", 3, "inventing spells"),
        ("Disputatio", 3, "teaching"),
        ("Etiquette", 5, "nobility"),
        ("Finesse", 3, "Mentem"),
        ("Folk Ken", 4, "townsfolk"),
        ("Great Weapon", 3, "quarterstaff"),
        ("Hermes Lore", 5, "politics"),
        ("Hermetic Law", 4, "mundane relations"),
        ("Magic Theory", 10, "potions"),
        ("Parma Magica", 6, "Mentem"),
        ("Penetration", 3, "Mentem"),
        ("Ride", 3, "speed"),
        ("Scribe Bulgar", 3, "original composition"),
        ("Scribe Latin", 6, "original composition"),
        ("Scribe Cyrillic", 4, "original composition"),
        ("Speak Bulgar", 3, "trade"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Polish", 2, "Leczyca dialect"),
        ("Speak Russian", 5, "Novgorod dialect"),
        ("Storytelling", 4, "epics"),
        ("Wagoneering", 3, "rough terrain"),
    ],
    arts=arts(19, 21, 18, 17, 22, 14, 9, 11, 24, 16, 19, 19, 26, 14, 21),
    spells=[],
    traits={"Genial": 2, "Gregarious": 2, "Shrewd": 4},
    reputations={
        "Canny bargainer (local merchants)": 4,
        "Venerable patriarch (Novgorod district)": 3,
        "Politician (Order of Hermes)": 3,
    },
    mastery=1,
    notes=(
        "Balding, rheumatic and short-sighted. His Deleterious "
        "Circumstances, worsened from major to total in Twilight, is the "
        "Definitive Edition's Minor Flaw here, though his magic fails "
        "altogether when he is alone. His quarterstaff is enchanted to "
        "stony hardness (Damage +6), his fur robes to strength and "
        "resistance (Protection +5). The book has him master every listed "
        "spell of InCo, InIm, InMe, ReCo, ReIm and ReMe, and abhor flashy "
        "destructive magic."
    ),
)

ZASHYA = Fourth(
    age=119,
    apparent=None,
    characteristics=characteristics(2, 1, 2, 0, -1, 0, 1, 0),
    confidence=2,
    twilight=15,
    decrepitude=0,
    granted=["Heartbeast"],
    virtues=[
        ("Follower of Bjornaer", 1),
        ("Magic Affinity", 2, "weather"),
        ("Magical Affinity", 3, "Animal"),
        ("Animal Ken", 1),
        ("Venus' Blessing", 1),
        ("Dark Secret", -1),
        ("Major Magical Deficiency", -4, "Perdo"),
        ("Common Fear", -2),
        ("Cyclic Magic (-)", -1, "the dark of the moon"),
    ],
    abilities=[
        ("Animal Ken", 5, "birds"),
        ("Area Lore: Kiev", 2, "personalities"),
        ("Area Lore: Novgorod District", 5, "geography"),
        ("Artes Liberales", 3, "music"),
        ("Awareness", 5, "alertness"),
        ("Brawling", 4, "dodge"),
        ("Certamen", 6, "Animal"),
        ("Charm", 5, "courtly love"),
        ("Chirurgy", 3, "binding wounds"),
        ("Concentration", 6, "spells"),
        ("Disputatio", 4, "teaching"),
        ("Etiquette", 4, "court"),
        ("Faerie Lore", 3, "water faeries"),
        ("Finesse", 5, "grace"),
        ("Hermes Lore", 3, "politics"),
        ("Magic Affinity", 6, "Animal"),
        ("Magic Affinity", 5, "weather"),
        ("Magic Theory", 10, "potions"),
        ("Parma Magica", 6, "Auram"),
        ("Penetration", 5, "Animal"),
        ("Play Harp", 4, "solo"),
        ("Scribe Latin", 5, "illuminating"),
        ("Scribe Cyrillic", 5, "illuminating"),
        ("Sing", 3, "ballads"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Russian", 5, "Novgorod dialect"),
        ("Survival", 5, "lakes"),
        ("Swim", 3, "underwater"),
        ("Will Over Form", 6, "the swan"),
    ],
    arts=arts(20, 16, 30, 7, 29, 27, 14, 25, 28, 11, 9, 12, 16, 9, 21),
    spells=[],
    traits={"Gentle": 2, "Conciliatory": 3, "Passionate": 2},
    reputations={
        "Romantic soul (Novgorod Tribunal)": 4,
        "Great beauty (Novgorod district)": 4,
    },
    notes=(
        "Swan heart-beast, not battle-worthy, its shape hidden. "
        "Claustrophobic; short of breath. Her Cloak of Silken Feathers, "
        "Nicollo's gift, is snow-white silk stitched with tiny diamonds: "
        "Protection 4, and at a word it becomes a feather mantle that "
        "merges with her swan's plumage. The book has her extremely "
        "powerful in CrAu, CrAn, MuAu and MuAn, with Aquam and Corpus "
        "requisites, knowing few formulaics outside them; she can work "
        "enhanced versions of most combat CrAu spells."
    ),
)

MALINCKA = Fourth(
    age=70,
    apparent=None,
    characteristics=characteristics(4, 2, -1, 1, -1, 0, 2, 1),
    confidence=4,
    twilight=12,
    decrepitude=0,
    size=-1,
    virtues=[
        ("Hermetic Prestige", 1),
        ("Magical Affinity", 3, "Vim"),
        ("Higher Purpose", 1),
        ("Magic Sensitivity", 1),
        ("Great Characteristic", 2, "Intelligence"),
        ("Small Frame", -3),
        ("Major Magical Deficiency", -4, "Perdo"),
        ("Driving Goal", -1),
    ],
    abilities=[
        ("Area Lore: Hungary", 3, "Buda"),
        ("Area Lore: Urals", 3, "the Kama river"),
        ("Awareness", 3, "searching"),
        ("Brawling", 2, "dagger"),
        ("Certamen", 4, "Intellego"),
        ("Concentration", 4, "lab work"),
        ("Faerie Lore", 4, "Slavic"),
        ("Finesse", 3, "Vim"),
        ("Hermes Lore", 3, "history"),
        ("Legend Lore", 2, "Slavic gods"),
        ("Magic Affinity", 6, "Vim"),
        ("Magic Sensitivity", 4, "auras"),
        ("Magic Theory", 8, "inventing spells"),
        ("Parma Magica", 5, "Ignem"),
        ("Penetration", 2, "Intellego"),
        ("Scribe Latin", 5, "original composition"),
        ("Scribe Cyrillic", 3, "original composition"),
        ("Speak Latin", 4, "Hermetic"),
        ("Speak Hungarian", 4, "Buda"),
        ("Speak Russian", 4, "Novgorod dialect"),
    ],
    arts=arts(14, 19, 11, 5, 11, 8, 6, 5, 15, 6, 7, 10, 17, 6, 18),
    spells=[
        ("Shiver of the Lycanthrope", "InAn", 10),
        ("Tongue of the Beasts", "InAn", 20),
        ("The Immaculate Beast", "MuAn", 15),
        ("Soothe the Ferocious Bear", "ReAn", 5),
        ("Voice of the Lake", "InAq", 25),
        ("Ward Against Faeries of the Water", "ReAq", 15),
        ("Whispering Winds", "InAu", 15),
        ("Eyes of the Bat", "InAu", 25),
        ("Gentle Touch of the Purified Body", "CrCo", 15),
        ("Sight of the True Form", "InCo", 20),
        ("The Inexorable Search", "InCo", 20),
        ("Hunt for the Wild Herb", "InHe", 15),
        ("Pilum of Fire", "CrIg", 20),
        ("Eyes of the Past", "InIm", 20),
        ("Wizard's Sidestep", "ReIm", 10),
        ("Peering into the Mortal Mind", "InMe", 30),
        ("Emotion of Reversed Intentions", "MuMe", 20),
        ("Charge the Magical Circle", "CrVi", 25),
        ("Read the Magic Sphere", "InVi", 35),
        ("Plumb the Magical Scent", "InVi(Me)", 20),
        ("Air of Friendly Magic", "MuVi", 30),
    ],
    traits={"Compassionate": 2, "Impetuous": 2, "Proud": 1},
    reputations={
        "Follower of Bonisagus (Order of Hermes)": 3,
        "Radical (Novgorodian magi)": 4,
    },
    notes=(
        "Higher Purpose: to unite the Order of Hermes and mundanes. "
        "Driven: to invent a blended theory of Volkhv and Hermetic magic. "
        "Liver-spotted, stiff in the hips. Her Twilights gave her more Vim "
        "and an insight into Volkhv magic."
    ),
)

NASTASSIA = Fourth(
    age=54,
    apparent=None,
    characteristics=characteristics(1, 1, 2, 0, 1, 1, 1, 0),
    confidence=3,
    twilight=4,
    decrepitude=0,
    granted=["Heartbeast"],
    virtues=[
        ("Follower of Bjornaer", 2),
        ("Magic Affinity", 2, "birds"),
        ("Animal Ken", 1),
        ("Inspirational", 1),
        ("Fury", -3, "abuse of animals"),
        ("Major Magical Deficiency", -2, "Aquam"),
        ("Obsession", -1, "the Firebird"),
    ],
    abilities=[
        ("Animal Handling", 4, "falconry"),
        ("Animal Ken", 3, "birds"),
        ("Area Lore: Suzdalia", 2, "people"),
        ("Area Lore: Urals", 3, "the gorge"),
        ("Awareness", 3, "alertness"),
        ("Brawling", 3, "dodge"),
        ("Certamen", 3, "Ignem"),
        ("Concentration", 2, "spells"),
        ("Finesse", 2, "precision"),
        ("Hermes Lore", 3, "politics"),
        ("Leadership", 3, "obedience"),
        ("Legend Lore", 3, "beasts"),
        ("Magic Affinity", 4, "birds"),
        ("Magic Theory", 6, "inventing spells"),
        ("Parma Magica", 3, "Ignem"),
        ("Penetration", 2, "Ignem"),
        ("Scribe Latin", 4, "copying"),
        ("Scribe Cyrillic", 3, "copying"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Russian", 4, "Suzdal dialect"),
        ("Survival", 3, "mountains"),
        ("Will Over Form", 3, "the eagle"),
    ],
    arts=arts(5, 11, 15, 5, 8, 16, 6, 14, 16, 8, 15, 7, 5, 7, 10),
    spells=[
        ("Full Health of Beast and Bird", "CrAn", 25),
        ("Soothe Pains of the Beast", "CrAn", 20),
        ("Tongue of the Beasts", "InAn", 20),
        ("Tongue of the Birds", "InAn", 30),
        ("The Immaculate Beast", "MuAn", 15),
        ("Soothe the Ferocious Bear", "ReAn", 5),
        ("The Gentle Beast", "ReAn", 20),
        ("Eyes of the Bat", "InAu", 25),
        ("Preternatural Growth and Shrinking", "MuCo", 20),
        ("Shape of the Woodland Prowler", "MuCo", 25),
        ("Form of the Avenging Beast", "MuCo", 20),
        ("Echo of the Firebird", "MuCo(An,Au,Ig)", 40),
        ("Rise of the Feathery Body", "ReCo", 5),
        ("Lamp Without Flame", "CrIg", 10),
        ("Pilum of Fire", "CrIg", 20),
        ("Prison of Flames", "MuIg", 15),
        ("Trapping the Fire", "MuIg", 25),
    ],
    traits={"Brave": 3, "Determined": 2, "Overbearing": 2},
    reputations={
        "Radical (Novgorod Tribunal)": 2,
        "Radical (House Bjornaer)": 4,
        "Intemperate (Order of Hermes)": 1,
    },
    notes=(
        "Eagle heart-beast, battle-worthy, its shape hidden; as an "
        "Avenging Beast or under Echo of the Firebird it gains Soak +15. "
        "The book's Tongue of the Birds is an extended-range version. A "
        "devotee of Khors and of Hermes."
    ),
)

REHAMCHI = Fourth(
    age=71,
    apparent=None,
    characteristics=characteristics(2, 1, 1, 0, 0, 1, 0, 1),
    confidence=0,
    twilight=3,
    decrepitude=0,
    traditions=["trad_volkhvy"],
    virtues=[
        ("Volkhv", 2),
        ("Emerged Latent Magical Ability", 2, "swallow heart-beast"),
        ("Cyclic Magic (+)", 2, "noon"),
        ("Herbalism", 1),
        ("Second Sight", 1),
        ("Cyclic Magic (-)", -2, "midnight"),
        ("Susceptible to Divine Power", -4),
        ("Slow Caster", -2),
    ],
    abilities=[
        ("Area Lore: Urals", 5, "the Kama river"),
        ("Awareness", 4, "alertness"),
        ("Brawling", 3, "dagger"),
        ("Chirurgy", 5, "wounds"),
        ("Clan History", 5, "ancestors"),
        ("Climb", 2, "trees"),
        ("Concentration", 4, "spells"),
        ("Faerie Lore", 7, "faerie lords"),
        ("Finesse", 2, "precision"),
        ("Herbalism", 4, "simples"),
        ("Hermes Lore", 2, "politics"),
        ("Hunt", 3, "tracks"),
        ("Magic Theory", 3, "inventing spells"),
        ("Parma Magica", 2, "Animal"),
        ("Penetration", 1, "Animal"),
        ("Scribe Latin", 2, "copying"),
        ("Second Sight", 4, "spirits"),
        ("Shield and Weapon", 3, "shortspear and round shield"),
        ("Sing", 5, "solo"),
        ("Theology: Slavic", 5, "the gods of the Kama"),
        ("Legend Lore", 6, "Slavic"),
        ("Speak Latin", 3, "Hermetic"),
        ("Speak Russian", 5, "Ural dialect"),
        ("Stealth", 3, "wilderness"),
        ("Survival", 4, "hill country"),
    ],
    arts=arts(6, 7, 4, 2, 5, 4, 1, 5, 6, 6, 4, 4, 1, 2, 5),
    spells=[
        ("Shiver of the Lycanthrope", "InAn", 10),
        ("Soothe the Ferocious Bear", "ReAn", 5),
        ("Whispering Winds", "InAu", 15),
        ("Gentle Touch of the Purified Body", "CrCo", 15),
        ("Hunt for the Wild Herb", "InHe", 15),
        ("Wizard's Sidestep", "ReIm", 10),
    ],
    traits={"Wry": 2, "Patient": 3},
    reputations={
        "Holy (Thousand Caves)": 2,
        "Hedge wizard (Novgorod Tribunal)": 2,
    },
    notes=(
        "A Volkhv, priest of Khors, with Pagan Conviction 6. His Fourth "
        "Edition Disciplines are kept here as the book prints them, not "
        "converted: Spirit Touch 6, Healing 7, Shapeshift 6, "
        "Weatherworking 9, Animal Magic 8, Remove Curse 10, Prophecy 7, "
        "Sun Magic 11 and Earth Magic 6; Khors gives him +5 Sun Magic, "
        "+3 Spirit Touch, +3 to the Great Ritual and +3 to shift into a "
        "golden horse, and -5 Earth Magic. His Volkhv Magic Resistance is "
        "his Conviction, 3 more at noon and 3 less at midnight; in "
        "Communion it adds the aura, and his Communion Total against "
        "fire, heat and Ignem; he takes the better of it or his Parma, not "
        "both. Nastassia found his swallow heart-beast. Bad teeth, a "
        "limp. Shortspear, round shield and a fur hauberk. The book "
        "prints no Confidence for him."
    ),
)

YELLINA = Fourth(
    age=139,
    apparent=None,
    characteristics=characteristics(3, 1, -1, 0, -1, 0, 1, 1),
    confidence=3,
    twilight=21,
    decrepitude=3,
    granted=["Heartbeast"],
    virtues=[
        ("Follower of Bjornaer", 2),
        ("Special Circumstances", 1, "swimming"),
        ("Animal Ken", 1),
        ("Herbalism", 1),
        ("Quiet Magic", 2),
        ("Reclusive", -1),
        ("Chaotic Magic", -4),
        ("Blatant Gift", -1),
        ("Delusion", -1, "her parens Roslav is alive"),
    ],
    abilities=[
        ("Animal Ken", 6, "water beasts"),
        ("Area Lore: Pripet", 6, "geography"),
        ("Artes Liberales", 4, "astronomy"),
        ("Awareness", 4, "keeping watch"),
        ("Brawling", 4, "dodge"),
        ("Certamen", 6, "Aquam"),
        ("Boating", 5, "fishing"),
        ("Concentration", 5, "spells"),
        ("Faerie Lore", 4, "marsh faeries"),
        ("Finesse", 5, "precision"),
        ("Herbalism", 7, "antidotes"),
        ("Hermetic Lore", 6, "politics"),
        ("Hermetic Law", 4, "Tribunal procedures"),
        ("Intrigue", 5, "alliances"),
        ("Lectio", 6, "tractatus"),
        ("Magic Theory", 11, "potions"),
        ("Parma Magica", 6, "Aquam"),
        ("Penetration", 5, "Aquam"),
        ("Scribe Latin", 5, "copying"),
        ("Scribe Cyrillic", 4, "copying"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Russian", 5, "Turov dialect"),
        ("Stealth", 5, "natural places"),
        ("Survival", 5, "marsh"),
        ("Swim", 6, "underwater"),
        ("Will Over Form", 6, "the otter"),
    ],
    arts=arts(19, 22, 32, 17, 26, 34, 27, 16, 29, 24, 12, 13, 15, 14, 21),
    spells=[],
    traits={"Otter": 5, "Secretive": 3, "Wary": 3, "Protective": 3},
    reputations={
        "Senile (Novgorod Tribunal)": 2,
        "Respected (House Bjornaer)": 2,
    },
    notes=(
        "Otter heart-beast, battle-worthy, its shape hidden. Afflictions: "
        "a limp, failing sight, deafness (she reads lips by a minor InCo "
        "spell), dementia and long-term memory loss; her dementia counts "
        "against her in spontaneous magic and in controlling a Twilight. "
        "A Twilight gave her Clumsy Magic and the next turned it to "
        "Chaotic Magic; she is near Final Twilight. The book has her know "
        "every listed Animal spell and every listed MuCo, InCo, MuHe and "
        "MuAq spell, and any formulaic her Technique + Form beats by ten "
        "levels, casting level 10 and less spontaneously."
    ),
)

STANIS = Fourth(
    age=101,
    apparent=None,
    characteristics=characteristics(3, 0, 1, 1, 0, -1, 0, 0),
    confidence=3,
    twilight=17,
    decrepitude=0,
    virtues=[
        ("Gentle Gift", 1),
        ("Deft Art", 1, "Rego"),
        ("Busybody", 1),
        ("Social Contacts", 1, "nobility"),
        ("Free Expression", 1),
        ("Patron", 2),
        ("Major Magical Deficiency", -4, "Creo"),
        ("Faerie Enmity", -1),
        ("Common Fear", -2, "cats"),
    ],
    abilities=[
        ("Animal Handling", 3, "horses"),
        ("Area Lore: Leczyca", 5, "politics"),
        ("Area Lore: Sieradz", 3, "politics"),
        ("Area Lore: Silesia", 4, "politics"),
        ("Artes Liberales", 3, "rhetoric"),
        ("Brawling", 3, "dagger"),
        ("Certamen", 7, "Rego"),
        ("Charm", 3, "wit"),
        ("Civil and Canon Law", 5, "papal law"),
        ("Concentration", 3, "lab work"),
        ("Disputatio", 4, "debate"),
        ("Etiquette", 5, "nobility"),
        ("Finesse", 5, "grace"),
        ("Folk Ken", 5, "nobles"),
        ("Hermes Lore", 5, "politics"),
        ("Hermetic Law", 4, "Wizard's Marches"),
        ("Intrigue", 3, "plotting"),
        ("Longshaft Weapons", 4, "lance"),
        ("Magic Theory", 8, "potions"),
        ("Parma Magica", 6, "Rego"),
        ("Penetration", 4, "Rego"),
        ("Play Lute", 5, "solo"),
        ("Ride", 4, "battle"),
        ("Scribe Latin", 5, "original composition"),
        ("Shield and Weapon", 4, "longsword and round shield"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Polish", 5, "Leczyca dialect"),
        ("Speak Russian", 2, "Novgorod dialect"),
        ("Theology", 3, "the Bible"),
    ],
    arts=arts(12, 19, 14, 27, 29, 10, 5, 9, 21, 8, 11, 9, 22, 9, 18),
    spells=[],
    traits={"Manipulative": 2, "Argumentative": 3, "Stubborn": 2},
    reputations={
        "Skilled lutist (Polish nobles)": 4,
        "Political hack (Order of Hermes)": 2,
    },
    mastery=1,
    notes=(
        "His patron is the Count of Leczyca. A stooped back, rheumatism, "
        "fretful bouts. A Twilight turned his minor Creo deficiency major. "
        "His lance, longsword and dagger carry an enhanced Razor's Edge "
        "(Damage +6), his shield and half chain mail subtle ReTe spells "
        "that lighten them. The book has him master every listed spell of "
        "Rego and Perdo with Corpus and Mentem, for political influence "
        "and battlefield destruction."
    ),
)

YANNES = Fourth(
    age=127,
    apparent=None,
    characteristics=characteristics(4, 3, -2, -4, 0, 0, 1, 2),
    confidence=0,
    twilight=23,
    decrepitude=4,
    virtues=[
        ("Great Intelligence", 2, "Intelligence"),
        ("Knack with Enigma", 3, "Enigmatic Wisdom"),
        ("Visions", 2),
        ("Poor Communication", -2, "Communication"),
        ("Sense of Doom", -3),
        ("Unpredictable Magic", -4),
        ("Painful Magic", -3),
        ("Blatant Gift", -1),
    ],
    abilities=[
        ("Area Lore: Leczyca", 5, "politics"),
        ("Area Lore: Silesia", 3, "politics"),
        ("Artes Liberales", 6, "geometry"),
        ("Awareness", 5, "alertness"),
        ("Brawling", 2, "dagger"),
        ("Certamen", 4, "Mentem"),
        ("Civil and Canon Law", 6, "Polish"),
        ("Concentration", 6, "spells"),
        ("Disputatio", 6, "debate"),
        ("Enigmatic Wisdom", 7, "prophecy"),
        ("Finesse", 6, "grace"),
        ("Hermes Lore", 6, "history"),
        ("Hermetic Law", 3, "political intrigue"),
        ("Magic Theory", 9, "inventing spells"),
        ("Occult Lore", 4, "demons"),
        ("Parma Magica", 7, "Mentem"),
        ("Penetration", 6, "Mentem"),
        ("Philosophiae", 7, "metaphysics"),
        ("Ride", 4, "speed"),
        ("Scribe Latin", 6, "original composition"),
        ("Speak Latin", 5, "Hermetic"),
        ("Speak Polish", 5, "Leczyca dialect"),
        ("Theology", 4, "the Bible"),
        ("Visions", 8, "the serpent from the east"),
    ],
    arts=arts(17, 22, 23, 16, 17, 17, 14, 16, 22, 16, 18, 21, 24, 15, 22),
    spells=[],
    traits={"Lunatic": 6, "Inscrutable": 6},
    reputations={
        "Mad (Order of Hermes)": 4,
        "Passed into Final Twilight (Novgorod Tribunal)": 2,
    },
    mastery=1,
    notes=(
        "Afflictions: dementia, a limp, trouble speaking and greater "
        "trouble understanding speech, epilepsy. His longevity potion has "
        "failed. His great Twilight of 1206 gave him Unpredictable and "
        "Painful Magic; he has not worked magic since, and the storyguide "
        "may make it useless or wholly uncontrollable. The book has him "
        "master every listed spell of Intellego and Muto with Corpus, "
        "Imaginem, Mentem and Vim. Visions 8 has no Ability now; the "
        "Virtue stays."
    ),
)

#: The blocks, by magus key, with the aura of the covenant each works in.
BLOCKS: dict[str, tuple[Fourth, int]] = {
    "andrei": (ANDREI, 4),
    "yury": (YURY, 4),
    "zashya": (ZASHYA, 4),
    "malincka": (MALINCKA, 0),
    "nastassia": (NASTASSIA, 0),
    "rehamchi": (REHAMCHI, 0),
    "yellina": (YELLINA, 6),
    "stanis": (STANIS, 4),
    "yannes": (YANNES, 4),
}
#: The Arts whose listed spells a magus knows, where the book prints no
#: spells: (Technique and Form pairs, the lowest level he casts as a
#: formulaic).
LISTED: dict[str, tuple[tuple[str, ...], int]] = {
    "andrei": (("InMe", "InIm", "PeIm", "ReCo", "ReIm", "ReMe", "ReVi"), 0),
    "yury": (("InCo", "InIm", "InMe", "ReCo", "ReIm", "ReMe"), 0),
    "zashya": (("CrAu", "CrAn", "MuAu", "MuAn"), 0),
    "yellina": (
        ("CrAn", "InAn", "MuAn", "PeAn", "ReAn", "MuCo", "InCo", "MuHe", "MuAq"),
        10,
    ),
    "stanis": (("ReCo", "ReMe", "PeCo", "PeMe"), 0),
    "yannes": (
        ("InCo", "InIm", "InMe", "InVi", "MuCo", "MuIm", "MuMe", "MuVi"),
        0,
    ),
}

#: The printed longevity modifiers (carried across, DE p. 391).
LONGEVITY: dict[str, int] = {
    "andrei": 14,
    "yury": 13,
    "zashya": 13,
    "malincka": 10,
    "nastassia": 8,
    "rehamchi": 5,
    "yellina": 14,
    "stanis": 12,
}

#: The magi's own spells: Range, Duration, Target, page, and what it does.
OWN_SPELLS: dict[str, tuple[str, str, str, str, str]] = {
    "Charge the Magical Circle": (
        "Touch",
        "Sun",
        "Circle",
        "125",
        "A Ritual blending Hermetic method with Volkhv dance and sung "
        "invocations to Slavic gods, which raises a small circular magic "
        "aura where none was: +1 for one extra pawn of vis beyond the "
        "Ritual's, +2 for three, +3 for six, and so on up the pyramid "
        "(none extra gives a worthless +0). Cast always with six botch "
        "dice; cast where an aura exists it fails, with as many more botch "
        "dice as the aura's strength, and other things nearby can twist "
        "it (Herbam vis at its edge once raised a +10 aura and opened a "
        "gate to the Spirit Lands). Malincka thinks it useless without "
        "mundanes to steady it. The book's level stands, and leaves open "
        "whether aura-making can truly work (p. 120).",
    ),
    "Air of Friendly Magic": (
        "Personal",
        "Sun",
        "Room",
        "125",
        "A Ritual, again of blended method, that turns a small area of "
        "Faerie aura of 6 or less into a Magic aura of the same strength. "
        "It needs six mundane assistants making Hermetic gestures and "
        "Volkhv chants, whose part steadies it for reasons she does not "
        "yet know. Cast with three extra botch dice; spells cast in the "
        "changed aura have two, and the aura stays faerie-tainted, so "
        "spells show fay traits and botches bring bizarre faerie "
        "manifestations. The book's level stands; whether aura-making can "
        "truly work the book leaves open (p. 120).",
    ),
    "Read the Magic Sphere": (
        "Personal",
        "Concentration",
        "Individual",
        "125",
        "Her newest aura spell, eight years old: she sees any aura, chiefly "
        "by sight, to the limit of her view, and may walk its bounds. She "
        "knows its realm at once; a Perception roll tells its strength up "
        "to 7 (9+), the way to its centre (12+) and its age (15+). With "
        "Magic Sensitivity all that comes freely, with +5 to Sensitivity, "
        "and Per + Sensitivity asks whether it is stable, waning or "
        "growing (12+), its source and whether another aura was there "
        "before (15+), how long ago and of what kind (18+), and its "
        "strength (21+). The book's level stands.",
    ),
    "Plumb the Magical Scent": (
        "Personal",
        "Momentary",
        "Group",
        "126",
        "Her first study of how a Great Ritual touches its worshippers' "
        "minds: tells whether a human mind is under magic's influence, and "
        "a Per + Magic Sensitivity stress roll of 9+ gives details. Useful "
        "but imprecise, and its fleeting duration makes it clumsy. The "
        "book's level stands.",
    ),
    "Form of the Avenging Beast": (
        "Personal",
        "Sun",
        "Individual",
        "110",
        "The Bjornaer spell the book reprints from Houses of Hermes: the "
        "heart-beast grows more powerful, fearsome and larger, if a little "
        "distorted. A battle-worthy beast gains +5 Attack and Damage and +15 "
        "Soak, any other +3, +3 and +10, and neither feels wounds or fatigue "
        "until it falls. Spell focus a part of such an animal (+2). The "
        "book's level stands.",
    ),
    "Echo of the Firebird": (
        "Personal",
        "Sun",
        "Individual",
        "128",
        "Nastassia's newest heart-beast spell: her eagle grows toward an "
        "ideal Firebird, Size +1, Attack +5, Damage +8 and Soak +15, "
        "untroubled by wounds or fatigue until it drops; feathers, talons "
        "and beak gleam ruddy gold and trail wisps of flame in flight, and "
        "it radiates heat, touching it like touching a torch. Not "
        "cumulative with Form of the Avenging Beast. The book's level "
        "stands.",
    ),
}


def stats(records: Records) -> None:
    b = records.b
    for key, (block, aura) in BLOCKS.items():
        character = records.magi.get(key)
        if character is None:
            continue
        if key in LISTED:
            pairs, above = LISTED[key]
            theory = next(s for n, s, _ in block.abilities if n == "Magic Theory")
            block = replace(
                block,
                spells=listed(
                    pairs,
                    block.arts,
                    block.characteristics["intelligence"],
                    theory,
                    aura,
                    above=above,
                ),
            )
        stat, age = convert(key, block, area=AREA)
        b.stats(character, stat)
        character.background.year_born = b.year - age
        _own_spells(character)
        if key in LONGEVITY:
            character.aging.longevity_modifier = LONGEVITY[key]
    for key, profile in PROFILES.items():
        character = records.magi.get(key)
        if character is not None:
            apply(b, character, profile)


def _own_spells(character: Character) -> None:
    for spell in character.invented_spells:
        own = OWN_SPELLS.get(spell.name)
        if own is None:
            continue
        spell.range, spell.duration, spell.target, spell.page = own[:4]
        spell.source = "D&B"
        spell.description = own[4]


RUSSIAN, POLISH = "Russian", "Polish"

PROFILES: dict[str, Profile] = {
    # Three Lakes
    "pavel": Profile(
        strong="int per",
        arts={"In": 7, "Me": 6, "Vi": 4},
        abilities={
            "Code of Hermes": (7, "Tribunal procedures"),
            "Magic Theory": (6, "enchanting devices"),
        },
        age=100,
        native=POLISH,
    ),
    "georgi": Profile(
        strong="com pre",
        arts={"In": 6, "Me": 6, "Re": 5, "Mu": 4, "Co": 4},
        abilities={
            "Bargain": (6, "furs"),
            "Area Lore: Novgorod Trade Territories": (5, "trails"),
            "Folk Ken": (4, "merchants"),
        },
        age=95,
        native=RUSSIAN,
    ),
    "susan": Profile(
        strong="sta per",
        arts={"Re": 6, "Co": 6, "Au": 4},
        abilities={
            "Ride": (5, "long journeys"),
            "Area Lore: Novgorod Tribunal": (6, "covenants"),
            "Survival": (5, "the north"),
        },
        age=100,
        native="Irish",
    ),
    "olga": Profile(
        strong="int com",
        arts={"Im": 6, "Me": 5, "Re": 4, "Vi": 4},
        abilities={
            "Faerie Lore": (8, "Slavic faeries"),
            "Teaching": (6, "apprentices"),
            "Etiquette": (4, "faerie courts"),
        },
        age=130,
        native=RUSSIAN,
    ),
    "boris": Profile(
        strong="sta str",
        arts={"An": 9, "Mu": 6, "In": 4},
        abilities={
            "Magic Lore": (5, "magical beasts"),
            "Faerie Lore": (4, "beast lords"),
        },
        native=RUSSIAN,
    ),
    "nicollo": Profile(
        strong="int dex",
        arts={"Cr": 6, "Te": 6, "Re": 5, "Vi": 5, "Ig": 4},
        abilities={
            "Magic Theory": (8, "enchanting devices"),
            "Craft: Goldsmith": (5, "fine work"),
            "Charm": (3, "dinner"),
        },
        age=110,
        native="Italian",
    ),
    # Thousand Caves
    "lelya": Profile(
        strong="pre int",
        arts={"Cr": 5, "An": 5, "Vi": 4},
        abilities={
            "Theology: Pagan": (5, "Khors"),
            "Music": (4, "rites"),
        },
        age=45,
        native=RUSSIAN,
    ),
    "basyl": Profile(
        strong="pre com",
        arts={"Im": 7, "Cr": 5, "Re": 4},
        abilities={
            "Faerie Lore": (5, "faerie friends"),
            "Guile": (4, "pranks"),
        },
        age=45,
        native=RUSSIAN,
    ),
    "otto": Profile(
        strong="per sta",
        arts={"An": 7, "Mu": 6, "Co": 5},
        abilities={
            "Area Lore: Urals": (4, "the tribes"),
            "Organization Lore: House Bjornaer": (6, "Crintera"),
        },
        age=110,
        native="High German",
    ),
    "yakim": Profile(
        strong="int sta",
        arts={"Cr": 6, "Ig": 7, "Pe": 4},
        abilities={
            "Philosophiae": (5, "natural philosophy"),
            "Theology: Islam": (4, "the schools"),
            "Medicine": (3, "Galenic"),
        },
        age=45,
        native="Bulgar",
    ),
    "narina": Profile(
        strong="per sta",
        weak="com",
        arts={"An": 8, "Cr": 5, "Co": 5, "He": 4},
        abilities={
            "Animal Ken": (5, "wild beasts"),
            "Survival": (5, "the Urals"),
            "Chirurgy": (4, "wounds"),
        },
        age=42,
        native=RUSSIAN,
    ),
    # Pripet Maior
    "vlachs": Profile(
        strong="per qik",
        arts={"An": 7, "Au": 6, "Mu": 6, "Cr": 4},
        abilities={"Awareness": (5, "keeping watch"), "Stealth": (4, "towns")},
        age=125,
        native="High German",
    ),
    "casimi": Profile(
        strong="str sta",
        weak="int",
        arts={"Mu": 7, "Co": 7, "An": 6},
        abilities={"Brawl": (5, "horns")},
        native=POLISH,
    ),
    "miya": Profile(
        strong="int com",
        arts={"Re": 7, "An": 8, "He": 5, "Mu": 4},
        abilities={"Animal Ken": (6, "waterfowl")},
        native=RUSSIAN,
    ),
    "lev": Profile(
        strong="int qik",
        arts={"Mu": 6, "An": 6, "Pe": 5, "Co": 5},
        abilities={"Stealth": (5, "the marsh"), "Guile": (4, "seeming pleasant")},
        age=120,
        native=RUSSIAN,
    ),
    # Leczyca
    "kasina": Profile(
        strong="pre int",
        arts={"Im": 6, "Mu": 5, "He": 4, "An": 4},
        abilities={
            "Faerie Lore": (6, "weird lore"),
            "Bows": (4, "short bow"),
        },
        age=100,
        native=POLISH,
    ),
    "frania": Profile(
        strong="int sta",
        arts={"Re": 6, "Pe": 5, "Me": 5, "Co": 4},
        abilities={
            "Civil and Canon Law": (5, "Polish law"),
            "Single Weapon": (4, "sword"),
        },
        age=100,
        native=POLISH,
    ),
    "tomaszi": Profile(
        strong="int dex",
        weak="com",
        arts={"Cr": 7, "Te": 7, "Re": 5, "Vi": 5},
        abilities={
            "Magic Theory": (8, "enchanting devices"),
            "Craft: Weaponsmith": (6, "swords"),
        },
        native=POLISH,
    ),
    "ruprecht": Profile(
        strong="sta str",
        arts={"Cr": 5, "Au": 5, "Pe": 5, "Te": 4},
        abilities={
            "Leadership": (5, "the turb"),
            "Ride": (4, "battle"),
            "Single Weapon": (4, "sword"),
        },
        native="Norman French",
    ),
    "sanya": Profile(
        strong="sta per",
        arts={"An": 7, "Mu": 5, "Te": 4},
        abilities={"Animal Handling": (5, "horses")},
        age=85,
        native=POLISH,
    ),
    "barchek": Profile(
        gifted=False,
        strong="sta qik",
        abilities={
            "Area Lore: Rhine Tribunal": (4, "covenants"),
            "Area Lore: Transylvanian Tribunal": (3, "the Carpathians"),
            "Ride": (4, "long journeys"),
            "Guile": (3, "passing as a peasant"),
            "Dead Language: Latin": 4,
        },
        age=40,
        native=POLISH,
    ),
}
