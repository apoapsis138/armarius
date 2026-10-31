"""A Demonically Inspired Cult (Ant pp. 95-107), in paraphrase.

Five demons with their printed blocks (Abaissier, Bufonia, Fabrico, the
Small Demons of Rot and Malicia), the template for possessed followers,
the flagellants as a faction with its two late halves, the rag
manufactory as a place, and the cult's rise as a dormant threat with one
stage for each of the book's. The book names no human member and prints
none, so the cult has no characters. Its items have no record of their
own without a covenant to hold them: they are listed in the faction's
secrets."""

from __future__ import annotations

from ...models import BodyVis
from ..builder import Builder, characteristics, dormant, paragraphs, vf_puissant

S = Builder.stage
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
INFERNAL = "Infernal"
TRACK = "A track"

COAGULATION = (
    "Builds a solid body out of the world's ambient, unformed matter; "
    "the Appearance says what it looks like."
)
ENVISIONING = (
    "For 1 point the demon enters and twists a dream; for 5 it makes a "
    "waking hallucination. One meant to terrify is ignored on a Brave "
    "roll of 9+, and failing brings on a violent bodily reaction such as "
    "a seizure."
)


def build(b: Builder) -> None:
    abaissier = _abaissier(b)
    bufonia = _bufonia(b)
    fabrico = _fabrico(b)
    rot = _small_demons(b)
    malicia = _malicia(b)
    possessed = _possessed(b)
    cult = _cult(b)
    for demon, note in (
        (abaissier, "Its true master"),
        (fabrico, "Claims part of it, then serves Abaissier against his will"),
        (bufonia, "Poisons wells beside it, for her own ends"),
        (malicia, "Lieutenant, recruited with a promise of prey"),
        (rot, "Sent to ruin grain"),
        (possessed, "Followers ridden by demons"),
    ):
        b.link(demon, "places", cult, note)
    threat = _threat(b)
    b.link(threat, "places", cult, "The movement this story follows")
    for demon in (abaissier, fabrico, bufonia, malicia):
        b.link(threat, "creatures", demon, "Behind the cult")


def _abaissier(b: Builder):
    return b.creature(
        "Abaissier",
        page="p. 96",
        realm=INFERNAL,
        might=35,
        form="Ignem",
        size=2,
        order="Lord of the Avengers of Evil",
        hierarchy=5,
        confidence=(1, 3),
        weakness=(
            "Protected group: people who whip themselves in a way the Church allows."
        ),
        block={
            "characteristics": characteristics(2, 0, 2, 3, 1, 3, 3, 4),
            "abilities": [
                ("Awareness", 4, "flagellants"),
                ("Civil and Canon Law", 4, "petty errors"),
                ("Philosophiae", 5, "making people feel guilty"),
                ("Single Weapon", 6, "whip"),
                ("Theology", 6, "threatening Scriptural quotations"),
            ],
            "traits": {"Relentless": 5, "Merciful": -3},
            "reputations": {
                "Angel of Punishment (Infernal)": 3,
                "Scourge of the Pious (Infernal)": 1,
            },
        },
        attacks=[b.attack("Flailing chain (five at a time)", 5, 12, 11, 9)],
        soak=5,
        fatigue_levels="OK, 0, -1, -1, -3, -3, -5, Unconscious",
        powers=[
            b.power("Coagulation", 3, -1, "Corpus", does=COAGULATION),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does=paragraphs(
                    ENVISIONING,
                    "Abaissier likes to show people some tiny failing, to feed "
                    "their Pride with the thought that a little flagellation "
                    "would make them perfect. These visions are resisted on a "
                    "Humble roll of 9+.",
                ),
            ),
            b.power(
                "Protective Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points. If it beats Magic Resistance while "
                "someone commits a sinful thought or deed, that person gains a "
                "temporary Self-loathing trait, and at the next chance rolls "
                "against a suitable trait to avoid harming or punishing "
                "himself. If the Obsession fails the trait goes; if it wins "
                "the trait is permanent. A person under it has a Light Wound "
                "modifier of +1, stacking for no more than three wounds (+3).",
            ),
            b.power(
                "Punish the Sinner",
                5,
                3,
                "Corpus",
                does="Delivered by touch, and usable with a blow of the flail. "
                "If it penetrates, an unexpiated mortal sin causes a Heavy "
                "wound and a venial sin a Light wound. Someone with no obvious "
                "sin takes damage equal to the sum of his negative Personality "
                "Traits.",
            ),
        ],
        vis=[BodyVis(7, "Perdo", "one in each whip")],
        appearance=(
            "An angel whose body is chain on fire, coloured like old blood and "
            "brass. Its pale robe, alone among its kind, shows a stain like "
            "blood when it is hurt. It has no right hand, only five slender "
            "chains with weights at their tips, which run out to a startling "
            "length in a fight and strike each for itself."
        ),
        notes=paragraphs(
            "Wound Penalties as printed: +1* (1-7), -3 (8-14), -5 (15-22), "
            "Incapacitated (23-30), Dead (31+). *Light wounds make him more "
            "dangerous: he may hurt himself each round for the bonus, which "
            "cannot pass +5.",
            "Cost of Envisioning: 1 or 5 points. Cost of Protective "
            "Obsession: 1 to 3 points.",
            "The block calls his order the Avengers of Evil; his text calls "
            "him a Lord of the Angels of Punishment. Vis: the book gives 7 "
            "pawns, one in each whip, and five chains.",
        ),
        secrets=paragraphs(
            "A demon of Pride who turns the very pious from God: suffer more, "
            "he says, and you are more beloved of Him. It is false, and the "
            "more people have given up, the harder it is to admit it. He "
            "tempts single believers and seduces charismatic men who then "
            "lead small heretical groups, and he makes sinners harm themselves "
            "and think they have atoned. As a Lord he commands many lesser "
            "demons.",
            "He brings several cells into the open at once so they are hard "
            "to stamp out, then forces the weaker Fabrico into servitude. When "
            "the Church or the magi move, he stays out of sight and will "
            "sacrifice Fabrico if it shows him who his enemies are and how "
            "they work. He signs his work: the red mark on the flagellants' "
            "robes is a cult symbol he has used before.",
            "His Pride is his weakness. He underestimates the player "
            "characters and can be goaded into a fight; evidence able to "
            "destroy the cult's remains may bring him to attack in person.",
        ),
    )


