"""The adventures of the Toframanna Saga (Land of Fire & Ice, chapters
11-17, pp. 98-132), all of it storyguide material: each chapter is a
dormant threat under its own title with a stage for each scene, the
book's story seeds are dormant threats of their own, and the places,
creatures and minor people they use are records, their hidden facts in
secrets.

The two arc threats are the saga part's and are not repeated. A place or
person another part already made is added to, not made twice, so the
parts may be built in any order (`_site`, `_sketch`).

Creatures follow the pack's readings (see the package docstring), with
Fourth Edition body levels and fatigue columns in the notes. Trolls and
giants take Might Form Corpus, where their body vis lies (pp. 30-31), and
each record says so. Jotunn talents (Curse, Shapeshift, Svonhverfing,
Potency, External Soul and the like) are described, not built."""

from __future__ import annotations

from typing import Any

from ...models import BodyVis, Character
from ...models.world import Neighbour
from ..builder import Builder, characteristics, dormant, paragraphs
from ..builder import secrets as hidden
from ..fourth import Fourth, convert

S = Builder.stage
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)
TROLL_FATIGUE = "OK, 0, 0, 0, -1, -3, -5, Unconscious"
#: What the book's parts of a giant or troll without a full block use.
TROLL_POWERS = (
    "Has the common troll's powers (p. 30): Shapeshift, Curse, Hex, "
    "described on the trolls' record."
)
#: The Might Form of a troll or giant, which the book does not print.
CORPUS_FORM = (
    "Might Form Corpus is this pack's reading, from the body vis of trolls "
    "and giants (pp. 30-31)."
)


def build(b: Builder) -> None:
    _thords_feast(b)
    _meet_the_dragon(b)
    _feast_of_thanks(b)
    _glittering_plains(b)
    _brighdes_gauntlet(b)
    _spider_through_mist(b)
    _into_the_gateway(b)


# -- helpers --


def _named(b: Builder, name: str) -> Neighbour | None:
    """The neighbour another part made under `name`."""
    return next((n for n in b.saga.neighbours if n.name == name), None)


def _site(
    b: Builder, name: str, *, summary: str, secrets: str = "", **fields: Any
) -> Neighbour:
    """The place `name`: another part's record with these words added, or
    a new one, kept from the player's eye."""
    found = _named(b, name)
    if found is None:
        return b.place(name, summary=summary, secrets=secrets, **fields)
    found.secrets = paragraphs(found.secrets, summary, secrets)
    return found


def _sketch(
    b: Builder,
    name: str,
    *,
    age: int | None,
    summary: str,
    secrets: str,
    traits: dict[str, int] | None = None,
    type: str = "companion",
) -> Character:
    """A minor person: another part's record with these words added, or a
    new sketch."""
    for character in b.saga.characters:
        if character.name == name:
            character.secrets = paragraphs(character.secrets, secrets)
            return character
    return b.magus(
        name,
        covenant=None,
        house="",
        age=age,
        type=type,
        summary=summary,
        traits=traits,
        secrets=secrets,
    )


def _mundane(
    b: Builder,
    name: str,
    block: Fourth,
    *,
    summary: str,
    secrets: str,
) -> Character:
    """A mundane the book gives a block: converted, without the Gift and
    the Hermetic Virtue the conversion gives a magus."""
    stat, age = convert(name, block)
    stat["virtues_flaws"] = []
    person = b.magus(
        name,
        covenant=None,
        house="",
        age=age,
        type="companion",
        summary=summary,
        secrets=secrets,
    )
    return b.stats(person, stat)


# -- Chapter 11 --


def _thords_feast(b: Builder) -> None:
    snaefellsnes = _named(b, "Snaefellsnes")
    _site(
        b,
        "Stad",
        summary="The estate of the godi Thord Sturluson.",
        secrets="Thord feasts the foreign magi here, and here Blund Thorgilsson's "
        "thirty horsemen ride in to summon them (p. 98).",
        realm="",
        inside=snaefellsnes,
    )
    _site(
        b,
        "Thorsnes",
        summary="The seat of a district thing on Snaefellsnes.",
        secrets="The witchcraft case opens at this varthing and passes to the "
        "Althing; Blund's man offers terms during the first proceedings (p. "
        "99). Blund's farm lies about 13 miles east.",
        realm="",
        inside=snaefellsnes,
    )
    farm = _site(
        b,
        "Blund's Farmstead",
        summary="A rich farm on the north coast of Snaefellsnes, with several "
        "tenancies and its own church.",
        secrets=paragraphs(
            "About 13 miles east of Thorsnes (p. 99). Every fertile woman and "
            "beast of the household is miscarrying. A Per + Second Sight roll "
            "of 9+ shows a great spirit cat falling on the swarms of flies that "
            "come over the rise, and Intellego Vim also finds them: Hlokk, "
            "Una's sickly house cat, is fighting them off.",
            "The cause lies at the mud pits about 2 miles south.",
        ),
        realm="",
        inside=snaefellsnes,
    )
    nest = _site(
        b,
        "Blund's Mud Pits",
        summary="A field of boiling mud pits on Snaefellsnes that the farmers shun.",
        secrets=paragraphs(
            "Six pits in an exact circle, in a Magic aura of +4, about 2 miles "
            "south of Blund's farm; Per + Awareness 6+ spots something just "
            "under each surface. In each lies a white egg of Size +0, laid in "
            "the 3rd Century, of Pan Caudarax's brood. Blund and his people have "
            "no idea (pp. 98, 100).",
            "In the middle stands a nidstong, a pole with a horse's head, whose "
            "runes promise loss to a killer of children. It is Einar "
            "Gamlisson's. Each day it stands there is a chance the curse takes "
            "the eggs; destroying it ends the effect (p. 101; p. 59). The pole "
            "is an Arcane Connection to Einar, but a broken one fades within "
            "twelve weeks. No Intellego reaches him in Glasvellir.",
            "The disease spirits gather here, trying to get into the eggs, and "
            "vanish if the curse is broken. One egg is discoloured and its pit "
            "stinks of rot: the infant in it is dead, and spirits rise from it "
            "and fly down the valley to Blund's farm. Its shell holds 4 pawns "
            "of Terram and the body 3 of Animal, 3 of Vim and 3 of Ignem; the "
            "egg has no Magic Resistance and Soak +5 (pp. 100-101).",
            "Guarding the site needs a mundane cover: hut-men from among the "
            "covenfolk, which Blund as landowner and the farmers' hreppur must "
            "accept, though the land can hardly feed them. Sulfur gathering "
            "might pass. The galdramen hreppur will not stand for anything a "
            "traveller could walk into; Intellego and regular visits are the "
            "easiest answer (p. 106).",
        ),
        aura=4,
        inside=snaefellsnes,
    )
    _site(
        b,
        "Dagverdara Farmstead",
        summary="A farm of Thord Sturluson's on Snaefellsnes, under Snaefell.",
        secrets="The farm nearest the tunnel, and Scartaris's foothold on the "
        "surface; about three miles separate the two (p. 89). Iain completes the "
        "purchase once Blund's affair is settled. With his money and De "
        "Panne's support it can employ up to thirty adults and their "
        "families, a huge household by Icelandic standards: the house must be "
        "greatly extended and perhaps a second one built. Iain links it to the "
        "Scartaris gateroom with the spare gatestones, and new Icelandic "
        "characters can enter the saga simply by coming here for work (p. "
        "101). The story needs this farm later.",
        realm="",
        inside=snaefellsnes,
    )
    _mundane(
        b,
        "Blund Thorgilsson",
        Fourth(
            age=32,
            apparent=None,
            characteristics=characteristics(0, -1, -1, 1, 1, 2, 1, 0),
            confidence=3,
            twilight=0,
            decrepitude=0,
            virtues=(),
            abilities=(),
            arts={},
            spells=(),
            traits={"Protective of Family": 3, "Quick Tempered": 2, "Honorable": 1},
            reputations={
                "Cursed (Snaefellsnes residents)": 3,
                "Independent (baendur)": 2,
            },
            notes="Land of Fire & Ice p. 99. The book prints no Abilities.",
        ),
        summary="A storbondi of northern Snaefellsnes, tall, dark-haired and "
        "brown-eyed, rich and influential, with several tenancies and the "
        "local church.",
        secrets="He hates magicians and needs one: his priest has failed him "
        "and he is growing desperate. He killed a local witch in mistaken "
        "revenge, so the hreppur left him to suffer (pp. 98, 105). Years later "
        "Einar turns him against the eggs (p. 114). If he hurts one of Pan "
        "Caudarax's brood he has few days left (p. 115).",
    )
    _mundane(
        b,
        "Una",
        Fourth(
            age=22,
            apparent=None,
            characteristics=characteristics(2, 1, 0, 1, -1, 1, 3, 1),
            confidence=1,
            twilight=0,
            decrepitude=0,
            virtues=(),
            abilities=(),
            arts={},
            spells=(),
            traits={"Despondent": 4, "Frightened": 4, "Protective of Family": 3},
            reputations={"Cursed (people of Snaefellsnes)": 3},
            notes="Land of Fire & Ice p. 99. The book prints no Abilities.",
        ),
        summary="Blund Thorgilsson's young wife, of average height with light "
        "brown hair and green eyes, mother of two daughters aged four and two.",
        secrets="She has miscarried twice in a year and is pregnant again "
        "without knowing it (p. 99). Her cat Hlokk guards her.",
    )
    b.creature(
        "Hlokk",
        page="p. 100",
        realm="Magic",
        might=20,
        form="Animal",
        size=-3,
        place=farm,
        cunning=True,
        age="2",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(3, 2, 0, 0, -4, 0, 4, 2),
            "virtues_flaws": ["Ferocity", "Perfect Balance"],
            "abilities": [
                ("Athletics", 4, ""),
                ("Awareness", 3, ""),
                ("Hamfarir", 5, ""),
                ("Hunt", 3, ""),
                ("Stealth", 4, "hunting"),
                ("Second Sight", 5, ""),
            ],
            "traits": {"Devoted": 3, "Curious": 3, "Aloof": 1},
        },
        attacks=[
            b.attack("Bite or Claw", 5, 5, 7, -5),
            b.attack("Spiritual Form", 8, 7, 6, 8),
        ],
        soak=-2,
        fatigue_levels="OK, -3, Unconscious",
        powers=[
            b.power(
                "Eyes of the Cat",
                0,
                2,
                "Animal",
                does="Sees in near-darkness.",
            ),
            b.power(
                "Grant Fertility",
                1,
                1,
                "Corpus",
                level=30,
                does="CrCo 30. A woman of childbearing age who lets her sleep "
                "in her lap for over a quarter of an hour conceives, provided "
                "the conception would not be immaculate.",
            ),
            b.power(
                "Hamfaring",
                1,
                1,
                "Vim",
                level=30,
                does="ReVi 30, 1 point an hour. While she seems asleep, her "
                "spirit form hunts whatever spirits threaten her mistress.",
            ),
        ],
        vis=[BodyVis(4, "Creo", "in her body")],
        appearance="To all appearances an ordinary tabby.",
        secrets=paragraphs(
            "A beast of virtue, worn out by defending Una from the disease "
            "spirits. If she sees that the magi mean to help she tries to lead "
            "them to the mud pits (p. 100).",
            "Converted: her Spiritual Form has Str +3, Sta +1, Size -1 and Soak "
            "+5. Ferocity 3 is the Virtue, for protecting her mistress, and "
            "Hamfaring 5 is Hamfarir. Body levels OK, -3, Incapacitated. "
            "Might Form Animal is this pack's reading.",
        ),
    )
    b.creature(
        "Disease Spirits",
        page="p. 101",
        realm="Magic",
        might=10,
        form="Corpus",
        size=-6,
        how_many="Swarms like flies",
        place=nest,
        soak=-5,
        powers=[
            b.power(
                "Slay the Unborn",
                10,
                -10,
                "Corpus",
                level=10,
                does="PeCo 10, costing 10 permanent Might. The victim makes a "
                "Sta stress roll of 6+ or miscarries. Against the dragon eggs "
                "success takes extraordinary luck, but given time one spirit "
                "gets through.",
            ),
        ],
        appearance="Fly-like swarms, seen with Second Sight.",
        secrets="A manifestation of Einar's curse, which disappear if it is "
        "broken (p. 100). Body levels OK, Banished. The book prints no "
        "Characteristics; Might Form Corpus is this pack's reading.",
    )
    b.creature(
        "Unhatched Dragon of Pan Caudarax",
        page="p. 100",
        realm="Magic",
        might=20,
        form="Ignem",
        how_many="Five living eggs, of six laid",
        place=nest,
        soak=40,
        appearance="A large white egg of Size +0 in a boiling mud pit.",
        secrets=paragraphs(
            "Each living egg has Magic Resistance +40, Soak +40 and 10 Body "
            "levels; the infant inside has Magic Might 20 and Soak +10, and if "
            "the shell breaks it defends itself or tries to flee (p. 100).",
            "Destroying one is a very bad idea, as Vifil will say, dropping his "
            "cover to do it (p. 101). They hatch twenty years after the "
            "settlement with Pan Caudarax (p. 105). Might Form Ignem is this "
            "pack's reading, from the dead infant's vis.",
        ),
    )
    dormant(
        b.threat(
            "Thord's Feast",
            place=nest,
            antagonist="Einar Gamlisson's curse",
            summary="A witchcraft suit draws the magi into Icelandic law when a "
            "cursed storbondi, Blund Thorgilsson, demands they lift the blight "
            "on his household, and the godi Thord Sturluson offers to stand "
            "behind them for a price (pp. 98-101).",
            secrets=paragraphs(
                "Blund wrongly took vengeance on a local witch, so the regional "
                "leader of the galdramen hreppur blacklisted him. He hopes to "
                "force the newcomers to help, and Thord hopes his suit brings "
                "them under his influence.",
                "The curse is not aimed at Blund at all. Einar Gamlisson laid it "
                "on Pan Caudarax's eggs, laid in the 3rd Century, and "
                "the farm is merely near them. Einar has good reason to hate "
                "the eggs' father.",
                "How Blund knows: the magi landed on Snaefellsnes with no known "
                "ship just as a demon beast ran wild, Brighde/Hetep's "
                "transformation had many witnesses, and Icelanders with Second "
                "Sight or Magical Sensitivity soon notice a Parma and a Gift. "
                "Rumour goes from farm to farm, and magi outside the hreppur "
                "are easy targets (p. 98).",
            ),
            stages=[
                S(
                    "The feast at Stad",
                    at=1,
                    clues="Iain asks Thord about buying or renting the farm "
                    "nearest the Scartaris tunnel; Thord wants to know the magi "
                    "first and invites them to dine. At mid-afternoon Blund "
                    "rides in with thirty horsemen and summons them for "
                    "witchcraft. Thord explains the law, offers his support if "
                    "they become his thingmen, and offers the farm.",
                    ignored="If the magi will not join a godord, Iain does, and "
                    "they count as his household. Owning the farm makes them "
                    "residents, who must by law attach to a godord; that is no "
                    "feudal bond, so it may pass under Hermetic Law, and as of "
                    "1220 the Peripheral Code has no ruling on it.",
                ),
                S(
                    "The Thorsnes varthing",
                    at=2,
                    clues="The case moves toward the Althing. Blund's man offers "
                    "to drop it if the magi try to lift the curse, and Thord "
                    "urges them to agree. Thord lends them Vifil as guide and "
                    "interpreter; he is a galdraman sent to watch them, says so "
                    "only if asked, and lacks the Gentle Gift, so they may well "
                    "guess.",
                    ignored="If they refuse, the case goes to the Althing (see "
                    "Meet the Dragon).",
                ),
                S(
                    "Blund's farmstead",
                    at=3,
                    clues="Women and beasts miscarry; Una's cat Hlokk sleeps and "
                    "hardly eats. Second Sight or Intellego Vim reveals the fly "
                    "spirits and the cat that hunts them.",
                ),
                S(
                    "The Dragon's Nest",
                    at=4,
                    clues="The spirits lead to six mud pits, six eggs, and a nidstong.",
                    stopped="Throwing down the nidstong ends the curse. Vifil "
                    "says the rest is the hreppur's business: Blund should hear "
                    "only that it is over, and being used to magicians' secrecy "
                    "he will not press. Vifil tells them about Pan Caudarax, "
                    "fears his reaction, and urges them to the hreppur meeting "
                    "just after the Althing.",
                    turned="Magi who think of breaking the eggs bring Vifil out "
                    "of hiding to explain why not.",
                ),
                S(
                    "The covenant farmstead",
                    at=5,
                    clues="With Blund satisfied Iain buys Dagverdara.",
                ),
            ],
        )
    )


