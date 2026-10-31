"""Father Joseph of Napoli (Antagonists pp. 37-49), in paraphrase.

The legate is a full character; Pompius, his dead master, is a sketch. The
Societas of the Mystical Christ is a faction with no named member. Napoli, San
Giovanni Maggiore and the papal curia are records, the last naming the two
popes. His three books and his letters of authority are books he owns. His
relic is a Bestiary record, the only place with a home for its Divine Might
and its powers. His mission is one dormant threat, and each of the book's
story seeds is a dormant threat of its own. The book ties him to no covenant;
his Rome and Rhine background may be moved (Ant p. 40)."""

from __future__ import annotations

from ... import storage
from ...models import Book, Character, Creature, Neighbour
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    secrets,
)

JOSEPH = "Father Joseph of Napoli"
POMPIUS = "Pompius of House Guernicus"
GUERNICUS = "house_guernicus"
HONORIUS = "Pope Honorius III"
TRACK = "A track"
S = Builder.stage

_BLOCK: StatBlock = {
    "characteristics": characteristics(3, 0, 1, 2, -2, -1, 1, -1),
    "aging_points": {"quickness": 1},
    "size": 0,
    "apparent_age": 44,
    "decrepitude": (0, 1),
    "warping": (3, 5),
    "confidence": (1, 3),
    "virtues_flaws": [
        "Priest",
        "Arcane Lore",
        "Inspirational",
        "Relic",
        "Temporal Influence",
        "Well-Traveled",
        "Commanding Aura",
        "Driven (Major)",
        ("Ability Block", {"abilities": "Martial"}),
        "Arthritis",
        "Visions",
        "Vow (Minor)",
        "Weak Characteristics",
    ],
    "traits": {"Driven": 6, "Religious": 3},
    "reputations": {
        "Papal Legate to the Order of Hermes (ecclesiastical)": 4,
        "Quaesitor's notary (Hermetic)": 1,
    },
    "abilities": [
        ("Area Lore: Naples", 3, "history"),
        ("Area Lore: Rhine Tribunal", 2, "covenant locations"),
        ("Area Lore: Rome", 2, "churches"),
        ("Area Lore: Rome Tribunal", 3, "covenant locations"),
        ("Artes Liberales", 1, "logic, reads Latin script"),
        ("Awareness", 3, "spell effects"),
        ("Bargain", 3, "treaties"),
        ("Charm", 2, "covenant grogs"),
        ("Civil and Canon Law", 5, "magic"),
        ("Code of Hermes", 3, "mundane interference"),
        ("Concentration", 2, "meditation"),
        ("Dead Language: Latin", 5, "church use"),
        ("Dominion Lore", 1, "angels"),
        ("Etiquette", 3, "Hermetic"),
        ("Folk Ken", 4, "magi"),
        ("Guile", 2, "written communication"),
        ("Intrigue", 5, "magi"),
        ("Leadership", 5, "religious"),
        ("Living Language: Low German", 3, "travel"),
        ("Living Language: Italian", 5, "Napoli dialect"),
        ("Magic Theory", 2, "spells"),
        ("Music", 1, "church"),
        ("Organization Lore: Church", 5, "papal curia"),
        ("Organization Lore: Order of Hermes", 4, "Christian magi"),
        ("Profession: Scribe", 3, "copying"),
        ("Ride", 2, "long distances"),
        ("Theology", 3, "magic"),
    ],
    "notes": paragraphs(
        "Combat (Ant p. 38). Dodge: Init -1, Attack +1, Defense -1, Damage n/a. "
        "Soak +2 (-1 Stamina, +3 papal legate). Fatigue Levels: OK, 0, -1, -3, "
        "-5, Unconscious. Wound Penalties: -1 (1-5), -3 (6-10), -5 (11-15), "
        "Incapacitated (16-20), Dead (21+). Encumbrance 0.",
        "Magic Resistance 25: 15 as a papal legate and 10 from his relic. Faith "
        "Points 2: 1 from the relic, which regenerates, and 1 from mass. Age 54, "
        "looking 44, with a Longevity Ritual of +5. Powers: Commanding Aura as "
        "papal legate, and Faithful Wisdom from the relic. Arthritis and Visions "
        "are due to Warping, and his Ability Block is Martial.",
        "Equipment: priest's stole, a well-worn monk's habit, the finger-bone "
        "relic, letters of authority in a leather scroll case, writing gear "
        "(ink, parchment, the legate's seal, wax and so on), and a riding horse "
        "with saddle and tack.",
        "Tall and ascetic, with a slight stoop from years at the writing desk, "
        "though he straightens and his eyes shine when he preaches. He is plainly "
        "old but not frail. He wears a priest's regalia, carries a satchel of "
        "writing gear, and rides a costly glossy black stallion, lighter and "
        "quicker than a warhorse, that can go for days with little rest. One or "
        "two clergymen ride with him, and later perhaps a magus ally dressed as "
        "one.",
        "Commanding Aura (Ant p. 38; DE p. 82, same figures): as Aura of Rightful "
        "Authority at Voice Range, at no cost and with no Penetration, with Magic "
        "Resistance 15 and Soak +3, the Magic Resistance added to any relic's. It "
        "fails if he delays or strays from his mission, until he does penance, "
        "and ends when the mission is done. It comes from his office, not his "
        "letters (Ant p. 43).",
        "He has no True Faith and cannot work miracles, though he can pray to "
        "the saints (Ant p. 39). His Magic Resistance does not stop him crossing "
        "an Aegis of the Hearth, but the relic's Divine Might needs a token "
        "there, unless the Aegis is too weak to stop it; he can leave it behind "
        "(Ant p. 41). Replace his Area Lores and Living Languages if his past is "
        "moved to another Tribunal (Ant p. 40). A storyguide rolls Order of "
        "Hermes Lore, Code of Hermes, Magic Theory or Area Lore for anything "
        "rare he might know (Ant p. 40).",
    ),
}