def _bufonia(b: Builder):
    return b.creature(
        "Bufonia",
        page="p. 97",
        realm=INFERNAL,
        might=20,
        form="Animal",
        size=0,
        order="Likely a Vessel of Iniquity",
        hierarchy=1,
        confidence=(1, 3),
        weakness="Protected group: people who never drink well-water.",
        block={
            "characteristics": characteristics(1, 0, 2, 0, 1, 1, 3, 1),
            "abilities": [
                ("Awareness", 4, "the Divine"),
                ("Guile", 6, "frightened people"),
                ("Medicine", 6, "contaminants"),
                ("Thrown Weapon", 6, "vial of poison"),
                ("Teaching", 6, 'to make "cures"'),
            ],
            "traits": {"Depraved": 6, "Hateful": 6, "Loathes greengrocers": 3},
            "reputations": {"Poisoner of Wells (Infernal)": 1},
        },
        attacks=[b.attack("Thrown vial", 0, 7, 0, 0)],
        soak=1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power("Envisioning", 1, 0, "Mentem", does=ENVISIONING),
            b.power(
                "Form of Wickedness",
                2,
                0,
                "Mentem",
                does="Makes a solid form of pure sin, held for one round before "
                "she must take spiritual or human form. Those near her without "
                "enough Magic Resistance start to suspect their neighbours of "
                "poisoning them. Each hour they make a Stamina stress roll of "
                "6+: failing costs a Fatigue level, success breaks the hold, "
                "and falling unconscious ends it. A botch brings temporary "
                "insanity and a Minor Personality Flaw suited to the sin.",
            ),
            b.power(
                "Form of The Proud Man",
                0,
                0,
                "Corpus",
                does="Once she has taken corporeal form by Form of Wickedness, "
                "she can take her solid form; the Appearance describes it.",
            ),
            b.power(
                "Possession",
                0,
                2,
                "Mentem",
                does="Variable points. After overcoming Magic Resistance she "
                "stores some Might in a temporary pool in the victim, and the "
                "possession ends when it is spent. The two parts of her can "
                "speak only in sight of each other. She drives the host, but "
                "something the victim finds abhorrent costs Might: a stress "
                "die plus the Might spent against his Personality trait roll. "
                "A Supernatural ability costs 1 Might, or as many as a "
                "possessed creature spends on one of its powers.",
            ),
            b.power(
                "Contagious Obsession",
                1,
                0,
                "Mentem",
                does="1 point a victim. If it beats Magic Resistance while "
                "someone commits a sinful thought or deed, he gains a temporary "
                "Hates (group) trait and at the next chance rolls against a "
                "suitable trait to avoid trying to harm the scapegoats. If it "
                "fails the trait goes; if it wins the trait is permanent. Each "
                "victim carries it and can pass it, by the same rolls, to "
                "anyone he abuses; every new victim costs her 1 Might. It stops "
                "spreading when the carrier runs out of Might or a day passes "
                "with nobody infected, though those afflicted stay so.",
            ),
        ],
        vis=[BodyVis(4, "Perdo", "long nose")],
        appearance=(
            "By nature a shapeless darkness, sin given sight. In solid form "
            "she passes for a tall lady of good breeding, and often goes in "
            "the dress of a plague doctor."
        ),
        notes=paragraphs(
            "Thrown vial: touching the undiluted contents is poisoning of Ease "
            "Factor 9, doing heavy damage (ArM5 p. 180; Definitive Edition "
            "p. 406).",
            "Soak: +1 in human form, entered here; the book also prints Toad "
            "form +3, though no power or appearance gives her a toad form.",
            "Wound Penalties as printed: -1 (1-5), -3 (6-10), -5 (11-15), "
            "Incapacitated (16-20), Dead (21+).",
            "Her vis lies in a long nose, which neither of her printed shapes "
            "mentions.",
            "The plague (p. 100). With the disease rules of Art & Academe pp. "
            "47-50: Severity 13, Stable 9, Improve 12, interval a week, "
            "causing a Heavy Wound. Otherwise use ArM5 p. 180 and treat it as "
            "a poison of Ease Factor 12 causing a Major Wound. The symptoms are "
            "thirst and burning in the fingertips, nose and toes, then "
            "bleeding from the eyes and ears.",
            "The plague need not be the Black Death. The book suggests "
            "something the players think of as mild, such as measles or "
            "scarlet fever, or symptoms they cannot name.",
        ),
        secrets=paragraphs(
            "She teaches people to poison wells, and never does it herself, "
            "so that a scapegoat takes the hatred: Jews, lepers, pagans, "
            "Muslims, sorcerers and, her own passion, greengrocers. In human "
            "form she tells some dupes their brews protect against plague. "
            "They drink it strong to save themselves and soon die, and she so "
            "enjoys telling them whom they have killed that she keeps a few "
            "such victims when willing helpers would do more harm.",
            "For this plague each potion needs a human heart, best from a "
            "plague death. Neither ally nor servant of Abaissier, she thinks "
            "Fabrico rules the flagellants and does not fear him. Once the "
            "processions begin she recruits poisoners in towns near them to "
            "destroy whichever outsiders come easiest, magi included, and if "
            "strong opposition appears she wants Fabrico blamed. Their evils "
            "fit so well they seem to be working together.",
            "She can brew many diseases and may change them to avoid being "
            "caught, but must not show more range than Fabrico could (p. 100).",
        ),
    )


