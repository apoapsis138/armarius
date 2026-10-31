"""Baron Geoffroi d'Arques (Antagonists pp. 6, 8-23), in paraphrase.

The book prints one block for Geoffroi, at the start of his journey, and says
his scores change little afterwards but for the realm lores (p. 9): the record
holds that block, and his yearly advancement is in its notes. Ysabeau, Claude
de Fécamp and Edwin Locke have the book's blocks; the rest of the family and
the council's wizards are sketches, and the disguised faerie is a creature with
no figures. The story is one dormant threat, a stage for each of the book's
methods, with its seeds as threats of their own. The sample items are devices
nobody holds yet; the sample inceptions, reagents and theriacs have no maker in
the book, so they are listed in the council's secrets."""

from __future__ import annotations

from ... import storage
from ...models import (
    CHARGED,
    INVESTED,
    Character,
    EnchantedDevice,
    InstilledEffect,
    Neighbour,
)
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    vf_art,
)

S = Builder.stage
BARON = "Baron Geoffroi d'Arques"
COUNCIL = "Geoffroi's Council of Wizards"
TRACK = "A track"
WOUNDS = (
    "Fatigue levels: OK, 0, -1, -3, -5, Unconscious. Wound penalties: -1 (1-5), "
    "-3 (6-10), -5 (11-15), Incapacitated (16-20), Dead (21+)."
)
_LATIN = "Dead Language: Latin"
_LOCAL_LANGUAGE = "Living Language: (Local)"
_NORMAN_FRENCH = "Living Language: Norman French"


def build(b: Builder) -> None:
    arques, school = _places(b)
    geoffroi, ysabeau, claude = _household(b)
    children = _children(b)
    barony = _barony(b, arques, geoffroi, ysabeau, claude, children)
    locke = _locke(b, school)
    council = _council(b, geoffroi, locke)
    _items(b)
    _story(b, barony, council)
    _seeds(b)


def _places(b: Builder) -> tuple[Neighbour, Neighbour]:
    arques = b.place(
        "Arques",
        realm="",
        summary=(
            "A lordship in the Duchy of Normandy, and the birthplace of its "
            "baron. His family's fortune was made there when King John lost "
            "his French holdings and they stood with the winners."
        ),
    )
    school = b.university(
        "York Cathedral School",
        summary=(
            "The cathedral school of York in the north of England, where "
            "Edwin Locke is a well-known tutor."
        ),
    )
    return arques, school


# -- the household --


def _geoffroi_block() -> StatBlock:
    return {
        "characteristics": characteristics(1, 0, 1, 0, 1, 1, 2, 0),
        "size": 0,
        "warping": (0, 1),
        "confidence": (1, 3),
        "virtues_flaws": [
            "Landed Noble",
            "Knight",
            "Wealthy",
            (
                "Driven (Major)",
                {"detail": "Learn all there is about the supernatural"},
            ),
            "Oath of Fealty",
            "Reckless (Minor)",
        ],
        "traits": {"Driven": 3, "Brave": 2, "Chivalrous": 1},
        "reputations": {
            "Prudhomme (nobles of England and France)": 3,
            "Excellent soldier (the continental tourney circuit)": 2,
            "Lord of Arques (Normandy population)": 2,
        },
        "abilities": [
            ("Animal Handling", 3, "falconry"),
            ("Area Lore: Arques", 3, "nobles"),
            ("Artes Liberales", 2, "arithmetic"),
            ("Athletics", 2, "running"),
            ("Awareness", 3, "battle"),
            ("Brawl", 2, "fist"),
            ("Charm", 2, "first impressions"),
            ("Chirurgy", 1, "sword wounds"),
            ("Etiquette", 3, "noble"),
            ("Living Language: French", 5, "giving orders"),
            ("Great Weapon", 4, "great sword"),
            ("Hunt", 4, "deer"),
            ("Intrigue", 4, "noble courts"),
            (_LATIN, 3, "church ceremonies"),
            ("Leadership", 4, "in battle"),
            ("Music", 2, "singing"),
            ("Ride", 5, "in combat"),
            ("Single Weapon", 5, "long sword"),
            ("Survival", 1, "forests"),
        ],
        "notes": paragraphs(
            "As printed at the start of his story, just as the fascination "
            "takes him (Ant p. 9). The book prints no later block: his scores "
            "change little, except that his knowledge of the realms grows.",
            "Combat, with superior arms and armor counted: Dodge Init -2, "
            "Defense +2. Fist Init -2, Attack +5, Defense +3, Damage +1. Lance "
            "and heater shield (mounted) Init +0, Attack +14, Defense +12, "
            "Damage +6. Long sword and heater shield Init +0, Attack +12, "
            "Defense +11, Damage +7. Long sword and heater shield (mounted) "
            "Init +0, Attack +15, Defense +14, Damage +7. Great sword Init +0, "
            "Attack +13, Defense +8, Damage +10. Soak +11. Encumbrance 3 (4).",
            WOUNDS,
            "Equipment: superior full chain armor (+1 soak), superior long "
            "sword (+1 attack), superior heater shield (+1 defense), a great "
            "sword, and a horse for every occasion.",
            "Advancement (Ant p. 9): Wealthy gives him three free seasons, for "
            "20 experience points a year: two seasons taught at quality 7, 14 "
            "points in one or two Abilities; a season's practice at quality 4 "
            "in a martial Ability; and a season's exposure, 2 points in a "
            "language or Order of Hermes Lore. Once his Latin is better he "
            "takes tuition in the four realm lores as tutors can be found.",
            "Optional rule (Ant p. 9): a troupe may give him Ability Block "
            "(Supernatural), balanced by Temporal Influence. The book offers "
            "this as a choice and does not list either in his block.",
        ),
    }


