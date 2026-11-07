"""The Waimie (Antagonists pp. 7 and 133-144), in paraphrase.

The Waimie and each of the ten ages of her brood are creatures, one record
per printed block: the book says what changes with age, and everything a
block leaves out (Season, Confidence, Mundane Qualities, traits, Reputation)
is her own, so it is entered as hers (p. 133). Each brood power keeps the
figures printed in her block. The father of the brood and the rebellious
daughter are creatures with no figures, as printed.

Her caves are a place with its regio; the insula, the Serpent Map, the four
sample exits, the marjoram grove and the milk pasture are places. The Cult of
the Serpent, a variation the book offers, is a faction with its leader as a
sketch. The story is one dormant threat with the book's stages, and each story
seed is a dormant threat of its own. The rumours people tell are in her notes;
the tellers and the figures in the tales are words only, for none of it is
true (p. 138). The book sets her nowhere: the lair goes where the saga needs."""

from __future__ import annotations

from math import ceil
from typing import Any, NamedTuple

from ...models import BodyVis, Creature, CreaturePower, Neighbour
from ..builder import (
    Builder,
    Secrets,
    characteristics,
    dormant,
    paragraphs,
    titled,
    vf_minor,
    wound_ranges,
)

LOCAL = "Locally"
FATIGUE = "OK, 0, -1, -3, -5, Unconscious"
#: From eight years old the bulk costs a Fatigue level (p. 144).
FATIGUE_REDUCED = "OK, -1, -3, -5, Unconscious"
ELDERS = "Just a handful in the caves, with a few gone to the insula"

GIFT = ("Greater Power", {"power": "The Envenomed Gift"})
TWO_HEADS = ("Greater Power", {"power": "Two Heads Are Better Than One"})
SCION = ("Personal Power", {"power": "Scion of the World Serpent"})
ATTACK = ("Improved Attack", {"weapon": "fangs"})
DEFENSE = ("Improved Defense", {"weapon": "fangs"})
MUST_BITE = ("Restricted Power", {"power": "must bite to use The Envenomed Gift"})
QUICK = vf_minor("Great Quickness")
BETTER = vf_minor("Improved Characteristics")
SENSE = vf_minor("Magic Sensitivity")
TOUGH = vf_minor("Tough")
TONGUE = ("Minor Flaw", {"flaw": "Afflicted Tongue"})
CLUMSY = ("Minor Flaw", {"flaw": "Clumsy"})
EYESIGHT = ("Minor Flaw", {"flaw": "Poor Eyesight"})

#: Hers, and so every age's: "all other statistics" are the mother's.
MUNDANE = ["Ambush Predator", "Loathsome Appearance", "Slippery", "Venomous"]
TRAITS = {
    "Serpent (Essential Trait)": 6,
    "Brave": 3,
    "Hungry for Vis": 3,
    "Territorial": 2,
}
REPUTATIONS = {"Venomous (local)": 4}
CONFIDENCE = (2, 6)


def _times(entry: Any, count: int) -> list[Any]:
    """A Quality taken `count` times."""
    return [entry] * count


class _Age(NamedTuple):
    """One block of the brood (pp. 142-144)."""

    label: str
    page: str
    might: int
    perception: int
    strength: int
    quickness: int
    size: int
    qualities: list[Any]
    fangs: tuple[int, int, int, int]
    #: Init, Attack, Defense; None before she can constrict.
    constriction: tuple[int, int, int] | None
    soak: int
    fatigue: str
    brawl: int
    magic_sensitivity: int
    swim: int
    how_many: str
    appearance: str
    notes: str


