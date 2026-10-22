"""Mesopotamia, the Jazira and the north (TC&TC ch07), in paraphrase.

Places: the region places["mesopotamia"] (no `inside`), holding the
old gods, Tiamat's brood and the demons of the land (C15); east.py's
shared places["iraq"], ["georgia"] and ["greater_armenia"] are set
inside it here (their place_id only, never their text);
["harut_and_marut"] already sits in Iraq and is linked from Babylon.
Provinces places["jazira"], ["azarbayjan"], ["arran"], ["mukan"],
["shirvan"] and ["gilan"]. Sites, by slug: places["karbala_tomb"] and
["najaf_shrine"] (Divine 8, Divine Might 75 each), ["ighraq_gorge"]
(Magic 6, Ighraq's 2 Aquam a year), ["great_swamp"] and in it
["uruk"] (Faerie 2, the way to Gilgamesh's Elysium), ["babylon"],
["ubulla_whirlpool"], ["nimrods_furnace"] (at Kutha), ["ctesiphon"],
["dayr_al_aqul"], ["dayr_hizqil"], ["qasr_shirin"], ["siffin"],
["sanjah_bridge"], ["mount_judi"] (the ark's regio), ["lake_urmiya"]
(Magic 2) and on its island ["urmiya_tower"] (Magic 3, a candidate
covenant site), ["water_of_life"] (Rumoured), ["rock_of_moses"] (at
Shamakhi, a relic of Faith 3) and ["armenian_site"] (the candidate
covenant site in Greater Armenia, C16).

Towns: east.py's world["baghdad"] and ["mosul"] are not remade (Mosul
is set in the Jazira here); this part adds world["al_madain"],
["basra"], ["kufa"], ["najaf"], ["hilla"], ["samarra"], ["kutha"],
["ubulla"], ["nasibin"], ["barqaid"], ["amid"], ["raqqa"], ["harran"],
["edessa"] (the Mandylion in its summary, C23), ["arzanjan"],
["tabriz"], ["maragha"], ["shamakhi"], ["barvan"] (Divine 1, in its
summary), ["bajarvan"], ["baylaqan"] and ["tiflis"]. order.py puts Dayr
Qunna in world["al_madain"] and the House of the Heavens in
world["nasibin"].

Lords (C13): east.py's world["caliph"], ["lord_of_mosul"],
["al_aziz"] and ["king_of_georgia"] are not remade (the Emir of Mosul
and al-'Aziz are set in the Jazira when they have no place); this part
adds world["atabeg_uzbek"] (Azarbayjan and Arran, at Tabriz; answering
to persia.py's world["khwarazm_shah"] in finish), ["shirvanshah"] and
["emir_of_gilan"] (linked to east.py's world["nizaris"] and ["imam"]).

Factions (C15): world["sabians"] (Harran), ["ashipu"] (the exorcists)
and ["brass_smiths"] (the guild of Arzanjan, its Lesser Power in the
summary); none has a tradition record. Creatures with stats (the
aladlammu, girtablullu, mushhushshu, Ighraq) are bestiary.py's; the
whirlpool's jinni, the demon of Nimrod's furnace and Gilgamesh are
sentences at their places. Golden Baghdad is jinn.py's. The book gives
these places no vis without a source, so none has suggested vis. The
story seeds are stories.py's, hung on these keys."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import Builder, paragraphs

if TYPE_CHECKING:
    from ...models import Neighbour
    from . import Cradle

RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "In the region"}

#: Shared records (east.py's) this part places when they have none:
#: (world or places key, key of this part's place).
SHARED_PLACES: tuple[tuple[str, str], ...] = (
    ("iraq", "mesopotamia"),
    ("georgia", "mesopotamia"),
    ("greater_armenia", "mesopotamia"),
    ("mosul", "jazira"),
    ("lord_of_mosul", "jazira"),
    ("al_aziz", "jazira"),
)


def _place(cradle: Cradle, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and keep it under `key` for the other parts."""
    place = cradle.b.place(name, **kw)
    cradle.places[key] = place
    return place


def build(cradle: Cradle) -> None:
    _region(cradle)
    _iraq(cradle)
    _jazira(cradle)
    _north(cradle)
    _lords(cradle)
    _towns(cradle)
    _factions(cradle)
    _shared(cradle)


def finish(cradle: Cradle) -> None:
    """Atabeg Uzbek owns the Khwarazm-shah as overlord, once persia.py
    has made him."""
    shah = cradle.world.get("khwarazm_shah")
    uzbek = cradle.world["atabeg_uzbek"]
    if shah is not None and uzbek.answers_to is None:
        uzbek.answers_to = shah.id
    _shared(cradle)


def _shared(cradle: Cradle) -> None:
    for key, where in SHARED_PLACES:
        record = cradle.find(key)
        place = cradle.places.get(where)
        if record is not None and place is not None and record.place_id is None:
            record.place_id = place.id


# -- the region --