def build(b: Builder) -> None:
    joseph = _father(b)
    pompius = _pompius(b, joseph)
    curia, napoli = _places(b, joseph)
    relic = _relic(b, joseph)
    books = _books(b, joseph)
    societas = _societas(b, joseph)
    _mission(b, joseph, pompius, curia, napoli, relic, books, societas)
    _seeds(b, joseph)


def _father(b: Builder) -> Character:
    joseph = b.magus(
        JOSEPH,
        covenant=None,
        house="",
        age=54,
        type="companion",
        summary=paragraphs(
            "A papal legate sent as envoy to the Order of Hermes, who "
            "introduces himself as such and hides nothing of his past. A "
            "fisherman's son of Napoli, he left the Church as a deacon at 19 "
            "to serve as notary to the Quaesitor Pompius, and traveled with him "
            "through the Rome and Rhine Tribunals for almost 17 years. After "
            "Pompius passed into Final Twilight in 1202 he went home, became a "
            "canon at San Giovanni Maggiore and wrote about the Order. Ordained "
            "in 1210 and soon called to Rome to advise Innocent III on the "
            "Order, he stayed on under Honorius III, who made him legate in "
            "1219.",
            "He is a good man who tries to live by Christ's teaching, a "
            "patient talker rather than a fighter, and no saint. He proposes "
            "that the Order become a true religious order under a Grand Master "
            "and the pope, and he wants magi to think and talk about it.",
        ),
        secrets=paragraphs(
            "His mission has three parts: seat a Grand Master, have him "
            "recognized by the pope as a Christian title, subject to Rome, and "
            "in time have anyone who refuses the new Order Marched. He "
            "expects that to mean devout pagans, Muslims and Jews who will not "
            "convert, and those who want to stay free of Rome. Wizard War "
            "waged by his allies would also serve, but he prefers a March's "
            "legal clarity (Ant p. 37).",
            "He has no quarrel with magic. Canon law would stretch to cover "
            "magi as a new order of religious, with the Code and the Peripheral "
            "Codes as new volumes of it. Houses, Tribunals, independence and "
            "scholarship may all stay, and arcane theories would be treated as "
            "Church theologians' are: some embraced, some tolerated, a few "
            "outlawed (Ant pp. 37-38).",
            "He still knows many covenants of Rome and Rhine, some hidden in "
            "regiones, their sites and numbers nearly twenty years stale, and "
            "little of magi Gauntleted since. He knows the Oath, the common "
            "Peripheral Code rulings, Marches, Wizard War, Certamen, the "
            "Houses, Quaesitors, Redcaps and the Order's history; that Mystery "
            "Cults exist; and in outline the Arts, Parma Magica, Arcane "
            "Connections and vis. He cannot teach or cast, but copied such "
            "texts for Pompius. He may recognize Aegis of the Hearth, Frosty "
            "Breath of the Spoken Lie, Whispers Through the Black Gate, Demon's "
            "Eternal Oblivion and various Wards by their effects (Ant p. 40).",
            "He once bitterly envied the Gift, and blames that on his own "
            "failing, perhaps helped by the Gift's effect on others. He says "
            "little of his family for fear of threats, though threats would "
            "not sway him, and he accepts he may die in office (Ant pp. 39, 42, "
            "49). He holds Holy Magic and Hermetic magic to be two cathedrals, "
            "one built by angels and one by men, both to God's glory (Ant p. "
            "39). He is not mind-proof: Hermetic magic can ruin his mind or "
            "turn him from his mission (Ant p. 48).",
            "The pope may not expect him to succeed; his failure could be the "
            "pretext for harsher measures against the Order. Whether God "
            "favors his mission is for the troupe to decide (Ant pp. 38-39).",
        ),
    )
    b.stats(joseph, _BLOCK, source="Ant")
    joseph.background.faith_points = 2
    joseph.aging.longevity_modifier = 5
    joseph.aging.longevity_by = POMPIUS
    return joseph