def _ysabeau_block() -> StatBlock:
    return {
        "characteristics": characteristics(1, 0, 2, 2, -1, -1, 2, -1),
        "size": 0,
        "warping": (0, 0),
        "confidence": (1, 3),
        "virtues_flaws": [
            "Gentleman/woman",
            "Educated",
            "Privileged Upbringing",
            "Temporal Influence",
            "Dependent",
            "Humble",
        ],
        "traits": {"Humble": 2, "Protective": 2, "Honest": 1},
        "reputations": {"Geoffroi's wife (within the county)": 3},
        "abilities": [
            ("Animal Handling", 1, "horses"),
            ("Area Lore: Arques", 2, "personalities"),
            ("Artes Liberales", 2, "music"),
            ("Awareness", 2, "alertness"),
            ("Carouse", 2, "staying sober"),
            ("Charm", 5, "first impressions"),
            ("Etiquette", 5, "nobility"),
            ("Folk Ken", 2, "nobles"),
            ("Guile", 3, "avoiding offence"),
            (_LATIN, 4, "church ceremonies"),
            ("Leadership", 2, "servants"),
            (_LOCAL_LANGUAGE, 3, "local dialect"),
            ("Music", 3, "sing"),
            (_NORMAN_FRENCH, 5, "Arques dialect"),
            ("Organization Lore: Household", 3, "personalities"),
            ("Ride", 3, "recreation"),
        ],
        "notes": paragraphs(
            "Stat block: Ant p. 11. A minor supporting character, with few "
            "Virtues and Flaws; the book invites a troupe to add to her.",
            "Combat: Dodge Init -1, Defense -1. Fist Init -1, Attack +2, "
            "Defense -1, Damage -1. Soak -1. Encumbrance 0 (0).",
            WOUNDS,
            "Equipment: an elegant gown and a superior gold necklace, which "
            "adds +1 to first-impression Charm rolls: her Charm is printed "
            "5 + 1.",
        ),
    }


def _claude_block() -> StatBlock:
    return {
        "characteristics": characteristics(2, 2, -1, 0, 0, 1, -1, -1),
        "size": 0,
        "warping": (0, 4),
        "confidence": (1, 3),
        "virtues_flaws": [
            "Clerk",
            "Guardian Angel",
            "Clear Thinker",
            "Sharp Ears (Minor)",
            "Strong-Willed",
            "Oath of Fealty",
            "Missing Hand",
            "Noncombatant",
            "Temperate",
            "Weak Characteristics",
        ],
        "traits": {"Loyal": 3, "Taciturn": 2, "Frivolous": -1},
        "reputations": {"Geoffroi's right-hand man (within Geoffroi's court)": 2},
        "abilities": [
            ("Area Lore: Arques", 3, "personalities"),
            ("Area Lore: (Local)", 1, "geography"),
            ("Artes Liberales", 2, "logic"),
            ("Profession: Steward", 4, "noble manors"),
            ("Church Lore", 3, "personalities"),
            (_LOCAL_LANGUAGE, 5, "local dialect"),
            ("Etiquette", 2, "nobility"),
            ("Folk Ken", 3, "nobles"),
            ("Guile", 2, "discerning lies about his master"),
            ("Intrigue", 2, "alliances"),
            (_LATIN, 4, "academic usage"),
            ("Leadership", 2, "household staff"),
            (_NORMAN_FRENCH, 5, "County of Rouen dialect"),
            ("Philosophiae", 2, "moral philosophy"),
            ("Theology: Christian", 3, "biblical knowledge"),
        ],
        "notes": paragraphs(
            "Stat block: Ant p. 12.",
            "Combat: Dodge Init -4, Defense -4. Soak +1, or +6 with the +5 his "
            "guardian angel grants. Encumbrance 0 (0).",
            WOUNDS,
            "Divine Resistance 15: the angel gives him Magic Resistance +15 "
            "aligned with the Divine while he acts in accord with God's will.",
            "Equipment: a plain monk-style habit, a wooden crucifix, and a "
            "purse usually holding enough for most expenses.",
        ),
    }


