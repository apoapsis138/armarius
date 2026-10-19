"""The Transylvanian Tribunal's history, as the book tells it. The book has
no timeline of its own, so the dated events are gathered from every
chapter: the Order's founding and the Sundering, the Curators of
Tablinum, each oppidum's founding and the deeds of its magi, and the
mundane history of Hungary, Bulgaria, Serbia, Croatia and the
Teutonic Knights, each as a Tribunal Diary entry, up to spring 1220.
What the book tells without a year (the Founder's deeds at Coeris, the
legal covenants' first sites, the Schism War) and the older history of
the lands go, era by era, into the Tribunal's History.

Dates are AD. Where the book gives only a rough date ("about a hundred
years ago", "in the mid-800s") the entry takes a round year and says
so. Where the book slips on a ruler's name or a date, the entry uses
history's and gives the book's in brackets. What lies ahead after 1220
is not an event yet, so it closes the History under its Secrets
heading; the threats themselves are the Stories part's."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import SECRETS, paragraphs, secrets

if TYPE_CHECKING:
    from . import Transylvania

#: The order of the seasons within a year; an entry with none comes first.
SEASON_ORDER = {"": 0, "Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

#: (year, season, title, details, hidden): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str], ...] = (
    # -- The Order and the Sundering --
    (
        767,
        "",
        "The Order of Hermes founded",
        "The Order is founded. The Transylvania Chronicle, kept in Tablinum's "
        "exhibit hall, begins its record with this year, though sceptics note how "
        "little it says of House Tremere's beginnings.",
        "",
    ),
    (
        780,
        "",
        "A skirmish at the Shipka Pass",
        "In the Order's first years the Founder Tremere fights a band of Theban magi "
        "at the Shipka Pass, the best road through Bulgaria's mountains. A regio "
        "lies beside the battlefield: some say Tremere knew of it and laid his "
        "ambush from it, others that a Twilight born of the fight's strain made it. "
        "For long afterwards House Tremere and the Theban covenants meet there to "
        "reflect and to sign their treaties. (The book gives no year.)",
        "",
    ),
    (
        803,
        "",
        "Krum takes Hungary and Transylvania",
        "Khan Krum the Conqueror adds the lands of Hungary and Transylvania to the "
        "First Bulgarian Empire.",
        "",
    ),
    (
        810,
        "",
        "Tremere wears the Roman dragon's face",
        "Early in the ninth century, when dragon raids flare up in defiance of the "
        "Pax Draconis, the Founder Tremere takes the shape of Fetillusclaviceps, the "
        "Roman dragon who made the peace, and puts down the rebels. He never speaks "
        "of it, and whatever record of his reasons existed was lost in the "
        "Sundering. (The book gives no exact year.)",
        "",
    ),
    (
        814,
        "",
        "Death of Krum",
        "Krum, who had beaten two Byzantine emperors in battle and laid siege to "
        "Constantinople, dies suddenly, and no one knows quite how.",
        "",
    ),
    (
        848,
        "",
        "The Sundering",
        "Tremere's bid to master the Order ends in the Sundering. No longer trusting "
        "his domus magna at what is now Lycaneon, he moves his seat, and its name, "
        "to Coeris in Maramures, where the Covenant of Asclepius then stood; "
        "Lycaneon stays the House's manufactory. His successor Albanus turns the "
        "Order's anger at Tremere's memory into a means of binding the House "
        "together. A Grand Tribunal caps the Tribunal at five named covenants, "
        "Coeris, Domostron, Asclepius, Diodorus and Pannonia, which still exist in "
        "law though every one has since moved or changed its membership. To keep "
        "the others from seceding, Tremere grants concessions to their leaders, "
        "and the covenants bind one another by contract; the Triumph of Asclepius "
        "is still paid from them.",
        "",
    ),
    (
        850,
        "",
        "Akilina finds Tablinum's site",
        "The maga Akilina comes upon a place in the Danube delta where many regiones "
        "lie one over another, the future site of Tablinum. (The book says only the "
        "middle of the ninth century.)",
        "",
    ),
    (
        878,
        "",
        "Tablinum founded",
        "In the years after the Sundering Tablinum is founded as a storehouse for "
        "artifacts, with Akilina its first Curator. Since the Tribunal may hold only "
        "five covenants, it has no official standing and no recognised residents "
        "until the custom of oppida spreads, when it remakes itself as an oppidum "
        "with Curators who live there. Its founders are said to have walked a "
        "ritual path through the regiones, fixing an Arcane Connection to each "
        "level and destroying the path behind them.",
        "",
    ),
    (
        886,
        "",
        "Cyril and Methodius's church in Bulgaria",
        "Boris I, the first Christian khan of Bulgaria, baptised Michael, welcomes "
        "the mission of Saints Cyril and Methodius, from which the Bulgarian Church "
        "takes its descent.",
        "",
    ),
    (
        900,
        "",
        "Potitus opens Tablinum",
        "Akilina names her apprentice Potitus her successor and resigns. The first "
        "Curator to make his home at Tablinum, he opens what had been a closed "
        "storehouse to study. By this year the Chronicle already mentions its "
        "regiones and the Arcane Connections that reach them.",
        "",
    ),
    (
        917,
        "",
        "Akilina vanishes",
        "Tablinum's first Curator disappears and is presumed dead.",
        "",
    ),
    (
        926,
        "",
        "Symeon's Bulgarian Church",
        "Symeon, son of Boris and the first Bulgarian ruler to style himself tsar "
        "rather than khan, makes the Bulgarian Church autonomous. By the peace of "
        "927 the patriarch of Constantinople accepts its independence, and it soon "
        "has a patriarch of its own.",
        "",
    ),
    (
        946,
        "",
        "Tiberia shares the Curatorship; Saint Ivan of Rila dies",
        "Potitus appoints Tiberia, a Tremere general, as his successor, and for a "
        "short time the two share the office; Potitus's term ends in 948. In the "
        "same year the hermit, healer and mystic Ivan Rilski dies; his body, "
        "still uncorrupted, now lies at Tarnovo, and he is Bulgaria's patron "
        "saint.",
        "",
    ),
    # -- The Schism War --
    (
        1001,
        "",
        "Evredika instituted",
        "The Cult of Orpheus had worshipped in the Rhodope mountains for decades as "
        "an informal cult, and when it joined the Order its sacred sites there "
        "became Hermetic ground. In this year Evredika, named for Eurydice in the "
        "Bulgarian tongue, becomes a formal oppidum.",
        "",
    ),
    (
        1005,
        "",
        "The zenodochia devised",
        "During the Schism War the Tremere generals plan a network of tiny hidden "
        "hospitals, the zenodochia, reasoning that one hospital oppidum would be "
        "found and destroyed in time, while a web of small ones could not be, and "
        "that no single captured magus would know more than a few of them. Hundreds "
        "are planned; many are never built. (The book gives no year.)",
        "",
    ),
    (
        1007,
        "",
        "Tiberia falls; Anatolus Curator",
        "Tiberia is killed in the Schism War. Anatolus, also a Tremere general, "
        "succeeds her, the first Curator of Tablinum chosen by the Tribunal rather "
        "than by the one before. He becomes known for strange battle magic, said "
        "to come from Tablinum's halls.",
        "",
    ),
    (
        1008,
        "",
        "Kezdö Válasz founded",
        "Norsius of House Tremere, more scholar than soldier, founds Primum "
        "Responsans, better known by its Hungarian name Kezdö Válasz, to guard the "
        "Tribunal's borders in the Schism War. Taking Trajan's Wall as his model, "
        "he builds a few forts in magic auras near the frontier, each with two magi "
        "who study between alarms; his own first fort stands in the ruins of "
        "Sarmizegethusa, Decebalus's palace. The war never reaches Transylvania, "
        "and the forts are never tested. Later his filius Gasparus spreads the "
        "forts across the whole Tribunal and has each pair of magi move to a new "
        "one after every Tribunal meeting.",
        "",
    ),
    (
        1018,
        "",
        "Bulgaria falls to Byzantium; Anatolus slain",
        "The First Bulgarian Empire, founded by Asparukh's Bulgars, falls to "
        "Byzantine rule. The Bulgarian Church loses its independence, is reduced to "
        "an archbishopric at Ohrid and filled with Greek clergy. In the same year "
        "the Curator Anatolus dies in a Wizard's War, and Tablinum has no Curator "
        "for two years.",
        "",
    ),
    (
        1020,
        "",
        "Silus Curator",
        "Silus becomes Curator of Tablinum.",
        "",
    ),
    (
        1027,
        "",
        "Silus Marched; Justius Curator",
        "Silus is accused of infernalism and Marched. His successor Justius is said "
        "to have taken apart a number of infernal exhibits and driven demons out of "
        "many of Tablinum's regio levels during his long tenure.",
        "",
    ),
    (
        1080,
        "",
        "Scribonius Curator",
        "Scribonius becomes Curator of Tablinum and writes the first catalogue of "
        "its exhibits to claim completeness.",
        "",
    ),
    (
        1091,
        "",
        "Croatia offered to Hungary",
        "The Trpimirović line of Croatian kings ends in a feeble quarrel between "
        "brothers, and the nobles of the north invite Ladislaus I of Hungary to "
        "rule. Croatia has been a vassal principality of Hungary ever since.",
        "",
    ),
    (
        1092,
        "",
        "Villages bound to their churches",
        "A Church council in Hungary rules that a village with a church may not move "
        "far from it, beginning the end of the Magyars' wandering villages.",
        "",
    ),
    (
        1095,
        "",
        "Jeremiah enters the ghostly castle",
        "The Order had long known of a phantom castle in the Carpathians; this year "
        "Jeremiah of Tremere solves the secret of its regio and becomes the first "
        "magus to enter the tower. One inhabitant waits there, and he has not aged "
        "since.",
        "",
    ),
    (
        1100,
        "",
        "Coloman's law: witches do not exist",
        "King Coloman the Learned of Hungary decrees that, as witches do not exist, "
        "no one may be tried for witchcraft. The Quaesitors look into it as "
        "discreetly as they can but find no magus behind it, and the law still "
        "stands. (The book says only the eleventh century; Coloman reigned from "
        "1095 to 1116.)",
        "",
    ),
    (
        1102,
        "",
        "Scribonius leaves; Calpurnius Curator",
        "Scribonius resigns as Curator, quits House Tremere and joins House Jerbiton "
        "in the Theban Tribunal. His successor Calpurnius greatly enlarges "
        "Tablinum's Faerie collection.",
        "",
    ),
    (
        1120,
        "",
        "Murat and Radomir purge the vampires; Laniena founded",
        "The vampire of a dead magus hunts out dhampirs, has them trained and then "
        "kills them to make more vampires, the latest of the infiltrations that "
        "have dogged House Tremere. The famed hunter Murat of Terezin comes to "
        "Coeris and with the young Radomir of Tremere clears every vampire from the "
        "House; Murat kills the nest's master himself. The two ask the Tribunal "
        "for an oppidum to train hunters, and once Murat joins House Ex "
        "Miscellanea the Praeco agrees. Working from old initiation scripts a "
        "Gnostic scholar took down while spying on a taltós clan, they learn after "
        "years of trials to Open the Gifted to the Hunters' Arts; Radomir calls "
        "them interfectores, soon shortened to Fectores. Laniena begins as part of "
        "the Scholomance and later moves to the Aggtelek caves. House Tremere now "
        "forbids its magi to take a dhampir as apprentice. (The book says about a "
        "hundred years ago.)",
        "Murat of Terezin was himself a dhampir, and became a vampire when he died. "
        "He survives as a kukudhi, a vampire passing as a man, living far from "
        "Laniena with his fourth mortal wife and fathering dhampirs. Only Murat the "
        "Younger knows, and lets him be for the hunters his children give Laniena.",
    ),
    (
        1125,
        "",
        "Coeris takes the Scholomance",
        "Thirty years after Jeremiah's entry Coeris claims the ghostly tower and "
        "makes it a mansio for the Redcaps of the Tribunal's north. Within a few "
        "years it is training Redcaps, and soon after mundanes of use to House "
        "Tremere.",
        "",
    ),
    (
        1137,
        "",
        "Akilina seen again; Scribonius dies",
        "Magi studying at Tablinum report meeting Akilina, or someone who claims to "
        "be her, in the maze of its regiones, two centuries after she vanished. "
        "Scribonius, the former Curator, dies this year.",
        "",
    ),
    (
        1164,
        "",
        "Stefan Nemanja serves the emperor",
        "Stefan Nemanja, a Serbian prince of modest beginnings and then a "
        "Byzantine vassal, helps the emperor in his war on Hungary.",
        "",
    ),
    (
        1165,
        "",
        "The Roman dragon's last sighting",
        "Fetillusclaviceps, keeper of the Pax Draconis, is seen for the last time. "
        "He had shown himself only half a dozen times in three centuries, never to "
        "a magus, and his lair has never been found. (The book says only more than "
        "fifty years before 1220.)",
        "Some Tremere wonder whether the later sightings were the dragon at all, or "
        "magi of their own House repeating the Founder's disguise.",
    ),
    (
        1167,
        "",
        "Pantino",
        "Stefan Nemanja turns on his Byzantine overlord and beats an imperial army "
        "at the Battle of Pantino.",
        "",
    ),
    (
        1170,
        "",
        "Nestor Curator",
        "Nestor succeeds Calpurnius as Curator of Tablinum, an office held for life, "
        "and becomes known for his research into regiones.",
        "",
    ),
    (
        1171,
        "",
        "Nemanja taken to Constantinople",
        "Nemanja allies with Venice, Hungary and German princes to throw off "
        "Byzantine rule, but Serbian feuds, a Venetian mutiny and plague wreck the "
        "campaign. Manuel Komnenos invades Raška, besieges Ras and carries "
        "Nemanja to Constantinople in chains; against all expectation the two "
        "become friends, and Nemanja returns as the emperor's strategos and the "
        "sole lawful ruler of the Serbs.",
        "",
    ),
    (
        1185,
        "",
        "The Asen brothers free Bulgaria",
        "Three brothers, Teodor Petar, Ivan Asen and Kaloyan, lead the Bulgarians "
        "out of Byzantine rule and found the Second Bulgarian Empire. Their origins "
        "are a mystery, perhaps Bulgarian, perhaps Vlach or Cuman, and their "
        "inherited gift for swaying crowds troubles the Order. Cuman tribes shelter "
        "the rebel princes after their first army is beaten and supply the core of "
        "the next.",
        "",
    ),
    (
        1190,
        "",
        "The Teutonic Order founded at Acre",
        "Barbarossa died in 1189 and most of his German nobles went home, but a "
        "faithful few stay for the siege of Acre. Ill and neglected by the French "
        "and English Hospitallers, crusaders from Bremen and Lübeck found a "
        "hospital order for Germans, backed by Duke Friedrich of Swabia, and Pope "
        "Celestine III approves it. (The book says some twenty years before 1220.)",
        "",
    ),
    (
        1195,
        "",
        "Nemanja abdicates",
        "Stefan Nemanja retires and hands Serbia to his second son, Stefan, passing "
        "over the eldest, Vukan.",
        "",
    ),
    (
        1197,
        "",
        "Kaloyan tsar",
        "Kaloyan begins his reign and restores the Bulgarian Empire; his Cuman "
        "bride seals an alliance with the nomads that must be renewed by rite each "
        "summer. New German crusaders reach the Holy Land and find the Teutonic "
        "hospital flourishing.",
        "",
    ),
    (
        1198,
        "",
        "The Teutonic Knights take up the sword",
        "Seeing the crusader kingdom's border forts badly manned, the newcomers "
        "decide the Teutonic brothers, former knights, can fight as well as nurse, "
        "and the pope gives the Order a new charter as a military order.",
        "",
    ),
    (
        1199,
        "",
        "Death of Stefan Nemanja",
        "Nemanja dies, and holy oil begins to flow from his tomb, so the people call "
        "him the Myrrh-flowing.",
        "",
    ),
    (
        1200,
        "",
        "Saint Simeon; Eudocia driven out",
        "Less than a year after his death the Eastern Church canonises Stefan "
        "Nemanja. Stefan II accuses his first wife, Eudocia Angelina, daughter of "
        "Emperor Alexios Angelos and mother of five of his children, of adultery "
        "and drives her from Serbia. About this time Hungary stops exporting "
        "slaves, probably as part of the king's plan to people the kingdom's "
        "edges.",
        "",
    ),
    (
        1202,
        "",
        "Zadar sacked",
        "Crusaders raid and destroy Zadar, Croatia's richest port and a possession "
        "of the King of Hungary, and little is done to dislodge the Venetians.",
        "",
    ),
    (
        1203,
        "",
        "Tarnovo's primate; the Zadar zenodochium",
        "Pope Innocent III names the Archbishop of Tarnovo primate of all Bulgaria "
        "and Wallachia, tying the Asens' church to Rome, though Ohrid stays "
        "Orthodox. Soon after the violence at Zadar, House Tremere builds a "
        "zenodochium in a regio within a magical lacuna in the city and staffs it "
        "with a skilled surgeon and his assistants. Some months later the House "
        "loses touch with them, and the regio itself seems to vanish.",
        "",
    ),
    (
        1204,
        "",
        "Constantinople falls; Adulio joins Kezdö Válasz",
        "Constantinople falls to the Latins, and the Latin Church soon controls "
        "much of the city; the magi of Thebes learn what crusading armies can do. "
        "Two months later Adulio of House Tremere, just out of his apprenticeship, "
        "joins Kezdö Válasz to keep the same fate from Transylvania. In Serbia "
        "Vukan's resentment breaks into civil war against his brother Stefan II, "
        "who wins but cannot take any of the lost Byzantine lands. A loyal "
        "Croatian noble wrests Zadar back from the crusaders.",
        "",
    ),
    (
        1205,
        "",
        "Baldwin captured; Venice takes the coast",
        "Tsar Kaloyan captures Emperor Baldwin of the Latin Empire, who is held in "
        "the tower above Tarnovo's Frankish quarter that still bears his name. "
        "Venice takes Dubrovnik, which pays it tribute and harbours its galleys, "
        "and regains Zadar, this time by a treaty that makes the Venetians "
        "overseers rather than occupiers; the townsfolk see through it.",
        "",
    ),
    (
        1206,
        "",
        "Saint Simeon comes to Studenica",
        "Nemanja's relics are carried from Mount Athos to the monastery of Studenica.",
        "",
    ),
    (
        1207,
        "",
        "Death of Kaloyan; the singers' war at the Wartburg",
        "Kaloyan's reign ends. In Germany the Landgrave of Thuringia (the book "
        "calls him margrave) holds a contest for the crown of poetry, on the terms "
        "that every losing singer must die; Henry of Ofterdingen loses to Wolfram "
        "von Eschenbach and is let go to fetch the one bard he says is better, "
        "Klingsohr.",
        "",
    ),
    (
        1208,
        "",
        "Sava returns to Studenica",
        "Sava, Nemanja's youngest son, who had left family politics for the monks "
        "of Mount Athos, comes back to Studenica and begins to organise the Serbian "
        "Orthodox Church.",
        "",
    ),
    (
        1210,
        "",
        "Hermann von Salza hochmeister; Simium writes to Polyaigos",
        "Hermann von Salza is elected hochmeister of the Teutonic Order. About this "
        "time Simium, headmaster of the Scholomance, begins writing to Polyaigos "
        "in the Theban Tribunal, a covenant that also prepares pupils before "
        "apprenticeship; an exchange is talked of, but old enmity between Thebes "
        "and Transylvania stands in its way. (The book says within the last ten "
        "years or so.)",
        "",
    ),
    (
        1211,
        "",
        "The Burzenland granted to the Teutonic Knights",
        "Straight after a marriage contract between King Andrew II and Landgrave "
        "Hermann of Thuringia for their children, Hermann von Salza's Order is "
        "invited to Transylvania (the book also credits a King Bela, and makes "
        "Hermann of Thuringia head of the Salza family). Andrew gives it the "
        "Burzenland, free of taxes and dues, keeping the right to mint and half "
        "the gold and silver mined, and charges it to hold the Carpathian passes "
        "against the Cumans. Brother Theoderich commands the mission; Saxon "
        "settlers follow in numbers, and the Knights begin five castles, "
        "Marienburg, Kronstadt, Rosenau, Schwarzenburg and Kreuzburg.",
        "",
    ),
    (
        1215,
        "",
        "Macrobius slain; Essedarius leads Kezdö Válasz",
        "Macrobius, filius of Gasparus and leader of Kezdö Válasz, is torn apart "
        "by an angry griffin he met by chance in the Prokletije, the Accursed "
        "Mountains. His filius Essedarius, the fourth leader in Norsius's line, "
        "takes command. Leona, his partner, was not with him; she hunts the beast "
        "down and still hunts griffins in her grief.",
        "",
    ),
    (
        1216,
        "",
        "The Valley of the Thracian Kings found",
        "A Tremere necromancer serving as a hoplite finds the burial ground of the "
        "ancient Thracian kings close to Seuthopolis, their old capital. Tremere's "
        "necromancers rejoice and House Verditius wants a dig too, since the "
        "Thracians honoured smith gods; Benilda, wary of cheerful necromancers, "
        "bars the way.",
        "",
    ),
    (
        1217,
        "",
        "Stefan the First-Crowned; Andrew II goes on crusade",
        "A papal legate crowns Stefan II king of all the Serbian and coastal lands, "
        "and most Serbian dioceses take up the Latin rite, though Kotor and Ston "
        "keep the Greek. Andrew II of Hungary sets out on crusade.",
        "",
    ),
    (
        1218,
        "",
        "Poena becomes Prima; Ivan Asen II tsar",
        "Poena becomes Prima of House Tremere, and Monica Ierne takes the post of "
        "legata, the House's field commander. The former Primus is given charge of "
        "the Burning Acorns Vexillation, which hunts surviving Diedne, a post that "
        "lets him roam as he pleases. Ivan Asen II takes the Bulgarian throne at "
        "Tarnovo and marries a daughter of the King of Hungary. Andrew II comes "
        "home from crusade to a hostile nobility (the book dates his return to "
        "1222).",
        "",
    ),
    (
        1219,
        "",
        "Sava archbishop of an autocephalous Serbian Church",
        "At Sava's request the patriarch of the Greek Church makes the Serbian "
        "Church self-governing and consecrates Sava its archbishop. Sava's "
        "Nomocanon becomes the book of church law for all the Slav churches.",
        "",
    ),
)

#: The history the book tells without a year, era by era, for the
#: Tribunal's History.
ERAS: tuple[tuple[str, str], ...] = (
    (
        "Dacians, Romans and dragons",
        "The Getae, the first tribe of the region named in history, were "
        "conquered by Darius of Persia. Their god Zalmoxis, said by his cult to "
        "have studied magic with Pythagoras on Samos, was once worshipped openly "
        "and now only in the hidden places of the Carpathians. Rome made the land "
        "Dacia; Trajan bridged the Danube and Decebalus's treasure is still lost. "
        "In the second century Fetillusclaviceps, the Roman dragon, forged the Pax "
        "Draconis: dragons would not war together, would keep their violence at "
        "home, would defer to the stronger and leave men be, and a wife taken "
        "without a greater dragon's leave made the taker an outlaw. Goths, Huns, "
        "Gepids and Avars drove the Vlachs into the hills; the Goths beat Valens "
        "near Adrianople in 376, and the Huns sacked Nikopolis in 447.",
    ),
    (
        "Slavs, Bulgars and Magyars",
        "The Slavs crossed the Carpathians in the sixth and seventh centuries, led, "
        "their tales say, by a taltós hermit of matchless power, and the Seven "
        "Tribes ruled the Balkans for about a century. Khan Asparukh's Bulgars "
        "crossed the Danube between 679 and 681 to found the First Bulgarian "
        "Empire. More than a thousand years ago the taltós, wise men of the Huns, "
        "turned their vampire-slaying magic on one another and all but wiped "
        "themselves out within a few years. The Szeklers claim descent from "
        "Attila's rearguard and allied with the Magyars when they came; Saint "
        "Stephen made Hungary Christian, gave it to the Virgin and first taught the "
        "doctrine of the living Holy Crown. In the eleventh century Pechenegs, "
        "Magyars and Uzes overran Bulgaria in turn, and the Cumans took the lands "
        "east of the Carpathians.",
    ),
    (
        "The Founder and the legal covenants",
        "Dacian magicians held the site of Coeris in Maramures, beyond the reach of "
        "Rome and the Church, until Tremere killed their faerie god, burned its "
        "heart and swallowed its ashes in wine; its priests became his followers, and "
        "Coeris was first built as a refuge for wounded Tremere. He chose Lycaneon "
        "for its metals and mined its gold out in the covenant's first decades. "
        "Asclepius began as a settlement of Dacian sorcerers on the site of "
        "Coeris, long since absorbed by the House; Domostron was founded by "
        "Tremere's Hermetic allies, and Theban raiders destroyed its first site; "
        "Diodorus housed the followers of the faerie magician Muj, now a small "
        "sect of House Tremere; Pannonia was a fortified Tremere covenant on the "
        "border of three Tribunals, until a great monastery at the springs of its "
        "river killed its aura and its magi became the first to scatter into "
        "oppida. Centuries ago Pannonia sold nearly all its concessions to the "
        "chief Mercere of the Tribunal.",
    ),
    (
        "Refugees, war and watchfulness",
        "Covenants worn down by quarrels in neighbouring Tribunals have sought "
        "refuge here as foederati of Pannonia: the Covenant of the Four "
        "Divinities, Verditius magi of the Cabeiri cult, came from the Theban "
        "Tribunal and became Seuthopolis, long since the seat of the Quaesitors "
        "and hoplites; Histria came from the Roman Tribunal, with its chapter "
        "house at Shrouded Bay on Cres, first built to guard Cres against "
        "Transylvanian Tremere. After the Schism War Lycaneon was enlarged and "
        "fully manned for decades, Hermanus raised many of Coeris's defences until "
        "his obsession had him cast out, and the House compiled the Diedne sigils "
        "now kept at Seuthopolis. Some storm wizards joined House Ex Miscellanea "
        "in that war and fought beside the Tremere. Lycaneon was fully mobilised "
        "almost a year before the Corruption of Tytalus was disclosed at Tribunal, "
        "and Tasgilla, the corrupted Prima of Tytalus, had spread infernal taint "
        "through spells and texts. A few decades ago one Primus had the Redcaps "
        "seek Gifted Arab and African children for his House to raise.",
    ),
)

#: What lies ahead after 1220, for a saga that follows history.
FUTURE = (
    "If the saga follows history, Andrew II's nobles force the Golden Bull on "
    "him in 1222; the Mongols break the Cumans at the Kalka in 1223; Hermann "
    "von Salza has the Burzenland made a fief of the Holy See in 1225 and the "
    "Knights are driven out; Ivan Asen II spreads his rule over Thrace, "
    "Macedonia and Epiros within the decade; a crusade against Bosnia comes in "
    "1237; and the Mongols invade in 1241."
)


def build(transylvania: Transylvania) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, in order of
    year and season, and add the undated history, by era, to the
    Tribunal's History, with what lies ahead under Secrets. Nothing is
    written when the Tribunal has not been made yet (the parts build in
    order, this one after the Tribunal's)."""
    tribunal = transylvania.tribunal
    if tribunal is None:
        return
    for year, season, title, details, hidden in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        transylvania.b.event(
            tribunal, year, title, secrets(details, hidden), season=season
        )
    eras = paragraphs(*(f"{title}. {text}" for title, text in ERAS))
    # Any history already written keeps its place, its secrets after ours.
    head, _, hidden = tribunal.history.partition("\n\n" + SECRETS + "\n")
    tribunal.history = secrets(paragraphs(head, eras), paragraphs(hidden, FUTURE))