def _pompius(b: Builder, joseph: Character) -> Character:
    pompius = b.magus(
        POMPIUS,
        covenant=None,
        house=GUERNICUS,
        age=None,
        summary=paragraphs(
            "A Quaesitor and archmage, in his last years a bright-eyed, lively "
            "old man with bent and wiry limbs, much sought to judge, "
            "investigate and advise. In the summer of 1202 he turned to stone "
            "in the midst of an investigation and passed into Final Twilight. "
            "A nearby covenant recovered the statue, and his case notes went "
            "to his successor.",
        ),
        secrets=paragraphs(
            "He made Joseph a Longevity Ritual and spent long talks with him "
            "on the place of Order and Church in the Divine plan (Ant p. 39). "
            "The Quaesitorial records of his cases hold Joseph's signature, a "
            "Sympathetic Connection to the legate (ArM5 p. 84; Ant p. 42).",
            "Perhaps Joseph was somebody's pawn from his notary days on (Ant "
            "pp. 41, 49).",
        ),
    )
    b.link(joseph, "characters", pompius, "His old master")
    return pompius


def _places(b: Builder, joseph: Character) -> tuple[Neighbour, Neighbour]:
    curia = b.church(
        "The Papal Curia",
        church="Large urban church",
        ruler=HONORIUS,
        summary=paragraphs(
            "The pope's court at Rome. Under Innocent III and, since his death "
            "in 1216, Honorius III, it has worked to reform the Church and "
            "draw power to itself. To speak to a legate is to speak to the "
            "pope, and an attack on one is as good as an attack on him.",
        ),
        secrets=paragraphs(
            "Bringing the Order under Rome would be a great prize, and a "
            "widespread pseudo-religious order outside papal authority is bad "
            "politics: the monastic orders might wonder if they too could do "
            "without Rome. Other Church factions may oppose the mission (Ant "
            "pp. 38-39). The curia knows of the Societas of the Mystical "
            "Christ, and Father Joseph's books circulate there (Ant pp. 42, "
            "45).",
            "The papacy has no sound way to prove its letters: seals can be "
            "forged, despite harsh penalties (Ant p. 43).",
        ),
    )
    napoli = b.town(
        "Napoli",
        summary=(
            "Father Joseph's birthplace, where his family still live. Few "
            "there, outside perhaps the bishop's court, have more than a vague "
            "idea of his mission."
        ),
    )
    church = b.church(
        "San Giovanni Maggiore",
        church="Large urban church",
        place=napoli,
        summary=(
            "The church in Napoli where Joseph was a canon and wrote his books "
            "on the Order of Hermes between 1203 and 1210. He is well known "
            "there."
        ),
    )
    b.link(curia, "characters", joseph, "Its legate to the Order")
    b.link(church, "characters", joseph, "A canon here, 1203-1210")
    kin = b.faction(
        "The Family of Father Joseph",
        faction="Family",
        place=napoli,
        summary=(
            "Poor folk of Napoli, simple fishermen for the most part, with "
            "several relatives in the lower clergy."
        ),
        secrets=(
            "He keeps them out of his talk to protect them from unscrupulous "
            "magi; he would put his mission first if they were threatened "
            "(Ant p. 42)."
        ),
    )
    b.link(kin, "characters", joseph, "Their son")
    return curia, napoli


