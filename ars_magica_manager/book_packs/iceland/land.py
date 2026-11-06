"""Land and History (Land of Fire & Ice pp. 6-19, with the map on p. 10 and
the list of districts on p. 34), in paraphrase.

The island, its four Quarters and thirteen thing districts, the volcanoes,
glaciers, farms and battlefields the chapter names, and the lands west of it
are places. The eight riki of 1220 are lords, named for their lands so that
a person's own record can stand apart; the five families, the Guardians, the
Irish priests, the Skraelings, the Freestate, the storgodar, the storbaendur and
the draug are factions. A place printed only on the map has a short record.

The pack has no Tribunal, and its one covenant is built by a later part, so
the history has no Diary to go in: the Freestate's record holds it, and
TIMELINE keeps it as data, a line for each date. The years after 1220 are the
dormant story of the storgodar's feud, and the Lava Fields' encounters are
dormant stories too.

The chapter's bishoprics, cathedrals and monasteries are the law_church
part's; the Galdramen Hreppur and the kinds of magician are the magic part's;
Pan Caudarax's stats, Kerlingarfjoll and the Scartaris Sanctum are the later
parts'."""

from __future__ import annotations

from ...models import Neighbour
from ..builder import Builder, dormant, joined_lines, paragraphs

S = Builder.stage
DATED = "Fixed dates"
TRACK = "A track"

#: (year, the date as printed, what happened): pp. 16-18. A year before Christ
#: is negative; a span sits at its first year.
TIMELINE: tuple[tuple[int, str, str], ...] = (
    (-4000, "c. 4000 BC", "The civilization of the Old Ones is destroyed."),
    (-2000, "c. 2000 BC", "The Egyptian cult of Thoth is at its height."),
    (-500, "c. 500 BC", "The Greek cult of Hermes is at its height."),
    (412, "412", "The cult of Mercury is officially disbanded."),
    (767, "767", "The Order of Hermes is founded at Durenmar."),
    (
        790,
        "790",
        "Irish priests, whom the Norse will call papar, reach Iceland and make "
        "it their summer retreat.",
    ),
    (800, "800-1100", "The Viking period."),
    (
        825,
        "825",
        "The Irish monk Dicuil mentions Thule in his book on the measure of the world.",
    ),
    (
        850,
        "850",
        "Naddoddur the Swede, blown off his course to the Faeroes, comes on "
        "the island and calls it Snaeland, snowland.",
    ),
    (
        855,
        "855",
        "Gardar Svavarsson sails round the island and winters at Husavik on "
        "the north coast.",
    ),
    (
        860,
        "860",
        "Floki Vilgerdarson brings his family to Snaeland, soon tires of it "
        "and renames it Island, ice land.",
    ),
    (
        870,
        "870-930",
        "The landnam, the land-taking: 10-20 thousand Norsemen claim the "
        "farmland, and the Irish priests choose not to come back.",
    ),
    (
        874,
        "874",
        "Ingolfur Arnarson makes his home at a place he names Reykjavik, smoky bay.",
    ),
    (890, "890-930", "Harald Fairhair reigns in Norway."),
    (910, "910-990", "The life of Egil Skallagrimson: warrior, poet, magician."),
    (
        925,
        "925",
        "Pan Caudarax orders the landvaettir to clear the island of people, "
        "and volcanoes stir all over it. Trollsynir, galdramen and vitkir "
        "attack him and in the end win a truce.",
    ),
    (
        930,
        "930",
        "The Althing, the general assembly, is set up with the first "
        "constitution, opening what will be called the Freestate.",
    ),
    (
        930,
        "930",
        "The island is declared albyggt, fully inhabited: 40-50 thousand "
        "people, 400 named settlers with their kin, women and slaves.",
    ),
    (
        950,
        "950",
        "The magicians form a hreppur to guard their interests, and meet in "
        "the Eldborg caldera, which the dragon's wrath made 25 years before, "
        "in memory of their first alliance.",
    ),
    (
        965,
        "965",
        "The constitution is refined: four quarters (fjordungar), each with a "
        "court at the Althing.",
    ),
    (970, "970", "An outlaw who kills three other outlaws earns a free pardon."),
    (
        979,
        "979",
        "Harald Bluetooth Gormsson of Denmark sends a trollson to look at "
        "Iceland. The Guardians meet him, and Harald gives up his plan of "
        "invasion.",
    ),
    (
        982,
        "982",
        "Outlawed from Iceland, Eirik the Red sails west and comes on Greenland.",
    ),
    (
        984,
        "984",
        "The native Thorvald and the German bishop Fridrekr build the first "
        "church in Iceland. Their mission does well, but the Althing they "
        "attend mocks them.",
    ),
    (986, "986", "Greenland is colonized."),
    (987, "987", "Bjarni Herjolfsson catches sight of Vinland."),
    (
        997,
        "997",
        "A law rules that conversion may in some cases count as a defilement "
        "of the family.",
    ),
    (
        1000,
        "1000",
        "The Althing makes Iceland Christian, thanks chiefly to three zealous "
        "Christian godar. They argue that two faiths under one law would "
        "split the land into two states, and pressure over trade from Denmark "
        "and Norway helps. Exposing newborns, eating horseflesh and private "
        "sacrifice to the old gods stay lawful.",
    ),
    (1001, "1001", "Leif Eiriksson goes west in search of Vinland."),
    (
        1002,
        "1002-20",
        "Vinland's colonies are tried, and given up by 1020 at the latest "
        "under native attacks. Gathering furs and timber there may go on into "
        "the mid fourteenth century.",
    ),
    (1005, "1005", "A fifth court is set up."),
    (
        1007,
        "1007",
        "Holmganga, single combat, ends as a legal way of deciding a case. "
        "The last duel recorded on the islet in the Oxara was fought by the "
        "warrior-poet Gunnlaugur Serpent-Tongue against the husband of the "
        "woman he loved.",
    ),
    (
        1014,
        "1014-1030",
        "Olaf Haraldson, St Olaf, reigns in Norway. A treaty of 1020 with "
        "Iceland settles the rights of each country's people in the other, "
        "and with it the last pagan practices become illegal.",
    ),
    (
        1030,
        "1030-1118",
        "The Fridharold, the age of peace.",
    ),
    (
        1031,
        "1031-1041",
        "Magic helps to kill Grettir the Strong, and laws against all magic "
        "follow. For ten years the magicians give no help at all, until the "
        "godar agree to protect in secret those accused of harmless magic.",
    ),
    (
        1056,
        "1056",
        "The first bishopric is founded at Skalholt in the Southern Quarter, "
        "and its bishop gains a seat in the logretta.",
    ),
    (1056, "1056-80", "Isleif Gizursson is Iceland's first native bishop."),
    (
        1056,
        "1056-1133",
        "The life of Saemundur Sigfusson the Wise, godi of Oddi, galdraman and "
        "bishop, whose sister Halla was a seithkona.",
    ),
    (1096, "1096", "The law of tithes comes in."),
    (
        1106,
        "1106",
        "A second bishopric is founded at Holar in the Northern Quarter, its "
        "bishop too sitting in the logretta. Its first, Jon the Saint "
        "Ogmundarson (1106-1121), a mighty foe of heathen ways, is later made "
        "a saint. Bergthor Hrafnsson, Haflidi Masson and others write down "
        "the laws, a work that comes to be called Gragas, Grey Goose.",
    ),
    (
        1122,
        "1122-1133",
        "Ari the Learned writes the Islendingabok, a history from the founding "
        "to the death of Bishop Gizur in 1118.",
    ),
    (1123, "1123", "Iceland's Christian law is set down as a code."),
    (
        1218,
        "1218-1220",
        "Earl Skuli, for King Hakon of Norway, makes an expedition to Iceland "
        "to secure trade. Snorri Sturluson heads off violence by agreeing to "
        "help bring Iceland under Norway.",
    ),
)

