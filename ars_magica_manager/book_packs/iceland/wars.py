"""The Icelandic Wars, a digital supplement to Land of Fire & Ice (Fourth
Edition, all 15 pages), in paraphrase.

The book is an outline for a storyguide: every line of it is future or
hidden, so public text is kept to what a magus could know in 1220 and the
rest sits in secrets and dormant stories.

- The dormant threat "The Icelandic Wars", on fixed dates at the book's
  years only: the Bergen Expedition (1214, already past, so it is marked
  Happened and beginning the story leaves the later years alone), the
  ghost (1224), the War Tribunal (1230) and the armada (Summer 1232). The
  stages after that carry no year, as the book prints none.
- Each of the book's story seeds is a dormant threat of its own, named
  "Icelandic Wars: ...", with stages where the book orders events.
- People: Hadrianus, Julius, Lavinia and Albinus, with Gunnar Loftursson,
  Asta and Vigdis. None has a stat block in the book.
- Creatures: the four blocks it prints (Vindsvall, the Gray Bull, the
  Host and Gull Hellirsson), by the pack's readings (see the package
  docstring), Abilities renamed. The old Fatigue column and the Body
  levels are kept in the notes.
  The Jotunn magic of Gull's block is kept in words, not converted.
- Places and factions the book names and no other part of this pack
  makes. Records of other parts (Pan Caudarax, Bard, Biorn Egilsson,
  Bishop Magnus, Skalholt, the hreppur, Vindolanda) are found by name for
  links, and skipped when missing.
- Links across both books: this part runs last, so it ties each story to
  its cast and the people to each other (`CAST`, `TIES`).

Where Land of Fire & Ice differs (Hadrianus's voyage in 1214 against the
ship of 1218, the Bull's size and how fast it grows) both are kept, in
secrets."""

from __future__ import annotations

from typing import Any

from ...models import Creature, Neighbour
from ...rules.sites import PLACE
from ..builder import Builder, characteristics, dormant, paragraphs

S = Builder.stage
DATED = "Fixed dates"
PAGE = "Icelandic Wars p. {}"
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
EX_MISC = "house_ex_miscellanea"
#: The stage a past event is given, so that Begin This Story moves nothing.
HAPPENED = "Happened"

FURIOUS = (
    "All three are Furious Attacks, which can strike several foes in one "
    "round with no penalty."
)
CRUSADERS = "The crusaders of the Order of Hermes"
CRUSADE_FOES = "The guardians, the galdramen and the giants of Iceland"


def _neighbour(b: Builder, *names: str) -> Neighbour | None:
    """The record of the first of `names` another part made, if any."""
    for name in names:
        for neighbour in b.saga.neighbours:
            if neighbour.name == name:
                return neighbour
    return None


def _link(record: Any, kind: str, target: Any, note: str) -> None:
    """A link to a record that may be missing."""
    if target is not None:
        Builder.link(record, kind, target, note)


def _replace_sketch(b: Builder, creature: Creature) -> None:
    """Put a printed block in the place of another part's sketch of the
    same creature: it keeps the sketch's id, so links to it hold, and
    takes its secrets and home."""
    for sketch in b.saga.creatures:
        if sketch.name == creature.name and sketch is not creature:
            creature.id = sketch.id
            creature.secrets = paragraphs(sketch.secrets, creature.secrets)
            creature.place_id = sketch.place_id or creature.place_id
            creature.place_level = sketch.place_level
            b.saga.creatures.remove(sketch)
            return


def build(b: Builder) -> None:
    places = _places(b)
    people = _people(b)
    factions = _factions(b, people)
    creatures = _creatures(b)
    war = _war(b)
    _link_war(b, war, places, people, factions, creatures)
    _seeds_before_the_sailing(b)
    _seeds_of_the_voyage(b)
    _seeds_of_the_foothold(b)
    _seeds_of_the_ending(b)
    _link_saga(b)


# -- places --


def _places(b: Builder) -> dict[str, Neighbour]:
    return {
        "bergen": b.town(
            "Bergen",
            summary="A Norwegian port with ships bound for Iceland.",
            secrets="Hadrianus and his two filii took ship here (Icelandic Wars "
            "p. 1); Land of Fire & Ice p. 70 also sails a ship of Flambeau "
            "magi from here. This is not the Bergen on Rügen.",
        ),
        "island": b.place(
            "The Haunted Scottish Island",
            summary="One of the Scottish isles, unnamed, which islanders say "
            "is haunted.",
            secrets="The drowned body of Hadrianus came ashore here and his "
            "spirit walks the island. In 1224 a magus of Loch Leglean meets "
            "it and hears its broken story; having told it, the spirit rests "
            "(Icelandic Wars p. 2).",
            realm="",
            status="Rumoured",
        ),
        "durenmar": b.place(
            "Durenmar",
            summary="The domus magna of House Bonisagus, in the Black Forest.",
            secrets="In 1230 Lavinia calls the War Tribunal here, open to all "
            "with an interest, to debate and organise a crusade against "
            "Iceland (Icelandic Wars p. 2).",
            realm="",
        ),
        "sinus_wodinis": b.place(
            "Sinus Wodinis",
            summary="A covenant of House Bjornaer on an island off the "
            "southeast coast of Norway, long out of touch with the Order. Its "
            "magi dislike strangers.",
            secrets="The Mythic Seas pp. 62-63 prints it. "
            "Crusaders may send to it for Bjornaer help; its magi may "
            "be allied with Norse wizards, and one may be a trollson "
            "(Icelandic Wars p. 9). The Mythic Seas sets it on a frozen bay "
            "of the southern coast, not an island.",
            realm="",
            status="Rumoured",
        ),
        "harbor": b.place(
            "The Southeastern Harbor",
            summary="A bay on Iceland's southeastern quarter, where a ship can anchor.",
            inside=_neighbour(b, "Iceland"),
            secrets="The armada's surviving ship drops anchor here, and if "
            "the Gray Bull is free it charges into the bay (Icelandic Wars "
            "p. 8).",
            realm="",
        ),
        "tower": b.place(
            "The Crusaders' Mystic Tower",
            summary="A very remote part of Iceland's southeastern highlands, "
            "in a valley with mountains around it.",
            inside=_neighbour(b, "Iceland"),
            secrets=paragraphs(
                "Once the crusade lands (or Bjornaer magi carry the materials "
                "ashore) a Hermes Portal is secretly set up here; a strong "
                "force comes through, conjures a Mystic Tower and casts an "
                "Aegis of the Hearth, and hunts Iceland's magicians from it "
                "(Icelandic Wars p. 9).",
                "Julius's magi keep Gull's son here, alive through his "
                "External Soul, and cut him for vis (p. 11). Gull's hammer "
                "needs seven strikes to break the Aegis; if it falls, over a "
                "hundred giants cross the valley and the host tears the "
                "tower apart (p. 12).",
            ),
            realm="",
            status="Rumoured",
            known="Locally",
        ),
    }


# -- people --


