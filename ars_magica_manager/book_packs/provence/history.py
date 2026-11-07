"""The Provençal Tribunal's history, as the book tells it. The book has no
timeline of its own, so the dated events are gathered from its history
chapter, its chapter on Hermetic culture and each region's covenant
histories: the founding and fall of each covenant, the Tribunal's
meetings and rulings, the Wizard's Wars and Marches, and the Albigensian
Crusade year by year to 1219, each as a Tribunal Diary entry. The older
mundane history goes, era by era, into the Tribunal's History.

Dates are AD. Where the book gives one event two dates, the Diary takes
the one the 1221 Tribunal assumes and the entry mentions the other. What
the book foretells after spring 1220 is not an event yet, so it closes
the History under its Secrets heading."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import more_secrets, paragraphs, secrets, titled

if TYPE_CHECKING:
    from . import Provence

#: The order of the seasons within a year; an entry with none comes first.
SEASON_ORDER = {"": 0, "Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

#: (year, season, title, details, hidden): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str], ...] = (
    # -- Val-Negra and the early Order --
    (
        773,
        "",
        "Regional Tribunals created",
        "As the Order grows, the Second Grand Tribunal sets up regional Tribunals, made "
        "of covenants that lie near one another rather than of lands with fixed borders. "
        "The rules for founding and governing them come out of a quarrel over Val-Negra's "
        "charter: Flambeau wanted lordship over every covenant his home helped to found.",
        "",
    ),
    (
        774,
        "",
        "Val-Negra recognized",
        "After years of argument between Flambeau and Guernicus over its charter, the "
        "covenant of Val-Negra in the Pyrenees is formally recognized, and a regional "
        "Tribunal forms around it. Flambeau is the only Founder to make his home there, "
        "though Trianoma and Mercere visit often. Tolosa Paratge, a large Diedne covenant "
        "in a lake regio at Toulouse, is one of the four first covenants of the new "
        "Tribunal, and most of the region's other covenants belong to House Diedne.",
        "",
    ),
    (
        801,
        "",
        "Gelon becomes Primus of Verditius",
        "Gelon, the first apprentice of Verditius, becomes Primus of his House. He lives "
        "for decades at Val-Negra, forging his famous enchanted swords, and his followers "
        "go on to found the Confraternity of Roland.",
        "",
    ),
    (
        809,
        "",
        "Kaeso joins House Flambeau",
        "The Christian wizard Kaeso, whose power rests on an old underground temple of "
        "Mithras by the Garonne, joins House Flambeau. Training under Apromor and "
        "Flambeau in the Pyrenees, he forms the Hoplites, soldier-magi who hurl Pilum of "
        "Fire from behind a strong Parma Magica, and leads many of them into the Legion "
        "of Mithras. Many count him the first Hoplite.",
        "",
    ),
    (
        820,
        "",
        "Apromor becomes Primus of Flambeau",
        "Apromor, the Founder's first apprentice, who has drifted from his master's ways, "
        "becomes the first Primus of House Flambeau, and Kaeso's Hoplites carry on "
        "Flambeau's war against the sahirs of Iberia. Apromor welcomes pagan and "
        "non-Hermetic wizards into the Order, works with Priamitus of Mercere to revive "
        "the Cult of Mercury from the last Roman priests of the region, and spreads "
        "Val-Negra's outposts across the Pyrenees.",
        "",
    ),
    (
        821,
        "",
        "Portus Cottiae and Yf founded",
        "Julius Donnus, an outcast Mercurian of House Flambeau from the Greater Alps, "
        "founds Portus Cottiae outside Briançon as a second home for the revived Cult of "
        "Mercury, after Harco. It becomes the first Mercer House of the region and grows "
        "into a covenant of several sites, with chapter houses at Gap, Chorges and Embrun "
        "and a post at Oulx guarding the passes. In the same year Diedne magi found Yf on "
        "an island off the coast of Arelat.",
        "",
    ),
    (
        822,
        "",
        "Lapurdum founded",
        "Flambeau magi found Lapurdum where the Adour meets the sea in Gascony, around a "
        "mithraeum in what was once a Roman army camp.",
        "",
    ),
    (
        843,
        "",
        "Campus Elysii founded",
        "A small group of spirit masters, necromancers of Ex Miscellanea, settles in the "
        "crypts of the Alyscamps at Arles as the covenant of Campus Elysii.",
        "",
    ),
    (
        844,
        "",
        "Vikings on the Garonne",
        "King Pepin II of Aquitaine, seeking freedom from Charles the Bald, is accused of "
        "apostasy for letting the Viking Jarl Oscar sail his raiders up the Garonne to "
        "Toulouse. Northmen camp all along the western coast, and Marseilles has already "
        "been sacked by Arab pirates (838); Byzantine freebooters (849) and Normans based "
        "in the Camargue follow. Tales of rune-wizards among the raiders finally draw the "
        "magi in, and Flambeau comes to resent how little the Diedne do to help.",
        "",
    ),
    (
        850,
        "",
        "Castra Solis founded",
        "Raids on Gascon villages have grown since 840, and the Flambeau wrongly believe "
        "an organized Order of Odin is behind them. Kaeso returns to Bordeaux and "
        "fortifies his temple as a covenant, Castra Solis, the encampment of the sun, "
        "under the sign of a quartered sun.",
        "",
    ),
    (
        852,
        "",
        "Bordeaux falls to the Northmen",
        "Before the Hoplites can do more than raise hasty defences, the northern pagans "
        "take Bordeaux. Unwilling to harm the townsfolk, the magi spend five years trying "
        "to end the war by force against the rune-wizards alone, and many die in their "
        "traps, Kaeso among them.",
        "",
    ),
    (
        855,
        "",
        "Sinapis founded",
        "With Bordeaux too near the front, the surviving Flambeau build a fortified "
        "covenant, Sinapis, further north in Anjou. Castra Solis becomes a camp of tents "
        "for quick strikes, and to outsiders it looks like an offshoot of Sinapis.",
        "",
    ),
    (
        858,
        "",
        "Lapurdum abandoned",
        "Worn down by Viking raids and quarrels among its magi, Lapurdum is given up. "
        "Its ruins lie somewhere under the city of Bayonne.",
        "",
    ),
    (
        865,
        "",
        "Seven Tribunals defined",
        "The Grand Tribunal draws up seven regional Tribunals. Val-Negra goes to the "
        "Iberian Tribunal, along with the mountains and the Basque lands north of them; "
        "the bulk of France goes to the West Franks, and a strip from Friesland through Burgundy to "
        "Arelat forms the Lotharingian Tribunal.",
        "",
    ),
    (
        889,
        "",
        "Fraxinetum founded",
        "Two Tytalan war-magi, Sayyid Shajarat al-Darda (who called himself a Flambeau, "
        "though the House denies him) and his lieutenant Nasr ibn Amaf, settle in the "
        "Massif des Maures above St Tropez with a band of Andalusian raiders. Their "
        "covenant, named for the ash groves Sayyid planted, stays hidden from the "
        "Tribunal for its first century while it backs Moorish attacks on Provençal "
        "towns.",
        "",
    ),
    (
        895,
        "",
        "Barbegal founded",
        "Three Verditius mage-smiths found a covenant in the Roman watermill complex of "
        "Barbegal, just north of Arles.",
        "",
    ),
    (
        898,
        "",
        "Lotharingia divided",
        "The Grand Tribunal hands the northern covenants of the Lotharingian Tribunal to "
        "Normandy or the Rhine. What is left, the Kingdom of Arles along the Rhône and a "
        "few covenants in the Toulousain (a Mercer House at Arles, a strong Diedne "
        "covenant at Lyon, and a handful of others), comes to be called the Provençal "
        "Tribunal.",
        "",
    ),
    (
        901,
        "",
        "The Birds of Camargue founded",
        "Bjornaer magi found a covenant in the marshes at the mouth of the Rhône.",
        "",
    ),
    (
        906,
        "",
        "Portus Cottiae overrun",
        "Berber mountaineers overrun the scattered sites of Portus Cottiae, one of the "
        "first Lotharingian covenants to fall to the Saracens. Its magi flee down the "
        "Durance; at the motherhouse near Briançon the defenders bring the mountain down "
        "on the raiders and bury themselves in their own sancta. The one surviving maga, "
        "Anaïs of Jerbiton, reaches Avignon and becomes a loud voice for the Hermetic "
        "league that becomes the Coenobium.",
        "",
    ),
    (
        911,
        "",
        "Yf falls",
        "The Diedne covenant of Yf falls to the raids of Fraxinetum. One of its magae "
        "later joins the Coenobium to avenge it, but her line dies out shortly before "
        "the Schism War.",
        "",
    ),
    (
        930,
        "",
        "Barbegal abandoned",
        "The undefended mills of Barbegal are abandoned under Saracen raiding. The "
        "surviving smiths help to found the Rhône covenant of Coenobium Rhodanien.",
        "",
    ),
    (
        945,
        "",
        "Askelarre founded",
        "A coven of Hermetic sorginak, Basque witches spread across the Basque country, "
        "founds the covenant of Askelarre.",
        "",
    ),
    (
        955,
        "",
        "Sorginak join Ex Miscellanea; Donjon Leyre founded",
        "A few sorginak at last join House Ex Miscellanea, resented by their hedge sisters "
        "and anxious to keep their distance from the Diedne, who had long taken sorginak "
        "into their own House. In the same year Donjon Leyre, an early vassal of "
        "Montverte, is founded at the fork of the Leyre in the Landes as a base for raids "
        "into the Basque Pyrenees.",
        "",
    ),
    (
        970,
        "",
        "The Birds of Camargue merge into the Coenobium",
        "Threatened by Fraxinetum, the Bjornaer of the Birds of Camargue join the wider "
        "league of Rhône magi that becomes the Coenobium Rhodanien.",
        "",
    ),
    (
        973,
        "",
        "Maieul of Cluny captured",
        "The Moors of the Massif des Maures capture and ransom Maieul, abbot of Cluny, and "
        "push into the foothills of the Alps. The alarm this raises moves the mostly "
        "Jerbiton magi of eastern Provence to band together in a pact of mutual defence. "
        "Working through their families, churchmen and noble allies, they quietly back "
        "the army of William I of Provence, which routs the Moors at Tourtour.",
        "",
    ),
    (
        975,
        "",
        "Fraxinetum destroyed",
        "William's army takes the Moorish base and the Fraxinetum magi vanish into the "
        "forest. The history chapter says the Coenobium Rhodanien, which it calls newly "
        "formed (the Birds of Camargue had joined it in 970), destroyed the "
        "covenant by Wizard's War; the Arelat chapter says no war was ever openly "
        "declared and the league narrowly escaped the Quaesitors' anger for acting "
        "through mundane arms. Either way, the victors stay together as a covenant of "
        "many sites along the Rhône and the coast. In the same year Anaïs of Toulouse, a "
        "renegade Criamon expelled from her House, brings her followers, the Gorgiastic "
        "Cathars, into House Ex Miscellanea.",
        "The Fraxinetum magi did not perish. Their heirs live on in secret as Fraxinetum "
        "Redux on the Hyères islands, never declared to the Tribunal.",
    ),
    (
        997,
        "",
        "Grand Tribunal: the Northmen driven out",
        "At the Grand Tribunal the Hoplites declare the rune-wizards rooted out of the "
        "region after more than a century of war: all three Danish settlements on the "
        "coast have been burned. Many of their fortified outposts, such as the tower at "
        "Mimizan, later grow into covenants counted as offshoots of Castra Solis. The "
        "Diedne, uneasy with the Mithraic piety of the Hoplites, took no part, which "
        "deepens Flambeau's suspicion of them.",
        "",
    ),
    # -- The Schism War --
    (
        1008,
        "",
        "Donjon Leyre falls",
        "All the founding magi of Donjon Leyre die fighting in the Schism War, which "
        "rages through Gascony as Val-Negra's forces storm the Diedne covenants one "
        "after another; many Gascon Diedne burn their own sites and flee.",
        "",
    ),
    (
        1009,
        "",
        "Campus Elysii driven out",
        "The spirit masters of Campus Elysii, who hid underground through the war, are "
        "forced out of the Alyscamps when the Coenobium stirs up the townsfolk with "
        "tales of diabolists under the necropolis. They try to begin again in a cave "
        "network in the Verdon gorge as Portus Termini, but all contact is lost before "
        "the next Tribunal and the new covenant is never registered.",
        "Many suspect that Hoplites in the Coenobium's pay hunted down the survivors.",
    ),
    (
        1011,
        "",
        "Askelarre destroyed",
        "The sorginak covenant of Askelarre is destroyed in the Schism War. Two of "
        "Val-Negra's magi, the Flambeau Leo Augustus and the Tremere Vegetius, die "
        "in the attack.",
        "",
    ),
    (
        1012,
        "",
        "The fall of Val-Negra",
        "As the Schism War draws to its close, while its zealous magi are away striking at "
        "the Diedne, five Diedne archmagi storm Val-Negra. Of twenty-five magi at the war's "
        "start, only four are left. Shortly before the war many of its Flambeau had left, "
        "after a vision, to found Aedes Mercurii in Val-Negra's outlying halls; now the "
        "survivors join it, and it declares itself a Provençal covenant and the heir of "
        "Val-Negra. Many other covenants change to the Provençal Tribunal at this time, "
        "partly to keep Tytalus from claiming the spoils of the fallen Diedne. The "
        "domus magna of Flambeau moves to Castra Solis, and the Quaesitors strike nine or "
        "more Diedne sites from the records. Why Val-Negra was never rebuilt, and even "
        "where it stood, is soon forgotten.",
        "The Diedne reached the Iron Door in the depths of Val-Negra, and in the fighting "
        "the Adulteration of Flambeau was loosed. It killed three defenders and all the "
        "attackers before the last two archmagi forced it back and sealed the door with "
        "a Hermetic ward, one that breaks if the door is simply opened. The Quaesitors "
        "kept it quiet and ruled that Val-Negra must never rise again.",
    ),
    (
        1016,
        "",
        "Bellaquin founded",
        "As the Schism War dies down, Flambeau magi restore an abandoned castle, the "
        "Château de Penne in Tarn above the Aveyron, as a stronghold. The war ends before "
        "it is needed, and they hand it to House Jerbiton, who make it one of the most "
        "admired covenants in the Order and, in time, the lords of a fief of their own.",
        "",
    ),
    # -- Peace and expansion --
    (
        1050,
        "",
        "Mistridge founded",
        "A covenant is founded in the Val du Bosque, in a tower raised by magic at the "
        "brink of a sheer drop.",
        "",
    ),
    (
        1060,
        "",
        "Windgraven founded",
        "Necromancers found Windgraven in the squat stone towers of a ruined Visigothic "
        "fort on a rocky plateau in the southern part of the County of Toulouse.",
        "",
    ),
    (
        1063,
        "",
        "Filii Sinapis founded",
        "Flambeau magi from the abandoned Normandy covenant of Sinapis found Filii "
        "Sinapis.",
        "",
    ),
    (
        1089,
        "",
        "Berinor founded",
        "Jerbiton magi found Berinor, a small covenant in the County of Toulouse that "
        "becomes a patron of troubadours and trobairitz.",
        "",
    ),
    (
        1103,
        "",
        "Gascony joins the Provençal Tribunal",
        "When the Normandy Tribunal splits, Castra Solis leads a faction into the "
        "enlarged Provençal Tribunal. The magi of Sinapis leave their site to join the "
        "domus magna, and smaller covenants of the area, Mimizan among them, come too.",
        "",
    ),
    (
        1106,
        "",
        "Bentalone founded",
        "A covenant is founded in a castle in the Toulousain; it stays in Summer for a "
        "century.",
        "",
    ),
    (
        1129,
        "",
        "Grand Tribunal: the Occitan border",
        "To settle quarrels between Normandy and the newly enlarged Provençal Tribunal, "
        "the Grand Tribunal rules that the border between them runs wherever Occitan "
        "stops being spoken. Unpopular at first, the rule is soon embraced by the "
        "southern magi to secure their claims to vis, and the Tribunal's minutes and "
        "proclamations are written in both Latin and Occitan.",
        "",
    ),
    (
        1174,
        "",
        "The Golden Court at Beaucaire",
        "Count Henry II of Provence holds a festival in the meadows north of Beaucaire to "
        "mark the reconciliation of the Duke of Narbonne and the King of Aragon. A "
        "chronicler praises its hundred thousand knights, its gold sown in the earth and "
        "its herds roasted over wax torches.",
        "Most of the knights were faeries revelling in the troubadours' spirit of "
        "foolishness, and the gold was glamour; the meadow still holds Faerie vis.",
    ),
    (
        1177,
        "",
        "Saint Jean Pied-de-Port razed",
        "When Richard the Lionheart sacks Saint Jean Pied-de-Port, the large outpost "
        "Aedes Mercurii kept there is lost; its covenfolk had already fallen under the "
        "townsfolk's suspicion of witchcraft.",
        "",
    ),
    (
        1180,
        "",
        "Miniata Sophia founded",
        "A Criamon eremite founds Miniata Sophia in the cave system of Niaux, about forty "
        "years before 1220. For a decade and more it keeps to itself.",
        "",
    ),
    (
        1192,
        "",
        "Lariander founded",
        "Tremere magi found Lariander, a young covenant in a faerie wood near the "
        "village of Montgey in the Toulousain.",
        "",
    ),
    (
        1193,
        "",
        "Tribunal: Miniata Sophia announced",
        "Miniata Sophia makes itself known at the Tribunal and registers its site, the "
        "village of Niaux, with the Redcaps. It has attended every meeting since, voting "
        "on each question as seems most apt or abstaining, and making no alliances.",
        "",
    ),
    (
        1195,
        "",
        "Ara Maxima Nova founded",
        "Merinita magi who have explored the labours of Heracles in the east come west to "
        "follow the rest of his journey and found Ara Maxima Nova among the vineyards "
        "outside Perpignan, close to the Via Domitia. Their charter binds them to seek "
        "the Hesperides every five years.",
        "",
    ),
    (
        1197,
        "",
        "Windgraven destroyed",
        "Magi of Mistridge destroy Windgraven in a properly declared Wizard's War, "
        "battering its towers flat with giant stones conjured by magic. Few mourn its "
        "necromancers, who were widely thought diabolists, and the war foreshadows "
        "Mistridge's own end.",
        "",
    ),
    (
        1200,
        "",
        "Bellaquin falls",
        "Overstretched by its feudal ties, Bellaquin tries to help two warring lords at "
        "once and is accused by both of stirring up their war. With churchmen urging "
        "them on, and a companion betraying the covenant, they storm the Château de "
        "Penne by surprise and kill several magi. The survivors, warned to prepare by "
        "archmagi, take their hidden reserves, destroy what they cannot carry and leave "
        "the site to their mundane proxies. Since the harm fell only on Bellaquin, no "
        "charges are brought.",
        "Some suspect other magi had a hand in arranging the mundane attack.",
    ),
    (
        1202,
        "",
        "Bellaquin moves to Andorra",
        "Bellaquin settles in a house in the parish of Ordino in Andorra, keeping its "
        "charter but changing its ways: subtler, richer and turned toward banking.",
        "",
    ),
    # -- The crusade --
    (
        1207,
        "Spring",
        "Raimond VI excommunicated",
        "In May Count Raimond VI of Toulouse is excommunicated for sheltering heretics. "
        "He promises the pope to drive them out, and the sentence is lifted in August.",
        "",
    ),
    (
        1207,
        "Summer",
        "Tribunal at Aedes Mercurii",
        "The Tribunal meets at Aedes Mercurii and spends a whole day on the Church's "
        "drive against the Cathars, without deciding anything. Oxioun of Tytalus, leader "
        "of the host covenant, urges the Order to stay out of mundane affairs, and the "
        "Mercurian bloc is content to wait in its mountains, despite the worries of the "
        "lowland covenants of the Toulousain, the Narbonnais and the Rhône.",
        "",
    ),
    (
        1207,
        "",
        "Bentalone overrun",
        "The book's list of fallen covenants ends Bentalone in 1207: Simon de Montfort's "
        "army takes its castle for a Cathar stronghold and storms it in a surprise "
        "attack, though his campaigns in the south only begin in 1209.",
        "",
    ),
    (
        1208,
        "Winter",
        "The legate murdered",
        "In January Raimond meets the papal legates at St Gilles, stalls, and threatens "
        "them in anger as they leave. At dawn, waiting for the ferry to Arles, the "
        "legate Pierre de Castelnau is run through by a knight, forgiving his killer as "
        "he dies. Innocent III blames the count and proclaims a crusade; Arnaud Amaury "
        "and Bishop Foulques preach it, promising the crusaders a share of heretic lands "
        "and release from their debts to Jewish lenders.",
        "",
    ),
    (
        1208,
        "",
        "Protantus dies; Tibaut chief Quaesitor",
        "A few months after the 1207 Tribunal, Protantus, the Traditionalist chief "
        "Quaesitor, dies and is followed by the more flexible Tibaut, a Transitionalist "
        "with no ties to the Mercurians. Few magi remark the coincidence with the "
        "legate's death, but it marks a turning point. The history chapter tells it so; "
        "the Gascony chapter names Senex as chief Quaesitor until 1210, with Tibaut "
        "acting in his place only from 1214.",
        "",
    ),
    (
        1208,
        "",
        "Interdict in Gascony",
        "Innocent III lays all of King John's lands under interdict. Many Gascon churches "
        "close their doors and say no Mass for six years.",
        "During the interdict a band of demons, the Six Deadly Spirits, settles in the "
        "wild lands of Gascony away from the pilgrim roads, and some linger there still.",
    ),
    (
        1209,
        "Summer",
        "Raimond joins the crusade",
        "As the crusaders muster at Lyon, Raimond is scourged barefoot before a crowd at "
        "St Gilles and accepts hard terms. In June he takes the cross himself, robbing "
        "the crusade of its main target, which turns on the Trencavel lands instead. "
        "Raimond-Roger Trencavel is refused leave to join.",
        "",
    ),
    (
        1209,
        "Summer",
        "The sack of Béziers",
        "Béziers refuses to hand over two hundred heretics. When its young men sally "
        "against the crusade's camp followers, the rabble surges through the open gate "
        "and the knights follow. Asked how to tell the faithful from the heretics, Arnaud "
        "Amaury is said to have answered that God would know His own. Fifteen to thirty "
        "thousand die, many in the churches.",
        "",
    ),
    (
        1209,
        "Summer",
        "Carcassonne surrenders",
        "In August Viscount Raimond-Roger Trencavel leaves Carcassonne to parley and is "
        "seized and imprisoned. The city yields; its people are spared but its "
        "treasures plundered. Why so strong a city gave in so soon remains a mystery.",
        "",
    ),
    (
        1209,
        "Autumn",
        "Simon de Montfort leads the crusade",
        "When the great lords go home after their forty days, the legate's council "
        "chooses Simon de Montfort, a minor knight of the Île de France, to lead. With "
        "his wife Alice, thirty knights and five hundred foot he holds Carcassonne and "
        "takes the Trencavel titles of Béziers and Carcassonne, but Pedro II of Aragon will "
        "not take his homage. Revolts follow, the abbot of St Gilles is murdered, and de "
        "Montfort answers with the atrocity at Bram. In Toulouse Bishop Foulques forms "
        "his White Brotherhood against heretics, Jews and moneylenders, and a Black "
        "Brotherhood rises against it.",
        "",
    ),
    (
        1209,
        "Winter",
        "Mistridge destroyed",
        "The Rusticani magus Tres declares Wizard's War on every magus of Mistridge. With "
        "two other magi of his tradition and a company of mercenaries armed with his "
        "enchanted weapons, he levels the tower with magical siege engines and kills its "
        "defenders. Some say he avenged Windgraven; others that Mistridge had scorned him "
        "as a hedge wizard.",
        "",
    ),
    (
        1210,
        "",
        "Minerve and Termes fall",
        "When the castle of Aguilar holds out, de Montfort turns to besiege Minerve, where a hundred and thirty-seven Cathars are burned and only "
        "three women recant. Termes and more castles follow, making him master of the "
        "Trencavel lands. So few heretics have died that the war is plainly one of "
        "conquest.",
        "",
    ),
    (
        1210,
        "",
        "Berinor falls; Senex vanishes",
        "Berinor falls when de Montfort's men dispossess the lord who held its castle, "
        "and its survivors take refuge at Tolosa Paratge. The same year Senex of "
        "Guernicus, the chief Quaesitor, goes into a village to look into something and "
        "is never seen again.",
        "Senex had begun to look into Dama's cult of the Matres and Matrones. While she "
        "was away at an akelarre he slipped into her sanctum at Mimizan; she came back "
        "early and caught him there. Her Revoke the Protection of Bonisagus and Maju's "
        "venom killed him, Maju devoured the body as a drake, and Dama told no one. In "
        "law he had forfeited his immunity by entering her sanctum.",
    ),
    (
        1211,
        "",
        "Lavaur, and the first siege of Toulouse",
        "Pedro II at last accepts de Montfort's homage and tries to broker peace, but the "
        "legates' terms are too harsh and the south rises. Lavaur is sacked, sixty "
        "Cathars taken at Les Casses are burned, and de Montfort besieges Toulouse. "
        "Bishop Foulques tells the faithful to give up the city and their count or share "
        "the heretics' fate; they drive him out instead, and the siege fails.",
        "",
    ),
    (
        1211,
        "Summer",
        "Montgey and the fall of Lariander",
        "Peasants and southern knights massacre some three hundred German crusaders "
        "marching through a faerie forest near Montgey to Lavaur. In reprisal the "
        "crusaders destroy the village, burn the woods and slaughter the Tremere of "
        "Lariander, taking their black robes for those of Cathar perfecti. Garsenda of "
        "Lariander believes she is the only survivor.",
        "Garsenda had stirred the villagers to the ambush, and the white ladies and "
        "walking trees the survivors spoke of were real.",
    ),
    (
        1211,
        "Autumn",
        "Battle of St Martin-Lalande",
        "Raimond gathers his army against de Montfort's small force, but the crusaders "
        "keep raiding and seizing the initiative, and when the southerners finally attack "
        "they are routed in open battle.",
        "",
    ),
    (
        1212,
        "",
        "The Children's Crusade; Las Navas de Tolosa",
        "Thousands of children and peasants follow a young visionary from the Rhineland "
        "through France to Marseilles, sure the sea will open for them. It does not; "
        "many board ships for Africa and vanish, feared sold as slaves. In Iberia the "
        "Christian kings win the great victory of Las Navas de Tolosa.",
        "",
    ),
    (
        1213,
        "Autumn",
        "Battle of Muret",
        "Pedro II of Aragon, Raimond and the count of Foix take Muret, ten miles up the "
        "Garonne from Toulouse, with a great army. De Montfort crosses the marshes to "
        "fall on their flank: Pedro is killed and some ten thousand die in under half an "
        "hour, many drowning in the river, where their cries are still heard in flood. "
        "Resistance is broken for years, and Raimond seeks redress in Rome.",
        "",
    ),
    (
        1214,
        "",
        "Tribunal at Castra Solis",
        "The meeting set for Toulouse moves to Castra Solis, with de Montfort's army "
        "outside the city, to the Mercurians' annoyance. It is the most bitter gathering "
        "since the Schism War, taken up with the crusade and charges of meddling with "
        "mundanes: some blame Normandy magi, some Flambeau blame Tytalus for the crusade "
        "itself. Tolomae of Jerbiton calls for open Hermetic resistance and is thrown out "
        "of the debate, swearing revenge on the Mercurians and on the Coenobium. Aedes "
        "Mercurii threatens to walk out and so void the Tribunal, until Tibaut and the "
        "chief Redcap Alazais, who threatens to stop all Redcap service, avert anarchy. "
        "Senex is absent, and Tibaut acts as chief Quaesitor.",
        "",
    ),
    (
        1214,
        "",
        "Ruling: Tres acquitted",
        "Charges are brought against Tres for arming mercenaries with enchanted weapons, "
        "calling them his grogs, and using them to destroy Mistridge. However deplored, it "
        "was a lawfully declared Wizard's War and no ruling forbids grogs in one; the "
        "vote goes narrowly his way. Tres flees into hiding from Mistridge's friends, and "
        "after the meeting the Hermetic faidits begin to gather at Aguilar as the Ostal "
        "des Exiles, Rixenda of Mistridge first and Gilbert of Flambeau their leader.",
        "",
    ),
    (
        1215,
        "",
        "De Montfort enters Toulouse; Filii Sinapis abandoned",
        "Simon de Montfort enters Toulouse in triumph and takes up residence in the "
        "Château Narbonnais. The Waldensians are condemned as heretics, though Innocent "
        "III thought them good Christians. Filii Sinapis is abandoned in the wake of the "
        "crusade.",
        "",
    ),
    (
        1216,
        "",
        "Tolomae declared orbus; Tibaut confirmed",
        "House Jerbiton expels Tolomae of Bellaquin, leader of the Procrustean League, "
        "which calls for open war on the Church, and declares him orbus. He is suspected "
        "of the legate's murder and flees rather than answer the Quaesitor's questions. "
        "With Senex absent two years, Tibaut is confirmed as chief Quaesitor. In Toulouse "
        "an autumn rising is put down with great effort, and de Montfort names himself "
        "count of Toulouse.",
        "",
    ),
    (
        1217,
        "Autumn",
        "Raimond returns to Toulouse",
        "While de Montfort campaigns in the north, Raimond slips back into Toulouse to the "
        "citizens' joy. De Montfort finds the gates shut against him and lays siege for "
        "months.",
        "Tibaut, who found the first threads of Senex's inquiry in his laboratory notes, "
        "begins this year to investigate the Tribunal's mystery cults, the Cathars and "
        "the sorginak, sharing his suspicions with his filia Beatrice. A letter he sent "
        "her lies in the satchel of a Redcap who died of crusaders' wounds along the Via "
        "Domitia.",
    ),
    (
        1218,
        "Spring",
        "Tolomae Marched",
        "Early in the year Tolomae is Marched for repeatedly meddling with mundanes, and "
        "slain. His suspected supporters scatter among other covenants or hide among the "
        "faidits.",
        "",
    ),
    (
        1218,
        "Summer",
        "Simon de Montfort killed",
        "A stone from a siege engine on the walls of Toulouse strikes Simon de Montfort "
        "on the head and kills him. Amaury de Montfort claims his titles, and Alice "
        "remains a leader of the campaign, but Simon's great domain begins to fall apart.",
        "Some suspect the engine was one of those Tres built to destroy Mistridge.",
    ),
    (
        1218,
        "Summer",
        "Wizard's Wars at Tolosa Paratge",
        "In the weeks before de Montfort's death, Augustus of Tolosa Paratge, a senior "
        "Quaesitor, is persuaded by Bishop Foulques that Toulouse will fall and asks the "
        "covenant's Gorgiastic Cathars to leave for their safety. They refuse; Marc "
        "declares Wizard's War on him and, believing him possessed, kills him in the "
        "tower. Within the month St Tropez declares Wizard's War on the unresisting Marc and "
        "kills him. Under Mariola, the covenant splits into the Blacks, who hold it, and "
        "the Whites, who plot in the city to retake it.",
        "",
    ),
    (
        1218,
        "Winter",
        "Siege of Marmande",
        "Soon after Christmas, Prince Louis's crusaders under Centule d'Astarac besiege "
        "Marmande.",
        "",
    ),
    (
        1219,
        "Summer",
        "Marmande massacred; Toulouse besieged",
        "After nine months Marmande surrenders on terms. Amaury de Montfort, urged by the "
        "Bishop of Saintes, then kills all five thousand townsfolk and their beasts and "
        "burns the town. Prince Louis's royal crusade besieges Toulouse but withdraws "
        "when pestilence breaks out in his army, and Raimond begins to win back his "
        "county.",
        "",
    ),
    (
        1219,
        "",
        "Tibaut dies",
        "Tibaut, the Presiding Quaesitor, dies in the care of the monks of Saint Hilaire, "
        "taken for a Cathar by crusaders who later raid the abbey. His body is buried "
        "there and his belongings sit locked in the abbot's chest. At Dama's suggestion "
        "his filia Beatrice of Guernicus fills the office until the 1221 Tribunal. (The "
        "Hermetic culture chapter also says once that he died in 1214; the 1221 "
        "Tribunal takes 1219.)",
        "Warned by Luc of Ara Maxima Nova of Tibaut's questions, Dama ambushed him with "
        "Maju near the road to Foix. Her Revoke the Protection of Bonisagus shattered his "
        "Parma, but Maju's venom worked slowly; he staggered into the road and "
        "divinely blessed crusader knights carried him to the abbey before she could "
        "reach him. Before he died he confided something to the knights.",
    ),
)

#: The mundane history of the south, era by era, for the Tribunal's
#: History.
ERAS: tuple[tuple[str, str], ...] = (
    (
        "The Roman Provincia",
        "In antiquity the Aquitanians, a Basque people, held what is now Gascony, and "
        "Greek traders from Massalia founded Marseilles and Trinquetaille and traded up "
        "the rivers with the Celts of Arelat. Rome came in 125 BC and split its "
        "Provincia into Novempopulania facing the Atlantic and Narbonensis facing the "
        "Mediterranean, and both prospered for five centuries. The one great revolt came "
        "in 106 BC, when a governor drained the sacred lake of the Tolosates to take the "
        "gold sunk in it; with the Cimbri's help the rebels beat Rome at Arausio in 105 "
        "BC, and the treasure was lost and never found.",
    ),
    (
        "The coming of Christianity",
        "Tradition says Mary Magdalene and the Virgin landed at Saintes-Maries-de-la-Mer, "
        "and Lazarus became the first bishop of Marseilles. The land kept to the Roman "
        "gods until Bishop Sernin of Toulouse was dragged to death behind a bull in 257; "
        "his martyrdom broke the Cult of Mercury in the city, which became a centre of "
        "the new faith.",
    ),
    (
        "Visigothic Septimania",
        "Rome withdrew in 419 and the Visigoths, Arian allies of the empire, settled "
        "Narbonensis by treaty in 462, gave up its lands east of the Rhône in 475 for "
        "full independence, and took Arles in 472. Their kingdom, named Septimania for "
        "its seven cities, ruled from Toulouse until Clovis beat them at Vouillé in 507. "
        "The Ostrogoths checked the Franks, and Visigothic kings held the Narbonnais "
        "until the 720s. Converted to the mainstream faith by the mid-sixth century, the "
        "Goths still kept old customs, and the last Roman flamens of the Cult of Mercury "
        "kept secrets that Priamitus and Apromor would later seek.",
    ),
    (
        "Franks and Moors",
        "Under the Merovingian Franks a dark age of usurpation, plague and famine fell on "
        "the land; Roman cities in Arelat emptied, marshes swallowed old fields, and the "
        "lords of Toulouse made themselves dukes all but free of the crown. The Moors "
        "took Narbonne in 719 and marched on Toulouse, where Duke Odo of Gascony and "
        "Toulouse beat them in 721, buying time for Charles Martel's victory at Tours in "
        "732. The Franks took Septimania in 759 and the Pyrenees by the century's end, "
        "but their southern dukes rebelled again and again.",
    ),
    (
        "Charlemagne",
        "Charlemagne crushed the southern lords in 770 on his way to Spain. In 778 he "
        "besieged the Moor Mirat at Lourdes, who surrendered and was baptised, and on "
        "the way home from Spain his rearguard was cut down at the pass of Roncevaux. "
        "The deaths of Roland and Bishop Turpin are the troubadours' most beloved tale.",
    ),
    (
        "The counts of Toulouse",
        "By the ninth century Toulouse's counts had again slipped free of the distant "
        "Frankish throne, reaching their height under Raimond IV, count of St Gilles and "
        "marquis of Arelat (1093 to 1105), when Occitan letters and the troubadours "
        "flowered. The counts feuded with Foix and with the Trencavel of Carcassonne "
        "and Béziers, clashed with the bishops who share justice in Toulouse and with "
        "the rising capitouls, and bought popular support with privileges, so that the "
        "county is full of knights and ladies holding their own castles. Notaries, heirs "
        "of Roman law, appeared in the Narbonnais in the 1140s alongside the consular "
        "towns.",
    ),
    (
        "Heresy",
        "Cathar belief took root in the tenth century and by 1220 rivals the Church in "
        "the south. Bernard of Clairvaux preached against it for one summer in 1145, "
        "with success in Albi and Toulouse and scorn in the countryside. The Council of "
        "Tours condemned the heretics and those who sheltered them in 1163; churchmen "
        "found them heretical at Lombers in 1165 but let them go, and by 1167 they had "
        "bishops of their own. The Third Lateran Council called for arms against them in "
        "1179, a legate's army besieged Lavaur in 1181 to little effect, and two legates "
        "sent in 1203 found the southern bishops corrupt and immovable. Arnaud Amaury "
        "was made legate and Foulques bishop of Toulouse, a see so low he dared not live "
        "in it. Dominic of Guzman walked barefoot among the heretics from 1206 to 1208, "
        "winning more love than converts.",
    ),
)

#: What lies ahead after spring 1220, for a saga that follows the book.
FUTURE = [
    titled(
        "The Tribunal of 1221",
        "The Tribunal next meets in summer 1221 at the ruins of Glanum, a neutral "
        "site agreed on by all; its first business is whether Beatrice of Guernicus "
        "succeeds Tibaut as Presiding Quaesitor.",
    ),
    titled(
        "Dama's Longevity Ritual",
        "Dama must renew her Longevity Ritual before 1232.",
    ),
    titled(
        "Storyguide Notes",
        paragraphs(
            "If the Tribunal resolves to act against the crusade and the Church, "
            "the Pyrenean covenants may boycott the meeting of 1227 and, with the "
            "four covenants a Tribunal needs, ask the Grand Tribunal of 1228 to "
            "let them secede.",
            "If the saga follows history, Guy de Montfort is killed near "
            "Castelnaudary in April 1220, James I of Aragon comes of age in 1223, "
            "the count of Foix defies Louis in 1226 and 1227, and the crusade "
            "ends in 1229.",
        ),
    ),
]


def build(provence: Provence) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, in order of
    year and season, and add the mundane history, by era, to the
    Tribunal's History, with what lies ahead under Secrets. Nothing is
    written when the Tribunal has not been made yet (the parts build in
    order, this one after the Tribunal's)."""
    tribunal = provence.tribunal
    if tribunal is None:
        return
    for year, season, title, details, hidden in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        provence.b.event(tribunal, year, title, secrets(details, hidden), season=season)
    eras = paragraphs(*(f"{title}. {text}" for title, text in ERAS))
    # Any history already written keeps its place, its secrets ahead of ours.
    tribunal.history = paragraphs(tribunal.history, eras)
    tribunal.secrets = more_secrets(tribunal.secrets, FUTURE)