# -- Chapter 12 --


def _hreppur_people(b: Builder) -> None:
    member = "Attends the hreppur at Eldborg."
    council = "A member of the galdramen hreppur's council."
    _sketch(
        b,
        "Signy Grettisdottir",
        age=196,
        summary=council,
        traits={"Quick Temper": 3, "Distrustful": 2, "Boorish": 1, "Cautious": 1},
        secrets="A trollson of the council: Magic Resistance 63, Size +2, looks "
        "37, printed Confidence 3. Her giant mother raised her and she never "
        "met her outlawed father. She picked fights until age taught her some "
        "caution, and trollsynir magic has left her looking more troll than "
        "human. She has come to back her descendant Arnor Arngeirsson in his "
        "dispute, and the attack on the eggs worries her (p. 103).",
    )
    _sketch(
        b,
        "Arnor Arngeirsson",
        age=72,
        summary=council,
        traits={
            "Judgmental": 3,
            "Honorable": 2,
            "Narrow minded": 2,
            "Cautious": -1,
        },
        secrets="Leader of the few vitkir left: Size +1, looks 67, printed "
        "Confidence 4. His temple lies in a regio near his farm, and such "
        "regiones are rare and precious to vitkir, who must keep their rites "
        "wholly secret. Wanting back those that have left vitkir hands, for "
        "vitkir lately fled from Norway, he blights fields and cattle to force "
        "sales and hides it from his victims' fylgjur. A galdraman has reported "
        "him. He will answer that the victims never suspected and that he paid "
        "fair prices (p. 103).",
    )
    _sketch(
        b,
        "Leif Beogart",
        age=51,
        summary=member,
        traits={"Secretive": 2, "Loyal to the Beogarts": 2, "Warlike": -1},
        secrets="A vitki of the powerful Beogart family, in a feud of centuries "
        "with the Odd-Karnors. Size +0, printed Confidence 4. He has come only "
        "to make plain that he had no part in the attack on the eggs (p. 103).",
    )
    _sketch(
        b,
        "Biorn Egilsson",
        age=106,
        summary="Leader of the galdramen hreppur.",
        traits={"Detached": 3, "Fair": 2, "Respectful": 3},
        secrets="Iceland's oldest galdraman, a deft politician: Size +1, looks "
        "85, printed Confidence 3, Twilight Points 19. Most galdramen have made "
        "the long hamfaring (Final Twilight) by his age, and he knows his "
        "fylgja's call cannot be refused for ever. He wants peace for those to "
        "come, and finds the quarrel between the two Christian schools the "
        "hardest to settle (p. 104). He sees no reason the magi should not "
        "belong, and offers vis rights if they appease the dragon (p. 105).",
    )
    _sketch(
        b,
        "Father Halldor Ormsson",
        age=56,
        summary="Represents the Holar school on the hreppur's council.",
        traits={"Cynical": 1, "Calculating": 2, "Curious": 1, "Pragmatic": 2},
        secrets="Size +0, printed Confidence 3. He seems to want the balance "
        "kept, but his first aim is his school's right to harvest magical "
        "sites. Bishop Gudmund's troubles leave Holar to itself. When some "
        "Skalholt vis sites went unharvested, Holar claimed abandonment and "
        "took them. Some at Holar deny the hreppur's authority; Halldor thinks "
        "the moment is wrong, not the idea. The school seeks a breakthrough to "
        "the strength of the trollsynir and traditional galdramen, and with it "
        "would press for independence (p. 104).",
    )
    _sketch(
        b,
        "Father Vebrand Thoroddson",
        age=73,
        summary="Represents the Skalholt school on the hreppur's council.",
        traits={"Forthright": 3, "Pious": 2, "Kind": 1, "Tolerant": 1},
        secrets="Size +0, printed Confidence 2. Local priests gather the "
        "school's vis, and several have died of late, so sites stood idle "
        "until new priests came. Holar calls them abandoned. Vebrand hopes the "
        "hreppur rules against Holar, and it probably will, since abandonment "
        "normally means many years of disuse (p. 104).",
    )
    _sketch(
        b,
        "Aldis Kolbeinsdottir",
        age=81,
        summary="Nominal leader of the Seithkona.",
        traits={"Fatalistic": 4, "Otherworldly": 3, "Patient": 3},
        secrets="Size -1, looks 75, printed Confidence 3. Her gloomy prophecies "
        "come true often enough that people listen, and some claim to have "
        "escaped disaster by solving her riddles, but she argues practical "
        "matters badly (p. 104).",
    )
    _sketch(
        b,
        "Helga Grimsdottir",
        age=56,
        summary="Speaks for the Seithkona at the hreppur.",
        traits={"Confidence": 3, "Polite": 3, "Forthright": 2},
        secrets="Size +0, looks 51, printed Confidence 4. Being women, most "
        "Seithkona cannot attend, so they are always outvoted. For years she "
        "has proposed that the absent may hand their votes to those who go, "
        "which the powers at the hreppur will never pass, unless she brings "
        "every Seithkona in Iceland to one meeting (pp. 104-105).",
    )


