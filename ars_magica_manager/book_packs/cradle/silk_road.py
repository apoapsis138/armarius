"""The Silk Road and beyond: Transoxiana, Bactria, Farghana, Badakhshan,
the Wakhan and the lands to Khashgar and the steppe (TC&TC ch09), in
paraphrase.

Places: the region places["silk_road"] (no `inside`); its provinces
places["transoxiana"], with ["khwarazm"], ["sogdiana"], ["farghana"]
and ["bactria"] inside it, and ["badakhshan"] and ["wakhan"]; and
places["great_steppe"] (Great Tengri). The sites, by slug: ["oxus"]
(its spirits), ["old_oxus_bed"] (Magic 2, Aquam vis, C17),
["jaxartes"] (its Faerie spirit and the road from Arcadia at Talas),
["aral_sea"] and in it ["jabal_jaghrahaz"] (Magic 4, the marid
Jaghrahaz), ["kyzylkum"], ["sogdian_rock"] (Magic 3, a candidate
covenant site, C16), ["ai_khanoum"] (Magic 4, an altar of Alexander)
with ["ai_khanoum_gymnasium"] (Magic 7) inside it, ["kalyan_minaret"]
(Divine 7, a regio level 8), ["ismail_tomb"] (Magic 3 by night,
Divine 3 by day), ["jobs_spring"] (Faerie 3, its vis), ["kasri_orifon"]
(the wishing tree, a Faerie regio level 2), ["otrar_ruins"] (Infernal
6, Uqana's ghost), ["shahr_i_zindah"] (Faerie 5 by day, Infernal 5 by
night, with Rostam's mace), ["gutluk_temir"] (Magic 7, the sahirs who
keep the Oxus spirits bound, C5), ["wakhan_road"] (Faerie 2 rising to
6), ["lahzvard"] (the lapis mines and the Lapis of Virtue's Corpus),
["roof_of_world"] (Magic 4), ["taklimakan"] (two wandering auras of
7), ["yenghissar"] (the buran's village), ["turris_lapidae"] (the
Stone Tower, Rumoured) and ["janaindar"] (the City Above the Clouds,
Rumoured). Naw Bahar is zoroastrians.py's; Khashgar the jinn land is
jinn.py's (places["khashgar"]), linked from the town in finish.

Towns (world): ["bukhara"] (order.py puts its house of wisdom there:
the key is kept), ["samarkand"], ["otrar"], ["gurganj"], ["balkh"],
["khojend"], ["osh"], ["kath"], ["khashgar_town"], ["tashkent"] and
["talas"].

Lords (C13): world["genghis_khan"], the Great Khan, with the six
origins the book offers under secrets= and none chosen (C21), and the
Qara Khitai as a faction of kind "Faerie court", beaten in 1218
(world["qara_khitai"]). East.py's world["mongol_conquest"] is not
remade: its place is set to Bukhara when it has none; persia.py's
world["khwarazm_shah"] is set in Khwarazm here.

Itineris Serica and Cartophilius are stories.py's (C20). Creatures
with stats (the Heavenly Horse, the ruq, the Asian elephant, the
Bactrian camel, the steppe pony, the lesser steppe spirits, the buran
and the Mongol templates) are bestiary.py's; beings named without
stats are sentences at their places. Vis sources are lines in their
places' summaries (C17); the book gives no place vis without a source
here, so none has suggested sources. The book's story seeds are
stories.py's to add in its finish (C22)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs, titled

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Cradle

RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}
RUMOURED_LOCALLY: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _place(cradle: Cradle, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = cradle.b.place(name, **kw)
    cradle.places[key] = place
    return place


def _town(cradle: Cradle, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a town and keep it under `key` for the other parts."""
    town = cradle.b.town(name, **kw)
    cradle.world[key] = town
    return town


def build(cradle: Cradle) -> None:
    _regions(cradle)
    _rivers(cradle)
    _khwarazm(cradle)
    _sogdiana(cradle)
    _bactria_and_farghana(cradle)
    _the_east(cradle)
    _the_steppe(cradle)
    _lords(cradle)
    _shared(cradle)


def finish(cradle: Cradle) -> None:
    """Link to the jinn's lands once jinn.py has made them, and place the
    shared records still nowhere."""
    _shared(cradle)
    b, places, w = cradle.b, cradle.places, cradle.world
    khashgar = places.get("khashgar")
    if khashgar is not None:
        b.link(w["khashgar_town"], "places", khashgar, "The jinn city behind it")
    qaf = places.get("qaf")
    if qaf is not None:
        b.link(places["roof_of_world"], "places", qaf, "Part of Qaf, in legend")


def _shared(cradle: Cradle) -> None:
    """The Mongol conquest begins at Bukhara and the Khwarazm-shah sits in
    Khwarazm, when no part has placed them."""
    w = cradle.world
    conquest = w.get("mongol_conquest")
    if conquest is not None and conquest.place_id is None:
        conquest.place_id = w["bukhara"].id
    shah = w.get("khwarazm_shah")
    if shah is not None and shah.place_id is None:
        shah.place_id = cradle.places["khwarazm"].id


# -- the regions --


