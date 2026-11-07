"""Bishop Orris (Antagonists pp. 7, 50-66), in paraphrase.

The bishop has the one full stat block; his household, his three friars and
his double are sketches with the ages and traits the book prints. The
cathedral is written up as a covenant (p. 52) because the book builds it on
that system, so its Boons, Hooks, books, relics and vis are his to call on.
The canons and the friars are factions with their members linked; St. John
the Apostle, whom the bishop invokes, is a creature.

His campaign against the magi is one dormant threat with a stage for each
step of it, and the book's side stories are dormant threats of their own.
The book leaves his diocese, his city and the origin of his curse to the
storyguide, so no place is named for them, and the choices stay in the
secrets. Rules the app does not model are in the secrets, cited by page."""

from __future__ import annotations

from ...models import Character, Covenant, Neighbour, Secret
from ..builder import (
    Builder,
    add_possession,
    boons_hooks_from,
    characteristics,
    dormant,
    joined_lines,
    paragraphs,
    titled,
    vf_great,
    vf_puissant,
)

S = Builder.stage
TRACK = "A track"
CANTORES = "trad_cantores"
CATHEDRAL = "The Cathedral of St. John the Apostle"


def build(b: Builder) -> None:
    cathedral = _cathedral(b)
    people = _people(b, cathedral)
    _factions(b, people)
    _saint(b)
    campaign = _campaign(b)
    b.link(campaign, "characters", people["orris"], "Drives it")
    b.link(campaign, "characters", people["adam"], "Secretary at the visitation")
    b.link(campaign, "covenants", cathedral, "His seat and his resources")
    _double(b, people)
    _side_stories(b)


# -- the cathedral --


def _cathedral(b: Builder) -> Covenant:
    what_matters = joined_lines(
        "Hook: Pilgrimage Site (Major) (Surroundings); Urban (Major) (Site)",
        "Boon: Aura (Major) (Site); Chapter of Canons (Minor) (Church); "
        "Edifice (Minor) (Lady Chapel, Fortifications); "
        "Edifice (Minor) (Chancel, Fortifications)",
    )
    cathedral = b.covenant(
        CATHEDRAL,
        founded=None,
        aura=5,
        realm="Divine",
        what_matters=what_matters,
        summary=paragraphs(
            "The seat of the diocese, in a city near the covenant. A relic of "
            "St. John the Apostle draws a steady stream of pilgrims, who are "
            "both a nuisance and an income to the cathedral's staff and "
            "congregation.",
            "The bishop is served by a secretary, several archdeacons, a "
            "chapter of canons and a crowd of assistants in minor orders. Each "
            "archdeacon runs the canon court and the Church's interests in his "
            "own archdeaconry; the canons keep the cathedral and sing in the "
            "choir that has made it famous.",
        ),
        notes=paragraphs(
            "Written up as a covenant, as The Church pp. 48-51 allows. The "
            "bishop may use its resources as a magus uses his covenant's "
            "(Ant p. 52). 502 Build Points. The Hooks and Boons are from The "
            "Church and Covenants.",
            "Divine aura 5, rising to 6 in the Lady Chapel (p. 52).",
            "Specialists (p. 52): provost of canons (Theology 5), chief "
            "chorister (Holy Music 8), 4 Cantores (Ceremony 5), 3 canons "
            "(Organization Lore: Church 5), archdeacon (Civil & Canon Law 7), "
            "2 notaries (Profession: Scribe 5), exorcist (Divine Lore 6), "
            "deacon (Profession: Steward 5), 4 doorwardens (Brawl 5), 8 "
            "acolytes used as clerks, scribes, messengers and distributors of "
            "alms (Organization Lore: Church 4).",
            "Setting it in a saga (p. 50): it fits most cities of western "
            "Mythic Europe. It need not be dedicated to St. John, but could "
            "still hold a major relic of his, since where the Hand lies is not "
            "known. Outside the Roman Church, change the details to suit "
            "Eastern Christianity.",
        ),
    )
    cathedral.boons_hooks = boons_hooks_from(what_matters)
    b.place(
        "The Lady Chapel of St. John's",
        realm="Divine",
        aura=6,
        summary="The cathedral's Lady Chapel, where the Divine aura is at its "
        "strongest.",
    )
    _library(b, cathedral)
    _relics(cathedral)
    for name, art, pawns, words in (
        ("Tears of St. John", "Creo", 3, "Tears on the statue of St. John."),
        (
            "Easter Echoes",
            "Imaginem",
            5,
            "Echoes in the cathedral following Easter Mass.",
        ),
        ("Chancel Water", "Vim", 2, "Water washed off the chancel steps."),
    ):
        add_possession(
            cathedral, "vis_source", name, art=art, pawns=pawns, description=words
        )
    return cathedral


def _library(b: Builder, cathedral: Covenant) -> None:
    theology = "Theology: Christian"
    church = "Organization Lore: Church"
    bible = [
        b.book(
            cathedral,
            "The Bible (Theology)",
            "Summa",
            ability=theology,
            level=10,
            quality=3,
        ),
        b.book(
            cathedral,
            "The Bible (Organization Lore)",
            "Summa",
            ability=church,
            level=3,
            quality=3,
        ),
    ]
    b.codex("The Bible", bible)
    b.book(
        cathedral,
        "Parish Register",
        "Summa",
        ability="Area Lore: Diocese",
        level=3,
        quality=5,
    )
    missal = [
        b.book(
            cathedral,
            "The Missal (Organization Lore)",
            "Tractatus",
            ability=church,
            quality=7,
        ),
        b.book(
            cathedral, "The Missal (Music)", "Tractatus", ability="Music", quality=7
        ),
    ]
    b.codex("The Missal", missal)
    b.book(cathedral, "Breviary", "Tractatus", ability=church, quality=8)
    b.codex(
        "Sentences",
        [
            b.book(
                cathedral,
                f"Sentences, tractatus {number}",
                "Tractatus",
                ability=theology,
                quality=9,
                author="Peter the Lombard",
            )
            for number in range(1, 5)
        ],
    )
    b.book(
        cathedral,
        "The Decretum",
        "Summa",
        ability="Civil and Canon Law",
        level=5,
        quality=11,
        author="Gratian",
    )
    b.book(
        cathedral,
        "Sic et Non",
        "Summa",
        ability=theology,
        level=5,
        quality=13,
        author="Peter Abelard",
    )
    b.book(
        cathedral,
        "Eight other tractatus",
        "Tractatus",
        quality=7,
        description="Eight more tractatus on Theology, Civil & Canon Law and "
        "Organization Lore: Church, all of Quality 7. The book does not say "
        "how many are on each subject (p. 52).",
    )


