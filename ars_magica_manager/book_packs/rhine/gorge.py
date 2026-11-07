"""The Rhine Gorge (Chapters 11 and 12): the middle Rhine between
Mainz and Cologne as the book's ready-made saga, in paraphrase. The
Gorge and its sites, the towns, castles and toll-lords of the river,
the three archbishops where no earlier part made them, the curse as a
threat whose stages lay out the saga's plot, the people a new covenant
meets, and the factions of the book's saga chapter, with the Order of
Odin left as undecided as the book leaves it.

Supernatural inhabitants (Hatto's shade, the Loreley, Red-Hame, the
gladiators) live in the summary of the place they haunt; the four lost
covenants live in the summaries of the places where they stood."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...arms import Arms
from ..builder import Builder, Secrets, more_secrets, paragraphs, titled

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Rhine

ARMS_MAINZ = Arms("Gules", charge="Wheel", charge_tincture="Argent")
ARMS_COLOGNE = Arms("Argent", charge="Cross", charge_tincture="Sable")
ARMS_TRIER = Arms("Argent", charge="Cross", charge_tincture="Gules")
ARMS_PALATINE = Arms("Sable", charge="Lion", charge_tincture="Or")
ARMS_TEUTONIC = Arms("Argent", charge="Cross", charge_tincture="Sable")
ARMS_FRANKFURT = Arms("Gules", charge="Eagle", charge_tincture="Argent")

TOLLS = (
    "Only the greatest nobles, the archbishops among them, hold imperial leave "
    "to take a 'just' toll; the imperial rates are a penny for a small rowing "
    "boat of five or fewer, two for a large rowing boat or fishing vessel, four "
    "for a small ship of ten tons or less, eight for a single-masted ship and "
    "twelve for a ship of two masts or more. Two dozen vessels or more pass a "
    "station each day, so a station brings in ten shillings a day or better, "
    "enough to feed a couple of hundred peasants or keep a castle; but a toll "
    "needs real force behind it, and captains pass word of weak stations and "
    "run those that ask too much."
)


def _add_to(record: Neighbour, more: str, hidden: Secrets = "") -> None:
    """Add the Gorge's paragraph to a record another part made, and
    `hidden` to its secrets."""
    record.summary = paragraphs(record.summary, more)
    record.secrets = more_secrets(record.secrets, hidden)


def build(rhine: Rhine) -> None:
    valley = rhine.places.get("rhine_valley")
    mainz, cologne, trier = _archbishops(rhine, valley)
    gorge = _gorge(rhine, valley)
    _gorge_places(rhine, gorge, valley)
    lords = _lords(rhine, gorge, valley, mainz, trier)
    _towns(rhine, gorge, valley, mainz, cologne, trier, lords)
    _churches(rhine, gorge, cologne)
    _threat(rhine, gorge)
    _people(rhine)
    _factions(rhine, gorge, cologne)


# -- the archbishops --


def _archbishops(
    rhine: Rhine, valley: Neighbour | None
) -> tuple[Neighbour, Neighbour, Neighbour]:
    """The three archbishops whose lands meet in the Gorge: the records
    an earlier part made, or made here from this chapter's facts."""
    b = rhine.b
    mainz = rhine.world.get("archbishop_of_mainz")
    if mainz is None:
        mainz = b.church(
            "Archbishop of Mainz",
            summary=paragraphs(
                "Siegfried II holds the see of Mainz and with it the office of "
                "Archchancellor of the Empire. He takes customs duties at Mainz "
                "and just tolls at Bingen's Burg Klopp, and holds Moseburg and "
                "Burg Rheinstein besides; the counts of Bolanden and the barons "
                "of Rüdesheim are his vassals.",
                "Two of his predecessors matter to the Gorge: Hatto II, the "
                "tenth-century builder of the Mouse Tower whom legend has eaten "
                "alive by mice, and Rudbrecht, who claimed and sanctified the "
                "land of the burnt covenant of Rudiaria.",
            ),
            church="Archbishop's cathedral",
            order="secular clergy",
            ruler="Siegfried II",
            place=valley,
            arms=ARMS_MAINZ,
        )
        rhine.world["archbishop_of_mainz"] = mainz
    cologne = rhine.world.get("archbishop_of_cologne")
    if cologne is None:
        cologne = b.church(
            "Archbishop of Cologne",
            summary="Engelbert I holds the see of Cologne and the office of "
            "Archchancellor of Italy. He takes customs duties at Cologne and "
            "just tolls at Schloss Fürstenberg, Burg Drachenfels and Burg "
            "Rheineck, and his great castle stands directly over the "
            "Drachenfels cave. A pious man, he leads the Holy Vehm.",
            secrets=[
                titled(
                    "Gymir and the Holy Vehm",
                    "Gymir, the demon prince of the North, is working its way into "
                    "the Holy Vehm.",
                ),
                titled(
                    "Storyguide Notes",
                    "If the book's future holds, the archbishop is murdered in 1225 "
                    "at the demon's contriving.",
                ),
            ],
            church="Archbishop's cathedral",
            order="secular clergy",
            ruler="Engelbert I",
            place=valley,
            arms=ARMS_COLOGNE,
        )
        rhine.world["archbishop_of_cologne"] = cologne
    trier = rhine.world.get("archbishop_of_trier")
    if trier is None:
        trier = b.church(
            "Archbishop of Trier",
            summary=paragraphs(
                "Dietrich I holds Trier, taking customs duties there, and the "
                "city of Koblenz with its just tolls, as well as Burg "
                "Erembertstein and Burg Treis; the count of Veldenz is his vassal.",
                "His see is the Order's worst enemy on the middle Rhine: Trier's "
                "churchmen drove the covenant of Treverorum from the city in 1172, "
                "and his predecessor led the mundane army that razed Rheinstein "
                "on Pfalz Island in 1200.",
            ),
            church="Archbishop's cathedral",
            order="secular clergy",
            ruler="Dietrich I",
            place=valley,
            arms=ARMS_TRIER,
        )
        rhine.world["archbishop_of_trier"] = trier
    return mainz, cologne, trier


# -- the Gorge and its places --


def _gorge(rhine: Rhine, valley: Neighbour | None) -> Neighbour:
    gorge = rhine.b.place(
        "The Rhine Gorge",
        summary=paragraphs(
            "Below Mainz the valley closes in under forested hills. A poor "
            "road follows the banks at least as far as Bingen and Rüdesheim, "
            "but nearly everything travels by water, and in the middle, at the "
            "Loreley, the banks rise into cliffs. Between Bingen and Koblenz "
            "more than a dozen castles stand, with more a-building, because "
            "the narrow river lets a castle force a toll on the heavy "
            "traffic; the map is a chessboard on which nobles trade and "
            "conquer castles for their toll positions, and the worst of the "
            "minor lords levying 'unjust' tolls are plain robber-barons.",
            TOLLS,
            "The river's two great hazards are the Bingen Hole and the "
            "Loreley rapids; nearly half the merchants carry their goods "
            "overland from Rüdesheim to Lorch to avoid the Hole, and some now "
            "as far as Kaub, where the count of Katzenelnbogen taxes them. "
            "Here the lands of the archbishops of Mainz, Cologne and Trier "
            "meet, and two ancient faerie courts face each other across the "
            "water; Trier's Roman remains lie up the Mosel and the "
            "Westerwald, where Siegfried slew Fafnir, to the east. Four "
            "covenants have stood here and all four have fallen, the last two "
            "so badly that the Tribunal of 1200 banned magic in the Gorge for "
            "twenty years. That ban has now run out.",
        ),
        secrets=[
            titled(
                "The seventy-seven years",
                "Students of the Tribunal's records notice that each lost covenant "
                "fell within exactly eleven Tribunals, seventy-seven years, of its "
                "founding: the root of the tale that the Gorge is cursed, officially "
                "idle speculation.",
            ),
            titled(
                "Storyguide Notes",
                "By the middle of the century a dozen toll stations stand between "
                "Mainz and Cologne, and in the Interregnum of the 1250s they double "
                "in four years.",
            ),
        ],
        inside=valley,
        known="In the Order",
    )
    rhine.places["rhine_gorge"] = gorge
    return gorge