def _region(cradle: Cradle) -> None:
    region = _place(
        cradle,
        "mesopotamia",
        "Mesopotamia",
        summary=paragraphs(
            "The political heart of Sunni Islam and its north-western "
            "provinces, from Iraq up through the Jazira to the "
            "Caucasus. Nearly every ruler owns the 'Abbasid caliph at "
            "least in name, but most provincial lords govern as they "
            "please and look to Baghdad only when its blessing helps "
            "their claim. The land falls into three: fertile plains "
            "between and along the Tigris and Euphrates, watered in Iraq "
            "by canals thousands of years old that shifting ground and "
            "neglect have badly worn down; mountains to the north, east "
            "and north-west, farmed only in the valleys; and the Syrian "
            "desert to the west, running south into Arabia's Nefud. Most "
            "people are Muslims, with many Christians and Jews, living "
            "in towns and villages, with nomads and oasis folk in the "
            "desert.",
            "The old gods of the land were faeries, and are starving: "
            "their worship lingers only at a few cult centres, at "
            "Harran, Mardin, Ashshur and Mosul, whose priests, many of "
            "them yatus, walk the streets unafraid in their tall "
            "conical hats. Too few to feed them, so the gods have hidden "
            "in regiones for centuries and crave attention, some "
            "dreaming of their cults reborn, some only of friends, and "
            "none quite understanding mortals. Among them: Anu of the "
            "sky at Uruk, head of the elder Anunnaki; Ea of the waters "
            "under the earth, of craft, magic and wisdom, at Eridu; "
            "Ellil of the earth at Nippur, head of the younger Igigi, "
            "who keeps the Tablet of Destinies; Ishtar of love, "
            "fertility and war at Uruk, Nineveh and Erbil; Dumuzi of "
            "flocks and fields, her lover, half of each year in the "
            "underworld; Adad of storms, canals and liver omens at "
            "Aleppo; Mami the great mother at lost Kesh; Nergal of war, "
            "plague and fire and his weeping queen Ereshkigal at Kutha; "
            "Sin of the moon at Ur and Harran; Shamash of the sun and "
            "justice at Sippar and Larsa; Marduk at Babylon; and Ashshur "
            "at Ashshur.",
            "Tiamat, the first mother, bore the gods with her consort "
            "Apsu, then tired of the young gods' din and bred eleven "
            "kinds of monster to destroy them, until Marduk killed her "
            "and made the world from her body; students of the Magic "
            "Realm will see in it a Titanomachia, faerie gods taking "
            "power from primordial Magic beings. Her brood serve the "
            "fading gods still: the seven-headed dragon mushmahhu, the "
            "lion-dragon ushumgallu, the horned snake bashmu sixty "
            "leagues long, the snake-dragon mushhushshu, the hairy giant "
            "lahamu, the lion-headed, bird-footed ugallu, the "
            "lion-bodied man uridimmu, the scorpion-man girtablullu, the "
            "fierce storm umu dabrutu, the merman kulullu and the "
            "bull-man kusarikka. Colossal statues of the winged bulls, "
            "the aladlammu and apsasu, guard many old ruins, and a land "
            "that has one may call on the faerie against disease and "
            "demons.",
            "Demons throng the land, some busy since ancient times: the "
            "uttuku, Infernal jinn of the Mazzikim's kind; the galla, "
            "great spirits of disease, whom the aladlammu fight; the "
            "lilu, ghuls of the wastes who prey on children and women "
            "with child, and their female counterparts, the lilitu "
            "succubi; and the gidim, ghosts who come back to torment "
            "the families that mourn them. Realms of Power: The Infernal "
            "places the Mulhidun, an Infernal tradition, mostly in the "
            "Jazira.",
        ),
    )
    for key, name, summary in (
        (
            "jazira",
            "The Jazira",
            "The fertile country north of Iraq between the rivers, "
            "mostly under Ayyubid princes who spend their days plotting "
            "against one another, so that the towns they do not hold "
            "outright own them in name only. Nearly all its rulers, the "
            "Ayyubids included, honour the caliph, to little effect.",
        ),
        (
            "azarbayjan",
            "Azarbayjan",
            "A mountainous province north of the Jazira, ruled lightly "
            "by the Atabegs of Azarbayjan from Tabriz and mostly left to "
            "local governors. Its people are Turks, Persians and "
            "Caucasians, Muslims, Christians, Jews, Zoroastrians and "
            "others; its communities are scattered by the mountains and "
            "its greatest centres no more than big towns. A Turkic "
            "tongue is the common speech, with local dialects beside "
            "it.",
        ),
        (
            "arran",
            "Arran",
            "The province north of Azarbayjan, held by its atabegs in "
            "name, though they do little here. Most of its people are "
            "Armenian Christians, with a large Sunni community that "
            "includes most of the ruling class.",
        ),
        (
            "mukan",
            "Mukan",
            "Mostly a marshy plain running from the north-western "
            "mountains down to the Caspian, much of it farmed for rice "
            "and wheat.",
        ),
        (
            "shirvan",
            "Shirvan",
            "A mountainous province north of Arran and Mukan, its towns "
            "in the valleys, ruled for centuries by the Shirvanshahs, a "
            "Persianised Arab dynasty, from Shamakhi. Most of its people "
            "are Sunnis, like their rulers, or Christians.",
        ),
        (
            "gilan",
            "Gilan",
            "A backwater, neither rich nor famous: mostly jungle-clad "
            "mountains, with a fertile coastal plain of rice and wheat "
            "on the Caspian. Its rulers pay tribute to the lords of "
            "Jibal to the south and are otherwise left alone.",
        ),
    ):
        _place(cradle, key, name, inside=region, summary=summary)


