"""Vindolanda (Land of Fire & Ice, chapter 10, with the Sea Temple of pp.
122-124): the covenant, its sites and rooms, the Kerlingarfjoll valley,
Ammon and his rats, and the stories they hold.

The covenant stands outside every Tribunal. Its Place holds Scartaris, Old
Vindolanda and the two other sancta; the valley stands apart, in Iceland.
The chapter is for storyguides only, so a summary here says no more than a
stranger could learn, and all the rest is in secrets. Mechanics stay as the
book prints them, in words, where they are a story's: the four Scartaris
spells and the Obsidian Gate ritual are Fourth Edition texts, not catalog
spells. The app's shields draw no griffon, so the arms stay in words.

The creature blocks follow the pack's readings (see the package
docstring), with body levels as wound ranges."""

from __future__ import annotations

from ...arts import ARTS
from ...models import BodyVis, Covenant, Neighbour
from ...models.books import TEXT_SPELL
from ..builder import (
    Builder,
    characteristics,
    dormant,
    paragraphs,
    secrets,
    wound_ranges,
)

SOURCE = "LFI"
#: How far the book's sites are known: to those who were told.
LOCAL = "Locally"
HIDDEN = "Rumoured"
TRACK = "A track"
#: The Definitive Edition's Confidence for an important creature.
CONFIDENCE = (1, 3)

#: Scartaris's rooms outside the baths: (name, what is printed).
SCARTARIS_ROOMS: tuple[tuple[str, str], ...] = (
    (
        "Gate Room",
        "A chamber thirty paces square whose high vault rests on twelve "
        "pillar arches, each pillar carrying a perch made for a gargoyle; "
        "mosaics cover floor and walls. The gate from De Panne stands in an "
        "alcove in the south wall; two corridors run west and one north. In "
        "the southeast corner sits the brazier that lights and warms most "
        "of the sanctum (pp. 89, 91).",
    ),
    (
        "Laundry Room",
        "Twelve paces by ten. Stone basins along one wall run with warm "
        "water when working; a magical rack on the other wall dries any "
        "wet inanimate thing within a minute, by a Perdo Aquam effect (pp. "
        "89, 91).",
    ),
    (
        "Meeting Hall",
        "Twelve paces by seventeen, empty, and made impressive by the "
        "finely decorated ceiling (p. 89).",
    ),
    (
        "Kitchen",
        "Twelve paces by six and well equipped. A big magical oven stands "
        "by the west wall, its heat set by a user's concentration. The "
        "fountain here is Scartaris's drinking water: it draws and purifies "
        "water from a deep shaft into a glacial fissure, as often as wished "
        "and for as long as the user concentrates. A wooden partition "
        "enchanted against putrefaction closes off the larder (pp. 89, 91).",
    ),
    (
        "Latrine",
        "Eight paces by six, with stone benches on the north and south "
        "walls whose holes open on the drainage that destroys inanimate "
        "matter (p. 89).",
    ),
    (
        "Servants' Quarters",
        "Twelve paces by eight, divided into four sleeping closets (p. 89).",
    ),
    (
        "Store Rooms",
        "Two small rooms beside the laundry room, printed only on the map (p. 90).",
    ),
    (
        "Library",
        "Twelve paces by ten, with four lecterns and four writing desks. "
        "About fifty books stand on their own lecterns along the walls, "
        "with room for ten times as many, and an enchantment preserves "
        "them. Iain's accounts and ledgers lie among them; the book "
        "promises details that it never gives (pp. 89, 91-92).",
    ),
    (
        "Victor's Private Chambers",
        "Lectern, writing desk, bed, chests and cabinets, with Victor's "
        "sanctum marker on the door (p. 89).",
    ),
    (
        "Victor's Lab",
        "Victor's body remains within the ward in the western corner. The "
        "laboratory is equipped but holds no consumables, and a season's "
        "work would make it usable. His sanctum marker is on the door (p. "
        "89).",
    ),
    (
        "Iain's Private Chambers",
        "Lectern, writing desk, bed, chests and cabinets, with signs of "
        "only occasional use, and Iain's sanctum marker on the door. A "
        "strongbox by the bed holds 500 pounds of silver; a box under the "
        "bed holds a pair of unused gatestones (pp. 89-90).",
    ),
    (
        "Iain's Lab",
        "Equipped for a Natural Magician, with Iain's sanctum marker on "
        "the door (p. 89).",
    ),
    (
        "Weapons Yard",
        "Forty paces by ten, where Vindolanda's grogs once trained. The "
        "training gear left here is too brittle with age to use (p. 90).",
    ),
    (
        "Secret Tunnel",
        "The way out: two miles of stairs ending on the southern slope of "
        "Snaefell about 500 paces above the sea. Victor dug it as an "
        "exploration tunnel, climbing nearly a thousand paces. Its mouth "
        "is well hidden and unremarkable, about three miles from the "
        "nearest farmstead (pp. 89-90).",
    ),
)

