"""The Divine Abbot (Ant pp. 108-119), in paraphrase.

Rasa the Dragon Abbot as a creature; the jinn Howling Knife of the Dunes,
with no block printed; the abbey as a church, whose kind gives the aura
5 at the top of the book's 4 or 5; the friar or monk, the prior and the
penitent knight with their printed stats (the friar or monk as one
record with a variant for each choice the block offers); Acumenis as a
sketch; the five pilgrimage sites the book names, as sketches under the
names other packs use; and the dragon's slow campaign as a dormant
threat, its four stories in the book's order. Stellatus is the
Bestiary's own record and is not remade."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from typing import Any

from ...models import BodyVis, Character
from ..builder import (
    Builder,
    StatBlock,
    characteristics,
    dormant,
    paragraphs,
    vf_ability,
    vf_minor,
)

S = Builder.stage
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
WOUNDS = (
    "Wound Penalties: -1 (1-5), -3 (6-10), -5 (11-15), Incapacitated "
    "(16-20), Dead (21+)."
)
DIVINE = "Divine"
TRACK = "A track"
EX_MISC = "house_ex_miscellanea"


def build(b: Builder) -> None:
    rasa = _rasa(b)
    jinn = _jinn(b)
    abbey = _abbey(b)
    friar = _friar(b)
    prior = _prior(b)
    knight = _knight(b)
    acumenis = _acumenis(b)
    _pilgrimages(b)
    threat = _threat(b)
    b.link(rasa, "places", abbey, "Rules it as abbot, unseen")
    b.link(rasa, "creatures", jinn, "An old enemy")
    b.link(abbey, "characters", prior, "Acts in the abbot's stead")
    b.link(abbey, "characters", friar, "Its brothers")
    b.link(abbey, "characters", knight, "On a task for the abbot")
    b.link(rasa, "characters", acumenis, "Saw it and wrote of it")
    b.link(threat, "creatures", rasa, "Behind the abbey's works")
    b.link(threat, "places", abbey, "Where it all comes from")


def _rasa(b: Builder):
    return b.creature(
        "Rasa the Dragon Abbot",
        page="pp. 110-111",
        realm=DIVINE,
        might=50,
        form="Vim",
        size=8,
        season="Winter",
        age="n/a",
        confidence=(2, 10),
        encumbrance="0 (0)",
        equipment="None",
        block={
            "characteristics": characteristics(4, 2, 8, 4, 14, 8, 3, -2),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                "Senior Clergy",
                ("Greater Immunity", {"hazard": "heat and fire"}),
                "Font of Knowledge",
                "Magic Sensitivity",
                "Piercing Gaze",
                "Premonitions",
                "Second Sight",
                "Self-Confident",
                ("Student of {realm}", {"realm": DIVINE}),
                ("Hunger for {form} Magic", {"form": "Any"}),
                "Monastic Vows",
                "Driven (Minor)",
                "Infamous",
                "Gift of Speech",
                *["Greater Power"] * 3,
                "Improved Abilities",
                *[("Improved Attack", {"weapon": "claws"})] * 2,
                ("Improved Damage", {"weapon": "claws"}),
                ("Improved Defense", {"weapon": "claws"}),
                "Improved Fatigue",
                *["Improved Might"] * 8,
                *["Improved Powers"] * 3,
                *["Improved Soak"] * 6,
                vf_minor("Piercing Gaze"),
                vf_minor("Premonitions"),
                vf_minor("Magic Sensitivity"),
                *["Ritual Power"] * 6,
                "Monstrous Appearance",
                "Susceptible to Deprivation",
            ],
            "abilities": [
                ("Area Lore: (One Area)", 5, "trade routes"),
                ("Area Lore: (A Second Area)", 5, "trade routes"),
                ("Area Lore: (A Third Area)", 4, "trade routes"),
                ("Area Lore: Silk Road", 5, "trade routes"),
                ("Living Language: Arabic", 4, "trade terms"),
                ("Artes Liberales", 4, "rhetoric"),
                ("Awareness", 5, "humans"),
                ("Brawl", 6, "claws"),
                ("Church Lore", 2, "famous shrines"),
                ("Civil and Canon Law", 3, "mendicant orders"),
                ("Concentration", 3, "prayer"),
                ("Divine Lore", 4, "relics"),
                ("Dominion Lore", 4, "miracles"),
                ("Etiquette", 2, "scholars"),
                ("Folk Ken", 3, "scholars"),
                ("Font of Knowledge", 3, "lost battlefields"),
                ("Guile", 3, "scholars"),
                ("Infernal Lore", 2, "demons"),
                ("Intrigue", 3, "long-term schemes"),
                ("Dead Language: Latin", 4, "old dialects"),
                ("Leadership", 4, "scholars"),
                ("Living Language: (One)", 4, ""),
                ("Living Language: (Another)", 3, ""),
                ("Living Language: (A Third)", 2, ""),
                ("Language: (Another)", 2, ""),
                ("Language: (A Further One)", 2, ""),
                ("Magic Lore", 4, "pagan rituals"),
                ("Magic Sensitivity", 1, "spell effects"),
                ("Philosophiae", 3, "moral philosophy"),
                ("Premonitions", 2, "threats to its goals"),
                ("Second Sight", 2, "invisible material things"),
                ("Stealth", 4, "remaining unseen"),
                ("Theology", 4, "saints"),
            ],
            "traits": {"Driven": 3, "Pious": 3, "Curious": 2, "Hungry": 2},
            "reputations": {
                "The Hungry Dragon Who Eats Travelers (several different regions)": 4,
                "The Reclusive Abbot of the Monastery (local)": 4,
            },
        },
        attacks=[
            b.attack("Large Claws", -2, 18, 14, 13),
            b.attack("Large Fangs", -1, 12, 10, 11),
            b.attack("Constrict", -2, 12, 9, None),
        ],
        soak=22,
        fatigue_levels="OK, 0, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Cleansing Flame",
                2,
                3,
                "Ignem",
                rtd=("Voice", "Momentary", "Individual"),
                level=50,
                does="A gout of flame 12 paces wide, 12 tall and 55 long; "
                "everything in it takes stress die +25 fire damage. CrIg 50 "
                "(Base 20, +2 Voice, +4 size): Greater Power (50 levels) and "
                "partial Improved Powers (-3 Might cost).",
            ),
            b.power(
                "Taste of Memory",
                4,
                -10,
                "Mentem",
                rtd=("Touch", "Momentary", "Individual"),
                level=35,
                does="From a creature it eats, Rasa takes a particular memory "
                "of an act or event, 5 experience points of a skill, or a "
                "Virtue. Skills improve as normal, but the creature must be "
                "eaten alive; a Virtue may be taken once a year. Might spent "
                "on skills or Virtues also lowers its Might Score, regained "
                "with 10 pawns of vis per point or a season's rest, without "
                "using the power so, in a Divine aura of 5 or more. Not a "
                "Hermetic power: the figures are for mechanics only. PeMe 35 "
                "(Base 15, +1 Touch, +1 Cr requisite, +2 complexity): Ritual "
                "Power x2 (35 levels, -3 points).",
            ),
            b.power(
                "Gift of Blood",
                5,
                -12,
                "Corpus",
                rtd=("Touch", "", ""),
                level=25,
                does="Whoever drinks its blood gains the Tough Virtue until "
                "Rasa takes it back or the drinker dies; the Might stays out "
                "of its pool until then. Rasa may also heal itself of a "
                "Medium Wound or less, and that Might returns normally. No "
                "Hermetic equivalent. CrAn 25 (Base 20, +1 Touch): Ritual "
                "Power (25 levels).",
            ),
            b.power(
                "Sign of Peace",
                5,
                3,
                "Mentem",
                rtd=("Voice", "Moon", "Structure"),
                level=50,
                does="An incense-scented mist fills the building, and those "
                "without Magic Resistance can scarcely do violence or sin: they "
                "gain Peaceful +4, Kind +3 and Obedient +3. To act against "
                "these, one must fail an Ease Factor 9 roll on the trait, or "
                "pass one on an opposing trait at 9 plus the trait's bonus. A "
                "grog trying to hurt someone must fail 9+ on Peaceful or make "
                "13+ on Violent, Angry or Vengeful. ReMe 50 (Base 10, +2 Voice, "
                "+3 Moon, +3 Structure): Greater Power (50 levels), Improved "
                "Powers x2 (initiative).",
            ),
            b.power(
                "Scale of Truth",
                5,
                -7,
                "Mentem",
                rtd=("Sight", "Sun", "Room"),
                level=50,
                does="One of its scales, in plain sight, makes the eyes of "
                "anyone in the room flash red for an instant when they lie or "
                "quibble. Brothers who know of it look down or shut their eyes "
                "to fib, and hold a speaker's gaze when listening. It lasts "
                "until Rasa rescinds it, destroying the scale, and the Might "
                "does not return until then. InMe 50 (Base 10, +3 Sight, +2 "
                "Sun, +2 Room, +1 tethered to object): Greater Power (50 "
                "levels).",
            ),
            b.power(
                "Gift of the Stigmata",
                15,
                -26,
                "Corpus",
                rtd=("Arcane Connection", "Moon", "Individual"),
                level=75,
                does="Rasa imbues a scale and trades it to someone for a lock "
                "of hair. Until the next full moon, wounds that person takes "
                "while holding it pass to the dragon, which cannot Soak them "
                "but judges them on its own scale: a 13-point hit that would "
                "be a Heavy Wound on a Size 0 friar is a Light Wound to Rasa. "
                "CrCo 75 (Base 35, +4 Arcane Connection, +3 Moon, +1 Rego "
                "requisite): Ritual Power x3 (75 levels).",
            ),
        ],
        vis=[BodyVis(10, "Vim", "in its blood")],
        appearance=(
            "A wingless, eight-legged worm of some seventeen paces, of which "
            "three are head and eight tail. It is pale as mother-of-pearl at "
            "the neck, darkening along the back to the brown of old blood. "
            "Its belly hangs near the ground, yet its shoulder is a little over "
            "two paces high. Its fangs and talons are dagger-long, and its "
            "black, gold-ringed eyes are almost two palms wide. Mist heavy with "
            "sandalwood pours from its jaws, which do not move when it speaks, "
            "for the voice rises from far within."
        ),
        notes=paragraphs(
            "Wound Penalties as printed: -1 (1-13), -3 (14-26), -5 (27-39), "
            "Incapacitated (40-52), Dead (53+). Decrepitude n/a.",
            "Virtues as printed; the book calls Magic Animal 'Magical Animal' "
            "and Student of Divine 'Student of Dominion', and gives Rasa one "
            "more Minor Virtue of the storyguide's choice. Hunger for Any "
            "Magic is Hunger for (Form), but any vis will do. Magical Qualities "
            "name claws for Attack, Damage and Defense.",
            "Font of Knowledge (Minor Supernatural Virtue, p. 109): grants the "
            "Ability at 1. A roll of Intelligence + Font of Knowledge + stress "
            "die against 6 + 3 x the day's earlier uses, failures included, "
            "lets it try a task with an untrained Ability as if at score 2. "
            "After two uses, Rasa rolls 7 + stress die against 12.",
            "It can squeeze through most ordinary doorways, but no power lets "
            "it take human shape. Gift of Blood prints a Touch range and no "
            "Duration or Target.",
            "Sign of Peace is printed at 5 points though a 50-level Greater "
            "Power would cost 10.",
            "Naming it (p. 109): 'the abbot' keeps the focus on its office; an "
            "angelic name stresses the change in it; 'Rasa' stresses the "
            "dragon's past. The troupe's choice colours how the characters "
            "deal with it.",
        ),
        secrets=paragraphs(
            "Once a mere marauding serpent that gained a sliver of what it "
            "ate, it grew aware and began to choose: fewer beasts, more "
            "villages and caravans. A veteran of the Silk Road sent it east; "
            "years there gave it scraps of six tongues. A missionary priest "
            "turned it west toward the great cities of the Eastern Empire. "
            "It lingered in one "
            "place after another for decades, for centuries, until it ate the "
            "abbot.",
            "It threatened a remote abbey, and the abbot, a man of True Faith, "
            "went out alone to face it. Eating him gave it his understanding "
            "and Faith, and an epiphany that changed it. It took his place; "
            "the community called it a miracle and serves it devoutly. Its "
            "faith is genuine, though its grasp of people and the Divine is "
            "secondhand and a little flawed.",
            "It works to widen the Divine, believing that brings people nearer "
            "God and the world nearer Paradise: through charity, teaching "
            "crafts, and great works. It cares for the other realms only as "
            "foils, and may lure their creatures near for its monks to beat. "
            "Their texts and artifacts are to be gathered, hidden and at last "
            "destroyed. It treats opposition as God's test of its faith and "
            "never blames its opponents.",
            "Enemies: a Tremere whose Redcap lover it ate, who raised a "
            "vexillation that failed to hunt it; the jinn Howling Knife of the "
            "Dunes; and Stellatus (ArM5 p. 194, the Definitive Edition p. 465), "
            "who could not transform to stop its attack on a caravan he rode "
            "with, and fought it several times in the decades after.",
            "It eats trained birds for what they saw, the reason for the "
            "abbey's aviaries, and now and then dogs or cats, with a small "
            "prayer of thanks. Because these are natural and non-magical, "
            "Parma does not interfere, though neither bird nor dragon knows "
            "of it. It must eat vis, so friars harvest lesser sites, knowing "
            "that success destroys what it needs.",
            "It buried a hoard at every old lair, full of coin, jewels, "
            "weapons and curios. A trusted clergyman or penitent knight goes "
            "with a mule and a gift of its blood to fetch them, journeys that "
            "may take long, and its plans allow for that. From its stolen "
            "memories it also recalls where relics lie.",
        ),
    )


def _jinn(b: Builder):
    return b.creature(
        "Howling Knife of the Dunes",
        page="pp. 108-109",
        notes="A jinn. The book prints no statistics, Might or realm.",
        secrets=(
            "It sold protection to a sorcerer, whom Rasa ate, spoiling a "
            "reputation until then unblemished, and it hates the dragon still. "
            "The abbot's rivalry with it can be worked into later stories."
        ),
    )


def _abbey(b: Builder):
    return b.church(
        "The Abbey of the Reclusive Abbot",
        church="Monastery or nunnery",
        summary=paragraphs(
            "A remote abbey of good craftsmen, known for its charity, its "
            "fairs and its pigeon lofts. Its church-building and seasonal "
            "fairs bring work to the country round it, and the prior deals "
            "with outsiders, since the abbot keeps to his bed after driving "
            "off a dragon at great cost to his health.",
            "Visitors are kept to a small, detached part of the grounds. The "
            "scriptorium's windows are sealed with parchment, and the library "
            "is closed.",
        ),
        secrets=paragraphs(
            "The abbot is the dragon. Only a few monks know; three or four "
            "senior brothers run the house and tell the rest he has visions "
            "on his sickbed (use the priest, ArM5 p. 23, or Brother Julian, "
            "Art & Academe p. 85). The archdeacon may be among those who "
            "revere it. No one lies for it: they say the abbot cannot come or "
            "dine, and the prior stands in.",
            "The aura is Divine 4 or 5 in the abbey and scriptorium (p. 118). "
            "The order is the troupe's: the book says friars and monks "
            "loosely, and no order of 1220 has both, so decide at the start "
            "of the saga (p. 109).",
            "If discovery nears, the abbot 'dies', and a trusted elder or the "
            "prior is elected to front for it while it hides nearby or in the "
            "cellars. If nobles push in a new abbot, the monks do not contest "
            "it, but work to bring him into the fold.",
            "Relics and items (p. 113): Ancient Magic oddities such as "
            "Canaanite clay tablets, defixio plates, fetish figures or pieces "
            "of automata; texts about them; practical Hermetic devices of at "
            "most three magnitudes, for moving stones or clearing brush; and "
            "small relics such as thorns of the Crown, scraps of Christ's "
            "robe, slivers of the True Cross or saints' bones. It uses what "
            "it safely can for the people, as tools of God, then gives relics "
            "to the bishop after parading them; what it cannot use it destroys "
            "or locks away.",
            "A band's leader may carry a small relic giving a little Magic "
            "Resistance, and bands take four pigeons, two to send for help, "
            "one after two nights, and one kept for an attack.",
        ),
    )


def _variant(
    b: Builder, character: Character, label: str, age: int, block: StatBlock
) -> dict[str, Any]:
    version = b.stats(deepcopy(character), block)
    return {"label": label, "age": age, "character": asdict(version)}


def _friar_block(travelling: bool) -> StatBlock:
    """The block printed once with its choices marked: the friar's asterisked
    Virtue, Abilities and stick, or the cloistered monk's."""
    chosen = {
        "virtues": ["Mendicant Friar", "Well-Traveled"]
        if travelling
        else ["Priest", "Long-Winded"],
        "abilities": [
            ("Area Lore: (Travel Area)", 3, "travel routes"),
            ("Chirurgy", 2, "sword wounds"),
            ("Stealth", 1, "hiding in brush"),
        ]
        if travelling
        else [],
        "gear": "Monk's habit, sandals"
        + (", walking stick (club)" if travelling else ""),
    }
    return {
        "characteristics": characteristics(0, 0, 1, 1, 1, 2, 1, 2),
        "size": 0,
        "apparent_age": 34,
        "warping": (0, 4),
        "confidence": (1, 3),
        "virtues_flaws": [
            chosen["virtues"][0],
            "Clear Thinker",
            "Improved Characteristics",
            chosen["virtues"][1],
            "Monastic Vows",
            "Compassionate (Minor)",
        ],
        "abilities": [
            ("Area Lore: (Native Area)", 3, "towns and villages"),
            ("Artes Liberales", 2, "rhetoric"),
            ("Athletics", 2, "hiking"),
            ("Brawl", 2, "Dodge"),
            ("Charm", 2, "peasants"),
            ("Church Lore", 3, "local diocese"),
            ("Civil and Canon Law", 1, "regulations for the clergy"),
            ("Dominion Lore", 3, "saints"),
            ("Etiquette", 3, "Church"),
            ("Folk Ken", 6, "members of the diocese"),
            ("Intrigue", 2, "parishes"),
            ("Leadership", 3, "preaching"),
            ("Dead Language: Latin", 4, "religious phrases"),
            ("Living Language: (Second)", 4, "conversation"),
            ("Living Language: (Native)", 5, ""),
            ("Profession: (Or Craft)", 3, "appropriate to position in abbey"),
            ("Theology", 2, "scripture"),
            *chosen["abilities"],
        ],
        "traits": {"Pious": 3, "Dedicated": 2, "Loyal": 2},
        "reputations": {"Trustworthy (local)": 2},
        "notes": paragraphs(
            "Combat: Dodge Init +3, Defense +4. Club Init +3, Attack +4, "
            "Defense +3, Damage +4. Staff Init +4, Attack +6, Defense +6, "
            "Damage +3. Soak +2.",
            f"Fatigue: {FATIGUE}. {WOUNDS}",
            f"Equipment: {chosen['gear']}. Encumbrance 0 (0).",
            "The book prints one block with choices: Mendicant Friar or "
            "Priest; Well-Traveled, for a member who has gone out on the "
            "abbot's tasks, or Long-Winded; and Abilities and a stick marked "
            "for a friar. Its Native Language has no specialty.",
        ),
    }