def _relics(cathedral: Covenant) -> None:
    add_possession(
        cathedral,
        "item",
        "The Hand of St. John the Apostle",
        description=paragraphs(
            "The hand that wrote the fourth Gospel, three Epistles and the Book "
            "of Revelation, and one of Christendom's most significant relics. "
            "St. John, the Beloved Disciple, guardian of the Blessed Virgin and "
            "brother of St. James the Greater, died at Ephesus. He and James "
            "were called the Sons of Thunder.",
            "Faith score 4, so 4 Faith Points and a Divine Might of 40 (p. 52). "
            "It gives its bearer Magic Resistance 40 (p. 66).",
            "Turn Back the Missile, 2 points, Init +5, appropriate Form: at "
            "Range Voice, guards up to 10 people from any missile, thrown, shot "
            "or moved by magic, and hurls each back at whoever sent it. The "
            "attacker defends against his own attack; any Penetration uses the "
            "relic's Might. It lasts until no longer needed, typically the end "
            "of the fight. It copies one of the saint's miracles.",
            "Curse of Drowning, 2 points, Init +8, Aquam: the target vomits sea "
            "water and begins to drown, for as long as the wielder concentrates "
            "or chooses. The target can do nothing else and makes Deprivation "
            "rolls (ArM5 pp. 180-181) every 30 seconds. If the target lives, any "
            "wounds from drowning become Long Term Fatigue levels.",
        ),
    )
    add_possession(
        cathedral,
        "item",
        "The Rib of St. Martin of Tours",
        description="A relic of the patron of beggars, horsemen and soldiers, a "
        "saint popular in France and Italy. Faith score 2, so 2 Faith Points "
        "and a Divine Might of 20. Its holder can activate the saintly power "
        "Grant of Serenity (RoP: The Divine Revised Edition p. 88).",
    )
    add_possession(
        cathedral,
        "item",
        "A Fragment of the True Cross",
        description="A relic of Faith score 1.",
    )
    add_possession(
        cathedral,
        "item",
        "Other minor relics",
        quantity=3,
        description="Three more minor relics, each of Faith score 1.",
    )


# -- the people --


def _people(b: Builder, cathedral: Covenant) -> dict[str, Character]:
    orris = _orris(b, cathedral)
    geoffrey = b.magus(
        "Archdeacon Geoffrey",
        covenant=cathedral,
        house="",
        type="companion",
        age=51,
        traits={"Avaricious": 3, "Self Important": 3, "Social Climber": 2},
        summary="The senior archdeacon of the diocese and the only one ordained "
        "a priest, so he is also called Father Geoffrey. He is at home in the "
        "intrigues of the bishop's household and likes to think of himself as "
        "the power behind the throne.",
        secrets=[
            titled(
                "Geoffrey's real influence",
                "He is no power behind the throne: Orris has seen his ambition "
                "and keeps real influence out of his hands (p. 51).",
            ),
            titled(
                "Geoffrey skims the funds",
                "He loves money and skims diocesan funds when he thinks it safe.",
            ),
            titled(
                "Geoffrey and the double",
                "He found Turstan, the bishop's double, a few years ago, and "
                'takes fees from clients for having the "bishop" bless new '
                "premises and ventures (p. 63).",
            ),
            titled(
                "Geoffrey and the summoner",
                "The summoner of the visitation may be in league with Geoffrey, "
                "inventing sins for the fees and fines (p. 54).",
            ),
            titled(
                "Geoffrey's archdeaconry",
                "The covenant lies in his archdeaconry. Orris questions him "
                "about it and has him ask around at his next visitation (p. "
                "58).",
            ),
        ],
    )
    adam = b.magus(
        "Deacon Adam",
        covenant=cathedral,
        house="",
        type="companion",
        age=32,
        traits={"Loyal to Bishop": 3, "Obsequious": 3, "Jealous": 2},
        summary="The bishop's devoted secretary, who is also chamberlain and "
        "steward of his household and his manservant. He guards his place at "
        "the bishop's side so jealously that he lets no one share the work, and "
        "goes about overworked and nearly always exhausted.",
    )
    peter = b.magus(
        "Father Peter",
        covenant=cathedral,
        house="",
        type="companion",
        age=67,
        traits={"Practical": 3, "Honorable": 2, "Brave": 1},
        summary="The provost of St. John's canons, and the bishop's confessor and "
        "confidant. He is old, suspects he has little time left, and worries "
        "that no one can follow him. He respects Brother Theodoric as a true "
        "mystic, but does not count him fit for so worldly a task.",
        secrets=[
            titled(
                "Father Peter's sway",
                "He could sway the bishop a great deal and has never tried (p. 51).",
            ),
            titled(
                "Who knows the bishop best",
                "Father Peter knows the bishop better than anyone, so an angel "
                "or saint guiding the characters might turn them toward him (p. "
                "63).",
            ),
            titled(
                "Father Peter and the canons",
                "He works hard to soothe the canons who feel passed over by the "
                "Cantores (p. 52).",
            ),
            titled(
                "Storyguide Notes",
                "Theology 5, as the cathedral's provost of canons (p. 52).",
            ),
        ],
    )
    theodoric = b.magus(
        "Brother Theodoric",
        covenant=cathedral,
        house="",
        type="companion",
        age=42,
        traditions=[CANTORES],
        traits={"Pious": 5, "Otherworldly": 3, "Hopeful": 1},
        summary="The chief chorister of St. John's and its most experienced "
        "singer. He is no natural leader, and does not notice that some "
        "canons feel snubbed.",
        secrets=[
            titled(
                "Theodoric and the Cantores",
                "He is the de facto head of the Holy Tradition of Cantores, "
                "which he founded here ten years ago. He picks recruits by the "
                "visions he receives.",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "He has True Faith (p. 52), and Holy Music 8 as chief "
                    "chorister (p. 52).",
                    "If Orris's motives are made selfish, Theodoric may turn "
                    "ally to the characters (p. 53). If the bishop is murdered, "
                    "his ghost may come to Theodoric and tell how he died (p. "
                    "66).",
                ),
            ),
        ],
    )
    friars = {
        "peter": b.magus(
            "Brother Peter",
            covenant=None,
            house="",
            type="companion",
            age=None,
            summary="A black-habited friar, common-born and cheerful, with a "
            "ready store of Scripture. He keeps up a running banter with Brother "
            "Bartholomew, whom he resembles so closely that they could be kin, "
            "and he speaks the diocese's language as his own.",
            secrets=[
                titled(
                    "Brother Peter's learning",
                    "More the theologian of the pair, with a great memory for "
                    "Scripture (p. 59).",
                ),
                titled(
                    "Storyguide Notes",
                    "See The Friars Preacher for his statistics.",
                ),
            ],
        ),
        "bartholomew": b.magus(
            "Brother Bartholomew",
            covenant=None,
            house="",
            type="companion",
            age=None,
            summary="A black-habited friar who plays the fool to draw a crowd, "
            "with a practised pratfall and a head-over-heels tumble. He is so "
            "like Brother Peter that they could be brothers by blood, and his "
            "banter puts people at their ease.",
            secrets=[
                titled(
                    "Behind Bartholomew's clowning",
                    "His clowning and common manners hide a keen mind and an "
                    "academic training (p. 59).",
                ),
                titled(
                    "Storyguide Notes",
                    "See The Friars Preacher for his statistics.",
                ),
            ],
        ),
        "alonso": b.magus(
            "Brother Alonso",
            covenant=None,
            house="",
            type="companion",
            age=None,
            summary="A black-habited friar from a distant kingdom, with a thick "
            "accent and no visible humour. He seems a little sinister, gives no "
            "quarter to sin, and likes to describe the torments of sorcerers in "
            "Hell in fine detail.",
            secrets=[
                titled(
                    "Alonso's command of the tongue",
                    "He understands the local tongue better than he lets on, and "
                    "uses his seeming ignorance to keep his distance from the "
                    "others (p. 59).",
                ),
                titled(
                    "Storyguide Notes",
                    "He may come from Aragon or Sicily; rename him Alan if he is "
                    "from northern Europe. See The Friars Preacher for his "
                    "statistics.",
                ),
            ],
        ),
    }
    return {
        "orris": orris,
        "geoffrey": geoffrey,
        "adam": adam,
        "peter": peter,
        "theodoric": theodoric,
        **{f"friar_{key}": friar for key, friar in friars.items()},
    }


