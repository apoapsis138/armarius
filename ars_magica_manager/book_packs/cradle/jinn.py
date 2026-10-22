"""The jinn (TC&TC ch04, with Golden Baghdad from ch07 and Khashgar from
ch09), in paraphrase.

East.py's world["jinn"] (the faction, its realms, peoples and
weaknesses, and the spirits that are not jinn) and its places
["jinnistan"] and ["qaf"] are shared: not remade, their text not
changed. This part adds the other four lands as places, Rumoured
(C11): places["amerabad"] (Amerabad, the City of Amber, inside
Jinnistan), ["golden_baghdad"] (the faerie reflection of the city,
inside world["baghdad"], with its ways in described), ["khashgar"]
("Khashgar of the Jinn", the faerie city behind the silk_road part's
town world["khashgar_town"], and inside it once that part has made it,
else inside places["silk_road"]) and ["al_khadar"] (the Green Ocean
beyond the known world, inside nothing); and the faerie court of
Golden Baghdad, the faerie Harun, Ja'far and Masrur, as
world["golden_court"], a faction of kind "Faerie court" seated in
Golden Baghdad. The shared faction world["jinn"] links to each of the
four lands and to the court (a link from a shared record is this
pack's to add).

Named jinn without stats (Iblis, Jaghrahaz, the marid of Zamzam) are
sentences in their places (the region parts'); jinn with stats are
bestiary.py's (C19). The jinn's story seeds are stories.py's (C22),
which can hang them on these keys."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import paragraphs

if TYPE_CHECKING:
    from . import Cradle

RUMOURED = "Rumoured"

#: Where each of this part's places sits: its key, then the keys to
#: try in turn for what holds it (another part's, or a shared one).
INSIDE: dict[str, tuple[str, ...]] = {
    "amerabad": ("jinnistan",),
    "golden_baghdad": ("baghdad", "iraq", "mesopotamia"),
    "khashgar": ("khashgar_town", "silk_road"),
}


def build(cradle: Cradle) -> None:
    _lands(cradle)
    _golden_court(cradle)
    _links(cradle)
    _settle(cradle)


def finish(cradle: Cradle) -> None:
    """Put a land still nowhere in the town or region another part has
    made since."""
    _settle(cradle)


def _settle(cradle: Cradle) -> None:
    for key, holders in INSIDE.items():
        place = cradle.places.get(key)
        if place is None or place.place_id is not None:
            continue
        held = next(
            (found for k in holders if (found := cradle.find(k)) is not None), None
        )
        if held is not None:
            place.place_id = held.id


# -- the lands --


def _lands(cradle: Cradle) -> None:
    b = cradle.b
    cradle.places["amerabad"] = b.place(
        "Amerabad, the City of Amber",
        realm="Faerie",
        status=RUMOURED,
        summary=paragraphs(
            "One of the whole cities the jinn keep inside the shifting "
            "borders of Jinnistan, and the one the tales name first. The "
            "book gives it only that line: its streets, rulers and ways "
            "in are the storyguide's to make.",
        ),
    )
    cradle.places["golden_baghdad"] = b.place(
        "Golden Baghdad",
        realm="Faerie",
        status=RUMOURED,
        summary=paragraphs(
            "The faerie reflection of Baghdad as it was under Harun "
            "al-Rashid, its greatest caliph: roofs of gold, streets of "
            "marble, and the tales of the Thousand and One Nights played "
            "out again and again, whether or not a visitor joins in. A "
            "traveller may overhear Sinbad the Sailor telling his voyages "
            "to Sinbad the Porter, go fishing with Judar, ride out beyond "
            "the walls in search of Solomon's ring with Bulukiyya, or "
            "help Hasan the goldsmith of Basra win a jinn bride; he may "
            "even find himself living one of those parts. Its bazaars "
            "sell the hidden folk's kohl, seldom for coin. The poet Abu "
            "Nuwas, once of Harun's court, lives on here as a creature of "
            "the tales.",
            "Its ways in are scattered all over mundane Baghdad. One may "
            "be an ordinary doorway that happens to open onto it, another "
            "a gate only Second Sight, Faerie Sight or a like power can "
            "see, and where the Guardian is part of the Threshold a "
            "visitor can cross into Faerie without noticing. So many "
            "Baghdadis stray across by accident that it counts in the "
            "city as a fair excuse for being missed, and most of them "
            "have been there at least once. The Order of Suleiman has "
            "tried to chart the entrances, but they open, close and move "
            "as they please and differ for each traveller, so only a few "
            "steady ones are known for sure. Sahirs still argue whether "
            "the strange beings met in the mundane city belong there or "
            "have wandered out of the golden one.",
        ),
    )
    cradle.places["khashgar"] = b.place(
        "Khashgar of the Jinn",
        realm="Faerie",
        status=RUMOURED,
        summary=paragraphs(
            "The legendary oasis city where the roads from north and south "
            "meet before they part around the Taklimakan for the Land of "
            "Silk, and the best known of all the cities of the eastern "
            "journey. Scholars quarrel over where and what it is, but "
            "agree that men, jinn and other eastern faeries crowd its "
            "streets beside angels, demons and sorcerers of every "
            "tradition but the Hermetic. Its Sunday market, the "
            "Yekshenbar bazaar, sells anything at all: brigands and tired "
            "merchants trade silks, knives and jewels beside magical "
            "wares, and slaves, ordinary and otherwise, are to be had for "
            "a price.",
            "Muslim in name since the late ninth century, it suffered "
            "under the faerie Qara Khitai and has lately passed to the "
            "Mongols without a fight; neither its human nor its magical "
            "people seem to mind the change of masters. Merinita who say "
            "they reached its market through Arcadia think several "
            "Khashgars may stand at once, or that the whole town lies in "
            "a regio with doors at many places in the mundane world. Its "
            "traders pay the scholars no heed.",
        ),
    )
    cradle.places["al_khadar"] = b.place(
        "Al-Khadar, the Green Ocean",
        status=RUMOURED,
        summary=paragraphs(
            "The great ocean beyond the ring of the known world, past "
            "the pale blue seas off Persia and past the merchants' "
            "Erythraean Sea: a wall of magic and of metaphor that only "
            "jinn, heroes, sorcerers and Muslim saints have crossed. Few "
            "claim to have reached its far shores, or its drifting "
            "islands with their trees bearing human heads and their "
            "thinking apes, and those who say they came back tell of it "
            "in parables and lies, as Sinbad the Sailor did.",
            "Islamic cosmology puts whole worlds out beyond it, peopled by "
            "terrible angels, strange men, outlandish jinn and stranger "
            "things still. Hermetic scholars of the Keepers of Tales "
            "place those lands in Eudokia, in the Faerie realm, while "
            "Criamon magi read the tale of Buluqya as a road into the "
            "Magic Realm that leads out of the Circle of Time.",
        ),
    )


# -- the court of Golden Baghdad --


def _golden_court(cradle: Cradle) -> None:
    cradle.world["golden_court"] = cradle.b.faction(
        "The Court of Golden Baghdad",
        faction="Faerie court",
        decides="Its leader",
        ruler="the faerie Harun al-Rashid",
        realm="Faerie",
        place=cradle.places["golden_baghdad"],
        wants="Visitors who can add something to the glory of his city.",
        offers="Reward for the good, punishment for the wicked, and a "
        "place in the tales.",
        summary=paragraphs(
            "The faerie caliph of Golden Baghdad and his two companions: "
            "a Harun al-Rashid, with Ja'far the Barmakid, his vizier, and "
            "Masrur the eunuch, his executioner, who go about the city at "
            "night in disguise to see how its people behave, rewarding "
            "the good and punishing the wicked, and who may call on a "
            "guest after dark.",
            "Sahirs have told of meeting him since a few years after the "
            "real caliph died in 809. It begins harmlessly, with a talk "
            "with three strangers, and usually turns into a wild "
            "adventure across the Threshold. Many sahirs take him for "
            "the faerie ruler of the golden city, who invites only those "
            "he judges able to do something for its good.",
        ),
    )


# -- links from the shared faction --


def _links(cradle: Cradle) -> None:
    b = cradle.b
    jinn = cradle.world.get("jinn")
    if jinn is None:
        return
    for key, note in (
        ("amerabad", "Their City of Amber, in Jinnistan"),
        ("golden_baghdad", "Their bazaars there"),
        ("khashgar", "Their city on the Silk Road"),
        ("al_khadar", "The ocean only they cross freely"),
    ):
        b.link(jinn, "places", cradle.places[key], note)
    b.link(
        jinn, "places", cradle.world["golden_court"], "The faerie court of the tales"
    )
    b.link(
        cradle.world["golden_court"],
        "places",
        cradle.places["golden_baghdad"],
        "Its city",
    )
