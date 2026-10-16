"""Anjou and Aquitaine, as of spring 1220: the old Angevin heartland on
the Loire and the great duchy south of it to the Dordogne and the
Auvergne. Its land (the river valleys, the megaliths, the cave
dwellings, the marshes and the extinct volcanoes, and their regiones);
its living covenants Oleron, Nidi and Atsingani with their magi,
libraries and vis; and its mundane world of bailli, counts and dukes,
bishops and abbeys, towns and brigands, in paraphrase of The Lion and
the Lily, chapter six.

The chapter's ruined covenants (Sinapis at Tavant, Ligurio, Vexatores,
Nauche-Fleur and Alcuin's Auberge) are tribunal.py's; the lines of
fealty are set in its finish."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Normandy

# House ids, so a typo cannot slip into a record.
BJORNAER = "house_bjornaer"
EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"

# The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."

RUMOURED = {"status": "Rumoured", "known": "Locally"}
UNKNOWN = {"status": "Unknown", "known": "Nobody"}
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _place(normandy: Normandy, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


#: The records that answer to the King of France, whom a later part
#: makes (`world["king"]`): linked in `finish`.
CROWN_HELD = ("bailli_anjou", "chinon", "tours", "saumur", "le_puy_st_front")


def build(normandy: Normandy) -> None:
    tribunal = normandy.tribunal
    assert tribunal is not None
    _regions(normandy)
    _anjou_places(normandy)
    _aquitaine_places(normandy)
    _anjou_world(normandy)
    _aquitaine_world(normandy)
    _oleron(normandy, tribunal)
    _nidi(normandy, tribunal)
    _atsingani(normandy, tribunal)


# ---------------------------------------------------------------- regions


def _regions(normandy: Normandy) -> None:
    _place(
        normandy,
        "anjou",
        "Anjou",
        summary=paragraphs(
            "The counties of Anjou, Touraine and Maine on the lower Loire, "
            "the heart of the old Angevin lands. Druid-led tribes fought the "
            "Romans here, every city keeps Roman traces, and Norse raids in "
            "the ninth and tenth centuries sacked the towns and filled the "
            "land with fortresses. Its greatest counts were Fulk Nerra, the "
            "Black Falcon (987 to 1040), and Henry, who became Henry II of "
            "England and ruled from the Scottish border to the Pyrenees. "
            "Philip II took Anjou from King John and had to win many of its "
            "castles one by one; there has been no count since 1203, the "
            "crown claims every comital right, and royal bailli govern it "
            "district by district, as in Normandy.",
            "Castles, abbeys and churches crowd the river valleys, so that "
            "little besides the Church and the nobility seems to hold power; "
            "the forested uplands between (pine to the north, broadleaf to "
            "the south) are noble hunting grounds, full of menhirs and "
            "dolmens. The Loire is the great road, shrunk to braided streams "
            "round sandbanks in summer and flooding in spring and autumn, "
            "plied by flat-bottomed square-sailed boats and fished for eels "
            "and fowl. Its tributaries cut through soft white tufa to gravels "
            "that grow fine vines, and along many of them as many as half "
            "the people live in caves dug into the limestone cliffs.",
            "The Hermetic covenants of the chapter are Oleron, Nidi and "
            "Atsingani; the ruins of Sinapis, Alcuin's Auberge, Ligurio, "
            "Nauche-Fleur and Vexatores lie in the two regions. The Way of "
            "St. James runs through Tours, Poitiers, Melle and Saintes to "
            "the Dordogne crossing at Libourne, with branches by Angers and "
            "Niort and from Poitiers by Angoulême and Aubeterre; pilgrims "
            "from England, Normandy and Brittany often come by sea to the "
            "Gironde ports. Travelling in a band of pilgrims is a good way "
            "for careful magi to pass unremarked.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        normandy,
        "aquitaine",
        "Aquitaine",
        summary=paragraphs(
            "The largest duchy of France, over two hundred and forty miles "
            "from the Bay of Biscay to the upper Loire: Poitou, Limousin, "
            "Périgord, Saintonge and the Auvergne. The west is wooded "
            "limestone plateau cut by rivers running to the Loire or the "
            "Dordogne; the east is the Central Massif, hard volcanic upland "
            "and puys where only sheep and goats thrive. South-facing "
            "limestone slopes carry vineyards, and wine, truffles and walnut "
            "oil go down the rivers; behind the coastal dunes lie wide "
            "marshes. Castles guard every road and river and churches stand "
            "almost everywhere, so little land escapes the lords and the "
            "Dominion.",
            "Charlemagne made a kingdom of Aquitaine in 778; by the tenth "
            "century its barons were feuding behind their walls and ignoring "
            "any overlord. Eleanor of Aquitaine brought the duchy to Louis of "
            "France in 1137 and, after their divorce, to Henry of Anjou in "
            "1154, since when it has been the prize between the kings of "
            "France and England. The present duke is Henry III, King of "
            "England.",
            "The Tribunal counts Aquitaine north of the Dordogne as its own, "
            "though the southern folk speak Dordonha, a tongue of Oc. Nidi "
            "is the only covenant down there, and it is older than the Grand "
            "Tribunal's ruling of 1103; any covenant founded that far south "
            "now would belong to Provence.",
            "In the cemeteries of Berry, Limousin and the Dordogne stand "
            "lanterns of the dead, slender stone towers six or eight times as "
            "tall as they are wide, with a lamp lit on top each night for "
            "the holy dead; the custom began with a novice of Charlieu shown "
            "such a tower in a vision by his dead uncle. Tradition-minded "
            "grogs ask for one over a covenant's graveyard, but an angel "
            "sees one torn down if those beneath are unworthy.",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- Anjou


def _anjou_places(normandy: Normandy) -> None:
    anjou = normandy.places["anjou"]
    _place(
        normandy,
        "behuard",
        "Béhuard Island",
        inside=anjou,
        aura=2,
        summary=(
            "An island in the Loire south-west of Angers, where a small "
            "Christian oratory was built over an ancient shrine of a sea "
            "goddess. Locals come to pray for the rivermen, and their "
            "devotion has raised a Dominion aura that swamps the shrine's "
            "Magic aura of 2."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "mayenne_valley",
        "The Mayenne Valley",
        inside=anjou,
        summary=(
            "North of Angers the River Mayenne runs through a valley too "
            "steep to build in and unfit for cave homes, so it is one of the "
            "few places near the city with no Dominion aura: a possible "
            "refuge or site for magi."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "le_mans_menhir",
        "The Menhir of Le Mans",
        inside=anjou,
        aura=0,
        summary=secrets(
            paragraphs(
                "A striped, pinkish standing stone at the south corner of "
                "the west front of Le Mans cathedral, pitted with a few "
                "holes; seen side-on in the right light it looks like a "
                "hooded figure. The site was pagan before the church, and "
                "folk still think it lucky to put their fingers in the "
                "holes. A Seeker might study it for what it shows of old "
                "fertility rites.",
                "Story seed: the cathedral clergy, unwilling to involve rival "
                "clerics or to speak openly, ask the magi through a go-between "
                "to take the stone away quietly.",
            ),
            paragraphs(
                "The menhir was the heart of a fertility cult whose true rite "
                "is forgotten: at each equinox a sheep was killed and its "
                "blood poured over the stone; once dry, it scrapes off as "
                "several pawns of Creo vis. The first "
                "Christians meant to move it, but whoever tried met with a "
                "nasty accident, so they built it into the church. Its "
                "Magic aura was once 6 round the stone; with the cult gone it "
                "would be 4, but the cathedral's Dominion smothers it.",
                "A year ago some drunken local lads rediscovered what the "
                "holes were really for, and their wives and sweethearts bore "
                "strong, healthy babies nine months later. The story has "
                "spread, others are trying their luck, and the Church wants "
                "it stopped.",
            ),
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "mercurian_tower",
        "The Gallo-Roman Tower by Tours",
        inside=anjou,
        aura=1,
        summary=secrets(
            "A windowless Roman brick tower west of Tours, high on a ridge "
            "over the Loire's north bank, sixteen feet square and about a "
            "hundred feet tall. No one locally knows what it was for. The "
            "Magic aura is 1 at its foot and rises to 5 at the top.",
            "Roman soldiers built it during the conquest of Gaul as a lookout "
            "for a magician of the Cult of Mercury.",
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "azay_valley",
        "The Valley of Empty Caves",
        inside=anjou,
        aura=4,
        summary=(
            "An enclosed valley about four miles south of Azay-le-Rideau on "
            "the Indre, south-west of Tours, where the people round about "
            "live in cliff caves of white tufa. Its many damp caves stand "
            "empty, it holds a Magic aura of 4, and a steady source there "
            "yields a little Aquam vis: a likely site for a new covenant."
        ),
        **RUMOURED,
    )
    _place(
        normandy,
        "faeries_cave",
        "The Faeries' Cave",
        inside=anjou,
        realm="Faerie",
        aura=3,
        summary=(
            "A dolmen deep in the forest some six miles north-west of Tours: "
            "eight great stones holding up three huge slabs over a chamber "
            "twelve feet long and four high, with a cross-stone closing off a "
            "small private space at one end. Its Faerie aura of 3 rises to 5 "
            "while the fae are there; they feast in it at least once a year."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "gennes",
        "The Nymphs' Shrine at Gennes",
        inside=anjou,
        summary=paragraphs(
            "Beside the Roman amphitheatre at Gennes, downstream of Saumur, "
            "lies a small Magic regio holding a Gallo-Roman shrine.",
        ),
        levels=[
            Builder.level(
                "The shrine of the water cult",
                0,
                notes=(
                    "Several nymphs live here (aura not given). They gladly "
                    "talk about the water cult that honoured them under Rome "
                    "and may give Aquam vis to visitors who amuse, honour or "
                    "serve them. They are attentive, persuasive and loath to "
                    "lose male company, so a man may find it hard to leave."
                ),
            )
        ],
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "bagneux",
        "The Dolmen of Bagneux",
        inside=anjou,
        aura=1,
        summary=(
            "The largest of the many menhirs and dolmens hidden in the "
            "wooded hills round Saumur: a chamber sixty-six feet long and "
            "twenty-three wide, walled by sixteen upright slabs and roofed by "
            "four flat stones on a central pillar. It has a low Magic aura, "
            "as do the other megaliths far enough from the Dominion."
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "doue",
        "The Sarcophagus Rock of Doué-la-Fontaine",
        inside=anjou,
        summary=(
            "An outcrop south-west of Saumur whose stone holds Creo vis and "
            "keeps flesh from decay. Merovingian masons cut thousands of "
            "stone coffins from it, but its virtue has been forgotten."
        ),
        **UNKNOWN,
    )


def _anjou_world(normandy: Normandy) -> None:
    b = normandy.b
    w = normandy.world
    anjou = normandy.places["anjou"]

    w["bailli_anjou"] = b.lord(
        "The Bailli of Anjou",
        title="landed",
        wealth="Wealthy",
        manors=0,
        seat="Angers",
        place=anjou,
        summary=(
            "Since 1203 there has been no Count of Anjou: King Philip claims "
            "all the count's old rights and duties and governs Anjou, "
            "Touraine and Maine through professional royal officers, each "
            "bailli ruling a district in his name. They answer to the king, "
            "not to the local barons, and many castles had to be taken by "
            "force before they would."
        ),
    )
    w["montoire"] = b.lord(
        "Count John IV of Montoire",
        title="count",
        seat="Vendôme castle",
        place=anjou,
        summary=secrets(
            "Lord of the castle that looks down on Vendôme from its rocky "
            "spur. An old spear with a short dark shaft and an outdated "
            "plain iron head hangs on his wall; thrown, it has no lift and "
            "always lands flat. Two old folk of the castle believe it is one "
            "of the spears of the abbey's legend.",
            "It is. The second lies forgotten in an old chest in the darkest "
            "corner of the oldest part of the abbey crypt, and a farmer's "
            "wife a few miles out treasures the third as an heirloom. Each "
            "is an Arcane Connection to the other two, and once all three "
            "are together, each drips a drop of red flame holding a pawn of "
            "Divine-tainted Ignem vis on the first Sunday after Pentecost. "
            "Swapping the count's for a new spear is easy, but negotiation "
            "is safer than theft.",
        ),
    )

    w["angers"] = b.town(
        "Angers",
        charter="Noble lord",
        ruler="The royal bailli",
        answers_to=w["bailli_anjou"],
        place=anjou,
        summary=paragraphs(
            "Capital of the county of Anjou on the River Maine and long the "
            "seat of Plantagenet power, built of the pale tufa of White "
            "Anjou and the dark schist and slate of Black Anjou. Henry II "
            "loved its fortress and founded its Hospital of St. John. A long "
            "stair climbs from the quay to the cathedral of St. Maurice. The "
            "abbeys of Ronceray (Fulk Nerra's foundation), St. Serge and St. "
            "Aubin stand in the city.",
        ),
    )
    w["angers_cathedral"] = b.church(
        "Cathedral of St. Maurice, Angers",
        church="Bishop's cathedral",
        place=anjou,
        summary=(
            "The bishop's church of Angers; a long stair climbs to it from "
            "the quay. Pilgrims pray here for relief from gout and "
            "cramp."
        ),
    )
    w["angers_abbeys"] = b.church(
        "The Abbeys of Angers",
        church="Monastery or nunnery",
        order="Benedictine",
        place=anjou,
        summary=(
            "Three religious houses of the city: Ronceray, founded by Fulk "
            "Nerra, and the abbeys of St. Serge and St. Aubin."
        ),
    )
    w["chinon"] = b.town(
        "Chinon",
        charter="Noble lord",
        place=anjou,
        summary=paragraphs(
            "A wine town on the River Vienne below the great castle Henry II "
            "built along the wooded north bank, a quarter of a mile end to "
            "end; below the slope the streets follow the line of the river. The church is St. Maurice's, the cliffs to the east hold "
            "cave homes and the cave Chapel of St. Radegonde, and the Forest "
            "of Chinon lies beyond. Henry II died here in 1189, John married "
            "Isabelle of Angoulême here in 1200, and the Treaty of Chinon "
            "gave the town to Philip II in 1214.",
            "Six miles upstream, at Tavant, a small parish church with "
            "astonishingly lifelike paintings and carvings of griffins, "
            "sirens and a two-bodied monster is all that is left of the "
            "covenant of Sinapis.",
        ),
    )
    w["le_mans"] = b.town(
        "Le Mans",
        charter="Noble lord",
        answers_to=w["bailli_anjou"],
        place=anjou,
        summary=(
            "Capital of Maine on the River Sarthe, still ringed by its "
            "Gallo-Roman wall. Its cathedral of St. Julien has carving to "
            "rival Chartres, and a pagan menhir stands against its west "
            "front."
        ),
    )
    w["le_mans_cathedral"] = b.church(
        "Cathedral of St. Julien, Le Mans",
        church="Bishop's cathedral",
        place=normandy.places["le_mans_menhir"],
        summary=(
            "The bishop's church of Maine, its sculpture second only to "
            "Chartres. The old standing stone built into its west front is "
            "an embarrassment its clergy would gladly be rid of."
        ),
    )
    w["solesmes"] = b.church(
        "Abbey of St. Peter, Solesmes",
        church="Monastery or nunnery",
        order="Benedictine",
        place=anjou,
        summary=(
            "An abbey south-west of Le Mans that keeps a Holy Thorn, one of "
            "the thorns of Christ's crown, which the Lord of Sablé carried "
            "home from the Holy Land; it has Faith 2."
        ),
    )
    w["tours"] = b.town(
        "Tours",
        charter="Noble lord",
        place=anjou,
        summary=paragraphs(
            "A trading city on the south bank of the Loire, its fortress and "
            "great churches inside the repaired Roman walls and a newer "
            "quarter to the west built after the Viking raids. It is a "
            "centre of learning and pilgrimage, with the tomb of St. Martin "
            "in his basilica and the Abbey of St. Julien. Philip took it "
            "from the Angevins in 1205.",
            "St. Martin was tricked into coming here in 371, hid from the "
            "crowd come to make him bishop, was given away by honking geese, "
            "and served twenty-six years while living simply at Marmoutier "
            "by the city gate. Gregory of Tours was cured at Martin's tomb "
            "in 563 and became bishop in 573. Alcuin of York became abbot "
            "of St. Martin's on leaving Charlemagne's court and founded its "
            "school and scriptorium.",
            "The Redcaps moved their Mercer House here from Lixivia in 1124, "
            "beneath an enlarged pilgrim hostel; Alcuin's Auberge prospered "
            "until raiders took it in 1197. Some say Fudarus sent them; "
            "nothing was proved.",
        ),
    )
    w["st_martin_tours"] = b.church(
        "Basilica and Abbey of St. Martin, Tours",
        church="Large urban church",
        order="Benedictine",
        place=anjou,
        summary=paragraphs(
            "The tomb of St. Martin, one of the great pilgrim shrines of "
            "France, and the abbey whose school of the liberal arts and "
            "busy scriptorium Alcuin of York founded; the scriptorium still "
            "thrives.",
            "The works of Gregory of Tours, the city's sixth-century bishop, "
            "are read here: the ten books of his History of the Franks (a "
            "summa on the Frankish royal house, level 4, quality 14, which "
            "also serves as a summa on the lore of France, level 3, quality "
            "14; Magic Lore, level 3, quality 12; Divine Lore, level 2, "
            "quality 14; and Intrigue, level 2, quality 10), with much on "
            "the uncanny powers of the Merovingian kings; the Lives of the "
            "Fathers (a tractatus on Church Lore, quality 10); four books on "
            "the miracles of St. Martin, the last unfinished (a tractatus on "
            "Dominion Lore, quality 8); and On the Courses of the Stars, a "
            "psalm commentary that times the night office by the stars "
            "(tractatus on astronomy, quality 6, and on Church Lore, "
            "quality 12).",
        ),
    )
    w["st_julien_tours"] = b.church(
        "Abbey of St. Julien, Tours",
        church="Monastery or nunnery",
        order="Benedictine",
        place=anjou,
        summary="An abbey in the old walled quarter of Tours.",
    )
    w["marmoutier"] = b.church(
        "Marmoutier",
        church="Monastery or nunnery",
        order="Benedictine",
        place=anjou,
        founded=372,
        summary=(
            "The monastery by the gate of Tours where St. Martin lived "
            "simply while bishop. Its monks keep a priory at Sallertaine in "
            "the Vendée marshes."
        ),
    )
    w["saumur"] = b.town(
        "Saumur",
        charter="Noble lord",
        place=anjou,
        summary=(
            "A town grown round a ninth-century fortified monastery built for "
            "the relics of St. Florent, long fought over by the counts of "
            "Blois and Anjou; perhaps in memory of that, tournaments are "
            "held here in the last week of July. Its often-battered castle "
            "was rebuilt again after Philip II took the town in 1203."
        ),
    )
    w["st_florent"] = b.church(
        "Monastery of St. Florent, Saumur",
        church="Monastery or nunnery",
        place=anjou,
        summary="The fortified monastery round which Saumur grew, keeping St. Florent's relics.",
    )
    w["fontevraud"] = b.church(
        "Abbey of Fontevraud",
        church="Monastery or nunnery",
        order="Order of Fontevraud",
        ruler="The abbess, of an Angevin noble family",
        place=anjou,
        founded=1100,
        summary=(
            "A double abbey south of Candes-St-Martin, where a chapel marks "
            "St. Martin's death. A woodland hermit founded it in 1100 for the "
            "men and women who gathered round him, ruled by an abbess, "
            "usually of an Angevin noble house, who guides six separate "
            "communities: contemplative nuns, lay sisters, priests, lay "
            "brothers, lepers and the sick. The Plantagenet tombs are here; "
            "Eleanor of Aquitaine spent her last ten years here and was "
            "buried here in 1204."
        ),
    )
    w["le_puy_notre_dame"] = b.church(
        "Church of Le Puy-Notre-Dame",
        church="Large urban church",
        place=anjou,
        summary=(
            "A church far too big for its village south of Doué, a halt on "
            "the road to Santiago. It holds the Girdle of the Virgin, lately "
            "brought from Jerusalem, a help in childbirth with a Faith score "
            "of 1."
        ),
    )
    w["vendome"] = b.town(
        "Vendôme",
        charter="Noble lord",
        ruler="Count John IV of Montoire",
        answers_to=w["montoire"],
        place=anjou,
        summary=(
            "A town laced with streams where the River Loir splits into "
            "braids, under a castle on the outcrop to the south. Many of the "
            "valley's people live in caves, above all at Trôo, where the poor "
            "live in damp caves at the cliff foot and steps cut in the rock "
            "lead up to the homes of the better-off."
        ),
    )
    w["trinity_vendome"] = b.church(
        "Abbey of the Trinity, Vendôme",
        church="Monastery or nunnery",
        order="Benedictine",
        place=anjou,
        founded=1032,
        summary=(
            "Founded in 1032 by Geoffroy Martel, Count of Anjou, on the spot "
            "where three fiery spears he saw drop from the heavens struck the ground "
            "near a spring. He gave it the arm of St. George (Faith 2) and a "
            "tear Christ wept at the tomb of Lazarus (Faith 3). It is one of "
            "the most powerful religious houses in France. One of the three "
            "spears lies forgotten in its crypt."
        ),
    )


# ---------------------------------------------------------------- Aquitaine


def _aquitaine_places(normandy: Normandy) -> None:
    aquitaine = normandy.places["aquitaine"]
    _place(
        normandy,
        "mount_mercury",
        "Mount Mercury",
        inside=aquitaine,
        summary=(
            "The highest point of the Vendée, the thinly peopled forest, moor "
            "and marsh of north-western Aquitaine, whose trade goes to "
            "Nantes. Its village of St. Michael has a church on the site of a "
            "shrine to Mercury, patron of travellers. Since a maga who sought "
            "out such places identified the old dedication, Redcaps have "
            "come here as pilgrims to honour Mercury or the saint and to "
            "look out over the forest to the ocean."
        ),
        **KNOWN_ORDER,
    )
    _place(
        normandy,
        "vendee_marsh",
        "The Vendée Marshes",
        inside=aquitaine,
        summary=(
            "The greatest of the Vendée marshes, over eighty square miles, "
            "where a few people live by fishing and fowling. Marmoutier's "
            "monks have a priory on higher ground at Sallertaine and there is "
            "a Benedictine abbey at Chauvet. The lord of Montaigu rules it "
            "from La Garnache on its north-eastern edge. The covenant of "
            "Ligurio stood here for about a century; little is left of it, "
            "its buildings sunk into the marsh."
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "demon_cleft",
        "St. Hilary's Demon",
        inside=aquitaine,
        realm="Infernal",
        summary=(
            "Past the pine-held dunes the Vendée coast turns rocky. At the "
            "end of one promontory a cleft runs down to a cave far below the "
            "sea, where a demon is imprisoned: as the surf surges up the "
            "cleft his wailing can be heard, and at high tide in a strong "
            "wind he roars and flings great bursts of spray over the cliffs. "
            "Long ago the sea drowned the low land; the people prayed, and "
            "St. Hilary found the demon behind the floods, caught him and "
            "drove him beneath the waves."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "noirmoutier",
        "Noirmoutier",
        inside=aquitaine,
        aura=3,
        summary=(
            "A low island off the coast just south of the Loire mouth, "
            "marshy in the middle, its southern tail reaching toward the "
            "mainland across a dangerous current. The whole isle has a Magic "
            "aura of 3, rising to 5 at a sheltered north-western beach once "
            "sacred to Gallic druidesses, whose name still keeps people "
            "away. A covenant here would eat well on seafood and could sell "
            "salt from the marshes."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "sevre_marsh",
        "The Marsh of the Sèvre",
        inside=aquitaine,
        summary=secrets(
            "Wide marshland north of La Rochelle about the rivers Vendée and "
            "Sèvre Niortaise, with the fortress of Niort beyond it to the "
            "east and the oak and beech of the Argenson Forest on the hills "
            "to the east and south. Five local abbeys have lately joined to "
            "drain its northern part for farmland.",
            "The drainage will damage or destroy several vis sources the "
            "abbeys know nothing of: moulted tail feathers of pintails "
            "wintering at one pool (Animal, 4 pawns a year); the leaves of an "
            "aspen that quiver in still air (Auram, 3); the oversized cones "
            "of one alder (Creo, 3); plume feathers of egrets nesting in a "
            "certain grove (Imaginem, 2); and the bark of a white poplar "
            "whose black diamond marks are unusually regular (Rego, 4).",
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "bougon",
        "The Bougon Tumuli",
        inside=aquitaine,
        summary=secrets(
            paragraphs(
                "Six grassy mounds of stone and earth hidden in the forest "
                "about halfway between Niort and Poitiers. Locals think them "
                "haunted and keep away; they are an undiscovered pagan "
                "burial ground of great interest to some magi.",
                "Three stand together: a large round mound over a domed "
                "chamber twenty-seven feet across, split by a slab set on "
                "edge; a long barrow with two burial places at each end; and "
                "a smaller round mound seventeen feet high over a chamber "
                "with a rectangular platform. Beyond a low earth bank lie "
                "the other three, with banks enclosing a rectangle about "
                "two hundred and sixty feet long that holds two small oval "
                "mounds, each with a passage to a square chamber; the sixth "
                "mound is entered from the east by a low passage to two "
                "chambers.",
            ),
            paragraphs(
                "A tribe long gone built it for a chieftain, his family and "
                "the retinue that would guard and serve them. Animals or "
                "dark-loving fae may have moved into a mound, or all may be "
                "undisturbed. The large mound holds the scant bones of some "
                "twenty hunters and warriors among scattered stones; the "
                "long barrow is empty; the smaller round mound holds the "
                "broken bones of one dismembered man, a shaman, in a filled "
                "pit by the platform; each small oval mound holds the "
                "remains of a woman with jet bracelets, the chief's "
                "daughters or concubines; and the last mound holds the "
                "chieftain and his wife. At least one mound probably has a "
                "ghost.",
            ),
        ),
        **RUMOURED,
    )
    _place(
        normandy,
        "chassenon",
        "The Roman Baths of Chassenon",
        inside=aquitaine,
        summary=secrets(
            "The ruins of a Roman spa town west of Angoulême. A stretch of "
            "wall and the overgrown temple and theatre can be found by "
            "searching; the baths are easy to find, roofless but with walls, "
            "pools, hypocausts and tunnels, and the whole sequence of "
            "changing room, warm, hot, steam and cold rooms, plunge pools "
            "and exercise hall can still be traced. The healing water holds "
            "Creo vis, but it flows weakly and fitfully.",
            "When Christianity came, the pagan statues were thrown into the "
            "gutters and sewers, then buried when invaders pulled the town "
            "down. If the right god's statue is dug out of the old drains "
            "under the baths and set back in its temple, the water will "
            "flow strongly and steadily again.",
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "vesone",
        "The Spring of Vésone",
        inside=aquitaine,
        summary=(
            "A spring on the south side of the River Isle at Le Cité, sacred "
            "before Christianity. Some locals know of it; it yields Aquam "
            "vis."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "truffle_oaks",
        "The Truffle Oaks of Périgord",
        inside=aquitaine,
        summary=(
            "On the limestone plateaus round Le Cité and south to the "
            "Dordogne, a knobbly fungus grows about the roots of certain "
            "oaks: purplish-black outside, pale and white-veined within, "
            "earthy when fresh and foul when overripe. It is prized as an "
            "aphrodisiac and dug from December to March with pigs or dogs. "
            "The fungus is common, but the rare potent nodules hold Herbam "
            "vis."
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "la_coloubre",
        "La Coloubre's Cave",
        inside=aquitaine,
        summary=(
            "A cave on the south bank of the Dordogne at Lalinde, above "
            "Bergerac, where the river runs through rapids. The dragon La "
            "Coloubre lived here, preying on those who walked round the "
            "rapids, until St. Front killed it and burned the body on the "
            "hill above. A chapel marks the spot and fires are lit there "
            "every year, perhaps a warning that keeps other dragons from "
            "moving in."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "vezere",
        "The Painted Caves of the Vézère",
        inside=aquitaine,
        aura=1,
        summary=secrets(
            paragraphs(
                "The Vézère winds south-west between high limestone cliffs "
                "to join the Dordogne near Limeuil. Hardly anyone lives in "
                "the valley; the only sizeable settlement is St. "
                "Christopher's Rock, halfway along, where folk live on five "
                "levels up the cliff in part-cave houses on ledges reached "
                "by stairs.",
                "A broad Magic aura lies under the lower valley, reaching "
                "out to Rouffignac to the west and along the Beune valley to "
                "the east, and touches the surface at 1 in a few places.",
            ),
            paragraphs(
                "Undiscovered caves and passages run beneath, many painted "
                "or carved with deer, horses, mighty bulls and huge beasts "
                "with great curved tusks; where the pictures are most vivid "
                "the aura is 5 or 6, aligned with Animal. Other caves are "
                "hung with coloured stone, stalactites, stalagmites and "
                "crystal, the finest with auras up to 6, one or two aligned "
                "with Imaginem. Bjornaer of Clan Ilfetu know a cave here "
                "that is an ancestor site, fit for House rituals.",
                "A string of small caves and low passages leads into a regio.",
            ),
        ),
        levels=[
            Builder.level(
                "The fresh paintings",
                3,
                enter="Through a chain of small linked caves and low passages",
                notes=(
                    "There is light enough to see without a lamp, and the "
                    "pictures on the walls look newly made."
                ),
            ),
            Builder.level(
                "The painted land",
                5,
                notes=(
                    "A wide open country of rolling hills, grassy plains, "
                    "dense forest and broad rivers, full of animals, some "
                    "familiar and some known only from the pictures on the "
                    "cave walls."
                ),
            ),
        ],
        **UNKNOWN,
    )
    _place(
        normandy,
        "clermont_grove",
        "The Druids' Grove of Clermont",
        inside=aquitaine,
        summary=secrets(
            "All that is left of the druids' sacred wood where Clermont now "
            "stands is a clump of stunted trees south-west of the cathedral, "
            "beside a market, where a mineral spring soaks the soil.",
            "Some Diedne magi knew of it and found a way into a regio here.",
        ),
        levels=[
            Builder.level(
                "The living grove",
                3,
                enter="Only when the moon is full, both in and out",
                notes=("A healthy grove of trees. A spring inside yields Terram vis."),
            )
        ],
        **UNKNOWN,
    )
    _place(
        normandy,
        "puy_de_dome",
        "The Puy de Dôme",
        inside=aquitaine,
        summary=secrets(
            "An extinct volcano west of the road south from Clermont, its "
            "steep sides forested. The summit shrine was Lug's, then "
            "Mercury's, and is now St. Barnabas's. Locals believe the "
            "sorcerers of the Auvergne meet there at dead of night, a memory "
            "of the Mercurian magicians of Rome. What is left of a Roman road "
            "climbs to the top.",
            "Climbing on foot and keeping exactly to the Roman road crosses "
            "into a small regio. A higher level, where the temple is whole, "
            "and an older route up to Lug's shrine are still undiscovered.",
        ),
        levels=[
            Builder.level(
                "The roofless temple",
                3,
                enter="Climb on foot, staying exactly on the Roman road",
                notes="The temple of Mercury stands abandoned and roofless.",
            ),
            Builder.level(
                "The whole temple",
                0,
                notes=secrets(
                    "Aura not given.",
                    "No one has found this level yet: here the temple is intact.",
                ),
            ),
        ],
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "auvergne_volcanoes",
        "The Auvergne Volcanoes",
        inside=aquitaine,
        summary=paragraphs(
            "The ancient volcanoes west of the Clermont road: the Puy de "
            "Dôme, the Puy de Sancy and the Cantal mountains. Before there "
            "were people, great magical creatures of air, water, earth and "
            "fire fought here and left the dramatic landscape behind them.",
            "Many lovely lakes, waterfalls and strange rocks have low Magic "
            "auras, and some yield vis: a rock at Tuillière shaped like "
            "giant sheaves of wheat holds Creo vis; a polished black basalt "
            "stone cast into Lake Pavin on the longest night of the year "
            "stirs up a fierce storm that leaves several pawns of Auram vis "
            "to collect; at Bort-les-Orgues, pebbles like little loaves and "
            "fruits caught now and then in the hollows called giants' "
            "cauldrons hold Rego vis, and the echo off the grey columns of "
            "rock holds Imaginem vis when the right sound is made.",
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "auvergne_springs",
        "The Hot Springs of the Auvergne",
        inside=normandy.places["auvergne_volcanoes"],
        summary=paragraphs(
            "Hot springs and hot vapours at Royat, le Mont-Dore and la "
            "Bourboule, warmed by a mighty fire elemental that has lived "
            "deep underground for ages. The water eases skin complaints and "
            "aching joints, the vapour chest ailments: half an hour in "
            "either gives +3 to a recovery roll, but longer harms, for the "
            "water and vapour are hot and noxious.",
            "Aquam, Auram, Creo and Ignem vis are gathered here, and the "
            "Tribunal leases them as tropaea.",
        ),
        **KNOWN_TRIBUNAL,
    )


def _aquitaine_world(normandy: Normandy) -> None:
    b = normandy.b
    w = normandy.world
    aquitaine = normandy.places["aquitaine"]

    # The King of England is the duchy part's; he is Duke of Aquitaine too.
    duke = w.get("henry_iii") or b.lord(
        "Henry III of England",
        title="duke",
        wealth="Wealthy",
        seat="England",
        ruler="Henry III",
        summary="The young King of England, Duke of Aquitaine.",
    )
    w.setdefault("henry_iii", duke)
    w["montaigu"] = b.lord(
        "Lord of Montaigu-en-Vendée",
        title="landed",
        wealth="Poor",
        seat="La Garnache",
        answers_to=duke,
        place=normandy.places["vendee_marsh"],
        summary=(
            "The local lord of the great Vendée marsh, who lives in his "
            "castle at La Garnache on the north-eastern fringe of his watery "
            "lands."
        ),
    )
    w["lusignan"] = b.lord(
        "Hugh X of Lusignan, Count of La Marche",
        title="count",
        wealth="Wealthy",
        seat="Lusignan",
        place=aquitaine,
        summary=secrets(
            paragraphs(
                "Head of the house of Lusignan, kin of the old Counts of "
                "Poitiers, whose castle was raised by faerie magic. He is "
                "betrothed to Isabella of Angoulême, King John's widow. A "
                "cadet line holds Parthenay, in a castle the family's "
                "ancestress conjured for her second son.",
                "Legend tells that Raymond, adopted son of a Count of "
                "Poitiers, killed his father by mischance while defending "
                "him from a cornered boar, fled through the forest and came "
                "on three beautiful women by a bubbling spring. One, "
                "Mélusine, married him on condition she spend each Sabbath "
                "alone. Their many children were fine people, each with some "
                "odd mark. Raymond learned she spent that day with a "
                "serpent's tail and kept silent, until, distraught when a "
                "son of theirs who was a monk was murdered in a Norse raid, "
                "he let slip that he knew, and she fled forever. A water "
                "sprite called Mélusine (more than one supernatural woman "
                "has taken the name) appears on the castle walls whenever a "
                "count is about to die or be born.",
                "Story seed: Mélusine stands on the ramparts for days though "
                "the count is well and his wife not with child. A maga is "
                "asked to learn what she wants while the count is kept out "
                "of harm's way.",
                "Story seed: people with the marks of Mélusine's children "
                "(drooping ears and odd-coloured eyes, a red face, one eye "
                "higher than the other, claw-like nails, a missing eye, or "
                "little tusks in the lower jaw) come to the covenant. Each "
                "has Undine Blood and could be worth recruiting; one bears "
                "his ancestress's curse and wants it lifted.",
            ),
            "Mélusine wants help to save her spring, which is being made "
            "into a well for a new convent.",
        ),
    )
    w["angouleme_countess"] = b.lord(
        "Isabella, Countess of Angoulême",
        title="count",
        wealth="Wealthy",
        seat="Angoulême",
        place=aquitaine,
        summary=(
            "The beautiful widow of King John of England, mother of King "
            "Henry III, who holds the county of Angoulême from her castle "
            "there and is betrothed to Hugh X of Lusignan, Count of La "
            "Marche."
        ),
    )
    w["perigord"] = b.lord(
        "Count of Périgord",
        title="count",
        seat="Le Cité",
        answers_to=duke,
        place=aquitaine,
        summary=(
            "Lord of Le Cité, capital of Périgord. He and his city stayed "
            "loyal to King John as Duke of Aquitaine, while the rival "
            "pilgrim town of Le Puy-St-Front took Philip II's side. With the "
            "bishop of Le Cité he contends with the bishop of St. Front for "
            "prestige, influence and taxes."
        ),
    )
    w["auvergne"] = b.lord(
        "Count of Auvergne",
        title="count",
        seat="Montferrand",
        place=aquitaine,
        summary=(
            "The count whose castle at Montferrand, beside Clermont, the "
            "town grew up round. He is the bitter rival of the Lord Bishop "
            "of Clermont and is strengthening Montferrand's walls now."
        ),
    )
    w["couzan"] = b.lord(
        "Lord of Couzan",
        title="baron",
        seat="Couzan Castle",
        answers_to=w["auvergne"],
        place=aquitaine,
        summary=(
            "Ruler of Forez from Couzan Castle: the granite mountains east of "
            "the Livradois forests, moorland summits often lost in mist, "
            "where women and children summer with the herds while the men "
            "farm the valleys."
        ),
    )
    w["castillon"] = b.lord(
        "The de Castillon family of Aubeterre",
        title="landed",
        seat="Aubeterre-sur-Dronne",
        place=aquitaine,
        summary=(
            "Owners of the castle on the cliff above Aubeterre's monolithic "
            "church, joined to its gallery by a steep passage. The crusader "
            "Pierre de Castillon brought back relics of the Holy Sepulchre "
            "that are said to be kept in the church's hexagonal shrine."
        ),
    )
    w["de_born"] = b.lord(
        "The de Born family of Hautefort",
        title="landed",
        seat="Hautefort",
        place=aquitaine,
        summary=secrets(
            "The castle of Hautefort, east of Le Cité. The troubadour "
            "Bertrand de Born, a favourite of Henry II, who gave him the "
            "castle in 1185, quarrelled over it with his jealous brother "
            "Constantine, who with the help of Henry's son Richard ruined it "
            "the next year.",
            "Bertrand's music had a supernatural gift; his brother had "
            "something darker and more destructive, and magic probably "
            "brought the fortress down.",
        ),
    )

    w["la_rochelle"] = b.town(
        "La Rochelle",
        charter="Commune",
        answers_to=duke,
        place=aquitaine,
        summary=(
            "A walled port trading with England and Flanders, chartered as "
            "independent in 1199. Its ownership is disputed between France "
            "and England; it is English for now (history has it fall to "
            "France after a siege in 1224). It has a castle, a mint, a "
            "Templar church and a nunnery of St. Catherine."
        ),
    )
    w["poitiers"] = b.town(
        "Poitiers",
        charter="Noble lord",
        place=aquitaine,
        summary=paragraphs(
            "The city stands on a promontory between the Boivre and the "
            "Clain, the oldest Christian community of the region and still a "
            "great church centre: the fourth-century Baptistery of St. John, "
            "where until the last century every baptism in the city was "
            "held, its Dominion aura faded to 4; the splendid Church of Our "
            "Lady the Great; the unfinished Cathedral of St. Peter; the "
            "Cluniac abbey of Montierneuf; the Abbey of the Holy Cross; and "
            "the Church of St. Hilary, its most famous bishop, whose relics "
            "are venerated there.",
            "North of the city Charles Martel turned back the Moors.",
        ),
    )
    w["st_hilary_poitiers"] = b.church(
        "Church of St. Hilary, Poitiers",
        church="Large urban church",
        place=aquitaine,
        summary=(
            "Keeps the relics of St. Hilary, doctor of the Church and the "
            "most famous bishop of Poitiers, who in legend chained the "
            "demon of the Vendée coast under the sea."
        ),
    )
    w["poitiers_cathedral"] = b.church(
        "Cathedral of St. Peter, Poitiers",
        church="Bishop's cathedral",
        place=aquitaine,
        summary="The bishop's church of Poitiers, still under construction.",
    )
    w["liguge"] = b.church(
        "Abbey of Ligugé",
        church="Monastery or nunnery",
        place=aquitaine,
        founded=361,
        summary=(
            "Just south of Poitiers, the oldest monastery in the west, "
            "founded by St. Martin in 361 when he came to learn the faith "
            "from St. Hilary and stayed ten years. A tiny, very old basilica "
            "on the ruins of his Gallo-Roman villa has a Dominion aura of 5."
        ),
    )
    w["marsh_abbeys"] = b.faction(
        "The Five Abbeys of the Marsh",
        faction="Other",
        decides="A council",
        members=5,
        place=normandy.places["sevre_marsh"],
        wants="More farmland, and the wealth it brings",
        summary=(
            "Five abbeys near La Rochelle that have joined to drain the "
            "northern part of the marsh of the Vendée and Sèvre for "
            "cultivation. They do not know the work threatens several vis "
            "sources."
        ),
    )
    w["angouleme"] = b.town(
        "Angoulême",
        charter="Noble lord",
        ruler="Isabella, Countess of Angoulême",
        answers_to=w["angouleme_countess"],
        place=aquitaine,
        summary=(
            "A walled city on a promontory over the River Charente, with a "
            "cathedral of St. Peter built last century and the countess's "
            "castle; houses and workshops cluster round the little port "
            "outside the walls."
        ),
    )
    w["limoges"] = b.town(
        "Limoges",
        charter="Church",
        place=aquitaine,
        summary=paragraphs(
            "Two rival settlements: the Cité, the church quarter round the "
            "Cathedral of St. Stephen near the Vienne, with a new bridge of "
            "1210 and a temple of Jupiter under the cathedral; and the "
            "market town on the slopes round the castle and the Abbey of St. "
            "Martial, which got its own bridge in 1215.",
            "South at Solignac is the great monastery St. Eligius founded in "
            "632 (a Limoges goldsmith who became King Dagobert's adviser); "
            "west at Noblat is the Monastery of St. Léonard, Clovis's godson "
            "who lived as a forest hermit there.",
        ),
    )
    w["st_martial"] = b.church(
        "Abbey of St. Martial, Limoges",
        church="Monastery or nunnery",
        order="Benedictine",
        place=aquitaine,
        summary=(
            "Built over the burial ground where St. Martial, who converted "
            "the region, lies; his relics are here, three more churches "
            "stand round his tomb for the pilgrim crowds, and its "
            "scriptorium is famed for splendid work."
        ),
    )
    w["saintes"] = b.town(
        "Saintes",
        charter="Noble lord",
        place=aquitaine,
        summary=(
            "A regional capital on the Charente, where the Roman bridge "
            "carries the votive Arch of Germanicus and a near-constant "
            "stream of traffic, many of them pilgrims to Santiago, who lodge "
            "west of the river at the Monastery of St. Eutrope or east of it "
            "at the Ladies' Abbey of St. Mary. The town clusters round the "
            "Cathedral of St. Peter west of the river; the Roman town lay on "
            "the hill to the east."
        ),
    )
    w["st_emilion"] = b.town(
        "St-Émilion",
        charter="Commune",
        ruler="The Jurade",
        place=aquitaine,
        summary=paragraphs(
            "A walled hillside town on the north bank of the Dordogne, "
            "founded in the eighth century by Émilion, a Breton monk who "
            "made his hermitage here, and ringed by vineyards making the "
            "best red wine in the land. Richard I made it a self-governing "
            "commune to protect the wine trade with England; the Jurade, an "
            "assembly of citizens, oversees justice, taxes, defence and the "
            "quality of the wine. By the market a church has been dug out "
            "round the hermit's cave, about a hundred and thirty feet long, "
            "sixty-five wide and up to thirty-five high, in three aisles of "
            "square pillars, and catacombs honeycomb the soft rock below.",
            "North-west at Blaye on the Gironde is Rudel castle, birthplace "
            "a century ago of the troubadour Geoffroy Rudel, who sang of "
            "courtly love and lived it, devoted to the distant Countess "
            "Hodierna of Tripoli.",
        ),
    )
    w["le_cite"] = b.town(
        "Le Cité",
        charter="Noble lord",
        ruler="Count of Périgord",
        answers_to=w["perigord"],
        place=aquitaine,
        summary=(
            "Capital of Périgord in fertile wooded country on the River Isle, "
            "among the remains of the Roman city of Vesunna. St. Front "
            "converted the land and built St. Stephen's Cathedral over a "
            "temple of Mars. The city is fiercely at odds with neighbouring "
            "Le Puy-St-Front."
        ),
    )
    w["le_puy_st_front"] = b.town(
        "Le Puy-St-Front",
        charter="Commune",
        place=aquitaine,
        summary=(
            "A town of pilgrims and trade grown up on the hilltop beside Le "
            "Cité where St. Front was buried, round a Byzantine-style "
            "basilica over his tomb. In the latest round of its rivalry with "
            "Le Cité it sided with Philip II."
        ),
    )
    w["st_front"] = b.church(
        "Basilica of St. Front",
        church="Large urban church",
        place=aquitaine,
        summary=(
            "The Byzantine-style basilica over St. Front's tomb at Le "
            "Puy-St-Front, whose bishop vies with the bishop of Le Cité and "
            "the Count of Périgord for prestige, influence and taxes."
        ),
    )
    w["brantome"] = b.church(
        "Abbey of Brantôme",
        church="Monastery or nunnery",
        order="Benedictine",
        place=aquitaine,
        founded=769,
        summary=(
            "A rich abbey under the cliffs of the Dronne north of Le Cité, "
            "founded by Charlemagne in 769 with a relic of St. Sicaire. The "
            "monks have taken over the Fountain of the Rock, a pagan spring "
            "in the cliff caves, where pilgrims bathe sickly infants."
        ),
    )
    w["aubeterre"] = b.church(
        "Monolithic Church of Aubeterre",
        church="Parish church",
        place=aquitaine,
        summary=(
            "Beside the Dronne at Aubeterre (whose Church of St. Jacques has "
            "a zodiac carved round its west door), monks are finishing a "
            "church cut from a single block of rock; it has a gallery, side "
            "chapels holding tombs and a pool for baptisms. A six-sided shrine "
            "cut from the same rock is said to hold relics of the Holy "
            "Sepulchre."
        ),
    )
    w["bergerac"] = b.town(
        "Bergerac",
        charter="Noble lord",
        place=aquitaine,
        summary=(
            "A crossing and wine port on the north bank of the Dordogne "
            "where the river opens into a wide valley, with vineyards behind "
            "the town; Nidi lies barely an hour's walk away. Upstream past "
            "the rapids of Lalinde and the two great loops, a chapel of St. "
            "Martin near Limeuil, finished in 1194, was paid for by Henry II "
            "in penance for Becket's murder and completed by Richard I."
        ),
    )
    w["clermont"] = b.town(
        "Clermont",
        charter="Church",
        ruler="The Lord Bishop of Clermont",
        place=aquitaine,
        summary=(
            "A city of black local stone ruled by its Lord Bishop, with a "
            "basilica and a cathedral both of Our Lady and over thirty "
            "churches and chapels. The count's town of Montferrand stands "
            "beside it, and the two rulers are bitter rivals. South of it a "
            "road runs between vast upland forests: the Livradois and Forez "
            "to the east, the volcanoes to the west."
        ),
    )
    w["clermont_bishop"] = b.church(
        "The Lord Bishop of Clermont",
        church="Bishop's cathedral",
        ruler="The Lord Bishop of Clermont",
        place=aquitaine,
        summary=(
            "Lord of Clermont as well as its bishop, from his cathedral of "
            "Our Lady. His feud with the Count of Auvergne in Montferrand is "
            "a trap for any magus or covenant caught misusing magic or "
            "breaking the law: each side would gladly buy silence with "
            "magical help against the other, and both may try it."
        ),
    )
    w["montferrand"] = b.town(
        "Montferrand",
        charter="Noble lord",
        ruler="Count of Auvergne",
        answers_to=w["auvergne"],
        place=aquitaine,
        summary=(
            "The town grown up round the Count of Auvergne's castle beside "
            "Clermont, its walls being strengthened against the bishop."
        ),
    )
    w["chaise_dieu"] = b.church(
        "Abbey of St. Robert, La Chaise-Dieu",
        church="Monastery or nunnery",
        order="Benedictine",
        ruler="The abbot, answerable only to the Pope",
        place=aquitaine,
        summary=(
            "The most powerful lordship of the southern plateau: an abbey "
            "of some three hundred monks whose abbot answers directly to the "
            "Pope and heads more than two hundred priories in France, Spain "
            "and Italy."
        ),
    )
    w["brabancons"] = b.faction(
        "The Brabançons",
        faction="Other",
        decides="Its leader",
        place=aquitaine,
        wants="Pay, or plunder where there is none",
        offers="Hardened soldiers, horsemen and crossbowmen for hire",
        summary=paragraphs(
            "Bands of skilled, disaffected soldiers, named for the duchy of "
            "Brabant east of Flanders, who roam and blight the south of the "
            "Tribunal. In 1179 Pope Alexander III put freebooters under the "
            "ban against heretics, naming the Brabanters and "
            "excommunicating any who hired or harboured them; few heeded "
            "it. Philip of France used a troop against troublesome vassals "
            "such as the count of Sancerre, then sent it to aid the Young "
            "King Henry against his father; on the way to Limoges it "
            "massacred Noialle and took its wealth, and when the rebel could "
            "not pay, it turned to sacking monasteries.",
            "Atsingani's turb is largely Brabançon.",
        ),
    )
    w["capuchonnes"] = b.faction(
        "The Capuchonnes",
        faction="Other",
        place=aquitaine,
        summary=(
            "A movement begun in the 1180s by Durand, a freeman of Le Puy, "
            "to wipe out the brigands and bring peace. Its members wore a "
            "set hood and dress and swore to live soberly, without gambling "
            "or taverns; nobles, abbots and bishops joined, and it spread "
            "across southern France and southern Aquitaine, massacring three "
            "thousand brigands in the Auvergne in 1183, among them the "
            "father of Jacques of Atsingani. It soon turned to robbing the "
            "rich and keeping the spoils."
        ),
    )


# ---------------------------------------------------------------- Oleron


def _oleron(normandy: Normandy, tribunal: Tribunal) -> None:
    b = normandy.b
    isle = _place(
        normandy,
        "oleron_isle",
        "The Isle of Oléron",
        inside=normandy.places["aquitaine"],
        summary=paragraphs(
            "A small island in the Bay of Biscay known for its fishers and "
            "traders, many of whose sailors roam the coasts. Its people know "
            "the Apple Mile is there, over the north of the island and the "
            "sea about it, and generally keep clear of its folk.",
            "The way in is an orchard of small, sour apples, long shunned as "
            "unlucky: the challenge ground where the Queen's champion is "
            "fought for.",
        ),
        levels=[
            Builder.level(
                "The Apple Mile",
                5,
                "Faerie",
                enter=(
                    "Through the orchard of sour apples, the challenge ground "
                    "on the mortal side"
                ),
                notes=secrets(
                    "A summer that never ends: a splendid castle where the "
                    "magi and their chief servants live, a harbour town for "
                    "the lesser servants, fields running out into an endless "
                    "orchard of sweet apples, and the covenant's own sea. "
                    "Roads seem to lead away but loop back after long "
                    "detours; only two go anywhere, one to the mortal world "
                    "and one to the Stone Couches, the earth-covered stone "
                    "cenotaphs of the Sleepers.",
                    "The link to the mortal world fails if the champion does "
                    "not answer a challenge by sunset of the next day.",
                ),
            )
        ],
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A covenant descended from a faerie court of Arthur's day, whose "
        "Merinita magi love tales of deeds of arms, passionate wooing and "
        "tragic death, and take an unusual interest, for their House, in "
        "certamen and in the lives of their peasants. It lies in the Apple "
        "Mile, a Faerie regio (aura 5) over the north of the Isle of Oléron, "
        "where it is always summer; the leadership is fought for at the "
        "orchard that joins it to the mortal world. It has five magi, three "
        "of them Merinita, and is one of the five great liege lines of the "
        "Tribunal.",
        "In Arthur's time the young knight Lanval won the love of Triamour, "
        "Faerie Queen of Oleron, and after love lost and found was taken to "
        "live there forever. Arthur's knights might challenge him at the "
        "regio's entrance any Midsummer's Day; none won, and in time the "
        "place was forgotten except in songs. In 1028 Kherion of Merinita "
        "found it, beat Lanval and married his daughter, by then Queen of "
        "the Court of the Apple Mile. Its isolation and the might of its "
        "Sleepers have let it take part in the Order's crises without "
        "reprisal. Caprican of Merinita, consort of Triamour's "
        "great-granddaughter, rules it now.",
        "A faerie queen, who embodies the land, rules with her magus "
        "consort and his council, which takes in most of the magi. The "
        "folk are humans and faeries from many lands and ages, for faeries "
        "have carried people off to the Apple Isle for thousands of years, "
        "and abductees, their faerie doubles and their descendants mingle "
        "in a colourful culture that each new queen bends to her liking. "
        "The place mixes real chivalry with modern romances of the past, "
        "and a magus who knows history sees the seams: a castle no Roman "
        "could have built, Lanval's arms on ancient things from before "
        "knights bore arms, and his armour in the hall too modern and too "
        "bright. The magi share the romantic feudalism, are keener on war "
        "than most Merinita, and look after their common folk with noble "
        "condescension.",
        "The champion's seat is won by challenge: whoever would claim it "
        "sinks an axe into an apple tree ringing the challenge ground on "
        "Midsummer's Day, which the queen feels at once, and the champion "
        "must meet him in a contest of arms before sunset the next day; it "
        "need not be to the death, and lately certamen has served. A "
        "beaten or fleeing challenger must apologize and perform a hard "
        "task the queen sets, enforced by the site as a Rego Mentem effect "
        "of Penetration 75 (never suicidal, but very hard for a "
        "battle-hardened magus). A victor must marry the queen's daughter, "
        "who becomes queen at the wedding; if there is none, one appears, "
        "grown and with a lifetime's memories, the next evening, and the "
        "faeries and every human without Magic Resistance remember her "
        "life. Refusing the marriage counts as defeat. Old consorts and "
        "queens usually stay; some queens travel to the great faerie courts "
        "and Merinita covenants, and some old consorts let their Parma "
        "lapse to remember the life they are supposed to have led.",
        "The Stone Couches are the Queen's power alone: tumuli that, like "
        "kilns, grow faerie copies of folk heroes. A skeleton forms in "
        "three years and flesh over eighteen more, when the Sleeper begins "
        "to breathe; its Might keeps growing, slowly after a century and a "
        "half, and its powers are what the folk of the Atlantic shores "
        "believe of the hero. Sleepers wake when the covenant is in danger, "
        "at the queen's call, or when something suits their story, and "
        "the covenfolk say all will one day wake for a last battle against "
        "an unnamed evil. A Sleeper who stays awake leaves his Couch "
        "growing a duplicate with all his memories. An ordinary human "
        "buried in a Couch becomes a minor faerie copy of himself, a fate "
        "faerie magi think beneath them.",
        "Oberon is the best-known: begun centuries ago as a faerie "
        "Alberich, the magician brother of Merovech, he was remade when "
        "the Capetians made that story useless and the magi spread the "
        "song of Huon of Bordeaux, in which a dwarf-king Oberon helps Huon "
        "through his impossible penance at the court of the Amir of "
        "Babylon. Once the song caught on, the Queen woke him for good. He "
        "looks like the most beautiful three-year-old ever born, which "
        "limits him in towns, and is called the son of Julius Caesar and "
        "Morgan le Fay; his horn banishes hunger and thirst, heals, draws "
        "people to it willy-nilly and lightens hearts, he captures the will "
        "of those who talk to him, and he is a master of illusion. A second "
        "Oberon now grows on his Couch, oddly taller than a man.",
        "Oleron prefers vassals with strong defences and treats vassalage "
        "as trade: surplus vis from the regio for mundane goods the vassals "
        "obtain, beside what it buys through House Mercere. It has lately "
        "taken weaker vassals too, to profit from Fudarus's troubles, and "
        "it fears House Tytalus, whose easiest way to strike at the "
        "unassailable regio is through weak vassals outside it.",
    )
    what_matters = _lines(
        "Vis: surplus vis harvested in the Apple Mile, traded to vassals for mundane goods (kinds and amounts not given)",
        "Income: the vassals' mundane goods, and purchases through House Mercere",
        "Boon: Regio (Major): the Apple Mile, a Faerie regio of aura 5",
        "Boon: Fantastic Environment: an endless summer, looping roads and the covenant's own sea",
        "Boon: Natural Fortress: any invader faces every Sleeper, some made for home defence",
        "Boon: Inhuman Residents: faeries and the Sleepers of the Stone Couches",
        "Boon: Faux Feudalism: ruled by the faerie queen and her champion consort",
        "Hook: Faerie Aura",
        "Hook: Hermetic Politics: liege of Nidi; at odds with Fudarus and House Tytalus",
        "Tension: the champion's seat is open to any challenger on Midsummer's Day; an unanswered challenge would cut the regio off",
        "Tension: magi explore the looping roads and the sea for another way out, to the world or to Arcadia, without success",
        "Tension: censured by the chief Quaesitor of Stonehenge for trying to rescue Eleanor of Aquitaine from captivity",
        "Tension: the Keepers of a Thousand Tales dislike the Stone Couches for fixing stories to one place and one version",
        "Mundane: can raise gangs of sailors from the isle to make trouble in Paris, but keeps no agents there",
    )
    hidden = _lines(
        "Caprican has helped other covenants claim Fudarus's resources while Fudarus is weak, and has added and fortified vassals; if House Tytalus learns of it there will be reprisals once it unites behind a Primus.",
        "One ancient Sleeper, older than the Hermetic colony, may be a mighty faerie Ogier the Dane, Charlemagne's paladin whom Morgan le Fay kept two hundred years in Avalon with a rejuvenating ring and a crown of forgetfulness. He has woken and escaped at least once and might again if disaster strikes Denmark; Rhine and Norman magi who dream of colonising Denmark would like his help, but he is hard to control and would likely seek service with Philip II. Whoever puts on the ring he wears dies at once, his place taken by a faerie that believes it is, and may be, his spirit.",
        "The prophecy of a last battle may itself be a story planted to wake every Sleeper at the covenant's hour of need.",
        "Nidi's weakness is a lure Oleron built for Tytalus: Oleron can reinforce it by rapid travel magic and stocks it with hidden resources.",
    )
    oleron = b.covenant(
        "Oleron",
        tribunal=tribunal,
        founded=1028,
        place=isle,
        level=1,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=5,
        realm="Faerie",
        unnamed_magi=2,
        season="Autumn",
    )
    normandy.covenants["oleron"] = oleron
    normandy.tenure(
        "The surplus vis of the Apple Mile (kinds and amounts not given)",
        oleron,
        "seisin",
        notes="Harvested in the covenant's own regio and traded to its vassals.",
    )
    _oleron_magi(normandy, b, oleron)
    b.book(
        oleron,
        "Oleron's library",
        "Other",
        description=(
            "The book names no titles. Quintinus inherited the laboratory "
            "of a dead member skilled in magical brewing, and the covenant "
            "keeps the Queen's designs for the Stone Couches, which he will "
            "not discuss."
        ),
    )
    w = normandy.world
    w["keepers_of_tales"] = b.faction(
        "The Keepers of a Thousand Tales",
        faction="Gild",
        place=isle,
        wants="Stories kept alive in Arcadia",
        summary=(
            "A Merinita society devoted to seeing that stories live on in "
            "Arcadia, with a particular interest in Arabic tales. Caprican "
            "of Oleron is an active and controversial member: he does not "
            "share the Arabic focus, and those who know of the Stone Couches "
            "think them opposed to the society's aim, since they fix a story "
            "to one place and one version."
        ),
    )


def _oleron_magi(normandy: Normandy, b: Builder, oleron: Covenant) -> None:
    m = normandy.magi
    m["caprican"] = b.magus(
        "Caprican of Merinita",
        covenant=oleron,
        house=MERINITA,
        age=92,
        traits={
            "Loves Wife and Family": 4,
            "Proud": 3,
            "Suspicious of Tytalus Magi": 2,
        },
        summary=secrets(
            paragraphs(
                "Leader and champion of Oleron, apparently about fifty-five, "
                "who fought as a mercenary in the wars of the faerie courts in "
                "his youth. The last champion, afraid of dying unbeaten "
                "(with unknown results), asked him to take the seat. His "
                "wife is the faerie queen Lysette and he has an infant "
                "daughter, Columbine, whose birth tells him he will likely "
                "lose the seat within a few decades.",
                "He follows other magi's careers and gossip closely to guess "
                "who his heir will be, and may groom a likely candidate. He "
                "dislikes Tytalus magi and would use Wizard's War, even war "
                "between covenants, to stop his heir coming from that "
                "House, for his daughter must love whoever wins her, and he "
                "cannot see how a woman could be happy wed to a creature of "
                "strife.",
                "He has Strong Faun Blood, and his magic bends the emotions "
                "of people and animals. He belongs to the Keepers of a "
                "Thousand Tales.",
            ),
            "While Fudarus is empty and its leaders feud, he has helped "
            "other covenants take its resources and has added and fortified "
            "vassals. He expects reprisals if Tytalus finds out, and is "
            "untroubled: with Ushant so near, attacks will come anyway.",
        ),
    )
    m["amelie"] = b.magus(
        "Amelie of Merinita",
        covenant=oleron,
        house=MERINITA,
        age=33,
        traits={"Curious": 3, "Meddlesome": 2},
        summary=paragraphs(
            "Oleron's usual spokeswoman and traveller. She is short and "
            "slight; river-nymph blood leaves her naturally bald, which she "
            "hides with illusory blonde hair, and her fingers and toes are "
            "webbed, so she always wears mittens and shoes in public.",
            "She is no great negotiator and knows it, so she lets deals fail "
            "or sends partners to Caprican, and uses her office mostly as an "
            "excuse to see interesting places and people. Her magic is "
            "Aquam, above all the making of unnatural liquids.",
        ),
    )
    m["quintinus"] = b.magus(
        "Quintinus of Verditius",
        covenant=oleron,
        house=VERDITIUS,
        age=40,
        traits={"Self-effacing": 2, "Enthusiastic": 2},
        summary=paragraphs(
            "An odd Verditius, apparently thirty-five, drawn to Oleron by "
            "magical brewing, especially with cider; when a member skilled "
            "in such things died he asked to join and take over the dead "
            "magus's laboratory. He now builds the new Stone Couches to the "
            "Queen's design, finds it far more rewarding than making "
            "enchanted items, and may soon ask to change Houses.",
            "He stays out of his House's games of status, which spares him "
            "his Housemates' enmity, but his silence about the Couches makes "
            "him look idle or incompetent, and his standing in the House is "
            "very poor.",
        ),
    )


# ---------------------------------------------------------------- Nidi


def _nidi(normandy: Normandy, tribunal: Tribunal) -> None:
    b = normandy.b
    w = normandy.world
    site = _place(
        normandy,
        "nidi_manor",
        "Lord Henri's Manor and Chase",
        inside=normandy.places["aquitaine"],
        summary=secrets(
            paragraphs(
                "A small castle and its manor in farmland an hour's walk "
                "from Bergerac, once lightly wooded and far from any town. "
                "South and east, the woods have been felled to make "
                "fields; to the west is the waste, woodland where peasants "
                "forage their beasts and gather wood; to the north is the "
                "chase, kept for the lord's hunting and patrolled by his "
                "men. In the chase stand wax statues of classical heroes.",
            ),
            "The chase hides a grove of oaks, perhaps druidic, overgrown by "
            "huge lilacs always in flower whose blossoms yield Herbam vis; "
            "the statues are the work of Regulus's bees.",
        ),
        **KNOWN_LOCALLY,
    )
    labs = _place(
        normandy,
        "nidi_riverbank",
        "The Riverbank Laboratories",
        inside=site,
        realm="Faerie",
        aura=1,
        summary=secrets(
            "A clay bank on the river, half a mile north of the castle, once a water "
            "nymph's home, with a weak Faerie aura. A hollow tree full of "
            "bees stands there, and their stings keep the locals away.",
            "Nidi's laboratories are dug into the bank. Most entrances suit "
            "something smaller than a man; the one a human can use is "
            "through the bee-infested tree.",
        ),
        **UNKNOWN,
    )
    summary = paragraphs(
        "Conventio Nidi, the nest: Bjornaer and Merinita magi who, unlike "
        "most of their kind, do not see towns as wasteland. As towns grow "
        "into cities and their communities fragment, wildness creeps back "
        "into the cracks, and Nidi seeks such niches. It has no mark of its "
        "own and uses the badge of Henri, the nobleman who serves it. It "
        "takes a new name with each new leader; Nidi refers to Micropedus's "
        "starling heartbeast.",
        "Oleron founded it as a vassal in 1100 in light woodland far from "
        "any settlement. In the twelfth century the land was cleared for "
        "crops and the port of Bergerac grew up barely an hour away; most "
        "of the Merinita members left for wilder places, and the two who "
        "stayed, Regulus of Merinita and Micropedus of Bjornaer, chose to "
        "embrace the towns. Luna of Bjornaer joined lately. It lies south "
        "of the Dordogne line but is older than the 1103 ruling, so it "
        "belongs to Normandy.",
        "The magi live and hold council in Lord Henri's small castle, which "
        "was once the covenant's main building. When clearing made "
        "discovery certain, the magi recruited Henri's father as their "
        "nominal overlord: the family holds mundane title to the covenant's "
        "lands, hides the magi from other landowners, gives them shield "
        "grogs, and keeps the key sites as a chase its men patrol, which "
        "should keep settlement and the Dominion off them. Henri knows his "
        "guests are wizards; for his hospitality and services he is "
        "promised a long, healthy old age. He is proud, so the magi ask and "
        "never order, and though he has never refused, being treated like a "
        "grog would rankle.",
        "Their philosophy is the starling's: a wild bird that nests in the "
        "eaves of houses, sheltered by people who drive off its predators, "
        "and lives on what they overlook. A few magi, Micropedus argued, "
        "can do the same: live unnoticed in the spaces mundanes ignore, "
        "draw unwitting protection from them and live as parasites on "
        "their communities. They see themselves as pioneers of urban "
        "territory and want more members, knowing Micropedus is near his "
        "end.",
    )
    what_matters = _lines(
        "Vis: the lilac-grown oak grove in the chase, Herbam vis from the flowers; Regulus can turn it into honey holding Animal vis, losing a third",
        "Vis: pays its tithes openly, through the Redcaps and at Tribunal, for show",
        "Boon: Tame Nobleman: Lord Henri, who hosts the magi and holds their lands",
        "Boon: Hidden Resources: unused magic items, copies of a strong Aegis, servants trained by awakened Sleepers",
        "Hook: Urban: close beside farmland and the port of Bergerac, and seeking niches in towns",
        "Hook: Beholden: vassal of Oleron",
        "Tension: the faeries driven out by the Dominion may come back in hardier forms; losing the riverbank laboratories or the grove in the chase could finish the covenant",
        "Tension: Micropedus is close to Final Twilight; his weather magic keeps the district prosperous",
        "Tension: Henri's only child Lila must marry a man the covenant can manage, and be happy, or the arrangement fails; Henri will soon want a longevity potion",
        "Tension: a girl found as a baby in a wild hive a few days south may be a Bee Queen; Regulus wants her raised far away",
    )
    hidden = _lines(
        "Nidi's weakness is deliberate. Oleron means it to look a fit target for House Tytalus once the Tytalan civil war ends and its magi go back to provoking the Tribunal: Tytalus magi who attack it in earnest will underestimate it, be driven off and be exposed before the Tribunal.",
        "Its hidden resources: many small magic items it never uses, several copies of a remarkably strong Aegis of the Hearth, and servants whom awakened Sleepers have trained. Its magi may use them only with Oleron's leave or against magi of Fudarus, and Oleron can reinforce it quickly by travel magic.",
        "For over thirty years its tithes have been repaid, or traded at good rates for other vis, by Oleron.",
        "Its magi are promised places in Oleron or another of its vassals should Nidi fall.",
    )
    nidi = b.covenant(
        "Nidi",
        tribunal=tribunal,
        founded=1100,
        place=labs,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=1,
        realm="Faerie",
    )
    normandy.covenants["nidi"] = nidi
    normandy.tenure(
        "The lilac grove in Lord Henri's chase (Herbam; amount not given)",
        nidi,
        "seisin",
        notes="The source that justified the covenant's founding.",
    )
    w["lord_henri"] = b.lord(
        "Lord Henri",
        title="landed",
        seat="His castle near Bergerac",
        place=site,
        summary=secrets(
            paragraphs(
                "A minor nobleman of Aquitaine whose small castle and manor "
                "near Bergerac shelter the magi of Nidi. His father was "
                "recruited as the covenant's nominal lord; Henri knows his "
                "guests are wizards and serves them as host and shield in "
                "return for a long and healthy old age. He keeps his pride: "
                "the magi make requests, never give orders.",
                "Story seed: Henri has one child, his daughter Lila, and "
                "insists on her happiness. Young magi of Nidi might tour "
                "covenants that hide behind mortal families so she can "
                "choose a husband, or another covenant's magi might bring a "
                "servant to Nidi as a suitor.",
            ),
            "The covenant needs Lila to marry a man it can steer. Once Henri "
            "takes his longevity potion he will age too slowly: cosmetics "
            "will serve a few decades, then illusions, and in true old age "
            "he must be hidden away. Mythic Europe holds others like him, and "
            "the covenant could be asked to find a place for one who has "
            "become inconvenient.",
        ),
    )
    _nidi_magi(normandy, b, nidi)
    b.book(
        nidi,
        "Nidi's library",
        "Other",
        description=(
            "The book names no titles. Micropedus has written at length on "
            "his philosophy of small covenants living in the overlooked "
            "spaces of towns, which many of his Bjornaer sodales reject."
        ),
    )


def _nidi_magi(normandy: Normandy, b: Builder, nidi: Covenant) -> None:
    m = normandy.magi
    m["regulus"] = b.magus(
        "Regulus of Merinita",
        covenant=nidi,
        house=MERINITA,
        age=72,
        traits={"Joyful": 3, "Fierce": 2},
        summary=secrets(
            paragraphs(
                "The Bee King: blond, amber-eyed and golden-skinned, "
                "smelling faintly of candles, and looking no more than "
                "twenty-one. His looks come of Strong Faerie Blood: he is a "
                "Bee King, a creature so rare that some Merinita think one "
                "is made when a young woman swallows a drone from a faerie "
                "hive, the steeds of the tiny knights of a sprite queen whose "
                "court wanders Mythic Europe.",
                "A Bee King never seems to age but dies of a swift illness a "
                "century after birth if nothing kills him first. He can "
                "command any bees to do anything they can, even to their "
                "deaths, gives long messages through a bee on his tongue, "
                "understands hives and reads the bees he touches, and is "
                "never stung. He turns the grove's Herbam vis into honey "
                "holding Animal vis, and his bees build the wax statues in "
                "the chase.",
            ),
            "Two Bee Kings can never meet: if Regulus comes within scent of "
            "the hive-girl he will fall into a murderous rage and have to "
            "kill her. She is the child of faeries like him, or his own by "
            "some forgotten affair; he wants her raised happily far away, "
            "and watched, for he has never heard of a human Bee Queen.",
        ),
    )
    m["luna"] = b.magus(
        "Luna of Bjornaer",
        covenant=nidi,
        house=BJORNAER,
        age=26,
        traits={"Sly": 3, "Shy": 1},
        summary=paragraphs(
            "A noble rat. Born in Sicily of mixed Italian and Arab stock, "
            "dark-haired and dark-eyed and just under five feet tall, she "
            "dresses in few layers so as to slip in and out of her "
            "heartbeast. She has no talisman yet and is looking for "
            "something to enchant.",
            "She trained first in the Beast Master tradition of House Ex "
            "Miscellanea; Micropedus drew out her heartbeast and got her "
            "accepted, if not respected, in his House, whose members think "
            "a rat heartbeast freakish. She thinks rats noble: sneaky, "
            "tenacious, hardy and made for living beside wasteful humans. "
            "Micropedus grooms her as his heir. At least an hour a week, "
            "and whenever she is stressed, she sits as a rat on a rafter of "
            "the covenant's granary gazing at more food than a rat could eat "
            "in a century.",
            "Animal is her best Art, the rest learned piecemeal for useful "
            "tricks. She has mastered a spell to tunnel through stone or "
            "wood in rat form. Her combat spells are weak, but she can still "
            "call and command animals and defends herself with hordes of "
            "rats.",
        ),
    )
    m["micropedus"] = b.magus(
        "Micropedus of Bjornaer",
        covenant=nidi,
        house=BJORNAER,
        age=93,
        traits={"Determined": 3, "Fidgety": 1},
        summary=paragraphs(
            "The Starling, Nidi's leader, apparently sixty. He spends much "
            "of his time as a bird and finds it ever harder, slower and more "
            "painful to change back as his Warping grows; a Twilight Scar "
            "leaves patches of feathers on his scalp in human form. His "
            "name, small feet, comes from another scar: his heartbeast looks "
            "like the footless starling of folklore, and his feet have "
            "shrunk with age to a child's; he suspects they will drop off "
            "when he enters Final Twilight.",
            "The idea that small covenants can live in the uncharted spaces "
            "of towns is his. He has written on it at length and trained a "
            "few apprentices, though many Bjornaer reject it. An Auram magus "
            "skilled at weather, he breaks droughts with rain and kills "
            "grain blight with frost; the prosperity this brought is "
            "arguably why a town grew so close to the covenant.",
        ),
    )


# ---------------------------------------------------------------- Atsingani


def _atsingani(normandy: Normandy, tribunal: Tribunal) -> None:
    b = normandy.b
    camp = _place(
        normandy,
        "atsingani_camp",
        "Atsingani's Camp",
        inside=normandy.places["aquitaine"],
        summary=(
            "A large semi-mobile camp a little way inside a forest in the "
            "sparsely peopled uplands of the Auvergne: a half-ring of "
            "wagons, tents both opulent and shabby, a temporary barracks "
            "and a horse corral. Moving about, it has no aura of its own, "
            "though the magi settle in a Magic aura when they can find one."
        ),
        **KNOWN_TRIBUNAL,
    )
    tower = _place(
        normandy,
        "atsingani_tower",
        "Atsingani's Council Tower",
        inside=normandy.places["aquitaine"],
        summary=(
            "A ruined, windswept hilltop tower a couple of days from the "
            "present camp, given to Atsingani by Montverte as its council "
            "chamber. It is unfit to live in and neglected, but the magi "
            "must come every summer to hold council and gather the vis "
            "there, for the Tribunal's custom forbids moving a council "
            "chamber, and Quaesitors have more than once checked that they "
            "do."
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A small, mobile Spring covenant, vassal of Montverte, made up "
        "mostly of soldiers of doubtful repute with wagons and tents, "
        "living by brigandage or as mercenaries. When they have stirred up "
        "enough trouble where they are, they move on to somewhere they "
        "will be noticed less. It is camped now in the uplands of the "
        "Auvergne, in the east of Aquitaine.",
        "Its founder Aureliana came of the Atsingani, a Byzantine tradition "
        "of wandering seers who served Emperor Constantine IX in the "
        "mid-eleventh century against wild beasts and rebel peasants, then "
        "fell from favour. As Byzantium declined she left the Theban "
        "Tribunal with another magus and her apprentice Viviana and went "
        "west looking for a Tribunal that would have them: Transylvania "
        "drove them out, the Rhine would not recognise them as a covenant, "
        "and Normandy, where founding a covenant is far easier, accepted "
        "them in 1187. To survive they swore fealty to Montverte, the liege "
        "closest to their way of thinking.",
        "Since then they have roamed the south of the Tribunal and raided "
        "weaker covenants, winning few friends and much mistrust. With no "
        "fixed base they have no steady income: they prosper when their "
        "mercenaries serve rich masters and otherwise rob villages, "
        "monasteries, merchants, pilgrims and weak covenants. They have no "
        "stone buildings or walls and only poor shared laboratories in "
        "tents, apart from Viviana's. Hardship binds them: magi and "
        "covenfolk are close and loyal, and the magi are not aloof from "
        "their servants.",
        "About fifty people follow the covenant, three dozen of them "
        "Brabançon mercenaries, with nearly as many horses: Byzantines and "
        "Brabanters, mostly young or in middle age, since the camp can "
        "hardly keep the infirm and mothers often leave to settle down. The "
        "Brabançons are coarse, crude men but expert soldiers and riders, "
        "deadly with the crossbow. There may be one or two more magi beyond "
        "the two the book describes.",
    )
    what_matters = _lines(
        "Vis: the one permanent source, gathered each summer at the ruined council tower (kind and amount not given)",
        "Vis: whatever the magi find, take or win at the Tourney",
        "Income: mercenary service when there are rich masters; robbery when there are not",
        "Boon: Veteran Fighters: three dozen Brabançon mercenaries",
        "Boon: Crossbowmen: the Brabançons are expert with the crossbow",
        "Boon: Cavalry: expert horsemen, with nearly as many horses as people",
        "Boon: Loyal Covenfolk: a close-knit, loyal company",
        "Boon: Strong Community",
        "Hook: Constantly Mobile: wagons and tents, moving on whenever it wears out its welcome",
        "Hook: Poverty: no stable income",
        "Hook: Beholden: vassal of Montverte",
        "Hook: Criminals: brigands, some excommunicate under the ban on Brabanters",
        "Tension: raids on weaker covenants have made it widely distrusted in the Tribunal",
        "Tension: its council chamber cannot be moved, and Quaesitors check that council is really held there",
        "Hook: it may settle near the players' covenant and prey on its convoys, or offer its services for a share of the spoils; fighting it off will anger Montverte",
    )
    atsingani = b.covenant(
        "Atsingani",
        tribunal=tribunal,
        founded=1187,
        place=camp,
        summary=summary,
        what_matters=what_matters,
        aura=0,
        season="Spring",
    )
    normandy.covenants["atsingani"] = atsingani
    normandy.tenure(
        "The vis of Atsingani's ruined council tower (kind and amount not given)",
        atsingani,
        "seisin",
        notes=f"Gathered each summer at {tower.name}, Montverte's gift.",
    )
    for art in ("Aquam", "Auram", "Creo", "Ignem"):
        normandy.tenure(
            f"The hot springs of the Auvergne: {art} vis",
            None,
            "tropaeum",
            notes="Gathered at Royat, le Mont-Dore and la Bourboule.",
        )
    _atsingani_people(normandy, b, atsingani)
    b.book(
        atsingani,
        "Atsingani's library",
        "Other",
        description=(
            "The book names no titles. The covenant has only poor shared "
            "tent laboratories; Viviana's laboratory in her faerie wagon is "
            "the exception."
        ),
    )


def _atsingani_people(normandy: Normandy, b: Builder, atsingani: Covenant) -> None:
    m = normandy.magi
    m["viviana"] = b.magus(
        "Viviana of Ex Miscellanea",
        covenant=atsingani,
        house=EX_MISC,
        age=54,
        traits={"Restless": 2, "Passionate": 1, "Thoughtful": 1},
        summary=(
            "Spiritual leader and guide of Atsingani, a fading beauty of "
            "Mediterranean blood who looks about forty-one: filia of "
            "Aureliana, the eldest of the founders, and a soothsayer and "
            "healer of the same Byzantine tradition. She owns the "
            "covenant's most prized possession, a grand wagon of faerie "
            "make, far larger inside than out and richly fitted, with room "
            "for a laboratory and a bedchamber; it never runs out of fresh "
            "clothes and linen for her, and rides so smoothly over rough "
            "roads that nothing inside is jolted."
        ),
    )
    m["jacques"] = b.magus(
        "Jacques of Flambeau",
        covenant=atsingani,
        house=FLAMBEAU,
        age=44,
        traits={"Disciplined": 2, "Questionable Ethics": 2, "Greedy": 1},
        summary=(
            "Captain of the covenant's mercenaries, apparently thirty-nine. "
            "Already a seasoned Brabançon warrior, he was apprenticed at "
            "eighteen to an Ex Miscellanea eremite, so he is only some ten "
            "years past his Gauntlet. As soon as he became a magus he left "
            "his pater's covenant to rejoin his own people, and soon after "
            "joined House Flambeau. He burns to avenge his father on the "
            "Capuchonnes who killed him in 1183."
        ),
    )
    m["baudouin"] = b.magus(
        "Baudouin",
        covenant=atsingani,
        house="",
        age=32,
        type="grog",
        traits={"Surly": 2, "Brave": 1, "Bored": 1},
        summary=(
            "One of Atsingani's more experienced Brabanters, in its service "
            "since his youth, when he was branded a thief. A shifty man with "
            "an unkempt beard, fierce blue eyes and a face marred by the "
            "brand, he handles his weapons like an expert. Banditry is "
            "second nature, but he is tired of the wandering, the "
            "on-and-off poverty and the lack of women. Reliably violent but "
            "no leader, he is usually picked for the vanguard of a raid."
        ),
    )


# ---------------------------------------------------------------- stats


def _stats_baudouin(b: Builder, baudouin: Any) -> None:
    b.stats(
        baudouin,
        {
            "characteristics": {
                "intelligence": -2,
                "perception": 0,
                "presence": 0,
                "communication": -1,
                "strength": 1,
                "stamina": 1,
                "dexterity": 3,
                "quickness": 2,
            },
            "size": 0,
            "decrepitude": (0, 0),
            "apparent_age": 32,
            "virtues_flaws": [
                "Branded Criminal",
                ("Puissant {ability}", {"ability": "bows"}),
                "Tough",
                "Weakness (Minor)",
                "Depressed",
            ],
            "abilities": [
                ("Animal Handling", 3, "horses"),
                ("Area Lore: Aquitaine", 2, "wilderness"),
                ("Athletics", 2, "running"),
                ("Awareness", 3, "keeping watch"),
                ("Brawl", 3, "dagger"),
                ("Bows", 5, "crossbow"),
                ("Carouse", 1, "dice"),
                ("Concentration", 1, "ambush"),
                ("Living Language: French", 5, "Walloon"),
                ("Hunt", 3, "rabbits"),
                ("Profession: Carpenter", 2, "wagons"),
                ("Ride", 4, "long distance"),
                ("Single Weapon", 6, "axe"),
                ("Stealth", 3, "ambush"),
                ("Survival", 2, "forest"),
            ],
            "traits": {"Surly": 2, "Brave": 1, "Bored": 1},
            "notes": (
                "Age 32. His Weakness is for loose women. Bows is 5, +2 "
                "from Puissant Bows.\n"
                "Dagger: Init 0, Atk +9, Def +6, Dam +4. "
                "Axe and round shield, mounted: Init +1, Atk +17, Def +14, "
                "Dam +7; on foot: Init +1, Atk +14, Def +11, Dam +7. "
                "Crossbow: Init +5, Atk +16, Def +10, Dam +8. "
                "Soak +7; Encumbrance 2 (3); Fatigue OK, 0, -1, -3, -5, "
                "Unconscious. Wounds: -1 (1-5), -3 (6-10), -5 (11-15), "
                "Incapacitated (16-20).\n"
                "Equipment: partial leather scale armour, axe, round shield, "
                "crossbow, and a grog's pack with carpenter's tools and his "
                "lucky dice."
            ),
        },
    )


P = Profile


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


def _focus(name: str, focus: str) -> tuple[str, dict[str, str]]:
    return (name, {"focus": focus})


#: Each sketched magus's profile, by its key in `normandy.magi`.
PROFILES: dict[str, Profile] = {
    # -- Oleron --
    "caprican": P(
        strong="pre int com",
        native="French",
        arts={"Re": 6, "Me": 6, "An": 5, "Mu": 3, "Im": 3, "Vi": 3, "Cr": 2},
        abilities={
            "Single Weapon": (3, "sword"),
            "Faerie Lore": (3, "faerie courts"),
            "Leadership": (3, "covenfolk"),
            "Intrigue": (2, "Hermetic gossip"),
            "Ride": 2,
        },
        virtues=[
            ("Strong Faerie Blood", {"blood": "faun"}),
            _focus("Minor Magical Focus", "emotions"),
            "Proud (Minor)",
            "Hatred (Minor)",
            "Dark Secret",
        ],
        reputations={"Champion of the Apple Mile (Hermetic)": 3},
    ),
    "amelie": P(
        strong="int com",
        weak="str",
        native="French",
        arts={"Aq": 6, "Cr": 4, "Mu": 4, "Im": 3, "In": 2},
        abilities={
            "Faerie Lore": 2,
            "Area Lore: Normandy Tribunal": (2, "covenants"),
            "Etiquette": (1, "magi"),
            "Bargain": 1,
        },
        virtues=[
            ("Faerie Blood", {"blood": "river nymph"}),
            _art("Affinity with {art}", "aquam"),
            "Small Frame",
            "Meddler (Minor)",
        ],
    ),
    "quintinus": P(
        strong="int dex",
        native="French",
        arts={"Cr": 5, "Te": 5, "He": 4, "Mu": 3, "Aq": 3, "Vi": 3},
        abilities={
            "Craft: Brewing": (3, "cider"),
            "Craft: Stonemason": (3, "tumuli"),
            "Faerie Lore": (2, "the Stone Couches"),
        },
        virtues=["Inventive Genius", "Secretive", "Infamous"],
        reputations={"Idle and incompetent (House Verditius)": 2},
    ),
    # -- Nidi --
    "regulus": P(
        strong="pre com",
        native="Occitan",
        arts={"An": 6, "He": 5, "Mu": 5, "Cr": 3, "Vi": 3, "Re": 3},
        abilities={
            "Animal Handling": (3, "bees"),
            "Faerie Lore": (3, "sprites"),
            "Craft: Wax Sculpture": (2, "statues"),
        },
        virtues=[
            "Bee King",
            "Wrathful (Minor)",
            "Compassionate (Minor)",
            "Driven (Minor)",
        ],
    ),
    "luna": P(
        strong="dex qik per",
        weak="str",
        native="Italian",
        arts={"An": 6, "Mu": 4, "Re": 3, "Co": 3, "Te": 2, "He": 2},
        abilities={
            "Heartbeast": (4, "rat"),
            "Stealth": (3, "in towns"),
            "Animal Handling": (2, "rats"),
        },
        virtues=[
            "Summon Animals",
            "Small Frame",
            "Outsider (Minor)",
            "Weakness (Minor)",
        ],
    ),
    "micropedus": P(
        strong="int sta",
        native="Occitan",
        arts={"Au": 7, "Cr": 4, "Re": 4, "Mu": 3, "An": 3, "Pe": 2, "He": 2},
        abilities={
            "Heartbeast": (4, "flight"),
            "Teaching": (2, "Bjornaer apprentices"),
            "Philosophiae": (2, "natural philosophy"),
        },
        virtues=[
            _art("Affinity with {art}", "auram"),
            _focus("Minor Magical Focus", "weather"),
            "Driven (Minor)",
            "Lame",
        ],
    ),
    # -- Atsingani --
    "viviana": P(
        strong="pre int per",
        native="Greek",
        arts={"In": 6, "Cr": 5, "Co": 5, "Me": 3, "Im": 2, "He": 2},
        abilities={
            "Medicine": (3, "herbal cures"),
            "Chirurgy": 2,
            "Ride": (2, "wagons"),
            "Living Language: French": 3,
        },
        virtues=[
            ("Divination and Augury", {"method": "soothsaying"}),
            _focus("Minor Magical Focus", "healing"),
            "Necessary Condition",
            "Wanderer",
            "Rolling Stone",
        ],
    ),
    "jacques": P(
        strong="sta str dex",
        native="French",
        arts={"Ig": 6, "Pe": 5, "Cr": 3, "Re": 3, "Co": 2},
        abilities={
            "Single Weapon": (4, "axe"),
            "Bows": (3, "crossbow"),
            "Ride": (3, "in battle"),
            "Leadership": (3, "mercenaries"),
            "Area Lore: Aquitaine": 2,
        },
        virtues=["Warrior", "Greedy (Minor)", "Hatred (Minor)"],
    ),
}


def finish(normandy: Normandy) -> None:
    """Set the royal towns and officers under the King of France."""
    king = normandy.world.get("king")
    if king is None:
        return
    for key in CROWN_HELD:
        record = normandy.world[key]
        if record.answers_to is None:
            record.answers_to = king.id


def stats(normandy: Normandy) -> None:
    """Baudouin's printed block, then a generated block for every magus
    of the chapter."""
    b = normandy.b
    _stats_baudouin(b, normandy.magi["baudouin"])
    for key, profile in PROFILES.items():
        apply(b, normandy.magi[key], profile)
