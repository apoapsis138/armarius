"""The Sunken Laboratory of Hermanus, in paraphrase of Legends of Hermes,
chapter five (pp. 95-120): the Tremere who walled Coeris in defenses for
eighty years and vanished with a floor of it in Final Twilight in 1098.

The sea valley off Crete is a place with its guardian and ghosts; the
laboratory structure is a place within it, each of its seven rooms a place
of its own holding that room's devices, in words, as no covenant owns them.
Hermanus and the other dead of the story are sketches. The search, House
Tremere's claim and the three hooks of p. 98 are dormant stories. Coeris is
named in words only: this pack has no Tribunal.

The errata (p. 78) correct Sense the Airy Trespass, and are followed here.
The rest is a summary of the book, not its words."""

from __future__ import annotations

from ...models import BodyVis, Neighbour
from ..builder import Builder, characteristics, dormant, paragraphs

SOURCE = "LoH"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"
S = Builder.stage

#: The spirits' one block (p. 109): Ferox and Fidelius differ only in
#: Personality Traits.
SPIRIT_ABILITIES = [
    ("Area Lore", 3, "near Coeris"),
    ("Awareness", 3, "keeping watch"),
    ("Brawl", 2, "dodging"),
    ("Code of Hermes", 3, "Transylvanian Tribunal"),
    ("Dead Language: Latin", 5, "Hermetic use"),
    ("Folk Ken", 3, "magi"),
    ("Great Weapon", 3, "staff"),
    ("Magic Lore", 3, "near Coeris"),
    ("Intrigue", 3, "negotiation"),
    ("Organization Lore: Order of Hermes", 3, "House Tremere"),
    ("Stealth", 3, "shadowing"),
]
WOUNDS_SIZE_0 = (
    "Wounds: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+)."
)
FISH_FATIGUE = "OK, OK, 0, -1, -3, -5, Unconscious"

STAFF = paragraphs(
    "Staff of the Wooden Soldiers. An invested device, a thick hazel staff "
    "topped with a silver eye, with a small chamber near the top for an Arcane "
    "Connection to one mannequin. Opened with 14 pawns, all filled. Four "
    "powers, each 12 a day, item maintains concentration, R: Arc, D: Conc: "
    "Pretense of Humanity (MuIm 19, T: Ind), the mannequin looks like a person "
    "of its size; Animate Mannequin (ReHe 34, T: Ind), it moves as the holder "
    "commands, with the holder's Dexterity, Quickness and Abilities and "
    "Strength +3; View from the Mannequin and Ears of the Mannequin (each InIm "
    "34, T: special, based on Room), the holder's sight or hearing moves to "
    "the mannequin, seeing or hearing even creatures with Magic Resistance, "
    "and into adjacent rooms and out of windows (p. 112-113).",
    "A blow of damage 10 or more takes a limb off a mannequin, 19 or more on "
    "the armored ones of the complex. Melee weapons they swing are resisted by "
    "Magic Resistance; crossbow bolts are not, not being driven by magic. "
    "Each mannequin's detachable wooden feature serves as the Arcane "
    "Connection, changed regularly at Coeris; those here have not decayed, as "
    "no time passed in the Void.",
)


def _people(b: Builder) -> None:
    b.magus(
        "Hermanus of Tremere",
        covenant=None,
        house=TREMERE,
        age=None,
        summary=paragraphs(
            "c. 940 to 1098 (Final Twilight). The master strategist who gave "
            "more than eighty years to making Coeris, the domus magna of House "
            "Tremere, a safe storehouse for the House's treasure. Thirty-nine "
            "years past his apprenticeship when the Schism War began, he "
            "served as a master of auxiliaries, training and leading mundane "
            "soldiers. Twice he won by foreseeing the attack: his unit, warded "
            "beforehand, outlasted two Diedne magi and their beasts until help "
            "came, and he hunted down and slew Nuala of Diedne, fifteen years "
            "his elder. He had no Gentle Gift and little persuasion, yet his "
            "troops held; so the primus gave him the Adamant Rook Vexillation, "
            "a group of enchanters.",
            "The House could not count on better magi than its foes, or on "
            "magics they did not know. Hermanus used what it did have, its "
            "cohesion, drawing in as much of its magi and resources as he "
            "could to build a network of devices through the covenant that "
            "found and held anyone acting against the Tremere. The more he "
            "built, the less he was content; his mind came to see only "
            "weakness. In 1070 the primus dissolved the vexillation, calling "
            "the work excessive, and others began to ask whether the vis had "
            "been well spent. For twenty-eight years more he kept at it alone, "
            "arguing, seeking the primacy, studying and enchanting.",
            "In the autumn of 1098, three hours after a last quarrel with the "
            "primus, the top floor of his wing of Coeris vanished with him, "
            "most think in Final Twilight. The Abyssal Bearer Vexillation "
            "(Houses of Hermes: True Lineages p. 122) searched, and the "
            "Unbarred Gateway Vexillation searched until early 1104. His fame "
            "outside the House came later (see Velius of Tremere).",
            "What the Order Remembers (pp. 10-11, 96). Intelligence + Order of "
            "Hermes Lore simple roll; the character recalls everything up to "
            "the Ease Factor reached. Research in a library: Covenants p. 98.",
            "Ease Factor 0, Known by All: His Final Twilight took away a whole "
            "part of Coeris. He was a Schism War veteran who oversaw defenses "
            "for the House's resources. He is famed for marshalling so much of "
            "the House to that end for decades. He found Diedne sympathizers "
            "in House Tremere, a cabal that destroyed him and made his "
            "laboratory vanish.",
            "Ease Factor 6, Widely Known: At the end he enchanted his "
            "laboratory to move, so he could see the world from behind its "
            "wards, and left Coeris and the House for good. He went on "
            "strengthening Coeris for twenty-eight years after the vexillation "
            "ended, clashing ever more with the primus and senior magi, and "
            "sought the primacy to further it.",
            "Ease Factor 12, Uncommon Knowledge: A vexillation hunted for him "
            "and the laboratory, and after four years found them beyond any "
            "Tremere method. He ended a great expert in Intellego, but was "
            "chosen for leadership; the greatest Adamant Rook works were "
            "made by magi in groups. Age made him ever more fearful, seeing "
            "attacks in everything, and he took to sending an enchanted "
            "human-sized doll out for vis in his stead. He died seeking vis "
            "from a Provencal town besieged by giant bats, and all record "
            "of the town save this has been destroyed by someone or something "
            "keeping it secret.",
            "Ease Factor 18, Lost Secrets: Amarantha of Tremere went on "
            "searching after the vexillation reported and dissolved. She "
            "disappeared in 1110, without a trace.",
        ),
        secrets=paragraphs(
            "False among the recollections (p. 96): the Diedne cabal; the "
            "laboratory enchanted to move; the Provencal town of giant bats. "
            "Much of his work may be known only inside House Tremere (p. 11).",
            "By 1091 he saw the House would never give him the vis, and "
            "meant to find it himself; but his fears kept him in his laboratory, "
            "behind eight warded rings. So he enchanted one of the Coeris "
            "mannequins and sent it out under his control, through Opening the "
            "Intangible Tunnel, to look for vis. That autumn evening in 1098 "
            "it stood on the sea floor off the south coast of Crete, among the "
            "wrecks of Demetrios the Poliorketes' battle with Ptolemy, and he "
            "tried to bring the vis home with a Rego spell from a casting "
            "tablet. The casting failed terribly. He and his familiar were "
            "lost to Final Twilight; the laboratory and its structure went to "
            "the Terram province of the Twilight Void, tethered to the "
            "mannequin and the vis.",
        ),
    )
    b.magus(
        "Amarantha of Tremere",
        covenant=None,
        house=TREMERE,
        age=None,
        summary=paragraphs(
            "Died late in 1110. A member of the Unbarred Gateway Vexillation "
            "who would not let the search end when it dissolved in 1104. She "
            "questioned those who had spoken with Hermanus or his familiar, "
            "read what he had read in his last years, and went through their "
            "letters. By 1110 she had a long list of places he might have sent "
            "his mannequin, and set off alone to visit them, telling no one: "
            "she feared looking a fool, and doubting the vexillation would "
            "have offended influential magi of the House.",
        ),
        secrets="Her end came far from help, somewhere the Abyssal Bearer "
        "Vexillation, charged with recovering the bodies of Tremere magi, never "
        "knew of. Her notes held some ideas for researching a spell to bring "
        "the laboratory back, but no firm plan. See The Remains of Amarantha.",
    )
    b.magus(
        "Velius of Tremere",
        covenant=None,
        house=TREMERE,
        age=None,
        summary=paragraphs(
            "Archmage from 1104; Final Twilight 1120. Come to Coeris from the "
            "Rhine Tribunal, he took on the danger of a vanished wing full of "
            "the covenant's own devices, shored up the defenses, then kept "
            "them working. In 1115 his former apprentice challenged him; "
            "he set her to fetch a token from a Coeris vault within the year, "
            "and she failed. Elonora of Tytalus then challenged him, sure he "
            "would not dare invite an outsider at the vaults; he put his "
            "marker there again, and she failed three times in the year. The "
            "primus was furious at his overconfidence, and a third use of the "
            "challenge was thought unlikely to go unpunished.",
        ),
    )
    b.magus(
        "Elonora of Tytalus",
        covenant=None,
        house=TYTALUS,
        age=None,
        summary=paragraphs(
            "The maga who challenged the Archmage Velius after his filia failed, "
            "and made three failed attempts on the defenses of Coeris. She passed on "
            "what she remembered of them, and spread tales that Velius leaned "
            "on Hermanus' work rather than his own. From her stories magi tried "
            "to reckon the vis and seasons spent at Coeris, and the legend of "
            "its unbreachable defenses went through the Order, helped by the "
            "Tremere, who wished their sodales to think any raid futile.",
        ),
    )


