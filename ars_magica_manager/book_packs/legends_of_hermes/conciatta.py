"""The Four Aspects of Conciatta, in paraphrase of Legends of Hermes,
chapter two (pp. 12-45): the legend of Conciatta of Bonisagus and Currito of
Jerbiton; the four tempora of her life; the four Iberian cities and the
sites beyond them where her sundered spirit waits (La Torre no Vista, the
Convento de San Ildefonso, Tartessos and the Narixa caves); the four
aspects and those around them; and the story of the hunt, dormant until the
storyguide begins it.

The chapter's new Virtues, Flaw, spells and guidelines (pp. 14-18) are in
the catalogs and rules already, and are cited here, not repeated. Books,
Lab Texts and devices are in the words of whoever holds them, since a Book
record needs a covenant. The aspects are creatures, as Might-bearing
spirits; the book prints them no Arts. Stat blocks are the book's; the rest
is a summary, not its words."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Creature, CreaturePower, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    joined_lines,
    paragraphs,
    secrets,
    titled,
    vf_ability,
    vf_great,
    vf_puissant,
    wound_ranges,
)

BONISAGUS = "house_bonisagus"
JERBITON = "house_jerbiton"
KNOWN: dict[str, Any] = {"status": "Known", "known": "In the region"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
LOOKS = "Appears in her late thirties"
ACCLAIM = {"Bonisagus House Acclaim (Magi Bonisagi)": 3}
S = Builder.stage

CONCIATTA_CHARACTERISTICS = characteristics(4, 0, -1, 1, -1, -1, 0, 0)

#: What the Magical and Infernal aspects both carry.
CONCIATTA_VIRTUES: list[Any] = [
    "Magic Spirit",
    "Hermetic Magus",
    ("Major Magical Focus", {"focus": "Auras"}),
    "True Understanding of the Realms",
    vf_ability("Affinity with {ability}", "Magic Theory"),
    "Confluence of the Realms",
    "Famous",
    vf_great("Intelligence"),
    "Insight of the Realms",
    "Inventive Genius",
    vf_puissant("Magic Theory"),
    ("Student of {realm}", {"realm": "Infernal"}),
    "Well-Traveled",
    "Blatant Gift",
    "The Constant Expression",
    ("Driven (Major)", {"detail": "extend Hermetic Theory"}),
    (
        "Deleterious Circumstances",
        {"circumstance": "when not within a supernatural aura"},
    ),
    "Judged Unfairly",
    "Study Requirement",
]

#: The Magical and Infernal aspects' Abilities, and the Faerie aspect's
#: Pretenses.
CONCIATTA_ABILITIES: list[tuple[str, int, str]] = [
    ("Animal Handling", 2, "owls"),
    ("Living Language: Arabic", 4, "poetry"),
    ("Area Lore: Qadis", 2, "ghostly personalities"),
    ("Area Lore: Zaragoza", 3, "lacunae"),
    ("Area Lore: Narixa", 2, "regiones"),
    ("Area Lore: Toledo", 2, "the convent"),
    ("Artes Liberales", 3, "ceremonial magic"),
    ("Awareness", 2, "spell effects"),
    ("Living Language: Aragonese", 4, "poetry"),
    ("Charm", 2, "first impressions"),
    ("Code of Hermes", 1, "Bonisagus obligations"),
    ("Concentration", 3, "lab work"),
    ("Dominion Lore", 5, "divine places"),
    ("Etiquette", 2, "faeries"),
    ("Faerie Lore", 5, "ancient faeries"),
    ("Finesse", 2, "precision"),
    ("Folk Ken", 2, "magi"),
    ("Infernal Lore", 5, "regiones"),
    ("Intrigue", 1, "House Bonisagus"),
    ("Dead Language: Latin", 5, "Hermetic usage"),
    ("Leadership", 1, "laboratory work"),
    ("Organization Lore: La Torre no Vista", 3, "history"),
    ("Magic Lore", 5, "regiones"),
    ("Magic Theory", 15, "Vim"),
    ("Organization Lore: Order of Hermes", 2, "history"),
    ("Parma Magica", 2, "Vim"),
    ("Penetration", 2, "Vim"),
    ("Philosophiae", 3, "ceremonial magic"),
    ("Teaching", 3, "Magic Theory"),
]

REMEMBERED = [
    titled(
        "What all know of Conciatta",
        "Ease Factor 0, Known by All: she brought the four realms under the "
        "single Art of Vim; apprentices often study her The Application of Vim "
        "to the Supernatural Humors; she left Hermetic society in later life.",
    ),
    titled(
        "What is widely known of Conciatta",
        "Ease Factor 6, Widely Known: she lived in Iberia, with ties to "
        "Christian and Muslim communities alike; her parens was marched for "
        "diabolic corruption; her husband, a Jerbiton artist, aided her work.",
    ),
    titled(
        "Uncommon knowledge of Conciatta",
        "Ease Factor 12, Uncommon Knowledge: some hold she kept part of her "
        "research from the Order; she overcame the Dominion's effect on magic "
        "(false: a distortion grown from Currito's later writings); she "
        "vanished into Twilight before the turn of the millennium (what the "
        "Order at large believes, and false).",
    ),
    titled(
        "Conciatta's lost secrets",
        "Ease Factor 18, Lost Secrets: the hubris of her research cost her "
        "control of her magic; she died in a convent near Toledo; shortly "
        "before her death four women came to her, and she gave each a magical "
        "treasure.",
    ),
]
REMEMBERED_NOTES = (
    "What the Order Remembers (p. 14; rule pp. 10-11): Intelligence + Order "
    "of Hermes Lore simple roll; the character recalls everything up to the "
    "Ease Factor reached. Bonisagi add +3, for her rank of Cannophori "
    "(Houses of Hermes: True Lineages p. 21). Research in a fit library: "
    "Covenants p. 98."
)

ARTIFACTS = joined_lines(
    "List of Artifacts (p. 18), with integration or breakthrough points:",
    "Confluence of the Realms: Maintaining the Unstable Conjuration 6, The "
    "Fourfold Lens 11, Subsume the Apparent Dominion 10.",
    "Insight of the Realms: Clearing the Mind of the Caster 6, The Insightful "
    "Stylus 5, The Lodestone 7, The Sands of Time 4.",
    "True Understanding of the Realms: Ward Against Woodland Spirits 9.",
    "The table calls the first Maintaining the Divine Conjuration; p. 30 "
    "prints it as Maintaining the Unstable Conjuration.",
)

REYES: StatBlock = {
    "characteristics": characteristics(1, 0, 2, 1, 0, 0, 0, -1),
    "apparent_age": 35,
    "confidence": (1, 3),
    "virtues_flaws": [
        "Capo",
        "Clear Thinker",
        "Famous",
        "Educated (Vernacular)",
        vf_puissant("Bargain"),
        "Gossip",
        "Many Marriageable Daughters",
        "Weak Characteristics",
        "Greedy (Minor)",
        ("Weakness (Minor)", {"detail": "Hedonism"}),
    ],
    "traits": {"Bombastic": 2, "Greedy": 2, "Tolerant of Fools": -1},
    "reputations": {"Generous Host (merchants)": 4, "Gossip (Zaragoza)": 1},
    "abilities": [
        ("Living Language: Arabic", 4, "Zaragoza"),
        ("Area Lore: River Ebro", 3, "geography"),
        ("Area Lore: Zaragoza", 4, "personalities"),
        ("Artes Liberales", 1, "arithmetic"),
        ("Awareness", 1, "alertness"),
        ("Dead Language: Latin", 3, "trade usage"),
        ("Bargain", 3, "wine"),
        ("Brawl", 1, "bludgeon"),
        ("Carouse", 3, "drinking songs"),
        ("Living Language: Aragonese", 5, "Zaragoza"),
        ("Charm", 3, "being witty"),
        ("Etiquette", 3, "mercantile dealings"),
        ("Folk Ken", 4, "strangers"),
        ("Guile", 4, "lying to strangers"),
        ("Leadership", 4, "workers"),
        ("Profession: Merchant", 4, "wine"),
        ("Music", 2, "flute"),
        ("Ride", 2, "distance"),
        ("Organization Lore: Reyes' Company", 2, "personalities"),
        ("Teaching", 1, "Profession: Merchant"),
    ],
    "notes": paragraphs(
        "A big man fond of too much food and drink, round and ruddy in the "
        "face, his black hair thinning. He dresses to show what he is worth, "
        "as a man of his standing should. Merchant clothing.",
        "Combat: dodge Init -1, Defense +0; fist Init -1, Attack +1, Defense "
        "+0, Damage +0; bludgeon Init -2, Attack +4, Defense +1, Damage +2. "
        "Soak 0. Fatigue OK, 0, -1, -3, -5, Unconscious. Wound penalties: -1 "
        "(1-5), -3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+).",
        "Capo, Many Marriageable Daughters and Vernacular Education are from "
        "City & Guild pp. 108-109; the catalog has the last as Educated "
        "(Vernacular). His Weakness is Hedonism. LoH p. 24.",
    ),
}

PRUDENCIA: StatBlock = {
    "characteristics": characteristics(2, 1, 0, 1, -1, 1, 0, -1),
    "apparent_age": 45,
    "confidence": (1, 3),
    "virtues_flaws": [
        "Senior Clergy",
        "Clear Thinker",
        "Educated",
        vf_puissant("Leadership"),
        "Relic",
        "Monastic Vows",
        "Poor",
        "Weak Characteristics",
    ],
    "traits": {"Contempt for Men": 2, "Prickly": 3, "Compassionate": 1},
    "reputations": {
        "Abbess of a convent in need of money (Toledo)": 4,
        "Aloof (Toledo)": 2,
        "Strict (convent)": 3,
    },
    "abilities": [
        ("Living Language: Arabic", 2, "markets"),
        ("Area Lore: Toledo", 3, "people of the Church"),
        ("Artes Liberales", 2, "rhetoric"),
        ("Awareness", 3, "things being out of place"),
        ("Living Language: Castilian", 5, "commerce"),
        ("Chirurgy", 3, "minor wounds"),
        ("Church Lore", 4, "Toledo"),
        ("Concentration", 1, "accounts"),
        ("Etiquette", 3, "wealthy visitors"),
        ("Folk Ken", 4, "men"),
        ("Dead Language: Latin", 4, "church ceremonies"),
        ("Leadership", 5, "novices"),
        ("Medicine", 3, ""),
        ("Profession: Scribe", 1, "copying"),
        ("Teaching", 3, "theology"),
        ("Theology: Christian", 4, "psalms"),
    ],
    "notes": paragraphs(
        "She strides about her convent with complete authority and a "
        "withering look, straight of neck and back, eyebrows raised, hands "
        "clasped, her eyes always finding some fault. Two novices follow her "
        "and do as she bids.",
        "Combat: dodge Init -1, Defense -1; fist Init -1, Attack +0, Defense "
        "-1, Damage -1. Soak +1. Fatigue OK, 0, -1, -3, -5, Unconscious. "
        "Wound penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
        "(16-20), Dead (21+).",
        "Magic Resistance 10, from her relic. Clear Thinker gives +3 to resist "
        "lies, confusion and subterfuge. Senior Clergy is from Realms of "
        "Power: The Divine p. 93. LoH p. 29.",
    ),
}

IMMACULADA: StatBlock = {
    "characteristics": characteristics(1, 2, 0, 0, 0, 0, 2, 0),
    "apparent_age": 17,
    "warping": (1, 5),
    "virtues_flaws": [
        "Peasant",
        "Sense Holiness and Unholiness",
        vf_puissant("Sense Holiness and Unholiness"),
        "Enfeebled",
        "Plagued by Supernatural Entity",
        "Monastic Vows",
        "Visions",
    ],
    "traits": {
        "Fearful of being alone": 3,
        "Confident": -2,
        "Strong-Willed": -1,
    },
    "abilities": [
        ("Artes Liberales", 1, "music"),
        ("Music", 1, "sing"),
        ("Church Lore", 1, "the convent"),
        ("Profession: Scribe", 1, "copying"),
        ("Chirurgy", 2, "minor wounds"),
        ("Living Language: Castilian", 5, "poetry"),
        ("Charm", 2, "first impressions"),
        ("Concentration", 2, "prayers"),
        ("Profession: Farmer", 2, "almonds"),
        ("Folk Ken", 2, "clergy"),
        ("Sense Holiness and Unholiness", 4, "the unseen"),
        ("Dead Language: Latin", 4, "church ceremonies"),
        ("Swim", 1, "short distances"),
        ("Theology: Christian", 3, "biblical knowledge"),
    ],
    "notes": paragraphs(
        "A small girl of seventeen, pale and tear-streaked, her eyes red with "
        "crying. Her hair is shorn and her habit has given way to a dirty "
        "white smock and cap; her nails are picked and bitten raw. Chalk "
        "covers her fingers, face and clothes.",
        "Combat: dodge Init +0, Defense +0; fist Init +0, Attack +2, Defense "
        "+0, Damage +0. Soak 0. Fatigue OK, 0, -1, -3, -5, Unconscious. Wound "
        "penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated (16-20), "
        "Dead (21+).",
        "Confidence: none. Enfeebled and Visions are imposed by the spirit "
        "within her; the rest of the block is the girl as she should be. "
        "She rarely sleeps, so is always at a -3 Fatigue penalty. Her "
        "Warping is Divine. LoH p. 31.",
    ),
}

HABIB: StatBlock = {
    "characteristics": characteristics(2, 0, 0, 2, -2, -1, -1, -1),
    "apparent_age": 45,
    "confidence": (1, 3),
    "virtues_flaws": ["'Alim", "Educated", "Arcane Lore", "Poor"],
    "traits": {"Inquisitive": 2, "Humble": 1, "Persistent": 1},
    "abilities": [
        ("Living Language: Arabic", 5, "Qadis"),
        ("Art of Memory", 2, "academic texts"),
        ("Artes Liberales", 5, "astronomy"),
        ("Awareness", 2, "searching"),
        ("Area Lore: Qadis", 3, "geography"),
        ("Concentration", 3, "reading"),
        ("Dominion Lore", 1, "auras"),
        ("Faerie Lore", 2, "auras"),
        ("Folk Ken", 2, "townsfolk"),
        ("Dead Language: Greek", 3, "ancient texts"),
        ("Infernal Lore", 2, "auras"),
        ("Islamic Law", 4, "Ijma'"),
        ("Dead Language: Latin", 3, "academic usage"),
        ("Magic Lore", 2, "auras"),
        ("Philosophiae", 5, "metaphysics"),
        ("Profession: Scribe", 3, "copying"),
        ("Teaching", 4, "Artes Liberales"),
        ("Theology: Islam", 4, "Sunni"),
    ],
    "notes": paragraphs(
        "A small wiry man, gray of hair and beard, with a large nose and a "
        "brow creased by thought and worry. His clothes are threadbare, "
        "since what money he has goes on his studies. He carries slates and "
        "chalk, quill, ink and parchment.",
        "Combat: dodge Init -1, Defense -1; fist Init -1, Attack -1, Defense "
        "-1, Damage -2; bludgeon Init -2, Attack +1, Defense -1, Damage +0. "
        "Soak -1. Fatigue OK, 0, -1, -3, -5, Unconscious. Wound penalties: "
        "-1 (1-5), -3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+).",
        "'Alim is from Realms of Power: The Divine p. 114. The block spells "
        "his Area Lore Cadis Lore; the same city. LoH p. 34.",
    ),
}

HAMID: StatBlock = {
    "characteristics": characteristics(2, -1, 0, 2, -1, 0, 0, 0),
    "apparent_age": 55,
    "confidence": (1, 3),
    "virtues_flaws": [
        "'Alim",
        "Intuition",
        "Sharp Ears (Minor)",
        "Palsied Hands",
        "Visions",
        "Weak Characteristics",
    ],
    "traits": {"Good-natured": 2, "Knowing": 2},
    "reputations": {"Librarian (imams)": 3},
    "abilities": [
        ("Living Language: Arabic", 5, "religious use"),
        ("Artes Liberales", 5, "logic"),
        ("Awareness", 2, "searching"),
        ("Brawl", 1, "fist"),
        ("Charm", 5, "invoking baraka"),
        ("Concentration", 4, "reading"),
        ("Dominion Lore", 2, "holy forebearers"),
        ("Folk Ken", 5, "nobles"),
        ("Guile", 2, "lying to authority"),
        ("Infernal Lore", 2, "auras"),
        ("Intrigue", 3, "alliances"),
        ("Islamic Law", 4, "Narixa customs"),
        ("Leadership", 2, "within the mosque"),
        ("Profession: Librarian", 5, "forgotten scrolls"),
        ("Music", 3, "calling to prayer"),
        ("Area Lore: Narixa", 4, "legends"),
        ("Philosophiae", 4, "metaphysics"),
        ("Teaching", 4, "theology, Islamic"),
        ("Theology: Islam", 6, "prophets"),
    ],
    "notes": paragraphs(
        "A small aging man with a gray beard, eyes narrowed from squinting "
        "and a toothless smile. Dust seems to find his turban and robes, and "
        "his library has plenty to spare.",
        "Combat: fist Init -2, Attack +0, Defense +0, Damage -1. Soak 0. "
        "Fatigue OK, 0, -1, -3, -5, Unconscious. Wound penalties: -1 (1-5), "
        "-3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+).",
        "'Alim, Islamic Law and Theology: Islam are from Realms of Power: The "
        "Divine. LoH p. 40.",
    ),
}


def _sites(b: Builder) -> dict[str, Neighbour]:
    """The tempora, then the four cities with what lies in or beyond them."""
    sites: dict[str, Neighbour] = {}
    for key, name, trait, words, hidden in (
        (
            "study",
            "The Vestige of Study",
            "Studious",
            "Conciatta's sanctum, rich and thriving, stopped in the middle of "
            "a talk: Currito leans forward in a great chair, hands shaping "
            "something in the air, and she stands at her work table with a "
            "finger on a line of an open book. Shelves of texts and devices "
            "line the walls. The window shows Moorish Saraqusta and the Noor "
            "Mosque, like a painting hung a few feet beyond the frame, and "
            "only from where she stands.",
            [
                titled(
                    "The open book",
                    "The open book in the Vestige of Study is the journal of an "
                    "unnamed magus thrown by accident into a regio that stifled "
                    "his magic, who broke out by spending all his vis; the line "
                    "under Conciatta's finger says all of it was Vim vis.",
                ),
                titled(
                    "The archaic tractatus",
                    "A tractatus on Vim in archaic Hermetic Latin lies beside "
                    "the open book, arguing that the realms could only be "
                    "touched by new Arts, which any magus now sees is absurd. "
                    "The pages cannot be turned.",
                ),
                titled(
                    "The way out of the Vestige of Study",
                    "The door is the way in and out.",
                ),
            ],
        ),
        (
            "acclaim",
            "The Vestige of Acclaim",
            "Proud",
            "A great lecture hall of Durenmar, which a Bonisagus knows at "
            "once. Benches of magi of several Houses face a dais where "
            "Conciatta stands at a lectern. The scene jumps as the visitor "
            "walks the central aisle: questions, doubt and approval, arguments "
            "breaking out, and at last applause, as a few elders stalk out. "
            "Through all of it Currito sits at the back, quietly proud, and "
            "does not rise.",
            [
                titled(
                    "The curled stylus",
                    "The last image of the Vestige of Acclaim, seen only from "
                    "where Conciatta stands, shows the first sign of what was "
                    "to come: the silver stylus on her lectern has curled in on "
                    "itself and floats above the wood.",
                ),
                titled(
                    "The way out of the Vestige of Acclaim",
                    "The door at the rear is the way in and out.",
                ),
            ],
        ),
        (
            "seclusion",
            "The Vestige of Seclusion",
            "Bitter",
            "The foot of a winding stair that stands alone in blank "
            "whiteness, with no tower around it. Currito waits on the steps, "
            "bowed, dressed for the road with a heavy bag on his shoulder. "
            "The steps behind the visitors dissolve into mist, and those "
            "ahead end at Conciatta's door.",
            [
                titled(
                    "Off the stair",
                    "To step off the stair in the Vestige of Seclusion is to "
                    "fall into the void.",
                ),
                titled(
                    "Behind Conciatta's door",
                    "Behind the door there is nothing but its other side; "
                    "through the keyhole is her darkened sanctum, with things "
                    "floating about her as she stands weeping at her table, "
                    "fists clenched.",
                ),
                titled(
                    "The way out of the Vestige of Seclusion",
                    "Opening Conciatta's door is the way out.",
                ),
            ],
        ),
        (
            "death",
            "The Vestige of Death",
            "Fearful",
            "The foot of a bed in the convent near Toledo, where the aged "
            "Conciatta is dying. One nun holds her hand and prays, one bends "
            "to catch her words, and a senior sister stands by. Small things "
            "rise as if lifted, weakly, and fall. At her last breath the "
            "candles die, and in the gloom four figures stand in the room's "
            "four corners. Then it all begins again.",
            [
                titled(
                    "Conciatta's last words",
                    "Her last words beg that her broken soul be gathered: one "
                    "part is here, one in fire and damnation, one deep in the "
                    "lost city, one at home at last.",
                ),
                titled(
                    "Currito's triptych",
                    "Currito's triptych of Saint Ildefonso hangs in the Vestige "
                    "of Death and also exists in the mundane convent, his gift "
                    "for their help with her studies (Intelligence + Church "
                    "Lore simple roll against 6 names the saint). Looked at "
                    "closely, it also shows the other three tempora, and is the "
                    "way to each.",
                ),
            ],
        ),
    ):
        sites[key] = b.place(
            name,
            summary=words,
            secrets=[
                *hidden,
                titled(
                    "Storyguide Notes",
                    f"A tempus of the Magic Realm (LoH pp. 19-21), found during "
                    f"a story of that realm. Those within gain the Personality "
                    f"Trait {trait} +3 while they stay, unless they have a "
                    f"supernatural ability of the Magic Realm (Realms of Power: "
                    f"Magic p. 15). With the Magical Travel rules (same book p. "
                    f"23) it has a level of 5, Ease Factor 15 to reach the next "
                    f"tempus. No vestige connects to the mundane world, so none "
                    f"leads straight to the sanctum.",
                ),
            ],
            **RUMOURED,
        )

    zaragoza = sites["zaragoza"] = b.place(
        "Zaragoza",
        realm="Divine",
        summary=paragraphs(
            "A strong walled city at the heart of Aragon, and its capital "
            "since Alfonso el Batallador took it in 1118. Good roads run north "
            "to Jaca and the river runs southeast toward Barcelona. The Ebro "
            "bounds it on the north and its tributary the Huerva on the east, "
            "with many bridges. Church spires and old minarets crowd toward "
            "the middle, and in the narrow market streets Christian, Jew and "
            "Muslim haggle side by side between the bells and the calls to "
            "prayer.",
            "The valley rises slowly to mountains and holds desert, deep "
            "woods, plains and farms. Wheat is exported, and wine from up the "
            "Ebro makes the city rich. Spring is wet and summer a scorching "
            "drought. In winter two great cold spirits fight over the city: "
            "a fog that settles on it and a dry wind off the mountains that "
            "tries to drive the fog away.",
            "As Saraqusta it was an Arab city of the Emirate of Cordoba in "
            "Conciatta's day, later a Taifa kingdom under the Banu Tujib and "
            "the Banu Hud, whose armies El Cid led from 1081 to 1086. The "
            "Almoravids held it from 1110.",
        ),
        secrets=[
            titled(
                "Zaragoza's lost libraries",
                "When Alfonso took Zaragoza many libraries went south with "
                "fleeing Muslims, and the rest were sent to Paris, where they "
                "remain in the university's care. Hermetic texts were among "
                "them, Conciatta's too (p. 22).",
            ),
        ],
        **KNOWN,
    )
    sites["torre"] = b.place(
        "La Torre no Vista",
        inside=zaragoza,
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "In the northwest of the city, where the Ebro bends sharply back "
            "on itself, stand the home and great warehouse of the merchant "
            "Reyes de Barbastro, looking over the river. Beneath the warehouse "
            "is a low, gloomy cellar full of forgotten crates and barrels, "
            "with two pillars in its middle opposite the stairs. Its walls are "
            "plastered and whitewashed, and grubby with age. Here and there "
            "the plaster has flaked away from an older painting underneath.",
            "It keeps the name of the covenant Currito and Conciatta founded, "
            "which is all that most know of it: birds appear and vanish in "
            "the air above the place.",
        ),
        secrets=[
            titled(
                "The covenant in the air",
                "The covenant of La Torre no Vista is in the regio above the "
                "cellar, which hangs high in the air.",
            ),
            titled(
                "How Currito built the tower",
                "Currito raised the tower inside the regio by ritual after "
                "buying the land, and built wharfs and the warehouse in the "
                "mundane world as cover and income. The covenant dissolved in "
                "990.",
            ),
            titled(
                "What the Mercere records say",
                "Mercere records at Harco place La Torre no Vista only in "
                "Saraqusta. Yuval's, the Mercer house in Barcelona (Houses of "
                "Hermes: True Lineages p. 82), names Currito and Conciatta, says "
                "the tower rose from a regio on the south bank of the Ebro, "
                "gives a place for Redcaps in the east of the city apart from "
                "the sancta, and hints the regio lay north of the Noor Mosque.",
            ),
            titled(
                "Where the Noor Mosque stood",
                "The Noor Mosque is gone: Intelligence + Zaragoza Lore against 9 "
                "shows the Aljaferia palace stands on its site.",
            ),
            titled(
                "The fresco",
                "The fresco (pp. 24-25). The older painting in the cellar, by "
                "Currito, is a casting tablet for Conciatta's ritual Subsume the "
                "Apparent Dominion (printed ReVi 40 here, ReVi 50 on p. 26, "
                "whose working adds to 50; 50 is followed), its Hermetic words "
                "wound among scenes of the Cordoban city.",
            ),
            titled(
                "The missing part of the fresco",
                "The fresco is damaged and deliberately incomplete; the rest is "
                "the wall behind Conciatta in the illumination in Currito's "
                "journal, which shows her between these two pillars. It is the "
                "only casting tablet for the spell.",
            ),
            titled(
                "Subsuming the cellar's Dominion",
                "Once the cellar's Dominion is subsumed the level 1 Magic aura "
                "shows and the regio is far easier to enter.",
            ),
            titled(
                "What Reyes knows of the fresco",
                "Reyes knows nothing of the design.",
            ),
            titled(
                "The tower after the reunion",
                "After the reunion (p. 45). The tower gains a preternatural "
                "tether of Strength 1 and its aura aligns to Vim; 12 pawns of Vim "
                "vis lie there as crystal shards, and 4 pawns of Vim manifest in "
                "the tower on each anniversary. But the regio has lost the great "
                "being that helped tether its aura, and unless the tower returns "
                "to magical use the aura weakens over time.",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The cellar lies in a level 2 Dominion that subsumes a "
                    "Magic aura of level 1 (p. 24).",
                    "Finding it (p. 23). Or watch the air for birds appearing "
                    "or vanishing: Perception + Awareness simple roll against "
                    "9, a week's search plus a week per point missed.",
                    "With both parts of the casting tablet, Intelligence + "
                    "Magic Theory stress roll against 9, +1 per magus "
                    "collaborating after the first, one day plus a day per "
                    "point missed. On a botch the magus thinks he has it, but "
                    "the casting total is 0 and he rolls six extra botch dice. "
                    "Casting tablets: Covenants p. 89.",
                ),
            ),
        ],
        levels=[
            b.level(
                "The tower",
                6,
                see="Spells or abilities that see through regio boundaries "
                "show a stair winding around the outside of the cellar and "
                "up out of sight.",
                enter="Taking the stair pushes a character through the "
                "boundary. From within the Dominion, Perception + Second Sight "
                "simple roll against 21, and the aura penalizes any non-Divine "
                "power used; once the ritual has made the Magic aura apparent, "
                "against 15 (p. 25). Regio rules: ArM5 p. 189.",
                notes=secrets(
                    "A tower of several stories, each with room for several "
                    "chambers and a laboratory, and little sign of any staff. "
                    "From a balcony midway up, the Aljaferia can be seen as "
                    "through a mist.",
                    paragraphs(
                        "Currito's sanctum, midway up: the warped door gives "
                        "way to a burst of three dozen startled birds. "
                        "Centuries of guano have ruined all within; the "
                        "cabinets are empty and what equipment he left lies "
                        "smashed.",
                        "Conciatta's sanctum, near the top: the sanctum marker "
                        "is still on the unlocked door. Perception + Awareness "
                        "against 6 hears movement within. The Magical "
                        "Conciatta is inside. Most of the books and devices "
                        "are copies of the same few things, scraped or broken "
                        "down so she could write or build them again. What is "
                        "of use (pp. 26-27), each a source of insight; where "
                        "noted, a lab text or device gives a bonus to the "
                        "insight roll equal to its magnitude (Ancient Magic "
                        "p. 8), counting only a device's highest-level effect:",
                        "Subsume the Apparent Dominion, lab text, ReVi 50 "
                        "Ritual: R Touch, D Year, T Room; suppresses an "
                        "apparent Dominion of strength 3 or less, and the "
                        "strongest other aura present manifests. It creates a "
                        "preternatural tether of level one and a +1 yearly "
                        "aura modifier (Realms of Power: Magic p. 10). "
                        "Conciatta's code must be broken first (ArM5 p. 102), "
                        "at least a season's work. Re-creating it gives 10 "
                        "points toward Confluence of the Realms.",
                        "The Sands of Time, InVi 19: a three-chambered "
                        "hourglass a foot tall that shows whether a Magic aura "
                        "waxes (sand runs up), wanes (runs down) or holds "
                        "(gathers in the middle). R Touch, D Sun, T Ind, 2/day "
                        "triggered at sunrise and sunset. Only a broken one "
                        "remains, its glass smashed and sand gone; the wooden "
                        "frame survives for a skilled Verditius to reforge. "
                        "Broken it gives no bonus but 4 points toward Insight "
                        "of the Realms; working, +3 to an insight roll.",
                        "The Lodestone, InVi 33: a palm-sized silver device "
                        "with a pointer under a lens, which in a Magic aura "
                        "points to the nearest tether, and wanders if the aura "
                        "is diffuse. R Touch, D Sun, T Ind, 2/day triggered at "
                        "sunrise and sunset. No insight bonus; re-creating the "
                        "effect gives 7 points toward Insight of the Realms.",
                        "The Tome of Binro: 60 correspondences (Covenants p. "
                        "90), many in the hand of Binro, an early Bonisagus "
                        "follower called a heretic half in jest for holding "
                        "the founder's theory flawed. Studied as a level 6 "
                        "tractatus on Magic Theory, it reveals a casting "
                        "tablet of Ward Against Woodland Spirits, ReHe(Vi) 41 "
                        "(R Touch, D Ring, T Circle), with penetration built "
                        "in; re-created without that at level 30, it gives 9 "
                        "points toward True Understanding of the Realms.",
                    ),
                ),
            ),
        ],
        **RUMOURED,
    )

    toledo = sites["toledo"] = b.place(
        "Toledo",
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "A walled city on a rocky height, the Tagus around three sides "
            "and only the north open to the land. Drab and brown from afar, "
            "within it dazzles with slender winding streets and fine squares. "
            "Near the middle of the peninsula, it draws people from all "
            "Iberia. It is the heart of the Iberian church, and was so even "
            "under Islam. Christians, Jews and Muslims all practice freely, "
            "the Jews better treated than in most Christian cities, and for a "
            "century a school of translation has brought in texts from across "
            "the known world, so a scholar may find nearly anything.",
            "Castles of the military orders ring the city, and two orders are "
            "open rivals here. The Order of Calatrava, Benedictine, wears a "
            "red cross fleurdelisée on white, and only lately won back its "
            "name after losing its castle to the Almohades; it suspects its "
            "rivals of corruption. The Knights of Santiago, Augustinian, wear "
            "a red cross ending in a sword, protect pilgrims, and admit "
            "secular knights and lay members; they think the Calatravans weak.",
        ),
        secrets=[titled("Storyguide Notes", "Dominion aura 4 by day (p. 28).")],
        **KNOWN,
    )
    sites["convent"] = b.place(
        "Convento de San Ildefonso",
        inside=toledo,
        realm="Divine",
        aura=5,
        summary=paragraphs(
            "Low whitewashed buildings behind a low, dusty white wall, off "
            "the road a short way from Toledo, with a few dry fields behind "
            "and almond trees bleached of color by the sun. Inside, the "
            "convent sinks into the ground around a sunken courtyard with "
            "narrow tiled cloisters. It is poor and lives on Toledo's charity. "
            "A young novice here is said to receive divine visions, and the "
            "wealthy of Toledo and beyond sometimes come to consult her. "
            "Abbess Prudencia does not admit men inside the wall unless she "
            "trusts them or they are plainly very rich.",
            "The small graveyard lies some way off in the shade of a low "
            "hill. One small headstone bears the name of Conciatta.",
        ),
        secrets=[
            titled(
                "Who lies in Conciatta's grave",
                "By custom, the novice who last carried Conciatta's spirit lies "
                "in that grave when she dies; Conciatta's bones, like those of "
                "every later host, were moved to the ossuary, and no record "
                "says which are hers.",
            ),
            titled(
                "The seeming audience",
                "The audience (pp. 29-30). No outsider may see the holy sister, "
                "but money buys a seeming audience the next day: one visitor, "
                "with Prudencia and an attendant, addresses a curtain. Behind it "
                "her other attendant plays the seer, telling of a long journey, "
                "revelations, slights borne by grace, and acting both forcefully "
                "and temperately. If the sham is exposed Prudencia does not "
                "apologize, and shows them the girl, thinking that will send them "
                "away.",
            ),
            titled(
                "The automatic writing",
                "Automatic Writing (p. 30): a great heap of scrolls, books and "
                "slates written by the hosts out of Conciatta's knowledge.",
            ),
            titled(
                "What collating yields",
                "A season's collating of the convent's automatic writing yields "
                "several tractatus, of the storyguide's making, on Magic Theory, "
                "Vim and Dominion Lore, and a lab text for a large casting "
                "circle.",
            ),
            titled(
                "The casting circle",
                "The convent writings' casting circle is enchanted with "
                "Maintaining the "
                "Unstable Conjuration, ReVi 30, Pen +16, 3/day (R Personal, D "
                "Ring, T Circle): it sustains a spell of level 15 or less cast "
                "within, even the non-Hermetic magic of the Learned Magicians, "
                "until the target leaves or another spell is cast there. Built, "
                "it is a large iron ring in pieces, riveted in brass to the floor "
                "and opened with 20 pawns of vis; it gives a +1 specialization in "
                "experimentation and +1 Safety. The text gives +6 to the insight "
                "roll, and finishing the ring gives 6 points toward Confluence of "
                "the Realms.",
            ),
            titled(
                "Four effects for one device",
                "Conciatta's notes call Maintaining the Unstable Conjuration one "
                "of four effects for one Greater Enchanted Device, the others "
                "for the other realms and for spirits' non-Hermetic effects, "
                "which implies Infernal spirits once aided her.",
            ),
            titled(
                "Storyguide Notes",
                "The aura is a constant level 5 (p. 28).",
            ),
        ],
        **KNOWN,
    )

    qadis = sites["qadis"] = b.place(
        "Qadis",
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "An ancient city still in Moorish hands, on a sand spit in the "
            "Atlantic a little northwest of the Pillars of Hercules. Its "
            "loose ground bears few tall buildings, so the skyline sits low, "
            "but the port is busy, its view full of masts from all the world. "
            "The mouth of the Guadalquivir is a day's ride north.",
            "Old Qadis does not lie quiet. At sunset the living give the city "
            "over to its dead, a thousand ghosts or more from all its long "
            "history, who go about their affairs unseen by most. Strangers, "
            "and magi above all, draw their interest.",
        ),
        secrets=[
            titled(
                "The watching ghosts",
                "After some days in Qadis, Second Sight or fit magic shows "
                "ghosts watching the characters: loose-formed specters sent by "
                "stronger masters, who mostly flee if challenged. Then the "
                "characters begin to see others abroad at night.",
            ),
            titled(
                "Storyguide Notes",
                "Dominion aura 2 on average, 1 at night, and the city is full "
                "of lacunae of Magic, Faerie and Infernal (p. 33). The "
                "storyguide may offer a ghost ally, who can make introductions "
                "and point out places of power, and will expect something in "
                "return.",
            ),
        ],
        **KNOWN,
    )
    sites["theatre"] = b.place(
        "The Roman Theater of Qadis",
        inside=qadis,
        realm="Divine",
        summary="A sunken half-circle of chipped and broken marble steps, "
        "disused for centuries and stripped of all else. Stories of its "
        "haunting are likely why it was never built over. The living know the "
        "place, but not the name of the actor who holds it; the dead know "
        "both, and come often to watch.",
        secrets=[
            titled(
                "The theater's ghost",
                "Seiffeddin is the Roman Theater's only ghost.",
            ),
            titled(
                "Why the dead attend",
                "The dead attend Seiffeddin less for love of his art than from "
                "the constraints of their own roles (p. 34).",
            ),
        ],
        **KNOWN,
    )
    marsh = sites["marsh"] = b.place(
        "The Guadalquivir Marshes",
        realm="Faerie",
        aura=2,
        summary="The marshes around the Guadalquivir delta, a day's ride north "
        "of Qadis. Bits of an ancient wall lie out in them, and a witch's "
        "torch moves about by night.",
        secrets=[
            titled(
                "The marsh faeries",
                "Other faeries in the Guadalquivir Marshes lure the unwary to "
                "their doom (Realms of Power: Faerie p. 92).",
            ),
            titled(
                "The old walls",
                "Sections of the old walls in the marshes lie in Faerie "
                "regiones (Realms of Power: Faerie p. 16).",
            ),
            titled("Storyguide Notes", "Faerie aura 2 where the city stood."),
        ],
        **KNOWN,
    )
    sites["tartessos"] = b.place(
        "Tartessos",
        inside=marsh,
        realm="Faerie",
        summary=paragraphs(
            "Once a mighty trading city, silver-rich, whose metal paid for "
            "Greece's defense against the Persians, which traded with the Tin "
            "Islands and the Phoenicians under its absolute king Arganthonios. "
            "A great calamity sank it into the sea in a single day. It lives "
            "now only in the Faerie Realm.",
            "Lightning flashes in a sky of rolling thunder over endless ruins, "
            "and the weeping of an unseen dying people comes from all around. "
            "Every brick that falls has another about to fall. At the center "
            "stands the shell of a palace, all pillars and broken arches.",
        ),
        secrets=[
            titled(
                "Bruja's book",
                "Bruja brings the characters to the road but does not go in; "
                "she meets them when they leave, gives them a book with a "
                "warning not to open it until the other side, and summons the "
                "Threshold.",
            ),
            titled(
                "What Bruja's book holds",
                "Bruja's book holds the Faerie Conciatta.",
            ),
            titled(
                "Storyguide Notes",
                "The story's theme is reunification (pp. 36-37). Each challenge "
                "passed leads closer to the palace; each failure closer to the "
                "mundane world. Examples: a mother crying for her lost daughter; "
                "two brothers fighting over the last loaf; a statue of a young "
                "warrior who has lost his spear, which lies in the path (Excellent "
                "quality long spear, +2 attack and defense): return it and he "
                "points the way, take it and robbers may come; an old man whose "
                "well bucket has fallen, who leads to the palace only if the well "
                "is mended. Two or more passed find the palace; three failed find "
                "a facade whose doors lead out to the mundane world. Each success "
                "earns a Fable Point (Realms of Power: Faerie p. 21).",
            ),
        ],
        levels=[
            b.level(
                "The city gates",
                5,
                "Faerie",
                see="Two broken pillars and great shards of rotted wood rise "
                "from the marsh.",
                enter="Only on the anniversary of the city's loss, one night "
                "a year; a guide is needed to find it and to cross the "
                "Threshold into the Faerie Realm (p. 35).",
                notes=secrets(
                    "A faerie regio of the old walls and the way into the city.",
                    "If using Realms of Power: Faerie (p. 20): Threshold "
                    "Strength 24; on the anniversary the Threshold Total is "
                    "already 15 (6 for the gates, 9 for the night), before "
                    "personal Thresholds, artistic endeavor and Arcadian "
                    "Mysteries. Bruja's potion can add the rest. Without that "
                    "book, Bruja is simply able to guide them through, and "
                    "frogs are still involved. Bruja, as guardian of the "
                    "road, then offers a choice of kingdoms of silver and "
                    "gold or a kingdom of loss and despair: Tartessos is the "
                    "kingdom of loss, and any other answer makes the road "
                    "vanish and sends them back to Qadis (p. 36).",
                ),
            ),
        ],
        **RUMOURED,
    )

    narixa = sites["narixa"] = b.place(
        "Narixa",
        realm="Divine",
        aura=3,
        summary="A small, wealthy Muslim town on the Mediterranean shore of Al "
        "Andalus, with white beaches below, low mountains behind that fall to "
        "fine cliffs, and silks famous across the Muslim world. Fishing boats "
        "launch daily from the sand, and the markets are full of fish, "
        "livestock, fruit and grain; the merchant quarter trades silk, spice "
        "and European goods among street players and the calls to prayer. "
        "There are few dhimmis this far into Al Andalus, but people from all "
        "the Islamic world. The poor quarters mistrust foreigners, the rich "
        "ones are used to them, and men who look for trouble find it.",
        secrets=[
            titled(
                "The evil in the mountains",
                "Narixa knows little of the evil in the mountains.",
            ),
            titled(
                "Storyguide Notes", "Dominion aura 3 over most of its lands (p. 40)."
            ),
        ],
        **KNOWN,
    )
    sites["mosque"] = b.place(
        "The Al Narixa Mosque",
        inside=narixa,
        realm="Divine",
        summary="A mosque with a long-tended library, among the many that "
        "fill Narixa's skyline. Its imams have little interest in helping "
        "foreigners hunt old scrolls, but may send the persuasive to Hamid "
        "ibn Harun, who keeps the library.",
        secrets=[
            titled(
                "Notes left at the mosque",
                "Conciatta and Currito left many notes in the Al Narixa "
                "Mosque's library on the last of their visits, well over two "
                "centuries ago (p. 40).",
            ),
            titled(
                "Conciatta's Scrolls",
                "Conciatta's Scrolls (p. 41): collated, a map of a cave system "
                "two miles east of the town, with how to find and enter it, and a "
                "warning of tunnels where the unwary slip between regio levels "
                "unawares. It gives +1 to rolls to navigate the caves and their "
                "regiones.",
            ),
            titled(
                "The Insightful Stylus",
                "The Insightful Stylus (p. 41): in a small sealed leather case "
                "marked Conciatta ex Bonisagus, a slender silver stylus traced "
                "with Hermetic and occult symbols of the Infernal, and a scrap of "
                "parchment on its effects. Opened with 12 pawns of vis. Sense the "
                "Line, InVi 14, Pen +0, constant (R Touch, D Sun, T Ind): detects "
                "the line of an Infernal regio boundary. Inscribe the Line, ReTe "
                "14, Pen +0, constant (R Personal, D Sun, T Ind): held to a wax "
                "tablet, the stylus traces that boundary in miniature, at the "
                "speed of a magus drawing a circle. Note These Landmarks, ReTe "
                "14, Pen +0, unlimited (R Personal, D Mom, T Ind): at a Latin "
                "command it marks distances and landmarks, even while inscribing. "
                "It must be investigated in the laboratory, and is then a source "
                "of insight; re-creating it gives 5 points toward Insight of the "
                "Realms.",
            ),
        ],
        **KNOWN,
    )
    sites["caves"] = b.place(
        "The Narixa Caves",
        inside=narixa,
        realm="Infernal",
        aura=3,
        summary="Ancient caves in the low mountains two miles east of Narixa, "
        "of deep fissures and domed chambers. Mice, scorpions and snakes "
        "swarm over floor and wall, and the laughter of hyena echoes from "
        "somewhere deep inside. Here and there human bones jut from the rock.",
        secrets=[
            titled(
                "What dwells in the caves",
                "The Narixa Caves are a hive of corrupted beasts, jinn and demons.",
            ),
            titled(
                "The bleeding regiones",
                "Unlike most, the regiones of the Narixa Caves bleed into each "
                "other as the tunnels do, and the bones are those of victims "
                "caught between a regio and the mundane world. The unprepared "
                "are certain to be lost for good (pp. 39-41).",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "A level 3 Malevolent Infernal aura, with Tartaran regiones "
                    "throughout (Realms of Power: The Infernal pp. 15-16).",
                    "All terrain is hazardous: an extra botch die on physical actions, "
                    "and large weapons at -2 to attack and defense. Three events "
                    "should test the party on the way to the throne room (pp. 41-43). "
                    "A sheer face: three climb rolls of rising difficulty (6, 9, 12, "
                    "say); a failure starts a fall with an initiative of 6, for "
                    "fast-casting; a botch may be lethal or draw him into a regio, "
                    "and Area Lore: Narixa Caves stress against 12 finds him. A rock "
                    "fall: those beating an initiative of 6 may react, and the rest "
                    "are as in a collapsing stone building (ArM5 p. 181). Hyena "
                    "ambush: Perception + Awareness against their stealth; a pack "
                    "splits, two dragging one victim toward a regio and three blocking "
                    "the rest. After four rounds he is taken deeper: a grog is dead, "
                    "any other may fight free and flee the regio.",
                ),
            ),
        ],
        levels=[
            b.level(
                "The throne room",
                5,
                "Infernal",
                see="A huge domed chamber, its floor split by chasms, flames "
                "running on the walls, and at its far end craggy steps that "
                "sweep out over a wide fiery chasm to a throne of writhing "
                "serpents.",
                notes=secrets(
                    "A level 5 Tartaran regio, and the heat is unbearable.",
                    paragraphs(
                        "The fight should be deadly (p. 44). The storyguide "
                        "sets the numbers; all the beasts mean to kill. A "
                        "hyena pack that holds a positive grapple strength "
                        "two rounds running drags its enemy to a chasm: "
                        "Dexterity + Athletics or Climb stress against 9 to "
                        "cling on. If he fails, another who has not acted may "
                        "fast-cast, or leap to catch him (Quickness + "
                        "Athletics stress against 9): both end prone and must "
                        "recover their weapons. Climbing back is Dexterity + "
                        "Climb stress against 9. A fall ends in the lava "
                        "hundreds of feet below.",
                    ),
                ),
            ),
        ],
        **RUMOURED,
    )
    return sites


def _legends(b: Builder) -> None:
    """Conciatta and Currito, long gone."""
    b.magus(
        "Conciatta of Bonisagus",
        covenant=None,
        house=BONISAGUS,
        age=None,
        summary=paragraphs(
            "Born Dolorita, a wealthy merchant's daughter of Barcelona, about "
            "885. Baltasar of Bonisagus took her to Leon and fostered her out "
            "as far as Al Andalus, Provence and Lombardy, and she left "
            "apprenticeship hungry to reach the unseen realms by Hermetic "
            "means alone. She worked as a laboratory assistant across Iberia "
            "and beyond. On her travels she met Currito of Jerbiton, and "
            "within a year they had raised a tower in a regio at Zaragoza and "
            "married.",
            "Her peers held that the realms would yield only to new Arts. She "
            "disagreed, and in 930 published The Application of Vim to the "
            "Supernatural Humors (tractatus on Magic Theory, quality 7), "
            "showing that auras fall into four categories matching the realms "
            "and that Vim can reach all four. Her name was made. Then Baltasar "
            "confessed to Infernal corruption and was marched; her rivals "
            "used it, her sex and her youth against her, and she was quietly "
            "shut out of Bonisagus society. She sent her last unfinished notes "
            "to Durenmar.",
            "For forty years she studied strange places and published nothing, "
            "while Currito found her vis and books. In the end he left, and "
            "she stayed on alone in her tower while the world forgot her. The "
            "Order holds that she vanished into Twilight before the "
            "millennium. Her fame survives as a primer and, among Bonisagi, a "
            "warning.",
            "Vim itself, as the Founders taught it, covered only active magic; "
            "the Forms did what Vim now does (p. 15). Much of the language "
            "magi use of auras is hers: diffuse and tethered; stable, waning "
            "and waxing; existential and moral; apparent and subsumed.",
        ),
        secrets=[
            titled(
                "Conciatta's leaking magic",
                "Her Gift grew blatant and magic began to leak from her "
                "unbidden, ruining her studies and drawing Twilight on.",
            ),
            titled(
                "Conciatta at the convent",
                "After five years alone, as the millennium turned, she went to "
                "a convent near Toledo she knew from her research, hoping the "
                "Dominion would quiet her magic. It did for a while.",
            ),
            titled(
                "Conciatta's broken spirit",
                "Warping took her into Final Twilight eleven years on, and her "
                "spirit broke into four aspects, one for each realm, which fled "
                "the convent.",
            ),
            titled(
                "What the aspects guard",
                "Each of Conciatta's four aspects keeps something of her and "
                "guards a part of her unpublished breakthroughs (p. 14).",
            ),
            *REMEMBERED,
            titled(
                "Storyguide Notes",
                paragraphs(
                    REMEMBERED_NOTES,
                    ARTIFACTS,
                    "Her new Virtues and Flaw, spells and guidelines (pp. 14-18) are "
                    "in the catalogs: Confluence, Insight and True Understanding of "
                    "the Realms; The Constant Expression, which magi Initiating her "
                    "Virtues take through ordeal; To See What Binds this Magical "
                    "Place; This Heart of Darkness; Dominance Over the Infernal. Her "
                    "guidelines may be used by any maga who has studied one of her "
                    "unpublished works. Integrating her discoveries: Ancient Magic p. "
                    "7; original research: Houses of Hermes: True Lineages p. 26; "
                    "summary: Hedge Magic Revised Edition p. 14; the two add together "
                    "(p. 18). The book gives her dates as c. 885 to 1007, yet has her "
                    "at the convent eleven years from the new millennium (p. 14).",
                ),
            ),
        ],
    )
    b.magus(
        "Currito of Jerbiton",
        covenant=None,
        house=JERBITON,
        age=None,
        summary=paragraphs(
            "An artist at heart and Conciatta's husband, impetuous and "
            "confident. He found the auras of Zaragoza and founded La Torre "
            "no Vista with her. His paintings were mostly religious, though "
            "for a time rich covenants prized his Hermetic triptychs, and "
            "frescoes of his can still be found across the Order.",
            "He gave up his own studies and art to supply his wife, was "
            "mocked by his peers for it, and after she went a full year "
            "without seeing him he left Zaragoza, bitter, with some of her "
            "notes to sell. Reports put him in the Levant before 1000. By the "
            "Schism War his best days were long gone, and he ended as a "
            "wandering artist living on old fame and old friends' hospitality "
            "until his welcome wore out. In unguarded moments he spoke of a "
            "great prize: Hermetic magic fueled by the Dominion's own aura.",
        ),
        secrets=[
            titled(
                "The Life of Currito",
                "The Life of Currito (p. 22): his book, written in age, in a "
                "shaky hand between leather flaps; a five-day distraction to read. "
                "It tells that their hidden covenant was still plagued by birds "
                "from the mundane world; that Conciatta stayed in Zaragoza after "
                "La Torre no Vista dissolved; that she studied the Dominion at a "
                "convent in Toledo and ended her days there; that they survived "
                "an Infernal cave system at Narixa and left notes and a map in "
                "the library of the al Narixa mosque; and, with evident "
                "bitterness and no detail, that she bargained for knowledge with "
                "the king of a lost city outside Qadis, which began to turn her "
                "from him.",
            ),
            titled(
                "The illumination",
                "A full-page illumination in The Life of Currito shows "
                "Conciatta under a wide arch, its pillars held up on one side "
                "by an angel on a demon, on the other by a dragon on a winged "
                "man with a lute. Hermetic text fills the wall behind her: the "
                "missing part of the cellar's casting tablet.",
            ),
            titled(
                "Storyguide Notes",
                "Books and devices he took may turn up in a covenant's library "
                "or stores, and casting tablets of his on auras too; his "
                "surviving frescoes can foreshadow the story by showing one "
                "subject as touched by the four realms (p. 19).",
            ),
        ],
    )


def _people(b: Builder) -> None:
    """The living who stand in the way, or hold what is sought."""
    reyes = b.magus(
        "Reyes de Barbastro",
        covenant=None,
        house="",
        age=35,
        type="companion",
        summary="A prosperous Zaragoza merchant whose home and warehouse "
        "look over the Ebro. He trades chiefly in wine from Logroño, where he "
        "keeps another warehouse, but will buy and sell most things. He has "
        "three daughters, of 17, 16 and 14, and no sons, and wants husbands "
        "who will care for his business and his daughters, in that order.",
        secrets=[
            titled(
                "What lies under Reyes's warehouse",
                "His warehouse cellar bounds the old covenant's aura, which he "
                "knows nothing of.",
            ),
            titled(
                "Winning Reyes's cellar",
                "Characters wanting the cellar may appeal to his wish for "
                "sons-in-law (pp. 23-24).",
            ),
        ],
    )
    b.stats(reyes, REYES, source="LoH")
    prudencia = b.magus(
        "Abbess Prudencia",
        covenant=None,
        house="",
        age=45,
        type="companion",
        summary="Abbess of the Convento de San Ildefonso, thought strict and "
        "aloof; the aloofness is mostly contempt for the men who come to her "
        "convent for their own secular gain. She knows little of magic and "
        "dislikes magi at her door.",
        secrets=[
            titled(
                "Prudencia's relic",
                "She unknowingly wears a relic of San Ildefonso, a cord from his "
                "robe wound into a belt handed from abbess to abbess.",
            ),
            titled(
                "The abbesses' vow",
                "She holds the vow, passed down the line of abbesses, to protect "
                "the spirit, and will not lightly break it (pp. 29-30).",
            ),
            titled(
                "Winning Prudencia's trust",
                "Winning her trust: a task she needs done, of no great danger, "
                "that lets the characters show virtue; a good name for "
                "kindness, charity or judgment around Toledo; or generosity to "
                "the convent.",
            ),
            titled(
                "If the spirit harms the girl",
                "If she is persuaded the spirit harms the girl, she will not let "
                "the suffering go on, and lets the magi try to part them (p. "
                "32).",
            ),
            titled("Storyguide Notes", "The relic has one Faith Point."),
        ],
    )
    b.stats(prudencia, PRUDENCIA, source="LoH")
    immaculada = b.magus(
        "Novice Immaculada",
        covenant=None,
        house="",
        age=17,
        type="companion",
        summary="The novice of the Convento de San Ildefonso whose visions "
        "the wealthy pay to hear. The sisters care for her, for she cannot "
        "care for herself. She lives in a windowless room lit by candles, "
        "among bedding, slates and parchment, writing and speaking in "
        "tongues without warning.",
        secrets=[
            titled(
                "The spirit Immaculada carries",
                "She carries the Divine Conciatta, the latest of generations of "
                "possessed novices, and fares worst of them all.",
            ),
            titled(
                "A miracle forgotten",
                "The convent has long taken Immaculada's possession for God's "
                "miracle, and its magical origin is all but forgotten (p. 29).",
            ),
            titled(
                "Sense in her babble",
                "When visitors enter, sense surfaces in her babble (pp. 31-32): "
                "she once had many brothers and sisters and now only three, "
                "who hide, though she remembers where she went; Seiffeddin, an "
                "actor in Qadis, may know her and where she is; she would like "
                "to see her sisters.",
            ),
            titled(
                "What binds the spirit to her",
                "Her fear of being alone binds the spirit to her. If that is "
                "abated, the spirit can pass to another host.",
            ),
            titled(
                "Storyguide Notes",
                "How the spirit passes to another host is left to the troupe (p. 32).",
            ),
        ],
    )
    b.stats(immaculada, IMMACULADA, source="LoH")
    habib = b.magus(
        "Habib al-Hadi",
        covenant=None,
        house="",
        age=45,
        type="companion",
        summary="A scholar of Qadis, and cleric, astronomer, translator and "
        "teacher, who takes any work that keeps him in food and parchment, "
        "though not always in that order. He can be met at night searching "
        "the city with a strange instrument, and likes nothing better than "
        "to talk to the learned. His observatory is his room on the top "
        "floor of a tenement in a poor and noisy district.",
        secrets=[
            titled(
                "Habib's strange instrument",
                "He found the Fourfold Lens lately, took it for a device to "
                "study the heavens, and has seen auras and the ghostly citizens "
                "through it. He files what he sees under the four elements, "
                "tying them uncertainly to the four auras.",
            ),
            titled(
                "Parting Habib from the Lens",
                "He is slow to lend or sell the Fourfold Lens, but may part "
                "with it if his study of supernatural Qadis can be fed some "
                "other way (pp. 34-35).",
            ),
            titled(
                "The Fourfold Lens",
                "The Fourfold Lens (p. 34): an adjustable iron stand with four "
                "hand-sized lenses on swinging arms, each enchanted for one "
                "realm and clear if its aura is absent. Conciatta made it for her "
                "custos and Currito to take on journeys, and it was lost on one. "
                "Each lens is Unveil the Subsumed (Realm), InVi 54, constant (R "
                "Personal, D Sun, T Vision, 2/day triggered at sunrise and "
                "sunset): it shows any aura present of its realm, subsumed or "
                "not, and the world as that aura would make it. It finds "
                "subsumed auras of any level but can only penetrate an apparent "
                "aura of level 3, and only the lowest level of each, so it does "
                "not show regiones. Re-creating it gives 11 points toward "
                "Confluence of the Realms.",
            ),
        ],
    )
    b.stats(habib, HABIB, source="LoH")
    hamid = b.magus(
        "Imam Hamid ibn Harun",
        covenant=None,
        house="",
        age=55,
        type="companion",
        summary="An imam of the Al Narixa Mosque all his adult life, kept "
        "mostly to its library. He suffers visions he takes for warnings from "
        "Allah, always of tunnels, caves, and hungry yellow eyes in the dark.",
        secrets=[
            titled(
                "The queen in Hamid's visions",
                "If the caves are spoken of with or near him in Arabic, he also "
                "sees a seductive queen clothed in smoke and fire (p. 40).",
            ),
        ],
    )
    b.stats(hamid, HAMID, source="LoH")


def _powers_of_vim(b: Builder) -> list[CreaturePower]:
    """The powers the Magical and Infernal aspects share."""
    return [
        b.power(
            "Crafter of Vim",
            1,
            0,
            "Vim",
            level=25,
            does="Focus Power: any Creo or Rego Vim effect of level 25 or "
            "less, at 1 Might point a magnitude. Init 0 minus the points "
            "spent.",
        ),
        b.power(
            "Eidolon",
            0,
            0,
            "Imaginem",
            does="Focus Power: an illusory form both seen and heard, made and "
            "unmade at will, and she always keeps it. Realms of Power: Magic "
            "p. 102.",
        ),
        b.power(
            "Ghost Touch",
            1,
            0,
            "Terram",
            does="Greater Power: moves objects not held or fastened down, 5 "
            "pounds for 1 Might point, doubling with each further point. In "
            "constant use, mostly beyond her control, and often drains her "
            "Might. Init 0 minus the points spent. Realms of Power: Magic p. "
            "102.",
        ),
        b.power(
            "Master of Vim",
            1,
            0,
            "Vim",
            level=25,
            does="Focus Power: changes or destroys weak sources of magic she "
            "can perceive, as any Muto or Perdo Vim effect of level 25 or "
            "less, at 1 Might point a magnitude. Init 0 minus the points "
            "spent.",
        ),
    ]


def _aspects(
    b: Builder, sites: dict[str, Neighbour], tower: Neighbour
) -> dict[str, Creature]:
    """The four aspects of Conciatta."""
    found: dict[str, Creature] = {}
    found["magic"] = b.creature(
        "The Magical Conciatta",
        page="p. 26",
        realm="Magic",
        might=30,
        age=LOOKS,
        confidence=(1, 3),
        soak=-1,
        fatigue_levels=FATIGUE,
        place=tower,
        level=1,
        block={
            "characteristics": CONCIATTA_CHARACTERISTICS,
            "virtues_flaws": [
                *CONCIATTA_VIRTUES,
                *["Focus Power"] * 3,
                "Greater Power",
            ],
            "abilities": CONCIATTA_ABILITIES,
            "traits": {"Driven": 3, "Introverted": 2, "Scholar": 3},
            "reputations": ACCLAIM,
        },
        powers=_powers_of_vim(b),
        appearance="Two steps from presentable: her long hair is tied up and "
        "working loose, her fingers and once-fine gown are stained with ink. "
        "She works at a large orderly table in a storm of floating books, "
        "bottles and boxes, among flashes of light and glimpses of far places "
        "or old faces.",
        notes=paragraphs(
            "Scholar is her Essential Trait. " + wound_ranges(0),
            "Might Form not printed. Things dart at intruders until she "
            "catches them, plainly with effort. She orders strangers out, "
            "then waits for proper overtures; in time she will find a reason "
            "to deal with them calmly (p. 25).",
        ),
        secrets=[
            titled(
                "What she knows of her death",
                "She knows she is dead and suspects a Final Twilight, prolonged "
                "and somehow made lasting, and that others like her may exist "
                "for the other realms.",
            ),
            titled(
                "Nothing new to learn",
                "She knows she can learn nothing new of note, unless perhaps "
                "what follows if her Final Twilight is let finish (p. 25). Her "
                "books scrape over her own work again and again.",
            ),
        ],
    )
    found["divine"] = b.creature(
        "The Divine Conciatta",
        page="p. 31",
        realm="Divine",
        might=30,
        form="Mentem",
        block={
            "virtues_flaws": ["Focus Power", *["Ritual Power"] * 3],
            "traits": {"Fearful": 2, "Confused": 1, "Distraught": 1},
        },
        powers=[
            b.power(
                "Possession",
                30,
                0,
                "Mentem",
                does="Focus Power: by spending all her Might she inhabits a "
                "target, her Personality Traits overlaying and adding to the "
                "host's. Thus she has held novices through the years.",
            ),
            b.power(
                "Grant (Visions)",
                0,
                0,
                "Vim",
                does="Ritual Power, used automatically on possession: gives "
                "the host the Visions Minor Story Flaw (ArM5 p. 60). Through "
                "it her memories of Hermetic work surface in the host.",
            ),
            b.power(
                "Grant (Enfeebled)",
                0,
                0,
                "Vim",
                does="Ritual Power x2, used automatically on possession: gives "
                "the host the Enfeebled Major Flaw (ArM5 p. 53).",
            ),
        ],
        place=sites["convent"],
        appearance="She has no body, only a personality and a run of "
        "ill-fitting memories within her host. At the reunion she rises from "
        "the host as an angelic presence.",
        notes="The book prints no Characteristics or combat scores: she "
        "persists only within a host, the girl Immaculada. Her knowledge lies "
        "just below the surface of the mind, beyond conscious control: one "
        "who chooses to carry her has no conscious access to it, but bears "
        "her Personality Traits and gains the protection of her Divine Might. "
        "A new host suffers Enfeebled and Visions.",
        secrets=[
            titled(
                "Visions in a new host",
                "Visions in a new host may show her as a queen, wreathed in "
                "serpents, or in the heart of a great fire, or a shining city "
                "sinking under a mighty river (p. 32).",
            ),
        ],
    )
    found["faerie"] = b.creature(
        "The Faerie Conciatta",
        page="p. 39",
        realm="Faerie",
        might=5,
        age=LOOKS,
        confidence=(1, 3),
        soak=-1,
        fatigue_levels=FATIGUE,
        place=sites["tartessos"],
        block={
            "characteristics": CONCIATTA_CHARACTERISTICS,
            "virtues_flaws": [
                "Humanoid Faerie",
                "Ritual Power",
                "Ritual Power",
                ("Sovereign Ward", {"ward": "cannot leave Tartessos"}),
                "Incognizant",
                *["Focus Power"] * 3,
                "Greater Power",
            ],
            "abilities": CONCIATTA_ABILITIES,
            "traits": {
                "Protective of Arganthonios": 3,
                "Regretful": 2,
                "Sorrowful": 2,
            },
            "reputations": ACCLAIM,
        },
        powers=[
            b.power(
                "Grant (Insight of the Realms)",
                5,
                -10,
                "Vim",
                rtd=("Touch", "Mom", "Ind"),
                does="Ritual; no Hermetic equivalent. Blesses the target with "
                "the Insight of the Realms Virtue for as long as she chooses. "
                "She regains the Might only by withdrawing the gift, and until "
                "then she in effect does not exist, reaching the world only "
                "by that withdrawal.",
            ),
        ],
        appearance="Young as she was in life, in a classical tunic and a "
        "cloak falling from her left shoulder, decked with silver and jewels. "
        "She sits beside the Silver King with her hand on his, and scorns all "
        "talk of the world she left.",
        notes=paragraphs(
            "Her Abilities are Pretenses: she believes she is Conciatta, "
            "with deep knowledge of Hermetic Theory, and that she swore her "
            "magic away. She cannot be made to use her former powers, and "
            "being Incognizant cannot see the truth of what she is. "
            "Arganthonios imposes her Sovereign Ward; it lifts when his "
            "bargain is met. " + wound_ranges(0),
        ),
        secrets=[
            titled(
                "Not truly Conciatta",
                "She is not truly Conciatta. The aspect the characters seek "
                "faded a century ago and became glamour, after pining for what "
                "she gave up and dying a second death; the true one had come "
                "back centuries ago to keep a bargain with the king.",
            ),
            titled(
                "Releasing the Faerie Conciatta",
                "If reminded of her love for Currito she is released, and takes "
                "her role to be reunited with her sisters (pp. 38-39).",
            ),
            titled(
                "The book of her essence",
                "On leaving Tartessos her essence goes into the book Bruja "
                "gives: a quality 7 tractatus on Faerie Lore in somewhat "
                "archaic Hermetic Latin. The one given it gains one of her "
                "breakthroughs as a charm (Realms of Power: Faerie pp. 39, "
                "104), usable while he carries the book and keeps it secret "
                "(p. 45).",
            ),
        ],
    )
    found["infernal"] = b.creature(
        "The Infernal Conciatta",
        page="p. 43",
        realm="Infernal",
        might=30,
        age=LOOKS,
        confidence=(1, 3),
        soak=-1,
        fatigue_levels=FATIGUE,
        place=sites["caves"],
        level=1,
        block={
            "characteristics": CONCIATTA_CHARACTERISTICS,
            "virtues_flaws": [
                *CONCIATTA_VIRTUES,
                "Focus Power",
                "Greater Power",
            ],
            "abilities": CONCIATTA_ABILITIES,
            "traits": {"Corrupted": 2, "Hateful": 2, "Scholar": 3},
            "reputations": ACCLAIM,
        },
        powers=[
            *_powers_of_vim(b),
            b.power(
                "Hell's Onslaught",
                0,
                1,
                "Ignem",
                does="Greater Power: as Pilum of Fire, +15 damage. Excess "
                "levels lower its cost, raise its initiative and master it, so "
                "she can loose two bolts together.",
            ),
            b.power(
                "Master of Stone",
                1,
                0,
                "Terram",
                level=25,
                does="Focus Power: any Muto or Perdo Terram effect of level "
                "25 or less, at 1 Might point a magnitude. Init 0 minus the "
                "points spent.",
            ),
        ],
        appearance="Her skin glows as if fire boiled just beneath it, and her "
        "hair is drifting smoke. She is alluring, beautiful and all but naked.",
        notes=paragraphs(
            "Might Form not printed. The block repeats the Magic Spirit and "
            "the other Virtues of the Magical aspect. " + wound_ranges(0),
            "Holy relics affect her, as she is a demon (p. 45). Her Qualities "
            "are as printed, though the block gives four powers marked Focus "
            "and two Greater.",
        ),
        secrets=[
            titled(
                "Beyond the Order's rules",
                "She mocks the visitors and says the Order's rules no longer bind her.",
            ),
            titled(
                "Her false bargain",
                "If the host of the Divine aspect is there, she offers to let "
                "the others go for one life; she will not keep her word.",
            ),
            titled(
                "How the Infernal Conciatta fights",
                "Soon bored, she sends in her army. She watches for hastily "
                "drawn circles and breaks them with Master of Stone, and does "
                "not trust her penetration against Parma Magica (p. 44). She "
                "will fight to the death.",
            ),
            titled(
                "What may bind her",
                "Her Might makes wards a hard way to bind her: holy relics; "
                "Perdo Vim to lower her Might; intense cold may harm her and "
                "force her to submit (pp. 44-45).",
            ),
            titled(
                "Storyguide Notes",
                "The troupe should be creative in binding her.",
            ),
        ],
    )
    return found


def _creatures(b: Builder, sites: dict[str, Neighbour]) -> None:
    """Those who guard the ways to the aspects."""
    b.creature(
        "Seiffeddin the Actor",
        page="p. 32",
        realm="Magic",
        might=10,
        form="Mentem",
        season="Autumn",
        age="Appears to be in his late fifties",
        confidence=(0, 0),
        soak=0,
        fatigue_levels=FATIGUE,
        place=sites["theatre"],
        block={
            "characteristics": characteristics(0, 0, 3, 1, 0, 0, 0, 0),
            "virtues_flaws": [
                "Magic Spirit",
                "Gossip",
                "Inspirational",
                vf_puissant("Profession: Actor"),
                ("Baneful Circumstances", {"circumstance": "exposed to sunlight"}),
                "Noncombatant",
                "Soft-Hearted",
                *["Focus Power"] * 3,
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "storytelling"),
                ("Artes Liberales", 3, "rhetoric"),
                ("Awareness", 2, "audience"),
                ("Carouse", 4, "with his audience"),
                ("Charm", 2, "being witty"),
                ("Concentration", 3, "recitals"),
                ("Disguise", 4, "masks"),
                ("Dominion Lore", 1, "Divine creatures"),
                ("Etiquette", 3, "Qadis ghosts"),
                ("Faerie Lore", 2, "places"),
                ("Folk Ken", 2, "the living"),
                ("Dead Language: Greek", 5, "storytelling"),
                ("Guile", 3, "subtle deceit"),
                ("Infernal Lore", 1, "undead"),
                ("Intrigue", 3, "the ghosts of Qadis"),
                ("Dead Language: Latin", 5, "ancient works"),
                ("Magic Lore", 4, "ghosts"),
                ("Profession: Actor", 5, "plays of many parts"),
                ("Area Lore: Qadis", 5, "history"),
                ("Teaching", 4, "Profession: Actor"),
            ],
            "traits": {"Artistic": 3, "Brave": -1, "Paternal": 2},
            "reputations": {
                "Gossip (Ghosts of Qadis)": 1,
                "Actor (Ghosts of Qadis)": 3,
            },
        },
        attacks=[b.attack("Dodge", 0, None, 0, None)],
        powers=[
            b.power(
                "Crafter of Illusion",
                1,
                0,
                "Imaginem",
                level=10,
                does="Focus Power: illusory props and sounds, as any Creo or "
                "Rego Imaginem effect of level 10 or less, at 1 Might point a "
                "magnitude. Never truly lifelike: they convey an idea or "
                "feeling. Init 0 minus the points spent.",
            ),
            b.power(
                "Eidolon",
                0,
                0,
                "Imaginem",
                does="Focus Power: an illusory form both seen and heard, made "
                "and unmade at will. Realms of Power: Magic p. 102.",
            ),
            b.power(
                "Master of Illusion",
                1,
                0,
                "Imaginem",
                level=10,
                does="Focus Power: alters the look of what he touches, as any "
                "Muto or Perdo Imaginem effect of level 10 or less, at 1 Might "
                "point a magnitude, always like stage props, scenery or "
                "costume. Init 0 minus the points spent.",
            ),
        ],
        equipment="A long white toga and various ephemeral props and masks.",
        appearance="An aging man with white hair and pale skin, dark dazzling "
        "eyes and a trained actor's mobile face. He moves with care, and his "
        "hands, like his expressions, are seldom still, marking every "
        "phrase. Illusions fill the theater around him with backcloth, "
        "scenery, props and sometimes other players.",
        notes="He contains no vis. His illusions spend his Might and leave "
        "him drained after each performance. Nervous of strangers, having been "
        "killed by one in life, he is welcoming once reassured. " + wound_ranges(0),
        secrets=[
            titled(
                "Seiffeddin remembers Conciatta",
                "He remembers Conciatta and her quest for Tartessos.",
            ),
            titled(
                "Seiffeddin's teaching",
                "He taught Conciatta and Currito, with other spirits of Qadis, "
                "over a year, and under him they made a set of stones that "
                "added power to their magic; he offers the magi the same "
                "teaching.",
            ),
            titled(
                "The way to Tartessos",
                "He can say how to reach Tartessos: only on the anniversary of "
                "its loss, a night the storyguide sets, and they must find "
                "Bruja out on the marsh (pp. 34-35).",
            ),
            titled(
                "The casting stones",
                "Seiffeddin's stones are ceremonial casting props (Houses of "
                "Hermes: Societates p. 59). A season of Magic Lore under him is a source "
                "of insight for Insight of the Realms, +10 to the initial roll. "
                "The maga must then enchant Clearing the Mind of the Caster, PeIm "
                "(Vi) 30, Pen +0, 1/day (R Touch, D Ring, T Circle): fifteen slate "
                "tablets, laced with leather and each carved with a symbol, laid "
                "around the caster in three rounds. Sensations not of the Magic "
                "realm are dulled as they cross in, though she may still attend "
                "to them; +1 to Concentration for activities wholly within, +3 "
                "as props in ceremonial casting. Re-creating it gives 6 points "
                "toward Insight of the Realms (p. 33).",
            ),
        ],
    )
    b.creature(
        "Bruja, the Marsh Witch",
        page="p. 37",
        realm="Faerie",
        might=15,
        form="Corpus",
        soak=2,
        place=sites["marsh"],
        block={
            "characteristics": characteristics(1, 1, -3, 0, 1, 2, 3, 1),
            "virtues_flaws": [
                *["Focus Power"] * 2,
                "Greater Power",
                "Faerie Sight",
                "Faerie Speech",
                "Lesser Power",
                "Humanoid Faerie",
                "Incognizant",
            ],
            "abilities": [
                ("Awareness", 3, "gifts"),
                ("Bargain", 6, "riches"),
                ("Brawl", 1, "claws"),
                ("Brew Potion", 4, "healing"),
                ("Chirurgy", 4, "treating poisons"),
                ("Faerie Speech", 5, "threats"),
                ("Folk Ken", 5, "seeing the evil of men"),
                ("Area Lore: Marsh", 3, "geography"),
            ],
            "traits": {"Irascible": 3, "Stubborn": 2},
        },
        attacks=[b.attack("Claws", 6, 7, 7, 3)],
        powers=[
            b.power(
                "Spirit Away",
                1,
                0,
                "Vim",
                does="Greater Power: a brewed potion adds Threshold Points to "
                "a character's Threshold Total, 1 Might point each. The "
                "character must already have a Threshold Total, and she cannot "
                "supply all the points needed. Init is its magnitude divided "
                "by 2.",
            ),
            b.power(
                "The Malicious Brew",
                1,
                -8,
                "Corpus",
                does="Focus Power: brews any Perdo Corpus effect with an "
                "Individual target up to 9th magnitude into a poison, Might "
                "points equal to magnitude. It grows toward a set moment "
                "(sunset, full moon, cockcrow), giving time for a cure. "
                "Intelligence + Medicine simple roll against 9 tells how long "
                "the target has. She regains the Might when the effect ends.",
            ),
            b.power(
                "The Merciful Brew",
                1,
                -9,
                "Corpus",
                does="Lesser Power: a healing potion, as Purification of the "
                "Festering Wounds but with a Duration of Season, so it serves "
                "those recovering from heavy wounds. It instantly relieves a "
                "Malicious Brew. Might points equal to magnitude, regained "
                "when the effect ends.",
            ),
        ],
        vis=[BodyVis(3, "Aquam", "in her legs")],
        appearance="A hunched crone, craggy and wrinkled, in a big-sleeved "
        "green cloak that trails behind her with plants growing in its "
        "threadbare weave. A satchel takes what she finds. She looks human "
        "until one sees her outsized lower legs, like a wading bird's, which "
        "carry her easily through the marsh.",
        notes=paragraphs(
            "The book prints her Abilities as Pretenses, and names Humanoid "
            "Form for what the catalog calls Humanoid Faerie. Her Virtues "
            "list Focus Power x2 though she has one Focus Power. " + wound_ranges(0),
            "Her powers pass through potions, poultices, possets, bandages or "
            "whatever suits, often leeches or foul mixes of animal parts and "
            "marsh water. The Might goes at the brewing, and the potion waits "
            "until applied. Most are brewed with a given person in mind, so "
            "cause no Warping.",
        ),
        secrets=[
            titled(
                "Bruja's price",
                "She will lead the characters to the gates if given a creature "
                "or herb not found in her marsh.",
            ),
            titled(
                "Bruja's potions",
                "She keeps no stock of potions, and brews each with spent "
                "Might; the Threshold draught is likely a live frog to be "
                "swallowed whole.",
            ),
            titled(
                "Safe passage",
                "Arganthonios can command her to give safe passage on a later "
                "visit (pp. 35-36, 39).",
            ),
        ],
    )
    b.creature(
        "Arganthonios, the Silver King",
        page="p. 38",
        realm="Faerie",
        might=35,
        form="Mentem",
        size=2,
        soak=5,
        place=sites["tartessos"],
        block={
            "characteristics": characteristics(0, 0, 3, 0, 4, 1, 0, -1),
            "virtues_flaws": [
                "External Vis (Major)",
                "Huge",
                *["Ritual Power"] * 2,
                "Faerie Speech",
                "Humanoid Faerie",
                *["Improved Soak"] * 2,
                ("Sovereign Ward", {"ward": "cannot leave Tartessos"}),
                "Depressed",
                "Incognizant",
                "Role Requires Suffering",
            ],
            "abilities": [
                ("Athletics", 4, "running"),
                ("Awareness", 3, "searching"),
                ("Bargain", 3, "foreigners"),
                ("Brawl", 5, "grappling"),
                ("Etiquette", 3, "messengers"),
                ("Faerie Lore", 3, "Iberian faeries"),
                ("Folk Ken", 4, "peasants"),
                ("Great Weapon", 5, "long spear"),
                ("Intrigue", 4, "spies"),
                ("Leadership", 5, "intimidation"),
                ("Penetration", 5, "Mentem"),
                ("Area Lore: Tartessos", 5, "past glories"),
            ],
            "traits": {"Resigned": 3, "Commanding": 2, "Depressed": 2},
            "reputations": {"King of a Lost City (Iberia)": 3},
        },
        attacks=[
            b.attack("Grappling", -2, 6, 4, 4),
            b.attack("Long spear", 1, 9, 5, 11),
        ],
        powers=[
            b.power(
                "Binding Oath",
                10,
                -22,
                "Vim",
                rtd=("Touch", "Mom", "Group"),
                does="Ritual; no Hermetic equivalent. Enforces an oath freely "
                "sworn between two or more parties, penetrating the Magic "
                "Resistance of all. If one acts against it the others know at "
                "once. A human oath-breaker sees Arganthonios in every "
                "reflective surface; one who ignores that is struck blind, as "
                "the Flaw. That ends through powers that destroy mystical "
                "effects, by fulfilling the oath, by a new oath with the "
                "wronged faerie, or by destroying all the oath's other "
                "parties. Faeries cannot break oaths, though some roles seek "
                "loopholes.",
            ),
        ],
        vis=[BodyVis(7, "Mentem", "in the crown he wears")],
        equipment="A silver crown of laurel leaves, too large for a mortal "
        "head. A great spear with a silver shaft, an ivory head and a binding "
        "hung with peacock feathers.",
        appearance="A giant over eight feet tall, muscled like an oversized "
        "Greek statue, his body and beard of shining fluid silver and his "
        "brow heavy under his crown. He sits brooding on a raised dais in "
        "the ruined throne room, and when he speaks his voice is low, smooth "
        "and full of calm command.",
        notes="The crown is his External Vis, and gives its wearer Puissant "
        "Leadership and the Reclusive Flaw. He is Incognizant: for all his "
        "understanding he cannot change or better his role. The book spells "
        "them Pretences; Tartessos Lore is entered as an Area Lore. " + wound_ranges(2),
        secrets=[
            titled(
                "A king who endures loss",
                "Alone but for his queen, it is his nature to endure loss, and "
                "he frees her freely (p. 38).",
            ),
            titled(
                "His bargain with Conciatta",
                "He made a bargain with Conciatta: she would rule beside him "
                "for knowledge of Faerie places, at the cost of renouncing her "
                "love for Currito.",
            ),
            titled(
                "His offer to the characters",
                "He explains what became of Conciatta, and offers that if the "
                "characters reunite this remnant with that love, he will "
                "release her to the world of men. If they cannot meet it yet, "
                "he gives them leave to go and return, and commands Bruja to "
                "grant safe passage (pp. 38-39).",
            ),
        ],
    )
    b.creature(
        "Narixa Hyena",
        page="p. 42",
        realm="Infernal",
        might=10,
        size=-1,
        how_many="In packs",
        soak=4,
        fatigue_levels=FATIGUE,
        place=sites["caves"],
        block={
            "characteristics": characteristics(3, 0, -2, 0, -1, 3, 2, 2),
            "virtues_flaws": [
                "Ferocity",
                *["Improved Characteristics"] * 2,
                "Long-Winded",
                "Sharp Ears",
                ("Compulsion (Minor)", {"detail": "killing"}),
                "Infamous",
                "Pack Animal",
                "Thick Fur/Thick Scales",
                *["Improved Powers"] * 2,
                "Lesser Power",
            ],
            "abilities": [
                ("Living Language: Arabic", 5, "taunts"),
                ("Athletics", 5, "distance running"),
                ("Awareness", 3, "smell"),
                ("Brawl", 5, "bite"),
                ("Hunt", 4, "track by smell"),
                ("Area Lore: Narixa Caves", 3, "regiones"),
                ("Survival", 3, "Narixa caves"),
            ],
            "traits": {
                "Brave When in a Pack": 3,
                "Cowardly When Alone": 3,
                "Hyena": 5,
            },
            "reputations": {"Bloodthirsty (Local)": 4},
        },
        attacks=[b.attack("Bite", 2, 11, 9, 0)],
        powers=[
            b.power(
                "Piercing the Infernal Veil",
                0,
                1,
                "Vim",
                does="Sees through the boundaries between regio levels. "
                "Improved Powers has brought its cost to 0 and raised its "
                "initiative.",
            ),
        ],
        appearance="Powerful shoulders, a sloping back and short rear legs "
        "make it look craven, but on the hunt it is nothing of the kind. It "
        "smiles at its prey's fear, and its eyes shine yellow in the dark.",
        notes="Ferocity applies against livestock. They roam the caves and "
        "leave them to hunt, more like wolves than natural hyena. A pack "
        "fights as a trained group: treat the Hyena trait as a score in "
        "Leadership. The book prints wounds of -1 (1-4), -3 (5-8), -5 (9-12), "
        "Incapacitated (13-16), Dead (21+); by those ranges Dead would be 17+.",
    )
    b.creature(
        "Scorpion Swarm",
        page="p. 44",
        size=1,
        how_many="In swarms",
        cunning=True,
        soak=0,
        fatigue_levels=FATIGUE,
        place=sites["caves"],
        block={
            "characteristics": characteristics(-1, -2, -5, -6, 2, 0, 2, 4),
            "virtues_flaws": ["Lightning Reflexes", "Infamous", "Venomous"],
            "abilities": [
                ("Area Lore: Narixa Caves", 4, "regiones"),
                ("Athletics", 5, "running"),
                ("Awareness", 2, "prey"),
                ("Brawl", 4, "sting"),
                ("Hunt", 4, "rodents"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 3, "caves"),
            ],
            "traits": {"Scorpion": 5},
            "reputations": {"Deadly (Local)": 4},
        },
        attacks=[b.attack("Sting", 8, 9, 3, 3)],
        appearance="A great shifting black sand of chitin and noise, covering "
        "everything in its path.",
        notes=paragraphs(
            "Venomous (Houses of Hermes: Mystery Cults p. 43), at the level "
            "of an Asp's bite (ArM5 p. 180). The scent of magic maddens them, "
            "and they surge past defenders to reach magi (p. 44). The book "
            "prints wounds of -1 (1-6), -3 (7-12), -5 (13-18), Incapacitated "
            "(19-24), Dead (21+); by those ranges Dead would be 25+.",
            "Optional swarm rules, for creatures of Size -3 or less totalling "
            "Size +1 or more: a swarm ignores defenders; it attacks as many "
            "targets each round as its Size; at the storyguide's discretion it "
            "may resist or ignore regular weapons; and unless destroyed "
            "outright it can disengage and come back at full strength after "
            "as many rounds as its highest wound penalty.",
        ),
    )


def _ghosts(b: Builder, qadis: Neighbour) -> None:
    b.faction(
        "The Ghosts of Qadis",
        faction="Spirits and beings",
        place=qadis,
        realm="Magic",
        summary="The dead of Qadis, perhaps a thousand or more, who have "
        "accepted that they persist and get on with their affairs by night. "
        "They split into factions by nation, former calling and era.",
        decides="By how well each recalls mortal life; lucid apparitions rule "
        "and use mindless specters as tools.",
        wants="To protect their interests, descendants and city; few care "
        "to be laid to rest.",
        secrets=[
            titled(
                "Faerie ghosts",
                "Faeries, drawn to Qadis for centuries, now fill the roles of "
                "the recently dead, who mostly get proper burial and do not "
                "linger. They think themselves ghosts, differ only in their "
                "Might, and feed on the living by quietly touching their lives.",
            ),
            titled(
                "Demons among the dead",
                "Demons take the forms of the dead of Qadis too, to corrupt the "
                "living, and the Magic and Faerie ghosts fight them as best "
                "they can.",
            ),
            titled(
                "Storyguide Notes",
                "The ranks follow the ghost types of Realms of Power: Magic p. "
                "115, with apparitions at the top (p. 35).",
            ),
        ],
    )


def _stories(b: Builder, sites: dict[str, Neighbour]) -> None:
    """The hunt, and the chapter's story seeds, for the storyguide to begin."""
    dormant(
        b.threat(
            "The Four Corners of the World",
            place=sites["torre"],
            antagonist="The Infernal Conciatta",
            summary=paragraphs(
                "Conciatta's spirit is sundered, with an aspect in each of "
                "four auras or regiones across Iberia: her sanctum, the "
                "convent of her last years, the sunken faerie city of "
                "Tartessos, and the depths of the Narixa caves. Whoever finds "
                "them may gather her treasures and make her whole.",
            ),
            secrets=[
                titled(
                    "Her secrets brought back",
                    "Whoever brings Conciatta's secrets back ties his name to "
                    "hers; whoever takes them further wins fame of his own.",
                ),
                titled(
                    "Storyguide Notes",
                    paragraphs(
                        "It can run as one story or as separate episodes, moving the "
                        "clues to spread it out (p. 18). The history and the journal "
                        "come in either order, and the four aspects in any order "
                        "the troupe likes (p. 19); the numbers on this track are only "
                        "the book's order of telling.",
                        "Foreshadowing (p. 19): raise her name in unrelated stories. "
                        "Run stories that turn on auras, or on the lack of any way "
                        "to find what anchors one. Old casting tablets on auras, "
                        "books or devices Currito took, her glosses in others' works, "
                        "and his frescoes may all surface; any study of Vim from a "
                        "book can bring up her name.",
                        "Moving it (p. 19): Tartessos could be Sybaris in the Roman "
                        "Tribunal, Zaragoza could be Paris with the Seine for the "
                        "Ebro, and Jerusalem could stand for Toledo.",
                        "Rewards (p. 45): a suggested 5 experience points for the "
                        "events around each aspect, 20 in all. Experience in the "
                        "Magic Realm comes as vis that can transform a character "
                        "(Realms of Power: Magic pp. 20, 26). Bonisagus Acclaim: "
                        "Houses of Hermes: True Lineages p. 21 and p. 45 here.",
                        "Aftermath (p. 45): magi still need a separate effect for "
                        "each realm. Letting Vim spells affect every realm without "
                        "re-invention would be a Hermetic Breakthrough, which her "
                        "Virtues reduce to a Major Breakthrough, with troupe approval; "
                        "a further Major Breakthrough can fully integrate each of "
                        "hers, so that all who study the sources may use Realm Lore.",
                    ),
                ),
            ],
            stages=[
                S(
                    "History Unfolding",
                    at=1,
                    clues="During a story of the Magic Realm the magi find "
                    "tempora of her life: pick the one that fits and let the "
                    "players explore. They give her past, hints of her "
                    "discoveries and fate, and where her sanctum was.",
                ),
                S(
                    "Currito's Journal",
                    at=2,
                    clues="A delegation brings one magus news that his pater "
                    "has died or gone to Final Twilight, with a tattered "
                    "heirloom in an unknown hand and word to read it well. It "
                    "is Currito's book, and each delegate wants it: a "
                    "Quaesitor who suspects foul play, a Bonisagus who wants "
                    "its magic public, and a Redcap who offers a small fortune "
                    "for Zebulon. It may instead lie in the covenant's library "
                    "or in Currito's old sanctum (pp. 21-22).",
                ),
                S(
                    "The Tower by the Water",
                    at=3,
                    clues="The Mercere records, or watching the birds, lead "
                    "to Reyes de Barbastro's warehouse in Zaragoza. See La "
                    "Torre no Vista.",
                    stopped="Fresco and journal together give the ritual that "
                    "opens the way to the Magical Conciatta (pp. 22-27).",
                ),
                S(
                    "Her Final Resting Place",
                    at=4,
                    clues="Prudencia guards the possessed novice Immaculada "
                    "outside Toledo. The characters must win access, then "
                    "decide how to deal with what they find; the setting asks "
                    "for mercy and sacrifice. The girl's words point to "
                    "Seiffeddin in Qadis.",
                    stopped="Her fear of being alone is eased, and the Divine "
                    "Conciatta passes to a willing new host (pp. 27-32).",
                ),
                S(
                    "The Lost City",
                    at=5,
                    clues="In Qadis the dead know Seiffeddin, who sends them "
                    "to Bruja on the marsh, on the one night the gates open.",
                    ignored="They fail three of the city's tests and are "
                    "turned back to the mundane world.",
                    stopped="Reminded of Currito's love, the Faerie Conciatta "
                    "is released and leaves in Bruja's book (pp. 32-39).",
                ),
                S(
                    "The Descent",
                    at=6,
                    clues="Hamid ibn Harun finds them Conciatta's scrolls; the "
                    "caves lie two miles east of Narixa.",
                    stopped="The Infernal Conciatta is bound or captured, "
                    "however the troupe contrives it, and carried off "
                    "(pp. 39-45).",
                ),
                S(
                    "The Return",
                    at=7,
                    clues="In the tower wait the scholar, the Divine spirit in "
                    "its host, the bound Infernal aspect, who curses them all "
                    "and shocks the Magical one, and the Faerie self in its "
                    "book.",
                    ignored="If any aspect is destroyed along the way, all "
                    "perish at that moment.",
                    stopped="By a rite of the troupe's devising, the Faerie "
                    "self steps from the book and the Divine rises from the "
                    "host. Divine joins Infernal, Faerie joins Magic, and "
                    "these two become one white-burning shard that pierces "
                    "floor and ceiling and flashes through all present. For "
                    "a moment the Magic Realm opens with scenes of her life "
                    "on the walls, and then she is gone. She leaves 12 pawns "
                    "of Vim vis in crystal shards (p. 45).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Invisible Enemy",
            antagonist="Possessing spirits riding a messenger",
            summary="A private messenger comes from a magus of a foreign "
            "Tribunal, who is said to be curious about Currito of Jerbiton's "
            "early years, and offers a good price for the journal. It seems "
            "odd that the master will not settle for a chance to study it: he "
            "wants the book itself.",
            secrets=[
                titled(
                    "What the messenger carries",
                    "The messenger unknowingly carries possessing spirits "
                    "across the Aegis (Realms of Power: The Infernal p. 32).",
                ),
                titled(
                    "The spirits' hunt",
                    "Inside the Aegis, the messenger's possessing spirits hunt "
                    "for the book and spread fear and mischief (p. 21).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Generous Knight of Santiago",
            place=sites["toledo"],
            realm="Infernal",
            antagonist="The debauched Infernal aura of a knight's feast",
            summary="A knight of Santiago befriended on the road invites the "
            "characters to his castle for his birthday, and his wife has "
            "brought food, wine and players from all Iberia. His dour priest "
            "scorns the excess and refuses the feast.",
            secrets=[
                titled(
                    "The priest's warning",
                    "The knight's priest may be right: the feast has a "
                    "debauched Infernal aura.",
                ),
                titled(
                    "Storyguide Notes",
                    "How long until the magi notice the debauched Infernal "
                    "aura? Will they give in? And must they either let the "
                    "devil win or damage the knight's name (p. 28)?",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Books of Al-Mu'taman",
            place=sites["zaragoza"],
            antagonist="None; a lineage to find and bargain with",
            summary="Yusuf ibn Ahmad al-Mu'taman ibn Hud ruled Zaragoza from "
            "1082 to 1085 and wrote at length on geometry. Readers of his "
            "works find references to magic there too.",
            secrets=[
                titled(
                    "Al-Mu'taman's line",
                    "Al-Mu'taman was a Learned Magician (Hedge Magic Revised "
                    "Edition p. 79), of a line that taught Conciatta its ways "
                    "past the ill effects of auras.",
                ),
                titled(
                    "What his line could teach",
                    "Modern magi might learn much from al-Mu'taman's line, if "
                    "they can be found and bargained with (p. 23).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Spirit-Binders of Qadis",
            place=sites["qadis"],
            antagonist="The united ghosts of Qadis",
            summary="Workers of spirit magic come to Qadis from time to time "
            "in search of strong new servants. Those allowed to leave go away "
            "disappointed.",
            secrets=[
                titled(
                    "The ghosts unite",
                    "The ghosts of Qadis will not stand for any attempt to "
                    "control them, and unite against whoever tries (p. 35).",
                ),
            ],
        )
    )


def build(b: Builder) -> None:
    sites = _sites(b)
    _legends(b)
    _people(b)
    _aspects(b, sites, sites["torre"])
    _creatures(b, sites)
    _ghosts(b, sites["qadis"])
    _stories(b, sites)