def _people(b: Builder) -> dict[str, Any]:
    hadrianus = b.magus(
        "Hadrianus of Flambeau",
        covenant=None,
        house=FLAMBEAU,
        age=None,
        summary="An archmagus of House Flambeau, teacher of two filii.",
        secrets=paragraphs(
            "In 1214 he heard of magicians working from Iceland and sailed "
            "from Bergen with his two filii. Their hostility roused the "
            "landvaettir watchers, and Pan Caudarax burned the ship. The "
            "filii died at once. Hadrianus lived through the flame and "
            "killed a band of landvaettir, then botched a spell and fell "
            "into brief Twilight, and was thrown in the sea and drowned "
            "(Icelandic Wars pp. 1-2).",
            "His ghost haunts a Scottish island until 1224, when it tells a "
            "magus of Loch Leglean, incoherently, that forces of the Order "
            "of Odin killed him, and rests. A summoning to learn more sends "
            "him into Final Twilight (p. 2). He spoke of a dragon and other "
            "beasts, not of spirits, as the landvaettir took solid form to "
            "reach him past his Parma (p. 6).",
            "Land of Fire & Ice p. 70 tells a like story with no names: in "
            "1218 powerful Flambeau magi on a ship from Bergen drew the "
            "dragon's fire, and Einar Gamlisson's wife and sons died with "
            "them. Both are kept; a troupe using both should make it one "
            "ship or two.",
        ),
    )
    julius = b.magus(
        "Julius of Flambeau",
        covenant=None,
        house=FLAMBEAU,
        age=None,
        summary="An archmagus of House Flambeau, an Ignem specialist, whose "
        "strongest spells are made for hunting renounced magi.",
        secrets=paragraphs(
            "After 1224 he rises to prominence and, with Lavinia, prepares "
            "the invasion of Iceland (Icelandic Wars p. 2). He is only "
            "average in Vim, and his Perdo Vim spells are against demons, "
            "not magical spirits (p. 6).",
            "He beats the senior opponent of the crusade in certamen at the "
            "War Tribunal (p. 4), burns Biorn Egilsson as he asks to talk "
            "(p. 9), and leads the hoplites against Vindolanda (p. 12). If "
            "Bard wins and Julius lives, he is taken at sunset and given to "
            "the Yfel lords (p. 13).",
        ),
    )
    lavinia = b.magus(
        "Lavinia of Guernicus",
        covenant=None,
        house=GUERNICUS,
        age=None,
        summary="An archmaga and Quaesitor of House Guernicus, an Intellego "
        "specialist skilled in wards and necromancy.",
        secrets=paragraphs(
            "With Julius she prepares the invasion, calls the War Tribunal at "
            "Durenmar in 1230 and declares it legal and binding (Icelandic "
            "Wars pp. 2, 4). She has no offensive spells against magical "
            "spirits (p. 6).",
            "If the hreppur swears the Oath she answers that joining a House "
            "needs its primus's consent, and demands the prima of Ex "
            "Miscellanea approve each candidate, knowing the prima will see "
            "no one (p. 4). She has witches' hearts brought to her to "
            "question their ghosts (p. 10). Her own divinations slowly show "
            "that Iceland's magicians knew nothing of any Order of Odin "
            "(p. 12).",
        ),
    )
    albinus = b.magus(
        "Albinus of Ex Miscellanea",
        covenant=None,
        house=EX_MISC,
        age=None,
        summary="An archmagus of House Ex Miscellanea, a Theban spirit master.",
        secrets=paragraphs(
            "His spells can beat the guardians. If support for the crusade "
            "holds he sails with it, drives off the Host and can bottle "
            "Vindsvall; he has an even chance of stopping the Gray Bull "
            "(Icelandic Wars pp. 7-8).",
            "If support is undermined he withdraws. If Lavinia rebuffs the "
            "hreppur he goes to Iceland, affirms its membership to the "
            "guardians and Biorn Egilsson, and with a laboratory from "
            "Vindolanda can make them magics against the crusade (p. 7). If "
            "the hreppur joins the Order he works to bring galdor into "
            "Hermetic Theory (p. 15).",
        ),
    )
    gunnar = b.magus(
        "Gunnar Loftursson",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="A bondi of Snaefellsnes, warden of the local church, married "
        "to the galdrakona Asta.",
        secrets="A neighbour of Dagverdara. His young daughter falls gravely "
        "ill during the war, and he rides to the magi for ond (Icelandic Wars "
        "p. 10).",
    )
    asta = b.magus(
        "Asta",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="A young galdrakona, wife of Gunnar Loftursson, with a fylgja.",
        secrets="Crusaders mark her for death. Warned by her fylgja, she "
        "keeps singing the spell that holds a Biarg spirit at her daughter's "
        "side from inside the church (Icelandic Wars p. 10).",
    )
    vigdis = b.magus(
        "Vigdis",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary="A Norn lady, a landvaettir lady of the Orlog spirits.",
        secrets="With Bard and Gull she warns Vindolanda that Julius has "
        "found Scartaris and will strike in three days, and she can give each "
        "magus a landvaettir attendant of Might 50 (Icelandic Wars pp. "
        "11-12).",
    )
    return {
        "hadrianus": hadrianus,
        "julius": julius,
        "lavinia": lavinia,
        "albinus": albinus,
        "gunnar": gunnar,
        "asta": asta,
        "vigdis": vigdis,
    }


# -- factions --


def _factions(b: Builder, people: dict[str, Any]) -> dict[str, Neighbour]:
    odin_hidden = (
        "The Icelandic Wars keeps it a phantom: a century of rumour and "
        "destroyed spring covenants in Norse lands drive the Order's fear, "
        "searches find only weak hedge wizards who have never heard the "
        "name, and neither Pan Caudarax nor any Icelandic magician knows of "
        "it. Who destroyed those covenants the book never says (Icelandic "
        "Wars pp. 1-3, 12)."
    )
    odin = _neighbour(b, "The Order of Odin")
    if odin is None:
        odin = b.faction(
            "The Order of Odin",
            summary="The rival order of Norse wizards that rumour has "
            "whispered of in the Order of Hermes for over a century. Magi "
            "credit it with destroying spring covenants in Scandinavia, and "
            "think its powers of concealment may be infernal.",
            secrets=odin_hidden,
        )
    else:
        odin.secrets = paragraphs(odin.secrets, odin_hidden)
    crusaders = b.faction(
        "The Hermetic Crusaders",
        summary="Magi of Houses Flambeau and Guernicus who want action "
        "against the Norse wizards.",
        secrets=paragraphs(
            "Led by Julius and Lavinia, for idealism, glory or vis. With "
            "strong support the force is twelve powerful hoplites and twenty "
            "moderately powerful magi, mostly Flambeau, with Albinus and a "
            "hundred well-equipped grogs a ship beyond the crew. If support "
            "is undermined Albinus, six hoplites and five other magi stay "
            "home; if the hreppur was rebuffed, eight hoplites and ten other "
            "magi leave it, and Albinus turns against them (Icelandic Wars p. 7).",
            "They carry spells for killing huge beasts and vis to pierce any "
            "resistance, but know nothing of spirits unless told (pp. 6, 8).",
        ),
        faction="Other",
        ruler="Julius of Flambeau and Lavinia of Guernicus",
        wants="Revenge for Hadrianus, and the end of the Order of Odin",
    )
    doubters = b.faction(
        "The Magi Against the Crusade",
        summary="Magi who say the Order of Odin is a myth, and are threatened "
        "for it by Flambeau and Guernicus magi as traitors.",
        secrets="Older magi stand ready against a real threat and have no "
        "time for childish adventures. If the player characters argue well "
        "many powerful magi withdraw, and after the War Tribunal some pledge "
        "to take the matter to the Grand Tribunal (Icelandic Wars pp. 3-4).",
        faction="Other",
    )
    leglean = b.faction(
        "The Loch Leglean Tribunal",
        summary="The Order's Tribunal in Scotland.",
        secrets="One of its magi looks into the haunting of Hadrianus in 1224 "
        "(Icelandic Wars p. 2).",
        faction="Other",
    )
    Builder.link(crusaders, "characters", people["julius"], "Leads it")
    Builder.link(crusaders, "characters", people["lavinia"], "Leads it")
    Builder.link(crusaders, "neighbours", odin, "Their pretext")
    return {
        "odin": odin,
        "crusaders": crusaders,
        "doubters": doubters,
        "leglean": leglean,
    }


# -- creatures --