#: The rooms of the baths at Scartaris.
SCARTARIS_BATHS: tuple[tuple[str, str], ...] = (
    ("Apodyterium", "The changing room (p. 89)."),
    (
        "Tepidarium",
        "The warm room, warm but bearable when working (p. 89).",
    ),
    (
        "Caldarium",
        "The hot room, steamy when working, with alcoves in its walls "
        "giving continuous plunges of hot water, hotter from one to the "
        "next (p. 89).",
    ),
    (
        "Laconicum",
        "A round chamber of dry heat, set apart from the baths to stay "
        "dry; the higher the tier of seats, the greater the heat (p. 89).",
    ),
    (
        "Frigidarium",
        "A round chamber full of cold water, which those leaving the "
        "laconicum should plunge straight into (p. 89).",
    ),
    (
        "Great Bath",
        "A rectangular bath 22m by 8.8m and 1.5m deep, with pleasantly hot "
        "water flowing through and steps around its edges. Two big silver "
        "vessels half hidden in the chamber's western wall feed all the "
        "baths, one with steaming water, one tepid (pp. 90-91).",
    ),
    (
        "Lucas Bath",
        "A tepid bath to cool the body before the return to the apodyterium (p. 90).",
    ),
    (
        "Smaller Baths",
        "Three baths: one by the weapons yard for combatants to wash, one "
        "by the southern caldarium as fierce as that room, and one off the "
        "southern tepidarium, tolerably cold (p. 90).",
    ),
)

#: The Sea Temple's rooms. Those marked * in the book stand under six
#: inches of water, with silt and debris on the floor.
SEA_TEMPLE_ROOMS: tuple[tuple[str, str], ...] = (
    (
        "Vindolanda Gate",
        "A chamber five paces square, with a passage east and the gateway "
        "to the Northumbrian site in an alcove in the west wall. Six "
        "inches of water; silt and debris (p. 123).",
    ),
    (
        "Kerlingarfjoll Valley Gate",
        "A chamber five paces square, with a passage west and the gateway "
        "to the hidden Icelandic valley in an alcove in the east wall. "
        "Unlike the archways the magi of Vindolanda made, this gatestone "
        "is the capstone of a trilithon. Six inches of water; silt and "
        "debris (pp. 123-124).",
    ),
    (
        "Library",
        "Twelve paces by ten, with four lecterns, four writing desks and "
        "about forty books in untidy piles on tables, under an enchantment "
        "of preservation: 900 levels of spells and 360 levels of books, "
        "with Ealasaid's translation notes and lab notes. Six inches of "
        "water; silt and debris (p. 124).",
    ),
    (
        "Latrine",
        "Eight paces by six, with stone benches on the north and south "
        "walls whose holes open on the drainage that destroys inanimate "
        "matter. Six inches of water; silt and debris (p. 124).",
    ),
    (
        "Bath",
        "Its magic items still work and, though three centuries of water "
        "have widened the drain, the bath stays warm and clean. The flood "
        "first stood about three feet deep here, until the drains of bath "
        "and latrine drew it down to the room's lowest drainage point. Six "
        "inches of water; silt and debris (p. 124).",
    ),
    (
        "Ealasaid's Private Chambers",
        "Her sanctum marker hangs on the remains of the door. A rotten bed "
        "and clothes chest, a writing desk, and on the lectern her last "
        "lab text, close to finishing the calling ritual for the Obsidian "
        "Gate. Six inches of water; silt and debris (p. 124).",
    ),
    (
        "Ealasaid's Lab",
        "Wholly submerged, its equipment past saving. Clay and basalt "
        "tablets here, in cuneiform and hieroglyphics, are how she "
        "identified the names and natures of the gateways' spirits (p. "
        "124).",
    ),
    (
        "Sea Dome Temple",
        "A round chamber thirty paces across, now open to the sea, with "
        "steps up to an altar. Its thick granite dome, enchanted to "
        "transparency, lies on the floor under four feet of sand, silt and "
        "sea life. Restored, the temple would give +5 to magical summoning "
        "rituals; spirits of the sea and secretive spirits such as "
        "Lucifugus (Hedge Magic p. 77) favor it greatly. A fresh-water "
        "spring feeds a fountain in the altar, which yields twelve pawns "
        "of Intellego vis at the winter solstice each year (p. 124).",
    ),
    (
        "Exit Tunnel",
        "The first way in, eight miles long, ending in a cave in a cliff (p. 124).",
    ),
    (
        "Ealasaid's Gate",
        "An archway wholly flooded and full of silt. Its gatestone joins "
        "Macomb's sanctum but is out of position and cannot be used (pp. "
        "123-124).",
    ),
)

SCARTARIS_MAGIC = (
    "Magic items run the sanctum; most were bought from House Verditius with "
    "the vis found when Iceland was first explored, and a single tome in the "
    "library sets out how each works (p. 90). The brazier in the Gate Room "
    "gives light like sun through cloud to every room but the sancta, "
    "sleeping chambers and library, through window-like shapes in the "
    "ceilings; an Imaginem requisite shows open sky in them. It runs on "
    "unattended or may be switched twenty-four times a day. Its Creo and "
    "Perdo also hold the main rooms at one temperature, set by touch and "
    "concentration (p. 91). Sancta, library, private chambers and servants' "
    "quarters each have an item giving a strange shadowless light, switched "
    "twenty-four times a day (p. 91). Each room of the baths has a heating "
    "or cooling item set by touch and concentration, and all start inactive "
    "(p. 91). Lead-lined channels carry the bath water, and lead-lined "
    "drains take the overflow to a big bronze vat whose Perdo effect "
    "destroys everything inanimate but metal and gems (p. 91). A Structure "
    "version of Chamber of Spring Breezes keeps the air fresh (p. 91)."
)

BATHS_WORK = (
    "The baths are dry and their items inactive (p. 92). To restore them, "
    "learn each item's activation, then balance heat and flow carefully. "
    "Brought up step by step from modest settings, all is well. Turned on at "
    "full power, the caldaria do +5 damage a round, the laconicum +10, and "
    "the frigidarium freezes and floods. Full working order takes about a "
    "month, then about an hour a week of adjustments, at least two full-time "
    "attendants (more with heavy use), and a season of a mason's repairs "
    "every five years."
)


