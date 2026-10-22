"""Arabia (TC&TC ch06), in paraphrase.

Places (C10, C16; the book's Dominion is Divine, a haram 3 and a city 4
where unnumbered, an unnumbered Magic pocket 3): the region
places["arabia"] (no `inside`), holding the pagan gods, the 'ashira,
the Bedouin and their beasts and Moamyn's falconry (C18: the book has
no holder); its provinces places["hijaz"], ["najd"] (with Yamama),
["bahrayn"], ["empty_quarter"] (Magic 10, its bright regiones as a
level, the way into the Twilight Void, suggested vis), ["yemen"] (with
'Asir), ["hadramawt"] (frankincense and myrrh) and ["uman"]. Inside
them: places["mecca_sanctuary"] (the five-mile haram, Divine 3; the
town of Mecca sits in it), ["mecca_haram"] (the Haram Mosque, Divine
10, Divine Might 100, the Ka'ba a regio level 10, the Black Stone),
["zamzam"] (the well, its water's vis, the marid under secrets=),
["mosque_of_the_jinn"] (Faerie 5, 4 when the jinn are not at prayer),
["medina_haram"] (Divine 3; the town of Medina sits in it), ["ukaz"]
(the poets' fair), ["al_qudayd"] (al-Manat's lost sanctuary),
["lukman_nest"] (a Magic regio, Lukman's falcons), ["stone_lovers"]
(Aja and Salma, suggested vis), ["abqar"] (the Valley of 'Abqar, a
Faerie regio), ["marib"] (Magic 3, a candidate covenant site) and in
it ["ghumdam"] (Magic 6), ["ubar"] (Iram of the Pillars, Magic 5),
["trees_that_cry_blood"] (Rego Terram vis) and ["hajar_ghosts"] (the
haunted shores of the Gulf).

Towns (world[...]): world["mecca"], ["medina"], ["taif"], ["sanaa"],
["muscat"], ["nizwa"], ["hajar"], ["tayma"] and ["khaybar"] (C13:
Jewish towns ruling themselves). order.py puts the houses of wisdom of
Sana'a, Muscat and Nizwa in world["sanaa"], ["muscat"] and ["nizwa"].

Lords (C13; the lord form's title left blank, the real title in the
name and summary): world["al_masud"] (the Ayyubid sultan of Yemen, at
Sana'a), ["sharif"] (the Grand Sharif Qatada of Mecca, answering to
east.py's al-Kamil, his death this year "if history holds" in the
summary), ["uyunids"] (Bahrayn), ["nabhanids"] (at Nizwa) and
["yahmad"] (Muscat). The Hijaz is linked to east.py's world["al_kamil"],
its overlord in name; al-Kamil's record is not changed.

Factions (C15, C12 as revised): world["bedouin_sahirs"] and
["muruwa"] (tradition "trad_bedouin_hakima"), ["daughters_cult"] (the
Cult of the Daughters of Allah at Ta'if, its three members in the
summary: no characters), ["witches_of_nizwa"] (no tradition record)
and ["jurhumites"] (the jann-blooded tribe that once held Mecca).

Beings named without stats (al-Khalil, the marid of Zamzam, Lukman's
falcons, the Jadis and Tasm, the pagan gods) are sentences in their
places; creatures with stats (the zawba'a, the nisnas, the giant of
'Ad, the flying serpent) are bestiary.py's. Vis (C17): Zamzam's water
and the Trees That Cry Blood are lines in their places' summaries; the
Empty Quarter and the Stone Lovers, given vis but no source, carry
"Suggested vis sources (not in the book)". The story seeds are
stories.py's, hung on these keys."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs

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


def build(cradle: Cradle) -> None:
    _regions(cradle)
    _holy_cities(cradle)
    _hijaz(cradle)
    _south(cradle)
    _east(cradle)
    _lords(cradle)
    _towns(cradle)
    _factions(cradle)


def finish(cradle: Cradle) -> None:
    """Link the Hijaz to its overlord in name, east.py's al-Kamil."""
    al_kamil = cradle.world.get("al_kamil")
    if al_kamil is not None:
        cradle.b.link(
            cradle.places["hijaz"], "places", al_kamil, "Its overlord, in name"
        )


# -- the region and its provinces --