def _creatures(b: Builder) -> dict[str, Creature]:
    iceland = _neighbour(b, "Iceland")
    spiritual_form = (
        "Takes solid form or none at will, and travels at a hundred times "
        "its speed while immaterial."
    )
    vindsvall = b.creature(
        "Vindsvall",
        page=PAGE.format(5),
        realm="Magic",
        might=75,
        form="Auram",
        size=6,
        cunning=True,
        confidence=CONFIDENCE,
        place=iceland,
        block={
            "characteristics": characteristics(5, 10, 0, 0, 10, 15, 15, 15),
            "traits": {"Fierce": 3, "Brave": 6, "Cunning": 3},
            "reputations": {"Guardian (Icelandic magicians)": 3},
        },
        attacks=[
            b.attack("Bite", 25, 20, 14, 30),
            b.attack("First Claw", 20, 20, 14, 20),
            b.attack("Second Claw", 20, 20, 14, 20),
        ],
        soak=41,
        fatigue_levels="OK, 0, 0, 0, -1, -1, -1, -3, -3, -5, -5, Unconscious",
        powers=[
            b.power(
                "Weather Mastery",
                0,
                15,
                "Auram",
                level=60,
                does="Makes any weather up to 12th magnitude. CrAu, ReAu.",
            ),
            b.power("Spiritual Form", 0, 15, "Vim", level=40, does=spiritual_form),
        ],
        appearance="A vast eagle the colour of a storm sky, whose wings seem "
        "to touch both sides of the heavens; beak and talons shine like "
        "lightning, and its wingbeats sound like thunder.",
        notes=paragraphs(
            "The second guardian of Iceland, a spirit as old as the land, "
            "bound by the ancients against hostile magic. Very cunning, yet "
            "an animal in mind: it cares only for what touches its duty.",
            f"{FURIOUS} Body levels as printed: OK, 0, 0, 0, -1, -1, -1, -3, "
            "-3, -5, -5, Incapacitated. Each attack's old Fatigue total was "
            "+20. The Might Form is the pack's reading of its powers. Land of "
            "Fire & Ice p. 112 gives it a wingspan of over 50 feet.",
        ),
    )
    bull = b.creature(
        "The Gray Bull",
        page=PAGE.format(6),
        realm="Magic",
        might=80,
        form="Animal",
        size=8,
        cunning=True,
        confidence=CONFIDENCE,
        tires=False,
        place=_neighbour(b, "Skalholt") or iceland,
        block={
            "characteristics": characteristics(0, 5, 0, 0, 30, 30, 5, 5),
            "traits": {"Fierce": 6, "Brave": 6, "Single Minded": 6},
            "reputations": {"Guardian (Icelandic magicians)": 3},
        },
        attacks=[
            b.attack("Gore", 20, 20, 7, 58),
            b.attack("First Kick", 15, 20, 7, 48),
            b.attack("Second Kick", 15, 20, 7, 48),
        ],
        soak=68,
        fatigue_levels="Tireless",
        powers=[
            b.power(
                "Shapeshift",
                0,
                5,
                "Animal",
                level=40,
                does="Changes its size at will from +2 to +8; away from its "
                "duty it roams the highlands at +2.",
            ),
            b.power("Spiritual Form", 0, 5, "Vim", level=40, does=spiritual_form),
        ],
        appearance="Today a big bull of the Norse breed with a near-white "
        "coat. Freed from the Dominion, a vast aurochs.",
        notes=paragraphs(
            "The third guardian of Iceland, wandering the highlands for "
            "millennia until the Norse brought cattle. In 1105 it strayed "
            "into the fields of Skalholt after the bishop's cows, stayed too "
            "long in the Dominion, lost its power and was caught. It ages "
            "and dies, and its spirit passes to a gray bull calf of its own.",
            "The block is its full power, Might 80 and Size +8. While the "
            "Dominion holds it, its Might is 20 and its Size +2.",
            "Only the Gore is ordinary; both Kicks are Furious Attacks that "
            "can strike several foes in a round with no penalty. Body levels "
            "as printed: OK, 0, 0, 0, -1, -1, -1, -3, -3, -3, -5, -5, -5, "
            "Incapacitated. The Might Form is the pack's reading of its "
            "powers.",
        ),
        secrets="The Icelandic Wars has it stand over 120 feet at the "
        "shoulder and regain its full size within minutes once out of the "
        "Dominion, fed by the Host (pp. 7-8). Land of Fire & Ice has it the "
        "size of a house (p. 7) and growing over weeks (p. 112). Both are "
        "kept.",
    )
    host = b.creature(
        "The Guardian Host",
        page=PAGE.format(7),
        realm="Magic",
        might=20,
        how_many="Around two thousand form the Host, with endless more to "
        "replace the slain",
        place=iceland,
        block={"traits": {"Fierce": 6}},
        powers=[
            b.power(
                "Spell Powers",
                0,
                0,
                "Vim",
                does="Each spirit can make a spell effect of a level equal to "
                "its permanent Might. Art and cost vary.",
            ),
            b.power(
                "Grant Might",
                0,
                0,
                "Vim",
                does="Gives the guardian temporary Might points. CrVi.",
            ),
            b.power(
                "Heal Guardian",
                10,
                0,
                "Corpus",
                does="Heals the guardian one Health level for every 10 Might "
                "spent, by touch. CrAn or CrCo.",
            ),
            b.power("Spiritual Form", 0, 0, "Vim", level=40, does=spiritual_form),
            b.power(
                "Shapeshift",
                0,
                0,
                "Vim",
                level=20,
                does="Takes any form it likes, fighting while solid as a "
                "Beast of Virtue of that kind; a landvaettir of Might 40 or "
                "more can become a fantastic beast of like Might.",
            ),
        ],
        notes=paragraphs(
            "A template, not a full block: Might 20 to 50 (the pack enters "
            "the lowest) and Size -5 to +3, Characteristics varying. Its "
            "spirits obey the guardian of the moment without question and "
            "with no thought for themselves, healing it, feeding it Might or "
            "fighting.",
            "Its look changes with each guardian; Land of Fire & Ice pp. 7 "
            "and following describes them.",
        ),
    )
    gull = b.creature(
        "Gull Hellirsson",
        page=PAGE.format(11),
        realm="Magic",
        might=68,
        form="Ignem",
        size=6,
        age="Irrelevant",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(3, 1, -1, 0, 23, 22, 2, 5),
            "abilities": [
                ("Survival", 7, "volcanoes"),
                ("Athletics", 5, "mountains"),
                ("Great Weapon", 14, "warhammer"),
                ("Thrown Weapon", 10, "molten metal"),
                ("Living Language: Jotunn", 12, "Clan of Geirrod"),
            ],
            "traits": {"Friend of Man": -2, "Calculating": 3, "Violent": 1},
            "reputations": {
                "Leader of fire giants (Icelandic giants)": 3,
                "Suicidal to cross (trolls)": 4,
            },
        },
        attacks=[
            b.attack("Warhammer", 30, 27, 19, 48),
            b.attack("Thrown Molten Gold", 20, 13, 0, 50),
        ],
        soak=48,
        fatigue_levels="OK, 0, 0, 0, -1, -1, -1, -3, -3, -5, -5, Unconscious",
        equipment="A full coat of scale mail, each scale over an inch thick "
        "(the Soak counts it), and a dwarf-forged warhammer whose head "
        "weighs over 1000 pounds.",
        powers=[
            b.power(
                "Jotunn Spells",
                0,
                5,
                "Ignem",
                does="Works some fire effects directly, without calling on "
                "Jotunn spirits, with Stamina in place of Communication in "
                "his Jotunn Affinity casting total. CrIg, Te varies. His "
                "favourite conjures molten gold that he handles unharmed and "
                "throws.",
            ),
            b.power(
                "Immunity to Fire",
                0,
                5,
                "Ignem",
                does="His Jotunn Affinity has made him proof against all heat "
                "and flame.",
            ),
            b.power(
                "Break Wards",
                0,
                5,
                "Vim",
                level=100,
                does="A power of the hammer, which must strike the target. "
                "The first blow dispels wards of 8th magnitude or less and "
                "breaks any barrier they guard; each later blow reaches a "
                "magnitude higher, to 20th. PeVi, Te.",
            ),
        ],
        appearance="A stern giant with golden hair and strange black eyes.",
        notes=paragraphs(
            "Leader of the fire giants. He cares nothing for dead galdramen "
            "or men in general. His rage is plain in the air around him, but "
            "he keeps it mastered.",
            "As printed, in words and not converted: Jotunn Affinity with "
            "Fire 20 (molten metal), Shapeshift 19 (dragons), Transform 9 "
            "(trolls), External Soul, Potency 12 (Jotunn Affinity). Climb 5 "
            "is Athletics.",
            "Molten gold: on the next round +35 fire damage, 5 less on each "
            "round after; anyone within 12 feet takes +20 the first round, "
            "+15 the second and so on. It is magical, so Magic Resistance "
            "counts, and turns to dust at sunrise or sunset. No Defense is "
            "printed for it. Old Fatigue totals: Warhammer +37, gold +33. "
            "Body levels as printed: OK, 0, 0, 0, -1, -1, -1, -3, -3, -5, -5, "
            "Incapacitated. The Might Form is the pack's reading of his fire.",
        ),
        secrets="A Hermetic scouting party attacked his son's regio home, "
        "killed his two granddaughters and took his son's beaten body to "
        "their tower. The son lives through his External Soul, and the magi "
        "cut him for vis; Gull takes it for a depraved game and wants Julius's "
        "forces dead (Icelandic Wars p. 11).",
    )
    _replace_sketch(b, vindsvall)
    clan = _neighbour(b, "The Clan of Geirrod")
    _link(gull, "neighbours", clan, "Speaks its Jotunn; leads the fire giants")
    return {"vindsvall": vindsvall, "bull": bull, "host": host, "gull": gull}