# -- Iraq --


def _iraq(cradle: Cradle) -> None:
    iraq = cradle.places["iraq"]
    _place(
        cradle,
        "qasr_shirin",
        "The Palace of Shirin",
        inside=iraq,
        realm="Faerie",
        summary=paragraphs(
            "Qasr Shirin, a big walled village on the road up to Jibal "
            "under the mountains of the Persian plateau, named for "
            "Shirin, wife of the Persian king Khusraw II Parviz, who "
            "lived here. Her palace is a ruin, but at every full moon it "
            "fills with faerie Shirins, Khusraws, the sculptor Farhad "
            "and their courtiers, playing out Shirin's courtship over "
            "and over, best known in al-Nizami's telling (he died in "
            "1209): the king loves the Armenian princess, the mighty "
            "Farhad becomes his rival, Khusraw sends him to cut through "
            "the Behistun cliffs for water and, when he does it, sends "
            "word that Shirin is dead, and Farhad leaps from the cliff; "
            "his pomegranate-wood axe grows into a tree whose fruit "
            "cures any sickness, and Shirin at last weds the king after "
            "he proves himself, killing a lion bare-handed to save "
            "her.",
            "Visitors at the full moon are drawn into the parts of the "
            "tale, and may win rewards or wisdom by playing them.",
        ),
    )
    _place(
        cradle,
        "ctesiphon",
        "The Palace of Ctesiphon",
        inside=iraq,
        summary=paragraphs(
            "The ruins of the Persian emperors' capital at al-Mada'in, "
            "witness to the end of the Sasanids. Over what was the "
            "throne room still stands a vaulted arch more than 110 feet "
            "high at its peak, of great interest to the Mystery of "
            "Hermetic Architecture. The townsfolk distrust foreigners "
            "who poke about the ruins.",
        ),
    )
    _place(
        cradle,
        "dayr_al_aqul",
        "Dayr al-'Aqul",
        inside=iraq,
        realm="Divine",
        summary=paragraphs(
            "The first of three Nestorian monasteries down the Tigris "
            "from al-Mada'in, linked to one another without knowing it. "
            "It stands on the river bank in a sizeable town of the same "
            "name, which has a great mosque. Its monks take a toll from "
            "the river traffic and share it with the town, which lives "
            "on it, but lately the banks have been changing fast and "
            "the river is drifting west, away from them. Nothing they "
            "try stops it, monks and townsfolk alike think something "
            "supernatural is at work, and some whisper that the 'monks' "
            "of Dayr Qunna, a mile east, are sorcerers out to ruin them.",
        ),
    )
    _place(
        cradle,
        "dayr_hizqil",
        "Dayr Hizqil",
        inside=iraq,
        realm="Divine",
        summary=paragraphs(
            "A monastery in the town of al-Nu'maniyya, twenty miles "
            "south of Dayr al-'Aqul, where the monks keep a madhouse "
            "for the insane: plain, strong men able to hold down their "
            "charges when they must.",
        ),
    )
    babylon = _place(
        cradle,
        "babylon",
        "The Ruins of Babylon",
        inside=iraq,
        summary=paragraphs(
            "The ruined city of southern Iraq that saw the chaining of "
            "Harut and Marut, who hang bound beneath it, the building "
            "of the Tower of Babel, the Jews' exile, Nebuchadnezzar's "
            "Hanging Gardens, and its fall with Belshazzar's kingdom to "
            "the Persians, in 539 BC. Ancient Magic tells more of its "
            "mysteries.",
        ),
    )
    harut = cradle.places.get("harut_and_marut")
    if harut is not None:
        cradle.b.link(babylon, "places", harut, "Beneath the ruins")
    swamp = _place(
        cradle,
        "great_swamp",
        "The Great Swamp",
        inside=iraq,
        summary=paragraphs(
            "South of Babylon a great marsh fills the land between the "
            "two rivers until they meet. Its air is foul and insects "
            "swarm, yet stubborn villagers have drained patches to farm "
            "and live in scattered villages and towns, getting about in "
            "shallow boats. They keep the old religion in fragments, "
            "with no priests left, but one tale they have recited "
            "faithfully for generations: the Epic of Gilgamesh.",
        ),
    )
    _place(
        cradle,
        "uruk",
        "The Ruins of Uruk",
        inside=swamp,
        realm="Faerie",
        aura=2,
        summary=paragraphs(
            "A great stepped ziggurat rising from the middle of the "
            "swamp, all that is left of a temple of Ishtar, with a "
            "Faerie aura of 2. The locals keep away: some who went "
            "never came back. A doorway choked with rubble is a faerie "
            "Guardian, and whoever breaks through it passes, unawares, "
            "into Elysium in the Faerie Realm; the Threshold is 33, "
            "but those who come to the temple and cross the doorway "
            "gather the points they need without fail.",
            "Within, Gilgamesh asks one or all of them to take the part "
            "of Enkidu in his tale, which sets them on a Path of "
            "Destiny. The tale: the gods send the wild man Enkidu to "
            "distract the unloved king; tamed by Shamhat, he wrestles "
            "Gilgamesh to a draw and they become friends; they kill "
            "Humbaba in the Pine Forest and the Bull of Heaven that "
            "Ishtar sends when Gilgamesh spurns her; the gods strike "
            "Enkidu dead for it; Gilgamesh wanders past the scorpion "
            "men to Siduri and Utnapishtim, fails to win eternal life, "
            "and comes home wise enough to rule well. Whoever dies as "
            "Enkidu is sent back through the Guardian alive, with what "
            "he came for; a player who knowingly lets her character take "
            "that part and die gains an Unmitigated Success and, the "
            "book suggests, a Confidence Point.",
        ),
    )
    _place(
        cradle,
        "ubulla_whirlpool",
        "The Whirlpool at Ubulla",
        inside=iraq,
        summary=paragraphs(
            "In the late eighth century a savage jinni made itself a "
            "whirlpool in the Shatt al-'Arab off Ubulla and wrecked "
            "every ship that came near, cutting Baghdad off from the "
            "Gulf. Zubayda bint Ja'far, Harun al-Rashid's wife, learnt "
            "in her studies that stone was its bane: she had ships "
            "loaded with stones and sunk in its maw, burying it in the "
            "river bed, and the waters grew calm. It is imprisoned "
            "there, not dead.",
        ),
    )
    _place(
        cradle,
        "nimrods_furnace",
        "Nimrod's Furnace",
        inside=iraq,
        realm="Divine",
        summary=paragraphs(
            "A huge tower of hardened ash in the town of Kutha, all "
            "that is left of the furnace of the tyrant Nimrod, builder "
            "of the Tower of Babel. He threw Abraham, son of his own "
            "vizier Terah, into it; God bade the fire be cool, and "
            "Abraham walked out unhurt while the furnace itself burnt "
            "away, leaving the Tower of Ashes.",
        ),
    )
    _place(
        cradle,
        "karbala_tomb",
        "The Tomb of al-Husayn",
        inside=iraq,
        realm="Divine",
        aura=8,
        summary=paragraphs(
            "At Karbala', in the desert, Umayyad troops cut down "
            "al-Husayn, son of 'Ali and grandson of the Prophet, and his "
            "followers in 680, as he pressed his claim to the caliphate "
            "after Mu'awiya's death. All Muslims remember it with "
            "sorrow and the Shi'is mourn it each year on 'Ashura', the "
            "tenth of Muharram. A small town has grown up round his "
            "tomb (his head is in Cairo), a great Shi'i pilgrimage: a "
            "domed shrine in a garden pool, with a silver gate the "
            "pilgrims kiss before going in, gold and silver lamps "
            "within, and silk curtains over its other doors.",
            "Its Divine aura is 8, and al-Husayn has Divine Might 75. "
            "Visitors may seek his baraka for these Saint Powers. To "
            "heal: Mass Healing, The Faithful Made Whole and Straighten "
            "the Crippled. Against evil: Expel Demons, Acknowledgement "
            "of Evil, Resist Temptation and Celestial Immunity. Besides "
            "these: Apparition, Grant of Serenity, Humility of Caesar "
            "and Terrify the Unbeliever.",
        ),
    )
    _place(
        cradle,
        "najaf_shrine",
        "The Shrine of 'Ali",
        inside=iraq,
        realm="Divine",
        aura=8,
        summary=paragraphs(
            "'Ali, struck down at Kufa in 661, asked that his body be "
            "set on a camel turned loose, and buried where it knelt. His "
            "followers kept the grave secret from the Umayyads until in "
            "791 Harun al-Rashid, hunting, chased a deer into a thicket "
            "that neither his horse nor his hounds would enter, had it "
            "dug up, found the body and built a tomb. Enlarged since, it "
            "is the heart of Najaf and draws thousands of pilgrims a "
            "year: a gold dome with a great portal and silver doorstep "
            "on each side, glazed tiles, thick carpets, gold and silver "
            "lamps and silk on doors and walls, the tomb itself fenced "
            "by engraved gold plates fixed with silver nails.",
            "Its Divine aura is 8, and 'Ali has Divine Might 75. "
            "Visitors may pray for his baraka for these Saint Powers. "
            "To heal: Cure Blindness, Mass Healing, The Faithful Made "
            "Whole and Straighten the Crippled. Against evil: Expel "
            "Demons, Acknowledgement of Evil, Resist Temptation and "
            "Celestial Immunity. Besides these: Apparition, Grant of "
            "Serenity, Rebuke the Unfaithful, Humility of Caesar and "
            "Terrify the Unbeliever. The shrine is famed for healing, so powers of "
            "that kind are invoked at +1.",
        ),
    )
    _place(
        cradle,
        "ighraq_gorge",
        "The Jinni's Gorge",
        inside=iraq,
        aura=6,
        summary=paragraphs(
            "The Siq al-Majnun, a narrow canyon on the lower course of "
            "the Lesser Zab, the Tigris tributary called Majnun, 'the "
            "mad river', for its wild currents. Here Ighraq al-Siq, 'the "
            "drowning flood of the gorge', an ancient pagan spirit of "
            "the Tigris who once roamed the whole river, is penned, and "
            "his fits bring the violent spring floods through the "
            "canyon. The canyon has a Magic aura of 6.",
            "He is shut in a Jinni Block, a strange tower tomb of the "
            "kind set at the gates of some lost cities, and while there "
            "can neither act nor be detected, being part of the stone; "
            "the block takes his Magic Resistance but can still be worn "
            "away or broken. Something unknown frees him whenever "
            "anyone intrudes on the canyon, to drive them off. The "
            "ground round the block is a fixed Arcane Connection to him "
            "(+1 to the Penetration multiplier), and standing barefoot "
            "on it or touching it a stronger one (+3) that also shares "
            "his Magic Resistance. A sahir, summoner or magus there may "
            "try to command him by Sihr or by scouring, even unaware he "
            "is there, but a failure frees him in a rage.",
            "Vis: clear rainwater that gathers each year in a niche "
            "cut into the block, 2 pawns of Aquam.",
        ),
    )


