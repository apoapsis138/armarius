"""Narbonnais, the old Roman province of the Tribunal's Mediterranean
shore, as of 1220: its counties under Toulouse and Aragon, its towns
(Narbonne, Béziers, Nîmes, Montpellier, Perpignan, Rodez, Millau, Lodève,
Foix), its churches, the university of Montpellier, the Via Domitia, its
caves, springs, dolmens and vis sites; the covenants Stella Durus and Ara
Maxima Nova with their magi and libraries; and its people, from the
Trencavel heir to the Moorish corsairs, in paraphrase of Faith & Flame
chapter seven, with each covenant's votes and politics from chapter
three.

The ruined covenants of Narbonnais (Himinis' Forge, Uxellodunum and two
lost Diedne sites in the Massif Central) are tribunal.py's, set in the
region place made here. Carcassonne is the Toulousain's, as the book puts
it there. Creatures (the Old Man of the Bridge, the Jinn Corsair, the
nymphs of the Grotto, the spirit of the Aude, the werewolves of the Massif
Central) are described in the summaries of the places they haunt, since
there is no bestiary yet. Records are kept in the Provence dicts: the
region is places["narbonnais"], the covenant sites places["stella_durus"]
and places["ara_maxima_nova"], the covenants covenants["stella_durus"] and
covenants["ara_maxima_nova"], the magi under their first names
(magi["marcella"], magi["luc"], ...)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...places import PLACE
from ..builder import Builder, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character, Covenant, Neighbour, Tribunal
    from . import Provence

BONISAGUS = "house_bonisagus"
FLAMBEAU = "house_flambeau"
JERBITON = "house_jerbiton"
TYTALUS = "house_tytalus"
MERINITA = "house_merinita"
MERCERE = "house_mercere"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(provence: Provence, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = provence.b.place(name, **kw)
    provence.places[key] = place
    return place


def _found(provence: Provence, *needles: str) -> Neighbour | None:
    """A neighbour (not a place) another part has already made, whose name
    holds one of `needles`."""
    return next(
        (
            n
            for n in provence.b.saga.neighbours
            if n.kind != PLACE and any(x in n.name for x in needles)
        ),
        None,
    )


def _character(provence: Provence, *names: str) -> Character | None:
    """A character another part has made, whose name starts with one of
    `names`."""
    return next(
        (
            c
            for c in provence.b.saga.characters
            if any(c.name.startswith(x) for x in names)
        ),
        None,
    )


def _tribunal(provence: Provence) -> Tribunal:
    """The Tribunal tribunal.py makes; a bare stand-in only while that
    part is still unwritten, so this one can be built on its own."""
    if provence.tribunal is None:
        provence.tribunal = provence.b.tribunal(
            "Provençal Tribunal",
            package="provence",
            summary="",
            meets_every=7,
            next_year=1221,
            next_season="Summer",
            meeting_place="Glanum",
        )
    return provence.tribunal


def build(provence: Provence) -> None:
    b = provence.b
    tribunal = _tribunal(provence)
    _region(provence)
    _lodeve(provence, b)
    _beziers(provence, b)
    _narbonne(provence, b)
    _nimes(provence, b)
    _rodez_millau(provence, b)
    _gevaudan_montpellier(provence, b)
    _roussillon(provence, b)
    _foix(provence, b)
    _flavour(provence, b)
    _stella_durus(provence, b, tribunal)
    _ara_maxima_nova(provence, b, tribunal)


# ------------------------------------------------------------- the region


def _region(provence: Provence) -> None:
    if "narbonnais" in provence.places:
        return
    _add(
        provence,
        "narbonnais",
        "Narbonnais",
        summary=paragraphs(
            "The Mediterranean lowland the Romans called Gallia Narbonensis "
            "and later ages Septimania, between the Rhône, the Massif "
            "Central and the eastern Pyrenees. Rome's heirs have lived here "
            "for more than a thousand years: Hannibal marched through on his "
            "way to Italy, the legions set out from here to conquer Gaul, "
            "and Charlemagne's Franks stopped the Moors on this ground. It "
            "is a patchwork of vineyards, olive groves, sheep pasture, cork "
            "woods and old Roman towns, crossed by the Via Domitia.",
            "In 1220 two men decide its mundane affairs: Raimond VI, count "
            "of Toulouse, whose vassals hold Béziers, Narbonne, Nîmes and "
            "Rodez, and the boy-king James of Aragon, whose crown holds "
            "Gévaudan, Millau, Montpellier and Roussillon and whose vassal "
            "rules Foix. Simon de Montfort counted for as much until he "
            "fell in 1218, and the Albigensian Crusade has not finished "
            "remaking the land; the kings of France watch it closely.",
            "Two living covenants keep to themselves here: Stella Durus on "
            "the edge of Narbonne and Ara Maxima Nova among the vineyards "
            "outside Perpignan. The ruins of Himinis' Forge and "
            "Uxellodunum lie in the region, and two Diedne covenants once "
            "stood somewhere in the Massif Central, their names and sites "
            "now forgotten.",
            "Rodez is the heart of the troubadours' art, and singers of "
            "every rank, from counts to commoners, wander the roads; "
            "Narbonne keeps the memory of Viscountess Ermengarde's judgements "
            "of love. Jewish scholars teach at Narbonne and Montpellier, "
            "notaries draw up the contracts of the consular towns, and "
            "Moorish corsairs prey on the coast. Pilgrims cross the land on "
            "the Way of St. James, guarded by the Templars and the knights "
            "of Aubrac.",
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------------- County of Lodève


def _lodeve(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    county = _add(
        provence,
        "lodeve_county",
        "County of Lodève",
        inside=region,
        summary=(
            "A county of the Aude river country under the counts of "
            "Toulouse, given over to vines and flocks of sheep; its "
            "Corbières hills are the Pyrenees' first, lowest foothills. "
            "Its chief town, Lodève, is a favourite halt on the pilgrims' "
            "road to Compostela, and a day's ride north of it the Knights "
            "Templar keep a walled and fortified town of their own."
        ),
        **KNOWN_REGION,
    )
    w["lodeve"] = b.town(
        "Lodève",
        place=county,
        summary=(
            "A small town on the Way of St. James, busy with pilgrims, in a "
            "land of vineyards and sheep. Its cathedral is its pride."
        ),
    )
    lodeve_cathedral = b.church(
        "Cathedral of St. Genesius, Lodève",
        church="Bishop's cathedral",
        place=county,
        summary=(
            "The cathedral of Lodève, dedicated to Genesius, a clerk of "
            "Arles beheaded in 303 in Diocletian's persecution and now the "
            "patron of clerks and notaries; the keystone of the apse shows "
            "his martyrdom. Bishop Fulcran, who died in 1006 and is "
            "venerated as a saint for the purity of his life, lies "
            "incorrupt in its catacombs. Divine aura 5."
        ),
    )
    lodeve_cathedral.details["relics"] = [
        {"name": "The incorrupt body of Bishop Fulcran", "saint": "St. Fulcran"}
    ]
    w["lodeve_cathedral"] = lodeve_cathedral
    grandmont = _add(
        provence,
        "grandmont_dolmen",
        "The Great Dolmen of Grandmont",
        inside=county,
        realm="Faerie",
        aura=4,
        summary=(
            "The largest of the dolmens in the oak wood round the priory "
            "of St. Michel de Grandmont, among Roman ruins and lesser "
            "standing stones on a high hill above the Lodève country. The "
            "priory's Divine aura of 4 rules the hilltop all year, but on "
            "the night of the summer solstice a Faerie aura of 4 rises "
            "round this one stone; the aura given here is that night's."
        ),
        **KNOWN_LOCALLY,
    )
    w["grandmont_priory"] = b.church(
        "Priory of St. Michel de Grandmont",
        church="Monastery or nunnery",
        order="Grandmontine",
        place=grandmont,
        summary=(
            "A Grandmontine house, keeping the Rule of St. Stephen, a few "
            "miles outside Lodève on a tall hill wrapped in an oak forest "
            "full of dolmens and Roman remains. It gives shelter to "
            "pilgrims on the road to Compostela. Divine aura 4; on "
            "midsummer night the great dolmen in its grounds carries a "
            "Faerie aura of 4."
        ),
    )
    _add(
        provence,
        "st_thibery",
        "The Bridge of St. Thibery",
        inside=county,
        realm="Infernal",
        summary=paragraphs(
            "The Via Domitia crosses the Hérault at the town of St. "
            "Thibery on a segmented stone bridge some 450 feet long. "
            "It passes for Roman work, but its spans do not match how "
            "the Empire built, and locals wonder whether a faerie or a "
            "demon raised it.",
            "A frail old peasant haunts it, bent under a bundle of "
            "firewood, leaning on a cane and carrying a lantern. He "
            "points out to travellers a split strongbox spilling gold "
            "and silver into what looks like calm, deep, clear water "
            "below the bridge, offers to mind their goods while they "
            "dive for it, and asks only half of what they bring up.",
        ),
        secrets=paragraphs(
            "The old man is the Tempter of St. Thibery, a demon of "
            "greed (Infernal Might 15, Vim; Hierarchy 0; a tempter). "
            "He is the demon of Greed among the Six Deadly Spirits "
            "that came to Gascony with the interdict of 1208, moved "
            "here from there. The treasure is his phantasm (Trove Just "
            "Beyond Reach, CrIm 20); once the dupe leaps, he turns the "
            "river into a churning undertow (Rushing Wages of Greed, "
            "ReAq 40, Swim rolls at -6 or drown). He can also take or "
            "drop a body, change shape (often a raven), impose an "
            "Obsession of Greed, and send dreams of desperate poverty "
            "that cost a long-term Fatigue level unless the dreamer "
            "makes a Brave roll against 9. He is greedy, selfish, "
            "tricky and cowardly; he fights with his stick if he must "
            "(Attack +6, Damage +6, Defense +7, Init +4; Soak +2).",
            "Weakness: he can do nothing else until he has counted "
            "every coin thrown on the ground and put it in his purse. "
            "The purse holds 3 pawns of Vim vis.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "ancient_wine_press",
        "The Ancient Wine Press",
        inside=county,
        realm="Faerie",
        summary=paragraphs(
            "A great rectangular trough hewn from the living rock "
            "beside a vineyard near St. Thibery, older than anyone "
            "remembers. Long ago a mob came upon village girls there "
            "at the end of the vintage, took what they saw for a pagan "
            "rite, and stoned them all, deaf to their pleas.",
            "Vis (unclaimed): if the first harvest's grapes are trodden "
            "here barefoot, the pomace (the seeds, skins and stalks "
            "left from the must) holds 4 pawns of Herbam. Treading the "
            "last harvest the same way yields 6 pawns, but of vis "
            "Infesta.",
        ),
        secrets="The girls had been pressing the last grapes when fauns "
        "seduced them, and the crowd caught them just after; the taint "
        "on the last harvest's vis is that killing.",
        **RUMOURED,
    )


# ------------------------------------------------------------- Béziers


def _beziers(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    county = _add(
        provence,
        "beziers_county",
        "County of Béziers",
        inside=region,
        summary=(
            "Temperate, wooded, rolling country that the house of "
            "Carcassonne, the Trencavel, has held since 1034. From 1194 "
            "Raimond-Rogier Trencavel ruled it with Carcassonne, Albi and "
            "the Razès, owing homage both to Peter II of Aragon and to "
            "Raimond VI of Toulouse, until the crusaders took him and he "
            "died their prisoner in 1209. The crusaders still hold his "
            "lands."
        ),
        **KNOWN_REGION,
    )
    trencavel = _found(provence, "Trencavel")
    if trencavel is None:
        trencavel = b.lord(
            "The Trencavel",
            title="count",
            wealth="Poor",
            manors=0,
            seat="Carcassonne (lost)",
            ruler="Raimond II Trencavel, aged 17",
            place=county,
            summary=paragraphs(
                "The viscounts of Béziers and Carcassonne, lords also "
                "of Albi and the Razès, and overlords of Béziers since "
                "1034. Raimond-Rogier Trencavel tried to join the "
                "crusade in 1209 and was turned away by the legate; he "
                "took Béziers' Jews to safety and fell back on "
                "Carcassonne, where he was seized while parleying "
                "under a promise of safe conduct and died in his own "
                "dungeon, of dysentery or of poison. He leaned heavily "
                "on the Jews of Béziers to run his affairs.",
                "His son, Raimond II, was stripped of everything by "
                "Simon de Montfort and is now seventeen and pressing "
                "his claim; many local clergy put out of their posts "
                "by northern churchmen have taken his side, and the "
                "southern lords and faidits look to him.",
            ),
            secrets="Rumours of a lady's betrayal hang over Raimond-Rogier's "
            "capture; see Lastours in the Toulousain.",
        )
    w["trencavel"] = trencavel
    massacre = _add(
        provence,
        "beziers",
        "The Massacre Ground of Béziers",
        inside=county,
        realm="Infernal",
        aura=7,
        summary=(
            "The burnt city of Béziers, where the crusaders slaughtered "
            "the people in 1209, even those who fled into the churches. "
            "The whole city lies under an Infernal aura of 7, which climbs "
            "to 8 each 22nd of July, the day of the killing, "
            "and fades to nothing through Advent and Lent. It was from "
            "the steps of the Madeleine that the legate Arnaud Amaury is "
            "said to have told the knights to kill everyone and leave God "
            "to sort out his own."
        ),
        **KNOWN_TRIBUNAL,
    )
    w["beziers"] = b.town(
        "Béziers",
        place=massacre,
        answers_to=trencavel,
        ruler="The crusaders, against the Trencavel claim",
        summary=(
            "A colony Augustus founded for retired legionaries, ringed on "
            "three sides by the Orb, whose walls were built from the stone "
            "of its own amphitheatre. It sells white wine. As a Cathar "
            "stronghold it was all but burnt to the ground by the "
            "crusade; rebuilding began in 1215 and has far to go, and the "
            "new cathedral rises on the footings of the old one of 1130. "
            "Hardly anything else stands: the tall limestone church of the "
            "Madeleine, once the viscount's chapel, and the church of St. "
            "Aphrodise, the city's first evangelist, built over a "
            "third-century burial ground."
        ),
    )
    w["beziers_churches"] = b.church(
        "Church of the Madeleine, Béziers",
        church="Large urban church",
        place=massacre,
        summary=(
            "A tall limestone church, formerly the viscount's chapel, one "
            "of the few buildings of Béziers left standing; the massacre's "
            "Infernal aura smothers it. The church of St. Aphrodise, over "
            "a third-century necropolis, also survives."
        ),
    )


# ----------------------------------------------------- Duchy of Narbonne


def _narbonne(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    duchy_land = _add(
        provence,
        "narbonne_duchy",
        "Narbonne and the Lower Aude",
        inside=region,
        summary=(
            "The country round Narbonne and the lower Aude, with the port "
            "and fisheries of the city and the old abbey lands of Lagrasse "
            "two days to the west. The ducal title, once the counts of "
            "Toulouse's, was taken from Raimond VI in the crusade."
        ),
        **KNOWN_REGION,
    )
    w["duchy_of_narbonne"] = b.lord(
        "Duchy of Narbonne",
        title="duke",
        wealth="Wealthy",
        seat="Narbonne",
        ruler="Arnaud Amaury, archbishop of Narbonne and papal legate",
        place=duchy_land,
        summary=(
            "The ducal title over the region, once held by the counts of "
            "Toulouse as their right. Raimond VI lost it in the crusade, "
            "and since Simon de Montfort's death in 1218 it has belonged "
            "to Arnaud Amaury, archbishop of Narbonne, papal legate and "
            "the abbot who led the crusade at Béziers. It is quite "
            "separate from the viscounty, which rules the city itself."
        ),
    )
    w["viscounty_of_narbonne"] = b.lord(
        "Viscounty of Narbonne",
        title="count",
        seat="Narbonne",
        ruler="The viscount of Narbonne",
        place=duchy_land,
        summary=(
            "The secular lordship of the city of Narbonne, distinct from "
            "the duchy. The viscounts and the archbishops fought over the "
            "city for decades of the last century; now the viscount holds "
            "its eastern half and the commune, the bourg. Viscountess "
            "Ermengarde, who ruled from 1132 to 1194, is the most famous of "
            "the line; in 1115 Viscount Aimery II gave the village of Le "
            "Lac to Lagrasse to settle a quarrel with the archbishop."
        ),
    )
    w["narbonne"] = b.town(
        "Narbonne",
        charter="Commune",
        ruler="The viscount (east and bourg) and the archbishop (west)",
        answers_to=w["viscounty_of_narbonne"],
        place=duchy_land,
        summary=paragraphs(
            "A tolerant old city that has been capital of Visigothic "
            "Septimania and a possession of the Emirate of Cordoba, where "
            "the Via Domitia meets the Via Aquitania. It has a busy port "
            "and fishing fleet on the Aude, is a centre of troubadour "
            "song, and its well-known Jewish scholars keep several "
            "schools. The Via Domitia enters it over a bridge of seven "
            "arches.",
            "The archbishop rules its western half and the viscount the "
            "east and the bourg. Their long feud has let many churches "
            "decay, the cathedral of St. Just and St. Pasteur among them, "
            "so the city's Divine aura is only 2, rising to 3 on its "
            "patron saints' feasts; the basilica of St. Paul-Serge keeps "
            "an aura of 5 always.",
            "Stella Durus stands on the left bank of the Aude just outside the city.",
        ),
    )
    w["archbishop_of_narbonne"] = b.church(
        "Cathedral of St. Just and St. Pasteur, Narbonne",
        church="Archbishop's cathedral",
        ruler="Arnaud Amaury, archbishop of Narbonne",
        place=duchy_land,
        summary=(
            "The archbishop's cathedral, neglected into ruin through the "
            "long quarrel between archbishops and viscounts over the city. "
            "Its archbishop, Arnaud Amaury, is also papal legate and, since "
            "1218, duke of Narbonne, holding the city's western half."
        ),
    )
    w["st_paul_serge"] = b.church(
        "Basilica of St. Paul-Serge, Narbonne",
        church="Large urban church",
        answers_to=w["archbishop_of_narbonne"],
        place=duchy_land,
        summary=(
            "A basilica raised over a fourth-century cemetery that "
            "Constantine founded. Unlike the city's neglected churches, it "
            "keeps an unfailing Divine aura of 5."
        ),
    )
    w["lagrasse"] = b.church(
        "Abbey of St. Mary of Lagrasse",
        church="Monastery or nunnery",
        order="Benedictine",
        place=duchy_land,
        founded=779,
        summary=(
            "A Benedictine abbey some two days' ride west of Narbonne. "
            "Nimphridius, abbot of Narbonne, gathered its monks in the "
            "seventh century; it became an abbey in 779 and grew rich on "
            "Charlemagne's patronage and the gifts of local lords, piling "
            "up lands, castles and priories. In the last century it ruled "
            "wide lands spread over the Béziers and Toulouse dioceses "
            "and Urgell county. It still carries weight in the "
            "region, but the crusade has cost it dearly."
        ),
    )
    w["courts_of_love"] = b.faction(
        "Ermengarde's Courts of Love",
        faction="Other",
        decides="Its leader",
        ruler="Once Viscountess Ermengarde of Narbonne",
        place=duchy_land,
        rules="Courtly love judged by a lady's verdict, after the fashion of André le Chapelain's treatise",
        wants="Troubadour song and courtly manners kept alive in Narbonne",
        summary=(
            "A mundane custom, not a Hermetic one. Viscountess Ermengarde, "
            "who ruled Narbonne from 1132 to 1194, gave five of the "
            "judgements of love that André le Chapelain records in his "
            "treatise on courtly love, De Arte Honeste Amandi. She wrote "
            "to and encouraged many troubadours, and the tradition of "
            "song and courtly debate she fostered in Narbonne has outlived "
            "her and survived the crusade. Jean Marie of Stella Durus is "
            "drawn to it and dreams of a league of troubadour-loving magi."
        ),
    )


# ------------------------------------------------------- County of Nîmes


def _nimes(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    county = _add(
        provence,
        "nimes_county",
        "County of Nîmes",
        inside=region,
        summary=(
            "The eastern march of the counts of Toulouse, theirs by "
            "inheritance since the ninth century: rolling hills, streams "
            "and woods under a mild Mediterranean sky, rich in cork, grapes "
            "and olives. In the hills between Millau and Nîmes lie the "
            "Bramabiau gorge and the Grotto of Faeries."
        ),
        **KNOWN_REGION,
    )
    toulouse = _found(provence, "Raimond VI", "County of Toulouse", "Count of Toulouse")
    w["viscount_of_nimes"] = b.lord(
        "Viscount of Nîmes",
        title="count",
        wealth="Wealthy",
        seat="Nîmes",
        ruler="The viscount of Nîmes, for Raimond VI of Toulouse",
        answers_to=toulouse,
        place=county,
        summary=(
            "A hereditary holding of the counts of Toulouse, the eastern "
            "edge of their lands. The viscount who governs Nîmes for the "
            "count keeps an order of knights, the Knights of the Arena, in "
            "the old amphitheatre."
        ),
    )
    arena = _add(
        provence,
        "arena_of_nimes",
        "The Arena of Nîmes",
        inside=county,
        realm="Divine",
        aura=3,
        summary="The Roman amphitheatre of Nîmes, big enough for sixteen "
        "thousand, now the seat of the city's government and its "
        "refuge in danger; the viscount's knights and the bishop's "
        "palace live in apartments built into it. Divine aura 3.",
        secrets="Legend says tunnels under the arena run all the way to the "
        "amphitheatre of Arles, which has also been made a fortress.",
        **KNOWN_REGION,
    )
    w["nimes"] = b.town(
        "Nîmes",
        charter="Commune",
        council=4,
        ruler="Four consuls, under the viscount",
        answers_to=w["viscount_of_nimes"],
        place=county,
        summary=paragraphs(
            "A cloth-making city that some say Nemausios, son of Heracles, "
            "founded beside a healing spring. Its government sits in the "
            "Roman arena. The Tour Magne, an eight-sided tower three "
            "storeys and nearly twenty paces high, crowns its highest "
            "point and takes in the last of the Roman walls; the Maison "
            "Carrée, a perfect Roman temple, houses the four consuls who "
            "speak for the city.",
            "Notaries hold office for the county of Nîmes.",
        ),
    )
    w["bishop_of_nimes"] = b.church(
        "Bishop of Nîmes",
        church="Bishop's cathedral",
        place=arena,
        summary=(
            "The bishop's palace stands inside the converted arena, and "
            "the see's presence has steadily weakened the old spirit of "
            "the Nemausian Spring nearby."
        ),
    )
    w["knights_of_the_arena"] = b.faction(
        "The Knights of the Arena",
        faction="Other",
        decides="Its leader",
        ruler="The viscount of Nîmes",
        place=arena,
        summary=(
            "An order of knights in the service of the viscount of Nîmes, "
            "quartered in the apartments of the Roman amphitheatre with "
            "the bishop's household."
        ),
    )
    _add(
        provence,
        "maison_carree",
        "The Maison Carrée",
        inside=county,
        realm="Faerie",
        aura=1,
        summary=(
            "A Roman temple in the heart of Nîmes, raised on a podium with "
            "six columns bearing a portico at each end. It was Apollo's, "
            "and judges met there; now the four consuls keep their offices "
            "in it. A faint Faerie aura of 1 clings to a hollow of the "
            "building, rising to 3 on the 9th of February, the old date of "
            "Apollo's festival."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "bramabiau",
        "The Bramabiau Gorge",
        inside=county,
        aura=3,
        summary=(
            "In the hills between Millau and Nîmes the river Bonheur "
            "plunges into a cave in a cliff, runs underground through a "
            "gorge with six waterfalls, and bursts out of a second cave as "
            "the Bramabiau, the Roaring Ox in Occitan, to run down a box "
            "canyon toward the sea. From the lower cave the passages can "
            "be explored. In a side tunnel just past one waterfall are "
            "ancient fetishes and wall paintings that a magus might study "
            "for Insight into the cultic Fertility Magic of Ancient Magic. "
            "The aura in that passage is Magic 3, rising to 4 under a full "
            "moon."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "grotto_of_faeries",
        "The Grotto of Faeries",
        inside=county,
        realm="Faerie",
        aura=3,
        summary=(
            "A deep cavern south of the Bramabiau, still in the hills "
            "between Millau and Nîmes, with an underground river running "
            "through its back. Its great galleries, which the locals call "
            "cathedrals, drop nearly two hundred paces into the rock and "
            "take a hard climb to reach the floor. A band of lesser nymphs "
            "(Realms of Power: Faerie) dances and sings there to the "
            "river's genius loci, and their voices are the rushing-water "
            "sound people hear at the cave mouth. The caves carry Faerie "
            "aura 3 throughout."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "nemausian_spring",
        "The Nemausian Spring",
        inside=county,
        summary=(
            "A spring near Nîmes. Some say the Gauls made it a shrine to "
            "Heracles' son before Caesar came; others that it is the old "
            "altar of Volcae, a magic spirit the native tribes worshipped "
            "until Rome arrived. A spirit still dwells here, much weakened "
            "by the spreading Dominion and the bishop's seat in the arena "
            "close by. Vis (unclaimed): every summer solstice it wells up "
            "in tiny, very clear pools of steaming water holding 3 pawns "
            "of Creo or Aquam."
        ),
        **KNOWN_LOCALLY,
    )


# ----------------------------------------------- Rodez, Millau and the Larzac


def _rodez_millau(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    rodez_land = _add(
        provence,
        "rodez_county",
        "County of Rodez",
        inside=region,
        summary=(
            "Carved out of the old county of Rouergue, first an appanage "
            "of Toulouse until the viscount's ancestor seized it in 1112. "
            "It is the heart of the troubadours' country. The Templars "
            "have held five places here since the mid-twelfth century, "
            "sold to them to pay for the count of Toulouse's part in the "
            "First Crusade."
        ),
        **KNOWN_REGION,
    )
    toulouse = _found(provence, "Raimond VI", "County of Toulouse", "Count of Toulouse")
    w["count_of_rodez"] = b.lord(
        "Henry I, count of Rodez",
        title="count",
        seat="Rodez",
        ruler="Henry I of the House of Millau",
        answers_to=toulouse,
        place=rodez_land,
        summary=paragraphs(
            "Head of the House of Millau, which has ruled Rodez without a "
            "break since 1112, and a troubadour himself, as was his father "
            "Hugh II, patron of the abbey of Bonnecombe; he came to the "
            "title after his half-brothers Hugh and William, neither long-lived. "
            "He is raising his children to love song as he does.",
            "Henry means to take the cross and go on crusade, leaving his "
            "eight-year-old son Hugh in the care of the boy's mother, "
            "Algayette, heiress of Guy, lord of Scorailles.",
        ),
    )
    w["rodez"] = b.town(
        "Rodez",
        ruler="The count and the bishop, each behind his own wall",
        answers_to=w["count_of_rodez"],
        place=rodez_land,
        summary=(
            "A farming and market town where the Aveyron meets the "
            "Auterne on the Ségala plateau, split into quarters by great "
            "double walls because its bishops and counts have long "
            "quarrelled over it. The red sandstone west wall of the "
            "cathedral, built in 1000 with two towers, is part of the "
            "town's defences. The bishop's palace has a tall tower."
        ),
    )
    w["rodez_cathedral"] = b.church(
        "Cathedral of Rodez",
        church="Bishop's cathedral",
        place=rodez_land,
        summary=(
            "A red sandstone cathedral whose west front, with its two "
            "towers, doubles as part of the town wall. The bishops are "
            "often at odds with the counts. Divine aura 5."
        ),
    )
    w["st_amand_rodez"] = b.church(
        "Church of St. Amand, Rodez",
        church="Parish church",
        place=rodez_land,
        summary=(
            "A church whose choir is hung with sixth-century tapestries of "
            "the miracles of St. Amand, the patron of brewers. Divine aura 4."
        ),
    )
    w["templars_larzac"] = b.church(
        "Templar Commanderies of the Larzac",
        church="Monastery or nunnery",
        order="Knights Templar",
        place=rodez_land,
        summary="The Templars' houses in the county of Rodez: the "
        "commanderies of Viala du Pas de Jaux and Sainte-Eulalie de "
        "Cernon and the walled villages of Saint-Jean d'Alcas, La "
        "Couvertoirade and La Cavalerie, all supporting the order's work here "
        "since the middle of the last century. Guillaume de Saunhac "
        "tutors the commander of Sainte-Eulalie.",
        secrets="Guillaume de Saunhac will be Master of the Temple in 1245.",
    )
    w["order_of_aubrac"] = b.church(
        "The Order of Aubrac",
        church="Monastery or nunnery",
        order="Augustinian (knights of Aubrac)",
        place=rodez_land,
        summary=(
            "A small order of knights who guard pilgrims on the Way of St. "
            "James, south-west to Compostela and south-east to Rome. It "
            "was founded at the Dômerie d'Aubrac in the eleventh century "
            "and took the Rule of St. Augustine in 1162, and it keeps "
            "hospitals it calls commanderies at Bozouls, Millau, Nazac and "
            "Rodez. It competes with the Hospitallers, who would like to "
            "swallow it but have so far failed."
        ),
    )
    w["troubadours_of_rodez"] = b.faction(
        "The Troubadours of Rodez",
        faction="Other",
        decides="A vote of all",
        place=rodez_land,
        wants="Patrons, audiences and peace to sing in",
        summary=(
            "Rodez is the local centre of the troubadour movement, under "
            "counts who sing themselves. The first troubadours were "
            "nobles, but now they come from all ranks of society. Fulk of "
            "Toulouse started as one before he repented, took orders and "
            "became bishop of Toulouse in 1205 and a force in the crusade. "
            "Renaud and Jean Marie of Stella Durus want to keep a "
            "troubadour at their covenant."
        ),
    )
    millau_land = _add(
        provence,
        "millau_county",
        "County of Millau",
        inside=region,
        summary=paragraphs(
            "A county that came to the crown of Aragon in the early "
            "twelfth century by the same marriage that brought it "
            "Gévaudan. It made pottery for the Roman Empire and still "
            "does; its craftsmen are famed for fine leather and for the "
            "Roquefort cheese they ripen in caves in the hills.",
            "Huge ancient dolmens and menhirs are strewn across the land. "
            "The locals leave them alone, taking them for faerie homes and "
            "meeting places; they carry Faerie auras of 2 to 4, and the "
            "stronger the aura, the mightier the creature that lairs "
            "there.",
        ),
        **KNOWN_REGION,
    )
    _add(
        provence,
        "millau_dolmens",
        "The Dolmens and Menhirs of Millau",
        inside=millau_land,
        realm="Faerie",
        aura=3,
        summary=(
            "Countless stone tables and standing stones across the "
            "Millau country, relics of its pagan past, shunned as the "
            "homes and gathering grounds of faeries. Each site has a "
            "Faerie aura of 2 to 4 (3 given here as typical), with "
            "stronger faeries at the stronger sites."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        provence,
        "millau_ruins",
        "The Roman Ruins across the Tarn",
        inside=millau_land,
        aura=3,
        summary=(
            "The remains of Roman Millau's potteries and town, mostly on "
            "the far bank of the Tarn from the living town and largely "
            "forgotten, though they hold a Magic aura of 3."
        ),
        **KNOWN_LOCALLY,
    )
    aragon = _found(provence, "King of Aragon", "Kingdom of Aragon", "James I")
    w["millau"] = b.town(
        "Millau",
        charter="Commune",
        ruler="Its consuls, under the crown of Aragon",
        answers_to=aragon,
        place=millau_land,
        summary=(
            "A trading town where the Tarn and the Dourbie meet, crossed "
            "by a Roman bridge of seventeen spans over the Tarn, one of "
            "the largest in Mythic Europe, which puts it on an important "
            "trade route. Alphonso II of Aragon granted it a consular "
            "charter, so its consuls may tax and keep the law."
        ),
    )
    espinasse = b.church(
        "Notre-Dame-de-l'Espinasse, Millau",
        church="Parish church",
        place=millau_land,
        summary=(
            "Millau's church, said to keep a piece of the Crown of Thorns: "
            "part of a rush with three pairs of thorns, broken from the "
            "great crown in Constantinople, in a small cage of gold mesh "
            "on a fine gold chain. The priest seldom takes it out for fear "
            "of harming it; it is carried before the people at Lent. It is "
            "an ordinary relic of Faith 3 with the saintly power to Cure "
            "Blindness. Divine aura 4."
        ),
    )
    espinasse.details["relics"] = [
        {"name": "Fragment of the Crown of Thorns", "saint": "Christ", "faith": 3}
    ]
    w["espinasse"] = espinasse


# ------------------------------------------------- Gévaudan and Montpellier


def _gevaudan_montpellier(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    aragon = _found(provence, "King of Aragon", "Kingdom of Aragon", "James I")
    gevaudan = _add(
        provence,
        "gevaudan",
        "County of Gévaudan",
        inside=region,
        summary=(
            "A county of the crown of Aragon since 1112, once part of the "
            "diocese of Mende. Its north takes in some of the roughest "
            "country of the Massif Central: thinly peopled and notorious "
            "for fierce, clever wolves."
        ),
        **KNOWN_REGION,
    )
    w["barons_of_gevaudan"] = b.lord(
        "The Barons of Gévaudan",
        title="baron",
        manors=8,
        ruler="Eight barons, sworn to James of Aragon",
        answers_to=aragon,
        place=gevaudan,
        summary=(
            "Eight barons who hold Gévaudan for the crown of Aragon and "
            "have fought off the bishop of Mende's rule, though Louis VII's "
            "Golden Bull of Gévaudan gave the bishop temporal power there. "
            "The bishops tried again and again in the last century to take "
            "the county back."
        ),
    )
    w["bishop_of_mende"] = b.church(
        "Bishop of Mende",
        church="Bishop's cathedral",
        place=gevaudan,
        summary=(
            "The bishop whose diocese once took in Gévaudan and who holds "
            "Louis VII's Golden Bull granting him temporal power there; "
            "the barons sworn to Aragon refuse him."
        ),
    )
    _add(
        provence,
        "wolves_cave",
        "The Wolves' Cave Shrine",
        inside=gevaudan,
        aura=3,
        summary="An ancient Gaulish cave shrine somewhere in the wilds of the "
        "Massif Central, with a Magic aura of 3, in country so empty a "
        "covenant could grow there far from the crusade, though "
        "specialists and rare supplies would be hard to get.",
        secrets="The wolves that hunt travellers in these hills are not "
        "ordinary wolves: they are a little tribe of shape-changing "
        "werewolves, and "
        "this cave is their lair. Could they be tamed, and the shrine "
        "become a covenant?",
        **RUMOURED,
    )
    montpellier_land = _add(
        provence,
        "montpellier_lordship",
        "Lordship of Montpellier",
        inside=region,
        summary=(
            "The city of Montpellier and its lands, which passed to the "
            "crown of Aragon when Marie of Montpellier, its hereditary "
            "ruler, married Peter II in 1204; James was born there in 1208."
        ),
        **KNOWN_REGION,
    )
    w["montpellier"] = b.town(
        "Montpellier",
        charter="Commune",
        council=12,
        ruler="Twelve consuls chosen every year, under the crown of Aragon",
        answers_to=aragon,
        place=montpellier_land,
        summary=paragraphs(
            "A spice-trading city the counts of Toulouse founded in 985, "
            "when pirate raids drove the coast-dwellers inland, and famous "
            "for tolerating Cathars, Jews and Muslims. It sits on two "
            "hills, Montpellier and Montpellieret, joined by steep streets, "
            "inside a wall with the Tour de la Babote and under a castle.",
            "When Marie of Montpellier wed Peter II of Aragon in 1204 the "
            "match secured her right to rule and won the city a charter "
            "under which it picks twelve consuls each year. Notaries hold "
            "office for the city. The trobairitz Gormonda de Monpeslier, "
            "a fierce enemy of the Cathars, is its daughter.",
        ),
    )
    w["university_of_montpellier"] = b.university(
        "University of Montpellier",
        school="University",
        place=montpellier_land,
        summary=(
            "The school William VII of Montpellier founded, recognised as "
            "a university this very year, 1220, and famous for medicine "
            "(see Art & Academe). Ara Maxima Nova's magi have searched its "
            "books for the way to the Hesperides."
        ),
    )
    w["jewish_scholars"] = b.faction(
        "The Wise of Provence",
        faction="Other",
        decides="A council",
        place=montpellier_land,
        summary=paragraphs(
            "The yeshivas of Arles, Montpellier and Narbonne (Realms of "
            "Power: The Divine), where Jewish scholars interpret and "
            "set down Talmudic thought. Famous rabbis and kabbalists "
            "have studied at Narbonne: Moses ha-Darshan in the "
            "eleventh century, and in the twelfth Moses ben Joseph ben "
            "Merwan ha-Levi, thought by many the greatest Jewish "
            "mystic of his day. Called Hachmei Provence, they set the "
            "literary style and pedigree that remain the standard of "
            "Jewish scholarship.",
        ),
        secrets="Story: a divinely blessed golem, servant of a kabbalist, "
        "breaks loose when a mob hangs its maker's grandson for "
        "something he never did, a lynching perhaps stirred up by a demon, "
        "a tainted jinn or a mischievous faerie. It beats its way "
        "through the town and will not stop until it finds the true "
        "culprit.",
    )


# --------------------------------------------------- County of Roussillon


def _roussillon(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    aragon = _found(provence, "King of Aragon", "Kingdom of Aragon", "James I")
    county = _add(
        provence,
        "roussillon",
        "County of Roussillon",
        inside=region,
        summary=paragraphs(
            "Named for Ruscino, a little stronghold where Gaulish chiefs "
            "met to weigh Hannibal's request for a parley. It is farming "
            "country known for vineyards and for woad, which is worked "
            "into a pale blue dye for cloth. The viscount owns some minor "
            "iron workings in the Pyrenean foothills and a gold mine of "
            "little yield near Saint-Jean-Pla-de-Corts.",
            "As the border with Catalonia it bristles with fortifications: "
            "Castle Rodes stands on a high granite spur commanding the "
            "head of the Têt valley, and the southern port of Collioure, "
            "where the Templars built a castle above the bay in 1207, is "
            "a starting point for many crusaders. The Via Domitia comes "
            "down from the pass near Le Perthus through Perpignan.",
        ),
        **KNOWN_REGION,
    )
    w["sancho_of_roussillon"] = b.lord(
        "Sancho, count of Roussillon",
        title="count",
        wealth="Wealthy",
        seat="Perpignan (the Château de Roussillon)",
        ruler="Sancho, with his son Nuno Sanche",
        answers_to=aragon,
        place=county,
        summary="Viscount Gerard II died heirless in 1172, and "
        "Roussillon passed to Alphonso II of Aragon by an agreement "
        "made beforehand with Gerard and his nobles, and Alphonso gave "
        "it to his brother Sancho. Sancho, count of Roussillon and "
        "Cerdagne, and his son Nuno Sanche, who holds Roussillon, "
        "Conflent, Vallespir and Cerdagne, are regents of Aragon for "
        "young James, who lives at Zaragoza.",
        secrets="Sancho, backed by Nuno, now and then plots against the king "
        "he serves as regent.",
    )
    w["perpignan"] = b.town(
        "Perpignan",
        charter="Commune",
        ruler="Its commune, under the viscount",
        answers_to=w["sancho_of_roussillon"],
        place=county,
        summary=paragraphs(
            "Roussillon's capital on the Têt, its largest river, founded in "
            "the ninth century and a partly self-governing commune since "
            "1197. It lives on wool, wine, cork, iron, leather and olive "
            "oil, behind high, thick walls. The viscount's compound holds "
            "a chapel, a hospital and the Château de Roussillon, whose "
            "round tower twenty paces high dominates it.",
            "Ara Maxima Nova's vineyards and cork nurseries lie among the "
            "farming estates on its outskirts, and its magi slip into town "
            "for sweets and chess. In one of its taverns Ducaru of Stella "
            "Durus and Etienne of Ara Maxima Nova have been playing a game "
            "of chess for months, and Redcaps drop in to follow it and bet "
            "on the winner.",
        ),
    )
    w["st_john_perpignan"] = b.church(
        "Hospital of St. John the Baptist, Perpignan",
        church="Chapel",
        place=county,
        summary=(
            "The chapel and hospital in the viscount's compound, both "
            "under the patronage of the Baptist; the hospital cares for "
            "Perpignan's urban poor."
        ),
    )
    w["poor_clares_perpignan"] = b.church(
        "The Poor Clares of Perpignan",
        church="Monastery or nunnery",
        order="Poor Clares",
        place=county,
        summary=(
            "The Order of Poor Sisters, living by Franciscan ideals, at "
            "work in the city and trying to found a convent there."
        ),
    )
    _add(
        provence,
        "abandoned_mine",
        "The Abandoned Mine",
        inside=county,
        summary=paragraphs(
            "A small worked-out mine, which the book leaves for the "
            "storyguide to place (the iron workings in the Pyrenean "
            "foothills or the poor gold mine at Saint-Jean-Pla-de-Corts "
            "would serve). Covenfolk quarrying stone or picking over its "
            "tailings strike a new vein of gold or iron, perhaps with a "
            "visible pawn of vis.",
            "Vis (unclaimed): every hundredth cartload of ore dug out by "
            "hand holds 2 pawns of Terram; ore taken out by magic holds "
            "none. Nobody knows how deep the vein goes, or whether the vis "
            "comes from the ore or from the labour of mining. The work "
            "could be dangerous for covenfolk new to it, the vis may end "
            "with the vein, and new digging may draw the local lord's eye.",
        ),
        **RUMOURED,
    )


# ------------------------------------------------------- County of Foix


def _foix(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    found = _found(provence, "Foix")
    if found is not None:
        w["foix"] = found
        return
    aragon = _found(provence, "King of Aragon", "Kingdom of Aragon", "James I")
    w["foix"] = b.lord(
        "Raymond Roger I, count of Foix",
        title="count",
        seat="Château de Foix",
        ruler="Raymond Roger I, fifth count of Foix",
        answers_to=aragon,
        place=region,
        summary=paragraphs(
            "The counts of Foix served Toulouse in the eleventh and twelfth "
            "centuries. Raymond Roger I, the fifth count, a troubadour and "
            "kinsman of Raimond VI, was held for a time in 1203 by the "
            "bishop of Urgell until Peter II of Aragon freed him, and he "
            "swore fealty to Peter. He is famous for generalship, "
            "chivalry, loyalty and fine clothes, and writes verse as well "
            "as paying for it. Not a Cathar himself, he married one and "
            "fought Simon de Montfort.",
            "Foix belongs to the Pyrenean marches but its count is busy "
            "across the Toulousain and Narbonnais. Charlemagne founded the "
            "town; the Château de Foix, on a seventh-century stronghold, "
            "looms over it with a great round tower, held out against "
            "several crusader assaults, sheltered hunted Cathars, and is "
            "said to stand on rock riddled with caves.",
        ),
    )
    w["st_volusien"] = b.church(
        "Abbey of St. Volusien, Foix",
        church="Monastery or nunnery",
        order="Canons Regular of St. Augustine",
        founded=1104,
        place=region,
        summary=(
            "A large red sandstone house of Augustinian canons founded in "
            "1104, with a three-naved church keeping the bones of St. "
            "Volusien, patron of Foix, whom the Visigoths carried off and "
            "tortured to death. It is the spiritual and social centre of "
            "the town. Divine aura 4."
        ),
    )


# ----------------------------------------------------------- local flavour


def _flavour(provence: Provence, b: Builder) -> None:
    region = provence.places["narbonnais"]
    w = provence.world
    coast = _add(
        provence,
        "gulf_of_lion",
        "The Gulf of Lion",
        inside=region,
        summary=paragraphs(
            "The Narbonnais shore, from Collioure past the mouths of "
            "the Aude and the Hérault toward the Rhône. Since the "
            "Umayyads took Iberia in the eighth century, Moorish "
            "corsairs have hunted these waters, and no crossing from "
            "the Catalan Sea to the Ligurian or Sardinian seas is safe "
            "from capture and slavery, so ships sail together in "
            "flotillas. Passing it takes a Moorish ship, magic, or a "
            "story (City & Guild).",
            "A brutal corsair raids this coast, landing reavers to "
            "fall on caravans and pilgrims and taking captives for "
            "ransom. He has struck a bargain with a jinn called "
            "Howling Knife of the Dunes.",
        ),
        secrets=paragraphs(
            "The Jinn Corsair (Faerie Might 20, Vim) looks like a "
            "handsome, grinning Maghrebi pirate with a brand on his "
            "left cheek, dressed in rich cloth, bearing a fine "
            "scimitar that looks like glass in the morning light. He "
            "is Muslim, proud and overconfident, and sells his "
            "service as a bodyguard; he has lost a charge only twice, "
            "once to a dragon and once to a Hermetic magus, perhaps "
            "of the players' own covenant. Powers: become a gritty "
            "desert whirlwind that can carry one person (Sirocco's "
            "Form, CrAu 50); find whoever an Arcane Connection he "
            "holds belongs to (InCo 20); sheathe his blade in white "
            "fire for +10 damage (CrIg 20); make one he touches "
            "invisible, though a shadow remains (PeIm 15). Scimitar: "
            "Attack +12, Damage +8, Defense +9, Init +3; Soak +6. He "
            "is bound by his name and serves whoever he has agreed "
            "to; failing a mission drives him to fury. His scimitar, "
            "weightless, holds one pawn apiece of Ignem, Auram, Imaginem "
            "and Corpus, and its bearer gains Puissant Single Weapon.",
            "The jinn knows of the Order and has promised the pirates "
            "untold wealth if they bring him one particular magus; he "
            "has a second master, someone the players have angered.",
        ),
        **KNOWN_REGION,
    )
    w["moorish_raiders"] = b.faction(
        "The Moorish Raiders",
        faction="Other",
        decides="Its leader",
        place=coast,
        wants="Plunder, captives to ransom or sell",
        summary=(
            "Corsairs based in the Maghreb, at Algiers, Marrakech, Tangier "
            "and the like, and in the nearby Balearics, who plunder "
            "Christian Iberia, Italy, Sicily and southern France, "
            "Narbonnais above all. The Balearic Crusade of 1115 stopped "
            "them for a year at most. The Italian cities, the Normans of "
            "Sicily, Aragon and Castile have tightened their hold on the "
            "western Mediterranean without ending the raids. Ara Maxima "
            "Nova buys some slaves from Arab merchants."
        ),
    )
    w["notaries"] = b.faction(
        "The Notaries of Narbonnais",
        faction="Gild",
        decides="A vote of all",
        place=region,
        rules="Lay office only: a notary who takes the tonsure leaves the notariate",
        offers="Drawn contracts, witnessed charters, verified documents, a seal",
        summary=(
            "A profession grown from the remnants of Roman law. Notaries "
            "arose in Narbonnais in the 1140s, writing up charters "
            "and contracts alongside the consular governments of the "
            "communes. At first they named themselves; now secular and "
            "Church lords appoint them, making notary a public office "
            "whose authenticated documents stand in court. They are paid "
            "at Christmas by their employers, may not be clergy, answer to "
            "secular law, and hold office only for a given realm or town, "
            "such as the county of Nîmes or Montpellier. Their patron is "
            "St. Genesius of Lodève."
        ),
    )
    _add(
        provence,
        "via_domitia",
        "The Via Domitia",
        inside=region,
        summary=paragraphs(
            "The ancient road the Romans paved: from the Pyrenean pass "
            "near Le Perthus through Perpignan, over a bridge of seven "
            "arches into Narbonne, on through Béziers, Montpellier and "
            "Nîmes into the Kingdom of Arelat, north at Céreste into "
            "the Piedmont, and over the Alps by the Col de Montgenèvre, "
            "the lowest main pass between France and Italy. Locals "
            "believe Heracles walked it on his labours, and Hannibal "
            "certainly marched it toward Rome. In Roman times "
            "mansiones, staging posts a day's journey apart, gave "
            "travellers rest and food.",
            "Ara Maxima Nova guards the road jealously and uses it in "
            "its initiations and rites; its magi often challenge to "
            "certamen any magus they think is studying the road's "
            "secrets rather than simply travelling it. Stella Durus "
            "respects its claim.",
        ),
        secrets=paragraphs(
            "Heraclean vis: someone who walks the whole road from the "
            "Le Perthus pass to the Col de Montgenèvre carrying a lion's "
            "skin, and camps for the night at six of the old mansio "
            "sites, finds 6 pawns of Intellego vis in the skin. One "
            "site is an open lot inside Narbonne, and Ara Maxima Nova "
            "watches the road closely. Its magi do not yet know of "
            "this vis, but some local faeries do and might trade the "
            "knowledge.",
            "An Iberian Redcap carrying Tibaut's sealed letter to "
            "Beatrice died of an ambush by crusader camp followers in "
            "the wilds along the road; the letter is still in his "
            "satchel (see The Serpent's Venom).",
        ),
        **KNOWN_ORDER,
    )
    _add(
        provence,
        "aude",
        "The River Aude",
        inside=region,
        summary="The river that runs down from the Pyrenees past Carcassonne "
        "to Narbonne and the sea, giving the city its port. A powerful "
        "magic spirit, a daimon, dwells in it. Stella Durus sits on "
        "its left bank, and Marcella of Bonisagus has studied its "
        "spirit for years.",
        secrets="Marcella hopes to tap the Aude's spirit for vis without "
        "killing it. One of the paths open to her is a ritual murder "
        "of the spirit for a single great store of vis; if that is "
        "done, the river will silt up over the years and Narbonne "
        "will decline as a port.",
        **KNOWN_REGION,
    )


# ------------------------------------------------------------ Stella Durus


def _stella_durus(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    region = provence.places["narbonnais"]
    site = _add(
        provence,
        "stella_durus",
        "The Villa of Stella Durus",
        inside=region,
        aura=2,
        summary=(
            "An old Roman villa on the left bank of the Aude, just outside "
            "Narbonne, altered, enlarged and rebuilt many times, with an "
            "old manor farm. Nothing about it stands out and it is hardly "
            "defended. Neighbours take it for the house of a merchant who "
            "travels a great deal, or of a petty lord away on crusade, and "
            "leave it alone. A Roman mithraeum once stood in its "
            "basements, which hold a Magic aura of 2."
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A small, cosmopolitan Autumn covenant on the outskirts of "
        "Narbonne, of Bonisagus, Flambeau, Jerbiton and one far-sighted, "
        "ambitious Tytalus. Its device is a shining five-pointed star. Its "
        "name speaks of the stars that guide explorers and plays on the "
        "senses of durus: hardy, rough and steadfast. Its magi study the "
        "region's magical spirits and ancient ruins, and want above all "
        "to go unnoticed by Hermetic and mundane politics while the "
        "crusade runs its course.",
        "It began as a small estate with an old manor farm beside the "
        "Aude. Its magi lived quietly among their neighbours, helping the "
        "city grow through the eleventh and twelfth centuries while the "
        "covenant recovered from its long-dead founders' part in the "
        "Schism War and some ventures against the Moors of Iberia. "
        "Marcella of Bonisagus and Jean Marie of Jerbiton are its "
        "seniors; Marcella's love of exploration and Jean Marie's taste "
        "for a pleasant country life drew Renaud, with his interest in "
        "Mithraic sites and troubadours.",
        "Its one real rule is that its members are individuals who have "
        "joined for protection and shared resources. Beyond a loose wish "
        "to keep the house standing, nothing binds them: they skip "
        "council meetings, squabble over who does which chore, and guard "
        "their own time. They like being near Narbonne and find the river "
        "a good enough moat. Its policy is to hide in plain sight.",
        "Its covenfolk and grogs come from many lands, brought by "
        "different magi over the years, and speak half a dozen tongues, "
        "the cause of most of their quarrels; Marcella likes the mix and "
        "urges them to keep their languages up. Its veteran turb is "
        "skilled but bored, and may not drill where it could be seen, so "
        "Renaud looks for ways to keep it sharp.",
    )
    what_matters = _lines(
        "Vis: none named by the book; Marcella and Giacoma seek a way to draw vis from the spirit of the Aude",
        "Income: Jean Marie helps run a relative's shipping company",
        "Library: Bonisagus research on spirits and genii loci, and Jean Marie's Intellego, Mentem, Rego and Vim (no books named)",
        "Aura: Magic 2, in the basements where a mithraeum stood",
        "Boon: Veteran Fighters (the bored turb), Manor House (the villa), Informants (Jean Marie's troubadour contacts)",
        "Hook: Poorly Defensible; Urban (Narbonne at the door); Roman Ruins (the villa and its mithraeum); Fractured Council",
        "Tension: Renaud and Jean Marie want to take in a troubadour; the others fear a wandering storyteller inside the walls",
        "Tension: Ducaru's meddling in noble marriages could bring charges at Tribunal",
        "Tension: the magi skip meetings and bicker over chores",
        "Policy: neutral toward new covenants, unless one takes its resources or settles between the Pyrenees and the counties of Albi, Béziers and Toulouse; it harasses those for at least a season a year",
        "Politics: 5 votes; usually follows Castra Solis through Renaud; would stay out of the crusade; counted in the Pyrenean conservative bloc",
    )
    notes = paragraphs(
        "Votes and politics. Stella Durus has 5 votes at Tribunal. Busy "
        "with their own projects, its magi rarely meddle in others'. They "
        "have usually backed Castra Solis, Renaud's domus magna, and act "
        "against it only when they must; they let the Coenobium lead so "
        "long as it leaves their projects alone; they feel they have "
        "escaped notice so far and see no need for the faidits' "
        "resistance. Jean Marie's letters keep it close to Bellaquin. It "
        "honours Ara Maxima Nova's unspoken claim to the Via Domitia. "
        "With Aedes Mercurii, Ara Maxima Nova and Miniata Sophia it is "
        "counted among the conservative southern covenants that would "
        "wait out the crusade, and that might boycott or secede if the "
        "Tribunal moved against the crusaders.",
        "Marcella's research. Her next steps might be: a ritual like "
        "Wizard's Communion, needing magi strong in Muto, Rego and the "
        "elemental Forms, to bind a lasting link to the Aude's spirit and "
        "harvest it as one distils Vim vis, but with a richer yield, at "
        "the cost of the daimon's knowing and loathing it; a long "
        "negotiation in which an Aspect of the daimon makes a willing "
        "sacrifice, strengthening its bond with the town's locus over "
        "time while yielding vis through a brief loss of Might; a ritual "
        "murder of the river's spirit for a single bolus of vis of the "
        "storyguide's choosing; or the search for the Roman watermills "
        "of Barbegal, which would set her against the Coenobium, so she "
        "would pay others, perhaps the players, in texts and connections "
        "to look for her.",
    )
    hidden = _lines(
        "Marcella has not yet found how to link a city's people to a daimon, how to call up an Aspect to harvest without the daimon noticing, or how to tap a spirit's locus for vis and leave it undisturbed; she guards her progress closely, and Toulouse's spirit would teach her much, but she will not go there.",
        "If the ritual murder of the Aude's spirit is done, the river will silt up over the years and Narbonne will decline as a port.",
        "Ducaru may have helped Ramon Berenguer IV escape the Templars in 1219, and works toward marriages that will, in time, marry the count's daughters into the royal houses of France, England and Sicily and to Richard of Cornwall.",
    )
    covenant = b.covenant(
        "Stella Durus",
        tribunal=tribunal,
        founded=None,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        aura=2,
        season="Autumn",
    )
    provence.covenants["stella_durus"] = covenant
    _stella_durus_magi(provence, b, covenant)
    b.book(
        covenant,
        "The library of Stella Durus",
        "Other",
        description=(
            "The book names no books here. The collection reflects its "
            "magi: two Bonisagi's work on genii loci, daimons and spirit "
            "vis; Renaud's Mithraic lore gathered from ruins and "
            "universities; and Jean Marie's strengths in Intellego, "
            "Mentem, Rego and Vim, on which he writes tractatus as prizes "
            "for his paradoxographia."
        ),
    )
    b.book(
        covenant,
        "Jean Marie's Paradoxographia",
        "Other",
        author="Jean Marie of Jerbiton",
        description=(
            "Letters of travel marvels Jean Marie writes about his "
            "journeys, especially his visit every five years to his "
            "birthplace near Marseilles, salted with lies. He sends them "
            "to a list of magi, Bellaquin's among them, and gives vis or a "
            "tractatus on Intellego, Mentem, Rego or Vim to whoever spots "
            "the most falsehoods."
        ),
    )


def _stella_durus_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["marcella"] = b.magus(
        "Marcella of Bonisagus",
        covenant=home,
        house=BONISAGUS,
        age=92,
        summary=paragraphs(
            "The elder Bonisagus of Stella Durus, far from her native "
            "Lancaster; she looks about sixty-three. She believes a "
            "genius loci or daimon and a nearby town can live in "
            "symbiosis, the people strengthening the spirit, so that "
            "vis it makes regularly, too little to be worth hunting, "
            "could be gathered; she is working on the spirit of the "
            "Aude. Obsessive in research, she keeps strange hours, "
            "chases tangents and travels wherever a lead or an expert "
            "takes her. She loves talking Hermetic theory with anyone, "
            "and at Tribunal is known for trapping listeners with odd "
            "trivia until something more urgent rescues them.",
            "She leaves the covenant's necessary chores to Jean Marie "
            "and cares only that there is money for supplies. She "
            "talked her filia Giacoma into coming back to help her for "
            "seven years in return for getting her out of trouble; "
            "Giacoma's indiscretions disappoint her. She is a "
            "suitable parens for a new magus of the Tribunal.",
        ),
        secrets="She secretly fears that one day she may be unable to protect "
        "or rescue her old apprentice. She keeps her progress on "
        "the Aude a close secret, and will not risk going to Toulouse "
        "to study its spirit, though it would help her.",
        traits={"Focused": 2, "Nurturing": 2, "Oblivious": 2},
    )
    m["giacoma"] = b.magus(
        "Giacoma of Bonisagus",
        covenant=home,
        house=BONISAGUS,
        age=28,
        summary=(
            "Filia of Marcella, who ran up a large debt through a "
            "Tribunal ruling in Rome and owes vis to a spiteful covenant "
            "on the far side of the Adriatic. Her mater offered her a bargain: work "
            "with Marcella on the spirit of the Aude three seasons a year "
            "for seven years, and get the vis to clear the debt, a share "
            "of the findings, and a Longevity Ritual. Somewhat bitter to "
            "be back in her mater's laboratory but glad to have escaped, "
            "she hopes the work will show a better method of drawing Vim "
            "vis out of nature spirits and so find vis in poor regions, which "
            "would make her rich, the thing she really cares about. She "
            "loves the worldly power of wealth and steers her own "
            "research toward it. She looks her age."
        ),
        traits={"Self-Serving": 3, "Inquisitive": 2, "Willing to Cut Corners": 2},
    )
    m["renaud"] = b.magus(
        "Renaud of Flambeau",
        covenant=home,
        house=FLAMBEAU,
        age=54,
        summary=paragraphs(
            "Filius of Cyprian of Tolosa Paratge, and a petty Norman "
            "lord's third son, fostered with an uncle who was a petty "
            "knight; he looks about forty. He has fought in Iberia, in the "
            "Albigensian Crusade, and in the Third Crusade soon after his "
            "Gauntlet. A believer in a sound mind in a sound body, he "
            "trains with the grogs as their mercenary captain and is the "
            "magus in charge of defences, and his battle record makes him "
            "known as a capable warrior and magus.",
            "Close calls with jinn in Iberia and disgust at the nobles "
            "leading the crusade left him soured and looking for "
            "inspiration, until a talk at Tribunal with Jean Marie about "
            "the troubadours brought him here. He hunts Mithraic lore in "
            "Roman ruins and the universities and enjoys living at the "
            "heart of the troubadours' art; twice he has proposed that "
            "the covenant take a troubadour under its patronage, and he "
            "may keep one himself despite the risk. He keeps Stella Durus "
            "close to Castra Solis and worries for his pater in the "
            "Toulouse feud. A suitable parens for a new magus.",
        ),
        traits={"Dignified": 3, "Courageous": 2, "Foolhardy": 2},
    )
    m["jean_marie"] = b.magus(
        "Jean Marie of Jerbiton",
        covenant=home,
        house=JERBITON,
        age=87,
        summary=paragraphs(
            "A follower of Jerbiton in pleasant semi-retirement, who "
            "looks about forty-five. Born just outside Marseilles, he "
            "goes back every five years, and now and then travels to "
            "Paris or on pilgrimage to Compostela or Rome. He advises "
            "and helps manage a relative's shipping company, and "
            "manages Stella Durus too, keeping it tasteful and "
            "observing every rule of Hermetic courtesy and "
            "hospitality. His strengths are Intellego, Mentem, Rego "
            "and Vim, and his paradoxographia, travel letters full of "
            "lies with a prize for the reader who finds the most, are "
            "much enjoyed, at Bellaquin above all.",
            "He likes Renaud's idea of a troubadour in the household "
            "and thinks of founding a league of magi who love "
            "troubadours and courtly love, to help the poets flourish "
            "despite the crusade, though he fears it might draw "
            "crusaders hunting Cathar refugees among the region's "
            "sympathetic nobles. He has lately taken up subtle "
            "Imaginem to tell better stories. A suitable parens for a "
            "new magus.",
        ),
        secrets="Through letters with Mariola of Tolosa Paratge he has fallen "
        "in love with her. He suspects Ducaru's game, since the Tytalus "
        "sometimes pumps him for news of the local nobles gathered "
        "through his troubadour friends.",
        traits={"Genial": 3, "Spendthrift": 2, "Talkative": 2},
    )
    m["ducaru"] = b.magus(
        "Ducaru of Tytalus",
        covenant=home,
        house=TYTALUS,
        age=44,
        summary=paragraphs(
            "A Romanian trained in the Theban Tribunal, who looks about "
            "thirty-four and is never seen without his goatskin cap. "
            "He joined Stella Durus for his own ends, and most of the "
            "Tribunal is very aware of him. His mastery of Mentem "
            "serves his purposes, though his expert Vim only makes "
            "people suspicious. He listens more than he talks, prefers "
            "to make a suggestion and watch what follows, and often "
            "acts, especially unexpectedly, just to see the outcome. "
            "He does not think himself evil but lets neither morals "
            "nor custom limit him.",
            "The least involved in running the covenant, he always "
            "helps at the most telling moment. He keeps a chess game "
            "going in a Perpignan tavern, where he is beating Etienne "
            "of Ara Maxima Nova after months of play, and Redcaps wager "
            "on the result.",
        ),
        secrets=paragraphs(
            "He means to work his way into the nobility and broker "
            "marriages and alliances from the shadows, and has begun, "
            "under a Norman persona; if it became well known he could "
            "face charges at Tribunal. He may have helped Ramon "
            "Berenguer IV escape the Templars in 1219, and the count's "
            "four daughters will one day marry into the royal "
            "houses of France, England and Sicily and to Richard of Cornwall; how "
            "he picks his matches (divination, eastern prophecy or "
            "sharp politics) and what he gains is unknown. He may be "
            "conspiring with Isabella of Angoulême to secure her line.",
        ),
        traits={"Boastful": 2, "Calculating": 2, "Reckless": 2},
    )


# --------------------------------------------------------- Ara Maxima Nova


def _ara_maxima_nova(provence: Provence, b: Builder, tribunal: Tribunal) -> None:
    roussillon = provence.places["roussillon"]
    site = _add(
        provence,
        "ara_maxima_nova",
        "The Villa of Ara Maxima Nova",
        inside=roussillon,
        summary=(
            "A cluster of small buildings round a modest villa, with "
            "vineyards and cork nurseries, among the many farming estates "
            "on the outskirts of Perpignan. It does not hide from its "
            "neighbours but keeps a carefully ordinary face. The book "
            "gives no aura."
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A Summer covenant grown rich on wine and cork, whose name means "
        "New Great Altar and whose device is a wine barrel. Three Merinita "
        "and a Gifted Mercere keep their laboratories here and have "
        "founded a splinter cult of the Keepers of a Thousand Tales, "
        "coloured by the Cult of Heroes and centred on the Via Domitia, "
        "the road both Heracles and Hannibal took. The Merinita hope to "
        "reach the spirits of vineyards older than Antiquity and learn the "
        "Dionysian mysteries from them, tracing how their road to "
        "enlightenment runs with the Roman roads and the wanderings of "
        "Heracles.",
        "Founded twenty-five years ago by its Merinita, it exists to "
        "develop the cult its senior magus made. After studying "
        "Heracles' trials in the east and reaching several initiations by "
        "experiment, they came west to explore the remaining labours and "
        "live nearer Rome. Perpignan's self-governing commune suited them, "
        "and so did open access to what is left of the Via Domitia. Their "
        "magic soon made them leading producers of wine and cork, with "
        "good stock even in years when weather or bad luck ruin others, "
        "sold to loyal buyers who ask little; with their mundane duties "
        "met, the magi have money to spare.",
        "Secrecy matters above all: they cast the Aegis of the Hearth at "
        "night, hidden by Luc's Imaginem, so that even most covenfolk "
        "never see it. They do not deny their House but are truly "
        "estranged from it. Friendly enough, they stay out of Tribunal "
        "politics unless their research is threatened. Their Herculean "
        "studies have gone better than the Dionysian, since the hero's "
        "tales escaped the purges that pagan mystery cults suffered.",
        "Three customs mark them. They make pilgrimages to Rome, to St. "
        "Stephen of the Carriages, a temple of Heracles turned church to "
        "save it, the original Ara Maxima, to study its architecture, seek "
        "relics, regiones and clues, hampered by the Dominion and wary of "
        "the clergy; they hope to rebuild it at the heart of the covenant "
        "and collect any art or text on Heracles, their treasure being a "
        "huge carved bearded head of the hero, gazing downward, recovered "
        "from Roman ruins. They seek the Hesperides: their charter sends a "
        "magus with grogs on a quest of up to two years every five years, "
        "and they have searched Durenmar, the remains of Alexandria's "
        "Museum, Constantinople and the universities of Paris and "
        "Montpellier, and would trade generously for a reliable route. And "
        "they court the faeries of the region's farms and vineyards; they "
        "have found nymphs and satyrs, but none who knows or will share "
        "the old rites. They believe ascension lies in retracing Heracles' "
        "labours through rituals that mirror them, crimes and penance "
        "included, and look for the tomb of Pyrene somewhere to the "
        "south-west.",
        "Covenfolk come from peasants seeking a new life in Perpignan, "
        "refugees from the Reconquista among them, and, to some dispute, "
        "slaves Etienne buys from Arab merchants. Many vineyard and cork "
        "workers have no idea whom they serve. A trusted, well-paid inner "
        "household tends the magi but is seldom allowed to travel far; "
        "only the small, well-trained turb, the foremen and the men who "
        "deal with Perpignan's merchants go farther.",
    )
    what_matters = _lines(
        "Vis: none of its own named by the book; the Ancient Wine Press (Herbam 4, or Infesta 6), the Nemausian Spring (Creo or Aquam 3) and the Abandoned Mine (Terram 2) lie unclaimed in Narbonnais",
        "Vis: the Via Domitia's Heraclean vis (Intellego 6) is on the road it guards, though its magi do not know of it",
        "Income: wine and cork, sold to loyal customers who ask few questions",
        "Library: texts on Heracles, the Dionysian mysteries and the Via Domitia, and Jeanne's faerie journals (no books named)",
        "Treasure: a colossal carved head of Heracles from the ruins of Rome",
        "Charter: a Hesperides quest every five years, one magus and grogs, for no more than two years",
        "Boon: Wealth, Secondary Income (wine and cork), Loyal Covenfolk (the inner household)",
        "Hook: Road (the Via Domitia); Dark Secret (Luc's cult); Ceremonies; Slavery; Hermetic Politics (estranged from House Merinita)",
        "Tension: Jeanne and Luc's wife Miriam quarrel over the cult; Etienne chafes at Luc's neglect of the covenant",
        "Tension: its magi challenge others on the Via Domitia to certamen, which the Coenobium resents",
        "Policy: harasses new magi whose Faerie or Seeker interests overlap its own unless they join the cult; otherwise neutral, so long as the Via Domitia is left open to it",
        "Politics: 4 votes; follows Castra Solis or abstains; Luc quietly works against the Coenobium; counted in the Pyrenean conservative bloc",
    )
    notes = paragraphs(
        "Votes and politics. Ara Maxima Nova has 4 votes. To keep the "
        "crusaders' eyes off it, it gives Castra Solis no reason to look "
        "closely, following its lead or abstaining. Luc thinks the "
        "Coenobium a bully to be defied and undermines it quietly. It "
        "talks with Aedes Mercurii and sometimes helps it, curious what "
        "secrets lie unrecognised in that old covenant; it would side "
        "with the faidits only if crusaders threatened it. It sends agents "
        "to the Andorran fairs. With Aedes Mercurii, Stella Durus and "
        "Miniata Sophia it is counted among the conservative southern "
        "covenants that would wait out the crusade.",
        "Story: Ara Maxima Nova might fund a joint expedition to the "
        "Hesperides with the players' covenant, built on what the "
        "players' magi learn (Ancient Magic). A storm raised by the dragon "
        "of the fierce currents could part the ships or wreck them on "
        "arrival, leaving the two parties to explore the islands, look "
        "for each other and a way home, and perhaps fight over the "
        "islands once reunited.",
        "Stella Durus honours its claim to the Via Domitia, and the two "
        "are cordial but distant neighbours. The Plaine de la Crau in "
        "Arelat, where Heracles stoned the giants Bergion and Ligur, "
        "interests it greatly.",
    )
    hidden = _lines(
        "Luc's cult is the secret behind the covenant; Castra Solis's devout members would quietly move against his resources if they learned of it.",
        "The magi do not know that walking the whole Via Domitia with a lion's skin yields 6 pawns of Intellego; local faeries do, and might sell the knowledge.",
        "Luc's grumbling to Dama about Tibaut's questions, after a certamen he lost to the Quaesitor, warned her of the investigation (see The Serpent's Venom).",
    )
    covenant = b.covenant(
        "Ara Maxima Nova",
        tribunal=tribunal,
        founded=1195,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        season="Summer",
    )
    provence.covenants["ara_maxima_nova"] = covenant
    _ara_maxima_nova_magi(provence, b, covenant)
    b.book(
        covenant,
        "The library of Ara Maxima Nova",
        "Other",
        description=(
            "The book names no books here. Its magi gather every text, "
            "carving and work of art on Heracles and his labours, notes "
            "from their pilgrimages to St. Stephen of the Carriages in "
            "Rome and from searches of Durenmar, Alexandria, "
            "Constantinople, Paris and Montpellier for the Hesperides, and "
            "Luc's experiments in cult rites. Luc wants to write an "
            "excellent text of his cult's teachings to pass, carefully, "
            "to sympathetic magi."
        ),
    )
    b.book(
        covenant,
        "Jeanne's Winter Journals of the Fae",
        "Other",
        ability="Faerie Lore",
        author="Jeanne of Merinita",
        description=(
            "Every winter Jeanne writes down her dealings with faeries "
            "that year, meaning one day to work them up into an "
            "authoritative summa on Faerie Lore."
        ),
    )


def _ara_maxima_nova_magi(provence: Provence, b: Builder, home: Covenant) -> None:
    m = provence.magi
    m["luc"] = b.magus(
        "Luc of Merinita",
        covenant=home,
        house=MERINITA,
        age=66,
        summary=paragraphs(
            "Mystagogue of a splinter of the Merinita branch of the "
            "Keepers of a Thousand Tales, a branch now absorbing the ways "
            "of the Cult of Heroes (Houses of Hermes: True Lineages), "
            "and unofficial leader of Ara Maxima Nova; he looks about "
            "fifty-four. A master of Imaginem, Mentem and Vim, "
            "obsessed with mysteries, he put off his Longevity Ritual "
            "until nearly fifty for fear it would spoil his pursuit of "
            "the Dionysian mysteries' sexual side. An inventive "
            "genius, thought to have been initiated as an apprentice, "
            "he crafts new initiations by blending odd esoterica, "
            "faerie tales and encounters, and astrological and "
            "natural signs, guided by visions from drinks laced with "
            "mandrake or poppy. He neglects the covenant's daily "
            "business, to Etienne's annoyance.",
            "His wife Miriam, a failed apprentice, is his lab "
            "assistant, fellow cultist and muse; they have two "
            "marriageable daughters. He leans on his sister Jeanne in "
            "every crisis, feeling only she understands their "
            "childhood under a harsh, sometimes cruel deacon in "
            "Brittany. He is infatuated with Guillermo. A suitable "
            "parens for a new magus.",
            "His goals: to find the Hesperides and steal their apples, "
            "the last labours but one of his reenactment, and then "
            "pass a lapis manalis he believes he has found into a "
            "regio where Cerberus may wait; to leave a lasting legacy "
            "for his cult in House Merinita and perhaps the Order, "
            "through a fine text (he would seize on the Elysian "
            "Ecstasy or Olympian Pact of The Sundered Eagle if he "
            "learned of them); and to undo his Longevity Ritual's "
            "sterility and father a son who could be his apprentice, "
            "the one dream that might make him set aside ascension.",
        ),
        secrets=paragraphs(
            "He has had many lovers of both sexes during his studies "
            "and does not say so, and there may be unknown bastards of "
            "his around the Mediterranean.",
            "After Tibaut questioned him hard about trouble with clergy "
            "or pilgrims on the Via Domitia and beat him at certamen "
            "for the answers, Luc gave only the barest replies and "
            "complained of it to Dama, telling her which Arts to "
            "expect: that warned her of the investigation.",
        ),
        traits={"Intense": 3, "Charismatic": 2, "Outspoken": 2},
    )
    m["etienne"] = b.magus(
        "Etienne of Merinita",
        covenant=home,
        house=MERINITA,
        age=68,
        summary=(
            "With Luc from the start through a chance fostering, he runs "
            "and administers Ara Maxima Nova and receives its visitors, "
            "keeping its buildings perfect with near-obsessive care. A "
            "specialist in Animal, Herbam, Muto and Rego, stocky, taciturn, "
            "dark and sharp-eyed, he looks about forty-three and has the "
            "Gentle Gift. He was once Luc's lover and ended it when Luc "
            "married Miriam; an active cultist with no wish for its "
            "innermost secrets, he simply wants to stay near Luc and help "
            "his search. Celibate outside the cult's rites, he loves "
            "sweets and chess and finds excuses to go into Perpignan for "
            "both, where Ducaru of Stella Durus is beating him in a long "
            "tavern game. He buys some slaves for the covenant from Arab "
            "merchants, and means to look for an apprentice very soon. A "
            "suitable parens for a new magus."
        ),
        traits={"Calm": 2, "Curious": 2, "Dedicated": 2},
    )
    m["jeanne"] = b.magus(
        "Jeanne of Merinita",
        covenant=home,
        house=MERINITA,
        age=63,
        summary=paragraphs(
            "Luc's younger sister, who looks about forty-six. Where "
            "Etienne is relaxed, she is eager and anxious, weighing "
            "everything for advantage. She dislikes Luc's wife Miriam and "
            "they argue over the cult's direction; Luc usually finds a "
            "middle way that leaves each a little pleased to see the "
            "other thwarted.",
            "When her first pater died, the aged Caprican of Oleran (see "
            "The Lion and the Lily), in Aquitaine, finished her training as a "
            "favour to him; she cares nothing for his Stone Couches or his "
            "covenant's leadership, though he may come looking for a "
            "reluctant champion for the Apple Mile. Initiated during her "
            "training, she wrote to her brother, and the two built the "
            "core of their cult. She seeks the Dionysian secrets the fae "
            "remember, is the covenant's expert on Arcadia and faerie "
            "customs, and keeps winter journals of her faerie encounters "
            "for a future summa. A suitable parens for a new magus.",
        ),
        traits={"Dedicated": 3, "Energetic": 2, "Reliable": 2},
    )
    m["guillermo"] = b.magus(
        "Guillermo of Mercere",
        covenant=home,
        house=MERCERE,
        age=56,
        summary=paragraphs(
            "A Gifted Mercere from Genoa, the covenant's newest member "
            "and the only one from outside France, who looks about "
            "thirty-three. Research into Heracles and Hannibal for the "
            "Cult of Heroes, plus a lord's mistaken idea about him and "
            "the lord's wife, sent him to the Via Domitia, where he kept "
            "meeting Luc; after several friendly certamen bouts over "
            "ruins and resources, which he lost, and long talks on "
            "heroic ascension, Luc invited him into the cult's first "
            "initiations. Luc is fascinated by his knowledge of old "
            "tales and of the land, and Guillermo feeds the "
            "infatuation to learn all he can.",
            "Soon after his Gauntlet he saved a young Tremere, "
            "Sagittaire, from bandits, and she taught him the Carvers' "
            "school of certamen (Houses of Hermes: True Lineages); he "
            "is known for gladly standing champion for any Redcap of "
            "the Tribunal who asks. A suitable parens for a new magus.",
        ),
        secrets="His loyalty is to himself alone: made to choose between a "
        "great sacrifice for the covenant and his own good, he will "
        "choose himself.",
        traits={"Bold": 2, "Foolhardy": 2, "Proud": 2},
    )


# ------------------------------------------------------------- ties


def finish(provence: Provence) -> None:
    """Links to the magi other parts make: Renaud's parens and Jean
    Marie's correspondent at Tolosa Paratge."""
    b = provence.b
    m = provence.magi
    if "renaud" not in m:
        return
    cyprian = _character(provence, "Cyprian")
    if cyprian is not None:
        b.link(m["renaud"], "characters", cyprian, "His parens")
    mariola = _character(provence, "Mariola")
    if mariola is not None:
        b.link(m["jean_marie"], "characters", mariola, "His correspondent")
    b.link(m["giacoma"], "characters", m["marcella"], "Her mater")
    b.link(m["jeanne"], "characters", m["luc"], "Her brother")
    b.link(m["ducaru"], "characters", m["etienne"], "His chess rival in Perpignan")