def _valley(b: Builder) -> Neighbour:
    valley = b.place(
        "The Aquatic Valley",
        status="Rumoured",
        known="",
        aura=2,
        summary=paragraphs(
            "A shallow valley on the sea floor off the south coast of Crete, "
            "of barnacled rock and gently sloping sand, strewn with the broken "
            "ships of an ancient battle. By day shafts of sunlight fall from "
            "the surface and move across the sand. It is very beautiful. "
            "Among the wrecks dozens of pale sailors go on fighting, day after "
            "day, as they have for fifteen hundred years. The water holds "
            "more light than its depth should allow.",
            "Rules. Magic aura 2. Depth 14 paces at the laboratory complex. "
            "Swimmers move at half walking speed; only thrusting weapons, or "
            "those where speed is no matter, work well, others suffering heavy "
            "penalties if they work at all. Trained groups do not carry over "
            "between land and water. Vision blurs, and only very large things "
            "show past 20 paces. Unaided, spells are cast with no words and "
            "subtle gestures, at the usual penalties, and a Voice range spell "
            "cast submerged reaches only targets in or touching the surface. "
            "After each 10 paces of descent a character loses, in Fatigue "
            "levels, a tenth of current depth minus Soak (armor not counted). "
            "Spells for going under water: Lungs of the Fish (ArM5 p. 122), "
            "Maris of Tytalus's creations (Magi of Hermes pp. 70-78), and here "
            "Cloak of Fins and Scales, Form of the Aquatic Predator and Shape "
            "of the Siren (p. 105-106), Breeze from Within and Eyes of the "
            "Fish (p. 106). Those transformed into fish suffer no pressure "
            "penalties. The Order holds such devices and Lab Texts, and a "
            "determined magus may bargain for them.",
            "The Ring of Aquatic Freedom (p. 106): a lesser enchanted device "
            "with Beyond Reach of the Sea, ReAq 34, constant effect, R: Touch, "
            "D: Sun, T: Part. Water stays 6 paces from the ring; the wearer "
            "cannot drink, and sweat is thrown from the body.",
        ),
        secrets=paragraphs(
            "The battle was fought between Demetrios the Poliorketes and "
            "Ptolemy I; the book dates it 306 BC on p. 99 and 309 BC on p. 101. "
            "Near the center of the valley lies a wreck with no ghosts on it. "
            "On it stands Hermanus' wooden mannequin, human-sized, gripping the "
            "mast, which is waterlogged but wholly free of rot and holds 8 "
            "pawns of Mentem vis. Hermanus' last spell pins both in place, "
            "against nearly any physical force.",
            "The return. Any spell aimed at either object (to move it, an "
            "Intellego spell, Rego Vim to draw the vis) undoes that spell and "
            "brings the laboratory structure back. All water within thirteen "
            "paces is thrust out, with sand and debris; swimmers are carried "
            "at least 20 paces unless they act against it. Characters not "
            "submerged should not be crushed. Stirred sediment blinds for a few "
            "minutes. A storyguide who wants the laboratory won rather than "
            "handed over can have the characters fetch it from the Twilight "
            "Void: Arcane Connections do not cross from the mundane world, "
            "so they must find a way into the Magic Realm (Realms of Power: "
            "Magic chapter three; p. 104).",
            "Moving the story (p. 101). Ancient naval battles fit, more or "
            "less as written, across the Mediterranean: Actium, 31 BC, in the "
            "Ionian Sea; Alalia off Corsica, 540 BC. North of it, Carlingford "
            "Loch, Ireland, where Norse and Danes fought three days in 852. "
            "A storyguide may invent a battle old enough to be unrecorded, or "
            "drop the water: the mannequin could lie in a regio of huge ice "
            "caves, a Saharan oasis, or the player covenant's best vis source, "
            "if that was claimed after 1098.",
        ),
    )
    b.creature(
        "Genius Loci of the Aquatic Valley",
        page="p. 103",
        realm="Magic",
        might=20,
        form="Aquam",
        season="Summer",
        confidence=(1, 3),
        place=valley,
        block={
            "characteristics": characteristics(1, 1, 0, 1, 1, 1, 1, 1),
            "virtues_flaws": ["Magic Spirit", ("Ways of the {land}", {"land": "Sea"})],
            "traits": {"Grim": 3, "Sensitive to Insult": 1, "Hopeful": -3},
            "abilities": [
                ("Area Lore", 5, "nearby undersea environs"),
                ("Awareness", 5, "submerged humans"),
                ("Bargain", 5, "sahirs"),
                ("Folk Ken", 3, "sailors"),
                ("Guile", 2, "pretending to be mightier than it is"),
                ("Intrigue", 2, "assessing threats"),
                ("Living Language: Greek", 5, "Cypriot"),
            ],
        },
        powers=[
            b.power(
                "Crafter of Water",
                1,
                -4,
                "Aquam",
                does="Variable points. Any non-ritual Creo or Rego Aquam spell "
                "of level 20 or less, one Might point per magnitude. Present "
                "throughout the valley, it can make most effects Personal or "
                "Touch.",
            ),
            b.power(
                "Emissary of Foam and Sand",
                3,
                -3,
                "Aquam",
                does="Aquam and Terram. Shapes within itself a human form of "
                "sand and water that speaks and handles things slowly and "
                "clumsily. Inanimate, it cannot be hurt as a creature can, but "
                "a strong current or a large object disperses it. It may leave "
                "the valley, though the spirit cannot perceive or control it "
                "more than a little way past its borders. (Base 5, +1 Conc, +1 "
                "Part, +1 Rego requisite, Terram requisite free; Lesser Power, "
                "1 Mastery Point to lower Might; cost 20.)",
            ),
            b.power(
                "Master of Water",
                1,
                -4,
                "Aquam",
                does="Variable points. Any non-ritual Muto or Perdo Aquam spell "
                "of level 20 or less, one Might point per magnitude. As Crafter "
                "of Water for Range.",
            ),
            b.power(
                "Presence",
                0,
                0,
                "Imaginem",
                does="Constant. Aware of all that passes in the valley, and "
                "present everywhere in it (Realms of Power: Magic pp. 103, "
                "106).",
            ),
        ],
        vis=[BodyVis(2, "Aquam", "stones buried in the grotto, each year")],
        appearance="The valley itself. Now and then it raises a human shape of "
        "sand and water to speak through, a puppet and nothing more.",
        notes=paragraphs(
            "The Qualities and Inferiorities heading is printed empty, and no "
            "Size is given. It cannot leave the valley. Over fifteen centuries "
            "it has taken the ships in as part of itself, and the ghosts' "
            "endless struggle has soured it: grim and dutiful, it wants the "
            "valley left beautiful and undisturbed forever, with no hope of "
            "anything better. Its vis does not accumulate if left unharvested.",
        ),
        secrets="It cares little for the mannequin. Disturbing the old ships or "
        "destroying the ghosts for good it takes as an attack on itself. If it "
        "hears of such plans it will try to bargain, without much hope, reading "
        "every offer and motive in the bleakest light.",
    )
    b.creature(
        "Ghost of an Ancient Sailor",
        page="p. 102",
        realm="Magic",
        might=10,
        form="Mentem",
        how_many="Dozens",
        age="Appears 16 to 35",
        place=valley,
        block={
            "characteristics": characteristics(0, 1, 1, -1, 1, 2, 1, 1),
            "virtues_flaws": [("Delusion", {"detail": "the battle goes on"})],
            "traits": {"Obsessed with the Battle": 3},
            "abilities": [
                ("Athletics", 2, "climbing"),
                ("Carouse", 2, "drinking songs"),
                ("Dead Language: Ancient Greek or Egyptian", 5, "nautical terms"),
                ("Leadership", 3, "sailors"),
                ("Profession: Fisherman", 4, "net repair"),
                ("Profession: Sailor", 3, "warships"),
                ("Single Weapon", 3, "short sword"),
                ("Thrown Weapon", 3, "javelin"),
            ],
        },
        attacks=[
            b.attack("Sword", 0, 7, 5, 6),
            b.attack("Javelin", -1, 4, 5, 7),
        ],
        soak=4,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        encumbrance="4 (2)",
        powers=[
            b.power(
                "Eidolon",
                0,
                -1,
                "Imaginem",
                does="An illusory image of its former self, moving and speaking "
                "as it directs. It cannot help making one: remade each "
                "morning, lasting until a temporary end in battle or the next "
                "morning (Realms of Power: Magic p. 102).",
            ),
            b.power(
                "Ghost Touch",
                1,
                -1,
                "Terram",
                does="Variable points, Init -1 minus points spent. Moves "
                "objects not held or fastened: 1 point for five pounds, each "
                "further point doubling it. Hurled, Thrown Weapon and +5 damage "
                "a point. It can fight with an object on its usual totals, "
                "though it rarely does, keeping this for handling things "
                "(Realms of Power: Magic p. 102).",
            ),
            b.power(
                "Strike",
                1,
                -5,
                "Terram",
                level=15,
                does="For one Diameter its sword strikes as a material object. "
                "The attack is magical and must penetrate Magic Resistance. "
                "Lesser Power with no direct Hermetic equivalent, treated as "
                "level 15; 2 Mastery Points reduce the cost.",
            ),
        ],
        vis=[],
        equipment="Leather scale armor, short sword, javelins and a sailor's "
        "gear, all insubstantial.",
        appearance="A pale, slightly see-through man in fourth-century BC "
        "armor, desperate and afraid, struggling with enemies who look just "
        "like him.",
        notes=paragraphs(
            "Combat figures apply only if it is made corporeal or uses Strike. "
            "Fights in trained groups of 4, group bonus +12. Veteran is printed "
            "among its Virtues; the catalog lacks it. Decrepitude n/a. "
            + WOUNDS_SIZE_0,
            "It sorts all it meets into ally and enemy, and may change its "
            "mind: a shout of agreement and a salute can make a friend; not "
            "joining its fight, or not answering a question in an ancient "
            "tongue, can make an enemy.",
            "Vis: none in the spirit. When truly destroyed, not merely slain "
            "in the daily battle, 1 pawn of Mentem vis appears in the wreck of "
            "its ship, and the ship mends a little toward what it was before "
            "it sank.",
        ),
    )
    return valley