def _fabrico(b: Builder):
    return b.creature(
        "Fabrico",
        page="p. 98",
        realm=INFERNAL,
        might=20,
        form="Corpus",
        size=0,
        order="Deluder",
        hierarchy=1,
        confidence=(1, 3),
        weakness="Fascinated by valuable mundane objects.",
        block={
            "characteristics": characteristics(1, 1, -1, 3, 3, 1, 4, 2),
            "virtues_flaws": [vf_puissant("Guile")],
            "abilities": [
                ("Awareness", 4, "the Divine"),
                ("Guile", 6, "Divine"),
                ("Brawl", 6, "claws"),
                ("Theology", 6, "miracles"),
            ],
            "traits": {"Credible": 3, "Sly": 2},
            "reputations": {
                "Creator of relics (Infernal)": 1,
                "Deluder (Infernal)": 1,
            },
        },
        attacks=[b.attack("Claw-like fingernails (two)", 2, 7, 10, 5)],
        soak=1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power("Coagulation", 3, -1, "Corpus", does=COAGULATION),
            b.power(
                "Delusion",
                1,
                3,
                "Imaginem",
                does="Vivid illusions: 1 point for a single object, 5 for one "
                "the size of a room. Each has some subtle fault. He uses them "
                "to fake miraculous messages.",
            ),
            b.power(
                "Duplicate the Magi's Creation or Transmutation",
                0,
                1,
                "Variable",
                does="Variable cost and Form. Does any non-ritual Creo or Muto "
                "Hermetic spell of level 20 or lower; he uses it with props to "
                "make false relics.",
            ),
            b.power(
                "Envisioning",
                1,
                0,
                "Mentem",
                does=paragraphs(
                    ENVISIONING,
                    "Fabrico often uses waking dreams to counterfeit visions, "
                    "resisted with a suitable Personality Trait roll of 9+.",
                ),
            ),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points. If it beats Magic Resistance while "
                "someone commits a sinful thought or deed, he gains a temporary "
                "Gullible trait, and at the next chance rolls against a "
                "suitable trait to avoid believing something dangerous or "
                "stupid. If it fails the trait goes; if it wins the trait is "
                "permanent.",
            ),
        ],
        vis=[BodyVis(4, "Perdo", "eyes")],
        appearance=(
            "Like any deluder, by nature he is a dark tear in things, crowded "
            "with eyes, teeth and innards. For this story he goes as a "
            "flagellant bound up in bandages."
        ),
        notes=paragraphs(
            "Guile is printed 6+2, the +2 being his Puissant Guile.",
            "Wound Penalties as printed: -1 (1-5), -3 (6-10), -5 (11-15), "
            "Incapacitated (16-20), Dead (21+).",
            "Cost of Delusion and Envisioning: 1 or 5 points. Cost of "
            "Obsession: 1 to 3 points.",
        ),
        secrets=paragraphs(
            "He enjoys passing off his work as the Divine: he makes ordinary "
            "objects, wraps them in fake miracles until they are hailed as "
            "relics, and backs whoever teaches the resulting errors. His "
            "little cults believe a saint has chosen them, and that regular "
            "signs let them know God's will better than the Church. The "
            "Church usually puts them down.",
            "In this story he first spreads prophets of the Antichrist and "
            "the world's end, then notices the flagellants and claims part of "
            "them. Beaten, he serves Abaissier against his will and knows his "
            "master would spend him as a decoy, so the player characters may "
            "set him on Abaissier and weaken both. Destroying him does not "
            "end the cult, but it costs it the public's love and drives it "
            "back, over time, to secret cells.",
        ),
    )