def _gorge_places(rhine: Rhine, gorge: Neighbour, valley: Neighbour | None) -> None:
    b = rhine.b
    places = rhine.places

    places["rudesheim_bromserburg"] = b.place(
        "Rüdesheim and the Brömserburg",
        ruined=True,
        summary=paragraphs(
            "The site of Rudiaria, the first covenant of the Gorge, on the "
            "right bank opposite Bingen some twenty miles below Mainz. "
            "Rudiaria was founded in 892 with the First Tribunal's "
            "sponsorship and the grant of every magical site on the Rhine "
            "between Mainz and Cologne, a Flambeau-leaning house dogged by "
            "reports of malefic doings; a charge of diabolism against its "
            "magus Eginolf went unproven in 962, and in 969 the place burned "
            "in what looked like a magical catastrophe, every magus dead or "
            "missing, while a crippling famine gripped the region. Its lesson "
            "to later founders: do not deal with demons.",
            "Nothing could be salvaged, and Archbishop Rudbrecht of Mainz "
            "claimed and sanctified the land. The magi's keep was rebuilt as "
            "the squat square Brömserburg, long held by a minor family of "
            "Mainz's vassals, and a sizeable village grew round it; the "
            "town's name probably comes from the covenant or the archbishop. "
            "Redcap Crumena's note of 1032 AA spoke of a fortress partly "
            "visible from Bingen with covenant boatmen at its dock; only the "
            "fortress is still true, hardly a trace of magic remains, and of "
            "the four sites this is the least promising.",
            "The Brömsers have their own sorrow: Hans Brömser, taken on the "
            "Second Crusade, vowed his only daughter to the Church for his "
            "freedom; Mechthild, who loved a young knight of Bolanden, could "
            "not face the convent and drowned herself in the Rhine, and he "
            "built a chapel on the hill in her memory. Her restless ghost "
            "still troubles the family, and Thibaud the Fat, the present "
            "baron, quietly asks learned strangers for help.",
        ),
        secrets=[
            titled(
                "Rudiaria's old dungeons",
                "The old dungeons of Rudiaria beneath the castle were merely bricked "
                "up and forgotten, and may hold Hermetic treasures and traces of its "
                "black past.",
            ),
            titled(
                "A captive demon",
                "Were the baron to open Rudiaria's old dungeons he might loose a "
                "captive demon on the district.",
            ),
            titled(
                "Storyguide Notes",
                "Mechthild's ghost has no realm or Might given. In the Infernal "
                "reading of the curse Rudiaria sold its souls for seventy years of "
                "power, held Hatto II in thrall, tried to cheat and burned, and the "
                "famine and Hatto's madness both trace back to it.",
            ),
        ],
        inside=gorge,
    )

    places["rupertsberg"] = b.place(
        "Rupertsberg",
        summary=(
            "The hill above Bingen on which Hildegard founded her monastery in "
            "the middle of the twelfth century; it looks down on the town and on "
            "the Nahe's meeting with the Rhine."
        ),
        inside=gorge,
        realm="Divine",
    )

    places["mauseturm"] = b.place(
        "The Mäuseturm",
        summary=paragraphs(
            "A slender half-ruined tower on a small island at the mouth of "
            "the Bingen Hole, built in the tenth century by the grasping "
            "Archbishop Hatto II of Mainz to squeeze tolls from the river. "
            "The tale runs that in a famine the starving begged him for his "
            "hoarded corn; he shut them in an empty barn and burned it, "
            "laughing that the mice were squeaking in his corn, whereupon "
            "thousands of mice poured out, chased his boat to the tower and "
            "ate him alive. Nobody lives there, sailors cross themselves as "
            "they pass, and none has landed in decades.",
            "Hatto's shade still holds the tower: an Infernal spirit of Might "
            "30 (Mentem), a ragged man-shaped shard of darkness with a twisted "
            "mitred face, wholly insubstantial and beyond any weapon, kept in "
            "being by hate (Hateful +6, Merciless +4, Brave +3, Int +1). It "
            "lurks unseen in the shadows (Perception and Awareness against 12, "
            "or 9 by day), fills up to ten people with a dread of the island "
            "that with repetition drives them mad or kills them with fright, "
            "the fate of anyone who spends a night there, and its chill touch "
            "(Initiative +3, Attack +6, dodged only with Brawl) takes a "
            "Fatigue level and gives it back five Might. Some ten swarms of "
            "demonic mice serve it, each of Might 10 (Animal), about a "
            "thousand mice to a swarm, fiery-toothed and proof against fire, "
            "and they grow back from the aura until it is cleansed. A swarm "
            "takes on about three people; an unprotected victim takes a "
            "stress die +6 each round, falling with better clothing and "
            "armour to -9 in full armour with helm and gauntlets (armour does "
            "not add its Soak), and kills ten mice for every five points of "
            "Brawl attack total; a swarm flees at half its number. Group or "
            "Room spells hit a swarm and its victims together; an Animal "
            "effect at Voice, Concentration and Group takes one swarm, and one "
            "more magnitude clears the island for a while. Hatto's crosier "
            "holds 6 pawns of Perdo vis, found only once he is destroyed.",
        ),
        secrets=[
            titled(
                "Hatto and Rudiaria",
                "Hatto's corruption and the famine may both be linked to Rudiaria's "
                "misdeeds.",
            ),
            titled(
                "Storyguide Notes",
                "In the Infernal reading of the curse the covenant held him in its "
                "sway.",
            ),
        ],
        inside=gorge,
        realm="Infernal",
        aura=3,
    )

    places["bingen_hole"] = b.place(
        "The Bingen Hole",
        summary=(
            "The stretch just below Bingen, one of the river's two deadliest: "
            "rocks, a sudden quickening of the current and treacherous eddies. "
            "Only skilled, seasoned or foolhardy boatmen attempt it, though there "
            "are enough of those; many merchants portage round it."
        ),
        inside=gorge,
    )

    places["stone_of_bacchus"] = b.place(
        "The Stone of Bacchus",
        summary=paragraphs(
            "A small wooded island opposite Baccharach's quay where the wildest "
            "part of the town's autumn-equinox wine festival takes place; a few "
            "yards off its far side a weathered finger of rock rises fifteen feet "
            "from the water, the Stone of Bacchus, touched by the locals for luck "
            "with the harvest. Far too small for a covenant.",
            "Wine drunk on the island during the festival grants +6 to resist "
            "its ill effects, but brings on mounting hallucinations and visions "
            "and debauched behaviour that each reveller perceives differently "
            "(personality traits may shift by up to 3 for the night), and at "
            "dawn the drinker is at -6 for a day. The dregs left over are Muto "
            "vis, usually about 6 pawns and up to 12: the more riotous the "
            "revelry, the more vis, however much wine is left, and hoarding the "
            "wine does not help.",
        ),
        inside=gorge,
        aura=2,
    )

    places["pfalz_island"] = b.place(
        "Pfalz Island",
        summary=paragraphs(
            "The site of Rheinstein, mid-river a couple of hundred yards above "
            "Kaub (not the haunted island by Bingen). Rheinstein was founded "
            "in 1123 by Schwall of Bjornaer and Fulmonious of Tytalus with the "
            "First Tribunal's sponsorship, promising every other covenant "
            "three pawns of vis a Tribunal for five Tribunals; its magi also "
            "seemed to hold Burg Rheinstein near Bingen, though they were "
            "seldom there, as Redcap Ioanna noted in 1265 AA. In 1200 an army "
            "of angry mundanes under the archbishop of Trier destroyed it, "
            "and the magi's fate is unknown; Horst of Mercere's report laid "
            "much of the blame on their own conduct, and the Tribunal banned "
            "magic in the Gorge for twenty years. Its lesson: be subtle "
            "enough and strong enough.",
            "The island is about a hundred yards long and under half as wide. "
            "Its upstream half carries the castle, still unrepaired since the "
            "attack, with a tiny courtyard and the rocky stump of a central "
            "tower, and a small pier on half-sunk rocks facing the left bank "
            "where the traffic runs; the downstream half is a copse of a dozen "
            "trees, with a fresh corpse on a makeshift gallows. A longer, "
            "thinner, more wooded crescent of an island lies a couple of "
            "hundred yards upstream, joined by a spine of rock that shows only "
            "at the lowest water; at high water everything but the castle and "
            "the trees floods. It looks like a stone ship riding the river. "
            "Rebuilt, it would make a cramped but serviceable covenant and a "
            "uniquely good toll station, a bowshot covering the whole river.",
            "Lord Robert Schönburg, the baron's bastard, holds it with about a "
            "dozen ruffians taking tolls that amount to piracy; Wolkan, a "
            "branded thief, is among them. Baron Jürgen Schönburg owns the "
            "island and must be dealt with. Dripstones (chalcedonius) grow on "
            "the rock spine, one a season, brownish and waxy to the touch; "
            "pierced and worn at the neck one lets its wearer see through "
            "magical or faerie illusions (Perception against 3 plus the "
            "illusion's magnitude) and tell truth from lies (Perception "
            "against 6), and each is worth a pawn of Imaginem; a passing "
            "captain may ask for the Loreley charm the old inhabitants sold. "
            "A young vine in the copse yields a little Intellego vis from its "
            "sap with great care.",
        ),
        secrets=[
            titled(
                "Where the vine came from",
                "The vine on Pfalz Island was cut in secret from Durenmar's famous "
                "vine; Durenmar does not know and may be displeased.",
            ),
            titled(
                "The dripstone charms",
                "The old magi of Pfalz Island sold dripstone charms against the "
                "Loreley to ship captains.",
            ),
            titled(
                "The burial mounds",
                "Two ancient burial mounds hide among the upstream island's trees; "
                "Robert Schönburg robbed them (paltry treasure, perhaps vis) and woke "
                "their guardians, two powerful undead corpses with powers of stealth "
                "and destruction, who wait for a midsummer night when the river is "
                "low enough to cross the spine and fall on the castle.",
            ),
            titled(
                "Storyguide Notes",
                "The mounds' guardians are of unstated realm and Might.",
            ),
        ],
        inside=gorge,
        aura=2,
    )

    places["loreley"] = b.place(
        "Loreley",
        summary=paragraphs(
            "The narrowest and most treacherous point of the Gorge: the river "
            "squeezes into a canyon 150 yards wide roaring over hidden rocks "
            "between rocky slopes, and a cliff four hundred feet high, all but "
            "unclimbable from above or below, rises over it. Even with no siren "
            "singing (she may go unseen at night, in rain or in fog) the passage "
            "needs Profession: Boating against 9 from anyone who has not learned "
            "the rocks. Vis might be gathered here at great hazard.",
            "The Loreley herself is a faerie of Might 30 (Aquam), an exceedingly "
            "beautiful maiden clothed only in the long golden hair she combs for "
            "ever with a jewelled comb (Pre +5, Com +5, Dex +2, Str -2, Sta -1; "
            "Hateful to Men +3, Jealous of Women +3). Daughter of the Rhine "
            "Spirit of the Rhinefalls, she resents mankind's taming of her "
            "father and wrecks its shipping, and envies women who win men's "
            "hearts: she lures mariners toward the cliff, climbs down, bends them "
            "to her will and drowns them. She has a faerie's nature (no fatigue, "
            "disease or ageing, speech with anyone, Second Sight) and a faerie's "
            "bane in iron, which wounds her at a touch. Her song (4 points, "
            "Imaginem) makes up to ten people a round long to reach her, an "
            "Intelligence stress roll against 9, with +3 for women and for "
            "wax-stopped ears, and a dripstone's wearer shrugs it off on "
            "Perception against 6; her gaze (8 points, Mentem) binds one man at a "
            "time who fails Intelligence against 12 to obey her utterly, even to "
            "death; she works any Creo or Rego Aquam effect up to level 30 for a "
            "point a magnitude; and for 10 points she melts into the Rhine, "
            "regaining 5 Might an hour and healing in minutes, hours and days, so "
            "that she is all but unkillable. Her blood holds 6 pawns of Aquam and "
            "her comb 4 of Imaginem.",
        ),
        inside=gorge,
        realm="Faerie",
        aura=2,
    )

    places["maria_laach"] = b.place(
        "Kloster Maria Laach",
        summary=(
            "A Benedictine abbey of 1093 in lonely meadows beside Laach Lake, "
            "the foremost monastery of the middle Rhine. Its church is a "
            "Romanesque masterpiece, the first columned basilica built with "
            "arches, and the garden court before it, full of statues and "
            "fountains, is a divinely inspired image of Eden; the aura of 4 is "
            "the garden's."
        ),
        inside=gorge,
        realm="Divine",
        aura=4,
    )

    places["teufelsloch"] = b.place(
        "The Teufelsloch",
        summary=(
            "The Devil's Hole, in the hills west of Laach Lake: a huge eroded "
            "pit with steep crumbling edges, black within and of unknown depth, "
            "reeking of the livestock that have fallen in and rotted."
        ),
        inside=gorge,
        realm="Infernal",
        aura=1,
    )

    places["rolandseck"] = b.place(
        "Rolandseck and Nonnenwerth",
        summary=(
            "On the left bank north of the Gorge the ruined castle of Rolandseck "
            "looks down on the quiet island of Nonnenwerth and its convent. "
            "Legend says Roland, count of Angers, Charlemagne's nephew and his "
            "greatest knight, loved Hildegunde, daughter of the local count "
            "Heribert, and began a castle and watchtower for them; called to "
            "fight the infidel in Iberia he was reported dead, she took the veil "
            "on the island, and when he came home too late the two could only "
            "greet each other across the water for the rest of their lives."
        ),
        inside=gorge,
    )

    places["drachenfels"] = b.place(
        "Drachenfels",
        summary=paragraphs(
            "The lowest of the Seven Hills and the nearest the Rhine, a thousand "
            "feet high. Under it runs the cave where Siegfried slew the dragon "
            "Fafnir and bathed in its blood to make himself invulnerable, as the "
            "Nibelungenlied tells; the catacombs are extensive and the aura of 3 "
            "runs throughout. It would suit a covenant were it not for Schloss "
            "Drachenfels, the archbishop of Cologne's great castle built "
            "directly above. Who or what lives in the caves is not said; perhaps "
            "Fafnir's brood endures, or that of his brother Regin who plotted "
            "the slaying with Siegfried.",
            "The hills themselves have their legend: the wild Rhine once pooled "
            "into a lake here and spilled ruinously northward, until seven "
            "giants dug a gap with great spades to drain it, were paid in mined "
            "treasure, and left their spoil heaps as the Seven Hills.",
        ),
        inside=gorge,
        aura=3,
    )

    westerwald = b.place(
        "The Westerwald",
        summary=paragraphs(
            "East of the right bank north of Koblenz, running more than fifty "
            "miles eastward with the Lahn valley for its southern edge: an "
            "almost unbroken rumpled blanket of birch, beech and oak with fir and "
            "pine on the heights, home to many wolf packs and, in its heart, to "
            "the faerie Court of Bright Winter. The count of Nassau, whose lands "
            "lie just to the south, is pushing into the forest and sending bands "
            "of foresters to kill its wolves.",
            "The Court asks that the wolves be protected and intruders driven "
            "out, and would give leave to hunt and gather vis in return; the "
            "Rhine's ruling that magi may actively defend a wilderness applies. "
            "Red-Hame, a large faerie wolf of Might 12 with a ruddy ruff and "
            "back, carries the Court's wishes to the hedge wizards of Waldheim "
            "through his companion Torven. No aura is given for the forest as a "
            "whole; the glade at Waldheim is Magic 2.",
        ),
        inside=gorge,
    )
    places["westerwald"] = westerwald

    places["waldheim"] = b.place(
        "Waldheim",
        summary=paragraphs(
            "The site of Oakdell, a dozen miles into the Westerwald. Oakdell was "
            "founded in 934 by magi of House Diedne with the First Tribunal's "
            "sponsorship and a ban on trespassing on Rudiaria's territory; "
            "unwelcoming and secretive, it brought spurious charges of spying "
            "against Durenmar in 997, saw Wizard War declared on its Caithlinn by "
            "Severus Maximus of Flambeau and on its Pietro by Cirion of Tremere "
            "in 1004, and was razed in the Schism War in 1016 with every magus "
            "slain. Its lesson: do not make powerful Hermetic enemies. Redcap "
            "Harundo's directions of 1075 AA still serve: by boat from Koblenz "
            "up the Lahn to Ems, north on the forest track for several miles to "
            "a weathered standing stone on the left, then a barely used path "
            "north-west for a couple of hours and over a small stream into a "
            "glade round an ancient oak.",
            "The glade now holds a tiny hamlet of rude buildings and little more "
            "than a dozen people: the large hut of the elder Ludold, the smaller "
            "one of his son Torven, two more family huts and a barn. The "
            "crumbled foundations of Oakdell's two stone buildings hold a neat "
            "vegetable plot and an open pen of wild-looking pigs that obediently "
            "leave the vegetables alone. The villagers trade pigs for grain and "
            "see almost nobody else; visitors are met politely but warily. The "
            "path beyond leads toward the Court of Bright Winter, whom the "
            "villagers serve for protection while calling themselves the count "
            "of Nassau's loyal subjects and refusing to speak of the court.",
            "Ludold, gaunt and white-haired with a necklace of bones, is a "
            "cunning man of minor potions and charms whose shelves hold bones, "
            "herbs, mushrooms and preserved organs, some perhaps vis, which he "
            "gathers round the glade; he will trade them for a wife found for "
            "Torven, there being nobody of marriageable age in the hamlet. A "
            "covenant could settle here by ousting the villagers, angering forest "
            "and court alike, or by living beside them, who resist any major "
            "building; the place is isolated and has nothing beyond the basics.",
        ),
        inside=westerwald,
        aura=2,
    )

    places["faerie_courts"] = b.place(
        "The Courts of Dark Summer and Bright Winter",
        summary=paragraphs(
            "Two rival faerie courts facing each other across the Gorge, "
            "their details left to the storyguide. Bright Winter, Seelie, "
            "belongs to light, snow, cold and the hunt, keeps court in the "
            "highest snowy hills of the central Westerwald east of the river, "
            "and is found at midwinter by day; Dark Summer, Unseelie, belongs "
            "to dark, fire, warmth and the fields, keeps court in the lowest "
            "swampy ground of the Hunsrück forest west of the Gorge, and is "
            "found at midsummer by night. Dark Summer rules Bright Winter from "
            "Walpurgis Night to All Hallows' Eve, and Bright Winter rules Dark "
            "Summer the rest of the year. With diplomacy either court might "
            "become a contested source of vis. Red-Hame the wolf serves Bright "
            "Winter; the Schönburg family carries Dark Summer's blood.",
            "The storyguide may instead use the Courts of the Seasons of the "
            "forests chapter: King Holly of Winter in the Westerwald, the Alder "
            "Prince of Spring in the Odenwald, King Oak of Summer in the "
            "Palatinate Forest and the Willow Maiden of Autumn in the Hunsrück.",
        ),
        secrets=[
            titled(
                "A cure for Karlotte",
                "The fae of Dark Summer know a cure for Karlotte Schönburg and will "
                "sell it.",
            ),
            titled(
                "Storyguide Notes",
                "In the Faerie reading of the curse the two courts play a game of "
                "seventy-seven years with the Gorge's nobles as pawns and clear the "
                "board at the end of every round.",
            ),
        ],
        inside=gorge,
        realm="Faerie",
    )

    places["schonburg"] = b.place(
        "The Schönburg",
        summary=(
            "The large castle of Baron Jürgen Schönburg on the riverside hill "
            "just south of Oberwesel, on the left bank. The family descends at a "
            "distance from the fae of the Court of Dark Summer and keeps a little "
            "faerie blood, and a faint trace of Faerie hangs about the place at "
            "certain times of year. The red crocuses that bloom outside its walls "
            "in early summer are a source of Ignem vis. Here live the baron, his "
            "heir Karlotte, and, when he is not on Pfalz Island, his bastard son "
            "Robert."
        ),
        inside=gorge,
        realm="Faerie",
    )

    places["seven_maidens"] = b.place(
        "The Seven Maidens",
        summary=(
            "Seven pointed rocks just breaking the water below Oberwesel, held up "
            "as a warning to Rhineland girls. Seven cold-hearted virgin sisters "
            "of the Schönburg, raised by a meek aunt after their father died of "
            "grief for want of a son, spent their days feasting, riding and "
            "hawking and toyed with and cruelly refused every suitor; pressed at "
            "last to choose, they left by boat, the eldest mocking the crowd on "
            "the shore, and a storm wave drowned them all at this spot."
        ),
        inside=gorge,
    )

    places["mosel_valley"] = b.place(
        "The Mosel Valley",
        summary=(
            "The Mosel comes from the Vosges through Upper Lorraine, and its "
            "lower course between Trier and Koblenz winds between the Eifel and "
            "the Hunsrück past castles and south-facing vineyards. Smaller and "
            "quieter than the Rhine, it still carries fair traffic upstream from "
            "Koblenz to Trier or Metz."
        ),
        inside=valley,
    )

    places["treverorum_site"] = b.place(
        "Treverorum",
        ruined=True,
        summary=paragraphs(
            "The lost covenant beneath Trier, between the Fleischstrasse that "
            "leads to the main market and the poorer Niederstrasse behind it. "
            "First proposed in 1088 by Xantippes and Julia of Jerbiton and "
            "Selena Tibicena of Bonisagus to recover Rome's secrets, and "
            "refused for want of sponsors from Irencillia, Crintera and "
            "Dankmar, it was approved in 1095 when Arliandus of Tremere joined "
            "them. Mundane meddling ruined it: Redcap Ioanna was murdered in "
            "the city in 1151, Xantippes was convicted in 1158 of years of "
            "self-devised Mentem magic on Trier's people for gain, the "
            "covenant was fined fifty pawns in 1165 for harming the Order's "
            "standing with town and Church, and in 1172 Scholastus of "
            "Jerbiton declared himself its last survivor, called Trier unsafe "
            "for magi because of its churchmen, and left for the Greater Alps "
            "with part of the fine unpaid. Its lesson: do not meddle "
            "drastically with mundanes and the Church. Its symbol, the Porta "
            "Nigra, is carved on the smashed council table.",
            "Redcap Ioanna's directions of 1236 AA named a merchant's shop on "
            "the Fleischstrasse and the password 'Pax Hermae'. The shop now "
            "sells wine under Isaac for his uncle David ben David, neither of "
            "whom knows of magi; the Blaue Keiler inn stands to its left and a "
            "narrow alley to a back street and a butcher's to its right. Two "
            "underground levels lie behind the shop under the alley, with "
            "five ways in: a bricked-off passage in the wine cellar that the "
            "last owner called haunted; the wooden ceiling shutters of two "
            "upper sancta under the rubbish-strewn old garden yard; a raised "
            "stone 'grave' of Selena Tibicena in the neglected graveyard "
            "across the alley, marked with a sanctum sign instead of a cross, "
            "hiding stairs to her sanctum (she is not buried there); a disused "
            "stair in a burnt-out house next to a brothel on the "
            "Niederstrasse, where vagabonds sleep; and, least likely, the "
            "Roman culvert from outside the walls, which runs a few hundred "
            "yards to the maze beneath the ruined Barbarathermen and the other "
            "way under the Frankenturm, a fortified merchant tower in the city.",
            "Of the four sites this is the most intact and the most readily "
            "claimed, but it lies underground in a city: settling it without "
            "the merchant above knowing is nearly impossible, and privacy "
            "hard to come by. Its remaining vis is a few pawns of Mentem in "
            "old Roman coins in Arliandus's sanctum, and the ghosts of the "
            "amphitheatre outside the walls. Divine at street level, Magic 1 "
            "on the upper level and Magic 2 on the lower, as are many of "
            "Trier's other Roman cellars Magic 1.",
        ),
        secrets=[
            titled(
                "The ghosts of Treverorum",
                "The ghosts of Treverorum's magi rest in the burial alcoves by the "
                "underground stream; disturbing one may bring pestering, or lost "
                "secrets at a price.",
            ),
        ],
        inside=valley,
        realm="Divine",
        levels=[
            Builder.level(
                "Upper level",
                1,
                notes=(
                    "Three sancta, decayed and mostly empty but for rubbish and "
                    "rats; Selena's, under the graveyard, holds assorted "
                    "skeletons. A wide circular light shaft at the centre, its "
                    "path now overgrown and impassable, and an old ladder up."
                ),
            ),
            Builder.level(
                "Lower level",
                2,
                notes=(
                    "The council chamber with its smashed oak table; a solid "
                    "metal sanctum-marked door that reads as magical; the library "
                    "of waterlogged, moss-covered books and parchment and the "
                    "empty stores; double doors to an overgrown pond at the foot "
                    "of the shaft and to the old sewer stream with the magi's "
                    "burial alcoves. Behind the door Arliandus's sanctum stands "
                    "intact: a well-equipped Mentem laboratory with modest "
                    "treasures and Mentem vis in Roman coins. The Door of Deimos, "
                    "iron embossed with faces and skulls inlaid in lead and "
                    "silver, is unlocked but latched through a leering mouth: it "
                    "compares whoever touches it with an arcane connection to the "
                    "long-dead Arliandus (InCo 5, level 8, 6 a day, Touch, "
                    "Momentary) and on a mismatch or a resisted check fills the "
                    "intruder with terror (CrMe 15, level 43, Touch, Sun, 6 a day, "
                    "Penetration 22, Intelligence against 12 or flee), gloves "
                    "notwithstanding. The Crystal of a Hundred Candles in the "
                    "ceiling lights the room when the door opens (CrIg 10, level "
                    "23, 24 a day). The Mirror of Dreams, gold-framed with smaller "
                    "fragments, shows a willing gazer his thoughts as images and "
                    "gives +3 to Mentem laboratory totals at a Warping Point a "
                    "season (InCrMeIm 35, level 45, Eye, Concentration, unlimited). "
                    "The Trumpet of Ghostly Summoning, a small silver trumpet, "
                    "calls nearby ghosts and spirits and makes them visible "
                    "(MuMeIm 40, level 41, Touch, Sun, Room, 2 a day). The "
                    "storyguide may add books and laboratory texts here."
                ),
            ),
        ],
    )

    places["trier_amphitheatre"] = b.place(
        "The Amphitheatre of Trier",
        summary=paragraphs(
            "A deserted oval Roman amphitheatre a few hundred yards east of "
            "Trier's walls along the Hermesstrasse, at the foot of the "
            "Martinsberg. Overgrown passages lead from the sandy arena into "
            "small empty chambers in the hillside once used by gladiators, "
            "where spells or Second Sight find faint ghosts; the arena is "
            "Magic 1 and the chambers Magic 2.",
            "Three ghostly gladiators of Might 20 (Magic) linger: Marcus the "
            "Valiant, their leader, a stocky hoplomachus with round shield, "
            "arm-guard, greave, gladius and brimmed bronze helm (Str +2, Sta "
            "+3, Dex +3; Attack +14, Defence +13, Damage +7, Soak +7; Brave +3, "
            "Duty-Bound +3, Honourable +1); Cyrillus of Argentoratum, a wiry "
            "retiarius with trident, net, shoulder-guard and copper Poseidon "
            "mask (Qik +4; Initiative +7, Attack +12, Defence +14, Damage +7, "
            "the net a scuffling attack, Soak +4; Crafty +1); and Caudelix the "
            "Gaul, a burly giant of Size +1 with a great axe, iron skull-cap "
            "with a spectacled mask and leather breeches (Str +5, Sta +4; "
            "Attack +16, Defence +9, Damage +15, Soak +8; Violent +1). Blown "
            "here at night, the Trumpet of Ghostly Summoning raises the three, "
            "who arm themselves and challenge whoever is present to a duel to "
            "the death, each wagering a trinket of jewellery or Roman coin "
            "against a stake of like worth. The fight looks real but is not "
            "deadly: a killing blow knocks out, wounds are tracked as "
            "non-lethal and the players learn their true wounds only after "
            "treatment. A gladiator who wins takes his prize, later found "
            "buried in the chambers and ruined by age, and fades; one who "
            "loses fades leaving his trinket, worth 2 pawns of Mentem vis. "
            "Each fights once a year.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The record of 1248 AA, Valdus of Tytalus fined a pawn for twice "
                "harvesting vis from Treverorum's site outside the walls, is the clue "
                "that leads to a vis source near Trier, and so to the amphitheatre, "
                "its ghosts and the trumpet.",
            ),
        ],
        inside=valley,
        aura=1,
        levels=[
            Builder.level(
                "The gladiators' chambers",
                2,
                notes="Small empty rooms in the hillside off the arena's passages.",
            )
        ],
    )

    places["fenistal"] = b.place(
        "Fenistal",
        summary="A regio deep in the southern Bohemian Forest, dangerously close to "
        "Irencillia, of which the Order knows nothing.",
        secrets=[
            titled(
                "What Fenistal is",
                "Fenistal is the original temple of Diana, where Merinita served as "
                "the goddess's last disciple in Germania, long thought destroyed but "
                "held ever since by the surviving renegades of early House Merinita, "
                "the exsules, as their 'covenant'.",
            ),
            titled(
                "Fenistal's regio",
                "Fenistal's regio has a single level, the top, with no intermediate "
                "levels, so that entering it is very hard; the strongest magic of its "
                "masters goes to keeping it hidden.",
            ),
            titled(
                "Who lives at Fenistal",
                "Fewer than a dozen exsules live at Fenistal with the barest staff of "
                "servants, all once animals given human form, and two of them always "
                "stand guard.",
            ),
            titled(
                "What comes from Fenistal",
                "From Fenistal come raids on weak covenants, the recruiting of failed "
                "apprentices, fae set against the Order, the Huntress in the Wood as "
                "an unwitting arm, and a long-planned revenge on the Tribunal.",
            ),
            titled(
                "Storyguide Notes",
                "The regio's single level is at Magic 8.",
            ),
        ],
        inside=rhine.places.get("bohemia") or valley,
        status="Rumoured",
        known="Locally",
        levels=[
            Builder.level(
                "The temple of Diana",
                8,
                enter="The only level; with no intermediate levels, very hard to enter.",
                notes="The exsules' hidden covenant.",
            )
        ],
    )