AGES = (
    _Age(
        "Hatchling",
        "p. 142",
        0,
        2,
        -14,
        9,
        -7,
        [
            "Improved Initiative",
            *_times(BETTER, 3),
            vf_minor("Puissant Stealth"),
            vf_minor("Sharp Eyes"),
            "Miniature",
            "Temporary Might",
        ],
        (12, 8, 13, -13),
        None,
        3,
        FATIGUE,
        2,
        0,
        1,
        "At least a hundred in the caves",
        "Three feet long and an inch thick at the fattest, born this year.",
        "Printed Stealth 4+2: the +2 is Puissant Stealth. A hatchling has +3 on "
        "any roll to hide, for its tininess.",
    ),
    _Age(
        "One Year Old",
        "p. 142",
        5,
        -2,
        -8,
        6,
        -4,
        [*_times(GIFT, 2), *_times("Improved Powers", 2), BETTER]
        + ["Temporary Might", MUST_BITE],
        (6, 8, 10, -7),
        None,
        3,
        FATIGUE,
        2,
        0,
        1,
        "Perhaps half as many as the hatchlings in the caves",
        "Over six and a half feet long and three inches thick at the fattest, "
        "the size of an unusually big adder.",
        "Her Magical Qualities differ greatly from a hatchling's: many have been "
        "traded for others.",
    ),
    _Age(
        "Two Years Old",
        "p. 142",
        10,
        -2,
        -2,
        5,
        -1,
        ["Gigantic", *_times(GIFT, 2), *_times("Improved Powers", 2)]
        + [QUICK, BETTER, SENSE, "Temporary Might", MUST_BITE],
        (5, 8, 9, -1),
        None,
        3,
        FATIGUE,
        2,
        1,
        2,
        "Perhaps half as many as the hatchlings in the caves",
        "About 13 feet long and six inches thick at the widest.",
        "",
    ),
    _Age(
        "Three Years Old",
        "p. 142",
        15,
        -2,
        2,
        3,
        1,
        [*_times("Gigantic", 2), *_times(GIFT, 2), *_times("Improved Powers", 2)]
        + ["Improved Soak", QUICK, BETTER, SENSE, TOUGH]
        + ["Temporary Might", MUST_BITE],
        (5, 8, 7, 3),
        (3, 8, 5),
        8,
        FATIGUE,
        2,
        2,
        3,
        ELDERS,
        "About 21 feet long, with a greatest thickness of nine inches.",
        "Big enough now to constrict human-sized targets.",
    ),
    _Age(
        "Four Years Old",
        "p. 143",
        20,
        -2,
        6,
        1,
        3,
        [*_times("Gigantic", 3), *_times(GIFT, 2), ATTACK, DEFENSE]
        + [*_times("Improved Powers", 2), "Improved Soak"]
        + [QUICK, BETTER, SENSE, TOUGH, "Temporary Might", MUST_BITE],
        (3, 10, 7, 7),
        (1, 8, 3),
        8,
        FATIGUE,
        2,
        3,
        3,
        ELDERS,
        "About 33 feet long, with a greatest thickness of 16 inches.",
        "Can swallow whole any character of Size -2 or smaller.",
    ),
    _Age(
        "Five Years Old",
        "p. 143",
        25,
        -2,
        8,
        0,
        4,
        [*_times("Gigantic", 4), TWO_HEADS, *_times(GIFT, 2), ATTACK, DEFENSE]
        + [*_times("Improved Powers", 3), "Improved Soak"]
        + [QUICK, BETTER, SENSE, TOUGH, "Temporary Might"]
        + [CLUMSY, EYESIGHT, MUST_BITE],
        (2, 11, 7, 9),
        (0, 9, 3),
        8,
        FATIGUE,
        3,
        3,
        3,
        ELDERS,
        "About 42 feet long, with a greatest thickness of 20 inches, and made "
        "ungainly by her bulk.",
        "Can swallow whole any character of Size -1 or smaller.",
    ),
    _Age(
        "Six Years Old",
        "p. 143",
        30,
        -2,
        10,
        -1,
        5,
        [*_times("Gigantic", 5), TWO_HEADS, *_times(GIFT, 2), "Gift of Speech"]
        + [*_times(ATTACK, 2), DEFENSE, *_times("Improved Powers", 3)]
        + [*_times("Improved Soak", 2), QUICK, BETTER, SENSE, TOUGH]
        + ["Temporary Might", TONGUE, CLUMSY, EYESIGHT, MUST_BITE],
        (1, 13, 6, 11),
        (-1, 9, 2),
        10,
        FATIGUE,
        3,
        3,
        3,
        ELDERS,
        "Over 53 feet long, with a greatest thickness of two and a quarter feet.",
        "Can swallow whole any character of Size 0 or smaller. From this age she "
        "can talk, but her divided tongue keeps her voice to a bare whisper.",
    ),
    _Age(
        "Seven Years Old",
        "p. 144",
        35,
        -2,
        12,
        -2,
        6,
        [*_times("Gigantic", 6), TWO_HEADS, *_times(GIFT, 2), "Gift of Speech"]
        + [*_times(ATTACK, 2), *_times(DEFENSE, 2), *_times("Improved Powers", 3)]
        + [*_times("Improved Soak", 3), QUICK, BETTER, SENSE, TOUGH]
        + ["Temporary Might", TONGUE, CLUMSY, EYESIGHT, MUST_BITE],
        (0, 14, 8, 13),
        (-2, 10, 2),
        12,
        FATIGUE,
        4,
        4,
        3,
        ELDERS,
        "About 67 feet long, with a greatest thickness of three feet.",
        "Can swallow whole any character of Size +1 or smaller.",
    ),
    _Age(
        "Eight Years Old",
        "p. 144",
        40,
        -2,
        14,
        -3,
        7,
        [*_times("Gigantic", 7), TWO_HEADS, *_times(GIFT, 2), "Gift of Speech"]
        + [*_times(ATTACK, 2), *_times(DEFENSE, 2), *_times("Improved Powers", 3)]
        + [*_times("Improved Soak", 4), QUICK, BETTER, SENSE, TOUGH]
        + [*_times(SCION, 2), "Temporary Might", TONGUE, CLUMSY, EYESIGHT]
        + ["Reduced Fatigue", MUST_BITE],
        (-1, 14, 7, 15),
        (-3, 10, 1),
        14,
        FATIGUE_REDUCED,
        4,
        4,
        3,
        ELDERS,
        "About 84 feet long, with a greatest thickness of three and a half feet.",
        "Can swallow whole any character of Size +2 or smaller. Brood of this "
        "size and larger tire easily under their bulk: one Fatigue level fewer.",
    ),
    _Age(
        "Nine Years Old",
        "p. 144",
        45,
        -2,
        16,
        -4,
        8,
        [*_times("Gigantic", 8), TWO_HEADS, *_times(GIFT, 2), "Gift of Speech"]
        + [*_times(ATTACK, 3), *_times(DEFENSE, 3), *_times("Improved Powers", 3)]
        + [*_times("Improved Soak", 4), QUICK, BETTER, SENSE, TOUGH]
        + [SCION, "Temporary Might", TONGUE, CLUMSY, EYESIGHT]
        + ["Reduced Fatigue", MUST_BITE],
        (-2, 16, 8, 17),
        (-4, 10, 0),
        14,
        FATIGUE_REDUCED,
        4,
        4,
        3,
        ELDERS,
        "About 106 feet long, with a greatest thickness of five feet.",
        "Can swallow whole any character of Size +3 or smaller. This is the "
        "biggest the brood grow, one Size below their mother. The block prints "
        "Personal Power once for Scion of the World Serpent, where the "
        "eight-year-old's has it twice.",
    ),
)


def build(b: Builder) -> None:
    caves, insula = _lair(b)
    grove, pasture = _vis_places(b)
    _exits(b, insula)
    waimie = _waimie(b, insula)
    brood = _brood(b, caves)
    husband, daughter = _kin(b, insula, caves)
    _cult(b, waimie)
    threat = _story(b, waimie)
    _seeds(b, grove, insula, husband, daughter)
    b.link(threat, "creatures", waimie, "The serpent behind the thefts")
    b.link(threat, "creatures", brood[1], "The first thief at the vis source")
    b.link(waimie, "places", grove, "Her favourite vis")
    b.link(pasture, "creatures", waimie, "The tale of the milk")


# -- the powers --


def _constriction() -> CreaturePower:
    return Builder.power(
        "Constriction",
        0,
        0,
        "",
        does="Non-magical. She can constrict only a victim smaller than she is, "
        "by the grappling rules (ArM5 p. 174). While she holds the grapple the "
        "victim counts as deprived of air (ArM5 p. 180) and makes a Stamina check "
        "every five rounds or takes the usual effects. Once a grapple is "
        "established she can keep constricting and still bite, at the held "
        "victim or at someone else. (p. 134)",
    )


