"""Persia and Khurasan (TC&TC ch08, with the shah's history from ch02
and the timeline), in paraphrase.

Places: the region places["persia"] (no `inside`), and its provinces
places["fars"], ["jibal"], ["khuzistan"], ["kirman"], ["mazandaran"]
(with Hyrcania's vis-hunting rules summarised and suggested vis
sources, C17), ["daylam"], ["qumis"], ["great_desert"] (with
["dasht_i_kavir"] and ["dasht_i_lut"] inside it), ["makran"] and
["khurasan"], with Khurasan's districts ["seistan"], ["quhistan"] and
["ghur"] inside it. The sites, by slug: ["well_of_hindijan"],
["salt_of_seven_colours"] (Darabgerd), ["kamfiruz"] (the lions' oak
wood), ["shiraz_shrines"] (the imamzadihs), ["black_man"] (the bound
div near Shapur), ["jam_karan"] (Divine 7), ["rayy_spring"] (Aquam
vis), ["jiruft_forest"] (the lion-shah's Faerie wood), ["damavand"]
(the Simurgh, Zahhak beneath, the seven closed yatu houses),
["baghl_cave"] (Baghl's cave in the Elburz, its yearly Terram),
["gurgan_wall"] (Magic 5, and its breach), ["alamut"] (Magic 3, its
garden's way into the Magic Realm, and the named Nizari castles of
Daylam, Quhistan, Qumis and Fars listed, C14), ["maimun_diz"],
["girdkuh"], ["caspian_gates"], ["rig_i_jinn"] (Faerie 3, moving),
["gandom_beriyan"] (Infernal 4, a Tartaran level 7),
["gedrosian_desert"] (its ghosts), ["rostam_tower"] (Zaranj),
["imam_reza_shrine"] (Divine 6), ["footsteps_of_reza"],
["bamiyan_idols"] and ["firuzkuh_minaret"]. The Royal Fires, Naw
Bahar, Mount Khajeh, the Kishmar cypresses, Sirishk and the Yazd pirs
are zoroastrians.py's; the Savah observatory and the House of Healing
are order.py's.

Towns (world): ["savah"], ["gundeshapur"], ["ramhurmuz"], ["merv"],
["nishapur"] (order.py puts houses of wisdom there: the keys are
kept), ["shiraz"], ["isfahan"], ["yazd"], ["rayy"], ["qum"],
["mashhad"], ["herat"], ["zaranj"], ["ghazni"], ["kabul"],
["arranjan"], ["darabgerd"], ["kajaran"], ["istakhr"] (the Cup of
Jamshid), ["kish"], ["shapur"], ["kirmanshah"], ["ahwaz"],
["bardasir"], ["jiruft"], ["gurgan"], ["damghan"], ["dartal"],
["bamiyan"] and ["firuzkuh"].

Lords (C13, the title left blank and the real one in the name):
world["khwarazm_shah"] (Ala al-Din Muhammad; his envoys' deaths,
Genghis's war and "if history holds" dates in the summary; silk_road
sets his place in Khwarazm), ["salghurids"] (the atabegs of Fars, at
Shiraz) and ["ghuzz_atabeg"] (Khuzistan, answering to the shah, as the
book says). East.py's world["nizaris"] and ["imam"] are not remade:
their place is set to Alamut when they have none.

Factions with no tradition record (C15): world["yatus"], ["ghuzz"],
["shansabani"] (the heir under secrets=), ["zutt"], ["balu"],
["peris"] (the peris and pairikas) and ["isfahan_guilds"] (the
carpet-weavers, Dadvand and the Yarankush). Relics (C23): the Cup of
Jamshid in Istakhr's summary, Rostam's tiger skin in Ghur's, his
bones in his tower's (his mace is in silk_road's Shahr-i-Zindah).
Creatures with stats (Azi Dahak, the Simurgh, Baghl, the nasu, the
Hyrcanian tiger, the olghoi khorkhoi, the gazelle) are bestiary.py's;
beings without stats are sentences at their places. Vis sources are
lines in their places' summaries (C17). The book's story seeds are
stories.py's to add in its finish (C22): the records they hang on are
here (Hindijan's well, Kajaran, Darabgerd, Shiraz's shrines, Herat,
Merv, the footsteps of Reza, the Gurgan wall and so on)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs, titled

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Cradle

RUMOURED_LOCALLY: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}


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
    _region(cradle)
    _lords(cradle)
    _fars(cradle)
    _jibal(cradle)
    _khuzistan(cradle)
    _kirman(cradle)
    _mazandaran(cradle)
    _desert_and_makran(cradle)
    _khurasan(cradle)
    _ghur(cradle)
    _factions(cradle)
    _shared(cradle)


def finish(cradle: Cradle) -> None:
    """Link to what the later parts have made, skipping what is missing."""
    _shared(cradle)
    b, w = cradle.b, cradle.world
    azi_dahak = cradle.find("azi_dahak")
    if azi_dahak is not None:
        b.link(w["shansabani"], "creatures", azi_dahak, "Their forefather's demon")
        b.link(cradle.places["damavand"], "creatures", azi_dahak, "Zahhak's demon")
    genghis = w.get("genghis_khan")
    if genghis is not None:
        b.link(w["shansabani"], "places", genghis, "Their heir, by rumour")
        b.link(w["khwarazm_shah"], "places", genghis, "His enemy")
    conquest = w.get("mongol_conquest")
    if conquest is not None:
        b.link(w["khwarazm_shah"], "places", conquest, "The war he brought on")


def _shared(cradle: Cradle) -> None:
    """The Nizaris and their head sit at Alamut, when no part has placed
    them; their text is east.py's and is not changed."""
    alamut = cradle.places["alamut"]
    for key in ("nizaris", "imam"):
        record = cradle.world.get(key)
        if record is not None and record.place_id is None:
            record.place_id = alamut.id


# -- the region --


