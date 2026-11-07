"""The Order of Suleiman's own records (TC&TC ch03, with the houses the
regional chapters name): its families, its houses of wisdom as
covenants with no Tribunal, its sahirs, the Majlis and its hall, and
the one printed stat block.

The Order itself and its Stone and River families are east.py's shared
records (world["order"], ["stone"], ["river"]): not remade, and their
text not changed. This part adds the other four groups as factions of
the kind "Family", each answering to the Order and naming the Sahirs
tradition: world["star"] (Ashab al-Najm, Meriq its Asala), ["hand"]
(Ashab al-Yad), ["heart"] (Ashab al-Qalb) and ["circle"] (Ashab
al-Halqa, the unrecognised sixth, with HoH:S's Hermetic Sahirs named
in its summary). The feud with the Nizaris (world["nizaris"]) is a
link from the Order (C14).

Places: places["majlis_hall"] (the hidden six-sided hall in Baghdad's
summer bazaar, world["baghdad"]), ["island_fortress"] (the grand
vizier's stronghold in the Magic Realm, Rumoured, the oubliette in its
secrets), ["house_of_the_heavens"] (the Star family's empty seat at
Nasibin, a place and not a covenant, C5), ["savah_observatory"] (Magic
5, inside Savah's tower) and ["house_of_healing"] (Gundeshapur's
academy: Divine above, Magic pockets below as a regio level).

Covenants (C5): sketches covenants["dar_al_hikma"] (Baghdad, the First
Council's academy, about a hundred sahirs, Niya its vizier),
["bayt_savah"] (the Star family's house, in the observatory) and
["bayt_gundeshapur"] (the House of Healing, the Hand family's); line
records ["dayr_qunna"], ["bayt_sanaa"], ["bayt_muscat"],
["bayt_nizwa"], ["bayt_merv"], ["bayt_nishapur"], ["bayt_bukhara"],
["bayt_ramhurmuz"], and the Stone's and River's seats ["bayt_damascus"]
and ["bayt_cairo"], which have no place record, their towns being
outside the book's lands (C5 as revised). None has a Tribunal. A house
is put in its town or site (the region parts' keys in SITES) in build,
or in finish when that part had not made it yet.

People, companions of the Sahirs tradition (C6 as revised), with The
Gift where the book says so: people["khatrazh"] (Kha'trazh, the grand
vizier, of no house), ["niya"] (Dar al-Hikma), ["meriq"] (Savah),
["nil"] (Gundeshapur, his Nizari ties in secrets=) and ["arkhaman"]
('Arkhaman, vizier of Sana'a, entered as printed in `stats`, with
Kharrat, creatures["kharrat"], as his bound jinni and his seven spells
as tradition effects; C9, C10).

'Umar Khayyam's books are Book records of the Nishapur house he led
(C18). The Majlis of each August is a calendar entry (C4). The Order's
history is history.py's (C3), in the Dar al-Hikma's Diary."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..builder import Builder, Secrets, StatBlock, _virtue_flaw, paragraphs, titled
from ..east import SAHIRS

if TYPE_CHECKING:
    from ...models import Character, Covenant
    from . import Cradle

#: The book's sahirs are companions: a "magus" is Hermetic (C6).
COMPANION = "companion"
#: Where the region parts put each house's town or site, by covenant key
#: (a key of theirs, or one of this part's places).
SITES: dict[str, str] = {
    "dar_al_hikma": "baghdad",
    "bayt_savah": "savah_observatory",
    "bayt_gundeshapur": "house_of_healing",
    "dayr_qunna": "al_madain",
    "bayt_sanaa": "sanaa",
    "bayt_muscat": "muscat",
    "bayt_nizwa": "nizwa",
    "bayt_merv": "merv",
    "bayt_nishapur": "nishapur",
    "bayt_bukhara": "bukhara",
    "bayt_ramhurmuz": "ramhurmuz",
}
#: Where each of this part's places sits: its own key, the key of what
#: holds it.
INSIDE: dict[str, str] = {
    "majlis_hall": "baghdad",
    "house_of_the_heavens": "nasibin",
    "savah_observatory": "savah",
    "house_of_healing": "gundeshapur",
}
#: Each house's family, by covenant key.
FAMILIES: dict[str, str] = {
    "dar_al_hikma": "heart",
    "bayt_savah": "star",
    "bayt_gundeshapur": "hand",
    "bayt_muscat": "river",
    "bayt_damascus": "stone",
    "bayt_cairo": "river",
}


def build(cradle: Cradle) -> None:
    _families(cradle)
    _places(cradle)
    _houses(cradle)
    _sahirs(cradle)
    _books(cradle)
    _majlis(cradle)
    _settle(cradle)


def finish(cradle: Cradle) -> None:
    """Put whatever house or place is still nowhere in the site another
    part has made since."""
    _settle(cradle)


# -- the families --


def _families(cradle: Cradle) -> None:
    b = cradle.b
    order = cradle.world["order"]
    cradle.world["star"] = b.faction(
        "Ashab al-Najm, the Followers of the Star",
        faction="Family",
        decides="Its leader",
        ruler="Meriq, the Asala al-Najm",
        tradition=SAHIRS,
        summary=paragraphs(
            "The family of Solomonic Astrology. It began with a handful of "
            "Zoroastrian converts who came to Baghdad to learn from "
            "al-Khwarizmi, al-Fazari's pupil, and went on to found a "
            "small academy at Nasibin in the north and houses given "
            "wholly to the stars in many Persian cities. It is the most "
            "widespread of the families and the most arcane: its sahirs "
            "look and dress the part of the wise magician, and hold that "
            "magic must keep its grandeur in the people's eyes even as "
            "it serves them.",
            "Its seat, the House of the Heavens at Nasibin, emptied in "
            "1186 when its Asala and vizier led every sahir of the city "
            "away; the family's astrologers have since travelled in "
            "caravans with their laboratories, most of them still in "
            "Jazira. Meriq of Savah has led it since.",
        ),
    )
    cradle.world["hand"] = b.faction(
        "Ashab al-Yad, the Followers of the Hand",
        faction="Family",
        decides="Its leader",
        ruler="the Asala al-Yad",
        tradition=SAHIRS,
        summary=paragraphs(
            "The family of Solomonic Physic, begun by the Bakhtyshu "
            "physicians, who carried their art to Gundeshapur and its "
            "House of Healing. Its first members were Nestorian "
            "Christians, and it has always taken in Muslims, Jews and "
            "pagans alike; that openness has given it a poor name among "
            "the sahirs, who see in it a family that can harm as readily "
            "as it heals, and never quite know which a Follower of the "
            "Hand will do.",
        ),
    )
    cradle.world["heart"] = b.faction(
        "Ashab al-Qalb, the Followers of the Heart",
        faction="Family",
        decides="Its leader",
        ruler="the Asala al-Qalb",
        tradition=SAHIRS,
        summary=paragraphs(
            "The family of Solomonic Storytelling. Al-Zill Habib, the "
            "'beloved shadow', founded it, but so little is known of him "
            "that its sahirs look instead to al-Khayzuran as their "
            "mother and model. Its art has stayed rooted in Baghdad, the "
            "city of a thousand tales, and most grand viziers have come "
            "from it, Kha'trazh among them. Its sahirs are political, "
            "deal with faeries and magical beings more than the other "
            "families do, are seldom Gifted, and are nearly as often "
            "women as men.",
            "Its Asala is old; Niya of the Dar al-Hikma is expected to follow him.",
        ),
    )
    cradle.world["circle"] = b.faction(
        "Ashab al-Halqa, the Followers of the Circle",
        faction="Family",
        decides="Nobody",
        tradition=SAHIRS,
        wants="A sixth Asala, and Sihr counted as a sixth Solomonic art.",
        summary=paragraphs(
            "Not a recognised family but a name for sahirs who follow "
            "none of the five arts, or who put their summoning first. "
            "The sahirs of Cordoba used it before they left the Order, "
            "after the rim of the pentacle in Solomon's Seal. Most "
            "Gifted sahirs and self-taught summoners count among them; "
            "they keep away from the Majlis, where viziers of the other "
            "families must speak for them. Some draw the Seal with six "
            "points, to claim Sihr as a sixth art and their own, and a "
            "movement among them asks for a sixth Asala.",
            "The Cordoban sahirs who joined the Order of Hermes in 925 "
            "are the Hermetic Sahirs of Houses of Hermes: Societates, "
            "Followers of the Circle within House Ex Miscellanea.",
        ),
    )
    for key in ("star", "hand", "heart", "circle"):
        family = cradle.world[key]
        family.answers_to = order.id
        note = "Unrecognised" if key == "circle" else "One of the five families"
        b.link(order, "places", family, note)
    nizaris = cradle.world.get("nizaris")
    if nizaris is not None:
        b.link(order, "places", nizaris, "Feud: traitors to the Order")


# -- places --


def _places(cradle: Cradle) -> None:
    b = cradle.b
    cradle.places["majlis_hall"] = b.place(
        "The Hall of the Majlis",
        status="Rumoured",
        summary=paragraphs(
            "A great six-sided hall at the heart of Baghdad's summer "
            "bazaar, where the Order of Suleiman meets. Magic hides it: "
            "from outside it is only a cluster of bright tents that "
            "always seem further off, and spirits the Asalat summon "
            "guard it. Within, tiers of cushions, lamps and fans descend "
            "in six steps, one for each family, under a ceiling that "
            "shows the open heavens; conjured servants carry food and "
            "drink, and on the stage at the centre, inlaid with a golden "
            "pentacle, the grand vizier sits on a jewelled throne.",
            "When autumn comes the fair packs up and the district is "
            "left looking like rubble; the local sahirs keep that "
            "illusion up all year so that no one stumbles on the hall, "
            "and the few traders who stay are in the secret.",
        ),
    )
    cradle.places["island_fortress"] = b.place(
        "The Grand Vizier's Island Fortress",
        status="Rumoured",
        summary=paragraphs(
            "A stronghold of stone in the Magic Realm, on an island far "
            "out in a cold, empty sea. Sahirs who have met Hermetic magi "
            "are brought here to talk with the grand vizier in private, "
            "since the war is never discussed at the Majlis, where the "
            "enemy might be listening.",
        ),
        secrets=[
            titled(
                "The Order's prison",
                "A pit at the centre of the Grand Vizier's Island Fortress "
                "is the Order of Suleiman's prison.",
            ),
            titled(
                "The Oubliette al-Wazir",
                "The grand vizier is said to hold an Arcane Connection to "
                "the prison pit in his Island Fortress, and a Travel ritual "
                "of level 45, the Oubliette al-Wazir, opens a way straight "
                "there without crossing the Twilight Void, so a traitor can "
                "be sent into exile with no one the wiser.",
            ),
        ],
    )
    cradle.places["house_of_the_heavens"] = b.place(
        "The House of the Heavens",
        summary=paragraphs(
            "For most of the Order's life the seat of the Followers of "
            "the Star: five great buildings of white stone set round a "
            "sixth with an observatory and astrolabe, and in the "
            "courtyard between them a procession of statues of the old "
            "Babylonian figures for the planets and the signs.",
            "Late in the summer of 1186, soon after its vizier and the "
            "Asala al-Najm came home from the Majlis, every sahir of "
            "Nasibin left together. Some had packed beforehand; others "
            "walked away from unfinished work. Astrologers reckon that "
            "all seven planets then stood in Libra, a sign of subtlety, "
            "independence and help given to others. Neither leader has "
            "been heard of since. Most sahirs think they went to help "
            "Salah al-Din at Hattin and the taking of Jerusalem in 1187; "
            "others that they set out to be rid of Rashid al-Din Sinan, "
            "the Syrian Nizaris' chief. The houses stand empty.",
            "Meriq, the family's Asala, insists that this is still the "
            "family's house and that those who left will come back to it.",
        ),
        secrets=[
            titled(
                "Storyguide Notes",
                "The book leaves why the sahirs of Nasibin went, and whether "
                "Meriq is right, to the storyguide.",
            ),
        ],
    )
    cradle.places["savah_observatory"] = b.place(
        "The Observatory of Savah",
        aura=5,
        summary=paragraphs(
            "The top of the tall domed tower beside Savah's great "
            "mosque, above the library, kept by Savah's house of wisdom. "
            "It is famous across the world for its star maps, from old "
            "Babylon to the present day, and for the newest instruments "
            "of the astronomers. Besides its Magic aura of 5, it gives +3 "
            "to every astrology roll, Solomonic Astrology included.",
        ),
    )
    cradle.places["house_of_healing"] = b.place(
        "The Halls of the House of Healing",
        realm="Divine",
        aura=4,
        levels=[
            Builder.level(
                "The laboratories beneath",
                3,
                notes="Rooms dug deep under the house, where buried "
                "pockets of Magic let the sahirs work; long, narrow "
                "ladders lead down to them from the common rooms.",
            )
        ],
        summary=paragraphs(
            "Gundeshapur's great medical school and hospital, founded by "
            "the sahir Bakhtyshu of Harun's council and run ever since "
            "by his descendants; the Seljuk sultans paid for it and the "
            "Khwarazm-shah still honours it. A palatial building near the "
            "middle of the town, open on every side under canvas porches "
            "on wooden columns, with a great hall ringed by a corridor "
            "like a cloister and windows showing the tales of the First "
            "Council, which townsfolk take for Christian legends.",
            "A Divine aura lies over the whole house, so its sahirs have "
            "dug their laboratories far below.",
        ),
    )
    cradle.b.link(
        cradle.world["order"],
        "places",
        cradle.places["majlis_hall"],
        "Its council's hall",
    )
    cradle.b.link(
        cradle.world["order"],
        "places",
        cradle.places["island_fortress"],
        "The grand vizier's stronghold",
    )
    cradle.b.link(
        cradle.world["star"],
        "places",
        cradle.places["house_of_the_heavens"],
        "Its old seat",
    )


# -- the houses of wisdom --


def _houses(cradle: Cradle) -> None:
    b = cradle.b
    cradle.covenants["dar_al_hikma"] = b.covenant(
        "Dar al-Hikma",
        founded=787,
        season="Summer",
        aura=4,
        realm="Divine",
        unnamed_magi=99,
        summary=paragraphs(
            "The Followers of the Heart's great academy in Baghdad and the "
            "Order of Suleiman's first house: the house where the First "
            "Council studied and taught grew into it after 805. It "
            "stands north of the caliph's palace, halfway between the Bab "
            "al-Sham and the Bab al-Khurasan, a building as grand as the "
            "Golden Gate palace and mosque, and nearly a hundred sahirs, "
            "young and old, live and study there. Its observatory is "
            "exceptional, with perhaps the best astrolabe yet made.",
            "Baghdad has seven other houses of wisdom besides, and about a "
            "thousand sahirs in all, more than any other city. The house "
            "chooses its leader, and so its vizier at the Majlis, by what "
            "its members achieve; by custom its vizier acts as grand "
            "vizier when the seat falls empty between meetings.",
        ),
        what_matters=paragraphs(
            "Library: the Order's oldest, its contents not given in the book.",
            "Tension: Niya's views make her succession to the acting "
            "grand vizier's place, should Kha'trazh die, hard to hold.",
        ),
    )
    cradle.covenants["bayt_savah"] = b.covenant(
        "The House of Wisdom of Savah",
        founded=None,
        season="Autumn",
        summary=paragraphs(
            "The Followers of the Star's house in Savah, a town of "
            "camel-drivers and herdsmen, where every sahir is of that "
            "family. It keeps the tall domed tower attached to the great "
            "mosque and its hospital: the library on the lower floors, "
            "the best magical library in Persia, and the observatory at "
            "the top. Meriq, the family's Asala, is of this house.",
        ),
        what_matters=paragraphs(
            "Library: the finest collection of magic in Persia, with "
            "Meriq's own books on Artes Liberales and Solomonic "
            "Astrology; the book gives no scores.",
            "Site: its observatory, Magic 5, gives +3 to astrology.",
        ),
    )
    cradle.covenants["bayt_gundeshapur"] = b.covenant(
        "The House of Healing",
        founded=None,
        season="Summer",
        summary=paragraphs(
            "The Followers of the Hand's academy at Gundeshapur and the "
            "town's largest house of wisdom: its great medical school "
            "and hospital, run by the descendants of its founder "
            "Bakhtyshu. Its sahirs work in laboratories dug far below, "
            "out of the Divine aura that covers the house.",
            "Nizari visitors have come to see its vizier, Nil, here more than once.",
        ),
        what_matters=paragraphs(
            "Tension: the Order suspects its vizier of Nizari sympathies.",
        ),
    )
    lines = (
        (
            "dayr_qunna",
            "Dayr Qunna",
            "Summer",
            "A house of wisdom a mile east of Dayr al-'Aqul, near "
            "al-Mada'in, posing as a Nestorian monastery: a large "
            "building behind walls so high and strong it looks a "
            "fortress. Its sahirs and their followers live as monks and "
            "are posted there to watch the caliphs. The townsfolk of "
            "Dayr al-'Aqul, who suffer some hidden enemy, wonder whether "
            "its 'monks' are sorcerers.",
        ),
        (
            "bayt_sanaa",
            "The House of Wisdom of Sana'a",
            "Summer",
            "The house in Sana'a where 'Arkhaman was born in secret and "
            "raised. Its older sahirs have made him their vizier and are "
            "sending him to the Majlis this summer, hoping he will meet "
            "other Gifted sahirs before his Gift drives him mad.",
        ),
        (
            "bayt_muscat",
            "The House of Wisdom of Muscat",
            "Spring",
            "A large company of sahirs of Solomonic Travel in Muscat, "
            "the port lately taken from the 'Abbasids by the Yahmad "
            "tribe, whose house is given to finding the fabled islands "
            "of Sinbad the Sailor's voyages.",
        ),
        (
            "bayt_nizwa",
            "The Houses of Wisdom of Nizwa",
            "Summer",
            "Several houses of sahirs in Nizwa, the royal city of 'Uman, "
            "and the country round it, taken here as one record. Nizwa "
            "also has a name for witches and sorcerers, who are not of "
            "the Order.",
        ),
        (
            "bayt_merv",
            "The House of Wisdom of Merv",
            "Autumn",
            "The house in Merv, keeper of the magical library of Nizam "
            "al-Mulk, the Seljuk grand vizier, among the city's famous "
            "libraries. Taught by the Ghuzz sack and fearing Genghis "
            "Khan, its sahirs are copying every irreplaceable book they "
            "can, since the colleges and madrasas will not move theirs.",
        ),
        (
            "bayt_nishapur",
            "The House of Wisdom of Nishapur",
            "Autumn",
            "The house where Hasan-i Sabbah, Nizam al-Mulk and 'Umar "
            "Khayyam learnt the Solomonic arts. 'Umar later led it, "
            "until his death in 1123, and his books are in its keeping.",
        ),
        (
            "bayt_bukhara",
            "The House of Wisdom of Bukhara",
            "Winter",
            "Bukhara's own house of wisdom, which paid for the new "
            "mausoleum over Job's Spring at the edge of the farmers' "
            "market; one of its sahirs visits the spring each year. As "
            "1220 opens, Genghis Khan's horde is before the town.",
        ),
        (
            "bayt_ramhurmuz",
            "The House of Wisdom of Ramhurmuz",
            "Autumn",
            "A few sahirs in Ramhurmuz, a rich town of silk and perfume, "
            "with a modest library. Long ago they took in a sorcerer of "
            "Soqotra, learnt his island's secrets and perfumes and made "
            "a trade of them; when he saw he had been cheated he left a "
            "curse behind, and the district swarms with gnats and biting "
            "midges every year.",
        ),
        (
            "bayt_damascus",
            "The House of Wisdom of Damascus",
            "Summer",
            "The seat of the Followers of the Stone at Damascus, outside "
            "this book's lands and the heart of the sahirs' war on the "
            "crusaders and their magi. The town is the Levant pack's to "
            "describe; this record has no place.",
        ),
        (
            "bayt_cairo",
            "The House of Wisdom of Cairo",
            "Summer",
            "The great academy of the Followers of the River at Cairo, "
            "outside this book's lands and still the centre of the "
            "family's art; the city once sent twelve viziers to a single "
            "Majlis. The town is the Levant pack's to describe; this "
            "record has no place.",
        ),
    )
    for key, name, season, summary in lines:
        # A house in a city takes the book's Divine 4 for a city with no
        # aura given; the walled 'monastery' of Dayr Qunna, outside one,
        # takes Magic 3, the pack's value for a magical site the book
        # leaves unnumbered, since sahirs would not settle where there
        # is no aura at all.
        town = key != "dayr_qunna"
        cradle.covenants[key] = b.covenant(
            name,
            founded=None,
            season=season,
            summary=summary,
            aura=4 if town else 3,
            realm="Divine" if town else "Magic",
        )
    for key, family in FAMILIES.items():
        b.link(cradle.covenants[key], "places", cradle.world[family], "Its family")


# -- the sahirs --


def _sahir(
    cradle: Cradle,
    key: str,
    name: str,
    *,
    covenant: Covenant | None,
    age: int | None,
    summary: str,
    secrets: Secrets = "",
    gifted: bool = False,
    vizier: bool = False,
) -> Character:
    person = cradle.b.magus(
        name,
        covenant=covenant,
        house="",
        age=age,
        summary=summary,
        type=COMPANION,
        traditions=[SAHIRS],
        secrets=secrets,
    )
    names = ["The Gift"] * gifted + ["Sahir"] + ["Vizier"] * vizier
    person.virtues_flaws = [_virtue_flaw(n) for n in names]
    cradle.people[key] = person
    return person


def _sahirs(cradle: Cradle) -> None:
    b, world, covenants = cradle.b, cradle.world, cradle.covenants
    khatrazh = _sahir(
        cradle,
        "khatrazh",
        "Kha'trazh al-Wazir al-Dall Ariq al-Qalb",
        covenant=None,
        age=97,
        vizier=True,
        summary=paragraphs(
            "Grand vizier of the Order of Suleiman for nearly thirty "
            "years, a Follower of the Heart from Basra. He is calm and "
            "quiet and weighs every word; no one thinks him especially "
            "clever or strong, and he lacks The Gift. He took the laqab "
            "al-Wazir al-Dall, 'the dignified vizier', as a promise not "
            "to abuse his place. The viziers keep electing him because "
            "he heeds them, hears out anyone who wants to speak, and "
            "stays on fair terms with all five Asalat. Close to a "
            "hundred years old, he looks barely fifty, and many expect "
            "him to die soon.",
            "He avoids open conflict with the Order of Hermes for now. At "
            "the Majlis he holds formal council the first evening, into "
            "the night and all the next day, keeping the hardest matters "
            "for the second evening after dinner, and does not mind who "
            "dozes.",
        ),
    )
    khatrazh.aging.apparent_age = 50
    niya = _sahir(
        cradle,
        "niya",
        "Niya al-Waziriyya al-Jabr Satefa al-Inshai al-Qasri al-Qalb",
        covenant=covenants["dar_al_hikma"],
        age=35,
        gifted=True,
        vizier=True,
        summary=paragraphs(
            "Vizier of the Dar al-Hikma, a Gifted sahira of the Heart. "
            "She has found a way of joining her Solomonic arts that "
            "gives her two spells of her own: one calls a spirit straight "
            "out of the Magic Realm, the other many spirits at once. For "
            "that the house chose her to lead it, young as she is and "
            "Gifted though she is, and she is likely to be the next Asala "
            "al-Qalb when the present one dies.",
            "She holds that the Order has stagnated and that its Gifted "
            "members are its best hope of surviving, a view few share: "
            "under a tenth of the sahirs are Gifted, and those are not "
            "much liked. If Kha'trazh dies between meetings she would act "
            "for him by custom, and is unlikely to keep the post at the "
            "vote.",
        ),
    )
    meriq = _sahir(
        cradle,
        "meriq",
        "Meriq al-Asala al-Qalani al-Safar al-Najm",
        covenant=covenants["bayt_savah"],
        age=75,
        summary=paragraphs(
            "The Asala al-Najm, head of the Followers of the Star, a "
            "wizened old man of Savah best known for a hat that seems to "
            "be on inside out; his head, he jokes, sits on his hat. When "
            "the last Asala vanished from Nasibin in 1186 Meriq put "
            "himself forward, and the astrologer-viziers, having asked "
            "the stars, accepted him. Many now think he takes the "
            "charge too lightly, but no one asks him to go.",
            "He is unGifted, a fine communicator, and the author of many "
            "good books on Artes Liberales, Solomonic Astrology and "
            "more. He maintains that the House of the Heavens at Nasibin "
            "is still the family's home.",
        ),
    )
    nil = _sahir(
        cradle,
        "nil",
        "Nil al-Wazir al-Salih al-Yad",
        covenant=covenants["bayt_gundeshapur"],
        age=None,
        vizier=True,
        summary=paragraphs(
            "Vizier of the House of Healing at Gundeshapur, a Follower of "
            "the Hand born to a Christian family, who took Islam after he "
            "joined the Order. He is a great historian of the Middle "
            "East and knows Europe's past as well. He is no great "
            "healer, to his family's disappointment, and prefers "
            "Solomonic Storytelling; his singing voice is said to "
            "enchant. The accusations made against him at the Majlis do "
            "not seem to trouble him.",
        ),
        secrets=[
            titled(
                "Nil and the Nizaris",
                "Many believe he is far too close to the Nizaris, some of "
                "whom have called on him at the House of Healing.",
            ),
            titled(
                "Storyguide Notes",
                "How close Nil is to the Nizaris, the book does not say.",
            ),
        ],
    )
    arkhaman = _sahir(
        cradle,
        "arkhaman",
        "'Arkhaman Laqy al-Hayz al-Nahr",
        covenant=covenants["bayt_sanaa"],
        age=25,
        summary=paragraphs(
            "A young sahir of the River, vizier of the house at Sana'a. "
            "His mother, niece of the imam, bore him in secret at the "
            "house to keep him from her uncle, and said his father was a "
            "black-eyed jinni of flame. Raised by the sahirs, he wanted "
            "only to serve them, and as he grew to look like his "
            "mother's family they brought him into the Order. The first "
            "spirit he summoned was Kharrat, the Infernal jinni he "
            "believes to be that father, whom he has kept in hand with "
            "vis so far.",
            "His Gift came late, and its power has made him wild: one "
            "spell leads him to cast another, and his taint unsettles "
            "those without The Gift. His masters fear he will go mad "
            "without Gifted company, so they have made him vizier and are "
            "sending him to Baghdad this summer. He is pale, with black "
            "hair, thin brows and a curled moustache, an innocent "
            "twinkle and a confident smile, a hooded robe that has "
            "hardly travelled, and usually a seat.",
        ),
        secrets=[
            titled(
                "Kharrat's plan for 'Arkhaman",
                "Kharrat is sure that the boy's longing for a father's "
                "approval will carry him into evil, and means to bind him to "
                "a duty to go and find his mother, whose shame the spirit "
                "would relish.",
            ),
        ],
    )
    b.link(world["order"], "characters", khatrazh, "Grand vizier")
    b.link(world["heart"], "characters", khatrazh, "His family")
    b.link(world["heart"], "characters", niya, "Likely next Asala")
    b.link(world["star"], "characters", meriq, "Asala")
    b.link(world["hand"], "characters", nil, "His family")
    b.link(world["river"], "characters", arkhaman, "His family")
    b.link(covenants["dar_al_hikma"], "characters", niya, "Vizier")
    b.link(covenants["bayt_gundeshapur"], "characters", nil, "Vizier")
    b.link(covenants["bayt_sanaa"], "characters", arkhaman, "Vizier")
    nizaris = world.get("nizaris")
    if nizaris is not None:
        b.link(nil, "places", nizaris, "Suspected ties")


# -- 'Umar Khayyam's books --


def _books(cradle: Cradle) -> None:
    b = cradle.b
    house = cradle.covenants["bayt_nishapur"]
    author = "'Umar Khayyam"
    b.book(
        house,
        "Treatise on Demonstration of Problems of Algebra",
        "Ability Summa",
        ability="Artes Liberales",
        level=5,
        quality=9,
        language="Arabic",
        author=author,
        description="'Umar's algebra.",
    )
    b.book(
        house,
        "Explanations of the Difficulties in the Postulates of Euclid",
        "Ability Tractatus",
        ability="Artes Liberales",
        quality=10,
        language="Arabic",
        author=author,
        description="'Umar on Euclid's postulates.",
    )
    for ability in ("Artes Liberales", "Solomonic Astrology"):
        b.book(
            house,
            f"Map of the Stars ({ability})",
            "Ability Tractatus",
            ability=ability,
            quality=11,
            language="Arabic",
            author=author,
            description="One book that serves as a tractatus on both Artes "
            "Liberales and Solomonic Astrology; its beautiful illustrations "
            "add 1 to its Quality, counted here.",
        )
    b.book(
        house,
        "Rubaiyat",
        "Ability Summa",
        ability="Philosophiae",
        level=4,
        quality=9,
        language="Persian",
        author=author,
        description="'Umar's quatrains, his best-known work.",
    )


# -- the Majlis --


def _majlis(cradle: Cradle) -> None:
    cradle.b.calendar(
        "The Majlis al-Sulayman",
        1220,
        "Summer",
        repeats="Each year",
        note=paragraphs(
            "The Order of Suleiman's council meets in its hidden hall in "
            "Baghdad's summer bazaar for three days: from dusk on the day "
            "the sun passes from Leo into Virgo, as its astrologers "
            "reckon to match the First Council, breaking up before dusk "
            "of the third day; in 1220 that is 15 to 17 August. Only "
            "viziers sit, each vouched for by an Asala, with one vote "
            "apiece, usually given by acclaim or a show of hands; all "
            "five Asalat must be present, and they settle ties and "
            "disputed votes. The new grand vizier's first act is to "
            "confirm the judgements made since the last meeting.",
        ),
    )


# -- where things sit --


def _settle(cradle: Cradle) -> None:
    """Put each house and place in its site once a part has made it."""
    for key, site in INSIDE.items():
        place = cradle.places.get(key)
        held = cradle.find(site)
        if place is not None and place.place_id is None and held is not None:
            place.place_id = held.id
    for key, site in SITES.items():
        covenant = cradle.covenants.get(key)
        held = cradle.find(site)
        if covenant is not None and covenant.place_id is None and held is not None:
            covenant.place_id = held.id


# -- the printed stat block --

#: 'Arkhaman's block (TC&TC ch03). His seven spells are naranj and one
#: summoning, as tradition effects: name, rule, art, level, Penetration,
#: what it does.
ARKHAMAN_EFFECTS = (
    (
        "Kharrat, the braggart",
        "Summoning",
        "Sihr",
        10,
        12,
        "Summons Kharrat (Infernal Might 10) by his name.",
    ),
    (
        "What are the words that surround [Target]?",
        "Naranj",
        "Solomonic Astrology",
        15,
        7,
        "Detail: Thorough, Ritual. While his spirit keeps it up he hears "
        "everything spoken near the target, without being there.",
    ),
    (
        "[Spirit], his arms wide",
        "Naranj",
        "Solomonic Storytelling",
        10,
        7,
        "Allure: Simple. Listeners grasp a brief message carried in his "
        "voice, whatever their language.",
    ),
    (
        "Make their eyelids heavy and their heads to fall",
        "Naranj",
        "Solomonic Storytelling",
        15,
        7,
        "Allure: Supernatural. Everyone in earshot falls into a natural "
        "sleep; supernatural perception may resist.",
    ),
    (
        "Through the gray haze",
        "Naranj",
        "Solomonic Travel",
        20,
        14,
        "Delay: Sun. At dawn or dusk opens a way through a regio "
        "boundary of up to the spell's magnitude + 3.",
    ),
    (
        "[Spirit] brings the curse of Bayna",
        "Naranj",
        "Solomonic Travel",
        25,
        14,
        "Delay: Immediate. A target he touches gains two Warping Points.",
    ),
    (
        "We will meet again as the seasons turn",
        "Naranj",
        "Solomonic Travel",
        25,
        14,
        "Delay: Season, Ritual. Draws a portal from one supernatural aura "
        "to another of the same realm he has been to; sahirs use it to "
        "reach the Majlis.",
    ),
)

ARKHAMAN: StatBlock = {
    "characteristics": {
        "intelligence": 2,
        "perception": 1,
        "presence": 2,
        "communication": 1,
        "strength": -1,
        "stamina": 0,
        "dexterity": 0,
        "quickness": 0,
    },
    "warping": (2, 2),
    "confidence": (1, 3),
    "virtues_flaws": [
        "The Gift",
        "Sahir",
        "Vizier",
        "Wise One",
        "Gentle Gift",
        "Sihr",
        "Arcane Lore",
        ("Puissant {ability}", {"ability": "Solomonic Travel"}),
        "Magic Addiction",
        "Infernal Spirit Companion",
        "Reckless (Minor)",
        "Sheltered Upbringing",
        "Tainted with Evil",
    ],
    "abilities": [
        ("Living Language: Arabic", 5, "Solomonic usage"),
        ("Area Lore: Sana'a", 3, "people"),
        ("Artes Liberales", 2, "lab work"),
        ("Awareness", 2, "alertness"),
        ("Bargain", 3, "with Kharrat"),
        ("Concentration", 2, "regaining control"),
        ("Finesse", 2, "casting multiple effects"),
        ("Infernal Lore", 5, "spirits"),
        ("Magic Lore", 2, "spirits"),
        ("Penetration", 2, "Infernal spirits"),
        ("Profession: Scribe", 5, "copying lab texts"),
        ("Stealth", 2, "sneaking"),
        ("Sihr", 10, ""),
        ("Solomonic Alchemy", 0, ""),
        ("Solomonic Astrology", 5, ""),
        ("Solomonic Physic", 0, ""),
        ("Solomonic Storytelling", 5, ""),
        ("Solomonic Travel", 10, ""),
    ],
    "traits": {"Optimistic": 3, "Reckless": 3, "Friendly": 2, "Brave": -1},
    "notes": "His Sihr is of the Magic realm. Solomonic Travel 10 is +2 "
    "with his Puissant Virtue (10+2 in the book).",
}


def stats(cradle: Cradle) -> None:
    """'Arkhaman as printed, his spells as tradition effects and Kharrat
    as his bound jinni (linked to its Bestiary record once bestiary.py
    makes creatures["kharrat"])."""
    b = cradle.b
    arkhaman = cradle.people.get("arkhaman")
    if arkhaman is None:
        return
    kharrat = cradle.creatures.get("kharrat")
    block = {
        **ARKHAMAN,
        "traditions": [SAHIRS],
        "effects": [
            Builder.effect(
                name,
                rule=rule,
                uses=[art],
                level=level,
                parameters=does,
                notes=f"Penetration +{penetration}.",
            )
            for name, rule, art, level, penetration, does in ARKHAMAN_EFFECTS
        ],
        "bound_beings": [
            Builder.bound_being(
                "Kharrat",
                kind="Bargained jinni",
                creature=kharrat,
                notes="His Infernal Spirit Companion, whom he believes his "
                "father; held so far with vis.",
            )
        ],
    }
    b.stats(arkhaman, block)
    if kharrat is not None and not any(
        link.target_id == kharrat.id for link in arkhaman.links
    ):
        b.link(arkhaman, "creatures", kharrat, "His bound jinni")
