"""Connacht, the western province closed to the Order, as of 1220: the
province (places["connacht"]), shut to covenants by the Treaty of Cnoc
Maol Réidh; the kingdom of Bréifne (places["breifne"]) and the kingdom
of Connacht, with King Cathal (world["cathal"]), tributary to the Lord
of Ireland under the Treaty of Windsor, and the clans beneath them; the
see of Triburnia under Armagh and the dioceses of Tuam, with their
bishops, abbeys and holy places; the gazetteer of the province, from
Glencar and the Stags of Broadhaven to the Aran Isles, with its auras
and vis; the Pact of Oireadh, eight druids meeting at Oireadh
(places["oireadh"]), whose members are told in the faction's summary
(hedge traditions are not modelled); the covenant of Praesis on Lough
Ree, Ballack's since the siege, its cathach the Gáe Bulg, and its magi;
Meadhbh, its old leader, in sanctuary at Qui Sonant; and Faolán of Ex
Miscellanea, living in Connacht against the Treaty, with no covenant.
In paraphrase of The Contested Isle chapter five.

Keys: the covenant is covenants["praesis"], its island
places["praesis"] inside places["lough_ree"]; its magi are
magi["ballack"], ["baetain"], ["guillaume"] and ["cacht"], with Oscar
von Harz, the spear's guardian, as the companion magi["oscar"];
magi["meadhbh"] (covenant Qui Sonant) and magi["faolan"] (none). The
Black Pig's Dyke and the Slieve Aughty are shared with the Ulster and
Munster chapters: `finish` adds Connacht's part to the place those parts
made, or makes it when they have not."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from ..builder import Builder
    from . import Hibernia

TYTALUS = "house_tytalus"
TREMERE = "house_tremere"
FLAMBEAU = "house_flambeau"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}

#: The two churches of Ireland, as each church record names its own.
IRISH = "Of the Irish church."
ANGLO_IRISH = "Of the Anglo-Irish church."


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(hibernia: Hibernia, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = hibernia.b.place(name, **kw)
    hibernia.places[key] = place
    return place


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    _region(hibernia)
    _breifne(hibernia)
    _north_and_west(hibernia)
    _tuam_and_the_west(hibernia)
    _elphin_and_the_east(hibernia)
    _the_south(hibernia)
    _aran(hibernia)
    _lords(hibernia, b)
    _churches(hibernia, b)
    _towns(hibernia, b)
    _oireadh(hibernia, b)
    tribunal = hibernia.tribunal or next(iter(b.saga.tribunals), None)
    if tribunal is not None:
        _praesis(hibernia, b, tribunal)
    _meadhbh_and_faolan(hibernia, b)


# ------------------------------------------------------------- the region


def _region(hibernia: Hibernia) -> None:
    _add(
        hibernia,
        "connacht",
        "Connacht",
        inside=hibernia.places.get("ireland"),
        summary=paragraphs(
            "The western province of Ireland, beyond the Sionainne "
            "(Shannon), which serves as its eastern border; Ulster lies "
            "north of it, Meath and Leinster east, Munster south. Its "
            "coasts to the north, west and south are all cliffs, inlets "
            "and islands with good harbours, where villages live off the "
            "sea and graze beasts on the slopes; inland there are plains "
            "in the middle, ridges of mountain to the north, west and "
            "south, wide peat bogs in the north and west, and lakes "
            "without number. The great rivers are the Muaidhe (Moy), the "
            "Gaillimhe and the Sionainne. The land is fertile.",
            "Closed to covenants. By the Treaty of Cnoc Maol Réidh the "
            "Order may found no covenant here, and no magus may stay "
            "more than three nights running under a Connacht sky or "
            "roof, even at a druid's invitation. Every hedge wizard in "
            "the province counts as one of the Coill Trí, who must hand "
            "seven Gifted Connachta children to the Order at each "
            "Tribunal; the druids resent the tithe as the Fir Bolg once "
            "resented the Fomórach's, and as the kings resent the "
            "English tribute. Whether the Treaty's Connacht ends at the "
            "Sionainne or takes in all the lands its kings rule (Bréifne "
            "reaches far east of the river) is unsettled. Younger magi "
            "with continental ideas see an untouched prize here.",
            "Rule. The kingdom of Connacht rules the province and takes "
            "fealty from the kingdom of Bréifne in the north. Both have "
            "kept the English out so far, guarding their borders hard, "
            "but both pay tribute to the English and rule by agreement. "
            "The Connachta clans descend from Conn of the Hundred Battles "
            "and are cousins of the Uí Néill. The Uí Briúin rose five "
            "centuries ago through their friendship with the druids; "
            "their branches are the Uí Briúin Bréifne (the rival Uí "
            "Ruairc and Uí Raghallaigh) and the Uí Briúin Ai, whose Uí "
            "Conchobhair hold the crown. The older Uí Fiachrach and the "
            "fading Uí Maine sing of the days when they ruled. The last "
            "of the Fir Bolg live on the Aran Isles.",
            "Magic. Few places in Ireland are so magical. Magic and "
            "Faerie auras are everywhere, and hedge wizards prosper even "
            "inside the Dominion. Vis is common but rarely plentiful in "
            "one place, much of it extraordinary vis, with herbs and "
            "things of virtue the druids use. The nobles keep and "
            "consult druids, and few would block one's road; druids who "
            "read omens warn that within a generation the English may "
            "cross the border.",
            "Booleys and crannógs. Many villages move with the seasons "
            "after their herds or the harvest, leaving booleys, rough "
            "huts lived in for a season or two; between times faeries "
            "use them, and a traveller who shelters in one when they are "
            "home may never leave. Crannógs, lake dwellings raised on "
            "timber and stone, once held homes and whole villages; most "
            "now stand empty, given over to faeries and druids.",
            "Vis (each in its place): Glencar's healing water "
            "(spell-like), the Lough Conn hills (spell-like), Omey's "
            "holy well (Divine).",
        ),
        **KNOWN_ORDER,
    )


# ---------------------------------------------------------- Bréifne


def _breifne(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    breifne = _add(
        hibernia,
        "breifne",
        "Bréifne",
        inside=connacht,
        summary=paragraphs(
            "The northern kingdom, subject to Connacht, stretching from "
            "Sligo on the western sea nearly to Kells in the east, with "
            "Ulster to its north and Meath to its east. It crosses the "
            "Sionainne, which is why the Treaty's reach here is in "
            "doubt: no covenant stands in Bréifne, and the Coill Trí "
            "claim all of it. Lough Allen splits its western half, "
            "mountains to the north and gentle plain to the south-east. "
            "Most of its people live by its brief stretch of sea, round "
            "Lough Allen, or beside the Sionainne and the Erne.",
            "Few people and wild, unspoilt country leave Bréifne full "
            "of Magic auras rooted in the land's own beauty, with little "
            "pull from the other realms. West Bréifne, the Uí Ruairc's, "
            "is wooded and ringed by high mountains, rich in boar, deer, "
            "game birds, wolves and eagles; East Bréifne, the Uí "
            "Raghallaigh's, is hemmed in by Ulster, Meath and Leinster "
            "and feels English pressure, yet keeps many magical places "
            "and strong magic.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "glencar",
        "The Glencar Waterfall",
        inside=breifne,
        aura=4,
        summary=(
            "A fifty-foot fall in the north-west of Bréifne that runs "
            "clean all year. Its beauty anchors a strong Magic aura (4; "
            "the book gives no number), and its water is said to wash "
            "and heal wounds, the work of the spell-like vis in the fall. "
            "No one holds it."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "cavan_crannogs",
        "The Crannógs of Cavan",
        inside=breifne,
        aura=2,
        summary=(
            "A tangle of small lakes north and north-west of Cavan, "
            "many with crannógs. Most are overgrown and look like "
            "islets near the shore; fishermen and booley folk still use "
            "a few. Some were druids' homes, and their Magic auras (2; "
            "the book gives no number) have not yet faded. With a little "
            "work they would make a covenant site, easy to defend and "
            "near markets, but they lie east of the Sionainne in lands "
            "the Coill Trí call Connacht's."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "druim_leatan",
        "Druim Leatan",
        inside=breifne,
        realm="Infernal",
        aura=4,
        summary=paragraphs(
            "The ridge between the Uí Ruairc and the Uí Raghallaigh, "
            "with a priory on it that marks the line between the two "
            "halves of Bréifne. The priory itself is in a Dominion aura "
            "of 6, but the ridge round it has a malevolent Infernal "
            "aura that at times reaches 4, and demons there urge both "
            "clans to raid and avenge; the priory, as the border's "
            "emblem, is often sacked. Magh Slécht lies some miles west.",
            "If history runs its course, Bréifne splits along this line "
            "in 1256, both halves still subject to Connacht.",
        ),
        **KNOWN_REGION,
    )


# --------------------------------------------- Killala, Achonry and Mayo


def _north_and_west(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    _add(
        hibernia,
        "stags_of_broadhaven",
        "The Stags of Broadhaven",
        inside=connacht,
        realm="Faerie",
        aura=3,
        levels=[
            hibernia.b.level(
                "The Otherworld of the western shore",
                6,
                "Faerie",
                enter="Through the cave that runs right through one of the islands",
                notes="The realm of the Tuatha Dé who rule the Atlantic coast.",
            )
        ],
        summary=(
            "Sheer island rocks off the far north-west coast in the "
            "diocese of Killala, thick with seabirds. A cave passes "
            "clean through one of them: it is a regio's way into the "
            "Otherworld of the Tuatha Dé who hold the Atlantic shore. "
            "The dolphins and seals of the bay are their messengers and "
            "envoys. Faerie 3 outside and 6 within (the book gives no "
            "numbers)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "lough_gara",
        "Lough Gara",
        inside=connacht,
        realm="Faerie",
        summary=(
            "A lake near Sligo that covers a drowned village. A faerie "
            "widow with a baby begged at every door one night and was "
            "turned away by all; leaving, she cursed the place, and the "
            "brook rose and drowned the sleepers in their beds. Magi "
            "after ghosts of the drowned, or spirits of regret, may still "
            "find them on the lake bed. The book gives no aura."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "cnoc_na_re",
        "Cnoc na Ré",
        inside=connacht,
        realm="Faerie",
        aura=3,
        summary=(
            "A hill at the western end of the Cúil Irra peninsula, two "
            "miles from Sligo, between Sligo Bay and Ballisodare Bay, "
            "among rolling hills covered in stone circles and tombs. On "
            "its top is an enormous cairn of loose stone, some 180 feet "
            "across and about 35 high: the grave of Queen Maedhbh, "
            "buried standing and facing north-east toward Ulster in case "
            "its men try their luck. Her body lies here, but her spirit "
            "keeps court at Cruachan. Faerie 3 (the book gives no aura)."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "drumcliffe",
        "Drumcliffe",
        inside=connacht,
        summary=(
            "A village north of Sligo Bay, where the old druid Bran "
            "Bodhar spends his days in a round tower. He truly has the "
            "gift of divination, sometimes seeing as far as the next "
            "day, but he is deaf and cannot read, so anyone who comes to "
            "ask him must bring great patience and small hopes. No aura "
            "is given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "binn_ghulbain",
        "Binn Ghulbain",
        inside=connacht,
        summary=(
            "A flat-topped mountain seen from all round Sligo: 1,700 "
            "feet of steep grass and then a sudden cliff. The Fianna, "
            "Finn mac Cumhail's young landless warriors, kept here, and "
            "some say their spirits still do, lending their deeds to "
            "whoever will make the climb. No aura is given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "loch_na_sul",
        "Loch na Súl",
        inside=connacht,
        aura=2,
        summary=(
            "The Lake of the Eye. When Lugh's sling-stone burst Balor's "
            "eye at the second battle of Mag Tuired, its fire scooped a "
            "hollow in the ground and the falling giant's blood filled "
            "it. The blood is long gone, but a shard of the eye remains "
            "in the lake and is the source of its Magic aura of 2. A "
            "covenant wanting a cathach could take the shard, and the "
            "aura would die."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "maol_reidh",
        "Maol Réidh",
        inside=connacht,
        aura=2,
        summary=(
            "Cnoc Maol Réidh, Connacht's highest mountain at over 2,500 "
            "feet, falling steeply into Killary Harbour, with thin "
            "woods on its flanks: the mountain that names the Treaty. "
            "Its beauty gives it a weak Magic aura (2), built up by "
            "centuries of spells cast on its top and strongest (3) where "
            "it looks over the harbour; the book gives no numbers. The "
            "view from it reaches far across the land, which some spells "
            "can use."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "neifinn",
        "Néifinn",
        inside=connacht,
        aura=2,
        summary=(
            "Connacht's second mountain, also over 2,500 feet, named for "
            "Nemed of the ancient invasions. Its Magic aura (2) rises "
            "toward the summit (3), where druids have long stood to cast "
            "their spells; the book gives no numbers. Like Maol Réidh it "
            "commands a wide view, and Lough Conn can be seen from it."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "lough_conn",
        "Lough Conn",
        inside=connacht,
        aura=2,
        levels=[
            hibernia.b.level(
                "Umor's hiding place",
                4,
                "Magic",
                see="Not from outside",
                enter="By day, where Umor Ard sleeps; he can be found outside it only by night",
            )
        ],
        summary=paragraphs(
            "Lough Conn and Lough Cullin, joined to it, make a chain of "
            "water nearly ten miles long that empties to the Atlantic by "
            "the Muaidhe (Moy), a river lined with rich churches. They "
            "say a magic boar fleeing Fionn mac Cumhaill and his hounds "
            "Conn and Cullin poured water from its feet as it ran until "
            "the lakes formed and drowned the hounds; it was never "
            "caught, and roams the Faerie realm still, unseen in the "
            "mortal world since.",
            "The hills above the lake are full of spell-like vis of "
            "every kind (unheld; the hedge druid Umor Ard Mac Adar of "
            "the Pact of Oireadh lives here), in a Magic aura of 2, "
            "with a hidden regio of 4 where Umor sleeps by day; the book "
            "gives no numbers.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "dooncarton",
        "The Stones of Dooncarton",
        inside=connacht,
        realm="Faerie",
        aura=4,
        summary=(
            "Dooncarton is a village of shellfish farmers below the high "
            "cliffs south of Sruwaddacon Bay, with a small church, a "
            "devout flock and a strong Dominion. A short walk out, on "
            "the slopes of Caubeen Mountain above it, stands a ring of "
            "seven stones, four feet high and no more than ten across, "
            "in a strong Faerie aura (4; the book gives no number)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "achill",
        "Achill Island",
        inside=connacht,
        aura=2,
        summary=(
            "A mountainous island: Croaghaun, over 2,000 feet, drops "
            "from its northern face straight into the Atlantic, "
            "Slievemore stands to its east, and more mountains fill the "
            "south. The wild land gives the whole island a Magic aura "
            "(2; the book gives no number), broken only by the Dominion "
            "round its church bells. Farmland is scarce, so most of the "
            "inland people move with the seasons between booleys. Its "
            "harbours, sheltered by cliffs, are Keel and Keem in the "
            "west and Cashel in the east."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "clew_bay",
        "Clew Bay",
        inside=connacht,
        realm="Faerie",
        aura=1,
        summary=(
            "A great bay guarded at its mouth by mountainous Clare "
            "Island and inside by drumlins, small drowned hills whose "
            "tops just break the water. Some call them faerie whales "
            "that swim free at high tide and turn to stone as it ebbs; "
            "certainly no one who counts them twice on different days "
            "gets the same number. Faerie 1 (the book gives no aura)."
        ),
        **KNOWN_LOCALLY,
    )
    croagh = _add(
        hibernia,
        "croagh_patrick",
        "Croagh Patrick",
        inside=connacht,
        realm="Divine",
        aura=5,
        summary=paragraphs(
            "A mountain of more than 2,000 feet looking over Clew Bay, "
            "above Murrisk and Lucanvey, some four miles out of "
            "Westport. Saint Patrick fasted forty days and nights on its "
            "top while the she-demon Caoranach plagued him with a cloud "
            "of crows and every snake in Ireland; at the end he flung a "
            "silver bell into the air, and its noise scattered the crows "
            "and drove the serpents out of the island for good.",
            "A great pilgrimage site in a strong Divine aura (5; the "
            "book gives no number), ringed by shrines to Patrick, with a "
            "small church on the summit. Its roads are dangerous: "
            "robbers, faeries and demons all test pilgrims bound for "
            "Lough Nacorra, trials that serve as opposition for a "
            "pilgrimage (The Church's pilgrimage rules).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "lough_nacorra",
        "Lough Nacorra",
        inside=croagh,
        realm="Divine",
        aura=3,
        summary=(
            "The lake below Croagh Patrick where Caoranach fell when "
            "the bell struck her from the sky. Its Divine waters held "
            "her for a time; when she broke free, Patrick tracked her to "
            "Lough Derg near Donegal and destroyed her there. Divine 3 "
            "(the book gives no number)."
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------- Tuam and Connemara


def _tuam_and_the_west(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    _add(
        hibernia,
        "mag_tuired",
        "The Field of the First Battle of Mag Tuired",
        inside=connacht,
        summary=(
            "Near Cong, where the Tuatha Dé beat the Fomórach in the "
            "first battle. Woods have grown over most of it, and magical "
            "and faerie relics of the fight may still lie under the "
            "trees. No aura is given."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "lough_gaillimhe",
        "Lough Mask and Lough Gaillimhe",
        inside=connacht,
        realm="Faerie",
        summary=(
            "Lough Mask, the lesser lake, drains into the great Lough "
            "Gaillimhe (Corrib), and that into the sea; streams under "
            "Cong join the two. Manannán mac Lir of the Tuatha Dé claims "
            "Lough Gaillimhe as his own, so when the Friar's Cut, a "
            "canal from the lake through the settlement round the Dún "
            "to the Atlantic, was dug, the druids of Tuam had to agree "
            "its course with him. The book gives no aura."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "dun_bhun_na_gaillimhe",
        "Dún Bhun na Gaillimhe",
        inside=connacht,
        realm="Infernal",
        aura=2,
        summary=paragraphs(
            "A fort at the mouth of the Gaillimhe (Corrib), facing south "
            "over Loch Lurgain, built by Tairrdelbach Uí Conchobhair in "
            "1124 as a naval base, guarded by bog to the north and wide "
            "tidal mud to the south and east. It never was strong: hard "
            "to supply and easy to batter, it was razed by Munster "
            "raiders after the cattle of the Maigh Seola in 1132 and "
            "again in 1149, and it keeps the same flaws today. Something "
            "Infernal hangs over it (Infernal 2; the book gives no "
            "number).",
            "If history runs its course, the Normans attack the fort "
            "and its settlement again and again once they enter "
            "Connacht, about 1230.",
        ),
        **KNOWN_REGION,
    )
    connemara = _add(
        hibernia,
        "connemara",
        "Connemara",
        inside=connacht,
        summary=(
            "The country west of Lough Gaillimhe, split north from south "
            "by the short range of the Twelve Bens; the feuding families "
            "of each half think the line matters greatly. The Ó Cadhla "
            "rule it, but families from Leinster and Munster pushed out "
            "by the English are coming west looking for land. No aura is "
            "given."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "clifden",
        "Clifden",
        inside=connemara,
        realm="Faerie",
        summary=(
            "A village where the Owenglen River meets Clifden Bay, its "
            "hills scattered with barrows and stone tombs. Unlike most "
            "Irish folk, its people no longer fear or honour the Tuatha "
            "Dé, and have carried stones from the cairns and graves to "
            "build houses and churches. The Tuatha Dé are furious, and "
            "both worlds need a go-between. No aura is given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "omey",
        "Omey Island",
        inside=connemara,
        realm="Divine",
        aura=3,
        summary=(
            "A tidal island reached on foot across the sands at low "
            "water, where the villagers race ponies all August, a time "
            "for trading, friendship and courting. Saint Feichin's "
            "monastery here is failing and may be abandoned unless new "
            "patrons come, but its stone church is sound, and its holy "
            "well has a Divine aura of its own (3; the book gives no "
            "number) and yields Divine vis. Vis: the holy well, Divine "
            "(no one holds it)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "inishbofin",
        "Inishbofin and Inishark",
        inside=connemara,
        summary=(
            "Twin islands some five miles off Connemara under a strange "
            "magical curse: for all their mild weather and good food, "
            "those who live there age faster than mainlanders (a -1 "
            "Living Conditions penalty). Ruins of monks who died out "
            "with no one to follow them litter the islands, the latest "
            "Saint Colman's monastery on Inishbofin, gone since the "
            "tenth century. Whether something like the Aegis of the "
            "Hearth could shield settlers from the curse would take "
            "research. No aura is given."
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------- Elphin and Lough Ree


def _elphin_and_the_east(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    b = hibernia.b
    _add(
        hibernia,
        "cruachan",
        "Cruachan",
        inside=connacht,
        realm="Faerie",
        aura=3,
        levels=[
            b.level(
                "Queen Maedhbh's court",
                6,
                "Faerie",
                enter="By a way into the regio among the ruins of the ráth",
                notes="Her spirit still holds court here, and kings, princes and druids seek her out.",
            )
        ],
        summary=paragraphs(
            "Rathcroghan, the Ráth of Cruachan, near Tulsk, from which "
            "Queen Meadhbh ruled ancient Connacht. Only ruins and worn "
            "banks are left of her fortress, but a way still leads into "
            "the Faerie regio that holds her court. Mounds and barrows "
            "surround it, and from them monsters, beasts and faerie folk "
            "break into the mortal world, most of all at Samhain; druids, "
            "nightwalkers among them, guard the villages round about. "
            "Faerie 3 outside and 6 in the court (the book gives no "
            "numbers).",
            "Queen Maedhbh: the scheming, lustful queen of legend knew "
            "every magic for ruling a man's mind and heart, and death has "
            "not taken her power. She offers it to kings, princes and "
            "druids who give themselves to her, and loves Connacht "
            "jealously: if the men of Ulster attack, she may bring an "
            "army out of the Otherworld against them.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "rathbeg",
        "Rathbeg",
        inside=connacht,
        summary=(
            "A small group of barrows nine miles north of Roscommon, "
            "where Fir Bolg warriors slain in battle were laid long "
            "before Saint Patrick made their people Christian. Their "
            "spirits sleep on below, waiting for someone to call them. "
            "No aura is given."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "castlestrange",
        "The Castlestrange Stone",
        inside=connacht,
        summary=(
            "A lone egg-shaped stone a yard long near Athleague, on a "
            "gentle slope, carved all over with a single winding line. "
            "There is no aura, but those who have touched it call it "
            "unnatural, so few would move it. A larger, more upright "
            "stone at the Rath of Fir Mhor near Bullaun bears almost the "
            "same design; studied together, the two might give up the "
            "carvings' meaning."
        ),
        **KNOWN_LOCALLY,
    )
    lough_ree = _add(
        hibernia,
        "lough_ree",
        "Lough Ree",
        inside=connacht,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "A long lake on the Sionainne between Connacht and Meath. "
            "Its western shore is a faerie trod: the shoreline has a "
            "Faerie aura of 5 and can carry a traveller to several other "
            "trods across Connacht. Annaghmore lies on the western side, "
            "Agharanagh on the eastern. The covenant of Praesis stands "
            "on a wooded island out in the water, and the villages of "
            "both shores now fear its magi and their men.",
            "During the siege of Praesis, Ballack's forces camped on "
            "the eastern shore.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "praesis",
        "The Island of Praesis",
        inside=lough_ree,
        aura=2,
        levels=[
            b.level(
                "The tower's regio",
                3,
                "Magic",
                see="The mortal world sees only the island and its rubble",
                notes="The new tower and the Gáe Bulg on its platform stand here, warded.",
            )
        ],
        summary=(
            "A wooded island in Lough Ree, far enough from either shore "
            "that a spell at Voice range cannot reach it, chosen because "
            "it lies between the Coill Trí's land and the Order's. The "
            "rubble of the first tower and its outbuildings is strewn "
            "about, and the trees, burnt and broken in the siege, are "
            "greening again. Magic 2 (the book gives no number). The "
            "island lies in the lake, not on the Connacht shore, so the "
            "covenant stands outside the Treaty's Connacht."
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------- Cill Mhic Dhuach and Clonfert


def _the_south(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    _add(
        hibernia,
        "fir_mhor",
        "The Rath of Fir Mhor",
        inside=connacht,
        aura=1,
        levels=[
            hibernia.b.level(
                "The true Rath",
                3,
                "Magic",
                enter="It comes down into the mortal world when the nightwalkers gather",
                notes="Palisade and buildings entire.",
            )
        ],
        summary=(
            "A great ring fort close to Bullaun village and the bigger "
            "town of Loughrea. Local nightwalkers use it to guard "
            "the harvest from storm spirits, faeries after their cattle "
            "and plagues the Infernal sends on the wind: at such times "
            "the true Rath, palisade, buildings and all, comes down out "
            "of the Magic regio that usually hides it, and from it they "
            "shield the land for about twenty miles round. A yard-high "
            "rounded stone covered in a swirling line stands here, kin "
            "to the Castlestrange Stone, perhaps with the same "
            "enchantments. Magic 1 outside, 3 in the regio (the book "
            "gives no numbers)."
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------------------- the Aran Isles


def _aran(hibernia: Hibernia) -> None:
    connacht = hibernia.places["connacht"]
    aran = _add(
        hibernia,
        "aran_isles",
        "The Aran Isles",
        inside=connacht,
        summary=(
            "Three islands off Gaillimhe Bay, in the small diocese of "
            "Annaghdown, home to the last Fir Bolg of Ireland, one tribe "
            "to each island. Driven west into Connacht by the Tuatha Dé "
            "and then out to the islands by the Milesians, they now serve "
            "the kings of Connacht as counsellors of long memory. All but "
            "the Fir Domhnann are Christian, converted by Saint Patrick. "
            "No aura is given for the isles as a whole."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "arainn_mhor",
        "Árainn Mhór",
        inside=aran,
        summary=paragraphs(
            "The largest and westernmost island, seat of the Fir Bolg "
            "royal line. King Rudraige Ua Sláine lives in Dún Aonghasa, "
            "a huge old ring-fort of four dry-stone walls on a clifftop, "
            "built by Aonghus mac Úmhór when the Fir Bolg came into exile "
            "in Connacht; three lesser forts built the same way (Dún "
            "Eoghanachta, Dún Dubhchathair and Dún Eochaill) house other "
            "royal kin, and the rest live in clóchan, beehive huts of "
            "dry stone. A dozen monasteries hold human and Fir Bolg monks "
            "together. Ruaidhri Uí Conchobhair came here for counsel "
            "before he made his peace with the English.",
            "The Brannock Islands, two islets to the west: one is the "
            "island Gerald of Wales wrote of, where the dead are left "
            "in the open and never rot, so a man may go there and look "
            "on any number of his forefathers; no mouse can live there "
            "either, and any brought over drown themselves or drop dead. "
            "The magi of Qui Sonant long to learn more of it, but the "
            "Treaty keeps them out of Connacht.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "arainn_meain",
        "Árainn Meáin",
        inside=aran,
        summary=(
            "The middle island, home of the Fir Domhnann, smallest of "
            "the three tribes, who all live inside the Dun Chonchuir "
            "ring-fort. They feel their Fomóir blood and worship the "
            "Fomóir goddess Domnu, whose power their druids channel; "
            "they have never forgiven the rule of men, since their "
            "ancestor Gannan was the one given Connacht to rule when "
            "the Fir Bolg first came. There is no church here and no "
            "Divine aura; the book gives no other aura."
        ),
        **KNOWN_REGION,
    )
    thiar = _add(
        hibernia,
        "arainn_thiar",
        "Árainn Thiar",
        inside=aran,
        summary=(
            "The smallest island, home of the Fir Gaileoin, Christian in "
            "name but hardly practising; the island has a single church. "
            "No aura is given."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "tempull_bheanain",
        "Tempull Bheanáin",
        inside=thiar,
        realm="Divine",
        aura=2,
        levels=[
            hibernia.b.level(
                "The great church",
                5,
                "Divine",
                enter="By stepping through the oratory's door",
                notes="A terrestrial regio: the church inside is vast and wondrous, and no harm can come to anyone within.",
            )
        ],
        summary=(
            "A tiny oratory on a high ridge in the south-east of Árainn "
            "Thiar that looks like a deserted ruin. Step through into the "
            "terrestrial regio over it and the church is large and "
            "overwhelmingly lovely, and nothing can harm those inside. "
            "Divine 2 outside and 5 within (the book gives no numbers)."
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------------ the lords


def _lords(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    connacht = hibernia.places["connacht"]
    breifne = hibernia.places["breifne"]
    w["cathal"] = b.lord(
        "Kingdom of Connacht",
        title="duke",
        wealth="Average",
        manors=60,
        ruler="Cathal Uí Conchobhair",
        place=connacht,
        summary=paragraphs(
            "King Cathal Uí Conchobhair, of the Uí Briúin Ai, who rules "
            "Connacht and takes Bréifne's fealty as a tributary of the "
            "English: under the Treaty of Windsor, signed on 6 October "
            "1175, the kings of Connacht hold their crown in return for "
            "a yearly tribute to the Lord of Ireland, still paid. His "
            "half-brother Ruaidhri, the last free king and the last "
            "High-King of Ireland, rose by hard politics, arms and the "
            "druids' help; his exile of Mac Murrough brought the English "
            "in and lost the other four provinces. Taking the counsel of "
            "Fionntan from the Fir Bolg kings of Árainn Mhór (that a "
            "tribute can be borne or escaped), he made terms, gave up the "
            "high-kingship and died a monk at Cong in 1198. The see of "
            "Tuam matches the kingdom's bounds and so props up its "
            "authority.",
            "The kings guard the Sionainne fiercely and crush any raid "
            "across it. The Templars were given land at Ballymote to "
            "shield the kingdom, and the king may think of giving the "
            "Order land for the same reason, to steer who settles in "
            "Connacht; his druids advise strongly against it.",
            "Tribute owed: a yearly tribute to the Lord of Ireland "
            "(Treaty of Windsor).",
            "If history runs its course, Cathal reigns until 1224, when "
            "his son Aedh follows him, and the high-kingship is never "
            "restored, though two attempts are made.",
        ),
    )
    w["ualgarg"] = b.lord(
        "Kingdom of Bréifne",
        title="count",
        wealth="Average",
        manors=25,
        ruler="Ualgarg Uí Ruairc",
        answers_to=w["cathal"],
        place=breifne,
        summary=paragraphs(
            "King Ualgarg Uí Ruairc, sworn to Connacht. The crown of "
            "Bréifne passes by choice, not birth: the men of the Uí "
            "Briúin Bréifne pick a king from the male line, and "
            "claimants have often blinded or gelded rivals to bar them; "
            "its politics are still savage. The Uí Ruairc in the west "
            "and the Uí Raghallaigh in the east, rich, strong and "
            "fiercely served, have fought over it time and again, each "
            "with friends inside Connacht and beyond; the Uí "
            "Conchobhair back the Uí Ruairc. The English meddle from "
            "outside the province.",
            "Tribute owed: fealty to the king of Connacht.",
            "If history runs its course, Ualgarg loses the throne for a "
            "year in 1228 to his cousin Niall, wins it back when Niall "
            "dies, and keeps it until his own death in 1231; in 1256 "
            "the clans' feud splits Bréifne in two along Druim Leatan, "
            "both halves still under Connacht.",
        ),
    )
    w["ui_raghallaigh"] = b.lord(
        "The Uí Raghallaigh",
        title="baron",
        wealth="Average",
        manors=12,
        answers_to=w["ualgarg"],
        place=breifne,
        summary=paragraphs(
            "The clan of East Bréifne, the Uí Ruairc's great rivals for "
            "its crown, pressed by the English and their Irish vassals "
            "on three sides. One of their nobles shelters a witch who "
            "has bewitched a farmer's son.",
            "If history runs its course, Cathal Uí Raghallaigh takes "
            "Walter de Lacy's castle at Kilmore in 1224 and pulls it "
            "down.",
        ),
    )
    w["o_cadhla"] = b.lord(
        "The Ó Cadhla",
        title="landed",
        wealth="Average",
        manors=6,
        answers_to=w["cathal"],
        place=hibernia.places["connemara"],
        summary=(
            "The clan that rules Connemara, facing families driven out "
            "of Leinster and Munster by the English who now seek new "
            "land in the west."
        ),
    )
    w["mac_diarmaid"] = b.lord(
        "The Mac Diarmaid",
        title="landed",
        wealth="Wealthy",
        manors=6,
        answers_to=w["cathal"],
        place=connacht,
        summary=(
            "A rich family near Boyle, patrons of its Cistercian abbey. "
            "Unlike the other nobles of the region they have often "
            "spurned druids' advice, and since 1161 no druid has been "
            "allowed at their court."
        ),
    )
    w["o_sheachnasaigh"] = b.lord(
        "The Ó Sheachnasaigh",
        title="landed",
        wealth="Wealthy",
        manors=4,
        seat="Gort",
        answers_to=w["cathal"],
        place=connacht,
        summary=(
            "A family of the Uí Fiachrach whose busy stronghold is Gort, "
            "beside Cill Mhic Dhuach Monastery, in a diocese grown rich "
            "but too weak in arms to stop raiders crossing from Munster."
        ),
    )
    w["ui_fiachrach"] = b.faction(
        "The Uí Fiachrach",
        faction="Family",
        decides="Its leader",
        place=connacht,
        wants="The rule of Connacht they once held",
        offers="Old songs, long memories and a rich southern diocese",
        summary=(
            "The clan that ruled Connacht for generations before the Uí "
            "Briúin overtook them, and whose songs still tell of it; "
            "they hold the middle and west of the province, and Cill "
            "Mhic Dhuach is their ancestral country. Among their "
            "families are the Ó Cléirigh and the Ó Sheachnasaigh."
        ),
    )
    w["ui_maine"] = b.faction(
        "The Uí Maine",
        faction="Family",
        decides="Its leader",
        place=connacht,
        wants="To hold their Sionainne lands as their power wanes",
        offers="Fighting men on the eastern border",
        summary=(
            "The clan that drove the Fir Bolg west when it took their "
            "lands by the Sionainne; its strength has faded of late, and "
            "the Fir Bolg still bear it a grudge. The Ó Fallamháin, the Ó "
            "Ceallaigh and the Ó Domhnalláin are among its families."
        ),
    )


# ------------------------------------------------------------ the Church


def _churches(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    connacht = p["connacht"]
    w["bishop_triburnia"] = b.church(
        "Diocese of Triburnia",
        church="Bishop's cathedral",
        ruler="Bishop Flann Ó Connachtaig",
        place=p["breifne"],
        summary=(
            f"{IRISH} The see of Bréifne, also called Kilmore, whose "
            "bounds are the kingdom's and whose bishop sits at Kilmore. "
            "It answers to Armagh, not Tuam, which ignores Bréifne's "
            "subjection to Connacht and has been quarrelled over ever "
            "since. Bishop Tuathal Ua Connachtaig caused an uproar in "
            "1172 when, as Bishop of Kells, he swore fealty to Henry II, "
            "and the Church seems a party to opening Bréifne to the "
            "English, something newcomer magi might exploit. The present "
            "bishop, Flann Ó Connachtaig, is a scholar with no wish to "
            "stand against English influence."
        ),
    )
    w["druim_leatan_priory"] = b.church(
        "Druim Leatan Priory",
        church="Monastery or nunnery",
        answers_to=w["bishop_triburnia"],
        place=p["druim_leatan"],
        summary=(
            f"{IRISH} The priory on the ridge between the Uí Ruairc and "
            "the Uí Raghallaigh, a holy island in an evil land and often "
            "sacked as the emblem of the border."
        ),
    )
    w["bishop_killala"] = b.church(
        "Diocese of Killala",
        church="Bishop's cathedral",
        place=connacht,
        summary=(
            f"{IRISH} The north-western tip of Connacht, mostly "
            "mountain with few people, wide inland marshes and peat "
            "bog; the Stags of Broadhaven lie off its coast. The book "
            "does not name its bishop."
        ),
    )
    w["bishop_achonry"] = b.church(
        "Diocese of Achonry",
        church="Bishop's cathedral",
        place=connacht,
        summary=(
            f"{IRISH} The see round Sligo, cut off from Killala by a "
            "mountain ridge and from Bréifne by nothing but goodwill, so "
            "its people must keep both the Uí Ruairc and the Uí "
            "Conchobhair kings content. The book does not name its "
            "bishop."
        ),
    )
    w["mayo_clergy"] = b.church(
        "Diocese of Mayo",
        church="Parish church",
        place=connacht,
        summary=paragraphs(
            f"{IRISH} A see that is no more: a papal legate dissolved it "
            "in 1202 and gave its lands and monasteries straight to "
            "Tuam, and Pope Innocent III confirmed it in 1216, but its "
            "clergy still resist and would take their case to Rome. "
            "Croagh Patrick, Aughagower and Achill lie in its old lands.",
            "If history runs its course, another legate confirms the "
            "dissolution in 1221 and Pope Gregory IX does so finally in "
            "1240.",
        ),
    )
    w["croagh_patrick_church"] = b.church(
        "The Church on Croagh Patrick",
        church="Chapel",
        answers_to=w["mayo_clergy"],
        place=p["croagh_patrick"],
        summary=(
            f"{IRISH} A small church on the summit where Patrick "
            "fasted, the goal of pilgrims, amid shrines to the saint."
        ),
    )
    w["aughagower"] = b.church(
        "Aughagower",
        church="Parish church",
        answers_to=w["mayo_clergy"],
        place=connacht,
        summary=(
            f"{IRISH} A village church on the pilgrims' road in "
            "Patrick's steps. In a slim tower in its grounds lives a "
            "druid whose power is Divine, a lone cantor who blesses "
            "travellers whose faith is wavering and who need a sign "
            "they are on the right road (the Cantores of Realms of "
            "Power: The Divine)."
        ),
    )
    w["cong_abbey"] = b.church(
        "Cong Abbey",
        church="Monastery or nunnery",
        order="Augustinian",
        place=connacht,
        summary=paragraphs(
            f"{IRISH} Founded by Saint Deichin early in the seventh "
            "century; its monks lately took the Augustinian rule and "
            "left the old Celtic ways. Burnt early in the twelfth "
            "century, rebuilt about 1135, sacked by the English knight "
            "William de Burgh in 1203 though it lies deep in Connacht, "
            "and rebuilt again. Ruaidhri Uí Conchobhair retired here "
            "after giving up the high-kingship.",
            "The Cross of Cong, a golden processional cross that "
            "Tairrdelbach Uí Conchobhair had made nearly seventy years "
            "ago, is a reliquary of a fragment of the True Cross (3 "
            "Faith Points). It was meant for Tuam's cathedral and came "
            "here when the abbey was last rebuilt.",
        ),
    )
    w["bishop_elphin"] = b.church(
        "Diocese of Elphin",
        church="Bishop's cathedral",
        ruler="Bishop Dionysius Ó Mórda",
        place=connacht,
        summary=(
            f"{IRISH} The eastern edge of Connacht, along the Sionainne, "
            "whose people watch the far bank for the English. Saint "
            "Patrick made Elphin a see when the druid Ono, lord of these "
            "lands, was converted and gave him his castle for a "
            "monastery. Many of its men have died fighting for the "
            "druids against those of Leinster, and they fear an English "
            "attack will follow. Bishop Dionysius Ó Mórda has little "
            "patience or sympathy for druids."
        ),
    )
    w["boyle_abbey"] = b.church(
        "Boyle Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        answers_to=w["bishop_elphin"],
        place=connacht,
        founded=1160,
        summary=(
            f"{IRISH} A Cistercian house not sixty years old, built "
            "with the wealth of the Mac Diarmaid and still being built; "
            "its church was consecrated only in 1218. It is the "
            "Cistercians' third try at a site in Connacht, where they "
            "have struggled to take root."
        ),
    )
    w["bishop_annaghdown"] = b.church(
        "Diocese of Annaghdown",
        church="Bishop's cathedral",
        place=connacht,
        summary=(
            f"{IRISH} A small see with few people, which matters because "
            "Ireland's Fir Bolg on the Aran Isles fall within it. The "
            "book does not name its bishop."
        ),
    )
    w["aran_monasteries"] = b.church(
        "The Monasteries of Árainn Mhór",
        church="Monastery or nunnery",
        answers_to=w["bishop_annaghdown"],
        place=p["arainn_mhor"],
        summary=(
            f"{IRISH} A dozen monasteries on the largest Aran island, "
            "where human and Fir Bolg monks live side by side."
        ),
    )
    w["bishop_cill_mhic_dhuach"] = b.church(
        "Diocese of Cill Mhic Dhuach",
        church="Bishop's cathedral",
        place=connacht,
        summary=(
            f"{IRISH} The old home of the Uí Fiachrach in the south, "
            "rich now but too weak in arms to keep out raiders from "
            "Munster. The book does not name its bishop."
        ),
    )
    w["cill_mhic_dhuach_monastery"] = b.church(
        "Cill Mhic Dhuach Monastery",
        church="Monastery or nunnery",
        answers_to=w["bishop_cill_mhic_dhuach"],
        place=connacht,
        summary=paragraphs(
            f"{IRISH} A monastery beside Gort that has grown in standing "
            "over the past century: a fine stone church and other "
            "buildings, and a tall round tower with a marked lean to the "
            "east. They say no one in this diocese can be killed by "
            "lightning.",
            "If history runs its course, its wealth sees it plundered "
            "many times in the thirteenth century.",
        ),
    )
    w["bishop_clonfert"] = b.church(
        "Diocese of Clonfert",
        church="Bishop's cathedral",
        place=connacht,
        summary=(
            f"{IRISH} The south-eastern see, whose cathedral grew from "
            "the older monastery, its church begun about 1180. A "
            "magical stonemason carved the great arch round its doors so "
            "beautifully that supernatural beasts of every realm came to "
            "watch him, and the stone still bears the faces of those who "
            "came. The book does not name its bishop."
        ),
    )
    w["omey_monastery"] = b.church(
        "Saint Feichin's Monastery, Omey",
        church="Monastery or nunnery",
        place=p["omey"],
        summary=(
            f"{IRISH} Saint Feichin's foundation on Omey Island, hard "
            "pressed in recent years and likely to be abandoned without "
            "new patrons; its stone church is sturdy and its holy well "
            "gives Divine vis."
        ),
    )
    w["temple_house"] = b.church(
        "The Temple House at Ballymote",
        church="Monastery or nunnery",
        order="Knights Templar",
        place=connacht,
        founded=1181,
        summary=(
            "Of neither Irish church: a house of the Knights Templar, "
            "Connacht's only one, under their own order. A plain square "
            "castle with no keep, built in 1181 on the edge of "
            "Ballymote, ten miles south of Sligo and five west of Lough "
            "Arrow, close enough to Bréifne to provoke. A few foreign "
            "Templars and many Connachta lay brothers live in it. The "
            "kings granted the land about forty years ago for politics' "
            "sake, as a shield against anyone with designs on Bréifne."
        ),
    )


# -------------------------------------------------------------- towns


def _towns(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    connacht, breifne = p["connacht"], p["breifne"]
    king = w["cathal"]
    w["sligo"] = b.town(
        "Sligo",
        charter="Noble lord",
        ruler="Cathal Uí Conchobhair",
        answers_to=king,
        place=connacht,
        summary=(
            "A town on the Sligeach estuary, home to fishermen who "
            "gather the shellfish along its shore; the river comes down "
            "from Lough Gill, a lake some six miles long. It has no "
            "walls, castle, abbey or cathedral, only many small "
            "religious houses scattered round about. Lough Gara, Cnoc na "
            "Ré, Drumcliffe and Binn Ghulbain are near."
        ),
    )
    w["carrick"] = b.town(
        "Carrick",
        charter="Noble lord",
        ruler="Ualgarg Uí Ruairc",
        answers_to=w["ualgarg"],
        place=breifne,
        summary=(
            "A small Bréifne town at a natural ford of the Sionainne, "
            "with a soldierly air: if the English ever invaded Connacht, "
            "both sides would race to hold it, for it commands the "
            "supply road. The Black Pig's Dyke passes west and south of "
            "it."
        ),
    )
    w["kilmore"] = b.town(
        "Kilmore",
        charter="Church",
        answers_to=w["bishop_triburnia"],
        place=breifne,
        summary=paragraphs(
            "The seat of the bishop of Triburnia, twenty miles east of "
            "the Sionainne and a couple of miles from Cavan, guarded by "
            "a motte-and-bailey castle Walter de Lacy raised in 1211, "
            "one of many he has built to push into Connacht. The Black "
            "Pig's Dyke encloses Kilmore and Cavan on the west, north "
            "and east, about five miles out on each side.",
            "If history runs its course, Cathal Uí Raghallaigh seizes "
            "the castle in 1224 and razes it, the fate of many of de "
            "Lacy's castles.",
        ),
    )
    w["cavan"] = b.town(
        "Cavan",
        charter="Noble lord",
        answers_to=w["ui_raghallaigh"],
        place=breifne,
        summary=(
            "A town of East Bréifne just south-east of a cluster of "
            "small lakes full of crannógs, a couple of miles from "
            "Kilmore."
        ),
    )
    w["ballymote"] = b.town(
        "Ballymote",
        charter="Noble lord",
        ruler="Cathal Uí Conchobhair",
        answers_to=king,
        place=connacht,
        summary=(
            "A town that has done better since the Templars built their "
            "castle beside it: it keeps off the bandits that used to "
            "trouble it, and supplying the knights keeps its merchants "
            "busy."
        ),
    )
    w["tuam_town"] = b.town(
        "Tuam",
        charter="Church",
        place=connacht,
        summary=paragraphs(
            "A city whose political weight is fading. The Uí Conchobhair "
            "built a castle here in 1164 to tighten their hold on "
            "Connacht, but it has gone downhill since: it has five "
            "monasteries and several high crosses, yet its cathedral "
            "burnt down in 1184 and, with the king's abdication in 1185 "
            "and the strain on the borders, nobody has rebuilt it. Its "
            "markets and fairs thrive and its merchants grow rich, but "
            "the great men have left, and an archbishop without a "
            "cathedral presides over ground some would call ripe for the "
            "Infernal.",
        ),
    )
    w["cong"] = b.town(
        "Cong",
        charter="Church",
        answers_to=w["cong_abbey"],
        place=connacht,
        summary=(
            "A town on an island made by the streams that flow round it, "
            "above underground channels that link Lough Mask to Lough "
            "Gaillimhe, near the field of the first battle of Mag Tuired "
            "and home to its abbey. A rich nobleman of Cong keeps the "
            "druid Ádhamh Brathair, who works his magic for the noble "
            "and his family."
        ),
    )
    w["elphin"] = b.town(
        "Elphin",
        charter="Church",
        answers_to=w["bishop_elphin"],
        place=connacht,
        summary=(
            "A pious town south of Carrick and north of Boyle. When "
            "Patrick came through, the druid Ono ruled here; converted, "
            "he gave the saint his land and castle for a monastery, and "
            "a spring of pure water that broke out at Patrick's miracle "
            "still runs through the town."
        ),
    )
    w["boyle"] = b.town(
        "Boyle",
        charter="Noble lord",
        answers_to=w["mac_diarmaid"],
        place=connacht,
        summary="The Mac Diarmaid's town, with its new Cistercian abbey.",
    )
    w["roscommon"] = b.town(
        "Roscommon",
        charter="Noble lord",
        ruler="Cathal Uí Conchobhair",
        answers_to=king,
        place=connacht,
        summary=(
            "A market town with charters aplenty and many roads through "
            "it, yet strangely listless. Every three years ill luck "
            "comes back: three years ago an Ollamh singer was driven "
            "out, three before that the church bell cracked, three "
            "before that a magical swan was killed. Whatever the cause, "
            "something like a fog is settling over its people."
        ),
    )
    w["athlone"] = b.town(
        "Athlone",
        charter="Noble lord",
        ruler="Walter de Lacy",
        place=connacht,
        summary=paragraphs(
            "The English foothold in Connacht, ten miles south-east of "
            "Roscommon below Lough Ree, at an old ford: south of here "
            "the Sionainne cannot be crossed until Clonmacnoise, so the "
            "place has always mattered. Tairrdelbach Uí Conchobhair "
            "built a bridge and ring fort a century ago; John de Gray, "
            "Bishop of Norwich, justiciar from 1209 to 1212, put a stone "
            "castle in the fort's place ten years ago. Walter de Lacy "
            "now holds it with a small garrison, and the English keep "
            "the great stone bridge that links Meath and Leinster with "
            "Connacht. The town thrives under English rule, its market "
            "selling goods hard to find in the west, and the trade of "
            "the Sionainne and the Great Highway passes through. The "
            "castle keeps Connachta armies out of Meath but not the "
            "small bands that slip across the river to try themselves "
            "against the English.",
            "At night the banshee's dreadful cry is often heard here, "
            "for many local families carry the death omen; those who "
            "hear it weep and mourn, but a quick-witted listener who "
            "learns which kinsman is doomed can sometimes turn the death "
            "aside.",
        ),
    )
    w["gort"] = b.town(
        "Gort",
        charter="Noble lord",
        answers_to=w["o_sheachnasaigh"],
        place=connacht,
        summary=(
            "The bustling stronghold of the Ó Sheachnasaigh in the "
            "south, beside Cill Mhic Dhuach Monastery."
        ),
    )


# -------------------------------------------------- the Pact of Oireadh


def _oireadh(hibernia: Hibernia, b: Builder) -> None:
    connacht = hibernia.places["connacht"]
    oireadh = _add(
        hibernia,
        "oireadh",
        "Oireadh",
        inside=connacht,
        summary=(
            "A village where the druids of the Pact of Oireadh meet "
            "every season, no more than two days' journey for any of "
            "them. Its villagers are well paid for their hospitality and "
            "loyal; they know where to reach each druid, eye strangers "
            "asking after them (-1 to social rolls with them), and "
            "quietly send word to Mór Greannach at nearby Carrowmore. "
            "The book gives no aura."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "carrowmore",
        "Carrowmore",
        inside=connacht,
        summary=(
            "The village near Oireadh where Mór Greannach lives, "
            "gathering herbs and things of virtue from the hills and "
            "woods round it."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "rosbeg",
        "Rosbeg",
        inside=connacht,
        summary=(
            "A coastal village west of Oireadh, where Tuathal an "
            "Iarrainn keeps a well-equipped smithy and workshop with two "
            "mundane apprentices."
        ),
        **KNOWN_LOCALLY,
    )
    hibernia.world["pact_of_oireadh"] = b.faction(
        "The Pact of Oireadh",
        faction="Hedge coven",
        decides="A council",
        members=8,
        ruler="Ádhamh Brathair",
        realm="Magic",
        place=oireadh,
        rules="Druids of every tradition sit as equals; members keep apart but for the seasonal meeting; the research stays secret",
        wants="A single theory of the magics of Ireland, and the protection it would bring",
        offers="Healing, divination, bound spirits and forged wonders, herbs of virtue, and wide contacts among the hedge folk",
        summary=secrets(
            paragraphs(
                "Eight druids of mixed traditions, sworn to work "
                "together toward a single theory of their magic. Unlike "
                "the Order they make no distinction of tradition: witch, "
                "learned magician, goetic sorcerer and Fir Bolg all sit "
                "together as equals. They do not live together but "
                "meet each season at Oireadh, each keeping an aura that "
                "suits his own magic; living apart blunts the Gift's "
                "ill will, which bites only face to face, and their "
                "helpers and messengers, often met on the roads of the "
                "region, carry word between them. They help one another "
                "in magic and in worldly affairs, live mostly in "
                "Connacht, and have no love for the English. Hedge "
                "traditions are not modelled: the druids are told here.",
                "History. Praesis was once where Connacht's hedge "
                "wizards met the Ordo Hiberniae, and long talk there made "
                "some of them wonder what the magi kept from them. These "
                "druids were Praesis's allies until Meadhbh asked too "
                "much of them; they left her, and began asking what gave "
                "the Order its strength and what shielded it while lesser "
                "wizards fell.",
                "Ádhamh Brathair (55, looks 55; Charismatic +3, "
                "Determined +2, Cautious +1), a Gifted learned magician "
                "whose lineage goes back to Bologna, master of "
                "experimental philosophy, in minor orders, kept by a "
                "rich nobleman of Cong. He thought of the Pact and leads "
                "its research, which he knows will outlast him; he would "
                "like the glory but works for the greater good. Wary of "
                "how close the Coill Trí stand to the Ordo Hiberniae, he "
                "tells them little, the more so since they took a Gifted "
                "child from him for the Order's tithe.",
                "Umor Ard Mac Adar (Autumn, looks 50; Magic Might 25; "
                "Gentle +3, Independent +2, Idealistic +1), a "
                "transformed Fir Domhnann, one of the few to leave "
                "Árainn Meáin, still faithful to Domnu: bigger than any "
                "man, with a second pair of arms from his sides for his "
                "Fomóir blood, otherwise nearly handsome; his blood gives "
                "him Might and the power to heal. Bitter at his people's "
                "exile, he helps Ádhamh to win the favour of men so the "
                "Fir Domhnann may one day return to the mainland; some "
                "of his kind call him a traitor. He fears humans but "
                "trusts Ádhamh, and often calms quarrels between the "
                "Gifted members. He lives in the hills above Lough Conn "
                "and can be found only at night.",
                "Mór Greannach, 'grey-beard' (75, looks 75; Mischievous "
                "+3, Meddling +2, Trustworthy -1), a folk witch named for "
                "the thin beard on her chin, who has spent her long life "
                "serving her community and is as feared and mistrusted "
                "as she is honoured and asked for help. She knows the "
                "magical world deeply and enriches the herbs and objects "
                "of virtue she gathers. She has the widest acquaintance "
                "of the Pact: her coven, scores of nightwalkers, "
                "faerie-touched craftsmen, Ollamhain and the Kilkenny "
                "coven in Leinster. She lives closest to Oireadh, at "
                "Carrowmore.",
                "Tuathal an Iarrainn (40, looks 40; Honest +3, "
                "Disciplined +2), a goetic sorcerer, master of the Ars "
                "Goetica that summon, bind and command spirits; some "
                "mistrust his magic and its source, but he never hides "
                "what he is. A master smith of Rosbeg, he binds spirits "
                "into what he forges, and lately commands them at "
                "Ádhamh's asking to hunt for things the research needs.",
                "The other four members are not named. The Coill Trí "
                "and the Ordo Hiberniae both know the Pact as a fellowship "
                "of druids; its research is kept from both.",
            ),
            _lines(
                "The Pact's true aim is a Parma Magica of its own; the Order knows nothing of it.",
                "Ádhamh's vision is a theory of magic that takes in every Irish tradition and gives every practitioner each tradition's defences: a breakthrough of at least 120 points (the Original Research rules of Houses of Hermes: True Lineages). He has 15. So far he has made amulets, after the Folk Witch tradition, that give their wearer Second Sight, Dowsing or Cursing at a score of 4 for a season; they have shown him how his own magic differs from the witches', and by learning those Abilities he hopes to gain their small magical defences. His notes are hidden for those who come after him.",
                "The Gifted child the Coill Trí took from Ádhamh is now an apprentice in a Hermetic covenant, and he may yet ask her to report on summoners she meets.",
                "Tuathal's goetic arts are Infernal at root, though he does not hide them and Ádhamh has not yet seen it. His Goetic master has just died in Dublin, leaving him a book of Infernal Lore on particular demons.",
                "Umor's three cousins have sworn to kill him for leaving Árainn Meáin.",
            ),
        ),
    )


# -------------------------------------------------------------- Praesis


def _praesis(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    island = hibernia.places["praesis"]
    summary = paragraphs(
        "A winter covenant in a stone tower on a wooded island in Lough "
        "Ree, between Connacht and Meath. Its device is a spear made of "
        "thigh bones with a skeletal hand. Once the shining proof of "
        "friendship between the Order and the druids of Ireland, it was "
        "left to its fate by the Tribunal and taken in a year's siege by "
        "Ballack of Tytalus and the foreign magi with him; it now leans "
        "to the English. Some see in it the danger of outsiders, others "
        "proof that Hibernia must change, and its new masters must "
        "somehow drag it out of its winter.",
        "Its cathach is the Gáe Bulg, a spear of the thigh bones of the "
        "monstrous witch Coinchenn, whom Art son of Conn killed, tipped "
        "with her clawed right hand. When it pierces a target the hand "
        "clamps on bone or gut and will not let go until the victim "
        "dies. Whoever holds it gains the Death Prophecy Virtue; each "
        "prophecy differs, but every one begins with the spear being "
        "lost. The witch was hideous and cruel, her daughter lovely and "
        "good: foreseeing that she would die on the day her daughter "
        "was won, she kept the girl close and set the heads of suitors "
        "on the stakes round her house.",
        "The tower is cold and bare; from almost every window the ruined "
        "laboratories of the siege can be seen. A council meets weekly "
        "to track where Meadhbh and her friends are and what they "
        "intend, and to keep the defences ready in case they come back. "
        "Holzner's head still hangs from the palisade where Meadhbh put "
        "it. For two seasons Guillaume has been telling the others of "
        "promising sites his spies have found over the Connacht border, "
        "and the shifting crowd of foreign magi newly come to Hibernia "
        "who stay here is looking west with growing interest.",
        "The country round shuns it: the villages of both shores serve "
        "it only grudgingly, and anyone tied to Praesis counts as "
        "Infamous, with a bad Reputation of 4. Mundanes will not help, "
        "and the Coill Trí warn hedge wizards against it.",
    )
    what_matters = _lines(
        "Cathach: the Gáe Bulg, held by Ballack's Praesis since the siege",
        "Vis: the covenant's own sources round the island and the lake, stripped bare by Ballack's besiegers and slow to recover",
        "Vis (contested): sources over the Connacht border that Guillaume's Bréifne mercenaries seek out and raid",
        "Income: none yet; Ballack lives on vis and casting tablets borrowed from distant benefactors, and needs the covenant to pay its way soon",
        "Right: by the Treaty, its members may enter Connacht in pursuit of Hermetic justice, at Manannán mac Lir's express request, or to find bees for their hives",
        "Library: no books are named; what the fire and the siege left is unknown",
        "Boon: Island (a wooded island in Lough Ree, beyond Voice range of both shores)",
        "Boon: Regio (Minor) (the tower and the spear stand in a warded regio)",
        "Boon: Veteran Fighters (Guillaume's turb of Bréifne mercenaries)",
        "Hook: Infamous (the villages of Lough Ree fear its people)",
        "Hook: Indebted (Major) (Ballack's debts of vis and favours)",
        "Hook: Crumbling (the ruins of the old tower and laboratories)",
        "Hook: Death Prophecies (the Gáe Bulg)",
        "Hook: Rival (Major) (Meadhbh and the magi who fled with her)",
        "Hook: Hermetic Politics (the extended Wizard War, and whether the Gáe Bulg may be shown in 1221)",
        "Tension: Báetáin shares the tower with Guillaume, who burnt the people he grew up among",
        "Tension: Guillaume's raids into Connacht could break the Treaty for everyone",
    )
    notes = paragraphs(
        "History. Praesis was founded where Connacht meets Meath, not "
        "long after the Treaty of Cnoc Maol Réidh, as a meeting place for "
        "the Order and Connacht's hedge wizards. Within a century that "
        "purpose was nearly forgotten and its standing was already "
        "falling. Its druid allies, later the Pact of Oireadh, left "
        "Meadhbh when her demands outgrew their friendship.",
        "The siege. In spring 1213 Praesis took in, warily, a foreigner "
        "from the continent, Holzner of Tytalus. He stole the cathach "
        "and fled; his sodales caught and killed him, and Meadhbh hung "
        "his head by the hair from the palisade. His parens Ballack "
        "came from the Rhine for justice and, arguing that if the "
        "Tribunal would not punish Praesis it must be taken by force, "
        "declared Wizard War and struck. Praesis held. From the eastern "
        "shore Ballack's people stripped its vis sources and killed "
        "anyone going in or out, which kept Praesis from the Tribunal "
        "of 1214, where it might have found allies. For a full year of "
        "stalemate mercenaries and several young magi on both sides "
        "died while the covenants of Hibernia argued; magic and men "
        "were evenly matched, but Ballack's nerve lasted longer. As "
        "Praesis's last allies fled, Báetáin Ua Traimair made terms: "
        "the Gáe Bulg for Meadhbh's safe passage. She took sanctuary at "
        "Qui Sonant Pro Quieto, and Ballack has held Praesis since. Not "
        "all the besiegers were foreign; some were sons of old Irish "
        "lines who saw the war as a blow against centuries of "
        "tradition. The new tower was raised by Hermetic ritual.",
        "The cathach in 1221. Praesis did not show its cathach at the "
        "Tribunal of 1214. Ballack has now held the Gáe Bulg for years, "
        "well beyond the year a thief must keep a cathach, but whether "
        "a cathach given up as the price of a truce may be presented "
        "by the men who besieged its covenant, and whether the Wizard "
        "War that won it should be challenged, are both open questions "
        "for the next meeting; its new masters expect no trouble.",
        "Covenfolk: barely any yet beyond the conquerors' own servants, "
        "except Guillaume's turb of Bréifne mercenaries, who serve him "
        "for good pay and plenty of food, fighting, drink and women, "
        "and whom the country round has learned to dread. Oscar von "
        "Harz, a white-haired man of giant's blood, fearless and wholly "
        "loyal to Ballack, guards the Gáe Bulg, standing on a wooden "
        "platform that looks toward Meath with the spear held out as a "
        "dare; by custom it is kept outside the Aegis of the Hearth.",
        "Six magi live here, four of them named, and two apprentices; "
        "one is the apprentice Guillaume took with the cathach of an "
        "independent magus. The book gives no founding year: 855 is "
        "assumed, soon after the Treaty was signed in 851.",
        secrets(
            "What the players do not know.",
            _lines(
                "The tower and the spear stand in a regio, out of mortal sight, warded and guarded by magic: the platform the world sees is not where the spear truly is.",
                "Oscar has seen his own death through the Gáe Bulg. No one knows what he saw; since taking the spear he has been studying the legends of the Fir Bolg.",
                "Ballack's distant benefactors are a powerful cult or society he does not belong to but took help from; they may soon send someone to remind him of what he owes.",
            ),
        ),
    )
    praesis = b.covenant(
        "Praesis",
        tribunal=tribunal,
        founded=855,
        place=island,
        level=1,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=2,
        detail=FULL,
        season="Winter",
    )
    hibernia.covenants["praesis"] = praesis
    hibernia.cathaigh["praesis"] = {
        "cathach": "The Gáe Bulg, a spear of the witch Coinchenn's thigh bones and clawed hand",
    }
    b.book(
        praesis,
        "The library of Praesis",
        "Other",
        language="Latin",
        description=(
            "The book names no books at Praesis. What the old covenant "
            "kept from its centuries of dealings with Connacht's druids "
            "may have burned in the siege or gone with Meadhbh; the new "
            "masters have brought little, and Ballack is too poor to buy."
        ),
    )
    m = hibernia.magi
    m["ballack"] = b.magus(
        "Ballack",
        covenant=praesis,
        house=TYTALUS,
        age=80,
        summary=paragraphs(
            "Lord of Praesis, a Tytalus from the Rhine who looks "
            "sixty-five; Holzner was his filius. He delighted in "
            "turning Hibernia's own customs on the Irish and taking his "
            "revenge on Meadhbh, yet it says something of him that "
            "Holzner's head still hangs from the palisade exactly where "
            "she hung it. He despises the Irish magi and their old "
            "ways, and is courting the established English covenants "
            "and the newcomers alike.",
            "He has spent the past year tightening his grip on the "
            "ruins, but the war cost him dearly. His own resources are "
            "gone, he owes vis and favours to a number of magi, and he "
            "has had to borrow more vis and casting tablets from far-off "
            "backers. For all his swagger he knows his prize is only on "
            "loan until he pays, so he is hunting for a way to make the "
            "covenant pay its way; he cannot be seen to give it up.",
        ),
        traits={"Confident": 3, "Driven": 2, "Patient": 1},
    )
    m["baetain"] = b.magus(
        "Báetáin Ua Traimair",
        covenant=praesis,
        house=TREMERE,
        age=60,
        summary=paragraphs(
            "The traitor of Praesis, who looks forty-seven: one of the "
            "besieged, he lost faith in Meadhbh as the siege grew "
            "hopeless and, choosing a Praesis that survived over one "
            "destroyed, handed the Gáe Bulg to Ballack. When the others "
            "found out, they knew the fight was lost and fled.",
            "One of the few Irish-born magi of House Tremere, he has "
            "spent his whole life at Praesis; years ago his parens went "
            "into retirement at Coeris and took Báetáin's sigil with him. He seldom "
            "leaves the old tower now, for every walk takes him past the "
            "burnt homes of people he knew, and he still hears their "
            "screams as fire fell from the sky; he lives under one roof "
            "with Guillaume, who killed them. Still, Praesis stands, and "
            "can be rebuilt.",
        ),
        traits={"Regretful": 3, "Conflicted": 2, "Pragmatic": 1},
    )
    m["guillaume"] = b.magus(
        "Guillaume of Normandy",
        covenant=praesis,
        house=FLAMBEAU,
        age=65,
        summary=paragraphs(
            "Guillaume Flambeau of Normandy, who looks fifty-two. He "
            "could never get out from under the shadow of Montverte, "
            "where he was apprenticed, and came to Hibernia ten years "
            "ago to make his name, drawn by stories heard as an "
            "apprentice. He is frighteningly good with Ignem. He has "
            "already taken the cathach of an independent magus, and "
            "with it that magus's resources and his apprentice, whom he "
            "is shaping in his own image.",
            "He is striking at places in Connacht through the Bréifne "
            "mercenaries he pays, who find vis sources and raid them; he "
            "has not crossed the border himself yet. Gráinne inghean "
            "Uaitéar of Vigil has long been his rival, and he "
            "would love to see the witch brought low before him.",
        ),
        traits={"Bombastic": 3, "Aggressive": 2, "Patient": -1},
    )
    m["cacht"] = b.magus(
        "Cacht",
        covenant=praesis,
        house=CRIAMON,
        age=50,
        summary=paragraphs(
            "Cacht of the Cultas Críamoine, who looks forty: a "
            "Hibernian-born maga raised at Qui Sonant and chosen by the "
            "Path of Strife. Turning from her House's usual morality "
            "drew her to conflict, and the siege offered a rare test, "
            "the overthrow of the way things were. She killed for "
            "Ballack, then lost interest in his goals.",
            "She has no cause of her own and stays at Praesis only "
            "until one finds her, but she listens closely to Guillaume's "
            "reports on Connacht, scenting a new war in the making.",
        ),
        traits={"Remote": 3, "Cold": 2, "Precise": 1},
    )
    m["oscar"] = b.magus(
        "Oscar von Harz",
        covenant=praesis,
        house="",
        age=None,
        type="companion",
        summary=paragraphs(
            "The guardian of the Gáe Bulg: a white-haired giant-blooded "
            "man, without fear and wholly loyal to Ballack, who stands "
            "on a wooden platform facing Meath with the spear held out "
            "as a challenge to any who would steal it. The book prints "
            "no stats for him.",
        ),
    )


# ------------------------------------------------- Meadhbh and Faolán


def _meadhbh_and_faolan(hibernia: Hibernia, b: Builder) -> None:
    m = hibernia.magi
    m["meadhbh"] = b.magus(
        "Meadhbh",
        covenant=hibernia.covenants.get("qui_sonant"),
        house=EX_MISC,
        age=None,
        summary=paragraphs(
            "The fallen leader of Praesis, now in sanctuary at Qui "
            "Sonant Pro Quieto, whose lands the Treaty makes a haven for "
            "all. When Holzner stole the Gáe Bulg she had him caught and "
            "executed and hung his head by its hair from the palisade; "
            "she held Praesis through a year's siege until Báetáin gave "
            "the spear away for her safe passage. Her druid allies had "
            "already left her, saying her demands had grown "
            "unreasonable. At Praesis they meet weekly to guess where she "
            "and her supporters are and whether they will come back.",
            "The book gives neither her House (Ex Miscellanea is assumed) nor her age.",
        ),
    )
    m["faolan"] = b.magus(
        "Faolán",
        covenant=None,
        house=EX_MISC,
        age=None,
        summary=secrets(
            paragraphs(
                "A magus of the Younger House (Ex Miscellanea) who fled "
                "into Connacht before Praesis fell and has stayed far "
                "longer than three nights, a plain breach of the Treaty. "
                "His parens was one of the true Ollamhain, and he has "
                "only a weak grasp of the Hermetic Arts, so he feels "
                "nearer the Connacht druids than the Order; he may have "
                "friends among the Coill Trí. He belongs to no covenant, "
                "a vagrant at law.",
            ),
            "He is turning his back on the Order. The Tribunal has not "
            "yet worked out where he is; when it does, it will want him "
            "brought back, with or without the Coill Trí's help.",
        ),
    )


# ------------------------------------------------------------- finish


def _place_like(hibernia: Hibernia, *words: str) -> Neighbour | None:
    """A place another part made whose name holds one of the words."""
    for neighbour in hibernia.b.saga.neighbours:
        if neighbour.kind != "place":
            continue
        name = neighbour.name.casefold()
        if any(word in name for word in words):
            return neighbour
    return None


BLACK_PIG = (
    "In Connacht. Through Bréifne the dyke runs north to south across "
    "the west, then west to east, then climbs south to north through "
    "the east, passing west and south of Carrick and round Kilmore and "
    "Cavan. As a faerie trod it is worn and broken in places. The "
    "Connachta druids want it left that way: dug out again, it would "
    "ring Ulster with a boundary that bites into Connacht and opens "
    "more land to the Order's claims."
)
AUGHTY = (
    "In Connacht. A thickly wooded range along the Connacht-Munster "
    "border and a great refuge of magical beasts. Magi come seeking "
    "familiars, and some stray over into Connacht by accident, which "
    "has strained the Order's peace with the Coill Trí. Whoever could "
    "set a magical boundary marking the border across these hills "
    "would win the thanks of both the Tribunal and the Coill Trí. Elk's "
    "Run stands on the Munster side."
)


def _append(place: Neighbour, text: str) -> None:
    if text not in place.summary:
        place.summary = paragraphs(place.summary, text)


def finish(hibernia: Hibernia) -> None:
    """Put Connacht in Ireland; add Connacht's stretch to the Black
    Pig's Dyke and the Slieve Aughty (made here when the Ulster or
    Munster part has not); give Meadhbh her covenant of sanctuary; and
    tie the kings, bishops and Athlone to the lords and archbishops
    other parts made."""
    p, w = hibernia.places, hibernia.world
    connacht, breifne = p["connacht"], p["breifne"]
    ireland = p.get("ireland")
    if ireland is not None and not connacht.place_id:
        connacht.place_id = ireland.id
    dyke = _place_like(hibernia, "black pig")
    if dyke is None:
        dyke = _add(
            hibernia,
            "black_pigs_dyke",
            "The Black Pig's Dyke",
            inside=breifne,
            realm="Faerie",
            aura=2,
            summary="A faerie trod (Faerie 2; the book gives no number).",
            **KNOWN_REGION,
        )
    _append(dyke, BLACK_PIG)
    aughty = _place_like(hibernia, "slieve aught")
    if aughty is None:
        aughty = _add(
            hibernia,
            "slieve_aughty",
            "Slieve Aughty",
            inside=connacht,
            summary="The book gives no aura.",
            **KNOWN_TRIBUNAL,
        )
    _append(aughty, AUGHTY)
    meadhbh = hibernia.magi.get("meadhbh")
    qui_sonant = hibernia.covenants.get("qui_sonant")
    if meadhbh is not None and qui_sonant is not None and not meadhbh.covenant_id:
        meadhbh.covenant_id = qui_sonant.id
    _answers(w.get("cathal"), w.get("henry_iii"))
    _answers(w.get("athlone"), w.get("walter_de_lacy"))
    tuam = _archbishop(hibernia, "tuam")
    _answers(w.get("tuam_town"), tuam)
    armagh = _archbishop(hibernia, "armagh")
    _answers(w.get("bishop_triburnia"), armagh)
    for key in (
        "bishop_killala",
        "bishop_achonry",
        "mayo_clergy",
        "bishop_elphin",
        "bishop_annaghdown",
        "bishop_cill_mhic_dhuach",
        "bishop_clonfert",
        "cong_abbey",
        "omey_monastery",
    ):
        _answers(w.get(key), tuam)


def _archbishop(hibernia: Hibernia, key: str) -> Neighbour | None:
    """church.py's archbishop, by its key; a town of that name is not."""
    found = hibernia.world.get(key)
    return found if found is not None and found.kind == "church" else None


