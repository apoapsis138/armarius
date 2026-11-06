"""Records two or more book packs share: the Middle East and its
neighbours as of 1220, built the same way by every pack that holds
them, so importing a second pack matches each by name and updates it
rather than adding a twin.

Each function takes the pack's Builder (and where the record sits, which
is each pack's own map) and returns what it made. The text follows The
Cradle and the Crescent wherever that book describes the record, with
what Blood and Sand adds on the same record (a threat's Levant stages)
written in here too, since a record two packs build must come out the
same in both. A pack adds its own facts on its own records, never by
changing these.

The Sultan of Rum and the Emperor of Trebizond are The Sundered Eagle's
(the Theban pack's) records, in its words; the Levant pack builds them
through the same two functions.

`middle_east(b)` builds the whole shared set in its order and returns it
by key; a pack may instead call the functions one by one.

The Mongols' stages in Russia and Poland are The Dragon and the Bear's
(the Novgorod pack's), written into the shared record the same way.

Sources: The Cradle and the Crescent, Blood and Sand: The Levant
Tribunal, The Sundered Eagle and The Dragon and the Bear: The Novgorod
Tribunal (Atlas Games), content under CC-BY-SA 4.0; the text here is a
summary of them, not their words."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .builder import Builder, paragraphs

if TYPE_CHECKING:
    from ..models import Creature, Neighbour

#: The Sahirs tradition (The Cradle and the Crescent), named by the
#: Order of Suleiman and its families.
SAHIRS = "trad_sahirs"
#: The Nizari Mustajibs tradition, named by the Nizaris.
MUSTAJIBS = "trad_nizari_mustajibs"


# -- the lords the Theban pack made first --


def sultan_of_rum(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Seljuk Sultan of Rum, ruled in 1220 by Kayqubad I."""
    return b.lord(
        "Sultan of Rum",
        title="duke",
        wealth="Wealthy",
        seat="Konya",
        ruler="Kayqubad I",
        place=place,
        summary=paragraphs(
            "The Seljuk Sultanate of Rum holds the Anatolian plateau, lost "
            "to the empire after Manzikert, and in the north reaches the "
            "Black Sea at Sinope, splitting Nicaea from Trebizond. It drove "
            "north between them in 1214, killing David Komnenos, but could "
            "not reach Trebizond through the mountains. Its sultan "
            "Kaykhusraw I died at Antioch-on-the-Maeander in 1211, and the "
            "Maeander has been the border with Nicaea since. Trebizond "
            "still fears it.",
            "The book names no sultan for 1220. History has Kaykhusraw's "
            "son Kaykaus I reign from 1211 to his death about 1220, "
            "followed by his brother Kayqubad I, who is named as ruler "
            "here.",
        ),
    )


