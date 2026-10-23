"""The County of Toulouse, the Provençal Tribunal's heartland, as of 1220:
the red towns, castles and drovers' plains between the Pyrenees and the
uplands of Provence; the city of Toulouse with its six districts, its
capitouls and its drowned lake; the hinterland, the Albigeois, the
Agenais, Cahors and the Carcassès, scarred by the crusade's atrocities;
Tolosa Paratge, at war with itself in its regio under the city, and the
unrecognised Ostal des Exiles in the caves under Castle d'Aguilar, with
their magi and libraries; and the count, the capitouls, Bishop Foulques,
the legate, the crusade's lords and the towns, each with who holds it in
1220, in paraphrase of Faith & Flame chapter four (and chapter three for
the covenants' votes and standing).

The ruined covenants of the county (Windgraven, Lariander, Berinor) are
tribunal.py's; the crusade's threat is stories.py's. Creatures (the
Spirit of Tolosa, the follets of Auriac, the demesoilles, the lady of
Puivert's lake, the demon cat of Fanjeaux and the county's many ghosts)
are described in the summaries of the places they haunt, since there is
no bestiary yet. Records are kept in the Provence dicts under slugs: the
region is places["toulousain"], the city places["toulouse_city"], the
covenant sites places["tolosa_lake"] and places["aguilar_grottoes"], and
the haunted wood of Montgey, where Lariander stood, places["montgey"]; the
city is also under places["toulouse"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, joined_lines, paragraphs, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Provence

JERBITON = "house_jerbiton"
FLAMBEAU = "house_flambeau"
VERDITIUS = "house_verditius"
EX_MISC = "house_ex_miscellanea"
TREMERE = "house_tremere"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}
HIDDEN = {"status": "Hidden", "known": "Locally"}


def _add(provence: Provence, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = provence.b.place(name, **kw)
    provence.places[key] = place
    return place


def build(provence: Provence) -> None:
    b = provence.b
    tribunal = provence.tribunal or next(iter(b.saga.tribunals), None)
    if tribunal is None:
        # tribunal.py builds the Tribunal first; without it there is
        # nothing to hang the covenants on.
        return
    _region(provence)
    _city(provence)
    _lake(provence)
    _hinterland(provence)
    _albigeois(provence)
    _agenais(provence)
    _cahors(provence)
    _carcasses(provence)
    _tolosa_paratge(provence, b, tribunal)
    _ostal(provence, b, tribunal)
    _lords(provence, b)
    _churches(provence, b)
    _towns(provence, b)
    _factions(provence, b)


# ------------------------------------------------------------- the region


def _region(provence: Provence) -> None:
    if "toulousain" in provence.places:
        return
    _add(
        provence,
        "toulousain",
        "The County of Toulouse",
        summary=paragraphs(
            "The middle of the Tribunal: a broad, shallow basin between the "
            "Pyrenees to the south and the uplands of Provence to the east, "
            "dusty with orchards, vines and fields. Every ridge and rocky "
            "spur seems to carry a castle. Villages are of timber and wattle "
            "or of the local brick, pink to deep red, so that whole towns "
            "flush with colour at sunrise and sunset, a sight northerners "
            "never stop praising. Drovers' roads up to a mile wide cross the "
            "plain, and each late spring huge herds of cattle, sheep and goats "
            "go up to the Pyrenean pastures, coming down again in early "
            "autumn.",
            "The counts began as Merovingian officials, made the office "
            "hereditary under the Carolingians, and took on the speech and "
            "customs of the south, owning the French king as liege in name "
            "only. Raimond III pushed the county over old Septimania in the "
            "tenth century; Raimond IV (1093 to 1105) took the march of "
            "Provence and the Narbonnais, which with his Aragonese marriage "
            "made him lord of nearly all the Tribunal save Gascony. Raimond V "
            "gave the city its council of capitouls. A daughter may inherit "
            "when there is no son, as Philippa, Duchess of Aquitaine, did.",
            "Lordship sits lightly here. Many lords long ago shook off their "
            "oaths, as the counts shook off the king's, and Raimond VI's easy "
            "rule, tax exemptions and war have raised a class of merchants "
            "and landholders who owe fealty to nobody and are often richer "
            "than the barons. A covenant here can stand outside the feudal "
            "web more easily than almost anywhere in Mythic Europe. Many "
            "towns copy Toulouse and elect capitouls or consuls of their own.",
            "The crusade has turned the county into a patchwork. Since Simon "
            "de Montfort died before Toulouse in 1218 there are no borders: "
            "castles of either side stand a few miles apart, both keep "
            "garrisons scattered across the land, and the faidits, knights "
            "stripped of their lands by the crusaders, are drifting home to "
            "take them back by papal favour or by the sword. Raimond VI holds "
            "his city and much of the county again; Amaury de Montfort holds "
            "Carcassonne and the crusader strongholds. The massacres have "
            "left Infernal auras across the land, at Lavaur, Montgey, Bram, "
            "Montlaur, Hautpoul, Puisserguier and Alairac.",
            "Hermetically the county is Tolosa Paratge's, one of the "
            "Tribunal's oldest covenants, now torn in two; the exiles of the "
            "Ostal des Exiles hide under Castle d'Aguilar. Windgraven, "
            "Lariander and Berinor have fallen here within living memory, "
            "and the Tribunal of 1214, meant for Toulouse, was moved to "
            "Castra Solis because de Montfort's army stood outside the walls.",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- the city


def _city(provence: Provence) -> None:
    region = provence.places["toulousain"]
    city = _add(
        provence,
        "toulouse_city",
        "The City of Toulouse",
        inside=region,
        realm="Divine",
        summary=paragraphs(
            "Capital of the county and heart of the Languedoc, once a Roman "
            "and then a Visigothic seat, and among the largest, richest and "
            "most cultivated cities of Mythic Europe; its people think Paris "
            "a backward rival. The count rules it in name, but the elected "
            "Capitole holds most of the power he has handed over, and the "
            "bishop shares the right of justice, so the city lives in "
            "constant friction between them.",
            "Its stout wall has turned back siege after siege: de Montfort "
            "failed before it in 1211, was let in in 1215, was thrown out by "
            "a rising in 1216, besieged it from autumn 1217 until a stone "
            "killed him under the walls in summer 1218, and in 1219 Prince "
            "Louis tried again and withdrew when disease struck his camp. "
            "De Montfort razed the towers built into the wall, but twenty or "
            "more fortified towers still stand within the city, kept by petty "
            "nobles, capitouls and rich burghers with small guards of their "
            "own; the White faction of Tolosa Paratge holds one of them, and "
            "buying or building one is a sensible way for magi or wealthy "
            "companions to keep a foothold here.",
            "Justice is shared by old custom between the count's court (now "
            "the Capitole) and the bishop's, each poaching on the other's "
            "ground, and a man condemned by one can sometimes win on appeal "
            "to the other. The law is the magisterial Roman law of the south, "
            "the Ability Civil and Canon Law, not the common law of France.",
            "Since the White and Black Brotherhoods fought in the streets, "
            "lending at interest has been forbidden and money is hard to "
            "raise; the moneylenders have gone to Cahors. Six districts make up the city, and each returns two capitouls, who wear red "
            "robes trimmed with black fur over clothes in their district's "
            "colours.",
        ),
        **KNOWN_ORDER,
    )
    provence.places["toulouse"] = city
    _add(
        provence,
        "chateau_narbonnais",
        "The Château Narbonnais",
        inside=city,
        summary=(
            "The count's castle on the western edge of the city, inside the "
            "walls, commanding the great western gate; it serves as the "
            "citadel if the walls fall. Raimond once gave it to Bishop "
            "Foulques to win him over. Alice de Montfort held it against the "
            "townsfolk when Raimond came back in autumn 1217 and had to yield "
            "it. In 1213 a mob broke into its dungeon, seized three crusader "
            "knights taken at Pujol, and tore them apart in the streets."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "saint_sernin",
        "Saint-Sernin District",
        inside=city,
        realm="Divine",
        summary=(
            "The district of the great basilica of Saint-Sernin, for "
            "centuries the region's chief pilgrim shrine, which Pope Urban consecrated while travelling to Clermont to call the First Crusade. Its huge church of "
            "white stone and red brick, with its octagonal tower and spire, "
            "looms over the houses; Augustinian canons keep it, with a "
            "college and a hospice for the city's poor, and pilgrims crowd it "
            "each summer to see the relics. An Augustinian poetry contest is "
            "held in its orchard. Its capitouls wear yellow and white."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "la_pierre",
        "La Pierre (Saint-Pierre des Cuisines)",
        inside=city,
        realm="Divine",
        summary=paragraphs(
            "A poor riverside parish of boatmen by the Garonne, known for "
            "vice and theft; its harlots are called Magdalenes. Its church, a "
            "property of the Benedictines of Moissac, stands on the oldest "
            "Christian site in the Tribunal, though the building is only two "
            "hundred years old. Humble as it is beside Saint-Sernin and the "
            "Daurade, it is where the counts hold court, make their great "
            "announcements and sign their charters before the crowd, and "
            "where the capitouls proclaim their laws. Its capitouls wear deep "
            "blue.",
            "The church steps hold a tiny Magic lacuna of aura 1. Here the "
            "counts swear to the people and new capitouls take their oaths, "
            "and here alone the Spirit of Tolosa can bind an oath made before "
            "the crowd: whoever breaks it, even unknowingly and in secret, "
            "becomes the subject of mostly false rumours across the county "
            "and gains the Flaw Infamous, though nobody learns what he did.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "santa_maria_dealbata",
        "Santa Maria Dealbata District",
        inside=city,
        realm="Divine",
        summary=(
            "St Mary the White, named for the lime wash on its church: a "
            "district of rich merchants among smaller shops and craftsmen. "
            "A few wealthy artisans resent the merchants' grip, and an "
            "ambitious would-be capitoul can buy his way in if he will wade "
            "into the quarrel between the two. Its capitouls wear carnation "
            "pink. A candidate must live in the city a month before an "
            "election, and the capitouls talk of making it seven years."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "saint_etienne",
        "Saint-Etienne District",
        inside=city,
        realm="Divine",
        summary=(
            "The wealthiest quarter, home to nobles and rich citizens. In "
            "Toulouse birth matters less than wealth, taste, learning and "
            "influence, and a rich commoner can climb into the petty "
            "nobility, to the scorn of nobles from elsewhere. Its cathedral, "
            "on the site of a chapel Saint Sernin founded, is a Romanesque "
            "basilica forever being enlarged and now caged in scaffolding; "
            "it has less standing than the other churches, perhaps because "
            "of its bishop, the hated Foulques, who is away with the "
            "crusaders. Its capitouls wear violet and white."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "pont_vieux",
        "Pont-Vieux and the Boom",
        inside=city,
        summary=paragraphs(
            "The district round the oldest bridge over the Garonne, "
            "whose capitouls wear amaranth, a maroon, and white. A huge "
            "timber boom has lately been built across the river to "
            "narrow it and quicken the current for the many watermills. "
            "Adam Carpentiere of Tolosa Paratge enchanted it with small "
            "devices set through its frame: it tames the river so that "
            "even the snow-melt floods no longer spill over, and, in a "
            "way few magi follow, it props up the covenant's regio, "
            "which is bound to the river's flow and had been fading as "
            "silt choked the channel.",
            "At night the Spirit of Tolosa sometimes sits on the boom in "
            "the shape of a fisherman, glad to talk to anyone.",
        ),
        secrets="The boom helps the regio not through the water but through the "
        "prosperity it has brought the mills and their shareholders.",
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "adams_lacuna",
        "Adam Carpentiere's Waterfront Lacuna",
        inside=city,
        aura=2,
        summary=(
            "A small pocket of Magic aura 2 on the waterfront, amid the "
            "city's Dominion, where Adam Carpentiere of Tolosa Paratge has "
            "long kept his sanctum and laboratory."
        ),
        **HIDDEN,
    )
    _add(
        provence,
        "daraude",
        "Daraude, the District of the Sea Bream",
        inside=city,
        realm="Divine",
        summary=(
            "The quarter nearest the Garonne, whose capitouls wear green and "
            "white. Its church, Our Lady of the Sea Bream (the Daurade), is a domed basilica of twelve sides whose gold mosaics outshine even its dome, "
            "built on a Roman temple of Apollo and served by Benedictines; "
            "it keeps a Black Madonna, Notre-Dame Noire. Each early May the "
            "church is decked with flowers brought in procession and a public "
            "feast is held. The district is loyal both to Toulouse and to the "
            "Church, and Cathars are not welcome. Somewhere in its misty "
            "alleys lies the way into the drowned lake of Tolosa."
        ),
        **KNOWN_LOCALLY,
    )


def _lake(provence: Provence) -> None:
    daraude = provence.places["daraude"]
    _add(
        provence,
        "tolosa_lake",
        "The Drowned Lake of Tolosa",
        inside=daraude,
        summary=paragraphs(
            "Before Rome, the Tolosates appeased a spirit in a lake by "
            "the Garonne, here in what is now the Daurade quarter: when "
            "fever rose from the marshes they sank consecrated gold and "
            "silver in its waters and the sickness passed. In 106 BC the "
            "governor Quintus Caepio drained it and carried off the "
            "hoard, the aurum Tolosanum, and something stranger besides, "
            "it is whispered. The Tolosates rose against Rome for the "
            "first time; within a year Caepio was dead in battle and the "
            "treasure gone. Some say it is the hoard the Cathars are "
            "rumoured to guard at Montségur, and every legend agrees "
            "gold still lies hidden in the region under a deadly curse. "
            "A temple of Apollo replaced the lake, and the Daurade "
            "replaced the temple.",
            "Yet the lake survives. Whoever knows the signs, or simply "
            "loses his way in the riverside lanes on a misty evening, "
            "may with difficulty cross into a regio where the houses and "
            "streets stand empty and the water rises toward the river "
            "until only roofs break the surface of a still, black lake "
            "under drifting mist. Those who know the way step from roof "
            "to roof to the last house, where a boat waits to row them "
            "to the island of Tolosa Paratge. Things move in the dark "
            "water that are only ever half seen.",
            "The regio is the work of the city's genius loci, the Spirit "
            "of Tolosa (Magic Might 40, Aquam; it answers to no name but "
            "Tolosa). Seen with Second Sight it is a damp mist or a "
            "sexless figure of water and reeds; in human shape, from one "
            "sunrise or sunset to the next, it is an unremarkable common "
            "townsman who nonetheless unsettles everyone, and it likes to "
            "fish from Adam Carpentiere's boom at night and chat, making "
            "little sense to mortals. It is soft-hearted toward the "
            "citizens and bound to the land. Its powers mend a breach in "
            "the walls until the next sunset or sunrise, when the stone "
            "falls away again; steer a body such as the capitouls in "
            "session or the bishop toward what is best for the whole "
            "city; bless a person with sudden prosperity and the Virtue "
            "Ways of Toulouse for as long as it likes; and bind oaths "
            "sworn on the steps of Saint-Pierre des Cuisines. The magi "
            "leave it alone, but know it has grown much weaker of late.",
        ),
        secrets="The regio echoes the old sacrificial lake and is bound both to "
        "the river and to the power and prosperity of Toulouse itself. "
        "De Montfort's conquest and the city's strife are what weakened "
        "the aura and made the regio hard to reach, and the magi's own "
        "feud mirrors the city's. Only healing the city will save the "
        "covenant: restoring learning and culture, perhaps by founding a "
        "university inside the walls or championing Occitan letters. "
        "Adam's boom is only a first step, and it worked through the "
        "mills' wealth, not the water.",
        levels=[
            Builder.level(
                "The drowned streets and the lake",
                3,
                see="Signs known to the Tolosates, or a misty evening in the waterfront lanes",
                enter="Hard to find; the empty streets slope down into black water",
                notes=(
                    "Empty houses sink into a misty lake; an island with a "
                    "black octagonal tower and red brick houses holds Tolosa "
                    "Paratge. An enchanted boat comes to the last roof when "
                    "a short Occitan poem is called."
                ),
            )
        ],
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------- the hinterland


def _hinterland(provence: Provence) -> None:
    region = provence.places["toulousain"]
    land = _add(
        provence,
        "toulouse_hinterland",
        "The Toulouse Hinterland",
        inside=region,
        summary=(
            "The towns round the city stand among golden wheat, with stony "
            "sheep pastures on the low hills. Many have followed Toulouse in "
            "shedding feudal dues and electing capitouls to rule for their "
            "artisans and burghers. Small castles dot the country, some held "
            "by crusaders or their friends, some by southern lords still "
            "hiding Cathars and faidits."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "termes",
        "Termes",
        inside=land,
        summary=(
            "Reckoned with Cabaret and Minerve among the three mightiest castles of the region, taken by de Montfort after a hard siege. Held in 1220 "
            "by a crusader garrison, but word has come that Oliver and "
            "Bernard of Termes, its defender's sons, are coming back with "
            "their men this spring, as dispossessed southern lords across the "
            "county retake their lands."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "pujol",
        "Pujol",
        inside=land,
        summary="A small castle and hamlet three miles from the city, the home of "
        "Carolus St. Tropez, who passes for a minor southern noble owing "
        "no liege. De Montfort took it; St. Tropez won it back with a "
        "handful of men in summer 1213, captured the three crusader "
        "knights holding it (they had been burning crops round Toulouse, "
        "and with them vis sources) and put the rest of the garrison to "
        "the sword. A Toulousain mob later dragged the knights from the "
        "Château Narbonnais and hanged what was left of them outside the "
        "walls. Arnaud Amalric often stays here as St. Tropez's guest. "
        "Held in 1220 by St. Tropez.",
        secrets="St. Tropez believes the Gorgiastic Cathar Marc controlled the "
        "knights' minds; it fed the hatred that ended in Marc's death.",
        **KNOWN_REGION,
    )
    _add(
        provence,
        "montgey",
        "The Ashen Field and Haunted Wood of Montgey",
        inside=land,
        realm="Infernal",
        aura=6,
        summary=paragraphs(
            "Montgey is gone: only a field of ash remains. In 1211 a "
            "column of crusaders, mostly Rhinelanders, marching to the "
            "siege of Lavaur was caught in the woods here by the Count of "
            "Foix's knights and the villagers, and some six hundred were "
            "butchered. Survivors spoke of white ladies, the faerie "
            "demesoilles, casting spells on the column and of the trees "
            "themselves attacking. When Lavaur fell, de Montfort came "
            "back and hanged the villagers.",
            "Both the village site and the wood of the massacre now hold "
            "Infernal auras of 6, and dark shapes scurry between the "
            "trees at night. In the burned wood stood Lariander, the "
            "Tremere covenant the crusaders destroyed in the reprisals, "
            "mistaking its black-robed magi for Cathar perfecti.",
        ),
        secrets="The tales are true. Garsenda of Lariander stirred the villagers "
        "to fall on the column, hoping it would save Lavaur, with the "
        "demesoilles' help, and so brought the crusaders down on her own "
        "covenant.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        provence,
        "puivert",
        "Castle Puivert and its Lake",
        inside=land,
        summary=paragraphs(
            "A castle on a low hill in a green, thickly wooded valley, "
            "famous for a great gathering of Cathars in 1170 and for its "
            "open-handed welcome to troubadours. Bernard of Congost held "
            "it until de Montfort took it in 1210; the crusader "
            "Lambert de Thury rules it in 1220.",
            "Below it lies a quiet lake with a throne-shaped rock on the "
            "shore, where troubadours serenaded the ladies of the castle. "
            "On Midsummer night, if a new song praising a lady's beauty "
            "is sung while she sits on the throne, the lock of hair she "
            "gives the singer holds 4 pawns of Rego vis (unclaimed). The "
            "faerie lady of the lake grows jealous of such homage and "
            "sometimes raises the waters to carry off the lady, her maids "
            "and the singer beneath the water to a regio where all of them must serve her.",
        ),
        secrets="Lambert de Thury may come home from a late Midsummer hunt to "
        "find his castle empty and his wife and household gone beneath "
        "the lake.",
        **KNOWN_REGION,
    )
    _add(
        provence,
        "bruniquel",
        "Bruniquel",
        inside=land,
        summary=(
            "A castle Count Raimond meant to destroy when he saw he could not "
            "hold it against de Montfort. His brother Baudouin talked him "
            "out of it and took command of the garrison, but Baudouin had "
            "already gone over to the crusade and handed the castle to it "
            "at once, a treachery that later cost him his life."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "puilaurens",
        "Puilaurens",
        inside=land,
        summary=(
            "A powerful castle, a fief of the King of Aragon since 1162, where faidits and hunted Cathars find shelter; being Aragonese, it is off limits to the crusaders. Held in 1220 for the King of "
            "Aragon."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "villedieu",
        "Villedieu-du-Temple",
        inside=land,
        realm="Divine",
        summary=(
            "A Templar commandery near Montauban, where a Templar knight cut "
            "Baudouin of Toulouse down from the walnut tree he was hanged on "
            "and buried him. The Templars stay mostly neutral in the war, "
            "though they lean to the crusaders."
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------------- the Albigeois


def _albigeois(provence: Provence) -> None:
    region = provence.places["toulousain"]
    land = _add(
        provence,
        "albigeois",
        "The Albigeois",
        inside=region,
        summary=(
            "The country south of Albi, so steeped in Cathar sympathy that its "
            "name came to stand for every heretic, and for the crusade sent to destroy them. It is well wooded, and its vineyards make a cheap, plain "
            "but drinkable wine poured all over the Tribunal and beyond."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "demesoilles_woods",
        "The Woods of the Demesoilles",
        inside=land,
        realm="Faerie",
        summary=(
            "The many woodlands of the Albigeois are haunted by the "
            "demesoilles, faerie White Ladies who take the part of the poor "
            "and oppressed. Several are close to Garsenda of the Ostal des "
            "Exiles, and some of them helped turn the woods of Montgey "
            "against the crusaders in 1211. The book gives no auras or Might "
            "for them."
        ),
        **RUMOURED,
    )
    _add(
        provence,
        "lavaur",
        "Lavaur and the Field of Ashes",
        inside=land,
        realm="Infernal",
        aura=6,
        summary=paragraphs(
            "A small Trencavel town on the Agout, called the citadel of "
            "Satan for its heresy. The Bishop of Clairvaux failed to take "
            "it in 1181; in 1211 its horseshoe of earthen ramparts and "
            "walls, backed against a high cliff, looked unbreakable. "
            "Faidits had gathered there under Aimery of Montreal and his "
            "learned sister Na Geralda (Guirauda), who ran a house for "
            "Cathar women believers and patronised troubadours and "
            "scholars. It fell after six weeks: Aimery's gallows broke "
            "under his armour and his throat was cut with his knights'; "
            "Na Geralda was given to the soldiers, thrown into a well and "
            "stoned to death, which sickened even some crusaders; and "
            "three or four hundred Cathars walked willingly onto a pyre "
            "in a meadow outside the walls. Toulousain knights found in "
            "the garrison exposed Raimond's double game and turned the "
            "crusade against him for good. Gui de Lucy holds it for the "
            "crusade in 1220.",
            "Where the Cathars burned is a field of ash on which nothing "
            "grows, with an Infernal aura of 6. Na Geralda's ghost haunts "
            "the town, appearing whole and finely dressed; she courts a "
            "likely lover in fin amor and only well into the affair "
            "reveals what she is and begs for her bones to be properly "
            "buried. Refused, she shows herself as the mangled corpse she "
            "became and terrifies the faithless suitor. The crusaders "
            "cannot see her and laugh at the stories, but they want her "
            "bones left alone, and anyone trying to lay her to rest will "
            "face Gui de Lucy and his men.",
        ),
        secrets="Nobody knows why the crusaders cannot see the ghost.",
        **KNOWN_REGION,
    )


# -------------------------------------------------------------- the Agenais


def _agenais(provence: Provence) -> None:
    region = provence.places["toulousain"]
    land = _add(
        provence,
        "agenais",
        "The Agenais",
        inside=region,
        summary=(
            "The county's far north round Agen: low wooded hills and sheep "
            "country, more like France than the south. Its fine wool keeps it "
            "prosperous, and the heretics are very strong here."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "lolmie",
        "Château Lolmie",
        inside=land,
        summary="The castle near Montcuq where, in 1214, Baudouin of Toulouse's "
        "own men betrayed him to two of his brother's knights; he was "
        "hauled naked from his bed and carried off over a saddle, then "
        "hanged at Montauban a few days later.",
        secrets="Dying, Baudouin cursed his brother's bones never to be buried "
        "and the traitors of Lolmie to early graves. Most of the thirty "
        "have died in strange accidents, and the rest are desperate for "
        "help. The curse is a unique Invocation of level 60, of Divine or "
        "Infernal power as the storyguide chooses; its victims roll four "
        "extra botch dice until they confess the treachery and are "
        "forgiven.",
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "morlhon",
        "Morlhon le Haut",
        inside=land,
        summary=(
            "The castle of the Morlhon family, crusaders in the Holy Land; "
            "Odo de Morlhon built the Cluniac house of the Holy Sepulchre at "
            "nearby Villeneuve after a vision. Orthodoxy did not save them: "
            "the crusaders took castle and town in 1214, made the lord a "
            "faidit, and burned seven Waldensians in the market place a year "
            "before the Church even condemned them. The de Montfort family "
            "holds the Morlhon titles in 1220. Pons de Morlhon has joined the "
            "Ostal des Exiles as a companion, advised by the furious shades of the seven Waldensians burned there."
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------------------------- Cahors


def _cahors(provence: Provence) -> None:
    region = provence.places["toulousain"]
    _add(
        provence,
        "cahors_vineyards",
        "The Vineyards of Cahors",
        inside=region,
        summary="The country round Cahors gives itself to the famous black wine, "
        "in truth a deep red, shipped all over Mythic Europe; vines climb "
        "almost every south-facing slope, many crowned by castles. A few "
        "flasks, rightly made, hold a strong source of spell-like vis "
        "(unclaimed).",
        secrets="A Cahors moneylender ruined by a noble of Toulouse who calls his "
        "loan void under the city's ban on usury offers the magical wine "
        "to anyone who can make the debt good; the loan was made after "
        "the ban, so it may take the capitouls or the bishop to settle.",
        **KNOWN_REGION,
    )


# ---------------------------------------------------------- the Carcassès


def _carcasses(provence: Provence) -> None:
    region = provence.places["toulousain"]
    land = _add(
        provence,
        "carcasses",
        "The Carcassès",
        inside=region,
        summary=(
            "The old Trencavel lands round Carcassonne: hilly, with oak and "
            "beech forest and villages of grain or vines as the soil allows, "
            "littered with castles from the Trencavels' endless wars with the "
            "counts. Pilgrims on the way to Santiago de Compostela pass "
            "through. The crusade's worst cruelties were done here, and its "
            "marks are Infernal auras in castle after castle."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "carcassonne_springs",
        "The Dry Wells of Carcassonne",
        inside=land,
        summary="In 1209 the springs, cisterns and castle well of Carcassonne all "
        "failed in a hard drought, and with its viscount taken by "
        "treachery the city surrendered. The besiegers call it a miracle; "
        "the townsfolk suspect magic was turned on them.",
        secrets="Nobody has found out what dried the wells.",
        **RUMOURED,
    )
    _add(
        provence,
        "auriac",
        "The Gold Mines of Auriac",
        inside=land,
        realm="Faerie",
        aura=4,
        summary=(
            "Ancient gold mines, long abandoned, where nuggets can still be "
            "found and Terram vis gathered (unclaimed), if anyone can face "
            "what lives there. A Faerie aura of 4 fills the tunnels, home to "
            "follets: stone-throwing fae like northern goblins who love to "
            "bring the roof down on intruders. They live under two rival "
            "counts, one in each mine, and wage a bitter war on each other."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "bram",
        "The Marketplace of Bram",
        inside=land,
        realm="Infernal",
        aura=3,
        summary=(
            "A small walled town that held de Montfort off for three days. "
            "The priest of Montreal, who had betrayed the crusaders, was "
            "defrocked here by Bishop Gui of Carcassonne, mutilated, dragged "
            "through the streets and hanged. The hundred defenders had their "
            "eyes put out and their ears, noses and lips cut off, and were "
            "sent to Cabaret led by one man left a single eye. Some of the "
            "maimed still live, and some serve as grogs at the Ostal des "
            "Exiles. The market place keeps an Infernal aura of 3, and "
            "violence and revenge are now common there."
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "lastours",
        "Lastours and the Castles of Cabaret",
        inside=land,
        summary=paragraphs(
            "Rich in nearby iron and staunchly Cathar, Lastours is famous "
            "for three small stone castles a few miles apart on a sheer "
            "ridge above the Grésillon: Quertinheux on a rock low in the "
            "valley, Fleur Epine crowning the slopes, and Cabaret on a "
            "spur ringed by cliffs and the Orbiel on three sides, one of "
            "the three strongest fortresses of the region. The crusaders "
            "fell back in winter 1210, and de Montfort's kinsman Bouchard "
            "de Marly spent sixteen months in chains here; in 1211 "
            "Pierre-Roger de Cabaret had to give up the castles and free "
            "him, but escaped capture. The castles are held for the "
            "crusade in 1220, and Pierre-Roger, a friend of Cathars and a "
            "lavish host to troubadours, may win them back now the "
            "crusade falters.",
            "At Fleur Epine his brother Jourdain, lord of Pennautier, "
            "kept court with his wife Auda, a famous beauty called Na "
            "Loba, the She-Wolf, cruel to the lovers she enthralled; the "
            "troubadour Peire Vidal once crept up in a wolfskin to sing "
            "to her and was mauled by a mastiff that took him for a real "
            "wolf. Now old, she waits in exile with her three bewitching "
            "daughters.",
        ),
        secrets="Na Loba is blamed for betraying her liege Raimond-Roger "
        "Trencavel in 1209: he spurned her for her eldest daughter, so "
        "she arranged his safe-conduct to de Montfort and then withdrew "
        "her guards. She may bear the Curse of Venus, Venus' Blessing or "
        "something darker. Peasants whisper that her daughters are "
        "werewolves, and those who repeat it disappear.",
        **KNOWN_REGION,
    )
    _add(
        provence,
        "montlaur",
        "Montlaur",
        inside=land,
        realm="Infernal",
        aura=4,
        summary=(
            "The villagers besieged the garrison de Montfort left in the "
            "castle; he came back, hanged everyone he could catch and burned "
            "the village to the ground. Their ghosts are still seen in the "
            "woods, a dreadful sight, and the site has an Infernal aura of 4."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "hautpoul",
        "Hautpoul",
        inside=land,
        realm="Infernal",
        aura=3,
        summary=(
            "A Visigothic fortress on a crag which de Montfort took in 1212 after a four-day siege, many defenders slipping away in a thick fog "
            "that rose without warning during the assault. Castle and town "
            "were burned; now an eerie, bat-haunted ruin stands above a few "
            "shacks of survivors, under an Infernal aura of 3 and frequent "
            "uncanny fogs."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "saissac",
        "Saissac",
        inside=land,
        summary=(
            "Once a Cathar stronghold known for its generosity to "
            "troubadours, taken after Carcassonne fell and given to de "
            "Montfort's friend Bouchard de Marly, who holds it in 1220 "
            "against its dispossessed heirs. The heirs will likely look for "
            "help to win it back, and are open-minded enough to welcome a new "
            "covenant inside the citadel."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "puisserguier",
        "Puisserguier",
        inside=land,
        realm="Infernal",
        aura=4,
        summary="When a northern knight killed a southern lord of the crusade in "
        "a quarrel, de Montfort had him buried alive as southern custom "
        "demanded. The dead lord's nephew was not appeased: he changed "
        "sides, set fire to Puisserguier, the castle entrusted to him, threw its fifty northern soldiers into the dry moat and "
        "buried them alive under stones, and took its two knights to "
        "Minerve to be blinded and mutilated. The moat has an Infernal "
        "aura of 4.",
        secrets="The buried garrison still claws at the earth at night and will "
        "soon break out to take revenge on the living, unless someone "
        "buries them deeper or brings their spirits peace.",
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "castelnaudry",
        "Castelnaudry and St. Martin-Lalande",
        inside=land,
        summary=(
            "A weak castle, which is why de Montfort went there in 1211, to "
            "lure Raimond and the Count of Foix into open battle. At nearby "
            "St. Martin-Lalande the southerners routed Bouchard de Marly's "
            "relief column, but de Montfort rode out with fifty knights, "
            "rallied the fugitives and fell on the southerners as they looted "
            "the baggage, turning their victory into a costly defeat. "
            "Afterwards the mercenary captain Savary de Mauléon kidnapped "
            "Raimond's son for his unpaid wages. Raimond's false claim that "
            "de Montfort had fallen sparked a revolt, crushed with great "
            "brutality."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "alairac",
        "The Ruins of Alairac",
        inside=land,
        realm="Infernal",
        aura=4,
        summary=(
            "A Visigothic mountain fortress that de Montfort stormed in a "
            "howling gale, throwing every defender from the battlements onto "
            "the rocks thousands of feet below. Bandits now lair in its "
            "shattered, bat-haunted towers, an almost endless wind whistles "
            "through them, and the ghosts of the dead seek burial for their "
            "broken bones. Infernal aura 4."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "prouille",
        "Fanjeaux and Prouille",
        inside=land,
        realm="Divine",
        summary="Fanjeaux, a small castle town on a hilltop, is where Dominic "
        "lived from 1206 to 1215 and led the preaching against the "
        "Cathars. Below it, at Prouille, he founded the nunnery of St "
        "Marie for women won back from Catharism and girls seeking the "
        "veil. Even Cathars honour his holiness, the more so since he "
        "drove off a demon here shaped like a huge cat with burning eyes "
        "and a long grasping tongue, a corrupted beast that may still "
        "roam the country. Once a heretic stronghold, the town now meets "
        "Cathars with threats and denounces them.",
        secrets="Perfecti keep slipping back into Fanjeaux at the risk of the "
        "stake; they are looking for something they left there.",
        **KNOWN_REGION,
    )
    castle = _add(
        provence,
        "aguilar",
        "Castle d'Aguilar",
        inside=land,
        summary=(
            "A fortress with six great towers on a dome of rock, Roman in "
            "origin and strengthened by the Visigoths, long home to many "
            "Cathars. A Trencavel castle, it was taken by de Montfort in 1210 and "
            "the de Termes family withdrew to Termes, but it was retaken in "
            "1213 and has been a centre of resistance ever since; the "
            "crusaders passed it by. Faidits and minor dispossessed nobles "
            "shelter within its walls and in the villages round about. Held "
            "in 1220 by the southern party, under the lords of Termes."
        ),
        **KNOWN_REGION,
    )
    grottoes = _add(
        provence,
        "aguilar_grottoes",
        "The Grottoes of Aguilar",
        inside=castle,
        aura=3,
        summary=(
            "A wide, little-known maze of natural caves riddling the rock "
            "under Castle d'Aguilar, with a Magic aura of 3, known to the "
            "Order of old as a mithraeum and a vis source. Here the Ostal des "
            "Exiles has its sanctums."
        ),
        **HIDDEN,
    )
    _add(
        provence,
        "aguilar_mithraeum",
        "The Mithraeum of Aguilar",
        inside=grottoes,
        aura=5,
        summary=(
            "Deep in the grottoes, a mithraeum with a Magic aura of 5, long "
            "used by Flambeau magi pursuing the Mithraic mysteries. The "
            "exiles have left it alone, but it lies inside their Aegis of the "
            "Hearth, and the Flambeau may soon find the new covenant on their "
            "doorstep and have to decide what to do about it."
        ),
        **KNOWN_ORDER,
    )


# --------------------------------------------------------- Tolosa Paratge


def _tolosa_paratge(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "An old, cosmopolitan covenant in a regio under the city of Toulouse, "
        "on an island in the ghost of a holy lake: nine magi of five Houses, a lone follower of Verditius among magi of Jerbiton, Flambeau, Criamon and Ex Miscellanea. "
        "It has outlasted centuries of Hermetic politics, but the crusade "
        "has split it in two, and Wizard's Wars between its own members "
        "have killed two magi and left the rest afraid. Its magi guard the "
        "city's genius loci and think of themselves as the city's servants; "
        "when the citizens turned on each other, madness and death came to "
        "the covenant too.",
        "It was founded in the Order's first generation as a Diedne "
        "covenant, among the four with which the Val-Negra Tribunal began, large for its day, with six or more magi for two "
        "centuries, and rumoured to excel at spirit magic, which gave it a "
        "faintly sinister name. Its refusal to admit Quaesitors after the "
        "mysterious death of the Tribunal's senior Tremere maga was among "
        "the first sparks of the Schism War. In that war Flambeau magi "
        "stormed it and slew its magi, and held the site until the "
        "Gorgiastic Cathar Anaïs arrived and rebuilt it as a covenant of "
        "many Houses. As the city grew the regio grew harder to reach, but "
        "the covenant rose in power and fame. Some think Anaïs's teaching, "
        "popular among the grogs, helped shape Cathar doctrine; others think "
        "the debt runs the other way. Its lineage of Gorgiastic Cathars, "
        "theurgical dualists, lives on here, and the survivors of Berinor "
        "joined it in 1210.",
        "A run of brilliant magi made it famous for culture and urbanity "
        "and for a quiet hand in the growth of Toulouse's institutions, the "
        "capitouls above all. Its magi kept ties with every power in the "
        "walls (guilds, bishop, capitouls, count), and the good of the city "
        "and the covenant held them together even when their meddling "
        "crossed. The leader, Augustus, a senior Quaesitor, saw that nobody "
        "looked too hard at their dealings with mundanes as long as the "
        "covenant and the Order came to no harm. Through the crusade it "
        "stayed loyal to the city and would serve no foreign master.",
        "In the weeks before de Montfort's death in 1218, Bishop Foulques "
        "persuaded Augustus that the city would fall, and he asked the "
        "Gorgiastic Cathars to leave for their own safety. They refused; one, "
        "Marc, called it betrayal of everything the covenant stood for and "
        "declared Wizard's War on him, a thing almost unheard of between "
        "covenant mates. Augustus did not take a Cathar pacifist seriously, "
        "but Marc, sure that Augustus was in a demon's grip, killed him in a "
        "muddled quarrel in the tower. A month later Carolus St. Tropez "
        "declared Wizard's War on Marc, who did not resist, and killed him. "
        "Mariola was made leader, but she did nothing, and the covenant "
        "broke into the Blacks, who side with the Cathars, and the Whites, "
        "who would expel the heretics for bringing ruin on their sodales. "
        "The Blacks are the stronger and hold the island; the Whites plot in "
        "the city to take it back, by appeal at the Tribunal of 1221 or by "
        "Wizard's War.",
        "A narrow path winds up the cliffs of a small rocky island to red "
        "brick townhouses round an eight-storey octagonal tower of black "
        "stone. A few covenfolk and some magi live on the island; many "
        "prefer the city. Summoned by a few lines of Occitan verse, an enchanted boat rows between the island's jetty and the last rooftop on the shore. "
        "The covenant keeps an inn in the city, thirty houses and some "
        "eighty covenfolk, many of them artisans or labourers in Toulouse. "
        "Beneath three of the houses lie well-equipped laboratories, "
        "despite the Dominion, and several magi keep sanctums in the city, "
        "working on the island by day and sleeping in Toulouse.",
        "Its people, the Tolosates, are proud of their place among the first "
        "covenants of the Order (few dare mention that it was Diedne then). "
        "Newcomers must serve ten years before full membership unless they "
        "were apprenticed and gauntleted here; visiting magi use "
        "Organization Lore: Tolosa Paratge in place of Etiquette; guests must "
        "be invited before crossing the lake; and hundreds of other customs "
        "go unmentioned to newcomers because the residents think them "
        "ordinary, sometimes with awkward or dangerous results. 'Paratge' "
        "means something like gentility: its magi are proud of Occitan "
        "language, poetry and culture, and famous across the Order as "
        "patrons of artists, poets, troubadours and original minds. Many a "
        "performer has been rowed to the impossible island to sing, and woke "
        "in his own bed afterwards wondering if he had dreamed it, beside a "
        "heavy purse of silver. Those apprenticed here wear a small silver "
        "flower, members a gold one, and members who were also apprenticed "
        "here a jewelled flower of gold and silver.",
        "Its covenfolk are split evenly between the factions. Most live in "
        "the city; about six grogs and a dozen covenfolk are besieged in "
        "the regio, their friends outside plot a rescue and may seek help "
        "from magi outside the city or by Redcap, and covenfolk of both sides "
        "brawl in the streets, drawing citizens into the fighting.",
    )
    what_matters = joined_lines(
        "Votes: 9 at Tribunal, divided between the factions",
        "Vis: none named in the book",
        "Income: an inn in Toulouse, thirty houses, and the trades of some eighty covenfolk in the city",
        "Library: the covenant's old collection (no books named); a borrowed text is stuck there since the split",
        "Laboratories: on the island, and under three of its city houses despite the Dominion",
        "Enchantment: Adam Carpentiere's boom at Pont-Vieux tames the Garonne and props up the fading regio",
        "Enchantment: a boat that answers a short Occitan poem and rows between the last roof and the island",
        "Treasure: rumoured to hide a legendary hoard, perhaps the gold Quintus Caepio tried to steal",
        "Customs: ten years' service before full membership; guests by invitation only; flowers of silver, gold or both by rank",
        "Customs: Organization Lore: Tolosa Paratge stands in for Etiquette for visiting magi",
        "Boon: Regio; Urban; Prestige (one of the Tribunal's oldest and most cultured covenants)",
        "Hook: Fractured Council (Whites against Blacks); Heretics (the Gorgiastic Cathars); Weak Aura (the regio is fading)",
        "Hook: City; Mundane Politics (ties to count, bishop, capitouls and guilds); Rebellious Covenfolk (fighting in the streets)",
        "Tension: the Blacks hold the regio; the Whites, too afraid to enter it, blockade it from labs in the city",
        "Tension: both sides deprive each other of magical resources, against the Code, but nobody has brought a case",
        "Tension: St. Tropez killed Marc in a lawful Wizard's War and may seek martyrdom before he is convicted of anything",
        "Tension: the Black faction may ask Stella Durus, through Cyprian's filius Renaud, to join it; the Whites may use Mariola's letters with Jean Marie of Stella Durus to keep it neutral or win it",
    )
    standing = paragraphs(
        "Votes and standing. Tolosa Paratge has nine votes at Tribunal, cast "
        "by faction. Most of the Tribunal believes it is destroying itself and "
        "has tacitly agreed, out of decorum, to let it settle its own affairs "
        "and see what is left; individual magi act on their opinions only "
        "behind the scenes. Renaud of Stella Durus worries for his pater "
        "Cyprian, and the Coenobium has always admired the covenant's style. "
        "Each faction wants the Coenobium, and the Ostal des Exiles, on its "
        "side. A new covenant that ignores the factions is ignored in turn; "
        "one that backs the wrong side may face Wizard's War. Its civil war "
        "may come before the Tribunal of 1221 if anyone brings a case.",
        "The founding year is not given: the covenant was one of the four "
        "that made up the Tribunal when the regional Tribunals were set up "
        "in 773.",
    )
    hidden = joined_lines(
        "The regio is tied to the prosperity of Toulouse as well as to the river: the city's conquest and strife weakened it, and the magi's feud mirrors the city's. Healing the city (a university, or championing Occitan learning) is the only lasting cure.",
        "Bishop Foulques came to the island as a gifted young troubadour; his memory of it may have been altered by magic, or he may think it a dream.",
        "Mariola is rumoured to be an initiate of the Matres & Matrones.",
        "Raimond of the Blacks believes he will drown in the Garonne and fears no other death.",
        "Adam joined the Whites over his debts to the Jewish moneylenders of Cahors and an old grudge against the Gorgiastics, who opposed his boom.",
    )
    tolosa = b.covenant(
        "Tolosa Paratge",
        tribunal=tribunal,
        founded=773,
        place=provence.places["tolosa_lake"],
        level=1,
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(standing),
        secrets=hidden,
        aura=3,
        unnamed_magi=4,
        season="Autumn",
    )
    provence.covenants["tolosa_paratge"] = tolosa
    _tolosa_magi(provence, b, tolosa)
    b.book(
        tolosa,
        "The library of Tolosa Paratge",
        "Other",
        description=(
            "The library of one of the Tribunal's oldest covenants, gathered "
            "since the Order's first generation and rich, one may suppose, in "
            "spirit lore from its Diedne past and in Occitan poetry from its "
            "patronage of troubadours; the book names none of its books. With "
            "the Blacks holding the island and the Whites working in the city, "
            "neither faction can freely use what the other holds. A valuable "
            "text lent before the split is somewhere inside, and its owners "
            "may send someone to fetch it."
        ),
    )


def _tolosa_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["mariola"] = b.magus(
        "Mariola",
        covenant=home,
        house=JERBITON,
        age=96,
        summary="Of House Jerbiton, leader of Tolosa Paratge, apprenticed there and "
        "fiercely proud of its heritage. After Augustus and Marc died she "
        "seemed the one magus both factions could accept, and was pushed "
        "into a leadership she never wanted. Her agents have long carried "
        "messages between Count Raimond's party and the bishop's, and she "
        "knows people in every corner of the city, though she has little "
        "sway with the capitouls. A strong Imaginem maga, she failed to "
        "act against St. Tropez after he killed Marc, and the covenant "
        "fell apart; too proud and inward-looking to ask for help, she "
        "has shut herself in her sanctum, sunk in doubt. She corresponds "
        "with Jean Marie of Stella Durus, who has fallen for her. Looks "
        "about eighty.",
        secrets="She is rumoured to belong to the Matres & Matrones.",
        traits={"Proud": 2, "Indecisive": 2, "Withdrawn": 2},
    )
    m["carolus_st_tropez"] = b.magus(
        "Carolus St. Tropez",
        covenant=home,
        house=JERBITON,
        age=54,
        summary="Of House Jerbiton, Mariola's former apprentice and still fond of "
        "her, leader of the White faction. He passes as a minor southern "
        "noble and keeps a small castle and household at Pujol outside "
        "the city, owing no liege. A Perdo specialist, he declared "
        "Wizard's War on Marc after Marc killed Augustus, letting years "
        "of resentment loose; Marc did not defend himself. Fearing the "
        "other Gorgiastics, he fled into the city, rallied many grogs and "
        "covenfolk to his white banner and swore to drive the heretics "
        "from the covenant and then from Toulouse; his Whites now try to "
        "blockade the regio, though no new Wizard's War has been declared. "
        "His great coup was winning the legate Arnaud Amalric to the "
        "southern cause and turning him against the French crown. He "
        "believes the Cathars brought God's judgement on the land and "
        "that only their destruction will spare it. No Tribunal has "
        "convicted him, and he may seek martyrdom attacking the "
        "Gorgiastics first. Looks about forty-two.",
        secrets="Arnaud Amalric does not know St. Tropez is a magus; he thinks "
        "the Order a loose fellowship of scholars and natural "
        "philosophers. St. Tropez also blames Marc for the crusader "
        "knights of Pujol, whom he thinks Marc controlled.",
        traits={"Vindictive": 3, "Determined": 2, "Pious": 1},
    )
    m["cyprian"] = b.magus(
        "Cyprian",
        covenant=home,
        house=FLAMBEAU,
        age=84,
        summary=(
            "A Flambeau magus who heads the Black faction, a Perdo Terram "
            "specialist and the pater of Renaud of Stella Durus. He has been a "
            "troubadour knight and an ardent Seeker after the Tribunal's lost "
            "magical secrets, and years posing as a knight errant and "
            "unmatched skill at arms made him the Blacks' natural leader. He "
            "is devoted to the covenant and to Mariola above all, and belongs to "
            "the Cult of Mercury. He is no Cathar, and finds their pacifism "
            "and mysticism rather tiresome, but he thinks Bishop Foulques "
            "betrayed the Church and his own honour, and St. Tropez's killing "
            "of the defenceless Marc and the anarchy after it have made him "
            "ready to fight his sodales, if only to defend his home. Looks "
            "about seventy-one."
        ),
        traits={"Dignified": 3, "Courageous": 2, "Foolhardy": 2},
    )
    m["adam_carpentiere"] = b.magus(
        "Adam Carpentiere",
        covenant=home,
        house=VERDITIUS,
        age=77,
        summary=(
            "A follower of Verditius in the White faction, steeped in "
            "Hermetic Architecture, with his sanctum and laboratory in a "
            "waterfront lacuna of Magic aura 2 in the city. He cares far more "
            "for the city's politics than his covenant's. He owes a great sum "
            "to the Jewish moneylenders of Cahors, so Bishop Foulques's "
            "railing against Jews and Cathars pleases him, and that alone "
            "made him a White. The Gorgiastics opposed his enchanted boom "
            "across the Garonne, fearing for the aura, and he has never "
            "forgiven them; since the Wizard's Wars he has backed St. Tropez "
            "as the covenant's best hope. Looks about sixty-five."
        ),
        traits={"Industrious": 3, "Hubris": 3, "Avaricious": 2},
    )
    m["raimond"] = b.magus(
        "Raimond",
        covenant=home,
        house=EX_MISC,
        age=41,
        summary=(
            "Of House Ex Miscellanea, a Gorgiastic Cathar of the Black "
            "faction and a sworn Cathar Good Man, though his theurgical faith "
            "is far from the Divine belief of ordinary Cathars. He is convinced his soul has passed through many lives, even through these very lives over and over in "
            "endless cycles of the world, and means to escape rebirth through "
            "Final Twilight and help hold open the way to the refuge outside "
            "time. So he acts unpredictably to break the pattern of his past "
            "lives, and seeks out Twilight as a way to step outside time. He "
            "does not fear dying against the Whites, sure that if he fails "
            "now he will win in a later cycle; besides, he knows he is fated "
            "to drown in the Garonne, so offensive magic holds no terror for "
            "him. Gorgiastic Cathars are prone to Twilight, keep a guardian "
            "spirit they call their Genius, and cast quietly. Looks about "
            "thirty-nine."
        ),
        traits={"Pacifist": 3, "Introspective": 2, "Serene": 1},
    )


# ------------------------------------------------------- Ostal des Exiles


def _ostal(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The House of the Exiles: the newest covenant of Provence, hidden in "
        "the caves under Castle d'Aguilar, where magi whose covenants the "
        "war destroyed have gathered. As the faidits are a force in the "
        "region's politics, so these Hermetic faidits have lost labs, "
        "libraries and homes; older magi have left for other Tribunals, but "
        "younger ones will not. Shocked by the ruin of Mistridge, Windgraven "
        "and Lariander, they formed the covenant after the Tribunal of 1214 "
        "to defend their homeland and Occitan civilisation. They welcome new "
        "Spring covenants as allies and recruit hard for the defence of the "
        "county against the northerners. More than outcasts, they may be "
        "outlaws: they are ready to meddle with mundanes to stop the south's "
        "destruction, even at the risk of a Wizard's March, though any blow "
        "they strike will be subtle, for they know what bringing ruin on "
        "one's sodales means.",
        "The grotto was known to the Order of old as a mithraeum and a vis "
        "source. Garsenda of Lariander survived the destruction of her "
        "covenant at Montgey in 1211; after Tres destroyed Mistridge in a "
        "Wizard's War, Rixenda was the first to take shelter at Aguilar; "
        "and in Gilbert of Flambeau, a magnetic figure, the exiles found both unity and purpose: resistance to the northerners whatever it "
        "costs. The Tribunal has not recognised the covenant. It does not "
        "formally owe the lords of Termes allegiance, but they know it is "
        "there and tolerate it. It is a clearing house for any magus willing "
        "to fight the crusade: four magi keep sanctums here, but the number "
        "present runs as high as eight or nine. It is an important centre of "
        "the Knights of the Green Stone, where that cult is used.",
        "Seven magi are members, four of them the leading figures. The "
        "covenfolk are mostly seasoned fighters, with few women or "
        "children, since many of the refugee women are celibate Cathars; if "
        "the covenant is to last, that must change. Few grogs live in the "
        "dark caves; most lodge in the villages round about. The turb drills "
        "constantly, backed by companions who are mostly faidits, minor lords, "
        "knights and serjeants, well horsed and armed, ready to risk "
        "everything for their homeland. Some of the maimed defenders of Bram "
        "serve as grogs, and Pons de Morlhon is among the companions.",
    )
    what_matters = joined_lines(
        "Votes: 6 counted at Tribunal, though the covenant is not yet recognised",
        "Vis: the grotto was a known vis source of old (Art and amount not given)",
        "Aura: Magic 3 in the grottoes; the Flambeau mithraeum within (Magic 5) lies inside their Aegis, untouched",
        "Library: next to nothing; the exiles' libraries burned with their covenants",
        "Boon: Natural Fortress (caves under a six-towered castle the crusaders passed by); Veteran Fighters; Hidden Ways",
        "Hook: Refugee; War Zone; Gender Imbalance (few women and children); Hermetic Politics (unrecognised)",
        "Mundane: shelters under the faidits of Aguilar and the lords of Termes, who tolerate them",
        "Allies: the Knights of the Green Stone, led by Gilbert, with links to the cult in the Rhine and Normandy",
        "Tension: Gilbert's vengeance against Rixenda's hope of acceptance by the Tribunal",
        "Tension: Popilia hates all Cathars, Gorgiastics included, while Rixenda and Garsenda sympathise with them",
        "Tension: none of the exiles has forgiven Tres for Mistridge",
        "Tension: the Flambeau of the mithraeum may soon find them and must decide what to do",
        "Tension: the Coenobium hates Gilbert for leaving House Jerbiton for Flambeau",
    )
    standing = paragraphs(
        "Votes and standing. The Ostal counts six votes in the Tribunal's "
        "reckoning, but the Tribunal has not recognised it, and its "
        "recognition is an open question for 1221. It weighs every covenant "
        "by what it could give the cause and what it could take in return, "
        "courts Stella Durus for Renaud's experience, and will press at "
        "Glanum, with the other faidits, for licence to defend themselves and "
        "to win back what the crusade took, looking for support from Garus and Castra Solis's milites. Aedes Mercurii thinks it draws "
        "crusaders' eyes to the Order; Castra Solis admires its spirit but "
        "would rather fold its magi into quieter covenants; the Coenobium "
        "would temper its zeal or bring it under its own direction; both "
        "factions of Tolosa Paratge would like its help.",
        "The founding year is not given; the covenant took shape after the "
        "Tribunal of 1214.",
    )
    hidden = joined_lines(
        "Garsenda roused the villagers of Montgey, with the demesoilles, to massacre the crusader column in 1211, and so brought the crusaders down on Lariander. She dreads the Order learning she brought ruin on her sodales.",
        "Gilbert may be a mystagogue of the Knights of the Green Stone; Garsenda met him through an esoteric cult, perhaps the same.",
        "Gilbert has boasted that he would fight a second Schism War for his homeland even if the Grand Tribunal condemned him.",
    )
    ostal = b.covenant(
        "Ostal des Exiles",
        tribunal=tribunal,
        founded=1215,
        place=provence.places["aguilar_grottoes"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(standing),
        secrets=hidden,
        aura=3,
        unnamed_magi=3,
        season="Spring",
    )
    provence.covenants["ostal_des_exiles"] = ostal
    _ostal_magi(provence, b, ostal)
    b.book(
        ostal,
        "The library of the Ostal des Exiles",
        "Other",
        description=(
            "Hardly a library at all: the exiles' books burned with Mistridge, "
            "Lariander and the other fallen covenants, and only what each "
            "magus carried out survives. The book names no books; a covenant "
            "that could offer texts would win the exiles' gratitude."
        ),
    )


def _ostal_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["gilbert"] = b.magus(
        "Gilbert",
        covenant=home,
        house=FLAMBEAU,
        age=95,
        summary="Of House Flambeau, the exiles' leader, born near Marseilles of "
        "noble blood, Gently Gifted, and an ardent follower of Apromor's "
        "Perdo tradition. Apprenticed late, at the Coenobium, he passed "
        "his Gauntlet as a Jerbiton and wandered the Tribunal for years, "
        "careless of its politics; his move to House Flambeau earned the "
        "Coenobium's undying hatred. Cultured and polished, he is known "
        "across the region as a knight and romantic troubadour, and few "
        "of the noble ladies who favour him know he is a magus. Long an outsider among magi, he found a purpose "
        "when Lariander fell and the Tribunal began to buckle; after "
        "Mistridge he saw it coming apart. Love of battle has replaced "
        "courtly love, solitude has given him the strength to lead, and "
        "he has vowed to defend the Order against all its foes and to cut down anyone who hinders him. Charismatic and unstable, he leads "
        "the Knights of the Green Stone here. Looks about forty.",
        secrets="Few care to test whether his boast of a second Schism War is only talk.",
        traits={"Aloof": 3, "Vengeful": 2, "Genteel": 1},
    )
    m["rixenda"] = b.magus(
        "Rixenda Mistridge",
        covenant=home,
        house=JERBITON,
        age=40,
        summary=(
            "Of House Jerbiton, the first exile to settle at Aguilar after Tres "
            "destroyed Mistridge, who welcomed Gilbert and the others as they "
            "came. Where Gilbert stands for the anger of the wronged, she "
            "stands for rebirth: a Mentem maga drawn to dreams and nightmares, "
            "she wants the Tribunal's acceptance, not revenge, and thinks the "
            "Order's future may lie in hiding from the world. Her calm good "
            "sense makes her a real rival to Gilbert. No Cathar, she "
            "sympathises with them and writes to some learned Perfectae, "
            "though she cannot see why they hold so woman-hating and "
            "world-denying a faith, and quietly uses her influence to protect "
            "the best women scholars. She was appalled by Marc's war on "
            "Augustus and is one of the few magi to have watched Tolosa "
            "Paratge's collapse closely. Like the other exiles she has not "
            "forgiven Tres, and knows her alliance with Gilbert is a "
            "dangerous one. Looks about thirty-eight."
        ),
        traits={"Forgiving": 2, "Optimistic": 2},
    )
    m["garsenda"] = b.magus(
        "Garsenda of Lariander",
        covenant=home,
        house=TREMERE,
        age=35,
        summary="Of House Tremere, only a few years past her Gauntlet when "
        "Lariander was destroyed; she fled into the forest and somehow "
        "lived, the only survivor she knows of. A Seeker after the "
        "magical secrets of antiquity, above all those of faerie powers "
        "once worshipped as gods, she is now chasing tales of the Drac, "
        "dragonish creatures said to haunt the region's rivers, and is "
        "troubled by strange dreams. An Imaginem specialist, she dresses "
        "as an outlaw rather than a knight, is close to several local "
        "demesoilles, and shares their zeal for the poor and oppressed. "
        "She sympathises with the Cathars only because she questions "
        "every authority by nature, and has no religion. Guilt makes her "
        "jumpy and short-tempered with magi she does not know.",
        secrets="Her part in the Montgey massacre brought the crusaders down on "
        "Lariander, and she fears the Order will learn of it. She may be "
        "a Knight of the Green Stone, and met Gilbert through an esoteric "
        "mystery cult.",
        traits={"Troubled": 2, "Brash": 2, "Vengeful": 1},
    )
    m["popilia"] = b.magus(
        "Popilia",
        covenant=home,
        house=EX_MISC,
        age=60,
        summary=(
            "Of House Ex Miscellanea, a Pharmacopoeian who came to the Order "
            "late, after her village cast her out. A midwife and herbalist, "
            "she clashed with Sicart of Lavaur, a Perfectus who damned "
            "childbirth as the worst of sins and reviled sex and the raising "
            "of children; when he attacked her she went at him with a knife "
            "and was banished for it. She still broods on it and hates the "
            "Cathars, the Gorgiastics included, as fiercely as she resists "
            "the northerners, and the crusade has only convinced her the "
            "heretics brought this horror on the south. She has three "
            "children, two grown and the youngest, Jacquemart, fifteen. "
            "Looks about fifty-one."
        ),
        traits={"Angry": 3, "Proud": 2, "Protective": 1},
    )


# ------------------------------------------------------------ the world


def _lords(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["count_of_toulouse"] = b.lord(
        "Count of Toulouse",
        title="count",
        wealth="Wealthy",
        manors=40,
        seat="The Château Narbonnais, Toulouse",
        ruler="Raimond VI",
        place=p["toulousain"],
        arms=Arms(field="Gules", charge="Cross", charge_tincture="Or"),
        summary=paragraphs(
            "Raimond VI has ruled since 1194, easy-going and tolerant, and "
            "has never tried to win back the power the capitouls took in "
            "1188. The crusade stripped him of many titles; after losing "
            "Toulouse he spent four years in exile, much of it at the papal "
            "court with his son pleading for his lands, while Simon de "
            "Montfort named himself count in 1216. He came back in 1217 and "
            "has won back many vassals; de Montfort died besieging him in "
            "1218 and Prince Louis's royal army was turned back in 1219. In "
            "1220 he holds his city firmly and much of the county by force of "
            "arms, and works tirelessly to be recognised again as its "
            "rightful count, a title Amaury de Montfort also claims; whether "
            "he can make terms with the French crown and the pope and leave "
            "the county to his son is still in doubt.",
            "His heir is his loyal son Raimond; Raimond's daughter Joan, born "
            "in 1220, will inherit only if he has no son. Bishop Foulques is "
            "his implacable enemy, but the legate Arnaud Amalric has lately "
            "made peace with him. He let his brother Baudouin, who had gone "
            "over to the crusade, be hanged at Montauban in 1214 and watched "
            "with approval.",
            "The arms shown are Toulouse's red and gold; the real charge is "
            "the voided, pommelled cross of Toulouse, which the app draws as "
            "a plain cross. The number of manors is a guess; the book gives "
            "none.",
        ),
    )
    w["amaury_de_montfort"] = b.lord(
        "Amaury de Montfort",
        title="count",
        wealth="Average",
        seat="Carcassonne",
        ruler="Amaury de Montfort",
        place=p["carcasses"],
        arms=Arms(field="Gules", charge="Lion", charge_tincture="Argent"),
        summary=paragraphs(
            "Simon de Montfort's son, who claims his father's titles: Count of "
            "Toulouse and Viscount of Béziers and Carcassonne. Since Simon "
            "was killed in 1218 the great domain he carved out has been "
            "falling apart, and in 1220 Amaury hangs on to Carcassonne, where "
            "his father lies in St Nazaire, and to the crusader garrisons "
            "scattered through the county. His mother, Alice de Montfort, "
            "remains a leader and strategist of the campaign; she was forced "
            "to give up the Château Narbonnais when Raimond returned in 1217.",
            "The Montfort lion has a forked tail, which the app draws as a plain lion.",
        ),
    )
    amaury = w["amaury_de_montfort"]
    w["trencavel"] = b.lord(
        "Raimond II Trencavel",
        title="landed",
        wealth="Poor",
        seat="Carcassonne (claimed)",
        ruler="Raimond II Trencavel",
        place=p["carcasses"],
        summary=(
            "The seventeen-year-old heir of the Trencavel viscounts of Béziers "
            "and Carcassonne, dispossessed by Simon de Montfort. His father "
            "Raimond-Roger was seized during talks under a supposed "
            "safe-conduct in the siege of 1209 and died in his own dungeon, "
            "of dysentery or poison. The young viscount is trying to reclaim "
            "his title, and many local clergy pushed out by northern priests "
            "back him; Castres looks to the Montforts instead."
        ),
    )
    w["lords_of_termes"] = b.lord(
        "Lords of Termes",
        title="landed",
        wealth="Average",
        seat="Termes (to be retaken)",
        ruler="Oliver and Bernard of Termes",
        place=p["termes"],
        answers_to=w["trencavel"],
        summary=(
            "The sons of Termes's defender, dispossessed by de Montfort, who "
            "are said to be coming home with their men in spring 1220 to take "
            "Termes back. Their family held Castle d'Aguilar, lost it in 1210 "
            "and won it back in 1213; the Hermetic exiles in its caves owe "
            "them no formal fealty, but the family knows of them and lets "
            "them be."
        ),
    )
    w["st_tropez_pujol"] = b.lord(
        "Lord of Pujol",
        title="landed",
        wealth="Average",
        seat="Pujol",
        ruler="Carolus St. Tropez",
        place=p["pujol"],
        summary="A minor southern noble who holds the small castle of Pujol, three "
        "miles from Toulouse, owing allegiance to nobody, and won it back "
        "from the crusaders in 1213. He has befriended the legate Arnaud "
        "Amalric, who often stays with him and has been swayed by him "
        "against the French.",
        secrets="The lord is Carolus St. Tropez of Tolosa Paratge, leader of its "
        "White faction.",
    )
    w["gui_de_lucy"] = b.lord(
        "Gui de Lucy",
        title="landed",
        seat="Lavaur",
        ruler="Gui de Lucy",
        place=p["lavaur"],
        answers_to=amaury,
        summary=(
            "The crusader who holds Lavaur in 1220. He admits Na Geralda's killing was a crime and wants her bones and her memory left "
            "undisturbed; he and his men will turn on anyone who tries to "
            "lay her ghost, which they cannot see and do not believe in."
        ),
    )
    w["lambert_de_thury"] = b.lord(
        "Lambert de Thury",
        title="landed",
        seat="Castle Puivert",
        ruler="Lambert de Thury",
        place=p["puivert"],
        answers_to=amaury,
        summary=(
            "The crusader who has ruled Castle Puivert since it fell to de "
            "Montfort in 1210, taking it from Bernard of Congost. His wife, "
            "the Lady de Thury, keeps the castle's custom of welcoming "
            "troubadours, and with it the jealousy of the lake's faerie lady."
        ),
    )
    w["bouchard_de_marly"] = b.lord(
        "Bouchard de Marly",
        title="landed",
        seat="Saissac",
        ruler="Bouchard de Marly",
        place=p["saissac"],
        answers_to=amaury,
        summary=(
            "De Montfort's kinsman and loyal friend, who spent sixteen months "
            "chained in the dungeons of Cabaret until its surrender in 1211, "
            "and whose relief column was routed at St. Martin-Lalande. He "
            "holds Saissac in 1220 against its dispossessed heirs."
        ),
    )
    w["pierre_roger_de_cabaret"] = b.lord(
        "Pierre-Roger de Cabaret",
        title="landed",
        wealth="Poor",
        seat="Cabaret (claimed)",
        ruler="Pierre-Roger de Cabaret",
        place=p["lastours"],
        answers_to=w["trencavel"],
        summary=(
            "The faidit lord of the three castles of Lastours, a friend of the "
            "Cathars and a lavish host to troubadours, who had to surrender "
            "them in 1211 but was never caught. He is working to get his lands "
            "and fortresses back, and with the crusade faltering he may "
            "succeed. His brother Jourdain, lord of Pennautier, is husband "
            "of Na Loba."
        ),
    )


def _churches(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["bishop_of_toulouse"] = b.church(
        "Bishop of Toulouse",
        church="Bishop's cathedral",
        order="secular clergy",
        ruler="Foulques de Marseille",
        place=p["saint_etienne"],
        summary=paragraphs(
            "Foulques de Marseille, among the most powerful and divisive "
            "men in the region, hated by most of Toulouse, even former "
            "friends of the Church. A celebrated troubadour in his youth, "
            "he turned from his old life after a vision twenty-five years "
            "ago, and now weeps and does harsh penance whenever a song of his reaches his ears, appalled that his sins outlive him. As a "
            "churchman he fights the south's easy morals and has three "
            "great hates, heretics, troubadours and moneylenders, and "
            "since many lenders are Jews he has come to dislike the Jews.",
            "He backs Dominic's preaching mission. Replacing a corrupt, "
            "indifferent predecessor, he needed the pope's help to take "
            "his cathedral and an armed guard at all times, and grew to "
            "return the city's hatred; by the time the crusade was called "
            "he could no longer safely enter his see, and joined the "
            "crusaders. Count Raimond tried to win him, even giving him "
            "the Château Narbonnais, but they became bitter enemies. In "
            "1220 he rides with the crusaders, pressing for Toulouse to be captured and the heretics wiped out, and he favours an "
            "Inquisition of clerical investigators to hunt heresy. In "
            "1209 he founded the White Brotherhood.",
            "He knows of the Order and, through dealings with the "
            "Quaesitor Augustus, respects it, but has no idea of its real "
            "power or of its Cathar magi; he thinks the scholars of "
            "Toulouse practise natural magic. Proof of heretic magi "
            "against his faith would make him a terrible enemy of the "
            "Order and add it to the crusade's targets unless the pope "
            "forbade it.",
        ),
        secrets="As a young man he went to Tolosa Paratge as a gifted "
        "troubadour; his mind may have been magically changed afterwards, "
        "or he may have put it down to a dream. He is a great latent "
        "danger to the Order in the south.",
    )
    bishop = w["bishop_of_toulouse"]
    w["arnaud_amalric"] = b.church(
        "Arnaud Amalric, Papal Legate",
        church="Archbishop's cathedral",
        order="Cistercian",
        ruler="Arnaud Amalric",
        place=p["pujol"],
        summary=paragraphs(
            "For twenty years the leading figure in the Church's effort to reclaim the south from heresy, a Cistercian of great learning who rode with "
            "de Montfort, presided over the burning of Cathars and the "
            "massacre of those who resisted, and is credited with the "
            "notorious order at Béziers to kill everyone and let God sort "
            "out his own. Made bishop (archbishop) of Narbonne in 1212, "
            "he has defended the local Church against northern "
            "appointees, and he never supported French claims to the "
            "land.",
            "In 1220 he has made peace with Count Raimond, convinced at "
            "last of his piety and alarmed at the threat the French crown "
            "poses to southern culture; he keeps a soft spot for Alice and Amaury de Montfort while standing hard against the French push south. "
            "Since de Montfort's death he has befriended the young knight "
            "Carolus St. Tropez and often stays at his castle of Pujol. He "
            "thinks the Order a loose fellowship of scholars and natural "
            "magicians, and likes it as long as it heeds the Church; if he "
            "found it sheltering heretics he would turn the curia against "
            "it unless it cast them out.",
        ),
        secrets="He does not know St. Tropez is a magus, and St. Tropez's "
        "influence has hardened him against the French and woken his "
        "southern sympathies.",
    )
    w["saint_sernin_abbey"] = b.church(
        "Basilica of Saint-Sernin",
        church="Monastery or nunnery",
        order="Augustinian canons",
        ruler="Abbot Jordan Giordano",
        place=p["saint_sernin"],
        answers_to=bishop,
        summary=(
            "The great pilgrim church of Toulouse, kept by Augustinian canons "
            "under their compassionate abbot Jordan Giordano, who runs its "
            "college and the hospice for the city's poor. Summer brings "
            "crowds of pilgrims to its relics, and a poetry contest is held "
            "in its orchard."
        ),
    )
    w["saint_pierre_des_cuisines"] = b.church(
        "Saint-Pierre des Cuisines",
        church="Parish church",
        order="Benedictine (of Moissac)",
        place=p["la_pierre"],
        answers_to=bishop,
        summary=(
            "The oldest church site in the Tribunal, rebuilt two centuries "
            "ago and owned by the monks of Moissac: the poor relation of the "
            "city's churches, yet the place where the counts hold court and "
            "swear to the people and the capitouls proclaim their laws. Its "
            "steps hold a Magic lacuna of aura 1."
        ),
    )
    w["la_daurade"] = b.church(
        "Our Lady of the Sea Bream (La Daurade)",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["daraude"],
        answers_to=bishop,
        summary=(
            "A domed basilica of twelve walls glittering with gold mosaic, built on a Roman "
            "temple of Apollo and attached to a Benedictine monastery, home "
            "of the Black Madonna, Notre-Dame Noire. It hosts the flower "
            "procession and feast each early May. In history the Saint-Sernin "
            "poetry contest moves here within the decade and grows into the "
            "Festival of the Flowers, with gold and silver flowers for the "
            "best Occitan verse."
        ),
    )
    w["bishop_of_carcassonne"] = b.church(
        "Bishop of Carcassonne (St Nazaire)",
        church="Bishop's cathedral",
        order="secular clergy",
        ruler="Gui de Vaux-de-Cernay (contested)",
        place=p["carcasses"],
        summary="A Romanesque cathedral, which some crusaders want rebuilt in the "
        "Gothic style, holding the tomb of Simon de Montfort. The northern "
        "lords prefer clergy who came with the crusade, and many local "
        "priests have lost their posts and gone over to the Trencavel "
        "heir. Gui de Vaux-de-Cernay was made bishop in 1212, replacing Bernard Raimond de Roquefort, dismissed for sympathy "
        "with the Cathars (his mother and brother among them), but "
        "Bernard still claims the see and disputes Gui's appointment. Gui "
        "defrocked the treacherous priest of Montreal at Bram.",
        secrets="On the feast of Saint Nazarius Gui may suddenly cry out from the "
        "altar that he is a usurper and hand his mitre to Bishop "
        "Raimond, then at sunset claim he was bewitched and accuse "
        "Raimond of sorcery.",
    )
    w["albi_cathedral"] = b.church(
        "Cathedral of Saint Cecilia, Albi",
        church="Bishop's cathedral",
        order="secular clergy",
        place=p["albigeois"],
        summary=(
            "The stone cathedral that towers over red-brick Albi, though few "
            "of the townsfolk come to Mass."
        ),
    )
    w["castres_abbey"] = b.church(
        "Abbey of St. Benoît, Castres",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["albigeois"],
        summary=(
            "The Benedictine monastery round which Castres grew. In 1209 two "
            "Cathar Good Men handed over by the consuls were burned in the "
            "market, the crusade's first Cathar victims; one had recanted, "
            "and the clergy burned him anyway lest his repentance be false, "
            "but his chains fell away in the flames and he walked out "
            "unhurt, and was spared."
        ),
    )
    w["prouille"] = b.church(
        "Nunnery of St. Marie, Prouille",
        church="Monastery or nunnery",
        order="Dominican",
        ruler="Founded by Dominic",
        place=p["prouille"],
        summary=(
            "The house Dominic founded below Fanjeaux as a home for converted Cathar women and for girls with a calling, while "
            "he preached from Fanjeaux between 1206 and 1215."
        ),
    )
    w["villeneuve_sepulchre"] = b.church(
        "Monastery of the Holy Sepulchre, Villeneuve",
        church="Monastery or nunnery",
        order="Cluniac",
        place=p["morlhon"],
        summary=(
            "Built by Odo de Morlhon after a vision on crusade bade him found "
            "a house in honour of the Holy Sepulchre; it is now under Cluny."
        ),
    )
    w["villedieu_templars"] = b.church(
        "Templar Commandery of Villedieu-du-Temple",
        church="Chapel",
        order="Knights Templar",
        place=p["villedieu"],
        summary=(
            "The Templars here buried Baudouin of Toulouse after one of their "
            "knights cut him down from the gallows. They keep largely out of "
            "the war, though their sympathies are with the crusaders."
        ),
    )


def _towns(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    count = w["count_of_toulouse"]
    amaury = w["amaury_de_montfort"]
    lord, church, commune = "Noble lord", "Church", "Commune"

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "toulouse",
        "Toulouse",
        "One of the largest and richest cities in Mythic Europe, ruled in "
        "practice by its twelve capitouls, two from each of six districts, "
        "elected every seven years (or on a death) by householders of good "
        "standing who meet a wealth test. Raimond IV set up a chapter of "
        "four lawyers, two judges and six sheriffs in 1154 to judge trade "
        "and law for him, in return for unnamed favours from the Order, "
        "whose Tribunals it copies; in 1188 the elected sheriffs threw out "
        "the lawyers and judges and took over the guard, the militia, war, "
        "taxes and trade, and Raimond V let it pass. They sit in the "
        "Capitole, houses bought in 1190 and knocked into one, hearing "
        "petitions, trade disputes, taxes, guild law and justice; a simple "
        "majority makes a law, and a favourable ruling often takes wealth, "
        "influence or a story to earn. Former capitouls are treated as "
        "minor nobility for life and keep the title 'sheriff'. Held in 1220 "
        "by Count Raimond VI.",
        charter=commune,
        council=12,
        ruler="The Capitole, under Count Raimond VI",
        answers_to=count,
        place=p["toulouse_city"],
        arms=Arms(field="Gules", charge="Cross", charge_tincture="Or"),
    )
    town(
        "albi",
        "Albi",
        "A red-brick town on the Tarn and an old Cathar stronghold, which "
        "met the legate Alberic of Ostia with drums, donkeys and jeers. St "
        "Bernard won many over for a while, but the heresy is still strong "
        "despite the garrison Simon de Montfort put there. Held in 1220 by "
        "a crusader garrison.",
        charter=lord,
        ruler="A crusader garrison",
        answers_to=amaury,
        place=p["albigeois"],
    )
    town(
        "castres",
        "Castres",
        "A fortified town round the abbey of St. Benoît between the Agout "
        "and the Durenque, its upper storeys jutting out over the water. Its "
        "consuls surrendered to de Montfort in September 1209, handing over "
        "two Cathars, and still favour the crusade, looking to France and "
        "the Montforts rather than to the Trencavel heir. Held in 1220 by "
        "its consuls, for the Montforts.",
        charter=commune,
        ruler="Its consuls, loyal to the Montforts",
        answers_to=amaury,
        place=p["albigeois"],
    )
    town(
        "lavaur",
        "Lavaur",
        "A small Trencavel town on the Agout with a cathedral of St Alan, "
        "infamous as a nest of heresy, stormed in 1211 with terrible "
        "slaughter; now a crusader stronghold. Held in 1220 by Gui de Lucy "
        "for the crusade.",
        charter=lord,
        ruler="Gui de Lucy",
        answers_to=w["gui_de_lucy"],
        place=p["lavaur"],
    )
    town(
        "agen",
        "Agen",
        "The chief town of the county's wooded, sheep-rearing north, "
        "prosperous on fine wool, where the heretics are very strong. The "
        "book does not say who holds it in 1220.",
        charter=lord,
        place=p["agenais"],
    )
    town(
        "cahors",
        "Cahors",
        "A city notorious for its moneylenders, in the Jewish quarter and "
        "outside it, condemned by the Church. Since Toulouse banned "
        "mortgages and loans at the Church's insistence about twenty years "
        "ago, Cahors is where one goes to raise money fast. Its towns live "
        "by the black wine. The book does not say who holds it in 1220.",
        charter=lord,
        place=p["cahors_vineyards"],
    )
    town(
        "montcuq",
        "Montcuq",
        "A Cathar stronghold with a small castle, taken by de Montfort in "
        "summer 1212 and handed to Raimond's brother Baudouin, who had taken the crusaders' side against his own family. It went back to the "
        "Toulousain cause, and Baudouin was brought here captive from "
        "Lolmie in 1214. Held in 1220 for Count Raimond.",
        charter=lord,
        ruler="Count Raimond VI",
        answers_to=count,
        place=p["agenais"],
    )
    town(
        "montauban",
        "Montauban",
        "The town outside whose walls Baudouin of Toulouse was hanged from a "
        "walnut tree for treason in 1214, as Raimond and the Count of Foix "
        "looked on. Held in 1220 for Count Raimond.",
        charter=lord,
        ruler="Count Raimond VI",
        answers_to=count,
        place=p["toulouse_hinterland"],
    )
    town(
        "carcassonne",
        "Carcassonne",
        "A great city of the Trencavels, often defiant of its lords (it "
        "drove them out in 1107 and from 1120 to 1124) and called "
        "ungovernable, yet loyal to Viscount Raimond-Roger until he was "
        "taken by treachery in 1209. It is named, they say, for Lady Carcas, "
        "a Saracen commander's wife who under Charlemagne's siege fed the "
        "last grain to the last pig and flung it over the wall, so that the "
        "besiegers, seeing grain burst from it, gave up on a city so well "
        "fed. In 1220 it has one Visigothic wall over Roman work and an "
        "eleventh-century stone castle. Almost all its people were driven "
        "out after the fall, but most came back, and as the crusaders' base "
        "it prospers; resentment of the northerners runs high, but with so "
        "many knights quartered there rising would be hopeless. Held in "
        "1220 by Amaury de Montfort.",
        charter=lord,
        ruler="Amaury de Montfort",
        answers_to=amaury,
        place=p["carcasses"],
    )
    town(
        "bram",
        "Bram",
        "A small walled town whose hundred defenders were blinded and "
        "mutilated after a three-day siege; its market keeps an Infernal "
        "aura of 3. The book does not say who holds it in 1220, but it "
        "fell to the crusade.",
        charter=lord,
        place=p["bram"],
    )
    town(
        "fanjeaux",
        "Fanjeaux",
        "A town on a hill crowned by a small castle, once a heretic stronghold and "
        "Dominic's home while he preached; its people fled the crusaders in "
        "1209, and now nobody there dares shelter a Cathar. The book does "
        "not name its lord in 1220; the town sides with the Church and the "
        "crusade.",
        charter=church,
        place=p["prouille"],
    )


def _factions(provence: Provence, b: Builder) -> None:
    w = provence.world
    p = provence.places
    w["white_brotherhood"] = b.faction(
        "The White Brotherhood",
        faction="Other",
        decides="Its leader",
        place=p["toulouse_city"],
        ruler="Founded by Bishop Foulques",
        wants="Heresy and usury rooted out of Toulouse",
        summary=(
            "A society of Toulousain citizens Bishop Foulques raised in 1209 "
            "to take up arms against heretics and moneylenders, oppose Count "
            "Raimond and back the crusade, named for the white robes and "
            "hoods they wore for their midnight arrests and terror. Loyal to "
            "the Church but also to their city, they broke when the bishop "
            "and many clergy slipped away during de Montfort's siege, and "
            "many, fearing another Béziers, fought the crusaders. Guilty of "
            "murder, lynching and riot, they are now a small, violent "
            "fanatical core that still prowls the streets at night; their "
            "legacy is a strong hatred of Jews among former Whites and the "
            "ban on usury. Membership can be the Flaw Dark Secret."
        ),
    )
    w["black_brotherhood"] = b.faction(
        "The Black Brotherhood",
        faction="Other",
        decides="Its leader",
        place=p["toulouse_city"],
        wants="The Cathars and Jews of Toulouse protected from the Whites",
        summary=(
            "Formed in answer to the White Brotherhood, mostly from the "
            "suburbs and the countryside, it fought the Whites in the streets "
            "to protect Cathars and Jews, and committed atrocities of its "
            "own. Since the siege ended it has dwindled to a small, violent "
            "fanatical core that still lurks in the streets after dark. "
            "Membership can be the Flaw Dark Secret."
        ),
    )
    w["tolosa_whites"] = b.faction(
        "The Whites of Tolosa Paratge",
        faction="Other",
        decides="Its leader",
        ruler="Carolus St. Tropez",
        place=p["toulouse_city"],
        wants="The Gorgiastic Cathars expelled from the covenant, then from the city",
        summary=(
            "The faction of Tolosa Paratge that sides with Bishop Foulques "
            "and would expel the heretics for bringing ruin on their sodales: "
            "St. Tropez, Adam Carpentiere and the grogs and covenfolk who "
            "rallied to St. Tropez's white banner. Too afraid to enter the "
            "regio, they keep laboratories and a fortified tower in the city "
            "and try to blockade the island, waiting to retake it by appeal "
            "to the Tribunal in 1221 or by Wizard's War. The White "
            "Brotherhood counted some magi among its supporters."
        ),
    )
    w["tolosa_blacks"] = b.faction(
        "The Blacks of Tolosa Paratge",
        faction="Other",
        decides="Its leader",
        ruler="Cyprian of Flambeau",
        place=p["tolosa_lake"],
        wants="The Gorgiastic Cathars kept safe from the Whites and the crusade",
        summary=(
            "The stronger faction of Tolosa Paratge, holding the regio and "
            "favouring the Cathar cause: Cyprian, who leads it though no "
            "Cathar, and the Gorgiastic Cathar Raimond, with about six grogs "
            "and a dozen covenfolk besieged on the island, fearing to leave "
            "and waiting for the next Wizard's War. The Black Brotherhood "
            "counted some magi among its supporters."
        ),
    )
    w["faidits_of_toulouse"] = b.faction(
        "The Faidits",
        faction="Other",
        decides="A council",
        place=p["toulousain"],
        wants="Their lands back, by papal favour or by the sword",
        offers="Seasoned, well-mounted fighting men",
        summary=(
            "Knights and minor lords stripped of their lands by the crusade, "
            "landless and lordless, sheltering in castles such as Aguilar, "
            "Puilaurens and Cabaret and in friendly villages; in 1220 they "
            "are coming home, as the sons of Termes are. Among them are Pons "
            "de Morlhon, counselled by the ghosts of seven Waldensian "
            "martyrs, Pierre-Roger de Cabaret, and the heirs of Saissac. The "
            "Hermetic exiles of Aguilar call themselves Hermetic faidits, and "
            "many faidits serve them as companions."
        ),
    )
    w["na_loba"] = b.faction(
        "Na Loba and her Daughters",
        faction="Family",
        decides="Its leader",
        ruler="Auda (Na Loba)",
        place=p["lastours"],
        wants="Their birthright, the three castles of Lastours",
        offers="Charm, intrigue and marriage alliances",
        summary="Auda, called Na Loba, the She-Wolf, once the beauty of Fleur "
        "Epine, and her three daughters, who have a strong claim to the "
        "castles of Lastours. With no Trencavel overlord left to answer to, the daughters seek husbands rather than wait for them, and use their dark allure to "
        "snare good husbands, while the old woman remains a formidable "
        "schemer; they travel the country looking for powerful allies.",
        secrets="Peasants whisper that the daughters are werewolves, and anyone "
        "who says so soon vanishes. Na Loba betrayed Raimond-Roger "
        "Trencavel to de Montfort in 1209 out of jealousy.",
    )
    w["cahors_moneylenders"] = b.faction(
        "The Moneylenders of Cahors",
        faction="Gild",
        decides="A council",
        place=p["cahors_vineyards"],
        wants="Their loans honoured and their trade left alone",
        offers="Ready money, at interest",
        summary=(
            "The moneylenders of Cahors, Jewish and Christian, who took over "
            "the business of lending when Toulouse outlawed it; Bishop "
            "Foulques loathes them, and the former Whites threaten the Jews "
            "among them. Adam Carpentiere of Tolosa Paratge owes them a "
            "large sum."
        ),
    )


# --------------------------------------------------------------- stats

P = Profile
OCCITAN = "Occitan"


#: The apparent age the book gives each magus, by character id.
APPARENT = {
    "mariola": 80,
    "carolus_st_tropez": 42,
    "cyprian": 71,
    "adam_carpentiere": 65,
    "raimond": 39,
    "gilbert": 40,
    "rixenda": 38,
    "garsenda": 35,
    "popilia": 51,
}

#: Each magus the book sketches without a stat block, by provence.magi key.
PROFILES: dict[str, Profile] = {
    "mariola": P(
        strong="pre com int",
        arts={"Im": 8, "Cr": 4, "Mu": 4, "Me": 3, "In": 2},
        abilities={
            "Area Lore: Toulouse": (3, "factions"),
            "Etiquette": (3, "nobles"),
            "Intrigue": (2, "Toulouse"),
            "Organization Lore: Tolosa Paratge": 3,
            "Civil and Canon Law": 1,
        },
        virtues=[
            ("Social Contacts", {"group": "the count's and the bishop's factions"}),
            vf_art("Affinity with {art}", "imaginem"),
            "Proud (Minor)",
            "Covenant Upbringing",
        ],
        native=OCCITAN,
    ),
    "carolus_st_tropez": P(
        strong="pre int com",
        arts={"Pe": 8, "Co": 4, "Me": 4, "Re": 3, "Ig": 2},
        abilities={
            "Etiquette": (3, "nobles"),
            "Leadership": (2, "covenfolk"),
            "Guile": (2, "his noble guise"),
            "Ride": 2,
            "Single Weapon": 2,
            "Area Lore: Toulouse": 2,
        },
        virtues=[
            vf_art("Affinity with {art}", "perdo"),
            vf_art("Puissant {art}", "perdo"),
            "Hatred (Major)",
            "Driven (Minor)",
            "Dark Secret",
        ],
        native=OCCITAN,
    ),
    "cyprian": P(
        strong="str sta pre",
        arts={"Pe": 7, "Te": 7, "Ig": 4, "Re": 3, "Cr": 2},
        abilities={
            "Single Weapon": (4, "sword"),
            "Ride": (3, "charging"),
            "Music": (2, "troubadour songs"),
            "Magic Lore": (3, "lost Hermetic secrets"),
            "Organization Lore: Cult of Mercury": 2,
        },
        virtues=[
            vf_art("Affinity with {art}", "perdo"),
            vf_art("Affinity with {art}", "terram"),
            "Seeker",
            "Reckless (Minor)",
            "Heroic Personality",
        ],
        native=OCCITAN,
    ),
    "adam_carpentiere": P(
        strong="int dex per",
        arts={"Re": 6, "Aq": 6, "Te": 5, "Vi": 4, "Cr": 3},
        abilities={
            "Craft: Carpentry": (4, "mills and booms"),
            "Magic Theory": (4, "enchantments"),
            "Bargain": 2,
            "Area Lore: Toulouse": (2, "the waterfront"),
        },
        virtues=[
            "Hermetic Architecture",
            "Inventive Genius",
            "Avaricious (Minor)",
            "Hubris (Minor)",
        ],
        native=OCCITAN,
    ),
    "raimond": P(
        strong="int per pre",
        weak="str",
        arts={"Vi": 7, "Me": 6, "In": 4, "Cr": 3, "Re": 3},
        abilities={
            "Organization Lore: Gorgiastic Cathars": (4, "transmigration"),
            "Concentration": 2,
            "Magic Lore": (2, "Twilight"),
        },
        virtues=[
            "Ghostly Warder",
            "Quiet Magic",
            "Death Prophecy",
            "Twilight Prone",
            "Vow (Major)",
            "Driven (Minor)",
        ],
        native=OCCITAN,
    ),
    "gilbert": P(
        strong="pre com sta",
        arts={"Pe": 8, "Ig": 5, "Co": 4, "Re": 3, "Me": 3},
        abilities={
            "Etiquette": (4, "noble ladies"),
            "Music": (3, "love songs"),
            "Single Weapon": (3, "sword"),
            "Ride": 2,
            "Leadership": (3, "faidits"),
            "Organization Lore: Knights of the Green Stone": 2,
        },
        virtues=[
            "Gentle Gift",
            vf_art("Affinity with {art}", "perdo"),
            "Enemies",
            "Wrathful (Minor)",
        ],
        reputations={"Troubadour knight (local)": 3},
        native=OCCITAN,
    ),
    "rixenda": P(
        strong="int com per",
        arts={"Me": 8, "Im": 4, "In": 4, "Cr": 3, "Re": 3},
        abilities={
            "Folk Ken": (3, "dreamers"),
            "Etiquette": 2,
            "Artes Liberales": (2, "letters"),
        },
        virtues=[
            vf_art("Affinity with {art}", "mentem"),
            "Dream Magic",
            "Optimistic (Minor)",
            "Compassionate (Minor)",
        ],
        native=OCCITAN,
    ),
    "garsenda": P(
        strong="per qik pre",
        arts={"Im": 7, "He": 4, "Mu": 4, "In": 3, "Re": 3},
        abilities={
            "Faerie Lore": (3, "demesoilles"),
            "Survival": (2, "forests"),
            "Stealth": (2, "woods"),
            "Magic Lore": (2, "pagan gods"),
        },
        virtues=[
            vf_art("Affinity with {art}", "imaginem"),
            "Second Sight",
            "Seeker",
            "Dark Secret",
            "Visions",
        ],
        native=OCCITAN,
    ),
    "popilia": P(
        strong="int sta per",
        arts={"Cr": 6, "Co": 6, "He": 6, "Re": 3, "Pe": 2},
        abilities={
            "Chirurgy": (3, "childbirth"),
            "Medicine": (2, "herbs"),
            "Area Lore: Toulouse": 2,
        },
        virtues=[
            "Herbalism",
            "Hatred (Major)",
            "Close Family Ties",
        ],
        native=OCCITAN,
    ),
}


def stats(provence: Provence) -> None:
    """Generated stats for the magi of the County of Toulouse, none of whom
    the book prints a stat block for."""
    b = provence.b
    for key, profile in PROFILES.items():
        character = provence.magi[key]
        apply(b, character, profile)
        if key in APPARENT:
            character.aging.apparent_age = APPARENT[key]