def _regions(cradle: Cradle) -> None:
    arabia = _place(
        cradle,
        "arabia",
        "Arabia",
        summary=paragraphs(
            "The peninsula where Islam began, holding its two holy "
            "cities, Mecca and Medina, which every Muslim should visit "
            "on the hajj once in a lifetime if he can. It is not all "
            "sand: stony desert fills the north, mountains run behind "
            "most of the coasts with thin, fertile plains below them, a "
            "high plateau in the east (the Najd and Yamama) has green "
            "valleys of crops, sheep and goats, and in the south the "
            "hills of Yemen and Hadramawt are wooded, well watered and "
            "rich in incense trees, the Romans' Happy Arabia. The old "
            "incense road through the deserts is gone; its trade now "
            "goes by ship round the coasts. Three great deserts lie "
            "within: the Nefud in the north, the Empty Quarter in the "
            "south and the Dahna between them, with burning sun, short "
            "water, dry quicksands, sandstorms, brigands and the jinn "
            "who conjure false oases for the thirsty.",
            "Its people are townsfolk round the oases, mostly farmers, "
            "and Bedouin herders who trade with them, guide and guard "
            "the caravans and pilgrims, and now and then quarrel with "
            "them. Most are Muslims of one kind or another, with many "
            "Christians and Jews among them. Local dynasties rule the "
            "settled lands and most honour the 'Abbasid caliph in "
            "name; the Ayyubids, Salah al-Din's family, share the Hijaz, "
            "'Asir and Yemen.",
            "Beneath the sands lie buried cities, across the land holy "
            "shrines, and in the ruins jinn and stranger beings, some "
            "of whom live openly in the towns. The Bedouin treat "
            "date-palms, rocks carved by the wind and precious wells "
            "almost as gods: many such places are home to an 'ashira, "
            "a 'close friend' spirit appeased with gifts, and are where "
            "auras and elemental vis are found. The strongest 'ashira "
            "are Magic jinn, genii loci who were the gods of the "
            "Ignorance before Islam, or Infernal jinn who have taken "
            "their places: Abgal of the camel-drivers, Dhu'l-Khalasa of "
            "oracles, Dhu Shara of the mountains, Hubal of the moon and "
            "divination, Ishtar, Manaf whom women worshipped, Nakhla of "
            "the date-palm, al-Qawm of war, night and caravans, Sa'd, "
            "Wadd and Yaghuth. One name may cover several spirits a few "
            "miles apart, of different realms and power, from little "
            "elementals of Might under 10 to the spirits of great lonely "
            "landmarks near 50.",
            "The Bedouin prize the camel above every beast, then their "
            "Arabian horses, saluqi hounds and falcons, and their "
            "falconry, al-Qanas, puts food on the winter fire more than "
            "it entertains. Their birds are the enduring saqr and the "
            "swift shahin. The Arabian phoenix, the anqa, red, orange "
            "and gold, flies to its eyrie above the Mountains of Qaf "
            "when it grows old, burns and is reborn as a black egg; a "
            "magus who watches this for a season may count it as a "
            "significatos in Animal, Ignem or Vim.",
            "Falconry's great authority is an untitled Arabic book by "
            "the falconer Moamyn, which no house in the book is named "
            "as holding: a summa on Animal Handling (falconry), level 4, "
            "Quality 7, with a tractatus on Hunt (hawking), Quality 7. "
            "Master Theodore of Antioch will put it into Latin for "
            "Frederick II within the decade (Quality 6), and by 1250 the "
            "emperor's own corrected and glossed version, De arte "
            "venandi cum avibus, reaches Quality 8.",
            "Kohl, the black or blue eye powder women wear across the "
            "Middle East, is said to come from the jinn, and the hidden "
            "folk sell it in the bazaars of Golden Baghdad for prices "
            "seldom paid in coin. The commonest magical kohl, a Bedouin "
            "folk witch's brew, grants Second Sight for a day; other "
            "kinds give Keen Vision, Magic Sensitivity, Piercing Gaze "
            "or Wilderness Sense at a score of 2 or 3. As a material it "
            "gives +3 to affect sight; its base is burnt frankincense.",
        ),
    )
    _place(
        cradle,
        "hijaz",
        "The Hijaz",
        inside=arabia,
        summary=paragraphs(
            "The holy land of Islam on the Red Sea coast, home to Mecca "
            "and Medina, with more traffic than all the rest of Arabia: "
            "pilgrims above all, and ships putting into its many "
            "harbours on the run between Egypt and the Indian Ocean. "
            "The sultan of Egypt holds it in name.",
            "Sahirs are few here, and live far from the great cities: "
            "the thick Divine auras and regiones make magic hard, and "
            "wizards of every kind, Gifted or not, keep out of the "
            "religious authorities' sight. Infernal jinn crowd the "
            "pilgrim roads, planting doubt and impious thoughts.",
            "Non-Muslims may not enter the harams, the sacred ground "
            "reaching some five miles round each holy city. The book "
            "offers a troupe four ways round this: going in disguised "
            "or hidden by magic (a grave sacrilege if caught, with the "
            "high auras against any spell), sending only the Muslim "
            "characters, a special arrangement under local escort, or "
            "simply letting non-Muslims into the mythic cities. Either "
            "way a visit should be a deeply religious experience. Each "
            "haram has a Divine aura of 3, with the Calm trait at +3 "
            "unless noted, and the cities 4 or more; fighting and "
            "killing are forbidden there, save for slaughtering animals "
            "for food or putting down savage or sick ones, and God has "
            "been known to strike down the impious with Ignis Domini, "
            "the Smiting of the Lord, or by swallowing them alive.",
            "The hajj, one of the five pillars, is set out in Realms of "
            "Power: The Divine. A Muslim who completes it gains Pious +3 "
            "and 3 Faith Points; going again can restore them, but never "
            "takes the trait past +3.",
        ),
    )
    _place(
        cradle,
        "najd",
        "The Najd and Yamama",
        inside=arabia,
        summary=paragraphs(
            "A high plateau tilting down from west to east. Yamama is "
            "thick with oases and farming villages; the Najd is rockier "
            "and more mountainous, its villages in valleys that catch "
            "the rain's run-off. Most of the people are Bedouin, though "
            "some towns are big. The Jadis and the Tasm, two old tribes "
            "of faerie jinn, still roam here, known for their "
            "strange wares, their spotless honour and the most wonderful "
            "hospitality anywhere.",
            "Yamama tells of Zarqa al-Yamama, a blue-eyed witch of the "
            "days of Tasm and Jadis who could see a rider thirty miles "
            "off. A king of Yemen who conquered the land killed her and "
            "had his physicians cut out her eyes for the secret; they "
            "found them smudged with kohl.",
            "In the north the Jews of Tayma' and Khaybar keep their own towns.",
        ),
    )
    _place(
        cradle,
        "bahrayn",
        "Bahrayn",
        inside=arabia,
        summary=paragraphs(
            "The eastern coast of Arabia and the islands off it. From "
            "899 to 1076 it was held by the Qarmatians, Isma'ili Shi'is "
            "who in 930 sacked Mecca and Medina and carried off the "
            "Black Stone of the Ka'ba. It came back in 951, left in a "
            "sack in the great mosque of Kufa with a note saying that it "
            "had been taken, and was now returned, on command; most "
            "credit the Fatimids of North Africa with talking the "
            "Qarmatians round, but no one knows. The stone came home "
            "broken in seven. The Sunni Uyunids drove the Qarmatians "
            "out and rule in 1220, though some Qarmatians still live "
            "here.",
            "The busy markets round the fortress of al-Mushaqqar, with "
            "good wages and cheap wine, are where the jann guide Jumayl "
            "likes best to be found.",
        ),
    )
    _place(
        cradle,
        "empty_quarter",
        "The Empty Quarter",
        inside=arabia,
        aura=10,
        levels=[
            Builder.level(
                "The bright sands",
                10,
                see="Shining, featureless sand where the dunes should be.",
                enter="Only unawares, but with frightening ease: +6 to the "
                "roll to enter.",
                notes="Many pockets lie within the Quarter, traps for the "
                "careless. Leaving one is hard: -3 to the roll, so those "
                "without Second Sight, Magic Sensitivity or some such power "
                "may never find the way out.",
            )
        ],
        summary=paragraphs(
            "Rub' al-Khali, the trackless desert dividing north from "
            "south Arabia. No caravan has crossed it since the kingdom "
            "of 'Ad fell in the third century and its frankincense trade "
            "with it, and even the Bedouin keep to its edges. Some miles "
            "past the last settlements the dunes rise a thousand feet, "
            "and beyond them the traveller is in the realm of al-Khalil, "
            "'the Empty One', a mighty elemental jinni, a Magic daimon "
            "and genius loci, said to guard the lost lands of the times "
            "before Islam.",
            "Few Magic auras in the Middle East are as vast or as "
            "strong: past the great dunes it climbs quickly to 10, "
            "lower only at the fringes, and the land dissolves into "
            "shifting brightness, full of regiones of blank sand. Some "
            "travellers pass straight into the Twilight Void without "
            "noticing any regio, most often near the edge of the "
            "provinces of Auram, Imaginem or Terram; some tell of the "
            "ghosts of old cities or wandering tribes, or of provinces "
            "of other Forms. Some old magical disaster, and a power of "
            "ritual strength of al-Khalil's, seem to have made the way "
            "so easy, and the empty land echoes the emptiness of the "
            "Void.",
            "Local sahirs, and the few magi who know of it, call it the "
            "Valuable Quarter: great stores of vis and of the Magic "
            "Realm's riches lie within reach of any wizard, though "
            "getting back out is far harder than going in, and those "
            "who return often come back Warped; a few mundane folk have "
            "come home knowing Sihr and a Solomonic art, and are never "
            "quite trusted by other sahirs. Criamon magi wonder whether "
            "it hides a way into the Counter-Cyclical Alam, Merinita "
            "magi whether it rings a hidden gate to Arcadia where the "
            "old gods of Arabia lie trapped. Some sahirs think Al-Hajjaj "
            "and Al-Zill of the First Council vanished into it, and will "
            "return like King Baluqiya.",
            "Suggested vis sources (not in the book), for the storyguide "
            "to use, change or ignore: glassy tears of fused sand on "
            "the crests of the great dunes after a lightning storm, 4 "
            "pawns of Terram a year; the whistling wind at the Quarter's "
            "edge at dawn, caught in a sealed jar, 3 pawns of Auram a "
            "year; the shimmer over the bright sands, gathered as a "
            "mirage-glass, 3 pawns of Imaginem a year.",
        ),
    )
    _place(
        cradle,
        "yemen",
        "'Asir and Yemen",
        inside=arabia,
        summary=paragraphs(
            "The south-west of the peninsula, under the Ayyubid sultan "
            "of Yemen. Most of its people are Sunnis or Zaydi Shi'is, "
            "with scattered Tayyibis, Isma'ilis of the Fatimid line "
            "who await a hidden line of imams. The Tayyibis are great "
            "traders and keep up dealings with Soqotra to the south, "
            "an island of non-Hermetic sorcerers described in Rival "
            "Magic, and Yemeni seafarers are pushing into the old "
            "Ethiopian lands of Africa and across the sea to al-Sind.",
        ),
    )
    _place(
        cradle,
        "hadramawt",
        "Hadramawt",
        inside=arabia,
        summary=paragraphs(
            "A backwater of the Muslim world: dry, thinly peopled "
            "valleys, and hills sometimes thickly wooded but too steep "
            "to farm or coppice. Few pilgrims or strangers come so far "
            "south, and the locals are startled to meet one. It is known "
            "only for the nisnas, a half-man of its forests whose flesh "
            "the people find sweet, and as the source of much of the "
            "incense and spice carried up the coast to Europe. Its "
            "remoteness, its wild magic and its little-known Magic jinn "
            "make it a possible first home for Hermetic settlers, if "
            "they can find magical answers to its poverty and distance.",
            "Frankincense and myrrh come from twisted trees on its "
            "foggy mountains, with groves too in 'Uman, Ethiopia and "
            "Soqotra. Harvesters cut the bark and wait three months for "
            "the sap to harden into tears, worth more than their weight "
            "in gold. White flying serpents, the syrenii or iaculii, "
            "guard the trees and are driven off with the smoke of "
            "storax brought from Anatolia. Frankincense, olibanum, pale "
            "yellow tinged with green, quickens the blood: as a "
            "material it gives +3 to medicine and +5 to promote life. "
            "Myrrh, reddish brown, darker and clearer the better it is, "
            "flavours wine and goes into embalming and the Orthodox holy "
            "oil: +3 to ease arthritis or inflammation, +5 to preserve, "
            "+2 to sanctify.",
        ),
    )
    _place(
        cradle,
        "uman",
        "'Uman",
        inside=arabia,
        summary=paragraphs(
            "The eastern tip of the peninsula: hot, dry desert inside, "
            "cooler and fertile coastal mountains and plains where crops "
            "grow, and ports through which Arabia trades with the Indian "
            "Ocean. Most of its people are Ibadis. The last giants of "
            "'Ad live in Magic regiones deep in its deserts, and weaken "
            "if they stay too long outside their strong auras; now and "
            "then one comes out to build for a sorcerer or emir in "
            "return for some secret of eternal life.",
        ),
    )