def _orris(b: Builder, cathedral: Covenant) -> Character:
    orris = b.magus(
        "Bishop Orris",
        covenant=cathedral,
        house="",
        type="companion",
        age=57,
        summary=paragraphs(
            "The bishop of the diocese, a long, gaunt man with a great beak of "
            "a nose and bright blue eyes. The red hair of his youth has gone "
            "white, though he has kept it all but the tonsure. In the pulpit "
            "he is formidable, with a big voice and a sure command of "
            "argument, and he can move a congregation.",
            "He is a local man made good, the second son of a wealthy knight who "
            "grew up in the diocese and served as a parish priest in it before "
            "his election, and the city is proud of him. He preaches in his "
            "people's own tongue, unlike the standoffish bishop before him, and "
            "knows their troubles. He is known for his sense of justice, for "
            "mediating disputes between prominent locals, and for standing with "
            "the poor against the powerful. The citizens love to see him face "
            "down lords who lean on the free men of the city.",
            "Churchmen think well of him. The story goes that a saint called him "
            "to religion in a dream. He joined the Benedictines, then after "
            "ordination won release from his monastic vows to take a parish, "
            "against his family's wishes. The abbey where he was a novice was "
            "abandoned soon after, for innocent reasons. He was known for quiet "
            "faith, strength of character and efficiency, and his election "
            "surprised no one.",
        ),
        secrets=_orris_secrets(),
    )
    b.stats(
        orris,
        {
            "characteristics": characteristics(1, 0, 2, 4, -1, -1, -1, -1),
            "aging_points": {"communication": 2, "strength": 1, "quickness": 1},
            "size": 0,
            "apparent_age": 47,
            "decrepitude": (1, 0),
            "warping": (1, 5),
            "confidence": (1, 3),
            "virtues_flaws": [
                "Senior Clergy",
                "Educated",
                vf_great("Communication"),
                "Inspirational",
                "Magic Sensitivity",
                "Privileged Upbringing",
                vf_puissant("Magic Sensitivity"),
                "Sense Holiness and Unholiness",
                "Meddler (Major)",
                "Mistaken Identity",
                "Clumsy",
                (
                    "Lesser Malediction",
                    {"detail": "cannot distinguish evil from magic"},
                ),
                ("Fear", {"detail": "the Infernal; from Warping"}),
                "Noncombatant",
                "Poor Hearing",
            ],
            "traits": {
                "Protective of Flock": 4,
                "Paranoid About Hell's Intentions": 3,
                "Brave": 2,
                "Devoted to God": 2,
            },
            "reputations": {"Just (Local)": 4, "Trustworthy (Ecclesiastic)": 3},
            "abilities": [
                ("Dead Language: Ancient Greek", 3, "translation"),
                ("Area Lore: Diocese", 4, "parishes"),
                ("Artes Liberales", 2, "rhetoric"),
                ("Charm", 3, "invoking saints"),
                ("Civil and Canon Law", 5, "papal bulls"),
                ("Concentration", 3, "while praying"),
                ("Dominion Lore", 2, "Cantores"),
                ("Etiquette", 4, "the Church"),
                ("Folk Ken", 4, "penitents"),
                ("Intrigue", 5, "church politics"),
                ("Dead Language: Latin", 4, "liturgy"),
                ("Leadership", 6, "holy influence"),
                ("Magic Sensitivity", 3, "practitioners of magic"),
                ("Living Language: (Native)", 5, "exhortation"),
                ("Organization Lore: Church", 5, "clergy"),
                ("Organization Lore: Nobility", 3, "pious nobles"),
                ("Organization Lore: Order of Hermes", 0, "legal issues"),
                ("Philosophiae", 2, "theological concordance"),
                ("Profession: Preaching", 4, "swaying hearts"),
                ("Ride", 1, "on roads"),
                ("Sense Holiness and Unholiness", 2, "good"),
                ("Theology: Christian", 7, "biblical knowledge"),
            ],
            "notes": paragraphs(
                "Equipment: ruby ring of office, clerical vestments. He may also "
                "carry the Hand of St. John, particularly if he fears for his "
                "life from supernatural sources; he does not routinely carry the "
                "cathedral's relics when he enters the saga. Encumbrance 0 (0).",
                "As printed (p. 51): Faith Score 0 (1), the point coming from "
                "taking the Eucharist. Dodge: Init -1, Attack n/a, Defense -1, "
                "Damage n/a. Soak -1. Fatigue levels OK, 0, -1, -3, -5, "
                "Unconscious. Wound penalties -1 (1-5), -3 (6-10), -5 (11-15), "
                "Incapacitated (16-20), Dead (21+).",
                "The block gives Magic Sensitivity as 3+2, the +2 from Puissant, "
                "Organization Lore: Order of Hermes as 0 (2), and Divine Lore "
                "and Civil & Canon Lore, entered here as Dominion Lore and Civil "
                "and Canon Law. Meddler is taken as the Major Flaw, by its place "
                "in the block's list.",
                "Both his Supernatural Abilities are Divine: no supernatural "
                "aura penalizes them, and a Dominion aura adds to them (p. 51).",
            ),
        },
    )
    _set_experience(orris, "Organization Lore: Order of Hermes", 2)
    return orris


def _set_experience(character: Character, ability: str, xp: int) -> None:
    """The experience a block prints beside a score ("0 (2)")."""
    next(a for a in character.abilities if a.name == ability).xp = xp