def _envenomed_gift() -> CreaturePower:
    return Builder.power(
        "The Envenomed Gift",
        0,
        0,
        "Vim",
        level=50,
        does="On top of the ordinary venom she may choose to taint the Gift of "
        "anyone she bites, who suffers the Painful Magic Flaw for a day. No "
        "Hermetic equivalent. Greater Power x 2 (50 levels, -5 Might cost, +5 "
        "Init). The book prints the word Init with no figure after it, so the "
        "Initiative here is left at 0. (p. 134)",
    )


def _serpent_spies() -> CreaturePower:
    return Builder.power(
        "Serpent Spies",
        2,
        -4,
        "Animal",
        rtd=("Touch", "Sun", ""),
        level=40,
        does="With a touch she links her mind to one of her children and sees "
        "and hears all that the young serpent does. She can hold any number of "
        "these links at once, and each lasts until she drops it, but the Might "
        "spent on a link does not return until then. Printed as Init Qik -4. "
        "InAn 40 (Base 15, +1 Touch, +2 Sun, +1 extra sense, +1 constant). "
        "Greater Power (40 levels, -2 Might cost). (pp. 134-135)",
    )


def _scion() -> CreaturePower:
    return Builder.power(
        "Scion of the World Serpent",
        0,
        -2,
        "Animal",
        rtd=("", "Sun", ""),
        level=30,
        does="She swells to any Size from one above her present Size up to +12, "
        "with +2 Strength and -1 Quickness per point of Size and new wound "
        "ranges. Size +9 is 130 feet long and six feet thick, +10 is 170 by "
        "seven, +11 is 210 by ten, and +12 is 265 by thirteen. It must be "
        "renewed at sunrise and sunset and may lapse if she is distracted then. "
        "While it lasts her natural attacks are magical and must Penetrate "
        "Magic Resistance; Animal spells still use her original Size. MuAn 30 "
        "(Base 4, +2 Sun, +4 Size to affect Size +12). Personal Power x 2 (30 "
        "levels, -3 Might cost, +1 Init). (p. 135)",
    )


def _swallow_whole() -> CreaturePower:
    return Builder.power(
        "Swallow Whole",
        0,
        0,
        "",
        does="Non-magical. She can swallow anything at least 5 Size points "
        "smaller than she is. A creature not first subdued by Constriction may "
        "struggle, but stays constricted while swallowed. No one can breathe "
        "inside her, so deprivation rolls (ArM5 p. 180) apply even after "
        "escaping the grapple. Three rounds later the victim reaches the "
        "stomach: acid does +9 damage a round, or +36 at full immersion (ArM5 "
        "p. 181). A Strength + Athletics roll each round may brace him: Ease "
        "Factor 6 for half immersion (triple damage), 9 for one limb (double), "
        "12 for a splash (normal). She swallows no second creature until the "
        "first reaches the stomach. (p. 135)",
    )


def _two_heads() -> CreaturePower:
    return Builder.power(
        "Two Heads Are Better Than One",
        1,
        -4,
        "Animal",
        rtd=("", "Sun", ""),
        level=50,
        does="Costs 1 or more points. Her head splits lengthwise into two or "
        "more, one more per extra Might point, each giving another attack. She "
        "fights as a trained group of as many as she has heads, with no "
        "Leadership limit on the Group bonus. Physical attacks made with this "
        "power must Penetrate Magic Resistance. MuAn 50 (Base 25, +2 Sun, +3 "
        "Size). Greater Power (50 levels, -4 Might cost and +1 Init from "
        "Improved Powers). (p. 135)",
    )


def _venomous_bite() -> CreaturePower:
    return Builder.power(
        "Venomous Bite",
        0,
        0,
        "",
        does="Non-magical. Compare her Attack Advantage with the victim's armor "
        "Protection, not his Soak: if hers is higher, he takes the effects of "
        "adder venom (Poison Table, ArM5 p. 180), wounded or not. (p. 135)",
    )


# -- the creatures --