def emperor_of_trebizond(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Grand Komnenos at Trebizond, Alexios I."""
    return b.lord(
        "Emperor of Trebizond",
        title="duke",
        wealth="Wealthy",
        seat="Trebizond",
        ruler="Alexios I Komnenos",
        place=place,
        summary=paragraphs(
            "Alexios Komnenos, thirty-eight, grandson of the Emperor "
            "Andronikos Komnenos, who seized Trebizond with his brother "
            "David in 1204, the very year Constantinople fell, and calls "
            "himself 'Emperor and Autocrat of the Romans'. David pushed "
            "west into Paphlagonia and Heraclea, provoking Rum and then "
            "Nicaea, which won back most of his gains in 1212; Rum killed "
            "him in 1214. Alexios rules on, propped by Georgian troops and "
            "Latin and Seljuk mercenaries, cut off from Nicaea and still "
            "threatened by Rum, and also rules Cherson and Kerch across "
            "the Black Sea; Cherson pays him tribute.",
            "He lives with his family in the castle behind the city. Like "
            "his grandfather he patronises art and letters, giving titles "
            "and stipends to astronomers, alchemists and experimental "
            "philosophers, and his Silk Road market and its taxes make "
            "Trebizond very rich.",
        ),
    )


# -- the Order of Suleiman --


def order_of_suleiman(b: Builder) -> dict[str, Neighbour]:
    """The Suhhar Sulayman, and the two of its five families whose seats
    are in the Levant: Stone at Damascus and River at Cairo. Keys
    "order", "stone", "river"."""
    order = b.faction(
        "The Order of Suleiman",
        faction="Hedge coven",
        decides="A council",
        members=5000,
        ruler="Kha'trazh, grand vizier",
        tradition=SAHIRS,
        rules="Enchanted items go to sahirs alone; no extracted vis is "
        "traded to Hermetic magi; a sahir who can himself be summoned "
        "may not be a member.",
        wants="To drive the crusaders, and the magi who came with them, "
        "out of the lands of Islam.",
        offers="Solomonic magic, and a guide for a promising ruler or scholar.",
        summary=paragraphs(
            "The Suhhar Sulayman, the great society of sahirs, whom "
            "Hermetic magi have long whispered about as a rival Order "
            "bent on their ruin. Its members are mostly unGifted Muslim "
            "summoners who command jinn and other spirits and work spells "
            "and devices much like the Order's; they claim Solomon's "
            "powers, taught him (they say) by al-Khidr. About five "
            "thousand live east of the Levant, with two or three thousand "
            "more in Syria and Egypt, perhaps one in ten of them Gifted; "
            "they outnumber the magi about five to one. Founded in 805 by "
            "the First Council's heirs, it has a grand vizier elected for "
            "life (Kha'trazh, of the Heart, for some thirty years), five "
            "Asalat who lead the families, and a vizier for every "
            "community of three or more.",
            "The Majlis, its council, meets in Baghdad's summer bazaar for "
            "three days each August; only viziers sit, one vote each. Its "
            "chief rules: enchanted items go to sahirs only, extracted "
            "vis is never sold to magi, a sahir who can be summoned "
            "counts as a spirit and may not belong, a sahir silent for "
            "five years is lost, and the penalty is expulsion or a fine "
            "of vis or service; quarrels go to duels or trials of boasts, "
            "stories or champions. When the grand vizier's seat is empty "
            "the vizier of Baghdad's Dar al-Hikma acts by custom.",
            "Long turned inward, the Suhhar was shaken by the Crusades. "
            "Its sahirs met the invading magi, found most of them proof "
            "against Solomonic magic, and lost when they fought them "
            "openly; so they worked in secret, guiding rulers, ambushing "
            "through the Magic Realm and reading the stars, and helped "
            "retake Edessa and break the Second Crusade. By custom a "
            "vizier may go in disguise as a nameless sage, 'sending a "
            "guide', to offer a promising leader help; Nur al-Din "
            "declined, having been taught by al-Khidr himself, and "
            "Salah al-Din refused without a word.",
            "In 1220 the Suhhar still counts itself at war with the "
            "crusaders and every Hermetic magus among them. It welcomes "
            "magi into its lands, where they are easier to watch, studies "
            "them closely, and is planning a Solomonic counter-crusade "
            "against the Levant. It never signed the Treaty of Baghdad "
            "that binds the Levant's magi and the caliph's court, and it "
            "treats the Nizaris as traitors.",
            "Its summoning, naranj, Al-Iksir and the rest are the Sahirs "
            "tradition's chapter and The Cradle and the Crescent's "
            "chapter on the Order.",
        ),
    )
    stone = b.faction(
        "Ashab al-Sakhr, the Followers of the Stone",
        faction="Family",
        decides="Its leader",
        ruler="the Asala al-Sakhr",
        tradition=SAHIRS,
        wants="War on the crusaders and the magi with them.",
        offers="Arms, armour and Solomonic Alchemy.",
        summary=paragraphs(
            "The family of Solomonic Alchemy, heirs of Jabir ibn Hayyan, "
            "the one Gifted member of the First Council. Its seat is "
            "Damascus, once the Umayyads' capital and now the heart of "
            "the sahirs' war on the invading soldiers and magi. Its "
            "members are devout, almost never anything but Muslim, cold "
            "to Europeans, proud of their honour, and fond of good steel: "
            "many fight with blades rather than spells, or with blades "
            "their magic has strengthened. An Asala of the Stone first "
            "called the crusaders the Infernal's tools and led the "
            "counter-crusade among the Syrian viziers; the family's "
            "Asala is usually chosen by a test of arms.",
            "Its house at Damascus is a bayt of the Order of Suleiman, "
            "not a Hermetic covenant.",
        ),
    )
    river = b.faction(
        "Ashab al-Nahr, the Followers of the River",
        faction="Family",
        decides="Its leader",
        ruler="the Asala al-Nahr",
        tradition=SAHIRS,
        summary=paragraphs(
            "The family of Solomonic Travel, the art of journeys between "
            "worlds: Faerie and the Magic Realm, the Divine and Infernal "
            "places, dreams and the land of the dead. It was thought a "
            "lesser art until the Nabatean Ibn Wahshiyya, two "
            "generations after its founder al-Hajjaj, read its secrets "
            "out of the old Egyptians' writings. Its great academy is in "
            "Cairo, still the centre of the family's magic. Both "
            "founders were known for passion that ended in madness, and "
            "the family's sahirs are an eccentric lot.",
            "Its house at Cairo is a bayt of the Order of Suleiman, not "
            "a Hermetic covenant.",
        ),
    )
    for family in (stone, river):
        family.answers_to = order.id
        b.link(order, "places", family, "One of the five families")
    return {"order": order, "stone": stone, "river": river}


# -- the jinn --


def jinn(b: Builder, *, inside: Neighbour | None = None) -> dict[str, Neighbour]:
    """The jinn as one faction, with Jinnistan and the Mountains of Qaf.
    Keys "jinn", "jinnistan", "qaf"."""
    faction = b.faction(
        "The jinn",
        faction="Spirits and beings",
        decides="Its leader",
        summary=paragraphs(
            "In Islamic teaching God made three thinking peoples: angels "
            "of light, jinn of smokeless fire, and humans of clay. Jinn, "
            "like men, can be saved or damned; many have taken Islam, "
            "others tempt men and refuse the faith. Iblis was once among "
            "the mightiest of them. A jinni's body is Faerie glamour, "
            "Infernal power or pure magic, by its realm, usually of Vim "
            "and sometimes of an element; most can take a body of matter "
            "and change shape.",
            "There are no Divine jinn. The faerie jinn are pious or "
            "impious, the magic jinn pagan spirits, genii loci and "
            "elementals, the Infernal jinn corrupt. They divide into "
            "tribes, said to number 112, which follow their realms "
            "loosely: the jann, lesser faerie jinn who keep Islam and "
            "pass for merchants, nomads or shepherds; the shaitan, dark "
            "faeries and demons; the ghul, faerie predators and Infernal "
            "eaters of the dead who haunt graveyards; the marid, ancient "
            "spirits of water, wind and weather, mostly in Arabia; and "
            "the 'ifrit. Every jinni has a true name, belongs to the "
            "lands of Islam, speaks Arabic and knows its theology. The "
            "bismillah, the four Quls and the Throne Verse are their "
            "weaknesses, and a hajji resists some of their powers.",
            "Many things the common folk call jinn are not: ghosts, "
            "naddahas, nisnases, shiqq and the rest, the Persian divs, "
            "yazatas and peris, the Soqotran jinniyah, and the planetary "
            "spirits the Arabs call al-Nujum, the Stars. Sihr commands "
            "true jinn only.",
            "Their lands: Jinnistan, the Mountains of Qaf, Amerabad the "
            "City of Amber, Golden Baghdad, Khashgar and the ocean "
            "al-Khadar.",
        ),
    )
    jinnistan = b.place(
        "Jinnistan",
        realm="Faerie",
        status="Rumoured",
        known="In the region",
        inside=inside,
        summary=paragraphs(
            "Wherever jinn make their homes, just out of a man's sight: "
            "behind a door that cannot fit between two houses, round the "
            "last corner of a bazaar alley, under the ground, in the "
            "wilds, in ruins, and beyond this world in regiones and the "
            "otherworlds. All of it is Jinnistan. Perhaps it began in the "
            "Magic Realm; the tales now put most of it in "
            "Arcadia, with branches into Eudokia and perhaps into Hell. "
            "Its jinn live much as their human neighbours do and pass "
            "freely between the two, and whole jinn cities lie within "
            "it, Amerabad the City of Amber among them.",
            "Travellers say it lies past the great rivers, past the "
            "eastern mountains, or over the edge of the sea; they are "
            "right and wrong at once, for where jinn are, Jinnistan is.",
        ),
    )
    qaf = b.place(
        "The Mountains of Qaf",
        status="Rumoured",
        known="In the region",
        inside=inside,
        summary=paragraphs(
            "In Muslim lore a ring of peaks around the known world, "
            "green as emerald and impassable, the wall between the lands "
            "of men and the homes of the jinn and the jinn's homeland. "
            "Geographers have put it in the Caucasus, the Pamirs, the "
            "Hindu Kush, even the Urals or the Atlas, and the learned "
            "match it with the Greeks' great eastern range at the end of "
            "Alexander's world.",
            "It may be the very idea of mountains in the Magic Realm, "
            "with other worlds behind it, or Faerie's distillation of "
            "every tale ever told of mountains no one can cross.",
        ),
    )
    b.link(faction, "places", jinnistan, "Their homes")
    b.link(faction, "places", qaf, "Their homeland's wall")
    return {"jinn": faction, "jinnistan": jinnistan, "qaf": qaf}


def al_khidr(b: Builder, *, place: Neighbour | None = None) -> Creature:
    """Al-Khidr, the Green One, named without stats."""
    return b.creature(
        "Al-Khidr, the Green One",
        page="p. 137",
        source="TC&TC",
        realm="Divine",
        place=place,
        appearance="An old Muslim in a woollen cloak, his skin and clothes "
        "tinged blue-green by the Water of Life.",
        notes=paragraphs(
            "A prophet of Islam who cannot die, having drunk of the Water "
            "of Life, which he reached by the light of a jewel Adam "
            "brought from Paradise; in some tales he and Alexander sought "
            "it together, and Alexander lost his way in the dark. He "
            "roams the world advising where God sends him, and is said "
            "to have guided every prophet since his birth save Muhammad, "
            "who taught him instead. Sky, sea and every growing thing "
            "obey him, and the Sufis hold him the perfect shaykh.",
            "The sahirs say he taught Solomon his secrets, and the "
            "Nizaris count him among the forms of their immortal imam. "
            "He taught Nur al-Din magic before the Order of Suleiman's "
            "guide could, and their talk is kept in a book at Baghdad. "
            "He rarely gives his name, and his advice can seem mad but "
            "always proves right; he helps those who seek the Water of "
            "Life only if they mean well. Shamakhi's Rock of Moses marks "
            "where Moses met him.",
            "Named without stats: neither book gives his Might or powers.",
        ),
    )


# -- the Nizaris --


def nizaris(b: Builder, *, place: Neighbour | None = None) -> dict[str, Neighbour]:
    """The Nizari Isma'ilis and their head, Jalal al-Din Hasan, at
    Alamut. Keys "nizaris", "imam"."""
    imam = b.lord(
        "Lord of Alamut",
        title="count",
        wealth="Wealthy",
        seat="Alamut",
        ruler="Jalal al-Din Hasan",
        place=place,
        summary=paragraphs(
            "The dai'd-duat, grand master of the Nizari Isma'ilis, who "
            "has held Alamut and its castles in Daylam, Quhistan, Qumis "
            "and Fars since 1210. Jalal al-Din Hasan has done what none "
            "thought possible and turned the sect Sunni in public; his "
            "followers take it for taqiyya and obey, and many think him "
            "the imam-qa'im. He looks for friends against the "
            "Khwarazm-shah, the caliph in the west and Genghis Khan in "
            "the east, has allied with the rulers of Arran and "
            "Azarbayjan, and has married the emir of Gilan's four "
            "daughters. The Syrian Nizaris at Masyaf answer to him.",
        ),
    )
    sect = b.faction(
        "The Nizaris",
        faction="Faith or sect",
        decides="Its leader",
        ruler="Jalal al-Din Hasan",
        tradition=MUSTAJIBS,
        place=place,
        rules="The imam's word is absolute; taqiyya, hiding one's faith, "
        "is lawful in danger.",
        summary=paragraphs(
            "The Nizari Isma'ilis, whom the crusaders call the "
            "Assassins (a slander from Syria; the ascetic Nizaris take "
            "no drugs) and the Persians the Batiniyya or the heretics. "
            "Their founder Hasan-i Sabbah, a sahir, murdered the "
            "Suhhar's grand vizier, fled to Alamut and taught his faith's "
            "followers Solomon's art, so that the Nizaris walk unseen, "
            "bend minds, poison and cross great distances in an instant. "
            "The Suhhar and the Nizaris have tried to destroy each other "
            "ever since, with equal losses; the Suhhar still calls them "
            "traitors and will not treat with them, while the Nizaris "
            "kill sahirs, as anyone else, only when they stand in the "
            "imam's way.",
            "Seven ranks: the fida'i and lasiq, uninitiated killers who "
            "make the sect's name; the mustajib, the first initiates and "
            "its magicians; the da'i, the hujja over each territory or "
            "jazira, and the dai'd-duat, grand master of Alamut; and the "
            "imam-qa'im, the immortal teacher who was once Elijah, "
            "Enoch, Khidr and 'Ali. They seek the hidden meaning of the "
            "Qur'an, live by the fifty-one epistles, and hold that the "
            "law no longer binds those who know it, so they reject the "
            "Pillars and the caliph alike. Members call one another "
            "rafiq, comrade.",
            "Besides Daylam, Quhistan and Qumis they keep hidden "
            "communities in the southern Zagros (Shardiz among them) and "
            "cells in most great cities. The Syrian branch holds Masyaf "
            "and a stronghold near Aleppo; its most famous chief, Rashid "
            "al-Din Sinan, the crusaders' Old Man of the Mountain, died "
            "in 1193.",
        ),
    )
    b.link(sect, "places", imam, "Their head")
    return {"nizaris": sect, "imam": imam}


# -- the lords of 1220 --


def caliph(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The 'Abbasid caliph al-Nasir at Baghdad."""
    return b.lord(
        "Caliph of Baghdad",
        title="duke",
        wealth="Wealthy",
        seat="Baghdad",
        ruler="al-Nasir li-Din Allah",
        place=place,
        summary=paragraphs(
            "The 'Abbasid caliph, Commander of the Faithful, al-Nasir, "
            "who has reigned since 1180 and is a forceful one. The "
            "'Abbasids have ruled from Baghdad since 762, as figureheads "
            "under others for much of three centuries, but since "
            "al-Muqtafi (1136 to 1160) the caliphs have governed Iraq "
            "themselves, and in 1157 drove the Seljuk sultan from the "
            "city. His real realm is little more than Iraq, sometimes "
            "the Jazira and parts of Persia too; most Sunni rulers "
            "honour him in name, the Ayyubids among them, and he has yet "
            "to recognise the Khwarazm-shah's claim to be shah. He has "
            "built ribats for the Sufis and restored mosques, shrines "
            "and colleges to heal the city's quarrels.",
            "His court is party to the Treaty of Baghdad with the Levant's "
            "magi (Blood and Sand). If history holds he reigns until "
            "1225; the Mongols take Baghdad in 1258 and kill the last "
            "caliph by rolling him in a carpet and trampling him, so that "
            "no royal blood touches the ground.",
        ),
    )


def al_kamil(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Ayyubid sultan of Egypt, head of the family."""
    return b.lord(
        "Ayyubid Sultan of Egypt",
        title="duke",
        wealth="Wealthy",
        seat="Cairo",
        ruler="al-Kamil Muhammad",
        place=place,
        summary=paragraphs(
            "Al-Kamil, sultan in Cairo since 1218, the head of Salah "
            "al-Din's family, the Ayyubids, whose princes rule Egypt, "
            "Syria, the Jazira and Yemen and spend much of their time "
            "plotting against one another. The Hijaz, Mecca and Medina "
            "are his in name; his kinsman al-Mas'ud Yusuf holds Yemen and "
            "'Asir more closely.",
            "In 1220 the Fifth Crusade sits in Damietta, taken in 1219 "
            "after he offered, and was refused, all the old Latin lands "
            "west of the Jordan for the Crusade's leaving Egypt and a "
            "thirty-year truce. He camps at al-Mansura. If history holds "
            "he reigns until 1238.",
        ),
    )


def al_aziz(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Ayyubid ruler of Aleppo, who holds Edessa."""
    return b.lord(
        "Ayyubid Sultan of Aleppo",
        title="count",
        wealth="Wealthy",
        seat="Aleppo",
        ruler="al-'Aziz Muhammad",
        place=place,
        summary=paragraphs(
            "Al-'Aziz, Salah al-Din's grandson, who has ruled Aleppo since "
            "1216 and holds Edessa, taken from the crusaders by Zangi on "
            "Christmas Eve 1144, where most of the people are Christians "
            "of several churches. Edessa's Mandylion, the cloth bearing "
            "Christ's face, went to Constantinople in the tenth century "
            "and was lost in the sack of 1204. If history holds he "
            "reigns until 1236.",
        ),
    )


def lord_of_mosul(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Zangid emirate of Mosul under its regent, Badr al-Din Lu'lu'."""
    return b.lord(
        "Emir of Mosul",
        title="count",
        wealth="Wealthy",
        seat="Mosul",
        ruler="Badr al-Din Lu'lu', regent",
        place=place,
        summary=paragraphs(
            "Mosul has been the Zangids' since 1128; their founder 'Imad "
            "al-Din Zangi, who died in 1146, is famed for taking Edessa "
            "from the crusaders. In 1220 the real ruler is the mamluk "
            "Badr al-Din Lu'lu', regent for the emir al-Qahir Mahmud, "
            "who owns the Ayyubids as overlords and the caliph above "
            "them, in name.",
        ),
    )


def king_of_georgia(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """Giorgi IV Lasha, king of Georgia."""
    return b.lord(
        "King of Georgia",
        title="duke",
        wealth="Wealthy",
        seat="Tiflis",
        ruler="Giorgi IV Lasha",
        place=place,
        summary=paragraphs(
            "Giorgi IV Lasha, king since 1213, of a Christian kingdom "
            "free of Muslim rule only since Dawid II took Tiflis in 1121, "
            "after centuries of war with Muslim overlords. His people "
            "are Georgians, Armenians, Turks, Persians and Alans, "
            "Christian and Muslim; the Georgian church answers to neither "
            "the pope nor the emperor. His troops prop up the Emperor of "
            "Trebizond. If history holds he reigns until 1223.",
        ),
    )


# -- places --


def iraq(b: Builder, *, inside: Neighbour | None = None) -> Neighbour:
    return b.place(
        "Iraq",
        inside=inside,
        known="In the region",
        summary=paragraphs(
            "The land of the Tigris and Euphrates, settled for thousands "
            "of years and in 1220 still thick with towns along the "
            "rivers. The faerie gods who once ruled it are seen no more, "
            "though their ziggurats still tower over passers-by. Since "
            "the 'Abbasids took power in 750 it has been the political "
            "heart of Islam, whatever the caliph's real reach; the caliph "
            "rules it directly now. North of it lies the Jazira, mostly "
            "under quarrelling Ayyubid princes and cities that honour "
            "them only in name.",
        ),
    )


def baghdad(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    return b.town(
        "Baghdad",
        place=place,
        ruler="the caliph al-Nasir",
        summary=paragraphs(
            "The caliph's city and so the political centre of Islam, "
            "founded by al-Mansur in 762. Its heart is his Round City on "
            "the west bank, three walls round the first palace of the "
            "Golden Gate; the caliphs spread it over both banks with "
            "mosques, palaces and gardens in its golden age. Fire, flood "
            "and civil strife have ruined much of it since: on the west "
            "bank each quarter stands walled off among ruins, and only "
            "the third of the city round the caliph's palace on the east "
            "bank thrives. Shi'is and Sunnis, and the Sunni schools of "
            "law, quarrel and sometimes fight; the Sufis prosper in the "
            "ribats the caliphs build them.",
            "Each summer a vast fair fills the streets and open ground "
            "south of the city for most of the season, where anything at "
            "all may be bought, from vendors who appear only when their "
            "wares are wanted, or whose tents swallow the careless. The "
            "Order of Suleiman holds its Majlis there in August. About a "
            "thousand sahirs live in the city, more than anywhere else, "
            "in eight houses of wisdom, the greatest the Dar al-Hikma "
            "north of the palace, with nearly a hundred sahirs and a "
            "famous observatory.",
        ),
    )


def mosul(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    return b.town(
        "Mosul",
        place=place,
        ruler="Badr al-Din Lu'lu', regent",
        summary=paragraphs(
            "On the east bank of the Tigris across from the ruins of "
            "Nineveh, behind a double wall, a strong citadel and the "
            "river; a broad road runs north to south through it and many "
            "houses are of marble, with gardens and suburbs outside. Its "
            "mosques hold the tombs of Jonah and of St George, a prophet "
            "to Muslims too; it has a healing spring, a squash tree the "
            "Prophet planted, colleges and Christian monasteries. Its "
            "people are Muslims, Christians and Yazidis, and its cloth "
            "gives muslin its name.",
        ),
    )


def georgia(b: Builder, *, inside: Neighbour | None = None) -> Neighbour:
    return b.place(
        "Georgia",
        inside=inside,
        known="In the region",
        summary=paragraphs(
            "A Christian kingdom of mountains, hills and high plains, "
            "with lowland only on the Black Sea coast and along the "
            "Rioni and Kura. Its capital Tiflis sits on great trade "
            "roads, the Silk Road among them, behind double walls and "
            "three strong gates, and for all the wars fought over it is "
            "a tolerant city where mosque, church and synagogue may stand "
            "side by side.",
        ),
    )


def greater_armenia(b: Builder, *, inside: Neighbour | None = None) -> Neighbour:
    return b.place(
        "Greater Armenia",
        inside=inside,
        known="In the region",
        summary=paragraphs(
            "East of Asia Minor and south-west of Georgia, a war-torn "
            "land of mountains, high plains and valleys, with winters of "
            "eight months and more. Taken by the Muslims in the seventh "
            "century, tributary and free in the ninth, fought over by "
            "Muslims and Byzantines (many Armenians left for Lesser "
            "Armenia then), and lost to the Turks in the eleventh, it is "
            "contested still: the Ayyubids hold some of the south, "
            "Trebizond a piece in the north-west, and local dynasties the "
            "rest. Greeks, Armenians and Turks grow grain, fish, mine "
            "silver and salt, and weave, dye and embroider.",
            "Its remote sites keep strong Magic auras, and its politics "
            "leave room for a new covenant that does not grow too strong "
            "for its neighbours, if it can be supplied through the "
            "winters.",
        ),
    )


def pit_of_harut_and_marut(b: Builder, *, inside: Neighbour | None = None) -> Neighbour:
    """The pit under Babel where the two angels hang chained."""
    return b.place(
        "The Pit of Harut and Marut",
        inside=inside,
        status="Rumoured",
        known="In the region",
        summary=paragraphs(
            "Beneath the ruins of Babylon hang Harut and Marut, the two "
            "angels who taught men magic, chained there for it; some "
            "sahirs say they spread the dark, Infernal form of "
            "Solomon's art as a test of mankind's faith. The ruins above "
            "saw the Tower of Babel, the Jews' exile, Nebuchadnezzar's "
            "Hanging Gardens and the Persians' overthrow of Belshazzar. "
            "Ancient Magic says more of the city's mysteries.",
        ),
    )


# -- threats --


def fifth_crusade(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """The Crusade at Damietta, with Blood and Sand's stages for the
    years ahead and The Cradle and the Crescent's counter-crusade."""
    return b.threat(
        "The Fifth Crusade",
        place=place,
        antagonist="The crusaders at Damietta, and the papal legate Pelagius",
        moves="Fixed dates",
        summary=paragraphs(
            "In 1218 the Crusade chose to strike at Egypt, the heart of "
            "Muslim power, and laid siege to Damietta. Al-Kamil offered "
            "every old Latin land west of the Jordan and a thirty-year "
            "truce if it would leave Egypt; it refused, and Damietta "
            "fell in 1219. The legate Pelagius claims the conquests for "
            "the Church, not the Kingdom of Jerusalem, and the Muslim "
            "armies are working their way back toward the city.",
            "Both orders of wizards watch it. Foothold and the Levant's "
            "crusading magi want the Treaty of Baghdad voted down in "
            "1221 so they can help it, and the True Cross has opened a "
            "covenant in Damietta itself; the Order of Suleiman is "
            "planning its own counter-crusade against the Levant.",
        ),
        stages=[
            Builder.stage(
                "The legate and the king fall out",
                year=1220,
                clues="Pelagius and John of Brienne quarrel over who "
                "commands and who keeps what is won.",
                ignored="John leaves the camp, and the Crusade loses its momentum.",
            ),
            Builder.stage(
                "The Nile rises",
                year=1221,
                clues="The host marches south toward al-Kamil's camp at al-Mansura.",
                ignored="The flood cuts the crusaders off; Pelagius "
                "agrees an eight-year truce and the Crusade leaves "
                "Egypt.",
            ),
        ],
    )


def mongol_conquest(b: Builder, *, place: Neighbour | None = None) -> Neighbour:
    """Genghis Khan's war on the Khwarazm-shah in 1220."""
    return b.threat(
        "The Mongol Conquest",
        place=place,
        antagonist="Genghis Khan and his horde",
        moves="Fixed dates",
        summary=paragraphs(
            "As 1220 opens Genghis Khan is camped before Bukhara with a "
            "great part of his horde. He has come for the Khwarazm-shah, "
            "whose governor at Otrar killed his merchants and who shamed "
            "and killed his envoys, and the shah's empire from the "
            "Jaxartes to the Gulf is about to fall. The cities the "
            "Mongols sack and leave empty may take Infernal auras of "
            "wrath, which draw lesser demons, dark faeries, ghuls and "
            "evil jinn in the horde's wake, and the unburied dead "
            "wander.",
            "If history holds, the Mongols take Persia, Georgia, Armenia, "
            "northern Iraq and Asia Minor in the decades after, sack "
            "Baghdad in 1258, and are stopped only by Egypt's Mamluks in "
            "Syria in 1260. The Levant's magi know almost nothing of "
            "them yet.",
            "In Russia and Poland, if history holds, they come twice: a "
            "reconnaissance that breaks the princes on the Kalka in 1223, "
            "and from 1237 a conquest that burns Ryazan, Vladimir, "
            "Chernigov and Kiev, ravages Poland and Hungary, and lays the "
            "Mongol yoke on Russia for two centuries. Their spirits run "
            "ahead of them: since 1206 wingless thunder wyrms have raided "
            "Slavic Arcadia in the Onslaught, and their spies and shamans "
            "work among the princes long before the horde returns.",
        ),
        stages=[
            Builder.stage(
                "Bukhara falls",
                year=1220,
                season="Winter",
                ignored="The town falls within a fortnight; its "
                "defenders are killed, its people enslaved or driven "
                "off, and fire leaves it in ruins under an Infernal "
                "aura of 3, save round the Kalyan minaret.",
            ),
            Builder.stage(
                "Samarkand and the Jaxartes towns",
                year=1220,
                season="Spring",
                ignored="The horde, swelled by Turkish recruits, "
                "destroys the oasis towns along the Jaxartes as far as "
                "Khojend and takes Samarkand.",
            ),
            Builder.stage(
                "Gurganj and the shah",
                year=1220,
                season="Autumn",
                ignored="Gurganj falls and its great dykes are broken; "
                "the shah is hunted across Khurasan to die on the "
                "Caspian shore; Baylaqan in the west is razed.",
            ),
            Builder.stage(
                "Into Persia",
                year=1221,
                ignored="Balkh, Merv, Nishapur and Herat are sacked, "
                "the shah's son is driven over the Indus, and Jebe and "
                "Subadei ride north into Russia.",
            ),
            Builder.stage(
                "The Kalka",
                year=1223,
                season="Spring",
                clues="Refugee Cumans beg the Russian princes for help; "
                "Mongol envoys come with gifts.",
                ignored="Subadei, having bought off and then destroyed the "
                "Cumans, draws the princes' host into a nine-day pursuit "
                "and routes it on the Kalka: nine princes die, the Prince "
                "of Kiev smothered under a carpet for the murdered envoys. "
                "Then the Mongols ride home past the Volga Bulgars, and the "
                "Russians forget them.",
            ),
            Builder.stage(
                "The return",
                year=1237,
                season="Winter",
                clues="Mongol spies along the steppe; the princes at war over Kiev.",
                ignored="Great Bulgar is razed; in December the horde "
                "enters Ryazan, then burns Vladimir and kills the Grand "
                "Prince. Northern Russia submits in four months; Novgorod "
                "is spared by the thaw.",
            ),
            Builder.stage(
                "Kiev falls",
                year=1240,
                season="Winter",
                ignored="Chernigov and Pereyaslavl are crushed, and on 6 "
                "December Kiev is stormed and left a field of bones.",
            ),
            Builder.stage(
                "Legnica and the Sajo",
                year=1241,
                season="Spring",
                ignored="Two toumens sack Sandomierz and Krakow and destroy "
                "Henry the Pious's army at Legnica; a day later Batu and "
                "Subadei annihilate the Hungarian host on the Sajo.",
            ),
            Builder.stage(
                "The horde turns back",
                year=1242,
                season="Winter",
                ignored="Word of Ogedei's death recalls Subadei; Batu "
                "withdraws to the Volga steppe, razing as he goes, and "
                "rules Russia from Sarai.",
            ),
        ],
    )


# -- the whole set --


def middle_east(b: Builder) -> dict[str, Neighbour | Creature]:
    """Every shared record, in a fixed order, by key: "order", "stone",
    "river", "jinn", "jinnistan", "qaf", "iraq", "baghdad", "mosul",
    "georgia", "greater_armenia", "harut_and_marut", "caliph",
    "al_kamil", "al_aziz", "lord_of_mosul", "king_of_georgia",
    "nizaris", "imam", "sultan_of_rum", "emperor_of_trebizond",
    "al_khidr", "fifth_crusade", "mongol_conquest". Places are left
    outside any region; each pack sets them in its own map."""
    found: dict[str, Neighbour | Creature] = {}
    found.update(order_of_suleiman(b))
    found.update(jinn(b))
    found["iraq"] = place_iraq = iraq(b)
    found["baghdad"] = baghdad(b, place=place_iraq)
    found["mosul"] = mosul(b)
    found["georgia"] = place_georgia = georgia(b)
    found["greater_armenia"] = greater_armenia(b)
    found["harut_and_marut"] = pit_of_harut_and_marut(b, inside=place_iraq)
    found["caliph"] = caliph(b, place=place_iraq)
    found["al_kamil"] = al_kamil(b)
    found["al_aziz"] = al_aziz(b)
    found["lord_of_mosul"] = lord_of_mosul(b)
    found["king_of_georgia"] = king_of_georgia(b, place=place_georgia)
    found.update(nizaris(b))
    found["sultan_of_rum"] = sultan_of_rum(b)
    found["emperor_of_trebizond"] = emperor_of_trebizond(b)
    found["al_khidr"] = al_khidr(b)
    found["fifth_crusade"] = fifth_crusade(b)
    found["mongol_conquest"] = mongol_conquest(b)
    return found
