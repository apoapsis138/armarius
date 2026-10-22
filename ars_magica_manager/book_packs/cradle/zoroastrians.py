"""The Mazdeans and their fire temples (TC&TC ch05, with the temples
of ch08 and ch09), in paraphrase.

World: world["mazdeans"], a faction (C12 as revised) naming the
Mobeds tradition ("trad_mobeds"; RoP:D's Zoroastrians mentioned in the
summary): the ranks (ervad, mobed, dastur), the heresies (Zurvanites,
Mazdakites, the cult of Mithras), the communities of Yazd (and its six
pirs), Kirman and Daylam, the mobed at Sirishk and the hidden one at
Naw Bahar; the grades of fire, the rites and the calendar described,
not as rules (no calendar entries); the Ameshaspand, yazdan and chief
daevas named; the Avesta texts' and the Shahnameh's scores in the
summary, since a Book record needs a holder (C18); the Staff of Yoisht
Frayana, which the book gives no keeper, in the summary too (C23). No
living priest is named, so no characters. It sits in world["yazd"],
its open stronghold (else places["persia"]).

Places, each inside the region part's province or town it lies in
(found with cradle.find, set again in finish if not made yet; see
INSIDE): the three Royal Fires, each a place with a Divine regio level
of 8 and its boon: places["adur_farnbag"] (on Mount Kavarvand, Fars),
["adur_gushnasp"] (Takht-i-Suleiman, Jibal), ["adur_burzen_mihr"] (the
village of Mihr, on the Nishapur road, Khurasan); places["naw_bahar"]
(Divine 5, in Balkh, its hidden community in the regio's higher
levels), ["mount_khajeh"] (Lake Zarah, Divine 2, Seistan),
["kishmar_cypresses"] (Divine 1, Calm, Quhistan), ["yazd_pirs"] (the
six mountain shrines of Yazd) and ["sirishk"] (Herat's fire temple,
with its living mobed). The faction links to each, and in finish to
Azi Dahak (creatures["azi_dahak"], bestiary.py's), the yatus
(world["yatus"]) and the Order (world["order"]) when they are there.
The Black Man div near Shapur and Isma'il Samanid's tomb are the
region parts'. Story seeds are stories.py's (C22), which can hang them
on these keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import Builder, paragraphs, secrets

if TYPE_CHECKING:
    from . import Cradle

DIVINE = "Divine"
MOBEDS = "trad_mobeds"

#: Where each of this part's records sits: its key, then the keys to
#: try in turn for what holds it (the region parts' towns and
#: provinces, then their region).
INSIDE: dict[str, tuple[str, ...]] = {
    "adur_farnbag": ("fars", "persia"),
    "adur_gushnasp": ("jibal", "persia"),
    "adur_burzen_mihr": ("khurasan", "persia"),
    "naw_bahar": ("balkh", "bactria", "silk_road"),
    "mount_khajeh": ("seistan", "khurasan", "persia"),
    "kishmar_cypresses": ("quhistan", "khurasan", "persia"),
    "yazd_pirs": ("yazd", "persia"),
    "sirishk": ("herat", "khurasan", "persia"),
    "mazdeans": ("yazd", "persia"),
}
#: The faction's links to its temples: place key, note.
TEMPLES: tuple[tuple[str, str], ...] = (
    ("adur_farnbag", "The Royal Fire of the priests"),
    ("adur_gushnasp", "The Royal Fire of the warriors"),
    ("adur_burzen_mihr", "The Royal Fire of the farmers and craftsmen"),
    ("naw_bahar", "Its great temple, and a hidden community"),
    ("mount_khajeh", "Zoroaster's lake"),
    ("kishmar_cypresses", "Zoroaster's cypress and its seedlings"),
    ("yazd_pirs", "Its pilgrim shrines"),
    ("sirishk", "A temple with a mobed still in it"),
)


def build(cradle: Cradle) -> None:
    _temples(cradle)
    _mazdeans(cradle)
    _settle(cradle)


def finish(cradle: Cradle) -> None:
    """Put whatever is still nowhere in the place another part has made
    since, and link the faction to the other parts' records."""
    _settle(cradle)
    b = cradle.b
    mazdeans = cradle.world["mazdeans"]
    for key, kind, note in (
        ("azi_dahak", "creatures", "The serpent-demon a temple's flame repels"),
        ("yatus", "places", "Old enemies: the mobeds' purges broke them"),
        ("order", "places", "Strained: a few mobeds became sahirs"),
        ("nizaris", "places", "Rivals for Daylam's rulers"),
    ):
        found = cradle.find(key)
        if found is not None:
            b.link(mazdeans, kind, found, note)