# -- Mecca and Medina --


def _holy_cities(cradle: Cradle) -> None:
    hijaz = cradle.places["hijaz"]
    sanctuary = _place(
        cradle,
        "mecca_sanctuary",
        "The Haram of Mecca",
        inside=hijaz,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The sacred ground reaching about five miles out from Mecca, "
            "closed to non-Muslims, where no blood may be shed. Its "
            "Divine aura is 3, with Calm at +3; inside the city itself "
            "every aura is a point higher than it would be elsewhere, "
            "so 5 in its streets. God's favour shows plainly: the "
            "weather is gentle beyond nature, plants grow lush but never "
            "run wild, and peace hangs over the streets.",
        ),
    )
    haram = _place(
        cradle,
        "mecca_haram",
        "The Haram Mosque",
        inside=sanctuary,
        realm="Divine",
        aura=10,
        levels=[
            Builder.level(
                "The Ka'ba within",
                10,
                "Divine",
                see="A still richer Ka'ba, which holds more worshippers "
                "than the shrine could.",
                enter="Pious Muslims who go in on the days it is opened "
                "to all, most Mondays and Fridays.",
                notes="Here, as at the spot near the south-west wall where "
                "the Prophet prayed, a crowd may all pray in the same place "
                "without jostling.",
            )
        ],
        summary=paragraphs(
            "The holiest of mosques, at the heart of Mecca: a great "
            "courtyard ringed by richly decorated halls of many rows of "
            "columns, with twenty gates and seven minarets. Off its "
            "north-west hall is the Dar al-Nadwa, where the scholars "
            "take counsel with the Grand Sharif; off the south-west "
            "hall the house of the Maliki scholars. Its Divine aura is "
            "10, overwhelming; a Muslim may invoke baraka here for any "
            "of the Saint Powers of Realms of Power: The Divine, and the "
            "site counts as Divine Might 100 where that matters.",
            "In the courtyard stands the Ka'ba, which Adam built under "
            "the angels' guidance and Abraham and Ishmael rebuilt: a cube "
            "of about forty feet a side and forty-six high, its upper "
            "walls hung with the green kiswa. In its eastern corner, "
            "five feet up, is set the Black Stone, which fell from Heaven "
            "to mark the spot for Adam and Eve, white once and "
            "blackened by the sins it has soaked up; pilgrims touch or "
            "kiss it to be forgiven. Since the Qarmatians stole it, it "
            "has been seven pieces held in a silver band. A door seven "
            "feet up the north-east wall, reached by wheeled wooden "
            "steps, opens on marble of many colours, three pillars, a "
            "stair to the roof, old and precious Qur'ans and the records "
            "of those who restored the shrine. Muslims may seek baraka "
            "from the Prophet inside the Ka'ba and just outside it.",
            "About twenty yards east of the Ka'ba, under a marble dome, "
            "is the Well of Zamzam.",
        ),
    )
    _place(
        cradle,
        "zamzam",
        "The Well of Zamzam",
        inside=haram,
        realm="Divine",
        aura=10,
        summary=paragraphs(
            "The spring God showed to Hajar, Ibrahim's wife, when she "
            "searched for water for her thirsty son Ishmael, older than "
            "any building of Mecca. Its water is clean and pure, and "
            "pilgrims drink it as an act of devotion, but most of the "
            "year it has no power.",
            "Vis: on the night after Ramadan ends the Divine aura over "
            "the well sinks a little, and its water, drawn by moonlight, "
            "is an unusual Extraordinary Aquam vis: each mouthful "
            "restores all of a character's lost Fatigue levels by an "
            "unknown non-Hermetic effect of ritual strength. The book "
            "gives no number of pawns.",
        ),
        secrets=paragraphs(
            "Zamzam is also a name: an ancient Magic marid lies trapped "
            "in a smothered Magic regio at the bottom of the well, its "
            "powers crushed by the Divine aura. What strength it keeps "
            "goes into keeping the water so pure, and it has come to "
            "hate its prison. It remembers far back, and knows things "
            "of the past no other source can tell.",
        ),
    )
    _place(
        cradle,
        "mosque_of_the_jinn",
        "The Mosque of the Jinn",
        inside=sanctuary,
        realm="Faerie",
        aura=5,
        summary=paragraphs(
            "On Mecca's northern edge lies al-Ma'la, the cemetery of "
            "many of the Prophet's kin and companions, his mother Amina, "
            "his first wife Khadija and his grandfather 'Abd al-Muttalib "
            "among them. Beside it is the mosque where a band of jinn "
            "heard the Prophet recite the Qur'an and took Islam.",
            "It has become the jinn's own centre of worship. At the "
            "hours of prayer, and above all at Friday noon, it teems "
            "with faerie jinn of every shape and size, and even its "
            "officials are jinn who do not trouble to disguise "
            "themselves. By an unspoken rule they take no shape too "
            "monstrous or too big for the room. A few humans pray here "
            "too, sahirs and other wizards among them, and respectful "
            "mortals are always made welcome, sometimes a little too "
            "warmly. The jinn draw their vitality from human worship "
            "beside them, not from any aura of the Divine.",
            "Its Faerie aura is 4, and 5 while the jinn are at prayer.",
        ),
    )
    _place(
        cradle,
        "medina_haram",
        "The Haram of Medina",
        inside=hijaz,
        realm="Divine",
        aura=3,
        summary=paragraphs(
            "The sacred ground about five miles round Medina, closed to "
            "non-Muslims, where no blood may be shed: Divine 3, with "
            "Calm at +3. As at Mecca, every aura inside the city is a "
            "point higher than elsewhere, so 5 in its streets, and the "
            "city is full of mosques, shrines and places of the "
            "Prophet's life. Old lava fields, long cooled, ring the "
            "plain.",
        ),
    )