# -- the Jazira --


def _jazira(cradle: Cradle) -> None:
    jazira = cradle.places["jazira"]
    _place(
        cradle,
        "mount_judi",
        "Mount Judi",
        inside=jazira,
        realm="Divine",
        levels=[
            Builder.level(
                "The resting place of the Ark",
                3,
                "Divine",
                enter="Walk through the mosque's mihrab, though it looks to "
                "be solid marble.",
                notes="The same regio can be reached from Mount Ararat in "
                "Armenia; Ancient Magic describes it.",
            )
        ],
        summary=paragraphs(
            "Where the Muslims hold that Noah's Ark came to rest, as "
            "Christians and Jews say it did on Ararat in Armenia; both "
            "are right, for its remains lie in a regio that can be "
            "reached from either mountain. A mosque on the summit marks "
            "the spot. At its foot is the town of Thamanin, 'eighty', "
            "whose people claim to descend from the eighty companions "
            "of Noah who, they say, founded it.",
        ),
    )
    _place(
        cradle,
        "siffin",
        "The Battlefield of Siffin",
        inside=jazira,
        realm="Divine",
        summary=paragraphs(
            "Across the Euphrates from Raqqa, where 'Ali and Mu'awiya "
            "fought in 657. After months of skirmishes Mu'awiya asked "
            "for arbitration; 'Ali agreed, and some of his followers "
            "left him over it, among them Ibn Muljam, who later killed "
            "him. 'Ali's dead lie buried here, and from a distance their "
            "uncorrupted bodies can be seen through the earth, though "
            "they vanish as one comes near. It is a Shi'i place of "
            "pilgrimage.",
        ),
    )
    _place(
        cradle,
        "sanjah_bridge",
        "The Sanjah Bridge",
        inside=jazira,
        summary=paragraphs(
            "A superb bridge over the Sanjah, a tributary of the "
            "Euphrates: a single arch over two hundred paces long, of "
            "huge dressed stones, built long ago by a sorcerer in a "
            "local ruler's service with the help of a talisman he "
            "carried. That talisman now sits high in the arch's keystone; "
            "what it does, and what removing it would do, nobody knows. The villages round about depend on "
            "the bridge to get their crops to market.",
        ),
    )