def _settle(cradle: Cradle) -> None:
    for key, holders in INSIDE.items():
        record = cradle.places.get(key) or cradle.world.get(key)
        if record is None or record.place_id is not None:
            continue
        held = next(
            (found for k in holders if (found := cradle.find(k)) is not None), None
        )
        if held is not None:
            record.place_id = held.id


# -- the temples --


def _temples(cradle: Cradle) -> None:
    b, p = cradle.b, cradle.places
    p["adur_farnbag"] = b.place(
        "Adur Farnbag",
        realm=DIVINE,
        levels=[
            Builder.level(
                "The temple of the Royal Fire",
                8,
                DIVINE,
                see="Holy flame streams out of the mountainside where the "
                "way stands open.",
                enter="The way opens on the mountain's west face at "
                "dawn and on its east face at dusk.",
                notes="A terrestrial Divine regio holding the fire temple "
                "of Adur Farnbag. An ervad or any higher initiate adds his "
                "Theology: Zoroastrian (the book's Theology: Mazdean) to "
                "every Ability and magic roll he makes inside it. A temple "
                "fire kindled from this flame gains a further +1 to its "
                "Divine aura.",
            )
        ],
        summary=paragraphs(
            "The first of the three Royal Fires of the Mazdeans, on Mount "
            "Kavarvand in Fars, called the shining mountain for the holy "
            "fire that spills from its slopes. The Royal Fires are held "
            "to have been lit before the world was made and carried out "
            "on the back of the ox Srishok to spread the faith and guard "
            "mankind. Adur Farnbag, the fire of the priests, is counted "
            "the holiest of the three, the earthly image of the yazata "
            "Atar who burns before Ohrmazd. It first burned in Khwarazm "
            "and was later brought here. Mazdeans still come to the "
            "mountain as pilgrims.",
            "Its temple stands in a regio of Divine 8; the book gives the "
            "mountain itself no aura.",
        ),
        secrets=paragraphs(
            "The mobeds who brought the fire from Khwarazm still live on "
            "Kavarvand, kept alive across the centuries by the Gifts of "
            "Gayomart.",
        ),
    )
    p["adur_gushnasp"] = b.place(
        "Adur Gushnasp",
        realm=DIVINE,
        levels=[
            Builder.level(
                "The temple of the Royal Fire",
                8,
                DIVINE,
                enter="The temple's own walls are the regio's bounds.",
                notes="A weapon forged at a fire lit from Adur Gushnasp and "
                "quenched in the lake gives +4 to calls on God's aid in "
                "battle (RoP:D) whenever the warrior it was made for "
                "fights with it, for as many years as his Theology: "
                "Zoroastrian. In anyone else's hand it loses the gift for "
                "good.",
            )
        ],
        summary=paragraphs(
            "The second Royal Fire, the fire of warriors and nobles, at "
            "Takht-i-Suleiman, the Throne of Solomon, in a half-moon "
            "valley in the mountains of Jibal. A small, deep lake fed by "
            "a spring from below fills the top of a low flat hill, and on "
            "its shore stands a fire temple in remarkably good repair, "
            "whose walls are also the edges of a Divine regio of 8 where "
            "the fire rests.",
            "The book gives the hill no aura of its own.",
        ),
    )
    p["adur_burzen_mihr"] = b.place(
        "Adur Burzen-Mihr",
        realm=DIVINE,
        levels=[
            Builder.level(
                "The temple of the Royal Fire",
                8,
                DIVINE,
                see="Outside, only a ruined temple.",
                enter="Through the ruins of the fire temple.",
                notes="Here the temple is whole and the holy flame burns. "
                "A tool left in the regio for a year is purified and gives "
                "+4 to its owner's Craft or Profession rolls made with it, "
                "for as many years as his Theology: Zoroastrian; if anyone "
                "else so much as touches it, it loses its purity for ever.",
            )
        ],
        summary=paragraphs(
            "The third Royal Fire, the fire of farmers and craftsmen, in "
            "Mihr, a plain village on the road to Nishapur. The ruins of "
            "an old fire temple hide the way into a Divine regio of 8, "
            "where the temple still stands and the fire burns.",
            "The book gives the village no aura of its own.",
        ),
    )
    p["naw_bahar"] = b.place(
        "Naw Bahar",
        realm=DIVINE,
        aura=5,
        levels=[
            Builder.level(
                "The temple within",
                6,
                DIVINE,
                see="A fire burning at the temple's heart, with no one tending it.",
                enter="By going into the temple and on towards its fire.",
                notes="The first level of a terrestrial Divine regio "
                "reached through the temple; the book numbers none of its "
                "levels.",
            ),
            Builder.level(
                "The hidden community",
                7,
                DIVINE,
                notes=secrets(
                    "The higher levels of the regio.",
                    "A small community of Mazdeans lives here, out of "
                    "the world's reach.",
                ),
            ),
        ],
        summary=paragraphs(
            "A fire temple in a suburb of Balkh, the city where Zoroaster "
            "was born and lies buried, built under the Sasanids to rival "
            "the Ka'ba at Mecca. Precious stones stud its walls, brocade "
            "curtains hang everywhere, and centuries of anointing have "
            "left the walls and floors smelling sweetly of perfume. A "
            "cupola 375 feet high crowns the main hall, and 360 chambers "
            "for its mobeds ring it.",
            "It is no longer a working temple, yet it keeps a Divine aura "
            "of 5, and neither time nor treasure-hunters have touched it; "
            "its floors stay clean of dirt and vermin. The few who dare to "
            "go in say a fire burns at its centre, though no one is ever "
            "seen there.",
        ),
    )
    p["mount_khajeh"] = b.place(
        "Lake Zarah and Mount Khajeh",
        realm=DIVINE,
        aura=2,
        summary=paragraphs(
            "The lake of Seistan, near Zaranj, whose waters carry a Divine "
            "aura of 2. The Nestorians say the three magi set out for "
            "Bethlehem from its shores; the Mazdeans that it keeps the "
            "seed of Zoroaster, and that when the world's renewal draws "
            "near three virgins will go into it and bear the saviours of "
            "mankind.",
            "Out of the water rises Mount Khajeh, a flat-topped black hill "
            "with an ancient fire temple and two deserted forts, together "
            "called Qal'a-e Sam after Saum, Rostam's grandfather.",
        ),
    )
    p["kishmar_cypresses"] = b.place(
        "The Cypresses of Kishmar",
        realm=DIVINE,
        aura=1,
        summary=paragraphs(
            "At Kishmar near Turshiz Zoroaster planted a cypress grown "
            "from a branch he had carried from Paradise, to mark King "
            "Goshtasp's conversion; it outgrew every cypress there had "
            "ever been. In 861 the caliph al-Mutawakkil had it pulled up "
            "and hauled across Persia for beams in his new palace, and "
            "was killed the very day it arrived.",
            "Several cypresses in Quhistan are said to have grown from its "
            "seed, and some truly have. Each has a Divine aura of 1 out to "
            "five paces, tempered with Calm (RoP:D). Fallen branches fed "
            "to a Mazdean temple's sacred fire raise that temple's aura "
            "by 1 for as long as they burn; wood cut from the trees does "
            "not.",
        ),
    )
    p["yazd_pirs"] = b.place(
        "The Pirs of Yazd",
        realm=DIVINE,
        aura=3,
        summary=paragraphs(
            "Six holy shrines in the mountains around Yazd, the heart of "
            "the faith since Persia became Muslim and one of the few lands "
            "where Mazdeans still worship openly. Each year the "
            "Zoroastrian villages go to them on pilgrimage together, an "
            "occasion as much for feasting and dancing as for prayer.",
            "The book names none of the six and gives them no aura; they "
            "take the Divine 3 this pack gives a holy place left "
            "unnumbered.",
        ),
    )
    p["sirishk"] = b.place(
        "Sirishk",
        realm=DIVINE,
        aura=3,
        summary=paragraphs(
            "A Zoroastrian fire temple on a hilltop two leagues north of "
            "Herat. Unusually, a mobed still lives and serves in it, and "
            "the faithful come up from the hills around to worship. "
            "Shamiran castle, just behind the temple, may be part of why "
            "it has lasted. A Nestorian church stands between it and the "
            "city.",
            "The book gives it no aura; it takes the Divine 3 this pack "
            "gives a holy place left unnumbered.",
        ),
    )