def _orris_secrets() -> list[Secret]:
    return [
        titled(
            "Orris's curse",
            "He senses evil and the good in people's hearts, and he senses "
            "magic, but his curse makes the two one to him. He has met the "
            "power of Hell and feels the same thing around magic, and has never "
            "felt magic any other way, so he does not know the two can be told "
            "apart. Add his piety and his dread of the Infernal, and he takes "
            "the characters for Hell's allies (pp. 50, 57).",
        ),
        titled(
            "What Orris knows of the Order",
            "He has a working knowledge of the Order, partly wrong through the "
            "Order's own misinformation (Lords of Men pp. 40-41). He thinks "
            "covenants are like chapters or monasteries; he knows, unless they "
            "have hidden it, that this one lies in his diocese, and perhaps its "
            "name. He has never met a magus and expects blue robes, tall "
            "brimmed blue hats and staves. He knows of the Order's laws, its "
            "secret Tribunals and its democracy (pp. 52-53).",
        ),
        titled(
            "Orris reserves judgment",
            "Sorcerers Orris has met seemed evil to him. He accepts in reason "
            "that not all wizards are evil, but God has given him the power to "
            "know evil, and he reserves judgment until he meets them himself "
            "(pp. 52-53).",
        ),
        titled(
            "What Orris feels near the supernatural",
            "Near a Divine, Infernal or Magic manifestation Orris grows dizzy "
            "and breaks into a cold sweat. The Divine brings joy and rays of "
            "golden light from the source; Infernal or Magic things are hard to "
            "look at, wrapped in gloom and hollow despair (p. 56).",
        ),
        titled(
            "Orris's nights of prayer",
            "He spends night after night prostrate on the chancel steps, "
            "praying for a sign that he judges rightly and that his way is the "
            "only way to protect his people (p. 62).",
        ),
        titled(
            "Orris under threat",
            "If the characters are thought ruthless Orris may hire bodyguards "
            "and keep the relics by him. He prays for a miracle if attacked. "
            "Beyond that he is an aging man who has never fought and is easily "
            "killed (p. 66).",
        ),
        titled("Storyguide Notes", _orris_notes()),
    ]


def _orris_notes() -> str:
    return paragraphs(
        "He is a good man acting for his flock: run him as a puzzle to solve, "
        "not a monster to beat (p. 50).",
        "Who cursed him is the storyguide's choice (p. 57). God or an angel, to "
        "test whether the characters will keep the high ground and hold back "
        "their power. A demon, years ago, when he was a rising priest, so that "
        "a dangerous enemy of Hell would waste himself on magic and the "
        "innocent. Or a powerful hedge wizard or faerie he offended when young: "
        "fittingly, he probably saw something he did not understand and "
        "called it the Devil's work.",
        "His Magic Sensitivity (p. 56): he "
        "must Penetrate any Magic Resistance to feel anything. The Ease Factor "
        "to detect a Gifted person is 15 minus the highest Art divided by 5, or "
        "the highest Supernatural Ability. Next to the altar his Dominion aura "
        "of 5 and the Just temper add to the roll. A character on trial stands "
        "in aura 5, bystanders in aura 4; subtract 3 times the aura from Magic "
        "Resistance within the Dominion. He may detect a spell or an enchanted "
        "item instead. If he fails to Penetrate, the target feels something "
        "rebuffed. The storyguide may simply rule that he succeeds.",
        "What a character knows of him (p. 54): Intelligence + Organization "
        "Lore: Church, or a stress die + his Reputation of 4 without it; "
        "everything up to the highest Ease Factor beaten. Botch: facts about a "
        "different bishop. 3: this is Bishop Orris. 6: he is thought fair, and "
        "his city is proud of him. 9: he is a local, raised about ten miles "
        "from here. 12: he is influential in his city and a powerful orator. "
        "15: he has been very hard on sorcerers.",
        "Holy Influence (pp. 55, 57): Presence + Leadership + stress die. 9 "
        "grants +1, 15 grants +2, 24 grants +3. The temper of the Dominion is "
        "described in RoP: The Divine Revised Edition pp. 38-40.",
        "His frame of mind (p. 62): a spy in the cathedral may learn from his "
        "nights of prayer that he is no villain and that peace can still be "
        "found.",
        "Attacking him (p. 66): he may be warned of a plot in a dream. The Hand "
        "gives Magic Resistance 40, and his usual Dominion aura of at least 4 "
        "raises it to 44.",
        "Reworking him (pp. 53-54). Not a bishop: an abbot changes least; a "
        "Templar preceptor or a pious noble tied to the clergy, perhaps by a "
        "younger brother, may need rebuilt, more martial statistics. Other "
        "motives: he may not be deluded at all, but resent the magi's power or "
        "covet a resource such as an income. Then the Cantores help him less, "
        "Theodoric may side with the characters, and his allies are less loyal. "
        "He could be truly corrupt, but use this with care: it is a tired "
        "figure, it loses the dilemma, and angels and saints make such a man "
        "unlikely in that seat.",
        "More powerful (pp. 53-54): an archbishop or cardinal has personal Magic "
        "Resistance that stacks with relics, and the Commanding Aura (RoP: The "
        "Divine Revised Edition pp. 42-43; The Church p. 26). An archbishop's "
        "cathedral should have another 500 Build Points. The Cantores may gain "
        "Holy Powers and act at his direction; Understanding would give him "
        "counsel and visions of what the characters do. A Templar, Hospitaller "
        "or Teutonic preceptory in his city brings the knights in sooner, "
        "their engines protected by a Cantores Blessing of Magic Resistance. "
        "Weaker: he is a busy man and can afford to move slowly unless they "
        "retaliate, so make him less ardent.",
    )


# -- the groups --


def _factions(b: Builder, people: dict[str, Character]) -> None:
    chapter = b.faction(
        "The Cathedral Chapter of St. John",
        faction="Religious community",
        members=9,
        ruler="Father Peter",
        tradition=CANTORES,
        realm="Divine",
        summary="The nine canons of St. John's, who care for the cathedral and "
        "sing its plainchant under the provost, Father Peter. The choir's music "
        "fills the congregation with wonder at God, or whatever feeling suits "
        "the Mass, and it has made the cathedral famous. Some canons feel "
        "snubbed at being left out of Brother Theodoric's circle of singers.",
        secrets=[
            titled(
                "The Cantores among the canons",
                "Five of the nine canons, Theodoric among them, are a Holy "
                "Tradition of Cantores, who worship through plainchant. The "
                "other four, Father Peter among them, sometimes join their group "
                "ceremonies (p. 53).",
            ),
            titled(
                "Orris and the Cantores",
                "Orris knows what the Cantores can do and is in awe of their "
                "faith. He has rarely asked for their miracles, trusting "
                "Theodoric's piety.",
            ),
            titled(
                "The chapter's blessing on Orris",
                "In thanks for his rarely asking for their miracles, the chapter "
                "has blessed Orris's health in a yearly ritual for 10 years.",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The Cantores are in RoP: The Divine Revised Edition pp. "
                    "93-94. Their favored Abilities are Holy Music, Invocation, "
                    "Blessing and Enchanting Music; they use the last to move "
                    "the congregation (p. 53).",
                    "The yearly blessing on Orris gives +5 to his aging rolls "
                    "(Holy Music / Blessing 50), and is the source of his "
                    "Warping.",
                    "Ceremony totals (p. 53): Theodoric leading the four "
                    "Cantores adds +24 to miraculous effects (the Cantores' "
                    "Presence + Holy Music). The full nine, unled, add +46 (+25 "
                    "group bonus, -9 participants, +30 from the Cantores' and "
                    "canons' Presence + Holy Music). By Invocation instead of "
                    "Holy Music, the bonus from Communication + Invocation is "
                    "+14 led and +16 unled.",
                    "The block of specialists gives the 4 Cantores Ceremony 5 "
                    "(p. 52), an Ability not among the favored ones of p. 53.",
                ),
            ),
        ],
    )
    for key, note in (("theodoric", "Chief chorister"), ("peter", "Provost")):
        b.link(chapter, "characters", people[key], note)
    b.link(chapter, "characters", people["orris"], "The bishop they bless")
    friars = b.faction(
        "The Friars Preacher",
        faction="Religious community",
        members=3,
        rules="They travel together and preach by turns, drink little, eat "
        "frugally, and stay only a few nights in each town or village.",
        wants="To turn hearts from idolatry and sin, and to expose the sorcerers "
        "named to them.",
        realm="Divine",
        summary="Three black-habited Dominican friars lent to the diocese by the "
        "local chapter house, and models of good conduct. They preach by turns "
        "in market squares and alehouses, moving on every few nights. Their "
        "theme is God's hatred of idolaters and sorcerers, whom they put beside "
        "murderers, adulterers, perjurers and fornicators.",
        secrets=[
            titled(
                "Who sent for the friars",
                "The Order of St. Dominic was founded to fight heresy, and "
                "Orris asks for these three friars once his inquiries are done "
                "(p. 59).",
            ),
            titled(
                "What the friars say of the magi",
                "The friars call magicians fraudsters who fake miracles, sinners "
                "against Nature and God, and idolaters who call on demons. They "
                "name the player magi outright, using whatever Orris has found, "
                "but they are honest: they do not embellish or lie (p. 59).",
            ),
            titled("Storyguide Notes", _friar_notes()),
        ],
    )
    for key in ("friar_peter", "friar_bartholomew", "friar_alonso"):
        b.link(friars, "characters", people[key], "A member")
    b.link(friars, "characters", people["orris"], "Asked for them")
    _knights(b)


