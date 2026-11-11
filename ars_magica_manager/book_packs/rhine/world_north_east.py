"""The mundane and supernatural world of the north, centre and east of
the Rhine Tribunal (Guardians of the Forests chapters 7 to 10): the
Hanseatic and Saxon towns and their lords and churches, Thuringia,
Franconia and Bavaria north of the Danube, the Eastern Marches and
Bohemia, with the factions and threats that move among them. Each real
entity is made once; the west module makes the Welfs, the emperor, the
count palatine and the Rhineland archbishops, and this module links to
those records by key where it finds them.

Everything here is a paraphrase of the notes on the book, not its words."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...arms import Arms
from ...models import Neighbour
from ..builder import titled

if TYPE_CHECKING:
    from . import Rhine


def _place(rhine: Rhine, *keys: str) -> Neighbour | None:
    """The first of the places another part made under `keys`."""
    for key in keys:
        found = rhine.places.get(key)
        if found is not None:
            return found
    return None


def _world(rhine: Rhine, *keys: str) -> Neighbour | None:
    """The first of the world records another part made under `keys`."""
    for key in keys:
        found = rhine.world.get(key)
        if found is not None:
            return found
    return None


def build(rhine: Rhine) -> None:
    _lowlands(rhine)
    _central(rhine)
    _east(rhine)
    _bohemia(rhine)
    _factions(rhine)
    _threats(rhine)


# -- the Lowlands (chapter 7) --


def _lowlands(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    lowlands = _place(rhine, "lowlands")
    welfs = _world(rhine, "welfs", "henry_the_lion", "welf")
    emperor = _world(rhine, "emperor", "frederick_ii", "holy_roman_emperor")

    # Lords of the north.
    w["valdemar_ii"] = b.lord(
        "Valdemar II of Denmark",
        title="duke",
        wealth="Wealthy",
        seat="Roskilde",
        place=lowlands,
        arms=Arms("Or", charge="Lion", charge_tincture="Azure", count=3),
        summary=(
            "King of Denmark, called the Victorious, and the overlord of the whole "
            "northern coast of the Tribunal. He took Holstein in 1201 and occupied "
            "Hamburg in 1216, and in 1214 Frederick II formally recognised his hold "
            "on Holstein and Pomerania in return for Danish support of his claim to "
            "the Empire. His father Valdemar I conquered Rügen in 1168 after secretly "
            "climbing the Königstuhl, and burnt Rostock in 1161 to drive out the "
            "pagans; it is not known whether the son has made the climb. Prince "
            "Mestwin of Pomerania has sworn allegiance to him, and he keeps an uneasy "
            "alliance with the Knights of the Sword. The coastal towns chafe under "
            "him and want Free Imperial City status; if history holds, Adolf IV of "
            "Holstein defeats him in 1227 and Holstein and Pomerania return to the "
            "Empire."
        ),
    )
    w["erich_holstein"] = b.lord(
        "Duke Erich of Holstein",
        title="duke",
        seat="Holstein",
        answers_to=w["valdemar_ii"],
        place=lowlands,
        summary=(
            "A Dane of the house of Sven Estridson who governs Holstein as duke on "
            "behalf of King Valdemar II. Lübeck, Hamburg and Nortorf lie in his "
            "charge."
        ),
    )
    w["saxony_duke"] = b.lord(
        "Albert I, Duke of Saxony",
        title="duke",
        seat="Saxony",
        place=lowlands,
        summary=(
            "The present duke of Saxony, of the Ascanian line descended from Albert "
            "the Bear, the rival of Henry the Lion who profited most when the great "
            "Welf fell. The Welfs remain the ancestral house of Saxony and the chief "
            "rivals of the ruling Hohenstaufen, so the duke's title sits uneasily on "
            "lands whose towns still remember Henry."
        ),
    )
    w["mecklenburg_princes"] = b.lord(
        "The Princes of Mecklenburg",
        title="count",
        wealth="Poor",
        seat="Mecklenburg castle",
        place=lowlands,
        summary="A Sorbian dynasty named for their castle between Lübeck and Rostock, a "
        "little inland north of Schwerin, who rule Rostock. The family and the "
        "region once worshipped Radegast, until Valdemar I burnt Rostock in 1161 "
        "and drove the pagans into the countryside. They have since accepted "
        "Christianity and sworn to the emperor, hoping to win back their "
        "ancestral lands.",
        secrets=[
            titled(
                "The Mecklenburgs and Radegast",
                "The Mecklenburgs still secretly worship Radegast and have gained "
                "unnatural powers from him.",
            ),
            titled(
                "A prophet of Radegast",
                "Imanitos Mendax of Oculus Septentrionalis has lately appeared to the "
                "Mecklenburgs as a prophet of Radegast.",
            ),
        ],
    )

    # Churches of the north.
    w["archbishop_of_bremen"] = b.church(
        "Archbishop Gerhard II of Bremen",
        church="Archbishop's cathedral",
        order="secular clergy",
        ruler="Archbishop Gerhard II",
        place=lowlands,
        summary=(
            "The oldest Saxon bishopric, founded in the eighth century when "
            "Charlemagne sent the missionary Willehad to the Saxons; the first church "
            "rose in 789 and a sizeable cathedral stands there now. The see moved "
            "here from Hamburg after the Wendish raids. St Ansgar, the Apostle of the "
            "North, lies buried here since 865. Archbishop Gerhard II contends with "
            "Bremen's independent-minded merchants for control of the city."
        ),
    )
    w["corvey"] = b.church(
        "Abbey of Corvey",
        church="Monastery or nunnery",
        order="Benedictine",
        place=lowlands,
        summary=(
            "A great scholarly abbey near Höxter, twenty miles east of Paderborn, "
            "where in the tenth century the monk Widukind wrote his history of the "
            "Saxons."
        ),
    )
    w["magdeburg_archbishop"] = b.church(
        "Archbishopric of Magdeburg",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=lowlands,
        summary=(
            "Otto the Great founded a Benedictine monastery and the cathedral at "
            "Magdeburg and raised it to an archbishopric in 962. It has been the "
            "centre of missionary work and Church authority over the Eastern Marches "
            "ever since."
        ),
    )
    w["munster_cathedral"] = b.church(
        "Cathedral of St Liudger, Münster",
        church="Bishop's cathedral",
        order="secular clergy",
        place=lowlands,
        summary=(
            "Founded in 805 as a monastery, from which the city takes its name, to "
            "serve as a base for converting the Saxons. The cathedral is dedicated to "
            "St Liudger, its first bishop."
        ),
    )
    w["quedlinburg_abbey"] = b.church(
        "Collegiate foundation of Quedlinburg",
        church="Monastery or nunnery",
        place=lowlands,
        summary=(
            "A foundation for noblewomen established by Mathilde, widow of Henry the "
            "Fowler. Its abbesses have ruled the town of Quedlinburg since."
        ),
    )

    # Towns of Holstein and the Baltic coast.
    w["schleswig"] = b.town(
        "Schleswig",
        charter="Noble lord",
        ruler="Valdemar II of Denmark",
        answers_to=w["valdemar_ii"],
        place=lowlands,
        summary=(
            "A fishing town on the north side of the Schlei fjord, grown up some two "
            "hundred years after the Vikings' Haithabu beside a Benedictine cloister "
            "of St Johannis. The earth ramparts and burial mounds of Haithabu, where "
            "the land crossing between the Baltic and the North Sea is shortest, lie "
            "a few miles off, and locals say its ghosts remain."
        ),
    )
    w["hamburg"] = b.town(
        "Hamburg",
        charter="Commune",
        ruler="Valdemar II of Denmark",
        answers_to=w["valdemar_ii"],
        place=lowlands,
        arms=Arms("Gules", charge="Tower", charge_tincture="Argent"),
        summary=(
            "A sizeable trading city on the Elbe estuary, founded early in the ninth "
            "century, destroyed by a Viking fleet in 845, burnt by the Poles in 1030 "
            "and raided twice by the Wends, after which its archbishop moved his see "
            "to Bremen. Frederick Barbarossa freed it of tax and customs on sea and "
            "river goods in 1189 and made it a Free Imperial City, but Valdemar II "
            "occupied it in 1216 and it now owes allegiance to Denmark. It controls "
            "the Lüneburg salt that Lübeck needs for its herring. If history holds, "
            "its free status returns in 1227."
        ),
    )
    w["nortorf"] = b.town(
        "Nortorf",
        answers_to=w["erich_holstein"],
        place=lowlands,
        summary=(
            "A small Holstein town where the roads to Schleswig, Lübeck and Hamburg "
            "meet. Unremarkable but for the small ash in its churchyard, cut down "
            "every New Year's Night by a white rider while a black rider fails to "
            "stop him."
        ),
    )
    w["lubeck"] = b.town(
        "Lübeck",
        charter="Commune",
        ruler="Valdemar II of Denmark",
        answers_to=w["valdemar_ii"],
        place=lowlands,
        arms=Arms("Argent", division="Per fess", second="Gules"),
        summary=(
            "Germany's most important coastal port and one of its richest cities, "
            "the hub of Baltic trade, set on an oval island at the mouth of the Trave "
            "ringed by moat canals. Henry the Lion founded it in effect in 1157, "
            "built the harbour, made it a bishopric and granted the Statutes of "
            "Lübeck: self-rule by a merchants' council under an Älderman with its own "
            "justice, whose taxes pay for proud civic works, including a great brick "
            "cathedral at the south tip due within a decade. Furs, leather, timber, "
            "amber and iron ore come in; salt, spices, grain, herring, cloth and "
            "metalware go out, and a large fleet fishes off Scania under a profitable "
            "herring monopoly. Its merchants have kept a trading counter in Novgorod "
            "since 1205. The city has an ordinary Divine aura and is the home of "
            "Oculus Septentrionalis, of the Goldenes Kalb tavern and of the Novgorod "
            "Inn at the north end of town. Under Danish rule until 1227, when it is "
            "expected to become a Free Imperial City and, in time, the leading city "
            "of the Hanseatic League."
        ),
    )
    w["rostock"] = b.town(
        "Rostock",
        charter="Noble lord",
        ruler="The Princes of Mecklenburg",
        answers_to=w["mecklenburg_princes"],
        place=lowlands,
        summary="A growing Baltic port in Mecklenburg, overshadowed by Lübeck, and the "
        "chief town of the Sorbian princes of Mecklenburg. Valdemar I burnt it in "
        "1161 and drove its Radegast-worshippers into the countryside, and it is "
        "now mostly German.",
        secrets=[
            titled(
                "The Mecklenburgs' worship",
                "The Mecklenburg family still worship Radegast in secret.",
            ),
            titled(
                "Storyguide Notes",
                "See the Princes of Mecklenburg's record and the Cult of Radegast.",
            ),
        ],
    )

    # Towns of Saxony and Westphalia.
    w["munster"] = b.town(
        "Münster",
        charter="Church",
        answers_to=w["munster_cathedral"],
        place=lowlands,
        summary=(
            "A prosperous market city at the centre of the flat, highly fertile "
            "Münsterland in Westphalia. It grew from the monastery founded in 805 as "
            "a base for converting the Saxons, and its cathedral is St Liudger's."
        ),
    )
    w["dortmund"] = b.town(
        "Dortmund",
        place=lowlands,
        summary=(
            "A Westphalian town known among those who know of such things as the "
            "principal seat of the Holy Vehm, the secret courts of the north."
        ),
    )
    w["paderborn"] = b.town(
        "Paderborn",
        place=lowlands,
        summary=(
            "A Saxon town built round hundreds of tiny warm springs that form the "
            "source of the little River Pader. Here in 799 Charlemagne met Pope Leo "
            "III and the founding of the Holy Roman Empire was agreed; Charlemagne "
            "began a lofty cathedral and a palace for it, and the palace is now a "
            "ruin after fires in 1000 and 1165. The Externsteine stand on the edge of "
            "the Teutoburger Forest nearby, and the abbey of Corvey lies twenty miles "
            "east."
        ),
    )
    w["bremen"] = b.town(
        "Bremen",
        charter="Church",
        ruler="Archbishop Gerhard II",
        answers_to=w["archbishop_of_bremen"],
        place=lowlands,
        arms=Arms("Gules", charge="Key", charge_tincture="Argent"),
        summary=(
            "A port on the north bank of the Weser and the oldest Saxon bishopric, "
            "its first church built in 789 after Charlemagne sent Willehad to the "
            "Saxons; the see came here from Hamburg. The market traders have long "
            "held independent rights, and Archbishop Gerhard II contends with them "
            "for control of the city. The cursed, misted peat waste of the "
            "Teufelsmoor lies to the north-east."
        ),
    )
    w["luneburg"] = b.town(
        "Lüneburg",
        answers_to=welfs or w["saxony_duke"],
        place=lowlands,
        summary=(
            "A Saxon town built over extensive salt mines that have made it very "
            "rich, with grand brick buildings, though subsidence tilts the houses "
            "over rickety streets, and a planned great brick cathedral is of doubtful "
            "wisdom. Its salt goes out through Hamburg. The open Lüneburg Heath, "
            "where shepherds keep the goat-like Heidschnucken, lies to the south."
        ),
    )
    w["hildesheim"] = b.town(
        "Hildesheim",
        charter="Church",
        place=lowlands,
        summary=(
            "Called the jewel of northern Germany. In 815 Louis the Pious hung relics "
            "of the Virgin on a rosebush while hunting; they could not be removed, so "
            "he founded a church, and the rosebush still grows in a cloister by the "
            "cathedral. St Bernward, bishop early in the eleventh century and adviser "
            "to Otto II, established the Romanesque style here and left magnificent "
            "churches and civic buildings, artists and architects. The greatest "
            "church is St Michael on its own hill north of the cathedral, with six "
            "towers, many relics and paintings, and Bernward's crypt."
        ),
    )
    w["brunswick"] = b.town(
        "Brunswick",
        charter="Noble lord",
        answers_to=welfs,
        place=lowlands,
        summary=(
            "Henry the Lion's residence in the twelfth century, adorned with art and "
            "monuments: the bronze Burglöwe lion stands in the central square, the "
            "fortress-like cathedral begun in 1173 is now complete and rich, in a "
            "style other Welf churches have copied, and beside it is Henry's fortress "
            "Burg Dankwarderode, named for the city's heroic founder."
        ),
    )
    w["goslar"] = b.town(
        "Goslar",
        charter="Commune",
        answers_to=emperor,
        place=lowlands,
        summary=(
            "A Free Imperial City on the northern edge of the Harz, famed for the "
            "Rammelsberg silver mines, Germany's largest and a prized imperial asset, "
            "now slowly flooding because spiteful gnomes have turned an underground "
            "river into them. Henry the Lion's claim to these mines led Barbarossa to "
            "strip him of his estates. Whoever drains the mines would be richly "
            "rewarded by the emperor."
        ),
    )
    w["quedlinburg"] = b.town(
        "Quedlinburg",
        charter="Church",
        answers_to=w["quedlinburg_abbey"],
        place=lowlands,
        summary=(
            "Henry the Fowler's effective capital for a generation early in the tenth "
            "century, with a castle on the Burgberg at the south end and a palace "
            "that has hosted Imperial Diets. The abbesses of the foundation for "
            "noblewomen that his widow Mathilde established have ruled the town "
            "since. It is now overshadowed by the greater Saxon cities."
        ),
    )
    w["magdeburg"] = b.town(
        "Magdeburg",
        charter="Church",
        answers_to=w["magdeburg_archbishop"],
        place=lowlands,
        summary=(
            "Otto the Great's favoured city on the west bank of the Elbe, an "
            "archbishopric since 962 and the centre of Church authority over the "
            "Eastern Marches. The Magdeburg Law, with its generous charters and quick "
            "local courts, encourages new settlements in the east. The forgotten "
            "stone circle of the Teufelsküche lies deep in the Haldensleben Forest to "
            "the north-west."
        ),
    )


# -- Central Germany (chapters 7 and 8) --


def _central(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    central = _place(rhine, "central")
    emperor = _world(rhine, "emperor", "frederick_ii", "holy_roman_emperor")
    mainz = _world(rhine, "archbishop_of_mainz")

    # Lords.
    w["thuringia_landgrave"] = b.lord(
        "Louis IV, Landgrave of Thuringia",
        title="duke",
        wealth="Wealthy",
        seat="The Wartburg",
        place=central,
        arms=Arms("Azure", charge="Lion", charge_tincture="Argent"),
        summary=(
            "Louis IV, called the Pious, is landgrave of Thuringia, seated at the "
            "Wartburg near Eisenach, the ancestral castle founded in 1067 by Count "
            "Louis I and never breached. His father Hermann I, who ruled from 1190 to "
            "1217, made it a famous court of literature and music on the French "
            "model, with lavish festivals and travelling minnesänger. Louis is to "
            "marry Elisabeth, daughter of the king of Hungary, who was raised amid "
            "the Wartburg's splendour and finds it empty, giving herself in secret "
            "to the poor and sick; stopped once with bread for beggars in her apron, "
            "she opened it to show roses. If history holds, Louis dies in 1227, "
            "Elisabeth founds a hospice at Marburg, dies in 1231 and is canonised in "
            "1235, and the Teutonic Knights raise a great church over her hospice."
        ),
    )

    # Churches.
    w["hersfeld_abbey"] = b.church(
        "Imperial Abbey of Hersfeld",
        church="Monastery or nunnery",
        order="Benedictine",
        place=central,
        summary=(
            "One of the largest and most important abbeys in Germany, founded in the "
            "eighth century by Lullus, archbishop of Mainz. The springs it was built "
            "round are known for restorative powers of a magical kind; they and the "
            "giant bell in the Katharinenturm are both named for Lullus. Its rival "
            "Fulda lies forty miles south."
        ),
    )
    w["fulda_abbey"] = b.church(
        "Abbey of Fulda",
        church="Monastery or nunnery",
        order="Benedictine",
        place=central,
        summary=(
            "The huge and wealthy monastery that holds the grave of St Boniface, the "
            "martyred English monk, and so a major place of pilgrimage. The "
            "Michaelskirche at the town's centre copies the Holy Sepulchre as a Greek "
            "cross, and four monastic churches outside the town at the compass "
            "points form a giant cross; the eastern one, the Peterskirche on its "
            "hill, holds the crypt of St Lioba, Boniface's kinswoman. It rivals "
            "Hersfeld."
        ),
    )
    w["bishop_of_wurzburg"] = b.church(
        "Bishop of Würzburg",
        church="Bishop's cathedral",
        order="secular clergy",
        place=central,
        summary=(
            "A bishopric since the eighth century. The cathedral holds the shrine of "
            "St Kilian, the seventh-century Irish missionary and martyr who first "
            "brought the faith here and is popularly the patron of wine, for the "
            "bishop is master of Franconia's largest vineyards. He has begun a huge "
            "rectangular fortress on the Marienberg across the Main as his future "
            "residence."
        ),
    )
    w["bamberg_cathedral"] = b.church(
        "Cathedral of Bamberg",
        church="Bishop's cathedral",
        order="secular clergy",
        founded=1007,
        place=central,
        summary=(
            "Emperor Henry II made Bamberg a bishopric in 1007 and founded the "
            "cathedral on the chief of its seven hills, where he is buried."
        ),
    )
    w["erfurt_petersberg"] = b.church(
        "Abbey of the Petersberg, Erfurt",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=mainz,
        place=central,
        summary=(
            "The Benedictine abbey on Erfurt's Petersberg, where Barbarossa often "
            "held court. Erfurt's other hill, the Domhügel, carries the eighth-century "
            "Marienkirche."
        ),
    )

    # Towns of Thuringia and Hesse.
    w["eisenach"] = b.town(
        "Eisenach",
        charter="Noble lord",
        ruler="Louis IV of Thuringia",
        answers_to=w["thuringia_landgrave"],
        place=central,
        summary=(
            "The town beneath the Wartburg, the landgraves' never-breached castle. "
            "Under Hermann I the castle became a centre of poetry and song; at the "
            "Sängerkrieg of 1204 Walther von der Vogelweide beat every rival, Wolfram "
            "von Eschenbach and Henry von Ofterdingen among them. Walther then wrote "
            "for Philip of Swabia and for Otto of Brunswick, helping the latter to "
            "the throne by 1209. The fashionable epics are the Nibelungenlied, made "
            "for the court of Passau, Tristan und Isold, Parzival and the Gudrunlied, "
            "beside courtly verse of chaste devotion to an unattainable lady."
        ),
    )
    w["erfurt"] = b.town(
        "Erfurt",
        charter="Church",
        answers_to=mainz or w["erfurt_petersberg"],
        place=central,
        summary=(
            "Thuringia's oldest and largest town, held by the archbishops of Mainz, "
            "from which St Boniface set out to the Slavs. It rises on two hills: the "
            "Domhügel with the eighth-century Marienkirche and the Petersberg with "
            "its Benedictine abbey. Frederick II's court has visited four times "
            "between 1214 and 1220. Its wealth comes from exporting woad for blue "
            "dye."
        ),
    )
    w["naumburg"] = b.town(
        "Naumburg",
        charter="Church",
        place=central,
        summary=(
            "A well-fortified, scenic town high above the Saale in eastern Thuringia, "
            "originally the New Castle the Ekkehardinger counts built when they moved "
            "their seat across the river in the tenth century. It has its own bishop "
            "and a prosperous market, and has just begun a large cathedral of St "
            "Peter and St Paul. The young and secretive sculptor-architect known as "
            "the Master of Naumburg, German-born, French-trained and rumoured to owe "
            "his unmatched work to sorcery or divine inspiration, is expected to "
            "leave great works here, at Mainz and at Meissen."
        ),
    )
    w["hersfeld"] = b.town(
        "Hersfeld",
        charter="Church",
        answers_to=w["hersfeld_abbey"],
        place=central,
        summary=(
            "A town on the border of Thuringia and Hesse wholly dominated by its "
            "huge imperial abbey, whose springs are held to heal and whose giant "
            "bell hangs in the Katharinenturm."
        ),
    )
    w["fritzlar"] = b.town(
        "Fritzlar",
        place=central,
        summary=(
            "A Hessian town. A little to the north, near Züschen, stands the "
            "Riesenstein, the stone the Devil threw at the church-building villagers "
            "of Neueburg and wept bloody tears on; the hidden glade of the Donar Oak "
            "at Geismar lies somewhere in the wilderness nearby."
        ),
    )

    # Towns of Franconia.
    w["frankfurt"] = b.town(
        "Frankfurt",
        charter="Noble lord",
        population=10000,
        ruler="Emperor Frederick II",
        answers_to=emperor,
        place=central,
        arms=Arms("Gules", charge="Eagle", charge_tincture="Argent"),
        summary=(
            "A city of some ten thousand on the Main whose bridge is the gateway "
            "between north and south Germany. Charlemagne founded it in the eighth "
            "century after a fog-hidden ford, shown by deer, saved his retreating "
            "army from the Saxons, and built a fortress on the Römerberg over an "
            "older Roman site. After the Treaty of Verdun in 843 it was the capital "
            "of Louis the German, who founded St Saviour's in 852; it declined in the "
            "eleventh century, and the Hohenstaufen revived and fortified it, so that "
            "it now hosts imperial elections. The Römerberg square holds markets, "
            "fairs, tournaments and coronation festivals, and Italian banking houses "
            "keep offices here. In 1220 Frederick II holds here his last German Diet "
            "for fifteen years."
        ),
    )
    w["fulda"] = b.town(
        "Fulda",
        charter="Church",
        answers_to=w["fulda_abbey"],
        place=central,
        summary=(
            "The pilgrimage town of St Boniface's grave, in a long valley between the "
            "bright wooded Vogelsberg to the west and the impenetrable Rhön to the "
            "east, laid out as a giant cross of churches round its wealthy abbey."
        ),
    )
    w["wimpfen"] = b.town(
        "Wimpfen",
        charter="Noble lord",
        ruler="Emperor Frederick II",
        answers_to=emperor,
        place=central,
        summary=(
            "A favoured imperial residence high above the Neckar, held in turn by the "
            "Romans, the Franks and the bishops of Worms until Barbarossa took it in "
            "the twelfth century. The imperial palace stands where the Roman frontier "
            "fort had its temple of Mercury; the walls carry towers each of a "
            "different colour, the Roter Turm of red sandstone and the Blauer Turm of "
            "blue limestone among them. The bishop of Worms's administrator still "
            "lives in the grand Wormser Hof with much land and influence. The lower "
            "town clusters round the Stiftskirche and a Benedictine abbey by an "
            "ancient Neckar bridge, and the fertile wine hills of the Stromberg lie "
            "south."
        ),
    )
    w["neustadt_linden"] = b.town(
        "Neustadt an der grossen Linden",
        charter="Commune",
        place=central,
        summary=(
            "A free trading post in Franconia that has stayed a quiet backwater under "
            "its guardian lime tree, whose spirit has taken the townsfolk for its "
            "realm. The tree's siege-ruined branches rest on stone columns and "
            "monuments carved with the arms of the princes who fought there, and the "
            "townsfolk will not clear their woods. Prophecy says the town loses its "
            "freedom when the tree dies."
        ),
    )
    w["wurzburg"] = b.town(
        "Würzburg",
        charter="Church",
        ruler="The bishop of Würzburg",
        answers_to=w["bishop_of_wurzburg"],
        place=central,
        summary=(
            "An influential episcopal city of artists and scholars on the Main in "
            "central Franconia, amid the region's largest vineyards; wine is its "
            "export and St Kilian, whose shrine is in the cathedral, its patron. The "
            "bishop's new fortress rises on the Marienberg across the river. Peter "
            "von Würzburg of Fengheld takes his name from here."
        ),
    )
    w["bamberg"] = b.town(
        "Bamberg",
        charter="Church",
        answers_to=w["bamberg_cathedral"],
        place=central,
        summary=(
            "Henry II's city on seven hills, built from 1007 to rival Rome and far "
            "smaller, but keeping a spacious grandeur. Beer is its export: more than "
            "a dozen breweries, the oldest and largest of them the Bierhaus, older "
            "than the city and of legendary quality. East of it lie the weathered "
            "granite blocks of the Luisenburg and the empty Fichtelgebirge."
        ),
    )
    w["nuremberg"] = b.town(
        "Nuremberg",
        charter="Noble lord",
        ruler="Emperor Frederick II",
        answers_to=emperor,
        place=central,
        arms=Arms("Or", charge="Eagle", charge_tincture="Sable"),
        summary=(
            "Among Franconia's youngest cities yet arguably its most important, home "
            "to the Kaiserburg on its sandstone hill, an unofficial capital and the "
            "Empire's treasury, where by custom each new emperor holds his first "
            "Diet. Barbarossa and lately Frederick II have added wings and towers, "
            "and the upper level of the Kaiserkapelle is for the emperor alone. A "
            "crossroads trading city exporting linen, with many carpenters who make "
            "looms. The Harberg, with its wandering Drudenbaum, overlooks it."
        ),
    )
    w["regensburg"] = b.town(
        "Regensburg",
        place=central,
        summary=(
            "The principal city of the Danube in Bavaria. The Rhine Tribunal's "
            "Bavarian lands stop at the river; Regensburg, the other Danube cities "
            "and everything south of it are claimed by the Greater Alps Tribunal."
        ),
    )


# -- the Eastern Marches (chapter 9) --


def _east(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    east = _place(rhine, "east")

    # Lords.
    w["pomerania_duke"] = b.lord(
        "Mestwin I of Pomerania",
        title="duke",
        seat="Stettin",
        answers_to=w["valdemar_ii"],
        place=east,
        summary=(
            "Prince of Pomerania, a thinly peopled Slavic land between the Baltic and "
            "Poland that has been part of the Empire only since 1181, when Barbarossa "
            "made Bogislaw a duke. Mestwin rules under an oath of allegiance to "
            "Valdemar II of Denmark. He is old, with four sons; the eldest, "
            "Swantopolk, is expected to succeed him as duke. German settlers are "
            "arriving, the Church is weak here, and the Knights of the Sword found "
            "towns and monasteries and hunt pagan remnants in the forests."
        ),
    )
    w["brandenburg_margraves"] = b.lord(
        "Albert II, Margrave of Brandenburg",
        title="duke",
        seat="Brandenburg",
        place=east,
        arms=Arms("Argent", charge="Eagle", charge_tincture="Gules"),
        summary=(
            "Margrave of the low, forested march east of the Elbe that Albert the "
            "Bear, a Saxon, founded in 1150 after his campaigns against the Wends, "
            "and that his Ascanian descendants have ruled since. Its people are a "
            "thorough mix of Germans and Wends, and the forest is slowly being "
            "cleared for farms. Albert II is old; his heir is Otto, called the "
            "Pious."
        ),
    )
    w["meissen_margrave"] = b.lord(
        "Dietrich the Oppressed, Margrave of Meissen",
        title="duke",
        seat="The Burgberg of Meissen",
        place=east,
        arms=Arms("Or", charge="Lion", charge_tincture="Sable"),
        summary=(
            "Wettin margrave of Meissen, a dynasty ruling since 1089, who also rules "
            "the march of Lusatia. Meissen is the most civilised part of the Marches, "
            "rolling, moderately peopled, fully German and a political and "
            "ecclesiastical backwater; Lusatia is forest wilderness peopled only by "
            "Sorbs. No Hermetic covenant has stood in Meissen since Sirmium fell to "
            "the Magyars in the tenth century, and the vis sources the Order knew "
            "there perished with it."
        ),
    )

    # Churches.
    w["absalon"] = b.church(
        "Bishop Absalon of Roskilde",
        church="Bishop's cathedral",
        order="secular clergy",
        place=east,
        summary=(
            "The Danish bishop of Roskilde who rode with Valdemar I's invasion of "
            "Rügen in 1168 and in 1169 destroyed the fortress-temple of Arkona, the "
            "holiest site of the sun-god Svantovit. The Danish Church brought the "
            "faith to the island, where it is still new."
        ),
    )
    w["brandenburg_cathedral"] = b.church(
        "Cathedral of Brandenburg",
        church="Bishop's cathedral",
        order="secular clergy",
        founded=948,
        answers_to=w["brandenburg_margraves"],
        place=east,
        summary=(
            "The first bishopric east of the Elbe, founded in 948 by Otto the Great "
            "and briefly lost to a Slavic counter-attack later that century. Albert "
            "the Bear rebuilt the cathedral on the middle of Brandenburg's three "
            "islands."
        ),
    )
    w["bergen_marienkirche"] = b.church(
        "Marienkirche of Bergen",
        church="Parish church",
        place=east,
        summary=(
            "The church of Bergen, the only town on Rügen. With the Pfarrkirche at "
            "Altenkirchen it is one of the two churches of note on the island."
        ),
    )
    w["altenkirchen_church"] = b.church(
        "Pfarrkirche of Altenkirchen",
        church="Parish church",
        place=east,
        summary=(
            "One of Rügen's two churches of note, on the windswept northern peninsula "
            "of Wittow, where two last priests of Svantovit scrape a living."
        ),
    )
    w["rugen_cistercians"] = b.church(
        "Cistercian monastery of Rügen",
        church="Monastery or nunnery",
        order="Cistercian",
        place=east,
        summary=(
            "A monastery founded after the Danish conquest of 1168. Its monks have "
            "only just begun farming the Mönchgut peninsula, which takes its new name "
            "from them, and a church is planned at Sagard, five miles from Crintera, "
            "which would push the Dominion toward the covenant."
        ),
    )

    # Towns.
    w["bergen"] = b.town(
        "Bergen",
        charter="Noble lord",
        ruler="Valdemar II of Denmark",
        answers_to=w["valdemar_ii"],
        place=east,
        summary=(
            "The only town of any size on Rügen, founded by the Danes and ruled by "
            "them, with the Marienkirche. The islanders are mostly Slavic, "
            "Christianity is new, and the Danes have requisitioned every horse on "
            "the island."
        ),
    )
    w["stettin"] = b.town(
        "Stettin",
        charter="Noble lord",
        ruler="Mestwin I of Pomerania",
        answers_to=w["pomerania_duke"],
        place=east,
        summary=(
            "A small port on the Oder below an old Wendish fortress, the ancestral "
            "seat of the Pomeranian rulers. Germans have settled since the middle of "
            "the twelfth century and paid for the church of St Jakob, finished in "
            "1187."
        ),
    )
    w["brandenburg"] = b.town(
        "Brandenburg",
        charter="Noble lord",
        ruler="Albert II of Brandenburg",
        answers_to=w["brandenburg_margraves"],
        place=east,
        summary=(
            "The only notable city of the margravate east of the Elbe, on the site of "
            "an old Wendish settlement across three adjacent islands in the Havel; "
            "the middle island carries the cathedral Albert the Bear rebuilt."
        ),
    )
    w["meissen"] = b.town(
        "Meissen",
        charter="Noble lord",
        ruler="Dietrich of Meissen",
        answers_to=w["meissen_margrave"],
        place=east,
        summary=(
            "Seat of the margravate, on the left bank of the Elbe below the Burgberg, "
            "the stronghold Henry I founded in 929. A bishopric since 963, with a "
            "prosperous market where German merchants meet traders from Lusatia, "
            "Silesia and Poland, but not yet rich enough for a cathedral. Upstream "
            "the limestone pinnacles of the Bastei rise a thousand feet over the "
            "river."
        ),
    )
    w["freiberg"] = b.town(
        "Freiberg",
        answers_to=w["meissen_margrave"],
        place=east,
        summary=(
            "The largest of the new mining towns of the Ore Mountains, founded in "
            "1186 after silver and tin were found in that bleak evergreen range; a "
            "twelfth-century imperial decree lets anyone prospect there and keep the "
            "proceeds. Its merchants travel to Prague by the bridges at Most."
        ),
    )
    w["bautzen"] = b.town(
        "Bautzen",
        answers_to=w["meissen_margrave"],
        place=east,
        summary=(
            "The one place in Lusatia with real German influence, not far from "
            "Meissen. The Peace of Bautzen in 1018 ceded the area from Henry II to "
            "Boleslaus I of Poland, and it returned to the Empire in 1033. The "
            "Knights of the Sword keep a large fortification here where slaves, "
            "mostly Pomeranian, are held before being taken south to the market at "
            "Prague."
        ),
    )


# -- Bohemia and Moravia (chapter 10) --


def _bohemia(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    bohemia = _place(rhine, "bohemia")
    mainz = _world(rhine, "archbishop_of_mainz")

    w["otakar"] = b.lord(
        "King Otakar of Bohemia",
        title="duke",
        wealth="Wealthy",
        seat="Prague",
        place=bohemia,
        arms=Arms("Gules", charge="Lion", charge_tincture="Argent"),
        summary=(
            "Premyslid king of Bohemia, a semi-autonomous subject kingdom of the "
            "Empire that Barbarossa raised from a duchy a generation ago. His house "
            "has ruled since the eighth century, descended from the farmer Premysl "
            "whom the Gifted princess Libuse chose by vision at Vysehrad. The "
            "margrave of Moravia, the Empire's easternmost march on the Hungarian "
            "border, is usually the king's son or brother. Bohemia has no great "
            "cities, only modest towns round and north of Prague, living by farming, "
            "hunting, mining, glass, brewing and horses; many more towns are "
            "expected to be founded through the century as German feudal ways "
            "replace the Slavic chiefdoms."
        ),
    )

    w["st_vitus"] = b.church(
        "Basilica of St Vitus, Prague",
        church="Bishop's cathedral",
        order="secular clergy",
        founded=973,
        answers_to=mainz,
        place=bohemia,
        summary=(
            "The seat of the bishopric of Prague, created in 973 under Mainz with "
            "Thietmar of Merseburg as its first bishop. Inside the castle, it holds "
            "the shrine and grave of St Wenceslaus and relics of St Adalbert. The "
            "Basilica of St George, with its convent, stands beside it."
        ),
    )
    w["strahov"] = b.church(
        "Strahov monastery",
        church="Monastery or nunnery",
        order="Premonstratensian",
        founded=1140,
        place=bohemia,
        summary="An austere Premonstratensian house near Prague Castle, founded in 1140.",
    )
    w["sedlec"] = b.church(
        "Sedlec monastery",
        church="Monastery or nunnery",
        order="Cistercian",
        founded=1142,
        place=bohemia,
        summary=(
            "A Cistercian monastery a couple of dozen miles south-east of Prague, "
            "founded in 1142. A monk named Anton, napping after work in the vineyard, "
            "woke to find three rods of silver sprouting beside his head and left his "
            "frock, his kutna, to mark the spot; the monks have just opened a mine "
            "there of fantastically rich deposits. If history holds, a wealthy royal "
            "town grows up round it later in the century and takes Goslar's place as "
            "the Empire's chief source of silver. A far-sighted magus might buy the "
            "land for a trifle and mine it by magic, until Bohemian merchants notice "
            "prices rising and the Quaesitores take an interest."
        ),
    )

    w["prague"] = b.town(
        "Prague",
        charter="Noble lord",
        population=3000,
        ruler="King Otakar",
        answers_to=w["otakar"],
        place=bohemia,
        summary=(
            "Bohemia's chief settlement and the ancestral seat of its rulers, founded "
            "late in the ninth century on the Vltava at the land's centre; small by "
            "German standards at about three thousand people. Prague Castle on its "
            "hill over the west bank encloses the basilicas of St George and St "
            "Vitus, with Strahov monastery nearby, and a second castle stands on "
            "Vysehrad rock just south. Since the eleventh century the city has spread "
            "to the east bank, with a market run mostly by German merchants and a "
            "small Jewish quarter. It exports cheap glassware to northern Germany "
            "and holds a large slave market."
        ),
    )
    w["most"] = b.town(
        "Most",
        answers_to=w["otakar"],
        place=bohemia,
        summary=(
            "A town and market south of the Ore Mountains, grown up round the maze of "
            "wooden bridges over swampy ground that lets merchants pass between "
            "Freiberg and Prague; its name means Bridge."
        ),
    )
    w["brunn"] = b.town(
        "Brünn",
        charter="Noble lord",
        answers_to=w["otakar"],
        place=bohemia,
        summary=(
            "Seat of the Premyslid margraves of Moravia, where a castle and the "
            "church of St Michael were founded on Petrov Hill early in the eleventh "
            "century at the meeting of the Svitava and Svratka; a market town and "
            "mines have grown round them, and a handful of German settlers have "
            "lately arrived. In the town hall hangs the stuffed carcass of the Dragon "
            "of Brünn, which generations ago ate townsfolk from a cave by the "
            "Svratka until a travelling butcher fed it an ox hide sewn full of "
            "unslaked lime; it drank from the river and burst. Whether he was a "
            "butcher, a wizard or a magus in disguise nobody knows."
        ),
    )


# -- factions --


def _factions(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    lowlands = _place(rhine, "lowlands")
    central = _place(rhine, "central")
    east = _place(rhine, "east")
    bohemia = _place(rhine, "bohemia")

    w["hansa"] = b.faction(
        "The Hansas",
        faction="Gild",
        place=lowlands,
        wants="Protection from robbers and pirates; agreed prices; justice for their burgesses abroad",
        offers="Mutual protection, settlement of disputes and price agreements among member merchants",
        summary=(
            "Associations of merchants for mutual protection, the settling of "
            "disputes and agreed prices, which have existed since at least the "
            "twelfth century but remain small. If history holds, a treaty between "
            "Lübeck and Hamburg in 1241, sharing the cost of guarding the Trave and "
            "Elbe against robbers and punishing crimes against each other's "
            "burgesses, becomes the first great one; scores of German and Baltic "
            "cities join over the following decades, and by 1300 the League is rich "
            "and powerful under Lübeck's lead, fighting pirates with bigger ships, "
            "convoys, hired armies and noble allies. Whether Oculus Septentrionalis "
            "stands at its heart, and whether Imanitos Mendax plants corruption "
            "there, is for the storyguide."
        ),
    )
    w["holy_vehm"] = b.faction(
        "The Holy Vehm",
        faction="Council or assembly",
        place=lowlands,
        ruler="The archbishop of Cologne, as Oberststuhlherr",
        rules=(
            "Members swear to uphold the Vehm, keep its secrets even from kin and "
            "report everything; each receives a rope and a knife marked SSGG. Courts "
            "sit on a hillock or known spot, lately also in vast underground "
            "chambers, and intruders are killed. An accused who does not appear is "
            "condemned if the accuser brings seven character witnesses, without the "
            "charge being examined; one who appears needs twenty-one to be "
            "acquitted; a member clears himself by oath unless charged with "
            "betraying the Vehm. Women, children, Jews, heathens and in practice "
            "nobles are exempt."
        ),
        wants="The Blutbann, the power of life and death, which it says the nobility has usurped",
        offers="Judgement on heresy, witchcraft, perjury, murder and sacrilege where the lords will not act",
        summary="A system of secret courts, mainly in northern Germany and seated at "
        "Dortmund, claiming the power of life and death from an imperial mandate "
        "of Charlemagne. Its members, the Wissende, number tens of thousands: any "
        "free, legitimately born man who is neither excommunicate nor outlaw may "
        "be initiated. It works by secret meetings, kidnappings by night, hostile "
        "trials and in some regions torture, and passes one sentence, hanging in "
        "a public place with an SSGG knife left by the corpse. Its officers are "
        "the Stuhlherr, usually the local secular or church lord; the Freigraf, "
        "appointed for life, who truly rules the court; the Freischöffen who "
        "accuse and decide; the Fronboten who execute; and the Fehmenotes, "
        "secret informants across the Empire. Its supreme head is the archbishop "
        "of Cologne. Philippus Niger of Durenmar has assured House Guernicus that "
        "it poses no danger to the Order.",
        secrets=[
            titled(
                "Philippus Niger's men in the Vehm",
                "Philippus Niger uses the Vehm: two of his trusted men are Freigrafs "
                "and he knows more than twenty Fehmenotes.",
            ),
            titled(
                "The Vehm's hangings",
                "Philippus Niger has had dozens of suspected hedge wizards and at "
                "least one Marched magus hanged by the Vehm's courts, and is "
                "spreading it southward as a weapon against hedge wizards.",
            ),
            titled(
                "Philippus Niger's assurance",
                "Philippus Niger has no grounds for his assurance to House Guernicus.",
            ),
        ],
    )
    w["harz_witches"] = b.faction(
        "The Witches of the Harz",
        tradition="trad_folk_witches",
        faction="Hedge coven",
        realm="Faerie",
        place=central,
        rules="Council at the Hexentanzplatz each April; only the strongest approach the Witches' Altar",
        wants="To venerate Walpurga and keep the old ways of the villages",
        offers="Potions, charms and the goddess's favour; a place where magi find apprentices",
        summary=(
            "Cunning-folk who venerate Walpurga as a goddess and keep the old ways "
            "with dozens of traditional villagers. They hold council on the "
            "Hexentanzplatz crag every April and go on to the Brocken on Walpurgis "
            "Night, 30 April, to light fires and sing to forgotten gods while "
            "Walpurga calls up the spirits of summer against winter's; only the most "
            "powerful may approach the Witches' Altar at the summit. Their design is "
            "left to the storyguide, as folk with minor powers of potion and charm; "
            "they can never cast true spells or work major magic, or the Order would "
            "long since have absorbed or destroyed them. Magi know the gatherings as "
            "a good place to find a potential apprentice."
        ),
    )
    w["woden_priesthood"] = b.faction(
        "Priesthood of Woden",
        faction="Hedge coven",
        place=lowlands,
        summary=(
            "Tall red-bearded priests in long white cloaks who once came to the "
            "forgotten stone circle of the Teufelsküche, deep in the Haldensleben "
            "Forest north-west of Magdeburg, in the hour before dawn with men in "
            "skins and darker shapes, to slaughter a sacrifice and burn its vitals to "
            "herald the day. The missionaries who purged the cult named the place "
            "the Devil's Kitchen. Whether any of the priests survive is for the "
            "storyguide; the Wild Hunt rises from the same stones."
        ),
    )
    w["cult_of_radegast"] = b.faction(
        "Cult of Radegast",
        faction="Faith or sect",
        place=east,
        ruler="Igor Rastvan of Roznov, high priest",
        wants="A kingdom of the Slavs united under Radegast",
        offers="Temporal influence at pagan courts; the god's favour to the inspired and the overconfident",
        summary="The worship of Radegast, the Slavic god of chieftainship and war, and "
        "also of fertility and harvest. His worship was anciently centred in "
        "Pomerania at his Oracle in the fortress-temple of Rethra, now ruined and "
        "plundered, though Mount Radhost in Moravia was always his sacred site "
        "and the Ex Miscellanea half of Roznov is his priesthood, with Igor "
        "Rastvan as high priest. His devotees are often tied to noble or royal "
        "pagan families and serve as court advisers; his favoured are inspiring "
        "and commanding, and overconfident. The princes of Mecklenburg were "
        "driven from his open worship in 1161.",
        secrets=[
            titled(
                "The Mecklenburgs at Rethra",
                "The Mecklenburg nobility still come secretly to Rethra to honour "
                "Radegast and have gained powers from him.",
            ),
            titled(
                "A prophet of Radegast",
                "Imanitos Mendax poses as Radegast's prophet to the Mecklenburgs.",
            ),
            titled(
                "The Roznov festival",
                "At Roznov the summer-solstice festival hides human sacrifices.",
            ),
            titled(
                "Storyguide Notes",
                "In the saga plot Between the Devil and the Deep Blue Sea, Radegast "
                "is a demon.",
            ),
        ],
    )
    w["frisian_pirates"] = b.faction(
        "Pirates of Frisia",
        faction="Brigands and mercenaries",
        place=lowlands,
        summary=(
            "The pirates of the Frisian coast, Waddenzee's among them, who bury their "
            "dead at the Pirates' Graveyards in Drenthe, a low ridge of standing "
            "stones and boulders above the swamp a couple of dozen miles up the Ems, "
            "the only stones in Friesland. The local nobility cannot unite against "
            "them."
        ),
    )
    w["rhine_tremere"] = b.faction(
        "House Tremere in the Rhine",
        faction="Hermetic group",
        ruler="Stentorius of Fengheld, exarch",
        rules="Only Stentorius and Severicus hold their own sigils; the exarch holds about three-fifths of the rest, Severicus the remainder",
        wants="Order, hierarchy and a strong hand on the Tribunal's eastern frontier",
        summary=(
            "The Tremere of the Tribunal fall under two men. Stentorius of Fengheld "
            "is exarch and holds about three-fifths of the Tremere sigils, his "
            "filius's and the two Tremere of Triamore's among them; Severicus of "
            "Roznov holds the other two-fifths, including his two filii's and "
            "Hygwald Veritas's of Waddenzee. Fengheld's Tremere, with the "
            "Transylvanian Tribunal, served Henry III's conquests of Bohemia, Poland "
            "and Hungary and seized many vis sites; blocked by the Tribunal from "
            "founding daughter covenants, they built chapter houses instead, the "
            "largest run by Clemens filius Stentorius, and have lately loosened their "
            "Transylvanian ties. Roznov Fort remains an arch-conservative stronghold "
            "in regular contact with Transylvania, suspected since 1074 of being a "
            "beach-head for that Tribunal, and its companion Ladislaus sends Gifted "
            "children from the Prague slave market to Coeris."
        ),
    )
    w["bear_lineage"] = b.faction(
        "The bear lineage of House Bjornaer",
        faction="Family",
        realm="Magic",
        place=central,
        members=2,
        summary="Bjornaer magi of bear heartbeast who look back to the Founder herself; "
        "the Senior Elder of the House always has a bear heartbeast in her "
        "memory.",
        secrets=[
            titled(
                "Who is left of the line",
                "An ancient hidden line descending from Bjornaer, now only Archmage "
                "Urgen of Crintera and his filia Odorpes of Fengheld's Lusatia "
                "chapter.",
            ),
            titled(
                "The Bears' Cave",
                "Urgen and Odorpes keep the Bears' Cave in the northern Harz, floored "
                "with the bones of primeval bears, as a private source of Animal vis; "
                "each visits now and then and would be furious to find anyone else "
                "harvesting it.",
            ),
        ],
    )
    w["harmonists"] = b.faction(
        "Harmonists of House Bjornaer",
        faction="Hermetic group",
        place=east,
        ruler="Falke, Prima of Bjornaer, sympathises",
        wants="Mundanes persuaded to live respectfully alongside the wild",
        rules="Dominant on the Bjornaer council; chose in 1168 to wait out the Danish occupation",
        summary=(
            "One of the two ancient factions of House Bjornaer, whose shared "
            "philosophy holds the Magic realm to be the pristine state of the world "
            "before the fae, who arise where wilderness mixes with human curiosity, "
            "and that wilderness must be guarded from mankind, the Church and the "
            "fae alike. Harmonists hold that human expansion cannot be stopped and "
            "Bjornaer are too few to defend everything, so mundanes who do not "
            "destroy the wild must be taught to live beside it. They dominate the "
            "council at Crintera: Jon Arnsson and Phyllia are committed, and Falke "
            "leans their way without declaring. Their counsel prevailed in 1168, "
            "when the House chose to wait out the Danes on Rügen."
        ),
    )
    w["wilderists"] = b.faction(
        "Wilderists of House Bjornaer",
        faction="Hermetic group",
        place=east,
        ruler="Urgen, Senior Elder of Bjornaer",
        wants="Humans confined to walled cities; forests, marshes and moors left to beasts and feared",
        rules="Zealots revert tamed land to wilderness and drive out settlers",
        summary="The more extreme faction of House Bjornaer. Wilderists would keep "
        "humanity behind city walls and the wild places feared, and their "
        "zealots work to turn farmland back to wilderness and drive settlers "
        "off. Urgen, Senior Elder, former Primus and leader of the Hawthorn Gild, "
        "is their most influential voice, arguing that the Order must hold back "
        "the growing mundane population and that Bjornaer should enter Hermetic "
        "politics to do it; Istvan Padas of the Horse seat belongs, and Zora, "
        "priestess of Hertha, backs them. They gain adherents as the occupation "
        "of Rügen drags on, and the Gathering of 1227 is expected to bring the "
        "dispute to a head.",
        secrets=[
            titled(
                "Urgen's campaigns",
                "Urgen is widely suspected of driving mundanes from the wild with "
                "covert animal attacks, and is stepping up such campaigns now he is "
                "free of the Primacy.",
            ),
        ],
    )
    w["forest_brothers_volkhvy"] = b.faction(
        "Volkhvy of the Forest Brothers",
        tradition="trad_volkhvy",
        faction="Hedge coven",
        realm="Faerie",
        place=east,
        rules="All male; nearly all have Ways of the Forest and a fierce devotion to family",
        offers="Burial at the Ziegensteine; the opening of its gate for Bjornaer magi",
        summary="The few remaining priests of Rugevit, Porevit and Porenitz, the gods of "
        "rowan, beech and larch still worshipped in Rügen's wild places. They "
        "are welcome in the Stubnitz Forest, bury devout believers among the "
        "graves and megaliths of the Ziegensteine near Mönchgut, and alone can "
        "open the great empty barrow there, which they often let Bjornaer magi "
        "use because of their friendship with Crintera; Janis, leader of "
        "Crintera's Swan clan, is one of them.",
        secrets=[
            titled(
                "The barrow's gateway",
                "The barrow at the Ziegensteine is a pre-Hermetic gateway, one end of "
                "a faerie trod through a particularly dark region of Arcadia that "
                "comes out near the covenant of Pripet Major in the Novgorod "
                "Tribunal. Nobody at the Russian end can open it, so it works one way "
                "only.",
            ),
        ],
    )
    w["svantovit_volkhvy"] = b.faction(
        "Volkhvy of Svantovit",
        tradition="trad_volkhvy",
        faction="Hedge coven",
        realm="Faerie",
        place=east,
        members=2,
        wants="A white horse for a Great Ritual to the four-faced god",
        offers="Knowledge of the rites of Arkona, which helped Falke learn to thaw the Baltic",
        summary="Only two priests of the four-faced sun- and war-god Svantovit remain, a "
        "very old man and his grandson, scraping a living on the windswept Wittow "
        "peninsula below the ruined temple of Arkona that Bishop Absalon "
        "destroyed in 1169. The elder is trying to pass on all he knows; the "
        "grandson has seen no power and follows only out of family duty. No "
        "white horse remains on Rügen for the Great Ritual, since the Danes took "
        "them all; were one brought, the old man would have his grandson steal "
        "it, and the rite's display of power would make the doubter a zealous "
        "pagan messiah bent on returning Rügen to the god, which watching magi "
        "might take for diabolism.",
        secrets=[
            titled(
                "Svantovit's statue",
                "The two priests of Svantovit have laboriously moved the surviving "
                "upper half of Svantovit's statue from Arkona into a well-hidden "
                "shrine: four faces looking four ways, a bull's horn in its right "
                "hand, the god's huge sword laid before it. Looters took the jewelled "
                "saddle and bridle.",
            ),
        ],
    )
    w["hertha_priesthood"] = b.faction(
        "Priesthood of Hertha",
        faction="Hedge coven",
        realm="Faerie",
        place=east,
        ruler="Zora",
        rules="Every May Eve the goddess bathes in Hertha Lake and one marked watcher is drowned",
        offers="Good harvests for farmers who sprinkle their field corners with the lake's water; Creo vis yearly to Crintera",
        summary=(
            "A small priesthood of women led by Zora, darkly beautiful through her "
            "goddess's gifts and the lover of Istvan Padas of Crintera, whose "
            "Wilderist stance she strongly backs. Every Walpurgis Night Hertha bathes "
            "in the small dark lake in the Stubnitz Forest a short walk from Crintera "
            "and afterwards drowns one of the mortals gathered to watch, marked by "
            "the priestess and the only one present unaware of his fate; the ghosts "
            "of earlier victims gather on the shore. Crintera protects the "
            "priestesses from discovery, and in return Zora gives the covenant Creo "
            "vis each year and never chooses her victim from its covenfolk."
        ),
    )
    w["order_of_odin"] = b.faction(
        "The Order of Odin",
        faction="Hedge coven",
        summary=(
            "The Norse wizards beyond the northern border, as the Order imagines "
            "them. The fear of them has stopped any Hermetic covenant lasting long "
            "enough in Norse lands to attend a Tribunal, which leaves Zealand a grey "
            "area between the Rhine and Novgorod. The Tribunal founded Oculus "
            "Septentrionalis in 1144 to learn about them and it never did; the new "
            "covenant of Heorot has taken up the task, and Pancrestis of Heorot "
            "longs to meet a Norse wizard. Most Lowland magi know of at least a few "
            "Scandinavian wizards."
        ),
    )
    w["knights_of_the_sword"] = b.faction(
        "The Knights of the Sword",
        faction="Military order",
        realm="Divine",
        place=east,
        ruler="Albert von Buxhövden, bishop of Riga, founder",
        rules="A rule modelled on the Templars; in practice murder, rape and robbery go unpunished",
        wants="The pagan Baltic conquered and baptised; estates and silver",
        offers="Christian towns and monasteries in Pomerania; slaves for the Prague market",
        summary=(
            "A military order founded in 1202 by Albert von Buxhövden, bishop of "
            "Riga, to crusade against the pagans of Livonia, far east along the "
            "Baltic in the Novgorod Tribunal; they took Fellin in 1211, massacring "
            "captives and baptising by force, and it is now their base. They grow "
            "ever more lawless, in an uneasy alliance with the Danish king and with "
            "Bishop Albert, who cannot restrain them. In Pomerania their war is as "
            "good as won and knights have settled on seized estates, feared by all "
            "and most by the less pious; nearly twenty years ago they desecrated and "
            "looted the temple of Rethra. They control the slave trade, holding "
            "slaves, mostly Pomeranian, at their fortification in Bautzen before "
            "taking them to Prague, and the profits fund their expansion."
        ),
    )
    w["pomeranian_werewolves"] = b.faction(
        "The Werewolves of Pomerania",
        faction="Family",
        realm="Magic",
        place=east,
        rules="Once a year on Walpurgis Night the factions of a region meet round great bonfires under compacts that forbid fighting",
        wants="Territory, kinship renewed, and the old glory remembered",
        summary="The fireside tales of witches and werewolves in the Eastern Marches are "
        "warnings, and villagers watch neighbours and strangers for odd features "
        "or accents, for animals' fear, for a prickling neck. Shapeshifting runs "
        "in distinct lineages that form one far-flung extended family, passed "
        "reliably from two werewolf parents and less so from one; some live "
        "apart from humanity, others prey on livestock and children. Their only "
        "organisation, contrary to what House Bjornaer believes, is the yearly "
        "meeting on 30 April where disputes are settled, territories agreed, "
        "kinships renewed and the young hear the legends of a glorious past "
        "united under a war-leader against the Romans. Children of werewolf "
        "families are Skinchangers; those born to human families usually have "
        "the Lycanthrope Flaw and cannot control the change. Small animals flee "
        "them, horses shy and dogs bark, unless they have Animal Ken. Some, "
        "especially women, become greatly respected witches with powers of "
        "entrancement or second sight. The storyguide may add bear or lynx "
        "clans.",
        secrets=[
            titled(
                "The betrayal of Bjornaer",
                "The Pomeranian werewolves' legends tell of the betrayal of Bjornaer, "
                "who carried their secrets to the Roman priests, which they blame for "
                "their fall from kings of men to fringe-dwellers.",
            ),
            titled(
                "What the Founder was",
                "Bjornaer the Founder was a Pomeranian shapeshifter-witch of their "
                "kind.",
            ),
        ],
    )
    w["god_of_truth"] = b.faction(
        "The God of Truth",
        faction="Faith or sect",
        realm="Faerie",
        place=bohemia,
        rules="No catechism beyond reverence for the wild and leaving the churches",
        wants="Mankind led into the wild by the angels men call faeries",
        summary="A dualist faith that has arisen in the last decade in the villages near "
        "the Bohemian Forest. It teaches that a God of Truth made the cosmos, "
        "while a God of Law made and rules the material world without caring "
        "for its people, and that the Church errs by worshipping the stern God "
        "of Law. The God of Truth is immaterial and can be found only in the "
        "wild, where he has sent his angels, whom men call faeries, to guide "
        "humanity. With no clear leader or line of transmission, churchmen "
        "cannot stamp it out. Tales speak of the Prophet Iacob, always "
        "accompanied by an albino crow, who appears unpredictably and never "
        "preaches, yet the religion springs up wherever he has been seen.",
        secrets=[
            titled(
                "Who the Prophet is",
                "The Prophet is Iacob of Irencillia, whose caricature Nestor is the "
                "white crow, carrying out Primus Handri's plan to found a religion in "
                "the name of the fae. The Quaesitores would be appalled.",
            ),
        ],
    )


# -- threats --


def _threats(rhine: Rhine) -> None:
    b, w = rhine.b, rhine.world
    lowlands = _place(rhine, "lowlands")
    central = _place(rhine, "central")
    east = _place(rhine, "east")
    bohemia = _place(rhine, "bohemia")
    stage = b.stage

    w["waddenzee_piracy"] = b.threat(
        "Waddenzee's piracy",
        antagonist="The magi of Waddenzee",
        place=_place(rhine, "waddenzee_site") or lowlands,
        summary=(
            "Five magically enhanced ships and nearly two hundred pirates raid North "
            "Sea shipping from Terschelling, breaking mundane law daily and skirting "
            "the Code by leaving no witnesses. Oculus Septentrionalis has lost "
            "several ships and cargoes, the Nebelkönigin with its vis and books "
            "among them, and waits for one misstep; the Quaesitores have warned the "
            "pirates repeatedly that they will get no Tribunal support if the "
            "mundane authorities move against them. Only the nobles' failure to "
            "unite has saved the covenant so far."
        ),
        stages=[
            stage(
                "Ships lost",
                at=1,
                clues="Merchants of Lübeck and the Frisian coast count their losses; a stolen flagship sails under a new master.",
                ignored="The raids grow bolder and each pirate magus edges nearer a charge of High Crimes.",
                stopped="A ship recovered or a witness left alive gives Oculus Septentrionalis its case at Tribunal.",
            ),
            stage(
                "The nobles unite",
                at=2,
                clues="Lords who could never agree begin to talk of the haunted island.",
                ignored="A mundane army is raised against Terschelling, perhaps at Oculus Septentrionalis's secret prompting.",
                turned="The Tribunal is asked whether Waddenzee's magi brought ruin on themselves.",
            ),
            stage(
                "War on the pirates",
                at=3,
                clues="Bigger ships sail in convoy; the merchant towns hire soldiers and court noble allies.",
                ignored="With Oculus Septentrionalis at the head of the merchant league, a direct assault on Waddenzee follows; but this lies more than twenty years off.",
            ),
        ],
    )
    w["ash_of_nortorf"] = b.threat(
        "The Ash of Nortorf",
        antagonist="The black horseman and the spirit of the ash",
        realm="Infernal",
        place=lowlands,
        summary=(
            "A small ash seedling in Nortorf's churchyard, cut down every New Year's "
            "Night by a white rider on a white horse while a black rider on a black "
            "horse tries and fails to stop him. Prophecy says that one day the black "
            "rider wins, the shoot grows into a tree, and when a horse can be tied "
            "beneath it a king comes with a great army; while his horse stays under "
            "the tree he cannot be beaten and gains fell powers. The tree spirit is "
            "Infernal, of Might 10 now and potentially 40, ambitious, and able to "
            "grant victory and the gifts of entrancement, inspiration and "
            "toughness; the white rider is Divine, the black an agent of Hell."
        ),
        stages=[
            stage(
                "A tip about a vis source",
                at=1,
                clues="Agents of the black rider tell the magi of a tree in a churchyard that will one day yield vis, but not of the prophecy.",
                ignored="The characters are expected at Nortorf on New Year's Night to guard it.",
            ),
            stage(
                "New Year's Night",
                at=2,
                clues="A white rider comes to cut down a seedling; a black rider rides against him.",
                ignored="If the Divine rider is driven off or killed he never returns, and evil gains a foothold.",
                stopped="The white rider cuts the ash as every year, and the seedling stays small.",
            ),
            stage(
                "The tree grows",
                at=3,
                clues="The ash leafs and thickens year on year until a horse can be tied beneath it.",
                ignored="A king comes with a great army and the tree's fell gifts.",
            ),
        ],
    )
    w["boglins"] = b.threat(
        "Boglins",
        antagonist="Boglins, swamp spirit-beasts of Might 25",
        realm="Magic",
        place=lowlands,
        summary=(
            "Tentacled spirit-beasts of the northern bogs, Magic Might 25 of Aquam: "
            "eight slimy dark-brown tentacles twelve feet long round a carapaced "
            "sac of a body with a toothy maw, lying under murky water where a foul "
            "stench and faint murmuring betray their pools. Gluttonous, reclusive and "
            "cunning, a boglin ambushes anything that passes, chokes it with a cloud "
            "of stinking gas, paralyses it with venomous barbs and drags it to the "
            "maw within a few rounds to eat later. Each tentacle takes wounds "
            "separately and regrows over a season's hibernation; the carcass yields "
            "eight pawns of Animal vis, one per tentacle, and six of Perdo from the "
            "black nodule of its brain."
        ),
    )
    w["vehm_threat"] = b.threat(
        "The Holy Vehm's hangings",
        antagonist="The Holy Vehm, and Philippus Niger behind it",
        place=lowlands,
        summary="The secret courts of the north hang suspected witches and heretics "
        "after trials no accused can win, and leave an SSGG knife by the corpse. "
        "Their informants are everywhere, their jurisdiction covers witchcraft "
        "and sacrilege, and their courts have lately begun to sit south of their "
        "old lands.",
        secrets=[
            titled(
                "Philippus Niger and the Vehm",
                "Philippus Niger of Durenmar turns the Vehm on hedge wizards, has had "
                "at least one Marched magus hanged by it, and spreads it southward "
                "while telling House Guernicus it is no threat to the Order.",
            ),
        ],
        stages=[
            stage(
                "Courts in the south",
                at=1,
                clues="Hanged men with knives beside them appear where the Vehm never sat before; a hillock gathering by night.",
                ignored="Cunning-folk and hedge wizards near the covenant vanish one by one.",
            ),
            stage(
                "A hedge wizard hanged",
                at=2,
                clues="A wise-woman the covenant dealt with is found hanging in the market place.",
                ignored="Informants note the covenant's own dealings; a grog or companion is summoned to appear.",
                stopped="A Freigraf's men are exposed, and someone asks who he answers to.",
            ),
            stage(
                "A magus accused",
                at=3,
                clues="Seven witnesses are ready to swear; the accused is not expected to appear.",
                ignored="A sentence of hanging on a magus, and a quarrel at Tribunal over whether the Vehm is a mundane matter.",
                turned="The trail leads to Durenmar's archmage and a scandal before the Quaesitores.",
            ),
        ],
    )
    w["imanitos_mendax"] = b.threat(
        "Imanitos Mendax",
        antagonist="Imanitos Mendax of Jerbiton",
        place=lowlands,
        summary="A master of House Jerbiton at Oculus Septentrionalis in Lübeck who "
        "poses as the owner of the upmarket Goldenes Kalb tavern, with a "
        "discreet brothel upstairs for rich clients, and whose third trade is "
        "the blackmail and extortion of citizens and magi. Tall, lean and "
        "handsome, a subtle Mentem specialist with competent Imaginem for "
        "disguises; his covenant-mates find him useful despite his morals.",
        secrets=[
            titled(
                "Imanitos and the pirates",
                "Imanitos Mendax feeds Eric Ribecus of Waddenzee advance word of the "
                "covenant's ship movements for a share of the plunder, perhaps by "
                "tiny Astasian messenger demons taken for airy spirits; discovery "
                "would mean expulsion and undying enmity.",
            ),
            titled(
                "Storyguide Notes",
                "Optionally he is a diabolist of a hidden dark Jerbiton lineage "
                "serving the demon Radegast, corrupting Lübeck's notables through the "
                "Goldenes Kalb, posing as the prophet of Radegast to the "
                "Mecklenburgs, able to swap the covenant's three Verditius magestones "
                "for infernally tainted copies, and perhaps planting corruption at "
                "the heart of the coming merchant league.",
            ),
        ],
        stages=[
            stage(
                "Word reaches the pirates",
                at=1,
                clues="Waddenzee's ships always know where the richest Lübeck cargo sails; airy spirits are seen about the Goldenes Kalb.",
                ignored="More ships are lost and Oculus Septentrionalis blames bad luck.",
            ),
            stage(
                "The prophet of Radegast",
                at=2,
                clues="The Mecklenburg princes grow bold; a stranger is honoured at their secret rites.",
                ignored="A pagan house with unnatural powers gains a Hermetic adviser.",
                stopped="The prophet unmasked, the Mecklenburgs turn on their god's false servant or on the Order.",
            ),
            stage(
                "Tainted stones",
                at=3,
                clues="Greed and quarrels grow in the covenant's laboratories.",
                ignored="The three magestones are copies; the Hermetic books Waddenzee stole are tainted, and Lucas von Beck's necromancy draws on infernal lore unknowing.",
                turned="His treachery proven, Imanitos is expelled and the richest covenant in the Rhine has a new enemy.",
            ),
        ],
    )
    w["wild_hunt"] = b.threat(
        "The Wild Hunt",
        antagonist="The Wild Huntsman, Unseelie lord of Might 50",
        realm="Faerie",
        moves="Fixed dates",
        place=lowlands,
        summary=(
            "Folk memory confuses two hunts. Hellequin's Hunt is a host of the "
            "unfulfilled dead in a mobile regio centred on Hellequin, a cursed "
            "spirit whose task is to guide souls that cannot reach Heaven; its "
            "ghosts seek the grace of mortals to pass on. The Wild Hunt proper is a "
            "troupe of winter and storm faeries that rises from the Teufelsküche and "
            "sweeps Germany on stormy winter nights: the Huntsman, a grim figure on "
            "an immense black horse in a storm-grey robe with a gleaming helm and a "
            "spear, perhaps a fragment of Woden, with ten to fifteen ghostly "
            "Horsemen of Might 20 who merge with their mounts and command fear, "
            "wind and cold, and twenty-five to thirty immense grey Hounds of Might "
            "10 whose howls are the arctic wind. It hunts the Holzfrauen, holding "
            "that if every vegetation faerie is caught spring cannot come, and "
            "sometimes mortals; being spirits of wind and night it can only terrify, "
            "buffet and chill, unless the Huntsman talks a mortal into riding with "
            "it. Then every huntsman strikes with lethal force, and the rider is "
            "found at dawn exhausted and frozen, Enfeebled for good."
        ),
        # The Hunt rides through the winter and is beaten on Walpurgis
        # Night (Guardians of the Forests p. 81), so its spring follows its
        # winter; the years are the pack's, the book gives none.
        stages=[
            stage(
                "Stormy winter nights",
                year=1220,
                season="Winter",
                clues="Howling like the arctic wind over the peasants' roofs; a grim rider who asks a traveller to mount up.",
                ignored="A mortal who rides is found at dawn, never to recover.",
                stopped="A Holzfrau sheltered or a rider refused, and winter loosens its grip a little.",
            ),
            stage(
                "Frau Holle's flight",
                year=1221,
                season="Spring",
                clues="For nine days before Walpurgis Night a humble wood-wife in a rickety wagon begs villagers for help and shelter and checks their housekeeping, the Hunt at her heels.",
                ignored="A village that turns her away hears the Hunt pass over; one that shelters her draws its attention.",
                turned="A peasant who carves her a new linchpin finds the shavings turned to gold; a farmer who hides her in his barn finds gold in his rye.",
            ),
            stage(
                "Walpurgis Night",
                year=1221,
                season="Spring",
                clues="The Harz witches climb the Brocken, fires are lit on the slopes and the auras double.",
                ignored="The Hunt fights the airy spirits of summer round the Witches' Altar and loses, and at dawn Walpurga drives her wagon off across the clouds.",
            ),
        ],
    )
    w["bergstrasse_bandits"] = b.threat(
        "Bandits of the Bergstrasse",
        antagonist="Outlaws of the Rhine marshes",
        place=central,
        summary=(
            "Bandits hide in the swampy, deserted east bank of the Rhine along the "
            "western edge of the Odenwald and prey on the merchants who use the old "
            "Roman road, now the busy Bergstrasse, north to Frankfurt. Fortified "
            "way-stations are being built along the road against them."
        ),
    )
    w["fengheld_ambition"] = b.threat(
        "Fengheld's hidden ambition",
        antagonist="The senior magi of Fengheld",
        place=_place(rhine, "fengheld_site") or central,
        summary="Fengheld commands more than forty Tribunal votes, nearly a quarter of "
        "the whole, though they are seldom all cast together, and presents "
        "itself as the Tribunal's neutral peacemaker and arbiter of disputes. "
        "The more paranoid magi already suspect a hidden agenda behind the "
        "neutrality.",
        secrets=[
            titled(
                "Fengheld's real policy",
                "Fengheld's real policy is to keep every other covenant so tangled in "
                "politics that nobody notices its own growing power, and it has "
                "worked so far.",
            ),
        ],
    )
    w["balastor_liberation"] = b.threat(
        "Balastor's liberation",
        antagonist="Balastor of Criamon",
        place=_place(rhine, "fengheld_site") or central,
        summary=(
            "A young journeyman of Fengheld, born feral, who believes enlightenment "
            "means casting off humanity and means to return himself and others, "
            "consenting or not, to a primal state. His magic releases suppressed "
            "emotion and behaviour, his face takes a savage cast when he casts, and "
            "he delights in humbling self-important mundanes."
        ),
    )
    w["great_khan"] = b.threat(
        "The Great Khan",
        antagonist="The Mongol Khan",
        realm="Magic",
        place=central,
        summary=(
            "At the foot of the tallest peak of the Kyffhäuser stands a withered "
            "apple tree of Might 45, guarded by the unaging men-at-arms who failed "
            "to hang their shields on it. Whichever prince hangs his shield there "
            "rules all the West; Clovis, Charlemagne and Barbarossa each did and cut "
            "it down, and it regrows and withers with their fortunes. When it next "
            "leafs a terrible fight begins; when it fruits the king hangs his shield "
            "and the wicked are rooted out. The Mongol Khan may hear of it and come "
            "to hang his shield, and the fate of the West will turn on who stops "
            "him."
        ),
        stages=[
            stage(
                "The tree leafs",
                at=1,
                clues="Travellers in the Kyffhäuser report the dead apple tree in full leaf.",
                ignored="A terrible fight begins, as the legend says.",
            ),
            stage(
                "The Khan rides west",
                at=2,
                clues="Word from the east of a lord of horsemen who asks after a tree where kings hang their shields.",
                ignored="The Khan's host reaches the hills and the men-at-arms meet it.",
                stopped="Whoever defeats the guards and fails to hang his shield is possessed and joins them.",
            ),
            stage(
                "The tree fruits",
                at=3,
                clues="Fruit on the branches for the first time since Barbarossa.",
                ignored="A king hangs his shield, all men rally to it, and the wicked are rooted out, whoever he is.",
            ),
        ],
    )
    w["grendels_kin"] = b.threat(
        "Grendel's kin",
        antagonist="The trolls of Zealand's bogs",
        realm="Magic",
        place=_place(rhine, "heorot_site") or east,
        summary=(
            "Trolls still haunt the bogs of Zealand round the site of Hrothgar's "
            "hall, where the new covenant of Heorot has settled. They have killed "
            "fourteen of its grogs and taken the left arm of its leader Signum "
            "Irruptus, who believes them the degenerate descendants of gods and "
            "pursues his study of them regardless."
        ),
    )
    w["danish_rugen"] = b.threat(
        "The Danish occupation of Rügen",
        antagonist="Valdemar II of Denmark and the Church on Rügen",
        realm="Divine",
        place=_place(rhine, "crintera_site") or east,
        summary=(
            "Since Valdemar I and Bishop Absalon took the island in 1168, Rügen has "
            "had Danish rulers, the Danish-founded town of Bergen, new churches at "
            "Bergen and Altenkirchen, a Cistercian monastery whose monks now farm "
            "Mönchgut, and a church planned at Sagard, five miles from Crintera. "
            "The domus magna of House Bjornaer has been in Winter for fifty years "
            "because of it: recruiting a turb from an increasingly Christian island "
            "is hard, its magical resources were damaged, and the Dominion creeps "
            "toward the Stubnitz Forest. The Tribunal of 1186 split on whether the "
            "Guardians of the Forests ruling allowed a reprisal, and in 1194 "
            "Quaesitor Caecilius ruled that no wilderness had been invaded while "
            "Crintera's forest stood; the grievance drives the House toward the "
            "Wilderists."
        ),
        stages=[
            stage(
                "The church at Sagard",
                at=1,
                clues="Masons and a priest arrive at Sagard; the monks' fields spread over Mönchgut.",
                ignored="A Divine aura grows five miles from Crintera's regio and the covenfolk's children are baptised.",
                stopped="Animal attacks and tales of witches drive the builders off, and Bjornaer magi face prosecution as after 1186.",
            ),
            stage(
                "Crintera's turb dwindles",
                at=2,
                clues="Empty roundhouses on the first level; the Horse clan's herd thinned by Danish requisitions.",
                ignored="The Wilderists gain the council, and Urgen's covert campaigns grow open.",
                turned="A Harmonist settlement with the Danes, if the Quaesitores and the king can both be satisfied.",
            ),
            stage(
                "The Gathering of 1227",
                at=3,
                clues="Fifty to a hundred Bjornaer converge on Rügen for the Teufelsjahr.",
                ignored="The dispute between Harmonists and Wilderists comes to a head before the whole House.",
            ),
        ],
    )
    w["prague_slave_trade"] = b.threat(
        "The slave trade of Prague",
        antagonist="The Knights of the Sword and the slave merchants of Prague",
        place=bohemia,
        summary="Prague holds a large slave market, and the word for a slave is the word "
        "for a Slav; the Church forbids only the enslavement of Christians. The "
        "Knights of the Sword control the trade, which pays for their corrupt "
        "expansion in Pomerania and beyond: they bring slaves to Prague and sell "
        "them to Jewish merchants who resell them in Muslim lands. An ordinary "
        "slave costs a few shillings, less than a good horse; the exceptional "
        "ten times that, and the young, healthy and strong fetch more. Owning "
        "slaves is legal in Germany and frowned on by the Church.",
        secrets=[
            titled(
                "Who Ladislaus is",
                "Ladislaus, a shady-looking man at the market, is a trusted companion "
                "of Roznov; he picks out Gifted children among the slaves, who are "
                "delivered to Coeris, the domus magna of House Tremere in "
                "Transylvania.",
            ),
            titled(
                "Where the other slaves go",
                "The other slaves Ladislaus buys are traded or used by Roznov, and "
                "some become the victims of its summer-solstice sacrifices.",
            ),
            titled(
                "Storyguide Notes",
                "Ladislaus has Magic Sensitivity.",
            ),
        ],
    )
    w["bohemian_giants"] = b.threat(
        "Giants of the Bohemian Forest",
        antagonist="The giants of the forest",
        place=_place(rhine, "bohemia") if bohemia is not None else None,
        summary=(
            "Giants haunt the Bohemian Forest, nearly as large as the Black Forest "
            "and kept free of men by its climate and its peat bogs, swamps and "
            "marshes. They gathered the great broken rocks of Obri Hrad, the Giants' "
            "Castle, on its hilltop above the Losenice at the forest's southern "
            "edge, and may still visit it, though its Magic aura of 3 makes it a "
            "possible covenant site. Rügen's giants were long ago driven out to "
            "Pomerania after an epic battle, leaving only the out-of-place boulders "
            "of that island."
        ),
    )