def _small_demons(b: Builder):
    return b.creature(
        "Small Demons of Rot",
        page="p. 100",
        realm=INFERNAL,
        might=5,
        form="Herbam",
        size=-4,
        how_many="In groups",
        order="Vessel of Iniquity",
        confidence=(1, 3),
        weakness=(
            "They cannot harm, and are burned by touching, the Host or wheat "
            "meant to become the Host."
        ),
        block={
            "characteristics": characteristics(0, 1, 0, 0, -8, 0, 0, 6),
            "abilities": [("Awareness", 4, "foes"), ("Brawl", 6, "feet")],
            "traits": {"Depraved": 6, "Enthusiastic": 6},
            "reputations": {
                "Bringers of Famine (Infernal)": 1,
                "Vessel of Iniquity (Infernal)": 1,
            },
        },
        attacks=[b.attack("Sharp claws (two)", 6, 6, 12, -8)],
        soak=2,
        fatigue_levels=FATIGUE,
        powers=[b.power("Coagulation", 3, -1, "Corpus", does=COAGULATION)],
        vis=[BodyVis(1, "Perdo", "tongue")],
        appearance=(
            "Little rat-like humanoids that turn up wherever grain is stored "
            "and foul it with the pus from their claws."
        ),
        notes=paragraphs(
            "Foes for grogs and companions. Too weak to do much with one "
            "blow, they attack in groups; a large group may grapple or blind "
            "an opponent while the others try called shots.",
            "Claws: a putrid ichor causes fever and sepsis in a scratch (a "
            "disease of Ease Factor 6 causing a minor wound, ArM5 p. 180) and "
            "makes plant products moulder and rot.",
            "Wound Penalties as printed: -1 (1), -3 (2), -5 (3), "
            "Incapacitated (4), Dead (5+).",
        ),
        secrets="Abaissier orders them to rot seed corn, to break communities "
        "with famine before his preachers arrive.",
    )