def _friar_notes() -> str:
    return paragraphs(
        "On preachers, see Art & Academe pp. 13-14.",
        "Their statistics are not printed. Base them on the Franciscan "
        "friar of RoP: The Divine Revised Edition p. 96, with Profession: "
        "Preacher in place of Teaching, and perhaps a Puissant Virtue in "
        "it (p. 59). Finding them may take several days of following their "
        "trail (p. 59).",
        "Reputation (p. 59): their campaign gives everyone identified with "
        "the covenant's magic a bad Reputation of 1, its nature varying by "
        "person. Each identifiable event adds an experience point, and so "
        "does each season of preaching; it rises as an Ability (ArM5 p. "
        "167). It hurts business in the diocese and the covenfolk's loyalty "
        "(Covenants p. 40).",
        "Against them (p. 64): a public clash rallies the locals against "
        "the attacker, and three mysterious deaths feed the rumours. Orris "
        "sends replacements, who raise Reputation at half the rate, these "
        "three being the order's best. If deaths go on, their superior "
        "eventually refuses to send more.",
        "Debate (p. 64): a formal challenge draws wide attention, and the "
        "bad Reputation gains no experience that season; an ad hoc "
        "debate does not give this. Rules are in Houses of Hermes: "
        "Societates p. 90 and Art & Academe p. 104. The friars keep to "
        "academic disputatio; magi may range wider but suffer The Gift's "
        "penalty. A win earns a good Reputation of 1 that counters the "
        "bad, possibly for the others too. A loss still stops the rise "
        "that season; a botch adds a point. Later debates earn 1 experience "
        "each, and only one debate a season counts.",
        "Scripture they may quote (p. 60): Wisdom 17:7; Exodus 22:18; "
        "Leviticus 19:31 and 20:27; Deuteronomy 18:10-12; 1 Samuel 15:23; "
        "Isaiah 47:13-14; Micah 5:12-13; Malachi 3:5; Galatians 5:19-21; "
        "Revelation 21:8 and 22:14-15.",
    )


def _knights(b: Builder) -> None:
    b.faction(
        "The Church Knights",
        faction="Military order",
        wants="To fight pagans and infidels, as the pope charges them, and to aid "
        "a bishop who asks with the authority of his rank.",
        summary="Whichever military order keeps the nearest commandery: the Order "
        "of Santiago in Iberia, the Teutonic Order, working from Hungary, in "
        "eastern Europe, and the Knights Templar nearly everywhere else. They "
        "are veterans of war, of sieges above all.",
        secrets=[
            titled(
                "The knights' commander",
                "The Church knights' commander has direct experience in the Holy "
                "Land and siege engineers who can undermine a fortress; he leads "
                "his force as a trained group (p. 62).",
            ),
            titled(
                "The knights' relics",
                "Each of the Church knights very likely has a relic (p. 62).",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The commander has Leadership 5 (p. 62).",
                    "Numbers (p. 62): at least five knights beyond the "
                    "commander, and a dozen or more sergeants, sized to the "
                    "covenant's strength before any desertions: at least as many "
                    "sergeants as the turb had grogs, and as many knights as "
                    "there are companions.",
                    "Statistics (p. 62): The Church pp. 126-127. Otherwise, "
                    "knights are the Knight companion template (ArM5 p. 23), "
                    "sergeants the Standard Soldier (ArM5 p. 22), and the leader "
                    "of each trained group of five a Grizzled Veteran (ArM5 p. "
                    "21). Each knight's relic is of Faith 1 or more. Mass "
                    "warfare and sieges: Lords of Men pp. 109-116.",
                    "This is the generic force of the story. Sagas with a "
                    "Tribunal pack may already hold the order itself.",
                ),
            ),
        ],
    )


def _saint(b: Builder) -> None:
    b.creature(
        "St. John the Apostle",
        page="p. 61",
        realm="Divine",
        might=75,
        appearance="Shown in art with a chalice and serpent, a book, or an eagle.",
        powers=[
            b.power(
                "Curse of Drowning",
                2,
                8,
                "Aquam",
                rtd=("", "Concentration", ""),
                does="As the Hand of St. John's power (p. 52): the target vomits "
                "sea water and drowns, unable to act, making Deprivation rolls "
                "every 30 seconds until the wielder stops.",
            ),
            b.power(
                "Grant Visions",
                2,
                0,
                "Imaginem",
                does="A true vision of the future, clouded in mystical allegory. "
                "Intelligence + Divine Lore against Ease Factor 9 gives a rough "
                "reading; a higher roll reveals more.",
            ),
            b.power(
                "Heal Burns",
                2,
                0,
                "Corpus",
                does="Heals any non-lethal wound caused by fire.",
            ),
            b.power(
                "Purge Poison",
                1,
                0,
                "Corpus",
                does="The target vomits the poison up, is healed of any non-lethal "
                "wound or fatigue from it, and takes no more damage.",
            ),
            b.power(
                "Turn Back the Missile",
                2,
                5,
                "",
                rtd=("Voice", "", "Up to 10 people"),
                does="As the Hand of St. John's power (p. 52), of the appropriate "
                "Form: missiles are hurled back at those who sent them.",
            ),
        ],
        notes=paragraphs(
            "Areas of veneration: authors, booksellers, friendships, against "
            "burns and poisoning, and tanners. Feast: December 27.",
            "He also has Expel Demons, Ignis Domini, Raise the Dead and Terrify "
            "the Unbeliever, whose figures this book does not print; see RoP: "
            "The Divine Revised Edition.",
            "Invoked by Bishop Orris (p. 60) under RoP: The Divine Revised "
            "Edition p. 87, and by humiliating his relic under RoP: The Divine "
            "pp. 87-88. If moved, he strikes with Curse of Drowning or Ignis "
            "Domini.",
        ),
    )