# -- lords and towns --


def _lords(
    rhine: Rhine,
    gorge: Neighbour,
    valley: Neighbour | None,
    mainz: Neighbour,
    trier: Neighbour,
) -> dict[str, Neighbour]:
    b = rhine.b
    world = rhine.world
    lords: dict[str, Neighbour] = {}

    lords["count_palatine"] = b.lord(
        "Louis I Wittelsbach, Count Palatine of the Rhine",
        summary=(
            "Duke of Bavaria and Count Palatine of the Rhine. He holds Baccharach "
            "with Burg Stahleck, where his tolls are just, and Burg Thurant, and "
            "is overlord of Eberhard von Eppstein. A legitimate toll-gatherer, "
            "and, if the book's future holds, a member of the Rhine League."
        ),
        title="duke",
        place=gorge,
        arms=ARMS_PALATINE,
    )
    lords["bolanden"] = b.lord(
        "Werner IV, Count of Bolanden",
        summary=(
            "A vassal of Mainz and a fervent builder of castles, with lands "
            "south-west of Mainz and Burg Ehrenfels, Burg Sterrenberg, whose "
            "tolls are unjust, and Burg Liebenstein. Elder brother of Philip I of "
            "Falkenstein. A knight of Bolanden was the lover of Mechthild Brömser."
        ),
        title="count",
        answers_to=mainz,
        place=gorge,
    )
    lords["katzenelnbogen"] = b.lord(
        "Dieter II, Count von Katzenelnbogen",
        summary=paragraphs(
            "A fervent castle-builder holding a large, thinly peopled territory "
            "between the Taunus and the Lahn east of the Gorge: Kaub, whose tolls "
            "are unjust, Burg Hohenstein, Burg Kaub, still a-building, and Burg "
            "Katzenelnbogen, whose tolls are also unjust. His family rose fast "
            "from humble east-bank origins in two generations, and its castles "
            "and intrusion into the Gorge alarm the archbishops.",
            "Tall, proud and not very pious, fond of tournaments and war, he "
            "loves nothing so much as ruthlessly gathering land and castles. "
            "Easy to make an enemy of, but treated with care and respect a "
            "possible ally: he has no qualms about dealing with useful wizards.",
        ),
        title="count",
        place=gorge,
    )
    lords["nassau"] = b.lord(
        "Henry II the Rich, Count of Nassau",
        summary=(
            "Holds land along the Lahn and round the Westerwald: Burg Nassau, "
            "the town of Nassau and Limburg, taking unjust tolls at both. He is "
            "pushing hard into the Westerwald to bring it under his hand and "
            "sends foresters to kill its wolves, the grievance of the Court of "
            "Bright Winter. Torven of Waldheim's uncle was one of his foresters."
        ),
        title="count",
        wealth="Wealthy",
        seat="Burg Nassau",
        place=gorge,
    )
    lords["veldenz"] = b.lord(
        "Gerlach IV, Count of Veldenz",
        summary=(
            "A vassal of Trier whose lands lie south-west of Koblenz and along the Mosel."
        ),
        title="count",
        answers_to=trier,
        place=valley,
    )
    lords["aremberg"] = b.lord(
        "Eberhard II, Count of Aremberg",
        summary=(
            "Holds lands on the edge of the Eifel west of Koblenz: Altenahr, Burg "
            "Are and Burg Aremberg."
        ),
        title="count",
        seat="Burg Aremberg",
        place=gorge,
    )
    lords["falkenstein"] = b.lord(
        "Philip I, Baron Falkenstein",
        summary=(
            "Younger brother and vassal of the count of Bolanden, holding some of "
            "the Bolanden lands and Burg Reichenstein."
        ),
        title="baron",
        answers_to=lords["bolanden"],
        place=gorge,
    )
    lords["schonburg"] = b.lord(
        "Jürgen, Baron Schönburg",
        summary=paragraphs(
            "Holds Oberwesel, the Schönburg and Burg Pfalz, where the tolls are "
            "unjust. Of distant faerie descent from the Court of Dark Summer. "
            "Father of Karlotte, his lawful heir, and of the bastard Robert, whom "
            "he put in charge of the Pfalz tolls; he is ashamed of Robert and "
            "suspects him of unjust tolls, but divided loyalties leave him "
            "paralysed and blind to the worst of it.",
            "He owns Pfalz Island. Magi who cure Karlotte and prove Robert's "
            "guilt win his gratitude; he may then lease them the island, perhaps "
            "sharing the toll profits if they rebuild Burg Pfalz and run the "
            "station, though Robert's band must still be put out by force. "
            "Driving Robert out first makes an enemy of the baron.",
        ),
        title="baron",
        seat="The Schönburg",
        place=gorge,
    )
    lords["braubach"] = b.lord(
        "Eberhard von Eppstein, Baron of Braubach",
        summary=(
            "A vassal of the Count Palatine holding Braubach and the Marksburg, "
            "where his tolls are unjust."
        ),
        title="baron",
        seat="The Marksburg",
        answers_to=lords["count_palatine"],
        place=gorge,
    )
    lords["rudesheim"] = b.lord(
        "Thibaud the Fat, Baron of Rüdesheim",
        summary=(
            "A minor vassal of Mainz holding Rüdesheim and the Brömserburg, the "
            "old keep of Rudiaria. Haunted by the ghost of his ancestress "
            "Mechthild, he discreetly asks knowledgeable strangers for help."
        ),
        title="baron",
        seat="The Brömserburg",
        answers_to=mainz,
        place=rhine.places["rudesheim_bromserburg"],
    )
    lords["eltz"] = b.lord(
        "Arnold, Baron von Eltz",
        summary="A minor noble holding Karden and Burg Eltz, where his tolls are unjust.",
        title="baron",
        seat="Burg Eltz",
        place=rhine.places["mosel_valley"],
    )
    lords["sooneck"] = b.lord(
        "Hermann von Wien, Baron of Sooneck",
        summary="A minor noble holding Burg Sooneck, where his tolls are unjust.",
        title="baron",
        seat="Burg Sooneck",
        place=gorge,
    )
    for key, lord in lords.items():
        world[key] = lord
    return lords