def _malicia(b: Builder):
    return b.creature(
        "Malicia",
        page="p. 101",
        realm=INFERNAL,
        might=15,
        form="Corpus",
        size=0,
        order="Fury",
        hierarchy=1,
        confidence=(1, 3),
        weakness="Protected group: children.",
        block={
            "characteristics": characteristics(2, 2, -2, 0, 3, 0, 3, 2),
            "virtues_flaws": ["Berserk"],
            "abilities": [
                ("Awareness", 4, "the weak"),
                ("Brawl", 5, "bite"),
                ("Guile", 6, "the weak"),
            ],
            "traits": {"Wrathful": 4, "Angry": 2, "Self-controlled": -6},
            "reputations": {
                "Eater of the self-destructive (Infernal)": 1,
                "Fury (Infernal)": 1,
            },
        },
        attacks=[b.attack("Bite", 2, 12, 9, 4), b.attack("Hands", 2, 8, 7, 3)],
        soak=1,
        fatigue_levels=FATIGUE,
        powers=[
            b.power("Coagulation", 3, -1, "Corpus", does=COAGULATION),
            b.power(
                "Obsession",
                1,
                -5,
                "Vim",
                does="Costs 1 to 3 points. If it beats Magic Resistance while "
                "someone commits a sinful thought or deed, he gains a temporary "
                "Self-Harming trait, and at the next chance rolls against a "
                "suitable trait to avoid hurting himself. If it fails the trait "
                "goes; if it wins the trait is permanent.",
            ),
            b.power("Envisioning", 1, 0, "Mentem", does=ENVISIONING),
            b.power(
                "Endurance of the Enraged",
                0,
                0,
                "Corpus",
                does="She takes no Wound penalties, except on Defense totals.",
            ),
            b.power(
                "Waxing of the Humors",
                3,
                2,
                "Mentem",
                does="Passion drowns sense: the victim needs a Personality "
                "trait stress roll of 9+ to hold the emotion in check. Often "
                "used straight after a successful Obsession.",
            ),
        ],
        vis=[BodyVis(3, "Perdo", "serpent head")],
        appearance=(
            "A young woman out of whose breast a snake grows. It worries at "
            "her everywhere but the face, leaving small bleeding bites, some "
            "of them bruised dark by poison and decay."
        ),
        notes=paragraphs(
            "Berserk: +2 Attack on both lines; Soak +3 in place of +1. The "
            "bite is venomous, as an asp's (ArM5 p. 180; Definitive Edition "
            "p. 406: Ease Factor 9, Incapacitating).",
            "Wound Penalties as printed: -1 (1-5), -3 (6-10), -5 (11-15), "
            "Incapacitated (15-20), Dead (21+). The book's 15 falls in two "
            "ranges; the usual table starts Incapacitated at 16.",
            "Cost of Envisioning: 1 or 5 points. Cost of Obsession: 1 to 3 points.",
        ),
        secrets=paragraphs(
            "A Fury, feeding on the anger that destroys the one who feels it, "
            "drawn to the cult by a promise of plenty of prey. Flagellants she "
            "takes whip the onlookers and may kill themselves by mistake; "
            "leaders she takes may counsel suicide.",
            "She is the lieutenant to set before the player characters so the "
            "saga does not close too early in a fight with the main demons. "
            "Destroying her slows the cult and weakens it locally, though it "
            "still reaches the next stage. If Abaissier falls she tries to "
            "seize part of his cult and turn its despair under the crackdown "
            "into mass suicide.",
        ),
    )


def _possessed(b: Builder):
    return b.creature(
        "Possessed Follower",
        page="p. 102",
        realm=INFERNAL,
        might=10,
        how_many="As the story needs",
        block={"virtues_flaws": ["Berserk"]},
        notes=(
            "A template, not a person: take any suitable grog or companion, "
            "give them Infernal Might 10 and the Berserk Virtue, and add +3 to "
            "their Soak and +3 to their damage. The book prints no Form for "
            "the Might."
        ),
        secrets=(
            "These attack the counter-processions, and defend the rag "
            "manufactory, where bodiless demons help the acolytes fight and "
            "work their corpses after death. Some guard the false saints."
        ),
    )


