"""The mundane Greater Alps (ch09): its lords, its Church, its towns and
the factions the book names.

Lords: world["emperor"] (Frederick II), ["duke_of_austria"] (Leopold
VI), ["duke_of_bavaria"] (named as the Rhine pack names him, so the two
packs share him), ["savoy"] (Thomas I), ["kyburg"], ["hapsburg"] and
["zahringen"] (extinct). The book names few rulers for 1220; those it
doesn't name are history's, and say so (A22). The Church: the bishops of
Basel, Constance, Chur, Geneva, Lausanne and Regensburg, the archbishop
of Salzburg, and the abbeys of Saint Gallen, Einsiedeln, Reichenau and
Melk, their auras the church kinds' (DE p. 418: a cathedral or major
monastery Divine 5). Towns: Basel (named as the Rhine pack names
it), Berne, Constance, Fribourg, Geneva, Lausanne, Lucerne, Chur, Zurich,
Interlaken, Augsburg, Munich, Regensburg, Salzburg and Vienna, each
Divine 3 over most of it. Factions: the Rowan Sisterhood, the Craft
School, the Jovians, the Black Mark, the Cult of Dyssynergy and the
Abbaye des Vignerons."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from .state import Alps

#: Said of a ruler the book does not name.
HISTORY = "The book names no ruler; history's for 1220 is given, marked so."


def build(alps: Alps) -> None:
    _lords(alps)
    _church(alps)
    _towns(alps)
    _factions(alps)


# -- lords --


def _lords(alps: Alps) -> None:
    b, w, p = alps.b, alps.world, alps.places
    w["emperor"] = b.lord(
        "Frederick II, Holy Roman Emperor",
        title="duke",
        wealth="Wealthy",
        manors=0,
        place=p["alps"],
        summary=paragraphs(
            "King of the Germans, crowned Emperor in Rome late in 1220. "
            "Zurich came under him in 1218, and Berne the same year; the "
            "Schwytzers are his allies against his rivals.",
            HISTORY,
        ),
    )
    w["duke_of_austria"] = b.lord(
        "Leopold VI, Duke of Austria",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="Vienna",
        answers_to=w["emperor"],
        place=p["eastern_marches"],
        summary=paragraphs(
            "The Babenberg duke of Austria and Styria, whose house holds the "
            "eastern marches. His seat has been Vienna since 1156; his "
            "family founded a mint there in 1190. The archbishop of "
            "Salzburg opposes him.",
            HISTORY,
        ),
    )
    w["duke_of_bavaria"] = b.lord(
        "Louis I Wittelsbach, Count Palatine of the Rhine",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="Regensburg",
        answers_to=w["emperor"],
        place=p["bavaria"],
        summary=paragraphs(
            "Duke of Bavaria, of the Wittelsbachs who have ruled it since "
            "1180 and won the Rhenish Palatinate in 1214. His seat is "
            "Regensburg on the Danube.",
            HISTORY,
        ),
    )
    w["savoy"] = b.lord(
        "Thomas I, Count of Savoy",
        title="count",
        wealth="Wealthy",
        manors=0,
        answers_to=w["emperor"],
        place=p["western_alps"],
        summary=paragraphs(
            "The House of Savoy holds the Tribunal's lands in the Kingdom "
            "of Burgundy and rings the count of Geneva's with forts, and goes "
            "on building castles round Fribourg (Gruyères, Estavayer, Morat). "
            "Journeys End claims many vis sources in Savoy, and most Alpine "
            "covenants keep a chapter there to gather vis; the land has been "
            "ill-omened for the Order, its settlements destroyed in the "
            "Schism War and the purge of House Tytalus, and some say the "
            "next crisis will be heralded by a Hermetic settlement's fall "
            "here.",
            HISTORY,
        ),
    )
    w["kyburg"] = b.lord(
        "The Counts of Kyburg",
        title="count",
        wealth="Wealthy",
        manors=100,
        seat="Kyburg, near Winterthur",
        answers_to=w["emperor"],
        place=p["western_alps"],
        summary="Their home castle stands outside Winterthur near Zurich, "
        "with a vassal's second castle overlooking the town; their lands "
        "run north to the Rhine and east to Lake Constance, with about a "
        "hundred castles held of them. They inherited the Zähringers' lands "
        "in 1217. The book names no count.",
    )
    w["hapsburg"] = b.lord(
        "The Hapsburgs",
        title="count",
        manors=0,
        seat="Hapsburg castle, in Vindonissa",
        answers_to=w["emperor"],
        place=p["western_alps"],
        summary="A noble house named for the castle Bishop Werner of "
        "Strasbourg built in the ruins of Vindonissa; a lesser scion lives "
        "there, by his ancestors' graves. A vassal of theirs holds Oberhofen "
        "on Lake Thun. The book names no count.",
    )
    w["zahringen"] = b.lord(
        "The House of Zähringen",
        title="duke",
        manors=0,
        place=p["western_alps"],
        summary="Extinct since Berthold V died in 1217; its lands went to "
        "the Kyburgs. The Zähringers founded Fribourg (Berthold IV, 1157), "
        "Berne (Berthold V, 1191) and Thun, and set the nobles' craze for "
        "building towns and castles.",
    )


# -- the Church --


#: (key, name, church, region, founded, summary, ruler)
CHURCH: tuple[tuple[str, str, str, str, int | None, str, str], ...] = (
    (
        "bishop_of_basel",
        "The Bishop of Basel",
        "Bishop's cathedral",
        "western_alps",
        None,
        "Has ruled Basel since 1032; its cathedral is less than two centuries old.",
        "Henry of Thun (history's)",
    ),
    (
        "bishop_of_constance",
        "The Bishop of Constance",
        "Bishop's cathedral",
        "western_alps",
        None,
        "Rules the city, perhaps the richest bishopric north of the Alps; a "
        "decisive bishop counts in both secular and Church politics. The "
        "Code names Constance a place where even minor violence is "
        "interference with the Church. A bishop of Constance came to "
        "consecrate Einsiedeln's church in 968 and heard God had done it.",
        "Konrad of Tegerfelden (history's)",
    ),
    (
        "bishop_of_chur",
        "The Bishop of Chur",
        "Bishop's cathedral",
        "western_alps",
        None,
        "A see eight hundred years old; its new cathedral was finished "
        "about 1150. Round it Rhaetia lives under club law, scattered with "
        "petty castles whose lords squeeze their peasants. The book names "
        "no bishop.",
        "",
    ),
    (
        "bishop_of_geneva",
        "The Bishop of Geneva",
        "Bishop's cathedral",
        "western_alps",
        None,
        "Rules the city, a Roman see; the count of Geneva rules the lands about it.",
        "Aymon of Grandson (history's)",
    ),
    (
        "bishop_of_lausanne",
        "The Bishop of Lausanne",
        "Bishop's cathedral",
        "western_alps",
        None,
        "Rebuilding his cathedral slowly, for the castle-building has taken "
        "every labourer and mason. The book names no bishop.",
        "",
    ),
    (
        "bishop_of_regensburg",
        "The Bishop of Regensburg",
        "Bishop's cathedral",
        "bavaria",
        None,
        "His cathedral, begun last century, is still unfinished: each bishop "
        "adds to its tangled design, and something indefinable keeps it from "
        "completion; the Devil is said to build cathedrals here.",
        "Konrad IV of Frontenhausen (history's)",
    ),
    (
        "archbishop_of_salzburg",
        "The Archbishop of Salzburg",
        "Archbishop's cathedral",
        "eastern_marches",
        None,
        "A powerful archbishop who opposes the duke of Austria, in an "
        "impregnable castle never taken by siege. He keeps the Ring of Saint "
        "Maurice, a relic said to make its wearer undefeatable in battle; "
        "Saint Maurice was a soldier martyred in 302 for refusing to worship "
        "the Roman gods.",
        "Eberhard II of Regensberg (history's)",
    ),
)

#: The great abbeys, each in its own place: (key, name, region, founded,
#: summary).
ABBEYS: tuple[tuple[str, str, str, int | None, str], ...] = (
    (
        "saint_gallen_abbey",
        "The Abbey of Saint Gallen",
        "western_alps",
        None,
        paragraphs(
            "Grown from the hermitage of Gallus of Iona, who fell into a "
            "briar, took it for God's sign, and built his cell with a bear's "
            "help. It became a centre of learning that sent out monks to "
            "found houses; its library, the Stiftsbibliothek, is marvellous "
            "still, though its prestige has waned. In the tenth century an "
            "abbot walled the town and with perhaps a hundred armed monks "
            "conquered his neighbours; the abbots have ruled many lands round "
            "it since, with a palace near Rorschach.",
            "The abbot is Valnastium's ally. The book names none.",
        ),
    ),
    (
        "einsiedeln",
        "The Abbey of Einsiedeln",
        "western_alps",
        None,
        paragraphs(
            "Where Saint Meinrad, praying before a figure of the Virgin, was "
            "murdered in 861 and his tame ravens followed his killers to "
            "Zurich. In 968 an angelic voice told the bishop consecrating "
            "its new church that God had consecrated it already; the Pope "
            "made the chapel a place of plenary indulgence, and it is the "
            "Tribunal's greatest pilgrimage, with a torchlight procession "
            "each 14 September.",
            "Second only to Saint Gallen in secular power among the western "
            "abbeys, its abbots are great princes served by hereditary "
            "noble officers. They say they paid for the Devil's Bridge on "
            "the Saint Gotthard; they were given the lands round Schwyz as "
            "waste, and its people fell on their tenants. The book names no "
            "abbot.",
        ),
    ),
    (
        "reichenau",
        "The Abbey of Reichenau",
        "western_alps",
        724,
        paragraphs(
            "A Benedictine abbey that owns its island and estates down "
            "through the Alps to Italy. Charles the Fat, who died here in 888, "
            "lies in its Münster church among dozens of spurious treasures: "
            'a water pot of Cana, and Charlemagne\'s 28-pound "emerald", which '
            "is glass. Merinita magi think the fakes come of a wager between "
            "one of theirs and a local faerie queen, who paid him vis for each "
            "ever more flagrant forgery the Church accepted; the right to the "
            "wager may have passed to an heir.",
        ),
    ),
    (
        "melk",
        "The Abbey of Melk",
        "eastern_marches",
        None,
        paragraphs(
            "Once a Babenberg castle, given to the Benedictines a century and "
            "a half ago. Its monks collect and catalogue knowledge, and its "
            "library is excellent. It answers to the Pope with no bishop "
            "between, and rumour ties it to a school for magi who take "
            "monastic and military vows to war on demons.",
        ),
    ),
)


def _church(alps: Alps) -> None:
    b, w, p = alps.b, alps.world, alps.places
    for key, name, church, region, founded, summary, ruler in CHURCH:
        w[key] = b.church(
            name,
            church=church,
            founded=founded,
            ruler=ruler,
            place=p[region],
            summary=summary,
        )
    for key, name, region, founded, summary in ABBEYS:
        w[key] = b.church(
            name,
            church="Monastery or nunnery",
            order="Benedictine",
            founded=founded,
            place=p[region],
            summary=summary,
        )


# -- towns --


#: (key, name, region, ruler key, summary)
TOWNS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "basel",
        "Basel",
        "western_alps",
        "bishop_of_basel",
        paragraphs(
            "Founded by the Romans in AD 44, near the highest navigable "
            "point of the Rhine, facing a smaller settlement across the "
            "river that it also governs: a cosmopolitan city of merchants "
            "and usurers. Basilisks hatch here more often than elsewhere.",
            "House Mercere owns the Copper Rooster inn here, named "
            "euphemistically for the basilisk: a message point and resting "
            "place for Redcaps of three Tribunals, who change horses, "
            "restock and leave or collect letters bound across the borders. "
            "Old Redcaps retire to it and train apprentices, so some tenants "
            "seem to lodge for ever.",
        ),
    ),
    (
        "berne",
        "Berne",
        "western_alps",
        "emperor",
        "Founded in 1191 by Berthold V of Zähringen, who killed a huge bear "
        "the day he laid its first stone and named it for his prize; the "
        "Emperor's since 1218, and eyeing its neighbours' villages. The "
        "Celts here worshipped a bear goddess, Artio; folk tales tell of an "
        "army of bears led by a talking bear, and a merchant's daughter "
        "married to a bear. The talking bears' home is unknown to the Order.",
    ),
    (
        "constance",
        "Constance",
        "western_alps",
        "bishop_of_constance",
        "The chief city on Lake Constance, regulating the trade from Bavaria "
        "into the Alps; its merchants and its bishop, who rules it, are very "
        "rich. Valnastium keeps a chapter here.",
    ),
    (
        "fribourg",
        "Fribourg",
        "western_alps",
        "savoy",
        "South-west of Berne, founded by Berthold IV of Zähringen in 1157, "
        "now ringed by Savoy's new castles. Folk say that staying up on Saint "
        "John's Eve one may catch the fiery golden seeds of ferns, which the "
        "Devil's servants must buy with a bag of money; magi think them "
        'Ignem vis, "the blood of the Sun".',
    ),
    (
        "geneva",
        "Geneva",
        "western_alps",
        "bishop_of_geneva",
        "A rich city, ruled by the Romans, who made it a see, then by the "
        "Burgundians; its bishop rules it, its count the lands round it, and "
        "Savoy's forts ring both. Valnastium keeps a chapter here.",
    ),
    (
        "lausanne",
        "Lausanne",
        "western_alps",
        "bishop_of_lausanne",
        "A fortified town near Geneva, settled by survivors of the Alemannic "
        "attacks on Roman Lousonna, set to hold the approaches to the Saint "
        "Bernard.",
    ),
    (
        "lucerne",
        "Lucerne",
        "western_alps",
        "emperor",
        "A small fishing village near Mount Pilatus that grows rich and "
        "important as the Saint Gotthard opens. A girl here tells of a "
        "barbegazi who gave her healing herbs and a cheese that turned to "
        "gold, and of the avalanche that buried her heartless uncle. A "
        "dragonet near the town killed its killer with its corrosive blood.",
    ),
    (
        "chur",
        "Chur",
        "western_alps",
        "bishop_of_chur",
        "The chief town of Rhaetia, once a Roman colony.",
    ),
    (
        "zurich",
        "Zurich",
        "western_alps",
        "emperor",
        "Roman Turicum, a customs port for Gaul's textiles bound south, "
        "grown with the trade; under Frederick since 1218.",
    ),
    (
        "interlaken",
        "Interlaken",
        "western_alps",
        "kyburg",
        paragraphs(
            "On a strip of land between the lakes of Thun and Brienz, a "
            "docking point for merchants bound south, under Unspunnen castle. "
            "The Unspunnens' line ended in the beautiful Ida, whom Rudolph of "
            "Wadenschwyl, of a Zähringer house, carried off; years later he "
            "brought her and their son home, and the count founded yearly "
            "games of racing, stone-throwing and wrestling to mark the day.",
            "The Harder Man, a face in Mount Harder's rocks, is said to be a "
            "possessed monk who drove a child off a cliff, set in stone to "
            "wait for the Last Day. Thun's castle is a Zähringer one, "
            "Oberhofen a Hapsburg vassal's, and Spiez, between Thun and "
            "Interlaken, was founded by Attila. The book names no lord here; "
            "the Kyburgs inherited the Zähringers.",
        ),
    ),
    (
        "augsburg",
        "Augsburg",
        "bavaria",
        "duke_of_bavaria",
        "Very rich from its gold, silver and copper mines, and of great "
        "prestige; secret tunnels lie under it.",
    ),
    (
        "munich",
        "Munich",
        "bavaria",
        "duke_of_bavaria",
        "A town grown round a Benedictine monastery of the 700s, and still growing.",
    ),
    (
        "regensburg",
        "Regensburg",
        "bavaria",
        "duke_of_bavaria",
        "The duke of Bavaria's seat and the region's richest city, astride "
        "the Danube where deep-draughted ships can go no further, trading "
        "east and over the Brenner into Italy, so that Italian fashions "
        "show in its richer streets. (The book spells it Regensberg.)",
    ),
    (
        "salzburg",
        "Salzburg",
        "eastern_marches",
        "archbishop_of_salzburg",
        "The chief town of a broad Alpine land since the Romans mined its "
        "salt; it escaped the barbarians who wasted its neighbours and drew "
        "their refugees, and its leaders have long counted in the region. The "
        "archbishop's seat.",
    ),
    (
        "vienna",
        "Vienna",
        "eastern_marches",
        "duke_of_austria",
        paragraphs(
            "At the crossing of the Danube and the road from the Baltic to "
            "Italy: a Roman city abandoned on a saint's advice, a village "
            "for five hundred years, then a crusaders' last German halt; a "
            "town by 1137, the duke's seat since 1156, with a mint from 1190 "
            "and by 1200 a great stop on the road to Venice, rich in wine.",
            "The Rorschach Chapter holds a large property here in the name of "
            "House Mercere's trading house, and Valnastium keeps a chapter. "
            "A basilisk hatched in a house here in 1212; the people chased it "
            "into a well and stoned it in, and several covenants would thank "
            "anyone who learnt its fate.",
        ),
    ),
)


def _towns(alps: Alps) -> None:
    b, w, p = alps.b, alps.world, alps.places
    for key, name, region, ruler, summary in TOWNS:
        lord: Neighbour | None = w.get(ruler)
        w[key] = b.town(
            name,
            answers_to=lord,
            place=p[region],
            summary=paragraphs(summary, "Divine 3 over most of it (DE p. 418)."),
        )


# -- factions --


FACTIONS: tuple[tuple[str, str, dict[str, Any]], ...] = (
    (
        "rowan_sisterhood",
        "The Rowan Sisterhood",
        {
            "faction": "Hermetic group",
            "summary": "An informal society founded in the purge of the Shadow "
            "Flambeau and led by Archmaga Jacinta, all but inactive now, whose "
            "members still watch for diabolic or vampiric corruption and keep "
            "a scattered store of specialised spells and items. Membership "
            "passes to a member's eldest filius or filia, so some sisters are "
            "men, which is kept quiet: it makes the group seem smaller.",
        },
    ),
    (
        "craft_school",
        "The Craft School",
        {
            "faction": "Hermetic group",
            "summary": "A Hermetic movement that prizes beautiful and useful "
            "objects; most Crafters are mage-smiths. Constance of Valnastium "
            "leads it, and Angela belongs. Crafters buy odd things at the Fair "
            "for their art, and vie with natural magicians for objects of "
            "virtue.",
        },
    ),
    (
        "jovians",
        "The Jovians",
        {
            "faction": "Hermetic group",
            "summary": "Archmage Pietro's lineage within House Flambeau, "
            "Auram magi who must learn the Incantation of Lightning and a "
            "longer Wings of the Soaring Wind, and master the first; some "
            "Flambeau call them interlopers. The book's Pietrine lineage "
            "package is a Fourth Edition one and stays in the book.",
        },
    ),
    (
        "black_mark",
        "The Black Mark",
        {
            "faction": "Hermetic group",
            "summary": "A splinter of House Criamon which believes the "
            "Dominion will destroy all magic on Earth unless stopped, and "
            "denies that it comes from an almighty God.",
        },
    ),
    (
        "dyssynergy",
        "The Cult of Dyssynergy",
        {
            "faction": "Hermetic group",
            "summary": "House Criamon's bugbear, which may not exist: its "
            "members are said to oppose humanity's rush into Twilight, for "
            "reasons that change with the teller, and are feared as "
            "diabolists are in other Houses. If the Cult of Twilight is in a "
            "saga, the Cave is one of its centres and the Dyssynergists want "
            "to subvert it.",
        },
    ),
    (
        "vignerons",
        "The Abbaye des Vignerons",
        {
            "faction": "Gild",
            "summary": "A society of vine growers centred on Vevey that acts "
            "like a gild, rewarding skilled growers with medals and pruning "
            "shears. Every fifteen or twenty years it holds a festival: the "
            "best grower is crowned, and the village's loveliest girl gets a "
            "dowry and the husband she chooses. Bronze tools were once given to "
            "the Rhaetians' goddess, so it may be very old.",
        },
    ),
)


def _factions(alps: Alps) -> None:
    b, w, p = alps.b, alps.world, alps.places
    for key, name, kw in FACTIONS:
        w[key] = b.faction(name, place=p["alps"], **kw)


def finish(alps: Alps) -> None:
    """Members of the factions, and the abbot of Saint Gallen as
    Valnastium's ally."""
    w, m = alps.world, alps.magi
    for faction, key, note in (
        ("rowan_sisterhood", "jacinta", "Its leader"),
        ("craft_school", "constance", "A leading member"),
        ("craft_school", "angela", "A member"),
        ("jovians", "pietro", "Its founder"),
    ):
        if faction in w and key in m:
            alps.b.link(w[faction], "characters", m[key], note)
    valnastium = alps.covenants.get("valnastium")
    if valnastium is not None:
        alps.b.link(valnastium, "neighbours", w["saint_gallen_abbey"], "Ally")