def _household(b: Builder) -> tuple[Character, Character, Character]:
    geoffroi = b.magus(
        BARON,
        covenant=None,
        house="",
        age=32,
        type="companion",
        summary=paragraphs(
            "A wealthy Norman nobleman of thirty-two, baron of Arques and "
            "lately come to look after some distant manors he had long "
            "ignored. He is a superb soldier, known on the French tourney "
            "circuit, and astute enough to know that he is no great "
            "politician. He is married with several children, one of them "
            "an acknowledged bastard, has few enemies, and has always been "
            "a God-fearing man who takes faeries and unicorns for tales.",
        ),
        secrets=paragraphs(
            "His first brush with the supernatural turns into an obsession. "
            "He wants it for three reasons: plain curiosity, in an idle and "
            "secure lord; display, since a noble who commands an enchanter "
            "outshines one who pays a painter, and can give magical prizes "
            "and gifts and keep a veiled threat over his rivals; and use, "
            "with crops, spies and victories to be had from the right "
            "magician (Ant p. 13).",
            "He can never learn a Supernatural Ability himself. He attempts "
            "Initiations, but he is too much the master of his domain to be "
            "anyone's apprentice, so they all fail, and he contents himself "
            "with keeping those who have the gifts he lacks (Ant p. 9). Every "
            "time he reappears after the first meeting he should have some "
            "new magical possession to show off (Ant p. 10).",
            "He suspects, but cannot be sure, that François is his son, and "
            "may have an astrologer settle it (Ant pp. 10, 21).",
            "Relocating him (Ant pp. 8-10): he is a lesser baron and need "
            "not stay one. He needs enough wealth to spend his time on this, "
            "secure lands, and holdings both near the covenant and far "
            "enough off to explain long absences. In a saga set near Arques, "
            "move his old lands elsewhere. The local manors may be a dowry, "
            "an inheritance, or won by conquest or at a tourney.",
        ),
    )
    b.stats(geoffroi, _geoffroi_block())
    geoffroi.description.physical_description = (
        "Clean-shaven, upright and well turned out, with the best of "
        "everything about him, from armor and travelling clothes to the gold "
        "rings on his fingers, and a horse, saddle and barding to match."
    )

    ysabeau = b.magus(
        "Ysabeau",
        covenant=None,
        house="",
        age=25,
        type="companion",
        summary=(
            "The baron's wife and the mother of his three legitimate "
            "children, a young woman of twenty-five. She runs her household "
            "with assurance and is modest and quiet before her husband and "
            "his guests."
        ),
        secrets=paragraphs(
            "Her first care is the safety and future of her children. She "
            "loves Geoffroi, but as his obsession grows she can be brought "
            "to put them before him, which makes her the weak link the "
            "characters can work on (Ant pp. 10, 11). She knows of Guillaume "
            "and does not know of François.",
            "Near the end she fears for her children, for his people, and "
            "that his lands will fall to his wizards or to knights picking "
            "over his failing estates. She can tell the covenant what is "
            "planned for Alenard, who is to take him, and that for all his "
            "Initiations Geoffroi has never learned the least piece of magic "
            "(Ant p. 19).",
        ),
    )
    b.stats(ysabeau, _ysabeau_block())
    ysabeau.description.physical_description = (
        "An attractive young woman, always elegantly dressed, and fond of a "
        "golden necklace her husband gave her not long ago."
    )

    claude = b.magus(
        "Claude de Fécamp",
        covenant=None,
        house="",
        age=28,
        type="companion",
        summary=(
            "The baron's steward, twenty-eight, trusted with much of his "
            "business and met as often as the baron himself. Schooled at a "
            "Benedictine monastery, he has served the household for six "
            "years and is known for his loyalty and sobriety."
        ),
        secrets=paragraphs(
            "In his first year he resented his master's wealth and his own "
            "place, and made enemies. One night persons unknown beat him "
            "almost to death, and an angel enfolded him and showed him his "
            "faults. He renewed his loyalty and gave up his old ways, and the "
            "angel promised him protection while he stays true. The household "
            "barely remembers the man he was (Ant p. 12).",
            "He is loyal to the end and cannot be turned by mundane means (Ant p. 10).",
        ),
    )
    b.stats(claude, _claude_block())
    claude.description.physical_description = (
        "A slight man, neither tall nor short, bald by the razor, with a "
        "long and sober face. His right arm stops at the elbow, and he "
        "keeps the empty sleeve of his habit pinned up."
    )
    b.link(geoffroi, "characters", ysabeau, "his wife")
    b.link(geoffroi, "characters", claude, "his steward")
    return geoffroi, ysabeau, claude


def _children(b: Builder) -> dict[str, Character]:
    """Their ages are at the start of the baron's story."""
    return {
        "guillaume": b.magus(
            "Guillaume",
            covenant=None,
            house="",
            age=12,
            type="companion",
            summary=(
                "The baron's eldest son, twelve, a bastard by a woman of low "
                "birth, openly acknowledged. He is getting his education on "
                "the Normandy tourney circuit."
            ),
            traits={"Loyal": 2},
            secrets=(
                "Geoffroi means to give him much of his land as an appanage, "
                "held until Guillaume's death. If the baron is left to decline, "
                "Guillaume is among those fighting over the estates "
                "(Ant pp. 19, 20)."
            ),
        ),
        "francois": b.magus(
            "François",
            covenant=None,
            house="",
            age=10,
            type="companion",
            summary=(
                "A boy of ten, brought up as the son of a man of rank in Normandy."
            ),
            traits={"Loyal": 0},
            secrets=(
                "He is the baron's bastard by a married woman of rank, though "
                "only she and Geoffroi suspect it and neither can be sure, and "
                "the boy knows nothing. Her resentment of Geoffroi has kept "
                "his Loyalty at 0. Made public, it would set a vengeful "
                "cuckold on the baron's Norman lands (Ant pp. 10, 20)."
            ),
        ),
        "alenard": b.magus(
            "Alenard",
            covenant=None,
            house="",
            age=7,
            type="companion",
            summary=(
                "The baron's son and heir, seven years old and as demanding "
                "a young prince as any."
            ),
            traits={"Loyal": 2},
            secrets=(
                "His Loyalty may change as he grows and understands where he "
                "stands beside his brothers. Geoffroi means him for magic, "
                "and promises him to one of the court's wizards (Ant pp. 10, "
                "16, 19). He comes to resent how his father has used him."
            ),
        ),
        "joie": b.magus(
            "Joie",
            covenant=None,
            house="",
            age=5,
            type="companion",
            summary="The baron's elder legitimate daughter, five years old.",
            traits={"Loyal": 2},
        ),
        "viollette": b.magus(
            "Viollette",
            covenant=None,
            house="",
            age=3,
            type="companion",
            summary="The baron's younger legitimate daughter, three years old.",
            traits={"Loyal": 2},
        ),
    }