def _regions(cradle: Cradle) -> None:
    region = _place(
        cradle,
        "silk_road",
        "The Silk Road",
        summary=paragraphs(
            "The way to Serica, the land of silk, which is taking shape "
            "once more as the century opens: by putting down the "
            "endless banditry of the east, the Mongols' invasion, "
            "strangely, makes the road safer for merchants and "
            "missionaries. It has existed since antiquity, open or shut "
            "by turns, and is not one road but a web of caravan stages "
            "joined by caravanserais, branching and meeting again "
            "through desert, steppe and mountain as the caravans go "
            "north-east from Baghdad, through Khurasan and on into "
            "Transoxiana, Badakhshan and the Wakhan, past the edge of "
            "the Mythic Middle East and into the supernatural realms "
            "beyond.",
            "Local rulers keep caravanserais, stone stations with water "
            "and a small garrison, a day's journey apart (ten to "
            "fifteen miles). Asses, camels, horses or mules carry the "
            "goods as the ground allows; great caravans come down from "
            "the Volga Bulghars and the northern forests through Merv, "
            "Baghdad, Samarkand or Khojend, and go on west by Venetian "
            "hands or east by Sogdian ones. Some are towns on the move: "
            "Ibn Fadlan saw one of up to 3,000 beasts and 5,000 men. "
            "Such a caravan could hide a wandering covenant, or carry a "
            "troupe of the region's own.",
            "The Asian elephant is still kept in small numbers in the "
            "east, by nobles as a curiosity and by the Khwarazmian army "
            "as shock troops; elephants fear nothing that crawls but "
            "flee a pig's squeal. Ghosts of ancient war elephants can be "
            "called up from their bones on old battlefields across "
            "Arabia, Persia and Transoxiana, and the bones of the faerie "
            "war elephants of Hind that Alexander's armies met lie in "
            "the far eastern mountains and the southern deserts of "
            "Persia.",
        ),
    )
    _place(
        cradle,
        "transoxiana",
        "Transoxiana",
        inside=region,
        summary=paragraphs(
            "Mawara'n-nahr, the Lands Beyond the River, Turan to the "
            "Persians: the borderland past the Oxus, always at the edge "
            "of civilisation. The Khwarazm-shah rules it in name. It "
            "takes in the old oases of Farghana, Sogdia and Bactria, the "
            "river-mouth province of Khwarazm and the jinn-ridden "
            "Kyzylkum, with the endless steppe to the north-east and the "
            "Pamir and the Paromisidae walling it to the east.",
            "Qutayba's Arabs swept over it in the seventh century, and "
            "Islam's tide broke there on the edge of the steppe. Islam "
            "changed as it went: strict Sunni ways took little root, but "
            "ecstatic Sufism, with its likeness to the nomads' shamans "
            "and its charismatic holy men, did better, and many who "
            "profess Islam still keep pagan beliefs and folk customs "
            "tied to the local Faerie and Magic spirits. Nomad overlords "
            "have come and gone and the river oases have had dynasties "
            "of their own; no one power has held both herdsman and "
            "townsman since the old Turk Empire, until now.",
            "Two great rivers bound and shape it, a border of trade and "
            "changing cultures between the wild steppe beyond the "
            "Jaxartes and the towns south of the Oxus. A third, the "
            "lesser Zeravshan, 'the golden', runs past Samarkand and "
            "Bukhara and dies in the desert before it reaches a sea. To "
            "the north-west lies the Bahr Khazar, the Caspian, beyond "
            "which the Khazars once ruled, nomads who took up Judaism and "
            "held Islam back in the ninth century before fading into the "
            "steppe; the tales they left have bred Faerie jinn that ape "
            "their kingdom. Travellers past the Caucasus to the sea's "
            "far shore may find the Amazons' secret isle (Rival Magic), "
            "and beyond it the outer reaches of Jinnistan.",
        ),
    )
    t = cradle.places["transoxiana"]
    _place(
        cradle,
        "khwarazm",
        "Khwarazm",
        inside=t,
        summary=paragraphs(
            "Transoxiana's farming heart, a province of canals and "
            "gardens at the Oxus mouth, and home of the warlike "
            "Khwarazm-shah, Sultan Mohammed II Iskander, whose deeds "
            "have brought the Mongols down on it. It grows great crops "
            "of cotton and keeps big flocks of sheep and herds of cattle "
            "in the marshes among its canals; it trades chiefly, in "
            "costly furs from the Bulghar lands among much else, and "
            "above all in Turkish slaves: young nomads bought or stolen "
            "from the steppe, schooled in Islam and sent to every corner "
            "of the Islamic world.",
        ),
    )
    _place(
        cradle,
        "sogdiana",
        "Sogdiana",
        inside=t,
        summary=paragraphs(
            "Since antiquity a land of merchants and go-betweens, still "
            "a place of crossroads and caravans: the main roads from "
            "Baghdad run through it by Samarkand to the Turkish lands "
            "beyond. Once the heartland of the Manichean heresy, it "
            "holds a passing mix of trading faiths, Sunni Muslims, "
            "Nestorian Christians and Jews.",
        ),
    )
    _place(
        cradle,
        "farghana",
        "Farghana",
        inside=t,
        summary=paragraphs(
            "The broad open valley north-east of Sogdiana, the furthest "
            "east that Islam's first wave reached. It is famous for "
            "horses, metalwork and above all weapons, and has good oil "
            "and bitumen; Arab armies fill clay pipes with its oil as "
            "fire bombs in sieges, a trick the Mongols will learn. The "
            "Heavenly Horses of its valley head, said to be sired by "
            "river dragons or divine steeds on the wild herds, are "
            "sought by magi and Gifted sahirs alike, for the Gift does "
            "not trouble them, and envoys from Serica are said to come "
            "great distances for a single one.",
        ),
    )
    _place(
        cradle,
        "bactria",
        "Bactria",
        inside=t,
        summary=paragraphs(
            "Bactriana, lately called Tokharistan: the lands between "
            "the Oxus and the Caucasus Indicus, long a melting pot and a "
            "breeding ground of revolt. Cyrus made it a satrapy; it "
            "fought off Alexander, then became the heart of the Seleucid "
            "empire and of an independent Greek kingdom. Sakas, Kushans, "
            "Sasanids, Hephthalites and Arabs conquered it in turn, but "
            "its back country keeps many classical monuments and ties to "
            "the Faerie powers of Greek myth: outside the Theban "
            "Tribunal no part of the Mythic Middle East has more Greek "
            "buildings.",
        ),
    )
    _place(
        cradle,
        "badakhshan",
        "Badakhshan",
        inside=region,
        summary=paragraphs(
            "Mountains famed for rubies, sapphires and other jewels, "
            "rising into the Caucasus Indicus south of a great northward "
            "bend of the Oxus and cut by its chief tributary, the Nahr "
            "Dirgham (the Badakhshan or Kokcha river). The ancients "
            "called it Balascia and set it on the north face of the "
            "south-eastern slopes of Mount Imeon. Rid now of the "
            "Shansabani of Bamiyan, whose demons ruled it from the "
            "south, it is a borderland of the old world, known to the "
            "traders who cross it from north-west to south-east.",
        ),
    )
    _place(
        cradle,
        "wakhan",
        "The Wakhan",
        inside=region,
        summary=paragraphs(
            "The narrow land along the Oxus from lower Badakhshan up "
            "to its fabled source, home of the Vakhi, shy herdsmen whose "
            "Parsi is so odd that speakers of it are at -3. A trade "
            "route has climbed the valley to Serica since antiquity, "
            "though no merchant yet says he has made the whole journey "
            "and come back; now and then strange travellers and pilgrims "
            "arrive in the west claiming to have come the other way, "
            "with tales of the mountains and of the cities of their "
            "homes in the Taklimakan beyond.",
        ),
    )


