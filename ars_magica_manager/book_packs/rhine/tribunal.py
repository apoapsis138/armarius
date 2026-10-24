"""The Rhine Tribunal itself: the record and its summary (build, before
the covenants exist), then its gilds, officers, Peripheral Code and
docket (finish, once the covenants and magi it names have been made).

Years of rulings are AD; the Rhine's records count in Anno Aegis (AA),
139 years ahead, and the text keeps both."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import Character
from ...tribunal_packages.rhine import KEY
from ..builder import paragraphs

if TYPE_CHECKING:
    from . import Rhine

NAME = "The Rhine Tribunal"

SUMMARY = paragraphs(
    "The First Tribunal covers every Imperial land north of the Alps: from "
    "the Jutland border in the north to the Danube in the south, and from "
    "the mouth of the Schelde, the Ardennes and the Argonne in the west to "
    "the Oder in the east, where its border with the Novgorod Tribunal is "
    "disputed and shifts. About 130 magi, close to a ninth of the Order, "
    "make it the largest and oldest of the thirteen Tribunals; it hosts the "
    "Grand Tribunal, and the domus magnae of Bonisagus (Durenmar), Bjornaer "
    "(Crintera) and Merinita (Irencillia) all stand in its forests. Its "
    "magi descend from Roman and Germanic traditions with Slavic and "
    "Scandinavian additions, and about a sixth of them are peregrinatores, "
    "wandering magi who guest at covenants under the Tribunal's old laws "
    "of hospitality.",
    "The Tribunal meets every seven years at Durenmar, opening on "
    "Walpurgis Night, the eve of the first of May, and sitting for over a "
    "week; the gilds and some Houses meet in the three days before. Its "
    "Praeco is not its oldest magus but the Prima of House Bonisagus, who "
    "votes the sigil of Bonisagus by proxy, a custom since Notatus; some, "
    "led by Fengheld, now want the Order's usual rule instead. Magi hold "
    "the ranks of journeyman, master and archmage: only masters take "
    "apprentices and hold a retired magus's sigil by proxy, archmagi hold "
    "two, and in a dispute that certamen would otherwise settle the higher "
    "rank has the right. Every apprentice trained here spends a season at "
    "Durenmar under a Bonisagus, and most join one of the six political "
    "gilds, which transcend House and covenant and monopolise the "
    "Tribunal's long-term quarrels, so that little changes at its meetings.",
    "The Rhine is no longer a leading force in the Order but is respected "
    "for its age and cannot be ignored for its size. Its old tension with "
    "Novgorod continues except among the Bjornaer; the Greater Alps are "
    "friendly trading neighbours who think their Roman covenants superior; "
    "Transylvania's Tremere press on Moravia. The next meeting is in 1221, "
    "the 1360th year of the Aegis.",
)

SECRET = (
    "The Apple Gild, with Oculus Septentrionalis, Triamore, about half of "
    "Fengheld's magi and two covenants of Normandy, means to propose a new "
    "Lotharingian Tribunal over the Low Countries and the north-west at the "
    "Grand Tribunal of 1228; Waddenzee, though no friend of the Apple Gild, "
    "would join to escape the Rhine. The Ash Gild's older members quietly "
    "plan war on the Norse wizards beyond the Baltic, which Murion does "
    "not oppose. Eule of Fengheld, the likeliest Praeco by age, is in fact "
    "in Final Twilight, which her covenant conceals."
)


def build(rhine: Rhine) -> None:
    rhine.tribunal = rhine.b.tribunal(
        NAME,
        package=KEY,
        summary=SUMMARY,
        secrets=SECRET,
        meets_every=7,
        next_year=1221,
        next_season="Spring",
        meeting_place="Durenmar, in the Black Forest: the Forum of Hermes and the Tribunal Field",
        magi_total=130,
    )


#: Each gild: its name, what it wants (its dues line, as the book gives
#: no dues), and the keys of the covenants whose magi mostly belong to it.
GILDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    (
        "Oak Gild (Eichengilde)",
        "None: a member owes the gild their vote and reasonable aid. The "
        "oldest and largest gild, a quarter of the Tribunal: tradition, "
        "respect for elders and the Founders, the Rhine's old glory. Led by "
        "Murion of Durenmar; Bonisagus, Guernicus and Tremere favour it.",
        ("durenmar", "fengheld"),
    ),
    (
        "Hawthorn Gild (Weissdorngilde)",
        "None: a member owes the gild their vote and reasonable aid. The smallest: protects the wild places and beasts "
        "from mundanes and shuns contact with them. Led by Urgen of "
        "Crintera; mostly Wilderist Bjornaer.",
        ("crintera",),
    ),
    (
        "Ash Gild (Eschengilde)",
        "None: a member owes the gild their vote and reasonable aid. Dominion over the land, a forthright Order, and "
        "(unspoken) war on the Order of Odin. Led by Philippus Niger of "
        "Durenmar; Flambeau, Tremere and Tytalus.",
        (),
    ),
    (
        "Elder Gild (Holundergilde)",
        "None: a member owes the gild their vote and reasonable aid. Split from the Hawthorn: the fae and friendship with "
        "them above all. Led by Iacob of Irencillia; nearly all of "
        "Irencillia and Dankmar, with a few Harmonist Bjornaer.",
        ("irencillia", "dankmar"),
    ),
    (
        "Linden Gild (Lindengilde)",
        "None: a member owes the gild their vote and reasonable aid. Founded after the Schism War by former Fengheld "
        "magi: co-operation, peace and an end to apathy; nearly a fifth of "
        "the Tribunal, the go-between. Led by Occultes of Durenmar; Mercere, "
        "Jerbiton, Verditius, Tremere and Trianoma's Bonisagus.",
        ("fengheld",),
    ),
    (
        "Apple Gild (Apfelgilde)",
        "None: a member owes the gild their vote and reasonable aid. The newest and weakest: friendship with mundanes, "
        "acceptance, humility before God. Led by Henri de Tours of Oculus "
        "Septentrionalis, Wilhelm Weiss of Fengheld and Daria la Gris of "
        "Triamore.",
        ("oculus", "triamore", "fengheld"),
    ),
)


#: The Peripheral Code: (year AD or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        None,
        "A season at Durenmar",
        "From the Tribunal's founding: every apprentice trained in the Rhine "
        "spends at least one season at Durenmar, taught by a magus of House "
        "Bonisagus.",
    ),
    (
        822,
        "The laws of hospitality (961 AA)",
        "A magus may ask hospitality of any lawful Rhine covenant, which must "
        "publish its conditions; a guest who accepts them is guaranteed at "
        "least three and at most seven years, pays at least three pawns of "
        "vis a year, and the conditions are the same for every guest in "
        "residence and change only when there are none.",
    ),
    (
        878,
        "Proxy sigils (1017 AA)",
        "Firm rules on the voting of retired magi, ending twenty years of "
        "dispute: a master is entrusted with one retired magus's sigil, an "
        "archmage with a second, cast in the retired magus's name and, by "
        "custom, by his likely wishes.",
    ),
    (
        None,
        "Ranks",
        "Only a master may take an apprentice (a journeyman's filius is "
        "treated as a new hedge recruit); three masters of other covenants, "
        "Houses and gilds confer the rank; in any dispute certamen would "
        "otherwise settle, the higher rank has the right. House Tremere "
        "contests this, as it was made to curb them.",
    ),
    (
        885,
        "Founding a covenant (1024 AA)",
        "A new covenant needs a sponsoring magus from every existing covenant "
        "of the Tribunal. Arae Flaviae and Schwarzburg abolished the same "
        "year. Chapter houses need no such leave, which is how Fengheld "
        "grows.",
    ),
    (
        1053,
        "Guardians of the Forests (1192 AA)",
        "Magi may actively defend the wilderness against those who would "
        "destroy it. In 1194 Caecilius ruled that the Danish occupation of "
        "Rügen is no such destruction, as no wilderness was invaded.",
    ),
    (
        1109,
        "A day's march (1248 AA)",
        "A magical site within a day's march of a covenant belongs to it; "
        "Valdus of Tytalus, who harvested Treverorum's, was fined a pawn as "
        "the covenant had lost nothing, and told to ask in future.",
    ),
    (
        1144,
        "A covenant without a site",
        "At the Ash Gild's urging the Tribunal founded Oculus Septentrionalis "
        "to learn of the Norse wizards, ruling that a covenant needs no site "
        "at founding, only magi bound by a charter. In 1158 its magi were "
        "fined three pawns each for keeping neither.",
    ),
    (
        1151,
        "Dankmar against Durenmar",
        "Durenmar, found to have molested the fay and plundered faerie sites, "
        "paid a rook of vis to every other covenant and was barred from "
        "faerie sites for fourteen years unless it made peace with them.",
    ),
    (
        1200,
        "No magic in the Rhine Gorge (1339 AA)",
        "After Rheinstein was destroyed by the archbishop of Trier's army, "
        "largely through its own doing, no magical activity in the Rhine "
        "Gorge for twenty years: a ban that ends in 1220.",
    ),
    (
        1207,
        "Waddenzee is Terschelling",
        "The two survivors of Terschelling renamed it Waddenzee with a new "
        "charter and symbol; a vote to call it a new covenant needing leave "
        "failed, by the Oak and Ash Gilds. The same year Rethra, silent for "
        "decades, was declared abolished.",
    ),
)


def _case_text(rhine: Rhine) -> None:
    b, tribunal = rhine.b, rhine.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "Heorot asks to join the Tribunal",
        kind="motion",
        brought_by="Heorot",
        against="",
        charge="Heorot, founded on Zealand in 1215 with Oculus Septentrionalis' "
        "backing, applies for membership at the Tribunal of 1221; Zealand "
        "is nominally Novgorod's, which does not know of it.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
    )
    b.case(
        tribunal,
        "The Lusatia chapter and the Novgorod border",
        kind="motion",
        brought_by="Fengheld",
        against="",
        charge="Fengheld's Lusatia chapter house stands ten miles from the "
        "agreed border, the latest of the Rhine's boundary disputes with "
        "Novgorod; the Tribunal is asked to assert its claim east to the "
        "Oder and to take the matter to the Grand Tribunal of 1228.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
    )
    b.case(
        tribunal,
        "Choosing the Praeco by age",
        kind="motion",
        brought_by="Fengheld",
        against="Durenmar",
        charge="That the Rhine should choose its Praeco as the rest of the "
        "Order does, by age, and not always the Prima of Bonisagus; Eule of "
        "Fengheld would then be the likeliest, with Caecilius of Durenmar "
        "and Schadrit of Dankmar the other candidates.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Crintera and the Danes",
        kind="motion",
        brought_by="Crintera (the Hawthorn Gild)",
        against="",
        charge="Fifty years after Valdemar's invasion of Rügen, Crintera "
        "again asks the Tribunal to act against the Danish occupation and "
        "the Dominion it brings; the Tribunal split on gild lines in 1186 "
        "and Caecilius ruled against in 1194, and Bjornaer who attacked "
        "settlers have been prosecuted since.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Triamore's dealings with mundanes",
        kind="charge",
        brought_by="The Quaesitores",
        against="Triamore",
        charge="Triamore's long entanglement in the politics of the Meuse, "
        "for which the Quaesitores have sought censure for years; Daria la "
        "Gris has so far talked the covenant out of it.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Fengheld's house at Durenmar",
        kind="charge",
        brought_by="Durenmar",
        against="Fengheld",
        charge="Fengheld is building a three-storey stone house on the "
        "Tribunal Field as a permanent chapter at Durenmar, with a "
        "laboratory and its own Mercere Portal, after Durenmar refused it a "
        "Portal in the Forum; Durenmar calls it an encroachment.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Waddenzee's piracy",
        kind="charge",
        brought_by="The Quaesitores",
        against="Waddenzee",
        charge="Waddenzee's magi prey on North Sea shipping; the Quaesitores "
        "have warned them repeatedly that they walk a fine line and will "
        "get no help if the mundane powers move against them, and that each "
        "would face High Crimes charges.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Odorpes of Fengheld's neglect",
        kind="charge",
        brought_by="Fengheld",
        against="Odorpes of Bjornaer",
        charge="Fengheld has more than once accused its own Odorpes, of the "
        "Lusatia chapter, of neglecting her duties to the covenant.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "The Rhine Gorge after the ban",
        kind="motion",
        brought_by="",
        against="",
        charge="The twenty-year ban on magic in the Rhine Gorge runs out in "
        "1220; whoever would found a covenant there needs a sponsor from "
        "every covenant. Durenmar wants a neutral, traditional foundation; "
        "Fengheld would rather it were one of its chapters.",
        filed_year=1220,
        filed_season="Spring",
    )


def finish(rhine: Rhine) -> None:
    from .history import ERAS, REGION_HISTORY

    b, tribunal = rhine.b, rhine.tribunal
    assert tribunal is not None
    # The mundane history, by era, in the Tribunal's own History.
    tribunal.history = paragraphs(*(f"{title}. {text}" for title, text in ERAS))
    tribunal.summary = SUMMARY
    # Each region's own history after its description.
    for key, history in REGION_HISTORY.items():
        region = rhine.places.get(key)
        if region is not None:
            region.summary = paragraphs(region.summary, history)
    for name, dues, keys in GILDS:
        members = [rhine.covenants[k] for k in keys if k in rhine.covenants]
        b.gild(tribunal, name, dues, members)
    praeco = rhine.magi.get("murion")
    quaesitor = rhine.magi.get("caecilius")
    tribunal.praeco_id = praeco.id if praeco else None
    tribunal.quaesitor_id = quaesitor.id if quaesitor else None
    if "tabanus" not in rhine.magi:
        rhine.magi["tabanus"] = b.magus(
            "Tabanus",
            covenant=None,
            house="house_guernicus",
            age=38,
            summary="Journeyman of House Guernicus and a Quaesitor, filius of "
            "Jart, a peregrinator sent to the Rhine about ten years ago because "
            "the House thought its presence here weak. His evidence once "
            "Marched a Hawthorn Gild magus on what many called a technicality, "
            "and he is unpopular, that gild especially; he moves from covenant "
            "to covenant every few years, preferring young covenants that will "
            "not try to browbeat him. He lately left Triamore. With Winfrida "
            "of Durenmar he may be one of only two Guernicus in the Tribunal. "
            "The book offers him as a player character.",
        )
    if "felicia" not in rhine.magi:
        rhine.magi["felicia"] = b.magus(
            "Felicia",
            covenant=None,
            house="house_bonisagus",
            age=24,
            summary="Journeyman of House Bonisagus, filia of Dorana of "
            "Fengheld in the lineage of Irmele, freshly Gauntleted and a "
            "peregrinator. Sturdy and weather-beaten, often taken for a young "
            "man, which lets her travel alone. Her weather magic is strongest "
            "in winter, when she overwinters at a covenant (Fengheld has "
            "promised her a spare laboratory for favours it has yet to name), "
            "and weakest in summer, when she takes to the road. The book "
            "offers her as a player character; it spells her name Felecia "
            "too.",
        )
    _proxies(rhine)
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _case_text(rhine)
    tribunal.covenants_total = len(
        [c for c in rhine.b.saga.covenants if c.tribunal_id == tribunal.id]
    )


#: Sigils of living Tremere magi their exarchs vote with, beyond those of
#: their own covenant: Stentorius holds Triamore's two, Severicus holds
#: Hygwald Veritas's of Waddenzee.
TREMERE_SIGILS = {"fengheld": 2, "roznov": 1}


def sigils_by_rank(summary: str) -> int:
    """The retired magi's sigils a magus wields by proxy: one for a
    master, a second for an archmage. Each magus's summary opens with
    their rank; a magus whose rank the book leaves out holds none."""
    first = summary.split(",", 1)[0].split(" ", 1)[0]
    if first.startswith("Archmag"):
        return 2
    return 1 if first == "Master" else 0


#: The rank Virtues and the retired sigils each holds (Guardians of the
#: Forests p. 20).
RANK_SIGILS = {"vf_archmage_rhine_tribunal": 2, "vf_master_rhine_tribunal": 1}


def rank_sigils(character: Character) -> int:
    """The proxies a magus wields: by his rank Virtue, else by the rank his
    summary opens with."""
    held = [
        RANK_SIGILS[vf.vf_id]
        for vf in character.virtues_flaws
        if vf.vf_id in RANK_SIGILS
    ]
    return max(held) if held else sigils_by_rank(character.summary)


def _proxies(rhine: Rhine) -> None:
    """The proxies each covenant carries to the meeting of 1221: its
    masters' and archmagi's retired sigils, and the Tremere sigils its
    exarch holds for magi of other covenants."""
    tribunal = rhine.tribunal
    assert tribunal is not None
    for key, covenant in rhine.covenants.items():
        held = sum(
            rank_sigils(c)
            for c in rhine.b.saga.characters
            if c.covenant_id == covenant.id and c.type == "magus"
        ) + TREMERE_SIGILS.get(key, 0)
        if held:
            tribunal.proxies[covenant.id] = held