def _cult(b: Builder):
    cult = b.faction(
        "The Flagellants",
        summary=paragraphs(
            "A penitential movement spreading from town to town, led by "
            "eloquent lay preachers. Its people pray, fast and call the "
            "world to repentance. Later they march in great processions "
            "behind banners that denounce human weakness, carrying whips and "
            "birch scourges, and in undyed robes with a red mark on the "
            "breast.",
            "Its followers believe that their suffering is saving the world, "
            "and gladly say so to anyone who will listen. The sickness of "
            "recent years has passed them by.",
        ),
        decides="Its leader",
        wants="To expiate the sins of the world and end God's punishments.",
        rules=(
            "They call and answer in songs as they whip themselves, and at "
            "the name of Christ fling themselves to the ground."
        ),
        secrets=paragraphs(
            "Each cell's preacher thinks an angel chose him alone; the angel "
            "is Abaissier, an Angel of Punishment. Cells do not talk to each "
            "other, which is the cult's weakness, since Redcaps do. Questioned "
            "gently in many places and with the answers pooled, its members "
            "reveal its shape without ever noticing. A leader flattered in "
            "his spiritual Pride describes his visitor well enough for an "
            "expert in Infernal Lore to name the kind of demon.",
            "Money and goods: at first members' own goods and alms; later "
            "extortion from towns and gifts from hidden patrons. Stocks were "
            "laid up for years, a sin in itself, and the processional crosses "
            "come from distant artisans, a first hint that the plot spans "
            "Europe. Unused caches can be destroyed. Tracing the goods names "
            "the nobles and churchmen who secretly support it; they will put "
            "themselves at the front of the crackdown and sabotage it.",
            "Items. Uniforms: robes of wool or cotton given as alms by a "
            "nobleman in penance for a terrible crime, told to by an 'angel'; "
            "tracing them finds many local gathering points. False relics: "
            "Fabrico's, some breathing out the evil airs of plague, with an "
            "antidote for the flagellants. Blood-soaked rags: see the Open "
            "Heresy stage. Bufonia's 'holy oil', sprinkled on the rags. The "
            "Letter From an Angel: a false relic read out before a procession, "
            "which eases its way past obstacles and whose symbols Fabrico "
            "marks on things to order them destroyed, held or venerated.",
            "Truly pious flagellants exist, monks and even saints among them. "
            "Moderate, voluntary flagellation or one set by a bishop is "
            "allowed when treated as punishment or as a way to fix the "
            "attention, not as earning merit; penance in place of atonement "
            "is not. Abaissier tries to trick his enemies into attacking "
            "such people. Those spared can dispute with the leaders and "
            "bring followers back to the Church.",
        ),
    )
    b.faction(
        "The False Saints",
        summary=(
            "Flagellant leaders hailed as men returned from the dead, who "
            "ordain their own priests outside the Church. Some shelter with "
            "noblemen already on poor terms with the bishops."
        ),
        decides="Its leader",
        secrets=paragraphs(
            "Their deaths and returns are elaborate waking dreams worked by "
            "Abaissier and Fabrico, given to one leader in each region so "
            "that each thinks himself uniquely blessed. Once false priests "
            "are ordained the Church turns on these groups, with arms if "
            "needed.",
            "Finding one means learning where he hides and passing his "
            "guards: noblemen, possessed followers, or animals tainted by "
            "demons without his knowing. A pious character can win one over "
            "on a contested roll of stress die + Communication + Theology "
            "against his Pride, beating him by at least 6; showing him that "
            "demonic animals guard him adds 6. The penitent may enter a "
            "monastery or nunnery, though some bishops will want him dead, or "
            "find work with the Order.",
        ),
    )
    b.faction(
        "The Loyal Flagellants",
        summary=(
            "Flagellant groups that denounce the false saints and keep the "
            "support of part of the Church. Some nobles follow them and make "
            "war on those who shelter the saints, and parts of the Order "
            "favour them."
        ),
        decides="Its leader",
        secrets=paragraphs(
            "Their opposition is a strategic pose that survives the purge and "
            "lets Abaissier go on training heretics for some years.",
            "Ways to prove it. Bring Church witnesses to one of the secret "
            "meetings between senior members of the two halves. Capture one "
            "of the very few 'loyal' men the demons have told are saints: put "
            "to the question, he is too Proud to keep up the lie. Help the "
            "nobleman who has had a false angel and also a true vision of the "
            "Archangel Michael: he attacks lords of the 'loyal' side while "
            "rivals in disguise muster with the false saints, and if he wins "
            "he can take them, or their bodies, to the Church as proof.",
        ),
    )
    b.place(
        "The Abandoned Building",
        realm="",
        summary="An abandoned building in the district.",
        secrets=paragraphs(
            "The manufactory of bloodied rags. Flagellants take turns whipping themselves here, sitting on a "
            "floor spread with filthy bed sheets. Each evening an acolyte "
            "cuts the sheets into palm-sized pieces, which are carried off, "
            "sprinkled with 'holy oil' and smuggled to supporters in nearby "
            "towns.",
            "If it is attacked, bodiless demons possess the acolytes, help "
            "them fight and move their bodies after death. The book sets it "
            "in the covenant's local area, and prints no aura.",
        ),
    )
    return cult