def _relic(b: Builder, joseph: Character) -> Creature:
    relic = b.creature(
        "The Finger Bone of Saint Jerome",
        page="p. 42",
        realm="Divine",
        might=10,
        tires=False,
        can_be_wounded=False,
        appearance=(
            "A saint's finger bone on a silver chain, worn under the robes "
            "round Father Joseph's neck. Saint Jerome, patron of scholars, "
            "who translated the Vulgate, is known to anyone with a score in "
            "Church Lore."
        ),
        notes=paragraphs(
            "A relic, not a being, held here for its Might and powers: 1 Faith "
            "Point and Divine Might 10, which gives its bearer Magic Resistance "
            "(ArM5 p. 189; RoP:D pp. 43-46). Its powers run on its Might, which "
            "returns each sunrise. The book prints no Might Form. Intellego Vim "
            "with enough Penetration gives a rough idea of its powers (Ant p. "
            "42).",
            "To scale it, raise its Faith to 2 or 3 for a total Magic Resistance "
            "of 35 or 45, perhaps with more powers, or swap Faithful Wisdom "
            "for another; RoP:D p. 88 has more (Ant pp. 43, 49). The book's two "
            "examples, not on the bone as printed:",
            "Life of the Ascetic: 5 points, Init +3, Corpus, R Touch, D Sun, T "
            "Individual. The one blessed feels hunger and thirst but takes no "
            "harm from going without food or drink.",
            "Rebuke of the Scholar: 1 point, Init +10, Corpus, R Voice, D Sun, T "
            "Individual. A curse of stammering that bars coherent speech. A "
            "caster takes the penalty for casting without words, but can still "
            "make noise, so Voice spells keep their range.",
        ),
        powers=[
            Builder.power(
                "Faithful Wisdom",
                1,
                3,
                "Mentem",
                rtd=("Touch", "Season", "Individual"),
                does="Blesses someone to read one text named at the blessing "
                "(tractatus, summa, Lab Text or the like), whatever their "
                "literacy, language or script, at a normal reader's pace, with "
                "the text in hand. Anyone literate may also copy it, without "
                "error, by the normal rules; the copy is exact, not a "
                "translation, so they may not read it afterward.",
            )
        ],
    )
    b.link(relic, "characters", joseph, "Worn by him")
    return relic


def _books(b: Builder, joseph: Character) -> list[Book]:
    made = []
    for name, kind, ability, quality, description in (
        (
            "The Order of Hermes",
            "Tractatus",
            "Organization Lore: Order of Hermes",
            8,
            "Written at San Giovanni Maggiore for clerical readers, and "
            "circulating in the Church, especially the curia.",
        ),
        (
            "The Rule of The Order of Hermes",
            "Tractatus",
            "Code of Hermes",
            8,
            "An account of the Order's law, written at San Giovanni Maggiore "
            "for clerical readers. The book calls the subject Code of Hermes "
            "Lore.",
        ),
        (
            "History of the Magi of the Ecclesiastical Province of Rome",
            "Tractatus",
            "Organization Lore: Order of Hermes",
            8,
            "A regional history of the Order, written at San Giovanni Maggiore "
            "for clerical readers.",
        ),
        (
            "The Legate's Letters of Authority",
            "Other",
            "",
            None,
            secrets(
                "Letters under papal seal, kept in a leather scroll case. They "
                "name Father Joseph as legate and envoy to the Order, with "
                "free and safe passage, the right to speak with magi for the "
                "pope, and power to requisition help from churches, bishops "
                "and monasteries.",
                "He shows them to the bishop of each new diocese, who sends a "
                "well-known deacon or priest with him, for his credit and to "
                "watch him, as bishops fear an audit; the deacon goes on with "
                "him to the next diocese. A bishop who truly thinks the Order "
                "heretical or Infernal may hinder him (Ant p. 43). Intelligence "
                "+ Church Lore against Ease Factor 9 knows or guesses he has "
                "them. InAn (ArM5 p. 117) shows they came from the curia, "
                "probably by a scribe. They only record his powers: losing "
                "them costs him no authority and gives a thief none, though a "
                "careful impostor could use them. Fresh ones mean returning to "
                "Rome, unless he left a set with a friendly bishop (Ant pp. "
                "43-44).",
            ),
        ),
    ):
        book = Book(
            id=storage.generate_unique_id(name, [x.id for x in b.saga.books]),
            name=name,
            type=kind,
            author=JOSEPH if kind == "Tractatus" else "",
            owner_kind="character",
            owner_id=joseph.id,
            subject_kind="Ability" if ability else "",
            ability=ability,
            quality=quality,
            description=description,
        )
        b.saga.books.append(book)
        made.append(book)
    return made