def build(b: Builder) -> None:
    home = _home(b)
    scartaris = _scartaris(b, home)
    old = _old_vindolanda(b, home)
    _glyder_fawr(b, home)
    _sea_temple(b, home)
    valley = _valley(b)
    # The saga part builds the arc before this valley exists.
    arc = next(n for n in b.saga.neighbours if n.name == "Spider in the Ice")
    arc.place_id = valley.id
    covenant = _covenant(b, home)
    _library(b, covenant)
    _bestiary(b, old)
    _stories(b, scartaris, old)


def _room(
    b: Builder, name: str, inside: Neighbour, site: str, words: str, *hidden: str
) -> Neighbour:
    return b.place(
        f"{name}, {site}",
        summary=f"A room of the {site} sanctum.",
        secrets=paragraphs(words, *hidden),
        inside=inside,
        known=LOCAL,
    )


def _home(b: Builder) -> Neighbour:
    return b.place(
        "Vindolanda",
        summary="The holdings of the covenant of Vindolanda, in sites far "
        "apart. It keeps no single home that a stranger could visit.",
        aura=5,
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "The covenant's main site in Northumberland never held a "
            "sanctum: each magus's sanctum lay elsewhere, joined to it by a "
            "Gatestone. None of those gates works now except the one into "
            "Scartaris, which Lord Peter stole from De Panne (p. 88). The "
            "aura here is that of Scartaris, the only site in use.",
            "The Northumbrian site is rubble in an Infernal aura; Macomb's "
            "sanctum has collapsed; Ealasaid's is partly flooded and full of "
            "sea life. The gateways to both lie buried in the wreck of the "
            "main site, and the gatestone to the Temple valley is in "
            "Ealasaid's sanctum. As the saga is written, the magi find "
            "these only after Brighde's Gauntlet (p. 88).",
            "The book's saga adds neither Liam's sanctum nor Iain's "
            "original one, and leaves a storyguide free to invent these or "
            "any others. Being gruagachan, neither man needed a laboratory "
            "(p. 96).",
        ),
    )


def _scartaris(b: Builder, home: Neighbour) -> Neighbour:
    site = "Scartaris"
    scartaris = b.place(
        site,
        summary="A hidden sanctum of the covenant of Vindolanda.",
        aura=5,
        inside=home,
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "The first sanctum Vindolanda made, deep inside the southern "
            "peak of Snaefell, in a +5 magical aura. The volcano stands "
            "just over 1440 paces high near the tip of the Snaefellsnes "
            "peninsula, which runs some forty miles into the Atlantic; it "
            "can be seen a hundred miles off, and two main peaks stand "
            "north and south of its crater (pp. 88-89).",
            "When the Carnac gateway opened, the magi found the Temple "
            "valley and then Iceland, and learned how rich the island was "
            "in vis. The temple was plainly tied to Damhan-Allaidh, so it "
            "was unsafe. Scartaris gave easy access to the vis in a place "
            "he did not know (p. 88).",
            "There are only two laboratory areas, both taken by the elders "
            "Victor and Iain, and quarters for a handful of covenfolk. "
            "There is no vis supply, no servants but those the magi bring, "
            "and a library with only the basics on the Arts (p. 88). New "
            "magi must carve their own space from the mountain with the "
            "library's spells (p. 90).",
            SCARTARIS_MAGIC,
            "The whole peninsula is full of trolls, enemies of the covenant "
            "(p. 89; their statistics are on p. 30).",
        ),
    )
    for name, words in SCARTARIS_ROOMS:
        _room(b, name, scartaris, site, words)
    baths = b.place(
        f"The Baths, {site}",
        summary="The bathing rooms of the Scartaris sanctum.",
        inside=scartaris,
        known=LOCAL,
        secrets=BATHS_WORK,
    )
    for name, words in SCARTARIS_BATHS:
        b.place(
            f"{name}, {site}",
            summary="A room of the baths of Scartaris.",
            secrets=words,
            inside=baths,
            known=LOCAL,
        )
    return scartaris