def _region(cradle: Cradle) -> None:
    _place(
        cradle,
        "persia",
        "Persia",
        summary=paragraphs(
            "The lands from the Tigris east to the Oxus: a high plateau "
            "some four or five thousand feet up, ringed by the Alborz in "
            "the north and the Zagros in the south and west, seven parts "
            "in ten of it desert or waste. Only the Gulf coast below the "
            "Zagros and the Caspian shore, a little under sea level, lie "
            "low. The plateau's rivers find no sea and die in sand or "
            "marsh, so the farmers, most of them tenants sharing their "
            "harvest with landlords who live in the towns, depend on "
            "qanats, underground channels that want constant, skilled "
            "upkeep. The Lurs of the Zagros and the Ghuzz of Khurasan "
            "are its chief nomads.",
            "Its people speak Parsi, a tongue unlike the region's other "
            "languages; Arabic keeps its place in religion, but most "
            "secular books are now written in Persian, and Turkish "
            "dialects have spread among the Ghuzz and the Lurs since the "
            "Seljuks. The provinces are held by atabegs, once the tutors "
            "of Seljuk princes and now princes in their own right, or by "
            "mamluks, slave soldiers set over a land as the sultan's "
            "direct servants; nearly all have sworn to the Khwarazm-shah.",
            "The Seljuks held Persia for almost two hundred years, an "
            "empire of two halves with a sultan of Khurasan in the east. "
            "That sultanate ended in 1149, when the Shansabani broke "
            "Seljuk rule there with Infernal help; the Ghuzz, settled in "
            "Persia as soldiers, rose in Khurasan in 1151 and held "
            "Sultan Ahmed Sanjar prisoner for more than three years. "
            "Tekish of Khwarazm rose on the empire's decline and beat "
            "Togril III in 1194; his son is the shah of 1220.",
            "Besides the Order of Suleiman, whose sahirs are in every "
            "city, five supernatural powers matter here: the yatus, the "
            "mobeds, the Nizari Isma'ilis, the Ghuzz and the "
            "Shansabani, with the peris and pairikas all over the land. "
            "The Shahnameh, Ferdowsi's tenth-century Epic of Kings, is "
            "its people's own story, from the making of the world and "
            "the first crafts through the heroes Saum, Zal and Rostam "
            "to Alexander, the Sasanids and the Arab conquest. A fine "
            "illuminated copy, in Parsi and often seven volumes long, is "
            "a summa of Persian Lore at level 4, Quality 12, and can be "
            "read as four tractatus, on Magic, Faerie, Divine and "
            "Infernal Lore, of Quality 10 each.",
            "Zahhak, the demon king of the heroic age who sawed Jamshid "
            "in two and ruled a thousand years from Ctesiphon until the "
            "hero Feridun ended his reign, is not one man but whoever "
            "the demon Azi Dahak possesses: a black snake grows from "
            "each of the host's shoulders, regrows when cut, and hungers "
            "for human brains. The demon first drives his host to evil "
            "and then corrupts him with promises until he learns the "
            "Goetic Arts; no host has yet resisted. Persian sahirs have "
            "fought several Zahhaks since; the last was the Shansabani "
            "sultan Mohammed al-Ghuri, beaten fourteen years ago, and "
            "some sahirs fear Genghis Khan is, or is counselled by, "
            "another.",
            "The disease rishtah, which the Latins call dracunculus, is "
            "common in Khurasan under Mars: worms in a limb whose hot "
            "poison swells and paralyses it, most often a leg (Lame "
            "until cured), sometimes an arm or an eye. It is a Serious "
            "Choleric disease of Severity 12, Stable 4, Recovery 18, "
            "with an interval of a month. The Ghuzz cure it by burying "
            "the limb in hot sand from dawn to dusk, and the worm that "
            "creeps out sometimes lives on to become an olghoi "
            "khorkhoi.",
        ),
    )
    p = cradle.places["persia"]
    _place(
        cradle,
        "fars",
        "Fars",
        inside=p,
        summary=paragraphs(
            "The cradle of the Achaemenid and Sasanid dynasties, which "
            "gave its old name, Parsa, Hellenised as Persis, to the "
            "whole land. It is an atabegate of the Salghurids, who rule "
            "from Shiraz. Its climate splits it in two: the Garmsir, the "
            "hot lowlands by the Gulf, and the Sardsir, the cold uplands "
            "to the north; the desert of Mandistan lies in its "
            "south-west. Its five great cities are Arranjan, Shiraz, "
            "Darabgerd, Istakhr and Shapur. The Nizaris keep hidden "
            "communities in the southern Zagros here, among them the "
            "fortress of Shardiz.",
        ),
    )
    _place(
        cradle,
        "jibal",
        "Jibal",
        inside=p,
        summary=paragraphs(
            "The Arabs' 'mountains', ruled by the Zagros, which cross "
            "its southern quarter from north-west to south-east. Its "
            "four great cities, Hamadan, Qazvin, Kirmanshah and Isfahan, "
            "have each housed a dynasty or a conqueror in their turn, "
            "and Isfahan, the largest, has always done well. South of "
            "Hamadan the Lurs, half nomads, herd goats in the emirate "
            "of Luristan. The Khurasan Road runs through it from Baghdad "
            "by Kirmanshah, Hamadan and Rayy and on through the Caspian "
            "Gates into Qumis.",
            "It is one of Persia's most crowded provinces and has sahirs "
            "to match: one is often seen borne through the air on a "
            "whirlwind of a jinni's making, or on one of Isfahan's "
            "flying carpets. The Vulture Hills and the Black Hills west "
            "of Isfahan, Kargas Kuh and Siyah Kuh, are the plain's "
            "highest and grimmest peaks and a robbers' haunt; between "
            "them the caravanserai of Dayr al-Jiss keeps four great "
            "tanks filled, by the sultan's order, for those crossing the "
            "Dasht-i Kavir.",
        ),
    )
    _place(
        cradle,
        "khuzistan",
        "Khuzistan",
        inside=p,
        summary=paragraphs(
            "Persia's oldest settled land, the Elam of Babylon's day, "
            "lying in the basin of the Karun, which comes down from the "
            "Zagros. Its well-watered plains grow sugar cane, and its "
            "rivers, all of them navigable, have been cut into canals "
            "for fields and towns. Lurs roam its north. A Ghuzz atabeg "
            "of the Hazarasp family, sworn to the Khwarazm-shah, rules "
            "it from Ahwaz.",
        ),
    )
    _place(
        cradle,
        "kirman",
        "Kirman",
        inside=p,
        summary=paragraphs(
            "Part of Persia on paper, nearly independent in fact. The "
            "Ghuzz crossed the desert and took it some fifty years ago, "
            "but their rule fell apart, since no Ghuzz will be ruled, "
            "and they have joined the Khwarazm-shah's army, which now "
            "occupies the province. It is mostly steppe and half "
            "desert, known for oranges, dates and pistachios, and "
            "shelters several Mazdean communities who keep their heads "
            "down after past persecution. The Jabal Kufs, south of the "
            "Dasht-i Lut, take up a quarter of it and are the Balu's "
            "country. Bardasir and Sirjan are its trading towns.",
        ),
    )
    _place(
        cradle,
        "daylam",
        "Daylam",
        inside=p,
        summary=paragraphs(
            "Highlands lying across Gilan and Mazandaran, a country of "
            "their own in all but name. In the tenth century Daylam held "
            "Gilan, Tabaristan, Gurgan and Qumis; now those are ruled "
            "apart and Daylam is a people more than a place. The Alborz "
            "cut it off from the plateau, and its fiercely independent "
            "folk held out against Sasanids and Arabs and were among the "
            "last Persians to take Islam. Zoroastrianism is still fairly "
            "strong here, living uneasily beside the Isma'ilis, whose "
            "fifty castles in Daylam are led by Alamut; Maimun-Diz is "
            "the strongest and Lamasar the most remote.",
        ),
    )
    _place(
        cradle,
        "qumis",
        "Qumis",
        inside=p,
        summary=paragraphs(
            "A province in the eastern Alborz, south of Tabaristan. "
            "Damghan, its chief town, is about the only place in it the "
            "Isma'ilis do not hold, and its emir lives besieged in his "
            "own land, treading softly with subjects any of whom may be "
            "a Nizari. The sect runs Qumis from the mountain fortress of "
            "Girdkuh. The road from Rayy to Nishapur crosses it through "
            "the Caspian Gates.",
        ),
    )
    _place(
        cradle,
        "great_desert",
        "The Great Desert",
        inside=p,
        summary=paragraphs(
            "Al-Mafazah, the Wilderness: Persia's dry heart, which is in "
            "truth two deserts, the Dasht-i Kavir in the north and the "
            "Dasht-i Lut in the south. No province owns it. Outlaws "
            "shelter there, and apart from its three oases (Garmah, "
            "Naband and Sanij) nobody lives in it for good. The roads "
            "across it have domed water tanks every three or four "
            "leagues, which merchants do well to keep filled, and both "
            "deserts are full of jinn.",
        ),
    )
    _place(
        cradle,
        "makran",
        "Makran",
        inside=p,
        summary=paragraphs(
            "The coast towards Al-Sind, named for its fish-eaters (mahi "
            "khoran) and thinly peopled in fishing villages. Its capital "
            "Fannazbur is poor beside the cities of the other "
            "provinces, and the port of Tiz is a halt between Al-Sind "
            "and Fars. The caliphs and the kings of Al-Sind once fought "
            "over it, and the war elephants taken from Al-Sind went into "
            "the Persian army. Bands of Ghuzz left from the invasion of "
            "Kirman still roam it.",
        ),
    )
    _place(
        cradle,
        "khurasan",
        "Khurasan",
        inside=p,
        summary=paragraphs(
            "The greatest province of Persia, the land where the sun "
            "(khor) rises. Long a sultanate of its own, it is now firmly "
            "part of the Khwarazm-shah's empire; Seistan, Quhistan and "
            "Ghur are its districts, not provinces. Merv, Nishapur, Herat "
            "and Mashhad are its great cities. The Karakum, the black "
            "sand or Desert of the Ghuzz, lies between the Caspian and "
            "the Aral Sea, bounded on the north-east by the Oxus.",
        ),
    )
    k = cradle.places["khurasan"]
    _place(
        cradle,
        "seistan",
        "Seistan",
        inside=k,
        summary=paragraphs(
            "Low country round and east of Lake Zarah, into which "
            "several great rivers drain. The Shahnameh calls it "
            "Zabulistan, home of Zal and of his son Rostam, a giant of "
            "a hero. Many Ghuzz live here. Its capital is Zaranj; Dartal "
            "in the Zamin-Dawar guards the passes into Ghur.",
            "Rostam was so huge that the Simurgh had to teach his "
            "father to cut him from his mother; his stallion Rakhsh "
            "could carry him, kill a lion and outrun any horse. In "
            "Rostam's Seven Quests he rescues his king from the demons "
            "of Mazandaran and ends by fighting the White Demon, the "
            "Div-e Sepid; in Rostam and Sohrab he kills his own son "
            "unknowing; and he died by the treachery of the king he "
            "served. Any Persian knows the tale; its details want an "
            "Area Lore. Rostam's descendants carry Mythic Blood (the "
            "catalog's general Virtue): a short-lived +3 to one "
            "athletic, riding or swimming action of their choosing, a "
            "Minor Focus in harming supernatural creatures, the Reckless "
            "Flaw, and often Large or Giant Blood.",
        ),
    )
    _place(
        cradle,
        "quhistan",
        "Quhistan",
        inside=k,
        summary=paragraphs(
            "The 'land of the mountains' east of the Great Desert, "
            "between Khurasan and Seistan: a cool highland unlike the "
            "lands about it. It is a dependency of Khurasan on paper "
            "and part of the hidden Isma'ili state in fact; the Nizaris "
            "hold its mountain castles: Tabas, Qa'in, Birjand, Turshiz, "
            "Muminabad, Nih and Dara.",
        ),
    )
    _place(
        cradle,
        "ghur",
        "Ghur",
        inside=k,
        summary=paragraphs(
            "Mountains whose people are kin to the Baluchi and to the "
            "folk of Bactria and Badakhshan more than to the Persians. "
            "When the Khwarazm-shah drove the Shansabani out, their "
            "familiar demons and evil spirits stayed: malicious jinn "
            "haunt its roads, demons walk its towns in human shape, and "
            "the Ghurs watch even their own kin for any strange "
            "behaviour. In some towns the demons rule openly and the "
            "people cannot stop them. No new ruler has replaced the "
            "vanished Shansabani; Bamiyan, Firuzkuh and Ghazni were "
            "their three capitals.",
            "Rostam's tiger skin, which he wore over his armour and "
            "slept in, is held by the emir of Ghur. It adds +5 to Soak "
            "on top of any armour, with a Load of 1, and lets its owner "
            "recover long-term Fatigue from any night's sleep, however "
            "hard or cold the ground; but he sleeps so deeply that waking "
            "him takes a Stamina roll of 9, and he is at -1 to all he "
            "does until sunrise, unless he spends a Confidence point. "
            "Joined with his mace (in Samarkand's Shahr-i-Zindah) and "
            "his bones (in the tower at Zaranj), it is said to rouse the "
            "hero for a while to defend Persia; a quest in Rostam's tale "
            "in Elysium may point the way to both.",
        ),
    )


