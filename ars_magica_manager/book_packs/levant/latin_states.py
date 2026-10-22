"""The Latin states and the other Christian lords of 1220 (ch03, ch04,
the appendix of ruling dynasties), in paraphrase.

Lords (L18): the King of Jerusalem (Queen Isabel, called Yolanda, with
John of Brienne as regent, at Acre), whose summary holds the kingdom's
government: the crown's claims, the Haute Cour and the great offices,
the money-fiefs and the burgesses, the courts and the subject peoples;
the Count of Tripoli and the Prince of Antioch, both Bohemond IV; the
King of Cyprus (Henry I), with the island's own customs; the King of
Lesser Armenia (Raymond-Rupen holding Tarsus, with Constantine's party
in the summary); and the Alans of the Caucasus as a faction. Each
lord's "if history runs on" dates are in his summary (L18, L22), from
history where the book's appendix stops.

The shared lords are east.py's and keep their text: in finish the
Sultan of Rum and the Emperor of Trebizond are set in places["asia_minor"]
and the King of Georgia in places["georgia"] where they have no place
yet. Each lord sits in his region from places.py (set again in finish
when places.py made it late), and finish links the lords to their
capitals (places.py's towns, and Tarsus), to one another, and the Alans to Urania.

Keys: world["jerusalem_king"], ["tripoli_count"], ["antioch_prince"],
["cyprus_king"], ["armenian_king"], ["alans"]."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Levant

#: Where each of this part's records sits: its key in world, and the
#: region (a key in places) places.py makes for it.
REGIONS: tuple[tuple[str, str], ...] = (
    ("jerusalem_king", "jerusalem_kingdom"),
    ("tripoli_count", "tripoli_county"),
    ("antioch_prince", "antioch"),
    ("cyprus_king", "cyprus"),
    ("armenian_king", "lesser_armenia"),
    ("alans", "alan_lands"),
)

#: The shared lords this pack places on its own map, where they have no
#: place yet: (world key, places key).
SHARED_REGIONS: tuple[tuple[str, str], ...] = (
    ("sultan_of_rum", "asia_minor"),
    ("emperor_of_trebizond", "asia_minor"),
    ("king_of_georgia", "georgia"),
)

#: Each lord's capital, a town of places.py's: (lord key, town key, note).
CAPITALS: tuple[tuple[str, str, str], ...] = (
    ("jerusalem_king", "acre", "The kingdom's capital since 1187"),
    ("tripoli_count", "tripoli", "His county's capital"),
    ("antioch_prince", "antioch_city", "His capital, retaken in 1219"),
    ("cyprus_king", "nicosia", "His capital"),
    ("cyprus_king", "famagusta", "His island's rising port"),
)


def build(levant: Levant) -> None:
    _jerusalem(levant)
    _tripoli_and_antioch(levant)
    _cyprus(levant)
    _lesser_armenia(levant)
    _alans(levant)


def _region(levant: Levant, key: str) -> Neighbour | None:
    return levant.places.get(dict(REGIONS)[key])


# -- the Kingdom of Jerusalem --


def _jerusalem(levant: Levant) -> None:
    levant.world["jerusalem_king"] = levant.b.lord(
        "King of Jerusalem",
        title="duke",
        wealth="Wealthy",
        seat="Acre",
        ruler="Queen Isabel II (Yolanda); John of Brienne, regent",
        place=_region(levant, "jerusalem_king"),
        summary=paragraphs(
            "Since Hattin the kingdom is a narrow coast running from "
            "Beirut down to Ascalon, saved by the crusades of the 1190s "
            "and governed from Acre since Jerusalem fell in 1187. Its "
            "heir is Isabel, whom many call Yolanda, still a child; her "
            "father John of Brienne has ruled for her since 1210 and is "
            "king in all but name. Latin lords sit over native "
            "Christians, Jews and Muslims, and the realm lives chiefly on "
            "the goods that pass through its ports between the East and "
            "Europe, with its farms besides.",
            "The crown. A king must be the next heir and be accepted by "
            "the barons of the Latin states, though the barons' choice "
            "only counts when the succession is disputed. He rules this "
            "kingdom and claims a precedence over Antioch and Tripoli. A "
            "run of quarrelled-over successions and weak kings, worst "
            "after Hattin, let the nobles grow strong at the crown's "
            "expense; John has set out to undo that, but he is hampered "
            "now, for the legate Pelagius holds that whatever the Crusade "
            "wins in Egypt is the Church's and not the kingdom's, and the "
            "quarrel waits on the Crusade's end.",
            "The Haute Cour and the offices. The king governs in his High "
            "Court with the barons, the masters of the military orders, "
            "the heads of the communes and the great churchmen, though "
            "the great landholders usually carry it; the same court "
            "judges the nobility. The work of government falls to "
            "officers chosen from the nobles: the seneschal is the king's "
            "deputy, the constable leads his armies, the chamberlain "
            "runs his household, and the chancellor, who keeps his "
            "letters and his treasury, is always a cleric and of little "
            "weight.",
            "Fiefs and burgesses. The kingdom has far more knights than "
            "land to give them, so beside the great barons who hold land "
            "of the king and enfeoff their own men, many lesser knights "
            "hold a money-fief: a fixed yearly sum for their service, "
            "some of it barely a living. Such knights depend wholly on "
            "their lords and mostly live in the towns. Under the nobles "
            "are the burgesses, free commoners sprung from the settlers "
            "who came out behind the first crusaders: they hold their "
            "houses, gardens and vineyards in burgage tenure for a token "
            "rent, work mostly as craftsmen and traders, serve as "
            "officials, police, customs men and paid foot, and the most "
            "successful have risen in the royal or church service, some "
            "even marrying lesser nobles.",
            "The courts. Nobles are judged in the Haute Cour and vassals "
            "in their lords' courts; townsmen go to the Court of "
            "Burgesses; the subject peoples of a town go to the Court of "
            "the Market, which sends grave cases up to the Burgesses; "
            "the Court of the Chain hears matters of the sea; and the "
            "communes and the Church keep courts of their own. A village "
            "wholly of natives follows its own law, but a mixed one is "
            "judged by the Latins. Juries hear most cases, yet combat and "
            "the ordeal are used at every level. Government writes in "
            "Latin, and French is the Latins' commonest tongue.",
            "The subject peoples. Every native, Christian, Jew or Muslim, "
            "is a subject of the Latins and ranks below any Latin; the "
            "Maronites, united with Rome since 1182, are the exception "
            "and are nearly the Latins' equals. Natives may not join a "
            "commune and are rarely nobles or merchants; most farm or "
            "work a craft, and some serve as dragomans, interpreting "
            "between the Latins and the Muslims. Some lords leave their "
            "subjects in peace so long as dues are paid, others treat "
            "them, Muslims above all, much like serfs, and captives not "
            "ransomed are enslaved. Many Latins have learnt to trade and "
            "even ally with Muslim neighbours, and zeal for the holy war "
            "comes and goes; the new Crusade in Egypt has stirred it up, "
            "though not every Latin of the Levant backs it.",
            "If history runs on: Isabel marries the Emperor Frederick II "
            "in 1225 and he is king through her; she dies in childbirth, "
            "leaving him regent for their infant son. Frederick reaches "
            "Acre in 1228 and in February 1229 wins Jerusalem, Bethlehem "
            "and a road to the coast by treaty with al-Kamil, the Muslims "
            "keeping the Temple enclosure. The city is lost again in "
            "1244, Louis IX of France crusades from 1248 to 1254, and "
            "Acre, the last capital, falls to the Mamluks in 1291.",
        ),
    )


# -- Tripoli and Antioch --


def _tripoli_and_antioch(levant: Levant) -> None:
    b = levant.b
    levant.world["tripoli_count"] = b.lord(
        "Count of Tripoli",
        title="count",
        wealth="Wealthy",
        seat="Tripoli",
        ruler="Bohemond IV of Antioch (Bohemond I of Tripoli)",
        place=_region(levant, "tripoli_count"),
        summary=paragraphs(
            "The county runs north along the coast from about Beirut to "
            "Valania and reaches a little further inland than the "
            "kingdom; on its north-east it meets Masyaf and the lands of "
            "the Syrian Nizaris. When Count Raymond III died in 1187 it "
            "passed to the house of Antioch, so its count is the Prince "
            "of Antioch, Bohemond, fourth of that name at Antioch and "
            "first at Tripoli. Latin lords rule native Christians, Jews "
            "and Muslims, and the county lives on trade, fruit and grain.",
            "If history runs on: Bohemond dies in 1233 and his son "
            "Bohemond V follows him; Tripoli itself holds out until "
            "Qalawun takes it in April 1289.",
        ),
    )
    levant.world["antioch_prince"] = b.lord(
        "Prince of Antioch",
        title="count",
        wealth="Average",
        seat="Antioch",
        ruler="Bohemond IV",
        place=_region(levant, "antioch_prince"),
        summary=paragraphs(
            "The oldest of the Latin states, on the north-east corner of "
            "the coast and much the smallest of them. When Prince "
            "Bohemond III died in 1201 the principality should have gone "
            "to his grandson Raymond-Rupen, but Raymond-Rupen's uncle "
            "Bohemond IV pushed him aside. Raymond-Rupen won it back in "
            "1216 and lost it to his uncle again in 1219, the year he "
            "inherited Lesser Armenia; he is now making himself secure "
            "at Tarsus and is expected to try for Antioch once more if "
            "he can. Bohemond, Count of Tripoli as well, is back in the "
            "capital.",
            "If history runs on: Bohemond rules until 1233, and Baybars "
            "takes Antioch in May 1268, ending the oldest of the Latin "
            "states.",
        ),
    )


# -- Cyprus --


def _cyprus(levant: Levant) -> None:
    levant.world["cyprus_king"] = levant.b.lord(
        "King of Cyprus",
        title="duke",
        wealth="Wealthy",
        seat="Nicosia",
        ruler="Henry I of Lusignan",
        place=_region(levant, "cyprus_king"),
        summary=paragraphs(
            "The youngest Latin state and the only one off the Levantine "
            "coast: an island some 150 miles by 70, mountainous in the "
            "north and west and a fertile plain elsewhere, living by its "
            "farms, with wine and salt above all. Richard the Lionheart "
            "took it from Isaac Comnenus on his way to Acre in 1191 and "
            "sold it to the Templars, who could not hold it and handed "
            "it back; in 1192 he sold it to Guy of Lusignan, whose great-"
            "nephew Henry I is king now. The book says no more of him; "
            "history has Henry a child crowned in 1218, with his mother "
            "Alice of Champagne as regent and Philip of Ibelin as bailli.",
            "The Lusignans have brought the mainland's laws and feudal "
            "order to the island, but keep it their own way. The Latins "
            "rule a people mostly Greek, mostly rural and Greek in "
            "custom, most of them reduced to servitude, though some "
            "wealthier Greeks are still free. Fearing rebellion, the "
            "king lets few vassals hold a stronghold, and he keeps the "
            "Church strictly from holding fiefs. The island's church is "
            "under an archbishop at Nicosia, not a patriarch, and its "
            "king is a monarch in his own right who owes nothing to the "
            "King of Jerusalem. Its ports are Kyrenia, Limassol and, "
            "rising fastest, Famagusta. The Lusignans are quick to see a "
            "threat to their rule.",
            "If history runs on: Henry reigns until 1253. When the "
            "mainland falls in 1291 the military orders withdraw to "
            "Cyprus, and it is the one place the Latins, and the Order's "
            "magi, stay on: the Lusignans hold it until 1489 and Venice "
            "until 1573, when the Ottomans take it.",
        ),
    )


# -- Lesser Armenia --


def _lesser_armenia(levant: Levant) -> None:
    levant.world["armenian_king"] = levant.b.lord(
        "King of Lesser Armenia",
        title="duke",
        wealth="Average",
        seat="Tarsus",
        ruler="Raymond-Rupen",
        place=_region(levant, "armenian_king"),
        summary=paragraphs(
            "Cilicia, once a western march of Greater Armenia: mountains "
            "with a thin coastal plain that broadens to the east. A "
            "Byzantine land, it filled with Armenians fleeing east in "
            "the tenth century; after Manzikert in 1071 local dynasties "
            "set up on their own, outlasted the Seljuks, and dealt with "
            "the Latins and Byzantines by turns as friends and foes, "
            "until in 1198 Leon II was crowned king in Tarsus "
            "cathedral before the papal legate, Conrad of Mainz.",
            "Leon died in 1219 after thirty-two years, and his "
            "great-nephew Raymond-Rupen, put out of Antioch the same "
            "year, came to Tarsus to take the crown. His hold is weak: "
            "the people of Tarsus would rather have Leon's cousin "
            "Constantine, and he may not keep the throne for long. The "
            "country lives by timber from the Taurus forests, goatskins "
            "and goat-hair cloth, and is famed for its illuminated books "
            "and metalwork, which it sells to Genoa and Venice. Its "
            "rulers keep the Armenian national church, neither Latin nor "
            "Greek.",
            "If history runs on (history, not the book): Constantine's "
            "party takes Raymond-Rupen in 1221 and he dies a prisoner "
            "the next year; Leon's daughter Isabel is crowned instead, "
            "wed first to Philip, a son of Bohemond IV, and in 1226 to "
            "Constantine's son Hethum, who reigns until 1270.",
        ),
    )


# -- the Alans --


def _alans(levant: Levant) -> None:
    levant.world["alans"] = levant.b.faction(
        "The Alans",
        faction="Other",
        place=_region(levant, "alans"),
        summary=paragraphs(
            "A people of many tribes in the Caucasus mountains and the "
            "country north of them, the far north-eastern edge of the "
            "Tribunal. Most are Greek Christians, though their loyalty "
            "to that church has wavered over the years; some live in "
            "Georgia too. The aloof covenant of Urania lies deep in "
            "their lands, kept safe mostly by how remote it is.",
            "If history runs on: Mongol riders under Jebe and Subadei "
            "come through the Caucasus in 1222 and beat the Alans, and "
            "the Mongols conquer the Alan lands in 1238, destroying "
            "Urania with them.",
        ),
    )


# -- after every part has built --


def _place_in(record: Neighbour | None, place: Neighbour | None) -> None:
    if record is not None and place is not None and record.place_id is None:
        record.place_id = place.id


def finish(levant: Levant) -> None:
    b, w = levant.b, levant.world
    for key, region in (*REGIONS, *SHARED_REGIONS):
        _place_in(w.get(key), levant.places.get(region))
    for lord, town, note in CAPITALS:
        found = w.get(town)
        if found is not None:
            b.link(w[lord], "places", found, note)
    tripoli, antioch = w["tripoli_count"], w["antioch_prince"]
    b.link(tripoli, "places", antioch, "Held by the same man, Bohemond IV")
    b.link(antioch, "places", tripoli, "Held by the same man, Bohemond IV")
    b.link(
        w["armenian_king"],
        "places",
        antioch,
        "His uncle, who twice put him out of Antioch",
    )
    tarsus = levant.places.get("tarsus")
    if tarsus is not None:
        b.link(
            w["armenian_king"],
            "places",
            tarsus,
            "His seat, where Constantine is favoured",
        )
    legate = w.get("pelagius")
    if legate is not None:
        b.link(
            w["jerusalem_king"],
            "places",
            legate,
            "Claims the Crusade's conquests for the Church",
        )
    crusade = w.get("fifth_crusade")
    if crusade is not None:
        b.link(w["jerusalem_king"], "places", crusade, "John of Brienne fights in it")
    urania = levant.covenants.get("urania")
    if urania is not None:
        b.link(w["alans"], "covenants", urania, "Lies in their lands")