# -- the north --


def _north(cradle: Cradle) -> None:
    p = cradle.places
    lake = _place(
        cradle,
        "lake_urmiya",
        "Lake Urmiya",
        inside=p["azarbayjan"],
        aura=2,
        summary=paragraphs(
            "A lake of startling blue, smooth as glass, named for the "
            "town on its western shore. Fishermen on a small island at "
            "its centre catch the odd dog-headed fish that live in it. "
            "The leavings of an old sorcerer's work and the beauty of "
            "the place give the lake a Magic aura of 2, and 3 on the "
            "island.",
        ),
    )
    _place(
        cradle,
        "urmiya_tower",
        "The Sorcerer's Tower of Urmiya",
        inside=lake,
        aura=3,
        summary=paragraphs(
            "The ruin on Lake Urmiya's island where a mighty sorcerer "
            "of old bred and experimented on the lake's fish, until a "
            "failed experiment blew up most of the tower and him with "
            "it. Catacombs remain under the ruins, very likely full of "
            "his hybrid creatures. The book suggests it as a site for a "
            "new covenant.",
        ),
    )
    _place(
        cradle,
        "water_of_life",
        "The Fountain of the Water of Life",
        inside=p["mukan"],
        realm="Divine",
        **RUMOURED,
        summary=paragraphs(
            "The spring of the Water of Life, which is said to make "
            "whoever bathes in it immortal, and from which al-Khidr, "
            "the Green One, drank. Bajarvan in Mukan and Shamakhi in "
            "Shirvan both claim it is near them, so seekers might start "
            "where the Cyrus and the Araxes meet; no one has found it, "
            "or no one who did has come back. Al-Khidr will guide only "
            "those whose purpose is pure.",
        ),
    )
    _place(
        cradle,
        "rock_of_moses",
        "The Rock of Moses",
        inside=p["shirvan"],
        realm="Divine",
        aura=4,
        summary=paragraphs(
            "The stone at Shamakhi that marks where Moses met al-Khidr: "
            "the fish Moses and his servant laid on it came alive and "
            "swam away, and the townsfolk still come to pray here for "
            "the dying. For Muslims it is a relic of Faith 3 with the "
            "Saint Power The Faithful Made Whole. The aura is the "
            "city's.",
            "Moses asked al-Khidr to teach him and was allowed to "
            "follow only if he never questioned; he protested when "
            "al-Khidr holed a boat, killed a boy and rebuilt a wall for "
            "people who had refused them food, and on the third time "
            "was told why (a king was seizing boats, the boy was an "
            "unbeliever whose parents would have a better child, the "
            "wall hid orphans' treasure) and they parted. Sufis take it "
            "as the model of student and master; it would serve a "
            "Mystery's Initiation too.",
        ),
    )
    _place(
        cradle,
        "armenian_site",
        "The Armenian Highlands",
        inside=cradle.places["greater_armenia"],
        summary=paragraphs(
            "A candidate covenant site. Greater Armenia's many "
            "remote sites have kept out mundane folk and may hold strong "
            "Magic auras, and its tangled politics let a newcomer set up "
            "independently, so long as the covenant does not grow strong "
            "enough to alarm its neighbours. The cruel winters make it "
            "hard to supply, and as the Tribunals fill, other magi may "
            "be looking for sites here too and contest the best.",
        ),
    )