def _barony(
    b: Builder,
    arques: Neighbour,
    geoffroi: Character,
    ysabeau: Character,
    claude: Character,
    children: dict[str, Character],
) -> Neighbour:
    barony = b.lord(
        "The Barony of Arques",
        title="baron",
        wealth="Wealthy",
        manors=10,
        seat="Arques",
        ruler=BARON,
        place=arques,
        summary=paragraphs(
            "A lesser barony of ten manors, owing the service of ten knights "
            "and a hundred infantry. Its lands lie partly round Arques in "
            "Normandy and partly in a few sizable manors near the covenant, "
            "where the baron has not lived long enough to learn the language.",
            "At first his court looks like that of any rich noble, if with "
            "an eye for the unusual and a readiness to pay for the best.",
        ),
        secrets=(
            "Every family tie is a lever: track the children's ages, because "
            "the baron's marriages for them and his fears for them can be "
            "used against him (Ant p. 10). As a wealthy lord he need give "
            "only a season a year to his estates, and in time he fails even "
            "that (Ant p. 17)."
        ),
    )
    b.link(barony, "characters", geoffroi, "the baron")
    b.link(barony, "characters", ysabeau, "the baron's wife")
    b.link(barony, "characters", claude, "the steward")
    for key, child in children.items():
        if key != "francois":  # his parentage is a secret
            b.link(barony, "characters", child, "the baron's child")
    return barony


# -- the wizards --


def _locke(b: Builder, school: Neighbour) -> Character:
    locke = b.magus(
        "Edwin Locke",
        covenant=None,
        house="",
        age=40,
        type="mythic companion",
        traditions=["trad_elementalists"],
        summary=(
            "An academic from the north of England and a prominent tutor at "
            "York's cathedral school, forty years old, with the look of a man "
            "left permanently unamused by his students."
        ),
        secrets=paragraphs(
            "An elementalist, unGifted. He neither hides his magic from his "
            "colleagues nor discusses it, and lives two lives, one in the "
            "cathedral and one among spirits and supernatural beasts. He knows "
            "little of the realms themselves, but knows of other traditions "
            "and of the Order, and sees meeting them as an intellectual "
            "challenge (Ant p. 16). He is the likeliest of the wizards to "
            "go out and bring others to the court (Ant p. 12), and may "
            "take Claude's place as steward (Ant p. 18).",
        ),
    )
    b.stats(
        locke,
        {
            "characteristics": characteristics(1, 0, 2, 0, 0, 2, 0, 0),
            "size": 0,
            "decrepitude": (0, 0),
            "warping": (1, 8),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Magister in Artibus",
                ("{type} Summoning (Major)", {"type": "Theurgical"}),
                ("{type} Controlling (Major)", {"type": "Theurgical"}),
                "Clear Thinker",
                "Elementalist Air",
                "Elementalist Earth",
                "Elementalist Fire",
                "Elementalist Water",
                "Luck",
                vf_art("Puissant {art}", "Elementalist Controlling"),
                "Overconfident (Major)",
                "Weak Elemental Resistance",
                ("Ability Block", {"abilities": "Martial"}),
                ("Mentor", {"detail": "Walter de Gray"}),
            ],
            "traits": {
                "Authoritative": 2,
                "Ordered": 1,
                "Choleric": 2,
                "Melancholic": 2,
                "Phlegmatic": 2,
                "Sanguine": 2,
            },
            "reputations": {
                "Tutor at York Cathedral School (among academics)": 2,
                "Elementalist of Repute (among elementalist societies)": 1,
            },
            "abilities": [
                ("Artes Liberales", 5, "grammar"),
                ("Carouse", 2, "games of chance"),
                ("Charm", 3, "being witty"),
                ("Etiquette", 1, "the Church"),
                ("Folk Ken", 2, "townsfolk"),
                ("Living Language: Greek", 3, "prose"),
                (_LATIN, 5, "academic usage"),
                ("Leadership", 2, "students"),
                ("Magic Lore", 2, "spirits"),
                ("Organization Lore: Order of Hermes", 1, "history"),
                ("Philosophiae", 5, "natural philosophy"),
                ("Teaching", 4, "Philosophiae"),
                ("Area Lore: York", 1, "personalities"),
                ("Elementalist Controlling", 15, ""),
                ("Elementalist Summoning", 15, ""),
                ("Elementalist Air", 4, ""),
                ("Elementalist Earth", 3, ""),
                ("Elementalist Fire", 4, ""),
                ("Elementalist Water", 3, ""),
            ],
            "notes": paragraphs(
                "Stat block: Ant p. 16. An unGifted Mythic Companion, who may "
                "take four more Virtues balanced by two further Flaws. The "
                "book prints his Arts as (Theurgical) Controlling 15 +3 and "
                "(Theurgical) Summoning 15, and the four Elementalist Forms "
                "as Difficult Arts.",
                "Combat: Dodge Init +0, Defense +0. Fist Init +0, Attack +0, "
                "Defense +0, Damage +0. Bludgeon Init -1, Attack +2, Defense "
                "+0, Damage +2. Soak +2. Encumbrance 0 (0).",
                WOUNDS,
                "Equipment: philosophical texts and an astrolabe.",
                "Vis: 4 pawns each of Aquam, Auram, Ignem and Terram, as "
                "glass-like crystals in small bottles of preservative oil, "
                "in a wooden case made for them.",
            ),
        },
    )
    locke.description.physical_description = (
        "A man well into middle age with thinning gray hair, confident and "
        "determined in his bearing."
    )
    mentor = b.magus(
        "Walter de Gray",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="The patron and adviser of Edwin Locke of York.",
    )
    b.link(locke, "characters", mentor, "his Mentor")
    b.link(school, "characters", locke, "a tutor here")
    return locke