#: (name, Quarter, what else the chapter says of it): the thirteen districts of
#: p. 34, spelt as the map on p. 10 does but where p. 15 differs.
DISTRICTS: tuple[tuple[str, str, str], ...] = (
    ("Thverarthing", "West", "Snorri Sturluson is gathering its chieftaincies."),
    ("Thornessthing", "West", ""),
    ("Thorskafjardarthing", "West", ""),
    (
        "Rangarthing",
        "South",
        "All its chieftaincies belong to the Oddaverjar family.",
    ),
    (
        "Arnesthing",
        "South",
        "All three of its chieftaincies belong to the Haukdaelir family.",
    ),
    ("Kjalarnessthing", "South", ""),
    ("Sunnudalsthing", "East", ""),
    ("Mulathing", "East", "Thorarin Jonsson's riki."),
    ("Skaftafellsthing", "East", "Orm Jonsson's riki."),
    (
        "Hunavatnsthing",
        "North",
        "Kolbeinn Tumason of the Asbirningar added it to his lands.",
    ),
    (
        "Hegranesthing",
        "North",
        "The Skagafjord district, the Asbirningar's first.",
    ),
    ("Vadlathing", "North", "Sighvat Sturluson holds it."),
    ("Thingeyjarthing", "North", "Sighvat Sturluson holds it."),
)


def build(b: Builder) -> None:
    iceland = _island(b)
    quarters = _quarters(b, iceland)
    districts = _districts(b, quarters)
    _sites(b, iceland, quarters, districts)
    _west_over_sea(b)
    _guardians(b)
    _freestate(b)
    _families(b)
    _riki(b, quarters, districts)
    _norway(b)
    _peoples(b)
    _stories(b, iceland)


# -- the island --


def _island(b: Builder) -> Neighbour:
    return b.place(
        "Iceland",
        realm="",
        summary=paragraphs(
            "A rugged island larger than Ireland, and mostly unfit to live on: "
            "over half of it stands above 400 metres, high indeed so far "
            "north. Quick rivers run through lowland meadows over great "
            "waterfalls, and shift their courses from one generation to the "
            "next. Gorges slash the open plains and defeat the traveller. Pits "
            "of boiling mud, hot pools and geysers are everywhere, in over 250 "
            "hot districts with 780 springs, and old lava and ash are never "
            "far off. The highlands, with their burning ranges and vast "
            "glaciers, are left to trolls, giants, the mad and the desperate.",
            "It rains, sleets, snows or drizzles most days, though winters are "
            "mild and a shower often gives way to a sunny afternoon. Gales and "
            "fog can make life miserable. The north is the sunniest coast and "
            "the east the warmest. The interior has clearer skies, but "
            "blizzards in every season and icy sandstorms that rise from "
            "nothing.",
            joined_lines(
                "The land, about 800 and about 1220, as a share of the whole:",
                "Cultivated: none, 1%",
                "Grassland: 40%, 30%",
                "Lakes and rivers: 6%, 6%",
                "Bush and forest: 25%, 1%",
                "Lava fields: 11%, 11%",
                "Glaciers: 11%, 11%",
                "Sand: 4%, 4%",
                "Other wasteland: 3%, 36%",
            ),
            "The first settlers found dwarf willow woods, and bog and marsh "
            "along parts of the coast. Clearing for firewood and pasture let "
            "the soil wash away, and the highland erosion goes on; another 8% "
            "of the grass will be lost in years to come. Ireland, by "
            "comparison, is 13% tilled, 68% grass and 5% woods.",
            "Only the arctic fox and the polar bear are native. The bears were "
            "killed or caught and sold abroad, and one that drifts over from "
            "Greenland on the ice is soon hunted down; the foxes, as disliked, "
            "hid better. Common and grey seals feed on the coastal shelves and "
            "are hunted by orca, other whales are often seen, and walrus bask "
            "on the floes between dives for clams.",
            "Gulls, cormorants and great auks fill the coasts, with ducks, "
            "whooping swans, owls, divers, gyrfalcons and the snow-white "
            "arctic eagle, the grandest of all. Eels, salmon, trout and Arctic "
            "char swim the rivers, and the sea is thick with food.",
            "The settlers brought chickens, cattle, cats, dogs, sheep, goats, "
            "pigs and horses, and without meaning to, mice and rats. Goats and "
            "pigs did such harm to the thin grass that by 1000 few were kept.",
            "Before people came, the whole island lay under a magical aura, "
            "known only to dragons, giants and magical beasts, and spirits of "
            "the land warred like the fire and ice they mirrored. The prayers "
            "of Irish priests drove that power back into the geyser fields, "
            "mountains, volcanoes and glaciers.",
            "Icelanders have no family names: each is known as the son or "
            "daughter of the father, rarely the mother, as Una Eiriksdottir or "
            "Thord Eiriksson, and a nickname may set one man apart from "
            "another, as Viga-Thord, Battle-Thord, or Thord inn audgi, Thord "
            "the Rich.",
        ),
        secrets=paragraphs(
            "Auras (p. 9): the lowlands are mundane. Dominion is low and "
            "patchy: a farm beside a church may have Divine 1, seldom reaching "
            "its neighbours, and only around the cathedrals does it cover much "
            "ground. Most faerie auras of the pagan temples went with the "
            "conversion. Lowland volcanic regions often keep Magic 1 or 2; "
            "little-travelled highlands a patchy Magic 1; mountains and "
            "glaciers normally Magic 2, peaking higher at particular sites. "
            "Before the Irish priests, the aura in many places reached right "
            "into the magic realm (p. 6).",
            "Wards (p. 9): the magicians keep wards on the interior paths that "
            "stop trolls and landvaettir of Magic Might 20 or less, and on "
            "some stretches up to 30.",
            "The Order (p. 9): Icelandic magicians do not know of Hermetic "
            "magi, and the Order knows little of the island. Magi suspect all "
            "Nordic lands, where many blame a powerful Order of Odin for the "
            "loss of every covenant tried there, so most shun even the "
            "Scandinavian mainland and few have heard of Iceland. In 1220 it "
            "has no known Hermetic presence.",
        ),
    )