def _waimie(b: Builder, insula: Neighbour) -> Creature:
    return b.creature(
        "The Waimie",
        page="pp. 134-135",
        realm="Magic",
        might=49,
        form="Animal",
        size=9,
        season="Autumn",
        confidence=CONFIDENCE,
        place=insula,
        block={
            "characteristics": characteristics(0, -1, -6, -6, 18, 2, 2, -5),
            "virtues_flaws": [
                "Magic Animal",
                "Magical Monster",
                ("Greater Immunity", {"hazard": "blades"}),
                "Arcane Lore",
                "Improved Characteristics",
                "Lightning Reflexes",
                "Personal Vis Source",
                ("Student of {realm}", {"realm": "magic"}),
                "Difficult Underlings",
                "Driven (Minor)",
                "Infamous",
                *_times("Gigantic", 9),
                ("Greater Power", {"power": "Serpent Spies"}),
                TWO_HEADS,
                *_times(GIFT, 2),
                "Gift of Speech",
                *_times(ATTACK, 3),
                *_times(DEFENSE, 3),
                *_times("Improved Powers", 3),
                *_times("Improved Soak", 4),
                QUICK,
                BETTER,
                SENSE,
                TOUGH,
                *_times(SCION, 2),
                ("Major Flaw", {"flaw": "Hunger for Animal Magic"}),
                TONGUE,
                CLUMSY,
                EYESIGHT,
                "Reduced Fatigue",
                "Reduced Might",
                MUST_BITE,
                *MUNDANE,
            ],
            "abilities": [
                ("Area Lore: Local", 6, "vis sources"),
                ("Area Lore: Regional", 4, "vis sources"),
                ("Area Lore: Magic Realm", 5, "Animal boundaries"),
                ("Awareness", 3, "prey"),
                ("Brawl", 6, "fangs"),
                ("Hunt", 4, "vis"),
                ("Leadership", 4, "brood"),
                ("Living Language: Local", 5, "common dialect"),
                ("Magic Lore", 5, "Magic Realm"),
                ("Magic Sensitivity", 5, "vis"),
                ("Organization Lore: Order of Hermes", 2, "covenants"),
                ("Stealth", 4, "stalking prey"),
                ("Survival", 2, "grassy areas"),
                ("Swim", 4, "rivers"),
            ],
            "traits": TRAITS,
            "reputations": REPUTATIONS,
        },
        attacks=[
            b.attack("Fangs", -3, 18, 8, 19),
            b.attack("Constriction", -5, 12, 1, None),
        ],
        soak=14,
        fatigue_levels=FATIGUE_REDUCED,
        powers=[
            _constriction(),
            _envenomed_gift(),
            _serpent_spies(),
            _scion(),
            _swallow_whole(),
            _two_heads(),
            _venomous_bite(),
        ],
        vis=[BodyVis(6, "Animal", "eyes"), BodyVis(4, "Perdo", "teeth")],
        appearance=paragraphs(
            "A monstrous legless, wingless dragon of a serpent, 130 feet from end "
            "to end and more than six feet through at the widest. Each horny "
            "scale carries a ridge drawn out into a spine lying flat along the "
            "body, and snake's scutes run down her belly. The head is eight feet "
            "long and wedge-shaped, hooked at the tip, with curved fangs. She is a "
            "blotched green, darker along the back and paler toward the belly, "
            "and she speaks in a whisper that trembles over a forked tongue.",
        ),
        notes=paragraphs(
            wound_ranges(9),
            "Printed Magic Lore 5+2: the +2 is Student of Magic. Serpent is her "
            "Essential Trait. Her block gives Fatigue levels OK, -1, -3, -5, "
            "Unconscious.",
            "Pronounced WAY-mee. It is the word of northern England and southern "
            "Scotland for a worm, in the sense of a dragon. Elsewhere she takes "
            "another name: the Orm in northern Europe, the Wivere where French is "
            "spoken, the Suge among the Basques, the Mengue in Cantabria, the "
            "Hudra among the Greeks, and perhaps the Lindwurm in the Rhine "
            "Tribunal. (p. 134)",
            "What the valley tells. A century ago, they say, a sinner fishing on "
            "a Sunday caught an eel-like thing and threw it down a well. It grew. "
            "Milk sated its hunger for livestock, until the valley's one dairy "
            "farmer could not keep up, and each wound it took from the knights "
            "closed with its own blood. A champion in armor set with blades faced "
            "it astride a river and it cut itself apart in his grip; the river "
            "carried off the blood, and every piece became a small serpent "
            "waiting to be fished out on a Sunday. One old man holds instead that "
            "its hide was proof against everything, and that it died of burning "
            "peat thrust down its throat on a spear, new serpents rising where "
            "the burning blood fell on marjoram. A third swears it was a princess "
            "cursed by her stepmother and freed by her brother, and that the "
            "curse rebounded on the witch, who haunts the land with her brood "
            "still. (pp. 137-138)",
            "Add the aura modifier to Magic Resistance and subtract the Magic "
            "Sensitivity score. A Quality or Inferiority that changes a Magic "
            "Animal's Size leaves its Might alone, as Size comes off Might before "
            "Qualities are bought (Realms of Power: Magic pp. 30-36); a change "
            "of Size by a Virtue or Flaw does alter Might. The book offers this "
            "as a clarification. (pp. 134-135)",
        ),
        secrets=[
            titled(
                "Why the Waimie wants vis",
                "An ancient creature of the Magic Realm, and very strong for it. "
                "She needs vis to hold what she has learned and to grow, so she "
                "bears serpents without end and sends them to fetch it. (p. 133)",
            ),
            titled(
                "What becomes of her brood",
                "She feels little for her serpents. Most die in the crush of "
                "siblings; those that live often lose ground to Acclimation as "
                "they grow. (p. 133)",
            ),
            titled(
                "Half the year in the Magic Realm",
                "She keeps half the year in the Magic Realm, sharing her cave with "
                "whichever child is least stupid. (pp. 133, 137)",
            ),
            titled(
                "Eyes in her children",
                "She spies through her small children, and so learned of the Order "
                "and how magi hunt and hoard vis, which suggested an easier way to "
                "feed. (pp. 133, 137)",
            ),
            titled(
                "What she does not know",
                "She has no knowledge of the Aegis of the Hearth. (pp. 133, 137)",
            ),
            titled(
                "Her rebellious daughters",
                "Her large daughters press her constantly, sometimes in league with "
                "younger ones, for too many survivors try to kill her and mother "
                "broods of their own. (p. 133)",
            ),
            titled("What blades do to her", "Blades cannot harm her. (p. 138)"),
            titled(
                "Wounds that bleed serpents",
                "In her insula each wound she takes bleeds a living serpent into "
                "the fight on her side: a one-year-old from a Light Wound, a "
                "three-year-old from a Medium, a five-year-old from a Heavy or "
                "Incapacitating. These do not spawn in turn when hurt. (p. 140)",
            ),
            titled(
                "How she fights at home",
                "She hides among the mounds of her insula and strikes by surprise. "
                "(p. 140)",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "None of the tales is true, but one holds a hint that blades "
                    "cannot harm her; the book does not say which, and nothing "
                    "tells the characters so. (p. 138)",
                    "A harder fight in the insula adds her offspring of six to "
                    "eight years. (p. 140)",
                    "A weaker Waimie: use one of the brood as the mother, and slow "
                    "them to two or more years per step. Or alternate the yearly 5 "
                    "Might with 5 points of Inferiorities: Minor Flaw (Anchored to "
                    "(Land), Baneful Circumstances, Clumsy, Environmental "
                    "Sensitivity, Essential Flaw, (Form) Monstrosity, Lesser "
                    "Malediction or Poor Characteristic), Reduced Attack, Reduced "
                    "Might or Reduced Powers; some are in Realms of Power: Magic "
                    "pp. 47-51. (p. 135)",
                    "A stronger Waimie: give her human servants, the Cult of the "
                    "Serpent, held perhaps by something like Entrancement. Without "
                    "Difficult Underlings she can send her children in coordinated "
                    "groups, and if she beats the magi outright she need share no "
                    "vis source with her brood. (p. 136)",
                ),
            ),
        ],
    )


def _brood(b: Builder, caves: Neighbour) -> list[Creature]:
    return [_one_age(b, caves, age) for age in AGES]