# -- the war --


def _war(b: Builder) -> Neighbour:
    bergen = S(
        "The Bergen Expedition",
        year=1214,
        clues="For over a century rumours of a Norse order and the loss of "
        "spring covenants in Scandinavia have fed the Order's fear; each "
        "search has found only weak hedge wizards. In 1214 Hadrianus hears "
        "of a great society of magicians on Iceland.",
        ignored="The landvaettir watchers sense the ship's intent and tell "
        "Pan Caudarax, who burns it. Hadrianus's filii die; he kills a band "
        "of landvaettir, falls into Twilight on a botched spell and is "
        "drowned. His body drifts to a Scottish island.",
    )
    bergen["outcome"] = HAPPENED
    return dormant(
        b.threat(
            "The Icelandic Wars",
            place=_neighbour(b, "Iceland"),
            summary=paragraphs(
                "An outline of how the Order of Hermes might go to war with "
                "Iceland over a myth, written for the Toframanna Saga but "
                "with seeds for players on either side. Hermetic archmagi "
                "meet the guardians, the landvaettir and the giant clans; "
                "unless the player characters are as strong, they work by "
                "politics and tactics, guarding their own future and limiting "
                "the ruin. The book's aim is story, and storyguides should "
                "fit it to their own troupe and power level.",
                "Three of the book's events carry years before the fleet "
                "sails; everything after that has none, and the outcome "
                "hangs on what the characters do. The conflict barely "
                "touches the mainland's mundane history, but could alter "
                "Iceland's: see Land of Fire & Ice p. 18.",
            ),
            secrets=paragraphs(
                "Land of Fire & Ice pp. 29 and 63 foresee this war: killing "
                "great galdramen enrages the landvaettir lords, killing "
                "trollsynir enrages the giants, and the hreppur is the "
                "nearest thing to an Order of Odin that exists. The saga "
                "there is not official history (p. 67), and neither is this.",
                "Land of Fire & Ice p. 70 sets a ship of Flambeau magi from "
                "Bergen on fire in 1218, not 1214, and kills Einar Gamlisson's "
                "family with them. Both stand; the book's year is used here.",
                "At the War Tribunal the characters may keep quiet, which the "
                "winner will remember; aid the crusade out of duty, ignorance "
                "or fear, for who else destroyed those covenants; or try for "
                "peace, which for Vindolanda means showing that it survives "
                "(p. 3). Many there want a hunt, glory or new vis, whatever "
                "is said. Whether Julius and Lavinia are renounced, punished "
                "or pardoned after a crusade ruled illegal is the storyguide's; "
                "their followers share it by rank (pp. 12-13).",
            ),
            antagonist="Archmagi Julius of Flambeau and Lavinia of Guernicus",
            moves=DATED,
            stages=[
                bergen,
                S(
                    "The Ghost Speaks",
                    year=1224,
                    clues="The covenant's redcap brings news of Hadrianus's "
                    "ghost, and of whom it blames. Over the next couple of "
                    "years magi start to say something must be done.",
                    ignored="A Loch Leglean magus meets the ghost, which "
                    "blames the Order of Odin and then rests; a summoning "
                    "for more sends it into Final Twilight. The Primus of "
                    "Flambeau demands vengeance, Guernicus magi press their "
                    "old case, and Julius and Lavinia start preparing.",
                ),
                S(
                    "The War Tribunal",
                    year=1230,
                    clues="A few years after the ghost, letters reach every "
                    "covenant of the northern Tribunals asking for help and "
                    "for knowledge of Iceland. Lavinia then calls a special "
                    "Tribunal at Durenmar, open to all with an interest.",
                    ignored="The Tribunal declares all Icelandic magicians "
                    "enemies of the Order, their lives forfeit, in revenge "
                    "for Hadrianus, and Lavinia rules that binding. Those who "
                    "kept quiet will not be thanked by the winner.",
                    stopped="It cannot quite be stopped: the war party has "
                    "the loudest voice, wanting a hedge-wizard hunt, glory or "
                    "new vis. If the hreppur swears the Oath, Lavinia demands "
                    "approval from a prima who refuses all contact as she "
                    "readies for the end of the world, and voids it. Uproar "
                    "follows; their peers leave, and Julius wins the certamen "
                    "against the eldest open opponent.",
                    turned="Well argued, the doubts spread: senior magi "
                    "withdraw, leaving a controversial venture, and elders "
                    "pledge to take it to the Grand Tribunal.",
                ),
                S(
                    "The Armada Sails",
                    year=1232,
                    season="Summer",
                    clues="Two large ships, each under a modified Aegis of "
                    "the Hearth giving +75 Magic Resistance, with strong "
                    "wards against fire and a Muto Herbam spell giving +20 "
                    "Soak. Icelandic seers grow uneasy at omens of death.",
                    ignored="The crusaders sail, not knowing what they face "
                    "unless told.",
                    stopped="If the characters gave Vindolanda as a base, "
                    "there is no armada: the first strike kills many leading "
                    "magicians. If the Aegis at Scartaris is not raised to "
                    "75th level, Bard may flood it.",
                    turned="Warned, Bard and Pan Caudarax prepare and tell "
                    "Vindsvall and the Gray Bull. The magi can teach Parma "
                    "quickly, but their best advice to the galdramen is to "
                    "hide. Grogs and companions sent alone escape the watchers.",
                ),
                S(
                    "Assault on the Guardians",
                    clues="As the coast rises Pan Caudarax sends drake "
                    "images to test the ships, then becomes a lindorm and "
                    "dives.",
                    ignored="The Host breaks on the wards, too many to kill, "
                    "while the dragon strikes from below as a kraken and is "
                    "repelled. He may die, unless the Host heals him. Then "
                    "Vindsvall's storm breaks one ward; the Host's winds sink "
                    "that ship with about seven magi and most mundanes, and "
                    "a spontaneous Kill the Living Air with two rooks of vis "
                    "drains him. The last ship anchors in the southeast, "
                    "where the Gray Bull, if free, may smash it.",
                    stopped="If the guardians repel them, they go home and "
                    "by next summer try another way (see Hermetic Foothold). "
                    "The Bull smashes through the ward, and a ship still afloat "
                    "has two rounds to cut anchor and make open water. If both "
                    "ships go, only Leap of Homecoming and the like save anyone.",
                    turned="Albinus drives off the Host and can bottle "
                    "Vindsvall, and has an even chance against the Bull. If "
                    "he captures it the crusaders land, and Bard waits as "
                    "the giants arm.",
                ),
                S(
                    "Hermetic Foothold",
                    clues="If repelled, Bonisagus magi guess that Bjornaer in "
                    "animal form will escape the guardians' notice; they do.",
                    ignored="The materials for a Hermes Portal are ferried "
                    "to the remote southeastern highlands. A strong force "
                    "steps through, conjures a Mystic Tower, casts an Aegis "
                    "of the Hearth and starts hunting. If the crusaders got "
                    "past the guardians, they simply build it.",
                    stopped="Vindolanda may disrupt the ritual and keep the "
                    "main force out.",
                ),
                S(
                    "The Night of Tears",
                    clues="Under illusion, magi question mundanes by magic "
                    "and find several galdramen, witches and seithkona.",
                    ignored="In one night they fall on twelve farmsteads and "
                    "kill everyone. Warned at the last moment, Biorn Egilsson "
                    "stands before his farm and asks Julius in Latin to "
                    "talk; Julius burns him through his Ol-spirit, and the "
                    "farm dies with him. The magi withdraw to their base. "
                    "Talk of foreign Latin magi may now expose Vindolanda.",
                ),
                S(
                    "The Grapes of Wrath",
                    clues="Ten galdramen, twelve seithkona and two trollsynir "
                    "lie dead among over 120 farmers, labourers and kin, with "
                    "three priests, one a son of Bishop Magnus Gizurarson. "
                    "With no one owning the deed, Icelanders call it "
                    "cowardly murder.",
                    ignored="The landvaettir lords vow revenge for Biorn; "
                    "after giants and trollsynir die, the giant families "
                    "rally to Bard; the Bishop of Skalholt calls all "
                    "Christians to find the killers. Every galdraman gets "
                    "an attendant spirit of Might equal to Song Talent x 5 "
                    "for the war, cutting his casting to the spell phase, "
                    "and it asks little or no vis.",
                    turned="Crusader characters may press for moderation.",
                ),
                S(
                    "The Battle for Iceland",
                    clues="Vigdis warns that Julius has found Scartaris and "
                    "strikes in three days. Bard plans to hit the tower "
                    "while Julius is at Vindolanda, his vanguard flying "
                    "there as eagles; Norns coordinate.",
                    ignored="Gull needs seven strikes on the Aegis and falls "
                    "to six vis-backed Clenching Hand of the Crushed Heart "
                    "spells. Bard takes up the hammer under a rain of spells "
                    "while the Host shields him, unless Albinus banishes it.",
                    stopped="Crusader Victory: Bard falls and the Hermetics "
                    "clear Iceland of magicians, while Lavinia finds that "
                    "none knew of an Order of Odin. Policy may turn to offers "
                    "of membership. The Icelanders now know who did it, and "
                    "bringing such condemnation is itself a Hermetic crime; "
                    "if the hreppur tried to join, the Grand Tribunal may "
                    "call the crusade illegal.",
                    turned="Bard is Victorious: the seventh blow shatters "
                    "the ward, over a hundred giants storm in and the Host "
                    "rips the tower apart. A few magi flee by the Portal or "
                    "Leap of Homecoming. Julius, if alive, is taken at "
                    "sunset for the Yfel lords.",
                ),
                S(
                    "The Battle Comes Home",
                    clues="Either way Bishop Magnus goes to Bremen, and with "
                    "the archbishop to Rome, to ask the Pope to act.",
                    ignored="If Bard won, galdramen and giants raid "
                    "Hermetic covenants, Pan Caudarax's mate joining as "
                    "guardian if he is dead. Unchecked, the raids bring the "
                    "full Order, which Iceland cannot withstand. If the "
                    "Pope agrees, he excommunicates all Christian magi and "
                    "forbids Christians to serve or trade with them, perhaps "
                    "for years.",
                    stopped="If Bard won with Albinus's help, the Icelanders "
                    "may be talked into Hermetic justice instead of raids.",
                ),
                S(
                    "The Resolution",
                    clues="Pressure builds for a settlement.",
                    ignored="Hermetic Domination: with no real pressure, "
                    "clearance goes on and Iceland empties for a land-rush. "
                    "Mundane hatred lasts decades or centuries, and the "
                    "landvaettir never forgive, though newcomers may strike "
                    "their own treaties.",
                    stopped="Hermetic Failure with indiscriminate raids: the "
                    "Order calls the crusade justified and strikes in full, "
                    "and almost surely wins. House Jerbiton gets the "
                    "excommunication lifted, and an inquiry into sorcery by "
                    "Icelandic clergy closes both cathedral magic schools.",
                    turned="Hermetic Failure with no raids, or raids only on "
                    "the guilty: sooner or later the Order seeks peace. The "
                    "primi of Guernicus, Bonisagus and Jerbiton send "
                    "emissaries, who land unchallenged and go before Bishop "
                    "Magnus. Pressure on Julius and Lavinia can force the "
                    "same talks.",
                ),
                S(
                    "The Settlement",
                    clues="Bishop Magnus chairs the talks, on three options: "
                    "the hreppur joins House Ex Miscellanea; it is recognised "
                    "with a treaty of mutual protection; or it joins as a "
                    "new House, keeping its own laws in Iceland.",
                    ignored="The Order wants the first if there were any "
                    "raids, and fights the second; the hreppur wants the "
                    "second; the third needs skilled bargaining. A past "
                    "refusal of admission undercuts the emissaries.",
                    stopped="Icelanders demand compensation for every dead "
                    "or hurt countryman; Bard demands it for the giants, and "
                    "a separate treaty, which the new galdramen leader makes "
                    "a condition. With raids, the Order wants its own "
                    "losses paid. Each body's rank is argued for days.",
                    turned="Outlawry is argued: Hermetic killers of "
                    "Icelanders if they return, Icelandic killers within a "
                    "league of a covenant they attacked. The Order wants "
                    "it limited to killers of mundanes and wider for "
                    "Icelanders. The less wanton side has the edge. The "
                    "bishop writes to the Pope for absolution.",
                ),
            ],
        )
    )