def _quarters(b: Builder, iceland: Neighbour) -> dict[str, Neighbour]:
    words = {
        "West": "Home of the Sturlungar. Thord Sturluson holds Snaefellsnes and "
        "Dalir, and Snorri Sturluson Borgarfjord. The Vestfirdir peninsula "
        "still keeps the old ways of godar and baendur. Its assembly sites are "
        "Thverar, Thorsnes and Thorskafjardar.",
        "South": "Skalholt, the first bishopric, stands here. The Oddaverjar "
        "rule Rangarthing and the Haukdaelir Arnesthing. Its assembly sites are "
        "Rangar, Arnes and Kjarlarnes.",
        "East": "All of it belongs to the Svinfellingar, split between the "
        "brothers Orm and Thorarin Jonsson. Its assembly sites are Sunnudals, "
        "Mula and Skaftafells.",
        "North": "Holar, the second bishopric, stands here. The Asbirningar "
        "hold the west of the Quarter and Sighvat Sturluson the east. It alone "
        "has four districts, and its assembly sites are Hunavatns, Hegranes, "
        "Vadla and Thingeyjar.",
    }
    names = {
        "West": "Western Quarter",
        "South": "Southern Quarter",
        "East": "Eastern Quarter",
        "North": "Northern Quarter",
    }
    return {
        key: b.place(names[key], inside=iceland, realm="", summary=words[key])
        for key in names
    }


def _districts(b: Builder, quarters: dict[str, Neighbour]) -> dict[str, Neighbour]:
    found: dict[str, Neighbour] = {}
    for name, quarter, words in DISTRICTS:
        found[name] = b.place(
            name,
            inside=quarters[quarter],
            realm="",
            summary=paragraphs(
                f"A thing district of the {quarter}ern Quarter, holding its own "
                "spring assembly.",
                words,
            ).strip(),
        )
    return found


def _short(
    b: Builder, name: str, inside: Neighbour, summary: str, realm: str = ""
) -> Neighbour:
    return b.place(name, inside=inside, realm=realm, summary=summary)


