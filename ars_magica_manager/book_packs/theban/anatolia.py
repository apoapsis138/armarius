"""Anatolia, the Theban Tribunal's Asian shore, as of 1220: Bithynia, the
Troad, Lydia, Thrakesion and the Black Sea coast of Paphlagonia and
Pontus; the Mercere covenant of Alexandria above Smyrna and its Redcaps;
Moero's Garden, the Jerbiton exiles in Nicaea; the region's auras,
regiones and vis; and the Empire of Nicaea, its emperor and the Orthodox
patriarch, the Empire of Trebizond, the Sultanate of Rum and its Greek
vassal at Sinope, in paraphrase of The Sundered Eagle chapter eight (with
chapter two for the empires in 1220 and chapter three for each
covenant's politics).

Wilusa, the covenant lost at Troy, is tribunal.py's, set at level 1 of
places["ilion"]; the other ruins of Anatolia (Miphoria, Estropi,
Kyddopetre, Lamites) are tribunal.py's too, inside places["anatolia"].
Creatures are the Bestiary's (the Demon of Nicaea at
places["nicaea_roads"], the druj at places["xerxes_hill"], Klymene at
places["great_altar"], the glass submarine at places["mount_pagus"]),
named here only in the summaries of the places they haunt. Evantia of
Moero's Garden is realms.py's; this part's finish sets her covenant if
realms has not."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...models.world import FULL
from ..builder import Builder, paragraphs, secrets
from ..generated import Profile, apply

if TYPE_CHECKING:
    from ...models import Covenant, Neighbour, Tribunal
    from . import Theban

BONISAGUS = "house_bonisagus"
JERBITON = "house_jerbiton"
MERCERE = "house_mercere"
TYTALUS = "house_tytalus"

#: The lead line of a covenant's notes, before its secrets.
STORYGUIDE = "What the players do not know."

KNOWN_ORDER: dict[str, Any] = {"status": "Known", "known": "In the Order"}
KNOWN_TRIBUNAL: dict[str, Any] = {"status": "Known", "known": "In the Tribunal"}
KNOWN_REGION: dict[str, Any] = {"status": "Known", "known": "In the region"}
KNOWN_LOCALLY: dict[str, Any] = {"status": "Known", "known": "Locally"}
RUMOURED: dict[str, Any] = {"status": "Rumoured", "known": "Locally"}
RUMOURED_TRIBUNAL: dict[str, Any] = {"status": "Rumoured", "known": "In the Tribunal"}


def _lines(*lines: str) -> str:
    """The lines as one text, one entry a line."""
    return "\n".join(lines)


def _add(theban: Theban, key: str, name: str, **kw: Any) -> Neighbour:
    """Make a place and store it under `key` for the other parts."""
    place = theban.b.place(name, **kw)
    theban.places[key] = place
    return place


def _tribunal(theban: Theban) -> Tribunal:
    tribunal = theban.tribunal
    if tribunal is None and theban.b.saga.tribunals:
        tribunal = theban.b.saga.tribunals[0]
    if tribunal is None:
        raise RuntimeError("tribunal.py must build the Theban Tribunal first")
    return tribunal


def build(theban: Theban) -> None:
    b = theban.b
    tribunal = _tribunal(theban)
    _region(theban)
    _bithynia(theban)
    _troad(theban)
    _pergamos(theban)
    _lydia(theban)
    _thrakesion(theban)
    _black_sea(theban)
    _alexandria(theban, b, tribunal)
    _moeros_garden(theban, b, tribunal)
    _lords(theban, b)
    _churches(theban, b)
    _towns(theban, b)
    _factions(theban, b)


# ------------------------------------------------------------- the region


def _region(theban: Theban) -> None:
    _add(
        theban,
        "anatolia",
        "Anatolia",
        summary=paragraphs(
            "Asia Minor, where East meets West: a great central plateau "
            "walled off from the coasts by two long mountain chains, the "
            "Taurus in the south and the Pontic range in the north. The "
            "emperors once ruled all of it in provinces, or themes, but "
            "since the twelfth century much has gone to the Seljuk Turks, "
            "and in 1220 the Greeks keep only the shores: the Aegean coast "
            "west of the Taurus and the Black Sea coast north of the Pontic "
            "mountains. The interior and the lands beyond are fought over "
            "by Turks, Persians, Pechenegs, Cumans and Georgians.",
            "The Tribunal has always kept to Byzantine soil, so its "
            "covenants sit on the Aegean shore, round the Sea of Marmara "
            "and by the Black Sea. Theban magi once founded covenants on "
            "the far edges, nearer foreign wizards and strange magic, but "
            "every one of them has failed, from neglect, invasion or "
            "something stranger; the Byzantine magi of the plateau fled "
            "after Manzikert in 1071 and have never gone back. Two "
            "covenants remain on this shore: Alexandria above Smyrna, of "
            "the Kretan phyle, which takes in southern Nicaea, and "
            "Moero's Garden in Nicaea itself, of the Propontian phyle, "
            "which takes in the north.",
            "Most of the Greek coast belongs to the Empire of Nicaea, which "
            "has just gone back to war with the Latins of Constantinople; "
            "the Latins hold the northern Troad and part of Bithynia, the "
            "Sultanate of Rum holds the plateau and Sinope, and the Empire "
            "of Trebizond holds the far end of the Black Sea.",
            "Vis of Anatolia (each in its place): the clay votive limbs of "
            "the Asklepieion at Pergamos (12 Corpus a year), the old "
            "Dionysian vineyard on Mount Tmolus by Philadelphia (Mentem, "
            "distilled from its wine), the magical plants of Trebizond's "
            "gardens (several would give vis every year if harvested "
            "properly), and perhaps the time-slowed regio of the Seven "
            "Sleepers' cave near Ephesus. The book does not say which of "
            "them, if any, are the polity's common sources. The Great "
            "Altar of Pergamos powers ritual spells without vis, at a "
            "price.",
        ),
        **KNOWN_ORDER,
    )


# -------------------------------------------------------------- Bithynia


def _bithynia(theban: Theban) -> None:
    region = theban.places["anatolia"]
    bithynia = _add(
        theban,
        "bithynia",
        "Bithynia",
        inside=region,
        summary=paragraphs(
            "The north-west corner of Anatolia, facing Constantinople and "
            "the Thracian shore across the Sea of Marmara: wide forests, "
            "green hills and rich valleys, famous for its oranges and other "
            "fruit and for its grain. It is full of old and great cities, "
            "and armies have tramped over it again and again these twenty "
            "years. It is the march between the Latin Empire and the "
            "Empire of Nicaea, and its coastal castles have changed "
            "hands many times.",
            "Six years of peace followed Theodore Laskaris's treaty with "
            "the Latins, sealed in 1219 by his marriage to a niece of the "
            "late Emperor Henry; but in 1220 the emperor is massing troops "
            "along the border for a new attack, and the Bithynians watch "
            "them gather with dread.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "nicaea_roads",
        "The Roads about Nicaea",
        inside=bithynia,
        realm="Infernal",
        summary=secrets(
            paragraphs(
                "The highways outside Nicaea's walls, where lone travellers "
                "are now and then found torn to pieces, roughly once a "
                "month. Most townsfolk blame bandits or skirmishers from "
                "one army or the other; a few recall the tale of St Andrew "
                "the apostle, who drove off seven demons in the shape of "
                "slavering dogs that were killing wayfarers here, then "
                "raised from the dead a young man the same seven had "
                "savaged in his bed, who followed the saint from then on.",
                "The seven still hunt the roads round the city, though "
                "they may not pass its walls: the Demons of Nicaea, see "
                "the Bestiary. They strike at dusk or just after, choose "
                "people travelling alone, leave large parties be, and "
                "flee a stronger band. A Redcap riding solo is just the "
                "prey they like.",
            ),
            "No magus has yet connected the roadside killings with the "
            "demons; a Redcap of Alexandria or Moero's Garden's covenfolk "
            "on an errand are the likeliest next victims.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "nicomedia_warren",
        "The Warren beneath Nicomedia",
        inside=bithynia,
        summary=paragraphs(
            "Nicomedia is shaken by an earthquake about once a century, "
            "which brings down houses and starts fires. Some Theban magi "
            "suspect an old titan lies bound under the city and strains "
            "at its chains every hundred years. The townsfolk would laugh "
            "at them: everyone knows it is the dragon St George the "
            "Megalomartyras (the 'great martyr') wounded long ago, "
            "writhing in agony in tunnels below the streets.",
            "George, a Roman tribune from Cappadocia, wounded a dragon to "
            "save a king's daughter offered to it and led the beast back "
            "to the city on a leash; towns from Jerusalem to Ireland claim "
            "the tale, perhaps Nicomedia among them. Whatever the truth, "
            "something does lie under the city. The book gives it no "
            "aura or realm.",
        ),
        **RUMOURED,
    )


# -------------------------------------------------------------- the Troad


def _troad(theban: Theban) -> None:
    region = theban.places["anatolia"]
    troad = _add(
        theban,
        "troad",
        "The Troad",
        inside=region,
        summary=paragraphs(
            "The big peninsula of north-western Anatolia (Troas), with a "
            "cold, wet north on the Sea of Marmara and a milder west on "
            "the Aegean, hot in summer and dry inland. Seven rivers run "
            "off the plateau of Mount Ida through gorges to the sea, and "
            "the cliffs and small bays of the shore offer many sites for "
            "a town that wants defending.",
            "As in Bithynia, Latin crusaders hold the northern half, quiet "
            "since the peace of 1216: their lords govern and let the "
            "people thrive, and many of their knights are away fighting "
            "the Bulgarians. Theodore Laskaris means to exploit their "
            "absence and march on Holkos on the Hellespont; at the "
            "saga's start his army is gathered and the blow is about to "
            "fall.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "hellespont",
        "The Hellespont",
        inside=troad,
        summary=paragraphs(
            "The thirty-eight-mile strait between Greece and Anatolia that "
            "links the Aegean with the Sea of Marmara, called the straits "
            "of St George by the French; Greeks and Persians long used it "
            "as a moat and a frontier. Though only one to four miles "
            "across, it is hard sailing: its currents flow either way with "
            "the tide and the hour, and pilots steer with great care.",
            "Holkos, the Latin port where the strait meets the Marmara, is "
            "Laskaris's goal; he would make it a second base for his navy, "
            "to guard the straits against Venetian shipping. History has "
            "him take it, and the Latins, beset from the north, ask for "
            "peace in 1221.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "xerxes_hill",
        "The Vantage Point of Xerxes",
        inside=troad,
        realm="Infernal",
        aura=3,
        summary=secrets(
            paragraphs(
                "A small round hill near Abydos, west of Holkos along the "
                "shore, from which the whole Hellespont can be seen. Looked "
                "at closely it is man-made, worn by age and wind. "
                "Artabanos, the sorcerer of Xerxes, raised it in the "
                "Persian Wars and set a marble throne on top that sharpened "
                "the king's sight by magic; the throne is gone.",
                "Whoever stands on the hill still sees the strait and its "
                "shores as if with Keen Vision. The hill has an Infernal "
                "aura of 3.",
            ),
            "Artabanos made a druj build the hill in a single day, then "
            "bound her under it and fed her power into the king's view; "
            "her malice seeped through and filled Xerxes with doubt and "
            "gloom. She is bound there still (Infernal Might 30, an "
            "Obsession of Doubt; see the Bestiary), and anyone using the "
            "view is open to her Obsession.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "ilion",
        "Ilion (Troy)",
        inside=troad,
        realm="Faerie",
        aura=2,
        levels=[
            Builder.level(
                "Wilusa's Troy",
                4,
                "Faerie",
                notes=(
                    "The regio in which the covenant of Wilusa was raised "
                    "in 1109, now dressed as Troy and closed by the faerie "
                    "who calls himself Odysseus; time runs slow inside."
                ),
            )
        ],
        summary=secrets(
            paragraphs(
                "Priam's city, Ilium to the Latins, razed by the Greeks at "
                "the end of the Trojan War, about 1184 BC by Eratosthenes's "
                "reckoning. Nothing stands on the sandy shore now, the "
                "Scamander has dried up, and even Augustus's Roman town "
                "has vanished without a stone. It matters nothing to Greeks "
                "or Turks as land, but much as propaganda: many Westerners "
                "claim Trojan descent and call the Latin conquest of "
                "Constantinople Troy's revenge on the Greeks.",
                "Magi find it important and perilous. So many tales are "
                "told of Ilion that it might be called the cradle of "
                "storytelling, and it swarms with faeries each longing to "
                "replay a story. The beach and the stony field have a "
                "Faerie aura of 2, riddled with hidden Faerie regiones that "
                "overlap and connect in a bewildering maze. Merinita magi "
                "say one holds a faerie city called Ilion, reached only by "
                "sea, ever readying for the siege; others replay the Greek "
                "ships and camp, the bloody plain and the burning city. "
                "The strong faeries each take one scene from a hero's life, "
                "so there are several Akhilles, several Paris and several "
                "Odysseus.",
                "Left alone, the faeries play their parts idly; a mortal "
                "visitor is chum in the water, and the mightiest snatch him "
                "for their own tales, the lesser ones pulling the other "
                "way. Several Hektors, say, will each want him in a "
                "different part of Hektor's story. The strongest can shut a "
                "regio and keep their captives fighting the war for ever, "
                "and locals say people who wander the plain of Troy can "
                "vanish for good and that the ghosts of the fallen haunt "
                "it.",
                "Every few Tribunals someone proposes a covenant here. In "
                "1109 the Tribunal let Droserius of Merinita and four "
                "others found Wilusa, claiming the spirit of the Scamander "
                "had promised to be its patron; by the next meeting it had "
                "vanished and no search found a trace. The Tribunal now "
                "turns down any new proposal with ease.",
            ),
            paragraphs(
                "Wilusa was built swiftly by magic in a Faerie regio of "
                "aura 4, but not the one where the Scamander's spirit "
                "dwells: a faerie calling himself Odysseus fooled "
                "Droserius, then sealed the regio. He has glamoured the "
                "covenant to look like Troy and throws the war's last "
                "assault at it again and again, the magi defending it by "
                "reflex; by bending time, the faeries have kept it up for "
                "more than a century, while the magi think only months "
                "have passed. Odysseus is fully cognizant and hopes to "
                "gather enough vitality to change his own story.",
                "Finding that regio is hard: other faeries lure searchers "
                "into their own tales, it takes good Faerie Lore and "
                "patient exploring, and more than one regio stages the "
                "sack, so beating the 'Greeks' may only show the searchers "
                "they are in the wrong Troy. Even rescued, Droserius and "
                "his sodales will be loath to leave until shown that a "
                "hundred years have gone by.",
            ),
        ),
        **KNOWN_TRIBUNAL,
    )


# --------------------------------------------------------------- Pergamos


def _pergamos(theban: Theban) -> None:
    troad = theban.places["troad"]
    acropolis = _add(
        theban,
        "pergamos",
        "The Acropolis of Pergamos",
        inside=troad,
        summary=paragraphs(
            "A great city to the Greeks and early Romans that has long "
            "since dwindled: its old acropolis, a stair of terraces above "
            "the Caicus and its plain, is a jumble of Greek and Roman "
            "ruins. To Greeks of 1220 it matters as one of the seven "
            "churches of St John's Revelation; the Church of St John, "
            "raised over a temple of Isis and Serapis, serves the "
            "Christians who still live there.",
            "To magi it matters for its temples, ruined and mostly "
            "unexplored: above all the Library of Pergamos, once the rival "
            "of Ptolemy's at Alexandria in Egypt. Pergamos took to "
            "parchment while Alexandria still wrote on papyrus, so "
            "Hermetic scholars hope codices survive in hidden rooms "
            "underground. Mark Antony gave most of its books to Cleopatra "
            "as a wedding gift, but Theban Seekers have turned up a few "
            "texts left behind.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "pergamos_library",
        "The Library of Pergamos",
        inside=acropolis,
        aura=2,
        summary=(
            "The ruined library on the upper acropolis, with a Magic aura "
            "of 2. Most of its scrolls went to Egypt with Cleopatra, but "
            "Seekers have found a few remaining texts, and secret rooms "
            "below may still hold parchment codices."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "pergamos_temples",
        "The Temples of Dionysus and Athena at Pergamos",
        inside=acropolis,
        realm="Faerie",
        aura=3,
        summary=(
            "Two ruined temples on the upper acropolis, one to Dionysus "
            "and one, the Sanctuary of Athena Polias Nikephoros, to "
            "Athena the Bringer of Victory; each has a Faerie aura of 3."
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "great_altar",
        "The Great Altar of Pergamos",
        inside=acropolis,
        realm="Faerie",
        aura=4,
        summary=secrets(
            paragraphs(
                "A huge open-air altar at the north of the acropolis, on a "
                "terrace above St John's basilica: about forty feet long, "
                "twenty deep and up to forty high, Ionic columns along "
                "three sides over four great friezes of the gods' war with "
                "the titans and the gods' family trees, and on the fourth "
                "side a long flight of steps up to the central podium. "
                "Christians shun it, for St John's Revelation calls it "
                "Satan's throne.",
                "Magi know it has a Faerie aura of 4, and guess it was once "
                "a magic site too, as the friezes show the faerie gods "
                "beating the magical titans. Its oddity: a Hermetic magus "
                "who casts a ritual spell standing on it needs no vis, the "
                "altar supplying the power. The cost is that a botch is "
                "tainted as if by Faerie vis, and even a good casting may "
                "have strange side effects. The locals think it evil and "
                "have run off magi before as demon worshippers, so, with "
                "vis plentiful in the Tribunal, it is little used; but "
                "Lucian and his Children of Olympos think it central to "
                "their plan to make pacts with the Greek gods.",
            ),
            paragraphs(
                "The altar is the lock on the prison of Klymene, Titaness "
                "of fame (Magic Might 50, see the Bestiary), one of the "
                "titanesses who stayed neutral in the Titanomachy and were "
                "bound away from Tartaros. A quirk of her binding lets "
                "magi draw on her power for their rituals. The bonds have "
                "a strength of 50, restored at each new year, and each "
                "ritual cast here wears them down by the pawns it would "
                "normally cost; if they fall to nothing within one year, "
                "the altar splits in two and she goes free.",
                "She thought her prison a kindness, gentler than Tartaros "
                "and shared with her sisters, and freed she has nowhere "
                "to go: she might go back to the Magic Realm, settle on a "
                "mountain of the Tribunal and upset all around her, or "
                "range the land freeing other titanesses to bring back "
                "their old revels.",
            ),
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "asklepieion",
        "The Asklepieion of Pergamos",
        inside=acropolis,
        aura=3,
        summary=paragraphs(
            "A sanctuary of Asklepios two miles south of the acropolis, "
            "built over a sacred healing spring. It began as an offshoot "
            "of the shrines at Epidauros and grew more famous in the "
            "second century through Galen of Pergamos, who studied and "
            "taught here and whose ideas still shape the medicine of 1220. "
            "It has a Magic aura of 3.",
            "Vis: 12 pawns of Corpus a year, as small clay body parts like "
            "the votive offerings of the sick. The book does not say who "
            "gathers them.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ------------------------------------------------------------------ Lydia


def _lydia(theban: Theban) -> None:
    region = theban.places["anatolia"]
    lydia = _add(
        theban,
        "lydia",
        "Lydia",
        inside=region,
        summary=paragraphs(
            "Mountain country south of the Troad, its Aegean shore a run of "
            "cliffs, sandy coves, bays and good harbours. The Hermus, one "
            "of the great rivers of Asia Minor, crosses it from the "
            "Anatolian mountains to the Bay of Smyrna. A Byzantine province "
            "since the fourth century, it was briefly overrun by the Turks "
            "more than once in the twelfth. Legend makes it the homeland "
            "of the Amazons and the scene of many of Herakles's labours.",
            "Its forests hide the cercopes, small blue-green monkeys said "
            "to descend from two prankster brothers Zeus changed into apes "
            "for tormenting Herakles. Each is a magical creature, rare and "
            "always met alone, and how they breed is a mystery to the "
            "Order; hard to find, they are prized as familiars by Theban "
            "magi.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "mount_pagus",
        "Mount Pagus",
        inside=lydia,
        aura=1,
        levels=[
            Builder.level(
                "The Camp of the Ghosts",
                3,
                notes=(
                    "A grid of plain cloth tents like the bivouac of "
                    "Alexander's army, where most of the covenant's ghosts "
                    "dwell, and Fides, its patron, among them."
                ),
            ),
            Builder.level(
                "The Stone Houses of Alexandria",
                5,
                notes=(
                    "At the heart of the tent camp: the fine stone "
                    "buildings of the covenant, the old Redcaps' homes, the "
                    "Tribunal's records and two Hermetic laboratories (one "
                    "in use); a dozen servants live here."
                ),
            ),
        ],
        summary=secrets(
            paragraphs(
                "A small mountain south of Smyrna, looking over the city "
                "and its bay, crowned by a ruined citadel whose walls and "
                "towers have crumbled to a shell. Alexandria only cleared "
                "the inside and built wooden houses for its staff, leaving "
                "the walls unmended so as not to draw soldiers' eyes. The "
                "citadel has a Magic aura of 1, and inside it lie two "
                "regiones, one within the other: the ghosts' tent camp "
                "(Magic 3) and, at its centre, the covenant's stone "
                "houses (Magic 5).",
                "A small Nicene garrison now holds the citadel, put there "
                "by the emperor to guard Smyrna against the Turks. The "
                "soldiers live in Alexandria's wooden houses, have turned "
                "out its covenfolk, and do not know that a regio lies "
                "inside the walls, which makes coming and going hard for "
                "the Redcaps.",
            ),
            "The glass submarine kept by Alexandria (an iron anima, see "
            "the Bestiary) is chained to one of its ships in Smyrna "
            "harbour, not here.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "nymphaeum",
        "The Palace of Nymphaeum",
        inside=lydia,
        summary=paragraphs(
            "An imperial palace ten miles south of Smyrna, built some forty "
            "years ago by Andronikos I Komnenos and now the residence "
            "Theodore Laskaris likes and uses best. The way to it runs "
            "through Smyrna's old agora, the oldest and most ruined "
            "quarter of the city.",
            "Lone travellers there are sometimes accosted by an old man who "
            "says he is Homer: he trails after them asking how his poems "
            "are faring and whether they would like a recitation, and "
            "runs off if threatened or if a crowd comes near. Some magi "
            "take him for a faerie playing Homer, who loved the banks of "
            "the nearby Meles; a few Jerbiton think he is the poet "
            "himself, made a magic human by becoming a legendary artist.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "artemis_temple",
        "The Temple of Artemis at Ephesus",
        inside=lydia,
        realm="Faerie",
        aura=2,
        levels=[
            Builder.level(
                "Diana's Temple",
                4,
                "Faerie",
                enter=(
                    "Step over the statue's broken head on the eve of "
                    "Diana's festival, 13 August"
                ),
                notes=(
                    "The temple whole and splendid, with a forest round it "
                    "where the faerie Diana hunts stags with her herd of "
                    "faerie deer."
                ),
            )
        ],
        summary=paragraphs(
            "Once among the greatest temples of the ancient world, built "
            "over a spring sacred to Cybele, the old Earth Mother; an "
            "arsonist burned it, and the Ephesians even refused Alexander's "
            "offer to rebuild. They went on making and selling images of "
            "Diana until St Paul, defied by the craftsmen, prayed and the "
            "goddess's stone statue burst into rubble, at which they "
            "converted.",
            "The shell stands on a hillside outside the city, most of its "
            "stone carried off for building, with a Faerie aura of 2; the "
            "statue's broken, mossy head lies in a corner. Stepping over "
            "it on the eve of Diana's festival leads into a Faerie regio "
            "of aura 4 where the temple stands whole. A faerie calling "
            "herself Diana lives there with her faerie deer as servants "
            "and invites visitors to hunt stags in the regio's forest. "
            "Women who hunt well get small prizes; men she lures by "
            "bathing in woodland pools, and any who look on her naked she "
            "attacks, setting her stags on them.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "seven_sleepers",
        "The Cave of the Seven Sleepers",
        inside=lydia,
        realm="Divine",
        aura=3,
        levels=[
            Builder.level(
                "The Sleepers' Regio",
                6,
                notes=(
                    "The old Magic regio, hard to enter but still there; "
                    "time is dilated inside."
                ),
            )
        ],
        summary=paragraphs(
            "A cave a few leagues outside Ephesus, a great pilgrimage site. "
            "In Decius's persecution seven Christians fled into it with "
            "Roman soldiers behind them and were sealed in; they lay down "
            "to sleep, and woke when an earthquake broke the seal, to find "
            "more than a century gone and the empire Christian. They lived "
            "long and were buried in the cave. The Qur'an tells the story "
            "too, oddly with a dog among them.",
            "The cave has a Divine aura of 3, which has replaced the Magic "
            "aura it once had; the old regio survives, hard to enter, with "
            "a Magic aura of 6 and dilated time. Alexandria's Redcaps think "
            "vis might be gathered there, but the gatherer would have to "
            "stay the night, with no knowing how long would pass outside.",
        ),
        **KNOWN_TRIBUNAL,
    )


# -------------------------------------------------------------- Thrakesion


def _thrakesion(theban: Theban) -> None:
    region = theban.places["anatolia"]
    thrakesion = _add(
        theban,
        "thrakesion",
        "Thrakesion",
        inside=region,
        summary=paragraphs(
            "Nicaea's southernmost theme, Thrakesion, running from Lydia to the Maeander and its fertile "
            "basin: the old Ionia and Caria, once thick with towns and "
            "ports along the Aegean. Centuries of war with the Turks have "
            "drawn its people into walled cities, Philadelphia the chief. "
            "The Maeander has been Nicaea's southern frontier since 1211, "
            "when Theodore Laskaris beat Kaykhusraw I of Rum at "
            "Antioch-on-the-Maeander.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "maeander",
        "The Maeander",
        inside=thrakesion,
        summary=paragraphs(
            "The longest river of Asia Minor, winding from the interior "
            "to the Aegean: fast and deep, if not always wide, so only "
            "small sailing or rowing craft can use it.",
            "One small tributary, of great interest to Redcaps, flows into "
            "a cave, and a boat that follows it through comes out on the "
            "Alfeios in Elis, on the western Peloponnese: an hour's sail "
            "for a journey of days across the Aegean. The underground "
            "river is magical in ways Hermetic theory cannot explain, and "
            "Redcaps just call it a natural Mercere Portal. Alexandria's "
            "glass submarine cannot use it, the Maeander being too muddy "
            "and narrow.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "tmolus_vineyard",
        "The Vineyard of Dionysus on Mount Tmolus",
        inside=thrakesion,
        realm="Faerie",
        aura=3,
        summary=paragraphs(
            "Of the many vineyards on the slopes of Mount Tmolus above "
            "Philadelphia, one has borne grapes for centuries, and its "
            "wine is unusually strong, above all for women. Hermetic "
            "inquiry shows it was once a festival ground of Dionysus, "
            "where satyrs and maenads (women driven to frenzy by wine) "
            "gathered. It has a Faerie aura of 3.",
            "Vis: its grapes can be distilled into Mentem vis, 1 pawn for "
            "each hundred gallons of wine. The book names no one who "
            "gathers it.",
            "No magus has found a satyr, though tales of them are many; "
            "the women of Philadelphia know that if enough of them get "
            "drunk and dance wildly, the satyrs come.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "antioch_maeander",
        "The Field of Antioch-on-the-Maeander",
        inside=thrakesion,
        summary=secrets(
            paragraphs(
                "The battlefield of 1211 where Nicaea's southern border was "
                "won. French and Greek chronicles agree the Turks were "
                "winning until Theodore Laskaris met Sultan Kaykhusraw "
                "himself; the sultan, on an enormous horse, struck the "
                "emperor down but was killed before he could finish him. "
                "The French say Laskaris did the killing; the Greeks tell "
                "of a strange French knight who came from nowhere and "
                "slew the sultan. That blow saved the empire and stilled "
                "the Turkish threat for years.",
                "The Tribunal whispers that the knight was a magus in "
                "disguise, which would be a gross breach of the Code. The "
                "field, at the far frontier, is not easy to reach. A "
                "senior magus may ask player magi to find out before the "
                "Tribunal of 1221.",
            ),
            "The magus who sets them on may suspect someone and want "
            "proof, or may be the knight himself, testing how easily the "
            "truth can be found.",
        ),
        **KNOWN_TRIBUNAL,
    )
    _add(
        theban,
        "sipylus",
        "Mount Sipylus",
        inside=thrakesion,
        summary=paragraphs(
            "A dead volcano some 5000 feet high near the Maeander's "
            "headwaters, seen from Smyrna and the coast, with a crater lake "
            "at its summit. Legend makes it the seat of Tantalus, son of "
            "Zeus, whose royal city on the peak was destroyed when he "
            "betrayed his father; his treasury is said to lie sunk under "
            "the lake's murky bed.",
            "Each version of his crime hints at lost lore. Diodorus says he "
            "told secrets learned from Zeus, which stirs Bonisagus who "
            "would break the Limits of magic; Pindar says he stole nectar "
            "and ambrosia, and Epidauros's magi wonder whether these could "
            "better a Longevity Ritual; a third tale, dear to Verditius, "
            "has him keep a golden automaton that guarded Zeus's temple on "
            "Crete. No seeker has yet found the treasury or any of its "
            "marvels.",
        ),
        **KNOWN_TRIBUNAL,
    )


# ---------------------------------------------- Paphlagonia and Pontus


def _black_sea(theban: Theban) -> None:
    region = theban.places["anatolia"]
    pontus = _add(
        theban,
        "pontus",
        "Paphlagonia and Pontus",
        inside=region,
        summary=paragraphs(
            "The southern shore of the Black Sea east of Bithynia: "
            "Paphlagonia in the west, Pontus in the east, both mountainous "
            "with only a thin strip of farmed and settled coast under thick "
            "broadleaf forest, mild in winter and muggy in summer. The "
            "Pontic mountains close it to the south, wooded and snowy most "
            "of the year, and the rivers cutting down through them make "
            "valleys rich in hazelnuts, plums, cherries and pears.",
            "The Komnenos brothers, Alexios and David, took both provinces "
            "soon after Constantinople fell, but in 1220 three powers share "
            "the coast: Nicaea as far as Amastris, midway along "
            "Paphlagonia; the Seljuks from Sinope, where Paphlagonia meets "
            "Pontus; and Trebizond in the far half of Pontus. The last "
            "real fighting was in 1214, when Theodore Laskaris took "
            "Amastris, and all has been quiet since. Merchants of all "
            "three meet to trade, all three great cities have Genoese and "
            "Venetian trade agreements, and foreigners pay only a tax on "
            "what they bring in.",
        ),
        **KNOWN_REGION,
    )
    _add(
        theban,
        "trebizond_gardens",
        "The Gardens of Trebizond",
        inside=pontus,
        summary=secrets(
            paragraphs(
                "Trebizond's beauty has given rise to several Magic auras, "
                "most of them in the city's gardens and arboretums (the "
                "book gives no strengths). Magic has soaked into the "
                "plants, and the city has many magical herbs, fruits and "
                "hardwoods: one grove's bark is as hard as iron and must "
                "soak in water a year before it can be worked, and "
                "Aristotle wrote of some of them, among them a vine "
                "dripping honey that cures madmen and epileptics.",
                "Vis: several of the plants would give vis each year if "
                "harvested properly. Unclaimed; Ingasia is buying "
                "Trebizond oak for its new buildings.",
                "Lately bardi have plagued the city: shapeshifting spirits "
                "in the form of a she-jackal, solitary, whose wail "
                "foretells a death. The clergy call them demons, the "
                "townsfolk faeries; no magus has caught one to study. "
                "Their warnings are uncannily true: everyone who has seen "
                "the jackal and heard it wail has soon lost someone dear.",
            ),
            "Fishermen of the docks have lately seen a huge, savage shark "
            "off the shore that has killed several men who tried to kill "
            "it, and they are sure it hunts the Pearl of Peroz, which must "
            "be somewhere in the city. That pearl, the greatest ever seen, "
            "hung from the ear of King Peroz of Persia, who marched into "
            "eastern Anatolia against the Ephthalite Huns in the fifth "
            "century. A fisherman found it by watching a monstrous shark "
            "follow an oyster that showed it its pearl; he threw the "
            "oyster ashore and was eaten, and the shark haunted the king "
            "whenever he went near the sea. Peroz, falling into a trench "
            "his enemies had dug, tore the pearl from his ear and threw "
            "it away rather than be buried with it; it has turned up now "
            "and then since, and whoever bears it near water soon meets "
            "the shark. The fishermen think the shark magical and the "
            "pearl mighty.",
        ),
        **KNOWN_LOCALLY,
    )
    _add(
        theban,
        "serapis_shrine",
        "The Hidden Shrine of Serapis at Sinope",
        inside=pontus,
        realm="Infernal",
        status="Rumoured",
        known="Locally",
        summary=secrets(
            "Somewhere deep under Sinope, a heretical Christian sect meets "
            "in secret. The book gives no aura.",
            paragraphs(
                "The sect has put Serapis in God's place. Alexander brought "
                "the god into Anatolia from Babylon; after his death Ptolemy "
                "took the cult statue to Egyptian Alexandria and blended "
                "Serapis with Egypt's gods to make one deity, and under "
                "Hadrian Egyptian Christians began worshipping him. The "
                "sect was thought stamped out in the fourth century, but "
                "the statue survived and its last followers smuggled it to "
                "Sinope, where it has stayed.",
                "Serapis is a False God (see the Christians of Serapis).",
            ),
        ),
    )


# ------------------------------------------------------------- Alexandria


def _alexandria(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    site = theban.places["mount_pagus"]
    summary = paragraphs(
        "The Mercere covenant of the Tribunal, of the Kretan phyle, and the "
        "hub of its bureaucracy and its news: home to most of the Theban "
        "Redcaps and a retreat for those too old or too Warped to ride "
        "any more. Its stone houses stand in a regio inside the ruined "
        "citadel on Mount Pagus above Smyrna, which a Nicene garrison now "
        "occupies. It is an Autumn covenant.",
        "It is the second all-Mercere covenant of Thebes. The first, "
        "Miphoria, on the shore outside Smyrna, travelled by marvellous and "
        "open magic, riding giant magical sea turtles among other things; "
        "the Tribunal judged it drew mundane eyes to the Order and told "
        "it to lie low, and without its turtles it withered, most of its "
        "Redcaps living in other covenants by 1063. A central house had "
        "made the Redcaps' paperwork far easier, so a second was thought "
        "wise.",
        "Methodius, then the best-loved Redcap of the Tribunal, who claimed "
        "Alexander's blood and had won fame by finding Alexander's flying "
        "device in Seljuk lands, chose the old fortress on Mount Pagus, "
        "with its Magic aura and regiones, though Alexander's ghostly "
        "soldiers haunted it. He bound an eidolon living among the ghosts "
        "as patron, left the broken walls alone to avoid soldiers' notice, "
        "built in wood in the aura and in stone in the regio, finished in "
        "1075, and named the covenant after the many cities of his "
        "ancestor.",
        "Centralised Redcap work and trade treaties with the nations "
        "round the Aegean made it rich; Seekers it paid found the glass "
        "submarine, a second of Alexander's relics, and the pair drew "
        "Philagrius of Verditius, who found both were mechanica made by "
        "Heron's heirs. But the strong Longevity Rituals its members took "
        "warped them: many lived very long and gathered magical Flaws, "
        "shunned the world and hid in the regio, and the covenant that "
        "had been known for bold merchant venturers and shrewd "
        "politicians came to be seen as a home for odd old Redcaps.",
        "It still does its work, but the fall of Constantinople has cost "
        "it. Petronas, logothete for nearly a century, gave up the post at "
        "the Tribunal of 1207, and his successor Leontius has done badly, "
        "barely escaping ostracism in 1214; and the emperor's soldiers now "
        "sit in its outer houses. Its fifteen members are all unGifted "
        "Redcaps but one, the Bonisagus maga Catella: five elders past 130, "
        "much twisted by Warping, who live in the regio retelling old "
        "exploits, taunting the ghosts and needling each other; five in "
        "middle age (sixty to a hundred, Warping 3 to 5), who run the "
        "covenant, its trade and the Tribunal's records and hold the "
        "better posts; and five young ones who live in Smyrna or farther "
        "off and ride as messengers and heralds, building the standing "
        "for weightier work.",
    )
    what_matters = _lines(
        "Purpose: to give the Tribunal's bureaucracy a central seat and its Redcaps a safe, handy home",
        "Boon: Powerful Ally (Fides, the covenant's patron)",
        "Boon: Regio (two levels inside the citadel, Magic 3 and 5)",
        "Boon: Wealth (trade treaties round the Aegean, warehouses and three ships at Smyrna)",
        "Hook: Mercer House; Hermetic Services (the Tribunal's records and the logothete's register)",
        "Hook: Haunted (the ghosts of Alexander's army); Crumbling (the citadel's walls left unmended)",
        "Hook: Mundane Politics (a Nicene garrison holds the outer citadel; food must be smuggled in and members slip in and out)",
        "Hook: Hermetic Politics (the logothete's failure and succession)",
        "Vis: no source of its own is named; its Redcaps are rich enough in vis to buy strong Longevity Rituals, and borrowers of its artifacts pay 1 pawn a week",
        "Vis: the Seven Sleepers' regio near Ephesus, a possible source its Redcaps have only speculated about",
        "Income: merchant trade through its warehouses and three ships in Smyrna harbour",
        "Library: the records of the Theban Tribunal and the register of tokens and shards",
        "Enchantments: Alexander's flying device (a ReTe 39 mechanica, idle since its flying horses escaped two years ago), the glass submarine (an anima, see the Bestiary), and small items for travelling Redcaps",
        "Tension: Leontius has lost records and kept a faulty register; he will resign in 1221 and the Redcaps mean to propose Proximios",
        "Tension: Catella wants the artifacts for her research, but must lend them out",
        "Tension: the garrison could find the regio at any time",
    )
    notes = paragraphs(
        "The patron. Fides is an eidolon, the spirit of loyalty born of "
        "the steadfast devotion of Alexander's soldiers to their king. "
        "When he died and his empire fell apart she stayed among the "
        "troops, and found those posted at Smyrna the most devoted; the "
        "most loyal of them became ghosts, held by their slavish faith in "
        "Alexander's idea of empire, and she thrives among their tents on "
        "the regio's first level. Methodius bound her on the promise that "
        "the covenant would go on honouring Alexander and his empire, and "
        "tied that to the Tribunal: she is content with the 'Hermetic "
        "Empire of Thebes' in place of world conquest, and will stay as "
        "long as the members stay loyal to it and to the Order. Chapter "
        "three, in passing, instead says Alexandria reveres the spirit of "
        "a grove of myrrh trees; the covenant's own section names Fides.",
        "The artifacts. Alexander's two relics belong to the covenant: any "
        "member may use them, and they may be lent to any Theban magus "
        "whose tokens outnumber his shards, against a deposit of vis or "
        "valued magic items that grows with the length of the loan, plus "
        "1 pawn of vis a week, and must come back on time. The flying "
        "device is a two-wheeled chariot with waist-high rails and a long "
        "hitch, a mechanica with one power: it rises into the air as "
        "lightly as smoke but cannot be steered, drifting on the wind, "
        "unless flying beasts with a total Size of +8 are yoked to it "
        "(the hitch takes four, the car six riders of Size 0); the tale "
        "of Alexander's gryphons is unproven. Its horses, each shod with "
        "a magic flying shoe, escaped two years ago, shoes and all. The "
        "glass submarine is a living iron dolphin the size of an "
        "elephant, holding five riders, chained by six hundred feet of "
        "iron to a guarded ship in Smyrna harbour that is used like any "
        "other merchant vessel to avoid suspicion; only someone with "
        "Mechanica or Automata can repair it, which Catella lacks, though "
        "a few Theban Verditius have Automata. Redcaps keep the lesser "
        "items given to them: water-shedding cloaks, vis gauges, flasks "
        "that keep wine sweet.",
        "Covenfolk. A dozen servants and cooks, not fighters, live in the "
        "inner regio; two dozen more work the warehouses, docks and ships "
        "in Smyrna on good pay and are fairly loyal. The covenant gives "
        "its staff a feast each year in a private house in Smyrna; most "
        "of the town workers have never been to Alexandria or met its "
        "strange-looking elders.",
        "Founded: the site was chosen after Miphoria failed (by 1063) and "
        "the building was finished in 1075, the year given here.",
        "Members: fifteen Redcaps and Catella. Leontius and Proximios are "
        "named; the book names none of the other Redcaps of Alexandria, "
        "kept here as thirteen unnamed members. Lysandros, Diantha and "
        "Niko, the Redcaps of chapter three, have no covenant in the "
        "book and may be among them.",
        secrets(
            STORYGUIDE,
            _lines(
                "Proximios, the likely next logothete and co-founder of the League of the Vigilant, is secretly an infernalist bent on the Order's downfall; his place at Alexandria lets him read the missives and private letters that pass through it (see his entry and An Enemy Within).",
                "The garrison does not know of the regio; if it finds it, the covenant's secrecy and the Tribunal's records are at risk.",
            ),
        ),
    )
    alexandria = b.covenant(
        "Alexandria",
        tribunal=tribunal,
        founded=1075,
        place=site,
        level=2,
        aura=5,
        realm="Magic",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=13,
        detail=FULL,
        season="Autumn",
    )
    theban.covenants["alexandria"] = alexandria
    _alexandria_magi(theban, b, alexandria)
    b.book(
        alexandria,
        "The records of the Theban Tribunal",
        "Other",
        language="Classical Greek",
        description=(
            "The book names no books. Alexandria's stone houses in the "
            "inner regio are the storehouse of the Tribunal's records, kept "
            "by its middle-aged Redcaps, and the logothete keeps the "
            "register of every polites's tokens and shards and of each "
            "neutralization a Redcap has witnessed. Under Leontius records "
            "have gone astray, lists have vanished and the register has "
            "been found faulty."
        ),
    )


def _alexandria_magi(theban: Theban, b: Builder, home: Covenant) -> None:
    m = theban.magi
    m["leontius"] = b.magus(
        "Leontius",
        covenant=home,
        house=MERCERE,
        age=132,
        summary=paragraphs(
            "The logothete, the Tribunal's Chief Redcap since Petronas "
            "stepped down in 1207: a tall, thin, unGifted man with a "
            "receding hairline and a long grey moustache, who looks "
            "eighty-two. An old Supernatural Virtue gives him the full "
            "benefit of a Longevity Ritual as a magus would have it, but "
            "Warping has lately given him his first Major Flaw: to his "
            "shame, the Curse of Lycaon. He turns into a wolf not at the "
            "full moon but when he grows too anxious.",
            "He regrets ever taking the post. For all his efforts, records "
            "have gone astray, lists have vanished, and the register of "
            "tokens and shards, the most important book of all, has been "
            "found wrong; he scraped past ostracism in 1214, knows the "
            "Tribunal is unhappy, and means to resign at the next meeting.",
        ),
        traits={"Worried": 3},
    )
    m["proximios"] = b.magus(
        "Proximios",
        covenant=home,
        house=MERCERE,
        age=91,
        summary=secrets(
            paragraphs(
                "An unGifted Redcap who looks forty-two: broad in the "
                "shoulder, handsome, his dark hair neatly combed. He is of "
                "the blood of Andreas, a mythic hero of Justinian's "
                "Persian Wars, a gymnast rather than a soldier, who beat "
                "two armoured Persian champions hand to hand; from him "
                "Proximios has astonishing gifts, near-legendary feats of "
                "tumbling among them. As a young messenger he dazzled the "
                "magi he carried letters to with his acrobatics, and "
                "Lucian of Aegaea loved the show.",
                "He is known as a quick, capable politician, though he has "
                "never held office and has always been somebody's "
                "assistant; so deep in Tribunal business is he that for "
                "twenty years he has been let off ordinary Redcap duty and "
                "carries no messages. It was his idea, in 1186, to make "
                "the logothete's post permanent instead of seven years, "
                "for continuity and so no newcomer need learn the records "
                "afresh, and it pleased those who complain the Tribunal's "
                "officers change too often. Many Redcaps want him as the "
                "next logothete and will propose it in 1221; he neither "
                "seeks nor refuses it, and most think that is humility.",
                "With Hydatius of Ingasia he founded the League of the "
                "Vigilant, paying for it and supplying its magic while "
                "Hydatius leads it. He backs Ziper's wish to take the "
                "craftsmen Nanno and Ampelius into Moero's Garden, "
                "pointing to how well his own House of unGifted folk "
                "serves the Order.",
            ),
            paragraphs(
                "Proximios is an infernalist, unknown to anyone: a master "
                "of the Unholy Method of Incantation and the Unholy Power "
                "of Diablerie, with a long list of demons' True Names. He "
                "uses summoned demons as spies and lures, and sets "
                "Tempters and Evil Spirits to drive his fellows to sin. He "
                "means to bring down the Order, starting in Thebes, and "
                "works slowly and covertly among magi who would spot "
                "anything blatant, seeking a weak link in every covenant; "
                "his post at Alexandria shows him the letters and missives "
                "passing through. Neither Method nor Power is on his "
                "generated sheet: the storyguide adds them.",
                "He set up the League of the Vigilant to aim it, in time, "
                "at innocent magi who look like diabolists (Caterina da "
                "Vigonovo, young magi of Erebos, nosy Delfini of Aegaea), "
                "sending league members to look into them, never going "
                "himself, and then having a demon dressed as Hydatius "
                "order an attack. He would turn Aiakia, or more easily "
                "the hotter Tisiphon, against Gigas by blaming its Tremere "
                "for Constantinople's fall, and set Celaenea, who adores "
                "Hermes, against Lucian's Children of Olympos; the demon "
                "Moreto has told him an infernalist planted in that league "
                "could make it raise a False God in place of a faerie.",
                "In 1220 these plans are only forming. He will take the "
                "logothete's post, seeming reluctant so the blame falls "
                "elsewhere when things unravel, and use the register of "
                "tokens and shards to reward those who cooperate. He has "
                "not yet recruited magi, but has his eye on a few who "
                "might be tempted. His plots always look like someone "
                "else's work; the book suggests him as a saga's chief "
                "enemy, his threat growing slowly over the years (see An "
                "Enemy Within).",
            ),
        ),
        traits={"Intense": 3, "Eloquent": 2, "Humble": 2},
    )
    m["catella"] = b.magus(
        "Catella",
        covenant=home,
        house=BONISAGUS,
        age=41,
        summary=paragraphs(
            "The only Gifted member of Alexandria, who looks thirty-nine. "
            "She came straight from her Gauntlet, two years before "
            "Constantinople fell, while the covenant's name was still good, "
            "drawn by Alexander's artifacts; in some twenty years of study "
            "she has got little further with them.",
            "Because of that interest she was made keeper of the "
            "artifacts and their loans, which both thrills and galls her: "
            "she loves having charge of them but hates that they are often "
            "out when she wants to study them. Alexandria has chosen to "
            "lend them freely, and she abides by it even when it upsets her "
            "own plans. She has no Mechanica yet, so cannot mend the glass "
            "submarine. She would also dearly like Hagia Sophia in "
            "Constantinople studied for insights from Heron's theories, and "
            "will fund any magus with a way to do it.",
        ),
        traits={"Patient": 3, "Cheerful": 1, "Determined": 1},
    )


# --------------------------------------------------------- Moero's Garden


def _moeros_garden(theban: Theban, b: Builder, tribunal: Tribunal) -> None:
    site = _add(
        theban,
        "hipparchus_house",
        "The House of Hipparchus",
        inside=theban.places["bithynia"],
        realm="Divine",
        aura=2,
        summary=paragraphs(
            "The ancestral house of Hipparchus of Nicaea, the Greek "
            "astronomer of about 190 BC, in a merchants' quarter in a "
            "corner of Nicaea: three storeys about an outer and an inner "
            "courtyard, palatial by merchants' standards and squalid, "
            "cramped and undignified to the magi of Moero's Garden, who "
            "fled here in 1204 and have struggled to make it beautiful. "
            "Laboratories fill the top floor, the magi live on the "
            "second, the covenfolk on the ground floor, and the library "
            "and works of art are kept, to the magi's horror, in the "
            "basement.",
            "It lies in a Divine aura of 2, no great obstacle to the magi "
            "but hard on their apprentices, who struggle to cast and to "
            "finish their training here.",
        ),
        **KNOWN_TRIBUNAL,
    )
    summary = paragraphs(
        "A covenant of Jerbiton magi, of the Propontian phyle, living in "
        "the House of Hipparchus in Nicaea, the new capital of the exiled "
        "empire: aristocratic and effete, driven from their first home in "
        "Constantinople and longing to go back, filling the time with art "
        "and gracious living. It has eight magi, seven Jerbiton and one "
        "Tytalus with the Gentle Gift, and the League of Constantine meets "
        "here.",
        "Ionnia of Jerbiton, a minor Byzantine noble with a love of women "
        "poets, founded it in 1163, in Manuel Komnenos's golden years, "
        "after seeking out the house of the poet Moero (about 300 BC) in "
        "the old quarters of Constantinople; it lay in one of the city's "
        "lacunae, and she summoned Moero's ghost to be patron. She "
        "gathered sodales, all Jerbiton of aristocratic family, to find "
        "the literature and art of the early Byzantine age, a task her "
        "House thinks very worthy. A member may not work for a living, "
        "like a Roman senator or Byzantine noble: income must come from "
        "land others till. It flourished, and its magi had leisure for "
        "letters and art.",
        "In Constantinople its magi went to court functions but kept the "
        "imperial family and politicians at arm's length, spending their "
        "effort on their covenant, costly travel and visits to the "
        "Tribunal's old buildings and paintings, sure that staying out "
        "of the emperor's politics would keep them safe. When the "
        "crusaders took the city it escaped the first ruin, but fearing "
        "for its library and treasures it fled with most of the rich "
        "Greeks, carrying what it could and leaving most behind, to its "
        "chapter house in Nicaea, Hipparchus's old summer home, which is "
        "now all it has.",
        "Its first purpose was to gather the finest art and writing of "
        "the past to show the calm, intellectual delight of beauty, "
        "cooling hot tempers and spreading serenity through the Order; "
        "since 1204 it also seeks to win back what it lost. Its magi "
        "think, like nobles, that they should not have to work, and "
        "that gets harder the longer they are away from Constantinople. "
        "Four of the seven Jerbiton belong to the League of Constantine "
        "and want the covenant to help the Nicene emperor retake the "
        "city; the youngest, Trasaric and Helladius, say it fell because "
        "the covenant idled; Ionnia and Syagricus answer that the city "
        "has come through disasters before and this occupation will pass "
        "too. The covenant is evenly split.",
    )
    what_matters = _lines(
        "Purpose: to collect the art and literature of the past to show the harmony of beauty, and to recover what was lost in 1204",
        "Boon: Local Ally (Hipparchus's ghost, the covenant's patron)",
        "Boon: Secondary Income (the craftsmen and artists of Nicaea that its autocrat backs)",
        "Hook: Urban (a merchants' quarter of Nicaea, in a Divine aura of 2)",
        "Hook: Poverty (Minor) (its finances are dwindling); Dwindling Resource (its vis stores)",
        "Hook: Refugee (driven out of Constantinople in 1204)",
        "Hook: Resident Nuisance (the patron's ghost torments the covenfolk)",
        "Vis: one source found to replace the many it lost round Constantinople (the book does not say which); most of its vis is gifts from other Theban magi",
        "Vis: its magi found the rite that makes the Serpent Column in Constantinople's Hippodrome yield 8 pawns of Animal vis a year",
        "Income: the craftsmen it has set up, chief among them Nanno, a maker of wondrous cosmetics, and Ampelius, a master of religious murals",
        "Library: Kassia's poetry, gathered by Ionnia; her own summae and tractatus on Rego and Mentem; her poems",
        "Allies: the League of Constantine, centred here",
        "Tension: the covenant is split four to four on helping the emperor retake Constantinople; Pancratius, due his Gauntlet in 1221, may tip it",
        "Tension: Ziper, backed by Proximios, wants Nanno and Ampelius made unGifted Jerbiton members; all but Syagricus are appalled, and the pair threaten to ask the Tribunal at Delos",
        "Hook: the magi know a secret way under the Theodosian Walls near the Gate of Pege and often send searchers into Constantinople for lost art and relics",
    )
    notes = paragraphs(
        "The patrons. Moero's ghost is still bound at the old site in "
        "Constantinople, but the Tribunal requires a covenant's patron to "
        "live within it, so Ionnia had to summon and bind a second, the "
        "ghost of Hipparchus, against its will. It is weak in Might and "
        "resents being woken from centuries of sleep, so it torments "
        "whoever it can, chiefly the covenfolk, the magi being too strong "
        "for it: pulling hair, knocking over wine bowls, snuffing lamps. "
        "When it grows unbearable Ionnia calms it by spending an evening "
        "with it watching the stars and talking astronomy, which settles "
        "it for a week or so.",
        "Covenfolk. About forty craftsmen and servants work for the "
        "covenant. The autocrat Pastor runs its daily business and "
        "finances, now shrinking, and its ever smaller vis stores; to "
        "make up the losses he has used most of the treasury to back "
        "craftsmen and artists of Nicaea, who have grown rich and now "
        "give much of the covenant's income. Two of them can make "
        "enchanted goods: Nanno, who makes wondrous cosmetics, and "
        "Ampelius, who paints breathtaking religious murals. The magi "
        "like the money but shudder that it comes from craftsmen; "
        "Ampelius, being an artist, is held in better regard. Pastor's "
        "wife Viviana is the chief scribe and keeper of the library.",
        "Apprentices: three of the Jerbiton have apprentices nearly ready "
        "for their Gauntlet; Syagricus's Pancratius hopes for his at the "
        "Tribunal of 1221 and will likely join as a full member.",
        "Season: the book gives none; Autumn is the pack's reading of a "
        "covenant living on dwindling means away from its old riches.",
        "Members: eight magi. Ionnia, Syagricus, Ziper, Trasaric and "
        "Helladius are here; Evantia, the most respected of the Seekers of "
        "the Fallen, is with the realms; the two other Jerbiton are "
        "unnamed. Krum the Swift of Aegaea was a member in "
        "Constantinople.",
    )
    garden = b.covenant(
        "Moero's Garden",
        tribunal=tribunal,
        founded=1163,
        place=site,
        aura=2,
        realm="Divine",
        summary=summary,
        what_matters=what_matters,
        notes=notes,
        unnamed_magi=2,
        detail=FULL,
        season="Autumn",
    )
    theban.covenants["moeros_garden"] = garden
    _garden_magi(theban, b, garden)
    _garden_library(b, garden)


def _garden_magi(theban: Theban, b: Builder, home: Covenant) -> None:
    m = theban.magi
    m["ionnia"] = b.magus(
        "Ionnia",
        covenant=home,
        house=JERBITON,
        age=107,
        summary=paragraphs(
            "The founder: a tall maga with thin white hair and dull blue "
            "eyes, who looks ninety-one and wears rich robes, gold "
            "necklaces, jewelled rings and bracelets crusted with gems. "
            "Before Moero's Garden she won a great name in House Jerbiton "
            "by collecting every poem of Kassia, the ninth-century nun "
            "who is the empire's most famous woman poet. A master of Rego "
            "and Mentem, she summons and questions ghosts in her hunt for "
            "old poetry.",
            "Longevity Rituals have never worked well for her, and she is "
            "very frail and near her end, which does not trouble her: "
            "though she grieves for the old site, she is content with "
            "idle pleasures, letters to her two living daughters and "
            "early evening company. She has served the Tribunal before "
            "but says she is too old for politics now; still, she means "
            "to go to Delos for the next meeting to offer vis to the "
            "covenant's patron. She soothes Hipparchus's ghost with "
            "evenings of star-gazing.",
        ),
        traits={"Poetic": 3, "Blunt": 2, "Frivolous": 2},
    )
    m["syagricus"] = b.magus(
        "Syagricus",
        covenant=home,
        house=JERBITON,
        age=102,
        summary=paragraphs(
            "The oddest Jerbiton of the covenant in body and temper, who "
            "looks forty-three: a true hermaphrodite, medically proven, "
            "proud of it, who dresses to show both natures, with a full "
            "beard and a gown that shows off his bust. He calls his "
            "nature beautiful and will not hide it; his sodales accept it "
            "but wish he spoke of it less. He takes his Longevity Ritual "
            "gladly, a daily draught of herbs and powders at noon, and is "
            "hale.",
            "He shares his sodales' love of art, manners and comfort, but "
            "cares more for winning back the covenant's lost art than for "
            "pleasure: he belongs to Valnastium's league of New "
            "Iconophiles and goes to Constantinople at least once a year "
            "to hunt for the missing pieces. He sides with Ionnia against "
            "the League of Constantine, and is the only one besides Ziper "
            "not appalled at taking in Nanno and Ampelius. His apprentice "
            "Pancratius is due his Gauntlet at the Tribunal of 1221 and "
            "will probably join; Trasaric and Helladius hope he will vote "
            "with them.",
        ),
        traits={"Outspoken": 3, "Opinionated": 2, "Kind": 1},
    )
    m["ziper"] = b.magus(
        "Ziper",
        covenant=home,
        house=TYTALUS,
        age=129,
        summary=paragraphs(
            "The eldest of Moero's Garden, who joined only after it moved "
            "to Nicaea, a Tytalus with the Gentle Gift. Stooped, wrinkled "
            "and wholly bald, in white robes under a red toga, he looks "
            "sixty-five and venerable, but has the energy and sharpness "
            "of a young man.",
            "He thinks the covenant too small to carry weight in the "
            "Tribunal and has proposed taking the craftsmen Nanno and "
            "Ampelius in as members of House Jerbiton: they are not magi, "
            "but can put minor enchantments in their work. Proximios of "
            "Alexandria backs him. Everyone else but Syagricus is "
            "appalled, less because the pair are unGifted than because "
            "they are craftsmen. The book once calls Ziper a maga but "
            "elsewhere 'he'; the pack follows the latter.",
        ),
        traits={"Conniving": 3, "Obsequious": 3, "Busybody": 2},
    )
    m["trasaric"] = b.magus(
        "Trasaric",
        covenant=home,
        house=JERBITON,
        age=None,
        summary=(
            "One of the two youngest magi of Moero's Garden and of the "
            "League of Constantine, who holds that Constantinople fell "
            "because the covenant's magi idled instead of defending their "
            "homeland, and wants it to help the Nicene emperor take the "
            "city back. He hopes Pancratius, once Gauntleted, will tip the "
            "vote his way. The book gives only his name and this stand."
        ),
    )
    m["helladius"] = b.magus(
        "Helladius",
        covenant=home,
        house=JERBITON,
        age=None,
        summary=(
            "With Trasaric the youngest of Moero's Garden and a member of "
            "the League of Constantine: he too blames the city's fall on "
            "the covenant's idleness and wants to back the emperor of "
            "Nicaea against the Latins, and courts Pancratius's future "
            "vote. The book gives only his name and this stand."
        ),
    )


def _garden_library(b: Builder, garden: Covenant) -> None:
    b.book(
        garden,
        "The poems of Kassia",
        "Other",
        language="Greek",
        author="Kassia",
        description=(
            "Ionnia's famous collection of the complete poetry of Kassia, "
            "the ninth-century nun who is the best-known woman poet of the "
            "empire, the heart of the covenant's library. Its gathering "
            "made Ionnia's name in House Jerbiton. Much of the library was "
            "left in Constantinople in 1204; what came is kept in the "
            "basement by the scribe Viviana."
        ),
    )
    b.book(
        garden,
        "Ionnia's summa on Rego",
        "Art Summa",
        art="Rego",
        language="Classical Greek",
        author="Ionnia of Jerbiton",
        description=(
            "One of the several summae and tractatus on Rego and Mentem "
            "Ionnia has written; the book gives no levels or qualities."
        ),
    )
    b.book(
        garden,
        "Ionnia's summa on Mentem",
        "Art Summa",
        art="Mentem",
        language="Classical Greek",
        author="Ionnia of Jerbiton",
        description=(
            "Ionnia's summa on the Art of the mind, by which she calls up "
            "and questions ghosts; the book gives no level or quality."
        ),
    )
    b.book(
        garden,
        "Ionnia's tractatus on Rego and Mentem",
        "Tractatus",
        art="Mentem",
        language="Classical Greek",
        author="Ionnia of Jerbiton",
        description=(
            "Ionnia's tractatus on her two Arts, entered as one record; the "
            "book gives neither their number nor their quality."
        ),
    )
    b.book(
        garden,
        "Ionnia's poems",
        "Other",
        language="Greek",
        author="Ionnia of Jerbiton",
        description=(
            "Tractatus of Ionnia's own poetry, kept with the covenant's "
            "great collection of verse."
        ),
    )


# ------------------------------------------------------- the mundane world


def _lords(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    region = p["anatolia"]
    w["emperor_of_nicaea"] = b.lord(
        "Emperor of Nicaea",
        title="duke",
        wealth="Wealthy",
        seat="Nicaea",
        ruler="Theodore I Laskaris",
        place=p["bithynia"],
        summary=paragraphs(
            "Theodore Laskaris, who fought bravely for Constantinople in "
            "1204 and then fled to Nicaea, where so many great Byzantines "
            "followed that he could hold a court as splendid as the old "
            "one. He named Michael Autoreianos patriarch in 1205, and was "
            "crowned emperor in 1208; he has sworn to retake "
            "Constantinople and to keep the empire alive at Nicaea until "
            "he does. The book calls him Theodore II; history has him as "
            "Theodore I, so the pack does too.",
            "Shrewd at turning neighbours to his use, he has been friend "
            "and foe in turn to the Latins, the Bulgarians and the "
            "Sultanate of Rum; Frankish mercenaries stiffen his army while "
            "he recruits native Anatolians. He is best known for beating "
            "the Sultan of Rum in single combat in 1211, for seizing and "
            "imprisoning his treacherous father-in-law Alexios III, and "
            "for driving along the Black Sea to check Trebizond. His "
            "cabinet rule is leaner than the old bureaucracy, the taxes "
            "that once went to Constantinople pour into Nicaea, his "
            "soldiers are content after years of victories, and art and "
            "learning flourish.",
            "A staunch Orthodox, he is nonetheless open to Church union: "
            "he would put the Eastern Church under Rome for a time to win "
            "Constantinople, the pope has hinted that would do, and in "
            "1220 he has gathered churchmen to end the schism, if he can "
            "bring the patriarch and Anatolia's bishops round. His peace "
            "with the Latins, sealed by marrying Marie de Courtenay in "
            "1219, has broken, and he is about to fall on Holkos. His navy "
            "is based at Smyrna, and his favourite residence is the Palace "
            "of Nymphaeum; his soldiers occupy Alexandria's citadel.",
        ),
    )
    nicaea = w["emperor_of_nicaea"]
    w["sultan_of_rum"] = b.lord(
        "Sultan of Rum",
        title="duke",
        wealth="Wealthy",
        seat="Konya",
        ruler="Kayqubad I",
        place=region,
        summary=paragraphs(
            "The Seljuk Sultanate of Rum holds the Anatolian plateau, lost "
            "to the empire after Manzikert, and in the north reaches the "
            "Black Sea at Sinope, splitting Nicaea from Trebizond. It drove "
            "north between them in 1214, killing David Komnenos, but could "
            "not reach Trebizond through the mountains. Its sultan "
            "Kaykhusraw I died at Antioch-on-the-Maeander in 1211, and the "
            "Maeander has been the border with Nicaea since. Trebizond "
            "still fears it.",
            "The book names no sultan for 1220. History has Kaykhusraw's "
            "son Kaykaus I reign from 1211 to his death about 1220, "
            "followed by his brother Kayqubad I, who is named as ruler "
            "here.",
        ),
    )
    rum = w["sultan_of_rum"]
    w["lord_of_sinope"] = b.lord(
        "Governor of Sinope",
        title="landed",
        wealth="Wealthy",
        seat="Sinope",
        ruler="Etoumes",
        answers_to=rum,
        place=p["pontus"],
        summary=secrets(
            "Etoumes, a Greek and a vassal of the Seljuk sultan, though no "
            "Muslim himself, who governs Sinope and pays tribute to Rum. "
            "He is on good terms with Alexios of Trebizond. He has lately "
            "taken a new confessor.",
            "The confessor is a priest of the Christians of Serapis, to the "
            "demon's delight; nothing good can come of it.",
        ),
    )
    w["emperor_of_trebizond"] = b.lord(
        "Emperor of Trebizond",
        title="duke",
        wealth="Wealthy",
        seat="Trebizond",
        ruler="Alexios I Komnenos",
        place=p["pontus"],
        summary=paragraphs(
            "Alexios Komnenos, thirty-eight, grandson of the Emperor "
            "Andronikos Komnenos, who seized Trebizond with his brother "
            "David in 1204, the very year Constantinople fell, and calls "
            "himself 'Emperor and Autocrat of the Romans'. David pushed "
            "west into Paphlagonia and Heraclea, provoking Rum and then "
            "Nicaea, which won back most of his gains in 1212; Rum killed "
            "him in 1214. Alexios rules on, propped by Georgian troops and "
            "Latin and Seljuk mercenaries, cut off from Nicaea and still "
            "threatened by Rum, and also rules Cherson and Kerch across "
            "the Black Sea; Cherson pays him tribute.",
            "He lives with his family in the castle behind the city. Like "
            "his grandfather he patronises art and letters, giving titles "
            "and stipends to astronomers, alchemists and experimental "
            "philosophers, and his Silk Road market and its taxes make "
            "Trebizond very rich.",
        ),
    )
    w["amastris_border"] = b.lord(
        "Nicene Governor of Amastris",
        title="landed",
        seat="Amastris",
        answers_to=nicaea,
        place=p["pontus"],
        summary=(
            "Amastris, taken by Theodore Laskaris in 1214, marks the "
            "eastern end of the Empire of Nicaea on the Black Sea. It "
            "pays tribute to the emperor and governs itself as best it "
            "can; the book names no governor."
        ),
    )


def _churches(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["orthodox_patriarch"] = b.church(
        "The Orthodox Patriarchate at Nicaea",
        church="Archbishop's cathedral",
        ruler="Manuel I Charitopoulos, Patriarch",
        place=p["bithynia"],
        summary=paragraphs(
            "Since Theodore Laskaris named Michael Autoreianos patriarch in "
            "1205, the line of Orthodox patriarchs of Constantinople has "
            "carried on in exile at Nicaea. In 1220 the patriarch, Manuel "
            "I Charitopoulos, works hand in glove with the emperor; his "
            "authority is accepted in Trebizond, Epiros and the other "
            "Greek lands, and by many Orthodox under Latin rule who reject "
            "the Latin patriarch.",
            "His cathedral is Nicaea's Haghia Sophia, at the centre of the "
            "city's grid of streets. The emperor's plan to submit the "
            "Church to Rome for a time, to win back Constantinople, needs "
            "the patriarch and the bishops of Anatolia, and the council he "
            "has called in 1220 must settle the procession of the Holy "
            "Spirit, unleavened bread and, hardest of all, the pope's "
            "primacy.",
        ),
    )
    w["koimesis"] = b.church(
        "Church of the Koimesis, Nicaea",
        church="Chapel",
        place=p["bithynia"],
        summary=(
            "The private chapel of the emperor and his family, in the "
            "south of Nicaea near the imperial palace."
        ),
    )
    w["st_john_pergamos"] = b.church(
        "Church of St John the Apostle, Pergamos",
        church="Parish church",
        place=p["pergamos"],
        summary=(
            "The basilica serving the Christians who still live at "
            "Pergamos, one of the seven churches of Revelation; it stands "
            "over an older temple of Isis and Serapis, below the terrace "
            "of the Great Altar."
        ),
    )
    w["st_john_ephesus"] = b.church(
        "Basilica of St John, Ephesus",
        church="Bishop's cathedral",
        place=p["lydia"],
        summary=(
            "Ephesus's cathedral, built over the tomb of St John, with a "
            "Divine aura of 5. With the houses of Mary and St John it makes "
            "the town a pilgrimage, and Ephesus has long drawn pillar "
            "saints and ascetics; their numbers give the rest of the town "
            "a Divine aura of 3."
        ),
    )
    w["philadelphia_church"] = b.church(
        "The Great Church of Philadelphia",
        church="Large urban church",
        place=p["thrakesion"],
        summary=(
            "The main church of Philadelphia, one of the seven churches of "
            "Revelation, which Greek theologians think was once the "
            "headquarters of the infant Church. Its Divine aura is 6, in "
            "a city whose own aura of 4 is unusually strong."
        ),
    )


def _towns(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    nicaea = w["emperor_of_nicaea"]

    def town(key: str, name: str, summary: str, **kw: Any) -> None:
        w[key] = b.town(name, summary=summary, **kw)

    town(
        "nicaea",
        "Nicaea",
        "Always a great city of the empire, the emperors' summer seat and "
        "host of several Church councils, now capital of the Empire of "
        "Nicaea. Its straight streets run in a grid from the cathedral of "
        "Haghia Sophia at the centre; the palace and the Koimesis chapel "
        "lie to the south. Walls thirty feet high with over a hundred "
        "towers ring it, its three chief gates set midway along the "
        "northern, eastern and southern sides; on the west the lake of "
        "Ascania washes the wall, "
        "where small gates open on the docks. While Constantinople sinks "
        "under Infernal auras, Nicaea glows like a new dawn: revenues "
        "flow in, merchants and craftsmen thrive, scholars and "
        "theologians debate, Latin friars and papal envoys are welcome, "
        "and cypresses and peach orchards grow outside the walls. Moero's "
        "Garden lives in a merchants' quarter; the seven Demons of Nicaea "
        "hunt the roads outside but may not enter.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["bithynia"],
    )
    town(
        "nicomedia",
        "Nicomedia",
        "A walled Roman city on the Gulf of Astacus, sixty miles east of "
        "Constantinople and a day from Nicaea, with a citadel, forums, an "
        "amphitheatre, aqueducts and cisterns, one of the few in Asia "
        "Minor the Turks have not held in a century. After 1204 a hundred "
        "Latin knights sailed over, the people fled to Nicaea, and the "
        "knights fortified the church and ruled for nearly a year until "
        "Laskaris drove them into it; Emperor Henry came to their aid, "
        "and the two traded the city for the French hostages. It has "
        "been Greek since. It suffers an earthquake about once a "
        "century, blamed by its people on St George's dragon.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["bithynia"],
    )
    town(
        "holkos",
        "Holkos",
        "The Latin-held port where the Hellespont meets the Sea of "
        "Marmara, which Theodore Laskaris is about to attack, meaning to "
        "make it a second base for his fleet against Venetian ships. "
        "History has him take it.",
        charter="Noble lord",
        place=p["troad"],
    )
    town(
        "smyrna",
        "Smyrna",
        "Once a rival of Ephesus and Pergamos for the title of First City "
        "of Asia, it has declined since the capital moved to "
        "Constantinople, won and lost between Turks and Greeks for "
        "generations. Nicaea's strength has calmed its fears but not "
        "rebuilt it: over half the city is rubble, crumbling houses and "
        "overgrown streets leading nowhere. It is the royal port of the "
        "Nicene navy, which guards the Aegean; its war on Venetian "
        "merchants ended with the trade treaty of August 1219, and it "
        "will turn next to Chios, Lesbos and Rhodes. The harbour bustles "
        "with warships and merchantmen, Alexandria's three ships among "
        "them, and the city has the largest Jewish community in "
        "Anatolia. Alexandria's warehouses are here, its citadel on "
        "Mount Pagus above.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["lydia"],
    )
    town(
        "ephesus",
        "Hagios Theologos (Ephesus)",
        "Small but famous: one of Revelation's seven churches, the "
        "recipient of an epistle, an early centre of the faith where St "
        "Paul lived nearly three years and St John was martyred and "
        "buried, and the seat of the Third Ecumenical Council in 431, "
        "which condemned Nestorius. The Turks held it for almost forty "
        "years until the empire won it back in 1100 and renamed it "
        "Hagios Theologos. Its harbour has silted up and only a few "
        "hundred people remain, guarded by a small garrison and no "
        "wall, so a Turkish raid would go hard with it. Pilgrims and "
        "monks give it a Divine aura of 3, 5 in St John's Basilica.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["lydia"],
    )
    town(
        "pergamos_town",
        "Pergamos",
        "The small Christian town that survives below the ruined "
        "acropolis, by the Caicus, served by the Church of St John; its "
        "only weight with the Greeks is as one of Revelation's seven "
        "churches. Locals have chased off magi using the Great Altar as "
        "demon worshippers.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["troad"],
    )
    town(
        "philadelphia",
        "Philadelphia",
        "A strong fortress city on a high plateau at the foot of Mount "
        "Tmolus over the Maeander valley, the march against the Turks of "
        "Rum and the bulwark against their advance; its finest hour came "
        "in 1211, when Laskaris led its men out to beat Sultan "
        "Kaykhusraw. Its archers are said by the Nicenes to be the best "
        "in the world. One of Revelation's seven churches, it has a "
        "Divine aura of 4, rising to 6 in its main church. A terrible "
        "earthquake in AD 17 nearly levelled it, and since then its "
        "people have lived outside the walls, going in only when an "
        "enemy comes.",
        charter="Noble lord",
        answers_to=nicaea,
        place=p["thrakesion"],
    )
    town(
        "amastris",
        "Amastris",
        "A fortified Black Sea port, Nicaea's eastern limit since 1214, "
        "with its market outside the walls, old Greek families and many "
        "foreigners, more of Scandinavian blood than elsewhere since it "
        "was once the end of the road for mercenaries coming from "
        "Russia. It pays tribute and governs itself.",
        charter="Noble lord",
        answers_to=w["amastris_border"],
        place=p["pontus"],
    )
    town(
        "sinope",
        "Sinope",
        "A fortified port where Paphlagonia meets Pontus, the Seljuks' "
        "window on the Black Sea, much like Amastris: a market outside "
        "the walls, old Greek families and a good mix of foreigners, "
        "here more of Persian descent. Under its Muslim overlords it is "
        "unusually tolerant, letting its people be Christian, Muslim or "
        "Jewish as they please. Its Greek governor Etoumes pays tribute "
        "to Rum. A heretical sect hides beneath it.",
        charter="Noble lord",
        answers_to=w["lord_of_sinope"],
        place=p["pontus"],
    )
    town(
        "trebizond",
        "Trebizond",
        "The capital of the Empire of Trebizond, on ground sloping to the "
        "Black Sea with the Pontic mountains behind and a ravine on "
        "either side, beautiful and strong, with massive walls and two "
        "tall towers guarding the bridges over the ravines; the castle "
        "stands apart behind a narrow valley and its own walls. Its weak "
        "points are the harbour beside a short promontory and the market "
        "outside the walls. At one end of the Silk Road, it sells the "
        "East's goods to Western merchants and taxes every sale, and is "
        "very rich. Leaving dogma and the schools to Nicaea, its scholars "
        "pursue esoteric learning and look kindly on Persian and Arabic "
        "wisdom; among its libraries is a clean copy of Ptolemy's "
        "Geography, put back into Greek from Arabic, which no magus of "
        "Anatolia knows of, though any student of celestial magic or "
        "Ptolemy's magical coordinates would give a great deal for it. "
        "Its gardens hold magical plants, bardi wail before deaths, and "
        "a great shark haunts its docks.",
        charter="Noble lord",
        answers_to=w["emperor_of_trebizond"],
        place=p["pontus"],
    )


def _factions(theban: Theban, b: Builder) -> None:
    w = theban.world
    p = theban.places
    w["christians_of_serapis"] = b.faction(
        "The Christians of Serapis",
        faction="Other",
        decides="A council",
        members=200,
        realm="Infernal",
        place=p["serapis_shrine"],
        wants="New followers, and a hold over Sinope's ruler",
        offers="Hidden supernatural gifts to the faithful",
        summary=secrets(
            "A heretical Christian sect hidden beneath Sinope, about two "
            "hundred strong, led by a dozen priests, who keep an ancient "
            "cult statue smuggled out of Egypt. Its priests dress and act "
            "like Orthodox clergy, never quarrelling with the Church's own "
            "priests, the better to win converts quietly.",
            "Serapis is a False God, a demon. Few followers know what they "
            "worship, and he masks the Infernal nature of the Supernatural "
            "Abilities he grants them with his power to shroud the stench "
            "of the Pit. Etoumes, Sinope's Greek governor, has lately made "
            "one of its priests his confessor, to the demon's joy.",
        ),
    )
    w["council_of_union"] = b.faction(
        "The Council of Union at Nicaea",
        faction="Other",
        decides="A council",
        ruler="Theodore I Laskaris, its convener",
        place=p["bithynia"],
        wants="An end to the schism of East and West, and with it Constantinople",
        offers="Imperial favour to the churchmen who agree",
        summary=(
            "The churchmen Theodore Laskaris has gathered at Nicaea in 1220 "
            "to heal the schism between the Eastern and Western Churches. "
            "Besides the doctrinal quarrels over the procession of the Holy "
            "Spirit and unleavened bread at communion, they must settle the "
            "political question of the pope's primacy. The pope has "
            "hinted that a temporary submission would do; the emperor "
            "still has to win over the patriarch and Anatolia's bishops."
        ),
    )


# ------------------------------------------------------------- finishing


def finish(theban: Theban) -> None:
    """Tie Proximios to the magi of other parts once they exist."""
    b = theban.b
    proximios = theban.magi["proximios"]
    hydatius = theban.magi.get("hydatius")
    if hydatius is not None:
        b.link(
            proximios,
            "characters",
            hydatius,
            "Co-founder of the League of the Vigilant, which Hydatius leads",
        )
    b.link(
        proximios,
        "characters",
        theban.magi["ziper"],
        "Backs Ziper's proposal to take Nanno and Ampelius into Moero's Garden",
    )
    lucian = theban.magi.get("lucian")
    if lucian is not None:
        b.link(
            proximios,
            "characters",
            lucian,
            "Delighted Lucian with acrobatics as a young messenger",
        )
    evantia = theban.magi.get("evantia") or next(
        (c for c in b.saga.characters if c.name.startswith("Evantia")), None
    )
    if evantia is not None and evantia.covenant_id is None:
        evantia.covenant_id = theban.covenants["moeros_garden"].id


# --------------------------------------------------------------- stats

P = Profile
GREEK = "Greek"
THEBES = "Area Lore: Theban Tribunal"
CONSTANTINOPLE = "Area Lore: Constantinople"


def _art(name: str, art: str) -> tuple[str, dict[str, str]]:
    return (name, {"art": art})


#: Each magus the book sketches without a stat block, by character key.
PROFILES: dict[str, Profile] = {
    "leontius": P(
        gifted=False,
        strong="int com per",
        native=GREEK,
        abilities={
            "Organization Lore: Order of Hermes": (4, "the Theban polity"),
            THEBES: (4, "covenants"),
            "Profession: Scribe": (3, "records"),
            "Code of Hermes": (3, "the Peripheral Code"),
            "Dead Language: Classical Greek": 4,
            "Dead Language: Latin": 2,
            "Ride": 2,
            "Bargain": 2,
        },
        virtues=["Redcap", "Lycanthrope", "Dutybound"],
        reputations={"Failed logothete (Hermetic)": 3},
    ),
    "proximios": P(
        gifted=False,
        strong="pre com dex qik",
        native=GREEK,
        abilities={
            "Intrigue": (5, "Theban politics"),
            "Athletics": (6, "acrobatics"),
            "Guile": (4, "seeming humble"),
            "Folk Ken": (3, "magi"),
            "Organization Lore: Order of Hermes": (4, "the Theban polity"),
            THEBES: 3,
            "Dead Language: Classical Greek": 4,
            "Ride": 2,
        },
        virtues=["Redcap", "Mythic Blood", "Dark Secret", "Driven (Major)"],
        reputations={"Able politician (Hermetic)": 4},
    ),
    "catella": P(
        strong="int per dex",
        arts={"Re": 6, "Te": 6, "Vi": 5, "In": 5, "Mu": 3},
        abilities={
            "Magic Theory": (6, "enchanted devices"),
            "Philosophiae": (3, "mechanics"),
            "Magic Lore": (2, "Alexander's relics"),
        },
        virtues=["Inventive Genius", "Obsessed (Minor)", "Dutybound"],
        native=GREEK,
    ),
    "ionnia": P(
        strong="int pre com",
        weak="sta str",
        arts={"Re": 8, "Me": 8, "In": 4, "Im": 3, "Co": 3},
        abilities={
            "Artes Liberales": (4, "poetry"),
            "Etiquette": (4, "the imperial court"),
            "Magic Lore": (3, "ghosts"),
            CONSTANTINOPLE: 3,
            "Teaching": 2,
        },
        virtues=["Famous", "Difficult Longevity Ritual", "Frail"],
        native=GREEK,
        reputations={"Gatherer of Kassia's poems (Hermetic)": 3},
    ),
    "syagricus": P(
        strong="pre com sta",
        arts={"Im": 6, "Cr": 5, "In": 4, "Co": 4, "Te": 3},
        abilities={
            "Etiquette": (4, "nobles"),
            CONSTANTINOPLE: (3, "lost treasures"),
            "Charm": 2,
            "Artes Liberales": 2,
        },
        virtues=["Driven (Minor)"],
        native=GREEK,
    ),
    "ziper": P(
        strong="int com pre",
        arts={"Me": 7, "Im": 5, "Re": 5, "In": 4, "Cr": 3},
        abilities={
            "Intrigue": (5, "covenant politics"),
            "Guile": (4, "flattery"),
            "Etiquette": 3,
            "Folk Ken": 3,
        },
        virtues=["Gentle Gift", "Busybody", "Ambitious (Major)"],
        native=GREEK,
    ),
    "trasaric": P(
        age=45,
        strong="pre sta str",
        arts={"Re": 5, "Co": 4, "Mu": 4, "Ig": 4, "Me": 3, "Te": 3},
        abilities={
            "Etiquette": 3,
            "Leadership": (2, "soldiers"),
            "Single Weapon": 2,
            CONSTANTINOPLE: 2,
        },
        virtues=["Driven (Minor)", "Close Family Ties"],
        native=GREEK,
    ),
    "helladius": P(
        age=43,
        strong="int pre com",
        arts={"Me": 5, "In": 4, "Im": 4, "Re": 4, "Co": 3},
        abilities={
            "Etiquette": 3,
            "Intrigue": (2, "the Nicene court"),
            CONSTANTINOPLE: 2,
        },
        virtues=["Driven (Minor)", "Reckless (Minor)"],
        native=GREEK,
    ),
}

#: The apparent ages the book gives.
APPARENT_AGES: dict[str, int] = {
    "leontius": 82,
    "proximios": 42,
    "catella": 39,
    "ionnia": 91,
    "syagricus": 43,
    "ziper": 65,
}


def stats(theban: Theban) -> None:
    """Generated stats for the magi of Anatolia, none of whom has a
    printed stat block, with the apparent ages the book gives."""
    b = theban.b
    for key, profile in PROFILES.items():
        character = theban.magi[key]
        apply(b, character, profile)
        if key in APPARENT_AGES:
            character.aging.apparent_age = APPARENT_AGES[key]
