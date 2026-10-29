"""The six covenants Sanctuary of Ice describes (ch03-ch08), rebuilt
rather than converted (A8): each keeps the book's site, season, founding,
aura, members, library, vis and allies, drops the Fourth Edition point
totals, and takes Boons and Hooks from the Covenants catalog as lines in
what_matters. Vis supplies printed only as points are 30 pawns and 5 a
point (Fourth Edition core p. 206): Journeys End's +15 is 105 pawns and
Valnastium's +19 is 125, its printed 570 kept as a note; the Cave keeps
its printed 160.

Keys: covenants["cave"] (the Cave of Twisting Shadows, on
places["axis_magica"]), ["icy_north"] (the Covenant of the Icy North, its
motherhouse on places["icy_north_hill"]), ["journeys_end"] (on
places["mont_joux"], its regio level 1), ["sinews"] (Sinews of
Knowledge), ["tarragon_vale"] (a sketch, its magi vanished) and
["valnastium"]. The seventh public covenant the book leaves blank, and
the roster's count covers it (A14).

The chapters (A9) are places linked to their covenants:
places["rorschach"], ["junos_spire"] and ["tower_of_ashes"] (Icy North),
["vienna_chapter"], ["constance_chapter"], ["saint_gallen_chapter"] and
["geneva_chapter"] (Valnastium). Their magi are members of the covenant,
with their chapter in their summary.

Magi are sketches here; stats_magi.py converts the printed blocks of
magi["kentigern"], ["miklos"], ["ragoneda"] and ["andru"], and of the
Redcap companion magi["cymena"], and generates everyone else's. The Larta
of Valnastium (Josephine, François, Chloe) are companions, covenfolk and
not members of House Jerbiton (the errata pp. 44-45), and Carmine's
children are a note on her (Houses of Hermes: Societates p. 52)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ... import storage
from ...models import Possession
from ...models.world import FULL
from ..builder import joined_lines, paragraphs

if TYPE_CHECKING:
    from ...models import Character, Covenant, Tribunal
    from .state import Alps

CRIAMON = "house_criamon"
GUERNICUS = "house_guernicus"
TYTALUS = "house_tytalus"
EX_MISC = "house_ex_miscellanea"
BJORNAER = "house_bjornaer"
MERCERE = "house_mercere"
FLAMBEAU = "house_flambeau"
MERINITA = "house_merinita"
JERBITON = "house_jerbiton"
BONISAGUS = "house_bonisagus"
VERDITIUS = "house_verditius"


def build(alps: Alps) -> None:
    tribunal = alps.tribunal
    if tribunal is None:
        return
    _cave(alps, tribunal)
    _icy_north(alps, tribunal)
    _journeys_end(alps, tribunal)
    _sinews(alps, tribunal)
    _tarragon_vale(alps, tribunal)
    _valnastium(alps, tribunal)


def _vis_source(covenant: Covenant, name: str, art: str, pawns: int, note: str) -> None:
    covenant.possessions.append(
        Possession(
            id=storage.generate_unique_id(name, [p.id for p in covenant.possessions]),
            kind="vis_source",
            name=name,
            art=art,
            pawns=pawns,
            description=note,
        )
    )


def _magus(
    alps: Alps,
    key: str,
    name: str,
    covenant: Covenant | None,
    house: str,
    age: int | None,
    summary: str,
    *,
    kind: str = "magus",
    secrets: str = "",
) -> Character:
    character = alps.b.magus(
        name,
        covenant=covenant,
        house=house,
        age=age,
        summary=summary,
        type=kind,
        secrets=secrets,
    )
    alps.magi[key] = character
    return character


def _chapter(
    alps: Alps, key: str, name: str, covenant: Covenant, region: str, summary: str
) -> None:
    place = alps.b.place(
        name,
        inside=alps.places.get(region),
        aura=0,
        summary=summary,
        known="In the Tribunal",
    )
    alps.places[key] = place
    alps.b.link(covenant, "places", place, "A chapter of the covenant")


# ----------------------------------------------- the Cave of Twisting Shadows


def _cave(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    summary = paragraphs(
        "The domus magna of House Criamon, a covenant older than the "
        "Christian era, carved into a mountain and repeated on nine "
        "levels of regio about the Axis Magica. Its device is an eye with "
        "the sign of infinity for its pupil. Many Criamon return here as "
        "their lives end; the young are sent away to bring fresh insight "
        "back when they return for new riddles.",
        "Its people are mostly dead. Hundreds of ghosts of covenfolk and "
        "magi live on in families led by their living members, the "
        "weakest no more than patches of darkness, which give the covenant "
        "its name; the ghosts of the past Primi teach in place of a "
        "library, and are stingy with it. The autocrat is Hera, a ghost "
        "Criamon himself bound to the place. The living covenfolk never "
        "see daylight, grow distorted with age and often die young; they "
        "eat the nutty fungi of the mushroom farms Muscaria laid out, and "
        "speak a Romansch found nowhere else.",
        "Customs. Visitors are welcome to learn the Enigma, vouched for by "
        "another covenant so as not to breach the Code, but none goes "
        "above the first level unless asked to a ritual; their tutors mark "
        "each insight with a tattoo. The council rules by consensus, the "
        "wisest weighing most, and seekers are sometimes asked to sit in "
        "it. When a Primus nears Twilight, a magus of another House "
        "ritually kills her before the ghosts of the past Primi, and the "
        "magi enter a communal vision until one rises as the new Primus "
        "(on the ninth level, and with Enigmatic Wisdom 3 or more, as "
        "Houses of Hermes: Mystery Cults has it).",
        "Magi. Sanctuary of Ice names fifteen; Houses of Hermes: Mystery "
        "Cults gives the Central Clutch twelve living magi, so the twelve "
        "it can hold are resident here (A10): the Prima Muscaria, Circum "
        "Perfico, Darius, Echo, Gunther, Hagen, Latrunculus, Pellam, "
        "Phalene, Regina, Siobhan and Viscus. Fortuito travels; Esther is "
        "petrified and arguably a member. La, Prima and Praeco in "
        "Sanctuary of Ice, has since been ritually slain and is one of the "
        "spectral Primi. The covenant counts twenty-two members in theory; "
        "eight live in the mundane land about it and belong only in law.",
    )
    what_matters = joined_lines(
        "Vis stores: 100 pawns",
        "Vis: 160 pawns a year, much of it from creatures that must be hunted down and killed (the book's own figure, kept: A12 as amended)",
        "Library: the ghosts serve as its library, about 2100 levels of spells if they will teach; Hermetic books worth 450 points, kept mostly for trade (its magi study from vis or in the Magic realm); mundane books worth 60 points, mostly tractatus on Enigmatic Wisdom",
        "Covenfolk: room for 18 magi and 40 specialists; most inhabitants are technically dead",
        "Enchantments: none; magic items kept in the upper levels bleed into the Axis",
        "Laboratories: none better than +1, and none on the ninth level",
        "Allies: every Criamon magus, if the Cave were threatened with destruction",
        "Enemies: malign spirits from the Magic realm; the Cult of Dyssynergy, which may not exist",
        "Boon: Regio (Major) (nine levels about the Axis Magica)",
        "Boon: Vast and Labyrinthine (looping tunnels repeated on every level)",
        "Boon: Inhuman Residents (the ghosts of covenfolk and magi)",
        "Boon: Seclusion (all but unreachable from the mundane world)",
        "Hook: House Covenant (House Criamon)",
        "Hook: Seat of Power (the domus magna and its Primi)",
        "Hook: Distorted Covenfolk (they never see daylight)",
        "Hook: Haunted (the ghosts, and Hera)",
    )
    covenant = b.covenant(
        "The Cave of Twisting Shadows",
        tribunal=tribunal,
        founded=None,
        place=alps.places["axis_magica"],
        level=1,
        aura=5,
        summary=summary,
        what_matters=what_matters,
        detail=FULL,
        season="Winter",
        unnamed_magi=8,
        secrets=paragraphs(
            "La, when still the apprentice Lucia, fell in with the Black "
            "Mark, a Criamon splinter that holds the Dominion will destroy "
            "all magic unless stopped and doubts that it comes from an "
            "almighty God; she murdered a priest on his own altar and has "
            "been cursed by God since.",
            "Echo is in love with a Criamon three centuries dead, an affair "
            "that is also an illicit Twilight; the ghostly Esther is a juno "
            "born of it. The Primi delay Esther's unpetrifying to watch it.",
        ),
    )
    alps.covenants["cave"] = covenant
    for key, name, age, summary in CAVE_MAGI:
        _magus(alps, key, name, covenant, CRIAMON, age, summary)


CAVE_MAGI: tuple[tuple[str, str, int | None, str], ...] = (
    (
        "muscaria",
        "Muscaria",
        41,
        "Prima of House Criamon, filia Demetrius, forty-one and looking an "
        "energetic adolescent who knows far too much: her master, an "
        "alchemist, gave her a longevity potion at fourteen, and she has "
        "kept her body from growing up in his honour. Named for the "
        "mushroom the first local magicians used, she finds such "
        "compounds dull, doubts her own insights, and chose to support "
        "others instead, building the mushroom farms that feed the "
        "living. She did not expect the Primacy: it is the wish to give up "
        "wisdom to serve others, not wisdom, that marks a Primus. She "
        "leads the council of magi and elected covenfolk, and dislikes "
        "obfuscation (DE p. 21; Houses of Hermes: Mystery Cults pp. 44, "
        "56).",
    ),
    (
        "circum_perfico",
        "Circum Perfico",
        None,
        "Filia Johannes, an elderly maga who believes a Hermes Portal "
        "between the Cave and the North Pole would line up the Earth's "
        "axis with its magical and magnetic fields, making the Earth "
        "more like the stars, so that the answer to the Enigma could exist "
        "in it without being sullied.",
    ),
    (
        "darius",
        "Darius",
        None,
        "Filius Yannes, a Muto Mentem specialist with strong Intellego and "
        "Herbam who brews mind-altering substances, alcohol above all. "
        "Popular with grogs across Europe and drunk much of the time, he "
        "studies drunken mobs, spikes the wells of remote villages, and "
        "is to host the nine-yearly meeting of magical brewers in 1226. "
        "The Quaesitores blame him for much of the petty trouble at the "
        "Midsummer Fair. He holds that the Enigma's answer will take the "
        "mundanes into the Twilight lineage, and that ecstasy is the one "
        "philosophy they will accept.",
    ),
    (
        "echo",
        "Echo",
        65,
        "Filia Gribbinus, a pleasant, bland maga in her sixties, a Mentem "
        "specialist with an affinity for ghosts, who is gaining little "
        "wisdom for an illicit affair. If it came out, her covenmates "
        "would send her from the Central Clutch for her own good. She and "
        "Esther, trained by the same master, argue often.",
    ),
    (
        "esther",
        "Esther",
        None,
        "Filia Gribbinus, once an Imaginem specialist, turned to stone by "
        "faeries a couple of years ago. Her ghost floated free when the "
        "statue came home, but the curse can be undone, so she may not be "
        "dead; she is unsure whether she is a projected image, a ghost, "
        "or a spirit that thinks it is Esther, and fears she is someone "
        "else's figment. Arguably a member of the covenant: no one is "
        "sure.",
    ),
    (
        "fortuito",
        "Fortuito",
        None,
        "Filius Circum Perfico, who travels Europe studying diviners and "
        "seers to learn where their knowledge comes from. He sends letters "
        "dated before a disaster, to be delivered only after it, asking "
        "how its survivors lived, since a warning would spoil his "
        "observations, and many magi never forgive him. A Seeker of "
        "sorts, he is browbeaten by others for what he withholds.",
    ),
    (
        "gunther",
        "Gunther",
        None,
        "Filius Frederico, the covenant's chief baker, who no longer studies "
        "magic and acts as little like a magus as he can, seeking wisdom "
        "in the small perfect moments of mundane life.",
    ),
    (
        "hagen",
        "Hagen",
        None,
        "Filius Flauberto the Difficult, who makes atonal music with "
        "summoned spirits, believing a hidden composition resonates under "
        "the world's events. Many of his line were driven mad by Plato's "
        "Comma, the flaw in the seven notes that answer the seven planets.",
    ),
    (
        "latrunculus",
        "Latrunculus",
        None,
        "Filius Aurelia, a skilled Terram magus and surveyor who believes "
        "the Roman roads overlie magical paths, with the Great Ones buried "
        "at the great crossings under the cities; reckon finely enough and "
        "one could dig up an ancient. Seekers consult him, and he may go "
        "to Egypt to help catalogue a cat cemetery, with younger, more "
        "violent magi.",
    ),
    (
        "pellam",
        "Pellam",
        None,
        "Filius Cato, a young magus who believes ball games are the folk "
        "remnants of pagan rites that might lead toward the Enigma or the "
        "Seekers' sacred places; Darius's ally.",
    ),
    (
        "phalene",
        "Phalene",
        None,
        "Filia Innocu, who sees Twilight as a metamorphosis like a moth's "
        "and studies creatures that transform. Her philosophy has people "
        "outgrowing the Enigma, the House's politics wrong and the Primi's "
        "sacrifice pointless, so she does not debate it.",
    ),
    (
        "regina",
        "Regina",
        None,
        "Filia Gribbinus, first trained in House Bonisagus by Dexter, whose "
        "long study of the Enigma has drawn her into Criamon. She makes "
        "mystical spaces in which things impossible in the mundane world "
        "become possible.",
    ),
    (
        "siobhan",
        "Siobhan",
        None,
        "Filia Vespasian the Avaricious, from Hibernia, with plain links to "
        "Bright Summer: the House's specialist in faeries, a Vim maga with "
        "weaker Arts than most of her House, who retrained under a "
        "Merinita to learn Faerie Magic. She holds Twilight and deep "
        "Arcadia to be the same place. Her three apprentices share her "
        "air of knowing more than one could understand.",
    ),
    (
        "viscus",
        "Viscus",
        None,
        "Filius Circum Perfico, a haruspex who seeks the Enigma in the "
        "entrails of magical beasts, and of familiars most of all; he once "
        "looked at the liver of a young Jerbiton killed in a lab accident. "
        "Magi send him the remains of beasts whose vis they have cut out, "
        "which makes him the Redcaps' least favourite magus, and his "
        "bottled oddities sell at the Fair.",
    ),
)


# ------------------------------------------------- the Covenant of the Icy North


def _icy_north(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    summary = paragraphs(
        "One of the Order's first covenants of magi trained by different "
        "masters, founded in 771 by Italians, as its name shows, and now a "
        "loose league of autonomous chapters that is a covenant mostly in "
        "law. Half a century after its founding the motherhouse and its "
        "three greatest chapters each claimed to be the true covenant; "
        "they settled before the Tribunal could break them up, and the "
        "chapters meet in council each year at the Midsummer Fair. It has "
        "nine chapters now, five of them a single magus each. Its device "
        "is a web or snowflake of three hexagons.",
        "The motherhouse in Bavaria stands where Highest Aspiration fell in "
        "the Sundering of Tremere. The Quaesitores were set to harvest "
        "that covenant's vis, the Bavarian Common, and divide it each "
        "year; the trade that grew round the distribution raised the "
        "Common's chapter until the old motherhouse became a chapter and "
        "the magi moved here. It is all but a house covenant of "
        "Guernicus, home to four quaesitores and two hoplites, built far "
        "larger than its people need so that the Tribunal can meet in it, "
        "and many rooms stand empty but in summer. In an emergency a "
        "March gathers here.",
        "A chair is offered for the best use of its empty buildings. Two "
        "dozen Gifted children were born at once in Sicily five years ago, "
        "and the likeliest proposal is a school for them by collegial "
        "training, which the Quaesitores favour lest so many of one age "
        "and affinity unbalance a single House. Mircalla, a mother "
        "murdered here by a magus's grogs when she came for her stolen "
        "daughter, haunts it, immune to Hermetic magic, kind to ill-used "
        "apprentices and ruinous to dangerous experiments, so no magus "
        "here keeps an apprentice.",
        "Magi of the motherhouse: Athena Alpina, Cato, Adrasteia and "
        "Kentigern, the quaesitores; Archmage Vincent of Criamon and "
        "Katrina of Bjornaer, the hoplites. Thirteen more live in the "
        "chapters, of whom the book names Mary and Rogitien of Rorschach, "
        "Archmage Pietro of Juno's Spire and Archmaga Jacinta of the Tower "
        "of Ashes; the rest are unnamed.",
    )
    what_matters = joined_lines(
        "Vis stores: 100 pawns",
        "Vis: 60 pawns a year, with the Domleschg oak grove's Rego vis among its sources and the Bavarian Common divided at the Fair",
        "Income: 700 pounds of silver a year",
        "Library: 2100 levels of spells, favouring investigation and violence; Hermetic books worth 900 points, strongest in Intellego and Ignem; mundane books worth 240 points, favouring Hermetic history and law",
        "Covenfolk: 6 magi, 20 specialists and 50 grogs at the motherhouse",
        "Enchantments: Hermes Portals to several chapters and to Magvillus",
        "Laboratories: four, each +3",
        "Allies: Magvillus",
        "Enemies: the local count; a local faerie prince; the restless spirit Mircalla; magi of the Rhine and Transylvania who poach from the Bavarian Common; rivals in its business",
        "Boon: Mystical Portal (Hermes Portals to the chapters and Magvillus)",
        "Boon: Powerful Ally (Magvillus and House Guernicus)",
        "Boon: Prestige (Minor) (the site of the Midsummer Fair and the Tribunal)",
        "Hook: Chapter House (Major) (nine chapters across the Alps)",
        "Hook: House Covenant (all but a Guernicus house)",
        "Hook: Hermetic Services (Major) (the Fair, the Tribunal and the Bavarian Common)",
        "Hook: Haunted (Mircalla)",
        "Hook: Contested Resource (the Bavarian Common)",
    )
    covenant = b.covenant(
        "The Covenant of the Icy North",
        tribunal=tribunal,
        founded=771,
        place=alps.places["icy_north_hill"],
        aura=6,
        summary=summary,
        what_matters=what_matters,
        detail=FULL,
        season="Autumn",
        unnamed_magi=9,
    )
    alps.covenants["icy_north"] = covenant
    _vis_source(
        covenant,
        "The Domleschg oaks",
        "Rego",
        0,
        "A grove of oaks over the old druids' battlefield, each grown from "
        "an acorn in a dead man's mouth; the book gives no yield.",
    )
    _chapter(
        alps,
        "rorschach",
        "The Rorschach Chapter",
        covenant,
        "western_alps",
        "A tiny chapter house just outside Rorschach, a trading village on "
        "Lake Constance near the abbots of Saint Gallen's palace, home of "
        "two Mercere magi. The trade through the town covers the House's "
        "work in the Tribunal; a Hermes Portal joins it to the motherhouse "
        "and so to other chapters, and it offers a fifth of the vis for any "
        "new portal it may use. Salt, inks and vellum come cheaply through "
        "it. It holds a large property in Vienna in the name of House "
        "Mercere's trading house.",
    )
    _chapter(
        alps,
        "junos_spire",
        "Juno's Spire",
        covenant,
        "western_alps",
        "Archmage Pietro's own chapter. Its Hermes Portal to the "
        "motherhouse, a relic of the days of strife within the covenant, "
        "sits in a room that can be barred with a thick metal plate and "
        "enchanted to burn all human flesh in it on command; that it is "
        "widely known feeds the rumour that Pietro is the Antares.",
    )
    _chapter(
        alps,
        "tower_of_ashes",
        "The Tower of Ashes",
        covenant,
        "western_alps",
        "The home of Archmaga Jacinta of Flambeau.",
    )
    for key, name, house, age, summary in ICY_NORTH_MAGI:
        _magus(alps, key, name, covenant, house, age, summary)


ICY_NORTH_MAGI: tuple[tuple[str, str, str, int | None, str], ...] = (
    (
        "athena",
        "Athena Alpina",
        GUERNICUS,
        112,
        "The chief Quaesitor of the Alps for fourteen years, appointed by "
        "the Primus of Guernicus; called Alpina to tell her from the many "
        "Athenas of her House. An Intellego specialist most interested in "
        "Hermetic contracts of trade and sale, she runs the Fair and "
        "arranges the exchange of listed sites between covenants. "
        "Respected for her post and disliked as a person, since she lacks "
        "her neighbours' biases: trained in the Roman Tribunal, she does "
        "not dislike the Tremere and wants them to play a larger part. "
        "She is a hundred and twelve and looks in her late sixties, of "
        "Slavic blood, dark-haired, tall and solid, and travels in the "
        "stola with its veil, lifting it to speak in public.",
    ),
    (
        "cato",
        "Cato",
        GUERNICUS,
        None,
        "The second most senior quaesitor in the Tribunal and Athena's "
        "deputy, who spies in disguise as a crumpled drunk old man (or a "
        "busty serving maid), letting magi take him for a magical "
        "incompetent until his subtle illusions catch them.",
    ),
    (
        "adrasteia",
        "Adrasteia",
        TYTALUS,
        None,
        "A quaesitor of House Tytalus, chosen for stealth and defensive "
        "violence, who roams the borders hunting raiders who plunder the "
        "vis sites the Code calls Alpine. Allowed to strike only those "
        "caught in the act, she lays elaborate traps and ruses, always with "
        "two hoplites at her back. Elsewhere her methods would not pass; "
        "here the powerful covenants wish for more like her, and the "
        "Primus of Guernicus, who sees she may become a problem, keeps "
        "her because she deters vigilantes and counter-raids, which she "
        "treats as fair game too.",
    ),
    (
        "kentigern",
        "Kentigern",
        EX_MISC,
        99,
        "A quaesitor of a Hibernian beast-mage tradition with a magical "
        "affinity for dogs, whose faerie hounds prowl the Midsummer Fair "
        "growling at anyone who smells suspicious. A skilled tracker, he "
        "hunts magical beasts through blizzards and air elementals through "
        "the sky, and calls on the nearest covenant for a quarry too strong "
        "for him. Once a monastic novice, he keeps an interest in the "
        "Church and canon law, vets the contracts between mundanes and the "
        "covenants' shell houses, and is the quaesitor likeliest to "
        "witness an oath. He came three years ago from retraining at "
        "Magvillus: a respectable quaesitor and a poor hedge wizard both, "
        "and so an unknown quantity.",
    ),
    (
        "vincent",
        "Vincent",
        CRIAMON,
        None,
        "An archmage of Criamon and a hoplite, who seeks the Enigma through "
        "the violent application of magic to the body: his spells, he "
        "holds, purify his enemies and teach them not to break the Code. "
        "Arms and reason share a Greek root, and he means to make the "
        "world's pieces fit by shoving them. One of the finest exponents of "
        "certamen in the Tribunal, with some success against demons; his "
        "deadliest spell is a high-level form of the Gift of the Enigma. He "
        "will not be called back to the Central Clutch soon.",
    ),
    (
        "katrina",
        "Katrina",
        BJORNAER,
        None,
        "One of the Order's youngest hoplites, whose heartbeast is the "
        "wolverine, the glutton: all but tireless, very strong and immune "
        "to cold. She serves the Quaesitores, travels with Adrasteia, and "
        "is preparing to challenge for archmage, exploring magical sites "
        "for creatures whose vis she can trade for items useful in either "
        "form.",
    ),
    (
        "mary",
        "Mary",
        MERCERE,
        None,
        "The senior maga of the Rorschach Chapter, a Gifted Mercere who "
        "makes lesser enchanted devices for Redcaps of other Tribunals: "
        "illusions for disguise, invisibility and swift travel.",
    ),
    (
        "rogitien",
        "Rogitien",
        MERCERE,
        None,
        "Of the Rorschach Chapter: an alchemist with the Gentle Gift who "
        "brews the longevity potions of the Tribunal's Redcaps and, by "
        "arrangement with House Guernicus, its long-serving hoplites. He "
        "prefers travel to the laboratory and goes often between the "
        "covenants. His large mundane family has many Redcaps in it.",
    ),
    (
        "pietro",
        "Pietro",
        FLAMBEAU,
        None,
        "Archmage of Juno's Spire, the Tribunal's senior hoplite and its "
        "lictor: a spry, small, elderly man fascinated by structured "
        "conflict. Trained in House Tytalus, he won his way into Flambeau "
        "by beating its champions with lightning, because it was hard and "
        "because some Tytalus think it their duty to found lineages in "
        "other Houses; some Flambeau call his descendants, the Jovians, "
        "interlopers. Hunting a leopard for his hoplite's sash, he was "
        "stalked and ambushed by it, and courted it as his familiar: "
        "Cinnamon, who catches birds from behind clouds. Rumour makes him "
        "the Antares, the Council of Archmagi's ceremonial war leader, who "
        "wears a great ruby.",
    ),
    (
        "jacinta",
        "Jacinta",
        FLAMBEAU,
        None,
        "Archmaga of the Tower of Ashes, filia Nicoli of the line of "
        "Apromor: the eldest of her line and so the most able Perdo maga "
        'in the Order, who studies "suboptimal" spells that make Perdo do '
        "other Techniques' work (one ages blood into a scab to bind wounds, "
        "another destroys disease spirits; Carve the Mystic Tower etches "
        "a building out of rock). Many Alpine magi hope she dies before "
        "the few Flambeau older or deadlier than she, for as Prima she "
        "would make the Icy North her House's domus magna. She leads the "
        "Rowan Sisterhood. She and Pietro were born in the same Portuguese "
        "village, declared Wizard's War on each other on the same day "
        "twenty-eight years ago, and have been allies, rivals, enemies "
        "and perhaps lovers since; neither has fought a witnessed "
        "certamen. Her apprentice Ash is now the maga Noire.",
    ),
)


# ----------------------------------------------- the Covenant Where Journeys End


def _journeys_end(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    summary = paragraphs(
        "A covenant of Houses Merinita and Bjornaer in a regio on Mont "
        "Joux, founded in 817. Lucia filia Merinita came seeking the "
        "temple of Jupiter, found it sacked, and turned on the faeries "
        "instead, discovering a vast regio tied to Bright Winter and ruled "
        "by the White Lady, a queen of illusion. She killed the queen, "
        "took her kingdom and hunted her servants for the vis in them, "
        "sparing a few souled half-breeds to tend the vis sources; a "
        "decade later her apprentice founded the covenant. Peonn's death "
        "cut the regio off for about five years, and when the way was "
        "found again it claimed the vis Peonn had guarded. Its name comes "
        "from an old habit of kidnapping travellers until they no longer "
        "wished to leave, curbed this past century. Its device is a ring "
        "of sharp circumflexes.",
        "The regio copies the mountain: long, low houses of blue-white "
        "stone on terraces above vineyards, orchards and fields, almost "
        "everything warped by the aura to magical sight; the magi's "
        "laboratories are burrowed into the mountain's heart and kept at "
        "mundane warmth. It is bitterly cold, and its people, crops and "
        "beasts have adapted, with a body heat far below normal; the magi "
        "make charms against heat and cold, often in wedding rings, but "
        "give them to no outsider. Its 200 covenfolk are warped by the "
        "Aura of Ice; their children together are at best faeries, so 5 "
        "or 6 well-chosen mundanes must be kidnapped or won as spouses "
        "each year. Two laboratories are made for ice-distorted magi, and "
        "no Ignem can be studied in them.",
        "Uninvited mundanes meet a slow but very hostile answer from a "
        "small turb trained against faeries, good javelin men, some with "
        "spears that flash-heat and then freeze deep snow over their "
        "victims. It trades crystals, vis-spent wine and crafted goods at "
        "the Fair or through Rorschach. Only Merinita and Bjornaer magi "
        "vote, and Yselt, the senior Merinita, may veto any policy; there "
        "is always at least one Bjornaer, whose nature magic opens its "
        "oldest wards.",
    )
    what_matters = joined_lines(
        "Vis stores: 200 pawns",
        "Vis: 105 pawns a year, mostly Perdo, Auram and Herbam (the book prints +15; 30 pawns and 5 a point, Fourth Edition core p. 206)",
        "Income: covers its costs; it exports its farm surplus, smoky and black quartz, fluorite and lead from a small galena mine",
        "Supplies: 350 pounds of silver",
        "Library: 4500 levels of spells, mostly unpleasant faerie magic; Hermetic books worth 1350 points, favouring Perdo; mundane books worth 300 points, favouring faerie lore",
        "Covenfolk: about 200, distorted by the Aura of Ice",
        "Enchantments: trinkets that let ordinary people live in the cold, and magical spears; its guardian statues of ice or diamond are a spell",
        "Laboratories: average, specialised against the aura's rejection of fire",
        "Allies: the frost giants of Dachstein",
        "Enemies: Valnastium",
        "Boon: Regio (Major) (a Faerie 8 regio under an icy lake on Mont Joux)",
        "Boon: Difficult Access (a pool on a mountain, hidden by illusion)",
        "Boon: Mystical Allies (the giants of Dachstein)",
        "Boon: Mystical Portal (the gate to Arcadia on the peak)",
        "Hook: Faerie Aura (Bright Winter's regio)",
        "Hook: Distorted Covenfolk (the Aura of Ice)",
        "Hook: Evil Custom (spouses kidnapped each year)",
        "Hook: Suffrage (only Merinita and Bjornaer vote; Yselt's veto)",
        "Hook: Rival (Valnastium)",
    )
    covenant = b.covenant(
        "The Covenant Where Journeys End",
        tribunal=tribunal,
        founded=817,
        place=alps.places["mont_joux"],
        level=1,
        aura=8,
        realm="Faerie",
        summary=summary,
        what_matters=what_matters,
        detail=FULL,
        season="Autumn",
    )
    alps.covenants["journeys_end"] = covenant
    for key, name, house, age, summary in JOURNEYS_END_MAGI:
        _magus(alps, key, name, covenant, house, age, summary)


JOURNEYS_END_MAGI: tuple[tuple[str, str, str, int | None, str], ...] = (
    (
        "yselt",
        "Yselt",
        MERINITA,
        None,
        "Filia Rosalia, an ice-distorted, faerie-blooded maga who rarely "
        "leaves the covenant: leader of its council and community, a kind "
        "of stern aunt to her people, with the right to veto any policy. "
        "Her sigil is the icicle. Her sodales fear her Final Twilight may "
        "make her a faerie in the absent Queen's place, twisting the "
        "covenfolk into the shapes of the Queen's slain servants; she "
        "might one day have to be exiled. She and Andru of Valnastium are "
        "enemies, Miklos going between them.",
    ),
    (
        "carlo",
        "Carlo",
        MERINITA,
        None,
        "Filius Innocu, born of two parents distorted by the Aura of Ice, "
        "with the barbegazi's features: huge feet to tunnel through snow "
        "or slide over ice, burial in snow no harm to him, blizzards at his "
        "call. No one can tell where his faerie powers end and his "
        "Hermetic magic begins; many think he makes gestures with his "
        "faerie powers as a private jest. His sigil is icicles forming in "
        "his beard.",
    ),
    (
        "charlotte",
        "Charlotte",
        MERINITA,
        None,
        "Filia Lupina, daughter of a farmer and a goose maiden, who lacks "
        "the bundle of feathers that would let her take her mother's "
        "shape: her master trimmed the few she sprouted each year and used "
        "them in experiments. Graduated a decade ago, she has saved every "
        "feather since as Muto vis, and does not know her bundle is almost "
        "whole. She is timid, happier in a group with a strong leader, and "
        "still stuck in the unhappy adolescence her master's meddling left "
        "her.",
        # Her Latent Mystical Ability is a secret; see stats_magi.
    ),
    (
        "giselle",
        "Giselle",
        MERINITA,
        None,
        "Filia Bertrand, taken as an apprentice in error: her father was no "
        "faerie but a water elemental that possessed and sustained a "
        "drowned sailor. She has Faerie Magic, but her style is practical, "
        "decisive and acquisitive, and she often represents the covenant "
        "to other magi: mysterious, a little frightening and skilled in "
        "certamen. Her sigil coats each spell's target in moisture, "
        "deadly in the Alps.",
    ),
    (
        "capra",
        "Capra",
        BJORNAER,
        None,
        "Filia Bullfinch, a middle-aged Bjornaer maga whose heartbeast is "
        "the ibex. Faeries took her at sixteen, in mid-apprenticeship; she "
        "found her heartbeast with their help and served as a faerie wet "
        "nurse after her son, now the covenant's turb captain, was "
        "weaned. Recruited as a faerie midwife for the covenfolk's hard "
        "births, she travels the Order to deliver children too strange "
        "for Corpus spells. Her magic is poor for her age, and she cannot "
        "take an apprentice. She believes she is the new Amalthea, destined "
        "to find and raise the new Jupiter Pennius; her House thinks her "
        "mad and has asked the other Bjornaer to keep her from harm.",
    ),
    (
        "miklos",
        "Miklos",
        JERBITON,
        40,
        "Filius Kosma, a young Jerbiton who fell for Lyndsay, a companion "
        "the covenant brought to the Fair, and after three years and some "
        "willing mind-reading was let in. They have four children, none "
        "Gifted, each with faerie blood from both sides. Faerie-blooded "
        "himself, tied to night and summer, charming and a fine musician "
        "with his Arcadian mandolin, he is the covenant's emissary, an "
        "unofficial go-between of Yselt and Andru through Sourdine, and "
        "fascinated by magical clothes. A non-voting member.",
    ),
    (
        "eginhard",
        "Eginhard",
        BJORNAER,
        None,
        "Filius Caspar, of middle age, bonded with Kamilla; both take the "
        "shape of the lammergeier, and they share a laboratory and a "
        "sanctum. The less enlightened of the pair, since the perfect "
        "vulture is female, he spends more time in human form and has the "
        "better social skills: he dissects what he wants with great skill, "
        "mentions trouble-making stratagems to others rather than try "
        "them, and is glacially patient, then efficient and ruthless.",
    ),
    (
        "kamilla",
        "Kamilla",
        BJORNAER,
        None,
        "Filia Bamber, slightly younger than her partner Eginhard and the "
        "dominant of the two: she exemplifies the vulture's mind, "
        "intimidating smaller creatures, endlessly patient and so prudent "
        "about combat that it passes for cowardice. (The book also spells "
        "her Kamillia.)",
    ),
)


# ----------------------------------------------- Sinews of Knowledge


def _sinews(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    summary = paragraphs(
        "The Longevity Project, in caves behind a waterfall on a minor "
        "Danube tributary. Before the Order a hereditary priesthood kept a "
        '"dead god" here: an eight-foot skeleton chained by magical iron '
        "to a slab, which bleeds and slowly grows flesh, which the priests "
        "peeled away lest it rise and take revenge, and which slows aging "
        "when eaten. Guernicus judged it a human-shaped magical creature "
        "outside the Code. Someone wiped out the converted priesthood in "
        "the Sundering and tried to break its chains; House Guernicus "
        "sealed the site, and the Grand Tribunal of 865 gave it to Sancia "
        "filia Sabrina, archmaga of Perdo Corpus, who founded the Project. "
        "Its device is a cartouche crossed by a waterfall, a ruby at its "
        "foot.",
        "Bonisagus's longevity potions were first bettered by Sabrina "
        "filia Maura, third Primus of Bonisagus; progress has since slowed "
        "to nearly nothing, the last breakthrough being a formula that "
        "slows apparent aging, and the chief researcher is forever brewing "
        "for Hermetic notables. An eleventh-century Verditius founded a "
        "little lineage of hydraulic magi, who with Valnastium's Greek "
        "texts have built water and steam machines far beyond Europe's.",
        "It has no surplus income, which galls its magi: the Tribunal "
        "ordered it to stop making goods from vis to sell. It has no Hermes "
        "Portal, its magi have been surveying sites as far as Africa and "
        "Persia, and several minor covenants of outlying Tribunals have "
        "proposed a formal alliance that would make them its outlet. At "
        "its Aegis feast a dwarf's statue is sent over the falls in a "
        "barrel; it vanishes and turns up on the riverbank up to 21 miles "
        "away, and the covenfolk hunt it all year. Few grogs; its "
        "covenfolk, many in the village at the foot of the falls, speak "
        "Latin among their many tongues, their distortions mostly "
        "Immunities.",
        "Magi: Archmaga Philomena and Hubert of Bonisagus, Archmage Paxon "
        "and Balbina of Verditius, Sabastien of Tytalus and Cara of "
        "Bjornaer, with Ragoneda of Tytalus as a long-term, non-voting "
        "visitor.",
    )
    what_matters = joined_lines(
        "Vis stores: 200 pawns, mostly Corpus",
        "Vis: 80 pawns a year, 50 of them Corpus, the dead god's flesh among them",
        "Income: none; ordered by the Tribunal to stop making goods from vis",
        "Supplies: in trading debt",
        "Library: 3900 levels of spells, mostly Corpus rituals; Hermetic books worth 1800 levels, mostly fine Corpus tractatus with the lab texts and notes of every longevity researcher; mundane books worth 240 levels",
        "Enchantments: devices worth 275 levels, mostly for comfort: heat, light, clean air and water",
        "Laboratories: the two archmagi's excellent, if eccentric (Paxon's +10 to longevity rituals); Sabastien's and Cara's minimal; the other two good",
        "Allies: the elderly magi who need its service, who would help it in desperate times",
        "Enemies: the local count",
        "Contacts: the same clients, an informal and unreliable web of news",
        "Boon: Prestige (Major) (famous through the Order for the finest longevity potions)",
        "Boon: Superior Engineering (Major) (the overshot wheel and its steam and water machines)",
        "Boon: Favors Owed (Major) (the elderly magi it serves)",
        "Hook: Hermetic Services (Major) (longevity potions for the Order's notables)",
        "Hook: Poverty (Minor) (no surplus income)",
        "Hook: Monster (Major) (the dead god chained in its depths)",
        "Hook: Rival (Minor) (the local count)",
    )
    covenant = b.covenant(
        "Sinews of Knowledge",
        tribunal=tribunal,
        founded=865,
        place=alps.places["sinews_falls"],
        aura=7,
        summary=summary,
        what_matters=what_matters,
        detail=FULL,
        season="Autumn",
        notes="The site is older than the Order; 865 is the Grand Tribunal "
        "that gave it to Sancia filia Sabrina, its Hermetic founding.",
    )
    alps.covenants["sinews"] = covenant
    _vis_source(
        covenant,
        "The dead god's flesh",
        "Corpus",
        0,
        "The strips of flesh the chained skeleton grows, which slow aging; "
        "the book gives the covenant 50 Corpus pawns a year in all.",
    )
    for key, name, house, age, summary, hidden in SINEWS_MAGI:
        _magus(alps, key, name, covenant, house, age, summary, secrets=hidden)


SINEWS_MAGI: tuple[tuple[str, str, str, int | None, str, str], ...] = (
    (
        "philomena",
        "Philomena",
        BONISAGUS,
        None,
        "Archmaga, filia Rafe, the Longevity Project's chief researcher, "
        "slowed because her predecessors all but exhausted its line of "
        "work; if she succeeds, magi of middling Corpus could keep "
        "themselves until Twilight. Her own contribution is the potion "
        "that slows apparent aging. She asks magi to send her the bodies "
        "of human-shaped faeries through the Redcaps, freely shares a "
        "spell that keeps such bodies from decay, and pays for rare ones; "
        "some Merinita hate her for dissecting their kin. A Progressive, "
        "who sees Bonisagus as human and fallible and her own generation "
        "as no lesser. Many suspect she can strip a man's organs out onto a "
        "table; in truth she is no combat maga.",
        "She is an amaranth halfling, daughter of one of the faeries who "
        "grow the forbidden flower: immune to it, since her body makes it, "
        "she stopped aging at 21 and began gaining Twilight as if under a "
        "longevity potion, and expects to fade into Arcadia to join her "
        "father. She has a weak hold over amaranth addicts, who resist her "
        "words the worse for their addiction.",
    ),
    (
        "paxon",
        "Paxon",
        VERDITIUS,
        None,
        "Archmage, filius Valentin, the senior Verditius of the Tribunal "
        "and the finest longevity brewer active in the Order. He brews at "
        "most one potion for others every two years, and though a poor "
        "fighter has leverage enough to deter archmagi: to win his help "
        "one must outbid what an archmage or Primus could offer, and never "
        "by threat. He breaks no new ground and rarely competes at Verdi, "
        "so his House ranks him second tier, but he is its wealthiest and "
        "among its most influential. He holds the right to Staubbach "
        "Fall's Imaginem vis.",
        "",
    ),
    (
        "hubert",
        "Hubert",
        BONISAGUS,
        None,
        "Filius Lorenz, who studies the means by which hedge wizards "
        "lengthen their lives, to give them Hermetic form. His best lead "
        "inverts a familiar bond, so that the magus dies of age only when "
        "his familiar does: a snake, an eagle or an immortal faerie or "
        "elemental would carry him to Twilight without aging rolls, but "
        "its death would kill him at once.",
        "",
    ),
    (
        "balbina",
        "Balbina",
        VERDITIUS,
        None,
        "Filia Havelock (the member list calls her filius Seneca), whose "
        "name means stammerer: a curse stops her speaking aright while "
        "casting, so she leans on casting tools and is more traditional "
        "than most. She keeps the covenant's machines running, the great "
        "wheel above all, and is among the few of her House who repair "
        "enchanted items, a costly ritual designed anew each time; magi "
        "send her the strange things they dig up in the Levant, and she "
        "can often tell what one does and disable its defences. A "
        "descendant of Himinis the Mad, whose devices hide dangerous jokes.",
        "",
    ),
    (
        "sabastien",
        "Sabastien",
        TYTALUS,
        None,
        "Filius Luise, a professional intruder: for a stiff fee he walks "
        "into a dead magus's sanctum, makes sure nothing is about to "
        "explode, and for more disarms its wards; diabolism costs extra. "
        "The Council of Archmagi and the Quaesitores hire him, and between "
        "jobs he breaks into living magi's labs to show them their "
        "weaknesses. One of the highest Parmas in the Order, a Rego Vim "
        "specialist who keeps his trade secrets, with Charmed Life or "
        "Destiny or both; he spreads rumours of a unique Parma, a way past "
        "the Aegis and an artifact of the Mercurian priesthood.",
        "",
    ),
    (
        "cara",
        "Cara",
        BJORNAER,
        None,
        "Filia Sigurd, whose heartbeast is a piest, a serpent-whale the "
        "Irish know, from her birth near the Temple of Nodens in the "
        "Stonehenge Tribunal. She lives in the covenant's vast underground "
        "lake, explores the caves that riddle the Alps, and farms the deep "
        "pools: winkles by the pound and oysters by the bucket at the Fair, "
        "lobsters too big for two hands to ring, and now seed pearls, to "
        "ease the Tribunal's quarrel over wealth made by magic.",
        "",
    ),
    (
        "ragoneda",
        "Ragoneda",
        TYTALUS,
        56,
        "Filia Elisa, a comparatively young Corpus maga and a long-term, "
        "non-voting visitor who trades her service as the covenant's "
        "negotiator on minor matters for library and laboratory time; the "
        "maga a young covenant is likeliest to deal with at the Fair. She "
        "makes longevity enchantments for young magi, as tattoos, and is "
        "the covenant's chosen liaison to the spring covenant it hopes to "
        "trade through. Her sigil, the colour of bone, marks all her "
        "work: since her longevity potion she is all bone and ivory, and "
        "her fingernails are serrated like an infant's teeth and change "
        "with her mood. She keeps company to stay human, knowing that "
        "solitude leads to the Tower of Skulls. Her apprentice Augustina, "
        "eight years in training, is a bone maga of Animal who wants "
        "adventure.",
        "",
    ),
)


# ----------------------------------------------- Tarragon Vale


def _tarragon_vale(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    covenant = b.covenant(
        "Tarragon Vale",
        tribunal=tribunal,
        founded=None,
        place=alps.places["tarragon_hill"],
        aura=3,
        summary=paragraphs(
            "A covenant of metaphysical geographers and explorers, Hermetic "
            "pioneers of Arcadia and the land of spirits, whose great "
            "breakthrough was the Narrative Map, a device showing the "
            "structures under the shifting lands of the mystic realms. "
            "They held that faeries were only ways of meeting deeper forces "
            "that better tools let one ignore, which made them many enemies "
            "in House Merinita.",
            "Its four magi and its covenfolk vanished twenty-two years ago, "
            "the Vanishing Away, and no one has found out why. Its charter "
            "makes no provision for its end, so the Quaesitores will not "
            "dissolve it without bodies, lest its magi come back from "
            "Arcadia demanding their back vis: they store its income, "
            "spending only on its Aegis and its Shrouded Glen, and no estate "
            "may be settled without proof of death. The heirs want the "
            "hoard; most Alpine magi hope the heirs multiply until each "
            "gets only a rook. A quarter of those born here once had Second "
            "Sight, and its Sighted grogs were a prized export; the gift has "
            "waned, and children brought here to be born no longer get it.",
            "Cymena, a Redcap without the Gift whose grandparents came "
            "from here, lives at the site by no right but custom.",
        ),
        what_matters=joined_lines(
            "Vis: its income, about twenty years' worth, held in store by the Quaesitores",
            "Hook: Missing Expedition (the Vanishing Away)",
            "Hook: Indebted (Minor) (debts and supernatural enemies no one can name)",
        ),
        season="Winter",
        unnamed_magi=0,
    )
    alps.covenants["tarragon_vale"] = covenant
    _magus(
        alps,
        "cymena",
        "Cymena",
        covenant,
        MERCERE,
        48,
        "A Redcap without the Gift, small and level-headed, who looks in "
        "her late twenties: a mythic Redcap of the Alps, sure of every safe "
        "road between the covenants. She killed an Alpine dragonette "
        "herself and wears boots of its skin, of which she is very proud.",
        kind="companion",
    )


# ----------------------------------------------- Valnastium


def _valnastium(alps: Alps, tribunal: Tribunal) -> None:
    b = alps.b
    summary = paragraphs(
        "The domus magna of House Jerbiton, the Founder's family villa in "
        "a Dolomite valley, founded in law in 773 and in practice about "
        "775. Its device is a griffin collared with olive. Primi once built "
        "palaces round the town's plaza; most are now homes of favoured "
        "servant families or public buildings, and the Primus lives in the "
        "little villa on the hill as the Founder did. Magi lodge in the "
        "town and keep their laboratories in the gardens, among the "
        "enchanted graves of Jerbiton magi; the gardens, which the Founder "
        "laid out, are kept with reverence: a magically flat lawn, snails "
        "and dormice for the table, beehives, and plants from far lands in "
        "magical climates. Each fashion of the House leaves a layer in the "
        "valley, gallery, museum, patron's court, embassy or Roman farm.",
        "Members churn faster than at other old covenants. By tradition it "
        "has twenty or twenty-one, counting its chapters in Vienna, "
        "Constance, Saint Gallen and Geneva and its ties to covenants of "
        "other Tribunals, all joined by Hermes Portals, though only the "
        "council here may bar anyone from them; the valley itself has "
        "eleven residents. Four more chairs go to visiting specialists and "
        "guests, and the twenty-first, Bonisagus's chair, is a bursary of "
        "up to seven years for an exceptional young magus or a new spring "
        "covenant.",
        "The House elects its Primus by hourly ballots, one vote a magus, "
        "with proxies witnessed by a Quaesitor and no binding campaign "
        "promises; a Steward, a resident the Primus appoints, runs the "
        "House between Primi (Houses of Hermes: Societates p. 51, in place "
        "of Sanctuary of Ice's Secundi). Grogs serve in tent groups of "
        'eight, the contubernium from which, they say, "turb" comes. Its '
        "library, the finest in the Order for mundane research, invented "
        "the sloping shelf and trains librarians for other covenants.",
        "Magi resident: Primus Andru, Constance, Sourdine, Sirocco, Grazia, "
        "Kalliope, Bronwyn and Angela; Carmine of Flambeau lives here as "
        "Andru's wife and a vouched-for specialist, not a member. The "
        "Larta of Sanctuary of Ice (Josephine, François and Chloe) are "
        "covenfolk here, not members of the House.",
    )
    what_matters = joined_lines(
        "Vis stores: 100 pawns",
        "Vis: 125 pawns a year, traded to give a broad mix of Techniques (the book prints +19, 570 pawns; 30 pawns and 5 a point gives 125, and 570 is taken for a slip)",
        "Supplies: 50 pounds of silver",
        "Library: 2400 levels of spells; Hermetic books worth 900 levels; mundane books worth 1200 levels, some held in the chapters",
        "Covenfolk: almost a thousand in the valley's town and villages",
        "Enchantments: a wide network of Hermes Portals; masks and devices of the House that the Primus borrows",
        "Laboratories: good, but highly specialised",
        "Allies: the abbot of Saint Gallen",
        "Enemies: the Covenant Where Journeys End; the Fanes",
        "Contacts: a cardinal whose grandfather was a Jerbiton magus",
        "Boon: Wealth (Major) (the House's own)",
        "Boon: Mystical Portal (Hermes Portals to its chapters and beyond)",
        "Boon: Strong Community (the Ierbii)",
        "Boon: Powerful Ally (the abbot of Saint Gallen)",
        "Hook: House Covenant (House Jerbiton)",
        "Hook: Seat of Power (the domus magna and its Primus)",
        "Hook: Center of Excellence (the library)",
        "Hook: Rival (Minor) (Journeys End)",
        "Hook: Chapter House (Major) (Vienna, Constance, Saint Gallen and Geneva)",
    )
    covenant = b.covenant(
        "Valnastium",
        tribunal=tribunal,
        founded=773,
        place=alps.places["valnastium_valley"],
        aura=3,
        summary=summary,
        what_matters=what_matters,
        detail=FULL,
        season="Autumn",
        unnamed_magi=7,
    )
    alps.covenants["valnastium"] = covenant
    for key, name, city, region in (
        ("vienna_chapter", "Valnastium's Vienna Chapter", "Vienna", "eastern_marches"),
        (
            "constance_chapter",
            "Valnastium's Constance Chapter",
            "Constance",
            "western_alps",
        ),
        (
            "saint_gallen_chapter",
            "Valnastium's Saint Gallen Chapter",
            "Saint Gallen",
            "western_alps",
        ),
        ("geneva_chapter", "Valnastium's Geneva Chapter", "Geneva", "western_alps"),
    ):
        _chapter(
            alps,
            key,
            name,
            covenant,
            region,
            f"Valnastium's small chapter in {city}, joined to the valley by a "
            "Hermes Portal. Its magi supply the covenant with goods and live "
            "under the city's full Dominion, behind false owners for its "
            "houses and shops.",
        )
    for key, name, house, age, summary, kind in VALNASTIUM_PEOPLE:
        _magus(alps, key, name, covenant, house, age, summary, kind=kind)


VALNASTIUM_PEOPLE: tuple[tuple[str, str, str, int | None, str, str], ...] = (
    (
        "andru",
        "Andru",
        JERBITON,
        81,
        "Primus of House Jerbiton, filius Astrolabe, from Greece: elected "
        "Secundus at thirty-eight and Primus at forty-three, in 1182, "
        "helped by his fame for finding Akrotiri, the city buried in ash on "
        "Thera, whose works of art he recovered until vampires drove him "
        "off. Tall, muscular and clean-shaven, with short dark curls, "
        "dignified before crowds and warm alone; his hardest spells are "
        "illusions. A conciliator who looks conservative but may radicalise "
        "his House: he favours open dealings with great mundanes, keeps a "
        "network of agents and a vast correspondence, rallied the House to "
        "save Constantinople's art, and hopes to show the Church that the "
        "Gift is a charism. His talisman is a flame-red wedding veil, and "
        "his familiar a small aristocratic cat, Crucifixo (Houses of "
        "Hermes: Societates p. 52).",
        "magus",
    ),
    (
        "constance",
        "Constance",
        JERBITON,
        131,
        "Filia Frederich et Vortimer, over a hundred and thirty: trained in "
        "House Verditius, she worked for the Jerbiton under contract for "
        "fifty years before joining the House. Andru made her his Lesser "
        "Secundus, an office the Fifth Edition's House no longer has. A "
        "leader of the Craft School, which prizes the beautiful and the "
        "useful, she builds soaring, twisting laboratories and simple "
        "items for specialist labs; her lab texts sell at the Fair. Her "
        "adoptive parens Vortimer is of the lineage of Carolinus. The eldest "
        "living magus whose age the book gives, and so the Praeco here.",
        "magus",
    ),
    (
        "angela",
        "Angela",
        JERBITON,
        None,
        "Filia Constance, a Crafter who uses casting tools and makes magical "
        "instruments prized by musicians, and the covenant's factor at the "
        "Fair, where she buys unpredictably for her art, once a Belaquin "
        "grog's club of faerie-grown wood for its sound. Crafters and "
        "natural magicians compete for things of virtue. Not in the book's "
        "member list, but described as one (the twelfth).",
        "magus",
    ),
    (
        "sourdine",
        "Sourdine",
        JERBITON,
        None,
        "Filia Bronwyn, the House's finest spy: Gently Gifted and a silent "
        "caster of subtle gestures, she is Lord Roland of the Val Gardenia "
        "at the Emperor's court, but would sooner take a kidnapped servant's "
        "place and smooth it over with Mentem. One of Andru's closest "
        "confidants, she runs the top of his intelligence network, whose "
        "reports go to the library's correlators, and is Miklos's contact.",
        "magus",
    ),
    (
        "sirocco",
        "Sirocco",
        JERBITON,
        None,
        "Filia Andru, who leads the House's push into Islamic North Africa "
        'with the pro-Islamic Jerbiton of Iberia\'s "Roman" covenants and '
        "their links to Moorish magicians. She is quietly trying to learn "
        "what became of the last covenant founded near Tunis, said to be "
        "enslaved by desert demons.",
        "magus",
    ),
    (
        "grazia",
        "Grazia",
        JERBITON,
        None,
        "Filia Natura, an Animal specialist who keeps the stables, kennels "
        "and mews: horses, donkeys, hounds and hawks trained to accept the "
        "Gifted, a few truly magical, sold at the Fair and along the "
        "Redcap roads. She pays well for breeding stock and established "
        "pairs of magical beasts, and is beginning to tame griffins.",
        "magus",
    ),
    (
        "kalliope",
        "Kalliope",
        JERBITON,
        None,
        "Filia Bibliophilus, a magus of middle years, the latest of the "
        "valley's line of librarian-magi, who keep a small community with "
        "their like at Durenmar, Verdi and a few other covenants.",
        "magus",
    ),
    (
        "bronwyn",
        "Bronwyn",
        JERBITON,
        None,
        "Filia Astrolabe, trained by the Primus's own parens, who studies "
        "Hermetic phonotactics, the voice as a tool of casting, and now "
        "rhyme and metre in spells, which would make them easier to learn "
        "if harder to design. Flighty and easily distracted, she has not "
        "published, and her verse is doggerel.",
        "magus",
    ),
    (
        "carmine",
        "Carmine",
        FLAMBEAU,
        None,
        "Filia Susannah of House Flambeau, of mixed Iberian blood, one of "
        "the most beautiful women alive, dark-haired and dressed in black. "
        "She came in Andru's entourage forty-three years ago, became his "
        "model, his mistress and his wife, and is the valley's hostess. "
        "She follows the School of Sebastian, works magic on molten metal, "
        "and helps House Jerbiton when extreme violence is called for; she "
        "has passed the Jerbiton Gauntlet but prefers her independence. A "
        "muse. Their children are middle-aged, with grandchildren in their "
        "twenties; none has the Gift, and some are autocrats, scribes, "
        "priests and librarians (Houses of Hermes: Societates p. 52).",
        "magus",
    ),
    (
        "josephine",
        "Josephine",
        "",
        None,
        "A chef from the Engadine whose food is as good as magic, at home "
        "with both noble and peasant cooking: an urban kind of folk "
        "magician. Sanctuary of Ice makes her a Larta, an unGifted member "
        "of House Jerbiton; the errata removes such members, so she is a "
        "companion of the covenant.",
        "companion",
    ),
    (
        "francois",
        "François",
        "",
        None,
        "The elderly but powerful blacksmith of the Village of the Vale, "
        "whose smithy is one of the most magical places in the valley. His "
        "large family serves as grogs; some have a frightening knack with "
        "weapons and become sergeants elsewhere, and his journeymen find "
        "places in covenants across the Order. A Larta in Sanctuary of "
        "Ice, a companion here.",
        "companion",
    ),
    (
        "chloe",
        "Chloe",
        "",
        None,
        "The valley's chief minstrel, who composes rather than performs: "
        "soaring choral prayers, magical when others sing them, often clergy "
        "in churches, and a key part of Andru's charm offensive. She seems "
        "an odd, perhaps unique, natural magician. A Larta in Sanctuary of "
        "Ice, a companion here.",
        "companion",
    ),
)


def finish(alps: Alps) -> None:
    """Andru and Carmine are husband and wife, and Miklos's contact at
    Valnastium is Sourdine."""
    andru, carmine = alps.magi.get("andru"), alps.magi.get("carmine")
    if andru is not None and carmine is not None:
        alps.b.link(andru, "characters", carmine, "His wife")
        alps.b.link(carmine, "characters", andru, "Her husband")
    miklos = alps.magi.get("miklos")
    sourdine = alps.magi.get("sourdine")
    if miklos is not None and sourdine is not None:
        alps.b.link(miklos, "characters", sourdine, "His contact at Valnastium")