def _sites(
    b: Builder,
    iceland: Neighbour,
    quarters: dict[str, Neighbour],
    districts: dict[str, Neighbour],
) -> None:
    west, north, east = quarters["West"], quarters["North"], quarters["East"]
    b.place(
        "Hekla",
        inside=iceland,
        summary=paragraphs(
            "A burning mountain of the south-west, and the lair of the dragon "
            "Pan Caudarax, first of the Guardians. In 924 he woke to find the "
            "lowlands full of men and set the volcanic spirits to shake the "
            "land. Galdramen and trollsynir tracked him here and many died "
            "before the trollsdottir Aud found his weak spot and wounded him. "
            "Each side drew back, and a truce was struck: he called off the "
            "spirits, and the Norse pay him forty horses a year.",
            "He has cared little for humans since, and they seldom come near. "
            "Eruptions still happen, but they are not his doing.",
        ),
        secrets=paragraphs(
            "Pan Caudarax came back to his lair in 108 after almost a thousand "
            "years in Flanders and made a nest for his mate's brood. The eggs "
            "were laid in 232, and he then took the mantle of Guardian from "
            "his mate. They will hatch on the day of the solar eclipse, 22 May "
            "1248 (p. 11).",
            "The book prints 924 here (p. 11) and 925 in its timeline (p. 17), "
            "where vitkir join the attackers.",
        ),
    )
    b.place(
        "Eldborg",
        inside=west,
        summary="A great crater in the west, alone in a flat lava field not far "
        "short of the Snaefellsnes peninsula, 200 paces across and 50 deep, torn "
        "open by Pan Caudarax's wrath about 925. The way to its wide floor goes "
        "up the outer slope and down the inner. Iceland's magicians have met "
        "here since 950, in memory of the alliance that stood against him.",
        secrets="A magical site; the book prints no aura for it (pp. 17, 27, 102).",
    )
    b.place(
        "Odadahraun, the Lava Fields of Misdeeds",
        inside=iceland,
        summary=paragraphs(
            "The wild lava north of the Vatnajokull glacier, where the East, "
            "North and South Quarters meet and which none of them truly owns. "
            "Twisted spires of rock and crumbling pumice stand among sulphur "
            "springs that belch foul air, under glaciers and volcanoes.",
            "No church has ever touched it. Only the most desperate outlaws "
            "brave its freezing winds and scalding steam, and they are "
            "dangerous men. Unfriendly spirits of every sort haunt it, some of "
            "Pan Caudarax's older brood have settled here, and giants are "
            "fairly common, above all of the clans of Geirrod and Bergelmir.",
        ),
        secrets=paragraphs(
            "Vis (p. 14): this may be Iceland's richest ground for it. A season "
            "of searching yields one pawn for each ten points of Per + "
            "Intellego + Vim + 10, likely of Perdo, Ignem, Terram, Aquam or "
            "Auram. The season costs at least a penalty to the aging roll, of "
            "a size the book does not print, and always draws the notice of "
            "something living here.",
            "The Dominion has never reached it. The book prints no aura for it "
            "(p. 14).",
        ),
    )
    glacier = "Mountains and glaciers normally have Magic 2 (p. 9)."
    myrdal = b.place(
        "Myrdalsjokull",
        inside=iceland,
        aura=2,
        summary="A southern glacier, with the volcano Katla under its ice.",
        secrets=glacier,
    )
    vatna = b.place(
        "Vatnajokull",
        inside=iceland,
        aura=2,
        summary="The great glacier, with the Lava Fields of Misdeeds to its "
        "north and the volcanoes Grimsvotn and Oraefi beneath it.",
        secrets=glacier,
    )
    active = "An active volcano"
    b.place("Katla", inside=myrdal, summary=f"{active} beneath Myrdalsjokull.")
    b.place("Grimsvotn", inside=vatna, summary=f"{active} beneath Vatnajokull.")
    b.place("Oraefi", inside=vatna, summary=f"{active} beneath Vatnajokull.")
    myvatn = _short(
        b, "Lake Myvatn", iceland, "A northern lake, by the volcano Krafla."
    )
    b.place("Krafla", inside=myvatn, summary=f"{active} at Lake Myvatn.")
    islands = _short(
        b,
        "Vestmannaeyjar",
        iceland,
        "Islands holding the volcano Helgafell.",
    )
    b.place(
        "Helgafell in Vestmannaeyjar",
        inside=islands,
        summary=f"{active} on the islands. Not the monastery of Helgafell in the west.",
    )
    _short(
        b,
        "Heimaey",
        iceland,
        "An island off the south coast.",
    )
    _short(
        b,
        "Hvannadalshnukur",
        iceland,
        "A height near the south-east coast.",
    )
    thingvoll = _short(
        b,
        "Thingvoll",
        iceland,
        "The assembly field beside a lake in the south-west, also called Thingvellir.",
    )
    _short(
        b,
        "The Oxara",
        thingvoll,
        "The river of the assembly field, also called the Axe, with an islet "
        "where men fought holmganga until the law ended "
        "it in 1007. The last recorded duel there was Gunnlaugur "
        "Serpent-Tongue's.",
    )
    _short(
        b,
        "Snaefelljokul",
        west,
        "The glacier Eirik the Red sailed from when he went looking for Greenland.",
    )
    snaefellsnes = _short(
        b,
        "Snaefellsnes",
        west,
        "Part of Thord Sturluson's domain, with Dalir.",
    )
    _short(
        b,
        "Snaefell",
        snaefellsnes,
        "The great volcano near the tip of the peninsula, seen from a hundred "
        "miles off, with one main peak north of its crater and one south.",
    )
    _short(
        b,
        "Dalir",
        west,
        "Part of Thord Sturluson's domain, with Snaefellsnes. Sighvat Sturluson "
        "began here before moving north.",
    )
    _short(
        b,
        "Hvamm",
        west,
        "The home of Sturla Thordarson, father of the Sturlung brothers.",
    )
    _short(
        b,
        "Borgarfjord",
        west,
        "Snorri Sturluson's domain since 1202, when he came to take up his "
        "wife's inheritance.",
    )
    _short(
        b,
        "Rekjaholt",
        west,
        "Snorri Sturluson's home.",
    )
    _short(
        b,
        "Vestfirdir",
        west,
        "The western fjords, the largest district still keeping the old "
        "bond between godar and baendur.",
    )
    _short(
        b,
        "Vatsfjord",
        west,
        "Seat of a godord, and home of Snorri Sturluson's brother-in-law Thorvald.",
    )
    _short(
        b,
        "Eyjafjordur",
        north,
        "Where Sighvat Sturluson moved to take over chieftaincies given to his son.",
    )
    _short(
        b,
        "Skagafjord",
        districts["Hegranesthing"],
        "The Asbirningar's home district, in the Northern Quarter.",
    )
    _short(
        b,
        "Oddi",
        districts["Rangarthing"],
        "The home of the Oddaverjar, from which Jon Loftsson arbitrated "
        "between chieftains of all four Quarters.",
    )
    _short(b, "Orlygsstad", iceland, "Where Sighvat and Sturla will fall in 1238.")
    _short(
        b,
        "Haugnes",
        iceland,
        "Field of the greatest battle in Iceland's history, to come in 1246.",
    )
    _short(
        b,
        "Reykjavik",
        iceland,
        "Smoky Bay, where Ingolfur Arnarson made his home in 874.",
    )
    _short(
        b,
        "Husavik",
        north,
        "A north coast harbour where Gardar Svavarsson wintered in 855.",
    )
    _short(
        b,
        "The Eastern Fjords",
        east,
        "The fjords of the east coast.",
    )
    _short(
        b,
        "Haukadalur",
        iceland,
        "The home of the Haukdaelir, and of one of Iceland's two most famous schools.",
    )
    _short(
        b,
        "Vapnafjord",
        iceland,
        "A place whose men have a quarrel with the trolls of the Eastern Quarter.",
    )
    _short(
        b,
        "Kirkadale",
        iceland,
        "A valley of farms well above the lowlands.",
    )