# -- the great rivers --


def _rivers(cradle: Cradle) -> None:
    t = cradle.places["transoxiana"]
    _place(
        cradle,
        "oxus",
        "The Oxus",
        inside=t,
        summary=paragraphs(
            "The Jahyun of the Arabs, the Turks' Amu Darya, wrongly "
            "taken for Gihon, a river of Eden, and always a frontier of "
            "the classical world. The people of Qarabolaq in the high "
            "Pamir say it is born of the eerie Lake Zorkul near by; the "
            "old geographers, that it melts out of an ice cave under a "
            "glacier high in the Wakhan. In winter the lower Oxus and the "
            "Jaxartes freeze, so caravans, and now nomad armies, cross "
            "with ease.",
            "Its delta's spirit was once one great Magic spirit; the "
            "clash of peoples on its lower banks has split it into a "
            "throng of lesser ones as the river splits into channels "
            "and canals towards the Aral Sea. Just short of the sea the "
            "great dykes of Gurganj, magically strengthened with jinn "
            "enslaved by the sahirs of before Islam, turn the river from "
            "its natural course into the canals that water the "
            "province. Faerie, Infernal and Magic river spirits, and "
            "perhaps Divine ones, are bound along that broken lower "
            "course, each with its own name and loyalty, gathering at "
            "times into shifting alliances and courts. One, the captive "
            "Magic spirit Ahurani or Anahit, the remnant of a fertility "
            "yazata older than Zoroaster that the Sogdians adopted, is "
            "yoked to the shah's harvests; the faerie lords called Old "
            "Jahyun and the Son of the Oxus are the most fickle and the "
            "strongest, and a clever magus or sahir might strike a "
            "bargain with one against the other.",
        ),
        secrets=[
            titled(
                "Why the Oxus freezes",
                "The Oxus's winter freeze is the outcome of a running "
                "struggle between the Faerie and Magic jinn who claim the "
                "lands on either bank. In winter the faeries rule and the "
                "rivers ice over, letting nomads, and their stories, cross "
                "between steppe and town, feeding the faeries on the strife; "
                "in summer the old Magic spirits take back the rivers and let "
                "them run to water the towns downstream.",
            ),
        ],
    )
    _place(
        cradle,
        "old_oxus_bed",
        "The Old Bed of the Oxus",
        inside=t,
        aura=2,
        summary=paragraphs(
            "The river's first course, which runs six days' march west "
            "across the desert to the Caspian near the fishing town of "
            "Khalkhal. Its spirits have all been bound into the works "
            "and canals round Gurganj, and nothing magical lives in it "
            "now, but a failing Magic aura of 2 lies along its dry "
            "length.",
            "Vis: Aquam, as small clear pools that form along the dry "
            "bed on cool nights while Aquarius is rising; the book gives "
            "no amount.",
        ),
    )
    _place(
        cradle,
        "jaxartes",
        "The Jaxartes",
        inside=t,
        realm="Faerie",
        summary=paragraphs(
            "The Sayhun, or river of Shash, gathered from many mountain "
            "streams in Farghana and running through it past the desert "
            "homelands of the Ghuzz Turks into the north-east of the Aral "
            "Sea by many channels. More than the Oxus it is the true "
            "line between Iran and Turan, Persian and Turk, farmer and "
            "nomad. Unlike the Oxus, one Faerie being rules it, and "
            "meddles in every tale of nomads breaking in.",
            "Near the old town of Talas lie the ruins of a nomad fort, "
            "and just outside them ends a road from Arcadia to a faerie "
            "image of the steppe.",
        ),
        secrets=[
            titled(
                "The Jaxartes's old spirit",
                "The Jaxartes's old river spirit feeds on the townsmen's "
                "dread of the steppe's barbarians: every few centuries it "
                "calls a faerie host under a new name down the Arcadian road "
                "by Talas, one more wave in an endless cycle of ruin, each "
                "slightly different, each breaking on civilisation's shore.",
            ),
            titled(
                "The Mongols and the river spirit",
                "The Mongols may be only the latest telling of the Jaxartes "
                "spirit's endless cycle of faerie hosts.",
            ),
        ],
    )
    aral = _place(
        cradle,
        "aral_sea",
        "The Aral Sea",
        inside=cradle.places["khwarazm"],
        summary=paragraphs(
            "The Lake of Khwarazm: shallow and reedy, with fine fishing "
            "in its south, though no one counts it navigable.",
        ),
    )
    _place(
        cradle,
        "jabal_jaghrahaz",
        "Jabal Jaghrahaz",
        inside=aral,
        aura=4,
        **RUMOURED_LOCALLY,
        summary=paragraphs(
            "A small island with a single low hill in the south-east of "
            "the Aral Sea, in a Magic aura of 4. The water round it never "
            "thaws. The local people are sure a mighty water jinni, the "
            "marid Jaghrahaz, lives there, but nobody dares cross the "
            "ice to look.",
        ),
    )
    _place(
        cradle,
        "kyzylkum",
        "The Kyzylkum",
        inside=t,
        summary=paragraphs(
            "The red sands between the two rivers, on the south-east "
            "edge of Khwarazm and the north-west of Sogdiana, haunted by "
            "jinn. For all its crescent dunes, its gentler eastern edge "
            "is full of game: gazelle, golden eagles, deer and koulan, "
            "the wild ass. Its north belongs to the waral, giant lizards "
            "of real wit, whose leaders walk upright and speak the local "
            "tongue, though their magic seems slight.",
        ),
    )


# -- Khwarazm --