# -- the lords --


def _lords(cradle: Cradle) -> None:
    b, w, p = cradle.b, cradle.world, cradle.places
    w["atabeg_uzbek"] = b.lord(
        "Atabeg of Azarbayjan",
        title="",
        wealth="Wealthy",
        seat="Tabriz",
        ruler="Muzaffar al-Din Uzbek",
        place=p["azarbayjan"],
        summary=paragraphs(
            "Muzaffar al-Din Uzbek, atabeg since 1210 and head of the "
            "Atabegs of Azarbayjan, who rule Azarbayjan and, in name, "
            "Arran, from Tabriz. He rules lightly, leaving much to local "
            "governors; he owns the Khwarazm-shah as overlord and pays "
            "tribute to the king of Georgia. Jalal al-Din Hasan of the "
            "Nizaris has made an alliance with him. If history holds he "
            "rules until 1225.",
        ),
    )
    w["shirvanshah"] = b.lord(
        "Shirvanshah",
        title="",
        wealth="Wealthy",
        seat="Shamakhi",
        ruler="Farrukhzad I and Garshasp I",
        place=p["shirvan"],
        summary=paragraphs(
            "The Shirvanshahs, a Persianised Arab dynasty and Sunnis, "
            "have ruled Shirvan for centuries from Shamakhi. Two of the "
            "royal house share power now: Farrukhzad I ibn Manuchihr "
            "III, who came to the throne after 1187, and his son "
            "Garshasp I, who has reigned with him since 1204. If history "
            "holds both are gone by 1225.",
        ),
    )
    w["emir_of_gilan"] = b.lord(
        "Emir of Gilan",
        title="",
        seat="Barvan",
        ruler="the emir of Gilan",
        place=p["gilan"],
        summary=paragraphs(
            "The ruler of Gilan, who pays tribute to the lords of Jibal "
            "and otherwise governs alone. He has been pushed into "
            "alliance with Jalal al-Din Hasan, head of the Nizaris, who "
            "has married his four daughters.",
        ),
    )
    for key, note in (("nizaris", "His allies"), ("imam", "His son-in-law")):
        target = w.get(key)
        if target is not None:
            b.link(w["emir_of_gilan"], "places", target, note)


# -- the towns --