# -- the lords --


def _lords(cradle: Cradle) -> None:
    b, w = cradle.b, cradle.world
    w["khwarazm_shah"] = b.lord(
        "The Khwarazm-shah",
        title="",
        wealth="Wealthy",
        seat="Gurganj and Samarkand",
        ruler="Ala al-Din Muhammad",
        summary=paragraphs(
            "Ala al-Din Muhammad, Sultan Mohammed II, son of Tekish, the "
            "mamluk ruler of Khwarazm who brought the Seljuks down in "
            "1194. He went on with his father's conquest of the Seljuk "
            "lands and named himself their shah in 1205, a title the "
            "caliph has never granted; he broke the Shansabani in "
            "Khurasan in 1206, added Transoxiana in 1212, and beat the "
            "faerie Qara Khitai in 1218. His empire now runs from the "
            "Jaxartes to the Gulf, with twin capitals at Samarkand and "
            "Gurganj, and most of Persia's atabegs and mamluks have "
            "sworn to him. Kirman is under his army's occupation; the "
            "House of Healing at Gundeshapur keeps his favour.",
            "In 1218 his cousin Inalchuq, governor of Otrar, put to "
            "death a whole Mongol trade caravan with its envoy; when "
            "Genghis Khan's ambassadors met the shah at Samarkand, he "
            "had them killed or shaved, a mortal insult, and sent back. "
            "As 1220 begins the Khan's horde is before Bukhara.",
            "If history holds: Bukhara, Otrar, Samarkand and Gurganj "
            "fall in 1220, and the shah, hunted across Khurasan, dies "
            "on the Caspian shore at the year's end. In 1221 the "
            "Mongols sack Balkh, Merv, Nishapur and Herat, and his son "
            "Jalal al-Din is driven over the Indus; the Mongols take "
            "eastern Persia by 1227 and western Persia between 1230 and "
            "1240.",
        ),
    )
    w["salghurids"] = b.lord(
        "Salghurid Atabeg of Fars",
        title="",
        wealth="Wealthy",
        seat="Shiraz",
        ruler="the Salghurid atabeg",
        place=cradle.places["fars"],
        summary=paragraphs(
            "The Salghurid dynasty, Turkish atabegs who hold Fars from "
            "Shiraz. The book names none of them. Like most of Persia's "
            "provincial lords they owe the Khwarazm-shah their oath, and "
            "Shiraz is their capital.",
        ),
    )
    w["ghuzz_atabeg"] = b.lord(
        "Ghuzz Atabeg of Khuzistan",
        title="",
        seat="Ahwaz",
        ruler="the Hazarasp atabeg",
        answers_to=w["khwarazm_shah"],
        place=cradle.places["khuzistan"],
        summary=paragraphs(
            "An atabeg of the Ghuzz family of Hazarasp, ruling Khuzistan "
            "from Ahwaz under an oath of loyalty to the Khwarazm-shah. "
            "The book gives no name.",
        ),
    )


# -- Fars --


def _fars(cradle: Cradle) -> None:
    fars, w = cradle.places["fars"], cradle.world
    _town(
        cradle,
        "arranjan",
        "Arranjan",
        place=fars,
        ruler="the Isma'ilis",
        summary=paragraphs(
            "The westernmost of Fars's five great cities, on the south "
            "bank of the Tab, which divides Fars from Khuzistan; date "
            "palms and olive groves ring it, and it is known for soap "
            "and bitumen. Isma'ili strongholds have long crowned the "
            "hills about it, and the Isma'ilis have lately taken the "
            "city itself. Hindijan, on the lower Tab, is its port.",
        ),
    )
    _place(
        cradle,
        "well_of_hindijan",
        "The Well of Hindijan",
        inside=fars,
        summary=paragraphs(
            "A well at Hindijan, Arranjan's port, where treasure hunters "
            "have wasted many nights looking for a hoard said to be "
            "hidden in the town. Its poisonous fumes kill any bird that "
            "flies over it, so it drops in, and for the same reason "
            "nobody has yet gone down it.",
        ),
    )
    _town(
        cradle,
        "darabgerd",
        "Darabgerd",
        place=fars,
        summary=paragraphs(
            "A round city founded by a family from Daylam, quietly "
            "Isma'ili in sympathy though it has never said so. Near it "
            "is the Kubbat al-Mumiya, the Bitumen Dome, shut by an iron "
            "door; each year the sultan's officer comes, unlocks it and "
            "boxes up the bitumen gathered since, for the court.",
        ),
    )
    _place(
        cradle,
        "salt_of_seven_colours",
        "The Hill of the Seven-Coloured Salt",
        inside=fars,
        summary=paragraphs(
            "A hill near Darabgerd where rock salt of seven colours is "
            "now and then dug out.",
            "Vis: the salt is Dedicated Vis (Realms of Power: Magic) for "
            "summoning jinn, who love it: each pawn counts as two when "
            "summoning a jinni, though not other spirits. The book gives "
            "no yearly amount. Princes keep the salt workings in their "
            "own hands and use the salt to woo or reward sahirs.",
        ),
    )
    _town(
        cradle,
        "kajaran",
        "Kajaran",
        place=fars,
        summary=paragraphs(
            "A small, well-off town near the Gulf, home of the Kajarani "
            "worms, an odd Beast of Virtue that can be Enriched while "
            "alive. Kept alone in a dark box for a season and fed twelve "
            "mulberry leaves a day, each folded into a pellet, a worm "
            "gives Luck to whoever fed it (it dies if two people feed "
            "it). Enriched again each year it grows, to a mouse's size "
            "and Puissant (an Ability), then a cat's and Venus' "
            "Blessing, then a dog's and Wealthy, the Virtues adding up "
            "and all lost if it dies; but in its third year its keeper "
            "cannot refuse its comforts (Compulsion) and in its fourth "
            "it begins to repel him (Fear). A worm eats any other worm "
            "it meets, and nobody in Kajaran lets one see a fifth year.",
            "They remember Haftvad, a peasant who let his worm grow seven "
            "years into a gleaming black dragon patterned in saffron, "
            "and rode his luck to rule from Basra to Kirman, beating the "
            "first Sasanid, Ardeshir, until Ardeshir killed the "
            "elephant-sized beast with boiling lead. Haftvad's fortress "
            "still stands, hidden high in the mountains.",
        ),
    )
    _town(
        cradle,
        "istakhr",
        "Istakhr",
        place=fars,
        summary=paragraphs(
            "The seat of Fars's northern district, the Persepolis of the "
            "Greeks, and once Takht-e Jamshed, the capital of Jamshid, "
            "the Shahnameh's fourth king of the world: a great sorcerer "
            "who ruled every jinni and gave men armour, weaving and "
            "dyeing, masonry, wine and ships, until pride drove off the "
            "royal farr, Ahura Mazda's shining blessing, and Zahhak "
            "murdered him. Buildings of Jamshid's and Solomon's day stand "
            "in and around the city. Rice and pomegranate villages crowd "
            "the shore of Lake Bakhtigan near by; on the hills to the "
            "north-west the Sih Gundaban, three great fortresses, guard "
            "a dam in a deep gorge that holds a year's water for a "
            "thousand besieged men, and a drill ground on a flat "
            "hilltop.",
            "The Jaam-e Jam, the Cup of Jamshid, of silver with seven "
            "bands of gold and jewels, lay hidden in Istakhr from "
            "the Arab conquest until a sahir found it a few years ago. "
            "Filled with an elixir of long life (al-Iksir, say, or a "
            "longevity potion) brewed new for its user, it works for one "
            "season and spends the elixir: its holder names any place in "
            "the world and sees it in the cup, as Summoning the Distant "
            "Image does but with no Arcane Connection, and its views of "
            "the heavens double his Artes Liberales for astrology and "
            "his Solomonic Astrology for magic.",
        ),
        secrets=[
            titled(
                "Who has the cup",
                "The sahir who found the cup at Istakhr uses it to pry on "
                "neighbours and rivals (the troupe perhaps among them).",
            ),
            titled("Storyguide Notes", "The book does not name the sahir."),
        ],
    )
    _place(
        cradle,
        "kamfiruz",
        "The Forest of Kamfiruz",
        inside=fars,
        summary=paragraphs(
            "An oak wood amid pastures between Shiraz and Istakhr, by "
            "the town of Bayda, whose fierce lions are the terror of the "
            "herds grazing round it. The local emir has begun to hunt "
            "them down.",
        ),
    )
    _town(
        cradle,
        "kish",
        "Kish",
        place=fars,
        ruler="the emir of Kish",
        summary=paragraphs(
            "The island that is the Gulf's chief port, about twelve "
            "miles out, under a great walled city. It is famous for its "
            "pearls and crowded with the trade of Arabia, Africa and "
            "Al-Sind, which goes over to Huzu on the mainland and north "
            "to Shiraz. It has risen over the last century since Siraf, "
            "the old port further west, was ruined by an earthquake "
            "that went on for seven days.",
            "Pirates from Abarkavan, the Long Island, prey on its "
            "traders and on the divers of its pearl banks, to its emir's "
            "fury; one of them is an elementalist (Hedge Magic) who "
            "plays with wind and wave.",
        ),
    )
    _town(
        cradle,
        "shiraz",
        "Shiraz",
        place=fars,
        answers_to=w["salghurids"],
        ruler="the Salghurid atabeg",
        summary=paragraphs(
            "The capital of Fars and of the Salghurids, made the empire's "
            "capital by the Buyids (945 to 1055), who filled it with "
            "palaces, mosques and a great wall. It is now the Dar "
            "al-Elm, the House of Knowledge, for its academies and its "
            "schools of famous poets; sitting at the middle of Fars, it "
            "takes most of the province's trade through narrow, packed "
            "markets, and it has three great mosques.",
        ),
    )
    _place(
        cradle,
        "shiraz_shrines",
        "The Imamzadihs of Shiraz",
        inside=fars,
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "Shiraz's many shrines to the imamzadihs, kin and "
            "descendants of the twelve Shi'i imams. Each grants its own "
            "miracle, most often the cure of a given complaint, a "
            "husband or wife, or an easy birth, and they compete for "
            "pilgrims. The shrine of the fourth imam's brother, on the "
            "Street of Butchers, has baraka for hurt limbs; the shrine "
            "of the sixth imam's daughter, beside the main square, for "
            "every trouble of the feet; and the two are bitter rivals.",
            "The book gives no aura; the shrines take the city's 4.",
        ),
    )
    _town(
        cradle,
        "shapur",
        "Shapur",
        place=fars,
        summary=paragraphs(
            "The City of Flowers, which sends out irises, violets, "
            "jasmine and narcissus and above all its red rose. It makes "
            "ten scented oils from them; its attar of roses is dear "
            "enough to reach the courts of England and France.",
        ),
    )
    _place(
        cradle,
        "black_man",
        "The Black Man",
        inside=fars,
        realm="Infernal",
        summary=paragraphs(
            "A forty-foot statue of a man in black stone in a cave near "
            "Shapur, three carved leaves at its feet; behind it a "
            "waterfall, and a wind that never stops blowing out of the "
            "cave. Some say it is King Shapur, others a real man God "
            "turned to stone. The old kings anointed it with oil; nobody "
            "has honoured it for centuries.",
        ),
        secrets=[
            titled(
                "What the Black Man is",
                "The statue of the Black Man is a great div, one of the "
                "forty-five named demons (which one is unknown), bound in it "
                "long ago by a mobed.",
            ),
            titled(
                "The green leaves",
                "Knowing his binding of the div in the Black Man would not "
                "last forever, the mobed made the leaves green, to fade as it "
                "wore off; each anointing came with a mobed's blessing that "
                "renewed it. Under Muslim rule the rite was banned as "
                "idolatry, and only a tenth of one leaf is still green: the "
                "demon is nearly free.",
            ),
        ],
    )
    _town(
        cradle,
        "yazd",
        "Yazd",
        place=fars,
        summary=paragraphs(
            "The stronghold of the Mazdean faith since Islam came, and "
            "one of the few places it is still openly kept. The city is "
            "well walled, with two iron gates on the Istakhr road, and "
            "the streams from the near mountains make it so fertile, "
            "this close to the Great Desert, that it seems a paradise; "
            "the mobeds get the credit. The six pirs, mountain shrines "
            "of the Zoroastrian villages, are near by.",
        ),
    )


