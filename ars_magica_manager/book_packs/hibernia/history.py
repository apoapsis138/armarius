"""The Hibernian Tribunal's history, as the book tells it. The book's
history chapter runs from the five peoples of the old tales to the fall
of Praesis; the dated events are gathered from it and from every other
chapter: Patrick and the saints, the Order's arrival in 778, Diedne's
pogrom, the Ostmen and their rune wizards, the Treaty of Cnoc Maol Réidh,
the Tribunal's secession, each covenant's founding, the Schism War and
Clontarf, the English conquest, the quarrels of the two churches, and
the Siege of Praesis, each as a Tribunal Diary entry, up to spring 1220.
The ages before Patrick are only a sentence in the first entry.

Dates are AD. Where the book gives only a rough date ("after
Clontarf", "soon after the Treaty") the entry takes a round year and
says so. Where two chapters disagree, the entry follows the pack's
decisions (Elk's Run in 1159, Holzner's theft in 1213, the siege in 1214,
the fall in 1215) and gives the other reading in brackets; where the
book slips on a date history settles, the entry uses history's and gives
the book's in brackets. What the book foretells after 1220 belongs to the
lords' notes and the stories, not the Diary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import secrets

if TYPE_CHECKING:
    from . import Hibernia

#: The order of the seasons within a year; an entry with none comes first.
SEASON_ORDER = {"": 0, "Spring": 1, "Summer": 2, "Autumn": 3, "Winter": 4}

#: (year, season, title, details, hidden): one Diary entry each.
EVENTS: tuple[tuple[int, str, str, str, str], ...] = (
    # -- Saints and kings --
    (
        432,
        "",
        "Patrick's mission",
        "The old tales tell of five peoples who took Ireland one after another "
        "(Cessair's, Partholón's, Nemed's, the Fir Bolg and the Tuatha Dé) "
        "before the Sons of Míl, the Gaels, won it for good and the Tuatha Dé "
        "went under the hills. Palladius's mission had already failed when "
        "Patrick, once a slave of Irish raiders, comes back to preach. He goes "
        "round the island from Leinster to Connacht, Ulster, Meath and Munster, "
        "outdoes the druids in a contest of wonders and drives them out, banishes "
        "the snakes and turns the people Christian; he lies today in Down "
        "Cathedral. (The book says only the fifth century, and that the sources "
        "disagree; 432 is the year tradition gives.)",
        "",
    ),
    (
        450,
        "",
        "Patrick baptises Eóghan at Aileach",
        "At Aileach, Patrick baptises Eóghan son of Niall, from whom the Cenél "
        "nEóghain of Tír Eóghain descend.",
        "",
    ),
    (
        490,
        "",
        "Brigid's abbey at Kildare; the Uí Enechglaiss driven to Arklow",
        "In the last years of the century Saint Brigid founds a double house of "
        "monks and nuns at Cill Dara and lights the fire that has burned there "
        "ever since. In Meath the ruling Uí Enechglaiss are driven south to "
        "Arklow, and the Uí Mael Sechlainn, the southern Uí Néill, take the land "
        "and give Ireland several high-kings. Saint Aebh's monastery is founded "
        "at Antrim about the same time. (The book says only the late fifth "
        "century.)",
        "",
    ),
    (
        549,
        "",
        "Ciarán dies at Clonmacnoise",
        "Saint Ciarán, a founder of many monasteries, dies of the yellow plague "
        "at Clonmacnoise, his greatest house. (The book puts it early in the "
        "sixth century; the plague of Justinian came in the 540s.)",
        "",
    ),
    (
        555,
        "",
        "Comgall founds Bangor",
        "Saint Comgall founds the abbey of Beannchor Mór, around which the town "
        "of Bangor grows.",
        "",
    ),
    (
        560,
        "",
        "Ruadán curses Tara",
        "Saint Ruadán, wronged by King Diarmait, foretells that the king will die "
        "in his own hall at Tara; the high-kings' seat begins its long "
        "decline. (The book says only the sixth century.)",
        "",
    ),
    (
        571,
        "",
        "The Battle of Tola",
        "The Ulaidh beat the Osraighe at Tola, the first of the defeats that wear "
        "down the kingdom of Ossory.",
        "",
    ),
    # -- The Order comes to Ireland --
    (
        778,
        "",
        "Four magi come treasure-hunting",
        "Two Tytalus and two Merinita magae come looking for the four treasures "
        "of the Tuatha Dé. With a local ward-maker they dig a cauldron out of a "
        "mound at the Brú na Bóinne and take it for the Dagda's. The high-king "
        "sends his druid and a warband against the grave robbers; the five hold "
        "a barrow against three days of assaults, and, true to their leader's "
        "boast, stay on the mound for a whole year.",
        "The cauldron is not the Dagda's but the Cauldron of Llasar Llaes "
        "Gyfnewid, which raises a dead warrior to fight for one more day.",
    ),
    (
        780,
        "",
        "Circulus Ruber founded",
        "The four magae move to the Burren and raise a tower by magic on Hag's "
        "Head, among the Cliffs of Moher, vowing to hold it for a year. Local "
        "wizards and their kin fight hard to be rid of them, but with allies "
        "from the Rhine and Iberia the newcomers hold, and at the Tribunal of "
        "this year the covenant is founded, named for the red wards their "
        "helper drew. By the decade's end eight magi live there.",
        "",
    ),
    (
        793,
        "",
        "Diedne comes to Ireland",
        "Diedne arrives seeking the druids for her House, and the chief druid "
        "Sechnassach, offended by a choice of joining or dying, sends her away. "
        "She leaves with threats he does not take seriously.",
        "",
    ),
    (
        795,
        "",
        "The first Ostmen raids",
        "Norse and Danish raiders begin to fall on the monasteries without "
        "warning, at first only in spring and summer. Within a generation they "
        "stay, turning the coastal trading posts into the towns of Dublin, "
        "Waterford, Wexford, Cork and Limerick, and they bring rune wizards with "
        "them. (The book says only the late eighth century.)",
        "",
    ),
    (
        797,
        "",
        "Diedne's pogrom begins",
        "Twenty-seven Diedne magi land near Wexford and split into three bands "
        "of nine to hunt the druids, offering each the same choice; most "
        "choose death. Quendalon (Cuin-dallán), an Ulsterman of House "
        "Merinita, comes home from the Rhine to save what he can: some of the "
        "old wizards he takes into his House, others he hides in Connacht. "
        "Meanwhile the Diedne found covenants of their own and dig in. In the "
        "midst of the purge the druid Raghallach meets Petrifer of House "
        "Flambeau, attacks him on learning he is a magus, and is won over to "
        "the Order instead.",
        "",
    ),
    (
        800,
        "",
        "Qui Sonant Pro Quieto founded",
        "The druids who sing the giant to sleep in the Cuailnge mountains, at a "
        "place already old and already a burial ground for Ireland's magical "
        "powers, join the Order, and the covenant grows up around them. Ever "
        "since, Hibernia's magi have been laid to rest there. (The book gives "
        "no year, only that the druids joined the Order after the magi came.)",
        "",
    ),
    (
        806,
        "",
        "Diedne and Pralix quarrel at Lough Cuan",
        "Pralix, chasing followers of Damhan-Allaidh, meets Diedne on the shore "
        "of Lough Cuan. Diedne expects help with her purge; Pralix wants to "
        "recruit the druids without forcing them. Their argument becomes an "
        "illegal Wizard War that neither ever charges, and Nendrum monastery on "
        "Machaoi island is left in ruins, no one knows by which of them. About "
        "twenty of Ireland's stronger native wizards fight for Pralix against "
        "Damhan-Allaidh, and the survivors join her new order, the root of "
        "House Ex Miscellanea.",
        "",
    ),
    (
        816,
        "",
        "Diedne boasts the druids are gone",
        "After almost fifteen years of killing, Diedne tells the Tribunal that "
        "not one druid is left in Ireland. It is an exaggeration, but the old "
        "tradition is broken. (The history chapter counts seventeen years of "
        "pogrom from 793.)",
        "",
    ),
    (
        826,
        "",
        "Lámbaird founded",
        "Petrifer and Raghallach of House Flambeau turn their camp in the Wicklow "
        "Mountains, a refuge for Raghallach's tradition, into the covenant of "
        "Lámbaird. Diedne's complaints at Tribunal fail, so she makes Wizard War "
        "on the druids in House Flambeau; only Raghallach and two others live "
        "to found the school of magical combat that bears his name.",
        "",
    ),
    (
        830,
        "",
        "Rune wizards raid the Diedne Vigil",
        "Runesmiths from Dublin raid Vigil, then a Diedne covenant in the "
        "Sperrin foothills whose magi won their standing by killing the great "
        "black pig and keeping its tusks. Vigil recovers and helps defend other "
        "covenants against the northmen's wizards.",
        "",
    ),
    (
        832,
        "",
        "The Order of Odin",
        "At the Grand Tribunal, Hibernia's magi name the Ostmen's wizards \"the "
        'Order of Odin." Unsure of their strength, the Order looks for peace: '
        "Máel-tuili of House Merinita meets the Dublin rune wizards and offers "
        "a large tribute, but they fall on his party and kill most of it, "
        "Máel-tuili among them. Skirmishes with rune wizards, raids on native "
        "druids and certamen in reprisal become the custom of the age.",
        "",
    ),
    (
        844,
        "",
        "The high-king's embassy",
        "Cormacan the Learned, Chief Bard of Ireland, brings an embassy from the "
        "high-king: his subjects, hedge wizards, complain of the Order's "
        "harassment. The Mercere Fedelmid Ua Heirméais is chosen to treat for "
        "the Order, and since Diedne's pogrom has shown that the Irish would "
        "rather die than join, he looks for another way. (The book names the "
        "high-king Congalach Cnogba, who in history reigned a century later.)",
        "",
    ),
    (
        851,
        "",
        "Diedne withdraws; the Treaty of Cnoc Maol Réidh",
        "On the brink of open war over peace with the Coill Trí, Primus Obregon "
        "declares that the Diedne will no longer shield their unworthy sodales, "
        "and Hibernia's Diedne shut themselves in their covenants. In their "
        "absence the other magi sign the Treaty of Cnoc Maol Réidh. The Diedne "
        "never accept it and keep entering Connacht, so hedge wizards seek out "
        "magi as personal protectors, one to one, on the model of amici.",
        "",
    ),
    (
        852,
        "",
        "Merinita take Vigil north",
        "With House Diedne gone from the Tribunal's affairs, a band of Merinita "
        "magi sacks the Diedne Vigil and carries the boar's tusks to the far "
        "north, where they raise a new fortress and an unseen tower from which "
        "all Ireland can be watched, to hunt the rune wizards and their "
        "warriors. Fighting the Diedne and the northmen at once, Vigil makes "
        "pacts with the faeries and beasts of the northern sea that guard the "
        "coast to this day. (The book says only after 851.)",
        "",
    ),
    (
        865,
        "",
        "Hibernia made part of Britannia",
        "At the Grand Tribunal Hibernia's magi complain of raiders from England "
        "and Scotland, and are told their treaty with the hedge wizards is "
        "illegal. Ireland is joined to England and Scotland in the new "
        "Britannian Tribunal under its Peripheral Code, and the Irish plea that "
        "the Treaty alone keeps the native traditions alive is refused.",
        "",
    ),
    (
        898,
        "",
        "The Hibernian Tribunal; the Treaty ratified",
        "Following the Tytalus lead, the Irish magi leave the Britannian "
        "Tribunal. The first Hibernian Tribunal ratifies the Treaty of Cnoc "
        "Maol Réidh and holds every private treaty between magus and hedge "
        "wizard binding; those who flouted them are brought to heel. The hedge "
        "wizards of Connacht are gathered into the Comman Cosán Chían, soon "
        "called the Coill Trí, and those who quarrel with magi over resources "
        "are helped, or pushed, to move there. The same meeting gives rise to "
        "the two Mercer Houses: the Redcap Imag, wife of the abbot of Cloyne, "
        "is granted the southern house of Leth Moga and begins the Red Book of "
        "Cloyne, and Leth Cuinn is founded on Lough Neagh. Treaties, trophies "
        "and lawful raiding enter the Code as an outlet for the island's "
        "violence.",
        "",
    ),
    (
        855,
        "",
        "Praesis founded",
        "Praesis is raised on an island in Lough Ree, on the border of Connacht "
        "and Meath, as a meeting place between the Order and the Coill Trí. "
        "Within a century its purpose is mostly forgotten and its standing on "
        "the wane. (The book says only soon after the Treaty.)",
        "",
    ),
    (
        909,
        "",
        "Clonmacnoise's stone cathedral",
        "The high-king builds the stone cathedral at Clonmacnoise.",
        "",
    ),
    (
        975,
        "",
        "Mathgamain slain",
        "Mathgamain mac Cennétig, who won Cashel and Limerick for the Dál gCais, "
        "is killed, leaving his brother Brian Bóramha sole king of Munster.",
        "",
    ),
    (
        980,
        "",
        "The Battle of Teamhrach",
        "Olaf Cuaran, king of Dublin and Northumberland, threatens Tara. Vigil "
        "magically binds the kings of Leinster and Ulster in a pact with Máel "
        "Sechnaill mac Domnaill, then fights beside his army to rout the "
        "northmen and open the way to Dublin. The Tribunal lets this "
        "interference go unpunished, holding Tara's sanctity at stake.",
        "",
    ),
    (
        986,
        "",
        "A pestilence out of Tír Chonaill",
        "Another of the great plagues born in Tír Chonaill sweeps Ireland, and "
        "the annals tell of demons dancing among the dead.",
        "",
    ),
    (
        1002,
        "",
        "Brian Bóramha high-king",
        "Having beaten Munster's and Leinster's ruling clans, Brian marches into "
        "Ulster and the Uí Néill high-king gives up the title to him. Druids and "
        "hedge wizards of Munster march with his army, and the magi watch him "
        "so closely that the Schism War takes them by surprise.",
        "",
    ),
    # -- The Schism War --
    (
        1011,
        "",
        "The Schism War: the Widow's Throat falls",
        "Of the Tribunal's six Diedne covenants, three prove empty, their magi "
        "fled abroad or gathered in the other three, and the Hibernian magi "
        "split their forces against them. The Diedne have allies ready: Salmon's "
        "Eye in Munster has Donn, and the Widow's Throat in Ulster has a Fomóir "
        "fleet, five ships of which sail up the Shannon while five fall on "
        "Circulus Ruber. The magi regroup to save Circulus Ruber and beat the "
        "fleet at sea, then destroy the Widow's Throat; two months later their "
        "first attack on Lugh's Retreat, at the Shannon's source in the Dartry "
        "Mountains, fails. Vigil strikes its old enemies hard, taking heads, "
        "libraries and familiars, and Lámbaird draws Flambeau from abroad to "
        'fight, earning the name "Lombard." (The book gives no years for '
        "these battles, only that they come before Clontarf.)",
        "",
    ),
    (
        1012,
        "",
        "The Schism War: Warbler's Way and Salmon's Eye",
        "The Munster Diedne and Donn's host destroy Warbler's Way, a Merinita "
        "covenant in the woods by Lough Leane. The magi unite to answer, raze "
        "Salmon's Eye and drive Donn back to his island. So many dead are "
        "brought to Qui Sonant in these years that the record of who lies there "
        "is lost. (The book gives no year.)",
        "",
    ),
    (
        1013,
        "",
        "The Third Battle of Moytirra",
        "Two years after the first assault the magi move on Lugh's Retreat "
        "again, joined this time by the druids and hedge wizards of Connacht, "
        "whom Mercere messengers had warned. Together they destroy it, killing "
        "Fomóir and Diedne alike. The poets call it the Third Battle of "
        "Moytirra. (The book gives no year.)",
        "",
    ),
    (
        1014,
        "Spring",
        "Clontarf",
        "Brian Bóramha marches on the Ostmen of Dublin. His dwarf druid, "
        "Muírcheartach mac Lía, warns Lámbaird's magi that druids calling "
        "themselves sons of Diedne ride with the army, and the Flambeau go to "
        "the battle. On Good Friday, while Irish and Ostmen fight at Clontarf, "
        "they hunt the Diedne down in a short and blazing duel that ends the "
        "House in Hibernia. The Ostmen are beaten for good, but Brian dies on "
        "the field and his army goes home too weak to rule the island. No one "
        "knows what became of the three Diedne bodies: Cliffheart says one is "
        "its cathach, and some say Qui Sonant buried each beside a rival.",
        "Cliffheart's cathach is a Diedne magus turned to a standing stone, "
        "alive only while the spell holds; the magi renew it every year, since "
        "its ending would kill him at once.",
    ),
    (
        1015,
        "",
        "Cliffheart founded",
        "Three Merinita survivors of Warbler's Way, who fought the Diedne for "
        "their alliance with Munster's Tuatha Dé, settle on Cape Clear Island "
        "and found Cliffheart. (The book says only after Clontarf.)",
        "",
    ),
    (
        1016,
        "",
        "The Red Book closed",
        "Fergal mac Cuircc of Leth Moga, having set down the Schism War in the "
        "Red Book of Cloyne, closes it to all but Redcaps so that the magi may "
        "forget their war; he goes on recording. (The book says only after the "
        "Schism War.)",
        "",
    ),
    (
        1020,
        "",
        "The Ostmen thrown out of Cork",
        "Raiding Ostmen winter at Cork; an Uí Briain and mac Cárthaigh army "
        "storms the walls while its druids blast the earthworks with lightning, "
        "and Cork becomes the one Irish town to cast the Ostmen out.",
        "",
    ),
    (
        1029,
        "",
        "Dáire Farranta takes Leth Cuinn",
        "Back after seven years away, Dáire Farranta challenges his parens, the "
        "leader of Leth Cuinn, to Wizard War and wins with no spell cast, by "
        "feats of the clesrada. He exiles the other Redcaps, fills the house "
        "with his own kin and the faerie Úathach who taught him, and makes it "
        "an outpost of the Cult of Heroes, which his descendants still run.",
        "",
    ),
    (
        1084,
        "",
        "The Rogh Rámhach",
        "A plague called the Rogh Rámhach is said to kill a quarter of Ireland.",
        "",
    ),
    (
        1096,
        "",
        "The Scuab a Fánait foretold",
        "A pestilence is prophesied to come out of the north of Tír Chonaill. "
        "It never does.",
        "",
    ),
    (
        1101,
        "",
        "Aileach broken",
        "The King of Munster breaks the power of Aileach in Tír Eóghain.",
        "",
    ),
    (
        1124,
        "",
        "Dún Bhun na Gaillimhe built",
        "Tairrdelbach Uí Conchobhair builds a fort above Loch Lurgain as a naval "
        "base; Munster's kings destroy it in 1132 and again in 1149.",
        "",
    ),
    (
        1132,
        "",
        "Malachy archbishop of Armagh; Kildare's abbess deposed",
        "Máel Máedóc, later Saint Malachy, becomes Archbishop of Armagh and "
        "sets about reforming a lax church. Diarmait Mac Murchada removes the "
        "abbess of Kildare and gives the post to his niece.",
        "",
    ),
    (
        1135,
        "",
        "Cong Abbey rebuilt",
        "Cong Abbey, burned early in the century, is rebuilt. (The book says "
        "about 1135.)",
        "",
    ),
    (
        1137,
        "",
        "Malachy goes to Down",
        "Malachy resigns Armagh to become Bishop of Down, ruling from Bangor and "
        "bringing Augustinian canons to Downpatrick.",
        "",
    ),
    (
        1140,
        "",
        "Mellifont founded",
        "Malachy founds Mellifont, near Drogheda, on land from the King of "
        "Meath; it becomes mother of most of Ireland's Cistercian houses. He "
        "also founds the Augustinian abbey of Saint Mary at Trim.",
        "",
    ),
    (
        1142,
        "",
        "Newry and Cahir",
        "Cistercians rebuild the old monastery at Newry, and a town grows up "
        "around it. Conchovor Uí Briain builds Cahir castle.",
        "",
    ),
    (
        1148,
        "",
        "Malachy dies; Baltinglass founded",
        "Saint Malachy dies. Diarmait mac Murchadha founds a Cistercian house at "
        "Baltinglass with monks from Mellifont, and the place is called the "
        "Valley of Salvation.",
        "",
    ),
    (
        1152,
        "",
        "The Synod of Kells; Derbforgaill taken",
        "The Synod of Kells ratifies Malachy's reforms and divides Ireland into "
        "thirty-six sees under four archbishops, at Armagh, Cashel, Dublin and "
        "Tuam; Kildare's abbess is put under the bishop. Diarmait Mac Murchada, "
        "King of Leinster, carries off Derbforgaill, wife of Tighearnán Ua "
        "Ruairc of Bréifne, the Irish Helen, who is content to stay with him.",
        "",
    ),
    (
        1154,
        "",
        "A King of Meath deposed by Mellifont",
        "At the abbot of Mellifont's urging, a synod excommunicates and exiles "
        "Donnchadh Ua Maeleachlainn, King of Meath, and makes his brother "
        "Diarmaid king.",
        "",
    ),
    (
        1155,
        "",
        "Laudabiliter",
        "Pope Adrian's bull Laudabiliter, later read as granting Henry II the "
        "right to take Ireland and reform its church.",
        "",
    ),
    (
        1159,
        "",
        "Elk's Run founded",
        "Oswald of Bonisagus and Lugardis of Guernicus arrive from abroad with "
        "cattle, silver, unknown vis sources and the antlers of a giant elk, "
        "and claim a valley in the Slieve Aughty. Irish magi challenge the "
        "cathach and the vis; Oswald wagers for all he can ride round before "
        "sunset without a spell, throws down the antlers, and rides the living "
        "elk they become over the mountains until dusk. Elk's Run is founded. "
        "(The history chapter places it just after the Grand Tribunal of 1195; "
        "this pack follows the Munster chapter's 1159.)",
        "",
    ),
    (
        1160,
        "",
        "Derry's Great Church; the Nun's Church",
        "Tempull Mór is finished at Doire. Derbforgaill endows the Nun's Church "
        "at Clonmacnoise. Domnall Mac Giolla Phádraig founds a Benedictine house "
        "for Saint Nicholas's relics where Jerpoint now stands; it fails.",
        "",
    ),
    (
        1161,
        "",
        "The Mac Diarmaids turn the druids away",
        "From this year the Mac Diarmaids, patrons of Boyle, keep no druid at "
        "their court.",
        "",
    ),
    (
        1164,
        "",
        "A castle at Tuam",
        "The Uí Conchobhair build a castle at Tuam to tighten their hold on Connacht.",
        "",
    ),
    (
        1166,
        "",
        "Diarmait exiled",
        "Tighearnán Ua Ruairc invades Leinster, Ossory rises, and Diarmait Mac "
        "Murchada loses his throne and flees to England. Henry II will not "
        "invade for him, so he hires English mercenaries, while the new "
        "high-king, Ruaidrí Ua Conchobair, takes Leinster.",
        "",
    ),
    (
        1168,
        "",
        "A gathering at Tlachtga; Christchurch Augustinian",
        "Ruaidrí Ua Conchobair musters a great host at the Hill of Tlachtga, but "
        "Tlachtga does not show herself. Lorcán Ua Túathal makes Christchurch "
        "in Dublin an Augustinian priory.",
        "",
    ),
    (
        1169,
        "",
        "The English land",
        "Diarmait and Robert FitzStephen besiege Wexford, which the Bishop of "
        "Ferns persuades to open its gates, and win the Pass of Achad-ur from "
        "the Osraighe with a Norman cavalry charge.",
        "",
    ),
    (
        1170,
        "",
        "Strongbow",
        "Strongbow, Earl of Pembroke, invades Leinster, puts Diarmait back on "
        "his throne and marries his daughter Aoife. The conquest stirs the "
        "Order's interest in Hibernia for the first time in a long while, "
        "House Tremere first among them.",
        "",
    ),
    (
        1171,
        "",
        "Diarmait dies; Henry II comes",
        "Diarmait dies and Strongbow takes Leinster, against Brehon law. Henry "
        "II comes to bring his vassal to heel, takes Dublin, Wexford and "
        "Wicklow for the crown, receives the Irish kings' tribute and has a "
        "synod called at Cashel. The English close the abbey of Kildare when "
        "its last abbess dies. Tighearnán Ua Ruairc parleys with Hugh de Lacy "
        "on Tlachtga and is killed, by murder or mishap. (History puts his "
        "death in 1172.)",
        "",
    ),
    (
        1172,
        "",
        "Meath granted to Hugh de Lacy",
        "The last King of Meath is deposed and his kingdom granted to Hugh de "
        "Lacy; the Uí Mael Sechlainn settle near Clonmacnoise. Henry II sails "
        "for France from Wexford, leaving its mills to the Templars. Bishop "
        "Tuathal Ua Connachtaig of Kells swears fealty to Henry, to much "
        "anger.",
        "",
    ),
    (
        1174,
        "",
        "Limerick burned",
        "Domnall Mór Uí Briain burns Limerick rather than let the English have it.",
        "",
    ),
    (
        1175,
        "Autumn",
        "The Treaty of Windsor",
        "Ruaidhri Uí Conchobhair, unable to stop the English, seeks the Fir Bolg "
        "kings on Árainn Mhór, who give him Fionntan's counsel. On 6 October he "
        "signs the Treaty of Windsor, owning Henry as ruler of Ireland and "
        "keeping Connacht for a yearly tribute still paid.",
        "",
    ),
    (
        1177,
        "",
        "De Courcy takes Ulster",
        "John de Courcy, granted Ulster if he can win it, marches with twenty-two "
        "knights and some three hundred men and takes Down by surprise on 1 "
        "February. The King of Ulster, laid low by Macha's Birth-Pangs, returns "
        "with an army a week later and is routed, and de Courcy soon holds all "
        "the land east of the Bann. He sacks the abbey of Erenagh and builds "
        "castles at Belfast and Carrickfergus. Cork, held back from the English "
        "by mac Cárthaigh, is granted to Robert FitzStephen and Milo de Cogan, "
        "who take it by force.",
        "",
    ),
    (
        1180,
        "",
        "Inch, Dundrum and Jerpoint",
        "De Courcy founds the Cistercian abbey on Iniscourcy in penance for "
        "Erenagh and builds Dundrum castle. Donogh O'Donoghoe, king of the "
        "Osraighe, founds Jerpoint Abbey. Work begins on Clonfert's cathedral, "
        "where a magical mason's arch draws beasts of every realm to watch.",
        "",
    ),
    (
        1181,
        "",
        "The Temple House at Ballymote",
        "The Templars build Connacht's only Temple House near Ballymote, close "
        "to the Bréifne border.",
        "",
    ),
    (
        1183,
        "",
        "Down's cathedral priory",
        "De Courcy founds a Benedictine cathedral priory at Downpatrick with "
        "monks from Chester.",
        "",
    ),
    (
        1184,
        "",
        "Tuam's cathedral burns",
        "Tuam's cathedral burns down; it has not been rebuilt.",
        "",
    ),
    (
        1185,
        "",
        "Prince John, Lord of Ireland; Ruaidrí abdicates",
        "Henry II makes his son John Lord of Ireland. John, seventeen, mocks the "
        "Irish kings who come to do him homage and pulls their beards. Gerald "
        "of Wales comes with him, and his books on the marvels of Ireland stir "
        "Stonehenge's magi to talk of reform. Ruaidrí Ua Conchobair gives up "
        "the high-kingship and retires to Cong. Aed Meith Ua Néill seizes "
        "Tír Eóghain from Aileach. Work begins on Saint Flannan's cathedral at "
        "Killaloe. Using minstrels, Helles and Pollices persuade Raymond le Gros "
        "that the Uí Riain plan rebellion and, in the fighting, take Rhiannon's "
        "body from their chief's ráth. (The book gives no year for the theft.)",
        "",
    ),
    (
        1186,
        "",
        "The Tribunal of 1186: Ashenrise's cathach",
        "Helles and Pollices, refugees from Normandy's fallen Moles Magna, with "
        "three sodales from Stonehenge, present the dancing corpse of Rhiannon, "
        "a former Prima of House Merinita, at Tara and announce their "
        "covenant, to live as guests in a FitzGerald knight's castle. The hall "
        "erupts and Wizard Wars are declared, but Conán Derg, then praeco, "
        "accepts it, ruling that the raw vis grown in its bones makes it magical "
        "enough. Hugh de Lacy dies, and Walter de Lacy will take Meath. A church "
        "council at Dublin, called at Prince John's wish, shows how far English "
        "reform means to go.",
        "",
    ),
    (
        1186,
        "",
        "Conán Derg maimed",
        "Two months after the Tribunal, walking alone on the Connacht border, "
        "Conán Derg loses his right arm to an attacker. Refusing to regrow it, "
        "he holds that a leader must be whole, gives up the office of praeco "
        "and leaves Hermetic politics. Some magi suspect Faisgia of Cliffheart, "
        "who often travels there; Conán Derg will neither confirm nor deny it, "
        "and Faisgia scorns the charge.",
        "",
    ),
    (
        1187,
        "",
        "Ashenrise recognised",
        "Helles and Pollices hold Rhiannon's corpse for a year against all "
        "comers, and Ashenrise is a covenant at law. It has pressed for reform "
        "of the Code ever since.",
        "",
    ),
    (
        1189,
        "",
        "The Paruchia of Nerius",
        "Fedelmid of Limerick, who saw visions of the magus-saint Nerius in an "
        "Alpine valley on pilgrimage to Rome, with his apprentice Indrechtach "
        "and Indrechtach's own pupil, brings a tiny tradition of the Céli Dé "
        "into House Ex Miscellanea and founds a monastery and covenant on the "
        "Saltee islands.",
        "",
    ),
    (
        1190,
        "",
        "Damisona attacked; Dublin burns",
        "Damisona of Jerbiton and her party are set upon by what seem to be young "
        "Irish magi, and three grogs die. Knowing nothing of the macgnímartha, "
        "Stonehenge cries out for something to be done about Hibernia. A great "
        "fire wrecks Dublin, and settlers from Bristol and Wales take the place "
        "of those who leave.",
        "",
    ),
    (
        1193,
        "",
        "The Tribunal of 1193: Lámbaird reprimanded",
        "Lámbaird's secret help to the Wicklow clans against the English is "
        "noticed, and the Tribunal reprimands the covenant without a sanction. "
        "Milvia of Bonisagus presides as praeco, as she has at every meeting "
        "since. Geoffrey fitz Robert founds Saint Mary's priory at Kells in "
        "Ossory.",
        "",
    ),
    (
        1194,
        "",
        "Limerick falls to the English; Drogheda's charter",
        "Domnall Mór Uí Briain dies, and the English take Limerick and most of "
        "its lands. Drogheda-in-Meath receives its charter.",
        "",
    ),
    (
        1195,
        "",
        "The Grand Tribunal at Durenmar",
        "Magi who want Hibernia reformed under a Code like Stonehenge's debate "
        "long against those who uphold a Tribunal's right to its own; Milvia "
        "leads the Hibernian delegation. The parentes of the apprentices who "
        "attacked Damisona in their macgnímartha are found guilty only of a "
        "Low Crime, to Stonehenge's fury. Traffic with the continent and "
        "appeals to Magvillus grow. William Marshal builds his castle at "
        "Kilkenny.",
        "",
    ),
    (
        1196,
        "",
        "De Courcy beats Tír Chonaill",
        "De Courcy defeats the King of Tír Chonaill and takes tribute from his land.",
        "",
    ),
    (
        1197,
        "",
        "Limerick chartered",
        "Limerick receives its charter and is given to Philip de Braose.",
        "",
    ),
    (
        1198,
        "",
        "Ruaidrí dies; de Courcy's revenge",
        "Ruaidrí Ua Conchobair, the last High-King, dies at Cong and is buried "
        "at Clonmacnoise. After his brother is murdered at his court, de Courcy "
        "harries the north of Ulster and destroys Raphoe's cathedral. "
        "Archbishop John Comyns orders Saint Patrick's Cathedral built in "
        "Dublin.",
        "",
    ),
    (
        1199,
        "",
        "King John; Lismore's bishop returns",
        "John becomes King of England, to de Courcy's ruin (the book dates his "
        "accession to 1201). Desmond gives up its long sieges of Cork. When the "
        "English Bishop of Waterford, who had seized Lismore and driven out "
        "Bishop Felix, dies, Felix goes home, and the long quarrel of Waterford "
        "and Lismore begins.",
        "",
    ),
    (
        1200,
        "",
        "King John's Castle; Temple Melaghlin",
        "King John's Castle rises on King's Island in Limerick. The Uí Mael "
        "Sechlainn build Temple Melaghlin at Clonmacnoise.",
        "",
    ),
    (
        1202,
        "",
        "Mayo dissolved; Ossory's cathedral moved",
        "A papal legate dissolves the diocese of Mayo into Tuam, against its "
        "clergy's will. Bishop Felix O'Dulany moves Ossory's see to Kilkenny "
        "and begins a stone cathedral, dying the same year.",
        "",
    ),
    (
        1203,
        "",
        "De Courcy overthrown; Cong attacked",
        "Allied with Cathal Crobhdearg of Connacht, de Courcy is taken in "
        "rebellion by Hugh de Lacy, younger son of the Lord of Meath. William "
        "de Burgh attacks Cong Abbey, deep in Connacht.",
        "",
    ),
    (
        1204,
        "",
        "Dublin Castle; Malachy back at Lismore",
        "King John orders a castle built at Dublin. Bishop Malachy of Lismore, "
        "who escaped Waterford's prison and was restored by Innocent III, comes "
        "home to find his rival Robert dead.",
        "",
    ),
    (
        1205,
        "Spring",
        "Hugh de Lacy, Earl of Ulster",
        "In May King John makes Hugh de Lacy the first Earl of Ulster, with all "
        "the lands de Courcy held.",
        "",
    ),
    (
        1206,
        "",
        "The Liberty of Kildare",
        "King John creates the Liberty of Kildare to crush the deposed Uí "
        "Dúnlainge, and summons the nobles to Naas to submit.",
        "",
    ),
    (
        1207,
        "",
        "Charters for Kilkenny and New Ross; Bishop David killed",
        "Kilkenny and New Ross receive royal charters. Malachy, driven from "
        "Lismore again by the Welsh Bishop David of Waterford and confirmed "
        "again at Rome, returns to find David murdered.",
        "",
    ),
    (
        1208,
        "",
        "Plague in Dublin",
        "A terrible plague kills many in Dublin.",
        "",
    ),
    (
        1209,
        "Spring",
        "Black Monday; Swan of Ghent killed",
        "On Easter Monday the Ua Broin and Ua Túathal fall on English settlers "
        "at their sport outside Dublin's walls and kill three hundred. The "
        "maga Swan of Ghent dies among them. Dublin still marks the day under "
        "arms.",
        "",
    ),
    (
        1210,
        "",
        "Munster granted; Waterford's new bishop",
        "King John grants Munster to his favourites, keeping Waterford, "
        "Limerick and Cork: the lands north of Waterford to Robert le Poer, "
        "Thomond to Philip de Braose, Desmond to Robert FitzStephen and Milo de "
        "Cogan, none of whom can take them. Kerry becomes a shire. Robert II is "
        "consecrated Bishop of Waterford, seizes Malachy, and has him "
        "tortured; no court dares convict him. John de Gray, the justiciar, "
        "builds a stone castle at Athlone, now Walter de Lacy's. (The book says "
        "ten years before 1220.)",
        "",
    ),
    (
        1211,
        "",
        "Kilmore castle",
        "Walter de Lacy builds a motte and bailey at Kilmore, one of many for a "
        "push into Connacht. Geoffrey fitz Robert dies a hostage of William "
        "Marshal at Hereford.",
        "",
    ),
    # -- The Siege of Praesis --
    (
        1213,
        "Spring",
        "Holzner at Praesis",
        "Praesis, wary of foreigners, accepts Holzner of Tytalus from the Rhine. "
        "He tries to steal the covenant's cathach, the Gáe Bulg, and flee, and "
        "is caught and executed; Meadhbh, its leader, hangs his head by the "
        "hair from the palisade. His parens Ballack leaves the Rhine for "
        "Hibernia, persuades others that if the Tribunal will not punish "
        "Praesis they must take it by force, and declares Wizard War. (The "
        "Connacht chapter puts the theft two years after his arrival.)",
        "",
    ),
    (
        1214,
        "",
        "The Siege of Praesis; the Tribunal of 1214",
        "Repulsed by a covenant stronger than it looked, Ballack's forces camp on "
        "Lough Ree's eastern shore, strip Praesis's vis sources and kill anyone "
        "who goes in or out. The siege keeps Praesis from the Tribunal at Tara, "
        "where it might have found allies; few intervene, since the Code allows "
        "the war, and the Tribunal debates while mercenaries and young magi on "
        "both sides die. At the same meeting Oswald of Elk's Run is granted a "
        "second, Irish-born apprentice. The mac Cárthaighs massacre Uí "
        "Súilleabháin nobles at a peace feast at Raheen, and within the year "
        "Desmond falls to a war between two mac Cárthaigh brothers. Glendalough's "
        "diocese is folded into Dublin's.",
        "",
    ),
    (
        1215,
        "",
        "Praesis falls",
        "After four seasons of stalemate Ballack's nerve outlasts the defenders'. "
        "As the last of Praesis's allies flee, Báetáin Ua Traimair trades the "
        "cathach for Meadhbh's safe passage, and Ballack takes the covenant; "
        "Meadhbh claims sanctuary at Qui Sonant. The druids of Oireadh, once "
        "Praesis's friends, had already left Meadhbh over her demands. William "
        "Marshal the younger loses his wife.",
        "Ballack has spent everything he had on the war and borrows vis and "
        "casting tablets from distant, powerful benefactors whose debts he is "
        "beginning to forget.",
    ),
    (
        1216,
        "",
        "The Conspiracy of Mellifont; King John dies",
        "A visitation from Cîteaux arrives to restore the Rule in Ireland, and "
        "Mellifont shuts its gates on it. Innocent III confirms the end of the "
        "diocese of Mayo. King John dies; his young son Henry III succeeds, and "
        "Waterford's bishop loses his protector, ending the Lismore quarrel "
        "for now.",
        "",
    ),
    (
        1217,
        "",
        "Abbot Thomas deposed; the itinerant justices",
        "The Cistercian general chapter deposes Thomas, abbot of Mellifont, in "
        "name only: backed by his monks and daughter houses, he stays. Itinerant "
        "justices begin riding the Liberties to hold English assizes. Dublin "
        "pays the royal tallage.",
        "",
    ),
    (
        1218,
        "",
        "The Chief Bard dies",
        "Giolla Ernain Ua Martain, Chief Bard of Ireland, dies, and no successor "
        "has been chosen. Boyle's abbey church is consecrated. Ailbe Ua Mail "
        "Mhuaidh, Bishop of Ferns, writes a life of Saint Abbán.",
        "",
    ),
    (
        1219,
        "",
        "William Marshal dies; Cashel goes to Rome",
        "William Marshal dies, and his son William the younger takes up the "
        "regency. The Archbishop of Cashel leaves for Rome to plead the Irish "
        "clergy's case against the bar on Irish-born bishops.",
        "The Pope has ruled the policy against Rome's will; the archbishop will "
        "be home with the order to drop it in August 1220, and word has not yet "
        "reached Henry de Londres.",
    ),
    (
        1220,
        "",
        "Henry de Londres vows to quench Brigid's fire",
        "Archbishop Henry de Londres, viceroy in Dublin, declares he will put out "
        "Saint Brigid's sacred fire at Kildare to prove it a superstition, a "
        "blow at the Uí Dúnlainge whose patroness she is.",
        "",
    ),
)


def build(hibernia: Hibernia) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, in order of
    year and season. Nothing is written when the Tribunal has not been
    made yet (the parts build in order, this one after the Tribunal's)."""
    tribunal = hibernia.tribunal
    if tribunal is None:
        return
    for year, season, title, details, hidden in sorted(
        EVENTS, key=lambda e: (e[0], SEASON_ORDER[e[1]])
    ):
        hibernia.b.event(tribunal, year, title, secrets(details, hidden), season=season)
