"""The saga's stories (Chapter Ten, with the threads Chapters Three, Five
and Eleven add), in paraphrase: each a threat whose stages lay out how
it unfolds if the troupe ignores, stops or turns it. Five are the
Tribunal's own plots (the Boar King, the Children of Odin, Augustina the
Traitor, the Lotharingian movement and the fixing of the Tourney); four
are the chapter's saga frames (A Romantic Saga, The Boar and the
Dragon, The Tradition of Kings, The Advance of the Dominion), so the
import form offers frames and plots side by side to begin.

Also the factions behind them (the Boar King's court, the Children of
Odin as a Mystery Cult with its scripts and Ordeals, the Cabal of
Frankish Gold, the Cabal of the Golden Coin and the Lotharingian
movement), the two places only this chapter describes, and the three
people only it names (Queen Skuld, Porphyrion and Salvirius). The Boar
King himself, a creature, lives in his court's summary until the app
has a bestiary.

`finish` ties the stories to the covenants, magi and places the other
parts made, found by name, and closes the Tribunal's summary with The
Noble Life, Tytalus Schemes and Salvirius's quests."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from . import Normandy

S = Builder.stage
P = Profile


def build(normandy: Normandy) -> None:
    _places(normandy)
    _people(normandy)
    _factions(normandy)
    _boar_king(normandy)
    _children_of_odin(normandy)
    _augustina(normandy)
    _lotharingia(normandy)
    _golden_coin(normandy)
    _frames(normandy)


# -- places --


def _places(normandy: Normandy) -> None:
    b = normandy.b
    normandy.places["boar_kings_hall"] = b.place(
        "The Boar King's Hall",
        summary="A timber stronghold in a faerie regio, reached from several dark, "
        "damp groves deep in the Tribunal's forests where the air is close and "
        "the sun hardly reaches the ground. From outside the groves show only "
        "gloom and rot; it takes days of travel to reach the forest's heart.",
        secrets="The hall is the Boar King's, and his court of faerie knights and "
        "courtiers camps there between hunts. Some of the plenty the court "
        "offers guests is glamour. The King learns each day roughly where "
        "and how many humans are in his forest, so visitors are expected "
        "long before they arrive.",
        realm="Faerie",
        status="Rumoured",
        known="Locally",
        levels=[
            b.level(
                "The Boar King's fortress",
                7,
                "Faerie",
                enter="Through one of the dark groves, if the King allows it",
                notes="The King has barred Hermetic hoplites from entering.",
            )
        ],
    )
    normandy.places["ships_of_flame"] = b.place(
        "The Ships of Flame",
        summary="Three small magical regiones along the Seine, each holding a Viking "
        "longship that burns without end as the pyre of a dead warlord. A "
        "regio opens only to someone drifting down the river in a burning "
        "boat on the day that warlord died; leaving needs only a swim to the "
        "bank. The fire needs no fuel and never consumes the ship, but it "
        "burns away anything brought in that magic does not protect, and "
        "anyone on deck suffers +20 fire damage each round, a magical attack "
        "of Penetration 30. A strong Perdo Ignem effect could put a fire out, "
        "and would probably destroy the regio with it.",
        secrets="Queen Skuld, Hierophant of the Children of Odin, lives here alone "
        "and keeps her laboratory on the deck of one ship. A cult initiate's "
        "first Quest is to reach a deck unaided and take an axe from a fallen "
        "warrior. Few others visit, as the days are hard to time, so Skuld "
        "speaks to her cult through Haunt of the Living Ghost.",
        realm="Magic",
        status="Rumoured",
        known="Locally",
        levels=[
            b.level(
                f"The {which} burning ship",
                6,
                "Magic",
                enter=(
                    "Drift down the Seine in a boat aflame on the death-day of "
                    "the warlord it holds"
                ),
                notes=notes,
            )
            for which, notes in (
                ("first", "Queen Skuld's laboratory is on its deck."),
                ("second", ""),
                ("third", ""),
            )
        ],
    )


# -- people only this chapter names --


def _people(normandy: Normandy) -> None:
    b, magi = normandy.b, normandy.magi
    if not _find(b.saga.characters, "Skuld", "Queen Skuld"):
        magi["skuld"] = b.magus(
            "Queen Skuld",
            covenant=None,
            house="house_ex_miscellanea",
            age=77,
            summary="Once an unremarkable Tytalus maga of Atramentum, Skuld left her "
            "House for Ex Miscellanea in 1178 and vanished a few years later, "
            "last seen sailing a small boat through the Channel towards "
            "Scandinavia. The Order believes she never came back. She looks "
            "about 37. (The book has her living at Atramentum before 1178, "
            "though Atramentum was founded only in 1200: a slip it leaves "
            "for the storyguide to settle.)",
            secrets="She returned in 1205 and lives in a regio on the Seine, on a "
            "burning longship, as Hierophant of the Children of Odin; she has "
            "been Mystagogue at every initiation so far. She claims descent "
            "from Rollo and means to be crowned maga-queen of a Normandy "
            "taken back from the French king. She may not be the Skuld who "
            "left at all, but an impostor: a faerie or magical creature, a "
            "powerful hedge wizard (perhaps of the Order of Odin), or a "
            "survivor of the Schism War. If the cult's Viking magic is not "
            "genuine, she may know it.",
            traits={"Driven": 3, "Proud": 2, "Secretive": 2},
        )
    if not _find(b.saga.characters, "Porphyrion"):
        magi["porphyrion"] = b.magus(
            "Porphyrion",
            covenant=None,
            house="house_tytalus",
            age=None,
            summary="A powerful Tytalus archmagus who came to Normandy from the Rome "
            "Tribunal three years ago and has lived alone since. He may ask "
            "to join a young covenant, bringing political and magical weight "
            "it could hardly refuse.",
            secrets="Tytali who have looked into him think he wants the House's "
            "leadership, before or more likely after Harpax or Buliste falls, "
            "and that joining a weak covenant serves that end. A third "
            "contender is the one thing that would make the two Primi work "
            "together.",
        )
    if not _find(b.saga.characters, "Salvirius"):
        normandy.magi["salvirius"] = b.magus(
            "Salvirius",
            covenant=None,
            house="",
            age=None,
            type="mythic companion",
            summary="Adviser to the Boar King, who looks about fifty and dresses as a "
            "hunter or woodsman. He keeps his own road, joins the court only "
            "when it is camped, and takes little part in its feasts. A huge "
            "scar, like the mark of a spear wound to the heart, crosses his "
            "chest, usually hidden. He can grant Virtues by setting a quest "
            "that demands a sacrifice: Strong Faerie Blood, Shapeshifter, "
            "Animal Ken, Faerie Blood, Second Sight and Wilderness Sense, and "
            "the storyguide may add Hermetic ones.",
            secrets="He may be a faerie, a magus turned faerie, a magus living at the "
            "faerie court, or a Diedne refugee from the Schism War. He can "
            "teach Diedne Magic, and uses the offer to mark a magus for a "
            "watcher who scries the road to the Hill of Martyrs in Paris.",
            traits={"Reclusive": 3, "Manipulative": 2},
        )


PROFILES: dict[str, Profile] = {
    "skuld": P(
        strong="int sta pre",
        native="French",
        arts={"Ig": 6, "Mu": 5, "Cr": 3, "Me": 3, "Re": 3, "Vi": 3, "Co": 2},
        abilities={
            "Area Lore: Normandy": (3, "the Seine"),
            "Living Language: West Norse": 4,
            "Leadership": (3, "cultists"),
            "Intrigue": 3,
            "Profession: Sailor": 2,
            "Order of Hermes Lore": 2,
        },
        virtues=[
            "Life Boost",
            ("Minor Magical Focus", {"focus": "Shape-shifting"}),
            "Life-Linked Spontaneous Magic",
            "Blood Haze",
            "Dark Secret",
            "Ambitious (Major)",
        ],
    ),
    "porphyrion": P(
        strong="int pre com",
        native="Italian",
        age=160,
        arts={"Re": 5, "Me": 5, "Pe": 4, "In": 4, "Vi": 4, "Im": 3, "Cr": 3},
        abilities={
            "Intrigue": (5, "House Tytalus"),
            "Certamen": 4,
            "Leadership": 3,
            "Order of Hermes Lore": 3,
            "Code of Hermes": 3,
        },
        virtues=["Strong-Willed", "Ambitious (Major)", "Proud (Minor)"],
    ),
}


def stats(normandy: Normandy) -> None:
    """Stat the magi this part made, from their profiles."""
    for key, profile in PROFILES.items():
        character = normandy.magi.get(key)
        if character is not None and character.type == "magus":
            apply(normandy.b, character, profile)


# -- factions --


def _factions(normandy: Normandy) -> None:
    b, world = normandy.b, normandy.world
    world["court_of_the_boar_king"] = b.faction(
        "The Court of the Boar King",
        summary=paragraphs(
            "A faerie the Gauls once worshipped, the Boar King is a big man "
            "with a boar's head and two great tusks that thicken his speech; "
            "his bare arms and chest carry abstract tattoos and bronze rings, "
            "and he wears hide trousers and a cloak and rides a wild horse "
            "bareback with faerie knights and courtiers at his side. He claims "
            "the Tribunal's forests, as other powers also do, hunts boar each "
            "autumn, and turns the hunt on hunters who take too much.",
            "Centuries ago House Diedne helped him guard his woods. He knows "
            "the House fell, has watched men and the Divine eat into the "
            "forest, and has decided that killing the odd greedy hunter "
            "changes nothing; he now looks for new Hermetic allies, most "
            "likely among Merinita and Bjornaer, to halt and undo the "
            "clearing of the forest. His offer copies the Forest Paths of the "
            "Rhine; whether it is a true one hardly matters given what his "
            "court can supply an ally.",
            "In brief, as the book gives him: Faerie Might 40 (Animal), Size "
            "+1, Reckless +3, Proud +2, Wrathful +1, known locally as King of "
            "the Forest and in the Order as an ally of House Diedne. He "
            "fights with boar spears and his tusks, is a master hunter and "
            "woodsman, and speaks Gaulish, Latin and Breton. His powers let "
            "him command the forest's beasts and plants, sense the human "
            "intruders in his forest each day, fall into a day-long rage that "
            "will not retreat or spare anyone, pin a victim helpless with a "
            "thrown spear until it is pulled out (a Heavy Wound), and appear "
            "anywhere in his forest. Each tusk holds 4 pawns of Animal vis.",
        ),
        secrets="Salvirius, his subtle adviser, sounds out the magi the King "
        "approaches and sets the quests by which the court grants Virtues. "
        "A Diedne magus thought dead in the Schism War is rumoured to ride "
        "with the court.",
        faction="Faerie court",
        decides="Its leader",
        ruler="The Boar King",
        realm="Faerie",
        rules="Take no more from the forest than it can spare; the King's word is law.",
        wants=(
            "Hermetic allies to replace House Diedne as wardens of his forests, "
            "and the advance of men and the Church driven back"
        ),
        offers=(
            "A share of the forest's power, Virtues through Salvirius's quests, and "
            "the court's resources, some of them glamour"
        ),
        place=normandy.places["boar_kings_hall"],
    )
    world["children_of_odin"] = b.faction(
        "The Children of Odin",
        summary=paragraphs(
            "A secret Mystery Cult whose magi call themselves heirs to the "
            "magic of the ninth-century Viking raiders. The pedigree is "
            "claimed, not real: the cult is barely ten years old. It is "
            "small, probably no more than half a dozen magi, and the Order "
            "has not found it. Members need a good Ignem score to survive "
            "their first Quest, which suits Flambeau, and Montverte magi "
            "descended from that covenant's Scandinavian founders are likely "
            "recruits. It is not the Order of Odin, only a cult claiming to "
            "have found some of its secrets.",
            "Initiation Scripts. The cult can initiate three Virtues: Life "
            "Boost (Minor Hermetic), Minor Magical Focus in shape-shifting "
            "(Minor Hermetic) and Life-Linked Spontaneous Magic (Major "
            "Hermetic). The Ordeals that go with them may leave the "
            "initiate with Blood Haze (Minor Hermetic: within a dozen paces "
            "of blood shed in violence the maga takes -10 to Formulaic magic "
            "and -3 to Concentration), Flawed Parma Magica against Vim "
            "(Minor Hermetic) or Deficient Technique in Creo (Major "
            "Hermetic).",
            "Initiation. Without the Mystery Cult rules, the Mystagogue sets "
            "the initiate a Quest of about a year, during which they suffer "
            "an Ordeal (a Flaw) and gain the Mystery (a Virtue); the "
            "instructions are an Initiation Script, a special Laboratory "
            "Text. The first Quest is to reach the deck of one of the Ships "
            "of Flame unaided and bring back an axe from a dead Viking. "
            "Raiding with Nordic Triumph has served as another.",
            "Nordic Triumph is the cult's ritual (MuMe(He)(Te) 65; Touch, "
            "Moon, Structure): cast aboard a ship, it turns her into a "
            "dragon-prowed longship and her crew into Viking warriors who "
            "follow the caster as their chief, fighting as a trained band "
            "though they gain no Abilities they lacked.",
        ),
        secrets=paragraphs(
            "Queen Skuld is Hierophant and has been Mystagogue at every "
            "initiation. Her aim is power: Normandy back in Norman hands and "
            "herself crowned its maga-queen as Rollo's heir. What draws other "
            "magi is not her politics but the Viking secrets she says she "
            "found in wrecks and ruins as a young maga.",
            "Thormod of Montverte is a leading member who practises the "
            "cult's Viking magic and uses his influence for it; he may be "
            "Skuld's kin or lover. If the cult truly descends from the Order "
            "of Odin, it may know rune magic, or a researcher may one day "
            "bring the runes into Hermetic theory; if it does not, Skuld may "
            "be lying to her followers.",
        ),
        faction="Other",
        decides="Its leader",
        ruler="Queen Skuld",
        rules=(
            "Secrecy; obedience to the Hierophant; advancement by initiation, a "
            "Quest and an Ordeal for each Mystery"
        ),
        wants="Normandy taken from the French crown, with Skuld crowned its maga-queen",
        offers=(
            "Viking magic: Life Boost, a shape-shifting Focus, Life-Linked "
            "Spontaneous Magic, and the ritual Nordic Triumph"
        ),
        place=normandy.places["ships_of_flame"],
    )
    world["cabal_of_frankish_gold"] = b.faction(
        "The Cabal of Frankish Gold",
        summary=paragraphs(
            "A Tytalan cabal working to make the Lotharingian Tribunal "
            "happen. Like every Tytalus cabal its members are anonymous to one "
            "another, meet in disguise or not at all, and may come from more "
            "than one Tribunal; they share the goal, not the reasons. Some "
            "honestly want the new Tribunal as a utopia for magi, Tytali "
            "above all, free of the weight of their old Peripheral Codes, "
            "and mean to found a new covenant there whether or not their "
            "own covenants join.",
        ),
        secrets="Augustina of Confluensis, the Traitor, belongs: she thinks the new "
        "Tribunal doomed but likes the principle that unhappy magi may "
        "break from an old Tribunal, and wants to see how the Order answers "
        "a challenge in its heartland. Prima Buliste joins only to keep her "
        "brother Harpax busy. At least one member is a saboteur, quietly "
        "souring relations between the movement's covenants.",
        faction="Other",
        rules="Membership anonymous; meetings in disguise or by letter and spell",
        wants="A Lotharingian Tribunal founded, each member for their own reasons",
        offers="Tytalan wit, gold and connections in two or more Tribunals",
    )
    world["cabal_of_the_golden_coin"] = b.faction(
        "The Cabal of the Golden Coin",
        summary="A cabal that fixes the Hermetic Tourney so its members take the "
        "best prizes. Tytali began it, but most members now come from other "
        "Houses. Several of the changes to the prize levels, put forward as "
        "points of tradition, were its work, meant to open gaps in the "
        "prizes it can exploit.",
        secrets="Members agree in secret which contests to throw so their teams "
        "place best. Some leave their covenant's team to field a separate "
        "one, which places remarkably well: a team of three young magi, each "
        "of a different covenant and House, has come fourteenth at the last "
        "three Tourneys. Late in a Tourney a member may quietly offer a "
        "covenant a fixed contest for a little vis.",
        faction="Other",
        rules="Members anonymous to outsiders; agreements made in secret and kept",
        wants="The Tourney's prizes, the tropaeum leases above all",
        offers="A contest fixed for a modest bribe of vis",
    )
    world["lotharingian_movement"] = b.faction(
        "The Lotharingian Movement",
        summary=paragraphs(
            "Covenants of the north and west of the Rhine and the neighbouring "
            "part of Normandy that want to revive the Lotharingian Tribunal, "
            "which the Grand Tribunal of 865 created and that of 898 "
            "dissolved. Four Rhine covenants back it in whole or part "
            "(Triamore, Fengheld's supporters, Waddenzee and Oculus "
            "Septentrionalis) with three of Normandy (Florum, its vassal "
            "Spider's Palace, and Requies Aeterna, also Florum's vassal). "
            "Florum and Triamore conceived it.",
            "Their aim is a Tribunal where magi need not hide what they are, "
            "brought about slowly with help from churchmen in the Rhine "
            "cities, using their arts for mankind's good without breaking "
            "the Oath's ban on meddling. Writing their own Peripheral Code, "
            "they would allow more than the Rhine and less than Normandy, and "
            "they think the consortium strong enough to keep nobles from "
            "dragging them into war and politics. They mean to put the "
            "proposal to the Grand Tribunal of 1228 and found the Tribunal "
            "only later, expecting resistance.",
        ),
        secrets="Their reasons differ: Daria la Gris wants Triamore to matter; about "
        "half of Fengheld's 23 magi agree in theory and plan chapter houses "
        "beyond Cologne; Waddenzee wants a Code that permits its piracy; "
        "Oculus Septentrionalis wants open trade and may plant a covenant to "
        "counter Waddenzee. Requies Aeterna expects a Lotharingian Code to "
        "dissolve its oath to Florum and would not mind. Montverte and "
        "Waddenzee plan for Waddenzee to join and then defect as Montverte's "
        "vassal, crippling the new Tribunal.",
        faction="Other",
        decides="A council",
        members=7,
        rules="Each covenant pledges support in whole or in part",
        wants=(
            "A new Lotharingian Tribunal with its own Peripheral Code, proposed at "
            "the Grand Tribunal of 1228"
        ),
        offers=(
            "Freedom from Normandy's raiding and its rulings on meddling, and "
            "openness with the mundane world"
        ),
    )


# -- the Tribunal's plots --


def _boar_king(normandy: Normandy) -> None:
    b = normandy.b
    normandy.world["threat_boar_king"] = b.threat(
        "The Boar King's Hunt",
        summary="The Boar King, a faerie lord of the old Gaulish forests, has "
        "decided that hunting down greedy hunters no longer holds back the "
        "plough, the axe and the Church. He wants Hermetic wardens for his "
        "woods, as House Diedne once was, and is ready to court them, with "
        "Salvirius to make the offers. Whether he exists in this saga is the "
        "troupe's choice.",
        secrets="A Diedne magus believed killed in the Schism War is rumoured to "
        "ride with him, and the Quaesitores will come. Salvirius is not what "
        "he seems: he can teach Diedne Magic, and his last offer marks the "
        "magus who takes it for an unknown watcher in Paris.",
        antagonist="The Boar King, faerie lord of the forests",
        realm="Faerie",
        place=normandy.places["boar_kings_hall"],
        stages=[
            S(
                "Hunters hunted",
                at=1,
                clues=(
                    "Each autumn the boar hunts end badly for those who took too "
                    "much: poachers and lords' huntsmen are found speared deep "
                    "in the forest. Charcoal-burners speak of a rider with a "
                    "boar's head leading faerie knights through groves where the "
                    "sun never reaches."
                ),
                ignored="The killings go on and foresters and settlers stay out of the deep woods.",
                stopped=(
                    "The covenant warns the locals to take less; the hunt passes "
                    "them by, and the King notices who gave the warning."
                ),
                turned="The covenant learns the court's customs and earns a cautious welcome.",
            ),
            S(
                "Master of the Hunt",
                at=2,
                clues=(
                    "A Merinita or Bjornaer magus travelling alone through the "
                    "forest is met by the King and a quieter courtier, Salvirius, "
                    "who tests his feeling for the wild and, if he likes the "
                    "answers, offers a share of the forest's power for a sacrifice "
                    "and a quest, perhaps the destruction of a new settlement "
                    "cut into the woods."
                ),
                ignored="The King finds another magus, perhaps one of a rival covenant.",
                stopped=(
                    "The offer is refused; the court counts the covenant among "
                    "the men of the axe."
                ),
                turned=(
                    "A magus of the covenant becomes the King's ally and forest "
                    "warden, gaining Virtues from Salvirius at the price of a Flaw "
                    "each, and owing the court his help."
                ),
            ),
            S(
                "The desecrated temple",
                at=3,
                clues=(
                    "Missionaries once pulled down the Boar King's temples, and "
                    "now a revived cult is trying to consecrate one again. The "
                    "cultists may come to the covenant asking help against the "
                    "Church, or local churchmen may come asking help to put the "
                    "cult down, and to be sure the covenant has no part in it."
                ),
                ignored=(
                    "Cult and Church clash, blood is spilled, and the Church looks "
                    "for wizards behind the pagans."
                ),
                stopped="The cult is broken up; the Church is satisfied and the King enraged.",
                turned=(
                    "The covenant brokers a quiet peace: the old rites kept deep "
                    "in the wood, out of the bishop's sight, or covenant members "
                    "lead the cult themselves."
                ),
            ),
            S(
                "The hidden enemy",
                at=4,
                clues=(
                    "A Quaesitor of the Tribunal visits, raising hoplites to "
                    "look, by force if need be, into word of a Diedne magus seen "
                    "with the Boar King. The King meets the hoplites outside his "
                    "regio, orders them gone and refuses them entry."
                ),
                ignored=(
                    "The Quaesitores go in without the covenant, and anyone who "
                    "dealt with the King may later be asked why."
                ),
                stopped=(
                    "The hoplites force the regio and break the court; the King, "
                    "in his ancient rage, turns on every settler in his woods."
                ),
                turned=(
                    "A magus allied with the King defends his realm against the "
                    "Quaesitor, setting himself against his own sodales, or "
                    "brokers terms that spare both."
                ),
            ),
            S(
                "The forest pushed back",
                at=5,
                clues=(
                    "With Hermetic allies at last, the King moves openly against "
                    "new clearings and villages, as he once did with Diedne at "
                    "his side; nobles and abbots who own the assarts complain of "
                    "wizards in the woods."
                ),
                ignored=(
                    "Villages burn, the Church and the nobles blame the Order, and "
                    "the Tribunal asks who let it happen."
                ),
                stopped=(
                    "The King is humbled or bound by treaty, and the plough moves "
                    "on into the forest."
                ),
                turned=(
                    "A lasting compact keeps some forests the King's and gives the "
                    "covenant a faerie ally, and perhaps his tusks' vis in time."
                ),
            ),
        ],
    )


def _children_of_odin(normandy: Normandy) -> None:
    b = normandy.b
    normandy.world["threat_children_of_odin"] = b.threat(
        "Queen Skuld and the Ships of Flame",
        summary="Raiders out of the Viking age appear on a coast that has not seen "
        "them in two hundred years. Behind them is the Children of Odin, a "
        "young and secret Mystery Cult, and its Hierophant Queen Skuld, who "
        "wants Normandy back from the French king and herself crowned its "
        "maga-queen. Whether the cult exists in this saga is the troupe's "
        "choice.",
        secrets="Thormod of Montverte is a leading member. Skuld wants the Bayeux "
        "Tapestry to help her spell get through to King Philip, Normandy's "
        "duke in law. She may be an impostor, and the cult's magic may not "
        "be the Order of Odin's at all.",
        antagonist="Queen Skuld, Hierophant of the Children of Odin",
        realm="Magic",
        place=normandy.places["ships_of_flame"],
        stages=[
            S(
                "A Norman conquest",
                at=1,
                clues=(
                    "A covenant magus of strong Norman blood is visited by a "
                    "relative who wants backing for an Anglo-Norman attack on "
                    "mainland France. The relative is controlled by a Child of "
                    "Odin, sounding out how the magus feels about the French "
                    "holding Normandy."
                ),
                ignored="The cult tests other Norman-born magi until one bites.",
                stopped="The control is found and broken; the cult learns it has been noticed.",
                turned=(
                    "The magus seems keen, is approached by the cult with its "
                    "'more realistic plan', and may be initiated through its "
                    "degrees."
                ),
            ),
            S(
                "Attack ships",
                at=2,
                clues=(
                    "Vikings raid a string of monasteries on the Normandy coast "
                    "and merchant ships go missing. The covenant, being near, is "
                    "asked to investigate. Hermetic magic is plainly involved, "
                    "but the casting sigils are shrouded. The raids are a cult "
                    "initiate's Quest, carried out with Nordic Triumph."
                ),
                ignored=(
                    "The raids go on; the Church and the king's officers look for "
                    "the wizards behind them."
                ),
                stopped=(
                    "The responsible cultist is found and the raids end; a case "
                    "at Tribunal may bring the cult to the Order's notice."
                ),
                turned=(
                    "The culprit is bargained with and the secret kept, for a "
                    "price; or the culprit is a player magus already in the cult."
                ),
            ),
            S(
                "The tapestry",
                at=3,
                clues=(
                    "A band of Vikings appears at the gates of Bayeux, hacks its "
                    "way into the cathedral and makes off with the Tapestry; or a "
                    "cult member is sent to fetch it quietly. The Church asks the "
                    "covenant to recover it, or its magi are in the town when the "
                    "raiders come."
                ),
                ignored="The Tapestry vanishes into a burning regio on the Seine.",
                stopped="The Tapestry is recovered, and the Church is grateful.",
                turned=(
                    "The covenant keeps the Tapestry, a bargaining piece both the "
                    "cult and the Church want back."
                ),
            ),
            S(
                "The burning ships",
                at=4,
                clues=(
                    "The trail leads to the Seine and to three burning longships "
                    "in regiones that open only to a burning boat drifting "
                    "downstream on a warlord's death-day. The fire on deck kills "
                    "the unprotected."
                ),
                ignored="Skuld finishes her preparations undisturbed.",
                stopped=(
                    "Skuld is confronted on her ship and the cult laid before the "
                    "Quaesitores; quenching the fires would end the regiones too."
                ),
                turned="The covenant strikes a bargain with the Hierophant or joins her.",
            ),
            S(
                "The maga-queen of Normandy",
                at=5,
                clues=(
                    "With the Tapestry as her link, Skuld casts at the French "
                    "king; risings in Normandy and Norman relatives across the "
                    "Channel are stirred to strike at once."
                ),
                ignored=(
                    "Magic strikes the King of France; if it is traced, the Order "
                    "is blamed and ruin follows."
                ),
                stopped=(
                    "The cult is broken and Skuld slain, Marched or driven back "
                    "into the North."
                ),
                turned=(
                    "Skuld is unmasked as someone else entirely, or her cult is "
                    "turned to a quieter search for the true magic of the Order "
                    "of Odin."
                ),
            ),
        ],
    )


def _augustina(normandy: Normandy) -> None:
    b = normandy.b
    normandy.world["threat_augustina"] = b.threat(
        "The Traitor's Game",
        summary=paragraphs(
            "House Tytalus keeps a Traitor: a volunteer exiled from the House "
            "and counted the loser of all her contests, beneath any Tytalus's "
            "notice as a rival, whose one duty to the House is to restart its "
            "struggles when they stall. Since the time of Tasgillia the "
            "Traitor has carried a magical key; most think it once weakened "
            "Fudarus's defences, and some think it now only a symbol.",
            "The present Traitor, Augustina of Confluensis, a hoplite trained "
            "by the last Traitor, serves Proctor, who trusts no Tytalus and "
            "gives her the riskiest work. Meanwhile the House's two Primi, "
            "Harpax and Buliste, have been deadlocked for twenty years, and "
            "only one can take the House's seat at the Grand Tribunal of "
            "1228.",
        ),
        secrets="Augustina sits in the Cabal of Frankish Gold, backing the "
        "Lotharingian Tribunal she expects to fail, to see how the Order "
        "answers a challenge in its heartland. She was trained by Buliste's "
        "own mater. Buliste is in the cabal only to keep Harpax busy, and a "
        "saboteur in it works against the movement. Each of the feud's ends "
        "is open: one Primus yields, one dies or disappears (neither will "
        "commit a High Crime), or a third contender beats both.",
        antagonist="Augustina of Tytalus, the Traitor",
        stages=[
            S(
                "A stalled feud",
                at=1,
                clues=(
                    "Decimi wearing Harpax's sigil and Fideli under Buliste's "
                    "purple banner shout down mediators, who come away feeling "
                    "they were the joke. Harpax holds Fudarus, its vis and its "
                    "Rod; Buliste holds the House's web of spies and suppliers. "
                    "Nothing moves, and Augustina is seen asking after both."
                ),
                ignored="The deadlock holds and the Traitor decides the game needs waking.",
                stopped="Proctor keeps Augustina busy elsewhere, for now.",
                turned="The covenant becomes Augustina's confidant and hears what she plans.",
            ),
            S(
                "The dangerous device",
                at=2,
                clues=(
                    "Fudarus offers new vassals generous terms. Sworn vassals are "
                    "sent to find the pieces of a powerful pre-Hermetic item for "
                    "Harpax, not knowing it is a Diedne relic, that Buliste led "
                    "him to want it, or that she means to frame him with it. A "
                    "trusted merchant vanishes on false charges laid by Harpax, "
                    "and a spirit from Buliste offers help."
                ),
                ignored=(
                    "The covenant is left holding a relic that is dangerous both "
                    "magically and politically."
                ),
                stopped="The relic is hidden or destroyed, and both Primi are cheated.",
                turned="The covenant plays the Primi against each other for its own gain.",
            ),
            S(
                "Gold for Lotharingia",
                at=3,
                clues=(
                    "The Cabal of Frankish Gold puts its weight behind the "
                    "Lotharingian movement, while someone sours the movement's "
                    "covenants against one another. Augustina's name surfaces "
                    "where the Traitor has no business."
                ),
                ignored="The movement and its enemies grow bitter; the Traitor watches the Order react.",
                stopped=(
                    "The saboteur, or Augustina's part, is exposed; Proctor must "
                    "answer for his Traitor."
                ),
                turned="The covenant uses the cabal's gold and secrets for its own ends.",
            ),
            S(
                "A third contender",
                at=4,
                clues=(
                    "Porphyrion of Tytalus, an archmagus who came from Rome three "
                    "years ago, asks to join a young covenant. Local Tytali think "
                    "he wants the House for himself; Harpax and Buliste close "
                    "ranks against him."
                ),
                ignored="Porphyrion settles elsewhere and waits for one Primus to fall.",
                stopped="He is refused, and both Primi are quietly grateful.",
                turned=(
                    "His power transforms the covenant, and makes it the target "
                    "of both Primi."
                ),
            ),
            S(
                "The seat at Durenmar",
                at=5,
                clues=(
                    "The Grand Tribunal of 1228 nears and the feud escalates: "
                    "whoever sits in the House's seat will have shown they are "
                    "the stronger. If Buliste sits alone, Harpax may arrive on "
                    "the last day with news of a threat to the Order, perhaps one "
                    "of his own making."
                ),
                ignored=(
                    "The feud spills into the Tribunal, and the Order may face a "
                    "danger Harpax manufactured."
                ),
                stopped="One Primus yields, and the House settles under a single head.",
                turned=(
                    "A third contender takes the House, steadying it and restoring "
                    "Fudarus's power in Normandy."
                ),
            ),
        ],
    )


def _lotharingia(normandy: Normandy) -> None:
    b = normandy.b
    normandy.world["threat_lotharingia"] = b.threat(
        "The Lotharingian Secession",
        summary=paragraphs(
            "A Tribunal needs twelve magi from four covenants. Florum and "
            "Triamore lead a movement to carve a new Lotharingian Tribunal "
            "from the north and west of the Rhine and the neighbouring part "
            "of Normandy, to be proposed at the Grand Tribunal of 1228. The "
            "last new Tribunal was Novgorod in 1008, but this one would take "
            "land the Rhine and Normandy have held for centuries, and the "
            "traditionalists, most of the Rhine among them, are horrified. "
            "Both losing Tribunals have their critics, and the distant ones "
            "do not care.",
            "For Normandy the loss is serious: the region holds great mundane "
            "wealth and some of the Tribunal's best vis, and without it "
            "Brittany, Tytalus country, would produce more vis than the rest "
            "of the Tribunal together. A covenant in Flanders, Picardy or "
            "Champagne must watch closely, and so must any covenant holding "
            "legacies there, which a Lotharingian Code might not honour.",
        ),
        secrets="The Cabal of Frankish Gold backs the movement, with a saboteur "
        "inside. Montverte and Waddenzee plan for Waddenzee to join and then "
        "defect as Montverte's vassal, leaving the new Tribunal hemmed in by "
        "predatory Normandy covenants. Provençal may welcome the new "
        "Tribunal and try to merge with it, or fear for its own old "
        "Lotharingian lands; with all eyes on Lotharingia, Normandy's Tytali "
        "may try to win back ground lost to the Provençal Flambeau.",
        antagonist="The Lotharingian movement, led by Florum and Triamore",
        stages=[
            S(
                "Speculative missions",
                at=1,
                clues=(
                    "Magi are sent into the region to weigh vis sources, mystical "
                    "places and other resources that may become bargaining chips. "
                    "Florum airs its grievances over raiding and meddling at "
                    "every meeting."
                ),
                ignored="Others survey the land first and know its worth.",
                stopped="The covenant keeps what it learns to itself.",
                turned="What the covenant learns buys it a voice with either side.",
            ),
            S(
                "Choosing sides",
                at=2,
                clues=(
                    "Each covenant must declare itself. A vassal of Florum is "
                    "expected to follow its liege; a vassal of another liege must "
                    "weigh support against its oath. Requies Aeterna quietly hopes "
                    "the new Code will free it of its oath."
                ),
                ignored="The covenant is counted undecided, and courted or threatened by both sides.",
                stopped="The covenant stands with Normandy, and the movement loses a hope.",
                turned=(
                    "The covenant pledges to the movement and may lose its "
                    "Normandy legacies, or its liege's goodwill."
                ),
            ),
            S(
                "Soured friendships",
                at=3,
                clues=(
                    "Someone works to spoil relations between the movement's "
                    "covenants and their neighbours. Waddenzee's pirates court "
                    "Montverte's council, and Oculus Septentrionalis talks of a "
                    "covenant of its own in the region."
                ),
                ignored="The movement fractures from within before it reaches Durenmar.",
                stopped="The saboteur is unmasked, and the movement's members trust again.",
                turned="The covenant feeds the quarrels to its own advantage.",
            ),
            S(
                "Riches and vis",
                at=4,
                clues=(
                    "Confluensis sends agents inside and outside the Tribunal to "
                    "talk the covenants out of independence or rally the Grand "
                    "Tribunal's voters against it, and quietly scouts a site for "
                    "a Quaesitorial covenant and Mercer House in the new "
                    "Tribunal's lands."
                ),
                ignored="Proctor's agents shape the outcome without the covenant.",
                stopped="The movement's supporters are won back one by one.",
                turned=(
                    "Player magi found a frontier covenant as 'the new law' in "
                    "the new Tribunal."
                ),
            ),
            S(
                "The Grand Tribunal of 1228",
                at=5,
                clues=(
                    "The proposal goes before the Grand Tribunal at Durenmar, "
                    "with the House leaders lobbied hard by both sides."
                ),
                ignored=(
                    "The vote goes as the powerful wish; the political map of the "
                    "western Order may be redrawn without the covenant's say."
                ),
                stopped=(
                    "The proposal fails and Lotharingia stays divided between the "
                    "Rhine and Normandy."
                ),
                turned=(
                    "The proposal passes; a new Tribunal follows with its own "
                    "Peripheral Code, and vassal oaths and legacies there may be "
                    "void."
                ),
            ),
        ],
    )


def _golden_coin(normandy: Normandy) -> None:
    b = normandy.b
    normandy.world["threat_golden_coin"] = b.threat(
        "The Fixed Tourney",
        summary="The Hermetic Tourney after each Tribunal decides the tropaeum "
        "leases for seven years, the Tribunal's books and other prizes. The "
        "Cabal of the Golden Coin rigs it.",
        secrets="The cabal's members trade thrown contests, field 'lucky' separate "
        "teams, and shaped the prize levels to suit themselves. Members of "
        "the Cabal of the Crushed Viper, who hate the chivalric ideal, may "
        "want the Tourney ended altogether.",
        antagonist="The Cabal of the Golden Coin",
        stages=[
            S(
                "Points of tradition",
                at=1,
                clues=(
                    "Proposals to adjust the prize levels come up at Tribunal, "
                    "each presented as old custom; together they open odd gaps "
                    "in who wins what."
                ),
                ignored="The changes pass, and the gaps grow.",
                stopped="The covenant argues them down at Tribunal.",
                turned="The covenant proposes changes of its own that suit it.",
            ),
            S(
                "The lucky fourteenth",
                at=2,
                clues=(
                    "A team of three young magi from three covenants and three "
                    "Houses has come fourteenth at three Tourneys in a row; some "
                    "magi skip their covenant's team to enter one of their own."
                ),
                ignored="The pattern is noticed by no one, or no one says so.",
                stopped="The covenant shows the tallies to the Redcaps who keep them.",
                turned="The covenant asks the team, quietly, how it is done.",
            ),
            S(
                "An offer in the lists",
                at=3,
                clues=(
                    "Late in the Tourney a member of the cabal, perhaps one of "
                    "the fourteenth-place team, approaches the covenant and "
                    "offers to fix a contest for a little vis."
                ),
                ignored="The covenant ranks lower than it should, and a rival higher.",
                stopped=(
                    "The offer is refused and reported; the Quaesitores take an "
                    "interest."
                ),
                turned="The covenant pays, places higher, and is now the cabal's accomplice.",
            ),
            S(
                "Fair play",
                at=4,
                clues=(
                    "The cabal now chooses who holds the tropaeum leases; covenants "
                    "that lost out begin to wonder aloud."
                ),
                ignored=(
                    "The Tourney becomes a sham, and the Tribunal's vis drifts to "
                    "the cabal's members."
                ),
                stopped=(
                    "A case at Tribunal breaks the cabal, the prizes are restored "
                    "and the Tourney's rules mended."
                ),
                turned="The covenant joins the cabal and shares its prizes, and its risk.",
            ),
        ],
    )


# -- the saga frames --


def _frames(normandy: Normandy) -> None:
    b, world = normandy.b, normandy.world
    world["frame_romantic"] = b.threat(
        "A Romantic Saga",
        summary=paragraphs(
            "A saga frame. The romances sung by trouvères (noble poets who "
            "collect their songs in chansonniers) and jongleurs (lower-born "
            "minstrels) shape the Tribunal's culture: chivalry, courtly love, "
            "and more and more often wizards, faeries and devils. Their two "
            "great cycles are the Matter of Britain, which Chrétien de Troyes "
            "and his followers made French, and the Matter of France, "
            "Charlemagne and his twelve paladins, with Roland's fall at "
            "Roncevaux the best known of all. In Mythic Europe the Arthurian "
            "tales lack Galahad, and Camelot does not fall through Lancelot "
            "and Guinevere.",
            "The songs hide true lore: monsters, regiones, treasures, vis "
            "sources and faerie places, and many cite old books, perhaps lost "
            "Hermetic works, such as the ancient Breton book Geoffrey of "
            "Monmouth claimed and the book Meister Kyot found in Toledo. "
            "Magi read them as clues, Grail-seekers such as the Knights of "
            "the Green Stone as maps, and a few, like Celeres of Cunfin, as a "
            "code to live by. In a high-fantasy telling, the magi keep "
            "stumbling into faerie regiones where faerie knights guard every "
            "crossroads.",
        ),
        secrets="The troupe should decide early whether the Grail is a thing to be "
        "found, as in the early romances, or a symbol of spiritual "
        "perfection, as in the later ones.",
        antagonist="The romance's own peril: the gap between the ideal of chivalry and its practice",
        stages=[
            S(
                "A song worth hearing",
                at=1,
                clues=(
                    "A jongleur's chanson names a place the magi recognise; some "
                    "trouvères know of the Order and sing magi's deeds for "
                    "Hermetic patrons. A knight errant who looks exactly like one "
                    "of the magi arrives at the gate: a twin, and an Arcane "
                    "Connection, that the magus's parens never mentioned."
                ),
                ignored="Rivals mine the songs first, and the twin's resemblance is noticed by others.",
                stopped="The covenant keeps its secrets and the knight rides on.",
                turned="The songs lead to a vis source or a faerie place; the twin becomes a companion.",
            ),
            S(
                "The unbreakable blade",
                at=2,
                clues=(
                    "Grogs back from Compostela bring a sliver of metal full of "
                    "magic, sold near Roncevaux as a chip of Durendal, Roland's "
                    "relic-hilted sword that would not break. Is the sword at "
                    "Rocamadour, as the locals say, or elsewhere?"
                ),
                ignored="Others follow the sliver to the sword.",
                stopped="The fragment proves a fake, or is laid to rest with the relics.",
                turned="The search for Durendal begins in earnest.",
            ),
            S(
                "The strange fate of Chrétien de Troyes",
                at=3,
                clues=(
                    "Celeres of Cunfin faints over a book a Redcap brought him: "
                    "Chrétien's own journal, planning a trip to Brittany's "
                    "Arthurian sites to finish Perceval and fearing knights who "
                    "shadow him, knights who match Wolfram's Grail Templars. It "
                    "ends as he sets out."
                ),
                ignored="The journal's trail goes cold, or someone else follows it.",
                stopped="The mystery is solved: an ordinary death, or a faerie regio, as Merlin's was.",
                turned="The magi find what Chrétien was looking for in Brittany.",
            ),
            S(
                "The Grail in Iberia",
                at=4,
                clues=(
                    "A covenant knight brings home Wolfram's Parsifal, rumoured "
                    "to be the work of the Rhine magus Gunnar von Falster. Its "
                    "margins name a book by 'Flegetanis the heathen' found in "
                    "Toledo, and beside the Grail castle someone has written "
                    "'Montserrat', the jagged mountain above Barcelona where a "
                    "covenant once vanished."
                ),
                ignored="Others go to Montserrat first.",
                stopped="Montserrat holds only the lost covenant's ruins.",
                turned="The quest for the Grail leads south.",
            ),
            S(
                "Courtly love",
                at=5,
                clues=(
                    "A maga finds herself the subject of love songs the covenfolk "
                    "now hum. The trouvère, a powerful lord with a relic in his "
                    "ring, comes to court her, thinks her a noblewoman, writes "
                    "verses about her 'court', and may propose marriage. An old "
                    "knight friend of the covenant, ruined, rides to a tournament "
                    "for ransoms he cannot win, with a magus watching from the "
                    "stands."
                ),
                ignored=(
                    "The suitor's songs draw eyes to the covenant; the old knight "
                    "is maimed or killed."
                ),
                stopped="Delicate diplomacy or a clever ruse sends the suitor away content.",
                turned=(
                    "The suitor becomes a patron; the old knight wins, helped "
                    "covertly, and the watching magus is fooled."
                ),
            ),
            S(
                "The Grail quest",
                at=6,
                clues=(
                    "The lost books, Durendal and Chrétien's road all point to the "
                    "Grail, as the troupe has chosen to see it."
                ),
                ignored="The Grail is found by others, or lost again for an age.",
                stopped="The quest fails, as the knights of the romances so often do.",
                turned="The Grail, or the perfection it stands for, is won.",
            ),
        ],
    )
    world["frame_boar_and_dragon"] = b.threat(
        "The Boar and the Dragon",
        summary="A saga frame. The boar stood for the kings of Gaul a thousand years "
        "ago, the dragon for the Vikings who ruled the region three centuries "
        "back. The lion and the lily eclipse both now, but leftovers of those "
        "courts remember their greatness and plot its return: the Boar King "
        "and the Children of Odin, antagonists for a hoplite saga or any "
        "other, or courts the characters may join.",
        secrets="One, both or neither may exist in a given saga; the troupe decides. "
        "Begin The Boar King's Hunt or Queen Skuld and the Ships of Flame "
        "alongside this frame for their detail.",
        antagonist="The Boar King and Queen Skuld, old courts seeking revival",
        stages=[
            S(
                "Old courts stirring",
                at=1,
                clues=(
                    "Hunters vanish in the deep forest; Viking raiders are "
                    "reported on the coast. The troupe chooses which court, if "
                    "either, is real."
                ),
                ignored="The courts grow in strength unseen.",
                stopped="The rumours are run to ground early.",
                turned="The covenant makes contact with one court or both.",
            ),
            S(
                "The boar's offer",
                at=2,
                clues=(
                    "The Boar King, through Salvirius, courts a Merinita or "
                    "Bjornaer magus as the new Diedne of his forests."
                ),
                ignored="He finds his warden elsewhere.",
                stopped="He is refused, and the forest turns hostile.",
                turned="A covenant magus joins the court.",
            ),
            S(
                "The dragon's call",
                at=3,
                clues=(
                    "The Children of Odin sound out Norman-blooded magi and send "
                    "initiates raiding as Vikings."
                ),
                ignored="The cult grows and its raids multiply.",
                stopped="The cult is exposed to the Quaesitores.",
                turned="A covenant magus is initiated.",
            ),
            S(
                "Lion and lily answer",
                at=4,
                clues=(
                    "The Church, the king and the Quaesitores react to pagan rites "
                    "in the woods and raiders on the coast, and look for the "
                    "wizards behind both."
                ),
                ignored=(
                    "The Order is blamed for the old courts' revival and must "
                    "answer to mundane powers."
                ),
                stopped="Both courts fall back into legend.",
                turned=(
                    "The covenant stands between the old courts and the new "
                    "powers, bargaining with each."
                ),
            ),
        ],
    )
    world["frame_tradition_of_kings"] = b.threat(
        "The Tradition of Kings",
        summary=paragraphs(
            "A saga frame for a covenant with ties to the nobility. Philip "
            "Augustus rules France absolutely under a divine mandate, yet "
            "several plots aim at the throne or at the holy oil of anointing "
            "kept at Reims. The characters meet each plot in turn through "
            "their noble kin, oaths and the Order, and the ending is best "
            "saved for when several ripen at once.",
            "Where does kingship lie: in the oil, in the oil with the Church's "
            "blessing, in the crown or throne, or in the blood of Merovech, "
            "whose long hair and beard the Frankish kings still wear in their "
            "images? A magus who solved it might turn the secret to power in "
            "the Order. Saints linked to the Frankish kings (Clotilde, "
            "Martin of Tours, Remi, Riquier, Valery, Vedast) may answer a "
            "prayer with guidance. If history holds, Louis IX, now five, "
            "becomes king in 1226 and is canonised in 1297, and diviners may "
            "try to help or hinder that.",
        ),
        secrets="Behind the king's bad counsel is a truly evil man on his staff, "
        "prompted by a demon.",
        antagonist="The plotters against the oil and the throne of France",
        stages=[
            S(
                "Does it depend on the oil?",
                at=1,
                clues=(
                    "A powerful magus, one bad Twilight past sense, prepares "
                    "spells to walk into Reims Cathedral and anoint himself, "
                    "sure it will make him Primus; he may visit to consult a "
                    "history or let a clue slip at Tribunal. German nobles plan "
                    "to steal the oil to stop Philip anointing his son, and crown "
                    "an East Frankish heir of Charlemagne, wrongly thinking the "
                    "seven generations' grace of Pope Stephen II's ruling is "
                    "nearly over."
                ),
                ignored="The oil is taken, and the wrath of the mundane powers falls on the Order.",
                stopped=(
                    "The magus is exposed without the characters being charged "
                    "with scrying, though a senior magus makes a dangerous enemy."
                ),
                turned="The characters guard the oil at Reims, and meet the German plot there.",
            ),
            S(
                "Does it depend on the man?",
                at=2,
                clues=(
                    "French nobles plan a 'hunting accident' for Philip, meaning "
                    "to shape his young son into a proper king, and the "
                    "characters' closest noble contact asks for help. A learned, "
                    "striking young man asks the covenant for a permanent, "
                    "scarless tattoo of a red cross, for another plot to replace "
                    "Philip's line. The king is said to be badly advised: clerks "
                    "pack the court with kin, keep him from the crusade, and feed "
                    "him lies. Has he kept divine favour?"
                ),
                ignored="The king dies or falls under worse counsel.",
                stopped="The plotters and the false counsellors are exposed.",
                turned="The characters gain the gratitude, and the secrets, of the court.",
            ),
            S(
                "Does it depend on the bloodline?",
                at=3,
                clues=(
                    "A Jerbiton maga has taken as apprentice an un-Gifted boy of "
                    "Merovech's line, who wins every brawl, understands animal "
                    "calls, divines a little, has the Purifying Touch and never "
                    "cuts his hair; she means to bring him near the throne. A "
                    "lone Ex Miscellanea peregrinator of the Rhine, Merovech's "
                    "heir and perhaps Gifted with the Quinotaur's legacy, plots "
                    "to take the throne herself."
                ),
                ignored=(
                    "A Merovingian claimant appears, and the Church, the "
                    "nobility and the Quaesitores turn on the Order."
                ),
                stopped=(
                    "The claimants are thwarted quietly, without a charge of scrying."
                ),
                turned="The covenant shapes the boy's future, and with it perhaps a kingdom's.",
            ),
            S(
                "Reims",
                at=4,
                clues=(
                    "The plots come due together at the cathedral where the kings "
                    "are anointed."
                ),
                ignored="The succession breaks, or a false king is anointed.",
                stopped="The oil and the throne are kept safe, and the Order's hand stays hidden.",
                turned=(
                    "The characters learn the secret of kingship, and must decide "
                    "what to do with it."
                ),
            ),
        ],
    )
    world["frame_advance_of_dominion"] = b.threat(
        "The Advance of the Dominion",
        summary=paragraphs(
            "A saga frame, as the central arc or as a background theme. "
            "Towns grow, and each one turns the land for twenty miles round "
            "into farmland under the Dominion, which hampers magic and wears "
            "away vis sites. Paris, as big as some kingdoms, is a diamond the "
            "magi long for and cannot grasp, and anything that harms it "
            "harms the many covenants that buy rare supplies there. The "
            "royal court has settled in Paris, drawing the great lords there "
            "and leaving their lands to stewards who are easier to suborn "
            "but punish harder. The French Church grows rich and spends on "
            "good works that spread the Dominion, though its quarrel with "
            "the pope gives magi room to settle scores.",
            "Covenants work through masks, mundane agents who can be dropped "
            "or killed: Confluensis among the Seine shippers and the law "
            "faculty, Fudarus in the Dyers' Guild and the fashionable "
            "clothiers, Eboris among the ivory carvers and the "
            "underworld, Montverte in the Hanse Parisienne, Oleron with "
            "sailors' gangs. Eboris is senex of Paris, so proxy wars there "
            "are now illegal, and Eboris may raise the alarm if something "
            "monstrous threatens the city.",
        ),
        secrets="The strong will prey on the weak: young covenants become vassals "
        "at a rising price, some lieges fail, and some covenants may seek "
        "lieges outside the Tribunal. A coalition may set out to colonise "
        "Denmark, West Africa or a vis-rich Tribunal. Old wards set in the "
        "Schism War or the Corruption of Tytalus will crack as the Dominion "
        "rises.",
        antagonist="The spread of towns, fields and the Dominion",
        stages=[
            S(
                "The plough's twenty miles",
                at=1,
                clues=(
                    "New fields creep towards a covenant vis site and its aura "
                    "weakens. On a winter night of storm the liege lord brings a "
                    "covenant knight a swaddled child to hide and raise as his "
                    "own, and will not say why."
                ),
                ignored="A vis source fails, and the child's secret finds the covenant.",
                stopped="The covenant protects its sites, by law, purchase or cunning.",
                turned="The covenant moves its harvests, or learns who the child is.",
            ),
            S(
                "War!",
                at=2,
                clues=(
                    "After years of peace, neighbouring lords raid, vassals rebel, "
                    "crops burn and castles are besieged, but only the covenant's "
                    "mundane holdings are hit, as Normandy's Code allows. A "
                    "Hermetic rival is suspected."
                ),
                ignored="The covenant's mundane base is destroyed and the covenant falls.",
                stopped="The rival is found and turned away.",
                turned="The covenant turns the rival's mundane allies against him.",
            ),
            S(
                "Threats to Paris",
                at=3,
                clues=(
                    "Something menaces Paris: a preacher bent on reducing the city "
                    "to joyless prayer, a ring of diabolists in its court, guard "
                    "or clergy, plague, famine, invasion by a rebel duke or a "
                    "foreign king, or riots of merchants against nobles or French "
                    "against foreigners. Eboris calls for help."
                ),
                ignored="Paris suffers, and with it every covenant that depends on it.",
                stopped="The city is saved, though the Dominion hampers every spell.",
                turned="The covenant gains masks and influence in Paris.",
            ),
            S(
                "Moral hazard",
                at=4,
                clues=(
                    "Nobles who know the Order offer covenants under pressure what "
                    "they need in return for help, as Henry II and Philip did in "
                    "their war, when Oleron was censured for trying to free "
                    "Eleanor of Aquitaine. Liege covenants raise their prices."
                ),
                ignored=(
                    "Weakened covenants slip into alliance with the crown or a "
                    "rebel; the Quaesitores' fears come true."
                ),
                stopped="The covenant refuses, and finds its own way to endure.",
                turned=(
                    "The covenant becomes a liege that profits from others' "
                    "weakness, or joins a colonial venture abroad."
                ),
            ),
            S(
                "The cracking of old wards",
                at=5,
                clues=(
                    "As magic fails, ancient wards fade. In a sea cave at the end "
                    "of a promontory in the Vendée a demon, maddened by the sea, "
                    "bellows at high tide and hurls spray over the cliffs; it is "
                    "held by a Magical ward, which the coming Dominion will wear "
                    "away faster than it harms the demon."
                ),
                ignored="The ward breaks and the demon goes free.",
                stopped="The ward is renewed or the demon destroyed.",
                turned=(
                    "The weakened site, empty of its old prisoner, becomes a home "
                    "for a new covenant."
                ),
            ),
        ],
    )


# -- tying the stories to the other parts' records --


def _find(records: list[Any], *names: str) -> Any | None:
    """The first record whose name is one of `names` (ignoring case), or
    failing that whose name starts with one of them."""
    wanted = [n.casefold() for n in names]
    for record in records:
        if record.name.casefold() in wanted:
            return record
    for record in records:
        if any(record.name.casefold().startswith(n) for n in wanted):
            return record
    return None


def _add_to(record: Any, more: str, hidden: str = "") -> None:
    """Add a paragraph to a record's summary, and `hidden` to its
    secrets."""
    record.summary = paragraphs(record.summary, more)
    record.secrets = paragraphs(record.secrets, hidden)


def _merge_duplicates(normandy: Normandy) -> None:
    """A faction of this part's that another part also made: keep the
    other's record, with this part's paragraph and details added."""
    saga = normandy.b.saga
    for key in (
        "children_of_odin",
        "cabal_of_frankish_gold",
        "cabal_of_the_golden_coin",
        "lotharingian_movement",
        "court_of_the_boar_king",
    ):
        mine = normandy.world[key]
        other = next(
            (
                n
                for n in saga.neighbours
                if n is not mine
                and n.kind == mine.kind
                and n.name.casefold() == mine.name.casefold()
            ),
            None,
        )
        if other is None:
            continue
        _add_to(other, mine.summary, mine.secrets)
        for field, value in mine.details.items():
            if value and not other.details.get(field):
                other.details[field] = value
        for record in saga.neighbours:
            if record.answers_to == mine.id:
                record.answers_to = other.id
        saga.neighbours.remove(mine)
        normandy.world[key] = other


SPIDERS = ("Spider's Palace", "The Spider's Palace", "Palace of the Spider")

#: The links `finish` makes, where the other parts made the target:
#: (this part's record, link kind, the target's possible names, note).
LINKS: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    ("court_of_the_boar_king", "characters", ("Salvirius",), "The Boar King's adviser"),
    ("children_of_odin", "characters", ("Queen Skuld", "Skuld"), "Hierophant"),
    ("children_of_odin", "characters", ("Thormod",), "A leading member, in secret"),
    ("cabal_of_frankish_gold", "characters", ("Augustina",), "A member, in secret"),
    (
        "cabal_of_frankish_gold",
        "characters",
        ("Buliste",),
        "A member, to distract Harpax",
    ),
    ("lotharingian_movement", "covenants", ("Florum",), "Its architect in Normandy"),
    ("lotharingian_movement", "covenants", SPIDERS, "Supports its liege Florum"),
    (
        "lotharingian_movement",
        "covenants",
        ("Requies Aeterna",),
        "Expected to follow Florum",
    ),
    ("threat_boar_king", "characters", ("Salvirius",), "Makes the King's offers"),
    (
        "threat_children_of_odin",
        "characters",
        ("Queen Skuld", "Skuld"),
        "The antagonist",
    ),
    (
        "threat_children_of_odin",
        "characters",
        ("Thormod",),
        "A leading member of the cult",
    ),
    (
        "threat_children_of_odin",
        "covenants",
        ("Montverte",),
        "Thormod's covenant; Norse-descended magi",
    ),
    (
        "threat_children_of_odin",
        "places",
        ("Atramentum",),
        "Skuld's covenant before she left",
    ),
    ("threat_augustina", "characters", ("Augustina",), "The Traitor"),
    ("threat_augustina", "characters", ("Harpax",), "Primus, holding Fudarus"),
    (
        "threat_augustina",
        "characters",
        ("Buliste",),
        "Prima, holding the House's web of spies",
    ),
    ("threat_augustina", "characters", ("Porphyrion",), "A third contender"),
    ("threat_augustina", "covenants", ("Confluensis",), "Augustina's covenant"),
    (
        "threat_augustina",
        "covenants",
        ("Fudarus",),
        "The House's seat the Primi contest",
    ),
    ("threat_lotharingia", "covenants", ("Florum",), "Leads the movement in Normandy"),
    ("threat_lotharingia", "covenants", SPIDERS, "Florum's vassal, an enthusiast"),
    (
        "threat_lotharingia",
        "covenants",
        ("Requies Aeterna",),
        "Florum's vassal, indifferent",
    ),
    (
        "threat_lotharingia",
        "covenants",
        ("Montverte",),
        "Plots with Waddenzee to wreck it",
    ),
    ("threat_lotharingia", "covenants", ("Confluensis",), "Works to defeat it"),
    ("frame_romantic", "characters", ("Celeres",), "Lives by the code of chivalry"),
    ("frame_romantic", "covenants", ("Cunfin",), "Keeps the Grail Library"),
    ("frame_boar_and_dragon", "covenants", ("Montverte",), "Founded by Norsemen"),
    ("frame_advance_of_dominion", "covenants", ("Eboris",), "Senex of Paris"),
    (
        "frame_advance_of_dominion",
        "covenants",
        ("Confluensis",),
        "Masks among the Seine shippers",
    ),
    (
        "frame_advance_of_dominion",
        "covenants",
        ("Fudarus",),
        "Masks in the Dyers' Guild",
    ),
)

#: Each story and the faction behind it.
BEHIND: dict[str, str] = {
    "threat_boar_king": "court_of_the_boar_king",
    "threat_children_of_odin": "children_of_odin",
    "threat_augustina": "cabal_of_frankish_gold",
    "threat_lotharingia": "lotharingian_movement",
    "threat_golden_coin": "cabal_of_the_golden_coin",
}


def finish(normandy: Normandy) -> None:
    _merge_duplicates(normandy)
    saga, world = normandy.b.saga, normandy.world
    for story, faction in BEHIND.items():
        world[story].answers_to = world[faction].id
    candidates: dict[str, list[Any]] = {
        "characters": saga.characters,
        "covenants": saga.covenants,
        "places": [n for n in saga.neighbours if n.kind == "place"],
    }
    seine = _find(
        candidates["places"], "The Seine", "River Seine", "The Seine Basin", "Seine"
    )
    if seine is not None:
        normandy.places["ships_of_flame"].place_id = seine.id
    for key, kind, names, note in LINKS:
        target = _find(candidates[kind], *names)
        if target is not None:
            Builder.link(world[key], kind, target, note)
    if normandy.tribunal is not None:
        _add_to(normandy.tribunal, CLOSING)


CLOSING = paragraphs(
    "The Noble Life. Living cheek by jowl with the mundane world, some "
    "Normandy covenants put their lands in a companion's name, since a magus "
    "may not swear fealty and a castle or manor is hard to hold without a "
    "liege. The knight still owes his own lord forty days of armed service "
    "a year and attendance at court at the great feasts, Easter, Pentecost "
    "and Christmas, and a rich one may pay écuage instead. Knights also do "
    "justice under Frankish customary law (the Common Law Ability), where "
    "trial by combat, often by champion, is still claimed. They hunt, write "
    "verse (some are trouvères), fight in tournaments the Church and king "
    "distrust, ride out young as knights errant, and pursue courtly love, the "
    "devotion to a lady glimpsed and unattainable; in time they settle on a "
    "manor to marry well, raise an heir and enlarge the family estate, and "
    "expect their magi to help, which can strain the Code. Montverte lives "
    "this way; Cunfin shelters by a Cistercian abbey and Florum behind a "
    "merchant's front. Iola of Guernicus held in 1047 that living in a lord's "
    "house is no breach without an oath of vassalage, so magic may serve the "
    "companion lord as a consors; the rulings against Florum in 1088, on "
    "mundane resources in 1116, for Infelicitas in 1130 and for Pernix in "
    "1179 mark how far that goes.",
    "Tytalus Schemes. With Fudarus in the Tribunal, Tytali are everywhere, "
    "but each nurses her own schemes and the Primi are too busy with their "
    "feud to direct any grand plot. For a shared end they form cabals, "
    "anonymous by agreement, meeting in disguise or by letter, often drawn "
    "from more than one Tribunal, each member with her own reasons: the "
    "Cabal of the Laden Cart, founded by Kybella after a Twilight vision of "
    "Death reaping Europe, which hunts the Ankeu to hold Death to ransom; "
    "the Cabal of the Crushed Viper, mostly Stonehenge magi under Arthurian "
    "names ('Lancelot', 'Vivian', 'Pellinore') working against the chivalric "
    "ideal; the Cabal of Frankish Gold, behind the Lotharingian movement; and "
    "the Cabal of the Golden Coin, which fixes the Tourney. Over all hangs the "
    "twenty-year feud of Primus Harpax (whose Decimi hold sway in Normandy) "
    "and Prima Buliste (whose Fideli and spies reach beyond it), which must "
    "be settled, by surrender, death or a third contender, before the Grand "
    "Tribunal of 1228 seats only one of them.",
    "Salvirius's quests. The Boar King's adviser grants Virtues: he sets the "
    "seeker a mystical quest that demands a sacrifice, a Flaw taken on, and "
    "the Virtue follows. He offers Strong Faerie Blood, Shapeshifter, Animal "
    "Ken, Faerie Blood, Second Sight and Wilderness Sense, and the troupe may "
    "let him teach Hermetic Virtues. To one magus he offers Diedne Magic, "
    "taught in a season, which brings the Major Story Flaw Dark Secret with "
    "it (part of the Virtue, not counted in the balance) and a Major Hermetic "
    "Flaw besides.",
)
