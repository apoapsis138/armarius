"""The Bestiary: every creature and spirit Guardians of the Forests prints
a stat block for, from the forest spirits that rule whole woodlands to
the boglins of the northern swamps, each at the place it haunts.

The forest spirits' Special Powers are the general ones the book's
chapter on the forests defines (Grant Virtue, Regio, Shroud and the
rest); their costs depend on how the spirit spends its Might Pool, so
they are named in the notes rather than written up as Powers."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis

if TYPE_CHECKING:
    from . import Rhine

FAERIE_NATURE = (
    "Faerie nature: untouched by disease and age, understands "
    "and is understood in any tongue, has Second Sight, and its powers take "
    "the aura's bonus or penalty by the Realm Interaction table."
)


def build(rhine: Rhine) -> None:
    _forest_spirits(rhine)
    _faeries(rhine)
    _magical_beasts(rhine)
    _infernal(rhine)
    _ghosts(rhine)


def _forest_spirits(rhine: Rhine) -> None:
    """The genii loci of the forests and their sacred trees, which the book
    gives a Might, Personality Traits and Special Powers."""
    b, places, world = rhine.b, rhine.places, rhine.world

    b.creature(
        "The Courts of the Seasons",
        page="p. 34",
        realm="Faerie",
        might=40,
        block={
            "traits": {
                "Compassionate (Alder Prince)": 3,
                "Secretive (Alder Prince)": 2,
                "Regal (King Oak)": 3,
                "Generous (King Oak)": 2,
                "Manipulative (Willow Maiden)": 3,
                "Uncaring (Willow Maiden)": 2,
                "Tyrannical (King Holly)": 3,
                "Cold-hearted (King Holly)": 2,
            }
        },
        appearance=(
            "Four faerie rulers, each bound to a fragment of one broken forest "
            "spirit: the shy, red-hued Alder Prince in a misty western vale, "
            "generous but touchy King Oak beneath a great oak in the south, the "
            "scheming Willow Maiden in the east, and iron-willed King Holly in "
            "his northern holly grove."
        ),
        notes=(
            "The book prints Faerie Might 20-50 by the time of year. Each "
            "ruler keeps a Might score of 40 for Magic Resistance and "
            "Penetration all year, but the Might Pool swings: 50 (and an aura "
            "of 3 across the wood) in the month of its own solstice or equinox, "
            "losing 5 a month to the next court down to 20 at the opposite "
            "season, then gaining 5 a month back.\n"
            "Special Powers: Alder Prince: Shroud, Grant Virtue (Rapid "
            "Convalescence). King Oak: Guide, Grant Virtue (Inspirational). "
            "Willow Maiden: Guide, Grant Flaw (Weak-Willed). King Holly: "
            "Shroud, Grant Flaw (Depressed). All four: Control Weather, Regio. "
            "Each ruler should also have faerie powers of the storyguide's "
            "choosing."
        ),
        place=places["seasonal_courts"],
    )

    king_fir = b.creature(
        "The King Fir of the Black Forest",
        page="p. 50",
        realm="Faerie",
        might=60,
        block={"traits": {"Malicious": 5, "Secretive": 3, "Vengeful": 3}},
        appearance=(
            "A great dark fir alone on the bare summit of the Feldberg; the "
            "spirit, the King of the Black Mountain, is said to show itself as "
            "a huge man in a black cloak with a dreadful face."
        ),
        notes=(
            "Faerie Might 60: the book prints 90, which its errata "
            "corrects.\n"
            "Special Powers: Control Weather, Grant Flaw (many, among them "
            "Depressed, Fear, Lame and No Sense of Direction), Grant Victory "
            "(very seldom used), Grant Virtue (unknown, very seldom used), "
            "Possession, Regio, Shroud.\n"
            "The splintered, faerie-twisted wild half of the Black Forest's "
            "first genius loci. Its regio under the Feldberg has several "
            "levels of Faerie aura 3 to 8 and a vast dungeon of enslaved "
            "trespassers; no mortal who sees the fir may leave the forest. It "
            "cannot reach the Glade of the Seven Waterfalls or the Fane of the "
            "Founders, and wants Durenmar destroyed so that the oath binding "
            "its other half lapses."
        ),
        place=places["feldberg"],
    )
    b.link(
        world["king_of_the_black_mountains_attacks"],
        "creatures",
        king_fir,
        "the spirit behind the attacks",
    )
    b.link(world["dark_fae"], "creatures", king_fir, "their dread ruler")

    b.creature(
        "The Glade of the Seven Waterfalls",
        page="p. 51",
        realm="Magic",
        might=80,
        block={"traits": {"Enigmatic": 4, "Wise": 3}},
        appearance=(
            "A stream falling over seven waterfalls down a steep valley of "
            "hazel and beech at the heart of the Black Forest; the spirit of "
            "the glade is peaceful and is spoken of as she."
        ),
        notes=(
            "Special Powers: Grant Virtue (Clear Thinker), Guide, "
            "Oath-Swearing, Regio, Shroud.\n"
            "What remains of the Black Forest's original genius locus, bound "
            "long ago by the Cult of Mercury's oath. Each waterfall is a level "
            "of its regio, and the spirit lets a visitor climb past one only "
            "after a Quest (and perhaps a Sacrifice), each granting deeper "
            "understanding of the Forest. The glade has never been found; some "
            "magi think its spirit has been replaced by a maga in Final "
            "Twilight, perhaps Merinita herself."
        ),
        place=places["glade_of_seven_waterfalls"],
    )

    ash = b.creature(
        "The Ash of Nortorf",
        page="p. 69",
        realm="Infernal",
        might=15,
        block={"traits": {"Ambitious": 2}},
        appearance=("A small ash seedling in the churchyard of Nortorf in Holstein."),
        notes=(
            "Infernal Might 15, with the potential to reach 60 once the ash is "
            "grown.\n"
            "Special Powers: Grant Victory, Grant Virtue (Entrancement), Grant "
            "Virtue (Inspirational), Grant Virtue (Tough).\n"
            "Every New Year's Night a white horseman cuts the shoot down while "
            "a black horseman tries to stop him; if the black rider ever wins, "
            "the tree will grow, a king will tether his horse under it, and he "
            "will be unbeatable in a terrible battle while the horse stays "
            "there. Grown, it would be a rich source of vis."
        ),
        place=places["ash_of_nortorf"],
    )
    b.link(world["ash_of_nortorf"], "creatures", ash, "the spirit of the ash")

    b.creature(
        "The Teutoburger Forest",
        page="p. 77",
        realm="Magic",
        might=50,
        block={"traits": {"Patient": 3, "Unforgiving": 1}},
        appearance=(
            "A ring of ancient trees of different kinds round a great clearing "
            "at the forest's heart, which guard the wood together."
        ),
        notes=(
            "Special Powers: Grant Flaw (Simple-Minded), Grant Victory, Regio, "
            "Shroud, Stasis.\n"
            "In the top level of its regio the Roman legionaries who fled into "
            "the forest after Hermann's victory still hold a fortified camp in "
            "the clearing: the guardians let them neither die nor leave, "
            "though they may hunt beyond the clearing and have come to revere "
            "the trees."
        ),
        place=places["teutoburger_forest"],
    )

    b.creature(
        "The Apple of the Kyffhäuser",
        page="p. 86",
        realm="Magic",
        might=70,
        block={"traits": {"Regal": 4, "Peaceful": -1}},
        appearance=(
            "A withered apple tree at the foot of the Kyffhäuser's tallest "
            "peak, guarded by men-at-arms."
        ),
        notes=(
            "Special Powers: Grant Victory (to whoever hangs a shield on the "
            "tree), Grant Virtue (Unaging, to keep its men-at-arms in their "
            "prime), Heal Wounds, Possession (of any who fail to beat the "
            "men-at-arms).\n"
            "Whoever hangs his shield on it becomes lord of the West; those "
            "who try and fail serve forever among its guards. Clovis, "
            "Charlemagne and Barbarossa succeeded and cut it down, and each "
            "time it grew back and withered with their fortunes. It last bore "
            "fruit under Barbarossa."
        ),
        place=places["apple_of_the_kyffhauser"],
    )

    b.creature(
        "The Donar Oak",
        page="p. 88",
        realm="Divine",
        might=40,
        block={"traits": {"Peaceful": 5, "Wild": -3}},
        appearance=(
            "The stump of the great oak of Geismar, a plain cross set in its "
            "centre, with offshoots growing round it in a hidden glade."
        ),
        notes=(
            "Special Powers: Grant Virtue (various, rarely used), Healing.\n"
            "Once the heart of the Hercynian Forest's pagan power, until St "
            "Boniface felled it into four pieces. Wild beasts grow docile in "
            "the glade; its acorns are Creo vis, tame any animal that eats "
            "one, and tame a forest where one grows to maturity. Some think "
            "the glade a gate to Eden."
        ),
        place=places["donar_oak"],
    )

    linden = b.creature(
        "The Linden of Neustadt",
        page="p. 88",
        realm="Magic",
        might=30,
        block={"traits": {"Protective": 6}},
        appearance=(
            "A great spreading lime tree whose broken boughs are held up by "
            "stone columns carved with the arms of the nobles who once "
            "defended the town."
        ),
        notes=(
            "Special Powers: Grant Victory, Grant Virtue (Berserk), Grant "
            "Virtue (Tough), given to the town's defenders.\n"
            "Alone among the forest spirits it has taken a town's people into "
            "its realm, which weakens it but keeps them sparing of the woods. "
            "It is said the town's freedom ends when the tree dies."
        ),
        place=places["linden_of_neustadt"],
    )
    b.link(world["neustadt_linden"], "creatures", linden, "the town's guardian")

    b.creature(
        "The Drudenbaum of Harberg",
        page="p. 89",
        realm="Magic",
        might=30,
        block={"traits": {"Mysterious": 3}},
        appearance=(
            "A tree of no known kind atop the Harberg above Nuremberg, a great "
            "black bird perched in its crown."
        ),
        notes=(
            "Special Powers: Grant Virtue (Magic Sensitivity), Grant Virtue "
            "(Second Sight), Possession.\n"
            "The spirit possesses any tree of its domain, which then takes on "
            "the Drudenbaum's look and gifts, the black bird settling in its "
            "top. Its golden drops are Creo vis and the milk from its roots "
            "Vim vis, which is why wizards gather beneath it; the guarding "
            "dragon and treasure of the tale are only legend."
        ),
        place=places["drudenbaum"],
    )

    holm_oak = b.creature(
        "The Holm Oak of Romowe",
        page="p. 99",
        realm="Magic",
        might=45,
        block={"traits": {"Domineering": 3, "Cruel": 1}},
        appearance=(
            "A massive evergreen oak in the sacred grove of Romowe, hung with "
            "ribbons and talismans, a fire kept burning under its boughs."
        ),
        notes=(
            "Magic Might 45, currently 30 while it is trapped.\n"
            "Special Powers: Grant Flaw (Depression, on anyone who breaks a "
            "branch or kills a beast in the grove), Possession (of anyone who "
            "takes a branch).\n"
            "St Adalbert of Prague drove the tyrant spirit back into the oak "
            "and lit the fire that holds it; a band of foresters keeps the "
            "fire fed, for if it goes out the spirit is free."
        ),
        place=places["romowe"],
    )
    holm_oak.might_pool = 30


def _faeries(rhine: Rhine) -> None:
    b, places, world = rhine.b, rhine.places, rhine.world

    holzfrau = b.creature(
        "Holzfrau",
        page="p. 36",
        tires=False,
        realm="Faerie",
        might=20,
        how_many="many, in the forests of Germany",
        block={
            "characteristics": {
                "intelligence": 1,
                "perception": 1,
                "presence": 2,
                "communication": -1,
                "strength": -2,
                "stamina": 0,
                "dexterity": 0,
                "quickness": 0,
            },
            "virtues_flaws": [("Ways of the {land}", {"land": "Forest"})],
            "abilities": [
                ("Athletics", 2, "escaping pursuers"),
                ("Awareness", 2, "travelers"),
                ("Charm", 3, "men"),
                ("Chirurgy", 5, "infected wounds"),
                ("Faerie Lore", 5, "faerie plants"),
                ("Magic Lore", 4, "magical herbs"),
                ("Second Sight", 4, "animals"),
                ("Stealth", 3, "hiding from pursuers"),
            ],
            "traits": {"Kindly": 3, "Shy": 3},
        },
        attacks=[b.attack("Dodging", 0, None, 0, None)],
        soak=0,
        powers=[
            b.power(
                "Control Plants",
                1,
                1,
                "Herbam",
                does=(
                    "Any Creo or Rego Herbam effect up to 20th level, for 1 "
                    "Might per magnitude; the cost doubles in winter."
                ),
            ),
            b.power(
                "Fertility",
                4,
                1,
                "Herbam",
                does=(
                    "As The Bountiful Feast: fruitful, protected crops. She can "
                    "take the blessing back if her kindness is abused."
                ),
            ),
            b.power(
                "Healing",
                4,
                -1,
                "Corpus",
                does=(
                    "Her kiss eases pain, cleans infection from a wound or "
                    "speeds healing: it cures a Light Wound from disease or "
                    "gives +9 to recovery rolls."
                ),
            ),
        ],
        vis=[BodyVis(4, "Herbam", "in her hair")],
        appearance=(
            "Always a woman, often young and lovely, barefoot in peasant dress, "
            "with some telling detail of clothing that marks which kind of "
            "wood-wife she is."
        ),
        notes=(
            "A wood-wife, a usually kindly faerie of growing things; many serve "
            "the Alder Prince of the Courts of the Seasons.\n"
            f"{FAERIE_NATURE}\n"
            "Vulnerable to iron: cold-forged iron pains her and she shuns its "
            "touch, though it does her no harm.\n"
            "Wound penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20)."
        ),
    )
    b.link(
        world["wild_hunt_and_holzfrau"], "creatures", holzfrau, "the hunted wood-wife"
    )

    bockman = b.creature(
        "Bockman",
        page="p. 50",
        tires=False,
        realm="Faerie",
        might=20,
        form="Animal",
        size=-1,
        how_many="many, though each hunts alone",
        block={
            "characteristics": {
                "intelligence": -1,
                "perception": 1,
                "presence": -5,
                "communication": 0,
                "strength": 1,
                "stamina": 2,
                "dexterity": 5,
                "quickness": 2,
            },
            "virtues_flaws": [("Ways of the {land}", {"land": "Forest"})],
            "abilities": [
                ("Athletics", 3, "leaping"),
                ("Awareness", 3, "forests"),
                ("Area Lore: Black Forest", 6, "roads"),
                ("Brawl", 3, "claws"),
                ("Second Sight", 4, "glamors"),
                ("Stealth", 3, "forests"),
                ("Survival", 6, "forests"),
            ],
            "traits": {"Malicious": 3, "Brave": -1},
        },
        attacks=[b.attack("Claws", 9, 13, 9, 3)],
        soak=5,
        powers=[
            b.power(
                "The Patient Stance",
                0,
                0,
                "Imaginem",
                does=(
                    "Init n/a. Standing still in a forest it cannot be told "
                    "from the undergrowth, in effect invisible."
                ),
            ),
            b.power(
                "Unease of the Still Forest",
                2,
                0,
                "Mentem",
                does=(
                    "Init n/a; costs 2 points per hour. A hush and creeping "
                    "dread for 100 paces round it: each hour gives a "
                    "cumulative -1 to brave or bold Personality Traits and a "
                    "like boost to ones such as Short-Tempered or Suspicious, "
                    "and no one in it can sleep or recover Fatigue."
                ),
            ),
            b.power(
                "Fear",
                4,
                2,
                "Mentem",
                does=(
                    "Victims who fail a stress roll against 6 (adjusted by "
                    "Brave) flee until exhausted, or cower until sunrise if "
                    "they cannot run. Up to ten who can see it, or one target "
                    "if it is unseen."
                ),
            ),
        ],
        vis=[
            BodyVis(1, "Animal", "in its right horn"),
            BodyVis(1, "Mentem", "in its left horn"),
        ],
        appearance=(
            "Man-shaped only in chest and arms, with a goat's head and legs, "
            "sharp swept-back horns, wild eyes and a drooling mouth of sharp "
            "teeth."
        ),
        notes=(
            "Lurks by the Black Forest's paths (and in many old German "
            "forests) to frighten travellers away: it spooks them and their "
            "mounts with its unease, then springs out with Fear. Weak and "
            "cowardly in a real fight. Its claws include the Ways of the "
            "Forest bonus.\n"
            f"{FAERIE_NATURE}\n"
            "Vulnerable to iron: iron weapons do it 2 extra damage.\n"
            "Wound penalties: -1 (1-4), -3 (5-8), -5 (9-12), Incapacitated "
            "(13-16)."
        ),
        place=places["black_forest_road"],
    )
    b.link(world["bockmen"], "creatures", bockman, "their stat block")

    b.creature(
        "Loreley",
        page="p. 127",
        tires=False,
        realm="Faerie",
        might=30,
        form="Aquam",
        block={
            "characteristics": {
                "intelligence": 0,
                "perception": 1,
                "presence": 5,
                "communication": 5,
                "strength": -2,
                "stamina": -1,
                "dexterity": 2,
                "quickness": 0,
            },
            "traits": {"Hateful to Men": 3, "Jealous of Women": 3},
        },
        attacks=[b.attack("Dodging", 0, None, 0, None)],
        soak=5,
        powers=[
            b.power(
                "Infatuation",
                4,
                0,
                "Imaginem",
                does=(
                    "Her song makes up to ten hearers a round long to reach "
                    "her at any cost, into the river or onto the rocks. "
                    "Resisted by an Intelligence stress roll against 9; women "
                    "and those with waxed ears get +3, and a dripstone lets "
                    "its wearer ignore it on a Perception roll against 6."
                ),
            ),
            b.power(
                "Control Person",
                8,
                2,
                "Mentem",
                does=(
                    "On a man who meets her eyes, one at a time: unless he "
                    "makes an Intelligence stress roll against 12 he does "
                    "whatever she says, even leaping to his death."
                ),
            ),
            b.power(
                "Control Water",
                1,
                0,
                "Aquam",
                does=(
                    "Any Creo or Rego Aquam effect up to 30th level, for 1 "
                    "Might per magnitude."
                ),
            ),
            b.power(
                "Form of Water",
                10,
                3,
                "Aquam",
                does=(
                    "She becomes water and slips into the Rhine, regaining 5 "
                    "Might an hour (four times her usual rate) and healing "
                    "Light, Medium and Heavy wounds in minutes, hours and days; "
                    "she is all but unkillable."
                ),
            ),
        ],
        vis=[
            BodyVis(6, "Aquam", "in her blood"),
            BodyVis(4, "Imaginem", "in her comb"),
        ],
        appearance=(
            "A maiden of great beauty, clad only in long golden hair that she "
            "combs without end with a jewelled comb."
        ),
        notes=(
            f"{FAERIE_NATURE}\n"
            "Vulnerable to iron: the least touch of cold iron gives her a "
            "Light Wound, and an iron weapon that gets past her Soak raises "
            "its wound by one level.\n"
            "Wound penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20)."
        ),
        place=places["loreley"],
    )


def _magical_beasts(rhine: Rhine) -> None:
    b, places, world = rhine.b, rhine.places, rhine.world

    sordus = b.creature(
        "Sordus, a Basilisk",
        page="p. 61",
        realm="Magic",
        might=30,
        form="Animal",
        size=-2,
        block={
            "characteristics": {
                "intelligence": -3,
                "perception": 0,
                "strength": 0,
                "stamina": 4,
                "dexterity": -3,
                "quickness": -3,
            },
            "abilities": [
                ("Folk Ken", 2, "intimidate"),
                ("Living Language: German", 5, "insults"),
                ("Hunt", 4, "lying in wait"),
                ("Dead Language: Latin", 5, "whispers"),
                ("Magic Lore", 2, "beasts"),
                ("Living Language: West Norse", 3, "threats"),
            ],
            "traits": {"Disdainful": 3, "Lazy": 3, "Indifferent": 1},
        },
        soak=10,
        fatigue_levels="OK, -1, -5, Unconscious",
        powers=[
            b.power(
                "Gaze of Death",
                8,
                -3,
                "Corpus",
                does="Anyone his gaze falls on, if he wills it, takes an "
                "Incapacitating wound.",
            ),
            b.power(
                "Horrid Wilting",
                0,
                0,
                "Herbam",
                does=(
                    "Init n/a; always on. Plants within 5 paces die, food "
                    "rots and grows worms, and wood starts to decay within a "
                    "day."
                ),
            ),
            b.power(
                "Pollute Water",
                0,
                0,
                "Aquam",
                does=(
                    "Init n/a; always on. Standing water within 5 paces "
                    "stagnates, other liquids putrefy, and running water turns "
                    "black until he moves on."
                ),
            ),
        ],
        vis=[
            BodyVis(10, "Perdo", "in his left eye"),
            BodyVis(10, "Perdo", "in his right eye"),
        ],
        appearance=(
            "A huge lizard about knee-high and six feet from snout to tail, "
            "with tiny diamond scales of grey, dark green and black and a "
            "crown-like fleshy crest; every movement slow and deliberate."
        ),
        notes=(
            "Familiar of Archmage Philippus Niger of Durenmar, who keeps him "
            "mostly out of sight but lets him prowl a room to underline a "
            "threat. Presence and Communication n/a. Too lazy to fight.\n"
            "Bond (PeVi Lab Total 81): Bronze +2, Silver +2, Gold +4. Familiar "
            "power: Mental Communication (level 15), constant mental contact "
            "with Philippus, which either can shut off.\n"
            "Wound penalties: -1 (1-3), -3 (4-6), -5 (7-9), Incapacitated "
            "(10-12)."
        ),
        place=places["durenmar_site"],
    )
    b.link(rhine.magi["philippus_niger"], "creatures", sordus, "his familiar")

    boglin = b.creature(
        "Boglin",
        page="p. 79",
        cunning=True,
        realm="Magic",
        might=25,
        form="Aquam",
        size=3,
        how_many="a few, each in its own foul pool",
        block={
            "characteristics": {
                "intelligence": 1,
                "perception": -2,
                "presence": -5,
                "communication": -3,
                "strength": 5,
                "stamina": 6,
                "dexterity": -1,
                "quickness": 2,
            },
            "virtues_flaws": [
                ("Greater Immunity", {"hazard": "bludgeoning weapons"}),
                ("Ways of the {land}", {"land": "Swamp"}),
                "Tough",
                "Blind",
                "Greedy (Major)",
                "Obese",
                "Tainted With Evil",
            ],
            "abilities": [
                ("Awareness", 5, "swamp"),
                ("Brawl", 8, "tentacle"),
                ("Stealth", 3, "swamp"),
                ("Survival", 6, "swamp"),
                ("Swim", 3, "swamp"),
            ],
            "traits": {"Greedy": 5, "Reclusive": 2, "Guileful": 1},
        },
        attacks=[
            b.attack("Tentacle", 10, 14, 12, 8),
            b.attack("Bite", 3, 10, 11, 13),
        ],
        soak=12,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Abominable Stench",
                5,
                2,
                "Auram",
                does=(
                    "A cloud of choking swamp gas from beneath the waterline "
                    "spreads 15 yards over 3 rounds and takes 3 more to clear. "
                    "Anyone in it fails a Stamina roll against 9 and can do "
                    "nothing but reel back; a botch leaves them retching on "
                    "the ground."
                ),
            ),
            b.power(
                "Paralysis",
                3,
                0,
                "Corpus",
                does=(
                    "Init n/a; Corpus or Animal. A tentacle hit that wounds "
                    "injects venom: unless the victim makes a Stamina roll "
                    "against 9, his muscles cramp for -5 to physical actions "
                    "for about an hour. Once per tentacle per fight."
                ),
            ),
            b.power(
                "Writhing Grasp",
                0,
                0,
                "Corpus",
                does=(
                    "Init n/a; Corpus or Animal. A tentacle hit worth a Medium "
                    "Wound or worse does only a Light Wound but wraps the "
                    "victim. Each round he may try an opposed Strength roll to "
                    "break free or an opposed Dexterity roll to free his "
                    "hands; held, he is hauled to the maw in 3 rounds, and "
                    "only then can it Bite."
                ),
            ),
            b.power(
                "Regeneration",
                20,
                0,
                "Animal",
                does="Init n/a. It hibernates and regrows one lost tentacle a season.",
            ),
        ],
        vis=[
            BodyVis(8, "Animal", "one pawn in each tentacle"),
            BodyVis(6, "Perdo", "in its brain, a black and stinking nodule"),
        ],
        appearance=(
            "Eight slimy dark-brown tentacles twelve feet long round a huge, "
            "lumpy, shell-covered body that seldom leaves the murky water, "
            "with a wide toothed mouth somewhere within."
        ),
        notes=(
            "A foul primeval spirit of the north German swamps; a stink and "
            "faint murmuring betray its pool. The book gives Size +3 for the "
            "body, 0 for each tentacle. "
            "Its Greater Immunity makes it immune to damage from bludgeoning "
            "weapons; its attacks include the Ways of the Swamp bonus.\n"
            "Each tentacle fights as a separate creature with its own wounds; "
            "an Incapacitating blow may sever it, which costs the body a Light "
            "Wound. Wound penalties: body -1 (1-8), -3 (9-16), -5 (17-24), "
            "Incapacitated (25-32); each tentacle -1 (1-5), -3 (6-10), -5 "
            "(11-15), Incapacitated (16-20)."
        ),
        place=places["northern_swamps"],
    )
    b.link(world["boglins"], "creatures", boglin, "their stat block")


def _infernal(rhine: Rhine) -> None:
    b, places = rhine.b, rhine.places
    tower = places["mauseturm"]

    b.creature(
        "The Mice of the Mäuseturm",
        page="p. 122",
        realm="Infernal",
        might=10,
        form="Animal",
        size=0,
        how_many="about ten swarms, endlessly renewed by the aura",
        powers=[
            b.power(
                "Swarm",
                0,
                0,
                "",
                does=(
                    "A swarm of about a thousand mice engages about three "
                    "people and bites bare flesh with no attack roll. Damage a "
                    "round by protection (armour does not add to Soak): none, "
                    "stress die +6; sturdy clothes, +3; winter garb or partial "
                    "armour, +0; half armour, -3; full armour, -6; full armour "
                    "with helm and gauntlets, -9."
                ),
            )
        ],
        notes=(
            "Size -10 each; a swarm counts as one Size 0 creature. A victim "
            "kills 10 mice for every 5 points of his Brawl Attack Total each "
            "round, and the swarm flees once over half are dead. Area spells "
            "(Group, Room) can strike a whole swarm but will catch its "
            "victims too; an Animal spell at Voice, Concentration, Group "
            "affects one swarm, and one magnitude higher clears the island for "
            "a while. Their teeth burn and they are immune to fire. The "
            "island's Infernal aura breeds them anew until it is cleansed."
        ),
        place=tower,
    )

    b.creature(
        "Bishop Hatto",
        page="p. 122",
        realm="Infernal",
        might=30,
        form="Mentem",
        block={
            "characteristics": {"intelligence": 1},
            "traits": {"Hateful": 6, "Merciless": 4, "Brave": 3},
        },
        attacks=[b.attack("Touch", 3, 6, 0, None)],
        powers=[
            b.power(
                "Lurk in Shadows",
                0,
                0,
                "",
                does=(
                    "Hidden wholly in a shadow; even moving in, the dark patch "
                    "is seen only on Perception + Awareness against 12 (9 by "
                    "day). His attacks can be dodged only once he is seen."
                ),
            ),
            b.power(
                "Fear",
                4,
                0,
                "Mentem",
                does=(
                    "Up to ten people a use are filled with terror of the "
                    "island; repeated, it can drive the trapped mad or kill "
                    "them of fright, the fate of any who stay the night."
                ),
            ),
            b.power(
                "Chill Touch",
                0,
                3,
                "Corpus",
                does=(
                    "Init +3, with his attack. An icy touch that takes a "
                    "Fatigue level from the target and gives the bishop 5 "
                    "Might."
                ),
            ),
        ],
        vis=[BodyVis(6, "Perdo", "in his crosier, found only once he is destroyed")],
        appearance=(
            "A ragged shard of darkness, roughly man-shaped; close up, the "
            "bishop's demon-twisted face and mitre show in it."
        ),
        notes=(
            "The damned ghost of the bishop who haunts the Mäuseturm. His "
            "touch can be defended against only with Brawl: weapon defences "
            "fail as the blade passes through him. Its damage is his Chill "
            "Touch."
        ),
        place=tower,
    )


def _ghosts(rhine: Rhine) -> None:
    """The three gladiators the Trumpet of Ghostly Summoning calls up in
    Trier's amphitheatre."""
    b = rhine.b
    arena = rhine.places["trier_amphitheatre"]
    shared = (
        "One of three ghostly gladiators who form in the amphitheatre of Trier "
        "when the Trumpet of Ghostly Summoning is blown there at night. Each "
        "challenges all comers to a duel to the death, staking a trinket "
        "(worth 2 pawns of Mentem vis) against something of like value; the "
        "fight feels real but is truly non-lethal, a killing blow leaving the "
        "loser unconscious. A gladiator fades whether he wins or loses and "
        "cannot be called again that year."
    )

    b.creature(
        "Marcus the Valiant",
        page="p. 134",
        realm="Magic",
        might=20,
        block={
            "characteristics": {
                "intelligence": 0,
                "perception": 0,
                "presence": 1,
                "communication": 2,
                "strength": 2,
                "stamina": 3,
                "dexterity": 3,
                "quickness": 2,
            },
            "traits": {"Brave": 3, "Duty-Bound": 3, "Honorable": 1},
        },
        attacks=[
            b.attack("Gladius and round shield", 3, 14, 13, 7),
            b.attack("Gladius", 3, 13, 10, 7),
            b.attack("Dagger", 2, 11, 8, 5),
        ],
        soak=7,
        equipment=(
            "Round shield, manica on the right arm, greave on the left leg, "
            "gladius, ornate brimmed bronze helmet."
        ),
        appearance=("The stocky leader of the three, armed as a hoplomachus."),
        notes=(
            f"{shared}\n"
            "Wound penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20)."
        ),
        place=arena,
    )

    b.creature(
        "Cyrillus of Argentoratum",
        page="p. 134",
        realm="Magic",
        might=20,
        block={
            "characteristics": {
                "intelligence": 0,
                "perception": 0,
                "presence": 1,
                "communication": 1,
                "strength": 2,
                "stamina": 2,
                "dexterity": 2,
                "quickness": 4,
            },
            "traits": {"Brave": 3, "Duty-Bound": 3, "Crafty": 1},
        },
        attacks=[
            b.attack("Trident and net", 7, 12, 14, 7),
            b.attack("Net", 4, 11, 11, 7),
            b.attack("Dagger", 4, 8, 8, 5),
        ],
        soak=4,
        equipment=(
            "Trident, net, galerus (metal shoulder guard), manica of quilted "
            "linen on the left arm, copper mask of Poseidon."
        ),
        appearance="A wiry, dark-haired retiarius.",
        notes=(
            f"{shared}\n"
            "His net attack is resolved as a scuffle, to pin a foe or "
            "entangle a weapon.\n"
            "Wound penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
            "(16-20)."
        ),
        place=arena,
    )

    b.creature(
        "Caudelix the Gaul",
        page="p. 134",
        realm="Magic",
        might=20,
        size=1,
        block={
            "characteristics": {
                "intelligence": 0,
                "perception": 0,
                "presence": 1,
                "communication": 0,
                "strength": 5,
                "stamina": 4,
                "dexterity": 2,
                "quickness": 1,
            },
            "traits": {"Brave": 3, "Duty-Bound": 3, "Violent": 1},
        },
        attacks=[
            b.attack("Great axe", 1, 16, 9, 15),
            b.attack("Hatchet", 1, 11, 7, 9),
            b.attack("Gauntlet", 1, 8, 8, 7),
        ],
        soak=8,
        equipment=(
            "Long-hafted axe, hatchet, iron skull cap with a spectacle mask, "
            "leather bracae on the thighs, bracers."
        ),
        appearance="A huge, burly man with fair braided hair.",
        notes=(
            f"{shared}\n"
            "Wound penalties: -1 (1-6), -3 (7-12), -5 (13-18), Incapacitated "
            "(19-24)."
        ),
        place=arena,
    )