def _west_over_sea(b: Builder) -> None:
    greenland = b.place(
        "Greenland",
        realm="",
        summary=paragraphs(
            "The land Eirik the Red found in 982, once outlawed from Iceland as "
            "he had been from Norway. A Norwegian called Gunnbjorn had sighted "
            "it some fifty years earlier. Eirik found open grass and plenty of "
            "bears, foxes, caribou, sea mammals, birds and fish, spent three "
            "years marking out farms along the coast, and settlers followed in "
            "986.",
            "It sends out furs and hides, ropes and cables, oil, woollens and "
            "sea-ivory, white bears and falcons, and takes in corn, iron, "
            "timber, clothes and luxuries.",
        ),
    )
    b.place(
        "The Eastern Settlement",
        inside=greenland,
        realm="",
        summary="The Greenland colony, governed on the Icelandic model. At its "
        "height it held 190 farms, twelve parish churches, a cathedral, a "
        "monastery and a nunnery.",
    )
    b.place(
        "Helluland",
        realm="",
        summary="Flatstone Land, which Leif Eiriksson found: "
        "mountains and glaciers, barren and without grass.",
        secrets="A realm ruled by giants, where King Dumb reigned and Bard "
        "Snaefellsass was born (p. 141). Fleeing trollsynir and giants make "
        "for it in the Icelandic Wars (Icelandic Wars p. 13).",
    )
    b.place(
        "Markland",
        realm="",
        summary="Leif Eiriksson's flat forest land, with long white sands and "
        "gently shelving beaches. Greenlanders still sail there in 1220 for "
        "furs and timber.",
    )
    b.place(
        "Vinland",
        realm="",
        summary=paragraphs(
            "Wineland, rich and fertile, with mild winters. A colonist blown "
            "off course saw it first, and fifteen years on Leif Eiriksson "
            "wintered there. His brother Thorvald died by a native arrow on "
            "the next voyage.",
            "Thorfinn Karlsefni brought three ships, 160 men, some wives and "
            "livestock, and stayed three winters before raids and quarrels "
            "over women sent him home. Freydis Eiriksdottir's attempt in 1019 "
            "turned to war at once against far greater numbers and was the "
            "last.",
        ),
    )


# -- the powers --


def _guardians(b: Builder) -> None:
    b.faction(
        "The Guardians of Iceland",
        faction="Spirits and beings",
        realm="Magic",
        summary=paragraphs(
            "Four great powers who answer the landvaettir, the spirits of the "
            "land, when danger comes to the island's shores. No one knows who "
            "set them there, but they are very old. The host goes first to the "
            "First Guardian, and passes to the next if he fails.",
            "Snorri Sturluson's Heimskringla tells how a warlock of King Harald "
            "of Denmark swam to Iceland as a whale. A dragon with serpents and "
            "toads drove him from the east, an eagle with its birds from the "
            "north, a gray bull with land spirits from the west, and a giant "
            "with an iron staff, leading other giants, from the south. He swam "
            "home, and the Danish fleet turned back.",
            "The First Guardian is the dragon Pan Caudarax, whose host of "
            "serpents, toads and fishes rolls with poison vapour. The Second "
            "is Vindsvall, an eagle whom most see as a dark storm cloud: his "
            "wings are the wind, and his cry the lightning. His host is birds "
            "of every kind.",
            "The Third is a gray bull, an aurochs as big as a house, its hide "
            "proof against iron. In 1105 it strayed after the bishop's cows at "
            "Skalholt, stayed too long and shrank, and herdsmen caught it. It "
            "has fathered strong calves; as it ages and dies a gray bull calf "
            "takes up its spirit.",
            "The Fourth is the chief of Iceland's jotunn, an office passed on "
            "to each new chief. Bard Dumbson is the second to hold it. All the "
            "clans of giants set aside their rivalries to march with him.",
        ),
        secrets=paragraphs(
            "Rules (p. 7): the landvaettir alert the Guardians only to a being "
            "of substantial magical power who means harm to the land or its "
            "people, judged as Sight of the Transparent Motive at Penetration "
            "45, resistance counting as hostile.",
            "Their weakness is within: they were set against invaders, and "
            "ignore magicians native to Iceland. In the Toframanna Saga the "
            "portal to the Scartaris Sanctum, opening inside Iceland, does not "
            "alert them either.",
            "Those without Second Sight see neither the spirit hosts nor the "
            "eagle, only a tumult of air or a storm. Under the Dominion the "
            "Gray Bull's power lies dormant, so the host goes past it to the "
            "Fourth Guardian; if it were freed its host would take the shapes "
            "of land animals. The landvaettir lend the giants power (p. 7).",
            "The landvaettir are described on p. 32, and Pan Caudarax's stats "
            "are on p. 140.",
        ),
    )