#: The council's sample wizards: name, what is known of them, their secrets,
#: and the hedge traditions the book's heading gives them.
_WIZARDS: tuple[tuple[str, str, str, tuple[str, ...]], ...] = (
    (
        "Ádhamh Brathair",
        "A learned scholar from Hibernia at the baron's court. His name is "
        "said EWE BRO-hur.",
        "A learned magician, who means to build one unified theory of magic "
        "on sound philosophy. He studies his colleagues' magic and pursues "
        "the breakthroughs the theory needs.",
        ("trad_learned_magicians",),
    ),
    (
        "Dominici Viterbo",
        "A scholar who has lately joined the baron's court.",
        "A goetic sorcerer, desperate to escape a dark fate, who hopes to "
        "hide in the council. The demons of his past soon find him. By "
        "teaching others he may mend his mistakes and cleanse his arts of "
        "their corruption.",
        (),
    ),
    (
        "Hannelore of the Baron's Council",
        "A woman who has joined the baron's council of scholars.",
        "A student of the Maleficia who brings Infernal magic to the council "
        "for protection from Hermetic enemies of her past. She wants a "
        "direct road to influence, and sets out to take Ysabeau's place "
        "in the baron's affections.",
        (),
    ),
    (
        "Jabir Al-Qazwini",
        "An Arabic magus who has travelled far to the baron's court.",
        "An itinerant sahir, seeking a council of the wise that a powerful "
        "spirit of the sands promised him. He believes he has found it and "
        "stays to learn, seemingly blind to the baron's decline and the "
        "council's growing power.",
        (),
    ),
    (
        "Carles Peregrinus",
        "A man with a grievance, newly welcome at the baron's council.",
        "A failed Hermetic apprentice, denied what he sees as his place in "
        "the Order. He means to dominate the council through his strong "
        "Entrancement.",
        (),
    ),
)


def _council(b: Builder, geoffroi: Character, locke: Character) -> Neighbour:
    council = b.faction(
        COUNCIL,
        faction="Hedge coven",
        ruler=BARON,
        decides=(
            "The baron as patron, with the prominent and most socially "
            "tolerable members guiding him."
        ),
        wants=(
            "Learning from strange traditions, safety at court, and as much "
            "as the baron will give."
        ),
        offers=(
            "Counsel, curiosities, and works of magic and philosophy to the "
            "baron's order."
        ),
        summary=(
            "A gathering of scholars and practitioners of many traditions at "
            "the baron's court, kept at his expense. The baron compares it "
            "to the court of Sicily, where scholars of many cultures work "
            "side by side, and speaks of shared learning and peaceful "
            "understanding."
        ),
        secrets=paragraphs(
            "Most members are unGifted, because of what The Gift does to "
            "company; one or two with the Gentle Gift may lead. Since a "
            "tradition takes an opened Gift or a ritual Initiation, they "
            "exchange only knowledge of the realms, of the Order, and of "
            "each other's traditions (Ant p. 11).",
            "Under the talk of learning, their shared concern is to get all "
            "they can from the baron. They counsel him and manage what he "
            "sees of the world, and give him trinkets for security and "
            "funds: at court each enjoys the effect of the Wealthy Virtue, "
            "an extra season of study (Ant p. 11).",
            "Output (Ant p. 11): one average tractatus on Magic, Faerie or "
            "Infernal Lore for each practitioner; one or two inceptions and "
            "formulae a year; one enriched object a year; 10 levels of other "
            "enchantments a year. The collection may be studied book by "
            "book or as realia (Covenants p. 102; Ant p. 15).",
            "Lesser folk touched by magic, not on the council (Ant p. 13): a "
            "mundane astrologer and philosopher, skilled in inceptions, who "
            "wants true magic; a blind beggar cursed with prophetic visions, "
            "who would trade one sight for the other; a young boy who sees "
            "ghosts, and the mother who took him from their frightened "
            "village; a faerie-touched armorer of great skill, who needs a "
            "place to work, money for his workshop, and someone to deal with "
            "the faerie forever trying to take back its tools.",
            "Sample inceptions (Art & Academe ch. 5; the astrologer knows how "
            "to make each, and a season makes copies, finished by casting the "
            "horoscopes): Has N Betrayed the Confidence of NA?, level 5, "
            "Binary (Base 4, +1 past), whether the first person has probably "
            "revealed a secret of the second: Geoffroi uses it on Ysabeau. Is "
            "N the Father of NA?, level 5, Binary (Base 5), which reads the "
            "boy's present state, not the past: Geoffroi uses it on François "
            "(Ant p. 21).",
            "Sample reagent: Glass of Uncommon Purity, level 20, Substantial "
            "(Base 10, +2 Substantial), purifies glass as it is worked; "
            "decanters and glasses of it give a host +2 to Leadership while "
            "entertaining guests (Ant pp. 21-22).",
            "Sample theriacs: Compress of Tormentil, level 15, Mild (Base 10, "
            "+1 Mild), a bandage of tormentil and comfrey that heals a Light "
            "Wound from a slashing or piercing weapon in a week. Tincture of "
            "Vitality, level 15, Moderate (Base 5, +2 Moderate), a draft that "
            "at once lifts Tired to Weary: Geoffroi uses these at the tourney "
            "(Ant p. 22).",
            "Without Art & Academe, use only the effects (Ant p. 21). The "
            "amulets, chartae and wondrous items are device records.",
        ),
    )
    b.link(council, "characters", geoffroi, "its patron")
    b.link(council, "characters", locke, "the Elementalist")
    for name, summary, hidden, traditions in _WIZARDS:
        wizard = b.magus(
            name,
            covenant=None,
            house="",
            age=None,
            type="companion",
            summary=summary,
            secrets=hidden,
            traditions=list(traditions),
        )
        b.link(council, "characters", wizard, "a member of the council")
    anning = b.creature(
        "Dorothy Anning",
        page="p. 12",
        realm="Faerie",
        appearance="A wise woman of the baron's council.",
        notes="The book prints no statistics.",
        secrets=(
            "A faerie in the guise of a wise woman, with pretenses and powers "
            "in place of magical ability, who has joined the council to learn "
            "how men use their power for the good of others."
        ),
    )
    b.link(council, "creatures", anning, "a member of the council")
    return council


