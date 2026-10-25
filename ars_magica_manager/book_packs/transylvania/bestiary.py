"""The Bestiary: every creature Against the Dark gives a stat block, from
chapter 8's dragons, giants, vampires and vilas to the stat blocks that
sit elsewhere in the book (Monica Ierne's wolf Silexa, the four-eyed dog
Zuban and Saint Ivan Rilski). Chapter 10 prints no stat blocks. Silexa
is also bound to Monica as her familiar.

The many beings the book names without stats (the great dragons of the
Pax Draconis, the Madara Horseman, the faerie queens, the white wolves
and the rest) are a sentence each in the summary of the place they
haunt, added in `finish`; a lair gets a place of its own only when no
region part made one.

Numbers are the book's; what powers do, how a creature looks and the
notes are a summary in the pack's own words. The page reference is the
chapter, since the Open Content text has no page numbers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ... import storage
from ...models import Ability, BodyVis, Familiar, Possession, ScoredTrait
from ...rules import creation_access as access
from ...rules.xp import ability_xp
from ..builder import _virtue_flaw, characteristics, vf_great, vf_ward, wound_ranges

if TYPE_CHECKING:
    from ...models import Covenant, Creature, Neighbour
    from . import Transylvania

#: A person's Fatigue levels, as the book's stat blocks print them.
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"

#: Where each creature lives: the place keys a region part may have made
#: (most likely first), words a place's name may hold, and the region to
#: fall back on.
HOMES: dict[str, tuple[tuple[str, ...], tuple[str, ...], str]] = {
    "upokorituma": (("upper_danube",), ("Upper Danube",), "hungary"),
    "danaslepih": (("drina", "danaslepih_grove"), ("Drina", "Danaslepih"), "slavs"),
    "giant_brothers": ((), ("Szekler",), "transylvania"),
    "costache": ((), (), "hungary"),
    "nicoleta": (
        ("madara", "madara_plateau", "madara_horseman"),
        ("Madara",),
        "bulgaria",
    ),
    "fet_frumos": (
        ("nicoleta_lair", "madara", "madara_plateau", "madara_horseman"),
        ("Madara",),
        "bulgaria",
    ),
    "vampire_human": ((), (), "transylvania"),
    "vampire_bestial": ((), (), "transylvania"),
    "vampire_incorporeal": ((), (), "transylvania"),
    "gadja": ((), (), "transylvania"),
    "vampire_snake": ((), (), "transylvania"),
    "vampire_tree": ((), (), "transylvania"),
    "broukolak": ((), (), "bulgaria"),
    "vila": (("seven_lakes",), ("Seven Lakes",), "slavs"),
    "zuban": ((), (), "bulgaria"),
    "ivan_rilski": (
        ("ivan_rilski_cave", "rila", "rila_monastery"),
        ("Ivan Rilski", "Rila"),
        "bulgaria",
    ),
}

#: The note on each place's link to its creature.
_ROLE = {
    "upokorituma": "an aždaja that sinks river boats on the upper Danube",
    "danaslepih": "a blind zmaj guarding a horse-chestnut grove",
    "giant_brothers": "two giant brothers forever quarrelling over a fence",
    "costache": "a giant kept chained in a barrel in some king's palace",
    "nicoleta": "a giant's mother on her hidden horse farm",
    "fet_frumos": "the faerie horse starved on Nicoleta's farm",
    "vampire_human": "the commonest vampire, wearing a dead villager's shape",
    "vampire_bestial": "the boneless wolf-shaped vampire",
    "vampire_incorporeal": "the unseen vampire that haunts a dead man's kin",
    "gadja": "the formless sack the young vampire becomes",
    "vampire_snake": "a snake turned vampire",
    "vampire_tree": "a hanging tree turned vampire",
    "broukolak": "the Bulgarian demon that wears a corpse",
    "vila": "a template for the white ladies of the Tribunal",
    "zuban": "a four-eyed dog, born to hunt vampires",
    "ivan_rilski": "the patron saint of Bulgaria",
}

#: The creatures this part makes, by slug, for `finish`.
_MADE: dict[str, Creature] = {}


def _power(name: str) -> tuple[str, dict[str, str]]:
    return ("Lesser Power", {"power": name})


def build(transylvania: Transylvania) -> None:
    _MADE.clear()
    _dragons(transylvania)
    _giants(transylvania)
    _vampires(transylvania)
    _vila(transylvania)
    _elsewhere(transylvania)


# -- chapter 8: dragons --


def _dragons(transylvania: Transylvania) -> None:
    b = transylvania.b
    _MADE["upokorituma"] = b.creature(
        "Upokorituma",
        page="p. 105",
        realm="Infernal",
        might=17,
        form="Vim",
        size=2,
        confidence=(1, 3),
        weakness="Abhorrent Material (Serbian spruce)",
        block={
            "characteristics": characteristics(0, 0, -2, -5, 2, 4, 1, -2),
            "virtues_flaws": [
                "Greater Infernal Power",
                "Greater Infernal Power",
                vf_great("Stamina"),
                "Lesser Infernal Power",
                "Tough",
                "Greedy",
                "Horrifying Appearance",
                (
                    "Demonic Weakness",
                    {"weakness": "Abhorrent material: Serbian spruce"},
                ),
                "Corrupted Beast",
                "Fear",
            ],
            "abilities": [
                ("Athletics", 3, "flying"),
                ("Awareness", 3, "food"),
                ("Brawl", 6, "claw"),
                ("Survival", 3, "wooded gulches"),
            ],
            "traits": {"Covetous": 6, "Furious": 3, "Vengeful": 3},
        },
        attacks=[b.attack("Claws", -3, 10, 8, 4)],
        soak=7,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Claws as Sharp as Satan's",
                5,
                3,
                "Animal",
                does="Hardens his claws for a day, adding +4 to their Damage.",
            ),
            b.power(
                "February's Frosty Bite",
                5,
                3,
                "Ignem",
                does="A cold so fierce it burns, striking a target he can see "
                "for +10 damage.",
            ),
            b.power(
                "Flight of the Raven",
                0,
                0,
                "Animal",
                does="Always on: gives him wings strong enough to fly.",
            ),
        ],
        vis=[BodyVis(4, "Vim", "one in each of his four biggest fangs")],
        appearance=(
            "Squat and heavy as a thick-legged horse, dark grey with pink "
            "eyes and gums the red of blood, with eight heads on eight thick "
            "necks and wings that look far too small for him, though he flies "
            "well."
        ),
        notes=(
            "An aždaja, an Infernal dragon: a corrupted beast rather than a "
            "demon, and, unlike most Infernal beasts, intelligent. The book "
            "builds him from Infernal Virtues and Flaws laid over beast "
            "Qualities (Realms of Power: The Infernal). His Fear is of doves. "
            "He hides in the ravines along the upper Danube and lies under "
            "the water waiting for merchant boats; once one has passed above "
            "him he rears up behind it, kills everyone aboard, sinks the "
            "hull and hauls the cargo home. "
            + wound_ranges(2)
            + "\nThe aždaje rank themselves by raw strength, the stronger "
            "taking the best lairs and hunting grounds and punishing the "
            "weaker; their lairs are bleak, rotting places, mostly in "
            "Infernal auras, and some pass themselves off as Magic dragons to "
            "keep the magi away."
        ),
    )
    _MADE["danaslepih"] = b.creature(
        "Danaslepih",
        page="p. 107",
        realm="Magic",
        might=25,
        form="Animal",
        size=4,
        season="Summer",
        confidence=(2, 6),
        block={
            "characteristics": characteristics(1, 0, -2, -5, 10, 3, 3, -2),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                *["Improved Characteristics"] * 3,
                "Self-Confident",
                "Tough",
                "Tough",
                "Blind",
                *["Gigantic"] * 3,
                *["Greater Power"] * 3,
                "Improved Attack",
                "Improved Initiative",
                "Improved Powers",
                *["Personal Power"] * 3,
                "Gift of Speech",
            ],
            "abilities": [
                ("Athletics", 3, "climbing"),
                ("Awareness", 2, "listening"),
                ("Brawl", 9, "large teeth"),
                ("Stealth", 3, "hiding"),
                ("Living Language: South Slavonic", 3, "Serbian"),
                ("Survival", 3, "forests"),
            ],
            "traits": {"Protective": 6, "Aloof": 3, "Disrespectful": 3},
        },
        attacks=[b.attack("Bite", 0, 17, 9, 13)],
        soak=9,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "The Beast with Five Heads",
                0,
                0,
                "Animal",
                does="Always on: five more heads, six in all, each able to talk "
                "and bite. Lost or hurt heads do not grow back. Bought as three "
                "Personal Powers and Improved Powers.",
            ),
            b.power(
                "Assuming the Horse-chestnut",
                4,
                -6,
                "Animal",
                does="Becomes a horse-chestnut tree, upright if he rears onto "
                "his hind legs first, or a fallen trunk if he lies down.",
            ),
            b.power(
                "The Field Made Fallow",
                4,
                -6,
                "Herbam",
                does="A touch of his claw withers a field: as many as ten "
                "thousand plants at once.",
            ),
            b.power(
                "The Captive Encased in Bark",
                3,
                -7,
                "Corpus",
                does="His breath, from nostrils almost touching the victim, "
                "turns a person into a smaller horse-chestnut.",
            ),
            b.power(
                "Inquiry of the Leafy Sentinel",
                3,
                -5,
                "Herbam",
                does="Lets him talk with trees and bushes.",
            ),
        ],
        vis=[BodyVis(5, "Animal", "in the five largest scales along his back")],
        appearance=(
            "Long, lean and low: forty feet from snout to tail but only six "
            "feet at the shoulder, his green scales looking mouldy though "
            "that is just their colour. His six heads weave and flick like "
            "tasting tongues, and fall still only when he stalks."
        ),
        notes=(
            "A young zmaj, a Magic dragon, blind from birth, who finds his way "
            "by smell and hearing and knows the scent of every plant in the "
            "Tribunal. His lair is in a dense stand of horse-chestnuts by the "
            "Drina in western Serbia. He hunts deer along his borders and "
            "drives off farmers: grain sown too near his home is destroyed, "
            "and a farmer he meets loses his crop and becomes a tree. Rude "
            "but not violent, and, like most zmajevi, in search of a wife. "
            "He may bite many times a round, but a Size 0 foe only twice, "
            "plus once more for each point of Size above 0. "
            + wound_ranges(4)
            + "\nThe zmajevi want what the aždaje want, wives and gold, but "
            "do harm without noticing or caring. Some walk on their hind "
            "legs with small clawed hands. Their lairs are lavish, and their "
            "pecking order is one of remembered favours and insults, much "
            "like a noble court."
        ),
    )


# -- chapter 8: giants and faerie horses --


def _giants(transylvania: Transylvania) -> None:
    b = transylvania.b
    _MADE["giant_brothers"] = b.creature(
        "Georghe and Ladislau",
        page="p. 112",
        realm="Faerie",
        might=15,
        form="Corpus",
        size=4,
        how_many="two giant brothers, who share these statistics",
        block={
            "characteristics": characteristics(-2, -1, 0, -2, 11, 3, 2, -5),
            "virtues_flaws": [
                "Negative Reaction",
                ("Focus Power", {"focus": "Shrinking"}),
                *["Huge"] * 3,
                "Humanoid Faerie",
                "Incognizant",
                vf_ward("places"),
            ],
            "abilities": [
                ("Area Lore: (their district)", 2, "hidden pastures"),
                ("Animal Handling", 2, "draft horses"),
                ("Ride", 2, "charging"),
                ("Single Weapon", 6, "long sword"),
                ("Living Language: (local tongue)", 4, "bragging"),
            ],
            "traits": {"Warlike": 3, "Persistent": 2},
        },
        attacks=[
            b.attack("Long Sword & Heater Shield (on foot)", -3, 13, 6, 17),
            b.attack("Long Sword & Heater Shield (mounted)", -3, 15, 8, 17),
            b.attack("Lance & Heater Shield (mounted)", -3, 14, 4, 16),
        ],
        soak=12,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Shrinking",
                3,
                0,
                "Corpus",
                level=20,
                does="In a moment he shrinks to Size +2 or grows back to +4, "
                "his arms and armour with him. The book prints no Init.",
            ),
        ],
        vis=[BodyVis(3, "Corpus", "one in each ear and one in the nose")],
        equipment="Full chainmail, heater shield, long sword.",
        appearance=(
            "Two plain local knights grown to giant size, their armour "
            "undecorated but kept in good order."
        ),
        notes=(
            "Brothers with farms side by side, next to their mother's, each "
            "forever edging the shared fence onto the other's land; when one "
            "notices, they fight, and being equally strong they can go at it "
            "for hours. Their quarrels spill onto the road that runs past "
            "the farms, and after a few blows one of them will ask a passing "
            "traveller to judge between them, or to take up arms against the "
            "other. Their scores are Pretenses, as for any faerie. Wound "
            "ranges at Size +2: Light 1-7 to Dead from 29; at Size +4: "
            "Light 1-9 to Dead from 37.\n"
            "Transylvanian giants (also called ogres) are no fools: they "
            "bear arms like knights, keep homesteads and horses, and can be "
            "witty. Many change Size between +2 and +5, shrinking to ride "
            "and growing just before a fight, and many can take other "
            "shapes (a pear tree, a brook, a poisonous flower), in which "
            "they can still be hurt. Each has a sorceress mother, and giant "
            "blood shows as hair growing inside the mouth."
        ),
    )
    _MADE["costache"] = b.creature(
        "Costache",
        page="p. 113",
        realm="Faerie",
        might=20,
        form="Mentem",
        size=3,
        block={
            "characteristics": characteristics(2, 2, -3, -3, 7, 3, 3, -6),
            "virtues_flaws": [
                "Negative Reaction",
                "Greater Power",
                "Greater Power",
                "Huge",
                "Huge",
                "Humanoid Faerie",
                "Incognizant",
                vf_ward("iron"),
            ],
            "abilities": [
                ("Athletics", 3, "running"),
                ("Awareness", 2, "listening"),
                ("Brawl", 4, "fist"),
                ("Charm", 1, "princesses"),
                ("Folk Ken", 3, "guests"),
                ("Guile", 4, "inventing stories"),
                ("Legerdemain", 4, "snatching small objects"),
                ("Living Language: (local tongue)", 5, "telling lies"),
                ("Stealth", 4, "sneaking through castles"),
                ("Survival", 1, "forests"),
            ],
            "traits": {"Deceitful": 3, "Sly": 2},
        },
        attacks=[b.attack("Fist", -6, 8, -1, 7)],
        soak=3,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Rousing the Castle's Curiosity",
                4,
                -10,
                "Mentem",
                does="Everyone in the building is gripped by curiosity and "
                "goes poking into every passage, room and locked door.",
            ),
            b.power(
                "Flee like a Bird",
                3,
                -9,
                "Auram",
                does="As Wings of the Soaring Wind: once let out, he flies off "
                "through a window.",
            ),
            b.power(
                "The Shock of Consequence",
                4,
                -10,
                "Corpus",
                does="Freezes up to ten people where they stand; he uses it "
                "on his rescuers the moment he is free, scolds them and "
                "makes off with something valuable.",
            ),
        ],
        vis=[BodyVis(4, "Mentem", "in his tongue")],
        appearance=(
            "A big captive prince or lord in ragged robes, unkempt and filthy, "
            "his eyes glittering with spite; moments after his release his "
            "clothes are new again and he is clean and well groomed."
        ),
        notes=(
            "The giant locked in the forbidden room of a king's palace, held "
            "in a barrel lined with spikes and bound with three iron chains. "
            "He is easily caught and hard to keep, for his power makes the "
            "household curious, and he feeds on the thrill and dread of "
            "people prying where they have been told not to. Scores are "
            "Pretenses. " + wound_ranges(3)
        ),
    )
    _MADE["nicoleta"] = b.creature(
        "Nicoleta, a Giant's Mother",
        page="p. 112",
        realm="Faerie",
        might=30,
        form="Ignem",
        size=1,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(2, 0, -3, -1, 1, 2, 1, 3),
            "virtues_flaws": [
                "Monstrous Appearance",
                "Greater Power",
                "Faerie Speech",
                "Humanoid Faerie",
                "Large",
                "Lesser Power",
                "Incognizant",
                vf_ward("edelweiss"),
                "Slow Might Recovery",
            ],
            "abilities": [
                ("Animal Handling", 2, "horses"),
                ("Athletics", 4, "running"),
                ("Bargain", 2, "hiring servants"),
                ("Brawl", 8, "fist"),
                ("Folk Ken", 2, "detecting lies"),
                ("Hunt", 4, "tracking"),
                ("Profession: Rancher", 4, "breeding horses"),
            ],
            "traits": {"Vengeful": 3, "Greedy": 2, "Suspicious": 2},
        },
        attacks=[
            b.attack("Brawl", 3, 10, 12, 1),
            b.attack("Brawl (as a wheel)", 3, 10, 12, 6),
            b.attack("Brawl (as a flaming wheel)", 3, 10, 12, 26),
        ],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Assume the Shape of the Spinning Wheel",
                4,
                -2,
                "Corpus",
                does="Turns her into a great stony cartwheel that runs her "
                "foes down, adding +5 to her Brawl damage.",
            ),
            b.power(
                "A Mother's Fury",
                1,
                2,
                "Ignem",
                does="Wraps her in flames that do +20 damage to whoever she "
                "touches, if they penetrate.",
            ),
        ],
        vis=[BodyVis(6, "Ignem", "in her two tusks")],
        appearance=(
            "Tall, lean and dirty, with wiry hair, warts and boils, and a "
            "great boar's tusk jutting from each side of her mouth; she wears "
            "a grimy patterned dress under a stained apron."
        ),
        notes=(
            "A shadowy figure deep in the woods whom the locals know of and "
            "keep away from. She spurs her son to do his neighbours every harm "
            "he can, and people put up with him because killing him would "
            "bring her fury down on them. She breeds horses on a farm hidden "
            "in a valley of the Madara Plateau (the book's reference to "
            "chapter 3 means Bulgaria's chapter 4), and among them is a "
            "faerie horse she keeps dirty and half-starved so no one sees "
            "what it is. Stories have someone trying to win that horse from "
            "her with impossible chores. Roused, she becomes the burning "
            "wheel and tries to crush her enemies. Scores are Pretenses. "
            + wound_ranges(1)
            + "\nA giant's mother is always a sorceress, cleverer than her "
            "son: she picks the home, runs the household and the herd, "
            "steers his choices and hunts down whoever beats him; without a "
            "son she pines or rages until she adopts another. No two are "
            "alike: others breathe fire, shake the earth, turn into poison "
            "clouds or throw mountains, and not all are giant-sized."
        ),
    )
    _MADE["fet_frumos"] = b.creature(
        "Fet-Frumos, a Faerie Horse",
        page="p. 113",
        realm="Faerie",
        might=10,
        form="Auram",
        size=2,
        block={
            "characteristics": characteristics(3, 1, 2, 2, 4, 2, 1, -2),
            "virtues_flaws": [
                "Positive Folktales",
                "Highly Cognizant",
                "Huge",
                vf_great("Strength"),
                "Improved Characteristics",
                "Improved Characteristics",
                "Faerie Speech",
                ("Focus Power", {"focus": "Flight"}),
            ],
            "abilities": [
                ("Athletics", 6, "flying"),
                ("Brawl", 5, "kick"),
                ("Faerie Lore", 4, "giant kin"),
                ("Area Lore: (his district)", 4, "faerie homes"),
            ],
            "traits": {"Patient": 3, "Wise": 2, "Compassionate to Humans": 1},
        },
        attacks=[b.attack("Kick", 0, 9, 4, 5)],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Flight",
                2,
                0,
                "Auram",
                does="Always on: he can fly (Realms of Power: Faerie).",
            ),
        ],
        vis=[BodyVis(2, "Auram", "one in each front hoof")],
        equipment="Fitting tack and harness.",
        appearance=(
            "Held captive, a worn-out, filthy old nag, sway-backed and "
            "bow-legged; once freed and serving his hero, a young, healthy "
            "horse whose coat gleams. Smaller than a warhorse, he still "
            "carries an armoured knight with ease."
        ),
        notes=(
            "A faerie horse's tale: languish dirty and hungry on a giant's "
            "mother's ranch (or as a giant's mount) until a hero finds him, "
            "then carry and counsel the hero, and leave just before the "
            "final victory so the hero wins it alone. More aware of his part "
            "than most faeries, he can foresee how other faeries will play "
            "theirs (that a thwarted giant's mother will storm the maiden's "
            "castle, say), which mortals take for prophecy; he knows nothing "
            "of what other realms will do. Scores are Pretenses. " + wound_ranges(2)
        ),
    )


# -- chapter 8: vampires --

_VAMPIRES = (
    "\nA Transylvanian vampire is a faerie, not the dead man's spirit: it "
    "takes the shape of someone recently dead and feeds on blood and on "
    "the fear it stirs. Each is unique, with its own one to three "
    "precautions that stop it forming, one to three limits it must obey "
    "and one rite that ends it for good (lists in chapter 8 and in the "
    "vampire hunters of chapter 9); killed any other way it forms again "
    "after days or weeks, and while the community's wound is unhealed "
    "another faerie takes its place. Every vampire has Feast of the "
    "Dead, a Traditional Ward of sunlight and the Lesser Power Sap the "
    "Life (PeCo 15: a disease starting at a Light Wound that also takes "
    "two Fatigue levels)."
)


def _vampires(transylvania: Transylvania) -> None:
    b = transylvania.b

    def sap(cost: int, init: int, *, level: int = 15, wound: str = "Light") -> Any:
        return b.power(
            "Sap the Life",
            cost,
            init,
            "Corpus",
            level=level,
            does=f"A touch that saps the victim's vitality: a disease beginning "
            f"with a {wound} Wound and two Fatigue levels lost until it "
            f"passes. Each week a Recovery roll of 12 holds steady and 18 "
            f"improves; Faerie Lore or Medicine can treat it.",
        )

    _MADE["vampire_human"] = b.creature(
        "Human-like Vampire",
        page="p. 118",
        realm="Faerie",
        might=15,
        form="Corpus",
        how_many="a template: the commonest vampire of the Tribunal",
        block={
            "characteristics": characteristics(-2, 0, -3, 0, 3, 2, 1, 3),
            "virtues_flaws": [
                "Negative Reaction",
                "Feast of the Dead",
                "Humanoid Faerie",
                "Increased Faerie Might",
                "Increased Faerie Might",
                _power("Sap the Life"),
                "Incognizant",
                vf_ward("sunlight"),
            ],
            "abilities": [
                ("Area Lore: (its village)", 3, "livestock"),
                ("Athletics", 5, "climbing"),
                ("Brawl", 5, "teeth"),
                ("Charm", 3, "bereaved family"),
                ("Living Language: (local dialect)", 5, ""),
                ("Stealth", 5, "village streets"),
            ],
            "traits": {"Hungry": 3},
        },
        attacks=[b.attack("Teeth", 3, 8, 10, 4)],
        soak=2,
        powers=[sap(2, 1)],
        vis=[BodyVis(2, "Corpus", "in grave dirt")],
        appearance=(
            "A fresh corpse, often with red eyes and red nails, in a burial "
            "shroud or nothing at all."
        ),
        notes=(
            "Called platenik or ubour by Bulgarians, drakus by the Thracians "
            "of the Rhodopes, moroi by the Vlachs, oiocoi by the "
            "Transylvanians, lampir in Bosnia and upir among the Ruthenians. "
            "The kukudhi are the old ones that have lost their fear of "
            "daylight (though direct sun still hurts them) and live among "
            "people. 5 points of Virtues and 3 of Flaws; a template to "
            "tailor. "
            + wound_ranges(0)
            + _VAMPIRES
            + "\nThe life cycle: an unseen haunting of the family (zduhacz) "
            "for seven or forty days, then a shapeless gadja for forty days, "
            "then the dead one's own shape (platenik), preying first on its "
            "kin; after seven years it moves far away as a kukudhi, takes a "
            "trade and a family, and its children are dhampirs. Vampires "
            "are busiest from St Andrew's Eve to St George's Eve."
        ),
    )
    _MADE["vampire_bestial"] = b.creature(
        "Bestial Vampire",
        page="p. 118",
        realm="Faerie",
        might=20,
        form="Animal",
        how_many="a template: the vukodlaci, wolf-shaped vampires",
        block={
            "characteristics": characteristics(-3, 2, -3, -1, 3, 3, 2, 1),
            "virtues_flaws": [
                "Increased Faerie Might (Major)",
                "Feast of the Dead",
                "Hybrid Form",
                _power("Contort the Boneless Body and Sap the Life"),
                ("Personal Power", {"power": "Transform into Animal"}),
                "Tough",
                "Monstrous Appearance",
                "Incognizant",
                vf_ward("sunlight"),
            ],
            "abilities": [
                ("Area Lore: (its district)", 3, "livestock"),
                ("Athletics", 5, "running"),
                ("Awareness", 3, "movement"),
                ("Brawl", 5, "claws"),
                ("Hunt", 5, "human prey"),
                ("Stealth", 5, "woods"),
            ],
            "traits": {"Hungry": 6},
        },
        attacks=[b.attack("Claws", 1, 13, 10, 7)],
        soak=9,
        powers=[
            b.power(
                "Contort the Boneless Body",
                2,
                -1,
                "Animal",
                level=10,
                does="Squeezes its boneless body through the smallest crack, "
                "or hides where nothing so big could fit.",
            ),
            b.power(
                "Transform into Animal",
                1,
                -1,
                "Animal",
                level=20,
                does="Takes the shape of a wolf for the day (a Personal Power).",
            ),
            sap(3, -2),
        ],
        vis=[BodyVis(2, "Animal", "in its eyes")],
        appearance=(
            "A nightmare cross of wolf and man on two legs, grey-furred, with "
            "a great wolf's claws and muzzle and wide, mad, human eyes."
        ),
        notes=(
            "Vukodlaci to the Slavs (a word also used of living werewolves), "
            "farkaskoldus to the Hungarians, blautsauger to the Saxons and "
            "pricolici to the Vlachs; a few look like bears or dragons "
            "instead. For all their strength they have no bones. Dying by a "
            "wolf, eating from a wolf's kill or a violent crime such as "
            "murder draws them, and every varcolac becomes one when he dies. "
            "8 points of Virtues and 5 of Flaws; the single Lesser Power "
            "covers both its lesser powers. " + wound_ranges(0) + _VAMPIRES
        ),
    )
    _MADE["vampire_incorporeal"] = b.creature(
        "Incorporeal Vampire",
        page="p. 119",
        realm="Faerie",
        might=5,
        form="Ignem",
        how_many="a template: the ghostly zduhacz, luderc and their kin",
        block={
            "characteristics": characteristics(1, 0, 2, 0, 0, 0, 0, 2),
            "virtues_flaws": [
                "Feast of the Dead",
                ("Focus Power", {"focus": "Ghost Touch"}),
                _power("Eidolon"),
                _power("Vampiric Touch (Sap the Life)"),
                "Second Sight",
                "Intangible Flesh",
                "Freshly Sprung",
                "Incognizant",
                "Negative Reaction",
                vf_ward("sunlight"),
            ],
            "abilities": [
                ("Area Lore: (its village)", 3, "village"),
                ("Awareness", 2, "family"),
                ("Brawl", 3, "dodging"),
                ("Charm", 5, "bereaved family"),
                ("Living Language: (local dialect)", 5, ""),
                ("Second Sight", 3, "spirits"),
                ("Stealth", 3, "livestock"),
                ("Thrown Weapon", 3, "knives"),
            ],
            "traits": {"Malicious": 3},
        },
        attacks=[
            b.attack("Dodge", 2, None, 7, None),
            b.attack("Thrown Knife", 2, 5, 6, 7),
        ],
        soak=0,
        powers=[
            b.power(
                "Eidolon",
                2,
                -2,
                "Imaginem",
                level=20,
                does="An image it can see and hear through and steer as it "
                "likes, usually the dead one's likeness, kept until it has no "
                "more use for it.",
            ),
            sap(2, -1),
            b.power(
                "Ghost Touch",
                1,
                -3,
                "Terram",
                level=25,
                does="Its Focus Power: moves loose objects, 5 pounds for 1 "
                "point and double for each point more; thrown, an object "
                "does +5 damage a point, and every physical attack must "
                "penetrate. The cost varies with the weight.",
            ),
        ],
        vis=[BodyVis(1, "Ignem", "in the object its Ghost Touch is moving")],
        appearance=(
            "Unseen, or a glowing speck of light, or the dead one's face and "
            "form made by its Eidolon."
        ),
        notes=(
            "Haunts the dead one's family, smashing pots and making a "
            "nuisance of itself, visits people in dreams and may father "
            "children on a widow; it shows as points of light or burning "
            "shafts. Being bodiless it need not really dodge. The Hungarians "
            "call it luderc; the nekrstenik or ustrel comes for an "
            "unbaptised child's death and threatens newborns and young "
            "mothers, the sjanka rises from the blood of a man knifed to "
            "death, and the ljugat is a gentler kind that feeds only "
            "briefly. 7 points of Virtues and Flaws. " + wound_ranges(0) + _VAMPIRES
        ),
    )
    _MADE["gadja"] = b.creature(
        "Gadja",
        page="p. 119",
        realm="Faerie",
        might=10,
        form="Corpus",
        how_many="a template: the formless stage of a young vampire",
        block={
            "characteristics": characteristics(0, 2, -3, 0, 3, 3, -2, 0),
            "virtues_flaws": [
                "Feast of the Dead",
                "Hybrid Form",
                "Increased Faerie Might",
                "Lesser Power",
                "Monstrous Appearance",
                "Clumsy",
                "Incognizant",
                vf_ward("sunlight"),
                vf_ward("thorns"),
            ],
            "abilities": [
                ("Area Lore: (its district)", 3, "livestock"),
                ("Awareness", 5, "livestock"),
                ("Brawl", 5, "bite"),
                ("Concentration", 3, "while feeding"),
                ("Hunt", 5, "wounded animals"),
                ("Stealth", 5, "fields"),
            ],
            "traits": {"Hungry": 3},
        },
        attacks=[b.attack("Bite", 0, 7, 7, 4)],
        soak=3,
        powers=[
            b.power(
                "Calm the Sheep of the Field",
                2,
                -2,
                "Animal",
                level=10,
                does="Keeps a beast from running away as it rolls up to feed.",
            ),
            sap(3, -3),
        ],
        vis=[BodyVis(2, "Corpus", "in the jelly of blood inside it")],
        appearance=(
            "A limp bag of skin about a pace across, with little beady eyes "
            "and a sharp snout."
        ),
        notes=(
            "The second stage of a human-shaped vampire's life: a swollen "
            "sack of hide and hair full of blood like jelly, rolling from "
            "place to place, sometimes likened to an ox's head, that sucks "
            "blood mostly from animals through its snout. Thorns and "
            "piercing weapons do it fearful harm. 4 points of Virtues and 7 "
            "of Flaws. Its Init values are the book's Qik-based ones worked "
            "out. " + wound_ranges(0) + _VAMPIRES
        ),
    )
    _MADE["vampire_snake"] = b.creature(
        "Vampire Snake",
        page="p. 119",
        realm="Faerie",
        might=5,
        form="Animal",
        size=-3,
        cunning=True,
        how_many="a template: a venomous snake turned vampire",
        block={
            "characteristics": characteristics(-1, -2, -5, -6, -6, 0, 2, 2),
            "virtues_flaws": [
                "Faerie Beast",
                "Feast of the Dead",
                "Lightning Reflexes",
                "Incognizant",
                "Negative Reaction",
                vf_ward("sunlight"),
            ],
            "abilities": [
                ("Awareness", 2, "prey"),
                ("Brawl", 4, "fangs"),
                ("Hunt", 4, "rodents"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 3, "grassy areas"),
            ],
            "traits": {"Hostile": 2},
        },
        attacks=[b.attack("Fangs", 2, 10, 8, -5)],
        soak=0,
        powers=[sap(3, -1, level=20, wound="Medium")],
        vis=[BodyVis(1, "Animal", "in its tongue")],
        appearance=(
            "An unusually big red-eyed snake, a good two paces long and "
            "thick as a man's thigh."
        ),
        notes=(
            "Venomous snakes are the likeliest animals to turn vampire; "
            "stallions, lambs and others may too, but never dogs or wolves. "
            "+6 more Defense against grapples. 3 points of Virtues and 3 of "
            "Flaws. Wound ranges: Light 1-2, Medium to 4, Heavy to 6, "
            "Incapacitated to 8, Dead from 9." + _VAMPIRES
        ),
    )
    _MADE["vampire_tree"] = b.creature(
        "Vampire Tree",
        page="p. 120",
        realm="Faerie",
        might=10,
        form="Herbam",
        size=5,
        cunning=True,
        how_many="a template: a tree turned vampire, most often a hanging tree",
        block={
            "characteristics": characteristics(-3, -1, 1, -3, 10, 5, 0, -5),
            "virtues_flaws": [
                *["Huge"] * 4,
                "Feast of the Dead",
                "Lesser Power",
                "Passes for Human",
                "Freshly Sprung",
                "Freshly Sprung",
                "Incognizant",
                "Limited Movement",
                vf_ward("fire"),
            ],
            "abilities": [
                ("Area Lore: (its fields)", 3, "fields"),
                ("Awareness", 3, "victims"),
                ("Brawl", 4, "branch"),
                ("Living Language: (local dialect)", 5, ""),
                ("Leadership", 3, "menacing"),
                ("Stealth", 3, "pretending to be a normal tree"),
                ("Survival", 2, "harsh winters"),
            ],
            "traits": {"Hostile": 2},
        },
        attacks=[
            b.attack("Branch", 5, 9, 2, 12),
            b.attack("Grapple", 5, 8, 1, None),
        ],
        soak=15,
        powers=[sap(1, -8)],
        vis=[BodyVis(2, "Herbam", "in its bark")],
        appearance=(
            "A white willow some twenty feet high with every branch pointing "
            "skyward until they whip down after blood; its silvery-green "
            "leaves are flecked with blood and bones lie among its roots."
        ),
        notes=(
            "A plant that killed a man, or grew from ground soaked with his "
            "blood, may turn vampire, even a gourd or melon kept too long; "
            "trees are the worst, above all one a suicide hanged himself "
            "from. Thorn trees never do, so they serve as gallows. It "
            "understands speech but cannot talk. It fights like a trained "
            "group with up to four limbs, always adding its +9 group bonus "
            "to Attack, grapples one victim at a time and adds +5 Grapple "
            "Strength for each further branch holding on (ArM5 p. 174). Its "
            "Passes for Human stands for the book's Passes for Plant, and "
            "Limited Movement is from Realms of Power: Magic. Sap the "
            "Life's Init is Qik-3 worked out. Not for a player. "
            + wound_ranges(5)
            + _VAMPIRES
        ),
    )
    _MADE["broukolak"] = b.creature(
        "Broukolak",
        page="p. 121",
        realm="Infernal",
        might=20,
        form="Corpus",
        confidence=(1, 3),
        how_many="a kind: the demons that wear corpses in Bulgaria",
        order="Vessels of Iniquity",
        weakness="Protected Group (those born on a Saturday)",
        block={
            "characteristics": characteristics(0, 0, 0, 0, 4, 4, 0, 2),
            "virtues_flaws": [
                "Shapeshifter",
                "Improved Characteristics",
                "Lightning Reflexes",
            ],
            "abilities": [
                ("Athletics", 10, "leaping"),
                ("Brawl", 5, "grapple"),
                ("Folk Ken", 3, "passing for human"),
                ("Shapeshifter", 3, "at night"),
                ("Thrown Weapon", 5, "spittle"),
            ],
            "traits": {"Hateful": 6, "Depraved": 6},
        },
        attacks=[
            b.attack("Grapple", 2, 6, 7, 4),
            b.attack("Teeth", 2, 10, 8, 7),
            b.attack("Spittle", 2, 6, 0, 10),
        ],
        soak=14,
        fatigue_levels=FATIGUE,
        powers=[
            b.power(
                "Form of Wickedness",
                2,
                0,
                "Mentem",
                does="Reveals its true horror (Realms of Power: The Infernal).",
            ),
            b.power(
                "Form of Man",
                0,
                0,
                "Corpus",
                does="Wears the dead man's face (Realms of Power: The Infernal).",
            ),
            b.power(
                "Contagious Obsession",
                1,
                0,
                "Mentem",
                does="A point for each victim (Realms of Power: The Infernal).",
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points: the Obsession Trait Fear.",
            ),
            b.power(
                "Burning Spittle",
                0,
                2,
                "Ignem",
                does="Spits liquid fire as far as five paces: +10 damage if it "
                "penetrates, and whatever parries it is eaten away and ruined.",
            ),
        ],
        vis=[BodyVis(4, "Corpus", "in its teeth (the book gives no Art)")],
        appearance=(
            "Like anyone else until it uses its powers; then a hunchback with "
            "glossy black skin, black hands and long nails, a peeling "
            "blood-red face, a cat's or wolf's teeth and wild hair and "
            "beard. As a shapeshifter it is mostly a cat, a goat or an owl."
        ),
        notes=(
            "The Bulgarian name for the demon the Greeks call vrykolakas (The "
            "Sundered Eagle has it too): it devours a corpse and wears its "
            "shape. What draws a faerie vampire can draw it, but a curse at "
            "the moment of death is surest, and some wicked people curse "
            "themselves as they die. It sets up in trade in a village where "
            "no one knows it, eats and drinks first from the dead man's "
            "relatives, then further off, and the district's health "
            "declines as it feeds by night on beasts and people. It likes "
            "lone victims, grapples and bites, and may keep one alive for "
            "nightly feeding with scuffle damage. Its Spittle has no "
            "Defense. " + wound_ranges(0)
        ),
    )


# -- chapter 8: vilas --


def _vila(transylvania: Transylvania) -> None:
    b = transylvania.b
    _MADE["vila"] = b.creature(
        "Minor Vila",
        page="p. 122",
        realm="Faerie",
        might=5,
        form="Corpus",
        how_many="a template: the white ladies, cast to suit each role",
        block={
            "characteristics": characteristics(0, 0, 3, 0, 1, 0, 0, 0),
            "virtues_flaws": [
                "Passes for Human",
                "Faerie Sight",
                "Humanoid Faerie",
                "Incognizant",
                vf_ward("offerings: food, cakes or ribbons"),
            ],
            "abilities": [
                ("Athletics", 3, "dance"),
                ("Awareness", 3, "mortals"),
                ("Brawl", 3, "claws"),
                ("Carouse", 3, "getting mortals to drink"),
                ("Charm", 6, "preferred type of mortal"),
                ("Folk Ken", 3, "festivals"),
                ("Music", 5, "singing"),
            ],
        },
        attacks=[b.attack("Claws", -1, 6, 7, 3)],
        soak=0,
        vis=[BodyVis(1, "Corpus", "in a long fair hair")],
        appearance="A lovely young woman, naked or dressed in white.",
        notes=(
            "A weak vila fit for stories with grogs, or as a player "
            "character; she needs powers and more Might to be much use, and "
            "any Virtue added must be balanced by a Flaw (antagonists need "
            "not balance). The book's Human Form is the catalog's Humanoid "
            "Faerie. Her Might Form is usually Corpus. "
            + wound_ranges(0)
            + "\nPowers by role (all Greater unless marked; in a hurry, "
            "double the Might cost and quadruple the Init penalty): "
            "shapeshifting into a falcon, horse, serpent, swan or wolf (2 to "
            "4 points); the Enthralling Voice set (Allure 1, Enthralling "
            "Sound 3, Enthrallment 4, Guide 3, Kiss of Forgetfulness 4, "
            "Steal Judgment 2); the Blessing Dance (Grant a Major Virtue 10, "
            "a Minor Virtue 5, Puissance 2); the Cursing Dance (a cursed "
            "dancing ring made as a trinket, 10 or 15); Spirit Away. Roles: "
            "the captured wife whose skin or feathers are hidden; the cloud "
            "or storm maiden (Flight, a Storms Focus Power up to level 25, "
            "Guide to lead travellers astray); the cursed lover whose "
            "admirers pine away or die in a set kind of accident; the "
            "huntress (Bow 5, Ride 5, a bow at Attack +9, Damage +7, "
            "Shake the Earth 3), who kills oath-breakers; the "
            "temptress (Allure, Illusory Home 4, Pine Away 3); the water "
            "maiden (Illusory Home, Kiss of the Mermaid 3 for breathing "
            "water); the weaver witch, whose loom seems to spin out foot "
            "and horse soldiers; the woodland maiden (Extend Glamour, Guide, "
            "a Manifestation Focus Power over beasts and plants, and powers "
            "turning victims into beasts (3) or things (5)); and the wise "
            "woman (a Healing Focus Power, and a show of prophecy).\n"
            "Wards: many vilas have a Sovereign Ward against a strand of "
            "their own hair, which forces them back into their basic shape "
            "and stops them harming its holder. The hair is often a Minor "
            "External Vis source, so she cannot truly die while it lasts; "
            "a strong vila may have Residual Power, which carries the hair "
            "away when she falls. Food, cakes and ribbons left at the edges "
            "of woods, roads, rivers and wells ward a house or a village. "
            "Giants have vila daughters; vilas bear humans, vilas or "
            "witches; witches bear witches, giants or dragons."
        ),
    )


# -- stat blocks elsewhere in the book --


def _elsewhere(transylvania: Transylvania) -> None:
    b = transylvania.b
    _MADE["silexa"] = b.creature(
        "Silexa",
        page="p. 32",
        realm="Magic",
        might=10,
        form="Animal",
        size=-1,
        season="Summer",
        confidence=(1, 3),
        block={
            "characteristics": _SILEXA_CHARS,
            "virtues_flaws": _SILEXA_VIRTUES,
            "abilities": _SILEXA_ABILITIES,
            "traits": {"Brave": 3, "Loyal (Monica)": 3, "Wolf": 3, "Cautious": 2},
            "reputations": {"Honorable (Hermetic wolves)": 4},
        },
        attacks=[b.attack("Teeth", 5, 11, 13, 6)],
        soak=11,
        fatigue_levels="OK, 0 (x2), -1 (x3), -3 (x2), -5, Unconscious",
        powers=[
            b.power(
                "Hands of the Magical Animal",
                0,
                0,
                "Animal",
                level=15,
                does="Carries things as though she had hands, with Strength 5; "
                "doing anything but carrying needs concentration (a Personal "
                "Power).",
            ),
        ],
        vis=[BodyVis(2, "Animal", "in her heart")],
        appearance="A wolf with a coat the colour of flint.",
        notes=(
            "Monica Ierne's familiar (Monica's sheet has the bond). An Irish "
            "wolf rather than one of the native white wolves, she is a senior "
            "member of the odd society of wolves that lives off House "
            "Tremere. She cannot speak. Wolf is an Essential Trait: it keeps "
            "her loyal to her pack, out of reach of Hermetic magic, and "
            "proof against spells that would make her behave like a person. "
            "The book's list also names Magical Creature, left out here "
            "because it adds nothing to Magic Animal. Wound ranges: Light "
            "1-4, Medium to 8, Heavy to 12, Incapacitated to 16.\n"
            "Cords: Gold +2, Silver +1, Bronze +3. Bond powers: shared sight "
            "(ArM5 p. 105), the complex form of mental speech, and "
            "Ever-present Familiar, which calls her to Monica's side from up "
            "to seven leagues off, 24 times a day; she often fetches Arcane "
            "Connections to places for Monica's Leap of Homecoming."
        ),
    )
    _MADE["zuban"] = b.creature(
        "Zuban, a Four-Eyed Dog",
        page="p. 131",
        realm="Magic",
        might=5,
        form="Animal",
        size=-2,
        season="Spring",
        cunning=True,
        block={
            "characteristics": characteristics(0, 2, -2, 1, -4, 2, 0, 4),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Friend",
                ("Ferocity", {"audience": "against vampires"}),
                "Long-Winded",
                "Sharp Ears",
                "Clumsy",
                "Reckless",
                "Domesticated",
                "Keen Sense of Smell",
                "Pack/Herd Leader",
                "Tireless",
                "Improved Abilities",
                "Improved Powers",
                _power("Dispel the Dark"),
                ("Minor Virtue", {"virtue": "Second Sight"}),
                ("Minor Flaw", {"flaw": "Slow Power"}),
            ],
            "abilities": [
                ("Athletics", 2, "distance running"),
                ("Awareness", 3, "keeping watch"),
                ("Brawl", 3, "bite"),
                ("Hunt", 3, "track by scent"),
                ("Leadership", 3, "dogs"),
                ("Penetration", 3, "Dispel the Dark"),
                ("Second Sight", 2, "vampires"),
            ],
            "traits": {"Loyal": 3, "Reckless": 3, "Brave": 2},
        },
        attacks=[b.attack("Bite", 4, 7, 9, -3)],
        soak=3,
        fatigue_levels="OK, 0/0, -1/-1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Dispel the Dark",
                1,
                1,
                "Vim",
                level=10,
                does="A faerie that hears his bark loses 5 Might if it "
                "penetrates; his Slow Power means he must bark for two rounds "
                "first.",
            ),
        ],
        vis=[BodyVis(1, "Intellego", "in his eyes")],
        appearance=(
            "A middling dog with his tail held high, tawny with white chest "
            "and paws, a black muzzle and two black spots over his eyes. He "
            "keeps walking into things, as if his eyes were on something "
            "nobody else can see."
        ),
        notes=(
            "A sabotnik dog: anyone born on a Saturday is safe from the "
            "direct powers of vampires that cannot harm the Saturday-born, "
            "and such dogs are known by the black marks over their eyes. "
            "Ferocity 1 (3). He makes a magical animal companion, or a grog "
            "if his Cunning becomes Intelligence. Wound ranges: Light 1-3, "
            "Medium to 6, Heavy to 9, Incapacitated to 12, Dead from 13."
        ),
    )
    _MADE["ivan_rilski"] = b.creature(
        "Saint Ivan Rilski",
        page="p. 47",
        realm="Divine",
        might=50,
        powers=[
            b.power(
                "Strike Dumb",
                1,
                8,
                "Corpus",
                does="Leaves the target wholly mute until the saint chooses to "
                "lift it.",
            ),
        ],
        appearance=(
            "Shown with the Holy Cross and a scroll or open book written in "
            "Cyrillic letters."
        ),
        notes=(
            "John of Rila, the patron of Bulgaria: a hermit, healer and "
            "mystic who died in 946 after twelve years in a cave, three in a "
            "hollow oak and seven on a high rock above the cave, where his "
            "followers grew into the monastery of Rila. The cave, the tree "
            "and the rock have a Divine aura of 4, apart from the "
            "monastery's Dominion of 3; his body, still uncorrupted, lies "
            "in Tarnovo. Venerated by the Bulgarians, the people of Sredets "
            "and Tarnovo, monks and hermits; his feast is 19 October. Other "
            "powers (Realms of Power: The Divine): Apparition, Expel Demons, "
            "The Faithful Made Whole and Grant of Serenity.\n"
            "The monks speak for him and carry weight in Bulgarian politics. "
            "Before they help, they may ask petitioners to repeat his "
            "ordeal in miniature, twelve days in the cave, three in the oak "
            "and seven on the rock, while he weighs their purity of purpose; "
            "those who pass may gain the monastery as an ally, and a like "
            "ordeal could initiate a Holy Tradition of the saint."
        ),
    )


_SILEXA_CHARS = characteristics(2, 1, -2, 1, -1, 3, 2, 2)

_SILEXA_VIRTUES: list[Any] = [
    "Magic Animal",
    ("Essential Virtue (Minor)", {"trait": "Wolf"}),
    "Improved Characteristics",
    "Improved Characteristics",
    ("Ferocity", {"audience": "when hungry"}),
    "Long Winded",
    "Sharp Ears",
    "True Friend",
    "Wilderness Sense",
    "Infamous",
    ("Personal Power", {"power": "Hands of the Magical Animal"}),
    "Improved Damage",
    "Improved Damage",
    "Improved Defense",
    "Improved Defense",
    "Improved Fatigue",
    "Improved Fatigue",
    "Improved Initiative",
    "Improved Soak",
    "Improved Soak",
]

_SILEXA_ABILITIES: list[tuple[str, int, str]] = [
    ("Area Lore: Transylvanian Tribunal", 3, ""),
    ("Athletics", 5, "distance running"),
    ("Awareness", 3, "smell"),
    ("Brawl", 5, "teeth"),
    ("Hunt", 4, "track by smell"),
    ("Dead Language: Latin", 5, "listening"),
    ("Leadership", 3, "wolves"),
    ("Survival", 3, "winter"),
    ("Swim", 3, "rivers"),
    ("Wilderness Sense", 5, "Transylvania"),
]


# -- finish: homes, the familiar, and the beings without stats --


def finish(transylvania: Transylvania) -> None:
    """Set each creature at its place, list it among the place's
    creatures, bind Silexa to Monica, and name the beings without stats
    in the places they haunt."""
    b = transylvania.b
    lairs = {
        "danaslepih": lambda region: b.place(
            "Danaslepih's Grove",
            summary=(
                "A thick stand of horse-chestnuts on the Drina in western "
                "Serbia, the lair of the blind zmaj Danaslepih (see the "
                "Bestiary), who withers any crop sown near it."
            ),
            inside=region,
        ),
        "nicoleta": lambda region: b.place(
            "Nicoleta's Horse Farm",
            realm="Faerie",
            summary=(
                "A horse ranch hidden in a remote valley of the Madara "
                "Plateau, home of the giant's mother Nicoleta and of the "
                "faerie horse Fet-Frumos she keeps starved and filthy (see "
                "the Bestiary)."
            ),
            inside=region,
        ),
    }
    for slug, creature in _MADE.items():
        place = _silexa_home(transylvania) if slug == "silexa" else None
        if slug != "silexa":
            keys, words, region = HOMES[slug]
            place = _home(transylvania, keys, words)
            if place is None and slug in lairs:
                place = lairs[slug](transylvania.places.get(region))
                transylvania.places[f"{slug}_lair"] = place
            if place is None:
                place = transylvania.places.get(region)
        if place is None:
            continue
        creature.place_id = place.id
        b.link(place, "creatures", creature, _ROLE.get(slug, ""))
    _familiar(transylvania)
    _without_stats(transylvania)


def _home(
    transylvania: Transylvania, keys: tuple[str, ...], words: tuple[str, ...]
) -> Neighbour | None:
    """The first of `keys` a part made, else a place whose name holds one
    of `words`."""
    for key in keys:
        if key in transylvania.places:
            return transylvania.places[key]
    places = [n for n in transylvania.b.saga.neighbours if n.kind == "place"]
    for word in words:
        found = next((p for p in places if word.casefold() in p.name.casefold()), None)
        if found is not None:
            return found
    return None


def _silexa_home(transylvania: Transylvania) -> Neighbour | None:
    coeris = transylvania.covenants.get("coeris")
    if coeris is not None and coeris.place_id:
        return transylvania.b.saga.neighbour(coeris.place_id)
    return transylvania.places.get("transylvania") or transylvania.places.get("hungary")


def _familiar(transylvania: Transylvania) -> None:
    """Silexa as Monica Ierne's bound familiar, with the book's numbers."""
    monica = transylvania.magi.get("monica")
    silexa = _MADE.get("silexa")
    if monica is None or silexa is None:
        return
    saga = transylvania.b.saga
    if any(f.character_id == monica.id for f in saga.familiars):
        return
    familiar = Familiar(
        id=storage.generate_unique_id("Silexa", [f.id for f in saga.familiars]),
        character_id=monica.id,
        name="Silexa",
        species="Wolf of Irish stock, flint-grey",
        magic_might=10,
        size=-1,
        virtues_flaws=[_virtue_flaw(entry) for entry in _SILEXA_VIRTUES],
        personality_traits=[
            ScoredTrait("Brave", 3),
            ScoredTrait("Loyal (Monica)", 3),
            ScoredTrait("Wolf", 3),
            ScoredTrait("Cautious", 2),
        ],
        reputations=[ScoredTrait("Honorable (Hermetic wolves)", 4)],
        golden_cord=2,
        silver_cord=1,
        bronze_cord=3,
        characteristics=silexa.characteristics,
        base_soak=11,
        natural_weapons=[
            Possession(
                id=storage.generate_unique_id("Teeth", []),
                kind="weapon",
                name="Teeth",
                weapon_init=5,
                weapon_attack=11,
                weapon_defense=13,
                weapon_damage=6,
            )
        ],
        abilities=[
            Ability(
                name=name,
                category=access.ability_category(name),
                xp=ability_xp(score),
                specialty=specialty or None,
            )
            for name, score, specialty in _SILEXA_ABILITIES
        ],
    )
    saga.familiars.append(familiar)
    transylvania.b.link(monica, "creatures", silexa, "her familiar, Silexa")


#: The beings the book names without stats: the place keys a part may
#: have made, words a place's (or oppidum's) name may hold, the region
#: to fall back on, the name the text must not already mention, and the
#: sentence to add.
_NAMED: tuple[tuple[tuple[str, ...], tuple[str, ...], str, str, str], ...] = (
    (
        (),
        (),
        "transylvania",
        "Fetillusclaviceps",
        "Transylvania's dragons have been held in check since the second century by "
        "the Pax Draconis of Fetillusclaviceps, a Roman dragon who beat the "
        "twelve-headed Carpathian zmaj Abur-ciocîrlie in a duel and set "
        "the aždaja Slomljenakrila against the oath-breaking Britvazub; he "
        "has not been seen for fifty years, his lair is unknown, and some "
        "Tremere suspect the later sightings were magi in his likeness, as "
        "the Founder once was (see the Bestiary and the Dragon War).",
    ),
    (
        ("scholomance",),
        ("Scholomance",),
        "transylvania",
        "Aževastjepan",
        "The dragon king of the Carpathians around the Scholomance is Aževastjepan, a "
        "seven-headed zmaj who keeps the Pax Draconis harshly and bars "
        "aždaje from his realm; no magus has met him and even other "
        "dragons don't know his lair, and a few magi have noticed how like "
        "the Scholomance's caretaker's his name sounds.",
    ),
    (
        (),
        (),
        "bulgaria",
        "Rabidanadas",
        "From a mountain eyrie the powerful aždaja Rabidanadas watches the "
        "demon Akgah's success in the Theban Tribunal and dreams of leading "
        "a band of aždaje against the Bulgarian kingdom.",
    ),
    (
        (),
        (),
        "slavs",
        "Veles",
        "The Slavs' dragon god Veles, Perun's eternal foe, sleeps in his "
        "own realm; a revival of Perun's worship could wake him and set "
        "the dragons loyal to him at war.",
    ),
    (
        ("cakoc",),
        ("Cakoc",),
        "hungary",
        "dragon",
        "A green dragon lives in the hills near Cakoc, where Saint George "
        "once killed a maiden-eating black beast: it frightens people and "
        "takes sheep, will speak only to warn a shepherd to hold his dog, "
        "and no one knows if it is Infernal.",
    ),
    (
        ("diocletians_palace", "diocletian"),
        ("Diocletian",),
        "slavs",
        "dragon",
        "Tremere magi sometimes search the ruins of Diocletian's palace for the dragon said to lie "
        "coiled round a heap of Roman gold, probably in a regio; whether it "
        "is Magic or Infernal no one knows.",
    ),
    (
        ("madara", "madara_horseman", "madara_plateau"),
        ("Madara",),
        "bulgaria",
        "lion",
        "The right faerie rite wakes the carved Madara Horseman (Faerie "
        "Might 20 or more), with his horse, hound and eagle, and the lion "
        "under his spear (a separate faerie of equal Might) wakes with "
        "him; he rides against whatever he judges the worst threat to his "
        "people, and neither can be killed for good.",
    ),
    (
        ("starosel",),
        ("Starosel",),
        "bulgaria",
        "spirit",
        "Starosel's genius loci, a magical spirit shaped like a woman of black "
        "soil and red clay with great power over earth and plants, guards "
        "the tomb temple and resists any change; settlers must master or "
        "pacify it for good, though vis gatherers may strike a bargain.",
    ),
    (
        ("valley_of_the_thracian_kings", "thracian_valley", "thracian_kings"),
        ("Thracian Kings", "Thracian Valley"),
        "bulgaria",
        "Kabeiros",
        "In the Valley of the Thracian Kings a faerie calling itself Kabeiros, a tall brass man with a crab's "
        "claw for a left hand, is reviving the Cabeiri cult here, initiating "
        "Quaesitors' servants into Eyes of Theseus and the other cult "
        "Virtues.",
    ),
    (
        ("seven_lakes",),
        ("Seven Lakes",),
        "bulgaria",
        "vila",
        "Each of the Seven Lakes in the Rila mountains is home to a rival vila sister of the water "
        "maiden kind, who offers a bather a faerie gift for a year and a day "
        "in her home under the water but must kill the guest on the last "
        "day; it is said a man who wins all seven gifts becomes their lord.",
    ),
    (
        ("isle_of_achilles", "white_island"),
        ("Achilles", "White Island"),
        "bulgaria",
        "Helen",
        "The spirits of Achilles and Helen and their retinue keep the "
        "Isle of Achilles in the Black Sea: no woman may land, men only by day, and Achilles kills "
        "anyone of Trojan blood; Tremere come to talk war with him and "
        "scholars ask Helen where old cities lie.",
    ),
    (
        ("palace_of_the_giant_king",),
        ("Giant King", "Balbona"),
        "transylvania",
        "Balbona",
        "The Szekler giants' king Balbona called his giants to council with huge "
        "golden bells, buried deep at his death, which still ring on feast "
        "days and make the ground tremble harmlessly.",
    ),
    (
        ("faerie_courts",),
        ("Firtos", "Faerie Court"),
        "transylvania",
        "Firtos",
        "In the Szekler lands the good faeries obey Queen Firtos in her "
        "golden palace and the evil ones Queen Tartos, whose hall is lit by "
        "three head-sized diamonds and heaped with golden bars, lions with "
        "carbuncle eyes, a golden hen with chicks and casks of coin.",
    ),
    (
        ("istria",),
        ("Istria",),
        "slavs",
        "strigon",
        "Istria's own vampire is the strigon, which knocks on doors after "
        "midnight to foretell a death, lies with widows and drinks "
        "children's blood; staking it in the belly at its grave ends it "
        "and leaves the grave full of vis-rich blood, more the older it "
        "was.",
    ),
    (
        ("arena_of_pula", "pula"),
        ("Pula",),
        "slavs",
        "builder",
        "Swarms of small building faeries (Brownies of Realms of Power: "
        "Faerie) raised the Arena of Pula in a single night, left unfinished when a "
        "confused cock crowed early; what they build carries an aura, and "
        "their leaders, or the hidden watchers in the arena's back row on "
        "auspicious nights, can be bargained with.",
    ),
    (
        ("tomb_of_aspyrtus", "aspyrtus_tomb"),
        ("Aspyrtus", "Aspytrus"),
        "slavs",
        "votaress",
        "Aspyrtus's tomb on Cres is said to hold the magical serpents Medea sealed away, "
        "perhaps orms or votaress snakes, clever murderous faerie serpents "
        "sworn not to sleep through winter until they have killed someone.",
    ),
    (
        ("lycaneon",),
        ("Lycaneon",),
        "transylvania",
        "white wolves",
        "Packs of magical white wolves guard the mountains of Lycaneon; Tremere took "
        "their leader as his familiar, and the wolves say they were once "
        "people trapped in wolf shape when the Oracles fell silent, now "
        "and then bearing a cub that turns human three nights each summer.",
    ),
)


def _without_stats(transylvania: Transylvania) -> None:
    """Add each being without stats to the summary of the place it haunts,
    unless that summary already mentions it."""
    for keys, words, region, name, sentence in _NAMED:
        record = _named_home(transylvania, keys, words)
        if record is None:
            # In the region, the place's own name says whether it is there.
            record, name = transylvania.places.get(region), (words or (name,))[0]
        if record is None or name.casefold() in record.summary.casefold():
            continue
        record.summary = _append(record.summary, sentence)


def _named_home(
    transylvania: Transylvania,
    keys: tuple[str, ...],
    words: tuple[str, ...],
) -> Neighbour | Covenant | None:
    """A place for `keys` or `words`, else an oppidum's place or the
    oppidum itself."""
    place = _home(transylvania, keys, words)
    if place is not None:
        return place
    for key in keys:
        covenant = transylvania.covenants.get(key)
        if covenant is not None:
            site = (
                transylvania.b.saga.neighbour(covenant.place_id)
                if covenant.place_id
                else None
            )
            return site or covenant
    return None


def _append(summary: str, sentence: str) -> str:
    """`summary` with `sentence` added to its last paragraph."""
    return f"{summary.rstrip()} {sentence}".strip()