# --------------------------------------------------------------- stats

P = Profile


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


def _ability(name: str, ability: str) -> tuple[str, dict[str, str]]:
    return (name, {"ability": ability})


AREA = "Area Lore: Provençal Tribunal"

#: Each magus the book sketches without a stat block, by character id.
PROFILES: dict[str, Profile] = {
    "marcella": P(
        strong="int com per",
        arts={"Vi": 7, "In": 5, "Mu": 4, "Re": 4, "Aq": 3, "Cr": 2},
        abilities={
            "Magic Lore": (4, "genii loci"),
            "Magic Theory": (3, "vis"),
            "Teaching": 2,
            AREA: 2,
        },
        virtues=[
            _art("Affinity with {art}", "vim"),
            "Inventive Genius",
            "Obsessed (Minor)",
            "Busybody",
        ],
        native="English",
    ),
    "giacoma": P(
        strong="int com",
        arts={"Vi": 5, "In": 4, "Cr": 3, "Re": 3, "Aq": 2},
        abilities={"Bargain": (3, "vis"), "Magic Lore": (2, "spirits")},
        virtues=["Inventive Genius", "Greedy (Minor)", "Enemies"],
        native="Italian",
    ),
    "renaud": P(
        strong="sta str int",
        arts={"Ig": 6, "Cr": 5, "Pe": 4, "Co": 2, "Re": 2},
        abilities={
            "Single Weapon": (4, "sword"),
            "Leadership": (3, "grogs"),
            "Ride": 2,
            "Athletics": 2,
            "Area Lore: Iberia": 1,
        },
        virtues=["Warrior", "Tough", "Reckless"],
        native="French",
    ),
    "jean_marie": P(
        strong="com pre int",
        arts={"Me": 6, "In": 5, "Re": 5, "Vi": 5, "Im": 3},
        abilities={
            "Etiquette": (3, "nobles"),
            "Charm": (3, "conversation"),
            "Bargain": (2, "shipping"),
            "Music": 1,
            AREA: 2,
        },
        virtues=["Well-Traveled", "Busybody"],
        native="Occitan",
    ),
    "ducaru": P(
        strong="int per com",
        arts={"Me": 7, "Vi": 6, "In": 3, "Re": 3, "Im": 3},
        abilities={
            "Intrigue": (4, "marriages"),
            "Guile": (3, "false identities"),
            "Folk Ken": (3, "nobles"),
            "Etiquette": 2,
        },
        virtues=[
            _art("Affinity with {art}", "mentem"),
            "Dark Secret",
            "Reckless",
        ],
        native="Romanian",
    ),
    "luc": P(
        strong="int pre per",
        arts={"Im": 7, "Me": 7, "Vi": 6, "Cr": 3, "Mu": 3},
        abilities={
            "Faerie Lore": (4, "Dionysian rites"),
            "Leadership": (2, "cultists"),
            "Charm": 2,
        },
        virtues=["Inventive Genius", "Visions", "Lecherous (Minor)", "Driven (Major)"],
        native="Breton",
    ),
    "etienne": P(
        strong="int sta",
        arts={"An": 6, "He": 6, "Mu": 5, "Re": 5},
        abilities={
            "Bargain": (3, "wine merchants"),
            "Profession: Steward": (3, "the covenant"),
            AREA: 1,
        },
        virtues=["Gentle Gift", "Dutybound", "Vow (Minor)", "Compulsion (Minor)"],
        native="Occitan",
    ),
    "jeanne": P(
        strong="int per pre",
        arts={"Me": 5, "Im": 5, "In": 4, "Mu": 3},
        abilities={
            "Faerie Lore": (4, "Arcadia"),
            "Faerie Speech": 2,
            "Etiquette": (2, "faerie customs"),
        },
        virtues=["Faerie Sight", "Close Family Ties"],
        native="Breton",
    ),
    "guillermo": P(
        strong="pre com sta",
        arts={"Re": 5, "Mu": 4, "Co": 4, "Ig": 3, "Vi": 3},
        abilities={
            "Certamen": (3, "the Carvers' style"),
            "Ride": (2, "long journeys"),
            "Area Lore: Via Domitia": 3,
            "Organization Lore: House Mercere": 2,
        },
        virtues=["Well-Traveled", "Proud (Minor)"],
        native="Italian",
    ),
}


def stats(provence: Provence) -> None:
    """Generated stats for the magi of Narbonnais; the book prints none."""
    b = provence.b
    for key, profile in PROFILES.items():
        apply(b, provence.magi[key], profile)