# -- Jibal --


def _jibal(cradle: Cradle) -> None:
    jibal = cradle.places["jibal"]
    _town(
        cradle,
        "isfahan",
        "Isfahan",
        place=jibal,
        summary=paragraphs(
            "Jibal's largest city, on the north bank of the Zayandah, "
            "which rises in the Zagros, sinks into the Gav-Khanah swamp "
            "on the edge of the Dasht-i Kavir, and comes up again ninety "
            "leagues off in Kirman. It is two towns: Jay to the east, "
            "inside a wall of a hundred towers, and Al-Yahudiyah to the "
            "west, where Jews have lived since Nebuchadnezzar. Ibn Sina, "
            "the Latins' Avicenna, lived and taught here. It sells silk, "
            "cotton, saffron and every fruit, but its carpets are what "
            "it is famous for: an Isfahan rug has an ivory field with one "
            "central medallion among leaves and vines, in blues, rose "
            "and indigo dyed by methods its weavers keep secret.",
        ),
    )
    _town(
        cradle,
        "kirmanshah",
        "Kirmanshah",
        place=jibal,
        summary=paragraphs(
            "The seat of Kurdistan, a half-independent province Sultan "
            "Sanjar made for his nephew about 1150, with a great mosque "
            "and a splendid palace. A day's march east the rock of "
            "Bustam bears carvings of Darius taking his vassal kings' "
            "tribute and, far later, of Khusraw Parviz and Queen "
            "Shirin, whose sculptor Farhad killed himself for love of "
            "her. On the road east lies Kanguvar, which the Arabs call "
            "the Robbers' Castle for good reason.",
        ),
    )
    _town(
        cradle,
        "qum",
        "Qum",
        place=jibal,
        summary=paragraphs(
            "After Mashhad perhaps Persia's holiest place for Muslims: "
            "the tomb of Fatima, Imam Reza's sister, with the ninth "
            "imam's three daughters beside her. Reza promised Paradise "
            "to whoever made the pilgrimage to her. The mosque of Jam "
            "Karan lies a few miles east.",
        ),
    )
    _place(
        cradle,
        "jam_karan",
        "The Mosque of Jam Karan",
        inside=jibal,
        realm="Divine",
        aura=7,
        summary=paragraphs(
            "A mosque a few miles east of Qum, on holy ground. In 986 "
            "the hidden Imam and al-Khidr appeared to "
            "Hassan ibn Muthih and bade him build here, and the mosque "
            "he raised has hardly an equal in Persia for its building "
            "and adornment. Its Divine aura is 7.",
        ),
    )
    _town(
        cradle,
        "rayy",
        "Rayy",
        place=jibal,
        summary=paragraphs(
            "A strong city whose five gates open on five roads, to "
            "Qum, Hamadan, Qazvin, Mazandaran and Khurasan. The inner "
            "city, with the mosque and the officials' houses, is "
            "ditched round; the outer city rings and overlooks it, with "
            "a busy fruit market of melons, peaches and apricots. It "
            "sells blue-dyed cotton, striped cloth above all, and "
            "hardwood from the Mazandaran forests.",
        ),
    )
    _place(
        cradle,
        "rayy_spring",
        "The Shrine of Shahr Banu",
        inside=jibal,
        realm="Divine",
        summary=paragraphs(
            "A shrine on a mountain near Rayy to Shahr Banu, a Sasanid "
            "princess and the fourth Shi'i imam's mother, whom the "
            "mountain swallowed, they say, sooner than let her enemies "
            "kill her. For centuries before, the place was a shrine of "
            "Anahita, the Mazdean yazata of water and fertility. The "
            "book gives it no aura.",
            "Vis: Aquam, in the water of the shrine's spring, when it "
            "is drawn while Venus is in the sky; the book gives no "
            "amount.",
        ),
    )
    _town(
        cradle,
        "savah",
        "Savah",
        place=jibal,
        summary=paragraphs(
            "A town of camel-drivers and herdsmen whose great mosque "
            "holds the finest magical library in Persia. A hospital and "
            "a tall domed tower adjoin the mosque: the tower has the "
            "library below and the observatory at the top, and Savah's "
            "house of wisdom, every member of it of the Followers of "
            "the Star, keeps both.",
        ),
    )


# -- Khuzistan --


def _khuzistan(cradle: Cradle) -> None:
    khuzistan, w = cradle.places["khuzistan"], cradle.world
    _town(
        cradle,
        "ahwaz",
        "Ahwaz",
        place=khuzistan,
        answers_to=w["ghuzz_atabeg"],
        ruler="the Hazarasp atabeg",
        summary=paragraphs(
            "Khuzistan's capital, beset by jinn: they make its days "
            "unbearably hot and fill its nights with biting flies, the "
            "water jinn crashing over its weir keep newcomers awake, and "
            "snakes and scorpions swarm in the fields about it. An "
            "alchemist here claims he can make gold of base metal, if "
            "only he had a few magical ingredients, above all the wood "
            "the Zagros griffins gather for their nests.",
        ),
    )
    _town(
        cradle,
        "gundeshapur",
        "Gundeshapur",
        place=khuzistan,
        summary=paragraphs(
            "The town of the House of Healing, the great medical school "
            "and hospital founded by the sahir Bakhtyshu, a Nestorian of "
            "Harun's council, and still run by his descendants; the "
            "Seljuk sultans paid for it and the Khwarazm-shah holds it "
            "in honour. It is also the town's largest house of wisdom.",
        ),
    )
    _town(
        cradle,
        "ramhurmuz",
        "Ramhurmuz",
        place=khuzistan,
        summary=paragraphs(
            "A rich town living on silk and perfume, with a modest "
            "library. Its sahirs once took in one of the famous "
            "sorcerers of Soqotra, who studied with them for some years "
            "and, too trusting, gave away much of his island's lore, "
            "among it many perfume recipes, which the sahirs turned into "
            "a thriving trade. Seeing he had been cheated, he left, and "
            "cursed the district: every year gnats and biting midges "
            "swarm over it.",
            "South-east of the town, near Fars, is the district of the Zutt.",
        ),
    )