def _threat(b: Builder):
    return dormant(
        b.threat(
            "The Rise of the Flagellants",
            antagonist="The flagellant preachers",
            moves=TRACK,
            summary=(
                "Lay preachers of unusual eloquence are appearing across the "
                "region, and prophets are foretelling the Antichrist and the "
                "end of the world."
            ),
            secrets=paragraphs(
                "Three demons who usually work alone happen to be active in "
                "one region. Demons cannot truly be patient or share, so this "
                "is no plan: each sets its minions going, and the humans, who "
                "can scheme, find their own mischief. Left alone the cult "
                "kills thousands, ruins the region's economy and leaves "
                "Infernal auras behind. A storyguide need not use every "
                "stage, but should plant the motifs of any skipped.",
                "Why magi must care. The Church or the Divine will end the "
                "heresy, but not gently: preachers first, then armies, and an "
                "invasion is an invasion to a covenant's farmers and "
                "merchants. Crusaders also strike at Jews, Muslims, pagans and "
                "problem people with fortresses, and a younger son who takes a "
                "heretic's castle may keep it, so beaten raids do not deter "
                "them. Infernal auras left behind seed later trouble.",
                "Any stage. Abaissier may trick the characters into attacking "
                "the truly pious. His movement also wrecks other demons' "
                "plots, so a storyguide who wants it harder may have him "
                "suborn them as fractious lieutenants. Rival bands fall out, "
                "and helping one side yields the other's secrets, which are "
                "much the same.",
                "Research. Infernal Lore can find earlier flagellant heretics, "
                "but naming a demon from the Order's usual sources is very "
                "hard. Specialists can spot Abaissier and foresee the early "
                "stages, until he and Fabrico join and the precedent breaks; "
                "the uniforms then make him easy to identify.",
                "Ending it. Goad Abaissier into battle, or draw out Fabrico. "
                "Dispute with the charismatic dupes: if they are humbled and "
                "reconciled the cult crumbles. Relieve the famine and disease "
                "that feed it, and prove the prophecies false. A big enough "
                "lie may do it, a false miracle saying God is satisfied and "
                "sending people back to the Church. Comedy works too: one "
                "historical revival died when the laity of Rome laughed at "
                "its marchers.",
            ),
            stages=[
                S(
                    "Cells of Flagellants",
                    at=1,
                    clues=(
                        "A man known for his eloquence turns lay preacher; "
                        "Abaissier seduces at least six such. Fabrico's "
                        "separate prophets of the end make people ready to "
                        "listen. The first meeting is one cult member in a "
                        "story about something else."
                    ),
                    ignored=(
                        "Seed: a senior bandit says an angel told him to leave "
                        "sinners, helps the characters ambush his old band, "
                        "and goes off to preach; he may return as a flagellant."
                    ),
                    turned=(
                        "Seed: Abaissier destroys a cell whose leader "
                        "proselytizes too soon, to keep the Church's eyes off. "
                        "Assailed by Hell, the cell looks holy, and survivors "
                        "given positions of trust are later contacted as his "
                        "agents."
                    ),
                ),
                S(
                    "Shock to the Community",
                    at=2,
                    clues=(
                        "Crops fail, whether naturally or by raiders, small "
                        "demons rotting seed corn and arsonists. Bufonia's "
                        "minions pour poison in city wells, and plague comes. "
                        "Mortal puppets spread leaders' venal sins and forged "
                        "crimes. Public flagellants, untouched by the plague, "
                        "appear across a wider area, asking only prayer and "
                        "fasting; some gatherings raise brief Dominion auras."
                    ),
                    ignored=(
                        "Communities lose heart and blame God's displeasure. "
                        "Characters may exploit the rumours against rivals."
                    ),
                    stopped=(
                        "Seeds: magi feed nearby towns by magic or wealth and "
                        "hunt the local causes of harm, though few will link "
                        "them to Abaissier yet. Stopping the well-poisoners "
                        "lets the plague burn out; smeared potentates may "
                        "want rumours traced or need mediating. Destroying "
                        "Malicia here slows the cult."
                    ),
                ),
                S(
                    "Processions Begin",
                    at=3,
                    clues=(
                        "Pilgrims march with whips and scourges still unused, "
                        "under banners of threat on God's behalf. Fights break "
                        "out at the edges."
                    ),
                    ignored="Unopposed, the processions gain popularity.",
                    stopped=(
                        "Opposed, the marchers grow furious and think worldly "
                        "powers corrupt. Local priests answer with processions "
                        "for local saints."
                    ),
                    turned=(
                        "Seed: Infernal disruptions hit the counter-processions, "
                        "with possessed attackers, loose herds, impassable "
                        "roads and fires. Those who protect them earn a good "
                        "Reputation with the priests likeliest to lead the "
                        "fight."
                    ),
                ),
                S(
                    "Spread of the Cult",
                    at=4,
                    clues=(
                        "Waking dreams, visitations, bards and pilgrims carry "
                        "the ideas, and Redcaps, alarmed at how many places "
                        "they start from, tell friendly covenants. Rival bands "
                        "fight in the streets. Seers report a battle of "
                        "powers. Flagellants near the covenant take up "
                        "uniforms."
                    ),
                    ignored=(
                        "Fabrico claims part of the movement and the two "
                        "demons fight until one makes the other a vassal; the "
                        "book expects Abaissier to win."
                    ),
                    stopped=(
                        "Seed: assassination, prison, disputation, smears or "
                        "cutting off resources reduce local leaders. So can "
                        "passing their names to moderate churchmen, who hold "
                        "them apart from their followers, or to nobles they "
                        "have mocked."
                    ),
                ),
                S(
                    "Larger Processions",
                    at=5,
                    clues=(
                        "Marches last 33.5 days, a day for each year of "
                        "Christ's life, and reach a thousand of both sexes and "
                        "all ages. False miracles are talked of. Flagellant "
                        "songs appear, and marchers grow proud of their filthy "
                        "robes and skip Sunday services."
                    ),
                    ignored=(
                        "Superabundant suffering: some think their whipping "
                        "excuses other crimes. Seed: a noble seizes a widow "
                        "and her lands by rape and forced marriage, his guards "
                        "using peasants as shields and digging up babies' "
                        "corpses to spread terror. Intervening wins the widow "
                        "as an ally. Other flagellant nobles, first to "
                        "question the Church, may suit covenants on bad terms "
                        "with it."
                    ),
                    stopped=(
                        "Seed: funnier ballads (stress die + Communication + "
                        "a suitable Ability, 15+) outrun the songs, or bards "
                        "are paid, jailed or killed. Magic items that remove "
                        "songs from memory help; Quaesitores and Redcaps hold "
                        "a few, and Quaesitores need more convincing to lend."
                    ),
                ),
                S(
                    "Inadvertent Sins",
                    at=6,
                    clues=(
                        "Sickness follows long pilgrimages, late enough for "
                        "the flagellants to claim they held it off. Some of "
                        "the Church still backs them; most know something is "
                        "wrong. Counter-processions grow and are sabotaged, "
                        "and flagellants think whipping pays for that too."
                    ),
                    ignored=(
                        "Fabrico's relics carry plague down the roads. In the "
                        "nearest city a pro-flagellant faction plans to open "
                        "the gates, riot and overthrow its rulers; if shut "
                        "out, Bufonia's students poison the wells to discredit "
                        "the rulers. Elsewhere the pious, aided by saints, "
                        "resist, in riots, battles or de facto sieges."
                    ),
                    stopped=(
                        "Seed: spreading word that the processions herald "
                        "plague makes towns shut their gates. Characters can "
                        "infiltrate the fifth column, catch the poisoners, "
                        "purify wells or find other water, and find a cure "
                        "for Fabrico's vapours or Bufonia's toxin. Dupes may "
                        "drop concoctions or false relics in water to protect "
                        "their town."
                    ),
                ),
                S(
                    "Open Heresy",
                    at=7,
                    clues=(
                        "Knowing God will end the cult, Abaissier pushes it "
                        "to do all the harm it can and gives Fabrico free "
                        "rein. Flagellation is held to replace the sacraments, "
                        "and to pass its virtue to others, so the rich buy "
                        "forgiveness, which is simony. Leaders work miracles, "
                        "only outside towns, since the Dominion there is too "
                        "strong. Rags and a Letter From an Angel appear. Some "
                        "leaders 'die and rise'."
                    ),
                    ignored=(
                        "A woman, most often, who makes a rag herself and "
                        "wipes the blood in her eyes thinks she has holy "
                        "sight. It opens a hole in her defences: demons use "
                        "Evocation on her, resisted by a Personality roll of "
                        "9+. Rags may carry plague, and Bufonia has them "
                        "dropped in wells and granaries. False saints begin "
                        "ordaining, and all Church support for them ends."
                    ),
                    stopped=(
                        "Seeds: a merchant burns rivals' shops and keeps three "
                        "flagellants in a woodland cottage to forgive him; "
                        "their families gossip. Another puts ergot and chalk "
                        "in bread, and criminals know him as a bulk buyer. "
                        "Grogs patrol for rags and neighbourhood watches drive "
                        "off spreaders. The manufactory can be found and "
                        "destroyed. Fewer leaders means each works miracles "
                        "more often, and demons cannot be everywhere, so "
                        "strike several false prophets at once; a big alliance "
                        "will probably be noticed by a minor demon. A cult "
                        "shattered here makes the region a centre of "
                        "resistance, a crusaders' staging area spared invasion, "
                        "and the covenant's influence can shield a few others."
                    ),
                    turned=(
                        "Seed: with an original letter and its materials, "
                        "forgers (Intelligence + Finesse or Dexterity + Craft, "
                        "9+) can send a group anywhere, since not even a "
                        "visited leader can overrule God's own letter. He "
                        "obeys more zealously if the tone stokes his Pride. "
                        "Fabrico will notice, and may hide it from Abaissier "
                        "if the magi seem useful against him."
                    ),
                ),
                S(
                    "Flagellant Civil War",
                    at=8,
                    clues=(
                        "Some groups oppose the false saints and keep Church "
                        "backing. Nobles take sides, some on each, and parts "
                        "of the Order support the 'loyal' flagellants. "
                        "Crusaders march on the false saints."
                    ),
                    ignored=(
                        "The purge spares the loyal half, and Abaissier goes "
                        "on training heretics for years."
                    ),
                    stopped=(
                        "Killing or detaining a false saint shifts the "
                        "Church's attention elsewhere. Proving the split a "
                        "pose destroys the rest of the cult, and may bring "
                        "Abaissier down on those who prove it."
                    ),
                ),
                S(
                    "Resurrecting the Cult",
                    at=9,
                    clues=(
                        "Remnants of broken cells are told they passed God's "
                        "test, and new secret societies form from them, "
                        "together or apart."
                    ),
                    ignored=(
                        "The cycle begins again, and the demons may feud "
                        "anew when Abaissier finds Fabrico's cults."
                    ),
                    stopped=(
                        "Handled personally, the cells give leads to confront "
                        "the demons. Reported, the Church destroys them and "
                        "ties with it grow. The demons may then treat the "
                        "characters as enemies, avoid them, or both."
                    ),
                ),
            ],
        )
    )