def _friar(b: Builder) -> Character:
    friar = b.magus(
        "Friar or Monk of the Abbey",
        covenant=None,
        house="",
        age=34,
        type="companion",
        summary=(
            "A typical brother of the abbey in a woollen robe, trusted in the "
            "district. He sees to the house's daily needs and maintenance, "
            "or walks the roads on errands for its abbot. The abbot, he says, "
            "beat the dragon and lies recovering."
        ),
        secrets=(
            "These are the bulk of the dragon's servants, and few know what "
            "their abbot is. The senior priests do, and keep up the story."
        ),
    )
    blank = deepcopy(friar)
    b.variants[friar.id] = [
        _variant(b, blank, "Friar, travelling", 34, _friar_block(True)),
        _variant(b, blank, "Monk, cloistered", 34, _friar_block(False)),
    ]
    b.stats(friar, _friar_block(True))
    return friar


def _prior(b: Builder) -> Character:
    prior = b.magus(
        "The Prior of the Abbey",
        covenant=None,
        house="",
        age=43,
        type="companion",
        summary=(
            "He acts for the bedridden abbot: dealing with outside officials, "
            "supervising the monks and running the house, which he does "
            "excellently. Trusted locally and thought wise across the region, "
            "he may seem friendly and genial, brusque, or distant and "
            "calculating."
        ),
        secrets=paragraphs(
            "He knows. Choose his kind. A sincere man inspired by a miracle, "
            "Peter to the dragon's messiah. A faithless pragmatist who sees "
            "what a real miracle can do. Or a man unbalanced by a Divine act "
            "who might go either way, Paul or Judas: as a betrayer he goes on "
            "serving, collecting records, secretly asking for help, and "
            "learning weaknesses for those who would truly kill it.",
            "He inspects the sleeping quarters and dines with guests in the "
            "abbot's place, and may be elected abbot to front for the dragon.",
        ),
    )
    b.stats(
        prior,
        {
            "characteristics": characteristics(2, 1, 1, 2, 0, 2, -1, -2),
            "size": 0,
            "apparent_age": 43,
            "warping": (0, 2),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Senior Clergy",
                "Monastic Vows",
                "Intuition",
                "Regular",
                "Temporal Influence",
                "Vow (Minor)",
            ],
            "abilities": [
                ("Area Lore: (Native Area)", 3, "towns and villages"),
                ("Artes Liberales", 3, ""),
                ("Athletics", 1, "hiking"),
                ("Brawl", 2, "Dodge"),
                ("Carouse", 1, "remaining sober"),
                ("Charm", 3, "clergy"),
                ("Church Lore", 4, "local diocese"),
                ("Civil and Canon Law", 4, "regulations for the clergy"),
                ("Dead Language: Latin", 5, ""),
                ("Dominion Lore", 3, "saints"),
                ("Etiquette", 4, "Church"),
                ("Folk Ken", 4, "member of the diocese"),
                ("Intrigue", 3, "parishes"),
                ("Leadership", 3, "preaching"),
                ("Living Language: (Second)", 5, "conversation"),
                ("Living Language: (Native)", 5, ""),
                ("Profession: (Unspecified)", 3, "autocrat"),
                ("Theology", 3, ""),
            ],
            "traits": {"Organized": 3, "Calculating": 2, "Dedicated": 2},
            "reputations": {"Trustworthy (local)": 4, "Wise (regional)": 4},
            "notes": paragraphs(
                "Combat: Dodge Init +3, Defense +4. Soak +2.",
                "The book prints Dodge Init +3 and Defense +4 though his "
                "Quickness is -2 and Brawl 2; the figures are entered as "
                "printed.",
                f"Fatigue: {FATIGUE}. {WOUNDS}",
                "Equipment: Monk's habit, sandals, walking stick. Encumbrance 0 (0).",
                "The tiers of Vow are not printed: taken as Minor, which "
                "balances his Virtues and Flaws.",
            ),
        },
    )
    return prior