def _one_age(b: Builder, caves: Neighbour, age: _Age) -> Creature:
    powers = [_venomous_bite()]
    if age.might >= 5:
        powers.append(_envenomed_gift())
    if age.constriction is not None:
        powers.insert(0, _constriction())
    if age.might >= 20:
        powers.append(_swallow_whole())
    if age.might >= 25:
        powers.append(_two_heads())
    if age.might >= 40:
        powers.append(_scion())
    attacks = [b.attack("Fangs", *age.fangs)]
    if age.constriction is not None:
        attacks.append(b.attack("Constriction", *age.constriction, None))
    abilities = [
        ("Awareness", 2, "prey"),
        ("Brawl", age.brawl, "fangs"),
        ("Hunt", 4, "rodents"),
        ("Stealth", 4, "stalking prey"),
        ("Survival", 3, "grassy areas"),
        ("Swim", age.swim, "rivers"),
    ]
    if age.magic_sensitivity:
        abilities.append(("Magic Sensitivity", age.magic_sensitivity, "vis"))
    return b.creature(
        f"The Waimie's Brood: {age.label}",
        page=age.page,
        realm="Magic",
        might=age.might,
        form="Animal",
        size=age.size,
        season="Autumn",
        confidence=CONFIDENCE,
        cunning=True,
        age=age.label,
        how_many=age.how_many,
        place=caves,
        block={
            "characteristics": characteristics(
                -1, age.perception, -6, -6, age.strength, 2, 2, age.quickness
            ),
            "virtues_flaws": [
                "Lightning Reflexes",
                "Infamous",
                *age.qualities,
                *MUNDANE,
            ],
            "abilities": abilities,
            "traits": TRAITS,
            "reputations": REPUTATIONS,
        },
        attacks=attacks,
        soak=age.soak,
        fatigue_levels=age.fatigue,
        powers=powers,
        vis=[BodyVis(ceil(age.might / 5), "Animal", "eyes")] if age.might else [],
        appearance=paragraphs(
            age.appearance,
            "The young look like snakes. With size the head lengthens to a "
            "crocodile's wedge, and the scales thicken, overlap and grow ridges "
            "and spines.",
        ),
        notes=paragraphs(
            wound_ranges(max(age.size, -4)),
            age.notes,
            "Her Season, Confidence, Mundane Qualities, Personality Traits and "
            "Reputation are not in this block: all a block omits is her mother's "
            "(p. 133). Each power has the figures of her mother's block. A year "
            "adds 5 Might and 5 points of Magical Qualities, Gigantic first from "
            "the second year (p. 134).",
            "Add the aura modifier to Magic Resistance and subtract the Magic "
            "Sensitivity score. Animal spells need a Size modifier above Size +1: "
            "one for +2 to +4, two for +5 to +7, three for +8 to +10 (ArM5 p. "
            "113). A pawn of Animal vis per 5 points of Might, or part of 5, "
            "lies in the eyes of the corpse (p. 134). As magical creatures they "
            "need no food, water or air (p. 138).",
        ),
        secrets=[
            titled(
                "Sent by the Waimie",
                "Sent for vis by her mother, the Waimie, who may be watching "
                "through her eyes. (pp. 134-135, 139)",
            ),
            titled(
                "Poor eyes",
                "Easily fooled by illusions, shapeshifting and distractions, she is "
                "not very attentive and sees poorly, though Magic Sensitivity, once "
                "she has it, hinders invisibility used to slip past her. (pp. "
                "134-135, 139)",
            ),
        ],
    )


def _kin(b: Builder, insula: Neighbour, caves: Neighbour) -> tuple[Creature, Creature]:
    husband = b.creature(
        "The Serpent's Husband",
        page="p. 140",
        place=insula,
        appearance="To look at, a man, and a much smaller thing than his wife.",
        notes="The book prints no statistics and leaves his powers to the "
        "storyguide. An optional inhabitant of the insula.",
        secrets=[
            titled("Whose husband he is", "The father of the Waimie's brood."),
            titled(
                "A friendly greeting",
                "Once the characters are exploring he comes to them with a friendly "
                "greeting and says who he is, with no wish for revenge and no "
                "feeling at all at the Waimie's death. He explains the Serpent Map "
                "and is useful.",
            ),
            titled(
                "What he truly is",
                "The Serpent of Eden was a snake that took human shape: he is very "
                "likely a shapechanger, either a magical man who can be a serpent or "
                "a snake who walks as a man.",
            ),
        ],
    )
    daughter = b.creature(
        "The Rebellious Daughter",
        page="p. 136",
        place=caves,
        notes="An elder daughter of the Waimie. The book names no age and prints "
        "no block of her own: use the brood block that suits.",
        secrets=[
            titled(
                "Looking for freedom",
                "If the characters are not at once hostile to the brood, she looks "
                "to them for freedom.",
            ),
            titled(
                "Shut out by the Waimie",
                "Her mother shuts the eldest out of the Magic Realm cave, so that "
                "Acclimation stunts them and they can neither challenge her nor "
                "brood, which needs a serpent of the mother's size. Some eat their "
                "kin for the vis; some roam far for it, and it is barely enough.",
            ),
            titled(
                "What the daughter needs",
                "She needs a Magic aura strong enough to stop Acclimation, and a "
                "mate that is near enough serpent or dragon.",
            ),
        ],
    )
    return husband, daughter


# -- the lair --


