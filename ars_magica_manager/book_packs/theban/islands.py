"""The Islands, the Theban Tribunal's sea, as of 1220: the North Aegean
(Lesbos, Lemnos and their neighbours), Delos where the Tribunal meets,
the Cyclades of the Duchy of Naxos, the Dodecanese and Rodos, and
Venetian Candia; the covenants of Aegaea and Ingasia (of the Aegean
phyle) and Favonius and Polyaigos (of the Kretan phyle) with their magi,
patrons, libraries and vis; Orphykia and Zacharias; Memnos's shipyard
on Andros; Marcus Tauros at Knossos; and the lords, churches, towns and
pirates of the islands, in paraphrase of The Sundered Eagle chapter six
(with chapter three for Delos's part in the meeting and each covenant's
politics, and chapter five for Negroponte).

Creatures (the Hyperborean nymphs of Delos, Talos, the vrykolakes, the
stringles, Typhon) are the Bestiary's or the realms' and are only named
in the summaries of the places they haunt. Patrons are described in
their covenant's notes. Tokens, shards and phylai are tribunal.py's.

Keys: the region is places["islands"]; Delos is places["delos"]; the
covenant sites are places["aegaea_palace"], ["favonius_fleet"],
["mosychlos"] and ["polyaigos"]; Memnos's shipyard is
places["memnos_shipyard"] and Orphykia places["orphykia"]; the
covenants are covenants["aegaea"], ["favonius"], ["ingasia"] and
["polyaigos"]; the magi are under their first names (magi["lucian"],
magi["memnos"], magi["stouritus"], magi["maria_laskarina"],
magi["zacharias"], magi["marcus_tauros"] and the rest)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, paragraphs
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Neighbour, Tribunal
    from . import Theban

BJORNAER = "house_bjornaer"
BONISAGUS = "house_bonisagus"
CRIAMON = "house_criamon"
EX_MISC = "house_ex_miscellanea"
FLAMBEAU = "house_flambeau"
GUERNICUS = "house_guernicus"
JERBITON = "house_jerbiton"
MERINITA = "house_merinita"
VERDITIUS = "house_verditius"

#: The lead line of a covenant's notes, before its secrets.
KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(theban: Theban, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = theban.b.place(name, **kw)
    theban.places[key] = place
    return place


def build(theban: Theban) -> None:
    b = theban.b
    tribunal = theban.tribunal
    assert tribunal is not None
    _region(theban)
    _north(theban)
    _delos(theban)
    _cyclades(theban)
    _dodecanese(theban)
    _candia(theban)
    _aegaea(theban, b, tribunal)
    _favonius(theban, b, tribunal)
    _ingasia(theban, b, tribunal)
    _polyaigos(theban, b, tribunal)
    _loose_magi(theban, b)
    _lords(theban, b)
    _churches(theban, b)
    _towns(theban, b)
    _factions(theban, b)


# ------------------------------------------------------------- the region


def _region(theban: Theban) -> None:
    _add(
        theban,
        "islands",
        "The Islands",
        summary=paragraphs(
            "The Aegean, the sea of the Greek heroes' voyages, and its "
            "hundreds of islands, from bare rocks to lands of hundreds of "
            "square miles: the Archipelago, as it was called of old and "
            "still is. It is named for Aegeus, the Athenian king who drowned "
            "himself when his son Theseus forgot the white sail of victory, "
            "and also for Aegaea, Poseidon's palace under its waters; the "
            "Bulgarians, comparing it with the stormy Black Sea, call it the "
            "White Sea. Many islands are green, with vines, orchards, olives "
            "and grain, goats and sheep on the heights; the small ones are "
            "mostly barren. Some are volcanic, others rich in marble, stone "
            "or ore. Windmills, learned from the Muslims during the "
            "crusades, grind the corn in the steady winds. Every town that "
            "matters is a port, and none is a great city.",
            "After 1204 the islands were shared, on parchment, between "
            "Venice and the Latin Empire, but real control varies and has "
            "shifted for fifteen years; local despots and even pirates rule "
            "some. Venice took the key harbours: Candia, Rodos, Karpathos and "
            "the Cyclades, and in the north only Lemnos, Ingasia's island, "
            "which makes some magi suspect House Verditius of a secret "
            "bargain with the old doge, or of helping the crusade.",
            "Piracy is ancient here and has hardly changed: booty, and "
            "captives held for ransom. Dionysos himself was once seized by "
            "Tyrrhenian pirates, and turned their oars to snakes and the men "
            "to dolphins. On the poorer islets raiding is a way of life with "
            "no shame in it, though every lord hangs pirates when he can. "
            "The empire's collapse has swelled their numbers, and some pirate "
            "chiefs now rule ports, checked only by the crusaders and the "
            "Venetian fleet; some Venetian captains will deal with pirates "
            "who prey on their rivals. The Tribunal forbids covenants to "
            "attack one another's ships, but not to rob mundanes, though that "
            "is frowned on.",
            "The islands have always been places of exile: early Christians "
            "under Rome, then pagans, heretics, criminals and traitors under "
            "the Byzantines, and wicked hedge wizards with the beasts and "
            "demons they called up, many of them bound by the old Byzantine "
            "magicians. Since Constantinople fell those old bindings have "
            "been failing, and many of the menaces are loose again. Covens "
            "of stringles infest several small isles (see the realms), and "
            "islanders bury the cursed on bare islets so they cannot rise as "
            "vrykolakes.",
            "Vis of the islands, each described in its place: the stone "
            "roots of Lesbos's Petrified Forest (Perdo), Ikaria's healing "
            "springs (Creo), the bows of Delos's nymphs (Rego, see the "
            "Bestiary), the springs of Naxos, the mane of Keos's stone lion "
            "(Rego), Thera's pumice (Perdo), the echo in St John's cave on "
            "Patmos (Intellego), the old wreath of the Tree of Hippocrates "
            "on Kos (8 Creo), the Colossus's bronze shards on Rodos (Ignem), "
            "the acorns of Mount Zeus's oak (Vim) and Talos's ichor on "
            "Candia (7 Ignem). The book does not say which of them are the "
            "polity's common sources.",
            "Of the Tribunal's phylai, the Aegean takes in the northern "
            "islands with Aegaea and Ingasia; the Kretan takes in Candia, the "
            "Cyclades and the Dodecanese, with Favonius and Polyaigos.",
        ),
        **KNOWN_ORDER,
    )
    _add(
        theban,
        "islets_of_the_dead",
        "The burial islets",
        inside=theban.places["islands"],
        realm="Infernal",
        summary=paragraphs(
            "Small empty islets off the settled islands where wise "
            "islanders bury those cursed or wicked in life, so they will not "
            "come back as vrykolakes (see the Bestiary). Many hold tumbledown "
            "graveyards with an Infernal aura (the book gives no strength) "
            "and are plagued by the vampires, whom the sea usually keeps "
            "from the inhabited shores.",
        ),
        **KNOWN_REGION,
    )


# ------------------------------------------------------ the North Aegean


def _north(theban: Theban) -> None:
    region = theban.places["islands"]
    _add(
        theban,
        "north_aegean",
        "The North Aegean",
        inside=region,
        summary=paragraphs(
            "The northern half of the Archipelago. Its western waters have "
            "few large islands save the Sporades, wooded and farmed; to the "
            "east a chain of bigger islands follows the Asian shore, all "
            "nominally the Latin Empire's except Venetian Lemnos. Among the "
            "beings met here are the Gorgona (see Greece) and the magi of "
            "Aegaea with their tritones. In size after Lesbos come Khios, "
            "Lemnos, Samos, Thasos, Imbros, Ikaria and Samothraki.",
        ),
        **KNOWN_TRIBUNAL,
    )
    north = theban.places["north_aegean"]
    lesbos = _add(
        theban,
        "lesbos",
        "Lesbos",
        inside=north,
        summary=paragraphs(
            "The third island of Greece in size, after Candia and Euboea: "
            "green and pleasant, full of gardens and flowers, with two great "
            "inlets, two mountains and several hot springs. It is famed for "
            "minstrels, poets and lovers, and here, unusually, women stand "
            "above men. Five of its old towns, Mytilene, Mithymna, Issa, "
            "Antissa and Avrisi, bear the names of the daughters of King "
            "Makaras, son of Helios, who each ruled one, and the island's "
            "women have ruled ever since; it took its name from Lesbos, one "
            "of his sons-in-law. Cybele was worshipped here of old, and her "
            "male devotees unmanned themselves and lived as women.",
            "Sappho, the poetess of the sixth century BC, was born here; "
            "the ancients called her the tenth Muse, but she wrote in "
            "obscure Aeolic and Byzantine scholars now neglect her. Her "
            "spirit still walks the gardens, inspiring poets and lovers, and "
            "would suit a covenant here as patron. Aristotle wrote his "
            "History of Animals and four related works on the island; Rome "
            "and Byzantium neglected it and used it for exiles, Empress "
            "Irene of Athens among them in 802.",
            "A native who keeps Lesbos's ways abroad, the domineering woman "
            "or the meek man, should take Social Handicap; Enchanting Music "
            "and Free Expression are common.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "orphykia",
        "Orphykia",
        inside=lesbos,
        aura=4,
        summary=paragraphs(
            "The sacred grove of Orpheus on the westernmost shore of Lesbos, "
            "near Antissa. When the maenads tore the singer apart, his head "
            "and lyre were carried by a river to the sea and washed up here; "
            "the islanders buried the head with honour in the middle of a "
            "rich shrine, and Terpander of Antissa, the great minstrel who "
            "made the seven-stringed lyre, took the lyre for himself. Now it "
            "is an idyllic garden with a Magic aura of 4, where the "
            "nightingales sing better than anywhere known, and Sappho's "
            "spirit often lingers.",
            "It is holy to the Cult of Orpheus (Houses of Hermes: "
            "Societates), and a lone magus of that tradition, Zacharias of "
            "House Ex Miscellanea, keeps it.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "petrified_forest",
        "The Petrified Forest of Lesbos",
        inside=lesbos,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "A desolate vale in western Lesbos where a forest has turned to "
            "stone: trunks of all sizes stand upright, and a few of the stone "
            "pillars look much like cursed woodcutters. A spiteful band of "
            "kalotyches, the tree spirits who avenge a felling (see the "
            "Faerie landscape), lives here, and the place, with its Faerie "
            "aura of 3, is dreaded across the island.",
            "Vis: the stone roots of the trees can be cut as Perdo vis, "
            "which angers the spirits. For fear of sharing the woodcutters' "
            "fate the islanders honour their trees and never fell them, one "
            "reason Lesbos has so many tended gardens and groves.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "khios",
        "Khios",
        inside=north,
        summary=paragraphs(
            "A dry, mountainous island, with vines in its best corners and "
            "the mastic bush, a prized spice that yields a chewing gum and "
            "grows nowhere else. Its black medicinal wine, first grown by "
            "King Oenopion, a son of Dionysos, is among the Tribunal's best. "
            "Nea Moni, the 'new monastery' founded by Constantine IX, is one "
            "of the largest religious houses of the old empire.",
        ),
        **KNOWN_REGION,
    )
    lemnos = _add(
        theban,
        "lemnos",
        "Lemnos",
        inside=north,
        summary=paragraphs(
            "A fertile volcanic island of grain, olives and sheep, shaped "
            "like an upturned U round a deep bay on its southern side. Most "
            "of it is flat fields, gentle pastures and olive groves, with "
            "sandy beaches and well-peopled ports; the largest towns are "
            "Myrina on the west coast and Hephaistia on the north-east. The "
            "north-western corner is rockier, with the two highest peaks, "
            "Mount Vigla and the volcano Mosychlos, home of Ingasia and one "
            "of the Forges of Hephaistos, a cult site of House Verditius.",
            "Venice has held it since 1204 and has taken the island's "
            "products for itself, above all the Lemnian Earth (Lemnia "
            "Sphragis), a reddish clay dug near Hephaistia and used to stop "
            "bleeding and treat snakebite, which once enriched Ingasia.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "mosychlos",
        "Mount Mosychlos and the Forge of Hephaistos",
        inside=lemnos,
        aura=4,
        summary=paragraphs(
            "The active volcano of Lemnos, quiet for centuries, and the seat "
            "of Ingasia. Stone houses dot its slopes; a large stone hall is "
            "both the covenant's meeting room and the mouth of a labyrinth "
            "that runs all through the mountain, with hidden tunnels and "
            "secret caverns the present magi have never fully explored. At "
            "its heart, close to the molten core, is the Forge of Hephaistos, "
            "the centre of a Magic aura of 4, now a shared Hermetic "
            "laboratory that gives +8 to Rego and +5 to making enchanted "
            "items.",
            "The volcano's genius loci, Mosychlos, is the covenant's patron. "
            "His temper can shake the ground and bring down tunnels, or send "
            "lava into the passages nearest the core; the magi's devices "
            "hold back the magma and prop the tunnels while they stay in "
            "place.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "samos",
        "Samos",
        inside=north,
        summary=paragraphs(
            "A green island thick with vineyards and olive groves, where "
            "Hera was born; the ruins of her great temple, the Heraion, stand "
            "here. The Tunnel of Eupalinos, an ancient aqueduct cut "
            "wonderfully straight for over a thousand yards under a mountain, "
            "was built with the help of Pythagoras, a Samian.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "thasos",
        "Thasos",
        inside=north,
        summary="Four miles off the Macedonian shore, an island rich in "
        "mines of silver, gold and lead, and in marble quarries.",
        **KNOWN_REGION,
    )
    _add(
        theban,
        "imbros",
        "The stable of Pegasus off Imbros",
        inside=north,
        summary=(
            "Rumour has it that a great sea cave just off Imbros, near the "
            "narrow mouth of the Sea of Marmara, is where Pegasus, "
            "Poseidon's winged son, is stabled."
        ),
        **RUMOURED,
    )
    _add(
        theban,
        "ikaria",
        "The healing springs of Ikaria",
        inside=north,
        summary=(
            "Ikaria is named for Icarus, who fell when the sun melted his "
            "wax wings. Its famous springs cure barrenness, and Creo vis may "
            "be gathered there."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "samothraki",
        "Samothraki",
        inside=north,
        summary=paragraphs(
            "A mountainous granite island with no natural harbour, home "
            "of the half-ruined Sanctuary of the Great Gods, centre in "
            "antiquity of a mystery cult as popular as the more secretive "
            "Eleusinian one (see Greece). A sunken city lies off the "
            "east coast; the sponge-divers knew it well and dived there "
            "until a monster guarding it ate one who went too near.",
        ),
        secrets="The islanders notice occasional visitors who are always "
        "dripping wet, and suspect they come from the drowned city.",
        **KNOWN_LOCALLY,
    )


# ------------------------------------------------------------------ Delos


def _delos(theban: Theban) -> None:
    cyclades = _add(
        theban,
        "cyclades",
        "The Cyclades",
        inside=theban.places["islands"],
        summary=paragraphs(
            "The Encircling Isles, several dozen islands in the middle of "
            "the Aegean south-east of Attica and Euboea, said to have been "
            "spun round Delos, birthplace of Apollon and Artemis. Cypresses "
            "sacred to Artemis grow everywhere, and since they are trees of "
            "Hades and resurrection too they cluster by graveyards. In the "
            "middle of every village stands an old plane tree, carefully "
            "kept: a kalotyche lives in it and blesses the village with "
            "sweet vines, herbs and flowers as long as no one harms it. The "
            "northerly Etesian winds that cool the summers were Zeus's gift "
            "after sacrifices on Keos.",
            "The islands now make up the Duchy of Naxos. In size after "
            "Naxos come Andros, Paros, Melos, Keos, Ios, Thermia and "
            "Mykonos; Thera lies at the southern end, and Polyaigos off "
            "Melos.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "delos",
        "Delos",
        inside=cyclades,
        aura=3,
        detail=FULL,
        summary=paragraphs(
            "A small barren island, a mile or two across, once the seat "
            "of the Delian League and now forgotten: no people, nothing "
            "to take, no strategic worth. That is why so few mortals "
            "have noticed that it has torn free of the sea bed and "
            "floats wherever the Aegean and Kretan currents take it. The "
            "Theban Tribunal has met here since it began; Thebes and "
            "other sites were proposed, each by a faction seeking "
            "advantage, and Delos won for its history, its empty "
            "shores and its aura. It belongs, in name, to the Duchy of "
            "Naxos.",
            "Its legend. The titaness Asteria, sister of Leto and "
            "mother of Hekate, fled Zeus's advances as a quail and fell "
            "into the sea as a floating island (hence its old names "
            "Asteria and Ortygia, from ortyx, quail). When Hera swore "
            "that the pregnant Leto would find rest on neither land nor "
            "sea, the drifting island was neither, and Leto bore Apollon "
            "and Artemis there; in thanks she pinned it to the sea floor "
            "with four great columns, and Zeus decreed that no one "
            "should be born or die on it again. Only the priests of "
            "Artemis, Apollon, Leto and Dionysos lived here, with three "
            "nymphs Apollon brought from Hyperborea; predators were "
            "banned to protect the sacred quail, still plentiful. The "
            "League kept its treasury at Apollon's temple, and markets "
            "for goods and slaves flourished, but with no food, timber "
            "or much water the island emptied, and it has been "
            "deserted for at least a thousand years. Some time between "
            "eight and twelve centuries ago it began to float again; "
            "Hermetic study suggests Leto's binding weakened, but the "
            "titans' magic is little understood.",
            "Its aura. Magic outweighs Faerie, since Asteria was of "
            "Magic: the whole island has a Magic aura of 3, rising to 8 "
            "in places such as the sacred lake, and there are Faerie "
            "auras or regiones at the abandoned shrines of Apollon (the "
            "book gives no strengths). The aura is aligned to "
            "restlessness: anyone ashore gains Restless +1 (+2 where "
            "the aura is above 3), magi included. Quail, hares and "
            "lizards never stop moving, plants sprout, fruit and wither "
            "regardless of season, and visitors never want to stay; "
            "magi at a meeting pace about or slip out of the agora, and "
            "leave quickly once it ends.",
            "Its wanderings. Delos follows the currents, south in "
            "summer and east-north-east in winter, turning clockwise "
            "through the Cyclades within roughly the bounds of "
            "Astipalaia, Thera, Melos and Andros, and comes back to its "
            "old berth between Mykonos and Syros every 19 years. "
            "Redcaps crossing the Cyclades watch for it, so the "
            "Tribunal can chart it roughly.",
            "The Hyperborean nymphs. Arge, Opis and Loxo, embodiments "
            "of archery (distance, aim and flight), came with Apollon "
            "and Artemis and still guard the shrines (see the "
            "Bestiary). Disturbing a structure or relic calls them out, "
            "and vandals have moments to explain before the arrows fly; "
            "the wounded do not die until they have left the island. Two "
            "more sisters, Hyperoche and Laodice, brought sacred "
            "offerings from Hyperborea and vanished on the way home; "
            "the three long for news of them. They speak Hyperborean, "
            "and seekers of Hyperborean magic (Ancient Magic) may find "
            "answers in Apollon's temple or from them, if they prove "
            "worthy.",
            "The Tribunal's customs here. Zeus's ban on birth and death "
            "is thought to hold still: it is generations since anyone "
            "tried to kill here, and every magus present stopped it, "
            "fearing Olympian wrath. So no pregnant woman or beast may "
            "come to a meeting, and every predator is barred, familiars "
            "and companions included; Bjornaer with predatory "
            "heartbeasts avoid taking that shape here.",
            "The agora. The meetings are held in the Delian League's old "
            "assembly place, a natural bowl lined with marble steps and ringed "
            "with carved marble pillars.",
            "The four phyle houses. At a distance from the agora stand the "
            "walls of four large buildings and several huts; before each "
            "meeting they are roofed and mended, and each phyle shares one of "
            "the four with its staff. Tables, chairs and bedding must all be "
            "brought from elsewhere. On Mount Kynthos, at the island's centre, "
            "among the ruins of the Sanctuary of the Foreign Gods (shrines to "
            "Egyptian and eastern deities raised by foreign visitors), a few "
            "houses lodge the metoikoi.",
            "The treasury. On the very spot of the Delian League's treasury, a "
            "little temple-like building, empty above but for a great leaden "
            "trapdoor in the floor, copied from the trapdoor of "
            "Bonisagus's tower at Durenmar, never breached and opened only by a big "
            "iron key the archon keeps (a ceremonial charge, as the vault is "
            "seldom opened between meetings except in emergency). Stairs go "
            "down to dusty chambers far underground, where several hundred "
            "pawns of vis and many old items and texts are stored and "
            "catalogued; so much vis together makes spontaneous magical "
            "effects common. The nymphs guard it as they guard every sacred "
            "site here. The tamias draws the next seven years' vis from it at "
            "each meeting.",
            "The sacred lake. Its shore, with a Magic aura of 8, is where the "
            "Ceremony of Propitiation is held after the Rite of Dismissal: "
            "each covenant has raised a plinth at the water's edge, holding or "
            "awaiting an Arcane Connection to its patron (or the patron "
            "itself). The archon opens the rite with an old Ritual from a "
            "Casting Tablet, paid with eight pawns of Creo or Vim vis from the "
            "Tribunal, which wakes the lake's power; each covenant then tells "
            "its patron's deeds, renews its dedication and casts an offering, "
            "mostly vis, into the water. The League Against Idolatry boycotts "
            "it.",
            "Preparing a meeting. The phyle whose turn it is readies the site, "
            "and the work falls to its youngest magi: food for sixty magi and "
            "their servants for a week, and seven years of decay, since "
            "everything perishable rots fast here; repairs anger the nymphs, "
            "who hate any change to the island. Magical beasts drawn by the "
            "aura on its wanderings are often stranded on it, and must be "
            "driven off, not killed, and kept from the agora by wards, which "
            "the phyle teaches its young magi or lends them on Casting "
            "Tablets.",
        ),
        secrets="The vault is less safe than it looks: a clever magus could "
        "rob it, or a dishonest arche skim from it, without great "
        "difficulty. No one thinks it has ever happened, and it would "
        "be judged a grave crime.",
        **KNOWN_ORDER,
    )


# --------------------------------------------------------- the Cyclades


def _cyclades(theban: Theban) -> None:
    cyclades = theban.places["cyclades"]
    naxos = _add(
        theban,
        "naxos",
        "The island of Naxos",
        inside=cyclades,
        summary=paragraphs(
            "The largest and most fertile of the Cyclades, in their middle, "
            "and the duke's seat: Marco Sanudo has just finished his strong "
            "fortress, the Kastro, and is starting a cathedral. On Mount "
            "Zas, the highest peak of the islands, a huge cave like a "
            "cathedral was sacred to Dionysos, who wed Ariadne there after "
            "Theseus left her on the island.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "naxos_springs",
        "The springs of Krini and Karava",
        inside=naxos,
        realm="Faerie",
        summary=paragraphs(
            "Two rival springs in the north-east of Naxos. The spring of "
            "Krini at Apeiranthos has a shape-changing stoicheion (see "
            "the Faerie landscape); that of nearby Karava always appears "
            "as a white cat. Karava is the stronger faerie, Krini the "
            "more versatile.",
            "Vis: the springs yield vis to those their guardians allow "
            "(the book names neither Art nor amount).",
        ),
        secrets="When anyone takes an interest in the springs, Krini turns "
        "into a white cat, passes itself off as Karava, and grants "
        "leave to take vis from Karava's spring.",
        **KNOWN_LOCALLY,
    )
    andros = _add(
        theban,
        "andros",
        "The island of Andros",
        inside=cyclades,
        summary=(
            "The other great port of the Cyclades, famous for its "
            "shipwrights, and the home port of the ship-borne covenant of "
            "Favonius, whose founder Memnos keeps his shipyard here."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "memnos_shipyard",
        "Memnos's shipyard",
        inside=andros,
        summary=paragraphs(
            "The island workshop of Memnos of Verditius, builder of the "
            "Favonius fleet, on the Andros shore: where the felled oak "
            "forest of the spirit Dryops was brought, where each sanctum "
            "ship was laid down, and where a fifth and last magical ship "
            "for the covenant is now on the stocks. His laboratory here "
            "has many specialisations and improvements, and four "
            "forge-companions work with him. He rarely lacks a "
            "commission for a sea-going vessel.",
            "The fifth ship is to carry three laboratories, and the "
            "book offers it as a home for a troupe's magi.",
        ),
        secrets="Memnos never sails: a Death Prophecy says he will die with "
        "the sky above him and the sea below.",
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "paros",
        "The quarries of Paros",
        inside=cyclades,
        summary=(
            "The source of translucent white Parian marble, cut in "
            "antiquity by tens of thousands of slaves; the quarries are now "
            "mostly idle."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "melos",
        "Melos",
        inside=cyclades,
        summary=(
            "With Thera, one of the two volcanic Cyclades: fertile, rich in "
            "obsidian, and full of hot springs, odd caves and striking "
            "pillars of rock. Polyaigos, three miles off, buys most of its "
            "everyday goods here, and several of its covenfolk keep wives "
            "and families on the island."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "keos",
        "Keos and Leon Petrino",
        inside=cyclades,
        summary=paragraphs(
            "An island of sweet black wine and many springs, whose nymphs "
            "were driven out long ago by a huge lion, Leon Petrino, which "
            "seems carved from the mountainside and comes to life to defend "
            "Keos. Vis: whoever beats it may cut stones from its mane as "
            "Rego vis.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "ios",
        "Ios",
        inside=cyclades,
        summary=(
            "Where Homer is buried: an island under thick oak forest, the "
            "best ship timber in the Archipelago."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "vryokastro",
        "Vryokastro on Thermia",
        inside=cyclades,
        realm="Infernal",
        summary=paragraphs(
            "Thermia, named for its hot springs, is barren; on it lies "
            "Vryokastro, a ruined town of huge stones raised by the drakoi "
            "(see the Faerie landscape), now haunted by more vrykolakes than "
            "anywhere else in Greece (see the Bestiary). They lived on Hydra "
            "in the Saronic Gulf until a bishop banished them here. They "
            "pass as men among the islanders; once a year those of the "
            "nearby isles gather on Thermia and show their true shapes to "
            "one another, before the dupes they lured along. Most of those "
            "are eaten; a few are left mad and let go, to keep Thermia in "
            "terror.",
            "A blight on a whole island like this might draw the magi of "
            "the Donatores Requietis Aeternae (Houses of Hermes: "
            "Societates). The book gives no aura.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "mykonos",
        "Mykonos",
        inside=cyclades,
        realm="Infernal",
        summary=paragraphs(
            "An island strewn with great boulders, said to be giants turned "
            "to stone by Herakles. Several covens of stringles infest it "
            "(see the realms), and it is thought the capital of their "
            "'kingdom'. Stringles elsewhere in Greece are said to summon a "
            "Mykonian demon to help them, at the price of an infant "
            "tithed to the witches of Mykonos each year.",
        ),
        **RUMOURED,
    )
    _add(
        theban,
        "thera_bay",
        "The Bay of Thera",
        inside=cyclades,
        aura=7,
        summary=paragraphs(
            "Thera, the southernmost of the Cyclades, newly called "
            "Santorini (St Irene) by the Latins, is a crescent of rock "
            "round a lagoon that would be a vast harbour but for its "
            "sheer black cliffs; a few hamlets perch on top. The still "
            "blue bay, several miles across and entered by two wide "
            "channels, is fathomless save at its centre, where a "
            "volcano's peak smoulders just under the surface. It was "
            "land until the last battle of titans and Olympians blew it "
            "apart, more than a thousand years before Christ, sending a "
            "wave to wreck the coasts of the Cyclades and Candia (see the "
            "Magical landscape). Zeus cast Typhon of the hundred serpent "
            "heads into Tartaros, and he lies imprisoned in the volcano, "
            "now and then belching a whirl of dust and fire that sweeps "
            "the whole Aegean. The lagoon has a Magic aura of 7.",
            "Vis: the burning pumice the cloud scatters is Perdo vis.",
            "Outside the bay the Thalassomachos, the Warrior of the Sea "
            "(see the Faerie landscape), haunts the waters, stealing "
            "fishermen's nets and raising contrary winds; he never "
            "enters the bay, and if he suddenly flees Thera, a great "
            "storm from Typhon may be coming.",
        ),
        secrets="The Seekers of the Fallen believe that clearing the mouth of "
        "the sunken volcano would open a way into Tartaros, part of the "
        "Magic Realm.",
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------ the Dodecanese


def _dodecanese(theban: Theban) -> None:
    dodecanese = _add(
        theban,
        "dodecanese",
        "The Dodecanese",
        inside=theban.places["islands"],
        summary=paragraphs(
            "Some two dozen islands in the south-east of the Aegean, the "
            "edge of the Greek world in antiquity. Christianity rooted here "
            "before anywhere else in the Tribunal, through the missions of "
            "St Paul and St John; Muslim rulers left their mark on some "
            "islands, but Byzantium's is stronger and newer, in forts, "
            "monasteries and churches everywhere. Save Rodos, Karpathos and "
            "their neighbours, claimed by Venice, the Dodecanese are the "
            "Latin Empire's, though the nearest Asian shores are split "
            "between Nicaea and the Seljuks.",
        ),
        **KNOWN_TRIBUNAL,
    )
    patmos = _add(
        theban,
        "patmos",
        "Patmos",
        inside=dodecanese,
        realm="Divine",
        summary=paragraphs(
            "A little island at the north of the Dodecanese, the holiest in "
            "Greece: St John the Apostle was exiled here, fresh from Nero's "
            "persecutions, and a baptismal font marks where he came ashore. "
            "Save the monastery of St John the Divine, it is empty of "
            "people, but crowded with pilgrims. The book gives no aura.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "cave_apocalypse",
        "The Cave of the Apocalypse",
        inside=patmos,
        realm="Divine",
        summary=paragraphs(
            "A small cave high on Patmos's tallest peak, where St John "
            "received the visions of the Revelation, written down by his "
            "disciple Prochorus. Pilgrims see the stone he slept on, the "
            "cross he cut in the rock and the triple cleft through which he "
            "heard Christ's voice. Some monks of the monastery claim visions "
            "of their own here. The book gives no aura.",
            "Vis: a visiting Criamon magus once caught the murmuring echo "
            "from the cleft in a velvet bag, and it proved to be Intellego "
            "vis.",
        ),
        **KNOWN_LOCALLY,
    )
    kos = _add(
        theban,
        "kos",
        "The island of Kos",
        inside=dodecanese,
        realm="Divine",
        summary=paragraphs(
            "In antiquity one of the richest ports, famed for wine, an ally "
            "of Egypt and favourite of its kings (Ptolemy II was born here); "
            "under Byzantium still a busy harbour with rich farms. In the "
            "war of titans and gods, Poseidon broke off part of Kos and "
            "threw it at the titan Polybotes, who lies pinned beneath it: "
            "the islet of Nisyros, just south. A Divine aura covers the "
            "town (the book gives no strength).",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "tree_of_hippocrates",
        "The Tree of Hippocrates",
        inside=kos,
        aura=4,
        summary=paragraphs(
            "An ancient plane tree in the middle of Kos town, the oldest "
            "and biggest in the Tribunal. Settlers from Epidauros set "
            "up an asklepieion on Kos, and there Hippocrates, a native, "
            "learnt healing from Asklepios and taught it in the tree's "
            "shade; later St Paul preached under it. Each autumn the "
            "women of Kos weave a wreath of its leaves, which is blessed "
            "and hung among the church's icons, and carry the last "
            "year's wreath in procession to the shore and throw it into "
            "the sea; returning, they hug the tree, which grants them "
            "long years and strength. The tree has a Magic aura of 4 "
            "inside the town's Divine aura.",
            "Vis: the old wreath holds 8 pawns of Creo vis.",
        ),
        secrets="A magus usually waits unobtrusively in a boat to fish the "
        "wreath out of the sea.",
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "nisyros",
        "Nisyros",
        inside=dodecanese,
        aura=3,
        summary=(
            "The islet south of Kos that Poseidon tore from it and hurled "
            "at the titan Polybotes, who is trapped under it still. It has "
            "a Magic aura of 3."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "rodos",
        "The island of Rodos",
        inside=dodecanese,
        summary=paragraphs(
            "The largest of the Dodecanese, named for the nymph Rhode, "
            "daughter of Aphrodite and consort of Helios; both were its "
            "protectors, and her gift, the pink hibiscus called rhoda, "
            "blooms on every shore. The Colossus, a giant Helios astride "
            "the harbour mouth and one of the Seven Wonders, stood less "
            "than a century before an earthquake broke it at the knees; "
            "the bronze lay for centuries until the Saracens broke it up "
            "in the seventh century and sold it to a mysterious Jewish "
            "merchant from the Holy Land, who took it away on a thousand "
            "camels.",
            "Vis: small bronze shards of the Colossus can still be found, "
            "and are Ignem vis; perhaps the merchant knew it.",
            "The Saracens walled the city and split it into quarters, "
            "one still largely Jewish, with another for its rulers. The "
            "First Crusade gave it back to Byzantium; Richard the "
            "Lionheart took it in 1191 and enlisted its sailors; Venice, "
            "whose fleet has kept a base here since 1082, claimed it "
            "after 1204. Leo Gavalas, a rich and corrupt dynatos of "
            "Constantinople, now rules it as self-proclaimed despot. "
            "Fearing that free reading breeds rebellion, he seized every "
            "book on the island; only works he approves, which flatter "
            "him, may be sold.",
        ),
        secrets="The despot's closest adviser is a hedge wizard of foul "
        "character, very likely Infernal, who bends him to his own "
        "ends; he wrote the only books left on the island, tainted "
        "works including a corrupted Bible, and is greedily hoarding "
        "the island's vis while his demon master watches, pleased. "
        "Rumours of depravity and sorcery on Rodos may lead the "
        "Tribunal to ask for volunteers to look into it (The Despot's "
        "Advisor).",
        **KNOWN_REGION,
    )


# ---------------------------------------------------------------- Candia


def _candia(theban: Theban) -> None:
    candia = _add(
        theban,
        "candia",
        "Candia",
        inside=theban.places["islands"],
        summary=paragraphs(
            "Creta in Latin: the largest island of Greece and second of the "
            "eastern Mediterranean after Cyprus, the Tribunal's southern "
            "edge, some two hundred miles north of Africa. Mountains and "
            "rock cover most of it; their streams water the greener plains "
            "and plateaus with their olive groves, and sheep and goats "
            "graze the hills.",
            "Minos, son of Zeus and Europa and after death a judge of the "
            "dead, founded its ancient kingdom. His grandson Idomeneus, a "
            "leader at Troy, vowed Poseidon the first living thing he met "
            "on coming home if the god saved his ship, met his own son, "
            "killed him, and brought a curse on himself and the island.",
            "Rome, Byzantium and the Saracens held it in turn until "
            "Nikephoros II won it back in the tenth century. After 1204 it "
            "fell to Boniface of Montferrat, who sold it to Venice for 1000 "
            "marks; the Genoese pirate Enrico Pescatore held it for years "
            "until Venice made good its claim in 1212 and set up the "
            "Kingdom of Candia. Venetian families have been settled on it "
            "since, under four successive dukes of two years each, and the "
            "Greeks seethe at the ports' new taxes and tolls.",
            "Talos, the bronze guardian of Candia, walks again (see the "
            "Bestiary): bound for centuries in a cellar of Knossos by the "
            "Byzantines, he was freed when the old spell failed, circles "
            "the island three times a day hurling rocks at hostile ships, "
            "and grips any who land in a red-hot embrace. Vis: drained, his "
            "ichor is 7 pawns of Ignem vis. He has become a scourge of "
            "Venetian shipping, and the island's rulers offer a fine "
            "reward for this 'demon'; House Verditius would want to know "
            "what he really is, and he might make a covenant's patron.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "mount_zeus",
        "Mount Zeus",
        inside=candia,
        summary=paragraphs(
            "The mountain behind Chandax: from the sea it shows the huge "
            "profile of Zeus's face turned to the sky, though Christian "
            "Cretans prefer to see God's. Candia is Zeus's island, where he "
            "was born and raised, and the old belief is that he is born "
            "anew each year in his cave on Ida, grows up, and dies each "
            "winter here. Vis: the acorns of the mountain's single oak are "
            "a strong source of Vim vis.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "cave_of_zeus",
        "The Cave of Zeus on Mount Ida",
        inside=candia,
        realm="Faerie",
        aura=8,
        summary=paragraphs(
            "Somewhere on the slopes of Mount Ida, Candia's highest peak, "
            "the mountain of the Mother Goddess, is the cave where Rhea hid "
            "the newborn Zeus from Kronos and three nymphs raised him, "
            "beating spears on shields to drown his cries. It has a Faerie "
            "aura of 8. A golden dog guards it, and the great eagles that "
            "gave Zeus his thunder patrol the heights. Lucian the Scholar "
            "of Aegaea claims to have met the nymphs and the infant god on "
            "his travels here.",
        ),
        **RUMOURED,
    )
    _add(
        theban,
        "knossos",
        "The Labyrinth of Knossos",
        inside=candia,
        aura=3,
        levels=[
            Builder.level(
                "The intact labyrinth",
                6,
                "Faerie",
                notes=(
                    "The highest level of a regio in the ruins, where the "
                    "palace stands whole; bull and labrys emblems are "
                    "everywhere inside, and the old tales (Glaukos raised "
                    "by Polyeidos's herb, Theseus and the Minotaur, Daidalos "
                    "and Icarus) may be played out again."
                ),
            )
        ],
        summary=paragraphs(
            "The ruins of Candia's ancient capital on a hillside near "
            "Chandax, setting of many legends. Poseidon gave Minos a "
            "splendid white bull for sacrifice; the king kept it, and "
            "the god made Queen Pasiphae desire it, so Daidalos built "
            "her a wooden cow, and she bore the bull-headed Minotaur. "
            "The bull ravaged the island until Herakles caught it in "
            "his seventh labour. Daidalos built the palace, a maze of "
            "more than a thousand rooms, to hide the Minotaur, and "
            "after Zeus helped Minos against Athens the city sent seven "
            "youths and seven maidens a year to feed it; prisoners "
            "were turned loose there too, freed if they found the way "
            "out. The double axe, the labrys that gave the labyrinth "
            "its name, was a sign of protection.",
            "The ruins have a Magic aura of 3 over a weaker Faerie one. "
            "Marcus Tauros of House Criamon, who has had visions of a "
            "past life as a Minoan priest, may be met here searching "
            "the catacombs beneath for what a magical bull cult of the "
            "Minoans knew.",
        ),
        secrets="Marcus has not yet found that the whole labyrinth survives "
        "inside a regio, whose highest level has a Faerie aura of 6. "
        "Talos was bound in one of the cellars until lately.",
        **KNOWN_LOCALLY,
    )
    gorge = _add(
        theban,
        "gorge_of_apollon",
        "The Gorge of Apollon",
        inside=candia,
        aura=2,
        summary=paragraphs(
            "The greatest gorge in Europe, over ten miles long, cut by a "
            "river from the White Mountains of western Candia; going "
            "through it, from over 4000 feet at the north end down to the "
            "southern shore, is a hard journey of two days or more along "
            "its walls and floor. A Magic aura of 2 runs its whole length. "
            "Caves and springs, homes of nereids, old cypresses and pines "
            "line the way, with healing mountain flowers: the peony, named "
            "for Paion, physician of the gods, who healed Hades and Ares "
            "with it; dittany, which wild ibex chew to heal their wounds; "
            "and the dark dragon arum, a poison to all but snakes, flower "
            "of Hades.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "keno",
        "Keno",
        inside=gorge,
        realm="Faerie",
        aura=4,
        summary=paragraphs(
            "Halfway down the gorge, where the cliffs tower a thousand feet "
            "but stand only a dozen apart, great bronze gates close the "
            "way. Beyond lies the hamlet of Keno, with a Faerie aura of 4, "
            "where an ancient Cretan people worship Apollon at a temple in "
            "its middle. They speak Classical Greek in a Doric dialect, are "
            "superb archers and hunters, and know almost nothing of the "
            "world. Apollon hid here from Zeus's anger after killing "
            "Python, Delphi's guardian, and fell in love with a local "
            "nymph and forgot to raise the sun on time; to this day the "
            "sun reaches the gorge's heart only at noon.",
        ),
        **RUMOURED,
    )


# ---------------------------------------------------------------- Aegaea


def _aegaea(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    p = theban.places
    p["aegaea_palace"] = b.place(
        "The Palace of Poseidon",
        inside=p["north_aegean"],
        realm="Faerie",
        levels=[
            Builder.level(
                "The palace and its gardens",
                8,
                "Faerie",
                enter="Through the sea, by the covenant's leave: Redcaps "
                "use Alexandria's glass submarine, or Aegaea's own "
                "devices, and call the covenant with its conch",
                notes=(
                    "The water of this level is airy: mortals breathe, ink "
                    "dries and fire burns, and one may walk or swim. It is "
                    "lit by constant sunshine, as if the surface were a few "
                    "dozen feet above, though it lies hundreds of feet down."
                ),
            )
        ],
        summary=paragraphs(
            "A Faerie regio on the floor of the Aegean, not far off the "
            "coast of Euboea, whose upper level (Faerie aura 8) holds what "
            "is taken for Poseidon's palace amid lavish gardens of sea "
            "flowers in countless colours and plants with sea-green, "
            "shimmering leaves. The palace is a sprawl of open courts, "
            "halls and towers, Greek in style but laid out more like a "
            "sultan's: white coral and shell lined with silver and gold, "
            "floors of a creamy, pearly stone set with gems. The magi have "
            "their sancta in some of its grandest rooms and towers. Honoured "
            "guests are received in the great central hall, an airy throne "
            "room of Doric columns, where Poseidon's throne stands empty at "
            "the far end.",
            "Tritones, mermen with green hair and eyes, attend the palace; "
            "a lovely nereid, half maiden and half fish (see the Faerie "
            "landscape), may be found resting here and there, and sea "
            "lions, dolphins, strange fish and sea serpents drift through "
            "unconcerned. Grand stables breed fine horses, every one with "
            "some faerie blood, which the covenant now and then gives to "
            "other magi; on land their nature can show in unexpected ways.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "One of the Tribunal's most splendid covenants, of the Aegean "
        "phyle, and one of its strangest and hardest to reach: a sanctuary "
        "under the sea in what is thought to be Poseidon's palace, devoted "
        "to keeping and studying the legends of the Tribunal, old and new. "
        "It is an Autumn covenant with strong magic at hand, but its magi "
        "are thought to wield little power beyond their sea floor, and many "
        "Theban magi wave it aside for its Faerie aura and the faerie "
        "leanings of most of its members.",
        "Orithyia of Merinita founded it about two centuries ago. By her "
        "own account (her lively books of fantastic journeys are half "
        "legend in the Tribunal), returning from Arcadia she was guided "
        "through the sea by a mighty golden man with a dolphin's tail, whom "
        "she took for Triton, Poseidon's herald, and made a pact with him "
        "to stay with her followers; the palace, she reasoned, could only "
        "be Homer's Aegaea, and she named the covenant for it. The "
        "Tribunal doubted her until Redcaps vouched for the place, and its "
        "splendour, and its patron.",
        "Ever since, Aegaea has been a little-understood, aloof presence, "
        "distrusted by many; hardly any magi but Redcaps have seen it, "
        "though most who have speak well of their welcome. Under Lucian it "
        "has earned a fair name as a fickle ally whose loyalties shift like "
        "the sea, though it has sometimes served the Tribunal by dealing "
        "with menaces under the waves. Lucian has gathered about half a "
        "dozen magi, mostly Merinita and Bjornaer, cast in his mind as "
        "members of Poseidon's court. Every magus needs some Aquam to come "
        "and go; non-Merinita who live long here, eating faerie food and "
        "using faerie materials, become heavily Warped.",
    )
    what_matters = _lines(
        "Boon: Powerful Ally (Triton, the covenant's patron)",
        "Boon: Regio (the palace, Faerie aura 8); Fantastic Environment (air-like water, constant sunlight); Inhuman Residents (the tritones and nereids); Wealth (faerie treasure, real only inside the regio)",
        "Hook: Faerie Aura; Hermetic Politics (Lucian's shifting alliances); Warping to a Pattern (non-Merinita are heavily Warped)",
        "Library: a surprisingly good one, excellent in Faerie Lore and Aquam, and a peerless collection of ancient Greek and Byzantine poetry",
        "Income: almost none needed; the tritones furnish food, furniture, tools and clothes, and only parchment, ink and some laboratory rarities come from outside",
        "Devices: items lent to visitors, such as a necklace that turns the wearer into a sea lion and a floating orb in a bubble of air; a magic conch on permanent loan to the Tribunal's Redcaps calls the covenant from up to a league away",
        "Turb: no human servants or grogs; an army of warrior tritones in need",
        "Horses: faerie-blooded horses bred in the palace stables, given as gifts",
        "Tension: blamed for every shipwreck, and thought treacherous; predictable only in defending Faerie sites and rebuking those who abuse them",
        "Tension: Lucian's Children of Olympos and his secret Mysteries",
        "Tension: it says loyalty to Triton, lord of the tritones, keeps it out of the battle for the Stone Ship of Corfu's vis (see Greece), and it enjoys coaxing other magi into trying",
    )
    patron = paragraphs(
        "The patron. Triton, son and herald of Poseidon, is perhaps the "
        "mightiest of the Tribunal's patrons, and unusually has a Faerie "
        "Might: a great golden-skinned merman with a trident and a conch "
        "trumpet that can calm the waves or rouse them. Sometimes he is at "
        "the palace, sometimes far off in the Aegean. A host of tritones "
        "(Realms of Power: Faerie) attends him, men above and dolphins "
        "below, their torsos mostly covered in small hard scales; the "
        "swiftest, the centaur-tritones, have a horse's forelegs in place "
        "of arms. They are his warriors, messengers and servants.",
        "Customs. Aegaea makes much of ceremony and of the old myths, "
        "Poseidon's above all. The few visitors are often cast in a role "
        "in some elaborate rite or re-enactment on arrival, and in an "
        "eccentric mood Lucian sets them a small quest before he will see "
        "them. Most Redcaps have cut these welcomes down to a bearable "
        "nuisance, but Lucian still names each of them after a child of "
        "Hermes (Pan, Tyche, Hermaphroditus, Rhodos and so on). Lucian "
        "writes to other covenants in the Theban way, in tales whose "
        "meaning must be read between the lines.",
        "Founded: the book says about two centuries ago; 1020 is assumed.",
    )
    hidden = _lines(
        "They probably could do real harm to other covenants' shipping if they ever cared to.",
        "Lucian is the only magus with an Olympian Pact; he is mystagogue of every member of his league who has Elysian Ecstasy, and may be channelling pretenders, faerie or infernal, rather than gods.",
        "Proximios means to have the nosy Delfini falsely accused of diabolism by the League of the Vigilant, and to set Celaenea of Hedyosmos against Lucian.",
    )
    aegaea = b.covenant(
        "Aegaea",
        tribunal=tribunal,
        founded=1020,
        place=p["aegaea_palace"],
        level=1,
        realm="Faerie",
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(patron),
        secrets=hidden,
        unnamed_magi=2,
        detail=FULL,
        season="Autumn",
    )
    theban.covenants["aegaea"] = aegaea
    b.book(
        aegaea,
        "The library of Aegaea",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. Built up over two centuries, it is "
            "strong in Faerie Lore and Aquam and holds an unrivalled "
            "collection of ancient Greek and Byzantine poetry; Orithyia's "
            "own colourful accounts of her travels are among the Tribunal's "
            "half-legendary texts."
        ),
    )
    m = theban.magi
    m["lucian"] = b.magus(
        "Lucian the Scholar",
        covenant=aegaea,
        house=MERINITA,
        age=112,
        summary=paragraphs(
            "Aegaea's unchallenged leader and the last filius of its "
            "founder Orithyia, looking sixty-five: a famous scholar of "
            "Byzantine and ancient Greek letters who can recite dozens "
            "of long poems by heart and studies the power of story and "
            "rhetoric. He is believed to know several Mysteries, among "
            "them the Folk Mystery of Story Magic. White-haired and "
            "kindly of face, he wears loud dark blue robes embroidered "
            "with scenes of Greek and Byzantine legend. Unlike most of "
            "his covenant he travels widely and cares little for the "
            "sea.",
            "He is an active politician with obscure, eccentric aims, "
            "liable to switch his support at once to any magus he sees "
            "acting heroically or in keeping with old stories and "
            "traditions, though Aegaea's name for treachery blunts his "
            "influence. He leads the Children of Olympos, who want the "
            "old Greek gods as the covenants' patrons, and coined the "
            "names of the three titan factions (the Seekers of the "
            "Fallen, the Legion of Atlas and Kampe's Lovers) in a "
            "mocking speech four Tribunals ago. He claims to have met "
            "the infant Zeus on Ida, and enjoyed young Proximios's "
            "acrobatics when the Redcap brought messages.",
            "His Twilight Scars are hidden: some mental flaws, above "
            "all lapses in which he forgets who he is and claims to be "
            "someone else, usually a hero of Greek legend.",
        ),
        secrets="He devised two Mysteries, Elysian Ecstasy and Olympian Pact, "
        "through which a person is possessed by a Greek god, and he "
        "alone holds an Olympian Pact. His changeable politics are a "
        "plan: he has cast the Tribunal's magi and covenants in roles "
        "in a grand re-enactment of the myths and steers them toward "
        "their parts, hoping Faerie will one day replace the Magic "
        "auras of the covenants. He may be duped by pretenders, faerie "
        "or infernal, and Proximios hopes to slip an infernalist into "
        "his league so that it raises a False God.",
        traits={"Scholarly": 4, "Whimsical": 3, "Treacherous": 2},
    )
    m["leukothea"] = b.magus(
        "Leukothea",
        covenant=aegaea,
        house=MERINITA,
        age=73,
        summary=paragraphs(
            "Charming and lovely, looking twenty-five and younger every "
            "year: born with the blood of the sea nereids, she has tail fins "
            "for feet and purple eyes, and her Twilight Scars are making "
            "her less human and more nereid. The latest has given her a "
            "crab's pincers at her temples, mostly hidden in her blue-green "
            "hair. Lucian hails this as a sign that she will become the "
            "faerie Amphitrite, Poseidon's bride, and urges her toward the "
            "Inner Mystery of Becoming; she is of two minds about it, but "
            "has begun wearing queenly white robes trimmed with gold. She "
            "often rides her dolphin familiar, Hippothoon, named for a "
            "mortal son of Poseidon.",
        ),
        traits={"Withdrawn": 3, "Tempestuous": 2, "Regal": 1},
    )
    m["delfini"] = b.magus(
        "Delfini",
        covenant=aegaea,
        house=BJORNAER,
        age=62,
        summary=paragraphs(
            "A plain, earnest woman who looks forty-three, whose "
            "heartbeast, as her name says, is a dolphin: she joined "
            "Aegaea for the water, not for any love of Faerie. Friendly "
            "and curious, she likes to swim beside ships carrying "
            "Redcaps to trade gossip (sailors think a dolphin alongside "
            "lucky). Most magi like her for her open ways, but some "
            "think her a busybody and distrust her.",
        ),
        secrets="Proximios has marked her as one of the innocents the League "
        "of the Vigilant is to be steered into accusing of diabolism.",
        traits={"Gregarious": 2, "Curious": 2, "Fierce": 1},
    )
    m["krum"] = b.magus(
        "Krum the Swift",
        covenant=aegaea,
        house=BJORNAER,
        age=57,
        summary=paragraphs(
            "A tall, athletic Bulgarian who looks forty, with a stallion "
            "heartbeast. As a young magus of Moero's Garden in "
            "Constantinople he loved racing in the Hippodrome. After the "
            "sack and that covenant's flight to Nicaea he met Lucian at the "
            "Tribunal of 1207, who filled his head with tales of Poseidon, "
            "maker of the horse and inventor of riding and racing, and Krum "
            "joined Aegaea on the spot, a sharp change of scene. He now "
            "means to grow his heartbeast into one of the golden-maned "
            "sea-horses that drew Poseidon's chariot.",
        ),
        traits={"Competitive": 3, "Naive": 2, "Changeable": 2},
    )


# -------------------------------------------------------------- Favonius


def _favonius(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    p = theban.places
    p["favonius_fleet"] = b.place(
        "The fleet of Favonius",
        inside=p["islands"],
        aura=2,
        levels=[
            Builder.level(
                "The sanctum ships' hidden laboratories",
                3,
                enter="By a secret way built into each sanctum ship",
                notes=(
                    "A regio exactly the size of each ship made of Dryops's "
                    "wood, holding the magi's laboratories."
                ),
            )
        ],
        summary=paragraphs(
            "Four round ships and a dozen or so lesser vessels, always on "
            "the move round the Aegean, with Andros as home port. The two "
            "sanctum ships built of Dryops's wood each carry a Magic aura "
            "and a regio of exactly the ship's size: the magi live on the "
            "mundane level, in a Magic aura of 2, and work in the regio "
            "above it, with a Magic aura of 3, reached by a secret way.",
            "The Philomela, Memnos's first, 72 feet long, holds two "
            "laboratories; her captain is Verecunda, and her timbers, "
            "enchanted to command the wind at the captain's will, set the "
            "fleet's pace and course. The Tereus, 18 feet longer, holds "
            "three, under Aeliophanes. The Procne, 60 feet long, is the "
            "covenant's main trader, an ordinary Aegean round ship with "
            "one deck almost all hold, under Basil of Andros. The Halcyon, "
            "115 feet by 40, little better than a barge and the clumsiest "
            "of them, is the magi's meeting place and the store for their "
            "costliest and most fragile goods; it sails in the middle of "
            "the fleet, its spells calming rough seas around it. Some of "
            "the other ships are Memnos's early work, with Sails and "
            "Rudders of Quality or small charms of speed and handling.",
            "Each main ship is a structure of Excellent Quality (City & "
            "Guild): +2 to navigation and ship-handling. The Tereus and the "
            "Halcyon are Size +9 with 16 damage levels; the Philomela is "
            "Size +8 and the Procne +7, with 12 each. All four are warded "
            "against fire and mend themselves by taking in new wood; they "
            "are bought with the Magical Fortress Boon, so their "
            "enchantments cost no covenant Build Points.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "An unusual covenant of the Kretan phyle: a flotilla of four main "
        "ships with a train of others, forever sailing the Aegean, the "
        "creation of Memnos, one of the best-known living Verditii, and "
        "kept moving by its thrill-hungry patron.",
        "Some fifty years ago, travelling in mainland Greece, Memnos met "
        "Dryops, a bored genius loci who longed to roam and see the world. "
        "Memnos offered it that in return for part of its power: he had "
        "its oak forest on a mountainside felled and carried to his "
        "workshop on Andros, the spirit with it, and after decades of "
        "planning began his great work, a ship of Dryops's wood which the "
        "spirit would inhabit and in which it would raise a Magic regio "
        "for a laboratory. While building it Memnos came to dread the sea, "
        "so his apprentice was the first captain. The Philomela sailed for "
        "many years, gathering ships for the covenant's companions and "
        "grogs; when the Procne joined her, the covenant took the name "
        "Favonius, for the kindly west wind. The Tereus and the Halcyon "
        "followed, and Memnos is building a fifth and final magical ship.",
        "It has five magi: Memnos, who stays ashore at his shipyard; his "
        "filia Verecunda, the real leader, on the Philomela; Aeliophanes "
        "on the Tereus; and one more on each of those ships, whom the book "
        "leaves to the storyguide (or the sancta may be empty, and with "
        "the fifth ship coming the covenant could be a home for a troupe's "
        "magi).",
    )
    what_matters = _lines(
        "Boon: Powerful Ally (Dryops, the covenant's patron)",
        "Boon: Magical Fortress (the four enchanted ships); Regio (a laboratory regio on each sanctum ship); Hunters or Sailors",
        "Hook: Constantly Mobile; Indebted (a great debt to Dryops)",
        "Income: trade by the Procne under Basil of Andros; a third of Peter Monocheiros's plunder",
        "Library: no books named",
        "Services: passage for other magi, sometimes for a shard neutralised for one of their members",
        "Expansion: a fifth sanctum ship of three laboratories is being built at Memnos's shipyard",
        "Tension: Basil wants profitable voyages; Verecunda and Dryops want adventures",
        "Tension: the patron's notion of excitement often puts the fleet in real danger",
    )
    patron = paragraphs(
        "The patron. Dryops was once a mere woodpecker spirit, one of the "
        "Fauni (Realms of Power: Magic), whose ambition and restlessness "
        "made it genius loci of a mountain wood; but as a bird it had "
        "roamed, and now it was fixed in place. Jumping at Memnos's plan, "
        "it gave up being a Daimon and genius loci by Transformation and "
        "became a wandering spirit again. Each use of its Regio power costs "
        "it 15 points of Might for good, which it bears gladly for the "
        "adventures it has as the fleet's spirit. To Second Sight it is a "
        "woodpecker as big as a goose, spotted black and white with a red "
        "face, usually perched in some ship's rigging.",
        "Customs. Favonius keeps off the main sea lanes to stay unseen, "
        "and has sailed to the Black Sea, Cyprus, Egypt and Sicily; the "
        "ships mostly keep together, while the small cogs scout ahead and "
        "watch shipping, warships above all. It will usually carry magi "
        "of other covenants, having seldom a destination of its own. The "
        "magi have sworn to find ways to give Dryops back its lost Might, "
        "which makes them slaves to its whims; it has recovered enough to "
        "agree to Memnos's fifth sanctum ship.",
        "Covenfolk. Drawn from all round the Mediterranean, they speak "
        "the Lingua Franca among themselves; their numbers change with the "
        "season, as some spend the winter at home on one island or "
        "another. The flotilla counts a dozen little cogs and scores of "
        "skiffs and rafts. Basil of Andros, the chief companion, a merchant-"
        "adventurer (City & Guild) on his way to his own trading house, "
        "keeps the supplies coming and quarrels hotly with Verecunda. Peter "
        "Monocheiros, 'One Hand', a pirate who owes Aeliophanes his life, "
        "owns two of the vessels and commands eight of the best fighters.",
        "Founded: the book gives no year, only that Memnos conceived the "
        "covenant about fifty years ago and spent decades on the first "
        "ship; 1190 is assumed for the Philomela's first voyage.",
    )
    hidden = _lines(
        "Peter Monocheiros pays the covenant a third of his plunder for its protection; Basil sells anything traceable in distant ports.",
        "Peter's crew wear masks at their 'work', and his ships are enchanted to change their look, so nothing can be traced to Favonius.",
    )
    favonius = b.covenant(
        "Favonius",
        tribunal=tribunal,
        founded=1190,
        place=p["favonius_fleet"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(patron),
        secrets=hidden,
        unnamed_magi=2,
        detail=FULL,
        season="Summer",
    )
    theban.covenants["favonius"] = favonius
    b.book(
        favonius,
        "The library of Favonius",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. Whatever the covenant keeps is "
            "stowed in the sancta of the Philomela and the Tereus, and its "
            "costliest and most delicate goods in the Halcyon's hold."
        ),
    )
    m = theban.magi
    m["memnos"] = b.magus(
        "Memnos",
        covenant=favonius,
        house=VERDITIUS,
        age=92,
        summary=paragraphs(
            "Founder of Favonius and designer of its wonderful ships, "
            "looking fifty-eight: a hale man, black-bearded and "
            "curly-haired, his skin browned by life on the shore and "
            "his body hugely muscled from heaving beams, a fine climber "
            "with sure balance. A lifelong lover of ships, he "
            "specialises in enchanting them and is famous as a builder "
            "of sea-going vessels, nearly always busy with a "
            "commission. He is best in Rego and in craft magic, which "
            "eases his labour; four forge-companions work with him, and "
            "his laboratory on Andros is richly specialised.",
            "He belongs to the Mystic Fraternity of Samos (The "
            "Mysteries Revised Edition), or whatever cult teaches "
            "Hermetic Architecture in your saga.",
        ),
        secrets="An initiation gone wrong left him with a Death Prophecy, that "
        "he will die with the sky above and the sea below; so he has "
        "never sailed on any of his own ships.",
        traits={
            "Hubris": 4,
            "Fearful of Open Water": 3,
            "Diligent": 2,
            "Talkative": -2,
        },
    )
    m["verecunda"] = b.magus(
        "Verecunda",
        covenant=favonius,
        house=VERDITIUS,
        age=51,
        summary=paragraphs(
            "Memnos's filia and the covenant's real leader, looking "
            "thirty-eight: a lithe woman who dresses as a sailor, far handier "
            "than robes on deck, and holds the title of Gubernatrix, chief "
            "helmsman of the fleet, captain of the Philomela. Her enchanting "
            "is in ropes, knots, cords and twine, very useful aboard but no "
            "way to win steady customers for items. Her familiar is a "
            "monkey she found on one of the fleet's longer voyages, often "
            "seen keeping watch from the Philomela's rigging. She and Basil "
            "of Andros argue endlessly over profit against adventure.",
        ),
        traits={"Avaricious": 3, "Uncompromising": 2, "Careless": 1, "Hubris": 1},
    )
    m["aeliophanes"] = b.magus(
        "Aeliophanes",
        covenant=favonius,
        house=FLAMBEAU,
        age=32,
        summary=paragraphs(
            "Captain of the Tereus, where his sanctum is, though he spends "
            "most of his time in a one-man sailing boat he paid Memnos to "
            "build. A monster hunter who chases creatures for their vis: "
            "the Tribunal knows that if a covenant has a monster too much "
            "for it, Aeliophanes will kill it, if he can be found. He is "
            "after glory, not helping, yet he is likeable, and the grogs "
            "love his dash and his Gentle Gift.",
            "He looks nineteen, a dark-haired young hero with a neat beard, "
            "and is Unaging. His talisman is his spear, enchanted to strike "
            "home despite the Might of his quarry. Peter Monocheiros owes "
            "him his life and is utterly loyal.",
        ),
        traits={"Adventurous": 2, "Proud": 2, "Careful": -3},
    )


# --------------------------------------------------------------- Ingasia


def _ingasia(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    p = theban.places
    summary = paragraphs(
        "An Autumn covenant of the Aegean phyle on Lemnos and, if a "
        "House's domus magna is wherever its primus lives, the domus magna "
        "of House Verditius: Stouritus, primus since lately, has stayed "
        "here rather than move to Verdi. Most Verditii, wrapped up in "
        "their own work, hardly care, but the question will matter more "
        "as the Verditius Contest of 1234 draws near.",
        "Gifted smiths have worked here since long before the Order. In "
        "the age of the gods Hephaistos built a forge on Lemnos and trained "
        "Gifted helpers; they stayed when he left, living apart to dull "
        "the distrust they felt for one another, and kept up their craft "
        "and their apprentices without ever growing rich. With the Order "
        "and the Parma they could truly work together, and their number "
        "grew from two to three to six and more. In law Ingasia was "
        "founded after Verdi; in history it was Hephaistos's first forge, "
        "and its magi think it the older and nobler. It stayed neutral in "
        "every war of Thebes and every quarrel of the Order, selling "
        "enchanted items to all sides alike.",
        "The fall of Constantinople strained that neutrality. Venice has "
        "held Lemnos since 1204 and seized its products, the Lemnian Earth "
        "above all, so the magi have had to raise the prices of the items "
        "they sell. Its stated purpose is to carry on House Verditius's "
        "traditions, serving the whole Tribunal by staying strictly neutral "
        "and selling to anyone who can pay. Its six magi are all Verditius: "
        "Stouritus, Theorus the Old, Hydatius, Eudoxia, and the twins "
        "Gemma and Bobila.",
    )
    what_matters = _lines(
        "Boon: Powerful Ally (Mosychlos, the covenant's patron)",
        "Boon: Aura (Magic 4); Vast and Labyrinthine (the tunnels under the volcano); Famous Resident (the primus); Prestige (Verditius domus magna in all but name)",
        "Boon: a shared forge laboratory at the Forge of Hephaistos, +8 to Rego and +5 to enchanting",
        "Hook: House Covenant; Natural Disaster (the volcano's tempers); Inhuman Covenfolk (the karkinoi)",
        "Vis: a large store kept on hand for enchanting, unusual in the Theban Tribunal, kept by the autocrat",
        "Income: enchanted items sold to all sides through vendatores; five a year may go to mundanes, Items of Quality not counted",
        "Income lost: the Lemnian Earth, seized by Venice",
        "Library: no books named; kept underground in the labyrinth",
        "Duty: the Forge of Hephaistos under Olympos (see Greece), kept by Theorus the Old",
        "Plans: Stouritus's new buildings above ground and laboratories below, to host the Contest of 1234; Egyptian marble and Trebizond oak are on order, masons and labourers hired from the villages",
        "Tension: pro-Verdi and pro-Ingasia factions of the House over the Contest's venue",
        "Tension: suspected of a secret deal with the old doge, or of aiding the crusade, since Venice took Lemnos alone of the northern isles",
    )
    patron = paragraphs(
        "The patron. Mosychlos, the volcano's moody genius loci, took "
        "little notice of the magi, who were happy to live off his aura "
        "like parasites; when the Theban Tribunal was founded and every "
        "covenant needed a patron, they made a formal pact with him. He is "
        "crabbed and cantankerous: his grumbles shake the ground and "
        "sometimes bring down tunnels, and in a rage he floods the "
        "passages near the core with lava. His oath binds him to keep "
        "this rare, but it still happens, so the magi have made devices "
        "that stop the magma and shore up the tunnels; while they stay in "
        "place, he is no danger.",
        "The covenant. Stone houses on the slopes, one for each magus; a "
        "great stone hall as meeting room and the way into the labyrinth "
        "beneath, where the laboratories, vis stores and library lie, the "
        "magi using only the tunnels to rooms they know. Life runs as "
        "regularly as a weavers' guild: forge-companions and magi work by "
        "day, Stouritus and his autocrat plan, and vendatores sell the "
        "items. Redcaps call often with the Tribunal's needs, news from "
        "Verdi and gossip about the Theban Verditii. Stouritus handles "
        "every inner and outer affair so the others can stay at their "
        "forges, and has announced that Ingasia welcomes new Verditius "
        "members, to show the Order a welcoming, well-run house against a "
        "narrow, quarrelsome Verdi.",
        "Covenfolk. Few are islanders. Most are karkinoi, descendants of a "
        "tribe Hephaistos found when he fell to Lemnos: amphibious, born "
        "and raised in the sea before they walk on land, with pincers for "
        "hands. They live in three stone houses by the coast joined to the "
        "covenant by tunnels, two for the karkinoi and one for the "
        "mundane forge-companions. A dozen covenfolk serve as maids, cooks "
        "and servants. The autocrat, Theodorus, has his own house and "
        "keeps the accounts of money and vis.",
        "Founded: the book gives no year: in law after Verdi; the pact "
        "with Mosychlos dates from the Tribunal's founding.",
    )
    hidden = _lines(
        "Gemma and Bobila sell more enchanted items than the law allows, and favour Nicaea, sworn enemy of Venice; Stouritus, busy with his buildings, has not noticed, and they raise the covenant's wealth slowly to avoid notice. Their long-term aims are unknown.",
        "Theodorus has seen the twins' rising takings but says nothing, since the money will pay for Stouritus's building.",
        "Proximios is using Hydatius and the League of the Vigilant to persecute innocent magi; a demon in Hydatius's likeness is to lead the league's members to attack.",
    )
    ingasia = b.covenant(
        "Ingasia",
        tribunal=tribunal,
        founded=None,
        place=p["mosychlos"],
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(patron),
        secrets=hidden,
        detail=FULL,
        season="Autumn",
    )
    theban.covenants["ingasia"] = ingasia
    b.book(
        ingasia,
        "The libraries of Ingasia",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. The libraries lie underground in the "
            "labyrinth of Mosychlos beside the laboratories and vis stores, "
            "and as befits the House's chief covenant Stouritus has long "
            "studied its history, members and rulings."
        ),
    )
    m = theban.magi
    m["stouritus"] = b.magus(
        "Stouritus",
        covenant=ingasia,
        house=VERDITIUS,
        age=178,
        summary=paragraphs(
            "Primus of House Verditius, looking ninety-three, and a rare "
            "thing in his House: a humble man. Long expecting to be primus, "
            "he shunned most of the Inner Mysteries that feed pride and "
            "studied instead the House's history, members and rulings. To "
            "him Verditius is the one House to outlast time, since a magus "
            "dies but an enchanted item may last for ever. He has made "
            "Ingasia a model Verditius covenant.",
            "He would like to forbid vendettas among its members but has "
            "no power to, so he leads by example and refuses what he sees as "
            "a violent, divisive custom of his House; Hydatius follows him. "
            "He has taken part in the Tribunal's government for some "
            "seventy years and is known as honest and fair. His long cause "
            "has been how many items a Verditius may sell to mundanes: the "
            "Order only demands intermediaries, and many Tribunals follow "
            "Rome's one a year, but he has raised Thebes's limit to five and "
            "persuaded it that Items of Quality are not enchanted items and "
            "do not count. He is determined that the Contest of 1234 will be "
            "held at Ingasia.",
        ),
        traits={"Driven": 3, "Humble": 2, "Hubris": 1},
    )
    m["theorus"] = b.magus(
        "Theorus the Old",
        covenant=ingasia,
        house=VERDITIUS,
        age=None,
        summary=paragraphs(
            "The second eldest of Ingasia, after Stouritus, and its keeper "
            "of the Forge of Hephaistos at the foot of Mount Olympos (see "
            "Greece), a Verditius cult site with a Faerie aura of 4 and "
            "legendary items of the god's making, where he lives alone. The "
            "book says nothing more of him.",
        ),
    )
    m["hydatius"] = b.magus(
        "Hydatius",
        covenant=ingasia,
        house=VERDITIUS,
        age=None,
        summary=paragraphs(
            "A magus of Ingasia who follows Stouritus's example and "
            "will not join in vendettas. With Proximios of Alexandria "
            "he has just founded the League of the Vigilant to hunt out "
            "infernal corruption in the Order, he as its general and "
            "the Redcap as its purse and supplier. They want members "
            "from outside the Tribunal, fresh blood to root out the "
            "bad, mean to keep the others' names secret while they "
            "themselves seek help openly, and watch their fellows "
            "patiently for a slip. Their fine reputations make the "
            "league respectable, and its critics hold their tongues.",
        ),
        secrets="Proximios, an infernalist, founded the league through him "
        "and talked him into leading it, meaning to turn it on "
        "innocents (Caterina, the young magi of Erebos, Delfini). He "
        "will urge Hydatius to send members after the suspects, and a "
        "demon in Hydatius's shape will order them to attack.",
    )
    m["eudoxia"] = b.magus(
        "Eudoxia",
        covenant=ingasia,
        house=VERDITIUS,
        age=57,
        summary=paragraphs(
            "A maker of enchanted mosaics who looks forty-two, one of "
            "the Confraternity of Irene (see Houses of Hermes: Mystery Cults). "
            "Spiteful and proud, she has lately been initiated into the "
            "Inner Mystery of automata, and works to unlock the secrets of "
            "two statues from the Hippodrome's rows that she has got hold "
            "of. (The book once spells her Euxodia.)",
        ),
        traits={"Hubris": 3, "Unpleasant": 2, "Gossip": 1},
    )
    twins = paragraphs(
        "Conjoined twins, joined at the spine so that they always face "
        "away from each other, who look thirty-five. Stouritus trained "
        "them, and they make most of Ingasia's enchanted items, forever "
        "at work. They long ago learned to live with their bodies: their "
        "laboratories are joined and mirror each other, forge for forge "
        "and bench for bench, so each can work her own enchantment at the "
        "same station as her sister. Each has her own vendator and team of "
        "forge-companions and runs her own Hermetic business. They take "
        "a season off only to study vis.",
    )
    twins_secret = (
        "Unknown to Stouritus, they sell more items than the law allows, "
        "and favour Nicaea, Venice's sworn enemy; they enrich the covenant "
        "slowly so as not to be noticed, and their long-term plans are "
        "unknown."
    )
    m["gemma"] = b.magus(
        "Gemma",
        covenant=ingasia,
        house=VERDITIUS,
        age=89,
        summary=paragraphs(twins, "Her twin is Bobila."),
        secrets=twins_secret,
        traits={"Hubris": 3, "Diligent": 2, "Bickering": 1},
    )
    m["bobila"] = b.magus(
        "Bobila",
        covenant=ingasia,
        house=VERDITIUS,
        age=89,
        summary=paragraphs(
            twins, "Her twin is Gemma. (The book also spells her Boblia.)"
        ),
        secrets=twins_secret,
        traits={"Hubris": 3, "Diligent": 2, "Bickering": 1},
    )
    b.link(m["gemma"], "characters", m["bobila"], "Her conjoined twin")


# -------------------------------------------------------------- Polyaigos


def _polyaigos(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    p = theban.places
    cyclades = p["cyclades"]
    site = _add(
        theban,
        "polyaigos",
        "Polyaigos",
        inside=cyclades,
        aura=4,
        summary=paragraphs(
            "A little rocky, mostly barren island at the Cyclades' western "
            "edge, three miles by four, with two peaks of a thousand "
            "feet; its name means 'many goats', and wild goats overrun it. "
            "On the higher peak the magi have built a watchtower that is "
            "also their council chamber and library. Below it eight "
            "dragon-houses (drakos-houses) stand at equal distances in an "
            "octagon, one due north of the peak, the next north-east, and so "
            "on: squat, rough cones of great boulders and slates, very "
            "strong, each of two floors, home and laboratory. Laskaris had "
            "an expert in Hermetic Architecture place them and raise a Magic "
            "aura in place of the Infernal one, and Varazes heaved the "
            "boulders from all over the island. The Magic aura round the "
            "peak and the sancta has grown to 4.",
            "In a flat green spot in the middle of the island is the "
            "covenfolk's stone village: a square bell tower ringed by four "
            "pavilions for drill and teaching, then barracks, kitchens, "
            "stables, workshops and lodgings. Ruined houses of the giants, "
            "some now mere heaps of boulders, are scattered about. The "
            "covenant's warship lies in the small harbour. There is no "
            "other settlement; Melos, larger and greener, lies three miles "
            "west.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "stroggylo",
        "Stroggylo, the house of Varazes",
        inside=site,
        realm="Faerie",
        aura=2,
        summary=(
            "The lower peak of Polyaigos, crowned by a bigger dragon-house "
            "where the covenant's patron, the drakos Varazes, lives, in a "
            "Faerie aura of 2."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "argentiera",
        "Argentiera",
        inside=cyclades,
        summary=(
            "An island just over a mile north-west of Polyaigos, named for "
            "its prized silvery stone, where the covenant holds a monopoly "
            "of the quarrying."
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "sifnos",
        "The mines of Sifnos",
        inside=cyclades,
        summary="An island a little north of Argentiera, with ancient gold and "
        "silver mines long abandoned.",
        secrets="Polyaigos has quietly reopened them.",
        **RUMOURED,
    )
    summary = paragraphs(
        "A strong Autumn covenant of the Kretan phyle, sworn to protect "
        "and defend the Theban Tribunal and its magi, whose members, "
        "undisputed masters of their island, have formidable martial and "
        "magical skill. Far from threatening other covenants they are "
        "widely valued for their tireless service: whenever magi are "
        "menaced by war, strife, renegades or hedge wizards, Polyaigos is "
        "first to stand up for the Order. Its good name, its famous school "
        "and its nearness to Delos bring it many visitors.",
        "In the eleventh century a nest of stringles, foul crow-women (see "
        "the Infernal landscape), infested the island and plagued the "
        "Cyclades, Delos too. When a renegade Flambeau was found among "
        "them aiding their crimes, the Tribunal's Assembly demanded action, "
        "and the hoplite Quaesitor Laskaris fought his way ashore. There "
        "he met the native drakos Varazes and struck a quick alliance "
        "against the common foe: Laskaris duelled the renegade and shielded "
        "the giant, who clubbed the Flambeau to death. Having killed or "
        "driven out the witches and cleansed the site, he founded a "
        "covenant there named for the island, pledged to make the Tribunal "
        "strike harder and faster at such enemies.",
        "It has since had several victories over the Tribunal's foes and "
        "won the trust of most, though not all, Theban magi, building its "
        "strength (now great) while taking care to work with nearby "
        "covenants rather than provoke them. With eight sancta its "
        "membership stays at eight, more than one of them Flambeau and "
        "more than one Guernicus, drawn by fighting or by teaching; several "
        "are hoplites, and the magi are often sent for when a battle is "
        "looming. It is run with military discipline under a leader chosen "
        "by the council of magi, who takes the rank and title of general.",
    )
    what_matters = _lines(
        "Boon: Powerful Ally (Varazes, the covenant's patron)",
        "Boon: Island; Veteran Fighters (a famous, well-equipped turb); Militocracy (an elected general); Aura (Magic 4)",
        "Hook: School (the Gifted children's school); Hermetic Services (defence of the Tribunal); Mundane Politics (the Duke of Naxos covets its wealth)",
        "Income: mining and quarrying, a quarry monopoly on Argentiera, and the old gold and silver mines of Sifnos",
        "Income: a small vis stipend from the Tribunal for schooling Gifted children",
        "Library: kept in the watchtower on the high peak; no books named",
        "School: classical Greek, Latin, philosophy and the liberal arts for Gifted children awaiting the Apprentice Presentation (up to a dozen by the end of the seven years), and a few unGifted youths trained as autocrats, stewards and scribes",
        "School: a military school where grogs are always drilling; other covenants send their soldiers and captains to train",
        "Warship: a crewed war galley in the island's small harbour",
        "Tension: Varazes's crushes on attractive female visitors, and the wife the magi promised him and have not found",
        "Tension: Caterina's Venetian links make other Jerbiton distrust her",
    )
    patron = paragraphs(
        "The patron. Unusually, a Faerie patron for a covenant of Magic "
        "aura whose magi care little for the fay: Varazes, a huge drakos, a "
        "faerie giant of great courage and strength, who thinks himself "
        "the island's guardian. He is a mighty ally, but his stupidity and "
        "clumsiness sometimes make him a burden; he visits when bored or "
        "lonely, and falls hopelessly in love with any handsome woman who "
        "comes, which takes tact to end peacefully. Angered, he may become "
        "a vast serpent, though his blocky, man-like head stays the same. "
        "At the Ceremony of Propitiation the magi recite the foes he has "
        "beaten.",
        "Covenfolk. Many, mostly men given the covenant's bent, with a "
        "turb famous for its training, gear, strength and fitness; a handful "
        "of its soldiers are giants who must have drakos blood. A crew "
        "mans the warship. Several have wives and families on Melos.",
        "Founded: the book gives only the eleventh century; 1050 is assumed.",
    )
    hidden = _lines(
        "Marco Sanudo, Duke of Naxos, overlord in name of the Cyclades, has heard of the school's wealth and envies it.",
        "Caterina has met the duke, posing as a rich noblewoman, and is laying the ground for a quiet arrangement with him.",
        "Satabus, newly arrived, is the duke's lost brother Pietro and has not yet written to him.",
        "Proximios means to have Caterina falsely accused of diabolism by the League of the Vigilant.",
    )
    polyaigos = b.covenant(
        "Polyaigos",
        tribunal=tribunal,
        founded=1050,
        place=site,
        summary=summary,
        what_matters=what_matters,
        notes=paragraphs(patron),
        secrets=hidden,
        unnamed_magi=3,
        detail=FULL,
        season="Autumn",
    )
    theban.covenants["polyaigos"] = polyaigos
    b.book(
        polyaigos,
        "The library of Polyaigos",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. The library is in the watchtower on "
            "the high peak, with the council chamber, and serves the "
            "covenant's school of Greek, Latin, philosophy and the liberal "
            "arts as well as its magi."
        ),
    )
    m = theban.magi
    m["maria_laskarina"] = b.magus(
        "Maria Laskarina",
        covenant=polyaigos,
        house=GUERNICUS,
        age=94,
        summary=paragraphs(
            "The Tribunal's polemarch, elected in 1207 and again in 1214: a "
            "sturdy grey-haired woman who looks fifty-eight and dresses as "
            "an ancient Greek soldier. Filia of Laskaris, the founder, and "
            "named for him, she is a seasoned hoplite known for ruthless "
            "efficiency, a master of Rego and Terram whose trademark is a "
            "crushing hail of stones. Her familiar Hadrianus, a fierce wild "
            "goat of the island and sure-footed on its rocks, patrols it "
            "hard and butts any suspicious newcomer down the cliffs into the "
            "sea.",
        ),
        traits={"Warlike": 2, "Stubborn": 2, "Pedantic": 1},
    )
    m["gerasimos"] = b.magus(
        "Gerasimos the Simple",
        covenant=polyaigos,
        house=FLAMBEAU,
        age=54,
        summary=paragraphs(
            "Drakos blood makes him huge, strong and brave, and he is held "
            "to be Varazes's own grandson, heir to his mythic strength, and "
            "to the drakoi's dreadful stupidity: hardly a grog on Polyaigos "
            "is duller, and he reduced his long-suffering master to tears. "
            "He has had to give up most book learning, and subtle Arts like "
            "Mentem and Vim are nearly beyond him, but the raw force of his "
            "simple earth and fire magic makes up for it. Honestly pious, "
            "like many of his House, he looks forty-four and has fought in "
            "more than one Wizard's March.",
        ),
        traits={"Dim-witted": 3, "Courageous": 3, "Pious": 2},
    )
    m["ioannes"] = b.magus(
        "Ioannes",
        covenant=polyaigos,
        house=BONISAGUS,
        age=49,
        summary=paragraphs(
            "A lanky, fair-haired eunuch in plain white robes, looking "
            "forty-one. Bought as a castrated slave, he was educated for the "
            "imperial court like many eunuchs until a Jerbiton maga of "
            "Moero's Garden found him; she wanted him for her apprentice, "
            "but a Bonisagus of Trianoma's line saw his fine mind and "
            "claimed him at Tribunal. He has served twice on the Council of "
            "Magistrates, a brilliant administrator there and at home, and in "
            "his second term was chosen archon, a rare honour for so young a "
            "magus.",
        ),
        traits={"Organized": 3, "Shrewd": 2, "Effeminate": 1},
    )
    m["caterina"] = b.magus(
        "Caterina da Vigonovo",
        covenant=polyaigos,
        house=JERBITON,
        age=53,
        summary=paragraphs(
            "A Venetian maga trained in the Roman Tribunal, newly come to "
            "Thebes, the reverse of many of her House, who have gone the "
            "other way; she looks her age. Her apparent ties to Venice, "
            "chief author of the crusade that took Constantinople, make "
            "the Theban Jerbiton deeply distrust her. Polyaigos has put "
            "her in charge of running and growing its mines and trade, "
            "for which she has a true Venetian gift.",
            "Like many Jerbiton she long refused a Longevity Ritual, but "
            "failing vigour has made her accept she needs one; she hopes "
            "the Tribunal will sponsor it, and is working to build a good "
            "name and earn tokens. As a metoikos she can hold none until "
            "her citizenship is decreed.",
        ),
        secrets="She has met the Duke of Naxos in the guise of a rich "
        "noblewoman and is preparing a discreet arrangement with him. "
        "Proximios has marked her as an innocent for the League of the "
        "Vigilant to accuse of diabolism.",
        traits={"Opulent": 2, "Elegant": 2, "Vain": 1},
    )
    m["satabus"] = b.magus(
        "Satabus",
        covenant=polyaigos,
        house=VERDITIUS,
        age=None,
        summary=paragraphs(
            "A young Verditius, trained at Ingasia, who has just moved "
            "to Polyaigos. The book gives no age or traits.",
        ),
        secrets="He was born Pietro, younger brother of Marco Sanudo, Duke of "
        "Naxos, and nephew of Doge Enrico Dandolo: a pleasant, clever, "
        "bookish boy with something deeply strange about him, who made "
        "his brother uneasy. Among his last acts Dandolo found him a "
        "place, which was apprenticeship at Ingasia. At Polyaigos he has "
        "learnt of Marco's rise; he keeps a warm love for his family but "
        "has not yet got in touch, while Marco often wonders what became "
        "of him and hopes for news.",
    )


# ------------------------------------------------------------ loose magi


def _loose_magi(theban: Theban, b: Builder) -> None:
    m = theban.magi
    m["zacharias"] = b.magus(
        "Zacharias",
        covenant=None,
        house=EX_MISC,
        age=None,
        summary=paragraphs(
            "A magus of the Cult of Orpheus (Houses of Hermes: Societates) "
            "who keeps Orpheus's sacred grove of Orphykia on Lesbos alone, "
            "belonging to no covenant. The book gives no more.",
        ),
    )
    m["marcus_tauros"] = b.magus(
        "Marcus Tauros",
        covenant=None,
        house=CRIAMON,
        age=None,
        summary=paragraphs(
            "A Criamon described in Magi of Hermes who seems to have "
            "had visions of a past life as a priest of Minoan Candia, "
            "and may be found at the ruins of Knossos digging in the "
            "catacombs for the lore of a magical bull cult of the "
            "Minoans.",
        ),
        secrets="He has not yet found the regio in which the labyrinth survives whole.",
    )


# ---------------------------------------------------------- mundane world


def _lords(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["duke_of_naxos"] = b.lord(
        "Duchy of Naxos",
        title="duke",
        wealth="Wealthy",
        manors=50,
        seat="The Kastro, Naxos",
        ruler="Marco Sanudo",
        place=p["cyclades"],
        summary=paragraphs(
            "The new realm of the Cyclades. Marco Sanudo, a Venetian, "
            "nephew of Doge Enrico Dandolo of the Fourth Crusade and "
            "heir to much of his charm and good sense, was charged with "
            "putting down Cycladic piracy; he borrowed Venetian galleys, "
            "fell on Naxos in 1207 and, after hard fighting, took it, "
            "and by 1212 he held nearly all the Cyclades, which he split "
            "into more than fifty lordships under him, many held by his "
            "kin. Delos is his, in name.",
            "The duchy thrives: it does homage to the Latin emperor and "
            "is mostly left alone in the endless wars and intrigues. In "
            "name a vassal of the Latin Empire, Marco holds his lands in "
            "his own right, free of Venice and its doge yet close to "
            "Venetian interests. He brought in the Latin Church and "
            "barred the Orthodox from high office, but left Greek "
            "churches and clergy largely in peace, and his people seem "
            "content to go on as before under new lords. He has just "
            "finished the Kastro on Naxos and begun a cathedral. He has "
            "heard tales of Polyaigos's riches and envies them.",
        ),
        secrets="His younger brother Pietro, whom he never felt easy with and "
        "often wonders about, is Satabus of Verditius, now at "
        "Polyaigos. Caterina da Vigonovo has met him as a wealthy "
        "noblewoman and is preparing a quiet bargain.",
    )
    b.link(
        w["duke_of_naxos"],
        "characters",
        theban.magi["satabus"],
        "His lost brother Pietro",
    )
    w["negroponte"] = b.lord(
        "Lordship of Negroponte",
        title="baron",
        manors=6,
        seat="Chalkis",
        ruler="The heirs of Ravano dalle Carceri, under Venetian bailiffs",
        place=p["islands"],
        summary=paragraphs(
            "Euboea, sparsely peopled since William of Sicily's sack of "
            "1157, fell after 1204 to three barons of Verona, the Triarchy, "
            "who made it a lordship of baronies named for Negroponte, the "
            "Venetian name for Chalkis's bridge, the city and then the "
            "whole island: the central barony at Chalkis, the northern at "
            "Oreoi, the southern at Karystos. Ravano dalle Carceri, one of "
            "the three, took the whole island and, defying his homeland, "
            "accepted Venice as overlord. After he died in 1216 the "
            "Venetian bailiffs halved each barony and shared the six "
            "among his kin and heirs. Aegaea lies under the sea not far off "
            "its coast (Euboea itself is described with Greece).",
        ),
    )
    w["candia"] = b.lord(
        "Kingdom of Candia",
        title="duke",
        wealth="Wealthy",
        seat="Chandax",
        ruler="A Venetian duke, named for two years",
        place=p["candia"],
        summary=paragraphs(
            "Venice's Candia, set up in 1212 once the republic had wrested "
            "the island from the Genoese pirate Enrico Pescatore; Boniface "
            "of Montferrat had sold it to the doge for 1000 marks. Four "
            "Venetian dukes have ruled it in turn for two years each, and "
            "Venetian families are encouraged to settle. The Greeks resent "
            "the higher taxes and tolls of the ports, and the mood is "
            "rebellious. The rulers are walling Chandax anew and building a "
            "harbour fortress, and they offer a handsome reward for the "
            "capture or death of Talos, the bronze 'demon' who sinks their "
            "ships.",
        ),
    )
    w["lemnos"] = b.lord(
        "Venetian Lemnos",
        title="landed",
        seat="Myrina",
        place=p["lemnos"],
        summary=paragraphs(
            "Lemnos, the only northern island Venice claimed in 1204, has "
            "been under Venetian rule since, and its new masters have "
            "claimed the whole island and its goods, the Lemnian Earth of "
            "Hephaistia above all, cutting into Ingasia's finances. Some "
            "magi read the choice as a sign of a secret deal between House "
            "Verditius and the old doge. The book names no governor; "
            "history has the Venetian Filocalo Navigajoso holding the island "
            "as a fief, with the title of megadux.",
        ),
    )
    w["rodos"] = b.lord(
        "Despotate of Rodos",
        title="landed",
        wealth="Wealthy",
        seat="Rodos",
        ruler="Leo Gavalas, despot",
        place=p["rodos"],
        summary=paragraphs(
            "Leo Gavalas, a rich and corrupt dynatos who came from "
            "Constantinople soon after it fell, has made himself despot "
            "of Rodos, an island Venice claims and where it has kept a "
            "naval base since 1082. He fears that free reading will "
            "make his subjects rebel, so one of his first acts was to "
            "confiscate every book; only works he has approved, which "
            "show him in a good light, may be sold.",
        ),
        secrets="His closest adviser, an infernal hedge wizard, steers him, "
        "wrote the island's only books (a perverted Bible among them), "
        "and is gathering all its vis for himself.",
    )


def _churches(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["st_john_patmos"] = b.church(
        "Monastery of St John the Divine, Patmos",
        church="Monastery or nunnery",
        place=p["patmos"],
        summary=(
            "Founded at the end of the eleventh century and later fortified "
            "against pirates and petty despots, the only house on holy "
            "Patmos, thronged with pilgrims. Its patron saint is St "
            "Leontios, a holy fool made a saint for his asceticism alone "
            "(see the Divine landscape). Some of its monks claim visions in "
            "the Cave of the Apocalypse."
        ),
    )
    w["nea_moni"] = b.church(
        "Nea Moni, Khios",
        church="Monastery or nunnery",
        place=p["khios"],
        summary=(
            "The 'new monastery' of Khios, founded by the emperor "
            "Constantine IX, one of the largest in the old Byzantine Empire."
        ),
    )
    w["chandax_archbishop"] = b.church(
        "Archbishopric of Chandax",
        church="Archbishop's cathedral",
        place=p["candia"],
        summary=(
            "Chandax, seat of the Kingdom of Candia, is also an "
            "archbishop's see; the book says no more of its clergy."
        ),
    )
    w["naxos_cathedral"] = b.church(
        "The new cathedral of Naxos",
        church="Bishop's cathedral",
        place=p["naxos"],
        summary=(
            "The Latin cathedral Marco Sanudo has just begun beside his "
            "Kastro, as he brings the Western Church to the Cyclades while "
            "leaving the Orthodox churches largely alone."
        ),
    )
    w["kos_church"] = b.church(
        "The church of Kos",
        place=p["kos"],
        summary=(
            "The town church where the wreath from the Tree of Hippocrates "
            "hangs among the icons for a year after it is blessed, before "
            "the women carry it to the sea."
        ),
    )


def _towns(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "chandax",
        "Chandax",
        "The chief city of Candia and the largest of the Greek islands, "
        "which the Venetians just call Candia, on the site of old Iraklion "
        "halfway along the north coast. The Saracens refounded it in the "
        "ninth century, ringed it with a moat and raided Byzantine shipping "
        "from it; the Byzantines razed and rebuilt it when they took it. "
        "Now seat of the kingdom and an archbishopric, it is getting a "
        "stronger wall over the Saracen defences and a new harbour fort. "
        "Mount Zeus's profile looms behind it.",
        charter="Noble lord",
        answers_to=w["candia"],
        place=p["candia"],
    )
    town(
        "rodos_town",
        "Rodos",
        "The walled city at the north of the island, split by the "
        "Saracens into quarters, one still largely Jewish, with its own "
        "quarter for the rulers; a Venetian naval base since 1082, and now "
        "the despot's seat, where only books he approves may be sold.",
        charter="Noble lord",
        answers_to=w["rodos"],
        place=p["rodos"],
    )
    town(
        "naxos_town",
        "Naxos",
        "The duke's seat, under the new Kastro, with a cathedral rising.",
        charter="Noble lord",
        answers_to=w["duke_of_naxos"],
        place=p["naxos"],
    )
    town(
        "kos_town",
        "Kos",
        "A busy port among rich farms, round the Tree of Hippocrates, "
        "inside a Divine aura.",
        charter="Noble lord",
        place=p["kos"],
    )
    town(
        "andros_town",
        "Andros",
        "The Cyclades' other great port, famous for its shipwrights; home "
        "port of Favonius and Memnos's yard.",
        charter="Noble lord",
        answers_to=w["duke_of_naxos"],
        place=p["andros"],
    )
    town(
        "myrina",
        "Myrina",
        "One of the two largest towns of Lemnos, on its west coast.",
        charter="Noble lord",
        answers_to=w["lemnos"],
        place=p["lemnos"],
    )
    town(
        "hephaistia",
        "Hephaistia",
        "The other great town of Lemnos, on the north-east coast, near "
        "the pits of the Lemnian Earth that Venice has taken over.",
        charter="Noble lord",
        answers_to=w["lemnos"],
        place=p["lemnos"],
    )
    town(
        "mytilene",
        "Mytilene",
        "The first of the five towns of Lesbos named for King Makaras's "
        "daughters, on an island where women rule.",
        charter="Noble lord",
        place=p["lesbos"],
    )
    town(
        "antissa",
        "Antissa",
        "A town of western Lesbos, birthplace of the minstrel Terpander, "
        "near Orpheus's grove of Orphykia.",
        charter="Noble lord",
        place=p["lesbos"],
    )


def _factions(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["aegean_pirates"] = b.faction(
        "The Pirates of the Aegean",
        faction="Other",
        decides="Its leader",
        place=p["islands"],
        wants="Booty and ransoms",
        offers="Hire as mercenaries; news of shipping",
        summary=paragraphs(
            "The countless crews who have raided the Archipelago since "
            "antiquity, now swollen in number by the empire's fall; some of "
            "their chiefs rule ports as despots. On the poor islets raiding "
            "is a respectable living. Lords hang them, but rulers have long "
            "hired them too, and some Venetian captains will deal with any "
            "who prey on their rivals. The Tribunal bans covenants from "
            "attacking one another's ships, but pirates know nothing of the "
            "Order, and robbing mundanes is not forbidden, only frowned on. "
            "They may be villains holding a covenant's people for ransom, "
            "or bold rogues standing up to greedy lords and captains.",
        ),
    )
    w["monocheiros"] = b.faction(
        "Peter Monocheiros's crew",
        faction="Other",
        decides="Its leader",
        members=8,
        ruler="Peter Monocheiros",
        place=p["favonius_fleet"],
        wants="Plunder, under Favonius's protection",
        offers="A third of the plunder to Favonius; eight capable warriors",
        summary="Peter 'One Hand', a pirate who sails with Favonius in two "
        "ships of his own, with eight of the covenant's best fighters "
        "sworn to him. He owes his life to Aeliophanes and is utterly "
        "loyal.",
        secrets="He gives the covenant a third of his plunder for the fleet's "
        "protection, passing anything identifiable to Basil to sell in "
        "far ports; his men wear masks at work and his ships are "
        "enchanted to change their look, so nothing leads back to "
        "Favonius.",
    )
    w["basil_andros"] = b.faction(
        "The trading house of Basil of Andros",
        faction="Gild",
        decides="Its leader",
        ruler="Basil of Andros",
        place=p["andros"],
        wants="Profitable voyages, and a trading house of his own",
        offers="Supplies, trade, sales in distant ports",
        summary=(
            "Favonius's chief companion, captain of the Procne and a "
            "merchant-adventurer (City & Guild) well on his way to founding "
            "his own house; he keeps the fleet supplied, and his hot temper "
            "keeps him arguing with Verecunda over profit and adventure."
        ),
    )


# ------------------------------------------------------------- finishing


def finish(theban: Theban) -> None:
    """Put the Duke of Naxos under the Latin Emperor once
    constantinople.py has made him."""
    emperor = theban.world.get("latin_emperor")
    if emperor is not None:
        theban.world["duke_of_naxos"].answers_to = emperor.id


# --------------------------------------------------------------- stats

P = Profile
GREEK = "Greek"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "lucian": P(
        strong="int com pre",
        arts={"Im": 6, "Me": 6, "Aq": 4, "Mu": 4, "In": 3, "Cr": 3},
        abilities={
            "Faerie Lore": (5, "Greek gods"),
            "Artes Liberales": (4, "rhetoric"),
            "Charm": 2,
            "Intrigue": 3,
            "Area Lore: Theban Tribunal": 3,
        },
        virtues=[
            "Story Magic",
            "Olympian Pact",
            "Elysian Ecstasy",
            "Well-Traveled",
            "Twilight Prone",
            "Delusion",
            "Obsessed (Major)",
            "Infamous",
        ],
        native=GREEK,
    ),
    "leukothea": P(
        strong="pre com sta",
        arts={"Aq": 7, "Mu": 5, "An": 4, "Co": 3, "Re": 3},
        abilities={"Swim": (4, "underwater"), "Faerie Lore": (3, "the sea fae")},
        virtues=[
            ("Strong Faerie Blood", {"blood": "nereid"}),
            _art("Affinity with {art}", "aquam"),
            "Warped by Magic",
            "Disfigured",
            "Reclusive",
            "Lost Love",
        ],
        native=GREEK,
    ),
    "delfini": P(
        strong="com per sta",
        arts={"Aq": 6, "An": 6, "Mu": 5, "In": 3, "Co": 3},
        abilities={"Swim": (5, "as a dolphin"), "Folk Ken": 2, "Charm": 2},
        virtues=["Gossip", "Warped by Magic", "Driven (Minor)"],
        native=GREEK,
    ),
    "krum": P(
        strong="qik sta str",
        weak="int",
        arts={"An": 7, "Mu": 6, "Co": 4, "Aq": 3},
        abilities={"Athletics": (5, "racing"), "Ride": (3, "racing"), "Swim": 3},
        virtues=["Reckless", "Warped by Magic"],
        native="Bulgarian",
    ),
    "memnos": P(
        strong="str int dex",
        arts={"Re": 8, "He": 6, "Aq": 4, "Au": 3, "Cr": 3},
        abilities={
            "Craft: Shipwright": (6, "round ships"),
            "Profession: Sailor": 0,
            "Athletics": (3, "climbing"),
            "Magic Theory": (6, "enchanting ships"),
        },
        virtues=[
            "Hermetic Architecture",
            "Items of Quality",
            "Skilled Climber",
            "Fear",
            "Hubris",
            "Obsessed (Minor)",
        ],
        native=GREEK,
    ),
    "verecunda": P(
        strong="dex qik int",
        arts={"Re": 6, "He": 5, "An": 3, "Au": 4},
        abilities={
            "Profession: Sailor": (5, "helmsman"),
            "Craft: Ropemaker": (4, "knots"),
            "Leadership": (3, "sailors"),
        },
        virtues=["Avaricious (Minor)", "Hubris"],
        native=GREEK,
    ),
    "aeliophanes": P(
        strong="pre qik sta",
        arts={"Pe": 6, "Ig": 5, "Cr": 3, "An": 4, "Vi": 3},
        abilities={
            "Single Weapon": (4, "spear"),
            "Hunt": (4, "monsters"),
            "Profession: Sailor": 2,
            "Magic Lore": (3, "creatures"),
        },
        virtues=[
            "Gentle Gift",
            "Unaging",
            "Proud (Minor)",
            "Reckless",
            "Driven (Minor)",
        ],
        native=GREEK,
    ),
    "stouritus": P(
        strong="int com per",
        arts={"Re": 7, "Te": 6, "Ig": 5, "Vi": 5, "Cr": 4},
        abilities={
            "Code of Hermes": (6, "the sale of items"),
            "Organization Lore: Order of Hermes": (5, "House Verditius"),
            "Magic Theory": (7, "enchanting"),
            "Leadership": 3,
        },
        virtues=["Hermetic Prestige", "Humble", "Driven (Minor)", "Hubris"],
        native=GREEK,
    ),
    "theorus": P(
        strong="int sta",
        arts={"Ig": 7, "Te": 6, "Re": 5, "Vi": 3},
        abilities={"Faerie Lore": (3, "Olympos"), "Magic Theory": (6, "enchanting")},
        virtues=["Reclusive", "Hubris"],
        age=150,
        native=GREEK,
    ),
    "hydatius": P(
        strong="int per pre",
        arts={"In": 6, "Vi": 6, "Re": 4, "Te": 4, "Ig": 3},
        abilities={
            "Infernal Lore": (4, "demons"),
            "Leadership": (3, "the league"),
            "Folk Ken": 2,
        },
        virtues=["Driven (Minor)", "Hubris"],
        age=90,
        native=GREEK,
    ),
    "eudoxia": P(
        strong="int dex",
        weak="pre com",
        arts={"Im": 6, "Te": 6, "Re": 5, "Mu": 4},
        abilities={"Craft: Mosaicist": (5, "enchanted mosaics")},
        virtues=["Automata", "Hubris", "Proud (Major)"],
        native=GREEK,
    ),
    "gemma": P(
        strong="int dex sta",
        arts={"Re": 6, "Te": 6, "Ig": 5, "Vi": 4},
        abilities={"Craft: Goldsmith": (5, "jewellery"), "Bargain": 2},
        virtues=["Inventive Genius", "Disfigured", "Hubris", "Dark Secret"],
        native=GREEK,
    ),
    "bobila": P(
        strong="int dex sta",
        arts={"Re": 6, "Te": 6, "Ig": 5, "Vi": 4},
        abilities={"Craft: Smith": (5, "fine metalwork"), "Bargain": 2},
        virtues=["Inventive Genius", "Disfigured", "Hubris", "Dark Secret"],
        native=GREEK,
    ),
    "maria_laskarina": P(
        strong="sta str int",
        arts={"Re": 8, "Te": 8, "Pe": 4, "In": 3},
        abilities={
            "Single Weapon": (4, "spear"),
            "Code of Hermes": (5, "Wizard's Marches"),
            "Leadership": (4, "hoplites"),
            "Penetration": 4,
        },
        virtues=[_art("Puissant {art}", "terram"), "Dutybound", "Proud (Minor)"],
        native=GREEK,
    ),
    "gerasimos": P(
        strong="str sta",
        weak="int com",
        arts={"Te": 8, "Ig": 8, "Cr": 5, "Pe": 5, "Me": 0, "Vi": 0},
        abilities={"Brawl": (4, "grapple"), "Great Weapon": (3, "club")},
        virtues=[
            "Giant Blood",
            "Simple-Minded",
            "Pious (Minor)",
            "Weak Scholar",
        ],
        native=GREEK,
    ),
    "ioannes": P(
        strong="int com per",
        arts={"In": 5, "Me": 5, "Re": 5, "Vi": 4, "Cr": 3},
        abilities={
            "Civil and Canon Law": (4, "Byzantine law"),
            "Profession: Scribe": (3, "accounts"),
            "Etiquette": (3, "the imperial court"),
            "Code of Hermes": (5, "the polity"),
        },
        virtues=["Archieunuch", "Dutybound", "Driven (Minor)", "Social Handicap"],
        native=GREEK,
    ),
    "caterina": P(
        strong="pre com int",
        arts={"Te": 6, "Me": 5, "Im": 5, "Re": 4, "Cr": 3},
        abilities={
            "Bargain": (4, "mining contracts"),
            "Etiquette": (4, "Venetian nobility"),
            "Charm": 3,
        },
        virtues=["Social Contacts", "Proud (Minor)", "Ambitious (Minor)"],
        native="Italian",
        hermetic="Latin",
    ),
    "satabus": P(
        strong="int per",
        arts={"Re": 5, "Te": 4, "Ig": 4, "Vi": 3},
        abilities={"Craft: Goldsmith": 3, "Artes Liberales": 2},
        virtues=["Close Family Ties", "Dark Secret"],
        age=26,
        native="Italian",
    ),
    "zacharias": P(
        strong="pre com per",
        arts={"An": 6, "He": 6, "Me": 5, "Au": 3},
        abilities={"Music": (5, "lyre"), "Animal Ken": 3},
        virtues=["Sorcerous Music", "Reclusive", "Vow"],
        age=60,
        native=GREEK,
    ),
    "marcus_tauros": P(
        strong="int per",
        arts={"In": 6, "An": 5, "Me": 4, "Te": 3},
        abilities={"Philosophiae": 2, "Magic Lore": (3, "regiones")},
        virtues=["Visions", "Obsessed (Minor)"],
        age=45,
        native=GREEK,
    ),
}


def stats(theban: Theban) -> None:
    """Generated stats for the magi of the islands, none of whom has a
    printed stat block."""
    b = theban.b
    for key, profile in PROFILES.items():
        apply(b, theban.magi[key], profile)