def _knight(b: Builder) -> Character:
    knight = b.magus(
        "Penitent Knight",
        covenant=None,
        house="",
        age=26,
        type="companion",
        summary=(
            "A lone knight in a black surcoat, of stoic bearing, with good "
            "gear and a good horse, known locally as pious and more widely as "
            "wrathful. He wears the black until his quest is done, to show "
            "his sinful state, and leads a small band of men-at-arms."
        ),
        secrets=(
            "He does not know what the abbot is. He seeks absolution for a "
            "wrong done on his travels, believes this task will win it, and "
            "cannot be talked out of it. He is met recovering an item or "
            "harvesting a vis site for the dragon."
        ),
    )
    b.stats(
        knight,
        {
            "characteristics": characteristics(0, -1, 1, 0, 2, 2, 2, 1),
            "size": 0,
            "apparent_age": 26,
            "confidence": (1, 3),
            "virtues_flaws": [
                "Knight",
                "Wealthy",
                vf_ability("Affinity with {ability}", "Single Weapon"),
                "Improved Characteristics",
                "Tough",
                "Warrior",
                "Oath of Fealty",
                "Continence",
                "Pious (Minor)",
                "Poor Student",
                ("Vow (Minor)", {"detail": "complete the abbot's task"}),
                "Wrathful (Minor)",
            ],
            "abilities": [
                ("Area Lore: (Native Area)", 4, "castles"),
                ("Area Lore: (Travel Area)", 3, "travel routes"),
                ("Athletics", 4, "armored"),
                ("Awareness", 1, "battle"),
                ("Brawl", 4, "dodge"),
                ("Chirurgy", 1, "sword wounds"),
                ("Etiquette", 3, "court"),
                ("Great Weapon", 4, "lance"),
                ("Hunt", 3, "boar"),
                ("Intrigue", 2, "court"),
                ("Leadership", 4, "small groups"),
                ("Dead Language: Latin", 1, "religious phrases"),
                ("Living Language: (Second)", 4, "commands"),
                ("Living Language: (Native)", 5, "commands"),
                ("Ride", 3, "battle"),
                ("Single Weapon", 5, "Long sword"),
                ("Theology", 2, "scripture"),
            ],
            "traits": {"Pious": 2, "Wrathful": 2},
            "reputations": {"Pious (local)": 2, "Wrathful (region)": 2},
            "notes": paragraphs(
                "Combat: Dodge Init +1, Defense +5. Lance and shield (mounted) "
                "Init +3, Attack +14, Defense +12, Damage +10. Long sword and "
                "shield (mounted) Init +3, Attack +15, Defense +14, Damage "
                "+11. Long sword and shield Init +3, Attack +12, Defense +11, "
                "Damage +8. Mace and shield Init +2, Attack +10, Defense +9, "
                "Damage +10. Soak +14.",
                f"Fatigue: {FATIGUE}. {WOUNDS}",
                "Equipment: War horse, full chain mail, heater shield, lance, "
                "long sword, mace. Encumbrance 2 (4).",
                "His men-at-arms: one grizzled veteran (ArM5 p. 21) and four "
                "standard soldiers (ArM5 p. 22). The tiers of his Flaws are "
                "not printed: the Personality Flaws are taken as Minor, which "
                "balances his Virtues and Flaws.",
            ),
        },
    )
    return knight