def _spirits(b: Builder, sanctum: Neighbour) -> None:
    for name, traits in (
        ("Ferox", {"Stubborn": 3, "Surly": 2}),
        ("Fidelius", {"Loyal to House Tremere": 3, "Proud": 2}),
    ):
        b.creature(
            name,
            page="p. 109",
            realm="Magic",
            might=6,
            form="Terram",
            size=-1,
            confidence=(1, 3),
            place=sanctum,
            block={
                "characteristics": characteristics(3, 2, -3, -3, 3, 3, -1, -1),
                "virtues_flaws": ["Educated", "Arcane Lore"],
                "traits": traits,
                "abilities": SPIRIT_ABILITIES,
            },
            attacks=[b.attack("Staff of the Wooden Soldiers", 1, 6, 6, 5)],
            powers=[
                b.power(
                    "Ghostly Hands",
                    0,
                    -1,
                    "Terram",
                    does="Moves objects not held or fastened down; so they work "
                    "the Staves of the Wooden Soldiers.",
                ),
                b.power(
                    "Ghostly Tongues",
                    0,
                    -1,
                    "Imaginem",
                    does="Makes sound as if it had a body with a voice.",
                ),
            ],
            vis=[BodyVis(2, "Terram", "the statue in the sanctum")],
            appearance="Unseen by most. Second Sight or fitting Intellego Vim "
            "shows a small sturdy statue of a man in a wizard's robes.",
            notes=paragraphs(
                "A spirit of the element of Terram (Realms of Power: Magic p. "
                "104), of one of the pair of granite statues in Hermanus' "
                "sanctum; Ferox and Fidelius share one printed block. Immaterial: "
                "they cannot manifest physically. No Soak, Fatigue or Wounds "
                "printed.",
            ),
            secrets=paragraphs(
                "Bound by old agreements with Hermanus to defend the complex, "
                "they know its defenses and devices well. Summoned by the "
                "Statue of Conjured Assistants, they go first to the receiving "
                "room for the Staves, then use the mannequins to carry justiciars "
                "and sentinels about against the intruders, keeping as far from "
                "magi as they can, perhaps slipping outside to act only through "
                "the dolls. If the mannequins of the spare laboratory are "
                "destroyed and they still hold the Staves, they will fetch Arcane "
                "Connections from the store room pair.",
                "In the laboratory proper they find they can trigger the "
                "Butterfly's Gaze and the Tapestry of Confident Possession at "
                "will, and use them to fire any justiciar that helps. Once the "
                "ward against magical creatures is down they might, as a last "
                "resort, use the Helm of Unravelling, but are likelier to teach "
                "its use to any non-magus they think is under the Cross of the "
                "Preempted Conflict (errata p. 79).",
                "They will not die for the laboratory. If destruction can be "
                "avoided only by flight or surrender they do that; if magi "
                "clearly mean to destroy them they leave and go overland to "
                "Coeris to warn the House. That takes a season, with finding "
                "it, drawing notice from outside its Aegis of the Hearth, and "
                "proving their good will. Entering the spare laboratory while "
                "the Hourglass or Prison stands there would trap them.",
            ),
        )


