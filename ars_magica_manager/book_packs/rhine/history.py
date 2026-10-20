"""The Rhine Tribunal's history, as the book tells it: every Hermetic
event up to spring 1220 as a Tribunal Diary entry, the Mundane history
of Germany as a tuple of eras for the Tribunal's summary, and a short
mundane history of each of the six regions for their places.

Dates are AD; "AA" is Anno Aegis, the Order's own count, given where
the book gives it (the Rhine's gatherings fall on the years the book
numbers in AA). Only what happened by 1220 is recorded; what the book
foretells is left to the summaries of the places and factions it
concerns."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import secrets

if TYPE_CHECKING:
    from . import Rhine

#: (year, title, details, hidden): one Diary entry each, in order of year.
EVENTS: tuple[tuple[int, str, str, str], ...] = (
    (
        64,
        "Mercurian temple at Durenmar's site",
        "Priests of the Roman Cult of Mercury raise a temple deep in the Black Forest, "
        "on the ground Durenmar later takes, hoping to turn the primeval power of the "
        "Hercynian Forest to their own use. In the Roman years they bind the forest's "
        "spirit by its own oaths into what is now the Fane of the Founders; a wild "
        "splinter of it escapes south and in time becomes the King of the Black Mountain.",
        "",
    ),
    (
        74,
        "Black Forest Road finished",
        "The Eighth Legion under Cornelius Clemens completes the road from Offenburg to "
        "Rottweil with the help of Mercurian priests, who set warding milestones along it. "
        "The Roman limes of the same age cuts the Black Forest, and its spirit, off from "
        "the rest of the Hercynian Forest.",
        "",
    ),
    (
        725,
        "Donar Oak felled",
        "St Boniface cuts down the Donar Oak at Geismar in Thuringia and builds an oratory "
        "of St Peter from its wood. Pagan magic, relics and belief wane from that day, and "
        "the one great spirit of the Hercynian Forest is shattered into the many lesser "
        "forests of Germany.",
        "",
    ),
    (
        731,
        "Trianoma apprenticed to Bonisagus",
        "Trianoma finds Bonisagus in his cave in the Alps, becomes his apprentice and "
        "learns the Parma Magica.",
        "",
    ),
    (
        731,
        "The Founders gathered",
        "From 731 to 767 Trianoma seeks out the wizards who will be the Founders and brings "
        "them to Bonisagus, who refines his theory with each. Merinita comes in from the "
        "wild and persuades the shapeshifter Bjornaer to join, for which Bjornaer's old "
        "fellows, the sorceress Gyongy among them, condemn her.",
        "",
    ),
    (
        754,
        "Bonisagus settles at Durenmar",
        "Bonisagus leaves his Alpine cave for the ruined Roman temple in the Black Forest, "
        "hoping to reconcile his Hermetic theory with the forest's primeval magic; "
        "between 754 and 767 the place is built up with room for many magi.",
        "",
    ),
    (
        767,
        "Order of Hermes founded at Durenmar",
        "The Founders compose and swear the Oath at the Fane of the Founders and hold the "
        "first Tribunal gathering. Bonisagus's followers and some of the Founders settle "
        "at Durenmar and build the covenant.",
        "",
    ),
    (
        767,
        "Covenants on Durenmar's model",
        "Between 767 and 773 Flambeau and his apprentices leave to found Val-Negra in the "
        "Pyrenees, and other magi found covenants of their own after Durenmar's pattern.",
        "",
    ),
    (
        771,
        "Bjornaer's first council on Rügen",
        "Bjornaer and her followers meet in council on Rügen; her House has gathered there "
        "every twelve years since.",
        "",
    ),
    (
        773,
        "Second Grand Tribunal",
        "A Tribunal is ruled to need at least twelve magi from four covenants. Crintera, "
        "the domus magna of House Bjornaer, and Fenistal, the domus magna of House "
        "Merinita, are founded.",
        "",
    ),
    (
        780,
        "First Rhine Tribunal (919 AA)",
        "The Rhine Tribunal meets for the first time, at Durenmar. Arae Flaviae in Swabia "
        "and Rethra in the Eastern Marches are founded.",
        "",
    ),
    (
        789,
        "Jerbiton before Charlemagne",
        "Jerbiton, who has taken on the apprentices of the imperial mage-smith Carolinus, "
        "meets Charlemagne. The emperor outlaws sorcery and paganism but allows the kind of "
        "benevolent magic Jerbiton practises.",
        "",
    ),
    (
        792,
        "Merinita leaves the Order",
        "The Founder Merinita is seen for the last time, going to seek the spirit of the "
        "wilderness; the Bohemian chapter dates her going to 785 and says her last words "
        "are carved over Irencillia's gate. Fenistal becomes the first covenant to enter "
        "Winter, and the new Primus Quendalon founds Irencillia.",
        "",
    ),
    (
        799,
        "Third Grand Tribunal",
        "After the gathering Quendalon goes into the faerie woods of Bohemia, leaving "
        "Myanar to lead House Merinita.",
        "",
    ),
    (
        801,
        "Quendalon returns; Irencillia the domus magna",
        "In 801 and 802 Quendalon comes back from the faerie woods and Myanar denies he is "
        "the true Quendalon. The struggle kills Myanar and loses Fenistal; Irencillia "
        "becomes the domus magna of House Merinita, the House turns to faerie magic, and "
        "the Elder Gild splits away from the Hawthorn Gild.",
        "",
    ),
    (
        807,
        "Tytalus lost in the Maddenhofen Woods",
        "The Founder Tytalus enters the Maddenhofen Woods in Bohemia, saying he will face "
        "the Queen of all the Fae, and is never seen again.",
        "",
    ),
    (817, "Fourth Grand Tribunal", "", ""),
    (
        831,
        "Bjornaer's last words",
        "At the Gathering of Twelve Years at Crintera, Bjornaer speaks for the last time "
        "to her House and goes into the forest as a bear.",
        "",
    ),
    (
        832,
        "Fifth Grand Tribunal",
        "Grand Tribunals are to meet every thirty-three years from now on, and the regional "
        "Tribunals every seven years from 836.",
        "",
    ),
    (
        850,
        "Hercynius's lineage",
        "From about 850 to 948 Hercynius of Bonisagus founds a lineage within his House and "
        "draws other magi to his teaching on the forest's magic.",
        "",
    ),
    (
        857,
        "Tribunal of 996 AA: the Twilight spirits",
        "The spirits of three magi lost to Twilight famously return to the gathering.",
        "",
    ),
    (
        865,
        "Sixth Grand Tribunal",
        "The borders of the Tribunals are fixed along the lines of the Frankish partition and "
        "named: Rhine, Normandy, Provencal, Britannian, Roman, Theban, Eastern and Greater "
        "Alps.",
        "",
    ),
    (
        878,
        "Tribunal of 1017 AA: proxy sigils",
        "Firm rules on the votes of retired magi end twenty years of dispute over whether and "
        "how their sigils may be cast.",
        "",
    ),
    (
        885,
        "Tribunal of 1024 AA: founding rules",
        "Arae Flaviae and Schwarzburg are abolished, and strict rules for the founding of "
        "new covenants are agreed.",
        "",
    ),
    (
        892,
        "Rudiaria founded (1031 AA)",
        "The Tribunal sponsors Rudiaria, a Flambeau-leaning covenant on the right bank of "
        "the Rhine opposite Bingen, and grants it every magical site along the river between "
        "Mainz and Cologne.",
        "",
    ),
    (898, "Seventh Grand Tribunal", "", ""),
    (
        930,
        "Sirmium destroyed by the Magyars",
        "Magyar raiders destroy the covenant of Sirmium in Meissen, and with it the "
        "region's known vis sources. Wiederich of Flambeau, the only survivor, joins Henry "
        "the Fowler's army for revenge and serves at Riade in 933 and on the Lech in 955; "
        "after the Magyars' defeat House Bjornaer adopts three Magyar shapechangers, whose "
        "horse-hearted line survives, and Wiederich's descendants have hounded them as "
        "blood enemies ever since.",
        "",
    ),
    (931, "Eighth Grand Tribunal", "", ""),
    (
        934,
        "Oakdell founded (1073 AA)",
        "Diedne magi found Oakdell in the Westerwald, a dozen miles east of the Rhine, with "
        "the Tribunal's sponsorship and on condition that it keeps out of Rudiaria's "
        "territory (the book's list of covenants puts its founding in 931).",
        "",
    ),
    (
        941,
        "Tribunal of 1080 AA: the Rowan Gild",
        "The Tribunal's followers of Diedne, until now of the Hawthorn Gild, found the "
        "Rowan Gild.",
        "",
    ),
    (
        962,
        "Diabolism charge against Eginolf (1101 AA)",
        "Charges of diabolism against Eginolf of Flambeau of Rudiaria are not proven, but "
        "the reports of malefic doings near the covenant are noted with disapproval; "
        "Rudiaria is ordered to investigate, report within seven years and stop troubling "
        "the mundanes.",
        "",
    ),
    (964, "Ninth Grand Tribunal", "", ""),
    (
        969,
        "Rudiaria destroyed (1108 AA)",
        "House Mercere reports Rudiaria burnt out in what looks like a catastrophic magical "
        "accident, every magus slain or missing; diabolism is suspected. The fall comes "
        "with a crippling famine and unrest in the region.",
        "",
    ),
    (
        976,
        "Rudiaria's site sanctified (1115 AA)",
        "Nothing can be salvaged at Rudiaria; an archbishop of Mainz has sanctified the "
        "ground. Oakdell's claim to Rudiaria's sites is refused.",
        "",
    ),
    (
        990,
        "Waldherz founded",
        "Followers of Hercynius leave Durenmar to found Waldherz, first as a chapter house "
        "and later as a disputed covenant in its own right.",
        "",
    ),
    (
        993,
        "Grand Silesia founded",
        "Crintera and Rethra sponsor Grand Silesia, the Order's easternmost covenant yet; "
        "its Bjornaer and the Bonisagi of Waldherz join the Rowan Gild.",
        "",
    ),
    (
        997,
        "Tenth Grand Tribunal",
        "The Rhine's own gathering of this year is the first of three (997, 1004 and 1011) "
        "at which distrust within the Order stops the renewal of the Founders' vows at the "
        "Fane.",
        "",
    ),
    (
        997,
        "Oakdell's charges dismissed (1136 AA)",
        "Oakdell's accusations of espionage and meddling against magi of Durenmar are "
        "thrown out as spurious and unproven.",
        "",
    ),
    (
        1004,
        "Tribunal of 1143 AA: the Rowan Gild Marched",
        "The whole Rowan Gild is Marched, beginning the Schism War in the Rhine. Severus "
        "Maximus of Flambeau declares Wizard's War on Caithlinn of Oakdell and Cirion of "
        "Tremere on Pietro of Oakdell; Tremere and Flambeau magi set about destroying "
        "Oakdell and Waldherz.",
        "",
    ),
    (
        1008,
        "New Slavonic Tribunal declared",
        "The Slavic covenants, Rethra and Grand Silesia among them, break with their "
        "sponsors and declare a New Slavonic Tribunal. Grand Silesia is destroyed the same "
        "year (the book's list of covenants says 1009).",
        "",
    ),
    (
        1016,
        "Oakdell razed (1155 AA)",
        "Oakdell is razed and all its Diedne magi slain in the Schism War.",
        "",
    ),
    (
        1018,
        "Tribunal of 1157 AA: the Schism War ends",
        "The Schism War is declared over; the Linden Gild grows up over the following "
        "decades. The renewal of the Founders' vows at the Fane resumes, an Ex Miscellanea "
        "magus taking the place Diedne's representative once held.",
        "",
    ),
    (
        1030,
        "Eleventh Grand Tribunal",
        "Over the Rhine's protests, the New Slavonic Tribunal is given authority over new "
        "covenants in Slavic lands.",
        "",
    ),
    (
        1039,
        "Tribunal of 1178 AA: Fengheld founded",
        "Veteran Tremere and Flambeau magi back from the Schism War in Britannia (fought in "
        "Stonehenge and Normandy) found Fengheld in the Harz with the Tribunal's ready "
        "approval, as a quiet retreat for ageing war heroes away from the mundanes.",
        "",
    ),
    (
        1039,
        "Fengheld's Tremere in Henry III's wars",
        "Through the reign of Henry III (1039 to 1056) Fengheld's political Tremere, working "
        "with the Transylvanian Tribunal, take part in the emperor's conquests of Bohemia, "
        "Poland and Hungary and seize many vis sites.",
        "",
    ),
    (
        1048,
        "Aschlaranda returns to Durenmar",
        "Aschlaranda, once of Waldherz, reappears at Durenmar.",
        "",
    ),
    (
        1052,
        "Dankmar founded",
        "Aschlaranda, exiled from Durenmar and from House Bonisagus, settles with her "
        "apprentice Schadrit at Dankmar in the Black Forest (the timeline puts their "
        "occupation of the site in 1053).",
        "",
    ),
    (
        1052,
        "Crintera allied with Pripet Maior",
        "Bjornaer magi once of Grand Silesia settle at Pripet Maior in the New Slavonic "
        "Tribunal, and Crintera and Pripet Maior form an alliance across the Tribunal "
        "border.",
        "",
    ),
    (
        1053,
        "Tribunal of 1192 AA: Guardians of the Forest",
        "The Guardians of the Forest ruling is made, allowing magi to defend wild places. "
        "Dankmar goes unrecognised as a covenant, Durenmar's influence seeing to it.",
        "",
    ),
    (
        1063,
        "Twelfth Grand Tribunal",
        "To curb the Rhine, the Grand Tribunal rejects its claim to the Polish lands left "
        "empty by Grand Silesia's fall and grants all Slavic lands to the New Slavonic "
        "Tribunal.",
        "",
    ),
    (
        1067,
        "Tribunal of 1206 AA: Roznov and Dankmar",
        "Roznov is founded in Moravia by three Ex Miscellanea magi, and Dankmar is at last "
        "recognised as a covenant of the Rhine.",
        "",
    ),
    (
        1074,
        "Roznov admitted",
        "Roznov is admitted to the Rhine Tribunal; two Tremere from Transylvania join it "
        "almost at once.",
        "",
    ),
    (
        1081,
        "Durenmar's charge against Dankmar",
        "Durenmar accuses Dankmar before the Tribunal of being secretly in league with the "
        "forest fay. Nothing is proven.",
        "",
    ),
    (
        1085,
        "King of the Black Mountain raids Durenmar",
        "The great faerie lord of the Black Forest attacks Durenmar; several Bonisagus magi "
        "and many covenfolk are killed or carried off, and the captives are never returned. "
        "In the years after, Durenmar's magi devise the most powerful Aegis of the Hearth "
        "yet known.",
        "",
    ),
    (
        1088,
        "First Treverorum proposal fails (1227 AA)",
        "Xantippes and Julia of Jerbiton and Selena Tibicena of Bonisagus propose a covenant "
        "in Trier to recover Roman secrets; with no sponsor from Irencillia, Crintera or "
        "Dankmar it is not recognised.",
        "",
    ),
    (
        1095,
        "Treverorum approved (1234 AA)",
        "The same three, now joined by Arliandus of Tremere, propose again and Treverorum is "
        "approved.",
        "",
    ),
    (1096, "Thirteenth Grand Tribunal", "", ""),
    (
        1100,
        "Durenmar's lean half-century",
        "From about 1100 to 1150 Durenmar loses several magical sites to Zähringen settlement, "
        "runs short of vis and raids the forest's faerie sites greedily to make it up. The "
        "Black Fir begins to grow at the edge of its Aegis about this time.",
        "",
    ),
    (
        1109,
        "Valdus fined a pawn (1248 AA)",
        "Treverorum charges Valdus of Tytalus with twice harvesting vis from its site outside "
        "Trier's walls; he admits it but calls the site neglected and not theirs. The "
        "Tribunal rules that a site within a day's march of a covenant belongs to it, yet as "
        "Treverorum lost nothing Valdus pays one pawn and must ask leave in future.",
        "",
    ),
    (
        1123,
        "Rheinstein founded (1262 AA)",
        "Schwall of Bjornaer and Fulmonious of Tytalus found Rheinstein on Pfalz Island in "
        "the Rhine Gorge with the Tribunal's sponsorship, promising every other covenant a "
        "tithe of three pawns of vis a Tribunal for five Tribunals.",
        "",
    ),
    (1129, "Fourteenth Grand Tribunal", "", ""),
    (
        1144,
        "Tribunal of 1283 AA: Oculus Septentrionalis founded",
        "At the Ash Gild's urging the Tribunal resolves to learn more of the Norse wizards, "
        "the supposed Order of Odin, and orders a covenant founded for the purpose; three "
        "magi under Axior volunteer and Oculus Septentrionalis is born. The Tribunal rules "
        "that a covenant need have no site at its founding, only magi bound by a charter.",
        "Three Verditius magestones were secretly given to the new covenant.",
    ),
    (
        1151,
        "Tribunal of 1290 AA: Durenmar fined",
        "Dankmar accuses Durenmar of molesting faeries and plundering the Black Forest's "
        "faerie sites for vis. With Crintera, Irencillia and Fengheld, and the Hawthorn and "
        "Elder Gilds, behind the charge, Durenmar is fined a rook of vis to every other "
        "covenant and barred from faerie-site vis for fourteen years unless it makes peace "
        "with the fay; no such peace has ever been made.",
        "",
    ),
    (
        1151,
        "Triamore founded",
        "The newly risen Apple Gild founds Triamore at the court of Conrad III; Oculus "
        "Septentrionalis takes up the Gild as well.",
        "",
    ),
    (
        1151,
        "Redcap Ioanna murdered in Trier (1290 AA)",
        "The Redcap Ioanna is murdered in Trier; Treverorum denies all knowledge and a "
        "Quaesitorial investigation is ordered.",
        "",
    ),
    (
        1158,
        "Tribunal of 1297 AA: Oculus Septentrionalis fined",
        "The magi of Oculus Septentrionalis are found to have broken their charter: no site, "
        "no investigation, and still living in their old sancta. Each is fined three pawns "
        "of vis and ordered out of the old sancta within a year, with a permanent site to "
        "be found before the next Tribunal; two Jerbiton join them.",
        "",
    ),
    (
        1158,
        "Xantippes convicted of meddling (1297 AA)",
        "Xantippes of Jerbiton is found guilty of major mundane meddling, having worked "
        "Mentem magic of his own devising on the people of Trier for gain, to the harm of "
        "the Order's standing and perhaps a cause of Ioanna's death. He is fined ten pawns, "
        "his fortune is shared equally among the Tribunal's covenants and he owes three "
        "seasons' scribing to the Great Library.",
        "",
    ),
    (
        1158,
        "Agnes claims to have seen Merinita",
        "Agnes of Irencillia tells the Tribunal she has seen the Founder Merinita in "
        "Bohemia; few believe her.",
        "",
    ),
    (
        1158,
        "Hildegard of Bingen a Larta of Jerbiton",
        "Hildegard of Bingen is said to have been taken into House Jerbiton about this year "
        "as an unGifted maga under its protection and tutelage; she never attends a "
        "Tribunal and meets few magi, and the tale is unconfirmed.",
        "",
    ),
    (
        1160,
        "Oculus Septentrionalis settles in Lübeck",
        "About 1160 three magi of Oculus Septentrionalis settle in Henry the Lion's new city "
        "of Lübeck; Axior leaves them.",
        "",
    ),
    (
        1162,
        "Fifteenth Grand Tribunal",
        "The Rhine again loses the Polish boundary dispute to Novgorod, as the New Slavonic "
        "Tribunal is now called.",
        "",
    ),
    (
        1165,
        "Tribunal of 1304 AA: the Lübeck charter",
        "Oculus Septentrionalis announces its new seat at Lübeck, and the Quaesitores force "
        "additions to its charter, among them that it admit only Gentle-Gifted magi.",
        "",
    ),
    (
        1165,
        "Treverorum fined fifty pawns (1304 AA)",
        "A Quaesitorial inquiry into the unrest in Trier finds Treverorum guilty of "
        "interfering with mundanes and the Church to the possible harm of its sodales; it is "
        "fined fifty pawns, payable by the next Tribunal, and ordered to repair its "
        "relations with the town.",
        "",
    ),
    (
        1165,
        "Terschelling founded",
        "Axior of Flambeau founds Terschelling on the Frisian island of that name. He dies "
        "in a magical accident within twenty years.",
        "",
    ),
    (
        1165,
        "Urgen Primus of Bjornaer",
        "Urgen takes the Primacy of House Bjornaer, which he holds through the Danish "
        "conquest of Rügen until 1203.",
        "",
    ),
    (
        1167,
        "Gathering of Twelve Years",
        "Jon Arnsson takes the Seat of the Stag on Crintera's council, a year before the "
        "Danes land on Rügen.",
        "",
    ),
    (
        1168,
        "Crintera enters Winter",
        "Valdemar I of Denmark conquers Rügen and Bishop Absolon breaks the temple of "
        "Arkona the next year. Over the Wilderists' objections Crintera chooses to wait the "
        "Danes out; the covenant falls into crisis and the Winter it has lived in for fifty "
        "years begins.",
        "",
    ),
    (
        1172,
        "Tribunal of 1311 AA: Treverorum abolished",
        "Scholastus of Jerbiton declares himself Treverorum's last survivor and the covenant "
        "is abolished; he calls Trier unsafe for magi because of its churchmen, gives no "
        "details and leaves for the Greater Alps. The fine is partly unpaid, so he is held "
        "liable and a Redcap request follows him. No one from Crintera attends.",
        "",
    ),
    (
        1179,
        "Tribunal of 1318 AA: Wizard's War on Prudentum",
        "Primus Urgen of Bjornaer charges Oculus Septentrionalis with aiding the Danish "
        "invasion of Rügen but offers no proof. Failing, he declares Wizard's War on its "
        "leader Prudentum of Jerbiton and kills him.",
        "",
    ),
    (
        1179,
        "Luctatio's crimes laid before the Tribunal",
        "Eule of Fengheld lays before the gathering her evidence that magi of Luctatio in "
        "the Roman Tribunal helped Milan beat Barbarossa at Legnano and that a necromancer "
        "of Vardian's Tomb made the plague that stopped his army before Rome.",
        "",
    ),
    (
        1186,
        "Tribunal of 1325 AA: Rügen and the Guardians ruling",
        "The Hawthorn Gild invokes the Guardians of the Forest ruling to strike back at the "
        "Danes on Rügen, with the Ash and, unexpectedly, the Elder Gilds in support. The "
        "Tribunal splits along factional lines and reaches no decision beyond a promised "
        "inquiry, so Crintera is refused leave to expel the Danes; several Bjornaer are "
        "prosecuted afterwards for attacking Danish settlers.",
        "",
    ),
    (
        1191,
        "Avarret Primus of Bonisagus",
        "Avarret becomes Primus of House Bonisagus and turns the House back to the "
        "conservative refinement of existing theory.",
        "",
    ),
    (
        1194,
        "Tribunal of 1333 AA: no wilderness invaded",
        "Held a year late because of the Grand Tribunal. Falke of Fengheld pleads "
        "passionately for Crintera to be allowed to resist the Danes, but Quaesitor "
        "Caecilius rules that no wilderness has been invaded or destroyed, Crintera's forest "
        "standing intact; the Guardians ruling is much narrowed and Crintera falls into "
        "factional infighting.",
        "",
    ),
    (
        1195,
        "Sixteenth Grand Tribunal",
        "Five magi of the Roman Tribunal are Marched over the Luctatio affair.",
        "",
    ),
    (
        1200,
        "Tribunal of 1339 AA: Rheinstein falls",
        "Horst of Mercere reports Rheinstein attacked and destroyed by an army of angry "
        "mundanes led by the archbishop of Trier, its magi's fate unknown; their own "
        "conduct drew the attention that undid them. The Tribunal bans all magical activity "
        "in the Rhine Gorge for twenty years.",
        "",
    ),
    (
        1200,
        "Terschelling turns to piracy",
        "Eric Ribecus and Hygwald Veritas join Terschelling and about this year kill a "
        "pirate chief and seize his three ships and their crews; the covenant takes to "
        "piracy, and Imanitos Mendax spends some years there as a guest soon after.",
        "",
    ),
    (
        1203,
        "Gathering of Twelve Years: Falke Prima",
        "Urgen resigns the Primacy of House Bjornaer but keeps the Seat of the Bear; Falke "
        "of Fengheld is elected Prima and takes the Seat of the Wolf.",
        "",
    ),
    (
        1207,
        "Tribunal of 1346 AA: Waddenzee",
        "Eric Ribecus and Hygwald Veritas announce they are the only magi left at "
        "Terschelling, rename it Waddenzee and change its charter and symbol. A Quaesitorial "
        "inquiry finds no wrongdoing, and a motion to treat it as a new covenant needing "
        "the Tribunal's leave narrowly fails, the Oak and Ash Gilds voting it down.",
        "",
    ),
    (
        1207,
        "Rethra abolished (1346 AA)",
        "The Tribunal declares the Slavic covenant of Rethra abolished, nothing having been "
        "heard from its magi for decades; the Knights of the Sword had lately desecrated and "
        "plundered its site (the book's list of covenants says 1202).",
        "",
    ),
    (
        1208,
        "St Georgen destroyed",
        "The monastery of St Georgen in the Black Forest is destroyed and its monks found "
        "dead among dark vines; Dankmar is suspected.",
        "",
    ),
    (
        1210,
        "God of Truth preached in Bohemia",
        "Over the last decade the religion of the God of Truth, preached by the prophet "
        "Iacob, spreads near the Bohemian Forest.",
        "",
    ),
    (
        1213,
        "Murion named Prima of Bonisagus",
        "Before his Final Twilight Primus Avarret names Murion his successor, passing over "
        "the better-qualified but 'too dangerous' Occultes and keeping the conservative line "
        "in charge of the House.",
        "",
    ),
    (
        1214,
        "Tribunal of 1214: St Georgen",
        "The latest Rhine gathering raises the destruction of St Georgen; Jiphella, "
        "Dankmar's only delegate, denies any part in it, and a close vote declines to "
        "investigate.",
        "",
    ),
    (
        1215,
        "Heorot founded on Zealand",
        "Three Rhine magi found Heorot on the Danish island of Zealand, on the site of "
        "Hrothgar's hall, in what is formally Novgorod's territory; Theoderich of Jerbiton "
        "leaves Oculus Septentrionalis to join them. It means to ask the Tribunal of 1221 "
        "for membership.",
        "",
    ),
    (
        1220,
        "The Gorge ban lapses",
        "The twenty-year ban on magic in the Rhine Gorge runs out. Durenmar's leadership, "
        "with no covenant founded for decades and Fengheld's chapters multiplying, sponsors "
        "newly Gauntleted magi to survey the Gorge's lost sites and found a new Middle Rhine "
        "covenant.",
        "",
    ),
    (
        1220,
        "Fengheld's Lusatia chapter and the border",
        "Fengheld, having been refused leave to sponsor daughter covenants of young Tremere, "
        "has lately founded a chapter house in Lusatia, ten miles from the agreed Novgorod "
        "border, provoking the latest boundary dispute between the two Tribunals; it has "
        "also loosened its Transylvanian ties, and Rudolph of Bonisagus proposes a Fengheld "
        "chapter at Durenmar itself.",
        "",
    ),
    (
        1220,
        "Fengheld's new masters and journeymen",
        "Imanitos Mendax attains Master rank at Fengheld, Beechleaf joins its main site, "
        "Felicia, Dorana's apprentice, passes her Gauntlet and Garrinchus is newly "
        "Gauntleted at the Rheingasse chapter.",
        "",
    ),
    (
        1220,
        "The Nebelkönigin stolen",
        "Waddenzee's pirates have lately taken the ship Nebelkönigin, with vis and books "
        "aboard, from Oculus Septentrionalis; as the Quaesitores had forbidden the trading "
        "venture she carried, the covenant cannot lawfully pursue her.",
        "",
    ),
    (
        1220,
        "Caprea blinds a peace envoy's familiar",
        "At Crintera the guest maga Caprea blinds the familiar of Carolus of Oculus "
        "Septentrionalis, sent as a peace envoy, and the two covenants' feud worsens.",
        "",
    ),
)

#: The Mundane history of Germany, era by era, for the Tribunal's summary.
ERAS: tuple[tuple[str, str], ...] = (
    (
        "Roman Germania",
        "Rome's frontier ran along the Rhine and the Danube, and under Domitian the gap "
        "between the rivers was closed by the limes, a fortified line from near Remagen to "
        "Abusina above Regensburg. West of the Rhine the provinces of Upper and Lower "
        "Germania had cities like Cologne, Bonn, Trier and Mainz, with forum, baths and "
        "temples, where the priests of Mercury were everywhere. Beyond the river lay "
        "Germania Magna, forest, moor and fen, whose tribes of hunters, herders and small "
        "farmers worshipped Woden, Thunor, Tius and Fria. Rome never held it: in 9 AD "
        "Hermann of the Cherusci destroyed three legions under Varus in the Teutoburger "
        "Forest. Tacitus, about 98 AD, found the Germans brave, honest and hospitable but "
        "greedy, rough and fond of drink. By the third century the limes was abandoned "
        "under pressure from Franks, Alemanni and Goths, though Trier flourished as a "
        "western imperial capital under Constantine early in the fourth.",
    ),
    (
        "The Great Migration and the Merovingians",
        "The wandering of the peoples was a slow drift rather than a flood: Goths into Gaul "
        "and Iberia, Vandals into Italy, Burgundians to the land that bears their name and "
        "to Worms in 413, Alemanni over the Rhine, Saxons, Angles and Jutes to Britain. "
        "The one violent eruption was Attila's Huns, checked at Chalons in 451 by Merovech "
        "and the Roman general Aetius. By about 600 the movements had ended, Slavs filling "
        "the empty lands of the Vistula and Oder and Saxons, Swabians, Frisians and "
        "Bavarians settled between the old Roman lines and the Slavs. The Franks rose under "
        "the Merovingians, named for the half-magical chieftain Merovech, whose grandson "
        "Clovis was baptised, united the Franks and ruled from Paris. The dynasty, credited "
        "with miraculous gifts, decayed after Clovis's grandsons Sigebert and Chilperic "
        "split the kingdom, and by 687 the mayors of the palace ruled in all but name. In "
        "751 Pepin the Short sent the last Merovingian to a monastery and took the crown "
        "with the Church's blessing.",
    ),
    (
        "The Franks and Charlemagne",
        "Charlemagne, king of the Franks from 768, carried Frankish rule, bishops and "
        "learning eastward from Aachen in three decisive campaigns that reached the Elbe and "
        "the Danube, gave the pagan Saxons the choice of baptism or death and planted "
        "bishoprics from Hamburg and Bremen to Paderborn, Hildesheim and Halberstadt. He "
        "fostered schools, made the count palatine his chief justice and in 789 outlawed "
        "sorcery and paganism while tolerating benevolent magic. On Christmas Day 800 the "
        "Pope crowned him emperor in Rome, and at his death in 814 the Frankish Empire held "
        "everything south and west of the Elbe, Bavaria included. His son Louis the Pious "
        "fought his own sons, and Frankish custom divided the inheritance: the Treaty of "
        "Verdun in 843 gave the west to Charles the Bald, the east to Louis the German and "
        "the imperial title with a narrow middle strip to Lothar. The later Carolingians "
        "faced Norse raids and the deposition of Charles the Fat in 887, and the last of "
        "them to be emperor, Arnulf of Carinthia, died in 899 amid rumours of murder.",
    ),
    (
        "The Ottonians",
        "The heirs of Louis the German were nominal kings over Saxons, Swabians, Bavarians, "
        "Burgundians and Franconians while Moslems raided Italy, Northmen the coasts and "
        "Magyar horsemen plundered as far as France. The Magyar threat rallied the tribes "
        "behind Henry the Fowler, duke of Saxony, crowned in 919, who crushed the Magyars at "
        "Riade on the Unstrut in 933; his son Otto, crowned at Aachen in 936, ended the "
        "menace for good at the Lechfeld in 955. Otto's imperial coronation in Rome in 962 "
        "bound the German kings, henceforth emperors, to Italian politics for good. Under "
        "the four Saxon emperors the empire became the leading power west of the Adriatic, "
        "Slavs and Danes were converted and bishoprics founded in the Eastern Marches and "
        "Denmark, while some pagan Slavs withdrew to Rügen. Each Ottonian left exactly one "
        "heir, which spared the empire the Frankish habit of partition. Bishops became the "
        "emperor's instruments of government, invested by him with spiritual and secular "
        "office alike, a practice soon to be contested.",
    ),
    (
        "The Salians and the Investiture Contest",
        "Conrad II began the Salian line in 1024, reaffirmed single inheritance of the "
        "crown, won in Italy and added the Burgundian crown in 1033; in 1037 the unfree "
        "knights called ministeriales entered the German feudal order. Henry III secured the "
        "loyalty of Bohemia, Poland and Hungary. Then in 1075 a papal bull forbade laymen to "
        "invest prelates, opening five decades of struggle over who led the Church: Gregory "
        "VII excommunicated Henry IV and forced his penance at Canossa in 1077, though Henry "
        "was crowned emperor in Rome in 1084 all the same. Papal authority advanced with the "
        "First Crusade, during which crusaders massacred the Jews of Worms, Speyer, Cologne, "
        "Trier and Mainz in 1096 while Henry tried in vain to punish them. The quarrel ended "
        "at Worms in 1122: the Church would elect its own bishops and abbots, while the "
        "emperor might attend elections and invest German prelates with their secular "
        "honours, keeping their feudal dues and much real influence. Henry V, the last "
        "Salian, died in 1125.",
    ),
    (
        "The Hohenstaufen and Frederick Barbarossa",
        "Lothar II's narrow election in 1125 and the Swabians' choice of Conrad III as "
        "anti-king in 1127 began the long feud of Welf and Hohenstaufen; Conrad became king "
        "in 1137 and his nephew Frederick Barbarossa followed in 1152. Barbarossa spent a "
        "third of his reign in Italy, where the towns resisted royal dues: the Milanese "
        "beat him at Legnano in 1176, the Helvetians held out and plague struck his army "
        "before Rome. In Germany his contest with Henry the Lion, duke of Saxony and leader "
        "of the Welfs, ended in 1180 with the duchy broken up, Henry exiled, Bavaria given to "
        "Otto of Wittelsbach and the Saxon lands to Hohenstaufen men. From about 1140 the "
        "push to the east cleared forests and planted settlers, a concern of frontier "
        "princes more than kings, who still looked to the Rhineland and Italy for the "
        "profits of lordship. Frederick carried the relics of the Three Magi from Milan to "
        "Cologne in 1164 and drowned in 1190 crossing the Seleph on crusade. His son Henry "
        "VI conquered Sicily in 1194 and died after six years; rival kings Philip of Swabia "
        "and Otto of Brunswick were elected in 1198, Philip was murdered at Bamberg in 1208, "
        "and the Welf Otto IV, crowned in Rome in 1209, was excommunicated and deposed.",
    ),
    (
        "The empire in 1220",
        "Frederick II, of a German father and a Sicilian mother, was made king of Germany in "
        "1212 and crowned at Aachen in 1214, helped Philip of France crush Otto IV at "
        "Bouvines that year, and was crowned emperor in Rome in 1220 after vowing a crusade "
        "he has made no move to begin. He prefers Sicily and a court of brilliant minds, "
        "writes poetry and a treatise on falconry, is called the wonder of the world, and "
        "has taken the wizard Michael Scot into his service, to the Church's unease. Germany "
        "is a loose elective kingdom with no capital: the king is crowned at Aachen and "
        "keeps his treasury at Nuremberg, and the princely nobility of dukes, archbishops, "
        "prince-bishops, landgraves, margraves and counts attend the Diet and choose him. "
        "Fiefs pass only in the male line and are divided among sons, so the provinces have "
        "splintered into countless small lordships, with new estates carved from eastern "
        "colonisation, forest clearance and drained marsh. Most cities belong to counts, "
        "dukes or bishops, but fourteen Free Imperial Cities answer only to the emperor. "
        "The Zähringen dukes died out in 1218, the Teutonic Knights and the Sword Brothers "
        "crusade in the Baltic, and Valdemar II of Denmark holds Holstein. More than half "
        "the land is still forest, and magic has withdrawn from the swelling cities into the "
        "woods.",
    ),
)

#: A short mundane history of each region, by its key in `rhine.places`.
REGION_HISTORY: dict[str, str] = {
    "rhine_valley": (
        "The Rhine was Rome's frontier, and its west bank is the oldest settled land in "
        "Germany: Trier, Mainz, Worms, Speyer, Strassburg and Cologne all began as Roman "
        "towns, and Trier was an imperial capital under Constantine. The Burgundians held "
        "Worms from 413 until the Huns destroyed them, the matter of the Nibelungenlied, and "
        "the Merovingian Franks ruled Austrasia from Metz before Charlemagne made Aachen his "
        "seat and Boniface made Mainz the Church's centre for all Germany. The Treaty of "
        "Verdun in 843 left the river's western lands as Lotharingia, long disputed between "
        "the kingdoms, and the Salian emperors made Speyer their favourite seat and resting "
        "place. The First and Second Crusades brought massacres of the Jews of Worms, "
        "Speyer, Mainz, Cologne and Trier, and in 1122 the Concordat of Worms ended the "
        "Investiture Contest. Today the three archbishops of Mainz, Cologne and Trier rule "
        "the valley with the prince-bishops and the Count Palatine, Cologne is the greatest "
        "city of the empire, and robber-baron castles live off the tolls of the Gorge."
    ),
    "black_forest": (
        "The Black Forest was the south-western part of the great Hercynian Forest until "
        "the Roman limes and the Black Forest Road of the first century cut it off; the "
        "Romans held its edges and never its heart. It became part of the duchy of Swabia, "
        "and from the eleventh century the Zähringen dukes cleared and settled its fringes, "
        "founding Freiburg in 1120, while Hirsau (1059) and its daughter houses such as St "
        "Georgen (1084) planted monasteries in its seclusion. The Hohenstaufen rose from "
        "their castle on the Kaiserberge nearby, and Barbarossa made Ulm a Free Imperial "
        "City in 1164. With the death of the last Zähringen duke in 1218 much of the forest's "
        "lordship passed to the Hohenstaufen; its interior remains unbroken wilderness, "
        "and the monasteries within it suffer attacks no one can explain."
    ),
    "lowlands": (
        "Hermann's destruction of Varus's legions in the Teutoburger Forest kept Rome out "
        "of the north, and the Saxons and Frisians held it as pagans until Charlemagne "
        "conquered the Saxons in the late eighth century and planted missionary bishoprics "
        "at Bremen, Münster, Paderborn, Hildesheim and the rest. Vikings founded Haithabu "
        "and burned Hamburg in 845, and the Poles burned it again in 1030; the coast stayed "
        "a frontier. In the twelfth century Henry the Lion, duke of Saxony, made Lübeck a "
        "city (1157) and built up Brunswick, until Barbarossa broke his duchy in 1180 and "
        "divided its lands. The northern towns have since grown rich on trade: Hamburg "
        "became a Free Imperial City in 1189 and Lübeck's merchants have traded at Novgorod "
        "since 1205, but Valdemar II of Denmark took Holstein in 1201 and occupied Hamburg in "
        "1216, and holds the coast with Frederick II's acknowledgement."
    ),
    "central": (
        "The heart of Germany, from the Harz to the Danube, was pagan country until "
        "Boniface felled the Donar Oak and planted the Church at Erfurt, Würzburg and "
        "Hersfeld in the eighth century, and Charlemagne founded Frankfurt, which became the "
        "capital of the eastern Franks under Louis the German in 843. Henry the Fowler and "
        "the Ottonians ruled from Saxony, Henry II made Bamberg a bishopric in 1007 and set "
        "out to build a second Rome there, and the silver of the Harz enriched Goslar. The "
        "Wartburg, founded in 1067, became under Landgrave Hermann I of Thuringia (1190 to "
        "1217) the centre of German song, where Walther von der Vogelweide won the singers' "
        "contest of 1204. The Hohenstaufen enlarged and fortified Frankfurt, where imperial "
        "elections are now held, and the Wittelsbachs have ruled Bavaria since 1180; "
        "Frederick II's court has visited Erfurt four times since 1214 and held its last "
        "German Diet for many years at Frankfurt in 1220."
    ),
    "east": (
        "The Marches between the Elbe and the Oder were Slavic lands, and Christianity came "
        "only in the tenth century from the frontier bishoprics of Magdeburg, Merseburg, "
        "Brandenburg (948) and Meissen (963), after Henry the Fowler fortified Meissen in "
        "929; the Slavic counter-attack later that century briefly undid the work. Since "
        "then war and peace with the Slavs have alternated with intermarriage and heavy "
        "German colonisation: the Wettins have ruled Meissen since 1089, Albert the Bear "
        "founded the March of Brandenburg in 1150, and the Saxon crusade of 1147 fell on the "
        "Wends of Pomerania. Valdemar I of Denmark conquered Rügen in 1168 and broke the "
        "temple of Arkona, Barbarossa made Bogislaw duke of Pomerania in 1181, and the "
        "Knights of the Sword, founded in 1202, crusade along the Baltic. Meissen is now "
        "wholly German, Lusatia mostly Sorb, and Rügen and Pomerania a mixed people under "
        "Danish overlords, with land so plentiful that the lords rarely quarrel."
    ),
    "bohemia": (
        "Bohemia has been ruled since the eighth century by the Premyslids, the line the "
        "Gifted princess Libuse founded when her vision at Vysehrad chose the ploughman "
        "Premysl as her husband. Christianity came in the ninth century with St Methodius "
        "and took generations to root; Duke Wenceslaus was murdered by his pagan brother "
        "early in the tenth, and the bishopric of Prague was created under Mainz in 973. "
        "Moravia passed to Poland in 999 and to Bohemia in 1019, and the kingdom has since "
        "been a semi-independent tributary of the empire, suffering Hungarian attacks early "
        "in the twelfth century, while Strahov (1140) and Sedlec (1142) brought the new "
        "monastic orders. Barbarossa raised the duchy to a subject kingdom a generation ago; "
        "King Otakar rules from Prague, and silver newly found at Sedlec promises to change "
        "a land of modest towns."
    ),
}


def build(rhine: Rhine) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary. Nothing is
    written when the Tribunal has not been made yet (the parts build in
    order, this one after the Tribunal's)."""
    tribunal = rhine.tribunal
    if tribunal is None:
        return
    for year, title, details, hidden in sorted(EVENTS, key=lambda e: e[0]):
        rhine.b.event(tribunal, year, title, secrets(details, hidden))
