"""The mundane world as of 1220 (ch02), in paraphrase: the Russian
princes, Novgorod's Veche, the Polish dukes, the Russian and Polish
Church, the towns, the crusading orders and the Baltic peoples, and the
Volkhvy and other pagans (N15, N16).

The rulers the book names for 1220 are its own; four it does not name
come from history and say so: the princes of Ryazan (Ingvar Igorevich),
Smolensk (Mstislav Davydovich) and Novgorod (Vsevolod Mstislavich), and
the Archbishop of Gniezno (Wincenty of Niałek). Polotsk's prince in 1220
is uncertain, so the town has none. The lords' titles are the app's, so
the princes and dukes are entered as dukes with their titles in their
names. Records other packs hold are named as they name them, so an
import matches them: Valdemar II of Denmark (the Rhine), The Teutonic
Knights (the Levant), The Knights of the Sword (the Rhine) and The
Cumans (Transylvania). The Volkhvy are a hedge coven of the catalog's
Volkhvy tradition, the Slavic gods notes on it (N13).

Keys: world["yury"], ["mstislav_daring"], ["mstislav_kiev"],
["mstislav_chernigov"], ["daniil"], ["ingvar"], ["mstislav_smolensk"],
["vsevolod_novgorod"], ["mikhail_turov"], ["leszek"], ["henry_bearded"],
["conrad"], ["wladislaw"], ["swietopelk"], ["count_leczyca"],
["valdemar_ii"], ["metropolitan"], ["archbishop_novgorod"],
["monastery_caves"], ["archbishop_gniezno"], ["bishop_riga"], the towns
by name (["novgorod"], ["kiev"] ...), ["teutonic_knights"],
["knights_of_the_sword"], ["baltic_pagans"], ["cumans"], ["volkhvy"],
["vedun"], ["beslavichi"], ["cult_of_hermes"], ["hanse"]."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs

if TYPE_CHECKING:
    from ..records import Records

HISTORY = "(The book names no one for 1220; history's ruler is taken.)"
CATHEDRAL = "Archbishop's cathedral"


def build(records: Records) -> None:
    _russia(records)
    _poland(records)
    _church(records)
    _towns(records)
    _peoples(records)


def _russia(records: Records) -> None:
    b, p, w = records.b, records.places, records.world
    russia = p["russia"]
    w["yury"] = b.lord(
        "Yury II Vsevolodovich, Grand Prince of Vladimir",
        title="duke",
        wealth="Wealthy",
        seat="Vladimir-in-Suzdalia",
        place=russia,
        summary="Grand Prince of Suzdalia since 1218, after the war among "
        "Vsevolod III's sons that his brother Konstantin won in 1216. The "
        "strongest prince of the north; his brother Yaroslav will be called "
        "to rule Novgorod in 1221. If history holds he dies against the "
        "Mongols in 1238, caught on open ground before his brothers can "
        "join him.",
    )
    w["mstislav_daring"] = b.lord(
        "Mstislav the Daring, Prince of Galicia",
        title="duke",
        wealth="Wealthy",
        seat="Galich",
        place=russia,
        summary="Mstislav Mstislavich, who left Novgorod in 1219 and has "
        "ruled Galicia since, a famous warrior and son-in-law of the Cuman "
        "Khan Kotian. It is he who will raise the princes against the "
        "Mongols in 1223 and lead them to the Kalka.",
    )
    w["mstislav_kiev"] = b.lord(
        "Mstislav Romanovich, Prince of Kiev",
        title="duke",
        wealth="Wealthy",
        seat="Kiev",
        place=russia,
        summary="Of the Rostislavichi, who hold Kiev from 1212 to 1235. If "
        "history holds he makes the last stand at the Kalka in 1223 and "
        "is smothered under a carpet by the Mongols, as befits royalty, "
        "for the murder of their envoys.",
    )
    w["mstislav_chernigov"] = b.lord(
        "Mstislav Svyatoslavich, Prince of Chernigov",
        title="duke",
        wealth="Average",
        seat="Chernigov",
        place=russia,
        summary="Head of the Olgavichi, whose two lines rule Chernigov and "
        "Novgorod-Seversk; he too dies at the Kalka, if history holds.",
    )
    w["daniil"] = b.lord(
        "Daniil Romanovich, Prince of Volinia",
        title="duke",
        wealth="Average",
        seat="Vladimir-in-Volinia",
        place=russia,
        summary="The young son of Roman of Galicia, killed at Zawichost in "
        "1205, and of his widow Anna; rising fast in Volinia. If history "
        "holds he wins Kiev in 1240 just before the Mongols destroy it, and "
        "submits to them in 1241.",
    )
    w["ingvar"] = b.lord(
        "Ingvar Igorevich, Prince of Ryazan",
        title="duke",
        wealth="Average",
        seat="Ryazan",
        place=russia,
        summary="Prince of Ryazan and Murom on the steppe's edge, the first "
        "land the Mongols will burn in 1237. " + HISTORY,
    )
    w["mstislav_smolensk"] = b.lord(
        "Mstislav Davydovich, Prince of Smolensk",
        title="duke",
        wealth="Average",
        seat="Smolensk",
        place=russia,
        summary="Of the Rostislavichi, ruling the trading city of Smolensk "
        "on the upper Dnieper. " + HISTORY,
    )
    w["vsevolod_novgorod"] = b.lord(
        "Vsevolod Mstislavich, Prince of Novgorod",
        title="duke",
        wealth="Average",
        seat="Novgorod",
        place=p["novgorod_lands"],
        summary="Son of the Prince of Kiev, called by Novgorod after "
        "Mstislav the Daring left in 1219. Novgorod's princes rule at the "
        "Veche's pleasure; the book says those after Mstislav failed, and "
        "in 1221 the city expels them and calls Yaroslav, Yury's brother, "
        "beginning a war with Chernigov that lasts until 1230. " + HISTORY,
    )
    w["mikhail_turov"] = b.lord(
        "Mikhail of Turov",
        title="landed",
        wealth="Wealthy",
        seat="Turov",
        place=p["pripet_marsh"],
        summary="A boyar of Pinsk-Turov who has hunted the 'marsh "
        "monsters' in force, talks of summoning harpoonists from distant "
        "Norway, and means to dig canals to the Pripet and drain the marsh "
        "for pasture, dealing firmly with any opposition. He thinks he "
        "faces wild beasts or faeries, not magi.",
        secrets="The Church may be brought in if he finds solid proof of "
        "supernatural meddling, and Pripet Maior is no secret in the "
        "district.",
    )
    w["valdemar_ii"] = b.lord(
        "Valdemar II of Denmark",
        title="duke",
        wealth="Wealthy",
        seat="Roskilde",
        place=p["baltic"],
        summary="The Victorious, King of Denmark, who has conquered "
        "northern Estonia since 1219 and holds Reval; the Estonians will "
        "rise against the Danes in 1223.",
    )


def _poland(records: Records) -> None:
    b, p, w = records.b, records.places, records.world
    poland = p["poland"]
    w["leszek"] = b.lord(
        "Leszek the White, Grand Duke of Krakow",
        title="duke",
        wealth="Wealthy",
        seat="Krakow",
        place=poland,
        summary="Duke of Sandomierz, who seized Krakow and the senior "
        "throne in 1202 and invaded Volinia from 1214 to 1218. He will be "
        "killed in 1227.",
    )
    w["henry_bearded"] = b.lord(
        "Henry the Bearded, Duke of Silesia",
        title="duke",
        wealth="Wealthy",
        seat="Wroclaw",
        place=poland,
        summary="Duke of Silesia since 1201, who has brought German "
        "settlers into his lands since 1205; he dies in 1238. His son "
        "Henry the Pious will fall at Legnica.",
    )
    w["conrad"] = b.lord(
        "Conrad of Mazovia",
        title="duke",
        wealth="Average",
        seat="Plock",
        place=poland,
        summary="Duke of Mazovia and Kujavia, harried by the Prussians, who "
        "early in the 1220s will invite the Teutonic Knights to Chelmno to "
        "fight them.",
    )
    w["wladislaw"] = b.lord(
        "Wladislaw Spindleshanks, Duke of Greater Poland",
        title="duke",
        wealth="Average",
        seat="Poznan",
        place=poland,
        summary="Duke of Greater Poland, the land about Gniezno and Poznan.",
    )
    w["swietopelk"] = b.lord(
        "Swietopelk of Pomerania",
        title="duke",
        wealth="Average",
        seat="Gdansk",
        place=poland,
        summary="Prince of eastern Pomerania from 1220, after Mestwin I "
        "(whom the Rhine pack keeps as prince in its year); he will break "
        "with the Polish dukes.",
    )
    w["count_leczyca"] = b.lord(
        "The Count of Leczyca",
        title="count",
        wealth="Average",
        seat="Leczyca",
        place=poland,
        summary="The lord of the town below the covenant, and Stanis "
        "Chechenko's patron. The book does not name him.",
    )


def _church(records: Records) -> None:
    b, p, w = records.b, records.places, records.world
    w["metropolitan"] = b.church(
        "Sancta Sophia of Kiev",
        church=CATHEDRAL,
        ruler="Metropolitan Matfey",
        place=p["russia"],
        summary=paragraphs(
            "The seat of the Metropolitan of Kiev, head of the Russian "
            "Church, Matfey (1209-1224), a Greek appointed from "
            "Constantinople. The Church is the princes' mediator and the "
            "Volkhvy's enemy; its white clergy marry, its black clergy are "
            "monks, and the Archbishop of Novgorod is second to the "
            "Metropolitan. Sees: Belgorod, Chernigov, Galich, Peremyshl, "
            "Pereyaslavl, Polotsk, Rostov, Ryazan, Smolensk, Suzdal, Turov, "
            "Vladimir-in-Suzdalia, Vladimir-in-Volinia and Tmutorokan. "
            "There is no inquisition. Saints have taken the old gods' "
            "places: Elijah Perun's, Mary Mati-Syra-Zemlya's, Paraskeva "
            "Mokosh's, Vlas Volos's.",
        ),
    )
    w["archbishop_novgorod"] = b.church(
        "Sancta Sophia of Novgorod",
        church=CATHEDRAL,
        ruler="The Archbishop of Novgorod",
        place=p["novgorod_lands"],
        summary="The Archbishop's cathedral in the Kremlin of Novgorod, "
        "whose lord is a power in the city's government. The book does "
        "not name him.",
    )
    w["monastery_caves"] = b.church(
        "The Monastery of the Caves",
        church="Monastery or nunnery",
        place=p["russia"],
        summary="The great monastery dug into the bluffs of the Dnieper at "
        "Kiev, the heart of Russian monasticism.",
    )
    w["archbishop_gniezno"] = b.church(
        "Gniezno Cathedral",
        church=CATHEDRAL,
        ruler="Wincenty of Niałek, Archbishop of Gniezno",
        place=p["poland"],
        summary="The seat of the Polish Church in the old capital. "
        "Archbishop Henry Kietlicz (1199-1219), who fought for the "
        "Church's freedom from the dukes, has just died; the book does not "
        "name his successor. " + HISTORY,
    )
    w["bishop_riga"] = b.church(
        "Riga Cathedral",
        church="Bishop's cathedral",
        ruler="Bishop Albert of Buxtehude",
        place=p["baltic"],
        summary="Albert, Bishop of Riga since 1200, founder of the "
        "Brotherhood of the Knights of the Sword, who are conquering "
        "Livonia in his name.",
    )


#: The towns: (key, name, place key, ruler, summary).
TOWNS: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "novgorod",
        "Novgorod",
        "novgorod_lands",
        "The Veche",
        "Lord Novgorod the Great on the Volkhov, a trading republic: its "
        "Veche, the assembly of free men, elects the Posadnik (mayor) and "
        "Tysiatsky, and calls and dismisses princes; the boyars' council, "
        "the Sovet Gospod, guides it. Five districts, the Hanse's Peterhof, "
        "the cathedral of Sancta Sophia. Sadko the merchant is its folk "
        "hero. Three Lakes' trade rivals are here.",
    ),
    (
        "ladoga",
        "Ladoga",
        "novgorod_lands",
        "",
        "Novgorod's northern town on the Volkhov near Lake Ladoga, where "
        "Three Lakes buys its luxuries.",
    ),
    (
        "beloozero",
        "Beloozero",
        "novgorod_lands",
        "",
        "The town on Lake Beloe, one of the three civilized places Three "
        "Lakes sits between.",
    ),
    (
        "kiev",
        "Kiev",
        "russia",
        "Mstislav Romanovich",
        "Mother of Russian cities, much fought over and past its greatness, "
        "with the Metropolitan's court and the Monastery of the Caves. If "
        "history holds it is stormed by the Mongols on 6 December 1240 and "
        "left a waste.",
    ),
    (
        "vladimir",
        "Vladimir-in-Suzdalia",
        "russia",
        "Yury II Vsevolodovich",
        "The Grand Prince's capital; Yannes Kolski vanished near it in "
        "1216. The Mongols will burn it in 1238.",
    ),
    (
        "smolensk",
        "Smolensk",
        "russia",
        "Mstislav Davydovich",
        "The Rostislavichi's trading city on the upper Dnieper.",
    ),
    (
        "chernigov",
        "Chernigov",
        "russia",
        "Mstislav Svyatoslavich",
        "The Olgavichi's seat, which the Mongols will crush in 1240.",
    ),
    (
        "polotsk",
        "Polotsk",
        "russia",
        "",
        "Vseslav the Sorcerer's city, raided by Lithuanians.",
    ),
    (
        "galich",
        "Galich",
        "russia",
        "Mstislav the Daring",
        "The capital of Galicia under the Carpathians.",
    ),
    (
        "turov",
        "Turov",
        "pripet_marsh",
        "",
        "The town at the marsh's edge, seat of Mikhail of Turov.",
    ),
    (
        "krakow",
        "Krakow",
        "poland",
        "Leszek the White",
        "The Grand Duke's city under Wawel Hill, where Krakus slew the dragon.",
    ),
    (
        "wroclaw",
        "Wroclaw",
        "poland",
        "Henry the Bearded",
        "Silesia's capital, filling with German settlers.",
    ),
    (
        "gniezno",
        "Gniezno",
        "poland",
        "Wladislaw Spindleshanks",
        "Poland's old capital and the seat of its archbishop.",
    ),
    (
        "leczyca_town",
        "Leczyca",
        "poland",
        "The Count of Leczyca",
        "The town north of the covenant's ridge, whose name it took.",
    ),
    (
        "sieradz",
        "Sieradz",
        "poland",
        "",
        "A town about fifty miles west of the covenant.",
    ),
    (
        "riga",
        "Riga",
        "baltic",
        "Bishop Albert of Buxtehude",
        "The crusaders' city at the mouth of the Dvina, seat of the Bishop "
        "and the Knights of the Sword.",
    ),
    (
        "great_bulgar",
        "Great Bulgar",
        "russia",
        "",
        "The Muslim city of the Volga Bulgars, a great market for the "
        "east; home of Yakim ibn Rassur and the scholar Haroun Hashemi. "
        "The Mongols will raze it in 1237.",
    ),
)


def _towns(records: Records) -> None:
    b, p, w = records.b, records.places, records.world
    for key, name, place, ruler, summary in TOWNS:
        w[key] = b.town(name, place=p[place], ruler=ruler, summary=summary)


def _peoples(records: Records) -> None:
    b, p, w = records.b, records.places, records.world
    w["teutonic_knights"] = b.faction(
        "The Teutonic Knights",
        faction="Military order",
        decides="Its leader",
        ruler="Grand Master Hermann von Salza",
        realm="Divine",
        place=p["baltic"],
        summary="The German crusading order, its headquarters at Montfort "
        "near Acre; Conrad of Mazovia will soon invite it to fight the "
        "Prussians, and its Prussian crusade begins in 1230. The military "
        "orders carry a wrathful Divine aura (Pax Dei).",
    )
    w["knights_of_the_sword"] = b.faction(
        "The Knights of the Sword",
        faction="Military order",
        realm="Divine",
        place=p["baltic"],
        summary="The Brotherhood of the Sword, founded by Bishop Albert of "
        "Riga, conquering Livonia; they took Fellin in 1211. Any Baltic "
        "saga must reckon with them.",
        wants="The Baltic pagans converted or conquered",
    )
    w["baltic_pagans"] = b.faction(
        "The Baltic Pagans",
        faction="People or tribe",
        place=p["baltic"],
        summary="The Prussians, Lithuanians, Samogithians, Curs, Selonians, "
        "Semgallians, Livonians, Letts and Estonians, who keep the old "
        "gods with their priests (the Lithuanians' Vorschatyen, the "
        "Prussians' Waidelots) and their house snakes, the zaltys. The "
        "Lithuanians raid Polotsk; the Estonians will rise in 1223; a papal "
        "legate, William of Modena, comes in 1225.",
    )
    w["cumans"] = b.faction(
        "The Cumans",
        faction="People or tribe",
        place=p["steppe"],
        ruler="Khan Kotian",
        summary="The nomads of the southern steppe, a branch of the "
        "Kipchaks; Batiba of Three Lakes is one. Khan Kotian is Mstislav "
        "the Daring's father-in-law. If history holds the Mongols break "
        "them in 1223, and in 1239 Kotian leads forty thousand into "
        "Hungary.",
    )
    w["volkhvy"] = b.faction(
        "The Volkhvy",
        faction="Hedge coven",
        tradition="trad_volkhvy",
        realm="Faerie",
        place=p["russia"],
        rules="Each serves a principal god and a pagan community, and "
        "sings his magic; most are illiterate, their lore oral",
        summary=paragraphs(
            "The Slavs' pagan priest-wizards (Znachor in Poland, Waidelots "
            "in Prussia, Vorschatyen in Lithuania), who held the Order out "
            "until the princes turned Christian, and still keep the rites "
            "in pagan villages, where faeries greet them as cousins. They "
            "keep their villages' auras Slavic, and their Pagan "
            "Conviction is their Magic Resistance. The Tribunal officially "
            "ignores them; Thousand Caves admits them.",
            "Their gods are great faerie lords of Slavic Arcadia, beyond "
            "statistics: Svarog of fire and the sky and his sons "
            "Svarozhich, Dazhdbog and Khors; Perun of thunder and war; "
            "Mati-Syra-Zemlya the earth; Ersvorsh of weather and Stribog of "
            "the winds; Volos of poetry, oracles and trade; Mokosh, Kupala "
            "and Beilbog of healing and women; the three Zorya; Baba Yaga "
            "of death; the dark Chernobog, Kolyada and the Nameless God of "
            "Demons, whose priests are Koldun; and the Baltic Dievs, "
            "Saule, Mehnesis, Zemlja and the rest.",
        ),
    )
    w["vedun"] = b.faction(
        "The Vedun",
        faction="Hedge coven",
        realm="Faerie",
        place=p["russia"],
        summary="The Slavs' cunning folk, and every pagan household: in a "
        "Slavic faerie aura, ordinary believers can charm a loom to weave "
        "through the night, bless a field or ensure a safe birth by "
        "domestic magic.",
    )
    w["beslavichi"] = b.faction(
        "The Beslavichi",
        faction="Family",
        place=p["novgorod_lands"],
        ruler="Yury Beslav",
        summary="The prosperous trading family the north takes Three Lakes "
        "for, with reindeer sleds and agents across north Russia and the "
        "Baltic; its patriarch and his son are its magi.",
    )
    w["cult_of_hermes"] = b.faction(
        "The Cult of Hermes",
        faction="Faith or sect",
        place=p["urals"],
        summary="The faith Thousand Caves has preached to its tribes for "
        "thirty years, with new festivals, rites and idols of Hermes in "
        "the Great Cavern's sanctum; Nastassia leads its rites, and the "
        "girl Stenya Vassanovna says Lord Hermes speaks to her.",
    )
    w["hanse"] = b.faction(
        "The German Merchants of the Peterhof",
        faction="Gild",
        place=p["novgorod_lands"],
        summary="The German traders' court at Novgorod, the Baltic trade's "
        "eastern end.",
    )