# -- the rest of the Hijaz and the Najd --


def _hijaz(cradle: Cradle) -> None:
    hijaz, najd = cradle.places["hijaz"], cradle.places["najd"]
    _place(
        cradle,
        "ukaz",
        "'Ukaz",
        inside=hijaz,
        summary=paragraphs(
            "A small oasis town halfway between Mecca and Medina, whose "
            "yearly poetry contest goes back to the Ignorance: the seven "
            "Suspended Odes, the Mu'allaqat, that now hang on the Ka'ba "
            "were first heard at its fair. Each year a different tribe "
            "of jinn sponsors it, and the prize is always precious and "
            "never the same: the hidden way to 'Abqar, kinship with the "
            "tribe for ever, a young jinni's service without condition. "
            "The competition is fierce and the poetry astonishing.",
        ),
    )
    _place(
        cradle,
        "al_qudayd",
        "Al-Qudayd",
        inside=hijaz,
        **RUMOURED,
        summary=paragraphs(
            "The lost sanctuary of al-Manat, goddess of fortune and "
            "fate, one of the three Daughters of Allah, somewhere about "
            "ten miles from Medina; no one now knows where. The cult of "
            "the Daughters at Ta'if is searching for it.",
        ),
    )
    _place(
        cradle,
        "lukman_nest",
        "The Nest of Lukman's Falcons",
        inside=hijaz,
        levels=[
            Builder.level(
                "The falcons' eyrie",
                3,
                enter="Only after a hard climb in the mountains of western Arabia.",
            )
        ],
        **RUMOURED,
        summary=paragraphs(
            "Lukman, son of 'Ad, once heard a voice and found here a "
            "nest of two falcon chicks. He raised the stronger, and in "
            "its eighty years of life he did not age a day; when it died "
            "he found another chick, and so on through seven birds, the "
            "last of them Lubad, until five centuries fell on him at "
            "once and he died. The nest lies in a Magic regio somewhere "
            "in the western mountains.",
            "Each fledgling raised as a companion keeps its trainer "
            "from every Aging roll for eighty years, at a Warping Point "
            "a year, and no Longevity Ritual works beside it; when the "
            "bird dies its owner ages quickly until he raises the next. "
            "The falcon itself makes no Aging roll and dies suddenly at "
            "eighty, unless killed: it has Magic Might 8 and is "
            "unaffected by The Gift.",
        ),
    )
    _place(
        cradle,
        "stone_lovers",
        "The Stone Lovers",
        inside=najd,
        aura=3,
        **RUMOURED_LOCALLY,
        summary=paragraphs(
            "Two oddly shaped outcrops of rock in a remote Magic aura. "
            "The local tribe counts them as 'ashiras and so as members "
            "of the tribe: its legends say they were the giants Aja and "
            "Salma, lovers banished here who lived on the spot for five "
            "hundred years and slowly turned into the half-human stone "
            "sentinels seen today. Dark faerie and Infernal jinn haunt "
            "them by night, and the tribe fears that wizards will wake "
            "the giants or draw the jinn. Vis can be had from the site, "
            "the book says, without saying what.",
            "Suggested vis sources (not in the book), for the storyguide "
            "to use, change or ignore: grit that weathers from the "
            "stones' faces on the night of the full moon, 2 pawns of "
            "Terram a year; dew that gathers in the hollow between the "
            "two figures at dawn, 1 pawn of Corpus a year.",
        ),
    )


