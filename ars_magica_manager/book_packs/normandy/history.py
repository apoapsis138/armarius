"""The Normandy Tribunal's history, as the book tells it: every Hermetic
event up to spring 1220 as a Tribunal Diary entry (the founding and
fall of each covenant, the dated meetings of the Tribunal and the Grand
Tribunals), and the mundane history of Mythic France, era by era, for
the Tribunal's History.

Dates are AD. The book's timeline also looks ahead past 1220, for a
saga that follows real history; those years are not events yet, so they
close the History under its Secrets heading rather than going in the
Diary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import as_secrets, secret_words
from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from . import Normandy

#: (year, title, details, hidden): one Diary entry each, in order of year.
EVENTS: tuple[tuple[int, str, str, str], ...] = (
    # -- The Founders and the first Tribunals --
    (
        731,
        "Trianoma's travels begin",
        "For more than thirty years Trianoma journeys across Europe, seeking out wizards "
        "and bringing them to meet Bonisagus. Many of those she finds become Founders of "
        "the Order.",
        "",
    ),
    (
        767,
        "Foundation of the Order of Hermes",
        "Bonisagus and the other Founders take the Oath of Hermes, and the first gathering "
        "of the Order is held at Durenmar.",
        "",
    ),
    (
        773,
        "Second Grand Tribunal: what a Tribunal is",
        "The Order settles how lesser Tribunals work: one needs at least twelve magi drawn "
        "from at least four covenants.",
        "",
    ),
    (
        789,
        "Jerbiton meets Charlemagne",
        "The Founder Jerbiton, who has taken on several apprentices of the emperor's "
        "mage-smith Carolinus, meets Charlemagne. The emperor's decree against sorcery and "
        "paganism that year spares magic of a kindly sort, such as Jerbiton's.",
        "",
    ),
    (
        791,
        "Branugurix founded",
        "House Diedne raises its domus magna, Branugurix (in Breton Bren Gwrac'h), in a "
        "regio near Mount Dol in Brittany. It becomes the head of a line of Diedne vassal "
        "covenants.",
        "",
    ),
    (
        798,
        "Tytalus founds Fudarus",
        "Tytalus carries off Hariste, the apprentice of his own former pupil Pralix, and "
        "raises the fortress of Fudarus on Ushant to keep her safe from Pralix's anger. "
        "He trains her to the Gauntlet in five years. Pralix takes over the running of "
        "House Tytalus.",
        "",
    ),
    (
        799,
        "Third Grand Tribunal",
        "The Order's third Grand Tribunal meets.",
        "",
    ),
    (
        807,
        "Tytalus vanishes; Hariste first Prima",
        "Tytalus walks out of Fudarus in a leper's robe and veil, staff in hand, visits his "
        "followers one last time and disappears into the Maddenhofen Woods of Bohemia. "
        "Hariste claims Fudarus and becomes the first Prima of House Tytalus; the "
        "covenant has housed the Primus ever since.",
        "",
    ),
    (
        810,
        "Confluensis founded",
        "Confluensis is founded at the mouth of the Seine, on the site Dragon's Rest holds "
        "today.",
        "",
    ),
    (
        817,
        "Fourth Grand Tribunal",
        "The Order's fourth Grand Tribunal meets.",
        "",
    ),
    (
        822,
        "Bibracte founded",
        "Bibracte, a vassal of Fudarus, is founded on Mount Beuvray in the Morvan by a few "
        "Diedne magi and one Tytalan.",
        "",
    ),
    (
        832,
        "Fifth Grand Tribunal: the seven-year cycle",
        "The Grand Tribunal fixes its own meetings at every thirty-three years, and those "
        "of the regional Tribunals at every seven years from 836.",
        "",
    ),
    (
        840,
        "Pagus founded",
        "Confluensis sponsors the vassal covenant of Pagus in a ruined Roman outpost near "
        "Cherbourg, overlooking the Channel. Its magi pour vis into restoring the Roman "
        "buildings and a dock.",
        "",
    ),
    (
        845,
        "Viking raids on the covenants",
        "As Norse fleets sack Paris and the coasts, covenants suffer with the monasteries. "
        "Confluensis, then at the Seine's mouth, is raided a dozen times in a hundred years "
        "and its magi grow skilled at battle magic; Pagus loses many vis sources and never "
        "recovers; the Diedne covenants of the Breton coast are struck too. Some raids are "
        "led by Gifted shapechangers using runes, and talk of a Norse 'Order of Odin' "
        "begins, much of it from Confluensis.",
        "",
    ),
    (
        851,
        "Baiocassium founded",
        "Baiocassium, a Diedne vassal of Branugurix, is founded in the forest near Bayeux. "
        "Its magi, heirs of Gaulish druids, stay on good terms with the local faeries.",
        "",
    ),
    (
        855,
        "Sinapis founded",
        "Sinapis is founded in Anjou, near the heart of France. It grows into an important "
        "liege covenant, head of a line of its own.",
        "",
    ),
    (
        865,
        "The Tribunals are drawn",
        "A stormy Grand Tribunal divides the Order into regional Tribunals, each free to "
        "make its own Peripheral Code, on House Mercere's argument that Redcaps should "
        "serve a region they know. The Tribunal of the West Franks is one of them. It "
        "takes in Gascony but neither Flanders nor Brittany: Brittany, independent since "
        "846 and steeped in Celtic and druidic tradition, goes to the Britannian Tribunal. "
        "The eastern lands fall to a new Lotharingian Tribunal.",
        "",
    ),
    (
        871,
        "Inaugural meeting of the Tribunal of the West Franks",
        "The first meeting gathers Confluensis, Pagus, Baiocassium, Bibracte and Sinapis. "
        "Fudarus and Branugurix attend the Britannian Tribunal instead.",
        "",
    ),
    (
        875,
        "Rotomagus founded",
        "The first generation of Sinapis's apprentices found Rotomagus near Rouen.",
        "",
    ),
    (
        885,
        "3rd meeting: Adela of Jerbiton acquitted",
        "Adela of Jerbiton, often at court, is charged with having been court wizard to "
        "King Louis III from 879 to 881. She blames a long feud with her accuser; nothing "
        "shows the Order was ever endangered by her friendship with the late king, and she "
        "is acquitted.",
        "",
    ),
    (
        892,
        "Rotomagus destroyed",
        "The Vikings sack Rouen and Rotomagus with it, less than a generation after its "
        "founding. Its one survivor leaves House Flambeau in shame for Ex Miscellanea.",
        "",
    ),
    (
        898,
        "The Lotharingian Tribunal dissolved",
        "Following the mundane partition of Lotharingia at Meersen in 870, the Rhine and "
        "West Frankish Tribunals had taken in its covenants, which welcomed the move. The "
        "seventh Grand Tribunal confirms it: the Lotharingian Tribunal ends, and its "
        "southern part becomes the Provençal Tribunal.",
        "",
    ),
    (
        899,
        "5th meeting: the Tribunal reaches the Rhine",
        "The West Franks vote to accept the Grand Tribunal's decision, take in part of the "
        "former Lotharingian lands and extend east to border the Rhine Tribunal.",
        "",
    ),
    (
        907,
        "Florum founded",
        "Florum is founded in Flanders, on the site Spider's Palace now holds. Like "
        "Confluensis it suffers several Viking raids in its early years.",
        "",
    ),
    (
        913,
        "Ligurio founded",
        "Fudarus sponsors Ligurio, a vassal on the border of Aquitaine and Brittany in the "
        "Vendée.",
        "",
    ),
    (
        920,
        "Kerguntuil founded",
        "Branugurix founds Kerguntuil on the Rose Coast of Brittany, by the stone said to "
        "be a petrified giant. Its magi study the Breton tales of giants, and its "
        "covenfolk grow larger than common folk.",
        "",
    ),
    (
        931,
        "Eighth Grand Tribunal",
        "The Order's eighth Grand Tribunal meets.",
        "",
    ),
    (
        936,
        "Baiocassium Minor founded",
        "Tired of Viking raids on their forest covenant, magi of Baiocassium make a spring "
        "sanctuary in a regio inside Bayeux. It becomes a covenant of its own, Baiocassium "
        "Minor, a vassal of Baiocassium.",
        "",
    ),
    (
        941,
        "Montverte founded",
        "Scandinavian converts to the Order found Montverte in Normandy. It becomes the "
        "head of one of the Tribunal's great lines.",
        "",
    ),
    (
        961,
        "The Betrayal of House Tytalus",
        "House Guernicus finds Prima Tasgillia corrupted by the Infernal and seizes her, "
        "and a large share of her House, far from Fudarus; she is executed for diabolism. "
        "Her filia Kalliste, the new Prima, refuses the Quaesitores and Flambeau hoplites "
        "entry to a covenant whose members have already been cleared, but is made to give "
        "way; the search finds nothing. The wounds between Tytalus and Flambeau last for "
        "a century.",
        "",
    ),
    (
        964,
        "Ninth Grand Tribunal",
        "The Order's ninth Grand Tribunal meets.",
        "",
    ),
    (
        969,
        "Bibracte sacked by Montverte",
        "Bibracte had revived a cult of Vercingetorix and turned against all things Roman, "
        "banning Latin for Brythonic and then refusing to deal with magi of the 'Roman' "
        "Houses. With Fudarus weakened after the Betrayal, four Flambeau and Tremere magi "
        "of Montverte declare Wizard's War on its magi at once, charging them with "
        "devil-worship, and destroy the covenant.",
        "",
    ),
    (
        981,
        "Caput Capra founded",
        "Branugurix founds its youngest and easternmost vassal, Caput Capra, on the Loire "
        "near Fleury, to guard the old druidic site there from the lawlessness of the age.",
        "",
    ),
    (
        983,
        "17th meeting: the Normandy Tribunal",
        "With the Duke of Normandy foremost in the Tribunal's lands and the Franks fading "
        "as a people, the Tribunal adopts the proposal of Adrianus of Montverte and renames "
        "itself the Normandy Tribunal.",
        "",
    ),
    (
        997,
        "Tenth Grand Tribunal",
        "The Order's tenth Grand Tribunal meets.",
        "",
    ),
    (
        998,
        "Aedes Salii founded",
        "Sinapis founds Aedes Salii on Jersey, named for the priests of Mars, as a base to "
        "coordinate the coming war in Normandy and the Stonehenge Tribunal.",
        "",
    ),
    (
        1004,
        "The Schism War declared",
        "War is declared on House Diedne. Some of its worst battles are fought in Normandy "
        "and Brittany, and for a long while the Diedne have the upper hand. A Diedne force "
        "comes by sea to Fudarus, cannot break in and besieges it for months with three "
        "great summoned spirits, until Primus Klynoites wrests the spirits from them, "
        "destroys the besiegers and binds the spirits into the covenant's walls.",
        "",
    ),
    (
        1005,
        "Caput Capra and Baiocassium Minor destroyed",
        "Caput Capra is the war's first casualty in the Tribunal; Confluensis still brings "
        "its apprentices to the scant ruins for their history lessons. Baiocassium Minor "
        "falls the same year.",
        "",
    ),
    (
        1007,
        "Kerguntuil destroyed",
        "The Diedne covenant on the Rose Coast is wiped out.",
        "Rumour says a Quaesitor later steered the Templars into building their chapel at "
        "Lanleff, to cleanse the district of the Diedne's supposed diabolic taint.",
    ),
    (
        1008,
        "Pagus destroyed",
        "Pagus, never recovered from the Viking raids, is destroyed by the magi of "
        "Baiocassium.",
        "",
    ),
    (
        1011,
        "Baiocassium and Ligurio destroyed",
        "Baiocassium falls to the Order. Ligurio, Fudarus's vassal in the Vendée, is "
        "crushed by giants hurling great boulders, thought to have been sent by "
        "Kerguntuil's magi before their end.",
        "",
    ),
    (
        1012,
        "The Tempest: Branugurix falls",
        "The war's last battle is fought at Branugurix. In its final moments the Diedne "
        "Primus somehow seals every entrance to the regio, and some of the Flambeau and "
        "Tremere attackers are never seen again. Diedne history and alleged crimes are "
        "later struck from the Tribunal's records, and House Guernicus guards the site's "
        "secrets.",
        "Guernicus's records hold the regio's exact location and the old way in. Rumour "
        "has it that some Diedne survive inside, and that someone is working to free them; "
        "the Quaesitores watch anyone who lingers around Mount Dol.",
    ),
    (
        1018,
        "22nd meeting: Brittany joins; the spoils",
        "The Schism War over, the Quaesitores list the vis sources and books taken from "
        "the fallen covenants. Fudarus, the only Breton covenant left, comes to the Normandy "
        "Tribunal, which claims Brittany and its magical wealth. Pertheus of Tytalus wins "
        "the victors the right of conquest over the spoils, on condition that a contest be "
        "held in seven years to share them out again. The old Tytalus-Flambeau quarrel "
        "flares over the spoils.",
        "",
    ),
    (
        1020,
        "Orchard of Sour Apples founded",
        "Confluensis sponsors a new vassal after the war, the Orchard of Sour Apples, on "
        "the Cotentin peninsula.",
        "",
    ),
    (
        1021,
        "Lixivia founded",
        "Florum founds Lixivia in Champagne as the great fairs begin, a covenant of Redcaps "
        "and Gentle Gifted magi meant to broker trade between the Order and merchants and "
        "fetch whatever any covenant wanted.",
        "",
    ),
    (
        1025,
        "23rd meeting: the Perthean Compact",
        "With Northern Tytali and Southern Flambeau close to open war over the Diedne "
        "spoils, the Quaesitores back Pertheus of Tytalus, whose statutes pass over this and "
        "the next two meetings. Contested vis becomes the Tribunal's, competed for every "
        "seven years, and magi gain set rights over the vis near their covenants with a "
        "way to win more as they grow. The Compact is refined at later meetings. Three "
        "Flambeau-led covenants of the south call it a Tytalan swindle and go over to the "
        "Provençal Tribunal.",
        "",
    ),
    (
        1028,
        "Oleron founded",
        "Oleron is founded on its island off Aquitaine. It becomes the head of one of the "
        "Tribunal's great lines.",
        "",
    ),
    (
        1030,
        "Eleventh Grand Tribunal",
        "The Order's eleventh Grand Tribunal meets.",
        "",
    ),
    (
        1048,
        "Vexatores founded",
        "Fudarus founds Vexatores purely to goad Sinapis, twenty-one miles north of it, "
        "the least distance the law allows, on a vis source taken from the Diedne.",
        "",
    ),
    (
        1051,
        "Confluensis moves; Dragon's Rest founded",
        "Confluensis moves to the Orchard of Sour Apples on the Cotentin, whose magi join "
        "their liege as the vassal covenant is wound up. Dragon's Rest is founded as a "
        "vassal of Confluensis on its old site at the Seine's mouth. By about this time the "
        "Tribunal has its modern borders.",
        "",
    ),
    (
        1063,
        "Twelfth Grand Tribunal: Flambeau withdraws",
        "The feud of Tytalus and Flambeau formally ends with House Flambeau withdrawing "
        "from all hostilities. Sinapis is abandoned as its members leave for Provence and "
        "Iberia, ending its line; Aedes Salii, left to the Flambeau after the Tremere went "
        "home, is disbanded, and two of its magi help found Lapis Crudus, a covenant shared "
        "by the two Houses and counted in the line of Sinapis.",
        "",
    ),
    (
        1064,
        "Vexatores abandoned",
        "Never meant to last, Vexatores is abandoned once the quarrel it was built to "
        "serve is over.",
        "",
    ),
    (
        1072,
        "Nauche-Fleur founded",
        "Montverte sponsors Nauche-Fleur near Niort in Aquitaine, a covenant that keeps a "
        "school of arms and letters whose fees pay for its magi's lavish living.",
        "",
    ),
    (
        1081,
        "The Library of the Tribunal begun",
        "Perpauca of Bonisagus, whose own covenant kept her great books from visitors, "
        "starts giving books to the Tribunal as a whole. Hers are declared the first books "
        "of the Library of the Normandy Tribunal, kept at Confluensis, and the right to "
        "read them becomes a prize of the Tourney. Other authors follow her lead.",
        "",
    ),
    (
        1095,
        "33rd meeting: Nauche-Fleur acquitted",
        "Nauche-Fleur is accused of swearing fealty to its local baron. The magi answer "
        "that the oath was taken by an unGifted companion standing as lord of the manor in "
        "their name, and the Tribunal finds them innocent.",
        "",
    ),
    (
        1096,
        "Thirteenth Grand Tribunal",
        "The Order's thirteenth Grand Tribunal meets.",
        "",
    ),
    (
        1099,
        "Infelicitas founded",
        "Rancrax of Tytalus loses a wager to his rival and, under its terms, must leave "
        "Fudarus; he founds Infelicitas as a vassal of Fudarus.",
        "",
    ),
    (
        1100,
        "Nidi founded",
        "Conventio Nidi is founded as a vassal of Oleron.",
        "",
    ),
    (
        1102,
        "34th meeting: the language border",
        "At the request of three Provençal Flambeau, the Tribunal rules that, without any "
        "clear natural frontier, disputed ground belongs to Normandy if the nearest "
        "settlement speaks the langue d'oeil and to Provençal if it speaks the langue d'oc.",
        "",
    ),
    (
        1109,
        "35th meeting: the Donatores join the Order",
        "In Picardy Quaesitor Muirgheal finds hedge wizards fighting a plague of restless "
        "dead. Once the dead are laid, many of them are taken into the Order as the "
        "Donatores Requietis Aeternae, a tradition of House Ex Miscellanea.",
        "",
    ),
    (
        1116,
        "36th meeting: mundane raiding; Praecepsus cleared",
        "Building on an earlier ruling on mundane resources, Quaesitor Lothaire holds that "
        "raiding a covenant's mundane resources is allowed. At the same meeting Praecepsus "
        "of Flambeau, accused of wielding a Perdo-enchanted sword for the king when the "
        "count of Meulan raided Paris in 1111, is cleared: nothing showed magic to mundane "
        "eyes, so there is no case to answer.",
        "",
    ),
    (
        1117,
        "Florum moves; Spider's Palace founded",
        "Florum leaves its first site, and Spider's Palace is founded there as its vassal.",
        "",
    ),
    (
        1118,
        "Lapis Crudus lost",
        "Lapis Crudus becomes trapped in its own regio and is given up for lost.",
        "",
    ),
    (
        1123,
        "37th meeting: Pandion and the Redcap's horses",
        "Pandion of Flambeau is found guilty of taking twelve horses, one a magical "
        "beast, from Antonin of Dragon's Rest, a Redcap, and so lessening his magical "
        "power. He must return that one and pay ten pawns, but keeps the other eleven as "
        "spoils of a lawful raid. Enchanted creatures, familiars or not, count toward a "
        "magus's power and ordinary livestock does not; Quaesitor Lothaire later adds that "
        "covenfolk do not count either. The same year the Donatores found Requies Aeterna "
        "as a vassal of Florum.",
        "",
    ),
    (
        1124,
        "Lixivia disbanded; Alcuin's Auberge founded",
        "Distrusted by magi who doubted its motives, Lixivia became everyone's favourite "
        "target for raids and is driven into poverty and disbanded. Its Redcaps found "
        "Alcuin's Auberge, a small Mercer House in Tours, as a vassal of Florum.",
        "",
    ),
    (
        1129,
        "Fourteenth Grand Tribunal: the border upheld",
        "Despite Provençal protests, the Grand Tribunal upholds Normandy's ruling that "
        "language marks the border between the two Tribunals.",
        "",
    ),
    (
        1130,
        "38th meeting: Jacinth of Oleron convicted",
        "Raiding Infelicitas, Jacinth of Oleron brought down its upper storey and wrecked "
        "two laboratories. The charge of trying to kill a magus by destroying the covenant "
        "is not proved, but he is convicted of deprivation. Quaesitor Lothaire rules that "
        "raiders may never damage a covenant's buildings and that a lawful raid does not "
        "excuse a breach of the Code. Jacinth escapes a March but loses his familiar.",
        "",
    ),
    (
        1136,
        "Moles Magna founded",
        "Oleron sponsors Moles Magna on the edge of the Morvan, a covenant built inside a "
        "dam across a small tributary of the Yonne, hidden behind its own waterfall.",
        "",
    ),
    (
        1144,
        "40th meeting: Lothaire accused",
        "Jacinth of Oleron accuses Quaesitor Lothaire of partisanship, naming raids by "
        "Montverte, Fudarus and their allies from which he profited. An inquiry clears him "
        "for want of substance, but he never regains his place as chief Quaesitor of "
        "Normandy and is invited to Magvillus in honour of his long service.",
        "",
    ),
    (
        1158,
        "Infelicitas abandoned",
        "Rancrax is killed in Wizard's War by a magus of Moles Magna, and the two magi "
        "left at Infelicitas have no wish to stay.",
        "",
    ),
    (
        1162,
        "Fifteenth Grand Tribunal",
        "The Order's fifteenth Grand Tribunal meets.",
        "",
    ),
    (
        1166,
        "Nauche-Fleur ends",
        "Its mundane dealings always controversial, Nauche-Fleur kept none of the "
        "apprentices it trained, and it dies when the last of its founders enters Final "
        "Twilight.",
        "",
    ),
    (
        1172,
        "44th meeting: Fudarus loses a legacy",
        "Atlax of Tytalus is charged with stealing and reading the messages the Redcap "
        "Camille carried while a guest at Fudarus. Quaesitor Whent holds the covenant "
        "answerable for its magus, strips Fudarus of the lease of a legacy and gives it to "
        "House Mercere.",
        "",
    ),
    (
        1179,
        "45th meeting: Pernix acquitted, Camille fined",
        "Pernix of Merinita, accused by Visurgis of Tytalus of interfering with mundanes "
        "for healing a young noble thrown from his horse, is acquitted: only the noble and "
        "the abbot, prior and infirmarian of a friendly monastery knew. Camille of Mercere, "
        "accused by Buliste of Tytalus of using a local knight to gather the vis of one of "
        "his legacies, is convicted after the knight confessed to doing the devil's work "
        "and Atlax of Fudarus had to avert the ruin; Camille pays fifteen pawns to Fudarus "
        "and the source is closed for thirty years or more.",
        "",
    ),
    (
        1182,
        "Moles Magna destroyed",
        "After heavy rain the river bursts the dam that housed Moles Magna and the "
        "covenant is swept away. Since its magi had magically strengthened the dam against "
        "exactly that, most think they angered some power of the river they held back.",
        "",
    ),
    (
        1187,
        "Atsingani founded",
        "Atsingani is founded in Anjou as a vassal of Montverte.",
        "",
    ),
    (
        1192,
        "Cunfin founded",
        "Cunfin is founded in Champagne as a vassal of Confluensis.",
        "",
    ),
    (
        1195,
        "Sixteenth Grand Tribunal; Harpax made Primus",
        "The Order's sixteenth Grand Tribunal meets. About this time Prima Buliste of House "
        "Tytalus falls into a Twilight so deep she is taken for dead, and her rival "
        "Harpax, her fellow apprentice, is chosen as Primus and takes the Rod of the Primus "
        "from her sanctum.",
        "",
    ),
    (
        1197,
        "Alcuin's Auberge falls",
        "The Mercer House in Tours falls to raiders no one has identified.",
        "",
    ),
    (
        1200,
        "Two Primi of Tytalus; Atramentum founded",
        "Buliste returns from Twilight, still wearing the Circlet of the Primus, and she "
        "and Harpax begin their struggle for the House; both are honoured as Primus and "
        "both rule Fudarus. Just as their battle begins, Fudarus sponsors the young vassal "
        "covenant of Atramentum.",
        "Cynics hold that Atramentum's founders were duped into readying the site for the "
        "magi who would soon take it.",
    ),
    (
        1201,
        "Exspectatio takes Atramentum's site",
        "The other magi of Fudarus leave the two Primi to their quarrel and settle at "
        "Atramentum, ousting its young magi and renaming it Exspectatio, still counting "
        "themselves members of Fudarus. Atramentum's founders form Atramentum Renatus, a "
        "vassal of Exspectatio, in Champagne.",
        "",
    ),
    (
        1204,
        "Eboris founded",
        "The covenant of Eboris is founded in Paris.",
        "",
    ),
    (
        1207,
        "49th meeting: Pugnatis expelled",
        "The previous meeting convicted Pugnatis of controlling the mayor of Laval by "
        "magic to reach a vis source, and fined her a number of enchanted items. Neither "
        "she nor the items appear at this meeting, and she is cast out of the Order. "
        "Proctor of Guernicus presides, as he does again in 1214.",
        "",
    ),
    (
        1215,
        "Lapis Crudus returns",
        "After nearly a century trapped in its regio, Lapis Crudus wins a kind of freedom "
        "and comes back into Hermetic affairs, reminding the Tribunal that the Diedne may "
        "still be waiting in theirs.",
        "",
    ),
    (
        1219,
        "Death of Renita, the Praeco",
        "Renita of Bjornaer, Praeco of the Tribunal and leader of Confluensis, dies in the "
        "winter. Proctor, the Presiding Quaesitor, takes charge of Confluensis; who will be "
        "the next Praeco is open. Stellatus, the next eldest, has left for Iberia, leaving "
        "Celeres of Cunfin first in line.",
        "",
    ),
)

#: The mundane history of Mythic France, era by era, for the Tribunal's
#: History.
ERAS: tuple[tuple[str, str], ...] = (
    (
        "Ancient Gaul",
        "The Gauls who once held these lands sacrificed to the mighty spirits and faeries "
        "of the country, revered the boar as the beast of their tribal kings, and followed "
        "druids who may have been forerunners of House Diedne. Julius Caesar conquered "
        "them between 58 and 50 BC, beating Vercingetorix at Alesia, and wrote his "
        "commentaries on the war. Rome's rule reached as far as Brittany and its ruins "
        "still dot the land. Many druids withdrew into the wilds, the Gauls kept their own "
        "gods beside Rome's, and a prosperous Gallo-Roman culture grew up around the great "
        "capital of Lugdunum.",
    ),
    (
        "The saints of Gaul",
        "Christianity reached Paris about 250 with Denis and his companions Eleutherius "
        "and Rusticus, who won many converts until the governor imprisoned them; after "
        "years in a dungeon they were beheaded on Montmartre in 275 and thrown into the "
        "Seine. The abbey of Saint-Denis honours them, and Denis is the king's own patron "
        "and a patron of France and of Paris. St Martin, who shared his cloak with a "
        "freezing beggar in 337, became bishop of Tours in 371 and died in 397. When the "
        "Huns came in 450 St Geneviève's prayers turned them from Paris, and in 464 she "
        "broke Childeric's siege of the city by leading boats down the Seine at night "
        "with food. In 451 Romans, Franks and Visigoths under the legendary Merovech "
        "defeated Attila at Châlons and ended his push west. In the fifth and sixth "
        "centuries Britons fleeing the fall of Arthur's kingdom and the Saxon raids "
        "settled Armorica, which became Brittany, with its own tongue and culture.",
    ),
    (
        "The Merovingian Franks",
        "The Franks, first settled as Rome's treaty allies, rose under Merovech, said to "
        "be the child of a Frankish queen and a sea-beast like the Quinotaur, and his son "
        "Childeric. Clovis, king from 481 to 511, beat the governor Syagrius in 486 and "
        "built an empire by war, guile and marriage. His Christian wife Clotilde's prayers "
        "healed their son, and when he vowed to give up Mercury and Jupiter for victory "
        "over the Alemanni in 496 and won, St Rémi baptised him at Reims; a dove brought "
        "the holy oil from Heaven, and that never-emptying ampoule has anointed every king "
        "since. By 507 he had beaten Romans, Burgundians and Visigoths and ruled from Paris. "
        "The long-haired Merovingian kings were held to be sorcerers. After Clovis the "
        "kingdom was split among his sons and wracked by civil war; Chlotar II reunited it "
        "in 613 and Dagobert I briefly ruled it all, but the mayors of the palace grew "
        "until, by 687, Pepin of Herstal ruled in all but name. Gregory, bishop of Tours "
        "from 573, wrote the history of the Franks that tells these tales. In 732 Charles "
        "Martel turned back a Muslim army near Tours and Poitiers, and in 751 his son "
        "Pepin the Short took the crown and sent the last Merovingian, shorn of his "
        "magical hair, to a monastery. Legend says other heirs of the blood escaped.",
    ),
    (
        "The Carolingians",
        "The new dynasty sought the Church's backing: the abbot of Saint-Denis supported "
        "it, and in 754 Pope Stephen II threatened excommunication on anyone who made a "
        "Frankish king of any other line. Charlemagne, king from 768, conquered Lombardy, "
        "founded the kingdom of Aquitaine in 778, set up schools with the help of the "
        "scholar Alcuin, and was crowned emperor in Rome in 800. Tales of him and his "
        "paladins, Roland at Roncesvalles above all, are sung by every minstrel of 1220. "
        "His empire did not outlast him long: his grandsons fought for four years and "
        "divided it at Verdun in 843, Brittany won its independence from Charles the Bald "
        "in 846, and after Charles the Fat briefly reunited the empire it broke apart in "
        "887. Kings of the old line and of rival houses followed one another amid feuding "
        "nobles.",
    ),
    (
        "The Northmen",
        "Viking raids on Breton monasteries began in the late eighth century. In 845 a "
        "hundred and twenty longships rowed up the Seine and extorted seven thousand pounds "
        "from Paris; monkish chroniclers saw the hand of God punishing the civil wars that "
        "followed Louis the Pious's death. Aquitaine was nearly ruined, Paris was besieged "
        "again in 885, and Count Odo's defence of it won him the crown in 888. The Norse "
        "wintered in Neustria until in 911 Charles the Simple granted Rouen, Lisieux and "
        "Évreux to their leader Rollo, who was baptised, married the king's daughter and "
        "was meant to hold off his kin. Instead his line drew in more settlers and seized "
        "more land, and the Land of the Northmen became Normandy. Monasteries learned to "
        "carry their relics and books inland each spring. In 1066 Duke William conquered "
        "England.",
    ),
    (
        "The Capetians",
        "Hugh Capet, descended from Robert the Strong, became king in 987 with the help of "
        "the scholar Gerbert of Aurillac, reputed to have some small magic, whom he made "
        "archbishop of Reims, and he made Paris his capital. Pope Stephen's ban hung over "
        "him until he recovered the relics of St Valéry and St Riquier, earning his line "
        "seven generations on the throne, of which Philip Augustus is the last so far. His successors "
        "were weak kings among strong vassals: Robert the Pious, Henry I, who saw the "
        "emperor crush Odo of Champagne at Bar in 1037, Philip I, and Louis VI, crowned at "
        "Orléans in 1108 because he could not reach Reims. Meanwhile the Church grew in "
        "strength: Cluny was founded in 910, Cîteaux in 1098 and St Bernard's Clairvaux in "
        "1115, the First Crusade set out in 1096, Abélard came to Paris in 1118, and work "
        "on Notre-Dame began in 1163. In 1134 a great flood reshaped the Flemish coast and "
        "gave Bruges back its way to the sea.",
    ),
    (
        "The Lions and the Lily",
        "In 1137 the young Louis VII married Eleanor, heiress of Aquitaine, Gascony and "
        "Poitou. The match soured: the monkish king and his worldly southern queen fell "
        "out on the Second Crusade, which St Bernard preached, amid rumours of her affair "
        "with her uncle Raymond of Antioch, and the marriage was annulled. Eleanor at once "
        "wed Henry of Anjou, son of Geoffrey V, who had married Matilda of England in 1127 "
        "and conquered Normandy in 1144. Henry inherited Normandy in 1151, married Eleanor "
        "in 1152 without his lord's leave and became King of England in 1154, master of "
        "half of France, and later took Brittany too. The Angevin lion seemed ready to "
        "maul the Capetian lily, but Henry's sons, egged on by their mother, rebelled "
        "against him again and again with French help, Eleanor was kept in comfortable "
        "captivity, and the barons of Aquitaine rose whenever they could. The Angevins "
        "boasted of descent from Melusine, a faerie or demon bride who could not abide the "
        "Mass.",
    ),
    (
        "Philip Augustus and Richard",
        "Philip, son of Louis VII and Adèle of Champagne, was crowned in 1179 after his "
        "father's pilgrimage to Becket's shrine saved him from a grave illness, and ruled "
        "alone from 1180: clever, combative and devoted to administration, he favoured "
        "clerks and lawyers over the old nobility. Henry the Young King died in 1183 and "
        "Geoffrey of Brittany in 1186, and in 1189 Richard, with Philip's help, beat his "
        "father and took England, Normandy and Anjou. Both kings went on the Third "
        "Crusade, but Philip came home after Acre, to whispers of cowardice, and built the "
        "Louvre. Returning, Richard was taken by Leopold of Austria, whom he had insulted, "
        "and handed to the emperor; Philip and Richard's brother John offered money to "
        "keep him jailed, but Eleanor paid his ransom in 1194. Richard then beat Philip at "
        "Fréteval and at Gisors in 1198, where the French king had to be fished out of a "
        "river, and built great castles such as Château Gaillard. In 1199 he died of a "
        "crossbow wound while besieging Châlus over a buried hoard, and on his deathbed "
        "named John, not his nephew Arthur of Brittany, as heir.",
    ),
    (
        "The fall of Angevin France",
        "John seized and married Isabella of Angoulême, already promised to Hugh de "
        "Lusignan, and seemed spellbound by her while his vassals rebelled. Summoned to "
        "Philip's court in 1202 he did not come, and Philip declared his French lands "
        "forfeit and backed Arthur of Brittany. John roused himself to rescue his mother "
        "at Mirebeau and capture Arthur, who vanished at Rouen in 1203, almost surely "
        "murdered, by John's own hand it is said, driving many vassals over to Philip. "
        "Eleanor died in 1204, Château Gaillard fell and Normandy with it, and Poitou "
        "followed in 1205. England was laid under interdict, and John, allied with the "
        "emperor, was crushed at Bouvines in 1214. His barons forced Magna Carta on him "
        "in 1215 and rebelled again in 1216; Prince Louis invaded England, but John's "
        "death that year rallied the barons behind the boy Henry III, now ruled for by a "
        "regency council.",
    ),
    (
        "France in 1220",
        "Philip has made the University of Paris a chartered body (1200) and fortified "
        "his capital; Chartres is rebuilding after its great fire of 1194, and the pope "
        "banned the teaching of law in Paris in 1219. The Tribunal's lands are at peace, "
        "though still split between French and Angevin lords, and the Angevins are no "
        "longer feared. Philip has not yet anointed his heir Louis, born in 1187 to "
        "Isabella of Hainault; he also has a daughter Mary and a son Philip by Agnès of "
        "Méranie. Many northern knights and mercenaries have fought in the Albigensian "
        "Crusade against the Cathars of the Langue d'oc since 1209, Philip letting his "
        "nobles go without leading them. In 1212 a shepherd boy of Châteaudun worked "
        "miracles at Saint-Denis and set the Children's Crusade moving, and the Fifth "
        "Crusade left in 1217. Magi of Normandy tend to frown on those who dig too deep "
        "into the past, and the Quaesitores watch anyone curious about the Schism War.",
    ),
)

#: What the timeline foretells after 1220, for a saga that follows real
#: history, with the book's hints at what lies behind the crown.
FUTURE = (
    "If the saga follows real history: Frederick II is crowned emperor in 1220. Louis "
    "VIII becomes king in 1223, and his son Louis IX, the future St Louis, in 1226. The "
    "seventeenth Grand Tribunal meets in 1228, the year of the Sixth Crusade and a papal "
    "ban on teaching Aristotle at Paris. The Albigensian Crusade ends in 1229. Orléans's "
    "cathedral school becomes a university in 1235 and Angers gains one in 1250. The "
    "Seventh Crusade runs from 1248 to 1254, and the Treaty of Corbeil settles France's "
    "claims against Aragon in 1258. The eighteenth Grand Tribunal meets in 1261, when a "
    "Troyes cobbler's son becomes Pope Urban IV; France takes a single coinage in 1263, "
    "and Guido le Gros of Saint-Gilles becomes Clement IV in 1265. The Eighth Crusade "
    "sails in 1270 and Philip III takes the throne. Simon de Brie of Touraine becomes "
    "Martin IV in 1281, Philip IV the Fair is crowned in 1285, the nineteenth Grand "
    "Tribunal meets in 1294, and Louis IX is made a saint in 1297. The Tribunal next "
    "meets in 1221, then 1227 (moved a year for the Grand Tribunal), 1235 and every "
    "seven years after.\n\n"
    "The seven generations granted to Hugh Capet's line end with Philip Augustus, so "
    "some sudden change of dynasty is due at his death. The Royal Touch that cures "
    "scrofula comes from the holy oil, not from Merovech's blood; most Merovingian heirs "
    "carry a hidden immunity to drowning and a red cross birthmark. And Arthur of "
    "Brittany may not be dead: if he had the Gift and was hidden away in a late "
    "apprenticeship, his memory altered by Mentem, he would only now have passed his "
    "Gauntlet, unaware of his birthright."
)


def build(normandy: Normandy) -> None:
    """Enter every event of `EVENTS` in the Tribunal's Diary, and add the
    mundane history, by era, to the Tribunal's History, with the future
    under Secrets. Nothing is written when the Tribunal has not been made
    yet (the parts build in order, this one after the Tribunal's)."""
    tribunal = normandy.tribunal
    if tribunal is None:
        return
    for year, title, details, hidden in sorted(EVENTS, key=lambda e: e[0]):
        normandy.b.event(tribunal, year, title, secrets(details, hidden))
    eras = paragraphs(*(f"{title}. {text}" for title, text in ERAS))
    # Any history already written keeps its place, its secrets ahead of ours.
    tribunal.history = paragraphs(tribunal.history, eras)
    tribunal.secrets = as_secrets(paragraphs(secret_words(tribunal.secrets), FUTURE))