def _towns(
    rhine: Rhine,
    gorge: Neighbour,
    valley: Neighbour | None,
    mainz: Neighbour,
    cologne: Neighbour,
    trier: Neighbour,
    lords: dict[str, Neighbour],
) -> None:
    b = rhine.b
    world = rhine.world

    world["bingen"] = b.town(
        "Bingen",
        summary=(
            "At the southern end of the Gorge, where the Nahe meets the Rhine "
            "under a Roman bridge: an old walled town guarded by Burg Klopp, "
            "where tolls are taken for Mainz. The Bingen Hole lies just "
            "downstream, and Hildegard's monastery of Rupertsberg looks down on "
            "the town."
        ),
        charter="Church",
        ruler="Siegfried II, Archbishop of Mainz",
        answers_to=mainz,
        place=gorge,
    )
    world["rudesheim"] = b.town(
        "Rüdesheim",
        summary=(
            "A sizeable village on the right bank opposite Bingen, grown up round "
            "the Brömserburg and held by Thibaud the Fat, a minor vassal of Mainz. "
            "The overland portage to Lorch, and now to Kaub, starts here."
        ),
        charter="Noble lord",
        ruler="Thibaud the Fat",
        answers_to=lords["rudesheim"],
        place=rhine.places["rudesheim_bromserburg"],
    )
    world["baccharach"] = b.town(
        "Baccharach",
        summary=(
            "A left-bank town amid wide vineyards making a potent and locally "
            "prized wine, with a modest quay. Its autumn-equinox wine festival "
            "draws townsfolk and peasants from miles about, the wildest of it on "
            "the island of the Stone of Bacchus opposite. Held by Louis I, the "
            "Count Palatine, from Burg Stahleck, whose tolls are just."
        ),
        charter="Noble lord",
        ruler="Louis I Wittelsbach, Count Palatine",
        answers_to=lords["count_palatine"],
        place=gorge,
    )
    world["kaub"] = b.town(
        "Kaub",
        summary=(
            "A walled town, little more than a prosperous village, on the right "
            "bank a couple of hundred yards below Pfalz Island. Count Dieter II "
            "von Katzenelnbogen took it lately, is building Burg Kaub on the "
            "hillside above, and has begun taking unjust tolls from the merchants "
            "who portage overland from Rüdesheim."
        ),
        charter="Noble lord",
        ruler="Dieter II von Katzenelnbogen",
        answers_to=lords["katzenelnbogen"],
        place=gorge,
    )
    world["oberwesel"] = b.town(
        "Oberwesel",
        summary=(
            "A prosperous left-bank town two miles below Kaub, held by Baron "
            "Jürgen Schönburg from his castle just to the south; the rocks of the "
            "Seven Maidens lie just downstream."
        ),
        charter="Noble lord",
        ruler="Jürgen, Baron Schönburg",
        answers_to=lords["schonburg"],
        place=gorge,
    )
    world["koblenz"] = b.town(
        "Koblenz",
        summary=(
            "A fair-sized city where the Mosel meets the Rhine, named from the "
            "Latin for the confluence. The Roman fort is long gone but the old "
            "walls stand; the chief church, the collegiate foundation of St "
            "Kastor of 830, has lately grown to four towers, and there are several "
            "more churches, a courthouse and many merchants grown rich on Mosel "
            "wine. Emperor Henry II gave it its charter in 1018 and the "
            "archbishops of Trier have held it since, taking just tolls. The "
            "Teutonic Knights have lately founded a chapter house at its north end."
        ),
        charter="Church",
        ruler="Dietrich I, Archbishop of Trier",
        answers_to=trier,
        place=gorge,
    )
    world["limburg"] = b.town(
        "Limburg",
        summary=(
            "A fortified town on the Lahn some two dozen miles above the Rhine, "
            "guarding a large wooden bridge of the twelfth century (not the duchy "
            "of the same name). Held by Henry II of Nassau, whose tolls here are "
            "unjust."
        ),
        charter="Noble lord",
        ruler="Henry II the Rich, Count of Nassau",
        answers_to=lords["nassau"],
        place=gorge,
    )
    gorge_trier = paragraphs(
        "The oldest city in Germany, named for the Celtic Treverii, raised by "
        "Augustus to a regional capital and under Constantine the capital of "
        "the western Empire with more than eighty thousand people; now barely "
        "a tenth of that live within smaller walls inside the Roman "
        "footprint, among the most complete Roman remains in Germany above, "
        "outside and beneath the city. Archbishop Dietrich I rules it and "
        "takes its customs duties. Wine is the chief export, shipped down to "
        "Koblenz.",
        "Its landmarks: Constantine's Basilica, a brick throne hall eighty "
        "yards long that is now the archbishop's palace; the cathedral of St "
        "Peter, the oldest church in Germany and one of Constantine's four "
        "founding churches with St Peter's in Rome, the Holy Sepulchre and the "
        "Nativity, on ground given by his mother St Helena and keeping the "
        "Seamless Robe Christ wore at the crucifixion; the Porta Nigra, a "
        "four-storey Roman gate of sandstone in the north wall made the church "
        "of St Simeon in 1035 for a Greek hermit saint, with the Simeonstift "
        "beside it; the Kaiserthermen rebuilt as a castle in the south-east "
        "wall; the ruined Barbarathermen outside the walls; the Frankenturm "
        "merchant tower; the basilica of St Matthias just south, with the "
        "apostle's bones brought by St Helena; and the amphitheatre on the "
        "Hermesstrasse. The city has a Jewish community, David ben David its "
        "most prominent merchant, though the famous Jewish academy is at Mainz.",
        "Trier is no friend to magi: its churchmen drove out Treverorum in "
        "1172, and its archbishop led the army that destroyed Rheinstein in "
        "1200.",
    )
    if "trier" in world:
        _add_to(world["trier"], gorge_trier)
        world["trier"].answers_to = world["trier"].answers_to or trier.id
    else:
        world["trier"] = b.town(
            "Trier",
            summary=gorge_trier,
            charter="Church",
            ruler="Dietrich I, Archbishop of Trier",
            answers_to=trier,
            place=valley,
            arms=ARMS_TRIER,
        )
    gorge_mainz = (
        "The seat of Archbishop Siegfried II, Archchancellor of the Empire, "
        "who takes its customs duties; home of the famous Jewish academy; the "
        "last stop on the road from Frankfurt to the Gorge. If the book's "
        "future holds, Mainz and Worms found the Rhine League in the 1250s."
    )
    if "mainz" in world:
        _add_to(world["mainz"], gorge_mainz)
        world["mainz"].answers_to = world["mainz"].answers_to or mainz.id
    else:
        world["mainz"] = b.town(
            "Mainz",
            summary=gorge_mainz,
            charter="Church",
            ruler="Siegfried II, Archbishop of Mainz",
            answers_to=mainz,
            place=valley,
            arms=ARMS_MAINZ,
        )
    gorge_frankfurt = (
        "On the road from Durenmar to the Gorge, between the Odenwald and "
        "Mainz, with a large market fair."
    )
    if "frankfurt" in world:
        _add_to(world["frankfurt"], gorge_frankfurt)
    else:
        world["frankfurt"] = b.town(
            "Frankfurt",
            summary=gorge_frankfurt,
            place=valley,
            arms=ARMS_FRANKFURT,
        )