def _lair(b: Builder) -> tuple[Neighbour, Neighbour]:
    caves = b.place(
        "The Malachite Caves",
        summary="A dozen or so joined caverns in wild country far from anyone, "
        "by a river mouth or among sea caves. The rock shows fluted columns that "
        "glitter with shifting colors by torchlight, and the walls are banded "
        "with green malachite, with the odd emerald in roof and floor. Some "
        "linking passages are too narrow for a man; the others are worn "
        "glass-smooth and faintly rippled by the passing of serpents beyond "
        "number.",
        status="Rumoured",
        known=LOCAL,
        aura=3,
        tethers="The labyrinthine caves (natural, 2); her long residence "
        "(preternatural, 2); the saga may add a waterfall (natural, 1), "
        "wave-carved stone (natural, 1) or a site of great rituals "
        "(preternatural, 1-2).",
        levels=[
            b.level(
                "The Malachite Mound",
                10,
                enter="Ease Factor 11 for the fitting Supernatural Ability (ArM5 "
                "p. 189), from the deepest cavern.",
                see="The floor is one great mound of solid malachite, with a deep "
                "spiral groove cut around it.",
                notes="Walking the spiral to the summit, at the middle of the room, "
                "passes through a gate into the Magic Realm.",
            )
        ],
        secrets=[
            titled(
                "The deepening aura",
                "The aura of the Malachite Caves is 3 by the entrance and rises "
                "with depth to 8 in the last cave, reached by no direct way though "
                "its passages are the widest, ten feet across on average. (pp. "
                "138-139)",
            ),
            titled(
                "A caveful at a time",
                "Each cave holds serpents of mixed sizes, who resent intruders but "
                "hardly talk to each other, so a party meets one caveful at a time. "
                "(pp. 138-139)",
            ),
            titled(
                "Killing the cave serpents",
                "Killing the serpents of the Malachite Caves does not stop the "
                "thefts. (pp. 138-139)",
            ),
            titled(
                "When the serpents are alert",
                "Once alert the cave serpents spread out, cutting area spells to "
                "between a half and a third. Sealed in, they simply wait. (p. 138)",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The saga chooses where the caves lie, but they must be near "
                    "water and in a Magic aura of at least 5, with some local "
                    "feature to explain it, by tethers added together (Realms of "
                    "Power: Magic p. 8). (pp. 138-139)",
                    "On the first visit their mother is away. A lone serpent two "
                    "years older than any yet met will seem the mistress of them "
                    "all; for a harder fight, a horde attacks as an untrained "
                    "group. (pp. 138-139)",
                    "Area spells catch several at once. An Individual of Ignem "
                    "fills the volume of one Size 0 creature, which is two of Size "
                    "-1, five of Size -2, ten of Size -3 or twenty of Size -4, and "
                    "so on. A Pilum of Fire can hit two hundred hatchlings, or "
                    "fifty with five yearlings and a two-year-old. (p. 138)",
                ),
            ),
        ],
    )
    insula = b.place(
        "The Waimie's Insula",
        inside=caves,
        level=1,
        status="Hidden",
        known="Hidden",
        aura=14,
        summary="A cave like those of the world outside but immeasurably larger, "
        "floored with hundreds of malachite mounds from a few feet across to "
        "the size of hills, each scored with a spiral. The spirals run both "
        "ways and interlock, and from a height they look like a map or a "
        "foreign, curling script. The land changes, too slowly to watch, as if "
        "a nest of snakes were languidly coiling.",
        secrets=[
            titled(
                "The Animal boundary",
                "The Waimie's Insula is enclosed by an Animal Boundary of level 4. "
                "(p. 140)",
            ),
            titled(
                "A hiding place for her children",
                "Even with the Waimie dead a child of hers may hide in the insula "
                "and grow to be a new danger. (p. 140)",
            ),
            titled(
                "Visitors from the Magic Realm",
                "Visitors from elsewhere in the Magic Realm, serpents and dragons "
                "most of all, slip through the boundary of the Waimie's Insula. "
                "(p. 140)",
            ),
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The effective Magic aura is 14, or 18 for anything to do "
                    "with Animal, her Magic Resistance and Penetration among them. "
                    "Any magical activity has four extra botch dice. (p. 140)",
                    "The storyguide peoples its far reaches. (p. 140)",
                    "Crossing a boundary has a base Ease Factor of 18, ignoring "
                    "Familiarity; using a vestige has (10 - vestige level) x 3. "
                    "See Realms of Power: Magic p. 23. (p. 141)",
                ),
            ),
        ],
    )
    b.place(
        "The Serpent Map",
        inside=insula,
        status="Hidden",
        known="Hidden",
        summary="The landscape of the insula itself, read by moving across it.",
        secrets=[
            titled(
                "A map in the speech of serpents",
                "The Serpent Map is both a map and a book in the speech of "
                "serpents: an intelligent snake crossing it begins to take in a "
                "chart of part of the Magic Realm, marked with its marvels and "
                "dangers. (pp. 140-141)",
            ),
            titled(
                "Studying the Serpent Map",
                "A season's study of the Serpent Map is a Summa on Area Lore: Magic "
                "Realm, Level 5, Quality 4. With the Animal Ken Virtue the Quality "
                "is the Animal Ken score if over 5; a Bjornaer with a snake "
                "heartbeast uses an effective Language score of 5 (Houses of "
                "Hermes: Mystery Cults p. 23); and spending half the season as a "
                "serpent adds 3. (p. 141)",
            ),
            titled(
                "Storyguide Notes",
                "At the storyguide's option it can locate things, at a week's study "
                "per 3 points of Ease Factor and a roll of Intelligence + Area "
                "Lore: Magic Realm: a Magic aura at 9 + aura, a Magic regio at 12 + "
                "its highest aura, a vis source at 15 + its yearly pawns, a Magic "
                "Realm gate at 18. Success lets the reader trace the place from any "
                "known aura in the mundane world. (p. 141)",
            ),
        ],
    )
    return caves, insula


def _exits(b: Builder, insula: Neighbour) -> None:
    for name, summary, title, secret in (
        (
            "The Stream of the Insula",
            "A stream crossing one part of the insula.",
            "Where the stream leads",
            "The stream is a boundary into an insula aligned to Aquam.",
        ),
        (
            "The Great Ivy Root",
            "The root of a huge ivy against one wall, climbing out of sight.",
            "Where the ivy leads",
            "A climber crosses this Herbam boundary into an insula ruled by plants.",
        ),
        (
            "The Malachite Statue",
            "A little abstract statue of the same malachite on a small mound, all "
            "arches and rings, which from some angles suggests a dancing woman.",
            "The dancers' vestige",
            "The Malachite Statue is a Terram vestige of level 4, of a Mystery Cult "
            "of dancers who raise fertility by their art. It is present too in an "
            "insula of Mentem and one of Corpus.",
        ),
        (
            "The Phantom Mouse",
            "A mouse that runs through the lair, glimpsed from the corner of the "
            "eye or heard as tiny feet.",
            "The cat's dream",
            "The Phantom Mouse is an Imaginem vestige of level 2, tied to the dream "
            "of a cat that is a magus' familiar. It appears in several insulae, and "
            "whoever catches it can travel with it to them.",
        ),
    ):
        b.place(
            name,
            inside=insula,
            status="Hidden",
            known="Hidden",
            summary=summary,
            secrets=[
                titled(title, f"{secret} (p. 141)"),
                titled(
                    "Storyguide Notes",
                    "A sample exit: the storyguide sets the true destination. (p. 141)",
                ),
            ],
        )


