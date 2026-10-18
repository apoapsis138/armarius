"""The Normandy Tribunal's Bestiary: every creature stat block The Lion
and the Lily prints (the korrigan of Brocéliande, the Black Dog, the
Three Great Spirits of Ushant, the Nains of Carnac, the lutin and the
Boar King), each at the place it haunts, in paraphrase.

The book's text on redcap.org carries no page numbers, so no page is
given. Creatures the book only describes (the Ankeu, St. Corentine's
fish, the Sleepers of the tumuli, the monster of the vacant castle) have
no stat block and stay in the summaries of their places. Built after the
places and stories, since it places the creatures there and links the
threats and courts they belong to."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis

if TYPE_CHECKING:
    from . import Normandy

#: The book gives no page numbers for its open-content text.
PAGE = ""


def build(normandy: Normandy) -> None:
    _korrigan(normandy)
    _black_dog(normandy)
    _great_spirits(normandy)
    _nain(normandy)
    _lutin(normandy)
    _boar_king(normandy)


def _korrigan(normandy: Normandy) -> None:
    b = normandy.b
    b.creature(
        "Korrigan",
        page=PAGE,
        age="n/a",
        confidence=(0, 0),
        encumbrance="0 (0)",
        tires=False,
        realm="Faerie",
        might=10,
        form="Animal",
        size=-2,
        how_many="Bands; they dance in rings at crossroads",
        block={
            "characteristics": {
                "intelligence": -2,
                "perception": 1,
                "presence": -2,
                "communication": 1,
                "strength": -1,
                "stamina": 3,
                "dexterity": 2,
                "quickness": 2,
            },
            "abilities": [
                ("Area Lore", 3, "paths"),
                ("Athletics", 5, "dancing"),
                ("Awareness", 4, "gold, silver"),
                ("Brawl", 2, "claws"),
                ("Guile", 1, "bargaining"),
                ("Living Language: Breton", 4, "commands"),
                ("Stealth", 4, "hiding"),
                ("Single Weapon", 2, "club"),
                ("Thrown Weapon", 2, "stones"),
            ],
            "traits": {"Avaricious": 2, "Capricious": 2, "Short-tempered": 2},
            "reputations": {
                "Dangerous (Local)": 3,
                "Tireless dancers (Local)": 1,
                "Magicians (Local)": 1,
            },
        },
        attacks=[
            b.attack("Claws", init=1, attack=7, defense=8, damage=1),
            b.attack("Club", init=3, attack=6, defense=5, damage=2),
            b.attack("Stone (thrown)", init=2, attack=5, defense=4, damage=1),
        ],
        soak=3,
        fatigue_levels="n/a",
        powers=[
            b.power(
                "Human Form",
                5,
                2,
                "Corpus",
                does=(
                    "Only the stronger korrigan have it. The korred becomes a "
                    "lovely young woman for an hour, or until it spends the "
                    "same Might again to change back. In that shape: Int -2, "
                    "Per +1, Pre +2, Com +1, Str -1, Sta 0, Dex 0, Qik -1, "
                    "Size 0; Club Init +0, Attack +2, Defense +0, Damage +2; "
                    "Stone (thrown) Init -1, Attack +3, Defense +1, Damage +1."
                ),
            )
        ],
        vis=[BodyVis(1, "Animal", "in its hooves")],
        equipment="Usually none.",
        appearance=(
            "A stooped little man about three feet high, with a cat's claws for "
            "hands and a goat's hooves for feet."
        ),
        notes=(
            "Might: the book gives typically 5 to 10, rarely 15; 10 is used here. "
            "These are the korrigan of Brocéliande, grown dangerous since their "
            "queen Viviane lost interest in the forest and them; elsewhere in "
            "Brittany (forests, caves, dolmens) they are milder, caring mostly "
            "for dancing and hoarded treasure, though still quick to anger. "
            "They punish those who vex them, now and then reward someone from "
            "their hoard, and invite passers-by into their moonlit dances: "
            "those who join may get a gift, those who refuse are punished. "
            "Natural weapons: Claws Init -1, Attack +2, Defense +3, Damage +2. "
            "Wound penalties: -1 (1-3), -3 (4-6), -5 (7-9), Incapacitated "
            "(10-12), Dead (13+). No Virtues or Flaws. The book prints the "
            "block under the Rose Coast."
        ),
        place=normandy.places["broceliande"],
    )


def _black_dog(normandy: Normandy) -> None:
    b = normandy.b
    b.creature(
        "The Black Dog",
        page=PAGE,
        cunning=True,
        confidence=(0, 0),
        realm="Divine",
        might=10,
        form="Animal",
        size=-1,
        block={
            "characteristics": {
                "intelligence": 0,
                "perception": 2,
                "presence": -4,
                "communication": 0,
                "strength": 0,
                "stamina": 2,
                "dexterity": 1,
                "quickness": 2,
            },
            "virtues_flaws": [
                "Improved Characteristics",
                "Long-Winded",
                "Sharp Ears (Minor)",
                "Reckless (Minor)",
                "Domesticated",
                "Keen Sense of Smell (Free)",
                "Pack Animal",
                "Pursuit Predator",
                "Vocal",
            ],
            "abilities": [
                ("Athletics", 3, "distance running"),
                ("Awareness", 3, "keeping watch"),
                ("Brawl", 3, "bite"),
                ("Hunt", 4, "track by scent"),
            ],
            "traits": {"Loyal": 3, "Reckless": 3, "Brave": 2},
            "reputations": {"Terrifying (Local)": 3},
        },
        attacks=[b.attack("Bite", init=2, attack=8, defense=7, damage=1)],
        soak=2,
        fatigue_levels="OK, 0/0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Fearsome Bark",
                1,
                2,
                "Animal",
                rtd=("Voice", "", ""),
                does=(
                    "Animal or Mentem. Works like Panic of the Trembling Heart, "
                    "but reaches as far as the bark is heard."
                ),
            ),
            b.power(
                "Dreadful Howl",
                3,
                2,
                "Animal",
                rtd=("Voice", "Sun", ""),
                does=(
                    "Animal or Mentem. Works like Weight of a Thousand Hells, "
                    "but lasts until sunrise or sunset and reaches as far as "
                    "the howl is heard."
                ),
            ),
        ],
        vis=[BodyVis(1, "", "in its tongue (1 or 2 pawns)")],
        appearance="A black dog, usually a little smaller than a man; rare ones are man-sized (Size 0).",
        notes=(
            "A Breton folk rite shuts the spirit of a dead relative who will "
            "not leave the house into a black dog: the dog is brought indoors, "
            "a favourite garment of the dead tied round it, and fed a lump of "
            "meat stuffed with plants from the graveyard, then drowned as fast "
            "as possible to free the spirit. Until it dies it is the creature "
            "here; killed any other way than drowning, it leaves the spirit "
            "bound to the spot where it died, and its tongue holds the vis (a "
            "drowned dog has none). Its Might is usually 5, up to 10 for a "
            "very holy or very wicked dead; a great sinner's spirit gives an "
            "Infernal dog, a pagan's (rarely) a Magic one. Natural weapons: "
            "Bite Init 0, Attack +3, Defense +1, Damage +1. Wound penalties: "
            "-1 (1-4), -3 (5-8), -5 (9-12), Incapacitated (13-16), Dead "
            "(17+). The book prints it under the Arrée Mountains, but the "
            "rite is used across Brittany."
        ),
        place=normandy.places["brittany"],
    )


def _great_spirits(normandy: Normandy) -> None:
    b = normandy.b
    fudarus = normandy.covenant_named("Fudarus")
    spirits = (
        (
            "Mogidell",
            "a spirit of mist and sea-fog",
            "Mastery of Mist",
            "Auram",
            "mist and fog",
            "A vast grey bird filling the sky; when she spreads her wings the "
            "sea-fog comes down over Ushant.",
        ),
        (
            "Kerseenn",
            "a spirit of misdirection",
            "Mastery of Misdirection",
            "Imaginem",
            "misdirection and concealment",
            "A sky-filling shape forever changing between strange blends of "
            "man and beast.",
        ),
        (
            "Arnev",
            "a spirit of stormy weather",
            "Mastery of Storms",
            "Auram",
            "gales, rain and other foul weather",
            "A vast serpent with a horse's head, filling the sky.",
        ),
    )
    for name, kind, mastery, art, subject, looks in spirits:
        spirit = b.creature(
            f"{name}, Great Spirit of Ushant",
            page=PAGE,
            realm="Magic",
            might=40,
            form="Auram",
            block={
                "characteristics": {
                    "intelligence": 2,
                    "perception": 4,
                    "presence": 5,
                    "communication": 3,
                    "strength": 3,
                    "stamina": 2,
                    "dexterity": -2,
                    "quickness": 0,
                },
                "virtues_flaws": [("Ways of the Land", {"land": "Island"})],
                "traits": {"Watchful": 5, "Capricious": 3, "Playful": 3},
            },
            powers=[
                b.power(
                    "Incorporeal",
                    0,
                    0,
                    "Mentem",
                    rtd=("", "Constant", ""),
                    does=(
                        "Always on. Unseen and untouchable, and beyond the "
                        "reach of the physical world; a spell can aim at the "
                        "spirit only if the caster can sense it is there."
                    ),
                ),
                b.power(
                    "Presence",
                    0,
                    0,
                    "Mentem",
                    rtd=("", "Constant", ""),
                    does="Always on. The spirit knows all that happens on Ushant.",
                ),
                b.power(
                    mastery,
                    1,
                    0,
                    art,
                    does=(
                        f"Costs 1 to 8 points: one per magnitude. Matches any "
                        f"non-Ritual spell of level 40 or less dealing with "
                        f"{subject}."
                    ),
                ),
            ],
            appearance=looks,
            notes=(
                f"One of the Three Great Spirits of Ushant, {kind}. The book "
                "gives the three one shared block (Size, Soak and combat not "
                "given; the Virtue is Ways of the Island). Diedne magi summoned "
                "them against Fudarus in the Schism War; Primus Klynoites took "
                "control of them, and they have been bound into the "
                "covenant's walls ever since as genii loci, taking turns to "
                "hide Fudarus from chance discovery and opening a way for "
                "visitors who give the password. They obey whoever bears the "
                "Circlet of the Primus, through the old pact with Fudarus's "
                "theurgists rather than the Circlet's own power. Their "
                "presence makes 12 pawns of vis appear on Ushant each year, 4 "
                "each of Creo, Auram and Imaginem, in a form only Fudarus "
                "knows. Mastery powers: the Might cost given here is the "
                "least; it rises with the effect's magnitude."
            ),
            place=normandy.places["ushant"],
        )
        b.link(fudarus, "creatures", spirit, "Bound into the covenant's walls")


def _nain(normandy: Normandy) -> None:
    b = normandy.b
    b.creature(
        "Nain",
        page=PAGE,
        age="n/a",
        confidence=(0, 0),
        encumbrance="0 (0)",
        tires=False,
        realm="Infernal",
        might=10,
        form="Animal",
        size=-2,
        how_many="Packs; three to each victim",
        block={
            "characteristics": {
                "intelligence": -2,
                "perception": 1,
                "presence": -3,
                "communication": 1,
                "strength": -1,
                "stamina": 3,
                "dexterity": 3,
                "quickness": 2,
            },
            "abilities": [
                ("Area Lore", 3, "Carnac"),
                ("Athletics", 5, "dancing"),
                ("Brawl", 2, "claws"),
                ("Folk Ken", 4, "temptation"),
                ("Guile", 1, "lying"),
                ("Living Language: Breton", 2, "yelping"),
                ("Stealth", 4, "ambushes"),
                ("Thrown Weapon", 3, "stones"),
            ],
            "traits": {"Sadistic": 2, "Lustful": 2, "Energetic": 2},
            "reputations": {
                "Demonic (Local)": 5,
                "Tireless Dancers (Local)": 2,
                "Magicians (Local)": 1,
            },
        },
        attacks=[
            b.attack("Claws", init=1, attack=7, defense=8, damage=1),
            b.attack("Stone (thrown)", init=2, attack=5, defense=4, damage=1),
        ],
        soak=3,
        fatigue_levels="n/a",
        powers=[
            b.power(
                "Glittering Treasure",
                2,
                3,
                "Terram",
                does=(
                    "Conjures silver coins that gleam in the moonlight among "
                    "the stones. They vanish at dawn; the Nains use them as "
                    "bait to draw the greedy into an ambush."
                ),
            ),
            b.power(
                "Deadly Dance",
                2,
                3,
                "Corpus",
                does=(
                    "Up to ten victims must dance wildly with the Nains until "
                    "sunrise. Each hour: Stamina stress roll against 6, or lose "
                    "a long-term Fatigue level; once unconscious, a Light Wound "
                    "instead. On a botch, two levels lost per 0 rolled (or the "
                    "Wound worsens by one level per 0). Many dance to death."
                ),
            ),
            b.power(
                "Magician's Desire Denied",
                1,
                3,
                "Vim",
                does=(
                    "Makes a pebble, leaf or the like seem to hold vis to an "
                    "Intellego Vim spell. The false vis vanishes at dawn or "
                    "when Sense the Nature of Vis is cast on it."
                ),
            ),
        ],
        vis=[BodyVis(1, "Animal", "in its hooves")],
        equipment="Usually none.",
        appearance=(
            "Imp-like little creatures the size of a child, with long filthy "
            "hair, a goat's bowed legs and red eyes that burn like fire."
        ),
        notes=(
            "The guardians of the stones of Carnac by night, when the "
            "Magic aura gives way to an Infernal one. They alone can read the "
            "signs traced on the rocks, seen only by starlight on moonless "
            "nights, and on their unholy night, the first Wednesday in May, "
            "they make blood sacrifices and the Infernal aura rises to 6. They "
            "lure the greedy with their false silver and false vis and attack "
            "in untrained packs, three to each victim. Natural weapons: Claws "
            "Init -1, Attack +2, Defense +3, Damage +2. Wound penalties: -1 "
            "(1-3), -3 (4-6), -5 (7-9), Incapacitated (10-12), Dead (13+). "
            "No Virtues or Flaws."
        ),
        place=normandy.places["carnac"],
    )


def _lutin(normandy: Normandy) -> None:
    b = normandy.b
    b.creature(
        "Lutin",
        page=PAGE,
        age="n/a",
        realm="Faerie",
        might=5,
        form="Aquam",
        size=-2,
        how_many="Common; one or more to a household",
        block={
            "characteristics": {
                "intelligence": -2,
                "perception": 2,
                "presence": 0,
                "communication": -1,
                "strength": -1,
                "stamina": 0,
                "dexterity": 3,
                "quickness": 2,
            },
            "abilities": [
                ("Area Lore: Normandy", 3, "villages"),
                ("Athletics", 4, "jumping"),
                ("Awareness", 3, "people"),
                ("Brawl", 1, "dodge"),
                ("Carouse", 2, "singing"),
                ("Etiquette", 4, "faeries"),
                ("Faerie Lore", 1, "nobles"),
                ("Guile", 3, "superiors"),
                ("Living Language", 5, "eavesdropping"),
                ("Profession: Servant", 5, "cleaning"),
                ("Stealth", 5, "indoors"),
                ("Swim", 3, "rivers"),
            ],
            "traits": {"Servile": 3, "Dreamer": 2},
            "reputations": {"Helpful spirit (Local)": 1},
        },
        attacks=[
            b.attack("Dodge", init=2, attack=None, defense=4, damage=None),
            b.attack(
                "Broom (improvised bludgeon)", init=2, attack=6, defense=3, damage=-3
            ),
        ],
        soak=0,
        powers=[
            b.power(
                "The Master's Things",
                0,
                0,
                "Terram",
                rtd=("", "Constant", "Room"),
                does=(
                    "Always on, indoors only. The lutin knows everything in "
                    "the room it is in, how many and where, by look alone, not "
                    "by use (a wand is just a little stick). It finds things "
                    "hidden by mundane means or by magic of magnitude 1 or "
                    "less; to find a person with Magic Resistance it must "
                    "penetrate."
                ),
            ),
            b.power(
                "Soap and Suds",
                1,
                1,
                "Aquam",
                rtd=("", "", "Room"),
                does=(
                    "Indoors only. The floor of the lutin's room turns soapy: "
                    "anyone moving quickly there, fighting included, rolls "
                    "Dexterity against 6 each round or slips."
                ),
            ),
        ],
        vis=[BodyVis(1, "Aquam", "in its heart")],
        equipment="Household things: a broom, a shovel or a cloth.",
        appearance=(
            "A small, servile goblin that looks like a tiny person; it keeps "
            "out of sight, even of those who leave it offerings."
        ),
        notes=(
            "Lutins clean houses in return for offerings of offal or clean "
            "water. They are common in Normandy's faerie courts and drawn to "
            "villages without a church. All of them dread a 'goblin duke of "
            "Normandy', of whom the Order knows nothing. The book gives no "
            "Fatigue levels, and Living Language without naming the tongue. "
            "Wound penalties: -1 (1-3), -3 (4-6), -5 (7-9), Incapacitated "
            "(10-12), Dead (13+). No Virtues or Flaws."
        ),
        place=normandy.places["normandy"],
    )


def _boar_king(normandy: Normandy) -> None:
    b = normandy.b
    king = b.creature(
        "The Boar King",
        page=PAGE,
        age="n/a (30)",
        confidence=(2, 6),
        realm="Faerie",
        might=40,
        form="Animal",
        size=1,
        block={
            "characteristics": {
                "intelligence": -1,
                "perception": 1,
                "presence": 2,
                "communication": -2,
                "strength": 4,
                "stamina": 5,
                "dexterity": 2,
                "quickness": 0,
            },
            "abilities": [
                ("Animal Handling", 5, "boar"),
                ("Area Lore: Normandy Tribunal", 5, "forest"),
                ("Athletics", 5, "running"),
                ("Awareness", 3, "trespassers"),
                ("Brawl", 9, "gore"),
                ("Carouse", 3, "lament"),
                ("Dead Language: Latin", 3, "hunting terms"),
                ("Dead Language: Gaulish", 5, "druidic terms"),
                ("Etiquette", 1, "courtly"),
                ("Faerie Lore", 5, "worship"),
                ("Folk Ken", 3, "hunters"),
                ("Great Weapon", 7, "boar spear"),
                ("Hunt", 10, "hunters"),
                ("Leadership", 5, "faeries"),
                ("Living Language: Breton", 3, "hunting terms"),
                ("Organization Lore: Order of Hermes", 2, "House Diedne"),
                ("Ride", 5, "hunting"),
                ("Stealth", 7, "forest"),
                ("Survival", 10, "forest"),
                ("Swim", 3, "swamp"),
            ],
            "traits": {"Reckless": 3, "Proud": 2, "Wrathful": 1},
            "reputations": {
                "King of the Forest (Local)": 3,
                "Ally of House Diedne (Hermetic)": 2,
            },
        },
        attacks=[
            b.attack("Boar Spear (foot)", init=3, attack=13, defense=9, damage=11),
            b.attack("Boar Spear (mounted)", init=3, attack=16, defense=12, damage=11),
            b.attack("Tusks (gore)", init=0, attack=12, defense=10, damage=7),
        ],
        soak=10,
        powers=[
            b.power(
                "Voice of the Woods",
                0,
                0,
                "Animal",
                rtd=("", "Constant", ""),
                does=(
                    "Always on; Animal, Herbam or Mentem. He can speak with any "
                    "beast or plant of the woods, and they carry out his "
                    "orders as best they can."
                ),
            ),
            b.power(
                "Sylvan Sanctity",
                1,
                0,
                "Mentem",
                does=(
                    "He learns roughly where and how many human intruders are "
                    "in his forest; too many to follow in full, but he easily "
                    "spots anyone entering a usually empty part. Must "
                    "penetrate, though magi's grogs seldom resist. Used daily, "
                    "and the forest's heart is days deep, so he is ready for "
                    "visitors."
                ),
            ),
            b.power(
                "Ancient Rage",
                5,
                -10,
                "Animal",
                rtd=("", "Sun", ""),
                does=(
                    "A frothing fury for a day: +3 to Attack and Soak, -3 to "
                    "Defense, no Wound Penalties short of Incapacitated. He "
                    "attacks at the least provocation and may neither retreat "
                    "nor spare anyone."
                ),
            ),
            b.power(
                "Impaled by the Thorn",
                5,
                -5,
                "Corpus",
                rtd=("Sight", "", "Ind"),
                does=(
                    "Corpus and Mentem. He hurls a boar spear at a human he can "
                    "see; it hits without a roll, and if it penetrates the "
                    "victim is frozen, unable to move, sense, think or cast, "
                    "and does not age. Pulling the spear out ends it but deals "
                    "a Heavy Wound, unless magic finds a way round that."
                ),
            ),
            b.power(
                "Call of the Hunter",
                10,
                0,
                "Herbam",
                does="He appears anywhere in his forest.",
            ),
        ],
        vis=[
            BodyVis(4, "Animal", "in his left tusk"),
            BodyVis(4, "Animal", "in his right tusk"),
        ],
        equipment=(
            "Several boar spears; his court can give him anything else he "
            "wants, though some of it may be glamour."
        ),
        appearance=(
            "A big man with a boar's head, two great tusks thickening his "
            "speech, abstract tattoos and bronze rings on his bare arms and "
            "chest, hide trousers and a cloak; he rides a wild horse bareback "
            "with faerie knights and courtiers about him."
        ),
        notes=(
            "A faerie the Gauls once worshipped, who claims the Tribunal's "
            "forests, hunts boar each autumn and hunts down hunters who take "
            "too much. Once allied with House Diedne, he now seeks Merinita "
            "or Bjornaer magi to replace them and turn back the clearing of "
            "his woods. He has no Virtues or Flaws. "
            "The book gives no Fatigue levels. Wound penalties: -1 (1-6), -3 "
            "(7-12), -5 (13-18), Incapacitated (19-24), Dead (25+)."
        ),
        place=normandy.places["boar_kings_hall"],
    )
    b.link(normandy.world["court_of_the_boar_king"], "creatures", king, "Its lord")
    b.link(normandy.world["threat_boar_king"], "creatures", king, "The antagonist")