# -- the stories --


def _campaign(b: Builder) -> Neighbour:
    return dormant(
        b.threat(
            "Bishop Orris's War on Sorcery",
            antagonist="Bishop Orris",
            moves=TRACK,
            realm="Divine",
            summary="The covenant lies in Bishop Orris's diocese, and he has been "
            "hard on sorcerers before. He is a just man, much loved by his flock.",
            secrets=_campaign_secrets(),
            stages=[
                S(
                    "The Visitation",
                    at=1,
                    clues="Every year a bishop must inspect his parishes, and Orris "
                    "usually leaves this to his archdeacon, who skips the remote "
                    "ones. The archdeacon has fallen ill, so the bishop comes "
                    "himself. Word reaches the covenant that a summoner, a "
                    "sub-deacon paid by the accused, has called someone to the "
                    "bishop's court for sorcery. The accused may be a farmer who "
                    "sells to the covenant, a past servant, a grog's relative, a "
                    "Dependent or True Love, or a magus notorious for a crime.",
                    ignored="The bishop arrives in mid-afternoon with his "
                    "secretary, four acolytes and four hired guards, ten in all "
                    "(more in lawless country), and the parish holds a feast. "
                    "A magus or companion of standing may be asked to sit at his "
                    "table, and the fateful meeting may happen there.",
                    turned="Intelligence + Organization Lore: Church against Ease "
                    "Factor 9 shows his retinue is unusually small, for two or "
                    "three times as many are allowed and can ruin a parish.",
                ),
                S(
                    "The Bishop's Court",
                    at=2,
                    clues="He holds court in the parish church the next day, on a "
                    "platform before the altar, with a notary and Deacon Adam. "
                    "He prays for justice and wisdom, tempering the Dominion aura "
                    "toward Justice, which aids all efforts to uncover secrets. "
                    "After the checklist of parish duties he tries the small "
                    "cases (brawling in church, missed festivals, a birth seven "
                    "months after a wedding) with warnings, small fines and "
                    "public penance, fairly and without undue leniency.",
                    ignored="If he senses magic on the accused he blanches, speaks "
                    "hotly of the danger of sorcery, then resorts to compurgation, "
                    "since he will not convict on hearsay. With fewer than 12 "
                    "oath-takers on the Bible he convicts: public penance such as "
                    "a white sheet before the congregation, a fine, or, for a "
                    "major crime done by magic, the secular courts.",
                    stopped="Twelve people swear to the accused's good character "
                    "and the accused goes free. Parishioners are slow to step "
                    "forward, and the accused may beg the covenant for witnesses.",
                    turned="A magus who swears for the accused is sensed as he takes "
                    "the oath: the bishop says nothing but marks him. If magic is "
                    "used to sway witnesses and he notices, he stops the hearing "
                    "and takes the accused to the cathedral for a full trial, "
                    "seeing Hell's hand at work.",
                ),
                S(
                    "Orris's Dilemma",
                    at=3,
                    clues="The court's verdict matters little: what counts is that "
                    "he smells Hell on a magus. Failing that, he meets one on the "
                    "road or at an inn, inspects a covenant chapel and feels the "
                    "aura through any gap in the Aegis, hears a priest's testimony "
                    "of a spell, or hears a grog's confession.",
                    ignored="He goes home to pray, torn between fighting evil and "
                    "sparing the weak. Short of knowledge and fearing for his "
                    "flock in a war, he decides to move slowly: learn about the "
                    "enemy and strengthen his parishes. The characters probably "
                    "do not yet know that they have an enemy.",
                ),
                S(
                    "A Prudent Populace",
                    at=4,
                    clues="Sermons on Prudence, with examples from his court; advice "
                    "to secular judges; open spiritual counsel. Grogs find less "
                    "drink, gambling and female company. Locals grow curious, "
                    "cautious and shrewd at bargaining, give no credit, and the "
                    "steward sees costs creep up. Vendors rethink trading with "
                    "wizards, and allies want assurances.",
                    ignored="All Dominion auras in the diocese take a Wise temper. "
                    "Roll his Holy Influence the first time each season that the "
                    "characters deal seriously with mundanes there. The bonus "
                    "goes to Careful, Cautious, Chaste, Practical and Prudent and "
                    "to sensible choices; the penalty to Ambitious, Overconfident, "
                    "Naive and Lecherous. Characters and covenfolk feel it only if "
                    "they live in a Dominion aura.",
                    turned="Perception + Folk Ken: Ease Factor 6 shows something has "
                    "changed, 9 pinpoints it. Intelligence + Divine Lore 6 traces "
                    "it to the temper of the Dominion.",
                ),
                S(
                    "Gathering Information",
                    at=5,
                    clues="A roadside stranger's chat turns oddly probing. An ally "
                    "asks whether a character ever met the cousin who came asking "
                    "where he lived. A Quaesitor, told through agents in the "
                    "papacy that a legate has been asked about the magi, arrives "
                    "to look into them without saying why, and may seem to be "
                    "behind it all.",
                    ignored="He questions Archdeacon Geoffrey, who listens for "
                    "complaints, rumours and ties to notables, so Orris learns "
                    "their local and ecclesiastic Reputations. Two hired agents "
                    "work the nearest towns and question friends, serfs and "
                    "enemies; he warns them off the covenant's servants unless "
                    "these are known to be unhappy. He writes to the papal legate "
                    "if the saga has one. He ends with at least most names; at "
                    "most, each magus's magic, weaknesses and crimes.",
                    stopped="The characters' own agents spot his and turn the "
                    "tables. Start that story mid-encounter, with the agents "
                    "fleeing home with news; if they die, no one learns it.",
                ),
                S(
                    "The Friars Preacher",
                    at=6,
                    clues="Rumours about the magi, and even the covenfolk, come back "
                    "from the villages. Mundanes turn sullen, hostile or afraid. "
                    "Grogs turn surly. Tracing the talk leads to Dominicans "
                    "preaching in a nearby village.",
                    ignored="Brothers Peter, Bartholomew and Alonso preach against "
                    "the magi by name, and the bad Reputation grows season by "
                    "season.",
                    stopped="Debate holds the Reputation back; see The Friars "
                    "Preacher.",
                ),
                S(
                    "Blame the Witch",
                    at=7,
                    clues="The characters are blamed for every misfortune in the "
                    "diocese, until they see how many rumours name them and "
                    "go looking for the source.",
                    ignored="See the side stories: The Bewitched Cows, The Familiar "
                    "on Trial, The Fallen Church and Unwanted Attention.",
                ),
                S(
                    "Invoking St. John",
                    at=8,
                    clues="This comes whenever the characters move directly and "
                    "openly against the bishop or diocese.",
                    ignored="He leads a public ceremony to call down the saint's "
                    "wrath on them, and repeats it daily if it fails. If the crime "
                    "was heinous and the saint has not answered, he humiliates the "
                    "relic the next week to force the saint's hand. If either "
                    "works, St. John uses Curse of Drowning or Ignis Domini.",
                ),
                S(
                    "The Last Sermon",
                    at=9,
                    clues="Before a packed congregation, on a great day such as St. "
                    "John's Mass (December 27), he begs the magi to submit, "
                    "and commands those he can name to burn their books, break "
                    "their staves and put aside magic. Most people believe a "
                    "magus needs his staff (Lords of Men p. 41). A written copy "
                    "goes to the covenant.",
                    ignored="He waits a week, then acts.",
                    stopped="See the resolutions in this story's secrets.",
                ),
                S(
                    "Excommunication",
                    at=10,
                    clues="At midnight in the cathedral, with all the clergy he can "
                    "muster, he excommunicates every wizard his evidence names. "
                    "All who knowingly keep company with them share the taint.",
                    ignored="Excommunication is a dreadful curse to the God-fearing. "
                    "Unless the covenfolk and turb are unusually loyal, or the "
                    "characters take great measures, the covenant empties.",
                    stopped="All effects end when a character is reconciled with "
                    "the Church. It is meant to heal, not to punish.",
                ),
                S(
                    "The Church Knights",
                    at=11,
                    clues="The knights enter the city in great pomp, cheered by "
                    "people who know why they have come. He hopes their name alone "
                    "will do, but knows he must be ready to shed blood. His "
                    "resolve is weakening, so he is readier to talk now, though "
                    "knights guard him by turns.",
                    ignored="They march on the covenant at once.",
                    turned="Spies in the city may give warning.",
                ),
                S(
                    "Against the Covenant",
                    at=12,
                    clues="The knights fight as veterans of siege warfare.",
                    ignored="They stockade a strong covenant and prepare an escalade, "
                    "while engineers undermine it. Mass warfare and sieges are in "
                    "Lords of Men pp. 109-116.",
                ),
            ],
        )
    )