def _old_vindolanda(b: Builder, home: Neighbour) -> Neighbour:
    return b.place(
        "Old Vindolanda",
        summary="The remains of one of the great Roman supply forts of "
        "Hadrian's Wall, halfway along it, about a mile northwest of the "
        "village of Bardon Mill in Northumberland. The site is hard to "
        "find, and those who look for it meet with accidents.",
        realm="Infernal",
        inside=home,
        ruined=True,
        secrets=paragraphs(
            "The covenant restored the fort to its full splendor and hid it "
            "from mundane notice with illusions and a kind of The Shrouded "
            "Glen. South of the wall, it still allied with Loch Leglean in "
            "the Praeses Septentrionalis. Damhan-Allaidh took it in 889, "
            "and a Hermetic army under Tremere and Flambeau magi then "
            "reduced it to rubble (p. 93).",
            "Many innocent locals and covenfolk died in that attack. "
            "Damhan-Allaidh had penned them up to feed his sacrifices, and "
            "the Tremere and Flambeau leaders chose to leave no witnesses. "
            "His sacrifice and their murder both served Hell. The Shrouded "
            "Glen kept the dead from Christian burial, and every night "
            "their shades relive their end and beg for mercy. That stain "
            "overcame the magic aura, and an Infernal regio took its place "
            "(p. 93).",
            "Finding the site takes a Perception stress roll of 12+ past "
            "the corrupted illusion and Shrouded Glen, and anyone trying "
            "will likely suffer an accident. Ammon, once Hetep's minion, "
            "rules the three-level regio with a score of infernal beasts "
            "(p. 93).",
            "Infernally tainted Mentem vis can be harvested on the middle "
            "level: tiny white salt crystals, formed from the ghosts' "
            "tears, which the demon sends down to draw more magi; the book "
            "prints no amount. Magi distrust the source because the covenant "
            "that first claimed the site belonged to ill-fated Castrum "
            "Antiquum (Heirs to Merlin p. 15). Burnham holds the harvesting "
            "rights by a legal settlement, went once, read the history, and "
            "means to pass the site to the next naive young covenant it can "
            "steer into a swap (p. 93).",
            "The gatestones lie on the top level under tons of rubble. "
            "Ammon bars magi from that level, so a spell must penetrate his "
            "Might to reach it. If the magi have followed Hetep here, the "
            "Sea Temple gatestone is already dug out and set up (pp. "
            "93-94).",
            "Once the infernal creatures are banished or killed, Christian "
            "burial for the victims of both Damhan-Allaidh and the Order "
            "can destroy the regio, and within a decade the place becomes a "
            "two-level magical regio (+2, +4). Digging while the Infernal "
            "regio stands draws further attacks, and many workers die in "
            "accidents (p. 94).",
            "The map (p. 93) shows the walled fort, with four barracks, stables "
            "on two sides, a granary, the headquarters, two storehouses and a "
            "catapult platform on one corner; beyond its wall stand the bath "
            "house, the mansio and the married quarters.",
        ),
        levels=[
            b.level("Lowest level", 1, "Infernal"),
            b.level(
                "Middle level",
                3,
                "Infernal",
                notes=secrets(
                    "", "Infernally tainted Mentem vis is harvested here (p. 93)."
                ),
            ),
            b.level(
                "Top level",
                6,
                "Infernal",
                notes=secrets(
                    "",
                    "Ammon admits no magus here, and a spell must defeat his "
                    "Might of 40. The gatestones lie under tons of rubble "
                    "(pp. 93-94).",
                ),
            ),
        ],
    )


def _glyder_fawr(b: Builder, home: Neighbour) -> Neighbour:
    return b.place(
        "Glyder Fawr Sanctum",
        summary="Glyder Fawr is a Welsh peak just under a thousand paces "
        "high, north of Snowdon and about ten miles east of the port of "
        "Caernarfon, off the pass of Llanberis.",
        aura=7,
        inside=home,
        ruined=True,
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "Ealasaid's first sanctum and later Macomb's, about 100 paces "
            "under the peak in a powerful +7 magical aura. Fleeing threats "
            "from Diedne magi, she had left her Welsh home before Pralix "
            "reached Britain; when the magi of Vindolanda set up sancta far "
            "from their main site she reclaimed her ancestral lands, near "
            "Cad Gadu, and later left this one to Macomb on moving to the "
            "Sea Temple (p. 94).",
            "A cave system lower on the southern side gives on to the "
            "passage, but the way in through Macomb's lab is blocked for "
            "about ten paces and the lab cannot be crossed (pp. 94-95). The "
            "characters will most likely come by the gatestone in Old "
            "Vindolanda (p. 95).",
            "The aura suited Macomb's and Ealasaid's ritual magic. They "
            "advised Victor on a temple to raise the site's power further, "
            "and it did better than they hoped, but the aura proved too "
            "strong for servants to live here safely, so covenfolk never "
            "used the quarters. Macomb's apprentice had one closet when "
            "Damhan-Allaidh came (p. 95).",
            "Macomb died quickly. His apprentice called up elemental spirits "
            "and set them on the attacker; the fight brought down most of "
            "the sanctum and drove Damhan-Allaidh off, but the apprentice "
            "was dead by then (p. 95).",
            "The map (p. 95) shows on the upper level storage, a kitchen, a "
            "meeting hall, a latrine, a bath, servants' quarters, the gate "
            "room and the temple; on the lower level storage, vis storage, "
            "Macomb's quarters, Macomb's lab, Ealasaid's Gate, and the "
            "altar passageway.",
            "Two earth elementals called by the apprentice remain: see "
            "Cadell and Enan.",
        ),
    )