# -- churches --


def _churches(rhine: Rhine, gorge: Neighbour, cologne: Neighbour) -> None:
    b = rhine.b
    world = rhine.world

    world["teutonic_knights_koblenz"] = b.church(
        "The Teutonic Knights of Koblenz",
        summary=(
            "A chapter house of the Teutonic Knights, newly founded at the north "
            "end of Koblenz."
        ),
        church="Monastery or nunnery",
        order="Teutonic Knights",
        place=gorge,
        arms=ARMS_TEUTONIC,
    )
    world["maria_laach"] = b.church(
        "Kloster Maria Laach",
        summary=(
            "The Benedictine abbey beside Laach Lake, founded in 1093 and the "
            "foremost monastery of the region, with its arched columned basilica "
            "and its garden court made in the image of Eden, where the Divine "
            "aura reaches 4."
        ),
        church="Monastery or nunnery",
        order="Benedictine",
        founded=1093,
        place=rhine.places["maria_laach"],
    )
    world["rupertsberg"] = b.church(
        "Rupertsberg monastery",
        summary=paragraphs(
            "The Benedictine house Hildegard of Bingen founded on the hill "
            "above Bingen in the middle of the twelfth century. Hildegard, "
            "schooled at a monastery from the age of eight, was theologian, "
            "physician, mystic, diplomat, poet and politician, and most "
            "famous for music that seemed close to miraculous; she never "
            "quite mastered Latin and wrote through a scribe to emperors, "
            "popes and archbishops, and to several Hermetic magi. She had "
            "Communication +4 and was a Good Teacher.",
            "Her works in the original are all of Quality 13 (copies may be "
            "poorer): Scivias, a tractatus on Theology; Liber Vitae Meritorum, "
            "a tractatus on moral Philosophiae and Theology; Liber Divinorum "
            "Operum, a summa on metaphysical Philosophiae at level 2 and "
            "Theology at level 5; Physica, a tractatus on natural Philosophiae "
            "and Medicine; Causae et Curae, a summa on natural Philosophiae at "
            "level 2 and Medicine at level 3; Ordo Virtutum, a tractatus on "
            "the music of Artes Liberales, moral Philosophiae and Theology; "
            "and Symphonia Armoniae Celestium Revelationum, a tractatus on the "
            "astronomy and music of Artes Liberales.",
        ),
        church="Monastery or nunnery",
        order="Benedictine",
        place=rhine.places["rupertsberg"],
    )


# -- the threat --


