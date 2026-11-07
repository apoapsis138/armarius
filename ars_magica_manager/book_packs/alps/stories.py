"""The saga's stories, in paraphrase (A23): each a threat whose stages
lay out what the book says may come of it.

Under way in 1220: Athena Alpina's likely ostracism at the meeting of
1221 (world["threat_athena"]), the raids on the Bavarian Common
(["threat_common"]) and the school for the Sicilian children
(["threat_school"]).

Dormant until the storyguide begins them: the Vanishing Away of Tarragon
Vale (["threat_vanishing"]), Jacinta and the Flambeau Primacy
(["threat_jacinta"]), the amaranth trade (["threat_amaranth"]),
Esther's petrification (["threat_esther"]), the Banner of Winter
(["threat_banner"]), the Vienna basilisk (["threat_basilisk"]), the
Werfen ice caves (["threat_werfen"]) and Sinews of Knowledge's money
troubles (["threat_sinews"]).

`finish` ties each story to the covenants, magi and places the other
parts made, by key, skipping any that is missing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import Builder, dormant, paragraphs, titled

if TYPE_CHECKING:
    from .state import Alps

S = Builder.stage
DATED = "Fixed dates"


def build(alps: Alps) -> None:
    b, w, p = alps.b, alps.world, alps.places
    w["threat_athena"] = b.threat(
        "The Ostracism of Athena Alpina",
        place=p.get("icy_north_hill"),
        summary=paragraphs(
            "Athena Alpina, chief Quaesitor for fourteen years, was trained "
            "in the Roman Tribunal and does not share her neighbours' ill "
            "will toward House Tremere: she wants a greater part for them in "
            "the Tribunal, and her even-handedness looks to Alpine eyes like "
            "blatant favouritism. At the meeting of 1214 she had to send away "
            "a Tremere hoplite. The sherds at the next meeting may name her.",
        ),
        secrets=[
            titled(
                "Why Cato came to the Alps",
                "Cato was sent to the Alps partly so that, if Athena Alpina "
                "goes, the chief Quaesitor's place passes to him and not to "
                "Adrasteia of Tytalus.",
            )
        ],
        antagonist="The Tribunal's old grudge against House Tremere",
        moves=DATED,
        stages=[
            S(
                "The meeting of 1221",
                year=1221,
                season="Autumn",
                clues="Magi weigh who will get the most sherds; Athena's "
                "dealings with the Tremere are talked of at the Midsummer "
                "Fair.",
                ignored="If one magus in four names her, she must leave the "
                "Greater Alps before the second full moon, for twenty-one "
                "years; her deputy Cato becomes chief Quaesitor.",
                stopped="Enough blank sherds, or another name, and she stays.",
            ),
        ],
    )
    w["threat_common"] = b.threat(
        "Raids on the Bavarian Common",
        place=p.get("bavaria"),
        summary=paragraphs(
            "Magi of the Rhine and Transylvania cross the borders to plunder "
            "the vis sources the Code calls Alpine, the Bavarian Common above "
            "all, which the Quaesitores harvest and divide at the Fair. "
            "Adrasteia of Tytalus and Katrina of Bjornaer hunt the raiders, "
            "baiting traps for the greedy and striking only those caught in "
            "the act; counter-raiders are fair game to them too.",
        ),
        antagonist="Vis poachers of the Rhine and Transylvania",
        position=1,
        stages=[
            S(
                "A trap is sprung",
                at=2,
                clues="A vis site of the Common is found stripped; a stranger "
                "is seen near another.",
                ignored="The poachers grow bolder, and Alpine magi talk of "
                "counter-raids into the Rhineland.",
                stopped="Adrasteia's ambush takes them in the act.",
            ),
        ],
    )
    w["threat_school"] = b.threat(
        "The Sicilian Children",
        place=p.get("icy_north_hill"),
        summary=paragraphs(
            "Five years ago a magical accident in Sicily brought about the "
            "birth of two dozen Gifted children at once. The Icy North "
            "motherhouse offers a chair to whoever makes the best use of its "
            "empty buildings, and many expect a school for the children: the "
            "likeliest proposal trains them collegially, an untried method, "
            "and the Quaesitores favour it, since two dozen magi of one age "
            "and one affinity graduating into a single House might unbalance "
            "the Order.",
        ),
        antagonist="The rival claimants to the empty buildings",
        position=1,
        stages=[
            S(
                "The chair is awarded",
                at=3,
                clues="Claimants put their proposals to the motherhouse; "
                "Houses that want the children for themselves stir.",
                ignored="The collegial school is founded, and the children "
                "come to the Alps.",
                turned="A troupe that wins the chair founds the school itself.",
            ),
        ],
    )
    w["threat_vanishing"] = dormant(
        b.threat(
            "The Vanishing Away",
            place=p.get("tarragon_hill"),
            summary=paragraphs(
                "Twenty-two years ago the four magi of Tarragon Vale and their "
                "covenfolk vanished. The Quaesitores hold their vis and will "
                "settle no estate without proof of death; the heirs want the "
                "hoard. Many tie the vanishing to the sudden appearance of the "
                "Schwytzers nearby.",
                "If the troupe solves it, they hold knowledge worth a great "
                "deal to rich heirs, and might ask to settle Tarragon Vale, "
                "taking on its legal standing, its debts and its unknown "
                "supernatural enemies, and the things in its sealed basements. "
                "If someone else solves it, the vis and the sources are shared "
                "out, and some heirs move to the Alps while others sell.",
            ),
            antagonist="Whatever took Tarragon Vale",
        )
    )
    w["threat_jacinta"] = dormant(
        b.threat(
            "Jacinta and the Flambeau Primacy",
            place=p.get("tower_of_ashes"),
            summary="Archmaga Jacinta is the eldest of her line and the most "
            "able Perdo maga in the Order. If the few Flambeau older or "
            "deadlier than she die first, she may be declared Prima, making "
            "the Icy North her House's temporary domus magna, to her "
            "neighbours' resigned disgust; others hope a younger, more distant "
            "fire magus is chosen instead.",
            antagonist="Time, and House Flambeau's succession",
        )
    )
    w["threat_amaranth"] = dormant(
        b.threat(
            "The Amaranth Trade",
            place=p.get("bavaria"),
            summary="The Code orders all amaranth destroyed, but the trade in "
            "the faerie flower goes on, around Ingolstadt above all. Taken as "
            "a dust in white wine it makes the Gifted see the world's hidden "
            "forces and keeps them from looking old, but it addicts them and "
            "makes Twilight likelier and worse, and Hermetic magic can neither "
            "detect it nor cure the craving. The Quaesitores believe faerie "
            "nobles grow it to make magi addicts and command them against the "
            "Order; others doubt it.",
            antagonist="The faeries who grow amaranth",
        )
    )
    w["threat_esther"] = dormant(
        b.threat(
            "Esther in Stone",
            place=p.get("axis_magica"),
            summary="Esther of Criamon was turned to stone by faeries two years "
            "ago; her ghost goes about the Cave, and the curse can be undone. "
            "The past Primi delay her unpetrifying to study the juno she has "
            "become, and her sodales think her death and return, rightly "
            "understood, could set her on her path to the Enigma.",
            antagonist="The faeries who cursed her",
        )
    )
    w["threat_banner"] = dormant(
        b.threat(
            "The Banner of Winter",
            place=p.get("dachstein"),
            summary="The giants of Dachstein want the Banner of Winter above "
            "all things: it would let them stay long in the hot Summer lands of "
            "Arcadia. Journeys End's magi search for it now and then, unsure "
            "they want to give it to their huge allies, who might use it to "
            "go deep into Arcadia or to rampage across Mythic Europe.",
            antagonist="The giants of Dachstein",
        )
    )
    w["threat_basilisk"] = dormant(
        b.threat(
            "The Vienna Basilisk",
            place=p.get("eastern_marches"),
            summary="A basilisk hatched in a house in Vienna in 1212. The "
            "townsfolk chased it into a well and poured stones on it; magi "
            "doubt that killed it, and even if it did, it lies dead in the "
            "groundwater. Several covenants would thank anyone who learnt its "
            "fate. Kentigern suspects a magus is making basilisks.",
            antagonist="The basilisk",
        )
    )
    w["threat_werfen"] = dormant(
        b.threat(
            "The Deaths at Werfen",
            place=p.get("werfen"),
            summary="Thirty pawns of Imaginem a year pour from a fountain in "
            "Werfen's ice caves, unclaimed. The second chapter to try for them "
            "was found dead without a wound, gibberish cut into the ice. A "
            "lucifugus is the common guess; a spirit of delirium or a sleeping "
            "ice wyrm are others.",
            antagonist="Whatever lives in the caves",
        )
    )
    w["threat_sinews"] = dormant(
        b.threat(
            "Sinews of Knowledge's Money",
            place=p.get("sinews_falls"),
            summary="Sinews of Knowledge has been caught again and again "
            "making goods from vis to sell, and has no income now; it cannot "
            "dispose of what it makes discreetly. It weighs a Hermes Portal to "
            "a chapter in another Tribunal, preferably eastward, or an "
            "alliance with a young covenant on the frontier, which would give "
            "that covenant the Alps' trade and make it depend on Sinews. Young "
            "magi who solve its money troubles would surely be offered a "
            "place.",
            antagonist="The Tribunal's ban on flagrant spending",
        )
    )


#: Each story's ties: (threat key, record key, note).
TIES: tuple[tuple[str, str, str], ...] = (
    ("threat_athena", "athena", "The magus at risk"),
    ("threat_athena", "cato", "Her deputy"),
    ("threat_athena", "adrasteia", "Who must not succeed her"),
    ("threat_common", "adrasteia", "Hunts the raiders"),
    ("threat_common", "katrina", "Hunts the raiders"),
    ("threat_school", "icy_north", "Offers the chair"),
    ("threat_vanishing", "tarragon_vale", "The vanished covenant"),
    ("threat_vanishing", "cymena", "Lives at the site"),
    ("threat_jacinta", "jacinta", "The likely Prima"),
    ("threat_amaranth", "philomena", "An amaranth halfling"),
    ("threat_esther", "esther", "The petrified maga"),
    ("threat_banner", "journeys_end", "Searches for it"),
    ("threat_basilisk", "kentigern", "Suspects a magus makes basilisks"),
    ("threat_sinews", "sinews", "The covenant"),
    ("threat_sinews", "ragoneda", "Its liaison to a trading partner"),
)


def finish(alps: Alps) -> None:
    for threat_key, key, note in TIES:
        threat = alps.world.get(threat_key)
        target = alps.magi.get(key) or alps.covenants.get(key)
        if threat is None or target is None:
            continue
        kind = "characters" if key in alps.magi else "covenants"
        alps.b.link(threat, kind, target, note)