def _freestate(b: Builder) -> None:
    b.custom(
        "The Icelandic Freestate",
        decides="No king: the godar and the Althing, under the law.",
        rules="One law for the whole island, from 930. Magic of any sort is "
        "outlawed, though harmless magic goes unpunished by quiet agreement. "
        "Slavery stays lawful, but by 1220 debt slaves are the only ones often "
        "seen.",
        summary=paragraphs(
            "Irish priests came in coracles about 790 and for eighty years spent "
            "their summers here in prayer. When the Norse arrived, they had "
            "seen enough of Vikings at home and sailed away.",
            "Word of the island spread after Naddoddur found it in 850, just as "
            "Harald Fairhair was making himself overlord of Norway, and many "
            "had reason to leave. Within sixty years the farmland was taken, "
            "by ten to twenty thousand people from Norway and the Norse "
            "colonies of Ireland, Scotland and the Hebrides. Gaelic wives, "
            "followers and slaves came with them, but left only a few "
            "place-names and their blood.",
            "Richer settlers raised temples and gave oxen and horses for "
            "sacrifice, and so became godar (singular godi), godly ones. A "
            "godi's power rested on how many householders, baendur (singular "
            "bondi), would freely ally with him as thingmen.",
            "Slaves cost more to feed than they earned, and spare land had to "
            "be defended, so owners freed them as labourers and tenants. "
            "Freedmen often came to own land, and their children were born "
            "free. Most slaves were free by the tenth century, and household "
            "slaves were very rare by the mid twelfth.",
            "Disputes first went to district spring assemblies, the varthing, "
            "each run by three local godar. With settlers from everywhere and "
            "no shared law, and no wish to ask Norway's king, the chieftains "
            "sent Ulfjot of Lon to study the Gulathing Law. With his uncle "
            "Thorleif the Wise he adapted it, and in 930 the Althing met.",
            "Magicians came with the settlers, drawn by the island's strong "
            "spirits and plentiful magical resources, and they were busy, for "
            "with the priests gone violent spirits, trolls and beasts fell on "
            "the farms, and wards were much sought after.",
            "Magicians were respected in pagan days, but magic in matters of "
            "honour was hated, and they kept out of feuds. A godi who practised "
            "invited talk of dishonour, so most godar chose politics, though "
            "they might seek magical help in secret. To keep the godar from "
            "leaning on them, the leading magicians formed a hreppur, which set "
            "wards against trolls on the trails, fixed the cost of their "
            "services, refused the blacklisted, backed members under pressure, "
            "treated with giants and dragons, and ruled the gathering of Ond, "
            "which is vis, from magical sites.",
            "After the conversion of 1000 the fear of hell became real to the "
            "magicians, and from 1020 private pagan worship was banned. Within "
            "a generation vitkir went from honoured priests to likely outlaws. "
            "Other magicians worked on in the open until, in 1031, a curse "
            "helped to kill the heroic outlaw Grettir. The outrage brought a "
            "ban on all magic, with lesser outlawry for spells and full "
            "outlawry for sorcery that sickened or killed.",
            "After a run of convictions the leading magicians met, admitted "
            "volur and visindamen to the hreppur for the first time, and gave "
            "the Christian party what it asked for. For ten years no magic was "
            "worked. Famine came, cattle sickened, fish failed, storms came "
            "unwarned, the trail wards failed and trolls took travellers and "
            "herds. In the end great baendur and godar quietly promised that "
            "cases over harmless magic would be crushed and charges of black "
            "sorcery fairly heard. The magicians came back, known to all and "
            "spoken of by none.",
            "In the twelfth century the most successful godar began to act as "
            "aristocrats, and saw what several chieftaincies (godord) could do "
            "for a man. Around 1200 the sons of Sturla began gathering them in "
            "the Western Quarter, and the race for mastery of Iceland began. By "
            "1220 nearly all of it lies in eight unstable domains, riki, ruled "
            "by close relatives from five families: the storgodar, big "
            "chieftains.",
            "Most baendur have lost their free choice of godi, and storgodar "
            "take little interest in local quarrels, so rich storbaendur, big "
            "householders, have become local advocates. Their loyalty still "
            "decides contests between storgodar, and their stout refusal of "
            "every tax keeps any one man from winning outright.",
            "Even inside the riki the storgodar rarely own every chieftaincy. "
            "Lesser chieftains lend their godord or follow a greater man and "
            "keep control under his protection, for failing to protect one's "
            "thingmen is a great shame, and few can stand alone. Yet no godi "
            "gives up his title unless honour leaves no other way.",
            "King Hakon of Norway now reaches for the Norse lands of the North "
            "Atlantic. His father-in-law Earl Skuli threatened Snorri Sturluson "
            "at court with a fleet. Snorri talked him out of it by offering to "
            "go home and win the chieftains over to the Crown, a cause he does "
            "not mean to champion.",
            joined_lines(
                "Timeline:",
                *(f"{date}: {words}" for _, date, words in TIMELINE),
            ),
        ),
        secrets=paragraphs(
            "The law on magic is quoted from Gragas on p. 14: lesser outlawry "
            "for spells, a panel of twelve, and full outlawry for black "
            "sorcery.",
            "Figures differ in the book: ten to twenty thousand settlers "
            "(pp. 8, 17) against 40-50 thousand people by 930 (p. 17). The "
            "hreppur is of the early tenth century on p. 12 and 950 on pp. 11 "
            "and 17. Skuli's expedition of 1218-1220 in the timeline (p. 18) "
            "sits oddly with the fleet Snorri talks him out of sending "
            "(p. 16). Both are entered as printed.",
            "Spellings: Isleif Gizursson and Jon Ogmundarson follow p. 43, "
            "where p. 18 prints Gizarson and Ogmudarson, and Bishop Gizur "
            "follows p. 43 for Gizurr.",
        ),
    )


def _families(b: Builder) -> None:
    b.faction(
        "The Svinfellingar",
        faction="Family",
        summary="The first family to reach beyond one or two godord. By 1220 "
        "they own the whole Eastern Quarter, split into two riki under the "
        "brothers Orm and Thorarin Jonsson.",
    )
    b.faction(
        "The Asbirningar",
        faction="Family",
        summary="Named for Asbjorn Arnorsson, of about 1100. Kolbeinn Tumason "
        "first ruled Skagafjord, added Hunavatnsthing, and by his death in 1208 "
        "had reached the western edge of the Northern Quarter. His brother "
        "Arnor leads them now, but is failing, and Kolbeinn the Young, Arnor's "
        "son, looks likely to follow soon.",
    )
    b.faction(
        "The Oddaverjar",
        faction="Family",
        decides="The family rules its district as a group.",
        summary="Jon Loftsson of Oddi was so respected that chieftains of all "
        "four Quarters sought him as arbitrator. He and his sons Orm and Pall, "
        "later bishop, came to rule all of Rangarthing. Pall died in 1211 and "
        "Orm in 1218, so the chieftaincies are shared among the third son, "
        "Saemundur, and his children.",
    )
    b.faction(
        "The Haukdaelir",
        faction="Family",
        summary="Prominent in bringing Christianity to Iceland, they hold all "
        "three chieftaincies of Arnesthing, and keep a famous school at "
        "Haukadalur.",
        secrets="The history prints Haukdaelir (p. 15) and the section on "
        "literacy Haukadalja (p. 24); the pack uses the first.",
    )
    b.faction(
        "The Sturlungar",
        faction="Family",
        summary="Descended from Sturla Thordarson of Hvamm in the Western "
        "Quarter. Sturla himself never held more than one chieftaincy, but his "
        "sons Thord, Snorri and Sighvat, each with a riki, are among the most "
        "powerful and ambitious chieftains of the age.",
    )


