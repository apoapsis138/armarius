"""Brittany, the Normandy Tribunal's wild western peninsula, as of spring
1220: its counties and lordships, Brocéliande, Carnac and the other
megaliths, forests, isles and regiones; Fudarus, the domus magna of House
Tytalus, and its vassal Exspectatio, with their magi, libraries and vis;
the vis sources the Perthean Compact holds there; and the duke, the
barons, the Breton sees and abbeys, the towns and the factions, in
paraphrase of The Lion and the Lily chapter four.

The ruined covenants of Brittany (Branugurix, Kerguntuil) are
tribunal.py's. Creatures (the Three Great Spirits of Ushant, the
korrigan, the Nains of Carnac, the Black Dog, the Ankeu) are described in
the summaries of the places they haunt; those with a stat block are also
bestiary.py's creatures.
Records are kept in the Normandy dicts under slugs: the region is
places["brittany"], the covenant sites places["ushant"] and
places["exspectatio_site"], Mount Dol (Branugurix's hill) places["mount_dol"]
and the Rose Coast (Kerguntuil's) places["rose_coast"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...arms import Arms
from ..builder import Builder, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Normandy

TYTALUS = "house_tytalus"

# The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}

#: The note on a vis source whose tenure the book leaves out.
INFERRED = (
    "The book gives no tenure; a known source that is neither a seisin "
    "nor under a legacy lease is a tropaeum under the ruling of 1032."
)
INFERRED_CONTEST = (
    "The book gives no tenure; a Tribunal source whose harvest rests on "
    "the harvester's skill is a luctatio under the ruling of 1039."
)


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(normandy: Normandy, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = normandy.b.place(name, **kw)
    normandy.places[key] = place
    return place


def build(normandy: Normandy) -> None:
    b = normandy.b
    tribunal = normandy.tribunal
    assert tribunal is not None
    _region(normandy)
    _rennes(normandy)
    _broceliande(normandy)
    _penthievre(normandy)
    _leon(normandy)
    _cornouaille(normandy)
    _broerec(normandy)
    _nantes(normandy)
    _fudarus(normandy, b, tribunal)
    _exspectatio(normandy, b, tribunal)
    _vis(normandy)
    _lords(normandy, b)
    _sees(normandy, b)
    _abbeys(normandy, b)
    _towns(normandy, b)
    _factions(normandy, b)


# ------------------------------------------------------------- the region


def _region(normandy: Normandy) -> None:
    if "brittany" in normandy.places:
        return
    _add(
        normandy,
        "brittany",
        "Brittany",
        summary=paragraphs(
            "A peninsula of hard crystalline rock thrust into the Atlantic at "
            "the Tribunal's western edge. The north-west wind brings fog, mist "
            "and rain most days, more in the north than in the sunnier south, "
            "and the sea keeps the land free of frost. The Armor, the "
            "country by the sea, is a long, ragged coast of high cliffs, "
            "drowned river valleys and countless islands, where great tides "
            "bare mud flats and rock shelves twice a day. The Argoat, the "
            "country of the wood, is an upland cut by deep valleys, forested "
            "or, where the trees went long ago, moorland; its thin soils "
            "over granite, schist and gneiss make its peasants among the "
            "poorest in the Tribunal, though the sheltered valleys farm well.",
            "Faeries, giants and magical beasts held the land first, served "
            "by a few pagans. Rome ruled for four centuries; then Celts from "
            "Britain settled it and saints crossed from Wales to convert it. "
            "Louis the Pious made it a duchy under Nominoé, who won its "
            "independence from Charles the Bald; Erispoë took the title of "
            "king, Salomon seized the throne by murder, and the kings held "
            "off the Norsemen until Alain Crookbeard died in 952. A century "
            "of noble feuding ended with Alain IV Fergent; marriage and "
            "fealty then drew the duchy to Anjou, and Henry II of England "
            "took it between 1158 and 1166. It slipped free of the English "
            "crown after King John was rumoured to have murdered his nephew "
            "Arthur of Brittany, and Peter of Dreux now rules it as regent "
            "for his wife Alice's son.",
            "The east speaks a French dialect close to its neighbours'; the "
            "west speaks Breton, seldom written, and in the countryside "
            "often nothing else. The harp and the Breton pipes play for "
            "dances in lines and rings; sports are lifting a heavy beam like "
            "a chariot axle, putting heavy stones, and a seated tug for a "
            "short stick with the feet braced on a low board. The great "
            "feasts are the pardons: processions with prayers, then feasting, "
            "each old parish keeping its own saint's day. Bretons hold that "
            "Welsh monks brought the faith, and every Breton should once in "
            "life make the Tro Briez, the round of the eight founders' "
            "cathedrals (St Malo, St Brieuc for St Broch, Perros-Guirec for "
            "St Guirec, St-Pol-de-Léon for St Paul, Dol for St Samson, "
            "Tréguier for St Tugdual, Quimper for St Corentine and Vannes for "
            "St Patern); whoever fails must make it after death, creeping a "
            "coffin's length every seven years.",
            "Brittany is the least civilised and emptiest part of the "
            "Tribunal and the richest in vis, much of it unclaimed, with "
            "only Fudarus and its vassals near; covenants founded here, in "
            "Brocéliande above all, have all failed. Megaliths are "
            "everywhere, many with an aura: a dolmen (flat slabs on upright "
            "stones) may be a giants' table, a faerie meeting place or an old "
            "altar; a menhir (one standing stone) may have been raised by "
            "saints, angels, demons, giants or faeries; a tumulus (a mound) "
            "may be a clod a giant threw or earth heaped over a faerie door, "
            "and many hide a dolmen. Every acre still has a lord, so a "
            "covenant on a lonely isle, a firm patch of marsh or a forest "
            "hollow must still deal with the feudal order and the Church.",
            "Across the duchy roam the Ankeu, Death as a shrouded skeleton "
            "with a scythe driving a creaking cart heaped with the dead (on "
            "the islands he comes by the Bag Noz, the night boat): to hear "
            "the cart foretells a loved one's death, and to meet it is "
            "nearly always one's own. A folk rite traps a ghost that will not "
            "leave its house in a black dog, to be drowned at once: the dog "
            "(Divine Might 10 at most, usually 5; Infernal for a sinner's "
            "ghost, Magic for a pagan's) barks fear and howls despair, and "
            "if it dies any way but drowning the spirit stays bound where it "
            "fell, with a pawn or two of vis in its tongue. Korrigan, "
            "hunched manikins with cat's claws and goat's hooves, dance at "
            "crossroads and hoard treasure in woods, caves and dolmens; "
            "outside Brocéliande they are more fond of dancing and riches "
            "than of harm, but quick to punish.",
            "Folk tales across the duchy hint at what magi might find: two "
            "quarrelling trees that are a bewitched husband and wife; a king "
            "of fishes, a king of birds and a bound demon king who each repay "
            "a rescue; three hermits whose advice adds up to an answer; "
            "starved beasts on rich grass beside fat beasts on bare ground; "
            "a loaf that never grows less; a silver whistle that calls the "
            "birds; a shirt that freezes an unwanted lover till dawn; apples "
            "of sleep; a honey cake that brings a maiden a helpful magic cat "
            "and a good husband; a cloth that lays a meal when spread. Other "
            "tales tell of the Princess of the Shining Star, kept from men "
            "in a tower of a green glass castle hung in the air on gold and "
            "silver chains inside a Magic regio, who steals young women as "
            "companions; of the Mother of Winds, a bearded old woman by her "
            "forest fire who keeps her four giant sons in order with a sack; "
            "and of a white Magic fox by a stone with an aura, whose ivory "
            "ball, if followed, rolls to a forest hermit.",
        ),
        **KNOWN_ORDER,
    )


# ------------------------------------------------------- County of Rennes


def _rennes(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    rennes = _add(
        normandy,
        "county_of_rennes",
        "County of Rennes",
        inside=region,
        summary=paragraphs(
            "The duchy's east, gentler, drier and richer than the rest, "
            "largely wooded, and studded with strong castles from the recent "
            "wars against the Normans and the Franks. Its northern shore, the "
            "Emerald Coast, runs low and marshy toward the sands of Mont St "
            "Michel; west of the marshes to St Brieuc Bay it turns to high, "
            "rocky cliffs with a few small beaches. Inland the Rance leads to "
            "the forested hills of Hunaudaye, deep ravines and scattered "
            "granite boulders crossed by a single trade road from Rennes to "
            "St Brieuc. At the centre stands Rennes on the Vilaine, which "
            "runs south-west between red stone hills; to the west lies "
            "Brocéliande, and near the Normandy border the forest round "
            "Fougères is thick with megaliths even for Brittany.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "mount_dol",
        "Mount Dol",
        inside=rennes,
        summary=paragraphs(
            "A granite knoll only about two hundred feet high that "
            "nonetheless commands the marshes, a holy place of the Gallic "
            "druids. Branugurix, the domus magna of House Diedne, lay "
            "hidden in a regio here. Christians shun the hill: they say "
            "St Michael fought the Devil on it and flung him down so hard "
            "that the hollow and the claw marks still show on its north "
            "side, beside the cleft of the saint's sword; when the Devil "
            "reappeared on Mont St Michel, the saint leapt after him and "
            "left a footprint on the summit.",
            "South of the town of Dol stands the menhir of Champ-Dolent.",
        ),
        secrets="The legend of St Michael is a garbled memory of the Order's "
        "assault on Branugurix. The regio's entrances were closed in the "
        "last battle of the Schism War.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "champ_dolent",
        "The Menhir of Champ-Dolent",
        inside=rennes,
        summary=(
            "The Field of Pain, south of Dol: a single stone thirty feet tall, "
            "square at the base and tapering to a point, which marks the "
            "ground of the last battle of the Schism War."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "decolle_point",
        "The Siren's Cave at Décollé Point",
        inside=rennes,
        summary=(
            "A cave at the foot of the first headland west of the Rance "
            "mouth, home to a siren. She guards a natural rock bridge "
            "between the cliffs and Décollé Point, and nobody has learned "
            "why she protects the point."
        ),
        **RUMOURED,
    )
    _add(
        normandy,
        "singing_stones",
        "The Singing Stones",
        inside=rennes,
        summary=(
            "A heap of rocks on the coast above the Arguenon estuary that "
            "rings like metal when struck. Struck the right way with a stone "
            "of the same kind, the sound can be harvested as Imaginem vis."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "corseul",
        "The Temple of Mars at Corseul",
        inside=rennes,
        aura=3,
        summary=(
            "A Roman settlement about five miles west of Dinan, where the "
            "round wall of a temple of Mars, of thin Roman brick, still "
            "rises above the treetops; nothing else of it shows. The ruin "
            "has a Magic aura of 3, and through the regio boundary the "
            "temple stands whole."
        ),
        levels=[
            Builder.level(
                "The temple whole",
                6,
                notes="Inside the walls, past the regio boundary, the building is intact.",
            )
        ],
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "st_brochs_fountain",
        "St Broch's Fountain",
        inside=rennes,
        realm="Divine",
        summary=(
            "The spring at St Brieuc beside which the saint lived. Once a "
            "week, leaving the cathedral after Sunday Mass, a person may "
            "dip the right hand in it and devoutly cross himself for a "
            "blessing that shifts one Personality Trait a step until sunset "
            "(no further than +3 or -3): a lowered step falls on the trait "
            "likeliest to lead to sin, a raised one on the trait likeliest "
            "to lead to good."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "plechatel",
        "The Caves and Oak of Pléchâtel",
        inside=rennes,
        aura=1,
        summary=(
            "Well-hidden caves near the village of Pléchâtel in the Vilaine "
            "valley, with a weak Magic aura (its strength is not given), and "
            "an ancient oak whose few unusually large acorns are vis (the "
            "book does not name the Art)."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "langon",
        "The Young Ladies of Langon",
        inside=rennes,
        summary="About thirty standing stones on the moor by Langon, a village "
        "on terraces above the Vilaine whose chapel of St Agatha is "
        "built into the walls of a Romano-Gallic temple of Venus. "
        "Locals say the stones are girls who danced on the moor instead "
        "of going to vespers and were turned to stone by God.",
        secrets="The stones are far older than the tale and belong with the "
        "temple: they record the fate of the women who served it.",
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "faeries_rock",
        "Faeries' Rock",
        inside=rennes,
        realm="Faerie",
        summary=paragraphs(
            "Forty-two huge slabs of purple schist in the forest south-east "
            "of Rennes, halfway to the Normandy border: a broad, low doorway "
            "facing the midwinter sunrise opens on a passage and a tall "
            "chamber divided into stalls.",
            "Each year on the eve of the winter solstice a faerie court sits "
            "here to judge faeries, and sometimes mortals, who have broken "
            "its seemingly arbitrary laws. The accused are snatched from "
            "their beds and set down in the chamber almost at once; anyone "
            "present, the accused included, may speak briefly for or "
            "against, and the presiding faerie noble gives verdict and "
            "sentence, rewards and punishments as capricious as the laws. "
            "However long the hearing seems, it ends when the first ray of "
            "dawn enters the chamber, and mortals must find their own way "
            "home.",
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------------------ Brocéliande


def _broceliande(normandy: Normandy) -> None:
    rennes = normandy.places["county_of_rennes"]
    forest = _add(
        normandy,
        "broceliande",
        "The Forest of Brocéliande",
        inside=rennes,
        realm="Faerie",
        aura=2,
        summary=paragraphs(
            "A vast, mysterious and perilous forest west of Rennes and the "
            "Vilaine, under a Faerie aura of 2 that runs much higher in "
            "places. A small monastery at Paimpont tries to counter its "
            "influences and makes little headway. Brittany's richest faerie "
            "and vis sites lie here, and every covenant founded in it has "
            "failed, whether to territorial faeries or territorial magi.",
            "The korrigan of Brocéliande are the most dangerous in Brittany "
            "since their queen Viviane lost interest in them and the forest. "
            "A korred is a hunched manikin about three feet tall with cat's "
            "claws and goat's hooves (Faerie Might usually 5 to 10, rarely "
            "15, Animal): a tireless dancer and a magician, greedy, "
            "capricious and short-tempered, quick with claws, club and "
            "thrown stones, and the stronger ones can spend Might to become "
            "a beautiful young woman for an hour. They punish whoever annoys "
            "them severely, sometimes reward from their hoards, invite "
            "passers-by to their moonlit crossroads dances and punish those "
            "who refuse. Each carries a pawn of Animal vis in its hooves. "
            "Anyone gathering vis or prying into the forest's secrets will "
            "meet them.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "fountain_of_youth",
        "The Fountain of Youth and the Stone of Merlin",
        inside=forest,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "A spring ringed with stones at the heart of the forest, in "
            "a glade with a Faerie aura of 5. Washing the face in it "
            "smooths an old person's wrinkles for a few hours, a faerie "
            "glamour no magus has yet learned to prolong or use. Merlin "
            "came here for solitude and met Viviane, the Lady of the "
            "Lake; tired of him, she put him into a deep sleep, and many "
            "think he sleeps still under the nearby pair of slabs called "
            "the Stone of Merlin. A drop of the fountain's water let "
            "fall on the stone turns to vapour, and the air fills with "
            "shadows and thunder.",
            "A magus following the Path of Aging may drink here for the second quest.",
        ),
        secrets="The drop on the stone is probably the first step of the rite "
        "that opens the Faerie regio where Merlin may lie sleeping.",
        levels=[
            Builder.level(
                "Merlin's sleeping place",
                0,
                "Faerie",
                enter="Perhaps by a rite that begins with fountain water dropped on the Stone of Merlin",
                notes="Rumoured; its aura is not given.",
            )
        ],
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "lake_comper",
        "Lake Comper and the Joyous Garden",
        inside=forest,
        realm="Faerie",
        summary=paragraphs(
            "Viviane's home deep in the forest. Merlin raised the Joyous "
            "Garden and the Crystal Castle there for her, peopled with faerie "
            "knights, ladies and maids, and where she is said to have "
            "raised Lancelot. She probably still lives in the Faerie regio "
            "that hides her estate; research suggests it can be found and "
            "entered on the night before Midsummer's Day. Given how she has "
            "treated suitors and great magicians, a senior magus risks "
            "being kept there, and one with the Curse of Venus is courting "
            "trouble.",
            "The lake yields up to 5 pawns of Aquam vis in a normal year; in "
            "a drought a local priest comes to dip a cross in the water for "
            "rain, and that season no vis can be gathered.",
        ),
        levels=[
            Builder.level(
                "The Joyous Garden and the Crystal Castle",
                0,
                "Faerie",
                enter="Perhaps on the night before Midsummer's Day",
                notes="Viviane's estate, with faerie knights, ladies and maids; aura not given.",
            )
        ],
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "bridge_of_secrets",
        "The Bridge of Secrets",
        inside=forest,
        summary=(
            "A bridge near the village of Beignon, about four miles south of "
            "Comper, where Lancelot and Guinevere are said to have shared "
            "their first kiss. The ruin that betrayal brought suggests Perdo "
            "vis may be had here on its anniversary, if anyone discovers how "
            "to harvest it."
        ),
        **RUMOURED,
    )
    _add(
        normandy,
        "barenton",
        "The Fountain of Barenton",
        inside=forest,
        summary=(
            "A spring about four miles west-south-west of the Fountain of "
            "Youth, sacred to the druids. Tales say that its water splashed "
            "on the stone called Merlin's Step calls up wild storms and a "
            "fierce knight in black armour. It is a source of Vim vis, held "
            "by the Tribunal as a tropaeum."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "faerie_mirror",
        "The Faeries' Mirror",
        inside=forest,
        realm="Faerie",
        summary=(
            "A small lake about four miles south of Barenton that the "
            "faeries use as a looking glass. If it has gone unused for a "
            "month, a little Imaginem vis can be gathered from it."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "valley_of_no_return",
        "The Valley of No Return",
        inside=forest,
        realm="Faerie",
        summary="A deep valley just past the Faeries' Mirror, where Morgan le "
        "Fay, Arthur's half-sister, imprisoned her faithless lover "
        "Guyomart at False Lover's Rock. Legend says no wrongdoer can "
        "leave it.",
        secrets="Only those unfaithful in love are actually held.",
        **KNOWN_REGION,
    )


# ---------------------------------------------------- Lordship of Penthièvre


def _penthievre(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    lordship = _add(
        normandy,
        "penthievre",
        "Lordship of Penthièvre",
        inside=region,
        summary=(
            "A barony along the rugged middle of the north coast that "
            "climbs inland over forested hills, thinly peopled. The Central "
            "Argoat inland is nearly all forest with a few small "
            "settlements: Loudéac, a crossroads market with two animal "
            "fairs a year; Moncontour under its castle where two valleys "
            "meet; Quintin among its flax fields, with the Long Rock menhir "
            "nearby and a small castle at Robien. Cistercian houses at "
            "Boquen, Quenécan and Gouarec, a Benedictine house in the Lorge "
            "Forest and St Briac's chapel at Bourbriac hide in the woods."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "rose_coast",
        "The Rose Coast",
        inside=lordship,
        summary=paragraphs(
            "The cliffs of pink granite, topped with moor, between St Brieuc "
            "Bay and Morlaix Bay, round small sandy beaches and creeks. Many "
            "of the oddly worn rocks look like beasts and people, and a few "
            "of them really were. Small islands lie offshore in great "
            "number. Tréguier stands on terraces between the Jaudy and the "
            "Guindy; beyond it the coast breaks into massive headlands split "
            "by deep clefts, and on the largest island nearby a dolmen "
            "stands on blue rock, for a giant hauled the whole isle here "
            "from south-west Wales.",
            "On a hill above the Trégastel headland stands the Dolmen of "
            "Kerguntuil, thought to be a giant turned to stone, which gave "
            "its name to a Diedne covenant destroyed in 1007. The Templars, "
            "it is rumoured at a Quaesitor's prompting, built along this "
            "coast to cleanse the Diedne taint: a round chapel at Lanleff in "
            "the eleventh century and Brélévenez church at Lannion on the "
            "Léguer in the twelfth. Behind the dunes north of the Léguer "
            "mouth lies the fifty-five-acre Quellen Marsh.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "brehat",
        "The Bréhat Isles",
        inside=lordship,
        aura=4,
        summary=paragraphs(
            "Two isles off the coast's eastern point, each about a mile "
            "across but deeply indented and almost touching, under a Magic "
            "aura of 4, with a mild, dry climate: pink cliffs on the wilder "
            "northern isle, low pink and grey sand and shingle on the east, "
            "and sea of many blues and greens over pink rocks bared only at "
            "low tide.",
            "At the far end is a deep cleft in the cliff. Once a year a "
            "maiden may drop a pebble into it: if it falls clean into the "
            "water she will marry within the year, and otherwise she waits "
            "a year for every bounce. The thrift clinging to the cleft holds "
            "Intellego vis, up to 5 pawns a year, but taking more than 3 "
            "spoils the prophecies for several years after.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "seven_isles",
        "The Seven Isles",
        inside=lordship,
        aura=4,
        summary=(
            "An archipelago east of Trégastel Head, far enough out to be "
            "troubled only by the seabirds of its high cliffs and the seals "
            "on the rocks below. Its clear waters, full of feathery weed and "
            "bright clinging creatures, usually yield 6 pawns of Herbam and "
            "5 of Animal vis a year, along with eels, crabs, lobsters and "
            "crayfish. Each isle has its own Magic aura: one 4, one 3, two "
            "2 and three 1."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "yaudet",
        "Yaudet",
        inside=lordship,
        summary=(
            "A round hilltop above the sea on the south side of the Léguer "
            "estuary, its humps and ditches the remains of a Romano-Gallic "
            "settlement. Locals sometimes glimpse oddly dressed men and "
            "women there and now and then wander into a regio. A surer way "
            "in lies a little along the coast at Plestin-les-Grèves, in the "
            "ruined Romano-Gallic bathhouse, through the alcove whose "
            "inscription says it held a statue of Teutates, or Mars."
        ),
        levels=[
            Builder.level(
                "The Romano-Gallic town",
                0,
                enter="By chance on the hill, or through the alcove of the bathhouse at Plestin-les-Grèves",
                notes="Its strangely dressed people are glimpsed from outside; aura not given.",
            )
        ],
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "long_rock",
        "The Long Rock",
        inside=lordship,
        summary=(
            "A menhir on a hilltop near Quintin that takes on a Faerie aura "
            "for a time, at intervals nobody can predict."
        ),
        **KNOWN_LOCALLY,
    )


# ----------------------------------------------------------- Léon


def _leon(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    leon = _add(
        normandy,
        "leon",
        "Lordship of Léon",
        inside=region,
        summary=paragraphs(
            "Brittany's north-western tip, woodland and bleak moor ringed on "
            "three sides by muddy estuaries, exposed beaches and islands; "
            "its far end is rightly called Finistère, Land's End. The coast "
            "of the Abers is drowned river mouths, small beaches and "
            "countless rocks awash at high tide; salt-laden westerlies "
            "poison the soil, and few people live there. The coast near "
            "Pontusval is known for lingering pagan ways tied to its many "
            "shipwrecks.",
            "Brest guards the north shore of its sheltered bay; the Crozon "
            "peninsula, all high cliffs, stacks and arches, closes it to the "
            "south. To the south and east the Arrée Mountains curve round "
            "the county.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "monsters_hole",
        "The Monster's Hole on Batz",
        inside=leon,
        summary=(
            "A low rock shelf on the isle of Batz, off St-Pol-de-Léon, "
            "covering the pit where St Paul the Aurelian penned the dragon "
            "that terrorised the island, after leading it there tamed on his "
            "stole. He founded a monastery on the island."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "barnenez",
        "The Barnenez Tumulus",
        inside=leon,
        summary=(
            "An enormous cairn of green, pink and grey stones across the "
            "estuary east of St-Pol. No door shows, but searchers find "
            "openings on the south-east side, each a passage of twenty to "
            "forty feet into one of eleven chambers."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "men_marz",
        "The Men-Marz Menhir",
        inside=leon,
        summary=(
            "A standing stone on Pontusval Point with a Celtic cross on top, "
            "where prayers are said from time to time, on a coast notorious "
            "for shipwrecks and the pagan practices bound up with them."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "tolente",
        "Tolente",
        inside=leon,
        status="Rumoured",
        known="In the Tribunal",
        summary="A Romano-Gallic town near Plougerneau, the westernmost village "
        "of the north coast, which vanished in 875 while Vikings "
        "attacked it; the village church stands on a pagan cairn. The "
        "Quaesitores investigate anyone known to be looking for a way "
        "in.",
        secrets="Druids almost certainly hid the town in a regio by magic.",
        levels=[
            Builder.level(
                "The hidden town",
                0,
                enter="Unknown; the Quaesitores watch for anyone seeking it",
                notes="Hidden since 875; aura not given.",
            )
        ],
    )
    ushant = _add(
        normandy,
        "ushant",
        "The Isle of Ushant",
        inside=leon,
        aura=7,
        summary=paragraphs(
            "A small island ten miles off Brittany's western tip, four "
            "miles by two and a half, its sheer cliffs rising 180 feet "
            "to a nearly flat top, ringed by treacherous currents and by "
            "reefs that sailors swear wander. The storm-beaten mainland "
            "opposite is empty. The fishing village of Lampaul lies on "
            "the gentler south-western shore; the rest is deserted but "
            "for Fudarus, the domus magna of House Tytalus, which "
            "crouches on the landward cliff edge in a Magic aura of 7. "
            "Without magic no one climbs the cliffs.",
            "Three Great Spirits bound into Fudarus's walls guard the "
            "island in turn (Magic Might 40, Auram), invisible and "
            "intangible, aware of all that happens on Ushant, and "
            "touchable by magic only by a caster who can sense them: "
            "Mogidell of mist and sea fog, a vast grey bird whose spread "
            "wings bring down the mist; Kerseenn of misdirection, always "
            "shifting between monstrous blends of man and beast; and "
            "Arnev of storms, a huge serpent with a horse's head. Each "
            "can match any non-Ritual spell of its kind up to level 40 "
            "at a point of Might a magnitude. Their presence makes 12 "
            "pawns of vis appear on the island each year, 4 each of "
            "Creo, Auram and Imaginem. They obey whoever bears the "
            "Circlet of the Primus, through an old pact that made them "
            "the island's genii loci.",
        ),
        secrets="Only the people of Fudarus know what form the spirits' vis takes.",
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "st_nerius",
        "St Nerius's Circle",
        inside=ushant,
        realm="Divine",
        aura=1,
        summary=(
            "A clean ring of grass just left of the gates of Fudarus, set in "
            "blackened, blasted ground: the place where St Nerius was "
            "martyred, with a Divine aura of 1. Every year on the "
            "anniversary a single blue flower of no known kind blooms in the "
            "burnt turf for a day. A few pious magi come to keep vigil and "
            "let no one pick it; Fudarus lets them come, does not interfere, "
            "and some of its magi have even joined the devotions with due "
            "solemnity."
        ),
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "camaret_menhirs",
        "The Menhirs of Camaret",
        inside=leon,
        aura=3,
        summary=(
            "An array of 143 standing stones in a Magic aura of 3 near "
            "Camaret, the tiny village at the west end of Crozon where "
            "pilgrims bound by sea for Rocamadour land and give thanks for "
            "their passage in a little chapel."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "morgat_caves",
        "The Caves of Morgat",
        inside=leon,
        summary=(
            "Many caves on Crozon's south shore, their roofs and walls "
            "brightly coloured by nature. Of the two groups of great "
            "caverns, one holds the cave called the Devil's Chamber and the "
            "other the cave called the Altar; many small caves can be "
            "reached only at low tide."
        ),
        **KNOWN_LOCALLY,
    )
    arree = _add(
        normandy,
        "arree",
        "The Arrée Mountains",
        inside=leon,
        summary=paragraphs(
            "The duchy's highest ground, an arc round the south and east of "
            "Léon, often lost in mist: rounded summits a little over 1,200 "
            "feet, mostly under deciduous forest thick with moss and fern, "
            "home to deer, boar and wolves, broken by bare saw-toothed crags, "
            "gorse and heather moor and a few sheltered fields. Its small, "
            "scattered folk mix Christian and pagan ways, and civilisation "
            "keeps to the edges: the Cistercians of Le Relecq to the east, a "
            "castle over the Élorn valley to the north-west, the church of "
            "King Salomon's martyrdom on the south-east fringe and the port "
            "of Landerneau at the head of the Élorn estuary.",
            "Exspectatio lies in a secluded valley of these mountains.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "exspectatio_site",
        "Exspectatio's Valley",
        inside=arree,
        summary=(
            "A secluded valley in the Arrée Mountains, about three days' "
            "journey from Fudarus, where the young magi of Atramentum founded "
            "their covenant in 1200 and the elder Tytali of Exspectatio took "
            "it from them a year later. Its aura is not given, but it is "
            "weaker than Fudarus's."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "huelgoat",
        "The Rocks of Huelgoat",
        inside=arree,
        realm="Faerie",
        summary=(
            "Piles of boulders left when the hamlets of Plouyé and Berrien "
            "went to war and pelted each other with stones that all fell "
            "between them. Nearby are the Devil's Cave, the huge Trembling "
            "Rock that rocks when pushed in the right spot, the Virgin's "
            "Kitchen, a chasm where the River Argent goes underground, a "
            "pool the faeries haunt and a cave where King Arthur once slept."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "youdig",
        "Youdig in the Yeun Elez",
        inside=arree,
        realm="Infernal",
        status="Rumoured",
        known="In the region",
        summary=(
            "A peat bog spreading east from the foot of St Michael's Mount "
            "near Brennilis, said to hide Youdig, a gate of Hell, which can "
            "be reached only in winter when mist lies on the bog. A short way "
            "to the north lies Mougau-Bihan, a giant's tomb: a covered walk of "
            "megaliths forty-five feet long."
        ),
    )


# ----------------------------------------------------------- Cornouaille


def _cornouaille(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    county = _add(
        normandy,
        "cornouaille",
        "County of Cornouaille",
        inside=region,
        summary=paragraphs(
            "A broad peninsula with points to north and south and wooded "
            "hills and valleys inland. At Locronan pilgrims climb the hill "
            "by the path St Ronan walked daily, fasting and barefoot. The "
            "Black Mountains, lower and softer than the Arrée across the "
            "broad Aulne valley, still shelter hermits' woods; from "
            "Ménez-Hom at their west end one sees Cornouaille, Crozon, the "
            "bay of Brest, St Matthew's Point and both ranges. Carhaix, the "
            "Roman Vorgium where seven roads met, is the only sizeable "
            "place for miles; further east lie the healing springs of "
            "Bulat-Pestivien and desolate Burthulet, so cold in winter that "
            "a demon froze to death there.",
            "Between Raz Point and Van Point opens the dreaded Bay of "
            "Troubled Souls, where the drowned wash ashore; south of it a "
            "twelve-mile shingle beach runs to the cliffs of Penmarch, with "
            "a yearly torchlit blessing of the sea halfway along.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "sein",
        "Sein Island",
        inside=county,
        summary=(
            "A low island off Raz Point, drowned by the highest tides, with "
            "two menhirs and a dolmen. The druids who died on the mainland "
            "were ferried here by boat for burial, and that keeps the locals "
            "away. Pomponius Mela wrote that nine virgin witches who could "
            "raise winds and storms lived on it."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "is",
        "The Drowned Town of Is",
        inside=county,
        status="Rumoured",
        known="In the region",
        summary=paragraphs(
            "King Gradlon's lovely capital in the sixth century, guarded "
            "from the sea by a dyke whose floodgates only the king could "
            "open. The Devil, as a handsome youth, seduced his daughter "
            "Dahut into stealing the key while Gradlon slept and opened the "
            "gates at high tide. The king fled with her on horseback, and "
            "when a voice told him to cast off the wicked woman he threw "
            "her into the flood; the waters drew back far enough for the "
            "townsfolk to escape, but Is sank. Gradlon founded Quimper in "
            "its place.",
            "Dahut became Marie-Morgane, an evil siren who still sings "
            "sailors to their deaths and peoples her sunken town with them. "
            "A Mass said in one of the drowned churches on Good Friday is "
            "said to banish her.",
        ),
    )
    _add(
        normandy,
        "karreg_an_tan",
        "Karreg an Tan",
        inside=county,
        summary=(
            "Fire Rock, a summit in the Black Mountains east of Ménez-Hom, "
            "where a rust-red lichen grows slowly on the stone; it is Ignem "
            "vis."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "rostrenen_hawthorn",
        "The Hawthorn of Rostrenen",
        inside=county,
        realm="Divine",
        summary=(
            "A hawthorn at Rostrenen in the east of the Black Mountains, "
            "dedicated to Our Lady, which blooms all year; it yields Herbam "
            "vis tainted by the Divine."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "corong_gorges",
        "The Gorges of Corong and Toul Goulic",
        inside=county,
        summary=(
            "Two gorges where a river vanishes under tumbled rocks, Corong's "
            "spilling out lower down in cascades, Toul Goulic's further "
            "east. Each has a temperamental genius loci, and the two have "
            "feuded so long neither remembers why; whichever has the upper "
            "hand has its river running above ground. Both would gladly end "
            "it and would reward whoever managed it without either seeming "
            "to give way."
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------------------------- Broërec


def _broerec(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    broerec = _add(
        normandy,
        "broerec",
        "Broërec",
        inside=region,
        summary=paragraphs(
            "Low forested plateaus cut by many rivers that widen into "
            "drowned estuaries on the coast; crops grow in the sheltered "
            "valleys, and the sea feeds the rest. By the Étel estuary a "
            "sailor's wife drops a crust into Ste Hélène's fountain "
            "and reads her husband's safe return in whether it floats "
            "or sinks; nearby, deaf petitioners sleep on St Cado's stone bed "
            "and pillow hoping for a cure.",
            "The Gulf of Morbihan is nearly closed by land, about twelve "
            "miles across and nine deep, fringed with mud and salt marsh and "
            "scattered with low islands. Inland Vannes stands on the Marle, "
            "and beyond it the Lanvaux Moors, a crescent of bare flaking "
            "rock dotted with megaliths; Ploëmel lies past them, founded by "
            "St Arthmael, who slew a dragon there. At Castennac, near the "
            "Cornouaille border, a statue the locals call their Venus serves "
            "lewd pagan rites; churchmen have thrown it in the river several "
            "times, and it always comes back.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "tumiac",
        "The Tumiac Tumulus",
        inside=broerec,
        summary=(
            "A mound on the arm of land south of the gulf from which Julius "
            "Caesar watched his fleet fight the Veneti, the strongest Gallic "
            "tribe: more than two hundred Gallic sailing ships against Roman "
            "galleys. Interesting relics very likely lie on the sea floor."
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        normandy,
        "gavrinis",
        "The Gavrinis Tumulus and Er Lanic",
        inside=broerec,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "A cairn about twenty feet high on an islet near the gulf's "
            "mouth, over a passage and a chamber roofed with huge slabs on "
            "uprights carved with spirals, cups and rings; the chamber is "
            "eight great slabs of a dark, fine-grained stone not found "
            "nearby. It has an evil name for dark magic done there long ago, "
            "and a Faerie aura of 3, and in the right conditions it opens on "
            "a dark Faerie realm.",
            "Just south, on the isle of Er Lanic, stones stand in a figure "
            "of eight, one ring drowned at high tide, in a Magic aura of 5.",
        ),
        levels=[
            Builder.level(
                "The dark Faerie realm",
                0,
                "Faerie",
                enter="Under the right circumstances, through the chamber",
                notes="Aura not given.",
            )
        ],
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "locmariaquer",
        "The Megaliths of Locmariaquer",
        inside=broerec,
        summary=(
            "A remarkable gathering of ancient monuments toward the end of "
            "the Rhuys peninsula. The greatest, once over sixty feet tall, "
            "lies broken in two; the slabs called the Merchants' Table are "
            "carved with crooks and an ox, so the place probably served old "
            "animal magic. Er-Grah, Mané-er-Hroech, Mané-Lud, Mané-Rethual, "
            "Kerlud and the Flat Stones are other dolmens of huge dressed "
            "and often carved stone, mostly a covered passage into a great "
            "chamber, likely giants' homes."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "quiberon",
        "Quiberon and Roh-en-Aod",
        inside=broerec,
        summary=(
            "A long isle cut off from the mainland only at high tide: dunes "
            "at the north, cliffs, caves and reefs pounded by the ocean on "
            "the west, long gentle beaches on the sheltered east, where "
            "twenty-two menhirs stand in rows. At the north end of the west "
            "cliffs the stone Roh-en-Aod has five cup-shaped hollows; women "
            "who tap them with hammers by night win fair winds for their "
            "husbands' boats, and Auram vis can be had from it, but only by "
            "a woman."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "belle_ile",
        "Belle-Île",
        inside=broerec,
        summary=paragraphs(
            "The largest Breton island, five miles out from Quiberon: a "
            "schist plateau cut by fast streams ending in creeks and "
            "small beaches, swept by westerly wind and rain, with trees "
            "only where sheltered. At Port-Goulphar on the south-west "
            "coast, bright algae gathering on the rocks of a deep, calm "
            "chasm are an unusual Herbam vis; a little further, the "
            "surf at the rocks called the Needles throws up foam that "
            "is Aquam vis.",
            "Two menhirs called Jean and Jeanne stand on a gorse moor in "
            "the north of the island, one of pale granite and one of "
            "dark schist: a betrothed couple turned to stone for not "
            "waiting for their wedding.",
        ),
        secrets="A suitable Hermetic ritual could restore Jean and Jeanne, who "
        "would be glad to join a covenant since their world is long "
        "gone. Jeanne is pregnant and gives birth three months after "
        "the spell ends, to a Gifted child with a close affinity for "
        "Terram.",
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "carnac",
        "Carnac",
        inside=broerec,
        aura=5,
        summary=paragraphs(
            "One of the mightiest magical sites in Mythic Europe: more "
            "than a thousand rough menhirs, from a child's height to "
            "over twenty feet, in broken avenues across the heath by the "
            "village of Carnac, on a scale that dwarfs Stonehenge. By "
            "day a Magic aura of 5 covers the heath, one of the largest "
            "the Order knows, rising to 6 or more on the avenues, with "
            "many regiones; the place is brighter and more real than the "
            "land round it, and its birds, flowers and beasts show odd "
            "cleverness, strange powers or speech. As the light goes the "
            "aura fades, and by night it is Infernal. No covenant has "
            "ever been built here, and none likely will be.",
            "The Order's legends set Trianoma's meeting with Diedne the "
            "Founder here on a bright summer afternoon, and here a "
            "fleeing remnant of the Diedne was hunted down and killed; "
            "some say that blood brought the curse. Locals credit "
            "faeries with the stones and try hedge charms to make them "
            "build houses overnight; the pious say St Cornelius, fleeing "
            "in his ox cart, prayed at the shore and God turned his "
            "faerie pursuers to stone. Most who live nearby agree that "
            "demons haunt it by night. Processions of the ancient dead "
            "are seen, and every Midsummer night the villagers bar "
            "themselves into St Cornelius's church to pray till dawn, "
            "for even the churchyard's aura turns Infernal 5.",
            "The Nains guard the stones' mysteries: child-sized, "
            "misshapen imps with filthy long hair, bandy goat legs and "
            "burning red eyes (Infernal Might 10, Animal), once korrigan "
            "corrupted by their own wickedness. They read the strange "
            "letters on the rocks that show only by starlight on "
            "moonless nights, dance orgies among the stones and vanish "
            "into regiones by dawn. They make moon-bright silver coins "
            "that vanish at daybreak to lure the greedy into ambush, "
            "conjure false vis that answers a simple Intellego Vim but "
            "melts away under closer study, and compel up to ten victims "
            "to dance with them till sunrise, often to death. They "
            "attack three to a victim, often with worse demons. Their "
            "unholy night is the first Wednesday in May, when they make "
            "blood sacrifice and the Infernal aura reaches 6; to come "
            "near then is suicide.",
            "Magi of Hermetic geometry and astrology come seeking "
            "insight, others suspect fertility magic, and a Breakthrough "
            "might unlock the stones. Jacques Vert of Merinita suggested "
            "the Nains were dead Diedne dreaming in faerie flesh; nobody "
            "believed him, and about fifty years ago he disappeared among "
            "the stones one moonless night, hunting the legendary, "
            "unnamed treasure of Carnac.",
        ),
        secrets="Rumours say Diedne fled into the regiones, or that the stones "
        "hold portals, like Mercere Portals, to other far-off stone "
        "rows, through which the surviving Diedne may one day return "
        "for revenge.",
        levels=[
            Builder.level(
                "The avenues",
                6,
                notes="Among the stones themselves the aura is 6 or higher by day, and many regiones are known.",
            ),
            Builder.level(
                "The heath by night",
                5,
                "Infernal",
                notes="After dusk the Magic aura gives way to an Infernal one; it reaches 6 on the first Wednesday in May.",
            ),
        ],
        **KNOWN_ORDER,
    )
    _add(
        normandy,
        "st_cados_pillar",
        "St Cado's Pillar and the Giant of Kerderf",
        inside=broerec,
        summary=(
            "North-east of Ploëmel, beside the petrified Giant of Kerderf, "
            "stands a lone pillar named for St Cado, which women who wish to "
            "conceive rub themselves against. The pillar yields Creo vis, "
            "of interest for what it shows of fertility cults, and perhaps "
            "a link to a magic that could undo the sterility a longevity "
            "ritual brings."
        ),
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------- County of Nantes


def _nantes(normandy: Normandy) -> None:
    region = normandy.places["brittany"]
    county = _add(
        normandy,
        "county_of_nantes",
        "County of Nantes",
        inside=region,
        summary=(
            "The country round Nantes on the Loire, hardly Breton at all: "
            "few Bretons live there, and its Frankish people feel closer to "
            "Anjou and Poitou. The road to Rennes runs through forest with "
            "little settlement; at Blain two minor trade roads cross, the "
            "old Roman one better than one would expect, and a leper house "
            "hides in the Gâvre Forest nearby. Redon, where several rivers "
            "meet, is the Vilaine's highest seaport and a market for a wide "
            "area."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        normandy,
        "st_just",
        "The Grey Stones of St Just",
        inside=county,
        aura=3,
        summary=(
            "Several groups of grey stones on the high ground by the "
            "village of St Just, north of Redon and west of the Vilaine, in "
            "a small Magic aura of 3."
        ),
        **KNOWN_REGION,
    )
    _add(
        normandy,
        "grande_briere",
        "The Grande Brière",
        inside=county,
        aura=1,
        summary=(
            "A huge peat marsh behind the coastal sands between the Loire "
            "and Vilaine estuaries, rich in fish, eels and wildfowl but "
            "almost empty of people, with a few firm islands. On one, "
            "Kerbourg in the south-west, stands a covered alley of megaliths "
            "with a weak Magic aura (its strength is not given). The fortress "
            "of Ranrouët is being built on the north side; Guérande overlooks "
            "the south-west edge, and on the rocky ridge between its salt "
            "marsh and the sea salt is worked in a small way."
        ),
        **KNOWN_LOCALLY,
    )


# ---------------------------------------------------------------- Fudarus


def _fudarus(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "The domus magna of House Tytalus and the westernmost covenant of "
        "Normandy, whose influence reaches across the whole Tribunal like a "
        "web. Tytalus the Founder lived here, as did his filia Pralix, "
        "founder of House Ex Miscellanea, and Tasgillia, corrupted by "
        "demons in the tenth century. Few magi of other Houses have ever "
        "entered its halls, though many have reached the island, and its "
        "secrecy and its members' schemes have given it a sinister name.",
        "Tytalus built it in 798 to defend the apprentice Hariste, whom he "
        "had stolen from his former pupil Pralix and loved; he trained her "
        "to a full maga in five years, but his refusal to show his love "
        "drove her away, and he held the magically raised fortress alone "
        "until he vanished. Hariste then claimed it and became the first "
        "Prima, and it has been the Primus's home ever since. In 961 House "
        "Guernicus caught Prima Tasgillia and many of the House in "
        "diabolism far from Fudarus; the new Prima Kalliste refused the "
        "Quaesitores and Flambeau hoplites entry, since the members left "
        "had been found clean, and when political pressure forced her to "
        "yield they found nothing. In the Schism War the Diedne came by sea "
        "and, unable to break in, laid siege with three mighty summoned "
        "spirits; after months Primus Klynoites wrested the spirits from "
        "them, destroyed his foes, and bound the spirits into the walls. "
        "Fudarus had sat with the Stonehenge Tribunal; as the only Breton "
        "covenant to survive the war, its move to Normandy in 1018 brought "
        "Brittany's rich vis into its hands, and the Tribunal favoured it "
        "in sharing the spoils.",
        "The covenant is a sprawling grey fortress in a semicircular wall "
        "on the very edge of Ushant's landward cliffs, and it spills down "
        "the cliff face: its towers hang upside down from buttresses at "
        "the top, reaching downward like the stone tendrils of a vast ivy. "
        "Most of its people live in the part that pours over the edge. "
        "Only the Primus's tower is occupied; by custom each Primus's tower "
        "is sealed by the successor, who builds a new one. Nine towers are "
        "sealed, one for each of the eight earlier Primi and one for "
        "Tytalus, and none but Tasgillia's has been entered since; some are "
        "thought to hold the ghosts or Twilight-changed remains of their "
        "owners. Harpax's tower has been building for twenty years and, "
        "thanks to Buliste, is nowhere near done, while Harpax devises ever "
        "cleverer ways to seal Buliste's tower and lock her out of her own "
        "sanctum.",
        "Visitors approaching by sea or land meet the defences of the Three "
        "Great Spirits, who take turns hiding the covenant from chance "
        "discovery. An invited guest or a Redcap stands facing the island, "
        "feet together and hands raised, and speaks the current password; "
        "the guarding spirit then opens a straight tunnel through its "
        "defences to the covenant. There are no steps or ropes, and the "
        "cliffs need magic to climb. Beside the gate is St Nerius's "
        "circle, where pious magi keep a yearly vigil undisturbed.",
        "The Heusaff family, an old Breton line, own Ushant and Lampaul, "
        "the fishing village whose catch is Fudarus's main supply; the "
        "fishermen have little to do with the family and know nothing of "
        "magi. A non-Tytalan magus must earn entry by meeting a challenge "
        "set by a Primus, usually some kind of conflict, and lodges in a "
        "tumbledown house outside the walls if he fails or refuses; every "
        "Tytalus has passed the House's Gauntlet and may enter. Membership "
        "carries no special honour in the House: any Tytalus with reason "
        "to join and the strength to make the members accept him may do "
        "so. Fudarus is an autocracy whose Primus decides everything; "
        "members act on their own initiative, but a Primus who feels his "
        "authority usurped punishes swiftly with the Rod of the Primus.",
        "For twenty-five years the two rival Primi, Buliste and Harpax, "
        "have been its only residents. Buliste was declared lost to Final "
        "Twilight and Harpax chosen in her place, but she returned a few "
        "years later, and the two have fought for the House ever since, "
        "evenly matched; the House gives both equal respect, leadership "
        "and rule of Fudarus. The other members withdrew to the vassal "
        "they renamed Exspectatio, remain members of Fudarus, and come back "
        "for books and for laboratory work in its stronger aura; Kybella "
        "casts the Aegis of the Hearth each year for both Primi, since "
        "neither trusts the other to. Within the walls the Primi stoop to "
        "pettiness; on the Order's stage their feud is as vicious as any "
        "between beloved rivals. Fudarus has two vassals, one being "
        "Exspectatio, which has its own vassal, Atramentum Renatus in "
        "Burgundy; both are bound by harsh oaths and must fight hard at "
        "the Tourney to pay their feudal dues, and Fudarus repays them with "
        "generous political support. It has a long record of vassals that "
        "win independence and then founder, and prefers no House in its "
        "vassals.",
        "Invisible servant spirits fill every room and do the cleaning, "
        "mending, carrying and cooking, each at the last task the wearer of "
        "the Circlet set it, so the fortress seems empty and silent and "
        "needs few servants, labourers or teamsters. There is a chef, an "
        "alchemist and a glassblower for the laboratories, a barber-surgeon "
        "who rules the covenant's regimen of health, and two craftsmen. The "
        "large turb is split evenly between the Primi and wears swatches "
        "of their colours, Harpax's green and Buliste's purple; warped by "
        "the aura, each side cannot see anyone wearing a substantial amount "
        "of the other's colour, Buliste included for Harpax's men, so a "
        "green cloak lets a man stab one of Buliste's grogs unopposed. "
        "Wearing both colours cancels the effect.",
    )
    what_matters = _lines(
        "Vis: 12 pawns a year manifest on Ushant through the Three Great Spirits, 4 each of Creo, Auram and Imaginem (seisin)",
        "Vis: Brittany's rich vis fell largely to Fudarus after 1018; Harpax governs it as Lord Heusaff",
        "Vis: stripped of a legacy lease in 1172, granted to House Mercere, after Atlax of Tytalus read a Redcap's messages here",
        "Income: Lampaul's fishing, through the Heusaff family",
        "Income: the feudal dues of two vassals, Exspectatio and one other, under harsh oaths",
        "Library: the House's great collection, used by Exspectatio's magi (no books named)",
        "Enchantment: the Rod of the Primus controls every room's light, heat, doorways, smells, sounds and textures, and can make the effect follow one person (held by Harpax)",
        "Enchantment: the Circlet of the Primus commands the servant spirits and the Three Great Spirits (worn by Buliste)",
        "Defence: the Three Great Spirits, Magic Might 40 each, bound into the walls since the Schism War",
        "Defence: sheer 180-foot cliffs, wandering reefs and currents, and a password tunnel for guests",
        "Boon: Natural Fortress, Magical Fortress, Mystical Allies (the spirits), Informants (Buliste's spies)",
        "Hook: House Covenant; Fractured Council (the two Primi); Divided Loyalty (the colour-blind turb)",
        "Mundane: Fudarus's agents run the Paris Dyers' Guild, a coup against Florum",
        "Tension: the feud of the two Primi, to be settled before the coming Grand Tribunal, where only one may sit",
        "Tension: Buliste holds the House's network of spies and the Order's respect; Harpax holds the covenant, its vis and coin, and more sway in Normandy",
        "Tension: the Traitor of Confluensis bears a key said to weaken Fudarus's defences",
        "Tension: accused in 1200 of ruining Atramentum by founding an artificers' guild at Le Conquet",
        "Hook: visitors must win entry by a Primus's challenge; an easy task is an insult, a hard one a compliment",
        "Hook: a covenant Fudarus favours may be given some of its colour-blind grogs",
    )
    challenges = paragraphs(
        "Challenges to enter Fudarus. Chance decides which Primus hears of "
        "a visitor and so sets the test, which is suited to the visitor's "
        "abilities: too easy a task is a subtle insult of the kind Tytali "
        "relish and shows the welcome to expect, a hard one is a "
        "compliment, and a visitor who fails but bears himself well may "
        "still be asked in.",
        "Buliste's challenges are mostly philosophical or plainly magical: "
        "argue convincingly that the Code of Hermes is outdated and harms "
        "the Order; talk a Lampaul villager into an act he thinks morally "
        "repugnant; work a ritual he does not know from a casting tablet "
        "without passing out; open the main gate without moving a muscle.",
        "Harpax's challenges are mostly physical: fight a magically made "
        "beast; pin one of Fudarus's grogs in a wrestling bout; catch at "
        "least seven of twelve spears thrown from the ramparts; fetch "
        "something from Lampaul before a water clock runs out.",
    )
    items = paragraphs(
        "The Rod and the Circlet of the Primus, made long ago at Hariste's "
        "order, are the covenant's great treasures and the tokens of the "
        "House's leadership. The Rod (six effects, R: Touch, D: Conc, T: "
        "Structure, Pen 0, unlimited uses, any number kept up at once but "
        "one begun a round) varies a room's light from darkness to "
        "blinding glare (MuIg 25), its heat from freezing to baking (MuIg "
        "25), opens arches or shuts doorways between rooms (MuTe 30), and "
        "fills it with sweet or foul smells (CrIm 25), soothing or "
        "clamorous noise (CrIm 25), and furnishings soft as down or sharp "
        "as thorns (MuIm 25). The Circlet (Control Spirit, ReVi 55, R: "
        "Arc, D: Conc, T: Ind, Pen 20, unlimited uses) commands one task of "
        "any spirit present or to which the wearer has an Arcane "
        "Connection; it is inscribed with the names of all Fudarus's "
        "servant spirits, and affects any whose Might is below its "
        "Penetration.",
    )
    hidden = _lines(
        "Lord Heusaff is Harpax in disguise: he stole the identity from Buliste's sanctum along with the Rod when she seemed dead.",
        "The Three Great Spirits obey the Circlet's wearer through the old pact, not because the Circlet compels them; their vis's form is known only inside Fudarus.",
        "Harpax is offering generous terms to new vassals for pawns in his feud, and wants the pieces of a pre-Hermetic item; it is a Diedne relic, Buliste has steered him to it, and she means to frame him once he has it.",
        "Harpax has a merchant of Fudarus's spy network jailed on false charges; Buliste sends a spirit to help whoever frees him.",
        "Porphyrion of Tytalus, an archmage who came from the Rome Tribunal three years ago, may mean to take the House for himself; a third contender is the one thing that would make the Primi work together.",
        "The Primi will not stoop to a High Crime or Wizard's War against each other, though either may put the other in mortal danger.",
    )
    fudarus = b.covenant(
        "Fudarus",
        tribunal=tribunal,
        founded=798,
        place=normandy.places["ushant"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(challenges, items),
        secrets=hidden,
        aura=7,
        season="Autumn",
    )
    normandy.covenants["fudarus"] = fudarus
    _fudarus_magi(normandy, b, fudarus)
    b.book(
        fudarus,
        "The library of Fudarus",
        "Other",
        description=(
            "The domus magna's library, gathered since 798; the book names "
            "none of its books. The magi of Exspectatio, still members of "
            "Fudarus, come back regularly to use it and to take books away, "
            "and its specialised laboratories draw them too. Exspectatio's "
            "oath as vassal gives it access to its liege's books."
        ),
    )


def _fudarus_magi(normandy: Normandy, b: Builder, fudarus: Covenant) -> None:
    m = normandy.magi
    m["buliste"] = b.magus(
        "Buliste",
        covenant=fudarus,
        house=TYTALUS,
        age=84,
        summary=paragraphs(
            "Prima of House Tytalus, Buliste filia Bulcis, who led the "
            "House for twenty years before a long Twilight left her "
            "seeming dead. She wore the Circlet of the Primus as it "
            "began, Harpax could not take it from her, and she wears it "
            "still, setting the covenant's invisible spirits to plague "
            "her rival: they pull stones from his unfinished tower, put "
            "ground glass in his food, sew up his clothes, and play "
            "countless other tricks that border on the deadly. More "
            "important to the House, she runs Fudarus's vast web of "
            "spies and speaks mind to mind with several of its key "
            "agents, through her mastery of Mentem and a collection of "
            "fixed Arcane Connections; that keeps her respected across "
            "the Order, though she has little power in the Normandy "
            "Tribunal. Her followers, the Fideli, rally to her purple "
            "banner. Her challenges to visitors are philosophical or "
            "magical.",
            "She looks a regal woman in her sixties, stout but not fat, "
            "in violet satin and white Breton lace, with a very "
            "expressive face. Her plainest Twilight scar is that her "
            "kindness and her anger can both be felt, the one gently, "
            "the other painfully. Older than Harpax, she has the more "
            "raw power, but several Twilights have hemmed in her magic.",
        ),
        secrets="She is steering Harpax toward a Diedne relic so she can frame "
        "him with it.",
        traits={"Petty": 3, "Generous": 2, "Caring": -1},
    )
    m["harpax"] = b.magus(
        "Harpax",
        covenant=fudarus,
        house=TYTALUS,
        age=70,
        summary=paragraphs(
            "Primus of House Tytalus, the tenth, Harpax filius Bulcis, "
            "who always felt held back by his elder 'sister', fought her "
            "hard for the House and lost. When she seemed to die he "
            "barely paused before breaking into her sanctum and taking "
            "the Rod of the Primus, and took over her role as Lord Heusaff. He "
            "torments her with the Rod: one day her sanctum is hot "
            "enough to melt her candles, the next she must break ice on "
            "her washbasin.",
            "He reads Tribunal politics and his fellow Tytali's plots "
            "better than Buliste, governs the covenant's wealth in vis "
            "and coin, keeps the oaths of its two vassals, and has "
            "bought many magi's loyalty; his Decimi, who wear the tenth "
            "Primus's sigil, are the stronger party in Normandy. Without "
            "the spies he cannot steer much of the House's business. "
            "More careful and more varied than his sister, he has a "
            "wider stock of spells and enchantments but less depth in "
            "the Arts. His challenges to visitors are physical.",
            "As himself he is a distinguished, stick-thin man who looks "
            "about fifty and suffers some arthritis; he keeps other "
            "guises too, and may first be met as a butler, a sentry or "
            "a tinker. His obsession and sigil is plurality, and his "
            "Twilight scar makes the cut of his clothes drift through "
            "the day, always in his forest green.",
        ),
        secrets="As Lord Heusaff he takes the shape of a dashing young nobleman, "
        "and has played the part so well that he has had to cultivate "
        "unpleasant habits to keep off marriageable women.",
        traits={"Mercurial": 3, "Impulsive": 1, "Sincere": 1},
    )


# ------------------------------------------------------------- Exspectatio


def _exspectatio(normandy: Normandy, b: Builder, tribunal: Tribunal) -> None:
    summary = paragraphs(
        "A covenant of six Tytalus magi in a secluded valley of the Arrée "
        "Mountains, about three days from Fudarus. When it was plain that "
        "the feud of Harpax and Buliste would not end soon, and since "
        "Tytalan rivalries are personal and private, the other magi of "
        "Fudarus looked for somewhere else to live. Their eye fell on "
        "Atramentum, a vassal Fudarus had sponsored only the year before, "
        "conveniently near: in 1201 the elder Tytali turned out its two "
        "founders and moved in, and renamed it Exspectatio, waiting in hope "
        "or in dread. Exspectatio paid the evicted magi, Helios and Gulo "
        "Midusulfis, with the means to found a new covenant in Burgundy on "
        "a former legacy of Fudarus, Atramentum Renatus, which is now "
        "Exspectatio's own vassal.",
        "All but one of its magi are at least forty years past "
        "apprenticeship, and they are technically still members of "
        "Fudarus. It is legally Fudarus's vassal, but the oath of fealty is "
        "very generous, since its magi helped write it, and one or more of "
        "them is often away at Fudarus using the library or a specialised "
        "laboratory. Its two leading magi are Adanos and Kybella, who stand "
        "on opposite sides of the Primi's feud.",
    )
    what_matters = _lines(
        "Vis: none given; the covenant draws on Fudarus's resources",
        "Library: Fudarus's, to which its members return for books",
        "Aura: not given; weaker than Fudarus's, so its magi do some laboratory work at the domus magna",
        "Oath: vassal of Fudarus on unusually generous terms, which its own magi helped draft",
        "Vassal: Atramentum Renatus in Burgundy, founded by the magi it evicted",
        "Boon: Seclusion (a hidden mountain valley)",
        "Hook: Fractured Council (Adanos for Harpax, Kybella for Buliste); Superiors (Fudarus)",
        "Tension: Cynics say the founders of Atramentum were duped into preparing the site for them",
        "Hook: Iasper's family, the Foutins, and his taste for turmoil",
    )
    hidden = _lines(
        "Iasper, looking for a way into the Cabal of the Laden Cart, draws a crossroads faerie of the passage between life and death, which blurs the border: corpses walk, the living fall into a death-like pallor, and Iasper must be freed from his own death-state to break the spell.",
        "When one of Iasper's Foutin cousins gets into trouble (perhaps a grog of the player covenant), Iasper smooths things over with the authorities by framing the player magi in a grand plot to destabilise the region, then comes to them contrite to help untangle the mess without admitting his part.",
        "Kybella founded the Cabal of the Laden Cart and hunts the Ankeu to imprison Death itself.",
    )
    exspectatio = b.covenant(
        "Exspectatio",
        tribunal=tribunal,
        founded=1201,
        place=normandy.places["exspectatio_site"],
        summary=summary,
        what_matters=what_matters,
        secrets=hidden,
        unnamed_magi=3,
        season="Summer",
    )
    normandy.covenants["exspectatio"] = exspectatio
    _exspectatio_magi(normandy, b, exspectatio)
    b.book(
        exspectatio,
        "The library of Exspectatio",
        "Other",
        description=(
            "The book names no books here. Exspectatio's magi rely on the "
            "library of Fudarus, of which they remain members, and fetch "
            "books from it on their regular visits. Adanos's own Lab Texts, "
            "The Mole's Work, are among the books held for the Tribunal."
        ),
    )


def _exspectatio_magi(normandy: Normandy, b: Builder, home: Covenant) -> None:
    m = normandy.magi
    m["adanos"] = b.magus(
        "Adanos Lutorum",
        covenant=home,
        house=TYTALUS,
        age=57,
        summary="Of House Tytalus, the youngest of Exspectatio's founders, with "
        "the blood of an earth spirit and a deep affinity for soil, "
        "stone and clay: over seven feet tall, entirely hairless, with "
        "skin like rock. He has backed Harpax staunchly ever since "
        "Buliste refused to take him as her apprentice. In any contest, "
        "of blows, words or magic, he lets his opponent wear herself out "
        "against his unbreakable defences and then strikes one crushing "
        "blow. He is Iasper's master, and wrote The Mole's Work, Terram "
        "Lab Texts now held for the Tribunal. Looks about forty.",
        secrets="Like Valerian of Confluensis, he is reputed to belong to the "
        "Guernicus Terrae cult.",
        traits={"Humorless": 2, "Unswerving": 3, "Loyal to Harpax": 3},
    )
    m["kybella"] = b.magus(
        "Kybella",
        covenant=home,
        house=TYTALUS,
        age=68,
        summary="Of House Tytalus, a leading member of the Titanoi, the House's "
        "cult of theurgists, and a close friend of Prima Buliste. She "
        "keeps up the enchantments that hold Fudarus's spirits in check "
        "and casts its Aegis of the Hearth each year for both Primi. "
        "She specialises in genii loci and searches every place she "
        "stays for signs of one. Her filius Helios, of Atramentum "
        "Renatus, is a theurgist too. Looks about fifty.",
        secrets="Twelve years ago a Twilight showed her Death reaping Europe, "
        "kings, bishops, commoners and magi alike, and she founded the "
        "Cabal of the Laden Cart to trap Death and hold it to ransom. "
        "The other members assume she is one of them but never know "
        "which disguise is hers. With another theurgist of her line she "
        "is obsessed with the Ankeu, and her agents listen across "
        "Brittany for anyone who hears its cart.",
        traits={"Loyal to Buliste": 3, "Suspicious": 1},
    )
    m["iasper"] = b.magus(
        "Iasper filius Adanos",
        covenant=home,
        house=TYTALUS,
        age=26,
        summary=(
            "Of House Tytalus, the youngest of Exspectatio, four years past "
            "his Gauntlet, a thin man with long shaggy black hair and "
            "stubble whose clothes are always immaculate. He is all "
            "contrasts: his magic is at once tightly harnessed and "
            "unpredictable, and he prides himself on self-control while "
            "delighting in turmoil and chaos, with a knack for Terram from "
            "his master. He holds that reined chaos is the road to knowing "
            "oneself and, unlike most Tytali, stirs up conflict beyond his "
            "power to control, taking the vagaries of chance as lessons. He "
            "means no harm but seldom thinks what his deeds do to others. "
            "He is close to his family, the Foutins, a large clan of local "
            "brawlers and ne'er-do-wells who are not quite criminals but "
            "find trouble easily, and he seeks to join the Cabal of the "
            "Laden Cart."
        ),
        traits={"Argumentative": 2, "Self-Disciplined": 2, "Brave": 1},
    )


# ------------------------------------------------------------- vis tenure


def _vis(normandy: Normandy) -> None:
    fudarus = normandy.covenants["fudarus"]
    t = normandy.tenure
    t(
        "Ushant: the Three Great Spirits, 4 Creo, 4 Auram and 4 Imaginem a year",
        fudarus,
        "seisin",
        notes="On Fudarus's own island; its form is known only inside the covenant.",
    )
    t(
        "Fountain of Barenton (Brocéliande): Vim",
        None,
        "tropaeum",
        notes="A druids' spring; amount not given.",
    )
    t(
        "Lake Comper (Brocéliande): up to 5 Aquam a year",
        None,
        "tropaeum",
        notes=f"None in a drought year, when a priest blesses the lake for rain. {INFERRED}",
    )
    t(
        "The Faeries' Mirror (Brocéliande): a little Imaginem",
        None,
        "tropaeum",
        notes=f"Only if the mirror has gone unused for a month. {INFERRED}",
    )
    t(
        "The Singing Stones (Arguenon estuary): Imaginem",
        None,
        "luctatio",
        notes=f"The stones must be struck just so with a stone of their kind. {INFERRED_CONTEST}",
    )
    t(
        "The oak of Pléchâtel: vis in large acorns",
        None,
        "tropaeum",
        notes=f"A few acorns; the Art is not given. {INFERRED}",
    )
    t(
        "Bréhat Isles: thrift in the cleft, up to 5 Intellego a year",
        None,
        "tropaeum",
        notes=f"Taking more than 3 ruins the cleft's prophecies for years. {INFERRED}",
    )
    t(
        "The Seven Isles: 6 Herbam and 5 Animal a year",
        None,
        "tropaeum",
        notes=f"From the weeds and creatures of the clear waters. {INFERRED}",
    )
    t(
        "Karreg an Tan (Black Mountains): Ignem lichen",
        None,
        "tropaeum",
        notes=f"The rust-red lichen grows slowly. {INFERRED}",
    )
    t(
        "The hawthorn of Rostrenen: Herbam, Divinely tainted",
        None,
        "tropaeum",
        notes=f"Dedicated to Our Lady and always in bloom. {INFERRED}",
    )
    t(
        "Roh-en-Aod (Quiberon): Auram",
        None,
        "luctatio",
        notes=f"Only a woman can gather it. {INFERRED_CONTEST}",
    )
    t(
        "Port-Goulphar (Belle-Île): Herbam algae",
        None,
        "tropaeum",
        notes=INFERRED,
    )
    t(
        "The Needles (Belle-Île): Aquam sea foam",
        None,
        "tropaeum",
        notes=INFERRED,
    )
    t(
        "St Cado's pillar (near Ploëmel): Creo",
        None,
        "tropaeum",
        notes=INFERRED,
    )


# ------------------------------------------------------- the mundane world


def _lords(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    w["duke_of_brittany"] = b.lord(
        "Duke of Brittany",
        title="duke",
        wealth="Wealthy",
        seat="Rennes",
        ruler="Peter I of Dreux",
        place=p["brittany"],
        arms=Arms("Ermine"),
        summary=paragraphs(
            "Peter I of Dreux holds the duchy by his marriage to Alice, heir "
            "of the old ducal house, and rules as regent for her son. "
            "Brittany won free of the English crown after King John was "
            "rumoured to have murdered his nephew Arthur of Brittany, the "
            "duke whom Philip Augustus had backed against him. Rennes, "
            "famous for holding out against Normandy, is the capital now; "
            "Nantes was Alain Crookbeard's and Vannes Nominoé's.",
            "The arms shown are the plain ermine Brittany bears in later "
            "years; Peter's own shield is the checky of Dreux with an "
            "ermine quarter. The duchy holds over six hundred mottes and "
            "forty great castles, and the barons were bloodily brought to "
            "heel by Henry II.",
        ),
    )
    duke = w["duke_of_brittany"]
    w["penthievre"] = b.lord(
        "Baron of Penthièvre",
        title="baron",
        seat="Lamballe",
        answers_to=duke,
        place=p["penthievre"],
        summary=(
            "Lord of the barony along the rugged middle of the north coast "
            "and the forested hills behind it, from his seat at Lamballe on "
            "the trade road from Rennes to St Brieuc. His land is sparsely "
            "peopled, and Bréhat, the Seven Isles and the Rose Coast lie "
            "within it."
        ),
    )
    w["fougeres"] = b.lord(
        "Baron of Fougères",
        title="baron",
        seat="Fougères castle",
        answers_to=duke,
        place=p["county_of_rennes"],
        summary=(
            "Lords of the strong castle on a spit of land in a bend of the "
            "Nançon below the town of Fougères, long the frontier with "
            "France. Raoul II of Fougères led the Breton barons who rose "
            "against Henry II's takeover; his castle was razed after a "
            "three-month siege, but he survived and began rebuilding at "
            "once."
        ),
    )
    w["leon"] = b.lord(
        "Count of Léon",
        title="count",
        seat="St-Pol-de-Léon",
        answers_to=duke,
        place=p["leon"],
        summary=(
            "Lord of Brittany's poor north-western tip, woodland and bleak "
            "moor round muddy estuaries and wreck-strewn coasts, with his "
            "home at the see of St-Pol-de-Léon. Brest castle, lately "
            "strengthened on Roman foundations, guards his bay."
        ),
    )
    w["heusaff"] = b.lord(
        "Lord Heusaff of Ushant",
        title="landed",
        wealth="Poor",
        seat="Ushant",
        place=p["ushant"],
        summary="Head of the Heusaff family, an ancient Breton line that owns "
        "the Isle of Ushant and its only village, Lampaul, whose fishing "
        "keeps the family. The lord is a dashing young nobleman with "
        "some off-putting habits; the fishermen have little to do with "
        "the family and do not know its 'castle' is a magical place.",
        secrets="Lord Heusaff is Harpax, Primus of House Tytalus, in a deep "
        "cover disguise taken from Buliste. Through the role he governs "
        "Fudarus's vis and coin.",
    )


def _sees(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    see = "Bishop's cathedral"
    w["bishop_of_dol"] = b.church(
        "Bishop of Dol",
        church=see,
        order="secular clergy",
        place=p["county_of_rennes"],
        summary=(
            "The see of St Samson, one of the seven Welsh founders and a "
            "station of the Tro Briez, in the small town of Dol on a cliff "
            "above the marsh. A fortified cathedral to the saint is being "
            "built. Mount Dol, just north, is shunned by Christians."
        ),
    )
    w["bishop_of_st_malo"] = b.church(
        "Bishop of St Malo",
        church=see,
        order="secular clergy",
        place=p["county_of_rennes"],
        founded=1144,
        summary=(
            "The see seated since 1144 in the Church of St Vincent, when the "
            "new town on the point took the name of St Malo and old Aleth, "
            "where the Welsh St Maclou converted the Gauls in the sixth "
            "century, was rededicated to St Servan. A station of the Tro "
            "Briez."
        ),
    )
    w["bishop_of_st_brieuc"] = b.church(
        "Bishop of St Brieuc",
        church=see,
        order="secular clergy",
        place=p["county_of_rennes"],
        summary=(
            "The see of St Stephen's Cathedral in St Brieuc, a station of "
            "the Tro Briez for St Broch, whose blessed fountain is beside "
            "the place where he lived."
        ),
    )
    w["bishop_of_treguier"] = b.church(
        "Bishop of Tréguier",
        church=see,
        order="secular clergy",
        place=p["penthievre"],
        summary=(
            "The see of the Church of St Tugdual at Tréguier, on terraces "
            "between the Jaudy and the Guindy; a station of the Tro Briez."
        ),
    )
    w["bishop_of_st_pol"] = b.church(
        "Bishop of St-Pol-de-Léon",
        church=see,
        order="secular clergy",
        place=p["leon"],
        summary=(
            "The bishopric St Paul the Aurelian founded; its twelfth-century "
            "cathedral bears his name; a station of the Tro "
            "Briez. The saint tamed the dragon of Batz with his stole. When "
            "Duke Mark refused him one of the seven bells that summoned his "
            "castle, a fisherman soon landed a great fish with a bell in its "
            "mouth and gave it to the saint; that bell and the others are "
            "lost."
        ),
    )
    w["bishop_of_quimper"] = b.church(
        "Bishop of Quimper",
        church=see,
        order="secular clergy",
        place=p["cornouaille"],
        summary=(
            "The see of St Corentine, first bishop of King Gradlon's new "
            "capital and a station of the Tro Briez. The saint lived on a "
            "magic fish caught daily from the river: he ate half and threw "
            "the rest back, and next morning it was whole. The fish (Divine "
            "Might 2, Animal) may still be nearby and might show itself to a "
            "deserving seeker."
        ),
    )
    w["bishop_of_vannes"] = b.church(
        "Bishop of Vannes",
        church=see,
        order="secular clergy",
        place=p["broerec"],
        summary=(
            "The see of the Cathedral of St Peter in Vannes, the largest "
            "town of Brittany, and the station of the Tro Briez for St "
            "Patern."
        ),
    )
    w["bishop_of_rennes"] = b.church(
        "Bishop of Rennes",
        church=see,
        order="secular clergy",
        place=p["county_of_rennes"],
        summary=(
            "The church of St Peter inside the walls of Rennes, the ducal "
            "capital, founded in the sixth century on a Romano-Gallic "
            "temple."
        ),
    )
    w["bishop_of_nantes"] = b.church(
        "Bishop of Nantes",
        church=see,
        order="secular clergy",
        place=p["county_of_nantes"],
        summary=(
            "The cathedral of Nantes, a place of martyrdom: in 843 pagan "
            "raiders slaughtered the bishop and his whole congregation "
            "there. Nantes is a political and church centre."
        ),
    )


def _abbeys(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    abbey = "Monastery or nunnery"
    chapel = "Chapel"
    rennes, penthievre = p["county_of_rennes"], p["penthievre"]
    leon, cornouaille = p["leon"], p["cornouaille"]
    broerec, nantes = p["broerec"], p["county_of_nantes"]
    w["st_melaine"] = b.church(
        "Abbey of St Mélaine",
        church=abbey,
        order="Benedictine",
        place=rennes,
        summary="An abbey within the walls of Rennes.",
    )
    w["st_magloire"] = b.church(
        "Abbey of St Magloire, Léhon",
        church=abbey,
        order="Benedictine",
        place=rennes,
        founded=850,
        summary=(
            "A monastery beside a castle at Léhon, just up the Rance from "
            "Dinan, founded by Nominoé in 850. Badly damaged by the Vikings "
            "and soon rebuilt, it has lately been enlarged in the new style "
            "by Geoffroy of Corseul."
        ),
    )
    w["st_savior_dinan"] = b.church(
        "Basilica of St Savior, Dinan",
        church="Large urban church",
        place=rennes,
        summary=(
            "Raised in the twelfth century by a crusader in thanks for his "
            "safe return from the Holy Land, it shows eastern features of "
            "building unknown elsewhere in these parts."
        ),
    )
    w["paimpont"] = b.church(
        "Monastery of Paimpont",
        church=abbey,
        place=p["broceliande"],
        summary=(
            "A small monastery set inside Brocéliande to counter the "
            "forest's other powers, with little success so far."
        ),
    )
    w["marmoutier_lamballe"] = b.church(
        "Priory of Marmoutier, Lamballe",
        church=abbey,
        order="Benedictine (Marmoutier)",
        place=penthievre,
        summary=(
            "A priory at Lamballe, the Baron of Penthièvre's seat, which "
            "also has a church of Our Lady."
        ),
    )
    w["our_lady_fougeres"] = b.church(
        "Chapel of Our Lady, Fougères",
        church=chapel,
        place=rennes,
        summary=(
            "A chapel in Fougères whose statue shows Our Lady suckling the "
            "Christ child; some mothers praying before it have been "
            "miraculously helped."
        ),
    )
    w["langon_chapels"] = b.church(
        "Churches of Langon",
        church="Parish church",
        place=rennes,
        summary=(
            "Langon's church of St Peter and its chapel of St Agatha, whose "
            "fabric takes in the walls of a Romano-Gallic temple of Venus; "
            "the Young Ladies stand on the moor nearby."
        ),
    )
    w["templars_rose_coast"] = b.church(
        "Templar chapels of Lanleff and Brélévenez",
        church=chapel,
        order="Knights Templar",
        place=p["rose_coast"],
        summary="A round chapel built by the Templars at Lanleff in the "
        "eleventh century and the church of Brélévenez at Lannion in "
        "the twelfth, raised to cleanse the coast of the Diedne's "
        "diabolic taint.",
        secrets="Rumour says a Quaesitor suggested the building to the Templars.",
    )
    w["our_lady_of_haut"] = b.church(
        "Chapel of Our Lady of Haut",
        church=chapel,
        place=penthievre,
        summary=(
            "A chapel two miles south-east of Moncontour where an unusual "
            "number of healing saints are petitioned: St Mamertus for colic, "
            "St Livertin and St Eugenia for headaches, St Leobinus for the "
            "eyes, St Méen for madness, St Hubert for sores and St "
            "Houarniaule for fear. It is hung with offerings, mostly wooden "
            "carvings of the body parts healed, and has a Dominion aura of "
            "5, higher than a chapel's usual."
        ),
    )
    w["our_lady_quintin"] = b.church(
        "Our Lady of Deliverance, Quintin",
        church="Parish church",
        place=penthievre,
        summary=(
            "The main church of Quintin, whose statue of Our Lady of "
            "Deliverance draws expectant mothers praying for her protection "
            "in childbirth."
        ),
    )
    w["argoat_cistercians"] = b.church(
        "Cistercians of Boquen, Quenécan and Gouarec",
        church=abbey,
        order="Cistercian",
        place=penthievre,
        summary=(
            "Three Cistercian monasteries hidden deep in the forests of the "
            "Central Argoat."
        ),
    )
    w["lorge"] = b.church(
        "Monastery of the Lorge Forest",
        church=abbey,
        order="Benedictine",
        place=penthievre,
        summary="A Benedictine house hidden in the Lorge Forest.",
    )
    w["bourbriac"] = b.church(
        "Chapel of St Briac, Bourbriac",
        church=chapel,
        place=penthievre,
        summary="A forest chapel where St Briac is prayed to for those who suffer fits.",
    )
    w["st_matthew"] = b.church(
        "Abbey of St Matthew's Point",
        church=abbey,
        order="Benedictine",
        place=leon,
        summary=(
            "A sixth-century monastery at the western point of Léon, with a "
            "village grown round it. It once held the head of St Matthew, "
            "a relic that calms storms at sea, but no one has seen it for "
            "centuries."
        ),
    )
    w["daoulas"] = b.church(
        "Abbey of Daoulas",
        church=abbey,
        order="Augustinian canons",
        place=leon,
        founded=500,
        summary=(
            "An abbey on the east shore of the bay of Brest, founded in 500 "
            "by followers of St Columba, destroyed by Vikings in the tenth "
            "century and lately rebuilt; a few men live there under the "
            "Rule of St Augustine."
        ),
    )
    w["landevennec"] = b.church(
        "Abbey of Landévennec",
        church=abbey,
        place=leon,
        summary=(
            "The abbey St Guénolé founded in the fifth century at the east "
            "end of the Crozon peninsula."
        ),
    )
    w["le_relecq"] = b.church(
        "Abbey of Le Relecq",
        church=abbey,
        order="Cistercian",
        place=p["arree"],
        summary="A Cistercian monastery on the eastern edge of the Arrée Mountains.",
    )
    w["king_salomon_church"] = b.church(
        "Church of King Salomon's Martyrdom",
        church="Parish church",
        place=p["arree"],
        summary=(
            "A small church on the south-eastern fringe of the Arrée "
            "Mountains where King Salomon was martyred in the ninth century."
        ),
    )
    w["locronan"] = b.church(
        "Monastery of Locronan",
        church=abbey,
        order="Benedictine",
        place=cornouaille,
        summary=(
            "A monastery by the pilgrimage of Locronan, where pilgrims "
            "climb the hill on St Ronan's daily path; it lodges them, stands "
            "in a forest the druids held sacred, and takes in brothers from "
            "other houses who need a change of scene."
        ),
    )
    w["st_gildas"] = b.church(
        "Abbey of St-Gildas-de-Rhuys",
        church=abbey,
        place=broerec,
        summary=(
            "The monastery St Gildas founded in the sixth century on the "
            "southern arm of the Gulf of Morbihan. Peter Abélard withdrew "
            "here and found it wild and full of dangerous beasts, its "
            "language strange and ugly, and its monks unruly."
        ),
    )
    w["st_cado_chapel"] = b.church(
        "Chapel of St Cado",
        church=chapel,
        place=broerec,
        summary=(
            "A chapel by the Étel estuary where the deaf spend a night on a "
            "stone bed with a stone pillow, hoping for a cure."
        ),
    )
    w["st_cornelius"] = b.church(
        "Church of St Cornelius, Carnac",
        church="Parish church",
        place=p["carnac"],
        summary=(
            "The village church of Carnac, where the people bar the doors "
            "and pray till dawn every Midsummer night while the dead process "
            "outside; even its churchyard then falls under an Infernal aura "
            "of 5."
        ),
    )
    w["josselin_virgin"] = b.church(
        "Our Lady of Josselin",
        church=chapel,
        place=broerec,
        summary=(
            "A wooden statue of the Virgin found in a bramble bush near "
            "Josselin castle on the Oust. Our Lady once came as a ragged "
            "beggar asking for water; the village women set their dogs on "
            "her, and their shouting turned to dogs' howls. Every Pentecost "
            "the women must beg forgiveness before the statue or the curse "
            "returns."
        ),
    )
    w["redon"] = b.church(
        "Abbey of St Savior, Redon",
        church=abbey,
        order="Benedictine",
        place=nantes,
        founded=832,
        summary="The abbey founded in 832 at Redon, where several rivers meet.",
    )
    w["guerande"] = b.church(
        "Church of St Aubin, Guérande",
        church="Parish church",
        place=nantes,
        summary=(
            "Built over a baptistery used in converting the local pagans, "
            "with a Merovingian sarcophagus in its crypt."
        ),
    )


def _towns(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    duke = w["duke_of_brittany"]
    lord, church = "Noble lord", "Church"
    rennes, penthievre = p["county_of_rennes"], p["penthievre"]
    leon, cornouaille = p["leon"], p["cornouaille"]
    broerec, nantes = p["broerec"], p["county_of_nantes"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "rennes",
        "Rennes",
        "A small city on the Vilaine at the heart of the duchy, known for "
        "its resistance to Normandy and now the ducal capital, with the "
        "church of St Peter and the Abbey of St Mélaine inside its walls.",
        charter=lord,
        answers_to=duke,
        place=rennes,
    )
    town(
        "nantes",
        "Nantes",
        "A city on the Loire, important in Roman times and before, now a "
        "political and church centre with a Frankish people closer in "
        "feeling to Anjou and Poitou than to Brittany. Alain Crookbeard "
        "made it his capital.",
        charter=lord,
        answers_to=duke,
        place=nantes,
    )
    town(
        "vannes",
        "Vannes",
        "Brittany's largest town, on the Marle near the Gulf of Morbihan, "
        "Nominoé's capital in the ninth century, with its Cathedral of St "
        "Peter.",
        charter=lord,
        answers_to=duke,
        place=broerec,
    )
    town(
        "st_malo",
        "St Malo",
        "A small port on the point where the drowned Rance meets the sea, "
        "pushed out toward the water and walled against the Vikings; a "
        "bishop's seat since 1144, beside old Aleth, now St Servan.",
        charter=church,
        place=rennes,
    )
    town(
        "dinan",
        "Dinan",
        "A small port at the head of the Rance, with the crusader's "
        "Basilica of St Savior; the castle and abbey of Léhon are just "
        "upriver, and Roman Corseul five miles west.",
        charter=lord,
        place=rennes,
    )
    town(
        "dol",
        "Dol",
        "A small town on a cliff at the south edge of the marsh, where a "
        "fortified cathedral of St Samson is being built; Mount Dol rises "
        "to the north and the menhir of Champ-Dolent stands to the south.",
        charter=church,
        place=rennes,
    )
    town(
        "st_brieuc",
        "St Brieuc",
        "A small port on a plateau cut by the Gouet and the Gouëdic, with "
        "a weekly market, two fairs a year, St Stephen's Cathedral and St "
        "Broch's fountain.",
        charter=church,
        place=rennes,
    )
    town(
        "fougeres",
        "Fougères",
        "A town clinging to steep slopes above its baron's castle, on the "
        "old border with France in a forest crowded with megaliths.",
        charter=lord,
        ruler="Baron of Fougères",
        place=rennes,
    )
    town(
        "lamballe",
        "Lamballe",
        "The Baron of Penthièvre's seat on the one trade road through the "
        "forest of Hunaudaye, with a church of Our Lady and a priory of "
        "Marmoutier.",
        charter=lord,
        ruler="Baron of Penthièvre",
        answers_to=w["penthievre"],
        place=penthievre,
    )
    town(
        "treguier",
        "Tréguier",
        "A town on terraces above the Jaudy and the Guindy, round the "
        "Church of St Tugdual.",
        charter=church,
        place=penthievre,
    )
    town(
        "lannion",
        "Lannion",
        "A small town on the Léguer, with the Templars' church of Brélévenez.",
        charter=lord,
        place=penthievre,
    )
    town(
        "loudeac",
        "Loudéac",
        "A small market town at a central crossroads, the trading hub of a "
        "wide forest country, with an animal fair twice a year.",
        charter=lord,
        place=penthievre,
    )
    town(
        "moncontour",
        "Moncontour",
        "A market town under a castle on a spur where two valleys meet, "
        "near the chapel of Our Lady of Haut.",
        charter=lord,
        place=penthievre,
    )
    town(
        "quintin",
        "Quintin",
        "A small market town on terraces of the Gouët valley, where flax "
        "is grown, with Our Lady of Deliverance and the Long Rock nearby "
        "and a small castle at Robien.",
        charter=lord,
        place=penthievre,
    )
    town(
        "st_pol",
        "St-Pol-de-Léon",
        "The Count of Léon's home and the see of St Paul the Aurelian, "
        "across the water from the isle of Batz.",
        charter=lord,
        answers_to=w["leon"],
        place=leon,
    )
    town(
        "brest",
        "Brest",
        "A port at the mouth of the Élorn on the north shore of a nearly "
        "landlocked bay; the Romans fortified it, and the castle built "
        "there in the eleventh century has lately been strengthened.",
        charter=lord,
        place=leon,
    )
    town(
        "landerneau",
        "Landerneau",
        "The main port of the Arrée country, at the head of the Élorn estuary.",
        charter=lord,
        place=leon,
    )
    town(
        "lampaul",
        "Lampaul",
        "Ushant's only settlement, a small fishing village owned by the "
        "Heusaff family; its catch is Fudarus's main supply.",
        charter=lord,
        ruler="Lord Heusaff",
        answers_to=w["heusaff"],
        place=p["ushant"],
    )
    town(
        "quimper",
        "Quimper",
        "The chief town of Cornouaille, founded by King Gradlon after Is "
        "drowned; the see of St Corentine.",
        charter=lord,
        place=cornouaille,
    )
    town(
        "carhaix",
        "Carhaix-Plouguer",
        "The Roman Vorgium, grown where seven roads met in the valley "
        "between the Arrée and the Black Mountains, and the only sizeable "
        "settlement for miles.",
        charter=lord,
        place=cornouaille,
    )
    town(
        "redon",
        "Redon",
        "The highest port on the Vilaine for seagoing ships, where several "
        "rivers meet, a market for a wide area, round the Abbey of St "
        "Savior.",
        charter=church,
        place=nantes,
    )
    town(
        "blain",
        "Blain",
        "A small castle and a busy market where two minor trade roads "
        "cross on the forest road from Nantes to Rennes.",
        charter=lord,
        place=nantes,
    )
    town(
        "guerande",
        "Guérande",
        "A settlement overlooking the south-west edge of the Grande Brière, "
        "with St Aubin's church and small salt workings on the ridge "
        "toward the sea.",
        charter=lord,
        place=nantes,
    )


def _factions(normandy: Normandy, b: Builder) -> None:
    w = normandy.world
    p = normandy.places
    w["foutins"] = b.faction(
        "The Foutins",
        faction="Family",
        place=p["brittany"],
        wants="A good brawl and a way out of the trouble that follows",
        offers="Muscle and local connections; their kinsman Iasper smooths things over",
        summary=(
            "Iasper of Exspectatio's mundane family, a big clan of local "
            "roustabouts and ne'er-do-wells: not criminals by nature, but "
            "gifted at finding trouble. Iasper stays close to them and is "
            "often called on to settle things with the authorities."
        ),
    )
    w["laden_cart"] = b.faction(
        "The Cabal of the Laden Cart",
        faction="Other",
        decides="Its leader",
        place=p["brittany"],
        ruler="Kybella of Tytalus (secretly)",
        wants="To trap Death and hold it to ransom, or to defeat disease and age",
        rules="Members are anonymous, meet in disguise or not at all, and write rather than meet",
        summary="A secret cabal of Tytalus magi, from Normandy and beyond, "
        "formed to entrap Death. Some members mean it literally, others "
        "as a fight against disease and the ravages of time. Its agents "
        "listen across Brittany for anyone who hears the creak of the "
        "Ankeu's cart, and a member soon calls on whoever does.",
        secrets="Kybella founded it twelve years ago after a Twilight vision of "
        "Death reaping all Europe; the others assume she is a member but "
        "never know which disguise is hers. She and another theurgist "
        "of her line mean to imprison the Ankeu. If they succeed, Death "
        "will not take kindly to being tamed; the cabal may already have "
        "caught a night spirit that is not Death, which must be freed "
        "far from Brittany. Iasper is seeking to join.",
    )
    w["fudarus_spies"] = b.faction(
        "The Web of Fudarus",
        faction="Other",
        decides="Its leader",
        ruler="Prima Buliste",
        place=p["brittany"],
        wants="Knowledge of everything that moves in the Order and the Tribunal",
        offers="Information, unusual goods and services, mercenaries",
        summary="House Tytalus's vast network of spies, informants, mercenaries "
        "and suppliers of unusual goods and services, run from Fudarus "
        "and the root of much of the House's strength. Agents rarely "
        "know one another: in Paris two merchant partners scheme against "
        "each other for patrons who are secretly the same magus, and the "
        "Dyers' Guild, won from Florum's agents, is Fudarus's.",
        secrets="Buliste controls the network and speaks mind to mind with "
        "several key agents; Harpax, without it, cannot steer much of "
        "the House's business and has jailed at least one agent on false "
        "charges.",
    )
    w["decimi"] = b.faction(
        "The Decimi",
        faction="Other",
        decides="Its leader",
        ruler="Primus Harpax",
        place=p["ushant"],
        wants="Harpax recognised as sole Primus of House Tytalus",
        summary=(
            "The Tytali who back Harpax and wear the tenth Primus's sigil, "
            "the stronger party in the Normandy Tribunal, where Harpax buys "
            "loyalty with Fudarus's vis and coin. Choosing a side is a "
            "matter of taste rather than merit, and Tytali of the two camps "
            "praise their champions so loudly that outsiders who try to "
            "mediate suspect a joke at their expense."
        ),
    )
    w["fideli"] = b.faction(
        "The Fideli",
        faction="Other",
        decides="Its leader",
        ruler="Prima Buliste",
        place=p["ushant"],
        wants="Buliste recognised as sole Prima of House Tytalus",
        summary=(
            "The Tytali loyal to Buliste's purple banner, strongest across "
            "the Order as a whole, where her web of spies keeps her at the "
            "centre of Fudarus's power. Normandy's Tytali have mostly "
            "declared for one Primus or the other but leave the two to "
            "settle it between themselves."
        ),
    )


# --------------------------------------------------------------- stats

P = Profile


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


def _ability(name: str, ability: str) -> tuple[str, dict[str, str]]:
    return (name, {"ability": ability})


#: Each magus the book sketches without a stat block, by character id.
PROFILES: dict[str, Profile] = {
    "buliste": P(
        strong="int pre com",
        arts={"Me": 7, "Vi": 4, "Re": 4, "In": 3, "Im": 3, "Cr": 2},
        abilities={
            "Intrigue": (4, "House Tytalus"),
            "Leadership": (3, "spies"),
            "Folk Ken": (2, "agents"),
            "Etiquette": 2,
            "Organization Lore: House Tytalus": 2,
        },
        virtues=[
            "Hermetic Prestige",
            ("Social Contacts", {"group": "Fudarus's spies"}),
            _art("Affinity with {art}", "mentem"),
            _art("Puissant {art}", "mentem"),
            "Twilight Prone",
            "Beloved Rival (Major)",
        ],
        reputations={"Prima of House Tytalus (Hermetic)": 5},
        native="Breton",
    ),
    "harpax": P(
        strong="int com per",
        arts={"Mu": 5, "Re": 5, "Im": 5, "Ig": 3, "Te": 3, "Vi": 3, "Cr": 3},
        abilities={
            "Intrigue": (4, "Normandy Tribunal"),
            "Guile": (4, "disguises"),
            "Etiquette": (3, "nobles"),
            "Bargain": (2, "vis"),
            "Leadership": 2,
            "Area Lore: Normandy Tribunal": 2,
        },
        virtues=[
            "Hermetic Prestige",
            _art("Affinity with {art}", "muto"),
            _ability("Puissant {ability}", "guile"),
            "Inventive Genius",
            "Beloved Rival (Major)",
            "Arthritis",
            "Dark Secret",
        ],
        reputations={"Primus of House Tytalus (Hermetic)": 5},
        native="Breton",
    ),
    "adanos": P(
        strong="sta str int",
        weak="com pre",
        arts={"Te": 8, "Re": 4, "Pe": 3, "Mu": 3, "Cr": 2},
        abilities={
            "Magic Lore": (3, "earth spirits"),
            "Brawl": 2,
            "Penetration": 3,
        },
        virtues=["Large", "Disfigured"],
        native="Breton",
    ),
    "kybella": P(
        strong="int per pre",
        arts={"Vi": 7, "Re": 5, "Me": 4, "In": 4, "Au": 3, "Cr": 2},
        abilities={
            "Magic Lore": (4, "genii loci"),
            "Awareness": (2, "spirits"),
            "Intrigue": 2,
        },
        virtues=[
            "Hermetic Theurgy",
            "Second Sight",
            _art("Affinity with {art}", "vim"),
            "Visions",
            "Obsessed (Minor)",
            "Secretive",
        ],
        native="French",
    ),
}


def stats(normandy: Normandy) -> None:
    """Iasper's printed stat block, then generated stats for the other
    magi of Brittany."""
    b = normandy.b
    b.stats(normandy.magi["iasper"], IASPER)
    for key, profile in PROFILES.items():
        apply(b, normandy.magi[key], profile)


IASPER: dict[str, Any] = {
    "characteristics": {
        "intelligence": 3,
        "perception": -1,
        "presence": 2,
        "communication": 0,
        "strength": 0,
        "stamina": 2,
        "dexterity": -1,
        "quickness": -2,
    },
    "size": 0,
    "confidence": (2, 6),
    "decrepitude": (0, 0),
    "warping": (0, 4),
    "virtues_flaws": [
        "The Gift",
        "Hermetic Magus",
        "Flexible Formulaic Magic",
        ("Affinity with {art}", {"art": "rego"}),
        "Clear Thinker",
        "Harnessed Magic",
        ("Minor Magical Focus", {"focus": "turmoil"}),
        ("Puissant {ability}", {"ability": "concentration"}),
        ("Puissant {art}", {"art": "terram"}),
        "Self-Confident",
        "Chaotic Magic",
        "Meddler (Major)",
        "Close Family Ties",
        "Incomprehensible",
        "Weird Magic",
    ],
    "traits": {"Argumentative": 2, "Self-Disciplined": 2, "Brave": 1},
    "abilities": [
        ("Artes Liberales", 3, "literature"),
        ("Brawl", 2, "fist"),
        ("Living Language: Breton", 3, "arguments"),
        ("Concentration", 2, "Rego"),
        ("Finesse", 2, "Terram"),
        ("Etiquette", 1, "politeness"),
        ("Living Language: French", 5, "Norman"),
        ("Dead Language: Latin", 4, "Hermetic"),
        ("Leadership", 1, "brow-beating"),
        ("Magic Lore", 1, "earth spirits"),
        ("Magic Theory", 4, "Terram"),
        ("Area Lore: Normandy", 1, "hostilities"),
        ("Parma Magica", 1, "Mentem"),
        ("Penetration", 1, "Terram"),
        ("Philosophiae", 1, "debating"),
    ],
    "arts": {
        "Creo": 4,
        "Intellego": 2,
        "Muto": 2,
        "Perdo": 2,
        "Rego": 10,
        "Animal": 2,
        "Aquam": 6,
        "Auram": 6,
        "Corpus": 3,
        "Herbam": 0,
        "Ignem": 3,
        "Imaginem": 5,
        "Mentem": 5,
        "Terram": 6,
        "Vim": 4,
    },
    "spells": [
        ("Chaos of the Angry Waves", "ReAq", 30, 0),
        ("Confusion of the Insane Vibrations", "ReIm", 30, 0),
        ("Confusion of the Numb Will", "ReMe", 15, 0),
        ("Crest of the Earth Wave", "ReTe", 20, 0),
        ("Panic of the Trembling Heart", "CrMe", 15, 0),
        ("Prying Eyes", "InIm", 5, 0),
        ("The Earth's Carbuncle", "ReTe(Mu)", 15, 0),
        ("Wielding the Invisible Sling", "ReTe", 10, 0),
    ],
    "notes": (
        "Self-Confident is his House Virtue. The book prints Concentration "
        "2+2 and Terram 6+3, the bonuses being his Puissant Concentration "
        "and Puissant Terram. Combat: fist Init -2, Attack +1, Defense 0, "
        "Damage 0; Soak +2. Appearance: thin, unshaven, with long, unkempt "
        "black hair, yet always impeccably dressed."
    ),
}