# -- Kirman --


def _kirman(cradle: Cradle) -> None:
    kirman = cradle.places["kirman"]
    _town(
        cradle,
        "bardasir",
        "Bardasir",
        place=kirman,
        summary=paragraphs(
            "A trading city between western Persia and Khurasan. The "
            "governor's palace sits in green gardens on a very tall hill "
            "outside it, a second fortress guards the gate and a third "
            "looks down on the houses from the middle of the town; for "
            "all that the Ghuzz sacked it, and Sirjan has since outgrown "
            "it.",
        ),
    )
    _town(
        cradle,
        "jiruft",
        "Jiruft",
        place=kirman,
        summary=paragraphs(
            "A city on the Div Rud, the Demon River, which runs so hard "
            "that waterwheels all over the town drive the working of "
            "indigo, cotton and grain. Lions from the forests about it "
            "hold the city under siege; anyone coming must pass through "
            "the dark woods, and its trade has dwindled to a trickle "
            "these last years.",
        ),
    )
    _place(
        cradle,
        "jiruft_forest",
        "The Forest of Jiruft",
        inside=kirman,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "The woods round Jiruft, whose lions a jinni, the lion-shah, "
            "took for his own about ten years ago. His glamour, spread "
            "over the forest, has given it a Faerie aura, and the lions "
            "have been a little Warped by it. The book gives no "
            "strength; 3 is assumed.",
        ),
    )


# -- Mazandaran and Daylam --


def _mazandaran(cradle: Cradle) -> None:
    b, p, w = cradle.b, cradle.places["persia"], cradle.world
    maz = _place(
        cradle,
        "mazandaran",
        "Mazandaran",
        inside=p,
        summary=paragraphs(
            "The lands between the Caspian and the Alborz: Gilan, with "
            "Daylam to its south, Tabaristan (its chief city Amul) and "
            "Gurgan, whose capital shares its name. The Arabs never took "
            "it, kept out by the mountains and by its old Mazdean "
            "nobility; the Bavand family held it for two hundred years, "
            "until the Nizari Isma'ilis brought them down in 1125, and "
            "the Nizaris rule its politics now. It is the ancient "
            "Hyrcania, the land of the tigers: hot, wet and very "
            "fertile, blessed by Ahura Mazda in the Zoroastrians' eyes, "
            "with houses built of wood rather than brick and a famous "
            "hardwood, khalanj. Its old demons are those Rostam fought, "
            "the White Demon among them.",
            "Three groups of magicians fight over it: the mobeds of "
            "Daylam, one of Zoroastrianism's last strongholds; the "
            "Nizaris in their Alborz castles, whose faith seeks to win "
            "every man and be rid of those who refuse; and the yatus of "
            "Mount Damavand. None will ever agree with the others: "
            "yatus and Nizaris fight over vis, mobeds and Nizaris over "
            "the local rulers, and the mobeds loathe the yatus as pagans "
            "and, they suppose, devil-worshippers.",
            "Hyrcanian vis. Vis is plentiful here: the yatus say "
            "Damavand is the source of all vis in the world, the mobeds "
            "that it is Ahura Mazda's gift. It gathers in whatever is "
            "odd or single: the one white egg among a hen's brown ones, "
            "the ear of wheat with thirteen grains, the driftwood "
            "furthest along the shore. A character may hunt for it, "
            "chasing rumours and dead ends through a land the size of a "
            "small county for a season: Perception + Area Lore: "
            "Mazandaran + a die against 9 finds a pawn, and each point "
            "over either adds a pawn or halves the time (both may be "
            "had; beating it by 8 might give five pawns in eleven days). "
            "To the roll add one of the magnitude of a vis-finding "
            "spell's Target or Magic Sensitivity; a Realm Lore, no "
            "higher than the Mazandaran Lore (with any Lore but Magic "
            "Lore, half the vis found, rounded up, is tainted by that "
            "realm); and the aura, if the whole search lies in a Magic "
            "aura. Ground searched in the last season costs -15, in the "
            "last six months -9, in the last year -3, whoever searched "
            "it; the storyguide may raise the Ease Factor where "
            "magicians or magical beings are thick. Elsewhere the same "
            "roll may be used with that land's Lore against 12 in "
            "wilds, 15 in settled country and 18 in a city, for less. "
            "It finds no renewable sources, which come from stories; "
            "most sahirs of the region, yatu or Nizari, find or are "
            "given a Personal Vis Source early on.",
            "Suggested vis sources (not in the book), for the storyguide "
            "to use, change or ignore, each found by a story and not by "
            "the roll: the thirteenth hen's egg laid each spring in a "
            "Daylami village where hens lay twelve (Animal, 2 pawns); "
            "the single white flower that opens on a khalanj tree in a "
            "Tabaristan valley each midsummer (Herbam, 3 pawns); and the "
            "piece of driftwood that comes ashore furthest up the beach "
            "after the first autumn storm (Aquam, 2 pawns).",
        ),
    )
    _town(
        cradle,
        "gurgan",
        "Gurgan",
        place=maz,
        summary=paragraphs(
            "The capital of Gurgan, the westernmost province of "
            "Mazandaran, near the Caspian end of the great wall that "
            "bears its name.",
        ),
    )
    _place(
        cradle,
        "damavand",
        "Mount Damavand",
        inside=maz,
        summary=paragraphs(
            "The mountain that towers over all Tabaristan, its snowy "
            "peak seen for hundreds of miles across Persia's plains. The "
            "Simurgh nests here, and the tyrant Zahhak is thought to lie "
            "imprisoned beneath it. On its lower slopes are seven "
            "settlements, each with its own house of wisdom of sahirs "
            "mostly of yatu descent: closed houses, which take no other "
            "sahirs, kept by the pagan yatus apart from the Order's "
            "other families. The yatus guard an Initiation Script for a "
            "Major Focus against the enemies of Persia; the rite works "
            "only within the Wall of Gurgan's aligned aura.",
        ),
        secrets=[
            titled(
                "The first Zahhak",
                "The first Zahhak was not killed by Feridun: with an angel's "
                "help he was chained and buried under Mount Damavand. The "
                "demon has long since left him, but he lives on there, kept "
                "from death by the holy bonds, an ancient survivor of the "
                "heroic age who might teach something to those facing a new "
                "Zahhak.",
            ),
        ],
    )
    _place(
        cradle,
        "baghl_cave",
        "Baghl's Cave",
        inside=maz,
        aura=3,
        **KNOWN_LOCALLY,
        summary=paragraphs(
            "A dark cave in the Elburz, once quarried until its jinni, "
            "Baghl, drove the miners away. He asks chiefly to be left "
            "with his lovely rock formations, though he will sometimes "
            "talk with scholars of theology. As a spirit of the place, "
            "the cave is an Arcane Connection to him (+1 to the "
            "Penetration multiplier). The book gives it no aura; 3 is "
            "assumed.",
            "Vis: 1 pawn of Terram a year, as a quartz-crusted "
            "stalactite at the back of the cave.",
        ),
    )
    _place(
        cradle,
        "gurgan_wall",
        "The Great Wall of Gurgan",
        inside=maz,
        aura=5,
        summary=paragraphs(
            "A vast rampart from the Caspian's east shore east and north "
            "to the Pishkamar Mountains, more than 120 miles long, with "
            "35 forts about every 30 miles: red brick, 25 feet thick and "
            "some 20 high, strengthened with steel and adamantine (an "
            "unbreakable metal some magicians make from diamond), with a "
            "canal down its middle the whole way. A Magic aura of 5 runs "
            "all along it. Alexander built it, the story goes (so it is "
            "also the Sadd-i-Iksandar), to keep the children of Gog and "
            "Magog out of Persia; yet the Ghuzz came in a century ago, "
            "and were asked to stay.",
            "Perhaps that is because of the breach at the fort nearest "
            "the Gates of Alexander, the wall's western end by the "
            "Caspian. Since it was found, the local sahirs have noticed "
            "that the wall's aura alignment (Realms of Power: Magic), "
            "which gave spells aimed at giants twice the usual aura "
            "bonus, is gone. Anyone who looks can see the gap was made "
            "on purpose and held open by magic that is not Solomonic. "
            "Mazandaran's sahirs care little: the Ghuzz do not threaten "
            "them.",
        ),
    )
    alamut = _place(
        cradle,
        "alamut",
        "Alamut",
        inside=cradle.places["daylam"],
        aura=3,
        summary=paragraphs(
            "The Nizaris' chief castle and the seat of their grand "
            "master, in Rudbar, the valley of the Shahrud. A king of "
            "Daylam, out hunting, saw his eagle settle on the rock and "
            "built a castle there named aluh-amut, the eagle's lesson; "
            "it has grown into a fortified village. The rock rises sheer "
            "on every side to a flat top crowded with buildings, with "
            "storerooms cut into the bedrock and a spring of its own. "
            "Amid the dust and stone lies a lavish garden, which gives "
            "the fortress its Magic aura of 3 and holds a way into the "
            "Magic Realm, where the Nizaris' initiates are taken to a "
            "paradise insula.",
            "The sect's other named castles: in Daylam, among fifty, "
            "Maimun-Diz (the strongest) and Lamasar (the most remote); "
            "in Quhistan, Turshiz, Qa'in, Birjand, Muminabad, Dara, Tabas "
            "and Nih; in Qumis, Girdkuh; in the Zagros of Fars, Shardiz. "
            "Arranjan and the hills round it are theirs too.",
            "Hasan-i Sabbah, a sahir of Nishapur, fled here after he "
            "murdered his boyhood friend Nizam al-Mulk, the Seljuk vizier "
            "and grand vizier of the Order of Suleiman, and it was here "
            "that Nizar's followers took refuge after the Isma'ili "
            "schism.",
        ),
    )
    _place(
        cradle,
        "maimun_diz",
        "Maimun-Diz",
        inside=cradle.places["daylam"],
        summary=paragraphs(
            "The strongest of the fifty Nizari castles of Daylam.",
        ),
    )
    _place(
        cradle,
        "girdkuh",
        "Girdkuh",
        inside=cradle.places["qumis"],
        summary=paragraphs(
            "The great Nizari mountain stronghold from which the sect "
            "runs Qumis. It takes a toll from everyone who passes, for it "
            "sits on the only road from western Persia to Khurasan that "
            "does not cross the Great Desert.",
        ),
    )
    _town(
        cradle,
        "damghan",
        "Damghan",
        place=cradle.places["qumis"],
        ruler="the emir of Qumis",
        summary=paragraphs(
            "The chief town of Qumis and nearly the only one there the "
            "Isma'ilis do not hold. Its emir rules a province that "
            "besieges him, never sure which of his subjects is a Nizari.",
        ),
    )
    _place(
        cradle,
        "caspian_gates",
        "The Caspian Gates",
        inside=cradle.places["qumis"],
        summary=paragraphs(
            "Sirdara to the Persians: the endless narrow gorge through "
            "which the road from Rayy to Nishapur crosses the mountains "
            "of Qumis. Carts go in single file between sheer cliffs, "
            "slowed further by water streaming down the rock and by the "
            "swarms of snakes that infest it; merchants still prefer it "
            "to the Great Desert.",
        ),
    )
    b.link(alamut, "places", cradle.places["maimun_diz"], "Nizari castle")
    b.link(alamut, "places", cradle.places["girdkuh"], "Nizari castle")
    for key in ("nizaris", "imam"):
        record = w.get(key)
        if record is not None:
            b.link(alamut, "places", record, "Its masters")