# -- the sample items --


def _unheld_item(
    b: Builder,
    name: str,
    *,
    kind: str,
    maker: str,
    description: str,
    effect: InstilledEffect,
) -> EnchantedDevice:
    """A device the book describes but puts in nobody's hands yet."""
    device = EnchantedDevice(
        id=storage.generate_unique_id(name, [d.id for d in b.saga.enchanted_devices]),
        name=name,
        type=kind,
        description=description,
        maker_name=maker,
    )
    effect.id = f"{device.id}-1"
    device.effects.append(effect)
    b.saga.enchanted_devices.append(device)
    return device


def _items(b: Builder) -> None:
    _unheld_item(
        b,
        "A Most Noble Ring",
        kind=INVESTED,
        maker="A master goldsmith with Divinely influenced power",
        description=paragraphs(
            "A ring made for the baron that lends its wearer a forceful "
            "and fair bearing.",
            "A wondrous item (City & Guild ch. 4), and an Arcane Connection "
            "to the man it was made for. Workshop Total 15 or more. Craft "
            "total needed: 1 season 28, 2 seasons 21, 3 seasons 19, 4 seasons "
            "18. The total is Dexterity + Craft + Workshop Bonus + an "
            "assistant's bonus + aura + the item's quality bonus (Ant p. 22).",
        ),
        effect=InstilledEffect(
            id="",
            name="Aura of Enobled Presence",
            technique="Muto",
            form="Imaginem",
            range="Touch",
            duration="Sun",
            target="Individual",
            level=10,
            description=(
                "+3 to attempts to influence, lead or convince others in his "
                "presence, as the spell of ArM5 p. 145. (Base 3, +1 Touch, "
                "+2 Sun)"
            ),
        ),
    )
    _unheld_item(
        b,
        "A Blade of Virtue",
        kind=INVESTED,
        maker="A magical craftsman",
        description=paragraphs(
            "An excellent long sword, perhaps the prize at one of the baron's "
            "tournaments, with +2 to attack and defense.",
            "A wondrous item, enchanted for one owner over some seasons. "
            "Steel first treated as in Art & Academe p. 76 adds +2 to damage. "
            "Craft total needed: 1 season 30, 2 seasons 23, 3 seasons 20, 4 "
            "seasons 19 (Ant p. 22).",
        ),
        effect=InstilledEffect(
            id="",
            name="The Rarefied Blade",
            technique="Muto",
            form="Terram",
            range="Personal",
            duration="Sun",
            target="Individual",
            level=15,
            restricted_use=True,
            restricted_to="Its intended owner",
            trigger="A secret incantation",
            description=(
                "Makes the sword lighter and better balanced in its owner's "
                "hand: +1 to attack and defense. While active it has "
                "Penetration 0 and is resisted by any Magic Resistance of 0 "
                "or more. (Base 3, +2 Sun, +2 metal)"
            ),
        ),
    )
    _unheld_item(
        b,
        "Grant Fortune At the Tourney (Single Weapon)",
        kind=CHARGED,
        maker="A learned magician",
        description=paragraphs(
            "An amulet in the form of an embroidered girdle, worn through a "
            "season of tournaments.",
            "A learned magician's amulet (Hedge Magic Revised Edition ch. 5), "
            "a season's work, for one subject; its charges come from the lab "
            "total and discharge one after another (Ant p. 23).",
        ),
        effect=InstilledEffect(
            id="",
            name="Grant Fortune At the Tourney (Single Weapon)",
            range="Touch",
            duration="Season",
            target="Individual",
            level=20,
            description=(
                "TuFa level 20. With Single Weapon only: on an attack advantage "
                "of 0 or less both combatants re-roll, and a positive second "
                "result is used; a botch is discarded unless the second roll "
                "also botches, when the less harmful stands. (Base 5, +0 "
                "Touch, +3 Season)"
            ),
        ),
    )
    _unheld_item(
        b,
        "An Arrow So True Has Never Been Struck",
        kind=CHARGED,
        maker="A learned magician",
        description=paragraphs(
            "A charta written out on the morning of a hunt.",
            "A single-use text for one person: a full day casting their "
            "horoscope, plus an hour for each magnitude (Ant p. 23).",
        ),
        effect=InstilledEffect(
            id="",
            name="An Arrow So True Has Never Been Struck",
            range="Touch",
            duration="Sun",
            target="Individual",
            level=15,
            description=(
                "SuFa level 15. +3 to all attack rolls with a bow. (Base 10, "
                "+0 Touch, +1 Sun)"
            ),
        ),
    )


# -- the story --


