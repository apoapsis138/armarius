"""The Muslim powers of 1220 (ch03, ch05, the appendix of ruling
dynasties), in paraphrase.

This part's own records: al-Mu'azzam, the Ayyubid sultan of Damascus,
answering to the shared al-Kamil, whose summary also holds how a Muslim
prince of the Levant rules (viziers, emirs, iqta's and niyabas,
mamluks); the Syrian Nizaris as a faction (tradition
trad_nizari_mustajibs, Q2), with the Assassin's dagger at DE levels
(L25), their chief at Masyaf as a lord answering to the shared Lord of
Alamut (Jalal al-Din Hasan), and Masyaf as a place in places["syria"];
and the Bedouin and the Turcomans as factions with no tradition (Q2).
Real titles (sultan, da'i) are in the names and summaries (L18), with
"if history runs on" dates.

The caliph, al-Kamil, al-'Aziz, the Emir of Mosul and the Nizaris are
east.py's shared records and keep their text. In finish this part sets
each one's place where it has none: al-Kamil in places["egypt"],
al-'Aziz in places["syria"], the Emir of Mosul in the region of
world["mosul"] (Iraq), and the Order of Suleiman and its two families
at their seats (world["baghdad"], ["damascus"], ["cairo"]); and links
al-Mu'azzam to Damascus, Jerusalem and Aedes Veritatis.

Keys: world["al_muazzam"], ["syrian_nizaris"], ["masyaf_chief"],
["bedouin"], ["turcomans"]; places["masyaf"]."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...rules.sites import PLACE
from ..builder import paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Levant

#: The shared records this pack places, where they have no place yet:
#: (world key, "places" or "world", key of the place).
SHARED_PLACES: tuple[tuple[str, str, str], ...] = (
    ("al_kamil", "places", "egypt"),
    ("al_aziz", "places", "syria"),
    ("order", "world", "baghdad"),
    ("stone", "world", "damascus"),
    ("river", "world", "cairo"),
)

#: This part's records and where they sit, set again in finish when
#: places.py made the place late: (world key, "places" or "world", key).
OWN_PLACES: tuple[tuple[str, str, str], ...] = (
    ("al_muazzam", "places", "syria"),
    ("syrian_nizaris", "places", "masyaf"),
    ("masyaf_chief", "places", "masyaf"),
    ("bedouin", "places", "levant"),
    ("turcomans", "places", "asia_minor"),
)


def build(levant: Levant) -> None:
    _damascus(levant)
    _nizaris(levant)
    _nomads(levant)


def _where(levant: Levant, kind: str, key: str) -> Neighbour | None:
    return (levant.places if kind == "places" else levant.world).get(key)


# -- Damascus --


def _damascus(levant: Levant) -> None:
    w = levant.world
    w["al_muazzam"] = levant.b.lord(
        "Ayyubid Sultan of Damascus",
        title="count",
        wealth="Wealthy",
        seat="Damascus",
        ruler="al-Mu'azzam 'Isa",
        answers_to=w.get("al_kamil"),
        place=levant.places.get("syria"),
        summary=paragraphs(
            "Al-Malik al-Mu'azzam 'Isa, nephew of Salah al-Din and "
            "younger brother of al-Kamil, who governed Damascus for their "
            "father al-'Adil from 1201 and has ruled it in his own right "
            "since al-'Adil died in 1218. He holds southern Syria and the "
            "Holy Land with Jerusalem, and owns his brother in Cairo as "
            "head of the family, though the two are rivals more than "
            "allies, as Ayyubid princes tend to be.",
            "In 1219, afraid that the family might have to give "
            "Jerusalem back to the crusaders in Egypt, he had the city "
            "torn down, its walls first, sparing only the Temple Mount, "
            "the Church of the Holy Sepulchre and the citadel; its "
            "Muslims have fled east, leaving whole streets empty. Against "
            "the Latins he has made Damascus's walls stronger and rebuilt "
            "its citadel, and he and his court favour the city's "
            "religious colleges and scholars. Aedes Veritatis, a few "
            "miles from his city, sells his builders quarry stone, which "
            "the quaesitores have ruled lawful.",
            "How a prince of the Levant rules. The great Muslim houses, "
            "the Ayyubids in Syria, the Holy Land and Egypt, the Seljuks "
            "in Asia Minor, owe the caliph allegiance and in practice "
            "go their own way. The caliph may invest a dynasty's head as "
            "sultan, though many take the title unasked. A vizier runs a "
            "ruler's civil and military business and can master a weak "
            "one. Below him come the emirs, Turks, Kurds, Persians or "
            "Arabs, appointed by the ruler, who may give an emir an "
            "iqta' (land held for a set number of horsemen, usually "
            "hereditary but revocable) or a niyaba (a governorship); the "
            "best of both go to the ruler's own kin, and the greatest "
            "are styled amir kabir or amir isfahsalar. The ruler names "
            "the commanders in war. An army's core is its mamluks, slave "
            "soldiers bought young, trained, freed when grown and loyal "
            "to their old masters, often Turks, with the emirs' levies, "
            "hired men and Bedouin volunteers beside them.",
            "If history runs on: al-Kamil, wanting help against him, "
            "sends envoys to Frederick II in 1226; al-Mu'azzam dies in "
            "1227 and his son al-Nasir Dawud follows him, until his "
            "uncle al-Ashraf Musa takes Damascus in 1229.",
        ),
    )


# -- the Syrian Nizaris --


def _site(levant: Levant, key: str, name: str, **kw: Any) -> Neighbour:
    """The place `name` if another part made it already, else a new one."""
    found = next(
        (n for n in levant.b.saga.neighbours if n.name == name and n.kind == PLACE),
        None,
    )
    if found is None:
        found = levant.b.place(name, **kw)
    levant.places[key] = found
    return found


def _nizaris(levant: Levant) -> None:
    b, w = levant.b, levant.world
    masyaf = _site(
        levant,
        "masyaf",
        "Masyaf",
        inside=levant.places.get("syria"),
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "The greatest fortress of the Syrian Nizaris, in the hills "
            "where the County of Tripoli ends on the north-east, and the "
            "seat of their chief. The sect took it with the other Syrian "
            "castles as its power spread in the twelfth century. Salah "
            "al-Din laid siege to it in 1176 and gave up, the tale goes, "
            "after he woke to find a poisoned dagger and a threat from "
            "Rashid al-Din Sinan in his tent; another story has Sinan's "
            "envoy show the sultan that his own two bodyguards would kill "
            "him on Sinan's word. After that Salah al-Din kept on good "
            "terms with Sinan. The book gives the castle no aura: a "
            "Muslim castle-town's Divine 2 is assumed.",
            "If history runs on: Baybars takes the last Syrian Nizari "
            "fortresses in 1273.",
        ),
    )
    w["syrian_nizaris"] = syrian = b.faction(
        "The Syrian Nizaris",
        faction="Other",
        decides="Its leader",
        tradition="trad_nizari_mustajibs",
        place=masyaf,
        rules="The chief at Masyaf obeys the master at Alamut, and every "
        "rafiq obeys his chief.",
        wants="Their castles kept, and any ruler who threatens them cowed",
        offers="A killing, a warning, or a ruler's ear",
        summary=paragraphs(
            "The Syrian branch of the Nizari Isma'ilis, the Assassins of "
            "the crusaders' tales, holding Masyaf and a chain of castles "
            "in the hills between the County of Tripoli and the Orontes. "
            "The name comes from hashishi, a slur their enemies used. The "
            "sect began with Hasan-i Sabbah, who seized Alamut in Persia "
            "in 1090 and backed Nizar, the Fatimid heir set aside in "
            "1094; Nizar died in prison at Alexandria, but the Nizaris "
            "hold that a grandson was smuggled to Alamut and reared "
            "there, and Alamut's masters have claimed the imamate since "
            "1162. The sect is ranked strictly under its head at Alamut; "
            "its religious leaders are called shaykh, or pir in Persian, "
            "and members call one another rafiq.",
            "Most of what is told of them comes from their enemies: that "
            "boys were raised to blind devotion, drugged and woken in a "
            "garden made to look like Paradise, then sent out with a "
            "dagger and the promise of going back. Their greatest Syrian "
            "chief, Rashid al-Din Sinan, the crusaders' Old Man of the "
            "Mountain, ruled from 1162 until about 1193 and was said to "
            "be a magician.",
            "The Assassin's dagger. A Syrian Nizari is armed with a "
            "gold-hilted, bright-bladed dagger which, when drawn, gives "
            "the man it was made for, and no other, the effect of "
            "Endurance of the Berserkers (ReCo 15 in the Definitive "
            "Edition), three times a day. Alamut's masters, who are "
            "chosen by birth and are not always magicians, cannot always "
            "make them, so the Syrian chiefs send batches east from time "
            "to time.",
            "If history runs on: the Mongols destroy the Persian "
            "strongholds in 1256, and Baybars takes the last Syrian ones "
            "in 1273.",
        ),
        secrets=paragraphs(
            "In this saga the chief of the Syrian Nizaris is always a "
            "magician. Blood and Sand makes him usually a raqi and "
            "sometimes a sahir or another tradition's man; The Cradle "
            "and the Crescent's Nizari mustajibs, renegade sahirs, are "
            "the faction's tradition here. He breeds his followers' "
            "fanatical loyalty with tricks and spells together.",
            "A shipment of daggers bound for Alamut is a prize many "
            "would want, the Order among them, and the sect will hunt "
            "down whoever holds one.",
        ),
    )
    w["masyaf_chief"] = b.lord(
        "The Old Man of the Mountain",
        title="baron",
        wealth="Average",
        seat="Masyaf",
        answers_to=w.get("imam"),
        place=masyaf,
        summary=paragraphs(
            "The da'i who leads the Syrian Nizaris from Masyaf, whom the "
            "crusaders call by the name they gave Sinan, the Old Man of "
            "the Mountain. He answers to the master at Alamut, Jalal "
            "al-Din Hasan, though Syria is far away and its chiefs have "
            "often gone their own way. The book does not name the chief "
            "of 1220.",
        ),
    )
    nizaris = w.get("nizaris")
    if nizaris is not None:
        syrian.answers_to = nizaris.id


# -- the nomads --


def _nomads(levant: Levant) -> None:
    b, w = levant.b, levant.world
    w["bedouin"] = b.faction(
        "The Bedouin",
        faction="Other",
        place=levant.places.get("levant"),
        wants="Their grazing, their wells and their freedom",
        offers="Guides across the desert, and riders in war",
        summary=paragraphs(
            "The Arab nomads of the deserts, in Syria, Sinai, Egypt and "
            "the steppe toward Iraq. Some tribes have emirs and settled "
            "lands, but many still wander as they please, outside the "
            "settled order. They trouble the rulers of the towns now and "
            "then, but mostly keep on good terms with them and send "
            "volunteers to their armies. Many are Twelver Shi'is, and "
            "spirit masters are common among their tribes. Bedouin by "
            "Giza tell of vengeful spirits in the pyramids.",
        ),
    )
    w["turcomans"] = b.faction(
        "The Turcomans",
        faction="Other",
        place=levant.places.get("asia_minor"),
        wants="Pasture, plunder and their own chiefs",
        offers="Horse archers for any prince who pays",
        summary=paragraphs(
            "The Turkish nomads who came west off the Asian steppe, "
            "grazing their herds across Asia Minor, the Jazira and the "
            "edges of Syria. Like the Bedouin, some follow emirs and have "
            "settled, while many more wander outside any ruler's order, "
            "an occasional menace to the towns and a ready source of "
            "horsemen in war.",
        ),
    )


# -- after every part has built --


def _place_in(record: Neighbour | None, place: Neighbour | None) -> None:
    if record is not None and place is not None and record.place_id is None:
        record.place_id = place.id


def finish(levant: Levant) -> None:
    b, w = levant.b, levant.world
    for key, kind, where in (*SHARED_PLACES, *OWN_PLACES):
        _place_in(w.get(key), _where(levant, kind, where))
    mosul, emir = w.get("mosul"), w.get("lord_of_mosul")
    if mosul is not None and emir is not None and mosul.place_id is not None:
        _place_in(emir, b.saga.neighbour(mosul.place_id))
    masyaf = levant.places.get("masyaf")
    if masyaf is not None and masyaf.place_id is None:
        _place_in(masyaf, levant.places.get("syria"))
    damascus = w["al_muazzam"]
    for key, note in (
        ("damascus", "His capital"),
        ("jerusalem", "His; he razed it in 1219"),
    ):
        town = w.get(key)
        if town is not None:
            b.link(damascus, "places", town, note)
    kamil = w.get("al_kamil")
    if kamil is not None:
        b.link(damascus, "places", kamil, "His brother and rival, head of the family")
    aedes = levant.covenants.get("aedes_veritatis")
    if aedes is not None:
        b.link(damascus, "covenants", aedes, "Buys its quarry stone")
    nizaris = w.get("nizaris")
    if nizaris is not None:
        b.link(w["syrian_nizaris"], "places", nizaris, "The sect they belong to")
    b.link(w["syrian_nizaris"], "places", w["masyaf_chief"], "Their chief")