def _sea_temple(b: Builder, home: Neighbour) -> Neighbour:
    site = "Sea Temple"
    temple = b.place(
        "Sea Temple Sanctum",
        summary="A sanctum of the covenant of Vindolanda, whose whereabouts "
        "its builder told no one.",
        inside=home,
        ruined=True,
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "Ealasaid's sanctum and the magi's last and boldest work, about "
            "eight miles due west of the isle of Lundy, under the sea "
            "between Devon and Wales. Thothian spirits led her to a magical "
            "site suited to her research on the Obsidian Gateway, on "
            "condition that she alone should know where it lay. She drove a "
            "tunnel of nearly eight miles under the sea and cast Carve the "
            "Mythic Chambers about ten paces below the seabed. The crystal "
            "dome rose from the seabed over a magical spring (pp. 94, "
            "122-123).",
            "Just before she died she had found the name of the spirit "
            "serving the Obsidian Gateway and had begun rebuilding its "
            "ritual. Damhan-Allaidh surprised her under the dome, her "
            "theurgy too slow to save her, and raised her ghost to torture "
            "out where Victor and Hetep were. Months later a Tremere and "
            "Flambeau force beat his army and he fled here, hurt and spent, "
            "and found Liam freeing her ghost. The two gruagachan took beast "
            "shape and fought. Even so Liam lost. When he lay incapacitated "
            "her spirit ordered an earth elemental to shatter the dome: the "
            "fall crushed both men's bodies and flooded most of the "
            "structure, and her ghost, its purpose done, rested (p. 123).",
            "Liam and Damhan-Allaidh have lain incapacitated under the "
            "rubble for over three hundred years, sea creatures feeding on "
            "their ever-mending bodies. Chapter 18's statistics are their "
            "state if freed and left to recover. Hermetic magic at Instant "
            "duration cannot mend their distortions, though spells may give "
            "brief relief, and both slowly lose their reason (pp. 122-123).",
            "Victor and Iain can tell the players nothing of where it lies. "
            "The way in is the gatestone at Old Vindolanda; the gatestone "
            "from Glyder Fawr is out of position (p. 123). The book also "
            "gives the trilithon from the valley (p. 96) and the exit tunnel "
            "(p. 124).",
            "The library holds all that is needed to recreate Ealasaid's "
            "work on the Obsidian Gateway. Twenty sets of her lab notes, "
            "once translated and written up, each serve as a Quality 2 "
            "Tractatus in Occult Lore (or Theurgy, with The Mysteries), and "
            "all must be studied first. Her personal translation notes are "
            "hard going: each studies as a Summa, Quality 0, on Speak "
            "Ancient Egyptian (Level 4), Scribe Hieroglyphics (3), Speak "
            "Assyrian (3) or Scribe Cuneiform (3). Using the tablets in her "
            "lab takes at least 3 in both Speak Ancient Egyptian and Speak "
            "Assyrian and at least 2 in both Scribe Hieroglyphics and Scribe "
            "Cuneiform. The ritual must be designed at level 40 (p. 124).",
            "Hetep frees Damhan-Allaidh here in Brighde's Gauntlet, after "
            "casting a Creo Auram spell on the chamber; the Hermetic "
            "equivalent is Sanctuary Beneath the Waves, CrAu (req Re) 30, "
            "Touch, Moon, Room, which makes air on the bed of a large body "
            "of water within an existing enclosure with clear bounds (p. "
            "122).",
        ),
    )
    for name, words in SEA_TEMPLE_ROOMS:
        _room(b, name, temple, site, words)
    return temple


def _valley(b: Builder) -> Neighbour:
    valley = b.place(
        "Kerlingarfjoll Valley",
        summary="A valley shut in by glacier-topped mountains, 30 km "
        "southwest of the peak of the Hofsjokull glacier.",
        inside=next(n for n in b.saga.neighbours if n.name == "Iceland"),
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "Warm, green and fertile, about four miles long and a mile wide, "
            "with a small river through it; steam vents keep it warm and "
            "wrapped in mist (p. 96). Its mundane level is only fertile "
            "grassland.",
            "A powerful ancient enchantment beats back all who try to climb "
            "in with rising wind and weather. It has a Penetration of +120 "
            "and also acts as a level 120 Aegis around the valley, but does "
            "not hinder the magic of creatures inside. A Wind of Mundane "
            "Silence strong enough for a level 120 spell overcomes it for "
            "Sun duration (p. 96).",
            "Around 30 June the warding fails for about two and a half "
            "minutes, one diameter, at midnight, and the mundane level can "
            "then be found. Only Hetep knows this, having been present when "
            "Setna made the ward (p. 96).",
            "The upper levels can be reached only with magic. A Perception "
            "+ Second Sight roll of 15+ moves a character between levels, "
            "and spells for that must penetrate a Magic Resistance of 30 "
            "(p. 96).",
        ),
        levels=[
            b.level(
                "First magical level",
                4,
                notes=secrets(
                    "",
                    "A ruined temple in the Egyptian style, one mile long and "
                    "half a mile wide, warmer than below with the sun higher "
                    "in the sky (p. 96).",
                ),
            ),
            b.level(
                "Top level",
                9,
                notes=secrets(
                    "",
                    "Printed as the third level of a two-tier regio. It "
                    "covers only the temple complex and walkway, whole here, "
                    "in a Mediterranean climate, and the stars agree with "
                    "Memphis in Egypt. The sacred architecture is bent on "
                    "opening the gateway, so other magic that would gain from "
                    "the aura does not; Infernal powers still take the usual "
                    "-9 to Penetration (pp. 96-97).",
                ),
            ),
        ],
    )
    b.place(
        "Temple of Thoth, Kerlingarfjoll",
        summary="An Egyptian temple at the top of the valley's regio.",
        inside=valley,
        level=2,
        status=HIDDEN,
        known=LOCAL,
        secrets=paragraphs(
            "A paved road runs about a hundred paces to the entrance, under "
            "five trilithons with enchanted lintels. Four are useless, their "
            "partners destroyed; the one farthest from the temple leads to "
            "Ealasaid's Lundy sanctum, and once stood in a cave near Carnac "
            "(p. 96).",
            "Within stands the Obsidian Gateway, a solid block shaped into "
            "an arch eight paces wide, sixteen high and a meter thick. The "
            "Thothian priests found it, and it joins its twin in the "
            "Obsidian Temple. Hieroglyphics on the walls tell of Setna's "
            "journey here, the raising of the temple, and his passage "
            "through the gate into the presence of Thoth (p. 96).",
            "Any Gifted person who sees the Gate longs to go through. The "
            "first time a magus touches it he falls in a fit and sees "
            "Damhan-Allaidh as he was in 681, shadow twisted and eyes "
            "darkened, stepping through after a ritual; a dark wave then "
            "runs from the gate, warping the hieroglyphics and wall images "
            "into demonic shapes; then the Order falls to diabolism, cunning "
            "folk burn, and crusaders put books and scholars to the torch "
            "and sword. It ends in a wordless plea for help. A magus who "
            "offers help rolls once on the Good Effects table (ArM4 p. 182), "
            "one who refuses on the Bad Effects table; either way he gains "
            "only one Twilight point (p. 97).",
            "Call of the Obsidian Serpent, ReVi 40 ritual (R: Spec, D: Spec, "
            "T: Ind), does not truly summon the daemon of the gate but draws "
            "its attention and asks it to come. It works only in this "
            "temple, on or around the last day of June; Ealasaid's notes "
            "give the date with Int + Artes Liberales 9+. It takes two hours, "
            "four from text, and must end at midday, timed by a shaft of "
            "light. The leader anoints the gate and declares his intent to "
            "summon its spirit, extols the spirit, chants the sacred words "
            "from Ealasaid's grimoire, and commands it to open as the light "
            "strikes the gateway's radial point. The oil takes eight pawns "
            "of Vim or Rego vis, serves as the ritual's vis, and takes a day "
            "in a lab. With The Mysteries, casting from text may need "
            "Theurgy 8; without Theurgy the spell must be learned and "
            "mastered. The gate then stays open while the caster "
            "concentrates (p. 97).",
        ),
    )
    return valley