def _towns(cradle: Cradle) -> None:
    b, w, p = cradle.b, cradle.world, cradle.places
    caliph = w.get("caliph")
    iraq, jazira = p["iraq"], p["jazira"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "al_madain",
        "Al-Mada'in",
        paragraphs(
            "A small, crowded town south-east of Baghdad, once, in the "
            "seventh and eighth centuries, a great cluster of seven "
            "towns, long in decline. Its mosque is much admired, with "
            "the tomb of Salman the Persian, a close companion of the "
            "Prophet, beside it, and the ruined palace of Ctesiphon "
            "stands here. A large town like this can keep fifty sahirs, "
            "split between its quarters. Downriver lie the monasteries "
            "of Dayr al-'Aqul, Dayr Qunna, which is really a house of "
            "wisdom, and Dayr Hizqil.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "basra",
        "Basra",
        paragraphs(
            "An important city of southern Iraq on two canals running "
            "into the Shatt al-'Arab, full of shrines and mosques. The "
            "best known, built by 'Ali ibn Abi Talib, has a minaret that "
            "shakes or stays still as an oath sworn before it is true or "
            "false, a miracle that can be neither fooled nor resisted. "
            "Its library is said to hold more than 15,000 books. Like "
            "al-Mada'in it can keep fifty sahirs; the grand vizier "
            "Kha'trazh comes from here.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "ubulla",
        "Ubulla",
        paragraphs(
            "A busy town of palaces, mosques and markets on the north "
            "side of a canal into the Shatt al-'Arab, by the buried "
            "jinni's whirlpool.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "kufa",
        "Kufa",
        paragraphs(
            "A city about seven miles north-east of Najaf, lively once, "
            "now declining and much of it ruined. In its eastern part "
            "the Great Mosque still stands in good repair: there 'Ali "
            "received his death wound from Ibn Muljam's poisoned sword "
            "in 661, at the spot a mihrab now marks, and Shi'i pilgrims "
            "still come on their way to or from Najaf. In 951 the stolen "
            "Black Stone was left in a sack in its great mosque.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "najaf",
        "Najaf",
        paragraphs(
            "A city of the greatest importance to the Shi'is, grown up "
            "round the shrine of 'Ali, with a vast graveyard where "
            "several prophets and many Shi'i nobles lie, and madrasas, "
            "mosques and other religious houses. It has several houses "
            "of wisdom.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "hilla",
        "Hilla",
        paragraphs(
            "A city on both banks of the Euphrates, most of it on the "
            "west, joined by a bridge of boats held by great iron "
            "chains. Many Twelver Shi'is live here waiting for "
            "the twelfth imam, who is to return at the end of time at "
            "one of its shrines, and it is a centre of Twelver learning, "
            "home to many scholars.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "samarra",
        "Samarra",
        paragraphs(
            "The 'Abbasid capital from 836 to 892, then a sprawl of "
            "rich palaces and mosques on both banks of the Tigris where "
            "the caliphs lived as prisoners of their guards, who fought "
            "one another for them. Once the caliphs went back to Baghdad "
            "it fell to ruin, save the huge Great Mosque of "
            "al-Mutawakkil (who reigned 847 to 861), still mostly whole, "
            "with its spiral minaret some 180 feet high.",
            "Most of its people in 1220 are Twelver Shi'is, staying by "
            "the tombs of the tenth and eleventh imams and a mosque "
            "with an underground room where the twelfth imam vanished "
            "and may one day come back, as he may at Hilla. Its wide "
            "ruins may hide Magic auras and devices of the old court "
            "sorcerers, and its wells and canals still work: a possible "
            "covenant site, if its people would bear foreign wizards.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "kutha",
        "Kutha",
        paragraphs(
            "The old cult centre of Nergal and Ereshkigal, where Nimrod's "
            "furnace stands as a tower of ash.",
        ),
        ruler="the caliph",
        answers_to=caliph,
        place=iraq,
    )
    town(
        "nasibin",
        "Nasibin",
        paragraphs(
            "A seat of Nestorian learning and of a bishop, its people "
            "Christians and Muslims. It is famed for its gardens, forty "
            "thousand of them it is said, full of unusually large and "
            "sweet-smelling white roses, and for the swarms of its "
            "scorpions, whose sting is particularly deadly. Here stood "
            "the House of the Heavens, empty since 1186. Its ruler and "
            "Mosul's each say the thieves of Barqa'id are the other's "
            "problem.",
        ),
        ruler="its own lord",
        place=jazira,
    )
    town(
        "barqaid",
        "Barqa'id",
        paragraphs(
            "A city travellers avoid, peopled almost wholly by thieves "
            "who rob visitors and the caravans on the Nasibin road. With "
            "fewer travellers passing, they have grown bolder and raid "
            "the towns and villages round about, whose appeals to Mosul "
            "and Nasibin have gone unanswered.",
        ),
        ruler="its thieves",
        charter="Rules itself",
        place=jazira,
    )
    town(
        "amid",
        "Amid",
        paragraphs(
            "A city of black basalt, heavily fortified by its Turkish "
            "lords: thick walls, many watchtowers, iron gates, a citadel "
            "on a high hill at its centre, and walled suburbs outside. "
            "Its great Sunni mosque and great Jacobite church, both of "
            "black basalt and iron, are famously beautiful. The walls "
            "are for the vast faerie armies, armed with wood and stone "
            "and armoured in some unknown old leather, that have "
            "attacked it for centuries, always at the spring equinox; "
            "the city prepares for them with weary resignation, and the "
            "shared enemy has made its Muslims and Christians firm "
            "friends.",
        ),
        ruler="its Turkish lords",
        place=jazira,
    )
    town(
        "raqqa",
        "Raqqa",
        paragraphs(
            "Once a residence of Harun al-Rashid, reviving under the "
            "Ayyubids, with thriving markets and famous blue-glazed "
            "pottery. The battlefield of Siffin lies across the "
            "Euphrates.",
        ),
        ruler="the Ayyubids",
        place=jazira,
    )
    town(
        "harran",
        "Harran",
        paragraphs(
            "An Ayyubid town of ancient name: Abraham lived here, and "
            "in the eighth century it was the first home of the "
            "scholars who put the classical learning into Arabic. About "
            "nine miles south a shrine marks where Abraham and Sarah "
            "lived. It was the centre of the Sabians, monotheist "
            "star-magicians, and a strong cult of Ashshur, the Assyrians' "
            "patron god, is here still. Travellers complain of its heat, "
            "shadeless and stale-watered.",
        ),
        ruler="the Ayyubids",
        place=jazira,
    )
    town(
        "edessa",
        "Edessa",
        paragraphs(
            "A city that has changed hands many times, Byzantine, "
            "Muslim and others; the crusaders took it in 1098 and made "
            "it the seat of one of their four states, Zangi won it back "
            "on Christmas Eve 1144, and the Ayyubid sultan of Aleppo, "
            "al-'Aziz, holds it now. Most of its people are Christians "
            "of several churches. Its churches' great relic was the Holy "
            "Mandylion, the cloth with Christ's face that he sent to "
            "King Abgar, which the city's Muslim rulers traded to the "
            "Byzantine emperor for prisoners in the tenth century and "
            "which vanished when the crusaders sacked Constantinople in "
            "1204; the people hope for a miracle to bring it home.",
        ),
        ruler="al-'Aziz of Aleppo",
        answers_to=w.get("al_aziz"),
        place=jazira,
    )
    town(
        "arzanjan",
        "Arzanjan",
        paragraphs(
            "A busy market town, mostly of Armenian Christians, famed "
            "for its craftsmen, above all its brass-smiths, whose work "
            "takes beautiful shapes no other town's smiths can match.",
        ),
        place=p["greater_armenia"],
    )
    uzbek = w["atabeg_uzbek"]
    town(
        "tabriz",
        "Tabriz",
        paragraphs("The seat of the Atabegs of Azarbayjan."),
        ruler="Atabeg Uzbek",
        answers_to=uzbek,
        place=p["azarbayjan"],
    )
    town(
        "maragha",
        "Maragha",
        paragraphs(
            "A city that seems to enjoy some supernatural being's "
            "favour: round it grow rich orchards of a strange melon, "
            "green outside, red within and sweet as honey, and its sky "
            "is never clouded, so astronomers love it.",
        ),
        ruler="Atabeg Uzbek",
        answers_to=uzbek,
        place=p["azarbayjan"],
    )
    town(
        "baylaqan",
        "Baylaqan",
        paragraphs(
            "The chief city of Arran, in a river valley fed by many "
            "streams, with many mills, gardens and orchards. Its people "
            "are divided over a popular preacher who raves of a storm "
            "gathering in the east that will soon swallow them: some "
            "want him locked up or killed, others call him a seer.",
        ),
        ruler="the Atabegs of Azarbayjan",
        answers_to=uzbek,
        place=p["arran"],
    )
    town(
        "bajarvan",
        "Bajarvan",
        paragraphs(
            "A modest town, one of Mukan's chief cities, famous for "
            "being near the spring of the Water of Life.",
        ),
        place=p["mukan"],
    )
    town(
        "shamakhi",
        "Shamakhi",
        paragraphs(
            "The Shirvanshahs' capital, built wholly of stone at the "
            "foot of a mountain among gardens. It too claims to be near "
            "the Water of Life, and it keeps the Rock of Moses.",
        ),
        ruler="the Shirvanshahs",
        answers_to=w["shirvanshah"],
        place=p["shirvan"],
    )
    town(
        "barvan",
        "Barvan",
        paragraphs(
            "Gilan's chief city, known only for its bad name: no good "
            "houses, no good markets, and no great congregational "
            "mosque, only a few small ones. Its Divine aura is unusually "
            "low, 1.",
        ),
        ruler="the emir of Gilan",
        answers_to=w["emir_of_gilan"],
        place=p["gilan"],
    )
    town(
        "tiflis",
        "Tiflis",
        paragraphs("The capital of Georgia since Dawid II took it in 1121."),
        ruler="Giorgi IV Lasha",
        answers_to=w.get("king_of_georgia"),
        place=p["georgia"],
    )


# -- the factions --


def _factions(cradle: Cradle) -> None:
    b, w = cradle.b, cradle.world
    w["sabians"] = b.faction(
        "The Sabians of Harran",
        faction="Hedge coven",
        place=w["harran"],
        summary=paragraphs(
            "A cult of monotheist star-magicians centred on Harran, "
            "whom the Muslims first met in the ninth century. They are "
            "said to have died out, but some may live on, passing for "
            "Muslims to avoid trouble. The book gives no tradition "
            "record for them.",
        ),
    )
    w["ashipu"] = b.faction(
        "The Ashipu",
        faction="Hedge coven",
        place=cradle.places["jazira"],
        summary=paragraphs(
            "Priest-magicians, exorcists, among those who still worship "
            "the old gods, as at Harran or Mardin. Most of their craft "
            "is knowing demons' weaknesses (Infernal Lore) and making "
            "amulets against them; some have more active powers against "
            "demons and may belong to the Order of Suleiman. The book "
            "gives no tradition record for them.",
        ),
    )
    w["brass_smiths"] = b.faction(
        "The Brass-Smiths' Guild of Arzanjan",
        faction="Gild",
        rules="Loyalty to the guild, and its secret kept.",
        place=w["arzanjan"],
        summary=paragraphs(
            "The guild of Arzanjan's brass-smiths, whose members can "
            "shape brass by hand: a Minor Supernatural Virtue, Lesser "
            "Power, gained by the guild's Initiation, whose script "
            "always brings the Minor Flaw Vow (guild loyalty). "
            "Organization Lore: Arzanjani Brass-Smiths' Guild serves as "
            "its Mystery's Lore. A character may start with it, with "
            "the Vow and a score of 1 in that Lore.",
            "The power, Crafter of Brass: 1 Fatigue level, Init "
            "Quickness - 6, Terram; R: Touch, D: Conc, T: Ind. Brass the "
            "smith touches turns supple and can be reshaped, though not "
            "joined, so the pieces must still be cut out with care; in "
            "skilled hands it gives work of great intricacy and beauty. "
            "ReTe 15 (base 4, +1 Touch, +1 Conc, +1 intricacy), a Lesser "
            "Power of 15 levels, -2 Might cost.",
        ),
    )