def _khwarazm(cradle: Cradle) -> None:
    b, khwarazm = cradle.b, cradle.places["khwarazm"]
    gurganj = _town(
        cradle,
        "gurganj",
        "Gurganj",
        place=khwarazm,
        ruler="the Khwarazm-shah",
        summary=paragraphs(
            "Al-Jurjaniyah, a leading town of the trade roads and one of "
            "the shah's two capitals, which has moved up and down the "
            "Oxus's west bank over the years to dodge its floods and the "
            "anger of the native river spirits.",
            "If history holds, the Mongols besiege it in 1220 and after "
            "five months break the great dyke in frustration: the Oxus "
            "floods the town once more and runs again to the Caspian, "
            "and the river spirits, set free, turn on the Khwarazmians "
            "who held them. When the Mongols leave, only bodies and the "
            "outline of broken walls remain.",
        ),
    )
    minaret = _place(
        cradle,
        "gutluk_temir",
        "The Gutluk-Temir Minaret",
        inside=khwarazm,
        aura=7,
        summary=paragraphs(
            "The tallest brick minaret of the Mythic Middle East, over "
            "180 feet, looking out over the watered province. For all "
            "its holy form a Magic aura of 7 surrounds it, and it is the "
            "hub of the web of fetters and wards that holds the Oxus "
            "spirits to the dykes. The local community of sahirs keeps "
            "those wards up, meets in the tower, and sees that the canals "
            "go on feeding the province's famous fields. It stands right "
            "in the Mongols' way; its few survivors may be among the "
            "first sahirs to carry the news west.",
        ),
    )
    b.link(gurganj, "places", minaret, "Its sahirs' tower")
    _town(
        cradle,
        "kath",
        "Kath",
        place=khwarazm,
        summary=paragraphs(
            "Once the capital of Khwarazm and seat of its native "
            "shahs, a fine city on the Oxus's east bank, until flood "
            "after flood washed it down to second rank. The mausoleum of "
            "Il-Arslan looks out over a great necropolis to its north.",
        ),
    )
    _town(
        cradle,
        "otrar",
        "Otrar",
        place=cradle.places["transoxiana"],
        ruler="Inalchuq, the shah's governor",
        answers_to=cradle.world.get("khwarazm_shah"),
        summary=paragraphs(
            "A town on the east bank of the Jaxartes. In 1218 a rich "
            "Mongol caravan came here with a message for the shah; the "
            "governor Inalchuq, the shah's cousin, jailed and killed all "
            "450 men of it with their envoy, as spies, or for their "
            "goods, and the second embassy was shamed. On that insult "
            "from a petty officer the horde has come down on the land.",
            "If history holds, Otrar holds out five months in the first "
            "half of 1220 before it falls. Inalchuq is taken alive and "
            "killed with molten silver poured into his eyes and ears, "
            "and the town is levelled, its people killed or enslaved.",
        ),
    )
    _place(
        cradle,
        "otrar_ruins",
        "The Ruins of Otrar",
        inside=cradle.places["transoxiana"],
        realm="Infernal",
        aura=6,
        summary=paragraphs(
            "What the Mongols leave of Otrar, in a Perfidious Infernal "
            "aura of 6 tainted with the sin of Deceit (the aura comes "
            "with the town's fall, if history holds, in 1220). Lies told "
            "among the ruins ring truer: the Ease Factor to see through "
            "one rises by the aura.",
            "Uqana haunts them, the Muslim merchant the Khan sent as his "
            "first envoy with a personal message of friendship, killed "
            "by a fellow Muslim: an apparition (Realms of Power: Magic) "
            "who cannot rest because his message was never given, though "
            "the Khan has avenged him, and whom the Mongols' trail of "
            "ruin makes hard to talk into going on. Forced by magic, he "
            "might tell much of the Mongol leaders' plans; but forcing "
            "or deceiving him in this aura may cost dear.",
        ),
    )


# -- Sogdiana: Samarkand and Bukhara --


