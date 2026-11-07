"""Fortunata of Jerbiton and her Island of Bound Spirits, in paraphrase of
Legends of Hermes, chapter three (pp. 46-69), with the errata's corrections
to Maintain the Caster's Spell and to Fax's block (Errata p. 78).

The island's sea and Tribunal are the saga's choice, so its location stays
blank and the book's guidance is in its secrets. Its Magic aura is 4 and the
villa's 6, with no regio. The books, Initiation Scripts, Lab Texts, devices
and spell containers are in words in the secrets of the laboratory that
holds them, since a Book record needs an owning covenant. The stories are
dormant threats. Stat blocks are the book's; the rest is a summary, not its
words. Every printed block is a spirit or beast, so all are in the Bestiary;
the book gives Fortunata herself none, and she and the other people without
blocks are sketches. Island Lore is kept as Area Lore: Fortunata's Island,
and Mediterranean Lore as Area Lore: Mediterranean. Magical Animal and the
free Size +2 of Monocaudus's block are not in the Virtue catalog, so they
are named in his notes only."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ...models import BodyVis
from ..builder import (
    Builder,
    characteristics,
    dormant,
    joined_lines,
    paragraphs,
    titled,
    vf_great,
    vf_puissant,
)

if TYPE_CHECKING:
    from ...models import Neighbour

JERBITON = "house_jerbiton"
BONISAGUS = "house_bonisagus"
FLAMBEAU = "house_flambeau"
ISLAND_LORE = "Area Lore: Fortunata's Island"
SEA_LORE = "Area Lore: Mediterranean"
ORDER_LORE = "Organization Lore: Order of Hermes"
GREEK = "Living Language: Greek"
ITALIAN = "Living Language: Italian"
LATIN = "Dead Language: Latin"

REMEMBERED = [
    titled(
        "What all know of Fortunata",
        joined_lines(
            "Known by All (Ease Factor 0):",
            "- A spirit master and maga of House Jerbiton.",
            "- Active in the Rome Tribunal, she left it for a private retreat.",
            "- She beat many enemies outside the Order in southern Europe and "
            "North Africa.",
            "- Her power came from ancient lore, and she translated the ancients.",
            "- She robbed many Mysteries of their power.",
            "- Her books are said to tell how to win the same powers.",
            "- Hermetic enemies drove her into exile.",
            "- She vanished into Twilight about 1123.",
        ),
    ),
    titled(
        "What is widely known of Fortunata",
        joined_lines(
            "Widely Known (Ease Factor 6):",
            "- She kept no familiar, only a spirit who went with her.",
            "- A cloud of airy spirits surrounded her, quick to obey.",
            "- [Jerbiton magi only] A very gifted scholar who failed her House "
            "through envy of magical power.",
            "- She belonged to no known Mystery Cult, though she wrote of many.",
            "- [Redcaps only] Her house in Venice welcomed Redcaps richly.",
        ),
    ),
    titled(
        "Uncommon knowledge of Fortunata",
        joined_lines(
            "Uncommon Knowledge (Ease Factor 12):",
            "- She answered charges of infernalism and magical spying and walked "
            "free, then retired anyway.",
            "- She owned and ran a house in Venice, for years a meeting place of "
            "Redcaps.",
            "- Her retreat lay among the many small islands of the Ionian Sea, or "
            "whichever part of the Mediterranean suits the saga.",
            "- Many admired her scholarship, but her parens was disappointed.",
            "- By magic she translated scrolls no one could read, going past the "
            "Hermetic limits on translation.",
        ),
    ),
]
REMEMBERED_NOTES = paragraphs(
    "What the Order Remembers (p. 48): a simple roll of Intelligence + Order "
    "of Hermes Lore recalls everything up to the Ease Factor it reaches (p. "
    "10). Some of it is false, grown from envy and from the fable she has "
    "become. A library can be searched as well (Covenants p. 98).",
    "Lost Secrets (Ease Factor 18): the book lists none for her. It says a "
    "few details are known only to some Redcaps or Jerbiton magi, and gives "
    "no bonus to any House's roll.",
)

LOCATION = [
    titled(
        "The island's vis",
        "Vis (p. 60): magi who take the time to study Fortunata's island can "
        "find sources of about 20 pawns a year, of Rego, Muto, Aquam, Auram, "
        "Imaginem, Mentem and Vim.",
    ),
    titled(
        "The bound guardians",
        "Bound spirits (p. 59): Fortunata cast a command spell on each guardian "
        "of her island and made it permanent by Spell Binding, each in a "
        "container now in the laboratory. Whoever holds a container may claim "
        "to rule that spirit.",
    ),
    titled(
        "Breaking a binding",
        "Breaking one of Fortunata's binding containers ends the Sustain spell "
        "and the command, and frees both spirits. A spell that countermands an "
        "active command must exceed its level and penetrate the spirit's Magic "
        "Resistance, so finding and breaking the container is usually easier.",
    ),
    titled(
        "How Tempestas is bound",
        "Tempestas's binding is the book's example: Coerce a Spirit of Auram "
        "(ReAu 15, Touch, Diameter, Individual; base 5, +1 Touch, +1 Diameter), "
        "held by Sustain a Spell of Auram (ReVi(Au) 20, Touch, Special, "
        "Individual, Ritual; four pawns of vis) and a lesser Auram spirit. "
        "Cheaper than an invested constant effect, it uses her own cast-spell "
        "Penetration. Countermanding it means beating level 15 and Tempestas's "
        "Might 35, or level 20 and the lesser spirit's Might.",
    ),
    titled(
        "The danger of the spirits",
        "The island's spirits often lack the Might to pass even a shared Parma "
        "Magica, but they work indirectly on magi and are very dangerous to "
        "companions and grogs parted from them by the storm. They are also part "
        "of the treasure, for whoever finds their containers (p. 67).",
    ),
    titled(
        "Storyguide Notes",
        paragraphs(
            "Location: the book leaves it open, with the governing Tribunal, "
            "for each saga to choose (pp. 56, 59). It offers the Tyrrhenian, "
            "the Adriatic, the Ionian, the Aegean or even the Balearics. Its "
            "text uses the Ionian Sea as its stand-in, which would put the "
            "island off the west coast of Greece between the Roman and Theban "
            "Tribunals, and wherever it says Ionian Lore it means the Area Lore "
            "of the saga's choice.",
            "Finding it by study (p. 56): after a season with her personal "
            "writings, roll Intelligence + Mediterranean Lore against Ease "
            "Factor 18, or Intelligence + Ionian Islands Lore against 15. "
            "Success gives a hunch where to look. A botch gives a false trail, "
            "which a visit clears up, and later study may still give the true "
            "place. Her writings describe how she lived, not where, so they are "
            "poor geography.",
            "The book gives neither the vis sources nor the split. It gives "
            "Tempestas's lesser spirit Might 20 in one place and Might 15 in "
            "another (p. 59).",
        ),
    ),
]

PRINCIPLES = [
    titled(
        "Principles Lore",
        "Principles Lore (pp. 47-50): an Organization Lore Fortunata devised "
        "to order the Initiations she made, which serves as Cult Lore for a "
        "set of Initiations with no cult: no ranks, no hierarchy, no fixed "
        "sequence. Some study of it is needed before any script can be used. "
        "Magi already in a Mystery Cult can adapt the texts to that cult. She "
        "practised it for whole seasons; a season's Practice of a Cult Lore "
        "has Source Quality 4, or 5 if inspired by a compatible text of "
        "another cult (p. 49).",
    ),
    titled(
        "The order of the scripts",
        "Fortunata's earlier scripts have higher bonuses, from when her Lore "
        "was low; later ones assume mastery. Partial order (p. 49): Spirit "
        "Familiar; Minor Magical Focus, with the Ordeal; Major Magical Focus, "
        "first after it; Spell Binding, second; Hermetic Empowerment, third.",
    ),
    titled(
        "The missing script",
        "A script for Hermetic Synthemata (The Mysteries: Revised Edition p. "
        "87) is gone from Fortunata's library.",
    ),
]
PRINCIPLES_NOTES = paragraphs(
    "Self-Initiation (pp. 49-50): the maga is her own Mystagogue, with her "
    "own Presence and Lore, at the Target Levels for a Virtue she lacks. "
    "Initiation is summarised on p. 50 and given in full in The Mysteries: "
    "Revised Edition, chapter 2. Adapting an existing organization needs "
    "troupe approval and a mystical character; otherwise devise a new "
    "Ability.",
    "Adapting a script (pp. 49-51): study another cult's script for a week, "
    "then Intelligence + that cult's Lore against 9 to understand it, or "
    "study again; a botch gives a false script. Modifying a component is "
    "Intelligence + own Lore against 12, replacing an element against 15, "
    "and adding a Quest (+3 Script Bonus) against 9. Keep a record of "
    "Ordeals: they lower the next three Initiation Totals. Scripts that "
    "overlap may have spent the same Quests and Ordeals. Sacrifices repeat "
    "more easily than Ordeals.",
)

SCRIPTS = [
    titled(
        "The Mastery of Principles",
        "The Mastery of Principles, Puissant Principles Lore, +2 to the score "
        "(p. 51). Quest for lost texts on the Lore, then write a new one; Vow "
        "to resurrect the Principles (an Ordeal, Minor Flaw); second Quest, "
        "three other magi study the text and each write a tractatus in return. "
        "At dawn on midwinter solstice, on a remote magical high peak (she "
        "suggests Olympus or the Great Pyramid), burn incense and give 5 pawns "
        "to the spirits of magic. Initiation Total 18, Script Bonus 16: Ordeal "
        "3, Quest 3, Quest 3, Place and Time 3, Initiate's Time 1, Sacrifice of "
        "Vis 1, Sympathy 2. Needs Presence + Lore 2. It seems she never used "
        "it; she left copies for others, and they sit forgotten in covenant "
        "libraries.",
    ),
    titled(
        "The Myth of Andros and the Tree",
        "The Myth of Andros and the Tree, Spirit Familiar (pp. 51-52), adapted "
        "from a Greek rite of union with spirits. Quest to find and free the "
        "spirit; Quest to beat and imprison its enemy; a place and time deeply "
        "significant to the pair, for the troupe to settle. Total 18, Script "
        "Bonus 12: Quest 3, Quest 3, Place and Time 3, Sympathy 3. The Virtue "
        "is in The Mysteries: Revised Edition p. 66; here bonding level is the "
        "spirit's Might + 25, and the cords are the Hermes, Isis and Hekate "
        "Cords (p. 52).",
    ),
    titled(
        "Plutonic Beginnings",
        "Plutonic Beginnings, Minor Magical Focus (commanding spirits) (pp. "
        "52-53), from a Roman cult of the dead. Suffer the torments of free "
        "spirits and command them aloud, under the vows of the Principles. The "
        "Ordeal gives the Major Flaw Necessary Condition (speak the names of "
        "spirits): she must always cast aloud, and hearers may know the "
        "invocations. She meant pagan gods; varying it to saints is an "
        "Intelligence + Principles Lore roll against 12, or the troupe may "
        "count saints as spirits. Covers Rego (Form) that commands "
        "insubstantial spirits of any Form, no Technique requisites. Total 18, "
        "Script Bonus 12: Major Ordeal 9, Sympathy 3.",
    ),
    titled(
        "The Myth of Aerius and Pluto",
        "The Myth of Aerius and Pluto, Major Magical Focus (spirit magic) (p. "
        "53). Replaces any Minor Magical Focus. Defeat a spirit of Might 20 or "
        "more, then use it to defeat a second as strong. At midnight on All "
        "Hallow's Eve, at the second defeat's site, free the first and give it "
        "a rook of vis. Covers Rego (Form) on insubstantial spirits, requisites "
        "allowed, and other Techniques with a Rego requisite. Total 21 (30 less "
        "9 for the Ordeal), Script Bonus 13: Required Virtue 3, Place and Time "
        "3, Quest 3, Quest 3, Sacrifice 1. Needs Presence + Lore 8.",
    ),
    titled(
        "The Myth of Heiro and the Cave",
        "The Myth of Heiro and the Cave, Spell Binding (pp. 53-54; the Virtue "
        "is in The Mysteries: Revised Edition p. 27). She found a flawless "
        "natural bubble of glass almost too fine to see. On the first new moon "
        "after midwinter she crawled without light or magic to the heart of a "
        "deep cave system in the Alps, and forced a spirit, still without "
        "magic, into the ball to sustain a spell of light, the one spell "
        "allowed. Tales differ on the spirit: a beaten foe freed on a promise, "
        "a bribed ghost, a tricked mountain elemental. Total 12 (18 less 6, as "
        "second after the Ordeal), Script Bonus 6: Place and Time 3, Quest 3. "
        "Needs Presence + Lore 6.",
    ),
    titled(
        "The Myth of Heiro and the Haunted Graveyard",
        "The Myth of Heiro and the Haunted Graveyard, Hermetic Empowerment "
        "(pp. 54-55; the Virtue is in The Mysteries: Revised Edition p. 64). "
        "Enchant a device in a graveyard, abandoned or hidden in, building a "
        "laboratory there (Basic Laboratory, ArM5 p. 94: a season, 500 square "
        "feet, -3 to Lab Totals; Covenants chapter 9). At least 5 pawns, each "
        "from the destruction of a different ghost: one pawn of its remains "
        "goes into the device, the rest to the spirits. A lesser device will "
        "do. On a quarter-day burn the device in the graveyard on a pyre of "
        "rare woods and incense, dawn to dusk. Total 18 (15 as third after the "
        "Ordeal), Script Bonus 9: Place and Time 3, Quest 3, Sacrifice 1, "
        "Sympathy 2. Graveyards usually have Divine aura 4, fading once "
        "abandoned; church rites keep Christian dead from rising, so look to "
        "those buried outside or to ancient pagan ground.",
    ),
    titled(
        "Two scripts without detail",
        "On A Pilgrimage To Jerusalem, Sense Holiness & Unholiness, and The "
        "Myth of Aquila's Eyes, Improved Characteristics (Perception): listed "
        "on p. 64, with no other detail in the book.",
    ),
]

LIBRARY = [
    titled(
        "Fortunata's works on Principles Lore",
        joined_lines(
            "Her own works on Principles Lore (p. 64):",
            "- Principles for a Better Life, tractatus, Quality 11",
            "- Principles of Life as a Magus, tractatus, Quality 11",
            "- Principles of Power, tractatus, Quality 11",
            "- Principles of the Spirit, tractatus, Quality 11",
            "- De Disciplinae Fortunatae (Fortunata's Principles), summa, Level "
            "4, Quality 11",
        ),
    ),
    titled(
        "Other texts in the library",
        joined_lines(
            "Other texts (p. 64):",
            "- Heroes of Olympos, tractatus on Magic Lore, Quality 7, Latin, by "
            "Julius of Nicomedia",
            "- Heroes and Gods, tractatus on Magic Lore, Quality 8, Greek, by Polymos",
            "- Necronomicus, tractatus on Necronomicus Lore, a forgotten cult, "
            "Quality 8, Latin, anonymous",
            "- Piraeon, tractatus on Piraeon Lore, a forgotten cult, Quality 9, "
            "Greek, anonymous, with her Latin translation",
            "- Cult of the Wanderer: revised edition, tractatus on Cult of the "
            "Wanderer Lore, a forgotten cult, Quality 9, her Latin translation "
            "of a lost anonymous Greek original",
            "- Heroes of Rome, tractatus on Magic Lore, Quality 8, and on "
            "Mediterranean Lore (history), Quality 8, Latin, by Caius of "
            "Mediolanum",
            "- Ionian Isles, tractatus on Mediterranean Lore, Quality 11, by Fortunata",
            "- The Names of Ghosts, tractatus on Magic Lore, Quality 11, by "
            "Fortunata, listing the ghosts she called and what use they were, "
            "such as the tongues they read",
            "- Ordinary Hermetic summae and tractatus on Magic Theory, Imaginem, "
            "Ignem, Terram, Mentem, Vim and all five Techniques; the book gives "
            "no titles or figures",
        ),
    ),
    titled(
        "Fortunata's Lab Texts",
        joined_lines(
            "Lab Texts (p. 65):",
            "- Coerce the Spirit of (Form), Re(Form) 20, Voice, Diameter, "
            "Individual (base 5, +2 Voice, +1 Diameter): obeys while she can "
            "threaten it. Coerce the Spirit of Earth (Te), Coerce the Spirit of "
            "Fire (Ig), Coerce the Spirit of Illusion (Im), Coerce Ghosts (Me)",
            "- Incantation of Summoning the Dead, ReMe 40, Arcane, Concentration, "
            "Individual, Ritual (ArM5 p. 152). Can call a ghost haunting the "
            "area if its full name is known, though a non-Ritual spell can too",
            "- Summon the Spirit of (Form), Re(Form) 40, Arcane, Concentration, "
            "Individual (base 15, +4 Arcane, +1 Concentration): needs an Arcane "
            "Connection or the spirit's non-magical name; the element serves as "
            "a Connection to a spirit residing in the area. Summon the Spirit of "
            "Earth (Te), Summon the Spirit of Fire (Ig), Summon the Spirit of "
            "Illusion (Im), Summon the Spirit of Man (Me). The last is a lesser "
            "non-Ritual Incantation of Summoning the Dead, reaching only a ghost "
            "actively haunting something, or one the caster has already called",
            "- Thoughts Within Babble, InMe 30, Personal, Sun, Hearing (base 5, "
            "+2 Sun, +3 Hearing): her version lasts the day, so she need not "
            "concentrate while texts are read to her",
            "- Sustain a Spell of (Form), ReVi(Form), general, Touch, Individual, "
            "Ritual, Mystery (Spell Binding): for Terram, Ignem, Imaginem and "
            "Mentem, at levels 20, 30 and 40. Duration Special on pp. 53 and 59, "
            "Momentary on p. 65",
            "- Empowering Prison of the Declining Spirit, Re(Mu)Vi(Form), "
            "general enchantment, Mystery (Hermetic Empowerment), Personal, "
            "Momentary, Individual, Pen +0, 1 use a day: for Terram, Ignem, "
            "Imaginem and Mentem, at levels 20, 34 and 50",
        ),
    ),
    titled(
        "The agony of empowerment",
        "The draining of a spirit bound by Hermetic Empowerment is agony: "
        "breaking the device is likely to free a maddened spirit that feels no "
        "gratitude.",
    ),
]
LIBRARY_NOTES = paragraphs(
    "Guidelines (p. 65, from The Mysteries: Revised Edition p. 28): level 5, "
    "control a disembodied spirit of (Form); level 15, summon one.",
    "Spell Binding (p. 53): cast the Ritual on a container, then the second "
    "spell while it lasts, or in the next round if it is Momentary. The "
    "second spell must be longer than Momentary and not a Ritual. Force a "
    "spirit into the container in that time and the spell lasts until the "
    "spirit is freed by dispelling or by breaking the container. The spirit "
    "must share something with the spell, as an elemental its element, and "
    "have Might of at least the spell's level. The Ritual's base level "
    "(guideline) must at least equal that level, and requires the spell's "
    "Forms.",
    "Hermetic Empowerment (p. 54): a device holds Ritual effects paid for by "
    "a bound spirit, each use draining the effect's magnitude from its Might "
    "Score, with effect level at most twice that score, so it is never quite "
    "emptied. Empowering Prison (guideline) has requisites for every Form it "
    "powers, base level at least twice the spirit's Might, and uses a day "
    "that limit the Ritual effects a day. The bound spirit spends Might only "
    "to resist, can use costless powers, and is freed if the Prison is "
    "disenchanted or the device broken.",
)

TREASURES = [
    titled(
        "The Spell Binding containers",
        "The Spell Binding containers (pp. 59-60, 65-66, 69): set into the "
        "solid stone of the floor by Rego Terram; Intellego Vim shows them. A "
        "carved agate head holds Tempestas, a large ruby Fax, a leaden "
        "plumb-weight Lapidosus.",
    ),
    titled(
        "Calling the Dead",
        "Calling the Dead, ReMe 60, Pen +20, 24/day, Arcane, Concentration, "
        "Individual (p. 65): calls a ghost with a regular haunt if the user is "
        "there, or one already called by magic, given an Arcane Connection such "
        "as its full name. Suits spirits first called by Ritual. The Staff "
        "keeps up the concentration until the ghost is dismissed. (Base 15, +4 "
        "Arcane, +1 Concentration, +10 levels Penetration, +5 levels 24/day, +5 "
        "maintain concentration.)",
    ),
    titled(
        "Maintain the Caster's Spell",
        "Maintain the Caster's Spell, ReVi 45, Pen +0, 24/day, Touch, Diameter, "
        "Individual (p. 65): holds up a spell of level 40 or below that the "
        "user has cast and is concentrating on, for a Diameter, while she does "
        "other things, and she may still concentrate to alter it. (Base 30, +1 "
        "Touch, +1 Diameter, +5 levels 24/day.) Per the errata (p. 78) this "
        "effect was invested in her Talisman, relies on a Talisman's closer tie "
        "to its maker, and works for no other magus, though laboratory "
        "investigation shows it.",
    ),
]
TREASURES_NOTES = (
    "The book names Tempestas, Fax and Lapidosus and says the guardians include "
    "them. The book says Staff of the first effect and the errata Talisman of "
    "the second; neither says they are one object, or where it lies."
)


def build(b: Builder) -> None:
    island, villa, venice, cave = _places(b)
    _people(b)
    _spirits(b, island, villa)
    witches = _witches(b)
    _stories(b, island, villa, venice, cave, witches)


def _places(b: Builder) -> tuple[Neighbour, Neighbour, Neighbour, Neighbour]:
    island = b.place(
        "Fortunata's Island",
        summary=paragraphs(
            "A small, low island, a mile or two across, no different from a "
            "distance from the countless others of the Mediterranean. If it "
            "has a name, only the fishermen nearby know it, and they keep "
            "away for the foul weather.",
            "Sandy beaches, dunes and dune grass ring it, and the storms "
            "leave driftwood along the shore. The ground rises 100 to 200 "
            "feet at the centre, where gorse, thorn and olive take over. "
            "Springs in the interior feed streams that run through gullies "
            "in the dunes to the sea, with mussels and small fish in them, "
            "crabs in the creeks, and sea fish for anyone who dares the "
            "weather.",
            "The beaches are featureless, and walkers lose count of the "
            "distance and cannot tell whose tracks they are following. "
            "Voices and music drift about the interior; people and buildings "
            "show in the distance, even a village, and are gone at the next "
            "turn. The ghosts of drowned sailors sometimes march along the "
            "shore. From a few places a Roman villa can be seen, before the "
            "dunes hide it again.",
        ),
        secrets=LOCATION,
        aura=4,
        status="Rumoured",
        known="",
    )
    villa = b.place(
        "Fortunata's Villa",
        inside=island,
        summary=paragraphs(
            "A house in the Roman manner, built new by a maga and not "
            "preserved from antiquity, after the Jerbiton villas of "
            "Valnastium. A central range of two stories runs about 120 feet, "
            "with two longer side ranges of stores and workrooms reaching "
            "150 feet south. It is shaded against the summer sun and has "
            "fireplaces for winter.",
            "It has been ill kept. The straw is old and stale, and most rooms "
            "are shuttered and damp, their furnishings under mouldering "
            "drapes and spider webs. Candle flames burn throughout, and "
            "mirrors hang on the walls. A corridor winds through the building, "
            "broken by some rooms, many of which open into one another; "
            "pillars moulded with Hermetic motifs frame the outer doors and "
            "those of the larger rooms. The best rooms, her bedchamber and "
            "dining room among them, have mosaic floors and painted walls in "
            "a classical style, now damaged.",
            "Mirrors here do not reflect truly, shadows move by themselves, "
            "and the spiders are alarmingly large, legs nearly a hand-span "
            "across and bodies bigger than a man's thumb.",
        ),
        secrets=[
            titled(
                "The warped villa",
                "The high aura has warped the contents of Fortunata's villa (p. 61).",
            ),
            titled(
                "Sight spells on the villa",
                "Magi casting Sight spells from outside soon learn they see "
                "only an image of the villa, not the house (p. 60).",
            ),
            titled(
                "The Imagines of the villa",
                "Imagines such as Error and Cantus gather in Fortunata's villa "
                "for the aura and to tease the mirrors, and treat strangers as "
                "toys (pp. 61-62).",
            ),
            titled(
                "Where Lucida goes",
                "Lucida moves through the library, the laboratory and "
                "Fortunata's bedroom, scolding Monocaudus.",
            ),
            titled(
                "Where Monocaudus lurks",
                "Monocaudus lurks by the villa's kitchen fire, and spends much "
                "of the day outdoors on the excuse of firewood or food.",
            ),
            titled("Whose flames they are", "The villa's flames are Fax's."),
            titled(
                "The hidden rooms",
                "Those who search only the open rooms of the villa find an "
                "abandoned house. The laboratory and library take careful "
                "looking (p. 55).",
            ),
        ],
        aura=6,
        known="",
    )
    b.place(
        "The Villa Graveyard and Necromanteion",
        inside=villa,
        summary=paragraphs(
            "A small graveyard beside the villa, where the dead rest in stone urns.",
            "Beside it are a spring and a pool among cypress trees, and a "
            "false doorway in the villa's north wall, sheltered by an arch "
            "and closed by an iron gate, with mosaics of Hades within.",
        ),
        secrets=[
            titled(
                "The pagan urns",
                "Many of the graveyard's urns hold pagan burials brought from "
                "elsewhere and re-interred so that their ghosts could be called "
                "with ease.",
            ),
            titled(
                "The false doorway",
                "The false doorway in the villa's north wall is a necromanteion, "
                "once used in ceremonies to reach the dead (p. 62).",
            ),
            titled(
                "Storyguide Notes",
                "The book prints no aura for the graveyard itself, so none is "
                "entered; the island's is 4 and the villa's 6.",
            ),
        ],
        known="",
    )
    b.place(
        "Fortunata's Laboratory and Library",
        inside=villa,
        summary=(
            "A room at the core of the house, surrounded by others, with no "
            "door and no window. The rooms around it are laid out so that its "
            "absence is not obvious."
        ),
        secrets=[
            titled(
                "Finding the hidden room",
                "Careful study or mapping shows the missing space in the villa, "
                "but only magic gets into Fortunata's laboratory.",
            ),
            titled(
                "Who knows the way in",
                "Monocaudus has never entered Fortunata's laboratory; only "
                "Lucida knows the secret (p. 62).",
            ),
            titled(
                "The bare laboratory",
                "Fortunata's laboratory is surprisingly sparse, since much of "
                "her work was done outdoors among spirits. Cleaned, with its "
                "perishable stocks replaced, it would serve as a standard "
                "laboratory.",
            ),
            *PRINCIPLES,
            *SCRIPTS,
            *LIBRARY,
            *TREASURES,
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The book says four tractatus, a summa and nine Initiation "
                    "Scripts, but names eight (p. 64); the ninth may be the lost "
                    "Hermetic Synthemata script.",
                    PRINCIPLES_NOTES,
                    LIBRARY_NOTES,
                    TREASURES_NOTES,
                ),
            ),
        ],
        aura=6,
        known="",
    )
    venice = b.place(
        "Fortunata's House in Venice",
        summary=(
            "An old house in Venice, sold cheaply after standing empty for "
            "a while. It was once a meeting place of Redcaps, and a rich "
            "welcome waited for them here; few now remember whose it was."
        ),
        secrets=[
            titled(
                "Lucio's haunting",
                "Fortunata's house in Venice is haunted by Lucio, who has "
                "frightened off earlier owners without meaning to.",
            ),
            titled(
                "The hidden papers",
                "Fortunata hid papers behind wall panels and under floorboards "
                "of her Venice house. A search finds personal papers and "
                "letters, a partial catalog of her library, and letters to "
                "contacts on several small islands about small purchases and "
                "favours.",
            ),
            titled(
                "The islands in the letters",
                "Intelligence + Mediterranean Lore against 9 shows that the "
                "islands in Fortunata's letters lie close together, and "
                "probably near hers.",
            ),
            titled(
                "Storyguide Notes",
                "The book gives its street and quarter no more than the city, "
                "and no aura. Any magus knows of a house in Venice on "
                "Intelligence + Order of Hermes Lore against 6, or Intelligence "
                "+ Mercere Lore against 3; a Redcap knows that this is that "
                "house against 9 (p. 56).",
            ),
        ],
        realm="",
        known="Locally",
    )
    cave = b.place(
        "Omaion's Cave",
        summary="A cave in a remote waste in Turkey.",
        secrets=[
            titled(
                "Whose cave it is",
                "The cave is the home of Omaion the Serpent, in the book's main "
                "version of him (p. 58).",
            ),
            titled(
                "Storyguide Notes",
                "The book says nothing more of where it lies.",
            ),
        ],
        realm="",
        status="Rumoured",
        known="",
    )
    return island, villa, venice, cave


def _people(b: Builder) -> None:
    fortunata = b.magus(
        "Fortunata of Jerbiton",
        covenant=None,
        house=JERBITON,
        age=None,
        summary=paragraphs(
            "Lived 986 to about 1123. Daughter of a prince of Milan, she was "
            "taken as apprentice around 996 by Apollo of Jerbiton, who saw "
            "her Gentle Gift. Her childhood name is lost; she took the name "
            "Fortunata at her Gauntlet. She became a fine scholar and made "
            "her parens proud, but envied the potent specialised magic of "
            "others and came to want it more than the learning of her House.",
            "As a young maga of the Rome Tribunal she travelled the old "
            "Roman and Greek ruins around the Mediterranean. She freed a "
            "spirit, Lucida, from a witch's binding in a cleft stone, and "
            "they became friends, travelling companions, and in time maga "
            "and familiar; some said lovers.",
            "She pursued the rites of lost cults. Her sudden power led "
            "rivals to accuse her of dealing with demons and of spying "
            "through spirits. The charges dogged her, and her secrecy did "
            "not help, so in later years she quit her covenant for a hidden "
            "island, keeping a house in Venice for the Redcaps. Those who met "
            "her reported shimmering clouds of spirits around her.",
            "She translated dead languages by having ancient ghosts read "
            "texts aloud while Mentem magic let her understand them, and many "
            "of her Latin versions spread through the Order, with notes in "
            "the margins that leave a reader wanting the rest. She was last "
            "met in 1123.",
        ),
        secrets=[
            titled(
                "No demons, no spying",
                "She dealt with no demons: she mastered Self-Initiation, "
                "turning quests into power with no cult to obey, and named the "
                "system Principles Lore (p. 47). She was careful of the "
                "Quaesitores and did not use her spirits to spy.",
            ),
            titled(
                "Fortunata's fate",
                "She probably died or entered Final Twilight soon after 1123; "
                "the chapter's heading says Final Twilight, its text that her "
                "fate is not recorded. Her island and library wait to be "
                "opened.",
            ),
            titled(
                "Where her rites came from",
                "She claimed to have found her rites in the ancients, yet many "
                "are Hermetic Virtues and there was no Hermetic magic before "
                "Bonisagus. She may have been deluded, may have lied, or may "
                "have had a knack for scripts that closely paralleled ancient "
                "Virtues (p. 47).",
            ),
            titled(
                "How Fortunata translated",
                "She never learned the ancient tongues, only called spirits "
                "until one could read the text (p. 68).",
            ),
            *REMEMBERED,
            titled(
                "Storyguide Notes",
                paragraphs(
                    "The book leaves open where her rites came from.",
                    REMEMBERED_NOTES,
                ),
            ),
        ],
    )
    fortunata.background.year_born = 986
    b.magus(
        "Cupressa of Algiers",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary=(
            "Long dead. A witch banished from Algiers for her dark practices, "
            "who left carrying her beast-son Monocaudus and cursed the city "
            "with seven years of failed harvests. By black arts she bound "
            "the spirit Lucida and took an island in the Mediterranean, where "
            "she raised her son. She died of old age."
        ),
        secrets=[
            titled(
                "Cupressa's heirs",
                "Her tradition still reveres her (p. 57).",
            ),
            titled(
                "How Cupressa died",
                "Monocaudus's tale that Fortunata slew her is false (p. 64).",
            ),
            titled(
                "The father of Cupressa's son",
                "The father of her son was Omaion the Serpent.",
            ),
            titled(
                "Storyguide Notes",
                "Her tradition resembles the Witches of Thessaly (Realms of "
                "Power: The Infernal p. 140).",
            ),
        ],
    )
    b.magus(
        "Omaion the Serpent",
        covenant=None,
        house="",
        age=None,
        type="mythic companion",
        summary=(
            "A great magical snake some 30 feet long, with penetrating "
            "venom and leathery skin that turns any weapon, who can also "
            "walk as a beautiful, lithe and seductive man. He may wander far "
            "from his cave in that shape."
        ),
        secrets=[
            titled(
                "Father of Monocaudus",
                "The father of Monocaudus, whom legend does not name (p. 58).",
            ),
            titled("Omaion and the Order", "He has hardly met a magus."),
            titled(
                "Omaion the Infernal",
                "Legends differ. Omaion the Infernal: a demon in the shape of a "
                "jet-skinned handsome man, in a fortified mansion in the old "
                "quarter of Algiers among beautiful servants and apparent "
                "wealth, Monocaudus's beast form then being Infernal and "
                "Magical blood mixed in flesh.",
            ),
            titled(
                "Omaion the Sorcerer",
                "Legends differ. Omaion the Sorcerer: one of the darker fae of "
                "Greece, brooding in dark forest glades, with a dragon's head "
                "and tail, a lion's chest, a man's arms and a goat's nether "
                "parts; to imply his origin is such a mixture of myths risks "
                "instant wrath.",
            ),
            titled(
                "Storyguide Notes",
                "The book gives him no stat block. See the story A Vengeful "
                "Father. A saga may choose another version of him.",
            ),
        ],
    )
    b.magus(
        "Lucio",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "The ghost of an elderly servant in an old Venetian house, who "
            "stayed faithful long after his mistress disappeared, until a "
            "gruesome plague killed him around 1130. He means no harm, and "
            "talks in an old Venetian dialect to anyone who can see him and "
            "does not run: of old Venice, of the maga who came to work on "
            "her books and letters, and of how he died."
        ),
        secrets=[
            titled(
                "What Lucio knows",
                "He knows that Fortunata hid papers behind wall panels and "
                "under floorboards (p. 56).",
            ),
            titled("Storyguide Notes", "The book gives him no stat block."),
        ],
    )
    b.magus(
        "Chrétien the Roamer",
        covenant=None,
        house="",
        age=None,
        type="companion",
        summary=(
            "A disreputable-looking monk, tall and forever tousled, who has "
            "wandered much of Europe, the southern Mediterranean coasts and "
            "England above all. A great storyteller, he has somehow survived "
            "many disasters and seen many wonders, and tells them for ale."
        ),
        secrets=[
            titled(
                "What Chrétien knows",
                "He knows much Church Lore, Dominion Lore, Magic Lore and Area "
                "Lore of England and the Mediterranean.",
            ),
            titled(
                "Storyguide Notes",
                "His lore should serve the story and not be a guide to "
                "everything (p. 57). The book gives no scores.",
            ),
        ],
    )
    b.magus(
        "Federo of Bonisagus",
        covenant=None,
        house=BONISAGUS,
        age=None,
        summary=(
            "An elderly magus who has studied Fortunata's life and gathered "
            "a great deal about her. He is sure she was a witch of Thessaly, "
            "sodalis, rival and at last victor over Cupressa of Algiers, and "
            "he has plans for expeditions to Algiers, Thessaly and various "
            "Mediterranean islands."
        ),
        secrets=[
            titled(
                "Federo's false lore",
                "Much of what he has is distorted, and the witches have fed him "
                "false information (p. 57).",
            ),
        ],
    )
    b.magus(
        "Pullatus of Flambeau",
        covenant=None,
        house=FLAMBEAU,
        age=None,
        summary=(
            "A magus obsessed with Viea, Trianoma's sister, and with dragons. "
            "He believes Viea founded a lineage of her own on knowledge stolen "
            "from Bonisagus, and that the sisters dealt with dragons. His "
            "research into her ideas and magics keeps him at his laboratory, "
            "so he looks for others to go in his stead."
        ),
        secrets=[
            titled(
                "Pullatus's theory",
                "He takes Cupressa's son for a half-dragon, and Cupressa and "
                "Viea for one woman, which would make the island the home of a "
                "near-Founder (pp. 57-58).",
            ),
            titled(
                "Storyguide Notes",
                "The book says nothing to support this. Viea's story is in "
                "Houses of Hermes: True Lineages p. 6.",
            ),
        ],
    )


def _spirits(b: Builder, island: Neighbour, villa: Neighbour) -> None:
    b.creature(
        "Tempestas",
        page="pp. 58-60",
        realm="Magic",
        might=35,
        form="Auram",
        season="Summer",
        size=0,
        cunning=True,
        place=island,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(1, 3, 0, -2, 3, 2, -2, 2),
            "virtues_flaws": [
                "Magic Spirit",
                *["Improved Characteristics"] * 2,
                "Keen Vision",
                "Fury",
                ("Greater Power", {"power": "Raise the Tempest"}),
                ("Focus Power", {"focus": "Crafter of Weather"}),
                *["Improved Might"] * 15,
                ("Improved Powers", {"detail": "reduce Might cost"}),
                *["Slow Power"] * 2,
            ],
            "abilities": [
                ("Awareness", 5, "searching"),
                ("Concentration", 5, "maintain powers"),
                (SEA_LORE, 3, "waters"),
            ],
            "traits": {"Stormy": 3},
        },
        powers=[
            b.power(
                "Crafter of Weather",
                1,
                -3,
                "Auram",
                level=25,
                does="Focus Power, 1-5 points: any non-Ritual weather effect "
                "up to level 25, at 1 Might per spell magnitude. A Slow Power, "
                "taking an extra round to prepare.",
            ),
            b.power(
                "Raise the Tempest",
                0,
                -6,
                "Auram",
                rtd=("Sight", "Concentration", "Group"),
                level=50,
                does="CrAu 50 (base 5, +3 Sight, +1 Concentration, +2 Group, "
                "+3 Size), Greater Power, -5 Might from Improved Powers. A "
                "hurricane ten miles across, like Wrath of Whirling Winds and "
                "Water, which builds over several minutes and dies soon after "
                "the power ends.",
            ),
        ],
        vis=[BodyVis(4, "Auram", "in storm spume")],
        appearance=(
            "To ordinary sight, only a great storm. Second Sight shows a huge "
            "disembodied blue head with bulging cheeks, ever blowing. The head "
            "is the size of a man; its Size does not count the storm."
        ),
        notes=paragraphs(
            "Spirit of storms and the island's outer guard. When a ship or "
            "swimmer comes near it raises a storm that drives off or wrecks "
            "any vessel not protected by powerful magic, so those who expect "
            "a quiet anchorage are likely to land on the shore separately, "
            "with little gear (pp. 59-60).",
            "Many of its weather effects are indirect, like capsizing a boat, "
            "but Tempest has Penetration 35, enough for direct effects such "
            "as lightning or rain to reach even magi.",
        ),
        secrets=[
            titled(
                "Where Tempestas is bound",
                "Bound as guardian by Spell Binding in a carved agate head in "
                "the library (pp. 59-60).",
            ),
            titled(
                "Storyguide Notes",
                "See the island's secrets for how the binding is built and broken.",
            ),
        ],
    )
    b.creature(
        "Lucida",
        page="pp. 60-61",
        realm="Magic",
        might=25,
        form="Mentem",
        season="Summer",
        size=0,
        confidence=(1, 3),
        place=villa,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(2, 2, 3, 0, -1, 1, 1, 3),
            "virtues_flaws": [
                "Magic Spirit",
                "Second Sight",
                ("Dutybound", {"detail": "Fortunata's memory"}),
                ("Focus Power", {"focus": "Ghost Touch"}),
                ("Focus Power", {"focus": "Crafter of Illusion"}),
                ("Greater Power", {"power": "Control Human"}),
                ("Greater Power", {"power": "Greater Eidolon"}),
                ("Greater Power", {"power": "Command Spirit"}),
                *[("Personal Power", {"power": "Travel"})] * 2,
                *["Improved Abilities"] * 4,
                *["Improved Characteristics"] * 4,
            ],
            "abilities": [
                ("Awareness", 3, "alertness"),
                ("Bargain", 3, "favors"),
                ("Concentration", 4, "maintain powers"),
                ("Faerie Lore", 1, "glamor"),
                ("Folk Ken", 1, "spirits"),
                (GREEK, 3, "old dialects"),
                ("Guile", 2, "lie to authority"),
                ("Intrigue", 2, "scheming"),
                (ISLAND_LORE, 4, "inhabitants"),
                (ITALIAN, 3, "old dialects"),
                (LATIN, 5, "hermetic use"),
                ("Leadership", 1, "grogs"),
                ("Magic Lore", 3, "spirits"),
                ("Magic Theory", 4, "help in lab"),
                (SEA_LORE, 1, "geography"),
                (ORDER_LORE, 2, "past magi"),
                ("Second Sight", 4, "spirits"),
            ],
            "traits": {"Airy": 3, "Brave": 2, "Grieving": 2},
        },
        powers=[
            b.power(
                "Command Spirit",
                0,
                0,
                "Mentem",
                rtd=("Voice", "Moon", "Individual"),
                level=30,
                does="ReMe 30 (base 5, +2 Voice, +3 Moon), Greater Power, -3 "
                "Might cost. If it penetrates, a disembodied spirit carries "
                "out her commands as best it can. It may try to break free "
                "when asked for anything complex, dangerous or against its "
                "nature: Intelligence + a fitting Personality Trait against "
                "Ease Factor 14 (9 + magnitude of her Might).",
            ),
            b.power(
                "Control Human",
                1,
                -1,
                "Mentem",
                rtd=("Voice", "Concentration", "Individual"),
                level=35,
                does="ReMe 35 (base 20, +2 Voice, +1 Concentration), Greater "
                "Power, -3 Might cost. As Command Spirit, on a person, with "
                "the same chance to break free.",
            ),
            b.power(
                "Crafter of Illusion",
                1,
                -2,
                "Imaginem",
                level=25,
                does="Focus Power, 1-5 points: any Creo or Rego Imaginem spell "
                "up to level 25, at 1 Might per magnitude.",
            ),
            b.power(
                "Greater Eidolon",
                0,
                1,
                "Imaginem",
                rtd=("Sight", "Concentration", "Individual"),
                level=30,
                does="Cr(In)Im 30 (base 2, +3 Sight, +1 Concentration, +2 "
                "move at command, +1 intricacy, +1 Intellego requisite), "
                "Greater Power, -3 Might, +1 Init. An image she can see and "
                "hear through, anywhere she can see, moving and speaking as "
                "she directs even out of sight or after she Travels, until "
                "she has no more use for it: a youth in loose robes with "
                "short white hair and a high clear voice. In the villa it "
                "often appears inside a mirror.",
            ),
            b.power(
                "Ghost Touch",
                1,
                -2,
                "Terram",
                does="Focus Power, 1-5 points: moves objects not held or "
                "fastened down, up to 5 pounds for 1 Might and double for "
                "each further point, until released. She cannot use or throw "
                "them as weapons.",
            ),
            b.power(
                "Travel",
                1,
                0,
                "Mentem",
                rtd=("Special", "Momentary", "Individual"),
                level=35,
                does="ReMe 35 (base 15, +4 Special, as Arcane), Personal "
                "Power x2, -3 Might. Brings her to any place she can see, "
                "knows well or has an Arcane Connection to, much like a "
                "maga's ReCo travel spells.",
            ),
        ],
        vis=[BodyVis(5, "Mentem", "in reflections")],
        appearance=(
            "No mortal form, and seldom in one place, her attention spread "
            "across the island. In her actual presence Second Sight shows a "
            "figure much like her image, a robed youth. She discourages "
            "speculation about what lies under the robes, though her name "
            "is feminine in Latin."
        ),
        notes=paragraphs(
            "Chief spirit of the island, holding the others ready against "
            "the day her mistress returns. She still grieves, bound to the "
            "memory of the maga by her own will. Told of intruders, she "
            "turns the Imagines and the rest on them, to drive them mad or "
            "away (p. 67).",
            "She calls herself an Airy Spirit, but she is far too strong for "
            "those minor spirits. Magic Lore scholars might call her a ghost, "
            "or a faerie who has moved into the Magic Realm.",
            "A familiar's death note (p. 61): when a magus dies an ordinary "
            "animal familiar dies too, but immortal beings such as spirits "
            "are released and lose the Bond's powers.",
        ),
        secrets=[
            titled(
                "Lucida in the cleft",
                "Trapped by Cupressa and Monocaudus in the cleft of a huge "
                "boulder until Fortunata freed her and later came back to "
                "defeat and bind the beast.",
            ),
            titled(
                "What Lucida really is",
                "She may know what she really is and not be telling, or may "
                "truly have forgotten (p. 61).",
            ),
            titled(
                "The way into the laboratory",
                "Only she knows the way into the laboratory (p. 62).",
            ),
            titled(
                "Lucida and Monocaudus",
                "She cannot force Monocaudus to obey; she can only repeat the "
                "old binding words and promise Fortunata's punishments, which "
                "feeds his hatred (p. 63).",
            ),
        ],
    )
    b.creature(
        "Monocaudus",
        page="pp. 63-64",
        realm="Magic",
        might=25,
        form="Animal",
        size=2,
        confidence=(1, 3),
        place=villa,
        block={
            "characteristics": characteristics(0, 1, -1, 1, 6, 3, 2, 0),
            "virtues_flaws": [
                "Magic Animal",
                ("Large", {"detail": "human form, free"}),
                "Animal Ken",
                *["Improved Characteristics"] * 3,
                *["Improved Soak"] * 2,
                vf_puissant("Brawl"),
                "Sharp Ears",
                "Tough",
                "Wilderness Sense",
                "Magical Monster",
                "Monstrous Appearance",
                ("Plagued by Supernatural Entity", {"detail": "Lucida"}),
                ("Disfigured", {"detail": "tattooed all over"}),
                "Gift of Speech",
                ("Personal Power", {"power": "Human Form"}),
                *["Improved Abilities"] * 4,
                *["Improved Attack"] * 2,
                *["Improved Damage"] * 2,
                "Improved Defense",
                *["Improved Might"] * 5,
                ("Slow Power", {"power": "Human Form"}),
            ],
            "abilities": [
                ("Animal Ken", 4, "serpents"),
                ("Awareness", 1, "alertness"),
                ("Athletics", 4, "run"),
                ("Brawl", 5, "fist"),
                ("Carouse", 3, "drunken stories"),
                ("Chirurgy", 3, "crude tools"),
                ("Concentration", 2, "when scolded"),
                (GREEK, 4, "curses"),
                ("Guile", 5, "elaborate lies"),
                ("Intrigue", 2, "malicious schemes"),
                (ISLAND_LORE, 4, "history"),
                (ITALIAN, 2, "sailors"),
                (LATIN, 4, "orders"),
                ("Magic Lore", 1, "creatures"),
                (SEA_LORE, 1, "nearby islands"),
                ("Wilderness Sense", 4, "islands"),
            ],
            "traits": {"Monstrous": 3, "Resentful": 3, "Bitter": 2},
        },
        attacks=[
            b.attack("Dodge (Man)", 2, None, 9, None),
            b.attack("Fist (Man)", 2, 14, 12, 8),
            b.attack("Bite (Man)", 2, 9, 9, 2),
            b.attack("Dodge (Serpent)", 0, None, 7, None),
            b.attack("Fist (Serpent)", 0, 14, 10, 12),
            b.attack("Bite (Serpent)", 0, 9, 7, 6),
            b.attack("Constrict (Serpent)", 0, 12, 7, None),
        ],
        soak=10,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Human Form",
                1,
                -2,
                "Corpus",
                does="He may, and is usually forced to, take human form for a "
                "Sun or until he ends it. It loses the serpent's Size +2, Str "
                "+4 and Qik -2, and has the Large Virtue, Size +1 with no "
                "change to his Characteristics. A Slow Power.",
            ),
        ],
        vis=[BodyVis(5, "Animal", "in his tattoos")],
        appearance=(
            "In truth a great serpent with the arms, chest and head of a man, "
            "his skin not scaled but covered in tattoos."
        ),
        notes=paragraphs(
            "An ancient serpent and the household's resentful slave, kept to "
            "menial work and to human shape. He does the least he can, for "
            "fear she may yet come back, and curses her and Lucida to anyone "
            "who will listen, chiefly minor spirits who understand little of "
            "it.",
            "Printed Virtues also include Size +2 (free), named here only. He was "
            "built by the rules for Dragons as Characters (Realms of Power: "
            "Magic p. 74). The block lists Personal Power (Human Form) twice; "
            "it is entered once.",
            "Human form: Int 0, Per +1, Pre -1, Com +1, Str +2, Sta +3, Dex "
            "+2, Qik +2 (printed without a sign), Size +1. Wounds as a man: "
            "-1 (1-6), -3 (7-12), -5 (13-18), Incapacitated (19-24; printed "
            "19-14). As a serpent: -1 (1-7), -3 (8-14), -5 (15-21), "
            "Incapacitated (22-28).",
            "Human Form is an active power, so his man-form attacks must "
            "penetrate Magic Resistance. In his natural form they need not: a "
            "magus who has been shrugging off his fists may be surprised by "
            "the change. Constriction uses the grappling rules (ArM5 p. 174): "
            "while he holds a victim in his tail, the victim suffers "
            "Deprivation from lack of air, and he is free to strike or bite.",
            "With her memory faded he may briefly defy his commands, rebelling "
            "or taking his true shape, on Stamina + a fitting Personality "
            "Trait against Ease Factor 12.",
        ),
        secrets=[
            titled(
                "Monocaudus's parents",
                "Son of Cupressa and Omaion, and with his mother Lucida's tormentor.",
            ),
            titled(
                "How Monocaudus was bound",
                "Fortunata and Lucida hunted and bound him, a Quest of her "
                "Initiation of Spirit Familiar (pp. 52, 57).",
            ),
            titled(
                "Man or serpent",
                "Her summa calls him now human, now serpent, and the reading of "
                "his name is uncertain.",
            ),
            titled(
                "Monocaudus' Binding",
                "Monocaudus' Binding (p. 64): ReMe 55, Touch, Sun, Individual, "
                "Pen +32, constant (base 20, +1 Touch, +2 Sun, +4 levels constant, "
                "+16 levels Penetration). A tiny enchanted topaz embedded in his "
                "chest, which renews the effect if it is ever suppressed. He must "
                "obey Fortunata, her continuing commands, or any agent she "
                "deputised.",
            ),
            titled(
                "Ruling Monocaudus",
                "Guileful, he is very hard to convince of any new command's "
                "authority, even Lucida's. He talks himself out of his duties, "
                "and Fortunata had to chastise him even in her day. It may be "
                "possible, with difficulty, to pose as Fortunata well enough to "
                "rule him.",
            ),
            titled(
                "What Monocaudus blames",
                "He does not know what binds him and blames Lucida (p. 64).",
            ),
            titled(
                "Outside the laboratory",
                "He has never entered the laboratory (p. 62).",
            ),
        ],
    )
    b.creature(
        "Fax",
        page="pp. 66-67",
        realm="Magic",
        might=10,
        form="Ignem",
        season="Spring",
        size=-5,
        place=island,
        block={
            "characteristics": characteristics(-3, 0, 2, -2, -10, 1, 3, 8),
            "virtues_flaws": [
                "Magic Spirit",
                "Tough",
                "Proud (Minor)",
                ("Focus Power", {"focus": "Crafter of Ignem"}),
                *[
                    (
                        "Greater Power",
                        {
                            "power": "Arc of Fiery Ribbons, Continual Flame, "
                            "Donning the Corporeal Veil, Hurl Flame"
                        },
                    )
                ]
                * 2,
                "Improved Abilities",
                *["Improved Defense"] * 3,
                *["Improved Soak"] * 2,
                ("Personal Power", {"power": "Flight of the Hummingbird"}),
                *["Miniature"] * 2,
            ],
            "abilities": [
                ("Athletics", 3, "run"),
                ("Awareness", 3, "alertness"),
                ("Brawl", 4, "fist"),
                ("Concentration", 1, "maintain powers"),
                ("Finesse", 1, "Ignem"),
                (ISLAND_LORE, 2, "places"),
                (LATIN, 3, "fire"),
                ("Magic Lore", 1, "spirits"),
            ],
            "traits": {"Fiery": 3, "Proud": 3},
        },
        attacks=[
            b.attack("Dodge", 8, None, 14, None),
            b.attack("Fist of Flame", 8, 3, 8, 5),
        ],
        soak=8,
        fatigue_levels="OK, 0, -1, -3, -5, Unconscious",
        powers=[
            b.power(
                "Arc of Fiery Ribbons",
                1,
                5,
                "Ignem",
                rtd=("Voice", "Momentary", "Individual"),
                level=25,
                does="CrIg 25 (base 5, +2 Voice, +2 Group), Greater Power, -2 "
                "Might cost. As the spell: +10 damage to all in a 60-degree "
                "arc as far as her voice carries.",
            ),
            b.power(
                "Continual Flame",
                1,
                6,
                "Ignem",
                rtd=("Touch", "Moon", "Individual"),
                level=15,
                does="CrIg 15 (base 3, +1 Touch, +3 Moon), Greater Power, -1 "
                "Might cost. Leaves a flame, candle- to torch-sized, on "
                "anything she touches, which burns a month with no fuel.",
            ),
            b.power(
                "Crafter of Ignem",
                1,
                6,
                "Ignem",
                level=15,
                does="Focus Power, 1-3 points (15 levels, +1 add 5 to maximum "
                "level, +1 Init): any non-Ritual Creo or Rego Ignem spell up "
                "to level 15, at 1 Might per magnitude.",
            ),
            b.power(
                "Donning the Corporeal Veil",
                2,
                5,
                "Ignem",
                rtd=("Touch", "Sun", "Individual"),
                level=25,
                does="Cr(Re)Ig 25 (base 5, +1 Touch, +2 Sun, +1 requisite), "
                "Greater Power, -1 Might cost. Makes and animates a body of "
                "elemental fire until the duration ends or she dissolves it. "
                "Slain in it she is killed, leaving 2 small rubies holding "
                "vis; injured, she can dissolve it to escape death.",
            ),
            b.power(
                "Flight of the Hummingbird",
                0,
                7,
                "Ignem",
                rtd=("Personal", "Concentration", "Individual"),
                level=10,
                does="ReIg 10, Personal Power, -1 Might cost. She flies in any "
                "direction by concentrating, and if that lapses she stops but "
                "does not fall. The block's reckoning says base 4, +2 Sun, "
                "against a printed Duration of Concentration.",
            ),
            b.power(
                "Hurl Flame",
                0,
                7,
                "Ignem",
                rtd=("Voice", "Momentary", "Individual"),
                level=10,
                does="CrIg 10 (base 4, +2 Voice), Greater Power, -1 Might cost. "
                "A torch-sized flame from her tiny hands, +5 damage where it "
                "strikes.",
            ),
        ],
        vis=[BodyVis(2, "Ignem", "in her ruby eyes")],
        appearance="A tiny naked woman made of flame.",
        notes=paragraphs(
            "Spirit of the firebrand. By day she races about the island from "
            "bush tip to bush tip, never stopping to burn the wood; at night "
            "she may settle a while like a torch. She makes her fuelless "
            "flames when bored, and they last so long that many burn at any "
            "time in the interior and all through the villa. If commanded by "
            "Lucida, or if she remembers her charge, she harries and hurts "
            "intruders.",
            "Fist of Flame burns on contact, not by impact. Wounds: -1 (1), "
            "-3 (2), -5 (3), Incapacitated (4). Her block also prints wound "
            "penalties under Powers; the errata deletes them (p. 78).",
        ),
        secrets=[
            titled(
                "Where Fax is bound",
                "Bound to protect the island by Spell Binding in a large ruby "
                "hidden in the library (p. 66).",
            ),
        ],
    )
    b.creature(
        "Cantus",
        page="p. 67",
        realm="Magic",
        might=5,
        form="Imaginem",
        season="Spring",
        place=island,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(0, 3, -2, 4, -3, 1, 0, 2),
            "virtues_flaws": [
                "Magic Spirit",
                ("Greater Power", {"power": "Music of the Spheres"}),
            ],
            "abilities": [
                ("Awareness", 3, "alertness"),
                ("Finesse", 3, "illusion"),
                ("Music", 3, "illusion"),
                (ISLAND_LORE, 2, "inhabitants"),
                ("Magic Lore", 2, "spirits"),
            ],
            "traits": {"Guileful": 3},
        },
        powers=[
            b.power(
                "Music of the Spheres",
                0,
                1,
                "Imaginem",
                rtd=("Voice", "Concentration", "Group"),
                level=25,
                does="CrIm 25 (base 1, +2 Voice, +1 Concentration, +2 Group, "
                "+2 move at command, +1 intricacy), Greater Power, -3 Might, "
                "+2 Init. Music or simpler sounds, from one to ten voices. It "
                "favours bell chimes and plaintive melodies.",
            ),
        ],
        vis=[BodyVis(1, "Imaginem", "in a chime which falls to the ground")],
        appearance=(
            "Seen with Second Sight, a set of chime bells, or the instrument "
            "it is sounding. It always sounds sweet."
        ),
        notes=(
            "A spirit of song, one of the many Imagines of the island, who "
            "wanders free and is not bound. It may be one of the native "
            "sounds Fortunata mentions. The book prints no Size for it, so "
            "none is entered."
        ),
    )
    b.creature(
        "Mnemos",
        page="p. 68",
        realm="Magic",
        might=5,
        form="Mentem",
        season="Spring",
        size=0,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(2, 0, 1, 2, 0, 1, 0, -1),
            "virtues_flaws": [("Magic Spirit", {"detail": "spectre"})],
            "abilities": [
                ("Artes Liberales", 3, "grammar"),
                ("Concentration", 1, "reading"),
                ("Dead Language: Sumerian", 5, "scholarship"),
            ],
            "traits": {"Lost": 3},
        },
        appearance=(
            "A dark-skinned man with a shaved head and a long waxed chin-"
            "beard, in a linen skirt and the ghost of a gold collar."
        ),
        notes=(
            "An ancient ghost, dead since well before Christ, who recalls "
            "only a bright, hot sun and much sand. He speaks a tongue long "
            "forgotten, but could read in life and still can. He has no vis, "
            "and he has faded so far that he does not know why he stays on "
            "earth, and does not remember Fortunata."
        ),
        secrets=[
            titled(
                "Cantus in The Names of Ghosts",
                "One of the ghosts in The Names of Ghosts, where Fortunata "
                "annotated him 'Sumerian?'.",
            ),
            titled(
                "Cantus the reader",
                "Fortunata would call him, have him read scrolls aloud, and "
                "follow by Thoughts Within Babble, transcribing, or studying "
                "from his voice as from the text.",
            ),
            titled("Storyguide Notes", "The book prints no haunt for him."),
        ],
    )
    b.creature(
        "Error",
        page="p. 68",
        realm="Magic",
        might=5,
        form="Imaginem",
        season="Spring",
        size=0,
        place=island,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(1, 3, -3, 2, -2, 2, 0, 2),
            "virtues_flaws": [
                "Magic Spirit",
                "Second Sight",
                "Meddler (Minor)",
                ("Greater Power", {"power": "Image of the Beloved"}),
                ("Focus Power", {"focus": "Warper of Imaginem"}),
                ("Slow Power", {"power": "Image of the Beloved"}),
            ],
            "abilities": [
                ("Awareness", 2, "alertness"),
                ("Finesse", 3, "illusion"),
                ("Folk Ken", 1, "common folk"),
                ("Guile", 3, "illusion"),
                (ISLAND_LORE, 1, "inhabitants"),
                ("Magic Lore", 1, "spirits"),
                ("Second Sight", 3, "illusion"),
            ],
            "traits": {"Meddler": 3, "Guileful": 3},
        },
        powers=[
            b.power(
                "Image of the Beloved",
                1,
                -2,
                "Imaginem",
                rtd=("Voice", "Concentration", "Group"),
                level=35,
                does="Cr(In)Im(Me) 35 (base 2, +2 Voice, +1 Concentration, +2 "
                "Group, +2 move at command, +1 intricacy, +1 Intellego "
                "requisite; the Mentem requisite is free), Greater Power, -3 "
                "Might cost. Believable figures who deal with a victim and "
                "companions, guessing by magic what they should say: compare "
                "its Perception + Finesse with the victim's roll, usually "
                "Perception + Awareness, or another Ability fitting the "
                "figure. It must penetrate to take something familiar from a "
                "victim, and concentrates a round first, as a Slow Power.",
            ),
            b.power(
                "Warper of Imaginem",
                1,
                1,
                "Imaginem",
                level=5,
                does="Focus Power: any Muto or Rego Imaginem spell up to level "
                "5, for 1 Might.",
            ),
        ],
        vis=[BodyVis(1, "Imaginem", "in a shard of glass")],
        appearance=(
            "None of its own. Second Sight shows only whichever figures it "
            "is portraying."
        ),
        notes=paragraphs(
            "A spirit of recollection, also called Delusion, one of the "
            "Imagines of the island, free and unbound. Its figures talk and "
            "jest among themselves whether anyone is watching or not, and "
            "they are the spirit itself. It finds other people's memories a "
            "welcome change and pursues visitors with glee.",
            "If found at play it draws the newcomer in, shifting the scene to "
            "suit. Otherwise it makes figures from a victim's memories, which "
            "can be very plausible, such as fellow survivors of the wreck.",
            "The block says only Meddler; the catalog has it at both tiers, "
            "and Minor is entered, since one Flaw balances its one Minor "
            "Virtue.",
        ),
    )
    b.creature(
        "Lapidosus",
        page="p. 69",
        realm="Magic",
        might=10,
        form="Terram",
        season="Spring",
        size=0,
        place=island,
        tires=False,
        can_be_wounded=False,
        block={
            "characteristics": characteristics(0, 3, -3, -3, 4, 4, 0, 1),
            "virtues_flaws": [
                "Magic Spirit",
                ("Greater Power", {"power": "Sense the Feet That Tread the Earth"}),
                (
                    "Greater Power",
                    {
                        "power": "The Crystal Dart, The Earth's Carbuncle, Hands "
                        "of the Grasping Earth, Pit of the Gaping Earth"
                    },
                ),
                vf_great("Strength"),
                vf_great("Stamina"),
                *[("Improved Powers", {"detail": "reduced Might cost"})] * 2,
            ],
            "abilities": [
                ("Awareness", 4, "searching"),
                ("Finesse", 4, "Terram"),
                (ISLAND_LORE, 2, "geography"),
                ("Magic Lore", 1, "spirits"),
            ],
            "traits": {"Stony": 3},
        },
        powers=[
            b.power(
                "The Crystal Dart",
                0,
                1,
                "Terram",
                level=10,
                does="As the spell, Mu(Re)Te 10. Greater Power, -1 Might and "
                "+1 Init from Improved Powers.",
            ),
            b.power(
                "The Earth's Carbuncle",
                0,
                0,
                "Terram",
                level=15,
                does="As the spell, Re(Mu)Te 15. Greater Power, -2 Might and "
                "+1 Init from Improved Powers.",
            ),
            b.power(
                "Hands of the Grasping Earth",
                0,
                0,
                "Terram",
                level=15,
                does="As the spell, Re(Mu)Te 15. Greater Power, -2 Might and "
                "+1 Init from Improved Powers.",
            ),
            b.power(
                "Pit of the Gaping Earth",
                0,
                1,
                "Terram",
                rtd=("Touch", "", ""),
                level=10,
                does="As the spell, reduced to Range Touch, PeTe 10. Greater "
                "Power, -1 Might and +1 Init from Improved Powers.",
            ),
            b.power(
                "Sense the Feet That Tread the Earth",
                0,
                0,
                "Terram",
                rtd=("Touch", "Momentary", "Part"),
                level=25,
                does="InTe 25 (base 4, +1 Touch, +1 Part, +3 Size), Greater "
                "Power, -3 Might, +2 Init. By thought alone he feels what "
                "moves on the ground within a mile, enough for the whole "
                "island: direction, distance, weight, number and manner of "
                "movement.",
            ),
        ],
        vis=[BodyVis(2, "Terram", "in sharp flints")],
        appearance=(
            "Insubstantial, but seen as an ugly, wrinkled, twisted man with "
            "a huge head and hands and almost no body. His skin looks like "
            "old brown leather, and close up like the earth itself."
        ),
        notes=(
            "A spirit of stony ground, set to guard the island. He can pass "
            "through solid matter but always keeps to soil, stony soil most "
            "of all, and may notice and attack anyone crossing open ground "
            "who is not on solid rock. Years of quiet have made him slack, so "
            "intruders may go about for some while before he recalls his task."
        ),
        secrets=[
            titled(
                "Where Lapidosus is bound",
                "Bound by Spell Binding in a leaden plumb-weight hidden in the "
                "library (p. 69).",
            ),
        ],
    )


def _witches(b: Builder) -> Neighbour:
    return b.faction(
        "The Heirs of Cupressa",
        faction="Hedge coven",
        summary=(
            "Witches of Algiers and the lands around, who revere the great "
            "Cupressa and have slowly spread into southern Europe, gathering "
            "what they can through paid agents."
        ),
        wants="The treasures of Fortunata's island, which they hold were "
        "stolen from Cupressa and are rightly theirs.",
        secrets=[
            titled(
                "How the heirs of Cupressa work",
                "They have met Hermetic magi before and fear the Parma Magica "
                "and strong spells, so they work through mundane agents who "
                "know nothing of their purpose or origin (p. 57).",
            ),
            titled(
                "Storyguide Notes",
                "A tradition like the Witches of Thessaly (Realms of Power: The "
                "Infernal p. 140). The book gives no number, leader or block.",
            ),
        ],
    )


def _stories(
    b: Builder,
    island: Neighbour,
    villa: Neighbour,
    venice: Neighbour,
    cave: Neighbour,
    witches: Neighbour,
) -> None:
    S = b.stage
    threats = [
        b.threat(
            "Finding Fortune",
            place=island,
            summary=paragraphs(
                "A loose adventure played over several sessions and not in "
                "a straight line: the search for Fortunata's forgotten "
                "island, its guardians and her library (p. 55). It may open "
                "with her texts, found on a back shelf or in a treasure "
                "chest.",
                "Any of the story starters can open it, or lead the seekers "
                "on. Some give direct evidence, some cross paths with her "
                "history without warning.",
            ),
            secrets=[
                titled(
                    "The unmentioned guardians",
                    "Fortunata's writings never mention the guardians of her "
                    "island, so they come as a surprise (p. 59).",
                ),
                titled(
                    "Storyguide Notes",
                    "The treasures become a saga's own quests: the Initiations' "
                    "Quests are story seeds that take the others to the far "
                    "corners of Mythic Europe, in supporting or even opposing "
                    "roles (pp. 47-48).",
                ),
            ],
            antagonist="The island's guardians, and Lucida",
            stages=[
                S(
                    "The trail is found",
                    at=1,
                    clues="A text, a witness or a story crossing her history "
                    "tells the magi of Fortunata.",
                ),
                S(
                    "The search",
                    at=2,
                    clues="The island is hidden and largely forgotten. A "
                    "direct search will probably fail, but others can give "
                    "leads, sometimes unknowingly.",
                ),
                S(
                    "A tempestuous approach",
                    at=3,
                    clues="Near the island a magical storm raised by a guardian "
                    "spirit breaks the vessel and casts the party ashore, "
                    "scattered.",
                ),
                S(
                    "Beset on the island",
                    at=4,
                    clues="Strange spirits close in. The Parma Magica shields "
                    "magi from direct assault, though many spirits strike "
                    "indirectly, and grogs parted from their magi may be "
                    "driven mad.",
                ),
                S(
                    "The villa",
                    at=5,
                    clues="Some reach the mansion, apparently abandoned and "
                    "decayed. Only a careful search finds the library, the "
                    "laboratory and the treasure in them.",
                ),
            ],
        ),
        b.threat(
            "In a Locked Box",
            summary=paragraphs(
                "A locked metal box, marked by salt-water corrosion and "
                "tightly sealed, turns up among a treasure, in a corner of an "
                "old covenant's library, or with a merchant who could not get "
                "it open and now wants to sell it.",
                "Its lock is for show: only magic will open it.",
            ),
            secrets=[
                titled(
                    "What the box holds",
                    joined_lines(
                        "Inside the locked box (pp. 55-56):",
                        "- Principles for a Better Life, tractatus on Principles "
                        "Lore, Quality 11, Latin",
                        "- Heroes of Greece, tractatus on Area Lore: Ancient Greece, "
                        "Quality 6, Ancient Greek",
                        "- Heroes of Greece (revised), tractatus on Area Lore: "
                        "Ancient Greece, Quality 8, Latin, with added notes",
                        "- The Myth of Andros and the Tree, Initiation Script needing "
                        "a forgotten cult Lore, Script Bonus 12, Ancient Greek",
                        "- Andros And the Tree, Principles Lore Initiation Script "
                        "for Spirit Familiar, Script Bonus 12, Latin",
                    ),
                ),
                titled(
                    "Andros And the Tree",
                    "Andros And the Tree opens as a myth of an unnamed hero who "
                    "beats a monster and frees a maiden caught in a tree, with "
                    "notes on playing it out in earnest. Intelligence + Magic "
                    "Lore against 12, or + any Mystery Cult Lore against 6, "
                    "shows it for an Initiation Script.",
                ),
                titled(
                    "Principles for a Better Life",
                    "Principles for a Better Life reads as a set of good habits, "
                    "such as rising with the sun and washing in cold water, but "
                    "is really the Organization Lore of a cult with no members. "
                    "Its style shows the same hand as the translator of the "
                    "myth.",
                ),
                titled(
                    "Heroes of Greece",
                    "Heroes of Greece could pass for Magic or Faerie Lore, but "
                    "mostly describes land and people. The revised copy says "
                    "the author lived among the Greek islands, and a seeker "
                    "might find clues in its notes.",
                ),
                titled(
                    "Whose texts they are",
                    "All of the locked box's texts are Fortunata's.",
                ),
            ],
            antagonist="None; the box leads to Fortunata",
        ),
        b.threat(
            "A House in Venice",
            place=venice,
            summary=(
                "A character, or someone close to one, buys a cheap house in "
                "Venice that has stood empty for a while, and finds that "
                "earlier owners left in a hurry."
            ),
            secrets=[
                titled(
                    "Whose house it was",
                    "The house in Venice was Fortunata's, and Lucio still haunts it.",
                ),
                titled(
                    "Storyguide Notes",
                    "See the house's and Lucio's secrets for the rolls and for "
                    "the hidden papers, which point towards the cluster of "
                    "islands near hers (p. 56).",
                ),
            ],
            antagonist="None; a harmless ghost",
        ),
        b.threat(
            "Chrétien the Roamer",
            summary=(
                "Among his many disasters, the monk Chrétien tells of a tempest "
                "on a voyage out of Venice. He alone survived, cast on the "
                "sandy shore of a small island full of strange sights and "
                "sounds and airy spirits or ghosts. He lived on crabs and "
                "stream water until he had driftwood enough for a raft."
            ),
            secrets=[
                titled(
                    "Chrétien's voyage",
                    "Chrétien may recall enough of the ship's storm-driven "
                    "course to help magi find the island.",
                ),
                titled(
                    "Storyguide Notes",
                    "Adjust where he sailed to the saga's choice of location (p. 57).",
                ),
            ],
            antagonist="None; a witness",
        ),
        _witches_quests(b, witches),
        b.threat(
            "Fortunata the Thessalian?",
            summary=(
                "Federo of Bonisagus offers a junior magus a reward to follow "
                "his leads and prove that Fortunata was a witch of Thessaly, "
                "with expeditions to Algiers, Thessaly and the islands where "
                "he thinks she lived."
            ),
            secrets=[
                titled(
                    "Federo misled",
                    "The witches have misled Federo and his quests are "
                    "misguided, though following them may uncover real truths "
                    "(p. 57).",
                ),
            ],
            antagonist="The Heirs of Cupressa, through false information",
        ),
        b.threat(
            "Viea's Legacy",
            summary=(
                "Pullatus of Flambeau seeks magi to find the island where, he "
                "is sure, Viea lived as Cupressa and raised a half-dragon son. "
                "He offers spells for dealing with dragons, texts on Magic Lore "
                "(Dragons), and a book of Mediterranean Lore on the area to be "
                "searched."
            ),
            secrets=[
                titled(
                    "Trianoma and Viea",
                    "As told in Houses of Hermes: True Lineages p. 6, Trianoma "
                    "and her sister Viea, sorceresses of Thessaly, woke a dragon "
                    "that led them to Bonisagus's cave, and Viea quarrelled with "
                    "her sister and fled before the Order was founded (pp. "
                    "57-58).",
                ),
                titled(
                    "Storyguide Notes",
                    "Whether any of Pullatus's theory is true, the book does not say.",
                ),
            ],
            antagonist="None; a patron with a theory",
        ),
        b.threat(
            "A Vengeful Father",
            place=cave,
            summary=(
                "Legend tells of the witch, of her son and of the maga who beat "
                "them, but not of the father, who is alive and has never learned "
                "what happened to them."
            ),
            secrets=[
                titled(
                    "Who the father is",
                    "Omaion the Serpent. Anyone looking into Cupressa or "
                    "Fortunata may cross his path (p. 58).",
                ),
                titled(
                    "A war Omaion starts",
                    "A war Omaion starts falls on those who woke it, under the "
                    "Oath's clause on endangering the Order.",
                ),
            ],
            antagonist="Omaion the Serpent",
            stages=[
                S(
                    "Curious",
                    at=1,
                    clues="He is neutral at first, and curious if offered news "
                    "of Cupressa.",
                ),
                S(
                    "Furious",
                    at=2,
                    clues="He learns what befell her and his son.",
                    ignored="If careless, the characters become the first "
                    "target of his wrath; more likely he flies off after "
                    "Fortunata.",
                ),
                S(
                    "War on the Order",
                    at=3,
                    clues="He finds that Fortunata is beyond reach, but that she "
                    "stood for an Order of magi.",
                    ignored="He blames the whole Order and begins a war against magi.",
                ),
                S(
                    "Before the Tribunal",
                    at=4,
                    clues="The characters face their sodales, under the Oath's "
                    "clause against endangering the Order by their actions.",
                ),
            ],
        ),
        b.threat(
            "Monocaudus's Incitements",
            place=villa,
            summary=(
                "On the island a monstrous servant pours out a tale of "
                "wrongs: the spirit Lucida is a usurper and a jailer, and "
                "visitors could right it by standing with him and setting him "
                "free."
            ),
            secrets=[
                titled(
                    "Monocaudus's false tales",
                    "Monocaudus's stories contradict one another but circle a "
                    "few themes: that Lucida has imprisoned the other spirits "
                    "and misuses the mistress's books, and that cruel Fortunata "
                    "fought and killed his kindly mother. All false.",
                ),
                titled(
                    "Lucida's scolding",
                    "Lucida's scolding may seem to bear Monocaudus out, but he "
                    "has earned most of it and overstates the rest (p. 64).",
                ),
            ],
            antagonist="Monocaudus",
        ),
    ]
    for threat in threats:
        dormant(threat)


def _witches_quests(b: Builder, witches: Neighbour) -> Neighbour:
    return b.threat(
        "The Witches' Quests",
        summary=(
            "Strangers with money approach companions and grogs, buying what "
            "they know or hiring them to learn more, about an island no one "
            "has heard of."
        ),
        secrets=[
            titled(
                "The witches' agents",
                "The heirs of Cupressa seek the island through agents (p. 57).",
            ),
            titled(
                "The witches' plan",
                "The heirs of Cupressa may feed characters information so that "
                "they find the island and are first through its defences, then "
                "follow and attack them while they are weak. Or, guarding their "
                "search, they may spread false tales that send others on false "
                "quests.",
            ),
            titled("Storyguide Notes", f"See {witches.name}."),
        ],
        antagonist=witches.name,
    )
