"""The mundane and supernatural world of the west and south of the Rhine
Tribunal: the Emperor and the great princes, the Rhenish archbishops and
bishops, the cities of the Rhine, Lorraine and the Low Countries, the
Swabian towns and monasteries of the Black Forest, and the factions and
threats round them, in paraphrase of Guardians of the Forests chapters
one, two, four, five and six.

Each record is stored in `rhine.world` under a slug key so later parts
(the Gorge, the Tribunal's history) can link to it."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...arms import Arms
from ..builder import Builder, paragraphs, secrets

if TYPE_CHECKING:
    from . import Rhine


def build(rhine: Rhine) -> None:
    b = rhine.b
    w = rhine.world
    valley = rhine.places.get("rhine_valley")
    forest = rhine.places.get("black_forest")
    lowlands = rhine.places.get("lowlands")
    central = rhine.places.get("central")

    _crown_and_princes(b, w, valley, forest, lowlands)
    _archbishops_and_bishops(b, w, valley, forest)
    _rhine_towns(b, w, valley)
    _swabian_towns(b, w, forest)
    _schools(b, w, valley)
    _factions(b, w, valley, forest)
    _threats(b, w, valley, forest, central)


# -- the crown and the princes --


def _crown_and_princes(b: Builder, w, valley, forest, lowlands) -> None:
    w["emperor"] = b.lord(
        "Emperor Frederick II",
        title="duke",
        wealth="Wealthy",
        seat="Sicily",
        ruler="Frederick II of Hohenstaufen",
        arms=Arms("Or", charge="Eagle", charge_tincture="Sable"),
        summary=paragraphs(
            "Holy Roman Emperor, the head of the Hohenstaufen house: born in 1194 "
            "to the emperor Henry VI and a Sicilian mother, made king of Germany in "
            "1212, crowned at Aachen in 1214 and crowned emperor in Rome in 1220. "
            "He is also King of Sicily and bears the titles of King of Italy and of "
            "Burgundy. He keeps his court in Sicily, prefers it to Germany, and is "
            "expected to stay away from the kingdom for more than ten years.",
            "A scholar and poet in the Sicilian tongue, author of a treatise on "
            "falconry and called the wonder of the world, he is tolerant of Moslems "
            "and of magic and has taken the hedge wizard Michael Scot into his court "
            "as his magician, which the Church holds against him. He swore to go on "
            "crusade and has made no move to do so, to the Pope's growing anger. At "
            "the Diet of Frankfurt in 1220 he granted customs privileges. His policy "
            "of clearing forest for settlement makes him an enemy of Dankmar.",
        ),
    )
    w["welfs"] = b.lord(
        "The Welfs of Brunswick",
        title="duke",
        wealth="Wealthy",
        seat="Brunswick",
        place=lowlands,
        arms=Arms("Gules", charge="Lion", charge_tincture="Or", count=2),
        summary=paragraphs(
            "The Saxon ducal house, rivals of the Hohenstaufen since the Swabians "
            "raised an anti-king against them in 1127; the book also gives the Welf "
            "name to the Ottonian emperors. Henry the Lion, duke of Saxony and the "
            "great opponent of Frederick Barbarossa, seized Lübeck in 1157 and made "
            "it a city; in 1180 his duchy was broken up, his lands given to "
            "Hohenstaufen supporters and Bavaria to Otto of Wittelsbach, and he was "
            "sent into exile.",
            "His descendant Otto IV of Brunswick was elected rival king in 1198, "
            "crowned emperor in 1209, excommunicated in 1210, beaten at Bouvines in "
            "1214 and died in 1218, leaving the house out of the crown.",
        ),
    )
    w["count_palatine"] = b.lord(
        "Count Palatine of the Rhine (Wittelsbach)",
        title="count",
        wealth="Wealthy",
        place=valley,
        arms=Arms("Sable", charge="Lion", charge_tincture="Or"),
        summary=paragraphs(
            "The Wittelsbach dukes of Bavaria, who have lately gained the County "
            "Palatine of the Rhine, the lands about the Palatinate Forest and the "
            "Odenwald. A count palatine began as the judicial governor of a royal "
            "estate, an office made to balance the dukes; it is now hereditary.",
            "Barbarossa gave Bavaria, the old Welf stronghold, to Otto of "
            "Wittelsbach after Henry the Lion's fall in 1180. A later Otto of "
            "Wittelsbach, count palatine, murdered King Philip of Swabia at Bamberg "
            "in 1208.",
        ),
    )
    w["dukes_of_upper_lorraine"] = b.lord(
        "Dukes of Upper Lorraine",
        title="duke",
        seat="Nancy",
        ruler="Dietrich III",
        place=valley,
        summary=(
            "The dukes rule Upper Lorraine from the fortress Duke Gerard raised at "
            "Nancy, hemmed in between the kings of France and the rival counts of "
            "Bar and Luxemburg. They have never recovered Metz, whose burghers threw "
            "them out in 1143 and now thwart them at every turn, though Toul stays "
            "loyal. Duke Dietrich III is expected to die this year, 1220, and his "
            "heir Matthew II to succeed him."
        ),
    )
    w["counts_of_holland"] = b.lord(
        "Counts of Holland",
        title="count",
        place=valley,
        arms=Arms("Or", charge="Lion", charge_tincture="Gules"),
        summary=(
            "The counts are draining new land from the marshes of the Rhine delta "
            "and founding towns on it, and with the bishop of Utrecht they hunt the "
            "pirates of the Zuider Sea, a fight centred on Deventer."
        ),
    )
    w["dukes_of_brabant"] = b.lord(
        "Dukes of Brabant",
        title="duke",
        wealth="Wealthy",
        place=valley,
        arms=Arms("Sable", charge="Lion", charge_tincture="Or"),
        summary=(
            "Lower Lorraine has broken into two rival duchies, Brabant and Limburg, "
            "with small counties filling the rest; Brabant is the greater. The lords "
            "of Cleves ruled Brabant once but do so no longer."
        ),
    )
    w["dukes_of_limburg"] = b.lord(
        "Dukes of Limburg",
        title="duke",
        place=valley,
        summary=(
            "The second of the two principal duchies into which Lower Lorraine has "
            "split, in rivalry with Brabant; the rest of the old duchy is a "
            "scatter of small counties."
        ),
    )
    w["lords_of_cleves"] = b.lord(
        "Lords of Cleves",
        title="baron",
        seat="The Schwanenburg",
        place=valley,
        summary=(
            "The lords hold the Schwanenburg, the Swan Castle above Cleves on the "
            "lower Rhine, and bear a swan in their arms. They once ruled Brabant "
            "but have lost it."
        ),
    )
    w["zahringen"] = b.lord(
        "The Zähringens",
        title="duke",
        wealth="Wealthy",
        seat="Zähringen castle, north of Freiburg",
        place=forest,
        arms=Arms("Or", charge="Eagle", charge_tincture="Gules"),
        summary=paragraphs(
            "Former dukes of Swabia whose estates lay in the fertile strip between "
            "the Rhine and the Black Forest. In the twelfth century they were the "
            "foremost castle builders of western Swabia and drew power and taxes "
            "from the Black Forest monasteries they founded and controlled. Conrad "
            "Zähringen founded Freiburg in 1120; the family castle stands just north "
            "of the town, and a lesser branch has its seat in the lower town of "
            "Baden.",
            "The main line failed in 1218 and the Hohenstaufen have taken much of "
            "its land. Their settlement of the forest cost Durenmar several magical "
            "sites early in the twelfth century; some wonder whether the covenant "
            "patronised the house or caused its withering, which is thought "
            "unlikely.",
        ),
    )
    w["hohenstaufen"] = b.lord(
        "The Hohenstaufens",
        title="duke",
        wealth="Wealthy",
        seat="Hohenstaufen castle, south of Gmünd",
        ruler="Frederick II",
        place=forest,
        arms=Arms("Or", charge="Lion", charge_tincture="Sable", count=3),
        summary=(
            "The imperial dynasty of Conrad III, Frederick Barbarossa and the "
            "present emperor Frederick II, and the Zähringens' rivals for Swabia, "
            "where they now hold much of the failed house's land. Their ancestral "
            "castle crowns the Hohenstaufen hill, the grandest of the three "
            "Kaiserberge south of Gmünd, the town Conrad III founded. The emperor's "
            "policy of clearing forest makes the house an enemy of Dankmar."
        ),
    )
    w["hohenzollern"] = b.lord(
        "The Hohenzollerns",
        title="count",
        place=forest,
        arms=Arms("Argent", division="Quarterly", second="Sable"),
        summary=(
            "Local lords of the Swabian Jura who have built forts on the defensible "
            "limestone peaks of those harsh hills."
        ),
    )
    w["free_imperial_cities"] = b.faction(
        "The Free Imperial Cities",
        faction="Other",
        members=14,
        rules=(
            "Each city answers to the emperor alone and not to any local lord; "
            "several are governed by their own councils."
        ),
        wants="Trade unhindered by any lord's tolls or wars.",
        offers="Wealth kept out of the hands of rival dukes, and loyalty to the crown.",
        summary=paragraphs(
            "Fourteen cities that in 1220 owe allegiance only to the emperor, who "
            "frees rich towns so their wealth is denied to rival dukes: Dortmund, "
            "Esslingen, Goslar, Hamburg, Metz, Nördlingen, Nuremberg, Regensburg, "
            "Schwäbisch-Hall, Speyer, Ulm, Wetzlar, Wimpfen and Worms. Ulm was freed "
            "in 1155 (the Black Forest chapter gives 1164), Hamburg in 1189 and "
            "Nuremberg in 1219.",
            "Lübeck is expected to join them in 1226, Aachen and Erfurt in 1250 and "
            "Cologne not until 1288.",
        ),
    )
    w["teutonic_knights"] = b.church(
        "The Teutonic Knights",
        church="Monastery or nunnery",
        order="Teutonic Knights (military order)",
        arms=Arms("Argent", charge="Cross", charge_tincture="Sable"),
        summary=(
            "The Order of Teutonic Knights, founded at Acre in 1190, crusades "
            "against the pagans of the Baltic alongside the Livonian Order of the "
            "Knights of the Sword, formed in 1202 in Pomerania and Livonia. The "
            "Sword Brothers are expected to be reprimanded and absorbed into the "
            "Teutonic Order in 1237, and the Order to conquer Prussia in 1240."
        ),
    )


# -- the Church --


def _archbishops_and_bishops(b: Builder, w, valley, forest) -> None:
    w["archbishop_of_mainz"] = b.church(
        "Archbishop of Mainz",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=valley,
        arms=Arms("Gules", charge="Wheel", charge_tincture="Argent"),
        summary=paragraphs(
            "The first churchman of Germany: Archchancellor of the Empire, chief "
            "of the princes who elect the king, the prelate who crowns him at "
            "Aachen, and as primate of Germany the Pope's deputy north of the Alps. "
            "His see counts as a Holy See, the only one besides Rome, which gives "
            "the cathedral its Divine aura of 7. The line began with St Boniface in "
            "the eighth century, and Willigis won the Archchancellorship in the "
            "tenth.",
            "Rhine traffic transships at Mainz for the Main and the upper river, and "
            "the customs make the archbishop very rich. The episcopal palace saw the "
            "ritual suicide of the city's Jews in 1096. The book does not name the "
            "present archbishop or give his stance toward magi; the Peace of Mainz "
            "is expected to be proclaimed here in 1235.",
        ),
    )
    w["archbishop_of_cologne"] = b.church(
        "Archbishop of Cologne",
        church="Archbishop's cathedral",
        order="secular clergy",
        ruler="Engelbert I",
        place=valley,
        arms=Arms("Argent", charge="Cross", charge_tincture="Sable"),
        summary=paragraphs(
            "Archchancellor of Italy, a prince of the Empire and ruler of its "
            "greatest city, which holds the relics of the Three Magi that Frederick "
            "Barbarossa carried off from Milan in 1164. The present archbishop, "
            "Engelbert I, is tall, fair and just, praised by the poet Walther von der "
            "Vogelweide; if history holds he will be murdered in 1225.",
            "His stance toward magi is not given, though Fengheld keeps a chapter "
            "house in his city. Cologne is expected to become a Free Imperial City "
            "only in 1288.",
        ),
    )
    w["archbishop_of_trier"] = b.church(
        "Archbishop of Trier",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=valley,
        arms=Arms("Argent", charge="Cross", charge_tincture="Gules"),
        summary=paragraphs(
            "The third of the great Rhenish prince-archbishops, lord of the oldest "
            "city in Germany and its oldest church, the cathedral of St Peter. In "
            "1200 the archbishop led an army of angry townsfolk that destroyed the "
            "covenant of Rheinstein in the Rhine Gorge, after which the Tribunal "
            "banned magic in the Gorge for twenty years: a hostile precedent "
            "toward magi.",
            "Trier's earlier covenant, Treverorum, had already been fined and then "
            "collapsed between 1165 and 1172 over its meddling with the town and "
            "the Church.",
        ),
    )
    w["bishop_of_worms"] = b.church(
        "Prince-bishop of Worms",
        church="Bishop's cathedral",
        order="secular clergy",
        place=valley,
        summary=(
            "The bishop rules Worms in his own right as a prince of the Empire, "
            "holding a royal fief of the kind earlier kings granted bishops to "
            "counter the dukes and governing through a lay advocate with power of "
            "life and death. His cathedral has a Divine aura of 6. His stance "
            "toward magi is not given."
        ),
    )
    w["bishop_of_speyer"] = b.church(
        "Bishop of Speyer",
        church="Bishop's cathedral",
        order="secular clergy",
        place=valley,
        summary=(
            "The bishop rules Speyer, the Salian emperors' favourite seat, whose "
            "cathedral (Divine aura 6) was begun by Conrad II in 1030 and holds "
            "kings and emperors in its crypt. During the First Crusade massacre his "
            "protection saved most of the city's Jews, though a dozen were killed in "
            "the cathedral for refusing baptism."
        ),
    )
    w["bishop_of_liege"] = b.church(
        "Prince-bishop of Liège",
        church="Bishop's cathedral",
        order="secular clergy",
        place=valley,
        summary=(
            "Liège has been a prince-bishopric since Otto II granted the diocese as "
            "a fief to Bishop Notger, who built the cathedral of St Lambert, the "
            "bishops' palace and the walls. The see has outgrown Verdun. Henry IV "
            "died here excommunicate."
        ),
    )
    w["bishop_of_utrecht"] = b.church(
        "Bishop of Utrecht",
        church="Bishop's cathedral",
        order="secular clergy",
        place=valley,
        arms=Arms("Gules", charge="Cross", charge_tincture="Argent"),
        summary=(
            "An early missionary bishopric of the Rhine delta. The bishop holds "
            "estates in the lands the counts of Holland are draining, and with "
            "the counts fights the pirates of the Zuider Sea."
        ),
    )
    w["convent_of_st_odile"] = b.church(
        "Convent of St Odile (Hohenburg)",
        church="Monastery or nunnery",
        place=valley,
        summary=(
            "A pilgrimage convent on Mount Saint Odile in the Vosges, where the "
            "saint was buried in 720; its spring has a Divine aura of 4."
        ),
    )
    w["hirsau"] = b.church(
        "Hirsau",
        church="Monastery or nunnery",
        order="Benedictine",
        founded=1059,
        place=forest,
        summary=paragraphs(
            "Probably the most powerful monastery in Germany, by a bridge over the "
            "Nagold north-east of the Black Forest, some fifteen miles north of "
            "Durenmar. Founded in 1059 with the relics of St Aurelius, a "
            "fifth-century Armenian bishop, it now has more than a hundred monks "
            "and daughter houses all over Germany, St Georgen among them. It led the "
            "eleventh-century Hirsau reform that freed religious houses from lay "
            "lords and bishops, bringing the customs of Cluny into Germany. Built of "
            "red sandstone, its basilica of St Aurelius is a hundred yards long.",
            "Its Divine aura is 5, and whether from the aura, its size or its place "
            "at the forest's edge it is largely immune to the faerie attacks other "
            "Black Forest houses suffer. It spreads rumours of Durenmar as a hidden "
            "city of sorcerers; magi for their part note how alike the two are, "
            "each a learned centre with many daughter houses holding back the "
            "forest. Legend has it that a Bonisagus archmagus renounced magic, took "
            "orders and helped found the house, and some think the monastery may be "
            "heir to his magical legacy, though no magus has braved the Dominion "
            "to find out.",
        ),
    )
    w["gengenbach"] = b.church(
        "Gengenbach",
        church="Monastery or nunnery",
        place=forest,
        summary=(
            "A monastery at the western end of the long uninhabited stretch of "
            "the Black Forest Road; the book gives no more about it."
        ),
    )
    w["blaubeuren"] = b.church(
        "Kloster Blaubeuren",
        church="Monastery or nunnery",
        place=forest,
        summary=(
            "A monastery beside the Blautopf pool at the southern edge of the "
            "Swabian Jura, whose humble monks go to the water faerie called the "
            "Schöne Lau to have their futures told."
        ),
    )
    w["zweifalten"] = b.church(
        "Zweifalten",
        church="Monastery or nunnery",
        place=forest,
        summary=(
            "A monastery on the south side of the Swabian Jura, near the "
            "Wimsener Höhle where the River Ach runs underground; the book gives "
            "no more about it."
        ),
    )


# -- the Rhine, Lorraine and the Low Countries --


def _rhine_towns(b: Builder, w, valley) -> None:
    w["cologne"] = b.town(
        "Cologne",
        charter="Church",
        population=20000,
        ruler="Archbishop Engelbert I",
        answers_to=w["archbishop_of_cologne"],
        place=valley,
        arms=Arms("Argent", charge="Crown", charge_tincture="Gules", count=3),
        summary=paragraphs(
            "The largest and grandest city in Germany and the biggest in the Empire "
            "north of the Alps, with more than twenty thousand citizens: the chief "
            "trading town of the kingdom and the hub of the Rhine. Roman Colonia "
            "Claudia Ara Agrippinensis, settled in 38 BC and a colony from 50 AD at "
            "Agrippina's request, it was capital of Lower Germania; Constantine's "
            "bridge of 310 has long since fallen. Walls of 1180 with a dozen gates "
            "and a moat enclose a half-circle two miles across on the west bank; "
            "sixteen great churches stand beside the cathedral (Divine aura 6), "
            "with many chapels and monasteries, and a quayside more than a mile "
            "long holds hundreds of ships with the main market behind it. Its "
            "weavers, dyers, goldsmiths, weaponsmiths and armourers are famous.",
            "The archbishop rules the city. The bones of the Three Magi, taken from "
            "Milan in 1164, lie in a golden shrine in the cathedral, and the church "
            "of St Ursula stands where the princess and her eleven thousand and ten "
            "virgins were slain by the Huns. The city's banner shows a two-headed "
            "black eagle with sword and sceptre under an archbishop's crown, with "
            "three gold crowns for the Magi and eleven flames for Ursula's "
            "thousands on its breast. The Jews were massacred here in 1096 and "
            "again in 1147. Fengheld keeps a chapter house in the Rheingasse near "
            "the market, staffed by Apple Gild magi. A vast new cathedral is "
            "expected to be begun in 1248, and the city to become a Free Imperial "
            "City in 1288.",
        ),
    )
    w["mainz"] = b.town(
        "Mainz",
        charter="Church",
        answers_to=w["archbishop_of_mainz"],
        place=valley,
        arms=Arms("Gules", charge="Wheel", charge_tincture="Argent"),
        summary=paragraphs(
            "Roman Moguntiacum, founded in 13 BC, on the Rhine where the Main comes "
            "in; an archbishopric since St Boniface in the eighth century and the "
            "Church's centre for all Germany. Its red sandstone cathedral has six "
            "towers and two choirs, one for the clergy and one for the emperor, and "
            "like St Peter's runs east to west; hemmed in by buildings, among them "
            "St Gothard, the archbishop's chapel, it has a Divine aura of 7 as a "
            "Holy See.",
            "Goods bound for Frankfurt on the Main or the upper Rhine are "
            "transshipped here, and the customs make the archbishop very rich. The "
            "Jewish academy has been famous since the tenth century, drawing "
            "students from Spain and Italy; the Jews of the city died by their own "
            "hands in the episcopal palace in 1096 and suffered again in 1147.",
        ),
    )
    w["trier"] = b.town(
        "Trier",
        charter="Church",
        answers_to=w["archbishop_of_trier"],
        place=valley,
        arms=Arms("Argent", charge="Cross", charge_tincture="Gules"),
        summary=(
            "On the Mosel; Roman Augusta Treverorum, founded in 16 BC on an older "
            "settlement and the oldest city in Germany. Constantine made it the "
            "western capital of the empire between 306 and 337, and its cathedral "
            "of St Peter is Germany's oldest church. The archbishop's seat; in 1096 "
            "the city's Jews drowned themselves rather than accept baptism. The "
            "covenant of Treverorum stood here until it was abolished in 1172."
        ),
    )
    w["worms"] = b.town(
        "Worms",
        charter="Commune",
        ruler="The prince-bishop of Worms",
        answers_to=w["bishop_of_worms"],
        place=valley,
        arms=Arms("Sable", charge="Key", charge_tincture="Argent"),
        summary=paragraphs(
            "An Upper Rhine city of Celts, Romans, Burgundians and Franks, a Free "
            "Imperial City ruled by its own prince-bishop. The Burgundians made it "
            "their capital in 413 and the Nibelungenlied is set here; Charlemagne "
            "and Barbarossa married here, and the Concordat of 1122 that ended the "
            "Investiture Contest was sealed here. The squat cathedral (Divine aura "
            "6), with two domed choirs, four round towers of seven tiers and "
            "strange statues, stands on the old Burgundian castle Charlemagne made "
            "his palace; an inscription calls it the Romans' holy temple, the "
            "Nibelungs' fortress and Charlemagne's hall, and its north door, the "
            "Kaiserportal, marks the quarrel of the queens Kriemhild and Brünhild.",
            "The northern third of the city is Little Jerusalem, the largest Jewish "
            "settlement in Germany, sacked in the first two Crusades; its synagogue "
            "was finished in 1175 and its ancient cemetery, the Heiliger Sand, lies "
            "outside the west wall. Frederick II is expected to wed Elizabeth of "
            "England here in 1235.",
        ),
    )
    w["speyer"] = b.town(
        "Speyer",
        charter="Commune",
        ruler="The bishop of Speyer",
        answers_to=w["bishop_of_speyer"],
        place=valley,
        summary=paragraphs(
            "A Roman camp on the Upper Rhine that became the favourite seat of the "
            "Salian emperors in the early eleventh century, and a Free Imperial "
            "City ruled by its bishop. Conrad II began the great cathedral in 1030 "
            "(Divine aura 6); kings and emperors lie in its crypt. The wealthy "
            "Jewish quarter south-west of the cathedral has a grand synagogue and "
            "bath-houses and trains rabbis; the bishop's protection saved most of "
            "its people in the First Crusade massacre, though a dozen were murdered "
            "in the cathedral for refusing baptism, and the city suffered again in "
            "1147.",
            "The bells of Speyer ring of themselves when an emperor dies. They "
            "stayed silent for the excommunicated Henry IV until his body was "
            "reburied here five years on and his faithful servant Kurt died, and "
            "for Henry V they rang the pattern tolled for a sinner led to "
            "execution.",
        ),
    )
    w["strassburg"] = b.town(
        "Strassburg",
        place=valley,
        summary=(
            "Roman Argentoratum, on a Celtic fishing village where the Ill meets "
            "the Upper Rhine; wrecked several times by invaders, it is now a "
            "thriving trading city at a crossroads, its name meaning the castle of "
            "roads, and is built around canals. The powerful boatmen's gild "
            "controls much of the trade of the Upper Rhine. Its ruler is not given."
        ),
    )
    w["basel"] = b.town(
        "Basel",
        place=valley,
        summary=(
            "On the Upper Rhine where the river turns north, at the head of "
            "navigation. House Mercere keeps the Copper Rooster Inn here for "
            "Redcaps passing between the Greater Alps, Rhine and Normandy "
            "Tribunals. Its ruler is not given."
        ),
    )
    w["mulhouse"] = b.town(
        "Mulhouse",
        place=valley,
        summary=(
            "A town of the southern Vosges and Upper Rhine, a dozen miles east of "
            "Thann Chapel; the book says no more of it."
        ),
    )
    w["metz"] = b.town(
        "Metz",
        charter="Commune",
        place=valley,
        summary=(
            "Gaulish and then Roman Divodurum, where the Seille joins the Mosel in "
            "Upper Lorraine; sacked by the Huns, when St Livier, beheaded by Attila, "
            "carried his head to his hilltop grave. Capital of Austrasia in the "
            "sixth century and of Lotharingia in the ninth. A Free Imperial City "
            "since its burghers rose against the duke in 1143, it is now a rich "
            "little republic behind stern walls that lends money to the French king, "
            "the Emperor and the dukes, and keeps thwarting the dukes of Upper "
            "Lorraine. Its cathedral of St Stephen is one of several grand churches."
        ),
    )
    w["toul"] = b.town(
        "Toul",
        charter="Noble lord",
        answers_to=w["dukes_of_upper_lorraine"],
        place=valley,
        summary=(
            "Roman Tullum, forty miles up the Mosel from Metz: venerable but poorer "
            "and with fewer tales to tell, loyal to the duke of Upper Lorraine, "
            "behind tall white stone walls that are partly Roman."
        ),
    )
    w["verdun"] = b.town(
        "Verdun",
        place=valley,
        summary=(
            "On the Meuse above the Ardennes in Upper Lorraine; the treaty that "
            "divided the Carolingian empire was made here in 843, and the Treaty of "
            "Mersen of 870 passed it to the western kingdom before it came into the "
            "Empire. A border city of intrigue that grew in the eleventh century and "
            "now declines behind Liège and Metz; spies and assassins can be hired "
            "here for work on either side of the border. Redcaps often meet here "
            "on the way between the Rhine and Normandy Tribunals."
        ),
    )
    w["nancy"] = b.town(
        "Nancy",
        charter="Noble lord",
        ruler="The duke of Upper Lorraine",
        answers_to=w["dukes_of_upper_lorraine"],
        place=valley,
        summary=(
            "The seat of the dukes of Upper Lorraine, grown round the fortress Duke "
            "Gerard built between two marshes in the eleventh century as the "
            "central stronghold of his duchy."
        ),
    )
    w["xanten"] = b.town(
        "Xanten",
        place=valley,
        summary=(
            "On the west bank of the lower Rhine: Roman Colonia Ulpia Traiana, "
            "where St Victor and the Theban Legion were martyred; the new town grew "
            "on their graveyard as Ad Sanctos Martyres, shortened to Xanten. The "
            "birthplace of Siegfried, the old capital of the Nibelungs' land and the "
            "first home of the Rhinegold. Its ruler is not given."
        ),
    )
    w["cleves"] = b.town(
        "Cleves",
        charter="Noble lord",
        answers_to=w["lords_of_cleves"],
        place=valley,
        summary=(
            "A lower Rhine town below the Schwanenburg, held by the lords of "
            "Cleves, who bear a swan in their arms and no longer rule Brabant."
        ),
    )
    w["deventer"] = b.town(
        "Deventer",
        place=valley,
        summary=(
            "A modest town on the right bank of the lower Rhine, set in marshland "
            "with waterways to the Zuider Sea and the river mouths, and with Utrecht "
            "one of the early missionary bishoprics. Its church of St Lebuinus "
            "began as a chapel in 768, was burnt by the Saxons and rebuilt by St "
            "Liudger in 776. It is the centre of the war the counts of Holland and "
            "the bishop of Utrecht wage on the Zuider Sea pirates; the town militia "
            "hunts them, yet sailors of doubtful character can still be hired "
            "here."
        ),
    )
    w["aachen"] = b.town(
        "Aachen",
        place=valley,
        summary=paragraphs(
            "Charlemagne's palace city in Lower Lorraine, on the road from Cologne "
            "to Liège and Flanders. He founded it in 768 after his horse stepped "
            "into a hot sulphur spring beside Roman baths, raised a round church "
            "shaped like a hoof over it, held his court here and was buried here "
            "in 814. German kings are crowned here by the archbishop of Mainz, on "
            "his throne of marble, wood and gold at the top of six steps: Otto I in "
            "936 and Frederick II in 1214.",
            "No longer of political weight, the city keeps a cathedral (Divine aura "
            "6) with a matchless hoard of relics, among them John the Baptist's "
            "garments, the Virgin's gown and Christ's swaddling clothes, and a newly "
            "finished shrine over Charlemagne's tomb. It is expected to become a "
            "Free Imperial City in 1250.",
        ),
    )
    w["liege"] = b.town(
        "Liège",
        charter="Church",
        ruler="The prince-bishop of Liège",
        answers_to=w["bishop_of_liege"],
        place=valley,
        summary=(
            "A sizeable market city of Lower Lorraine where the Legia joins the "
            "Meuse, grown round the miracle-working tomb St Hubert raised for the "
            "martyred St Lambert, bishop of Tongeren, in the seventh century. Otto "
            "II granted the diocese to Bishop Notger as a fief, and he built the "
            "cathedral of St Lambert, the prince-bishops' palace and the walls. "
            "Henry IV died here excommunicate."
        ),
    )
    w["utrecht"] = b.town(
        "Utrecht",
        charter="Church",
        ruler="The bishop of Utrecht",
        answers_to=w["bishop_of_utrecht"],
        place=valley,
        summary=(
            "An early missionary bishopric in the Rhine delta. Its bishop holds "
            "estates in the draining lands of Holland and fights the Zuider Sea "
            "pirates together with the counts of Holland."
        ),
    )


# -- Swabia and the Black Forest --


def _swabian_towns(b: Builder, w, forest) -> None:
    w["baden"] = b.town(
        "Baden",
        charter="Noble lord",
        ruler="A lesser branch of the Zähringens",
        answers_to=w["zahringen"],
        place=forest,
        summary=(
            "Roman Aquae, between the Rhine valley and the north-western slopes of "
            "the Black Forest, named for the hot springs halfway up the "
            "Florentinerberg that cure rheumatism and arthritis; the Romans built "
            "extensive baths. The upper town is mostly ruined and keeps a Magic "
            "aura of 2; Durenmar claims it as Hermetic property and harvests vis "
            "from the springs. The lower town is the seat of a lesser Zähringen "
            "branch. Not the other spa called Baden a hundred miles south beyond "
            "the Rhine, in the Greater Alps Tribunal."
        ),
    )
    w["freiburg"] = b.town(
        "Freiburg",
        charter="Noble lord",
        answers_to=w["zahringen"],
        place=forest,
        summary=(
            "The largest settlement about the Black Forest, founded in 1120 by "
            "Conrad Zähringen in the valley of the Dreisam with wooded heights on "
            "three sides. Around 1200 its citizens began paying for a lofty "
            "cathedral of the local red sandstone. The Zähringen castle stands a "
            "short way to the north."
        ),
    )
    w["rottweil"] = b.town(
        "Rottweil",
        place=forest,
        summary=paragraphs(
            "On the eastern edge of the forest at the eastern end of the Black "
            "Forest Road, perched defensibly over the upper Neckar. Roman Arae "
            "Flaviae, the Altar of the Flavians, was meant as a provincial capital "
            "at a crossroads until the frontier moved on; Roman temples, baths and "
            "buildings lie buried under the town, fewer than at Baden.",
            "Home of the Rottweiler, a large, fierce black-and-tan dog bred from "
            "Roman stock crossed with the dark faerie dogs of the forest, called the "
            "butcher's dog because butchers train it to pull carts; it seldom "
            "barks, keeps poor guard and attacks superbly. At least one Rhine magus "
            "keeps Rottweilers in place of grogs; a strongly faerie-blooded one "
            "ages like a man and often has Second Sight or Faerie Blood, while an "
            "ordinary dog makes seven aging rolls a year.",
        ),
    )
    w["offenburg"] = b.town(
        "Offenburg",
        place=forest,
        summary=(
            "The town at the western end of the Black Forest Road; the book gives "
            "no more about it."
        ),
    )
    w["waldmossingen"] = b.town(
        "Waldmössingen",
        place=forest,
        summary=(
            "An isolated village on the site of a ruined Roman fort at the eastern "
            "end of the Black Forest Road's uninhabited thirty-mile stretch."
        ),
    )
    w["gmund"] = b.town(
        "Gmünd",
        charter="Noble lord",
        answers_to=w["hohenstaufen"],
        place=forest,
        summary=(
            "A town of the Stauferland, the rolling hills between the Swabian "
            "Forest and the Swabian Jura named for the Hohenstaufens, founded by "
            "Conrad III in the twelfth century on the line of the Roman limes. It "
            "makes luxuries, jewellery and glassware. South of it rise the three "
            "round wooded Kaiserberge, each topped by a castle: Hohenstaufen to "
            "the west, the lowest and grandest and the imperial ancestral seat, "
            "Hohenrechberg, and Stuifen to the east, the highest."
        ),
    )
    w["ulm"] = b.town(
        "Ulm",
        charter="Commune",
        place=forest,
        summary=(
            "On the north bank of the upper Danube, first settled in the ninth "
            "century by Jews, of whom a small community remains. Frederick "
            "Barbarossa made it a Free Imperial City in 1164 and it has grown "
            "prosperous since: flax fields surround it, its many weavers make "
            "linen, and the cloth is traded across the Empire."
        ),
    )
    w["seebach"] = b.town(
        "Seebach",
        place=forest,
        summary=(
            "A settlement in the mountains near Mummel Lake, whose nixe comes "
            "down to the villages round about to bewitch young men."
        ),
    )


# -- schools --


def _schools(b: Builder, w, valley) -> None:
    w["jewish_academy_of_mainz"] = b.university(
        "Jewish academy of Mainz",
        school="Urban school",
        place=valley,
        summary=(
            "The centre of Jewish scholarship in Germany since the tenth century, "
            "known across Europe and drawing students from Spain and Italy. It gave "
            "rise to the Chasidic renaissance and to reforms of the law that "
            "widened women's rights and permitted usury, so that pious Jews could "
            "trade."
        ),
    )


# -- factions --


def _factions(b: Builder, w, valley, forest) -> None:
    w["forest_guides"] = b.faction(
        "Bjornaer and Merinita, guides of the forest paths",
        faction="Other",
        realm="Magic",
        offers="A guide to the paths of power through the forest, for those who can follow.",
        summary=(
            "The only two Houses that can show a seeker the paths through the "
            "forest: the heartbeast mystery of House Bjornaer is itself a path that "
            "every apprentice walks, and some Merinita know the routes into "
            "Arcadia. Their methods are alien to one another and to House "
            "Bonisagus; Causabon of Bonisagus muses that the three domus magnae "
            "each hold a fragment of the truth and ought to pool their secrets."
        ),
    )
    w["hercynius_lineage"] = b.faction(
        "The Hercynius lineage of House Bonisagus",
        faction="Other",
        realm="Magic",
        wants="To channel the forests' primal magic and complete the great work Bonisagus began.",
        summary=secrets(
            "A rumour from Causabon's journal: that a remaining few who follow "
            "Hercynius are working to channel the primal magic of the forests and "
            "finish the opus maximum of Bonisagus, who believed that Hermetic magic "
            "was only the beginning of it.",
            "The lineage's existence and purpose are rumour only; the book "
            "confirms nothing.",
        ),
    )
    w["hedge_wizards_of_the_paths"] = b.faction(
        "Hedge wizards of the forest paths",
        tradition="trad_forest_paths",
        faction="Hedge coven",
        realm="Magic",
        offers="Teaching of a path through the forest to magi, for a suitable price.",
        summary=(
            "Some hedge wizards know the paths of power through the forests and "
            "will teach them to magi for the right price. Mundanes who yield "
            "themselves to the forest gain minor spells and commonly end up "
            "possessed, serving as the spirit's agents beyond the trees."
        ),
    )
    w["forest_guardians"] = b.faction(
        "Forest Guardians",
        faction="Other",
        realm="Magic",
        rules=(
            "A Guardian publicly declares a wilderness his Hermetic territory and "
            "defends it; the Rhine Peripheral Code encourages the defence of "
            "wildernesses but gives him little other legal footing."
        ),
        wants="To keep the forests they guard untouched.",
        summary=(
            "Rhine magi, most of them Bjornaer, who publicly claim a wilderness as "
            "their Hermetic territory and defend it. The Rhine Peripheral Code "
            "encourages magi to defend wild places, which gives them some standing "
            "and little else in law. Becoming a Guardian is a sacrifice to the "
            "forest's spirit, and Guardians are rarely seen at Tribunal afterwards."
        ),
    )
    w["brethren_of_the_free_spirit"] = b.faction(
        "The Brethren of the Free Spirit",
        faction="Other",
        place=valley,
        rules="If all is God, nothing is sin.",
        wants=(
            "A new age of the Holy Spirit, and for its noble members lordship "
            "free of the Church."
        ),
        offers="Indulgence without sin, and for fanatics a claimed immunity to fire and torture.",
        summary=secrets(
            paragraphs(
                "A heretical pantheist cult born of Paris theologians at the start "
                "of the thirteenth century, from David of Dinant's teaching that "
                "God, matter and mind are one substance; it has spread in secret to "
                "Cologne and the country round it, among commoners and among nobles "
                "who want lordship free of the Church. Since all is God, nothing is "
                "sin: the Brethren hold naked masses to recreate Eden and indulge "
                "in licence and crime, and their fanatics claim that fire and "
                "torture cannot harm them. They herald a new age of the Holy "
                "Spirit.",
                "The Holy Vehm of Saxony counts them mortal enemies, hunts them and "
                "means to prove their claims false.",
            ),
            "An option for the saga: the magi of Fengheld's Cologne chapter house, "
            "all of the Apple Gild, may lead the Brethren, and a part of the cult "
            "may be a Mystery Cult of Rhine and Normandy magi; the creed suits the "
            "Apple Gild's aim of winning mundane acceptance of magic.",
        ),
    )
    w["chasidim"] = b.faction(
        "The Chasidim",
        faction="Other",
        realm="Divine",
        place=valley,
        rules="Asceticism, readiness for martyrdom and lifelong penitence.",
        summary=(
            "The German Jewish pietists, a mystical movement that arose after the "
            "First Crusade and centres on the academy of Mainz. They teach "
            "asceticism, martyrdom and lifelong penitence, and have reformed the "
            "law to widen women's rights and to permit usury, so that pious Jews "
            "may trade."
        ),
    )
    w["boatmens_gild"] = b.faction(
        "Boatmen's gild of Strassburg",
        faction="Gild",
        place=valley,
        wants="Its hold on the river trade of the Upper Rhine.",
        offers="Passage and carriage on the Upper Rhine.",
        summary=(
            "A powerful gild that controls much of the trade of the Upper Rhine "
            "from the canals of Strassburg."
        ),
    )
    w["zuider_sea_pirates"] = b.faction(
        "Zuider Sea pirates",
        faction="Other",
        place=valley,
        offers="Sailors of doubtful character for hire in Deventer.",
        summary=(
            "Pirates who roam the inland sea off Deventer. The town's militia, the "
            "counts of Holland and the bishop of Utrecht all hunt them, yet "
            "disreputable sailors still hire out in Deventer."
        ),
    )
    w["cult_of_mercury"] = b.faction(
        "The Cult of Mercury",
        faction="Other",
        realm="Magic",
        summary=(
            "The Roman magician-priests of the Rhine frontier towns, long gone. "
            "They sensed the power of the Hercynian forest spirit, built a temple "
            "on the site where Durenmar now stands and there bound the Black "
            "Forest's spirit by oath into the Fane of the Founders, guided the "
            "legions' limes and the Black Forest Road with warding milestones, and "
            "linked their temples and roads by magic into a barrier against the "
            "wilderness of Germania Magna. In doing so they began the great "
            "spirit's fragmentation; the splinter they bound later became the "
            "King of the Black Mountain."
        ),
    )
    w["bockmen"] = b.faction(
        "Bockmen",
        faction="Faerie court",
        realm="Faerie",
        place=forest,
        rules="Nearly always alone; discourage travel through the forest.",
        offers="A pawn of Animal vis in the right horn and one of Mentem in the left.",
        summary=paragraphs(
            "Goat-headed, goat-legged faeries of Might 20 (Animal) and Size -1 with "
            "backward-curving horns, feral eyes and slavering jaws, who lurk by the "
            "paths of the Black Forest and the oldest German forests, nearly always "
            "alone. Invisible while still, they unsettle travellers and their "
            "mounts for hours (birds fall silent, dread grows, brave traits sink "
            "by one each hour, and no one sleeps or recovers fatigue), then leap "
            "out to strike with fear that sends the victim fleeing until exhausted "
            "or collapsing until dawn. They are weak and cowardly in a fight "
            "(claws Init +9, Attack +13, Defence +9, Damage +3; Soak +5; iron does "
            "them two extra damage) but succeed in their purpose, which is to keep "
            "people out of the forest.",
            "Orphedra of Dankmar has a pact with the local bockmen to patrol the "
            "surroundings of her covenant.",
        ),
    )
    w["dark_fae"] = b.faction(
        "Dark fae of the deep Black Forest",
        faction="Faerie court",
        realm="Faerie",
        ruler="The King of the Black Mountain",
        place=forest,
        wants="An end to all human intrusion into the deep forest.",
        summary=(
            "The most malign faeries of the Black Forest haunt its deepest parts, "
            "furthest from people; many are shapeless or formless, embodying "
            "darkness, fear and malice, and they are the cause of the panic "
            "mortals feel in wild places. Several dark courts exist, all under the "
            "King of the Black Mountain. Dankmar deals with them carefully; "
            "Durenmar has known nothing of them since the Hercynian lineage was "
            "exiled."
        ),
    )


# -- threats --


def _threats(b: Builder, w, valley, forest, central) -> None:
    w["schwall"] = b.threat(
        "Schwall of Bjornaer and the Rhine elemental",
        antagonist="Schwall of Bjornaer",
        realm="Magic",
        place=valley,
        summary=secrets(
            "An elderly Bjornaer of the Hawthorn Gild, once of Rheinstein, lives "
            "alone at the Rhinefalls. Odd disturbances of the river would be the "
            "first sign that something is wrong.",
            "Schwall, a powerful Wilderist hidden in the Rhinefalls regio, means to "
            "release the imprisoned spirit of the Rhine and merge with it to cheat "
            "Final Twilight. The floods would devastate shipping, towns and cities "
            "the length of the river, a breach of the Code the Tribunal would "
            "answer with a Wizard's March. Magi may hinder him or help him.",
        ),
        stages=[
            Builder.stage(
                "Disturbances on the river",
                at=1,
                clues="Unexplained surges, eddies and floods along the Rhine.",
                ignored="Schwall's preparations go on unseen in the regio.",
                stopped="A search of the Rhinefalls regio finds the old magus.",
            ),
            Builder.stage(
                "The elemental released",
                at=2,
                clues="The falls change; the river rises out of season.",
                ignored=(
                    "Floods devastate shipping, towns and cities down the whole "
                    "Rhine; the Tribunal calls a March."
                ),
                stopped="The spirit stays bound and Schwall faces his Twilight.",
                turned="Magi who help him share in whatever he becomes.",
            ),
        ],
    )
    w["forest_spirits_wrath"] = b.threat(
        "The forest spirits' wrath",
        antagonist="A forest's genius locus",
        realm="Magic",
        summary=(
            "Wholesale or repeated magical harm to a forest draws the attention of "
            "its spirit. It can grant Flaws, possess, shroud a place, drown a "
            "region in grown undergrowth, turn the weather or drive beasts as "
            "puppets, and its Might of 30 or more resists the magic used against "
            "it."
        ),
        stages=[
            Builder.stage(
                "The spirit takes notice",
                at=1,
                clues="Beasts watch the offenders; paths close; the weather turns.",
                ignored="The spirit acts against the covenant.",
                stopped="Amends made to the forest, and the harm not repeated.",
            ),
            Builder.stage(
                "Reprisal",
                at=2,
                ignored=(
                    "Flaws granted, people possessed, the covenant shrouded or "
                    "swallowed in undergrowth, storms and driven beasts."
                ),
            ),
        ],
    )
    w["walking_the_paths"] = b.threat(
        "Walking the paths",
        realm="Magic",
        summary=(
            "Hermetic training does not cover the primal power of the forest. "
            "Those who walk its paths are scarred in body and mind, take permanent "
            "Flaws as sacrifices, and often lose their way or are never seen "
            "again; a regio of stasis can swallow decades, as when Alexander of "
            "Jerbiton came back too late for his mater. The paths may explain the "
            "Rhine's long record of magi who quietly vanish or retire."
        ),
    )
    w["malicious_woodland_spirits"] = b.threat(
        "Malicious woodland spirits",
        realm="Faerie",
        summary=(
            "The Baumesel, the ass of the trees, and the bockman of the Black "
            "Forest attack lone travellers; the Eschenfrau, the wife of the ash, is "
            "very evil to her neighbours and must be appeased with a sacrifice on "
            "Ash Wednesday. The book gives no realm or Might for these three."
        ),
    )
    w["pulch"] = b.threat(
        "Pulch of Merinita",
        antagonist="Pulch of Merinita",
        realm="Magic",
        place=central,
        summary=secrets(
            "The folk of Thuringia take Pulch, who haunts the Kammerforst and "
            "punishes wood-thieves and those who harm the trees, for a spirit of "
            "the forest.",
            "He is a Merinita magus skirting the edge of the Code; Quaesitores may "
            "send characters to bring him to account.",
        ),
    )
    w["wild_hunt_and_holzfrau"] = b.threat(
        "The Wild Hunt and the Holzfrau",
        antagonist="The local wood-wife and the Wild Hunt",
        realm="Faerie",
        summary=(
            "A covenant in a wilderness, above all in a Faerie aura, may stand on "
            "the spot where the local wood-wife has always hidden from the Hunt. "
            "Every autumn she tries to get in, and on stormy winter nights the "
            "Wild Hunt assaults the covenant."
        ),
        stages=[
            Builder.stage(
                "The wood-wife comes",
                at=1,
                clues="In autumn a Holzfrau of Might 20 seeks a way inside the covenant.",
                ignored="She is kept out and the Hunt finds her in the open.",
                turned="Sheltered, she repays the kindness; the Hunt comes looking.",
            ),
            Builder.stage(
                "The Wild Hunt",
                at=2,
                clues="Storms on winter nights, and horns in the wind.",
                ignored="The Hunt assaults the covenant.",
            ),
        ],
    )
    w["pogroms"] = b.threat(
        "Pogroms",
        place=valley,
        summary=(
            "Every announcement of a crusade sets off massacres of the Jews in the "
            "Rhine cities, as in 1096 at Speyer, Worms, Mainz, Cologne and Trier "
            "and again around 1147. Only the bishops hanging the ringleaders brings "
            "them to a stop."
        ),
        stages=[
            Builder.stage(
                "A crusade is preached",
                at=1,
                clues="Preachers and crusader bands gather in the Rhine cities.",
                ignored="Mobs turn on the Jewish quarters.",
            ),
            Builder.stage(
                "Massacre",
                at=2,
                ignored="The Jewish quarters are sacked and their people killed.",
                stopped="The bishop hangs the ringleaders and the killing ends.",
            ),
        ],
    )
    w["verduns_underworld"] = b.threat(
        "Verdun's underworld",
        place=valley,
        summary=(
            "In Verdun, a declining border city, spies and assassins can be hired "
            "to work in French or German lands by whoever pays."
        ),
    )
    w["destruction_of_st_georgen"] = b.threat(
        "The destruction of St Georgen",
        antagonist="The wilderness of the Black Forest; Dankmar suspected",
        moves="Fixed dates",
        position=2,
        realm="Faerie",
        place=forest,
        summary=secrets(
            paragraphs(
                "The Benedictine monastery of St Georgen, founded in 1084 as a small "
                "daughter house of Hirsau, was the Dominion's deepest incursion into "
                "the Black Forest and so the greatest threat to its ancient power; "
                "its bell was carried off to the Seven Waterfalls. The wilderness "
                "attacked it again and again, it was abandoned more than once and "
                "always refounded. In 1208 travellers found its buildings and fields "
                "in ruin, overgrown with strange dark vines in which the twisted "
                "bodies of the monks hung, their faces frozen in horror.",
                "The Order suspected Dankmar. The matter was raised at the Tribunal "
                "of 1214, where Jiphella, Dankmar's only delegate, denied it; the "
                "deed would be lawful in the letter under the Guardians of the "
                "Forests ruling, though the Tribunal would never openly approve, and "
                "with no mundane witnesses there was no breach of the Code. A close "
                "vote refused an investigation.",
            ),
            "Dankmar's part in the destruction is suspected; the book does not "
            "state it as fact.",
        ),
        stages=[
            Builder.stage(
                "The monks found dead",
                year=1208,
                clues="Travellers find St Georgen in ruin, its monks hanging in dark vines.",
                ignored="The Order suspects Dankmar; the house is not refounded.",
            ),
            Builder.stage(
                "The Tribunal declines to investigate",
                year=1214,
                clues="Jiphella denies Dankmar's involvement; the vote is close.",
                ignored="The suspicion stays unanswered and the forest's power grows.",
                turned="A new case brought at the next Tribunal reopens the question.",
            ),
        ],
    )
    w["king_of_the_black_mountains_attacks"] = b.threat(
        "Monastery attacks by the King of the Black Mountain",
        antagonist="The King of the Black Mountain",
        realm="Faerie",
        place=forest,
        summary=(
            "The other monasteries of the Black Forest that lie inside the King of "
            "the Black Mountain's domain suffer sinister attacks and unexplained "
            "accidents: monks vanish, crops are blighted, and landslides and "
            "earthquakes strike. Hirsau alone is largely immune."
        ),
    )