def _sogdiana(cradle: Cradle) -> None:
    b, sogdiana, w = cradle.b, cradle.places["sogdiana"], cradle.world
    samarkand = _town(
        cradle,
        "samarkand",
        "Samarkand",
        place=sogdiana,
        ruler="the Khwarazm-shah",
        answers_to=w.get("khwarazm_shah"),
        summary=paragraphs(
            "Marakanda to the Greeks, Sogdia's old capital on the upper "
            "Zeravshan, taken by one conqueror after another and still "
            "among the most crowded and cosmopolitan cities of the "
            "region; Alexander said it was finer than he had heard. It "
            "is the eastern capital of the shah's empire, and the first "
            "paper mill of Islam was built here after Talas.",
            "If history holds, Genghis Khan's armies besiege it in the "
            "spring of 1220, and for all its new walls it falls in five "
            "days; its surrendered garrison is put to death in batches, "
            "and its people are marched out for the sack and shared out "
            "as Bukhara's were.",
        ),
    )
    zindah = _place(
        cradle,
        "shahr_i_zindah",
        "The Shahr-i-Zindah",
        inside=sogdiana,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "The 'tomb of the living king', a street of tombs east of "
            "old Marakanda, named for its central shrine, the grave of "
            "Qusam ibn-Abbas. The other tombs are doors into a city of "
            "dark Faerie jinn and ghul, which gives the street a "
            "malevolent Faerie aura of 5 by day and an Infernal aura of "
            "the same strength by night. The shrine keeps a small Divine "
            "aura of 2, a lonely refuge in the dark.",
            "Rostam's mace lies forgotten in one of its tombs, carried to "
            "Turan by his enemies after his death: a superb two-handed "
            "mace (as a warhammer) giving +3 to Attack and Defence and "
            "the Inspirational Virtue to whoever holds it.",
        ),
    )
    b.link(samarkand, "places", zindah, "Its street of tombs")
    bukhara = _town(
        cradle,
        "bukhara",
        "Bukhara",
        place=sogdiana,
        summary=paragraphs(
            "An old trading town on the Zeravshan below Samarkand, in "
            "the middle of the Kyzylkum. In the ninth and tenth centuries "
            "it was the Samanids' capital and the heart of Islam's "
            "learning, home country of the poets Firdausi and Rudaki; "
            "Ibn Sina read in its famous library, and al-Biruni thought "
            "its book bazaars unequalled. It has a large Jewish "
            "community, one of the biggest of the Diaspora not to speak "
            "Hebrew. A sahir of its house of wisdom tends Job's Spring.",
            "As 1220 opens Genghis Khan and much of his horde are camped "
            "before it. If history holds, it falls within a fortnight: "
            "every defender left is killed, the townsfolk are driven "
            "out (craftsmen sent as slaves to Mongolia, young men forced "
            "into the army, the women worse used), and a fire burns the "
            "mostly wooden town, so that by winter's end it is smoking "
            "ruin. The whole place then lies under a Malevolent Infernal "
            "aura of 3 (Realms of Power: The Infernal), save round the "
            "Kalyan minaret, and the unburied dead wander it, open to "
            "any necromancer's call. Its book collections are lost, and "
            "poets will mourn them as a second Alexandria.",
        ),
    )
    _place(
        cradle,
        "kalyan_minaret",
        "The Kalyan Minaret",
        inside=sogdiana,
        realm="Divine",
        aura=7,
        levels=[
            Builder.level(
                "The round chamber above the rotunda",
                8,
                "Divine",
                enter="A devout Muslim who climbs the spiral stair just before dawn.",
                notes="A small terrestrial Divine regio, a round room "
                "that appears above the minaret's top.",
            )
        ],
        summary=paragraphs(
            "Bukhara's great minaret, in a Divine aura of 7, one of the "
            "few things left standing when the Mongols are done, spared "
            "by Genghis Khan himself: a gust took his hat as he looked "
            "up at it, and stooping for it he said it was the first "
            "thing he had ever bowed to. He spared the tower, but not "
            "the sheikhs: he killed two hundred holy men and had their "
            "heads thrown down the well near by before climbing the "
            "pulpit to make his famous speech. From its rotunda of "
            "sixteen arches the muezzin called the faithful and "
            "watchmen kept lookout; a frieze of diagonal brickwork "
            "lettered in Arabic rings its base.",
            "It belonged to the Po-i-Kalyan mosque, whose ruins about it "
            "keep a Divine aura of 5, an island in the Infernal aura "
            "that will lie over most of the ruined city. The mosque's well lies under "
            "an octagonal platform near by, and the grave of an imam "
            "whom the tower's builder, Arslan Khan, slew in a rite lies "
            "under the minaret's foot.",
        ),
    )
    _place(
        cradle,
        "ismail_tomb",
        "The Tomb of Isma'il Samanid",
        inside=sogdiana,
        aura=3,
        summary=paragraphs(
            "The half-buried tomb of Isma'il Samanid (r. 893 to 907), "
            "the Samanid dynasty's founder, just outside Bukhara, long "
            "forgotten by its dissolute townsfolk; if history holds, the "
            "dust of neglect hides it from the horde and it comes "
            "through untouched. Over its main door is carved a circle "
            "inside nested squares, a Zoroastrian sign. Because mobeds "
            "once used it, it has a Magic aura of 3 by night and a "
            "Divine aura of the same strength by day.",
        ),
    )
    _place(
        cradle,
        "jobs_spring",
        "Job's Spring",
        inside=sogdiana,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "The Chashma-Ayyub, a small mausoleum at the edge of "
            "Bukhara's farmers' market, newly built over a little spring "
            "in a Faerie aura of 3; unlike other tombs it holds no one. "
            "Folk say Job struck the ground with his staff here and "
            "water came, though the tale may cover an older pagan one. A "
            "sahir of the town's house of wisdom, which paid for the "
            "building, comes once a year.",
            "Vis: faerie-tainted Terram and Aquam, which the faerie "
            "jinni of the spring gives in a bargain for acting out the "
            "old story within its walls; the book gives no amount.",
        ),
    )
    _place(
        cradle,
        "kasri_orifon",
        "The Wishing Tree of Kasri Orifon",
        inside=sogdiana,
        realm="Faerie",
        levels=[
            Builder.level(
                "Beneath the arch",
                2,
                "Faerie",
                enter="Crawling under the arch of the trunk.",
                notes="A small Faerie regio, just big enough for a grown "
                "person, the home of a faerie jinni with power over "
                "fertility.",
            )
        ],
        summary=paragraphs(
            "In the main square of Kasri Orifon, a village just east of "
            "Bukhara, the dead trunk of an old mulberry twists into an "
            "arch. Childless women crawl under it hoping to conceive.",
        ),
    )
    b.link(bukhara, "places", cradle.places["kalyan_minaret"], "Its minaret")
    b.link(bukhara, "places", cradle.places["jobs_spring"], "Its house's charge")


# -- Bactria and Farghana --