def _link_war(
    b: Builder,
    war: Neighbour,
    places: dict[str, Neighbour],
    people: dict[str, Any],
    factions: dict[str, Neighbour],
    creatures: dict[str, Creature],
) -> None:
    for key, note in (
        ("hadrianus", "His death begins it"),
        ("julius", "Leads the crusade"),
        ("lavinia", "Leads the crusade"),
        ("albinus", "The crusade's spirit master, or its enemy"),
        ("vigdis", "Warns of the attack on Scartaris"),
    ):
        Builder.link(war, "characters", people[key], note)
    for key, note in (
        ("vindsvall", "The second guardian"),
        ("bull", "The third guardian"),
        ("host", "Fights for each guardian"),
        ("gull", "Breaks the crusaders' Aegis"),
    ):
        Builder.link(war, "creatures", creatures[key], note)
    for key, note in (
        ("bergen", "Hadrianus sailed from here"),
        ("island", "Where his ghost walks"),
        ("durenmar", "The War Tribunal of 1230"),
        ("harbor", "Where the armada anchors"),
        ("tower", "The crusaders' base"),
    ):
        Builder.link(war, "places", places[key], note)
    for key, note in (
        ("crusaders", "The invaders"),
        ("doubters", "Argue against it"),
        ("odin", "The pretext"),
        ("leglean", "Finds the ghost"),
    ):
        Builder.link(war, "neighbours", factions[key], note)
    for names, note in (
        (("Pan Caudarax, Dragon of Hekla",), "The first guardian"),
        (("Bard Snaefellsass Dumbson",), "The fourth guardian"),
        (("Biorn Egilsson",), "Leader of the hreppur, slain"),
        (("Skalholt",), "Bishop Magnus's seat; the Gray Bull's pasture"),
        (("Scartaris",), "Julius's target, and a trap"),
        (("The Norn Landvaettir",), "Coordinate the Icelandic assault"),
    ):
        wanted = [
            *(n for n in b.saga.creatures if n.name in names),
            *(n for n in b.saga.characters if n.name in names),
        ]
        if wanted:
            kind = "creatures" if isinstance(wanted[0], Creature) else "characters"
            Builder.link(war, kind, wanted[0], note)
        else:
            target = _neighbour(b, *names)
            place = target is not None and target.kind == PLACE
            _link(war, "places" if place else "neighbours", target, note)
    _link(
        war,
        "neighbours",
        _neighbour(b, "Galdramen Hreppur"),
        "The war's target",
    )