def _threat(rhine: Rhine, gorge: Neighbour) -> None:
    S = Builder.stage
    rhine.world["rhine_gorge_curse"] = rhine.b.threat(
        "The Curse of the Rhine Gorge",
        summary=paragraphs(
            "After Treverorum and Rheinstein fell, the Tribunal of 1200 "
            "forbade all magic in the Gorge for twenty years. The ban has now "
            "lapsed, and Durenmar's leaders want a new covenant on the middle "
            "Rhine to put life back into a Tribunal where no covenant has been "
            "founded in decades, Fengheld's chapter houses multiply and magi "
            "drift away to other Tribunals. Newly Gauntleted magi, some who "
            "finished their apprenticeships at Durenmar and some invited from "
            "elsewhere, are to survey the four lost sites, choose one and "
            "found a covenant under Durenmar's sponsorship, subject to the "
            "other covenants' approval. Murion, Prima of Bonisagus and Praeco, "
            "lays out the grand but detail-light plan at the Forum straight "
            "after their initiation; Occultes of Durenmar may offer "
            "encouragement; Xavier of Mercere, the Tribunal's archivist, "
            "supplies the old Redcap directions, and a season in the Great "
            "Library yields the records of the four covenants.",
            "The four teach the Lessons of Failure: Rudiaria, do not deal with "
            "demons; Oakdell, do not make powerful Hermetic enemies; "
            "Treverorum, do not meddle drastically with mundanes and Church; "
            "Rheinstein, be subtle and well defended. The storyguide may run "
            "it gently, with years of support from a parent covenant such as "
            "Fengheld or Durenmar and exploratory forays first, or throw the "
            "magi in at the deep end, with Durenmar disorganised and resources "
            "scant. The party should mix Rhine and non-Rhine magi: "
            "Rhine-trained ones may take the Gild Trained Virtue and a parens "
            "from the book's masters and archmagi; one or two from rich "
            "covenants start with a shield grog and money, and several, but "
            "fewer than half, should come from Fengheld with favoured "
            "resources for the sake of the politics. Grogs come from local "
            "recruits or sponsors' gifts, and a shield grog is played by "
            "someone other than its magus's player.",
        ),
        secrets=[
            titled(
                "The seventy-seven years",
                "Each lost covenant of the Gorge fell within exactly seventy-seven "
                "years of its founding.",
            ),
            titled(
                "The Magic reading",
                "The curse's Magic cause, the revenge of the Nibelungs: Siegfried "
                "cheated the dwarves and giants who first tamed the Rhine, dooming "
                "his line and every kingdom or wise man who follows him to fall "
                "within seven decades, as the Burgundians fell to Attila, the "
                "Merovingians, and Charlemagne's empire to the Norse. Breaking it may "
                "uncover the lost Rhinegold and may require the untaming of the "
                "river's elemental spirit.",
            ),
            titled(
                "The Faerie reading",
                "The curse's Faerie cause, the rivalry of the Courts: Dark Summer and "
                "Bright Winter play a game more than a thousand years old with the "
                "Gorge's nobles as pawns, and its rules clear the board every "
                "seventy-seven years, sweeping away nobles, covenants and kingdoms "
                "alike; the Romans were Dark Summer's pieces and the barbarians "
                "Bright Winter's, then Burgundians against Huns as the Nibelungenlied "
                "records.",
            ),
            titled(
                "The Infernal reading",
                "The curse's Infernal cause, the pact of Rudiaria: the first covenant "
                "sold its souls to a powerful devil for gifts falling due after "
                "seventy years, grew mighty, held Archbishop Hatto II in thrall, and "
                "when payment came tried to cheat and was destroyed battling Hell in "
                "a great fire; the devil has since lured each later covenant to the "
                "same fall on the same schedule.",
            ),
            titled(
                "The Divine reading",
                "The curse's Divine cause, the corruption of the Merovingians: the "
                "Christian wizard-kings, Merovech descended from David and keeper of "
                "the Grail, rose by God's plan and fell within seven decades to "
                "corruption and infighting; God blessed the Carolingians and cursed "
                "every wizard's work in the region to fail in the same span, the "
                "Order's included, and only humble pious wizards prosper. The counsel "
                "of Albertus Magnus may show the path.",
            ),
            titled(
                "Storyguide Notes",
                "The saga can climax about seven decades in, when the curse's forces "
                "gather and the covenant meets its predecessors' fate unless it "
                "breaks the curse and founds a lasting Hermetic power. The storyguide "
                "chooses one cause, or none but self-inflicted misfortune. The Magic "
                "cause ties to Schwall of Bjornaer's schemes and the Path of the "
                "Heartbeast; the Infernal cause ties to the Gymir and Radegast arc. "
                "If history holds, the Rhine League of the 1250s is a further threat "
                "to any covenant taking tolls.",
            ),
        ],
        antagonist="The curse of the Gorge, whichever realm the storyguide gives it",
        moves="A track",
        position=0,
        place=gorge,
        stages=[
            S(
                "The Praeco's commission",
                at=1,
                clues=(
                    "Durenmar's unease is talked of: no new covenant in decades, "
                    "Fengheld's chapters spreading, magi leaving. Right after the "
                    "initiation at the Forum Murion names the Gorge, now free of its "
                    "ban, and offers Durenmar's sponsorship. A season's work in the "
                    "Great Library (a fitting Mercere Gauntlet) turns up the "
                    "Tribunal records, and Xavier the archivist the Redcap "
                    "directions of Crumena, Harundo and Ioanna. A side road: a "
                    "panicked, injured young magus reports his reckless Jerbiton "
                    "friend and their grogs dragged off by shadowy figures in the "
                    "Black Forest, and Durenmar's own magi will not stir; the "
                    "rescue may serve as a Flambeau, Tytalus or Merinita Gauntlet, "
                    "may be a true accident or a parens's test, and the rescued "
                    "magus may promise to sponsor the covenant."
                ),
                ignored=(
                    "The magi scatter to other covenants or Tribunals and the "
                    "Gorge stays empty; Fengheld may plant a chapter there instead."
                ),
                stopped="Murion is refused; Durenmar looks weaker still, and remembers.",
                turned=(
                    "The magi take the commission on their own terms, bargaining "
                    "for gentle support or accepting the deep end."
                ),
            ),
            S(
                "The road north",
                at=2,
                clues=(
                    "Nearly a hundred miles and about a week from Durenmar: the "
                    "north-east edge of the Black Forest, Wimpfen, the Odenwald, "
                    "where bandits waylay badly guarded travellers, Frankfurt's "
                    "great market fair, and Mainz, whose archbishop rules the "
                    "southern Gorge."
                ),
                ignored="A careless party loses goods or grogs to the Odenwald's bandits.",
                stopped="The bandits are beaten off or bought; the magi reach Mainz intact.",
                turned=(
                    "A first acquaintance in Mainz or Frankfurt, a merchant or a "
                    "cleric, becomes a contact for the years ahead."
                ),
            ),
            S(
                "The four sites",
                at=3,
                clues=(
                    "At Rüdesheim only a fortress and a haunted baron; at Pfalz "
                    "Island Robert Schönburg's ruffians, a corpse on the gallows and "
                    "a cramped ruin that commands the river; at Waldheim a wary "
                    "hamlet, tame pigs and a path toward the faerie court; under "
                    "Trier a wine merchant's cellar, a false grave and a sealed "
                    "Tremere door. Round them wait the Mouse Tower, the Loreley, "
                    "the Stone of Bacchus and the amphitheatre's ghosts."
                ),
                ignored=(
                    "Hatto's dread, the Loreley's song or Robert's gang take their "
                    "toll of the unwary; a night on the Mäuseturm island kills."
                ),
                stopped=(
                    "Each hazard faced yields something: Perdo vis from Hatto's "
                    "crosier, dripstones against the Loreley, Mentem trinkets from "
                    "the gladiators."
                ),
                turned=(
                    "Thibaud, Ludold, David ben David or Baron Schönburg become "
                    "friends rather than obstacles, each with a price."
                ),
            ),
            S(
                "Forest or city, covenant or chapter",
                at=4,
                clues=(
                    "The choice mirrors the Tribunal's own divide: the forest "
                    "covenants Crintera, Irencillia and Dankmar against the city "
                    "covenants Oculus Septentrionalis, Triamore and Waddenzee. "
                    "Durenmar wants a neutral traditionalist covenant to pull the "
                    "Tribunal together; Fengheld wants a chapter house that would "
                    "make it the Tribunal's giant, and makes generous offers at the "
                    "cost of independence, which Fengheld-trained magi may favour."
                ),
                ignored=(
                    "Drift leaves the magi with no site and no patron as Tribunal "
                    "approaches."
                ),
                stopped=(
                    "Fengheld's offer refused, Durenmar's sponsorship stands, and "
                    "Fengheld becomes a rival, not an enemy."
                ),
                turned=(
                    "A Fengheld chapter: funded and protected, bound by Fengheld's "
                    "charter, needing no Tribunal vote, and Durenmar disappointed."
                ),
            ),
            S(
                "Sponsors at Tribunal",
                at=5,
                clues=(
                    "A new covenant needs one sponsoring magus from every other "
                    "covenant; one suffices against his fellows' views, and "
                    "refusing reflects badly on a covenant, so modest terms usually "
                    "serve unless the proposal looks like a direct threat. The deals "
                    "are best struck in the days before Tribunal opens at Durenmar, "
                    "and each sponsor brings a founding gift in the measure of its "
                    "regard: books, items, valuables, grogs, some only promised. One "
                    "gift may be an enigmatic item with only hints to its use; "
                    "another's lavish gifts turn mundane and insulting when the "
                    "Moon-duration Imaginem spells on them lapse, showing what the "
                    "giver really thinks."
                ),
                ignored="Without a sponsor from every covenant the foundation is not recognised.",
                stopped=(
                    "A covenant that sees the Gorge foundation as a threat withholds "
                    "its sponsor; the magi must find what it fears and buy it off."
                ),
                turned=(
                    "The covenant is recognised, its sponsors' favours owed and "
                    "their gifts in hand."
                ),
            ),
            S(
                "Settling in",
                at=6,
                clues=(
                    "Mundane entanglement is certain: at the island, toll-gathering "
                    "among archbishops, the Count Palatine, Katzenelnbogen and the "
                    "robber-barons, with Robert's band to evict and Karlotte to "
                    "cure; in the forest, survival, Nassau's foresters and the Court "
                    "of Bright Winter's demands; under Trier, a hostile archbishop "
                    "and a merchant overhead. Gild membership and the Durenmar-"
                    "Fengheld rivalry pull at the magi from inside the Order."
                ),
                ignored=(
                    "Unjust tolls, a slighted baron or a provoked court bring the "
                    "fate of Rheinstein closer."
                ),
                stopped=(
                    "The covenant holds its ground, pays or collects its tolls "
                    "lawfully and keeps the Church at arm's length."
                ),
                turned=(
                    "Katzenelnbogen or Schönburg becomes an ally; the Court sells "
                    "leave to harvest vis; the covenant is a power on the river."
                ),
            ),
            S(
                "The Lotharingian question",
                at=7,
                clues=(
                    "The north-western covenants, the Lotharingians, talk of "
                    "seceding from the Rhine to deal more freely with mundanes. A "
                    "Gorge covenant sits on the border and must choose between "
                    "loyalty to Durenmar's traditions and a freer hand in a smaller "
                    "Tribunal."
                ),
                ignored="Both sides count the covenant among the uncommitted and court or threaten it.",
                stopped="The covenant stands with Durenmar and the motion fails or passes without it.",
                turned="The covenant goes with the Lotharingians, and Durenmar's sponsorship sours.",
            ),
            S(
                "The seventy-seventh year",
                at=8,
                clues=(
                    "As the covenant nears its eleventh Tribunal the signs of its "
                    "predecessors' falls return: malefic rumours and famine as at "
                    "Rudiaria, powerful Hermetic enemies as at Oakdell, trouble "
                    "with town and Church as at Treverorum, an army at the gates as "
                    "at Rheinstein; the Rhine League, if history holds, is tearing "
                    "down robber castles. The chosen cause shows its hand: the "
                    "river spirit stirring, the Courts clearing their board, the "
                    "devil of Rudiaria calling in its debt, or the Order's works "
                    "withering where humble, pious wizards prosper."
                ),
                ignored="The covenant falls within seventy-seven years, like the four before it.",
                stopped=(
                    "The curse is broken at its root: the Rhinegold found and the "
                    "river untamed, the game of the Courts ended, the devil "
                    "defeated, or grace won through humility and the counsel of "
                    "Albertus Magnus; the covenant endures as a lasting power."
                ),
                turned=(
                    "The covenant survives by a bargain with the curse's source, "
                    "and inherits its debt."
                ),
            ),
        ],
    )


# -- people --