def _mannequin(b: Builder, lab: Neighbour) -> None:
    b.creature(
        "Wooden Mannequin of Coeris",
        page="pp. 109, 112-113",
        how_many="Six in the complex, two each in the store room, spare "
        "laboratory and sanctum; large supplies at Coeris",
        size=0,
        tires=False,
        can_be_wounded=False,
        place=lab,
        block={"characteristics": characteristics(3, 2, -3, -3, 3, 3, -1, -1)},
        attacks=[
            b.attack("Pole Arm", 2, 6, 3, 11),
            b.attack("Crossbow", 4, 4, -1, 7),
        ],
        equipment="Chain hauberks in the store room, full chain in the spare "
        "laboratory; polearms with the House Tremere symbol on the head, "
        "crossbows and bolts.",
        appearance="A human-sized wooden doll, armed and armored, with face "
        "pieces (eyes, nose, lips, brows) pegged in on small dowels.",
        notes="Figures printed for one animated by Ferox or Fidelius; another "
        "holder's Dexterity, Quickness and Abilities apply (Animate Mannequin). "
        "Soak n/a. Not hurt as living beings are, immune to pain and easily "
        "replaced; rules for limbs under the Staff of the Wooden Soldiers, in "
        "the Receiving Room's record.",
    )


def _beasts(b: Builder) -> None:
    b.creature(
        "Large Fish",
        page="p. 105",
        cunning=True,
        block={
            "characteristics": characteristics(-3, -2, -5, -6, 0, 4, 0, -2),
            "virtues_flaws": [
                "Aquatic",
                "Hardy",
                "Herd Animal",
                "Slippery",
                "Thick Fur/Thick Scales",
            ],
            "traits": {"Phlegmatic": 2},
            "abilities": [
                ("Awareness", 2, "food"),
                ("Brawl", 2, "dodge"),
                ("Survival", 3, "home territory"),
                ("Swim", 5, "home territory"),
            ],
        },
        attacks=[
            b.attack("Teeth", -2, 5, 1, 3),
            b.attack("Dodge", -2, None, 2, None),
        ],
        soak=5,
        fatigue_levels=FISH_FATIGUE,
        encumbrance="0",
        appearance="A fish about the size of a person, 80 to 250 pounds.",
        notes="The form given by Cloak of Fins and Scales. Defense +4 with "
        "Teeth and +5 with Dodge against grapples. Confidence 0; a group under "
        "attack gains the Ferocity Virtue, so Confidence 1 (3), but one "
        "attacked alone does not. " + WOUNDS_SIZE_0,
    )
    b.creature(
        "Large Shark",
        page="p. 105",
        size=2,
        cunning=True,
        confidence=(1, 3),
        block={
            "characteristics": characteristics(-3, -2, -5, -6, 4, 4, 1, -3),
            "virtues_flaws": [
                ("Ferocity", {"detail": "attacking prey"}),
                "Improved Characteristics",
                "Greedy (Major)",
                "Wrathful (Major)",
                "Aggressive",
                "Aquatic",
                "Large Teeth",
                "Pursuit Predator",
                "Slippery",
                "Tough Hide",
            ],
            "traits": {"Greedy": 3, "Wrathful": 3, "Phlegmatic": 2},
            "abilities": [
                ("Awareness", 2, "food"),
                ("Brawl", 5, "teeth"),
                ("Hunt", 4, "prey"),
                ("Survival", 3, "home territory"),
                ("Swim", 5, "home territory"),
            ],
        },
        attacks=[
            b.attack("Large Teeth", -3, 11, 8, 7),
            b.attack("Dodge", -3, None, 2, None),
        ],
        soak=6,
        fatigue_levels=FISH_FATIGUE,
        appearance="A shark of Size +2.",
        notes="The form given by Form of the Aquatic Predator. Ferocity lets it "
        "spend Confidence only when attacking prey (Houses of Hermes: Mystery "
        "Cults p. 40). Wounds: -1 (1-7), -3 (8-14), -5 (15-21), Incapacitated "
        "(22-28), Dead (29+).",
    )