# -- links across the book's chapters --

#: Each story of the two books and who appears in it, by record name.
CAST: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Fire and Song",
        (
            "Einar Gamlisson",
            "Pan Caudarax, Dragon of Hekla",
            "Bard Snaefellsass Dumbson",
        ),
    ),
    (
        "Spider in the Ice",
        (
            "Damhan-allaidh, the Spider",
            "Hetep the Corrupter",
            "Victor filius Pralix",
            "Brighde Scot",
            "Iain the Scot",
            "Liam the Shapeless",
            "Setna",
            "Pralix",
            "Ealasaid, Lady of the Waters",
            "Macomb",
        ),
    ),
    (
        "Blood of Innocence",
        (
            "Lord Peter",
            "Whisper",
            "Lord Peter's Men",
            "Brighde Scot",
            "Iain the Scot",
            "Donncadh Scot",
            "Eleanor, Iain's wife",
            "Mari, Donncadh's wife",
            "Hetep the Corrupter",
            "Victor filius Pralix",
            "Markus of Verditius",
            "Cornelius of Verditius",
            "Thord Sturluson",
            "Thingmen",
            "Walking Corpses",
        ),
    ),
    (
        "The Dragon's Bane",
        ("Pan Caudarax, Dragon of Hekla",),
    ),
    (
        "Thord's Feast",
        (
            "Thord Sturluson",
            "Blund Thorgilsson",
            "Una",
            "Vifil Halldorson",
            "Iain the Scot",
            "Einar Gamlisson",
            "Hlokk",
            "Disease Spirits",
            "Unhatched Dragon of Pan Caudarax",
        ),
    ),
    (
        "Meet the Dragon",
        (
            "Pan Caudarax, Dragon of Hekla",
            "Bard Snaefellsass Dumbson",
            "Vifil Halldorson",
            "Biorn Egilsson",
            "Blund Thorgilsson",
            "Signy Grettisdottir",
            "Arnor Arngeirsson",
            "Leif Beogart",
            "Father Halldor Ormsson",
            "Father Vebrand Thoroddson",
            "Aldis Kolbeinsdottir",
            "Helga Grimsdottir",
        ),
    ),
    (
        "Feast of Thanks",
        (
            "Bard Snaefellsass Dumbson",
            "Solrun",
            "Thordis",
            "Kollbjorn",
            "Skrukka",
            "Thorkel Red-Cloak's Son",
            "Vindsvall",
        ),
    ),
    ("The Troll-Bride", ("Kollbjorn", "Skrukka", "Drit", "Solrun")),
    ("The Gray Bull", ("The Gray Bull", "Bard Snaefellsass Dumbson")),
    (
        "The Glittering Plains",
        (
            "Einar Gamlisson",
            "Blund Thorgilsson",
            "Una",
            "Kar Liefsson",
            "Thorodd Gamlisson",
            "Gudmund of Glasvellir",
            "Geirrod",
            "Jarl Agdi",
        ),
    ),
    (
        "Brighde's Gauntlet",
        (
            "Brighde Scot",
            "Victor filius Pralix",
            "Hetep the Corrupter",
            "Damhan-allaidh, the Spider",
            "Whisper",
            "Ammon, Master of the Hidden Revels",
            "Liam the Shapeless",
        ),
    ),
    (
        "Spider Through Mist",
        ("Damhan-allaidh, the Spider", "Hetep the Corrupter", "Geirrod", "Setna"),
    ),
    (
        "Into the Gateway",
        (
            "Damhan-allaidh, the Spider",
            "Hetep the Corrupter",
            "Hetep's Undead Form",
            "Setna",
            "The Golden Sphinxes",
            "Geirrod",
            "Gudmund of Glasvellir",
            "Einar Gamlisson",
            "Iain the Scot",
            "Victor filius Pralix",
        ),
    ),
    ("The Hidden Revels", ("Ammon, Master of the Hidden Revels",)),
)

#: One person's tie to another: from, to, what the first is to the second.
TIES: tuple[tuple[str, str, str], ...] = (
    ("Iain the Scot", "Liam the Shapeless", "His father and parens"),
    ("Iain the Scot", "Victor filius Pralix", "Serves him"),
    ("Iain the Scot", "Eleanor, Iain's wife", "His wife"),
    ("Iain the Scot", "Donncadh Scot", "His son"),
    ("Donncadh Scot", "Mari, Donncadh's wife", "His wife"),
    ("Donncadh Scot", "Brighde Scot", "His daughter"),
    ("Brighde Scot", "Victor filius Pralix", "Her master, who possesses her"),
    ("Brighde Scot", "Hetep the Corrupter", "The demon held in her"),
    ("Victor filius Pralix", "Pralix", "His parens"),
    ("Victor filius Pralix", "Hetep the Corrupter", "His prisoner"),
    ("Macomb", "Ealasaid, Lady of the Waters", "His parens"),
    ("Lord Peter", "Whisper", "His familiar"),
    ("Blund Thorgilsson", "Una", "His wife"),
    ("Una", "Hlokk", "Her cat"),
    ("Einar Gamlisson", "Thorodd Gamlisson", "His brother"),
    ("Thord Sturluson", "Vifil Halldorson", "His guide for the magi"),
    ("Solrun", "Bard Snaefellsass Dumbson", "Her father"),
    ("Thordis", "Bard Snaefellsass Dumbson", "Her father"),
    ("Helga Bardsdottir", "Bard Snaefellsass Dumbson", "Her father"),
    ("Kollbjorn", "Skrukka", "His mother"),
    ("Kollbjorn", "Drit", "His daughter"),
    ("Thorkel Red-Cloak's Son", "Bard Snaefellsass Dumbson", "His half-brother"),
    ("Damhan-allaidh, the Spider", "Hetep the Corrupter", "His demon"),
    ("Hetep's Undead Form", "Damhan-allaidh, the Spider", "His body"),
    ("Hetep's Undead Form", "Hetep the Corrupter", "The same demon"),
    ("Gudmund of Glasvellir", "Geirrod", "His brother"),
    ("Geirrod", "Jarl Agdi", "His lieutenant"),
)


def _link_saga(b: Builder) -> None:
    """Tie the people of the two books to the stories and to each other,
    now that every part has made its records. This part runs last."""
    people: dict[str, tuple[str, Any]] = {
        **{c.name: ("characters", c) for c in b.saga.characters},
        **{c.name: ("creatures", c) for c in b.saga.creatures},
    }
    stories = {n.name: n for n in b.saga.neighbours if n.kind == "threat"}
    for story, cast in CAST:
        for name in cast:
            kind, person = people[name]
            Builder.link(stories[story], kind, person)
    for one, other, note in TIES:
        kind, person = people[other]
        Builder.link(people[one][1], kind, person, note)