def _covenant(b: Builder, home: Neighbour) -> Covenant:
    return b.covenant(
        "Vindolanda",
        founded=816,
        season="Winter",
        place=home,
        aura=5,
        summary="An early covenant of the Order of Hermes in northern "
        "England, which the Order reported destroyed in 889.",
        what_matters=paragraphs(
            "Boon: Mystical Portal (gatestones between its sites)\n"
            "Boon: Difficult Access (a hidden stair inside a mountain)\n"
            "Boon: Seclusion (no one outside knows where it is)\n"
            "Hook: Poverty (Minor) (no vis supply, no servants, the bare "
            "basics in its library)\n"
            "Hook: Monster (Minor) (trolls of the peninsula)\n"
            "Hook: Dark Secret (what its elders keep from the Order)\n"
            "Hook: Massacre Site (the ruin of its first home)"
        ),
        secrets=paragraphs(
            "Its symbol is a red griffon with claws raised, on a white field. "
            "Founded in 816. Its members: Victor filius Pralix, a leading "
            "figure of House Ex Miscellanea, now possessing the body of "
            "Brighde; Ealasaid filia Morwena, died 889; Macomb filius "
            "Ealasaid, died 889; Liam the Shapeless, filius of Brude, "
            "disappeared 889; and Iain the Unbowed, filius Liam. All followed "
            "Ex Miscellanea (p. 88). The book's list styles Victor founder of "
            "the House, a title only: Pralix founded it (p. 71).",
            "The players hold only Scartaris at first. Victor stays "
            "Disceptator but leaves the daily running to Iain, who gives "
            "funds and advice; Victor calls dreamscape councils only when "
            "he must, since holding Hetep takes most of his attention (p. "
            "87).",
            "The oath gives up every tie to another covenant for lasting "
            "loyalty to this one, and binds each member to its Charter, its "
            "council and its fellow members' lives, and to fight Damhan-Allaidh "
            "and his servants until nothing of him or his work is left. By the "
            "Charter all property serves the covenant. The Disceptator "
            "is elected by the members and holds office until death or "
            "final Twilight, breaks ties and may delegate. The Council is "
            "all the members, meeting around solstices and equinoxes, or in "
            "an emergency at the Disceptator's call. Each member owes seven "
            "seasons of covenant work a Tribunal period unpaid, and further "
            "work earns three pawns a season; work is set by Petition to the "
            "Council. An expelled magus must leave within a day (p. 85).",
        ),
    )