# -- Yemen, Hadramawt and 'Uman --


def _south(cradle: Cradle) -> None:
    yemen, hadramawt = cradle.places["yemen"], cradle.places["hadramawt"]
    uman = cradle.places["uman"]
    _place(
        cradle,
        "abqar",
        "The Valley of 'Abqar",
        inside=yemen,
        realm="Faerie",
        levels=[
            Builder.level(
                "'Abqar",
                3,
                "Faerie",
                enter="From Yemen or from southern Jordan; the poets' fair "
                "at 'Ukaz sometimes gives the way as its prize.",
            )
        ],
        **RUMOURED,
        summary=paragraphs(
            "In the times before Islam jinn lived in this valley and "
            "breathed inspiration into the greatest Arab poets, as "
            "their muses. It may be a faerie regio reached both from Yemen and from "
            "southern Jordan, a town in Arcadia, or both at once.",
        ),
    )
    marib = _place(
        cradle,
        "marib",
        "The Ruins of Ma'rib",
        inside=yemen,
        aura=3,
        summary=paragraphs(
            "East of Sana'a, the remains of the capital of Balqis, the "
            "Queen of Sheba, whose priest-kings, the mukkaribs, served "
            "the sun, moon and stars as al-Shams, 'Ilmaqa and al-Zuhara. "
            "Suleiman heard of her sun-worshipping land from the hoopoe "
            "and invited her to talk of faith; she came with riddles "
            "and a caravan of gold, spice and jewels, found her own "
            "throne fetched ahead of her and disguised, mistook his "
            "glass floor for water, and acknowledged the one God.",
            "Most of its palaces, temples and gardens are ruins, with "
            "small Magic auras scattered through them where pagan jinn "
            "who served the queen at Suleiman's command still live. "
            "Upstream, in the mountains, the great dyke that held back "
            "the Wadi Udhana and its wild water elementals lies broken. "
            "The book calls the land round it a good site for a "
            "covenant, for those who can supply so remote a place and "
            "face its hostile spirits, who love neither wizards nor "
            "summoners.",
        ),
    )
    _place(
        cradle,
        "ghumdam",
        "The Temple of Ghumdam",
        inside=marib,
        aura=6,
        summary=paragraphs(
            "The great temple the jinn built at Ma'rib, still standing "
            "alone and silent among the ruins, with a Magic aura of 6.",
        ),
    )
    _place(
        cradle,
        "ubar",
        "Iram, the City of a Thousand Pillars",
        inside=uman,
        aura=5,
        **RUMOURED,
        summary=paragraphs(
            "Ubar, capital of the giants of 'Ad, who ruled Yemen, "
            "Hadramawt and 'Uman five generations after the Flood from "
            "their homeland of al-Akhaf. They worshipped idols, "
            "rejected the prophet Hud whom God sent from among them, "
            "and held to their idols through the drought sent to warn "
            "them, until a great storm destroyed them, all but Hud and "
            "the few who listened, and drove the city deep under the "
            "sand.",
            "A wide hollow in the dunes above it has a Magic aura of 5. "
            "Below, in a vast cavern, the city stands whole, full of its "
            "people's riches and their dried corpses, its Magic auras "
            "still strong: a tempting covenant site, though everything "
            "is built for folk some twelve yards tall.",
        ),
    )
    _place(
        cradle,
        "trees_that_cry_blood",
        "The Trees That Cry Blood",
        inside=hadramawt,
        **RUMOURED_LOCALLY,
        summary=paragraphs(
            "A grove of five ancient mogar trees in Hadramawt's hills "
            "above the sea, growing straight out of the rock and "
            "standing up to the monsoon storms. The locals know the "
            "complicated timing of its harvests well, and dread the "
            "large, savage flock of flying serpents that nests in its "
            "branches, which shrugs off storax smoke and ordinary wards.",
            "Vis: frankincense gathered from these trees during a "
            "violent storm comes as unusually pure tears, each holding "
            "one pawn of Rego Terram vis; each tree gives several "
            "pawns a harvest.",
        ),
    )