# -- the story seeds --


def _seed(
    b: Builder,
    title: str,
    page: int | str,
    antagonist: str,
    *text: str,
    stages: list[dict[str, Any]] | None = None,
) -> Neighbour:
    """A story seed of the book, as a dormant threat."""
    return dormant(
        b.threat(
            f"Icelandic Wars: {title}",
            summary=paragraphs(*text, f"(Icelandic Wars p. {page})"),
            antagonist=antagonist,
            stages=stages,
        )
    )


def _seeds_before_the_sailing(b: Builder) -> None:
    _seed(
        b,
        "The Ghost in the Isles",
        2,
        "The ghost of Hadrianus",
        "For crusaders. On a journey in the Scottish isles the characters "
        "find Hadrianus's ghost themselves, carry the warning to the Order, "
        "and stand high in the crusading party for it.",
    )
    _seed(
        b,
        "Asking the Dragon",
        2,
        "Pan Caudarax",
        "For Vindolanda. Asked why he killed the archmagus, Pan Caudarax "
        "vaguely recalls his watchers warning of very strong, very hostile "
        "wizards, so he brought all his force. He owes nothing for slaying "
        "raiders, resents any notion that he serves an order of wizards, "
        "knows nothing of an Order of Odin and has small interest in Norse "
        "wizards.",
    )
    _seed(
        b,
        "Vindolanda's Secret",
        3,
        "The magi's own fear",
        "For Vindolanda, against the crusade. No outsider suspects the "
        "covenant lies in Iceland. Do its magi stay hidden, or show their "
        "hand and argue that Hadrianus's death had nothing to do with an "
        "Order of Odin? Speaking means admitting that it still exists over "
        "three hundred years after its reported fall, but others will rally "
        "to it if it stands up.",
    )
    _seed(
        b,
        "Scrying on the Doubters",
        3,
        "Magi who call the Order of Odin a myth",
        "For crusaders. Some magi say the Order of Odin is a myth, so they "
        "must be fooled or in league with it. Loyal magi should look into "
        "their contacts, and the danger may excuse a little scrying.",
    )
    _seed(
        b,
        "The Hreppur Takes the Oath",
        "3-4",
        "The pride of the hreppur, then Lavinia",
        "For Vindolanda, against the crusade. Before the Tribunal the "
        "characters may propose that the whole hreppur joins the Order, "
        "which would make the war illegal under the Code. Proud Norsemen "
        "who refuse any jarl or king balk at serving a primus.",
        stages=[
            S(
                "Win over the hreppur",
                at=1,
                clues="The galdramen fear for their independence.",
                ignored="The hreppur stays outside the Order.",
                turned="It swears, and the news is brought to the War Tribunal, "
                "catching Julius and Lavinia off guard.",
            ),
            S(
                "Lavinia's ruling",
                at=2,
                clues="She recovers fast, insisting that the prima of Ex "
                "Miscellanea approve each candidate, and that prima sees no one.",
                ignored="The membership is void. Senior magi dispute it; their "
                "peers leave Julius and Lavinia, and a certamen settles it for "
                "Julius.",
            ),
        ],
    )
    _seed(
        b,
        "Vindolanda as Base",
        4,
        "Bard and the guardians",
        "For Vindolanda, with the crusade. With Vindolanda as a base the "
        "force skips the guardians and, on the characters' information, "
        "kills many leading magicians in its first strike. Bard's counter "
        "likely fails against Scartaris and Iceland falls quickly, unless "
        "no one thought to raise the Aegis to 75th level, in which case he "
        "may flood the place. Stage that while the characters are away, so "
        "they survive. Bishop Magnus's delegation sails either way.",
    )
    _seed(
        b,
        "Lavinia's Demand",
        4,
        "Lavinia of Guernicus",
        "For Vindolanda, against the crusade. If the characters have shown "
        "their tie to Iceland, Lavinia orders their cooperation within a "
        "season. Defiance costs them the mainland site: Iain can have the "
        "gate spirit swallow the gatestone on one side and bring it out on "
        "the other, sealing Scartaris off. If they stayed hidden, the mainland "
        "site keeps them informed of the crusade.",
    )
    _seed(
        b,
        "Scouting Iceland",
        5,
        "Pan Caudarax",
        "For crusaders. Scouts are wanted. Magi meet Pan Caudarax and may die "
        "as Hadrianus did, but if they seem weak he plays with them: he "
        "denies serving the Order of Odin, calls the killing his own choice "
        "and their lives forfeit, then lets them go home, or lets the "
        "persuasive land on an oath of good conduct. Grogs and companions "
        "alone slip past the watchers, and may find Vindolanda on the "
        "Snaefellsnes if it is a non-player covenant.",
    )


def _seeds_of_the_voyage(b: Builder) -> None:
    _seed(
        b,
        "Casting Tokens",
        7,
        CRUSADERS,
        "For Vindolanda, against the crusade. Magi whose ties stayed secret "
        "may get people aboard. One who takes part in an Aegis casting, "
        "gets its tokens and brings them to Pan Caudarax puts the armada "
        "in grave danger.",
    )
    _seed(
        b,
        "Freeing the Gray Bull",
        "7-8",
        "Bishop Magnus Gizurarson",
        "For Vindolanda, against the crusade. The magi are asked to free "
        "the Bull, and Bishop Magnus will not lose his prize stud for less "
        "than an irresistible offer, so it means a raid.",
        stages=[
            S(
                "The raid",
                at=1,
                clues="A raid is not shameful in itself, but this target "
                "will hardly defend itself, so it may look cowardly; "
                "provoking a man as strong in law as a storgodi may also "
                "look bold.",
                ignored="The Bull stays tame.",
                turned="Outside the Dominion it bellows, the Host feeds it "
                "Might, and within minutes it is full size and gone to the "
                "highlands.",
            ),
            S(
                "The case",
                at=2,
                clues="It is the talk of Iceland for years.",
                ignored="The raid's leader faces outlawry; supporters must "
                "be gathered at once.",
                stopped="Even a settlement that avoids outlawry costs dear "
                "in compensation.",
            ),
        ],
    )
    _seed(
        b,
        "Traitors in the Fleet",
        8,
        "Traitors among the crusaders",
        "For the crusade. Traitors have joined the expedition. Can the "
        "characters find them and their plan before the fleet is lost?",
    )
    _seed(
        b,
        "Arming the Guardians",
        9,
        CRUSADERS,
        "For Vindolanda, against the crusade. With casting tokens Pan "
        "Caudarax capsizes one ship easily; the other's counterattack may "
        "kill or drive him off, and Vindsvall or the Bull finishes it. "
        "Level 85 Creo Vim or Rego Vim potions would also take him through "
        "the wards.",
    )
    _seed(
        b,
        "Saving the Drowning",
        9,
        "The guardians' storm",
        "For crusaders. Quick thought and spontaneous magic may save magi "
        "and grogs from certain death and hold down the losses.",
    )
    _seed(
        b,
        "Masters of Spirits",
        9,
        CRUSADE_FOES,
        "For crusaders. This stage turns on spirit magic, above all "
        "Albinus's. Characters very strong in Vim, with the right spells, "
        "may shift the balance as he does.",
    )
    _seed(
        b,
        "Disrupting the Portal",
        9,
        "Bjornaer magi of the crusade",
        "For Vindolanda, against the crusade. The magi learn of the Hermes "
        "Portal and may be a match for the Bjornaer casting it. Acting fast, "
        "they might break the ritual and bar the main force.",
    )
    _seed(
        b,
        "The Envoys to Sinus Wodinis",
        9,
        "The magi of Sinus Wodinis",
        "For crusaders. The characters are sent to ask the Bjornaer of Sinus "
        "Wodinis for help against the Order of Odin. They dislike strangers "
        "and may be allied with Norse wizards; one may even be a trollson.",
    )
    _seed(
        b,
        "Testing the Bonisagus Theory",
        9,
        "The guardians",
        "For crusaders. Bjornaer characters test whether heart-beasts pass "
        "the guardians, then help defend the Hermes Portal ritual and guard "
        "the base while it is raised.",
    )