def _vis_places(b: Builder) -> tuple[Neighbour, Neighbour]:
    grove = b.place(
        "The Marjoram Grove",
        status="Rumoured",
        known=LOCAL,
        summary="A far-off grove where marjoram grows.",
        secrets=[
            titled(
                "Whose vis grows here",
                "The Waimie's own vis source, which she prizes above all other vis. "
                "(p. 136)",
            ),
            titled(
                "Gathering the marjoram",
                "Each year a child of the Waimie's gathers three sprigs as the star "
                "Regulus rises; the herb stills the carrier's venom for the trip "
                "home. (p. 136)",
            ),
            titled(
                "Storyguide Notes",
                "The grove feeds her Hunger for Animal Magic. The book gives no pawn "
                "count and no place. (p. 136)",
            ),
        ],
    )
    pasture = b.place(
        "The Church's Parcel in the Valley",
        realm="",
        status="Known",
        known=LOCAL,
        summary="The one parcel in the valley where cows ever gave good milk; "
        "elsewhere it came out foul and acrid. The freeman who held it died "
        "childless and left it to the Church, which lets it to local serfs for "
        "garden crops.",
        secrets=[
            titled(
                "Why the milk was good",
                "Those who know the Waimie's appetite may guess why she liked the "
                "milk: put back to pasture, the land would give cows whose milk "
                "yields Creo vis. (p. 138)",
            ),
            titled("Storyguide Notes", "The book gives no amount. (p. 138)"),
        ],
    )
    return grove, pasture


# -- the people --


def _cult(b: Builder, waimie: Creature) -> None:
    cult = b.faction(
        "The Cult of the Serpent",
        summary="A band of folk who speak of a Scaly Queen and go about gathering "
        "news.",
        faction="Faith or sect",
        decides="A charismatic leader",
        secrets=[
            titled(
                "Whom the cult serves",
                "The cultists gather information and vis for the Waimie. (p. 136)",
            ),
            titled(
                "Storyguide Notes",
                "An option for a stronger Waimie, not part of the story as printed. "
                "Her human servants are perhaps held by a power like the "
                "Entrancement Ability. (p. 136)",
            ),
        ],
    )
    leader = b.magus(
        "The Leader of the Cult of the Serpent",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="The persuasive head of the Cult of the Serpent.",
        secrets=[
            titled(
                "A hedge wizard",
                "A hedge wizard with a selection of serpent-related powers. (p. 136)",
            ),
            titled(
                "Kin to the serpents",
                "The leader of the cult is somehow kin to the Waimie's brood. (p. 136)",
            ),
            titled(
                "Storyguide Notes",
                "Has The Gentle Gift and Magical Blood of the serpent. The book "
                "prints no statistics. (p. 136)",
            ),
        ],
    )
    b.link(leader, "places", cult, "Leads it")
    b.link(cult, "creatures", waimie, "Its Scaly Queen")


# -- the story --


def _story(b: Builder, waimie: Creature) -> Neighbour:
    return dormant(
        b.threat(
            "The Stolen Vis",
            antagonist=waimie.name,
            moves="A track",
            summary="Someone has been at the covenant's vis before the magi could "
            "get there. A snake has been seen near the place.",
            secrets=[
                titled(
                    "Who is stealing the vis",
                    "A serpent of the Magic Realm is sending her young to rob the "
                    "covenant's vis, first at its sources, then at home. (pp. 7, "
                    "133)",
                ),
                titled(
                    "A tithe instead of thefts",
                    "The Waimie need not be killed: she will settle for a tithe of "
                    "vis, smaller perhaps than what her children would steal, with "
                    "no lives lost. (p. 141)",
                ),
                titled(
                    "Storyguide Notes",
                    "She suits a run of linked stories close together better than "
                    "a saga-long theme, and her brood start small and grow more "
                    "dangerous. (pp. 7, 133)",
                ),
            ],
            stages=[
                b.stage(
                    "The Empty Vis Source",
                    at=1,
                    clues="A portable vis source, gathered without magic or "
                    "skill, is found already stripped, and again the next year. "
                    "Anyone left on guard sees a yearling snake come for it, "
                    "knowing just where the vis is and how to take it.",
                    ignored="She has a share of the covenant's vis every year.",
                    stopped="The thief's fate depends on the guards. (p. 136)",
                ),
                b.stage(
                    "A Bigger Thief Each Year",
                    at=2,
                    clues="If the yearling was opposed, a two-year-old comes next "
                    "year, perhaps the same snake, scarred, perhaps not. Each year "
                    "a bigger one comes until one gets away with the vis; then "
                    "that size until it keeps failing.",
                    ignored="She wants vis home at least every other year on "
                    "average, and sends whatever size will do it.",
                    turned="The corpses hold Animal vis, so the covenant may treat "
                    "this as a contested source. She answers by sending a tiny "
                    "serpent with each large one, to fetch the dead sibling's "
                    "eyes. (p. 136)",
                ),
                b.stage(
                    "The Theft Spreads",
                    at=3,
                    clues="After some years a hatchling lurks near the covenant, "
                    "unseen, and trails anyone who leaves, hoping to be led to "
                    "more vis. On the third source the magi may notice: one "
                    "snake too many.",
                    ignored="She begins robbing a second source; with no other "
                    "suitable source she gets nothing. (pp. 136-137)",
                ),
                b.stage(
                    "The Covenant Raided",
                    at=4,
                    clues="While the spotted hatchling is chased, a serpent one "
                    "year older than any yet met enters the covenant, seeking vis "
                    "by Magic Sensitivity at Ease Factor 12 less the pawns present.",
                    ignored="With a single store she may eat three-quarters of it "
                    "before being found; with vis in each sanctum, she reaches "
                    "two or three. Found, she flees for home to bring it all up "
                    "for her mother, unless the opposition is slight, when she "
                    "may stay and kill grogs.",
                    stopped="A strong Aegis may hold her out, so the fight is "
                    "outside the walls. Traps in stores or sancta can stop her. "
                    "(p. 137)",
                ),
                b.stage(
                    "Investigations",
                    at=5,
                    clues="The locals have tales, contradictory ones, on the way "
                    "to or from the cave. A serpent can be followed home: the "
                    "smaller, the harder. They shun settled land and keep to "
                    "rivers and the sea, and unless the trackers draw notice they "
                    "are not seen. (pp. 137-138)",
                ),
                b.stage(
                    "The Lair",
                    at=6,
                    clues="The caves teem with serpents, but the mother is in her "
                    "absent season.",
                    ignored="Fighting her children changes nothing: she breeds "
                    "more, and larger ones are with her in the Magic Realm.",
                    stopped="Best shown as a meeting with bigger serpents than "
                    "yet seen, still low in the order, to set up the next "
                    "stage. (p. 138)",
                ),
                b.stage(
                    "Besieged",
                    at=7,
                    clues="Having lost too much to the magi, she wants revenge and "
                    "sends a daughter of at least eight years against a place "
                    "they value: the covenant, a vis site, even a village. Swollen "
                    "by Scion of the World Serpent to as much as Size +12 and 265 "
                    "feet, she rings it, enclosing up to 70 feet across, in "
                    "overlapping coils if it is smaller, with her head at the main "
                    "gate; or she lies along the edge of an Aegis that stops her.",
                    ignored="She stays until killed or driven off. Outward-opening "
                    "doors are jammed; anyone going in or out is attacked; "
                    "supplies are swallowed or flung far away.",
                    stopped="Parma may turn her attacks, for her Penetration "
                    "with this power is Might + aura modifier, but she can still "
                    "swallow a magus, harmless as that is if horrid. A stealthy "
                    "character may slip by her poor eyes, though her Magic "
                    "Sensitivity hinders invisibility. Magi who see her size "
                    "flicker at dawn or dusk may break her attention then, so "
                    "she cannot renew the power. (p. 139)",
                ),
                b.stage(
                    "Final Showdown",
                    at=8,
                    clues="Following her children back, through the deepest cave "
                    "and the regio, the magi climb the spiral to her lair in the "
                    "Magic Realm.",
                    stopped="She is extremely hard to kill at home; the characters "
                    "may need another answer than a straight fight. (pp. 139-140)",
                    turned="She will take a tithe of vis in place of the thefts. "
                    "(p. 141)",
                ),
            ],
        )
    )