def _room(
    b: Builder, lab: Neighbour, name: str, summary: str, secrets: str
) -> Neighbour:
    return b.place(
        f"Laboratory of Hermanus: {name}",
        inside=lab,
        status="Rumoured",
        known="",
        summary=summary,
        secrets=secrets,
    )


def _laboratory(b: Builder, valley: Neighbour) -> None:
    lab = b.place(
        "The Sunken Laboratory of Hermanus",
        inside=valley,
        status="Rumoured",
        known="In the Order",
        summary=paragraphs(
            "A single-story disk of a building some 35 paces across and three "
            "and a half tall, stone-walled and wooden-roofed, shuttered on all "
            "sides, with one door ajar. It sits level on the sea floor, wreck "
            "and shards of lower floors scattered round it, in a sphere of "
            "dry space the water does not enter. Nothing in it has aged a day "
            "since 1098.",
        ),
        secrets=paragraphs(
            "Until the return it lies in the Terram province of the Twilight "
            "Void, tethered to the mannequin and mast in the Aquatic Valley; "
            "the fragments of lower floors hold nothing of value. No aura is "
            "printed for the structure. Seven rooms, each a record here: "
            "hallway, scriptorium and store room on the outer ring; receiving "
            "room, spare laboratory, sanctum (room 6) and laboratory (room 7).",
            "Sentinels and justiciars. Sentinels are devices with Intellego "
            "effects and Herald of Imperative, which fires the justiciars of "
            "the room; justiciars incapacitate. Built for a covenant where "
            "people live, they mostly imprison rather than kill. At Coeris "
            "other devices report any firing, so even one that fails to "
            "penetrate raises the alarm. Many of these "
            "devices are copies of those guarding Coeris.",
            "Herald of Imperative: ReVi 29, 50/day, R: Touch, D: Mom, T: Room. "
            "Performs one fixed triggering action on every object in the room. "
            "(Base 5, +1 Touch, +2 Room; +6 levels 50 uses, +3 levels linked "
            "trigger.) Rego Vim guideline, level 5: activate a device with a "
            "simple trigger, the caster knowing the action; the item fires "
            "directly (p. 107).",
            "The justiciar action. Every justiciar here, and at Coeris, uses "
            "one long, complex action of delicate handling and exact "
            "intonation: three rounds by hand, days of intense study to learn. "
            "It can be written down from the Herald's Lab Texts or by laboratory "
            "investigation of a sentinel or justiciar. The House keeps all "
            "other texts of it in the Coeris vaults; the ones here are the only "
            "others. An outsider who knows it weakens Coeris badly, which is "
            "the House's real concern. The vexillation argued over one action "
            "or many: one was easier to monitor and rearrange, and magi of the "
            "work were vetted by Intellego.",
            "A Modification (Penetration, frequency, triggers, effect use) does "
            "not count toward whether an effect warps its target, so Alarm of "
            "Dissemblance, say, does not (p. 112).",
            "Balance (p. 117; errata p. 78). Challenging, not impossible, "
            "avoiding the trivial and the merely annoying. For impatient or "
            "weaker groups, less active spirits or clues in Amarantha's notes; "
            "for strong ones, more than two elemental spirits, or greater "
            "Might. Players should see that disturbing the rings in the outer "
            "rooms may flood at least those rooms.",
            "Riches (p. 119), besides the devices and the laboratory: 6 pawns "
            "of Rego, 18 of Mentem and 8 of Vim vis. Lab Texts for every "
            "enchantment on the laboratory and every device in it, all "
            "sentinels and justiciars of this chapter, and the Ring and Circle "
            "wards active here, including Circular Ward Against Magical Spirits. "
            "A casting tablet (Covenants pp. 89-90) of Cargo of Angel's Wings, "
            "printed R: Arc, which Hermanus used through a spell like Opening "
            "the Intangible Tunnel to fetch vis and connections from his "
            "mannequin.",
        ),
    )
    _mannequin(b, lab)
    _room(
        b,
        lab,
        "Hallway",
        "A curved passage stripped of the trophies and records that once "
        "praised the Adamant Rook, with a thin rug, a chandelier of half-burnt "
        "candles, and a small table bearing a locked chest with a little marble "
        "statue of a man on it. Four doors. Steel bands run along the outer wall, "
        "and a few inches of sea water cling where it meets floor and ceiling.",
        paragraphs(
            "The doors: north, just under two paces high, to the sea floor, "
            "where water stands like a wall; a like door on the inside wall at "
            "the south end; and at each end a floor-to-ceiling door, flush with "
            "the outer wall so a caster can trace the rings. All but the outer "
            "are locked.",
            "Bands in the hallway, scriptorium and store room hold the outer "
            "wards: Ward Against Water (ReAq 20, cast forcelessly, Houses of "
            "Hermes: True Lineages p. 72, so Penetration 0, and magi and "
            "creatures with Magic Resistance carry their liquids through; "
            "others wet or sweating are slowed as water is stripped off them); "
            "Circular Ward Against Demons, level 40, Penetration 37; Circular "
            "Ward Against Faerie Spirits, level 40, Penetration 35, so Might 34 "
            "or lower. Rings can be reached over the small doors.",
            "Locksmith's Will (sentinel), on the north door: a lead horseshoe, "
            "opened with 6 pawns, filled. Lock Improperly Opened, InTe 29, "
            "constant, R: Touch, D: Sun, T: Room: fires the Herald when a lock "
            "in the room, walls and doors included, is opened without its key, "
            "whether picked, by magic or smashed.",
            "Statue of Conjured Assistants: hand-sized marble, like the statues "
            "in the sanctum. Summon the Stony Servants, ReTe 52, Penetration 8, "
            "6/day, R: Arc, D: Mom, T: Group, Arcane Connections built in: "
            "brings Ferox and Fidelius to the statue. Any improper opening "
            "here does so.",
            "In the locked chest: a silver ring holding 2 pawns of Vim vis.",
        ),
    )
    _room(
        b,
        lab,
        "Scriptorium",
        "Writing desks, quills, parchment and the tools of scribes and "
        "illuminators along the inner wall, with nothing in hand on them. A "
        "tall door at each end; the steel bands and clinging water run on "
        "through.",
        paragraphs(
            "The work in hand was taken away that evening at Hermanus' "
            "request, before he raised his defenses.",
            "Handle of Ill Will (sentinel), on the door to the store room: "
            "opened with 10 pawns, 9 filled. Test of Motive, InMe 60, "
            "Penetration +60, unlimited, R: Touch, D: Mom, T: Ind: whoever "
            "touches the handle, asks whether they wish House Tremere ill "
            "fortune, and fires the Herald if so.",
            "Net of Patient Thieves (justiciar), tied under a desk: a tiny "
            "bronze net, charged, 11 charges, usually hidden so victims cannot "
            "reach it. Elevation of the Interloper, ReCo 65, Penetration +60, "
            "R: Touch, D: Sun, T: Room: all people in the room float a few "
            "inches clear of floor and walls until next dawn or dusk, stuck "
            "unless they can move without touching anything.",
        ),
    )
    _room(
        b,
        lab,
        "Store Room",
        "Full of sweet-smelling smoke that hardly hides anything. Shelves on "
        "the inner wall are packed with laboratory equipment, and among it "
        "stand two wooden mannequins in chain hauberks with polearms and "
        "crossbows. The steel bands and clinging water continue here.",
        paragraphs(
            "Censer of the Unseen (sentinel), rock crystal, on the shelves: "
            "opened with 8 pawns, printed with one pawn free. Room of Pleasant "
            "Incense, CrAu 9, constant, R: Touch, D: Sun, T: Ind: smoke fills "
            "the room but no further, and those with Magic Resistance cannot "
            "smell it. Ascertaining the Absence of Images, InIm 34, constant, "
            "R: Touch, D: Sun, T: Room: fires the Herald if any space holds no "
            "image of smoke or object, as an invisible being does, or if all "
            "the smoke is cleared.",
            "Pebble of the Stone Prison (justiciar), a polished river pebble "
            "on the shelves, lesser device. Box of Stone, CrTe 16, 2/day, R: "
            "Touch, D: Sun, T: Ind: a foot of stone lines floor, walls and "
            "ceiling, between the room and its contents, pushing things a foot "
            "inward; things with Magic Resistance are not moved but left in "
            "holes in the stone. Things fixed to the room stay outside it. "
            "Self-supporting, but its great weight needs footing: a foolish "
            "choice for an upper floor, though the room now rests on the "
            "seabed.",
        ),
    )
    _room(
        b,
        lab,
        "Receiving Room",
        "Chairs, tables and cabinets, where the Adamant Rook once met, and "
        "where Hermanus later saw magi he would not admit further. A copper "
        "bowl and a carved wooden box sit on the middle table, and two staves "
        "tipped with silver eyes lean on the inner wall. The north door bears "
        "the sanctum symbol; a door-sized patch of different stonework marks "
        "the old way to the laboratory.",
        paragraphs(
            "Ferox and Fidelius have likely taken the staves before the party "
            "comes. If either is here it may lie on purpose to spring the room.",
            "Ear of Truth (sentinel), the copper bowl: invested, 10 pawns, "
            "printed filled. Alarm of Dissemblance, InMe 55, Penetration 34, "
            "unlimited, R: Touch, D: Diam, T: Room: fires the Herald on any "
            "lie told here. The limit of the Infernal keeps it from working on "
            "demons.",
            "Box of Vines (justiciar), a carved box the size of a loaf, lesser "
            "device. Chamber of Thorns, CrHe 16, 2/day, R: Touch, D: Sun, T: "
            "Group: in a flash, thorny bushes fill the room, around all within. "
            "Soak +15; only edged weapons cut them, a Heavy wound a pace. "
            "Forcing through: Strength stress roll, Ease Factor 9 a pace, "
            "+15 damage either way, 5 more on a botch.",
            STAFF,
            "These two staves hold the right ears of the spare laboratory's "
            "mannequins.",
        ),
    )
    _room(
        b,
        lab,
        "Spare Laboratory",
        "Hermanus' workroom while the vexillation lasted, left for the larger "
        "room when it ended. A table holds an hourglass of crystal and "
        "limestone and a silver candlestick. Two wooden mannequins in full "
        "chain stand ready with polearms and crossbows, each missing its right "
        "ear.",
        paragraphs(
            "Hourglass of Airy Trespass (sentinel): opened with 11 pawns. Sense "
            "the Airy Trespass, InVi 50 (errata p. 78; printed 75), Penetration "
            "+32, constant, R: Touch, D: Sun, T: Room: fires the Herald every "
            "round a being of Magic Might 31 or lower is present. The book says "
            "the two effects fill the 11 pawns; that was before the correction.",
            "Prison of Audacious Spirits (justiciar), the candlestick, so named "
            "on p. 113 though once called Prison of Insubstantial Spirits: "
            "charged, 7 charges. Insubstantial Prison, ReVi 71, Penetration 30, "
            "R: Touch, D: Sun, T: Room: creatures of Magic Might 30 or less "
            "cannot cross the room's bounds, nor can their powers, until it "
            "ends or is dispelled. Not limited to spirits.",
        ),
    )
    sanctum = _room(
        b,
        lab,
        "Sanctum",
        "The door opens on a wall of wood, flush with the frame, dented where "
        "the handle sat. Cleared, the room is richly furnished: fine tapestries, "
        "a bed, a dresser, a desk, and two foot-and-a-half granite statues of "
        "men. Two wooden mannequins stand by.",
        paragraphs(
            "Charm of the Herbam Padlock, a small silver ring on the floor by "
            "the laboratory door, where Hermanus left it: opened with 6 pawns, "
            "filled, made for the Coeris vaults, kept active there. Chamber of "
            "Heartwood, CrHe 29, constant, R: Touch, D: Sun, T: Ind: one block "
            "of wood fills the room, snug round its contents, on touching the "
            "door with the charm. Insubstantial Wooden Foundation, ReHe 24, "
            "constant, R: Touch, D: Sun, T: Ind: holds the block and keeps its "
            "weight off the floor.",
            "Two sentinels and one justiciar. Drawing a metal weapon without "
            "the House Tremere symbol, or touching the carpet while believing "
            "the House would disapprove of one's plans, fires the turtle.",
            "Ward against Foreign Steel (sentinel), a marble apple behind a "
            "chest by the bed: 8 pawns, filled. React to Naked Blades, InTe(Im) "
            "45, Penetration 42, constant, R: Touch, D: Sun, T: Room. Coeris "
            "grogs carry marked weapons, but visiting Tremere have had "
            "accidents.",
            "Carpet of Loyalty (sentinel), under the desk: an embroidered square "
            "rug about 2 paces across, showing Tremere and Guernicus, silver "
            "wires in the border; 9 pawns, filled. Interrogation of Interlopers, "
            "InMe 60, Penetration +60, unlimited, R: Touch, D: Mom, T: Ind: "
            "asks whoever touches it if the House's members would disapprove "
            "of their plans. Those with no idea what the Tremere think do not "
            "fire it.",
            "Turtle of Welcome Reflection (justiciar), a jet figurine in the "
            "northwest corner: charged, 11 charges. Armoring the Intruder, "
            "MuCo(An) 60, Penetration +50, R: Touch, D: Sun, T: Room: humans "
            "and others subject to Corpus spells become turtles until next "
            "sunrise or sunset.",
            "Oracle-Countering Tapestry, on the wall right of the door from the "
            "receiving room, lesser device, one of several copies. Masking the "
            "Magical Chamber, PeVi 45, constant, R: Touch, D: Sun, T: Room: "
            "Hermetic Intellego Vim cannot detect magic here below level 53.",
            "This third pair of mannequins is out of the spirits' reach until "
            "the block is gone, and even then they must get Arcane Connections "
            "to the staves.",
        ),
    )
    _spirits(b, sanctum)
    _room(
        b,
        lab,
        "Laboratory",
        "A tapestry hangs just past the door. Behind it a deep workbench runs "
        "round half the circular room, shelved to the ceiling with carpenters' "
        "and jewelers' tools. Eight rings of metal, stone and brick are set in "
        "the floor behind it. In the middle stand tables of equipment, a desk "
        "and many tomes of notes, and on one table a silver-eyed staff and a "
        "small wooden doll. The plaster ceiling shows the night sky reversed, "
        "black stars on white, and brass wires carry hooked spheres marked for "
        "the planets.",
        paragraphs(
            "Rings: Circular Ward Against Demons, level 40, Penetration 35; Ring "
            "of Warding Against Spirits, level 30, Penetration 40; Circular "
            "Ward Against Magical Spirits, level 40, Penetration 36; Circular "
            "Ward Against Faerie Spirits, level 40, Penetration 37; Ward Against "
            "Faeries of the Water, level 25, Penetration 30; Ward Against the "
            "Beasts of Legend, level 30, Penetration 30; Circle of Beast "
            "Warding; Ward Against Water.",
            "As a laboratory (Covenants chapter nine): Size +1, Refinement +6, "
            "and when working General Quality +3, Upkeep +4, Aesthetics +5, "
            "with +6 item creation, +1 texts, +1 Intellego, +1 Imaginem. "
            "Virtues: Greater Feature (workbench), Lesser Feature (ceiling), "
            "Greater Expansion, Highly Organized, Superior Lighting (the Orb). "
            "A Laboratory record needs a covenant, so it is kept here in words.",
            "Staff of the Wooden Soldiers: as in the Receiving Room; this one "
            "holds a connection to the remains of the sea-floor mannequin. The "
            "doll is a fixed Arcane Connection to that mannequin.",
            "Tapestry of Confident Possession (sentinel), silver-ornamented, "
            "covering about a third of the walls, so that entering or reaching "
            "many cabinets and books means moving it: invested, 16 pawns, 10 "
            "filled. Assurance of Ownership, InMe 65, Penetration 50, unlimited, "
            "R: Touch, D: Mom, T: Room: on moving it, fires the Herald if any "
            "mind present does not believe the laboratory is its own.",
            "Cross of the Preempted Conflict (justiciar), a small metal cross: "
            "charged, 13 charges. Beneficent Gift of Loyalty, ReMe 65, "
            "Penetration +40, R: Touch, D: Sun, T: Room: those present must do "
            "all they can to guard the laboratory, its contents and above all "
            "its rightful owners. Who those are is now arguable; Ferox and "
            "Fidelius will say House Tremere, and the characters may differ. "
            "None under it will let anything be taken from the complex. The "
            "vexillation hoped thieves would give themselves up.",
            "Butterfly's Gaze, a six-inch silver butterfly with ivory inlay on "
            "the wall: invested, 15 pawns. Gaze of Maker's Mark, InVi 49, "
            "constant, R: Touch, D: Sun, T: Room: seeks magic without Hermanus' "
            "sigil, the embattled lines. Counter Intruding Magics, PeVi 63, "
            "unlimited, R: Special, D: Mom, T: Ind: dispels it if its level "
            "doubled is met by stress die + 55, once a round, target chosen at "
            "random, when a targeted spell enters or is cast. A Momentary spell "
            "may take effect first.",
            "Wolf's Gaze, a six-inch silver wolf's head on the wall: invested, "
            "6 pawns, 5 filled. Awareness of Fire, InIg 14, constant, R: Touch, "
            "D: Sun, T: Room: triggers Protection of Cool and Dark, PeIg 28, "
            "unlimited, R: Touch, D: Mom, T: Room, putting out fires of +5 "
            "damage per exposure or less (ArM5 p. 181).",
            "Orb of Obedient Sunlight, a gold-colored wooden sphere on the "
            "wires, lesser device. Obedient Sunlight, CrIg 20, unlimited, item "
            "maintains concentration, R: Per, D: Conc, T: Ind: bright light on "
            "command, against fire and open windows.",
            "Helm of Unravelling, a steel helmet, 12 pawns, for grogs to break "
            "enemy magic; Coeris's trusted grogs carry but rarely wear them, "
            "for Sight of Forming Spells warps. Sight of Forming Spells, InVi "
            "60, Penetration +32, constant, R: Touch, D: Sun, T: Vision: magic "
            "shows as a violet glow, strongest in casting, not old residues. "
            "Shout of Unravelling, PeVi 60, Penetration +32, 12/day, R: Voice, "
            "D: Mom, T: Ind: shouted while staring at a power or effect; "
            "dispels if its level doubled is met by stress die + 50, and can "
            "counter a spell cast later in the round. Neither works past Magic "
            "Resistance it does not penetrate.",
            "On the room itself. Opened by Hermanus in its walls with 20 pawns, "
            "15 filled. Foreboding of Stones, InTe 19, constant, R: Pers, D: "
            "Sun, T: Hearing: senses a solid thing about to strike hard enough "
            "to do damage, and triggers Skin of the Sapphire Tortoise, MuTe(He) "
            "35, unlimited, R: Pers, D: Diam, T: Room: walls, floor or ceiling "
            "as hard as gemstone and tough as iron. Protection of the Mason's "
            "Vision, ReTe(He) 28, unlimited, R: Pers, D: Mom, T: Special: "
            "puts back any part of the structure removed, up to 5 paces out; "
            "rubble cannot reassemble. Invisible Eye Uncovered, InVi(Im) 45, "
            "constant, R: Pers, D: Sun, T: Room: shows any magical spying of "
            "up to level 52 as a flickering image in the room.",
        ),
    )