def _bactria_and_farghana(cradle: Cradle) -> None:
    bactria, farghana = cradle.places["bactria"], cradle.places["farghana"]
    _town(
        cradle,
        "balkh",
        "Balkh",
        place=bactria,
        summary=paragraphs(
            "A great old city, for long the home of Zoroastrianism, "
            "since Zoroaster was born and is buried inside its walls; "
            "it sheltered the emperor Yezdgird from the Arabs, but has "
            "since taken wholly to Islam. Its Greek name, Bactra, gave "
            "Bactria its own. The fire temple of Naw Bahar is in one of "
            "its suburbs.",
            "If history holds, the Mongols sack it in 1221.",
        ),
    )
    khanoum = _place(
        cradle,
        "ai_khanoum",
        "The Ruins of Ai Khanoum",
        inside=bactria,
        aura=4,
        summary=paragraphs(
            "Ruins where the Jahyun meets the Nahr Dirgham, once a "
            "centre of Hellenism: Alexander founded the place as "
            "Alexandria on the Oxus, and the Seleucids made it the city "
            "of Eucratidia. What is left of a gymnasium, a theatre "
            "nearly as big as Epidauros's and several temples of the "
            "Greek gods, Zeus and Dionysus above all, gives it a Magic "
            "aura of 4.",
            "An altar of Alexander lies hidden in one of the temples on "
            "the city's edge. The altars (Ancient Magic) are linked to "
            "one another and to over seventy sites: a magus casting at "
            "Arcane Connection range with his hand on one may reach any "
            "shrine, city or temple tied to it as though through an "
            "Arcane Connection worth a +4 Penetration multiplier. It could bring "
            "Seekers into the region, or be a lifeline home for Hermetic "
            "settlers far into strange lands.",
        ),
    )
    _place(
        cradle,
        "ai_khanoum_gymnasium",
        "The Gymnasium of Ai Khanoum",
        inside=khanoum,
        aura=7,
        summary=paragraphs(
            "The best kept of Ai Khanoum's buildings, in a Magic aura of "
            "7 centred on a pillar inscribed to Hermes and Hercules "
            "together.",
        ),
    )
    _place(
        cradle,
        "sogdian_rock",
        "Sogdian Rock",
        inside=bactria,
        aura=3,
        **RUMOURED_LOCALLY,
        summary=paragraphs(
            "The site of Alexander's battle with the rebel satrap of "
            "Sogdia, Oxyartes of Balkh, father of the fabled beauty "
            "Roxane. Only little-known mountain paths reach it, and only "
            "a handful of local tribesmen know just where it is. The "
            "ghosts of the thirty men who fell in the climb still haunt "
            "it and have no love for the heirs of their Persian foes.",
            "A candidate covenant site: a superb natural fortress, full "
            "of caves and cut cisterns that could store food and water "
            "for a siege, in a Magic aura of 3, perhaps higher deep in "
            "the caves. Remote as it is, it could be a base for Hermetic "
            "magi exploring the Mythic Middle East.",
        ),
    )
    _town(
        cradle,
        "khojend",
        "Khojend",
        place=farghana,
        summary=paragraphs(
            "A small trading town at the mouth of the Farghana valley, "
            "built by the ruins of Alexandria Eschate, the furthest town "
            "Alexander founded. If history holds, the Mongols lay waste "
            "the Jaxartes towns as far as Khojend in 1220.",
        ),
        secrets=[
            titled(
                "Khojend's altar",
                "Another altar of Alexander is hidden under Khojend or in "
                "the ruins beside it.",
            ),
        ],
    )
    _town(
        cradle,
        "osh",
        "Osh",
        place=farghana,
        summary=paragraphs(
            "The easternmost town of Farghana, just below the Jaxartes's "
            "source in the Pamir, and the northernmost of the caliphate: "
            "where certainty ends and stories of what lies past the map "
            "begin. It is the last caravan halt on the Great Khurasan "
            "Road from Baghdad; beyond it merchants follow legends, not "
            "tracks, up into the mountains towards the faerie city of "
            "Khashgar and the dreaded desert road to Serica.",
        ),
    )


# -- the east: Badakhshan, the Wakhan and beyond --