def _story(b: Builder, barony: Neighbour, council: Neighbour) -> None:
    threat = b.threat(
        "Baron Geoffroi's Hunger for Magic",
        antagonist=BARON,
        moves=TRACK,
        summary=(
            "A rich and curious baron near the covenant starts to take an "
            "interest in magic, and in the scholars next door."
        ),
        secrets=paragraphs(
            "Geoffroi begins as a reasonable man and a possible ally, grows "
            "obsessed, and ends a danger to himself, his vassals and his "
            "neighbors. He sees little difference between Divine, Faerie, "
            "Magic and Infernal, fills his woods with beasts from afar and "
            "his court with magicians. The story has two sides, his research "
            "and the neglect of his lands, and the book advises at least one "
            "story from each stage. Many stages can serve as news brought by "
            "infiltration, intrigue or scrying (Ant p. 14). The Infernal "
            "and Parma stages can be braided with the Divine Abbot's story "
            "(Ant p. 113).",
            "Investigating (Ant p. 18): the troubles plainly lead to his "
            "court; what remains is why, who holds his ear, and how to end "
            "it. Infiltrating the council can be done openly, but it will "
            "expect its members to do the baron's wishes, which an oath may "
            "forbid. Spying or scrying shows the alliances and plots kept out "
            "of the chamber, and can split the council. Arcane Connections "
            "taken from people or rooms allow listening in, or worse.",
            "Endings (Ant pp. 19-21). Let sleeping dogs lie: he loses his "
            "lands, signing whatever he is handed, and dies poor, while "
            "nobles and Guillaume fight over them, Ysabeau and her daughters "
            "go back to Arques, and the war or the wizards become the "
            "covenant's problem. Persuade him: threaten his family, expose "
            "François, take the council's place with proof of its treachery, "
            "or send rivals, friends or the Church to turn him. Eliminate "
            "him, if an heir is of age, or leave him infirm under a regent: "
            "the Code forbids it, the court wizards may trace it, and Ysabeau "
            "and the heir must then be guarded from them. Persuade the wizards "
            "to leave, by threats, bribes or a fair sharing of learning. "
            "Eliminate the wizards, perhaps through Tremere, Flambeau or "
            "Hoplites, and expect their traditions' revenge and the baron's "
            "own, by trade and fear. Induct them into Ex Miscellanea, under "
            "the Oath. Or found a rival order with a code of its own, which "
            "House Tremere would oppose, and which could become the great "
            "question of the next Grand Tribunal.",
            "Interference: whether acting against a hedge wizard is meddling "
            "with mundanes has no fixed answer. Each case goes to Tribunal, "
            "for the magi to argue and not for the troupe to rule (Ant p. 19).",
        ),
        stages=[
            S(
                "First Encounter",
                at=1,
                clues=(
                    "One of these, the others free for later (Ant pp. 13-14). "
                    "A magical stag of little might, fleeing his chase, is "
                    "trapped against the Aegis with his hounds behind it. A "
                    "demon that priests could not drive out jumps to a new "
                    "host, and a grog may carry it into the covenant. A "
                    "great egg-smooth stone wrecks a farmer's hayloft and "
                    "no team of oxen can lift it. A strange leper, whom he "
                    "drove off and who cursed him, is in truth a wandering "
                    "Tytalus magus, and the baron's son lies deathly ill."
                ),
                ignored=(
                    "He leaves curious, distrusting his Gifted helpers, and "
                    "feeling there may be others more amenable."
                ),
            ),
            S(
                "The Library",
                at=2,
                clues=(
                    "He tries to buy or commission books or hire a tutor, "
                    "sure that a book of spells is all he needs, and asks to "
                    "be sent on to other wizards if refused. A city merchant "
                    "offers him texts that prove to be on Infernal Lore, and "
                    "the covenant is asked to verify them. He visits a "
                    "regio, and a week later Claude comes for help: the baron "
                    "is at chess with a powerful faerie for his companions' "
                    "lives (Ant pp. 14-15)."
                ),
                ignored=(
                    "He has the start of a collection of grimoires, bestiaries "
                    "and strange objects."
                ),
            ),
            S(
                "The Hunt",
                at=3,
                clues=(
                    "He asks for a magically keen pack of hounds, turning "
                    "belligerent if he has seen a familiar. He invites the magi "
                    "to capture a faerie-touched sounder of boar, offering "
                    "first choice of the cuts; alone his party comes back "
                    "bloodied and a man short. He offers a bounty for beasts "
                    "of virtue brought alive, risking the covenant's allies "
                    "and vis. A man who turns wolf at the full moon claims "
                    "sanctuary from him, wanted as the quarry of a magical "
                    "hunt (Ant p. 15)."
                ),
                ignored="He is not yet dangerous, but has become a nuisance.",
            ),
            S(
                "The Tournament",
                at=4,
                clues=(
                    "Planned a year ahead for spring or summer. He commissions "
                    "an enchanted sword, a golden cup of grandeur, a horse of "
                    "virtue and a magical hawk, as well as magical "
                    "entertainments for the feast, pays well, wants help for "
                    "his own knights, and invites the covenant to enter. Where "
                    "kings frown on tournaments, as in Stonehenge, he asks the "
                    "magi to spy out how to win the king's favor, or goes to "
                    "an astrologer (Ant pp. 15-16; Lords of Men p. 64)."
                ),
                ignored=(
                    "Helping him may bring rivals to other wizards, and more "
                    "charges of interfering with mundanes."
                ),
            ),
            S(
                "The Council of Wizards",
                at=5,
                clues=(
                    "He assembles his council and invites the magi to join "
                    "and share their magic. One of the cunning folk (Hedge "
                    "Magic Revised Edition p. 101) comes to the land and is "
                    "held as a witch. The wizards seek Bonisagus' theory in "
                    "exchange for insights, and ask what the magi will give "
                    "instead of Parma. He promises Alenard to a magician, and "
                    "Ysabeau pleads with the covenant. A Quaesitor comes to "
                    "investigate the covenant's support for him, with old "
                    "scores to settle (Ant pp. 16-17)."
                ),
                ignored="The covenant gains the Rival External Relations Hook "
                "(Covenants p. 22).",
            ),
            S(
                "Stolen Resources",
                at=6,
                clues=(
                    "Vis sources are stripped, and the trail leads to a court "
                    "wizard; Geoffroi offers to protect them all, if only he "
                    "is told of them. The council claims every aura, beast "
                    "of virtue and Gifted child on his lands just as a magus "
                    "hears of a Gifted child. A nearby covenant, its own "
                    "sources raided, holds the characters' covenant to blame "
                    "and demands reparation (Ant p. 17)."
                ),
            ),
            S(
                "The Theft of Parma",
                at=7,
                clues=(
                    "A court wizard plots to abduct a magus or apprentice and "
                    "force a season's teaching of Parma Magica. The council "
                    "may not know. The troupe can play the abductors, planning "
                    "around Aegis and Parma (Ant p. 17). The Gift is needed to "
                    "use Parma, so most of them cannot, and a score of 1 is "
                    "probably the least worth teaching."
                ),
                ignored=(
                    "The Order would stop at nothing to prevent it, and "
                    "retribution and debate over who is to blame would follow."
                ),
                stopped="Dealt with quickly and quietly, before word gets out.",
            ),
            S(
                "Fines and Taxes",
                at=8,
                clues=(
                    "Heavy tallage, tolls and fines to pay for it. Hardship "
                    "sends the covenant to a far fair. Stolen crops lead to "
                    "his new tax collector. Bandits capture a Redcap, and "
                    "their leader's stolen devices make her look like one "
                    "of his wizards (Ant p. 17)."
                ),
                ignored=(
                    "With Covenants' Wealth & Poverty rules, each type of "
                    "inhabitant costs 1 point more (Covenants p. 63)."
                ),
            ),
            S(
                "A Poor Ruler",
                at=9,
                clues=(
                    "Ysabeau, banished for opposing Alenard's fate, passes the "
                    "grogs an Arcane Connection to herself as she goes under "
                    "guard to an outlying estate with her daughters. A rival "
                    "lord's men search travellers. Agitators blame the covenant "
                    "for leading the baron astray, perhaps as a distraction. "
                    "Serfs flee to the covenant, and Claude comes with armed "
                    "men, promising only the ringleaders will suffer (Ant "
                    "p. 18)."
                ),
            ),
            S(
                "The Expulsion of Claude",
                at=10,
                clues=(
                    "Geoffroi dismisses his steward for one gifted in magic, "
                    "perhaps Edwin Locke. Claude retires to a monastery in "
                    "Normandy (Ant p. 18)."
                ),
                turned=(
                    "He has gathered Arcane Connections to the court's "
                    "magicians, some still active, and might give them up if "
                    "he thought it served Geoffroi."
                ),
            ),
            S(
                "The Lady of the Manor",
                at=11,
                clues=(
                    "Ysabeau turns to the covenant. If Geoffroi finds out, he "
                    "may have an astrologer judge her daily, send her to "
                    "Normandy, have her silenced by magic, or threaten to take "
                    "her daughters (Ant p. 19)."
                ),
            ),
            S(
                "The Peasants' Revolt",
                at=12,
                clues=(
                    "Anger spills over into neighboring lands, fed by demons "
                    "of resentment, ambition and jealousy, and one of the "
                    "covenant's companions, possessed, plans and leads the "
                    "mob. A manor house, a mill and a chapel go first, then "
                    "the farms and granaries the peasants need most (Ant "
                    "p. 18)."
                ),
                ignored="The covenant gains the War Zone External Relations "
                "Hook (Covenants p. 22).",
            ),
        ],
    )
    b.link(threat, "places", barony, "the baron's lands")
    b.link(threat, "places", council, "his council of wizards")
    dormant(threat)


def _seeds(b: Builder) -> None:
    for name, summary, hidden in (
        (
            "The Ambitious Medicus",
            "An itinerant doctor settles happily into the baron's court.",
            "Skilled in the elemental arts, he tilts the court's humors "
            "toward the sanguine, so that all think him a friend, even as the "
            "baron's riches begin to vanish. Only the phlegmatic steward "
            "suspects, and looks for someone who will listen (Ant p. 13).",
        ),
        (
            "The Magical Swordsmith",
            "The baron asks that his swordsmith be let work at the covenant.",
            "A peasant craftsman, daunted by the wealthy and the Gifted, who "
            "needs the covenant's beneficial air. Can the magi learn from him, "
            "and will they send him back to Geoffroi or keep him for another "
            "use (Ant p. 15)?",
        ),
        (
            "The Stolen Ring",
            "A Jewish goldsmith and his apprentice ask the magi's help.",
            "A ring he burned magic into for Baron Geoffroi has been stolen. "
            "He fears the baron's wrath and that it will serve as an Arcane "
            "Connection to him. Where is it, what does the thief intend, and "
            "what is the apprentice's part (Ant p. 22)?",
        ),
    ):
        dormant(b.threat(name, antagonist=BARON, summary=summary, secrets=hidden))