# -- the Great Desert and Makran --


def _desert_and_makran(cradle: Cradle) -> None:
    desert = cradle.places["great_desert"]
    kavir = _place(
        cradle,
        "dasht_i_kavir",
        "The Dasht-i Kavir",
        inside=desert,
        summary=paragraphs(
            "The salt desert of the north, about 500 miles from west to "
            "east and 200 from north to south. Its middle is almost "
            "rainless, but it has marshes, wadis and stretches like "
            "steppe, and a great salt lake in the west, and many birds, "
            "sand grouse and great bustards, besides the Persian gazelle "
            "and the Hyrcanian tigers that hunt it.",
            "Its oases: Garmah, halfway between Isfahan and Tabas, three "
            "hamlets round a small fort, with palms and pasture, whose "
            "emir must keep the desert roads open; and Naband, between "
            "Kirman and Quhistan, whose guard house does not stop desert "
            "raiders hiding in its domed water tanks.",
        ),
    )
    _place(
        cradle,
        "rig_i_jinn",
        "The Rig-i Jinn",
        inside=kavir,
        realm="Faerie",
        aura=3,
        **KNOWN_LOCALLY,
        summary=paragraphs(
            "Dunes in the middle of the Dasht-i Kavir where a tribe of "
            "jinn lives, mischievous more than malicious; the caravans "
            "go round. Its Faerie aura of 3 is the tribe's own glamour "
            "and moves with them. Travellers who meet them see a green "
            "oasis where none should be, and are fed or wounded as the "
            "jinn please; either way the oasis moves while they are in "
            "it, and when the jinn draw off the travellers may be tens "
            "of leagues from where they began.",
        ),
    )
    lut = _place(
        cradle,
        "dasht_i_lut",
        "The Dasht-i Lut",
        inside=desert,
        summary=paragraphs(
            "The 'emptiness desert' of the south, some 300 miles along "
            "its north-west to south-east line and 200 across: salt flats "
            "on a low plateau in the east, mostly sand in the south-east, "
            "and far less life than the Kavir. Its oasis Sanij, in a "
            "valley joining Kirman to Seistan, is home to many people, "
            "whom the Balu raiders who know it well never leave in "
            "peace.",
        ),
    )
    _place(
        cradle,
        "gandom_beriyan",
        "The Gandom Beriyan",
        inside=lut,
        realm="Infernal",
        aura=4,
        levels=[
            Builder.level(
                "The burning heart",
                7,
                "Infernal",
                notes="A Tartaran regio at the waste's centre, where the "
                "air burns and the rock runs molten; one of the mightiest "
                "corrupt jinn of Persia lurks in it.",
            )
        ],
        summary=paragraphs(
            "The 'toasted wheat': the middle of the Dasht-i Lut, a "
            "volcanic waste of black lava cut by ravines and sinkholes "
            "and scoured by a fierce wind, the hottest place in Persia "
            "and empty of any plant or beast. The cruellest of the jinn "
            "tribes live here, in an Infernal aura of 4 tainted with a "
            "Debauched aura of exhaustion, so no one may spend "
            "Confidence while in it.",
            "Few come willingly: it is a place of Infernal pilgrimage, "
            "where a villain may be chased before he gives himself "
            "further to Hell; those fleeing the Balu may blunder in, and "
            "be saved by their pursuers, who would not feed the land "
            "more victims than they must; and as the hottest spot on "
            "earth it may serve a Mystery's initiation, or the forging "
            "or unmaking of a thing of power.",
        ),
    )
    _place(
        cradle,
        "gedrosian_desert",
        "The Gedrosian Desert",
        inside=cradle.places["makran"],
        summary=paragraphs(
            "The arid coast of Makran, the ancients' Gedrosia, famous "
            "for being all but impassable; it beat the armies of Cyrus, "
            "of Queen Semiramis and at last of Alexander's unbeaten "
            "veterans, and only scattered fisherfolk live on it. It is "
            "full of pagan ghosts, soldiers of every army that has died "
            "trying to cross it since antiquity. As restless dead they "
            "answer necromancers and other summoners readily, but most "
            "are so lost in despair and the memory of want that they "
            "can say little of use about their past.",
        ),
    )


# -- Khurasan and its districts --


