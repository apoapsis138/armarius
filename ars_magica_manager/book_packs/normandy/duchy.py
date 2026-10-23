"""The Duchy of Normandy, as of spring 1220: the Seine basin and Rouen,
the county of Bayeux with Caen, the Cotentin peninsula, Avranches and
Mont St. Michel, each with its places, towns, churches and lords; the
crown's bailli and the Archdiocese of Rouen; and the living covenant of
Montverte with its inner council of five, its library and its vassals,
in paraphrase of The Lion and the Lily, chapter five.

Confluensis and Dragon's Rest are confluensis.py's, and the ruined
covenants of the duchy (Baiocassium, Baiocassium Minor, Pagus,
Rotomagus, Aedes Salii, the Orchard of Sour Apples) are tribunal.py's;
they are named here only where a place's story needs them. The King
whom the duchy now answers to is ile_de_france.py's, linked in
`finish` once it exists.

Each record is kept under a slug in `normandy.places`, `.covenants`,
`.magi` or `.world`, so the other parts can find it."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, joined_lines, paragraphs, vf_ability, vf_art, vf_focus
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Character, Covenant, Neighbour, Tribunal
    from . import Normandy

# House ids, so a typo cannot slip into a record.
FLAMBEAU = "house_flambeau"
TREMERE = "house_tremere"
TYTALUS = "house_tytalus"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}

#: The arms of Normandy: gules, two lions passant or.
NORMANDY_ARMS = Arms("Gules", charge="Lion", charge_tincture="Or", count=2)


def _place(normandy: Normandy, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


def build(normandy: Normandy) -> None:
    b = normandy.b
    tribunal = normandy.tribunal
    assert tribunal is not None
    _places(normandy)
    _crown_and_lords(normandy, b)
    _church(normandy, b)
    _towns(normandy, b)
    _people(normandy, b)
    _montverte(normandy, b, tribunal)


def finish(normandy: Normandy) -> None:
    """Set the duchy's lords under the King, once ile_de_france.py has
    made him: the crown stands in the duke's place since 1204."""
    king = normandy.world.get("king") or next(
        (
            n
            for n in normandy.b.saga.neighbours
            if n.kind == "lord" and "Philip" in n.name and "King" in n.name
        ),
        None,
    )
    if king is None:
        return
    for key in (
        "duchy_of_normandy",
        "bailli_of_rouen",
        "bailli_of_caen",
        "bailli_of_bayeux",
        "bailli_of_cotentin",
    ):
        record = normandy.world.get(key)
        if record is not None and record.answers_to is None:
            record.answers_to = king.id


# ------------------------------------------------------------------ places