# -- the faith --


def _mazdeans(cradle: Cradle) -> None:
    b = cradle.b
    mazdeans = cradle.world["mazdeans"] = b.faction(
        "The Mazdeans",
        faction="Other",
        decides="A council",
        realm=DIVINE,
        tradition=MOBEDS,
        rules="A hereditary priesthood of men; constant ritual purity; "
        "a sacred fire must never go out or be fouled.",
        wants="To keep their fires alight and their faith alive at the "
        "edge of the Muslim world.",
        offers="Purification, the lore of the old magi, and True Names.",
        summary=paragraphs(
            "The followers of Zoroaster, who worship Ohrmazd, the Wise "
            "Lord, and hold to good thoughts, good words and good deeds. "
            "Their priests, the mobeds, gave their Greek name of magoi to "
            "magic itself: once they commanded angels and spirits, read "
            "the heavens and turned one substance into another, and at "
            "their height may have nearly matched Hermetic magic. Little "
            "is left. Zoroaster, born more than six centuries before "
            "Christ, converted the emperor Vishtaspa and was murdered by "
            "Turanian warriors at prayer in a fire temple at Balkh; his "
            "disciple Osthanes spread the faith through Persia. Alexander "
            "burned its temples and books, the Sasanids raised it again "
            "and, under the high priests Tansar and Kartir, gave it a "
            "Church with a hierarchy, which put down rival faiths; the "
            "Arab conquest broke that Church for good, though the "
            "priesthood survived. Muslims count the Mazdeans people of "
            "the book and dhimmis, and Zoroaster a prophet, yet call them "
            "gabars and fire-worshippers and press them to convert. Most "
            "who held out have gone to the poor, remote south-centre of "
            "Persia, and more drift east every year.",
            "Where they are. Yazd, where the faith is still openly kept, "
            "its six mountain pirs drawing yearly pilgrimages and its "
            "mobeds credited with the fertile land round the city; "
            "secretive villages in Kirman, which keep their heads down "
            "after hard persecution; Daylam, a stronghold of the faith "
            "where its mobeds, the Nizaris and the yatus of Damavand "
            "fight over vis, rulers and souls, and which holds Hyrcania's "
            "plenty to be Ohrmazd's gift; scattered believers in "
            "Azarbayjan; the one living mobed of Sirishk near Herat; and "
            "a hidden community in the regio of Naw Bahar at Balkh. With "
            "the Order of Suleiman relations have always been strained: "
            "a few Persian priests became sahirs, and the mobeds' purges "
            "of the Goetic yatus long ago ended the old Persian art of "
            "magical war.",
            "The priesthood. It passes from father to son, its priests "
            "marry, and it has no single head, so it settles doctrine as "
            "a college. An ervad performs the ordinary services; the "
            "martab ceremony makes him a mobed, who may perform them all; "
            "a dastur leads the priests of a district or a great temple "
            "(the Senior Clergy Virtue). The higher ranks are lost. Few "
            "mobeds have The Gift, many have True Faith, and only full "
            "mobeds wield holy power; a mobed who has the Ameratat gift "
            "can live about two hundred years, as the high priests "
            "Vishtana, Tansar and Kartir and Osthanes, the first Prince of "
            "Magi, did. Their holy magic, Mysteries and initiations are "
            "the Mobeds tradition's chapter; RoP:D's Zoroastrian holy "
            "magi, and the small Hermetic mystery cult of Zoroastrian "
            "magi, are kin to them.",
            "Fire and the Dominion. Fire is the sign of Ohrmazd's "
            "presence and of truth, kept burning always on clean dry wood "
            "in an iron urn on a stone dais in a square, vented temple, "
            "fed and prayed over five times a day. A household lamp or "
            "hearth (atesh dadgah) raises the Divine aura by 1, to at "
            "most 3; the atesh adaran, joined from four fires, by 3, to at "
            "most 5; the atesh Behram, joined from sixteen, by 6, to at "
            "most 10. The aura is strongest at the flame and fades to the "
            "temple's walls and the community's fields, and where "
            "Mazdeans live among Muslims or Christians it is likely to be "
            "in Schism. The daily Yasna lifts the aura round the fire by "
            "3 for an hour, to at most 8.",
            "The rites. The Bareshnum, ten days of washing with sand, "
            "water and consecrated bull's urine before two priests and a "
            "dog, which everyone undergoes once and which gives one Faith "
            "Point the first time; the daily Padyab ablution; the Nahn "
            "bath and the Riman for those who have handled the dead; "
            "every purification but the Padyab drives out a possessing "
            "spirit and ends any temporary non-Divine effect. The "
            "Videvdat service from midnight to dawn; birth lamps that "
            "raise a room's aura by 1, to at most 3; the Navjote, which "
            "gives a child of twelve to fifteen the sacred cord and shirt "
            "and a Faith Point, and puts his name beyond use as a True "
            "Name; marriage, which gives both a Faith Point; and the "
            "dakhma, the Tower of Silence, after which no magic can touch "
            "the soul. Haoma, the sacred plant, helps potions of health, "
            "fertility, spirit-sight and long life.",
            "The calendar. Twelve months of thirty days, each day and "
            "month sacred to a divine being, five extra days, and no "
            "week. With no leap year the dates have slipped, so "
            "communities keep either the Shenshai (Imperial) or the Fasli "
            "(Ancient) reckoning. Seven festivals of five days honour the "
            "Ameshaspand, the greatest No Roz, the New Day, which in 1220 "
            "falls on 27 January (Shenshai) or 26 February (Fasli). While a "
            "festival lasts, a temple's aura bars any Infernal being "
            "whose Might is under ten times the aura, and wounds one that "
            "gets in each hour by the aura's score, unsoakable on the last "
            "day. Their astrologers count a World Year of twelve thousand "
            "years, with a second saviour due about 1350.",
            "Holy and unholy beings. Ohrmazd is the one God of every "
            "faith of Abraham. Under him are the seven Ameshaspand, "
            "archangels of his aspects: Vohu Manah (Bahman), Asha "
            "(Asavahisht), Khshathra Vairya (Shahrevar), Spenta Armaiti "
            "(Spendarmad), Haurvatat (Hordad), Ameretat (Amurdad) and "
            "Spenta Mainyu; then forty named yazdan, among them Mithras, "
            "Haoma, Atar and Vayu, who may be invoked like saints by one "
            "made pure by the Nahn; and the frohar, the guardian spirits "
            "of all good things, who lead the dead to the Chinvat Bridge. "
            "Against them stands Ahriman, the Devil himself, with the "
            "daevas Aka Manah, Indra, Saura, Naonghaithya, Taurvi and "
            "Zairich and forty-five lesser named demons. The faith keeps "
            "no relics in the Christian way, but many holy objects carry "
            "Faith scores; the greatest is the Staff of Yoisht Frayana, "
            "who answered all ninety-nine riddles of the sorcerer Akhtya "
            "and sent him to Hell: Faith 5, with the powers Grant "
            "Serenity, Expel Demons, Celestial Immunity and Acknowledgement "
            "of Evil (RoP:D). The book "
            "names no one who holds it.",
            "Heresies. The Zurvanites, who gave Ohrmazd a father, Zurvan "
            "or Time, and called free will an illusion; the Mazdakites, "
            "ascetics vowed to poverty; and the cult of Mithras, strong in "
            "the empire's western provinces after Alexander. None "
            "survives in 1220, but their relics and monuments may.",
            "Scriptures. The priests carry the Avesta in memory; temples "
            "hold parts of it, in Avestan and Gathic (Dead Language: "
            "Avestan reads both). The Yasna, the chief liturgy: Summa on "
            "Theology: Zoroastrian, Level 9, Quality 4. The Visparad: "
            "Summa on Dominion Lore, Level 4, Quality 3. The Videvdat, the "
            "law against demons: Summa on Theology: Zoroastrian, Level 6, "
            "Quality 6. The Khordeh Avesta and the Yasht: each a Tractatus "
            "on Theology: Zoroastrian, Quality 6. Also named: the Dadistan "
            "i Menok i Khrat, which says astrology came from the Spirit of "
            "Wisdom to Zoroaster, and the Arda Viraz Namag. Ferdowsi's "
            "Shahnameh, the Persian epic, in Parsi and seven volumes: a "
            "fine copy serves as a Persian Lore Summa of Level 4 and Quality 12, "
            "and a Tractatus, Quality 10, on each of Magic, Faerie, "
            "Divine and Infernal Lore. The book's Theology: Mazdean is "
            "the catalog's Theology: Zoroastrian, and its Mobed Lore is "
            "Organization Lore: Mobeds.",
        ),
        secrets=paragraphs(
            "The mobeds who carried Adur Farnbag from Khwarazm to Mount "
            "Kavarvand are still alive there, through the Gifts of "
            "Gayomart, and a living Mazdean community shelters in the "
            "higher levels of Naw Bahar's regio. The most devout mobeds "
            "still know the rite of Saoshyant's Elixir, the faith's road "
            "to a life without end.",
        ),
    )
    for key, note in TEMPLES:
        b.link(mazdeans, "places", cradle.places[key], note)
