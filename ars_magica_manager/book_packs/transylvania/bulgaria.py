"""Bulgaria, the Transylvanian Tribunal's southern lands, as of 1220: the
Second Bulgarian Empire of Tsar Ivan Asen II from the Danube to the
Rhodopes; the oppida Evredika (the Orphic magi of the Rhodopes, with
Gela, the Devil's Throat, Perperikon and the Rock Womb), Seuthopolis
(the Quaesitors and lictors, with the Red and Black Libraries) and
Tablinum (the museum of regiones in the Danube delta, with the
Transylvania Chronicle), and their thirteen named magi; the Shipka Pass
regio where the Tribunal meets; the Valley of the Thracian Kings,
Starosel, the Madara Plateau, the Rila Mountains and the Seven Lakes;
Tarnovo, Sredets, the Bulgarian Church, Rila and the Bogomils, in
paraphrase of Against the Dark chapter four.

The creatures (Saint Ivan Rilski, the vilas of the Seven Lakes, the
Madara Horseman and his Lion, Starosel's genius, the false Kabeiros)
are the Bestiary's and are only named in the places they haunt. Keys:
the region is places["bulgaria"]; the Tribunal's meeting place is
places["shipka_pass"]; the oppida are covenants["evredika"],
["seuthopolis"] and ["tablinum"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, joined_lines, paragraphs, vf_art
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from . import Transylvania

BONISAGUS = "house_bonisagus"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"
GUERNICUS = "house_guernicus"
TREMERE = "house_tremere"

#: The lead line of an oppidum's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _add(transylvania: Transylvania, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = transylvania.b.place(name, **kw)
    transylvania.places[key] = place
    return place


def build(transylvania: Transylvania) -> None:
    b = transylvania.b
    tribunal = transylvania.tribunal
    if tribunal is None:
        tribunal = next(iter(b.saga.tribunals), None)
    assert tribunal is not None, "tribunal.py builds the Tribunal first"
    _region(transylvania)
    _danube(transylvania)
    _mountains(transylvania)
    _plains(transylvania)
    _rhodopes(transylvania)
    _thrace(transylvania)
    _evredika(transylvania, b, tribunal)
    _seuthopolis(transylvania, b, tribunal)
    _tablinum(transylvania, b, tribunal)
    _lords(transylvania, b)
    _churches(transylvania, b)
    _towns(transylvania, b)
    _factions(transylvania, b)


# ------------------------------------------------------------- the region


def _region(transylvania: Transylvania) -> None:
    _add(
        transylvania,
        "bulgaria",
        "Bulgaria",
        summary=paragraphs(
            "The Second Bulgarian Empire, which in 1220 holds most of the "
            "Balkans between the Black Sea and the Morava, and Wallachia "
            "beyond the Danube too. Its capital is Tarnovo; Niš, Sredets "
            "and Silistra are its great cities, and Varna and Nesebar its "
            "ports. Its young tsar, Ivan Asen II, means to win back the old "
            "empire's glory, and if the saga follows history he will within "
            "ten years master Thrace, Macedonia and Epiros and push west "
            "into Serbian lands as far as Belgrade.",
            "The land has always lived by its roads: the Danube and the "
            "Romanian plain carry trade from the Bosphorus to Central "
            "Europe, and so does the old highway by Adrianople, Plovdiv, "
            "Sredets, Niš and Belgrade. The fertile Danube lowlands in the "
            "north feed the empire; the Stara Planina runs across its "
            "middle; south of it lie the Sredets and Thracian plains, "
            "divided at the Gates of Trajan; and the Rila, Pirin and "
            "Rhodope ranges close the south.",
            "Thracians, Romans, Goths and Slavs all settled it before Khan "
            "Asparukh's Bulgars crossed the Danube in 679 to 681 and built "
            "the First Bulgarian Empire, which lasted until Byzantium "
            "swallowed it in 1018. Krum took Hungary and Transylvania in "
            "803 and died suddenly in 814 after beating two emperors and "
            "besieging Constantinople; Boris was baptised about 870 as "
            "Michael; Symeon took the title of tsar and gave the Church "
            "its own head in 926. Pechenegs, Magyars and Uzes followed. "
            "The brothers Teodor Petar, Ivan Asen and Kaloyan broke "
            "Byzantine rule in 1185, and Kaloyan, who reigned from 1197 to "
            "1207, rebuilt the empire.",
            "Bulgarians are stocky and dark, hard-working, tolerant and "
            "welcoming, steadier than the Serbs but stubborn fighters for "
            "a cause they think just. The men wear loose trousers tucked "
            "into tall boots, the women bright skirts, and both "
            "embroidered shirts with waistcoats or bodices.",
            "Hermetically, three oppida lie here: Evredika, the scattered "
            "sancta of the Cult of Orpheus in the Rhodopes; Seuthopolis, "
            "the Quaesitors' town near the Shipka Pass, where the Tribunal "
            "meets; and Tablinum, the museum of regiones in the Danube "
            "delta. Gigas, the Theban Tremere lodge south-west of Sofia, "
            "lies just over the border.",
            "Vis here (each in its place): the silivriak of the Rhodopes "
            "(Imaginem) and the bones of the Devil's Throat (Corpus), both "
            "Evredika's; Tablinum's Vim distillery; and Starosel's Terram "
            "and Herbam, which no oppidum holds.",
        ),
        **KNOWN_ORDER,
    )


# --------------------------------------------------------------- the Danube


def _danube(transylvania: Transylvania) -> None:
    region = transylvania.places["bulgaria"]
    _add(
        transylvania,
        "danube_delta",
        "The Danube Delta",
        inside=region,
        summary=paragraphs(
            "Where the Danube meets the Black Sea it spreads into a "
            "wilderness of swamp, reed beds and marsh covering perhaps a "
            "thousand square miles, home to vast flocks of white pelicans "
            "and egrets. South of it the Dobrudja is a dry country of sandy "
            "steppe and low hills full of copper, poor in a drought but "
            "very rich where it can be watered. Tablinum hides among the "
            "dunes and wetlands of the coast.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "galleries_tarnovo",
        "The Galleries of Tarnovo",
        inside=region,
        summary=paragraphs(
            "The Roman city of Nikopolis ad Istrum stood some twelve "
            "miles north of Tarnovo until the Huns sacked it in 447. "
            "Legend says its people fled to Trapezitsa Hill carrying "
            "the city's riches, dug passages deep into the rock, and "
            "hid the hoard there behind deadly traps. Treasure seekers "
            "have hunted it ever since, and the townsfolk fear its "
            "traps and its curse.",
        ),
        secrets="A Tarnovo man who has found a tunnel beneath his house looks "
        "for foreign adventurers to explore it, since no local will "
        "go down; he means to cheat them of whatever gold they bring "
        "out.",
        **RUMOURED,
    )
    _add(
        transylvania,
        "baldwins_tower",
        "Baldwin's Tower",
        inside=region,
        summary=paragraphs(
            "A tower over Tarnovo's Frankish quarter, built to hold "
            "Baldwin, the Latin emperor of Constantinople, whom Tsar "
            "Kaloyan took in battle in 1205. Kept at first as a "
            "precious hostage, Baldwin ruined himself by courting "
            "Kaloyan's Cuman wife (or, some say, she charged him with "
            "rape when he refused her); he was bricked up inside, his "
            "cries carried over the quarter for months and then "
            "stopped, and the tsar told the pope he was dead.",
            "Some say Kaloyan beheaded him and drank from his skull, "
            "and that his headless body, unburied, walks around the "
            "tower seeking vengeance on the Asens. At least one band "
            "of foreigners has tried to break in to free him, and "
            "failed: the tower cannot be forced.",
        ),
        secrets="Others insist Baldwin still lives, a prisoner the present "
        "tsar keeps for some purpose of his own.",
        **KNOWN_LOCALLY,
    )


# ----------------------------------------------------------- the mountains


def _mountains(transylvania: Transylvania) -> None:
    region = transylvania.places["bulgaria"]
    stara = _add(
        transylvania,
        "stara_planina",
        "The Stara Planina",
        inside=region,
        summary=paragraphs(
            "The Old Mountains, Haemus to the ancients: a narrow chain "
            "running nearly four hundred miles west from the Black Sea "
            "through the heart of Bulgaria. High meadows feed sheep and "
            "cattle, beech woods cover the middle slopes, and the foothills "
            "are farmed. The range shields the Thracian Plain from the "
            "hard winters of the Romanian side.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "shipka_pass",
        "The Shipka Pass",
        inside=stara,
        levels=[
            Builder.level(
                "The Tribunal regio",
                3,
                notes=(
                    "The book gives no aura; 5 is the pack's. A terraced "
                    "valley with the Hall of the Tribunal between the "
                    "Western and Eastern Promenades, a giant winged foot "
                    "of Hermes carved at each end."
                ),
            )
        ],
        summary=paragraphs(
            "The best way through Bulgaria's mountains, near Seuthopolis. "
            "In the Order's early years Tremere himself fought a band of "
            "Theban magi here, and beside the battlefield lies a regio: "
            "some think it older than the fight and the place Tremere laid "
            "his ambush, others that the battle's strain threw some magus "
            "into Twilight and made it. For a long time afterwards House "
            "Tremere and the Theban covenants met in it to reflect and to "
            "sign treaties.",
            "When House Guernicus took over the Tribunal site from the "
            "Praeco, and was asked to hold yearly Tribunals so that justice "
            "came quicker and trained apprentices were accepted sooner, the "
            "Quaesitors chose this regio: it was close to Seuthopolis and "
            "already had buildings. The full Tribunal every seven years is "
            "more a festival than a parliament, so the hall need not be "
            "large.",
            "Groups of magi raise splendid temporary buildings on the "
            "valley's terraces, as lodgings, shops and places of "
            "amusement; new coloniae often first show themselves by "
            "pitching a tent on the Western Promenade, west of the hall, "
            "while visitors from other Tribunals, especially those with "
            "goods to sell, gather on the Eastern. Strolling the "
            "Promenades with friends, again and again with each circle one "
            "belongs to, is the great pleasure of a meeting, and newcomers "
            "are told to bring good boots. Redcaps race on foot between "
            "the two carved winged feet of Hermes that mark the regio's "
            "ends, and some take the races very seriously.",
            "The Hall of the Tribunal is little more than an immense roof "
            "on plain columns of a Greek sort, a few carved in honour of "
            "magi who served the Order greatly, under a magically lit and "
            "richly decorated ceiling. Every magus of the Tribunal has a "
            "seat, in horseshoe rows around a dais, with room for a hundred "
            "more; on the dais stands the Praeco's oak throne, about whose "
            "making many tales are told. The servants of the visiting magi "
            "find the meetings full of romance, wagers, games and gossip.",
        ),
        **KNOWN_TRIBUNAL,
    )
    rila = _add(
        transylvania,
        "rila_mountains",
        "The Rila Mountains",
        inside=region,
        summary=paragraphs(
            "The range south of Sredets, whose northern peak, Mount "
            "Vitosha, looms over the Sredets Plain; with the Pirin to the "
            "south it nearly meets the Stara Planina at the Gates of "
            "Trajan. Saint Ivan Rilski's monastery and his hermitage lie "
            "here, and the Seven Lakes high above.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "rilski_cave",
        "Ivan Rilski's Cave",
        inside=rila,
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "Saint Ivan Rilski (John of Rila), hermit, healer and mystic, "
            "who died in 946, lived twelve years in this cave, three in a "
            "hollow oak and seven on a high rock above it; the disciples "
            "his fame drew became the monastery that still stands. Cave, "
            "tree and rock each hold a Divine aura of 4, apart from the "
            "monastery's own Dominion aura of 3. The saint's uncorrupted "
            "body now lies at Tarnovo. Saint Ivan Rilski himself, Bulgaria's "
            "patron, is in the Bestiary.",
            "Story seed: the monks speak for the nation's saint and sway "
            "the bolyeri, but before they grant a favour they may require "
            "the petitioners to repeat his life in little, twelve days in "
            "the cave, three in the oak and seven on the rock, while the "
            "saint tries the purity of their purpose. Those who pass may "
            "win the monastery's friendship; the same ordeal could serve "
            "as Initiation into a Holy Tradition of the saint.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "seven_lakes",
        "The Seven Lakes",
        inside=rila,
        realm="Faerie",
        aura=3,
        levels=[
            Builder.level(
                "The lake regiones",
                6,
                "Faerie",
                notes=(
                    "Each of the seven lakes has its own Faerie regio of 6, "
                    "the home of its vila: top to bottom Salzata "
                    "('Tear'), Okoto ('Eye'), Babreka ('Kidney'), "
                    "Bliznaka ('Twin'), Trilistnika ('Trefoil'), "
                    "Ribnoto Ezero ('Fish Lake') and Dolnoto Ezero "
                    "('Lower Lake')."
                ),
            )
        ],
        summary=paragraphs(
            "A chain of lakes high in the Rila Mountains, between about "
            "6,900 and 8,200 feet, where faerie magic makes the water run "
            "from one lake to the next in no sensible order. The district "
            "has a Faerie aura of 3. A water-maiden vila, one of seven "
            "jealous sisters, lives in each lake (see the Bestiary); each "
            "offers a bather a faerie gift for a year and a day as her "
            "guest beneath the water, and must kill the guest on the last "
            "day.",
            "Story seed: each sister's gift is a Minor Virtue with a "
            "Faerie Charm, and each can save the bearer from another "
            "sister's way of killing. Locals advise beginning at Babreka, "
            "whose gift sees through glamour and so defeats Dolnoto, the "
            "best illusionist; Dolnoto's gift, a lesser immunity to "
            "poison, is said to beat the sister who poisons her guests. "
            "Working out the order in which the water flows gives the "
            "order of the visits, and whoever wins all seven gifts is said "
            "to become the sisters' lord, owed their homage and obedience.",
        ),
        **KNOWN_LOCALLY,
    )


# -------------------------------------------------------------- the plains


def _plains(transylvania: Transylvania) -> None:
    region = transylvania.places["bulgaria"]
    _add(
        transylvania,
        "starosel",
        "Starosel",
        inside=region,
        aura=6,
        summary=paragraphs(
            "A tomb temple of Bendis, the Thracian earth goddess, on "
            "the Thracian Plain, ringed by a wall of huge dressed "
            "stones carved with suns. The tomb is a mound reached by a "
            "broad stone stair to a landing; its cave-like door, "
            "framed in cut stone, opens on a plain antechamber and a "
            "splendid domed inner chamber painted with a bright "
            "frieze. It has a strong Magic aura of 6.",
            "Vis: Terram and Herbam, gathered within a few yards of "
            "the temple (the book gives no amounts).",
            "A fine site for a new oppidum, with ready-made and easily "
            "held walls, but it has a guardian: the place's genius "
            "loci, a hazy woman's shape of black earth and red clay "
            "with great power over earth, who can rouse the plants to "
            "help her and hates all change (see the Bestiary). Settlers "
            "must defeat or lastingly appease her; vis gatherers may "
            "strike a bargain to guard the temple for her in return.",
        ),
        secrets="The genius may or may not be the goddess once worshipped "
        "here; its Magic nature suggests not, and if so, something "
        "befell Bendis that settlers would be wise to learn first.",
        **KNOWN_TRIBUNAL,
    )
    madara = _add(
        transylvania,
        "madara_plateau",
        "The Madara Plateau",
        inside=region,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "A plateau that rises from the Thracian Plain in a sheer cliff "
            "more than three hundred feet high, long holy to the Bulgar "
            "shamans, with a Faerie aura of 3. At its foot a path climbs "
            "to a great cave under an overhang, green with plants and "
            "watered by a small spring: a natural theatre where the old "
            "Bulgars honoured three water nymphs.",
        ),
        **KNOWN_REGION,
    )
    _add(
        transylvania,
        "madara_horseman",
        "The Madara Horseman",
        inside=madara,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "Seventy-five feet up the Madara cliff a vast relief shows "
            "a rider spearing a lion under his horse's hooves, with an "
            "eagle flying before him and a hound behind: one of the "
            "Bulgar shamans' gods. Close to the carving the Faerie "
            "aura rises to 5.",
            "The right faerie rite wakes the Horseman, and his horse, "
            "hound and eagle, which are part of his glamour, with him; "
            "the lion, a faerie in its own right, wakes too, and he "
            "must fight and beat it while he lives. He guards the "
            "local people he swore to protect and goes at once against "
            "whatever he judges their worst danger. Neither he nor the "
            "Lion (Faerie Might 20 or more each, the Lion's matching "
            "his) can be killed for good: the legend is so strong that "
            "other faeries of the region take up their glamour and they "
            "can be called again.",
        ),
        secrets="Story seed: a bolyar the magi know begs them to shelter him "
        "from the Horseman, loosed on him, he says, by a faerie "
        "wizard. In truth he paid the wizard to raise the Horseman "
        "against his enemies, but the Horseman had heard his people's "
        "prayers and judged the bolyar's pride and ambition the "
        "region's worst threat. The wizard only failed to warn him. "
        "If the magi let things run their course, the Lion may "
        "interfere.",
        **KNOWN_REGION,
    )


# ----------------------------------------------------------- the Rhodopes


def _rhodopes(transylvania: Transylvania) -> None:
    region = transylvania.places["bulgaria"]
    rhodopes = _add(
        transylvania,
        "rhodopes",
        "The Rhodope Mountains",
        inside=region,
        summary=paragraphs(
            "A tangle of ridges and valleys in the south, with summer "
            "pasture above woods of pine and fir, and since antiquity the "
            "heart of the worship of Orpheus and of Zagreus (the Greeks' "
            "Dionysus), Thrace's two great gods. The magi of Evredika keep "
            "their scattered sancta here in caves, stout houses and hidden "
            "stone towers.",
            "The silivriak, the Orpheus flower, grew from the singer's "
            "blood when the Maenads killed him: its pink bell flowers "
            "spring up anew each year even from a plant dried or scorched "
            "in a fire, and the year's first blooms give Evredika "
            "Imaginem vis. A vis-bearing flower is a Plant of Virtue that "
            "can be Enriched: write a poem each day for ninety days and "
            "recite them to it, then crush it and anoint three strings of "
            "an old-style lyre with its juice. The lyre gives its player "
            "Enchanting Music 3, effective only on the bereaved, which "
            "cannot be improved and replaces the player's own score; each "
            "broken string (on a botch, say) takes away a point for good.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "gela",
        "Gela",
        inside=rhodopes,
        summary=paragraphs(
            "Evredika's: a small village in the central Rhodopes, the "
            "legendary birthplace of Orpheus. The Cult of Orpheus keeps a "
            "sanctum here, usually held by a magus with the Gentle Gift, "
            "who has a yearly grant of vis from the oppidum (as a Personal "
            "Vis Source) and in return must teach music and performance to "
            "anyone who asks. The village is now known for its musicians "
            "and draws pupils, Gifted and not, from the whole region. The "
            "magi of Evredika gather once a year in a green meadow near "
            "it, ringed by mountains, when the silivriak blooms.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "devils_throat",
        "The Devil's Throat",
        inside=rhodopes,
        aura=4,
        summary=paragraphs(
            "Evredika's: Diavolsko Garlo, a great cave into which a "
            "waterfall plunges far underground, said (though other places "
            "make the same claim) to be the door to Hades that Orpheus "
            "used to seek Eurydice. The Thracians once threw their dead "
            "kings down the fall to speed them to the afterlife. At the "
            "bottom the water pools in a still, dark lake, and on its shore, "
            "in the din of the falls, is the sanctum that by custom belongs "
            "to the oppidum's Tremere aedile. Magic aura 4.",
            "The Orphic magi, who take Orpheus's descent as a journey of "
            "the spirit, care little for the site; they hold it for its "
            "history, and for the Corpus vis that now and then washes up "
            "on the lake shore as pieces of old skeletons.",
        ),
        **KNOWN_TRIBUNAL,
    )
    perperikon = _add(
        transylvania,
        "perperikon",
        "Perperikon",
        inside=rhodopes,
        aura=3,
        summary=paragraphs(
            "Evredika's: a stone city on a hilltop in the eastern "
            "Rhodopes, once a great shrine of Zagreus, left empty by "
            "ordinary folk for centuries. The small town that has grown "
            "at the foot of the hill calls it the City of Ghosts; "
            "Evredika's covenfolk secretly live among the ruins and may "
            "account for some of the tales. Magic aura 3.",
            "At its centre is an oval hall with a round altar on a stone "
            "dais: the oracle of Zagreus-Dionysus where Alexander learnt "
            "he would conquer Asia. A line of minor hedge wizards still "
            "takes auguries there the old way, pouring wine on the altar, "
            "setting it alight and reading the future in the flames; "
            "these priests are initiates of Divination and Augury who "
            "chiefly use pyromancy.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "rock_womb",
        "The Rock Womb",
        inside=perperikon,
        summary=paragraphs(
            "Evredika's: a cave near Perperikon shaped like a womb, with a "
            "carved altar at its far end. At noon a shaft of sun through a "
            "hole cut in the roof throws the shape of a phallus on the "
            "floor, and in January and February, with the sun low, on the "
            "altar itself; then the cave fills with a strong Magic aura of "
            "fertility (the book gives no number). Childless women come to "
            "lie with strangers here to conceive, and the children often "
            "carry magical blood.",
            "A magus seeking the lost Fertility Magics may find Insight "
            "here, for instance by watching by magic the whole growth in "
            "the womb of a child conceived in the cave, which might show "
            "how to align children to Supernatural Virtues or Abilities.",
        ),
        **KNOWN_LOCALLY,
    )


# --------------------------------------------------------------- Thrace


def _thrace(transylvania: Transylvania) -> None:
    region = transylvania.places["bulgaria"]
    caverns = _add(
        transylvania,
        "seuthopolis_caverns",
        "The Caverns of Seuthopolis",
        inside=region,
        aura=5,
        summary=paragraphs(
            "Seuthopolis's: under the fortified town lie the caverns of "
            "the old Thracian cult, with a Magic aura of 5 save in a few "
            "places. The magi use part of them for laboratories and "
            "libraries.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "martyred_virgin",
        "The Crypt of the Martyred Virgin",
        inside=caverns,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "Seuthopolis's: a vault in the caverns, hallowed by a martyred "
            "virgin's bones (Divine aura 3) and wrapped in layer "
            "on layer of magical defences. The Red and Black Libraries are "
            "kept here together, which troubles even magi who accept that "
            "they must exist; the Quaesitors answer that the vault cost a "
            "fortune and could not easily be built again.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        transylvania,
        "thracian_valley",
        "The Valley of the Thracian Kings",
        inside=region,
        summary=paragraphs(
            "The burial ground of the kings of ancient Thrace, close "
            "to Seuthopolis, their old capital, found four years ago "
            "by a Tremere necromancer then serving as a hoplite (the "
            "book gives no aura). House Tremere's necromancers were "
            "delighted; House Verditius wants to dig too, since the "
            "Thracians worshipped gods of the forge. Benilda, minding "
            "an old saying never to trust a happy necromancer, keeps "
            "everyone out for now, knowing Tremere will win in the end; "
            "she hopes to look first herself, or to steer who digs and "
            "why.",
            "Saga seed: an excavation must be hidden from mundanes, "
            "get past cunningly trapped tombs, calm guardian spirits "
            "the magician kings left and the diggers wake, judge the "
            "magic items among the grave goods and whether they help "
            "Original Research, and learn of the Cabeiri, the "
            "Thracians' gods, and the powers they gave their servants, "
            "perhaps by journeys into the Magic or Faerie realms or by "
            "seeking Initiation into their Mysteries.",
        ),
        secrets=joined_lines(
            "The false Kabeiros (see the Bestiary), a strong local "
            "faerie, is reviving the Cabeiri cult here: a tall brass "
            "man with a great crab claw for a left hand, which serves "
            "him as smith's tongs and to punish the unjust. He courts "
            "the servants of Quaesitors, posing as the guide of kings "
            "and giver of justice. His cult has four degrees "
            "(Interrogator, Invader, Observer, Liberator), all "
            "initiated in the valley on a holy day under a Vow to give "
            "fair and swift justice; they confer Piercing Gaze, "
            "Invasive Eyes, Bright Eyes and Eyes of Theseus, and he can "
            "take back Eyes of Theseus from the disloyal. He wants to "
            "teach Second Sight but has not yet stolen it from anyone.",
            "He took the idea from a cult of servants at a Quaesitorial "
            "covenant who long ago worshipped Asmodeus as patron of "
            "prying; an Infernal scholar of the Black Library might "
            "trace it, and Asmodeus may punish the cult if he learns "
            "his idea was reused.",
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------------- Evredika


def _evredika(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    p = transylvania.places
    summary = paragraphs(
        "The oppidum of the Cult of Orpheus, a societas of House Ex "
        "Miscellanea, spread across the Rhodope Mountains to guard the "
        "places of Orpheus's legend, and named for his lost love Eurydice "
        "in her Bulgarian form. Its magi live alone in caves, strong "
        "houses and hidden towers and seldom visit one another, meeting "
        "once a year in a meadow near Gela when the silivriak is in "
        "flower. Its sites are Gela, the Devil's Throat, Perperikon and "
        "the Rock Womb.",
        "When the Cult joined the Order, its two holiest places, on "
        "Lesbos and in the Rhodopes, came into the Hermetic world; the "
        "Rhodope cult, decades old by then, became an oppidum in 1001. "
        "Its five Orphic magi are foederati; the sixth is the aedile, "
        "always a Tremere, whom the House takes care to pick for respect "
        "for the Cult's ways and some love of music. Oeagrus drives most "
        "of them to ask for a new posting within about ten years.",
        "Approaches to the Theban Tribunal, where Evredika might seem to "
        "belong, met scorn from the Theban Jerbiton, who think its music "
        "a peasant's jig and its paganism an offence; its magi would "
        "rather House Tremere ignored them than House Jerbiton sneered.",
        "By the old Orphic rule women may not enter the cult's holy "
        "places and stay in the oppidum's unconsecrated buildings.",
    )
    what_matters = joined_lines(
        "Vis: Imaginem from the year's first silivriak flowers",
        "Vis: Corpus, bone fragments washed up in the Devil's Throat (now and then)",
        "Vis: a yearly grant to the teacher at Gela (a Personal Vis Source)",
        "Aura: Magic 4 at the Devil's Throat, 3 at Perperikon",
        "Library: no books named",
        "Hook: Contested Resource (its vis, which Gigas has been told not to contest)",
        "Hook: Superiors (the Tremere aedile the House posts there)",
        "Tension: Oeagrus and each Tremere aedile, Yekaterina most of all",
        "Tension: the Cult on Lesbos, which Oeagrus thinks hides Orpheus's head",
    )
    notes = paragraphs(
        "The book gives no season, and no single aura for an oppidum "
        "spread over many sites; the Devil's Throat's 4 is used. Three of "
        "its six magi are unnamed.",
        "Story seed: a hunting party led by a noble with a tame white "
        "wolf strips all of Evredika's vis sources, and Gigas, the "
        "Tremere's ill-hidden cat's paw in the Theban Tribunal, seems the "
        "obvious thief. If its protests are honest, who is framing Gigas, "
        "and why?",
    )
    hidden = (
        "Oeagrus keeps the mummified arm of Orpheus and means to remake "
        "the god by grafting his scattered limbs onto his own body."
    )
    evredika = b.covenant(
        "Evredika",
        tribunal=tribunal,
        founded=1001,
        place=p["rhodopes"],
        aura=4,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=3,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["evredika"] = evredika
    b.book(
        evredika,
        "The library of Evredika",
        "Other",
        language="Latin",
        description=(
            "No books are named. Each magus keeps what texts they have in "
            "their own distant sanctum; the Cult's lore is as much music "
            "and song as writing."
        ),
    )
    m = transylvania.magi
    m["oeagrus"] = b.magus(
        "Oeagrus",
        covenant=evredika,
        house=EX_MISC,
        age=109,
        summary=paragraphs(
            "The senior Orphic magus of the Tribunal, looking "
            "sixty-eight, who fancies himself head of the whole Cult, "
            "with no grounds at all. Unlike most of the Cult he "
            "worships Orpheus openly as a god, which has won him no "
            "friends among the Tremere. He thinks the Cult on Lesbos "
            "has Orpheus's head and is keeping it from him. He is "
            "mad: the Cult tends to call it divine madness, everyone "
            "else plain lunacy. He hates women.",
            "Outsiders seldom see him. He goes about in a loincloth, "
            "careless of his looks, his hair wild and twigs caught in "
            "his tangled beard.",
        ),
        secrets="His treasure is the mummified arm of Orpheus, whom the "
        "Maenads tore apart; he seeks a way to rebuild the god by "
        "grafting the dismembered body onto himself.",
        traits={"Devout": 3, "Misogynist": 3, "Domineering": 2},
    )
    m["bozhidar"] = b.magus(
        "Bozhidar",
        covenant=evredika,
        house=EX_MISC,
        age=54,
        summary=paragraphs(
            "The music teacher at Gela, looking thirty-eight, who usually "
            "has two or three pupils. His Study Bonus has made him strong "
            "in Imaginem from what his students bring, and he now needs "
            "ever finer musicians to learn from.",
            "A good-looking man with dark curls and an easy smile, "
            "thickening round the middle since the village's unmarried "
            "women began bringing him honey cakes.",
        ),
        traits={"Easily Enraptured": 3, "Tolerant": 1, "Brave": -2},
    )
    m["yekaterina"] = b.magus(
        "Yekaterina",
        covenant=evredika,
        house=TREMERE,
        age=48,
        summary=paragraphs(
            "Evredika's aedile, the latest of a line, looking thirty-two. "
            "Oeagrus usually sours each 'Tremere overseer', as he calls "
            "them, enough that they ask to leave after a decade or so, and "
            "he takes a woman in the post as a double insult from the "
            "House. She means, for now, to stay, and from her lonely "
            "sanctum in the Devil's Throat has deepened her study of "
            "necromancy.",
            "Slender and fair, she wears a mask made of a skull, which she "
            "has begun to turn into her talisman.",
        ),
        traits={"Tenacious": 2, "Morbid": 1, "Passionate": -2},
    )
    privileges = transylvania.privileges
    privileges["oeagrus"] = ("foederati", "")
    privileges["bozhidar"] = ("foederati", "")
    privileges["yekaterina"] = ("cives", "")
    transylvania.aediles["evredika"] = ["yekaterina"]


# ------------------------------------------------------------ Seuthopolis


def _seuthopolis(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    p = transylvania.places
    summary = paragraphs(
        "A walled town at the Tribunal's southern edge and the base of its "
        "Quaesitors and hoplites, on the border with the Theban Tribunal, "
        "where its magi fairly well keep the two Tribunals' quarrels from "
        "turning into raids across the line. It also looks after the "
        "Tribunal's meeting place in the Shipka Pass nearby.",
        "Seuthopolis was the Thracian capital when Rome came, ruled by a "
        "priest king of underworld gods whose rites Rome stamped out. A "
        "small sect of Verditius magi revived them in a Theban covenant, "
        "the Covenant of the Four Divinities, always two senior Verditius "
        "and two juniors (one now and then of another House), four being "
        "a holy number to the Cabeiri cult. After some friction its "
        "members came over to Transylvania as foederati. Over the "
        "centuries the cult faded and the oppidum became the Tribunal's "
        "seat of justice.",
        "House Guernicus forbids its members to worship the old Thracian "
        "gods: three of the House have been removed from office for "
        "irrational conduct, and the cult seems the thread linking them. "
        "Its initiates take on hubris, as Verditius magi do, and with it a "
        "taste for vendettas.",
        "Outwardly it is an ordinary small Bulgarian walled town, owing "
        "homage to no lord. Local nobles know nobody has ever taken it, "
        "and that those who tried died in ghastly, wondrous ways; the "
        "Quaesitors observe that no neighbouring lord has been melted "
        "into a puddle of boiling gold since they took over, being subtler "
        "than the Verditius, but the tales live on. The magi and their "
        "people live about the town in houses like rich merchants'.",
        "Eight Guernicus magi live here with six lictors. Benilda, the "
        "leader, keeps research, enchanting and Hermetic law for herself, "
        "and sends Vigilia to look into crimes within oppida, Scipio to "
        "mediate between oppida, and Caledonia to punish or to investigate "
        "by force, each with two lictors and a young Guernicus. For "
        "safety only two of the three teams are ever out at once.",
        "In other Tribunals crimes fall between covenants; here, where "
        "magi share oppida, they happen within them, and centuries of "
        "puzzling over how to investigate magi who live side by side have "
        "made these Quaesitors pioneers of their House's Transitionalist "
        "movement. Mediation is a common alternative to a case at "
        "Tribunal, where the Tremere always win but make enemies doing it.",
    )
    what_matters = joined_lines(
        "Aura: Magic 5 in the caverns; the vault of the libraries is Divine 3",
        "Library: the Red and Black Libraries, Benilda's charge",
        "Boon: Hidden Resources (laboratories and libraries in the caverns beneath the town)",
        "Boon: Prestige (no lord has ever taken the town, and the locals know it)",
        "Hook: Hermetic Politics (Transitionalist against Traditional Guernicus)",
        "Hook: Superiors (House Guernicus; the lictors serve House Tremere too)",
        "Duty: keeps the Shipka Pass Tribunal site and calls the yearly Tribunals",
        "Tension: the Valley of the Thracian Kings, which Benilda holds closed against House Tremere",
        "Tension: the Red and Black Libraries, which many think should be burnt",
        "Tension: the old cult of the Cabeiri, banned to Guernicus",
    )
    notes = paragraphs(
        "The book gives no season or founding year. Of its fourteen magi "
        "eight are unnamed: four younger Guernicus and four lictors.",
        "Lictors: hoplites sworn to long service, who guard the "
        "Quaesitors and do as they say. Here a lictor may claim reasonable "
        "help from any cives, socius, foederatus or colona, the Tribunal "
        "judging afterwards how much was reasonable by how great and how "
        "near the danger was. All the Tribunal's lictors belong to the "
        "same body, so all wear the same red and silver sash on formal "
        "occasions, fastened with a silver brooch called an astraea, "
        "usually enchanted: at least three inches long, a pair of wings "
        "spread from a forked lightning bolt, each with its own mark. "
        "Saturnino's is set in a six-inch oval studded with gems in the "
        "pattern of Virgo. Carrying a copy of a lictor's badge is a "
        "serious crime. The mediation and domestic teams' lictors change "
        "often, most serving three years; Terencia and Saturnino stay "
        "longer. The unnamed hoplites are mostly Tremere, but the Prima "
        "has lately moved some of them to Lycaneon, which leaves room for "
        "player characters.",
        "The townsfolk are Greeks, Bulgars and mountain Slavs who went "
        "where the wars of the other two could not easily reach them; the "
        "town has bowed to Byzantine and Bulgarian crowns in turn and is, "
        "with the Latin Empire so weak, under Bulgaria in name. They are "
        "the oppidum folk least shaped by Hermetic service, without the "
        "Tremere virtues of loyalty, letters, arms and merit, and with no "
        "former Redcaps among them: like many Western covenants it is "
        "staffed by people who fled the world for a different life, and "
        "the Quaesitors find their skills, some a little shady, useful.",
    )
    hidden = joined_lines(
        "The town's charter from Diocletian is a clever forgery.",
        "Rumour, perhaps true, says the Red Library also holds "
        "magic items, seized in investigations and never destroyed, "
        "that cast some of the Red Spells; the House might argue "
        "they are lawful to own, and lawful to use on hedge "
        "wizards, the Orders of Odin and Solomon, and Renounced "
        "magi, whom the Code does not protect.",
        "Saturnino thinks gathering the Red and Black Libraries was a grave mistake.",
    )
    seuthopolis = b.covenant(
        "Seuthopolis",
        tribunal=tribunal,
        founded=None,
        place=p["seuthopolis_caverns"],
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        unnamed_magi=8,
        detail=FULL,
        season="Summer",
    )
    transylvania.covenants["seuthopolis"] = seuthopolis
    b.book(
        seuthopolis,
        "The Red Library",
        "Other",
        language="Latin",
        description=paragraphs(
            "It grew from the Red Book, first a list of the sigils of "
            "Diedne magi drawn up after the Schism War so that any who "
            "tried to rejoin the Order could be known by their magic; it "
            "later took in the sigils of every Renounced magus. The book "
            "itself troubles nobody. Benilda and those before her went "
            "further: the Library keeps copies of spells notorious for "
            "having been made to commit Hermetic crimes, kept as evidence "
            "of old crimes for young Quaesitors to learn from.",
            "Among them are The Sleep of the Muses (Perdo Mentem; no "
            "other copy is known), an effect that makes magi forget for a while how "
            "to cast; The Curse of the Unportended Plague, which ruins "
            "cities; and The Trivialization of the Forgetful, which hides "
            "a spoken command in a magus's mind that makes him drop his "
            "Parma Magica. Kept with the Black Library in the Crypt of the "
            "Martyred Virgin.",
        ),
    )
    b.book(
        seuthopolis,
        "The Black Library",
        "Other",
        language="Latin",
        description=(
            "One copy of each of the very few books the Order has made it "
            "a crime to own. It began after the corruption of House "
            "Tytalus, whose fallen Prima Tasgilla wove Infernal taint into "
            "spells and texts on magic theory that she spread through the "
            "Order. The Quaesitors and their allies burnt them after the "
            "House was cleansed, keeping a few so that new copies could be "
            "recognised; some magi think these seeds of corruption should "
            "be destroyed too. Kept with the Red Library in the Crypt of "
            "the Martyred Virgin."
        ),
    )
    m = transylvania.magi
    m["benilda"] = b.magus(
        "Benilda",
        covenant=seuthopolis,
        house=GUERNICUS,
        age=78,
        summary=paragraphs(
            "Chief Quaesitor of the Tribunal and leader of Seuthopolis, a "
            "head of the Transitionalists in House Guernicus. She thinks "
            "the Tremere may be right that the way magi live is going to "
            "change, which will test those who keep justice hard, and "
            "innovates in law to ready her House. She specialises in "
            "investigation and keeps the Red and Black Libraries.",
            "The Traditionalists call her brand of Transitionalism "
            "collusion with House Tremere to bend the Code, but can do "
            "little against her while Tremere backs her: without Tremere "
            "arms the Quaesitors would struggle to make Autumn covenants "
            "elsewhere obey the Code. She thought it feeble of the Prima "
            "of Guernicus to give up reconciling the factions and send them "
            "to fight case by case at Tribunal; but since that is the war "
            "now, with the Order's future at stake, she will play politics "
            "as ruthlessly as any Traditionalist.",
            "She presides at Tribunal, witnesses oaths and binds contracts "
            "into the Peripheral Code; accusations are laid before her, "
            "and she is the Quaesitor characters meet for the Tribunal's "
            "business.",
        ),
        traits={"Assertive": 3, "Stubborn": 2},
    )
    m["caledonia"] = b.magus(
        "Caledonia",
        covenant=seuthopolis,
        house=GUERNICUS,
        age=65,
        summary=paragraphs(
            "The older Quaesitor sent where things are dangerous, raised "
            "(as her name says) in the Loch Leglean Tribunal. She has an "
            "odd faerie blood, that of the Washerwoman of the Ford, which "
            "shows her visions of her own possible death and her foes'. "
            "Her investigative spells are weak, but in Wizard's War she is "
            "skilful and unpredictable, and her speciality is magical "
            "self-defence.",
            "Met on her investigations, she can ask any magus for all "
            "reasonable help: lodging and supplies, and often companions "
            "and grogs with local knowledge or useful skills. She attends "
            "every Wizard's March. She seeks friends among the Merinita, "
            "thought partial in Scotland but of no matter here.",
        ),
        traits={"Determined": 3, "Interested in Faeries": 2},
    )
    m["saturnino"] = b.magus(
        "Saturnino",
        covenant=seuthopolis,
        house=CRIAMON,
        age=None,
        summary=paragraphs(
            "Marshal of Transylvania: House Guernicus's chief hoplite "
            "in the Tribunal, the senior lictor and leader of Wizard's "
            "Marches; his age is unknown. He is one of the elders of "
            "the Path of Strife, Criamon extremists who do evil so that "
            "their Housemates may stay clean, and who, unlike other "
            "Criamon, plunge into the world to dirty themselves. His "
            "House's notion of evil is so strange that he usually seems "
            "a very ordinary magus: eating meat is evil, and so is "
            "having a wife, and he does both.",
            "Only slowly do others see that he finds no moral "
            "difference between a bacon pie and burning a child, and "
            "would do either if it were needed. He knows right from "
            "wrong and, without remorse, picks wrong when it must be "
            "done, so others need not; but he does no pointless "
            "cruelty, will not deal with demons, which he thinks "
            "personal weakness, and will not betray his sect or his "
            "wife, since that would be right. He kills magi well and, "
            "in his own odd terms, can be relied on. He is still a "
            "Criamon, with riddles, strange quests and errands to "
            "magical places, only more often bloody to the elbows. He "
            "excels at surprising foes and at mystical swordplay.",
        ),
        secrets="He serves here because he thinks gathering the Red and Black "
        "Libraries was a deep error, and because he wonders whether "
        "the Tribunal's strange faeries come of the Criamon having "
        "stolen the World Tree.",
        traits={
            "Determined to do evil by doing what others call good": 5,
            "Spooky and enigmatic": 3,
        },
    )
    m["scipio"] = b.magus(
        "Scipio",
        covenant=seuthopolis,
        house=GUERNICUS,
        age=44,
        summary=paragraphs(
            "The mediator, skilled in talk and Mentem magic. At Tribunal "
            "each side argues and the rest vote, so Tremere's opponents "
            "always lose and Tremere wins only by making enemies; with "
            "Scipio between them a magus can settle with another magus or "
            "an oppidum without forcing the House to take sides. He would "
            "like a posting to a Tribunal where, without someone like him, "
            "blood might be shed; his superiors agree he will be useful "
            "there one day, but want him to keep honing his skills first, "
            "since there the smallest slip could be costly.",
            "The easiest of the four Quaesitors to approach: gentle in "
            "manner, less strict about the letter of the law, and willing "
            "to give legal advice. He can sometimes calm a quarrel between "
            "the characters and someone they have angered, though they may "
            "have to give ground.",
        ),
        traits={"Likes untangling problems": 3, "Sociable": 2},
    )
    m["terencia"] = b.magus(
        "Terencia",
        covenant=seuthopolis,
        house=TREMERE,
        age=21,
        summary=paragraphs(
            "A lictor on Caledonia's team and the oppidum's aedile, a "
            "young maga trained as a military scout, whose magic carries "
            "her fast through a country and weighs its dangers. She was "
            "put with Caledonia because the Quaesitor lacks many "
            "investigative spells; she is no great fighter, but Caledonia "
            "is far deadlier than most Quaesitors and her fellow lictor "
            "Saturnino is among the Order's most feared. She hopes a turn "
            "with the Quaesitors will help her to a posting abroad later.",
            "A Rego Corpus specialist with, like many of her House, some "
            "Terram, she wants her talisman to be a trophy of a famous "
            "case she helps Caledonia crack. Knowing she needs friends "
            "among young magi, and wanting some her own age, she is easy "
            "to approach and can help characters against their foes; she "
            "loves the work but never seems to have time to herself.",
        ),
        traits={"Humble (from inexperience)": 2, "Ambitious": 1},
    )
    m["vigilia"] = b.magus(
        "Vigilia",
        covenant=seuthopolis,
        house=GUERNICUS,
        age=76,
        summary=paragraphs(
            "A bitter old maga whom nothing magi do to each other surprises "
            "any more. Her spells find out what magi have done without "
            "breaking the Code, and she specialises in spying on magi. "
            "She always goes with two hoplites strong enough to cut her "
            "free of a camp that is in on a plot: dark Merinita once "
            "ambushed her and took both her legs, and though she regrew "
            "them with Corpus vis, seeing two suspects eat her feet made "
            "her careful.",
            "She is the only working Quaesitor of the Tribunal censured "
            "for breaking the Code, for spying on a magus by accident "
            "while casting without force; she kept her place because her "
            "accuser asked for mercy, but may no longer investigate the "
            "Histrian oppida, where she cannot seem neutral. Characters "
            "are right to distrust her, and she is becoming a problem for "
            "her House, but she is good at reading and undoing magical "
            "defences. She is called to judge whether a magus died in his "
            "laboratory, and to assess ancient magical sites.",
        ),
        traits={"Annoyed by people": 3, "Hates Redcaps": 2},
    )
    b.link(m["terencia"], "characters", m["caledonia"], "Lictor on her team")
    b.link(m["saturnino"], "characters", m["caledonia"], "Lictor on her team")
    privileges = transylvania.privileges
    privileges["benilda"] = ("socii", "")
    privileges["caledonia"] = ("socii", "")
    privileges["saturnino"] = ("hospites", "Marshal of Transylvania, senior lictor")
    privileges["scipio"] = ("socii", "")
    privileges["terencia"] = ("cives", "lictor")
    privileges["vigilia"] = ("socii", "")
    transylvania.aediles["seuthopolis"] = ["terencia"]


# --------------------------------------------------------------- Tablinum

#: Tablinum's regio levels, in the book's order: each is reached only by
#: an Arcane Connection.
_ART_EXHIBITS, _ARCANUM, _SCRIPTORIUM, _SPELL_HALL, _CHRONICLE = 1, 2, 3, 4, 5
_CHAPEL, _SANCTUM, _MIRRORED, _DUNGEON, _EMPTY = 6, 7, 8, 9, 10


def _tablinum_site(transylvania: Transylvania) -> Neighbour:
    level = Builder.level
    open_ = "Open: Tremere by right, others by the Curator's leave."
    restricted = "Restricted: Tremere with good reason; others sometimes, for a fee."
    return _add(
        transylvania,
        "tablinum",
        "Tablinum",
        inside=transylvania.places["danube_delta"],
        summary=paragraphs(
            "On the Black Sea coast among the dunes and marshes of the "
            "Danube delta: to the eye only a palisaded village of a "
            "few grogs of Slav stock who fish from small boats amid "
            "clouds of pelicans and egrets. All that marks it is an "
            "Aegis of the Hearth of magnitude 8 round the palisade "
            "and a magic bell for calling the magi, which makes no "
            "sound except within Tablinum's regiones.",
            "Here dozens of regiones lie on top of one another, each "
            "an exhibition hall: stone buildings joined by covered "
            "wooden walkways, vaulted halls under twisting brass "
            "chandeliers, narrow dark passages lined with scroll "
            "cases, alike in style but different in plan from level "
            "to level. The levels can be sensed but not crossed into "
            "by any path or ritual; one goes in only with an Arcane "
            "Connection and Leap of Homecoming or the like. The "
            "Curator holds Fixed Arcane Connections to most of them, "
            "stone beads on necklaces handed down from Curator to "
            "Curator, and by holding them controls who sees what. "
            "Unless noted, the levels can be entered and left by Rego "
            "Corpus magic.",
            "Outside the halls, where any opening exists, the light "
            "is a thick red, as of a summer evening or dawn, with no "
            "sun in the sky; featureless dunes surround the buildings "
            "and the Black Sea heaves to the east, its salt wind "
            "crusting the eastern walls. Every path through the dunes "
            "leads back to the halls. Some say other, perhaps ruined, "
            "buildings hide among the dunes on some levels.",
            "The Everbright Chandeliers that light the exhibits are "
            "enchanted items (CrIg 24, constant): they give bright "
            "light as from candles, with no flame to set the exhibits "
            "alight.",
        ),
        secrets=joined_lines(
            "Six hidden exhibits are rumoured, which most of the "
            "Tribunal only guesses at; some magi claim to have been "
            "there, and may be liars or mad. Even the Curator may not "
            "hold their Arcane Connections, which a cabal or Mystery "
            "Cult may keep, or which may be lost:",
            "The Founder's Exhibit: realia of the Founders' lives, "
            "first traditions and deaths, some say with several "
            "Founders' bodies on show.",
            "The Lower Dungeon: a web of wards binding hundreds of "
            "demons; its keepers would risk a charge of infernalism.",
            "The Refuge: not an exhibit but stocked laboratories and "
            "lodgings in hidden regiones, readied for House Tremere to "
            "flee to should catastrophe strike the House, the Tribunal "
            "or the world, and outlast it. Hidden laboratories do "
            "exist (Nestor uses one); if disaster such as the Mongols "
            "comes, desperate magi will come here.",
            "The Schism Exhibit: a full record of the Schism War, "
            "including Expurgatio, said to catalogue all the evidence "
            "House Tremere gathered against the Diedne in the decades "
            "before the war, with the artifacts and Lab Texts it "
            "names; called 'the truth', against a public record many "
            "think Tremere propaganda.",
            "The Seeker's Forum: realia of extinct (and not so "
            "extinct) magical traditions the Tremere have recovered "
            "across Mythic Europe, a rich source of Insight.",
            "The Warehouse of Ares: a great store of magic weapons, "
            "many made by both sides around the Schism War, kept "
            "against the day the Order splits in war again.",
        ),
        levels=[
            level(
                "The Art Exhibits",
                5,
                notes=(
                    f"{open_} Fifteen exhibits, one to each Art, each on its "
                    "own level, each a realia of hundreds of objects (the "
                    "Corpus halls full of skeletons and pickled organs, "
                    "flasks foul and pure in the Aquam, caged beasts behind "
                    "Circles of Beast Warding in the Animal). Study Bonus "
                    "and Study Requirement are met here up to an Art of 15."
                ),
            ),
            level(
                "The Arcanum Exhibit",
                6,
                notes=(
                    f"{open_} Four separate realia, on Finesse, Magic "
                    "Theory, Parma Magica and Penetration: star maps of "
                    "horoscopes' effect on Magic Resistance, glassware "
                    "assemblies, rune-covered magical eggs whose runes "
                    "writhe and slip."
                ),
            ),
            level(
                "The Scriptorium",
                4,
                notes=(
                    "Not an exhibit: lodgings for guests' servants and "
                    "companions (visiting magi live in the exhibit they "
                    "study), a guest laboratory with a viewing gallery, and "
                    "six scribes (Profession: Scribe 6, Magic Theory 1) "
                    "copying the Chronicle. Up to two may be hired for 2 "
                    "pawns a season, materials extra; a Tremere may take "
                    "one free, though not two seasons running; writing "
                    "desks are free. A small door leads to the Spell Hall."
                ),
            ),
            level(
                "The Spell Hall",
                4,
                notes=(
                    f"{open_} Archive Lab Texts in filed scroll cases: "
                    "every ArM5 spell, most from the supplements, few "
                    "originals, mostly free of private notation. Tremere "
                    "copy freely; others donate a usable Lab Text (copying "
                    "as many texts as its magnitude) or pay pawns equal to "
                    "the magnitudes copied. No laboratory; texts may not "
                    "leave, though the residents take them anyway."
                ),
            ),
            level(
                "The Chronicle",
                3,
                notes=(
                    f"{open_} Three copies of each of the 90 volumes of the "
                    "Transylvania Chronicle; one copy of a volume may be "
                    "taken out at a time. Anyone may study it."
                ),
            ),
            level(
                "The Chapel",
                6,
                "Divine",
                notes=(
                    f"{open_} The Divine exhibit, a realia in Dominion Lore: "
                    "glowing crosses hang in place of chandeliers over "
                    "mosaics of Christ's life, and jewelled reliquaries "
                    "fill the alcoves, dozens or hundreds of relics among "
                    "them, perhaps an uncatalogued piece of the True Cross. "
                    "The relics' Divine aura has drowned whatever aura the "
                    "level once had."
                ),
            ),
            level(
                "The Curator's Sanctum",
                5,
                notes=(
                    "Nominally open; the residents' lodgings and six "
                    "laboratories, four in use, under the usual sanctum "
                    "law. Nestor's laboratory here is a sham."
                ),
            ),
            level(
                "The Mirrored Hall",
                6,
                notes=(
                    f"{restricted} Hundreds of enchanted metal mirrors in "
                    "warded iron frames, each holding a faerie in its "
                    "reflection: a realia in Faerie Lore."
                ),
            ),
            level(
                "The Dungeon",
                3,
                "Infernal",
                notes=(
                    f"{restricted} A maze of dark passages displaying "
                    "horrors of cruelty and suffering: a realia in "
                    "Infernal Lore that many magi want destroyed. It holds "
                    "more objects than any other exhibit, far more than "
                    "the catalogues say, as anyone who studies it a season "
                    "realises."
                ),
            ),
            level(
                "The Empty Halls",
                3,
                notes=(
                    "Many empty regiones of vacant halls among the dunes, "
                    "with Magic auras of 3 or 4; some say people have been "
                    "stranded or imprisoned in them."
                ),
            ),
        ],
        **KNOWN_ORDER,
    )


#: The Chronicle's years, from the Order's founding, fifty to a set.
CHRONICLE_FROM, CHRONICLE_TO, CHRONICLE_SPAN = 767, 1217, 50

#: Tablinum's laboratories as the book prints them (Against the Dark pp.
#: 62-63): its owner's key ("" for a shared one), the Characteristics,
#: the Specializations and the Virtues and Flaws.
TABLINUM_LABS: tuple[tuple[str, str, dict[str, int], dict[str, int], str], ...] = (
    (
        "Nestor's Laboratory",
        "nestor",
        {
            "size": 3,
            "refinement": 3,
            "general_quality": 1,
            "upkeep": 4,
            "safety": 1,
            "warping": 2,
            "health": 2,
            "aesthetics": 4,
        },
        {"Experimentation": 1, "Teaching": 2, "Rego": 2, "Vim": 3},
        "Greater Feature (orrery), Palatial, Extensive Stores, Specimens, "
        "Missing Sanctum Marker, Regio, Impregnable, Predecessor",
    ),
    (
        "Demetrius's Laboratory",
        "demetrius",
        {"refinement": 3, "general_quality": -1, "safety": 1, "aesthetics": 4},
        {"Texts": 4, "Aquam": 1},
        "Greater Feature (desk), Specimens (Aquam), Studio, Cramped",
    ),
    (
        "Theodora's Laboratory",
        "theodora",
        {
            "refinement": 2,
            "general_quality": 1,
            "upkeep": -1,
            "safety": -1,
            "warping": 2,
            "health": -1,
            "aesthetics": -1,
        },
        {"Experimentation": 6, "Muto": 2, "Perdo": 1, "Terram": 1},
        "Greater Feature (cauldron), Faerie Ingredients (Terram), Dirty, "
        "Disorganized, Chaotic",
    ),
    (
        "Theodore's Laboratory",
        "theodore",
        {
            "refinement": 3,
            "general_quality": 3,
            "upkeep": 2,
            "safety": 3,
            "health": 2,
            "aesthetics": 6,
        },
        {"Vis Extraction": 1, "Creo": 1, "Intellego": 2, "Ignem": 1},
        "Greater Feature (pool), Superior Heating, Flawless Equipment, "
        "Grand Entranceway, Guard, Highly Organized, Spotless, Undecorated",
    ),
    (
        "The Vim Distillery",
        "",
        {"upkeep": -3, "safety": -1, "aesthetics": 1},
        {"Vis Extraction": 10},
        "Greater Feature (vis still), Lesser Feature (vis balance), Missing "
        "Ingredients (Intellego, Muto, Perdo and Rego Lab Totals halved), "
        "Missing Sanctum Marker, Superior Equipment, Cramped, Greater Focus "
        "(vis still)",
    ),
    (
        "The Empty Laboratory",
        "",
        {"upkeep": -1, "safety": -3, "warping": 2, "health": -1, "aesthetics": -3},
        {"Perdo": 1, "Mentem": 3},
        "Vis Source (2 pawns of Mentem a season, frost on the void "
        "window's sill), Empty, Undecorated, Abyss, Haunted",
    ),
    (
        "The Guest Laboratory in the Scriptorium",
        "",
        {"upkeep": -1, "safety": -1},
        {"Teaching": 1},
        "Gallery, No Stores, Undecorated",
    ),
)


def _tablinum(transylvania: Transylvania, b: Builder, tribunal: Tribunal) -> None:
    site = _tablinum_site(transylvania)
    summary = paragraphs(
        "The Tribunal's museum and storehouse, keeping records, spell "
        "texts and artifacts in dozens of regiones in the Danube delta, "
        "each hall reached only by Arcane Connection. It was founded in "
        "878, after the Sundering, where so many regiones overlie one "
        "another; with the Tribunal held to five covenants it had no "
        "standing and no lawful residents, only a place to keep things, "
        "until the idea of oppida spread and it remade itself as one, with "
        "resident Curators. The Curator holds office for life.",
        "Any Tremere may use the open exhibits, and others usually by the "
        "Curator's leave; vandals and thieves, Tremere too, are thrown out "
        "for good, at least in theory. Most of the restricted exhibits "
        "open to Tremere with good reason and to others now and then, "
        "sometimes for a fee. Exhibits are studied as realia, of Source "
        "Quality from about 5 (cursory) to 11 or more (unparalleled), "
        "lessened when several share one; a rival for an exhibit turns up "
        "unless a stress die beats 3, and certamen for love often settles "
        "who studies.",
        "Upkeep, checking wards, renewing preserving spells, feeding the "
        "Animal exhibit, takes one magus full time, with about a dozen "
        "grogs housed in the Scriptorium; the four residents each give it "
        "a season a year.",
        "Nestor pays collectors, in vis or access to restricted exhibits "
        "(or duplicate objects), for things from a named place or for a "
        "named exhibit; grogs and companions are paid in money. Owners, "
        "magi among them, may call it theft. Tremere collectors may serve "
        "in the vexillation Convectoris-Tablinum.",
    )
    what_matters = joined_lines(
        "Aura: Magic 5 in the Curator's Sanctum; ten listed levels from Infernal 3 to Divine 6",
        "Defence: an Aegis of the Hearth of magnitude 8 round the village palisade",
        "Vis: Vim, extracted from the aura in the shared Vim Distillery (Vis Extraction +10)",
        "Library: the Transylvania Chronicle, the Spell Hall and the exhibits as realia",
        "Boon: Regio (dozens of halls reached only by Arcane Connection)",
        "Boon: Hidden Resources (the Curators' necklaces of Arcane Connections)",
        "Hook: Superiors (the Tribunal appoints the Curator; Tremere has rights of access)",
        "Hook: Contested Resource (rival scholars, and owners of collected objects)",
        "Tension: the Dungeon and the Chapel's relics, which many want destroyed or returned",
        "Tension: Nestor's fear of a Tremere plot against him",
    )
    notes = paragraphs(
        "The book gives no season. All four magi are named.",
        joined_lines(
            "Past Curators:",
            "878-900 Akilina, the first, who found the site in the mid-800s, named her apprentice Potitus to follow her, resigned and vanished in 917; presumed dead, though magi as late as 1137 claim to have met her, or someone using her name, in the regiones.",
            "900-948 Potitus, the first to live there, who opened the storehouse to study.",
            "946-1007 Tiberia, a Tremere general named by Potitus and briefly Curator with him; killed in the Schism War.",
            "1007-1018 Anatolus, also a Tremere general and the first chosen by the Tribunal, known for strange battle magic said to come from Tablinum; killed in Wizard's War.",
            "1018-1020 no Curator.",
            "1020-1027 Silus, charged with infernalism and Marched.",
            "1027-1080 Justius, said to have dismantled several Infernal exhibits and driven demons from many levels.",
            "1080-1102 Scribonius, who wrote the first 'complete' catalogue, then resigned, left House Tremere for House Jerbiton in Thebes, and died in 1137.",
            "1102-1170 Calpurnius, who greatly enlarged the Faerie collection.",
            "1170- Nestor, known for his study of regiones.",
        ),
        "How so many sealed regiones came to lie here is unknown; they and "
        "their Arcane Connections existed by 900, when the Chronicle first "
        "mentions them. One story says a ritual path through a labyrinth "
        "once led into all of them, and the founders walked it fixing "
        "Arcane Connections and destroying the labyrinth behind them.",
        joined_lines(
            "Laboratories:",
            "Nestor's true laboratory, in an otherwise empty level, used by Curators for centuries: Greater Feature (orrery), Palatial, Extensive Stores, Specimens, Missing Sanctum Marker, Regio, Impregnable, Predecessor; Size +3, Quality +1, Refinement +3, Safety +1, Upkeep +4, Health +2, Warping +2, Aesthetics +4; Experimentation +1, Teaching +2, Rego +2, Vim +3.",
            "Demetrius's: Greater Feature (desk), Specimens (now Aquam, changed in a few days), Studio (where new acquisitions wait), Cramped; Size 0, Quality -1, Refinement +3, Safety 1, Upkeep 0, Health 0, Warping 0, Aesthetics +4; Texts +4, Aquam +1.",
            "Theodora's: Greater Feature (an ever-boiling cauldron), Faerie Ingredients (faerie rocks), Dirty, Disorganized, Chaotic; Size 0, Quality +1, Refinement +2, Safety -1, Upkeep -1, Health -1, Warping +2, Aesthetics -1; Experimentation +6, Muto +2, Perdo +1, Terram +1.",
            "Theodore's: Greater Feature (a still pool), Superior Heating, Flawless Equipment (dwarf-made), Grand Entranceway, Guard, Highly Organized, Spotless, Undecorated; Size 0, Quality +3, Refinement +3, Safety +3, Upkeep +2, Health +2, Warping 0, Aesthetics +6; Vis Extraction +1, Creo +1, Intellego +2, Ignem +1.",
            "The Vim Distillery, shared: Greater Feature (vis still), Lesser Feature (vis balance), Missing Ingredients (Intellego, Muto, Perdo and Rego Lab Totals halved), Superior Equipment, Greater Focus (vis still), Missing Sanctum Marker, Cramped; Size 0, Quality 0, Refinement 0, Safety -1, Upkeep -3, Health 0, Warping 0, Aesthetics +1; Vis Extraction +10.",
            "The Empty Laboratory, stripped and haunted by a magus murdered there in Wizard's War, with a window open on a void: Vis Source, Empty, Undecorated, Abyss, Haunted; Size 0, Quality 0, Refinement 0, Safety -3, Upkeep -1, Health -1, Warping +2, Aesthetics -3; Perdo +1, Mentem +3.",
            "The guest laboratory in the Scriptorium: Gallery, No Stores, Undecorated; all Characteristics 0 save Upkeep -1 and Safety -1; Teaching +1.",
        ),
        "Story seed: a Church delegation arrives while the magi study "
        "here. Since 1204 the Latins hold much of Constantinople, and "
        "scholars there have read in Greek Church records of Tablinum's "
        "hoard of relics; a papal legate comes to learn whether it exists "
        "and, if so, to take the relics to Rome. Nestor asks the visiting "
        "magi to help him deal with it.",
    )
    hidden = joined_lines(
        "The Empty Laboratory's void window is a vis source the "
        "residents do not know of: now and then frost forms on its "
        "sill that can be gathered as Mentem vis before it melts, "
        "2 pawns a season. The ghost knows.",
        "Nestor keeps most of the Curators' necklaces hidden and "
        "carries only the one for the most visited levels; his "
        "real laboratory is in a level of its own.",
        "The Dungeon's excess: either infernalists with their own "
        "Arcane Connections use it to hide their cult's "
        "paraphernalia, coming and going by Leap of Homecoming, or "
        "Hell has got in, and possessed exhibits are summoning "
        "more demons into the hall.",
        "Theodore once told Nestor many exhibits should be "
        "destroyed, and lately told Demetrius the Order has "
        "outlived its purpose.",
    )
    tablinum = b.covenant(
        "Tablinum",
        tribunal=tribunal,
        founded=878,
        place=site,
        level=_SANCTUM,
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        secrets=hidden,
        detail=FULL,
        season="Autumn",
    )
    transylvania.covenants["tablinum"] = tablinum
    chronicle = (
        "The Transylvania Chronicle, kept at Tablinum: the Tribunal's "
        "record of events since the Order's founding in 767, richly "
        "illustrated, 90 volumes in 1220, two to a decade, three copies "
        "of each. It claims to be complete, but says little of the years "
        "before the Schism War or of House Tremere's founding; it is "
        "still the Tribunal's first source for Peripheral Code rulings "
        "and Hermetic history. It is an encyclopedia: every fifty years "
        "(ten volumes) counts as a quality 6 tractatus on Order of Hermes "
        "Lore (Transylvania) and one on Code of Hermes, nine sets in all. "
        "To look up a fact takes about an hour and a stress roll of "
        "Intelligence plus Code of Hermes or Order of Hermes Lore, +1 for each "
        "full fifty years one can consult that bear on the question (+9 "
        "for the whole). The scribes in the Scriptorium copy it."
    )
    # Each fifty years, ten volumes, is a tractatus on each subject:
    # nine of each from 767 to 1216, bound as one encyclopedia (Against
    # the Dark p. 63).
    volumes = []
    for start in range(CHRONICLE_FROM, CHRONICLE_TO, CHRONICLE_SPAN):
        years = f"{start}-{start + CHRONICLE_SPAN - 1}"
        for subject, ability in (
            ("Order of Hermes Lore", "Organization Lore: Order of Hermes"),
            ("Code of Hermes", "Code of Hermes"),
        ):
            volumes.append(
                b.book(
                    tablinum,
                    f"The Transylvania Chronicle, {years} ({subject})",
                    "Tractatus",
                    ability=ability,
                    quality=6,
                    description=chronicle,
                )
            )
    b.codex("The Transylvania Chronicle", volumes, encyclopedia=True)
    b.book(
        tablinum,
        "The Spell Hall",
        "Other",
        language="Latin",
        description=(
            "Tablinum's archive of Lab Texts, hundreds of filed scroll "
            "cases: every spell of the core rules, most of the "
            "supplements' (as the troupe allows), and few original spells, "
            "nearly all in a form other magi can use without translation. "
            "Tremere copy freely; others pay by donating a usable Lab Text "
            "(one copy for each magnitude) or in vis, a pawn per magnitude "
            "copied. Texts may be copied but not taken away or worked from "
            "in the hall, which has no laboratory. With the exhibits, which "
            "are studied as realia, it makes up the oppidum's library."
        ),
    )
    m = transylvania.magi
    m["nestor"] = b.magus(
        "Nestor",
        covenant=tablinum,
        house=TREMERE,
        age=93,
        summary=paragraphs(
            "Curator of Tablinum since 1170, looking forty-eight: tall and "
            "bone-thin, in a monk's habit dyed bright yellow, walking with "
            "a quick, jerky, insect-like stride. His sigil is a tic of "
            "teleportation, made far worse by his Twilights: he vanishes "
            "and reappears an instant later half a step away.",
            "He affects to live apart from Tribunal politics, as for years "
            "he truly did, but for a decade he has feared that other "
            "Tremere are plotting against him, though he has found no "
            "plot. He knows that finding none may mean he is going mad, "
            "and since there might be a plot he dares tell no one of "
            "either fear. He may be both mad and the target of a plot.",
            "He studies what he believes is the drift of regiones "
            "against one another: Leap of Homecoming, he says, takes a "
            "tiny, measurable time that depends on the levels left and "
            "reached and changes from trip to trip, and a great brass "
            "orrery in his laboratory, whose spheres are regiones, plots "
            "their motion. He has found no use for it, may be quite "
            "wrong, and will not raise the subject, but will eagerly "
            "compare notes with a magus who does.",
        ),
        traits={"Reclusive": 3, "Paranoid": 3},
    )
    m["demetrius"] = b.magus(
        "Demetrius",
        covenant=tablinum,
        house=BONISAGUS,
        age=32,
        summary=paragraphs(
            "Tablinum's aedile, trained in the Theban Tribunal, young, "
            "keen to learn and fluent in Latin, Greek and Arabic. Born "
            "Basem in the Saracen lands, he was cast out by his village "
            "for his Blatant Gift and was living like a beast in the waste "
            "when a Bonisagus Seeker passing by found him. He now "
            "understands his Gift and bears his family no grudge, but "
            "abandonment left him desperate to please new friends: he "
            "knows it and tries not to act like an anxious puppy, though "
            "he usually sees how foolish he looked only after some "
            "pleading offer is made.",
            "His sigil is a faint pop, as if something small left the "
            "world, louder as his spells grow stronger. He spends long "
            "hours fixing the catalogues, shamefully wrong in his view, "
            "and means to send copies to the other Tribunals, since "
            "sharing knowledge was Bonisagus's vision; he suspects the "
            "others here do not agree.",
        ),
        traits={"Friendly (too)": 6, "Nervous": 2},
    )
    m["theodora"] = b.magus(
        "Theodora",
        covenant=tablinum,
        house=TREMERE,
        age=58,
        summary=paragraphs(
            "Theodore's twin, looking twenty-eight. Nestor took in the "
            "twins as bawling infants and hid them with two nurses in a "
            "secret regio until their Gifts could be Opened and he could "
            "claim them as apprentices. Theodora is noisy, her hair long "
            "and matted and her habits filthy, and screams, spits and "
            "throws things when crossed, yet she forgets slights quickly "
            "and bears with the beast in everyone. She took her longevity "
            "potion in her early twenties out of vanity and soon rued the "
            "barrenness it brought.",
            "Her magic, like her laboratory, is showy and reckless: she "
            "keeps tipping new ingredients, seemingly at random, into an "
            "ever-boiling cauldron, which she swears improves her magic, "
            "and her laboratory does often turn out work beyond her.",
        ),
        traits={"Wild": 3, "Loud": 3},
    )
    m["theodore"] = b.magus(
        "Theodore",
        covenant=tablinum,
        house=TREMERE,
        age=58,
        summary=paragraphs(
            "Theodora's twin, though looking sixty he could pass for her "
            "father. He hardly speaks except to the two nurses who raised "
            "them, now old women in their seventies, one almost blind and "
            "one bedridden, who still live in the nursery regio. He never "
            "raises his voice and keeps himself, his clothes and his "
            "laboratory spotless, with grogs guarding its door in shifts; "
            "he spends hours gazing at the still pool at its heart.",
            "His ideas are strange. He thinks body hair breeds disease and "
            "keeps himself hairless by magic, and he put off his longevity "
            "potion until fifty, perhaps only to mock his sister.",
        ),
        traits={"Aloof": 3, "Sober": 2},
    )
    b.link(
        m["nestor"], "characters", m["theodora"], "His apprentice, raised at Tablinum"
    )
    b.link(
        m["nestor"], "characters", m["theodore"], "His apprentice, raised at Tablinum"
    )
    b.link(m["theodora"], "characters", m["theodore"], "Her twin")
    privileges = transylvania.privileges
    privileges["nestor"] = ("cives", "Curator of Tablinum")
    privileges["demetrius"] = ("hospites", "")
    privileges["theodora"] = ("cives", "")
    privileges["theodore"] = ("cives", "")
    transylvania.aediles["tablinum"] = ["demetrius"]
    for name, owner, traits, specializations, vfs in TABLINUM_LABS:
        b.laboratory(
            tablinum,
            name,
            owner=m[owner] if owner else None,
            characteristics=traits,
            specializations=specializations,
            source="Against the Dark pp. 62-63",
            rooms={"Virtues and Flaws": vfs},
        )


# ------------------------------------------------------- the mundane world


def _lords(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["bulgaria_tsar"] = b.lord(
        "Tsardom of Bulgaria",
        title="duke",
        wealth="Wealthy",
        manors=100,
        seat="Tarnovo",
        ruler="Tsar Ivan Asen II",
        place=p["bulgaria"],
        summary=paragraphs(
            "The Second Bulgarian Empire. Its ruler styles himself Emperor "
            "and Autocrat of all Bulgarians and Vlachs, lord of a people "
            "rather than of lands. Ivan Asen II, nephew of Kaloyan, has "
            "reigned only two years but already shows promise, beginning "
            "with his marriage to the King of Hungary's daughter; he is "
            "aggressive and set on restoring the empire. Kaloyan's Cuman "
            "marriage gave the tsars an alliance with the Cumans that must "
            "be renewed by rite each summer, and the empire still fights "
            "with Cuman mercenaries.",
            "The tsar rules through the bolyeri, a hundred noble families "
            "of great and lesser bolyars; the great bolyars and the "
            "Patriarch form the Sinklit, the council that advises him. The "
            "land is divided into horas under a kefaliya (a duke), each "
            "with one or more katepans (counts) ruling katepanikons. "
            "(Duke is the app's highest title.)",
            "No one doubts the Asens' right to rule, but no one knows what "
            "it rests on: the brothers came from nowhere to lead the "
            "revolt, and while most think them Bulgarian, some say Vlach "
            "or even Cuman. Their obscure past worries many, the Order "
            "among them, and their strange and seemingly inherited power "
            "to sway crowds is something to fear, or to use.",
        ),
    )


def _churches(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["tarnovo_archbishop"] = b.church(
        "The Archbishopric of Tarnovo",
        church="Archbishop's cathedral",
        place=p["bulgaria"],
        summary=paragraphs(
            "The head of the Bulgarian Church, at the Patriarshiya on the "
            "top of Tsarevets Hill. The Church traces itself to Saints "
            "Cyril and Methodius, whom Boris I welcomed in 886; "
            "Constantinople granted it its own patriarch after the peace "
            "of 927, and took that away in 1018, when it shrank to an "
            "archbishopric at Ohrid led by Greek clergy.",
            "The Asens restored its independence with a new archbishopric "
            "at their capital, and when the Patriarch of Constantinople "
            "would not accept it they turned to Rome: in 1203 Innocent III "
            "named the Archbishop of Tarnovo Primate of all Bulgaria and "
            "Wallachia, joining it to the Latin Church, though Ohrid stays "
            "Orthodox. Tsar and archbishop are thought still to be seeking "
            "union with the Orthodox, on their own terms.",
        ),
    )
    w["rila_monastery"] = b.church(
        "The Monastery of Saint Ivan Rilski, Rila",
        church="Monastery or nunnery",
        order="Orthodox monks",
        place=p["rila_mountains"],
        summary=(
            "The community that grew from the disciples of Saint Ivan "
            "Rilski, with a Dominion aura of 3 apart from the Divine 4 of "
            "his cave, oak and rock. Its monks, thought to speak for the "
            "nation's patron saint, carry great weight in Bulgarian "
            "politics, and may set those who want their help the saint's "
            "own ordeal."
        ),
    )
    w["rilski_tarnovo"] = b.church(
        "The Monastery of Saint Ivan Rilski, Tarnovo",
        church="Monastery or nunnery",
        place=p["bulgaria"],
        summary=(
            "Within the walls of Trapezitsa Hill in Tarnovo, keeping the "
            "uncorrupted body of Saint Ivan Rilski, Bulgaria's patron."
        ),
    )
    w["saint_dimitar"] = b.church(
        "The Church of Saint Dimitar, Tarnovo",
        church="Large urban church",
        place=p["bulgaria"],
        summary=(
            "On the north side of Trapezitsa Hill, dedicated to Demetrius "
            "of Thessaloniki: here the Asens declared their revolt against "
            "Byzantium and the founding of the Second Bulgarian Empire."
        ),
    )
    w["saint_sofia"] = b.church(
        "The Church of Saint Sofia, Sredets",
        church="Bishop's cathedral",
        place=p["bulgaria"],
        summary=(
            "Built in the sixth century under Byzantine rule and lately "
            "made a bishop's seat of the Bulgarian Church, so that people "
            "have begun to call Sredets by the diocese's name, Sofia."
        ),
    )
    w["boyana"] = b.church(
        "The Boyana Church",
        church="Parish church",
        place=p["bulgaria"],
        summary=paragraphs(
            "A church at Sredets, the masterpiece of the city's "
            "craftsmen, whose frescoes Vasiliy, the Boyana Master, is "
            "still painting: the dome is done, with Christ, the "
            "Evangelists, the great feasts, the Passion and ten warrior "
            "saints, and he is now painting Saint Nicholas's life in "
            "eighteen panels in the narthex. His work moves men to "
            "tears; he is a Maestro, and like most of them notices "
            "little but his art.",
        ),
        secrets="An angel has taken Vasiliy under its wing, while a demon has "
        "fixed on the parish priest through his pride in the work, and "
        "the congregation are caught between them. Vasiliy may sense "
        "the struggle and ask for help, or the angel may ask the "
        "characters, or the demon trick them, to finish off the "
        "other.",
    )


def _towns(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    tsar = w["bulgaria_tsar"]
    w["tarnovo"] = b.town(
        "Tarnovo",
        ruler="Tsar Ivan Asen II",
        answers_to=tsar,
        place=p["bulgaria"],
        summary=paragraphs(
            "The capital, in a loop of the Yantra, a Danube tributary, on "
            "two hills the river splits and almost encircles, running in "
            "a gorge often three hundred feet below the walls; the New "
            "Town (Nov Grad) lies between them by the river. Tsarevets, "
            "on the left bank, is a rough triangle behind a wall thirty "
            "feet high and ten thick with three gates: the main gate "
            "(Sechena skala) with its drawbridge, the Small Gate (Malka "
            "porta) with its covered tower facing Trapezitsa, and the "
            "Frankish Gate into the Frankhissar, where foreign merchants "
            "lodge. The tsar's palace has its own second wall; the "
            "Patriarshiya crowns the hill among a dozen more churches, "
            "many paid for by the tsar; and from Execution Rock (Lobnata "
            "skala) at the north end traitors are thrown into the river.",
            "Trapezitsa, on the right bank, has a weaker wall along the "
            "hill's rim, its main gate on the south side, from which a "
            "road cut in the rock crosses the Yantra and the New Town to "
            "the Small Gate; within are Saint Ivan Rilski's monastery and, "
            "on the north slope, the Church of Saint Dimitar. Nobles keep "
            "houses on the hills; craftsmen live in the New Town and in "
            "Assenova on the right bank.",
        ),
    )
    w["sredets"] = b.town(
        "Sredets (Sofia)",
        answers_to=tsar,
        place=p["bulgaria"],
        summary=(
            "A chief city of the First Bulgarian Empire on the wide "
            "Sredets Plain under Mount Vitosha, famed for its craftsmen, "
            "its goldsmiths above all; since its Saint Sofia became a "
            "bishop's seat, people call it Sofia. The Boyana Church is "
            "here."
        ),
    )
    w["seuthopolis_town"] = b.town(
        "Seuthopolis",
        charter="A charter it says Diocletian granted",
        council=5,
        place=p["seuthopolis_caverns"],
        summary=paragraphs(
            "The walled town over the Quaesitors' caverns, laid out "
            "like many small Bulgarian towns, under Bulgaria in name "
            "but paying homage to no noble. A council of five old men "
            "governs it in public: one each for the carpenters, "
            "shepherds, weavers and potters, and a leader chosen from "
            "the four, whose guild at once names another in his "
            "place. Its people are Greeks, Bulgars and mountain Slavs.",
        ),
        secrets="The charter is a skilful forgery; the oppidum of Seuthopolis rules here.",
    )


def _factions(transylvania: Transylvania, b: Builder) -> None:
    w = transylvania.world
    p = transylvania.places
    w["bogomils"] = b.faction(
        "The Bogomils",
        faction="Faith or sect",
        decides="Its leader",
        ruler="The Protos",
        realm="Divine",
        place=p["bulgaria"],
        wants="To free the poor from lords, taxes and the Church's hold on wealth and learning",
        offers="Healing, the casting out of demons, and the loyalty of the downtrodden",
        rules=(
            "Viarvashti, the believers, give up meat, wine, wealth and "
            "begetting to seek perfection; slushateli, the listeners, live "
            "less strictly and may rise; savarsheni, the perfects, lead "
            "and teach. Women and men are equal."
        ),
        summary=paragraphs(
            "A dualist faith, risen in the tenth century, whose name means "
            "'dear to God'; neither tsar nor Church has stamped it out, and "
            "it is notorious across Europe. Bogomils teach that God had two "
            "sons: the elder, Satanael, rebelled and made the lower "
            "heavens, the earth and mankind (God giving the souls), and "
            "bound Adam to pay him homage for the soil; the younger, "
            "Michael, came as the man Jesus and broke that bond, so "
            "Satanael had him crucified and raised the Church to bind men "
            "anew. Whatever society makes is thus Satan's: they refuse "
            "taxes, serfdom and war, shun churches, sacraments and holy "
            "symbols, and pray in houses, holding to the Gospels, some "
            "epistles, the Psalms and the Prophets.",
            "They are led by the Protos, with four great fraternities "
            "(obshtini): the Bulgarian, the Romana, the Dragometsia "
            "of Macedonia and the Meliniqua of Serbia, each under a dedets, a "
            "kind of bishop, helped by starets, elders. Champions of the "
            "poor, they resist crown and Church from quiet refusal to open "
            "revolt, and their wandering preachers, who heal and drive out "
            "demons, have seeded movements far away, the Cathars of "
            "Provence among them.",
            "A Divine faith outside Christianity: their gatherings usually "
            "raise a Dominion aura of Calm temper, at odds with the "
            "Orthodox Church's, that fades between services. Dedetsi and "
            "starets hold Wise One, dedetsi Temporal Influence too; their "
            "missionaries are often of a Holy Tradition or Mythic "
            "Companions, like the Cathar Perfecti but with Intervention or "
            "Adjuration in place of Transcendence.",
        ),
    )
    w["sinklit"] = b.faction(
        "The Sinklit",
        faction="Council or assembly",
        decides="A council",
        ruler="Tsar Ivan Asen II",
        place=p["bulgaria"],
        wants="A say in the tsar's policy and the great bolyars' standing",
        offers="Counsel, troops and the lands of the hundred noble families",
        summary=(
            "The Bolyar Council: the great bolyars of Bulgaria's hundred "
            "noble families, with the Patriarch, who advise the tsar on "
            "policy. A bolyar who needs a favour from the magi, or whom "
            "the magi need, most likely sits here or serves one who does."
        ),
    )


# --------------------------------------------------------------- stats

P = Profile
BULGARIAN = "Bulgarian"
GREEK = "Greek"
ITALIAN = "Italian"
AREA = "Area Lore: Bulgaria"
ORPHEUS = "Mystery Cult Lore: Cult of Orpheus"


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "oeagrus": P(
        strong="pre com sta",
        weak="dex qik",
        arts={"Im": 9, "Me": 7, "Co": 6, "Cr": 4, "Re": 4},
        abilities={
            "Music": (6, "the lyre"),
            ORPHEUS: (6, "Orpheus's relics"),
            "Magic Lore": (3, "Orphic sites"),
            AREA: 2,
        },
        virtues=["Sorcerous Music", "Pagan (Minor)", "Obsessed (Major)", "Delusion"],
        native=GREEK,
    ),
    "bozhidar": P(
        strong="com pre int",
        arts={"Im": 10, "Me": 5, "Cr": 4, "Re": 3, "Au": 2},
        abilities={
            "Music": (6, "singing"),
            "Teaching": (5, "music"),
            ORPHEUS: 3,
            AREA: 2,
        },
        virtues=[
            "Gentle Gift",
            "Study Bonus",
            "Compulsion (Minor)",
            "Fear",
            "Dutybound",
            "Carefree",
        ],
        native=BULGARIAN,
    ),
    "yekaterina": P(
        strong="int sta per",
        weak="com pre",
        arts={"Co": 8, "Me": 8, "Pe": 6, "In": 4, "Re": 4, "Te": 2},
        abilities={
            "Magic Lore": (4, "ghosts"),
            "Infernal Lore": (2, "the restless dead"),
            "Music": 2,
            AREA: 3,
        },
        virtues=[
            ("Minor Magical Focus", {"focus": "the dead"}),
            "Driven (Minor)",
            "Dispassionate",
        ],
        native=BULGARIAN,
    ),
    "benilda": P(
        strong="int com pre",
        arts={"In": 9, "Me": 7, "Vi": 6, "Re": 5, "Cr": 4, "Te": 3},
        abilities={
            "Code of Hermes": (8, "the Peripheral Code"),
            "Intrigue": (5, "Hermetic politics"),
            "Folk Ken": (4, "magi"),
            "Magic Theory": (6, "enchantments"),
            "Leadership": 3,
            "Organization Lore: Order of Hermes": 4,
        },
        virtues=[
            "Hermetic Prestige",
            "Inventive Genius",
            "Ambitious (Minor)",
            "Enemies",
        ],
        native="High German",
    ),
    "caledonia": P(
        strong="sta per int",
        arts={"Pe": 8, "Ig": 7, "Re": 6, "Vi": 6, "Co": 5, "In": 1},
        abilities={
            "Penetration": (6, "Wizard's War"),
            "Faerie Lore": (4, "the Merinita"),
            "Parma Magica": (6, "Ignem"),
            "Code of Hermes": 4,
            "Area Lore: Loch Leglean": 2,
        },
        virtues=[
            ("Faerie Blood", {"blood": "the Washerwoman of the Ford"}),
            "Driven (Minor)",
            "Visions",
        ],
        native="Gaelic",
    ),
    "saturnino": P(
        strong="dex qik sta",
        arts={"Pe": 9, "Co": 8, "Ig": 6, "Re": 6, "Me": 5, "In": 4},
        abilities={
            "Enigmatic Wisdom": (6, "the Path of Strife"),
            "Single Weapon": (6, "sword"),
            "Mystery Cult Lore: Path of Strife": 4,
            "Penetration": (5, "magi"),
            "Stealth": 3,
        },
        virtues=["Tough", "Vow (Minor)", "Depraved (Minor)"],
        age=80,
        native=ITALIAN,
    ),
    "scipio": P(
        strong="com pre int",
        arts={"Me": 9, "In": 7, "Re": 5, "Cr": 3, "Im": 3},
        abilities={
            "Folk Ken": (6, "magi"),
            "Charm": (4, "calming tempers"),
            "Etiquette": (4, "Tribunals"),
            "Code of Hermes": 5,
            "Intrigue": 3,
        },
        virtues=["Social Contacts", "Ambitious (Minor)", "Compassionate (Minor)"],
        native=ITALIAN,
    ),
    "terencia": P(
        strong="per qik sta",
        arts={"Re": 8, "Co": 7, "Te": 4, "In": 4, "Mu": 3},
        abilities={
            "Awareness": (4, "ambushes"),
            "Survival": (3, "mountains"),
            "Stealth": 3,
            AREA: 2,
        },
        virtues=[vf_art("Affinity with {art}", "rego"), "Ambitious (Minor)", "Humble"],
        native=BULGARIAN,
    ),
    "vigilia": P(
        strong="int per sta",
        weak="pre com",
        arts={"In": 10, "Me": 7, "Vi": 6, "Co": 5, "Re": 4},
        abilities={
            "Magic Lore": (5, "magical sites"),
            "Finesse": (5, "subtle casting"),
            "Code of Hermes": 5,
            "Penetration": 4,
        },
        virtues=[
            "Subtle Magic",
            "Cautious Sorcerer",
            "Hatred (Minor)",
            "Infamous",
            "Low Tolerance",
        ],
        native=ITALIAN,
    ),
    "nestor": P(
        strong="int per sta",
        weak="pre com",
        arts={"Re": 12, "Vi": 10, "In": 8, "Co": 6, "Te": 5, "Mu": 4},
        abilities={
            "Magic Lore": (8, "regiones"),
            "Magic Theory": (8, "regiones"),
            "Organization Lore: Order of Hermes": 4,
            AREA: 3,
        },
        virtues=[
            "Inventive Genius",
            "Hermetic Prestige",
            "Twilight Prone",
            "Reclusive",
            "Secretive",
        ],
        native=BULGARIAN,
    ),
    "demetrius": P(
        strong="int com per",
        arts={"In": 8, "Aq": 6, "Vi": 6, "Cr": 5, "Re": 4},
        abilities={
            "Living Language: Greek": (5, "scholarship"),
            "Organization Lore: Order of Hermes": (4, "libraries"),
            "Magic Theory": (6, "texts"),
            "Profession: Scribe": 3,
        },
        virtues=["Linguist", "Book Learner", "Blatant Gift", "Feral Upbringing"],
        native="Arabic",
    ),
    "theodora": P(
        strong="pre sta qik",
        arts={"Mu": 9, "Te": 8, "Pe": 6, "Cr": 5, "An": 4},
        abilities={
            "Magic Theory": (6, "experimentation"),
            "Faerie Lore": (2, "faerie stones"),
            "Brawl": 2,
        },
        virtues=["Inventive Genius", "Wrathful (Minor)", "Reckless (Minor)"],
        native=BULGARIAN,
    ),
    "theodore": P(
        strong="int sta per",
        weak="com pre",
        arts={"In": 9, "Cr": 6, "Ig": 5, "Aq": 5, "Co": 4, "Pe": 3},
        abilities={
            "Magic Theory": (6, "laboratory hygiene"),
            "Concentration": (4, "contemplation"),
            "Medicine": (2, "disease"),
        },
        virtues=["Clear Thinker", "Delusion", "Aloof", "Secretive"],
        native=BULGARIAN,
    ),
}


def stats(transylvania: Transylvania) -> None:
    """Generated stats for the magi of Bulgaria, none of whom has a
    printed stat block."""
    b = transylvania.b
    for key, profile in PROFILES.items():
        apply(b, transylvania.magi[key], profile)
