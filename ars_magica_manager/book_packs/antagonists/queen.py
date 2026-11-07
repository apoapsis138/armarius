"""The Queen of Gold and Glass (Antagonists pp. 7, 120-132), in paraphrase.

A faerie who runs young magi through eight stories so that her court can
copy their spells. The Queen, the frame, her servants and the faeries of
her stories are creatures; her kingdom and her treasures are places, as a
pack with no covenant keeps them; her court is a faction; the eight
challenges are the stages of a dormant threat, and the book's story seeds
are dormant threats with no stages.

The captive princess and the actor have no printed stats (p. 124 leaves
mortal pawns to other books), so they stay sketches. A Distinguished
Servant with no block keeps what the book says of it and no figures: its
Might shows as 0 and its notes say none is printed.

Catalog names stand in for the book's where they are the same thing:
Greater Power for Greater Faerie Power, Personal Power for Personal
Faerie Power, Humanoid Faerie for Humanoid Form, Improved Characteristics
for Increased Characteristics, Immune to Terram for Immunity from
Terram, Puissant Pretense for Puissant Militant Pretense, and Increased
Faerie Might for Increased Might. A Great Characteristic the book leaves
unnamed is entered as such. Cognizant within Role, which no book defines,
is taken as Narrowly Cognizant, the one of Realms of Power: Faerie's three
levels (p. 52) that fits. Spirit Away, which the block lists among the
Major Virtues, is a Greater Faerie Power (Realms of Power: Faerie p. 23), so
it stands among the powers."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Creature, Neighbour
from ..builder import (
    Builder,
    Secrets,
    characteristics,
    dormant,
    paragraphs,
    titled,
    vf_ward,
)

S = Builder.stage
P = Builder.power
QUEEN = "The Queen of Gold and Glass"
STORYGUIDE = "Storyguide Notes"
TIRELESS = "Tireless"
PRETENSES = "Its Abilities are the book's Pretenses."
NO_FIGURES = (
    "The book prints no Might, Characteristics or Powers for it; it gives "
    "none of its Pretenses by name."
)
#: A Great Characteristic the book does not name.
GREAT = ("Great {characteristic}", {"characteristic": "Characteristic"})
MINOR_MIGHT = "Increased Faerie Might (Minor)"
MAJOR_MIGHT = "Increased Faerie Might (Major)"
BLINDING_LIGHT = ("Sovereign Ward", {"ward": "blinding light"})


def _times(entry: Any, count: int) -> list[Any]:
    """A Virtue or Quality taken `count` times."""
    return [entry] * count


def build(b: Builder) -> None:
    kingdom = _kingdom(b)
    court = _court(b, kingdom)
    queen = _queen(b, kingdom)
    frame = _frame(b, kingdom)
    servants = _servants(b, kingdom)
    wyrm = _ice_wyrm(b)
    smoothfaces = _smoothfaces(b)
    knockers = _knockers(b)
    treasures = _treasures(b, kingdom)
    princess, actor = _people(b)
    threat = _threat(b)

    b.link(court, "creatures", queen, "Its sovereign")
    for servant in servants:
        b.link(court, "creatures", servant, "Serves in the court")
    b.link(kingdom, "characters", princess, "Held captive here")
    for name, treasure in treasures.items():
        b.link(queen, "places", treasure, name)
    b.link(threat, "creatures", queen, "Sets every challenge")
    b.link(threat, "creatures", frame, "A piece follows each challenge")
    b.link(threat, "creatures", wyrm, "The Ignem challenge")
    b.link(threat, "creatures", smoothfaces, "Dupes of the Herbam challenge")
    b.link(threat, "creatures", knockers, "Dupes of the Terram challenge")
    b.link(threat, "characters", actor, "The Mentem challenge")
    b.link(threat, "characters", princess, "Freed if the Queen falls")
    _seeds(b)


def _kingdom(b: Builder) -> Neighbour:
    return b.place(
        "The Land of Gold and Glass",
        realm="Faerie",
        known="Hidden",
        status="Hidden",
        summary=paragraphs(
            "A kingdom in the faerie lands, reached by way of mirrors, where "
            "every familiar thing of the mortal world has its counterpart in "
            "warped glass.",
        ),
        secrets=[
            titled(
                "The way in",
                "The completed Frame of Gold, set between two mirrors, is a "
                "corridor to the Land of Gold and Glass (Ant p. 124).",
            ),
            titled(
                "Who meets raiders",
                "Raiders of the Land of Gold and Glass meet the "
                "Undistinguished Warriors, and at the last the Distinguished "
                "Knight (pp. 130-131).",
            ),
            titled(
                STORYGUIDE,
                paragraphs(
                    "The book prints no aura for the kingdom itself; where the "
                    "Queen extends it by Extend Glamour, the area has a Faerie "
                    "aura of 6 (p. 122).",
                    "Faerie Lore of 21+ tells of this kingdom and of its entry "
                    "by mirrors (p. 129).",
                ),
            ),
        ],
    )


def _court(b: Builder, kingdom: Neighbour) -> Neighbour:
    return b.faction(
        "The Court of Gold and Glass",
        faction="Spirits and beings",
        realm="Faerie",
        ruler=QUEEN,
        place=kingdom,
        summary=paragraphs(
            "Old tales speak of a faerie queen whose servants come and go by "
            "mirrors, each one a reflection of some real person, the very "
            "pattern of a place in human society.",
            "Her badge is the mirror. It may be worn, sewn, carried or painted "
            "on an inn sign.",
        ),
        rules=paragraphs(
            "The Distinguished are the Queen's finished servants, one to each "
            "role: Pretenses of 9 in what the role needs, nothing in its "
            "lesser tasks, and a symbolic object holding vis deep in the head "
            "(Ant pp. 129-130).",
            "The Undistinguished are unfinished: Pretense 6, Might 5 to 20, "
            "pieces of the body missing or see-through, but a flawless human "
            "face. None can break a mirror or attack anyone who carries one "
            "(p. 130).",
            "The Hazy Servants have no fixed role and the Shadowy Minions are "
            "hardly there at all (pp. 130-131).",
        ),
        secrets=[
            titled(
                "What the Queen wants",
                "The Queen wants a court magician: faeries who cast as real "
                "magi cast, wear what they wear and sound as they sound "
                "(Ant p. 120).",
            ),
            titled(
                "What a Distinguished Servant is worth",
                "The Queen will ransom a Distinguished Servant as a mortal "
                "monarch would, and is loath to lose one, but spends it if that "
                "draws out interesting spells. A defeat in battle seldom ends "
                "one. Given a ready replacement, she does not care "
                "(Ant p. 130).",
            ),
            titled(
                "The Queen reshapes her servants",
                "The Queen can redesign her lesser faeries (p. 121).",
            ),
            titled(
                "Hirelings and dupes",
                "The Queen uses human hirelings, dupes and captured monsters "
                "as well, because her faeries' powers are alike and would draw "
                "out too few kinds of spell (p. 124).",
            ),
            titled(
                "Faeries who scorn mirrors",
                "Smoothfaces and knockers are no part of the Court of Gold and "
                "Glass, but both scorn mirrors (pp. 127, 129).",
            ),
            titled(
                STORYGUIDE,
                paragraphs(
                    "Many Distinguished Servants have External Vis, which is "
                    "why a defeat in battle seldom ends them (Ant p. 130).",
                    "Highly cognizant faeries such as the Queen can redesign "
                    "their lesser faeries; the book gives this no Virtue, but "
                    "this story rests on it (p. 121).",
                ),
            ),
        ],
    )


def _queen(b: Builder, kingdom: Neighbour) -> Creature:
    return b.creature(
        QUEEN,
        page="pp. 122-123",
        realm="Faerie",
        might=40,
        form="Imaginem",
        size=0,
        tires=False,
        fatigue_levels=TIRELESS,
        place=kingdom,
        block={
            "characteristics": characteristics(3, 0, 3, 1, -1, 0, 1, 0),
            "virtues_flaws": [
                "Attribute Duplication",
                *_times("Greater Power", 4),
                "Highly Cognizant",
                *_times(MAJOR_MIGHT, 2),
                "Faerie Sight",
                "Humanoid Faerie",
                MINOR_MIGHT,
                "Passes for Human",
                "Personal Power",
                "Supernaturally Fragile",
                vf_ward("absolute darkness"),
            ],
            "abilities": [("Order of Hermes Lore", 2, "Arts")],
            "traits": {"Vain": 3, "Cares nothing for mortal suffering": 2},
        },
        attacks=[b.attack("Hands", 0, 2, 2, -1)],
        soak=-9,
        powers=[
            P(
                "Allure",
                1,
                -1,
                "Mentem",
                rtd=("Touch", "Sun", "Ind"),
                level=10,
                does=(
                    "+3 to every roll to impress or convince others. Base 3, "
                    "+1 Touch, +2 Sun."
                ),
            ),
            P(
                "Eidolon",
                2,
                -2,
                "Imaginem",
                rtd=("Touch", "Sun", "Ind"),
                level=20,
                does=(
                    "Makes an illusory figure that moves, acts and speaks at "
                    "her direction, best of all on something reflective. Base "
                    "2, +2 move at direction, +1 Touch, +2 Sun, +1 intricacy."
                ),
            ),
            P(
                "Extend Glamour",
                0,
                0,
                "Mentem",
                rtd=("Touch", "Until (while she remains present)", "Boundary"),
                level=25,
                does=(
                    "Constant. Makes a small mundane area part of her kingdom, "
                    "with no formal boundary needed. There she may change "
                    "anything cosmetic to suit her theme, summon any servant, "
                    "sense all that happens and appear anywhere, and the area "
                    "has a Faerie aura of 6. Fuller in Realms of Power: "
                    "Faerie. Cost marked Special."
                ),
            ),
            P(
                "Guide",
                3,
                -3,
                "Mentem",
                rtd=("Voice", "Conc", "Group"),
                level=30,
                does=(
                    "Nudges the victims toward a course of action; she uses it "
                    "to make humans exercise the skills she means to copy. "
                    "Base 5, +2 Voice, +1 Conc, +2 Group."
                ),
            ),
            P(
                "Hound",
                2,
                -2,
                "Corpus",
                rtd=("Arc", "Conc", "Ind"),
                level=20,
                does=(
                    "Tells her how far off her prey is, and in which "
                    "direction. Base 3, +4 Arc, +1 Conc."
                ),
            ),
            P(
                "Limited Enthrallment",
                4,
                -4,
                "Mentem",
                rtd=("Eye", "Conc", "Ind"),
                level=20,
                does=(
                    "Dominates a victim in a trance with one possible order: "
                    "to gaze at their own reflection without thought. Collapse "
                    "from exhaustion ends it; so does being shaken, or a hand "
                    "passed before the eyes. Printed as costing 20 levels "
                    "from Base 25, +1 Eye, +2 Conc."
                ),
            ),
            P(
                "Spirit Away",
                0,
                0,
                "",
                does=(
                    "Described in Realms of Power: Faerie; no Might cost or "
                    "dice here. Holds the princess in a mirror, lends the "
                    "Queen her form and powers the frame. She uses it no "
                    "further in this story."
                ),
            ),
            P(
                "Travel Through Mirrors",
                0,
                0,
                "Corpus",
                level=25,
                does=(
                    "Lets her step from Faerie into the mortal world through a "
                    "mirror. Fading back is no power but the nature of all "
                    "faeries, though most cannot return so fast. Cost marked "
                    "Greater Powers (Special)."
                ),
            ),
        ],
        vis=[
            BodyVis(8, "Imaginem", "in the shards of the heart-shaped mirror"),
            BodyVis(8, "", "in a gold and glass bead"),
        ],
        equipment=(
            "The finery of a barbarian queen of the time of Rome's expansion, "
            "all of it glamour that passes for mortal goods."
        ),
        appearance=paragraphs(
            "A tall, broad-shouldered woman who looks to be in her early "
            "twenties, red-haired and sharp-eyed, her eyes a vivid blue. Her "
            "cloak seems to be bands of leather and spotted hide by turns, "
            "pinned by a thorn at the right shoulder, over a close, sleeveless "
            "linen dress worked in purple and stout boots tooled along the "
            "tops.",
            "She and all she wears are a little see-through, and paler than "
            "they ought to be.",
        ),
        notes=paragraphs(
            "Wounds as printed (p. 122): -1 (1-5), -3 (6-10), -5 (11-15), "
            "Broken (16-20), Shattered (21+). Her Stamina 0 is supernaturally "
            "tireless. Her Pretenses are any that suit, with Order of Hermes "
            "Lore 2, which is why her challenges miss the mark. Her body and "
            "props, like any faerie's, are not resisted by Parma Magica "
            "(p. 121). " + PRETENSES,
            "Attribute Duplication has no Might cost and needs no Penetration "
            "(p. 121). Her Soak -9 comes of Supernaturally Fragile.",
            "Traditional Ward (absolute darkness): without Realms of Power: "
            "Faerie, she shuns darkness as a vampire shuns garlic. Reflective "
            "surfaces, in her powers, are any that show an outline, not "
            "detail (p. 123).",
            "Without Realms of Power: Faerie (p. 121): she has a role and no "
            "soul, so she must mark her work with repeated insignia, run her "
            "victims through a series of stories and face them at the end, "
            "and cannot sidestep the story, for instance by paying for what "
            "she wants, since she feeds on what they feel along the way.",
        ),
        secrets=[
            titled(
                "The cursed mirror",
                "Long ago, as Rome pushed out over the tribes, a mortal master "
                "made a flawless mirror for the woman he loved. She betrayed "
                "him, and he cursed it and buried it (Ant p. 120).",
            ),
            titled(
                "How she took the princess",
                "A faerie found the cursed mirror and gave it to a princess; "
                "when she looked in, the Queen reached through from Faerie and "
                "took her shape, her life and her place. Since then the Queen "
                "has toyed with mortals and made faerie copies of her foes "
                "(Ant p. 120).",
            ),
            titled(
                "What feeds her",
                "She is a dispenser of labours, a faerie fed by the quests she "
                "sets (p. 120).",
            ),
            titled(
                "Her court magician",
                "Now she wants one or more of her servants shaped into a court "
                "magician, true in every small detail. So she chooses young "
                "magi and goads them: every new spell her servants see or "
                "suffer is one her wizards can then imitate, and she counts a "
                "challenge won if she sees one (p. 120).",
            ),
            titled(
                "Why she spares the magi",
                "She does not want the magi dead, and may aid them against "
                "third parties. She is immortal and patient; they will know "
                "better spells when they are older.",
            ),
            titled(
                "She knows her role",
                "She knows her own role and how far she can exploit it (p. 121).",
            ),
            titled(
                "Why she keeps out of combat",
                "She keeps out of combat for fear of her fragility, and sets "
                "minions to fight for her. She tailors those minions to the "
                "magi's strength and scatters tokens that lead to her, like a "
                "game's final foe (p. 121).",
            ),
            titled(
                "Where her stories come from",
                "She has no originality: her stories take motifs from the "
                "magi's own lives, gathered by her Shadowy Minions (p. 124).",
            ),
            titled(
                "Her weaknesses",
                "Her weaknesses: faeries who cannot bear mirrors (the "
                "smoothfaces, and the knockers, who know much about her); "
                "darkness; her glass body (p. 123).",
            ),
            titled(
                "What her body breaks into",
                "If she is killed, her body breaks into gold-backed glass; the "
                "8 pawns of Imaginem in the largest piece are a decoy "
                "(p. 123).",
            ),
            titled(
                "Her true anchor",
                "Her true anchor is the bead the princess wears, holding 8 "
                "pawns. Unless that vis is taken, she may in time rebuild her "
                "body or move to another object (p. 123).",
            ),
            titled(
                STORYGUIDE,
                paragraphs(
                    "She is highly cognizant (p. 121).",
                    "The book means the troupe to enjoy her game-like tokens, "
                    "and to be rewarded for adding touches that suit it, such "
                    "as a faerie key that opens any lock, or enemies dying in "
                    "a shower of coins (p. 121). Fill her stories with motifs "
                    "from the magi's own lives (p. 124).",
                    "No Art is printed for the bead's 8 pawns (p. 123).",
                ),
            ),
        ],
    )


def _frame(b: Builder, kingdom: Neighbour) -> Creature:
    return b.creature(
        "The Frame of Gold",
        page="pp. 124-125",
        realm="Faerie",
        place=kingdom,
        vis=[BodyVis(8, "Rego", "in the completed frame")],
        powers=[
            P(
                "Spirit Away",
                0,
                0,
                "",
                does=(
                    "Used to carry on the story it was shaped for. The Queen's "
                    "own Spirit Away powers it (p. 122)."
                ),
            ),
        ],
        appearance=("Pieces of what seem to be a gilded picture frame."),
        notes=paragraphs(
            "Intellego Vim finds faerie glamour in a piece, and no vis that "
            "can be used. Completed and set between two mirrors, it is a "
            "corridor to the Land of Gold and Glass; in that form it is a "
            "whole faerie, and holds 8 pawns of Rego (Ant p. 124).",
            "Each piece can sense what is round it, speak to the others, move "
            "when unwatched and quietly influence its surroundings. It may "
            "change the dreams of anyone without Magic Resistance who claims "
            "aloud to own it (p. 125). " + NO_FIGURES,
            "A storyguide may make a separate story of the quest for each "
            "piece, with clues in place of the pieces (p. 124). The pieces can "
            "serve as Arcane Connections to each other (see Breaking the "
            "Story).",
        ),
        secrets=[
            titled(
                "What the frame is",
                "The Frame of Gold is no object but a faerie that longs to be "
                "whole. Its pieces lead their owners into each other's reach "
                "(Ant pp. 124-125).",
            ),
            titled(
                "A lost piece",
                "A piece of the Frame of Gold lost or destroyed does not "
                "matter: the Queen supplies another if she wants the magi to "
                "come (Ant pp. 124-125).",
            ),
            titled(
                STORYGUIDE,
                "The frame is a Threshold Guardian (Ant pp. 124-125).",
            ),
        ],
    )


def _distinguished(
    b: Builder, kingdom: Neighbour, name: str, page: str, notes: str, secrets: Secrets
) -> Creature:
    """A Distinguished Servant the book names, with no block printed."""
    return b.creature(
        name,
        page=page,
        realm="Faerie",
        place=kingdom,
        notes=paragraphs(
            notes,
            "Pretenses of 9 in what the role needs (p. 130). A symbolic object holding vis is embedded deep in its head; the pawns are not printed. "
            + NO_FIGURES,
        ),
        secrets=secrets,
    )


def _servants(b: Builder, kingdom: Neighbour) -> list[Creature]:
    knight = _knight(b, kingdom)
    warriors = _warriors(b, kingdom)
    return [
        knight,
        _distinguished(
            b,
            kingdom,
            "The Distinguished Herald",
            "p. 127",
            "One of the Distinguished Servants (p. 127).",
            [
                titled(
                    "The Herald's errand",
                    "In the Herbam challenge it steals a Gifted child, gives "
                    "it to smoothfaces, then spreads the tale among mortals "
                    "(p. 127).",
                )
            ],
        ),
        _distinguished(
            b,
            kingdom,
            "The Distinguished Huntsman",
            "p. 125",
            "One of the Distinguished Servants (p. 125).",
            [
                titled(
                    "The Huntsman's quarry",
                    "In the Animal challenge he goes after the giant beasts to "
                    "mark the Queen's hand, and looks like a rival for vis "
                    "until the magi learn they hold none (p. 125).",
                )
            ],
        ),
        _distinguished(
            b,
            kingdom,
            "The Distinguished Spy",
            "p. 128",
            "One of the Distinguished Servants (p. 128).",
            [
                titled(
                    "The Spy's training",
                    "The Distinguished Spy is still being perfected: the actor "
                    "of the Mentem challenge is taken off to help (p. 128).",
                )
            ],
        ),
        _distinguished(
            b,
            kingdom,
            "The Distinguished Ambassador",
            "p. 131",
            "One of the Distinguished Servants (p. 131).",
            [
                titled(
                    "The Ambassador's errand",
                    "The Distinguished Ambassador arranges the final meeting "
                    "with magi too dangerous to provoke (p. 131).",
                )
            ],
        ),
        b.creature(
            "The Queen's Steward",
            page="pp. 128, 132",
            realm="Faerie",
            place=kingdom,
            notes=(
                "Named only as the one who gives the actor his new tasks "
                "(p. 128). The book does not say that it is one of the "
                "Distinguished. " + NO_FIGURES
            ),
            secrets=[
                titled(
                    "A new steward",
                    "The Queen is designing a new steward (p. 132).",
                ),
                titled(STORYGUIDE, "See the seed Firebrand Tytalus (p. 132)."),
            ],
        ),
        warriors,
        b.creature(
            "Undistinguished Servants",
            page="p. 130",
            realm="Faerie",
            how_many="Many, filling roles next to those of the Distinguished",
            place=kingdom,
            appearance=(
                "Half made: bits of the body gone or clear as glass, under a "
                "faultless human face."
            ),
            notes=paragraphs(
                "Might from 5 to 20 by how near it is to finished, so the "
                "Might here shows 0. Pretense 6 in the skills most vital to "
                "its role. Powers vary, many of them the Queen's or the "
                "Distinguished Knight's (p. 130). A symbolic object holding vis is wedged in its head; the pawns are not printed.",
                "None can break a mirror or attack someone who carries one.",
            ),
            secrets=[
                titled(
                    "What they are shaped for",
                    "The Undistinguished Servants too are being shaped to "
                    "human roles (p. 130).",
                ),
                titled(
                    "How readily the Queen spends them",
                    "The Queen spends the Undistinguished Servants far more "
                    "readily than the Distinguished (p. 130).",
                ),
            ],
        ),
        b.creature(
            "Undistinguished Magi",
            page="p. 132",
            realm="Faerie",
            how_many=(
                "As suits the story; one per player character is a lot for a short saga"
            ),
            place=kingdom,
            appearance=(
                "Copies of real magi, comic exaggerations at first. After "
                "years of shaping, dressed to hide their flaws, they may fool "
                "even friends."
            ),
            notes=paragraphs(
                "Undistinguished Servants templated on the player magi, or on "
                "two or more at once. They share their models' looks, magic "
                "and strongest Personality Traits. The book prints no "
                "figures, and three ways to choose their spells: list every "
                "spell cast before her minions; note the highest level cast "
                "for each Technique and Form pair; or give only signature "
                "spells, with spontaneous magic to suit (p. 132).",
                "Intellego Vim would unmask one at once, but to cast it on a "
                "magus breaks the Code, and these copies offer no cause "
                "(p. 132).",
            ),
            secrets=[
                titled(
                    "The point of the scheme",
                    "The Undistinguished Magi are the point of the Queen's "
                    "whole scheme.",
                ),
                titled(
                    STORYGUIDE,
                    "See A Faerie Magus? in the last stage of A Run of Odd Troubles.",
                ),
            ],
        ),
        b.creature(
            "Hazy Servants",
            page="pp. 130-131",
            realm="Faerie",
            might=10,
            how_many="Many, at the edges of the court",
            place=kingdom,
            appearance=(
                "Like people glimpsed far off through smoke or fog, until "
                "something greater turns its eye on them, when they spring "
                "into shape."
            ),
            notes=paragraphs(
                "A template: any fitting character from any Ars Magica "
                "supplement, +10 Faerie Might, with powers from the Queen's "
                "or the Distinguished Knight's list. Their Characteristics "
                "shift with their roles (p. 130).",
                "One loses focus when ignored, and there is a small delay "
                "between being noticed and taking shape. They flee bright, "
                "clear light. They alone of her servants can break a mirror, "
                "but seem to die in doing so (p. 131). The Knight's shield "
                "may hold one (p. 130).",
                "They loose the plague of animals (p. 125).",
            ),
        ),
        b.creature(
            "Shadowy Minions",
            page="p. 131",
            realm="Faerie",
            might=1,
            how_many="Many",
            place=kingdom,
            appearance=(
                "Little more than an afterthought or a plan, a shadow given life."
            ),
            notes=(
                "No substance and no powers: they can neither touch a thing "
                "nor attack anyone. They can still spy, and the sight of one "
                "can scare people, set dogs barking or bolt horses (p. 131)."
            ),
            secrets=[
                titled(
                    "What they bring the Queen",
                    "The Shadowy Minions bring the Queen the details of the "
                    "magi's lives that she recycles in her stories (p. 124).",
                ),
                titled(STORYGUIDE, "Faerie Lore of 18+ knows of them (p. 129)."),
            ],
        ),
    ]


def _knight(b: Builder, kingdom: Neighbour) -> Creature:
    return b.creature(
        "The Distinguished Knight",
        page="p. 130",
        realm="Faerie",
        might=25,
        form="Imaginem",
        size=2,
        place=kingdom,
        block={
            "characteristics": characteristics(1, 1, 3, 1, 6, 3, 2, 0),
            "virtues_flaws": [
                "Huge",
                *_times(MAJOR_MIGHT, 4),
                "Faerie Sight",
                "Faerie Speech",
                *_times(GREAT, 2),
                "Humanoid Faerie",
                "Narrowly Cognizant",
                "Observant",
                *_times("Improved Characteristics", 4),
                ("Improved Damage", {"weapon": "sword"}),
                *_times("Personal Power", 3),
                "Puissant Pretense",
                BLINDING_LIGHT,
                ("Sovereign Ward", {"ward": "The Dominion"}),
            ],
            "abilities": [
                ("Area Lore", 9, "the kingdom"),
                ("Awareness", 9, "enemies"),
                ("Brawl", 9, "mortals"),
                ("Charm", 9, "ladies"),
                ("Etiquette", 9, "faerie court"),
                ("Faerie Speech", 6, "taunts"),
                ("Leadership", 9, "tournaments"),
                ("Ride", 9, "horses"),
                ("Single Weapon", 9, "tourney field"),
            ],
            "traits": {"Loyal": 3, "Proud": 3},
        },
        attacks=[
            b.attack("Brawl (gauntlets)", 0, 5, 7, 8),
            b.attack("Great sword and mirrored heater shield", 2, 17, 15, 22),
        ],
        soak=12,
        powers=[
            P(
                "Damaging Effect",
                2,
                -6,
                "Terram",
                level=15,
                does=(
                    "Supernaturally sharp: tiny slivers of glass break away "
                    "and stay in the wound. 2 intricacy points spent on cost. "
                    "Base 5, +1 Part, +1 Diameter; the book says this Base is "
                    "lower than Hermetic magic might suggest."
                ),
            ),
            P(
                "Flight",
                2,
                0,
                "Corpus",
                rtd=("Per", "Sun", "Ind"),
                level=15,
                does=(
                    "Constant. Base 4, +2 Sun, +1 constant, a Base deliberately "
                    "below what Hermetic magic might suggest."
                ),
            ),
            P(
                "Shift Human Shapes",
                0,
                -1,
                "Corpus",
                rtd=("Per", "Mom", "Ind"),
                level=5,
                does=(
                    "He dons or sheds his armour by willing it. 1 intricacy "
                    "point spent on cost. Printed as Base 3, +2 Sun, though "
                    "its Duration is Mom."
                ),
            ),
        ],
        vis=[BodyVis(5, "Imaginem", "a rusty piece from human-sized armor")],
        equipment=(
            "Armour of magical scales of faerie iron, a lance with pennant and "
            "other weapons, an attendant for a squire, and gear bearing the "
            "mirror. His glamour makes a faerie horse."
        ),
        appearance=paragraphs(
            "A towering figure in bright scale armour, who can change into a "
            "very large man of surface charm.",
            "His courtesy outdoes that of the humans he imitates, and he loves "
            "to call them out to duels over tiny failings of conduct.",
        ),
        notes=paragraphs(
            "The great sword's Damage includes +5 for Improved Damage and +5 "
            "for Damaging Effect. Single Weapon is 9+2; the +2 is Puissant "
            "Pretense (the book's Puissant Militant Pretense). The mirrored "
            "shield may hold a Hazy Servant. Charm 9 has limits: he has no "
            "notion of sex. His "
            "horse shares his vis, Might and Magic Resistance and, being "
            "glamour, flies when he does. He has more Pretense experience "
            "than his Virtues permit, which only a player faerie must balance; "
            "he is not designed as one (Ant p. 130). " + PRETENSES,
        ),
        secrets=[
            titled(
                "His place at court",
                "The Queen's champion, and her last guard if her realm is "
                "raided (Ant p. 130).",
            )
        ],
    )


def _warriors(b: Builder, kingdom: Neighbour) -> Creature:
    return b.creature(
        "Undistinguished Warriors",
        page="p. 131",
        realm="Faerie",
        might=20,
        form="Imaginem",
        size=1,
        how_many="Many",
        place=kingdom,
        block={
            "characteristics": characteristics(0, 1, 1, 0, 2, 2, 2, 1),
            "virtues_flaws": [
                "Faerie Sight",
                "Faerie Speech",
                "Humanoid Faerie",
                *_times("Improved Characteristics", 3),
                ("Improved Damage", {"weapon": "varies"}),
                *_times(MINOR_MIGHT, 3),
                "Large",
                "Narrowly Cognizant",
                "Observant",
                *_times("Personal Power", 2),
                BLINDING_LIGHT,
            ],
            "abilities": [
                ("Area Lore", 6, "the kingdom"),
                ("Awareness", 6, "enemies"),
                ("Brawl", 6, "mortals"),
                ("Faerie Speech", 6, "taunts"),
                ("Single Weapon", 6, "as weapon"),
            ],
            "traits": {"Loyal": 2, "Proud": 1},
        },
        attacks=[
            b.attack("Brawl (gauntlets)", 1, 9, 9, 9),
            b.attack("Bow", 0, 12, 10, 13),
            b.attack("Flail", 2, 12, 9, 15),
            b.attack("Greatsword", 3, 14, 10, 16),
            b.attack("Long Spear", 4, 12, 9, 14),
            b.attack("Pole Axe", 2, 14, 8, 18),
            b.attack("Warhammer", 1, 15, 8, 19),
        ],
        soak=10,
        powers=[
            P(
                "Damaging Effect",
                2,
                -6,
                "Terram",
                level=15,
                does=(
                    "Supernaturally sharp: tiny slivers of glass break away "
                    "and stay in the wound. 2 intricacy points spent on cost. "
                    "Base 5, +1 Part, +1 Diameter, a Base below the Hermetic "
                    "norm."
                ),
            ),
            P(
                "Flight",
                2,
                0,
                "Corpus",
                rtd=("Per", "Sun", "Ind"),
                level=15,
                does=(
                    "Constant. Base 4, +2 Sun, +1 constant, a Base deliberately "
                    "below what Hermetic magic might suggest."
                ),
            ),
            P(
                "Shift Human Shapes",
                0,
                -1,
                "Corpus",
                rtd=("Per", "Mom", "Ind"),
                level=5,
                does=(
                    "Dons or sheds armour by will. 1 intricacy point spent on "
                    "cost. Printed as Base 3, +2 Sun, though its Duration is "
                    "Mom."
                ),
            ),
        ],
        vis=[BodyVis(4, "Imaginem", "a rusty piece from human-sized armor")],
        equipment="Armour of magical scales of faerie iron.",
        appearance=(
            "No two are alike: bowman, spearman, swordsman and so on. Some "
            "lack limbs, yet walk without a leg and handle arms without a "
            "hand, and many lack pieces of the head."
        ),
        notes=(
            "Each has one of the six listed weapons, not all; every Damage "
            "includes +5 for Damaging Effect. The Pretense is printed Single "
            "Weapon or Bow 6 (as weapon). They hold more Pretense experience "
            "than their Virtues permit, and are not suitable as player faeries "
            "(Ant p. 131). " + PRETENSES
        ),
    )


def _ice_wyrm(b: Builder) -> Creature:
    return b.creature(
        "Ice Wyrm",
        page="p. 127",
        realm="Faerie",
        might=30,
        form="Animal",
        size=4,
        cunning=True,
        block={
            "characteristics": characteristics(3, -2, -6, -6, 9, 2, 2, -4),
            "virtues_flaws": [
                "Faerie Beast",
                *_times("Greater Power", 2),
                "Huge",
                "Faerie Sight",
                "Improved Characteristics",
                *_times(MINOR_MIGHT, 5),
                ("Personal Power", {"power": "Constant Damaging Effect"}),
                "Incognizant",
            ],
            "abilities": [
                ("Area Lore", 3, "watering points for prey"),
                ("Awareness", 3, "prey"),
                ("Brawl", 7, "crushing"),
                ("Hunt", 4, "rodents"),
                ("Faerie Speech", 5, "threats"),
                ("Folk Ken", 1, "human prey"),
                ("Stealth", 3, "stalking prey"),
            ],
            "traits": {"Inquisitive": 3, "Hungry": 2},
        },
        attacks=[
            b.attack("Fangs", -4, 14, 1, 10),
            b.attack("Constriction", -4, 11, 1, 10),
            b.attack("Claws (if appropriate)", -5, 13, 6, 5),
        ],
        soak=22,
        powers=[
            P(
                "Conjuration of the Indubitable Cold",
                0,
                -4,
                "Ignem",
                does=(
                    "As the spell of that name, ArM5 p. 142. 3 intricacy "
                    "points spent on cost."
                ),
            ),
            P(
                "Constrict",
                0,
                0,
                "",
                does=(
                    "A hit coils round the victim, who cannot use melee "
                    "weapons. Damage then comes each round with no Attack "
                    "roll, but may be Soaked. At the end of each round, the "
                    "first included, the victim may try to escape: Strength + "
                    "stress die against the wyrm's. Each helper adds +1 and "
                    "cannot attack the wyrm that round. Success frees him, to "
                    "attack as normal next round. Six rounds held (30 seconds) "
                    "calls for deprivation rolls, ArM5 p. 179."
                ),
            ),
            P(
                "Constant Damaging Effect",
                3,
                0,
                "Auram",
                level=25,
                does=(
                    "Constant. Its terrible cold deals +5 Damage each round. "
                    "Base 5, +1 Part, +2 Sun, +1 Constant."
                ),
            ),
            P(
                "Spreading a Mantle of Ice",
                0,
                -4,
                "Auram",
                does=(
                    "3 intricacy points spent on cost. All water freezes for a "
                    "mile about it, and any rain falls as snow. The air grows "
                    "so bitter that hunting it takes magic or preparation, "
                    "though spells that sense warmth can find it, always at "
                    "the coldest point. The cold being magical, Auram Magic "
                    "Resistance of 30 or more does not feel it."
                ),
            ),
            P(
                "Venomous Bite",
                0,
                0,
                "",
                does=(
                    "When its Attack Advantage beats the victim's armor "
                    "Protection (not Soak), the victim suffers adder venom "
                    "(Poison Table, ArM5 p. 180), wound or no wound. The "
                    "storyguide may shift the Advantage needed."
                ),
            ),
        ],
        vis=[BodyVis(6, "", "in a piece of lost string")],
        equipment="A small heap of frozen treasure.",
        appearance=(
            "A vast serpent, its slime frozen into hard plates of ice, with "
            "sickly blue skin and eyes like sapphires."
        ),
        notes=paragraphs(
            "Defense is +6 against grapples. A wyrm may grapple its own Size "
            "in Size 0 enemies. Attack Damage leaves out Constant Damaging "
            "Effect, which adds +5 when it applies. Soak is printed as 10, "
            "+12 plates of ice. No Art is printed for its vis (Ant p. 127). "
            + PRETENSES,
            "Printed: the plates neutralize its poison, yet Venomous Bite is "
            "listed; the challenge says seven miles freeze, the power says "
            "one mile.",
        ),
        secrets=[
            titled(
                "What ice wyrms stand for",
                "Ice wyrms stand for the edge between arable land and the "
                "snowy north, or peak and pasture, or the draining of life by "
                "winter (Ant p. 127).",
            ),
            titled(
                "How the wyrm must fall",
                "This ice wyrm must fall to humans in an epic fight that "
                "passes into local legend, and until then it hunts warm life "
                "to drain (Ant p. 127).",
            ),
            titled(
                "How the wyrm came here",
                "The Queen's servants catch the ice wyrm and move it by mirror.",
            ),
            titled(
                "A piece of the frame",
                "A piece of the Frame of Gold lies in the ice wyrm's treasure.",
            ),
            titled(STORYGUIDE, "The ice wyrm is a mastery faerie (Ant p. 127)."),
        ],
    )


def _smoothfaces(b: Builder) -> Creature:
    return b.creature(
        "Smoothface (Basic Soldier)",
        page="p. 126",
        realm="Faerie",
        might=10,
        form="Corpus",
        size=0,
        how_many="A troop",
        block={
            "characteristics": characteristics(-1, 0, -3, 0, 1, 1, 2, 2),
            "virtues_flaws": [
                "Greater Power",
                "Faerie Sight",
                "Humanoid Faerie",
                MINOR_MIGHT,
                "Personal Power",
                "Narrowly Cognizant",
                "Passes for Human",
                ("Personal Power", {"power": "Shift Human Shape"}),
                vf_ward("crowds"),
            ],
            "abilities": [
                ("Area Lore", 3, "lonely places"),
                ("Athletics", 3, "chasing people"),
                ("Awareness", 3, "victims"),
                ("Brawl", 4, "punching"),
                ("Carouse", 3, "luring people outside"),
                ("Charm", 4, "luring people to lonely places"),
                ("Etiquette", 3, "blending in"),
                ("Folk Ken", 4, "fitting in"),
                ("Guile", 5, "victims"),
                ("Single Weapon", 5, "axe"),
            ],
            "traits": {"Enjoys fear": 3, "Jovial": 2},
        },
        attacks=[
            b.attack("Axe and Heater shield", 0, 12, 11, 7),
            b.attack("Brawl", 2, 8, 8, 1),
        ],
        soak=8,
        powers=[
            P(
                "Gripping Fear",
                0,
                -2,
                "Corpus",
                rtd=("Sight", "Sun", "Ind"),
                does=(
                    "Constant. Humans who see the smooth face are seized by "
                    "terror and flee, losing Fatigue. Several may ambush a "
                    "resting victim together, or one may torment it alone "
                    "with Invisibility and Shift Human Shapes. As Panic of the "
                    "Trembling Heart, ArM5 p. 148, +1 constant, +2 intricacy "
                    "points to cut the cost; also printed as ReMe Base 5, +1 "
                    "Eye, +2 Sun, +2 intricacy."
                ),
            ),
            P(
                "Invisibility",
                2,
                -2,
                "Imaginem",
                rtd=("Per", "Sun", "Ind"),
                does="A personal Veil of Invisibility, ArM5 p. 146.",
            ),
            P(
                "Loss of Sense of Direction",
                0,
                -2,
                "Corpus",
                rtd=("Eye", "Sun", "Ind"),
                does=(
                    "A version of Guide, turning a fleeing victim toward some "
                    "deserted spot for another attack."
                ),
            ),
            P(
                "Shift Human Shapes",
                0,
                -1,
                "Corpus",
                rtd=("Per", "Mom", "Part"),
                does=(
                    "It wipes its face away with a hand, or back again, and "
                    "takes other human forms: invisibly it catches a spent "
                    "human, comes as a comfort and scares him afresh. Base 3, "
                    "+2 Sun, +1 intricacy point to cut cost, though its "
                    "Duration is Mom."
                ),
            ),
        ],
        vis=[BodyVis(2, "Corpus", "an eggshell")],
        equipment="As its disguise requires.",
        appearance=(
            "Altogether human until it pleases, when one stroke leaves skin as "
            "bare and white as an eggshell, which still sees and smells."
        ),
        notes=paragraphs(
            "Wounds as printed: 0, -1 (1-5), -1 (6-10), -3 (11-15), -5 "
            "(16-20), Incapacitated (21-25), Dead (26+). Soak includes full "
            "metal scale armor (Ant p. 126). " + PRETENSES,
            "A template: take the character it is pretending to be, then add "
            "10 Might, these Virtues and Flaws (or Infiltrator where it "
            "suits), Personality Traits, Powers and Vis. This example is the "
            "Basic Soldier of ArM5 p. 22. As a player character it needs "
            "higher Characteristics and six Minor Flaws, and may want the "
            "Damaging Effect power (p. 126).",
        ),
        secrets=[
            titled(
                "Whom smoothfaces haunt",
                "Smoothfaces haunt travellers and those who fear strangers, "
                "for sport and vitality (Ant p. 126).",
            ),
            titled(
                "A stolen face",
                "A smoothface who frightens a victim to death may wear that "
                "face (Ant p. 126).",
            ),
            titled(
                "When smoothfaces fight",
                "Smoothfaces fight only to defend themselves (Ant p. 126).",
            ),
            titled(
                "The Gifted child",
                "In the Herbam challenge the smoothfaces mean to keep the "
                "Gifted child, hoping it will draw faces for them "
                "(pp. 126-127).",
            ),
            titled(
                "Smoothfaces and the Queen",
                "Smoothfaces hate mirrors and the Queen hates them; they know "
                "nothing of her, but may be persuaded that she has put them in "
                "peril with her gift, and side with the magi at the end "
                "(pp. 126-127).",
            ),
        ],
    )


def _knockers(b: Builder) -> Creature:
    return b.creature(
        "Knockers",
        page="p. 129",
        realm="Faerie",
        might=5,
        form="Terram",
        size=-2,
        how_many="A band in a mine",
        block={
            "characteristics": characteristics(0, 2, -3, -2, -1, 3, 2, 4),
            "virtues_flaws": [
                ("Immune to {source} (Major)", {"source": "Terram"}),
                *_times(GREAT, 2),
                "Faerie Sight",
                "Faerie Speech",
                "Humanoid Faerie",
                *_times("Improved Characteristics", 2),
                "Intangible Flesh",
                "Observant",
                "Little",
                vf_ward("offerings"),
            ],
            "abilities": [
                ("Athletics", 2, "digging"),
                ("Awareness", 2, "hazards underground"),
                ("Bargain", 5, "with mortals"),
                ("Brawl", 6, "fist"),
                ("Craft (smith)", 5, "weapons"),
                ("Great Weapon", 5, "pick, as pole arm"),
            ],
            "traits": {"Vengeful": 3},
        },
        attacks=[
            b.attack("Brawl (fist)", 4, 9, 11, 3),
            b.attack("Pick/Tool (two handed)", 7, 8, 11, 11),
        ],
        soak=6,
        powers=[
            P(
                "Guide",
                3,
                -3,
                "Mentem",
                rtd=("Voice", "Conc", "Group"),
                level=30,
                does=(
                    "Nudges people toward a course of action: it rewards good "
                    "miners with warnings or the way to ore, and sends bad "
                    "ones astray or into peril. Base 5, +2 Voice, +1 Conc, +2 "
                    "Group."
                ),
            ),
            P(
                "Loosely Material",
                1,
                1,
                "Mentem",
                level=25,
                does=(
                    "Forms a solid body for a time, with all its gear. 2 "
                    "intricacy points cut the Might cost."
                ),
            ),
        ],
        vis=[BodyVis(1, "", "a discarded mining tool")],
        equipment="A miner's working gear.",
        appearance=(
            "Small, insubstantial dwarfs in miners' gear, who pass for the "
            "ghosts of Jewish miners killed underground. They cast no "
            "reflection."
        ),
        notes=paragraphs(
            "Combat totals include +1 for a Pretense specialization. Soak is "
            "printed +6, with Immunity from Terram (Ant p. 129). No Art is "
            "printed for the vis. " + PRETENSES,
            "They warn of cave-ins with their noise, and lead men to good ore "
            "by tapping. They count whistling very rude. They are sincerely "
            "religious, and cannot hold on to the riddle of why death made "
            "them dwarfs for more than a moment.",
        ),
        secrets=[
            titled(
                "Bargaining with knockers",
                "Knockers bargain gladly if approached in peace, above all "
                "with miners and Jews (Ant p. 129).",
            ),
            titled(
                "Oaths for the child",
                "The knockers give up the child for binding oaths that it be "
                "properly raised; break those, and they may undermine the "
                "covenant, shift its underground waters or find other revenges "
                "(Ant p. 129).",
            ),
            titled(
                "What knockers know",
                "Having no reflection, knockers have no use for mirrors, and "
                "they know much about the Queen.",
            ),
            titled(
                "How knockers give the Queen away",
                "Even attacked, knockers can give away the Queen's weakness: "
                "they fight a few rounds with tools and mirrors, cry out that "
                "the mirrors have failed them, and flee through tunnels or "
                "rock.",
            ),
        ],
    )


def _treasures(b: Builder, kingdom: Neighbour) -> dict[str, Neighbour]:
    return {
        "The mirror of her origin": b.place(
            "The Cursed Mirror of the Artisan",
            realm="Faerie",
            known="Hidden",
            status="Lost",
            summary=(
                "A flawless mirror made for a faithless lover in the days of "
                "Rome's first advance, then cursed and put in the ground."
            ),
            secrets=[
                titled(
                    "Who dug up the mirror",
                    "A faerie dug up the Cursed Mirror of the Artisan and gave "
                    "it to the princess, and through it the Queen took her "
                    "(Ant p. 120).",
                ),
                titled(
                    STORYGUIDE,
                    "The book does not say where it is now, or whether it is "
                    "the mirror of the heart.",
                ),
            ],
        ),
        "What she breaks into": b.place(
            "The Heart-Shaped Mirror",
            realm="Faerie",
            known="Hidden",
            status="Hidden",
            inside=kingdom,
            summary=(
                "Gold-backed glass in the shape of a heart, in whose depths a "
                "woman can be seen."
            ),
            secrets=[
                titled(
                    "What the mirror is",
                    "The Heart-Shaped Mirror is the largest piece of the "
                    "Queen's body when she dies (Ant p. 123).",
                ),
                titled(
                    "The woman in its depths",
                    "Characters can reach into the Heart-Shaped Mirror and "
                    "draw out the princess, which shatters it (Ant p. 123).",
                ),
                titled(
                    "The vis in its shards",
                    "The shards of the Heart-Shaped Mirror hold 8 pawns of "
                    "Imaginem in all. This is a decoy, not the Queen's anchor "
                    "(Ant p. 123).",
                ),
            ],
        ),
        "Her true anchor": b.place(
            "The Gold and Glass Bead",
            realm="Faerie",
            known="Hidden",
            status="Hidden",
            inside=kingdom,
            summary=(
                "A bead of gold and glass, the dearest possession of the woman "
                "who wears it."
            ),
            secrets=[
                titled(
                    "Whose spirit it holds",
                    "The Queen's spirit is anchored in the Gold and Glass "
                    "Bead, with 8 pawns of vis (Ant p. 123).",
                ),
                titled(
                    "What the bead does for its wearer",
                    "Wearing the Gold and Glass Bead works as Aura of Rightful "
                    "Authority (Ant p. 123).",
                ),
                titled(
                    "If the vis is left",
                    "Unless the Gold and Glass Bead's vis is harvested, the "
                    "Queen may in time move to another object or rebuild her "
                    "body (Ant p. 123).",
                ),
                titled(STORYGUIDE, "No Art is printed for the bead's vis."),
            ],
        ),
        "Her badge": b.place(
            "Gold-Backed Mirrors",
            realm="Faerie",
            known="Locally",
            summary=paragraphs(
                "Rome made its mirrors of glass with gilded backs. Nobody in "
                "Mythic Europe still does, unless perhaps some magus who keeps "
                "the old imperial crafts. Today's mirrors are steel, silver, polished "
                "marble and, here and there, glass backed with lead.",
                "So a mirror of any sort is scarce and costly, and one backed "
                "in gold stands out.",
            ),
            secrets=[
                titled(
                    "The Queen's name",
                    "The Queen of Gold and Glass takes her name from "
                    "gold-backed mirrors (Ant p. 123).",
                ),
                titled(
                    "The mark of her minions",
                    "A minion who takes a symbolic object for the Queen must "
                    "in time be shown as hers, by the mirror (p. 122).",
                ),
                titled(
                    STORYGUIDE,
                    "Awareness rolls about these mirrors are +3 easier (Ant p. 129).",
                ),
            ],
        ),
        "An old account of her": b.place(
            "A Bonisagus Account",
            realm="",
            known="Locally",
            summary="A centuries-old record by a long-dead magus of House Bonisagus.",
            secrets=[
                titled(
                    "What the account tells",
                    "The Bonisagus account tells of the Queen's earlier "
                    "attempt to make a faerie skilled in the Arts for her "
                    "courtier (Ant p. 129).",
                ),
                titled(
                    STORYGUIDE,
                    "Intelligence + Order of Hermes Lore against an Ease "
                    "Factor of 15 recalls or finds it. If the storyguide "
                    "wishes, the roll also points to The Rare Book "
                    "(Ant p. 129).",
                ),
            ],
        ),
        "A book on her": b.place(
            "The Rare Book",
            realm="",
            known="Hidden",
            status="Hidden",
            summary="A rare book.",
            secrets=[
                titled(
                    "What the book describes",
                    "The Rare Book describes the Queen's powers and "
                    "weaknesses (Ant p. 129).",
                ),
                titled(
                    "Where the book is",
                    "The Rare Book is held, by bad luck, at a reclusive "
                    "covenant far away (Ant p. 129).",
                ),
                titled(
                    STORYGUIDE,
                    "Getting to it makes a separate story, connected but with "
                    "a different theme (Ant p. 129). Neither covenant nor "
                    "book is named.",
                ),
            ],
        ),
    }


def _people(b: Builder) -> tuple[Any, Any]:
    princess = b.magus(
        "The Germanic Princess",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "A barbarian princess of the days of Rome's expansion, tall and "
            "red-haired with piercing blue eyes, and fond above all of a "
            "single gold and glass bead."
        ),
        secrets=[
            titled(
                "Where she is held",
                "She is held in a mirror, in the Queen's realm, and the Queen "
                "wears her form (Ant pp. 122-123).",
            ),
            titled(
                "How she can be freed",
                "If the Queen is killed she can be pulled from the "
                "heart-shaped mirror (Ant pp. 122-123).",
            ),
            titled(
                "Her bead",
                "She wears the bead that is the Queen's real anchor, which "
                "gives her the effect of Aura of Rightful Authority "
                "(Ant pp. 122-123).",
            ),
            titled(
                STORYGUIDE,
                "The book prints no stats and no name. She is held by the "
                "Queen's Spirit Away (Ant pp. 122-123).",
            ),
        ],
    )
    actor = b.magus(
        "The Actor",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "A player of some talent, who has been called away to a new part "
            "by the same patron every few years since his youth."
        ),
        secrets=[
            titled(
                "His first imposture",
                "When he was very young, in his first big role, a patron paid "
                "his way, then had him pose as a grieving husband to get a "
                "locket of hair from a corpse (p. 128).",
            ),
            titled(
                "His patron's returns",
                "Every four years since his first imposture, his patron has "
                "returned with a harder one. The one time he refused, not even "
                "his friends knew him until the job was done (p. 128).",
            ),
            titled(
                "If he is caught",
                "Taken in a nearby town, he confesses all and says he had no choice.",
            ),
            titled(
                "If he is left too long",
                "Left too long, he is taken to another kingdom and set new "
                "tasks by the Queen's Steward, to help perfect her "
                "Distinguished Spy.",
            ),
            titled(STORYGUIDE, "Mortal pawns have no printed stats (Ant p. 124)."),
        ],
    )
    return princess, actor


def _threat(b: Builder) -> Neighbour:
    return dormant(
        b.threat(
            "A Run of Odd Troubles",
            antagonist="Unknown",
            moves="A track",
            summary=(
                "Odd troubles come to the covenant, years apart, with no enemy "
                "to show for them."
            ),
            secrets=[
                titled(
                    "Who is behind the troubles",
                    "The Queen of Gold and Glass has two goals: to run the "
                    "magi through her stories, and to see Hermetic spells of "
                    "every Form, so that her court wizards can imitate them "
                    "(Ant p. 120).",
                ),
                titled(
                    "Why the troubles come years apart",
                    "The Queen sets roughly one story every four years. She "
                    "is immortal; she knows mortals grow, so there is no sense "
                    "in pressing them young; and any faster might sidetrack "
                    "them, for she values spells against faeries less and "
                    "does not want them over-specialized (p. 121).",
                ),
                titled(
                    "One Form to each trouble",
                    "Each of the Queen's stories is tied to one Form, and "
                    "tempts spells of it but forces none (p. 124).",
                ),
                titled(
                    "Subverting the pattern",
                    "The Queen misreads Hermetic magic, so those who see the "
                    "pattern of her stories can subvert it, which obliges her "
                    "to step in herself (p. 124).",
                ),
                titled(
                    "No Vim or Imaginem trouble",
                    "The Queen sets no Vim story, being already a mistress of "
                    "Vim and unwilling to give her minions weapons against "
                    "spirits, and no Imaginem story, thinking it kin to "
                    "glamour and missing its subtler uses (p. 124).",
                ),
                titled(
                    "When the magi do not play along",
                    "If the magi burn the animals with fire, the Queen simply adds "
                    "another Animal story and wonders whether she still needs "
                    "the Ignem one. She rarely knows when the magi have "
                    "reached their limits (p. 125).",
                ),
                titled(
                    "The frame pieces show her hand",
                    "The pieces of the Frame of Gold mark the link between "
                    "the troubles from the second piece on; the Queen wants "
                    "her hand known once she has her symbolic objects "
                    "(pp. 128-129).",
                ),
                titled(
                    "Other victims",
                    "Other victims, whom the Queen's servants introduce during "
                    "The Obvious Liar, tell of repeated challenges that test "
                    "growing skills. Questioning one brings back the event in "
                    "which his symbolic object was taken, and the magi may "
                    "then recall theirs (pp. 128-129).",
                ),
                titled(
                    STORYGUIDE,
                    paragraphs(
                        "Alter the frequency or count of the stories to suit "
                        "the saga (p. 121).",
                        "The stories are printed by Art and may come in any "
                        "order, harder as the magi age. All are suggestions "
                        "(p. 124).",
                        "If the players tire of this, she either leaves them "
                        "alone until they have other interests to exploit, or "
                        "moves to the confrontation (p. 125).",
                        "Questioning another victim is Communication + a "
                        "fitting Ability, Ease Factor 15, and the magi then "
                        "roll to recall their own symbolic objects "
                        "(pp. 128-129).",
                        "Intelligence + Faerie Lore on faeries and mirrors "
                        "(p. 129): 12+ her title, and that her servants travel "
                        "by mirror; 15+ they are reflections of real people, "
                        "epitomes of human roles; 18+ some are shadows and "
                        "reflections who spy; 21+ she has a kingdom in the "
                        "faerie lands entered by mirrors. Intelligence + Order "
                        "of Hermes Lore (Ease Factor 15) finds the Bonisagus "
                        "account.",
                    ),
                ),
            ],
            stages=[
                S(
                    "Marked as her protagonists",
                    at=1,
                    clues=paragraphs(
                        "A notable meeting with one of her minions, memorable "
                        "enough that the magi can later name it as the start. "
                        "She stays out of sight. A mirror about the minion "
                        "marks it as hers, though it need not be stressed: "
                        "embroidered on a surcoat, jumbled in a pocket, or "
                        "painted on an inn sign (Ant pp. 121-123).",
                        "Examples (pp. 123-124): a faerie smith mends a "
                        "magic item for the council's decanter, or a faerie "
                        "knight fights a demon at the magi's side and asks a "
                        "spent Aegis token. A sprite risks itself to steal "
                        "something trivial marked with the covenant's sigil, "
                        "outside the Aegis. A faerie bard offers a game of "
                        "riddles or a wager, the stake being one chosen word "
                        "the losers never say again; winnings only lead to "
                        "more of her servants. A faerie hostess swears not "
                        "to harm her guests and then takes their bathwater "
                        "and beard stubble to her mistress. A country lad, "
                        "sent to fish a year downstream and bring in what he "
                        "draws up, nets hair from the covenant's refuse.",
                    ),
                    ignored=(
                        "She needs symbolic objects for each magus: Arcane "
                        "Connections, or anything that stirs them strongly, or "
                        "items of the covenant that serve for all its members. "
                        "She can make Arcane Connections by speech and gifts "
                        "of food, and shape these into symbolic objects that "
                        "never fade (p. 122)."
                    ),
                ),
                S(
                    "Animal: The Plague of Animals",
                    at=2,
                    clues=(
                        "Hazy Servants loose small beasts foreign to the area, "
                        "which ruin its farming. Some, of a different colour, "
                        "hold a little vis; others are huge and fierce, even "
                        "of gentle kinds, and hold none. The Distinguished "
                        "Huntsman comes after the huge ones and seems a rival "
                        "for the vis (Ant p. 125)."
                    ),
                    ignored=(
                        "The common beasts are wholly natural and can migrate "
                        "through the Aegis. The vis-bearing ones have Might and "
                        "the giants carry a spell-like effect, so those cannot "
                        "cross it."
                    ),
                    stopped=(
                        "She hopes for conjured predators, magical pens and "
                        "direct destruction, to steal. A piece of the frame "
                        "may lie deep in one of the larger beasts."
                    ),
                ),
                S(
                    "Aquam: Unprecedented Flood",
                    at=3,
                    clues=(
                        "Mirrors on the bed of a great river let its water out "
                        "through shiny things in a small town near the "
                        "covenant (Ant p. 125)."
                    ),
                    ignored=(
                        "The longer the land stays soaked, the worse for crops "
                        "and buildings. Her powers hardly pierce the Aegis, so "
                        "trickles from shiny things in the covenant do no "
                        "direct harm, but water once moved is natural and "
                        "seeps in from outside."
                    ),
                    stopped=(
                        "Smash the reflective surfaces, some hard to reach "
                        "against the force of the water, and then deal with "
                        "what remains. A piece of the frame may be in a huge "
                        "sturgeon stranded at the high-water mark."
                    ),
                ),
                S(
                    "Auram: Sickening Vapors",
                    at=4,
                    clues=(
                        "A nearby village falls sick. The foul air comes up a "
                        "well, sent by mirror from a far-off swamp "
                        "(Ant pp. 125-126)."
                    ),
                    ignored="The cloud settles over the village and its corners.",
                    stopped=(
                        "A cover stops it, since the well's surface does not "
                        "reflect in the dark. Magi can treat the sick and "
                        "raise winds to clear the cloud. For good: cover it so "
                        "that light never falls on the water, cast a spell "
                        "with that effect, take the frame piece from the "
                        "sediment, or let down an unbroken mirror."
                    ),
                ),
                S(
                    "Corpus: People are Corpus, Too",
                    at=5,
                    clues=(
                        "Money, not magic: her servants hire pirates, rogues "
                        "and thieves to prey on the roads and ports round the "
                        "covenant (Ant p. 126)."
                    ),
                    ignored=(
                        "At the storyguide's choice she goes on with the "
                        "raids and adds plague corpses in foreign dress, "
                        "hidden in key places. From many lands, they carry "
                        "many deadly diseases, which together wear down the "
                        "people worse than she foresees; she may send help if "
                        "too many die."
                    ),
                    stopped=(
                        "She will be disappointed: magi need no Corpus magic "
                        "to fight people. Beaten, the leader of a skilled, "
                        "well-supplied band gives up a frame piece he swears "
                        "is a great gold nugget; she has clouded his mind so "
                        "he would not lose it."
                    ),
                ),
                S(
                    "Herbam: Stolen Child",
                    at=6,
                    clues=(
                        "Set in a forest in hopes of interesting use of its "
                        "wood. The Distinguished Herald takes a Gifted child, "
                        "gives it to smoothfaces, then gossips among mortals "
                        "that faeries have stolen a baby who could do some "
                        "small wonder (any trick that shows the Gift), so "
                        "that companions carry the tale home (Ant p. 127)."
                    ),
                    ignored="The smoothfaces keep the child to draw faces for them.",
                    stopped=("Return the baby and a frame piece is in its crib."),
                    turned=(
                        "Enemies now, the smoothfaces may become allies at the "
                        "end, if convinced the magi are strong and that the "
                        "Queen's gift has endangered them."
                    ),
                ),
                S(
                    "Ignem: The Ice Wyrm",
                    at=7,
                    clues=(
                        "Her servants catch an ice wyrm and move it by mirror "
                        "to a quiet place near the covenant, and seven miles "
                        "round it slowly freeze (Ant p. 127)."
                    ),
                    ignored="The freeze forces the magi to go looking for it.",
                    stopped=(
                        "Fire magic serves best against the wyrm and its "
                        "weather. A frame piece lies in its little hoard of "
                        "shiny things."
                    ),
                ),
                S(
                    "Mentem: The Obvious Liar",
                    at=8,
                    clues=(
                        "An actor hired by her servant comes to the covenant "
                        "as a merchant seeking his son, lost at a pilgrims' "
                        "stop: blood in the bedding, and a lump of wood matted "
                        "with gore and hair nearby. The real merchant is dead, "
                        "killed by a Distinguished Servant, and little like "
                        "him. The pilgrims recall no boy, but do recall a "
                        "vanished merchant of that name (Ant pp. 127-128)."
                    ),
                    ignored=(
                        "Not caught quickly, the actor is spirited off to "
                        "another kingdom by the Queen's Steward."
                    ),
                    stopped=(
                        "Mentem magic sees through the act, questions the "
                        "pilgrims, or speaks to the ghost of the merchant, "
                        "buried by the road. The frame piece is a deodand at "
                        "the nearest church, taken as the thing that beat a "
                        "pilgrim to death: an object that has killed is sold, "
                        "and the money goes to the family or stays with the "
                        "church, as the clergy's honesty decides."
                    ),
                ),
                S(
                    "Terram: We Did This Already!",
                    at=9,
                    clues=(
                        "The Herbam challenge over again, with knockers from "
                        "a mine as her dupes. She cannot truly invent, and the "
                        "repeat may show the magi that one hand is behind the "
                        "stories (Ant p. 128)."
                    ),
                    stopped=(
                        "The knockers give up the child for oaths that it be "
                        "rightly raised (p. 129)."
                    ),
                ),
                S(
                    "The Land of Gold and Glass",
                    at=10,
                    clues=(
                        "She wants the magi to come to terms with her, or even "
                        "storm her kingdom; the frame is how (Ant pp. 128-129)."
                    ),
                    ignored=paragraphs(
                        "A Faerie Magus? (p. 132): if she succeeds, her faerie "
                        "magi serve as pawns in her later stories. Some "
                        "faeries pose as magi already, and covenants must "
                        "sometimes deal with them lest lords or the Church "
                        "blame the Order, but hers cast, dress and speak with "
                        "uncanny accuracy, and only a Code-breaking Intellego "
                        "Vim gives them away.",
                    ),
                    stopped=paragraphs(
                        "Combat (pp. 129-131): her subjects rally to her, the "
                        "Undistinguished Warriors and at the last the "
                        "Distinguished Knight. Kill her and the princess "
                        "can be freed. Take the bead's vis too, or she returns.",
                        "Too Boring (p. 131): magi who refuse the bait and "
                        "stay in their laboratories are left alone; she wants "
                        "no recluse for a servant. It is the least satisfying "
                        "end and the easiest.",
                        "Too Powerful (p. 132): those able to raid her "
                        "kingdom may use the frame; if they are very "
                        "destructive she takes more care in provoking them.",
                    ),
                    turned=paragraphs(
                        "Too Clever (p. 131): she plays this game with other "
                        "mortals too, and magi who keep interfering force her "
                        "to terms.",
                        "Too Dangerous (p. 131): if her spies report that they "
                        "can destroy strong faeries, the Distinguished "
                        "Ambassador arranges a meeting and she offers a "
                        "lasting peace, and asks their help to get objects of "
                        "their replacements: it is easier for magi to walk "
                        "through a target's Aegis. They must leave a common "
                        "mirror in place of what they take, and she tells "
                        "them how she took theirs.",
                        "Too Involved in Other Realms (pp. 131-132): those "
                        "regularly aided by angels or demons are beyond her "
                        "copying. She lets diabolists sink, with the frame "
                        "pieces ordered away or into Deep Faerie, and keeps "
                        "watch on the godly, whose piety may fail with time.",
                        "Too Interesting (p. 132): some truly epic work draws "
                        "enough powerful faerie onlookers that she stops, so "
                        "as not to disappoint them.",
                        "Too Useful (p. 132): magi who see through it can "
                        "offer terms. A Merinita undergoing Becoming would be "
                        "ideal, perhaps as the power behind her throne, or to "
                        "redefine her role. More modestly, her minions serve "
                        "and observe the magi as allies. She will not "
                        "propose it herself, since models who know change "
                        "the copy, but may be drawn by new kinds of human, or "
                        "by objects of other magi whom they then challenge "
                        "with her help.",
                    ),
                ),
            ],
        )
    )


def _seeds(b: Builder) -> None:
    dormant(
        b.threat(
            "Breaking the Story",
            antagonist="Unknown",
            summary=(
                "A strange place where a story seems to be waiting to happen: "
                "people say the same few lines over and over, walk fixed "
                "paths, and do not see that bits of the scenery are missing."
            ),
            secrets=[
                titled(
                    "Where the frame pieces lead",
                    "Used as Arcane Connections to each other, the pieces of "
                    "the Frame of Gold can bring the magi to one of the "
                    "Queen's stories before it is ready, to wreck it and enjoy "
                    "a bizarre half-built setting (Ant p. 124).",
                ),
                titled(
                    STORYGUIDE,
                    "Played straighter, the setting is normal and the people "
                    "unsure why they are there. To rule this out, keep the "
                    "unfound pieces in Faerie, each let out only as its story "
                    "begins (Ant p. 124).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Firebrand Tytalus",
            antagonist="A young Tytalus magus",
            summary=(
                "A young Tytalus magus is at war with a local king, driving "
                "him and his people to their limits in the name of growth. It "
                "breaks the Code, and the Guernicus sent to look into it has "
                "been ambushed and shamed."
            ),
            secrets=[
                titled(
                    "Who the Tytalus is",
                    "The young Tytalus magus is a duplicate (Ant p. 132).",
                ),
                titled(
                    "What the Queen wants of the king",
                    "The Queen of Gold and Glass is designing a new steward, "
                    "and uses the duplicate Tytalus to stretch the mortal who "
                    "governs the kingdom (Ant p. 132).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Blood of the Glass",
            antagonist="Unknown",
            summary=(
                "A woman arrives to demand a baby bond, or the local "
                "equivalent, for a child she says one of the magi fathered. "
                "None of them knows anything about it."
            ),
            secrets=[
                titled(
                    "The child's blood",
                    "The child has very strong faerie blood of a new kind, and "
                    "can make many kinds of imperishable Arcane Connection, as "
                    "the Queen of Gold and Glass can (Ant p. 132).",
                ),
                titled(
                    "What the child is worth",
                    "The child is a source of guaranteed Insight for Original "
                    "Research, and useful in Wizard's Marches (Ant p. 132).",
                ),
                titled(
                    STORYGUIDE,
                    "The child has Faerie Blood of a new kind. Do the magi let "
                    "this be known? (Ant p. 132).",
                ),
            ],
        )
    )