def _societas(b: Builder, joseph: Character) -> Neighbour:
    societas = b.faction(
        "The Societas of the Mystical Christ",
        wants="A religious Order of Hermes under a Grand Master and the pope.",
        offers=paragraphs(
            "Standing among those high in the Church who know of it: a member "
            "who names it in a petition to the curia (The Church pp. 46-48) has "
            "+3 to his Petition Total. Low-ranking clergy will not have heard "
            "of it.",
        ),
        rules=paragraphs(
            "Open to any Christian magus, however devout; pagans, Muslims and "
            "Jews must convert and be baptized first. It is a political "
            "faction, not a Mystery Cult, and grants no magical benefit or cost "
            "(Ant pp. 44-45). It has a chapter in each Tribunal. Its sign is the "
            "chi-rho, followed by the astrological sign for mercury.",
        ),
        summary=(
            "A Hermetic societas of Christian magi, with chapters across the "
            "Tribunals, that discusses a closer union of the Order and the "
            "Church. It is no secret, but few have heard of it."
        ),
        secrets=paragraphs(
            "It was founded at Father Joseph's suggestion, though he is no "
            "magus, no member, and not its master. He meets its leaders at "
            "least once a year, knows who belongs, and may seek its help if "
            "threatened. It spreads his ideas and is the seed of his new "
            "Order: he expects the first Grand Master to come from its leaders, "
            "and lets it claim his ideas as its own (Ant pp. 44-45). It looks "
            "into the writings and deeds of pious magi as possible recruits "
            "(Ant p. 45).",
            "The book names no member, and the troupe sets its size and power "
            "to suit the saga (Ant p. 49). In a saga that wants it, an inner "
            "circle may hold Mystery scripts for Divine Virtues (Ant p. 45), or "
            "it may be a cabal of power-mad Tytalus magi, with Father Joseph "
            "their pawn since his days as a notary (Ant p. 49).",
            "Other possible allies (Ant p. 45): in the Rhine, it might work as "
            "a Gild (Guardians of the Forests p. 27) with the olive as its "
            "tree, or the Apple Gild may join him; in Thebes, a League might "
            "serve. The Priory of Saint Nerius (RoP:D p. 94) and the covenant "
            "of Cunfin (The Lion and the Lily p. 106) may also side with him.",
        ),
    )
    b.link(societas, "characters", joseph, "Shares its aims")
    return societas


