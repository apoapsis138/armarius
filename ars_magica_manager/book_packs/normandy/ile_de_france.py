"""The Ile de France, as of spring 1220, in paraphrase of chapter seven of
The Lion and the Lily: Paris and its quarters, the lands round the city
and the Loire country to the south, with their places and regiones; the
living covenants Eboris and Lapis Crudus with their magi, libraries and
vis; the eremite Anacrôn, King of the Beggars, with the stat block the
book prints; and the mundane world: King Philip, the University, the
Bishop of Paris, St. Denis and the other abbeys, the Templars, the towns
and the factions of the chapter.

The ruined covenant Caput Capra is tribunal.py's; the Cabal of the Golden
Coin is stories.py's. Every record is kept in the Normandy dicts under a
slug (the king is `world["king"]`, the region `places["ile_de_france"]`)
so the other parts can find it."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Normandy

# House ids, so a typo cannot slip into a record.
EX_MISC = "house_ex_miscellanea"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
MERINITA = "house_merinita"
TYTALUS = "house_tytalus"

# The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."

KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}

#: The arms of the King of France as the app can draw them: azure, three
#: fleurs-de-lis or (in 1220 the lilies were still strewn over the field).
ARMS_FRANCE = Arms("Azure", charge="Fleur-de-lis", charge_tincture="Or", count=3)
ARMS_TEMPLARS = Arms("Argent", charge="Cross", charge_tincture="Gules")


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _place(normandy: Normandy, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


def build(normandy: Normandy) -> None:
    tribunal = normandy.tribunal
    assert tribunal is not None
    _places(normandy)
    _crown(normandy)
    _church(normandy)
    _towns(normandy)
    _schools(normandy)
    _factions(normandy)
    _eboris(normandy, tribunal)
    _lapis_crudus(normandy, tribunal)
    _eremites(normandy)
    _links(normandy)


# ------------------------------------------------------------------ places


def _places(normandy: Normandy) -> None:
    region = _place(
        normandy,
        "ile_de_france",
        "The Ile de France",
        realm="Magic",
        summary=paragraphs(
            "The middle of the Normandy Tribunal and the heart of the French "
            "crown: the old Capetian demesne round Paris, ruled directly by "
            "the king through a mesh of small, loyal baronies whose lords "
            "fill his army, his council and his offices of provost and "
            "bailiff. Hugh Capet was chosen king at Senlis in 987, and the "
            "court, once forever on the road, has now settled for good in "
            "Paris. Merovingian gifts made the Church a great landholder "
            "here; the royal abbeys cleared the wild land and pray for the "
            "kings, and the new cathedrals of St. Denis, Sens and Chartres "
            "have launched a building style that is spreading across "
            "France.",
            "Most of the land is gentle, fertile farmland, among the richest "
            "in Europe, and only Flanders is more thickly peopled. The Seine "
            "and the Loire cross it from south-east to north-west. The forest "
            "of Cuise (Flanders and Picardy's) closes the north-east; south "
            "of Paris lie the forests of Yvelines and Fontainebleau, and "
            "below Orléans the marshy heath of the Sologne runs to Anjou. "
            "About a day out from Paris a ring of large towns stands on the "
            "radiating roads and along the Seine. South of the forests, the "
            "Loire valley holds the king's southernmost lands, two "
            "archbishops' sees and a handful of ancient schools.",
            "Living covenants: Eboris in Paris and Lapis Crudus in the forest "
            "of Fontainebleau. The ruins of Caput Capra lie on the Loire near "
            "Fleury.",
        ),
        **KNOWN_ORDER,
    )
    _paris(normandy, region)
    _fontainebleau(normandy, region)
    _place(
        normandy,
        "st_cloud_bridge",
        "The Bridge of St. Cloud",
        inside=region,
        aura=2,
        summary=paragraphs(
            "An old timber bridge over the Seine at St. Cloud, six miles "
            "below Paris, many times patched and guarded by a tall wooden "
            "tower at either end. Here the Merovingian prince Clodoald cut "
            "off the long hair that marked his royal blood and swam the "
            "river to escape his uncles. Legend says that any king who "
            "steps onto the bridge falls dead; nobody knows whether it is "
            "true, and French kings take no chances, crossing here by boat. "
            "The curse may bind a faerie king as surely as a mortal one. "
            "Magic aura 2.",
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "yvelines",
        "The Forest of Yvelines",
        inside=region,
        realm="Magic",
        summary=(
            "One of the sizeable forests south-west of Paris, at the centre "
            "of the realm, which with Fontainebleau marks the edge of the "
            "lands round the city and the start of the southern Ile de "
            "France. The book says little more of it."
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "sologne",
        "The Sologne",
        inside=region,
        realm="Magic",
        summary=(
            "A marshy forest of heath south of Orléans, on the border with "
            "Anjou, the last of the Ile de France's great woods before the "
            "Plantagenet lands."
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "chartres_well",
        "The Old Well of Chartres",
        inside=region,
        realm="Divine",
        summary=paragraphs(
            "An ancient well on a low hill above the Eure, beside which the "
            "cathedral of Chartres now stands. It has been holy in turn to "
            "the druids, to a Roman mother goddess and, once missionaries "
            "read the goddess as the Virgin, to Mary; that devotion is why "
            "Charlemagne gave Chartres the Sainte-Chemise. When the Vikings "
            "sacked the town in 858 they threw the bodies of martyrs down "
            "the well. Its aura is not given; the cathedral's crypt beside "
            "it is the largest in France.",
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "fleury_grove",
        "The Druids' Grove at Fleury",
        inside=region,
        realm="Magic",
        summary=paragraphs(
            "The ancient sacred grove beside the Loire, twenty miles above "
            "Orléans, where all the druids of Gaul once met each year, near "
            "the old heart of the Carnutes' land. Benedictines from Orléans "
            "founded the abbey of Fleury beside it in the seventh century, "
            "and St. Benedict's relics now draw pilgrims in their "
            "thousands. Its aura is not given.",
            "The Diedne covenant Caput Capra was founded nearby in 981 to "
            "guard the site through the lawless late tenth century, and was "
            "the first of Normandy's Diedne covenants to fall, in 1005.",
        ),
        **KNOWN_TRIBUNAL,
    )


def _paris(normandy: Normandy, region: Neighbour) -> None:
    _place(
        normandy,
        "ile_de_la_cite",
        "The Île de la Cité",
        inside=region,
        realm="Divine",
        summary=secrets(
            paragraphs(
                "The mile-long island in the Seine where the Parisii first "
                "settled: the oldest quarter of Paris and its ecclesiastical "
                "and administrative centre, a stifling maze of ancient "
                "timber houses round the grandest churches. Notre-Dame rises "
                "at the island's upstream end over the ruins of a "
                "Gallo-Roman temple: begun in 1163, its chancel consecrated "
                "in 1182 and its nave nearly done, it will be the greatest "
                "church in the West when finished. The stone Petit Pont of "
                "1186 joins the island to the left bank, and two longer "
                "stone bridges cross the broader channel to the right.",
                "The Seine is too shallow for sea-going ships, so there are "
                "no great docks, only busy small river craft; most "
                "long-distance goods travel by the road north to Rouen. Some "
                "parts of Paris have a high Divine aura (not given in "
                "numbers).",
            ),
            "Infernal auras lurk in the city's worst quarters, unmapped by the book.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        normandy,
        "paris_islets",
        "The Wooded Islets above the Cité",
        inside=region,
        realm="Magic",
        summary=(
            "A couple of small, mostly empty islands a stone's throw "
            "upstream of the Île de la Cité, thick with copses of trees. "
            "Parisians think them places of ill repute; the book does not "
            "say why."
        ),
        **RUMOURED,
    )
    _place(
        normandy,
        "left_bank",
        "The Left Bank of Paris",
        inside=region,
        realm="Divine",
        summary=paragraphs(
            "The south bank, centre of Roman Lutetia and now the city's "
            "scholarly quarter, where the cathedral and abbey schools have "
            "lately been recognised as a university. Its outer parts are "
            "less crowded, a string of village-like settlements with green "
            "ground between. Little of Rome survives: the forum and baths "
            "are built over and a Roman cemetery just south of the walls is "
            "buried and overgrown, but the amphitheatre of Lutetia still "
            "stands to the south-east. The abbey church of St. Geneviève "
            "crowns a prominent hill, and a little west of it is the abbey "
            "church of St. Germanus where most Merovingian kings lie.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        normandy,
        "right_bank",
        "The Right Bank of Paris (Le Marais)",
        inside=region,
        realm="Divine",
        summary=paragraphs(
            "The newest, largest and busiest quarter, home to about half of "
            "Paris and its commercial heart. It is called the Marais, the "
            "marsh, because it was swamp until the Capetians drained it and "
            "took much of it for themselves. Philip II enlarged and roofed "
            "the great market of Les Halles in 1183, and merchants come to "
            "it from far away; the Hanse Parisienne, the city's chief "
            "merchant league, wields great influence here. Just outside the "
            "walls to the west stands the Louvre, the king's tall square "
            "fortress of 1190, holding his residence, treasury and arsenal, "
            "with royal gardens and estates beyond. The Templars' great "
            "temple and treasury is also in Paris.",
            "Philip's walls and moats enclose both banks in two half-circles, "
            "three miles north to south and two east to west, and perhaps a "
            "third of each bank's people live outside them in large villages "
            "and towns. Paris is less a single city than a dozen towns grown "
            "into one, broken by walls, moats and channels and stitched "
            "together by gates and bridges, beneath a forest of spires and "
            "a haze of smoke.",
        ),
        **KNOWN_ORDER,
    )
    _place(
        normandy,
        "montmartre",
        "Montmartre",
        inside=region,
        realm="Divine",
        summary=secrets(
            paragraphs(
                "The Mount of Martyrs, a hill a little over a mile north of "
                "the walls, named for the martyrdom of St. Denis there. It "
                "was once Mons Mercurius and carried a Roman temple; a new "
                "abbey now stands on its slopes.",
            ),
            "In the saga frame of the Boar King, the faerie courtier "
            "Salvirius asks a magus to carry a message to the Hill of "
            "Martyrs at an exact day and hour.",
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "eboris_site",
        "The House of the Ivory Carvers",
        inside=region,
        realm="Magic",
        aura=0,
        summary=paragraphs(
            "Mathieus's great house on the Rue de la Tabletterie in a poor "
            "quarter of Paris: once a pilgrims' hostel, now three storeys "
            "over many levels of cellar, the office of an ivory-carving "
            "business, refronted in a style the local nobles sneer at as "
            "new money. It is the covenant of Eboris.",
            "In its basement is a lacuna, a space with no aura at all, not "
            "even the Dominion's, which probably helped Mathieus choose it. "
            "The house is grand for its street, and its owner quietly holds "
            "shares in at least thirty taverns, breweries, brothels and "
            "other businesses round about.",
        ),
        **KNOWN_TRIBUNAL,
    )


def _fontainebleau(normandy: Normandy, region: Neighbour) -> None:
    forest = _place(
        normandy,
        "fontainebleau",
        "The Forest of Fontainebleau",
        inside=region,
        realm="Faerie",
        summary=secrets(
            paragraphs(
                "A rocky, varied wild about twenty miles across, on the "
                "Seine's left bank some thirty miles south of Paris: "
                "parallel sandstone ridges among limestone, a dry country "
                "of hillocks, small gorges and old druid groves. Most of it "
                "is open woodland rich in game, hunted now and then from a "
                "few lodges; a tiny hermitage is the only settlement, though "
                "Parisian criminals are said to hide here. Its wettest part "
                "is a moor of ponds and clefts. Another part is a barren "
                "waste strewn with oddly shaped boulders, some of which look "
                "like beasts or even people; these stones can be harvested "
                "for Animal and Corpus vis (amount and tenure not given).",
                "At the forest's western end the bare sandstone massif of "
                "Les Trois Pignons hides the covenant of Lapis Crudus, and "
                "in the forest's middle lies the faerie regio of the "
                "Fountain of Fair Waters. The faerie Candidus dwells "
                "somewhere in the forest: a short man with chalk-white skin "
                "and hair, no eyes or sockets at all (yet he is not blind), "
                "dressed in dark blue, who grows in power by striking "
                "bargains with mortals and always asks a strange price.",
            ),
            "The man-shaped boulders may be hunters and hounds who pressed "
            "their chase into the nymph's domain and were cursed for it.",
        ),
        **KNOWN_REGION,
    )
    _place(
        normandy,
        "fountain_of_fair_waters",
        "The Fountain of Fair Waters",
        inside=forest,
        realm="Faerie",
        status="Rumoured",
        known="Locally",
        levels=[
            Builder.level(
                "Fontaine-Belle-Eau",
                6,
                "Faerie",
                enter="Rarely stumbled into; keen-nosed hounds sometimes find it by chance",
                notes=(
                    "The spring that names the forest, kept by a lovely "
                    "nymph whom the ancients took for Diana, with a gentle "
                    "white stag at her side and tame forest beasts, often "
                    "boar, all about. Hounds and owners who come humbly may "
                    "be tolerated or even rewarded; those who keep up the "
                    "hunt are likely cursed and may never leave."
                ),
            ),
        ],
        summary=(
            "A Faerie regio at the heart of the forest of Fontainebleau, "
            "about the spring of Fontaine-Belle-Eau, with a Faerie aura of 6 "
            "within. The stone figures in the surrounding waste may be its "
            "work, and they yield Animal and Corpus vis."
        ),
    )
    _place(
        normandy,
        "lapis_crudus_site",
        "Les Trois Pignons",
        inside=forest,
        realm="Faerie",
        tethers="Candidus's pact with the covenant",
        levels=[
            Builder.level(
                "The star valley of Lapis Crudus",
                7,
                "Faerie",
                see="Through the enchanted mirror in the shack that straddles the boundary",
                enter=(
                    "Only by the mirror: two people of comparable social "
                    "standing walk toward it from either side and change "
                    "places, each carrying what he can"
                ),
                notes=(
                    "The covenant itself: a dozen sandstone buildings in a "
                    "star of deep valleys, lit directly only at noon. Each "
                    "arm holds a magus's sanctum and the hub the covenfolk's "
                    "quarters; the Bleeding Stone lies in a cavern under the "
                    "council chamber, and Herbam-rich vines hang down the "
                    "cliffs."
                ),
            ),
        ],
        summary=paragraphs(
            "A barren sandstone massif at the western end of the forest of "
            "Fontainebleau, cut by deep dry valleys that meet in star "
            "shapes among the boulders. In the middle of one such star, "
            "inside a Faerie regio, sits the covenant of Lapis Crudus. From "
            "outside all that shows is a few rough huts of apparent outlaws, "
            "who are really the covenant's grogs; one hut straddles the "
            "regio's edge and holds the mirror through which people pass. "
            "The surface aura is not given.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------------- crown


def _crown(normandy: Normandy) -> None:
    b, w = normandy.b, normandy.world
    region = normandy.places["ile_de_france"]
    w["king"] = b.lord(
        "King Philip II Augustus",
        title="duke",
        wealth="Wealthy",
        seat="Paris (the Louvre)",
        ruler="Philip II Augustus, King of France",
        place=normandy.places["right_bank"],
        arms=ARMS_FRANCE,
        summary=paragraphs(
            "King of France, of the Capetian house, and the greatest "
            "power in the Tribunal. (He is entered as a duke because the "
            "app's titles stop there.) He rules the old royal demesne of "
            "the Ile de France directly, through loyal petty barons who "
            "supply his army, his advisers and the provosts and bailiffs "
            "who run his estates, and he has held Normandy since 1204. "
            "His court no longer wanders: it has settled in Paris, and the "
            "great nobles of France and of some small neighbouring states "
            "have built palaces there to be near him.",
            "Much of Paris is his work: its walls and moats, the Louvre "
            "(1190), the roofed market of Les Halles (1183), paved streets, "
            "and the progress of Notre-Dame. He finished the vast walls and "
            "Great Tower of Bourges in 1190, his one stronghold south of "
            "the Loire, and chartered the University of Paris in 1200. In "
            "1214 he won the battle of Bouvines in Flanders under the "
            "Oriflamme and took Count Ferdinand of Flanders prisoner.",
            "Kings of France never set foot on the bridge of St. Cloud. "
            "Magical war under the noses of the king and the abbey of St. "
            "Denis is a crime few magi would risk, and the Tribunal treats "
            "any meddling with the potentates of Paris as a grave matter.",
        ),
    )
    w["royal_barons"] = b.lord(
        "Barons of the Royal Demesne",
        title="baron",
        place=region,
        answers_to=w["king"],
        summary=(
            "The many small baronies of the Ile de France, wholly loyal to "
            "the king: they raise much of the royal army, sit on his "
            "council and serve as the provosts and bailiffs who manage his "
            "estates when he is away. They are a sketch for the many minor "
            "lords a saga may need round Paris."
        ),
    )


# ------------------------------------------------------------------ church


def _church(normandy: Normandy) -> None:
    b, w, p = normandy.b, normandy.world, normandy.places
    region = p["ile_de_france"]
    w["archbishop_of_sens"] = b.church(
        "Archbishop of Sens",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=region,
        summary=paragraphs(
            "Metropolitan over most of the sees of the Ile de France, Paris "
            "among them, and several in Champagne and Burgundy. His "
            "cathedral of St. Étienne, begun in the 1130s and now mostly "
            "complete, was the second church built in the new French style "
            "after St. Denis, and other builders have copied it, William of "
            "Sens among them at Canterbury. A rich episcopal palace and "
            "treasury hold many relics, including the alb of St. Thomas "
            "Becket.",
        ),
    )
    w["bishop_of_paris"] = b.church(
        "Bishop of Paris (Notre-Dame)",
        church="Bishop's cathedral",
        order="secular clergy",
        place=p["ile_de_la_cite"],
        answers_to=w["archbishop_of_sens"],
        founded=1163,
        summary=paragraphs(
            "The bishop of the greatest city in the North, whose new "
            "cathedral of Notre-Dame rises at the upstream end of the Île "
            "de la Cité on the site of a Gallo-Roman temple: begun in 1163, "
            "its chancel consecrated in 1182, its nave all but finished, "
            "and much still to build. The bishops also hold the town of "
            "St. Cloud. The book does not name the present bishop.",
            "In the last century the canon Fulbert, uncle of Héloïse, served "
            "this cathedral; his revenge on Peter Abélard is still a "
            "Parisian scandal.",
        ),
    )
    w["st_denis"] = b.church(
        "Abbey of St. Denis",
        church="Monastery or nunnery",
        order="Benedictine",
        place=region,
        answers_to=w["king"],
        summary=secrets(
            paragraphs(
                "The great royal abbey six miles north of Paris (twice that "
                "by the winding river), built over the grave of St. Denis, "
                "martyr and patron of France. Dagobert I founded it in the "
                "seventh century and Pepin the Short enlarged it; nearly "
                "every French king since the seventh century lies in its "
                "crypt, with Clovis and his son Childebert. Its most famous "
                "abbot, Suger, schoolfellow and confidant of Louis VII, "
                "became abbot in 1122 and ruled the kingdom justly as regent "
                "during the Second Crusade, earning the name father of the "
                "land.",
                "Suger's basilica of the 1130s, built after his vision of "
                "the heavenly Bethlehem, is the first church in the new "
                "French style: soaring pointed arches and slender columns "
                "that make room for stained glass on a scale never seen "
                "before. A great spire was recently added to one tower. "
                "Peter Abélard was a monk here late in life.",
                "Its greatest treasure is the Oriflamme, the flame-coloured "
                "royal banner taken by Clovis from Syagrius at Soissons and "
                "later carried by Charlemagne. It may fly only in the king's "
                "presence, at the head of his army on a lance; it heartens "
                "and strengthens his troops and seems to overrule any other "
                "supernatural effect nearby. It flew last at Bouvines in "
                "1214. Magi cannot tell whether it is Divine or Magical, and "
                "none admits to having tried his powers against it.",
            ),
            "The Oriflamme's true nature is left open by the book; a "
            "storyguide may decide.",
        ),
    )
    w["st_genevieve"] = b.church(
        "Abbey of St. Geneviève",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["left_bank"],
        answers_to=w["bishop_of_paris"],
        summary=(
            "The abbey church on its hill on the left bank, dedicated to "
            "Paris's patron. Geneviève, a pious peasant girl, turned Attila "
            "away from the city with her prayers in 451 and later broke "
            "Childeric's siege by bringing food in by boat; she died in 512 "
            "and many miracles followed. The book places her tomb in the "
            "Benedictine church of St. Peter and St. Paul that Clovis "
            "founded, which this record also stands for."
        ),
    )
    w["st_germanus"] = b.church(
        "Abbey of St. Germanus",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["left_bank"],
        answers_to=w["bishop_of_paris"],
        summary=(
            "An abbey church a short way west of St. Geneviève on the left "
            "bank, the burial place of most of the Merovingian kings; "
            "Clovis, notably, is not among them."
        ),
    )
    w["montmartre_abbey"] = b.church(
        "Abbey of Montmartre",
        church="Monastery or nunnery",
        place=p["montmartre"],
        answers_to=w["bishop_of_paris"],
        summary=(
            "A new abbey on the slopes of Montmartre, where St. Denis was "
            "martyred and where a Roman temple to Mercury once stood."
        ),
    )
    w["argenteuil"] = b.church(
        "Nunnery of Argenteuil",
        church="Monastery or nunnery",
        place=region,
        summary=(
            "A convent near Paris, where Peter Abélard sent his secret wife "
            "Héloïse to spare her the strain of their hidden marriage. "
            "Fulbert took her departure for desertion and had Abélard "
            "castrated, after which both took vows."
        ),
    )
    w["templars"] = b.church(
        "The Temple of Paris (Knights Templar)",
        church="Monastery or nunnery",
        order="Knights Templar (military order)",
        place=p["right_bank"],
        arms=ARMS_TEMPLARS,
        summary=paragraphs(
            "The Templars' great house in Paris and its immensely rich "
            "treasury, which works as a bank. It began by sparing pilgrims "
            "to the Holy Land the danger of carrying coin: a pilgrim pays "
            "the whole cost of his journey into a local commandery and "
            "takes a coded parchment receipt, draws credit at Templar "
            "houses on the way, and can withdraw at the Order's other great "
            "treasury in Jerusalem.",
            "The service now reaches far past pilgrims. The Order takes "
            "deposits and moves money for merchants, nobles, kings and the "
            "Church, and it lends, getting round the ban on usury by "
            "charging rents on the money borrowed. With the fortune this has "
            "built, the Templars pay for wars, crusades, trading ventures "
            "and great buildings.",
            "A covenant short of money may get a very large loan here. "
            "Missed payments, or magic the knights notice, will make a "
            "powerful enemy that is quick to stir up trouble at court or "
            "with arms.",
        ),
    )
    w["chartres_cathedral"] = b.church(
        "Cathedral of Chartres",
        church="Bishop's cathedral",
        order="secular clergy",
        place=p["chartres_well"],
        answers_to=w["archbishop_of_sens"],
        summary=paragraphs(
            "The cathedral of Our Lady on the hilltop beside the old well, "
            "keeper of the Sainte-Chemise, the tunic the Virgin wore at "
            "Christ's birth, given by Charlemagne. Lightning started the "
            "Great Fire of 1194, which burned most of the town and nearly "
            "all the church (fires had also ravaged the town in 1020 and "
            "1134); only one great steeple survived. Three days later "
            "priests were found shut safe in the treasury with the relic, "
            "and a papal legate called it a miracle and a sign to build "
            "greater.",
            "Gifts poured in from afar and the townsfolk hauled stone from "
            "the quarry themselves; in 1220 the vast new nave, modelled on "
            "St. Denis, is just finished, and a still greater steeple is "
            "planned. Its crypt is the largest in France. On the four great "
            "feasts of the Virgin the streets about it become a fair packed "
            "with pilgrims come to see the relic.",
        ),
    )
    w["fleury"] = b.church(
        "Abbey of Fleury (St. Benedict)",
        church="Monastery or nunnery",
        order="Benedictine",
        place=p["fleury_grove"],
        founded=650,
        summary=paragraphs(
            "The Benedictine abbey on the Loire twenty miles upriver of "
            "Orléans, founded in the mid seventh century beside the druids' "
            "grove, which soon received the relics of St. Benedict from "
            "Monte Cassino. Their many healing miracles bring pilgrims in "
            "thousands. The lofty white-stone basilica of St. Benedict, in "
            "the older style, was finished in 1218 after a century and a "
            "half and keeps his shrine in its crypt.",
            "Theodulf, the Goth poet-scholar of Charlemagne's circle and "
            "bishop of Orléans, founded its school, famous for its "
            "manuscripts; he fell from favour after Charlemagne died, and "
            "Vikings later raided the abbey. Abbot Abbo, confidant of "
            "Robert II, restored it in the late tenth century and enlarged "
            "its library.",
            "Its library holds the History of the Franks written here by "
            "the monk Aimon in Abbo's day (not Gregory of Tours's older "
            "work), now treated as the semi-legendary official chronicle "
            "of the Capetians. It is a single book that serves as three "
            "summae: Organization Lore: French Royalty, level 3, quality 9; "
            "Area Lore: Ile de France, level 2, quality 9; and Divine Lore, "
            "level 3, quality 9.",
        ),
    )
    w["archbishop_of_bourges"] = b.church(
        "Archbishop of Bourges",
        church="Archbishop's cathedral",
        order="secular clergy",
        place=region,
        summary=paragraphs(
            "Primate over much of Aquitaine, seated in the king's fortress "
            "city of Bourges. The cathedral, begun in the new style in 1195 "
            "under Archbishop Henry de Sully, is meant to proclaim the "
            "might of the Capetians and the archbishops alike. Work slowed "
            "when his successor William de Donjon died in 1209, but "
            "William was made a saint in 1218, and the pilgrims and gifts "
            "that followed have set the building going again at speed.",
        ),
    )


# ------------------------------------------------------------------- towns


def _towns(normandy: Normandy) -> None:
    b, w, p = normandy.b, normandy.world, normandy.places
    region = p["ile_de_france"]
    w["paris"] = b.town(
        "Paris",
        population=50000,
        ruler="The King of France",
        answers_to=w["king"],
        place=region,
        summary=secrets(
            paragraphs(
                "The largest city of northern Europe, with more than fifty "
                "thousand people, built where the Seine is crossed at an "
                "island: royal capital, seat of churchmen and scholars, and "
                "a market town. The right bank holds about half the people; "
                "the Cité and the left bank share the rest. Many Parisians "
                "are serfs who farm the king's rich fields for miles about, "
                "so Paris is no city of industry like Ghent, though it has a "
                "vast trading quarter and every craft. Since the court and "
                "the university came, it teems with rich young men who fear "
                "no officer of the law; by night the city boils with lust "
                "and brawling, by day it trades and argues philosophy.",
                "It is a melting pot of greed, heresy, petty crime, vice and "
                "sickness, with every pleasure and luxury for sale. The "
                "Brethren of the Free Spirit hold secret masses all over "
                "town, and the King of the Beggars rules its underworld. "
                "Writers accuse Parisians of idolatry and sorcery, mostly "
                "without cause: most are more or less devout.",
                "History: the Parisii fished here first; Roman Lutetia grew "
                "on the left bank and declined from the late third century. "
                "Geneviève's prayers turned Attila away in 451. The city "
                "burned at the end of the sixth century; Vikings sacked it "
                "in 845 and had to be bought off, and in 885 a far greater "
                "Viking host besieged it for ten months until Count Odo "
                "broke the siege. Peace came in 911, and in 987 Hugh Capet, "
                "elected king, made Paris his capital; it has thrived ever "
                "since.",
                "Hermetic: Eboris is the senex of Paris under the ruling of "
                "1200, so proxy wars between covenants' masks here are now "
                "illegal, and Eboris may pursue the sponsors of masks it can "
                "identify. Many covenants keep agents in the city: "
                "Confluensis among the Seine shippers and the law faculty, "
                "Fudarus through many independent agents, Montverte in the "
                "Hanse Parisienne. Folk magicians whose Gifts the Order "
                "missed are hidden among the crowds, and Parisian magi must "
                "buy them, warn them off, or kill them.",
            ),
            "Hidden Infernal auras fester in the seediest parts of the city.",
        ),
    )
    w["st_denis_town"] = b.town(
        "St. Denis",
        ruler="The Abbot of St. Denis",
        answers_to=w["king"],
        place=region,
        summary=(
            "A rich royal town about six miles north of Paris on an old "
            "Roman site, where the Paris-to-Beauvais road passes a wide bend "
            "of the Seine, grown up round the abbey. Each October the "
            "abbey's Lendit fair, begun in 1109 to raise money, fills the "
            "fields outside town with hundreds of stalls and draws "
            "merchants from abroad; parchment and writing materials are its "
            "speciality, bought up by the university's agents."
        ),
    )
    w["st_cloud"] = b.town(
        "St. Cloud",
        ruler="The Bishop of Paris",
        answers_to=w["bishop_of_paris"],
        place=region,
        summary=(
            "A small town on the Seine six miles below Paris, once called "
            "Nogent. Clodoald, grandson of Clovis, fled here in the sixth "
            "century after his father Clodomir fell in battle and his "
            "brothers were murdered; he cut off his royal hair to escape "
            "their fate, founded a monastery and was its abbot until his "
            "death in 560. His tomb drew pilgrims and the town took his "
            "name. It now belongs to the bishops of Paris; its old bridge "
            "is cursed for kings."
        ),
    )
    w["chartres"] = b.town(
        "Chartres",
        place=p["chartres_well"],
        summary=(
            "A town on the Eure in the rich plain of the Beauce, named for "
            "the Carnutes; the counts of Champagne hold the land. Burned in "
            "1020, 1134 and 1194 and sacked by Vikings in 858, it lives "
            "largely on the pilgrims and the four fairs held on the "
            "Virgin's feasts round its cathedral and relic."
        ),
    )
    w["sens"] = b.town(
        "Sens",
        ruler="The Archbishop of Sens",
        answers_to=w["archbishop_of_sens"],
        place=region,
        summary=(
            "Named for the Gaulish Senones and capital of Roman Senonia, "
            "Sens stands mostly on the right bank of the Yonne beside an "
            "island, inside old ramparts and a moat. It is above all the "
            "seat of the archbishop, with his cathedral of St. Étienne, "
            "palace and treasury."
        ),
    )
    w["orleans"] = b.town(
        "Orléans",
        answers_to=w["king"],
        place=region,
        summary=(
            "A town on the Loire at what was once the centre of Gaul and "
            "the Carnutes' country, near the druids' yearly meeting place "
            "at Fleury. The Romans named it Aurelianum. In 451 a Visigothic "
            "and Roman army lifted Attila's siege at the last moment, and "
            "early in the sixth century it was the capital of Clodomir's "
            "Merovingian kingdom of Burgundy. Its cathedral school is its "
            "glory."
        ),
    )
    w["bourges"] = b.town(
        "Bourges",
        ruler="The King of France",
        answers_to=w["king"],
        place=region,
        summary=paragraphs(
            "A heavily fortified city at the southern tip of the Ile de "
            "France, seat of an archbishop with primacy over much of "
            "Aquitaine. The count of Bourges sold it to Philip I in 1100 to "
            "pay for his crusade. When Henry II married Eleanor of "
            "Aquitaine, Bourges became the crown's only domain south of the "
            "Loire, so the kings spent thirty years walling it, a work "
            "Philip II finished in 1190: a great stone wall with earthworks "
            "and a moat round the whole city, fortified bridges, and in the "
            "southern wall the Great Tower, a moated keep that served as "
            "the model for the Louvre. It is a plain warning to the duke of "
            "Aquitaine, King Henry III of England.",
            "With pilgrims flocking to the tomb of St. William and money "
            "flowing to the cathedral, its population is growing fast.",
        ),
    )


# ----------------------------------------------------------------- schools


def _schools(normandy: Normandy) -> None:
    b, w, p = normandy.b, normandy.world, normandy.places
    w["university_of_paris"] = b.university(
        "University of Paris",
        school="University",
        place=p["left_bank"],
        answers_to=w["king"],
        summary=paragraphs(
            "The cathedral and abbey schools of the left bank, lately "
            "raised to a university; the king chartered it in 1200. Its "
            "students are mostly rich young men whose connections put them "
            "beyond the reach of the watch, and Paris's nights show it. In "
            "1219 Pope Honorius III banned the teaching of law in Paris, "
            "sending a wave of students to Orléans. The heresy of the "
            "Brethren of the Free Spirit began among its theologians. "
            "Mathieus chose his poor quarter partly to keep away from the "
            "university's fools; some of the law faculty keep in touch with "
            "Confluensis.",
            "Its most famous master was Peter Abélard, the brilliant and "
            "quarrelsome philosopher born at Le Pallet in Brittany in 1079, "
            "who studied at Chartres and came to Paris in 1118. Hired to "
            "tutor Héloïse, niece of the canon Fulbert, he fell in love "
            "with her; she bore a son, Astralabe, and they married in "
            "secret. Fulbert had him castrated and both took vows. Abélard "
            "fled to St-Gildas-de-Rhuys in Brittany, where the monks tried "
            "to poison him and he escaped by a secret passage in 1132; he "
            "later became a monk of St. Denis and died at Cluny.",
        ),
    )
    w["orleans_school"] = b.university(
        "Cathedral School of Orléans",
        school="Cathedral school",
        place=p["ile_de_france"],
        answers_to=w["orleans"],
        summary=(
            "One of the oldest schools of the West. Burgundian kings sent "
            "their sons here in the sixth century, Bishop Theodulf built it "
            "up in the eighth, and the eldest sons of both Charlemagne and "
            "Hugh Capet studied here, with students from across Christendom "
            "since. The papal ban of 1219 on teaching law in Paris has "
            "brought a new flood of law students. In history it becomes a "
            "university in 1235."
        ),
    )


# ---------------------------------------------------------------- factions


def _factions(normandy: Normandy) -> None:
    b, w, p = normandy.b, normandy.world, normandy.places
    w["hanse_parisienne"] = b.faction(
        "The Hanse Parisienne",
        faction="Gild",
        decides="A council",
        place=p["right_bank"],
        wants="Trade, privilege and the custom of the rich.",
        offers="Luxuries of every kind, and influence in the city.",
        summary=(
            "The chief league of Paris's merchants, powerful in the city "
            "and in its great market of Les Halles. Montverte has several "
            "contacts among them, who do well supplying those rich magi "
            "with luxuries."
        ),
    )
    w["beggars"] = b.faction(
        "The Court of the King of the Beggars",
        faction="Other",
        decides="Its leader",
        ruler="Anacrôn, the Grand Coësre",
        place=p["ile_de_la_cite"],
        rules=(
            "The king takes a share of every subject's takings; the cagoux "
            "collect it, enforce his edicts and drive interlopers from his "
            "pitches; the archisuppôts teach his law and train apprentices. "
            "Each court of argotiers is licensed for one trick and kept "
            "small so as not to glut the market."
        ),
        wants="Every good begging pitch in Paris, and freedom from the watch.",
        offers="Thieves, spies and hired hands for any job, and every rumour in Paris, for coin or vis.",
        summary=secrets(
            paragraphs(
                "A great gang of beggars, cutpurses and burglars that "
                "dominates, though it does not wholly own, the Paris "
                "underworld. Its king, also called the Grand Coësre, is "
                "rumoured to pay the city's officials to look away. Under "
                "him the cagoux, master thieves, act as his nobles; under "
                "them the archisuppôts, mostly fallen clergy, teach the "
                "rules. Both may beg as they like, untaxed.",
                "The rank and file, the argotiers, speak a secret cant and "
                "are licensed by trade: marcandiers play robbed merchants, "
                "francs-mitoux fake fainting fits, malingreux paint their "
                "faces with fat and ash to feign disease, piètres hobble on "
                "crutches, sabouleux smear on blood and froth with soap, "
                "polissons beg naked for clothes, courtauds-de-boutanche "
                "carry tools and plead lack of work, hutins claim mad-dog "
                "bites, coquillards show forged pilgrim papers, calots sit "
                "gaping like simpletons, capons cheat at cards, narquois "
                "are old soldiers who extort with threats, millards run "
                "rackets in the countryside, and orphelines cut rich men's "
                "purses.",
                "Seeds: a grog who has shown his mettle in Paris is "
                "kidnapped to be made one of the cagoux; visitors are caught "
                "up in a turf war between the king and a pretender.",
            ),
            "The present king is the magus Anacrôn of House Ex Miscellanea. "
            "Each year he enslaves a band of fighting men with The "
            "Irresistible Pressgang to serve as cagoux; when the spell "
            "ends, the Warping often leaves them witless and they sink "
            "among the calots. Two of his Hermetic forebears, crippled by "
            "age and Warping, live hidden among the beggars, kept alive "
            "against their will.",
        ),
    )
    w["free_spirit"] = b.faction(
        "The Brethren of the Free Spirit (Paris)",
        faction="Other",
        decides="A vote of all",
        place=p["paris_islets"],
        wants="The new age of the Holy Spirit, and freedom from sin and its rules.",
        summary=(
            "Among the biggest and best-loved heretical cults in Paris, "
            "begun by theologians of the schools and now loved by many "
            "common folk. They believe themselves heralds of a coming age "
            "of the Holy Spirit and beyond sin, and so indulge their "
            "pleasures without shame; their secret meetings and masses are "
            "held all over the city."
        ),
    )
    w["itinerarium"] = b.faction(
        "The Itinerarium",
        faction="Other",
        realm="Magic",
        decides="Its leader",
        place=p["eboris_site"],
        rules=(
            "Masters stay answerable under the Code for their apprentices' "
            "conduct, and some travel with them."
        ),
        wants="Taste, manners and a lived life for the young of House Jerbiton.",
        offers="Favours and social contacts to its hosts.",
        summary=paragraphs(
            "House Jerbiton's grand tour of the cities of art, meant to give "
            "senior apprentices and young magi taste, polish and enough "
            "experience of life to resist the pull of the laboratory. Before "
            "1204 they were sent to Constantinople; since its fall the tour "
            "usually runs from Paris over the Alps to Valnastium and on into "
            "Italy. Eboris hosts its first stage, and Mathieus keeps the "
            "rich, nearly-magi young merely foolish rather than "
            "disgraceful, or hides their mistakes; he is well "
            "paid in favours. Its leading figures are Antigones, the "
            "rising generation of Jerbiton who mean to mend the Order, and "
            "the tour lets them meet nearly every aspiring Jerbiton.",
        ),
    )
    w["candidus"] = b.faction(
        "Candidus, the Chalk-White Faerie",
        faction="Faerie court",
        realm="Faerie",
        decides="Its leader",
        ruler="Candidus",
        place=p["fontainebleau"],
        rules="Every bargain must be paid in full, at a price as strange as the wish is great.",
        wants="Pacts with mortals, and odd payments: a stone's breath, a man's reflection, a dying dragon's lament.",
        offers="Almost any wish, through a pact.",
        summary=secrets(
            paragraphs(
                "A powerful faerie of the forest of Fontainebleau who gains "
                "power by making pacts with mortals: the mere making of a "
                "bargain seems to give him the power to keep it. His name, "
                "Latin for chalk-white, was given by Lapis Crudus, who do "
                "not know his true one. He looks like a short man with "
                "chalky skin and white hair, dressed in dark blue, with "
                "smooth skin where eyes and sockets should be, yet he sees.",
                "In 1118 Aries of Flambeau tricked him into hiding and "
                "protecting Lapis Crudus. Candidus kept his word by moving "
                "the covenant into a regio, then sealed it in out of "
                "resentment. Since Aries's Final Twilight in 1215 he has "
                "allowed the exchange of the mirror.",
            ),
            "His limitless power may be borrowed: he may get the wishes he "
            "grants from other faeries or from humans through yet more "
            "pacts. Mnemon owes him an unknown and fearsome task.",
        ),
    )


# ------------------------------------------------------------------ Eboris


def _eboris(normandy: Normandy, tribunal: Tribunal) -> None:
    b = normandy.b
    summary = paragraphs(
        "Conventio Eboris, the House of the Ivory Carvers, is a small "
        "Jerbiton covenant in Paris whose members do no magical research. "
        "It was made not as a place to study but as a memorial: its "
        "founder, Archmagus Mathieus, saw Constantinople, the new Rome and "
        "in his eyes God's own instrument of civilisation, sacked in 1204, "
        "and the house is the machinery of his grief. He was away at "
        "Valnastium's library when the crusaders came, crossed their lines "
        "by magic too late to save the city, and fled with a few covenfolk "
        "and a little of his covenant's wealth by ship to Marseilles and "
        "overland to Paris, apparently to be out of the Latin Empire. His "
        "family and covenant were gone.",
        "For two years he was legally a wanderer, a nobleman in exile "
        "patronising the artists and scholars round the court. His Primus "
        "drew him back: he guided the Itinerarium on several of its tours, "
        "graduates came back to Paris to stay with him, and his home "
        "became a covenant. A Redcap, Marcus of Paris, runs the household "
        "as majordomo. The house is on the Rue de la Tabletterie, a former "
        "pilgrims' hostel turned ivory-carving office, chosen in a poor "
        "quarter so as not to threaten the nobility and to avoid the "
        "university; its basement lacuna counted too. Some members live "
        "elsewhere in the city.",
        "Its residents are the Sweated Shillings, a shifting band of young "
        "magi named for coins shaken in a bag until silver flakes off: "
        "always at least three besides Mathieus, many more during the "
        "Tour, interchangeable to outsiders, usually fun-loving and "
        "frantic to cram a lifetime into a year, and given to leaving "
        "Mathieus a crisis to mend. Jerbiton holds that magic tempts its "
        "practitioners to waste their lives, and that a vibrant city "
        "inoculates the young against the laboratory.",
        "Eboris owes no feudal dues and seeks none. Because its members do "
        "not study, it wants little of what other covenants fight over, "
        "so even its modest vis income leaves a surplus to trade, and it "
        "is rich. It is more and more a neutral ground for covenants in "
        "dispute. It is the senex of Paris. Mathieus holds revels "
        "eulogising great magi, feasts and games through the Paris night, "
        "for which he buys strange items from young magi across Europe as "
        "a way of drawing them into his circle; at least one magus he "
        "eulogised never existed, a fraud he blames on an unnamed Tytalus.",
        "Mathieus is the Warden of Paris: Jerbiton magi tell him what they "
        "do in the city and help him when it is threatened. He is also a "
        "convenient injured party for the Quaesitores, ready to say that "
        "another magus's doings caused him trouble with mundanes, which "
        "turns an unwelcome act into a breach of the Code; in Paris even "
        "small meddling with the powerful is punished. Not a hoplite, he "
        "is still a dangerous foe for young magi, with his illusions, his "
        "experience of casting in a city, his knowledge of Paris, his band "
        "of young allies and his political friends.",
    )
    what_matters = _lines(
        "Vis: a modest income (sources not given), enough to leave a surplus for trade",
        "Income: the ivory-carving business; silent shares in at least thirty Paris businesses; hospitality repaid in favours",
        "Income: Marcus of Paris's intelligence and recruiting services, sold to other covenants",
        "Boon: Urban; Wealth; Ivory carving as a covenant business; the lacuna in the cellar",
        "Boon: Neutral ground for negotiation between quarrelling covenants",
        "Boon: Senex of Paris (Tribunal ruling of 1200): its agents outrank others' in the city",
        "Hook: Mathieus is the only senior magus, elderly and without apprentices; succession is open",
        "Hook: the Sweated Shillings leave crises behind them",
        "Hook: the Itinerarium's apprentices to keep out of trouble",
        "Tension: an unsettled understanding with Anacrôn; if it came to war he has numbers and the streets",
        "Tension: Mathieus loathes Venice and the covenants he blames for the Fourth Crusade",
        "Mundane: influence over the quarter's thugs and the criminal class; patronage of artists; trust of the Byzantine émigrés",
        "Mundane: supports the French crown and the French Church",
    )
    hidden = _lines(
        "Mathieus's revels may honour magi long forgotten or entirely invented; some say the maga who never existed ought to have.",
        "Mathieus will help the Quaesitores by claiming injury when it suits him.",
        "Seed, the Folk Magicians: hedge wizards hidden in Paris need buying, warning off or killing.",
        "Seed, Rescuing Constantinopolitans: a slave of a Roman Tribunal covenant asks Mathieus to rescue survivors of his old covenant; Mathieus fears a Venetian trap and sends young magi to scout and smuggle.",
        "Seed, Treasure in Constantinople: Mathieus sealed away his dead friends' treasures in the city and now wants sturdy young magi to bring them out; he will not go himself.",
        "Seed, Succession: his named heir, Constantina filia Andru, was picked mostly to silence petitioners; a novel enough experience might win the player characters the place.",
        "Seed, Tremors at the End of the World: Paris's ivory comes through Trebizond, so a sudden stop means trouble in Asia, and Andru will send magi to look; a glut of walrus ivory would also make Mathieus ask who took it and why.",
    )
    eboris = b.covenant(
        "Eboris",
        tribunal=tribunal,
        founded=1204,
        place=normandy.places["eboris_site"],
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=0,
        unnamed_magi=3,
        season="Autumn",
    )
    normandy.covenants["eboris"] = eboris
    _eboris_magi(normandy, eboris)
    b.book(
        eboris,
        "The library of Eboris",
        "Other",
        description=(
            "The book names no Hermetic library here, and the covenant "
            "does no research. What it has are the few goods Mathieus "
            "carried from his fallen covenant in Constantinople and the "
            "curiosities he collects for his revels; a storyguide may give "
            "it Byzantine letters and art rather than Arts."
        ),
    )


def _eboris_magi(normandy: Normandy, eboris: Covenant) -> None:
    b, m = normandy.b, normandy.magi
    m["mathieus"] = b.magus(
        "Mathieus of Constantinople",
        covenant=eboris,
        house=JERBITON,
        age=104,
        summary=secrets(
            paragraphs(
                "Leader of Eboris and Warden of Paris, an archmagus, filius "
                "of Maria of Constantinople; apparent age 65. A scion of a "
                "Constantinopolitan noble house who plays the exiled lord, "
                "he follows the Jerbiton idea of sufficiency: he knows "
                "enough magic to live as he likes, and more study would "
                "only fool bigger crowds or win more certamen. Long bored "
                "by magic, he spent years in the vices of the rich; now he "
                "has goals he doubts he will reach.",
                "He backs the French crown, whose strength is remaking "
                "Paris into a city that could foster great beauty, which "
                "sets him against agents of the great dukes, of England "
                "and of Italian princes. He backs the Antigones, the "
                "rising Jerbiton generation, hoping they will mend an "
                "Order he thinks the best but a weak tool for peace. And "
                "he loathes Venice and the covenants he blames for the "
                "Fourth Crusade, supporting the French Church as a weight "
                "against Venice's hold on the pope and distrusting the "
                "Roman covenants with chapter houses in Venice. He is a "
                "master of illusion and of casting in a city.",
            ),
            "He named Constantina his heir mostly to stop people pestering "
            "him, and could be talked into naming someone who offers him a "
            "genuinely new experience.",
        ),
        traits={"Brave": 3, "Genteel": 2, "Debauched": 1, "Sad": 1},
    )
    m["marcus_of_paris"] = b.magus(
        "Marcus of Paris",
        covenant=eboris,
        house=MERCERE,
        age=None,
        summary=paragraphs(
            "Redcap and Mathieus's chief servant, the majordomo of Eboris "
            "(the book does not say whether he has the Gift). He sells "
            "news of Paris to other covenants, haggling every contract, "
            "from a weekly letter to the recovery of private papers, and "
            "sometimes passes the work to the young magi. When the nobles "
            "go home to their own lands he hires local magi's servants to "
            "keep watch on them for his clients.",
            "He also recruits: of the many odd characters who drift to "
            "Paris he picks the best, teaches some a little Latin and "
            "places them with covenants across the Tribunal for a fee from "
            "either side. A young covenant can get a full household from "
            "him, of very colourful pasts.",
        ),
    )
    m["constantina"] = b.magus(
        "Constantina filia Andru",
        covenant=None,
        house=JERBITON,
        age=None,
        summary=paragraphs(
            "A young firebrand of House Jerbiton, trained by the Primus "
            "Andru himself, and Mathieus's designated heir to Eboris, a "
            "choice he made largely to annoy the magi badgering him to "
            "pick one. The book does not say where she lives.",
        ),
    )
    m["andru"] = b.magus(
        "Andru",
        covenant=None,
        house=JERBITON,
        age=None,
        summary=paragraphs(
            "Primus of House Jerbiton, who drew Mathieus back into "
            "Hermetic life by asking him to host the Itinerarium, and who "
            "trained Constantina. He knows that the last time Paris's "
            "ivory dried up the Huns were coming, and would send magi to "
            "learn why if it happened again. He does not live in the "
            "Tribunal.",
        ),
    )


# ------------------------------------------------------------ Lapis Crudus


def _lapis_crudus(normandy: Normandy, tribunal: Tribunal) -> None:
    b = normandy.b
    summary = paragraphs(
        "Once one of the great covenants of Normandy, Lapis Crudus is a "
        "shadow of itself after more than eighty years shut inside a "
        "faerie regio, and its magi, lately able to come and go after a "
        "fashion, are trying to win back their old standing. It was born "
        "of the Schism War's spoils: the Grand Tribunal sponsored it in "
        "1063 to heal the breach between Flambeau and Tytalus, with two "
        "magi of each, a Jerbiton and a Bonisagus of Trianoma's line. "
        "Many of Normandy's Flambeau descend from its founders; for a "
        "time they were the only two Flambeau in the Tribunal. It grew "
        "more mixed, was a leading voice in Tribunal politics and culture "
        "for a century, was a liege covenant, and sponsored two vassals, "
        "both short-lived. In 1113 Koilios of Montverte raided its supply "
        "train, and the Tribunal's refusal to punish him set the "
        "precedent that allows raiding.",
        "In 1118 a mishap betrayed its site and nature to several noble "
        "families, who tried to use the magi; threats and blackmail held "
        "them off for a while. To escape, Aries of Flambeau tricked the "
        "faerie Candidus into protecting and hiding the covenant. Candidus "
        "kept the bargain by moving it into a regio, and in resentment "
        "sealed the borders. Some vis seisins lay inside, but at first "
        "the magi had to spend them on food and tools, until one of them "
        "learned to pass non-living goods inward and they tasted meat and "
        "wine for the first time in nearly seventy years. They lived on "
        "their large vis stocks and wore out their library. Their vassals, "
        "glad of freedom, made little effort to free them, and they were "
        "forgotten.",
        "Aries entered Final Twilight five years ago, in 1215, and "
        "Candidus agreed to new terms: anyone may leave if someone of like "
        "social standing enters in exchange, magus for magus, churchman "
        "for churchman or scholar, outcast for outcast, and the newcomer "
        "may bring whatever he can carry. The gate is a mirror in a hut "
        "that straddles the regio's edge on Les Trois Pignons in the "
        "forest of Fontainebleau; the two walk toward it from either side "
        "and change places. Laden grogs swap in and out constantly. "
        "Outside there are only a few shacks of apparent outlaws.",
        "Inside, under a Faerie aura of 7, a dozen sandstone buildings "
        "fill a star of valleys, lit directly only at midday: a sanctum in "
        "each arm, covenfolk at the centre, the council chamber over the "
        "cavern of the Bleeding Stone. Minor Herbam and Terram enchantments "
        "made in captivity are everywhere: doors open in walls as people "
        "approach, roofs turn clear on command, the humblest cook has a "
        "magic knife. Through Somnifer's dreams the magi kept up with the "
        "world, yet they are oddly naive about the Order, eager to see it "
        "again, and see it through the twist of the strong Faerie aura. "
        "Three ancient, narrowly specialised magi remain; Somnifer's "
        "filius Languidus has spoken for the covenant at Tribunal for ten "
        "years but will not join it. It has not entered the Tourney since "
        "it was sealed, and all its legacies are held to have lapsed. Most "
        "covenfolk were born inside, some of the third generation, and "
        "are badly Warped (a score of 3 by puberty and 5 by their late "
        "forties); they assume every covenant uses magic items for "
        "everyday work.",
    )
    what_matters = _lines(
        "Vis: the Bleeding Stone, in a cavern under the council chamber, Corpus and Terram (seisin; amount not given)",
        "Vis: the vines down the valley cliffs, Herbam (seisin; amount not given)",
        "Vis: large old stocks, much drawn down by eighty years of study",
        "Library: large, with several rare high-quality tomes and many tractatus written in captivity",
        "Boon: Regio; Faerie Aura 7; household enchantments everywhere (Herbam and Terram)",
        "Hook: trapped behind Candidus's mirror; leaving needs a substitute of like standing",
        "Hook: covenfolk heavily Warped; magi nearing Final Twilight",
        "Hook: all legacies lapsed; no Tourney team since the sealing",
        "Tension: means to reclaim its old vassals, now independent",
        "Tension: Mnemon's unknown debt to Candidus",
        "Tension: Somnifer is second in line for Praeco after Celeres of Cunfin",
    )
    hidden = _lines(
        "Seed, Through the Looking Glass: to travel, the magi must tempt other magi to take their place, offering seasons in the library; once out, they do not want to go back.",
        "Seed: as the price of the new terms Candidus bound Mnemon to a fearsome task once he gets out, which might destroy a player covenant's faerie-bound vis source, kill its guardian, or stir mundane politics to have it disbanded.",
        "Seed: Lapis Crudus will try to reassert its lost Oaths of Fealty, perhaps over the player covenant.",
        "Each magus took a Warping Point a year from the aura alone during the eighty years, and more from Longevity Rituals; the opening may have come just in time.",
    )
    lapis = b.covenant(
        "Lapis Crudus",
        tribunal=tribunal,
        founded=1063,
        place=normandy.places["lapis_crudus_site"],
        level=1,
        summary=summary,
        what_matters=what_matters,
        notes=secrets(STORYGUIDE, hidden),
        aura=7,
        realm="Faerie",
        unnamed_magi=1,
        season="Winter",
    )
    normandy.covenants["lapis_crudus"] = lapis
    normandy.tenure(
        "The Bleeding Stone (Corpus and Terram)",
        lapis,
        "seisin",
        notes="In a cavern under the council chamber, inside the regio",
    )
    normandy.tenure(
        "The cliff vines of Lapis Crudus (Herbam)",
        lapis,
        "seisin",
        notes="On the valley walls inside the regio",
    )
    _lapis_magi(normandy, lapis)
    b.book(
        lapis,
        "The library of Lapis Crudus",
        "Other",
        description=(
            "A large magical library, among the best in the Tribunal before "
            "the sealing, with several rare tomes of high quality. During "
            "the captivity the magi read it to exhaustion and added many "
            "tractatus of their own until their ink and parchment ran out; "
            "Somnifer also copied books held up to the mirror, rearranging "
            "the mirrored ink by magic. No titles are named. The magi offer "
            "seasons of study here to tempt others to take their places."
        ),
    )


def _lapis_magi(normandy: Normandy, lapis: Covenant) -> None:
    b, m = normandy.b, normandy.magi
    m["somnifer"] = b.magus(
        "Somnifer of Merinita",
        covenant=lapis,
        house=MERINITA,
        age=113,
        summary=secrets(
            paragraphs(
                "A master of dream magic, apparent age 30. During the "
                "captivity he sent his mind out in spirit form into the "
                "dreams of those he met and so kept the covenant informed "
                "of the world. He found his apprentice Languidus through "
                "dreams, lured him to the regio and trained him through the "
                "mirror in the hut that was his schoolroom and scriptorium. "
                "Warping blurs dream and waking for him, and it is hard to "
                "tell whether he is awake or sleepwalking.",
                "With Renita dead and Stellatus gone to Iberia, he is next "
                "after Celeres of Cunfin in the line of eldest magi from "
                "which the Praeco is named.",
            ),
            "Proctor, who wants a Praeco he can trust or control, finds "
            "Somnifer as awkward a choice as Celeres.",
        ),
        traits={"Sleepy": 5, "Thoughtful": 2, "Attentive": -2},
    )
    m["mnemon"] = b.magus(
        "Mnemon of Tytalus",
        covenant=lapis,
        house=TYTALUS,
        age=97,
        summary=secrets(
            paragraphs(
                "A master of Rego, apparent age 60. He was a year short of "
                "his Gauntlet when the regio closed (the book's age for him "
                "fits that badly), and has never really lived his House's "
                "culture of conflict. Searching for a way out, he grew "
                "expert in spells of transport; he made the mirror that is "
                "now the covenant's gate and negotiated the new terms with "
                "Candidus. Walking and running exasperate him, and he has "
                "an unsettling habit of popping across a room or snapping "
                "objects into his hand.",
            ),
            "Nobody knows what he promised Candidus. Once someone takes "
            "his place he must carry out a fearsome task the faerie bound "
            "him to, which could fall on a player covenant.",
        ),
        traits={"Impatient": 3, "Sly": 2, "Apparently Trustworthy": 1},
    )
    m["languidus"] = b.magus(
        "Languidus of Merinita",
        covenant=None,
        house=MERINITA,
        age=None,
        summary=(
            "Somnifer's filius, found in dreams and trained from the far "
            "side of the regio through the enchanted mirror. For the past "
            "decade he has represented Lapis Crudus at Tribunal, but he has "
            "refused to become a member."
        ),
    )


# ----------------------------------------------------------------- eremites


def _eremites(normandy: Normandy) -> None:
    b = normandy.b
    normandy.magi["anacron"] = b.magus(
        "Anacrôn, King of the Beggars",
        covenant=None,
        house=EX_MISC,
        age=56,
        summary=secrets(
            paragraphs(
                "An eremite of House Ex Miscellanea who lives on the "
                "streets of Paris as King of the Beggars, the Grand Coësre. "
                "Bitter, jealous and spiteful, he hates the world and most "
                "of humanity. His master took his legs above the knee when "
                "he was a boy, in opening him to the Arts, for his "
                "tradition's magic rests on pain, hatred and infirmity. He "
                "rides a two-wheeled cart drawn by two huge mastiffs: "
                "Affreux, his familiar, who can raise a ward that repels "
                "people and grow to the size of a bear, and Affreux's son "
                "Boiteux, his magical companion. Under the rags and filth "
                "he is a handsome, compelling man.",
                "When he grew strong enough to take over the gang that "
                "raised him, his pater crowned him king and left Paris, as "
                "his own pater had done; where they went, Anacrôn does not "
                "know. His family has ruled the beggars for over a century, "
                "far longer than Eboris has existed. Through his subjects "
                "he can find hands for any job and hears news the Order "
                "wants, and sells both for vis and enchantments, mostly to "
                "Eboris and Fudarus. He never takes part in the crimes he "
                "plans. Twice accused of interfering with mundanes, he was "
                "cleared once (no ruin was shown); the second time Harpax "
                "of Fudarus declared Wizard's War on the accuser and no "
                "charge was ever brought. Many wonder why he has such "
                "friends. He and Mathieus are still working out their "
                "terms by deed rather than word; both would avoid war, in "
                "which Anacrôn has the numbers, the streets and a killer's "
                "instinct. Montverte has dealt with him on raids against "
                "other covenants' town storehouses.",
            ),
            paragraphs(
                "His lineage shares a Death Prophecy: none can die until "
                "he is the eldest of the tradition alive. Two of his "
                "forebears, his grand-parens's own parens and her mater, "
                "survive hidden among his beggars in ruined bodies, "
                "riddled with Decrepitude and Warping and longing to die; "
                "he will not let them, since each death brings his own "
                "nearer. An enemy might strike at him through them.",
                "He knows many dirty secrets of Normandy's magi and has a "
                "few genuine allies who value his information. He might "
                "draw help from a cabal or Mystery Cult, or be a double "
                "agent hunting High Crimes among his apparent friends for "
                "the Quaesitores.",
            ),
        ),
        traits={"Jealous": 3, "Spiteful": 3, "Bitter": 3},
    )


def _links(normandy: Normandy) -> None:
    b, w, m, c = normandy.b, normandy.world, normandy.magi, normandy.covenants
    b.link(w["beggars"], "characters", m["anacron"], "Its king, the Grand Coësre")
    b.link(w["candidus"], "covenants", c["lapis_crudus"], "Bound to it by Aries's pact")
    b.link(w["itinerarium"], "covenants", c["eboris"], "Hosts the tour's first stage")


# -------------------------------------------------------------------- stats

ANACRON: dict[str, Any] = {
    "characteristics": {
        "intelligence": 3,
        "perception": 0,
        "presence": 2,
        "communication": 2,
        "strength": 0,
        "stamina": 1,
        "dexterity": -2,
        "quickness": -2,
    },
    "size": 0,
    "confidence": (1, 3),
    "decrepitude": (0, 0),
    "warping": (4, 2),
    "apparent_age": 40,
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Death Prophecy",
        "Life-Linked Spontaneous Magic",
        ("Affinity with {art}", {"art": "corpus"}),
        ("Minor Magical Focus", {"focus": "infirmity"}),
        "Personal Vis Source",
        "Piercing Gaze",
        ("Puissant {ability}", {"ability": "leadership"}),
        "Quiet Magic",
        ("Social Contacts", {"group": "the Paris underworld"}),
        "Crippled",
        "Envious (Major)",
        "Painful Magic",
        ("Deficient Form", {"form": "imaginem"}),
        "Infamous",
        ("Magical {being} Companion", {"being": "Animal"}),
    ],
    "traits": {"Jealous": 3, "Spiteful": 3, "Bitter": 3},
    "reputations": {"King of the Beggars (Local)": 3},
    "abilities": [
        ("Living Language: Argot", 4, "Parisian beggars"),
        ("Organization Lore: Argotiers", 4, "cagoux"),
        ("Artes Liberales", 2, "rhetoric"),
        ("Awareness", 2, "potential marks"),
        ("Brawl", 1, "self defence"),
        ("Chirurgy", 2, "bruises"),
        ("Civil and Canon Law", 2, "begging"),
        ("Code of Hermes", 1, "regarding mundanes"),
        ("Concentration", 2, "when in pain"),
        ("Finesse", 2, "Corpus"),
        ("Folk Ken", 2, "potential marks"),
        ("Living Language: French", 5, "Parisian"),
        ("Guile", 4, "to the charitable"),
        ("Area Lore: Ile de France", 3, "criminals"),
        ("Intrigue", 4, "Hermetic"),
        ("Area Lore: Kingdom of France", 2, "beggars"),
        ("Dead Language: Latin", 3, "coarse"),
        ("Leadership", 5, "beggars"),
        ("Legerdemain", 3, "slitting purses"),
        ("Magic Theory", 6, "studying from vis"),
        ("Area Lore: Paris", 4, "underworld"),
        ("Parma Magica", 4, "Corpus"),
        ("Penetration", 3, "Corpus"),
        ("Organization Lore: Order of Hermes", 3, "rivalries"),
        ("Single Weapon", 1, "club"),
        ("Stealth", 3, "sitting still"),
    ],
    "arts": {
        "Creo": 13,
        "Intellego": 6,
        "Muto": 8,
        "Perdo": 10,
        "Rego": 8,
        "Animal": 8,
        "Aquam": 5,
        "Auram": 5,
        "Corpus": 15,
        "Herbam": 4,
        "Ignem": 5,
        "Imaginem": 3,
        "Mentem": 14,
        "Terram": 5,
        "Vim": 8,
    },
    "spells": [
        ("Agony of the Beast", "PeAn", 15, 0),
        ("Arm of the Infant", "MuCo", 20, 0),
        ("Aura of Rightful Authority", "ReMe", 20, 0),
        ("Bane of the Decrepit Body", "PeCo", 25, 0),
        ("Circle of Beast Warding", "ReCo", 5, 0),
        ("Cripple the Howling Wolf", "PeAn", 25, 0),
        ("Disguise of the New Visage", "MuCo", 15, 0),
        ("Gift of the Frog's Legs", "ReCo", 15, 0),
        ("Loss of But a Moment's Memory", "PeMe", 15, 0),
        ("Panic of the Trembling Heart", "CrMe", 15, 0),
        ("Posing the Silent Question", "InMe", 20, 0),
        ("Prison of Flames", "MuIg", 20, 0),
        ("Stench of the Twenty Corpses", "CrAu", 10, 0),
        ("The Irresistible Pressgang", "CrMe", 35, 0),
        ("The Twisted Spine", "MuCo(Pe)", 20, 0),
        ("The Wound that Weeps", "PeCo", 15, 0),
        ("Trust of Childlike Faith", "PeMe", 10, 0),
    ],
    "notes": paragraphs(
        "Stat block as printed in The Lion and the Lily. Death Prophecy, "
        "Personal Vis Source and Painful Magic are his tradition's House "
        "Virtues and Flaw. Leadership is 5, +2 from Puissant Leadership. "
        "The spell list gives The Irresistible Pressgang as level 40 and "
        "The Twisted Spine as MuCo 25, while their own write-ups give CrMe "
        "35 and Mu(Pe)Co 20; the write-ups are used.",
        "Combat: club Init -2, Attack +2, Defence +1, Damage +3; dodge "
        "Init -3, Defence 0. Soak +1.",
        "Twilight Scars: his Gift draws vermin instead of repelling them; "
        "his breath has the scent of violets; his shadow is the red of blood.",
        "Equipment: a rickety wooden two-wheeled trolley. His talisman is a "
        "wand roughly carved from a human leg bone and set with three small "
        "bloodstones (+4 destroy human body, +4 blood and wounds), holding "
        "two enchantments: Agony of the Uncharitable Stranger (PeCo 30; "
        "Voice, Concentration, Individual; Penetration 20, 24 uses a day; "
        "racks the target with stabbing pains) and Hobble the Foul-Mouthed "
        "Wretch (PeCo 40; Voice, Sun, Individual; Penetration 20, 24 uses a "
        "day; lames the target for the duration).",
        "Vis: his Personal Vis Source is the skin he scrapes from his leg "
        "stumps, which gives Corpus vis at the price of much pain.",
        "Familiar: Affreux, a brindled mastiff, who can create a ward "
        "against people and grow to a bear's size. Magical Animal "
        "Companion: Boiteux, Affreux's son. The two pull his trolley.",
        "Each year, vis permitting, he casts The Irresistible Pressgang on "
        "at least ten fighting men to make them his cagoux; the five Warping "
        "Points it leaves often make them Simple-Minded or similar when it "
        "ends.",
    ),
}

P = Profile

#: Each sketched magus's profile, by character id.
PROFILES: dict[str, Profile] = {
    "mathieus": P(
        strong="pre com int",
        native="Greek",
        arts={"Im": 7, "Me": 4, "Cr": 3, "Mu": 3, "Re": 3, "In": 2},
        abilities={
            "Etiquette": (4, "the Paris court"),
            "Charm": 3,
            "Area Lore: Paris": (4, "its quarters by night"),
            "Living Language: French": 3,
            "Intrigue": (3, "Parisian potentates"),
            "Carouse": 2,
            "Folk Ken": 2,
            "Bargain": 1,
        },
        virtues=[
            "Gentle Gift",
            "Hermetic Prestige",
            ("Social Contacts", {"group": "the Paris court and its artists"}),
            ("Affinity with {art}", {"art": "imaginem"}),
            "Depressed",
            "Hatred (Minor)",
            "Lecherous (Minor)",
            "Enemies",
        ],
        reputations={"Warden of Paris (Hermetic)": 3},
    ),
    "marcus_of_paris": P(
        gifted=False,
        age=40,
        strong="per com",
        native="French",
        abilities={
            "Area Lore: Paris": (5, "informants"),
            "Bargain": (3, "contracts"),
            "Folk Ken": 3,
            "Intrigue": 2,
            "Guile": 2,
            "Leadership": (2, "servants"),
            "Etiquette": 2,
            "Dead Language: Latin": 3,
            "Organization Lore: Order of Hermes": 2,
            "Code of Hermes": 2,
        },
        virtues=[
            "Redcap",
            ("Social Contacts", {"group": "the servants of Paris"}),
            "Greedy (Minor)",
            "Busybody",
            "Dutybound",
            "Secretive",
        ],
    ),
    "constantina": P(
        age=30,
        strong="pre com",
        native="Greek",
        arts={"Ig": 5, "Cr": 4, "Re": 3, "Me": 3},
        abilities={
            "Etiquette": 2,
            "Charm": 2,
            "Intrigue": (2, "the Antigones"),
            "Organization Lore: Order of Hermes": (2, "House Jerbiton"),
        },
        virtues=[
            "Skilled Parens",
            "Self-Confident",
            "Reckless (Minor)",
            "Proud (Minor)",
        ],
    ),
    "andru": P(
        age=90,
        strong="pre int com",
        native="Italian",
        arts={"Me": 5, "Im": 4, "In": 3, "Re": 3},
        abilities={
            "Leadership": (3, "House Jerbiton"),
            "Intrigue": (4, "Hermetic politics"),
            "Etiquette": 3,
            "Organization Lore: Order of Hermes": (3, "House Jerbiton"),
            "Teaching": 2,
        },
        virtues=[
            "Hermetic Prestige",
            "Good Teacher",
            "Dutybound",
            "Busybody",
        ],
        reputations={"Primus of House Jerbiton (Hermetic)": 5},
    ),
    "somnifer": P(
        strong="per int",
        native="French",
        arts={"Me": 8, "In": 5, "Im": 4, "Re": 3, "Vi": 3, "Cr": 2},
        abilities={
            "Faerie Lore": (3, "Candidus"),
            "Teaching": (3, "through the mirror"),
            "Profession: Scribe": (2, "mirror-writing"),
        },
        virtues=[
            "Dream Magic",
            ("Minor Magical Focus", {"focus": "dreams"}),
            "Sleep Disorder",
            "Delusion",
        ],
    ),
    "mnemon": P(
        strong="int qik",
        native="French",
        arts={"Re": 8, "Te": 4, "Co": 4, "Vi": 3, "Im": 2},
        abilities={
            "Faerie Lore": (2, "pacts"),
            "Guile": (2, "bargaining with faeries"),
            "Intrigue": 1,
        },
        virtues=[
            ("Minor Magical Focus", {"focus": "transportation"}),
            "Fast Caster",
            "Dark Secret",
        ],
    ),
    "languidus": P(
        age=45,
        strong="com pre",
        native="French",
        arts={"Me": 5, "Im": 3, "In": 3},
        abilities={
            "Code of Hermes": (3, "Tribunal procedure"),
            "Intrigue": (2, "the Normandy Tribunal"),
            "Faerie Lore": 2,
        },
        virtues=["Weak Parens"],
    ),
}


def stats(normandy: Normandy) -> None:
    """Anacrôn's printed stat block, then generated stats for every other
    magus this part made."""
    b = normandy.b
    b.stats(normandy.magi["anacron"], ANACRON)
    for key, profile in PROFILES.items():
        apply(b, normandy.magi[key], profile)