def _library(b: Builder, covenant: Covenant) -> None:
    hidden = [
        (
            "Eyes of the Gnome",
            30,
            "InTe, R: Per, D: Sun, T: Spec. Sees through up to a thousand "
            "paces of rock and reads its formation, senses the stability of "
            "any part within 100 paces, and shows detail within 15 (p. 91).",
        ),
        (
            "Carve the Mystic Tunnels",
            25,
            "PeTe req Re, R: Touch, D: Spec, T: Spec. Destroys earth or rock "
            "before the caster as he walks, shoring the tunnel while the "
            "spell lasts, until he comes out or Sun duration ends. An "
            "unsupported tunnel may fall soon afterward; Eyes of the Gnome "
            "may find a route through stable rock (p. 91).",
        ),
        (
            "Soothing the Earth's Wound",
            20,
            "MuTe req Re, printed T: Touch, D: Sun/Inst, T: Spec. Turns the "
            "surfaces of a tunnel or chamber to clay and fuses the cracks, "
            "leaving an unbroken solid up to a pace thick. Best on rock; in "
            "earth it packs tight enough for dry ground, and vis makes the "
            "material granite, which holds even in earth (pp. 91-92).",
        ),
        (
            "Carve the Mystic Caverns",
            40,
            "PeTe req Mu, R: Touch, D: Inst, T: Str, Ritual. Carves a huge "
            "underground structure to the caster's complete design, changes "
            "the surrounding stone to granite, and may face it in any stone "
            "up to the finest marble and complex mosaic. Unlike Conjure the "
            "Mystic Tower it depends on the caster's skill: elaborate work "
            "may need Int + Architecture for lasting stability (p. 92).",
        ),
    ]
    tomes = []
    for name, level, words in hidden:
        text = b.book(
            covenant,
            name,
            "Lab Text",
            level=level,
            author="Timon, follower of Tremere",
            description=f"A spell of the Grimoire of the Hidden. {words}",
        )
        text.text_kind = TEXT_SPELL
        tomes.append(text)
    b.codex("Grimoire of the Hidden", tomes)
    hearth = b.book(
        covenant,
        "Grimoire of the Hearth",
        "Lab Text",
        level=20,
        author="Notatus, filius of Bonisagus",
        description="One Aegis of the Hearth at level 20, with notes on its "
        "design and its place in Hermetic Theory. It was rebound with notes on "
        "designing a like ritual for underground structures, a Structure "
        "version working 5 levels higher than its spell level (p. 92).",
    )
    hearth.text_kind = TEXT_SPELL
    volumes = [
        b.book(
            covenant,
            f"Encyclopedia of the Hermetic Arts: {art}, Target {target}",
            "Tractatus",
            art=art,
            quality=13,
            author="Cato, filius of Bonisagus",
            description=f"Part of a work printed as Libri quaestionum on all "
            f"the Arts at Target 0 and Target 3, Quality 13, bound in five "
            f"volumes (p. 92). This one has Target {target}.",
        )
        for art in ARTS
        for target in (0, 3)
    ]
    b.codex("The Encyclopedia of the Hermetic Arts", volumes)
    b.book(
        covenant,
        "Principia Hermetica",
        "Ability Summa",
        ability="Magic Theory",
        author="Bonisagus",
        description="In full: Principia Hermetica: Compendium de Principiis "
        "Hermeticae Magia, vel de Formis et Potentiis Vis Occultae, ac de "
        "Invocatione, Abjuratione, Transmutatione, Conjuratione et "
        "Divinatione. An authority on Hermetic Theory in one tome; the book "
        "prints no level or quality (p. 92).",
    )
    b.book(
        covenant,
        "Enchantments",
        "Other",
        description=secrets(
            "Short descriptions and instructions for the enchantments of the "
            "covenant's sites (p. 92).",
            "They cover Scartaris, Glyder Fawr and the Sea Temple, hold nothing "
            "Hermetic on making them, and cannot serve as lab texts.",
        ),
    )
    mundane = (
        ("The Heavens", "Ability Summa", "Artes Liberales", 5, 9),
        ("On Architecture", "Ability Summa", "Craft: Architecture", 5, 10),
        ("On the Gods (Legend Lore)", "Tractatus", "Magic Lore", None, 9),
        ("Asclepius", "Ability Summa", "Philosophiae", 5, 7),
        ("On the Gods (Philosophiae)", "Tractatus", "Philosophiae", None, 6),
        ("Pupil of the World", "Tractatus", "Infernal Lore", None, 6),
    )
    for name, kind, ability, level, quality in mundane:
        b.book(
            covenant,
            name,
            kind,
            ability=ability,
            level=level,
            quality=quality,
            description="A mundane book of the Scartaris library (p. 92).",
        )


def _bestiary(b: Builder, old: Neighbour) -> None:
    b.creature(
        "Ammon, Master of the Hidden Revels",
        page="p. 94",
        source=SOURCE,
        realm="Infernal",
        might=40,
        size=2,
        place=old,
        confidence=CONFIDENCE,
        tires=False,
        fatigue_levels="Tireless",
        soak=14,
        block={
            "characteristics": characteristics(1, 1, -6, 0, 8, 12, 3, 0),
            "traits": {"Cruel": 6, "Secretive": 3, "Cautious": 2},
        },
        attacks=[b.attack("Claws", 8, 11, 8, 10)],
        powers=[
            b.power(
                "Weight of a Thousand Hells",
                1,
                -1,
                "Mentem",
                level=25,
                does="CrMe 25, as the Hermetic spell (ArM4 p. 145).",
            ),
            b.power(
                "Control Regio",
                0,
                0,
                "Vim",
                level=40,
                does="ReVi 40. Decides who enters or leaves his regio; "
                "spells to travel between its levels must defeat his Infernal "
                "Might of 40.",
            ),
            b.power(
                "The Unblinking Eye",
                0,
                0,
                "Imaginem",
                level=30,
                does="InIm 30. Moves his sight to any point within the regio; "
                "neither Parma nor any Hermetic effect detects it.",
            ),
            b.power(
                "Sow Discord",
                1,
                -1,
                "Mentem",
                level=10,
                does="CrMe, MuMe 10. Quietly makes or changes the emotions of "
                "people in his regio, to steer his visitors. An Int roll of "
                "9+, modified by relevant Personality Traits, recognizes the "
                "urge as unnatural.",
            ),
            b.power(
                "Ill Fortune",
                2,
                -2,
                "Vim",
                level=30,
                does="CrVi 30. The victim botches automatically on any stress "
                "roll of 0.",
            ),
        ],
        vis=[
            BodyVis(8, "Corpus", "body"),
            BodyVis(4, "Perdo", "heart"),
            BodyVis(4, "Mentem", "brain"),
        ],
        appearance="A dried corpse in the remains of fine robes.",
        notes=paragraphs(
            "The block's full title is Ammon, Master of the Hidden Revels, "
            "Torturer of the Dead.",
            wound_ranges(2),
            "Converted: the printed body levels (OK, 0, 0, -1, -1, -3, -5, "
            "Incapacitated, Banished) become the Definitive Edition's wound "
            "ranges; Confidence is the baseline, as the block prints none; "
            "printed power costs and levels are kept. The book gives no "
            "Might Form, Range, Duration or Target.",
        ),
        secrets=paragraphs(
            "Making the regio tied Ammon to a physical form inside it: he "
            "can be hurt by physical attack and cannot withdraw. If it is "
            "assaulted he defends it until banished. He has gained no new "
            "souls in a hundred years and hopes to be beaten, so he lets "
            "attackers retreat, with mocking insults to bring them back (p. "
            "94).",
        ),
    )
    b.creature(
        "Infernal Rat Swarm",
        page="p. 95",
        source=SOURCE,
        realm="Infernal",
        might=5,
        size=-4,
        place=old,
        cunning=True,
        how_many="Each swarm is about a hundred rats; the block's heading prints (10)",
        block={
            "characteristics": characteristics(2, 2, -6, 0, -7, -3, 0, 1),
            "traits": {"Curious": 2, "Greedy": 1, "Vicious": 3},
        },
        powers=[
            b.power(
                "Swarm",
                0,
                1,
                "",
                does="Bites all exposed flesh. The storyguide rules on "
                "protection; armor does not add to Soak. Damage roll each "
                "round: loose clothes 9 + stress die; sturdy clothing 6; "
                "winter garb or hauberk 3; half armor 0; full armor -3; full "
                "armor with helm and gauntlets -6.",
            ),
        ],
        notes=paragraphs(
            "Might and Size are each rat's. A victim kills rats equal to his "
            "Brawl + Dex a round, and the swarm retreats once over half are "
            "dead. A spell over an area, such as Arc of Fiery Ribbons, may "
            "kill a whole swarm if well placed, but cast on a swarm already "
            "biting it catches the victim as well.",
            "Converted: the book prints no attack or Soak. It prints the "
            "block beside Ammon's and names no place for it, so it is set "
            "here among his infernal beasts.",
        ),
    )