def _khurasan(cradle: Cradle) -> None:
    b = cradle.b
    k, seistan = cradle.places["khurasan"], cradle.places["seistan"]
    zaranj = _town(
        cradle,
        "zaranj",
        "Zaranj",
        place=seistan,
        summary=paragraphs(
            "Seistan's capital, on a branch of the Helmund, so near "
            "Lake Zarah in flood time that the swelling lake almost "
            "reaches it. A walled inner town is ringed by outer "
            "suburbs; above-ground channels bring water to every house, "
            "and nearly every house has a cellar where its people live "
            "through the stifling summer. Salt marshes, drowned each "
            "year when the lake rises, lie round it, and sand beyond "
            "them. From early summer into autumn the baad sad va bist "
            "rooz, the wind of 120 days, blows from north to south, "
            "wrapping the land in dust; some think jinn live in it.",
        ),
        secrets=[
            titled(
                "The 120-day wind",
                "Zaranj's 120-day wind is a host of air elementals on their "
                "yearly migration, playing as they pass.",
            ),
            titled("Storyguide Notes", "Air elementals: Realms of Power: Magic."),
        ],
    )
    _place(
        cradle,
        "rostam_tower",
        "Rostam's Tower",
        inside=seistan,
        summary=paragraphs(
            "A fluted tower in Zaranj with no door, stair or any way up. "
            "The bones of Rostam and his horse Rakhsh are thought to lie "
            "on its top: their bodies were laid out to sun and vultures "
            "in the Zoroastrian way, the bones never gathered, and the "
            "tower sealed as their monument. Brought together with his "
            "tiger skin and his mace, the bones are said to wake the hero "
            "from his death-like sleep for a time, to stride out once "
            "more in Persia's defence.",
        ),
    )
    b.link(zaranj, "places", cradle.places["rostam_tower"], "In the town")
    _town(
        cradle,
        "dartal",
        "Dartal",
        place=seistan,
        summary=paragraphs(
            "The city of the Zamin-Dawar, the Land of Gates, named for "
            "the passes into Ghur; it keeps a strong garrison of horse "
            "guards against the warlike Ghurs beyond the mountains. The "
            "flocks of the Zamin-Dawar give Persia much of its wool. The "
            "Zur Mountain, near by, once had a shrine to a solid gold "
            "idol with ruby eyes, carried off as booty at the Muslim "
            "conquest.",
        ),
    )
    _town(
        cradle,
        "herat",
        "Herat",
        place=k,
        ruler="the emir of Herat",
        summary=paragraphs(
            "The Pearl of Khurasan, under the ruins of a citadel of "
            "Alexander's. It has changed hands many times in the last "
            "hundred years but has built a name for brasswork, still its "
            "chief export. The fire temple of Sirishk is two leagues "
            "north, with a Nestorian church between it and the city, and "
            "south of Herat lies a land as lush as a garden, watered by "
            "many canals.",
        ),
    )
    _town(
        cradle,
        "merv",
        "Merv",
        place=k,
        summary=paragraphs(
            "A great oasis city of the Silk Road, 'the meeting place of "
            "great and small', whose vast market is said to sell "
            "everything. Once it called itself the largest city in the "
            "world; but the Ghuzz plundered it in 1153, it has since "
            "passed among Khwarazmians, Ghuzz and Ghurids, and Nishapur "
            "has taken its place in Khurasan. Sultan Sanjar, the last of "
            "the great Seljuks, lies here under a dome of blue tiles so "
            "tall it shows a day's march off.",
            "Its libraries are famous. The Great Mosque has two, the "
            "'Aziziyah of over 12,000 books and the Kamaliyah with "
            "somewhat fewer; the libraries of the colleges of the "
            "Samanidiyah, the 'Umaydiyah and the Khatuniya are kept here "
            "too; and the small Dumayriyah's 200 books are priceless, "
            "many of them unique. What matters most to the sahirs is "
            "Nizam al-Mulk's library, the grand vizier's, now held among "
            "Merv's collections, and the town's house of wisdom keeps its books "
            "of magic.",
        ),
        secrets=[
            titled(
                "Faeries in Merv's market",
                "Faeries keep stalls in Merv's market beside the townsfolk "
                "and help earn Merv its name.",
            ),
            titled(
                "Trading with Merv's faeries",
                "The faeries of Merv's market draw their life from trading "
                "with mortals but supply nothing themselves: each deal they "
                "make is with another mortal who has the thing, so getting "
                "anything rare means a chain of favours, each faerie asking "
                "for something else, from a pebble with a white spot to the "
                "Sasanid king's crown. The trick is to know when to stop.",
            ),
        ],
    )
    _town(
        cradle,
        "mashhad",
        "Mashhad",
        place=k,
        summary=paragraphs(
            "Mashhad ar-Rizawi, the place of Reza's martyrdom: the city "
            "grew round the tomb of the eighth Shi'i imam. The Sunni "
            "caliph Mamun surprised everyone by naming Reza his heir, "
            "and when Sunnis rose in violence at the news, Reza died "
            "suddenly before he could take it up; the Shi'a say Mamun "
            "repented and settled the matter by murder. A pilgrimage "
            "here is held worth 70,000 to Mecca, and people come from "
            "all over Persia.",
        ),
    )
    _place(
        cradle,
        "imam_reza_shrine",
        "The Shrine of Imam Reza",
        inside=k,
        realm="Divine",
        aura=6,
        summary=paragraphs(
            "The rich shrine over the eighth imam's tomb at Mashhad, the "
            "holiest place in Persia for its Muslims. Its Divine aura is "
            "6.",
        ),
    )
    _town(
        cradle,
        "nishapur",
        "Nishapur",
        place=k,
        summary=paragraphs(
            "Named for the first Sasanid king, Shapur I, who briefly "
            "made it his capital, it commands the way east. Like most "
            "Khurasan cities it is ruled by its market, whose streets are "
            "lined with merchants' hostels and where almost every trade "
            "is found; nearly all the turquoise and malachite that "
            "reaches the Middle East and Europe comes from mines near "
            "by. Its house of wisdom trained Nizam al-Mulk, Hasan-i "
            "Sabbah and 'Umar Khayyam, three friends who swore to share "
            "any greatness one of them won: Nizam al-Mulk became vizier "
            "of the Seljuks and grand vizier of the Suhhar, 'Umar asked "
            "only the means to study, and Hasan, secretly an Isma'ili, "
            "took a post to come near his friend and murdered him. The "
            "Order held its hand at its dying grand vizier's wish. 'Umar "
            "Khayyam, astronomer, poet and sahir, later led the house, "
            "and died in 1123.",
        ),
    )
    _place(
        cradle,
        "footsteps_of_reza",
        "The Footsteps of Imam Reza",
        inside=k,
        realm="Divine",
        summary=paragraphs(
            "Prints in the rocky road all the way from Nishapur to "
            "Mashhad, held locally to be the imam's footsteps on his last "
            "journey. Whoever walks the whole road setting his own feet "
            "in each print is said to be blessed in his next venture; "
            "but wear and malicious jinn, who lay false trails, make "
            "some prints hard to find. Finishing it should be a short "
            "story testing the walker's faith, rewarded with the "
            "Intuition Virtue for the length of his next venture.",
        ),
    )


def _ghur(cradle: Cradle) -> None:
    ghur = cradle.places["ghur"]
    _town(
        cradle,
        "bamiyan",
        "Bamiyan",
        place=ghur,
        summary=paragraphs(
            "A rich city without walls in the east of Ghur, till lately "
            "one of the Shansabani's three capitals, from which a branch "
            "of the family ruled Bactria and Badakhshan. Its people are "
            "unbelievers who honour two great idols on the mountainside.",
        ),
    )
    _place(
        cradle,
        "bamiyan_idols",
        "The Idols of Bamiyan",
        inside=ghur,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Two statues cut from the living rock in a pillared chamber "
            "high on the mountain above Bamiyan, its walls carved with "
            "birds covered in beaten gold. The townsfolk call them Surkh "
            "and Khing, Red and Grey, twin faces of one god in their "
            "tangled faith. Now and then the idols walk out of their "
            "niche, bringing a Faerie aura with them: when Khing walks "
            "the people feast it and hang it with flowers, but when "
            "Surkh is abroad they hide indoors and shake. The book gives "
            "the aura no strength; 3 is assumed.",
        ),
    )
    _town(
        cradle,
        "firuzkuh",
        "Firuzkuh",
        place=ghur,
        summary=paragraphs(
            "The Ghurids' summer capital, the 'turquoise mountain', for "
            "the turquoise (and silver) in its hills. The Shansabani "
            "used it as a retreat to hide their wickedness: enemies "
            "brought there in secret were drowned in the Hari, and some "
            "say it was the heart of their devil-worship. The palace "
            "stands empty, haunted by the ghosts of their victims.",
        ),
    )
    _place(
        cradle,
        "firuzkuh_minaret",
        "The Minaret of Firuzkuh",
        inside=ghur,
        realm="Divine",
        summary=paragraphs(
            "A minaret of baked brick more than 200 feet high on a bend "
            "of the Hari, covered in glazed tiles in alternating bands of "
            "Qur'anic verse (from the sura of Maryam, on the mother of "
            "Jesus), geometric patterns and calligraphy in several "
            "scripts. The jinn of the Hari attack it, and a flash flood "
            "has lately swept away the mosque it belonged to, but it "
            "stands, warded powerfully against supernatural beings. "
            "Sahirs have studied it for years; all they have learnt is "
            "that the wards are Divine. The book gives no aura.",
        ),
    )
    _town(
        cradle,
        "ghazni",
        "Ghazni",
        place=ghur,
        summary=paragraphs(
            "Once the capital of the mamluk of Ghur, from which a "
            "Shansabani branch ruled Khurasan, and now forsaken by them. "
            "Its Bahramshah mosque has star-shaped minarets covered in "
            "geometric patterns, and the city is famously rich: even "
            "its meanest buildings are decorated, the poorest peasant "
            "wears a gold necklace or bracelet, and the great drip with "
            "jewels.",
        ),
        secrets=[
            titled(
                "Ghazni's wealth",
                "Ghazni's wealth is the gift of a False God, a demon that "
                "the Ghaznians worship in secret.",
            ),
            titled(
                "Storyguide Notes",
                "The demon's Wealth of Nations power (Realms of Power: The Infernal).",
            ),
        ],
    )
    _town(
        cradle,
        "kabul",
        "Kabul",
        place=ghur,
        ruler="The Shadowed One",
        summary=paragraphs(
            "A city much visited by merchants, who climb its one "
            "fortified road to trade with the strange merchants of "
            "Mythic Hind. The Persians want its indigo, which fetches a "
            "high price in the west, and also myrobalan, a greasy, "
            "speckled powder spicy like pepper or cardamom that "
            "physicians prize for its cures; taken with wine it brings "
            "pleasant visions and with water horrible ones, and either "
            "way it is ruinously addictive, so the markets are full of "
            "its slaves, vacant-eyed and dark of tooth. A demon known "
            "only as the Shadowed One rules the city, bound up somehow "
            "with the myrobalan trade; no one has seen him, and four "
            "lieutenants with demon-given powers govern for him.",
        ),
    )