def _remains(b: Builder) -> None:
    b.place(
        "The Remains of Amarantha",
        status="Rumoured",
        known="",
        summary=paragraphs(
            "Old bones and a large leather satchel, the one thing about them "
            "untouched by decay. Within: an apple, cheese and bread, and a "
            "bundle of notes.",
            "The book leaves the place open: somewhere remote that might hold "
            "vis, such as a regio, wilderness that could host a vis site, or "
            "what might have been a creature of might's lair in Hermanus' day. "
            "It can be worked into another adventure of the saga.",
        ),
        secrets=paragraphs(
            "The satchel (p. 100): a lesser enchanted device of Amarantha's "
            "own. Enchantment of Incorruptible Vellum, CrAn(He) 24, constant, "
            "R: Touch, D: Sun, T: Group: guards it and its animal and plant "
            "contents from natural decay. Long exposure has warped satchel and "
            "contents: the food cannot be digested and sickens anyone who "
            "tries it, and bare skin that touches leather or notes takes a "
            "mild rash.",
            "The notes take about a day to read. They say who she was and what "
            "she was about; sum up Hermanus' life and habits; tell of the "
            "mannequin, a fixed Arcane Connection, sent about the world and "
            "run by spells through Opening the Intangible Tunnel; say the "
            "laboratory surely held much vis, and that the House badly wants "
            "the texts and devices for what they reveal of Coeris's defenses; "
            "and give a part-checked list of sites.",
            "The list is long, but a century of Hermetic work has ruled out "
            "most of it. Checked against House Mercere's lists of covenants "
            "and claimed vis sources it falls to a short list, or to the true "
            "site alone, as the storyguide wishes.",
        ),
    )