def _stories(b: Builder, scartaris: Neighbour, old: Neighbour) -> None:
    b.faction(
        "Cadell and Enan",
        faction="Spirits and beings",
        summary="Two earth spirits at Glyder Fawr.",
        realm="Magic",
        place=next(n for n in b.saga.neighbours if n.name == "Glyder Fawr Sanctum"),
        secrets=paragraphs(
            "Two earth elementals left from those Macomb's apprentice "
            "called. Cadell is eager for a fight but will not strike "
            "unprovoked. Enan is more thoughtful and tries to talk a party "
            "into leaving. Both are good-natured and hold back from lethal "
            "force unless seriously threatened. Magi who convince them they "
            "belong to Vindolanda are welcomed and told of the battle with "
            "Damhan-Allaidh (p. 96).",
            "If the magi want the site back, Enan raises the rent: the "
            "original deal with Vindolanda was one pawn each a year. They "
            "open at over six hundred pawns (one a year each), can be "
            "talked down to around sixty over the next decade, and for a "
            "suitable consideration may restore the site as well (p. 96). "
            "The book prints no statistics for them.",
        ),
    )
    dormant(
        b.threat(
            "The Trolls of Snaefellsnes",
            antagonist="The trolls of the peninsula",
            moves=TRACK,
            place=scartaris,
            summary="Trolls fill the Snaefellsnes peninsula, and to them a "
            "new household is prey.",
            secrets="They come slowly into the saga, and only grow bolder if "
            "no reprisal follows (p. 89). Their statistics are on p. 30.",
            stages=[
                b.stage(
                    "Stolen sheep",
                    at=1,
                    clues="Sheep and the like go missing around the farms.",
                    ignored="With no reprisal the trolls grow bolder.",
                ),
                b.stage(
                    "Bolder attacks",
                    at=2,
                    clues="The thefts turn into attacks on the covenant's interests.",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "The Hidden Revels",
            antagonist="Ammon, Master of the Hidden Revels",
            moves=TRACK,
            place=old,
            realm="Infernal",
            summary="The dead of a Roman fort in Northumberland are said to "
            "beg for mercy every night.",
            secrets="The magi are best served by going before Brighde's "
            "Gauntlet, whose timing the storyguide may shift to suit (pp. "
            "92-93).",
            stages=[
                b.stage(
                    "The first visit",
                    at=1,
                    clues="Ammon and his minions; ideally the magi are forced "
                    "to retreat.",
                    ignored="Ammon lets them go, with insults to bring them "
                    "back (p. 94).",
                ),
                b.stage(
                    "Preparation",
                    at=2,
                    clues="The magi research spells or invest items for the "
                    "return (p. 93).",
                ),
                b.stage(
                    "The return",
                    at=3,
                    clues="Spells must penetrate Might 40 to reach the top "
                    "level, and the gatestones are under tons of rubble (pp. "
                    "93-94).",
                    stopped="With the infernal creatures gone, Christian "
                    "burial for all the victims can destroy the regio, and a "
                    "magical regio (+2, +4) forms within a decade (p. 94).",
                ),
            ],
        )
    )
    dormant(
        b.threat(
            "Burnham's Bargain",
            antagonist="The covenant of Burnham",
            moves=TRACK,
            place=old,
            summary="Burnham has a vis right in Northumberland it would like "
            "to exchange with a young covenant.",
            secrets="Burnham holds the harvesting rights to Old Vindolanda and "
            "will maneuver the next naive young covenant into taking them "
            "(p. 93).",
        )
    )