# -- the factions --


def _factions(cradle: Cradle) -> None:
    b, w, places = cradle.b, cradle.world, cradle.places
    persia = places["persia"]
    w["yatus"] = b.faction(
        "The Yatus",
        faction="Hedge coven",
        place=places["damavand"],
        summary=paragraphs(
            "Persia's old sorcerers, wholly secular where the mobeds "
            "served the faith, and loathed by the Mazdean priests. "
            "Ancient kings kept cadres of them with their armies, and "
            "the Greeks' unreadiness for their magic helps explain the "
            "early victories of Darius and Xerxes. Most were faerie "
            "wizards, said to have invented the Ars Fabulosa (Realms of "
            "Power: Faerie), Faerie Summoning and the arts round it, "
            "which oral lore traces to Canaanite necromancy, the root of "
            "all summoning. Darker, Goetic yatus brought down the "
            "mobeds' persecutions that ended Persia's magical warfare.",
            "When the Suhhar was founded, Persia gave it several yatu "
            "lineages that had outlived the Mazdean purges and the Arab "
            "conquest, and with them came True Names and the Virtue "
            "Invocation of Names of Power. Yatus live today in western "
            "Persia, Iraq and the north-west provinces; most are sahirs "
            "who join Faerie Summoning to the Solomonic arts, "
            "Storytelling chief among them, and the rest faerie wizards "
            "of the Ars Fabulosa. Faerie blood is common among them, and "
            "being often pagan they quarrel with many sahirs and keep to "
            "closed houses of their own, such as the seven on Damavand. "
            "They fight the Nizaris over vis in Mazandaran, and the "
            "mobeds detest them.",
        ),
    )
    w["ghuzz"] = b.faction(
        "The Ghuzz",
        faction="People or tribe",
        decides="Nobody",
        place=persia,
        summary=paragraphs(
            "Magic-blooded tribesmen from the steppes north of Persia "
            "and east of the Caspian, said to descend from Gog and "
            "Magog; their giant blood is plain to see. Big, warlike and "
            "famously ungovernable, they would be far more dangerous if "
            "they could hold together or stay loyal long enough to make "
            "an army. They live in many southern provinces, Kirman, "
            "Makran and Seistan above all, and breed huge horses; their "
            "magic kin ride mounts the size of elephants and sometimes "
            "keep eagles as big as a man. Invited in as soldiers, they "
            "rebelled in 1151, plundered Merv in 1153 and ruled Kirman "
            "for a time; now they serve in the shah's army, and one of "
            "their families rules Khuzistan.",
            "Every Ghuzz has the Large Virtue, save those in whom Gog and "
            "Magog's blood runs strong, usually their leaders: these are "
            "magic kin with Giant Blood and a Greater Immunity to having "
            "their minds swayed, by Leadership, Charm, Folk Ken, "
            "Inspirational or even Command the Masses, a Greater Power "
            "Virtue (Major, Supernatural) common among their chiefs, "
            "which makes a group of men strongly inclined to obey one "
            "order and lets him lead in battle without spending his "
            "turn on it (ReMe 30). Many Ghuzz, kin or not, have the "
            "Rebellious Flaw.",
        ),
    )
    w["shansabani"] = b.faction(
        "The Shansabani",
        faction="Family",
        decides="Its leader",
        place=places["ghur"],
        summary=paragraphs(
            "Ghur's ruling family, who count Zahhak their first "
            "forefather. Sultan Ala'uddin Hussain, the World Burner "
            "(Jahansoz), took Ghur from the Ghaznavids with his demon "
            "patrons' help, and he and his kin held Ghur and then "
            "Khurasan in an iron grip, in which troublemakers simply "
            "vanished. Their wars looked east to Hind, not west or "
            "south, to Persia's luck. Three branches ruled: Bactria and "
            "Badakhshan from Bamiyan, Khurasan from Ghazni, and Ghur "
            "itself from Firuzkuh.",
            "The last sultan, Mohammed al-Ghuri, was Zahhak's host; a "
            "Nizari killed him on the bank of the Indus in 1206 and the "
            "Khwarazm-shah forced the family out of Khurasan. They never "
            "gave Ghur up, nobody has been named in their place, and "
            "they have all disappeared: gone to Mythic Hind, some say, "
            "or into hiding. Their demons stayed behind.",
        ),
        secrets=[
            titled(
                "The Shansabani heir",
                "One rumour that will not die puts the Shansabani heir at "
                "Genghis Khan's court.",
            ),
        ],
    )
    w["zutt"] = b.faction(
        "The Zutt",
        faction="People or tribe",
        place=places["khuzistan"],
        summary=paragraphs(
            "A half-nomad tribe from south-east of Ramhurmuz near the "
            "edge of Fars, who say they came from beyond Al-Sind. They "
            "travel in brightly painted wagons and dress in vivid silks "
            "and deep-dyed linen; they are thought thieves, and the "
            "Khuzistanis greet them coldly when they come to trade. "
            "Their women are strong folk witches (Hedge Magic). They "
            "have been met as far off as Egypt and Samarkand, and some "
            "of the Atsingani covenfolk of Provence look much like them. "
            "A Zutt family now owns the golden idol of Zur, which has "
            "begun walking home to its mountain.",
        ),
    )
    w["balu"] = b.faction(
        "The Balu",
        faction="People or tribe",
        place=places["kirman"],
        summary=paragraphs(
            "The tribesmen of the Jabal Kufs, much feared by Persians: "
            "travellers say they stone their victims so as not to dull "
            "their swords, need neither food nor drink, and are as "
            "tireless as their war camels. They hate the Ghuzz but "
            "count them foes worth their blades, and they raid the oasis "
            "of Sanij. They carry strong Jinni Blood and often a Greater "
            "Immunity to thirst, ride to raid with their jinn kin "
            "beside them, and have wise men versed in Faerie Summoning "
            "and Bonding (Realms of Power: Faerie); some war leaders are "
            "bonded to a desert or mountain jinni and use its powers.",
        ),
    )
    w["peris"] = b.faction(
        "The Peris and Pairikas",
        faction="Faerie court",
        realm="Faerie",
        place=persia,
        summary=paragraphs(
            "The peris are Persia's courtly faeries, nearly all female "
            "and so lovely that a pretty girl is called peri-faced. "
            "They have a lesser nymph's statistics and part (Realms of "
            "Power: Faerie), the lover who ensnares, though they seldom "
            "rule plants; small male attendants, sprites with brightly "
            "coloured birds' wings, sometimes wait on their every whim.",
            "The pairikas are another matter: the Persian name for the "
            "Aerial Powers (Realms of Power: The Infernal), demons that "
            "sahirs treat as corrupt jinn. They are met all over Persia, "
            "mostly as the crushing heat of the desert or the terror of "
            "an earthquake.",
        ),
    )
    w["isfahan_guilds"] = b.faction(
        "The Carpet-Weavers of Isfahan",
        faction="Gild",
        place=w["isfahan"],
        summary=paragraphs(
            "Isfahan's makers of magical carpets, most of them Touched "
            "by Magic (City & Guild): a weaver adds an effect's "
            "magnitude and its uses a day to a base Craft Total of 12, "
            "can put only effects of two Hermetic Forms into his work, "
            "and a carpet works only for the one it was made for.",
            "Dadvand's family has woven flying carpets since the "
            "Sasanids and has patrons among the Suhhar; they cost a "
            "fortune for the skill they need. His Steed of the Air rises "
            "twice a day and carries its owner and all he holds through "
            "the air as fast as a running horse (ReAn 15, Ease Factor "
            "16 to make). He weaves other rugs too, such as one whose "
            "air of health speeds healing.",
            "Yarankush weaves carpets that guard their owners. His "
            "Murderers' Chagrin, woken twice a day, makes a noise of its "
            "own for a round whenever anyone but its owner touches it "
            "while he lies or sits on it (CrIm 3, Ease Factor 14): a "
            "boon to any great man in these days of hidden murder. Since "
            "saying you own one defeats its purpose, nobody talks of "
            "them.",
        ),
        secrets=[
            titled(
                "Yarankush's carpets",
                "Yarankush is a Nizari, and weaves into each carpet's design "
                "a hidden sign that tells the sect's killers not to step on "
                "it.",
            ),
        ],
    )
    b.link(w["yatus"], "places", places["damavand"], "Their seven closed houses")
    b.link(w["shansabani"], "places", w["firuzkuh"], "Their hidden retreat")
    b.link(w["shansabani"], "places", w["bamiyan"], "One of their capitals")
    b.link(w["shansabani"], "places", w["ghazni"], "One of their capitals")
    b.link(w["ghuzz"], "places", w["ghuzz_atabeg"], "Their kin in Khuzistan")
    b.link(w["balu"], "places", w["ghuzz"], "Hated foes")
    nizaris = w.get("nizaris")
    if nizaris is not None:
        b.link(w["isfahan_guilds"], "places", nizaris, "Yarankush's sect")
        b.link(w["yatus"], "places", nizaris, "Rivals for Mazandaran's vis")
    b.link(w["khwarazm_shah"], "places", w["salghurids"], "Sworn to him")
    b.link(w["khwarazm_shah"], "places", w["ghuzz_atabeg"], "Sworn to him")