def _seed(
    b: Builder,
    name: str,
    summary: str,
    secret: Secrets,
    place: Neighbour | None = None,
) -> Neighbour:
    """A story seed: a dormant threat with no stages."""
    return dormant(
        b.threat(
            name, antagonist="The Waimie", summary=summary, secrets=secret, place=place
        )
    )


def _seeds(
    b: Builder,
    grove: Neighbour,
    insula: Neighbour,
    husband: Creature,
    daughter: Creature,
) -> None:
    _seed(
        b,
        "The Queen's Vis",
        "A small serpent leaves the lair on some errand of its own, each year "
        "at the same time.",
        [
            titled(
                "Where the small serpent goes",
                "Whoever watches the lair and follows the small serpent can reach "
                "the Waimie's marjoram. (p. 136)",
            ),
            titled(
                "The marjoram as a hostage",
                "Taking the marjoram from her gives a strong hand with the Waimie, "
                "who may hold off the thefts for as long as he has it hostage. "
                "(p. 136)",
            ),
        ],
        grove,
    )
    rebel = _seed(
        b,
        "The Rebellious Daughter",
        "One of the great serpents does not attack on sight.",
        [
            titled(
                "An ally against the Waimie",
                "If the characters meet the Rebellious Daughter's needs she will "
                "stand with them against her mother; whether she can be trusted "
                "after that remains to be seen. (p. 136)",
            ),
            titled("Storyguide Notes", "See the daughter's record. (p. 136)"),
        ],
    )
    b.link(rebel, "creatures", daughter, "The daughter")
    _seed(
        b,
        "Wrong Side of the Fence",
        "The siege finds the covenant's people on both sides of the serpent.",
        [
            titled(
                "What lies inside the coils",
                "Those outside the serpent learn that what they need against her "
                "(vis, a ritual's casting tablet, an enchantment) is inside, and "
                "must get it past the coils. (p. 139)",
            )
        ],
    )
    _seed(
        b,
        "Not Alone",
        "A redcap brings word that a Hermetic rival is losing vis to the same "
        "thieves, and proposes a summit.",
        [
            titled(
                "Where the rival wants to meet",
                "The Hermetic rival wants the meeting held at the players' "
                "covenant. Some suspect a motive beyond the alliance against the "
                "serpent; surely not? (p. 139)",
            )
        ],
    )
    wed = _seed(
        b,
        "The Serpent's Husband",
        "A friendly man is met walking in the Waimie's lair.",
        [
            titled(
                "Storyguide Notes",
                "See the husband's record: is he all he seems? (p. 140)",
            )
        ],
        insula,
    )
    b.link(wed, "creatures", husband, "The husband")
    _seed(
        b,
        "Have We Made Things Worse?",
        "The great serpent is dead, and serpents are still seen.",
        [
            titled(
                "The young serpents",
                "The Waimie's death frees the brood. The young wander lost, and stay "
                "until Acclimation makes them plain serpents or their elders eat "
                "them. (p. 141)",
            ),
            titled(
                "The older serpents",
                "With the Waimie dead, the older of her brood flee to find auras and "
                "vis sources of their own; some may mature to her statistics and, "
                "with mates, brood. (p. 141)",
            ),
            titled(
                "Several Waimies",
                "With enough auras about there may be several Waimies competing for "
                "one set of vis sources, or a war until one rules. (p. 141)",
            ),
        ],
    )
    _seed(
        b,
        "Unwelcome Visitors",
        "Strangers from the Magic Realm begin to ask after the serpent's lair.",
        [
            titled(
                "Others who want the Serpent Map",
                "A few beings of the Magic Realm know of the Serpent Map and will "
                "not leave the characters to it. (p. 141)",
            ),
            titled(
                "A mightier seeker",
                "Some who seek the Serpent Map are only chancers, but what it holds "
                "is of use to mighty beings, and one will come in time, perhaps far "
                "worse than the Waimie was. (p. 141)",
            ),
        ],
        insula,
    )
