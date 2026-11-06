"""Ulster, the northern province of the Hibernian Tribunal, as of 1220:
the province (places["ulster"]) with its peoples, the Érainn, the
Cruithnigh and the English; the Gaelic kingdoms of Tír Chonaill, Tír
Eóghain and Airgíalla and the English Earldom of Ulster, each a place
with its king or earl, towns, bishops, abbeys and sites; Tír Fhomóraig,
the Fomórach's islands of Rathlin and Toraigh; the Mercer House of Leth
Cuinn with the Cult of Heroes and the eighteen clesa of the clesrada;
Qui Sonant Pro Quieto, the Order's cemetery and neutral ground, with the
giant under it and its funeral rites; and Vigil, its halls on Cionn
Mhálanna, the drowned vaults and Banbha's Crown, with the Folk
Mysteries. In paraphrase of The Contested Isle chapter nine (and
chapters two, four and thirteen where they speak of the same places).

Keys: the province is places["ulster"]; the four realms are
places["tir_chonaill"], ["tir_eoghain"], ["airgialla"] and
["earldom"], and the Fomórach's islands places["tir_fhomoraig"],
["rathlin"] and ["toraigh"]. The covenants are covenants["leth_cuinn"],
["qui_sonant"] and ["vigil"]; their magi are magi["daire_cu"],
["daire_an_chogaidh"], ["elen"], ["cantarus"], ["finn"], ["lewis"],
["turlough"], ["einri"], ["grainne"], ["mael_ruanaid"] and
["maoilfhinnein"], with Peter, Lewis's exiled rival, as magi["peter"]
and Bressal of Bonisagus as magi["bressal"], neither with a covenant.
Meadhbh, in sanctuary at Qui Sonant, is Connacht's. Sites other parts
place things in: places["sperrin"] (the Diedne Vigil's foothills),
["rath_chinneich"] (the Widow's Throat stands over it), ["lough_erne"]
(the Uí hEódhasa bardic school, Inis Doney), ["magh_sleacht"] and
["lough_neagh"]. The Earl is world["hugh_de_lacy"]; the kings are
world["king_tir_chonaill"], ["king_tir_eoghain"] and
["king_airgialla"]; the bishops are world["bishop_raphoe"],
["bishop_doire"], ["bishop_clogher"] and ["bishop_down"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import joined_lines, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from ..builder import Builder
    from . import Hibernia

MERCERE = "house_mercere"
JERBITON = "house_jerbiton"
VERDITIUS = "house_verditius"
CRIAMON = "house_criamon"
MERINITA = "house_merinita"
BONISAGUS = "house_bonisagus"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
HIDDEN: dict[str, Any] = {"status": "Rumoured", "known": "In the Tribunal"}


def _add(hibernia: Hibernia, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = hibernia.b.place(name, **kw)
    hibernia.places[key] = place
    return place


def _tribunal(hibernia: Hibernia) -> Tribunal:
    """The Tribunal tribunal.py made; while that part is still a stub, a
    bare stand-in so the province can be built and checked on its own."""
    b = hibernia.b
    found = hibernia.tribunal or next(iter(b.saga.tribunals), None)
    if found is None:
        found = b.tribunal(
            "Hibernian Tribunal",
            package="",
            summary="",
            meets_every=7,
            next_year=1221,
            next_season="Summer",
            meeting_place="the Hill of Tara",
        )
    return found


def build(hibernia: Hibernia) -> None:
    b = hibernia.b
    tribunal = _tribunal(hibernia)
    _province(hibernia)
    _tir_chonaill(hibernia)
    _tir_eoghain(hibernia)
    _airgialla(hibernia)
    _earldom(hibernia)
    _tir_fhomoraig(hibernia)
    _lords(hibernia, b)
    _churches(hibernia, b)
    _towns(hibernia, b)
    _factions(hibernia, b)
    _leth_cuinn(hibernia, b, tribunal)
    _qui_sonant(hibernia, b, tribunal)
    _vigil(hibernia, b, tribunal)
    _wanderers(hibernia, b)


# ------------------------------------------------------------ the province


def _province(hibernia: Hibernia) -> None:
    _add(
        hibernia,
        "ulster",
        "Ulster",
        inside=hibernia.places.get("ireland"),
        summary=paragraphs(
            "Ulaid, the most northerly of Ireland's provinces. In the days "
            "of King Conchobhar mac Neasa, who held court at Emhain Mhacha, "
            "its people, the Ulaidh, gave Ireland many of its greatest tales "
            "of kings and heroes, the Ruadhraigheacht or Ulster Cycle: the "
            "wars of the Ulaidh with the Connachta, Conchobhar's rivalry "
            "with Fearghus mac Róich, the strife of the two great bulls, and "
            "the deeds of Cú Chulainn. No kingdom of the province has an "
            "Ulaidh king any longer, yet Ulstermen keep a fierce pride in "
            "their past and hold together remarkably well for a people so "
            "long ruled by outsiders. The druids linked the north with war "
            "and strife, and the province's story bears them out.",
            "In 1220 it holds three Gaelic kingdoms, Tír Chonaill in the "
            "west, Tír Eóghain in the north and centre and Airgíalla in the "
            "south, with the English Earldom of Ulster in the east under "
            "Hugh de Lacy; off the north coast lie the islands of Tír "
            "Fhomóraig, the last refuge of the Fomórach. Three houses of the "
            "Order stand here: the Mercer House of Leth Cuinn on Lough "
            "Neagh, Qui Sonant Pro Quieto in the Cuailnge mountains and "
            "Vigil on Cionn Mhálanna.",
            "The peoples. Long ago the north was Tír Fhomóraig, the "
            "Fomórach's land from coast to coast, lording it over the "
            "Nemedians and the Tuatha Dé; when that race was driven out the "
            "Érainn took the land. The Érainn, one of the four root races "
            "sprung from Míl Espáine and once a client tribe of the "
            "Connachta, survived longest here as the Ulaidh, worshipping "
            "Dáire (a northern name for the Dagda) and Macha, goddess of "
            "horses and sovereignty. Legend says Conchobhar died on the day "
            "of the Crucifixion of an old wound dealt by magic, his soul "
            "kept in his skull until Saint Patrick, hearing it cry out, wept "
            "over it and so baptised it into Heaven.",
            "The Connachta pressed north up the Boyne valley until the "
            "Ulaidh fell back into the east; two of the four sons of Niall "
            "of the Nine Hostages carved out the west and centre, and the "
            "nine sub-kingdoms of Airgíalla each gave the high king a "
            "hostage, hence his byname. Hence the commons of the west and middle are "
            "Érainn with Connachta lords over them. The Ulaidh of pure descent are "
            "the Dál bhFiatach, lords of the east from Downpatrick until the English "
            "arrived, sometimes allied with and sometimes rivals of "
            "the Dál nAraidhe; some of their families still suffer Macha's "
            "Birth-Pangs, the curse laid on Ulstermen of the true blood.",
            "The Cruithnigh, the Picts of Scotland, are not a root race. "
            "They came seeking wives, having no women, and Éireamhóin mac "
            "Míl gave them Mílesian widows on condition that women lead "
            "them, as they still do. Their kingdom of Dál nAraidhe once "
            "reached over the north-east, the Isle of Man and Kintyre, but "
            "it was failing when its druids were ground between Diedne, who "
            "hunted pagan priesthoods that would not join her House, and "
            "Pralix, who hunted the supporters of Damhan-Allaidh. A few túatha remain in "
            "the north of the province and about Drogheda, with scattered "
            "folk elsewhere in the north and west. They run a little shorter "
            "and darker than the Gaels, love clothes of many colours and "
            "often tattoo themselves; a few pockets of their old religion "
            "survive, in Tír Fhomóraig at least, with priests just like the "
            "gruagachan.",
            "The English. John de Courcy was granted Ulster by the English "
            "king if he could win it, and took the grant at its word: with "
            "twenty-two knights and some three hundred men he marched "
            "through Meath and Airgíalla and fell on Down on 1 February "
            "1177. Ulster's king, Ruaidhrí mac Con Ulad Mac Duinn Sléibe, could not "
            "meet him in the field while Macha's curse lay on his "
            "men; he came back a week later with an army, but the Ulaidh "
            "broke at the sight of armoured knights on horseback, and even "
            "with the Cenél nEóghain beside them later that year they could "
            "not shift him. De Courcy, who seemed to have God's favour, soon "
            "held everything east of the Bann. In 1196 he beat the king of "
            "Tír Chonaill and made him pay tribute, and after an Irishman "
            "killed his brother at his court in 1198 he laid waste the "
            "north. When his old enemy John became king in 1201 he unwisely "
            "made common cause with Cathal Crobhdearg Ua Conchobhair of "
            "Connacht, and in 1203 Hugh de Lacy, younger son of the Lord of "
            "Meath, arrested him as a rebel; in May 1205 John made Hugh the "
            "first Earl of Ulster, with all the land de Courcy had held on "
            "the day of his defeat.",
            "Plagues. Tír Chonaill has loosed several plagues great enough "
            "to be named in the annals: the Crom Chonaill in the sixth "
            "century, the Buidhe Chonaill in the seventh, a pestilence in "
            "986 when demons were seen dancing among the dead, and the Rogh "
            "Rámhach of 1084, said to have killed a quarter of Ireland; the "
            "Scuab a Fánait foretold in 1096 never came. A great dragon is "
            "said to have flown overhead before each, and some note that the "
            "Fomórach once killed the Partholónians with plague, and that "
            "their last remnant lives on the islands just north of Tír "
            "Chonaill.",
            "Vis lies at Sliabh Crúibe (stones carried to its summit), held by no one.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        hibernia,
        "black_pigs_dyke",
        "The Black Pig's Dyke",
        inside=hibernia.places["ulster"],
        realm="Faerie",
        aura=1,
        summary=paragraphs(
            "The Gleann na muice duibhe, a ditch twelve feet deep in places "
            "between banks up to four feet high, which runs along Ulster's "
            "southern border between Donegal Bay on the west and Lough Cairlinn on "
            "the east. An enormous black faerie boar rooted it out with "
            "its snout and cleared it again every third year, until the "
            "magi of Vigil killed it and kept its tusks as their cathach; "
            "nobody has ploughed it since. It is broken now and badly "
            "neglected, but what survives is a faerie trod with a Faerie "
            "aura of 1.",
            "Restored, it would ring the whole of Ulster in one boundary, "
            "though a Target: Boundary spell covering the entire province "
            "would need seven size modifiers.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------------------- Tír Chonaill


def _tir_chonaill(hibernia: Hibernia) -> None:
    ulster = hibernia.places["ulster"]
    region = _add(
        hibernia,
        "tir_chonaill",
        "Tír Chonaill",
        inside=ulster,
        summary=paragraphs(
            "The land of the Cenél gConaill in the west of Ulster, a branch "
            "of the Uí Néill, the dynasty that also rules Connacht. It takes "
            "its name from Conall Gulban, son of Niall of the Nine Hostages, "
            "who won his byname by running up Beann Ghulban and back within "
            "a day without collapsing; for that feat the druids accepted him "
            "as king, and the lesser kings soon bent the knee. King Domhnall "
            "Mór mac Eicnechain, of Conall's line and the second king from "
            "the Uí Domhnaill, rules it with the help of his Lucht Tighe, "
            "the household families, and keeps it free of the English by "
            "the strength of his gallóglaigh. It is close allied with Tír "
            "Eóghain.",
            "A country of mountains: the Derryveagh range (Cnoic Dhoire "
            "Bheatha) to the north and the Blue Stacks (Cruacha Gorma) to "
            "the south, which cut the kingdom in two, with deep green sheep "
            "valleys between. The best farmland is the valley of the Finn "
            "and the Laggan round Raphoe.",
            "The Lucht Tighe. The Uí Domhnaill hand much of the running of "
            "the kingdom to household families, and other dynasties do the "
            "same; some covenants have copied the custom among their "
            "covenfolk. The book calls them eight and lists nine: the Mac "
            "Robhartaigh keep the clan's cathach, the Mac Suibhne lead the "
            "gallóglaigh and marshal the Uí Domhnaill's hosts, the Uí "
            "Breisléin are the brehons, the Uí Cléirigh the scribes and "
            "historians, the Mac Duinnshleibhe the physicians, the Uí "
            "Firghil the keepers of the clan's rites, the Uí Gallchobhair "
            "the captains of horse, the Uí Tiománagh the herdsmen, and the "
            "Mac a'Bháird the bards.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "lough_dearg",
        "Lough Dearg",
        inside=region,
        summary=paragraphs(
            "A wide, shallow lake known above all for its island of "
            "Inisphadraig, where the Purgatory of Saint Patrick draws "
            "pilgrims from across Ireland (see that church). Tales say "
            "tunnels beneath the water join some of its other islands.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "poisoned_glen",
        "The Poisoned Glen",
        inside=region,
        aura=1,
        summary=paragraphs(
            "A glen on the coast across from Toraigh Island, whose black, "
            "scorched mountainsides show where Balor of the Evil Eye, the "
            "Fomóir champion, glared at Ireland from his tower on the "
            "island. A standing stone at its mouth is said to be a warrior "
            "Balor turned to stone for his cheek. Magic aura 1, perhaps "
            "higher in places. The slopes of the Seven Sisters, the "
            "tallest of them An tEaragail (Mount Errigal), fall into it.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "beltany_tops",
        "Beltany Tops",
        inside=region,
        aura=2,
        summary=paragraphs(
            "A great stone circle on a lonely hill two miles south of "
            "Raphoe: sixty broad triangular stones, most about four feet "
            "tall and leaning a little outward, some touching and some "
            "parted by low boulders, ring a space nearly fifty feet across, "
            "with pillars over nine feet high at east and west. A carved "
            "stone head among them pulls a face as if blowing or shrieking; "
            "there were once at least three more, now broken or carried off. "
            "Magic aura 2.",
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------------ Tír Eóghain


def _tir_eoghain(hibernia: Hibernia) -> None:
    ulster = hibernia.places["ulster"]
    region = _add(
        hibernia,
        "tir_eoghain",
        "Tír Eóghain",
        inside=ulster,
        summary=paragraphs(
            "The kingdom of the Cenél nEóghain, named, like the Inis "
            "Eóghain peninsula, for Eóghan, son of Niall of the Nine "
            "Hostages and brother of Conall Gulban. It is a young kingdom "
            "that broke free of its old overlords at Aileach and now "
            "dominates them; Aed Meith mac Aeda Ua Néill, who took power "
            "from Aileach in 1185, is its first Uí Néill king.",
            "The Foyle, the Bann and the Blackwater roughly bound it, and "
            "the Sperrin Mountains (Sliabh Speirin) fill it. Between the "
            "mountains and Lough Neagh stretches a flat peat bog no crop "
            "will grow on, so most people live on the north coast or on the "
            "grain lands of the south toward Airgíalla.",
        ),
        **KNOWN_REGION,
    )
    inis = _add(
        hibernia,
        "inis_eoghain",
        "Inis Eóghain",
        inside=region,
        summary=(
            "The northern peninsula of Tír Eóghain, between Lough Foyle and "
            "Lough Swilly, which holds the hillfort of Aileach and, at its "
            "tip, Cionn Mhálanna, where Vigil stands."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "aileach",
        "Aileach",
        inside=inis,
        realm="Faerie",
        aura=2,
        summary=paragraphs(
            "A hillfort on Inis Eóghain, once the capital of a kingdom that "
            "held Airgíalla and Ulster as vassals; Saint Patrick baptised "
            "Eóghain mac Neill here in 450. The King of Munster broke its "
            "power in 1101, the English wore away more of it, and the Cenél "
            "nEóghain have ruled it since 1185.",
            "Its fortress, the Grianán Ailigh, is the Dagda's work, built to honour "
            "the sun, and was for a while the headquarters of the "
            "fight against the Fomórach. It stands empty, shattered by the "
            "Munstermen: Muirchertach Ua Briain, whose own fort the king of "
            "Aileach had razed twenty years before, had each of his soldiers "
            "carry a stone home to rebuild with, but a faerie-built fort is "
            "not so easily stolen, and every stone taken was replaced. The ring wall: "
            "17 feet tall, 13 thick, 77 across. The book gives it no aura; Faerie 2 "
            "is assumed for a "
            "fort of faerie make.",
            "It would make a fine covenant site, but Vigil has declared an "
            "interest in it. Vigil has no right in law to keep others from "
            "exploring it, but would likely back its claim with certamen and "
            "Wizard War.",
        ),
        **KNOWN_TRIBUNAL,
    )
    sperrin = _add(
        hibernia,
        "sperrin",
        "The Sperrin Mountains",
        inside=region,
        summary=paragraphs(
            "Sliabh Speirin, the mountains at the heart of Tír Eóghain. In "
            "their foothills House Diedne founded the first covenant of "
            "Vigil, the Diedne Vigil, raided by Dublin's rune wizards in "
            "830 and sacked by the Merinita after 851.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "beaghmore",
        "Beaghmore",
        inside=sperrin,
        aura=4,
        summary=paragraphs(
            "An Bheitheach Mhór, 'the big place of birch trees', a peat bog "
            "in the south-eastern foothills of the Sperrins full of "
            "contradictory auras and strange happenings. Seven stone "
            "circles, a dozen cairns and ten dead-straight stone rows, all "
            "set along a line from north-east to south-west, poke through "
            "the peat. The circles stand in three pairs and one alone; the "
            "lone circle is packed with a thousand upright triangular "
            "stones the locals call the dragon's teeth.",
            "Each pair of circles has its own Magic aura, from 1 to 3, the "
            "lone circle has 4, and every stone row has an aura of 2 tied "
            "to a different Form. Bressal of Bonisagus (Bressal Ua "
            "Boniségeas), who has studied the moor at length, thinks the "
            "clash of auras marks a shattered regio, broken by design or by "
            "chance he cannot say.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "leacht_abartaigh",
        "Leacht Ábartaigh",
        inside=region,
        summary=paragraphs(
            "A dolmen near Slaghtaverty over the grave of Ábhartach, a "
            "dwarf and sorcerer who ruled the district by fear and evil "
            "spells. A chieftain killed him, Fionn mac Cumhaill say some, "
            "Cathán, forebear of the local Ua Catháin, say others. Buried "
            "upright, he was back in his ráth the next day as wicked as "
            "ever; killed and buried again, he came back again. The third "
            "time a druid had him buried head down with a monument on top, "
            "and his magic stayed in the grave. He is a neamh-mairbh, one "
            "of the walking dead.",
            "The monument is long forgotten and the land is being cleared for farming.",
        ),
        **KNOWN_LOCALLY,
    )
    neagh = _add(
        hibernia,
        "lough_neagh",
        "Lough Neagh",
        inside=ulster,
        summary=paragraphs(
            "The great lake at the centre of Ulster, made when the giant "
            "hero Fionn mac Cumhail fought the Scottish giant Benandonner: "
            "he tore up a clod of earth and flung it at his rival, it fell "
            "short into the Irish Sea as the Isle of Man, and the hole it "
            "left filled with water. Rumour still speaks of a péist, a "
            "monster, in the lake, but Dáire Farranta, founder of Leth "
            "Cuinn as it now is, killed it centuries ago. The Mercer House "
            "of Leth Cuinn stands on its north-eastern shore.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "inisclabhall",
        "Inisclabhall",
        inside=neagh,
        aura=2,
        summary=paragraphs(
            "A thickly wooded island of about nine acres in the south-west "
            "of Lough Neagh, more than half a mile out, reached by Saint "
            "Patrick's Road, a sunken causeway less than two feet under "
            "water in summer. The saint is said to have used it as a "
            "retreat. Its great beauty is a natural tether for a Magic aura "
            "of 2, and it would be an ideal covenant site but for the "
            "English knight just granted leave to raise a motte on it.",
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------------- Airgíalla


def _airgialla(hibernia: Hibernia) -> None:
    ulster = hibernia.places["ulster"]
    region = _add(
        hibernia,
        "airgialla",
        "Airgíalla",
        inside=ulster,
        summary=paragraphs(
            "Oriel to the English: a league of nine sub-kingdoms in "
            "southern and central Ulster, ruled by the heirs of the Three "
            "Collas and their followers over a people of the Érainn. The "
            "Collas, Colla Uais, Colla Meann and Colla Fochra, came home from "
            "exile in Scotland after killing the father of the high king "
            "Muireadhach Tíreach, who pardoned them and urged them to win "
            "Ulster; they won six great battles against the Ulaidh, and the "
            "seventh raged a day and a night until the fighters stood waist "
            "deep in blood. The name means 'givers of hostages', for the "
            "nine noble hostages, chained in gold, that it gave the "
            "Connachta. Its king is Donnchad Ua nAnluain, at Clogher.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "emhain_mhacha",
        "Emhain Mhacha",
        inside=region,
        summary=paragraphs(
            "A hillfort of eighteen acres a few miles west of Armagh, the "
            "seat of Ulster's ancient kings, of Conchobhar mac Neasa and the "
            "Red Branch. It bears the name of Macha, chief goddess of the "
            "Ulaidh, a goddess of war and horses and a face of the "
            "Mór-Rióghain, whose consort was Dáire. Several mortal women "
            "named Macha belong to the place; one, the wife of Crunnchu, "
            "was made to race the king's horses while heavily pregnant "
            "because her husband had boasted she could outrun them, and won, "
            "and collapsed, and bore twins; dying, she cursed the men of "
            "Ulster to suffer her pangs for five nights and four days in "
            "their hour of greatest need, the ces noidhen.",
            "Conchobhar's palace, the Chraobhruadh or red-branched house, "
            "was a richly carved hall on posts of red yew, six rings of "
            "them round an oak pillar over forty feet tall that gave the "
            "Red Branch heroes their name. Long ago someone filled it with "
            "boulders at least six feet deep and burnt it, an enemy's "
            "attack or a rite after a king's death, no one knows. Treasure "
            "hunters still dig for the gold said to have clad the roof.",
            "Nearby lie the ruins of Bron Bherg, the 'house of sorrows' to "
            "the east, which Macha Mhuingruadh built, by tradition Mythic Europe's "
            "earliest hospital, in use until it was destroyed in "
            "22 AD; Loughnashade, the 'lake of the treasure', to the "
            "north-east, where Macha's druids threw gold, horses and "
            "enemies' heads to the gods; and the King's Stables to the "
            "north-west, where the king's sacred horses were kept. Their "
            "descendants still run about Armagh, and some are fíorláiridhe, "
            "true mares (see the Bestiary). The book gives no aura.",
        ),
        **KNOWN_TRIBUNAL,
    )
    cuailnge = _add(
        hibernia,
        "cuailnge",
        "Cuailnge",
        inside=region,
        summary=paragraphs(
            "The Cuailnge peninsula and its mountains, once the heart of "
            "Conaille Muirtheimne, a kingdom tributary to Ulster whose people "
            "are still Cruithnigh, of the Uí Echach Corbo; they held the "
            "land from the peninsula to the mouth of the Boyne, but the Earl "
            "of Ulster has given most of it to English knights hoping to "
            "make baronies of it. Qui Sonant Pro Quieto stands high on a "
            "ridge here.",
            "The plain of Muirtheimne is said to have lain under the sea "
            "until Conchobhar mac Neasa, before he was king, caught a "
            "daughter of the god Ler on the strand; to be let go she raised "
            "the plain and taught him to make a shield that strengthened its "
            "bearer and weakened his foes. The smith Culann left his forge "
            "on the Isle of Man to make it and was given the plain, the same "
            "Culann whose hound gave Cú Chulainn of Muirtheimne his name.",
            "Donn and Find. Two faeries, Donn the dark and Find the bright, "
            "have fought each other since memory began, changing shape "
            "between swineherds, hawks, fish, stags, warriors, phantoms and "
            "maggots; their best-known forms were the Donn Cuailnge, the "
            "dark bull of Cuailnge, and Findbheannach, the white bull of "
            "Connacht, whose rivalry began the Táin Bó Cuailgne. Find stands "
            "for light, wisdom and day; Donn for the dead, ghosts and night. "
            "Both forever try to draw mortals into their war. Donn has lately "
            "caused a number of faerie-blooded children to be born, meaning "
            "them for the heart of a new army; Find has made no answer yet.",
        ),
        **KNOWN_REGION,
    )
    hibernia.places["cuailnge"] = cuailnge
    fermanagh = _add(
        hibernia,
        "fermanagh",
        "Fermanagh",
        inside=region,
        summary=(
            "Fir Managh, once among the strongest of Airgíalla's tributary "
            "kingdoms, which kept itself half free and half bound to "
            "Connacht while staying on good terms with Airgíalla. In the "
            "early thirteenth century it has lost most of its independence."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "lough_erne",
        "Lough Erne",
        inside=fermanagh,
        summary=paragraphs(
            "The River Erne winds through Fermanagh and opens into two "
            "loughs. Lower Lough Erne has more than a hundred and fifty "
            "islands, many with Augustinian houses; the round tower on "
            "Daimhinis guides boats through them, its monks ringing the bell "
            "when visitors appear and the next tower taking up the message, "
            "so word passes bell by bell up the lough. The Uí hEódhasa "
            "bardic school stands on the shore.",
            "Boa Island, the largest, is named for Badhbh, one of the Tuatha "
            "Dé's bloodthirsty war goddesses, and bears a two-faced idol "
            "with hunched shoulders and a jutting tongue. White Island has "
            "eight statues, all by one mason two or three centuries ago, "
            "which the monks call saints though no one agrees which: a "
            "grinning naked woman, a Sile na gCíoch, displaying herself; a "
            "king on a throne; a cowled figure holding a staff; a king gesturing at "
            "his mouth; a man with two winged beasts, dogs or lions; a warrior "
            "with sword and shield; a figure with no features at all; and a "
            "scowling head.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "magh_sleacht",
        "Magh Sléacht",
        inside=region,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "The 'plain of adoration', holy to the pagan Érainn, where an "
            "idol of Crom Cruach stood with twelve lesser gods; some "
            "Merinita say he was a sun god and the twelve the months. Saint "
            "Patrick threw it down and made the idols sink into the earth, "
            "and since then the idol has been told of as Crom Dubh, 'the "
            "dark croucher', an image of the Antichrist. Faerie aura 3.",
            "Now and then someone who has turned from God comes here for "
            "power and, instead of the Antichrist, finds himself talking to "
            "its faerie copy. Crom Dubh gladly teaches faerie wizardry "
            "dressed up as infernalism when it feeds his own story.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "sidh_fionnachaidh",
        "The Sídh of Fionnachaidh",
        inside=region,
        realm="Faerie",
        aura=3,
        summary=(
            "The sídh of Lir which opens on Tír Tairngire, his Otherworld, the Land "
            "of Promise; there fish graze like sheep and the White "
            "Fields (fionnachaidh) turn to foam-capped waves. Swans love to "
            "rest here in memory of Lir's four children, cursed by a jealous "
            "stepmother to spend nine hundred years as swans. The book gives "
            "no aura; Faerie 3 is assumed."
        ),
        **KNOWN_TRIBUNAL,
    )
    meath = hibernia.places.get("meath")
    _add(
        hibernia,
        "millmount",
        "Millmount",
        inside=meath or region,
        summary=(
            "A huge mound in Drogheda-in-Meath holding the grave of Amairgen "
            "mac Míl, chief druid of the Milesians. Hugh de Lacy has built a "
            "bailey on top of it, to the alarm of the locals, who fear it "
            "will trouble the druid's restless spirit."
        ),
        **KNOWN_LOCALLY,
    )


# ---------------------------------------------------- the Earldom of Ulster


def _earldom(hibernia: Hibernia) -> None:
    ulster = hibernia.places["ulster"]
    region = _add(
        hibernia,
        "earldom",
        "The Earldom of Ulster",
        inside=ulster,
        summary=paragraphs(
            "The English earldom in the east of the province, on the old "
            "lands of the Dál bhFiatach and the Dál nAraidhe: won by John de "
            "Courcy, held since 1205 by his great rival Hugh de Lacy. To the "
            "English a castle says that what they have taken they mean to "
            "keep, and they have built them everywhere: besides Belfast, "
            "Carrickfergus and Dundrum, de Courcy and de Lacy have "
            "fortified Dunseverick, Dundalk, Dromore and Green Castle, and "
            "their knights have put up baileys and stone towers beyond "
            "counting.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "antrim",
        "The Round Tower of Antrim",
        inside=region,
        summary=(
            "Antrim is a town of note that grew round Saint Aebh's "
            "monastery of the late fifth century. Its 90-foot round tower "
            "was the bell tower of that early house, burnt in 1147 and "
            "never rebuilt. The Bullaun Stone at its foot bears the print "
            "of the knee and foot of a witch who threw herself from the top "
            "when the tower was finished."
        ),
        **KNOWN_LOCALLY,
    )
    bangor = _add(
        hibernia,
        "bangor",
        "Bangor",
        inside=region,
        realm="Divine",
        aura=6,
        summary=paragraphs(
            "Beannchor, the 'horned curve' of its bay: a town round the "
            "abbey of Beannchor Mór (see Bangor Abbey). Within earshot of "
            "the abbey's unbroken song the Dominion aura is 6, usually with "
            "a Calm temper.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "vale_of_angels",
        "The Vale of Angels",
        inside=bangor,
        realm="Divine",
        aura=2,
        levels=[
            hibernia.b.level(
                "The Celestial regio",
                5,
                "Divine",
                notes=(
                    "Home of Victorius, the angel set over Ireland, one of "
                    "the choir of principalities, and of the throng of "
                    "angels under him who tend every part of Ireland and "
                    "its people. A visit here gave Patrick his vision."
                ),
            )
        ],
        summary=(
            "A valley near Bangor Abbey where Saint Patrick saw a vision "
            "full of angels. Divine aura 2, with the way into a Celestial "
            "regio of aura 5."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "belfast_castle",
        "Belfast Castle",
        inside=region,
        summary=(
            "Beal Feirste, the 'mouth of the sandbank', an old fortress "
            "site; the present castle is John de Courcy's, of 1177."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "giants_ring",
        "The Giant's Ring",
        inside=region,
        aura=3,
        summary=paragraphs(
            "A vast earthwork near Belfast Castle, almost 200 paces across, "
            "its bank 15 feet high with three gaps, and inside the bank, "
            "set side by side in the Irish way, standing stones twelve feet "
            "tall. A little passage tomb lies just east of the centre. "
            "Magic aura 3.",
            "The giants of Ireland meet here, though they have held no "
            "council for centuries. A magus who wants a giant's ear cuts the "
            "giant's name in ogham on a stone and leaves it in the tomb; "
            "within forty days the giant sends a messenger.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "carrickfergus",
        "Carrickfergus Castle",
        inside=region,
        summary=(
            "Carraig Fhearghais, the 'rock of Fergus', for King Fearghus, "
            "wrecked nearby. John de Courcy built the castle on the "
            "promontory in 1177, a small bailey at its tip above Belfast "
            "Loch inside an inner ward and a great curtain wall, as the base "
            "of his wars on the Ulaidh. It is still the caput of the "
            "earldom; Hugh de Lacy has strengthened it with a new eastern "
            "tower and a wall along the seaward side."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "erenagh",
        "Erenagh",
        inside=region,
        summary=(
            "The ruined monastery of Erenagh, destroyed by John de Courcy in "
            "1177; its survivors went to his new abbey of Iniscourcy. Ghosts "
            "of its murdered monks still walk it, and survivors meet here in "
            "secret with brothers from Iniscourcy, first to plot the English "
            "out, now, at the ghosts' whispering, to take bloody revenge."
        ),
        **RUMOURED,
    )
    _add(
        hibernia,
        "saulpatrick",
        "Saulpatrick",
        inside=region,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "Sabhall Phádraig, where Saint Patrick died. For twelve days "
            "after his death no night fell here, and on his feast day the "
            "sun still does not set, so it draws a small pilgrimage that "
            "usually ends at Downpatrick, where his body lies. A Christian "
            "who sees the unsetting sun gains a Faith Point. A spell with "
            "Duration Sun cast here on his feast day lasts until the sun "
            "sets where its target is, up to a day and a half, and Parma "
            "Magica likewise. The book gives no aura; Divine 3 is assumed.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "dundrum_castle",
        "Dundrum Castle",
        inside=region,
        summary=paragraphs(
            "De Courcy's castle of 1180 on an old fort's site, on a hill 200 "
            "feet above the bay. Beaten by de Lacy, de Courcy ran to King Ragnold of "
            "Man, his wife's brother, and came back with a hundred "
            "longships of Norsemen, landed at Strangford and besieged it, "
            "but he had built it too well; he was taken and lived out his "
            "days in poverty. Its stone tower is new (the book credits an "
            "Earl Henry). The town below is now an important port of the "
            "earldom.",
        ),
        **KNOWN_REGION,
    )
    cuan = _add(
        hibernia,
        "lough_cuan",
        "Lough Cuan",
        inside=region,
        summary=paragraphs(
            "The 'calm lake', called Strangford Lough from the Norse for a "
            "strong fjord. The Ards Peninsula shuts it off from the sea, "
            "with a round tower at Kirkistown held and enlarged by the "
            "English le Savage family and the Cistercian abbey of Mainistir "
            "Liath; the Leath Cathail Peninsula closes its southern mouth. "
            "It has many islands, the largest Machaoi Island.",
            "Saint Machaoi, a swineherd Patrick baptised, founded Nendrum on "
            "that island and taught Saint Colmán of Drom Mór. Gathering wood "
            "one day, he met a wondrous bird that sang him three strains; "
            "each seemed a moment but took fifty years, and he came out of "
            "the wood to find his hermitage a monastery with a shrine to his "
            "memory. His feast is 23 June. Patrick gave him the eiteach, a "
            "crozier fallen from Heaven that could fly; the Bishop of Down "
            "holds it now.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "machaoi_island",
        "Machaoi Island",
        inside=cuan,
        aura=3,
        summary=(
            "The largest island of Lough Cuan, where Nendrum Monastery lies "
            "in ruins, wrecked in 806 in the magical battle between Diedne "
            "and Pralix, though no one knows which of them did it. Magic "
            "aura 3. The aura seems to stir up discord and strife among "
            "women, which is why no Hermetic covenant has settled here."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "leath_cathail",
        "The Leath Cathail Peninsula",
        inside=cuan,
        aura=2,
        summary=(
            "The peninsula at Lough Cuan's southern mouth, where Diedne and "
            "Pralix carried their fight on after Nendrum; it has a Magic "
            "aura of 2 throughout, with the same taint of strife between "
            "women as Machaoi Island."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "giants_causeway",
        "The Giants' Causeway",
        inside=region,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Clochán na bhFomóraig, a mass of locked many-sided rock columns "
            "on the north coast that step down from the clifftops and on "
            "under the sea; wind and waves draw a weird whistling from it, "
            "like hundreds of pipes out of tune. Faerie aura 3.",
            "One tale says Fionn mac Cumhaill built it to walk to Scotland "
            "and fight Benandonner. An older one says the Tuatha Dé laid "
            "their curse on the Fomórach here: each column is a year of the "
            "curse, and when sea and wind have ground all 40,000 to sand, "
            "Ireland lies open to the Tuatha Dé's old enemies again.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "mournes",
        "The Mountains of Mourne",
        inside=region,
        realm="Faerie",
        aura=2,
        summary=paragraphs(
            "Beanna Boirche, Boirche's Hills, heather mountains in the south "
            "of the earldom, notorious for thick mists in which travellers "
            "lose their way; the locals blame the faeries. While mist lies on "
            "them they have a Faerie aura of 2.",
            "The highest, Sliabh Dómhanghairt, is named for Saint "
            "Dómhanghart, a follower of Patrick, who never died but keeps "
            "watch on its summit for ever over the graves on Sliabh Crúibe.",
        ),
        **KNOWN_REGION,
    )
    cruibe = _add(
        hibernia,
        "sliabh_cruibe",
        "Sliabh Crúibe",
        inside=region,
        summary=paragraphs(
            "The 'mountain of the hoof', across a valley north of the "
            "Mournes, said to be where twelve kings lie buried. On Cairn "
            "Sunday, the first Sunday in August, the locals climb it, each "
            "bringing a stone to help bury the kings, though the legend "
            "does not say why.",
            "Vis: some of the stones carried up hold vis, gathered over "
            "many years and spread among many stones; magi have noticed. "
            "No one holds it.",
            "",
        ),
        secrets="The kings must stay buried. Eleven of the twelve graves "
        "hold a demon bound into a dead tyrant's body. The "
        "Cailleacha Phiseogach know a legend that if mortal hands "
        "uncover the kings they will rise, and that when a twelfth "
        "king joins them the world will end. They cannot dig the "
        "graves themselves, so they mean to lure vis-hungry magi "
        "into doing it.",
        **RUMOURED,
    )
    _add(
        hibernia,
        "rath_chinneich",
        "Rath Chinneich",
        inside=cruibe,
        summary=paragraphs(
            "A fortress the four sons of Madán Muinreamhair, king of the "
            "Fomórach, built for Nemed in a single day at his command; when "
            "it was done Nemed killed them so they could build no better "
            "for anyone else. Four hills nearby mark the graves of Bog, "
            "Robhog, Ruibhne and Rodan. Chapter two sets the fort, Ráth "
            "Cinn-Eich, on the slopes of Slieve Croob, with passages the "
            "brothers dug beneath it; House Diedne later built the Widow's "
            "Throat over its ruins.",
            "Fomórach are hard to kill, and some say the Mac Madáin only "
            "lie in a sleep like death, held by the Tuatha Dé's curse; the "
            "day they wake they will hunt Nemed's descendants for revenge.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "ballynoe",
        "Ballynoe",
        inside=region,
        aura=3,
        summary=paragraphs(
            "A great stone circle in the Mournes, named for the nearby "
            "settlement of an Baile Núa: over fifty close-set stones six "
            "feet tall in a ring almost 30 paces across, with a portal "
            "entrance on the west and, facing it inside, a horseshoe of "
            "stones over a stone-lined chamber underground. Magic aura 3.",
            "It is an exact twin of the circle at Swinside in Cumbria, and "
            "the two are joined by a lasting enchantment like Opening the "
            "Intangible Tunnel but of no apparent limit. Magi know of it but "
            "not where it came from or how best to use it. Original "
            "research here could yield a Major Breakthrough letting Hermetic "
            "magic join two places the same way; the flawed Hermes' Portal "
            "spell and Mercere's Portal enchantments may help.",
        ),
        **KNOWN_TRIBUNAL,
    )
    gullion = _add(
        hibernia,
        "ring_of_gullion",
        "The Ring of Gullion",
        inside=region,
        realm="Faerie",
        aura=2,
        summary=(
            "A strange perfect ring of hills round a central mountain, "
            "Sliabh gCuillinn, which has a Faerie aura of 2; the Cailleach Beara, a "
            "winter goddess of the faerie kind, haunts the lake on top."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "gullion_lake",
        "The Lake of Sliabh gCuillinn",
        inside=gullion,
        realm="Faerie",
        aura=5,
        summary=(
            "The Cailleach Beara's lake, Faerie aura 5. Whoever swims in it "
            "comes out old, fifty years older with Aging Points enough to "
            "raise their Decrepitude by 2. She may be begged to undo it, but "
            "even then some mark remains; Fionn mac Cumhaill, whom the crone "
            "goddess tricked, got his white hair here."
        ),
        **KNOWN_REGION,
    )


# ---------------------------------------------------------- Tír Fhomóraig


def _tir_fhomoraig(hibernia: Hibernia) -> None:
    ulster = hibernia.places["ulster"]
    region = _add(
        hibernia,
        "tir_fhomoraig",
        "Tír Fhomóraig",
        inside=ulster,
        summary=paragraphs(
            "The Kingdom of the Fomórach, on the islands north of Ireland "
            "since the Tuatha Dé threw them out after the Second Battle of "
            "Magh Tuireadh. Its two chief strongholds are Rathlin and "
            "Toraigh, though Fomórach are rumoured as far off as Islay and "
            "Arran in Scotland. Pure-blooded births have all but stopped; "
            "they do not age but still die of mishap and sickness, and "
            "fewer than a hundred may be left, a number still falling.",
            "Their king, Madán Muinreamhair ('thick-neck'), has no love for "
            "men, since Nemed killed his four sons at Rath Chinneich, but he "
            "has come to see humans as his race's only hope and has arranged "
            "marriages with the Cruithnigh of Rathlin. His people loathe "
            "these half-breeds and Pict-bloods, but may have no choice.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "rathlin",
        "Rathlin Island",
        inside=region,
        summary=paragraphs(
            "Inis Reachlainn, Pliny's Reginia and Ptolemy's Rhicina, where "
            "the Dál nAraidhe and the Fomórach live together and have held "
            "off both the Norsemen of Man and the Normans. The humans are "
            "Christian and the Fomórach are not; between them stand human "
            "priests with Fomóir blood who worship the Fomóir gods, Domnu "
            "the primal darkness above all, and are otherwise just like the "
            "gruagachan. King Madán keeps a tower on the southernmost point, "
            "from which he stares at the land he may never set foot on.",
        ),
        **KNOWN_TRIBUNAL,
    )
    toraigh = _add(
        hibernia,
        "toraigh",
        "Toraigh Island",
        inside=region,
        summary=(
            "An island nine miles off the north coast, home to some two "
            "dozen Fomórach, where no human dares land. It was once the "
            "Fomóir capital: King Conand ruled from a great tower the "
            "Nemedians threw down, which Balor Bailcbhéimneach ('strong smiting'), "
            "Balor of the Evil Eye, who came after him, built again. No "
            "Fomóir king lives on Toraigh now."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "tur_bhalair",
        "Túr Bhalair",
        inside=toraigh,
        summary=paragraphs(
            "'Balor's Tower', an unclimbable peak on Toraigh. Here Balor "
            "locked away his daughter Eithne, yet Cian of the Tuatha Dé got "
            "in and fathered Lugh on her; from its top Balor glared over "
            "Ireland, and the bare slopes of the Poisoned Glen still show "
            "it. Rumour says an Aspect of Balor sometimes comes back.",
            "Balor is among the mightiest of the primal Fomóir, a great "
            "daimon of the Magic realm who acted in the world through "
            "Aspects; since his half-blood grandson Lugh beat him at the "
            "Second Battle of Magh Tuireadh he has kept out of the mortal "
            "world, as he agreed with the Tuatha Dé. His usual Aspect was a "
            "huge monster with one venomous, fiery eye under seven covers: "
            "with one off plants withered, with three wood smoked, with five "
            "sparks flew, and with all seven gone whatever he looked on "
            "burst into flame, and living things in his gaze burned, turned "
            "to stone or fell dead as he chose. Anyone caught even by the "
            "edge of his glance was his for a year, to curse when he "
            "pleased.",
        ),
        **RUMOURED,
    )


# ----------------------------------------------------------- the world


def _lords(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["hugh_de_lacy"] = b.lord(
        "Earl of Ulster",
        title="count",
        wealth="Wealthy",
        seat="Carrickfergus Castle",
        ruler="Hugh de Lacy",
        place=p["earldom"],
        summary=paragraphs(
            "Hugh de Lacy, a younger son of Meath's English lord and "
            "brother of Walter de Lacy, who arrested John de Courcy for "
            "rebellion in 1203 and in May 1205 was made the first Earl of "
            "Ulster by King John, with all the lands de Courcy had held. The "
            "earldom is a Liberty: he runs it for the English crown and "
            "owes the Lord of Ireland his service and the king's revenues. "
            "He holds it from Carrickfergus, which he has strengthened, and "
            "has fortified Dundrum, the Millmount bailey at Drogheda and "
            "more. He has given most of Cuailnge and Muirtheimne to English "
            "knights hunting for baronies, and a knight leave to put a motte "
            "on Inisclabhall. Whether Tír Chonaill still pays the tribute "
            "de Courcy forced on it in 1196 the book does not say.",
        ),
    )
    w["king_tir_chonaill"] = b.lord(
        "King of Tír Chonaill",
        title="duke",
        seat="Donegal",
        ruler="Domhnall Mór mac Eicnechain Ua Domhnaill",
        place=p["tir_chonaill"],
        summary=(
            "Domhnall Mór mac Eicnechain, of Conall Gulban's line, the "
            "second king of Tír Chonaill from the Uí Domhnaill, a branch of "
            "the Uí Néill. He rose by leaning on the Lucht Tighe, his eight "
            "household families, and keeps his kingdom free of the English "
            "with his gallóglaigh rather than a levy of clansmen: better "
            "armed and trained, but fewer. He is close allied with Tír "
            "Eóghain. De Courcy made Tír Chonaill pay tribute after beating "
            "its king in 1196 and ravaged the north in 1198; Raphoe's "
            "cathedral still lies as he left it."
        ),
    )
    w["king_tir_eoghain"] = b.lord(
        "King of Tír Eóghain",
        title="duke",
        seat="Aileach",
        ruler="Aed Meith mac Aeda Ua Néill",
        place=p["tir_eoghain"],
        summary=(
            "Aed Meith mac Aeda Ua Néill, the first Uí Néill king of Tír "
            "Eóghain, who took power from Aileach in 1185; the Cenél "
            "nEóghain have ruled Aileach ever since, and the young kingdom "
            "now dominates its old overlords. Allied with Tír Chonaill, and "
            "one of the 'five bloods', the greatest túatha of Ireland. Doire is under "
            "the Mac Lochlainn, who were the Cenél nEóghain's kings until the Uí "
            "Néill took over."
        ),
    )
    w["king_airgialla"] = b.lord(
        "King of Airgíalla",
        title="duke",
        seat="Clogher",
        ruler="Donnchad Ua nAnluain",
        place=p["airgialla"],
        summary=(
            "Donnchad Ua nAnluain, king of the nine sub-kingdoms of "
            "Airgíalla, ruled from Clogher. Since the English came he has "
            "moved soldiers into his half of Drogheda and seems ready to "
            "stop them taking it, though they already hold the lands just "
            "north and west of it. Fermanagh, once among his strongest "
            "tributaries, has lost most of its freedom."
        ),
    )


def _churches(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["bishop_raphoe"] = b.church(
        "Bishopric of Raphoe",
        church="Bishop's cathedral",
        place=p["tir_chonaill"],
        summary=(
            "An Irish see. Saint Columba settled Ráth Bhoth and founded a "
            "monastery here, which his kinsman Saint Adomnán enlarged; the "
            "bishop's cathedra is dedicated to Adomnán, but the church has "
            "not been rebuilt since John de Courcy destroyed it in 1198. "
            "Beltany Tops stands two miles south."
        ),
    )
    w["bishop_doire"] = b.church(
        "Bishopric of Doire",
        church="Bishop's cathedral",
        place=p["tir_eoghain"],
        summary=(
            "An Irish see of the province of Armagh, whose cathedral, the "
            "great Tempull Mór, was finished in 1160. Saint Columba founded "
            "a monastery at Doire in the sixth century after beating the "
            "druids of its oak grove in a battle of words; they swore to "
            "return and never did."
        ),
    )
    w["bishop_clogher"] = b.church(
        "Bishopric of Clogher",
        church="Bishop's cathedral",
        place=p["airgialla"],
        summary=(
            "An Irish see, its bishop more often called the Bishop of "
            "Airgíalla. Its cathedral keeps the golden stone that gives "
            "Cloch Oir its name, a gold-clad idol once the relic of a pagan "
            "cult: its god, Cermand Cestach, spoke through a ban fáith, a "
            "druid priestess, and saw the future uncannily well."
        ),
    )
    w["bishop_down"] = b.church(
        "Bishopric of Down",
        church="Bishop's cathedral",
        place=p["earldom"],
        summary=paragraphs(
            "The see of the earldom, Anglo-Irish since the conquest, seated "
            "at Downpatrick, where Saint Patrick is buried in the cathedral "
            "grounds. Saint Malachy gave up Armagh in 1137 to become Bishop "
            "of Down, ruled the diocese from Bangor, enlarged the cathedral "
            "and brought Augustinian canons; in 1183 John de Courcy made it "
            "a cathedral priory of Benedictines from Chester.",
            "The bishop holds the eiteach of Saint Machaoi, the crozier "
            "from Heaven that once belonged to the abbots of Nendrum: a "
            "relic with 2 Faith Points that lets up to four people fly while "
            "they keep hold of it.",
        ),
    )
    w["bangor_abbey"] = b.church(
        "Bangor Abbey",
        church="Monastery or nunnery",
        answers_to=w["bishop_down"],
        place=p["bangor"],
        founded=555,
        summary=paragraphs(
            "Beannchor Mór, Saint Comgall's abbey of 555, an Irish house "
            "famed for its learning, the equal of the great theological "
            "schools abroad, and for the missionaries it sent across Mythic "
            "Europe. Viking raids in the eighth and ninth centuries hurt it "
            "badly, but a miracle saved it. Saint Malachy was abbot here "
            "until lately, and Bishop of Down too.",
            "Its perpetual harmony is an antiphonal chant that never stops, "
            "praising God without a break; the choir holds a Holy Tradition "
            "of Cantores, who can turn the monks' endless prayer to "
            "miracles. Anywhere the song can be heard has a Dominion aura of "
            "6, usually of Calm temper.",
        ),
    )
    w["downpatrick_priory"] = b.church(
        "Downpatrick Cathedral Priory",
        church="Bishop's cathedral",
        order="Benedictine",
        answers_to=w["bishop_down"],
        place=p["earldom"],
        founded=1183,
        summary=(
            "Anglo-Irish: the Benedictines from Chester whom John de Courcy "
            "set in Down's cathedral in 1183, keepers of Saint Patrick's "
            "grave. When Ulaidh and Uí Néill fought over the saint's body, "
            "it was carried off on a cart drawn by two oxen, but a "
            "miraculous vision of a second cart and team fooled the Uí "
            "Néill, and the body stayed at Dún Leathghlaise."
        ),
    )
    w["iniscourcy"] = b.church(
        "Iniscourcy Abbey",
        church="Monastery or nunnery",
        order="Cistercian",
        answers_to=w["bishop_down"],
        place=p["earldom"],
        founded=1180,
        summary=(
            "An Anglo-Irish Cistercian abbey John de Courcy founded in 1180 "
            "to atone for destroying Erenagh nearby in 1177; its monks came "
            "from Furness in England, with Erenagh's survivors. Some of "
            "those survivors meet in secret at Erenagh's ruins."
        ),
    )
    w["mainistir_liath"] = b.church(
        "Mainistir Liath",
        church="Monastery or nunnery",
        order="Cistercian",
        answers_to=w["bishop_down"],
        place=p["lough_cuan"],
        summary=(
            "An Anglo-Irish Cistercian abbey on the Ards Peninsula, founded "
            "by John de Courcy's Manx wife."
        ),
    )
    w["newry_abbey"] = b.church(
        "The Abbey of Iúbhar Chinn Trábha",
        church="Monastery or nunnery",
        order="Cistercian",
        place=p["earldom"],
        founded=1142,
        summary=(
            "An Irish Cistercian house, 'the yew at the head of the strand', "
            "called Newry by the English, in the valley between the Mournes "
            "and the Ring of Gullion. The old monastery was rebuilt in 1142 "
            "and given to the Cistercians, and a small town has grown up to "
            "serve the monks."
        ),
    )
    w["purgatory"] = b.church(
        "The Purgatory of Saint Patrick",
        church="Monastery or nunnery",
        order="Augustinian",
        answers_to=w["bishop_clogher"],
        place=p["lough_dearg"],
        summary=paragraphs(
            "One of Ireland's greatest pilgrim shrines, on Inisphadraig in "
            "Lough Dearg, kept by an Irish chapter of Augustinian canons. "
            "To settle the doubts of some converts, Patrick asked God for a "
            "proof and a pit opened where he stood, through which the joys "
            "of Heaven and the pains of Hell can be seen.",
            "The canons house and feed the penitents and draw lots among "
            "them for who keeps the night's vigil; those who keep it are "
            "taken through the horrors of Purgatory.",
        ),
    )
    w["daimhinis"] = b.church(
        "Daimhinis",
        church="Monastery or nunnery",
        order="Augustinian",
        answers_to=w["bishop_clogher"],
        place=p["lough_erne"],
        summary=(
            "An Irish Augustinian house on an island of Lower Lough Erne, "
            "one of many there, whose round tower is a landmark for boats "
            "among the islands; its monks ring the bell when they see "
            "visitors, and the call passes from tower to tower up the lough."
        ),
    )


def _towns(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["donegal"] = b.town(
        "Donegal",
        charter="Noble lord",
        ruler="Domhnall Mór Ua Domhnaill",
        answers_to=w["king_tir_chonaill"],
        place=p["tir_chonaill"],
        summary=(
            "Dun na nGaill, the 'fort of the foreigners', the largest town "
            "of Tír Chonaill and a stronghold of the Uí Domhnaill, founded "
            "by Norse settlers as a port. Most of the king's gallóglaigh "
            "live here, twenty corrughadh of about a hundred men each "
            "camped in and around the town, which is not always happy to "
            "have them."
        ),
    )
    w["doire"] = b.town(
        "Doire",
        charter="Church",
        answers_to=w["bishop_doire"],
        place=p["tir_eoghain"],
        summary=paragraphs(
            "Derry to the English, 'oak grove' in Irish, on the Foyle: a "
            "ritual site of the druids before Saint Columba founded his "
            "monastery, and now the seat of one of Armagh's bishops, with the "
            "Tempull Mór. Vikings from Man still raid it, and its sea side is "
            "strongly walled. From the market square at its heart four streets "
            "(Butcher's gate, Shipquay gate, Ferryquay gate and Bishop's gate) run "
            "out to four gates in the walls. The Mac "
            "Lochlainn protect it.",
            "The English have just built the fort of Greencastle at the "
            "mouth of Lough Foyle; the book names its builder Hugh de "
            "Burgos.",
        ),
    )
    w["armagh_town"] = b.town(
        "Armagh",
        charter="Church",
        place=p["airgialla"],
        summary=paragraphs(
            "Ard Mhacha, seat of one of Ireland's four archbishops and, to "
            "many, the first holy place of Ireland. Saint Patrick founded it "
            "when a series of miracles persuaded a lord named Dáire to give "
            "him the hill of Droim Saileach, whose monastery grew into the "
            "city. Built into the wall of the cathedral's nave is a pagan "
            "idol of Nuada of the Silver Arm, king of the Tuatha Dé, found "
            "at Tóin re Gaoith nearby; the cathedral also keeps the skull of "
            "Conchobhar mac Neasa.",
            "The Shrine of the Bell holds Bethechan, a little iron handbell "
            "Saint Colm Cille took from Patrick's grave, in a bell-shaped "
            "reliquary rich with gold and gems; the Ua Mellain family have "
            "kept it for four hundred years.",
        ),
    )
    w["clogher"] = b.town(
        "Clogher",
        charter="Noble lord",
        ruler="Donnchad Ua nAnluain",
        answers_to=w["king_airgialla"],
        place=p["airgialla"],
        summary=(
            "Cloch Oir, the 'golden stone', capital of Airgíalla and its "
            "bishop's seat, named for the gold-covered idol in the "
            "cathedral."
        ),
    )
    w["drogheda_airgialla"] = b.town(
        "Drogheda-in-Airgíalla",
        charter="Noble lord",
        ruler="Donnchad Ua nAnluain",
        answers_to=w["king_airgialla"],
        place=p["airgialla"],
        summary=(
            "Droichead Atha, the 'bridge of the ford', is split by the "
            "Boyne. The English hold Drogheda-in-Meath on the south bank, "
            "with the Norse fortress they took and strengthened (chartered "
            "1194); Drogheda-in-Airgíalla on the north bank grew from the "
            "trading post that served the castle. The king of Airgíalla has "
            "garrisoned it and seems ready to keep the English out."
        ),
    )
    w["downpatrick"] = b.town(
        "Downpatrick",
        charter="Noble lord",
        ruler="Hugh de Lacy",
        answers_to=w["hugh_de_lacy"],
        place=p["earldom"],
        summary=paragraphs(
            "Once Dún Leathghlaise, lately renamed Dún Phádraig, 'Patrick's "
            "stronghold', for the saint buried in its cathedral grounds; it "
            "was the capital of the old Dál bhFiatach kingdom, and the "
            "pilgrims from Saulpatrick end here.",
            "Its first fort, Rath Cealtchair, belonged to Celtchair mac "
            "Uitheachair, a huge ugly man whose bulbous nose, wing-like "
            "ears and rough grey hair betrayed Fir Bolg blood. He fought in "
            "all of Conchobhar's great battles, but for a murder done in "
            "rage he was bound by a geas to save Ulster from its three worst "
            "evils: the Fomóir Conganchneas, 'horny skin', whom no weapon "
            "could hurt until Celtchair's daughter learned that red-hot "
            "spikes through his soles would kill him; the monstrous hound "
            "Luchdhonn, whose heart he tore out through its throat; and his "
            "own dog Daolchú, one of Luchdhonn's three whelps (the others "
            "became Mac Da Thó's hound and the smith Culann's), meek with "
            "him but a terror when he was away. He speared it, its blood "
            "poisoned him, and he died.",
            "His spear, the Lúin Cheltchair, which Celtchair picked up where the "
            "Second Battle of Magh Tuireadh was fought, is a weapon of great power "
            "and "
            "almost certainly one of the Four Treasures of the Tuatha Dé. It "
            "had to be kept in a cauldron of blood or its shaft would burst "
            "into flame and it would run its owner through, and the silver "
            "rings round its head spun and rattled when battle was near. "
            "After Celtchair it passed to the sinister Dubhthach Daol Uladh, "
            "who died by it, as did Cúscraidh Meann Macha after him. Where it "
            "is now no one knows. Celtchair very likely knew the clesrada.",
        ),
    )
    w["dundrum"] = b.town(
        "Dundrum",
        charter="Noble lord",
        ruler="Hugh de Lacy",
        answers_to=w["hugh_de_lacy"],
        place=p["earldom"],
        summary=(
            "The port that has grown round Dundrum Castle, now one of the "
            "earldom's most important."
        ),
    )


def _factions(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["lucht_tighe"] = b.faction(
        "The Lucht Tighe of Tír Chonaill",
        faction="Family",
        decides="Its leader",
        ruler="Domhnall Mór Ua Domhnaill",
        place=p["tir_chonaill"],
        wants="Their hereditary offices under the Uí Domhnaill",
        offers="Brehons, scribes, physicians, bards, horse and the gallóglaigh",
        summary=(
            "The household families that carry the running of Tír Chonaill "
            "for the Uí Domhnaill: Mac Robhartaigh (keepers of the cathach), "
            "Mac Suibhne (chiefs of the gallóglaigh), Uí Breisléin "
            "(brehons), Uí Cléirigh (scribes and historians), Mac "
            "Duinnshleibhe (physicians), Uí Firghil (the clan's rites), Uí "
            "Gallchobhair (cavalry), Uí Tiománagh (herdsmen) and Mac "
            "a'Bháird (bards). The book calls them eight but names nine. "
            "Some covenants keep a Lucht Tighe of their own among their "
            "covenfolk."
        ),
    )
    w["galloglaigh"] = b.faction(
        "The Gallóglaigh of Donegal",
        faction="Brigands and mercenaries",
        decides="Its leader",
        members=2000,
        ruler="the Mac Suibhne",
        place=p["tir_chonaill"],
        wants="Pay and plunder",
        offers="Heavy infantry, the defence of Tír Chonaill",
        summary=(
            "The 'foreign warriors' of the Uí Domhnaill, mostly of mixed "
            "Norse and Gaelic blood come over from the Isles, the Norse kingdom off "
            "Scotland's west coast: twenty corrughadh of about a hundred men, "
            "superb with battle-axe and greatsword and all in mail. Tír "
            "Chonaill relies on them and not on a levy, and owes its freedom "
            "from the English to them, but they are a sore point in Donegal."
        ),
    )


# ---------------------------------------------------------- Leth Cuinn

#: The eighteen clesa Úathach teaches, by the Ability they use.
CLESA = (
    "Athletics. Baí Brasse, the Profit of Speed (Qik): hurry at three "
    "times and run at six times walking pace for a round. Cless Caitt, "
    "the Cat Feat (Dex): a standing long jump of up to eight times one's "
    "height, less Encumbrance. Ich-n-Erred, the Hero's Salmon Leap (Str): "
    "a standing high jump of up to four times one's height, less half "
    "Encumbrance. Ochtarchless, the Eight-Men Feat (Sta): +5 Strength to "
    "lift or bear a weight, held while the rolls keep succeeding. "
    "Rothchless, the Wheel Feat (Str): hurl what one could not normally "
    "throw, such as a chariot wheel, its Load as its damage. Tétchless, "
    "the Rope Feat (Dex, Ease Factor 3 and up for unstable, moving or "
    "sloping footing): balance on anything smaller than a foot, and "
    "soften falls.",
    "Concentration. Cless for Análaib, the Breath Feat (Sta): hold one's "
    "breath for minutes, or +3 to a precise task after three rounds of "
    "preparing. Corpchless, the Body Feat (Dex, 6, 9 or 12): dislocate "
    "joints to slip shackles or squeeze through small gaps, and +3 to "
    "break a grapple. Sáebchless Díberge, the Wild Feat of Contortion "
    "(Qik): bend the body unnaturally for +3 to trips, disarms and the "
    "like, or to resist them. Siaburchles, the Phantom Feat (Qik): give "
    "no defence and let a blow pass through a body made partly "
    "insubstantial, never two rounds running.",
    "Single Weapon (or Great Weapon, chosen at Initiation). Béim Co "
    "Commus, the Stroke of Precision (Dex): harmless feats of exactness "
    "with a blade, such as trimming a beard in a fight. Brúd nGeme, the "
    "Crushing Roar (Sta): a hit that damages the foe's weapon, harder "
    "against fine or enchanted ones. Fáenchless, the Sloped Shield Feat "
    "(Str): with an Irish edged shield, turn a winning parry into a "
    "glancing attack. Foramchles, the Swooping Feat (Sta): a leaping "
    "swing that ruins the armour on one location.",
    "Thrown Weapon. Cless Cletenach, the Javelin Feat (Dex): one javelin "
    "drives another for a 15-pace range increment and doubled damage. "
    "Cless Nónbair, the Nine-Men Feat (Str): up to nine javelins at one "
    "target at once. Torannchless, the Thunder Feat (Str): a sling stone "
    "to the head, with a thunderclap, that knocks the foe down. "
    "Ubullchless, the Apple Feat (Dex): juggle up to nine stones in one "
    "hand, loading a sling without pause or throwing three a round.",
)


def _leth_cuinn(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    neagh = hibernia.places["lough_neagh"]
    summary = paragraphs(
        "The northern Mercer House, on the north-eastern shore of Lough "
        "Neagh where the Slighe Mhidhluachra bends west for Doire. Like "
        "Leth Moga, its southern partner, it is not a covenant at law: it "
        "has no cathach and needs no cattle, for the Peripheral Code "
        "itself guarantees it, and it bears no device the book records. "
        "Its Redcaps serve the covenants of the northern half of the "
        "Tribunal, chiefly on three High Roads: an tSlighe Mhór, the Slighe Assail "
        "and the Slighe Mhidhluachra.",
        "Where Leth Moga keeps records, Leth Cuinn is warlike: it trains "
        "warriors and heroic Redcaps, and since 1029 it has been an outpost "
        "of the Cult of Heroes, run by Dáire Farranta's descendants and "
        "home to Úathach, the only living teacher of the clesrada. It is "
        "built like a king's hall, a bold gesture in the Earl of Ulster's "
        "lands, hidden from chance discovery by The Shrouded Glen; on the "
        "parade ground before it up to a dozen men at a time drill at "
        "gymnastics, weapons and feats of strength and endurance.",
        "Leaning: Irish in sentiment. House Mercere is neutral by custom, "
        "but its leader despises the English-friendly bookishness of Leth "
        "Moga, and his heir, Dáire an Chogaidh, hates the English and has "
        "even voted at Tribunal.",
    )
    what_matters = joined_lines(
        "Income: the Peripheral Code's guarantee and the Tribunal's "
        "covenants, which pay for Initiation into the clesrada",
        "Services: Initiation into the clesrada for Redcaps, grogs and "
        "companions; the training of covenants' warriors",
        "Price of Initiation: longevity rituals for the Tribunal's Redcaps, "
        "three years' casting of the Aegis of the Hearth and The Shrouded "
        "Glen (Leth Cuinn gives the vis and the casting tablets), or "
        "enchantments for its Redcaps",
        "Library: none described; the clesrada are taught in person by Úathach",
        "Boon: Veteran Fighters (a large turb trained in the clesrada)",
        "Boon: Mystical Allies (Úathach, a faerie of the Tuatha Dé)",
        "Boon: Hidden Ways (The Shrouded Glen hides the hall)",
        "Hook: Mercer House",
        "Hook: Superiors (House Mercere's primus may answer Dáire an Chogaidh's vote)",
        "Hook: Rival (Leth Moga, whose leader Dáire Cú scorns)",
        "Tension: Dáire an Chogaidh's votes against the House's neutrality",
        "Tension: the Earl of Ulster's lands all round a king's hall",
    )
    notes = paragraphs(
        "History. From its founding in 898 Leth Cuinn cared for martial "
        "skills. In 1029 Dáire Farranta came back after seven years away "
        "and challenged its leader, his own parens, to Wizard War; both "
        "were unGifted, and Dáire won without a spell, by feats of speed "
        "and swordplay out of legend, the clesrada. He exiled the other "
        "Redcaps and filled the house with his kin, among them Úathach, "
        "the faerie woman who had taught him. He made it a house of the "
        "Cult of Heroes, House Mercere's society that seeks to bring back "
        "the heroes of old by training exceptional people as champions, "
        "heroes and perhaps demigods; his heirs still rule it. Dáire "
        "Farranta also killed the péist of Lough Neagh.",
        "Úathach of the Glen. The name means 'spectre'. She has not aged "
        "a day since she came with Dáire Farranta: a faerie of great "
        "power, one of the few Tuatha Dé still active in Hibernia, a "
        "granddaughter of the battle gods Nuadha and Badhbh, and the "
        "daughter of Scáthach, Cú Chulainn's teacher, and his lover in the "
        "tales. She feeds on the vigour young warriors spend learning and "
        "practising war. She is severe, hatchet-nosed, her dark hair "
        "streaked grey and drawn back tight; she always wears leather "
        "armour and is never without nine javelins or more, a staff-sling and a "
        "thrusting spear, and her right forefinger is badly set, broken, "
        "they say, by Cú Chulainn when they first met. She is ritually "
        "married to Dáire Cú, a union more than symbolic since his mortal "
        "wife died. She has no stat block.",
        "Culture. All the Redcaps and most of the sizable turb practise "
        "the clesrada, which take constant hard training in weapons and "
        "athletics; at Tribunal its people are known for superb fitness "
        "and for showing it off. Its Redcaps also train grogs and "
        "companions the covenants send, and Dáire an Chogaidh can make a "
        "fighting force of raw recruits in months.",
        "The clesrada. The clesa ('feats', singular cles) were the Ulster "
        "heroes' displays on the battlefield, the exercise ground and in "
        "the king's hall, part weapon-play, part juggling, part magic. "
        "Lugh was held to have invented them, hence Ildánach, 'skilled in "
        "every art'; Cú Chulainn mastered all of them, one known only to "
        "him and to his son Connla, whom he taught it. Scáthach, daughter "
        "of Nuadha, taught them on Skye with her sons Cúar, Cet and "
        "Cruife; Cú Chulainn studied there a year and a day. Úathach "
        "alone teaches them now.",
        "Each cles is a separate Initiation (Ease Factor 15; Úathach's "
        "Presence + Organization Lore: Clesrada is 12): a quest tied in "
        "symbol to the feat, then a geas, a Prohibition Flaw linked to the "
        "feat that is in effect the charm that works it; break it and the "
        "cles is gone. Every script takes the geas as an Ordeal and none "
        "counts an earlier Ordeal, so the unGifted can be Initiated. "
        "Úathach also lays a geas, outside the Initiation, on every "
        "Initiate never to Initiate anyone else, on pain of losing every "
        "cles. Her sample script, the Ubullchless by Quest and Ordeal "
        "(+6): the Initiate leaves with an apple pip after a rite, and "
        "within a year and a day returns with an enchanted apple freely "
        "given by the supernatural creature that owned it (+3), then "
        "accepts the geas she whispers (+3), most often about apples or "
        "apple trees.",
        "Using clesa. A cles may be used as often as wished, at no cost "
        "unless its text says so, by a stress roll of an Ability; a botch "
        "always costs a Fatigue level. They are Faerie powers, each roll "
        "like a 15th-level spell with Penetration 0 plus the Penetration "
        "bonus, so magic that affects spells, an Aegis included, can touch "
        "them, but they act on the user, like Aimed spells, and need not "
        "penetrate a foe's resistance; while one works the user counts as "
        "magical. Several clesa of the same Ability may be chained into "
        "one action, each rolled in turn until one fails, with nothing "
        "else that round, an Attack included: a Redcap may run down a "
        "horse with the Profit of Speed, leap onto it with the Salmon Leap "
        "and keep his feet with the Rope Feat in one round. The troupe may "
        "invent more. With the Rope Feat, Perfect Balance adds its +6.",
        *CLESA,
        "Magi: seven Redcaps, none Gifted: Dáire Cú, five of his sons and "
        "daughters (Dáire an Chogaidh the eldest, Elen Bhodhar the "
        "youngest) and a nephew. No season is given.",
    )
    leth_cuinn = b.covenant(
        "Leth Cuinn",
        tribunal=tribunal,
        founded=898,
        place=neagh,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=4,
        detail=FULL,
        season="Summer",
    )
    hibernia.covenants["leth_cuinn"] = leth_cuinn
    b.book(
        leth_cuinn,
        "The library of Leth Cuinn",
        "Other",
        language="Latin",
        description=(
            "The book names no books and describes no library. What Leth "
            "Cuinn keeps is the clesrada, taught in person by Úathach "
            "through Initiation, and its Redcaps' knowledge of the northern "
            "High Roads."
        ),
    )
    m = hibernia.magi
    m["daire_cu"] = b.magus(
        "Dáire Cú Ua Dáire Ua Mearcaire",
        covenant=leth_cuinn,
        house=MERCERE,
        age=82,
        summary=paragraphs(
            "The unGifted leader of Leth Cuinn, who looks sixty-three; he "
            "took the house from his father, Dáire Direach, and is shaping "
            "his eldest son, Dáire an Chogaidh, to follow him. He is "
            "ritually wed to Úathach, and since his mortal wife died the "
            "marriage has been more than a form. He has nothing but scorn "
            "for the Redcaps of Leth Moga, and thinks their leader too "
            "doddering and bookish to lead the Tribunal's Redcaps.",
        ),
        traits={"Loyal to Family": 3, "Uncompromising": 2, "Loyal to Order": 1},
    )
    m["daire_an_chogaidh"] = b.magus(
        "Dáire an Chogaidh Mac Dáire Cú",
        covenant=leth_cuinn,
        house=MERCERE,
        age=65,
        summary=paragraphs(
            "Dáire Cú's eldest son, an unGifted Redcap who looks forty-eight. "
            "In his macgnímartha he fought de Courcy's English with the "
            "army of Ulster, which is how he got his name, 'of the wars'. He "
            "is against everything English and has even voted at Tribunal, "
            "for all his House's custom of neutrality; it has made him "
            "something of a celebrity, and the primus of House Mercere is "
            "rumoured to be readying an answer.",
            "He is more often on the drill ground with warriors than out on Ireland's "
            "roads, which is just where his father, "
            "well aware of his temper, wants him: a superb, frightening "
            "drill-master.",
        ),
        traits={"Aggressive": 3, "Hatred of the English": 3, "Humble": -2},
    )
    m["elen"] = b.magus(
        "Elen Bhodhar inghean Dáire Cú Ua Mearcaire",
        covenant=leth_cuinn,
        house=MERCERE,
        age=19,
        summary=paragraphs(
            "Elen the Deaf, youngest of Dáire Cú's five children, an "
            "unGifted Redcap of nineteen. Her mother died bearing her, and "
            "she was born without hearing; she reads lips perfectly and "
            "speaks through mime and a rough sign language. She has just "
            "finished her Redcap training and begun to ride Ireland's roads.",
        ),
        traits={"Eager": 3, "Self-Reliant": 1, "Brave": -2},
    )


# --------------------------------------------------------- Qui Sonant


def _qui_sonant(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    cuailnge = hibernia.places["cuailnge"]
    grounds = _add(
        hibernia,
        "qui_sonant_grounds",
        "The Burial Grounds of Qui Sonant",
        inside=cuailnge,
        aura=7,
        summary=paragraphs(
            "A ridge high in the Cuailnge mountains, reached only by "
            "dangerous winding tracks and often snowbound in its hard "
            "winters, where local lore says the giant Finn MacCumhaill "
            "sleeps. Dolmens, cairns and mounds of pale grey stone are "
            "scattered over the hills and peaks round Qui Sonant, few easy "
            "to reach, most cold, bleak and lonely: the graves of Ireland's "
            "magi, hedge wizards, faeries and magical beasts.",
            "Magic aura 7. Each time a new tomb is raised at its edge the "
            "aura stretches to take it in (under the Realms of Power: Magic "
            "rules, each spread calls for a roll on the Aura Weakening "
            "Table). Nothing that works through an Arcane Connection reaches "
            "a target inside it: spells cannot find their mark, and magi "
            "feel their talismans drift from them; so neither the bodies "
            "nor their grave goods can be used to summon the dead while the "
            "aura shields them.",
        ),
        **KNOWN_TRIBUNAL,
    )
    hibernia.cathaigh["qui_sonant"] = {
        "cathach": "Caer Ibormeith's great gold and silver necklace"
    }
    summary = paragraphs(
        "A covenant on a ridge high in the Cuailnge mountains, where "
        "legend says the giant Finn MacCumhaill is cursed to sleep for as "
        "long as song is heard above him; its magi see that the songs never "
        "stop. It is also the last resting place of Ireland's magi, hedge "
        "wizards and even faeries and magical beasts, and a great chantry "
        "where magi and covenfolk sing without end for the souls of the "
        "fallen.",
        "Its device is a silver rope hung with balls of gold along its "
        "length; its cathach is the necklace it pictures, the huge gold and "
        "silver necklace of Caer Ibormeith. Leaning: the Ordo Hiberniae, "
        "and neutral ground for all; the English newcomers find its "
        "customs unChristian.",
        "Low stone buildings stand outside a large walled manor round a "
        "cobbled courtyard, holding sanctums, libraries and the chantry; "
        "the craftsmen's workshops lie outside the wall.",
    )
    what_matters = joined_lines(
        "Services: burial of magi, hedge wizards, faeries and magical "
        "beasts, with tombs that keep the body whole",
        "Services: summoning the spirits of the buried, by leave of the "
        "praeco or the spirit's ambassador",
        "Services: aegis tokens for all in need, and neutral ground for "
        "ending Wizard Wars",
        "Library: the inner library of funerary rites and summonings, "
        "closed to visitors",
        "Duty: each magus gives the covenant a season a year (estates, "
        "research into the dead, leading the songs)",
        "Boon: Aura (Magic 7)",
        "Boon: Prestige (neutral ground recognised by every power of Ireland)",
        "Boon: Difficult Access (treacherous mountain tracks)",
        "Hook: Ceremonies (the songs must never stop)",
        "Hook: Sanctuary (Meadhbh of Praesis and any in need)",
        "Hook: Monster (the giant sleeping under the ridge)",
        "Hook: Harsh winters",
        "Tension: Cantarus has no heir he trusts, and Finn assumes he is it",
        "Tension: Lewis's exiled rival Peter is about to widen their feud",
        "Tension: the English call the aegis tokens reckless, an opening "
        "for the Infernal",
    )
    notes = paragraphs(
        "History. Druids have always sung the giant to sleep here, and the "
        "site was already old, and already a burial ground of Ireland's "
        "magical powers, when the Order came. When those druids joined the "
        "Order a covenant formed round them, and Ireland's magi have laid their dead "
        "here from then on. The book gives no founding year. "
        "In the Schism War many magi and their heroic companions were "
        "brought here; the list of who was buried was lost after the war, "
        "though the Vitae Magna in Hibernian libraries still mention "
        "them. Some say Qui Sonant buried the three Diedne who fell at "
        "Clontarf each beside the Hermetic rival who would most have "
        "hated it.",
        "The cathach. A finely made rope of silver hung with balls of "
        "purest gold, long enough to go three times round a body, said to "
        "be the necklace of Caer Ibormeith, wife of Aengus of the Tuatha "
        "Dé. It hangs on the arch over the courtyard gate, just outside the "
        "Aegis of the Hearth. Wound round a target, it shields it from "
        "every effect of a Magic aura; here that lifts the block on Arcane "
        "Connections, so a body wrapped in it can be used to call back its "
        "spirit.",
        "The giant. If the songs end, or the giant is disturbed, the tales "
        "say it will wake and leave Ireland, taking its magic with it. "
        "Every apprentice trained here learns the songs by heart, as do "
        "magi who join later. Opinions differ on what it is, why it sleeps "
        "and what its waking would bring; the favourite answers today are "
        "a Fomóir or Finn MacCumhaill himself, and the truth may never be "
        "known.",
        "The chantry. A plain stone building from which unaccompanied "
        "chant rises day and night. To a stranger it sounds like any "
        "church's, but the songs praise the heroes of myth, lull the "
        "giant and remember the dead nearby. By custom no magic is worked "
        "inside, and it is lit only by candles renewed through the day. "
        "The choir, magi and covenfolk together, is a dozen or so strong; "
        "two open cloisters join the chantry to the rest.",
        "The Hermetic cemetery. The covenant tends the dead, burying them "
        "where the aura keeps their spirits from being summoned, and as a "
        "courtesy gives the same rites to the Coill Trí's druids, the elder "
        "races and supernatural creatures. Magi of the Ordo Hiberniae who "
        "feel death coming visit to arrange their burial, so the covenant "
        "is on good terms with nearly every covenant in Hibernia; the "
        "exceptions are mostly newcomers from abroad, who find the custom "
        "unChristian and needless and dislike honouring hedge wizards like "
        "magi. Hibernia's few Tremere keep their own House's burial "
        "customs. Irish burial has long looked odd to foreigners (Saint "
        "Ciarán of Clonmacnoise had his bones laid bare on a hillside like "
        "a stag's, perhaps a custom of the Aran Isles), and for the Ordo "
        "Hiberniae, burial here is a cultural choice: the last rites save "
        "the soul, and the spirit rests while its wisdom stays within "
        "reach.",
        "Neutral ground. Every beast and people of Hibernia's "
        "supernatural realms honours the neutrality of Qui Sonant's lands, "
        "and the Treaty of Cnoc Maol Réidh makes them a haven for all. "
        "Some say that but for this sanctuary every native wizard would "
        "have died in Diedne's hunt, and many a foolish Wizard War has "
        "ended in a treaty agreed here. So Qui Sonant gives an aegis token "
        "to anyone in need. Meadhbh, Praesis's fallen leader, is in "
        "sanctuary here.",
        "Consulting the spirits. Anyone who would speak with the dead "
        "petitions the covenant, which asks the ambassador of the spirit's "
        "power, or the praeco for a magus. If they agree, the tomb is "
        "opened, the body and grave goods brought to a casting space "
        "inside, the body wound in the cathach to shield it from the aura "
        "(and its realm interaction bonuses and penalties), and a ritual "
        "invites the spirit back. Every spell of Qui Sonant is closely "
        "guarded; lab texts and casting tablets for the rites are in the "
        "inner library and are not shown to visitors.",
        "The funerary rites. A magus's body is first fixed as an Arcane "
        "Connection to his spirit, by the ordinary laboratory action. It "
        "is laid in a cairn among whatever grave goods his covenant gives "
        "and sealed with an enchanted capstone that wards it against "
        "weather, man and beast, with a hidden trigger that suspends the "
        "ward when the body is needed; further enchantments keep the body "
        "from rotting. Qui Sonant meets any other wish a magus has.",
        "Covenfolk. No soldiers: the covenfolk are good Irishmen, handy "
        "with an axe. All must sing in the chant, and all know "
        "Organization Lore: Order of Hermes and Latin. For all the hard "
        "weather and grim work they want for little, and on holidays the "
        "magi give feasts and gifts of clothes, shoes, tools and "
        "utensils.",
        "Magi: seven, each owing the covenant one season's work a year. "
        "Cantarus, Master of the Songs, Finn, Lewis and Turlough are "
        "described.",
    )
    hidden = joined_lines(
        "Turlough of Criamon, who keeps the cemetery and the spirits, "
        "wants more from the dead than summoning them, and hides his "
        "growing interest from his sodales; any help he gets must "
        "come from outside, and he would trade his favour with the "
        "Coill Trí for it.",
        "Should a magus appear who would commit himself to the covenant, "
        "Cantarus would happily pass Finn over and make that magus Master of "
        "the Songs.",
    )
    qui_sonant = b.covenant(
        "Qui Sonant Pro Quieto",
        tribunal=tribunal,
        founded=800,
        place=grounds,
        aura=7,
        realm="Magic",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=3,
        detail=FULL,
        season="Summer",
    )
    hibernia.covenants["qui_sonant"] = qui_sonant
    b.book(
        qui_sonant,
        "The library of Qui Sonant",
        "Other",
        language="Latin",
        description=(
            "The book names no books. There are libraries in the manor, and "
            "an inner library of lab texts and casting tablets for the "
            "covenant's funerary rites and summonings, closely guarded and "
            "never shown to visitors. Finn Mac Cantarus writes Vitae "
            "Magorum in Irish, lives of magi much read across Hibernia, and "
            "the covenant researches the magi it has buried."
        ),
    )
    m = hibernia.magi
    m["cantarus"] = b.magus(
        "Cantarus an t-Iarbiteon",
        covenant=qui_sonant,
        house=JERBITON,
        age=130,
        summary=paragraphs(
            "Master of the Songs, the head of Qui Sonant, for fifty years "
            "without a challenger; a magus of Jerbiton who looks eighty-five, "
            "born in the covenant and seldom outside it since. He knows "
            "death or Twilight is not far off, but has found no heir to "
            "trust with the covenant: most of the apprentices he has "
            "trained have walked away from Qui Sonant's burden, and only "
            "Finn remains, who has the wish to lead but not the gift.",
        ),
        traits={"Conservative": 3, "Disciplined": 2, "Reclusive": 1},
    )
    m["finn"] = b.magus(
        "Finn Mac Cantarus an t-Iarbiteon",
        covenant=qui_sonant,
        house=JERBITON,
        age=55,
        summary=paragraphs(
            "Cantarus's filius, of Jerbiton, who looks thirty-five. He has a "
            "gift for Vitae Magorum in Irish, and his histories of the Order "
            "are read all over Hibernia; he cares deeply for his covenant "
            "and the peace and fellowship it stands for.",
            "He takes it for granted that, as Cantarus's only filius at the "
            "covenant, he will be the next Master of the Songs, and has no "
            "idea of his pater's doubts. So he learns nothing from his "
            "mistakes as a leader, talks freely of his coming rank, and buys "
            "friends with long-term promises on the strength of it. He took "
            "Lewis's side when the two Verditius quarrelled.",
        ),
        traits={"Impatient": 3, "Arrogant": 2, "Scheming": 1},
    )
    m["lewis"] = b.magus(
        "Lewis Cultas Bhéardaoiteas",
        covenant=qui_sonant,
        house=VERDITIUS,
        age=70,
        summary=paragraphs(
            "Master Stonemason of Qui Sonant, of Verditius, who looks fifty. "
            "There were two Verditius stonemasons here until they fell out "
            "over whether Ingasia may call itself Verditius's domus magna; "
            "to cool the quarrel Finn sided with Lewis, and Peter chose to "
            "leave. Lewis offers younger Verditius Initiation into the "
            "House Mysteries, but only if they declare for Verdi, and such "
            "Initiates may find themselves caught in the vendetta his exiled "
            "rival is about to widen.",
            "He would pay well for an apprentice with a talent for craft "
            "magic, and within a few years will probably go to the Coill Trí seeking "
            "one of the seven Gifted children they owe "
            "each Tribunal; he will even warn rivals off the child, which "
            "Peter, now wandering, may turn against him.",
        ),
        traits={"Proud": 3, "Abrupt": 2, "Hubris (Proud)": 2, "Disciplined": 1},
    )
    m["turlough"] = b.magus(
        "Turlough Cultas Críothamon",
        covenant=qui_sonant,
        house=CRIAMON,
        age=80,
        summary=paragraphs(
            "Turlough of Criamon, who looks fifty-five, governs the "
            "cemetery, the funeral rites and the protection of the "
            "spirits in the covenant's keeping, and is well thought of "
            "inside the covenant and out. His own magic is the "
            "summoning of spirits. He has trained one apprentice and "
            "won another at the last Tribunal through his warm "
            "relations with the Coill Trí.",
        ),
        secrets="He feels there is more to gain from the spirits than summoning "
        "them, and fears his sodales will learn of this growing "
        "interest, so any help must come from outside; he would gladly "
        "bargain his influence with the Coill Trí for it.",
        traits={"Secretive": 3, "Affable": 2, "Disciplined": 1},
    )


# --------------------------------------------------------------- Vigil


def _vigil(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    inis = hibernia.places["inis_eoghain"]
    head = _add(
        hibernia,
        "cionn_mhalanna",
        "Cionn Mhálanna",
        inside=inis,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Malin Head, Ireland's most northerly promontory, a ragged coast "
            "thrust into the Atlantic, good grazing land often battered by "
            "storms off the sea. Vigil spreads across it as halls and "
            "homesteads in ringforts, one to each magus, each in a moderate "
            "Faerie aura (3 is assumed). Faerie auras are scattered all over "
            "the headland, and there seem to be as many faerie kings along "
            "the coast as mortals; Vigil keeps the peace between them. Its "
            "warriors most often fight a Fachan king and his Fer Caille.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "old_vigil",
        "The Old Fortress of Vigil",
        inside=head,
        summary=paragraphs(
            "The fortress the first Merinita of Vigil built on the rocks "
            "over the sea, long abandoned; little is left, its stone carted "
            "off for newer buildings. Beneath it lie the vaults, flooded and "
            "mostly forgotten.",
            "",
        ),
        secrets="Many magical weapons and devices brought from distant lands "
        "have outlasted centuries of rot in the drowned vaults, with "
        "a library of casting tablets and lab texts against Infernal "
        "sickness and foul weather. The old records are lost and "
        "Vigil's magi have no idea what lies under their feet, but "
        "the Vitae Magorum of Hibernia's magi mention the vaults.",
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "banbhas_crown",
        "Banbha's Crown",
        inside=head,
        realm="Faerie",
        aura=3,
        levels=[
            b.level(
                "The first level",
                4,
                "Faerie",
                see="Mossy stone stairs wind up round a spire some thirty feet high.",
                enter="Only by the stairs round the spire.",
            ),
            b.level(
                "The second level",
                5,
                "Faerie",
                enter="Only by the stairs round the spire.",
            ),
            b.level(
                "The third level",
                6,
                "Faerie",
                see="The ground is lost in mist below and the top hidden in cloud.",
                enter="Only by the stairs round the spire.",
                notes=(
                    "At the top a stone chair: whoever sits in it can watch and "
                    "listen to anywhere in Ireland (Penetration +35)."
                ),
            ),
        ],
        summary=paragraphs(
            "The northernmost point of mainland Ireland, where the spire "
            "the first Merinita of Vigil raised stands in a faerie regio. In "
            "the mundane world it is a fallen stone pillar, and the spire "
            "shows only to those passing through the regiones. On the first "
            "level mossy stairs wind round it, and it climbs through two "
            "more levels until mist hides the ground and cloud the top. "
            "A stone seat crowns it, and whoever sits there can watch and listen to "
            "any spot in Ireland (Penetration +35). The stairs are the "
            "only way through the levels, and climbing them costs two "
            "Long-Term Fatigue levels going up and two more coming down. "
            "The book gives the regio three levels but no auras; 4, 5 and 6 "
            "are assumed.",
            "Some Hibernian elders know of it, but most take it for a "
            "prepared casting space and know nothing of its own power. Its "
            "secret is taught at Vigil from master to pupil.",
        ),
        **HIDDEN,
    )
    _add(
        hibernia,
        "inishtrahull",
        "Inishtrahull",
        inside=inis,
        summary=(
            "An island some six miles north-east of Cionn Mhálanna, home of "
            "the faerie princess who is Maoilfhinnéin mac Lir's wife. The "
            "book gives no aura."
        ),
        **KNOWN_LOCALLY,
    )
    hibernia.cathaigh["vigil"] = {
        "cathach": "the tusks of the great black boar that dug the Black Pig's Dyke"
    }
    summary = paragraphs(
        "The covenant that keeps watch over Hibernia, guarding Ireland "
        "against any who mean her people harm; or so it once did. Those "
        "days are long past, and Vigil has grown fat and idle on old "
        "glory. Its halls and homesteads, each in its own ringfort with a "
        "magus, his household and his sanctum, are spread across Cionn "
        "Mhálanna on Inis Eóghain.",
        "Its device is a pair of huge boar's tusks curving viciously from "
        "root to tip; its cathach is the tusks themselves, those of the "
        "immense magical black pig. Leaning: the Ordo Hiberniae, "
        "traditionalist and decadent; the English are welcome in its halls "
        "so long as they keep the customs and do not try to change them.",
        "A Merinita covenant, though a half-forgotten treaty with House "
        "Verditius lets a magus of that House claim one laboratory here.",
    )
    what_matters = joined_lines(
        "Income: an endless supply of silver; Éinri's herds and bees "
        "(honey among Hibernia's best)",
        "Library: the drowned vaults, with anti-Infernal lab texts and "
        "casting tablets, rotting and forgotten",
        "Treasure: uncatalogued curios, magical weapons and devices from "
        "abroad in the vaults, in Gráinne's keeping",
        "Site: Banbha's Crown, a spire in a three-level Faerie regio that "
        "sees all Ireland",
        "Treaty: the beasts of the northern coast belong to Vigil's Order "
        "alone (Treaty of Cnoc Maol Réidh)",
        "Claim: Aileach, which Vigil will defend with certamen and Wizard War",
        "Boon: Aura (Faerie, at each hall)",
        "Boon: Regio (Banbha's Crown)",
        "Boon: Mystical Allies (the faeries and beasts of the northern sea)",
        "Boon: Veteran Fighters (the Two Dozen Men of Mhálanna)",
        "Boon: Wealth",
        "Hook: Faerie Court (faerie kings all along the coast)",
        "Hook: Monster (a Fachan king and his Fer Caille warriors)",
        "Hook: Rights and Customs (the Verditius right to a laboratory)",
        "Hook: Crumbling (the old fortress abandoned, the vaults drowned)",
        "Tension: Éinri's feud with Dalton Ballaugh of Lámbaird",
        "Tension: Gráinne and Guillaume of Praesis, and Maoilfhinnéin's plan for her",
    )
    notes = paragraphs(
        "History. House Diedne founded the first Vigil in the Sperrin "
        "foothills, winning its standing by hunting down the great black "
        "pig whose ditches later guarded old Ulster from the south and "
        "taking its tusks. Viking rune-smiths from Dublin raided it in "
        "830; it recovered and for a time helped other covenants against "
        "those invaders, until Ireland's Diedne, Vigil among them, "
        "withdrew from the Tribunal's affairs in 851. With the Diedne gone "
        "from Ireland's defence, a band of Merinita sacked Vigil, carried "
        "the tusks to the far north and raised a fortress there, the new "
        "Vigil, with a great unseen tower from whose top all Ireland could "
        "be seen, and used it to find and cut off the rune wizards and "
        "their Vikings. The book gives no year for the refounding.",
        "Fighting the vengeful Diedne and the rune wizards at once, Vigil "
        "made alliances with the faeries and beasts of the northern sea, "
        "which still guard the north coast against magical invasion; the "
        "treaties between the Order and the Coill Trí record them, and no "
        "druid outside the Order may deal with the creatures of the "
        "northern seas. In 980, unwilling to see Teamhrach fall to Olaf "
        "Cuaran, king of Dublin and Northumberland, Vigil used magic to seal a treaty "
        "of Máel Sechnaill mac Domnaill with the Leinster and Ulster kings and fought "
        "beside them to rout the Norse; the "
        "Tribunal let the interference go as vital to its own sanctity.",
        "When the Schism War came Vigil struck fast at its old enemies, "
        "taking Diedne heads as trophies, plundering their laboratories and "
        "libraries and killing their familiars. Afterwards it used the "
        "Diedne threat to prove its worth, and its magi went abroad to learn "
        "new magic for Ireland's defence; few came back, sending instead "
        "accounts of their travels, strange spells and devices won from "
        "foreign magi, while the vaults filled with curios and Vigil dined "
        "on its past. For two hundred years it has sunk into decadence and "
        "sloth, trading on a fame centuries stale, yet sure it is all that "
        "stands between Hibernia and its enemies.",
        "The cathach. The curled tusks, six feet from root to tip, hang "
        "over a great arched gate in the covenant's wall under faerie "
        "guard, and travel to Tribunal in an ornate wooden case. They tint "
        "Faerie auras so that they pass on a Personality Trait of "
        "Protecting Ireland +3, and turn Magic auras toward magic that "
        "guards Ireland from invasion.",
        "Culture. Vigil lives by conspicuous consumption, as its old "
        "Merinita did, who fought hard, traded vis to Verditius for arms "
        "and armour against the Vikings and the Diedne, and won more by "
        "conquest. Its magi love loud pleasures: hunting, certamen, raiding "
        "the country round, and above all baiting young magi in their "
        "macgnímartha. Yet they keep the old treaties, the Treaty of Cnoc "
        "Maol Réidh most of all, and guard every old custom of the "
        "Tribunal fiercely. They are urged to marry for comfort, not "
        "politics, and to share their Parma Magica with their wives "
        "against The Gift; to bind a familiar and make a talisman early; "
        "visitors with neither are teased, kindly. Each spins long tales "
        "of danger, adventure and love with himself as the hero, puffing "
        "up his familiar or his talisman, and there is a purpose to it: "
        "all of Vigil's magi know the Merinita Folk Mysteries, whose magic "
        "feeds on such symbols. Máel-ruanaid is their mystagogue.",
        "Its magi excel at music, etiquette and every pastime of the "
        "privileged. Every apprentice learns Charm Magic, and though none "
        "must stay, a bond of magic ties members together. Fiercely loyal "
        "to Ireland and Hibernia and its traditions.",
        "Covenfolk. Vigil's excess reaches its people too: well dressed, "
        "well fed, rather too familiar at the frequent feasts. Its "
        "warriors, the Two Dozen Men of Mhálanna, are trained in the "
        "clesrada, used to magic, armed and armoured in faerie gear forged "
        "in past wars, deadly and fiercely loyal to Vigil and above all to "
        "Gráinne. They spend most of their time keeping a Fachan king and "
        "his Fer Caille off Mhálanna.",
        "Magi: six, and two apprentices soon to set out on their "
        "macgnímartha. Éinri, Gráinne, Máel-ruanaid and Maoilfhinnéin are "
        "described. The founding year is not given (the Merinita took the "
        "tusks soon after 851).",
    )
    hidden = joined_lines(
        "The drowned vaults hold forgotten magical weapons and "
        "devices from far lands and a library against Infernal "
        "plague and winters; covenants struck by such troubles may "
        "come asking for it.",
        "No one recorded what turned Vigil's Merinita against the "
        "Diedne; those who know how demons work may wonder.",
        "Maoilfhinnéin expects the Ordo Hiberniae to be driven back "
        "as the native wizards once were, and has readied Inishtrahull "
        "to take the cathach and a rebuilt Vigil; he is courting "
        "Lámbaird, feeding Gráinne's overconfidence because a "
        "sacrifice may be needed, and steering the shards of her "
        "first talisman, now an Arcane Connection to her, toward "
        "Guillaume of Praesis.",
    )
    vigil = b.covenant(
        "Vigil",
        tribunal=tribunal,
        founded=852,
        place=head,
        aura=3,
        realm="Faerie",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=2,
        detail=FULL,
        season="Autumn",
    )
    hibernia.covenants["vigil"] = vigil
    b.book(
        vigil,
        "The drowned vaults of Vigil",
        "Other",
        language="Latin",
        description=(
            "The book names no books. Vigil's old library lies dark and "
            "untouched in the waterlogged vaults under the abandoned "
            "fortress: casting tablets and lab texts against Infernal "
            "sickness and harsh weather, with books and records earlier "
            "loremasters left to decay. Máel-ruanaid, its loremaster, takes "
            "the trust more seriously than they did. References to it "
            "survive in Hermetic annals and Vitae Magorum."
        ),
    )
    m = hibernia.magi
    m["einri"] = b.magus(
        "Éinri mac Cillíni mich Dáire Boircech",
        covenant=vigil,
        house=MERINITA,
        age=95,
        summary=paragraphs(
            "Vigil's leader, though not its eldest, a magus of Merinita who "
            "looks sixty: he keeps the bees, rules the herds and holds the black "
            "pig's tusks. Big and bearded, he goes in velvet hung with gold and "
            "silver chains, and eats and drinks more "
            "than his humours can bear and suffers gout; the spell he "
            "invented for it dulls the pain but sours his temper, which he "
            "blames on his wife's nagging. His huge court is the centre of "
            "the covenant, its kitchens full of cooks thanks to endless "
            "silver and its halls full of guests, Hermetic, faerie, magical "
            "and mundane. He loves stories, above all tales from beyond "
            "Ireland, and gives away his bees' honey, among the best in "
            "Hibernia, to friends and allies.",
            "His wife Aoife, kept young by strong longevity rituals, looks "
            "far younger than he. They have lately adopted a small boy into "
            "Vigil's court, whom Éinri means for House Mercere, so he may "
            "need a sponsor at one of the Mercer Houses. His talisman is a "
            "coat of bronze mail enchanted to grow with his girth; his "
            "familiar a big, lazy wolfhound. His parens Cillíni once taught "
            "a Scottish magus, Bróccín, the courtesy owed to Ireland's "
            "otherworld, a tale Éinri likes to tell.",
            "He has a long feud with Dalton Ballaugh of Lámbaird: many "
            "certamen and clashes of their grogs, not yet Wizard War, but "
            "real loathing, odd to onlookers given how alike the two men and "
            "their covenants are, and perhaps that is the trouble.",
        ),
        traits={"Welcoming": 3, "Boasting": 2, "Lordly": 1},
    )
    m["grainne"] = b.magus(
        "Gráinne inghean Uaitéar",
        covenant=vigil,
        house=MERINITA,
        age=60,
        summary=paragraphs(
            "A maga of Merinita, as boisterous as anyone at Vigil, who "
            "looks thirty-eight. She married the handsome Pádraig when both "
            "were young. Her familiar is a red kite named Úna, whose senses "
            "she shares, and her talisman a bow of many materials attuned "
            "to several effects, her second: tired of her first, a sword, "
            "she broke it in a rite and threw the pieces off the cliffs of "
            "Cionn Mhálanna. The same excess runs through her magic, for she "
            "is a Waster of Vis without much knowing it.",
            "As quartermaster, a mostly ceremonial post, she must approve "
            "any large spending of vis, and she has charge of the vaults "
            "and their uncatalogued treasures, though like those before her "
            "she has never grown into it and has little notion what they "
            "are worth. She knows of the Verditius right to work at Vigil, "
            "which may give her the leverage to win one of the Gifted children from "
            "Connacht when the Tribunal next meets. The Two Dozen Men of "
            "Mhálanna are devoted to her. Guillaume of Praesis, whom she has "
            "slighted many times, longs to see her humbled.",
        ),
        traits={"Boisterous": 3, "Flirtatious": 2, "Protective of Ireland": 1},
    )
    m["mael_ruanaid"] = b.magus(
        "Máel-ruanaid an Doire",
        covenant=vigil,
        house=MERINITA,
        age=75,
        summary=paragraphs(
            "Vigil's loremaster, of Merinita, who looks fifty: keeper of the "
            "covenant's magical traditions, a trust he takes more seriously "
            "than those before him, who let many books rot in the vaults, "
            "and the mystagogue of Merinita's Folk Mysteries for his sodales. His "
            "master taught him divination, "
            "the secret of Banbha's Crown, and spells to command the "
            "covenant's bees, guide their flight and use their senses; when "
            "he seems to know the unknowable, that is likely how.",
            "A master of Merinita Story Magic, he understands the power of "
            "symbols and believes Qui Sonant's magic rests not on the songs "
            "but on the symbolic act of singing; if he could learn it, the "
            "symbols of the Folk Mysteries might be freed from needing a "
            "physical form. His fellows find him a little dull, without "
            "their sense of fun. His familiar is an owl of like temper; his "
            "talisman a skull he found in the vaults and plated in silver.",
        ),
        traits={"Aloof": 3, "Languid": 2, "Thoughtful": 1},
    )
    m["maoilfhinnein"] = b.magus(
        "Maoilfhinnéin mac Lir",
        covenant=vigil,
        house=MERINITA,
        age=70,
        summary=paragraphs(
            "The Ambassador to the Sea, a magus of Merinita who looks "
            "fifty and spends much of his time at faerie and magical "
            "courts. His talisman is a staff of sea-unicorn horn, his "
            "familiar a porpoise, and his wife a faerie princess of "
            "Inishtrahull. With his long white hair and beard and his "
            "sturdy frame he looks like some old sea god, a likeness he "
            "plays up to keep eyes off what he is really doing.",
        ),
        secrets="He believes the old stories must repeat, that the Ordo "
        "Hiberniae will be driven back as the native wizards were, and "
        "sees the first signs already. Should Vigil come under threat, all is "
        "ready for the cathach to go to Inishtrahull and the covenant to be "
        "rebuilt on the island. Meanwhile he backs Lámbaird's views at Tribunal "
        "to mend the harm Éinri has done; he feeds Gráinne's "
        "overconfidence, knowing a sacrifice may soon be needed; and his "
        "allies in the sea have brought him the shards of her first "
        "talisman, which he has fixed as an Arcane Connection and is "
        "steering into the hands of Guillaume of Praesis.",
        traits={"Scheming": 3, "Loyal to Hibernia": 2, "Friendly": 1},
    )


def _wanderers(hibernia: Hibernia, b: Builder) -> None:
    """The two living magi the chapter names who have no covenant."""
    m = hibernia.magi
    m["peter"] = b.magus(
        "Peter",
        covenant=None,
        house=VERDITIUS,
        age=None,
        summary=paragraphs(
            "A Verditius stonemason who once worked at Qui Sonant beside "
            "Lewis. They fell out over Ingasia's claim to be Verditius's "
            "domus magna; when Finn took Lewis's side, Peter left, and he "
            "now wanders, nursing a vendetta he is about to escalate. He "
            "may exploit Lewis's warnings to rivals over one of the Coill "
            "Trí's Gifted children. Without a covenant he is a vagrant in "
            "Hibernian law. The book gives no age.",
        ),
    )
    m["bressal"] = b.magus(
        "Bressal Ua Boniségeas",
        covenant=None,
        house=BONISAGUS,
        age=None,
        summary=(
            "Bressal of Bonisagus, who has studied the peat moor of "
            "Beaghmore at length and holds that its warring auras are a "
            "shattered regio, broken by design or by accident. The book "
            "names no covenant for him and gives no age."
        ),
    )


# -------------------------------------------------------------- finish


def finish(hibernia: Hibernia) -> None:
    """Tie the Earl to the Lord of Ireland and the Ulster sees to
    Armagh, once meath.py and church.py have made them, and set the
    Tribunal's two Ulster ruins on their sites (the Widow's Throat over
    Rath Chinneich, the Diedne Vigil in the Sperrin foothills); anything
    still missing is skipped."""
    w = hibernia.world
    top = w.get("henry_iii")
    earl = w.get("hugh_de_lacy")
    if top is not None and earl is not None and earl.answers_to is None:
        earl.answers_to = top.id
    armagh = w.get("armagh")
    ulster = hibernia.places.get("ulster")
    for ruin, site in (
        ("ruin_widows_throat", "rath_chinneich"),
        ("ruin_diedne_vigil", "sperrin"),
    ):
        record, around = hibernia.places.get(ruin), hibernia.places.get(site)
        if record is None or around is None:
            continue
        if record.place_id is None or (ulster and record.place_id == ulster.id):
            record.place_id = around.id
    if armagh is not None:
        for key in (
            "bishop_raphoe",
            "bishop_doire",
            "bishop_clogher",
            "bishop_down",
            "newry_abbey",
        ):
            record = w.get(key)
            if record is not None and record.answers_to is None:
                record.answers_to = armagh.id
        town = w.get("armagh_town")
        if town is not None and town.answers_to is None:
            town.answers_to = armagh.id


# --------------------------------------------------------------- stats

P = Profile
IRISH = "Irish"
HIBERNIA_LORE = "Area Lore: Hibernian Tribunal"
ORDER_LORE = "Organization Lore: Order of Hermes"
LOCAL_ORDER = (1, "the Hibernian Tribunal")


#: Leth Cuinn's Redcaps: un-Gifted, their House's Rhine lore given no
#: weight in favour of Hibernia's.
_REDCAP: dict[str, int | tuple[int, str]] = {
    "Area Lore: Rhine Tribunal": 0,
    HIBERNIA_LORE: (4, "the High Roads"),
    ORDER_LORE: (3, "the Hibernian Tribunal"),
    "Organization Lore: Cult of Heroes": (3, "the clesrada"),
    "Athletics": (5, "running"),
    "Single Weapon": (5, "spear"),
    "Thrown Weapon": (4, "javelin"),
    "Ride": 3,
}

#: Each magus the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "daire_cu": P(
        gifted=False,
        strong="str sta pre qik",
        native=IRISH,
        abilities={
            **_REDCAP,
            "Leadership": (5, "Redcaps"),
            "Faerie Lore": (3, "the Tuatha Dé"),
        },
        virtues=[
            "Redcap",
            "Lúan Láith",
            "Warrior",
            "Heroic Personality",
            "Dutybound",
            "Driven (Minor)",
            "Proud (Minor)",
            "Covenant Upbringing",
        ],
    ),
    "daire_an_chogaidh": P(
        gifted=False,
        strong="str sta qik dex",
        weak="com int",
        native=IRISH,
        abilities={
            **_REDCAP,
            "Single Weapon": (6, "spear"),
            "Leadership": (5, "drilling warriors"),
            "Area Lore: Ulster": (3, "battlefields"),
        },
        virtues=[
            "Redcap",
            "Ríastradh",
            "Warrior",
            "Hatred (Major)",
            "Reckless (Minor)",
            "Wrathful (Minor)",
            "Heroic Personality",
            "Covenant Upbringing",
        ],
    ),
    "elen": P(
        gifted=False,
        strong="dex qik per",
        native=IRISH,
        abilities={
            **_REDCAP,
            "Athletics": (5, "balance"),
            "Awareness": (4, "sight"),
            "Folk Ken": (3, "reading lips"),
        },
        virtues=["Redcap", "Perfect Balance", "Deaf", "Covenant Upbringing"],
    ),
    "cantarus": P(
        strong="int sta com",
        arts={"Me": 7, "Co": 6, "Re": 6, "Im": 5, "Cr": 4, "Vi": 3},
        abilities={
            "Music": (5, "chant"),
            "Leadership": (4, "the covenant"),
            HIBERNIA_LORE: (3, "the dead of the Order"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=["Good Teacher", "Covenant Upbringing", "Dutybound"],
        native=IRISH,
    ),
    "finn": P(
        strong="com int pre",
        arts={"Me": 6, "In": 5, "Im": 5, "Re": 4},
        abilities={
            ORDER_LORE: (5, "Hibernian history"),
            "Living Language: Irish": (6, "writing"),
            "Profession: Scribe": (4, "Vitae Magorum"),
            "Music": (3, "chant"),
            "Charm": 2,
        },
        virtues=[
            "Good Teacher",
            "Overconfident (Minor)",
            "Ambitious (Minor)",
            "Covenant Upbringing",
        ],
        native=IRISH,
    ),
    "lewis": P(
        strong="int dex sta",
        weak="com pre",
        arts={"Te": 8, "Re": 6, "Cr": 5, "Vi": 4, "Mu": 4},
        abilities={
            "Craft: Stonemason": (6, "tombs"),
            "Craft: Goldsmith": 0,
            "Music": (2, "chant"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=[
            "Inventive Genius",
            "Verditius Elder Runes",
            "Proud (Minor)",
            "Hubris",
            "Enemies",
        ],
        native="Welsh",
    ),
    "turlough": P(
        strong="int pre com",
        arts={"Me": 8, "Re": 6, "In": 5, "Vi": 4, "Co": 3},
        abilities={
            "Magic Lore": (4, "spirits"),
            "Faerie Lore": (3, "the Coill Trí"),
            "Teaching": (3, "apprentices"),
            "Music": (2, "chant"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=["Obsessed (Minor)", "Dutybound"],
        native=IRISH,
    ),
    "einri": P(
        strong="pre com sta",
        weak="qik dex",
        arts={"An": 7, "Mu": 6, "Cr": 5, "Me": 4, "Im": 4},
        abilities={
            "Animal Handling": (4, "cattle"),
            "Etiquette": (4, "feasts"),
            "Music": (3, "harp"),
            "Faerie Lore": (4, "the northern coast"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=["Charm Magic", "Overconfident (Minor)", "Proud (Minor)"],
        native=IRISH,
    ),
    "grainne": P(
        strong="pre dex per",
        arts={"An": 6, "Ig": 6, "Re": 5, "Cr": 4, "Te": 3},
        abilities={
            "Bows": (4, "longbow"),
            "Hunt": (3, "deer"),
            "Faerie Lore": (3, "faerie arms"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=[
            "Charm Magic",
            "Waster of Vis",
            "Overconfident (Minor)",
            "Reckless (Minor)",
        ],
        native=IRISH,
    ),
    "mael_ruanaid": P(
        strong="int per com",
        weak="qik str",
        arts={"In": 8, "An": 6, "Im": 5, "Me": 4},
        abilities={
            "Faerie Lore": (5, "stories"),
            "Music": (3, "chant"),
            "Teaching": (3, "Initiation"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=[
            "Story Magic",
            "Charm Magic",
            "Obsessed (Minor)",
            "Higher Purpose (Minor)",
            "Dutybound",
            "Vulnerable to Folk Tradition",
        ],
        native=IRISH,
    ),
    "maoilfhinnein": P(
        strong="pre com int",
        arts={"Aq": 8, "An": 6, "Im": 5, "Re": 4, "Mu": 4},
        abilities={
            "Faerie Lore": (5, "the sea's courts"),
            "Magic Lore": (4, "sea beasts"),
            "Intrigue": (4, "Hermetic politics"),
            "Etiquette": (3, "faerie courts"),
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=[
            "Charm Magic",
            ("Social Contacts", {"group": "the faerie and magical courts of the sea"}),
            "Dark Secret",
        ],
        native=IRISH,
    ),
    "peter": P(
        strong="int dex sta",
        arts={"Te": 8, "Re": 6, "Cr": 5, "Vi": 4},
        abilities={
            "Craft: Stonemason": (6, "tombs"),
            "Craft: Goldsmith": 0,
            ORDER_LORE: LOCAL_ORDER,
        },
        virtues=["Driven (Minor)", "Proud (Minor)"],
        age=70,
        native="English",
    ),
    "bressal": P(
        strong="int per",
        arts={"In": 7, "Vi": 6, "Re": 4, "Te": 3},
        abilities={
            "Magic Lore": (5, "regiones"),
            "Philosophiae": (3, "natural philosophy"),
            ORDER_LORE: LOCAL_ORDER,
        },
        age=60,
        native=IRISH,
    ),
}


def stats(hibernia: Hibernia) -> None:
    """Generated stats for Ulster's magi and Redcaps, none of whom has a
    printed stat block."""
    b = hibernia.b
    for key, profile in PROFILES.items():
        character = hibernia.magi.get(key)
        if character is not None:
            apply(b, character, profile)