def _the_east(cradle: Cradle) -> None:
    places, region = cradle.places, cradle.places["silk_road"]
    _place(
        cradle,
        "lahzvard",
        "The Mines of Lahzvard",
        inside=places["badakhshan"],
        summary=paragraphs(
            "Limestone beds along the Badakhshan river at Lahzvard, the "
            "only source of lapis lazuli Mythic Europe knows (its name "
            "comes from the town's). The greedy jinn of Zubaydah, a fort "
            "named after Harun al-Rashid's favourite wife, oversee the "
            "chief workings, and heavily guarded loads go west to "
            "Europe's painters and magi, or east to Hind, Serica and "
            "perhaps the mountain lands of Faerie beside them.",
            "Lapis is often taken for sapphire. Its pure pigment, "
            "ultramarine, is prized for illuminating Hermetic texts as a "
            "strongly resonant material, though kuanos (azurite) often "
            "stands in for it. Its bonuses: +3 as an aphrodisiac, "
            "ground; +5 to keep limbs healthy; +5 to cure boils and "
            "ulcers; +6 against a demon's Obsession. Carved as an eye, "
            "set in gold and laid on an altar of Ra on a month's last "
            "day, it is Enriched to give Lesser Immunity to demons' "
            "Obsession; melted with lead to strip its gold flecks and "
            "ground onto the eyelids, it works as Venus' Blessing.",
            "Vis: a Lapis Lazuli of Virtue holds 2 pawns of Corpus.",
        ),
    )
    _place(
        cradle,
        "wakhan_road",
        "The Faerie Road to Serica",
        inside=places["wakhan"],
        realm="Faerie",
        aura=6,
        summary=paragraphs(
            "Past the Badakhshan river's mouth, the whole upper valley "
            "of the Oxus lies under one very long, narrow Faerie aura, "
            "fenced by the ridges north and south. It is only 2 on the "
            "edge of Ai Khanoum and grows as one climbs east, reaching 6 "
            "in the Wakhan proper, where its Warping helps make the "
            "nomads so silent (the Reclusive Flaw). Many Faerie regiones "
            "open off the path, according to the traveller's mood, aims "
            "and Faerie Sympathies: some lead only to dead-end canyons "
            "and death, some hold lost kingdoms and cities on the shore "
            "of a creeping desert, and the most sought lead into the "
            "worlds of Faerie, Arcadia most often, though one who goes "
            "alone is likelier drawn into Eudokia to settle the crisis "
            "that drove him past the Order's knowledge.",
        ),
    )
    roof = _place(
        cradle,
        "roof_of_world",
        "The Roof of the World",
        inside=region,
        aura=4,
        summary=paragraphs(
            "The Bam-i-Dunya: the high plateaus of the Pamir knot, the "
            "north-west of the Caucasus Indicus and the ranges running "
            "south and east out of the House of Islam. The peoples of its "
            "valleys have always stood between Rome and Persia in the "
            "west and Serica in the east. Islamic legend makes the chain "
            "part of the Mountains of Qaf, a homeland of the jinn; the "
            "classical writers, the lower flanks of Mount Imeon, the "
            "mountain at the centre of the world, where some Criamon "
            "magi think the Axis Magica stood before Criamon passed into "
            "Twilight.",
            "An unspoilt Magic aura of 4 at least covers it all, broken "
            "by higher auras and by regiones of other realms among the "
            "ice. Its valleys, strewn with diamonds the size of a fist, "
            "are the roosts of the great ruq, eagles that can lift a man "
            "in one claw like a mouse.",
        ),
    )
    _place(
        cradle,
        "janaindar",
        "Janaindar, the City Above the Clouds",
        inside=roof,
        **RUMOURED_LOCALLY,
        summary=paragraphs(
            "In the nomads' legends, a lost city on the edge of the "
            "Magic Realm, seen above the clouds on a great peak on a "
            "clear day and all but impossible to reach save by magic or "
            "in a ruq's claws. Its strange folk look human but say they "
            "come of an ancient magical race that once ruled the earth.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The book leaves Janaindar's truth open, offering a lost "
                "Nephilim settlement, the real Hyperborea in Turkistan, an "
                "old and secluded covenant of elder magi, the heirs of a "
                "rival tradition founded by Viea, Trianoma's sister, a final "
                "hiding place of the Zoroastrian mobeds, a high covenant "
                "site, or the Diedne's last sanctum.",
            ),
        ],
    )
    _place(
        cradle,
        "turris_lapidae",
        "Turris Lapidae, the Stone Tower",
        inside=region,
        **RUMOURED,
        summary=paragraphs(
            "In Ptolemy's Geography, the halt in the little mountain "
            "kingdom of Sarikol where caravans for Sera Metropolis, the "
            "Seres' capital, stopped. Some say the fort above it marks "
            "the halfway point between Europe and the east; others that "
            "the town stands half in the world and half in Faerie, a "
            "gate to Arcadia. The tales come from the merchant Maes "
            "Titanos, whom Ptolemy's own source, the pre-Hermetic "
            "wizard Marinus of Tyre, thought an invention, a faerie or "
            "an infernalist.",
            "In the Mythic world it is a sizeable town at the end of "
            "classical travel eastward, and one of the bounds of the "
            "Order's knowledge. No Redcap or Mercere magus claims to have "
            "been there or inside the tower, and some Merinita think it "
            "can only be reached along the Arcadian paths their House "
            "knows.",
        ),
    )
    _town(
        cradle,
        "khashgar_town",
        "Khashgar",
        place=region,
        ruler="the Mongols",
        summary=paragraphs(
            "The best known of the legendary cities of the road east in "
            "this century: an oasis where the routes from north and "
            "south meet before splitting round the Taklimakan towards "
            "the Land of Silk. Scholars argue over its origin and where "
            "exactly it is, but all agree that men, jinn and other "
            "Eastern faeries jostle in its streets with angels, demons "
            "and sorcerers of every tradition but the Hermetic. Nominally "
            "Muslim since the late ninth century, it suffered "
            "persecution under the faerie Qara Khitai and has lately "
            "fallen to the Mongols without a fight, which its people, "
            "mortal and magical, seem hardly to mind.",
            "Its Yekshenbar, the Sunday market, sells anything: desert "
            "robbers rub shoulders with weary merchants, and fine silks, "
            "knives and jewels lie beside magical wares, with slaves, "
            "mundane and magical, for a price. Some Merinita say they "
            "have reached its market through Arcadia, and suspect that "
            "the city exists in more than one version at a time, or that the whole "
            "town lies in a regio reached from many places in Mythic "
            "Europe.",
        ),
    )
    _place(
        cradle,
        "yenghissar",
        "Yenghissar",
        inside=region,
        summary=paragraphs(
            "A small village on the road to Khashgar, which a wild "
            "desert storm spirit, a buran, laid waste every seven years, "
            "ruining its crops and herds, until a sahir bound it.",
        ),
        secrets=[
            titled(
                "Who bound the buran",
                "The sahir who bound the buran of Yenghissar is Infernally "
                "aligned and used Goetic binding.",
            ),
            titled(
                "The buran in the sword",
                "The buran of Yenghissar rages in its binder's ancestral "
                "sword, ever trying to wreak elemental havoc round its "
                "careless captor.",
            ),
            titled(
                "Storyguide Notes",
                "The Goetic Art of Binding: Realms of Power: The Infernal.",
            ),
        ],
    )
    _place(
        cradle,
        "taklimakan",
        "The Taklimakan",
        inside=region,
        aura=7,
        summary=paragraphs(
            "A desert of death beyond the mountains, whose name means "
            "that those who go in never come out: oasis towns and the "
            "ruins of lost peoples, searing heat, cruel winds and "
            "malicious demons, all luring travellers from their caravans "
            "to die slowly of hunger and thirst. Two auras of a steady "
            "7, one Magic and one Infernal, wander across the sands, "
            "winding about each other like opposing storms, and as "
            "they spiral they swallow and uncover ancient Faerie "
            "regiones, deserted ruined cities or living oases peopled "
            "by jinn from before Islam. The record keeps the Magic aura; "
            "the Infernal one is as strong.",
            "The dunes off the main track are dreaded as the home of the "
            "qara buran, the black hurricanes, bloodthirsty wind spirits "
            "that fall on caravans as sandstorms and part travellers "
            "from camels and friends. They are much like elemental jinn, "
            "though some seem closer to the Infernal Aerial Powers; they "
            "split their loyalty between the Gok Buran, a fearsome "
            "Daimon in a still stronger Magic regio deep in the sands, "
            "and its rival, a Duke of Hell called Great Lop.",
        ),
    )


# -- the steppe --