def _people(rhine: Rhine) -> None:
    b = rhine.b
    magi = rhine.magi
    durenmar = rhine.covenants.get("durenmar")

    if "murion" not in magi:
        magi["murion"] = b.magus(
            "Murion",
            covenant=durenmar,
            house="house_bonisagus",
            age=None,
            summary=(
                "Prima of House Bonisagus and Praeco of the Rhine Tribunal at "
                "Durenmar, a powerful and overbearing archmaga. She sponsors the "
                "new Gorge covenant with a grand but vague plan and will back the "
                "proposal at Tribunal."
            ),
        )
    if "occultes" not in magi:
        magi["occultes"] = b.magus(
            "Occultes",
            covenant=durenmar,
            house="",
            age=None,
            summary=(
                "A magus of Durenmar who may offer the young magi of the Gorge "
                "support and encouragement."
            ),
        )
    if "xavier" not in magi:
        magi["xavier"] = b.magus(
            "Xavier",
            covenant=durenmar,
            house="house_mercere",
            age=None,
            summary=(
                "Of House Mercere, Archivist of the Rhine Tribunal. He compiles "
                "the old Redcap directions to the four lost covenants of the "
                "Gorge from the notes of Crumena, Harundo and Ioanna."
            ),
        )
    if "horst" not in magi:
        magi["horst"] = b.magus(
            "Horst",
            covenant=None,
            house="house_mercere",
            age=None,
            summary=(
                "Of House Mercere; the Redcap who reported Rheinstein's "
                "destruction to the Tribunal of 1200."
            ),
        )

    magi["hilda"] = b.magus(
        "Hilda",
        covenant=None,
        house="",
        age=28,
        type="grog",
        summary=(
            "A custos born and bred at Fengheld and given by it to the young "
            "magi: an immense blonde woman of Size +1 with piercing blue eyes in "
            "barrel-like scale armour made to measure, fighting with mace and "
            "heater shield (Attack +13, Defence +10, Damage +12, Soak +9) and "
            "carrying a pole axe and short bow besides. Great Strength and "
            "Puissant Single Weapon; Covenant Upbringing, Obese and Oversensitive "
            "to disrespect; Single Weapon 6+2, Leadership 5, Brawl 4, Latin 3, "
            "Order of Hermes Lore 2 (Fengheld). Prime leader material, she drills "
            "raw grogs into shape, brooks no disobedience, and is unpopular with "
            "the other grogs and untroubled by it; it puzzles her that mundanes "
            "object to a woman warrior."
        ),
        traits={"Brave": 3, "Loyal to magi": 3, "Tolerant": -3},
    )
    magi["byrek"] = b.magus(
        "Byrek",
        covenant=None,
        house="",
        age=27,
        type="grog",
        summary=(
            "Covenfolk given away by Crintera: tall, sturdy and awkward, filthy "
            "and lice-ridden, slouching on a long spear (Attack +10, Defence +10, "
            "Damage +7). Affinity with Athletics, Enduring Constitution and "
            "Long-Winded, perhaps from his amulet; Clumsy, Depressed and "
            "Simple-Minded; Athletics 7 (running), Great Weapon 5, West Slavonic "
            "5 (Sorbian), Survival 3, Ride 3. His mother, a witch of Crintera's "
            "Horse Clan, gave him a horse-bone amulet to make him swift and "
            "tireless as a horse, and he never takes it off, whether or not it "
            "works. A remarkable endurance runner and a reliable carrier of "
            "messages, single-minded and careless of routine; he feels Crintera "
            "cast him off, and his gloom may lift once he feels useful."
        ),
        traits={"Demoralised": 3, "Morose": 2},
    )
    magi["robert_schonburg"] = b.magus(
        "Lord Robert Schönburg",
        covenant=None,
        house="",
        age=29,
        type="companion",
        summary=paragraphs(
            "The bastard son of Baron Schönburg and the villain of the Gorge, "
            "not for a player. Tall and handsome with shoulder-length black "
            "hair, clean-shaven, dressed in costly black or dark green with "
            "showy jewellery bearing his device, an eagle displayed pierced "
            "through the heart by a spear, and startling green eyes that "
            "captivate women (Int +3, Pre +2). A gentleman with the "
            "Entrancement Virtue, Arcane Lore, Educated, Premonitions and a "
            "Privileged Upbringing; Avaricious, a Black Sheep, Nocturnal and "
            "Tainted with Evil; locally reputed little more than a thug. "
            "Entrancement 5 (women), Infernal Lore 4, Charm 4, Magic Lore 3, "
            "Philosophiae 3, Premonitions 3, Latin 3, Guile 3, Rhine Lore 3, "
            "Faerie Lore 1 (the Loreley); a useless fighter who carries a "
            "sword for show. He owns some 10 pawns of mixed vis and pouches of "
            "herbs, odd stones and animal parts.",
            "Schooled in Cologne, where a mentor initiated him into the Dark "
            "Arts, he was then given the Pfalz tolls by his father and runs a "
            "gang of ruffians there in what is really piracy, gate-crashing "
            "noble gatherings to behave disgracefully.",
        ),
        secrets=[
            titled(
                "Robert's master",
                "A committed servant of the Devil for the gains rather than from "
                "fervour; his greed grew with his initiation.",
            ),
            titled(
                "Robert's bewitchment",
                "People shun him, which he does not mind since his bewitchment "
                "compels obedience, used frivolously.",
            ),
            titled(
                "Robert's warnings",
                "Premonitions warn him when exposure nears.",
            ),
            titled(
                "Robert's magic",
                "He works minor natural magics as rituals needing time and vis, and "
                "might grow to rival a magus by dealing with a demon directly.",
            ),
            titled(
                "The burial mounds",
                "He robbed the burial mounds on the upstream island and woke their "
                "guardians.",
            ),
            titled(
                "The attack on Karlotte",
                "He is behind the attack on his half-sister Karlotte.",
            ),
            titled(
                "Storyguide Notes",
                "His rituals use Intelligence, Infernal Lore, the aura and a stress "
                "die and Shape and Material bonuses from gemstones.",
            ),
        ],
        traits={"Arrogant": 3, "Greedy": 3, "Scheming": 2},
    )
    magi["wolkan"] = b.magus(
        "Wolkan",
        covenant=None,
        house="",
        age=23,
        type="grog",
        summary="A branded thief and a possible grog, one of Robert's band on "
        "Pfalz Island. He would be handsome but for the livid brand on his "
        "cheek, hidden under shoulder-length brown hair; plain dress and a "
        "self-assured grace. Branded Criminal; Improved Characteristics "
        "and Social Contacts; Ambitious. Short sword (Attack +10, Defence "
        "+8, Damage +6) and thrown knife; Legerdemain 3, Stealth 3, "
        "Intrigue 3 (outlaws), Thrown Weapon 3, Rhine Lore 3 (criminals), "
        "Profession: Boatman 2. Baron Schönburg jailed him on Pfalz for "
        "theft and Robert freed him to help take tolls; he has no idea the "
        "tolls are unjust or that Robert is more than he seems. He knows "
        "the toll system, the dripstone trade against the Loreley, and the "
        "petty criminals and mercenaries of the towns up and down the Rhine.",
        secrets=[
            titled(
                "Wolkan's own aim",
                "His own aim is to lead his criminal contacts and get rich, perhaps "
                "with the covenant's resources.",
            ),
        ],
        traits={"Self-interest": 3, "Loyal": 0, "Brave": -1},
    )
    magi["karlotte_schonburg"] = b.magus(
        "Karlotte Schönburg",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="Baron Schönburg's daughter and heir, a striking red-haired young "
        "woman with more than the family's usual share of faerie blood, "
        "who knows her half-brother and rival Robert for what he is. On a "
        "recent journey she was attacked by an unknown dark figure in the "
        "woods west of the castle, and her seemingly slight wounds have "
        "left her in a coma from which nothing wakes her. The fae of Dark "
        "Summer will reveal a cure for a price.",
        secrets=[
            titled(
                "Who is behind the attack",
                "Robert Schönburg is behind the attack on Karlotte.",
            ),
            titled(
                "Storyguide Notes",
                "Proving it and curing her wins the baron's gratitude and with it "
                "Pfalz Island.",
            ),
        ],
    )
    magi["ludold"] = b.magus(
        "Ludold",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "Elder of Waldheim, gaunt and white-haired with a necklace of bones: "
            "a cunning man and lesser hedge wizard of minor potions and charms, "
            "whose hut is shelved with bones, herbs, mushrooms and preserved "
            "organs, some perhaps vis, which he gathers round the glade. He will "
            "trade potions, charms or vis to magi who find a wife for his son "
            "Torven."
        ),
    )
    magi["torven"] = b.magus(
        "Torven",
        covenant=None,
        house="",
        age=24,
        type="companion",
        summary=(
            "Ludold's son, the Wise One of Waldheim and a possible companion: "
            "unassuming, with scruffy brown hair, a patchy beard and a wolf-fur "
            "jerkin (Dex +3). Animal Ken, Intuition, Latent Magical Ability and "
            "Wilderness Sense; a Magical Air; a Magical Animal Companion and "
            "Reclusive; locally reputed a Wise One. Short bow (Attack +9); Animal "
            "Ken 3 (wolves), Animal Handling 3 (pigs), Forest Lore 3 "
            "(Westerwald), Hunt 3, Stealth 3, Survival 3, Wilderness Sense 3, "
            "Faerie Lore 2 (Bright Winter), Magic Lore 2 (herbs), Teaching 2. The "
            "villagers revere him for befriending and speaking with animals and "
            "treat him as their unofficial leader, a role he hates; he is poor at "
            "talk and makes strangers wary, but animals trust him, and he would "
            "rather be deep in the forest with Red-Hame, the faerie wolf who "
            "brings the Winter Court's wishes through him. He feels responsible "
            "for the village and defends it first; his hunches have saved it from "
            "disasters natural and human, wolf packs appear to help him in dire "
            "need, and the glade's creatures, the tame wild pigs among them, obey "
            "an unspoken command of his. He learned the bow from his uncle, a "
            "Nassau forester."
        ),
        traits={"Brave": 2, "Loner": 2, "Loyal to Waldheim": 2},
    )
    magi["isaac"] = b.magus(
        "Isaac",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "Manager of the wine shop on Trier's Fleischstrasse, the old front of "
            "Treverorum, for his uncle David ben David. He knows nothing of magi, "
            "sells wine to Gentiles under the recently relaxed rabbinical rule, "
            "and was told by the shop's last owner that the bricked-up passage in "
            "the cellar is haunted."
        ),
    )
    magi["david_ben_david"] = b.magus(
        "David ben David",
        covenant=None,
        house="",
        age=30,
        type="companion",
        summary=(
            "A prominent Jewish merchant of Trier and a possible companion, owner "
            "of the wine shop over Treverorum: of average height with short black "
            "hair and long side-curls, skull-cap and prayer shawl worn openly, "
            "moderate dress with the wheel badge of Jewry (Int +2, Com +2). A "
            "wealthy merchant; Educated, Puissant Bargain, Social Contacts and "
            "Well-Travelled; Pious, an Outsider, Judged Unfairly; locally reputed "
            "simply as a Jew. Bargain 5+2, High German 6 (Yiddish), Profession: "
            "Merchant 4, Aramaic 3, Latin 3, Artes Liberales 3, Civil and Canon "
            "Law 3, Folk Ken 3, Intrigue 3, Rhine Lore 3, Jewish Theology 3, "
            "Profession: Ship's Captain 2, Medicine 2, French, Italian and Low "
            "German 2. From a still wealthier family trading between Trier, "
            "Koblenz, Bingen and Mainz, he travelled with father and uncles as a "
            "boy, entered the Jewish academy at Mainz at thirteen, and took over "
            "the business and married Sophie when his father died ten years ago; "
            "they have no children yet. He will not soften his devotion for his "
            "Christian rivals' hatred, is level-headed and thick-skinned, and is "
            "likely soon to be asked to serve as a rabbi."
        ),
        traits={"Devout Jew": 3, "Honest": 2, "Insensitive to insults": 2},
    )
    magi["jarvis"] = b.magus(
        "Jarvis",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary="A forester of Semita Errabunda, suggested as a companion for the Gorge saga.",
    )
    magi["albertus_magnus"] = b.magus(
        "Albertus Magnus",
        covenant=None,
        house="",
        age=14,
        type="companion",
        summary="Albert of Cologne, born in Bavaria in 1206. If history holds he "
        "becomes the greatest natural magician and philosopher of his age: "
        "schooled at Padua, an early Dominican, a student at Bologna, a "
        "teacher at Cologne, Regensburg, Hildesheim, Freiburg and "
        "Strassburg, in Paris from 1245 and bishop of Regensburg in 1260, "
        "writing on theology, natural science, alchemy, astrology and the "
        "divination of dreams and arguing all of them compatible with "
        "Christianity. He might meet the magi, or be recruited into the "
        "Order.",
        secrets=[
            titled(
                "Storyguide Notes",
                "In the Divine reading of the curse his counsel is a path to grace.",
            ),
        ],
    )


# -- factions --