def _mission(
    b: Builder,
    joseph: Character,
    pompius: Character,
    curia: Neighbour,
    napoli: Neighbour,
    relic: Creature,
    books: list[Book],
    societas: Neighbour,
) -> None:
    threat = dormant(
        b.threat(
            "The Legate's Mission",
            antagonist=JOSEPH,
            moves=TRACK,
            summary=(
                "A papal legate is going from covenant to covenant, asking "
                "magi to consider joining the Order to the Church."
            ),
            secrets=paragraphs(
                "Father Joseph attacks no one; he sets the Order against "
                "itself, and politics may end in violence or a new Schism War "
                "(Ant p. 7). Decide how far he has come before the characters "
                "meet him: he may have few Hermetic allies, or many converts "
                "already (Ant p. 41). The stages are the book's strategies in "
                "its order.",
                "First meetings (Ant pp. 41-42). He seeks an audience at a "
                "covenant he knows of, or meets the magi as another covenant's "
                "guest. He may prefer a nearby parish church, sending a "
                "messenger, since spilling blood in a sanctuary is a canon "
                "crime that might give even hostile magi pause. He may be met "
                "on the road, as a rumor from friends or foes, or at Tribunal "
                "with a large faction behind him.",
                "Finding him out (Ant pp. 42, 46). Roll on the Reputation Ease "
                "Factor Table (ArM5 p. 19) to know him as Pompius's notary, "
                "or as a legate; any Church Lore tells what a legate is. Few "
                "magi remember him, while he remembers them well. Only magi "
                "with strong Church contacts will have noticed his books.",
                "If the Order is secretive, say how he got away (Ant pp. 40-41): "
                "he was thought dead in Pompius's spectacular Twilight; the "
                "local magi were lax; he was never let go, and is the pawn of "
                "a faction; or a miracle saved him or his memories.",
                "Ridicule (Ant p. 48). Many magi laugh, and he answers that "
                "Rome was a pagan capital once. Ignoring him avoids blame but "
                "works only for a while, since not every magus will.",
                "Befuddlement (Ant p. 48). Mentem magic can destroy his mind "
                "or his purpose, but if the papacy means it, a new legate "
                "comes, and a miracle may restore him. Tampering with the pope "
                "means the curia too, again and again, at the risk of a "
                "miracle, a charge of mundane interference and the Church's "
                "wrath.",
                "Enlistment (Ant p. 48). Magi who join may be asked to guard "
                "him or travel seeking converts, and may maneuver for terms "
                "or the Grand Mastership, at the risk of charges of "
                "endangering the Order.",
                "In the East (Ant pp. 48-49). Orthodox magi may refuse him, "
                "though Latin crusaders in the east are likely to back a "
                "papal Order. Greek fathers may raise a rival Order; one Grand "
                "Master may balance between Rome and Constantinople, or Latin "
                "and Greek Masters may stand side by side.",
                "Dominion (Ant p. 49). If Rome can have a Grand Master, might "
                "a magus become pope? Ambitious magi may see the way.",
                "Enemies of his enemies (Ant p. 49). Bishop Orris and other "
                "churchmen, perhaps some of the curia, may work with magi "
                "against him, and noble courts fear a pope with wizards at "
                "his command. Old foes may ally.",
                "Martyrdom (Ant p. 49). He can be killed, though a miracle may "
                "save him. At best a new legate follows, guarded by the "
                "military orders, with the Societas behind him. At worst the "
                "papacy wanted this, and preaches crusade: the military orders "
                "answer at once, and minor nobles would come for the lands of "
                "tame nobles called heretics. A major lord like Frederick II "
                "might use it to meet his own crusade vow close to home. The "
                "killers face Tribunal for interference, and mundane justice "
                "besides. If martyred he becomes a saint, perhaps patron of "
                "wizards, and works on (RoP:D pp. 85-89).",
                "Scaling him (Ant p. 49). Add Faith to the relic, choose his "
                "allies' power, and set how warmly the Church backs him. For a "
                "very high-level saga, a Grand Master has already been "
                "proclaimed, and the Order must submit or split.",
            ),
            stages=[
                S(
                    "Discussion and Travel",
                    at=1,
                    clues="He goes from covenant to covenant talking, settling "
                    "for seasons where regular meetings help, and courts the "
                    "Tribunal's influential magi so that they spread his ideas "
                    "(Ant p. 44).",
                    ignored="He gathers the sites of more covenants, and would "
                    "love to ride with a Redcap. He uses Redcaps for his "
                    "letters if allowed, and looks to clerical gossip when he "
                    "runs out of known covenants.",
                ),
                S(
                    "The Societas Grows",
                    at=2,
                    clues="Chapters of the Societas of the Mystical Christ "
                    "appear in the Tribunals, and investigators ask after "
                    "pious magi's characters (Ant pp. 44-45).",
                ),
                S(
                    "Hermetic Benefices",
                    at=3,
                    clues="Covenants are offered tithes as a monastery holds "
                    "them, keeping most, paying a parish priest, and sending a "
                    "little to the bishop (Ant pp. 45-46; The Church pp. "
                    "41-43).",
                    ignored="Magi come to care about their parishes, and their "
                    "covenants take a place like a monastery's among their "
                    "neighbors.",
                    turned="Magi can create wealth anyway, but the standing "
                    "is useful: Church backing lets a covenant turn down "
                    "nobles who ask for magic.",
                ),
                S(
                    "Synods and Tribunals",
                    at=4,
                    clues="Bishops and archdeacons invite local magi to synods "
                    "(The Church p. 45), and he urges magi to ask bishops and "
                    "abbots to Tribunals and councils as non-voting speakers "
                    "or observers (Ant p. 46).",
                    ignored="He can call special synods, but wants ties that "
                    "outlast him.",
                ),
                S(
                    "The Bishop's Court",
                    at=5,
                    clues="Once relations are good, bishops' courts ask magi "
                    "to help verify miracles and find facts in canon crimes "
                    "(Ant pp. 46-47).",
                    turned="He wants a court-wizard charge brought, once sure "
                    "his allies will carry it, and a Peripheral Code ruling "
                    "that this is no crime. A second-best outcome is a "
                    "precedent making it a lesser crime with a small vis fine.",
                ),
                S(
                    "Conversion and Baptism",
                    at=6,
                    clues="He debates pagans and infidels and urges baptism. "
                    "He uses no threats, knowing they would backfire, and "
                    "will not be distracted from the whole Order by a few "
                    "souls (Ant p. 47).",
                ),
                S(
                    "The Grand Master",
                    at=7,
                    clues="The Order must rally behind one Grand Master (Ant "
                    "pp. 47-48).",
                    ignored="He prefers a vote of the Grand Tribunal, then a "
                    "regional Tribunal's choice that forces the others to "
                    "choose, then a Societas leader declaring himself, and "
                    "last a papal appointment. Rome does not care how the "
                    "choice is made, only that most magi accept it; he "
                    "suggests the archmages elect one at each Grand Tribunal, "
                    "as cardinals elect a pope.",
                    turned="A Grand Master seen as illegitimate invites "
                    "certamen and Wizard's War.",
                ),
                S(
                    "A Religious Order",
                    at=8,
                    clues="The pope recognizes the title and the Order, likely "
                    "by bull, and the Grand Master accepts his authority. An "
                    "agreed Peripheral Code goes out as the new Order's canon "
                    "rules, and it goes on governing itself much as before "
                    "(Ant pp. 37, 48).",
                    ignored="In time those who refuse are Marched. Later "
                    "generations may push it toward monastic ways: separate "
                    "magi and magae, set prayers, an end to violence as a "
                    "legal tool.",
                ),
            ],
        )
    )
    b.link(threat, "characters", joseph, "Drives it")
    b.link(threat, "characters", pompius, "His past")
    b.link(threat, "places", curia, "Sends him")
    b.link(threat, "places", societas, "His instrument")
    b.link(threat, "places", napoli, "His home")
    b.link(threat, "creatures", relic, "He wears it")
    for book in books:
        b.link(joseph, "books", book, "His own")