def _acumenis(b: Builder) -> Character:
    return b.magus(
        "Acumenis",
        covenant=None,
        house=EX_MISC,
        age=None,
        summary="A magus of Ex Miscellanea who keeps a journal.",
        secrets=(
            "The book gives no more than this. The journal describes Rasa at length, in a converted scriptorium "
            "(p. 108), so its writer has met the Dragon Abbot face to face."
        ),
    )


def _pilgrimages(b: Builder) -> None:
    """The distant sites the book offers to send the dragon to (p. 118)."""
    note = "Named as a distant pilgrimage goal for the devout."
    b.town("Jerusalem", summary=note)
    b.place("Sea of Galilee", realm=DIVINE, summary=note)
    b.church(
        "St Catherine's Monastery",
        church="Monastery or nunnery",
        summary="At Mount Sinai, with a great library; " + note.lower(),
    )
    b.town(
        "Santiago de Compostela",
        summary="At the end of the Way of St. James in Spain; " + note.lower(),
    )
    b.church(
        "Canterbury Cathedral",
        church="Archbishop's cathedral",
        summary="In England; " + note.lower(),
    )


def _threat(b: Builder):
    return dormant(
        b.threat(
            "The Abbey's Good Works",
            antagonist="The Reclusive Abbot",
            moves=TRACK,
            realm=DIVINE,
            summary=(
                "The abbey's generosity is changing the country around it: "
                "new and mended churches, fairs, paid apprenticeships, repairs "
                "to plough and wagon. Vis sites seem to yield less, and folk "
                "of the old places grow uneasy."
            ),
            secrets=paragraphs(
                "A long-term foe with no wish for open conflict. It remakes "
                "the covenant's world instead: as the Divine aura climbs, "
                "Magic and Faerie ones fade and vis fails. Run it behind "
                "another arc, using all four first stories in order, with two "
                "or three of the main arc's stories between each. The book's "
                "example braids it with Baron Geoffroi (p. 113). Treat these "
                "as stages of one slow rise, ending when the troupe notices "
                "or the storyguide chooses, when it becomes the main arc.",
                "Works. Relics found from memory are paraded to build faith, "
                "then given to the bishop. Hoard money rebuilds churches, "
                "bridges, walls and wells, opens missions and pays for "
                "seasonal fairs at the abbey (City & Guild p. 106), quietly "
                "refunding peasants' table fees. Apprentices sponsored go "
                "home and enrich their regions.",
                "How magi notice. Quaesitores and Hoplites may come asking, "
                "magi at the edge of their powers notice it first, or Tribunal "
                "assigns it. Faeries seek out the cause and may offer alliance. "
                "Demons driven off look for sinful grogs and covenfolk, "
                "possessing them past the Aegis or harassing them outside it. "
                "Failing vis sets covenants against each other in certamen "
                "and at Tribunal, which argues the effect and not the cause. "
                "Masons and craftsmen won't work for anyone but the abbey; "
                "grogs take vows and crusade, covenfolk go on pilgrimage, "
                "scholars shun the covenant, and loaned books vanish into the "
                "abbey.",
                "The soft way. Win its trust and talk it into leaving: a "
                "pilgrimage to Jerusalem or the Sea of Galilee, St Catherine's "
                "on Sinai, Santiago by the Way of St. James, Canterbury, or a "
                "far hermitage. It stays there, and people from that place "
                "may later come asking where it came from. Or persuade it "
                "to sacrifice itself for its flock against Mongols, Crusaders "
                "or a Moorish or Arab host, with gathered proof of such armies' "
                "cruelty.",
                "The hard way. A frontal attack is near hopeless, given its "
                "Might, the aura and the consequences of assaulting a house "
                "of God. Hurt its supports instead. Ambush travelling clergy, "
                "at a cost in nerve and reputation. Impersonate monks to "
                "disgrace them, risking confession. Turn the Church on them "
                "with charges of heresy or crimes, or expose what it is, since "
                "it is not even human. Blight crops and stock, for instance "
                "Wizard's Autumn (PeHe 15), a moon-long salting of the earth "
                "(CrTe 15: Base 3, +1 Touch, +3 Moon), Clouds of Rain and "
                "Thunder or Clouds of Summer Snow (CrAu 25), or Curse of the "
                "Ravenous Swarm (CrAn 45); destroy a flock's wool (PeAn 15: "
                "Base 3, +2 Voice, +2 Group); or stop milk and eggs (PeAn 25: "
                "Base 5, +2 Voice, +2 Group). Spoil trade, for instance with "
                "Pains of Perpetual Worry (CrMe 20), Panic of the Trembling "
                "Heart (CrMe 15) or a moon-long Recollection of Memories Never "
                "Quite Lived (MuMe 5), or tip off bandits. A dragonslayer or "
                "another dragon may do the fighting. With Arcane Connections "
                "gathered and the dragon drawn out of its aura, magi stand a "
                "good chance.",
                "The enemy of my enemy. Another covenant, demons, an archbishop, "
                "the whole Tribunal or faeries may do the deed, but each leaves "
                "consequences: Quaesitores stay, clergy start purges, demons "
                "stay on, and faeries may turn from heroes to despots.",
            ),
            stages=[
                S(
                    "Conflict Over Vis",
                    at=1,
                    clues=(
                        "The magi reach a vis site to find a recent camp and a "
                        "plain trail to monks resting at an inn, with vis from "
                        "several sites, some unknown to them or owned by other "
                        "covenants."
                    ),
                    ignored=(
                        "The monks go home with the vis. They refuse politely; "
                        "coerced, they take sanctuary in the church, send a "
                        "peasant as decoy, and release pigeons for help."
                    ),
                    stopped=(
                        "The storyguide decides ahead what rescue comes: "
                        "the dragon itself, a devoted knight, or none, so it "
                        "can study the aftermath. Other magi may arrive for "
                        "their vis, with certamen or murder in mind. Those who "
                        "kill monks become the abbot's targets, and other "
                        "covenants may fall to show its power."
                    ),
                    turned=(
                        "However it ends, Rasa eats the pigeons and learns who "
                        "was there and what they did."
                    ),
                ),
                S(
                    "A Spiritual Encounter",
                    at=2,
                    clues=(
                        "A thinking faerie or magical nature spirit, too weak "
                        "for the Aegis, asks to speak with the magi: the "
                        "abbey's growing aura will overrun its home. It offers "
                        "a vis site, an alliance or treasure."
                    ),
                    ignored=(
                        "It turns to other covenants or to outlaws, whose "
                        "harassment brings the lord and the Quaesitor "
                        "around."
                    ),
                    turned=(
                        "Townsfolk are building a church and graveyard on its "
                        "glade, cutting the standing stone into a cross. A "
                        "cheerful friar with a noble's soldiers tells of a "
                        "bell and a saint's relic to come."
                    ),
                ),
                S(
                    "The Friars Approach",
                    at=3,
                    clues=(
                        "A rich man dies without heirs and leaves the abbey "
                        "money, with the bishop's approval, to rebuild a "
                        "church in or near the covenant's grounds. If the "
                        "covenant has a church, the monks offer to improve "
                        "it, or Rasa 'accidentally' burns it in a storm. "
                        "Representatives come with a writ, backed by bishop "
                        "and nobles."
                    ),
                    ignored=(
                        "Friars ask a rich covenant for money, or offer a poor "
                        "one more buildings, apprenticeships and tax help for "
                        "labour, and a new congregation grows at the door."
                    ),
                    stopped=(
                        "A forged heir, a talk with the bishop, or sabotage "
                        "confuses the friars, who won't fight but tell the "
                        "abbot, and its attention follows."
                    ),
                ),
                S(
                    "Failing Resources",
                    at=4,
                    clues=(
                        "The old, friendly abbey now closes its doors. "
                        "Rumour says the abbot drove off the dragon and lies "
                        "abed. New building begins and friars go abroad."
                    ),
                    ignored=(
                        "Craft and library are lost to the covenant, and the "
                        "Divine aura goes on spreading from the abbey."
                    ),
                    stopped=(
                        "This story most easily reveals the truth. The "
                        "battlefield may hold Arcane Connections, scrying may "
                        "glimpse the dragon, and a friar on the road may talk."
                    ),
                    turned=(
                        "Rasa may offer a bargain: its wisdom for help "
                        "gathering relics and vis, with a share of the "
                        "salvage. Its demands grow, its aura nears the "
                        "covenant, and an ally becomes a close foe."
                    ),
                ),
                S(
                    "The Traitor Within, The Traitor Without",
                    at=5,
                    clues=(
                        "A monk who found out what the abbot is flees to the "
                        "magi, sure a beast that ate a saint must serve Hell, "
                        "with descriptions, Arcane Connections or wrong plans."
                    ),
                    stopped=("He may stay and advise or go back as an inside man."),
                    turned=(
                        "Or the dragon cultivates him unknowing, to feed the "
                        "magi lies and bring them out where it can destroy "
                        "them without collateral damage. It may think them "
                        "Infernal agents."
                    ),
                ),
                S(
                    "The Lord's Bargain",
                    at=6,
                    clues=(
                        "The abbey's hold on labour and goods frustrates the "
                        "local nobility. A clever lord, or one the covenant "
                        "has dealt with, seeks the magi against this secretive, "
                        "incorruptible, ever more popular abbot."
                    ),
                    ignored=(
                        "He offers limited autonomy or relief from feudal "
                        "dues in return for quiet action, a hard offer to "
                        "turn down."
                    ),
                    turned=(
                        "Once they accept, he won't take failure and threatens "
                        "civil punishment. Reckless magi may be charged at "
                        "Tribunal as court wizards to a mundane lord, and "
                        "must find a Quaesitor to speak for them or defend "
                        "themselves, while the abbot's power grows."
                    ),
                ),
            ],
        )
    )