def _the_steppe(cradle: Cradle) -> None:
    region, t = cradle.places["silk_road"], cradle.places["transoxiana"]
    _place(
        cradle,
        "great_steppe",
        "The Great Steppe",
        inside=region,
        summary=paragraphs(
            "The sea of grass across the breadth of Asia, from the Sea "
            "of Azov and the plain of Hungary in the west as far as the "
            "Ordos and the endless eastern horizon, which even the Roman "
            "empire at its height only touched. Herodotus called its "
            "shore Scythia; no other land Hermetic magi know is on its "
            "scale, and out of it pour the Mongols.",
            "Its nomads share a belief in Khan Tengri, the Great Sky, "
            "common forefather and overlord: a vast spirit drawing on "
            "the Magic realm, an Elder Daimon in Hermetic terms, a "
            "Kosmokrator of the steppe and sky, as the spirit of the "
            "Hercynian Forest is in the west. Unlike that spirit, no "
            "Mercurian rite has weakened it and no town or Dominion has "
            "touched it save at its fringes: a reservoir of power for a "
            "magus who would finish the last work of Hercynius, folding "
            "Merinita's nature magic into Hermetic theory.",
            "Where towns press on the steppe's edges, Tengri has given "
            "up some of its power to lesser spirits, genii loci of "
            "grasslands from a valley to a kingdom in size (Magic Might "
            "30 to 45). Such a spirit may hold its own, keeping a "
            "magical steppe (the plains by the Sea of Azov, the "
            "Dzungarian basin, eastern Mongolia); may waste away and "
            "leave a mundane one (Pannonia, and the Hungarian plain, "
            "now a promontory of Divine pasture); or may be replaced, "
            "most often by a faerie fed on the nomads' descendants' "
            "tales: the towns along the Jaxartes border such a Faerie "
            "steppe.",
            "A few of the Mongol army are shamans of Great Tengri, who "
            "summon spirits to scout, spy and fight for them, bargain "
            "with them or bind them into weapons, using any spirit that "
            "serves, demons included; each has a familiar spirit of his "
            "homeland, like a qareen.",
        ),
    )
    _town(
        cradle,
        "tashkent",
        "Tashkent",
        place=t,
        ruler="the Mongols",
        summary=paragraphs(
            "The Turks' City of Stone, once the greatest Arab town past "
            "the Jaxartes: a city of canals famous for its vines, and the "
            "market between the Sogdians' heirs and their Turkish "
            "neighbours. The shah sacked much of it in 1214 and the "
            "Mongols laid it waste in 1219; under Mongol rule it is "
            "already being settled again and taking back its trade, and "
            "marks the line between civilisation and the wild.",
        ),
    )
    _town(
        cradle,
        "talas",
        "Talas",
        place=t,
        summary=paragraphs(
            "Where in July 751 Ziya ben Salih's Muslim army met a strange "
            "force from beyond the eastern steppe, the Arabs' furthest "
            "reach east; craftsmen taken there brought papermaking into "
            "Islam. Nearly five centuries on, here the shah beat the "
            "faerie Qara Khitai in 1218 to make Transoxiana his. The "
            "Mongols razed the town to the ground in 1219 on their way "
            "to Otrar.",
        ),
    )


# -- the lords --


def _lords(cradle: Cradle) -> None:
    b, w = cradle.b, cradle.world
    w["genghis_khan"] = b.lord(
        "Great Khan of the Mongols",
        title="",
        wealth="Wealthy",
        seat="His camp before Bukhara",
        ruler="Genghis Khan (Temujin)",
        place=cradle.places["great_steppe"],
        summary=paragraphs(
            "Temujin, Genghis Khan, Great Khan since 1206, master of "
            "the nomad empire coming down out of the east. Khashgar has "
            "fallen to him, and Tashkent and Talas were razed in 1219; "
            "as 1220 opens he is camped before Bukhara, come to punish "
            "the Khwarazm-shah for the caravan killed at Otrar and the "
            "envoys killed and shamed. He calls himself God's "
            "punishment on a sinful people.",
            "His generals are mostly gifted soldiers rather than his kin, "
            "masters of strategy whose great strength is knowing the "
            "ground and the enemy; their best trick is a feigned retreat "
            "that draws a foe into a long, wearing chase before turning "
            "on him. His troopers are fierce horse archers in "
            "fur-lined leather; shamans of Great Tengri ride with them. "
            "By the simplest reading he is a brilliant mundane general "
            "and history runs its course.",
            "If history holds: by the end of 1220 he has taken Bukhara, "
            "Otrar, Samarkand and Gurganj and harried the shah to his "
            "death; in 1221 his armies sack Balkh, Merv, Nishapur and "
            "Herat and drive Jalal al-Din over the Indus, while Jebe and "
            "Subadei begin their great raid into Russia. He dies in "
            "1227, holding the east as far as eastern Persia; his heirs "
            "take western Persia, Georgia, Armenia and northern Iraq in "
            "the 1230s, the Seljuks of Asia Minor in 1243, and Baghdad "
            "in 1258, where they roll the caliph in a carpet and trample "
            "him, and are checked only by Egypt's Mamluks in Syria in "
            "1260.",
        ),
        secrets=[
            titled(
                "What the sahirs fear",
                "Some Persian sahirs already fear that the Great Khan is the Zahhak.",
            ),
            titled(
                "Storyguide Notes",
                "What the Khan truly is the book leaves to each troupe, "
                "offering, with none chosen: an Infernal horde, its leaders "
                "Angels of Punishment, demons of the Avengers of Evil posing "
                "as God's vengeance, or the Khan a new Zahhak possessed by "
                "Azi Dahak; the Spawn of Gog and Magog, a horde ridden out "
                "of Arcadia in the endless nomad cycle, the Khan a dark "
                "faerie monarch and his officers court faeries; the legions "
                "of Prester John, faeries playing a pious part, born of "
                "garbled tales of the Qara Khitai's defeat of Sultan Sanjar; "
                "the Vengeance of God, a true Divine host of punishment; "
                "Blood of Heroes, the Khan and his generals scions of Ares "
                "or of Attila; or a Spirit Votary of Great Tengri, who made "
                "his bargain on the holy mountain of Burkhan Khaldun and "
                "wields elemental powers great enough to force the Order of "
                "Hermes to unite against him.",
            ),
        ],
    )
    w["qara_khitai"] = b.faction(
        "The Qara Khitai",
        faction="Faerie court",
        realm="Faerie",
        decides="Its leader",
        place=w["khashgar_town"],
        summary=paragraphs(
            "The Kara-Khitai, a mysterious nomad dynasty from the far "
            "east whom the book casts as Eastern faeries. Their "
            "confederation, which counted Nestorian Christians among its "
            "tribes, beat Sultan Sanjar on the Qatwan steppe near "
            "Samarkand in 1141, and garbled tales of that battle may lie "
            "behind the legend of Prester John. They lorded it over "
            "Khashgar, oppressing its Muslims, until the Khwarazm-shah "
            "Muhammad II broke their faerie host in 1218 and took "
            "Transoxiana; Khashgar has since gone to the Mongols.",
        ),
    )
    b.link(w["genghis_khan"], "places", w["khashgar_town"], "Taken without a fight")
    b.link(w["qara_khitai"], "places", w["khashgar_town"], "Once theirs")
    conquest = w.get("mongol_conquest")
    if conquest is not None:
        b.link(w["genghis_khan"], "places", conquest, "His war")
    shah = w.get("khwarazm_shah")
    if shah is not None:
        b.link(shah, "places", w["samarkand"], "His eastern capital")
        b.link(shah, "places", w["gurganj"], "His capital")
        b.link(w["qara_khitai"], "places", shah, "Beat them in 1218")