def _answers(record: Neighbour | None, overlord: Neighbour | None) -> None:
    if record is not None and overlord is not None and not record.answers_to:
        record.answers_to = overlord.id


# --------------------------------------------------------------- stats

P = Profile
IRISH_TONGUE = "Irish"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "ballack": P(
        strong="int com pre",
        weak="dex qik",
        arts={"Re": 6, "Me": 6, "Pe": 5, "Ig": 4, "Vi": 4},
        abilities={
            "Intrigue": (4, "alliances"),
            "Leadership": (4, "war"),
            "Guile": 3,
            "Code of Hermes": (3, "Wizard War"),
            "Area Lore: Hibernia": 2,
        },
        virtues=[
            _art("Affinity with {art}", "mentem"),
            "Driven (Minor)",
            "Proud (Minor)",
        ],
        native="High German",
    ),
    "baetain": P(
        strong="int sta per",
        weak="pre com",
        arts={"Re": 6, "Vi": 5, "Me": 5, "Te": 4, "Cr": 3},
        abilities={
            "Area Lore: Lough Ree": (4, "the island"),
            "Magic Lore": 3,
            "Folk Ken": 2,
            "Concentration": 2,
        },
        virtues=[
            "Covenant Upbringing",
            "Pessimistic",
        ],
        native=IRISH_TONGUE,
    ),
    "guillaume": P(
        strong="pre sta str",
        weak="per int",
        arts={"Ig": 10, "Cr": 6, "Pe": 6, "Re": 4, "Co": 3},
        abilities={
            "Penetration": (5, "Ignem"),
            "Leadership": (4, "mercenaries"),
            "Single Weapon": (3, "sword"),
            "Area Lore: Connacht": 2,
            "Intrigue": 2,
        },
        virtues=[
            _art("Affinity with {art}", "ignem"),
            "Mercenary Captain",
            "Overconfident (Minor)",
            "Wrathful (Minor)",
        ],
        native="Norman French",
    ),
    "cacht": P(
        strong="int per qik",
        weak="pre com",
        arts={"Pe": 7, "Co": 6, "Me": 5, "Vi": 4, "In": 3},
        abilities={
            "Enigmatic Wisdom": (5, "strife"),
            "Awareness": (3, "ambushes"),
            "Finesse": (3, "precision"),
            "Single Weapon": 2,
        },
        virtues=[
            "Clear Thinker",
            "Obsessed (Minor)",
            "Covenant Upbringing",
        ],
        native=IRISH_TONGUE,
    ),
    "meadhbh": P(
        strong="pre com int",
        weak="dex qik",
        arts={"Re": 6, "Me": 6, "He": 5, "An": 4, "Im": 4},
        abilities={
            "Leadership": (5, "covenfolk"),
            "Magic Lore": (4, "hedge wizards"),
            "Area Lore: Connacht": 4,
            "Intrigue": 3,
            "Code of Hermes": (3, "the Treaty"),
        },
        virtues=[
            "Hermetic Prestige",
            "Social Contacts",
            "Enemies",
            "Proud (Minor)",
            "Wrathful (Minor)",
        ],
        age=120,
        native=IRISH_TONGUE,
    ),
    "faolan": P(
        strong="com pre per",
        weak="int sta",
        arts={"Im": 5, "Me": 5, "Au": 3, "An": 3},
        abilities={
            "Music": (4, "singing"),
            "Faerie Lore": (3, "the Ollamhain"),
            "Area Lore: Connacht": 3,
            "Charm": 2,
        },
        virtues=[
            "Educated (Bardic)",
            "Weak Magic",
            "Outcast",
        ],
        age=35,
        native=IRISH_TONGUE,
    ),
}


def stats(hibernia: Hibernia) -> None:
    """Generated stats for the Praesis magi, Meadhbh and Faolán, none of
    whom has a printed stat block."""
    b = hibernia.b
    for key, profile in PROFILES.items():
        character = hibernia.magi.get(key)
        if character is not None:
            apply(b, character, profile)
