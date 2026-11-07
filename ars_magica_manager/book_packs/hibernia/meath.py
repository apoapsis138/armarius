"""Meath, the middle province of the Hibernian Tribunal, as of 1220: the
Liberty of Meath (places["meath"]) and its places, the Hill of Tara where
the Tribunal meets (with the Mound of Hostages and the Lia Fáil), the
Hill of Uisneach and its Stone of Division, the Brú na Bóinne and New
Grange, the Hills of Tlachtga and Tailten, Clonmacnoise with its crosses
and Faerie Stone, and the Eiscir Riada; the top of the English lordship
(the Lord of Ireland, his regent, the viceroy and Walter de Lacy), the
itinerant justices, the Baron of Delvin and the exiled Uí Mael Sechlainn;
the towns of Drogheda-in-Meath, Trim and Kells; Mellifont, Bective, Kells
and Clonmacnoise among the churches, with the Book of Kells; the Ostmen
of the ports as a faction; and, in finish, ch03's picture of the Irish
land, people and law in places["ireland"]. In paraphrase of The
Contested Isle chapter seven, and chapter three for the island.

Keys: places["meath"], ["tara"], ["mound_of_hostages"], ["lia_fail"],
["uisneach"], ["ail_na_mireann"], ["bru_na_boinne"], ["newgrange"],
["tlachtga"], ["tailten"], ["clonmacnoise"], ["north_cross"],
["faerie_stone"], ["eiscir_riada"]. world["henry_iii"], ["regent"],
["viceroy"], ["walter_de_lacy"], ["itinerant_justices"], ["delvin"],
["ui_mael_sechlainn"], ["ostmen"], ["drogheda_meath"], ["trim"],
["kells_town"], ["mellifont"], ["bective"], ["kells_abbey"],
["trim_abbey"], ["clonmacnoise_abbey"].

No covenant stands in Meath in 1220 (Praesis, on Lough Ree, is
Connacht's part; the lost covenant of Uisneach is the Tribunal's ruin),
so this part names no magi and has no stats. None of the four great
bardic schools lies in Meath; they are the Otherworld part's, and the
Chief Bard's empty seat is told in Ireland's notes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ... import storage
from ...arms import Arms
from ...models import Book
from ..builder import paragraphs, secrets, titled

if TYPE_CHECKING:
    from ...models import Neighbour
    from ..builder import Builder
    from . import Hibernia

#: The Lord of Ireland bears England's arms: three gold lions on red.
ENGLAND_ARMS = Arms("Gules", charge="Lion", charge_tincture="Or", count=3)

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}


def _add(hibernia: Hibernia, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = hibernia.b.place(name, **kw)
    hibernia.places[key] = place
    return place


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    _region(hibernia)
    _tara(hibernia)
    _uisneach(hibernia)
    _boyne(hibernia)
    _hills(hibernia)
    _clonmacnoise(hibernia)
    _lordship(hibernia, b)
    _meath_lords(hibernia, b)
    _churches(hibernia, b)
    _towns(hibernia, b)
    _ostmen(hibernia, b)
    _books(hibernia, b)


# ------------------------------------------------------------- the region


def _region(hibernia: Hibernia) -> None:
    _add(
        hibernia,
        "meath",
        "Meath",
        inside=hibernia.places.get("ireland"),
        summary=paragraphs(
            "Mide, 'the middle': the fifth province of Ireland and the "
            "smallest, counted a province rather than one more kingdom "
            "because of what it means. The legend says Túathal Techtmar, "
            "son of a deposed high-king, was carried in his mother's womb "
            "to Scotland when the four provincial kings rose against his "
            "father (his mother Eithne may be Bóinn under another name). "
            "Twenty years of famine followed under the usurper from Ulster "
            "until Túathal came back with an army, beat the kings of all "
            "four provinces in turn, and called them to Tara, where he gave "
            "laws and carved out a new province round the hill to be the "
            "high-kings' own land.",
            "Late in the fifth century the Uí Enechglaiss were driven south "
            "to Arklow, where they still live, and the Uí Mael Sechlainn, "
            "the Southern Uí Néill, took Meath and gave Ireland several "
            "high-kings. They in turn fled when the English came: the last "
            "king of Meath was put down in 1172 and the kingdom given to "
            "Hugh de Lacy, who kept it until he died in 1186 though Henry "
            "II had turned against him. Tighearnán Ua Ruairc of Bréifne "
            "contested the grant and was slain at a parley on the Hill of "
            "Tlachtga, and Hugh's son Walter de Lacy holds Meath for the "
            "English today. It is the one province with no Gaelic dialect "
            "of its own.",
            "A Liberty. Meath, Leinster and the earldom of Ulster are "
            "Liberties: the Crown governs each through a grantee, here "
            "Walter de Lacy, who gathers the king's revenue and does "
            "justice, and answers in turn to the Justiciar of Ireland. The "
            "wool and grain of the Liberties leave the Crown a surplus, but "
            "the king distrusts his great Irish lords; he takes their sons "
            "as hostages, orders them off to England or France, or "
            "hands their lands to others before any grows too strong.",
            "Justice. Since 1217 itinerant justices have ridden circuits "
            "through the Liberties, holding assizes under English common "
            "law. An Irishman in their court needs an interpreter, has "
            "little hope in a law he does not know, and finds his word "
            "weighed below an Englishman's; among themselves the Irish "
            "keep the Brehon Laws and see the assizes as a shield for "
            "English privilege.",
            "Places: the Hill of Tara, where the Tribunal meets; the Hill "
            "of Uisneach at the centre of Ireland; the Brú na Bóinne and "
            "New Grange on the bend of the Boyne; the Hills of Tlachtga and "
            "Tailten; Clonmacnoise on the Shannon; and the Eiscir Riada, "
            "the ridge dividing Leth Cuinn from Leth Moga. Towns: "
            "Drogheda-in-Meath, Trim and Kells. Churches: Mellifont, "
            "Bective, Kells, Trim and Clonmacnoise. No covenant stands in "
            "Meath, though Praesis looks across Lough Ree at it from the "
            "Connacht side.",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------------- Tara


def _tara(hibernia: Hibernia) -> None:
    meath = hibernia.places["meath"]
    tara = _add(
        hibernia,
        "tara",
        "The Hill of Tara",
        inside=meath,
        aura=6,
        summary=paragraphs(
            "Cnoc na Teamhrach, the seat of Ireland's ancient kingship and "
            "the setting of countless Irish tales, where the Hibernian "
            "Tribunal meets every seven years. In 1220 it lies quiet, "
            "famous everywhere yet left to grass and briar. It is a broad, "
            "low mound ringed by the ditch of an old ringfort, with lesser "
            "ráths and other ancient, magical works about it, and a Magic "
            "aura of 6 over the whole site except the Mound of Hostages, "
            "which is the Tuatha Dé's (Faerie 7). The aura has a "
            "Respectful aspect (Realms of Power: Magic), giving everyone "
            "present a Respectful +2 Personality Trait, and every Samhain, "
            "when sacred fires used to burn here, the auras rise by 2.",
            "The Uí Mael Sechlainn styled themselves Kings of Tara until de "
            "Lacy took Meath in 1172, though by then the title was only "
            "ceremonial. In the sixth century Saint Ruadán foretold that "
            "King Diarmait would die in his own hall here, for dragging men "
            "out of sanctuary in the saint's church; the hall burned and a "
            "falling beam killed him as foretold, and ever since it has "
            "been held that the saint's curse lets no hall stand on the "
            "hill. The greatest of Tara's kings was Cormac mac Airt, whom "
            "Fionn mac Cumhaill often served; his reign was a golden age, "
            "and many earthworks are the ruins of his halls. Here too King "
            "Conaire, son of a bird-man and so bound never to harm a bird, "
            "was made king after shapechangers in bird form laid geasa on "
            "him and sent him naked into Tara, fulfilling the chief druid's "
            "omen; he reigned well until he broke those geasa one by one "
            "and fell to three exiled brothers.",
            "Faeries replay the old stories here, such as Áillen mac "
            "Midgna setting the hall alight and Fionn driving him off; "
            "Áillen, a three-headed faerie magician of northern Connacht, "
            "still burns Tara from time to time. Mortals seldom come, "
            "except that every seventh year the magi of Hibernia gather "
            "here with the Coill Trí's envoys and great beings of Magic "
            "and Faerie. Circulus Ruber raises a temporary camp by magic "
            "for each meeting, and the sessions are held in the large ráth "
            "on the hilltop around the Lia Fáil. The five High Roads of "
            "Ireland start from the royal fort at Tara.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        hibernia,
        "mound_of_hostages",
        "The Mound of Hostages",
        inside=tara,
        realm="Faerie",
        aura=7,
        summary=(
            "A mound on the Hill of Tara that belongs to the Tuatha Dé, "
            "the one part of the hill outside its Magic aura: a Faerie "
            "aura of 7, rising by 2 at Samhain like the rest of Tara."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "lia_fail",
        "The Lia Fáil",
        inside=tara,
        aura=6,
        summary=(
            "The Stone of Fál, or Stone of Destiny, one of the four "
            "treasures the Tuatha Dé brought to Ireland, which cries out "
            "under the foot of the rightful king. It stands at the top of "
            "the Hill of Tara inside the great ráth where every session of "
            "the Hibernian Tribunal is held, in the hill's Magic aura of 6."
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------------------- Uisneach


def _uisneach(hibernia: Hibernia) -> None:
    meath = hibernia.places["meath"]
    uisneach = _add(
        hibernia,
        "uisneach",
        "The Hill of Uisneach",
        inside=meath,
        aura=5,
        summary=paragraphs(
            "The hill (OOSH-nakh) at the mystic centre of Ireland, with a "
            "strong Magic aura of 5, where all five provinces touch at the "
            "Stone of Division. The druids kindled a great Bealtaine fire "
            "here, visible from Tara, to open the feast for the whole "
            "island. Here the Milesians met Ériu, Banba and Fódla, and "
            "Ériu gave Ireland her name; Saint Brigid made her vows here, "
            "both as a nun and as a bishop. Many of the Tuatha Dé lie "
            "asleep under the hill's numerous sídhe, and the druid Merlin "
            "carried off many of the stones of Stonehenge from this place.",
            "The aura drew a covenant here in the Order's first years in "
            "Hibernia, but one summer evening it disappeared without trace; "
            "only scraps of record remain and even its name is lost (see "
            "the ruin of the covenant of Uisneach). Country tales tell of "
            "a great magician who wished to rule all Ireland, broke a "
            "geas, and was taken by the Good Folk for his pride. Another "
            "covenant will probably be founded here one day.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "ail_na_mireann",
        "The Ail na Míreann",
        inside=uisneach,
        aura=5,
        summary=(
            "The Stone of Division on the Hill of Uisneach, where the "
            "borders of Ulster, Meath, Leinster, Munster and Connacht "
            "meet. It is an Arcane Connection to all five provinces, for "
            "anyone bold enough to try a spell on a whole province, and "
            "gives a x3 Sympathetic Magic modifier. It is the customary "
            "place to swear oaths and seal treaties that bind the whole "
            "Tribunal."
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------ the Boyne


def _boyne(hibernia: Hibernia) -> None:
    meath = hibernia.places["meath"]
    bru = _add(
        hibernia,
        "bru_na_boinne",
        "The Brú na Bóinne",
        inside=meath,
        realm="Faerie",
        aura=4,
        summary=paragraphs(
            "A plain of nearly two thousand acres in the bend of the "
            "Boyne, crowded with sídhe, standing stones and dolmens, "
            "the river closing it on the south, west and east. Until "
            "lately it lay wild and half forgotten; now Mellifont's "
            "monks have laid nine granges over it, fortified farms the "
            "size of manors whose barns and outbuildings ring each one "
            "and sit on high ground, often on old sídhe and ráths. With "
            "the scrub cleared the forty sídhe stand out plainly, and "
            "the faeries asleep inside may be stirring.",
            "Many stones, and some old bones and slates, carry marks in "
            "a wholly unknown script, which, gathered and somehow "
            "read, might open the old mysteries once worked here "
            "(Ancient Magic). Magic and Faerie auras of many strengths "
            "shift and wander across the plain (the pack gives it "
            "Faerie 4), and no magus has found out why. Hibernian magi "
            "mostly keep away, fearing to wake the Tuatha Dé who sleep "
            "here. The Dagdha built it, and Bóinn (see the Bestiary) is "
            "often met here, but it is the home of their son Aonghus "
            "mac Óg, god of youth and lovers, who tricked his father "
            "out of it; he is perilous to cross. In 778 the four "
            "founders of the Order in Hibernia dug the Dagda's "
            "cauldron out of one of its mounds, then held a barrow "
            "here for a year against the high-king's men.",
        ),
        secrets=[
            titled(
                "The monks among the barrows",
                "The monks working among the barrows of the Brú na Bóinne may have stumbled on some old magical secret, which could lie behind the Conspiracy of Mellifont.",
            )
        ],
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "newgrange",
        "New Grange",
        inside=bru,
        realm="Faerie",
        aura=5,
        summary=(
            "Mellifont's newest grange on the Brú na Bóinne, and beside it "
            "the greatest sídh of the plain, the home of Aonghus mac Óg, "
            "which people are starting to call Newgrange after the farm. "
            "The lay brothers here tell of frightening happenings, and "
            "trooping faeries (see the Bestiary) have trampled and spoiled "
            "the crops many times. The book gives the sídh no number; the "
            "pack gives it Faerie 5."
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------------------- the hills


def _hills(hibernia: Hibernia) -> None:
    meath = hibernia.places["meath"]
    _add(
        hibernia,
        "tlachtga",
        "The Hill of Tlachtga",
        inside=meath,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "A ráth-crowned hill, one of the royal sites of Meath, where "
            "the faerie druidess Tlachtga, Mug Ruith's daughter, sleeps in "
            "her sídh. Mug Ruith still calls now and then in his marvellous "
            "flying machine, and she sometimes comes out to talk with "
            "mortals who wander onto the hill. She helped her father build "
            "that machine while he studied under Simon Magus, until Simon "
            "raped her; she fled home, her father broke with the sorcerer "
            "(whom Saint Paul later slew), and here she bore the triplets "
            "Doirb, Cumma and Muach before withdrawing into the hill. The "
            "druids lit their Samhain fires on it in her memory. The book "
            "gives no aura; the pack gives Faerie 3.",
            "Ruaidrí Ua Conchobair called a vast assembly here in 1168, "
            "and in 1171 Tighearnán Ua Ruairc of Bréifne met Hugh de Lacy "
            "here under truce to dispute Meath; a brawl broke out, de "
            "Lacy's interpreter was killed, de Lacy ran, and his men "
            "speared Tighearnán as he mounted, perhaps by design. Tlachtga "
            "stirred for neither.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "tailten",
        "Tailten",
        inside=meath,
        aura=3,
        summary=paragraphs(
            "The burial place of Tailtu, a Spanish princess wed to "
            "Eochaid mac Eirc, last Fir Bolg high-king, who built his "
            "capital here; it was razed after he fell against the Tuatha "
            "Dé, and nothing of it is left, though the Uí Néill still hold "
            "the site dear. Captured by the Tuatha Dé, Tailtu fostered "
            "Lugh, and died of clearing Ireland's plains of forest for the "
            "plough; she was buried here at Lammas amid great grief.",
            "Tailten Fair each Lammas (1 August) remembers her and the "
            "games the Fir Bolg and Tuatha Dé held before they came to "
            "battle: a merry, bawdy gathering and one of Ireland's few "
            "great markets, with wrestling, horse races, foreign wares "
            "and luxuries. Tailten Marriages, for a year and a day, were "
            "made here until the English and the Church reformers banned "
            "them a few years ago, to the people's disgust. Strangely, the "
            "site has a Magic aura of 3 by day and a Faerie aura of 3 by "
            "night.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "eiscir_riada",
        "The Eiscir Riada",
        inside=meath,
        summary=(
            "The best known of the eskers, long banks of sand and gravel "
            "that rise as much as fifty feet over the flat bogs and plains "
            "of central Ireland and have served as roads since ancient "
            "times; some say the Fomórach, the Fir Bolg or the Tuatha Dé "
            "built them, others that they are serpents turned to earth "
            "when Saint Patrick banished them. The Eiscir Riada runs from "
            "Galway Bay toward Dublin and carries the Great Highway (An "
            "tSlí Mhór), one of the High Roads, along its crest from "
            "Durrow Abbey to Clonmacnoise. It is the line between Conn's "
            "Half, Leth Cuinn, to the north and Mogha's Half, Leth Moga, "
            "to the south, which gave the two Mercer Houses their names."
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------- Clonmacnoise


def _clonmacnoise(hibernia: Hibernia) -> None:
    meath = hibernia.places["meath"]
    clon = _add(
        hibernia,
        "clonmacnoise",
        "Clonmacnoise",
        inside=meath,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "One of Ireland's most renowned old monastic sites, on the "
            "east bank of the Shannon where Meath meets Connacht: a busy "
            "town grown round the monastery, yet calm and holy, with a "
            "Dominion aura of 3 over the whole town, stronger in the "
            "graveyard and by the three high crosses that stand in its "
            "streets. A high-king built the stone cathedral in 909, and "
            "Ruaidrí Ua Conchobair, the last High-King of Ireland, was "
            "buried here in 1198. Pilgrims visit Saint Ciarán's tomb in "
            "the oldest church and then pray in each of the others, as "
            "custom now asks. The English have put a small stone keep on "
            "the hill above.",
            "The Uí Mael Sechlainn, who settled here after losing Meath "
            "in 1172, built Temple Melaghlin in 1200 as their dynasty's "
            "church, and the little Romanesque church by the river with "
            "its bell tower, home of one of Ireland's ancient sacred "
            "bells, and Temple Connor; from here they plot to win back "
            "Meath. Derbforgaill, wife of Tighearnán Mór Ua Ruairc and "
            "the 'Helen of Ireland' whose abduction by Diarmait began the "
            "English war, endowed the Nun's Church in 1160.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "north_cross",
        "The North Cross of Clonmacnoise",
        inside=clon,
        realm="Divine",
        aura=4,
        summary=(
            "One of the three great carved crosses, thirteen to fifteen "
            "feet high, in Clonmacnoise's streets; its shaft bears an old "
            "pagan carving of Cernunnos, the Celtic god of fertility. "
            "Taken away from Clonmacnoise, the stone might take back its "
            "first aura, but the whole countryside would rise against the "
            "thieves. The South Cross and the Cross of the Scriptures show "
            "ordinary Bible scenes in superb work. The book says only that "
            "the Dominion is stronger by the crosses; the pack gives "
            "Divine 4."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "faerie_stone",
        "The Faerie Stone of Clonmacnoise",
        inside=clon,
        realm="Divine",
        aura=3,
        summary="One of several big yellow sandstone boulders in "
        "Clonmacnoise, also called the Horseman's Stone. It bears the "
        "same strange script as the stones of the Brú na Bóinne and "
        "the prints of two human feet, and locals hold it the door of "
        "a faerie fort: a rider in golden armour was said to come out "
        "and cross the land on Midsummer night, the Feast of John the "
        "Baptist, but none has seen him for centuries, perhaps "
        "because the priests lead a procession to the rock and bless "
        "it that day. It sits in the town's Dominion aura of 3. Twenty "
        "years ago Josiane of Merinita, of the Normandy Tribunal, "
        "shrank it with Terram magic and led it off on a mule for her "
        "laboratory, but by morning it was gone, and back in "
        "Clonmacnoise she found it where she had first seen it; she "
        "sensibly did not try again.",
        secrets=[
            titled(
                "What binds the stone",
                "Whatever makes the Faerie Stone of Clonmacnoise return, it is bound to this spot.",
            ),
            titled(
                "The faerie fort",
                "The faerie fort behind the Faerie Stone of Clonmacnoise may still be inhabited.",
            ),
        ],
        **KNOWN_LOCALLY,
    )


# ---------------------------------------------------- the English lordship


def _lordship(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    ireland = hibernia.places.get("ireland")
    meath = hibernia.places["meath"]
    w["henry_iii"] = b.lord(
        "Henry III, Lord of Ireland",
        title="duke",
        wealth="Wealthy",
        seat="Westminster; in Ireland, Dublin",
        ruler="King Henry III",
        place=ireland,
        arms=ENGLAND_ARMS,
        summary=paragraphs(
            "Henry III, King of England and Lord of Ireland, a boy of "
            "fourteen in 1220. His lordship takes in the Liberties of "
            "Meath, Leinster and Ulster, the royal shires and cities "
            "round Dublin, Waterford and the other ports, and the tribute "
            "of the Irish kings who have submitted, Connacht's under the "
            "Treaty of Windsor among them. He rules through a regent, "
            "William Marshal the younger, and in Ireland through his "
            "viceroy, Archbishop Henry de Londres of Dublin.",
            "Like his forebears he eyes his great Irish lords warily: he "
            "keeps their sons as hostages for their good behaviour, calls "
            "them away to serve in England or France, or gives their "
            "estates to rivals. Lords of the Liberties keep what their "
            "lands yield; the king's shires pass most of their rents to "
            "him, and a shire with a city in it can make its keeper "
            "richer than a lord of a Liberty. The Liberties' wool and "
            "grain leave the Crown a surplus.",
        ),
    )
    w["regent"] = b.lord(
        "William Marshal the Younger, Regent",
        title="count",
        wealth="Wealthy",
        seat="Ferns, Kilkenny and Trim",
        ruler="William Marshal the younger",
        answers_to=w["henry_iii"],
        place=ireland,
        summary=paragraphs(
            "The regent for the young king, as the book has it: William "
            "Marshal the younger, thirty years old, Earl of Pembroke, who "
            "took up the regency when his famous father, the greatest "
            "knight of the age, died in 1219. He lives about Kilkenny, "
            "Ferns and Trim (his lands in Leinster are that part's to "
            "tell), and is betrothed to the king's five-year-old sister, "
            "Eleanor of Leicester.",
            "In real history the elder Marshal's regency passed to others "
            "in 1219; the book makes the son regent, and the pack follows "
            "the book.",
        ),
    )
    w["viceroy"] = b.lord(
        "Henry de Londres, Viceroy of Ireland",
        title="count",
        wealth="Wealthy",
        seat="Dublin",
        ruler="Archbishop Henry de Londres",
        answers_to=w["regent"],
        place=ireland,
        summary=paragraphs(
            "Henry de Londres, Archbishop of Dublin, holds the king's "
            "authority in Ireland as viceroy, the Justiciar to whom "
            "the lords of the Liberties answer; his see is the Church "
            "part's record. He is energetic, ambitious and personally "
            "fearless, and almost universally loathed. He once "
            "summoned his tenants to show the deeds to their lands, "
            "then tried to throw the parchments on the fire; they "
            "seized him, thrashed his men, pulled their deeds back by "
            "main force and frightened him into granting their "
            "rights, and they call him 'Henry the Scorcher'. He "
            "squeezes Dublin's tithes hard, cared little for those "
            "the fire of 1190 ruined, levied the royal tallage on the "
            "citizens in 1217, and simply takes what he fancies from "
            "merchants.",
            "He has sworn to put out Saint Brigid's Sacred Fire at "
            "Kildare. He will appoint only English-born bishops, a "
            "policy the Pope has ruled unlawful, and claims for "
            "Dublin primacy over Armagh (and Cashel), which has turned "
            "even the Irish reform party against him and wrecked much "
            "of the trust between the reformers and the English "
            "clergy. Itinerant justices hold his assizes in the "
            "Liberties.",
        ),
        secrets=[
            titled(
                "The Pope's ruling",
                "The Pope's ruling against his English-only bishops has not yet reached Dublin; he does not know he has lost.",
            )
        ],
    )
    w["walter_de_lacy"] = b.lord(
        "Walter de Lacy, Lord of Meath",
        title="count",
        wealth="Wealthy",
        seat="Trim Castle",
        ruler="Walter de Lacy",
        answers_to=w["viceroy"],
        place=meath,
        summary=paragraphs(
            "Walter de Lacy, son of Hugh de Lacy the conqueror of Meath "
            "and brother of Hugh de Lacy, Earl of Ulster, holds the "
            "Liberty of Meath for the Crown: he gathers the king's "
            "revenues, does justice, and answers to the Justiciar of "
            "Ireland. He built Trim Castle, the largest stone castle in "
            "Ireland, as the seat of Meath's government, and is often "
            "there with his household; he also built Drogheda's castle, "
            "takes customs and imposts at its port, and holds Carbury "
            "castle in Leinster, which his father seized from Meiler "
            "FitzHenry. Tighearnán Ua Ruairc of Bréifne, who disputed his "
            "father's grant, is dead.",
            "He has thrown castles westward to push into Connacht, among "
            "them the motte at Kilmore in Bréifne (1211). If your saga "
            "follows history, Cathal Uí Raghallaigh takes Kilmore in 1224 "
            "and pulls it down, and others of his castles go the same way.",
        ),
    )
    justices = b.faction(
        "The Itinerant Justices",
        faction="Council or assembly",
        decides="Its leader",
        ruler="Archbishop Henry de Londres",
        place=ireland,
        wants="To bring English common law and the king's peace to the Liberties",
        offers="Judgement at the assizes, for those who can use English law",
        summary=(
            "Since 1217 the king's justice in the Liberties has been done "
            "by judges who ride a circuit from county to county, sitting "
            "at assizes under English common law. An Irish party must "
            "find an interpreter, can make little of the strange "
            "procedure, and sees his testimony counted for less than an "
            "English witness's; to the Irish, who keep the Brehon Laws "
            "among themselves, the assizes are a tool of oppression that "
            "guards English privilege."
        ),
    )
    justices.answers_to = w["viceroy"].id
    w["itinerant_justices"] = justices


def _meath_lords(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    meath = hibernia.places["meath"]
    w["delvin"] = b.lord(
        "Richard de Capella, Baron of Delvin",
        title="baron",
        seat="Delvin castle",
        ruler="Richard de Capella",
        answers_to=w["walter_de_lacy"],
        place=meath,
        summary=(
            "Hugh de Lacy built the stone castle at Delvin and gave it to "
            "his brother-in-law Sir Gilbert Nugent, first Baron Delvin. "
            "Gilbert's son Richard, the second baron, called Richard de "
            "Capella, 'Richard of the horses', lives for horse breeding. "
            "He holds a fine horse fair at Delvin each year and races "
            "open to anyone with a good mount, with prizes of better "
            "horses still, and for a truly great rider a place at his "
            "court and maybe a knighthood. An English (Anglo-Irish) lord."
        ),
    )
    w["ui_mael_sechlainn"] = b.lord(
        "The Uí Mael Sechlainn",
        title="landed",
        wealth="Poor",
        seat="Clonmacnoise",
        place=hibernia.places["clonmacnoise"],
        summary=(
            "The Southern Uí Néill, the Máel Sechnaill, one of the five "
            "bloods of Ireland: kings of Meath and of Tara from the late "
            "fifth century, who gave Ireland several high-kings until the "
            "English took their kingdom in 1172. They have settled round "
            "Clonmacnoise, where Temple Melaghlin is their royal church, "
            "and scheme to retake the throne of Meath. A Gaelic dynasty "
            "without a kingdom, they owe tribute to no one and receive "
            "none; the book names no living head."
        ),
    )


# -------------------------------------------------------------- churches


def _churches(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    meath = hibernia.places["meath"]
    w["mellifont"] = b.church(
        "Mellifont Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        founded=1140,
        ruler="Abbot Thomas",
        place=meath,
        summary=paragraphs(
            "The greatest Cistercian house in Ireland, near Drogheda, "
            "founded in 1140 by Saint Malachy of Armagh on land from the "
            "King of Meath; an Irish house. It is mother to Bective, "
            "Baltinglass and twenty-three more Cistercian abbeys across "
            "Ireland, and with a hundred monks and three hundred lay "
            "brothers it rules the Order in Ireland. Its first abbot, "
            "Saint Christian, reformed monastic life well beyond his "
            "Order and helped the Irish reformers bring in dioceses and "
            "weaken the paruchiae, yet Mellifont's abbots grew as mighty "
            "as any comarba: in 1154 a synod here, urged by the abbot, "
            "excommunicated and exiled Donnchadh Ua Maeleachlainn, King "
            "of Meath, and set up his brother Diarmaid instead.",
            "The Conspiracy of Mellifont. Since the invasion Irish and "
            "English monks have drawn apart, and tales of corruption and "
            "loose living reached Cîteaux; in 1216 a visitation came to "
            "restore the Rule, and the monks barred the gates against "
            "their superiors, a thing unheard of that has shaken monks "
            "across Mythic Europe. The general chapter deposed Abbot "
            "Thomas in 1217, but he still rules, upheld by his monks and "
            "the daughter houses. Cîteaux is readying a deputation to "
            "restore discipline and remove the guilty abbots, and the Pope "
            "may step in. Its nine granges cover the Brú na Bóinne.",
        ),
    )
    w["bective"] = b.church(
        "Bective Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        place=meath,
        summary=(
            "A strong Cistercian abbey above the Boyne, a daughter of "
            "Mellifont, where Hugh de Lacy lies buried. Its monks welcome "
            "travellers more warmly than most Cistercians. It has joined "
            "the Conspiracy of Mellifont, standing with its mother house "
            "against the Order. An Irish house."
        ),
    )
    w["kells_abbey"] = b.church(
        "The Monastery of Kells",
        church="Monastery or nunnery",
        order="Columban",
        ruler="The abbot, comarba Columcille",
        place=meath,
        summary=paragraphs(
            "Saint Columba's monastery at Kells in Meath (not the Kells "
            "in Leinster), with a church Saint Patrick founded; the town "
            "has grown about it in the Irish way. Its abbot, comarba "
            "Columcille, heads the paruchia of Saint Columba and rules "
            "the town. Kells was briefly the seat of a short-lived "
            "diocese, and here in 1152 began the synod (soon moved to "
            "Mellifont) that broke the comarbai's power and remade the "
            "Irish Church on dioceses rather than monasteries. An Irish "
            "house.",
            "It keeps two famous books: the Book of Kells, closely "
            "guarded since a theft in the eleventh century, and the "
            "battle psalter of the Ó Domhnaill clan, left here for safe "
            "keeping by one of that Donegal family.",
        ),
    )
    w["trim_abbey"] = b.church(
        "The Abbey of Saint Mary, Trim",
        church="Monastery or nunnery",
        order="Augustinian",
        founded=1140,
        place=meath,
        summary=(
            "An Augustinian abbey of Saint Mary that Saint Malachy founded "
            "at Trim in 1140, beside the church of Saint Lommán, which "
            "Saint Patrick founded and which was burned twice, in 1008 and "
            "1127, by enemies of those sheltering in it, then rebuilt. An "
            "Irish house in an English castle town."
        ),
    )
    w["clonmacnoise_abbey"] = b.church(
        "The Monastery of Clonmacnoise",
        church="Monastery or nunnery",
        place=hibernia.places["clonmacnoise"],
        summary=(
            "Saint Ciarán's great monastery on the Shannon, with its stone "
            "cathedral of 909 and a ring of lesser churches: Temple "
            "Melaghlin of the Uí Mael Sechlainn, their small church by the "
            "river with its bell tower and ancient bell, Temple Connor, "
            "Derbforgaill's Nun's Church, and the oldest, where Ciarán is "
            "buried and pilgrims begin their round. Ruaidrí Ua Conchobair, "
            "the last high-king, lies here. An Irish house; the whole town "
            "is under a Dominion aura of 3."
        ),
    )


# ----------------------------------------------------------------- towns


def _towns(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    meath = hibernia.places["meath"]
    lord = w["walter_de_lacy"]
    w["drogheda_meath"] = b.town(
        "Drogheda-in-Meath",
        charter="Noble lord",
        ruler="Walter de Lacy",
        answers_to=lord,
        place=meath,
        summary=(
            "A busy port astride the Boyne, wholly English and heavily "
            "garrisoned: Hugh de Lacy built the walled new town and "
            "Walter de Lacy the stone castle on the hill to its south. "
            "Drogheda-in-Airgialla faces it across the river to the "
            "north. Ships putting in are searched for wine by Theobald "
            "Butler's agents and pay Walter de Lacy's customs and "
            "imposts, yet trade from Scandinavia, Iceland and all the "
            "British Isles never stops. Mellifont Abbey stands near by."
        ),
    )
    w["trim"] = b.town(
        "Trim",
        charter="Noble lord",
        ruler="Walter de Lacy",
        answers_to=lord,
        place=meath,
        summary="Home of the Cenél Lóegairi túath and, above all, of Trim "
        "Castle, the largest stone castle in Ireland, which Walter de "
        "Lacy raised on a hill to govern Meath in place of the "
        "ringwork his father built and the Irish destroyed. De Lacy "
        "and his household are often here. Saint Patrick's church of "
        "Saint Lommán and Saint Malachy's Augustinian abbey of Saint "
        "Mary stand in the town. The castle was lately the scene of a "
        "strange affair, the tale of the Three Sisters of Trim.",
        secrets=[
            titled(
                "Storyguide Notes",
                "The book names the Three Sisters of Trim but tells nothing more of them: the storyguide decides what happened.",
            )
        ],
    )
    w["kells_town"] = b.town(
        "Kells",
        charter="Church",
        ruler="The abbot of Kells, comarba Columcille",
        answers_to=w["kells_abbey"],
        place=meath,
        summary=(
            "An Irish town grown round Saint Columba's monastery and "
            "ruled by its abbot (Kells in Meath, not Kells in Leinster). "
            "It gave its name to the synod of 1152 that remade the Irish "
            "Church, and keeps the Book of Kells."
        ),
    )


# ---------------------------------------------------------------- Ostmen


def _ostmen(hibernia: Hibernia, b: Builder) -> None:
    hibernia.world["ostmen"] = b.faction(
        "The Ostmen",
        faction="People or tribe",
        decides="Councils of the leading families in each city",
        place=hibernia.places.get("ireland"),
        wants="Their trade, their quarters in the ports and their standing apart",
        offers="Ships, sea trade with Scandinavia and Iceland, and knowledge of the ports",
        summary=paragraphs(
            "The Norse of Ireland's port towns, 'Eastmen' from the lands "
            "they came from. Viking raiders who began wintering in Ireland "
            "in the ninth century made the island's first cities out of "
            "their winter camps, the longphorts: Dublin, Waterford, "
            "Wexford, Cork and Limerick, which are Ostman homes still. "
            "When the raiding stopped and the Irish had learned to use "
            "Norse weapons as well as the Norse, the two settled into an "
            "uneasy peace; the Ostmen became Christian and married into "
            "the Irish, ruling their towns as a warrior elite. The English "
            "invasion ended Norse rule of the ports, but the Ostmen remain "
            "a people apart.",
            "The Finn-Gaill, 'white foreigners', of Dublin now speak "
            "Leinster Gaelic; the Dubh-Gaill, 'black foreigners', of "
            "Wexford, Limerick, Waterford and Cork still speak the "
            "Norwegian dialect of West Norse. In Dublin they have moved "
            "north across the Liffey since the English came. Their rune "
            "wizards, whom the Order called the 'Order of Odin' in 832, "
            "fought the Hibernian magi in many indecisive skirmishes but "
            "never in open war.",
        ),
    )


# ----------------------------------------------------------------- books


def _book(hibernia: Hibernia, name: str, **kw: Any) -> Book:
    """A book the chapter names that no covenant owns: it files under the
    saga, and the place that keeps it says where it is."""
    saga = hibernia.b.saga
    ability = kw.get("ability", "")
    book = Book(
        id=storage.generate_unique_id(name, [x.id for x in saga.books]),
        name=name,
        subject_kind="Ability" if ability else "",
        **kw,
    )
    saga.books.append(book)
    return book


def _books(hibernia: Hibernia, b: Builder) -> None:
    kells = hibernia.world["kells_abbey"]
    book_of_kells = _book(
        hibernia,
        "The Book of Kells",
        type="Ability Summa",
        ability="Theology",
        level=5,
        quality=9,
        language="Latin",
        description=secrets(
            "A gorgeously illuminated Gospel book in Latin, written in "
            "Irish minuscule, which any magus would prize. Some say Saint "
            "Columba wrote it. It is kept at the monastery of Kells under "
            "close guard since a theft in the eleventh century. Studied, "
            "it is a summa of quality 9 on Theology (level 5) and on "
            "Dominion Lore (level 3), and it may hold more.",
            "Gerald of Wales was right: an angel wrote it in Heaven.",
        ),
    )
    b.link(kells, "books", book_of_kells, "Kept here under close guard")
    psalter = _book(
        hibernia,
        "The Battle Psalter of the Ó Domhnaill",
        type="Other",
        language="Latin",
        description=(
            "A fine old psalter that the Ó Domhnaill clan of Donegal carry "
            "into battle (the book calls it their 'scathach'), left at the "
            "monastery of Kells for safe keeping by one of the family. The "
            "book gives it no rules."
        ),
    )
    b.link(kells, "books", psalter, "Left here for safe keeping")
    for name, latin in (
        ("Topographia Hibernica", "The Topography of Ireland"),
        ("Expugnatio Hibernica", "The Conquest of Ireland"),
    ):
        _book(
            hibernia,
            name,
            type="Tractatus",
            ability="Area Lore: Ireland",
            quality=8,
            language="Latin",
            author="Gerald of Wales",
            description=(
                f"'{latin}', one of the two books Gerald of Wales "
                "(Giraldus Cambrensis) wrote about riding with the first "
                "English invaders: a tractatus on Area Lore (Ireland), "
                "quality 8. Gerald blames the island itself for its "
                "people's ills and paints the Irish as handsome but wild: "
                "children left to grow up untended, scanty clothes, bare "
                "feet, long hair and beards, quick to anger and revenge, "
                "unreliable in their word, fighting without armour with "
                "short spears, javelins and the axe every man carries. "
                "His book alarmed the Stonehenge magi into noticing "
                "Hibernia. In 1220 Gerald is 74 and lives at Hereford, "
                "near the Welsh border."
            ),
        )


# ---------------------------------------------------------------- finish


def finish(hibernia: Hibernia) -> None:
    """Put Meath in Ireland, tie the churches to Armagh once the Church
    part has made it, and write the island's land, people and law into
    Ireland's notes."""
    ireland = hibernia.places.get("ireland")
    meath = hibernia.places["meath"]
    if ireland is not None:
        if meath.place_id is None:
            meath.place_id = ireland.id
        w = hibernia.world
        for key in ("henry_iii", "regent", "viceroy", "itinerant_justices", "ostmen"):
            record = w.get(key)
            if record is not None and record.place_id is None:
                record.place_id = ireland.id
        ireland.summary = paragraphs(ireland.summary, IRELAND_NOTES)
    armagh = hibernia.world.get("armagh")
    if armagh is not None:
        for key in (
            "mellifont",
            "bective",
            "kells_abbey",
            "trim_abbey",
            "clonmacnoise_abbey",
        ):
            church = hibernia.world.get(key)
            if church is not None and church.answers_to is None:
                church.answers_to = armagh.id