def _campaign_secrets() -> list[Secret]:
    return [
        titled(
            "Orris will not rest",
            "Bishop Orris will not rest, and every step of his campaign is meant "
            "to drive the magi to submit (p. 62).",
        ),
        titled(
            "What the law says of magic",
            "Magic alone is neither a secular nor a canon crime in most of "
            "Mythic Europe; its methods or effects may be. Theft or murder by "
            "magic is a crime, and idolatry is for the canon court. Bonisagus "
            "purged overt idolatry, but theologians and holy magicians still "
            "find sacrilege in Hermetic words and gestures (RoP: The Divine "
            "Revised Edition pp. 66-69). The charge at the bishop's court is "
            "that the magic called on pagan beings, and it rests on hearsay (p. "
            "56). The bishop alone judges, over moral offenses, religious duties "
            "and all crimes of clergymen (p. 55).",
        ),
        titled(
            "What anathema brings",
            "Under anathema the baptismal name becomes a sympathetic "
            "connection. Demons take notice, and a death under it gives Hell "
            "the soul (p. 62). A non-Christian cannot be anathematized and "
            "suffers nothing. An excommunicant has no benefit of any sacrament "
            "but penance (p. 61).",
        ),
        titled(
            "Removing a bishop",
            "Usually only the pope can remove a bishop (The Church pp. 46-48), "
            "and legates test every such petition (pp. 63-64).",
        ),
        titled(
            "What Orris asks of the repentant",
            "Orris gladly meets magi he thinks repentant. He wants them in "
            "humble dress to confess before the congregation, break their "
            "staves, swear on the relics never to use magic, give up familiars, "
            "surrender their books to the Church and accept penance. Public "
            "confession is normal practice. If they do, he undoes all he has "
            "done. False oaths risk exposure and Divine anger, such as the "
            "Curse of Drowning and anathema. If they refuse, he has no more to "
            "say (p. 64).",
        ),
        titled(
            "The Order and those who submit",
            "A magus who dislikes the Church may charge magi who submit to "
            "Orris with endangering their sodales. Those who truly forswear "
            "magic may count as having left the Order, losing the Code's "
            "protection, and must be slain before they betray the Parma Magica "
            "(pp. 64-65).",
        ),
        titled(
            "Witnesses to Orris's curse",
            "Monks of Orris's novitiate, penitents who dabbled in magic, people "
            "he freed from possession, or the ghost of a witch convicted in his "
            "court show that he reacted alike to evil and to magic (p. 63).",
        ),
        titled(
            "Persuading Orris",
            "Early on Orris is strong and demands full contrition; later, "
            "complicit in excommunication and bloodshed, he wavers. Magi must "
            "convince him magic is not evil by scholarship, mysticism or "
            "theology, openly, for he is a good judge of character and deceit "
            "would be disastrous, and must correct his ignorance of the Order, "
            "which may strain their Oath (p. 65).",
        ),
        titled(
            "Orris's terms for peace",
            "If Orris accepts that magic is not evil (p. 65), he still requires "
            "confession and penance for known crimes; a church in the covenant, "
            "with Sunday Mass for all magi and a Friar Preacher as priest in "
            "charge; tithes; care for the diocese's mad and outcast, a possible "
            "source of grogs, companions or apprentices; and each magus's "
            "confession once a year. He does not demand that they give up "
            "magic. He will not bend for a year or so.",
        ),
        titled(
            "If Orris is killed",
            "Killing Orris brings the Code, the Church's inquiry and possibly a "
            "Tribunal conviction. The chapter asks the papacy for a successor "
            "who knows heresy and the Order, has political weight, and might "
            "even be a cardinal, with his own Divine Magic Resistance (p. 66).",
        ),
        titled("Storyguide Notes", _campaign_notes()),
    ]