def _places(normandy: Normandy) -> None:
    duchy = _place(
        normandy,
        "normandy",
        "The Duchy of Normandy",
        summary=paragraphs(
            "The northern duchy on the Channel coast, its shore a mix of sand "
            "and sheer white cliffs with England a hazy enemy across the water. "
            "Brittany and Maine lie south, the royal demesne and Flanders east. "
            "It is a land of heavy forest and many castles, cleared for farming "
            "mainly in the Seine basin in the east; its regions are the Seine "
            "basin, the county of Bayeux, the Cotentin peninsula and the small "
            "county of Avranches, with uplands in the south.",
            "Gallic tribes held it first, and the faerie folk they once "
            "worshipped still remember them fondly. Rome made it Secunda "
            "Provincia Lugdunensis; the Franks made it part of Neustria; in the "
            "ninth and tenth centuries Norse raiders overran it, settled, and "
            "their chief became its duke. Since then it has been the French "
            "crown's sometime ally and frequent enemy, until Philip II took it "
            "from the English king in 1203 and 1204.",
            "Lutins, small servile goblins (Faerie Might 5, Aquam), are common "
            "in the Norman faerie courts and in villages without a church. They "
            "clean houses in return for offal or clean water, avoid being seen, "
            "know everything in the room they stand in, can make a floor slick "
            "with suds, and carry a pawn of Aquam vis in the heart. All of them "
            "dread a 'goblin duke of Normandy' of whom the Order knows nothing.",
            "Living covenants: Confluensis on the Cotentin, its vassal Dragon's "
            "Rest at the mouth of the Seine, and Montverte in the southern "
            "uplands. The ruins of Aedes Salii, Baiocassium, Baiocassium Minor, "
            "Pagus, Rotomagus and the Orchard of Sour Apples (where Confluensis "
            "now stands) lie here too.",
        ),
        **KNOWN_ORDER,
    )

    # -- the Seine basin --
    seine = _place(
        normandy,
        "seine_basin",
        "The Seine Basin",
        inside=duchy,
        summary=paragraphs(
            "The fertile heart of the duchy: the counties of Rouen, Lisieux and "
            "Evreux along the winding Seine, the river road from Paris to the "
            "sea, with Dragon's Rest at its mouth. Prosperous towns line the "
            "river and its tributaries. Most of the old forest was felled long "
            "ago, leaving fragments such as the Forest of Lyons.",
            "Low stone walls split the fields into small plots, the bocage that "
            "sets Normandy apart from the Paris country. Wheat and oats make the "
            "bread; barley for beer is fickle and its failures leave peasants in "
            "debt, and frost often kills the autumn wheat, so the fields are "
            "resown with oats in spring. Cattle thrive on the grass, and the "
            "monks brought vines: much thin Norman wine goes downriver by barge "
            "to the towns but is not exported. A covenant that boosts its farms "
            "or its wine with Creo Herbam may find peasants at its gate wanting "
            "the same.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _place(
        normandy,
        "forest_of_lyons",
        "The Forest of Lyons",
        inside=seine,
        realm="Magic",
        summary="A surviving fragment of the primordial forest of the Seine basin, "
        "a favourite hunting ground of the Norman nobility. A castle stands "
        "at its heart, and building it destroyed the spirit of the forest.",
        secrets="The wild woodsmen say the forest is not dead and will rise one day "
        "to take back its heart.",
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "seine_bridges",
        "The Haunted Bridges of the Seine",
        inside=seine,
        realm="",
        summary=(
            "Ruined fortified bridges at the Seine's narrows, built to stop "
            "Viking ships rowing upstream. Most have been quarried for farms and "
            "town houses, but a few are kept up as tollhouses. Ghosts of Norse "
            "and Frankish warriors are said to haunt several of them, and "
            "silently act out their deaths again by the light of the waning "
            "moon."
        ),
        **RUMOURED,
    )

    # -- the county of Bayeux --
    bayeux = _place(
        normandy,
        "bayeux_county",
        "The County of Bayeux",
        inside=duchy,
        realm="Faerie",
        summary=paragraphs(
            "A forested county west of the Seine basin, its villages set in "
            "cleared valleys round a monastery or a manor; its two large towns, "
            "Caen and Bayeux, lie near the coast. The ruin of the Diedne covenant "
            "Baiocassium is in the forest. The people grow more numerous each "
            "generation and the forest shrinks before them.",
            "Pigs outnumber every other beast and run half wild in the woods. "
            "Each autumn the villages cull and salt them for winter, but "
            "woodland faeries claim the swine as theirs, and wise headmen honour "
            "the local court with a feast or a payment before the cull begins, "
            "a custom the Church distrusts and discourages.",
            "St Vigor, bishop here in the early sixth century, destroyed a pagan "
            "temple that was still in use. The faeries of Bayeux have never "
            "forgiven it and have schemed ever since to break the Divine's hold "
            "on the county.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _place(
        normandy,
        "white_ladies",
        "Courts of the White Ladies",
        inside=bayeux,
        realm="Faerie",
        summary=paragraphs(
            "A scatter of faerie regiones near the town of Bayeux, ruled by the "
            "white ladies, a coterie of Sidhe said to be sisters of the Lady of "
            "the Lake. They live for dancing and are always hunting for mortal "
            "partners: a lady and her minstrels wait at a narrow place near "
            "their court, a bridge, a ford or a gorge, and stop a passing man to "
            "ask him to dance.",
            "A man who refuses, or treads on her feet, is flung from the road by "
            "her mocking court; a fine dancer is rewarded, and may be asked to "
            "the great ball one of the ladies holds for the others every spring "
            "equinox. Who brings the best partner there decides which lady is "
            "foremost for the coming year.",
        ),
        **RUMOURED,
    )

    # -- the Cotentin --
    cotentin = _place(
        normandy,
        "cotentin",
        "The Cotentin Peninsula",
        inside=duchy,
        summary=paragraphs(
            "A thinly peopled, poor peninsula, much of it foul swamp and marsh, "
            "with a few castles and towns on the dry ground. Confluensis, the "
            "great Quaesitorial covenant, stands on the peninsula; the ruin of "
            "Pagus lies near Cherbourg, and a chapter house of the Rhine's "
            "Fengheld at Cherbourg controversially harvests some of Pagus's old "
            "vis sources.",
            "Anyone crossing the swamps rolls Stamina against 3 or catches the "
            "fen ague: a Heavy Wound with shaking, chills and endless fever. "
            "Hermetic magic can cure it.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _place(
        normandy,
        "forest_of_brix",
        "The Forest of Brix",
        inside=cotentin,
        realm="Faerie",
        summary=(
            "Forest south of Cherbourg where packs of savage faerie wolves "
            "ambush travellers. The villagers who live in it walk its paths "
            "safely."
        ),
        **KNOWN_LOCALLY,
    )
    _place(
        normandy,
        "hague_dicke",
        "The Hague-Dicke",
        inside=cotentin,
        realm="",
        summary=(
            "A Norse earthwork of the ninth century cutting off the north-west "
            "tip of the Cotentin, once barracks for raiders stranded by winter "
            "seas and a staging post in the raiding season. Now it is overgrown "
            "and unmanned, and even its line is uncertain. Rumour says raiders "
            "too laden with monastery loot buried treasure along it."
        ),
        **RUMOURED,
    )
    _place(
        normandy,
        "vacant_castle",
        "The Vacant Castle",
        inside=cotentin,
        realm="Magic",
        summary=paragraphs(
            "A castle on the Cotentin left empty since 1204, now the lair of a "
            "monstrous she-creature of Grendel's kin, freed by one of King "
            "John's vassals as he fled, who stalks its corridors for human "
            "flesh. A Hermetic expedition in 1218 lost several grogs without "
            "finding her for certain, but found a strong Magic aura.",
            "The expedition means to propose at the next Tribunal that "
            "colonists found a covenant here. The crown's officials would want "
            "the castle back in the feudal order, so settlers would do well to "
            "get a royal grant first.",
        ),
        **RUMOURED,
    )

    # -- Avranches and the Mont --
    avranches = _place(
        normandy,
        "avranches_county",
        "The County of Avranches",
        inside=duchy,
        summary=(
            "The small county on Normandy's southern border with Brittany. Its "
            "see is the town of Avranches on the Couesnon, but its great holy "
            "place is the Benedictine abbey of Mont St. Michel at the river's "
            "mouth."
        ),
        **KNOWN_TRIBUNAL,
    )
    _place(
        normandy,
        "mont_st_michel",
        "Mont St. Michel",
        inside=avranches,
        realm="Divine",
        aura=4,
        levels=[
            Builder.level(
                "The Mont at high tide",
                8,
                "Divine",
                enter=(
                    "Only at low tide: at high tide no one may enter or leave, "
                    "not even by flying or swimming."
                ),
                see=(
                    "From the shore an image of the abbey is still seen, but "
                    "it does not show what happens inside."
                ),
                notes=(
                    "When the tide is in and the sands lie under thirty feet "
                    "of water, the whole abbey passes into a Divine regio."
                ),
            )
        ],
        summary=paragraphs(
            "A rocky islet at the mouth of the Couesnon on the Breton "
            "border, crowned by a Benedictine abbey that draws many "
            "pilgrims. Once called Mount Tombe, it was a ritual site of the "
            "druids who came before House Diedne, until in 708 the "
            "archangel Michael appeared to Aubert, bishop of Avranches, and "
            "bade him desecrate the pagan graves and build a chapel. Aubert "
            "was slow to obey but finished in 709. His relics, kept here, "
            "include his skull, pierced where the angel struck him for his "
            "delay.",
            "Hermetic scholars think Aubert destroyed a Magic aura and that "
            "taking his relics away might in time revive it, but fear of the "
            "Divine and of the Diedne taint has kept every magus away.",
            "At low tide pilgrims cross less than a mile of sand to it, "
            "dangerous with quicksand (William the Conqueror had to be "
            "pulled out). Then its Divine aura is 4; at high tide it is "
            "a regio of 8.",
        ),
        secrets="The Uncovered Crypt: a magus dreams of the archangel pointing to "
        "the Mont, with headaches that halve her Study and Lab Totals until "
        "she goes. As she arrives, builders open a crypt under a tower: a "
        "dozen skeletons and an untitled Holy Magic Theory summa (Level 3, "
        "Quality 17). Whoever studies it is visited by Michael, who means "
        "to replace Hermetic magic, which he thinks pagan, with a Divine "
        "kind.",
        **KNOWN_ORDER,
    )

    # -- Montverte's hill --
    _place(
        normandy,
        "montverte_site",
        "The Green Mount of Montverte",
        inside=duchy,
        realm="Magic",
        aura=5,
        summary=(
            "A rocky hill in the uplands of southern Normandy, crowned by a "
            "sprawling Norman keep built on an old Carolingian fort, a smaller "
            "copy of the mount of Laon. Concentric walls step down the slopes "
            "with exotic hanging gardens among them, watered by a spring near "
            "the top that an early magus is said to have called forth, running "
            "down in a web of little streams. The hill is at once lovely and "
            "grim. The baron's large village lies in the valley below."
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------- crown and lords


def _crown_and_lords(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    duchy = normandy.places["normandy"]
    w["duchy_of_normandy"] = b.lord(
        "Duke of Normandy (held by the Crown)",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="Rouen",
        ruler="King Philip II of France, in the duke's place",
        place=duchy,
        arms=NORMANDY_ARMS,
        summary=paragraphs(
            "The Normans held their duchy to be an allod, given outright to the "
            "duke, which the French crown did not always accept. Since the "
            "conquest of 1203 to 1204 there has been no duke: the King rules "
            "Normandy directly and simply takes the duke's seat at the head of "
            "the feudal table, leaving the vassals' ties much as they were. "
            "Many lesser Anglo-Norman lords still hold land on both sides of "
            "the Channel, but Philip keeps the strategic places for himself "
            "and a few close allies. The English claimant is Henry III.",
            "The duchy was always heavily armed. The dukes hired Flemish, "
            "Norse and German mercenaries for great campaigns, whose captains "
            "often became vassals, and the bishop of Bayeux alone has a hundred "
            "knights. The dukes tried to keep their vassals from private war, "
            "judging quarrels in their court, where the usual penalty was loss "
            "of land; when war came anyway, the beaten could not be ransomed "
            "or plundered nor their houses and mills burnt. Philip upholds "
            "these rules.",
            "Most large towns hold charters letting their burgesses elect "
            "mayors, councils and courts for a collective rent; Philip has "
            "confirmed the great towns' charters, but many small ones were sold "
            "by King John in his last scramble for money before 1204 and the "
            "crown likes them less. A covenant that sheltered under a small "
            "town's easily led magistrates, or was itself chartered by John, "
            "may need new arrangements if the charter goes.",
        ),
    )
    w["henry_iii"] = b.lord(
        "Henry III of England",
        title="duke",
        wealth="Wealthy",
        manors=0,
        seat="England",
        ruler="Henry III",
        summary=(
            "The young King of England, who still claims the duchy of Normandy "
            "his father John lost to the French in 1204. England, conquered by "
            "the Normans in 1066, broods across the Channel as France's "
            "troublesome enemy."
        ),
    )
    bailli = (
        (
            "bailli_of_rouen",
            "Bailli of Rouen",
            "Jean de la Porte",
            1219,
            "seine_basin",
            "Rouen",
        ),
        (
            "bailli_of_caen",
            "Bailli of Caen",
            "Pierre du Thillai",
            1205,
            "bayeux_county",
            "Caen",
        ),
        (
            "bailli_of_bayeux",
            "Bailli of Bayeux",
            "Renaud de Ville-Thierry",
            1206,
            "bayeux_county",
            "Bayeux",
        ),
        (
            "bailli_of_cotentin",
            "Bailli of Cotentin",
            "Miles de Levis",
            1215,
            "cotentin",
            "",
        ),
    )
    for key, name, holder, appointed, place, seat in bailli:
        w[key] = b.lord(
            name,
            title="landed",
            wealth="Wealthy",
            manors=0,
            seat=seat,
            ruler=holder,
            place=normandy.places[place],
            summary=paragraphs(
                f"{holder}, appointed in {appointed}: one of the King's bailli, "
                "the salaried professional administrators of the bailliages "
                "that roughly follow the old Norman counties. Bailli are paid "
                "several hundred pounds a year, are drawn on purpose from "
                "neither the great families nor the Church (some are minor "
                "nobles or former officers), and are as a rule honest and loyal "
                "to the King. None is a Norman. From the 1220s, if history "
                "holds, they serve only three or four years.",
                "The bailli know the Order exists and where some covenants "
                "are, though nothing more. If magic brings disaster on the "
                "duchy, they may come to those covenants for help, or for "
                "suspects; otherwise a covenant that pays its taxes and leaves "
                "the feudal order alone is of no interest to them.",
            ),
        )
    w["baron_of_montverte"] = b.lord(
        "Baron of Montverte",
        title="baron",
        seat="The castle of Montverte",
        place=normandy.places["montverte_site"],
        summary=paragraphs(
            "Lord of the green mount, descended from Haland, the un-Gifted "
            "Norse elder brother of the founding magus Harivald. His family "
            "took their name from the hilltop castle the brothers seized, "
            "and the magi of Montverte have lived in it beside them since "
            "941. His household is the covenant's covenfolk, and his "
            "soldiers are rather too many and too well armed for a baron. "
            "The magi are called 'the resident scholars' or 'our valued "
            "guests', and the steward Edward sits at his side.",
            "His peers have quarrelled with him often over what the castle "
            "does, but its walls have won every war. The magi swear him no "
            "oath and say he runs his own affairs.",
        ),
        secrets="For generations the family has been wholly, and unknowingly, "
        "ruled by the magi through persuasion and subtle magic. The "
        "baron's high chair, centuries old, was enchanted by an early magus "
        "with a Mentem effect that keeps whoever sits in it compliant; long "
        "use has left a line of slightly Warped barons.",
    )


# ------------------------------------------------------------------ church


def _church(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    archbishop = w["archbishop_of_rouen"] = b.church(
        "Archbishop of Rouen",
        church="Archbishop's cathedral",
        order="secular clergy",
        ruler="Master Robert Poulain",
        place=p["seine_basin"],
        summary=paragraphs(
            "Metropolitan of a province whose borders almost match the "
            "duchy's, a hard-fought field in the conversion of the pagans. "
            "The first bishop, Nicaise, was martyred on arrival from Rome in "
            "the mid-third century; St Mellon founded the see, which became "
            "an archdiocese in 744. Sainted bishops include St Ouen "
            "(641-684), who converted or destroyed many pagans, and St "
            "Romanus, who overcame the Gargouille.",
            "The archbishop since 1208 is Master Robert Poulain, a "
            "theologian; if history holds, Thibaud d'Amiens follows him in "
            "1222. He holds the Order of Hermes heretical but has only "
            "argued the point with his bishops, who are not persuaded. The "
            "Norman church accepted Philip as king, by the Pope's leave; "
            "Philip has not meddled in elections and has given generously "
            "to religious houses, but in 1218 he made the archbishop yield "
            "the King's officers from excommunication.",
            "Each year Rouen's clergy pick one condemned prisoner to be "
            "pardoned before St Romanus's relics, remembering the prisoner "
            "who helped the saint drag the Gargouille, a scaled beast of the "
            "Seine with pale blue eyes, back to the town to be burned.",
        ),
        secrets="The Gargouille: townsmen are found dead near a covenant and the "
        "magi blamed. Archbishop Robert calls the magi the Gargouilles of "
        "the age, frees half a dozen condemned men and marches with them "
        "on the covenant behind the shrine of St Romanus (Faith Points 5). "
        "Harming him could start a crusade against the Order in Normandy; "
        "if the magi are innocent, someone framed them.",
    )
    bishops = (
        (
            "bishop_of_bayeux",
            "Bishop of Bayeux",
            "Master Robert des Ablèges",
            "bayeux_county",
            "A theologian elected in 1206, one of the Jumieges-trained scholar "
            "bishops who know of the Order and have met Hermetic scholars. The "
            "see, founded by St Exuperius in the first century, is one of the "
            "oldest in Mythic Europe; Bishop Odo of Conteville, the Conqueror's "
            "brother, built the fortified cathedral, fought at Hastings and "
            "had the great tapestry made. The bishop has the service of a "
            "hundred knights: twenty owed to the ducal host, ten to the royal "
            "host and seventy for his own use.",
        ),
        (
            "bishop_of_coutances",
            "Bishop of Coutances",
            "Master Hugh Neret",
            "cotentin",
            "A canonist elected in 1208, one of the Jumieges-trained scholar "
            "bishops who know of the Order and have met Hermetic scholars. His "
            "diocese takes in the Cotentin.",
        ),
        (
            "bishop_of_lisieux",
            "Bishop of Lisieux",
            "Master William du Pont-de-l'Arche",
            "seine_basin",
            "A canonist elected in 1218, one of the Jumieges-trained scholar "
            "bishops who know of the Order and have met Hermetic scholars.",
        ),
        (
            "bishop_of_avranches",
            "Bishop of Avranches",
            "William d'Ostilly",
            "avranches_county",
            "A former local dean, elected in 1212. Mont St. Michel lies in his "
            "diocese; his predecessor Aubert built its first chapel at the "
            "archangel's command in 709.",
        ),
        (
            "bishop_of_evreux",
            "Bishop of Evreux",
            "Luke of Evreux",
            "seine_basin",
            "A former local dean, elected in 1203 and now old. If history "
            "holds, he dies in 1220 and the chapter elects another local dean, "
            "Ralph de Cierrey.",
        ),
        (
            "bishop_of_sees",
            "Bishop of Sées",
            "Sylvester of Sées",
            "normandy",
            "The see's former archdeacon, elected in 1201 and now old. If "
            "history holds, he dies in 1220 and Gervase of Chichester, a "
            "foreigner the Pope favours, is elected: a sore point, since the "
            "foreign bishops before Sylvester squandered the diocese's "
            "treasury.",
        ),
    )
    for key, name, holder, place, words in bishops:
        w[key] = b.church(
            name,
            church="Bishop's cathedral",
            order="secular clergy",
            ruler=holder,
            answers_to=archbishop,
            place=p[place],
            summary=words,
        )
    w["rouen_cathedral"] = b.church(
        "Rouen Cathedral",
        church="Archbishop's cathedral",
        order="secular clergy",
        ruler="Master Robert Poulain",
        answers_to=archbishop,
        place=p["seine_basin"],
        summary=paragraphs(
            "The seat of the archdiocese, on a site where the Romans built a "
            "church in the third century and every age since has added to it. "
            "Many Norman nobles lie in its crypt, Rollo among them; some magi "
            "guess the noble dead are rich in Rego vis, but no one has dared "
            "dig them up.",
            "It keeps the original copies of works written at Rouen: St "
            "Victricius's De Laude Sanctorum (Theology summa, Level 5, Quality "
            "11) and Liber Regularum (Civil and Canon Law summa, Level 3, "
            "Quality 10), and Hugh of Amiens's Contra Haereticos (Divine Lore "
            "summa, Level 3, Quality 10, bound with an Infernal Lore tractatus "
            "of Quality 8).",
        ),
    )
    w["jumieges"] = b.church(
        "Abbey of Jumieges",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=archbishop,
        place=p["seine_basin"],
        founded=634,
        summary=paragraphs(
            "A Benedictine abbey on the north bank of the Seine below Rouen, "
            "founded by St Philibert in 634, burned by the Norsemen in the "
            "ninth century and lavishly endowed by the Norman dukes since. "
            "More than a thousand monks live there, with a sizeable town "
            "outside the walls to feed them. It is a great house of learning "
            "with large libraries of religious and philosophical works, and so "
            "many French bishops studied there that its abbot is a power in "
            "the kingdom's politics.",
            "Norman histories are found in its library as in any cathedral or "
            "monastic library: William of Newburgh's Historia rerum Anglicarum "
            "(Area Lore: England summa L5 Q7, Area Lore: Normandy tractatus Q8); "
            "Orderic Vitalis's Ecclesiastical History (Area Lore: Normandy "
            "summa L4 Q8, Area Lore: England summa L3 Q8, Civil and Canon Law "
            "tractatus Q7); William of Jumieges's Historia Normannorum (Area "
            "Lore: Normandy summa L5 Q9, Area Lore: England tractatus Q7, some "
            "copies with a later Normandy tractatus Q8 bringing it to 1137); "
            "and Dudo of St Quentin's History of the Normans (Area Lore: "
            "Normandy summa L4 Q8 and two Normandy tractatus of Q8).",
        ),
    )
    w["st_wandrille"] = b.church(
        "Abbey of St. Wandrille",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=archbishop,
        place=p["seine_basin"],
        summary=(
            "A large Benedictine abbey a day downstream of Jumieges. A Frankish "
            "count of the seventh century founded it; he and his wife "
            "renounced the world on the day they wed. It competes with Jumieges for noble "
            "patrons but is otherwise on good terms with it. Its monks first "
            "settled Mont St. Michel in 966."
        ),
    )
    w["bayeux_cathedral"] = b.church(
        "Bayeux Cathedral",
        church="Bishop's cathedral",
        order="secular clergy",
        ruler="Master Robert des Ablèges",
        answers_to=w["bishop_of_bayeux"],
        place=p["bayeux_county"],
        summary=(
            "Bishop Odo's fortified cathedral, which keeps his tapestry: really "
            "an embroidery nearly a hundred yards long and a yard high, its "
            "pictures captioned in Latin, telling the life of King Harold to "
            "his death at Norman hands. Magic was worked into its threads, and "
            "it is a +2 Sympathetic Connection to the Duke of Normandy and to "
            "the King of England."
        ),
    )
    w["mens_abbey"] = b.church(
        "The Men's Abbey of Caen",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=w["bishop_of_bayeux"],
        place=p["bayeux_county"],
        summary=paragraphs(
            "The fortified abbey William the Conqueror built at Caen, as "
            "Matilda built the Women's Abbey, the price of lifting the "
            "excommunication Pope Nicholas II laid on the cousins for "
            "marrying.",
            "William lies here. He died at the priory of St Gervais in "
            "Rouen in 1087 after a fall from his horse; his body rotted "
            "and stank, his servants defiled it and his courtiers fled, "
            "an omen of the anarchy that followed. A fire broke out as the "
            "corpse reached Caen, and at the funeral the swollen body "
            "burst from its coffin and the bishops, choking, botched the "
            "rite.",
        ),
        secrets="The Infernal Grave: an infernalist's belongings hold The "
        "Conquered Bastard (Infernal Lore tractatus, Quality 6), which says "
        "a demon inhabits William's corpse, helped him to his conquests and "
        "rotted his body, and was trapped in it by the botched rite; the "
        "infernalist's notes show he was trying to free her. Freeing or "
        "destroying her means digging William up and crossing the Church "
        "in Caen. The text may be a forgery, by demons or by rivals in the "
        "Tribunal, to drag the magi into an infernal plot.",
    )
    w["womens_abbey"] = b.church(
        "The Women's Abbey of Caen",
        church="Monastery or nunnery",
        order="Benedictine",
        answers_to=w["bishop_of_bayeux"],
        place=p["bayeux_county"],
        summary=(
            "The fortified abbey Matilda built at Caen, as William built the "
            "Men's Abbey, to win the lifting of their excommunication for "
            "marrying within the forbidden degrees."
        ),
    )
    w["mont_st_michel_abbey"] = b.church(
        "Abbey of Mont St. Michel",
        church="Monastery or nunnery",
        order="Benedictine",
        ruler="Abbot Jordan",
        answers_to=w["bishop_of_avranches"],
        place=p["mont_st_michel"],
        founded=966,
        summary=paragraphs(
            "The archangel's own foundation of the early eighth century, "
            "settled by Benedictines from St. Wandrille under Abbot Maynard in "
            "966 with Duke Richard I's backing. Abbot Hildebert enlarged it "
            "from 1020; in 1203 the Duke of Brittany set a fire that ruined "
            "much of it, and Abbot Jordan has been rebuilding since 1210, work "
            "that if history holds will finish about 1230 (extra hands are "
            "always wanted). Its relics include St Aubert's holed skull and "
            "right arm.",
            "Its founding is told in the anonymous Apparitio Sancti Michaelis "
            "Archangelis in Monte Tumba, a widely copied Divine Lore tractatus "
            "of Quality 11.",
        ),
    )


# ------------------------------------------------------------------- towns


def _towns(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    w["rouen"] = b.town(
        "Rouen",
        charter="Commune",
        ruler="Mayor and council, under the King",
        place=p["seine_basin"],
        summary=paragraphs(
            "Capital of the duchy, on the Seine, founded by the Romans beside a "
            "Gallic village as Rotomagus, chief city of Secunda Provincia "
            "Lugdunensis; a short-lived ninth-century covenant near it took "
            "the same name. Philip II took the town in 1203. Paris's Baltic "
            "shipping passes through, but the cross-Channel trade that made it "
            "rich has dwindled since the annexation, and in 1207 the slump led "
            "Philip to grant it a very generous charter to win support. It has "
            "many churches and the archbishop's cathedral.",
            "A large community of Jewish moneylenders lived here until "
            "renegade knights of the Third Crusade killed many who would not "
            "convert. The survivors prospered for a while practising their "
            "faith in secret, but Philip's laws against the Jews have made "
            "them ever less safe. A few remain in trade, less openly than "
            "before; a magus who floods the markets with magical wealth will "
            "earn their anger.",
        ),
    )
    w["rouen_jews"] = b.faction(
        "The Jewish families of Rouen",
        faction="Family",
        decides="A council",
        place=p["seine_basin"],
        summary=(
            "The few Jewish merchant families left in Rouen after the Third "
            "Crusade's massacres, now quietly in business under Philip II's "
            "harsh laws."
        ),
        wants="Safety, and if the persecution becomes unbearable, flight to Iberia",
        offers=(
            "A large holding of Arabic and Hebrew texts, which they might trade "
            "for magical help to escape; ruthless magi might simply join the "
            "persecution and seize them"
        ),
    )
    w["caen"] = b.town(
        "Caen",
        charter="Commune",
        place=p["bayeux_county"],
        summary=paragraphs(
            "A town on the Orne that served William the Conqueror as his real "
            "capital, for its distance from Paris, and as the staging ground "
            "for his campaigns, the invasion of England among them. Caen "
            "Castle, begun in 1060, dominates it: some five hectares inside a "
            "high crenellated wall and dry moat, with a hall and keep of the "
            "1120s and new towers and an inner wall round the keep added by "
            "Philip II.",
            "In 1220 workmen are pulling down the old north gatehouse and "
            "tower and building new gates in the south and east walls; "
            "labourers, engineers and architects are always wanted. William's "
            "Men's Abbey and Matilda's Women's Abbey stand in the town.",
        ),
    )
    w["bayeux"] = b.town(
        "Bayeux",
        charter="Church",
        answers_to=normandy.world["bishop_of_bayeux"],
        place=p["bayeux_county"],
        summary="Once Baiocasses, chief town of the Gauls, taken by Rome in the "
        "first century BC. Fragments of Roman buildings still stand and "
        "much of the town is built of their stone; nothing Gallic remains, "
        "but the land remembers where it stood. In the duchy's early years "
        "it was the seat of rival Norse settlers who sometimes rose against "
        "Rouen; it is quiet now. Its mills serve the country round, and "
        "its cathedral keeps Odo's tapestry.",
        secrets="Rumour puts a regio somewhere in the town that held the small "
        "Diedne vassal covenant Baiocassium Minor; no living magus admits "
        "to knowing where.",
    )
    w["avranches"] = b.town(
        "Avranches",
        charter="Church",
        answers_to=normandy.world["bishop_of_avranches"],
        place=p["avranches_county"],
        summary=(
            "The seat of the diocese of Avranches, on the Couesnon near the "
            "Breton border, the town pilgrims pass through on the way to Mont "
            "St. Michel."
        ),
    )
    w["barfleur"] = b.town(
        "Barfleur",
        place=p["cotentin"],
        summary=(
            "A harbour town of the Cotentin whose shipyards built much of "
            "William the Conqueror's invasion fleet and have built warships "
            "and merchantmen ever since. Its waters are dangerous: in 1120 "
            "William, son of Henry I of England, drowned when his ship struck "
            "a rock leaving harbour. Sea ghosts haunt it, among them a "
            "spectral fleet that sails past in the worst winter storms, "
            "searching in vain for a berth."
        ),
    )
    w["cherbourg"] = b.town(
        "Cherbourg",
        place=p["cotentin"],
        summary=(
            "The town at the north of the Cotentin, south of which lies the "
            "Forest of Brix. The ruined covenant of Pagus stood near it, and "
            "the Rhine covenant Fengheld has a chapter house here that claims "
            "some of Pagus's vis sources, to Confluensis's displeasure."
        ),
    )
    small = (
        ("beauvoir", "Beauvoir", "a small forest community"),
        ("laigle", "Laigle", "a small forest community"),
        ("trun", "Trun", "a small forest community"),
        ("conches", "Conches", "little more than a village outside an abbey"),
        ("lyre", "Lyre", "little more than a village outside an abbey"),
        (
            "saint_evroult",
            "Saint-Evroult",
            "little more than a village outside an abbey",
        ),
        ("claville", "Claville", "really a large manor"),
    )
    for key, name, what in small:
        w[key] = b.town(
            name,
            charter="Commune",
            place=p["normandy"],
            summary=(
                f"A chartered Norman community, {what}. Its charter is one of "
                "the many King John sold before 1204, which Philip II has not "
                "confirmed; a covenant that leans on its magistrates would be "
                "exposed if it were revoked."
            ),
        )


# ------------------------------------------------------------------ people


def _people(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    w["white_ladies"] = b.faction(
        "The White Ladies",
        faction="Faerie court",
        decides="Its leader",
        realm="Faerie",
        place=normandy.places["white_ladies"],
        summary=(
            "Sidhe sisters, said to be kin of the Lady of the Lake, who rule "
            "faerie regiones about Bayeux and waylay men at bridges and fords "
            "to dance. Whoever brings the best partner to the spring equinox "
            "ball is foremost among them for a year."
        ),
        wants="Excellent mortal dance partners",
        offers="Rewards for a fine dancer; a place at the equinox ball",
    )
    w["bayeux_swine_court"] = b.faction(
        "The Swine Court of Bayeux",
        faction="Faerie court",
        realm="Faerie",
        place=normandy.places["bayeux_county"],
        summary=(
            "The woodland faeries who claim the half-wild pigs of the Bayeux "
            "forest as theirs. Wise villages honour them before the autumn cull; "
            "they still nurse the grudge of St Vigor's broken temple and plot "
            "against the Divine in the county."
        ),
        wants="Tribute before the cull; the Church's hold on Bayeux broken",
        offers="A peaceful cull",
    )


# --------------------------------------------------------------- Montverte


def _montverte(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "An Autumn covenant, one of the five great lieges of the Tribunal and "
        "among its oldest, ruled in secret by an inner council of five. Feared, "
        "hated and often reviled for its warlike ways, it all but invented "
        "Hermetic raiding, and the practice survives only because Montverte and "
        "its followers have the strength, martial and political, to keep it "
        "alive.",
        "Two Norse brothers, kin of Rollo, came with the Viking settlers: "
        "Harivald, a master of elemental magic who joined the Order through Ex "
        "Miscellanea and then founded a Flambeau line that endures, and his "
        "un-Gifted elder brother Haland. Together they seized an old "
        "Carolingian fort and raised a Norman keep on it; the covenant's "
        "founding was announced at Tribunal in 941, and Haland's heirs became "
        "the lords of Montverte. The magi soon dominated their hosts and used "
        "their soldiers for raids and extortion, at first on the quiet and then "
        "openly. In the Schism War the castle was a rallying point for martial "
        "Tremere and Flambeau, killed many of Normandy's Diedne, and gained "
        "great prestige. Raiding went on after the war until Koilios's brazen "
        "raid on Lapis Crudus's convoy in 1113 won it the shelter of a "
        "Tribunal precedent. Sanctions and scandals mark its history, and it is "
        "blamed for the fall of several covenants, but it has thrived.",
        "The covenant fills the castle on the green mount, a sprawling keep "
        "above terraced walls and hanging gardens in a Magic aura of 5. The "
        "pentagonal inner curtain has a square tower at each corner, one for "
        "each councillor. The central keep holds the library, the meeting "
        "rooms and the guest chambers, and on its top floor the council "
        "chamber, a dark, bare hall round the ancient council table.",
        "The magi live as guests of the Baron of Montverte and run his house "
        "from behind the scenes; they deal with the world through him, and "
        "other magi often question whether this is lawful. The magi say, "
        "truly, that they swear him no oath, and, less truly, that they let "
        "him rule alone. The covenfolk are the baron's household, and most "
        "servants and soldiers know nothing of the Order or that they live in "
        "a covenant.",
        "Geirlaug leads the council and only its five sit in it. A dead "
        "councillor is replaced, usually from the junior magi, sometimes from "
        "outside, such as a leading magus of a loyal vassal. The four to six "
        "junior magi (the troupe decides) owe seasons of work and suit "
        "Tremere, Flambeau, Bonisagus, Verditius and Jerbiton; a Redcap "
        "probably lives here. Montverte has usually held one to three vassals, "
        "tools of its mischief that enjoy a strong liege's protection; "
        "Atsingani is its vassal now. Raiding by it and its vassals has made "
        "it one of the richest covenants in the Tribunal, and its magi live "
        "in luxury.",
    )
    what_matters = joined_lines(
        "Vis: the book names no source; the covenant's wealth comes from raiding, its vassals and its stores, which Runild keeps",
        "Income: the baron's domain and village, and the spoils of raids by Montverte and its vassals; one of the wealthiest covenants in the Tribunal",
        "Library: in the central keep, overseen by Runild; contents not described",
        "Vassals: Atsingani (since 1187); in the past Nauche-Fleur (1072-1166), and usually one to three at a time",
        "Boon: a castle on a fortified hill with concentric walls, hanging gardens and a spring",
        "Boon: a mundane baron and his soldiers wholly under the covenant's control",
        "Boon: contacts in the Hanse Parisienne, who supply luxuries, and dealings with the eremite Anacrôn on raids against other covenants' town storehouses",
        "Hook: raiding sets much of the Tribunal against it; its magi are blamed for the fall of past covenants",
        "Hook: other magi question whether living through a mundane baron breaks the Code",
        "Tension: Geirlaug's near-irrational hatred of Oleron, over an insult from its leader decades ago, and her dislike of the other lieges",
        "Tension: Geirlaug's mind; she is seen only in the council mirror, and the others doubt her sanity in private",
        "Tension: the succession to the Praeco: Geirlaug is third eldest in the Tribunal, after Celeres and Somnifer",
        "Tension: the Lotharingian Tribunal movement, which would carve covenants away from Normandy",
    )
    hidden = joined_lines(
        "The inner council is largely dysfunctional: each councillor is very able alone, but they barely coordinate, and behind a polite show of deference to Geirlaug runs a quiet contest of wills.",
        "The baron's high chair carries an old Mentem enchantment that keeps its occupant compliant, and has left several barons slightly Warped.",
        "Through a Mirror, Darkly: Geirlaug's face in the mirror begins to show two personalities quarrelling; perhaps a demon has supplanted her and rules through her image. Only Thormod seems untroubled.",
        "Odin's Magus: Thormod is a leading member of the Children of Odin, practises Viking magic and uses his position for the cult; he may be kin or lover of its hierophant, Queen Skuld.",
        "The Pirate Covenant: the council has allied with Waddenzee, the pirate covenant of the Rhine; Waddenzee would join the Lotharingian secession and then declare itself Montverte's vassal in Normandy instead, crippling the new Tribunal and winning a Tribunal that tolerates its raids.",
    )
    montverte = b.covenant(
        "Montverte",
        tribunal=tribunal,
        founded=941,
        place=normandy.places["montverte_site"],
        summary=summary,
        what_matters=what_matters,
        secrets=hidden,
        aura=5,
        unnamed_magi=5,
        season="Autumn",
    )
    normandy.covenants["montverte"] = montverte
    _montverte_magi(normandy, b, montverte)
    b.book(
        montverte,
        "The library of Montverte",
        "Other",
        description=(
            "Kept in the central keep under the inner council, and overseen by "
            "Runild with the vis stores and the junior magi's donated seasons "
            "of labwork. The book does not list its contents; the covenant's "
            "great wealth and centuries of raiding suggest a large collection, "
            "and its vassals may copy from it under their oath."
        ),
    )


def _montverte_magi(normandy: Normandy, b: Builder, montverte: Covenant) -> None:
    m = normandy.magi
    m["geirlaug"] = b.magus(
        "Geirlaug",
        covenant=montverte,
        house=FLAMBEAU,
        age=150,
        summary=paragraphs(
            "Leader of Montverte for more than half a century, an archmaga of "
            "House Flambeau of the founder Harivald's line, plainly a supreme "
            "master of Ignem, and the third eldest magus of the Tribunal. Her "
            "age is uncertain (perhaps 150, apparently in her mid-sixties). "
            "Erratic and marked by long Twilights whose dates no one knows, "
            "she hardly ever leaves her tower and is said to have come to "
            "depend on fire: great flames are often seen inside it.",
            "She attends council only as an image in a great mirror at the "
            "head of the table, an elegant, stern old woman with blazing eyes, "
            "the flames behind her moving with her mood: lucid, cryptic, "
            "silent or absent. The others privately doubt her sanity, but she "
            "tolerates no defiance and the council does her will. She hates "
            "Oleron almost beyond reason for an insult from its old leader "
            "decades ago, and dislikes the other lieges.",
        ),
        traits={"Unpredictable": 4, "Reclusive": 3, "Vengeful": 2},
    )
    m["thormod"] = b.magus(
        "Thormod",
        covenant=montverte,
        house=FLAMBEAU,
        age=87,
        summary="Filius of Geirlaug and her opposite: meticulously neat, his "
        "feelings and plans always hidden (he looks 48). Thought to "
        "specialise in Perdo, though nothing is really known of his tastes. "
        "He never seems to doubt or falter, which makes him secretly the "
        "most hated and feared magus of Montverte. He is the covenant's "
        "Hermetic ambassador, coldly efficient, and directs its vassals. "
        "Alone on the council he seems quite untroubled by Geirlaug and "
        "trusts her rule completely; if anyone knows her true state, it is "
        "he, and he says nothing.",
        secrets="He is a leading member of the Children of Odin, practises Viking "
        "magic and bends his influence to the cult's ends; he may be "
        "related to its hierophant, Queen Skuld, by blood or by a tryst.",
        traits={"Scheming": 2, "Tidy": 2, "Emotional": -3},
    )
    m["eduardus"] = b.magus(
        "Eduardus",
        covenant=montverte,
        house=TYTALUS,
        age=67,
        summary=paragraphs(
            "Steward of the castle, trained in House Jerbiton and a Tytalus for "
            "some decades (he looks 43): cultured, artistic and Gently Gifted. "
            "As steward he wears the persona of Edward so constantly that no "
            "one can tell him from the real Eduardus, of whom little is known. "
            "His chief task is to manage the baron, and through him the "
            "covenant's dealings with the world; a trusted adviser of the "
            "family, he is often at the baron's side. He also keeps the castle "
            "running. Edward is sociable, smooth-tongued and a seducer, and "
            "the covenfolk women he has charmed bring him the gossip that keeps "
            "him informed.",
            "One of the few purple Fideli, who back Buliste as the true Prima "
            "of House Tytalus, and a follower of the Hippian school.",
        ),
        traits={"Persuasive": 3, "Charming": 2, "Lecherous": 2},
    )
    m["rotgiers"] = b.magus(
        "Rotgiers de Gerberoy",
        covenant=montverte,
        house=TREMERE,
        age=78,
        summary=paragraphs(
            "Senior Tremere of Montverte, in charge of its martial affairs: its "
            "defences, mundane and magical, and its raids, which he runs "
            "ruthlessly but with fair treatment of his victims. A huge, gruff, "
            "grey-bearded man who looks about fifty, he lives as a knight, and "
            "the baron counts him one; abroad he rides in mail with a jewelled "
            "mace and a great shield bearing Montverte's arms, at home he wears "
            "charcoal Tremere robes over a nobleman's finery. His familiar is "
            "Simo, an ancient warhorse. He holds the sigils of most of the "
            "Tribunal's few Tremere.",
            "A feared champion of the Tourney, above all in the joust and "
            "certamen: his lance strikes true through the usual Rego Terram "
            "defences, and he can conjure a lance of bone that ignores them. "
            "He is not above a little cheating, having servants gather an "
            "Arcane Connection to an opponent for use with a figurine, or "
            "quietly stripping a rival's protections with Wind of Mundane "
            "Silence.",
        ),
        traits={"Blunt": 3, "Honorable": 2, "Violent": 1},
    )
    m["runild"] = b.magus(
        "Runild",
        covenant=montverte,
        house=TREMERE,
        age=64,
        summary=(
            "The youngest councillor (she looks 43), quiet and unassuming "
            "beside the other four. She oversees the covenant's magical "
            "resources: its library, its vis stores and the seasons of labwork "
            "the junior magi must give. She has just finished training her "
            "first apprentice but has no voting sigil of her own yet. Her "
            "familiar, a black cat, is descended from Jerbiton's familiar, and "
            "she keeps company with all of Montverte's many cats."
        ),
        traits={"Oblivious to Mundanes": 3, "Catlike": 2, "Inquisitive": 1},
    )


# ------------------------------------------------------------------- stats


P = Profile

#: Each sketched magus's profile, by character id.
PROFILES: dict[str, Profile] = {
    "geirlaug": P(
        strong="int sta",
        weak="com",
        native="French",
        arts={"Ig": 8, "Cr": 5, "Re": 4, "Pe": 4, "Im": 3, "Vi": 3, "In": 2},
        abilities={
            "Concentration": (3, "Ignem"),
            "Leadership": (2, "council"),
            "Area Lore: Normandy": 2,
            "Magic Lore": (2, "Twilight"),
        },
        virtues=[
            vf_art("Affinity with {art}", "ignem"),
            vf_art("Puissant {art}", "ignem"),
            vf_focus("Major Magical Focus", "fire"),
            "Twilight Prone",
            "Hatred (Major)",
            "Reclusive",
            "Warped by Magic",
        ],
        reputations={"Archmaga (Hermetic)": 4, "Master of Ignem (Hermetic)": 4},
    ),
    "thormod": P(
        strong="int pre",
        weak="com",
        native="French",
        arts={"Pe": 6, "Ig": 4, "Me": 3, "Re": 3, "Co": 2, "Vi": 2},
        abilities={
            "Intrigue": (4, "Hermetic politics"),
            "Leadership": (2, "vassals"),
            "Folk Ken": (2, "magi"),
            "Living Language: West Norse": 2,
            "Code of Hermes": (3, "vassalage"),
        },
        virtues=[
            vf_art("Affinity with {art}", "perdo"),
            "Self-Confident",
            "Clear Thinker",
            "Dark Secret",
            "Secretive",
            "Ambitious (Minor)",
        ],
    ),
    "eduardus": P(
        strong="pre com",
        native="French",
        arts={"Me": 6, "Im": 4, "In": 3, "Re": 3, "Mu": 2},
        abilities={
            "Charm": (4, "women"),
            "Etiquette": (3, "nobles"),
            "Guile": (3, "keeping a persona"),
            "Folk Ken": (3, "covenfolk"),
            "Intrigue": (2, "the baron's court"),
            "Artes Liberales": (2, "music"),
        },
        virtues=[
            "Gentle Gift",
            vf_ability("Puissant {ability}", "guile"),
            "Lecherous (Minor)",
            "Dutybound",
            "Ambitious (Minor)",
            "Enemies",
        ],
    ),
    "runild": P(
        strong="int per",
        weak="pre",
        native="French",
        arts={"Vi": 5, "In": 4, "An": 3, "Re": 3, "Cr": 2},
        abilities={
            "Magic Theory": (5, "vis"),
            "Profession: Scribe": 2,
            "Animal Ken": (2, "cats"),
            "Teaching": (2, "apprentices"),
        },
        virtues=[
            "Book Learner",
            vf_art("Affinity with {art}", "vim"),
            "Clear Thinker",
            "Busybody",
            "Dutybound",
            "Weak-Willed",
        ],
    ),
}


def stats(normandy: Normandy) -> None:
    """Enter Rotgiers's printed stat block, then stat the other magi of
    the chapter from their profiles."""
    b = normandy.b
    _rotgiers(b, normandy.magi["rotgiers"])
    for key, profile in PROFILES.items():
        character = normandy.magi.get(key)
        if character is not None:
            apply(b, character, profile)


def _rotgiers(b: Builder, rotgiers: Character) -> None:
    b.stats(
        rotgiers,
        {
            "characteristics": {
                "intelligence": 2,
                "perception": -1,
                "presence": 1,
                "communication": 1,
                "strength": 2,
                "stamina": 2,
                "dexterity": 1,
                "quickness": -1,
            },
            "aging_points": {"perception": 1, "presence": 1, "strength": 2},
            "size": 1,
            "confidence": (2, 10),
            "decrepitude": (0, 4),
            "warping": (6, 25),
            "apparent_age": 52,
            "virtues_flaws": [
                "The Gift",
                "Hermetic Magus",
                "Gentle Gift",
                ("Affinity with {art}", {"art": "rego"}),
                ("Affinity with {art}", {"art": "terram"}),
                "Cautious Sorcerer",
                "Improved Characteristics",
                "Large",
                ("Minor Magical Focus", {"focus": "certamen"}),
                ("Puissant {ability}", {"ability": "single weapon"}),
                "Subtle Magic",
                "Feud",
                "Proud (Major)",
                ("Deficient Form", {"form": "imaginem"}),
                "Driven (Minor)",
                "Poor Hearing",
                "Susceptibility to Faerie Power",
            ],
            "traits": {"Blunt": 3, "Honorable": 2, "Violent": 1},
            "reputations": {
                "Tourney Champion (Hermetic)": 4,
                "Overbearing and Violent (Local)": 2,
            },
            "abilities": [
                ("Animal Handling", 1, "horses"),
                ("Artes Liberales", 3, "music"),
                ("Code of Hermes", 1, "acts of aggression"),
                ("Concentration", 3, "Rego"),
                ("Craft: Figurines", 2, "of magi"),
                ("Etiquette", 2, "nobility"),
                ("Finesse", 5, "certamen"),
                ("Living Language: French", 5, "Norman"),
                ("Hunt", 1, "mounted"),
                ("Intrigue", 2, "Hermetic"),
                ("Dead Language: Latin", 4, "Hermetic"),
                ("Leadership", 3, "battle"),
                ("Magic Theory", 5, "Rego"),
                ("Area Lore: Normandy", 2, "nobility"),
                ("Organization Lore: Order of Hermes", 2, "Tourney"),
                ("Parma Magica", 5, "Corpus"),
                ("Penetration", 5, "Terram"),
                ("Philosophiae", 1, "ritual magic"),
                ("Profession: Scribe", 2, "about Rego"),
                ("Ride", 3, "battle"),
                ("Single Weapon", 5, "heater shield"),
                ("Teaching", 2, "apprentices"),
            ],
            "arts": {
                "Creo": 10,
                "Intellego": 7,
                "Muto": 7,
                "Perdo": 17,
                "Rego": 24,
                "Animal": 11,
                "Aquam": 5,
                "Auram": 5,
                "Corpus": 13,
                "Herbam": 4,
                "Ignem": 5,
                "Imaginem": 5,
                "Mentem": 8,
                "Terram": 14,
                "Vim": 7,
            },
            "spells": [
                ("Piercing Lance of Bone", "CrAn", 20, 2),
                ("Soothe Pains of the Beast", "CrAn", 20, 0),
                ("The Wizard's Mount", "CrAn", 20, 1),
                ("Beast of Outlandish Size", "MuAn", 15, 0),
                ("Agony of the Beast", "PeAn", 15, 0),
                ("Commanding the Harnessed Beast", "ReAn", 30, 0),
                ("Purification of the Festering Wounds", "CrCo", 20, 0),
                ("Preternatural Growth and Shrinking", "MuCo", 15, 0),
                ("Gift of the Bear's Fortitude", "MuCo", 25, 0),
                ("Grip of the Choking Hand", "PeCo", 25, 0),
                ("Stance of the Firm-Buttocked Knight", "ReCo", 20, 0),
                ("The Leap of Homecoming", "ReCo", 30, 0),
                ("Posing the Silent Question", "InMe", 20, 1),
                ("Aura of Rightful Authority", "ReMe", 20, 1),
                ("Wall of Protecting Stone", "CrTe", 25, 0),
                ("Edge of the Razor", "MuTe", 20, 2),
                ("Crest of the Earth Wave", "ReTe", 20, 0),
                ("The Unerring Lance", "ReTe", 20, 0),
                ("The Earth Split Asunder", "ReTe", 30, 0),
                ("Demon's Eternal Oblivion", "PeVi", 20, 0),
                ("Wind of Mundane Silence", "PeVi", 25, 2),
                ("Maintaining the Demanding Spell", "ReVi", 30, 0),
            ],
            "masteries": {
                "Piercing Lance of Bone": ["Penetration", "Fast Casting"],
                "The Wizard's Mount": ["Multiple Casting"],
                "Posing the Silent Question": ["Quiet Casting"],
                "Aura of Rightful Authority": ["Quiet Casting"],
                "Edge of the Razor": ["Multiple Casting", "Quiet Casting"],
                "Wind of Mundane Silence": ["Penetration", "Quiet Casting"],
            },
            "notes": (
                "Single Weapon is 5, +2 from Puissant Single Weapon. Combat: "
                "mace and heater shield mounted Init -2, Attack +15, Defense "
                "+13, Damage +10 (on foot Attack +12, Defense +10); lance and "
                "heater shield mounted Init -1, Attack +16, Defense +13, Damage "
                "+7; Soak +11, before his items' bonuses. Equipment: full chain "
                "mail imbued with protective effects, a heater shield, a lance, "
                "and an ornate jewelled mace enchanted as his talisman; "
                "Encumbrance 2 (4). Familiar: Simo, an ancient warhorse. "
                "Twilight Scars: weak-willed people feel an unnatural fear of "
                "him, his old wounds bleed again when his magic tires him "
                "badly, metal he wears never rusts, and he cannot hear "
                "compliments."
            ),
        },
    )