def _riki(
    b: Builder, quarters: dict[str, Neighbour], districts: dict[str, Neighbour]
) -> None:
    west, north = quarters["West"], quarters["North"]
    entries: tuple[tuple[str, str, Neighbour, str], ...] = (
        (
            "Riki of Skaftafellsthing",
            "Orm Jonsson",
            districts["Skaftafellsthing"],
            "A Svinfellingar domain, ruled by Orm Jonsson since 1212.",
        ),
        (
            "Riki of Mulathing",
            "Thorarin Jonsson",
            districts["Mulathing"],
            "A Svinfellingar domain, ruled by Orm's brother Thorarin Jonsson "
            "since 1220.",
        ),
        (
            "Riki of the Asbirningar",
            "Arnor",
            north,
            "The west of the Northern Quarter, from Skagafjord through "
            "Hunavatnsthing. Arnor is storgodi, in failing health.",
        ),
        (
            "Riki of Rangarthing",
            "Saemundur",
            districts["Rangarthing"],
            "The Oddaverjar's district, shared by Saemundur son of Jon Loftsson "
            "and his children.",
        ),
        (
            "Riki of Arnesthing",
            "",
            districts["Arnesthing"],
            "The Haukdaelir's three chieftaincies.",
        ),
        (
            "Riki of Snaefellsnes and Dalir",
            "Thord Sturluson",
            west,
            "Thord Sturluson, content most of the time with one chieftaincy, "
            "shares the district with his ambitious nephew Sturla Sighvatsson, "
            "but men still count Thord the storgodi.",
        ),
        (
            "Riki of Borgarfjord",
            "Snorri Sturluson",
            west,
            "Snorri Sturluson moved here in 1202 for his wife's inheritance, "
            "and is quickly securing other chieftaincies of the Thverarthing.",
        ),
        (
            "Riki of Vadlathing and Thingeyjarthing",
            "Sighvat Sturluson",
            north,
            "All the east of the Northern Quarter. Sighvat, third son of "
            "Sturla, started in Dalir and moved north to Eyjafjordur for "
            "chieftaincies given to his son.",
        ),
    )
    for name, ruler, place, summary in entries:
        b.lord(name, title="", manors=0, ruler=ruler, place=place, summary=summary)


def _norway(b: Builder) -> None:
    b.lord(
        "King Hakon Hakonarson of Norway",
        title="",
        manors=0,
        ruler="Hakon Hakonarson",
        summary="Called the Elder, and still a youth in 1220, he seeks control "
        "of every Norse land in the North Atlantic. Earl Skuli Bardson, his "
        "father-in-law, acts for him.",
    )


def _peoples(b: Builder) -> None:
    b.faction(
        "The Storgodar",
        faction="Estate or rank",
        summary="The big chieftains, closely related men of the five great "
        "families who rule the eight riki. Local quarrels bore them, and the "
        "householders' refusal of every tax keeps each from final mastery.",
        rules="Their rise and their limits are told on pp. 15-16.",
    )
    b.faction(
        "The Storbaendur",
        faction="Estate or rank",
        summary="The big householders, rich men who stepped in as local "
        "advocates when the storgodar lost interest in small disputes. Their "
        "loyalty still decides contests between storgodar, and fighting other "
        "men's cases brings them respect and wealth.",
        rules="Pp. 15, 38.",
    )
    b.faction(
        "The Draug",
        faction="Spirits and beings",
        realm="Magic",
        summary="The restless dead of the early settlement. With no Christian "
        "burial to lay them, the magic in the air sometimes raised a corpse, "
        "which troubled its farm until magic or metal ended it. Only an "
        "enchanted burial kept a body in the ground.",
        rules="P. 9.",
    )
    b.faction(
        "The Papar",
        faction="Religious community",
        realm="Divine",
        summary="The Irish priests who summered in Iceland from about 790, and "
        "whose prayers drove back the magical beasts. They fled the Norse and "
        "did not return.",
    )
    b.faction(
        "The Skraelingar",
        faction="People or tribe",
        summary="The people of Vinland, named screechers or uglies by the Norse. "
        "They traded gladly at first, keen on metal, which Karlsefni would not "
        "sell as weapons, and on red cloth. When the cloth ran out the raids "
        "began. With no shared tongue no peace could be made, and their "
        "numbers overwhelmed the last Norse attempt.",
    )


# -- the stories --


