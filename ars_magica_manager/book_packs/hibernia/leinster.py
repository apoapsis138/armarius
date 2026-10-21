"""Leinster, the south-east of the Hibernian Tribunal, as of 1220: the
province (places["leinster"]) with its three peoples, the Laighin, the
Osraighe and the Ostmen; the County of Wexford, the Wicklow Mountains,
the Liberty of Kildare, Ossory and the Liberty of Carlow, with their
towns, castles, holy places, faerie sites and vis; the three covenants
of the province, Ashenrise (the English reformers, whose cathach is the
dancing corpse of Rhiannon), Lámbaird (the Flambeau of the School of
Raghallach) and the Paruchia of Nerius (the Hermetic Céli Dé, with
Indrechtach's stat block as the book prints it), and their magi; the
English lords of the Liberty of Leinster and the Gaelic clans who
resist them from the hills; and the bishops, abbeys and churches of the
province (Ferns, Glendalough, Kildare's sacred fire, Dublin's two
cathedrals, Baltinglass, Jerpoint, Kells and Kilkenny). In paraphrase of
The Contested Isle, chapter six.

Keys: the province is places["leinster"], its regions places
["wexford_county"], ["wicklow"], ["kildare_liberty"], ["ossory"] and
["carlow"]; the covenants are covenants["ashenrise"], ["lambaird"] and
["paruchia"]; the magi are magi["helles"], ["pollices"], ["dyfrgi"],
["tug"], ["dorjan"], ["konstanczia"] (Ashenrise), ["dalton"],
["brian"], ["cliodna"] (Lámbaird), ["fedelmid"], ["indrechtach"] and
["coemgen"] (the Paruchia). The Liberty of Leinster, held by William
Marshal the Younger, is world["leinster_liberty"]; Dublin the town is
world["dublin"] (the viceroy who governs it is meath.py's lord, and the
see church.py's). Bóinn, who lives at Carbury, is the Bestiary's, and
so are the Púca's kind and the Swine of Drebrenn, named here only in a
sentence. The chapter's story seeds are stories.py's."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING, Any

from ... import catalog
from ...models.world import FULL
from ..builder import paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from ..builder import Builder, StatBlock
    from . import Hibernia

BJORNAER = "house_bjornaer"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
JERBITON = "house_jerbiton"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(hibernia: Hibernia, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = hibernia.b.place(name, **kw)
    hibernia.places[key] = place
    return place


def _tribunal(hibernia: Hibernia) -> Tribunal | None:
    if hibernia.tribunal is not None:
        return hibernia.tribunal
    return next(iter(hibernia.b.saga.tribunals), None)


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    _province(hibernia)
    _regions(hibernia)
    _places(hibernia)
    _lords(hibernia, b)
    _towns(hibernia, b)
    _churches(hibernia, b)
    tribunal = _tribunal(hibernia)
    if tribunal is None:
        # tribunal.py builds the Tribunal first; while it is a stub,
        # the covenants wait for it.
        return
    _ashenrise(hibernia, b, tribunal)
    _lambaird(hibernia, b, tribunal)
    _paruchia(hibernia, b, tribunal)


# ------------------------------------------------------------ the province


def _province(hibernia: Hibernia) -> None:
    _add(
        hibernia,
        "leinster",
        "Leinster",
        inside=hibernia.places.get("ireland"),
        summary=paragraphs(
            "The south-eastern province of Ireland, milder and drier than "
            "the rest of the island. Its many harbours face the Irish Sea, "
            "and its trade runs to England and Wales, Bristol above all. "
            "Behind a rich coastal strip rise the Wicklow Hills, low "
            "mountains that have always kept invaders out of the plains "
            "and sheltered outlaws and the dispossessed. The old Kingdom "
            "of Leinster has grown and shrunk over the centuries and was "
            "sometimes smaller than the province. Here the English first "
            "came, at the call of Leinster's own king, and here their hold "
            "is firmest, though the Ua Broin and the Ua Túathal fight on "
            "from the hills.",
            "Three peoples. The Laighin, who name the province, descend "
            "from Lughaidh mac Íth, uncle of Míl Espáine. Their founder "
            "Labraid Loingsech, struck dumb as a boy after he was forced "
            "to eat the hearts of his murdered father and grandfather, "
            "found his voice on the hurling field, served the King of "
            "France, and came home with an army bearing blue-tipped "
            "spears (the laighin); he burnt the usurping High-King "
            "Cobthach and thirty kings alive in an iron house at Din Rig, "
            "and his secret, the ears of an ass, was betrayed by a harp "
            "made from the willow his barber whispered it to. The "
            "Osraighe, the Deer People of Ossory in the west, are an "
            "Érainn people. The Ostmen are the Norse who founded Dublin "
            "and Wexford, Christian since the tenth century and Irish in "
            "speech, still a distinct minority in the ports.",
            "The kingdom. Úgaine Mór founded it; for centuries the Uí "
            "Cheinnselaig of the Wexford country and the Uí Dúnlainge of "
            "Kildare split it north and south, until the Uí Cheinnselaig "
            "reunited it in the eleventh century. Their last king, "
            "Diarmait mac Murchadha, schemed for the high-kingship, was "
            "driven out by Tigernán Ua Ruairc at the High-King's bidding, "
            "and brought in the Normans to win his land back. Grieving "
            "his son Domhnall, he wed his daughter Aoife to Strongbow, so "
            "that the royal line passed to the English when he died in "
            "1171. The English have ruled for some sixty years, but their "
            "ways are only now taking root outside the towns.",
            "The Hermetic province. Three covenants stand here: Ashenrise, "
            "the reformers from the continent; Lámbaird, the oldest, home "
            "of the School of Raghallach; and the Paruchia of Nerius, "
            "the Hermetic Céli Dé of Little Saltee.",
            "Vis (each in its place): the ducks of Templeshanbo (Divine "
            "Aquam, from moulted feathers); the Faerie Fire of Baltinglass "
            "(Ignem, won by contest); the tide rock off Arklow (Aquam); the "
            "Well of Wisdom at Carbury (Imaginem); the Fruit of Saint "
            "Kevin at Glendalough (Divine vis when dried); and the raw vis "
            "in Rhiannon's bones (Ashenrise's).",
        ),
        **KNOWN_ORDER,
    )


def _regions(hibernia: Hibernia) -> None:
    province = hibernia.places["leinster"]
    _add(
        hibernia,
        "wexford_county",
        "The County of Wexford",
        inside=province,
        summary=(
            "The south-eastern corner of Leinster, round the port of "
            "Wexford. In the sixty years since the English came it has "
            "become almost like England or Wales, with villages, markets "
            "and a largely Anglicized people, which makes it unlike "
            "anywhere else in Hibernia. Its towns are Wexford, Bannow, "
            "Ferns, Enniscorthy and New Ross; the Saltee islands, home of "
            "the Paruchia of Nerius, lie off its coast."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "wicklow",
        "The Wicklow Mountains",
        inside=province,
        summary=paragraphs(
            "The country round Carlow and Dublin: a low coastal plain that "
            "climbs steeply to the Wicklow mountains, which some say Saint "
            "Brigid raised by a miracle. They bar the way from the coast "
            "to the central plains, and turned back both Norse and English. "
            "Thick woods, caves and ravines among rocky hills make the "
            "outlaws who haunt the passes almost impossible to pin down. "
            "Here the Ua Broin and Ua Túathal, the old rulers, hide and "
            "fight on against the English, who call them O'Byrne and "
            "O'Toole.",
            "Lámbaird lies hidden in Gleann Molúra among these hills, and "
            "Glendalough at the crossing of their two great roads.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "kildare_liberty",
        "The Liberty of Kildare",
        inside=province,
        summary=(
            "Low inland country in the north of Leinster, cut off from "
            "Dublin on the east by the Wicklow hills. King John made it a "
            "Liberty in 1206 to crush the Uí Dúnlainge, whose kings he had "
            "set aside, and it is still fought over: English lords hold it "
            "down with a web of castles, while the Ua Broin and Ua Túathal "
            "wage a hit-and-run war against them from the hills. Its "
            "places are Kildare, Naas, the Hill of Allen, Carbury and "
            "Calverstown."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "ossory",
        "Ossory",
        inside=province,
        summary=paragraphs(
            "The old Kingdom of Ossory in the west of Leinster, seven "
            "great plains held by the Osraighe, descendants of Oengus "
            "Osraigh. Once mighty, they fell to the Ulaidh at the Battle "
            "of Tola in 571, were worn down by wars with the Vikings and "
            "the Laighin, and split into three at the start of the twelfth "
            "century; their túatha were folded into Leinster. They rose "
            "when Diarmait mac Murchadha was driven out, were beaten by "
            "Strongbow, and William Marshal built castles to tame them. "
            "Kilkenny and Kells now hold them down, though many still hate "
            "the English despite the wealth the conquest has brought. They "
            "are especially devoted to Saint Ciarán.",
            "Their royal house, the Mac Giolla Phádraig, has mostly "
            "accepted English rule and now goes by fitz Patrick. The Uí "
            "Riain, whose ancestral ráth held Rhiannon's grave, live here "
            "too.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "carlow",
        "The Liberty of Carlow",
        inside=province,
        summary=(
            "The valley of the River Barrow, between Ossory and the "
            "Wicklow hills, north of New Ross: English castles along the "
            "river, and Irish túatha, the Uí Riain and several Déise "
            "families, who resent every English lord on its banks. "
            "Ashenrise stands here."
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------------------------- places


def _places(hibernia: Hibernia) -> None:
    p = hibernia.places
    _add(
        hibernia,
        "templeshanbo",
        "The Duck Pool of Templeshanbo",
        inside=p["wexford_county"],
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "A pool by the church of a tiny hamlet under Mount Leinster, "
            "where Saint Colman once had a monastery (long gone; his feast "
            "is still kept on 27 October). It has a Dominion aura of 3 and "
            "thirteen wild ducks, very tame. Hunt or harass them and they "
            "fly away, and the pool goes brackish and foul until they come "
            "back; kill one and the pot it is cooked in will not boil, and "
            "unless the killer does proper penance the saint strikes him "
            "dead.",
            "Vis: the feathers the ducks moult are Divine Aquam vis, and "
            "anyone may gather them. No covenant claims them.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "ferns",
        "Ferns",
        inside=p["wexford_county"],
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "An old royal seat of Leinster, now a small town and village "
            "with a Dominion aura of 3. Diarmait mac Murchadha hid here "
            "before he called in Strongbow, with Derbforgaill, the Meath "
            "king's daughter he had stolen from her husband, Tigernán Ua "
            "Ruairc of Bréifne; she is sung of still "
            "as the Helen of Ireland, and the tale feeds a faerie, Aonghus "
            "son of Bóinn, who loves to stir up elopements and abductions "
            "that end in war.",
            "Here stand William Marshal the Younger's new castle, the "
            "Augustinian St. Mary's Abbey and the seat of the Bishop of "
            "Ferns, a centre of the reforming party in the Irish Church.",
        ),
        **KNOWN_REGION,
    )
    baltinglass = _add(
        hibernia,
        "baltinglass",
        "Baltinglass",
        inside=p["wicklow"],
        summary=(
            "A tiny settlement under a hill on the western edge of the "
            "Wicklow mountains, named for the hero Glas, who killed one of "
            "the six Swine of Drebrenn here: the witch Garbhdalbh's three "
            "daughters and their husbands, turned into monstrous boars "
            "that laid Ireland waste until Queen Maebh and Aillil hunted "
            "them down. A faerie swine still haunts the district, wasting "
            "the land until a hero kills it again. On the hill is the "
            "Faerie Fire; below it, the Cistercian abbey."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "faerie_fire",
        "The Faerie Fire",
        inside=baltinglass,
        realm="Faerie",
        aura=1,
        summary=paragraphs(
            "A ráth on the hill above Baltinglass, holding a mound with a "
            "stone doorway; its Faerie aura is 1 for most of the year. "
            "Druids are said to have kept an undying fire here. At "
            "midsummer a bonfire appears on top of the mound and burns "
            "until the season's first rain, and while it burns the aura "
            "rises to 3.",
            "Vis: a rich source of Ignem, but whoever would take it must "
            "beat the mound's folk at a contest of their choosing. The "
            "contest changes each year with the faerie set to guard the "
            "fire and the tale it plays out: dancing, music, storytelling, "
            "climbing and javelin throwing have all been tried, and it is "
            "never the same twice. The monks of Baltinglass mean one "
            "Christmas Day to plant a great wooden cross on the mound.",
        ),
        **KNOWN_REGION,
    )
    glendalough = _add(
        hibernia,
        "glendalough",
        "Glendalough",
        inside=p["wicklow"],
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The valley of two lakes, where the road east and west through "
            "the Wicklow Gap crosses the road south from Dublin: Saint "
            "Kevin's hermitage, then his monastery. It headed its own "
            "diocese until 1214, when the English joined it to Dublin's. "
            "A round wall rings the whole community, which is a "
            "sanctuary; the aura is Dominion 5 in the church and "
            "churchyard and 3 elsewhere.",
            "Sanctuary here lasts until the fugitive steps outside the "
            "walls, and the English have not yet dared to break it, so "
            "many have fled here: rebels against English rule (villains "
            "and brigands, to the English) and lesser criminals too.",
            "At the centre are the church and a hundred-foot round tower, "
            "plain but for four little windows facing the four quarters, "
            "from which a hand bell calls the faithful to Sunday mass and "
            "warns of good news and bad. Beyond them is the graveyard, "
            "fenced with bent willows. A few hermits live in stone cells "
            "inside the inner wall, holding out against the English "
            "churchmen; most of them, the abbot sometimes among them, are "
            "manaim with ties to the world beyond. The monks and their "
            "abbot's house, guesthouse, infirmary, kitchen and rectory "
            "fill the second wall, and outside it lay folk of every rank "
            "live much as continental villagers do.",
            "The Fruit of Saint Kevin. When a sick pupil begged for fruit "
            "and the monastery had none, Kevin prayed, and an old willow "
            "by the graveyard bore white, oblong fruit in minutes that "
            "cured the boy. The monks ringed the graveyard with its "
            "saplings, and each year, on the evening of the miracle, the "
            "willows fruit again: up to twenty-four a season, each adding "
            "+20 to recovery rolls for the season it is eaten in. The "
            "monks share them out to the sick across Ireland. Dried for a "
            "month by someone who knows Magic Theory, a fruit becomes "
            "Divine vis, Corpus if dried in a Magic aura, Creo in a Divine "
            "one.",
            "Tradition holds that whoever is buried among the willows goes "
            "to Heaven without passing through Purgatory, and many heroes "
            "lie there; the English churchmen scoff at it.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "puca_pool",
        "The Pool of the Púca",
        inside=glendalough,
        summary=(
            "On the road to Glendalough a waterfall spills down a rock "
            "face into a still, black pool. A Púca, or kelpie, haunts it: "
            "a handsome black horse that seems to have strayed onto the "
            "road; whoever mounts it is carried off at a gallop into the "
            "pool and drowned, or eaten. Locals shun the road, above all "
            "by night. Nobody knows whether it is a beast of Magic, a "
            "faerie or something Infernal, so the book gives the place no "
            "aura (for kelpies, see the Bestiary). It may be cleverer than "
            "it seems."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "arklow_rock",
        "The Tide Rock off Arklow",
        inside=p["wicklow"],
        aura=4,
        summary=(
            "A rock in the sea a few miles off Arklow where the tide falls "
            "on one side as it rises on the other: a strong magical place "
            "(Magic 4 here; the book gives no number), whose treacherous "
            "waters have drowned many sailors. Vis: Aquam, unclaimed. Not "
            "to be mistaken for Arklow Rock, a hill some miles inland."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "dun_ailinne",
        "The Hill of Allen (Dún Ailinne)",
        inside=p["kildare_liberty"],
        realm="Faerie",
        aura=4,
        summary=(
            "A hill looking west over the Bog of Allen: once the palace of "
            "the kings of Leinster, later Finn's home. A great ráth on it "
            "still holds a Faerie aura of 4, and it is no place to walk "
            "after dark."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "fechins_cross",
        "Saint Fechin's Cross",
        inside=p["kildare_liberty"],
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "A stone cross in the marketplace of Naas, raised where Saint "
            "Fechin's monastery of Tulach-Fobhair stood, south of the "
            "town, in memory of the day he came to bargain for captives. "
            "A prisoner within earshot who calls the saint's name sets an "
            "old blessing working that frees every captive, as The Captive "
            "Made Free (a saint's power; see the Bestiary). The aura is "
            "the town's Dominion, taken here as 3.",
            "The Ua Broin and Ua Túathal rebels all know it: they let "
            "themselves be caught, are held in the castle, and slip away "
            "with the saint's help as they are marched out to the gallows.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "sidh_neachtain",
        "Sídh Neachtain",
        inside=p["kildare_liberty"],
        realm="Faerie",
        aura=3,
        levels=[
            hibernia.b.level(
                "The Well of Wisdom",
                5,
                "Faerie",
                enter=(
                    "Only with Nuadha as guide, or by following the Boyne "
                    "upstream all the way to its source; on Trinity Sunday "
                    "the regio shows itself for a while in the mundane "
                    "world."
                ),
                notes=(
                    "A faerie spring ringed by nine willows, where magical "
                    "salmon who know great secrets swim. Whenever nuts drop "
                    "into the well it gives a great deal of Imaginem vis."
                ),
            )
        ],
        summary=paragraphs(
            "The faerie mound of Nuadha at Carbury, in the north of the "
            "Liberty of Kildare, beside the motte and bailey that Meiler "
            "FitzHenry built when he was Justiciar, which Hugh de Lacy "
            "seized and his son Walter de Lacy now holds. Every English "
            "lord there has been troubled by the hill's old magic. "
            "Nuadha of the silver arm still sleeps beneath it. The book "
            "gives no aura; Faerie 3 at the mound and 5 in the regio are "
            "this pack's.",
            "Nuadha's wife is Bóinn, the river goddess, who often goes as a "
            "shining white cow (see the Bestiary). Long ago she came to "
            "the spring and it burst out in a flood that became the River "
            "Boyne. The two quarrel; she bore Aonghus to the Daghda, which "
            "explains Aonghus's taste for tragic love that ends in strife "
            "and Nuadha's open dislike of him. Nuadha stands for the kings "
            "of Leinster; Bóinn would rather see him ruled than ruling, "
            "and favours tales of power flowing into Meath, as her river "
            "does. Both like to draw mortals into acting out the old "
            "stories.",
            "Vis: the Well of Wisdom (Imaginem), in the regio.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "achad_ur",
        "The Pass of Achad-ur",
        inside=p["ossory"],
        summary=(
            "The pass through the hills from Ossory into Munster, where in "
            "1169 Diarmait mac Murchadha and his English allies broke the "
            "Osraighe of Mac Giolla Phádraig with a Norman cavalry charge, "
            "took the pass and then fell back to Ferns. It is still a main "
            "road, and bandits plague it."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "dunamase",
        "The Rock of Dunamase",
        inside=p["ossory"],
        summary=(
            "A rocky outcrop fortified since old times. Meiler FitzHenry "
            "saw its worth and built a castle; through Aoife's marriage it "
            "passed to Strongbow, who gave it to William Marshal. Marshal "
            "raised a strong castle, which his son William now holds."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "kilree",
        "Kilree Tower",
        inside=p["ossory"],
        aura=4,
        summary=(
            "A woodland clearing a few miles from Kells with an old "
            "graveyard, deeply peaceful, with a Magic aura of 4 and "
            "perhaps other secrets. Its round tower stands eighty feet, "
            "roofless, with a window to each quarter; the High-King Niall "
            "mac Áeda is said to lie here. The Priory of St. Mary at Kells "
            "owns it and leaves it to sleep; a new covenant could be "
            "founded among the dead here if the prior agreed."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "little_saltee",
        "Little Saltee",
        inside=p["wexford_county"],
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The smaller of the two Saltee islands, five miles off the "
            "Wexford coast, empty but for the Paruchia of Nerius: the "
            "hermits' beehive cells, a small chapel, a cave system that "
            "holds their laboratories, a tall library tower, and a little "
            "graveyard of earlier hermits. It has no Magic aura; its aura "
            "is Divine 3.",
            "The tides are dangerous and the rocky shore has no good "
            "landing. By custom no woman, maga or not, may come ashore.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "great_saltee",
        "Great Saltee",
        inside=p["wexford_county"],
        summary=(
            "The larger Saltee, home to twenty-eight people (two farming "
            "families and three fisher brothers, with wives and children) "
            "and the parish church of St. Mary. They serve the hermits of "
            "Little Saltee as covenfolk but never set foot there. A small "
            "clifftop shrine keeps the Paruchia's cathach, the arm of "
            "Saint Nerius, and the islanders watch over it. The book gives "
            "no aura beyond the church's."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "gleann_molura",
        "Gleann Molúra",
        inside=p["wicklow"],
        aura=2,
        summary=(
            "A narrow dead-end glen in the Wicklow Mountains, seven miles "
            "long and under half a mile wide, between walls some 2000 feet "
            "high. One road runs in, and it ends at Lámbaird. The glen has "
            "a Magic aura of 2, rising to 4 where the covenant stands, and "
            "is home to what is left of the Uí Broin."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "ashenrise_castle",
        "Ashenrise Castle",
        inside=p["carlow"],
        aura=1,
        summary=(
            "A square English castle north of New Ross, some miles from "
            "the Barrow on its eastern side, with a square tower at each corner; its "
            "grounds hold a Magic aura of 1. Ralph fitz Stephen holds it, "
            "and the magi of Ashenrise live in three of its towers as his "
            "guests, two to a tower; the fourth is for the household. The "
            "courtyard has wooden barns, storehouses and stables. Half a "
            "mile west of it stands Rhiannon's corpse, facing Connacht and "
            "Munster."
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------- the lords


def _lords(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["leinster_liberty"] = b.lord(
        "The Liberty of Leinster",
        title="count",
        wealth="Wealthy",
        seat="Ferns Castle",
        ruler="William Marshal the Younger, Earl of Pembroke",
        place=p["leinster"],
        summary=paragraphs(
            "Strongbow's inheritance, the old kingdom of Leinster, held as "
            "a Liberty under the Lord of Ireland: its lord gathers the "
            "king's revenues and does justice in his name, and his wool "
            "and grain help feed the English crown. It is held by William "
            "Marshal the Younger, second Earl of Pembroke and Marshal of "
            "England like his father, the great William Marshal, the most "
            "famous knight of the age, who died last year (the same man "
            "is regent for the young king; see that record). The ports of "
            "Dublin, Wexford and Wicklow were kept back by Henry II under "
            "his own hand.",
            "William is a widower since 1215, bringing up his six-year-old "
            "daughter quietly in Ireland; his short spell as a rebel in "
            "the barons' revolt in England has been forgiven. At Ferns he "
            "is building a square stone keep with a round tower at each "
            "corner, far ahead of any castle in England, Wales or Ireland. "
            "He also holds the Rock of Dunamase, and his father built "
            "Kilkenny and New Ross.",
            "The curse. When he would not give back two manors his father "
            "had wrongly taken from the see, the Bishop of Ferns cursed "
            "the Marshal line to die out. The Pope has patched the quarrel "
            "up, but William keeps the manors, has no heir, and will not "
            "marry again until the curse is lifted; he swore to his father "
            "to keep the Irish lands whole.",
        ),
    )
    w["theobald_butler"] = b.lord(
        "Theobald Butler",
        title="baron",
        wealth="Wealthy",
        seat="Arklow Castle",
        ruler="Theobald Butler, Butler of Ireland",
        place=p["wicklow"],
        summary=(
            "Butler of Ireland, nineteen years old, holding Arklow, whose "
            "castle guards the harbour. His office gives him the right to "
            "hand the King of England a cup of wine at the coronation, and "
            "to take two barrels from every ship that lands wine at an "
            "Irish port, so his agents are busy in every harbour; at New "
            "Ross they enforce the right strictly."
        ),
    )
    w["prendergast"] = b.lord(
        "Sir Gerald de Prendergast",
        title="landed",
        seat="Enniscorthy",
        ruler="Sir Gerald de Prendergast",
        answers_to=w["leinster_liberty"],
        place=p["wexford_county"],
        summary=(
            "A young English knight of the chivalrous kind, holding the "
            "fortified manor of Enniscorthy, who dreams of raising a great "
            "castle there to match William Marshal the Younger's. Brave "
            "and romantic, he is well liked by the Irish round about as "
            "well as by the settlers."
        ),
    )
    w["fitz_maurice"] = b.lord(
        "William fitz Maurice fitz Gerald",
        title="baron",
        seat="Naas Castle",
        ruler="William fitz Maurice fitz Gerald",
        answers_to=w["leinster_liberty"],
        place=p["wicklow"],
        summary=(
            "Son of Maurice fitz Gerald, Strongbow's Norman ally, who built "
            "the Black Castle on its headland over Wicklow harbour; he is "
            "married to Strongbow's daughter Aoife. Naas Castle is his "
            "seat, but he rules from the port of Wicklow, a stronghold of "
            "English power that the hill clans often attack, and leaves "
            "Robert de Birmingham as castellan of Naas."
        ),
    )
    w["ralph_fitz_stephen"] = b.lord(
        "Ralph fitz Stephen",
        title="landed",
        seat="Ashenrise Castle",
        ruler="Ralph fitz Stephen",
        answers_to=w["leinster_liberty"],
        place=p["carlow"],
        summary=(
            "A second cousin of Raymond le Gros, given the castle now "
            "called Ashenrise for his part against the Uí Riain. He was "
            "captain of the grogs at Moles Magna in Normandy and brought "
            "its surviving magi here to his kinsmen; they live in his "
            "castle as permanent guests. He commands four knights and "
            "fifteen men-at-arms and is on good terms with the English "
            "lords nearby."
        ),
    )
    w["norragh"] = b.lord(
        "Peter de Norrach, Baron Norragh",
        title="baron",
        seat="Castle Norragh, Calverstown",
        ruler="Peter de Norrach",
        answers_to=w["leinster_liberty"],
        place=p["kildare_liberty"],
        summary=(
            "A descendant of Robert de St. Michael, a companion of "
            "Strongbow, holding Castle Norragh at Calverstown (Baile an "
            "Chalbhaigh). The Augustinian abbey of Kilrush, founded by "
            "William Marshal, is close by."
        ),
    )
    w["baron_of_kells"] = b.lord(
        "William fitz Robert, Baron of Kells",
        title="baron",
        seat="Kilkenny Castle",
        ruler="William fitz Robert",
        answers_to=w["leinster_liberty"],
        place=p["ossory"],
        summary=(
            "Son of Geoffrey fitz Robert, whom William Marshal made "
            "seneschal at Kilkenny and who styled himself Baron of Kells; "
            "Marshal later came to distrust Geoffrey and held him hostage "
            "at Hereford, where he died in 1211. William succeeded him and "
            "holds Kilkenny's castle today."
        ),
    )
    w["fitz_anthony"] = b.lord(
        "Thomas fitz Anthony",
        title="landed",
        seat="Grennan Castle",
        ruler="Thomas fitz Anthony",
        answers_to=w["leinster_liberty"],
        place=p["ossory"],
        summary=(
            "A Welsh lord who served Strongbow and founded Thomastown, half "
            "a mile north of the Irish settlement of Grianán, the sunny "
            "place. He lives there contentedly among many Welsh-speaking "
            "retainers and settlers, has walled the town against Osraighe "
            "raids, and built Grennan Castle as his home."
        ),
    )
    # The Gaelic lords and clans.
    w["fitz_patrick"] = b.lord(
        "Mac Giolla Phádraig (fitz Patrick) of Ossory",
        title="landed",
        ruler="Mac Giolla Phádraig",
        place=p["ossory"],
        summary=(
            "The old royal house of Ossory, the sons of Patrick, named for "
            "a great king of the Osraighe. They have largely accepted "
            "English rule and taken the name fitz Patrick, and as subjects "
            "of the English crown they keep much influence and power in "
            "the region. Many of their people remain hostile to the "
            "English. Irish."
        ),
    )
    w["fitz_dermot"] = b.lord(
        "Mac Gilla Mo-Cholmóg (fitzDermot)",
        title="landed",
        ruler="Mac Gilla Mo-Cholmóg",
        place=p["kildare_liberty"],
        summary=(
            "King of the Uí Dúnchada, one of the three families of the Uí "
            "Dúnlainge, ruling the land nearest Dublin. He came to terms "
            "with the invaders at once, allied with them and took the name "
            "fitzDermot. Irish."
        ),
    )
    w["ua_tuathal"] = b.lord(
        "The Ua Túathal",
        title="landed",
        ruler="the king of the Ua Túathal (the book does not name him)",
        place=p["wicklow"],
        summary=paragraphs(
            "A family of the Uí Dúnlainge, the O'Tooles to the English, "
            "who lead the alliance of hill clans resisting the English "
            "from the Wicklow Mountains; they owe and pay the English no "
            "tribute. Each of the three families proclaims its own king "
            "and tries to rule the others. Saint Laurence O'Toole, "
            "archbishop and peacemaker, was of this clan.",
            "With the Ua Broin they massacred three hundred of Dublin's "
            "newcomers on Black Monday, Easter Monday 1209. They are now "
            "hunted men and seldom come near Dublin, but they harass Naas, "
            "Wicklow and every road through the hills.",
        ),
    )
    w["ua_broin"] = b.lord(
        "The Ua Broin",
        title="landed",
        ruler="Cathasach Ua Broin",
        place=p["wicklow"],
        summary=paragraphs(
            "The O'Byrnes: a branch of the Uí Faelain, a royal line of "
            "Leinster, who lost their old lands round Cilldara to the "
            "Normans. What is left of them lives in Gleann Molúra beside "
            "Lámbaird, whose covenfolk they have been since its founding, "
            "and fights the English from the hills beside the Ua Túathal. "
            "They owe no tribute. Irish.",
            "Their chief, Cathasach Ua Broin, is young and green and leans "
            "on Dalton Ballaugh of Lámbaird; their seanchaidh Tadg Ua "
            "Broin keeps their traditions.",
        ),
    )
    w["ui_riain"] = b.lord(
        "The Uí Riain",
        title="landed",
        ruler="the chief of the Uí Riain (unnamed)",
        place=p["ossory"],
        summary=(
            "An Irish túath of Ossory, once vassals of Raymond le Gros, "
            "whose ancestral ráth held the grave of Rhiannon, a daughter "
            "of the clan and once Prima of House Merinita. Raymond drove "
            "them from their homes after rumours of a rising, and in the "
            "fighting her body was taken. They bear a long grudge against "
            "every English lord on the Barrow."
        ),
    )


# ---------------------------------------------------------------- towns


def _towns(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    liberty = w["leinster_liberty"]
    w["dublin"] = b.town(
        "Dublin",
        charter="Noble lord",
        ruler="the viceroy, Archbishop Henry de Londres",
        place=p["wicklow"],
        summary=paragraphs(
            "A Viking port on the Liffey, for centuries a great slave "
            "market where English and Welsh captives were sold, a trade "
            "that has ended under English rule. The Ostmen who once ruled "
            "it have moved across the river to Ostmantown since the "
            "invasion. The English, once besieged here, have replaced the "
            "Norse stockade and ditch with a strong stone wall. Henry II "
            "kept Dublin, Wexford and Wicklow under his own hand, out of "
            "Strongbow's reach.",
            "A great fire in 1190 burnt many houses and three churches, "
            "and many people left. A charter modelled on Bristol's "
            "brought settlers from Bristol and Wales to take their place: "
            "by 1220 a third of the citizens come of Bristol families, "
            "many of them merchants and craftsmen. Plague struck in 1208. "
            "On Easter Monday 1209 the Ua Broin and Ua Túathal fell on the "
            "newcomers at archery practice at the Hogges outside the "
            "walls, or gathering sticks in Cullen Woods, and killed three "
            "hundred; Black Monday is still kept with a militia march and "
            "the city on alert.",
            "Royal power here lies with the viceroy, Archbishop Henry de "
            "Londres, whom his tenants and many citizens hate. Dublin "
            "Castle, begun by King John's order in 1204, is unfinished: a "
            "square curtain wall about a courtyard, with no keep but great "
            "round towers at each corner, immensely strong. The city has "
            "two cathedrals, Christchurch and St. Patrick's.",
        ),
    )
    w["wexford"] = b.town(
        "Wexford",
        charter="Noble lord",
        place=p["wexford_county"],
        summary=paragraphs(
            "A walled port at the mouth of the Slaney, on the south side "
            "of its harbour, busy with ships for England and the "
            "continent, still Norse in character. Long ago the youth "
            "Garman Garbh stole a queen's crown and fled across the "
            "mudflats; a witch raised river and sea together, drowning "
            "him and casting the crown ashore. The flats are still "
            "dangerous, and some think her curse lingers. Saint Yvorus, "
            "who preached here before Patrick, drove out the rats: none "
            "comes ashore from a ship, and none can breed in the town.",
            "Diarmait mac Murchadha and Robert FitzStephen besieged it in "
            "1169, the first blow of the conquest, until the Bishop of "
            "Ferns persuaded the town to let them in. It has taken English "
            "rule quietly since, with much intermarriage. Henry II, "
            "sailing from here for France in 1172, gave its milling rights "
            "to the Templars, who keep a small garrison.",
        ),
    )
    w["bannow"] = b.town(
        "Bannow",
        charter="Noble lord",
        answers_to=liberty,
        place=p["wexford_county"],
        summary=(
            "A thriving port on a fine natural harbour where Strongbow's "
            "English first came ashore, camping in an old ráth on the "
            "headland before they marched on Wexford. Lately the bay has "
            "been silting up faster than anyone remembers, and the bigger "
            "ships must unload elsewhere."
        ),
    )
    w["new_ross"] = b.town(
        "New Ross",
        charter="Noble lord",
        answers_to=liberty,
        place=p["wexford_county"],
        summary=(
            "An English town beside the old monastic ráth of Saint Abbán's "
            "monastery, in the old kingdom of Ossory. Chartered by the "
            "king in 1207, it was made a great port by William Marshal, "
            "who built a stone bridge over the river. It is as famous for "
            "pirates as for merchants, Irish raids have people talking of "
            "a town wall, and Theobald Butler's agents watch the wine "
            "ships closely. A frontier town, lawless whenever the younger "
            "Marshal's men look away."
        ),
    )
    w["ferns_town"] = b.town(
        "Ferns Castle and town",
        charter="Noble lord",
        ruler="William Marshal the Younger",
        answers_to=liberty,
        place=p["ferns"],
        summary=(
            "The small town at the heart of Ferns, with William Marshal the "
            "Younger's new castle rising in its centre, the most advanced "
            "in these islands. He lives here with his young daughter."
        ),
    )
    w["wicklow_town"] = b.town(
        "Wicklow",
        charter="Noble lord",
        ruler="William fitz Maurice fitz Gerald",
        answers_to=w["fitz_maurice"],
        place=p["wicklow"],
        summary=(
            "Cill Mhantáin to the Irish, the church of the toothless one: "
            "a Viking port that still feels Norse, overlooked by the Black "
            "Castle on its rocky headland. A seat of English power, it is "
            "heavily garrisoned against the Ua Broin and Ua Túathal, who "
            "often strike at town and castle from the hills."
        ),
    )
    w["arklow"] = b.town(
        "Arklow",
        charter="Noble lord",
        ruler="Theobald Butler",
        answers_to=w["theobald_butler"],
        place=p["wicklow"],
        summary=(
            "A harbour town guarded by Theobald Butler's castle; the "
            "Uí Enechglaiss, driven out of Meath in the fifth century, "
            "still live round about. The tide rock lies offshore."
        ),
    )
    w["kildare_town"] = b.town(
        "Kildare",
        charter="Noble lord",
        place=p["kildare_liberty"],
        summary=(
            "Cill Dara, one of the largest ráths in the region, a "
            "flourishing market centre where Saint Brigid founded a double "
            "house of monks and nuns late in the fifth century. It was the "
            "seat of the Uí Dúnlainge, the royal line of northern Leinster; "
            "they have not reached for a crown in two centuries, but their "
            "three families, the Ua Broin, the Ua Túathal and the Uí "
            "Dúnchada, still hold the region and scheme against each other. "
            "Saint Brigid's sacred fire still burns here."
        ),
    )
    w["naas"] = b.town(
        "Naas",
        charter="Noble lord",
        ruler="William fitz Maurice fitz Gerald (castellan Robert de Birmingham)",
        answers_to=w["fitz_maurice"],
        place=p["kildare_liberty"],
        summary=paragraphs(
            "Nás na Ríogh, where kings once met: a small town growing "
            "fast as English settlers arrive. They have rededicated Saint "
            "Patrick's church to Saint David, and the Knights Hospitaller "
            "run it. The kings of Leinster were once made here in sacred "
            "rites on the great earthwork called the dún of Naas; holding "
            "Naas is thought to carry some right to rule the kingdom, but "
            "the rites may be forgotten. Saint Fechin's Cross stands in "
            "the market.",
            "It lies on the border of the Ua Broin and Ua Túathal, who "
            "once fought each other here and now raid the town together, "
            "so King John, who called the nobles here to submit in 1206, "
            "had a strong castle built.",
            "The Boroimhe. King Eochaid Aincheaun of Leinster married "
            "Darina, daughter of the High-King Túathal Techtmar, then "
            "craved her sister Fithir: he shut Darina up in his hall here, "
            "told her father she had died, and wed Fithir. Darina broke "
            "out during the feast, Fithir dropped dead at the sight of "
            "her, and Túathal came for vengeance, beheaded Eochaid and "
            "burnt Naas. Leinster then owed Tara a tribute every second "
            "year of 15,000 each of cows, pigs, linen cloths, silver "
            "chains, goats and copper cauldrons, a vast cauldron, and 30 "
            "red-eared white cows. Brian Bóramha revived it; a clever "
            "priest later had a King of Meath give it up for ever.",
        ),
    )
    w["kilkenny"] = b.town(
        "Kilkenny",
        charter="Noble lord",
        ruler="William fitz Robert, Baron of Kells",
        answers_to=w["baron_of_kells"],
        place=p["ossory"],
        summary=paragraphs(
            "Cill Chainnigh, an old monastic community by a ford of the "
            "Nore with a church of Saint Canice. William Marshal built a "
            "great four-towered castle here in 1195, walled and ditched, "
            "to hold down the Osraighe, married "
            "Strongbow's daughter Isabel de Clare here, and walled the "
            "town; it was chartered in 1207 and has thrived.",
            "It has two hearts: Irishtown about the monastery, outside the "
            "walls, and the English Hightown within them. Irishtown has "
            "the great stone cathedral of Ossory, still being built and "
            "dogged by accidents. The fitz Patricks keep much influence in "
            "the district.",
        ),
    )
    w["kells_leinster"] = b.town(
        "Kells (Ossory)",
        charter="Noble lord",
        answers_to=w["baron_of_kells"],
        place=p["ossory"],
        summary=(
            "A small walled town, not the Kells in Meath, called the city "
            "of the seven castles for the seven towers the English built "
            "to guard the Augustinian Priory of St. Mary. It has grown "
            "prosperous under English rule, but Osraighe clans still "
            "attack it. Kilree Tower is a few miles off."
        ),
    )
    w["thomastown"] = b.town(
        "Thomastown (Grianán)",
        charter="Noble lord",
        ruler="Thomas fitz Anthony",
        answers_to=w["fitz_anthony"],
        place=p["ossory"],
        summary=(
            "Thomas fitz Anthony's walled town, beside the Irish village of "
            "Grianán, full of Welsh speakers; Grennan Castle is his home. "
            "Jerpoint Abbey is near."
        ),
    )


# -------------------------------------------------------------- churches


def _churches(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["bishop_ferns"] = b.church(
        "Bishopric of Ferns",
        church="Bishop's cathedral",
        order="Cistercian",
        ruler="Bishop Ua Maíl Mhuaidh",
        place=p["ferns"],
        summary=(
            "Irish. Its elderly bishop, the Cistercian Ua Maíl Mhuaidh, is "
            "Irish-born yet a favourite of the English crown and of Rome, "
            "though he once preached that Irish clergy only took to sins "
            "of the flesh after English and Welsh priests showed them how. "
            "He is famed for holiness and justice. He cursed the Marshal "
            "line to die out when William the Younger would not return two "
            "manors his father had seized; the Pope has made them "
            "reconcile, but the manors are still held. The first bishop "
            "was Saint Yvorus, who came before Patrick and drove the rats "
            "out of Ferns and Wexford."
        ),
    )
    w["ferns_abbey"] = b.church(
        "St. Mary's Abbey, Ferns",
        church="Monastery or nunnery",
        order="Augustinian",
        place=p["ferns"],
        summary=(
            "Irish. An Augustinian house founded by Diarmait mac Murchadha "
            "where Saint Máedóc of Ferns's monastery once stood; a centre "
            "of the reforming party."
        ),
    )
    w["baltinglass_abbey"] = b.church(
        "Baltinglass Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        place=p["baltinglass"],
        founded=1148,
        summary=(
            "Irish. The Valley of Salvation, a Cistercian house founded by "
            "Diarmait mac Murchadha in 1148 with monks from Mellifont: 38 "
            "monks and 50 lay brothers. It is caught up in the Conspiracy "
            "of Mellifont, officially backing its mother house against the "
            "Cistercian Order; the abbot is all for Mellifont's defiance, "
            "but his monks are loyal to Cîteaux. The monks are mostly keen "
            "to march up the hill one Christmas Day and set a great "
            "wooden cross on the faerie mound; so far the abbot urges "
            "caution."
        ),
    )
    w["glendalough_monastery"] = b.church(
        "The Monastery of Glendalough",
        church="Monastery or nunnery",
        order="Irish monastic",
        place=p["glendalough"],
        summary=(
            "Irish. Saint Kevin's monastery, a sanctuary within its round "
            "wall, whose hermits resist the English churchmen. It was the "
            "seat of a diocese until 1214, when the English joined it to "
            "Dublin's. Its monks gather and share out the Fruit of Saint "
            "Kevin. Indrechtach of the Paruchia was a monk here until his "
            "Gift drove him out."
        ),
    )
    w["christchurch"] = b.church(
        "Christchurch Cathedral, Dublin",
        church="Archbishop's cathedral",
        order="Augustinian",
        place=p["wicklow"],
        summary=(
            "Anglo-Irish. The Norse cathedral King Sitric built in the "
            "eleventh century, which looked to Canterbury, not Armagh. In "
            "1168 the saintly archbishop Lorcán Ua Túathal (Saint Laurence "
            "O'Toole), a great peacemaker between English and Irish, made "
            "it an Augustinian priory; it holds his shrine, though he died "
            "and lies buried in Normandy, and a chapel Strongbow gave to "
            "the English Saint Edmund. The Augustinians are rebuilding it "
            "in stone."
        ),
    )
    w["st_patricks_dublin"] = b.church(
        "St. Patrick's Cathedral, Dublin",
        church="Archbishop's cathedral",
        place=p["wicklow"],
        founded=1198,
        summary=(
            "Anglo-Irish. Dublin's second cathedral, begun in 1198 by the "
            "English archbishop John Comyns, Lorcán's successor, and "
            "served by thirteen canons. Henry de Londres carries on the "
            "building and has let the canons elect a dean."
        ),
    )
    w["brigids_fire"] = b.church(
        "The Sacred Fire of Saint Brigid, Kildare",
        church="Monastery or nunnery",
        order="Irish monastic",
        place=p["kildare_liberty"],
        summary=paragraphs(
            "Irish. Saint Brigid's abbey at Kildare was ruled by an abbess, "
            "the comarba Naomh Bríd, head of one of the mightiest paruchiae "
            "and the only one led by a woman. Diarmait mac Murchadha threw "
            "out the abbess in 1132 for his own niece; the reformers made "
            "the abbess answer to the bishop at the Synod of Kells in 1152; "
            "and when the niece died in 1171 the English shut the abbey.",
            "A few stayed to tend the fire Brigid lit herself, which has "
            "never gone out, even without fuel. It burns outside the "
            "church inside a hedge of sharp thorns that only the nineteen "
            "nuns of its vigil can pass unharmed; one keeps watch each "
            "night, and any man who forces his way in is said to fall "
            "under a divine curse. Archbishop Henry de Londres has sworn "
            "in 1220 to put it out, to prove it superstition, and also "
            "because Naomh Bríd is the patroness of the restless Uí "
            "Dúnlainge.",
        ),
    )
    w["kilrush"] = b.church(
        "Kilrush Abbey",
        church="Monastery or nunnery",
        order="Augustinian",
        place=p["kildare_liberty"],
        summary=(
            "Anglo-Irish. An Augustinian abbey near Calverstown, founded "
            "by William Marshal."
        ),
    )
    w["bishop_ossory"] = b.church(
        "Bishopric of Ossory",
        church="Bishop's cathedral",
        place=p["ossory"],
        summary=(
            "Irish in its origins. In 1202 Bishop Felix O'Dulany moved the "
            "see to Kilkenny and began a great stone cathedral of Saint "
            "Canice in Irishtown; he died the same year, but the work goes "
            "on, plagued by accidents. The book does not name the bishop "
            "of 1220."
        ),
    )
    w["kells_priory"] = b.church(
        "The Priory of St. Mary, Kells",
        church="Monastery or nunnery",
        order="Augustinian",
        place=p["ossory"],
        founded=1193,
        summary=(
            "Anglo-Irish. An Augustinian priory founded in 1193 by "
            "Geoffrey fitz Robert, guarded by the seven towers of Kells. "
            "It owns Kilree Tower and lets it lie undisturbed."
        ),
    )
    w["jerpoint"] = b.church(
        "Jerpoint Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        place=p["ossory"],
        founded=1180,
        summary=paragraphs(
            "Irish. The Cistercian abbey of St. Nicholas, which Donogh "
            "O'Donoghoe, an Osraighe king, founded in 1180; his line "
            "backed the Irish reformers. Before it stood a Benedictine "
            "house that failed, founded in 1160 by King Domnall Mac Giolla "
            "Phádraig to keep the relics of Saint Nicholas, which Nicholas "
            "de Frainet, one of seven knights home from crusade, had "
            "brought. The abbey has joined the revolt against the "
            "Cistercian Order.",
            "The grave of Saint Nicholas lies in a ruined church inside the "
            "grounds: the ancient bishop of Asia Minor who raised three "
            "murdered children from a pickling barrel, honoured with a "
            "mass each Christmas.",
        ),
    )
    w["great_saltee_church"] = b.church(
        "St. Mary's Church, Great Saltee",
        church="Parish church",
        ruler="Father Diarmaid",
        place=p["great_saltee"],
        summary=(
            "Irish. The parish church of Great Saltee, where the hermits "
            "of the Paruchia cross every Sunday for mass. Its priest, "
            "Father Diarmaid, is a firm friend of the covenant and guards "
            "his lonely parish; some old fault got him sent here."
        ),
    )


# -------------------------------------------------------------- Ashenrise


def _ashenrise(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    place = hibernia.places["ashenrise_castle"]
    summary = paragraphs(
        "A covenant of continental magi, refugees of Moles Magna, the "
        "fallen covenant of the Normandy Tribunal, who mean to rise from "
        "its ashes to a leading place in Hibernia and to drag its "
        "Peripheral Code, which they think barbarous, into the thirteenth "
        "century. They live as guests in an English castle in the Liberty "
        "of Carlow. Its device is a scroll crossed with a sword. Its "
        "cathach is the corpse of Rhiannon Uí Riain, once Prima of House "
        "Merinita, enchanted to dance. It leans to the English Council: "
        "Helles leads the reform debate at every Tribunal, so far with "
        "little to show for it. It is at odds with most covenants, "
        "Lámbaird and Cliffheart above all.",
    )
    what_matters = _lines(
        "Vis: the raw vis grown in Rhiannon's bones, left in them on purpose (the cathach itself)",
        "Income: the hospitality of Ralph fitz Stephen, whose castle it is",
        "Library: unnamed; Helles's glosses of Hermetic law and the books the magi brought from Normandy and Stonehenge",
        "Boon: Courtyard Castle (a square castle with four corner towers)",
        "Boon: Local Ally (Ralph fitz Stephen, four knights and fifteen men-at-arms)",
        "Hook: Hermetic Politics (reform motions, and high crimes charged against its magi at every Tribunal)",
        "Hook: Rival (Lámbaird and Cliffheart, who press it with Wizard Wars and cathach raids)",
        "Hook: Infamous (a dead Prima's corpse made a dancing trophy)",
        "Tension: the Uí Riain and the Déise túatha resent every English lord on the Barrow",
    )
    notes = paragraphs(
        "History. Helles and Pollices fled to Ireland after Moles Magna "
        "fell, having heard that the Angevins had settled it; they found "
        "it scarcely settled and its old customs alive, and took up "
        "reforming its law as a worthy challenge. For their cathach they "
        "chose Rhiannon, who had been buried among her Uí Riain kin in "
        "Ossory rather than at Qui Sonant. They attacked the chieftain's "
        "ráth during the fighting between Raymond le Gros and the Uí "
        "Riain and carried her remains away. Joined by three sodales from "
        "Stonehenge, they showed the corpse at the Tribunal of 1186 and "
        "declared their covenant. The hall was in uproar and Wizard War "
        "was declared on them; some said a corpse was no magical "
        "treasure, but the Praeco Conán Derg ruled that the raw vis "
        "grown in the bones made it a fit cathach. They held it for the "
        "year, hard as it was, and were recognized in 1187.",
        "The cathach. Rhiannon had a Christian burial, so her ghost lies "
        "beyond Hermetic magic. The magi have enchanted the body against "
        "rot and to caper and dance at a word, and left the raw vis in "
        "its bones untouched. It stands half a mile west of the "
        "covenant's western tower, outside the Aegis, looking toward "
        "Connacht and Munster.",
        "Culture. The magi try to live as civilized continental magi: "
        "each pursues his own speciality, debate is lively, and they "
        "hunt, hawk and give lavish feasts with song and dance. Their "
        "neighbours harry them with Wizard Wars and raids on the "
        "cathach; they guard Rhiannon doggedly and usually wage their "
        "wars passively, keeping out of the aggressor's way. They keep "
        "the Hibernian Code to the letter until they can change it, and "
        "have sworn no oaths and broken no law, but they raid no "
        "cathaigh and send no apprentice on the macgnímartha, and they "
        "want both customs gone.",
        "Covenfolk. Beyond the sanctums it is an ordinary English castle "
        "of the colony, served by a few imported settlers. The magi deal "
        "openly with mundanes, though most must work through agents "
        "because of the Gift.",
        "Magi. Helles, Pollices and Dyfrgi, a Welsh Bjornaer with a wolf "
        "heartbeast, remain of the founders; Tug, Dorján and Konstanczia "
        "came later from the Stonehenge Tribunal. Tug, the only one the "
        "covenant would take in, may be the man to open talks with "
        "Cliffheart, if Ashenrise ever wants peace.",
        "Founded 1186, at the Tribunal where the cathach was shown; "
        "recognized 1187 after the year's defence. Season: Spring.",
    )
    hidden = _lines(
        "The Uí Riain rising was the magi's invention: they used minstrels to convince Raymond le Gros that his vassals meant to rebel, and his campaign gave them their chance at the grave.",
        "Dorján and Konstanczia's sigils are held by magi in Transylvania, who direct them to help Ashenrise modernise the Tribunal.",
        "Tug's sodales doubt his saint: he met Patrick in the Schwarzwald, a forest full of mischievous faeries, and it may have been a faerie that converted him. Tug admits he met many faeries there but swears it was the saint.",
    )
    ashenrise = b.covenant(
        "Ashenrise",
        tribunal=tribunal,
        founded=1186,
        place=place,
        aura=1,
        realm="Magic",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Spring",
    )
    hibernia.covenants["ashenrise"] = ashenrise
    hibernia.cathaigh["ashenrise"] = {
        "cathach": "the enchanted dancing corpse of Rhiannon, once Prima of House Merinita"
    }
    b.book(
        ashenrise,
        "The library of Ashenrise",
        "Other",
        description=(
            "No books are named. Helles spends his days studying and "
            "glossing Hermetic law against the charges brought at each "
            "Tribunal, and the magi brought their texts from Normandy and "
            "Stonehenge; Pollices keeps notes and samples from every "
            "plague site in Ireland."
        ),
    )
    m = hibernia.magi
    m["helles"] = b.magus(
        "Helles",
        covenant=ashenrise,
        house=TYTALUS,
        age=78,
        summary=paragraphs(
            "Founder and leader of Ashenrise, looking thirty-seven. Born in "
            "Champagne and trained in the Normandy Tribunal, he joined "
            "Moles Magna because a covenant inside a dam seemed a good "
            "place to hide from the world; when the dam burst and swept it "
            "away, he chose to hide in plain sight instead, and his grog "
            "captain Ralph fitz Stephen brought him to his kin in Ireland.",
            "A master of disputation in both the schoolmen's manner and "
            "his House's, he sees rewriting Hibernia's Peripheral Code as "
            "the greatest challenge there is. He studies and glosses "
            "Hermetic law daily to answer the high crimes charged against "
            "him and his sodales at every meeting.",
        ),
        traits={"Diplomatic": 3, "Clever": 2},
    )
    m["pollices"] = b.magus(
        "Pollices",
        covenant=ashenrise,
        house=JERBITON,
        age=69,
        summary=paragraphs(
            "'Thumbs', a founder of Ashenrise, looking forty-two: tall, "
            "hawk-like and dressed in black, a Sicilian with four thumbs, "
            "two where his little fingers should be, from an accident in "
            "his apprenticeship. No lover of beauty, he studies deformity "
            "and deadly plague, and has visited every place in Ireland "
            "where plague killed a crowd, gathering samples of something "
            "few can name. Irish magi find him grim and frightening.",
            "Among mundanes he is another man: his Gentle Gift lets him "
            "pass as a gloved scholar and physician of many languages, "
            "charming and pleasant, a welcome guest at the neighbouring "
            "lords' courts and much loved by the English settlers.",
        ),
        traits={"Vindictive": 3, "Easily Angered": 2},
    )
    m["dyfrgi"] = b.magus(
        "Dyfrgi",
        covenant=ashenrise,
        house=BJORNAER,
        age=None,
        summary=(
            "A Welsh magus of House Bjornaer with a wolf heartbeast, one "
            "of the three founders of Ashenrise who remain. The book says "
            "no more of him."
        ),
    )
    m["tug"] = b.magus(
        "Tug",
        covenant=ashenrise,
        house=CRIAMON,
        age=45,
        summary=(
            "Once Decamentus, a faithful follower of his House's ways, he "
            "met Saint Patrick in a long Temporary Twilight, and the saint "
            "blessed the coarse blanket he had wrapped himself in against "
            "the cold. He chose a new life at once, came to Hibernia and "
            "renamed himself Tug, which is a shawl in Irish slang. No "
            "covenant but Ashenrise would take him. Looks thirty-eight."
        ),
        traits={"Cheerful": 3, "Absent-Minded": 2},
    )
    m["dorjan"] = b.magus(
        "Dorján",
        covenant=ashenrise,
        house=TREMERE,
        age=59,
        summary=(
            "Born and trained in the Transylvanian Tribunal and sent on to "
            "Stonehenge, he and Konstanczia asked leave to join the new "
            "Hibernian covenant and came too late to help defend its "
            "cathach. Handsome and charming, he would be Leinster's most "
            "eligible bachelor but for his Gift. Always the defender, he "
            "has fought half a dozen Wizard Wars in Hibernia and killed "
            "four magi. Looks forty-three."
        ),
        traits={"Adventurous": 3, "Dashing": 2},
    )
    m["konstanczia"] = b.magus(
        "Konstanczia",
        covenant=ashenrise,
        house=TREMERE,
        age=65,
        summary=(
            "Dorján's elder and wiser companion from Transylvania by way "
            "of Stonehenge. She keeps her mind on Tribunal business and "
            "watches the known troublemakers. She too has fought half a "
            "dozen Wizard Wars as the defender, and has killed five magi. "
            "Looks forty-five."
        ),
        traits={"Adventurous": 3, "Dashing": 2},
    )
    b.link(
        m["dorjan"],
        "characters",
        m["konstanczia"],
        "Sodalis of House Tremere; came with him from Stonehenge",
    )
    b.link(
        m["helles"],
        "characters",
        m["pollices"],
        "Fellow founder; fled Moles Magna with him",
    )


# ---------------------------------------------------------------- Lámbaird


def _lambaird(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    place = hibernia.places["gleann_molura"]
    summary = paragraphs(
        "The arm of a bard (LAWM-beard), called Lombard by foreigners: an "
        "old covenant of House Flambeau, founded in 826 by Petrifer and "
        "the druid Raghallach, and home ever since to the School of "
        "Raghallach, a school of magical combat. Born when a Hermetic "
        "magus sheltered a native magician, it has always cast itself as "
        "guardian of the old ways, and has lately taken up the defence of "
        "the Irish against the Normans. Its device is a severed human arm, "
        "and its cathach the silver arm of the bard Cairpre. It is of the "
        "Ordo Hiberniae, and the fiercest political foe of any covenant "
        "it thinks is pursuing an English agenda; the English Council "
        "worries more about it every meeting. So far it has escaped real "
        "sanction by saying it only defends itself and its resources, "
        "but many suspect it of raiding the Normans.",
    )
    what_matters = _lines(
        "Income: horses, hounds and hawks bred and trained for Irish nobles and magi, including lines unaffected by the Gift and wolfhounds with Magic Sensitivity that smell out vis",
        "Library: none; texts stay with whoever used them last",
        "Boon: Veteran Fighters (the largest turb in the Tribunal, young Uí Broin warriors)",
        "Boon: Loyal Covenfolk (the Uí Broin, who have lived among its magi since it was founded)",
        "Boon: Secondary Income (the breeding of beasts)",
        "Boon: Difficult Access (a blind glen with a single road)",
        "Hook: School (the School of Raghallach, and its long-term visitors)",
        "Hook: Wooden (a palisade and a timber lodge)",
        "Hook: Hermetic Politics (reprimanded in 1193; the English Council's concern)",
        "Hook: Dark Secret (its part in the hill clans' war on the English)",
        "Tension: Dalton against Éinri of Vigil, a long feud of certamen and grog brawls",
        "Tension: Wizard War on any magus who undercuts its monopoly of bred beasts",
    )
    notes = paragraphs(
        "History. While Diedne was purging Ireland's native magicians, "
        "the druid Raghallach fell in with Petrifer of House Flambeau, "
        "newly settled in Ireland, and they became friends until "
        "Raghallach learnt Petrifer was of the Order, which he believed "
        "had sanctioned the purge. He attacked in fury; Petrifer barely "
        "survived behind his Parma, admired the druid's savage magic, "
        "and once Raghallach was subdued offered him a place in the "
        "Order. Reconciled, the two made a camp in the Wicklow Mountains "
        "and sheltered any of Raghallach's tradition. Diedne would not "
        "accept druids as Flambeau; when the Tribunal would not hear her, "
        "she made Wizard War on them, and only Raghallach and two others "
        "lived to found a true cell in the House. The camp became "
        "Lámbaird, and his druidic practice became a school of war.",
        "Lámbaird kept a deep hatred of Diedne and threw itself into the "
        "Schism War in Hibernia and the Tribunals round it. The school "
        "boomed as Flambeau magi flocked to the hills to study and to "
        "hunt Diedne, and foreigners turned the name into Lombard. At "
        "Clontarf in 1014 its magi, warned by Brian Bóramha's druid that "
        "sons of Diedne marched with his army, found the last Diedne of "
        "Hibernia on the field and destroyed them.",
        "The cathach. A hollow false arm of silver made by a magical "
        "smith for the bard Cairpre, which served him as a living arm. In "
        "the year the covenant sought recognition, one of its magi, "
        "stung by Cairpre's satire, broke the ancient ban on harming "
        "bards and killed him; Petrifer, his own pater, slew him in "
        "Wizard War for it, and his name has been struck from the "
        "records. A covenfolk bearer wears the arm over his own left arm, "
        "a great honour: his own arm is useless inside it, for the silver "
        "moves by its own will, the murdered bard's spirit, people say. "
        "The bearer may not stray from the covenant nor live within the "
        "Aegis.",
        "The covenant. A palisade of stakes rings it; inside there is a "
        "din of hounds barking, weapons clashing on the training fields "
        "and magi bellowing orders. The magi's two wings flank a great "
        "wooden lodge, with stables, kennels and mews behind for its "
        "many horses, dogs and hawks. It looks little like a Hermetic "
        "covenant: there is no library, the laboratories are cluttered "
        "with makeshift apparatus hard to bring so deep into the hills, "
        "and the magi ignore each other's sancta (never an outsider's) "
        "and borrow equipment without asking.",
        "Culture. The magi live like the heads of a family, not scholars "
        "or lords; they hunt with hounds and hawks in the wooded hills, "
        "everyone eats together and does a share of the work, and the "
        "covenfolk grow up used to the Gift and speak their minds (a cook "
        "may well send a magus to the well). The magi still make the "
        "great decisions. Beasts sold are gelded, and buyers are told "
        "that by common law any offspring belong to Lámbaird anyway; "
        "sales pay for laboratory gear and the odd luxury, and the "
        "covenant feeds itself.",
        "The School of Raghallach teaches that no defence withstands a "
        "strong enough attack. Raghallach's tradition drew power from "
        "blood and self-inflicted pain, cnámh greamú or bone-biting, "
        "which also gave House Tremere a certamen style of that name; the "
        "druidic tradition is lost, but the school has become expert at "
        "beating supernatural foes and is often asked to carry out a "
        "Wizard's March. Its magi learn to assault and dispel an enemy's "
        "Magic Resistance head-on rather than slip round it, and usually "
        "have high Penetration (Life Boost or Puissant Penetration suit "
        "them). On a hunt they watch their prey closely, steal "
        "possessions or even dig through latrine pits for arcane "
        "connections, but prefer blood from their soldiers' weapons, and "
        "use a foe's name as a sympathetic connection: they listen for it "
        "or introduce themselves first, by baptismal name, hoping for an "
        "answer. Their spells include Retrieve the Bloodied Arrow, Revoke "
        "the Protection of Bonisagus, and Revoke the Protection of (Form) "
        "and of (Realm) (in the spell catalog), built on two new Perdo Vim "
        "guidelines: dispel a Form Resistance of level up to the spell's "
        "+10 + a stress die, or the Magic Resistance of one Realm's Might "
        "up to the spell's +20 + a stress die, in each case penetrating "
        "the target's Vim resistance. Hibernia forbids enchantments of "
        "Revoke the Protection of Bonisagus without limits on who may "
        "use them or how long they last.",
        "Magi and covenfolk. Three Flambeau magi live here, with "
        "apprentices of the two elders; there is room for more once the "
        "stores are cleared out of the spare rooms, but it seldom takes "
        "magi from outside, since nearly all were trained here. The "
        "covenfolk are Uí Broin: Cathasach Ua Broin, their young, untried "
        "chief, who defers to Dalton; and Tadg Ua Broin, their "
        "seanchaidh, schooled at the bardic school of Ceall Cluaine at "
        "Dalton's expense, who binds the clan with tradition and loyalty. "
        "Its young men train as warriors, every one eager to hunt the "
        "Normans who plundered their home.",
        "Founded 826. Season: Summer. Aura: Magic 2 in the glen, 4 at the covenant.",
    )
    hidden = _lines(
        "Lámbaird gives the mountain clans magical help now and then against the English in the Wicklow Mountains, which the Tribunal would surely judge interference with mundanes if it were known.",
        "So far it has left no witnesses and has not tied the Order to the raids, but its doings have been noticed: hence the reprimand of 1193.",
    )
    lambaird = b.covenant(
        "Lámbaird",
        tribunal=tribunal,
        founded=826,
        place=place,
        aura=4,
        realm="Magic",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Summer",
    )
    hibernia.covenants["lambaird"] = lambaird
    hibernia.cathaigh["lambaird"] = {
        "cathach": "the silver arm of the bard Cairpre, worn by a covenfolk bearer"
    }
    b.book(
        lambaird,
        "The texts of Lámbaird",
        "Other",
        description=(
            "Lámbaird keeps no library: each text stays with whichever "
            "magus used it last. Among them are the School of Raghallach's "
            "spells and its two Perdo Vim guidelines for dispelling Form "
            "and Realm resistance."
        ),
    )
    m = hibernia.magi
    m["dalton"] = b.magus(
        "Dalton Ballaugh",
        covenant=lambaird,
        house=FLAMBEAU,
        age=67,
        summary=paragraphs(
            "Dalton Ballaugh an Flámbó (DOLL-ton BOLL-odge), leader of "
            "Lámbaird, looking forty-three. His father was an Uí Broin, "
            "and the covenfolk still call him Mac ind Óc, the Young Son, "
            "though few of them are his elders. He and Brian were "
            "apprentices together and passed their Gauntlets together, and "
            "are close friends.",
            "A great hunter, which shows in his Intellego: he reads a site "
            "as well as any Quaesitor. His mastery of fire matches it, and "
            "he is a dangerous enemy, as Éinri mac Cillíni of Vigil has "
            "learnt; the two have feuded for years, short of Wizard War. "
            "His familiar is Lóegaire Liath, Grey Lóegaire, a grizzled "
            "hunting dog, sire of the covenant's line of magical hounds.",
        ),
        traits={"Proud": 3, "Relentless": 2, "Cautious": -2},
    )
    m["brian"] = b.magus(
        "Brian Chilldara",
        covenant=lambaird,
        house=FLAMBEAU,
        age=62,
        summary=paragraphs(
            "Brian of Cilldara an Flámbó, looking fifty-seven: small, thin "
            "and entirely hairless, a skinchanger who becomes a salmon and "
            "spends long spells in Wicklow's lakes and streams, studying "
            "the moods of the water he loves.",
            "His familiar, a salmon like his other shape, was caught and "
            "eaten by Norman soldiers. He has not got over it and may never "
            "bind another; until then he means to destroy every Norman on "
            "Irish soil.",
        ),
        traits={
            "Hatred of Normans": 3,
            "Changeable": 2,
            "Abstemious": 1,
            "Dependable": -1,
        },
    )
    m["cliodna"] = b.magus(
        "Cliodna inghean hIolair",
        covenant=lambaird,
        house=FLAMBEAU,
        age=43,
        summary=(
            "Cliodna an Flámbó (CLEE-na), the youngest at Lámbaird, "
            "looking thirty-five, who has made herself in the image of a "
            "warrior-queen of legend: as good with a sword as with a "
            "spell, a superb rider and athlete. She is called daughter of "
            "the Eagle since a clan of magical birds of prey in the "
            "mountains adopted her, and her familiar is Artt, a son of the "
            "Eagle King."
        ),
        traits={"Self-Reliant": 4, "Hot-Tempered": 3, "Idealistic": 2},
    )
    b.link(
        m["dalton"],
        "characters",
        m["brian"],
        "Close friend; apprenticed and gauntleted together",
    )


# ---------------------------------------------------- the Paruchia of Nerius


def _paruchia(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    place = hibernia.places["little_saltee"]
    summary = paragraphs(
        "A monastic community and covenant of the Hermetic Céli Dé, a tiny "
        "tradition that joined House Ex Miscellanea in 1189: three Gifted "
        "holy men, two monks and a manaim, on Little Saltee, an island "
        "otherwise empty five miles off the Wexford coast, closely tied "
        "to the folk of Great Saltee next door. Its aura is Divine 3, not "
        "Magic. Its device is a skeletal hand shining with light, and its "
        "cathach the skeletal arm of Saint Nerius, a relic with three "
        "Faith Points. Irish by birth, its magi stand against the old "
        "pagan customs and argue for a Christian Tribunal on the "
        "continental model, so they get on better with the English "
        "reformers than with their fellow Irish magi and look for allies "
        "among newcomers.",
    )
    what_matters = _lines(
        "Vis: little needed, and none named",
        "Library: a tall tower on Little Saltee; Indrechtach begs leave to copy books across the Tribunal",
        "Boon: Island",
        "Boon: Difficult Access (treacherous tides, no good landing)",
        "Boon: Loyal Covenfolk (the twenty-eight islanders of Great Saltee)",
        "Hook: Missing Aura (Divine 3, no Magic aura; few visitors stay long)",
        "Hook: Gender Imbalance (no woman may land on Little Saltee)",
        "Hook: Hermetic Politics (its campaign for Holy Magic and a Christian Tribunal)",
        "Tension: the Túath Buidhe of the Coill Trí, and the Fomórach, Tuatha Dé and Fir Bolg ambassadors",
        "Tension: uneasy with much of House Ex Miscellanea and with House Merinita",
    )
    notes = paragraphs(
        "History. Fedelmid of Limerick, a Hermetic magus on pilgrimage to "
        "Rome, wandered into a strange valley in the Alps and saw a run "
        "of visions of the mysterious magus-saint Nerius that shaped the "
        "rest of his life. He sought out the secrets of Holy Magic and "
        "trained an apprentice, Indrechtach, who taught a manaim of his "
        "monastery in turn. All three are Gifted; Indrechtach has no "
        "Gentle Gift and was put out of his community. Together they made "
        "a new monastery and covenant on the Saltees. Fedelmid is on "
        "excellent terms with his fellow Céli Dé, even those of the Coill "
        "Trí, but some magi think these holy men untrustworthy, even "
        "dangerous should the Anglo-Irish Church start to take notice.",
        "The cathach. Nobody knows how Fedelmid came by the relic, given "
        "the mystery of Nerius's martyrdom. A little shrine high on Great "
        "Saltee's cliffs holds it, outside the Aegis; the islanders "
        "say it works miracles but keep quiet about them, fearing "
        "churchmen will carry it off to a mainland church.",
        "The Hermetic Céli Dé. They take Holy Magic as their Major "
        "Virtue and Subtle Magic as a Minor Hermetic Virtue, with the "
        "Restriction that their magic cannot touch women. Their ascetic "
        "life gives them a Living Conditions modifier of 0 to aging "
        "rolls, not a magus's usual bonus. As a Divine societas their "
        "Favored Abilities are Holy Magic, Intervention, Purity and "
        "Transcendence. They do not teach True Faith: they are a few who "
        "already have it and are drawn to this path, and they accept "
        "only Gifted apprentices of that rare devotion.",
        "The covenant. Beehive cells, a small chapel, laboratories in "
        "caves nearby and a tall library tower; a little graveyard holds "
        "earlier hermits. Each Sunday the monks cross to Great Saltee "
        "for mass in an enchanted coracle Fedelmid built. They need "
        "little vis and few laboratory texts, and welcome Hermetic "
        "visitors, whom the missing Magic aura and the diet (largely "
        "seaweed and seabirds' eggs) soon send on their way. Fedelmid and "
        "Indrechtach mean to save the Order by teaching it Holy Magic, "
        "and try to save newcomers' souls the same way. They would "
        "welcome magi of any House, though few will want to come.",
        "Covenfolk. The islanders of Great Saltee: two farming families "
        "and three fisher brothers with wives and children, and Father "
        "Diarmaid, priest of St. Mary's, a good friend who guards his "
        "isolated flock.",
        "Founded 1189, when the tradition joined the Order. Season: Spring.",
    )
    hidden = _lines(
        "Father Diarmaid was posted to Great Saltee for a past wrong that still haunts him; anyone who threatened to reveal it could blackmail him.",
        "Fedelmid made many enemies in the feuds of his youth, and some may try to kill him on the road before he reaches Qui Sonant to die.",
    )
    paruchia = b.covenant(
        "The Paruchia of Nerius",
        tribunal=tribunal,
        founded=1189,
        place=place,
        aura=3,
        realm="Divine",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Spring",
    )
    hibernia.covenants["paruchia"] = paruchia
    hibernia.cathaigh["paruchia"] = {
        "cathach": "the skeletal arm of Saint Nerius, a relic with three Faith Points"
    }
    b.book(
        paruchia,
        "The library of the Paruchia",
        "Other",
        description=(
            "No books are named. It is kept in a tall tower on Little "
            "Saltee, and holds what the hermits need for Holy Magic and "
            "their devotions; Indrechtach adds to it by copying books at "
            "other covenants with their leave."
        ),
    )
    m = hibernia.magi
    m["fedelmid"] = b.magus(
        "Fedelmid",
        covenant=paruchia,
        house=EX_MISC,
        age=102,
        summary=paragraphs(
            "Fedelmid an t-Éigse Measceal (FEDGE-el-midge on TCHAY-shuh "
            "MYES-kul), comarba Nerius, leader of the Paruchia, looking "
            "ninety-five. A young Céli Dé, he joined House Ex Miscellanea "
            "believing the Order the very spirit of learning and "
            "discipline a Gifted holy man should seek. Many of its members "
            "disappointed him; he stays loyal to his sodales but never "
            "puts them before the Church. His is not a loyalty to sees, "
            "bishops and institutions but a personal, heroic asceticism, "
            "a saint's life of his own.",
            "His pilgrimage changed him twice over: the Alpine visions sent "
            "him in search of the few who knew Nerius's secret, and Rome "
            "taught him that the Pope has spiritual authority but that "
            "spiritual troubles are best mended locally by those they "
            "touch. He trained Indrechtach, and grieved when Glendalough "
            "cast him out.",
            "Now very old, worn by decrepitude and long bouts of Twilight, "
            "he is preparing to leave Little Saltee to die and be buried "
            "at Qui Sonant Pro Quieto, and hopes the covenant's next "
            "visitors will escort him there.",
        ),
        traits={"Moribund": 3, "Belligerent": 2, "Determined": 1},
    )
    m["indrechtach"] = b.magus(
        "Indrechtach",
        covenant=paruchia,
        house=EX_MISC,
        age=50,
        summary=paragraphs(
            "Indrechtach an t-Éigse Measceal (IND-rukh-tukh), Céli Dé, "
            "looking forty-seven, Fedelmid's apprentice, driven from the "
            "monastery at Glendalough because his Gift unsettled the "
            "monks. He unsettles most people: fearless, blunt and honest "
            "past all tact, he says just what he thinks and will not tell "
            "the smallest white lie.",
            "He says the prayers at the Tribunal, and is the one of his "
            "covenant other magi meet most: he travels round Hibernia "
            "visiting covenants, asking leave to copy books, and lending a "
            "hand with humble work most magi would think beneath them.",
            "Tonsured in the Irish manner, in a rough robe and sandals. A "
            "Twilight effect crowns his head with a nimbus when he works "
            "magic and makes his face glow faintly by moonlight; his "
            "sigil, heard in every spell, is a moment of voices singing "
            "the Psalms.",
        ),
        traits={"Pious": 6, "Brave": 3, "Honest": 3},
    )
    m["coemgen"] = b.magus(
        "Cóemgen",
        covenant=paruchia,
        house=EX_MISC,
        age=22,
        summary=(
            "Cóemgen an t-Éigse Measceal (COE-muh-gen), newly gauntleted, "
            "looking his age: a manaim, who keeps the hours but has not "
            "taken a monk's full vows and may marry. He longs to marry and "
            "raise a family on Great Saltee, crossing to the covenant each "
            "day, but there is no unwed woman on the island, and his Gift "
            "and crippling shyness spoil his hopes. Gentle and likeable, "
            "he may one day row to Wexford to carry off a bride, or court "
            "a woman he meets, earnestly and clumsily."
        ),
        traits={"Gentle": 3, "Shy": 2, "Romantic": 1},
    )
    b.link(
        m["fedelmid"],
        "characters",
        m["indrechtach"],
        "His apprentice, trained in Holy Magic",
    )
    b.link(m["indrechtach"], "characters", m["coemgen"], "Taught him Holy Magic")


# ------------------------------------------------------------------ finish


def finish(hibernia: Hibernia) -> None:
    """Tie Leinster into the island, the Liberty to the Lord of Ireland,
    Dublin to the viceroy, the royal ports to the king, and the churches
    to the Archbishop of Dublin, once the other parts have made them."""
    w = hibernia.world
    province = hibernia.places.get("leinster")
    ireland = hibernia.places.get("ireland")
    if province is not None and province.place_id is None and ireland is not None:
        province.place_id = ireland.id
    king = w.get("henry_iii")
    if king is not None:
        for key in ("leinster_liberty", "theobald_butler", "wexford"):
            record = w.get(key)
            if record is not None and record.answers_to is None:
                record.answers_to = king.id
    viceroy = w.get("viceroy")
    dublin = w.get("dublin")
    if viceroy is not None and dublin is not None:
        dublin.answers_to = viceroy.id
    see = w.get("dublin_see")
    if see is not None:
        for key in CHURCHES:
            church = w.get(key)
            if church is not None and church.answers_to is None:
                church.answers_to = see.id


#: The churches this part makes, all in the province of Dublin.
CHURCHES = (
    "bishop_ferns",
    "ferns_abbey",
    "baltinglass_abbey",
    "glendalough_monastery",
    "christchurch",
    "st_patricks_dublin",
    "brigids_fire",
    "kilrush",
    "bishop_ossory",
    "kells_priory",
    "jerpoint",
    "great_saltee_church",
)


# ------------------------------------------------------------------ stats


@cache
def _spell(start: str) -> str:
    """The catalog's name of the book's spell whose name begins so: the
    Holy Magic spells are named for whole verses of Scripture."""
    key = "".join(ch for ch in start.casefold() if ch.isalnum())
    for spell in catalog.load_spell_catalog():
        name = "".join(ch for ch in spell.name.casefold() if ch.isalnum())
        if spell.source == "TCI" and name.startswith(key):
            return spell.name
    raise KeyError(f"No TCI spell beginning {start!r} in the catalog")


def _affinity(ability: str) -> tuple[str, dict[str, str]]:
    return ("Affinity with {ability}", {"ability": ability})


#: Indrechtach's stat block, as The Contested Isle prints it.
INDRECHTACH: StatBlock = {
    "characteristics": {
        "intelligence": 2,
        "perception": 1,
        "presence": 1,
        "communication": 1,
        "strength": 0,
        "stamina": 1,
        "dexterity": 0,
        "quickness": 0,
    },
    "aging_points": {"perception": 1},
    "size": 0,
    "confidence": (1, 3),
    "decrepitude": (0, 1),
    "warping": (3, 0),
    "apparent_age": 47,
    "virtues_flaws": [
        "Hermetic Magus",
        "The Gift",
        "Holy Magic",
        "True Faith",
        _affinity("purity"),
        _affinity("intervention"),
        "Educated",
        "Quiet Magic",
        "Quiet Magic",
        "Subtle Magic",
        "Restriction",
        "Pious (Major)",
        "Slow Caster",
        "Susceptibility to Faerie Power",
        "Vow (Minor)",
    ],
    "traits": {"Pious": 6, "Brave": 3, "Honest": 3},
    "reputations": {"Holy Man (Irish Church)": 1},
    "abilities": [
        ("Area Lore: Ireland", 2, "Leinster"),
        ("Artes Liberales", 2, "poetry"),
        ("Charm", 2, "bishops"),
        ("Chirurgy", 2, "tooth pulling"),
        ("Civil and Canon Law", 2, "Papal Bulls"),
        ("Concentration", 4, "prayer"),
        ("Dominion Lore", 3, "Irish saints"),
        ("Living Language: English", 2, "Leinster"),
        ("Finesse", 1, "Herbam"),
        ("Folk Ken", 2, "manaim"),
        ("Guile", 2, "spotting lies"),
        ("Holy Magic", 5, "Intervention"),
        ("Infernal Lore", 2, "demonic temptations"),
        ("Intervention", 4, "Transcendence"),
        ("Living Language: Irish", 5, "prayers"),
        ("Dead Language: Latin", 5, "ecclesiastical"),
        ("Medicine", 1, "fevers"),
        ("Organization Lore: Church", 3, "Céli Dé"),
        ("Organization Lore: Order of Hermes", 2, "Holy Magi"),
        ("Parma Magica", 1, "Vim"),
        ("Purity", 5, "Intervention"),
        ("Teaching", 5, "apprentices"),
        ("Theology: Christian", 3, "Holy Magic"),
        ("Transcendence", 2, "Purity"),
    ],
    "arts": {
        "Creo": 10,
        "Intellego": 5,
        "Muto": 5,
        "Perdo": 7,
        "Rego": 11,
        "Animal": 7,
        "Aquam": 5,
        "Auram": 5,
        "Corpus": 10,
        "Herbam": 5,
        "Ignem": 5,
        "Imaginem": 6,
        "Mentem": 5,
        "Terram": 5,
        "Vim": 11,
    },
    "spells": [
        ("Ward Against the Faeries of the Sea", "ReAq", 15, 0),
        ("Comfort of the Drenched Traveler", "PeAq", 5, 0),
        ("Bind Wounds", "CrCo", 10, 0),
        ("Cheating the Reaper", "CrCo", 30, 0),
        (_spell("For they are life"), "CrCo", 20, 0),
        ("Revealed Flaws of the Mortal Flesh", "InCo", 15, 0),
        (_spell("Put on the whole armor"), "MuCo", 20, 0),
        ("The Severed Limb Made Whole", "MuCo", 20, 0),
        ("Curse of the Unruly Tongue", "ReCo", 5, 0),
        (_spell("It will be health"), "ReCo", 20, 0),
        ("Spasms of the Uncontrolled Hand", "ReCo", 5, 0),
        (_spell("That I may come"), "ReCo", 25, 0),
        (_spell("Then I was the craftsman"), "ReHe", 15, 0),
        ("Moonbeam", "CrIg", 3, 0),
        ("Demon's Eternal Oblivion", "PeVi", 10, 0),
    ],
    "notes": paragraphs(
        "Stat block printed in The Contested Isle, chapter six. Age 50, "
        "looking 47. Soak 1; Encumbrance 0 (0). Fatigue: two OK levels, "
        "then -1, -3, -5 and Unconscious. Wounds: Light at 1-5 (-1), "
        "Medium at 6-10 (-3), Heavy at 11-15 (-5; the book prints 1-15), "
        "Incapacitated at 16-20, Dead at 21 or more. Combat: dodge, Init 0, Atk 0, Dfn 0, Dam n/a; punch, Init "
        "0, Atk 0, Dfn 0, Dam 0.",
        "Devotions: Saint Nerius 3 (5), a bonus of 3 to invoke him. "
        "Purity is printed as 5 (9) and Transcendence as 2 (4); the "
        "numbers in brackets are not entered. The book's 'Educated Quiet "
        "Magic (2)' is read as Educated and Quiet Magic taken twice; "
        "Pious is listed among his Major Flaws. The Restriction is that "
        "his magic cannot affect women; the Vow is the Céli Dé's. He has "
        "no Magic Theory score in the book.",
        "Casting totals as printed: Ward Against the Faeries of the Sea "
        "+16, Comfort of the Drenched Traveler +13, Bind Wounds, Cheating "
        "the Reaper and the Ritual 'For they are life' +21, Revealed "
        "Flaws of the Mortal Flesh, 'Put on the whole armor of God' and "
        "The Severed Limb Made Whole +16, the four Rego Corpus spells "
        "+22, 'Then I was the craftsman' +16, Moonbeam +16, Demon's "
        "Eternal Oblivion +19. The Severed Limb Made Whole is printed as "
        "MuCo 20 but the catalog's spell of that name is CrCo 25; Demon's "
        "Eternal Oblivion is printed at level 10.",
        "Holy Magic. All his magic is Holy Magic, which he was taught in "
        "place of the Hermetic kind; most of his spells match common "
        "Hermetic ones, and five are the book's own (in the catalog). He "
        "may not use magic for anything sinful and refuses Hermetic "
        "spells, and only someone with Holy Magic can learn his spells "
        "from him. Aligned to both Divine and Magic, he may use either "
        "column of the aura interaction table.",
    ),
}

P = Profile
IRISH = "Irish"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "helles": P(
        strong="int com pre",
        weak="str dex",
        arts={"Me": 8, "In": 6, "Re": 5, "Im": 4, "Cr": 3},
        abilities={
            "Code of Hermes": (7, "the Peripheral Code"),
            "Artes Liberales": (5, "rhetoric"),
            "Civil and Canon Law": 3,
            "Intrigue": (4, "Tribunal politics"),
            "Etiquette": 3,
            "Folk Ken": 3,
        },
        virtues=["Clear Thinker", "Driven (Minor)", "Proud (Minor)"],
        native="French",
    ),
    "pollices": P(
        strong="int per com",
        weak="str qik",
        arts={"Co": 9, "Pe": 7, "In": 6, "Cr": 4, "An": 3},
        abilities={
            "Medicine": (6, "plagues"),
            "Chirurgy": 3,
            "Etiquette": (4, "nobles"),
            "Charm": 3,
            "Philosophiae": 3,
            "Living Language: English": 3,
            "Living Language: Norman French": 3,
        },
        virtues=[
            "Gentle Gift",
            "Disfigured",
            "Wrathful (Minor)",
            "Obsessed (Minor)",
        ],
        native="Italian",
    ),
    "dyfrgi": P(
        strong="sta str per",
        weak="com",
        arts={"Mu": 7, "An": 8, "Co": 5, "Re": 4},
        abilities={
            "Heartbeast": (6, "wolf"),
            "Hunt": (4, "tracking"),
            "Survival": 3,
            "Animal Ken": 3,
            "Living Language: English": 2,
        },
        age=75,
        native="Welsh",
    ),
    "tug": P(
        strong="int per pre",
        arts={"In": 7, "Me": 7, "Vi": 5, "Cr": 4},
        abilities={
            "Enigmatic Wisdom": 5,
            "Dominion Lore": (3, "saints"),
            "Faerie Lore": (3, "forest faeries"),
            "Living Language: Irish": 3,
        },
        virtues=["Visions", "Pious (Minor)"],
        native="High German",
    ),
    "dorjan": P(
        strong="pre com qik",
        arts={"Pe": 7, "Cr": 6, "Ig": 7, "Re": 5, "Me": 4},
        abilities={
            "Penetration": 4,
            "Charm": (4, "women"),
            "Single Weapon": (3, "sword"),
            "Ride": 3,
            "Organization Lore: House Tremere": 3,
        },
        virtues=[("Puissant {ability}", {"ability": "charm"}), "Reckless (Minor)"],
        native="Hungarian",
    ),
    "konstanczia": P(
        strong="int per com",
        arts={"In": 7, "Me": 8, "Re": 6, "Pe": 5, "Vi": 4},
        abilities={
            "Code of Hermes": (5, "the Peripheral Code"),
            "Intrigue": (5, "Tribunal politics"),
            "Organization Lore: House Tremere": 4,
            "Folk Ken": (3, "magi"),
            "Penetration": 3,
        },
        virtues=["Clear Thinker", "Dutybound"],
        native="Hungarian",
    ),
    "dalton": P(
        strong="per sta int",
        weak="com",
        arts={"In": 9, "Ig": 9, "Cr": 5, "Pe": 5, "An": 4},
        abilities={
            "Hunt": (6, "tracking"),
            "Penetration": (5, "Ignem"),
            "Animal Ken": (4, "hounds"),
            "Leadership": (4, "the Uí Broin"),
            "Ride": 3,
            "Area Lore: Wicklow": 3,
        },
        virtues=[
            ("Puissant {ability}", {"ability": "penetration"}),
            "Life Boost",
            "Proud (Major)",
        ],
        native=IRISH,
    ),
    "brian": P(
        strong="sta dex int",
        weak="pre",
        arts={"Aq": 9, "Pe": 7, "Ig": 6, "Mu": 5, "An": 5},
        abilities={
            "Swim": (6, "rivers"),
            "Penetration": 4,
            "Area Lore: Wicklow": (4, "rivers and lakes"),
            "Survival": 3,
            "Stealth": 2,
        },
        virtues=["Skinchanger", "Hatred (Major)"],
        native=IRISH,
    ),
    "cliodna": P(
        strong="dex qik sta str",
        weak="com int",
        arts={"Ig": 8, "Cr": 6, "Re": 5, "An": 6, "Pe": 4},
        abilities={
            "Single Weapon": (5, "sword"),
            "Ride": (5, "charging"),
            "Athletics": (4, "running"),
            "Penetration": 3,
            "Animal Ken": (3, "eagles"),
        },
        virtues=["Warrior", "Life Boost", "Wrathful (Minor)", "Reckless (Minor)"],
        native=IRISH,
    ),
    "fedelmid": P(
        strong="int sta per",
        weak="qik dex",
        arts={"Cr": 9, "Re": 9, "Co": 8, "Vi": 8, "In": 5},
        abilities={
            "Holy Magic": 7,
            "Purity": 5,
            "Intervention": 5,
            "Transcendence": 4,
            "Dominion Lore": (5, "Irish saints"),
            "Theology: Christian": 4,
            "Teaching": 3,
            "Craft: Boatbuilding": 2,
        },
        virtues=[
            "Holy Magic",
            "True Faith",
            "Subtle Magic",
            "Educated",
            "Restriction",
            "Twilight Prone",
            "Enemies",
            "Vow (Minor)",
        ],
        native=IRISH,
    ),
    "coemgen": P(
        strong="com dex int",
        weak="pre",
        arts={"Cr": 5, "Re": 5, "Co": 5, "Vi": 3},
        abilities={
            "Holy Magic": 3,
            "Purity": 2,
            "Intervention": 2,
            "Dominion Lore": 2,
            "Profession: Fisherman": 2,
        },
        virtues=[
            "Holy Magic",
            "True Faith",
            "Subtle Magic",
            "Educated",
            "Restriction",
            "Pious (Major)",
            "Vow (Minor)",
            "Infatuation (Minor)",
        ],
        native=IRISH,
    ),
}


def stats(hibernia: Hibernia) -> None:
    """Indrechtach's printed stat block, then generated stats for the
    other magi of Leinster's three covenants."""
    b = hibernia.b
    indrechtach = hibernia.magi.get("indrechtach")
    if indrechtach is not None:
        b.stats(indrechtach, INDRECHTACH)
    for key, profile in PROFILES.items():
        magus = hibernia.magi.get(key)
        if magus is not None:
            apply(b, magus, profile)
