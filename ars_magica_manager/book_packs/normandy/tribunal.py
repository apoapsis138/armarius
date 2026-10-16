"""The Normandy Tribunal itself: the record and its summary, the
Peripheral Code (the Perthean Compact, the rulings on towns and mundane
resources, the founding of covenants, the meeting by lot and the
Hermetic Tourney), the vis the Tribunal holds in common, every fallen
covenant the book names as a ruined place, and the docket (build); then
the officers and the five great lines of fealty (finish, once the
covenants and magi the other parts make exist)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import vassals
from ...tribunal_packages.normandy import KEY
from ..builder import paragraphs, secrets

if TYPE_CHECKING:
    from ...models import Covenant
    from . import Normandy

NAME = "The Normandy Tribunal"

SUMMARY = paragraphs(
    "The old Tribunal of the West Franks, renamed for the Norman duchy in "
    "983, covers the French-speaking north of France: from the Atlantic "
    "east some four hundred miles to the edge of Lorraine and the Saône, "
    "where the lands owing fealty to the Emperor begin, and from the "
    "Channel south as far as the Dordogne, where its border with Provençal "
    "has been settled by language since 1102 (a place belongs to Normandy "
    "if its nearest settlement speaks the langue d'oïl). It takes in "
    "Brittany, claimed after the Schism War, and Flanders, but not imperial "
    "Lorraine or Arelat; the Massif Central at its south-eastern corner is "
    "uncertain ground that no covenant presently quarrels over.",
    "It is a land of crowded fields, great cities, cathedrals and castles, "
    "and the Dominion presses hard on the magi. Vis is scarce, and the "
    "rules for sharing it out (the Perthean Compact) shape everything: "
    "covenants are easy to found and hard to keep, so Normandy has perhaps "
    "more covenants than any other Tribunal but only a little over a "
    "hundred magi, most covenants holding about four. Three in four "
    "covenants are a liege, a vassal or both, bound by oaths of fealty "
    "copied from the feudal world around them, and five great lines rule "
    "its politics: Fudarus (the Domus Magna of House Tytalus, on its "
    "island off Brittany), Confluensis (the Quaesitores' covenant in the "
    "Cotentin), Florum in Flanders, Oleron in Aquitaine and Montverte in "
    "Normandy. A few eremites and the odd coenobium live outside the "
    "covenants. The countryside is strewn with the ruins of covenants that "
    "failed, and young ones keep rising in their place.",
    "Its magi are hard and competitive by other Tribunals' standards. "
    "Raiding a rival covenant's mundane supplies is lawful here; meddling "
    "with mundanes is only a crime once mundane reprisals actually fall on "
    "magi, so covenants work through mundane 'masks'; and the Tytalan "
    "spirit of contest runs through its customs. Young magi go errant like "
    "knights, far beyond the Tribunal, to win vis and a name before "
    "settling down. Old fears linger too: the Order of Odin from the "
    "Viking raids, and House Diedne, whose records the Guernicus censors "
    "cut from the archives and whose sealed Domus Magna, Branugurix, may "
    "not be empty. Regional quarrels between Breton, Norman, Parisian and "
    "Aquitanian grogs have even come to blows at Tribunal, and a few magi "
    "still follow Metrodorus's discredited belief that Mythic Blood makes "
    "an aristocracy of magi.",
    "The Tribunal meets every seven years, and since the Schism War the "
    "host is drawn by lot from the covenants rather than being the "
    "Praeco's home, so the next meeting's place is not yet known. Even a "
    "new Spring covenant may draw it, and must then provide a secluded "
    "ground for the Tourney, an excellent Aegis and lavish hospitality, "
    "while crowds of Quaesitores use the preparations as cover to look "
    "into its affairs; hosting can ruin a young covenant, which usually "
    "borrows from its liege or another great covenant, though many guests "
    "bring a pawn of vis or a Lab Text as a gift. Business comes first, "
    "then the Hermetic Tourney, where covenant teams compete for the "
    "Tribunal's vis sources and books for the next seven years.",
    "The next meeting is in 1221. Renita of Bjornaer, Praeco and leader of "
    "Confluensis, died last winter, and the post stands vacant: by custom "
    "the eldest magus succeeds, but her sept-mate Stellatus, the eldest, "
    "has gone to Iberia, leaving Celeres of Cunfin, then Somnifer of Lapis "
    "Crudus, then Geirlaug of Montverte. Proctor of Guernicus, Presiding "
    "Quaesitor these two meetings and now acting head of Confluensis, "
    "holds the Tribunal together with the two Jerbiton, Jerome of "
    "Confluensis (its envoy to the nobility) and Eloi of Cunfin (its link "
    "to the Church). Library books won at the Tourney and the list of the "
    "Tribunal's luctationes are kept at Confluensis.",
)

SECRET = (
    "The Cabal of the Golden Coin, begun by Tytalus magi and now drawn "
    "from many Houses, fixes Tourney events between its members and "
    "pushed through several of the odd prize levels to profit by them; "
    "the young three-magus team that has finished 14th at the last three "
    "Tourneys, just past the prizeless Siege of Shame, is one of its "
    "fronts. The Siege of Notatus's large prize may have a more practical "
    "origin than the tale of Notatus's love of seven, buried in the "
    "Tribunal's records. Three Normandy covenants back the Lotharingian "
    "movement, which would take some of the Tribunal's richest vis "
    "sources away and leave Tytalan Brittany producing more vis than the "
    "rest combined; a Tytalan Cabal of Frankish Gold works for it, with "
    "Augustina the Traitor among its members and at least one saboteur "
    "inside. Proctor's inherited hatred of House Tytalus may yet drive "
    "him to extremes. Rumour that Diedne survivors wait inside "
    "Branugurix's sealed regio, and that someone means to free them, may "
    "be true."
)


#: The duties of the Oath of Fealty a vassal covenant swears, and how it
#: breaks free, in summary.
OATH = paragraphs(
    "Service owed by the vassal: at each Tribunal its magi hand some or "
    "all of their sigils to the liege's representative as free proxies, "
    "or vote as the liege directs on a set number of questions; it pays a "
    "tithe of vis at agreed intervals (often of a given Art); it spends "
    "seasons copying or writing books for the liege's library; and it "
    "may be bound to harvest one of the liege's legacies each year.",
    "Protection owed by the liege: it never backs a motion at Tribunal "
    "that harms its vassal, and backs any that helps it unless it can "
    "show the harm to itself; it answers a set number of calls for aid "
    "every seven years (though not at the cost of a season or its own "
    "vis); it may gift the vassal a vis source, books or enchantments; "
    "and it lets the vassal spend seasons copying from its library, the "
    "copies protected by a Cow and Calf agreement.",
    "The oath is part of the Peripheral Code and enforceable at "
    "Tribunal. It ends by agreement of both sides, or after one side "
    "successfully prosecutes the other for defaulting on it, which is a "
    "Low Crime: a liege that breaks faith can be made to pay damages, "
    "and either side may then cancel the oath; a vassal that wants to go "
    "refuses a duty and lets itself be convicted and fined. A vassal that "
    "breaks away usually makes enemies of its old liege and that liege's "
    "other vassals.",
)


def build(normandy: Normandy) -> None:
    b = normandy.b
    normandy.tribunal = tribunal = b.tribunal(
        NAME,
        package=KEY,
        summary=secrets(SUMMARY, SECRET),
        meets_every=7,
        next_year=1221,
        next_season="Spring",
        meeting_place="",
    )
    for year, title, says in RULINGS:
        b.ruling(tribunal, title, year, says)
    _vis(normandy)
    _ruins(normandy)
    _docket(normandy)


# -- the Peripheral Code --

#: The Peripheral Code: (year or None, title, what it says).
RULINGS: tuple[tuple[int | None, str, str], ...] = (
    (
        1025,
        "The Perthean Compact: seisins",
        "Every vis source belongs to a covenant, never to a magus. A source "
        "within a day's return march of an established covenant is its "
        "seisin, harvested by it alone. Since 1109 the test is exact: a man "
        "on foot, with no magic, must go from the covenant's council chamber "
        "to the source and back between sunrise and sunset on a day within a "
        "month of an equinox. Covenants keep trained runners (cursores) to "
        "prove it before the Quaesitores (a fit man covers about 10 + twice "
        "his Athletics miles a day cross country, five fewer in wild country "
        "and five more on good roads). An unchallenged claim stands; roads "
        "built, forests cleared and even a hill moved have stretched the "
        "march, and rivals have done the reverse.",
    ),
    (
        1025,
        "The Perthean Compact: legacies",
        "A source too far away to be a seisin may be voted the discoverer's "
        "legacy: exclusive harvest for seven years. Since 1032 the lease must "
        "be renewed by vote at each meeting, and fewer than half the "
        "renewals succeed; a source refused becomes a tropaeum. A new find "
        "is usually granted without contest, and a legacy may last for many "
        "terms when only its holders can reach it. Harvesting another's "
        "legacy is the High Crime of depriving a magus of his power, though "
        "pleas for mercy are nearly always granted. The holder may grant the "
        "harvest to whom it likes, including new magi settling within a "
        "day's march, which is how most covenants are founded.",
    ),
    (
        1032,
        "The Perthean Compact: tropaea",
        "Known sources that are neither seisins nor legacies, and need "
        "little effort to harvest, are tropaea, owned by the Tribunal in "
        "common and leased for seven years as prizes at the Tourney, with "
        "the same exclusive harvest as a legacy. A covenant that would "
        "settle within a day's march of one needs the Tribunal's vote, and "
        "if it wins, the tropaeum becomes its seisin.",
    ),
    (
        1039,
        "The Perthean Compact: luctationes",
        "A Tribunal source whose harvest depends on the harvester's skill or "
        "daring is a luctatio, a contest open to any magus willing to try; "
        "success gives no right to later harvests. The list is public and a "
        "copy is kept at Confluensis, though how to win the vis need not be "
        "written down. Settling near one needs the Tribunal's leave, which "
        "is a little easier to get than for a tropaeum.",
    ),
    (
        1025,
        "Interim leases and plundering",
        "Whoever finds a vis source reports it to a Quaesitor, who grants an "
        "interim lease until the next meeting declares it. An interim lease "
        "is not exclusive: a second finder may get one too, and the holders "
        "settle it between themselves until the Tribunal rules. Harvesting "
        "an unknown source without declaring it is plundering, a Low Crime "
        "punished harshly, with fines above three times the vis taken. Vis "
        "traded or lent by the Redcaps, once it belongs to magi, is outside "
        "the Compact, which governs only gathering.",
    ),
    (
        1081,
        "The Library of the Tribunal",
        "Books given to the Tribunal in common, a custom begun by Perpauca "
        "of Bonisagus, are kept at Confluensis, their list public, and no "
        "one may read them unless they win them at the Tourney. A book won "
        "is leased for seven years under a Cow and Calf oath (copies made "
        "belong to the Tribunal) and must come back in good order before the "
        "next meeting. A magus who gives an original book wins at the next "
        "Tourney the lease of one of similar worth, settled by certamen when "
        "two authors want the same book. Pamphlets on each spine tell a "
        "reader its Quality and Level.",
    ),
    (
        1116,
        "Mundane resources and raiding",
        "Confirming the rulings of 1081 and 1088: a covenant's food, "
        "consumables, building supplies, arms and armour and luxuries are not "
        "part of its magi's magical power, so raiding them is no Hermetic "
        "crime; books (finished or not), vis, enchanted items and laboratory "
        "supplies are. Livestock and covenfolk have no protection (1123), "
        "but apprentices, familiars and magical beasts do. A raider may not "
        "damage the covenant's buildings (1130) or break the Code in any way "
        "during the raid, and must challenge any magus escorting the goods "
        "to certamen: losing ends the raid, winning sends the escort a mile "
        "off until sunrise. Raids by magi of other Tribunals fall under this "
        "Code too, and the Tribunal judges foreign raiders who break it "
        "especially harshly.",
    ),
    (
        1200,
        "The town senex",
        "The covenant nearest a town, its senex, has the better right there: "
        "if the senex's agents harm another covenant's interests in the "
        "town as a side effect, no ruin has been caused. The senex is the "
        "covenant where the town's church bells sound loudest, as a "
        "Quaesitor judges; a covenant that cannot hear them has no claim, so "
        "many towns have none. Made in Fudarus's favour against its vassal "
        "Atramentum over the artificers' guild of Le Conquet, and sometimes "
        "used to settle rival claims to urban vis.",
    ),
    (
        1207,
        "Urban covenants",
        "A covenant may sit in a town, and its magi's ordinary dealings with "
        "townsfolk ruin no one. A lord may grant a covenant a charter, but "
        "the magi may take none of its privileges, which would be fealty in "
        "all but name; paying a tax as a covenant is allowed, and seeking a "
        "charter to fix the limits of a lord's power is commended. Eligible "
        "covenfolk may vote and hold town office; magi may not. Made after "
        "several covenants took charters from King John and were then asked "
        "for soldiers. Fluvius's The Order and Towns (1208) is the standard "
        "commentary.",
    ),
    (
        None,
        "Mundane interference",
        "No ruling has ever been made. By long precedent a covenant is "
        "rarely convicted of meddling unless its actions bring mundane "
        "reprisals down on magi, and acting through a mundane 'mask' who "
        "never names his Hermetic sponsors protects it even when the mask "
        "is punished. Masks give no protection against a charge of "
        "depriving a magus of his power, so they cannot be used against a "
        "town's senex.",
    ),
    (
        None,
        "Founding a covenant",
        "A new covenant needs exclusive access to vis sources yielding at "
        "least a pawn a year for each of its magi, and never fewer than "
        "four, at its founding (aura vis does not count; losing the source "
        "or gaining magi later does not undo it), and a council chamber "
        "named to the Tribunal: any meeting place will do, a room, a cave or "
        "a grove, but not within a day's journey of another covenant's, by "
        "tradition out of reach of the Seven League Stride. Chapter houses "
        "may not be used to dodge the Compact; Fengheld's at Cherbourg is "
        "treated as a coenobium. Vis owed to a liege still counts.",
    ),
    (
        None,
        "Eremites and coenobia",
        "A solitary magus (an eremite) may own no seisin and lives on "
        "Tourney leases and luctationes. Magi who band together without "
        "meeting the vis rule are a coenobium, not a covenant: they own no "
        "seisin, rarely win a legacy, and enter the Tourney as solitary magi, "
        "and are looked down on for flouting the Tribunal's ways.",
    ),
    (
        None,
        "Oaths of fealty between covenants",
        "A liege covenant has one oath that all its vassals swear: support "
        "from the vassal (usually a vis tithe and its magi's sigils as free "
        "proxies), protection from the liege (using those proxies wisely and "
        "answering calls for aid on stated terms). The oath is part of the "
        "Peripheral Code and enforceable; it ends by agreement or after one "
        "side wins a prosecution of the other for default. Covenants still "
        "may not swear fealty to a mundane lord. When a liege dies out, all "
        "its vassals are free.",
    ),
    (
        1144,
        "Personal vis",
        "Vis that grows in a magus's own person, in his hair, blood and so "
        "on, is his alone and outside the Compact. A personal source outside "
        "him is still subject to it.",
    ),
    (
        None,
        "The host drawn by lot",
        "Since the Schism War the covenant that hosts the next meeting, and "
        "the Tourney after it, is drawn by lot from the Tribunal's covenants, "
        "not chosen as the Praeco's home. The host finds a secluded Tourney "
        "ground within a day's travel, hidden from mundane eyes (the "
        "Tribunal can lend a casting tablet for a Moon-duration Shrouded "
        "Glen), and must declare its own event to Confluensis by Redcap by "
        "the summer solstice before the meeting.",
    ),
    (
        None,
        "The Hermetic Tourney: entry and events",
        "Held after the meeting's business, usually over three days, with an "
        "even number of teams (the Redcaps recruit visitors to make it so) of "
        "at most five magi each, besides grogs and companions. A team that "
        "is not a recognised Normandy covenant stakes five pawns a magus, "
        "added to the prizes. A team starts with a point per member of its "
        "covenant (a coenobium's or visitor's magi one each). Six events: "
        "the hastiludium, a magical charge on village 'mounts' (20, 10 and 5 "
        "points to the semi-finalists); the certamen tournament (25, 15, 8); "
        "the dimicatio, forceless spells against a fast-cast defence, "
        "penetrating a Parma being a crime (23, 12, 6); each with a point for "
        "taking part; the melee of grogs rushing Creo Imaginem 'castles' "
        "with blunt weapons and no magic (6, then 2 for second to fourth, 1 "
        "for fifth; serious injury forfeits and is fined); the host's "
        "choice, a true test of magic it should not win (12, 8, 3, 3); and "
        "the deadly joust (20, 8, 3, 3), each with a point for taking part.",
    ),
    (
        1151,
        "The Hermetic Tourney: ranks and prizes",
        "Teams are ranked by points, ties going to the older covenant (or "
        "the earlier Gauntlet). Ranks win gold prize pawns, spent in rank "
        "order for leases until the next Tourney: at first one tropaeum or "
        "lump of one Art's vis and one book or item each, then again while "
        "pawns remain. A tropaeum costs a pawn for each pawn it yields; a "
        "book or item a pawn per 5 Build Points (no charged or limited "
        "items); a pawn buys at once 5 pawns of Form vis or 3 of Technique. "
        "First is the Siege of Normandy (31 pawns), second the Siege of "
        "Valor (24), seventh the Siege of Notatus (17), thirteenth the "
        "Siege of Shame (nothing, its prize going to the fourteenth, since "
        "an Iberian team disgraced the Tourney in 1151) and twenty-first the "
        "Siege of Alms (6 kept and 6 given to the teams below); each named "
        "rank brings a Hermetic Reputation of 2 for seven years. A prize not "
        "returned brings charges and a ban from the next Tourney.",
    ),
    (
        871,
        "The first meeting",
        "The Tribunal of the West Franks first meets with Confluensis, "
        "Pagus, Baiocassium, Bibracte and Sinapis; Fudarus and Branugurix "
        "attend the Britannian Tribunal instead.",
    ),
    (
        885,
        "Adela of Jerbiton acquitted",
        "Accused by a long-standing enemy of being court wizard to King Louis "
        "III from 879 to 881, Adela was acquitted, as nothing showed any "
        "danger to the Order from her friendship with the late king.",
    ),
    (
        899,
        "Lotharingia divided",
        "The Tribunal accepts the Grand Tribunal's decision, takes in part "
        "of the old Provençal lands and reaches east to the Rhine Tribunal.",
    ),
    (
        983,
        "The Normandy Tribunal",
        "On Adrianus of Montverte's proposal, the Tribunal of the West Franks "
        "is renamed for the Duke of Normandy, foremost lord of its lands.",
    ),
    (
        1018,
        "Brittany claimed",
        "Fudarus, the last Breton covenant left after the Schism War, is "
        "welcomed to the 22nd meeting, and the Tribunal claims Brittany and "
        "all its magical resources.",
    ),
    (
        1095,
        "Nauche-Fleur and the baron",
        "Nauche-Fleur was found innocent of swearing fealty to its baron, as "
        "the oath was taken by an unGifted companion acting as lord of the "
        "manor for the magi.",
    ),
    (
        1102,
        "The border by language",
        "On a complaint from three Flambeau of Provençal: where no clear "
        "border exists, disputed land goes by the language of its nearest "
        "settlement, langue d'oïl to Normandy and otherwise to Provençal. "
        "Upheld against Provençal's protest at the Grand Tribunal of 1129.",
    ),
    (
        1109,
        "The Donatores admitted",
        "Quaesitor Muirgheal brings into the Order the hedge wizards he "
        "found fighting a plague of restless dead, as the Ex Miscellanea "
        "tradition of the Donatores Requietis Aeternae.",
    ),
    (
        1116,
        "Koilios's raid; Praecepsus acquitted",
        "Quaesitor Lothaire upheld Koilios of Tytalus's raid of 1113 on Lapis "
        "Crudus's convoy of food and luxuries as no breach of the Code, "
        "fixing the custom of lawful raiding. Praecepsus of Flambeau, "
        "accused of cutting down the king's enemies with a Perdo sword in "
        "1111, had no charge to answer, as no mundane could tell magic was "
        "involved.",
    ),
    (
        1123,
        "Pandion's horses",
        "Pandion of Flambeau, who stole twelve horses from Antonin of "
        "Dragon's Rest, returned the one magical horse and paid ten pawns, "
        "keeping the other eleven as the spoils of a lawful raid: enchanted "
        "creatures count toward a magus's power, ordinary livestock and (as "
        "Lothaire added) covenfolk do not.",
    ),
    (
        1130,
        "Jacinth and Infelicitas",
        "Jacinth of Oleron, raiding Infelicitas, brought down its upper "
        "storey and two laboratories: convicted of deprivation (the charge "
        "of trying to kill a magus failed), he lost his familiar, and raiders "
        "were forbidden to damage a covenant's buildings.",
    ),
    (
        1144,
        "Lothaire accused",
        "Jacinth of Oleron accused Quaesitor Lothaire of profiting from raids "
        "by Montverte, Fudarus and their allies. He was cleared for want of "
        "substance but never regained his place as chief Quaesitor, and went "
        "to Magvillus.",
    ),
    (
        1172,
        "Atlax and the Redcap's letters",
        "Atlax of Tytalus read the messages Redcap Camille carried while a "
        "guest at Fudarus. Quaesitor Whent held the covenant responsible and "
        "gave one of its legacies to House Mercere.",
    ),
    (
        1179,
        "Pernix acquitted; Camille fined",
        "Pernix of Merinita, accused by Visurgis of Tytalus of healing a "
        "fallen nobleman by magic, was acquitted, as only the man and three "
        "friendly monks knew. Camille of Mercere, accused by Buliste of using "
        "a knight to gather a legacy's vis (the knight confessed to doing "
        "devils' work, and only Atlax of Fudarus averted ruin), paid fifteen "
        "pawns to Fudarus, and the source was closed for thirty years.",
    ),
    (
        1207,
        "Pugnatis expelled",
        "Convicted at the previous meeting of controlling the mayor of Laval "
        "by magic to reach a vis source and fined in enchanted items, "
        "Pugnatis came to neither this meeting nor with the items, and was "
        "expelled from the Order.",
    ),
)


# -- the Tribunal's own vis --

#: Vis sources the Tribunal holds in common that no region's part
#: enters: (source, tenure, until, notes). Tropaea are leased until the
#: next Tourney. Barenton, the Auvergne springs and the Cave of Sabinus
#: are entered with their regions.
TRIBUNAL_VIS: tuple[tuple[str, str, int | None, str], ...] = (
    (
        "Grove of St. Lie (Creo)",
        "tropaeum",
        1221,
        "A Gaulish mound in an oak grove above Reims with a hermit-saint's "
        "chapel: its pale flowers give a few pawns of Creo vis.",
    ),
)


def _vis(normandy: Normandy) -> None:
    for source, tenure, until, notes in TRIBUNAL_VIS:
        normandy.tenure(source, None, tenure, until, notes)


# -- the fallen covenants --

KNOWN_TRIBUNAL = {"status": "Known", "known": "In the Tribunal"}
KNOWN_LOCALLY = {"status": "Known", "known": "Locally"}
RUMOURED = {"status": "Rumoured", "known": "Locally"}

#: Each fallen covenant: (key, name, realm, status/known, summary, secret).
RUINS: tuple[tuple[str, str, str, dict[str, str], str, str], ...] = (
    (
        "bibracte",
        "Bibracte",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 822, sacked 969. A vassal of Fudarus on Mont Beuvray in the "
        "southern Morvan near Autun, the Gallic hill-city where Vercingetorix "
        "raised the tribes and Caesar wintered. A few Diedne and one Tytalus "
        "rebuilt its double ramparts and revived a cult of Vercingetorix, "
        "then turned against all things Roman: they banned Latin for "
        "Brythonic and refused to deal with the 'Roman' Houses. With Fudarus "
        "weakened after the corruption of House Tytalus, four Flambeau and "
        "Tremere of Montverte declared Wizard War on them together, calling "
        "them devil-worshippers, and destroyed the covenant. The overgrown "
        "ruins are mostly forgotten, though Helios of Atramentum Renatus now "
        "studies them and Philip of the Donatores fears he is angering the "
        "ghosts.",
        "Whether the cult succeeded in raising Vercingetorix's spirit is "
        "unknown; Helios means to find out.",
    ),
    (
        "pagus",
        "Pagus",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 840, destroyed 1008. A vassal of Confluensis at a ruined "
        "Roman outpost near Cherbourg, overlooking the Channel, whose magi "
        "spent heavily restoring the Roman buildings and a dock. The Viking "
        "raids wrecked it and cost it many vis sources; it never recovered, "
        "and the Diedne magi of Baiocassium destroyed it in the Schism War. "
        "Some of its old vis sources are now claimed, controversially, by "
        "Fengheld's chapter house at Cherbourg.",
        "",
    ),
    (
        "baiocassium",
        "Baiocassium",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 851, destroyed 1011. A vassal of Branugurix in the forest "
        "near Bayeux, its magi mostly Diedne descended from Gallic druids and "
        "friendly with the local faeries. Raided several times by Vikings, "
        "it founded a refuge in the town that became Baiocassium Minor; it "
        "destroyed Pagus in the Schism War and was itself destroyed in 1011. "
        "The ruin still lies in the shrinking forest of Bayeux.",
        "",
    ),
    (
        "sinapis",
        "Sinapis (the church at Tavant)",
        "Divine",
        KNOWN_LOCALLY,
        "Founded 855, abandoned 1063. Once a great liege in Anjou and head "
        "of its own line (Rotomagus, Aedes Salii and Lapis Crudus were its "
        "vassals), it was abandoned when the quarrel between Houses Tytalus "
        "and Flambeau ended and its magi left for Provençal and Iberia. All "
        "that remains is a small church at Tavant, six miles up the Vienne "
        "from Chinon, which a poor parish took over unaware of its past: "
        "lifelike paintings, lily-bearing figures by the crypt door, and "
        "carvings of griffins, sirens, a two-bodied monster and a serpent "
        "in a tree. Its old Magic aura shows only when the Dominion is at "
        "its weakest. Lapis Crudus counts itself of Sinapis's line.",
        "",
    ),
    (
        "rotomagus",
        "Rotomagus",
        "Magic",
        KNOWN_LOCALLY,
        "Founded 875, destroyed 892. Founded near Rouen by Sinapis's first "
        "apprentices and destroyed when the Vikings sacked the city less "
        "than twenty years later. Its one survivor left House Flambeau in "
        "shame for Ex Miscellanea.",
        "",
    ),
    (
        "ligurio",
        "Ligurio",
        "Magic",
        KNOWN_LOCALLY,
        "Founded 913, destroyed 1011. A vassal of Fudarus in the great "
        "marsh of the Vendée on the Aquitaine-Brittany border, lasting about "
        "a century until giants hurling boulders smashed it, sent, it is "
        "thought, by the Diedne of Kerguntuil. Little is left: its buildings "
        "have sunk into the marsh among fishers and fowlers, near the priory "
        "at Sallertaine and the abbey at Chauvet.",
        "",
    ),
    (
        "kerguntuil",
        "Kerguntuil",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 920, destroyed 1007. A Diedne vassal of Branugurix on the "
        "Rose Coast, named for the dolmen on a hilltop above the Trégastel "
        "headland, said to be a petrified giant. Its magi studied the Breton "
        "giant tales and many of its covenfolk were unusually large. Raided "
        "by Vikings, it was obliterated in the Schism War. The Templars' "
        "round chapel at Lanleff and the church at Lannion were built "
        "nearby, by rumour at a Quaesitor's suggestion, to cleanse the coast "
        "of Diedne taint.",
        "",
    ),
    (
        "baiocassium_minor",
        "Baiocassium Minor",
        "Magic",
        RUMOURED,
        "Founded 936, destroyed 1005. A vassal of Baiocassium, begun as a "
        "spring sanctuary in a regio inside the town of Bayeux after the "
        "Viking raids, and destroyed in the Schism War. No living magus "
        "admits to knowing where the regio is.",
        "",
    ),
    (
        "caput_capra",
        "Caput Capra",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 981, destroyed 1005. The youngest and easternmost vassal "
        "of Branugurix, on the Loire near Fleury, founded to guard the old "
        "druids' assembly ground there through the lawless late tenth "
        "century. It was the first covenant in the Tribunal to fall in the "
        "Schism War. Confluensis brings its apprentices to the scant ruins "
        "for their history lessons.",
        "",
    ),
    (
        "aedes_salii",
        "Aedes Salii",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 998, disbanded 1063. A vassal of Sinapis on Jersey, named "
        "for the priests of Mars and founded to run the Schism War in "
        "Normandy and Stonehenge. Its Tremere went home after the war, "
        "leaving it to House Flambeau, and it was disbanded when the "
        "Flambeau withdrew from the Tribunal; two of its magi joined Lapis "
        "Crudus.",
        "",
    ),
    (
        "orchard_of_sour_apples",
        "Orchard of Sour Apples",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1020, absorbed 1051. A vassal of Confluensis founded after "
        "the Schism War and named for a nearby vis source. When Confluensis "
        "had to move, it took over the site and the Orchard's magi joined "
        "their liege; Confluensis stands there now.",
        "",
    ),
    (
        "lixivia",
        "Lixivia",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1021, disbanded 1124. A vassal of Florum in Champagne, set "
        "up as the fairs began to deal between the Order and mundane "
        "merchants. Its Redcaps and Gentle Gifted magi offered to find "
        "anything any covenant wanted, but magi distrusted them, raided "
        "them freely, and drove them into poverty until they disbanded. "
        "Its Redcaps went on to found Alcuin's Auberge.",
        "",
    ),
    (
        "vexatores",
        "Vexatores",
        "Magic",
        KNOWN_LOCALLY,
        "Founded 1048, abandoned 1064. A vassal of Fudarus founded only to "
        "provoke Sinapis in the quarrel between Tytalus and Flambeau, 21 "
        "miles north of it (the least the law allowed) at one of the vis "
        "sources taken from House Diedne. Never meant to last, it was "
        "abandoned once the quarrel ended.",
        "",
    ),
    (
        "nauche_fleur",
        "Nauche-Fleur",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1072, ended 1166. A vassal of Montverte near Niort in "
        "Aquitaine that ran a school of arms and letters whose fees kept its "
        "magi in luxury. Cleared in 1095 of swearing fealty to its baron, it "
        "was always controversial for its part in mundane politics, so none "
        "of its apprentices stayed, and it died when the last founder went "
        "into Final Twilight.",
        "",
    ),
    (
        "infelicitas",
        "Infelicitas",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1099, abandoned 1158. A vassal of Fudarus in Flanders, "
        "founded when Rancrax of Tytalus lost a wager to his rival and had "
        "to leave Fudarus. Jacinth of Oleron's raid in 1130 brought down its "
        "upper storey and two laboratories. It foundered when Rancrax was "
        "killed in Wizard War by a magus of Moles Magna and the other two "
        "magi did not care to stay. Some once suspected it, or Florum, of "
        "raising the tidal wave that struck the Flemish coast.",
        "",
    ),
    (
        "alcuins_auberge",
        "Alcuin's Auberge",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1124, destroyed 1197. A small Mercer House of Florum's line "
        "in Tours, founded by Redcaps from Lixivia in rooms dug beneath a "
        "pilgrim hostel, home to two Redcaps and a stopping place for others "
        "and passing magi. It prospered, drew the wrong attention, and fell "
        "to unknown raiders; some blame Fudarus, unproven.",
        "",
    ),
    (
        "moles_magna",
        "Moles Magna",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1136, destroyed 1182. A vassal of Oleron on the edge of the "
        "Morvan, built inside a dam on a small tributary of the Yonne, the "
        "lake behind and the waterfall in front hiding it. One of its magi "
        "killed Rancrax of Infelicitas in Wizard War. The dam burst after "
        "heavy rain despite the magic that held it, and the covenant was "
        "swept away; most think the magi had angered a spirit of the river "
        "they penned.",
        "",
    ),
    (
        "atramentum",
        "Atramentum",
        "Magic",
        KNOWN_TRIBUNAL,
        "Founded 1200, taken 1201. A vassal of Fudarus in the Arrée "
        "Mountains of Brittany, founded by Helios of Tytalus and Gulo "
        "Midusulfis of Bjornaer and named 'Ink' for a sodalis who died at "
        "the founding, just as the two Tytalus Primi began their feud. It "
        "lost a case against Fudarus over the artificers' guild of Le "
        "Conquet (the town senex ruling of 1200), and a year after its "
        "founding the elder Tytali leaving Fudarus evicted its founders and "
        "made it Exspectatio. Cynics say the young magi were used to "
        "prepare the ground. The founders went on to found Atramentum "
        "Renatus.",
        "",
    ),
)


def _ruins(normandy: Normandy) -> None:
    b = normandy.b
    normandy.places["ruin_branugurix"] = b.place(
        "Branugurix (Mount Dol)",
        ruined=True,
        summary=secrets(
            paragraphs(
                "Founded 791, sealed 1012. The Domus Magna of House Diedne, "
                "properly Bren Gwrac'h, hidden in a regio on Mount Dol, a "
                "low granite outcrop in the county of Rennes sacred to the "
                "Gallic druids. In the last great battle of the Schism War "
                "the Diedne Primus somehow closed every entrance to the "
                "regio, and some of the Flambeau and Tremere attackers were "
                "shut inside and never seen again. Its vassals were "
                "Baiocassium, Kerguntuil and Caput Capra.",
                "Christians shun the mount; their tale of St. Michael "
                "hurling the Devil down here, and leaping after him to Mont "
                "St. Michel, remembers the assault. House Guernicus's "
                "records hold the regio's exact place and the old way in, "
                "and the House watches anyone who spends long around Mount "
                "Dol.",
            ),
            "Rumour says some Diedne survived inside the sealed regio and "
            "that someone is working to free them after two centuries; "
            "Lapis Crudus's return from its own regio has made the Tribunal "
            "fear this again.",
        ),
        realm="Magic",
        status="Known",
        known="In the Order",
        levels=[
            b.level(
                "Bren Gwrac'h",
                0,
                see="Sealed: no way in is known outside the Guernicus records.",
                enter="Closed by the Diedne Primus in 1012.",
                notes="The Diedne Domus Magna as it was sealed, with whatever "
                "attackers and defenders were trapped there. The book gives "
                "no aura.",
            )
        ],
    )
    for key, name, realm, standing, summary, hidden in RUINS:
        normandy.places[f"ruin_{key}"] = b.place(
            name,
            ruined=True,
            summary=secrets(summary, hidden),
            realm=realm,
            status=standing["status"],
            known=standing["known"],
        )


# -- the docket --


def _docket(normandy: Normandy) -> None:
    b, tribunal = normandy.b, normandy.tribunal
    assert tribunal is not None
    b.case(
        tribunal,
        "The Praeco's succession",
        kind="motion",
        brought_by="Proctor of Guernicus (Presiding Quaesitor)",
        charge="Renita of Bjornaer, Praeco and leader of Confluensis, died "
        "last winter. By custom the eldest magus succeeds: Stellatus, her "
        "sept-mate, has left for Iberia, so the next are Celeres of Cunfin, "
        "then Somnifer of Lapis Crudus, then Geirlaug of Montverte. Proctor "
        "fears Celeres's eccentricity and his sway over Cunfin's Redcaps and "
        "wants him set aside for someone he can trust or control, without "
        "seeming partial; many magi would rather see Proctor's own power "
        "checked.",
        filed_year=1220,
        filed_season="Spring",
        notice_given=True,
    )
    b.case(
        tribunal,
        "Augustina of Tytalus, the Traitor",
        kind="motion",
        brought_by="Proctor of Guernicus",
        against="Augustina of Tytalus",
        charge="The Traitor, exiled by her own choice from House Tytalus with "
        "the single duty of restarting its conflicts when they stall, serves "
        "Confluensis as hoplite. Twenty-five years into the stalled feud of "
        "the Primi Harpax and Buliste, and with the Traitor's key thought to "
        "weaken Fudarus's defences, Proctor, who distrusts every Tytalus, "
        "gives her the riskiest and least trusted tasks and questions "
        "whether she can be trusted with Quaesitorial work at all.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Fengheld's chapter at Cherbourg",
        kind="charge",
        brought_by="Confluensis",
        against="The Cherbourg chapter of Fengheld (Rhine)",
        charge="The lone maga of Fengheld's chapter house near Cherbourg, a "
        "coenobite under Normandy's Code, harvests vis sources that once "
        "belonged to Pagus and that Confluensis has traditionally gathered, "
        "and seeks recognition as a covenant. Chapter houses may not be used "
        "to sidestep the Perthean Compact.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "A Provençal claim by language",
        kind="motion",
        brought_by="A magus of the Provençal Tribunal",
        charge="A rich vis source in Normandy's southern reaches is claimed "
        "for Provençal on the ground that the nearby villagers say 'oc', not "
        "'oïl', which under the ruling of 1102 would make the land "
        "Provençal's. Whether the village is truly of the langue d'oc, or "
        "the claim a fraud, is unproven.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Praeda's vis auction",
        kind="charge",
        brought_by="",
        against="Praeda",
        charge="Praeda auctions vis smuggled in from the southern Tribunals "
        "to a paying consortium of covenants. Plundering another Tribunal is "
        "no crime here, but vis gathered this way is a luctatio and should "
        "be open to all, so selling it to a closed club breaches the "
        "Perthean Compact.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "Raiders from over the border",
        kind="motion",
        brought_by="The covenants of the borders",
        charge="Magi of the Rhine and Iberian Tribunals have raided Normandy "
        "covenants under Normandy's own Code. The Tribunal at large thinks "
        "it minor and can only punish foreign raiders harshly when they "
        "break the Code; covenants within reach of another Tribunal want "
        "more done.",
        filed_year=1220,
        filed_season="Spring",
    )
    b.case(
        tribunal,
        "A covenant at the vacant castle",
        kind="motion",
        brought_by="The expedition of 1218",
        charge="A castle in the Cotentin, empty since 1204 and now the lair "
        "of a monster akin to Grendel's kin, holds a strong Magic aura; the "
        "magi who explored it in 1218 will propose sending colonists to "
        "found a covenant there. French officials would seek influence over "
        "a repopulated castle unless a royal grant comes first.",
        filed_year=1220,
        filed_season="Spring",
    )


# -- after every part has built --

#: Each vassal and its liege, along the five great lines: (vassal names
#: tried in order, liege names tried in order).
FEALTY: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("Exspectatio",), ("Fudarus",)),
    (("Atramentum Renatus",), ("Exspectatio",)),
    (("Dragon's Rest",), ("Confluensis",)),
    (("Cunfin",), ("Confluensis",)),
    (("Spider's Palace", "The Spider's Palace"), ("Florum",)),
    (("Requies Aeterna",), ("Florum",)),
    (("Nidi", "Conventio Nidi"), ("Oleron",)),
    (("Atsingani",), ("Montverte",)),
)

#: What finish could not find, for the report.
MISSING: list[str] = []


def _covenant(normandy: Normandy, names: tuple[str, ...]) -> Covenant | None:
    for name in names:
        try:
            return normandy.covenant_named(name)
        except KeyError:
            continue
    MISSING.append(names[0])
    return None


#: The region each fallen covenant lies in, where the regions' parts
#: made it (they are built after the ruins).
RUIN_REGIONS: dict[str, str] = {
    "ruin_branugurix": "mount_dol",
    "ruin_kerguntuil": "rose_coast",
    "ruin_caput_capra": "ile_de_france",
    "ruin_bibracte": "burgundy",
    "ruin_baiocassium": "bayeux_county",
    "ruin_baiocassium_minor": "bayeux_county",
    "ruin_rotomagus": "seine_basin",
}


def finish(normandy: Normandy) -> None:
    tribunal = normandy.tribunal
    assert tribunal is not None
    saga = normandy.b.saga
    MISSING.clear()
    # The Praeco is vacant until the succession is settled.
    tribunal.praeco_id = None
    proctor = next(
        (c for c in saga.characters if c.name.split(",")[0].startswith("Proctor")),
        None,
    )
    tribunal.quaesitor_id = proctor.id if proctor is not None else None
    if proctor is None:
        MISSING.append("Proctor")
    for vassal_names, liege_names in FEALTY:
        vassal = _covenant(normandy, vassal_names)
        liege = _covenant(normandy, liege_names)
        if vassal is None or liege is None:
            continue
        vassal.liege_id = liege.id
        vassal.oath = vassal.oath or OATH
        vassals.swear(vassal, liege)
    for ruin, region in RUIN_REGIONS.items():
        site, around = normandy.places.get(ruin), normandy.places.get(region)
        if site is not None and around is not None and site.place_id is None:
            site.place_id = around.id
    tribunal.covenants_total = len(
        [c for c in saga.covenants if c.tribunal_id == tribunal.id]
    )