def _factions(rhine: Rhine, gorge: Neighbour, cologne: Neighbour) -> None:
    b = rhine.b
    world = rhine.world
    places = rhine.places

    odin = b.faction(
        "The Order of Odin",
        summary=paragraphs(
            "Whether it exists at all the book leaves to the storyguide, who "
            "must answer two questions: are there Norse wonder-workers who can "
            "match a Hermetic magus, and is there any organisation among them, "
            "and how tight? The answer may run from a Norse mirror of the "
            "Order hurling runic spells down to scattered weak hedge wizards "
            "brewing love potions. Norse legend tells of magicians who change "
            "shape, foretell the future and see far places, and of some who "
            "use runes to raise the dead, rule the weather, aid in battle and "
            "curse their foes; no single one of them should do all of these.",
            "Waddenzee hunts Norse wizards on the Ash Gild's behalf and has "
            "killed a handful; Heorot studies them; Oculus Septentrionalis "
            "wants the Baltic trade.",
        ),
        secrets=[
            titled(
                "Waddenzee and the myth",
                "Waddenzee has found no evidence of an organised Order of Odin and "
                "keeps the myth alive anyway.",
            ),
            titled(
                "Storyguide Notes",
                "The bulk of any such order may be Gymir's wizard pawns, or renegade "
                "Hermetic magi.",
            ),
        ],
        faction="Hedge coven",
        wants=(
            "Undecided: a rival Order's dominion over the North, or nothing more "
            "than a hedge wizard's living"
        ),
        offers="Norse magics of shape-changing, prophecy, far-seeing and the runes",
    )
    if "order_of_odin" in world:
        _add_to(world["order_of_odin"], odin.summary, odin.secrets)
        world["order_of_odin"].details["wants"] = odin.details["wants"]
        world["order_of_odin"].details["offers"] = odin.details["offers"]
        rhine.b.saga.neighbours.remove(odin)
    else:
        world["order_of_odin"] = odin
    world["gymir"] = b.custom(
        "Gymir",
        summary="A name from the North that the Order does not know in 1220.",
        secrets=[
            titled(
                "Gymir's fief",
                "A demon prince whose earthly fief is Scandinavia, at war with "
                "Radegast and with the Dominion.",
            ),
            titled(
                "Gymir's ways",
                "Gymir strikes at the Church, works through catastrophe and weather "
                "and through the Norse, commands an aggressive faction of wizards, "
                "and profits from Waddenzee's piracy.",
            ),
            titled(
                "Gymir and the Holy Vehm",
                "Gymir is worming into the Holy Vehm, meaning to turn the Vehm on "
                "Radegast's pagans in northern Germany.",
            ),
            titled(
                "Storyguide Notes",
                "Might not given. Gymir has murdered the Vehm's leader, the "
                "archbishop of Cologne, in 1225 if the book's future holds.",
            ),
        ],
        realm="Infernal",
        wants="(secret) the Church undone and the Holy Vehm turned on Radegast's followers",
        offers="(secret) storms, catastrophe and infernal power to its wizard pawns",
    )
    world["radegast"] = b.custom(
        "Radegast",
        summary="A god of the Old Ways to the Slavs of the Baltic shore, as far as "
        "the Order knows.",
        secrets=[
            titled(
                "Radegast's fief",
                "A demon prince whose fief is the Slavic lands, its heartland the "
                "eastern Baltic shore.",
            ),
            titled(
                "What Radegast wants",
                "Radegast wants the Germans deflected north and the Hanseatic towns "
                "rotted by greed.",
            ),
            titled(
                "Radegast's disguises",
                "Radegast poses as the pagan gods, and can dress Infernal power as "
                "Magic or Faerie: the auras of Rethra and Mount Radhost are really "
                "Infernal.",
            ),
            titled(
                "Radegast's pawns",
                "Radegast's pawns are Imanitos Mendax, willingly; Roznov, "
                "unwittingly; a cult among the townsfolk of Holstein and the Slavic "
                "princes of Mecklenburg; and an Ash Gild-led war on the Norse it is "
                "planning.",
            ),
            titled(
                "Storyguide Notes",
                "Might not given.",
            ),
        ],
        realm="Infernal",
        place=places.get("east"),
        wants="(secret) Germans turned north against the Norse, the Hansa corrupted by greed",
        offers="(secret) the powers of a 'god' to those who worship it",
    )
    world["radegast_cult"] = b.faction(
        "The cult of Radegast",
        summary="Worshippers of the Old Ways among the townsfolk of Holstein and the "
        "Slavic princes of Mecklenburg.",
        secrets=[
            titled(
                "What the cult worships",
                "Nobles and priests of the Holstein cities and the Mecklenburg "
                "princes who worship the demon Radegast believing it a god and "
                "receive diabolic powers.",
            ),
            titled(
                "The cult's high priest",
                "Imanitos Mendax poses as the high priest of the cult of Radegast and "
                "gathers power among its members.",
            ),
        ],
        faction="Hedge coven",
        realm="Infernal",
        place=places.get("lowlands"),
        wants="(secret) the favour of their 'god' and power over their neighbours",
        offers="(secret) diabolic powers to its members",
    )
    if "knights_of_the_sword" not in world:
        world["knights_of_the_sword"] = b.faction(
            "The Knights of the Sword",
            summary=(
                "A crusading knightly order in the Baltic lands, fighting the "
                "Prussian and Livonian pagans under the banner of the crusade. "
                "Any Baltic saga must reckon with them; the storyguide decides "
                "whether they are the righteous gone wrong, Satan's dupes or "
                "holy fools."
            ),
            faction="Military order",
            realm="Divine",
            place=places.get("east"),
            wants="The Baltic pagans converted or conquered",
            offers="Arms and the crusade's blessing",
        )
    if "holy_vehm" not in world:
        world["holy_vehm"] = b.faction(
            "The Holy Vehm",
            summary="A pious society led by the archbishop of Cologne; the book says "
            "no more of it.",
            secrets=[
                titled(
                    "Gymir and the Holy Vehm",
                    "Gymir is infiltrating and corrupting the Holy Vehm, and the "
                    "demon means to turn it on Radegast's pagan followers in northern "
                    "Germany.",
                ),
                titled(
                    "Storyguide Notes",
                    "Its leader is murdered in 1225 if the book's future holds.",
                ),
            ],
            faction="Council or assembly",
            realm="Divine",
            ruler="Engelbert I, Archbishop of Cologne",
            wants="Piety upheld",
        )
    world["exsules"] = b.faction(
        "The exsules of Fenistal",
        summary="Nothing of them is known to the Order in 1220.",
        secrets=[
            titled(
                "Who the exsules are",
                "Fewer than a dozen self-styled exiles (exsules; one exsul) living at "
                "Fenistal in the Bohemian Forest: descendants of the losing faction "
                "of early House Merinita who rejected the Order after Myanar's death "
                "and keep a Hermetic-like tradition cut off from modern Magic Theory.",
            ),
            titled(
                "The exsules' learning",
                "All the exsules know Parma Magica but imperfectly; most have studied "
                "from vis all their lives; the line bears Quendalon's curse; many "
                "have the blood of Merinita or of powerful magical spirits.",
            ),
            titled(
                "The exsules' nature magic",
                "Heirs of Merinita's nature magic, many exsules have walked the Paths "
                "through the Forest. With little access to Hermetic grimoires their "
                "spells rouse nature's fury rather than strike directly.",
            ),
            titled(
                "What the exsules mean to do",
                "The exsules mean to survive hidden, keep up with Hermetic advances "
                "by theft and spying, shelter failed apprentices, set the fae against "
                "the Order, and in the end take revenge on the Tribunal.",
            ),
            titled(
                "The exsules and Irencillia",
                "The exsules count Irencillia their greatest enemy, though Irencillia "
                "knows nothing of them.",
            ),
            titled(
                "The exsules' household",
                "The exsules keep no warriors and the barest servants, all former "
                "animals given human shape, which makes infiltration all but "
                "impossible; two members are always on guard.",
            ),
            titled(
                "The Huntress in the Wood",
                "The Huntress in the Wood is the exsules' unwitting instrument.",
            ),
            titled(
                "Storyguide Notes",
                "All have Weird Magic and Flawed Parma Magica; Poor Student is "
                "common; the line bears Supernatural Nuisance (Faeries) from "
                "Quendalon's curse; many have Mythic Blood from Merinita or from "
                "powerful magical spirits, and Ways of the Forest, Free Study and "
                "Study Bonus are common. Many may have overcome one or more Lesser "
                "Limits, and they may have taken in Diedne fleeing the Schism War, in "
                "which case they excel at spontaneous magic. Their spells should feel "
                "alien and frightening to a Hermetic magus.",
            ),
        ],
        faction="Hedge coven",
        realm="Magic",
        place=places["fenistal"],
        wants="(secret) to stay hidden, steal the Order's advances and avenge themselves on the Tribunal",
        offers="(secret) shelter to failed apprentices; the old nature magic of Merinita",
        rules="(secret) two members always on guard; no outsider enters",
    )
    world["huntress_in_the_wood"] = b.faction(
        "The Huntress in the Wood",
        summary="A secret society within the Order, mostly of House Bjornaer's "
        "followers, devoted to preserving primal, nature-bound magic. Its "
        "members meet in secret wearing animal masks.",
        secrets=[
            titled(
                "Who steers the Huntress",
                "The Huntress in the Wood is unknowingly a pawn of the exsules of "
                "Fenistal, who have steered it since its founding.",
            ),
            titled(
                "Under the masks",
                "With every face hidden, the Huntress's members do not know that not "
                "all of them are magi of the Order.",
            ),
            titled(
                "The Huntress's agenda",
                "The agenda instilled in the Huntress in the Wood is to take over the "
                "Elder Gild and with it Irencillia.",
            ),
        ],
        faction="Hermetic group",
        realm="Magic",
        rules="Members meet masked as animals and keep one another's names secret",
        wants="Primal nature magic preserved; (secret) the Elder Gild and Irencillia in its hands",
        offers="Fellowship among the Order's wild-hearted magi",
    )
    world["pomeranian_shapeshifters"] = b.faction(
        "The Pomeranian shapeshifters",
        summary="A close-knit but far from united community of mostly unGifted "
        "shapeshifters in Pomerania, long at feud with House Bjornaer, which "
        "no longer remembers why. They have factions and feuds of their own, "
        "and the most peaceable among them may treat with Prima Falke.",
        secrets=[
            titled(
                "Storyguide Notes",
                "In the Crintera Schism arc they are admitted to House Bjornaer in "
                "1227 and 1228 and mostly lean Wilderist, tipping the House's "
                "balance.",
            ),
        ],
        faction="Hedge coven",
        realm="Magic",
        place=places.get("east"),
        wants="Their old feud with Bjornaer settled on their own terms",
        offers="The shapeshifter's art, outside Hermetic tradition",
    )
    world["rhine_league"] = b.custom(
        "The Rhine League",
        summary="No such league exists in 1220.",
        secrets=[
            titled(
                "Storyguide Notes",
                "If history holds: as toll stations grow to a dozen by mid-century "
                "and double in four years in the Interregnum of the 1250s, merchants "
                "and lawful toll-takers suffer, and Mainz and Worms found the Rhine "
                "League to protect their merchants; many cities, the princely nobles "
                "(the three archbishops and the Count Palatine) and lesser nobles "
                "join. It puts down unjust tolls by trade sanctions and by destroying "
                "robber-barons' castles, besieging or razing nearly a dozen and "
                "unseating several barons, and disbands after three years with its "
                "aims met. A formidable foe for any covenant that acts as or allies "
                "with a robber-baron: vast resources, a large army and God on its "
                "side.",
            ),
        ],
        place=gorge,
        wants="(secret) unjust tolls ended and the robber castles razed",
        offers="(secret) protection for merchants and lawful toll-takers",
    )
    world["roberts_band"] = b.faction(
        "Lord Robert Schönburg's band",
        summary="About a dozen malcontents and ruffians living in the ruins on Pfalz "
        "Island under Lord Robert Schönburg, taking river tolls that amount "
        "to piracy; Wolkan the branded thief is one of them.",
        secrets=[
            titled(
                "Robert's secret",
                "Robert Schönburg is a diabolist.",
            ),
        ],
        faction="Brigands and mercenaries",
        members=12,
        ruler="Lord Robert Schönburg",
        place=places["pfalz_island"],
        wants="Tolls, by extortion if need be",
        offers="A living on the river for men nobody else will have",
    )
