"""Munster, the south of the Hibernian Tribunal, as of 1220: the province
(places["munster"]) with its old kingdoms and new English liberties
(Desmond, Thomond, Tipperary, Waterford, Limerick and Kerry), its peoples
(the Eoghanachta, the Dál gCais, the Déise), its Gaelic kings and English
lords, its towns (Cork, Waterford, Limerick, Killaloe, Tralee), its
churches and holy places (Cashel, Killaloe's cathedral, Singeal, Cloyne,
Skellig Michael) and its faerie and magic places (the Shannon, the
Burren, Lough Gur, Croc Áine, Sídh Femen, Craig Liath, Tech Dairbhre,
Dún Eochair, Scota's Grave); and the province's four Hermetic houses:
Circulus Ruber on Hag's Head, Cliffheart on Cape Clear Island, Elk's Run
in the Slieve Aughty and the Mercer House of Leth Moga at Cloyne, with
their magi and Redcaps, their libraries and the Red Book of Cloyne. In
paraphrase of The Contested Isle chapter eight.

Keys: the province is places["munster"]; its parts are
places["desmond"], ["thomond"], ["tipperary"], ["waterford_liberty"],
["limerick_liberty"] and ["kerry"]; the covenants' sites are
places["hags_head"], ["cape_clear"], ["slieve_aughty"] and ["cloyne"].
The covenants are covenants["circulus_ruber"], ["cliffheart"],
["elks_run"] and ["leth_moga"]. The magi are magi["milvia"],
["visioturpis"], ["conan_derg"] (Circulus Ruber); ["faisgia"],
["ruaidri"], ["aine_dhubh"], ["coscrach"], ["palantus"], ["styrbjorn"]
(Cliffheart); ["oswald"], ["lugardis"], ["igneous_drake"] (Elk's Run);
and the Redcaps ["diarmait"], ["gopstan"], ["ercc"], ["luathan"],
["ronan"], ["aine"] (Leth Moga). The lords, churches and towns are in
hibernia.world under the keys their makers below give them.

The chapter's story seeds are the stories part's; the places they use
are made here (the Yew of Éadaoin, the Coitse Bodhar's road, the Uí
Briain border mounds, Shandon Castle) so it can find them."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from ..builder import Builder
    from . import Hibernia

BONISAGUS = "house_bonisagus"
GUERNICUS = "house_guernicus"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"
FLAMBEAU = "house_flambeau"
MERCERE = "house_mercere"

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
    _region(hibernia)
    _places(hibernia)
    _lords(hibernia, b)
    _towns(hibernia, b)
    _churches(hibernia, b)
    tribunal = _tribunal(hibernia)
    if tribunal is None:
        # The Tribunal part makes the Tribunal first; without it there is
        # nothing for a covenant to belong to.
        return
    _circulus_ruber(hibernia, b, tribunal)
    _cliffheart(hibernia, b, tribunal)
    _elks_run(hibernia, b, tribunal)
    _leth_moga(hibernia, b, tribunal)


# ------------------------------------------------------------- the region


def _region(hibernia: Hibernia) -> None:
    island = hibernia.places.get("ireland")
    munster = _add(
        hibernia,
        "munster",
        "Munster",
        inside=island,
        summary=paragraphs(
            "Mumhan, the southern province of Mythic Ireland, and the first "
            "the Sons of Míl took: it fell to Éibhear Fionn, whose "
            "descendants split into many túatha. It was once three "
            "kingdoms, Desmond in the south, Thomond in the north and "
            "Ormond in the east, but much of it has been renamed and "
            "parcelled out to English lords. Irish kings keep their own "
            "privileges in their ancestral cantreds and keep English "
            "knights at bay to the east; English lords lay English law on "
            "the Irish they have subdued; the Ostmen and foreigners of the "
            "three cities, Cork, Waterford and Limerick, answer to the "
            "English in name and please themselves in fact; and outlaw "
            "bands in the forests rob Irish and English homesteads alike.",
            "The peoples. The Eoghanachta, named for Eoghan Mór, were the "
            "strongest clan of Munster for centuries and have split into "
            "several: the Eoghanachta Caisail round Cashel, the Eoghanachta "
            "Áine round Cnoc Áine and the Eoghanachta Locha Lein round the "
            "Lakes of Killarney. The Dál gCais, the tribe of Cas, came "
            "north from the south-east to the lands by the Shannon and the "
            "Fergus that became Thomond; their chief house is the Uí "
            "Briain. The Déise, a knot of clans west of the Nore and north "
            "of Waterford, were driven out of the lands round Tara by "
            "Cormac mac Airt long ago and were vassals of the Eoghanachta; "
            "they now bow to English lords by day and make what mischief "
            "they can by night.",
            "The English. In 1210 King John granted his favourites the "
            "province, keeping the three cities for himself: Robert le "
            "Poer had the country north of Waterford, Philip de Braose "
            "had Thomond, and Robert FitzStephen and Milo de Cogan shared "
            "Desmond. "
            "None of them made good the grant, and in 1220 their sons hold "
            "little; hostile neighbours and the lack of any great victory "
            "keep them in check. Both Desmond and Thomond have lately "
            "fought wars of succession in which every side hired English "
            "swords, and the English have crept into Desmond in the "
            "confusion, slowly, quarrelling among themselves as readily as "
            "the Irish do. In Cork and Limerick the Ostmen are beyond "
            "their lords' control, and are let raid the countryside, "
            "plundering whoever they find.",
            "Hermetic Munster. Four Hermetic houses stand here: Circulus "
            "Ruber, the first and largest covenant of Hibernia, on Hag's "
            "Head; Cliffheart on Cape Clear Island; Elk's Run, the English "
            "covenant, in the Slieve Aughty on the Connacht border; and "
            "the Mercer House of Leth Moga at Cloyne, which serves every "
            "covenant south of the Eiscir Riada. The Munster Tuatha Dé "
            "sided with House Diedne in the Schism War, and Donn's isle of "
            "Teach Duínn lies off this coast.",
            "Vis (each in its place): Lough Gur (five pawns of Aquam, "
            "faerie lake foam, under a full moon) and the pearls of Lén's "
            "anvil at Sídh Femen (Ignem, one night a year). Elk's Run "
            "holds the vis of the lands Oswald rode round; the book names "
            "no other source in the province.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        hibernia,
        "desmond",
        "The Kingdom of Desmond",
        inside=munster,
        summary=paragraphs(
            "Deas-Mhumhain, south Munster, the kingdom of the mac Cárthaigh "
            "kings, which vies with Thomond as the strongest Irish realm "
            "in the province and is shrinking: royal grants since the "
            "invasion have pushed its border west of the new Liberty of "
            "Cork, past the Bandon estuary and the English town of "
            "Kinsale. Five years ago Cormac Fionn rose against his brother "
            "King Diarmait; he failed, and the two patched up a peace when "
            "they saw the English pressing on the border.",
            "Small castles ring the kingdom, some thrown up in haste by "
            "English knights, others raised by Desmond's own nobles for "
            "defence and for raiding; Donagh Uí Mathghamhna has built "
            "twelve along the south coast to keep enemies from landing. "
            "Every summer Desmond's warriors fall on one of the Ostmen "
            "towns, Youghal or Cork.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "thomond",
        "The Kingdom of Thomond",
        inside=munster,
        summary=paragraphs(
            "Tuadhmhumhain, north Munster, the old lands of the Dál gCais "
            "and the Uí Briain, between the Shannon, the Fergus and the "
            "southern shores of Lough Derg. It is a buffer between "
            "Connacht and the Liberties of Limerick and Tipperary, and the "
            "Uí Briain have lately raided all three. The Shannon stops the "
            "English building castles here as the FitzStephens do in "
            "Desmond.",
            "The Dál gCais credit their rise to two patrons: Saint "
            "Patrick, who met them on their first march north and is "
            "honoured at their stone church of Singeal, and Aoibheall, a "
            "faerie land-goddess whose mound, Craig Liath, stands on Lough "
            "Derg's western shore. Every king of the Dál gCais weds her in "
            "a public rite, and if he rules well she gives him foresight "
            "and prophecy, though she spends little time with him and he "
            "usually keeps a mortal queen besides. Brian Bóramha married "
            "her and some say owed his high-kingship to her sight; she "
            "warned him on the eve of Clontarf that he would die there. "
            "In 1220 others hold both sacred sites.",
            "Some Uí Briain warriors are still buried the old way, upright "
            "and armed and facing Connacht, in nearly a hundred mounds "
            "along the northern border.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "tipperary",
        "The Liberty of Tipperary",
        inside=munster,
        summary=paragraphs(
            "Once the Kingdom of Ormond, a borderland with Ossory on its "
            "eastern side and Desmond and Thomond on its western, thick with "
            "Eoghanachta septs. The clans lost their standing when the Dál "
            "gCais felled their sacred yew, and the English found them "
            "easy prey. King John made Theobald Walter hereditary Chief "
            "Butler of Ireland with lands in the north; William de Burgh "
            "took the middle country between Cashel and the town of "
            "Tipperary, from his castles of Kilfearkle and Athassel; and "
            "Philip de Worcester the south, with Cahir castle, built by "
            "Conchovor Uí Briain in 1142.",
            "English holdings are islands in a rough sea. Life can be "
            "pleasant in the towns the English founded, Nenagh and Clonmel, "
            "and in those they hold, Athassel and Cahir, but the roads are "
            "perilous, and travellers between the towns go rarely or under "
            "guard, for the Déise and Eoghanachta clans gladly ambush them.",
            "The Silvermine Mountains on the Thomond border are a ring of "
            "wooded peaks round valleys of hazel, hawthorn and rowan that "
            "could hide an army; Keeper Hill, Sliabh Coimeálta, the "
            "mountain of fosterage, stands over them all. Legend says "
            "Sadhbh, a Connacht princess spurned by her Munster husband, "
            "hid there and gave their twins to the Tuatha Dé to raise; "
            "what became of them nobody knows. Magic auras are rare in the "
            "range, which may be why no covenant has been founded in such "
            "defensible country; a careful search might still find a site.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "waterford_liberty",
        "The Liberty of Waterford",
        inside=munster,
        summary=paragraphs(
            "South Déisi to the Irish, the first part of Munster the "
            "English took and, lying close to Leinster, the safest of the "
            "liberties. Its bounds run up the Suir to Clonmel, west to the "
            "abbey town of Lismore, then down the Blackwater to Youghal "
            "and the sea.",
            "Pockets of Irish resistance remain: Déisi fighters gather now "
            "and then to strike at English towns and castles, and the "
            "local lords cannot find where their war band shelters.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "limerick_liberty",
        "The Liberty of Limerick",
        inside=munster,
        summary=paragraphs(
            "Western Thomond and eastern Ormond, once the lands of the Uí "
            "Fidgenti, an Eoghanachta clan that kept them through every "
            "raid, since Irish princes take cattle and not land, and both "
            "mac Cárthaigh and Uí Briain called them to their hostings. "
            "The English take land, and have driven the Uí Fidgenti out. "
            "King John named it a liberty, but its English lords barely "
            "hold it, and the Uí Súilleabháin resist them from their "
            "castles in Kerry and west Cork.",
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "kerry",
        "Kerry",
        inside=munster,
        summary=paragraphs(
            "Carruidhe, named for the Ciarraige, the descendants of Ciar, "
            "son of Fergus mac Róich and Queen Medb. Stronger túatha drove "
            "half the clan north to the Thomond–Connacht border; those who "
            "stayed became the Uá Conchobhair, and the land was the "
            "Kingdom of Ceir, vassal to Desmond, until Henry II gave it to "
            "Robert FitzStephen and Milo de Cogan. King John made it a "
            "shire in 1210.",
            "A country of mountains and peninsulas, where Slieve Mish "
            "sweeps down to the shore of the Dingle peninsula; remote and "
            "dangerous. The Uí Súilleabháin are its strongest túath, then "
            "the Uí Cinnéide and the Uí Donnchadha; though the mac "
            "Cárthaigh have lately weakened them, the Uí Súilleabháin still "
            "pen the English lords in their castles, lords in name only.",
        ),
        **KNOWN_REGION,
    )


# ---------------------------------------------------------------- places


def _places(hibernia: Hibernia) -> None:
    p = hibernia.places
    munster, desmond, thomond = p["munster"], p["desmond"], p["thomond"]
    tipperary, kerry = p["tipperary"], p["kerry"]
    limerick_liberty = p["limerick_liberty"]

    # Desmond
    _add(
        hibernia,
        "magh_nala",
        "Magh nAla",
        inside=desmond,
        summary=(
            "The plain of swans: the mac Cárthaigh king's royal ráth, "
            "hidden deep in the Blackwater valley now that Cork is lost to "
            "him, and the gathering place of his hostings. Forest closes "
            "it in and it is hard to find, reached only by a few winding "
            "roads, not all of which lead there. In winter it is an "
            "ordinary ráth of a few hundred people and a thousand cattle; "
            "each spring King Diarmait calls every freeman and fighter of "
            "Desmond to war, and they come out of the woods in their "
            "hundreds."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "coitse_bodhar_road",
        "The Road of the Coitse Bodhar",
        inside=desmond,
        realm="Faerie",
        aura=1,
        levels=[
            hibernia.b.level(
                "The faerie forest",
                3,
                "Faerie",
                enter="Being struck from the road by the Coitse Bodhar",
                notes="A vast wooded regio where those thrown in wander lost.",
            )
        ],
        summary=(
            "One of the woodland roads toward Magh nAla, driven by the "
            "Coitse Bodhar, the Silent Wagon: a two-wheeled chariot whose "
            "driver, a malicious faerie woman, loves to ride travellers "
            "down. Those knocked off the road land in an endless faerie "
            "forest and wander there until magic fetches them out."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        hibernia,
        "tech_dairbhre",
        "Tech Dairbhre",
        inside=desmond,
        realm="Faerie",
        aura=4,
        summary=(
            "An island just off the Desmond coast, joined to the mainland "
            "by a thin neck of land (Dairbhre Isle). Mug Ruith lives here, "
            "the faerie who calls himself the most famous druid in Éire, "
            "court wizard to the king of the Munster Tuatha Dé and their "
            "ambassador to the Sacred Council. He flies the roth rámach, "
            "the oared wheel, in a bull's hide and a bird mask, and keeps "
            "a hoard of enchanted things: a shining chariot, a magic "
            "shield and a stone that can become a venomous eel. He often "
            "visits his daughter Tlachtga on her hill in Meath."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "shandon_castle",
        "Shandon Castle",
        inside=desmond,
        summary=(
            "A squat stone tower on a crag over Cork harbour, the "
            "keystone of the city's defences."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "yew_of_eadaoin",
        "The Yew of Éadaoin",
        inside=desmond,
        realm="Faerie",
        levels=[
            hibernia.b.level(
                "Inside the yew",
                4,
                "Faerie",
                see="The yew's reflection in the stream, so the legend says",
                notes="Where Eoghan Mór is said to live on with Éadaoin.",
            )
        ],
        summary=(
            "A faerie regio by a stream near the battlefield of Magh Léana, "
            "known only from the Red Book of Cloyne: an invisible yew in "
            "which the faerie woman Éadaoin is said to have carried off "
            "the dying Eoghan Mór. Nobody has found it."
        ),
        **RUMOURED,
    )

    # Thomond
    _add(
        hibernia,
        "river_shannon",
        "The River Shannon",
        inside=munster,
        realm="Faerie",
        aura=1,
        summary=paragraphs(
            "Abha na Sionainne, the longest river of Mythic Ireland, almost "
            "250 miles from its spring in the Dartry Mountains to the "
            "Atlantic, and the great barrier between east and west along "
            "Connacht's border. It is named for Sionainn, a mortal woman "
            "who lifted the capstone from a faerie well of knowledge and "
            "was drowned by the flood that became the river; changed by "
            "it, she now rides the water in a little hide boat, watching "
            "all that passes.",
            "The whole river has a Faerie aura of 1, stronger in its "
            "lonely reaches, where some pools and hidden eddies hold "
            "faerie regiones. West of the river faeries grow more "
            "dangerous: cruel solitary faeries are common, and trooping "
            "faeries do much of the harm laid at kings' doors. In one deep "
            "bend lives a bandraoi, a sea-witch who takes the shape of any "
            "fish or of a lovely woman, and drowns the fishermen she "
            "lures.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "craig_liath",
        "Craig Liath",
        inside=thomond,
        realm="Faerie",
        aura=4,
        summary=(
            "The mound of Aoibheall, the Dál gCais's faerie land-goddess "
            "and the bride of their kings, on the western shore of Lough "
            "Derg; men of Connacht raided it lately. Called the prophetess "
            "of the Uí Briain for the truth of her foresight."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "the_burren",
        "The Burren",
        inside=thomond,
        realm="Faerie",
        aura=2,
        summary=(
            "A plateau of limestone some hundred square miles on the coast "
            "of north-west Thomond, split by cracks (grikes) into "
            "thousands of bare pavements. The grikes are full of long "
            "grass and wild flowers, so cattle and sheep graze here, and "
            "raiders come after them, troubling the place and its many "
            "faeries, who live among the hundred or so stone tombs and "
            "cairns. Circulus Ruber's magi moved here after their year at "
            "the Brú na Bóinne."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "hags_head",
        "Hag's Head",
        inside=p["the_burren"],
        realm="Magic",
        aura=4,
        summary=(
            "Ceann na Cailleach, one of the higher Cliffs of Moher at the "
            "Burren's south-western edge, nearly 400 feet above the "
            "Atlantic, looking out to the Aran Islands and Galway Bay. "
            "Circulus Ruber's round tower stands on top. The cliffs are "
            "haunted by a Cailleach, a malicious faerie hag who would "
            "gladly pull the tower down; the Aegis keeps her off, but she "
            "torments travellers on the lonely road to the covenant, and "
            "some folk wrongly think she guards it. Fomóir raiders in the "
            "Schism War left scars on the land here."
        ),
        **KNOWN_ORDER,
    )
    _add(
        hibernia,
        "border_mounds",
        "The Uí Briain Border Mounds",
        inside=thomond,
        summary=(
            "Nearly a hundred burial mounds along Thomond's northern "
            "border, where Uí Briain warriors lie upright, weapons in "
            "hand, facing north toward Connacht in the pagan fashion. The "
            "book gives them no aura."
        ),
        **KNOWN_LOCALLY,
    )

    # Tipperary
    _add(
        hibernia,
        "sidh_femen",
        "Sídh Femen",
        inside=tipperary,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "The Mound of Femen, where Bodh Derg, the Dagda's son, holds "
            "court as king of the Munster Tuatha Dé: a vast hall under the "
            "earth, as full as any Irish king's, of minstrels, courtiers, "
            "herdsmen, warriors and wives. He is renowned as a judge and a "
            "reader of dreams, and other Tuatha Dé visit him often.",
            "His smith, Lén, forges enchanted things for the Munster "
            "Tuatha Dé, and at day's end hurls his anvil onto a nearby "
            "hill, where its sparks turn to pearls. They vanish when he "
            "takes the anvil back, save on one night a year, when they "
            "stay and can be gathered as Ignem vis (claimed by no "
            "covenant).",
        ),
        **KNOWN_TRIBUNAL,
    )
    rock = _add(
        hibernia,
        "rock_of_cashel",
        "The Rock of Cashel",
        inside=tipperary,
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "Caisel, a great outcrop rising sheer from the Golden Vale, "
            "crowned with stone churches, oratories, chapter houses and "
            "cathedrals, the church capital of Munster. Conall Corc "
            "founded it as the seat of the Eoghanachta kings, and Saint "
            "Patrick crowned one of them here and blessed the rock with "
            "miracles. When the Dál gCais drove the Eoghanachta out, the "
            "Rock was given to the Church (to the bishop of Limerick, the "
            "book says), so that no lay hand could hold it and the "
            "Eoghanachta could never win back their old capital. It was "
            "fortified before it was given away; some old buildings are "
            "in ruins, the newer ones are kept in repair. The whole Rock "
            "has a Divine aura of 2.",
            "Before the faith came, the Eoghanachta worshipped the yew, "
            "and a sacred yew stood at the heart of Cashel until Brian's "
            "brother Muircheartach cut it down in the Dál gCais raids; "
            "their hedge wizards say the clan will not rise again until a "
            "new one grows there.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "cormacs_chapel",
        "Cormac's Chapel",
        inside=rock,
        realm="Divine",
        aura=5,
        summary=("The main cathedral on the Rock of Cashel, with a Divine aura of 5."),
        **KNOWN_TRIBUNAL,
    )

    # Limerick
    _add(
        hibernia,
        "croc_aine",
        "Croc Áine",
        inside=limerick_liberty,
        realm="Faerie",
        aura=4,
        summary=paragraphs(
            "Two hills over the Munster plain near Lough Gur, home of the "
            "land-goddess Áine and the place where every royal marriage of "
            "Munster is made. Each midsummer the people light a bonfire on "
            "both summits, then carry blazing clairs, straw bundles bound "
            "to poles, round their fields and herds; those who keep the "
            "rite rightly gain +1 to their Aging Rolls.",
            "The hill is shared in four, one part for the faerie lord of "
            "each province but Meath. Every Tuatha Dé and social faerie "
            "comes to the rite unseen among the crowd and at midnight "
            "goes into Áine's sídh to feast; folk think it ill luck to "
            "witness this and hurry to finish first. A magus who wants a "
            "word with any faerie of Munster will find it here on the "
            "solstice.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "lough_gur",
        "Lough Gur",
        inside=limerick_liberty,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "A lake a few miles north-west of Croc Áine, Faerie 5, with a "
            "bad name. Once in seven years it vanishes for a night, leaving "
            "a wall of fog where the water was. Cairns ring it, and the sí "
            "gaoith, faerie whirlwinds, drag trespassers in to drown. Áine "
            "meets her husband Manannán here at times, but its worst "
            "dweller is a huge faerie eel, a dangerous solitary faerie "
            "that leaps out at night to attack visitors.",
            "Vis: the faerie foam that washes up on the shore; a night's "
            "gathering under a full moon is five pawns of Aquam vis, "
            "tainted by Faerie, so most who walk the shore at night are "
            "magi. Claimed by no covenant.",
            "Among the bigger cairns is one of Ireland's 365 Beds of Dermot "
            "and Grainne, the places where the eloping pair hid from "
            "Fionn mac Cumhaill for a year. The old druids held that a man "
            "who found every bed and slept in each in the proper order, "
            "through a year-long initiation, would gain supernatural "
            "powers.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "dun_eochair",
        "Dún Eochair",
        inside=limerick_liberty,
        realm="Faerie",
        levels=[
            hibernia.b.level(
                "The palace of Cú Roí",
                5,
                "Faerie",
                notes="The faerie-hero's court on the old palace grounds.",
            )
        ],
        summary=(
            "A ruin on the River Maigue, once the Uí Fidgenti's capital "
            "until the mac Cárthaigh drove them out; with English settlers "
            "nearby, both clans have left it. A regio over the old palace "
            "grounds hides the hall of Cú Roí, who in the Ulster tales was "
            "king of Munster, a magician, warrior and shape-changer, now a "
            "faerie-hero who misses the people who once lived here. He is "
            "most often a judge, famous for fair rulings: who is the "
            "better warrior or poet, or which course a man should take."
        ),
        **KNOWN_REGION,
    )

    # Kerry
    _add(
        hibernia,
        "scotas_grave",
        "Scota's Grave",
        inside=kerry,
        realm="Magic",
        aura=5,
        summary=(
            "A ring of tall stones in a small valley grove on Slieve Mish, "
            "beside an old trail into the mountains from Tralee. Scota, an "
            "Egyptian princess and sorceress, wife of Gaedheal Glas and "
            "mother of the Gaels, came to Ireland nearly two thousand "
            "years old to avenge two sons slain in the Milesians' first "
            "war with the Tuatha Dé; she killed their killers, was cut "
            "down by Munster faeries and lies where she fell. Magic 5."
        ),
        **KNOWN_REGION,
    )
    _add(
        hibernia,
        "skellig_michael",
        "Skellig Michael",
        inside=kerry,
        realm="Divine",
        aura=3,
        summary=(
            "Sceilig Mhichíl, Michael's Rock: a steep, barren island nine "
            "miles out, a monastery for six hundred years until Viking "
            "raids drove the monks away in the eleventh century. Their "
            "stone huts still sit on the peak above 750-foot cliffs. The "
            "whole island has a Divine aura of 3."
        ),
        **KNOWN_TRIBUNAL,
    )

    # The covenants' sites
    _add(
        hibernia,
        "cape_clear",
        "Cape Clear Island",
        inside=desmond,
        realm="Magic",
        aura=3,
        summary=paragraphs(
            "An island eight miles off Ireland's southernmost shore, a mile "
            "wide and three long, pinched in two by an isthmus. A small "
            "monastic community lives on the southern half; the somewhat "
            "larger north is empty but for birds and Cliffheart, whose "
            "ráth sits on a steep hill over a little cove, the Cove of the "
            "Black Stream; both hill and cove lie in a Magic aura of 3.",
            "Outside the ráth stand three standing stones the island folk "
            "call the Marriage Stones: they believe a couple who clasp "
            "hands through the hole in one of them will never part, and "
            "the monks try to stop the pagan practice.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "slieve_aughty",
        "The Slieve Aughty",
        inside=munster,
        realm="Magic",
        aura=3,
        summary=(
            "Hills west of Lough Derg on the Munster side of the border "
            "with forbidden Connacht (the book's Slieve Aught). In a large, "
            "remote valley here stands Elk's Run, which claims wide "
            "stretches of mountain, lake and forest round about and all "
            "the vis in them. The Uí Sheachnasaigh and the Ua Cathail of "
            "Cenél Áeda na hEchtge hold the country."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        hibernia,
        "cloyne",
        "Cloyne",
        inside=desmond,
        summary=paragraphs(
            "A village monastery in Desmond: wooden houses round a stone "
            "church and a round tower, with no palisade or wall; when "
            "danger comes, monks and villagers lock themselves in the "
            "tower. On its southern edge stand the Mercer House of Leth "
            "Moga, a large wooden house, and a seldom-used barn on a Magic "
            "aura of 1.",
            "Natural tunnels and caves run under the village, linking "
            "several important caverns and chambers; the abbot knows some "
            "of them.",
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------------------ the world


def _lords(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["desmond_king"] = b.lord(
        "Kingdom of Desmond",
        title="duke",
        wealth="Average",
        seat="Magh nAla",
        ruler="Diarmait mac Cárthaigh",
        place=p["desmond"],
        summary=paragraphs(
            "King Diarmait mac Cárthaigh, of the strongest clan of the "
            "Eoghanachta Caisail. His forebears were kings of Cashel until "
            "the Dál gCais drove them west of the Blackwater, and the "
            "English have pushed them further still. The clan hates the "
            "Uí Briain and the Uí Súilleabháin of Kerry far more than the "
            "English; the Uí Briain are too strong to strike, but in 1214, "
            "at a peace feast in the village of Raheen, the mac Cárthaigh "
            "murdered several Uí Súilleabháin nobles. Within the year "
            "Diarmait and his brother Cormac Fionn were fighting each "
            "other for Desmond.",
            "He rules from the hidden ráth of Magh nAla and summons his "
            "hosting every spring. He has set his hedge wizards, men who "
            "throw lightning, to bring down Shandon Castle, Cork's chief "
            "defence. The book records no tribute owed to the English "
            "crown.",
        ),
    )
    w["cormac_fionn"] = b.lord(
        "Cormac Fionn mac Cárthaigh",
        title="landed",
        place=p["desmond"],
        ruler="Cormac Fionn mac Cárthaigh",
        answers_to=w["desmond_king"],
        summary=(
            "King Diarmait's brother, who rose against him five years ago "
            "and failed; the two made an uneasy peace when the English "
            "crept up to the border."
        ),
    )
    w["ui_mathghamhna"] = b.lord(
        "The Uí Mathghamhna",
        title="landed",
        place=p["desmond"],
        ruler="Donagh Uí Mathghamhna",
        answers_to=w["desmond_king"],
        manors=12,
        summary=(
            "A Desmond túath whose lord, Donagh, has raised a chain of "
            "twelve castles along the kingdom's south coast to stop "
            "enemies landing from the Atlantic. Unlike the hasty English "
            "motte and bailey forts, every one is of fortified stone, and "
            "they went up so quickly that some magi suspect magic. "
            "Cliffheart, known to favour the Irish, is not far away."
        ),
    )
    w["thomond_king"] = b.lord(
        "Kingdom of Thomond",
        title="duke",
        wealth="Average",
        seat="Kincora, at Killaloe",
        ruler="Donnchadh Cairbre Uí Briain",
        place=p["thomond"],
        summary=paragraphs(
            "King Donnchadh Cairbre Uí Briain, of the Uí Briain, the "
            "greatest house of the Dál gCais and one of the five bloods of "
            "Ireland. Their fortunes began with Brian Bóramha's brother "
            "Mathgamain, who took Cashel and Limerick and fell in 975; "
            "Brian, sole provincial king after him, grew so strong that "
            "the Uí Néill high-king gave up the high-kingship to him, and "
            "he held it from 1002 until Clontarf in 1014. Each king of "
            "the Dál gCais weds Aoibheall of Craig Liath.",
            "Donnchadh worries more about Connacht, his old enemy, than "
            "about the English, and freely hires English soldiers from "
            "Tipperary and from the de Burgo family. A Connacht raid of "
            "the Uí Conchobhair lately burned Killaloe without breaking "
            "his power, and he is gathering mercenaries for a blow back "
            "into Connacht. Afraid after the raid, he buried his greatest "
            "treasures somewhere he has since forgotten. The book records "
            "no tribute owed to the English crown.",
        ),
    )
    w["ui_suilleabhain"] = b.lord(
        "The Uí Súilleabháin",
        title="landed",
        seat="Tralee",
        place=p["kerry"],
        summary=(
            "A branch of the Eoghanachta Caisail descended from a seventh-"
            "century king of Munster; their most famous king, Fedelmid mac "
            "Crimthainn, was at once king of Munster and abbot of Cork and "
            "Clonfert. Forever at war with the mac Cárthaigh, they were "
            "badly hurt by the massacre of Raheen in 1214, but they are "
            "still the strongest túath of Kerry, rule Tralee, and keep the "
            "English lords of Kerry and Limerick shut in their castles. "
            "The book names no chief."
        ),
    )
    w["deise"] = b.lord(
        "The Déise",
        title="landed",
        wealth="Poor",
        place=p["waterford_liberty"],
        summary=(
            "Clans west of the Nore and north of Waterford, once vassals "
            "of the Eoghanachta, driven from near Tara long ago when their "
            "founder Aonghus Gaífhuileach, 'bloody spear', fell out with a "
            "son of Cormac mac Airt over a woman. The southern Déise joined "
            "the Ostmen to defend Waterford against the English and lost; "
            "now they serve their English lords politely by day and make "
            "trouble by night. Déisi raiders still muster against English "
            "towns and castles from some hiding place nobody has found."
        ),
    )
    w["ui_sheachnasaigh"] = b.lord(
        "The Uí Sheachnasaigh",
        title="landed",
        place=p["slieve_aughty"],
        summary=(
            "One of the two great families of Cenél Áeda na hEchtge, a "
            "branch of the Uí Fiachrach Aidhne, the ancient royal house of "
            "Connacht. They serve Elk's Run as its covenfolk and enjoy its "
            "help, which their rivals the Ua Cathail resent."
        ),
    )
    w["ua_cathail"] = b.lord(
        "The Ua Cathail",
        title="landed",
        place=p["slieve_aughty"],
        summary=(
            "The other great family of Cenél Áeda na hEchtge, rivals of "
            "the Uí Sheachnasaigh. They resent the English magi of Elk's "
            "Run for helping their rivals, raid the covenant, lose men to "
            "Igneous Drake's fire, and may soon lay a formal complaint "
            "before the Tribunal."
        ),
    )
    # The English lords of Munster (they answer to the Lord of Ireland).
    w["le_poer"] = b.lord(
        "The le Poer Lands",
        title="landed",
        place=p["waterford_liberty"],
        ruler="Robert le Poer's son",
        summary=(
            "The lands north of Waterford, granted by King John in 1210 "
            "to Robert le Poer; neither he nor his son has made the grant "
            "good, and the Déise there obey only by daylight."
        ),
    )
    w["de_braose"] = b.lord(
        "The Lordship of Limerick",
        title="landed",
        seat="King John's Castle, Limerick",
        place=p["limerick_liberty"],
        ruler="Philip de Braose's son",
        summary=(
            "Thomond was granted to Philip de Braose in 1210 and Limerick "
            "given to him after its charter of 1197; his son holds the "
            "city but spends so much effort keeping order inside it that "
            "the countryside slips back into Irish ways."
        ),
    )
    w["fitzstephen"] = b.lord(
        "The FitzStephens",
        title="landed",
        place=p["desmond"],
        ruler="Robert FitzStephen's sons",
        summary=(
            "Robert FitzStephen was granted Desmond, Cork and Kerry with "
            "Milo de Cogan; his sons build castles in Desmond, encroaching "
            "slowly through the kingdom's succession wars, but hold little "
            "of what was granted."
        ),
    )
    w["de_cogan"] = b.lord(
        "The de Cogans",
        title="landed",
        place=p["desmond"],
        ruler="Milo de Cogan's sons",
        summary=(
            "Milo de Cogan shared the grants of Cork, Desmond and Kerry "
            "with Robert FitzStephen and took Cork by force with him; his "
            "sons hold the city with the Ostmen, and little beyond its "
            "walls."
        ),
    )
    w["butler"] = b.lord(
        "The Butler Lands of Tipperary",
        title="baron",
        place=p["tipperary"],
        ruler="the Chief Butler of Ireland, of Theobald Walter's line",
        summary=(
            "King John made Theobald Walter Chief Butler of Ireland, an "
            "office passed from father to son, and gave him lands in the "
            "north of Tipperary, including the town of Nenagh."
        ),
    )
    w["de_burgh"] = b.lord(
        "The de Burgh Lands of Tipperary",
        title="landed",
        seat="Kilfearkle and Athassel",
        place=p["tipperary"],
        ruler="the de Burgh family",
        summary=(
            "William de Burgh's grant of the middle of Tipperary, between "
            "Cashel and the town of Tipperary. The de Burgo family hires "
            "out its soldiers to the King of Thomond."
        ),
    )
    w["de_worcester"] = b.lord(
        "The de Worcester Lands of Tipperary",
        title="landed",
        seat="Cahir castle",
        place=p["tipperary"],
        ruler="Philip de Worcester",
        summary=(
            "The south of Tipperary, granted to Philip de Worcester with "
            "Cahir castle, which Conchovor Uí Briain built in 1142."
        ),
    )


def _towns(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["cork"] = b.town(
        "Cork",
        charter="Noble lord",
        ruler="the FitzStephens and de Cogans",
        answers_to=w["de_cogan"],
        place=p["desmond"],
        summary=paragraphs(
            "A city at the mouth of the Lee, once a little monastic "
            "community, home of Saints Finbarr and Nessan. Ostmen raiders "
            "wintered here in 1020 and, unusually, were thrown out: Uí "
            "Briain and mac Cárthaigh warriors stormed the walls while "
            "their druids broke the earthworks with lightning. Ostmen "
            "from Dublin, Limerick and Waterford took it back, though the "
            "king of Desmond was strong enough that its leaders bowed to "
            "him; meanwhile the Uí Briain carried Saint Finbarr's relics "
            "off to Killaloe.",
            "After the invasion the king of Desmond offered Cork to Henry "
            "II as tribute, and an English governor and garrison came; mac "
            "Cárthaigh took it back two years later, and four years after "
            "that Henry granted it to Robert FitzStephen and Milo de "
            "Cogan, who stormed it. Desmond besieged it again and again "
            "and gave up only in 1199.",
            "Chroniclers call it an evil place. English and Ostmen inside "
            "the walls can scarcely bear each other, and none dares go "
            "outside into country held firmly by Desmond and the Déise; "
            "the harbour is the only way in or out, yet Cork is second "
            "only to Dublin for trade. Shandon Castle guards it.",
        ),
    )
    w["waterford"] = b.town(
        "Waterford",
        charter="Noble lord",
        ruler="Thomas FitzAnthony, Marshal of Waterford",
        place=p["waterford_liberty"],
        summary=paragraphs(
            "A fishing place fortified by Viking raiders early in the "
            "tenth century, full of Ostmen and foreigners. Ostmen and "
            "Déisi, no friends before, joined to defend it against the "
            "English; they held off Strongbow for a day and yielded when "
            "a badly built tower was pulled down. Strongbow spared the "
            "town, killing only its two Ostman leaders, and soon married "
            "Diarmaid Mac Murchadha's daughter Aoife.",
            "The city of wines, with wine from Bordeaux landed every day, "
            "and the usual landing place of the English king, who kept "
            "it for himself. King John spent heavily on new walls three "
            "times as long as the old, now nearly done. The Marshal, "
            "Thomas FitzAnthony, makes his home with his household in "
            "Reginald's Tower, the city's oldest stone tower and once the "
            "Ostman lords' seat; he has little say outside the walls but "
            "is a masterful sheriff within. Most people inside are Ostmen "
            "and English, with a few Déisi, and it is the quietest of the "
            "three cities.",
            "Before the English came, a toad was found swimming in a "
            "puddle on one of its quays, though toads were unknown in "
            "Ireland; seers called it an omen of evil, and the English "
            "landed months later. Toads have grown commoner since, and a "
            "French merchant is said to have brought in a venomous snake.",
        ),
    )
    w["limerick"] = b.town(
        "Limerick",
        charter="Noble lord",
        ruler="Philip de Braose's son",
        answers_to=w["de_braose"],
        place=p["limerick_liberty"],
        summary=paragraphs(
            "Another Ostman wintering place grown into a city. Brian "
            "Bóramha slew its last strong Viking lord and made it "
            "Thomond's capital, and it changed hands often in the Uí "
            "Briain's dynastic wars; Domnall Mór Uí Briain burned it in "
            "1174 rather than let the English have it. The whole district "
            "was fought over until he died in 1194; then the English "
            "seized the city and most of the country round it. It was "
            "chartered in 1197 and given to Philip de Braose, and King "
            "John's Castle, paid for by the king and named for him, went "
            "up in 1200 on King's Island in the Shannon.",
            "The city is split in all but name: English Town is the "
            "castle with its walled precinct on King's Island, and Irish Town "
            "the walled quarter on the riverbank where Ostmen and Irish "
            "live; as an old royal seat of Thomond it is one of the few "
            "cities with Irish townsfolk. Murders by night are common, and "
            "strangers vanish easily into the harbour.",
        ),
    )
    w["killaloe"] = b.town(
        "Killaloe",
        charter="Noble lord",
        ruler="Donnchadh Cairbre Uí Briain",
        answers_to=w["thomond_king"],
        place=p["thomond"],
        summary=(
            "Thomond's capital and the Uí Briain's seat of power, near "
            "where Thomond, Limerick and Tipperary meet, guarding one of "
            "the few bridges over the Shannon. It began as a monastery; "
            "its value in war led an Uí Briain king to build a palace "
            "here, Kincora, where the king still lives. An Uí Conchobhair "
            "raid from Connacht burned much of it lately."
        ),
    )
    w["tralee"] = b.town(
        "Tralee",
        charter="Noble lord",
        ruler="the Uí Súilleabháin",
        answers_to=w["ui_suilleabhain"],
        place=p["kerry"],
        summary=(
            "Trá Lí, the largest town of Kerry, a harbour and market town "
            "under the Uí Súilleabháin on the northern edge of Slieve "
            "Mish. An ancient trail from it climbs into the mountains past "
            "Scota's Grave."
        ),
    )


def _churches(hibernia: Hibernia, b: Builder) -> None:
    w = hibernia.world
    p = hibernia.places
    w["st_flannan"] = b.church(
        "The Cathedral of Saint Flannan, Killaloe",
        church="Bishop's cathedral",
        place=p["thomond"],
        founded=1185,
        summary=paragraphs(
            "An Irish church. Flannan, a seventh-century abbot of Killaloe "
            "and nephew of the Uí Briain king, had a holy gift for seeing "
            "when a man would die, led his house in peace and plenty, and "
            "was soon made a saint; Thomond's people still come to his "
            "grave for guidance. The cathedral raised in his honour was "
            "begun in 1185 and is nearly finished in 1220; its foreman "
            "says the saint comes to him at night with advice. Saint "
            "Finbarr's relics, brought from Cork, lie beside Flannan's.",
            "A few yards from its foundations stands the Ogham Stone, "
            "waist-high, carved in ogham with a blessing on Thorgrimr and "
            "signed on the back in Norse runes by Thorgrimr as the "
            "carver. It is at least two hundred years old and magical, a "
            "strange bond between the old druids, Norse wizards and the "
            "faith; being so near the cathedral, nobody has carried it "
            "off to study.",
        ),
    )
    w["singeal"] = b.church(
        "Singeal",
        church="Parish church",
        place=p["thomond"],
        summary=(
            "The stone church (its name means chancel) the Dál gCais built "
            "where Saint Patrick met them on his mission through Munster; "
            "the saint, their favourite, often visits them now. One of the "
            "Dál gCais's two sacred sites, it has fallen to the English "
            "and Ostmen of Limerick, so it is in Anglo-Irish hands in 1220."
        ),
    )
    w["cloyne_monastery"] = b.church(
        "The Monastery of Cloyne",
        church="Monastery or nunnery",
        place=p["cloyne"],
        summary=(
            "An Irish house. Its abbot Cian Ua Cathain led a dozen monks "
            "when the Mercer House of Leth Moga was founded beside it in "
            "898; his wife was Imag, the House's founder. Monks and "
            "Redcaps still get on well, despite the reforms lately "
            "imposed on the Church, and the abbot and his staff know the "
            "Redcaps well. The present abbot knows some of the tunnels "
            "under the village."
        ),
    )
    w["cape_clear_monks"] = b.church(
        "The Monks of Cape Clear",
        church="Monastery or nunnery",
        place=p["cape_clear"],
        summary=(
            "An Irish monastic community on the southern half of Cape "
            "Clear Island. Its monks stop lovers clasping hands through "
            "the Marriage Stones outside Cliffheart, calling it pagan and "
            "wicked, which causes the covenant small troubles."
        ),
    )
    w["cashel_school"] = b.university(
        "The Schools of Cashel",
        school="Cathedral school",
        place=p["rock_of_cashel"],
        summary=(
            "A renowned seat of learning on the Rock of Cashel, which "
            "teaches anyone who can pay. It makes no books but owns a good "
            "many. The Redcap Gopstan once lived a year among its monks "
            "posing as an unlettered prince's son to get at the library; "
            "at the end of it the headmaster sent his greetings to "
            "Gopstan's parens, the first hint that he had seen through "
            "the ruse. An Irish school."
        ),
    )


# -------------------------------------------------------- Circulus Ruber


def _circulus_ruber(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The first covenant of Ireland, founded in 780, and still the "
        "largest and the loudest in its own praise: a round tower on Hag's "
        "Head, on the Cliffs of Moher, that is home to the Praeco and the "
        "senior Quaesitor. Its device is a hastily drawn red circle. Its "
        "cathach is a magic cauldron its founders found, long believed to "
        "be the Dagda's.",
        "It leads the traditionalists of the Ordo Hiberniae: it admires "
        "Hermetic scholarship and invention but will not hear of changing "
        "the Tribunal's ways, and foreign magi who visit often feel they "
        "have gone back in time, which is just what Circulus Ruber "
        "wants. It sees itself as the Tribunal's leader and model.",
    )
    what_matters = _lines(
        "Vis: the book names none",
        "Wealth: cattle, as tradition demands; the covenant never meets its wealth needs any other way",
        "Library: unnamed (see its library record)",
        "Duty: it makes all the arrangements for each Tribunal at Tara, raising the temporary camp by magic",
        "Boon: Magical Fortress (a great tower raised with an enlarged Conjuring the Mystic Tower)",
        "Boon: Prestige (the Tribunal's first and leading covenant)",
        "Boon: Famous Resident (the Praeco, Milvia)",
        "Hook: Monster (the Cailleach of Hag's Head, kept out only by the Aegis)",
        "Hook: Hermetic Politics (leader of the Ordo Hiberniae against the English reformers)",
        "Hook: Dark Secret (the cauldron's true nature and power)",
        "Tension: its love of feud and Wizard War against its duty to protect Hibernia",
    )
    notes = paragraphs(
        "History. Two Tytalus and two Merinita magae came to Ireland in "
        "778 to look for the four treasures of the Tuatha Dé. They found "
        "an island at war with itself and crowded with faeries, which "
        "pleased the Tytalus and the Merinita respectively, and the "
        "customs they set became the Peripheral Code: the Tytalus "
        "nurtured strife and self-reliance, the Merinita the island's "
        "faeries and its mythic past. After a year in the Brú na Bóinne "
        "they moved to the quiet Burren, raised a tower by magic on the "
        "cliffs and declared they would hold it for a year. Local "
        "wizards and their mundane kin fought hard to drive them out; "
        "allies from the Rhine and Iberia joined them, and by the end of "
        "the decade eight magi lived here. The covenant is named for the "
        "red wards a local ward-maker drew round them.",
        "Over the centuries it stood aside from what quarrels it could "
        "and joined those it had to: mundane wars it avoided where it "
        "might; faeries, druids and hedge wizards troubled it often; the "
        "Ostmen's rune wizards fought it to several draws; and in the "
        "Schism War a Fomóir fleet attacked, leaving scars on the tower "
        "and the land. It has ignored the English invaders as of no "
        "lasting account, though the magi who came in their wake may "
        "prove otherwise.",
        "The tower. A round tower 120 feet high and 60 across, made with "
        "an augmented Conjuring the Mystic Tower, with room for twelve "
        "magi and their staff; the magi live above, the servants on the "
        "lower floors. Each year the newest member paints a red ring "
        "round the tower's middle, halfway up.",
        "Culture. Clinging to a romantic idea of the past, its magi "
        "refuse to touch the Peripheral Code and stress the Tribunal's "
        "warlike, individual spirit. They urge magi to found covenants "
        "and have helped some; they champion the macgnímartha and their "
        "raids on other covenants' cathaigh; and they push quarrelling "
        "magi into Wizard War, even lending enchanted items and magic "
        "weapons to the fighters. Yet they are also Hibernia's guardians, "
        "protecting sacred mounds and other places the Tribunal values, "
        "supporting both Mercer Houses with hospitality, and giving up "
        "their own time readily to the Tribunal's business. It once "
        "lodged a travelling provincial king and two hundred followers "
        "on magically made food that did not nourish them.",
        "Magi: eight, including the Praeco Milvia and the senior "
        "Quaesitor Visioturpis, and Conán Derg, the eldest magus of "
        "Hibernia; the book names no others.",
        "The cathach.",
    )
    hidden = _lines(
        "The cauldron is not the Dagda's, which gives food and drink without end, but the Cauldron of Llasar Llaes Gyfnewid, a notorious giant who lived beneath a lake. Legend says that cauldron passed between Irish and Welsh kings and was broken in a war between them; either the tale is wrong, or this is another vessel with the same powers.",
        "It brings a dead warrior back to fight for one more day, if his head and spine are whole: he cannot speak, and for the next 24 hours he fights for whoever put him in. It will not raise the same corpse twice. The magi keep this from the Tribunal.",
    )
    covenant = b.covenant(
        "Circulus Ruber",
        tribunal=tribunal,
        founded=780,
        place=hibernia.places["hags_head"],
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=5,
        detail=FULL,
        season="Autumn",
    )
    hibernia.covenants["circulus_ruber"] = covenant
    hibernia.cathaigh["circulus_ruber"] = {
        "cathach": "a magic cauldron, thought to be the Dagda's"
    }
    b.book(
        covenant,
        "The library of Circulus Ruber",
        "Other",
        description=(
            "No books are named. The covenant honours Hermetic scholarship "
            "and invention; what it holds is not described."
        ),
    )
    m = hibernia.magi
    m["milvia"] = b.magus(
        "Milvia",
        covenant=covenant,
        house=BONISAGUS,
        age=164,
        summary=paragraphs(
            "Praeco of Hibernia, looking sixty-eight. She is not the "
            "eldest magus of the Tribunal, but Conán Derg gave up the "
            "office. Her passion is political unity, and she has steered "
            "a turbulent Tribunal skilfully through most of its storms; "
            "she has been Praeco at the last four meetings and led "
            "Hibernia's delegation to the Grand Tribunal of 1195.",
            "As a Bonisagus she respects Cliffheart's original research, "
            "though she fears its success would harm Hibernia's unity. "
            "She takes no side between the Irish and English magi.",
        ),
        traits={"Obsessed with details": 3, "Overly focused": 2},
    )
    m["visioturpis"] = b.magus(
        "Visioturpis",
        covenant=covenant,
        house=GUERNICUS,
        age=145,
        summary=paragraphs(
            "Hibernia's oldest Quaesitor and its presiding Quaesitor, "
            "looking fifty-six: ugly, bent and irritable, his long face "
            "scarred down both sides and his greasy hair hanging in "
            "strands. His name joins the Latin for face and ugly.",
            "Painful Magic makes him slow to cast, so he prefers one "
            "mighty spell to several small ones, though such spells flood "
            "him with more than he can sort and details get lost. He has "
            "reversed his rulings when what he first learned proved "
            "false; he is no fool to cling to a bad judgement, but he "
            "remembers long and hates to be shown wrong.",
        ),
        traits={"Dour": 2, "Irritable": 2},
    )
    m["conan_derg"] = b.magus(
        "Conán Derg",
        covenant=covenant,
        house=MERINITA,
        age=172,
        summary=paragraphs(
            "The oldest magus in Hibernia, who looks a hale twenty-nine "
            "and says his strong faerie blood keeps him young. He was "
            "Praeco when the trouble between Irish and English magi began "
            "and stood by the Peripheral Code, insisting that all the "
            "newcomers wanted could be had under it; in 1186 he accepted "
            "Ashenrise's cathach.",
            "Two months after the meeting of 1186, wandering alone on the "
            "Connacht border, he was ambushed and his right arm was taken "
            "off at the shoulder. He would not let magic regrow it: by the old "
            "Irish belief that a leader must be whole, he gave up the "
            "office of Praeco and withdrew from Hermetic politics, and he "
            "has seemed happier ever since. Some suspect Faisgia of "
            "Cliffheart; Conán Derg neither denies nor confirms it.",
        ),
        traits={"Mysterious": 3, "Close-mouthed": 2},
    )


# ------------------------------------------------------------- Cliffheart


def _cliffheart(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A ráth of a dozen huts on Cape Clear Island, off Ireland's "
        "southern tip, whose magi study faeries and have grown fearful "
        "of them; its device is three doves flying in a ring, and its "
        "cathach a Diedne magus turned into a standing stone. Founded "
        "after Clontarf by Merinita survivors of Warbler's Way.",
        "Staunchly of the Ordo Hiberniae: it will not accept English "
        "magi, uses every lawful means to stop them founding covenants, "
        "and is working out how to cast spells in Irish instead of "
        "Latin. Its magi keep their Oath and the Peripheral Code; they "
        "are anxious recluses, not criminals or troublemakers.",
    )
    what_matters = _lines(
        "Vis: the book names none",
        "Library: untidy on purpose (see its library record)",
        "Research: Palantus's spells in Irish, built from faeries' true speech",
        "Boon: Island (Cape Clear Island)",
        "Boon: Seclusion (few visitors, hidden by The Shrouded Glen: Perception against 9 to find)",
        "Boon: Ringwork (a simple ráth and palisade)",
        "Hook: Monastery (the monks on the southern half of the island)",
        "Hook: Hermetic Politics (against the English magi; Ashenrise especially)",
        "Hook: Rival (the faeries it fears, with Teach Duínn and Donn not far off)",
        "Tension: the Marriage Stones, lovers who seek them out and monks who forbid them",
    )
    notes = paragraphs(
        "History. Three Merinita magi founded it once their covenant, "
        "Warbler's Way (Cosán Ceolaire), fell in the Schism War. Most of "
        "House Merinita stayed out of that war, but these three fought, "
        "because House Diedne had allied with the Munster Tuatha Dé; "
        "after the last battle at Clontarf they moved to Cape Clear. Two "
        "centuries of questioning have never shown why the Tuatha Dé "
        "took Diedne's side, and since it could happen again, with Teach "
        "Duínn so close and Donn's past what it is, the magi keep "
        "dealing with them. The founders have gone to death or Final "
        "Twilight, and their filii carry on.",
        "The ráth. A simple ráth round a dozen huts on a steep hill over "
        "the Cove of the Black Stream on the island's north shore, where "
        "supplies are landed in secret. The Shrouded Glen hides it, less "
        "well than in a forest but well enough. Inside the palisade are "
        "the magi's huts and laboratories, the servants' huts, a meeting "
        "hall and the sheepfold. The steward Maynard handles every "
        "mundane matter, playing a madman who lives among the birds, and "
        "warns people that the standing stones are haunted; visiting "
        "magi look for the dirt track to the stones or for the hermit "
        "among the gulls and barnacle geese.",
        "The cathach. One of three standing stones outside the ráth is a "
        "Diedne magus turned into an obelisk. A hand-wide hole runs "
        "through it, which the magi say is a mortal wound: they renew "
        "the spell every year, since if it lapsed he would die at once. "
        "Faisgia keeps the spell up and moves the stone to each Tribunal "
        "with Rego Terram magic. Some say the three Diedne who fell at "
        "Clontarf were never found, and Cliffheart claims one though it "
        "did not fight there.",
        "Culture. Four of the six magi study faeries, collecting, "
        "fighting, questioning and entertaining them; the other two "
        "seldom leave their sancta. Faeries hate disorder, so the "
        "grounds, the library included, are kept a deliberate mess, and "
        "though the Aegis would stop nearly any faerie, the magi take "
        "many precautions besides: they never cut hair or beard; wear "
        "iron rings on both little fingers and necklaces of horses' back "
        "teeth; smash eggshells so small faeries cannot live in them; "
        "keep cats and dogs out; set each hut's front and back doors in "
        "line so a faerie walks straight through; never dig inside the "
        "ráth or trim its bushes and trees; sprinkle stale urine on "
        "every threshold; and never begin lab work or a journey on a "
        "Friday.",
        "The magi: Faisgia, the leader; the Merinita Ruaidrí Mór (Rego), "
        "Áine Dhubh, Black Ann (Herbam), and the warlike Coscrach Cam; "
        "and the Bonisagus Palantus and the Verditius Styrbjórn, who "
        "rarely leave their laboratories.",
    )
    covenant = b.covenant(
        "Cliffheart",
        tribunal=tribunal,
        founded=1015,
        place=hibernia.places["cape_clear"],
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        detail=FULL,
        season="Winter",
    )
    hibernia.covenants["cliffheart"] = covenant
    hibernia.cathaigh["cliffheart"] = {
        "cathach": "a Diedne magus turned into a standing stone"
    }
    b.book(
        covenant,
        "The library of Cliffheart",
        "Other",
        description=(
            "No books are named. Kept disorderly on purpose, like the "
            "rest of the ráth, to keep faeries away. Palantus's records of "
            "faeries made to speak their true tongue are his research "
            "material, each usable once."
        ),
    )
    m = hibernia.magi
    m["faisgia"] = b.magus(
        "Faisgia",
        covenant=covenant,
        house=MERINITA,
        age=157,
        summary=paragraphs(
            "Cliffheart's leader, filius of one of its founders, looking "
            "ninety-eight. He spends most of his time roaming Munster for "
            "faeries who fought in the Schism War. He keeps the cathach: "
            "each year he casts the spell that holds the Diedne magus in "
            "stone, and he works the Rego Terram magic that carries it to "
            "every Tribunal.",
            "Since Conán Derg was maimed on ground Faisgia often travels, "
            "some magi suspect him of the ambush; he scoffs at the idea.",
        ),
        traits={"Cranky": 3},
    )
    m["ruaidri"] = b.magus(
        "Ruaidrí Mór",
        covenant=covenant,
        house=MERINITA,
        age=None,
        summary=(
            "A Merinita of Cliffheart who specialises in Rego and travels "
            "the Tribunal studying faeries. The book gives no more of him."
        ),
    )
    m["aine_dhubh"] = b.magus(
        "Áine Dhubh",
        covenant=covenant,
        house=MERINITA,
        age=None,
        summary=(
            "Black Ann, a Merinita of Cliffheart who specialises in "
            "Herbam and travels the Tribunal studying faeries. The book "
            "gives no more of her."
        ),
    )
    m["coscrach"] = b.magus(
        "Coscrach Cam",
        covenant=covenant,
        house=MERINITA,
        age=None,
        summary=(
            "A combative Merinita of Cliffheart who travels the Tribunal "
            "among the faeries. The book gives no more of him."
        ),
    )
    m["palantus"] = b.magus(
        "Palantus",
        covenant=covenant,
        house=BONISAGUS,
        age=63,
        summary=paragraphs(
            "A German magus trained in the Rhine, looking forty-three, and "
            "a born linguist, researching how to cast spells in Irish. He "
            "has made a spell that compels a faerie to talk in its old, "
            "truer tongue instead of its Faerie Speech Pretense, records "
            "what it says and builds his research on it; each interview "
            "serves only once.",
            "He longs to meet and talk with every new faerie, but is ill "
            "at ease away from a laboratory and his sodales want no "
            "faerie visitors, so he often asks other Hibernian magi to "
            "lend him their laboratories for his interviews.",
        ),
        traits={"Scholarly": 3, "Absent-minded": 2},
    )
    m["styrbjorn"] = b.magus(
        "Styrbjórn",
        covenant=covenant,
        house=VERDITIUS,
        age=109,
        summary=(
            "A Scandinavian born in Dublin and trained at Verdi, looking "
            "fifty-five. He came home to guard his family when he heard of "
            "the English invasion, found they were in no real danger, and "
            "discovered he loved his homeland; Cliffheart took him in. He "
            "lives at the back of the ráth making magic items for his "
            "sodales, and gladly takes commissions from other Irish magi."
        ),
        traits={"Content when left alone": 3, "Suspicious of others": 2},
    )


# --------------------------------------------------------------- Elk's Run


def _elks_run(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A young covenant of three towers in a remote valley of the "
        "Slieve Aughty, west of Lough Derg, close to the border of "
        "forbidden Connacht, founded in 1159 by Oswald of Bonisagus and "
        "Lugardis of Guernicus. Its device, and its cathach, is a "
        "magnificent pair of giant elk antlers.",
        "It means to revive the learning, hospitality and scholarship of "
        "Ireland's golden age of covenants, and keeps a great library, "
        "but it is the English covenant, of the English Council's "
        "party: raided by Irish clansmen and by Irish magi after its "
        "cathach, it has turned more and more to English nobles for help.",
    )
    what_matters = _lines(
        "Vis: the sources across the mountains, loughs and forests Oswald rode round before sunset; the book does not list them",
        "Library: very large; mundane books, laboratory texts and rare magical volumes, among them the Ars Notoria (see its library record)",
        "Boon: Prestige (Oswald's name for generosity and scholarship across Mythic Europe)",
        "Boon: Local Ally (the Uí Sheachnasaigh, its covenfolk, and English nobles)",
        "Hook: Tribunal Border (on the edge of Connacht, closed to magi by the Treaty)",
        "Hook: Rival (the Ua Cathail, and Irish magi on their macgnímartha after the cathach)",
        "Hook: Mundane Politics (its ties to English nobles; the Ua Cathail's coming complaint)",
        "Tension: Igneous Drake's killings and Wizard Wars against Lugardis's diplomacy",
        "Tension: Oswald may leave Ireland with the library if politics turn against him",
    )
    notes = paragraphs(
        "History. Oswald of Bonisagus and Lugardis of Guernicus came in "
        "1159 with cattle, silver, vis sources the Tribunal did not know "
        "of and the giant antlers for a cathach, claimed a remote valley "
        "and began building a round tower in the old style. Native magi "
        "of several covenants soon came demanding to see the cathach. "
        "Oswald said the antlers came from a true Irish elk, seven feet "
        "tall, which he had hunted and killed in the Faerie realm by "
        "acting out an ancient story, a deed done before only by the Fir "
        "Bolg heroes who hunted the beasts out of Ireland. Since such "
        "antlers turn up in bogs, few believed him. The Irish saw a "
        "Stonehenge magus and a Quaesitor come to impose English rule on "
        "the Order as the English were doing on the kings, too near "
        "Connacht to be trusted with the Treaty.",
        "So they disputed the newcomers' right to the vis of the region, "
        "claiming it for other covenants by ancient custom (though "
        "Hibernian tradition gives such a claim no footing), reciting "
        "their lineages, old pacts and treaties with supernatural beings "
        "and local wizards. Without vis there could be no covenant. "
        "Oswald, a tiny man with a mop of white hair, offered a wager: "
        "all the land and vis he could ride round before sunset would be "
        "his. The Irish, taking it for a joke, agreed, and a wise maga "
        "added that he must cast no spell. He threw down the antlers, "
        "which rose as a giant elk; he rode it into the mountains over "
        "fallen trees, crumbling scree and flooding rivers, and came back "
        "with the last light as the beast turned back to antlers. Many of "
        "the Irish laughed and allowed his right; some were furious at "
        "the trick. Since then many young magi on their macgnímartha, and "
        "some older ones, have raided for the cathach, but none has held "
        "it long enough to end the covenant.",
        "The cathach. The antlers of an Irish elk, an extinct beast "
        "bigger than any living. Nobody knows what else they can do; "
        "Oswald has brought the elk to life and ridden it three times, "
        "each time to defend the covenant.",
        "The covenant. Three towers in the old style, a small feast "
        "hall, a good stone scriptorium that holds the library, a "
        "hamlet, pasture and fields, all within the Aegis; it claims "
        "great tracts of mountain, lake and forest beyond, and all the "
        "vis in them.",
        "The library and the Cow and Calf rule. Elk's Run lives for "
        "research and above all for collecting books. Oswald spent long "
        "years copying in the Archbishop of Armagh's fine library, where "
        "he learnt the Ars Notoria, and swaps texts with religious "
        "houses throughout Hibernia. The Cow and Calf rule is strictly kept here: "
        "anyone may make a copy of a book, but the copy may leave only in "
        "exchange for a text of like worth. Many books are copied here "
        "and sent to covenants across Mythic Europe as gifts or trades.",
        "Lately the other magi have grown warlike under constant raiding "
        "and have bound themselves to English nobles; Lugardis has warned "
        "them more than once that this may count as interfering with "
        "mundanes, but the feeling is that the covenant must lean on the "
        "English to survive.",
        "Covenfolk. The locals are Cenél Áeda na hEchtge, a branch of the "
        "Uí Fiachrach Aidhne, the ancient royal house of Connacht, in two "
        "great families: the Uí Sheachnasaigh, who serve the covenant, "
        "and the Ua Cathail, who resent the English magi's help to their "
        "rivals and may soon complain to the Tribunal. Other covenants "
        "might back them, though Lugardis works against it and it seems "
        "unlikely, since meddling with mundanes that brings ruin on "
        "sodales is itself a crime under the Code.",
        "Magi: three, with two apprentices, both Oswald's; the second, "
        "native born, was given him at the last Tribunal at Lugardis's "
        "urging. The magi agree less and less on what to do.",
        "The book puts the founding in 1159 in this chapter and just "
        "after the Grand Tribunal of 1195 in its history; the pack "
        "follows 1159.",
        "What the magi do not admit.",
    )
    hidden = _lines(
        "Oswald has used acts and gifts of magic to help Irish and English nobles and clerics in return for books, which could plainly be judged interfering with mundanes; he does not see how far he has compromised himself.",
        "Igneous Drake kills raiders, Ua Cathail bandits and hedge wizards who stray out of Connacht, and wages Wizard War on Irish magi he thinks have slighted the covenant, believing Hibernia enforces no law among magi.",
    )
    covenant = b.covenant(
        "Elk's Run",
        tribunal=tribunal,
        founded=1159,
        place=hibernia.places["slieve_aughty"],
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Autumn",
    )
    hibernia.covenants["elks_run"] = covenant
    hibernia.cathaigh["elks_run"] = {
        "cathach": "the antlers of a giant Irish elk, which Oswald can bring to life"
    }
    b.book(
        covenant,
        "The library of Elk's Run",
        "Other",
        description=paragraphs(
            "No single book is named but the Ars Notoria, which Oswald "
            "learnt at Armagh. A very large collection in a stone "
            "scriptorium, with every room of Oswald's tower full of books "
            "besides: a superb library of mundane works, a fine set of "
            "Laboratory Texts and some rare magical volumes, gathered by "
            "copying at Armagh and trading with monasteries across "
            "Hibernia.",
            "The Cow and Calf rule holds: a copy may be made, but leaves "
            "only in exchange for a text of equal value. Oswald hopes one "
            "day to give the rarest to Durenmar.",
        ),
    )
    m = hibernia.magi
    m["oswald"] = b.magus(
        "Oswald",
        covenant=covenant,
        house=BONISAGUS,
        age=97,
        summary=paragraphs(
            "Founder and leader of Elk's Run, looking seventy: a tiny man, "
            "scarcely a boy's size, under a shock of untidy white hair. "
            "Born in Leinster to an Irish mother, he was carried off to "
            "Stonehenge in childhood and brought up there, and after his "
            "Gauntlet planned his return, befriending Lugardis.",
            "His adventures are long behind him. He is wholly given to a "
            "rebirth of learning in Hibernia and to saving the island's "
            "texts for posterity: collecting, copying and trading books. "
            "Gentle Gifted, he has many friends among Irish and English "
            "nobles and clerics. He trusts to cunning and trickery against "
            "his enemies, whom he takes to be jealous of his standing in "
            "House Bonisagus and the Order abroad, and means one day to "
            "give his rarest texts to Durenmar.",
            "He is teaching two apprentices at once, which takes half his "
            "time; once they pass their Gauntlets he may leave Ireland "
            "with the library if the politics turn bad.",
        ),
        traits={"Studious": 3, "Cunning": 2, "Adventurous": 1},
    )
    m["lugardis"] = b.magus(
        "Lugardis",
        covenant=covenant,
        house=GUERNICUS,
        age=92,
        summary=paragraphs(
            "An Italian Quaesitor with raven hair, sharp features and a "
            "piercing stare, looking sixty-four, who has served in four "
            "Tribunals; she came from the Rhine, sent by Durenmar to look "
            "into the state of the Order in Hibernia after English magi "
            "wrote to Magvillus and Durenmar of hostility and barbarous "
            "customs and demanded reform. Her Blatant Gift frightens "
            "covenfolk and Irish folk, who cross themselves as she goes "
            "by, and sours milk almost at once, so she keeps away from "
            "the cattle and the dairy.",
            "She has come to see that Hibernia keeps the Code, if with an "
            "odd Peripheral Code, and having read Oswald's books she is "
            "amused by the Stonehenge magi's fear that Connacht shelters "
            "the last of the Diedne. Her letters home and to Durenmar "
            "explain the local customs and praise the Irish Order, who "
            "still suspect her deeply. She wants a diplomatic answer to "
            "the covenant's troubles, is appalled by Igneous and worried "
            "by Oswald.",
        ),
        traits={"Intimidating": 3, "Gentle": 2, "Just": 1},
    )
    m["igneous_drake"] = b.magus(
        "Igneous Drake",
        covenant=covenant,
        house=FLAMBEAU,
        age=87,
        summary=paragraphs(
            "A Stonehenge magus, looking seventy-two, in Hibernia only ten "
            "years: he came because he heard English magi were persecuted "
            "here, and because the macgnímartha raiders let him test his "
            "magic on the Hermetically trained, a better fight than hedge "
            "wizards. Violent, scornful of the natives and their ways, he "
            "delights in conflict and in burning the covenant's enemies.",
            "He has made a spell that raises a wall of fire on a Boundary, "
            "ringing the covenant during a raid; he burns those trapped "
            "inside and then hunts the survivors down. Bored of waiting "
            "for attacks, he has begun Wizard Wars against Irish magi. He "
            "backed the Siege of Praesis eagerly, spending seasons there "
            "teaching the attackers Ignem spells and doing much to bring "
            "the island covenant down, and he is a firm friend of Ballack "
            "and the new Praesis.",
        ),
        traits={"Violent": 3, "Xenophobic": 2, "Joyful": 1},
    )


# --------------------------------------------------------------- Leth Moga


def _leth_moga(hibernia: Hibernia, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The southern Mercer House, sister to Leth Cuinn, serving every "
        "covenant south of the Eiscir Riada from the village monastery of "
        "Cloyne in Desmond. It is not a covenant at law: it keeps no "
        "cathach, needs no cattle, and stands because it serves the "
        "Tribunal, guarded by many rulings of the Peripheral Code. The "
        "book gives it no device.",
        "Where the northern Redcaps train as warriors, Leth Moga's are "
        "the Tribunal's eye-witnesses and keep its history, above all in "
        "the Red Book of Cloyne. It takes no side between the Ordo "
        "Hiberniae and the English magi, though who may read the Red Book "
        "is a sore point with both.",
    )
    what_matters = _lines(
        "Income: its barn laboratory, rented to visiting magi for one pawn of vis a season",
        "Vis: stored behind locked doors in the caves beneath Cloyne; the book gives no amount",
        "Library: the Red Book of Cloyne (Diarmait's own, under his sanctum marker)",
        "Services: Redcaps as witnesses and recorders at Hermetic gatherings, each trained in the Art of Memory",
        "Hook: Mercer House",
        "Hook: Monastery (Cloyne's monks, on good terms)",
        "Boon: Hidden Resources (records, vis and magic items in the tunnels under the village)",
        "Hook: Hermetic Politics (magi who want the Red Book opened)",
        "Tension: who succeeds Diarmait, Gopstan or Luathan",
    )
    notes = paragraphs(
        "History. Leth Moga and Leth Cuinn were made in 898, out of "
        "Hibernia's first meeting as a Tribunal of its own. The Redcap "
        "Imag, wife of Cloyne's abbot Cian Ua Cathain, offered land and "
        "leadership and was given the southern house: he led the dozen "
        "monks and the monastery's people, she ran the House. After the "
        "monastic chroniclers' example she began the Red Book of Cloyne, "
        "the Tribunal's Hermetic history, and her successors have kept "
        "it up.",
        "The Red Book was open to all until Fergal mac Cuircc, leader "
        "after the Schism War, recorded the war faithfully and then shut "
        "the book on it, saying the magi had to forget; from then only "
        "Redcaps could read it. In the twelfth century magi argued that "
        "its eye-witness records would be useful evidence at law. "
        "Fergal's son-in-law and successor Diarmait agreed that each "
        "Redcap's own testimony should be available, but held that the "
        "book, inherited from Fergal as his own, lay under his sanctum "
        "marker; the Tribunal agreed, and several magi still resent it.",
        "The House. A large wooden house and a little-used barn on the "
        "southern edge of the monastery. The barn, draughty and cold on "
        "a Magic aura of 1, serves well enough as a laboratory; with no "
        "Gifted Redcap in residence, Diarmait rents it to other magi. "
        "Guest magi recast a weak Aegis of the Hearth round house and "
        "barn each year. The House's valuables, its records, stored vis "
        "and magic items, are kept behind locked doors in the caves "
        "under the village, out of the monks' way; Diarmait knows the "
        "tunnels far better than the abbot.",
        "Culture. Monks and Redcaps keep apart but on good terms, and the "
        "Redcaps mix freely with the villagers. Every Redcap here is kin "
        "to Imag through the female line, so with the abbot's household "
        "and the married Redcaps' families the House is hardly secret. "
        "All have been initiated into the Art of Memory, and after "
        "witnessing an event each must write it into the Red Book, a "
        "chore but not a heavy one. Apprentices who skip the "
        "macgnímartha sometimes come here for shelter, board and the "
        "libraries in return for copying and other service.",
        "Its Redcaps: six, none Gifted, Diarmait and his filius Gopstan, "
        "Ercc Cam and his filius Luathan, and the tearful Rónán and his "
        "filia Áine. Their worry is their ageing leader: by custom his "
        "filius follows him, but that is in doubt, and since leadership "
        "is not the Tribunal's business, the Redcaps must settle it.",
        "The book gives no season; Autumn is assumed, for an old leader "
        "and an open succession.",
    )
    covenant = b.covenant(
        "Leth Moga",
        tribunal=tribunal,
        founded=898,
        place=hibernia.places["cloyne"],
        aura=1,
        realm="Magic",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        detail=FULL,
        season="Autumn",
    )
    hibernia.covenants["leth_moga"] = covenant
    b.book(
        covenant,
        "The Red Book of Cloyne",
        "Other",
        author="Imag and the leaders of Leth Moga after her",
        description=paragraphs(
            "The annals of the Order in Hibernia since 898, kept by Leth "
            "Moga's Redcaps from their own eye-witness accounts: Imag "
            "began it, Fergal mac Cuircc recorded the Schism War in it "
            "and then closed it to all but Redcaps, and Gopstan has spent "
            "many hours entering recent events. It also keeps old Irish "
            "lore, such as the tale of Eoghan Mór carried off alive from "
            "Magh Léana.",
            "Diarmait holds it as his own property under his sanctum "
            "marker, by a ruling of the Tribunal; he will not have it "
            "copied but would like it to be seen. It is kept in the "
            "House's scriptorium, which has few defences. The book gives "
            "it no level or quality.",
        ),
    )
    m = hibernia.magi
    m["diarmait"] = b.magus(
        "Diarmait mac Fergaile",
        covenant=covenant,
        house=MERCERE,
        age=121,
        summary=paragraphs(
            "Leader of Leth Moga, an un-Gifted Redcap who looks seventy-"
            "five, and Fergal's son-in-law, who took over when his parens "
            "Fergal died; the Red Book came to him from Fergal as his own "
            "property. Unlike Fergal he thinks opening the Red Book to "
            "readers would add to its worth: it must not be copied, but it "
            "should be seen.",
            "The other Redcaps care more about whom he will name to follow "
            "him, Gopstan or Luathan. Dáire Cú of Leth Cuinn thinks him "
            "too doddering and bookish to lead the Tribunal's Redcaps.",
        ),
        traits={"Selfish": 3, "Worried": 2},
    )
    m["gopstan"] = b.magus(
        "Gopstan mac Diarmata",
        covenant=covenant,
        house=MERCERE,
        age=52,
        summary=paragraphs(
            "Diarmait's filius and son-in-law, looking thirty-seven, who "
            "has never left Ireland; his name comes from Irish slang for "
            "'Poor John'. Born rich, he gave away his goods with a show "
            "when he passed his Gauntlet. He was apprenticed late and "
            "knows House Mercere's ways less well than Redcaps of his age, "
            "which weighs on Diarmait when he thinks of handing over the "
            "House.",
            "He loves the Red Book dearly and has spent hours writing "
            "recent events into it. He once spent a year at Cashel posing "
            "as an unlettered prince's son to read its library, and was "
            "found out.",
        ),
        traits={"Eager": 2, "Entitled": 2},
    )
    m["ercc"] = b.magus(
        "Ercc Cam",
        covenant=covenant,
        house=MERCERE,
        age=None,
        summary=(
            "A Redcap of Leth Moga, un-Gifted like all its Redcaps, who "
            "trained his nephew Luathan as his filius. The book gives no "
            "more of him."
        ),
    )
    m["luathan"] = b.magus(
        "Luathan",
        covenant=covenant,
        house=MERCERE,
        age=33,
        summary=paragraphs(
            "Ercc Cam's filius and nephew, dashing and handsome and the "
            "best-loved Redcap of the south. He has the temper for the "
            "Cult of Heroes, but when he took his uncle's offer to train "
            "him his angry mother laid a geas on him, 'forever mundane or "
            "forever lame', so he may learn no Virtue that would give him "
            "quasi-magical powers; barred from the initiations of Leth "
            "Cuinn, he stayed south of the Eiscir Riada.",
            "He makes good use of magic items instead: a cloak that turns "
            "him into an eagle and a harpoon that lets him breathe under "
            "water.",
        ),
        traits={"Smiling": 3, "Foolhardy": 2},
    )
    m["ronan"] = b.magus(
        "Rónán",
        covenant=covenant,
        house=MERCERE,
        age=None,
        summary=(
            "A weepy Redcap of Leth Moga, parens of Áine. The book gives "
            "no more of him."
        ),
    )
    m["aine"] = b.magus(
        "Áine",
        covenant=covenant,
        house=MERCERE,
        age=None,
        summary=(
            "A Redcap of Leth Moga, Rónán's filia. The book gives no more of her."
        ),
    )


# ---------------------------------------------------------------- finish

#: The English lords of Munster, who answer to the Lord of Ireland.
ENGLISH_LORDS = (
    "le_poer",
    "de_braose",
    "fitzstephen",
    "de_cogan",
    "butler",
    "de_burgh",
    "de_worcester",
)
#: The churches of the chapter, which answer to the Archbishop of Cashel.
CASHEL_CHURCHES = ("st_flannan", "singeal", "cloyne_monastery", "cape_clear_monks")


def finish(hibernia: Hibernia) -> None:
    """Join Munster's records to the tops of the hierarchies other parts
    make: the English lords and the king's city of Waterford to the Lord
    of Ireland, the Déise to the le Poer lands, and the churches and the
    schools of Cashel to the Archbishop of Cashel. Anything not yet made
    is skipped."""
    w = hibernia.world
    lord_of_ireland = w.get("henry_iii")
    if lord_of_ireland is not None:
        for key in (*ENGLISH_LORDS, "waterford"):
            record = w.get(key)
            if record is not None and record.answers_to is None:
                record.answers_to = lord_of_ireland.id
    deise, le_poer = w.get("deise"), w.get("le_poer")
    if deise is not None and le_poer is not None and deise.answers_to is None:
        deise.answers_to = le_poer.id
    cashel = w.get("cashel")
    if cashel is not None:
        for key in (*CASHEL_CHURCHES, "cashel_school"):
            record = w.get(key)
            if record is not None and record.answers_to is None:
                record.answers_to = cashel.id


# --------------------------------------------------------------- stats

P = Profile
IRISH = "Irish"
LORE = "Area Lore: Hibernian Tribunal"
MUNSTER = "Area Lore: Munster"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus and Redcap the chapter sketches without a stat block, by key.
PROFILES: dict[str, Profile] = {
    "milvia": P(
        strong="int com pre",
        weak="str dex",
        arts={"Me": 7, "In": 6, "Re": 5, "Vi": 4},
        abilities={
            "Leadership": (5, "the Tribunal"),
            "Intrigue": (5, "Hermetic politics"),
            "Code of Hermes": (5, "the Peripheral Code"),
            LORE: (4, "covenants"),
            "Organization Lore: Order of Hermes": 3,
            "Living Language: English": 2,
        },
        virtues=[
            "Hermetic Prestige",
            "Clear Thinker",
            "Obsessed (Minor)",
            "Dutybound",
        ],
        native=IRISH,
    ),
    "visioturpis": P(
        strong="int per",
        weak="pre com",
        arts={"In": 9, "Me": 6, "Vi": 5, "Re": 3},
        abilities={
            "Code of Hermes": (6, "Quaesitorial procedure"),
            "Folk Ken": (3, "magi"),
            LORE: (4, "covenants"),
            "Intrigue": 2,
        },
        virtues=["Painful Magic", "Disfigured", "Wrathful (Minor)"],
        native=IRISH,
    ),
    "conan_derg": P(
        strong="pre sta com",
        arts={"Mu": 7, "Im": 6, "He": 5, "An": 4, "Re": 4},
        abilities={
            "Faerie Lore": (6, "the Tuatha Dé"),
            "Code of Hermes": (4, "the Peripheral Code"),
            LORE: (5, "history"),
            "Leadership": 3,
        },
        virtues=[
            ("Strong Faerie Blood", {"blood": "Tuatha Dé"}),
            "Missing Hand",
            "Reclusive",
            "Stuck in Your Ways",
        ],
        native=IRISH,
    ),
    "faisgia": P(
        strong="sta per",
        weak="com",
        arts={"Re": 7, "Te": 7, "Mu": 6, "Co": 4, "Vi": 4},
        abilities={
            "Faerie Lore": (6, "the Schism War"),
            MUNSTER: (4, "faerie haunts"),
            "Survival": 3,
        },
        virtues=[_art("Affinity with {art}", "terram"), "Wrathful (Minor)"],
        native=IRISH,
    ),
    "ruaidri": P(
        strong="int sta",
        arts={"Re": 9, "Mu": 4, "Im": 4, "Vi": 3},
        abilities={"Faerie Lore": (4, "the Tuatha Dé"), LORE: 3},
        virtues=[],
        age=95,
        native=IRISH,
    ),
    "aine_dhubh": P(
        strong="int per",
        arts={"He": 9, "Mu": 5, "Cr": 4, "Im": 3},
        abilities={"Faerie Lore": (4, "forest fae"), "Survival": 2, LORE: 2},
        virtues=[],
        age=75,
        native=IRISH,
    ),
    "coscrach": P(
        strong="sta str qik",
        weak="com",
        arts={"Pe": 6, "Ig": 5, "Re": 5, "Mu": 4, "Co": 3},
        abilities={
            "Faerie Lore": (4, "fighting faeries"),
            "Single Weapon": (3, "spear"),
            "Brawl": 2,
        },
        virtues=["Tough", "Reckless (Minor)"],
        age=65,
        native=IRISH,
    ),
    "palantus": P(
        strong="int com",
        weak="pre",
        arts={"Me": 8, "Re": 6, "Im": 5, "In": 4},
        abilities={
            "Living Language: Irish": (5, "archaic forms"),
            "Faerie Lore": (4, "faerie speech"),
            "Magic Theory": (5, "original research"),
            "Artes Liberales": (3, "grammar"),
        },
        virtues=["Linguist", "Reclusive"],
        native="High German",
    ),
    "styrbjorn": P(
        strong="int dex",
        weak="pre com",
        arts={"Cr": 6, "Re": 5, "Te": 5, "Ig": 4, "Vi": 4},
        abilities={
            "Craft: Goldsmith": (5, "jewellery"),
            "Craft: Smith": (4, "weapons"),
            "Living Language: Old Norse": 4,
        },
        virtues=[_art("Affinity with {art}", "terram"), "Reclusive"],
        native=IRISH,
    ),
    "oswald": P(
        strong="int com per",
        weak="str",
        arts={"An": 7, "Mu": 6, "Re": 5, "Im": 4, "In": 4, "Me": 3},
        abilities={
            "Profession: Scribe": (5, "copying"),
            "Artes Liberales": (4, "grammar"),
            "Teaching": (4, "apprentices"),
            "Guile": (3, "lying to magi"),
            "Living Language: English": 5,
            "Animal Ken": 2,
        },
        virtues=["Gentle Gift", "Book Learner", "Small Frame", "Obsessed (Major)"],
        native=IRISH,
    ),
    "lugardis": P(
        strong="int pre per",
        weak="com",
        arts={"In": 8, "Me": 7, "Re": 4, "Vi": 4},
        abilities={
            "Code of Hermes": (6, "the Peripheral Code"),
            "Intrigue": (4, "Hermetic politics"),
            "Organization Lore: Order of Hermes": (4, "Quaesitores"),
            "Living Language: English": 3,
            "Living Language: Irish": 2,
        },
        virtues=["Blatant Gift", "Well-Traveled"],
        native="Italian",
    ),
    "igneous_drake": P(
        strong="sta pre qik",
        weak="com int",
        arts={"Ig": 9, "Cr": 7, "Pe": 6, "Re": 4},
        abilities={
            "Penetration": (5, "Ignem"),
            "Hunt": (3, "fugitives"),
            "Athletics": 2,
        },
        virtues=[_art("Puissant {art}", "ignem"), "Wrathful (Major)", "Hatred (Minor)"],
        native="English",
    ),
    "diarmait": P(
        gifted=False,
        strong="int per",
        weak="str qik",
        abilities={
            "Organization Lore: Order of Hermes": (5, "Hibernian history"),
            LORE: (5, "covenants"),
            "Profession: Scribe": (4, "annals"),
            "Dead Language: Latin": 4,
            "Code of Hermes": 3,
            "Ride": 2,
        },
        virtues=["Redcap", "Greedy (Minor)", "Dutybound", "Close Family Ties"],
        native=IRISH,
    ),
    "gopstan": P(
        gifted=False,
        strong="int com",
        abilities={
            "Profession: Scribe": (4, "annals"),
            "Dead Language: Latin": 4,
            LORE: 3,
            "Artes Liberales": 2,
            "Guile": 2,
            "Ride": 2,
        },
        virtues=["Redcap", "Proud (Minor)", "Close Family Ties", "Heir"],
        native=IRISH,
    ),
    "ercc": P(
        gifted=False,
        strong="sta per",
        abilities={
            "Ride": (4, "long journeys"),
            LORE: (4, "covenants"),
            "Organization Lore: Order of Hermes": 3,
            "Dead Language: Latin": 3,
        },
        virtues=["Redcap", "Dutybound", "Close Family Ties", "Covenant Upbringing"],
        age=75,
        native=IRISH,
    ),
    "luathan": P(
        gifted=False,
        strong="pre qik dex",
        abilities={
            "Charm": (4, "first impressions"),
            "Athletics": 3,
            "Swim": 3,
            "Thrown Weapon": (3, "harpoon"),
            LORE: 3,
            "Ride": 2,
        },
        virtues=["Redcap", "Reckless (Minor)", "Close Family Ties", "Carefree"],
        native=IRISH,
    ),
    "ronan": P(
        gifted=False,
        strong="per sta",
        abilities={
            "Ride": (3, "long journeys"),
            LORE: (4, "covenants"),
            "Profession: Scribe": 3,
            "Dead Language: Latin": 3,
        },
        virtues=[
            "Redcap",
            "Oversensitive (Minor)",
            "Close Family Ties",
            "Covenant Upbringing",
        ],
        age=70,
        native=IRISH,
    ),
    "aine": P(
        gifted=False,
        strong="per com",
        abilities={
            "Ride": (4, "long journeys"),
            LORE: (3, "covenants"),
            "Profession: Scribe": 2,
            "Dead Language: Latin": 3,
        },
        virtues=["Redcap", "Close Family Ties", "Covenant Upbringing", "Dutybound"],
        age=40,
        native=IRISH,
    ),
}


def stats(hibernia: Hibernia) -> None:
    """Generated stats for Munster's magi and Redcaps, none of whom has a
    printed stat block."""
    b = hibernia.b
    for key, profile in PROFILES.items():
        character = hibernia.magi.get(key)
        if character is not None:
            apply(b, character, profile)