#: The book's story seeds (Ant pp. 44-48): a public line, then the seed.
_SEEDS: tuple[tuple[str, str, str], ...] = (
    (
        "Miracle of the Magi",
        "The local clergy are talking of wonders.",
        "Local clergy see the magi cast spells, and the dean writes to the "
        "curia asking guidance. The letter reaches Father Joseph, who "
        "recognizes Hermetic magic and comes to the deanery to find them (Ant "
        "p. 44).",
    ),
    (
        "Host of the Church",
        "The covenant is asked to house a preaching guest.",
        "Sympathetic magi let Father Joseph stay for seasons, and Christian "
        "magi from all over the Tribunal come to hear him, with retinues to "
        "house. Then argumentative pagan magi arrive; Father Joseph stays calm, "
        "but malicious certamen follows, and unless someone calms things, "
        "Wizard's War or murder (Ant p. 44).",
    ),
    (
        "Pilgrimage",
        "A legate wants a magus to travel with him.",
        "Father Joseph picks a magus who opposes him, though not a homicidal "
        "one, to travel the Tribunal with him, hoping to win him by argument "
        "and example. The magus may be accused of revealing hidden covenants, "
        "if that is a crime, and may have to defend him from pagans (Ant p. "
        "44).",
    ),
    (
        "The Address",
        "A churchman wants to speak at Tribunal.",
        "Father Joseph wants to propose a treaty and a religious Rule at "
        "Tribunal, where custom usually lets only magi speak. Allies argue his "
        "right or speak for him; foes block or answer him. He waits for a "
        "meeting where he has support; a significant minority publicly backing "
        "him is his second-best result, and without either he tries the next "
        "Tribunal (Ant p. 44).",
    ),
    (
        "Christ Underground",
        "Christian magi in a pagan Tribunal are growing wary.",
        "Where pagans or other anti-papal magi rule the Tribunal, the Societas "
        "must hide from concerted Wizard's War, moving Father Joseph from one "
        "safe house to the next as he preaches, glad of the likeness to the "
        "early Church; a martyr or two is no disaster. The magi may hide him, "
        "support their brothers across a border, or be sent to hunt him (Ant "
        "p. 45).",
    ),
    (
        "The Good News",
        "Someone is asking about the good character of local magi.",
        "The Societas recruits pious magi on its own account. Members may be "
        "asked to vouch for neighbors; others may stumble on its agents at "
        "this work (Ant p. 45).",
    ),
    (
        "First Rights",
        "The bishop has a gift for the covenant.",
        "On the pope's order the bishop gives the covenant several benefices, "
        "a Typical Income Source, taken from a chapter of canons he thinks too "
        "strong. The outraged canons, of the diocese's second church, make "
        "bitter enemies; refusing makes one of the bishop (Ant p. 46).",
    ),
    (
        "Care of Souls",
        "The covenant needs a priest for its new parish.",
        "With a benefice the magi must hire a priest, who then comes to them "
        "for help: sick farm animals, a lost child, a lie between merchants "
        "(Ant p. 46).",
    ),
    (
        "The Tithe",
        "It is time to assess the parish's crops.",
        "The magi or their agents must go round the parish yearly to assess "
        "each field's yield, a clerk's usual job and a chance to seek vis. A "
        "tithe that counted natural vis in the produce would be an easy gain "
        "(Ant p. 46).",
    ),
    (
        "Slanderous Accusations",
        "The bishop invites the magi to a synod.",
        "Slander has been a canon crime since 1215. A bishop who thinks magic "
        "no evil learns his priests preach that magi serve the devil, and "
        "calls a synod, inviting the magi to show otherwise (Ant p. 46).",
    ),
    (
        "Heretics",
        "The rural dean invites the magi to a synod.",
        "The dean near the covenant and some of his priests have fallen into "
        "heresy, perhaps Catharism, as the magi see at his synod. Report it "
        "and they may have to help reform or suppress him; ignore it and they "
        "may be accused themselves when the bishop finds out (Ant p. 46).",
    ),
    (
        "Opulent Council Chambers",
        "The bishop's deacon has come to the covenant's council.",
        "A severely ascetic deacon, at the covenant's yearly council, is "
        "shocked by its wealth. The bishop writes asking its sources of "
        "income, from curiosity, a hope of gifts, or his deacon's concern "
        "(Ant p. 46).",
    ),
    (
        "Authentic Miracles",
        "A holy man in a village is said to heal lepers.",
        "The bishop asks the magi if a village holy man who heals lepers who "
        "pray and fast with him is a true conduit of miracles, a charlatan, or "
        "a wizard of some kind (Ant p. 47).",
    ),
    (
        "Possession",
        "A family lies murdered on the cathedral steps.",
        "In a hot, still summer a Jewish family is murdered on the cathedral "
        "steps one Sunday evening, and no one knows by whom. Fearing demons "
        "in the townsfolk and a pogrom to come, the bishop asks the magi to "
        "investigate and deliver the town (Ant p. 47).",
    ),
    (
        "The River Jordan",
        "A legate is baptizing magi on the Danube.",
        "Father Joseph sets up a mission at a covenant on the Danube, offering "
        "baptism in the river as John did. Pagan magi come to be baptized, "
        "pursued by the jealous animal spirits of their cult. The magi may be "
        "hosts facing the spirits, or the converts defeating their old gods "
        "(Ant p. 47).",
    ),
    (
        "Order and Anti-Order",
        "Rival Grand Masters divide the Order.",
        "Rome and Normandy proclaim rival Grand Masters. Father Joseph asks "
        "respected magi to broker a peace, since the papacy could settle it "
        "but cannot tell who has the most support. A player's character may "
        "be one of the rivals (Ant p. 48).",
    ),
)


def _seeds(b: Builder, joseph: Character) -> None:
    for name, summary, seed in _SEEDS:
        threat = dormant(
            b.threat(name, antagonist=JOSEPH, summary=summary, secrets=seed)
        )
        b.link(threat, "characters", joseph, "Behind it, or near it")