def _stories(b: Builder, iceland: Neighbour) -> None:
    dormant(
        b.threat(
            "The Storgodar Feud",
            antagonist="The storgodar, and King Hakon of Norway",
            moves=DATED,
            place=iceland,
            summary="Driven by the ambition of the Sturlungar and their rivals, "
            "and by the Crown of Norway waiting for them to exhaust themselves. "
            "These are the last four decades of the Freestate as the Sturlunga "
            "Saga tells them; the book points to its bibliography (p. 143) for "
            "more. The stages follow pp. 18-19.",
            stages=[
                S(
                    "Snorri's second term",
                    year=1222,
                    ignored="Snorri Sturluson is Lawspeaker again until 1231. The "
                    "Prose Edda is composed in 1222.",
                ),
                S(
                    "The Snorrunga godord",
                    year=1228,
                    ignored="Snorri and Thord failed to claim their right, and "
                    "Sighvat took the godord and gave it to his son Sturla. "
                    "Snorri demands it at the Althing, gets no decision, and "
                    "seizes it, helped by his violent brother-in-law Thorvald of "
                    "Vatsfjord. That summer Thorvald is burnt to death in "
                    "revenge.",
                ),
                S(
                    "Thorvald's sons strike",
                    year=1229,
                    ignored="Blaming Sighvat and Sturla, they destroy Sturla's "
                    "property while he happens to be away.",
                ),
                S(
                    "A brief respite",
                    year=1230,
                    ignored="Snorri proves he had no part in the attack, and "
                    "makes peace with his nephews and with Sighvat.",
                ),
                S(
                    "Sturla's killing",
                    year=1232,
                    ignored="Seeking peace, Sturla is insulted by Thorvald's sons "
                    "and kills them, and goes on pilgrimage to Rome for it. "
                    "Snorri's illegitimate son Oraekia takes the Vatsfjord godord "
                    "and sends armed bands to plunder his own people.",
                ),
                S(
                    "The promise in Norway",
                    year=1234,
                    ignored="Coming home from Rome, Sturla falls under the sway "
                    "of Hakon and Skuli, and promises to subdue Iceland for the "
                    "title of earl.",
                ),
                S(
                    "Sturla against Snorri",
                    year=1235,
                    ignored="Sturla raises an army. Snorri will not fight his kin "
                    "and flees to the Eastern Quarter, though Thord tries to "
                    "reconcile them. Sturla takes Rekjaholt. Oraekia harries "
                    "Borgarfjord by sea, is taken by Sturla's false offer of "
                    "peace, and escapes blinding and maiming. Roused, Snorri "
                    "attacks and is beaten.",
                ),
                S(
                    "The summons",
                    year=1237,
                    ignored="To end it Hakon calls the godar to Norway, and "
                    "Snorri and his allies go.",
                ),
                S(
                    "Orlygsstad",
                    year=1238,
                    ignored="Sturla rules most of Iceland, opposed only by "
                    "Kolbeinn the Young and Gizur Thorvaldsson, husbands of "
                    "Snorri's daughters. Sturla seizes Gizur by a trick; Kolbeinn "
                    "forms a league and Gizur escapes to join it. At Orlygsstad "
                    "Sighvat and Sturla are beaten. New tyrants replace the old.",
                ),
                S(
                    "Earl Snorri",
                    year=1239,
                    ignored="Hakon's plan has failed. Duke Skuli makes Snorri an "
                    "earl, to rule Iceland for Norway if Skuli takes the crown. "
                    "Snorri goes home.",
                ),
                S(
                    "Skuli's fall",
                    year=1240,
                    ignored="Skuli's bid for the throne ends in his death.",
                ),
                S(
                    "The death of Snorri",
                    year=1241,
                    ignored="Hakon suspects Snorri and names Gizur to bring him "
                    "to Norway or kill him. Warned, Snorri escapes Kolbeinn at "
                    "the Althing to a church. That summer Gizur and Kolbeinn "
                    "enter his home at Rekjaholt in secret and kill him. Oraekia "
                    "tries to avenge him and is banished.",
                ),
                S(
                    "The Sturlungs fade",
                    year=1242,
                    ignored="Gizur leads the south alone and Kolbeinn holds the "
                    "west and north. Thord Kakali, Sighvat's only surviving son, "
                    "comes home to avenge the family.",
                ),
                S(
                    "Haugnes",
                    year=1246,
                    ignored="In the greatest battle Iceland has seen, Thord "
                    "breaks Kolbeinn and his kinsman Brand and takes the north "
                    "and west. He and Gizur agree to Hakon's arbitration; the "
                    "next spring Hakon favours Thord, who rules unopposed for "
                    "four years while Gizur stays in Norway.",
                ),
                S(
                    "The honourable captive",
                    year=1251,
                    ignored="Hakon, jealous, keeps Thord in Norway, and sends "
                    "Gizur home to win full recognition of the Crown.",
                ),
                S(
                    "Earl Gizur",
                    year=1258,
                    ignored="Gizur is made earl over the North and South "
                    "Quarters and all of Borgarfjord.",
                ),
                S(
                    "The Old Covenant",
                    year=1262,
                    ignored="At local assemblies Hakon's men offer peace for "
                    "allegiance. The men of the North and South swear, giving him "
                    "suzerainty and keeping Icelandic law. Hakon abolishes every "
                    "godord, and storgodar who will not swear lose their power.",
                ),
                S(
                    "King Magnus",
                    year=1263,
                    ignored="Hakon dies. His son Magnus Law-Mender takes care not "
                    "to offend the Icelanders.",
                ),
            ],
            secrets="The book spells Thorvald's fjord Vatsfjord and Vatfjord, "
            "Borgarfjord also Bogarfjord, and Kolbeinn also Kolbein (pp. 15, "
            "18-19); Skuli is Earl on p. 16 and Duke on pp. 18-19. The story "
            "here uses one spelling of each. Snorri's home is printed only as "
            "Rekjaholt.",
        )
    )
    dormant(
        b.threat(
            "The Eclipse of 1248",
            antagonist="The brood of Pan Caudarax",
            moves=DATED,
            summary="The dragon's eggs, laid at Hekla in 232, are due to hatch "
            "on one day. The book says no more of what follows (p. 11).",
            stages=[
                S(
                    "The eggs hatch",
                    year=1248,
                    season="Spring",
                    ignored="On the day of the solar eclipse of 22 May 1248.",
                )
            ],
        )
    )
    lava = "A possible encounter in the Lava Fields of Misdeeds (p. 14). "
    dormant(
        b.threat(
            "The Fire-Giant's Illusions",
            antagonist="A fire-giant",
            moves=TRACK,
            summary=f"{lava}The characters are caught in a fire-giant's illusions.",
        )
    )
    dormant(
        b.threat(
            "The Outlaws' Blood Bargain",
            antagonist="Outlaws, and the malicious spirits they serve",
            moves=TRACK,
            summary=f"{lava}Outlaws here feed the blood of those they catch to "
            "spiteful spirits, and are paid for it.",
        )
    )
    dormant(
        b.threat(
            "The Brood's Toll",
            antagonist="Two older dragons of Pan Caudarax's brood",
            moves=TRACK,
            summary=f"{lava}A pair of Pan Caudarax's elder young stop any "
            "magus crossing the fields and make him pay in vis.",
        )
    )
