"""The places of legend (ch12, and ch02's seeds): stone circles, barrows,
hill figures and haunted ground, most with a tale and no number. Auras
the book doesn't give are a judgement call (S10): an unnumbered magic
site Magic 3, a faerie one Faerie 3, marked inferred; places of no clear
realm have none. Stonehenge, which the book calls one of the most
magical places in Europe, takes the convention's 3 (S10)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..builder import paragraphs
from ..records import KNOWN_TRIBUNAL

if TYPE_CHECKING:
    from ..records import Records

INFERRED = "The book gives no aura; {} is inferred."

#: (key, name, region, realm, aura, summary)
PLACES: tuple[tuple[str, str, str, str, int, str], ...] = (
    (
        "stonehenge",
        "Stonehenge",
        "england",
        "Magic",
        3,
        paragraphs(
            "The Giant's Ring, which Merlin brought from Ireland, his art making "
            "the stones light as feathers for Uther's knights, and set up again on "
            "the plain where Hengest's Saxons murdered the Britons; its stones' "
            "virtue heals the wounded who bathe in the water that washed them. One "
            "of the most magical places in Europe. A ditch and bank with an "
            "entrance in the north-east, an avenue leading down to the valley, "
            "and within, symmetrical about the avenue's line, an outer circle of "
            "thirty shaped uprights joined by lintels, a circle of sixty "
            "bluestones, a horseshoe of five trilithons, the greatest over twenty "
            "feet, a horseshoe of bluestones and a last upright at the centre. "
            "From the entrance the midwinter sun sets between the great "
            "trilithon's uprights.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "avebury",
        "Avebury",
        "england",
        "Magic",
        3,
        paragraphs(
            "A great stone circle about a thousand feet across, inside a ditch "
            "thirty feet deep and a bank fifty feet high, with nearly three "
            "hundred boulders, and the village and church of Avebury inside it. "
            "Two winding avenues of stones lead away, one to a smaller double "
            "circle. South is Silbury Hill, the tomb of King Sel on horseback with "
            "his treasure, cursed to kill robbers, and beyond it a long barrow with "
            "a stone doorway, home of faeries or demons. The tales say that "
            "walking the avenue, the circles or the barrow on the right days takes "
            "one somewhere not wholly of this world.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "glastonbury_tor",
        "Glastonbury Tor",
        "england",
        "Faerie",
        3,
        paragraphs(
            "The hill above Glastonbury Abbey on the Isle of Avalon, where Saint "
            "Collen went into Gwynn ab Nudd's faerie castle.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "tintagel",
        "Tintagel",
        "england",
        "Faerie",
        3,
        paragraphs(
            "Very nearly an island off north Cornwall, its neck held by a ditch and "
            "mound three men could defend: Gorlois's stronghold, where Uther, "
            "disguised by Merlin, fathered Arthur, and later King Mark's seat. Only "
            "the mound and ditch remain, and the little chapel of Saint Juliot; "
            "the castle may be somewhat detached from the mundane world, and the "
            "chapel may be there to keep it from coming back.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "lyonesse",
        "Lyonesse",
        "england",
        "Faerie",
        3,
        paragraphs(
            "The drowned land between Land's End and the Isles of Scilly, Tristan's "
            "birthplace, once of a hundred and forty parishes and the town of Lyon "
            "at Lethoso; at the lowest tides its forests and towns show, and "
            "fishermen draw up pieces of windows. Only the first Trevelyan escaped "
            "east, riding his white horse ahead of the flood to Saint Michael's "
            "Mount. The anger of the Fair Folk is thought the cause, though no one "
            "has spoken of why for three centuries.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "merlins_well",
        "Merlin's Well",
        "england",
        "Magic",
        3,
        paragraphs(
            "On Alderley Edge in Cheshire, water runs from the cliff into a stone "
            "trough under a carved inscription in a slightly old form of the local "
            "tongue, never recut, and a face said to be Merlin's. Locals say Arthur "
            "and his knights sleep under the Edge, and the spring will water their "
            "horses when they wake.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "bryn_celli_ddu",
        "Bryn-Celli-Ddu",
        "wales",
        "Magic",
        3,
        paragraphs(
            "A mound on Anglesey whose narrow passage leads to a chamber with a "
            "smooth stone pillar; on top, by a pit, a stone carved on three sides "
            "with a labyrinth, part of some ward. Llewellyn, the last Primus of "
            "House Diedne, was last seen here, and his parting curse is carved "
            "into the passage wall, sheltered from the weather. Magi avoid the "
            "site.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "uffington",
        "The White Horse of Uffington",
        "england",
        "Magic",
        3,
        paragraphs(
            "A horse cut into the chalk below an old hillfort, overlooking Dragon "
            "Hill, whose flat top grows nothing. At certain times, or rightly "
            "called, the horse rises and goes about the country, or perhaps "
            "Arcadia, a white horse of surpassing beauty that no mortal can master "
            "but that might carry someone for gifts or respect.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "waylands_smithy",
        "Wayland's Smithy",
        "england",
        "Faerie",
        3,
        paragraphs(
            "A mile from the White Horse, home of an invisible smith: leave a horse "
            "and a penny on a certain stone, and by morning it is shod and the penny "
            "gone. Wayland is said to be able to shoe the White Horse itself, making "
            "it calm, and to have forged arms for heroes of old, for more than a "
            "penny.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "grimes_graves",
        "Grime's Graves",
        "england",
        "Faerie",
        3,
        paragraphs(
            "A dozen great pits on a chalk hill in Norfolk, each thirty feet across "
            "and deep, with small tunnels running from their bottoms; stone blades "
            "lie near their tops. Those who go near at night tend to vanish, strange "
            "lights are seen, and most locals think faerie folk live there; no one "
            "dares look by night.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "long_meg",
        "Long Meg and Her Daughters",
        "england",
        "Magic",
        3,
        paragraphs(
            "A circle of about seventy squat stones in the Lake District, with "
            "Long Meg, a carved sandstone pillar twice a man's height, outside its "
            "entrance. The stones cannot be counted, any answer from 65 to 75 "
            "coming up; harming them turns nature against the vandal, and chipped, "
            "Long Meg bleeds. They are thought a witch and her daughters turned to "
            "stone, by choice or curse, the tales do not say.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "rollright",
        "The Rollright Stones",
        "england",
        "Magic",
        3,
        paragraphs(
            "A circle of twenty-five stones on an Oxfordshire ridge, and the King "
            "Stone outside it, the most magical of them: chips of it ward off "
            "demons. They are a petrified army and its king, who go down to drink "
            "at a spring every New Year's Day, watched by the witch who cursed "
            "them, now an elder tree.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "belas_knap",
        "Belas Knap",
        "england",
        "Faerie",
        3,
        paragraphs(
            "A barrow 180 feet long with a blocked doorway in its north face that "
            "is said to open on certain nights into a faerie palace or some magical "
            "creature's home. No one returns, though the tales describe the inside "
            "in detail.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "men_an_tol",
        "Men-an-Tol",
        "england",
        "Magic",
        3,
        paragraphs(
            "A holed stone in a Cornish field with two pillars behind it. The sick "
            "are passed through the hole, three times for a child, nine for an "
            "adult, to be healed; a gift laid on top moves to answer a question.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "roughting_linn",
        "Roughting Linn",
        "england",
        "",
        0,
        "A rock face in Northumberland carved with more than sixty cups and rings: maps, or faerie memorials. Some magi think Gerfallon of Semitae carved them; he won't say.",
    ),
    (
        "carles",
        "Carles",
        "england",
        "Faerie",
        3,
        paragraphs(
            "A circle of forty-two stones inside a bank, three barrows within; in "
            "the east a rectangle of stones, the Porter's Lodge, where on certain "
            "nights a house stands and its porter guards the way to other places.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "black_horse_of_busha",
        "The Black Horse of Busha",
        "england",
        "Magic",
        3,
        paragraphs(
            "An outcrop of black shale high in the Howgill Fells; after storms, "
            "those who know where to look see a proud black stallion, returning, "
            "locals say, from travelling the world under the storm's cover, about "
            "purposes they won't name and don't trust.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "druids_circle",
        "The Druids' Circle",
        "wales",
        "Magic",
        3,
        paragraphs(
            "Stones on a raised bank on a moor over the Irish Sea, seen for miles. "
            "They move nearer to anyone who swears an oath inside, as if to listen, "
            "and the tales warn against breaking such oaths; darker ones tell of "
            "druids' human sacrifices.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "long_man",
        "The Long Man of Wilmington",
        "england",
        "",
        0,
        "A figure 240 feet tall cut into a Sussex hillside, invisible from many angles, holding two staves like a door's posts. One tale makes him Saint Paul, gaining a face as the land grows pious and fading with its wickedness; another the keeper of the gates of dawn, who will open them to the right petition.",
    ),
    (
        "wookey_hole",
        "Wookey Hole",
        "england",
        "",
        0,
        "A deep, half-flooded cave hung with stalactites, with more caves thought to lie beyond the water; something lives in it, though the tales disagree what.",
    ),
    (
        "cerne_giant",
        "The Cerne Giant",
        "england",
        "Magic",
        3,
        paragraphs(
            "A blatantly phallic giant cut into a Dorset hillside near an abbey "
            "whose monks have never defaced it. Barren women who sleep on it can "
            "conceive. He is said to be a giant who terrorised the land, pinned "
            "down asleep and slain, leaving only his outline.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "maiden_castle",
        "Maiden Castle",
        "england",
        "Faerie",
        3,
        paragraphs(
            "Great earthworks round a hill south of Dorchester, entered by twisting "
            "passages; deserted, but a faerie stronghold where those who come on "
            "the right night may meet the fay.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "down_tor",
        "Down Tor",
        "england",
        "Magic",
        3,
        paragraphs(
            "A stone circle round a barrow on Dartmoor, with a row of nearly two "
            "hundred stones running east. The circle binds a powerful ghost, which "
            "the right rites can call along the row, weakened enough to do the "
            "summoner no harm.",
            INFERRED.format("Magic 3"),
        ),
    ),
    (
        "trethevy_quoit",
        "Trethevy Quoit",
        "england",
        "Faerie",
        3,
        paragraphs(
            "Standing stones fifteen feet high under a holed capstone, one with a "
            "doorway cut in its corner: the home of a powerful faerie who does not "
            "like to be disturbed.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "merry_maidens",
        "The Merry Maidens",
        "england",
        "",
        0,
        "Nineteen levelled boulders at Land's End, with the two great Pipers to the north-east: girls who danced on a Sunday to demons' piping, turned to stone by God's wrath, and the demons with them as they fled.",
    ),
    (
        "offas_dyke",
        "Offa's Dyke",
        "wales",
        "Faerie",
        3,
        paragraphs(
            "The great dyke on the Welsh border, built with the help of Huarwar, a "
            "Welsh faerie bribed with ten thousand cattle and a hundred more every "
            "fourteen years; neglected, he eats the dyke and the villages by it.",
            INFERRED.format("Faerie 3"),
        ),
    ),
    (
        "minerva_shrine",
        "The Shrine of Minerva",
        "england",
        "Magic",
        3,
        paragraphs(
            "A shrine of Minerva carved in the rock south of the river at Chester, "
            "left unharmed: a pagan site.",
            INFERRED.format("Magic 3"),
        ),
    ),
)


def build(records: Records) -> None:
    b, p = records.b, records.places
    for key, name, region, realm, aura, summary in PLACES:
        kw: dict[str, Any] = dict(KNOWN_TRIBUNAL)
        p[key] = b.place(
            name,
            inside=p.get(region),
            realm=realm or "Magic",
            aura=aura,
            summary=summary,
            **kw,
        )