#: Chapter three's account of the island, for Ireland's notes.
IRELAND_NOTES = paragraphs(
    "The land. Ireland is shaped like a bowl: a rim of low mountains along "
    "most of the coast round rolling plains and deep forest, threaded with "
    "rivers and spotted with lakes. It is milder and wetter than England; "
    "snow is rare and never lies more than three days, rain falls more in "
    "the west than the east (three days in five, some say), and floods "
    "can wash out the spring sowing. Apple, hazel and oak forests shelter "
    "boar, wolves, deer, foxes, badgers, hares and squirrels, and the "
    "outlaws and fiannai (bands of young nobles living wild while they "
    "wait for their inheritance, to prove themselves); many outlaws today "
    "did nothing worse than hold land an Englishman wanted, and their "
    "neighbours call them heroes. One Area Lore (Ireland) covers the whole "
    "island, four days' walk from coast to coast and eight from the "
    "northern tip to the southern; its specialties are a province, a clan's history, a "
    "line of kings, legends or old feuds.",
    "Land and lordship. The Irish reckon land in cantreds, each in a clan "
    "chief's keeping. The English bundle cantreds into Liberties, "
    "heritable fiefs, and shires, the king's cities and their country; a "
    "lord of a Liberty keeps its rents and taxes and is freer, while a "
    "shire's keeper is the king's agent and sends him most of the money, "
    "though the trade of a city can make him the richer man.",
    "Cattle. Cows are wealth, power and honour; raising them and lifting "
    "them from others are the heart of Irish life. Herds move to high "
    "summer pasture and low winter pasture, and are shut in roofed byres "
    "at night against the wolves. A man must keep a herd fit for his "
    "rank, so a raid costs honour as well as beasts, and getting stolen "
    "cattle back from a stronger man depends on allies. Grain is a small "
    "part of a farm's yield (oats, then wheat and rye), sown in unfenced "
    "fields that last two harvests; cattle may lawfully cross a field to "
    "reach water, and fencing them from it is a crime.",
    "The túath. Irish society rests on the clan, a lineage claiming a "
    "heroic ancestor, and its unit is the túath, 'people', which means "
    "its land, its free and unfree clients and its slaves as well as its "
    "kin. Most túatha date from the fourth and fifth centuries; a strong "
    "leader may break away to found a new one, and a weak one is "
    "destroyed or swallowed. About 125 exist in 1220. The greatest are the "
    "five bloods: Ulster's Ua Néill, Meath's Máel Sechnaill, Connacht's Ua "
    "Conchobair, Leinster's Mac Murchadha and Munster's Ua Briain.",
    "Ranks. The daorcheile, those without honour, are slaves, unfree "
    "farmers and the poorest free farmers; the grád flatha, those with "
    "honour, are rich free farmers, nobles, clergy and the learned "
    "professions. A bothach, unfree, takes a cow and a plot from his lord "
    "for labour and goods on terms he can never pay off; a bóaire, free, "
    "gets terms he can. Nobles rise from lesser nobles, with the fewest "
    "client farmers, through cattle lords to greater nobles; the "
    "derbfine, everyone within four generations of the chief, are the "
    "clan's core. A rí tuaithe rules one túath, a fuirig or over-king "
    "holds others as clients, a rí ruirech is king of over-kings and a rí "
    "cóicid a provincial king (an English baron, earl and duke in turn, "
    "though the Irish rank a provincial king higher). There has been no "
    "ard rí, high-king, since the English came. Judges, poets and "
    "physicians are mostly hereditary, trained as long as a university "
    "master, and a great king names an ollamh to head each. Each túath "
    "meets in its oireacht at set places and seasons to settle disputes, "
    "fines and taxes and, when needed, to choose a king from the derbfine, "
    "sometimes naming a tánaise ríg, heir apparent, in advance. A king is "
    "wed to the tribal land in a sacred rite, in some túatha to a local "
    "Tuatha Dé land goddess.",
    "Eraic. Every free man has an honour-price, eraic, paid to him in "
    "cows for any harm to body, name, connections or goods; a slight "
    "costs a good share of it, a killing the whole. In play it is a "
    "Reputation within his túath (for example Eraic 1, Ua Riain túath). "
    "His herd should number twelve times his eraic and his blood-price is "
    "six times it, both doubled for the five bloods; lesser wrongs cost a "
    "share the troupe decides. Starting eraic follows Social Status: a "
    "slave (the Slave Flaw) and a bothach (Peasant) have none; a bóaire "
    "(Peasant and Wealthy, or Knight and Poor) has 1; a lesser noble is a "
    "Gentleman at 2 or a Knight at 3; a cattle lord (Landed Noble) has 5, "
    "6 if also a Knight; a king (Greater Noble) has 7. Wealthy adds 1 and "
    "Poor takes 1 away, and a Poor Knight falls to bóaire. Climbing a rung "
    "takes 10 Gratitude Points (Lords of Men). The Irish have no title "
    "for a knight, but the rank is the lowest of the grád flatha.",
    "Law and custom. The Brehon Laws are civil law, on marriage, "
    "hostages, fostering, rank and clientship; they set the share of the "
    "victim's eraic a wrong costs, and how big a man's house and herd may be, "
    "but give no king power to punish, so the wronged must collect for "
    "themselves. Only one marriage in twenty is made in church; a couple "
    "need only declare it, divorce and remarriage are easy, cousins wed, "
    "the groom pays a bride-gift, every son not born of a slave inherits, "
    "and marriage binds no alliance. Nobles give sons as hostages to a "
    "king, whose lives are forfeit if the túath breaks faith; noble "
    "children are fostered from seven to seventeen (girls to fourteen) and "
    "a foster-son is a son in all but inheritance. Every superior owes "
    "hospitality, a meal and a bed, and a monastery three nights; a mean "
    "host risks a satire, or a demon, and a lord's clients owe him cuddy, "
    "a night's feasting, when he goes on circuit.",
    "Settlements. Villages are ráths, palisades round wooden huts, set "
    "away from rivers and roads and movable with the clan; there are "
    "nearly a thousand. Monastic ráths enclose a stone church and round "
    "tower. The Ostmen founded the only cities, Dublin, Waterford, Wexford, "
    "Cork and Limerick; the great churches (Armagh, Cashel, Kildare, Tuam "
    "and Dublin) and royal seats have turned to stone walls.",
    "The year. Winter begins at Samhain (1 November), when on its eve "
    "ghosts and faeries are abroad and the Tuatha Dé move to their winter "
    "halls; summer begins at Bealtaine (1 May), a good day for year-long "
    "charms. Lughnasa (the Sunday nearest 1 August) is the harvest feast "
    "and Oímelg (1 February) the Feast of Saint Brighid. Ireland is wholly "
    "Christian, though: at Easter the sun dances, granting +1 to a pious "
    "Personality Trait for the week to all who see it, and on Christmas "
    "night beasts can speak until dawn, which it is very bad luck to hear.",
    "Pastimes. Poets and musicians pass freely between Irish and English "
    "halls (love songs are in fashion), which makes a poet a fine spy, and "
    "Performance Magic is common among Hibernian wizards, though native "
    "poets resent a magus taking their part. Irish youths of every rank "
    "play hurling, which the English shun and faeries love (a good player "
    "may be stolen for a night's faerie match); Athletics covers it, and a "
    "hurley hits as a club. Horses race riderless; fidhcheall uses "
    "Etiquette, or Carouse at -2, and táiplis (backgammon) is an English "
    "lord's game.",
    "Languages. Gaelic, with Munster, Connacht, Ulster and Leinster "
    "dialects (Meath has none of its own); Anglo-Norman French for the "
    "lords; English in many dialects for their servants; West Norse among "
    "the Ostmen of the southern ports; and Latin for the learned. A speaker "
    "of another dialect of the same tongue is at -1. Some Gaelic-speaking "
    "magi give their Houses Irish forms: Ua for the four lineages (Ua "
    "Bonaoságas), cultas for the four Mystery Cults (cultas Meriníte), and "
    "a byname for the societates (an Flambó, an t-Iarbiteon, an Taotalas, "
    "an t-Éigse Measceal); old accounts call House Diedne Deoradach, 'the "
    "banished'.",
    "The English opposition. The English prize land and the Irish prize "
    "cattle: Irish wars took herds, not territory, while the English build "
    "stone towers to keep what they take. Irish sons share their father's "
    "land and herd, worked together for five years and then divided by the "
    "youngest; the English give everything to the eldest, and an "
    "Englishman who marries an Irish heiress expects her father's lands "
    "and title, which her kin deny. An Irish king's son has no right to "
    "the throne, which the derbfine bestows, and an over-king cannot "
    "overturn his client king's rulings, where an English king's law runs "
    "over every lord. The settlers are failing to plant French feudalism "
    "on the clans and are instead going native, 'more Irish than the Irish "
    "themselves'.",
    "The Chief Bard. The ard-ollamh Érenn, Chief Bard of Ireland, is the "
    "high-king's own poet and king of the bards: he judges between bards "
    "and others, sets the fashions of verse and tale, and alone may strip "
    "a bard of rank; only a man whose father and grandfather were bards "
    "may hold it. The last, Giolla Ernain Ua Martain, died in 1218, and the "
    "seat has stood empty since.",
)