def _stories(b: Builder, valley: Neighbour) -> None:
    dormant(
        b.threat(
            "The Search for the Sunken Laboratory",
            place=valley,
            antagonist="Hermanus' defenses, and the sea",
            summary=paragraphs(
                "A dead Tremere's satchel points to the lost wing of Coeris: a "
                "hoard of vis and devices, if it can be found, raised and "
                "entered.",
            ),
            stages=[
                S(
                    "Amarantha's notes",
                    at=1,
                    clues="The characters come on her remains and satchel, "
                    "best within another adventure (The Remains of Amarantha; "
                    "the place is left to the storyguide). Her list of sites "
                    "shrinks against House Mercere's records.",
                ),
                S(
                    "The sea floor off Crete",
                    at=2,
                    clues="After perhaps trying other sites, they reach the "
                    "Aquatic Valley and the trials of working under water.",
                ),
                S(
                    "The valley's guardians",
                    at=3,
                    clues="The genius loci guards the ships and ghosts, and "
                    "the ghosts take newcomers for friend or foe.",
                ),
                S(
                    "The laboratory returns",
                    at=4,
                    clues="A spell on the mannequin or mast brings the "
                    "structure back. Inside, they must outwit its seven rooms "
                    "of defenses and Ferox and Fidelius to reach the treasure.",
                ),
                S(
                    "Bargaining with the House",
                    at=5,
                    clues="They deal with House Tremere over the devices and "
                    "secrets: see The Secrets of Coeris.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Secrets of Coeris",
            place=valley,
            antagonist="House Tremere",
            summary=paragraphs(
                "House Tremere holds the laboratory, its texts and its devices "
                "to be its own, made for it with its resources; only the vis it "
                "leaves out of the claim. Getting them back matters far less "
                "to it than keeping its designs and triggering action secret.",
            ),
            stages=[
                S(
                    "The House hears",
                    at=1,
                    clues="Ferox or Fidelius tells it; a Tremere who knows the "
                    "defenses spots or hears of a text or device; or the "
                    "characters let it slip.",
                ),
                S(
                    "Negotiation",
                    at=2,
                    clues="Legal argument over ownership, with tempting offers "
                    "of books and vis. No threat of immediate Wizard's War, for "
                    "fear frightened magi publish.",
                    ignored="The House makes life extremely hard for them until "
                    "they deal, keeping the means vague; Wizard's War is "
                    "implied only if they spread the secrets.",
                    stopped="It pays any reasonable price, which can be high, "
                    "but must rebuild Coeris's defenses anyway and buys time "
                    "rather than trust.",
                ),
                S(
                    "Forgetting and testimony",
                    at=3,
                    clues="It wants the triggering action gone from unwanted "
                    "minds, by Scraping Razor of Memory, spontaneous and "
                    "perhaps non-fatiguing with Ceremonial Casting (Houses of "
                    "Hermes: Societates p. 59). Before paying it asks each "
                    "party to testify to a Tremere Mentem expert or a neutral "
                    "Quaesitor, under Frosty Breath of the Spoken Lie or Ear of "
                    "Truth (Houses of Hermes: True Lineages p. 73), with checks "
                    "for tampering such as Sight of the Active Magics. It must "
                    "be voluntary, and the House will submit to like questions "
                    "to prove its intent. It will ask if they know the secret, "
                    "planned to recover it, know who else has it, and how they "
                    "would have cheated.",
                    stopped="If all pass, the House thinks it has time to "
                    "overhaul the defenses with care, and keeps its bargain.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Trojan Clothes Horse",
            antagonist="A summoned spirit or creature of might",
            summary="The characters find something once a Tremere magus's, "
            "perhaps robes. The House would like the finder to bring it to "
            "Coeris and tell how it was found, for a reward that barely pays "
            "the trip.",
            secrets=paragraphs(
                "The item holds a Waiting Spell, perhaps hidden by Masking the "
                "Odor of Magic, that wakes inside Coeris and summons a strong "
                "being bent on all the harm it can do. It appears among the "
                "characters, who may not be taken for bystanders. They, it and "
                "the defenders chase one another through the sentinels and "
                "justiciars.",
                "Outside the vaults these devices are built to delay, hold and "
                "above all raise the alarm, and several in Coeris locate any "
                "that fire. A raid on the vaults themselves is no fit story: "
                "the defenses, the House's resolve and the Order all stand "
                "against it (p. 98).",
            ),
        )
    )
    dormant(
        b.threat(
            "Unexpected Copies",
            antagonist="Whatever dwells there",
            summary="A magus has found a Vestige in the Magical Realm very like "
            "Coeris, and roughly set down how he reached it. The characters may "
            "retrace his way, to see if it holds like riches or like "
            "inhabitants.",
        )
    )
    dormant(
        b.threat(
            "Dispatched",
            antagonist="A regio's inhabitants",
            summary=paragraphs(
                "The House may arm its magi from these devices at need, so the "
                "characters can meet them away from Coeris. A Tremere maga with "
                "mundane helpers has gone into a regio for vis, nearer the "
                "characters' covenant than any other, and roused its "
                "inhabitants (fire spirits, demons, great clever spiders, as "
                "suits the saga). Defending her people she fell into Twilight. "
                "Her familiar escapes to the covenant to beg for rescue.",
            ),
            secrets="The rescuers face both the inhabitants and the maze of "
            "sentinels and justiciars the trapped party has set up to protect "
            "itself.",
        )
    )


def build(b: Builder) -> None:
    _people(b)
    valley = _valley(b)
    _laboratory(b, valley)
    _beasts(b)
    _remains(b)
    _stories(b, valley)