def _meet_the_dragon(b: Builder) -> None:
    _hreppur_people(b)
    _site(
        b,
        "Eldborg",
        summary="A great volcanic crater in a flat lava field, a little off the "
        "road to Snaefellsnes.",
        secrets="About 200 paces across and 50 deep; horses must be left and the "
        "sides climbed. Half an hour west across country from the northward "
        "path. The hreppur meets here just after the Althing. At the meeting "
        "the book describes, over three hours there arrive 11 trollsynir, 6 "
        "vitkir, 62 galdramen (11 of them schooled) and 8 Seithkona (p. 102).",
        realm="",
    )
    hekla = _site(
        b,
        "Hekla Lair",
        summary="Wide tunnels at the foot of the Hekla volcano, in air hot, dry "
        "and sulfurous.",
        secrets="Pan Caudarax's Icelandic lair, a Magic aura of +9. A river of "
        "lava comes from the far end of a vast cavern and flows down both "
        "sides into tunnels flanking the entrance. The dragon sleeps as a "
        "lindorm on a bed of pure white sand at the centre, in a red glow, "
        "with dozens of fire spirits darting into the lava (p. 105).",
        aura=9,
        inside=_named(b, "Hekla"),
    )
    snaefell = _named(b, "Snaefelljokul")
    _site(
        b,
        "Silver Spring of Snaefell",
        summary="A hot spring on the north face of Snaefell.",
        secrets="On the night of the winter solstice it runs with a silvery "
        "liquid usable as Vim vis. With the Ice Crystal Cave it is the "
        "hreppur's reward for a settlement with Pan Caudarax. The book "
        "recommends the two together give 3 pawns per magus per year; the "
        "storyguide sets the figure (p. 106).",
        inside=snaefell,
    )
    _site(
        b,
        "Ice Crystal Cave",
        summary="An icy cave high on Snaefell.",
        secrets="Through the summer it washes out odd ice crystals that do not "
        "melt until the summer solstice; gathered, they serve as Rego vis (p. "
        "106). Shared yield with the Silver Spring of Snaefell.",
        inside=snaefell,
    )
    dormant(
        b.threat(
            "Meet the Dragon",
            place=hekla,
            antagonist="Pan Caudarax",
            summary="The hreppur of Iceland's magicians calls the magi to "
            "Eldborg, and the dragon Pan Caudarax wants the priests of Hermes "
            "at his lair at the autumnal equinox to answer for the attack on "
            "his nest (pp. 102-106).",
            secrets=paragraphs(
                "One unborn dragon is dead and Pan Caudarax is sure to want "
                "revenge; the task is to keep it to the guilty. Had the hreppur "
                "known the truth of Blund's curse it would have acted at once, "
                "but it let him suffer because he had killed one of its own (p. "
                "105).",
                "The hreppur's authority is loose, with no oath or ceremony. "
                "Its agreement with the godar protects members from unwarranted "
                "suits, if they keep its laws; Eldborg and the pathway tax are "
                "voluntary. The Order of Hermes draws no objection from Biorn; "
                "the Order of Odin means nothing to anyone here (p. 105).",
                "Einar cannot be traced for now: he is in Glasvellir, and no "
                "galdraman knows who attacked the nest. The nearest clue is the "
                "ship Pan Caudarax destroyed five years ago, on which many "
                "Icelanders lost kin, none known as magicians (p. 106).",
                "Dragon magi. The Oath allows Hermetic training only for "
                "apprentices who will join the Order, and nothing forbids a "
                "non-human, though many would be vexed. The magi can agree: "
                "the dragons hatch in about 20 years, become human babies, "
                "start training five years later, and after 15 years' "
                "apprenticeship have no reason not to swear; the Order may "
                "debate it, but with no Oath broken a March is unlikely. They "
                "can agree and renegotiate or refuse in 25 years, when they may "
                "stand a chance against him. Or they can refuse now and be "
                "eaten (p. 106).",
            ),
            stages=[
                S(
                    "The Althing",
                    at=1,
                    clues="Vifil invites the magi to the hreppur, with the "
                    "Althing as cover for the journey; they can see the market, "
                    "the games and the procedure (p. 35).",
                    ignored="If they refused Blund or failed, they are at the "
                    "Althing for the suit. Vifil has quietly found the cause; "
                    "witchcraft cases embarrass the hreppur, so he helps Thord "
                    "settle by offering to lift a curse that is already gone. "
                    "Blund wants up to sixty ells of homespun for his delay and "
                    "cost. Vifil then invites the magi anyway.",
                ),
                S(
                    "The hreppur at Eldborg",
                    at=2,
                    clues="Vifil translates. The rules on magical services, on "
                    "owning vis (ond to Norsemen) and on discretion are read "
                    "(p. 28). Bard Snaefellsass, who speaks for giants and "
                    "greater spirits and mediates for them, delivers the "
                    "dragon's message, and watches the newcomers on 'his' land "
                    "without much interest. Biorn offers rights to a couple of "
                    "vis sources for appeasing the dragon.",
                    ignored="Magi who helped no one are summoned anyway, from "
                    "his long history with Latin magi and his curiosity; Vifil, "
                    "having found the nidstong alone, goes too and tells the "
                    "dragon they refused.",
                    stopped="Magi who will not go are told plainly they cannot "
                    "stay in Iceland: he commands volcanoes across the land, and "
                    "Scartaris sits on one.",
                ),
                S(
                    "Hekla Lair",
                    season="Autumn",
                    at=3,
                    clues="He greets them in archaic Latin, as priests of Hermes "
                    "the Thrice Blessed, hears how the curse was found, and asks "
                    "why he should not drive the human population into the sea.",
                    stopped="He settles for protection and then fostering of "
                    "his remaining children, Hermetic training included: he "
                    "will Transform them into human newborns when they hatch in "
                    "twenty years, and the magi raise and teach them. He also "
                    "offers a long hundred (120 pawns) of vis for the body of "
                    "the magician responsible.",
                ),
                S(
                    "Settlement",
                    at=4,
                    clues="The hreppur grants the Silver Spring and the Ice "
                    "Crystal Cave; if Vifil found the nidstong he takes an equal "
                    "share. He also tells them of Odadahraun, whose vis is for "
                    "anyone brave enough (p. 14). The nest is now theirs to "
                    "guard (see Blund's Mud Pits).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Mate of Pan Caudarax",
            place=hekla,
            antagonist="The lindorm, Pan Caudarax's mate",
            summary="Story seed (p. 106): a true Scandinavian lindorm, serpent "
            "bodied, small limbed and venomous of bite, may swim to Iceland to "
            "see how her brood fares under their father's guidance. Those "
            "fostering the young may not know who she is.",
        )
    )


# -- Chapter 13 --


def _feast_of_thanks(b: Builder) -> None:
    snaefell = _named(b, "Snaefelljokul")
    caves = _site(
        b,
        "The Troll Caves of Snaefell",
        summary="A cave reaching far back into the mountains near Snaefell, "
        "shunned by men.",
        secrets="Kollbjorn's trolls hold this cave system; its head is a night's "
        "shelter on the winter road to Bard. The trolls and the mountain giants "
        "keep a truce that begins only on the Longest Night. Passages twist "
        "and divide, some very narrow, some widened, and toward midday one "
        "section runs through a glacier in faint blue light (pp. 108-109).",
        inside=snaefell,
    )
    cave = _site(
        b,
        "The Singing Cave",
        summary="A deep, nearly closed valley among five mountains on "
        "Snaefellsnes, known by its echoes.",
        secrets="Songhellir in Norse. It looks like a cavern, but its roof is "
        "open and the winter sun "
        "comes down to a floor nearly three hundred paces across; every voice "
        "echoes perfectly. Bard holds his midwinter feast here (p. 109). No "
        "aura is printed.",
        inside=snaefell,
    )
    _site(
        b,
        "Husavik",
        summary="A fishing station and a farm around a small church, near the "
        "mouth of the River Laxa in the Northern Quarter.",
        secrets="The folk found a wounded eagle on the beach and laugh at talk of "
        "a giant bird: their priest carried it in his two hands and gave it to "
        "the hermit. On the rocky beach of the broad cove nearby the Scottish "
        "giants saw it fill the shore from the water to the clifftop, a "
        "wingspan of over 50 feet (p. 111).",
        realm="",
    )
    _site(
        b,
        "Skjalfandi",
        summary="An island near Husavik, home of a hermit known for his "
        "holiness and his care of hurt animals.",
        secrets="Reached by a borrowed boat. It lies in a Divine aura, of no "
        "printed strength (pp. 111-112). In the ashes of the hermit's fire lies "
        "the silver arrowhead, scratched with a runic curse to drain power from "
        "a spirit; he burnt the arrow as soon as he drew it.",
        realm="Divine",
        inside=_named(b, "Northern Quarter"),
    )
    b.creature(
        "Kollbjorn",
        page="p. 113",
        realm="Magic",
        might=35,
        form="Corpus",
        size=3,
        place=caves,
        age="Irrelevant",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(0, 0, -3, -2, 8, 5, -1, -2),
            "traits": {"Brave": 3, "Scheming": 1, "Aggressive": 2},
            "reputations": {"Troll-Chief of Western Quarter (trolls and giants)": 4},
        },
        attacks=[
            b.attack("Brawl (fist)", 9, 9, 6, 11),
            b.attack("Club", 11, 11, 9, 16),
            b.attack("Rock", 12, 9, 0, 13),
        ],
        soak=18,
        fatigue_levels=TROLL_FATIGUE,
        vis=[BodyVis(5, "Corpus", "at least; more in a powerful troll (p. 30)")],
        equipment="A staff of rusted iron.",
        appearance="Huge, back bowed and knees bent so his knuckles can drag; an "
        "exceedingly ugly face, the nose broken in three places and knotted, "
        "twisted like an old ram's horns.",
        notes=TROLL_POWERS,
        secrets=paragraphs(
            "The meanest of a mean lot, secure in his lordship with his mother "
            "Skrukka and his henchmen Gapi and Gljufra-Geir behind him (p. 113). "
            "He entraps a lone man before the truce begins, claims his life is "
            "forfeit, and offers a deal that Skrukka seals with a Curse.",
            "Converted: the book gives no combat table, only the standard "
            "troll's raised by 5 to Init, Atk and Dfn and by 3 to Damage; those "
            "totals are here, and his fatigue levels are the standard troll's. "
            "A Rock has no Defense (n/a), shown as 0. No more magic than the "
            "average troll.",
            CORPUS_FORM,
        ),
    )
    b.creature(
        "Skrukka",
        page="p. 113",
        realm="Magic",
        might=62,
        form="Corpus",
        size=1,
        place=caves,
        age="Irrelevant",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(2, -1, -4, -2, 4, 3, -2, -3),
            "traits": {"Malicious": 2, "Hostile to Humans": 4, "Brave": -1},
            "reputations": {"Powerful (trolls)": 3},
        },
        powers=[
            b.power(
                "Gift of the Magic Arts",
                1,
                -4,
                "Vim",
                level=25,
                does="Approximates any Hermetic spell at 1 Might per 5 spell "
                "levels, to level 25 alone; trolls in a group share the cost of "
                "higher spells, at about a minute per 5 levels (p. 30).",
            ),
        ],
        vis=[BodyVis(5, "Corpus", "at least; more in a powerful troll (p. 30)")],
        equipment="A short walking stick, the thighbone of a human priest.",
        appearance="So bowed with age her shape is lost in a filthy gray wrap "
        "that shows only face and hands; nose and chin nearly meet, and her "
        "eyes are filmed white, though she sees well. A fearful stench goes "
        "with her.",
        notes=TROLL_POWERS,
        secrets=paragraphs(
            "Most trolls who know of her are afraid of her. Many say she is the "
            "true chief, never in Kollbjorn's hearing. She is about as evil as "
            "trolls get. Her illusions split parties in the caves and show "
            "Solrun walking into them (p. 108).",
            "Printed abilities, described and not built: Curse 12, External "
            "Soul, Potency 9, Shapeshift 12, Speak Jotunn 9, Svonhverfing 18 "
            "(pp. 57-59 for those talents).",
            CORPUS_FORM,
        ),
    )
    b.faction(
        "Trolls of the Western Quarter",
        summary="Trolls of Snaefellsnes, the thickest concentration in Iceland "
        "(p. 125), who steal much-needed livestock (p. 107).",
        ruler="Kollbjorn",
        place=caves,
        secrets="Led by Kollbjorn, with his mother Skrukka and the henchmen Gapi "
        "and Gljufra-Geir. Trolls' law forbids stealing from or killing a "
        "relative (p. 108).",
    )
    b.creature(
        "Drit",
        page="p. 108",
        realm="Magic",
        might=20,
        form="Corpus",
        size=2,
        place=caves,
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(-3, -1, -1, -2, 6, 4, -1, -2),
            "traits": {"Aggressive": 2, "Territorial": 2},
        },
        attacks=[
            b.attack("Brawl (fist)", 4, 4, 1, 8),
            b.attack("Club", 6, 6, 4, 13),
            b.attack("Rock", 7, 4, 0, 10),
        ],
        soak=15,
        fatigue_levels=TROLL_FATIGUE,
        vis=[BodyVis(5, "Corpus", "in her body (p. 30)")],
        appearance="Plain to men, ugly to trolls. Her name means excrement.",
        notes=TROLL_POWERS,
        secrets=paragraphs(
            "Kollbjorn's daughter, for whom no troll husband can be found. She "
            "has a normal troll's statistics (p. 30) with Presence -1, and may "
            "become a player character if the storyguide agrees (p. 108). A "
            "Rock has no Defense (n/a), shown as 0.",
            CORPUS_FORM,
        ),
    )
    _scottish_giants(b)
    _bards_kin(b, cave)
    dormant(
        b.threat(
            "Feast of Thanks",
            place=cave,
            antagonist="The Scottish giants, and the rivalries around Bard's table",
            summary="Bard Snaefellsass, a giant and the people of Snaefell's "
            "half-remembered protector, invites the characters to his midwinter "
            "feast in thanks for appeasing Pan Caudarax, and sets them among "
            "Iceland's supernatural powers (pp. 107-112). Best where the "
            "covenant already has trouble with trolls.",
            secrets="Bard believes Iceland's guardians are under attack. The "
            "first was Pan Caudarax; the second is Vindsvall, now found shot; "
            "the third has been blunted by the Dominion; the fourth is himself "
            "(p. 111). He makes no claim to be more than a man who pays his "
            "debts, though Int + Area Lore 8+ ties his name to the spirit "
            "locals thank when disaster passes.",
            stages=[
                S(
                    "The invitation",
                    at=1,
                    clues="At dawn a grog sees a huge gray dog (Size +0) with "
                    "folded ears and a short nose, which leads him into a "
                    "ravine, passes behind a boulder, and comes out as a man "
                    "over eight feet tall. Bard asks them to his midwinter "
                    "feast and whistles the dog away.",
                    ignored="If they refuse he seems hurt, and sends Solrun "
                    "anyway, trusting to her charm.",
                ),
                S(
                    "Solrun",
                    at=2,
                    season="Winter",
                    clues="A month or so before midwinter a woman seeks shelter "
                    "from a storm of several days and wins the covenfolk with "
                    "tales of the Old Gods, which may offend the devout. Deep "
                    "snow keeps her on. On the morning before the solstice she "
                    "asks for the magi by name, says she has come to take them "
                    "to Bard, and calls herself his servant, not his daughter.",
                ),
                S(
                    "The journey",
                    at=3,
                    clues="Clear, dark weather; they need lights, as the sun "
                    "barely rises at noon. She leads them through the mountains "
                    "at a cost of a fatigue level by day's end, to a cave. She "
                    "warns them off the tunnels, since the truce between trolls "
                    "and giants does not begin until the Longest Night, and her "
                    "father is godi of the region's giants.",
                ),
                S(
                    "Meeting the troll-king",
                    at=4,
                    clues="In the night one man, best a grog with an eye for "
                    "Solrun, sees her cloak go into the tunnel. It is Skrukka's "
                    "illusion; companions are split up by more of the same. His "
                    "torch gutters, and Kollbjorn lurches out of the dark, "
                    "calling for Bravery rolls.",
                    ignored="Kollbjorn wrests away any weapon, declares his "
                    "life forfeit and offers whatever deal suits the saga. "
                    "Skrukka seals it with a Curse of fitting Flaws, lifted once "
                    "he keeps his side (see The Troll-Bride).",
                ),
                S(
                    "The Singing Cave",
                    at=5,
                    clues="Solrun leaves them in the glacier passage. Bard "
                    "greets them; seven of his daughters bring mead. His "
                    "brother Thorkel comes from the shadows, shrinking with "
                    "each stride to a mere nine feet, sneering at humans.",
                ),
                S(
                    "The feast",
                    at=6,
                    clues="About two dozen guests, four of them trolls, the "
                    "giants shrunk to Size +3 or less. Roast horse, illegal "
                    "heathen fare in Iceland, and two fermented sharks. Bard "
                    "toasts Freyr, Njordur and the Almighty God, meaning Thor. "
                    "Thordis, beside the party's leader, toasts the guests; "
                    "Thorkel recites his ancestors back to Kari son of Ymir; a "
                    "troll toasts Kollbjorn. At least one character must toast, "
                    "or the air chills, and Int + Etiquette 6+ (Icelanders 3+) "
                    "warns against toasting the host. Bard answers questions "
                    "freely.",
                ),
                S(
                    "Guests from afar",
                    at=7,
                    clues="Five thin, black-haired giants shout their way in, "
                    "squabbling in Pictish over a sack of sheep, and call the "
                    "characters dessert. Thorkel's party chuckles. Their leader "
                    "says he will not feast with animals. Bard cannot command "
                    "them without risking the rest of the clan, and advises a "
                    "show of strength.",
                    stopped="Size +6 by Bard's Transform (Ease Factor 31 + "
                    "Magic Resistance, stress die + 37, once per willing "
                    "character), or Str + Intimidation 9+, flashy magic at any "
                    "size, boasts on Com + Guile or Storytelling 9+, or beating "
                    "one fairly, even to death, earns their respect and a seat "
                    "beside them.",
                    ignored="Characters who make no impression are treated poorly.",
                ),
                S(
                    "Matters of trust",
                    at=8,
                    clues="Bard draws the giants to talk of their geas. They "
                    "mention an immense eagle on a Northern Quarter shore with "
                    "a lance-sized arrow in its breast. Bard turns grave and "
                    "begs the characters to investigate.",
                ),
                S(
                    "The Second Guardian",
                    at=9,
                    clues="The trail runs from the cove to Husavik, its priest, "
                    "and the hermit of Skjalfandi, who tends a slowly failing "
                    "eagle.",
                    stopped="The eagle is Vindsvall, forced into solid shape by "
                    "the arrow. Tended by a man of True Faith in a Divine aura "
                    "he regains no Might, and Int + Magic Theory 12+ shows the "
                    "Divine is killing him; the hermit blames the witchery on "
                    "the arrowhead. He recovers if the hermit, who has an "
                    "uncanny sense for lies, can be persuaded to stop, or if "
                    "fed Animal, Auram, Creo or Vim vis. Out of the Dominion he "
                    "calls his landvaettir, flocks of birds feed him Might, and "
                    "he swells to his true form and flies off. A hermit who "
                    "sees it swears it was an angel (p. 112).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Troll-Bride",
            place=caves,
            antagonist="Kollbjorn and Skrukka",
            summary="Story seed (p. 108): Kollbjorn's price for the trespasser's "
            "life is marriage to his daughter Drit.",
            secrets="Skrukka lays Curses of Lost Love and Short Attention Span "
            "on the groom, so he will come to the wedding to be rid of them. "
            "The feast is frightening: horse and human flesh, violent games, a "
            "rock-catching game for the humans. Skrukka performs the rite and "
            "the trolls drink themselves senseless, meaning to eat the guests "
            "but not the groom; Solrun comes by night to get them out. "
            "Kollbjorn's clan gives chase until several trolls are dead. A "
            "troll-chief for a father-in-law may in time bring peace between "
            "covenant and trolls, since their law protects kin, though Skrukka "
            "will likely oppose it.",
        )
    )
    dormant(
        b.threat(
            "Iceland's Enemy",
            antagonist="Unknown",
            summary="Story seed (p. 112): is anything truly hunting Iceland's "
            "guardians?",
            secrets="The book leaves it deliberately open whether a systematic "
            "threat exists: Einar Gamlisson may work alone, or someone unknown "
            "may be using him.",
        )
    )
    dormant(
        b.threat(
            "The Gray Bull",
            place=_named(b, "Skalholt"),
            antagonist="Bishop Magnus Gizurarson",
            summary="Story seed (p. 112): Bard, fearing a supernatural attack, "
            "perhaps by Damhan-allaidh himself, asks the characters to 'rescue' "
            "Iceland's third guardian from the Dominion's grip.",
            secrets="The Bishop of Skalholt owns the bull and will not part with "
            "it, for its many fine calves have made him prosperous, so a raid "
            "may be needed. Let loose on pasture free of the Dominion it casts "
            "off its tameness and over a matter of weeks, faster in a magical "
            "aura, grows dramatically; it lets no human near, and takes up "
            "Iceland's defence again.",
        )
    )


def _scottish_giants(b: Builder) -> None:
    b.faction(
        "The Scottish Giants",
        summary="A dozen or so brutish giants from Scotland, stranded in Iceland "
        "and barely tolerated by its giants, who think them barbarians.",
        ruler="Geamhradh Grian",
        wants="To leave Iceland.",
        secrets=paragraphs(
            "Five appear at Bard's feast: Suil Aon (sool-oon, One-Eye), "
            "Creagcas (kreg kos, Rock-Foot), Beinn (beyn, Mountain), Sruth Dubh "
            "(sroo-doo, Black Tide) and their leader Geamhradh Grian (gev-ra "
            "grean, Winter Sun). They speak Pictish, Jotunn and Gaelic. Use the "
            "giants' statistics of p. 31; none has magical abilities.",
            "Damhan-allaidh laid a geas on the clan after Victor took the Carnac "
            "gateway, seeking another road to the temple: they cannot leave "
            "Iceland until they have visited the Temple of Thoth in the "
            "Kerlingarfjoll valley. They have found the valley but not the way "
            "in. Bard wants them gone and knows nothing of it (p. 111).",
            "Telling them frees Iceland of them but may hand Damhan-allaidh "
            "vital secrets. One answer: set the Kerlingarfjoll gatestone outside "
            "the covenant and walk them through briefly, so the geas is met and "
            "they still cannot find the way in. Freed, they go home and refuse "
            "him further service; otherwise he forces them to one last service "
            "(pp. 111, 125).",
        ),
    )


def _bards_kin(b: Builder, cave: Neighbour) -> None:
    b.faction(
        "Bard's Daughters",
        summary="The nine golden-haired daughters of Bard Snaefellsass, all healers.",
        place=cave,
        secrets="Giantesses. By his first wife: Helga, Thordis and Solrun. By "
        "his second: Ragnhild, Flaumgerd, Thora, Thorkild, Geirrid and Mjoll. "
        "Some, Helga among them, have great magic, others less; all have the "
        "Jotunn Affinity with Frost and the Healer talent. A child of one and "
        "a human is likely to be a trollson (p. 112).",
    )
    _sketch(
        b,
        "Solrun",
        age=None,
        type="mythic companion",
        summary="A strikingly lovely woman with long golden hair, pale skin and "
        "very blue eyes, charming, guileless and full of stories.",
        secrets="Bard's daughter, sent to bring the characters to his feast; "
        "she calls herself his servant. She treats every admirer alike. She "
        "is a giantess with the Jotunn Affinity with Frost and the Healer "
        "talent, and turns up at need to rescue guests from the trolls (pp. "
        "107-108, 112).",
    )
    _sketch(
        b,
        "Thordis",
        age=None,
        type="mythic companion",
        summary="A golden-haired daughter of Bard Snaefellsass.",
        secrets="Paired with the party's leader at the feast, where she proposes "
        "the toast to the guests (p. 109). See Bard's Daughters.",
    )
    _sketch(
        b,
        "Helga Bardsdottir",
        age=None,
        type="mythic companion",
        summary="The eldest of Bard Snaefellsass's nine daughters, who does not "
        "live with him.",
        secrets="She has substantial magic, and quarrels constantly with a father "
        "much like her. Red-Cloak, Thorkel's eldest son, is drawn to her and "
        "cannot admit it, so it comes out as rivalry and spite: he once set "
        "her adrift on an ice floe in a storm (pp. 112-113).",
    )
    b.creature(
        "Thorkel Red-Cloak's Son",
        page="p. 112",
        realm="Magic",
        might=65,
        form="Corpus",
        size=6,
        place=cave,
        age="Irrelevant",
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(0, 6, -4, 0, 20, 25, -1, -1),
            "traits": {"Quarrelsome": 4, "Hot-Headed": 6},
            "reputations": {"Chief of the Clan of Hrym (Iceland's giants)": 6},
        },
        vis=[BodyVis(12, "Corpus", "a giant's (p. 31)")],
        appearance="Forty feet tall, a twisted parody of a face under a mop of "
        "straight black hair, with a pronounced limp.",
        notes="Bard's half-brother and leader of the clan of Hrym.",
        secrets=paragraphs(
            "Their mother Mjoll married the giant Red-Cloak after the giant-king "
            "Hardverk killed her first husband. Bard broke Thorkel's leg in a "
            "duel. Violent, unprincipled and cunning, he has a bad name as a "
            "troublemaker; humans annoy him, no more (p. 113).",
            "Printed abilities, described and not built: External Soul, Jotunn "
            "Affinity with Frost (blizzards) 20, Curse (bad luck) 10, Transform "
            "(into rocks) 15, Speak Jotunn (Clan of Hrym) 8, Potency 8. The book "
            "gives him no combat table.",
            CORPUS_FORM,
        ),
    )
    b.faction(
        "Thorkel's Sons",
        summary="Six giants of the clan of Hrym, sons of Thorkel and much like "
        "him: Red-Cloak, Solvi, Svadi, Ox-Thorir, Asvald and Skeggi.",
        place=cave,
        ruler="Thorkel Red-Cloak's Son",
        secrets="All share his temper, though Ox-Thorir finds humans intriguing "
        "and wants to know more. Red-Cloak, the eldest, torments Helga, Bard's "
        "daughter, because he is drawn to her (p. 113).",
    )


# -- Chapter 14 --


def _glittering_plains(b: Builder) -> None:
    snaefell = _named(b, "Snaefelljokul")
    plains = _site(
        b,
        "Glasvellir",
        summary="The Glittering Plains, an underworld spoken of in old tales.",
        inside=snaefell,
        levels=[
            Builder.level(
                "The Glittering Plains",
                8,
                notes=hidden(
                    "",
                    "A magical regio of level 8 with no lower levels, under the "
                    "glacier in Snaefell's central crater. On or around the last "
                    "day of June at midday the shadow of Scartaris peak falls on "
                    "the caldera glacier, the ice breaks, and a 2,800-foot shaft "
                    "opens until the third sunset after. No roll is needed to "
                    "enter. Cut off from the mundane realm: Leap of Homecoming "
                    "and any spell or item for communication fail. The only sure "
                    "ways home are the way in and the Obsidian Gate (pp. 115-116).",
                ),
            )
        ],
        secrets=paragraphs(
            "The road (pp. 115-116): the glacier has a Magic aura of +3 and the "
            "shaft +4, which cannot be found at other times. A steep tunnel runs "
            "east by southeast for a day and a half to a fork. The eastern way "
            "goes on two days, then rises to a dead end a day later, by which "
            "time the entrance has sealed. The western way goes a day and meets "
            "a hole in the wall jetting hot, drinkable water, from a fast river "
            "beyond a few feet of granite; the aura is +5 here, and the stream "
            "shows the road. Then two days southwest, level, past side tunnels "
            "that all fail, and a near-vertical crack of a stair for two and a "
            "half days, the stream a torrent, into a cavern with a barely "
            "visible roof and an aura of +8.",
            "Other tunnels lead out, none known to go anywhere, and digging by "
            "spell is as haphazard.",
            "Gudmund's realm has plains of golden barley and lush growth that "
            "glow softly. The arrival bank is about 200 yards wide under the "
            "cavern wall; the river is nearly 300 yards across and far too fast "
            "to swim, though it has cooled. Those swept off and able to stay "
            "afloat (Str + Swim) reach Geirrod's bank. A day downstream a bridge "
            "of what seems solid gold crosses it, or magic and ropes will serve. "
            "On the far side the barley stands eight feet tall, goats match "
            "cows, and cows match elephants (p. 116).",
            "Small families of twelve-foot giants herd and reap along the river "
            "and feed the city far to the southeast, where about three hundred "
            "families live in luxury under Gudmund. Most can shapeshift and have "
            "no other magic (p. 116).",
            "Gudmund's wonders (p. 117): a many-coloured waterfall and a cave of "
            "perfect echoes; a hall being built of gold studded with gems, from "
            "nuggets the river leaves on its banks; the hunt for immense boar in "
            "thick forest; a spring on a rocky hillock that tastes of the finest "
            "honey-mead, a draft of it holding 3 pawns of Creo vis and granting "
            "the Free Expression virtue for a day; the village of humans; and a "
            "day-long feast with the court's illusions.",
        ),
        aura=8,
    )
    b.faction(
        "The Humans of Glasvellir",
        summary="A village descended from people who strayed into Glasvellir "
        "centuries ago.",
        place=plains,
        secrets="They live in peace with its giants, speak West Norse and keep "
        "the heathen Norse gods. Einar Gamlisson settled here and started a new "
        "family. Geirrod's people raided the village lately and took several "
        "children as slaves or meat, Einar's among them; questions are referred "
        "to Gudmund (p. 117).",
    )
    b.faction(
        "Gudmund's People",
        summary="The fair folk of Glasvellir, more courtiers than warriors.",
        ruler="Gudmund",
        place=plains,
        secrets="Size +3, bigger than trolls, far smaller than giants proper. "
        "They usually have no magic but Shapechange in a handful of forms. "
        "About one in twenty is magically powerful, with the full range of "
        "trollsynir abilities and often Jotunn Affinities; these are usually "
        "his men-at-arms. The court has experts in illusion. His twelve sons "
        "attend him, all in red like their father (pp. 116, 119).",
    )
    b.creature(
        "Gudmund of Glasvellir",
        page="p. 118",
        realm="Magic",
        might=75,
        form="Corpus",
        place=plains,
        level=1,
        confidence=CONFIDENCE,
        appearance="Twenty feet tall, extraordinarily handsome, golden-haired "
        "and blue-eyed, in white with a rich scarlet cloak.",
        notes="King of the Glittering Plains, a gracious host in the best Norse "
        "manner, generous, forgiving and eager to supply his guests' needs.",
        secrets=paragraphs(
            "An extremely ancient giant who calls himself the son of Mimir, "
            "which would make him cousin to Odin (Mimir's sister Bestla being "
            "Odin's mother). The claim cannot be tested. He has a wide range of "
            "powers, but does not own the regio or control its bounds. The book "
            "says no other characteristics should be needed (p. 118).",
            "He may be magical or faerie: lineage and manners suggest fay, yet "
            "like landvaettir he is at home in a magic realm. The book leaves "
            "it deliberately open; Magic here is the printed realm of the regio, "
            "not a ruling.",
            CORPUS_FORM,
        ),
    )
    geirrodargard = _site(
        b,
        "Geirrodargard",
        summary="The land beyond the icy Hemra River on the north of the "
        "Glittering Plains.",
        secrets=paragraphs(
            "The sky seems dark red, thin mist lies on black soil and blasted "
            "plants, and packs of immense dogs roam so that almost nothing "
            "lives outside the city. There is one ford over the Hemra, about "
            "five miles from the city (p. 117).",
            "The obsidian-walled city is over five miles across, its walls three "
            "hundred feet high. Over two thousand trolls live there, with about "
            "five hundred human slaves, in ruin and decay under smoke that cuts "
            "sight to under fifteen paces. Visitors must trick their way in (p. "
            "118).",
            "One thing stands whole, hidden at the centre: a ziggurat over five "
            "hundred feet high, seemingly cut from a single block of obsidian, "
            "three golden winged sphinxes guarding its triple stairs, its one "
            "chamber at the summit behind an iron door. Its residents never go "
            "near it and have forgotten what it was (pp. 118, 130).",
            "The Hemra ford is where Einar stands with the Norns (p. 118).",
        ),
        inside=plains,
        level=1,
    )
    b.creature(
        "Geirrod",
        page="p. 118",
        realm="Magic",
        might=65,
        form="Corpus",
        place=geirrodargard,
        level=1,
        confidence=CONFIDENCE,
        appearance="A six-headed troll.",
        notes="King of Geirrodargard, Gudmund's brother and his enemy.",
        secrets=paragraphs(
            "Not as strong as his brother, but formidable. He has a special "
            "power over fire: he handles molten metal bare-handed and flings it "
            "in combat. He has an External Soul, so unless the magi have made a "
            "Setna's Blade for him he survives a battle (pp. 118, 127-128). He "
            "knows where Damhan-allaidh's soulstone is. No other statistics are "
            "printed.",
            CORPUS_FORM,
        ),
    )
    _sketch(
        b,
        "Jarl Agdi",
        age=None,
        type="mythic companion",
        summary="Geirrod's lieutenant, a troll.",
        secrets="He rules Geirrod's people with an iron fist (p. 118).",
    )
    b.faction(
        "Geirrod's People",
        summary="The trolls of Geirrodargard, shorter than Gudmund's folk, "
        "twisted and ugly, as mean and petty as any troll.",
        ruler="Geirrod",
        place=geirrodargard,
        secrets="Physically identical to trolls, kin to those the characters "
        "know. Many have a Jotunn Affinity with Fire and many of the females the "
        "Gift of the Magic Arts (p. 119). Their human slaves, about five "
        "hundred, have been hearing the Aesir religion from Einar (p. 127).",
    )
    b.faction(
        "The Norn Landvaettir",
        summary="Spirits of fate called up by orlog-galdor, seen as countless "
        "shadowy shapes about a lady.",
        place=plains,
        realm="Magic",
        secrets="Einar stands high among them, and their lady will help him. "
        "They can pass the characters off as human slaves and hide them from "
        "Second Sight. Attacking Einar enrages the lady and her court (p. 118).",
    )
    _sketch(
        b,
        "Kar Liefsson",
        age=None,
        summary="A peddler of household goods who carries the Snaefellsnes "
        "gossip from farm to farm.",
        secrets="He brings word of the dragon rumour and of Blund's tall "
        "machine, and nearly took a beating for asking about it (p. 114).",
    )
    _sketch(
        b,
        "Thorodd Gamlisson",
        age=None,
        summary="A farmer on the north side of Snaefell who keeps his own counsel.",
        secrets="Einar's brother. He says nothing of Einar until threatened, by "
        "force or magic. Then he says Einar has gone back to the Glittering "
        "Plains, beyond reach, and under more pressure that the way in lies in "
        "Snaefell's central crater. He knows nothing but the reasons for the "
        "vendetta (p. 115).",
    )
    dormant(
        b.threat(
            "The Glittering Plains",
            place=plains,
            antagonist="Einar Gamlisson",
            summary="Two years before the dragon eggs hatch, a rumour of a horde "
            "of dragons sets the Snaefellsnes farmers against the nest, and the "
            "man behind it can at last be followed (pp. 114-119).",
            secrets=paragraphs(
                "The galdraman Einar Gamlisson stirs up the farmers and is gone "
                "before the magi come. Pan Caudarax killed his first wife and "
                "their two children, and he has killed at least one of the "
                "dragon's. His honour is partly satisfied, so terms are possible: "
                "a settlement at the hreppur with compensation each way, even "
                "each fostering the other's child (p. 118).",
                "What matters to him now is his living children, whom Geirrod's "
                "people took. Without the characters' help he dies trying to "
                "save them (p. 119).",
            ),
            stages=[
                S(
                    "A plot is hatching",
                    at=1,
                    season="Summer",
                    clues="Around mid-July the peddler Kar Liefsson tells of "
                    "dragons coming to Snaefellsnes, and of a tall wooden device "
                    "at Blund's farm with ropes, pulleys and a huge iron-tipped "
                    "stake pointing down: a pile driver to skewer the infants "
                    "in their shells. Covenfolk who visit the nest may bring the "
                    "news instead.",
                ),
                S(
                    "Blund's farm",
                    at=2,
                    clues="Blund has left with labourers and householders. Una "
                    "says one Einar Gamlisson stayed a night, warned them, and "
                    "told Blund to go and look at the pits himself.",
                ),
                S(
                    "The pile driver",
                    at=3,
                    clues="Unless the magi are very swift, the driver stands "
                    "over the first pit and the stake has just cracked the "
                    "shell; one more blow will skewer the wounded infant. Guards "
                    "may delay them. Mob rule should not be underrated.",
                    stopped="Talk or force stops Blund, ideally without telling "
                    "too much, and the dragonet is calmed and tended.",
                    ignored="Blund has few days left if he harms one of the brood.",
                ),
                S(
                    "Einar's journey",
                    at=4,
                    clues="A man alone is remarked on. He rode west toward "
                    "Snaefell, to his brother Thorodd's farm. The crater shows no "
                    "entrance; Bard or Pan Caudarax can say it opens three days "
                    "a year, so the magi wait a year.",
                ),
                S(
                    "A long way down",
                    at=5,
                    clues="The shaft, the tunnels and the river (see Glasvellir).",
                ),
                S(
                    "Seven days with Gudmund",
                    at=6,
                    clues="Asked about Einar, Gudmund looks troubled and says to "
                    "ask tomorrow, for six days, showing a new wonder each day. "
                    "On the seventh he explains: he hoped they would stay. Einar "
                    "came years ago in sorrow and settled in the human village, "
                    "and was last seen going into Geirrod's realm. Gudmund means "
                    "to avenge the raid in his own time, and thinks anyone "
                    "following Einar throws his life away. He had not mentioned "
                    "Geirrod, with whom his people are at open odds; the raid "
                    "looks like a prelude to battle.",
                ),
                S(
                    "Einar's preparations",
                    at=7,
                    clues="On the road to the Hemra ford they find Einar "
                    "bargaining with a landvaettir lady amid shadowy shapes, "
                    "using orlog-galdor to learn of his children and to cloud "
                    "the trolls' sight.",
                    ignored="Attacking him brings the lady's anger on the players.",
                    turned="They can talk instead (see this story's secrets).",
                ),
                S(
                    "Rescue",
                    at=8,
                    clues="Geirrod's feast to rally his people against Gudmund "
                    "will have the captured children roasted as its centrepiece. "
                    "There are about three days. The storyguide fills in the "
                    "rescue. The Norns can pass the characters as slaves; Veil "
                    "of Invisibility with a Group version of Seven League Stride "
                    "makes it trivially easy.",
                    stopped="The rescue humiliates Geirrod, wins great favour "
                    "with Gudmund, and makes Einar more than willing to settle "
                    "with Pan Caudarax.",
                    ignored="Einar dies in the attempt.",
                ),
            ],
        )
    )


# -- Chapter 15 --


def _brighdes_gauntlet(b: Builder) -> None:
    dormant(
        b.threat(
            "Brighde's Gauntlet",
            place=_named(b, "Sea Temple Sanctum"),
            antagonist="Hetep",
            summary="About twenty years into the saga Brighde's training ends: "
            "Victor leaves her body and she is set down alone in a remote part "
            "of Flanders for her Gauntlet, to cast out the demon within her (pp. "
            "120-124).",
            secrets=paragraphs(
                "Victor's plan. Demonic deceit defeats magic, but demons can be "
                "fooled, and only Hetep knows where Damhan-allaidh lies, whom "
                "Victor means to see destroyed. For one season a year he has "
                "taught her the Arts, and for the other three how to fight the "
                "demon he locked in her. On leaving her he goes back to his "
                "own body, still preserved in his Scartaris lab behind a ward "
                "that falls only at his death. Brighde lets Hetep seem to win; "
                "the player magi follow to the lair; she Leaps home by a waiting "
                "spell into the restored ward; Hetep is held in Victor's body, "
                "and Victor destroys it, holding the spirit for the Thothian "
                "Watchers (p. 84). That is his death and his choice, and it "
                "frees Brighde.",
                "Hetep's plan. He has learnt to break free of her and can block "
                "the Leap. He bides his time; with Victor gone he means to take "
                "another host, kill her and escape.",
                "If Brighde is a player character whose player refuses, Hetep "
                "escapes into one of the covenfolk and is pursued instead (p. "
                "121).",
                "The story should end with Damhan-allaidh and Hetep escaping. If "
                "Victor knew of Hetep's threat to the Magic Realm he would "
                "destroy himself at once, but nobody knows of it yet (p. 122).",
            ),
            stages=[
                S(
                    "Council meeting",
                    at=1,
                    clues="Victor calls a dreamscape council for the following "
                    "spring and explains the plan. Brighde, raised Tytalus and "
                    "fighting the demon alone under his eye for three years, is "
                    "sure of herself. She has made a mirror showing whatever she "
                    "sees, even under Hetep, who does not know of it, and it "
                    "goes to the players. Other demons fall outside the "
                    "Gauntlet, so they may help her against those.",
                ),
                S(
                    "The gauntlet",
                    at=2,
                    season="Spring",
                    clues="Hetep takes her and heads west. He meets the demonic "
                    "crow Whisper (p. 83), who tells him Damhan-allaidh's last "
                    "location in a tongue Brighde cannot understand, and "
                    "resolves to take his old pawn as a host. The mirror lets "
                    "the players see he is making for Old Vindolanda. If she "
                    "tries the Leap he blocks her, and that fight does not end "
                    "before Damhan-allaidh is found.",
                ),
                S(
                    "Old Vindolanda",
                    at=3,
                    clues="See p. 93. Hetep has dug up the Lundy Island gatestone "
                    "and is freeing Damhan-allaidh; his minion Ammon guards the "
                    "gateway and must be beaten.",
                ),
                S(
                    "Damhan-allaidh's tomb",
                    at=4,
                    clues="Hetep fills the chamber with air by Creo Auram, digs "
                    "the body from the rubble, abandons Brighde, possesses his "
                    "ally and pours in Infernal Might. Within a few rounds "
                    "Damhan-allaidh wakes and tries to kill her before she can "
                    "Leap.",
                    stopped="Quick players may save her. A player Brighde may "
                    "fight it out as a dreamscape hunt for the Leap's hidden "
                    "trigger, and should get away at the last moment unless "
                    "very slow. A non-player Brighde may die here.",
                ),
                S(
                    "Victor's farewell",
                    at=5,
                    clues="Brighde is held in the lab ward with no demon in it, "
                    "and only Victor's end frees her. He gives what last advice "
                    "he can and wishes his filia well.",
                    ignored="If Brighde dies he stays in his body, and will not "
                    "possess anyone again, willing or not, having grown uneasy "
                    "at the sin of it. Trapped in ice, he speaks through Creo "
                    "Mentem and uses his Morphean Landscape to hold meetings "
                    "and teach them for the final conflict.",
                ),
            ],
        )
    )


# -- Chapter 16 --


def _spider_through_mist(b: Builder) -> None:
    kerlingarfjoll = _named(b, "Kerlingarfjoll Valley")
    dormant(
        b.threat(
            "Spider Through Mist",
            place=kerlingarfjoll,
            antagonist="Damhan-allaidh and Hetep",
            summary="Damhan-allaidh, possessed by Hetep, breaks into the "
            "Kerlingarfjoll valley and tries to pass the Obsidian Gateway; if he "
            "does, the sacred stelae are corrupted (pp. 125-126). Best about "
            "four years before the players can finish the Obsidian Gate ritual.",
            secrets=paragraphs(
                "His allies depend on the storyguide and on Feast of Thanks: "
                "the Scottish giants are forced to serve unless their geas was "
                "met, in which case they have gone home and refuse him. Side "
                "stories may have the characters foil his search for allies.",
                "Hetep knows a break in the ward, and a ritual like Tearing the "
                "Mystic Veil (Wizard's Grimoire Revised) that opens a tear wide "
                "enough for giants. It takes an hour to perform and ten minutes "
                "to widen, with a huge disturbance on both levels.",
                "If the stelae fall, corruption spreads to all magical writing "
                "in the world, far slower than if Hetep did it directly, with "
                "much variation. An average summa turns in as many years as the "
                "experience points it holds (55 for level 10); a Tractatus or "
                "Liber Quaestionum in years equal to its Quality; an average "
                "Authority in over 365. Books written meanwhile are corrupt "
                "from the start (p. 126).",
            ),
            stages=[
                S(
                    "Foreshadowing",
                    at=1,
                    season="Summer",
                    clues="Near the end of June, Per + Premonitions 6+ warns of "
                    "danger; failing their own insight, players roll Intelligence "
                    "6+ to recall that the Gate may be opened and the Glasvellir "
                    "tunnels reached about now. Guards might go to the valley "
                    "and the Snaefell caldera.",
                ),
                S(
                    "The assault",
                    at=2,
                    clues="At midnight on the day the ritual can be performed he "
                    "and his allies enter the mundane level of the valley, by a "
                    "gap only Hetep knows. Then the tear, which gives guards "
                    "time to warn Scartaris.",
                    ignored="If the magi take more than ten minutes, the first "
                    "giant through tries to smash the trilithon linked to the "
                    "covenant.",
                    stopped="With the Scottish giants the fight is very hard, and "
                    "if they are ahead in a close battle they may let the "
                    "characters retreat. If he is losing or falls, Hetep casts "
                    "Leap of Homecoming; the giants then offer an honourable "
                    "truce. Other allies panic, cannot leave the regio level, "
                    "and can be dealt with at leisure.",
                ),
                S(
                    "Damhan-allaidh succeeds",
                    at=3,
                    clues="He opens the Gate, steps through and smashes it at "
                    "once, drives off its guardian spirit Setna, and Hetep "
                    "finishes corrupting the stelae (his Corrupt Knowledge "
                    "power, p. 137). He stays, still possessed, to guard them.",
                    ignored="Run Into the Gateway's first section.",
                ),
                S(
                    "Damhan-allaidh fails",
                    at=4,
                    clues="He flees to Snaefell and the Glasvellir tunnels, "
                    "claims Geirrod's protection and tries the Obsidian Temple "
                    "from outside. Followers past the city gates face Geirrod "
                    "and his troll army, until he betrays Geirrod.",
                    ignored="Run Into the Gateway's second section.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Spider Among the Trolls",
            place=_named(b, "Snaefellsnes"),
            antagonist="Damhan-allaidh",
            summary="Story seed (p. 125): trolls on Snaefellsnes, the thickest "
            "concentration in Iceland, are being gathered under one leader.",
            secrets="Needing allies, Damhan-allaidh tries to unite the Western "
            "Quarter's trolls, no easy task with so territorial and quarrelsome "
            "a people, and the characters live among them.",
        )
    )
    dormant(
        b.threat(
            "Leiken and the Mara",
            antagonist="Leiken",
            summary="Story seed (p. 125): old women ride the covenfolk through "
            "terrifying dreams, sapping their strength.",
            secrets="The mara are evil landvaettir, witch-spirits, led by "
            "Leiken, among the most powerful of the yarthkin (p. 33), who has "
            "joined Damhan-allaidh. After a few attacks Victor may be persuaded "
            "to let the characters fight them on their own terms in his Morphean "
            "Landscape. If he is dead, it is harder.",
        )
    )


# -- Chapter 17 --


def _into_the_gateway(b: Builder) -> None:
    temple = _site(
        b,
        "The Obsidian Temple",
        summary="Nothing is known of this place.",
        secrets=paragraphs(
            "Where Thoth hid the first magical writings, reached from the "
            "summit chamber of the ziggurat in Geirrodargard or by the Obsidian "
            "Gateway. It is neither in the mundane world nor a regio, but a cut-"
            "off part of the Magic Realm with a +10 aura, in which magical "
            "abilities may break out in small ways; how strange is the "
            "storyguide's choice. There is no way on into the Realm: Setna "
            "warns those who try, and beyond the walls is only the Twilight "
            "Void, at the least an automatic temporary Twilight (p. 130).",
            "Three golden sphinxes guard the entrance, then come seven gates: "
            "iron, bronze, wood, ivory, ebony, silver and gold. Each opens by "
            "ritual from cryptic instructions on it (pp. 130-132). The roll is "
            "the best Intelligence plus the two best of Magic Theory or "
            "equivalent, Occult Lore, Enigmatic Wisdom, Philosophiae and Artes "
            "Liberales, among all who can really contribute, plus the highest "
            "quality die anyone rolls; Mythic Intelligence adds 5 and Mythic "
            "Feats do not apply. A failure spends the base time. Each full 3 "
            "points above the difficulty halves the time.",
            "Iron and Bronze, one week each, difficulty 18 and 21. Wood and "
            "Ivory, one month, 24 and 27. Ebony and Silver, one season, 30 and "
            "33. Gold, one year, 36. The doors cannot be damaged and are beyond "
            "Hermetic magic (p. 132).",
            "The Sanctum of the Stelae (p. 131): a black hemisphere 343 cubits "
            "(about 150 paces) across. The twin of the Obsidian Gateway stands "
            "at its centre, and before it a huge seated statue of Setna in "
            "gneiss, an ibis for Thoth at the back of his head; his spirit "
            "usually dwells in it. Around the wall stand seven emerald pillar "
            "stelae, seven cubits (about 3 paces) high, their hieroglyphics "
            "unknown. To a student Setna accepts they shift into his own tongue. "
            "They allow Arcane Experimentation (WGRE pp. 83-87) with no vis, "
            "lab or control rolls, the Research Lab Total at +10 for the aura; "
            "or they serve as a Quality 10 Authority on any magical Art or "
            "Knowledge. One student at a time, for no more than four seasons "
            "each.",
        ),
        aura=10,
    )
    b.creature(
        "The Golden Sphinxes",
        page="p. 130",
        realm="Magic",
        might=100,
        form="Terram",
        size=5,
        how_many="Three",
        place=temple,
        block={
            "characteristics": characteristics(3, 5, 3, 3, 15, 20, 15, 10),
        },
        attacks=[b.attack("Claws", 20, 25, 10, 25)],
        soak=45,
        tires=False,
        powers=[
            b.power(
                "Regeneration",
                1,
                9,
                "Terram",
                level=30,
                does="CrTe 30. Heals up to three wound levels a round at a Might "
                "point each, needing no action.",
            ),
            b.power(
                "Sense Intents",
                0,
                10,
                "Vim",
                level=100,
                does="InVi 100. Senses the presence of benign or malevolent forces.",
            ),
            b.power(
                "Binding Word",
                5,
                5,
                "Corpus",
                level=30,
                does="ReCo 30. Holds any person or group to its word by "
                "controlling their bodies.",
            ),
            b.power(
                "Thoughts Within the Babble",
                0,
                10,
                "Mentem",
                level=20,
                does="InMe 20. Speaks and understands any language.",
            ),
        ],
        vis=[BodyVis(50, "Vim", "in each, if destroyed")],
        appearance="Golden statues of winged sphinxes that come alive to fight "
        "any threat.",
        notes="Each can attack five individuals at once within reach of its "
        "claws. Body levels OK 0, 0, 0, -1, -1, -3, -3, -5, -5, Destroyed. The "
        "book prints Dex 15 without a sign, and Might Form Terram is this "
        "pack's reading.",
        secrets="The automata know of Setna's fate and of the corruption. Magi "
        "who think to explain themselves are let by, and defended on their "
        "way through the doors. Instead of harvesting vis they can be studied "
        "for liquid fire and true intelligence in automata (The Mysteries).",
    )
    b.creature(
        "Setna",
        page="p. 132",
        realm="Magic",
        might=120,
        form="Vim",
        place=temple,
        confidence=CONFIDENCE,
        block={
            "characteristics": {
                "intelligence": 5,
                "perception": 3,
                "presence": 3,
                "communication": 3,
            },
            "traits": {"Wise": 6, "Patient": 3, "Suffers Fools Gladly": -3},
        },
        powers=[
            b.power(
                "Words of Power",
                0,
                0,
                "Vim",
                does="Any spell effect the storyguide likes, up to half his "
                "current Might. Effects that would need vis cost 1 Might per "
                "magnitude; others cost nothing.",
            ),
        ],
        appearance="Usually speaks through his gneiss statue, which he animates "
        "for first impressions, though he can leave it.",
        notes="Might Form Vim is this pack's reading.",
        secrets=paragraphs(
            "Might 120, reduced to 30 by long battle with Hetep's corruption.",
            "Son of Rameses II, the most learned man in Egypt and perhaps its "
            "greatest magician, schooled in secret texts beyond the priests of "
            "Amen-Ra. Proud, he took the book of Thoth from Nefrekeptah's tomb "
            "despite warnings; a terrible vision from Thoth made him return it "
            "and do penance. He rose in Thoth's favour and was given the "
            "stelae's guardianship, which his spirit has held for nearly two and "
            "a half millennia.",
            "He has always seen Hetep's shadow in the magicians who tried to "
            "bring the poison in, until Damhan-allaidh. For four centuries he "
            "has fought it, and he can no longer bar Damhan-allaidh or stand "
            "against him. As the first to try to codify magical thought, he "
            "has become the embodiment of man's understanding of magic.",
            "Setna's Blade, PeVi 40, R: Spec, D: Spec (Constant Use), T: Ind. He "
            "supplies a papyrus scroll. It can only be invested in a weapon, "
            "never made a spell, and each weapon is for one named victim. Driven "
            "through the heart, whatever Magic Resistance stands against it, it "
            "destroys the soulstone and kills. In the end he can restore any "
            "magus Hetep's Sunder the Magician's Spirit has maimed, Iain "
            "included (p. 129).",
        ),
    )
    b.creature(
        "Hetep's Undead Form",
        page="p. 128",
        realm="Infernal",
        might=60,
        form="Corpus",
        size=1,
        place=temple,
        confidence=CONFIDENCE,
        block={
            "characteristics": characteristics(0, 2, 0, 3, 10, 15, 5, 8),
            "traits": {"Greedy": 5, "Secretive": 6, "Capricious": 6},
        },
        attacks=[
            b.attack("Bite", 16, 13, 16, 19),
            b.attack("Claw", 16, 13, 16, 16),
        ],
        soak=26,
        fatigue_levels="Tireless",
        tires=False,
        powers=[
            b.power(
                "Sunder the Magician's Spirit",
                10,
                -2,
                "Vim",
                level=50,
                does="PeVi 50. As Hetep's own power of that name: a landed "
                "blow wounds the victim's Gift, against Magic Resistance with "
                "Vim added to Parma.",
            ),
            b.power(
                "Shapechange",
                0,
                8,
                "Corpus",
                level=40,
                does="MuCo(An) 40. Gives a host he possesses his own beast shape.",
            ),
            b.power(
                "Raise Corpse",
                1,
                7,
                "Corpus",
                level=25,
                does="ReCo 25. Raises anyone he slays as walking dead.",
            ),
            b.power(
                "Infernal Spell",
                0,
                8,
                "Vim",
                level=30,
                does="The equivalent of spontaneous spells to level 30, at 1 "
                "Might per magnitude.",
            ),
        ],
        appearance="Damhan-allaidh's body, more hideous than in life: a huge "
        "skinless baboon running with putrefaction.",
        secrets="Hetep is bound into his former servant's shell. Destroying it "
        "lets the Thothian watchers capture him at once (p. 128). Body levels "
        "OK, 0, 0, -1, -3, -5, Incapacitated. Presence is printed N/A, shown as "
        "0. Might Form Corpus is this pack's reading.",
    )
    dormant(
        b.threat(
            "Into the Gateway",
            place=temple,
            antagonist="Damhan-allaidh and Hetep",
            summary="The magi finish Ealasaid's work on the Obsidian Gateway and "
            "must break into the Obsidian Temple to destroy the corrupted "
            "stelae, or defend them (pp. 127-132). Which half is played turns on "
            "the end of Spider Through Mist. It closes the saga.",
            secrets=paragraphs(
                "If they succeed, Hetep is imprisoned and the Magic Realm saved. "
                "Victor, if alive, says goodbye and dispels his ward. With "
                "stelae uncorrupted the magi could win untold power and fame; "
                "the storyguide may consider which Hermetic Limits are only "
                "Hermetic and which are limits of Magic, and from there the saga "
                "is his (pp. 129-130).",
                "Without Einar and Gudmund's support either assault is much "
                "harder. Einar has been teaching the Aesir religion to the "
                "human slaves and plans a rising, and they can poison the "
                "trolls wholesale when the gates open.",
            ),
            stages=[
                S(
                    "Corrupted: the wasteland",
                    at=1,
                    clues="The spirit of the Gate sets them down at the edge of a "
                    "corrupted waste in the Magic Realm, not at the Temple. "
                    "Setna greets them warmly, begs their help and shows them "
                    "Hetep's poison at work. He teaches Setna's Blade, tells of "
                    "the other entrance at the ziggurat's summit, and gives "
                    "directions to the Glittering Plains, knowing nothing of "
                    "who lives there now. They may go back to Kerlingarfjoll to "
                    "prepare.",
                ),
                S(
                    "Corrupted: assault on Geirrodargard",
                    at=2,
                    clues="With Einar and Gudmund, they sneak in as Gudmund "
                    "besieges the city, and need only open the gates and hold "
                    "them while the slaves' poison works. The fight at the gate "
                    "should be hard.",
                    stopped="Geirrod orders his people to stop and sues for "
                    "terms. Unless a Setna's Blade was made for him he lives, "
                    "and he gives up Damhan-allaidh's soulstone, frees the "
                    "slaves and opens the ziggurat; Gudmund takes tribute in "
                    "gold. Destroying the soulstone forces Hetep to Raise Corpse "
                    "at once, binding him to the body so that he can possess no "
                    "one; destroying the body lets the Thothian spirits take "
                    "him.",
                ),
                S(
                    "Corrupted: into the Obsidian Temple",
                    at=3,
                    clues="Sphinxes and seven gates (easier with Geirrod beaten) "
                    "lead to Damhan-allaidh and Hetep. If Damhan-allaidh still "
                    "lives Hetep may try to possess magi and strong companions; "
                    "resisted, he falls to the Thothian spirits.",
                    stopped="At the last the magi smash the emerald stelae to "
                    "end the spread of the corruption.",
                ),
                S(
                    "Uncorrupted: the sanctum",
                    at=4,
                    clues="The Gate spirit takes them to the stelae sanctum. "
                    "Setna greets them, knows only that Damhan-allaidh is coming "
                    "through the gates, and gives the Blade scroll. Investigation "
                    "in Glasvellir shows what has passed. The sphinxes barred "
                    "him, Geirrod would not help, so he bound Geirrod in magical "
                    "iron, left snakes dripping venom on his faces to learn "
                    "where the soulstone is, and made himself king of the "
                    "trolls. He has since destroyed the three sphinxes, at great "
                    "cost in trolls, and is at the ivory gate, the others left "
                    "open.",
                ),
                S(
                    "Uncorrupted: a web for the Spider",
                    at=5,
                    clues="They may trap him in the sanctum as he opens the "
                    "golden door. Setna conjures food and drink while they study "
                    "the stelae.",
                ),
                S(
                    "Uncorrupted: cutting the Spider's thread",
                    at=6,
                    clues="Or they return by the Gate, which they may do at will, "
                    "and go to Glasvellir, tell Einar and Gudmund, and open the "
                    "gates during the siege. The strongest trolls are dead or "
                    "maimed, so the city is lightly held. It should still be "
                    "hard, since success ends Damhan-allaidh and Hetep both.",
                    stopped="Gudmund frees his brother and leads the slaves to "
                    "his realm, with a substantial tribute.",
                    turned="They may do both at once, some defending the sanctum "
                    "and some striking from outside, or may have chased him into "
                    "Glasvellir after the valley fight. End it dramatically.",
                ),
            ],
        )
    )