# -- Bahrayn --


def _east(cradle: Cradle) -> None:
    _place(
        cradle,
        "hajar_ghosts",
        "The Haunted Shores of Hajar",
        inside=cradle.places["bahrayn"],
        summary=paragraphs(
            "In 350 the Persian king Shapur II sent his armies against "
            "the Arabs on both shores of the Gulf, and they killed, "
            "looted and carried off thousands round Hajar and on the "
            "Persian coast across the water. The dead walk those shores "
            "still: each night they come out and beg whoever they meet "
            "for help against their tormentors, until invisible "
            "soldiers cut them down, with weapons that are said to kill "
            "the living as well. So no one goes out after dark; they "
            "stop their ears to the screaming and the frantic hands "
            "beating on their doors.",
            "The sahirs of Hajar suspect the ghosts in any trouble by "
            "night, but cannot command the dead.",
        ),
    )


# -- the lords --


def _lords(cradle: Cradle) -> None:
    b, w, p = cradle.b, cradle.world, cradle.places
    w["al_masud"] = b.lord(
        "Ayyubid Sultan of Yemen",
        title="",
        wealth="Wealthy",
        seat="Sana'a",
        ruler="al-Mas'ud Yusuf",
        place=p["yemen"],
        summary=paragraphs(
            "Al-Mas'ud Yusuf, sultan of Yemen since 1215, the Ayyubid "
            "prince who holds 'Asir and Yemen, far more firmly than his "
            "kinsman the sultan of Egypt holds the Hijaz. He rules from "
            "Sana'a.",
            "If history holds, when the Grand Sharif Qatada is killed "
            "this year he marches in to end the bloodshed at Mecca and "
            "rules it as a soldier until his death in 1229, when the "
            "sharifs take it back.",
        ),
    )
    w["sharif"] = b.lord(
        "Grand Sharif of Mecca",
        title="",
        wealth="Wealthy",
        seat="Mecca",
        ruler="Qatada",
        answers_to=w.get("al_kamil"),
        place=p["mecca_sanctuary"],
        summary=paragraphs(
            "Qatada, Grand Sharif since 1201, governor of Mecca, a "
            "descendant of the Prophet through his grandson al-Hasan "
            "and of the Hawashim clan. He takes counsel with the "
            "scholars in the Dar al-Nadwa off the Haram Mosque, and "
            "owes the sultan of Egypt allegiance in name.",
            "If history holds, in 1220 his son al-Hasan kills him and "
            "many of the family in a massacre to make his own "
            "succession sure; the Ayyubid sultan of Yemen then takes "
            "the city in hand until 1229.",
        ),
    )
    w["uyunids"] = b.lord(
        "Uyunid Emir of Bahrayn",
        title="",
        seat="Bahrayn",
        ruler="the Uyunids",
        place=p["bahrayn"],
        summary=paragraphs(
            "The Uyunids, a Sunni Arab dynasty, rule Bahrayn in 1220, "
            "having driven out the Qarmatians, who had held it from 899 "
            "to 1076.",
        ),
    )
    w["nabhanids"] = b.lord(
        "Nabhanid King of 'Uman",
        title="",
        wealth="Wealthy",
        seat="Nizwa",
        ruler="the Nabhanids",
        place=p["uman"],
        summary=paragraphs(
            "The Nabhanids, the Ibadi kings of 'Uman, rule from Nizwa, "
            "their royal city.",
        ),
    )
    w["yahmad"] = b.lord(
        "Yahmad Lords of Muscat",
        title="",
        seat="Muscat",
        ruler="the Yahmad tribe",
        place=p["uman"],
        summary=paragraphs(
            "The Yahmad, a local tribe who have lately taken Muscat "
            "from the 'Abbasids and want to push its trade further "
            "east.",
        ),
    )


# -- the towns --