def _seeds_of_the_foothold(b: Builder) -> None:
    _seed(
        b,
        "Gunnar's Daughter",
        10,
        CRUSADERS,
        "For Vindolanda, against the crusade. A late rider, a chance to mend "
        "the magi's name with a church warden, and a raid they did not "
        "expect. Iceland being Iceland, such a gift is nearly sure to be "
        "repaid.",
        stages=[
            S(
                "Gunnar rides to Dagverdara",
                at=1,
                clues="Gunnar Loftursson asks for a magus at once: Asta's "
                "skill cannot save their dying daughter, and she needs ond "
                "(vis) for Biarg spirits, in Hermetic terms Creo, Corpus or "
                "Vim.",
                ignored="The child and her mother are left to the crusaders.",
                turned="The magi give vis or ride back with him.",
            ),
            S(
                "The church",
                at=2,
                clues="Warned by her fylgja an hour ahead, Asta and the women "
                "take to the church, where she sings on, exhausted, to keep "
                "the Biarg spirit with the girl.",
                ignored="As Gunnar returns, a Hermetic party faces the "
                "household's men before the door.",
            ),
        ],
    )
    _seed(
        b,
        "The Witch's Heart",
        10,
        "The characters' own orders",
        "For crusaders. Lavinia sends the characters to a western-quarter "
        "farmstead to kill a witch, bring her heart so she may question "
        "the ghost, and leave no witnesses. The galdrakona's fylgja warns "
        "her; she and the women bar themselves in the church with the "
        "children as the men take up arms. Neither is a danger to magi. Will "
        "they murder in cold blood? Mentem magic leaves the question of who "
        "kills her, and whether inside the church or out.",
    )
    _seed(
        b,
        "Moderating the Crusade",
        10,
        "Julius of Flambeau",
        "For crusaders. A plan that kills dozens of mundanes looks close to "
        "interfering with the mundanes, ethics aside. Uneasy magi may "
        "persuade the crusaders to hold back.",
    )
    _seed(
        b,
        "The Hidden Covenant",
        "10-11",
        "Landvaettir, giants and vengeful farmers",
        "For crusaders. Julius orders the characters to find a Hermetic "
        "covenant said to lie in the western quarter. Spirits and mundanes "
        "are watching for foreigners. A magus caught outside an Aegis at "
        "sunrise or sunset may be attacked with his Parma down, and grogs "
        "and companions without resistance at any time.",
    )
    _seed(
        b,
        "The Combined Assault",
        "11-12",
        "Julius of Flambeau",
        "For Vindolanda, against the crusade. Bard, Gull and Vigdis come to "
        "the magi: Julius will attack Scartaris in three days, and the tower "
        "is to be struck while he does. The magi must hold him there; "
        "Vigdis can give each a landvaettir of Might 50, and Orlog-spirits "
        "may let them lay an ambush or a trap.",
        "Julius and his retinue have strong Parma, though vis-boosted spells "
        "pass it, and the hoplites' wards cover mundane weapons. Above the "
        "sanctum sit thousands of tons of ice: tunnelling and Creo Ignem may "
        "flood Scartaris in an instant with plain water, and the blow alone "
        "should kill. If they are losing, landvaettir throw themselves before "
        "spells and earth spirits may carry them away through the mountain; "
        "they may yet be captured or killed.",
    )


def _seeds_of_the_ending(b: Builder) -> None:
    _seed(
        b,
        "Smuggling the Galdramen",
        13,
        CRUSADERS,
        "For Vindolanda, against the crusade. Survivors may use the gateway "
        "to get galdramen off the island, while trollsynir and giants "
        "shapeshift and flee, many to Helluland. Only mainland Hermetic "
        "support can stop the killing, perhaps by raising mundane anger, and "
        "Bishop Magnus's delegation is the best tool for that.",
    )
    _seed(
        b,
        "The Hornet's Nest",
        13,
        "Mundanes and churchmen",
        "For crusaders. The magic is won, but with no proof of a threat the "
        "campaign looks empty, and mundane anger may bring Hermetic charges. "
        "If the hreppur tried to join, every crusader may be in deep trouble. "
        "Time to negotiate a peace?",
    )
    _seed(
        b,
        "Into the Tower",
        13,
        CRUSADERS,
        "For Vindolanda, against the crusade. Not being magical creatures, "
        "the magi can carry the fight inside the Aegis, with penalties, or "
        "supply potions and other magics for Bard's forces.",
    )
    _seed(
        b,
        "Flight from Iceland",
        13,
        "Bard's forces",
        "For crusaders. Away scouting when the base falls, the characters "
        "must get off the island before they share their comrades' fate.",
    )
    _seed(
        b,
        "Hostages of Iceland",
        13,
        "Their captors",
        "For crusaders. Galdramen and landvaettir capture the characters, and "
        "Yfel spirits suppress their Gifts for a time. There are no prisons: "
        "on an oath of good conduct they live in a household and work for "
        "their food. Treated well, those who keep faith may teach Latin and "
        "letters and end up more guests than hostages. Escape is impossible "
        "without help, and attacking the householder is unwise.",
        "Not for every troupe, and not for those guilty of cowardly butchery, "
        "who die once they are named.",
    )
    _seed(
        b,
        "The Raiding Party",
        14,
        "The characters' Icelandic allies",
        "For Vindolanda, against the crusade. Asked to join a raid, with rich "
        "loot, will the magi take part in murderous vengeance? Refusal may "
        "offend and look suspicious, and random attacks would bring ruin. "
        "Most neutral magi would accept a strike on the guilty as justice, "
        "and Orlog spirits can arrange ambushes; a precise vendetta costs "
        "little support but makes Hermetic justice less likely.",
        "Instead they may urge the Icelanders to seek that justice: the "
        "landvaettir could be called faeries, and the crusaders plainly "
        "interfered with mundanes, so renunciation has a case. Icelanders "
        "will dislike it unless Hermetic help won their victory.",
    )
    _seed(
        b,
        "Ambush on the Road",
        14,
        "Unknown avengers",
        "For crusaders. Expedition members are ambushed and killed as they "
        "travel. The characters must take care, not knowing what form the "
        "attack will take.",
    )
    _seed(
        b,
        "The Bishop's Delegation",
        14,
        "Bishop Magnus Gizurarson",
        "For anyone. The characters hear of Bishop Magnus's journey. They may "
        "want it stopped, but how, without making things worse?",
    )
    _seed(
        b,
        "Vindolanda at the Table",
        15,
        "The Hermetic emissaries",
        "For Vindolanda. Magi who sided fully with the hreppur have great "
        "influence. If they taught galdramen Parma or Hermetic magic, the "
        "emissaries insist that the galdramen join the Order. If renounced "
        "they are reinstated on request. If they backed the crusade they may "
        "return to Scartaris, but lose any vis source the hreppur gave.",
    )
    _seed(
        b,
        "The Envoy's Mission",
        15,
        "The Icelandic negotiators",
        "For crusaders. Proven characters may join the envoys. Former "
        "prisoners, who know Icelandic ways, may be released and offered a "
        "place at the table.",
    )
    _seed(
        b,
        "Galdor into Theory",
        15,
        "The limits of Hermetic Theory",
        "For anyone. If the hreppur joins, Albinus works to bring galdor "
        "magic into Hermetic Theory. If he succeeds, galdramen may learn "
        "Hermetic Theurgy and Hermetic theurgists may summon landvaettir.",
    )
