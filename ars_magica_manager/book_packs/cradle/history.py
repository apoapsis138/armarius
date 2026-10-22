"""The history (C3), in paraphrase: the Order of Suleiman's past, as the
book tells it (ch03, the appendix timeline, and the dates of ch07 and
ch08 that concern the sahirs), as entries in the Dar al-Hikma's own
Diary (covenants["dar_al_hikma"], order.py's), since there is no
Tribunal Diary and the Dar al-Hikma is the First Council's academy and
the Order's acting seat. From the first Umayyad summoners about 700 to
the grand vizier Kha'trazh's election about 1190: the jinn war and the
siege of Damascus, Harun's council and the First Council, al-Khayzuran's
vanishing (C24: Harun's mother, not a grand vizier), Ja'far's fall, the
founding at Yahya's prison in 805, the golden age of the houses, the
twelve viziers of Cairo, the ruling on solitary sahirs, the Iberian
split of 912 to 925 (C24), the ruling on sahirs who can be summoned,
the Fatimids, the three friends of Nishapur, Hasan-i Sabbah and Alamut,
the First and Second Crusades and Edessa, 'Umar Khayyam's death, the
guides sent to Nur al-Din and Salah al-Din, and Nasibin's emptying in
1186. Sorted by year and season (C24).

Left out: mundane events (lines in the summaries of the ruler, town or
place they concern, the region parts'), events with nothing to hang on
(the first caliphs), and the Hermetic dates of the timeline (the
Order's founding, the Sundering, Tasgillia, the Schism War, the Grand
Tribunal of 1195), which belong to the Order of Hermes's packs (C3).
No Diary entry is after 1220: the Majlis of 1220 is order.py's calendar
entry, the dated stages to come are stories.py's, and "if history
holds" dates are in the lords' summaries.

Where the book gives only a century or "about", the entry takes a year
and says so; the season, which the book almost never gives, is Summer
for the Majlis's doings (it meets each August) and Spring otherwise.
The pack has no Tribunal, so b.event (a Tribunal's Diary) is never
used."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import secrets

if TYPE_CHECKING:
    from . import Cradle

#: The order of the seasons within a year.
SEASON_ORDER = {"Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

POLITICS = "Politics"
COUNCIL = "Council"
MEMBERSHIP = "Membership"
WAR = "Defence & Magic"

#: (year, season, title, details, hidden, category): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str, str], ...] = (
    (
        700,
        "Spring",
        "The caliph's first wazirs",
        "About this time three summoners swear lifelong service to the "
        "Umayyad caliph and take the title wazir, then meaning a bearer of "
        "magic for the caliph. Distrusted at first, they prove their worth "
        "when the armies meet foreign wizards who rain fire and raise the "
        "sea, for their spirits withstand such magic. Three become thirty "
        "and thirty more than a hundred, and they learn to command jinn "
        "and lead them into battle. (The book says about 700.)",
        "",
        WAR,
    ),
    (
        720,
        "Spring",
        "War with the jinn",
        "The wazirs have treated the spirits they summon as slaves, many "
        "of them believing jinn whom the Prophet's teaching forbids "
        "enslaving. Beings of other worlds turn on them, and by about "
        "this year the wazirs are so busy defending their homes against "
        "a magical war that they can no longer help the armies, and the "
        "conquests slow and stop. The caliphs blame their people, not "
        "their wazirs. (The book says about 720.)",
        "",
        WAR,
    ),
    (
        746,
        "Spring",
        "The jinn besiege Damascus",
        "While the 'Abbasids' supporters gather in Khurasan, more than a "
        "hundred jinn are said to surround Damascus and demand two wazirs "
        "hiding inside. After many such reprisals few summoners are left, "
        "the word wazir loses its link with wizardry, and their cruel "
        "kind of summoning survives only on the empire's edges.",
        "",
        WAR,
    ),
    (
        786,
        "Spring",
        "Harun's council",
        "Harun al-Rashid becomes caliph. His mother al-Khayzuran, a "
        "Yemeni woman skilled in enchanting music and tales, urges him "
        "to gather a council of wizards to advise him and secure his "
        "rule; he wants thinkers more than warriors. His old tutor and "
        "grand vizier, Yahya ibn Khalid the Barmakid, an unGifted scholar "
        "of potions and elixirs, writes to invite the best minds of "
        "Islam.",
        "",
        POLITICS,
    ),
    (
        787,
        "Spring",
        "The First Council",
        "Five answer: Jabir ibn Hayyan, Gifted alchemist and summoner, "
        "whose discovery lets the council join its many styles into one "
        "tradition; the astrologer Muhammad al-Fazari, maker of the first "
        "armillary sphere, whose father became a spirit to guard him and "
        "showed him how to open the unGifted to the art; Bakhtyshu, a "
        "Nestorian physician admitted on trial, who earns his place by "
        "casting out a demon that plagued the caliph and teaches the True "
        "Names of hundreds of spirits; Al-Zill Habib, the cloaked "
        "outlaw-hero with a band of jinn and yatus; and Al-Hajjaj, poet "
        "and mathematician, who claims al-Khidr as his teacher and never "
        "looks older than twenty-five. With Yahya and al-Khayzuran they "
        "make a shared language of their magic and invent the five "
        "Solomonic arts, answering to the caliph alone. The house in "
        "Baghdad where they teach will become the Dar al-Hikma.",
        "",
        COUNCIL,
    ),
    (
        789,
        "Spring",
        "Al-Khayzuran vanishes",
        "The caliph's mother complains of a headache, collapses, and is "
        "carried to her rooms, where her body and belongings disappear "
        "before her son and his advisers. Yahya retires to his studies "
        "and his Gifted son Ja'far becomes grand vizier and head of the "
        "council; Harun moves his palace north, away from the sahirs, and "
        "speaks to them only through Ja'far. (The timeline calls her a "
        "grand vizier; she was the caliph's mother, and the Order had no "
        "grand vizier until 805.)",
        "Sahirs who are sensitive to spirits feel a woman's presence in "
        "her old chamber, and some say a faerie queen made of the tales "
        "about her now lives there.",
        COUNCIL,
    ),
    (
        803,
        "Spring",
        "Ja'far beheaded",
        "Harun has grown wary of Ja'far and listens to other counsellors: "
        "Christopher Coronus, a young Hermetic magus said to come from "
        "Charlemagne's court, who writes often to Tremere and once "
        "threatens Jabir with a duel; the Sufi Fozail-e Iyaz; and an "
        "eastern miracle-worker called Dawud al-Kharita. Rumour paints "
        "Ja'far as a sorcerer after the throne, and when Harun's sister, "
        "whom Ja'far loves, pleads for him, Dawud says he has bewitched "
        "her. The caliph has Ja'far executed and the Barmakids killed or "
        "jailed; Yahya is spared, in prison.",
        "Another telling makes Ja'far guilty: too ambitious for his post, "
        "he tried to make Harun adopt him and, failing to enchant the "
        "caliph, ensnared his sister instead, until Harun's other "
        "advisers foiled him.",
        POLITICS,
    ),
    (
        805,
        "Summer",
        "The Suhhar Sulayman founded",
        "Months pass with no new grand vizier, and the five surviving "
        "masters meet Yahya secretly in his prison. At his urging they "
        "found a society that governs itself, free of the court's "
        "intrigues: the Suhhar Sulayman. Its founding document admits "
        "anyone who comes with a sponsor and shows he can summon a "
        "spirit, bars neither women nor non-Muslims, asks a quarter of "
        "each member's wealth on top of zakat, and expels any sahir who "
        "holds a thinking being in thrall; everything else is left to "
        "Islamic law. Harun, assured that they do not plot against him, "
        "blesses it on condition that its sahirs remain his loyal "
        "subjects. The first Majlis meets, and its members keep calling "
        "themselves viziers and their head the grand vizier.",
        "",
        COUNCIL,
    ),
    (
        810,
        "Spring",
        "The golden age of the houses",
        "The Suhhar flourishes. The council's house in Baghdad becomes a "
        "great academy, the Bayt al-Hikma (now the Dar al-Hikma), and "
        "sahirs carry the art across Islam; great communities grow round "
        "houses of learning in Damascus, Gundeshapur, Cairo and Cordoba, "
        "each sending viziers to the yearly gathering. Being apart from "
        "the court keeps the Suhhar strong as the caliphate later "
        "splinters. Africa, central Arabia and the frontiers stay "
        "dangerous, prowled by spirits still angry at the Umayyads. (The "
        "book gives no year: the years after the founding.)",
        "",
        MEMBERSHIP,
    ),
    (
        850,
        "Spring",
        "Al-Zill and Al-Hajjaj depart",
        "After years of teaching in Baghdad, the two founders leave "
        "without warning soon after a visit from Fozail-e Iyaz, and tell "
        "their followers not to come after them. Travellers from the "
        "Pillars of Hercules to the far east later tell of sharing meals "
        "with a young man in white and a companion hooded in black. (The "
        "book says the mid-800s.)",
        "Some say the two still live, unchanged in 1220.",
        MEMBERSHIP,
    ),
    (
        868,
        "Summer",
        "Cairo's twelve viziers",
        "Cairo has so many sahirs that it sends twelve viziers to the "
        "gathering, one for every house of more than two.",
        "",
        COUNCIL,
    ),
    (
        889,
        "Summer",
        "The viziers and the solitary sahirs",
        "The grand vizier rules that each community's vizier also speaks "
        "for the sahirs living alone or in pairs nearest it, and must "
        "seek them out before every gathering. Until now most viziers "
        "had avoided the hermits, many of them Gifted and unpleasant "
        "company.",
        "",
        COUNCIL,
    ),
    (
        900,
        "Summer",
        "A sahir who can be summoned",
        "A sahir complains to the Majlis that another has learned to "
        "summon him and shared the formula with friends, who keep "
        "calling him from his studies with absurd bargains; his "
        "tormentor, made vizier for the occasion, says no law forbids it. "
        "The grand vizier rules that one who can be summoned is no longer "
        "a sahir but a supernatural being, outside the Suhhar's laws and "
        "free to take what revenge he likes. Ever since, spirits and "
        "other such beings may not be members. (The book says only the "
        "tenth century.)",
        "",
        MEMBERSHIP,
    ),
    (
        912,
        "Spring",
        "The Iberians meet at Cordoba",
        "Perhaps wary of the long journey through hostile lands, the "
        "Iberian sahirs begin holding their own gatherings at Cordoba. "
        "Baghdad sends envoys for years to talk them out of it.",
        "",
        MEMBERSHIP,
    ),
    (
        919,
        "Spring",
        "The Iberians expelled",
        "Baghdad gives up its attempts at reconciliation and expels the "
        "Iberian sahirs from the Suhhar Sulayman. Many of them had called "
        "themselves Ashab al-Halqa, for the outer ring of Solomon's Seal.",
        "",
        MEMBERSHIP,
    ),
    (
        925,
        "Spring",
        "The Iberians join the Order of Hermes",
        "The Iberian council, meeting on its own since its expulsion, "
        "votes by a majority to join the Order of Hermes. The two groups "
        "have had little to do with each other since, though many sahirs "
        "now want to learn how Hermetic magic differs from theirs. (The "
        "timeline gives only this year for the split; ch03 has it run "
        "from 912.)",
        "",
        MEMBERSHIP,
    ),
    (
        950,
        "Spring",
        "Driven from North Africa",
        "With the Fatimid caliphate's rise, rumours spread of Berber "
        "wizards fighting for it whom the sahirs' spirits cannot beat, and "
        "many sahirs flee east into Egypt; those of the frontier retreat "
        "to the cities or vanish. With the Iberians gone, the Suhhar now "
        "holds only Egypt, Arabia and Persia, and turns inward to study "
        "in peace. The Berbers press no further. (The book says the "
        "mid-900s.)",
        "",
        WAR,
    ),
    (
        1050,
        "Spring",
        "Three friends at Nishapur",
        "By the middle of the century the Suhhar's magic is the "
        "tradition it is in 1220. At Nishapur's house of wisdom three "
        "apprentices, 'Umar Khayyam, Hasan-i Sabbah and Abu 'Ali "
        "al-Tusi, swear that whichever of them becomes great will share "
        "it with the others. Al-Tusi rises to be vizier to the Seljuk "
        "sultans, as Nizam al-Mulk, and grand vizier of the Suhhar; "
        "'Umar asks only for the means to study, and is given a pension. "
        "(The book says the middle of the eleventh century.)",
        "",
        MEMBERSHIP,
    ),
    (
        1090,
        "Spring",
        "Hasan-i Sabbah at Alamut",
        "Hasan-i Sabbah takes the post his friend offers only to get "
        "close to him, being secretly an Isma'ili, and at the sect's "
        "bidding murders the grand vizier. The outraged Suhhar holds back "
        "its vengeance, as Nizam al-Mulk asked as he died, but no "
        "reconciliation is possible, and Hasan takes Alamut, where Prince "
        "Nizar has fled after a split among the Isma'ilis. There he "
        "teaches his followers Solomon's art, making a rival society of "
        "sahirs: they walk unseen, bend minds, poison and cross great "
        "distances in a moment, and the Seljuk governor cannot stop them "
        "even with the Suhhar's help. The two have tried to destroy each "
        "other ever since. (The year is the timeline's for Alamut; the "
        "book places the murder before it and gives it none.)",
        "",
        WAR,
    ),
    (
        1099,
        "Summer",
        "The Crusaders take Jerusalem",
        "The Frankish knights' sieges of Antioch and Jerusalem shock the "
        "sahirs, who had turned wholly inward and were quite unprepared; "
        "a few try to save Tyre. Those sent to watch the European wizards "
        "find most proof against Solomonic magic, and those who fight "
        "magi in the field are beaten and many killed. Most survivors "
        "decide that God was with the invaders and Jerusalem is theirs by "
        "right, but the Asala al-Sakhr calls them Hell's tools, and a "
        "party against the crusaders grows round him among the Syrian "
        "viziers. The Suhhar stays aloof in public, yet relaxes its rules "
        "on fair dealing with non-Muslim spirits and names crusading magi "
        "enemies of Islam, leaving each sahir to strike back as he sees "
        "fit. (The timeline runs the First Crusade from 1095 to 1109.)",
        "",
        WAR,
    ),
    (
        1123,
        "Spring",
        "'Umar Khayyam dies",
        "The astronomer, poet and sahir dies at Nishapur, where he trained "
        "and later led the house of wisdom, leaving books on algebra, "
        "Euclid and the stars and the poems of the Rubaiyat.",
        "",
        MEMBERSHIP,
    ),
    (
        1144,
        "Spring",
        "Edessa retaken",
        "Working in secret, sahirs teach magic to Muslim leaders, use the "
        "Magic Realm's geography to fall on the Franks' rear and plunder "
        "their camps, and read the stars for the moment to strike. Their "
        "help wins Edessa back from the crusaders when Zangi takes it.",
        "",
        WAR,
    ),
    (
        1148,
        "Summer",
        "The Second Crusade broken",
        "The same hidden war helps bring the Second Crusade to nothing "
        "before Damascus.",
        "",
        WAR,
    ),
    (
        1174,
        "Spring",
        "Guides for Nur al-Din and Salah al-Din",
        "By custom a vizier may disguise himself as a nameless old sage, "
        "as al-Khidr does, to offer magic or aid to a promising Muslim "
        "leader or scholar without committing the Suhhar: 'sending a "
        "guide'. Both great men of the late century are sent one. Nur "
        "al-Din declines, saying al-Khidr himself has taught him, and the "
        "two exchange wisdom in a famous text now kept in Baghdad; Salah "
        "al-Din refuses without a reason, and the sahirs must help him "
        "unasked. (The book says the late 1100s; this is the year Salah "
        "al-Din begins to unite the Muslim Levant.)",
        "",
        POLITICS,
    ),
    (
        1186,
        "Summer",
        "The House of the Heavens empties",
        "Soon after the vizier of Nasibin and the Asala al-Najm come home "
        "from the Majlis, they and every sahir of the city leave in a body "
        "near the end of summer, some packed and ready, some walking away "
        "from half-done work. Astrologers find that all seven planets "
        "stood in Libra then. Neither leader has been heard of since; the "
        "family's sahirs now wander in caravans with their laboratories, "
        "and Meriq of Savah, who took the Asala's place, insists the "
        "house is still at Nasibin, waiting for them to come back.",
        "Most sahirs think they scattered to help Salah al-Din win at "
        "Hattin and retake Jerusalem the next year; others, that they "
        "went to set in motion a plan to remove Rashid al-Din Sinan of "
        "the Syrian Nizaris.",
        MEMBERSHIP,
    ),
    (
        1190,
        "Summer",
        "Kha'trazh elected grand vizier",
        "The viziers elect Kha'trazh of Basra, a Follower of the Heart, "
        "who takes the laqab al-Wazir al-Dall as a pledge not to abuse "
        "his seat. They will keep him there for some thirty years. (The "
        "book says he has led the Order for nearly thirty years by 1220.)",
        "",
        COUNCIL,
    ),
)


def build(cradle: Cradle) -> None:
    """Enter every event of `EVENTS` in the Dar al-Hikma's Diary, in
    order of year and season. Nothing is written when the house has not
    been made (order.py builds before this part)."""
    house = cradle.covenants.get("dar_al_hikma")
    if house is None:
        return
    for year, season, title, details, hidden, category in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        cradle.b.chronicle(
            house,
            year,
            title,
            secrets(details, hidden),
            season=season,
            category=category,
        )
    house.diary.sort(key=lambda e: (e.year, SEASON_ORDER.get(e.season, 0)))