def _campaign_notes() -> str:
    return paragraphs(
        "The bishop suits a covenant with ties to the mundane world; a socially "
        "isolated one feels him less. He shows the Order's problem: magi may "
        "not meddle with mundanes, but mundanes may meddle with them (p. 50). He "
        "can be a new appointment or an incumbent taking a larger part.",
        "The law (p. 55): a witness who hears and understands a casting may "
        "roll Intelligence + Artes Liberales to see pagan influences: Ease "
        "Factor 9, or 6 for a Ritual (p. 56).",
        "Anathema, at the storyguide's choice (p. 62): all Faith Points lost, "
        "and none gained while excommunicated without True Faith. One Confidence "
        "Point lost on hearing of it. A Local Reputation of Anathema 1. The "
        "Gift's penalty takes on the color of impiety. Those with Faith Points "
        "sense the danger to their souls.",
        "Ruining his name (pp. 63-64): hard, given a lifetime of good deeds, but "
        "possible with time. Magic can forge evidence. Give him a bad Reputation "
        "by a significant event and raise it as the friars raise theirs; once "
        "it passes his good one it takes precedence. To remove him, the chapter "
        "and the local witnesses must be falsified too. Using local nobles and "
        "churchmen invites a charge of meddling.",
        "Lifting the curse (p. 65; capitulation, hiding or all-out assault being "
        "the three main endings). While it lasts he cannot reach terms. A demon's "
        "curse ends with the demon, above all if he sees it; the demon or a "
        "minion checks on its work now and then, and can be tracked. A hedge or "
        "faerie curse likely has a condition to meet, and the one who laid it "
        "may want apology or reparation. A Divine curse ends when the characters "
        "have learned the lesson, perhaps through public penance. A non-Divine "
        "curse could yield to Perdo Vim, but he is hostile and bears relics. "
        "Against a Vim specialist, raise the curse's level and draw it from an "
        "unfamiliar tradition, so that learning it takes at least another story.",
        "A journey to lift the curse could be a pilgrimage (The Church pp. "
        "15-19) (p. 63).",
        "Full disclosure (p. 65): if he suffers The Gift, they cannot persuade "
        "him. Those present must have the Gentle Gift, be unGifted, or include "
        "him in a Parma Magica. Use the debate rules of Houses of Hermes: "
        "Societates p. 90, and no dirty tricks.",
        "Disappearance (pp. 65-66): they leave the diocese, or hide the covenant "
        "by powerful magic, with supplies from afar through layers of agents, "
        "and go out only in disguise. The bad Reputation fades by 1 experience "
        "point a year without suspicion, so it may take decades. Orris will "
        "likely be dead by then.",
        "Killing him (p. 66): Heaven should not leave the murder of a good man "
        "unpunished.",
    )


def _double(b: Builder, people: dict[str, Character]) -> None:
    turstan = b.magus(
        "Turstan",
        covenant=None,
        house="",
        type="companion",
        age=None,
        summary="A local scoundrel of the diocese, given to drink, dice, loose "
        "women and shady deals.",
        secrets=[
            titled(
                "The bishop's double",
                "Turstan is the bishop's near-identical double (p. 63). Orris "
                "has not worked out that he exists.",
            ),
            titled(
                "Turstan and the curse",
                "If confronted he claims to be a con man with a chance likeness, "
                "but he is bound up with the bishop's curse.",
            ),
            titled(
                "What Turstan knows",
                "He knows more about the bishop's curse than first appears (p. 63).",
            ),
            titled(
                "Storyguide Notes",
                "Turstan is Orris's Mistaken Identity Flaw (p. 63). What he is "
                "depends on who laid the curse: a diabolist taking the bishop's "
                "form to undo his works, the faerie tormentor dropping in to "
                "watch its victim, or an angel waiting to reveal the curse and "
                "set the characters on the road to removing it.",
            ),
        ],
    )
    double = dormant(
        b.threat(
            "Odd Tales of the Bishop",
            antagonist="Turstan",
            summary="Odd tales of the bishop reach the parishes: sightings that "
            "do not fit where he was.",
            secrets=[
                titled(
                    "Storyguide Notes",
                    "The book's way to feed the players' guess that Orris must "
                    "be crooked (p. 63). It is his Story Flaw coming into force "
                    "during this story.",
                ),
            ],
            stages=[
                S(
                    "A Scoundrel in the Bishop's Likeness",
                    at=1,
                    clues="Agents watching the bishop see him slip out of the "
                    "cathedral one evening in a townsman's clothes. It is "
                    "Turstan, off to the brothel with his pay from a false "
                    "blessing arranged by Archdeacon Geoffrey.",
                    ignored="Followed for a few days, he is seen drinking, "
                    "gambling, keeping loose company and dealing with rogues.",
                    stopped="The real bishop has perfect alibis: Mass before several "
                    "hundred townsfolk, a guild-master's wedding, alms for the poor.",
                    turned="Denouncing the bishop looks ludicrous and malicious "
                    "and worsens the characters' Reputations. Unmasking Turstan "
                    "leads toward the curse.",
                ),
            ],
        )
    )
    b.link(double, "characters", turstan, "The double")
    b.link(double, "characters", people["geoffrey"], "Runs the scam")
    b.link(double, "characters", people["orris"], "His double")


def _side_stories(b: Builder) -> None:
    for name, summary, secrets in (
        (
            "Burning Bridges",
            "Freemen across the diocese put sense before custom. One town "
            "commissions a bridge sooner than walk miles to the old one.",
            [
                titled(
                    "The demon builder",
                    "The town's new bridge draws a demon builder. The town "
                    "outwits it three times; shamed, it frames them for "
                    "diabolism and makes sure the characters see the evidence.",
                ),
                titled(
                    "Storyguide Notes",
                    "The demon comes under the Wise temper (p. 58); it may be "
                    "Architectus (RoP: The Infernal p. 66). If the covenant "
                    'tries to destroy this "evil" bridge, it only proves the '
                    "bishop right.",
                ),
            ],
        ),
        (
            "The Bewitched Cows",
            "Cows are bewitched and bread will not rise, and the covenant is blamed.",
            [
                titled(
                    "The faerie behind the bewitching",
                    "The faerie responsible for the bewitched cows gets no "
                    "vitality while the characters take the blame, and its "
                    "cravings change it into something more dangerous.",
                ),
                titled(
                    "Ending the bewitching",
                    "Faeries cannot starve, but defeating the faerie behind the "
                    "bewitched cows does not end the trouble: the cause of its "
                    "change must be dealt with.",
                ),
                titled(
                    "Storyguide Notes",
                    "Blame the Witch (p. 60). A cognizant faerie might accuse "
                    "the characters of molestation for stealing its vitality.",
                ),
            ],
        ),
        (
            "The Familiar on Trial",
            "A magus's predatory familiar is accused of eating valuable livestock "
            "and is summoned to the manor court for destroying the lord's "
            "property.",
            [
                titled(
                    "Men from the manor court",
                    "Men are sent to the covenant to make sure that the familiar "
                    "attends the manor court.",
                ),
                titled("Storyguide Notes", "Blame the Witch (p. 60)."),
            ],
        ),
        (
            "The Fallen Church",
            "A church in the diocese collapses, and the covenant is blamed.",
            [
                titled(
                    "What lay under the church",
                    "The fallen church stood on an ancient vis source.",
                ),
                titled(
                    "Who brought the church down",
                    "A rival covenant brought the church down, trading on the "
                    "magi's bad Reputation, and claims the vis.",
                ),
                titled("Storyguide Notes", "Blame the Witch (p. 60)."),
            ],
        ),
        (
            "Unwanted Attention",
            "A Quaesitor passing through hears what is being said of the magi and "
            "starts asking questions.",
            [
                titled(
                    "The Quaesitor's case",
                    "If the charges are specific, the talk of the magi may look "
                    "like a clear case of meddling with mundanes, and the "
                    "Quaesitor might find enough to bring a case at Tribunal.",
                ),
                titled(
                    "Storyguide Notes",
                    "Attracting Unwanted Attention (p. 60).",
                ),
            ],
        ),
    ):
        dormant(
            b.threat(
                name,
                antagonist="Bishop Orris's campaign",
                summary=summary,
                secrets=secrets,
            )
        )