def _towns(cradle: Cradle) -> None:
    b, w, p = cradle.b, cradle.world, cradle.places
    w["mecca"] = b.town(
        "Mecca",
        ruler="the Grand Sharif Qatada",
        answers_to=w["sharif"],
        place=p["mecca_sanctuary"],
        summary=paragraphs(
            "The holiest city of Islam, in a valley among mountains "
            "that shelter it from the desert's wind and heat: houses, "
            "and shrines, convents, colleges and a hundred mosques, the "
            "greatest of them the Haram Mosque with the Ka'ba at its "
            "centre. It is always crowded: townsfolk who serve its "
            "needs, scholars who live and teach in its mosques, and "
            "pilgrims of almost every Muslim persuasion who stay a "
            "fortnight or a few years and move on. Most of its people "
            "are Sunnis, with many Zaydi Shi'is.",
            "Muhammad left it for Medina in 622, the first year of the "
            "Muslim calendar, and took it in 630; the Qarmatians sacked "
            "it in 930.",
        ),
    )
    w["medina"] = b.town(
        "Medina",
        ruler="its governor",
        answers_to=w.get("al_kamil"),
        place=p["medina_haram"],
        summary=paragraphs(
            "Madinat al-Nabi, the City of the Prophet, Islam's second "
            "holy city, on a flat plain held between mountains and old "
            "lava flows where several valleys and passes meet. Its soil "
            "is unusually rich in fruit and grain. Strong walls with "
            "watchtowers enclose it, built in 1162 by Nur al-Din, sultan "
            "of Syria. Its governor owes the sultan of Egypt allegiance "
            "but the city largely runs itself. It has long been a city "
            "of scholars: Malik ibn Anas, who died in 795 and whose "
            "followers became the Maliki school of law, lived and "
            "taught here.",
        ),
    )
    w["taif"] = b.town(
        "Ta'if",
        place=p["hijaz"],
        summary=paragraphs(
            "A town on the mountain slopes about sixty miles south-east "
            "of Mecca, famous for its orchards, which feed Mecca and "
            "other towns with fruit. Before Islam a great idol of "
            "al-Lat stood here, goddess of fertility, shepherds and "
            "caravans; it was destroyed when the Muslims took the town "
            "in 631. The Cult of the Daughters of Allah lives here in "
            "secret.",
        ),
    )
    w["sanaa"] = b.town(
        "Sana'a",
        ruler="the sultan al-Mas'ud Yusuf",
        answers_to=w["al_masud"],
        place=p["yemen"],
        summary=paragraphs(
            "The seat of government of Yemen and 'Asir, high in the "
            "Yemeni hills where the air is fresh and cool, and home of "
            "the Ayyubid sultan. Its Salt Market, the Suq al-Milh, "
            "sells every kind of curiosity to whoever searches long "
            "enough, and its food is famous for being good.",
        ),
    )
    w["muscat"] = b.town(
        "Muscat",
        ruler="the Yahmad",
        answers_to=w["yahmad"],
        place=p["uman"],
        summary=paragraphs(
            "A coastal town, perhaps Ptolemy's Hidden Port or Pliny's "
            "Moscha, and a leading point of departure for voyages "
            "beyond the Middle East; many who sail from its quays "
            "dreaming of riches never come back. The Yahmad tribe "
            "lately took it from the 'Abbasids and want its trade to "
            "reach further east. A large house of sahirs of Solomonic "
            "Travel is here, seeking the islands of Sinbad's tales.",
        ),
    )
    w["nizwa"] = b.town(
        "Nizwa",
        ruler="the Nabhanid kings",
        answers_to=w["nabhanids"],
        place=p["uman"],
        summary=paragraphs(
            "The royal city of 'Uman, a centre of faith, trade and art, "
            "with many finely decorated mosques and palaces and busy "
            "markets famous for silver jewellery and fine daggers. "
            "Several houses of sahirs are in the city and the country "
            "round it.",
            "It also has a dark name as a home of witches and sorcerers.",
        ),
    )
    w["hajar"] = b.town(
        "Hajar",
        ruler="the Uyunids",
        answers_to=w["uyunids"],
        place=p["bahrayn"],
        summary=paragraphs(
            "The chief city and port of Bahrayn, its link with the "
            "Persian coast across the Gulf. Its people never go out at "
            "night, for the ghosts of Shapur II's massacre of 350. A "
            "community of sahirs lives here.",
        ),
    )
    for key, name in (("tayma", "Tayma'"), ("khaybar", "Khaybar")):
        w[key] = b.town(
            name,
            charter="Rules itself",
            ruler="its Jewish elders",
            place=p["najd"],
            summary=paragraphs(
                "Tayma', Khaybar and the towns near them have long been "
                "a refuge for Jews, and in 1220 they are free towns that owe no sultan anything. Jews "
                "are most of the people, and fierce, clever fighters: "
                "their children learn war young, and they keep in "
                "practice with raids on other Arabian settlements beside "
                "some of the Muslim Bedouin tribes. They can raise an "
                "army very quickly, but traditional Judaism thinks "
                "little of magic or those who use it.",
            ),
        )


# -- the factions --


