"""The Levant's regions and places (ch03, ch04, ch05, ch07), as of 1220.

Inside places["levant"] (tribunal.py's) the ten sub-regions:
places["jerusalem_kingdom"], ["tripoli_county"], ["antioch"] (the
Principality), ["cyprus"], ["lesser_armenia"], ["egypt"], ["sinai"],
["syria"] (named "Bilad al-Sham"), ["asia_minor"] (named "Asia Minor",
which no Theban record uses, L21) and ["alan_lands"]. Iraq, Georgia and
Greater Armenia are the shared places["iraq"], ["georgia"] and
["greater_armenia"], which tribunal.py sets inside the Levant.

The twelve towns of the Levant's own, as town records in world:
world["acre"], ["tripoli"], ["antioch_city"] (the city; places["antioch"]
is the Principality), ["nicosia"], ["famagusta"], ["cairo"],
["alexandria"], ["damietta"] (the Crusade's since 1219; Divine 1, none
at night, in its summary), ["jerusalem"], ["damascus"], ["aleppo"] and
["konya"]. Baghdad and Mosul are shared (world["baghdad"],
world["mosul"]). Each town's lord is set as its liege in finish, when
the lord's part has made it: world["jerusalem_king"] (Acre),
["tripoli_count"] (Tripoli), ["antioch_prince"] (Antioch),
["cyprus_king"] (Nicosia, Famagusta), ["al_kamil"] (Cairo, Alexandria),
["al_muazzam"] (Jerusalem, Damascus), ["al_aziz"] (Aleppo) and
["sultan_of_rum"] (Konya). The Italian communes, the courts and the
Latin coinage are in Acre's summary (L20).

The places with an aura, a regio, a covenant site, a story or a ruler
(checklist 10, L21): places["holy_city"] (Jerusalem, Divine 4, with the
Infernal 5 night of 15 July; the town of Jerusalem sits inside it) and in
it ["dome_of_the_rock"], ["aqsa_mosque"], ["holy_sepulchre"] and
["western_wall"] (each Divine 10), ["holy_fire"] (inside the
Sepulchre) and ["hidden_temple"] (a Divine regio level, 8, listed);
["giza"] (Magic 5; its level 1 is the temple of Thoth and Anubis, Magic
6, the second Pyramids' site) and ["great_pyramids"] (Magic 6, inside
Giza); ["babel"] (Magic 1, in Iraq; the shared places["harut_and_marut"]
is set inside it in finish); ["petra"] (Urbs Rubra's site, Magic 3,
listed, with its jinn in the summary); ["umayyad_mosque"] (Damascus,
with the Head of John the Baptist and its Faith Points);
["tower_of_serpents"] (Aleppo's talisman); ["mount_sinai"];
["mount_carmel"] (the Carmelites'); ["hattin"]; ["syrian_mountains"]
(Amirat al-Jabal's home); ["upper_egypt"] (the naddahas' wells);
["lebanon"] (the Druze refuge); ["taurus"] (al-Arama's mountains);
["harran"] (the Sabeans); ["colchis"] (in Georgia); and ["tarsus"]
(the Armenian king's seat). The covenant parts make their own sites
inside these regions.

Appended to places["levant"]'s summary in finish (L19, L21, L28): Sunni
Islam and its four schools, the Sufis, the dhimmis, the Dominion as
Realms of Power: The Divine describes it in place of the book's Islamic
aura table, the foreigners' optional -5 to +5 social rule, the jinn's
dwellings at wells, crossroads and rivers, the beings named without
stats who wander the whole land, and the coinage. The book gives none of
these places vis, so none has suggested vis sources (L10)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Levant

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
RUMOURED_LOCALLY: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
RUMOURED_REGION: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}


def _add(levant: Levant, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = levant.b.place(name, **kw)
    levant.places[key] = place
    return place


def build(levant: Levant) -> None:
    _regions(levant)
    _jerusalem(levant)
    _syria(levant)
    _egypt_and_sinai(levant)
    _the_north(levant)
    _babel(levant)
    _towns(levant)


# -- the regions --


def _regions(levant: Levant) -> None:
    region = levant.places["levant"]
    _add(
        levant,
        "jerusalem_kingdom",
        "The Kingdom of Jerusalem",
        inside=region,
        summary=paragraphs(
            "What is left of the Latins' kingdom since Salah al-Din's "
            "conquests of 1187: a narrow strip of coast from Beirut in "
            "the north down to Ascalon, saved by the crusades of the "
            "1190s. Jerusalem itself is not in it; the capital is Acre. "
            "Latin nobles rule over native Christians, Jews and Muslims, "
            "who are their subjects. The kingdom lives chiefly on the "
            "trade passing from the East to Europe, and grows grain, "
            "olives and vines besides. John of Brienne governs it as "
            "regent for his daughter Isabel, called Yolanda, and the "
            "king of Jerusalem claims precedence over the rulers of "
            "Antioch and Tripoli.",
            "The Crusade now in Egypt has opened a quarrel: the papal "
            "legate holds that whatever it conquers will not belong to "
            "the kingdom, and nothing will settle that until the Crusade "
            "is over.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "tripoli_county",
        "The County of Tripoli",
        inside=region,
        summary=paragraphs(
            "The coast north of Beirut as far as Valania, reaching a "
            "little further inland than the kingdom to its south; on "
            "its north-eastern side it meets Masyaf and the lands of "
            "the Nizaris. Latin lords rule here too, over Muslim, "
            "Christian and Jewish natives. When Count Raymond III died "
            "in 1187 the county passed to the house of Antioch, so its "
            "count is Bohemond IV, prince of Antioch, who counts as the "
            "first of his name in Tripoli. Trade brings most of its "
            "wealth, with fruit and grain.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "antioch",
        "The Principality of Antioch",
        inside=region,
        summary=paragraphs(
            "The north-eastern corner of the Levantine coast, much the "
            "smallest of the Latin states on the mainland. Bohemond III "
            "meant it for his grandson Raymond-Rupen when he died in "
            "1201, but the boy's uncle, Bohemond IV, pushed him aside. "
            "Raymond-Rupen won the city back for a while in 1216 and "
            "lost it to his uncle again in 1219, the year he also "
            "inherited Lesser Armenia from his great-uncle Leon II. He "
            "is at Tarsus now making his hold there firm, and is likely "
            "to try for Antioch once more when he has; meanwhile "
            "Bohemond IV rules from the city.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "cyprus",
        "Cyprus",
        inside=region,
        summary=paragraphs(
            "The youngest Latin state and the only one off the mainland: "
            "an island some 150 miles by 70, with mountains along its "
            "north and west and a broad plain over most of the rest. Its "
            "fertile land gives most of its wealth, wine and salt above "
            "all, and most of its people live in the countryside. "
            "Richard the Lionheart sold it to Guy de Lusignan in 1192, "
            "and Guy's great-nephew Henry I is king now. The Latins rule "
            "but most Cypriots are Greeks, and the island stays Greek in "
            "its ways.",
            "The Lusignans brought the mainland's feudal law with them "
            "and pressed the Greek majority into subjection, though some "
            "wealthier Greeks are still free. Unlike the mainland, the "
            "king lets few vassals hold castles, for fear of revolt; the "
            "ban on church fiefs is strictly kept; the church is under "
            "an archbishop at Nicosia rather than a patriarch; and the "
            "king answers to no king of Jerusalem. Its ports are "
            "Kyrenia on the north coast, Limassol, once the chief one, "
            "and Famagusta, which is taking its trade.",
            "The book suggests that no magus of the Tribunal may yet "
            "have settled on Cyprus, which would leave room for a new "
            "covenant, if it took care not to alarm the wary "
            "Lusignans.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "lesser_armenia",
        "Lesser Armenia",
        inside=region,
        summary=paragraphs(
            "Cilicia, once the western arm of Greater Armenia: mountains "
            "for the most part, with a thin coastal plain that broadens "
            "towards the east. A Byzantine land, it filled with "
            "Armenians from the east in the tenth century; after "
            "Manzikert in 1071 local dynasties set up for themselves, "
            "outlasted the Seljuks, and dealt with Latins and Byzantines "
            "by turns through the Crusades. Leon II was recognised as "
            "king in 1198. He died in 1219 after reigning thirty-two "
            "years, and his great-nephew Raymond-Rupen, put out of "
            "Antioch, now rules at Tarsus, on an uneasy throne: Tarsus "
            "itself would rather have Leon's first cousin Constantine.",
            "It lives on timber from the Taurus forests, goatskins and "
            "goat-hair cloth, and is known for its metalwork and its "
            "illuminated books; it trades with Genoa and Venice. Its "
            "kings keep the Armenian national church, which answers "
            "neither to Rome nor to Constantinople. Some Armenian "
            "illuminations are said to be enchanted and to glow in the "
            "dark, and no one knows who makes them, or why.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "egypt",
        "Egypt",
        inside=region,
        summary=paragraphs(
            "Muslim since the conquest of 639 to 642, governed for the "
            "caliphs until the Fatimids took it in 969; Salah al-Din "
            "ended their dynasty in 1171 and brought the land back to "
            "Sunni Islam, and it has been the seat of his family's power "
            "ever since. His nephew al-Kamil is sultan now. Since the "
            "1160s the Crusaders have known that Egypt is the key to "
            "winning back the Levant, and they keep coming: the present "
            "Crusade holds Damietta in the Nile delta.",
            "The towns cluster along the Nile, which gives water and "
            "carries goods, and the yearly flood keeps the delta and the "
            "valley rich; most of the rest is desert, roamed by Bedouin. "
            "Egypt trades its own produce and what comes down the Nile "
            "or across the Indian Ocean: spices, cloth, grain, sugar "
            "and gold. Coptic Christians and Jews live among its "
            "Muslims. Its old temples and tombs are everywhere, and "
            "priests still call on its ancient gods in their shadow.",
            "Far up the Nile, past Egypt's borders, lies Christian "
            "Ethiopia; beyond it, travellers say, the Ring of Fire, "
            "where the air is aflame and the sea boils, and past that a "
            "land of marvels where Prester John is king.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "sinai",
        "Sinai",
        inside=region,
        summary=paragraphs(
            "The peninsula between Egypt and the Holy Land: mountains in "
            "the south ringed by desert, marshes in the north, and fine "
            "beaches on the Red Sea shore. All three faiths of the land "
            "trace part of their beginnings here, at Mount Sinai deep in "
            "the south. Para Belli, the Covenant of Lions, hides a "
            "fortress somewhere in its deserts.",
            "Lilith, the first wife of Adam, who left him rather than "
            "be ruled by him, made her home by the Red Sea and mothered "
            "demons there; she still steals and kills children, boys "
            "above all, and Jewish mothers buy amulets from a baal shem "
            "against her. She is named here without stats (Kabbalah "
            "says more).",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "syria",
        "Bilad al-Sham",
        inside=region,
        summary=paragraphs(
            "The country of Syria, as the Muslims call it: the land of "
            "the later Syria, Lebanon, Jordan and Israel, and the edge "
            "of south-eastern Anatolia. Bar what the Latins and a few "
            "other Muslim lords hold, Ayyubid emirs govern it under the "
            "sultan in Cairo; the greatest of them are al-'Aziz, Salah "
            "al-Din's grandson, at Aleppo, and al-Mu'azzam, his nephew, "
            "at Damascus.",
            "Two ranges of mountains run side by side from north to "
            "south with a rift valley between. A coastal plain, narrow "
            "for most of its length, lies between the western range and "
            "the sea; the eastern range, lower and more broken, gives "
            "way to the Syrian desert, which runs on to the Euphrates. "
            "Its valleys are fertile, and the Holy Land is famous for "
            "its fruit, sugar cane and indigo and for what it mines and "
            "quarries: chalk, marble, sulphur, salt and bitumen. Most of "
            "its people are Muslims, with Jews and Christians of many "
            "churches among them.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "asia_minor",
        "Asia Minor",
        inside=region,
        summary=paragraphs(
            "The Levant Tribunal's share of Anatolia: everything east of "
            "the Empire of Nicaea, which belongs to Thebes by the border "
            "ruling. Most of it is the Seljuk sultans' Bilad al-Rum, the "
            "Romans' country, theirs since the eleventh century: rugged, "
            "crossed by mountain ranges with forests on their flanks, "
            "and at its heart a desert plateau between the Pontic "
            "mountains to the north and the Taurus to the south. Its "
            "towns are many. Turks rule over Georgians, Armenians, "
            "Persians and Greeks, most of them Muslim, a hardy people; "
            "the townsfolk trade round the Black Sea, with the Russians "
            "and the Venetians of Constantinople, through Sinope, and "
            "their carved wood and pottery are prized, while country "
            "folk raise sheep, goats and very fine fruit.",
            "On the Black Sea coast the Empire of Trebizond is the "
            "Levant's too. Two Comnenus brothers, Alexius and David, "
            "seized the city from its Byzantine governor within days of "
            "Constantinople's fall in 1204 and, with Georgian help, made "
            "an empire of the southern shore. Nicaea and the Turks have "
            "since cut it back, last when the Turks took Sinope in 1214, "
            "and it now owes the Seljuk sultan tribute and soldiers, "
            "though it takes tribute of its own from the Crimea. "
            "Alexius still reigns. Its mild, fertile coast grows olives "
            "and vines among its forests, so it lives by timber, oil and "
            "wine, and the Greek church holds sway there.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "alan_lands",
        "The Alan Lands",
        inside=region,
        summary=paragraphs(
            "The mountains of the Caucasus and the country north of "
            "them, north-east of the Black Sea, where the Alans live in "
            "many tribes. Most are Greek Christians, though their "
            "loyalty to the church has wavered at times. It is the "
            "Tribunal's remotest corner: Urania, its second covenant, "
            "has survived here since 806 by being so hard to reach. A "
            "people of faeries the magi call the Genjii live near it, "
            "so like the jinn that Urania's leader suspects the two "
            "share an ancestor.",
        ),
        **KNOWN_TRIBUNAL,
    )


# -- Jerusalem --


def _jerusalem(levant: Levant) -> None:
    syria = levant.places["syria"]
    city = _add(
        levant,
        "holy_city",
        "The Holy City of Jerusalem",
        inside=syria,
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "The holiest place in the Levant, sacred to all three of its "
            "faiths. For Muslims the Prophet rose from here through the "
            "seven heavens on his night journey; Abraham lived here; "
            "and here the dead will rise for the Last Judgement. For "
            "Christians it is where Christ died and rose again; for "
            "Jews, the capital of the Promised Land and the Temple's "
            "site. So many holy places make many Dominion auras, and "
            "every one of them in the city is a point stronger than it "
            "would be anywhere else, up to 10: the city at large has a "
            "Divine aura of 4. Where faiths share a site, the strongest "
            "aura holds.",
            "The Ghosts of Jerusalem. Ever since the massacre of 15 July "
            "1099 the city has been haunted. Each year on the night of "
            "15 July its Dominion auras give way to Infernal 5, and "
            "the ghosts of the slaughtered crowd the streets, "
            "shrieking and wailing, until anyone who goes out among "
            "them is driven mad; they give back a victim's wits only if "
            "they themselves are laid to rest.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "dome_of_the_rock",
        "The Dome of the Rock",
        inside=city,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "With the Aqsa Mosque, the greatest of Islam's holy places "
            "in Jerusalem, raised on the old Temple's ground. Its "
            "Dominion aura is 10, and al-Mu'azzam spared the Temple "
            "area when he pulled the city down in 1219.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "aqsa_mosque",
        "The Aqsa Mosque",
        inside=city,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "The great mosque on the Temple ground, beside the Dome of "
            "the Rock; its Dominion aura is 10. The Templars took their "
            "name from the part of this enclosure the kings of "
            "Jerusalem gave them as their first house, in the order's "
            "early days.",
        ),
        **KNOWN_ORDER,
    )
    sepulchre = _add(
        levant,
        "holy_sepulchre",
        "The Church of the Holy Sepulchre",
        inside=city,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "The church over Christ's tomb, in all but name the "
            "Christians' cathedral of Jerusalem, with a Dominion aura of "
            "10; it was spared when the city was razed in 1219. In 1099 "
            "the first Latin patriarch, Arnulf of Chocques, dug a relic "
            "of the True Cross out of the ground in its atrium. The "
            "Crusaders bore it into battle until Salah al-Din took it at "
            "Hattin in 1187, and the Muslims have it still; for a "
            "Christian it holds 7 Faith Points.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "holy_fire",
        "The Holy Fire",
        inside=sepulchre,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "A miracle of every Easter Eve. At noon a holy light breaks "
            "out of the tomb itself and climbs into a pillar of flame, "
            "the sign of the Resurrection, and a priest lights a candle "
            "from it: the Latin patriarch did so while the Latins held "
            "the city, and now the senior priest present does. He "
            "carries the flame out of the tomb and hands it on through "
            "the crowded church while all sing hymns of praise.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "western_wall",
        "The Western Wall",
        inside=city,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "The last of the Temple that stands. Jewish auras have waned "
            "everywhere since the Temple fell (Kabbalah says more), but "
            "here the Jewish Dominion is as strong as it can be: 10.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "hidden_temple",
        "The Hidden Temple of Jerusalem",
        inside=city,
        realm="Divine",
        aura=4,
        levels=[
            levant.b.level(
                "The Temple of Solomon",
                8,
                "Divine",
                notes=paragraphs(
                    "Only the kohanim and rabbis who know the way can "
                    "reach it. The book gives the regio no aura; 8 is "
                    "the pack's choice.",
                ),
            ),
        ],
        summary=paragraphs(
            "Jerusalem's Jews whisper that the Romans never destroyed "
            "the Temple in 70 AD: God hid it from mortal eyes, and it "
            "stands whole in a Divine regio over the city. There it is "
            "still in its glory, of limestone and cedar overlaid with "
            "gold, with its Holy Place (the hekal) and its Holy of "
            "Holies (the debir) among walled courts and outbuildings, "
            "and the two great pillars of cast bronze, Jachin and Boaz, "
            "still keep the door of its porch.",
            "The Ark of the Covenant once stood in the debir and has "
            "been lost since Babylon took the city in 587 BC: hidden, "
            "some say, or carried off. It is a chest of acacia wood "
            "plated in gold, borne on two gilded poles, with two golden "
            "cherubim facing each other on its lid, holding the tablets "
            "of the Law, a golden jar of manna and Aaron's rod. It has 7 "
            "Faith Points for a Jew and 5 for a Christian. Whether it is "
            "in the Hidden Temple the book does not say.",
        ),
        **RUMOURED_LOCALLY,
    )
    _add(
        levant,
        "hattin",
        "The Horns of Hattin",
        inside=syria,
        summary=paragraphs(
            "The hill above the Sea of Galilee where Salah al-Din "
            "destroyed the Latin army in 1187, took the True Cross and "
            "opened the way to Jerusalem. The Order lost as much as the "
            "kingdom: Muslim mages killed Hermetic magi in the battle, "
            "most of Aedes Veritatis's magi died there with their "
            "founder Maryam al-Dimashqiyya, and several Crusader "
            "covenants fell with the strongholds they stood by. The "
            "book gives it no aura.",
        ),
        **KNOWN_TRIBUNAL,
    )


# -- Bilad al-Sham --


def _syria(levant: Levant) -> None:
    syria = levant.places["syria"]
    _add(
        levant,
        "umayyad_mosque",
        "The Great Umayyad Mosque",
        inside=syria,
        realm="Divine",
        aura=6,
        summary=paragraphs(
            "Damascus's great mosque, built where a church stood until "
            "the Muslims took the city in the seventh century and pulled "
            "it down. In its ruins, they say, lay the head of John the "
            "Baptist, Yahya to the Muslims, skin and hair untouched, and "
            "the mosque has kept it since. The head holds 5 Faith "
            "Points, for a Christian or a Muslim alike.",
            "Constantinople and several French towns claim the head "
            "too. The book leaves the troupe to choose: all but one "
            "are fakes; every one is the true head, by a miracle; or "
            "there is one head that can be in many places at once, so "
            "that what befalls it in one is seen in all. None is chosen "
            "here. The book gives the mosque no aura; Divine 6 is the "
            "pack's choice.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "tower_of_serpents",
        "The Tower of the Serpents",
        inside=syria,
        summary=paragraphs(
            "A tower in Aleppo's walls where a talisman is kept, and "
            "while it is there no snake's venom can harm anyone in the "
            "city. How its enchantment works is unknown, and so is "
            "whether it would work anywhere else. A covenant would "
            "covet it, but it would be very hard to steal and harder to "
            "keep once word got out. The book gives no aura and no "
            "level for the talisman.",
        ),
        **KNOWN_REGION,
    )
    _add(
        levant,
        "petra",
        "Petra",
        inside=syria,
        aura=3,
        summary=paragraphs(
            "The old rose-red city in the far south of Bilad al-Sham. A "
            "deep, narrow gorge leads in to a meeting of valleys, where "
            "caves, chambers and buildings were cut and raised over the "
            "centuries, first by the Nabataeans and then by Romans and "
            "Byzantines. The Crusaders were the last to build, a castle "
            "on a hill deep inside, which they left soon after Hattin. "
            "Urbs Rubra, the Tribunal's first covenant, founded in 802, "
            "takes its name from the city.",
            "A community of jinn lives in the huge blocks of stone in "
            "the entrance gorge. They serve and guard the covenant's "
            "two old magi, and have grown so protective of them that "
            "they let no visitor through; some of them are strong "
            "enough that no Hermetic magus has yet forced a way past. "
            "The book gives Petra no aura; Magic 3 is the pack's "
            "choice, as for the covenant.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "syrian_mountains",
        "The Mountains of Northern Syria",
        inside=syria,
        summary=paragraphs(
            "Wild uplands full of jinn strongholds. The greatest of "
            "their jinn is Amirat al-Jabal, the Lady Emir of the "
            "Mountain, a marida fifteen feet tall whom a traveller may "
            "take for a crag; she cares little for mortals and much for "
            "the lesser jinn of the mountains, who look on her as a "
            "grandmother (see the Bestiary). The book gives the "
            "mountains no aura.",
        ),
        **KNOWN_REGION,
    )
    _add(
        levant,
        "lebanon",
        "The Mountains of Lebanon",
        inside=syria,
        summary=paragraphs(
            "The western range above the coast of Tripoli and the "
            "kingdom. The Druze, cast out by the Fatimid mission and "
            "hunted in Cairo after the caliph al-Hakim vanished in "
            "1021, took refuge in these mountains, where they live "
            "still, a secretive people awaiting al-Hakim's return. The "
            "book gives the mountains no aura.",
        ),
        **KNOWN_REGION,
    )
    _add(
        levant,
        "harran",
        "Harran",
        inside=syria,
        summary=paragraphs(
            "An old city of northern Syria, home to the Sabeans, who "
            "keep ancient rites of star-worship; in the first centuries "
            "of Islam they were counted among the peoples of the book. "
            "The book names them as one of the Levant's many magical "
            "traditions without giving them rules, or the city an "
            "aura.",
        ),
        **KNOWN_REGION,
    )
    _add(
        levant,
        "mount_carmel",
        "Mount Carmel",
        inside=levant.places["jerusalem_kingdom"],
        summary=paragraphs(
            "A mountain of the Holy Land above the coast south of Acre, "
            "where a new order of monks, the Carmelites, live on its "
            "slopes under a stern rule the Latin patriarch wrote for "
            "them: few, but noticed. Hermits seek God in the Levant's "
            "wild places too. The book gives the mountain no aura.",
        ),
        **KNOWN_REGION,
    )


# -- Egypt and Sinai --


def _egypt_and_sinai(levant: Levant) -> None:
    b = levant.b
    egypt = levant.places["egypt"]
    giza = _add(
        levant,
        "giza",
        "Giza",
        inside=egypt,
        aura=5,
        levels=[
            b.level(
                "The Temple of Thoth and Anubis",
                6,
                notes=paragraphs(
                    "A hidden temple near the pyramids and the Sphinx, "
                    "where twelve priests and priestesses of Thoth and "
                    "Anubis have kept their gods' worship, little "
                    "troubled, since ancient times: whenever one died, "
                    "a new Gifted soul was drawn to the temple to take "
                    "the empty place. The covenant of the Pyramids (II) "
                    "if the troupe uses it. The book gives the regio no "
                    "aura; 6, as by the great pyramids, is the pack's "
                    "choice.",
                ),
            ),
        ],
        summary=paragraphs(
            "The plateau on the west bank of the Nile across from "
            "Fustat, the greatest of Egypt's ancient monuments. Three "
            "great pyramids, between 70 and 160 yards high and sheathed "
            "in smooth alabaster, stand in a slanting line from "
            "south-west to north-east with lesser pyramids crowded at "
            "their feet; some 450 yards to the east a colossal head "
            "rises 25 feet out of the sand, the Sphinx, buried to its "
            "neck. No one knows who built them or how. Around 820 the "
            "caliph al-Ma'mun had the largest broken into: a long "
            "passage climbs gently to a burial chamber whose walls are "
            "covered with hieroglyphs, and in it his men found only a "
            "sarcophagus with some dry bones. Ayyubid sultans have "
            "carted off stone from the smaller pyramids, but for all "
            "their efforts little of the great ones' casing has come "
            "away.",
            "The whole site has a Magic aura of 5, and 6 close by the "
            "three great pyramids and the Sphinx. Nobody is sure why. "
            "The Bedouin tell of vengeful spirits let loose by al-Ma'mun's "
            "workmen and the sultans' quarrymen, stalking the plateau "
            "for revenge on those who broke into their tombs. Magi come "
            "to it like moths to a lamp, for its secrets and for its "
            "aura, which suits laboratory work, though the strength of "
            "the aura warps those who stay, and the spirits are not "
            "likely to welcome them.",
            "The book offers two covenants here, as alternatives or "
            "both at once: the Pyramids (I), two magi in a tent camp by "
            "the Great Pyramid, and the Pyramids (II), the priesthood in "
            "the regio.",
        ),
        secrets=paragraphs(
            "If the first Pyramids are in play, Ruth and Pariah have "
            "mastered the plateau's wandering spirits and use them to "
            "learn the pyramids' past and to keep intruders away.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "great_pyramids",
        "The Great Pyramids and the Sphinx",
        inside=giza,
        aura=6,
        summary=paragraphs(
            "The ground close about the three great pyramids and the "
            "Sphinx, where Giza's Magic aura rises to 6. The hieroglyphs "
            "on the walls of the largest pyramid's burial chamber have "
            "never been read, and none of the other pyramids has been "
            "opened.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        levant,
        "upper_egypt",
        "Upper Egypt",
        inside=egypt,
        summary=paragraphs(
            "The Nile valley south of Cairo, upstream, where the "
            "naddaha is found most often: an Infernal thing in the shape "
            "of an old woman wrapped in a black milaya, haunting wells "
            "and oases and calling lone travellers close (see the "
            "Bestiary). The book gives the valley no aura.",
        ),
        **KNOWN_REGION,
    )
    _add(
        levant,
        "mount_sinai",
        "Mount Sinai",
        inside=levant.places["sinai"],
        realm="Divine",
        aura=7,
        summary=paragraphs(
            "The mountain deep in southern Sinai where God gave Moses "
            "the Ten Commandments, holy to Muslims, Christians and Jews "
            "alike. At its foot Greek Orthodox monks keep St Catherine's "
            "Monastery, which the emperor Justinian founded in the sixth "
            "century; the monks trace it back to a little chapel the "
            "empress Helena built in the fourth, beside the bush that "
            "burned when God spoke to Moses. It bears St Catherine's "
            "name because Greek monks found her body nearby some three "
            "centuries after she was martyred at Alexandria. The book "
            "gives the mountain no aura; Divine 7 is the pack's choice.",
        ),
        **KNOWN_ORDER,
    )


# -- Lesser Armenia and the north --


def _the_north(levant: Levant) -> None:
    armenia = levant.places["lesser_armenia"]
    _add(
        levant,
        "taurus",
        "The Taurus Mountains",
        inside=armenia,
        summary=paragraphs(
            "The range that walls the Anatolian plateau off from the "
            "south and fills most of Lesser Armenia; its forests give "
            "the kingdom its timber. The covenant of al-Arama sits on a "
            "crag here, trading with the Roman Tribunal. The book gives "
            "the mountains no aura.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        levant,
        "tarsus",
        "Tarsus",
        inside=armenia,
        summary=paragraphs(
            "The royal city of Lesser Armenia, where Leon II was crowned "
            "in the cathedral in 1198 before the papal legate, Conrad of "
            "Mainz. Raymond-Rupen has ruled from it since Antioch was "
            "taken from him, but its people lean towards Leon's cousin "
            "Constantine, and the young king may not keep the throne "
            "long. The book gives it no aura.",
        ),
        **KNOWN_REGION,
    )
    georgia = levant.places.get("georgia")
    _add(
        levant,
        "colchis",
        "Colchis",
        inside=georgia,
        summary=paragraphs(
            "Western Georgia, in ancient times the rich land of Colchis, "
            "where Jason and the Argonauts sailed for the Golden Fleece. "
            "What became of the Fleece after Jason died no one knows. "
            "The book gives it no aura.",
        ),
        **RUMOURED_REGION,
    )


# -- Babel --


def _babel(levant: Levant) -> None:
    _add(
        levant,
        "babel",
        "Babel",
        inside=levant.places.get("iraq"),
        aura=1,
        summary=paragraphs(
            "The ruins of the city where men tried to build a tower to "
            "heaven, some fifty miles south of Baghdad, with a faint "
            "Magic aura of 1. Under them, sealed by a great mass of "
            "rock, is said to be the pit where the fallen angels Harut "
            "and Marut hang upside down by their feet, chained by the "
            "neck and knees. In creation's first days God judged them "
            "lacking in compassion for mankind, gave them human "
            "feelings and sent them down to be tempted; both sinned and, "
            "offered punishment in this life or the next, chose this "
            "one. They taught men magic by God's will, warning each "
            "pupil that it was a temptation.",
            "A great rock does lie at the centre of the ruins, thought "
            "to stop the pit's mouth; no one alive knows if it does. One "
            "man, the tale goes, once got in with a guide and saw the "
            "angels hanging there. He had been told never to say God's "
            "name in their hearing, but at the sight of them it burst "
            "from him, and the angels strained so wildly that their "
            "chains almost gave; he and his guide fled and never came "
            "back.",
        ),
        **KNOWN_REGION,
    )


# -- the towns --


def _towns(levant: Levant) -> None:
    b, p, w = levant.b, levant.places, levant.world

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "acre",
        "Acre",
        paragraphs(
            "The capital of the Kingdom of Jerusalem since Jerusalem "
            "fell in 1187. The Crusaders took it in 1104 and have held it "
            "since, but for the four years Salah al-Din had it, 1187 to "
            "1191. A big, busy port on a sandstone headland, its walls "
            "were pushed out to take in the suburb of Montmusard, which "
            "grew up outside the old Muslim defences, so a double wall "
            "and ditch now cut through the town. Here sit the "
            "government, the Latin church (the patriarch of Jerusalem "
            "rules from here while the holy city is Muslim) and the "
            "military orders, yet Acre's name is bad: courts in the "
            "West have begun to punish criminals by shipping them to "
            "the Holy Land, and many of them are here. Its Dominion "
            "aura hinders magic.",
            "The communes. Settlers who never mixed with the land's "
            "people keep apart as nations: Italians, Spaniards and "
            "Provençals above all, and the three great Italian cities, "
            "Venice, Pisa and Genoa, each as its own. Rewarded with "
            "trading rights for their help in the Crusades, they run "
            "most of the trade with Europe from quarters in the ports, "
            "govern themselves, and answer not to the king but to their "
            "home cities, each through an officer in one of the great "
            "towns; the Venetians' is a bailli general here in Acre. "
            "The law bars commune members from holding fiefs or burgage "
            "land, though some have come by them through marriage or "
            "sale, and the kingdom's lawyers have never settled what to "
            "do about it.",
            "The courts. The Haute Cour judges nobles, and each lord's "
            "court his own vassals; in a town the burgesses take their "
            "quarrels to the Court of Burgesses, the subject peoples to "
            "the Court of the Market (graver cases going up to the "
            "burgesses), and anything to do with ships to the Court of "
            "the Chain; the communes and the church keep courts of "
            "their own. Juries hear most cases, but trial by combat and "
            "by ordeal are used at every level.",
            "Money. The Latins strike a gold besant, worth 20 silver "
            "deniers, 40 silver oboles (half-deniers) or 240 copper "
            "coins; a Mythic Penny is 2 coppers. Byzantine and Muslim "
            "coins never went out of use, European money pours in with "
            "the trade, and barter is old and common. Minting was the "
            "king's alone, but by 1220 some great landholders strike "
            "their own coin.",
        ),
        charter="Noble lord",
        ruler="John of Brienne, regent for Queen Isabel",
        place=p["jerusalem_kingdom"],
    )
    town(
        "tripoli",
        "Tripoli",
        paragraphs(
            "Latin since it fell in 1109 and very strong: it stands on "
            "a peninsula thrust north-west into the sea, water on three "
            "sides and a great wall across the fourth, the south-east. "
            "About 4,000 yards that way a castle on a ridge looks down "
            "on it, built by Raymond of St Gilles when he first "
            "besieged the town in 1102, with gardens and orchards "
            "between; off the peninsula's tip lie four islands, a "
            "Crusader church on the largest. A busy port, if not Acre's "
            "equal, full of Latin and eastern Christians, Muslims and "
            "Jews; Genoa, Venice and Pisa all keep communes here, and "
            "its cloth and wine are much sought.",
        ),
        charter="Noble lord",
        ruler="Bohemond IV of Antioch, count of Tripoli",
        place=p["tripoli_county"],
    )
    town(
        "antioch_city",
        "Antioch",
        paragraphs(
            "On the south bank of the Orontes about twelve miles from "
            "the sea, Christian since the Crusaders took it in 1098. St "
            "Peter founded his first see here, and a Latin patriarch "
            "sits here now. The city fills a plain between the river "
            "and Mount Silpius and climbs the mountain's lower slopes, "
            "the citadel above it all; its walls carry four hundred "
            "towers, so that every stretch is within bowshot of one. "
            "Inside are hundreds of houses and markets, and gardens and "
            "pasture too; the Onopnicles, a stream of the Orontes, cuts "
            "across its north-eastern side. A lively place of trade, "
            "home to Latin and eastern Christians. The Holy Lance was "
            "found here in 1098, and lost again in 1101.",
        ),
        charter="Noble lord",
        ruler="Bohemond IV, prince of Antioch",
        place=p["antioch"],
    )
    town(
        "nicosia",
        "Nicosia",
        paragraphs(
            "Cyprus's capital, sixteen miles inland from Kyrenia, its "
            "nearest port on the north coast, on the Pedheios, a river "
            "that runs dry for part of the year but sometimes floods in "
            "winter. A round stone wall rings it, and in the middle "
            "stands the Latins' great new cathedral of St Sophia, the "
            "archbishop's. It is thriving under the Lusignans and fast "
            "becoming the finest capital of the Latin states, home to "
            "Latins and Greeks.",
        ),
        charter="Noble lord",
        ruler="Henry I of Lusignan, king of Cyprus",
        place=p["cyprus"],
    )
    town(
        "famagusta",
        "Famagusta",
        paragraphs(
            "A flourishing port on Cyprus's east coast, taking over from "
            "Limassol as the island's market because it lies handier "
            "for Lesser Armenia and the Latin coast, so merchants abound "
            "among its Latins, Greeks and Jews, and foreigners besides.",
        ),
        charter="Noble lord",
        ruler="Henry I of Lusignan, king of Cyprus",
        place=p["cyprus"],
    )
    town(
        "cairo",
        "Cairo",
        paragraphs(
            "Two cities growing into one. 'Amr ibn al-'As, who led the "
            "conquest, set his lasting camp of Fustat on the Nile's east "
            "bank; the Fatimids founded their new capital, al-Qahira, "
            "the Victorious, to its north in 969, and the two together "
            "now go by that name. Salah al-Din's citadel was the first "
            "great building outside the Fatimid walls, and Giza and "
            "Rawda island are favoured places to live. The Ayyubids' "
            "chief seat, it is hard to attack and commands the goods "
            "moving along the Nile to the coast, so trade and tolls "
            "make it rich. It is Egypt's heart in learning and faith "
            "as well: Salah al-Din, ending the Fatimid caliphate, "
            "founded houses to teach Sunni Islam, and as his first "
            "capital it grew a strong class of officials. Christians and "
            "Jews live here with the Muslims.",
        ),
        charter="Noble lord",
        ruler="Sultan al-Kamil",
        place=p["egypt"],
    )
    town(
        "alexandria",
        "Alexandria",
        paragraphs(
            "Alexander's city, outshone by Cairo now in Egypt's life but "
            "still one of the world's great markets, a match for the "
            "Italian cities. Barges bring down the goods of the interior "
            "from Cairo; it sells spices, sugar and cotton abroad and "
            "buys olive oil, dyes, gems, weapons and the wares of the "
            "East. Its yards once built the fleets with which the "
            "Muslims took Cyprus. The Pharos, its famous lighthouse, has "
            "a mosque in its ground floor and still guides ships with "
            "the rest. A great library stood here once, said to have "
            "held 500,000 books, which the book has the Romans destroy "
            "early in the first century. St Catherine was martyred "
            "here.",
        ),
        charter="Noble lord",
        ruler="Sultan al-Kamil, through his governor",
        place=p["egypt"],
    )
    town(
        "damietta",
        "Damietta",
        paragraphs(
            "A city in upheaval. The Crusaders sacked it in 1219 so "
            "savagely that Francis of Assisi, who had come with them, "
            "judged them more greedy than good and went home to Italy. "
            "It is in Latin hands now, its garrison living well and "
            "Latin settlers building homes at the expense of the Muslim "
            "natives, who bear it more calmly than Latins have borne "
            "the same, trusting that all will come right, though they "
            "dread another long siege so soon after the last. The "
            "Muslim armies, their offer of peace (the True Cross's "
            "return among its terms) refused, are slowly fighting their "
            "way back towards it.",
            "The sack has left the city's Dominion aura very weak: "
            "Divine 1 by day, and nothing at all at night. The young "
            "covenant of the True Cross was founded here after the "
            "conquest.",
        ),
        charter="Noble lord",
        ruler="The Crusade's leaders (the legate Pelagius claims it)",
        place=p["egypt"],
    )
    town(
        "jerusalem",
        "Jerusalem",
        paragraphs(
            "Muslim for four centuries before the Crusade: taken from "
            "the Byzantines in 638 and held by Sunni rulers until the "
            "Fatimids' reach grew in the tenth century. From 1071 the "
            "Fatimids and a Turkish chief, Atsiz ibn Uvak, fought over "
            "it for seven years; the Seljuks took it in 1078, the "
            "Fatimids took it back some twenty years on, and a year "
            "later, in 1099, the Crusaders stormed it. It was Latin "
            "until Salah al-Din won it in 1187, and the Ayyubids hold it "
            "still.",
            "It is in a sorry state. In 1219 al-Mu'azzam of Damascus, "
            "afraid he might have to hand it back to the Crusaders, had "
            "it torn down, all but the Temple ground, the Church of the "
            "Holy Sepulchre and the citadel; many houses stand empty, "
            "their Muslim owners gone east ahead of the Crusaders they "
            "expect. Muslims, Jews and eastern Christians still live "
            "here. In peacetime pilgrims of all three faiths come from "
            "the West, and the Muslims have never barred them, but with "
            "war in the Nile delta and the walls down, few come now.",
        ),
        charter="Noble lord",
        ruler="Al-Mu'azzam of Damascus",
        place=p["holy_city"],
    )
    town(
        "damascus",
        "Damascus",
        paragraphs(
            "On the desert's edge at the foot of the Anti-Lebanon, "
            "taken from the Byzantines in 635 and the Umayyad caliphs' "
            "capital until they fell in 750, when the capital moved to "
            "Baghdad and Damascus sank to a province under governors. "
            "The Fatimids held it from 970 to 1076, Turkish dynasties "
            "after them, and from 1176 Salah al-Din and his heirs; "
            "al-Mu'azzam rules it now. It flourished under Nur al-Din "
            "and has gone on flourishing: a busy market that even "
            "Italian merchants visit in quieter years, famed for silk "
            "brocade, copperware, glass and tanned lambskins, with a "
            "lively life of scholars and writers, many religious houses "
            "founded by the Ayyubids, and able officials. Against the "
            "Latins its walls have been made stronger and its citadel "
            "rebuilt.",
            "Aedes Veritatis stands on a mountain a few miles east and "
            "sells its quarry stone here, which the quaesitores have "
            "ruled lawful.",
        ),
        charter="Noble lord",
        ruler="Al-Mu'azzam",
        place=p["syria"],
    )
    town(
        "aleppo",
        "Aleppo",
        paragraphs(
            "On the little river Quwayq at the north-western tip of the "
            "Syrian desert, in the middle of a wide chalk plain. The "
            "Muslims took it from the Byzantines in 636 and built a "
            "great mosque; for much of the time since it was a frontier "
            "town facing Byzantium, fought over often, though mostly "
            "governed in the Baghdad caliph's name. 'Imad al-Din Zangi, "
            "who would destroy the Latin County of Edessa in 1144, took "
            "it in 1128, and under his son Nur al-Din it bloomed with "
            "colleges, convents and a hospital. Salah al-Din had it in "
            "1183; his grandson al-'Aziz rules it now.",
            "Salah al-Din's heirs have done well by it: walls repaired, "
            "citadel rebuilt, new suburbs for Turkish soldiers, canals "
            "mended to reach the whole city, more religious houses, "
            "bigger markets, and trade with the Venetians when there is "
            "peace. Its farmers grow wheat, cotton, olives, figs, vines "
            "and pistachios above all, its herdsmen raise sheep, and it "
            "is known for its cloth and soap. In one of its wall towers "
            "a talisman keeps the city safe from snakes.",
        ),
        charter="Noble lord",
        ruler="Al-'Aziz",
        place=p["syria"],
    )
    town(
        "konya",
        "Konya",
        paragraphs(
            "The Seljuk sultans' capital since the Crusaders took "
            "Nicaea from them in 1097. Once a Byzantine military post "
            "that the first Muslim conquests passed by, it fell to the "
            "Seljuks in the eleventh century. Unlike the country round "
            "it, it is well watered, so it is a centre of farming as "
            "well as of rule. It only truly rose after 1118, when "
            "Rukn al-Din Mas'ud I raised a mosque there, and more "
            "mosques, colleges, markets and walls followed. Greeks, "
            "Armenians and Jews live among the Turks, scattered through "
            "the town rather than in quarters of their own, and a "
            "house's size and height show its owner's rank.",
            "The book has 'Izz al-Din Kay Kawus ruling here; he dies "
            "this year, 1220, and his brother 'Ala al-Din Kayqubad "
            "succeeds him.",
        ),
        charter="Noble lord",
        ruler="Sultan Kayqubad I",
        place=p["asia_minor"],
    )


# -- after every part has built --

#: Each town's liege, by the key its lord's part keeps it under.
LIEGES: tuple[tuple[str, str], ...] = (
    ("acre", "jerusalem_king"),
    ("tripoli", "tripoli_count"),
    ("antioch_city", "antioch_prince"),
    ("nicosia", "cyprus_king"),
    ("famagusta", "cyprus_king"),
    ("cairo", "al_kamil"),
    ("alexandria", "al_kamil"),
    ("jerusalem", "al_muazzam"),
    ("damascus", "al_muazzam"),
    ("aleppo", "al_aziz"),
    ("konya", "sultan_of_rum"),
)

#: What the book says of the whole land that no one record holds,
#: appended to the Levant's summary (L19, L21, L28).
REGION_NOTES = paragraphs(
    "Faith. Sunni Islam is the faith of the rulers and of most of the "
    "people. Its law is taught by four schools, each named for its "
    "founder: the Hanafis (Abu Hanifa), the Malikis (Malik ibn Anas), "
    "the Shafi'is (al-Shafi'i) and the Hanbalis (Ahmad ibn Hanbal). They "
    "read the Qur'an and the hadith a little differently and so part on "
    "points of law; the Hanafis, for one, forbid only wine pressed from "
    "grapes, and all four argue over beer. The Shi'is of the land and "
    "the eastern churches have records of their own.",
    "The Sufis, Islam's mystics, take their name from their plain "
    "woollen dress. Their way goes back to al-Junayd and al-Hallaj, "
    "whom the authorities put to death for saying he was God made "
    "flesh; Ibn 'Arabi is its liveliest thinker now. Lately they have "
    "formed brotherhoods, the tariqas, each under a shaykh at a convent "
    "or a saint's tomb, and seek God through piety and through dhikr, "
    "chanting God's names, and sama', listening to holy music and "
    "verse. Once suspected of heresy, they are now thought a force for "
    "piety, and rulers build them zawiyas, khanqahs and ribats, which "
    "also let them keep an eye on the brotherhoods.",
    "The dhimmis. Christians and Jews, as peoples of a scripture, may "
    "live under Muslim rule if they accept the pact of protection: "
    "they pay a poll tax, the jizya, rarely more than a dinar a year, "
    "may not bear arms, ride horses or build new houses of worship, "
    "count for less as witnesses, and sometimes must dress apart. How "
    "strictly this is kept varies with the times. The Latin states "
    "treat their Muslim, Jewish and eastern Christian subjects in "
    "much the same way, and some Latin lords hold them little better "
    "than serfs. Hermetic magi stand outside both orders.",
    "Auras. The book's Dominion is the Divine realm, and Islamic, "
    "Christian and Jewish auras are all of it: where more than one "
    "covers a place, the strongest holds, and the faithful of each "
    "religion may draw on the others'. Realms of Power: The Divine's "
    "guidance on how strong a Dominion aura is replaces the book's "
    "table of Islamic auras by kind of place, which is optional "
    "flavour, and the Islamic Temper the book borrows from Pax Dei is "
    "simply the Dominion as that book describes it. The book takes all "
    "three faiths to be true, as Realms of Power: The Divine does; it "
    "names two other ways to play it, none chosen here: God is Law, "
    "where Islam alone is right and Christians and Jews must accept "
    "Muslim rule to be saved, and God is Love, where Christ's church is "
    "right, virtuous Muslims may still be saved, and Muslim auras are "
    "weaker or gone.",
    "Foreigners. An optional rule of the book's: in place of the "
    "Outsider Flaw for every visitor, a foreigner in the Latin states "
    "takes from -5 to +5 on social rolls, as the storyguide judges the "
    "state of relations between his people and the land he is in, "
    "how much his listener cares, and how plainly foreign he looks. "
    "The Definitive Edition's Outsider Flaw still applies to a "
    "character who takes it.",
    "The jinn among men. Pious jinn and corrupt ones like to live near "
    "people, the first to share in their worship and the second to "
    "lead them astray, so they make their homes in regiones at or "
    "close to wells, crossroads and rivers; a storyguide may set one "
    "at any such place. Heathen jinn keep to the deep wilderness. "
    "Their homelands are the Mountains of Qaf and Jinnistan.",
    "Beings named without stats who wander the whole land: Cain, "
    "cursed to roam without a home since he killed Abel, his city of "
    "Enoch long lost; and perhaps a few of the nephelim, the giant "
    "children of fallen angels and mortal women, who destroyed one "
    "another at Gabriel's urging, unless some survived, repentant or "
    "worse. Rukhkhs with wings thirty paces across, sphinxes, dragons "
    "and lesser serpents are in The Medieval Bestiary.",
    "Money. The Latins' gold besant is worth 20 silver deniers, 40 "
    "oboles or 240 coppers, and a Mythic Penny is 2 coppers (Acre's "
    "record says more). The Muslims strike the gold dinar, the silver "
    "dirham and the copper fals; their rates swing, but the book "
    "reckons a dinar at 20 dirhams and a dirham at 36 fals. Between "
    "the two, a besant passes for a dinar and a denier for a dirham, "
    "and a Mythic Penny is worth about 6 fals. Venice, Pisa and Genoa "
    "keep communes of their own in the Latin ports, trading under "
    "privileges won for their help in the Crusades.",
)


def finish(levant: Levant) -> None:
    region = levant.places["levant"]
    region.summary = paragraphs(region.summary, REGION_NOTES)

    # The shared pit of Harut and Marut lies under the ruins of Babel,
    # which is inside Iraq where the shared record puts it.
    pit, babel = levant.places.get("harut_and_marut"), levant.places["babel"]
    iraq = levant.places.get("iraq")
    if pit is not None and pit.place_id in (None, iraq.id if iraq else None):
        pit.place_id = babel.id

    for town, lord in LIEGES:
        record, liege = levant.world.get(town), levant.find(lord)
        if record is not None and liege is not None and record.answers_to is None:
            record.answers_to = liege.id