def _factions(cradle: Cradle) -> None:
    b, w, p = cradle.b, cradle.world, cradle.places
    w["bedouin_sahirs"] = b.faction(
        "The Bedouin Sahirs",
        faction="Hedge coven",
        tradition="trad_bedouin_hakima",
        place=p["arabia"],
        summary=paragraphs(
            "Far more Bedouin than townsfolk have supernatural power, "
            "and the Bedouin sahirs are Gifted more often than sahirs "
            "anywhere else in the Middle East. Most of Arabia's sahirs "
            "belong to a tribe, and few live in towns or houses of "
            "wisdom: they make their alliances by kin and blood. "
            "Arabia's vis is rich, and they trade it to their cousins "
            "in the towns for rare books on the Solomonic arts or for "
            "teaching.",
            "Most work Solomonic Storytelling or Solomonic Travel; some "
            "scorn the arts and only summon and bargain with jinn. Each "
            "keeps a favourite falcon or saluqi which is really a faerie "
            "jinni bound by a khadim bond. Every tribe has at least one "
            "sahir, often helped by women wise in folk magic, the "
            "hakima or kahina (soothsayers), like Folk Witches of the "
            "Faerie realm but with Animal Healing and Entrancement in "
            "place of Cursing and Flight, or by the shai'ir, poets in "
            "the old pagan manner. Most tribes have elders of jinn "
            "blood, a wandering sahir vizier with an 'afrit or marid "
            "in his service, and families of faerie jann among their "
            "kin, who take the shapes of camels, falcons, hounds and "
            "horses. To a Bedouin, man or jinni, Muslim or pagan, the "
            "clan comes first and the family second.",
            "Poetry is the Bedouin's pride. Poets (shai'ir, not to be "
            "mistaken for sahir) and reciters (rawi) are historians, "
            "soothsayers and praise-singers at once, carrying verses in "
            "praise of the tribe (qit'ah) and savage mockery of others "
            "(hija'). Bedouin sahirs still settle feuds by zajal, a "
            "mock battle in verse: opposed rolls of Communication + "
            "Solomonic Storytelling (Communication + Folk Ken between "
            "mundanes), +2 for Arabic 6 or more. Enchanting Poetry and "
            "Entrancement are common even among poets who are no "
            "wizards; the satirist Abu Nuwas of Harun's court passed "
            "into Golden Baghdad's tales as a faerie of Elysium.",
        ),
    )
    w["muruwa"] = b.faction(
        "Muru'a, the Bedouin Code",
        faction="Hedge coven",
        tradition="trad_bedouin_hakima",
        rules="Hospitality, courage, honour; loyalty to the clan above "
        "all; always keep your word.",
        place=p["arabia"],
        summary=paragraphs(
            "The code the northern nomads kept from before Islam, all "
            "of them Sunni Muslims in name: hospitality (diyafa), "
            "courage (hamasa) and honour (sharaf for men, ird for "
            "women) above all, with forgiveness, loyalty and "
            "self-sacrifice, and colouring town life too. Dutybound "
            "(Bedouin code) is nearly universal among Bedouin; a few "
            "from the deep desert are still Pagan.",
            "Knowledge of muru'a is an Organization Lore like a "
            "non-Hermetic Mystery's, through which the tribe's hakima, "
            "as Mystagogue, initiates faerie-aligned Virtues useful to "
            "a nomad: Arcadian Travel, Animal Ken, Art of Memory, "
            "Dowsing, Death Prophecy, Cursing, Entrancement, Enchanting "
            "Poetry (as Enchanting Music), Greater Immunity to thirst, "
            "Puissant Arabic, Wilderness Sense, Spiritual Pact and Ways "
            "of the Desert; Enchanting Poetry is the Major Virtue "
            "most often gained. Scripts differ from tribe to tribe, with "
            "ordeals tied to the code that leave Flaws such as "
            "Generous, Higher Purpose, Overconfident, Oversensitive to "
            "slights on honour, Proud, a Vow to keep one's word, or "
            "Weakness.",
            "A foreigner who shows the virtues the Bedouin admire may be "
            "taken into a clan and initiated, gaining Dutybound "
            "(Bedouin code) and Close Family Ties to the clan. To the "
            "tribe and its jinn that bond, 'asabiyya, outweighs every "
            "other, so a magus may have to choose between it and the "
            "Code, and a quaesitor come for him may find a whole tribe "
            "of jinn-blooded Bedouin standing behind him.",
        ),
    )
    w["daughters_cult"] = b.faction(
        "The Cult of the Daughters of Allah",
        faction="Other",
        decides="Its leader",
        members=3,
        ruler="'Abd al-Qadir",
        wants="To find al-Qudayd, al-Manat's lost sanctuary, and bring back "
        "the worship of the three goddesses.",
        place=w["taif"],
        summary=paragraphs(
            "Before Islam three goddesses were worshipped round Mecca: "
            "al-Lat at Ta'if, al-Manat, goddess of fortune and fate, at "
            "al-Qudayd near Medina, and al-'Uzza, of strength and of "
            "Venus, at a sanctuary outside Mecca. The "
            "pagans called them the Daughters of Allah, whom they "
            "already held to be the high creator. The story of the "
            "'Satanic Verses', still argued over by scholars, says Iblis "
            "once slipped verses into the revelation that let Muslims "
            "ask the Daughters to intercede, and that God at once sent "
            "verses rejecting them.",
            "A single family of Ta'if has kept their worship alive in "
            "secret through the centuries, always three strong, each "
            "member able to channel one goddess. Two sanctuaries, al-Lat's "
            "and al-'Uzza's, they have already found; they are hunting "
            "for the third. 'Abd al-Qadir speaks for al-Lat, with power over "
            "growth in men, beasts and plants and over swift travel; "
            "his son Yusuf for al-Manat, bending chance and the dice; "
            "and Yusuf's wife Farida for al-'Uzza, with great strength "
            "and power over beauty, love, performance and speech. The "
            "book suggests playing them as Spirit Votaries, or, if the "
            "cult is corrupt, as diabolists.",
        ),
        secrets=paragraphs(
            "Farida, the newest of the three, has doubts: her Muslim "
            "upbringing, what she is asked to do, or the child she may "
            "be carrying, who would replace her in a family that is "
            "never more than three.",
        ),
    )
    w["witches_of_nizwa"] = b.faction(
        "The Witches of Nizwa",
        faction="Hedge coven",
        place=w["nizwa"],
        summary=paragraphs(
            "The witches and sorcerers of Nizwa's dark reputation, who "
            "are not of the Order of Suleiman. They are said to travel "
            "in an instant by stepping over a line drawn in the sand, "
            "and, worse, to make people seem to die, take the 'corpses' "
            "and keep them as mindless slaves. The book has no "
            "tradition record for them.",
        ),
        secrets=paragraphs(
            "The book leaves their nature open: Infernalists, faerie "
            "wizards, Soqotran witches in exile, agents of the Olibanum "
            "King working against the Order of Suleiman, the last of "
            "Sheba's astral sorceresses, or nothing but slander.",
        ),
    )
    w["jurhumites"] = b.faction(
        "The Jurhumites",
        faction="Other",
        realm="Faerie",
        place=p["hijaz"],
        wants="Mecca back, and their old feud with its rulers.",
        summary=paragraphs(
            "An ancient tribe who ruled Mecca and parts of the Hijaz "
            "before Islam. They refused the faith, seemed beaten by the "
            "first Muslim armies, and now live on in the old tales of "
            "the pagan tribes: every one of them is a dark faerie jann, "
            "with more elemental power, of Auram and Terram, than most "
            "of their kind, though a few jinn-blooded sahirs are "
            "secretly counted as adopted kin. As Mecca's old masters "
            "they know hidden ways into the closed places.",
            "Other tribes of old survive, the Bedouin say, as faerie "
            "jinn clans: the Jadis, the Tasm and the Thamudites.",
        ),
    )
